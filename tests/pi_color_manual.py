#!/usr/bin/env python3
"""
Manual color tuning with live sliders.
Two sliders: Red gain and Blue gain.
Adjust until the image looks natural. Press 's' to print settings.

Usage:
    python tests/pi_color_manual.py
"""
import time
import cv2
import numpy as np

from picamera2 import Picamera2

cam = Picamera2()
cam.configure(cam.create_preview_configuration(
    main={"size": (640, 480), "format": "RGB888"}
))
cam.start()
time.sleep(2)

cv2.namedWindow("Color Tune")

# Sliders: value 10 = gain 1.0, value 20 = gain 2.0, etc.
# Range 5-30 means gain 0.5 to 3.0
cv2.createTrackbar("Red x10", "Color Tune", 15, 30, lambda x: None)
cv2.createTrackbar("Blue x10", "Color Tune", 10, 30, lambda x: None)

print("Adjust sliders until colors look natural.")
print("  's' = print current settings")
print("  'q' = quit")

last_r, last_b = 0, 0

while True:
    r_val = max(5, cv2.getTrackbarPos("Red x10", "Color Tune"))
    b_val = max(5, cv2.getTrackbarPos("Blue x10", "Color Tune"))

    r_gain = r_val / 10.0
    b_gain = b_val / 10.0

    # Only update camera if gains changed
    if r_val != last_r or b_val != last_b:
        cam.set_controls({"AwbEnable": False, "ColourGains": (r_gain, b_gain)})
        last_r, last_b = r_val, b_val
        time.sleep(0.3)

    frame = cam.capture_array()
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    # Show current gains on frame
    cv2.putText(frame, f"Red: {r_gain:.1f}  Blue: {b_gain:.1f}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

    # Show channel averages
    b_avg = frame[:,:,0].mean()
    g_avg = frame[:,:,1].mean()
    r_avg = frame[:,:,2].mean()
    cv2.putText(frame, f"Avg R={r_avg:.0f} G={g_avg:.0f} B={b_avg:.0f}", (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

    cv2.imshow("Color Tune", frame)
    key = cv2.waitKey(50) & 0xFF

    if key == ord('q') or key == 27:
        break
    elif key == ord('s'):
        print(f"\n  Current gains: Red={r_gain:.1f}  Blue={b_gain:.1f}")
        print(f"  Channel avgs:  R={r_avg:.0f}  G={g_avg:.0f}  B={b_avg:.0f}")
        print(f"\n  Put in config.py:")
        print(f'    CAMERA_AWB_MODE = "manual"')
        print(f"    CAMERA_COLOUR_GAINS = ({r_gain:.1f}, {b_gain:.1f})")
        print()

cam.close()
cv2.destroyAllWindows()
