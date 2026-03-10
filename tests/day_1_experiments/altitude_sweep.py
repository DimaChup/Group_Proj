#!/usr/bin/env python3
"""
altitude_sweep.py — Experiment: Detection Rate vs Altitude
==========================================================
PASSIVE — sends ZERO commands to Cube. Pilot flies manually.

Protocol:
  1. Pilot hovers directly above dummy at 10m — hold 30s
  2. Climb to 15m — hold 30s
  3. Climb to 20m — hold 30s
  4. Climb to 25m — hold 30s
  5. Climb to 30m — hold 30s

Script auto-bins data by altitude (5m buckets). After flight,
prints a summary table and saves CSV for later analysis.

Output CSV columns:
  timestamp, altitude_m, groundspeed, detection, confidence,
  pixel_x, pixel_y, expected_dummy_px, gps_lat, gps_lon, battery_v

Usage:
    python tests/experiments/altitude_sweep.py --headless --stream
    python tests/experiments/altitude_sweep.py --headless
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
STREAM_PORT = 8090
STREAM_W, STREAM_H = 320, 240
STREAM_FPS = 5
STREAM_QUALITY = 50

for _i, _a in enumerate(sys.argv):
    if _a == "--stream-port" and _i + 1 < len(sys.argv):
        STREAM_PORT = int(sys.argv[_i + 1])
    elif _a == "--stream-res" and _i + 1 < len(sys.argv):
        p = sys.argv[_i + 1].split("x")
        STREAM_W, STREAM_H = int(p[0]), int(p[1])

# ── MJPEG stream (reused from passive_flight.py) ────────────────────────
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
                    '<h2 style="color:#0f0">Altitude Sweep Experiment</h2>'
                    f'<img src="/stream" style="max-width:100%;border:2px solid #0f0"/>'
                    '</body></html>')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode())
        else:
            self.send_response(404)
            self.end_headers()
    def log_message(self, *a): pass

# ── FOV math ─────────────────────────────────────────────────────────────
def calc_fov():
    return 2 * math.atan(config.SENSOR_WIDTH_MM / (2 * config.FOCAL_LENGTH_MM))

def dummy_pixels_at_alt(alt_m):
    gw = 2 * max(1.0, alt_m) * math.tan(calc_fov() / 2)
    return int(config.DUMMY_HEIGHT_M * (config.IMAGE_W / gw))

# ── Cube connection (read-only) ──────────────────────────────────────────
def connect_cube():
    try:
        from pymavlink import mavutil
    except ImportError:
        print("[CUBE] pymavlink not installed")
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
            "battery_v": 0.0, "yaw": 0.0}
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
        elif mt == "ATTITUDE":
            data["yaw"] = math.degrees(msg.yaw)
    return data

# ── Altitude bucket ──────────────────────────────────────────────────────
ALT_BUCKETS = [10, 15, 20, 25, 30]
BUCKET_RANGE = 2.5  # +/- 2.5m = 5m bucket width

def get_bucket(alt):
    for b in ALT_BUCKETS:
        if abs(alt - b) <= BUCKET_RANGE:
            return b
    return None

# ── Main ─────────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("  EXPERIMENT: Detection Rate vs Altitude")
    print("  PASSIVE — sends ZERO commands. Pilot flies manually.")
    print("=" * 60)
    print()
    print("  Protocol: hover above dummy at 10m (30s), then 15, 20, 25, 30m")
    print("  Script auto-bins by altitude and logs everything.")
    print()

    mav = connect_cube()

    from vision import VisionSystem
    eyes = VisionSystem(camera_index=0,
                        model_path=os.path.join(project_root, "best.tflite"))
    if not eyes.using_ai:
        print("[WARN] AI model not loaded!")

    # CSV log
    ts_start = time.strftime("%Y%m%d_%H%M%S")
    log_path = os.path.join(project_root, f"exp_altitude_{ts_start}.csv")
    log_file = open(log_path, "w", newline="")
    writer = csv.writer(log_file)
    writer.writerow([
        "timestamp", "flight_sec", "altitude_m", "alt_bucket",
        "groundspeed", "detection", "confidence",
        "pixel_x", "pixel_y", "expected_dummy_px",
        "gps_lat", "gps_lon", "battery_v"
    ])

    # Start stream
    if STREAM:
        try:
            server = HTTPServer(('0.0.0.0', STREAM_PORT), _StreamHandler)
            threading.Thread(target=server.serve_forever, daemon=True).start()
            print(f"[STREAM] http://0.0.0.0:{STREAM_PORT}/")
        except Exception as e:
            print(f"[STREAM] Failed: {e}")

    if not HEADLESS:
        cv2.namedWindow("Altitude Sweep", cv2.WINDOW_NORMAL)

    # Stats per bucket
    bucket_stats = defaultdict(lambda: {"frames": 0, "detections": 0,
                                         "confidences": [], "pixel_sizes": []})
    t_start = time.time()
    frame_count = 0

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
            bucket = get_bucket(alt)
            dummy_px = dummy_pixels_at_alt(alt) if alt > 1 else 0

            # Detection
            found, px, py, conf = False, 0, 0, 0.0
            if eyes.using_ai:
                found, px, py, conf = eyes.detect_in_image(frame)

            # Bucket stats
            if bucket is not None:
                b = bucket_stats[bucket]
                b["frames"] += 1
                if found:
                    b["detections"] += 1
                    b["confidences"].append(conf)
                    b["pixel_sizes"].append(dummy_px)

            # CSV row
            writer.writerow([
                time.strftime("%H:%M:%S"), f"{flight_sec:.1f}",
                f"{alt:.1f}", bucket if bucket else "",
                f"{telem['groundspeed']:.1f}",
                "YES" if found else "no",
                f"{conf:.3f}" if found else "",
                px if found else "", py if found else "",
                dummy_px,
                f"{telem['lat']:.7f}", f"{telem['lon']:.7f}",
                f"{telem['battery_v']:.1f}"
            ])
            log_file.flush()

            # Stream update
            if STREAM:
                display = frame.copy()
                # HUD overlay
                color = (0, 255, 0) if found else (200, 200, 200)
                bucket_str = f"{bucket}m" if bucket else "---"
                cv2.putText(display, f"ALT: {alt:.1f}m  BUCKET: {bucket_str}",
                            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                if found:
                    cv2.putText(display, f"DETECTED  conf={conf:.2f}",
                                (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.circle(display, (int(px), int(py)), 15, (0, 255, 0), 2)
                # Live stats for current bucket
                if bucket and bucket_stats[bucket]["frames"] > 0:
                    bs = bucket_stats[bucket]
                    rate = 100 * bs["detections"] / bs["frames"]
                    avg_c = (sum(bs["confidences"]) / len(bs["confidences"])
                             if bs["confidences"] else 0)
                    cv2.putText(display,
                                f"@{bucket}m: {rate:.0f}% det ({bs['detections']}/{bs['frames']})  avg_conf={avg_c:.2f}",
                                (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                global _stream_frame
                with _stream_lock:
                    _stream_frame = display

            # Display
            if HEADLESS:
                if frame_count % 30 == 0 or found:
                    det_str = f"DETECT conf={conf:.2f}" if found else "scanning"
                    print(f"  [{det_str}]  alt={alt:.1f}m  bucket={bucket}  "
                          f"frames={frame_count}  bat={telem['battery_v']:.1f}V")
            else:
                display = frame.copy()
                color = (0, 255, 0) if found else (200, 200, 200)
                cv2.putText(display, f"ALT: {alt:.1f}m  BUCKET: {bucket if bucket else '---'}",
                            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                if found:
                    cv2.circle(display, (int(px), int(py)), 15, (0, 255, 0), 2)
                cv2.imshow("Altitude Sweep", display)
                if cv2.waitKey(1) & 0xFF in (ord('q'), 27):
                    break

    except KeyboardInterrupt:
        print("\nStopping...")

    log_file.close()
    eyes.release()
    if not HEADLESS:
        cv2.destroyAllWindows()

    # ── Summary table ────────────────────────────────────────────────────
    print()
    print("=" * 70)
    print("  ALTITUDE SWEEP RESULTS")
    print("=" * 70)
    print(f"  {'Altitude':>10}  {'Frames':>8}  {'Detections':>10}  {'Rate':>8}  {'Avg Conf':>10}  {'Avg Px':>8}")
    print("  " + "-" * 62)

    for b in ALT_BUCKETS:
        s = bucket_stats[b]
        if s["frames"] == 0:
            print(f"  {b:>8}m  {'---':>8}  {'---':>10}  {'---':>8}  {'---':>10}  {'---':>8}")
        else:
            rate = 100 * s["detections"] / s["frames"]
            avg_c = sum(s["confidences"]) / len(s["confidences"]) if s["confidences"] else 0
            avg_px = sum(s["pixel_sizes"]) / len(s["pixel_sizes"]) if s["pixel_sizes"] else 0
            print(f"  {b:>8}m  {s['frames']:>8}  {s['detections']:>10}  {rate:>7.1f}%  {avg_c:>10.3f}  {avg_px:>7.0f}")

    print()
    print(f"  Total frames: {frame_count}")
    print(f"  CSV saved: {log_path}")
    print()

    # Recommendation
    best_alt = None
    best_rate = 0
    for b in ALT_BUCKETS:
        s = bucket_stats[b]
        if s["frames"] >= 10:
            rate = s["detections"] / s["frames"]
            if rate >= 0.5 and b > (best_alt or 0):
                best_alt = b
                best_rate = rate
    if best_alt:
        print(f"  RECOMMENDATION: Max reliable detection altitude = {best_alt}m "
              f"({best_rate*100:.0f}% rate)")
        print(f"  Update config.py: TARGET_ALT = {best_alt}")
    else:
        print("  RECOMMENDATION: Not enough data. Re-run with longer hover times.")
    print("=" * 70)


if __name__ == "__main__":
    main()
