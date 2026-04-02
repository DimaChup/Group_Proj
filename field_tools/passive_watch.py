#!/usr/bin/env python3
"""
passive_watch.py — Passive camera observer with web stream + auto snapshots.

ZERO commands sent to anything. Just watches, detects, streams, saves.
Optionally reads GPS from mavproxy (read-only) for geotagging photos.

Run on Pi via SSH:
    cd ~/dima/Group_Proj
    source pienv/bin/activate
    DISPLAY= python passive_watch.py

Open in laptop browser:
    http://<PI_IP>:8090/          (stream page)
    http://<PI_IP>:8090/stream    (raw MJPEG)
    http://<PI_IP>:8090/snapshot  (latest detection frame)

Options:
    --port 8090         HTTP port (default 8090)
    --conf 0.4          Confidence threshold (default 0.4)
    --fps 5             Max inference FPS (default 5)
    --save-dir detections   Where to save snapshots (default: detections/)
    --no-save           Don't save snapshots, stream only
    --no-mavlink        Don't connect to mavproxy (no GPS overlay)
"""
import sys
import os
import time
import signal
import threading
import argparse
import subprocess
import csv
import json
import math
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn

# Add project root to path (field_tools/ is one level below root)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Ensure Ctrl+C works
signal.signal(signal.SIGINT, signal.SIG_DFL)

# Headless OpenCV
if not os.environ.get('DISPLAY'):
    os.environ.pop('QT_QPA_PLATFORM', None)

import cv2
import numpy as np
import config
from vision import VisionSystem

# ── Globals for streaming ──
latest_jpeg = None
latest_det_jpeg = None
latest_bullseye = None
latest_detection_jpeg = None   # latest detection snapshot
latest_smart_grid_jpeg = None  # 5x2 smart frames grid
latest_map_jpeg = None         # satellite map overlay
frame_lock = threading.Lock()
gps_lock = threading.Lock()
_all_gps_estimates = []
_map_base = None  # loaded map.jpg (once)
bullseye_map_bg = False  # toggle: dark background vs satellite map crop for bullseye plots 1-2

# ── Args ──
parser = argparse.ArgumentParser(description="Passive camera watch + stream + snapshots")
parser.add_argument('--port', type=int, default=8090)
parser.add_argument('--conf', type=float, default=0.4)
parser.add_argument('--fps', type=float, default=5)
parser.add_argument('--save-dir', default='detections')
parser.add_argument('--no-save', action='store_true')
parser.add_argument('--no-mavlink', action='store_true', help='Skip mavproxy connection (no GPS)')
parser.add_argument('--model', default='best.tflite', help='Path to .tflite model (default: best.tflite)')
parser.add_argument('--simple-names', action='store_true', help='Simple filenames (no det_ prefix, no JSON sidecars)')
parser.add_argument('--class-filter', type=str, default=None, help='Only save detections of this class (e.g. "person")')
parser.add_argument('--smart-estimate', action='store_true', help='Accumulate central detections, save after 10+ with median GPS')
parser.add_argument('--smart-min', type=int, default=10, help='Min central detections before saving (default 10)')
parser.add_argument('--smart-radius', type=float, default=0.5, help='Max spread for smart cluster (default 0.5m)')
parser.add_argument('--fake', action='store_true', help='Replay DJI video + SRT telemetry (no camera/mavproxy)')
parser.add_argument('--fake-video', default='RealVideo/DJI_0001_1456x1088_cropped_30fps.mp4')
parser.add_argument('--fake-srt', default='RealVideo/DJI_20260311172332_0001_V.SRT')
parser.add_argument('--no-stream', action='store_true', help='Disable HTTP stream server')
args = parser.parse_args()

# ── Model definitions for browser switcher ──
MODEL_TABLE = [
    {"id": 0, "name": "Original",    "path": "best.tflite",                         "backend": None},
    {"id": 1, "name": "SAR v2 TFL",  "path": "cv_models/sar_v2_1088/best.tflite",   "backend": None},
    {"id": 2, "name": "SAR v2 NCNN", "path": "cv_models/sar_v2_1088/best.tflite",   "backend": "ncnn"},
    {"id": 3, "name": "COCO Person", "path": "cv_models/human.tflite",              "backend": None},
]

# Runtime state (modified by API endpoints, read by main loop)
runtime_state = {
    "active_model_id": 0,       # index into MODEL_TABLE
    "conf_threshold": args.conf, # current confidence threshold
    "class_filter": args.class_filter or "all",  # "all", "dummy", "person"
    "model_switch_request": None,  # set to model_id to trigger reload in main loop
}
runtime_lock = threading.Lock()


# ── SRT parser for fake mode ──
def parse_srt(srt_path):
    """Parse DJI SRT → dict of frame_num → {lat, lon, alt, yaw}."""
    import re
    with open(srt_path, 'r') as f:
        text = f.read()
    entries = {}
    blocks = re.split(r'\n\n+', text.strip())
    frame = 0
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) < 3:
            continue
        try:
            int(lines[0])
        except ValueError:
            continue
        frame += 1
        data = ' '.join(lines[2:])
        lat = lon = alt = yaw = 0.0
        m = re.search(r'\[latitude:\s*([-\d.]+)\]', data)
        if m: lat = float(m.group(1))
        m = re.search(r'\[longitude:\s*([-\d.]+)\]', data)
        if m: lon = float(m.group(1))
        m = re.search(r'\[rel_alt:\s*([-\d.]+)', data)
        if m: alt = float(m.group(1))
        m = re.search(r'gb_yaw:\s*([-\d.]+)', data)
        if m: yaw = float(m.group(1))
        entries[frame] = {'lat': lat, 'lon': lon, 'alt': alt, 'yaw': yaw}
    return entries


# ── HTML page ──
HTML_PAGE = """<!DOCTYPE html>
<html><head><title>SAR Passive Watch</title>
<style>
  *{margin:0;padding:0;box-sizing:border-box}
  body{background:#111;color:#eee;font-family:monospace;padding:15px}
  h1{color:#0f0;margin-bottom:8px}
  h2{color:#0ff;font-size:0.85em;margin:10px 0 5px}
  .stats{color:#888;margin-bottom:3px;font-size:0.85em}
  .gps{color:#0af;margin-bottom:3px;font-size:0.85em}
  .est{color:#ff00ff;margin-bottom:3px;font-weight:bold;font-size:0.85em}
  .fov{color:#b90;margin-bottom:8px;font-size:0.75em}
  img{border:1px solid #333;display:block}
  .grid{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px}
  .left img,.right img{width:100%;height:auto}
  .bottom{display:grid;grid-template-columns:1fr 1fr;gap:10px}
  .bottom img{width:100%;height:auto}
  @media(max-width:1000px){.grid,.bottom{grid-template-columns:1fr}}

  /* ── Model selector control bar ── */
  .ctrl-bar{
    display:flex;align-items:center;gap:12px;flex-wrap:wrap;
    background:#1a1a1a;border:1px solid #333;border-radius:4px;
    padding:6px 12px;margin-bottom:8px;font-size:0.8em;
  }
  .ctrl-bar label{color:#999;white-space:nowrap}
  .ctrl-bar select,.ctrl-bar input[type=text]{
    background:#222;color:#0f0;border:1px solid #444;border-radius:3px;
    padding:3px 6px;font-family:monospace;font-size:1em;
  }
  .ctrl-bar select:focus,.ctrl-bar input:focus{outline:none;border-color:#0f0}
  .ctrl-bar .slider-group{display:flex;align-items:center;gap:4px}
  .ctrl-bar input[type=range]{
    width:100px;accent-color:#0f0;cursor:pointer;
  }
  .ctrl-bar .conf-val{color:#0f0;min-width:32px;text-align:right}
  .ctrl-bar .sep{color:#333;margin:0 2px}
  .ctrl-bar .model-status{color:#666;font-size:0.9em}
  .ctrl-bar .model-status.loading{color:#ff0}
  .ctrl-bar .model-status.ok{color:#0f0}
  .ctrl-bar .model-status.err{color:#f44}
</style>
</head><body>
<h1>SAR Passive Watch</h1>

<!-- Model selector control bar -->
<div class="ctrl-bar">
  <label>Model:</label>
  <select id="model-sel">
    <option value="0">Original (best.tflite)</option>
    <option value="1">SAR v2 TFLite</option>
    <option value="2">SAR v2 NCNN</option>
    <option value="3">COCO Person</option>
  </select>
  <span class="model-status" id="model-status"></span>
  <span class="sep">|</span>

  <label>Conf:</label>
  <div class="slider-group">
    <input type="range" id="conf-slider" min="0.05" max="0.95" step="0.05" value="0.20">
    <span class="conf-val" id="conf-val">0.20</span>
  </div>
  <span class="sep">|</span>

  <label>Class:</label>
  <select id="class-sel">
    <option value="all">all</option>
    <option value="dummy">dummy</option>
    <option value="person">person</option>
  </select>
</div>

<div class="stats" id="stats">Starting...</div>
<div class="gps" id="gps">GPS: waiting...</div>
<div class="est" id="est">ESTIMATE: waiting...</div>
<div class="fov" id="fov">FOV: ---</div>

<div class="grid">
  <div class="left">
    <h2>Camera Feed</h2>
    <img src="/stream" alt="Stream">
  </div>
  <div class="right">
    <h2>Latest Detection</h2>
    <img id="latest" src="/latest" alt="Detection" style="min-height:150px">
    <h2>SMART Frames</h2>
    <img id="smart-grid" src="/smart-grid" alt="Grid" style="min-height:100px">
  </div>
</div>

<div class="bottom">
  <div>
    <h2>Satellite Map</h2>
    <div id="imap-host"></div>
  </div>
  <div>
    <h2>SMART Frames (10)</h2>
    <img id="smart-grid2" src="/smart-grid" alt="Grid" style="min-height:100px">
  </div>
</div>

<h2 style="margin-top:15px">GPS Analysis (5 plots)
  <button id="toggle-map-bg" onclick="toggleMapBG()" style="margin-left:12px;font-size:0.8em;padding:2px 8px;background:#222;color:#0f0;border:1px solid #444;border-radius:3px;cursor:pointer;font-family:monospace">Toggle Map BG</button>
  <span id="map-bg-status" style="font-size:0.7em;color:#666;margin-left:6px">off</span>
</h2>
<div style="overflow-x:auto;margin-bottom:10px">
  <img id="bullseye" src="/bullseye" alt="GPS Plots" style="max-width:100%;height:auto;border:1px solid #333">
</div>

<h2 style="margin-top:15px">CV Detection Pipeline</h2>
<div id="cv-pipeline-host"></div>

<h2 style="margin-top:15px">GPS Estimation Pipeline</h2>
<div id="gps-pipeline-host"></div>

<script>
/* ── Control bar logic ── */
const modelSel = document.getElementById('model-sel');
const confSlider = document.getElementById('conf-slider');
const confVal = document.getElementById('conf-val');
const classSel = document.getElementById('class-sel');
const modelStatus = document.getElementById('model-status');

function sendCmd(url) {
  return fetch(url).then(r => r.json()).catch(() => ({ok:false,error:'network'}));
}

modelSel.addEventListener('change', () => {
  modelStatus.textContent = 'loading...';
  modelStatus.className = 'model-status loading';
  sendCmd('/api/switch-model?id=' + modelSel.value).then(d => {
    if (d.ok) {
      modelStatus.textContent = d.model || 'ok';
      modelStatus.className = 'model-status ok';
    } else {
      modelStatus.textContent = d.error || 'failed';
      modelStatus.className = 'model-status err';
    }
  });
});

confSlider.addEventListener('input', () => {
  confVal.textContent = parseFloat(confSlider.value).toFixed(2);
});
confSlider.addEventListener('change', () => {
  sendCmd('/api/set-conf?val=' + confSlider.value);
});

classSel.addEventListener('change', () => {
  sendCmd('/api/set-class?name=' + classSel.value);
});

/* ── Status polling (sync active model/conf from server) ── */
setInterval(()=>{
  fetch('/api/status').then(r=>r.json()).then(d=>{
    document.getElementById('stats').textContent=
      `CAM:${d.cam_fps} VIS:${d.vis_fps} STR:${d.stream_fps} Det:${d.detections}(${d.det_pct}%) Saved:${d.saved}`;
    document.getElementById('gps').textContent=
      `DRONE:${d.gps_lat},${d.gps_lon} Alt:${d.alt}m Sats:${d.sats} Mode:${d.flight_mode}`;
    document.getElementById('est').textContent=d.est_obs>0
      ?`EST:${d.est_lat},${d.est_lon}(${d.est_obs}obs)`:'EST: waiting...';
    document.getElementById('fov').textContent=
      `FOV: ${d.fov_deg}\u00b0 | @1m: ${d.cal_1m_w}\u00d7${d.cal_1m_h}cm`;
    const t=Date.now();
    document.getElementById('latest').src='/latest?'+t;
    document.getElementById('smart-grid').src='/smart-grid?'+t;
    document.getElementById('bullseye').src='/bullseye?'+t;
    document.getElementById('smart-grid2').src='/smart-grid?'+t;
    /* Update pipeline visuals with live data */
    if (typeof updatePipelineData === 'function') {
      updatePipelineData({alt: parseFloat(d.alt)||0, fps: parseFloat(d.vis_fps)||0});
    }
    if (typeof updateGPSData === 'function') {
      updateGPSData({alt: parseFloat(d.alt)||0, fov_deg: parseFloat(d.fov_deg)||49.4});
    }
    /* Sync controls from server state */
    if (d.active_model_id !== undefined && document.activeElement !== modelSel) {
      modelSel.value = d.active_model_id;
    }
    if (d.conf_threshold !== undefined && document.activeElement !== confSlider) {
      confSlider.value = d.conf_threshold;
      confVal.textContent = parseFloat(d.conf_threshold).toFixed(2);
    }
    if (d.class_filter !== undefined && document.activeElement !== classSel) {
      classSel.value = d.class_filter;
    }
    if (d.bullseye_map_bg !== undefined) {
      document.getElementById('map-bg-status').textContent = d.bullseye_map_bg ? 'MAP' : 'off';
    }
  });
},2000);

function toggleMapBG() {
  fetch('/api/toggle-bullseye-bg').then(r=>r.json()).then(d=>{
    if(d.ok) document.getElementById('map-bg-status').textContent = d.map_bg ? 'MAP' : 'off';
  });
}
</script>
</body></html>"""


# ── HTTP Server ──
class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *a):
        pass  # silent

    def do_GET(self):
        global bullseye_map_bg
        path = self.path.split('?')[0]  # strip query string for matching
        if path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            # Inject interactive map into the imap-host placeholder
            from field_tools.interactive_map import get_interactive_map_html
            from field_tools.cv_pipeline_visual import get_cv_pipeline_html
            from field_tools.gps_pipeline_visual import get_gps_pipeline_html
            imap_html = get_interactive_map_html(
                container_id="map-container", width="100%", height="350px"
            )
            page = HTML_PAGE.replace(
                '<div id="imap-host"></div>',
                imap_html
            ).replace(
                '<div id="cv-pipeline-host"></div>',
                get_cv_pipeline_html()
            ).replace(
                '<div id="gps-pipeline-host"></div>',
                get_gps_pipeline_html()
            )
            self.wfile.write(page.encode())

        elif path == '/stream':
            self.send_response(200)
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=frame')
            self.end_headers()
            while True:
                try:
                    with frame_lock:
                        jpeg = latest_jpeg
                    if jpeg:
                        self.wfile.write(b'--frame\r\n')
                        self.wfile.write(b'Content-Type: image/jpeg\r\n\r\n')
                        self.wfile.write(jpeg)
                        self.wfile.write(b'\r\n')
                    time.sleep(0.02)  # ~50fps max stream (was 0.05=20fps)
                except BrokenPipeError:
                    break

        elif path == '/snapshot':
            with frame_lock:
                jpeg = latest_det_jpeg or latest_jpeg
            if jpeg:
                self.send_response(200)
                self.send_header('Content-Type', 'image/jpeg')
                self.end_headers()
                self.wfile.write(jpeg)
            else:
                self.send_response(503)
                self.end_headers()

        elif path == '/bullseye':
            with frame_lock:
                jpeg = latest_bullseye
            if jpeg:
                self.send_response(200)
                self.send_header('Content-Type', 'image/jpeg')
                self.send_header('Cache-Control', 'no-cache')
                self.end_headers()
                self.wfile.write(jpeg)
            else:
                self.send_response(503)
                self.end_headers()

        elif path == '/latest':
            with frame_lock:
                jpeg = latest_detection_jpeg
            if jpeg:
                self.send_response(200)
                self.send_header('Content-Type', 'image/jpeg')
                self.send_header('Cache-Control', 'no-cache')
                self.end_headers()
                self.wfile.write(jpeg)
            else:
                self.send_response(503)
                self.end_headers()

        elif path == '/smart-grid':
            with frame_lock:
                jpeg = latest_smart_grid_jpeg
            if jpeg:
                self.send_response(200)
                self.send_header('Content-Type', 'image/jpeg')
                self.send_header('Cache-Control', 'no-cache')
                self.end_headers()
                self.wfile.write(jpeg)
            else:
                self.send_response(503)
                self.end_headers()

        elif path == '/map':
            # Serve raw map image (loaded once by interactive canvas)
            import os as _os
            map_path = config.MAP_FILE
            if _os.path.exists(map_path):
                with open(map_path, 'rb') as f:
                    data = f.read()
                self.send_response(200)
                self.send_header('Content-Type', 'image/jpeg')
                self.send_header('Cache-Control', 'public, max-age=86400')
                self.send_header('Content-Length', str(len(data)))
                self.end_headers()
                self.wfile.write(data)
            else:
                self.send_response(404)
                self.end_headers()

        elif path == '/map-rendered':
            # Legacy: server-rendered map with dots (for non-JS clients)
            with frame_lock:
                jpeg = latest_map_jpeg
            if jpeg:
                self.send_response(200)
                self.send_header('Content-Type', 'image/jpeg')
                self.send_header('Cache-Control', 'no-cache')
                self.end_headers()
                self.wfile.write(jpeg)
            else:
                self.send_response(503)
                self.end_headers()

        elif path == '/api/drone':
            # Near-realtime drone telemetry for interactive map
            import json as _json
            with gps_lock:
                d = {
                    "lat": gps_data.get("lat", 0),
                    "lon": gps_data.get("lon", 0),
                    "alt": gps_data.get("alt", 0),
                    "yaw": gps_data.get("yaw", 0),
                    "sats": gps_data.get("sats", 0),
                    "mode": gps_data.get("mode", "---"),
                }
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            self.wfile.write(_json.dumps(d).encode())

        elif path == '/api/estimates':
            # GPS detection estimates for interactive map
            import json as _json
            est_list = [[e[0], e[1]] for e in _all_gps_estimates]
            smart = None
            if smart_estimator and smart_estimator.locked:
                med = smart_estimator.get_median()
                if med:
                    smart = [med[0], med[1]]
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            self.wfile.write(_json.dumps({"estimates": est_list, "smart": smart}).encode())

        elif path == '/api/status':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            import json
            with runtime_lock:
                stats["active_model_id"] = runtime_state["active_model_id"]
                stats["conf_threshold"] = runtime_state["conf_threshold"]
                stats["class_filter"] = runtime_state["class_filter"]
                stats["bullseye_map_bg"] = bullseye_map_bg
            with frame_lock:
                status_json = json.dumps(stats).encode()
            self.wfile.write(status_json)

        elif path == '/api/switch-model':
            # GET /api/switch-model?id=0|1|2|3
            self._send_json_response(self._handle_switch_model())

        elif path == '/api/set-conf':
            # GET /api/set-conf?val=0.25
            self._send_json_response(self._handle_set_conf())

        elif path == '/api/set-class':
            # GET /api/set-class?name=person|dummy|all
            self._send_json_response(self._handle_set_class())

        elif path == '/api/toggle-bullseye-bg':
            bullseye_map_bg = not bullseye_map_bg
            self._send_json_response({"ok": True, "map_bg": bullseye_map_bg})

        else:
            self.send_response(404)
            self.end_headers()

    def _send_json_response(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _parse_qs(self):
        """Parse query string from self.path → dict."""
        from urllib.parse import urlparse, parse_qs
        qs = parse_qs(urlparse(self.path).query)
        return {k: v[0] for k, v in qs.items()}

    def _handle_switch_model(self):
        params = self._parse_qs()
        try:
            mid = int(params.get('id', -1))
        except (ValueError, TypeError):
            return {"ok": False, "error": "invalid id"}
        if mid < 0 or mid >= len(MODEL_TABLE):
            return {"ok": False, "error": f"id must be 0-{len(MODEL_TABLE)-1}"}
        with runtime_lock:
            runtime_state["model_switch_request"] = mid
        # Wait briefly for main loop to pick it up (up to 3s)
        for _ in range(30):
            time.sleep(0.1)
            with runtime_lock:
                if runtime_state["model_switch_request"] is None:
                    return {"ok": True, "model": MODEL_TABLE[mid]["name"],
                            "id": mid, "path": MODEL_TABLE[mid]["path"]}
        return {"ok": False, "error": "timeout waiting for model switch"}

    def _handle_set_conf(self):
        params = self._parse_qs()
        try:
            val = float(params.get('val', -1))
        except (ValueError, TypeError):
            return {"ok": False, "error": "invalid val"}
        if val < 0.01 or val > 0.99:
            return {"ok": False, "error": "val must be 0.01-0.99"}
        with runtime_lock:
            runtime_state["conf_threshold"] = val
        return {"ok": True, "conf": val}

    def _handle_set_class(self):
        params = self._parse_qs()
        name = params.get('name', '').strip().lower()
        if not name:
            return {"ok": False, "error": "missing name"}
        with runtime_lock:
            runtime_state["class_filter"] = name
        return {"ok": True, "class_filter": name}


class ThreadedServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True


# ── Stats (FOV fields populated after get_fov_info is defined) ──
stats = {
    "frames": 0, "detections": 0, "det_pct": "0", "saved": 0,
    "cam_fps": "0.0", "vis_fps": "0.0", "stream_fps": "0.0",
    "gps_lat": "---", "gps_lon": "---", "alt": "---", "sats": 0, "flight_mode": "---",
    "est_lat": "---", "est_lon": "---", "est_obs": 0,
    "fov_deg": "---", "cal_1m_w": "---", "cal_1m_h": "---",
}

# ── Rolling FPS trackers ──
class RollingFPS:
    """Track FPS over a rolling window."""
    def __init__(self, window=3.0):
        self.window = window
        self.times = []

    def tick(self):
        now = time.time()
        self.times.append(now)
        cutoff = now - self.window
        self.times = [t for t in self.times if t > cutoff]

    def fps(self):
        if len(self.times) < 2:
            return 0.0
        span = self.times[-1] - self.times[0]
        if span <= 0:
            return 0.0
        return (len(self.times) - 1) / span

cam_fps_tracker = RollingFPS()
vis_fps_tracker = RollingFPS()
stream_fps_tracker = RollingFPS()

# ── FOV / Calibration info ──
def get_fov_info():
    """Calculate FOV and ground coverage at various altitudes."""
    sw = config.SENSOR_WIDTH_MM
    fl = config.FOCAL_LENGTH_MM
    iw = config.IMAGE_W
    ih = config.IMAGE_H

    hfov_deg = 2 * math.degrees(math.atan(sw / (2 * fl)))
    vfov_deg = hfov_deg * ih / iw  # assuming square pixels
    f_px = fl * iw / sw  # focal length in pixels

    return {
        "hfov_deg": hfov_deg,
        "vfov_deg": vfov_deg,
        "f_px": f_px,
        "sensor_w": sw,
        "focal_mm": fl,
        "img_w": iw,
        "img_h": ih,
    }

def ground_coverage(alt_m):
    """Return (width_m, height_m) of ground visible at given altitude."""
    sw = config.SENSOR_WIDTH_MM
    fl = config.FOCAL_LENGTH_MM
    w = alt_m * sw / fl
    h = w * config.IMAGE_H / config.IMAGE_W
    return w, h

FOV = get_fov_info()

# Now populate FOV stats
stats["fov_deg"] = f"{FOV['hfov_deg']:.0f}"
stats["cal_1m_w"] = f"{ground_coverage(1.0)[0]*100:.0f}"
stats["cal_1m_h"] = f"{ground_coverage(1.0)[1]*100:.0f}"


# ── Dummy position estimator ──
class DummyEstimator:
    """Accumulate detection observations → estimate dummy GPS position.

    Uses inverse-variance weighting (lower altitude = more weight).
    """
    def __init__(self):
        self.total_weight = 0.0
        self.weighted_lat = 0.0
        self.weighted_lon = 0.0
        self.count = 0

    def add_observation(self, drone_lat, drone_lon, alt_m, yaw_deg, det_x, det_y):
        """Estimate dummy GPS from one detection.

        det_x, det_y: normalised detection coords (0-1, center of detection).
        Returns (est_lat, est_lon) or None if can't estimate.
        """
        if alt_m < 0.3:
            alt_m = 0.3  # clamp to min 30cm to avoid division issues

        # Pixel offset from frame centre
        dx_px = (det_x - 0.5) * FOV["img_w"]
        dy_px = (det_y - 0.5) * FOV["img_h"]

        # Metres on ground
        dx_m = dx_px * alt_m / FOV["f_px"]
        dy_m = dy_px * alt_m / FOV["f_px"]

        # Rotate by yaw (yaw=0 means North, positive clockwise)
        # Camera: top of image = drone forward
        # dx_px positive = target right of centre → East when yaw=0
        # dy_px positive = target below centre → South when yaw=0 (camera down, +y = forward away = South... no)
        # Actually: camera facing down, top of image = drone forward
        # dy_px negative = target above centre = further forward = more North
        # dy_px positive = target below centre = behind drone = more South
        yaw_rad = math.radians(yaw_deg)
        # Forward (negative dy) maps to North, Right (positive dx) maps to East at yaw=0
        forward_m = -dy_m  # negative dy = forward = North
        right_m = dx_m     # positive dx = right = East

        # Rotate by yaw
        north_m = forward_m * math.cos(yaw_rad) - right_m * math.sin(yaw_rad)
        east_m = forward_m * math.sin(yaw_rad) + right_m * math.cos(yaw_rad)

        # Convert metres to GPS offset
        lat_m_per_deg = 111320
        lon_m_per_deg = 111320 * math.cos(math.radians(drone_lat))

        est_lat = drone_lat + north_m / lat_m_per_deg
        est_lon = drone_lon + east_m / lon_m_per_deg

        # Weight: inverse altitude squared (10m obs is 9x more valuable than 30m)
        weight = 1.0 / (alt_m * alt_m)

        # Bonus: detection near frame centre = less projection error
        dist_from_centre = math.sqrt(dx_px**2 + dy_px**2)
        max_dist = math.sqrt((FOV["img_w"]/2)**2 + (FOV["img_h"]/2)**2)
        centre_factor = 1.0 + 4.0 * max(0, 1.0 - dist_from_centre / (max_dist * 0.3))
        weight *= centre_factor

        self.weighted_lat += est_lat * weight
        self.weighted_lon += est_lon * weight
        self.total_weight += weight
        self.count += 1

        return est_lat, est_lon

    def get_estimate(self):
        """Return (lat, lon, n_observations) or None."""
        if self.total_weight <= 0:
            return None
        return (
            self.weighted_lat / self.total_weight,
            self.weighted_lon / self.total_weight,
            self.count
        )

    def reset(self):
        self.total_weight = 0.0
        self.weighted_lat = 0.0
        self.weighted_lon = 0.0
        self.count = 0

dummy_estimator = DummyEstimator()


class SmartEstimator:
    """Greedy tightest cluster: find 10 estimates closest to each other."""
    def __init__(self, min_samples=10, max_spread=0.5):
        self.min_samples = min_samples
        self.max_spread = max_spread  # meters — all 10 must be within this
        self.all_estimates = []  # (est_lat, est_lon, pixel_dist, frame)
        self.locked = False
        self.locked_cluster = None  # list of (lat, lon, pixel_dist)
        self.locked_frame = None    # most central frame from cluster
        self.locked_spread = 0

    def add(self, est_lat, est_lon, pixel_dist, frame):
        """Add detection. Returns True if cluster just locked."""
        if self.locked:
            return False
        self.all_estimates.append((est_lat, est_lon, pixel_dist, frame.copy()))

        if len(self.all_estimates) < self.min_samples:
            return False

        # Find tightest 10
        indices, spread = self._find_tightest(self.min_samples)
        n = len(self.all_estimates)
        print(f"  [SMART] {n} detections, tightest {self.min_samples} spread: {spread:.2f}m (need <{self.max_spread}m)")

        if spread < self.max_spread:
            # LOCKED — save cluster
            self.locked = True
            self.locked_spread = spread
            cluster = [self.all_estimates[i] for i in indices]
            self.locked_cluster = [(e[0], e[1], e[2]) for e in cluster]
            # Most central frame (smallest pixel_dist)
            best = min(cluster, key=lambda e: e[2])
            self.locked_frame = best[3]
            med = self.get_median()
            print(f"  [SMART] *** LOCKED! Spread: {spread:.2f}m ***")
            print(f"  [SMART] Median: {med[0]:.7f}, {med[1]:.7f} ({med[2]} samples)")
            return True
        return False

    def _find_tightest(self, target_size):
        """Greedy: find target_size points closest to each other."""
        estimates = self.all_estimates
        n = len(estimates)

        # Pairwise distances
        mean_lat = sum(e[0] for e in estimates) / n
        dists = {}
        for i in range(n):
            for j in range(i + 1, n):
                dn = (estimates[i][0] - estimates[j][0]) * 111320
                de = (estimates[i][1] - estimates[j][1]) * 111320 * math.cos(math.radians(mean_lat))
                dists[(i, j)] = math.sqrt(dn**2 + de**2)

        if n <= target_size:
            spread = max(dists.values()) if dists else 0
            return list(range(n)), spread

        # Seed from closest pair
        min_pair = min(dists, key=dists.get)
        cluster = set(min_pair)

        # Greedily add point minimizing max spread
        while len(cluster) < target_size:
            best_pt = -1
            best_spread = float('inf')
            for c in range(n):
                if c in cluster:
                    continue
                max_d = max(dists.get((min(c, m), max(c, m)), 0) for m in cluster)
                if max_d < best_spread:
                    best_spread = max_d
                    best_pt = c
            if best_pt >= 0:
                cluster.add(best_pt)
            else:
                break

        cluster_list = sorted(cluster)
        spread = 0
        for i in cluster_list:
            for j in cluster_list:
                if i < j:
                    spread = max(spread, dists.get((i, j), 0))
        return cluster_list, spread

    def ready(self):
        return self.locked

    def get_median(self):
        """Return (median_lat, median_lon, n_samples)."""
        if not self.locked_cluster:
            return None
        lats = sorted(e[0] for e in self.locked_cluster)
        lons = sorted(e[1] for e in self.locked_cluster)
        n = len(lats)
        mid = n // 2
        if n % 2 == 0:
            m_lat = (lats[mid - 1] + lats[mid]) / 2
            m_lon = (lons[mid - 1] + lons[mid]) / 2
        else:
            m_lat = lats[mid]
            m_lon = lons[mid]
        return m_lat, m_lon, n

    def get_cep50(self):
        """Circular error probable — median distance from median center."""
        med = self.get_median()
        if not med:
            return 0
        m_lat, m_lon, _ = med
        dists = []
        for lat, lon, _ in self.locked_cluster:
            dn = (lat - m_lat) * 111320
            de = (lon - m_lon) * 111320 * math.cos(math.radians(m_lat))
            dists.append(math.sqrt(dn**2 + de**2))
        dists.sort()
        return dists[len(dists) // 2] if dists else 0

smart_estimator = None  # initialized in main() if --smart-estimate


def render_latest_detection(frame, last_det, gps_d):
    """Render latest detection thumbnail with arrow from center."""
    global latest_detection_jpeg
    if frame is None or last_det is None:
        return
    h, w = frame.shape[:2]
    thumb_w = 480
    s = thumb_w / w
    thumb = cv2.resize(frame, (thumb_w, int(h * s)))
    th = thumb.shape[0]
    dcx, dcy = int(last_det[0] * s), int(last_det[1] * s)
    fcx, fcy = thumb_w // 2, th // 2
    # Crosshair at frame center
    cv2.line(thumb, (fcx - 15, fcy), (fcx + 15, fcy), (0, 255, 255), 1)
    cv2.line(thumb, (fcx, fcy - 15), (fcx, fcy + 15), (0, 255, 255), 1)
    # Pink line: center → detection (matching draw_overlay style)
    cv2.line(thumb, (fcx, fcy), (dcx, dcy), (255, 0, 255), 2)
    # Pink dot at detection center
    cv2.circle(thumb, (dcx, dcy), 8, (255, 0, 255), -1)
    cv2.circle(thumb, (dcx, dcy), 8, (255, 255, 255), 1)
    # Pixel + real distance at midpoint
    px_dist = math.sqrt((dcx - fcx)**2 + (dcy - fcy)**2)
    mid_x = (fcx + dcx) // 2
    mid_y = (fcy + dcy) // 2
    cv2.putText(thumb, f"{px_dist:.0f}px", (mid_x + 6, mid_y - 6),
                cv2.FONT_HERSHEY_SIMPLEX, 0.38, (255, 0, 255), 1)
    alt_snap = gps_d.get('alt', 0)
    if alt_snap > 0.5:
        fov_h_rad = math.radians(FOV["hfov_deg"])
        gw = 2 * alt_snap * math.tan(fov_h_rad / 2)
        # px_dist is in thumbnail coords, convert back to original scale
        dist_m = (px_dist / s) / (w / gw)
        cv2.putText(thumb, f"{dist_m:.1f}m", (mid_x + 6, mid_y + 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, (0, 255, 255), 1)
    # Info bar
    cv2.rectangle(thumb, (0, th - 25), (thumb_w, th), (0, 0, 0), -1)
    info = f"{getattr(draw_overlay, '_last_class', '?')} {last_det[2]:.2f} | {gps_d['alt']:.0f}m | {gps_d['lat']:.5f},{gps_d['lon']:.5f}"
    cv2.putText(thumb, info, (5, th - 7), cv2.FONT_HERSHEY_SIMPLEX, 0.32, (200, 200, 200), 1)
    _, jpg = cv2.imencode('.jpg', thumb, [cv2.IMWRITE_JPEG_QUALITY, 80])
    with frame_lock:
        latest_detection_jpeg = jpg.tobytes()


def render_smart_grid(smart_est):
    """Render 5x2 grid of locked smart frames."""
    global latest_smart_grid_jpeg
    if not smart_est or not smart_est.all_estimates:
        return
    frames = [e[3] for e in smart_est.all_estimates if len(e) >= 4 and e[3] is not None][:10]
    if not frames:
        return
    cw, ch = 240, 180
    grid = np.zeros((ch * 2, cw * 5, 3), dtype=np.uint8)
    for i, f in enumerate(frames[:10]):
        r, c = i // 5, i % 5
        thumb = cv2.resize(f, (cw, ch))
        grid[r*ch:(r+1)*ch, c*cw:(c+1)*cw] = thumb
        cv2.putText(grid, f"#{i+1}", (c*cw+5, r*ch+18), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 1)
        if smart_est.locked:
            cv2.rectangle(grid, (c*cw, r*ch), ((c+1)*cw-1, (r+1)*ch-1), (0, 255, 0), 2)
    _, jpg = cv2.imencode('.jpg', grid, [cv2.IMWRITE_JPEG_QUALITY, 80])
    with frame_lock:
        latest_smart_grid_jpeg = jpg.tobytes()


def render_map(all_estimates, smart_est=None):
    """Render GPS estimates on satellite map."""
    global latest_map_jpeg, _map_base
    if _map_base is None:
        # Try loading map
        map_path = config.MAP_FILE
        if os.path.exists(map_path):
            img = cv2.imread(map_path)
            if img is not None:
                _map_base = cv2.resize(img, (600, int(img.shape[0] * 600 / img.shape[1])))
        if _map_base is None:
            # Placeholder
            _map_base = np.zeros((400, 600, 3), dtype=np.uint8)
            cv2.putText(_map_base, "map.jpg not found", (150, 200),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 100, 100), 1)
    disp = _map_base.copy()
    mh, mw = disp.shape[:2]

    def gps_to_px(lat, lon):
        dn = (config.REF_LAT - lat) * 111320
        de = (lon - config.REF_LON) * 111320 * math.cos(math.radians(config.REF_LAT))
        px = int(de / config.MAP_WIDTH_METERS * mw)
        py = int(dn / config.MAP_WIDTH_METERS * mw)
        return px, py

    # Plot all estimates
    for e in all_estimates:
        lat, lon = e[0], e[1]
        px, py = gps_to_px(lat, lon)
        if 0 <= px < mw and 0 <= py < mh:
            cv2.circle(disp, (px, py), 3, (0, 255, 0), -1)

    # Smart median star
    if smart_est and smart_est.locked:
        med = smart_est.get_median()
        if med:
            px, py = gps_to_px(med[0], med[1])
            if 0 <= px < mw and 0 <= py < mh:
                cv2.drawMarker(disp, (px, py), (255, 0, 255), cv2.MARKER_STAR, 15, 2)

    # Drone position
    with gps_lock:
        _drone_lat, _drone_lon = gps_data["lat"], gps_data["lon"]
    if _drone_lat != 0:
        px, py = gps_to_px(_drone_lat, _drone_lon)
        if 0 <= px < mw and 0 <= py < mh:
            cv2.circle(disp, (px, py), 5, (255, 0, 0), -1)

    # Title
    cv2.rectangle(disp, (0, 0), (mw, 20), (0, 0, 0), -1)
    cv2.putText(disp, f"MAP: {len(all_estimates)} estimates", (5, 15),
               cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)

    _, jpg = cv2.imencode('.jpg', disp, [cv2.IMWRITE_JPEG_QUALITY, 80])
    with frame_lock:
        latest_map_jpeg = jpg.tobytes()


def render_bullseye(all_estimates, smart_est=None):
    """Render 5 GPS plot types side-by-side (or 3 when smart disabled).

    all_estimates: list of (est_lat, est_lon, pixel_dist, altitude, confidence)
    smart_est: SmartEstimator or None
    """
    global latest_bullseye
    S = 350          # each plot is SxS
    BG = (20, 20, 20)
    SEP = 2          # separator width
    RING_CLR = (40, 40, 40)
    MARGIN = 35

    def heat_color(val):
        """val 0->1 maps green->red as BGR."""
        v = max(0.0, min(1.0, val))
        return (0, int(255 * (1 - v)), int(255 * v))

    def make_panel():
        return np.full((S, S, 3), BG, dtype=np.uint8)

    def make_map_panel(mean_lat, mean_lon, range_m):
        """Crop satellite map centered on mean GPS, covering range_m in each direction.
        Returns SxS image, or dark panel if map unavailable."""
        global _map_base
        if _map_base is None:
            map_path = config.MAP_FILE
            if os.path.exists(map_path):
                img = cv2.imread(map_path)
                if img is not None:
                    _map_base = cv2.resize(img, (600, int(img.shape[0] * 600 / img.shape[1])))
        if _map_base is None:
            return make_panel()

        mh, mw = _map_base.shape[:2]
        # GPS to pixel on the map
        dn = (config.REF_LAT - mean_lat) * 111320
        de = (mean_lon - config.REF_LON) * 111320 * math.cos(math.radians(config.REF_LAT))
        center_px = int(de / config.MAP_WIDTH_METERS * mw)
        center_py = int(dn / config.MAP_WIDTH_METERS * mw)
        # Crop radius in pixels: range_m maps to half the panel
        px_per_m = mw / config.MAP_WIDTH_METERS
        half_px = int(range_m * px_per_m)
        if half_px < 10:
            half_px = 50  # minimum crop size

        x1 = center_px - half_px
        y1 = center_py - half_px
        x2 = center_px + half_px
        y2 = center_py + half_px

        # Clamp to map bounds, pad with black if out of range
        pad_l = max(0, -x1)
        pad_t = max(0, -y1)
        pad_r = max(0, x2 - mw)
        pad_b = max(0, y2 - mh)
        cx1 = max(0, x1)
        cy1 = max(0, y1)
        cx2 = min(mw, x2)
        cy2 = min(mh, y2)

        if cx2 <= cx1 or cy2 <= cy1:
            return make_panel()

        crop = _map_base[cy1:cy2, cx1:cx2].copy()
        if pad_l or pad_t or pad_r or pad_b:
            crop = cv2.copyMakeBorder(crop, pad_t, pad_b, pad_l, pad_r,
                                       cv2.BORDER_CONSTANT, value=(0, 0, 0))

        panel = cv2.resize(crop, (S, S))
        # Semi-transparent dark overlay for readability
        overlay = np.full((S, S, 3), (0, 0, 0), dtype=np.uint8)
        cv2.addWeighted(panel, 0.6, overlay, 0.4, 0, panel)
        return panel

    def draw_rings(panel, cx, cy, rings_m, scale, usable):
        for r_m in rings_m:
            r_px = int(r_m * scale)
            if 5 < r_px < usable // 2:
                cv2.circle(panel, (cx, cy), r_px, RING_CLR, 1)
                cv2.putText(panel, f"{r_m}m", (cx + r_px + 2, cy - 2),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.25, (60, 60, 60), 1)

    def gps_to_meters(lat, lon, ref_lat, ref_lon):
        n = (lat - ref_lat) * 111320
        e = (lon - ref_lon) * 111320 * math.cos(math.radians(ref_lat))
        return e, n

    def auto_scale(pts_m, margin=MARGIN):
        """Compute scale from point cloud, returns (scale, usable, cx, cy)."""
        dists = [math.sqrt(p[0]**2 + p[1]**2) for p in pts_m]
        p95 = sorted(dists)[int(len(dists) * 0.95)] if dists else 5.0
        max_range = max(p95 * 2, 3.0)
        usable = S - 2 * margin
        sc = usable / max_range
        return sc, usable, S // 2, S // 2

    # ── Empty state ──
    has_smart = smart_est is not None
    n_plots = 5 if has_smart else 3
    total_w = n_plots * S + (n_plots - 1) * SEP

    if not all_estimates:
        plot = np.full((S, total_w, 3), BG, dtype=np.uint8)
        cv2.putText(plot, "Waiting for detections...", (50, S // 2),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 100), 1)
        _, jpg = cv2.imencode('.jpg', plot, [cv2.IMWRITE_JPEG_QUALITY, 80])
        with frame_lock:
            latest_bullseye = jpg.tobytes()
        return

    # ── Shared data ──
    lats = [e[0] for e in all_estimates]
    lons = [e[1] for e in all_estimates]
    mean_lat = sum(lats) / len(lats)
    mean_lon = sum(lons) / len(lons)

    pts_m = []   # (east_m, north_m, pixel_dist, altitude, confidence)
    for est_e in all_estimates:
        lat, lon = est_e[0], est_e[1]
        pdist = est_e[2]
        alt = est_e[3] if len(est_e) > 3 else 0
        conf = est_e[4] if len(est_e) > 4 else 0
        em, nm = gps_to_meters(lat, lon, mean_lat, mean_lon)
        pts_m.append((em, nm, pdist, alt, conf))

    dists_from_mean = [math.sqrt(p[0]**2 + p[1]**2) for p in pts_m]
    cep50 = sorted(dists_from_mean)[len(dists_from_mean) // 2] if dists_from_mean else 0
    max_spread = max(dists_from_mean) if dists_from_mean else 0
    scale, usable, cx, cy = auto_scale([(p[0], p[1]) for p in pts_m])

    panels = []

    # ── Compute map range for satellite background ──
    # Range in meters from center that the plot covers (matches auto_scale)
    _dists = [math.sqrt(p[0]**2 + p[1]**2) for p in pts_m]
    _p95 = sorted(_dists)[int(len(_dists) * 0.95)] if _dists else 5.0
    _map_range_m = max(_p95 * 1.1, 2.0)  # slightly beyond 95th percentile

    # ════════════════════════════════════════════════════════════
    # PLOT 1: GPS by Center Distance (pixel centrality)
    # ════════════════════════════════════════════════════════════
    p1 = make_map_panel(mean_lat, mean_lon, _map_range_m) if bullseye_map_bg else make_panel()
    cv2.putText(p1, f"BY CENTER DIST (N={len(all_estimates)})", (5, 15),
               cv2.FONT_HERSHEY_SIMPLEX, 0.38, (200, 200, 200), 1)

    draw_rings(p1, cx, cy, [1, 2, 3, 5, 10], scale, usable)
    cv2.drawMarker(p1, (cx, cy), (0, 255, 0), cv2.MARKER_CROSS, 12, 2)

    max_pd = max(p[2] for p in pts_m) if pts_m else 1
    for em, nm, pdist, alt, conf in pts_m:
        px = cx + int(em * scale)
        py = cy - int(nm * scale)
        if MARGIN < px < S - MARGIN and MARGIN < py < S - MARGIN:
            val = min(1.0, pdist / max(max_pd, 1))
            cv2.circle(p1, (px, py), 3, heat_color(val), -1)

    cv2.putText(p1, f"CEP50: {cep50:.1f}m  max: {max_spread:.1f}m", (5, S - 20),
               cv2.FONT_HERSHEY_SIMPLEX, 0.32, (180, 180, 180), 1)
    est = dummy_estimator.get_estimate()
    if est:
        cv2.putText(p1, f"Est: {est[0]:.6f}, {est[1]:.6f}", (5, S - 5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.30, (255, 0, 255), 1)
    panels.append(p1)

    # ════════════════════════════════════════════════════════════
    # PLOT 2: GPS by Altitude
    # ════════════════════════════════════════════════════════════
    p2 = make_map_panel(mean_lat, mean_lon, _map_range_m) if bullseye_map_bg else make_panel()
    alts = [p[3] for p in pts_m]
    min_alt = min(alts) if alts else 0
    max_alt = max(alts) if alts else 1
    alt_range = max(max_alt - min_alt, 0.1)

    cv2.putText(p2, f"BY ALTITUDE ({min_alt:.0f}-{max_alt:.0f}m)", (5, 15),
               cv2.FONT_HERSHEY_SIMPLEX, 0.38, (200, 200, 200), 1)

    draw_rings(p2, cx, cy, [1, 2, 3, 5, 10], scale, usable)
    cv2.drawMarker(p2, (cx, cy), (0, 255, 0), cv2.MARKER_CROSS, 12, 2)

    for em, nm, pdist, alt, conf in pts_m:
        px = cx + int(em * scale)
        py = cy - int(nm * scale)
        if MARGIN < px < S - MARGIN and MARGIN < py < S - MARGIN:
            val = (alt - min_alt) / alt_range
            cv2.circle(p2, (px, py), 3, heat_color(val), -1)

    # Color bar (vertical, right side)
    bar_x = S - 18
    bar_top, bar_bot = 30, S - 40
    for y in range(bar_top, bar_bot):
        val = (y - bar_top) / max(bar_bot - bar_top, 1)
        cv2.line(p2, (bar_x, y), (bar_x + 8, y), heat_color(val), 1)
    cv2.putText(p2, f"{min_alt:.0f}", (bar_x - 5, bar_top - 3),
               cv2.FONT_HERSHEY_SIMPLEX, 0.22, (120, 120, 120), 1)
    cv2.putText(p2, f"{max_alt:.0f}", (bar_x - 5, bar_bot + 10),
               cv2.FONT_HERSHEY_SIMPLEX, 0.22, (120, 120, 120), 1)

    cv2.putText(p2, f"CEP50: {cep50:.1f}m", (5, S - 5),
               cv2.FONT_HERSHEY_SIMPLEX, 0.32, (180, 180, 180), 1)
    panels.append(p2)

    # ════════════════════════════════════════════════════════════
    # PLOT 3: Error Convergence (line chart)
    # ════════════════════════════════════════════════════════════
    p3 = make_panel()
    cv2.putText(p3, "ERROR CONVERGENCE", (5, 15),
               cv2.FONT_HERSHEY_SIMPLEX, 0.38, (200, 200, 200), 1)

    n_pts = len(pts_m)
    if n_pts >= 2:
        # Compute running estimates for each detection count
        running_mean_err = []
        running_weighted_err = []
        running_median_err = []

        for k in range(1, n_pts + 1):
            subset = pts_m[:k]
            # Running mean
            rm_e = sum(p[0] for p in subset) / k
            rm_n = sum(p[1] for p in subset) / k
            # Running weighted by 1/cdist^2
            total_w_val = 0
            w_e, w_n = 0, 0
            for p in subset:
                cdist = max(p[2], 1.0)
                w = 1.0 / (cdist * cdist)
                w_e += p[0] * w
                w_n += p[1] * w
                total_w_val += w
            if total_w_val > 0:
                w_e /= total_w_val
                w_n /= total_w_val
            # Running median
            sorted_e = sorted(p[0] for p in subset)
            sorted_n = sorted(p[1] for p in subset)
            med_e = sorted_e[len(sorted_e) // 2]
            med_n = sorted_n[len(sorted_n) // 2]

            # Error = distance from final mean (best estimate)
            final_mean_e = sum(p[0] for p in pts_m) / n_pts
            final_mean_n = sum(p[1] for p in pts_m) / n_pts
            running_mean_err.append(math.sqrt((rm_e - final_mean_e)**2 + (rm_n - final_mean_n)**2))
            running_weighted_err.append(math.sqrt((w_e - final_mean_e)**2 + (w_n - final_mean_n)**2))
            running_median_err.append(math.sqrt((med_e - final_mean_e)**2 + (med_n - final_mean_n)**2))

        # Chart area
        chart_l, chart_r = 45, S - 10
        chart_t, chart_b = 30, S - 25
        chart_w = chart_r - chart_l
        chart_h = chart_b - chart_t

        # Y axis max
        all_errs = running_mean_err + running_weighted_err + running_median_err
        y_max = max(all_errs) if all_errs else 1.0
        y_max = max(y_max, 0.5)

        # Grid lines
        for ym in [0.5, 1.0, 2.0, 5.0, 10.0]:
            if ym <= y_max:
                gy = chart_b - int((ym / y_max) * chart_h)
                cv2.line(p3, (chart_l, gy), (chart_r, gy), (40, 40, 40), 1)
                cv2.putText(p3, f"{ym:.1f}m", (2, gy + 4),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.22, (80, 80, 80), 1)

        # Axes
        cv2.line(p3, (chart_l, chart_t), (chart_l, chart_b), (60, 60, 60), 1)
        cv2.line(p3, (chart_l, chart_b), (chart_r, chart_b), (60, 60, 60), 1)

        def plot_line(errs, color):
            prev = None
            for i, err in enumerate(errs):
                x = chart_l + int((i / max(n_pts - 1, 1)) * chart_w)
                y = chart_b - int((min(err, y_max) / y_max) * chart_h)
                if prev is not None:
                    cv2.line(p3, prev, (x, y), color, 1)
                prev = (x, y)

        plot_line(running_mean_err, (0, 255, 0))       # green = mean
        plot_line(running_weighted_err, (255, 255, 0))  # cyan = weighted
        plot_line(running_median_err, (255, 0, 255))    # magenta = median

        # Legend
        ly = S - 8
        cv2.putText(p3, "mean", (chart_l, ly), cv2.FONT_HERSHEY_SIMPLEX, 0.25, (0, 255, 0), 1)
        cv2.putText(p3, "weighted", (chart_l + 45, ly), cv2.FONT_HERSHEY_SIMPLEX, 0.25, (255, 255, 0), 1)
        cv2.putText(p3, "median", (chart_l + 110, ly), cv2.FONT_HERSHEY_SIMPLEX, 0.25, (255, 0, 255), 1)

        # X axis label
        cv2.putText(p3, f"N={n_pts}", (chart_r - 30, chart_b + 12),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.25, (100, 100, 100), 1)
    else:
        cv2.putText(p3, "Need 2+ detections", (30, S // 2),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (100, 100, 100), 1)
    panels.append(p3)

    # ════════════════════════════════════════════════════════════
    # PLOT 4: Smart Bullseye (tightest 10) — only if smart enabled
    # ════════════════════════════════════════════════════════════
    if has_smart:
        p4 = make_panel()
        if smart_est.locked and smart_est.locked_cluster:
            cluster = smart_est.locked_cluster  # list of (lat, lon, pixel_dist)
            cv2.putText(p4, "LOCKED", (5, 15),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 255, 0), 2)
            cv2.putText(p4, f"spread: {smart_est.locked_spread:.2f}m", (80, 15),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.32, (0, 255, 0), 1)

            c_lats = [e[0] for e in cluster]
            c_lons = [e[1] for e in cluster]
            c_mean_lat = sum(c_lats) / len(c_lats)
            c_mean_lon = sum(c_lons) / len(c_lons)
            c_pts = []
            for c_e in cluster:
                em, nm = gps_to_meters(c_e[0], c_e[1], c_mean_lat, c_mean_lon)
                c_pts.append((em, nm, c_e[2]))

            c_dists = [math.sqrt(p[0]**2 + p[1]**2) for p in c_pts]
            c_max = max(c_dists) * 1.5 if c_dists else 1.0
            c_max = max(c_max, 0.5)
            c_usable = S - 2 * MARGIN
            c_scale = c_usable / (2 * c_max)
            c_cx, c_cy = S // 2, S // 2

            draw_rings(p4, c_cx, c_cy, [0.1, 0.2, 0.5, 1.0], c_scale, c_usable)
            cv2.drawMarker(p4, (c_cx, c_cy), (0, 255, 255), cv2.MARKER_CROSS, 15, 2)

            for i, (em, nm, pdist) in enumerate(c_pts):
                px = c_cx + int(em * c_scale)
                py = c_cy - int(nm * c_scale)
                cv2.circle(p4, (px, py), 5, (0, 255, 255), -1)
                cv2.circle(p4, (px, py), 5, (255, 255, 255), 1)
                # Number label
                cv2.putText(p4, str(i + 1), (px + 7, py + 3),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.25, (200, 200, 200), 1)
                # Radial line from center
                cv2.line(p4, (c_cx, c_cy), (px, py), (40, 40, 40), 1)

            med = smart_est.get_median()
            if med:
                cv2.putText(p4, f"Med: {med[0]:.7f}, {med[1]:.7f}",
                           (5, S - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.28, (255, 0, 255), 1)
                cv2.putText(p4, f"N={med[2]} | CEP: {smart_est.get_cep50():.2f}m",
                           (5, S - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.28, (200, 200, 200), 1)
        else:
            n_est = len(smart_est.all_estimates)
            cv2.putText(p4, "searching...", (5, 15),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255, 0, 255), 1)
            cv2.putText(p4, f"{n_est} detections", (5, 35),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.35, (150, 150, 150), 1)
            cv2.putText(p4, f"Need tightest 10 <{smart_est.max_spread}m", (5, 55),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.30, (100, 100, 100), 1)
        panels.append(p4)

    # ════════════════════════════════════════════════════════════
    # PLOT 5: 4m Bullseye — central detections (<200px from center)
    # ════════════════════════════════════════════════════════════
    if has_smart:
        p5 = make_panel()
        central = [(em, nm, pdist, alt, conf) for em, nm, pdist, alt, conf in pts_m if pdist < 200]
        central_10 = central[:10]
        n_central = len(central_10)

        cv2.putText(p5, f"CENTRAL ({n_central}/10, <200px)", (5, 15),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.35, (200, 200, 200), 1)

        if central_10:
            c5_scale, c5_usable, c5_cx, c5_cy = auto_scale(
                [(p[0], p[1]) for p in central_10])
            draw_rings(p5, c5_cx, c5_cy, [1, 2, 3, 5, 10], c5_scale, c5_usable)
            cv2.drawMarker(p5, (c5_cx, c5_cy), (0, 255, 0), cv2.MARKER_CROSS, 12, 2)

            c5_max_pd = max(p[2] for p in central_10) if central_10 else 1
            for em, nm, pdist, alt, conf in central_10:
                px = c5_cx + int(em * c5_scale)
                py = c5_cy - int(nm * c5_scale)
                if MARGIN < px < S - MARGIN and MARGIN < py < S - MARGIN:
                    val = min(1.0, pdist / max(c5_max_pd, 1))
                    cv2.circle(p5, (px, py), 3, heat_color(val), -1)

            c5_dists = [math.sqrt(p[0]**2 + p[1]**2) for p in central_10]
            c5_cep = sorted(c5_dists)[len(c5_dists) // 2] if c5_dists else 0
            cv2.putText(p5, f"CEP50: {c5_cep:.1f}m", (5, S - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.32, (180, 180, 180), 1)
        else:
            cv2.putText(p5, "No central detections yet", (20, S // 2),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.35, (100, 100, 100), 1)
        panels.append(p5)

    # ── Assemble all panels with separators ──
    separator = np.full((S, SEP, 3), (60, 60, 60), dtype=np.uint8)
    strips = []
    for i, panel in enumerate(panels):
        if i > 0:
            strips.append(separator)
        strips.append(panel)
    plot = np.hstack(strips)

    _, jpg = cv2.imencode('.jpg', plot, [cv2.IMWRITE_JPEG_QUALITY, 80])
    with frame_lock:
        latest_bullseye = jpg.tobytes()


# ── GPS state (read-only from mavproxy) ──
gps_data = {
    "lat": 0.0, "lon": 0.0, "alt": 0.0, "sats": 0, "fix": 0,
    "yaw": 0.0, "pitch": 0.0, "roll": 0.0, "mode": "---"
}

COPTER_MODES = {
    0: "STABILIZE", 2: "ALT_HOLD", 3: "AUTO", 4: "GUIDED",
    5: "LOITER", 6: "RTL", 9: "LAND", 16: "POSHOLD",
}


def mavlink_reader(mav):
    """Background thread: read telemetry from mavproxy. Zero commands sent."""
    while True:
        try:
            msg = mav.recv_match(blocking=True, timeout=1)
            if msg is None:
                continue
            mtype = msg.get_type()

            if mtype == 'GLOBAL_POSITION_INT':
                with gps_lock:
                    gps_data["lat"] = msg.lat / 1e7
                    gps_data["lon"] = msg.lon / 1e7
                    gps_data["alt"] = msg.relative_alt / 1000.0

            elif mtype == 'GPS_RAW_INT':
                with gps_lock:
                    gps_data["sats"] = msg.satellites_visible
                    gps_data["fix"] = msg.fix_type

            elif mtype == 'HEARTBEAT':
                if msg.type != 6:  # skip GCS heartbeats (mavproxy)
                    with gps_lock:
                        gps_data["mode"] = COPTER_MODES.get(msg.custom_mode, f"MODE_{msg.custom_mode}")

            elif mtype == 'ATTITUDE':
                with gps_lock:
                    gps_data["yaw"] = msg.yaw * 57.2958  # rad to deg
                    gps_data["pitch"] = msg.pitch * 57.2958
                    gps_data["roll"] = msg.roll * 57.2958

        except Exception:
            time.sleep(0.1)


def draw_overlay(frame, last_det):
    """Draw detection box + GPS info on frame for stream."""
    h, w = frame.shape[:2]
    display = frame.copy()

    # GPS snapshot (needed early for altitude-dependent overlays)
    with gps_lock:
        g = dict(gps_data)

    # Draw last detection box (persists between frames)
    # Persistent detection box — redraw on EVERY frame (vision.py only draws on inference frames)
    if last_det is not None:
        det_cx, det_cy, conf, age = last_det
        if age < 2.0:
            alpha = max(0.3, 1.0 - age / 2.0)
            color = (0, int(255 * alpha), 0)
            bw = getattr(draw_overlay, '_last_bw', 80)
            bh = getattr(draw_overlay, '_last_bh', 80)
            x1 = max(0, det_cx - bw // 2)
            y1 = max(0, det_cy - bh // 2)
            x2 = min(w, det_cx + bw // 2)
            y2 = min(h, det_cy + bh // 2)
            cv2.rectangle(display, (x1, y1), (x2, y2), color, 3)
            cls_name = getattr(draw_overlay, '_last_class', '')
            label = f"AI {conf:.2f} [{cls_name}]"
            cv2.putText(display, label, (x1, y1 - 8),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    # Centre crosshair (helps pilot align directly over target)
    cx, cy = w // 2, h // 2
    cross_color = (100, 100, 100)  # subtle grey
    cross_len = 15
    cv2.line(display, (cx - cross_len, cy), (cx + cross_len, cy), cross_color, 1)
    cv2.line(display, (cx, cy - cross_len), (cx, cy + cross_len), cross_color, 1)

    # ── Pink line: center → detection (like video_test_compare.py) ──
    if last_det is not None:
        det_cx, det_cy, conf, age = last_det
        if age < 2.0:
            dcx_i, dcy_i = int(det_cx), int(det_cy)
            # Pink/magenta line from frame center to detection center
            cv2.line(display, (cx, cy), (dcx_i, dcy_i), (255, 0, 255), 2)
            # Pixel distance
            px_dist = math.sqrt((dcx_i - cx)**2 + (dcy_i - cy)**2)
            mid_x = (cx + dcx_i) // 2
            mid_y = (cy + dcy_i) // 2
            cv2.putText(display, f"{px_dist:.0f}px", (mid_x + 8, mid_y - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 0, 255), 1)
            # Estimated real distance in meters (using FOV + altitude)
            alt_now = g["alt"] if g["alt"] > 0.5 else 0
            if alt_now > 0.5:
                fov_h_rad = math.radians(FOV["hfov_deg"])
                ground_w_now = 2 * alt_now * math.tan(fov_h_rad / 2)
                px_per_m = w / ground_w_now
                dist_m = px_dist / px_per_m
                cv2.putText(display, f"{dist_m:.1f}m", (mid_x + 8, mid_y + 12),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1)

    # GPS overlay (bottom of frame)
    lat, lon = g["lat"], g["lon"]
    alt = g["alt"]
    sats = g["sats"]
    mode = g["mode"]

    if lat != 0.0 or lon != 0.0:
        gps_text = f"GPS: {lat:.6f}, {lon:.6f} | Alt: {alt:.1f}m | Sats: {sats}"
    else:
        gps_text = f"GPS: No Fix | Sats: {sats}"

    # Black background bar for text
    cv2.rectangle(display, (0, h - 25), (w, h), (0, 0, 0), -1)
    cv2.putText(display, gps_text, (5, h - 8),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 170, 255), 1)

    # Top bar: FPS + mode + attitude
    cv2.rectangle(display, (0, 0), (w, 30), (0, 0, 0), -1)
    cam_f = cam_fps_tracker.fps()
    vis_f = vis_fps_tracker.fps()
    str_f = stream_fps_tracker.fps()
    fps_text = f"CAM:{cam_f:.1f}  VIS:{vis_f:.1f}  STR:{str_f:.1f}"
    cv2.putText(display, fps_text, (5, 18),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)

    yaw_deg = g["yaw"]
    pitch_deg = g["pitch"]
    roll_deg = g["roll"]
    att_text = f"Y:{yaw_deg:.0f} P:{pitch_deg:.1f} R:{roll_deg:.1f}"
    cv2.putText(display, att_text, (w - 220, 18),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (180, 180, 180), 1)
    cv2.putText(display, mode, (w - 80, 18),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)

    # Compass rose (top-right corner)
    compass_cx = w - 45
    compass_cy = 65
    compass_r = 25
    cv2.circle(display, (compass_cx, compass_cy), compass_r, (80, 80, 80), 1)

    # N/S/E/W labels
    cv2.putText(display, "N", (compass_cx - 4, compass_cy - compass_r - 3),
                cv2.FONT_HERSHEY_SIMPLEX, 0.3, (200, 200, 200), 1)

    # Drone heading arrow (yaw = 0 means North, positive = clockwise)
    yaw_rad = math.radians(yaw_deg)
    arrow_x = int(compass_cx + compass_r * 0.8 * math.sin(yaw_rad))
    arrow_y = int(compass_cy - compass_r * 0.8 * math.cos(yaw_rad))
    cv2.arrowedLine(display, (compass_cx, compass_cy), (arrow_x, arrow_y),
                    (0, 255, 0), 2, tipLength=0.4)

    # "FRONT" label on the frame edge matching drone forward
    cv2.putText(display, "FRONT", (w // 2 - 25, 48),
                cv2.FONT_HERSHEY_SIMPLEX, 0.35, (100, 100, 100), 1)

    # ── FOV / calibration info bar (second from bottom) ──
    alt_val = g["alt"]
    gw, gh = ground_coverage(alt_val) if alt_val > 0.5 else (0, 0)
    cal_w, cal_h = ground_coverage(1.0)  # at 1m for calibration reference

    fov_y = h - 50  # above the GPS bar
    cv2.rectangle(display, (0, fov_y), (w, fov_y + 25), (0, 0, 0), -1)

    if alt_val > 0.5:
        fov_text = (f"FOV:{FOV['hfov_deg']:.0f}deg | "
                    f"Ground:{gw:.1f}x{gh:.1f}m @{alt_val:.0f}m | "
                    f"Cal@1m:{cal_w*100:.0f}x{cal_h*100:.0f}cm")
        # Draw ground coverage dimensions on frame edges (subtle, not overlapping UI)
        dim_color = (140, 110, 0)  # muted amber
        # Width: short arrows + label at bottom-left area (above info bars)
        w_label = f"<-- {gw:.1f}m -->"
        cv2.putText(display, w_label, (w // 2 - 50, h - 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, dim_color, 1)
        # Height: label rotated on left edge
        h_label = f"{gh:.1f}m"
        cv2.putText(display, h_label, (w - 45, h // 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, dim_color, 1)
    else:
        fov_text = (f"FOV:{FOV['hfov_deg']:.0f}deg  f={FOV['focal_mm']}mm  "
                    f"sens={FOV['sensor_w']}mm | Cal@1m:{cal_w*100:.0f}x{cal_h*100:.0f}cm")
    cv2.putText(display, fov_text, (5, fov_y + 16),
                cv2.FONT_HERSHEY_SIMPLEX, 0.35, (180, 140, 0), 1)

    # ── Scale bar: 1m reference at current altitude (like video_test_compare.py) ──
    alt_scale = g["alt"]
    if alt_scale > 0.5:
        fov_h_rad_s = math.radians(FOV["hfov_deg"])
        ground_w_s = 2 * alt_scale * math.tan(fov_h_rad_s / 2)
        scale_1m = int(w / ground_w_s)  # pixels per meter
        if scale_1m > 5:
            sx2 = w - 20
            sx1 = sx2 - scale_1m
            sy1 = h - 100  # above the info bars
            cv2.line(display, (sx1, sy1), (sx2, sy1), (255, 255, 255), 2)
            cv2.line(display, (sx1, sy1 - 5), (sx1, sy1 + 5), (255, 255, 255), 2)
            cv2.line(display, (sx2, sy1 - 5), (sx2, sy1 + 5), (255, 255, 255), 2)
            cv2.putText(display, f"1m ({alt_scale:.0f}m alt)", (sx1, sy1 - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1)

    # ── Pink dot on detection center ──
    if last_det is not None and last_det[3] < 1.0:  # (cx, cy, conf, age)
        det_cx = int(last_det[0])  # already pixel coords from line 609
        det_cy = int(last_det[1])
        cv2.circle(display, (det_cx, det_cy), 12, (255, 0, 255), -1)  # filled pink
        cv2.circle(display, (det_cx, det_cy), 12, (255, 255, 255), 2)  # white border

    # ── Estimated dummy position (if we have observations) ──
    est = dummy_estimator.get_estimate()
    est_y = h - 75  # above FOV bar
    cv2.rectangle(display, (0, est_y), (w, est_y + 25), (0, 0, 0), -1)

    if est is not None:
        e_lat, e_lon, n_obs = est
        est_text = f"DUMMY EST: {e_lat:.6f}, {e_lon:.6f} ({n_obs} obs)"
        est_color = (255, 0, 255)  # pink/magenta
    elif lat == 0.0 and lon == 0.0:
        est_text = "DUMMY EST: NO GPS — cannot estimate"
        est_color = (180, 0, 255)  # pink-red
    else:
        est_text = "DUMMY EST: waiting for detection..."
        est_color = (100, 100, 100)  # grey
    cv2.putText(display, est_text, (5, est_y + 16),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, est_color, 1)

    return display


# ── Main ──
def main():
    global latest_jpeg, latest_det_jpeg, smart_estimator, _all_gps_estimates

    if args.smart_estimate:
        smart_estimator = SmartEstimator(
            min_samples=args.smart_min,
            max_spread=args.smart_radius)
        print(f"[SMART] Enabled: {args.smart_min} central samples within {args.smart_radius}m")

    # Auto-detect IP
    pi_ip = "localhost"
    try:
        result = subprocess.run(['hostname', '-I'], capture_output=True, text=True, timeout=3)
        ip = result.stdout.strip().split()[0]
        if ip:
            pi_ip = ip
    except Exception:
        pass

    print("=" * 50)
    print("  SAR PASSIVE WATCH")
    print("  Camera + Detection + Stream + Snapshots")
    print("  ZERO commands sent. Safe to run anytime.")
    print("=" * 50)
    print(f"  Confidence: {args.conf}")
    print(f"  Max FPS:    {args.fps}")
    if not args.no_save:
        os.makedirs(args.save_dir, exist_ok=True)
        print(f"  Saving to:  {args.save_dir}/")
    else:
        print("  Saving:     OFF")
    print()
    print(f"  Dashboard:  http://{pi_ip}:{args.port}/")
    print(f"  Stream:     http://{pi_ip}:{args.port}/stream")
    print(f"  Snapshot:   http://{pi_ip}:{args.port}/snapshot")
    print()

    # Fake mode: replay video + SRT telemetry
    fake_cap = None
    fake_telem = None
    fake_frame_idx = [0]
    fake_fps = 30
    _fake_start = [time.time()]

    if args.fake:
        print(f"[FAKE] Loading video: {args.fake_video}")
        fake_cap = cv2.VideoCapture(args.fake_video)
        if not fake_cap.isOpened():
            print(f"[FAKE] ERROR: Cannot open {args.fake_video}")
            return
        fake_fps = fake_cap.get(cv2.CAP_PROP_FPS) or 30
        total = int(fake_cap.get(cv2.CAP_PROP_FRAME_COUNT))
        print(f"[FAKE] Video: {int(fake_cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(fake_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))} @ {fake_fps}fps, {total} frames")
        print(f"[FAKE] Loading SRT: {args.fake_srt}")
        fake_telem = parse_srt(args.fake_srt)
        print(f"[FAKE] SRT loaded: {len(fake_telem)} entries")
        print("[FAKE] Mavproxy disabled — using SRT telemetry")
    else:
        # Connect to mavproxy (read-only) for GPS
        mav = None
        if not args.no_mavlink:
            try:
                from pymavlink import mavutil
                print("[MAV] Connecting to udpin:0.0.0.0:14550 (read-only)...")
                mav = mavutil.mavlink_connection('udpin:0.0.0.0:14550')
                msg = mav.recv_match(type='HEARTBEAT', blocking=True, timeout=5)
                if msg:
                    print(f"[MAV] Connected! Reading telemetry (zero commands)")
                    t = threading.Thread(target=mavlink_reader, args=(mav,), daemon=True)
                    t.start()
                else:
                    print("[MAV] No heartbeat — running without GPS")
                    mav = None
            except Exception as e:
                print(f"[MAV] Could not connect: {e} — running without GPS")
                mav = None
        else:
            print("[MAV] Skipped (--no-mavlink)")

    # Start camera + AI
    if args.fake:
        eyes = VisionSystem(camera_index=None, model_path=args.model)
    else:
        eyes = VisionSystem(camera_index=0, model_path=args.model)
    if not eyes.using_ai:
        print("[WARN] AI model not loaded — stream only, no detection")

    # Set initial model ID from args.model path
    for m in MODEL_TABLE:
        if os.path.abspath(m["path"]) == os.path.abspath(args.model):
            runtime_state["active_model_id"] = m["id"]
            break
    print("[OK] Ready. Ctrl+C to stop.\n")

    # Start HTTP server
    if not args.no_stream:
        server = ThreadedServer(('0.0.0.0', args.port), Handler)
        server_thread = threading.Thread(target=server.serve_forever, daemon=True)
        server_thread.start()
        print(f"[OK] Stream serving on port {args.port}\n")
    else:
        print("[OK] Stream server disabled (--no-stream)\n")

    # Render initial empty bullseye
    render_bullseye([], smart_estimator)

    # CSV log for detections
    csv_path = os.path.join(args.save_dir, "detection_log.csv") if (not args.no_save and not args.simple_names) else None
    csv_file = None
    csv_writer = None
    if csv_path:
        write_header = not os.path.exists(csv_path) or os.path.getsize(csv_path) == 0
        csv_file = open(csv_path, 'a', newline='')
        csv_writer = csv.writer(csv_file)
        if write_header:
            csv_writer.writerow(['timestamp', 'frame', 'confidence', 'px_x', 'px_y',
                                 'drone_lat', 'drone_lon', 'alt_m', 'sats', 'yaw', 'mode',
                                 'est_dummy_lat', 'est_dummy_lon', 'est_n_obs', 'filename'])

    # Camera loop
    frame_count = 0
    det_count = 0
    saved_count = 0
    start_time = time.time()
    last_inference = 0
    min_interval = 1.0 / args.fps if args.fps > 0 else 0

    # Persistent detection state (for overlay)
    last_det = None  # (cx, cy, conf, time_since_det)
    last_det_time = 0

    while True:
        if args.fake:
            # Skip frames to maintain real-time playback
            # Read multiple frames to keep pace (inference slows us down)
            target_frame = int((time.time() - _fake_start[0]) * fake_fps) + 1
            while fake_frame_idx[0] < target_frame:
                ret, frame = fake_cap.read()
                if not ret:
                    fake_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    fake_frame_idx[0] = 0
                    _fake_start[0] = time.time()
                    break
                fake_frame_idx[0] += 1
            # Update GPS from SRT telemetry
            t = fake_telem.get(fake_frame_idx[0])
            if t:
                with gps_lock:
                    gps_data["lat"] = t["lat"]
                    gps_data["lon"] = t["lon"]
                    gps_data["alt"] = t["alt"]
                    gps_data["yaw"] = t["yaw"]
                    gps_data["sats"] = 12
                    gps_data["mode"] = "FAKE"
            if fake_frame_idx[0] % 100 == 1:
                with gps_lock:
                    print(f"  [FAKE] Frame {fake_frame_idx[0]} GPS:{gps_data['lat']:.5f},{gps_data['lon']:.5f} Alt:{gps_data['alt']:.0f}m Yaw:{gps_data['yaw']:.0f}")
        else:
            frame = eyes.get_frame()
            if frame is None:
                time.sleep(0.01)
                continue

        frame_count += 1
        now = time.time()
        if frame is None:
            continue
        h, w = frame.shape[:2]
        cam_fps_tracker.tick()

        # ── Handle model switch request from browser ──
        with runtime_lock:
            switch_req = runtime_state["model_switch_request"]
        if switch_req is not None:
            m = MODEL_TABLE[switch_req]
            print(f"[MODEL] Switching to {m['name']} ({m['path']}, backend={m['backend']})")
            try:
                new_eyes = VisionSystem(
                    camera_index=None if args.fake else 0,
                    model_path=m['path'],
                    backend=m['backend']
                )
                eyes = new_eyes
                print(f"[MODEL] Loaded: {m['name']} (backend={eyes.backend_name})")
                with runtime_lock:
                    runtime_state["active_model_id"] = switch_req
                    runtime_state["class_filter"] = "all"  # reset filter on model switch
                    runtime_state["model_switch_request"] = None
            except Exception as e:
                print(f"[MODEL] ERROR loading {m['name']}: {e}")
                with runtime_lock:
                    runtime_state["model_switch_request"] = None  # clear request, keep old model

        # Read runtime conf + class filter
        with runtime_lock:
            current_conf = runtime_state["conf_threshold"]
            current_class_filter = runtime_state["class_filter"]

        # Run detection (throttled)
        if eyes.using_ai and (now - last_inference) >= min_interval:
            last_inference = now
            found, x, y, conf = eyes.detect_in_image(frame)
            vis_fps_tracker.tick()

            # (detection logging removed — enable for debug)

            if found and conf >= current_conf:
                # Class filter: skip if detection class doesn't match
                if current_class_filter and current_class_filter != "all" and hasattr(eyes, 'last_class_name'):
                    if eyes.last_class_name.lower() != current_class_filter.lower():
                        continue  # skip this detection

                det_count += 1
                cx, cy = int(x), int(y)
                last_det = (cx, cy, conf, 0.0)
                last_det_time = now
                # Store bbox size + class for persistent overlay
                draw_overlay._last_bw = eyes.last_bbox_w if eyes.last_bbox_w > 0 else 80
                draw_overlay._last_bh = eyes.last_bbox_h if eyes.last_bbox_h > 0 else 80
                draw_overlay._last_class = getattr(eyes, 'last_class_name', '')

                # Estimate dummy GPS position — snapshot all telemetry under lock
                est_result = None
                with gps_lock:
                    d_lat, d_lon = gps_data["lat"], gps_data["lon"]
                    d_alt = gps_data["alt"]
                    d_yaw = gps_data["yaw"]
                    d_pitch = gps_data["pitch"]
                    d_roll = gps_data["roll"]
                    d_sats = gps_data["sats"]
                    d_mode = gps_data["mode"]
                if d_lat != 0.0 or d_lon != 0.0:
                    # Normalise pixel coords to 0-1 (estimator expects normalised)
                    norm_x = x / w if w > 0 else 0.5
                    norm_y = y / h if h > 0 else 0.5
                    est_result = dummy_estimator.add_observation(
                        d_lat, d_lon, d_alt, d_yaw, norm_x, norm_y
                    )

                    # Store for bullseye plotting
                    if est_result:
                        est_lat, est_lon = est_result
                        pixel_dist = math.sqrt((cx - w/2)**2 + (cy - h/2)**2)
                        _all_gps_estimates.append((est_lat, est_lon, pixel_dist, d_alt, conf))

                        # Smart estimate: greedy cluster finds tightest 10
                        if smart_estimator:
                            smart_estimator.add(est_lat, est_lon, pixel_dist, frame)

                        # Update bullseye plot
                        render_bullseye(_all_gps_estimates, smart_estimator)

                # Smart estimate: save ONLY when threshold reached, use median + most central image
                if args.smart_estimate and smart_estimator and not args.no_save:
                    if smart_estimator.ready() and not getattr(smart_estimator, '_saved', False):
                        smart_estimator._saved = True
                        med = smart_estimator.get_median()
                        saved_count += 1
                        fname = f"SMART_{med[0]:.6f}_{med[1]:.6f}_{med[2]}samp.png"
                        # Save most central frame from cluster (clean, no overlay)
                        if smart_estimator.locked_frame is not None:
                            cv2.imwrite(os.path.join(args.save_dir, fname), smart_estimator.locked_frame)
                        print(f"\n  {'='*60}")
                        print(f"  SMART ESTIMATE SAVED: {fname}")
                        print(f"  Median GPS: {med[0]:.7f}, {med[1]:.7f}")
                        print(f"  Cluster: {med[2]} samples, spread: {smart_estimator.locked_spread:.2f}m")
                        print(f"  {'='*60}\n")
                    # Skip normal save when in smart mode
                    if args.smart_estimate:
                        pass  # don't save individual frames
                elif not args.no_save:
                    pass  # fall through to normal save below

                # Save snapshot with GPS overlay (normal mode, skipped in smart mode)
                if not args.no_save and not args.smart_estimate:
                    saved_count += 1
                    save_frame = draw_overlay(frame, last_det)
                    sh, sw = save_frame.shape[:2]

                    # Add GPS text on saved image (larger, more prominent)
                    with gps_lock:
                        lat, lon = gps_data["lat"], gps_data["lon"]
                        alt = gps_data["alt"]
                    ts = datetime.now().strftime("%H:%M:%S")

                    if args.simple_names:
                        # Use estimated dummy GPS (not drone GPS) in filename
                        est_snap = dummy_estimator.get_estimate()
                        if est_snap:
                            fname = f"{saved_count:04d}_{est_snap[0]:.5f}_{est_snap[1]:.5f}.jpg"
                        elif lat != 0.0 or lon != 0.0:
                            fname = f"{saved_count:04d}_{lat:.5f}_{lon:.5f}.jpg"
                        else:
                            fname = f"{saved_count:04d}_nogps.jpg"
                    else:
                        if lat != 0.0 or lon != 0.0:
                            fname = f"det_{saved_count:04d}_{conf:.2f}_{lat:.5f}_{lon:.5f}.jpg"
                        else:
                            fname = f"det_{saved_count:04d}_{conf:.2f}_nogps.jpg"

                    # Stamp: time + conf + drone pos + dummy est (right side, stacked)
                    stamp_lines = [f"{ts} conf:{conf:.2f}"]
                    if lat != 0.0 or lon != 0.0:
                        stamp_lines.append(f"DRONE: {lat:.6f},{lon:.6f} @{alt:.0f}m")
                    else:
                        stamp_lines.append("DRONE: NO GPS")
                    est_snap = dummy_estimator.get_estimate()
                    if est_snap:
                        stamp_lines.append(f"DUMMY: {est_snap[0]:.6f},{est_snap[1]:.6f} ({est_snap[2]}obs)")
                    # Draw with black background for readability
                    for i, line in enumerate(stamp_lines):
                        ty = sh // 3 + i * 20
                        cv2.rectangle(save_frame, (sw - 280, ty - 14), (sw, ty + 4), (0, 0, 0), -1)
                        cv2.putText(save_frame, line, (sw - 275, ty),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

                    cv2.imwrite(os.path.join(args.save_dir, fname), save_frame)

                    # JSON sidecar metadata (skip if --simple-names)
                    if not args.simple_names:
                        g_w, g_h = ground_coverage(d_alt) if d_alt > 0.5 else (0, 0)
                        meta = {
                            "timestamp": datetime.now().isoformat(),
                            "frame": frame_count,
                            "detection": {
                                "confidence": round(conf, 3),
                                "pixel_x": cx, "pixel_y": cy,
                                "bbox_centre": [cx, cy],
                            },
                            "drone": {
                                "lat": round(d_lat, 7), "lon": round(d_lon, 7),
                                "alt_m": round(d_alt, 1),
                                "yaw_deg": round(d_yaw, 1),
                                "pitch_deg": round(d_pitch, 1),
                                "roll_deg": round(d_roll, 1),
                                "sats": d_sats,
                                "mode": d_mode,
                            },
                            "fov": {
                                "focal_mm": FOV["focal_mm"],
                                "sensor_w_mm": FOV["sensor_w"],
                                "hfov_deg": round(FOV["hfov_deg"], 1),
                                "ground_w_m": round(g_w, 2) if d_alt > 0.5 else None,
                                "ground_h_m": round(g_h, 2) if d_alt > 0.5 else None,
                            },
                            "estimate": {
                                "lat": round(est_snap[0], 7) if est_snap else None,
                                "lon": round(est_snap[1], 7) if est_snap else None,
                                "n_observations": est_snap[2] if est_snap else 0,
                            },
                            "image": fname,
                        }
                        json_fname = fname.replace('.jpg', '.json')
                        with open(os.path.join(args.save_dir, json_fname), 'w') as jf:
                            json.dump(meta, jf, indent=2)

                    # CSV log
                    if csv_writer:
                        est = dummy_estimator.get_estimate()
                        csv_writer.writerow([
                            datetime.now().isoformat(), frame_count, f"{conf:.3f}",
                            cx, cy, f"{d_lat:.7f}", f"{d_lon:.7f}", f"{d_alt:.1f}",
                            d_sats, f"{d_yaw:.0f}",
                            d_mode,
                            f"{est[0]:.7f}" if est else "",
                            f"{est[1]:.7f}" if est else "",
                            est[2] if est else 0,
                            fname
                        ])
                        csv_file.flush()

        # Update detection age for fading overlay
        if last_det is not None:
            age = now - last_det_time
            last_det = (last_det[0], last_det[1], last_det[2], age)

        # Update all plots every 2 seconds
        if frame_count % max(1, int(fake_fps * 2 if args.fake else 10)) == 0:
            render_bullseye(_all_gps_estimates, smart_estimator)
            render_map(_all_gps_estimates, smart_estimator)
            if smart_estimator:
                render_smart_grid(smart_estimator)
            if last_det is not None:
                render_latest_detection(frame, last_det, gps_data)

        # Draw overlay (detection box + GPS) on every frame for stream
        display = draw_overlay(frame, last_det)

        # Encode for stream
        _, jpg = cv2.imencode('.jpg', display, [cv2.IMWRITE_JPEG_QUALITY, 70])
        with frame_lock:
            latest_jpeg = jpg.tobytes()
        stream_fps_tracker.tick()

        # Update stats (gps_lock for telemetry reads, frame_lock for stats dict)
        det_pct = (det_count / frame_count * 100) if frame_count > 0 else 0
        with gps_lock:
            lat, lon = gps_data["lat"], gps_data["lon"]
            g_alt = gps_data["alt"]
            g_sats = gps_data["sats"]
            g_mode = gps_data["mode"]
        c_fps = cam_fps_tracker.fps()
        v_fps = vis_fps_tracker.fps()
        s_fps = stream_fps_tracker.fps()
        est = dummy_estimator.get_estimate()
        with frame_lock:
            stats.update({
                "frames": frame_count,
                "detections": det_count,
                "det_pct": f"{det_pct:.0f}",
                "cam_fps": f"{c_fps:.1f}",
                "vis_fps": f"{v_fps:.1f}",
                "stream_fps": f"{s_fps:.1f}",
                "saved": saved_count,
                "gps_lat": f"{lat:.6f}" if lat != 0 else "---",
                "gps_lon": f"{lon:.6f}" if lon != 0 else "---",
                "alt": f"{g_alt:.1f}" if g_alt != 0 else "---",
                "sats": g_sats,
                "flight_mode": g_mode,
                "est_lat": f"{est[0]:.6f}" if est else "---",
                "est_lon": f"{est[1]:.6f}" if est else "---",
                "est_obs": est[2] if est else 0,
            })

        # Terminal output every 50 frames
        if frame_count % 50 == 0:
            gps_str = f"GPS:{lat:.5f},{lon:.5f}" if lat != 0 else "GPS:---"
            print(f"  #{frame_count} CAM:{c_fps:.1f} VIS:{v_fps:.1f} STR:{s_fps:.1f} Det:{det_count} ({det_pct:.0f}%) Saved:{saved_count} {gps_str}")

    if csv_file:
        csv_file.close()
    eyes.release()
    server.shutdown()


if __name__ == "__main__":
    main()
