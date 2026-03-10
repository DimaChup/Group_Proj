#!/usr/bin/env python3
"""
Test computer vision pipeline. Loads the AI model and runs detection
on a test image or live camera feed.

Usage: python tests/test_cv.py                  (test with dummy.png)
       python tests/test_cv.py test_image.jpg   (test with specific image)
       python tests/test_cv.py --camera          (test with live camera)
"""
import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2
import numpy as np

def test_cv(image_path=None, use_camera=False):
    print("=" * 45)
    print("       COMPUTER VISION TEST")
    print("=" * 45)

    # 1. Load model
    print("\n  Loading AI model...")
    try:
        from vision import VisionSystem
        eyes = VisionSystem(camera_index=None, model_path="best.tflite")
    except Exception as e:
        print(f"  [FAIL] Could not import vision system: {e}")
        return False

    if not eyes.using_ai:
        print(f"  [FAIL] Model did not load.")
        print("\n  Troubleshooting:")
        print("    - Does best.tflite exist in the project root?")
        print("    - Is ultralytics or tflite-runtime installed?")
        return False

    backend = "TFLite" if eyes._use_tflite_direct else "Ultralytics"
    print(f"  [OK]   Model loaded ({backend})")

    # 2. Get test image
    if use_camera:
        print("  Opening camera for live detection...")
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("  [FAIL] Camera not available")
            return False

        print("  Live detection - press 'q' to quit\n")
        frame_count = 0
        detect_count = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1
            start = time.time()
            found, x, y, conf = eyes.detect_in_image(frame)
            elapsed = (time.time() - start) * 1000

            if found:
                detect_count += 1

            # Show inference time
            cv2.putText(frame, f"Inference: {elapsed:.0f}ms | Det: {detect_count}/{frame_count}",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

            cv2.imshow("CV Test - Live", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        print(f"  Frames: {frame_count}, Detections: {detect_count}")
        return True

    else:
        # Static image test
        if image_path and os.path.exists(image_path):
            frame = cv2.imread(image_path)
            src = image_path
        elif os.path.exists("dummy.png"):
            # Create a test scene: green background with dummy placed on it
            bg = np.zeros((480, 640, 3), dtype=np.uint8)
            bg[:] = (34, 139, 34)  # green grass
            dummy = cv2.imread("dummy.png", cv2.IMREAD_UNCHANGED)
            if dummy is not None:
                h, w = dummy.shape[:2]
                scale = 200 / h
                dummy_resized = cv2.resize(dummy, (int(w * scale), 200))
                dh, dw = dummy_resized.shape[:2]
                y_off = 480 - dh
                x_off = 320 - dw // 2
                if dummy_resized.shape[2] == 4:
                    alpha = dummy_resized[:, :, 3] / 255.0
                    for c in range(3):
                        bg[y_off:y_off+dh, x_off:x_off+dw, c] = (
                            (1 - alpha) * bg[y_off:y_off+dh, x_off:x_off+dw, c] +
                            alpha * dummy_resized[:, :, c]
                        )
                else:
                    bg[y_off:y_off+dh, x_off:x_off+dw] = dummy_resized
            frame = bg
            src = "generated scene (dummy.png on green bg)"
        else:
            # Plain test pattern
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            frame[:] = (34, 139, 34)
            cv2.circle(frame, (320, 240), 30, (0, 0, 255), -1)
            src = "test pattern (red circle)"

        print(f"  Test image: {src}")
        print(f"  Running detection...")

        start = time.time()
        found, x, y, conf = eyes.detect_in_image(frame)
        elapsed = (time.time() - start) * 1000

        print(f"  Inference time: {elapsed:.0f}ms")

        if found:
            print(f"  [OK]   Detection at ({x}, {y}) confidence={conf:.2f}")
        else:
            print(f"  [INFO] No detection (this may be normal for test images)")

        # Show result
        cv2.putText(frame, f"{'DETECTED' if found else 'No detection'} ({elapsed:.0f}ms)",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0) if found else (0, 0, 255), 2)
        cv2.imshow("CV Test Result", frame)
        print("\n  Press any key to close...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        return True

if __name__ == "__main__":
    img = None
    camera = False
    for arg in sys.argv[1:]:
        if arg == "--camera":
            camera = True
        else:
            img = arg
    success = test_cv(image_path=img, use_camera=camera)
    sys.exit(0 if success else 1)
