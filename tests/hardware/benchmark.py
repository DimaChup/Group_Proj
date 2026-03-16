#!/usr/bin/env python3
"""
STEP 3: Benchmark and compare backends.
Runs the SAME test image through detection and reports results.
Run on Windows (Ultralytics) and Pi/Docker (TFLite) - results should match.

Usage: python tests/hardware/benchmark.py
       python tests/hardware/benchmark.py my_image.jpg
"""
import sys
import os
import time
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, project_root)
os.chdir(project_root)

import cv2
import numpy as np

def create_test_image():
    """Create a test scene with the dummy on a green background."""
    bg = np.zeros((480, 640, 3), dtype=np.uint8)
    bg[:] = (34, 139, 34)

    if os.path.exists("dummy.png"):
        dummy = cv2.imread("dummy.png", cv2.IMREAD_UNCHANGED)
        if dummy is not None:
            h, w = dummy.shape[:2]
            scale = 180 / h
            resized = cv2.resize(dummy, (int(w * scale), 180))
            dh, dw = resized.shape[:2]
            y_off = 480 - dh - 20
            x_off = 320 - dw // 2

            if resized.shape[2] == 4:
                alpha = resized[:, :, 3] / 255.0
                for c in range(3):
                    bg[y_off:y_off+dh, x_off:x_off+dw, c] = (
                        (1 - alpha) * bg[y_off:y_off+dh, x_off:x_off+dw, c] +
                        alpha * resized[:, :, c]
                    )
            else:
                bg[y_off:y_off+dh, x_off:x_off+dw] = resized
            return bg, "generated (dummy on green)"
    return bg, "plain green (no dummy.png)"

def main():
    print("=" * 55)
    print("         CV BENCHMARK - Backend Comparison")
    print("=" * 55)

    # Load model
    from vision import VisionSystem
    eyes = VisionSystem(camera_index=None, model_path="best.tflite")
    if not eyes.using_ai:
        print("[FAIL] Model not loaded")
        return

    backend = "TFLite" if eyes._use_tflite_direct else "Ultralytics"
    print(f"\n  Backend: {backend}")

    # Get test image
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        frame = cv2.imread(sys.argv[1])
        src = sys.argv[1]
    else:
        frame, src = create_test_image()
    print(f"  Image:   {src} ({frame.shape[1]}x{frame.shape[0]})")

    # Warmup
    eyes.detect_in_image(frame.copy())

    # Benchmark: 50 runs
    N = 50
    times = []
    results = []
    print(f"\n  Running {N} inferences...")

    for i in range(N):
        test_frame = frame.copy()
        start = time.time()
        found, x, y, conf = eyes.detect_in_image(test_frame)
        elapsed = (time.time() - start) * 1000
        times.append(elapsed)
        results.append((found, x, y, conf))

    # Stats
    avg = sum(times) / len(times)
    fastest = min(times)
    slowest = max(times)
    detections = sum(1 for r in results if r[0])
    fps = 1000.0 / avg if avg > 0 else 0

    print(f"\n{'─' * 55}")
    print(f"  RESULTS ({backend})")
    print(f"{'─' * 55}")
    print(f"  Avg inference:  {avg:.1f}ms")
    print(f"  Fastest:        {fastest:.1f}ms")
    print(f"  Slowest:        {slowest:.1f}ms")
    print(f"  Effective FPS:  {fps:.1f}")
    print(f"  Detections:     {detections}/{N}")

    if detections > 0:
        # Get most common result
        det_results = [r for r in results if r[0]]
        avg_x = sum(r[1] for r in det_results) / len(det_results)
        avg_y = sum(r[2] for r in det_results) / len(det_results)
        avg_conf = sum(r[3] for r in det_results) / len(det_results)
        print(f"  Avg position:   ({avg_x:.0f}, {avg_y:.0f})")
        print(f"  Avg confidence: {avg_conf:.3f}")

    # Verdict
    print(f"\n  VERDICT:")
    if avg < 100:
        print(f"  Speed:     GREAT ({avg:.0f}ms)")
    elif avg < 200:
        print(f"  Speed:     OK ({avg:.0f}ms) - usable in flight")
    else:
        print(f"  Speed:     SLOW ({avg:.0f}ms) - may need lower resolution")

    if detections == N:
        print(f"  Detection: PERFECT ({detections}/{N})")
    elif detections > N * 0.8:
        print(f"  Detection: GOOD ({detections}/{N})")
    elif detections > 0:
        print(f"  Detection: WEAK ({detections}/{N}) - check model/image")
    else:
        print(f"  Detection: NONE - model may not detect this image")

    print(f"\n  ** Save this output and compare Windows vs Pi **")
    print(f"  ** Position and confidence should be similar on both **")
    print()

if __name__ == "__main__":
    main()
