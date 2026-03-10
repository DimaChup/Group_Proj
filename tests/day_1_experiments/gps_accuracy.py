#!/usr/bin/env python3
"""
gps_accuracy.py — Experiment: GPS Estimation Accuracy
=====================================================
PASSIVE — sends ZERO commands to Cube. Pilot flies manually.

Protocol:
  1. Before flight: enter known dummy GPS (from Mission Planner or phone)
  2. Pilot hovers above dummy at various altitudes
  3. Script estimates dummy GPS using pixel→GPS projection (same math as pi_flight.py)
  4. Compares estimated vs known GPS, logs error in metres

This tells you how accurate the GPS estimation pipeline is in the real world,
which directly predicts landing accuracy.

Output CSV columns:
  timestamp, drone_lat, drone_lon, drone_alt, yaw,
  detection, confidence, pixel_x, pixel_y,
  est_lat, est_lon, error_m, method

Usage:
    python tests/experiments/gps_accuracy.py --headless --stream --dummy-gps 51.4234,-2.6714
    python tests/experiments/gps_accuracy.py --headless --dummy-gps 51.4234,-2.6714
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
DUMMY_LAT = None
DUMMY_LON = None

for _i, _a in enumerate(sys.argv):
    if _a == "--dummy-gps" and _i + 1 < len(sys.argv):
        parts = sys.argv[_i + 1].split(",")
        DUMMY_LAT = float(parts[0])
        DUMMY_LON = float(parts[1])
    elif _a == "--stream-port" and _i + 1 < len(sys.argv):
        STREAM_PORT = int(sys.argv[_i + 1])

if DUMMY_LAT is None:
    print("=" * 60)
    print("  GPS ACCURACY EXPERIMENT")
    print("=" * 60)
    print()
    print("  You MUST provide the known dummy GPS position.")
    print("  Get it from Mission Planner (walk to dummy, read GPS) or phone.")
    print()
    print("  Usage:")
    print("    python tests/experiments/gps_accuracy.py --dummy-gps LAT,LON --headless --stream")
    print()
    gps_input = input("  Enter dummy GPS now (lat,lon): ").strip()
    if not gps_input:
        print("  No GPS entered. Exiting.")
        sys.exit(1)
    parts = gps_input.split(",")
    DUMMY_LAT = float(parts[0])
    DUMMY_LON = float(parts[1])

print(f"  Known dummy position: {DUMMY_LAT:.7f}, {DUMMY_LON:.7f}")

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
                    '<h2 style="color:#ff0">GPS Accuracy Experiment</h2>'
                    f'<img src="/stream" style="max-width:100%;border:2px solid #ff0"/>'
                    '</body></html>')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode())
        else:
            self.send_response(404)
            self.end_headers()
    def log_message(self, *a): pass

# ── Geo math ─────────────────────────────────────────────────────────────
def calc_fov():
    return 2 * math.atan(config.SENSOR_WIDTH_MM / (2 * config.FOCAL_LENGTH_MM))

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def pixel_to_gps(drone_lat, drone_lon, alt, yaw_deg, px, py):
    """Convert detection pixel (px, py) to estimated GPS using camera geometry."""
    if alt < 1:
        return drone_lat, drone_lon

    fov = calc_fov()
    ground_w = 2 * alt * math.tan(fov / 2)
    ground_h = ground_w * config.IMAGE_H / config.IMAGE_W
    m_per_px_x = ground_w / config.IMAGE_W
    m_per_px_y = ground_h / config.IMAGE_H

    # Pixel offset from image centre (right = +x, down = +y)
    dx_px = px - config.IMAGE_W / 2
    dy_px = py - config.IMAGE_H / 2

    # Convert to metres in camera frame
    dx_m = dx_px * m_per_px_x
    dy_m = dy_px * m_per_px_y

    # Rotate by yaw (camera frame → world frame)
    # Camera: +x = right, +y = down/forward
    # World: +x = east, +y = north
    yaw_rad = math.radians(yaw_deg)
    east = dx_m * math.cos(yaw_rad) + dy_m * math.sin(yaw_rad)
    north = -dx_m * math.sin(yaw_rad) + dy_m * math.cos(yaw_rad)

    # GPS offset
    d_lat = north / 111320.0
    d_lon = east / (111320.0 * math.cos(math.radians(drone_lat)))

    return drone_lat + d_lat, drone_lon + d_lon

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

# ── Main ─────────────────────────────────────────────────────────────────
def main():
    print()
    print("=" * 60)
    print("  EXPERIMENT: GPS Estimation Accuracy")
    print("  PASSIVE — sends ZERO commands. Pilot flies manually.")
    print("=" * 60)
    print()
    print(f"  Known dummy: {DUMMY_LAT:.7f}, {DUMMY_LON:.7f}")
    print("  Protocol: hover above dummy at various altitudes")
    print("  Script estimates GPS from pixel position and measures error.")
    print()

    mav = connect_cube()

    from vision import VisionSystem
    eyes = VisionSystem(camera_index=0,
                        model_path=os.path.join(project_root, "best.tflite"))

    ts_start = time.strftime("%Y%m%d_%H%M%S")
    log_path = os.path.join(project_root, f"exp_gps_{ts_start}.csv")
    log_file = open(log_path, "w", newline="")
    writer = csv.writer(log_file)
    writer.writerow([
        "timestamp", "flight_sec",
        "drone_lat", "drone_lon", "drone_alt", "yaw",
        "groundspeed", "detection", "confidence",
        "pixel_x", "pixel_y",
        "est_lat", "est_lon",
        "error_m",
        "battery_v"
    ])

    if STREAM:
        try:
            server = HTTPServer(('0.0.0.0', STREAM_PORT), _StreamHandler)
            threading.Thread(target=server.serve_forever, daemon=True).start()
            print(f"[STREAM] http://0.0.0.0:{STREAM_PORT}/")
        except Exception as e:
            print(f"[STREAM] Failed: {e}")

    if not HEADLESS:
        cv2.namedWindow("GPS Accuracy", cv2.WINDOW_NORMAL)

    # Running stats
    all_errors = []
    alt_errors = defaultdict(list)  # altitude_bucket → [error_m, ...]
    # Running average estimate
    est_lat_sum = 0.0
    est_lon_sum = 0.0
    est_weight = 0.0

    t_start = time.time()
    frame_count = 0
    det_count = 0

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

            found, px, py, conf = False, 0, 0, 0.0
            if eyes.using_ai:
                found, px, py, conf = eyes.detect_in_image(frame)

            est_lat, est_lon, error_m = 0, 0, 0
            if found and telem["lat"] != 0 and alt > 1:
                det_count += 1
                est_lat, est_lon = pixel_to_gps(
                    telem["lat"], telem["lon"], alt, telem["yaw"], px, py)
                error_m = haversine(DUMMY_LAT, DUMMY_LON, est_lat, est_lon)
                all_errors.append(error_m)

                # Inverse variance weighting (same as pi_flight.py)
                weight = 1.0 / max(1, alt * alt)
                est_lat_sum += est_lat * weight
                est_lon_sum += est_lon * weight
                est_weight += weight

                # Bin by altitude
                alt_bucket = round(alt / 5) * 5  # nearest 5m
                alt_errors[alt_bucket].append(error_m)

            # CSV
            writer.writerow([
                time.strftime("%H:%M:%S"), f"{flight_sec:.1f}",
                f"{telem['lat']:.7f}", f"{telem['lon']:.7f}",
                f"{alt:.1f}", f"{telem['yaw']:.1f}",
                f"{telem['groundspeed']:.1f}",
                "YES" if found else "no",
                f"{conf:.3f}" if found else "",
                px if found else "", py if found else "",
                f"{est_lat:.7f}" if found else "",
                f"{est_lon:.7f}" if found else "",
                f"{error_m:.1f}" if found else "",
                f"{telem['battery_v']:.1f}"
            ])
            log_file.flush()

            # Running average
            avg_error = sum(all_errors) / len(all_errors) if all_errors else 0
            if est_weight > 0:
                wavg_lat = est_lat_sum / est_weight
                wavg_lon = est_lon_sum / est_weight
                wavg_error = haversine(DUMMY_LAT, DUMMY_LON, wavg_lat, wavg_lon)
            else:
                wavg_error = 0

            # Stream
            if STREAM:
                display = frame.copy()
                if found:
                    cv2.circle(display, (int(px), int(py)), 15, (0, 255, 0), 2)
                    cv2.putText(display, f"DETECTED  err={error_m:.1f}m  conf={conf:.2f}",
                                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                else:
                    cv2.putText(display, f"scanning  alt={alt:.1f}m",
                                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (150, 150, 150), 2)
                cv2.putText(display,
                            f"AVG err: {avg_error:.1f}m  WEIGHTED err: {wavg_error:.1f}m  "
                            f"({det_count} obs)",
                            (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                global _stream_frame
                with _stream_lock:
                    _stream_frame = display

            # Terminal
            if HEADLESS:
                if found:
                    print(f"  DETECT #{det_count}  conf={conf:.2f}  alt={alt:.1f}m  "
                          f"err={error_m:.1f}m  avg={avg_error:.1f}m  wavg={wavg_error:.1f}m")
                elif frame_count % 60 == 0:
                    print(f"  scanning... {frame_count} frames  {det_count} detections  "
                          f"alt={alt:.1f}m  avg_err={avg_error:.1f}m")

            if not HEADLESS:
                cv2.imshow("GPS Accuracy", frame)
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
    print("=" * 70)
    print("  GPS ACCURACY RESULTS")
    print("=" * 70)
    print(f"  Known dummy:   {DUMMY_LAT:.7f}, {DUMMY_LON:.7f}")

    if est_weight > 0:
        wavg_lat = est_lat_sum / est_weight
        wavg_lon = est_lon_sum / est_weight
        wavg_err = haversine(DUMMY_LAT, DUMMY_LON, wavg_lat, wavg_lon)
        print(f"  Weighted est:  {wavg_lat:.7f}, {wavg_lon:.7f}")
        print(f"  Weighted err:  {wavg_err:.1f}m")
    print()

    if all_errors:
        print(f"  Total observations: {len(all_errors)}")
        print(f"  Mean error:     {sum(all_errors)/len(all_errors):.1f}m")
        print(f"  Median error:   {sorted(all_errors)[len(all_errors)//2]:.1f}m")
        print(f"  Min error:      {min(all_errors):.1f}m")
        print(f"  Max error:      {max(all_errors):.1f}m")
        print()

        # Error by altitude
        print(f"  {'Altitude':>10}  {'Obs':>6}  {'Mean Err':>10}  {'Min':>8}  {'Max':>8}")
        print("  " + "-" * 50)
        for alt_b in sorted(alt_errors.keys()):
            errs = alt_errors[alt_b]
            mean_e = sum(errs) / len(errs)
            print(f"  {alt_b:>8.0f}m  {len(errs):>6}  {mean_e:>9.1f}m  "
                  f"{min(errs):>7.1f}m  {max(errs):>7.1f}m")
    else:
        print("  No detections recorded!")

    print()
    print(f"  CSV saved: {log_path}")
    print()
    print("  INTERPRETATION:")
    print("    < 3m error → GPS estimation is good, offset landing will work")
    print("    3-5m error → acceptable, landing ~10m from target")
    print("    > 5m error → FOV calibration may be wrong, or yaw data is bad")
    print("=" * 70)


if __name__ == "__main__":
    main()
