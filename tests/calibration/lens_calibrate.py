#!/usr/bin/env python3
"""
Lens Calibrate — Lens distortion calibration using checkerboard pattern.

WHAT:    Computes camera matrix and distortion coefficients (k1, k2, p1, p2, k3) using
         OpenCV's checkerboard calibration. Captures 10-20 images of a printed
         checkerboard at various angles, then computes the intrinsic parameters.
         Saves calibration_data.npz which vision.py loads at startup to undistort
         every frame via precomputed cv2.remap() maps (~1.5ms per frame).
WHY:     Barrel/pincushion distortion shifts pixel positions near frame edges. Without
         correction, a dummy detected near the edge will have its GPS position estimated
         incorrectly (pixels map to wrong ground coordinates). The IMX296 global shutter
         camera has measurable distortion. Calibration RMS of 0.399 was achieved on Pi.
WHEN:    Once per camera (results are saved). Re-run if camera or lens changes.
         Must be done BEFORE flight — vision.py auto-loads calibration_data.npz.
WHERE:   Both Pi and laptop (auto-detects picamera2 or OpenCV camera).
ENV:     Any venv with opencv and numpy.
MODELS:  None (no AI inference, camera geometry only).
RISK:    None. Camera read-only, no commands sent.

USAGE:
    python tests/calibration/lens_calibrate.py                  # interactive calibration
    python tests/calibration/lens_calibrate.py --headless       # auto-capture mode (Pi/SSH)
    python tests/calibration/lens_calibrate.py --board 9x6      # custom board size
    python tests/calibration/lens_calibrate.py --board 13x8     # calib.io 14x9 board
    python tests/calibration/lens_calibrate.py --load           # load + show undistorted feed

FLAGS:
    --headless    Auto-capture mode (no cv2 display, captures every 3s, stops at 15)
    --board WxH   Inner corner count of checkerboard (default: 13x8 for calib.io 14x9 board)
    --load        Load existing calibration_data.npz and show live undistorted feed

OUTPUT:
    - calibration_data.npz (camera_matrix, dist_coeffs, rms_error, image_size)
    - RMS reprojection error (< 0.5 is good, < 1.0 is acceptable)
    - Camera matrix (fx, fy, cx, cy) and distortion coefficients
    - Side-by-side original vs undistorted comparison

BEST PRACTICES:
    - Print checkerboard on stiff paper/cardboard (no warping)
    - Use calib.io boards (14x9, 28mm squares) — they have rounded corners for better detection
    - Capture at different angles, distances, and positions across the frame
    - Include edge/corner positions (distortion is worst at edges)
    - 15-20 captures is ideal; minimum 5 required
    - Script uses findChessboardCornersSB fallback for non-standard boards
    - On Pi, calibration_data.npz stays on Pi (not in git)

DEPENDENCIES:
    opencv-python (or opencv-python-headless), numpy
    Optional: picamera2 (auto-detected on Pi)
"""

import sys, os, time
import cv2
import numpy as np

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, project_root)

HEADLESS = "--headless" in sys.argv
LOAD_ONLY = "--load" in sys.argv
BOARD_W, BOARD_H = 13, 8  # inner corners (for 14x9 squares calib.io board)

for _i, _a in enumerate(sys.argv):
    if _a == "--board" and _i + 1 < len(sys.argv):
        parts = sys.argv[_i + 1].split("x")
        BOARD_W, BOARD_H = int(parts[0]), int(parts[1])

CALIB_FILE = os.path.join(project_root, "calibration_data.npz")

def open_camera():
    """Open camera (picamera2 on Pi, OpenCV on laptop)."""
    try:
        from picamera2 import Picamera2
        picam = Picamera2()
        cam_config = picam.create_preview_configuration(
            main={"size": (640, 480), "format": "RGB888"})
        picam.configure(cam_config)
        picam.start()
        time.sleep(1)
        class PiCam:
            def read(self):
                return True, picam.capture_array()
            def release(self):
                picam.stop()
        print("[CAM] Using picamera2")
        return PiCam()
    except ImportError:
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("[CAM] Using OpenCV")
            return cap
    print("[CAM] No camera found!")
    return None


def calibrate():
    """Capture checkerboard images and compute calibration."""
    print("=" * 60)
    print("  LENS DISTORTION CALIBRATION")
    print("=" * 60)
    print()
    print(f"  Checkerboard: {BOARD_W}x{BOARD_H} inner corners")
    print("  Hold checkerboard at different angles in front of camera.")
    print("  Press SPACE to capture. Need 10-20 good captures.")
    print("  Press 'c' to compute calibration when ready.")
    print("  Press 'q' to quit.")
    print()

    cam = open_camera()
    if cam is None:
        return

    # Termination criteria for corner refinement
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    # 3D points in real world (checkerboard is flat, so z=0)
    objp = np.zeros((BOARD_H * BOARD_W, 3), np.float32)
    objp[:, :2] = np.mgrid[0:BOARD_W, 0:BOARD_H].T.reshape(-1, 2)

    obj_points = []  # 3D points
    img_points = []  # 2D points in image
    img_size = None

    if not HEADLESS:
        cv2.namedWindow("Lens Calibration", cv2.WINDOW_NORMAL)

    capture_count = 0

    print("[READY] Show checkerboard to camera. Press SPACE to capture.\n")

    try:
        while True:
            ret, frame = cam.read()
            if not ret or frame is None:
                time.sleep(0.05)
                continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            if img_size is None:
                img_size = gray.shape[::-1]

            # Try to find checkerboard (robust flags for calib.io boards with rounded edges)
            flags = (cv2.CALIB_CB_ADAPTIVE_THRESH +
                     cv2.CALIB_CB_NORMALIZE_IMAGE +
                     cv2.CALIB_CB_FAST_CHECK)
            found, corners = cv2.findChessboardCorners(gray, (BOARD_W, BOARD_H), flags)
            # Fallback: try the newer SB detector (handles non-standard boards better)
            if not found and hasattr(cv2, 'findChessboardCornersSB'):
                found, corners = cv2.findChessboardCornersSB(gray, (BOARD_W, BOARD_H), None)

            display = frame.copy()
            if found:
                # Refine corner positions
                corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
                cv2.drawChessboardCorners(display, (BOARD_W, BOARD_H), corners2, found)
                cv2.putText(display, "BOARD FOUND - press SPACE to capture",
                            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            else:
                cv2.putText(display, "Looking for checkerboard...",
                            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            cv2.putText(display, f"Captures: {capture_count}/10+  (SPACE=capture, C=compute, Q=quit)",
                        (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

            if HEADLESS:
                if found:
                    print(f"  Board found! {capture_count} captures so far. "
                          "Press SPACE in terminal (or auto-capture every 3s)")
                    # Auto-capture in headless mode
                    corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
                    obj_points.append(objp)
                    img_points.append(corners2)
                    capture_count += 1
                    print(f"  AUTO-CAPTURED #{capture_count}")
                    time.sleep(3)  # wait before next auto-capture
                    if capture_count >= 15:
                        break
                else:
                    time.sleep(0.5)
                continue

            cv2.imshow("Lens Calibration", display)
            key = cv2.waitKey(1) & 0xFF

            if key == ord(' ') and found:
                corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
                obj_points.append(objp)
                img_points.append(corners2)
                capture_count += 1
                print(f"  Captured #{capture_count}")

            elif key == ord('c'):
                if capture_count < 5:
                    print(f"  Need at least 5 captures (have {capture_count})")
                else:
                    break

            elif key == ord('q') or key == 27:
                print("  Cancelled.")
                cam.release()
                cv2.destroyAllWindows()
                return

    except KeyboardInterrupt:
        pass

    if not HEADLESS:
        cv2.destroyAllWindows()

    if capture_count < 5:
        print(f"  Not enough captures ({capture_count}). Need at least 5.")
        cam.release()
        return

    # Compute calibration
    print(f"\n  Computing calibration from {capture_count} images...")
    ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(
        obj_points, img_points, img_size, None, None)

    print(f"\n  Calibration RMS error: {ret:.4f}")
    print(f"  (< 0.5 is good, < 1.0 is acceptable)")
    print()
    print(f"  Camera matrix:")
    print(f"    fx = {camera_matrix[0, 0]:.1f}")
    print(f"    fy = {camera_matrix[1, 1]:.1f}")
    print(f"    cx = {camera_matrix[0, 2]:.1f}")
    print(f"    cy = {camera_matrix[1, 2]:.1f}")
    print()
    print(f"  Distortion coefficients:")
    print(f"    k1={dist_coeffs[0, 0]:.6f}  k2={dist_coeffs[0, 1]:.6f}")
    print(f"    p1={dist_coeffs[0, 2]:.6f}  p2={dist_coeffs[0, 3]:.6f}")
    print(f"    k3={dist_coeffs[0, 4]:.6f}")

    # Save
    np.savez(CALIB_FILE,
             camera_matrix=camera_matrix,
             dist_coeffs=dist_coeffs,
             rms_error=ret,
             image_size=img_size)
    print(f"\n  Saved to: {CALIB_FILE}")

    # Show undistorted comparison
    print("\n  Showing undistorted comparison (press any key)...")
    ret, frame = cam.read()
    if ret and frame is not None:
        h, w = frame.shape[:2]
        new_matrix, roi = cv2.getOptimalNewCameraMatrix(
            camera_matrix, dist_coeffs, (w, h), 1, (w, h))
        undistorted = cv2.undistort(frame, camera_matrix, dist_coeffs, None, new_matrix)

        if not HEADLESS:
            comparison = np.hstack([frame, undistorted])
            cv2.putText(comparison, "ORIGINAL", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            cv2.putText(comparison, "UNDISTORTED", (w + 10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.imshow("Calibration Result", comparison)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

    cam.release()

    print()
    print("  TO USE IN VISION.PY:")
    print("    data = np.load('calibration_data.npz')")
    print("    mtx = data['camera_matrix']")
    print("    dist = data['dist_coeffs']")
    print("    frame = cv2.undistort(frame, mtx, dist)")
    print()
    print("  This corrects barrel distortion, improving GPS accuracy")
    print("  for detections near frame edges.")


def load_and_test():
    """Load existing calibration and show undistorted feed."""
    if not os.path.exists(CALIB_FILE):
        print(f"  No calibration file found at: {CALIB_FILE}")
        print("  Run without --load first to create one.")
        return

    data = np.load(CALIB_FILE)
    camera_matrix = data["camera_matrix"]
    dist_coeffs = data["dist_coeffs"]
    rms = float(data["rms_error"])
    print(f"  Loaded calibration (RMS={rms:.4f})")
    print(f"  fx={camera_matrix[0,0]:.1f} fy={camera_matrix[1,1]:.1f}")

    cam = open_camera()
    if cam is None:
        return

    if not HEADLESS:
        cv2.namedWindow("Undistorted Feed", cv2.WINDOW_NORMAL)

    print("  Showing live undistorted feed. Press 'q' to quit.")

    try:
        while True:
            ret, frame = cam.read()
            if not ret:
                continue

            undistorted = cv2.undistort(frame, camera_matrix, dist_coeffs)

            if HEADLESS:
                print("  Feed running (headless). Ctrl+C to stop.")
                time.sleep(1)
            else:
                comparison = np.hstack([frame, undistorted])
                cv2.putText(comparison, "ORIGINAL", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                cv2.putText(comparison, "UNDISTORTED", (frame.shape[1] + 10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.imshow("Undistorted Feed", comparison)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
    except KeyboardInterrupt:
        pass

    cam.release()
    if not HEADLESS:
        cv2.destroyAllWindows()


if __name__ == "__main__":
    if LOAD_ONLY:
        load_and_test()
    else:
        calibrate()
