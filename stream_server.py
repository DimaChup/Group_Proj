# stream_server.py — HTTP streaming server module
# Extracted from main.py: MJPEG stream, dashboard HTML, command endpoint.
# Usage:
#   from stream_server import set_stream_frame, start_stream_server, cmd_queue
#   start_stream_server(port=8090, stream_w=320, stream_h=240, stream_fps=5, stream_quality=50)
#   set_stream_frame(frame)          # numpy BGR frame (will be resized + JPEG-encoded)
#   key_code = cmd_queue.get()       # int keycode from browser buttons / keyboard proxy

import time
import threading
import queue
import cv2
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn

# ---------------------------------------------------------------------------
# Thread-safe frame buffer
# ---------------------------------------------------------------------------
_stream_frame = None
_stream_lock = threading.Lock()


def set_stream_frame(frame):
    """Store a new BGR numpy frame for the stream (thread-safe)."""
    global _stream_frame
    with _stream_lock:
        _stream_frame = frame


def get_stream_frame():
    """Return the latest BGR numpy frame (or None)."""
    with _stream_lock:
        return _stream_frame


# ---------------------------------------------------------------------------
# Command queue — browser buttons / HTTP /cmd feed key codes here
# ---------------------------------------------------------------------------
cmd_queue = queue.Queue()

# ---------------------------------------------------------------------------
# Stream settings (set by start_stream_server, read by handler)
# ---------------------------------------------------------------------------
_cfg_stream_w = 320
_cfg_stream_h = 240
_cfg_stream_fps = 5
_cfg_stream_quality = 50


# ---------------------------------------------------------------------------
# HTTP handler
# ---------------------------------------------------------------------------
class StreamHandler(BaseHTTPRequestHandler):
    """Serves /, /stream, /snapshot, /cmd endpoints."""

    def do_GET(self):
        if self.path == '/stream':
            self._serve_stream()
        elif self.path == '/snapshot':
            self._serve_snapshot()
        elif self.path.startswith('/cmd?key='):
            self._serve_cmd()
        elif self.path == '/':
            self._serve_html()
        else:
            self.send_response(404)
            self.end_headers()

    # -- MJPEG multipart stream ------------------------------------------
    def _serve_stream(self):
        self.send_response(200)
        self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=frame')
        self.end_headers()
        _no_frame_count = 0
        while True:
            with _stream_lock:
                f = _stream_frame
            if f is None:
                _no_frame_count += 1
                if _no_frame_count > 300:  # 30 seconds with no frames
                    break
                time.sleep(0.1)
                continue
            _no_frame_count = 0
            small = cv2.resize(f, (_cfg_stream_w, _cfg_stream_h))
            ret, jpeg = cv2.imencode('.jpg', small, [cv2.IMWRITE_JPEG_QUALITY, _cfg_stream_quality])
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

    # -- Single JPEG snapshot --------------------------------------------
    def _serve_snapshot(self):
        with _stream_lock:
            f = _stream_frame
        if f is None:
            self.send_response(503)
            self.end_headers()
            return
        small = cv2.resize(f, (_cfg_stream_w, _cfg_stream_h))
        _, jpeg = cv2.imencode('.jpg', small, [cv2.IMWRITE_JPEG_QUALITY, _cfg_stream_quality])
        data = jpeg.tobytes()
        self.send_response(200)
        self.send_header('Content-Type', 'image/jpeg')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    # -- Command endpoint (/cmd?key=y) -----------------------------------
    def _serve_cmd(self):
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

    # -- Dashboard HTML --------------------------------------------------
    def _serve_html(self):
        html = '''<html><head><style>
body{background:#111;color:#fff;font-family:monospace;text-align:center;margin:0;padding:10px}
img{max-width:100%;border:2px solid #0f0;margin:10px 0}
.btns{display:flex;gap:8px;justify-content:center;flex-wrap:wrap;margin:10px 0}
.btn{padding:12px 24px;font-size:16px;font-weight:bold;border:none;border-radius:6px;cursor:pointer;
  font-family:monospace;min-width:80px}
.btn-y{background:#2ecc71;color:#000}.btn-n{background:#e74c3c;color:#fff}
.btn-dir{background:#3498db;color:#fff}.btn-m{background:#f39c12;color:#000}
.info{color:#aaa;font-size:12px}
#status{color:#0f0;margin:5px 0;min-height:20px}
</style></head><body>
<h2>SAR Drone Mission Feed</h2>
<img src="/stream" alt="Video Stream">
<div id="status"></div>
<p class="info">VERIFY: press Y (confirm) or N (reject). Then select landing side: N/E/W/S</p>
<div class="btns">
  <button class="btn btn-y" onclick="cmd('y')">Y Confirm</button>
  <button class="btn btn-n" onclick="cmd('n')">N Reject</button>
  <button class="btn btn-m" onclick="cmd('m')">M Manual</button>
</div>
<p class="info">Landing direction (after Y):</p>
<div class="btns">
  <button class="btn btn-dir" onclick="cmd('n')">North</button>
  <button class="btn btn-dir" onclick="cmd('e')">East</button>
  <button class="btn btn-dir" onclick="cmd('s')">South</button>
  <button class="btn btn-dir" onclick="cmd('w')">West</button>
</div>
<p class="info">''' + f'{_cfg_stream_w}x{_cfg_stream_h} | {_cfg_stream_fps} fps | Quality {_cfg_stream_quality}%' + '''</p>
<script>
function cmd(k){fetch('/cmd?key='+k).then(r=>r.json()).then(d=>{
  document.getElementById('status').textContent='Sent: '+k.toUpperCase()+' ('+new Date().toLocaleTimeString()+')';
}).catch(e=>{document.getElementById('status').textContent='Error: '+e})}
document.addEventListener('keydown',e=>{
  if(['y','n','e','w','s','m'].includes(e.key.toLowerCase()))cmd(e.key.toLowerCase());
});
</script></body></html>'''
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())

    def log_message(self, format, *args):
        pass  # Silence per-request logs


# ---------------------------------------------------------------------------
# Server lifecycle
# ---------------------------------------------------------------------------
class _ThreadingHTTP(ThreadingMixIn, HTTPServer):
    daemon_threads = True


def start_stream_server(port=8090, host='0.0.0.0',
                        stream_w=320, stream_h=240,
                        stream_fps=5, stream_quality=50):
    """Create and start the MJPEG streaming server in a daemon thread.

    Returns the server object (call server.shutdown() to stop), or None on error.
    """
    global _cfg_stream_w, _cfg_stream_h, _cfg_stream_fps, _cfg_stream_quality
    _cfg_stream_w = stream_w
    _cfg_stream_h = stream_h
    _cfg_stream_fps = stream_fps
    _cfg_stream_quality = stream_quality

    try:
        server = _ThreadingHTTP((host, port), StreamHandler)
        server_thread = threading.Thread(target=server.serve_forever, daemon=True)
        server_thread.start()
        # Get IP for display
        pi_ip = "localhost"
        try:
            import subprocess
            result = subprocess.run(['hostname', '-I'], capture_output=True, text=True, timeout=3)
            pi_ip = result.stdout.strip().split()[0]
        except Exception:
            pass
        print(f"[STREAM] Live feed: http://{pi_ip}:{port}/")
        print(f"[STREAM] Settings: {stream_w}x{stream_h} @ {stream_fps}fps, quality {stream_quality}%")
        return server
    except Exception as e:
        print(f"[STREAM] Failed to start: {e}")
        return None
