#!/usr/bin/env python3
"""
test_camera.py — Camera Connection Test

WHAT:    Opens a webcam (or Pi camera via OpenCV), reads properties (resolution,
         FPS), captures a test frame to verify the connection works, then shows
         a live preview window with resolution/FPS overlay. Press 's' to save
         a snapshot, 'q' to quit.
WHY:     Quick verification that the camera hardware is connected and producing
         frames. First thing to run when setting up a new machine or debugging
         camera issues.
WHEN:    When setting up a new environment. When camera stops working. Before
         running any CV tests.
WHERE:   Laptop only (also works on Pi with picamera2 OpenCV backend).
ENV:     "venv" (needs opencv-python only)
MODELS:  None (no AI inference).
RISK:    None — read-only camera access.

USAGE:
    python tests/laptop/test_camera.py           # default camera (index 0)
    python tests/laptop/test_camera.py 1         # camera index 1

FLAGS:
    [camera_index]   Optional positional argument: camera index (default: 0)

OUTPUT:
    Console: camera properties (resolution, FPS) and OK/FAIL status.
    Window: live camera preview with overlay text.
    File: test_snapshot.jpg (when 's' is pressed).
    Exit code: 0 if camera works, 1 if not.

BEST PRACTICES:
    - Try different camera indices if default fails (0, 1, 2)
    - On Pi, use libcamera-hello first to verify hardware
    - Check that resolution matches expected (640x480 or 1456x1088)

DEPENDENCIES:
    opencv-python
"""
import sys
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, project_root)

import cv2

def test_camera(index=0):
    print("=" * 45)
    print("       CAMERA TEST")
    print("=" * 45)

    print(f"\n  Opening camera {index}...")
    cap = cv2.VideoCapture(index)

    if not cap.isOpened():
        print(f"  [FAIL] Camera {index} could not be opened.")
        print("\n  Troubleshooting:")
        print("    - Is the camera connected / CSI ribbon seated?")
        print("    - Try: libcamera-hello  (Pi camera test)")
        print("    - Try different index: python tests/test_camera.py 1")
        return False

    # Read properties
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    # Capture a test frame
    ret, frame = cap.read()
    if not ret:
        print(f"  [FAIL] Camera opened but could not read a frame.")
        cap.release()
        return False

    print(f"  [OK]   Camera {index}: {w}x{h} @ {fps:.0f} fps")
    print(f"         Frame shape: {frame.shape}")
    print(f"\n  Live preview - press 'q' to quit, 's' to save snapshot")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Show frame info on screen
        cv2.putText(frame, f"Camera {index}: {w}x{h} @ {fps:.0f}fps",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        cv2.imshow("Camera Test", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            break
        elif key == ord('s'):
            filename = "test_snapshot.jpg"
            cv2.imwrite(filename, frame)
            print(f"  Saved: {filename}")

    cap.release()
    cv2.destroyAllWindows()
    return True

if __name__ == "__main__":
    cam_index = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    success = test_camera(cam_index)
    sys.exit(0 if success else 1)
