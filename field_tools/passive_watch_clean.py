#!/usr/bin/env python3
"""
passive_watch_clean.py — Same as passive_watch.py but saves CLEAN images.

Differences from passive_watch.py:
  - Saved images have NO overlay, NO bounding box, NO text — pure raw camera frame
  - Filename format: {num}_{lat}_{lon}.png  (PNG for lossless quality)
  - JSON sidecar still saved with full metadata (detection, GPS, FOV, estimate)
  - Stream still has full overlay (only saved files are clean)

Use case: collecting clean labelled training data during flight.

Run on Pi via SSH:
    cd ~/dima/Group_Proj
    source pienv/bin/activate
    DISPLAY= python field_tools/passive_watch_clean.py

Options:
    --port 8092         HTTP port (default 8092, avoids conflict with passive_watch)
    --conf 0.4          Confidence threshold (default 0.4)
    --fps 5             Max inference FPS (default 5)
    --save-dir clean_detections   Where to save (default: clean_detections/)
    --no-save           Don't save, stream only
    --no-mavlink        Skip mavproxy connection
    --model best.tflite Path to model
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

signal.signal(signal.SIGINT, signal.SIG_DFL)

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
parser = argparse.ArgumentParser(description="Passive watch — clean image capture (no overlay on saved files)")
parser.add_argument('--port', type=int, default=8092)
parser.add_argument('--conf', type=float, default=0.4)
parser.add_argument('--fps', type=float, default=5)
parser.add_argument('--save-dir', default='clean_detections')
parser.add_argument('--no-save', action='store_true')
parser.add_argument('--no-mavlink', action='store_true')
parser.add_argument('--model', default='best.tflite')
args = parser.parse_args()


# ── HTML page ──
HTML_PAGE = """<!DOCTYPE html>
<html><head><title>SAR Clean Capture</title>
<style>
  body { background:#111; color:#eee; font-family:monospace; margin:0; padding:20px; }
  h1 { color:#0f0; margin:0 0 10px; }
  .stats { color:#888; margin-bottom:10px; }
  .gps { color:#0af; margin-bottom:5px; }
  .est { color:#ff00ff; margin-bottom:5px; font-weight:bold; }
  img { max-width:100%; border:1px solid #333; }
</style>
</head><body>
<h1>SAR Clean Capture</h1>
<div class="stats" id="stats">Starting...</div>
<div class="gps" id="gps">GPS: waiting...</div>
<div class="est" id="est">DUMMY EST: waiting...</div>
<img src="/stream" alt="Camera Feed">
<script>
  setInterval(()=>{
    fetch('/api/status').then(r=>r.json()).then(d=>{
      document.getElementById('stats').textContent =
        `CAM: ${d.cam_fps} fps | VISION: ${d.vis_fps} fps | Det: ${d.detections} (${d.det_pct}%) | Saved: ${d.saved} (clean PNG)`;
      document.getElementById('gps').textContent =
        `DRONE: ${d.gps_lat}, ${d.gps_lon} | Alt: ${d.alt}m | Sats: ${d.sats} | Mode: ${d.flight_mode}`;
      document.getElementById('est').textContent = d.est_obs > 0
        ? `DUMMY EST: ${d.est_lat}, ${d.est_lon} (${d.est_obs} observations)`
        : `DUMMY EST: waiting for detection...`;
    });
  }, 1000);
</script>
</body></html>"""


# ── HTTP Server (identical to passive_watch.py) ──
class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *a):
        pass

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
                        self.wfile.write(b'Content-Type: image/jpeg\r\n')
                        self.wfile.write(f'Content-Length: {len(jpeg)}\r\n\r\n'.encode())
                        self.wfile.write(jpeg)
                        self.wfile.write(b'\r\n')
                        self.wfile.flush()
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
            self.wfile.write(json.dumps(stats).encode())
        else:
            self.send_response(404)
            self.end_headers()


class ThreadedServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True


# ── Stats ──
stats = {
    "frames": 0, "detections": 0, "det_pct": "0", "saved": 0,
    "cam_fps": "0.0", "vis_fps": "0.0",
    "gps_lat": "---", "gps_lon": "---", "alt": "---", "sats": 0, "flight_mode": "---",
    "est_lat": "---", "est_lon": "---", "est_obs": 0,
}

# ── Rolling FPS ──
class RollingFPS:
    def __init__(self, window=3.0):
        self.window = window
        self.times = []
    def tick(self):
        now = time.time()
        self.times.append(now)
        self.times = [t for t in self.times if t > now - self.window]
    def fps(self):
        if len(self.times) < 2:
            return 0.0
        span = self.times[-1] - self.times[0]
        return (len(self.times) - 1) / span if span > 0 else 0.0

cam_fps_tracker = RollingFPS()
vis_fps_tracker = RollingFPS()


# ── FOV ──
def get_fov_info():
    sw = config.SENSOR_WIDTH_MM
    fl = config.FOCAL_LENGTH_MM
    iw, ih = config.IMAGE_W, config.IMAGE_H
    hfov_deg = 2 * math.degrees(math.atan(sw / (2 * fl)))
    f_px = fl * iw / sw
    return {"hfov_deg": hfov_deg, "f_px": f_px, "sensor_w": sw,
            "focal_mm": fl, "img_w": iw, "img_h": ih}

def ground_coverage(alt_m):
    sw, fl = config.SENSOR_WIDTH_MM, config.FOCAL_LENGTH_MM
    w = alt_m * sw / fl
    return w, w * config.IMAGE_H / config.IMAGE_W

FOV = get_fov_info()


# ── Dummy GPS estimator (same as passive_watch.py) ──
class DummyEstimator:
    def __init__(self):
        self.total_weight = 0.0
        self.weighted_lat = 0.0
        self.weighted_lon = 0.0
        self.count = 0

    def add_observation(self, drone_lat, drone_lon, alt_m, yaw_deg, det_x, det_y):
        if alt_m < 0.3:
            alt_m = 0.3
        dx_px = (det_x - 0.5) * FOV["img_w"]
        dy_px = (det_y - 0.5) * FOV["img_h"]
        dx_m = dx_px * alt_m / FOV["f_px"]
        dy_m = dy_px * alt_m / FOV["f_px"]
        yaw_rad = math.radians(yaw_deg)
        forward_m = -dy_m
        right_m = dx_m
        north_m = forward_m * math.cos(yaw_rad) - right_m * math.sin(yaw_rad)
        east_m = forward_m * math.sin(yaw_rad) + right_m * math.cos(yaw_rad)
        lat_m_per_deg = 111132.954 - 559.822 * math.cos(2 * math.radians(drone_lat))
        lon_m_per_deg = 111132.954 * math.cos(math.radians(drone_lat))
        est_lat = drone_lat + north_m / lat_m_per_deg
        est_lon = drone_lon + east_m / lon_m_per_deg
        weight = 1.0 / (alt_m * alt_m)
        dist_from_centre = math.sqrt(dx_px**2 + dy_px**2)
        max_dist = math.sqrt((FOV["img_w"]/2)**2 + (FOV["img_h"]/2)**2)
        weight *= 1.0 + 4.0 * max(0, 1.0 - dist_from_centre / (max_dist * 0.3))
        self.weighted_lat += est_lat * weight
        self.weighted_lon += est_lon * weight
        self.total_weight += weight
        self.count += 1
        return est_lat, est_lon

    def get_estimate(self):
        if self.total_weight <= 0:
            return None
        return (self.weighted_lat / self.total_weight,
                self.weighted_lon / self.total_weight, self.count)

    def reset(self):
        self.total_weight = 0.0
        self.weighted_lat = 0.0
        self.weighted_lon = 0.0
        self.count = 0

dummy_estimator = DummyEstimator()


# ── GPS state ──
gps_data = {
    "lat": 0.0, "lon": 0.0, "alt": 0.0, "sats": 0, "fix": 0,
    "yaw": 0.0, "pitch": 0.0, "roll": 0.0, "mode": "---"
}

COPTER_MODES = {
    0: "STABILIZE", 2: "ALT_HOLD", 3: "AUTO", 4: "GUIDED",
    5: "LOITER", 6: "RTL", 9: "LAND", 16: "POSHOLD",
}

def mavlink_reader(mav):
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
            elif mtype == 'HEARTBEAT' and msg.type != 6:
                gps_data["mode"] = COPTER_MODES.get(msg.custom_mode, f"MODE_{msg.custom_mode}")
            elif mtype == 'ATTITUDE':
                gps_data["yaw"] = msg.yaw * 57.2958
                gps_data["pitch"] = msg.pitch * 57.2958
                gps_data["roll"] = msg.roll * 57.2958
        except Exception:
            time.sleep(0.1)


# ── Stream overlay (only for live stream, NOT saved images) ──
def draw_stream_overlay(frame, last_det):
    """Overlay for stream only — saved images stay clean."""
    h, w = frame.shape[:2]
    display = frame.copy()

    if last_det is not None:
        cx, cy, conf, age = last_det
        if age < 2.0:
            alpha = max(0.3, 1.0 - age / 2.0)
            color = (0, int(255 * alpha), 0)
            box = 40
            cv2.rectangle(display, (cx - box, cy - box), (cx + box, cy + box), color, 2)
            cv2.putText(display, f"{conf:.2f}", (cx - box, cy - box - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    # GPS bar
    lat, lon, alt = gps_data["lat"], gps_data["lon"], gps_data["alt"]
    gps_text = f"GPS: {lat:.6f}, {lon:.6f} | Alt: {alt:.1f}m" if (lat or lon) else "GPS: No Fix"
    cv2.rectangle(display, (0, h - 25), (w, h), (0, 0, 0), -1)
    cv2.putText(display, gps_text, (5, h - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 170, 255), 1)

    # FPS bar
    cv2.rectangle(display, (0, 0), (w, 25), (0, 0, 0), -1)
    fps_text = f"CAM:{cam_fps_tracker.fps():.1f}  VIS:{vis_fps_tracker.fps():.1f}  CLEAN SAVE MODE"
    cv2.putText(display, fps_text, (5, 16), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)

    return display


# ── Main ──
def main():
    global latest_jpeg, latest_det_jpeg

    pi_ip = "localhost"
    try:
        result = subprocess.run(['hostname', '-I'], capture_output=True, text=True, timeout=3)
        parts = result.stdout.strip().split()
        if parts:
            pi_ip = parts[0]
    except Exception:
        pass

    print("=" * 50)
    print("  SAR CLEAN CAPTURE")
    print("  Saves RAW images — no overlay, no text")
    print("  Filename: {num}_{lat}_{lon}.png")
    print("  ZERO commands sent. Safe to run anytime.")
    print("=" * 50)
    print(f"  Confidence: {args.conf}")
    print(f"  Max FPS:    {args.fps}")
    if not args.no_save:
        os.makedirs(args.save_dir, exist_ok=True)
        print(f"  Saving to:  {args.save_dir}/")
    else:
        print("  Saving:     OFF")
    print(f"  Dashboard:  http://{pi_ip}:{args.port}/")
    print(f"  Stream:     http://{pi_ip}:{args.port}/stream")
    print()

    # MAVLink (read-only)
    mav = None
    if not args.no_mavlink:
        try:
            from pymavlink import mavutil
            print("[MAV] Connecting to udpin:0.0.0.0:14550 (read-only)...")
            mav = mavutil.mavlink_connection('udpin:0.0.0.0:14550')
            msg = mav.recv_match(type='HEARTBEAT', blocking=True, timeout=5)
            if msg:
                print(f"[MAV] Connected! Reading telemetry (zero commands)")
                threading.Thread(target=mavlink_reader, args=(mav,), daemon=True).start()
            else:
                print("[MAV] No heartbeat — running without GPS")
                mav = None
        except Exception as e:
            print(f"[MAV] Could not connect: {e}")
            mav = None
    else:
        print("[MAV] Skipped (--no-mavlink)")

    # Camera + AI
    eyes = VisionSystem(camera_index=0, model_path=args.model)
    if not eyes.using_ai:
        print("[WARN] AI model not loaded — stream only")
    print("[OK] Camera ready. Ctrl+C to stop.\n")

    # HTTP server
    server = ThreadedServer(('0.0.0.0', args.port), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    print(f"[OK] Stream on port {args.port}\n")

    # CSV log
    csv_path = os.path.join(args.save_dir, "clean_detection_log.csv") if not args.no_save else None
    csv_file = None
    csv_writer = None
    if csv_path:
        os.makedirs(args.save_dir, exist_ok=True)
        csv_file = open(csv_path, 'a', newline='')
        csv_writer = csv.writer(csv_file)
        if os.path.getsize(csv_path) == 0:
            csv_writer.writerow(['timestamp', 'frame', 'confidence', 'px_x', 'px_y',
                                 'drone_lat', 'drone_lon', 'alt_m', 'sats', 'yaw', 'mode',
                                 'est_dummy_lat', 'est_dummy_lon', 'est_n_obs', 'filename'])

    # Main loop
    frame_count = 0
    det_count = 0
    saved_count = 0
    last_inference = 0
    min_interval = 1.0 / args.fps if args.fps > 0 else 0
    last_det = None
    last_det_time = 0

    while True:
        frame = eyes.get_frame()
        if frame is None:
            time.sleep(0.01)
            continue

        frame_count += 1
        now = time.time()
        cam_fps_tracker.tick()

        # Detection (throttled)
        if eyes.using_ai and (now - last_inference) >= min_interval:
            last_inference = now
            # IMPORTANT: detect on a COPY so bounding box doesn't get drawn on saved frame
            det_frame = frame.copy()
            found, x, y, conf = eyes.detect_in_image(det_frame)
            vis_fps_tracker.tick()

            if found and conf >= args.conf:
                det_count += 1
                h, w = frame.shape[:2]
                cx, cy = int(x * w), int(y * h)
                last_det = (cx, cy, conf, 0.0)
                last_det_time = now

                # GPS estimate
                d_lat, d_lon = gps_data["lat"], gps_data["lon"]
                d_alt = gps_data["alt"]
                d_yaw = gps_data["yaw"]
                est_result = None
                if d_lat != 0.0 or d_lon != 0.0:
                    est_result = dummy_estimator.add_observation(
                        d_lat, d_lon, d_alt, d_yaw, x, y)

                # Save CLEAN image (no overlay, no text, raw frame)
                if not args.no_save:
                    saved_count += 1
                    lat, lon = gps_data["lat"], gps_data["lon"]
                    alt = gps_data["alt"]

                    if lat != 0.0 or lon != 0.0:
                        fname = f"{saved_count:04d}_{lat:.6f}_{lon:.6f}.png"
                    else:
                        fname = f"{saved_count:04d}_nogps.png"

                    # Save the RAW frame — no overlay, no bbox, nothing
                    cv2.imwrite(os.path.join(args.save_dir, fname), frame)

                    # JSON sidecar with full metadata
                    g_w, g_h = ground_coverage(d_alt) if d_alt > 0.5 else (0, 0)
                    est_snap = dummy_estimator.get_estimate()
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
                    json_fname = fname.replace('.png', '.json')
                    with open(os.path.join(args.save_dir, json_fname), 'w') as jf:
                        json.dump(meta, jf, indent=2)

                    # CSV log
                    if csv_writer:
                        est = dummy_estimator.get_estimate()
                        csv_writer.writerow([
                            datetime.now().isoformat(), frame_count, f"{conf:.3f}",
                            cx, cy, f"{d_lat:.7f}", f"{d_lon:.7f}", f"{d_alt:.1f}",
                            gps_data["sats"], f"{gps_data['yaw']:.0f}", gps_data["mode"],
                            f"{est[0]:.7f}" if est else "",
                            f"{est[1]:.7f}" if est else "",
                            est[2] if est else 0, fname
                        ])
                        csv_file.flush()

        # Update detection age
        if last_det is not None:
            age = now - last_det_time
            last_det = (last_det[0], last_det[1], last_det[2], age)

        # Stream gets overlay (saved images don't)
        display = draw_stream_overlay(frame, last_det)
        _, jpg = cv2.imencode('.jpg', display, [cv2.IMWRITE_JPEG_QUALITY, 70])
        with frame_lock:
            latest_jpeg = jpg.tobytes()

        # Stats
        det_pct = (det_count / frame_count * 100) if frame_count > 0 else 0
        lat, lon = gps_data["lat"], gps_data["lon"]
        est = dummy_estimator.get_estimate()
        stats.update({
            "frames": frame_count, "detections": det_count,
            "det_pct": f"{det_pct:.0f}", "saved": saved_count,
            "cam_fps": f"{cam_fps_tracker.fps():.1f}",
            "vis_fps": f"{vis_fps_tracker.fps():.1f}",
            "gps_lat": f"{lat:.6f}" if lat else "---",
            "gps_lon": f"{lon:.6f}" if lon else "---",
            "alt": f"{gps_data['alt']:.1f}" if gps_data['alt'] else "---",
            "sats": gps_data["sats"], "flight_mode": gps_data["mode"],
            "est_lat": f"{est[0]:.6f}" if est else "---",
            "est_lon": f"{est[1]:.6f}" if est else "---",
            "est_obs": est[2] if est else 0,
        })

        if frame_count % 50 == 0:
            gps_str = f"GPS:{lat:.5f},{lon:.5f}" if lat else "GPS:---"
            print(f"  #{frame_count} CAM:{cam_fps_tracker.fps():.1f} VIS:{vis_fps_tracker.fps():.1f} Det:{det_count} ({det_pct:.0f}%) Saved:{saved_count} {gps_str}")

    if csv_file:
        csv_file.close()
    eyes.release()
    server.shutdown()


if __name__ == "__main__":
    main()
