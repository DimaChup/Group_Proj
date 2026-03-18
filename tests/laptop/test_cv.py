#!/usr/bin/env python3
"""
test_cv.py — Computer Vision Pipeline Test

WHAT:    Loads the AI model via VisionSystem and tests detection on either a
         static image or live camera feed. In static mode, generates a test
         scene (dummy.png composited on green background, or a custom image).
         In camera mode, runs continuous live detection with FPS counter and
         detection rate display. Reports inference time and detection coordinates.
WHY:     Validates the full CV pipeline (model loading, preprocessing, inference,
         postprocessing) works correctly. Tests both Ultralytics and TFLite
         backends depending on what is installed. Quick smoke test before
         running more complex scripts.
WHEN:    After installing dependencies. After swapping models. When detection
         seems broken. Before flight day to verify CV works.
WHERE:   Laptop only (requires display for cv2.imshow).
ENV:     "venv" (needs opencv-python, numpy, vision.py with Ultralytics or TFLite)
MODELS:  best.tflite from project root (via VisionSystem).
RISK:    None — read-only detection, no commands sent.

USAGE:
    python tests/laptop/test_cv.py                    # test with dummy.png
    python tests/laptop/test_cv.py test_image.jpg     # test with specific image
    python tests/laptop/test_cv.py --camera           # live webcam detection

FLAGS:
    [image_path]    Optional: path to test image (default: dummy.png composite)
    --camera        Use live webcam instead of static image

OUTPUT:
    Console: model backend (TFLite/Ultralytics), inference time, detection
    coordinates and confidence.
    Window: test image or live video with detection overlay.
    Exit code: 0 if model loads successfully, 1 if not.

BEST PRACTICES:
    - Run without args first (uses dummy.png) to verify model loads
    - Use --camera to test real-world detection with printed dummy
    - Check reported backend matches expectations (TFLite on Pi, either on laptop)

DEPENDENCIES:
    opencv-python, numpy, vision.py
"""
import sys
import os
import time
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, project_root)

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
        elif os.path.exists("assets/dummy.png"):
            # Create a test scene: green background with dummy placed on it
            bg = np.zeros((480, 640, 3), dtype=np.uint8)
            bg[:] = (34, 139, 34)  # green grass
            dummy = cv2.imread("assets/dummy.png", cv2.IMREAD_UNCHANGED)
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
