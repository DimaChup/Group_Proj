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
frame_lock = threading.Lock()

# ── Args ──
parser = argparse.ArgumentParser(description="Passive camera watch + stream + snapshots")
parser.add_argument('--port', type=int, default=8090)
parser.add_argument('--conf', type=float, default=0.4)
parser.add_argument('--fps', type=float, default=5)
parser.add_argument('--save-dir', default='detections')
parser.add_argument('--no-save', action='store_true')
parser.add_argument('--no-mavlink', action='store_true', help='Skip mavproxy connection (no GPS)')
args = parser.parse_args()


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
    });
  }, 1000);
</script>
</body></html>"""


# ── HTTP Server ──
class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *a):
        pass  # silent

    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode())

        elif self.path == '/stream':
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

        elif self.path == '/snapshot':
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

        elif self.path == '/api/status':
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
    if last_det is not None:
        cx, cy, conf, age = last_det
        if age < 2.0:  # show box for 2 seconds after last detection
            alpha = max(0.3, 1.0 - age / 2.0)  # fade out
            color = (0, int(255 * alpha), 0)
            box = 40
            cv2.rectangle(display, (cx - box, cy - box), (cx + box, cy + box), color, 2)
            cv2.putText(display, f"{conf:.2f}", (cx - box, cy - box - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

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
        det_cx = int(last_det[0] * w)
        det_cy = int(last_det[1] * h)
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
    global latest_jpeg, latest_det_jpeg

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
    eyes = VisionSystem(camera_index=0, model_path="best.tflite")
    if not eyes.using_ai:
        print("[WARN] AI model not loaded — stream only, no detection")
    print("[OK] Camera ready. Ctrl+C to stop.\n")

    # Start HTTP server
    server = ThreadedServer(('0.0.0.0', args.port), Handler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    print(f"[OK] Stream serving on port {args.port}\n")

    # CSV log for detections
    csv_path = os.path.join(args.save_dir, "detection_log.csv") if not args.no_save else None
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

            if found and conf >= args.conf:
                det_count += 1
                cx, cy = int(x * w), int(y * h)
                last_det = (cx, cy, conf, 0.0)
                last_det_time = now

                # Estimate dummy GPS position
                est_result = None
                d_lat, d_lon = gps_data["lat"], gps_data["lon"]
                d_alt = gps_data["alt"]
                d_yaw = gps_data["yaw"]
                if d_lat != 0.0 or d_lon != 0.0:
                    est_result = dummy_estimator.add_observation(
                        d_lat, d_lon, d_alt, d_yaw, x, y
                    )

                # Save snapshot with GPS overlay
                if not args.no_save:
                    saved_count += 1
                    save_frame = draw_overlay(frame, last_det)
                    sh, sw = save_frame.shape[:2]

                    # Add GPS text on saved image (larger, more prominent)
                    lat, lon = gps_data["lat"], gps_data["lon"]
                    alt = gps_data["alt"]
                    ts = datetime.now().strftime("%H:%M:%S")

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

                    # JSON sidecar metadata (same name, .json)
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
