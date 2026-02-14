#!/usr/bin/env python3
"""
STEP 9: Resolution vs Detection vs Speed trade-off.

Tests multiple resolutions to find the best balance for the Pi.
For each resolution, runs detection on the dummy and reports:
  - FPS (how fast)
  - Detection rate (does it still find the dummy?)
  - Confidence (how sure is it?)

Lower resolution = faster but might miss detections.
This script finds the sweet spot.

Usage:
    python tests/pi_9_resolution_test.py                # live camera
    python tests/pi_9_resolution_test.py my_image.jpg   # static image
"""
import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2
import numpy as np

# Resolutions to test (width x height)
RESOLUTIONS = [
    (640, 480),
    (480, 360),
    (320, 240),
    (160, 120),
]

# How many frames to test per resolution
FRAMES_PER_TEST = 30

# ==========================================
#   Camera or static image?
# ==========================================
static_image = None
if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
    static_image = cv2.imread(sys.argv[1])
    print(f"[OK] Using static image: {sys.argv[1]}")
else:
    # Try to open camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        # Try picamera2
        try:
            from picamera2 import Picamera2
            picam = Picamera2()
            picam.configure(picam.create_preview_configuration(
                main={"size": (640, 480), "format": "RGB888"}
            ))
            picam.start()
            time.sleep(1)
            # Grab one frame as source
            frame = picam.capture_array()
            static_image = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            picam.stop()
            print(f"[OK] Grabbed frame from picamera2")
        except Exception as e:
            # No camera - create test image with dummy
            print(f"[INFO] No camera ({e}). Using generated test image.")
            static_image = np.zeros((480, 640, 3), dtype=np.uint8)
            static_image[:] = (34, 139, 34)
            if os.path.exists("dummy.png"):
                dummy = cv2.imread("dummy.png", cv2.IMREAD_UNCHANGED)
                if dummy is not None:
                    h, w = dummy.shape[:2]
                    scale = 200 / h
                    resized = cv2.resize(dummy, (int(w * scale), 200))
                    dh, dw = resized.shape[:2]
                    y_off = 480 - dh - 20
                    x_off = 320 - dw // 2
                    if resized.shape[2] == 4:
                        alpha = resized[:, :, 3] / 255.0
                        for c in range(3):
                            static_image[y_off:y_off+dh, x_off:x_off+dw, c] = (
                                (1 - alpha) * static_image[y_off:y_off+dh, x_off:x_off+dw, c] +
                                alpha * resized[:, :, c])
                    else:
                        static_image[y_off:y_off+dh, x_off:x_off+dw] = resized
    else:
        # Grab frame from OpenCV camera
        ret, frame = cap.read()
        if ret:
            static_image = frame
            print(f"[OK] Grabbed frame from camera")
        cap.release()

if static_image is None:
    print("[FAIL] No image source available")
    sys.exit(1)

source_h, source_w = static_image.shape[:2]
print(f"[OK] Source image: {source_w}x{source_h}")

# ==========================================
#   Load AI model
# ==========================================
from vision import VisionSystem
eyes = VisionSystem(camera_index=None, model_path="best.tflite")
if not eyes.using_ai:
    print("[FAIL] AI model not loaded. Is best.tflite in project root?")
    sys.exit(1)

backend = "TFLite" if eyes._use_tflite_direct else "Ultralytics"
print(f"[OK] AI Model: {backend}")

# ==========================================
#   Run tests
# ==========================================
print(f"\n{'=' * 60}")
print(f"  RESOLUTION vs DETECTION vs SPEED")
print(f"{'=' * 60}")
print(f"  Testing {len(RESOLUTIONS)} resolutions, {FRAMES_PER_TEST} frames each")
print(f"  Backend: {backend}")
print()

results = []

for res_w, res_h in RESOLUTIONS:
    # Resize source image to this resolution
    test_frame = cv2.resize(static_image, (res_w, res_h))

    # Warmup
    eyes.detect_in_image(test_frame.copy())

    # Run detection N times
    times = []
    detections = 0
    confidences = []

    for i in range(FRAMES_PER_TEST):
        frame_copy = test_frame.copy()
        t0 = time.time()
        found, x, y, conf = eyes.detect_in_image(frame_copy)
        elapsed_ms = (time.time() - t0) * 1000
        times.append(elapsed_ms)
        if found:
            detections += 1
            confidences.append(conf)

    avg_ms = sum(times) / len(times)
    fps = 1000.0 / avg_ms if avg_ms > 0 else 0
    det_rate = detections / FRAMES_PER_TEST * 100
    avg_conf = sum(confidences) / len(confidences) if confidences else 0

    results.append({
        'res': f"{res_w}x{res_h}",
        'w': res_w, 'h': res_h,
        'avg_ms': avg_ms,
        'fps': fps,
        'det_rate': det_rate,
        'avg_conf': avg_conf,
        'detections': detections,
    })

    status = "DETECTED" if detections > 0 else "MISSED"
    print(f"  {res_w}x{res_h:<6}  {avg_ms:6.1f}ms  {fps:5.1f}fps  "
          f"{det_rate:5.0f}% detected  conf={avg_conf:.2f}  {status}")

# ==========================================
#   Summary & recommendation
# ==========================================
print(f"\n{'=' * 60}")
print(f"  COMPARISON TABLE")
print(f"{'=' * 60}")
print(f"  {'Resolution':<12} {'Inference':<12} {'FPS':<8} {'Detection':<12} {'Confidence':<12} {'Verdict'}")
print(f"  {'-'*12} {'-'*12} {'-'*8} {'-'*12} {'-'*12} {'-'*10}")

best = None
for r in results:
    # Verdict logic
    if r['det_rate'] == 0:
        verdict = "NO DETECT"
    elif r['avg_ms'] > 500:
        verdict = "TOO SLOW"
    elif r['det_rate'] < 50:
        verdict = "UNRELIABLE"
    elif r['avg_ms'] > 200:
        verdict = "USABLE"
    else:
        verdict = "GOOD"

    if r['det_rate'] >= 80 and r['avg_ms'] <= 200:
        if best is None or r['fps'] > best['fps']:
            best = r

    print(f"  {r['res']:<12} {r['avg_ms']:<12.0f}ms {r['fps']:<8.1f} {r['det_rate']:<12.0f}% {r['avg_conf']:<12.2f} {verdict}")

print()

# Speed comparison
if len(results) >= 2:
    slowest = results[0]  # highest res
    fastest_detecting = None
    for r in results:
        if r['det_rate'] > 0:
            fastest_detecting = r
    if fastest_detecting and fastest_detecting != slowest:
        speedup = slowest['avg_ms'] / fastest_detecting['avg_ms']
        print(f"  Dropping from {slowest['res']} to {fastest_detecting['res']}: {speedup:.1f}x faster")

if best:
    print(f"\n  >> RECOMMENDED: {best['res']}")
    print(f"     {best['fps']:.1f} FPS, {best['det_rate']:.0f}% detection, conf={best['avg_conf']:.2f}")
    print(f"     Update vision.py camera settings if changing from 640x480:")
    print(f"       self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, {best['w']})")
    print(f"       self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, {best['h']})")
else:
    print(f"\n  >> No resolution achieved both >80% detection and <200ms.")
    print(f"     Consider: quantised model, smaller YOLO variant, or accept slower FPS.")

print(f"{'=' * 60}\n")
