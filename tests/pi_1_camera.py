#!/usr/bin/env python3
"""
STEP 1: Just get camera frames on Pi. Nothing else.
Try OpenCV first, fall back to picamera2 if needed.

Usage: python tests/pi_1_camera.py
"""
import sys
import time

# --- Try OpenCV first (works on laptop AND might work on Pi) ---
cap = None
source = None

try:
    import cv2
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            source = "OpenCV"
            print(f"[OK] OpenCV camera works: {frame.shape[1]}x{frame.shape[0]}")
        else:
            cap.release()
            cap = None
    else:
        cap = None
except Exception as e:
    print(f"[--] OpenCV failed: {e}")
    cap = None

# --- If OpenCV failed, try picamera2 (Pi only) ---
picam = None
if cap is None:
    try:
        from picamera2 import Picamera2
        picam = Picamera2()
        picam.configure(picam.create_preview_configuration(
            main={"size": (640, 480), "format": "RGB888"}
        ))
        picam.start()
        time.sleep(1)  # let camera warm up
        frame = picam.capture_array()
        source = "picamera2"
        print(f"[OK] picamera2 works: {frame.shape[1]}x{frame.shape[0]}")
        print(f"     Format: {frame.dtype}, channels: {frame.shape[2]}")
        print(f"     NOTE: picamera2 gives RGB, not BGR (OpenCV uses BGR)")
    except ImportError:
        print("[FAIL] picamera2 not installed. Try: sudo apt install python3-picamera2")
        sys.exit(1)
    except Exception as e:
        print(f"[FAIL] picamera2 error: {e}")
        print("\n  Troubleshooting:")
        print("    - Is the camera ribbon cable connected properly?")
        print("    - Run: libcamera-hello  (test camera hardware)")
        print("    - Run: sudo raspi-config -> Interface -> Camera -> Enable")
        sys.exit(1)

if source is None:
    print("[FAIL] No camera available")
    sys.exit(1)

# --- Live preview ---
print(f"\nCamera source: {source}")
print("Showing live feed. Press 'q' to quit, 's' to save frame.\n")

import cv2 as cv2_display  # for display even if picamera2 is source

while True:
    if source == "OpenCV":
        ret, frame = cap.read()
        if not ret:
            break
    else:
        frame = picam.capture_array()
        # IMX296 sensor outputs BGR despite RGB888 label — no conversion needed

    cv2_display.putText(frame, f"Source: {source}", (10, 30),
                        cv2_display.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2_display.imshow("Pi Camera Test", frame)

    key = cv2_display.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('s'):
        cv2_display.imwrite("pi_test_frame.jpg", frame)
        print("Saved: pi_test_frame.jpg")

# Cleanup
if cap:
    cap.release()
if picam:
    picam.stop()
cv2_display.destroyAllWindows()
print("Done.")
