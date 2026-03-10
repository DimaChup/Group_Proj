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
  .gps { color:#0af; margin-bottom:10px; }
  img { max-width:100%; border:1px solid #333; }
</style>
</head><body>
<h1>SAR Passive Watch</h1>
<div class="stats" id="stats">Starting...</div>
<div class="gps" id="gps">GPS: waiting...</div>
<img src="/stream" alt="Camera Feed">
<script>
  setInterval(()=>{
    fetch('/api/status').then(r=>r.json()).then(d=>{
      document.getElementById('stats').textContent =
        `CAM: ${d.cam_fps} fps | VISION: ${d.vis_fps} fps | STREAM: ${d.stream_fps} fps | Det: ${d.detections} (${d.det_pct}%) | Saved: ${d.saved}`;
      document.getElementById('gps').textContent =
        `GPS: ${d.gps_lat}, ${d.gps_lon} | Alt: ${d.alt}m | Sats: ${d.sats} | Mode: ${d.flight_mode}`;
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


# ── Stats ──
stats = {
    "frames": 0, "detections": 0, "det_pct": "0", "saved": 0,
    "cam_fps": "0.0", "vis_fps": "0.0", "stream_fps": "0.0",
    "gps_lat": "---", "gps_lon": "---", "alt": "---", "sats": 0, "flight_mode": "---"
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

    # Top bar: FPS + mode
    cv2.rectangle(display, (0, 0), (w, 30), (0, 0, 0), -1)
    cam_f = cam_fps_tracker.fps()
    vis_f = vis_fps_tracker.fps()
    str_f = stream_fps_tracker.fps()
    fps_text = f"CAM:{cam_f:.1f}  VIS:{vis_f:.1f}  STR:{str_f:.1f}"
    cv2.putText(display, fps_text, (5, 18),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)
    cv2.putText(display, mode, (w - 100, 18),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)

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
                                 'gps_lat', 'gps_lon', 'alt_m', 'sats', 'yaw', 'mode', 'filename'])

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

                # Save snapshot with GPS overlay
                if not args.no_save:
                    saved_count += 1
                    save_frame = draw_overlay(frame, last_det)

                    # Add GPS text on saved image (larger, more prominent)
                    lat, lon = gps_data["lat"], gps_data["lon"]
                    alt = gps_data["alt"]
                    ts = datetime.now().strftime("%H:%M:%S")

                    if lat != 0.0 or lon != 0.0:
                        fname = f"det_{saved_count:04d}_{conf:.2f}_{lat:.5f}_{lon:.5f}.jpg"
                    else:
                        fname = f"det_{saved_count:04d}_{conf:.2f}_nogps.jpg"

                    # Stamp on image
                    cv2.putText(save_frame, f"{ts} | conf:{conf:.2f}", (5, 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

                    cv2.imwrite(os.path.join(args.save_dir, fname), save_frame)

                    # CSV log
                    if csv_writer:
                        csv_writer.writerow([
                            datetime.now().isoformat(), frame_count, f"{conf:.3f}",
                            cx, cy, f"{lat:.7f}", f"{lon:.7f}", f"{alt:.1f}",
                            gps_data["sats"], f"{gps_data['yaw']:.0f}",
                            gps_data["mode"], fname
                        ])
                        csv_file.flush()

        # Update detection age for fading overlay
        if last_det is not None:
            age = now - last_det_time
            last_det = (last_det[0], last_det[1], last_det[2], age)

        # Draw overlay (detection box + GPS) on every frame for stream
        display = draw_overlay(frame, last_det)

        # Encode for stream
        _, jpg = cv2.imencode('.jpg', display, [cv2.IMWRITE_JPEG_QUALITY, 60])
        with frame_lock:
            latest_jpeg = jpg.tobytes()
        stream_fps_tracker.tick()

        # Update stats
        det_pct = (det_count / frame_count * 100) if frame_count > 0 else 0
        lat, lon = gps_data["lat"], gps_data["lon"]
        c_fps = cam_fps_tracker.fps()
        v_fps = vis_fps_tracker.fps()
        s_fps = stream_fps_tracker.fps()
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
