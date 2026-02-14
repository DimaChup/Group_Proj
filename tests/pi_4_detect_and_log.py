#!/usr/bin/env python3
"""
Pi Test 4: Camera + AI + Cube - the full bench test.

Carry the drone by hand over a dummy printout. This script does everything:
  1. Detects the dummy with CV
  2. Reads Cube data (GPS, yaw, altitude)
  3. Buzzer beeps on detection
  4. Logs everything to CSV
  5. Shows guidance commands (go LEFT, RIGHT, CENTRED - DESCEND)

This is the final bench test before actual flight.

Usage:
    python tests/pi_4_detect_and_log.py                    # auto-detect serial
    python tests/pi_4_detect_and_log.py /dev/ttyAMA0 57600 # manual
"""
import sys
import os
import csv
import time
import math
import struct

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    # --- Parse args ---
    conn_str = None
    baud = 57600
    if len(sys.argv) >= 2:
        conn_str = sys.argv[1]
    if len(sys.argv) >= 3:
        baud = int(sys.argv[2])

    # --- Auto-detect connection if not specified ---
    if conn_str is None:
        try:
            import config
            conn_str = config.CONNECTION_STR
            baud = config.BAUD_RATE
        except Exception:
            for port in ["/dev/ttyAMA0", "/dev/ttyACM0", "/dev/ttyUSB0"]:
                if os.path.exists(port):
                    conn_str = port
                    break
            if conn_str is None:
                conn_str = "tcp:127.0.0.1:5762"

    # --- Connect to Cube ---
    print(f"[CUBE] Connecting: {conn_str} (baud={baud})")
    from pymavlink import mavutil
    if conn_str.startswith("/dev/"):
        mav = mavutil.mavlink_connection(conn_str, baud=baud)
    else:
        mav = mavutil.mavlink_connection(conn_str)

    print("[CUBE] Waiting for heartbeat...")
    mav.wait_heartbeat(timeout=10)
    print(f"[CUBE] Heartbeat OK (system {mav.target_system})")

    # --- Buzzer function ---
    def beep(tune="MFT200L8CDEC"):
        """Play a tune on the Cube's built-in buzzer via MAVLink PLAY_TUNE."""
        try:
            mav.mav.play_tune_send(
                mav.target_system, mav.target_component,
                tune.encode(),
                b""
            )
        except Exception:
            pass

    # Test buzzer on startup
    beep("MFT200L8CDE")
    print("[CUBE] Buzzer test - you should hear a short tune")

    # --- Start camera + AI ---
    from vision import VisionSystem
    vs = VisionSystem(camera_index=0, model_path="best.tflite")
    if not vs.using_ai:
        print("[ERROR] AI model not loaded. Is best.tflite in project root?")
        return

    # --- Log file ---
    log_path = "detection_log.csv"
    write_header = not os.path.exists(log_path)
    log_file = open(log_path, "a", newline="")
    writer = csv.writer(log_file)
    if write_header:
        writer.writerow(["timestamp", "lat", "lon", "alt_m", "yaw_deg", "pitch_deg", "roll_deg", "confidence", "pixel_x", "pixel_y"])

    # --- Guidance settings ---
    CENTRE_X = 320  # frame centre
    CENTRE_Y = 240
    CENTRE_THRESHOLD = 50  # pixels

    def get_guidance(px, py):
        """Return directional command based on where target is in frame."""
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

    print(f"\n[READY] Watching for targets. Logging to {log_path}")
    print("[READY] Carry drone over dummy. Follow guidance commands.")
    print("[READY] Press Ctrl+C to stop.\n")

    detections = 0
    frames = 0
    last_detection_time = 0

    try:
        while True:
            frame = vs.get_frame()
            if frame is None:
                time.sleep(0.1)
                continue

            frames += 1
            found, px, py, conf = vs.detect_in_image(frame)

            if found:
                now = time.time()
                # Avoid logging the same detection repeatedly (1s cooldown)
                if now - last_detection_time < 1.0:
                    continue
                last_detection_time = now

                # Read GPS from Cube (may be 0,0 indoors - that's fine)
                gps_msg = mav.recv_match(type='GLOBAL_POSITION_INT', blocking=True, timeout=2)
                if gps_msg:
                    lat = gps_msg.lat / 1e7
                    lon = gps_msg.lon / 1e7
                    alt = gps_msg.relative_alt / 1000.0
                else:
                    lat, lon, alt = 0.0, 0.0, 0.0

                # Read attitude (yaw/pitch/roll - always available, even indoors)
                att_msg = mav.recv_match(type='ATTITUDE', blocking=True, timeout=2)
                if att_msg:
                    yaw = math.degrees(att_msg.yaw)
                    pitch = math.degrees(att_msg.pitch)
                    roll = math.degrees(att_msg.roll)
                else:
                    yaw, pitch, roll = 0.0, 0.0, 0.0

                detections += 1
                timestamp = time.strftime("%H:%M:%S")
                writer.writerow([timestamp, f"{lat:.7f}", f"{lon:.7f}", f"{alt:.1f}",
                                 f"{yaw:.1f}", f"{pitch:.1f}", f"{roll:.1f}",
                                 f"{conf:.3f}", px, py])
                log_file.flush()

                # Guidance command
                guidance, centred = get_guidance(px, py)

                # Beep the Cube buzzer
                beep("MFT200L8CDEF")

                gps_str = f"GPS=({lat:.7f}, {lon:.7f})" if lat != 0 else "GPS=(no fix)"
                action = ">> CENTRED - DESCEND" if centred else f">> {guidance}"
                print(f"  [{timestamp}] DETECTED #{detections}  conf={conf:.2f}  "
                      f"{action}  {gps_str}  yaw={yaw:.0f}")
            else:
                if frames % 100 == 0:
                    print(f"  ... {frames} frames scanned, {detections} detections so far")

    except KeyboardInterrupt:
        print(f"\n[DONE] {detections} detections logged from {frames} frames.")
        print(f"[DONE] Log saved to {log_path}")
    finally:
        log_file.close()
        vs.release()

if __name__ == "__main__":
    main()
