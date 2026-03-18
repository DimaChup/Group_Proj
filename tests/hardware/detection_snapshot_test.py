#!/usr/bin/env python3
"""
Detection Snapshot Test — continuous detection with auto-saved annotated frames.

WHAT:    Opens the camera, runs AI detection on every frame, and saves annotated
         JPEGs (with bounding box and confidence) to a detections/ folder whenever
         a detection exceeds the confidence threshold. Prints detection info and
         periodic FPS updates to terminal. Runs headless — no display window needed.
WHY:     Provides a quick way to verify that camera + AI detection works on Pi over
         SSH without needing a display. Saved snapshots can be reviewed after the
         test to verify detection quality, bounding box accuracy, and confidence
         levels under real conditions.
WHEN:    After pushing new code/models to Pi. Before flight to verify camera sees
         the dummy. When testing detection at different distances or lighting.
WHERE:   Primarily Pi (designed for headless SSH use), but works on laptop too.
ENV:     pienv on Pi. Needs camera access (picamera2 or OpenCV camera).
MODELS:  best.tflite (any YOLOv8 TFLite model in project root).
RISK:    none — camera only, no drone commands, no MAVLink connection.

USAGE:
    python tests/hardware/detection_snapshot_test.py
    python tests/hardware/detection_snapshot_test.py --conf 0.3
    python tests/hardware/detection_snapshot_test.py --frames 100

FLAGS:
    --conf <float>    Confidence threshold for saving detections (default: 0.4).
                      Lower values catch more detections but may include false positives.
    --frames <int>    Stop after N frames (default: 0 = unlimited, run until Ctrl+C).

OUTPUT:
    - Annotated JPEG snapshots saved to detections/ folder (det_0001_0.95.jpg etc.)
    - Terminal: per-detection log (confidence, position, filename)
    - Terminal: periodic stats every 50 frames (frame count, detection count, FPS)
    - Final summary: total frames, detections, detection rate, FPS

BEST PRACTICES:
    - Point camera at the dummy before starting
    - Start with default --conf 0.4, lower to 0.25-0.3 if detections are missed
    - Use --frames 100 for quick tests, unlimited for extended monitoring
    - Review saved snapshots to check bounding box accuracy and false positives
    - Delete detections/ folder between test runs to avoid confusion

DEPENDENCIES:
    opencv-python (or opencv-python-headless), numpy, vision.py (project module)
"""
import sys
import os
import time
import signal

signal.signal(signal.SIGINT, signal.SIG_DFL)

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, project_root)

import cv2
import numpy as np
from vision import VisionSystem

# --- Args ---
conf = 0.4
max_frames = 0  # 0 = unlimited
for i, a in enumerate(sys.argv):
    if a == "--conf" and i + 1 < len(sys.argv):
        conf = float(sys.argv[i + 1])
    if a == "--frames" and i + 1 < len(sys.argv):
        max_frames = int(sys.argv[i + 1])

# --- Setup ---
save_dir = os.path.join(project_root, "detections")
os.makedirs(save_dir, exist_ok=True)

model_path = os.path.join(project_root, "best.tflite")
print(f"Model: {model_path}")
print(f"Confidence threshold: {conf}")
print(f"Saving detections to: {save_dir}/")
print()

eyes = VisionSystem(camera_index=0, model_path=model_path)
if not eyes.using_ai:
    print("[ERROR] AI model not loaded!")
    sys.exit(1)

print("[OK] Camera + AI ready. Point at target...")
print("     Ctrl+C to stop.\n")

frame_count = 0
det_count = 0
start_time = time.time()

while True:
    frame = eyes.get_frame()
    if frame is None:
        continue

    frame_count += 1
    found, x, y, c = eyes.detect_in_image(frame)

    if found and c >= conf:
        det_count += 1
        # Draw box on frame (x, y are already pixel coordinates from detect_in_image)
        box_size = 40
        cv2.rectangle(frame,
                      (int(x) - box_size, int(y) - box_size),
                      (int(x) + box_size, int(y) + box_size),
                      (0, 255, 0), 2)
        cv2.putText(frame, f"{c:.2f}", (int(x) - box_size, int(y) - box_size - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Save
        fname = f"det_{det_count:04d}_{c:.2f}.jpg"
        cv2.imwrite(os.path.join(save_dir, fname), frame)
        print(f"  [DET {det_count}] conf={c:.3f} pos=({x:.2f},{y:.2f}) -> {fname}")

    if frame_count % 50 == 0:
        elapsed = time.time() - start_time
        fps = frame_count / elapsed if elapsed > 0 else 0
        print(f"  ... frame {frame_count}, {det_count} detections, {fps:.1f} FPS")

    if max_frames > 0 and frame_count >= max_frames:
        break

elapsed = time.time() - start_time
fps = frame_count / elapsed if elapsed > 0 else 0
print(f"\nDone: {frame_count} frames, {det_count} detections ({det_count/frame_count*100:.0f}%), {fps:.1f} FPS")
print(f"Snapshots saved in: {save_dir}/")
eyes.release()
