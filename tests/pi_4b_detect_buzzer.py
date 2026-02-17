#!/usr/bin/env python3
"""
Pi Test 4b: Camera + AI + Cube buzzer — like pi_2 but with beep.

Same display as pi_2 (picamera2 support, live view) but adds:
  - Cube connection + buzzer beep on detection
  - Guidance commands (LEFT, RIGHT, CENTRED)
  - CSV logging of detections

Requires mavproxy running in another terminal.

Usage:
    python tests/pi_4b_detect_buzzer.py             # with display (Pi monitor)
    python tests/pi_4b_detect_buzzer.py --headless   # no display (SSH)
"""
import sys
import os
import csv
import time
import math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

headless = "--headless" in sys.argv

import cv2
import numpy as np

# ==========================================
#   STEP A: Open camera (same as pi_2)
# ==========================================
cap = None
picam = None
source = None

cap = cv2.VideoCapture(0)
if cap.isOpened():
    ret, _ = cap.read()
    if ret:
        source = "OpenCV"
        print(f"[OK] Camera: OpenCV")
    else:
        cap.release()
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
        source = "picamera2"
        print(f"[OK] Camera: picamera2")
    except Exception as e:
        print(f"[FAIL] No camera: {e}")
        sys.exit(1)

def get_frame():
    if source == "OpenCV":
        ret, frame = cap.read()
        return frame if ret else None
    else:
        frame = picam.capture_array()
        return cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

# ==========================================
#   STEP B: Load AI model (from vision.py)
# ==========================================
from vision import VisionSystem
eyes = VisionSystem(camera_index=None, model_path="best.tflite")

if not eyes.using_ai:
    print("[FAIL] AI model did not load. Is best.tflite in project root?")
    sys.exit(1)

backend = "TFLite" if eyes._use_tflite_direct else "Ultralytics"
print(f"[OK] AI Model: {backend}")

# ==========================================
#   STEP C: Connect to Cube + buzzer
# ==========================================
from pymavlink import mavutil
import config
conn_str = config.CONNECTION_STR

print(f"[CUBE] Connecting: {conn_str}")
mav = mavutil.mavlink_connection(conn_str)
print("[CUBE] Waiting for heartbeat...")
mav.wait_heartbeat(timeout=10)
print(f"[CUBE] Connected to system {mav.target_system}")

def beep(tune="MFT200L8CDEF"):
    try:
        mav.mav.play_tune_send(
            mav.target_system, mav.target_component,
            tune.encode(), b""
        )
    except Exception:
        pass

# Test buzzer
beep("MFT200L8CDE")
print("[CUBE] Buzzer test - you should hear a short tune")

# ==========================================
#   STEP D: Guidance + logging setup
# ==========================================
CENTRE_X = 320
CENTRE_Y = 240
CENTRE_THRESHOLD = 50

def get_guidance(px, py):
    dx = px - CENTRE_X
    dy = py - CENTRE_Y
    cmds = []
    if abs(dx) > CENTRE_THRESHOLD:
        cmds.append("RIGHT" if dx > 0 else "LEFT")
    if abs(dy) > CENTRE_THRESHOLD:
        cmds.append("BACK" if dy > 0 else "FORWARD")
    if not cmds:
        cmds.append("CENTRED")
    return " + ".join(cmds), "CENTRED" in cmds

log_path = "detection_log.csv"
write_header = not os.path.exists(log_path)
log_file = open(log_path, "a", newline="")
writer = csv.writer(log_file)
if write_header:
    writer.writerow(["timestamp", "lat", "lon", "alt_m", "yaw_deg",
                     "pitch_deg", "roll_deg", "confidence", "pixel_x", "pixel_y"])

# ==========================================
#   STEP E: Live detection loop (pi_2 style + buzzer)
# ==========================================
if headless:
    print(f"\nRunning HEADLESS. Buzzer beeps on detection. Ctrl+C to quit.\n")
else:
    print(f"\nRunning with display + buzzer. Press 'q' to quit.\n")

frame_count = 0
detect_count = 0
total_ms = 0
last_beep_time = 0

try:
    while True:
        frame = get_frame()
        if frame is None:
            continue

        frame_count += 1

        start = time.time()
        found, x, y, conf = eyes.detect_in_image(frame)
        elapsed_ms = (time.time() - start) * 1000
        total_ms += elapsed_ms

        if found:
            detect_count += 1

        # Display overlay (same as pi_2)
        avg_ms = total_ms / frame_count
        fps = 1000.0 / avg_ms if avg_ms > 0 else 0
        cv2.putText(frame, f"{backend} | {elapsed_ms:.0f}ms | {fps:.1f}fps",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        cv2.putText(frame, f"Detections: {detect_count}/{frame_count}",
                    (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

        if found:
            guidance, centred = get_guidance(x, y)
            color = (0, 255, 0) if centred else (0, 165, 255)
            action = "CENTRED - DESCEND" if centred else guidance

            cv2.putText(frame, f"TARGET ({conf:.2f}) at ({x},{y})",
                        (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(frame, f">> {action}",
                        (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

            # Beep (max once per second)
            now = time.time()
            if now - last_beep_time > 1.0:
                beep("MFT200L8CDEF")
                last_beep_time = now

                # Log detection with Cube data
                gps_msg = mav.recv_match(type='GLOBAL_POSITION_INT', blocking=False)
                att_msg = mav.recv_match(type='ATTITUDE', blocking=False)
                lat = gps_msg.lat / 1e7 if gps_msg else 0.0
                lon = gps_msg.lon / 1e7 if gps_msg else 0.0
                alt = gps_msg.relative_alt / 1000.0 if gps_msg else 0.0
                yaw = math.degrees(att_msg.yaw) if att_msg else 0.0
                pitch = math.degrees(att_msg.pitch) if att_msg else 0.0
                roll = math.degrees(att_msg.roll) if att_msg else 0.0

                timestamp = time.strftime("%H:%M:%S")
                writer.writerow([timestamp, f"{lat:.7f}", f"{lon:.7f}", f"{alt:.1f}",
                                 f"{yaw:.1f}", f"{pitch:.1f}", f"{roll:.1f}",
                                 f"{conf:.3f}", x, y])
                log_file.flush()

                gps_str = f"GPS=({lat:.7f}, {lon:.7f})" if lat != 0 else "GPS=(no fix)"
                print(f"  [{timestamp}] DETECTED #{detect_count}  conf={conf:.2f}  "
                      f">> {action}  {gps_str}  yaw={yaw:.0f}")

        if headless:
            if not found and frame_count % 100 == 0:
                print(f"  ... {frame_count} frames, {detect_count} detections")
        else:
            cv2.imshow("Pi Detection + Buzzer Test", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                cv2.imwrite("pi_detect_frame.jpg", frame)
                print(f"  Saved: pi_detect_frame.jpg")

except KeyboardInterrupt:
    print("\nStopping...")

# Cleanup
log_file.close()
if cap:
    cap.release()
if picam:
    picam.stop()
cv2.destroyAllWindows()

avg_ms = total_ms / max(1, frame_count)
print(f"\n{'=' * 45}")
print(f"  RESULTS")
print(f"{'=' * 45}")
print(f"  Frames:     {frame_count}")
print(f"  Detections: {detect_count}")
print(f"  Avg time:   {avg_ms:.0f}ms per frame")
print(f"  Log saved:  {log_path}")
print()
