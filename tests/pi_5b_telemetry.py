#!/usr/bin/env python3
"""
Pi Test 5b: The full bench test — everything combined.

Builds on pi_4b. Camera + AI + Cube buzzer + guidance + LIVE telemetry.
Everything from previous tests in one script:
  - pi_1: Camera feed (picamera2 or OpenCV)
  - pi_2: AI detection overlay on live feed
  - pi_3b: Buzzer beep on detection
  - pi_4b: Guidance commands + CSV logging
  - NEW:  Live Cube telemetry displayed continuously (alt, GPS, yaw, pitch, roll, battery)

Carry the drone over a dummy printout. The display shows everything at once:
  Top:    AI stats (backend, inference time, FPS)
  Middle: Detection info + guidance commands
  Bottom: LIVE Cube telemetry (altitude, GPS, attitude, battery)

On detection: buzzer beeps + telemetry logged to CSV.

Requires mavproxy running in another terminal.

Usage:
    python tests/pi_5b_telemetry.py             # with display (Pi monitor)
    python tests/pi_5b_telemetry.py --headless   # no display (SSH)
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

# Request higher data rate
try:
    mav.mav.request_data_stream_send(
        mav.target_system, mav.target_component,
        mavutil.mavlink.MAV_DATA_STREAM_ALL, 10, 1
    )
except Exception:
    pass

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
#   STEP D: Guidance + logging + telemetry
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

# Live telemetry state (updated every frame)
telem = {
    "lat": 0.0, "lon": 0.0, "alt_rel": 0.0, "alt_msl": 0.0,
    "yaw": 0.0, "pitch": 0.0, "roll": 0.0,
    "voltage": 0.0, "fix": "No GPS", "sats": 0,
    "ground_speed": 0.0, "hdg": 0.0,
}

def update_telemetry():
    """Drain all pending messages, then read latest of each type from mav.messages."""
    # Drain the buffer — processes ALL pending messages so mav.messages stays current
    while True:
        msg = mav.recv_msg()
        if msg is None:
            break

    # Read latest of each type from the message cache
    gps = mav.messages.get('GLOBAL_POSITION_INT')
    if gps:
        telem["lat"] = gps.lat / 1e7
        telem["lon"] = gps.lon / 1e7
        telem["alt_msl"] = gps.alt / 1000.0
        telem["alt_rel"] = gps.relative_alt / 1000.0
        vx = gps.vx / 100.0
        vy = gps.vy / 100.0
        telem["ground_speed"] = math.sqrt(vx**2 + vy**2)
        telem["hdg"] = gps.hdg / 100.0 if gps.hdg != 65535 else 0.0

    att = mav.messages.get('ATTITUDE')
    if att:
        telem["yaw"] = math.degrees(att.yaw)
        telem["pitch"] = math.degrees(att.pitch)
        telem["roll"] = math.degrees(att.roll)

    bat = mav.messages.get('SYS_STATUS')
    if bat:
        telem["voltage"] = bat.voltage_battery / 1000.0

    gps_raw = mav.messages.get('GPS_RAW_INT')
    if gps_raw:
        fix_names = {0: "No GPS", 1: "No Fix", 2: "2D", 3: "3D",
                     4: "DGPS", 5: "RTK Float", 6: "RTK Fixed"}
        telem["fix"] = fix_names.get(gps_raw.fix_type, f"Type {gps_raw.fix_type}")
        telem["sats"] = gps_raw.satellites_visible

# ==========================================
#   STEP E: Live loop — everything combined
# ==========================================
if headless:
    print(f"\nRunning HEADLESS. Live telemetry + detection + buzzer. Ctrl+C to quit.\n")
else:
    print(f"\nRunning with display. Press 'q' to quit, 's' to save frame.\n")

frame_count = 0
detect_count = 0
total_ms = 0
last_beep_time = 0
last_telem_print = 0

try:
    while True:
        frame = get_frame()
        if frame is None:
            continue

        frame_count += 1

        # Update telemetry from Cube (non-blocking, every frame)
        update_telemetry()

        # Run AI detection
        start = time.time()
        found, x, y, conf = eyes.detect_in_image(frame)
        elapsed_ms = (time.time() - start) * 1000
        total_ms += elapsed_ms

        if found:
            detect_count += 1

        # --- OVERLAY: AI stats (top) ---
        avg_ms = total_ms / frame_count
        fps = 1000.0 / avg_ms if avg_ms > 0 else 0
        cv2.putText(frame, f"{backend} | {elapsed_ms:.0f}ms | {fps:.1f}fps",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        cv2.putText(frame, f"Detections: {detect_count}/{frame_count}",
                    (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

        # --- OVERLAY: Detection + guidance (middle) ---
        if found:
            guidance, centred = get_guidance(x, y)
            color = (0, 255, 0) if centred else (0, 165, 255)
            action = "CENTRED - DESCEND" if centred else guidance

            cv2.putText(frame, f"TARGET ({conf:.2f}) at ({x},{y})",
                        (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(frame, f">> {action}",
                        (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

            # Beep + log (max once per second)
            now = time.time()
            if now - last_beep_time > 1.0:
                beep("MFT200L8CDEF")
                last_beep_time = now

                timestamp = time.strftime("%H:%M:%S")
                writer.writerow([timestamp,
                                 f"{telem['lat']:.7f}", f"{telem['lon']:.7f}",
                                 f"{telem['alt_rel']:.1f}",
                                 f"{telem['yaw']:.1f}", f"{telem['pitch']:.1f}",
                                 f"{telem['roll']:.1f}",
                                 f"{conf:.3f}", x, y])
                log_file.flush()

                gps_str = f"GPS=({telem['lat']:.7f}, {telem['lon']:.7f})" if telem['lat'] != 0 else "GPS=(no fix)"
                print(f"  [{timestamp}] DETECTED #{detect_count}  conf={conf:.2f}  "
                      f">> {action}  {gps_str}  alt={telem['alt_rel']:.1f}m  yaw={telem['yaw']:.0f}")

        # --- OVERLAY: Live telemetry (bottom of frame) ---
        t = telem
        gps_line = f"GPS: ({t['lat']:.7f}, {t['lon']:.7f})  {t['fix']} {t['sats']}sats"
        alt_line = f"Alt: {t['alt_rel']:.1f}m rel  {t['alt_msl']:.1f}m MSL  Spd: {t['ground_speed']:.1f}m/s"
        att_line = f"Yaw:{t['yaw']:.0f}  Pitch:{t['pitch']:.1f}  Roll:{t['roll']:.1f}  Bat:{t['voltage']:.1f}V"

        # Dark background strip for readability
        cv2.rectangle(frame, (0, 390), (640, 480), (0, 0, 0), -1)
        cv2.putText(frame, gps_line,
                    (10, 415), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        cv2.putText(frame, alt_line,
                    (10, 440), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        cv2.putText(frame, att_line,
                    (10, 465), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

        # --- Headless mode: print telemetry periodically ---
        if headless:
            now = time.time()
            if now - last_telem_print > 2.0:
                last_telem_print = now
                timestamp = time.strftime("%H:%M:%S")
                gps_str = f"({t['lat']:.7f}, {t['lon']:.7f})" if t['lat'] != 0 else "(no fix)"
                print(f"  [{timestamp}] f={frame_count} d={detect_count}  "
                      f"Alt={t['alt_rel']:.1f}m  Yaw={t['yaw']:.0f}  "
                      f"P={t['pitch']:.1f} R={t['roll']:.1f}  "
                      f"GPS={gps_str}  Bat={t['voltage']:.1f}V")
        else:
            cv2.imshow("Pi Full Bench Test", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                cv2.imwrite("pi_bench_frame.jpg", frame)
                print(f"  Saved: pi_bench_frame.jpg")

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
print(f"\n{'=' * 50}")
print(f"  RESULTS — Full Bench Test")
print(f"{'=' * 50}")
print(f"  Frames:     {frame_count}")
print(f"  Detections: {detect_count}")
print(f"  Avg time:   {avg_ms:.0f}ms per frame")
print(f"  Last alt:   {telem['alt_rel']:.1f}m relative")
print(f"  Last yaw:   {telem['yaw']:.0f} deg")
print(f"  Battery:    {telem['voltage']:.1f}V")
print(f"  Log saved:  {log_path}")
print()
