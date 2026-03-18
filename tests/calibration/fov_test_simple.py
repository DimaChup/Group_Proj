#!/usr/bin/env python3
"""
FOV Test Simple — Quick single-measurement FOV check.

WHAT:    A lightweight FOV calibration script that shows a live camera feed with
         edge markers and crosshair. Press SPACE to pause and enter a height/width
         measurement. Calculates actual FOV in degrees and compares against config.py
         values. Suggests SENSOR_WIDTH_MM or FOCAL_LENGTH_MM corrections.
WHY:     Simpler alternative to fov_calibrate.py for quick spot-checks. Useful when
         you just want to verify the current config is still correct (e.g. after
         changing resolution or camera mount) without the full multi-height procedure.
WHEN:    Quick pre-flight sanity check, or when you only have time for one measurement.
         Use fov_calibrate.py for thorough calibration with consistency checking.
WHERE:   Both Pi and laptop (auto-detects picamera2 or OpenCV).
ENV:     Any venv with opencv and numpy. Does NOT use vision.py (opens camera directly).
MODELS:  None (camera only, no AI inference).
RISK:    None. Camera read-only, no commands sent.

USAGE:
    python tests/calibration/fov_test_simple.py             # with display
    python tests/calibration/fov_test_simple.py --headless  # text prompts only

FLAGS:
    --headless    Skip cv2 display, text-only prompts (for PuTTY/SSH)

OUTPUT:
    - Measured FOV in degrees vs config.py FOV
    - Predicted vs actual ground width at measured height
    - Error percentage
    - Suggested config.py corrections (SENSOR_WIDTH_MM or FOCAL_LENGTH_MM)

BEST PRACTICES:
    - Use a tape measure flat on the floor for precise width reading
    - Camera must point STRAIGHT DOWN (even small tilt skews the result)
    - Take multiple measurements at different heights for confidence
    - On Pi, the IMX296 outputs BGR despite RGB888 label — no cvtColor needed
    - If error > 2 degrees, update config.py before flying

DEPENDENCIES:
    opencv-python (or opencv-python-headless), numpy, config.py
    Optional: picamera2 (auto-detected on Pi)
"""
import sys
import os
import math
import time
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, project_root)

headless = "--headless" in sys.argv

import cv2
import numpy as np
import config

# ==========================================
#   Camera setup
# ==========================================
cap = None
picam = None
source = None

cap = cv2.VideoCapture(0)
if cap.isOpened():
    ret, _ = cap.read()
    if ret:
        source = "OpenCV"
        print(f"[OK] Camera: OpenCV")
    else:
        cap.release()
        cap = None

if cap is None:
    try:
        from picamera2 import Picamera2
        picam = Picamera2()
        picam.configure(picam.create_preview_configuration(
            main={"size": (640, 480), "format": "RGB888"}
        ))
        picam.start()
        time.sleep(1)
        source = "picamera2"
        print(f"[OK] Camera: picamera2")
    except Exception as e:
        print(f"[FAIL] No camera: {e}")
        sys.exit(1)

def get_frame():
    if source == "OpenCV":
        ret, frame = cap.read()
        return frame if ret else None
    else:
        frame = picam.capture_array()
        # IMX296 sensor outputs BGR despite RGB888 label — no conversion needed
        return frame

# ==========================================
#   Current config values
# ==========================================
current_fov_h = 2 * math.atan(config.SENSOR_WIDTH_MM / (2 * config.FOCAL_LENGTH_MM))
current_fov_h_deg = math.degrees(current_fov_h)

# Assume square-ish sensor ratio for vertical FOV
aspect = config.IMAGE_H / config.IMAGE_W
sensor_h_mm = config.SENSOR_WIDTH_MM * aspect
current_fov_v = 2 * math.atan(sensor_h_mm / (2 * config.FOCAL_LENGTH_MM))
current_fov_v_deg = math.degrees(current_fov_v)

print(f"\n{'=' * 55}")
print(f"  FOV CALIBRATION - Bench Test")
print(f"{'=' * 55}")
print(f"  Current config.py values:")
print(f"    SENSOR_WIDTH_MM  = {config.SENSOR_WIDTH_MM}")
print(f"    FOCAL_LENGTH_MM  = {config.FOCAL_LENGTH_MM}")
print(f"    Horizontal FOV   = {current_fov_h_deg:.1f} degrees")
print(f"    Vertical FOV     = {current_fov_v_deg:.1f} degrees")
print(f"    Resolution       = {config.IMAGE_W}x{config.IMAGE_H}")
print(f"{'=' * 55}")
print()
print("  HOW TO USE:")
print("  1. Hold camera pointing straight down at a known height")
print("  2. Place a ruler/tape on the ground")
print("  3. Note what width (cm) the camera can see edge-to-edge")
print("  4. Press SPACE (or Enter in headless) to record measurement")
print("  5. Enter height (cm) and visible width (cm)")
print("  6. Script calculates your actual FOV")
print()

measurements = []

if headless:
    # Headless mode: just take measurements via terminal
    print("  Mode: HEADLESS. Type measurements directly.\n")
    try:
        while True:
            print(f"  --- Measurement #{len(measurements)+1} ---")
            h_input = input("  Camera height above ground (cm): ").strip()
            if h_input.lower() == 'q':
                break
            w_input = input("  Visible ground width edge-to-edge (cm): ").strip()
            if w_input.lower() == 'q':
                break

            try:
                height_cm = float(h_input)
                width_cm = float(w_input)
            except ValueError:
                print("  Invalid number. Try again.\n")
                continue

            # Calculate actual FOV from measurement
            actual_fov_h = 2 * math.atan((width_cm / 2) / height_cm)
            actual_fov_h_deg = math.degrees(actual_fov_h)

            # What config.py predicts at this height
            predicted_width = 2 * height_cm * math.tan(current_fov_h / 2)

            measurements.append({
                'height_cm': height_cm,
                'width_cm': width_cm,
                'actual_fov_deg': actual_fov_h_deg,
                'predicted_width': predicted_width
            })

            print(f"\n  Result:")
            print(f"    Actual FOV:       {actual_fov_h_deg:.1f} deg (config says {current_fov_h_deg:.1f} deg)")
            print(f"    Predicted width:  {predicted_width:.1f} cm (you measured {width_cm:.1f} cm)")
            error_pct = abs(predicted_width - width_cm) / width_cm * 100
            print(f"    Error:            {error_pct:.1f}%")
            print()
            print("  Enter another measurement or 'q' to finish.\n")

    except (KeyboardInterrupt, EOFError):
        pass

else:
    # Display mode: show camera feed, press SPACE to measure
    print("  Mode: DISPLAY. Press SPACE to take measurement, 'q' to finish.\n")

    try:
        while True:
            frame = get_frame()
            if frame is None:
                continue

            h, w = frame.shape[:2]

            # Draw edge markers and centre cross
            cv2.line(frame, (0, h//2), (w, h//2), (100, 100, 100), 1)
            cv2.line(frame, (w//2, 0), (w//2, h), (100, 100, 100), 1)

            # Edge markers (what defines the FOV edges)
            cv2.line(frame, (0, h//2-20), (0, h//2+20), (0, 255, 255), 3)
            cv2.line(frame, (w-1, h//2-20), (w-1, h//2+20), (0, 255, 255), 3)
            cv2.line(frame, (w//2-20, 0), (w//2+20, 0), (0, 255, 255), 3)
            cv2.line(frame, (w//2-20, h-1), (w//2+20, h-1), (0, 255, 255), 3)

            # Instructions
            cv2.putText(frame, "Hold camera above ruler. SPACE to measure.",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            cv2.putText(frame, f"Config FOV: {current_fov_h_deg:.1f}deg H, {current_fov_v_deg:.1f}deg V",
                        (10, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

            if measurements:
                last = measurements[-1]
                cv2.putText(frame, f"Last: FOV={last['actual_fov_deg']:.1f}deg (measured {last['width_cm']:.0f}cm at {last['height_cm']:.0f}cm)",
                            (10, h-20), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 1)

            cv2.imshow("FOV Calibration", frame)
            key = cv2.waitKey(1) & 0xFF

            if key == ord('q'):
                break
            elif key == ord(' '):
                # Pause display and ask for measurements
                print(f"\n  --- Measurement #{len(measurements)+1} ---")
                try:
                    h_input = input("  Camera height above ground (cm): ").strip()
                    w_input = input("  Visible ground width edge-to-edge (cm): ").strip()
                    height_cm = float(h_input)
                    width_cm = float(w_input)

                    actual_fov_h = 2 * math.atan((width_cm / 2) / height_cm)
                    actual_fov_h_deg = math.degrees(actual_fov_h)
                    predicted_width = 2 * height_cm * math.tan(current_fov_h / 2)

                    measurements.append({
                        'height_cm': height_cm,
                        'width_cm': width_cm,
                        'actual_fov_deg': actual_fov_h_deg,
                        'predicted_width': predicted_width
                    })

                    error_pct = abs(predicted_width - width_cm) / width_cm * 100
                    print(f"  Actual FOV: {actual_fov_h_deg:.1f}deg | Config: {current_fov_h_deg:.1f}deg | Error: {error_pct:.1f}%")
                    print()
                except (ValueError, EOFError):
                    print("  Skipped.\n")

    except KeyboardInterrupt:
        pass

# ==========================================
#   Summary
# ==========================================
if cap:
    cap.release()
if picam:
    picam.stop()
cv2.destroyAllWindows()

if measurements:
    avg_fov = sum(m['actual_fov_deg'] for m in measurements) / len(measurements)

    # Back-calculate what SENSOR_WIDTH_MM should be (keeping FOCAL_LENGTH_MM fixed)
    suggested_sensor_w = 2 * config.FOCAL_LENGTH_MM * math.tan(math.radians(avg_fov) / 2)

    # Or back-calculate FOCAL_LENGTH_MM (keeping SENSOR_WIDTH_MM fixed)
    suggested_focal = config.SENSOR_WIDTH_MM / (2 * math.tan(math.radians(avg_fov) / 2))

    print(f"\n{'=' * 55}")
    print(f"  CALIBRATION RESULTS ({len(measurements)} measurements)")
    print(f"{'=' * 55}")
    print(f"  Average measured FOV:  {avg_fov:.1f} degrees")
    print(f"  Config FOV:            {current_fov_h_deg:.1f} degrees")
    diff = avg_fov - current_fov_h_deg
    print(f"  Difference:            {diff:+.1f} degrees")
    print()

    for i, m in enumerate(measurements):
        print(f"  #{i+1}: height={m['height_cm']:.0f}cm  width={m['width_cm']:.0f}cm  FOV={m['actual_fov_deg']:.1f}deg")

    print()
    if abs(diff) > 2.0:
        print(f"  FOV is off by {abs(diff):.1f} degrees. Update config.py:")
        print(f"    Option A: SENSOR_WIDTH_MM = {suggested_sensor_w:.2f}  (keep focal={config.FOCAL_LENGTH_MM})")
        print(f"    Option B: FOCAL_LENGTH_MM = {suggested_focal:.2f}  (keep sensor={config.SENSOR_WIDTH_MM})")
    else:
        print(f"  FOV looks good! Within 2 degrees of config values.")
    print(f"{'=' * 55}\n")
else:
    print("\n  No measurements taken.\n")
