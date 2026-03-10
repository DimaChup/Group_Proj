#!/usr/bin/env python3
"""
FOV Calibration — measure real camera field of view.

Hold camera at a known height above a ruler/tape measure on the floor.
The script shows what the camera sees and calculates the real FOV,
then tells you what to put in config.py.

This is CRITICAL for accurate pixel→GPS conversion. If SENSOR_WIDTH_MM
or FOCAL_LENGTH_MM are wrong, the drone will over/undershoot the target.

The math:
    GSD = (SENSOR_WIDTH_MM * altitude) / (FOCAL_LENGTH_MM * IMAGE_W)
    FOV_width = GSD * IMAGE_W = (SENSOR_WIDTH_MM * altitude) / FOCAL_LENGTH_MM

So if you measure the actual width visible at a known height:
    FOCAL_LENGTH_MM = (SENSOR_WIDTH_MM * height_mm) / measured_width_mm

Steps:
    1. Place a ruler/tape measure flat on the floor
    2. Hold camera pointing straight down at a KNOWN height (e.g., 50cm, 100cm)
    3. Note how many cm of the ruler are visible edge-to-edge in the frame
    4. Enter those values when prompted

Usage:
    python tests2/fov_calibrate.py                # with display
    python tests2/fov_calibrate.py --headless     # terminal only
"""
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2
import numpy as np
from vision import VisionSystem
import config

HEADLESS = "--headless" in sys.argv

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model_path = os.path.join(project_root, "best.tflite")


def main():
    print()
    print("=" * 60)
    print("   FOV CALIBRATION — Camera to GPS accuracy")
    print("=" * 60)
    print()
    print("  Current config.py values:")
    print(f"    SENSOR_WIDTH_MM  = {config.SENSOR_WIDTH_MM}")
    print(f"    FOCAL_LENGTH_MM  = {config.FOCAL_LENGTH_MM}")
    print(f"    IMAGE_W          = {config.IMAGE_W}")
    print(f"    IMAGE_H          = {config.IMAGE_H}")

    # Calculate current FOV at various altitudes
    print(f"\n  Current FOV predictions:")
    print(f"  {'Altitude':<12} {'FOV Width':<14} {'FOV Height':<14} {'GSD':<14}")
    print(f"  {'-'*54}")
    for alt in [0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 30.0]:
        gsd = (config.SENSOR_WIDTH_MM * alt) / (config.FOCAL_LENGTH_MM * config.IMAGE_W)
        fov_w = gsd * config.IMAGE_W
        fov_h = gsd * config.IMAGE_H
        print(f"  {alt:<12.1f} {fov_w:<14.2f}m {fov_h:<14.2f}m {gsd:<14.4f} m/px")

    print(f"\n  CALIBRATION PROCEDURE:")
    print(f"  1. Place a ruler/tape measure on the floor")
    print(f"  2. Hold camera pointing straight DOWN at a known height")
    print(f"  3. Look at the live feed — note how wide the view is")
    print(f"  4. Press 'c' to capture and enter measurements")
    print(f"  5. Or press 'q' to skip to manual entry")
    print()

    eyes = VisionSystem(camera_index=0, model_path="__none__")

    if not HEADLESS:
        cv2.namedWindow("FOV Calibration", cv2.WINDOW_NORMAL)

    captured = False
    frame = None

    try:
        while not HEADLESS:
            frame = eyes.get_frame()
            if frame is None:
                time.sleep(0.05)
                continue

            display = frame.copy()
            h, w = display.shape[:2]

            # Draw crosshair and edge markers
            cv2.line(display, (w // 2, 0), (w // 2, h), (0, 255, 255), 1)
            cv2.line(display, (0, h // 2), (w, h // 2), (0, 255, 255), 1)

            # Edge markers (for measuring width)
            cv2.line(display, (0, h // 2 - 20), (0, h // 2 + 20), (0, 0, 255), 3)
            cv2.line(display, (w - 1, h // 2 - 20), (w - 1, h // 2 + 20), (0, 0, 255), 3)

            cv2.putText(display, "Hold camera over ruler, pointing DOWN",
                        (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            cv2.putText(display, "'c' capture  |  'q' manual entry",
                        (10, h - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

            cv2.imshow("FOV Calibration", display)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('c'):
                captured = True
                cv2.imwrite("fov_capture.jpg", frame)
                print("  Frame captured (fov_capture.jpg)")
                break
            elif key == ord('q') or key == 27:
                break

    except KeyboardInterrupt:
        pass

    if not HEADLESS:
        cv2.destroyAllWindows()
    eyes.release()

    # ── Multi-height measurement ──
    print()
    print("  MULTI-HEIGHT CALIBRATION")
    print("  Measure at 2-3 different heights to verify consistency.")
    print("  SENSOR_WIDTH and FOCAL_LENGTH are FIXED camera properties —")
    print("  they should give the same result at any height.")
    print()
    print("  How to measure:")
    print("    1. Place tape measure / ruler flat on floor")
    print("    2. Hold camera pointing STRAIGHT DOWN at known height")
    print("    3. Read how many cm of ruler are visible left-to-right edge")
    print("    4. Enter height and visible width below")
    print("    5. Repeat at a different height for verification")
    print("    6. Press Enter with empty height when done")
    print()

    measurements = []
    focal_estimates = []

    try:
        while True:
            h_input = input(f"  Measurement {len(measurements)+1} — Camera height (cm) [Enter to finish]: ").strip()
            if not h_input:
                break
            w_input = input(f"  Visible ruler width edge-to-edge (cm): ").strip()
            if not w_input:
                break

            h_cm = float(h_input)
            w_cm = float(w_input)
            h_mm = h_cm * 10
            w_mm = w_cm * 10

            # FOCAL_LENGTH_MM = (SENSOR_WIDTH_MM * height_mm) / visible_width_mm
            focal = (config.SENSOR_WIDTH_MM * h_mm) / w_mm
            focal_estimates.append(focal)
            measurements.append((h_cm, w_cm, focal))

            print(f"    -> Focal length estimate: {focal:.2f} mm")
            print()

    except (ValueError, KeyboardInterrupt):
        print()

    if not measurements:
        print(f"  No measurements entered.")
        print(f"  To calibrate: hold camera over ruler, measure visible width.")
        print()
        return

    # ── Results ──
    avg_focal = np.mean(focal_estimates)
    std_focal = np.std(focal_estimates) if len(focal_estimates) > 1 else 0

    print(f"\n  {'='*60}")
    print(f"  CALIBRATION RESULTS")
    print(f"  {'='*60}")

    print(f"\n  Measurements:")
    print(f"  {'Height(cm)':<12} {'Width(cm)':<12} {'Focal(mm)':<12}")
    print(f"  {'-'*36}")
    for h_cm, w_cm, focal in measurements:
        print(f"  {h_cm:<12.1f} {w_cm:<12.1f} {focal:<12.2f}")

    if len(measurements) > 1:
        print(f"\n  Consistency check:")
        print(f"    Average focal length: {avg_focal:.2f} mm")
        print(f"    Std deviation:        {std_focal:.3f} mm")
        spread = max(focal_estimates) - min(focal_estimates)
        print(f"    Spread:               {spread:.3f} mm")
        if spread < 0.3:
            print(f"    Excellent! Measurements are very consistent.")
        elif spread < 1.0:
            print(f"    Good. Minor variation (measurement precision).")
        else:
            print(f"    High variation — camera may not have been straight down,")
            print(f"    or ruler wasn't at exact edge of frame.")

    # Compare with current config
    current_focal = config.FOCAL_LENGTH_MM
    error_pct = abs(avg_focal - current_focal) / avg_focal * 100

    print(f"\n  Current config.py:  FOCAL_LENGTH_MM = {current_focal}")
    print(f"  Calibrated value:   FOCAL_LENGTH_MM = {avg_focal:.2f}")
    print(f"  Difference:         {error_pct:.1f}%")

    # Impact at flight altitudes
    print(f"\n  What this means in flight:")
    print(f"  {'Altitude':<10} {'Current FOV':<15} {'Real FOV':<15} {'Position Error':<15}")
    print(f"  {'-'*55}")
    for alt in [10.0, 15.0, 20.0, 30.0]:
        curr_fov = (config.SENSOR_WIDTH_MM * alt) / current_focal
        real_fov = (config.SENSOR_WIDTH_MM * alt) / avg_focal
        # Max position error = half the FOV difference
        pos_err = abs(curr_fov - real_fov) / 2
        print(f"  {alt:<10.0f} {curr_fov:<15.1f}m {real_fov:<15.1f}m +/- {pos_err:<10.1f}m")

    if error_pct > 10:
        print(f"\n  !!! {error_pct:.0f}% error is SIGNIFICANT !!!")
        print(f"  UPDATE config.py:")
        print(f"    FOCAL_LENGTH_MM = {avg_focal:.2f}")
        print(f"  Without this fix, centering will be off by metres.")
    elif error_pct > 5:
        print(f"\n  {error_pct:.0f}% error — worth updating config.py:")
        print(f"    FOCAL_LENGTH_MM = {avg_focal:.2f}")
    else:
        print(f"\n  Current config values are accurate. No change needed.")

    # ── Also check blur from camera ──
    print(f"\n  {'='*55}")
    print(f"  BLUR QUICK CHECK")
    print(f"  {'='*55}")
    print(f"  To test motion blur, run:")
    print(f"    python tests2/cv_benchmark.py --blur")
    print(f"  This simulates blur at different drone speeds.")
    print()


if __name__ == "__main__":
    main()
