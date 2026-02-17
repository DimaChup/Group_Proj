#!/usr/bin/env python3
"""
Pi Color Picker — Pick the most realistic color correction.

Shows 6 versions of the same camera frame with different corrections.
Press 1-6 to select the best one. It prints the config values to use.

Usage:
    python tests/pi_color_picker.py
"""
import sys
import os
import time
import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ── Camera setup ──────────────────────────────────────────────────────────
cap = None
picam = None

cap = cv2.VideoCapture(0)
if cap.isOpened():
    ret, _ = cap.read()
    if not ret:
        cap.release()
        cap = None
else:
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
    except Exception as e:
        print(f"[FAIL] No camera: {e}")
        sys.exit(1)


def get_frame():
    if cap:
        ret, f = cap.read()
        return f if ret else None
    if picam:
        f = picam.capture_array()
        return cv2.cvtColor(f, cv2.COLOR_RGB2BGR)
    return None


# ── Color corrections ─────────────────────────────────────────────────────

def gray_world(frame):
    """Gray world white balance."""
    f = frame.astype(np.float32)
    avg_b, avg_g, avg_r = f[:,:,0].mean(), f[:,:,1].mean(), f[:,:,2].mean()
    avg = (avg_b + avg_g + avg_r) / 3.0
    if avg_b > 0: f[:,:,0] = np.clip(f[:,:,0] * (avg / avg_b), 0, 255)
    if avg_g > 0: f[:,:,1] = np.clip(f[:,:,1] * (avg / avg_g), 0, 255)
    if avg_r > 0: f[:,:,2] = np.clip(f[:,:,2] * (avg / avg_r), 0, 255)
    return f.astype(np.uint8)


def warm_boost(frame):
    """Reduce blue, boost red — warm shift."""
    f = frame.astype(np.float32)
    f[:,:,0] = np.clip(f[:,:,0] * 0.7, 0, 255)   # reduce blue
    f[:,:,2] = np.clip(f[:,:,2] * 1.3, 0, 255)   # boost red
    return f.astype(np.uint8)


def strong_warm(frame):
    """Strong warm correction — heavy blue reduction."""
    f = frame.astype(np.float32)
    f[:,:,0] = np.clip(f[:,:,0] * 0.55, 0, 255)  # heavy blue reduction
    f[:,:,1] = np.clip(f[:,:,1] * 1.05, 0, 255)  # slight green boost
    f[:,:,2] = np.clip(f[:,:,2] * 1.4, 0, 255)   # strong red boost
    return f.astype(np.uint8)


def gray_world_warm(frame):
    """Gray world + slight warm shift on top."""
    f = gray_world(frame).astype(np.float32)
    f[:,:,0] = np.clip(f[:,:,0] * 0.9, 0, 255)   # slight blue reduction
    f[:,:,2] = np.clip(f[:,:,2] * 1.1, 0, 255)   # slight red boost
    return f.astype(np.uint8)


def histogram_match(frame):
    """Histogram equalization per channel — maximises contrast."""
    b, g, r = cv2.split(frame)
    b = cv2.equalizeHist(b)
    g = cv2.equalizeHist(g)
    r = cv2.equalizeHist(r)
    return cv2.merge([b, g, r])


CORRECTIONS = [
    ("1: RAW (no correction)", None),
    ("2: Gray World", gray_world),
    ("3: Warm Boost (R+30% B-30%)", warm_boost),
    ("4: Strong Warm (R+40% B-45%)", strong_warm),
    ("5: Gray World + Warm", gray_world_warm),
    ("6: Histogram Equalize", histogram_match),
]

CONFIG_VALUES = [
    'CAMERA_COLOR_CORRECTION = False  # no correction',
    'CAMERA_COLOR_CORRECTION = True   # gray_world only',
    'CAMERA_COLOR_CORRECTION = "warm_boost"',
    'CAMERA_COLOR_CORRECTION = "strong_warm"',
    'CAMERA_COLOR_CORRECTION = "gray_world_warm"',
    'CAMERA_COLOR_CORRECTION = "histogram"',
]


# ── Main ──────────────────────────────────────────────────────────────────

print("=" * 50)
print("  PI COLOR PICKER")
print("  Press 1-6 to select best color correction")
print("  Press 'r' to refresh with new frame")
print("  Press 'q' to quit without selecting")
print("=" * 50)

selected = None

while True:
    raw = get_frame()
    if raw is None:
        time.sleep(0.05)
        continue

    # Build grid: 2 rows x 3 columns
    thumb_w, thumb_h = 320, 240
    grid = np.zeros((thumb_h * 2 + 60, thumb_w * 3, 3), dtype=np.uint8)

    for i, (label, correction) in enumerate(CORRECTIONS):
        corrected = correction(raw.copy()) if correction else raw.copy()
        thumb = cv2.resize(corrected, (thumb_w, thumb_h))

        # Add label
        cv2.putText(thumb, label, (5, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

        row = i // 3
        col = i % 3
        y = row * (thumb_h + 30)
        x = col * thumb_w
        grid[y:y + thumb_h, x:x + thumb_w] = thumb

    # Instructions at bottom
    cv2.putText(grid, "Press 1-6 to select  |  'r' = refresh  |  'q' = quit",
                (10, grid.shape[0] - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

    cv2.imshow("Color Picker", grid)
    key = cv2.waitKey(0) & 0xFF

    if key == ord('q') or key == 27:
        print("\nNo selection made.")
        break
    elif key == ord('r'):
        print("  Refreshing...")
        continue
    elif ord('1') <= key <= ord('6'):
        idx = key - ord('1')
        selected = idx
        name = CORRECTIONS[idx][0]
        print(f"\n  >> Selected: {name}")
        print(f"\n  To apply, set in config.py:")
        print(f"    {CONFIG_VALUES[idx]}")

        # Show selected full size
        if CORRECTIONS[idx][1]:
            result = CORRECTIONS[idx][1](raw.copy())
        else:
            result = raw.copy()
        cv2.putText(result, f"SELECTED: {name}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.imshow("Selected Correction", result)
        print("\n  Press any key to close.")
        cv2.waitKey(0)
        break

# Cleanup
if cap:
    cap.release()
if picam:
    try:
        picam.stop()
    except Exception:
        pass
cv2.destroyAllWindows()

if selected is not None:
    print(f"\n{'=' * 50}")
    print(f"  NEXT STEP:")
    print(f"  Update config.py with:")
    print(f"    {CONFIG_VALUES[selected]}")
    print(f"  Then vision.py will apply this to every frame.")
    print(f"{'=' * 50}\n")
