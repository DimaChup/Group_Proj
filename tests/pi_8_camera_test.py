#!/usr/bin/env python3
"""
STEP 8: Camera Settings & Detection Quality Test.

Tests how camera settings affect detection:
  - Camera FPS vs pipeline FPS (what's the bottleneck?)
  - Motion blur detection (is the image sharp enough?)
  - Different resolutions (speed vs quality trade-off)
  - Confidence under movement vs stationary

Hold the camera still pointing at the dummy, then move it around.
The script reports whether motion kills detection.

Usage:
    python tests/pi_8_camera_test.py             # with display
    python tests/pi_8_camera_test.py --headless  # text only
"""
import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
    except Exception as e:
        print(f"[FAIL] No camera: {e}")
        sys.exit(1)

print(f"[OK] Camera: {source}")

def get_frame():
    if source == "OpenCV":
        ret, frame = cap.read()
        return frame if ret else None
    else:
        frame = picam.capture_array()
        # IMX296 sensor outputs BGR despite RGB888 label — no conversion needed
        return frame

# ==========================================
#   Load AI model
# ==========================================
from vision import VisionSystem
eyes = VisionSystem(camera_index=None, model_path="best.tflite")
if not eyes.using_ai:
    print("[FAIL] AI model not loaded")
    sys.exit(1)

backend = "TFLite" if eyes._use_tflite_direct else "Ultralytics"
print(f"[OK] AI Model: {backend}")

# ==========================================
#   Blur metric
# ==========================================
def blur_score(frame):
    """Laplacian variance - higher = sharper. Below ~50 = blurry."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return cv2.Laplacian(gray, cv2.CV_64F).var()

# ==========================================
#   Test 1: Camera-only FPS (no inference)
# ==========================================
print(f"\n{'=' * 55}")
print(f"  CAMERA SETTINGS & DETECTION TEST")
print(f"{'=' * 55}")

print(f"\n  TEST 1: Camera-only FPS (no AI)")
cam_frames = 0
cam_start = time.time()
while time.time() - cam_start < 3.0:
    frame = get_frame()
    if frame is not None:
        cam_frames += 1
cam_elapsed = time.time() - cam_start
cam_fps = cam_frames / cam_elapsed
actual_res = None
frame = get_frame()
if frame is not None:
    actual_res = f"{frame.shape[1]}x{frame.shape[0]}"
print(f"    Resolution: {actual_res}")
print(f"    Camera FPS: {cam_fps:.1f}")

# ==========================================
#   Test 2: Full pipeline FPS (camera + AI)
# ==========================================
print(f"\n  TEST 2: Full pipeline FPS (camera + AI)")
pipe_frames = 0
pipe_detections = 0
pipe_start = time.time()
inference_times = []
while time.time() - pipe_start < 5.0:
    frame = get_frame()
    if frame is None:
        continue
    pipe_frames += 1
    t0 = time.time()
    found, x, y, conf = eyes.detect_in_image(frame)
    inference_times.append((time.time() - t0) * 1000)
    if found:
        pipe_detections += 1
pipe_elapsed = time.time() - pipe_start
pipe_fps = pipe_frames / pipe_elapsed
avg_inf = sum(inference_times) / len(inference_times) if inference_times else 0

print(f"    Pipeline FPS:   {pipe_fps:.1f} (camera + inference)")
print(f"    Avg inference:  {avg_inf:.0f}ms")
print(f"    Detections:     {pipe_detections}/{pipe_frames}")
if cam_fps > 0 and pipe_fps > 0:
    bottleneck = "INFERENCE" if avg_inf > (1000 / cam_fps) else "CAMERA"
    print(f"    Bottleneck:     {bottleneck}")

# ==========================================
#   Test 3: Blur & detection (10 seconds)
# ==========================================
print(f"\n  TEST 3: Blur vs Detection (10 seconds)")
print(f"    Hold camera at dummy, then MOVE it around.")
if headless:
    print(f"    Ctrl+C to skip.\n")
else:
    print(f"    Press 'q' to skip.\n")

blur_detected = []     # blur scores when detection succeeded
blur_not_detected = [] # blur scores when detection failed
sharp_confs = []       # confidence when image is sharp
blurry_confs = []      # confidence when image is blurry
BLUR_THRESHOLD = 100   # below this = blurry

test3_start = time.time()
test3_frames = 0
skip = False

try:
    while time.time() - test3_start < 10.0 and not skip:
        frame = get_frame()
        if frame is None:
            continue

        test3_frames += 1
        bs = blur_score(frame)
        found, x, y, conf = eyes.detect_in_image(frame)

        if found:
            blur_detected.append(bs)
            if bs >= BLUR_THRESHOLD:
                sharp_confs.append(conf)
            else:
                blurry_confs.append(conf)
        else:
            blur_not_detected.append(bs)

        if not headless:
            # Draw info
            colour = (0, 255, 0) if found else (0, 0, 255)
            sharp_text = "SHARP" if bs >= BLUR_THRESHOLD else "BLURRY"
            cv2.putText(frame, f"Blur: {bs:.0f} ({sharp_text})", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, colour, 2)
            if found:
                cv2.putText(frame, f"DETECTED conf={conf:.2f}", (10, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(frame, f"Pipeline FPS: {pipe_fps:.1f}", (10, 90),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
            cv2.imshow("Camera Test", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                skip = True
        else:
            if test3_frames % 30 == 0:
                status = f"DETECTED conf={conf:.2f}" if found else "no detection"
                sharp_text = "SHARP" if bs >= BLUR_THRESHOLD else "BLURRY"
                print(f"    [{test3_frames}] blur={bs:.0f} ({sharp_text}) {status}")

except KeyboardInterrupt:
    pass

# ==========================================
#   Results
# ==========================================
if cap:
    cap.release()
if picam:
    picam.stop()
cv2.destroyAllWindows()

print(f"\n{'=' * 55}")
print(f"  RESULTS")
print(f"{'=' * 55}")

print(f"\n  SPEED:")
print(f"    Camera FPS:    {cam_fps:.1f}")
print(f"    Pipeline FPS:  {pipe_fps:.1f}")
print(f"    Inference:     {avg_inf:.0f}ms avg")
if avg_inf > 200:
    print(f"    >> SLOW - consider lower resolution or headless mode")
elif avg_inf > 100:
    print(f"    >> OK for flight")
else:
    print(f"    >> FAST")

total_det = len(blur_detected)
total_miss = len(blur_not_detected)
total = total_det + total_miss

if total > 0:
    print(f"\n  DETECTION:")
    print(f"    Detected:    {total_det}/{total} frames ({total_det/total*100:.0f}%)")

    if blur_detected:
        avg_blur_det = sum(blur_detected) / len(blur_detected)
        print(f"    Avg blur (detected):     {avg_blur_det:.0f}")
    if blur_not_detected:
        avg_blur_miss = sum(blur_not_detected) / len(blur_not_detected)
        print(f"    Avg blur (not detected): {avg_blur_miss:.0f}")

    print(f"\n  BLUR vs DETECTION:")
    print(f"    Blur threshold: {BLUR_THRESHOLD} (below = blurry)")

    if sharp_confs:
        print(f"    Sharp frames:  {len(sharp_confs)} detections, avg conf={sum(sharp_confs)/len(sharp_confs):.2f}")
    if blurry_confs:
        print(f"    Blurry frames: {len(blurry_confs)} detections, avg conf={sum(blurry_confs)/len(blurry_confs):.2f}")

    if blur_detected and blur_not_detected:
        avg_det = sum(blur_detected) / len(blur_detected)
        avg_miss = sum(blur_not_detected) / len(blur_not_detected)
        if avg_miss < avg_det * 0.5:
            print(f"\n    >> Motion blur IS hurting detection")
            print(f"    >> Consider: faster shutter speed, global shutter camera, or slower flight speed")
        else:
            print(f"\n    >> Motion blur does NOT significantly affect detection")
    elif not blur_not_detected:
        print(f"\n    >> Detection worked on all frames - no blur issues")

print(f"\n  WHAT TO DO WITH THESE NUMBERS:")
print(f"    - Pipeline FPS > 5:  OK for search at normal speed")
print(f"    - Pipeline FPS 2-5:  OK but may need slower search speed")
print(f"    - Pipeline FPS < 2:  Too slow, try lower resolution")
print(f"    - If blur kills detection: use global shutter or fly slower")
print(f"{'=' * 55}\n")
