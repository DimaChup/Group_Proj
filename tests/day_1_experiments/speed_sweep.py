#!/usr/bin/env python3
"""
speed_sweep.py — Experiment: Detection Rate vs Flyover Speed
=============================================================
PASSIVE — sends ZERO commands to Cube. Pilot flies manually.

Protocol:
  1. Pilot flies over dummy at fixed altitude (~15m recommended)
  2. First pass: slow (~3 m/s)
  3. Second pass: medium (~5 m/s)
  4. Third pass: fast (~7 m/s)
  5. Repeat if battery allows

Script auto-bins data by groundspeed (2 m/s buckets) at a fixed
altitude range. Measures detection rate, confidence, and image blur.

Output CSV columns:
  timestamp, altitude_m, groundspeed, speed_bucket, detection,
  confidence, blur_metric, pixel_x, pixel_y, gps_lat, gps_lon

Usage:
    python tests/experiments/speed_sweep.py --headless --stream
    python tests/experiments/speed_sweep.py --headless --alt 15
    python tests/experiments/speed_sweep.py --headless --save-frames
"""

import sys, os, csv, time, math, threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from collections import defaultdict

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, project_root)

import cv2
import numpy as np
import config

# ── CLI flags ────────────────────────────────────────────────────────────
HEADLESS = "--headless" in sys.argv
STREAM = "--stream" in sys.argv
SAVE_FRAMES = "--save-frames" in sys.argv
TARGET_ALT = 15  # only count frames near this altitude
ALT_TOLERANCE = 5  # +/- 5m
STREAM_PORT = 8090
STREAM_W, STREAM_H = 320, 240
STREAM_FPS = 5
STREAM_QUALITY = 50
SAVE_DIR = os.path.join(project_root, "speed_frames")

for _i, _a in enumerate(sys.argv):
    if _a == "--alt" and _i + 1 < len(sys.argv):
        TARGET_ALT = float(sys.argv[_i + 1])
    elif _a == "--stream-port" and _i + 1 < len(sys.argv):
        STREAM_PORT = int(sys.argv[_i + 1])
    elif _a == "--save-dir" and _i + 1 < len(sys.argv):
        SAVE_DIR = sys.argv[_i + 1]

# ── MJPEG stream ─────────────────────────────────────────────────────────
_stream_frame = None
_stream_lock = threading.Lock()

class _StreamHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/stream':
            self.send_response(200)
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=frame')
            self.end_headers()
            while True:
                with _stream_lock:
                    f = _stream_frame
                if f is None:
                    time.sleep(0.1)
                    continue
                small = cv2.resize(f, (STREAM_W, STREAM_H))
                _, jpeg = cv2.imencode('.jpg', small, [cv2.IMWRITE_JPEG_QUALITY, STREAM_QUALITY])
                try:
                    self.wfile.write(b'--frame\r\nContent-Type: image/jpeg\r\n')
                    self.wfile.write(f'Content-Length: {len(jpeg)}\r\n\r\n'.encode())
                    self.wfile.write(jpeg.tobytes())
                    self.wfile.write(b'\r\n')
                except (BrokenPipeError, ConnectionResetError):
                    break
                time.sleep(1.0 / STREAM_FPS)
        elif self.path == '/':
            html = ('<html><body style="background:#111;text-align:center;font-family:monospace">'
                    '<h2 style="color:#0ff">Speed Sweep Experiment</h2>'
                    f'<img src="/stream" style="max-width:100%;border:2px solid #0ff"/>'
                    '</body></html>')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode())
        else:
            self.send_response(404)
            self.end_headers()
    def log_message(self, *a): pass

# ── Blur metric ──────────────────────────────────────────────────────────
def laplacian_blur(frame):
    """Higher = sharper. Lower = more motion blur."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return cv2.Laplacian(gray, cv2.CV_64F).var()

# ── Cube connection (read-only, same as altitude_sweep) ──────────────────
def connect_cube():
    try:
        from pymavlink import mavutil
    except ImportError:
        return None
    conn_str = config.CONNECTION_STR
    print(f"[CUBE] Connecting: {conn_str}")
    try:
        if conn_str.startswith("/dev/"):
            mav = mavutil.mavlink_connection(conn_str, baud=config.BAUD_RATE)
        else:
            mav = mavutil.mavlink_connection(conn_str)
        mav.wait_heartbeat(timeout=10)
        print(f"[CUBE] Connected (system {mav.target_system})")
        mav.mav.request_data_stream_send(
            mav.target_system, mav.target_component, 0, 4, 1)
        return mav
    except Exception as e:
        print(f"[CUBE] Failed: {e}")
        return None

def read_telemetry(mav):
    data = {"alt": 0.0, "lat": 0.0, "lon": 0.0, "groundspeed": 0.0,
            "battery_v": 0.0}
    if mav is None:
        return data
    while True:
        msg = mav.recv_match(blocking=False)
        if msg is None:
            break
        mt = msg.get_type()
        if mt == "GLOBAL_POSITION_INT":
            data["lat"] = msg.lat / 1e7
            data["lon"] = msg.lon / 1e7
            data["alt"] = msg.relative_alt / 1000.0
        elif mt == "VFR_HUD":
            data["groundspeed"] = msg.groundspeed
            if data["alt"] == 0:
                data["alt"] = msg.alt
        elif mt == "SYS_STATUS":
            data["battery_v"] = msg.voltage_battery / 1000.0
    return data

# ── Speed buckets ────────────────────────────────────────────────────────
SPEED_BUCKETS = [
    (0, 2, "0-2"),      # hovering
    (2, 4, "2-4"),      # slow
    (4, 6, "4-6"),      # medium
    (6, 8, "6-8"),      # fast
    (8, 12, "8-12"),    # very fast
]

def get_speed_bucket(spd):
    for lo, hi, label in SPEED_BUCKETS:
        if lo <= spd < hi:
            return label
    return None

# ── Main ─────────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("  EXPERIMENT: Detection Rate vs Flyover Speed")
    print("  PASSIVE — sends ZERO commands. Pilot flies manually.")
    print("=" * 60)
    print()
    print(f"  Target altitude: {TARGET_ALT}m (+/- {ALT_TOLERANCE}m)")
    print("  Protocol: fly over dummy at 3, 5, 7 m/s passes")
    print("  Script auto-bins by groundspeed and measures blur.")
    print()

    mav = connect_cube()

    from vision import VisionSystem
    eyes = VisionSystem(camera_index=0,
                        model_path=os.path.join(project_root, "best.tflite"))

    if SAVE_FRAMES:
        os.makedirs(SAVE_DIR, exist_ok=True)
        print(f"[FRAMES] Saving to: {SAVE_DIR}/")

    ts_start = time.strftime("%Y%m%d_%H%M%S")
    log_path = os.path.join(project_root, f"exp_speed_{ts_start}.csv")
    log_file = open(log_path, "w", newline="")
    writer = csv.writer(log_file)
    writer.writerow([
        "timestamp", "flight_sec", "altitude_m", "groundspeed",
        "speed_bucket", "detection", "confidence", "blur_metric",
        "pixel_x", "pixel_y", "gps_lat", "gps_lon", "battery_v"
    ])

    if STREAM:
        try:
            server = HTTPServer(('0.0.0.0', STREAM_PORT), _StreamHandler)
            threading.Thread(target=server.serve_forever, daemon=True).start()
            print(f"[STREAM] http://0.0.0.0:{STREAM_PORT}/")
        except Exception as e:
            print(f"[STREAM] Failed: {e}")

    if not HEADLESS:
        cv2.namedWindow("Speed Sweep", cv2.WINDOW_NORMAL)

    bucket_stats = defaultdict(lambda: {"frames": 0, "detections": 0,
                                         "confidences": [], "blurs": [],
                                         "det_blurs": [], "miss_blurs": []})
    t_start = time.time()
    frame_count = 0
    in_range_frames = 0

    print(f"\n[READY] Logging to: {log_path}")
    print("[READY] Pilot can take off. Ctrl+C to stop.\n")

    try:
        while True:
            frame = eyes.get_frame()
            if frame is None:
                time.sleep(0.05)
                continue

            frame_count += 1
            now = time.time()
            flight_sec = now - t_start
            telem = read_telemetry(mav)
            alt = telem["alt"]
            spd = telem["groundspeed"]

            # Only count frames at target altitude
            in_alt_range = abs(alt - TARGET_ALT) <= ALT_TOLERANCE
            speed_bucket = get_speed_bucket(spd) if in_alt_range else None

            # Detection
            found, px, py, conf = False, 0, 0, 0.0
            if eyes.using_ai:
                found, px, py, conf = eyes.detect_in_image(frame)

            # Blur metric
            blur = laplacian_blur(frame)

            # Bucket stats (only when at target altitude)
            if speed_bucket is not None:
                in_range_frames += 1
                b = bucket_stats[speed_bucket]
                b["frames"] += 1
                b["blurs"].append(blur)
                if found:
                    b["detections"] += 1
                    b["confidences"].append(conf)
                    b["det_blurs"].append(blur)
                else:
                    b["miss_blurs"].append(blur)

            # CSV row (log everything, not just in-range)
            writer.writerow([
                time.strftime("%H:%M:%S"), f"{flight_sec:.1f}",
                f"{alt:.1f}", f"{spd:.1f}",
                speed_bucket if speed_bucket else "",
                "YES" if found else "no",
                f"{conf:.3f}" if found else "",
                f"{blur:.0f}",
                px if found else "", py if found else "",
                f"{telem['lat']:.7f}", f"{telem['lon']:.7f}",
                f"{telem['battery_v']:.1f}"
            ])
            log_file.flush()

            # Save frame
            if SAVE_FRAMES and speed_bucket and frame_count % 3 == 0:
                tag = f"DET_{conf:.2f}" if found else "MISS"
                fname = f"{tag}_spd{spd:.1f}_alt{alt:.1f}_blur{blur:.0f}_{frame_count:06d}.jpg"
                cv2.imwrite(os.path.join(SAVE_DIR, fname), frame)

            # Stream
            if STREAM:
                display = frame.copy()
                in_str = "IN RANGE" if in_alt_range else "OUT OF RANGE"
                color = (0, 255, 255) if in_alt_range else (0, 0, 200)
                cv2.putText(display, f"SPD: {spd:.1f} m/s  ALT: {alt:.1f}m  [{in_str}]",
                            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                cv2.putText(display, f"BLUR: {blur:.0f}  {'DETECTED' if found else ''}",
                            (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                            (0, 255, 0) if found else (150, 150, 150), 2)
                if found:
                    cv2.circle(display, (int(px), int(py)), 15, (0, 255, 0), 2)
                global _stream_frame
                with _stream_lock:
                    _stream_frame = display

            # Terminal
            if HEADLESS and (frame_count % 30 == 0 or found):
                tag = f"DETECT conf={conf:.2f}" if found else "scanning"
                rng = "IN" if in_alt_range else "OUT"
                print(f"  [{tag}]  spd={spd:.1f}  alt={alt:.1f}  blur={blur:.0f}  [{rng}]")

            if not HEADLESS:
                cv2.imshow("Speed Sweep", frame)
                if cv2.waitKey(1) & 0xFF in (ord('q'), 27):
                    break

    except KeyboardInterrupt:
        print("\nStopping...")

    log_file.close()
    eyes.release()
    if not HEADLESS:
        cv2.destroyAllWindows()

    # ── Summary ──────────────────────────────────────────────────────────
    print()
    print("=" * 80)
    print("  SPEED SWEEP RESULTS")
    print(f"  (altitude range: {TARGET_ALT-ALT_TOLERANCE:.0f}-{TARGET_ALT+ALT_TOLERANCE:.0f}m)")
    print("=" * 80)
    print(f"  {'Speed':>8}  {'Frames':>8}  {'Dets':>6}  {'Rate':>8}  {'Avg Conf':>10}  "
          f"{'Avg Blur':>10}  {'Det Blur':>10}  {'Miss Blur':>10}")
    print("  " + "-" * 78)

    for _, _, label in SPEED_BUCKETS:
        s = bucket_stats[label]
        if s["frames"] == 0:
            print(f"  {label:>7}s  {'---':>8}  {'---':>6}  {'---':>8}  {'---':>10}  "
                  f"{'---':>10}  {'---':>10}  {'---':>10}")
        else:
            rate = 100 * s["detections"] / s["frames"]
            avg_c = sum(s["confidences"]) / len(s["confidences"]) if s["confidences"] else 0
            avg_blur = sum(s["blurs"]) / len(s["blurs"])
            det_blur = sum(s["det_blurs"]) / len(s["det_blurs"]) if s["det_blurs"] else 0
            miss_blur = sum(s["miss_blurs"]) / len(s["miss_blurs"]) if s["miss_blurs"] else 0
            print(f"  {label:>7}s  {s['frames']:>8}  {s['detections']:>6}  {rate:>7.1f}%  "
                  f"{avg_c:>10.3f}  {avg_blur:>10.0f}  {det_blur:>10.0f}  {miss_blur:>10.0f}")

    print()
    print(f"  Total frames: {frame_count}  |  In-range frames: {in_range_frames}")
    print(f"  CSV saved: {log_path}")
    print()

    # Recommendation
    best_speed = None
    for _, _, label in reversed(SPEED_BUCKETS):
        s = bucket_stats[label]
        if s["frames"] >= 10 and s["detections"] / s["frames"] >= 0.5:
            best_speed = label
            break
    if best_speed:
        print(f"  RECOMMENDATION: Max reliable speed = {best_speed} m/s range")
        print(f"  Update config.py: SEARCH_SPEED_MPS accordingly")
    else:
        print("  RECOMMENDATION: Not enough data. Fly more passes.")
    print("=" * 80)


if __name__ == "__main__":
    main()
