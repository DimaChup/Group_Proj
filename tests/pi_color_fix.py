#!/usr/bin/env python3
"""
Pi Color Fix — Measures the blue tint and tries computed corrections.

Shows a grid of 9 different colour gain combinations.
Pick the best one, it tells you what to set in config.py.

Usage:
    python tests/pi_color_fix.py
"""
import sys
import os
import time
import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ── Camera ────────────────────────────────────────────────────────────────
from picamera2 import Picamera2
from libcamera import controls

cam = Picamera2()
cam.configure(cam.create_preview_configuration(
    main={"size": (640, 480), "format": "RGB888"}
))
cam.start()
time.sleep(2)  # let AWB settle

# ── Capture raw frame and analyse ─────────────────────────────────────────
raw = cam.capture_array()
raw_bgr = cv2.cvtColor(raw, cv2.COLOR_RGB2BGR)

# Measure channel averages
b_avg = raw_bgr[:,:,0].mean()
g_avg = raw_bgr[:,:,1].mean()
r_avg = raw_bgr[:,:,2].mean()

print(f"\n  Raw channel averages:  R={r_avg:.1f}  G={g_avg:.1f}  B={b_avg:.1f}")
print(f"  Blue is {b_avg/r_avg:.2f}x stronger than Red")

# ── Try different ColourGains via picamera2 ───────────────────────────────
# ColourGains = (red_gain, blue_gain) — applied at sensor level
# We need to boost red and reduce blue

# Compute ideal gains to balance channels
# Target: make R and B equal to G
ideal_r = g_avg / r_avg if r_avg > 0 else 1.5
ideal_b = g_avg / b_avg if b_avg > 0 else 0.8

print(f"  Computed ideal gains:  R={ideal_r:.2f}  B={ideal_b:.2f}")

# Generate a grid of gain combinations around the ideal
gain_sets = [
    (ideal_r * 0.7, ideal_b * 0.7, "70% of ideal"),
    (ideal_r * 0.85, ideal_b * 0.85, "85% of ideal"),
    (ideal_r, ideal_b, "Computed ideal"),
    (ideal_r * 1.15, ideal_b * 1.15, "115% of ideal"),
    (ideal_r * 1.3, ideal_b * 1.3, "130% of ideal"),
    (ideal_r, ideal_b * 0.7, "Ideal R, less B"),
    (ideal_r * 1.2, ideal_b * 0.8, "More R, less B"),
    (ideal_r * 1.3, ideal_b * 0.6, "Strong R, weak B"),
    (1.5, 1.2, "Default (1.5, 1.2)"),
]

print(f"\n  Capturing 9 versions with different gains...")
print(f"  (each takes ~2 seconds to settle)\n")

frames = []
for i, (rg, bg, label) in enumerate(gain_sets):
    rg = round(min(max(rg, 0.5), 4.0), 2)
    bg = round(min(max(bg, 0.5), 4.0), 2)

    cam.set_controls({"AwbEnable": False, "ColourGains": (rg, bg)})
    time.sleep(1.5)  # let it settle

    frame = cam.capture_array()
    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    # Measure new averages
    nb = frame_bgr[:,:,0].mean()
    ng = frame_bgr[:,:,1].mean()
    nr = frame_bgr[:,:,2].mean()

    print(f"  {i+1}. R={rg:.2f} B={bg:.2f} ({label})  →  R={nr:.1f} G={ng:.1f} B={nb:.1f}")

    frames.append((frame_bgr, f"{i+1}: R={rg:.2f} B={bg:.2f}", rg, bg, label))

cam.close()

# ── Show grid ─────────────────────────────────────────────────────────────
thumb_w, thumb_h = 213, 160  # 3x3 grid fits in 640x480
grid = np.zeros((thumb_h * 3 + 40, thumb_w * 3, 3), dtype=np.uint8)

for i, (frame, label, rg, bg, desc) in enumerate(frames):
    thumb = cv2.resize(frame, (thumb_w, thumb_h))
    cv2.putText(thumb, label, (5, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)
    cv2.putText(thumb, desc, (5, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (200, 200, 200), 1)

    row = i // 3
    col = i % 3
    y = row * thumb_h
    x = col * thumb_w
    grid[y:y + thumb_h, x:x + thumb_w] = thumb

cv2.putText(grid, "Press 1-9 to select  |  'q' = quit",
            (10, grid.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

cv2.imshow("Color Fix - Pick Best", grid)
print(f"\n  Press 1-9 to select the most realistic image, 'q' to quit")

while True:
    key = cv2.waitKey(0) & 0xFF
    if key == ord('q') or key == 27:
        print("  No selection.")
        break
    elif ord('1') <= key <= ord('9'):
        idx = key - ord('1')
        _, label, rg, bg, desc = frames[idx]
        print(f"\n  >> Selected: {label} ({desc})")
        print(f"\n  Add to config.py:")
        print(f"    CAMERA_AWB_MODE = \"manual\"")
        print(f"    CAMERA_COLOUR_GAINS = ({rg:.2f}, {bg:.2f})")
        print(f"\n  vision.py will apply these gains automatically.")

        # Show selected full size
        cv2.imshow("Selected", frames[idx][0])
        cv2.waitKey(0)
        break

cv2.destroyAllWindows()
