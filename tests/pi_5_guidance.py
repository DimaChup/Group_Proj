#!/usr/bin/env python3
"""
STEP 5: Camera-only guidance test. No Cube, no GPS needed.

Detects the dummy and gives directional commands based on where it
appears in the frame. Carry the drone/camera around and follow the
commands to centre on the target.

This tests the same logic that the real flight code uses for centering.

Usage:
    python tests/pi_5_guidance.py             # with display
    python tests/pi_5_guidance.py --headless  # text only
"""
import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

headless = "--headless" in sys.argv

import cv2
import numpy as np

# ==========================================
#   Camera setup (same as pi_1/pi_2)
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
#   Load AI model
# ==========================================
from vision import VisionSystem
eyes = VisionSystem(camera_index=None, model_path="best.tflite")

if not eyes.using_ai:
    print("[FAIL] AI model did not load. Is best.tflite in project root?")
    sys.exit(1)

print(f"[OK] AI Model loaded")

# ==========================================
#   Guidance settings
# ==========================================
FRAME_W = 640
FRAME_H = 480
CENTRE_X = FRAME_W // 2  # 320
CENTRE_Y = FRAME_H // 2  # 240

# How close to centre counts as "centred" (pixels)
CENTRE_THRESHOLD = 50

# Bounding box size thresholds (relative to frame)
# These tell us roughly how close we are
SIZE_FAR = 0.05      # < 5% of frame = very far
SIZE_MEDIUM = 0.15   # 5-15% = getting closer
SIZE_CLOSE = 0.30    # > 30% = close enough to "land"

def get_guidance(x, y, conf, frame):
    """Given detection position, return guidance command and details."""
    dx = x - CENTRE_X  # positive = target is right
    dy = y - CENTRE_Y  # positive = target is below

    # Direction
    commands = []
    if abs(dx) > CENTRE_THRESHOLD:
        commands.append("RIGHT" if dx > 0 else "LEFT")
    if abs(dy) > CENTRE_THRESHOLD:
        commands.append("BACK" if dy > 0 else "FORWARD")

    if not commands:
        commands.append("CENTRED")

    # Estimate relative distance from bounding box size
    # detect_in_image draws a rectangle, we can estimate from pixel position
    # For now, use confidence as rough proxy (higher conf = closer usually)
    if conf > 0.8:
        distance = "CLOSE"
    elif conf > 0.6:
        distance = "MEDIUM"
    else:
        distance = "FAR"

    direction = " + ".join(commands)
    centred = "CENTRED" in commands

    return direction, distance, centred, dx, dy

# ==========================================
#   Main loop
# ==========================================
print(f"\n{'=' * 50}")
print(f"  GUIDANCE TEST")
print(f"  Carry the camera around. Follow the commands")
print(f"  to centre on the target.")
print(f"{'=' * 50}")
if headless:
    print(f"  Mode: HEADLESS (text only). Ctrl+C to quit.\n")
else:
    print(f"  Mode: DISPLAY. Press 'q' to quit.\n")

frame_count = 0
detect_count = 0

try:
    while True:
        frame = get_frame()
        if frame is None:
            continue

        frame_count += 1
        found, x, y, conf = eyes.detect_in_image(frame)

        if found:
            detect_count += 1
            direction, distance, centred, dx, dy = get_guidance(x, y, conf, frame)

            # Draw guidance on frame
            colour = (0, 255, 0) if centred else (0, 165, 255)
            cv2.line(frame, (CENTRE_X, 0), (CENTRE_X, FRAME_H), (100, 100, 100), 1)
            cv2.line(frame, (0, CENTRE_Y), (FRAME_W, CENTRE_Y), (100, 100, 100), 1)
            cv2.circle(frame, (x, y), 10, colour, -1)
            cv2.arrowedLine(frame, (CENTRE_X, CENTRE_Y), (x, y), colour, 2)

            # Command text
            cmd_text = f">> {direction} | {distance}"
            if centred:
                cmd_text = ">> CENTRED - DESCEND"

            cv2.putText(frame, cmd_text, (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, colour, 2)
            cv2.putText(frame, f"offset: dx={dx:+d} dy={dy:+d}  conf={conf:.2f}",
                        (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

            if headless:
                print(f"  {cmd_text}  (dx={dx:+d} dy={dy:+d} conf={conf:.2f})")
        else:
            cv2.putText(frame, "SEARCHING...", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

            if headless and frame_count % 30 == 0:
                print(f"  SEARCHING... ({frame_count} frames)")

        if not headless:
            cv2.imshow("Guidance Test", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break

except KeyboardInterrupt:
    print("\nStopping...")

# Cleanup
if cap:
    cap.release()
if picam:
    picam.stop()
cv2.destroyAllWindows()

print(f"\n{'=' * 50}")
print(f"  {detect_count} detections in {frame_count} frames")
print(f"{'=' * 50}\n")
