"""Lightweight HTTP server for MJPEG streaming and operator commands.

Provides five endpoints on a single port (default 8090):

    /          Dashboard HTML with live video, operator buttons, and keyboard proxy.
    /stream    MJPEG multipart stream (resized + JPEG-encoded from the latest frame).
    /snapshot  Single JPEG capture of the current frame.
    /cmd?key=  Command injection — enqueues a keycode for the mission state machine.
    /status    JSON telemetry snapshot (state, alt, GPS, confidence, etc.).

Typical usage::

    from stream_server import set_stream_frame, set_telemetry, start_stream_server, cmd_queue

    server = start_stream_server(port=8090)
    set_stream_frame(bgr_numpy_array)   # call from any thread
    set_telemetry(state="SEARCH", alt=30.0, lat=51.42, lon=-2.67, ...)
    key_code = cmd_queue.get()           # blocks until an operator presses a button

Thread safety
-------------
* ``set_stream_frame`` / ``get_stream_frame`` are guarded by ``_stream_lock``.
* ``set_telemetry`` / ``get_telemetry`` are guarded by ``_telemetry_lock``.
* ``cmd_queue`` is a stdlib ``queue.Queue`` (inherently thread-safe).
* ``_ThreadingHTTP`` spawns a daemon thread per connection so concurrent
  ``/stream`` clients do not block each other or the ``/cmd`` endpoint.
* Module-level ``_cfg_*`` settings are written once in ``start_stream_server``
  before the server thread starts, then read-only — no lock required.
"""

import json as _json
import time
import threading
import queue

import cv2
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn

# -- Thread-safe frame buffer ------------------------------------------------

_stream_frame = None
_stream_lock = threading.Lock()


def set_stream_frame(frame):
    """Replace the current frame with *frame* (BGR ``numpy.ndarray``).

    Called by the main mission loop from any thread.  The frame is stored
    as-is; resizing and JPEG encoding happen lazily inside the handler.
    """
    global _stream_frame
    with _stream_lock:
        _stream_frame = frame


def get_stream_frame():
    """Return the latest BGR frame, or ``None`` if nothing has been published."""
    with _stream_lock:
        return _stream_frame


# -- Thread-safe telemetry buffer --------------------------------------------

_telemetry: dict = {}
_telemetry_lock = threading.Lock()


def set_telemetry(**kwargs):
    """Update telemetry fields from the mission loop.

    Call with keyword arguments, e.g.::

        set_telemetry(state="SEARCH", alt=30.0, lat=51.42, lon=-2.67,
                      speed=4.2, conf=0.87, wp_index=3, wp_total=12,
                      gps_fix=3, gps_sats=14, waiting=False,
                      selecting_side=False, verify_timeout=None)

    Only the supplied keys are updated; missing keys keep their previous
    values.  This lets callers push partial updates cheaply.
    """
    with _telemetry_lock:
        _telemetry.update(kwargs)


def get_telemetry() -> dict:
    """Return a shallow copy of the current telemetry dict."""
    with _telemetry_lock:
        return dict(_telemetry)


# -- Command queue -----------------------------------------------------------

cmd_queue: queue.Queue = queue.Queue()
"""Operator key-codes (``int``) from browser buttons or the ``/cmd`` endpoint.

Consumers should call ``cmd_queue.get(timeout=...)`` to avoid blocking
indefinitely.
"""

# -- Stream configuration (written once, then read-only) ---------------------

_cfg_stream_w: int = 320
_cfg_stream_h: int = 240
_cfg_stream_fps: int = 5
_cfg_stream_quality: int = 50


# -- HTTP request handler ----------------------------------------------------

class StreamHandler(BaseHTTPRequestHandler):
    """Route ``GET`` requests to the four public endpoints."""

    def do_GET(self):
        if self.path == '/stream':
            self._serve_stream()
        elif self.path == '/snapshot':
            self._serve_snapshot()
        elif self.path == '/status':
            self._serve_status()
        elif self.path.startswith('/cmd?key='):
            self._serve_cmd()
        elif self.path == '/':
            self._serve_html()
        else:
            self.send_response(404)
            self.end_headers()

    # -- MJPEG multipart stream ----------------------------------------------

    def _serve_stream(self):
        """Push JPEG frames as a ``multipart/x-mixed-replace`` stream.

        Disconnects automatically after 30 s of no frames or if the client
        drops the connection.
        """
        self.send_response(200)
        self.send_header('Content-Type',
                         'multipart/x-mixed-replace; boundary=frame')
        self.end_headers()

        idle_ticks = 0
        while True:
            with _stream_lock:
                f = _stream_frame
            if f is None:
                idle_ticks += 1
                if idle_ticks > 300:          # 300 * 0.1 s = 30 s timeout
                    break
                time.sleep(0.1)
                continue
            idle_ticks = 0

            small = cv2.resize(f, (_cfg_stream_w, _cfg_stream_h))
            ret, jpeg = cv2.imencode(
                '.jpg', small,
                [cv2.IMWRITE_JPEG_QUALITY, _cfg_stream_quality],
            )
            if not ret or jpeg is None:
                time.sleep(0.1)
                continue

            data = jpeg.tobytes()
            try:
                self.wfile.write(b'--frame\r\n')
                self.wfile.write(b'Content-Type: image/jpeg\r\n')
                self.wfile.write(f'Content-Length: {len(data)}\r\n\r\n'.encode())
                self.wfile.write(data)
                self.wfile.write(b'\r\n')
            except (BrokenPipeError, ConnectionResetError):
                break

            time.sleep(1.0 / _cfg_stream_fps)

    # -- Single JPEG snapshot ------------------------------------------------

    def _serve_snapshot(self):
        """Return one JPEG frame, or 503 if no frame is available yet."""
        with _stream_lock:
            f = _stream_frame
        if f is None:
            self.send_response(503)
            self.end_headers()
            return

        small = cv2.resize(f, (_cfg_stream_w, _cfg_stream_h))
        _, jpeg = cv2.imencode(
            '.jpg', small,
            [cv2.IMWRITE_JPEG_QUALITY, _cfg_stream_quality],
        )
        data = jpeg.tobytes()
        self.send_response(200)
        self.send_header('Content-Type', 'image/jpeg')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    # -- Telemetry JSON endpoint -----------------------------------------------

    def _serve_status(self):
        """Return current telemetry as JSON for the dashboard overlay."""
        data = get_telemetry()
        body = _json.dumps(data).encode()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    # -- Command endpoint ----------------------------------------------------

    def _serve_cmd(self):
        """Parse ``/cmd?key=<char>`` and enqueue the keycode.

        Valid keys: ``y``, ``n``, ``e``, ``w``, ``s``, ``m``.
        """
        parts = self.path.split('key=')
        if len(parts) < 2 or not parts[1]:
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"ok":false,"error":"missing key parameter"}')
            return

        key_char = parts[1][0].lower()
        valid = {'y', 'n', 'e', 'w', 's', 'm'}
        if key_char in valid:
            cmd_queue.put(ord(key_char))
            resp = f'{{"ok":true,"key":"{key_char}"}}'
        else:
            resp = f'{{"ok":false,"error":"invalid key: {key_char}"}}'

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(resp.encode())

    # -- Dashboard HTML ------------------------------------------------------

    def _serve_html(self):
        """Serve the single-page operator dashboard."""
        html = _build_dashboard_html()
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())

    # -- Logging -------------------------------------------------------------

    def log_message(self, format, *args):
        """Suppress per-request log spam from BaseHTTPRequestHandler."""
        pass


# -- Dashboard HTML template -------------------------------------------------

def _build_dashboard_html() -> str:
    """Return the operator dashboard as a self-contained HTML string.

    The page embeds the ``/stream`` MJPEG feed, operator buttons (Y/N/M and
    compass directions for landing), and a keyboard listener that mirrors
    physical key-presses to ``/cmd``.
    """
    return f"""<!DOCTYPE html><html><head><meta charset='utf-8'>
<title>SAR Drone</title>
<style>
*{{box-sizing:border-box}}
body{{background:#111;color:#fff;font-family:monospace;margin:0;padding:8px}}
.top{{display:flex;gap:8px;align-items:stretch;min-height:0}}
.video-box{{flex:2;position:relative;min-width:0}}
.video-box img{{width:100%;display:block;border:2px solid #0f0;border-radius:4px}}
.telem-panel{{flex:0 0 260px;background:#1a1a1a;border:1px solid #333;border-radius:6px;
  padding:10px;font-size:13px;display:flex;flex-direction:column;gap:6px;overflow-y:auto}}
.telem-panel h3{{margin:0 0 4px;color:#0f0;font-size:14px;border-bottom:1px solid #333;padding-bottom:4px}}
.t-row{{display:flex;justify-content:space-between;padding:2px 0}}
.t-label{{color:#888}}.t-val{{color:#fff;text-align:right}}
#t-state{{font-size:18px;font-weight:bold;text-align:center;padding:6px;
  border-radius:4px;background:#222;color:#0f0}}
#t-state.verify{{background:#e74c3c;color:#fff;animation:pulse 1s infinite}}
#t-state.manual{{background:#f39c12;color:#000}}
#t-state.search{{background:#2980b9;color:#fff}}
#t-state.done{{background:#333;color:#888}}
@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:0.6}}}}
.t-bar{{height:6px;background:#333;border-radius:3px;overflow:hidden}}
.t-bar-fill{{height:100%;background:#2ecc71;transition:width 0.3s}}
.btns{{display:flex;gap:8px;justify-content:center;flex-wrap:wrap;margin:6px 0}}
.btn{{padding:10px 20px;font-size:15px;font-weight:bold;border:none;border-radius:6px;
  cursor:pointer;font-family:monospace;min-width:70px}}
.btn-y{{background:#2ecc71;color:#000}}.btn-n{{background:#e74c3c;color:#fff}}
.btn-dir{{background:#3498db;color:#fff}}.btn-m{{background:#f39c12;color:#000}}
.info{{color:#888;font-size:11px;text-align:center;margin:2px 0}}
#cmd-status{{color:#0f0;text-align:center;margin:4px 0;min-height:18px;font-size:12px}}
#t-prompt{{text-align:center;padding:4px;font-size:13px;color:#ff0;display:none}}
</style></head><body>

<div class="top">
  <div class="video-box">
    <img src="/stream" alt="Video Stream">
  </div>
  <div class="telem-panel">
    <div id="t-state">CONNECTING</div>
    <div id="t-prompt"></div>

    <h3>Telemetry</h3>
    <div class="t-row"><span class="t-label">ALT</span><span class="t-val" id="t-alt">--</span></div>
    <div class="t-row"><span class="t-label">SPD</span><span class="t-val" id="t-spd">--</span></div>
    <div class="t-row"><span class="t-label">LAT</span><span class="t-val" id="t-lat">--</span></div>
    <div class="t-row"><span class="t-label">LON</span><span class="t-val" id="t-lon">--</span></div>

    <h3>Detection</h3>
    <div class="t-row"><span class="t-label">Conf</span><span class="t-val" id="t-conf">--</span></div>
    <div class="t-row"><span class="t-label">Queue</span><span class="t-val" id="t-queue">--</span></div>

    <h3>Search</h3>
    <div class="t-row"><span class="t-label">WP</span><span class="t-val" id="t-wp">--</span></div>
    <div class="t-bar"><div class="t-bar-fill" id="t-wp-bar" style="width:0%"></div></div>

    <h3>GPS</h3>
    <div class="t-row"><span class="t-label">Fix</span><span class="t-val" id="t-fix">--</span></div>
    <div class="t-row"><span class="t-label">Sats</span><span class="t-val" id="t-sats">--</span></div>
  </div>
</div>

<div id="cmd-status"></div>

<div class="btns">
  <button class="btn btn-y" onclick="cmd('y')">Y Confirm</button>
  <button class="btn btn-n" onclick="cmd('n')">N Reject</button>
  <button class="btn btn-m" onclick="cmd('m')">M Manual</button>
</div>
<p class="info">Landing direction (after Y confirm):</p>
<div class="btns">
  <button class="btn btn-dir" onclick="cmd('n')">North</button>
  <button class="btn btn-dir" onclick="cmd('e')">East</button>
  <button class="btn btn-dir" onclick="cmd('s')">South</button>
  <button class="btn btn-dir" onclick="cmd('w')">West</button>
</div>
<p class="info">{_cfg_stream_w}x{_cfg_stream_h} | {_cfg_stream_fps} fps | Q{_cfg_stream_quality}%</p>

<script>
function cmd(k){{
  fetch('/cmd?key='+k).then(r=>r.json()).then(d=>{{
    document.getElementById('cmd-status').textContent=
      'Sent: '+k.toUpperCase()+' ('+new Date().toLocaleTimeString()+')';
  }}).catch(e=>{{document.getElementById('cmd-status').textContent='Error: '+e}});
}}
document.addEventListener('keydown',e=>{{
  if(['y','n','e','w','s','m'].includes(e.key.toLowerCase()))
    cmd(e.key.toLowerCase());
}});

/* Poll /status every 1s for live telemetry */
function poll(){{
  fetch('/status').then(r=>r.json()).then(d=>{{
    var s=document.getElementById('t-state');
    s.textContent=d.state||'--';
    s.className='';
    var sl=(d.state||'').toLowerCase();
    if(sl==='verify')s.className='verify';
    else if(sl==='manual')s.className='manual';
    else if(sl.indexOf('search')>=0)s.className='search';
    else if(sl==='done')s.className='done';

    document.getElementById('t-alt').textContent=
      d.alt!==undefined?d.alt.toFixed(1)+'m':'--';
    document.getElementById('t-spd').textContent=
      d.speed!==undefined?d.speed.toFixed(1)+'m/s':'--';
    document.getElementById('t-lat').textContent=
      d.lat!==undefined?d.lat.toFixed(6):'--';
    document.getElementById('t-lon').textContent=
      d.lon!==undefined?d.lon.toFixed(6):'--';

    var confEl=document.getElementById('t-conf');
    if(d.conf!==undefined){{
      confEl.textContent=d.conf.toFixed(2);
      confEl.style.color=d.conf>0.5?'#2ecc71':d.conf>0?'#f39c12':'#888';
    }}else confEl.textContent='--';

    document.getElementById('t-queue').textContent=
      d.cmd_queue_size!==undefined?d.cmd_queue_size:'--';

    var wpEl=document.getElementById('t-wp');
    var wpBar=document.getElementById('t-wp-bar');
    if(d.wp_index!==undefined&&d.wp_total!==undefined&&d.wp_total>0){{
      wpEl.textContent=d.wp_index+'/'+d.wp_total;
      wpBar.style.width=Math.round(d.wp_index/d.wp_total*100)+'%';
    }}else{{wpEl.textContent='--';wpBar.style.width='0%';}}

    var fixTypes={{0:'No GPS',1:'No Fix',2:'2D',3:'3D',4:'DGPS',5:'RTK Float',6:'RTK Fix'}};
    document.getElementById('t-fix').textContent=
      d.gps_fix!==undefined?(fixTypes[d.gps_fix]||d.gps_fix):'--';
    document.getElementById('t-sats').textContent=
      d.gps_sats!==undefined?d.gps_sats:'--';

    /* Prompt bar for VERIFY / landing side */
    var pr=document.getElementById('t-prompt');
    if(d.selecting_side){{
      pr.style.display='block';pr.textContent='SELECT LANDING SIDE: N / E / S / W';
      pr.style.color='#0ff';
    }}else if(d.waiting){{
      var vt=d.verify_timeout!==undefined?' ('+Math.round(d.verify_timeout)+'s)':'';
      pr.style.display='block';pr.textContent='VERIFY TARGET: Y / N / I'+vt;
      pr.style.color='#f00';
    }}else pr.style.display='none';

  }}).catch(()=>{{}});
}}
setInterval(poll,1000);poll();
</script></body></html>"""


# -- Server lifecycle --------------------------------------------------------

class _ThreadingHTTP(ThreadingMixIn, HTTPServer):
    """HTTPServer that spawns a daemon thread per request.

    ``daemon_threads = True`` ensures all handler threads die when the main
    process exits.  ``allow_reuse_address = True`` prevents ``Address already
    in use`` errors on rapid restart.
    """
    daemon_threads = True
    allow_reuse_address = True


def start_stream_server(port: int = 8090, host: str = '0.0.0.0',
                        stream_w: int = 320, stream_h: int = 240,
                        stream_fps: int = 5, stream_quality: int = 50,
                        max_port_retries: int = 5):
    """Start the MJPEG streaming server on a background daemon thread.

    If the requested *port* is already in use the function tries up to
    *max_port_retries* consecutive ports (port+1, port+2, ...) before
    giving up.

    Parameters
    ----------
    port : int
        TCP port to bind (default 8090).
    host : str
        Bind address (default ``0.0.0.0`` = all interfaces).
    stream_w, stream_h : int
        Resolution to resize frames to before JPEG encoding.
    stream_fps : int
        Target frame rate for the ``/stream`` endpoint.
    stream_quality : int
        JPEG quality percentage (1--100).
    max_port_retries : int
        How many consecutive ports to try if the first is busy (default 5).

    Returns
    -------
    HTTPServer or None
        The running server instance (call ``server.shutdown()`` to stop),
        or ``None`` if no port could be bound.
    """
    global _cfg_stream_w, _cfg_stream_h, _cfg_stream_fps, _cfg_stream_quality
    _cfg_stream_w = stream_w
    _cfg_stream_h = stream_h
    _cfg_stream_fps = stream_fps
    _cfg_stream_quality = stream_quality

    pi_ip = "localhost"
    try:
        import subprocess
        result = subprocess.run(
            ['hostname', '-I'],
            capture_output=True, text=True, timeout=3,
        )
        pi_ip = result.stdout.strip().split()[0]
    except Exception:
        pass

    last_error = None
    for attempt_port in range(port, port + max_port_retries):
        try:
            server = _ThreadingHTTP((host, attempt_port), StreamHandler)
            threading.Thread(target=server.serve_forever, daemon=True).start()

            if attempt_port != port:
                print(f"[STREAM] Port {port} in use — bound to {attempt_port} instead")
            print(f"[STREAM] Live feed: http://{pi_ip}:{attempt_port}/")
            print(f"[STREAM] Settings: {stream_w}x{stream_h} "
                  f"@ {stream_fps}fps, quality {stream_quality}%")
            return server
        except OSError as e:
            last_error = e
            continue

    print(f"[STREAM] ERROR: could not bind ports {port}-{port + max_port_retries - 1}: "
          f"{last_error}")
    return None
