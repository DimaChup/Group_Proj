#!/usr/bin/env python3
"""
STEP 2: Camera + AI detection. Gets frames and runs TFLite detection.
This is the full CV pipeline on Pi - camera -> model -> result.

Usage:
    python tests/pi_2_detect.py             # with display (screen connected)
    python tests/pi_2_detect.py --headless  # no display (SSH / no screen)
"""
import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

headless = "--headless" in sys.argv

import cv2
import numpy as np

# ==========================================
#   STEP A: Open camera (same logic as pi_1)
# ==========================================
cap = None
picam = None
source = None

# Try OpenCV
cap = cv2.VideoCapture(0)
if cap.isOpened():
    ret, _ = cap.read()
    if ret:
        source = "OpenCV"
        print(f"[OK] Camera: OpenCV")
    else:
        cap.release()
        cap = None

# Try picamera2
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
        # picamera2 gives RGB, detection expects BGR
        return cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

# ==========================================
#   STEP B: Load AI model (from vision.py)
# ==========================================
from vision import VisionSystem
eyes = VisionSystem(camera_index=None, model_path="best.tflite")

if not eyes.using_ai:
    print("[FAIL] AI model did not load. Is best.tflite in project root?")
    sys.exit(1)

backend = "TFLite" if eyes._use_tflite_direct else "Ultralytics"
print(f"[OK] AI Model: {backend}")

# ==========================================
#   STEP C: Live detection loop
# ==========================================
if headless:
    print(f"\nRunning in HEADLESS mode (no display). Press Ctrl+C to quit.\n")
else:
    print(f"\nRunning live detection with display. Press 'q' to quit.\n")

frame_count = 0
detect_count = 0
total_ms = 0

try:
    while True:
        frame = get_frame()
        if frame is None:
            continue

        frame_count += 1

        # Run detection
        start = time.time()
        found, x, y, conf = eyes.detect_in_image(frame)
        elapsed_ms = (time.time() - start) * 1000
        total_ms += elapsed_ms

        if found:
            detect_count += 1

        # Display info
        avg_ms = total_ms / frame_count
        fps = 1000.0 / avg_ms if avg_ms > 0 else 0
        cv2.putText(frame, f"{backend} | {elapsed_ms:.0f}ms | {fps:.1f}fps",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        cv2.putText(frame, f"Detections: {detect_count}/{frame_count}",
                    (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

        if found:
            cv2.putText(frame, f"TARGET ({conf:.2f}) at ({x},{y})",
                        (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        if headless:
            # No display - print status + terminal beep on detection
            if found:
                print(f"\a  [{frame_count:4d}] DETECTED  conf={conf:.2f}  pos=({x},{y})  {elapsed_ms:.0f}ms")
            elif frame_count % 30 == 0:
                print(f"  [{frame_count:4d}] scanning... {elapsed_ms:.0f}ms  ({detect_count} detections so far)")
        else:
            cv2.imshow("Pi Detection Test", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                cv2.imwrite("pi_detect_frame.jpg", frame)
                print(f"  Saved: pi_detect_frame.jpg (found={found}, conf={conf:.2f})")

except KeyboardInterrupt:
    print("\nStopping...")

# Cleanup
if cap:
    cap.release()
if picam:
    picam.stop()
cv2.destroyAllWindows()

# Summary
avg_ms = total_ms / max(1, frame_count)
print(f"\n{'=' * 45}")
print(f"  RESULTS")
print(f"{'=' * 45}")
print(f"  Backend:    {backend}")
print(f"  Frames:     {frame_count}")
print(f"  Detections: {detect_count}")
print(f"  Avg time:   {avg_ms:.0f}ms per frame")
print(f"  Avg FPS:    {1000/avg_ms:.1f}" if avg_ms > 0 else "  Avg FPS:    N/A")
if avg_ms > 200:
    print(f"  WARNING:    {avg_ms:.0f}ms is slow for flight. Consider lower resolution.")
print()
