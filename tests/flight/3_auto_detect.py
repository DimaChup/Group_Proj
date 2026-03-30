#!/usr/bin/env python3
"""
Auto Detect — Mission Planner AUTO waypoints + AI detection + GUIDED hover.

WHAT:    Monitors camera with AI while the drone flies AUTO waypoints uploaded via
         Mission Planner. When the AI detects the target with sufficient confidence
         for N consecutive frames, switches from AUTO to GUIDED mode, calculates
         target GPS from pixel position, and sends position commands to center and
         hover above the target. After a timeout (or 'r' key), resumes AUTO waypoints.
         No descent or landing — hover only.
WHY:     Safe intermediate step between passive observation (step 1) and full autonomous
         mission (main.py). Tests the critical AUTO-to-GUIDED mode switch and GPS
         estimation from pixel detection in real flight, without the risk of descent
         or landing logic.
WHEN:    After waypoint flight (step 2) proves navigation works. Before full autonomous
         detect-and-center (step 4). Requires waypoints uploaded in Mission Planner.
WHERE:   Pi (with camera + Cube via mavproxy, outdoors). Also works on laptop with
         webcam + SITL.
ENV:     pienv on Pi (ai-edge-litert, opencv-headless, pymavlink). Dev venv on laptop.
MODELS:  best.tflite (YOLOv8n TFLite) — loaded via vision.py dual backend.
RISK:    Medium — sends mode switch commands (AUTO to GUIDED) and position hold commands
         when target is detected. Does NOT descend or land autonomously. RC kill switch
         always overrides. Use --dry-run to test detection without any commands.

USAGE:
    python tests/flight/3_auto_detect.py                       # live with screen
    python tests/flight/3_auto_detect.py --headless            # SSH mode
    python tests/flight/3_auto_detect.py --dry-run             # detect only, ZERO commands
    python tests/flight/3_auto_detect.py --timeout 10          # resume AUTO after 10s hover
    python tests/flight/3_auto_detect.py --min-conf 0.5        # higher confidence threshold
    python tests/flight/3_auto_detect.py --min-detections 3    # need 3 consecutive detections

FLAGS:
    --headless          Skip cv2.imshow, terminal output only (for SSH/PuTTY)
    --dry-run           Log detections but send ZERO commands to the Cube
    --timeout N         Auto-resume AUTO after N seconds of hovering (default 15)
    --min-conf N        Minimum detection confidence to trigger (default 0.4)
    --min-detections N  Consecutive detections required before switching (default 2)

OUTPUT:
    - auto_detect_log.csv: timestamped state, mode, GPS, detection, target GPS
    - Terminal: detection events, centering progress, hover countdown
    - OpenCV window (unless --headless): live video with state banner and overlays

BEST PRACTICES:
    - Upload simple waypoints in Mission Planner first, verify AUTO flight works
    - Start with --dry-run to verify detection works in flight before enabling commands
    - Keep RC transmitter ready — flip to STABILIZE to override at any time
    - If pilot takes RC control, script detects mode change and returns to WATCHING state
    - Ctrl+C switches back to AUTO before exiting (safe cleanup)

DEPENDENCIES:
    opencv-python (or opencv-headless), numpy, pymavlink, config.py, vision.py
"""

import sys
import os
import csv
import time
import math

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, project_root)

import cv2
import numpy as np
import config
from pymavlink import mavutil

# ArduCopter mode numbers
COPTER_MODES = {
    0: "STABILIZE", 1: "ACRO", 2: "ALT_HOLD", 3: "AUTO",
    4: "GUIDED", 5: "LOITER", 6: "RTL", 7: "CIRCLE",
    9: "LAND", 11: "DRIFT", 13: "SPORT", 14: "FLIP",
    15: "AUTOTUNE", 16: "POSHOLD", 17: "BRAKE", 18: "THROW",
    19: "AVOID_ADSB", 20: "GUIDED_NOGPS", 21: "SMART_RTL",
}

# --- Parse args ---
HEADLESS = "--headless" in sys.argv
DRY_RUN = "--dry-run" in sys.argv
HOVER_TIMEOUT = 15.0
MIN_CONF = 0.4
MIN_DETECTIONS = 2  # consecutive detections before switching

for i, arg in enumerate(sys.argv):
    if arg == "--timeout" and i + 1 < len(sys.argv):
        HOVER_TIMEOUT = float(sys.argv[i + 1])
    elif arg == "--min-conf" and i + 1 < len(sys.argv):
        MIN_CONF = float(sys.argv[i + 1])
    elif arg == "--min-detections" and i + 1 < len(sys.argv):
        MIN_DETECTIONS = int(sys.argv[i + 1])


# ── Cube connection ──────────────────────────────────────────────────

def connect_cube():
    """Connect to Cube, filter mavproxy GCS heartbeats."""
    conn_str = config.CONNECTION_STR
    baud = config.BAUD_RATE
    print(f"[CUBE] Connecting: {conn_str} (baud={baud})")

    if conn_str.startswith("/dev/"):
        mav = mavutil.mavlink_connection(conn_str, baud=baud)
    else:
        mav = mavutil.mavlink_connection(conn_str)

    print("[CUBE] Waiting for autopilot heartbeat...")
    start = time.time()
    while time.time() - start < 15:
        hb = mav.recv_match(type='HEARTBEAT', blocking=True, timeout=2)
        if hb and hb.type != mavutil.mavlink.MAV_TYPE_GCS:
            mav.target_system = hb.get_srcSystem()
            mav.target_component = hb.get_srcComponent()
            mode_name = COPTER_MODES.get(hb.custom_mode, f"MODE_{hb.custom_mode}")
            print(f"[CUBE] Connected (system {mav.target_system}, mode: {mode_name})")
            break
    else:
        print("[CUBE] No autopilot heartbeat!")
        sys.exit(1)

    # Request data streams
    mav.mav.request_data_stream_send(
        mav.target_system, mav.target_component,
        0, 10, 1  # ALL streams at 10 Hz
    )
    return mav


def get_mode(mav):
    """Get current Cube mode name."""
    msg = mav.messages.get('HEARTBEAT')
    if msg:
        return COPTER_MODES.get(msg.custom_mode, f"MODE_{msg.custom_mode}")
    return "UNKNOWN"


def set_mode(mav, mode_num, mode_name=""):
    """Switch Cube to given mode number."""
    mav.mav.command_long_send(
        mav.target_system, mav.target_component,
        mavutil.mavlink.MAV_CMD_DO_SET_MODE, 0,
        mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
        mode_num, 0, 0, 0, 0, 0
    )
    print(f"[MODE] → {mode_name or COPTER_MODES.get(mode_num, mode_num)}")


def send_position(mav, lat, lon, alt):
    """Send position target (GUIDED mode)."""
    mav.mav.set_position_target_global_int_send(
        0, mav.target_system, mav.target_component,
        mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
        0b110111111000,
        int(lat * 1e7), int(lon * 1e7), alt,
        0, 0, 0, 0, 0, 0, 0, 0
    )


def beep(mav, tune="MFT200L8CDEC"):
    """Play tune on Cube buzzer."""
    try:
        mav.mav.play_tune_send(
            mav.target_system, mav.target_component,
            tune.encode(), b""
        )
    except Exception:
        pass


# ── Telemetry ────────────────────────────────────────────────────────

def read_telemetry(mav):
    """Drain MAVLink messages, return latest telemetry."""
    data = {
        "alt": 0.0, "lat": 0.0, "lon": 0.0,
        "yaw": 0.0, "pitch": 0.0, "roll": 0.0,
        "groundspeed": 0.0, "battery_v": 0.0, "battery_pct": -1,
        "gps_fix": 0, "gps_sats": 0,
    }

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
            data["yaw"] = msg.yaw  # radians
            data["pitch"] = math.degrees(msg.pitch)
            data["roll"] = math.degrees(msg.roll)
        elif mtype == "VFR_HUD":
            data["groundspeed"] = msg.groundspeed
        elif mtype == "SYS_STATUS":
            data["battery_v"] = msg.voltage_battery / 1000.0
            if msg.battery_remaining >= 0:
                data["battery_pct"] = msg.battery_remaining
        elif mtype == "GPS_RAW_INT":
            data["gps_fix"] = msg.fix_type
            data["gps_sats"] = msg.satellites_visible

    return data


# ── GPS from pixel (same math as main.py) ────────────────────────────

def pixel_to_gps(px, py, drone_lat, drone_lon, drone_alt, drone_yaw_rad):
    """Convert pixel detection to GPS coordinate."""
    cx = config.IMAGE_W / 2
    cy = config.IMAGE_H / 2

    # Ground sample distance (meters per pixel)
    gsd = (config.SENSOR_WIDTH_MM * drone_alt) / (config.FOCAL_LENGTH_MM * config.IMAGE_W)

    delta_x_px = px - cx
    delta_y_px = py - cy

    # Camera frame: forward = -y, right = +x
    fwd_m = -delta_y_px * gsd
    right_m = delta_x_px * gsd

    # Rotate by yaw to get north/east offsets
    offset_n = fwd_m * math.cos(drone_yaw_rad) - right_m * math.sin(drone_yaw_rad)
    offset_e = fwd_m * math.sin(drone_yaw_rad) + right_m * math.cos(drone_yaw_rad)

    R_EARTH = 6378137.0
    d_lat = (offset_n / R_EARTH) * (180 / math.pi)
    d_lon = (offset_e / (R_EARTH * math.cos(math.radians(drone_lat)))) * (180 / math.pi)

    return drone_lat + d_lat, drone_lon + d_lon


# ── State ────────────────────────────────────────────────────────────

STATE_WATCHING = "WATCHING"      # Flying AUTO, AI monitoring
STATE_CENTERING = "CENTERING"    # GUIDED, moving to hover over target
STATE_HOVERING = "HOVERING"      # GUIDED, holding position above target
STATE_RESUMING = "RESUMING"      # Switching back to AUTO


# ── Main ─────────────────────────────────────────────────────────────

def main():
    print()
    print("=" * 60)
    if DRY_RUN:
        print("   AUTO DETECT — DRY RUN (no commands sent)")
    else:
        print("   AUTO DETECT — MP waypoints + detect & hover")
    print("=" * 60)
    print()
    print(f"  Min confidence:   {MIN_CONF}")
    print(f"  Min detections:   {MIN_DETECTIONS} consecutive")
    print(f"  Hover timeout:    {HOVER_TIMEOUT}s (then resume AUTO)")
    print(f"  Dry run:          {DRY_RUN}")
    print(f"  Headless:         {HEADLESS}")
    print()

    # Connect Cube
    mav = connect_cube()
    beep(mav, "MFT200L8CDE")

    # Start camera + AI
    from vision import VisionSystem
    eyes = VisionSystem(camera_index=0,
                        model_path=os.path.join(project_root, "best.tflite"))
    if not eyes.using_ai:
        print("[WARN] AI model not loaded!")
        sys.exit(1)

    # Log file
    log_path = os.path.join(project_root, "auto_detect_log.csv")
    write_header = not os.path.exists(log_path)
    log_file = open(log_path, "a", newline="")
    writer = csv.writer(log_file)
    if write_header:
        writer.writerow([
            "time", "state", "mode", "lat", "lon", "alt_m",
            "detection", "confidence", "pixel_x", "pixel_y",
            "target_lat", "target_lon", "groundspeed"
        ])

    if not HEADLESS:
        cv2.namedWindow("Auto Detect", cv2.WINDOW_NORMAL)

    # State
    state = STATE_WATCHING
    consecutive_detections = 0
    target_lat = 0.0
    target_lon = 0.0
    hover_start = 0.0
    last_cmd_time = 0.0

    # Stats
    t_start = time.time()
    frame_count = 0
    detect_count = 0
    hover_count = 0

    print()
    print("[READY] Upload waypoints in MP. Fly AUTO. Pi will detect.")
    print("[READY] RC kill switch → STABILIZE/LOITER at any time.")
    print("[READY] Press 'r' to resume AUTO | 'q' to quit")
    print()

    try:
        while True:
            frame = eyes.get_frame()
            if frame is None:
                time.sleep(0.05)
                continue

            frame_count += 1
            now = time.time()

            # Telemetry
            telem = read_telemetry(mav)
            alt = telem["alt"]
            mode = get_mode(mav)

            # Detection
            found, px, py, conf = eyes.detect_in_image(frame)
            good_detection = found and conf >= MIN_CONF

            if good_detection:
                detect_count += 1

            # ── State machine ──

            if state == STATE_WATCHING:
                # Flying AUTO, waiting for detection
                if good_detection:
                    consecutive_detections += 1
                else:
                    consecutive_detections = 0

                if consecutive_detections >= MIN_DETECTIONS and telem["lat"] != 0:
                    # Got enough consecutive detections — switch to GUIDED
                    target_lat, target_lon = pixel_to_gps(
                        px, py, telem["lat"], telem["lon"], alt, telem["yaw"]
                    )
                    print(f"\n  *** TARGET FOUND *** conf={conf:.2f}")
                    print(f"  Target GPS: {target_lat:.7f}, {target_lon:.7f}")
                    print(f"  Drone  GPS: {telem['lat']:.7f}, {telem['lon']:.7f}")
                    print(f"  Altitude:   {alt:.1f}m")

                    if not DRY_RUN:
                        set_mode(mav, 4, "GUIDED")
                        beep(mav, "MFT200L8CEGC")
                    else:
                        print("  [DRY RUN] Would switch to GUIDED + center here")
                        beep(mav, "MFT200L16CD")
                    state = STATE_CENTERING

            elif state == STATE_CENTERING:
                # Moving to hover above target
                if good_detection and telem["lat"] != 0:
                    # Update target GPS with latest detection
                    target_lat, target_lon = pixel_to_gps(
                        px, py, telem["lat"], telem["lon"], alt, telem["yaw"]
                    )

                # Send position command at 5Hz
                if now - last_cmd_time > 0.2:
                    send_position(mav, target_lat, target_lon, alt)
                    last_cmd_time = now

                # Check if centered (within 2m)
                dist = _gps_dist(telem["lat"], telem["lon"], target_lat, target_lon)
                if dist < 2.0:
                    print(f"  Centered! Distance: {dist:.1f}m — holding position")
                    hover_start = now
                    hover_count += 1
                    state = STATE_HOVERING

            elif state == STATE_HOVERING:
                # Holding above target
                if good_detection and telem["lat"] != 0:
                    # Keep updating target if we still see it
                    target_lat, target_lon = pixel_to_gps(
                        px, py, telem["lat"], telem["lon"], alt, telem["yaw"]
                    )

                # Keep sending position hold
                if now - last_cmd_time > 0.5:
                    send_position(mav, target_lat, target_lon, alt)
                    last_cmd_time = now

                hover_elapsed = now - hover_start
                if hover_elapsed >= HOVER_TIMEOUT:
                    print(f"\n  Hover timeout ({HOVER_TIMEOUT}s) — resuming AUTO")
                    state = STATE_RESUMING

            elif state == STATE_RESUMING:
                set_mode(mav, 3, "AUTO")
                beep(mav, "MFT200L8EDC")
                consecutive_detections = 0
                target_lat = 0.0
                target_lon = 0.0
                state = STATE_WATCHING
                print("  Resumed AUTO — watching for targets\n")

            # Check if pilot took over (RC override)
            if state in (STATE_CENTERING, STATE_HOVERING) and mode not in ("GUIDED", "AUTO"):
                print(f"\n  [RC OVERRIDE] Pilot took control (mode: {mode})")
                state = STATE_WATCHING
                consecutive_detections = 0

            # Log
            writer.writerow([
                time.strftime("%H:%M:%S"), state, mode,
                f"{telem['lat']:.7f}", f"{telem['lon']:.7f}", f"{alt:.1f}",
                "YES" if good_detection else "no",
                f"{conf:.3f}" if found else "",
                px if found else "", py if found else "",
                f"{target_lat:.7f}" if target_lat else "",
                f"{target_lon:.7f}" if target_lon else "",
                f"{telem['groundspeed']:.1f}"
            ])
            log_file.flush()

            # ── Display ──
            if HEADLESS:
                if state != STATE_WATCHING and frame_count % 10 == 0:
                    dist = _gps_dist(telem["lat"], telem["lon"], target_lat, target_lon) if target_lat else 0
                    hover_s = f" hover:{now - hover_start:.0f}s" if state == STATE_HOVERING else ""
                    print(f"  [{state}] dist={dist:.1f}m alt={alt:.1f}m{hover_s}")
                elif frame_count % 60 == 0:
                    print(f"  [{state}] {mode} alt={alt:.1f}m det={detect_count} frames={frame_count}")
            else:
                h, w = frame.shape[:2]

                # State banner
                state_colors = {
                    STATE_WATCHING: (200, 200, 200),
                    STATE_CENTERING: (0, 255, 255),
                    STATE_HOVERING: (0, 255, 0),
                    STATE_RESUMING: (255, 200, 0),
                }
                color = state_colors.get(state, (255, 255, 255))
                cv2.putText(frame, f"[{state}]  Mode: {mode}", (10, 25),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

                if DRY_RUN:
                    cv2.putText(frame, "DRY RUN", (w - 120, 25),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

                # Detection info
                if good_detection:
                    cv2.circle(frame, (int(px), int(py)), 15, (0, 255, 0), 2)
                    cv2.drawMarker(frame, (w // 2, h // 2), (255, 255, 255),
                                   cv2.MARKER_CROSS, 30, 1)
                    cv2.line(frame, (w // 2, h // 2), (int(px), int(py)), (0, 255, 0), 2)
                    cv2.putText(frame, f"conf={conf:.2f} ({consecutive_detections}x)",
                                (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

                # Hovering info
                if state == STATE_HOVERING:
                    hover_elapsed = now - hover_start
                    remaining = max(0, HOVER_TIMEOUT - hover_elapsed)
                    cv2.rectangle(frame, (0, 0), (w - 1, h - 1), (0, 255, 0), 4)
                    cv2.putText(frame, f"HOVERING — resume in {remaining:.0f}s",
                                (10, h // 2), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    dist = _gps_dist(telem["lat"], telem["lon"], target_lat, target_lon) if target_lat else 0
                    cv2.putText(frame, f"Dist to target: {dist:.1f}m",
                                (10, h // 2 + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

                elif state == STATE_CENTERING:
                    cv2.rectangle(frame, (0, 0), (w - 1, h - 1), (0, 255, 255), 3)
                    cv2.putText(frame, "CENTERING...", (10, h // 2),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

                # Info bar
                bar_y = h - 40
                cv2.rectangle(frame, (0, bar_y), (w, h), (0, 0, 0), -1)
                info = f"Alt:{alt:.0f}m  Spd:{telem['groundspeed']:.1f}  Det:{detect_count}  Hover:{hover_count}"
                cv2.putText(frame, info, (10, bar_y + 25),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)

                cv2.imshow("Auto Detect", frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == 27:
                    break
                elif key == ord('r') and state in (STATE_CENTERING, STATE_HOVERING):
                    print("  [KEY] Resuming AUTO")
                    state = STATE_RESUMING

    except KeyboardInterrupt:
        print("\n  Ctrl+C — cleaning up...")

    # Cleanup: switch back to AUTO if we're in GUIDED
    current_mode = get_mode(mav)
    if current_mode == "GUIDED" and not DRY_RUN:
        print("  Switching back to AUTO before exit...")
        set_mode(mav, 3, "AUTO")
        time.sleep(0.5)

    log_file.close()
    eyes.release()
    if not HEADLESS:
        cv2.destroyAllWindows()

    # Summary
    flight_min = (time.time() - t_start) / 60
    print()
    print("=" * 60)
    print("  AUTO DETECT SUMMARY")
    print("=" * 60)
    print(f"  Run time:       {flight_min:.1f} minutes")
    print(f"  Frames:         {frame_count}")
    print(f"  Detections:     {detect_count}")
    print(f"  Hover events:   {hover_count}")
    print(f"  Log saved:      {log_path}")
    print("=" * 60)


def _gps_dist(lat1, lon1, lat2, lon2):
    """Simple flat-earth distance in meters."""
    lat_scale = 111132.0
    return math.sqrt(((lat1 - lat2) * lat_scale) ** 2 +
                     ((lon1 - lon2) * lat_scale * math.cos(math.radians(lat1))) ** 2)


if __name__ == "__main__":
    main()
