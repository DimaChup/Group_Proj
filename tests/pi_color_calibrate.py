#!/usr/bin/env python3
"""
Pi Color Calibration — Systematic color correction with reference chart.

1. Print or display the color chart (saved as color_chart.png)
2. Point Pi camera at it
3. Adjust Red/Blue sliders until camera colors match the references
4. Press 's' to save settings

Usage:
    python tests/pi_color_calibrate.py
"""
import sys
import os
import time
import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ── Step 1: Generate a printable color chart ──────────────────────────────
def make_color_chart():
    """Create a simple color chart image to print/display."""
    chart = np.ones((400, 600, 3), dtype=np.uint8) * 240  # light gray background

    # 2x3 grid of color patches
    colors = [
        ("RED",    (0, 0, 255)),      # top-left
        ("GREEN",  (0, 200, 0)),      # top-centre
        ("BLUE",   (255, 0, 0)),      # top-right
        ("YELLOW", (0, 255, 255)),    # bottom-left
        ("WHITE",  (255, 255, 255)),  # bottom-centre
        ("BLACK",  (0, 0, 0)),        # bottom-right
    ]

    patch_w, patch_h = 160, 140
    margin = 20
    for i, (name, bgr) in enumerate(colors):
        row = i // 3
        col = i % 3
        x = margin + col * (patch_w + margin)
        y = margin + row * (patch_h + 50)

        # Color patch
        cv2.rectangle(chart, (x, y), (x + patch_w, y + patch_h), bgr, -1)
        cv2.rectangle(chart, (x, y), (x + patch_w, y + patch_h), (0, 0, 0), 2)

        # Label
        text_col = (0, 0, 0) if name != "BLACK" else (200, 200, 200)
        cv2.putText(chart, name, (x + 10, y + patch_h + 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

    cv2.putText(chart, "POINT CAMERA AT THIS CHART", (100, 390),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 200), 2)

    path = os.path.join(project_root, "color_chart.png")
    cv2.imwrite(path, chart)
    print(f"  Color chart saved: {path}")
    print(f"  Print it or display it on a screen, then point the Pi camera at it.\n")
    return chart


# ── Camera setup ──────────────────────────────────────────────────────────
chart = make_color_chart()

from picamera2 import Picamera2

cam = Picamera2()
cam.configure(cam.create_preview_configuration(
    main={"size": (640, 480), "format": "RGB888"}
))
cam.start()
time.sleep(2)

# ── Reference colors (what perfect calibration looks like) ────────────────
REF_COLORS = [
    ("RED",    (0, 0, 255)),
    ("GREEN",  (0, 200, 0)),
    ("BLUE",   (255, 0, 0)),
    ("YELLOW", (0, 255, 255)),
    ("WHITE",  (255, 255, 255)),
    ("BLACK",  (30, 30, 30)),
]


def draw_reference_panel(h):
    """Draw the reference color column on the right side."""
    panel_w = 160
    panel = np.ones((h, panel_w, 3), dtype=np.uint8) * 40

    cv2.putText(panel, "TARGET", (10, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

    patch_size = 50
    y_start = 45
    spacing = (h - y_start - 10) // 6

    for i, (name, bgr) in enumerate(REF_COLORS):
        y = y_start + i * spacing
        # Reference patch
        cv2.rectangle(panel, (10, y), (10 + patch_size, y + patch_size), bgr, -1)
        cv2.rectangle(panel, (10, y), (10 + patch_size, y + patch_size), (200, 200, 200), 1)
        # Label
        cv2.putText(panel, name, (70, y + 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)

    return panel, y_start, spacing, patch_size


def sample_camera_colors(frame):
    """Sample colors from 6 regions of the frame (2x3 grid)."""
    h, w = frame.shape[:2]
    samples = []
    for row in range(2):
        for col in range(3):
            # Sample from center of each grid cell
            cx = int((col + 0.5) * w / 3)
            cy = int((row + 0.5) * h / 2)
            # Average a 30x30 region
            r = 15
            region = frame[max(0,cy-r):cy+r, max(0,cx-r):cx+r]
            avg_color = region.mean(axis=(0, 1)).astype(int)
            samples.append((avg_color, cx, cy))
    return samples


# ── Main loop ─────────────────────────────────────────────────────────────
cv2.namedWindow("Calibration")
cv2.createTrackbar("Red x10", "Calibration", 15, 40, lambda x: None)
cv2.createTrackbar("Blue x10", "Calibration", 10, 40, lambda x: None)

print("=" * 55)
print("  COLOR CALIBRATION")
print("=" * 55)
print("  1. Display or print color_chart.png")
print("  2. Point Pi camera at the chart")
print("  3. Adjust sliders until camera colors match TARGET")
print("  4. Press 's' to save settings, 'q' to quit")
print("=" * 55)

last_r, last_b = 0, 0

while True:
    r_val = max(5, cv2.getTrackbarPos("Red x10", "Calibration"))
    b_val = max(5, cv2.getTrackbarPos("Blue x10", "Calibration"))

    r_gain = r_val / 10.0
    b_gain = b_val / 10.0

    if r_val != last_r or b_val != last_b:
        cam.set_controls({"AwbEnable": False, "ColourGains": (r_gain, b_gain)})
        last_r, last_b = r_val, b_val
        time.sleep(0.3)

    frame = cam.capture_array()
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    h, w = frame.shape[:2]

    # Draw grid lines on camera showing the 6 sample regions
    cv2.line(frame, (w//3, 0), (w//3, h), (100, 100, 100), 1)
    cv2.line(frame, (2*w//3, 0), (2*w//3, h), (100, 100, 100), 1)
    cv2.line(frame, (0, h//2), (w, h//2), (100, 100, 100), 1)

    # Sample colors from camera
    samples = sample_camera_colors(frame)

    # Draw sample circles on camera
    for avg_color, cx, cy in samples:
        color_tuple = (int(avg_color[0]), int(avg_color[1]), int(avg_color[2]))
        cv2.circle(frame, (cx, cy), 20, color_tuple, -1)
        cv2.circle(frame, (cx, cy), 20, (255, 255, 255), 2)

    # Gain info on camera
    cv2.putText(frame, f"R={r_gain:.1f} B={b_gain:.1f}", (10, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

    # Build reference panel
    ref_panel, y_start, spacing, patch_size = draw_reference_panel(h)

    # Add "CAMERA" patches next to reference
    for i, ((avg_color, _, _), (name, ref_bgr)) in enumerate(zip(samples, REF_COLORS)):
        y = y_start + i * spacing
        cam_color = (int(avg_color[0]), int(avg_color[1]), int(avg_color[2]))

        # "Camera sees" label and patch (to the right of reference)
        # We'll add an arrow between ref and camera
        # Reference is at x=10, camera patch at x=70 would overlap label
        # Let's put camera patch below the reference
        cy = y + patch_size + 2
        cv2.rectangle(ref_panel, (10, y + patch_size + 2), (10 + patch_size, y + patch_size + 18),
                      cam_color, -1)
        cv2.rectangle(ref_panel, (10, y + patch_size + 2), (10 + patch_size, y + patch_size + 18),
                      (150, 150, 150), 1)

        # Match indicator
        ref_arr = np.array(ref_bgr, dtype=float)
        cam_arr = np.array(cam_color, dtype=float)
        diff = np.sqrt(np.sum((ref_arr - cam_arr) ** 2))
        if diff < 60:
            status = "OK"
            status_col = (0, 255, 0)
        elif diff < 120:
            status = "~"
            status_col = (0, 200, 255)
        else:
            status = "X"
            status_col = (0, 0, 255)
        cv2.putText(ref_panel, status, (130, y + 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, status_col, 2)

    # Combine camera + reference panel
    canvas = np.hstack([frame, ref_panel])

    cv2.imshow("Calibration", canvas)
    key = cv2.waitKey(50) & 0xFF

    if key == ord('q') or key == 27:
        break
    elif key == ord('s'):
        print(f"\n  ===== CALIBRATION RESULT =====")
        print(f"  Red gain:  {r_gain:.1f}")
        print(f"  Blue gain: {b_gain:.1f}")
        print(f"\n  Put in config.py:")
        print(f'    CAMERA_AWB_MODE = "manual"')
        print(f"    CAMERA_COLOUR_GAINS = ({r_gain:.1f}, {b_gain:.1f})")
        print(f"  ==============================\n")

cam.close()
cv2.destroyAllWindows()
