#!/usr/bin/env python3
"""
Blur + Altitude Detection Test — simulate detection at different altitudes and speeds.

Creates synthetic frames: dummy.png composited on map.jpg at altitude-correct size,
then applies motion blur for different drone speeds. Tests each combination with the
vision model and reports detection success/confidence.

No camera needed — runs entirely from images.

USAGE:
    python tests/laptop/blur_altitude_test.py
    python tests/laptop/blur_altitude_test.py --model cv_models/sar_v2_1088/best.tflite
    python tests/laptop/blur_altitude_test.py --backend ncnn
"""
import sys
import os
import time
import numpy as np

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, project_root)
os.chdir(project_root)

import cv2
import config
from vision import VisionSystem

# --- Parameters ---
DUMMY_HEIGHT_M = 1.8  # real dummy height in meters
EXPOSURE_MS = 8.0     # IMX296 typical exposure time (ms) — global shutter

# Altitudes to test (meters)
ALTITUDES = [15, 20, 25, 30, 40, 50, 60, 80]

# Speeds to test (m/s)
SPEEDS = [0, 2, 5, 8, 10, 15, 20]

# --- Model selection ---
MODEL_PATH = "best.tflite"
for i, arg in enumerate(sys.argv):
    if arg == "--model" and i + 1 < len(sys.argv):
        MODEL_PATH = sys.argv[i + 1]


def dummy_pixels_at_altitude(alt_m):
    """How many pixels tall the dummy appears at given altitude."""
    gsd = (config.SENSOR_WIDTH_MM * alt_m) / (config.FOCAL_LENGTH_MM * 640)
    return int(DUMMY_HEIGHT_M / gsd)


def blur_pixels_at_speed(speed_mps, alt_m):
    """How many pixels of motion blur at given speed and altitude."""
    distance_m = speed_mps * (EXPOSURE_MS / 1000.0)
    gsd = (config.SENSOR_WIDTH_MM * alt_m) / (config.FOCAL_LENGTH_MM * 640)
    return max(1, int(distance_m / gsd))


def apply_motion_blur(image, kernel_size):
    """Apply horizontal motion blur."""
    if kernel_size <= 1:
        return image
    kernel = np.zeros((kernel_size, kernel_size))
    kernel[kernel_size // 2, :] = np.ones(kernel_size) / kernel_size
    return cv2.filter2D(image, -1, kernel)


def create_test_frame(bg_img, dummy_img, alt_m, frame_size=640):
    """Create a synthetic frame with dummy at correct size for altitude."""
    # Random background crop
    h_bg, w_bg = bg_img.shape[:2]
    x = np.random.randint(0, max(1, w_bg - frame_size))
    y = np.random.randint(0, max(1, h_bg - frame_size))
    frame = bg_img[y:y+frame_size, x:x+frame_size].copy()
    if frame.shape[0] != frame_size or frame.shape[1] != frame_size:
        frame = cv2.resize(frame, (frame_size, frame_size))

    # Resize dummy to altitude-correct size
    dummy_h_px = dummy_pixels_at_altitude(alt_m)
    if dummy_h_px < 3:
        return frame  # too small to see

    h_d, w_d = dummy_img.shape[:2]
    aspect = w_d / h_d
    dummy_w_px = int(dummy_h_px * aspect)

    if dummy_h_px >= frame_size or dummy_w_px >= frame_size:
        return frame  # too large

    dummy_resized = cv2.resize(dummy_img, (dummy_w_px, dummy_h_px))

    # Place in center of frame
    cx = frame_size // 2 - dummy_w_px // 2
    cy = frame_size // 2 - dummy_h_px // 2

    # Alpha blend if BGRA
    if dummy_resized.shape[2] == 4:
        alpha = dummy_resized[:, :, 3] / 255.0
        for c in range(3):
            frame[cy:cy+dummy_h_px, cx:cx+dummy_w_px, c] = (
                alpha * dummy_resized[:, :, c] +
                (1 - alpha) * frame[cy:cy+dummy_h_px, cx:cx+dummy_w_px, c]
            )
    else:
        frame[cy:cy+dummy_h_px, cx:cx+dummy_w_px] = dummy_resized[:, :, :3]

    return frame


def main():
    print("=" * 80)
    print("  BLUR + ALTITUDE DETECTION TEST")
    print("  Simulates dummy detection at different altitudes and drone speeds")
    print("=" * 80)
    print(f"  Model:       {MODEL_PATH}")
    print(f"  Dummy:       {DUMMY_HEIGHT_M}m tall")
    print(f"  Exposure:    {EXPOSURE_MS}ms (IMX296 global shutter)")
    print(f"  Altitudes:   {ALTITUDES}")
    print(f"  Speeds:      {SPEEDS} m/s")
    print(f"  Sensor:      {config.SENSOR_WIDTH_MM}mm, focal {config.FOCAL_LENGTH_MM}mm")

    # Load images
    bg = cv2.imread(config.MAP_FILE)
    dummy = cv2.imread(config.DUMMY_FILE, cv2.IMREAD_UNCHANGED)
    if bg is None:
        print(f"\n  [!] Background not found: {config.MAP_FILE}")
        return
    if dummy is None:
        print(f"\n  [!] Dummy not found: {config.DUMMY_FILE}")
        return

    # Load model
    print(f"\n  Loading model...")
    vis = VisionSystem(camera_index=None, model_path=MODEL_PATH)
    if not vis.using_ai:
        print("  [!] Model not loaded")
        return
    print(f"  Backend: {vis.backend_name}")

    # Show dummy size at each altitude
    print(f"\n  Dummy size at each altitude:")
    for alt in ALTITUDES:
        px = dummy_pixels_at_altitude(alt)
        print(f"    {alt:3d}m → {px:3d}px tall")

    # Show blur at each speed/altitude combo
    print(f"\n  Blur (pixels) at speed × altitude:")
    header = f"  {'Alt':>5s}" + "".join(f" {s:>4d}m/s" for s in SPEEDS)
    print(header)
    for alt in ALTITUDES:
        row = f"  {alt:4d}m"
        for spd in SPEEDS:
            bp = blur_pixels_at_speed(spd, alt)
            row += f"  {bp:4d}px"
        print(row)

    # Run detection tests
    print(f"\n  Running detection tests (3 frames per combination)...")
    print(f"\n  Detection Results (confidence, 0=miss):")
    header = f"  {'Alt':>5s}" + "".join(f" {s:>6d}m/s" for s in SPEEDS)
    print(header)
    print("  " + "-" * (6 + 7 * len(SPEEDS)))

    results = []
    for alt in ALTITUDES:
        row = f"  {alt:4d}m"
        for spd in SPEEDS:
            blur_px = blur_pixels_at_speed(spd, alt)

            # Test 3 frames, take best confidence
            best_conf = 0.0
            detections = 0
            for _ in range(3):
                frame = create_test_frame(bg, dummy, alt)
                frame = apply_motion_blur(frame, blur_px)
                found, x, y, conf = vis.detect_in_image(frame)
                if found:
                    detections += 1
                    best_conf = max(best_conf, conf)

            results.append({
                'alt': alt, 'speed': spd, 'blur_px': blur_px,
                'detections': detections, 'best_conf': best_conf,
                'dummy_px': dummy_pixels_at_altitude(alt),
            })

            if detections > 0:
                row += f"  {best_conf:5.2f}✓"
            else:
                row += f"  {'miss':>6s}"
        print(row)

    # Summary
    print(f"\n  {'=' * 60}")
    print(f"  SUMMARY")
    print(f"  {'=' * 60}")

    # Find max speed at each altitude
    for alt in ALTITUDES:
        alt_results = [r for r in results if r['alt'] == alt]
        max_speed = 0
        for r in alt_results:
            if r['detections'] > 0:
                max_speed = r['speed']
        px = dummy_pixels_at_altitude(alt)
        print(f"    {alt:3d}m ({px:2d}px): detects up to {max_speed} m/s")

    # Find max altitude at each speed
    print()
    for spd in SPEEDS:
        spd_results = [r for r in results if r['speed'] == spd]
        max_alt = 0
        for r in spd_results:
            if r['detections'] > 0:
                max_alt = r['alt']
        print(f"    {spd:2d} m/s: detects up to {max_alt}m altitude")

    # Save results
    save_path = os.path.join(project_root, "pi_data", "blur_altitude_results.txt")
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    try:
        from datetime import datetime
        import socket, platform
        with open(save_path, "a") as f:
            f.write(f"\n{'=' * 80}\n")
            f.write(f"  BLUR+ALT TEST — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"  Host: {socket.gethostname()}, Model: {MODEL_PATH}, Backend: {vis.backend_name}\n")
            f.write(f"{'=' * 80}\n")
            for r in results:
                status = f"{r['best_conf']:.2f}" if r['detections'] > 0 else "MISS"
                f.write(f"  alt={r['alt']}m spd={r['speed']}m/s blur={r['blur_px']}px "
                        f"dummy={r['dummy_px']}px det={r['detections']}/3 conf={status}\n")
            f.write("\n")
        print(f"\n  Results saved to: {save_path}")
    except Exception as e:
        print(f"\n  [!] Could not save: {e}")


if __name__ == '__main__':
    main()
