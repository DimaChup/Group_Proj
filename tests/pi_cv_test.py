#!/usr/bin/env python3
"""
pi_cv_test.py — Synthetic Image CV Model Benchmark
===================================================
Tests how well the AI model detects the dummy at various simulated altitudes,
positions, and rotations — using the same math as the real simulator.

Uses map.jpg as background and dummy.png as the target (both in git).
Runs entirely offline — no camera, no Cube, no connection needed.

Usage:
    python tests/pi_cv_test.py                  # interactive (shows frames)
    python tests/pi_cv_test.py --headless        # terminal-only output
    python tests/pi_cv_test.py --save            # save test frames to tests/cv_frames/
    python tests/pi_cv_test.py --headless --save # both
"""

import sys
import os
import argparse
import math
import time
import numpy as np
import cv2

# Add project root to path so we can import vision, config, utils
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

import config
from utils import overlay_image_alpha


# ── Frame Generation (same math as simulation.py) ───────────────────────

def calculate_fov():
    """Camera field of view in radians."""
    return 2 * math.atan(config.SENSOR_WIDTH_MM / (2 * config.FOCAL_LENGTH_MM))

def ground_footprint(alt_m, fov_rad):
    """Width of ground visible at a given altitude, in meters."""
    return 2 * max(1.0, alt_m) * math.tan(fov_rad / 2)

def generate_synthetic_frame(map_img, dummy_img, pix_per_m,
                              dummy_x, dummy_y, drone_alt,
                              offset_x=0, offset_y=0, yaw_deg=0):
    """
    Generate a camera frame as if the drone is at (dummy_x+offset_x, dummy_y+offset_y)
    at the given altitude, looking straight down.

    Returns: (frame, expected_screen_x, expected_screen_y, dummy_h_screen)
    """
    fov = calculate_fov()
    ground_w = ground_footprint(drone_alt, fov)

    # Map pixels covered by camera
    view_w_px = int(ground_w * pix_per_m)
    view_h_px = int(view_w_px * (config.IMAGE_H / config.IMAGE_W))

    # Drone position in map pixels
    cx = dummy_x + offset_x
    cy = dummy_y + offset_y

    map_h, map_w = map_img.shape[:2]

    # Handle rotation: crop a larger patch, rotate, then extract the view
    yaw_rad = math.radians(yaw_deg)
    diag = int(math.sqrt(view_w_px**2 + view_h_px**2))

    x1 = cx - diag // 2
    y1 = cy - diag // 2
    x2 = x1 + diag
    y2 = y1 + diag

    # Padding for edges
    pad_l = max(0, -x1)
    pad_t = max(0, -y1)
    pad_r = max(0, x2 - map_w)
    pad_b = max(0, y2 - map_h)

    sx1 = x1 + pad_l
    sy1 = y1 + pad_t
    sx2 = x2 - pad_r
    sy2 = y2 - pad_b

    if sx2 > sx1 and sy2 > sy1:
        raw_crop = map_img[sy1:sy2, sx1:sx2].copy()
        if pad_l > 0 or pad_t > 0 or pad_r > 0 or pad_b > 0:
            raw_crop = cv2.copyMakeBorder(raw_crop, pad_t, pad_b, pad_l, pad_r,
                                          cv2.BORDER_CONSTANT, value=(34, 100, 34))
    else:
        raw_crop = np.full((diag, diag, 3), (34, 100, 34), dtype=np.uint8)

    # Rotate
    center = (diag // 2, diag // 2)
    M = cv2.getRotationMatrix2D(center, yaw_deg, 1.0)
    rotated = cv2.warpAffine(raw_crop, M, (diag, diag),
                              borderValue=(34, 100, 34))

    # Extract final view
    start_x = (diag - view_w_px) // 2
    start_y = (diag - view_h_px) // 2
    crop = rotated[start_y:start_y + view_h_px, start_x:start_x + view_w_px]

    # Resize to camera resolution
    frame = cv2.resize(crop, (config.IMAGE_W, config.IMAGE_H))

    # Overlay dummy at correct screen position + scale
    px_per_m_screen = config.IMAGE_W / ground_w

    # Target position on screen (accounting for drone offset and yaw)
    dx = dummy_x - cx
    dy = dummy_y - cy
    angle_rad = -yaw_rad
    dx_rot = dx * math.cos(angle_rad) - dy * math.sin(angle_rad)
    dy_rot = dx * math.sin(angle_rad) + dy * math.cos(angle_rad)
    scale = config.IMAGE_W / max(1, view_w_px)
    screen_x = int((config.IMAGE_W / 2) + (dx_rot * scale))
    screen_y = int((config.IMAGE_H / 2) + (dy_rot * scale))

    if dummy_img is not None:
        dummy_h_screen = int(config.DUMMY_HEIGHT_M * px_per_m_screen)
        if dummy_h_screen >= 3:
            overlay_image_alpha(frame, dummy_img, screen_x, screen_y,
                                0, dummy_h_screen, rotation_deg=yaw_deg)
    else:
        # Fallback: draw a red dot
        dot_rad = int(config.TARGET_REAL_RADIUS_M * px_per_m_screen)
        cv2.circle(frame, (screen_x, screen_y), max(3, dot_rad), (0, 0, 255), -1)

    dummy_h_screen = int(config.DUMMY_HEIGHT_M * px_per_m_screen)
    return frame, screen_x, screen_y, dummy_h_screen


# ── Test Runner ──────────────────────────────────────────────────────────

def run_tests(args):
    print("=" * 60)
    print("  PI CV TEST — Synthetic Image Model Benchmark")
    print("=" * 60)

    # Load assets
    map_path = os.path.join(project_root, config.MAP_FILE)
    dummy_path = os.path.join(project_root, config.DUMMY_FILE)

    map_img = cv2.imread(map_path)
    if map_img is None:
        print(f"\n[!] map.jpg not found at {map_path}")
        print("    Creating plain green background (200x200m equivalent)")
        pix_per_m = 2.0
        map_w = int(200 * pix_per_m)
        map_h = int(200 * pix_per_m)
        map_img = np.full((map_h, map_w, 3), (34, 139, 34), dtype=np.uint8)
        # Add some texture
        for _ in range(500):
            rx, ry = np.random.randint(0, map_w), np.random.randint(0, map_h)
            shade = np.random.randint(25, 50)
            cv2.circle(map_img, (rx, ry), np.random.randint(2, 8),
                       (shade, 100 + shade, shade), -1)
    else:
        map_h, map_w = map_img.shape[:2]
        pix_per_m = map_w / config.MAP_WIDTH_METERS
        print(f"[OK] Map loaded: {map_w}x{map_h} px  ({config.MAP_WIDTH_METERS}m wide)")
        print(f"     Scale: 1m = {pix_per_m:.2f} px")

    dummy_img = cv2.imread(dummy_path, cv2.IMREAD_UNCHANGED)
    if dummy_img is not None:
        dh, dw = dummy_img.shape[:2]
        channels = dummy_img.shape[2] if len(dummy_img.shape) > 2 else 1
        print(f"[OK] Dummy loaded: {dw}x{dh} px, {channels} channels")
    else:
        print(f"[!]  Dummy not found at {dummy_path} — using red dot fallback")

    # Load AI model (no camera)
    print()
    from vision import VisionSystem
    eyes = VisionSystem(camera_index=None, model_path=os.path.join(project_root, "best.tflite"))
    if not eyes.using_ai:
        print("\n[FAIL] No AI model loaded. Cannot run benchmark.")
        print("       Ensure best.tflite exists in project root.")
        return

    # Save directory
    save_dir = None
    if args.save:
        save_dir = os.path.join(script_dir, "cv_frames")
        os.makedirs(save_dir, exist_ok=True)
        print(f"\n[SAVE] Frames will be saved to: {save_dir}")

    # Place dummy near map center
    dummy_x = map_w // 2
    dummy_y = map_h // 2

    # ── Test configurations ──
    test_altitudes = [5, 10, 15, 20, 25, 30, 35, 40, 50]
    test_offsets = [
        (0, 0, "CENTER"),       # dummy centered in frame
        (20, 0, "RIGHT 20px"),  # slightly off-center
        (0, 30, "DOWN 30px"),   # off-center vertically
    ]
    test_yaws = [0, 45, 90]

    print(f"\nCamera: {config.IMAGE_W}x{config.IMAGE_H}")
    print(f"Sensor: {config.SENSOR_WIDTH_MM}mm, Focal: {config.FOCAL_LENGTH_MM}mm")
    print(f"FOV: {math.degrees(calculate_fov()):.1f} degrees")
    print(f"Dummy height: {config.DUMMY_HEIGHT_M}m")
    print()

    # ── Phase 1: Altitude sweep (centered, no yaw) ──
    print("=" * 60)
    print("  PHASE 1: Altitude Sweep (dummy centered, yaw=0)")
    print("=" * 60)
    print(f"{'Alt(m)':>7} {'Ground(m)':>9} {'Dummy(px)':>9} {'Detect':>7} "
          f"{'Conf':>6} {'Err(px)':>7} {'Time(ms)':>8}")
    print("-" * 60)

    results = []

    for alt in test_altitudes:
        ground_w = ground_footprint(alt, calculate_fov())
        dummy_h_expected = int(config.DUMMY_HEIGHT_M * (config.IMAGE_W / ground_w))

        frame, exp_x, exp_y, _ = generate_synthetic_frame(
            map_img, dummy_img, pix_per_m,
            dummy_x, dummy_y, alt
        )

        # Run detection (multiple times for timing)
        times = []
        for _ in range(3):
            test_frame = frame.copy()
            t0 = time.time()
            found, det_x, det_y, conf = eyes.detect_in_image(test_frame)
            times.append((time.time() - t0) * 1000)

        avg_ms = sum(times) / len(times)

        if found:
            err = math.sqrt((det_x - exp_x)**2 + (det_y - exp_y)**2)
            err_str = f"{err:.1f}"
            conf_str = f"{conf:.3f}"
            det_str = "YES"
        else:
            err_str = "-"
            conf_str = "-"
            det_str = "NO"

        print(f"{alt:>7.0f} {ground_w:>9.1f} {dummy_h_expected:>9d} {det_str:>7} "
              f"{conf_str:>6} {err_str:>7} {avg_ms:>8.1f}")

        results.append({
            "alt": alt, "ground_w": ground_w, "dummy_h": dummy_h_expected,
            "found": found, "conf": conf if found else 0,
            "err": err if found else -1, "ms": avg_ms,
            "label": f"alt{alt}m"
        })

        if save_dir:
            # Save the frame WITH detection overlay
            test_frame_save = frame.copy()
            eyes.detect_in_image(test_frame_save)
            info = f"Alt={alt}m  Ground={ground_w:.0f}m  Dummy={dummy_h_expected}px"
            cv2.putText(test_frame_save, info, (10, 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            cv2.imwrite(os.path.join(save_dir, f"alt_{alt:02d}m.jpg"), test_frame_save)

        if not args.headless:
            display = frame.copy()
            eyes.detect_in_image(display)
            info = f"Alt={alt}m  Dummy={dummy_h_expected}px  {det_str}"
            cv2.putText(display, info, (10, 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.imshow("CV Test", display)
            key = cv2.waitKey(500)
            if key == 27:  # ESC
                cv2.destroyAllWindows()
                return

    # ── Phase 2: Position offset tests (at typical search altitude) ──
    test_alt = config.TARGET_ALT
    print()
    print("=" * 60)
    print(f"  PHASE 2: Position Offsets (alt={test_alt}m, yaw=0)")
    print("=" * 60)
    print(f"{'Offset':>15} {'Detect':>7} {'Conf':>6} {'Err(px)':>7} {'Time(ms)':>8}")
    print("-" * 60)

    for ox, oy, label in test_offsets:
        # Convert offset from map pixels to meters for context
        ox_m = ox / pix_per_m
        oy_m = oy / pix_per_m

        frame, exp_x, exp_y, _ = generate_synthetic_frame(
            map_img, dummy_img, pix_per_m,
            dummy_x, dummy_y, test_alt,
            offset_x=int(ox * pix_per_m), offset_y=int(oy * pix_per_m)
        )

        times = []
        for _ in range(3):
            test_frame = frame.copy()
            t0 = time.time()
            found, det_x, det_y, conf = eyes.detect_in_image(test_frame)
            times.append((time.time() - t0) * 1000)
        avg_ms = sum(times) / len(times)

        if found:
            err = math.sqrt((det_x - exp_x)**2 + (det_y - exp_y)**2)
            print(f"{label:>15} {'YES':>7} {conf:>6.3f} {err:>7.1f} {avg_ms:>8.1f}")
        else:
            print(f"{label:>15} {'NO':>7} {'-':>6} {'-':>7} {avg_ms:>8.1f}")

        if save_dir:
            test_frame_save = frame.copy()
            eyes.detect_in_image(test_frame_save)
            cv2.imwrite(os.path.join(save_dir, f"offset_{label.replace(' ', '_')}.jpg"),
                        test_frame_save)

    # ── Phase 3: Rotation tests ──
    print()
    print("=" * 60)
    print(f"  PHASE 3: Yaw Rotation (alt={test_alt}m, centered)")
    print("=" * 60)
    print(f"{'Yaw(deg)':>9} {'Detect':>7} {'Conf':>6} {'Err(px)':>7} {'Time(ms)':>8}")
    print("-" * 60)

    for yaw in test_yaws:
        frame, exp_x, exp_y, _ = generate_synthetic_frame(
            map_img, dummy_img, pix_per_m,
            dummy_x, dummy_y, test_alt,
            yaw_deg=yaw
        )

        times = []
        for _ in range(3):
            test_frame = frame.copy()
            t0 = time.time()
            found, det_x, det_y, conf = eyes.detect_in_image(test_frame)
            times.append((time.time() - t0) * 1000)
        avg_ms = sum(times) / len(times)

        if found:
            err = math.sqrt((det_x - exp_x)**2 + (det_y - exp_y)**2)
            print(f"{yaw:>9} {'YES':>7} {conf:>6.3f} {err:>7.1f} {avg_ms:>8.1f}")
        else:
            print(f"{yaw:>9} {'NO':>7} {'-':>6} {'-':>7} {avg_ms:>8.1f}")

        if save_dir:
            test_frame_save = frame.copy()
            eyes.detect_in_image(test_frame_save)
            cv2.imwrite(os.path.join(save_dir, f"yaw_{yaw:03d}deg.jpg"), test_frame_save)

    # ── Phase 4: Timing benchmark (many runs at search altitude) ──
    print()
    print("=" * 60)
    print(f"  PHASE 4: Inference Timing (50 runs at {test_alt}m)")
    print("=" * 60)

    frame, _, _, _ = generate_synthetic_frame(
        map_img, dummy_img, pix_per_m,
        dummy_x, dummy_y, test_alt
    )

    timing_runs = []
    detections = 0
    for i in range(50):
        test_frame = frame.copy()
        t0 = time.time()
        found, _, _, _ = eyes.detect_in_image(test_frame)
        ms = (time.time() - t0) * 1000
        timing_runs.append(ms)
        if found:
            detections += 1

    timing_runs.sort()
    avg = sum(timing_runs) / len(timing_runs)
    p50 = timing_runs[len(timing_runs) // 2]
    p90 = timing_runs[int(len(timing_runs) * 0.9)]
    p99 = timing_runs[int(len(timing_runs) * 0.99)]
    fps = 1000.0 / avg if avg > 0 else 0

    print(f"  Runs:       50")
    print(f"  Detections: {detections}/50 ({100*detections/50:.0f}%)")
    print(f"  Avg:        {avg:.1f} ms")
    print(f"  Median:     {p50:.1f} ms")
    print(f"  P90:        {p90:.1f} ms")
    print(f"  P99:        {p99:.1f} ms")
    print(f"  Min:        {min(timing_runs):.1f} ms")
    print(f"  Max:        {max(timing_runs):.1f} ms")
    print(f"  ~FPS:       {fps:.1f}")

    # ── Summary ──
    print()
    print("=" * 60)
    print("  SUMMARY")
    print("=" * 60)

    detected_alts = [r for r in results if r["found"]]
    missed_alts = [r for r in results if not r["found"]]

    if detected_alts:
        max_det_alt = max(r["alt"] for r in detected_alts)
        avg_conf = sum(r["conf"] for r in detected_alts) / len(detected_alts)
        print(f"  Detected at {len(detected_alts)}/{len(results)} altitudes")
        print(f"  Max detection altitude: {max_det_alt}m")
        print(f"  Avg confidence: {avg_conf:.3f}")

        if max_det_alt < config.TARGET_ALT:
            print(f"\n  [!] TARGET_ALT is {config.TARGET_ALT}m but max detection is {max_det_alt}m")
            print(f"      Consider lowering TARGET_ALT in config.py")
        else:
            print(f"\n  [OK] Model detects at TARGET_ALT ({config.TARGET_ALT}m)")

        if avg > 200:
            print(f"  [!] Inference is slow ({avg:.0f}ms). Target: <200ms")
        else:
            print(f"  [OK] Inference speed: {avg:.0f}ms (target: <200ms)")
    else:
        print("  [FAIL] No detections at any altitude!")
        print("         Check model file and dummy image.")

    if missed_alts:
        missed_str = ", ".join(str(r["alt"]) + "m" for r in missed_alts)
        print(f"\n  Missed altitudes: {missed_str}")

    if not args.headless:
        print("\nPress any key to close...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    print("\nDone.")


# ── Main ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Synthetic CV model benchmark")
    parser.add_argument("--headless", action="store_true",
                        help="No GUI windows (for SSH / Pi without display)")
    parser.add_argument("--save", action="store_true",
                        help="Save test frames to tests/cv_frames/")
    args = parser.parse_args()

    if args.headless:
        os.environ["DISPLAY"] = ""

    run_tests(args)
