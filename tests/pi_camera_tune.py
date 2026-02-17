#!/usr/bin/env python3
"""
pi_camera_tune.py — Live camera colour tuning
==============================================
Shows raw Pi camera feed with sliders to fix blue tint in real time.
Once it looks good, press 's' to print the values for config.py.

Controls:
    Red gain slider    — boost red to counter blue tint
    Blue gain slider   — reduce blue
    Green gain slider  — fine-tune
    Gray World toggle  — auto white balance algorithm
    's' — print current values (copy to config.py)
    'r' — reset to defaults
    'q' / ESC — quit

Usage:
    python tests/pi_camera_tune.py
"""

import sys
import os
import time
import numpy as np
import cv2

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

# ── Camera setup ─────────────────────────────────────────────────────────

def open_camera():
    """Open camera: try OpenCV first, then picamera2."""
    try:
        import config
        w, h = config.IMAGE_W, config.IMAGE_H
    except Exception:
        w, h = 640, 480

    # Try OpenCV
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        ret, _ = cap.read()
        if ret:
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
            print(f"[CAM] OpenCV camera {w}x{h}")
            return cap, None

    # Try picamera2
    try:
        from picamera2 import Picamera2
        picam = Picamera2()
        picam.configure(picam.create_preview_configuration(
            main={"size": (w, h), "format": "RGB888"}
        ))
        picam.start()
        time.sleep(1)
        print(f"[CAM] picamera2 {w}x{h}")
        return None, picam
    except Exception as e:
        print(f"[CAM] No camera found: {e}")
        return None, None


def get_frame(cap, picam):
    if cap:
        ret, frame = cap.read()
        return frame if ret else None
    if picam:
        frame = picam.capture_array()
        return cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    return None


# ── Color correction ─────────────────────────────────────────────────────

def apply_gains(frame, r_gain, g_gain, b_gain):
    """Apply per-channel gain (1.0 = no change)."""
    f = frame.astype(np.float32)
    f[:, :, 2] = np.clip(f[:, :, 2] * r_gain, 0, 255)  # R
    f[:, :, 1] = np.clip(f[:, :, 1] * g_gain, 0, 255)  # G
    f[:, :, 0] = np.clip(f[:, :, 0] * b_gain, 0, 255)  # B
    return f.astype(np.uint8)


def gray_world(frame):
    """Gray world auto white balance — assumes average scene is neutral gray."""
    f = frame.astype(np.float32)
    avg_b = f[:, :, 0].mean()
    avg_g = f[:, :, 1].mean()
    avg_r = f[:, :, 2].mean()
    avg_all = (avg_b + avg_g + avg_r) / 3.0
    if avg_b > 0:
        f[:, :, 0] = np.clip(f[:, :, 0] * (avg_all / avg_b), 0, 255)
    if avg_g > 0:
        f[:, :, 1] = np.clip(f[:, :, 1] * (avg_all / avg_g), 0, 255)
    if avg_r > 0:
        f[:, :, 2] = np.clip(f[:, :, 2] * (avg_all / avg_r), 0, 255)
    return f.astype(np.uint8)


# ── Main ─────────────────────────────────────────────────────────────────

def main():
    cap, picam = open_camera()
    if cap is None and picam is None:
        print("No camera available. Exiting.")
        return

    win = "Camera Tune"
    cv2.namedWindow(win, cv2.WINDOW_NORMAL)

    # Sliders: value 50 = gain 1.0, range 0-100 maps to 0.0-2.0
    cv2.createTrackbar("Red",   win, 50, 100, lambda x: None)
    cv2.createTrackbar("Green", win, 50, 100, lambda x: None)
    cv2.createTrackbar("Blue",  win, 50, 100, lambda x: None)
    cv2.createTrackbar("GrayWorld", win, 0, 1, lambda x: None)

    print("\n--- Camera Colour Tuning ---")
    print("Drag sliders to adjust. 50 = no change.")
    print("'s' = print config values  'r' = reset  'q' = quit\n")

    fps_t0 = time.time()
    fps_count = 0
    fps = 0.0

    while True:
        frame = get_frame(cap, picam)
        if frame is None:
            continue

        # Read slider values
        r_val = cv2.getTrackbarPos("Red", win)
        g_val = cv2.getTrackbarPos("Green", win)
        b_val = cv2.getTrackbarPos("Blue", win)
        use_gw = cv2.getTrackbarPos("GrayWorld", win)

        r_gain = r_val / 50.0  # 50 -> 1.0
        g_gain = g_val / 50.0
        b_gain = b_val / 50.0

        # Apply corrections
        if use_gw:
            corrected = gray_world(frame)
        else:
            corrected = apply_gains(frame, r_gain, g_gain, b_gain)

        # FPS
        fps_count += 1
        elapsed = time.time() - fps_t0
        if elapsed >= 1.0:
            fps = fps_count / elapsed
            fps_count = 0
            fps_t0 = time.time()

        # Build display: raw on left, corrected on right
        h, w = frame.shape[:2]
        half_w = w // 2
        raw_small = cv2.resize(frame, (half_w, h))
        cor_small = cv2.resize(corrected, (half_w, h))
        display = np.hstack([raw_small, cor_small])

        # Labels
        cv2.putText(display, "RAW", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        cv2.putText(display, "CORRECTED", (half_w + 10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        # Info
        if use_gw:
            info = "Mode: Gray World (auto)"
        else:
            info = f"R={r_gain:.2f}  G={g_gain:.2f}  B={b_gain:.2f}"
        cv2.putText(display, info, (10, h - 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        cv2.putText(display, f"{fps:.1f} FPS", (10, h - 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

        cv2.imshow(win, display)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:
            break
        elif key == ord('r'):
            cv2.setTrackbarPos("Red", win, 50)
            cv2.setTrackbarPos("Green", win, 50)
            cv2.setTrackbarPos("Blue", win, 50)
            cv2.setTrackbarPos("GrayWorld", win, 0)
            print("[RESET] All gains back to 1.0")
        elif key == ord('s'):
            print("\n" + "=" * 50)
            print("  Copy these to config.py:")
            print("=" * 50)
            if use_gw:
                print('CAMERA_COLOR_CORRECTION = True')
                print("# Gray world auto-correction enabled")
            else:
                print(f'CAMERA_AWB_MODE = "manual"')
                print(f'CAMERA_COLOUR_GAINS = ({r_gain:.2f}, {b_gain:.2f})  # (red, blue)')
                print(f'# Green gain: {g_gain:.2f}')
            print("=" * 50 + "\n")

    cv2.destroyAllWindows()
    if cap:
        cap.release()
    if picam:
        try:
            picam.stop()
        except Exception:
            pass
    print("Done.")


if __name__ == "__main__":
    main()
