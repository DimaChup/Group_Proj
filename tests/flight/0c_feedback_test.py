#!/usr/bin/env python3
"""
Feedback Loop Test — prove the vision-to-GPS-to-command pipeline end-to-end.

WHAT:    Runs camera + AI detection and converts pixel detections to GPS coordinates
         using the same math as main.py. Displays pixel position, guidance direction,
         meter offsets, estimated target GPS, and frame-to-frame drift. Sends ZERO
         commands to the Cube — read-only telemetry for altitude and yaw.
WHY:     Validates the entire feedback loop (camera -> detect -> pixel-to-GPS -> guidance)
         without any risk. Proves that the centering logic and GPS estimation work before
         testing them in flight. Also measures estimate stability (frame drift).
WHEN:    After 0b_bench_mission.py passes. Before any flight with CV. Carry the drone
         by hand over a printed dummy to test.
WHERE:   Pi (with camera + Cube via mavproxy) or laptop (with webcam + SITL).
ENV:     pienv on Pi (with ai-edge-litert), or dev venv on laptop (with ultralytics).
MODELS:  best.tflite (YOLOv8n TFLite) — loaded via vision.py dual backend.
RISK:    None — sends ZERO commands to the Cube. Read-only telemetry. Falls back to
         fake telemetry (10m altitude) if Cube is not connected.

USAGE:
    python tests/flight/0c_feedback_test.py                # with OpenCV window
    python tests/flight/0c_feedback_test.py --headless     # terminal only (SSH/PuTTY)

FLAGS:
    --headless    Skip cv2.imshow window, output to terminal only (for SSH sessions)

OUTPUT:
    Terminal table: frame number, pixel coords, guidance direction, meter offsets,
    target GPS estimate, and frame-to-frame drift in meters. Summary of total
    detections and what the test proved.

BEST PRACTICES:
    - Print the dummy image and hold the drone/camera above it at ~1m height
    - Watch frame drift column — should be < 0.5m when stationary
    - If drift is large, check FOCAL_LENGTH_MM and SENSOR_WIDTH_MM in config.py
    - Works without Cube (uses fake 10m altitude) — useful for camera-only testing

DEPENDENCIES:
    opencv-python, numpy, config.py, vision.py (VisionSystem), pymavlink (optional)
"""
import sys
import os
import time
import math

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, project_root)

import cv2
import numpy as np
import config

HEADLESS = "--headless" in sys.argv


def connect_cube():
    """Connect to Cube for telemetry (read-only)."""
    try:
        from pymavlink import mavutil
    except ImportError:
        print("[CUBE] pymavlink not installed — using fake telemetry")
        return None

    try:
        mav = mavutil.mavlink_connection(config.CONNECTION_STR)
        print(f"[CUBE] Connecting: {config.CONNECTION_STR}")
        mav.wait_heartbeat(timeout=10)
        print(f"[CUBE] Connected (system {mav.target_system})")
        mav.mav.request_data_stream_send(
            mav.target_system, mav.target_component, 0, 10, 1)
        return mav
    except Exception as e:
        print(f"[CUBE] Connection failed: {e} — using fake telemetry")
        return None


def read_telemetry(mav):
    """Read latest position from Cube."""
    data = {"lat": 0.0, "lon": 0.0, "alt": 1.0, "yaw": 0.0}
    if mav is None:
        # Fake telemetry for bench testing without Cube
        data["alt"] = 10.0  # pretend we're at 10m
        return data

    while True:
        msg = mav.recv_match(blocking=False)
        if msg is None:
            break
        mtype = msg.get_type()
        if mtype == "GLOBAL_POSITION_INT":
            data["lat"] = msg.lat / 1e7
            data["lon"] = msg.lon / 1e7
            data["alt"] = max(1.0, msg.relative_alt / 1000.0)
        elif mtype == "ATTITUDE":
            data["yaw"] = msg.yaw  # radians
    return data


def calculate_target_gps(u, v, drone_lat, drone_lon, alt, yaw):
    """
    Same math as main.py — convert pixel position to GPS coordinate.
    This is the core of the feedback loop.
    """
    cx = config.IMAGE_W / 2
    cy = config.IMAGE_H / 2

    # Ground Sample Distance: meters per pixel at this altitude
    gsd_m = (config.SENSOR_WIDTH_MM * alt) / (config.FOCAL_LENGTH_MM * config.IMAGE_W)

    # Pixel offset from center
    delta_x_px = u - cx
    delta_y_px = v - cy

    # Convert to meters (forward/right in camera frame)
    fwd_m = -delta_y_px * gsd_m    # up in image = forward
    right_m = delta_x_px * gsd_m   # right in image = right

    # Rotate by yaw to get North/East offsets
    offset_n = fwd_m * math.cos(yaw) - right_m * math.sin(yaw)
    offset_e = fwd_m * math.sin(yaw) + right_m * math.cos(yaw)

    # Convert meters to lat/lon
    R_EARTH = 6378137.0
    d_lat = (offset_n / R_EARTH) * (180 / math.pi)
    d_lon = (offset_e / (R_EARTH * math.cos(math.radians(drone_lat)))) * (180 / math.pi)

    target_lat = drone_lat + d_lat
    target_lon = drone_lon + d_lon

    return target_lat, target_lon, gsd_m, fwd_m, right_m


def get_guidance(px, py, img_w, img_h):
    """Same as passive_flight — direction to center target."""
    cx, cy = img_w / 2, img_h / 2
    off_x = (px - cx) / (img_w / 2)
    off_y = (py - cy) / (img_h / 2)

    DEAD_ZONE = 0.15
    dirs = []
    if off_x < -DEAD_ZONE:
        dirs.append("LEFT")
    elif off_x > DEAD_ZONE:
        dirs.append("RIGHT")
    if off_y < -DEAD_ZONE:
        dirs.append("FORWARD")
    elif off_y > DEAD_ZONE:
        dirs.append("BACK")

    return "CENTRED" if not dirs else "+".join(dirs)


def main():
    print()
    print("=" * 60)
    print("   FEEDBACK LOOP TEST")
    print("   Camera → Detect → GPS estimate → Command → Repeat")
    print("=" * 60)
    print()
    print("  Carry drone over dummy printout. Watch the loop work.")
    print("  No commands sent to Cube. Safe on bench.")
    print()

    mav = connect_cube()

    from vision import VisionSystem
    eyes = VisionSystem(camera_index=0,
                        model_path=os.path.join(project_root, "best.tflite"))

    if not HEADLESS:
        cv2.namedWindow("Feedback Test", cv2.WINDOW_NORMAL)

    detect_count = 0
    prev_target_lat = None
    prev_target_lon = None

    print(f"  Config: IMAGE={config.IMAGE_W}x{config.IMAGE_H}, "
          f"SENSOR={config.SENSOR_WIDTH_MM}mm, FOCAL={config.FOCAL_LENGTH_MM}mm")
    print(f"  Flip 180: {getattr(config, 'CAMERA_FLIP_180', False)}")
    print()
    print(f"  {'Frame':<7} {'Pixel':^12} {'Direction':^16} {'Offset(m)':^16} {'Target GPS':^30} {'Drift':^10}")
    print(f"  {'-'*7} {'-'*12} {'-'*16} {'-'*16} {'-'*30} {'-'*10}")

    try:
        while True:
            frame = eyes.get_frame()
            if frame is None:
                time.sleep(0.05)
                continue

            telem = read_telemetry(mav)
            found, px, py, conf = eyes.detect_in_image(frame)

            if found:
                detect_count += 1
                img_h, img_w = frame.shape[:2]

                # Step 1: Guidance direction
                guidance = get_guidance(px, py, img_w, img_h)

                # Step 2: GPS estimation (the main.py math)
                t_lat, t_lon, gsd, fwd, right = calculate_target_gps(
                    px, py,
                    telem["lat"], telem["lon"],
                    telem["alt"], telem["yaw"]
                )

                # Step 3: How much did the estimate change from last frame?
                drift = ""
                if prev_target_lat is not None and telem["lat"] != 0:
                    d = math.sqrt(
                        ((t_lat - prev_target_lat) * 111320) ** 2 +
                        ((t_lon - prev_target_lon) * 111320 * math.cos(math.radians(t_lat))) ** 2
                    )
                    drift = f"{d:.2f}m"
                prev_target_lat = t_lat
                prev_target_lon = t_lon

                # Print the feedback loop
                gps_str = f"({t_lat:.6f}, {t_lon:.6f})" if telem["lat"] != 0 else "(no GPS fix)"
                print(f"  #{detect_count:<5} ({px:>3},{py:>3})  {guidance:^16} "
                      f"F:{fwd:>+5.1f} R:{right:>+5.1f}  {gps_str}  {drift}")

                # Display
                if not HEADLESS:
                    # Crosshair + target + guidance
                    cv2.drawMarker(frame, (img_w // 2, img_h // 2),
                                   (255, 255, 255), cv2.MARKER_CROSS, 30, 1)
                    cv2.circle(frame, (int(px), int(py)), 10, (0, 255, 0), 2)
                    cv2.line(frame, (img_w // 2, img_h // 2),
                             (int(px), int(py)), (0, 255, 255), 2)

                    # Info overlay
                    guide_color = (0, 255, 255) if guidance != "CENTRED" else (0, 255, 0)
                    cv2.putText(frame, f"MOVE: {guidance}", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, guide_color, 2)
                    cv2.putText(frame, f"Fwd:{fwd:+.1f}m  Right:{right:+.1f}m", (10, 60),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
                    cv2.putText(frame, f"GSD: {gsd:.4f} m/px  Alt: {telem['alt']:.1f}m",
                                (10, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
                    cv2.putText(frame, f"conf={conf:.2f}  #{detect_count}", (10, img_h - 15),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

                    if drift:
                        cv2.putText(frame, f"Frame drift: {drift}", (10, 110),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 255), 1)

            if not HEADLESS:
                if frame is not None:
                    cv2.imshow("Feedback Test", frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == 27:
                    break
            else:
                time.sleep(0.01)

    except KeyboardInterrupt:
        print("\nStopping...")

    eyes.release()
    if not HEADLESS:
        cv2.destroyAllWindows()

    print()
    print("=" * 60)
    print(f"  Total detections: {detect_count}")
    print()
    print("  What this proved:")
    print("    1. Camera detects target (pixel position)")
    print("    2. Pixel → meters offset (using altitude + FOV)")
    print("    3. Meters → GPS coordinate (using yaw)")
    print("    4. Each frame updates the estimate (feedback loop)")
    print("    5. Frame drift shows estimate stability")
    print()
    print("  In main.py, step 3's GPS goes to the Cube as 'fly here'.")
    print("  Cube handles the actual flying (its own PID loop).")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
