#!/usr/bin/env python3
"""
Detection Log — General-purpose flight detection logger

WHAT:    The catch-all logger. Records every AI detection alongside full
         telemetry (GPS, altitude, speed, yaw, battery, satellite count) for
         any type of flight. Logs detections immediately and telemetry-only rows
         every 1 second. Optionally saves annotated detection images with
         bounding boxes.
WHY:     Provides a flexible data collection tool when the other experiments
         (altitude_sweep, speed_sweep, gps_accuracy) are too specific. Use it
         for general CV performance evaluation, demo flights, false positive
         debugging, or collecting data for later offline analysis.
WHEN:    Run during any manual RC flight. Works for any flight profile — no
         specific altitude or speed protocol required.
WHERE:   Pi (primary) or laptop (with webcam + SITL)
ENV:     Pi: pienv venv (pymavlink, opencv-headless, ai-edge-litert).
         Laptop: dev venv (ultralytics, opencv-python).
MODELS:  best.tflite from project root (active model, swappable).
RISK:    none — sends ZERO commands to the Cube. Purely observational.

USAGE:
    python tests/day_1_experiments/detection_log.py --headless --stream
    python tests/day_1_experiments/detection_log.py --headless --stream --save-detections
    python tests/day_1_experiments/detection_log.py --stream --det-dir ./my_detections

FLAGS:
    --headless          No cv2 window (required on Pi / PuTTY)
    --stream            Enable MJPEG video stream at http://0.0.0.0:8090/
    --stream-port N     Override stream port (default 8090)
    --save-detections   Save annotated JPEG for every detection (bounding box +
                        confidence + altitude overlay)
    --det-dir PATH      Override detection image directory (default detection_images/)

OUTPUT:
    - exp_detlog_YYYYMMDD_HHMMSS.csv in project root
      Columns: timestamp, flight_sec, lat, lon, alt, groundspeed, yaw,
      detection, confidence, pixel_x, pixel_y, expected_dummy_px,
      battery_v, battery_pct, gps_fix, gps_sats
    - Terminal summary: flight time, total frames, detection count and rate
    - Optional: annotated detection images in detection_images/ directory

BEST PRACTICES:
    - Use --save-detections to review false positives after the flight
    - Run alongside passive_watch.py on a different port for redundancy
    - Check gps_sats and gps_fix columns in CSV to correlate GPS quality
      with detection accuracy
    - Good for A/B model testing: run once with each model, compare CSVs

DEPENDENCIES:
    pymavlink, opencv-python (or opencv-python-headless), numpy, config.py, vision.py
"""

import sys, os, csv, time, math, threading
from http.server import HTTPServer, BaseHTTPRequestHandler

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, project_root)

import cv2
import numpy as np
import config

HEADLESS = "--headless" in sys.argv
STREAM = "--stream" in sys.argv
SAVE_DETECTIONS = "--save-detections" in sys.argv
STREAM_PORT = 8090
DET_DIR = os.path.join(project_root, "detection_images")

for _i, _a in enumerate(sys.argv):
    if _a == "--stream-port" and _i + 1 < len(sys.argv):
        STREAM_PORT = int(sys.argv[_i + 1])
    elif _a == "--det-dir" and _i + 1 < len(sys.argv):
        DET_DIR = sys.argv[_i + 1]

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
                small = cv2.resize(f, (320, 240))
                _, jpeg = cv2.imencode('.jpg', small, [cv2.IMWRITE_JPEG_QUALITY, 50])
                try:
                    self.wfile.write(b'--frame\r\nContent-Type: image/jpeg\r\n')
                    self.wfile.write(f'Content-Length: {len(jpeg)}\r\n\r\n'.encode())
                    self.wfile.write(jpeg.tobytes())
                    self.wfile.write(b'\r\n')
                except (BrokenPipeError, ConnectionResetError):
                    break
                time.sleep(0.2)
        elif self.path == '/':
            html = ('<html><body style="background:#111;text-align:center;font-family:monospace">'
                    '<h2 style="color:#fff">Detection Logger</h2>'
                    '<img src="/stream" style="max-width:100%;border:2px solid #fff"/>'
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
def dummy_pixels_at_alt(alt_m):
    fov = 2 * math.atan(config.SENSOR_WIDTH_MM / (2 * config.FOCAL_LENGTH_MM))
    gw = 2 * max(1.0, alt_m) * math.tan(fov / 2)
    return int(config.DUMMY_HEIGHT_M * (config.IMAGE_W / gw))

# ── Cube connection ─────────────────────────────────────────────────────
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
            "battery_v": 0.0, "battery_pct": -1, "yaw": 0.0,
            "gps_fix": 0, "gps_sats": 0}
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
            if msg.battery_remaining >= 0:
                data["battery_pct"] = msg.battery_remaining
        elif mt == "ATTITUDE":
            data["yaw"] = math.degrees(msg.yaw)
        elif mt == "GPS_RAW_INT":
            data["gps_fix"] = msg.fix_type
            data["gps_sats"] = msg.satellites_visible
    return data

# ── Main ─────────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("  DETECTION LOGGER — General Purpose")
    print("  PASSIVE — sends ZERO commands.")
    print("=" * 60)
    print()

    mav = connect_cube()

    from vision import VisionSystem
    eyes = VisionSystem(camera_index=0,
                        model_path=os.path.join(project_root, "best.tflite"))

    if SAVE_DETECTIONS:
        os.makedirs(DET_DIR, exist_ok=True)
        print(f"[SAVE] Detection images → {DET_DIR}/")

    ts_start = time.strftime("%Y%m%d_%H%M%S")
    log_path = os.path.join(project_root, f"exp_detlog_{ts_start}.csv")
    log_file = open(log_path, "w", newline="")
    writer = csv.writer(log_file)
    writer.writerow([
        "timestamp", "flight_sec", "lat", "lon", "alt", "groundspeed", "yaw",
        "detection", "confidence", "pixel_x", "pixel_y", "expected_dummy_px",
        "battery_v", "battery_pct", "gps_fix", "gps_sats"
    ])

    if STREAM:
        try:
            server = HTTPServer(('0.0.0.0', STREAM_PORT), _StreamHandler)
            threading.Thread(target=server.serve_forever, daemon=True).start()
            print(f"[STREAM] http://0.0.0.0:{STREAM_PORT}/")
        except Exception as e:
            print(f"[STREAM] Failed: {e}")

    if not HEADLESS:
        cv2.namedWindow("Detection Log", cv2.WINDOW_NORMAL)

    t_start = time.time()
    frame_count = 0
    det_count = 0
    det_saved = 0
    last_log = 0

    print(f"\n[READY] Logging to: {log_path}")
    print("[READY] Fly anywhere. Ctrl+C to stop.\n")

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
            dummy_px = dummy_pixels_at_alt(alt) if alt > 1 else 0

            found, px, py, conf = False, 0, 0, 0.0
            if eyes.using_ai:
                found, px, py, conf = eyes.detect_in_image(frame)

            if found:
                det_count += 1

                # Save detection image
                if SAVE_DETECTIONS:
                    det_frame = frame.copy()
                    box = max(30, dummy_px // 2) if dummy_px > 0 else 40
                    x1, y1 = max(0, int(px) - box), max(0, int(py) - box)
                    x2, y2 = min(frame.shape[1], int(px) + box), min(frame.shape[0], int(py) + box)
                    cv2.rectangle(det_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(det_frame, f"{conf:.2f} alt={alt:.0f}m",
                                (x1, y1 - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                    fname = (f"{time.strftime('%H%M%S')}_det{det_count}_"
                             f"conf{conf:.2f}_alt{alt:.0f}.jpg")
                    cv2.imwrite(os.path.join(DET_DIR, fname), det_frame)
                    det_saved += 1

            # Log (detections immediately, telemetry every 1s)
            if found or (now - last_log >= 1.0):
                writer.writerow([
                    time.strftime("%H:%M:%S"), f"{flight_sec:.1f}",
                    f"{telem['lat']:.7f}", f"{telem['lon']:.7f}",
                    f"{alt:.1f}", f"{telem['groundspeed']:.1f}",
                    f"{telem['yaw']:.1f}",
                    "YES" if found else "no",
                    f"{conf:.3f}" if found else "",
                    px if found else "", py if found else "",
                    dummy_px,
                    f"{telem['battery_v']:.1f}", telem['battery_pct'],
                    telem['gps_fix'], telem['gps_sats']
                ])
                log_file.flush()
                last_log = now

            # Stream
            if STREAM:
                display = frame.copy()
                color = (0, 255, 0) if found else (150, 150, 150)
                det_rate = (100 * det_count / frame_count) if frame_count > 0 else 0
                cv2.putText(display, f"ALT: {alt:.1f}m  SPD: {telem['groundspeed']:.1f}  "
                            f"DET: {det_count} ({det_rate:.0f}%)",
                            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)
                if found:
                    cv2.circle(display, (int(px), int(py)), 15, (0, 255, 0), 2)
                    cv2.putText(display, f"conf={conf:.2f}",
                                (int(px) + 20, int(py)), cv2.FONT_HERSHEY_SIMPLEX,
                                0.5, (0, 255, 0), 1)
                global _stream_frame
                with _stream_lock:
                    _stream_frame = display

            # Terminal
            if HEADLESS:
                if found:
                    print(f"  DETECT #{det_count}  conf={conf:.2f}  alt={alt:.1f}m  "
                          f"spd={telem['groundspeed']:.1f}  sats={telem['gps_sats']}")
                elif frame_count % 60 == 0:
                    print(f"  scanning... f={frame_count}  det={det_count}  "
                          f"alt={alt:.1f}  bat={telem['battery_v']:.1f}V")

            if not HEADLESS:
                cv2.imshow("Detection Log", frame)
                if cv2.waitKey(1) & 0xFF in (ord('q'), 27):
                    break

    except KeyboardInterrupt:
        print("\nStopping...")

    log_file.close()
    eyes.release()
    if not HEADLESS:
        cv2.destroyAllWindows()

    # ── Summary ──────────────────────────────────────────────────────────
    flight_min = (time.time() - t_start) / 60
    det_rate = (100 * det_count / frame_count) if frame_count > 0 else 0
    print()
    print("=" * 60)
    print("  DETECTION LOG SUMMARY")
    print("=" * 60)
    print(f"  Flight time:    {flight_min:.1f} min")
    print(f"  Frames:         {frame_count}")
    print(f"  Detections:     {det_count} ({det_rate:.1f}%)")
    if SAVE_DETECTIONS:
        print(f"  Images saved:   {det_saved} in {DET_DIR}/")
    print(f"  CSV saved:      {log_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
