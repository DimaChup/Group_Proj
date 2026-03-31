#!/usr/bin/env python3
"""
GPS Estimate Calibration — calibrate focal length + yaw for accurate target position estimation.

WHAT:    Place a target at known distances, compare estimated vs actual offset.
         Averages 10+ frames per measurement. Outputs corrected FOCAL_LENGTH_MM.
WHY:     GPS estimation accuracy depends on focal length calibration.
         10% focal length error = 3m GPS error at 30m altitude.
WHEN:    Before any flight that uses GPS estimation (passive_watch, main.py).
WHERE:   Indoors or outdoors. Needs camera + mavproxy (for altitude/yaw).
ENV:     Pi venv with vision.py dependencies.
RISK:    ZERO commands sent. Read-only telemetry.

USAGE:
    python tests/calibration/gps_estimate_calibrate.py
    python tests/calibration/gps_estimate_calibrate.py --no-mavlink   # use manual altitude input
    python tests/calibration/gps_estimate_calibrate.py --model cv_models/human.tflite

PROCEDURE:
    1. Hold camera at known height (e.g. 1.5m) pointing DOWN at floor
    2. Place target at known distance from directly below camera
    3. Enter height and distance when prompted
    4. Script captures 10 frames, averages detection position
    5. Computes focal length correction
    6. Repeat 3-4 times at different distances
    7. Ctrl+C for summary with corrected FOCAL_LENGTH_MM
"""
import sys
import os
import time
import math
import threading

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import cv2
import numpy as np
import config
from vision import VisionSystem

# ── GPS telemetry (read-only) ──
gps_data = {"lat": 0.0, "lon": 0.0, "alt": 0.0, "yaw": 0.0, "sats": 0}

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
            elif mtype == 'ATTITUDE':
                gps_data["yaw"] = msg.yaw * 57.2958
            elif mtype == 'GPS_RAW_INT':
                gps_data["sats"] = msg.satellites_visible
        except Exception:
            time.sleep(0.1)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Calibrate GPS estimation (focal length)")
    parser.add_argument('--no-mavlink', action='store_true')
    parser.add_argument('--model', default='best.tflite')
    parser.add_argument('--conf', type=float, default=0.2)
    parser.add_argument('--frames', type=int, default=10, help='Frames to average per measurement')
    args = parser.parse_args()

    print("=" * 60)
    print("  GPS ESTIMATE CALIBRATION")
    print("  Calibrate focal length for accurate target GPS estimation")
    print("  ZERO commands sent. Safe to run anytime.")
    print("=" * 60)

    # Current config
    f_px = config.FOCAL_LENGTH_MM * config.IMAGE_W / config.SENSOR_WIDTH_MM
    print(f"\n  Current config:")
    print(f"    FOCAL_LENGTH_MM = {config.FOCAL_LENGTH_MM}")
    print(f"    SENSOR_WIDTH_MM = {config.SENSOR_WIDTH_MM}")
    print(f"    IMAGE: {config.IMAGE_W}x{config.IMAGE_H}")
    print(f"    Focal length (px): {f_px:.1f}")

    # Connect mavlink
    mav = None
    if not args.no_mavlink:
        try:
            from pymavlink import mavutil
            print(f"\n[MAV] Connecting...")
            mav = mavutil.mavlink_connection('udpin:0.0.0.0:14550')
            msg = mav.recv_match(type='HEARTBEAT', blocking=True, timeout=5)
            if msg:
                print("[MAV] Connected (read-only)")
                threading.Thread(target=mavlink_reader, args=(mav,), daemon=True).start()
                time.sleep(1)
            else:
                print("[MAV] No heartbeat — use --no-mavlink and enter altitude manually")
                mav = None
        except Exception as e:
            print(f"[MAV] Failed: {e}")
            mav = None

    # Open camera + AI
    print(f"\n[CAM] Opening camera...")
    eyes = VisionSystem(camera_index=0, model_path=args.model)
    if not eyes.using_ai:
        print("[ERROR] AI model not loaded!")
        return
    print(f"[CAM] Ready. Backend: {eyes.backend_name}")

    print("\n" + "-" * 60)
    print("  PROCEDURE:")
    print("  1. Hold camera pointing DOWN at a target on the floor")
    print("  2. Measure camera HEIGHT above floor (meters)")
    print("  3. Measure target OFFSET from directly below camera (meters)")
    print("     (0 = directly below, 0.5 = half meter to the side, etc.)")
    print("  4. Script detects target, computes focal length correction")
    print("  5. Repeat 3-4 times. Ctrl+C for summary.")
    print("-" * 60)

    measurements = []
    measurement_num = 0

    try:
        while True:
            measurement_num += 1
            print(f"\n{'='*40}")
            print(f"  MEASUREMENT {measurement_num}")
            print(f"{'='*40}")

            # Get altitude
            if mav and gps_data["alt"] > 0.1:
                alt_m = gps_data["alt"]
                print(f"  Altitude from Cube: {alt_m:.2f}m")
                use_cube = input(f"  Use {alt_m:.2f}m? (Y/n or enter manual height): ").strip()
                if use_cube.lower() == 'n' or (use_cube and use_cube[0].isdigit()):
                    try:
                        alt_m = float(use_cube) if use_cube[0].isdigit() else float(input("  Enter height (m): "))
                    except ValueError:
                        alt_m = float(input("  Enter height (m): "))
            else:
                while True:
                    try:
                        alt_m = float(input("  Enter camera height above floor (m): "))
                        if alt_m > 0:
                            break
                    except ValueError:
                        pass

            # Get actual offset distance
            while True:
                try:
                    actual_dist = float(input("  Enter target distance from below camera (m): "))
                    if actual_dist >= 0:
                        break
                except ValueError:
                    pass

            if actual_dist == 0:
                print("  Target directly below — will measure center accuracy only")

            input("  Point camera at target. Press ENTER to capture...")

            # Capture frames
            detections = []
            print(f"  Capturing {args.frames} frames: ", end="", flush=True)

            for i in range(args.frames):
                frame = eyes.get_frame()
                if frame is None:
                    print("x", end="", flush=True)
                    time.sleep(0.1)
                    continue

                h, w = frame.shape[:2]
                found, x, y, conf = eyes.detect_in_image(frame)

                if found and conf >= args.conf:
                    # x, y are pixel coords from detect_in_image
                    # Normalise to 0-1
                    norm_x = x / w
                    norm_y = y / h
                    detections.append((norm_x, norm_y, conf))
                    print(".", end="", flush=True)
                else:
                    print("x", end="", flush=True)
                time.sleep(0.1)

            print()

            if len(detections) < 3:
                print(f"  [FAIL] Only {len(detections)} detections. Need at least 3. Try again.")
                continue

            # Average detections
            avg_x = sum(d[0] for d in detections) / len(detections)
            avg_y = sum(d[1] for d in detections) / len(detections)
            avg_conf = sum(d[2] for d in detections) / len(detections)

            # Spread (consistency check)
            spread_x = max(d[0] for d in detections) - min(d[0] for d in detections)
            spread_y = max(d[1] for d in detections) - min(d[1] for d in detections)
            spread_px = math.sqrt((spread_x * config.IMAGE_W)**2 + (spread_y * config.IMAGE_H)**2)

            print(f"  Detections: {len(detections)}/{args.frames}")
            print(f"  Avg confidence: {avg_conf:.3f}")
            print(f"  Avg position: ({avg_x:.4f}, {avg_y:.4f})")
            print(f"  Spread: {spread_px:.1f}px (< 20px is good)")

            # Pixel distance from center
            dx_px = (avg_x - 0.5) * config.IMAGE_W
            dy_px = (avg_y - 0.5) * config.IMAGE_H
            pixel_dist = math.sqrt(dx_px**2 + dy_px**2)

            # Current estimate of distance
            est_dist = pixel_dist * alt_m / f_px
            print(f"\n  Pixel offset from center: {pixel_dist:.1f}px")
            print(f"  Estimated distance: {est_dist:.3f}m")
            print(f"  Actual distance:    {actual_dist:.3f}m")

            if actual_dist > 0.05:  # Skip if target is dead center
                error = est_dist - actual_dist
                error_pct = 100 * error / actual_dist
                print(f"  Error: {error:.3f}m ({error_pct:+.1f}%)")

                # Corrected focal length
                f_px_corrected = pixel_dist * alt_m / actual_dist
                focal_mm_corrected = f_px_corrected * config.SENSOR_WIDTH_MM / config.IMAGE_W

                print(f"\n  Focal length correction:")
                print(f"    Current:   {config.FOCAL_LENGTH_MM:.2f}mm ({f_px:.1f}px)")
                print(f"    Corrected: {focal_mm_corrected:.2f}mm ({f_px_corrected:.1f}px)")

                measurements.append({
                    "actual_m": actual_dist,
                    "estimated_m": est_dist,
                    "error_m": error,
                    "focal_mm": focal_mm_corrected,
                    "alt_m": alt_m,
                    "pixel_dist": pixel_dist,
                    "n_detections": len(detections),
                    "confidence": avg_conf,
                    "spread_px": spread_px,
                })
            else:
                print(f"  Target at center — pixel offset: {pixel_dist:.1f}px (should be < 30)")

    except KeyboardInterrupt:
        pass

    # ── Summary ──
    if not measurements:
        print("\n  No measurements taken.")
        eyes.release()
        return

    print("\n\n" + "=" * 60)
    print("  CALIBRATION SUMMARY")
    print("=" * 60)

    for i, m in enumerate(measurements, 1):
        print(f"\n  #{i}: actual={m['actual_m']:.2f}m  est={m['estimated_m']:.2f}m  "
              f"err={m['error_m']:+.3f}m  focal={m['focal_mm']:.2f}mm  "
              f"conf={m['confidence']:.2f}  spread={m['spread_px']:.0f}px")

    # Weighted average (weight by confidence and inverse spread)
    total_weight = 0
    weighted_focal = 0
    for m in measurements:
        weight = m['confidence'] / max(1, m['spread_px'])
        weighted_focal += m['focal_mm'] * weight
        total_weight += weight

    avg_focal = weighted_focal / total_weight if total_weight > 0 else config.FOCAL_LENGTH_MM

    print(f"\n  {'='*40}")
    print(f"  RESULT: FOCAL_LENGTH_MM = {avg_focal:.2f}")
    print(f"  {'='*40}")
    print(f"  (was {config.FOCAL_LENGTH_MM:.2f}, change: {avg_focal - config.FOCAL_LENGTH_MM:+.2f}mm)")
    print(f"\n  Update config.py:")
    print(f"    FOCAL_LENGTH_MM = {avg_focal:.2f}  # calibrated {time.strftime('%Y-%m-%d')}")

    # Expected accuracy at different altitudes
    print(f"\n  Expected accuracy with new calibration:")
    for alt in [10, 20, 30, 50]:
        ground_w = alt * config.SENSOR_WIDTH_MM / avg_focal
        pixel_error_1m = avg_focal * config.IMAGE_W / (config.SENSOR_WIDTH_MM * alt)
        print(f"    {alt}m alt: ground {ground_w:.1f}m wide, 1px = {alt/(avg_focal*config.IMAGE_W/config.SENSOR_WIDTH_MM):.3f}m")

    eyes.release()
    print("\n  Done!")


if __name__ == "__main__":
    main()
