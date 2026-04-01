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
latest_bullseye = None  # rendered bullseye plot JPEG
frame_lock = threading.Lock()
_all_gps_estimates = []  # (est_lat, est_lon, pixel_dist) for bullseye plotting

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
args = parser.parse_args()


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
  body { background:#111; color:#eee; font-family:monospace; margin:0; padding:20px; }
  h1 { color:#0f0; margin:0 0 10px; }
  .stats { color:#888; margin-bottom:10px; }
  .gps { color:#0af; margin-bottom:5px; }
  .est { color:#ff00ff; margin-bottom:5px; font-weight:bold; }
  .fov { color:#b90; margin-bottom:10px; font-size:0.85em; }
  img { max-width:100%; border:1px solid #333; }
</style>
</head><body>
<h1>SAR Passive Watch</h1>
<div class="stats" id="stats">Starting...</div>
<div class="gps" id="gps">GPS: waiting...</div>
<div class="est" id="est">DUMMY EST: waiting...</div>
<div class="fov" id="fov">FOV: ---</div>
<img src="/stream" alt="Camera Feed">
<h2 style="color:#0ff; margin-top:15px;">GPS Estimate Plots</h2>
<img id="bullseye" src="/bullseye" alt="Bullseye Plot" style="max-width:100%; border:1px solid #333;">
<script>
  setInterval(()=>{
    fetch('/api/status').then(r=>r.json()).then(d=>{
      document.getElementById('stats').textContent =
        `CAM: ${d.cam_fps} fps | VISION: ${d.vis_fps} fps | STREAM: ${d.stream_fps} fps | Det: ${d.detections} (${d.det_pct}%) | Saved: ${d.saved}`;
      document.getElementById('gps').textContent =
        `DRONE: ${d.gps_lat}, ${d.gps_lon} | Alt: ${d.alt}m | Sats: ${d.sats} | Mode: ${d.flight_mode}`;
      document.getElementById('est').textContent = d.est_obs > 0
        ? `DUMMY EST: ${d.est_lat}, ${d.est_lon} (${d.est_obs} observations)`
        : `DUMMY EST: waiting for detection...`;
      document.getElementById('fov').textContent =
        `FOV: ${d.fov_deg}° | Cal@1m: ${d.cal_1m_w}x${d.cal_1m_h}cm (measure this to calibrate)`;
      document.getElementById('bullseye').src = '/bullseye?' + Date.now();
    });
  }, 2000);
</script>
</body></html>"""


# ── HTTP Server ──
class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *a):
        pass  # silent

    def do_GET(self):
        path = self.path.split('?')[0]  # strip query string for matching
        if path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode())

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
                    time.sleep(0.05)
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

        elif path == '/api/status':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            import json
            self.wfile.write(json.dumps(stats).encode())

        else:
            self.send_response(404)
            self.end_headers()


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
        self.observations = []  # (lat, lon, weight)
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
        lat_m_per_deg = 111132.954 - 559.822 * math.cos(2 * math.radians(drone_lat))
        lon_m_per_deg = 111132.954 * math.cos(math.radians(drone_lat))

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
        self.observations = []
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
        dists = {}
        for i in range(n):
            for j in range(i + 1, n):
                dn = (estimates[i][0] - estimates[j][0]) * 111320
                de = (estimates[i][1] - estimates[j][1]) * 111320 * math.cos(math.radians(estimates[i][0]))
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
        for lat, lon, _ in self.estimates:
            dn = (lat - m_lat) * 111320
            de = (lon - m_lon) * 111320 * math.cos(math.radians(m_lat))
            dists.append(math.sqrt(dn**2 + de**2))
        dists.sort()
        return dists[len(dists) // 2] if dists else 0

smart_estimator = None  # initialized in main() if --smart-estimate


def render_bullseye(all_estimates, smart_est=None):
    """Render bullseye plot showing all GPS estimates + smart cluster."""
    global latest_bullseye
    size = 400
    plot = np.zeros((size, size * 2, 3), dtype=np.uint8)  # two plots side by side

    if not all_estimates:
        cv2.putText(plot, "Waiting for detections...", (50, size // 2),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 100), 1)
        _, jpg = cv2.imencode('.jpg', plot, [cv2.IMWRITE_JPEG_QUALITY, 80])
        with frame_lock:
            latest_bullseye = jpg.tobytes()
        return

    # LEFT PLOT: all estimates centered on mean
    lats = [e[0] for e in all_estimates]
    lons = [e[1] for e in all_estimates]
    mean_lat = sum(lats) / len(lats)
    mean_lon = sum(lons) / len(lons)

    pts_m = []
    for lat, lon, pdist in all_estimates:
        n = (lat - mean_lat) * 111320
        e = (lon - mean_lon) * 111320 * math.cos(math.radians(mean_lat))
        pts_m.append((e, n, pdist))

    dists = [math.sqrt(p[0]**2 + p[1]**2) for p in pts_m]
    p95 = sorted(dists)[int(len(dists) * 0.95)] if dists else 5.0
    max_range = max(p95 * 2, 3.0)
    margin = 40
    usable = size - 2 * margin
    scale = usable / max_range
    cx, cy = size // 2, size // 2

    # Title
    cv2.putText(plot, f"ALL DETECTIONS (N={len(all_estimates)})", (10, 20),
               cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)

    # Rings
    for r_m in [1, 2, 3, 5, 10, 20]:
        r_px = int(r_m * scale)
        if 5 < r_px < usable // 2:
            cv2.circle(plot, (cx, cy), r_px, (40, 40, 40), 1)
            cv2.putText(plot, f"{r_m}m", (cx + r_px + 2, cy - 2),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.25, (60, 60, 60), 1)

    # Cross at mean
    cv2.drawMarker(plot, (cx, cy), (0, 255, 0), cv2.MARKER_CROSS, 15, 2)

    # Dots colored by pixel centrality
    max_pd = max(e[2] for e in all_estimates) if all_estimates else 1
    for e_m, n_m, pdist in pts_m:
        px = cx + int(e_m * scale)
        py = cy - int(n_m * scale)
        if margin < px < size - margin and margin < py < size - margin:
            val = min(1.0, pdist / max(max_pd, 1))
            g = int(255 * (1 - val))
            r = int(255 * val)
            cv2.circle(plot, (px, py), 3, (0, g, r), -1)

    # Weighted + median estimate
    est = dummy_estimator.get_estimate()
    if est:
        cv2.putText(plot, f"Est: {est[0]:.6f}, {est[1]:.6f} ({est[2]}obs)",
                   (10, size - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 0, 255), 1)

    # RIGHT PLOT: smart cluster (if active)
    ox = size  # offset for right plot
    if smart_est and smart_est.locked:
        cluster = smart_est.locked_cluster
        cv2.putText(plot, f"SMART LOCKED (spread: {smart_est.locked_spread:.2f}m)",
                   (ox + 10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.40, (0, 255, 0), 2)

        c_pts = []
        c_lats = [e[0] for e in cluster]
        c_lons = [e[1] for e in cluster]
        c_mean_lat = sum(c_lats) / len(c_lats)
        c_mean_lon = sum(c_lons) / len(c_lons)
        for lat, lon, pdist in cluster:
            n = (lat - c_mean_lat) * 111320
            e = (lon - c_mean_lon) * 111320 * math.cos(math.radians(c_mean_lat))
            c_pts.append((e, n, pdist))

        c_dists = [math.sqrt(p[0]**2 + p[1]**2) for p in c_pts]
        c_max = max(c_dists) * 1.5 if c_dists else 1.0
        c_max = max(c_max, 0.5)
        c_scale = usable / (2 * c_max)
        c_cx = ox + size // 2
        c_cy = size // 2

        # Rings
        for r_m in [0.1, 0.2, 0.5, 1.0]:
            r_px = int(r_m * c_scale)
            if 5 < r_px < usable // 2:
                cv2.circle(plot, (c_cx, c_cy), r_px, (40, 40, 40), 1)
                cv2.putText(plot, f"{r_m}m", (c_cx + r_px + 2, c_cy - 2),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.25, (60, 60, 60), 1)

        # Cross at median
        cv2.drawMarker(plot, (c_cx, c_cy), (0, 255, 255), cv2.MARKER_CROSS, 20, 2)

        # Dots
        for i, (e_m, n_m, pdist) in enumerate(c_pts):
            px = c_cx + int(e_m * c_scale)
            py = c_cy - int(n_m * c_scale)
            cv2.circle(plot, (px, py), 5, (0, 255, 255), -1)
            cv2.circle(plot, (px, py), 5, (255, 255, 255), 1)

        med = smart_est.get_median()
        if med:
            cv2.putText(plot, f"Median: {med[0]:.7f}, {med[1]:.7f}",
                       (ox + 10, size - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 0, 255), 1)
            cv2.putText(plot, f"Samples: {med[2]} | Spread: {smart_est.locked_spread:.2f}m",
                       (ox + 10, size - 12), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (200, 200, 200), 1)
    elif smart_est:
        n_est = len(smart_est.all_estimates)
        cv2.putText(plot, f"SMART: searching... ({n_est} detections)",
                   (ox + 10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.40, (255, 0, 255), 1)
        cv2.putText(plot, f"Need tightest 10 within {smart_est.max_spread}m",
                   (ox + 10, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (150, 150, 150), 1)
    else:
        cv2.putText(plot, "SMART: disabled (use --smart-estimate)",
                   (ox + 10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (100, 100, 100), 1)

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
                gps_data["lat"] = msg.lat / 1e7
                gps_data["lon"] = msg.lon / 1e7
                gps_data["alt"] = msg.relative_alt / 1000.0

            elif mtype == 'GPS_RAW_INT':
                gps_data["sats"] = msg.satellites_visible
                gps_data["fix"] = msg.fix_type

            elif mtype == 'HEARTBEAT':
                if msg.type != 6:  # skip GCS heartbeats (mavproxy)
                    gps_data["mode"] = COPTER_MODES.get(msg.custom_mode, f"MODE_{msg.custom_mode}")

            elif mtype == 'ATTITUDE':
                gps_data["yaw"] = msg.yaw * 57.2958  # rad to deg
                gps_data["pitch"] = msg.pitch * 57.2958
                gps_data["roll"] = msg.roll * 57.2958

        except Exception:
            time.sleep(0.1)


def draw_overlay(frame, last_det):
    """Draw detection box + GPS info on frame for stream."""
    h, w = frame.shape[:2]
    display = frame.copy()

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

    # GPS overlay (bottom of frame)
    lat, lon = gps_data["lat"], gps_data["lon"]
    alt = gps_data["alt"]
    sats = gps_data["sats"]
    mode = gps_data["mode"]

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

    yaw_deg = gps_data["yaw"]
    pitch_deg = gps_data["pitch"]
    roll_deg = gps_data["roll"]
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
    alt_val = gps_data["alt"]
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
    global latest_jpeg, latest_det_jpeg, smart_estimator

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
    print("[OK] Ready. Ctrl+C to stop.\n")

    # Start HTTP server
    server = ThreadedServer(('0.0.0.0', args.port), Handler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    print(f"[OK] Stream serving on port {args.port}\n")

    # Render initial empty bullseye
    render_bullseye([], smart_estimator)

    # CSV log for detections
    csv_path = os.path.join(args.save_dir, "detection_log.csv") if (not args.no_save and not args.simple_names) else None
    csv_file = None
    csv_writer = None
    if csv_path:
        csv_file = open(csv_path, 'a', newline='')
        csv_writer = csv.writer(csv_file)
        if os.path.getsize(csv_path) == 0:
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
                gps_data["lat"] = t["lat"]
                gps_data["lon"] = t["lon"]
                gps_data["alt"] = t["alt"]
                gps_data["yaw"] = t["yaw"]
                gps_data["sats"] = 12
                gps_data["mode"] = "FAKE"
            if fake_frame_idx[0] % 100 == 1:
                print(f"  [FAKE] Frame {fake_frame_idx[0]} GPS:{gps_data['lat']:.5f},{gps_data['lon']:.5f} Alt:{gps_data['alt']:.0f}m Yaw:{gps_data['yaw']:.0f}")
        else:
            frame = eyes.get_frame()
            if frame is None:
                time.sleep(0.01)
                continue

        frame_count += 1
        now = time.time()
        h, w = frame.shape[:2]
        cam_fps_tracker.tick()

        # Run detection (throttled)
        if eyes.using_ai and (now - last_inference) >= min_interval:
            last_inference = now
            found, x, y, conf = eyes.detect_in_image(frame)
            vis_fps_tracker.tick()

            # (detection logging removed — enable for debug)

            if found and conf >= args.conf:
                # Class filter: skip if detection class doesn't match
                if args.class_filter and hasattr(eyes, 'last_class_name'):
                    if eyes.last_class_name.lower() != args.class_filter.lower():
                        continue  # skip this detection

                det_count += 1
                cx, cy = int(x), int(y)
                last_det = (cx, cy, conf, 0.0)
                last_det_time = now
                # Store bbox size + class for persistent overlay
                draw_overlay._last_bw = eyes.last_bbox_w if eyes.last_bbox_w > 0 else 80
                draw_overlay._last_bh = eyes.last_bbox_h if eyes.last_bbox_h > 0 else 80
                draw_overlay._last_class = getattr(eyes, 'last_class_name', '')

                # Estimate dummy GPS position
                est_result = None
                d_lat, d_lon = gps_data["lat"], gps_data["lon"]
                d_alt = gps_data["alt"]
                d_yaw = gps_data["yaw"]
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
                        _all_gps_estimates.append((est_lat, est_lon, pixel_dist))

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
                                "yaw_deg": round(gps_data["yaw"], 1),
                                "pitch_deg": round(gps_data["pitch"], 1),
                                "roll_deg": round(gps_data["roll"], 1),
                                "sats": gps_data["sats"],
                                "mode": gps_data["mode"],
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
                            gps_data["sats"], f"{gps_data['yaw']:.0f}",
                            gps_data["mode"],
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

        # Update bullseye every 2 seconds
        if frame_count % max(1, int(fake_fps * 2 if args.fake else 10)) == 0:
            render_bullseye(_all_gps_estimates, smart_estimator)

        # Draw overlay (detection box + GPS) on every frame for stream
        display = draw_overlay(frame, last_det)

        # Encode for stream
        _, jpg = cv2.imencode('.jpg', display, [cv2.IMWRITE_JPEG_QUALITY, 70])
        with frame_lock:
            latest_jpeg = jpg.tobytes()
        stream_fps_tracker.tick()

        # Update stats
        det_pct = (det_count / frame_count * 100) if frame_count > 0 else 0
        lat, lon = gps_data["lat"], gps_data["lon"]
        c_fps = cam_fps_tracker.fps()
        v_fps = vis_fps_tracker.fps()
        s_fps = stream_fps_tracker.fps()
        est = dummy_estimator.get_estimate()
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
            "alt": f"{gps_data['alt']:.1f}" if gps_data['alt'] != 0 else "---",
            "sats": gps_data["sats"],
            "flight_mode": gps_data["mode"],
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
