#!/usr/bin/env python3
"""
Test camera connection. Captures a frame and shows a live preview.
Press 'q' to quit, 's' to save a snapshot.

Usage: python tests/test_camera.py
       python tests/test_camera.py 1        (camera index 1)
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
