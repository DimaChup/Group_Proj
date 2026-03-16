#!/usr/bin/env python3
"""
STEP 7: FOV Calibration from real drone.

Hover at 2 different altitudes. At each one, measure the ground
area the camera can see (use markers on the ground). Enter the
width. Script reads altitude from Cube and calculates your real FOV.

Setup:
  1. Lay a tape measure or place markers at known distances on the ground
  2. Fly drone up, hover steady
  3. Press SPACE - script reads altitude from Cube
  4. Look at what the camera sees - enter the ground width (metres)
  5. Climb higher, repeat
  6. Script tells you the real FOV and what to put in config.py

Usage:
    python tests/calibration/alt_test.py                    # auto-detect
    python tests/calibration/alt_test.py /dev/ttyAMA0 57600 # manual
"""
import sys
import os
import math
import time
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, project_root)

import cv2
import config

headless = "--headless" in sys.argv
args = [a for a in sys.argv[1:] if a != "--headless"]

# ==========================================
#   Connect to Cube
# ==========================================
conn_str = None
baud = 57600
if len(args) >= 1:
    conn_str = args[0]
if len(args) >= 2:
    baud = int(args[1])

if conn_str is None:
    try:
        conn_str = config.CONNECTION_STR
        baud = config.BAUD_RATE
    except Exception:
        for port in ["/dev/ttyAMA0", "/dev/ttyACM0", "/dev/ttyUSB0"]:
            if os.path.exists(port):
                conn_str = port
                break
        if conn_str is None:
            conn_str = "tcp:127.0.0.1:5762"

print(f"[CUBE] Connecting: {conn_str} (baud={baud})")
from pymavlink import mavutil
if conn_str.startswith("/dev/"):
    mav = mavutil.mavlink_connection(conn_str, baud=baud)
else:
    mav = mavutil.mavlink_connection(conn_str)

print("[CUBE] Waiting for heartbeat...")
mav.wait_heartbeat(timeout=10)
print(f"[CUBE] Heartbeat OK")

# ==========================================
#   Camera (for live view only, no AI needed)
# ==========================================
cap = None
if not headless:
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        print("[OK] Camera opened for live view")
    else:
        cap = None
        print("[INFO] No camera display - altitude-only mode")

# ==========================================
#   Current config
# ==========================================
current_fov_h = 2 * math.atan(config.SENSOR_WIDTH_MM / (2 * config.FOCAL_LENGTH_MM))
current_fov_h_deg = math.degrees(current_fov_h)

print(f"\n{'=' * 50}")
print(f"  FOV CALIBRATION (real drone)")
print(f"{'=' * 50}")
print(f"  Current config:")
print(f"    SENSOR_WIDTH_MM = {config.SENSOR_WIDTH_MM}")
print(f"    FOCAL_LENGTH_MM = {config.FOCAL_LENGTH_MM}")
print(f"    FOV = {current_fov_h_deg:.1f} degrees")
print()
print(f"  WHAT TO DO:")
print(f"    1. Place markers on ground at known distances")
print(f"    2. Hover at altitude 1, press SPACE")
print(f"    3. Enter the ground width you can see (metres)")
print(f"    4. Climb to altitude 2, repeat")
print(f"    5. Press 'q' when done")
print(f"{'=' * 50}\n")

# ==========================================
#   Read altitude continuously
# ==========================================
alt = 0.0

def update_telemetry():
    global alt
    while True:
        msg = mav.recv_match(blocking=False)
        if not msg:
            break
        if msg.get_type() == 'GLOBAL_POSITION_INT':
            alt = msg.relative_alt / 1000.0

# ==========================================
#   Collect measurements
# ==========================================
measurements = []

if headless:
    # Headless: just read altitude and prompt
    print("  Mode: HEADLESS. Press Enter to record altitude, 'q' to finish.\n")
    try:
        while True:
            update_telemetry()
            time.sleep(0.1)

            # Print altitude every 2 seconds
            print(f"\r  Altitude: {alt:.1f}m   (press Enter to record)", end="", flush=True)

            # Check for input (non-blocking is hard, so just use blocking input)
            inp = input()
            if inp.strip().lower() == 'q':
                break

            recorded_alt = alt
            print(f"\n  Recorded altitude: {recorded_alt:.1f}m")
            try:
                width = float(input("  Ground width visible (metres): ").strip())
            except (ValueError, EOFError):
                print("  Skipped.\n")
                continue

            actual_fov = 2 * math.atan((width / 2) / recorded_alt)
            actual_fov_deg = math.degrees(actual_fov)
            predicted_w = 2 * recorded_alt * math.tan(current_fov_h / 2)

            measurements.append({
                'alt': recorded_alt,
                'width': width,
                'fov_deg': actual_fov_deg,
                'predicted_w': predicted_w,
            })

            print(f"  -> Measured FOV: {actual_fov_deg:.1f}deg  (config predicts {predicted_w:.1f}m width)")
            print()
    except (KeyboardInterrupt, EOFError):
        pass

else:
    # Display mode: show camera + altitude, SPACE to record
    try:
        while True:
            update_telemetry()

            frame = None
            if cap:
                ret, frame = cap.read()
                if not ret:
                    frame = None

            if frame is not None:
                h, w = frame.shape[:2]
                # Show altitude big
                cv2.putText(frame, f"ALT: {alt:.1f}m", (10, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 0), 3)

                # Show predicted footprint
                pred_w = 2 * max(0.5, alt) * math.tan(current_fov_h / 2)
                pred_h = pred_w * (config.IMAGE_H / config.IMAGE_W)
                cv2.putText(frame, f"Predicted: {pred_w:.1f}m x {pred_h:.1f}m", (10, 75),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

                # Show measurements so far
                for i, m in enumerate(measurements):
                    cv2.putText(frame, f"#{i+1}: {m['alt']:.0f}m -> {m['width']:.1f}m wide (FOV={m['fov_deg']:.1f}deg)",
                                (10, h - 60 + i * 25), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 1)

                cv2.putText(frame, "SPACE = record | q = done", (10, h - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

                cv2.imshow("FOV Calibration", frame)

            key = cv2.waitKey(30) & 0xFF
            if key == ord('q'):
                break
            elif key == ord(' '):
                recorded_alt = alt
                print(f"\n  Altitude recorded: {recorded_alt:.1f}m")
                print(f"  Config predicts: {2*recorded_alt*math.tan(current_fov_h/2):.1f}m wide at this height")
                try:
                    width = float(input("  Actual ground width visible (metres): ").strip())
                except (ValueError, EOFError):
                    print("  Skipped.\n")
                    continue

                actual_fov = 2 * math.atan((width / 2) / recorded_alt)
                actual_fov_deg = math.degrees(actual_fov)
                predicted_w = 2 * recorded_alt * math.tan(current_fov_h / 2)

                measurements.append({
                    'alt': recorded_alt,
                    'width': width,
                    'fov_deg': actual_fov_deg,
                    'predicted_w': predicted_w,
                })
                print(f"  -> Measured FOV: {actual_fov_deg:.1f}deg")
                print()

    except KeyboardInterrupt:
        pass

# ==========================================
#   Cleanup
# ==========================================
if cap:
    cap.release()
cv2.destroyAllWindows()

# ==========================================
#   Results
# ==========================================
print(f"\n{'=' * 50}")
print(f"  RESULTS ({len(measurements)} measurements)")
print(f"{'=' * 50}")

if not measurements:
    print("  No measurements taken.")
    print(f"{'=' * 50}\n")
    sys.exit(0)

for i, m in enumerate(measurements):
    err = m['width'] - m['predicted_w']
    print(f"  #{i+1}:  Alt={m['alt']:.1f}m  Width={m['width']:.1f}m  "
          f"FOV={m['fov_deg']:.1f}deg  (config predicted {m['predicted_w']:.1f}m, err={err:+.1f}m)")

avg_fov = sum(m['fov_deg'] for m in measurements) / len(measurements)
suggested_sensor = 2 * config.FOCAL_LENGTH_MM * math.tan(math.radians(avg_fov) / 2)
suggested_focal = config.SENSOR_WIDTH_MM / (2 * math.tan(math.radians(avg_fov) / 2))

print()
print(f"  Your actual FOV:  {avg_fov:.1f} degrees")
print(f"  Config FOV:       {current_fov_h_deg:.1f} degrees")
diff = avg_fov - current_fov_h_deg
print(f"  Difference:       {diff:+.1f} degrees")

if len(measurements) >= 2:
    fov_spread = max(m['fov_deg'] for m in measurements) - min(m['fov_deg'] for m in measurements)
    if fov_spread < 3.0:
        print(f"  Consistency:      GOOD (spread {fov_spread:.1f}deg between measurements)")
    else:
        print(f"  Consistency:      CHECK (spread {fov_spread:.1f}deg - re-measure if > 5deg)")

print()
if abs(diff) > 2.0:
    print(f"  >> UPDATE config.py with ONE of these:")
    print(f"     SENSOR_WIDTH_MM = {suggested_sensor:.2f}  (keep FOCAL_LENGTH_MM = {config.FOCAL_LENGTH_MM})")
    print(f"     FOCAL_LENGTH_MM = {suggested_focal:.2f}  (keep SENSOR_WIDTH_MM = {config.SENSOR_WIDTH_MM})")
else:
    print(f"  >> Config looks correct! No changes needed.")

# Show what footprint looks like with corrected values
print()
print(f"  CORRECTED FOOTPRINT TABLE:")
print(f"  {'Alt':<8} {'Current config':<18} {'After correction':<18}")
print(f"  {'-'*8} {'-'*18} {'-'*18}")
corrected_fov = math.radians(avg_fov)
for h in [5, 10, 15, 20, 25, 30]:
    old_w = 2 * h * math.tan(current_fov_h / 2)
    new_w = 2 * h * math.tan(corrected_fov / 2)
    print(f"  {h}m{'':<4} {old_w:.1f}m wide{'':<8} {new_w:.1f}m wide")

print(f"{'=' * 50}\n")
