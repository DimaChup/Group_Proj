#!/usr/bin/env python3
"""
pi_passive_flight.py — Passive Detection During Manual Flight
=============================================================
Pilot flies manually on RC. Pi watches with camera + AI.
Flags detections on screen + buzzer. Logs everything. Sends ZERO commands.

What it shows:
  - Live camera feed with AI overlay
  - Current altitude from Cube
  - Expected dummy size at current altitude
  - Detection alerts (screen flash + buzzer)
  - GPS position, attitude, battery
  - Detection log saved to CSV

Controls:
  'q' / ESC — quit
  's' — save current frame as snapshot

Usage:
    python tests/pi_passive_flight.py                    # with screen
    python tests/pi_passive_flight.py --headless         # terminal only (SSH)
"""

import sys
import os
import csv
import time
import math

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

import cv2
import numpy as np
import config

HEADLESS = "--headless" in sys.argv


# ── Altitude / FOV math (same as simulation.py) ─────────────────────────

def calc_fov():
    return 2 * math.atan(config.SENSOR_WIDTH_MM / (2 * config.FOCAL_LENGTH_MM))

def ground_width_at_alt(alt_m):
    """Width of ground visible (meters) at given altitude."""
    return 2 * max(1.0, alt_m) * math.tan(calc_fov() / 2)

def dummy_pixels_at_alt(alt_m):
    """Expected dummy height in pixels at given altitude."""
    gw = ground_width_at_alt(alt_m)
    px_per_m = config.IMAGE_W / gw
    return int(config.DUMMY_HEIGHT_M * px_per_m)


# ── Cube connection (read-only) ──────────────────────────────────────────

def connect_cube():
    """Connect to Cube for telemetry. Returns mavlink connection or None."""
    try:
        from pymavlink import mavutil
    except ImportError:
        print("[CUBE] pymavlink not installed — running without Cube data")
        return None

    conn_str = config.CONNECTION_STR
    baud = config.BAUD_RATE
    print(f"[CUBE] Connecting: {conn_str} (baud={baud})")

    try:
        if conn_str.startswith("/dev/"):
            mav = mavutil.mavlink_connection(conn_str, baud=baud)
        else:
            mav = mavutil.mavlink_connection(conn_str)

        print("[CUBE] Waiting for heartbeat...")
        mav.wait_heartbeat(timeout=10)
        print(f"[CUBE] Connected (system {mav.target_system})")

        # Request data streams
        mav.mav.request_data_stream_send(
            mav.target_system, mav.target_component,
            0, 4, 1  # ALL streams at 4 Hz
        )
        return mav
    except Exception as e:
        print(f"[CUBE] Connection failed: {e} — running without Cube data")
        return None


def beep(mav, tune="MFT200L8CDEC"):
    """Play tune on Cube buzzer."""
    if mav is None:
        return
    try:
        mav.mav.play_tune_send(
            mav.target_system, mav.target_component,
            tune.encode(), b""
        )
    except Exception:
        pass


def read_telemetry(mav):
    """Read latest telemetry from Cube. Non-blocking."""
    data = {
        "alt": 0.0, "lat": 0.0, "lon": 0.0,
        "yaw": 0.0, "pitch": 0.0, "roll": 0.0,
        "groundspeed": 0.0, "battery_v": 0.0, "battery_pct": -1,
        "gps_fix": 0, "gps_sats": 0,
    }
    if mav is None:
        return data

    # Drain messages and keep latest of each type
    while True:
        msg = mav.recv_match(blocking=False)
        if msg is None:
            break
        mtype = msg.get_type()
        if mtype == "GLOBAL_POSITION_INT":
            data["lat"] = msg.lat / 1e7
            data["lon"] = msg.lon / 1e7
            data["alt"] = msg.relative_alt / 1000.0
        elif mtype == "ATTITUDE":
            data["yaw"] = math.degrees(msg.yaw)
            data["pitch"] = math.degrees(msg.pitch)
            data["roll"] = math.degrees(msg.roll)
        elif mtype == "VFR_HUD":
            data["groundspeed"] = msg.groundspeed
            data["alt"] = msg.alt  # backup altitude source
        elif mtype == "SYS_STATUS":
            data["battery_v"] = msg.voltage_battery / 1000.0
            if msg.battery_remaining >= 0:
                data["battery_pct"] = msg.battery_remaining
        elif mtype == "GPS_RAW_INT":
            data["gps_fix"] = msg.fix_type
            data["gps_sats"] = msg.satellites_visible

    return data


# ── Main ─────────────────────────────────────────────────────────────────

def main():
    print("=" * 55)
    print("  PASSIVE FLIGHT MODE — Camera + AI, No Control")
    print("  Pilot flies manually. Pi watches and logs.")
    print("=" * 55)
    print()

    # Connect Cube (read-only)
    mav = connect_cube()
    if mav:
        beep(mav, "MFT200L8CDE")

    # Start camera + AI
    from vision import VisionSystem
    eyes = VisionSystem(camera_index=0,
                        model_path=os.path.join(project_root, "best.tflite"))
    if not eyes.using_ai:
        print("[WARN] AI model not loaded — camera only, no detection")

    # Log file
    log_path = os.path.join(project_root, "passive_flight_log.csv")
    write_header = not os.path.exists(log_path)
    log_file = open(log_path, "a", newline="")
    writer = csv.writer(log_file)
    if write_header:
        writer.writerow([
            "time", "flight_sec", "lat", "lon", "alt_m",
            "yaw", "pitch", "roll", "groundspeed",
            "detection", "confidence", "pixel_x", "pixel_y",
            "guidance", "dummy_expected_px", "battery_v", "battery_pct"
        ])

    if not HEADLESS:
        cv2.namedWindow("Passive Flight", cv2.WINDOW_NORMAL)

    print(f"\n[READY] Logging to: {log_path}")
    print("[READY] Pilot can take off. Press Ctrl+C or 'q' to stop.\n")

    # Stats
    t_start = time.time()
    frame_count = 0
    detect_count = 0
    last_detect_time = 0
    last_beep_time = 0
    fps_t0 = time.time()
    fps_count = 0
    fps = 0.0
    snapshot_count = 0

    # Log rate control (1 row per second even when no detection)
    last_log_time = 0

    # On-screen event log (scrolling list of recent events)
    event_log = []  # list of (time_str, message, colour_bgr)
    MAX_EVENTS = 8  # how many lines to show on screen

    try:
        while True:
            frame = eyes.get_frame()
            if frame is None:
                time.sleep(0.05)
                continue

            # Flip 180° — camera is mounted inverted on the drone
            frame = cv2.flip(frame, -1)

            frame_count += 1
            fps_count += 1
            now = time.time()
            flight_sec = now - t_start

            # FPS
            if now - fps_t0 >= 1.0:
                fps = fps_count / (now - fps_t0)
                fps_count = 0
                fps_t0 = now

            # Telemetry
            telem = read_telemetry(mav)
            alt = telem["alt"]
            dummy_px = dummy_pixels_at_alt(alt) if alt > 1 else 0

            # Detection
            found = False
            conf = 0.0
            px, py = 0, 0
            guidance = ""
            if eyes.using_ai:
                found, px, py, conf = eyes.detect_in_image(frame)

            if found:
                detect_count += 1
                last_detect_time = now

                # ── Guidance: where should drone move to center target? ──
                img_h, img_w = frame.shape[:2]
                cx, cy = img_w / 2, img_h / 2
                off_x = (px - cx) / (img_w / 2)   # -1 (left) to +1 (right)
                off_y = (py - cy) / (img_h / 2)    # -1 (top/forward) to +1 (bottom/back)

                DEAD_ZONE = 0.15  # 15% of half-frame = "close enough to centered"
                dirs = []
                if off_x < -DEAD_ZONE:
                    dirs.append("LEFT")
                elif off_x > DEAD_ZONE:
                    dirs.append("RIGHT")
                if off_y < -DEAD_ZONE:
                    dirs.append("FORWARD")
                elif off_y > DEAD_ZONE:
                    dirs.append("BACK")

                if not dirs:
                    guidance = "CENTRED"
                else:
                    guidance = "+".join(dirs)

                # Event log entry
                ts = time.strftime("%H:%M:%S")
                gps_short = (f"({telem['lat']:.5f},{telem['lon']:.5f})"
                             if telem['lat'] != 0 else "(no GPS)")
                event_log.append((
                    ts,
                    f"DETECT #{detect_count}  conf={conf:.2f}  alt={alt:.1f}m  → {guidance}  {gps_short}",
                    (0, 255, 0)
                ))
                if len(event_log) > MAX_EVENTS:
                    event_log.pop(0)

                # Buzzer (max once per 2 seconds)
                if mav and now - last_beep_time > 2.0:
                    beep(mav, "MFT200L16CDEFG")
                    last_beep_time = now

            # Log (detections immediately, telemetry once per second)
            if found or (now - last_log_time >= 1.0):
                writer.writerow([
                    time.strftime("%H:%M:%S"), f"{flight_sec:.1f}",
                    f"{telem['lat']:.7f}", f"{telem['lon']:.7f}", f"{alt:.1f}",
                    f"{telem['yaw']:.1f}", f"{telem['pitch']:.1f}", f"{telem['roll']:.1f}",
                    f"{telem['groundspeed']:.1f}",
                    "YES" if found else "no",
                    f"{conf:.3f}" if found else "",
                    px if found else "", py if found else "",
                    guidance if found else "",
                    dummy_px,
                    f"{telem['battery_v']:.1f}", telem['battery_pct']
                ])
                log_file.flush()
                last_log_time = now

            # ── Display ──
            if HEADLESS:
                if found:
                    print(f"  ** DETECTED ** conf={conf:.2f} at ({px},{py})  "
                          f"→ {guidance}  alt={alt:.1f}m  GPS=({telem['lat']:.6f},{telem['lon']:.6f})")
                elif frame_count % 60 == 0:
                    bat_str = (f"{telem['battery_pct']}%"
                               if telem['battery_pct'] >= 0
                               else f"{telem['battery_v']:.1f}V")
                    print(f"  scanning... {frame_count} frames  {detect_count} detections  "
                          f"alt={alt:.1f}m  spd={telem['groundspeed']:.1f}  bat={bat_str}")
            else:
                h, w = frame.shape[:2]

                # Detection alert — flash border + guidance
                recently_detected = (now - last_detect_time) < 1.0
                if recently_detected:
                    cv2.rectangle(frame, (0, 0), (w - 1, h - 1), (0, 255, 0), 6)
                    cv2.putText(frame, "TARGET DETECTED", (w // 2 - 140, 40),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

                    # Guidance direction
                    if guidance:
                        guide_color = (0, 255, 255) if guidance != "CENTRED" else (0, 255, 0)
                        cv2.putText(frame, f"MOVE: {guidance}", (w // 2 - 100, h // 2 - 20),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 4)
                        cv2.putText(frame, f"MOVE: {guidance}", (w // 2 - 100, h // 2 - 20),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, guide_color, 2)

                    # Draw crosshair at center + line to target
                    cv2.drawMarker(frame, (w // 2, h // 2), (255, 255, 255),
                                   cv2.MARKER_CROSS, 30, 1)
                    if found and px > 0 and py > 0:
                        cv2.circle(frame, (int(px), int(py)), 10, (0, 255, 0), 2)
                        cv2.line(frame, (w // 2, h // 2), (int(px), int(py)),
                                 (0, 255, 255), 2)

                # Info bar at bottom
                bar_y = h - 70
                cv2.rectangle(frame, (0, bar_y), (w, h), (0, 0, 0), -1)

                # Row 1: altitude + expected size
                alt_str = f"Alt: {alt:.1f}m" if alt > 0.5 else "Alt: ground"
                if dummy_px > 0:
                    alt_str += f"  (dummy ~{dummy_px}px)"
                cv2.putText(frame, alt_str, (10, bar_y + 18),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

                # GPS
                if telem["lat"] != 0:
                    gps_str = f"GPS: {telem['lat']:.6f}, {telem['lon']:.6f}"
                else:
                    fix_names = {0: "no GPS", 1: "no fix", 2: "2D", 3: "3D"}
                    gps_str = f"GPS: {fix_names.get(telem['gps_fix'], '?')} ({telem['gps_sats']} sats)"
                cv2.putText(frame, gps_str, (320, bar_y + 18),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

                # Row 2: speed, battery, stats
                spd_str = f"Spd: {telem['groundspeed']:.1f}m/s"
                if telem["battery_pct"] >= 0:
                    bat_str = f"Bat: {telem['battery_pct']}% ({telem['battery_v']:.1f}V)"
                else:
                    bat_str = f"Bat: {telem['battery_v']:.1f}V"
                stats_str = f"Det: {detect_count}  Frames: {frame_count}"
                cv2.putText(frame, spd_str, (10, bar_y + 42),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
                cv2.putText(frame, bat_str, (200, bar_y + 42),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
                cv2.putText(frame, stats_str, (430, bar_y + 42),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

                # Row 3: FPS + flight time
                mins = int(flight_sec) // 60
                secs = int(flight_sec) % 60
                cv2.putText(frame, f"{fps:.0f} FPS  |  {mins}:{secs:02d} flight",
                            (10, bar_y + 62),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (150, 150, 150), 1)

                # Attitude
                cv2.putText(frame, f"Y:{telem['yaw']:.0f} P:{telem['pitch']:.0f} R:{telem['roll']:.0f}",
                            (430, bar_y + 62),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (150, 150, 150), 1)

                # Event log panel (right side, scrolling up)
                if event_log:
                    log_x = 10
                    log_y_start = 60 if recently_detected else 30
                    for i, (ets, emsg, ecol) in enumerate(event_log):
                        y_pos = log_y_start + i * 20
                        text = f"{ets} {emsg}"
                        # Shadow for readability
                        cv2.putText(frame, text, (log_x + 1, y_pos + 1),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 2)
                        cv2.putText(frame, text, (log_x, y_pos),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, ecol, 1)

                cv2.imshow("Passive Flight", frame)

                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == 27:
                    break
                elif key == ord('s'):
                    snapshot_count += 1
                    snap_path = os.path.join(project_root, f"snapshot_{snapshot_count:03d}.jpg")
                    cv2.imwrite(snap_path, frame)
                    print(f"  [SNAP] Saved: {snap_path}")

    except KeyboardInterrupt:
        print("\nStopping...")

    # Cleanup
    log_file.close()
    eyes.release()
    if not HEADLESS:
        cv2.destroyAllWindows()

    # Final summary
    flight_min = (time.time() - t_start) / 60
    print()
    print("=" * 55)
    print("  FLIGHT SUMMARY")
    print("=" * 55)
    print(f"  Flight time:  {flight_min:.1f} minutes")
    print(f"  Frames:       {frame_count}")
    print(f"  Detections:   {detect_count}")
    if frame_count > 0:
        print(f"  Detection rate: {100 * detect_count / frame_count:.1f}%")
    print(f"  Log saved:    {log_path}")
    print("=" * 55)


if __name__ == "__main__":
    main()
