#!/usr/bin/env python3
"""
Detect and Center — autonomous waypoint flight + AI detection + velocity centering.

WHAT:    Arms, takes off, flies a square GUIDED waypoint pattern while running AI
         detection on every frame. When the target is detected for N consecutive frames,
         switches to velocity-based centering (max 1 m/s) to position the drone directly
         above the target. Once centered, hovers and waits for operator decision:
         'l' to land, 'r' to resume search, 'q' to RTL. If target is lost during
         centering, holds position for 5s then resumes waypoints.
WHY:     The most advanced flight test before using main.py. Tests everything that
         passive flight does not: autonomous mode switching, velocity-based visual
         servo centering, target lock-on time, and false positive handling in real
         flight conditions.
WHEN:    Step 4 (final progressive test). After 3_auto_detect proves detection works
         in flight. Before trusting main.py for the real mission.
WHERE:   Pi (with camera + Cube via mavproxy, outdoors) or laptop (with webcam + SITL).
ENV:     pienv on Pi (ai-edge-litert, opencv-headless, pymavlink). Dev venv on laptop.
MODELS:  best.tflite (YOLOv8n TFLite) — loaded via vision.py dual backend.
RISK:    HIGH — this script arms, takes off, flies waypoints, and can land autonomously.
         Sends velocity commands during centering. RC kill switch must be ready. Use
         --dry-run to verify GPS + AI without arming.

USAGE:
    python tests/flight/4_detect_and_center.py                        # full mission
    python tests/flight/4_detect_and_center.py --dry-run              # verify without arming
    python tests/flight/4_detect_and_center.py --headless --stream    # Pi SSH + browser stream
    python tests/flight/4_detect_and_center.py --alt 15 --pattern 40  # custom altitude/pattern

FLAGS:
    --alt N             Flight altitude in meters (default 15)
    --pattern N         Square pattern size in meters (default 40)
    --speed N           Waypoint speed in m/s (default 3)
    --conf N            Detection confidence threshold (default 0.4)
    --min-detections N  Consecutive detections before centering (default 3)
    --dry-run           Connect, verify GPS + AI, run 10s detection test, don't arm
    --headless          Skip cv2.imshow, terminal only (for SSH/PuTTY)
    --stream            Enable MJPEG stream at http://PI_IP:8090/
    --stream-port N     Stream port (default 8090)

OUTPUT:
    - Terminal: real-time state, waypoint progress, centering direction, operator prompts
    - OpenCV window (unless --headless): live video with state banner, crosshair, detection
    - Optional MJPEG stream viewable in browser
    - Summary: frames processed, detections, waypoints reached

BEST PRACTICES:
    - ALWAYS run --dry-run first to verify GPS fix and AI detection
    - Start with a small --pattern (20m) and low --alt (10m) for first test
    - Keep RC transmitter ready — STABILIZE/LOITER overrides at any time
    - Ctrl+C triggers RTL as emergency fallback
    - Use --stream on Pi so you can watch the video feed from a laptop browser
    - If centering oscillates, increase --conf or --min-detections

DEPENDENCIES:
    opencv-python (or opencv-headless), numpy, pymavlink, config.py, vision.py
"""
import sys
import os
import time
import math
import signal
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, project_root)

from pymavlink import mavutil
import cv2
import numpy as np
import config

# ── Settings ──
TEST_ALT = 15.0
PATTERN_SIZE = 40.0
WAYPOINT_TOLERANCE = 3.0
SPEED = 3.0
CONF_THRESHOLD = 0.4
MIN_DETECTIONS = 3  # consecutive frames before centering
DRY_RUN = "--dry-run" in sys.argv
HEADLESS = "--headless" in sys.argv
STREAM = "--stream" in sys.argv
STREAM_PORT = 8090

for i, arg in enumerate(sys.argv):
    if arg == "--alt" and i + 1 < len(sys.argv):
        TEST_ALT = float(sys.argv[i + 1])
    elif arg == "--pattern" and i + 1 < len(sys.argv):
        PATTERN_SIZE = float(sys.argv[i + 1])
    elif arg == "--speed" and i + 1 < len(sys.argv):
        SPEED = float(sys.argv[i + 1])
    elif arg == "--conf" and i + 1 < len(sys.argv):
        CONF_THRESHOLD = float(sys.argv[i + 1])
    elif arg == "--min-detections" and i + 1 < len(sys.argv):
        MIN_DETECTIONS = int(sys.argv[i + 1])
    elif arg == "--stream-port" and i + 1 < len(sys.argv):
        STREAM_PORT = int(sys.argv[i + 1])

# ArduCopter mode numbers
MODE_STABILIZE = 0
MODE_GUIDED = 4
MODE_LAND = 9
MODE_RTL = 6

COPTER_MODES = {
    0: "STABILIZE", 1: "ACRO", 2: "ALT_HOLD", 3: "AUTO",
    4: "GUIDED", 5: "LOITER", 6: "RTL", 7: "CIRCLE",
    9: "LAND", 11: "DRIFT", 13: "SPORT", 14: "FLIP",
    15: "AUTOTUNE", 16: "POSHOLD", 17: "BRAKE", 18: "THROW",
    19: "AVOID_ADSB", 20: "GUIDED_NOGPS", 21: "SMART_RTL",
}

# States
STATE_WAYPOINTS = "WAYPOINTS"
STATE_CENTERING = "CENTERING"
STATE_HOVERING = "HOVERING"
STATE_LANDING = "LANDING"
STATE_RTL = "RTL"

# Stream globals
_stream_frame = None
_stream_lock = threading.Lock()

# Global for signal handler
mav = None


# ── Stream server ──

class _StreamHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/stream':
            self.send_response(200)
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=frame')
            self.end_headers()
            while True:
                with _stream_lock:
                    f = _stream_frame
                if f is None:
                    time.sleep(0.1)
                    continue
                small = cv2.resize(f, (320, 240))
                _, jpeg = cv2.imencode('.jpg', small, [cv2.IMWRITE_JPEG_QUALITY, 50])
                data = jpeg.tobytes()
                try:
                    self.wfile.write(b'--frame\r\n')
                    self.wfile.write(b'Content-Type: image/jpeg\r\n')
                    self.wfile.write(f'Content-Length: {len(data)}\r\n\r\n'.encode())
                    self.wfile.write(data)
                    self.wfile.write(b'\r\n')
                except (BrokenPipeError, ConnectionResetError):
                    break
                time.sleep(0.2)
        elif self.path == '/':
            html = '<html><body style="background:#111;text-align:center;font-family:monospace">'
            html += '<h2 style="color:#fff">Detect & Center — Live Feed</h2>'
            html += '<img src="/stream" style="max-width:100%;border:2px solid #0f0"/>'
            html += '</body></html>'
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass


# ── MAVLink helpers (same patterns as pi_waypoint_test.py) ──

def connect():
    """Connect to Cube, wait for autopilot heartbeat."""
    conn_str = config.CONNECTION_STR
    print(f"  Connecting: {conn_str}")

    if conn_str.startswith("/dev/"):
        m = mavutil.mavlink_connection(conn_str, baud=config.BAUD_RATE)
    else:
        m = mavutil.mavlink_connection(conn_str)

    print("  Waiting for autopilot heartbeat...")
    autopilot_hb = None
    start = time.time()
    while time.time() - start < 15:
        hb = m.recv_match(type='HEARTBEAT', blocking=True, timeout=2)
        if hb and hb.type != mavutil.mavlink.MAV_TYPE_GCS:
            autopilot_hb = hb
            break
    if autopilot_hb is None:
        print("  [FAIL] No autopilot heartbeat. Is mavproxy running?")
        sys.exit(1)

    m.target_system = autopilot_hb.get_srcSystem()
    m.target_component = autopilot_hb.get_srcComponent()
    print(f"  [OK] Connected to system {m.target_system}")

    m.mav.request_data_stream_send(
        m.target_system, m.target_component,
        mavutil.mavlink.MAV_DATA_STREAM_ALL, 10, 1)
    time.sleep(0.5)
    return m


def get_mode(m):
    while m.recv_msg() is not None:
        pass
    for _ in range(10):
        hb = m.recv_match(type='HEARTBEAT', blocking=True, timeout=3)
        if hb and hb.type != mavutil.mavlink.MAV_TYPE_GCS:
            return COPTER_MODES.get(hb.custom_mode, f"MODE_{hb.custom_mode}")
    return "UNKNOWN"


def set_mode(m, mode_num, mode_name):
    print(f"  Setting mode: {mode_name}...")
    m.mav.command_long_send(
        m.target_system, m.target_component,
        mavutil.mavlink.MAV_CMD_DO_SET_MODE, 0,
        mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
        mode_num, 0, 0, 0, 0, 0)
    time.sleep(1.5)
    actual = get_mode(m)
    if actual == mode_name:
        print(f"  [OK] Mode: {actual}")
        return True
    else:
        print(f"  [!!] Mode is {actual} (wanted {mode_name})")
        return False


def wait_for_gps(m, timeout=120):
    print(f"\n  Waiting for GPS 3D fix (timeout {timeout}s)...")
    start = time.time()
    while time.time() - start < timeout:
        while m.recv_msg() is not None:
            pass
        gps = m.messages.get('GPS_RAW_INT')
        if gps:
            fix = gps.fix_type
            sats = gps.satellites_visible
            elapsed = int(time.time() - start)
            if fix >= 3:
                lat = gps.lat / 1e7
                lon = gps.lon / 1e7
                print(f"  [OK] 3D Fix! sats={sats} pos=({lat:.6f}, {lon:.6f}) [{elapsed}s]")
                return lat, lon
            else:
                if elapsed % 5 == 0:
                    print(f"  ... fix={fix} sats={sats} [{elapsed}s]")
        time.sleep(1)
    print(f"  [FAIL] No GPS fix after {timeout}s")
    return None, None


def get_position(m):
    while m.recv_msg() is not None:
        pass
    pos = m.messages.get('GLOBAL_POSITION_INT')
    if pos:
        return pos.lat / 1e7, pos.lon / 1e7, pos.relative_alt / 1000.0
    return None, None, None


def distance_between(lat1, lon1, lat2, lon2):
    R = 6378137.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat/2)**2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))


def send_waypoint(m, lat, lon, alt):
    m.mav.set_position_target_global_int_send(
        0, m.target_system, m.target_component,
        mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
        0b110111111000,
        int(lat * 1e7), int(lon * 1e7), alt,
        0, 0, 0, 0, 0, 0, 0, 0)


def send_velocity(m, vx, vy, vz=0):
    """Send velocity command in body frame (NED). vx=forward, vy=right, vz=down."""
    m.mav.set_position_target_local_ned_send(
        0, m.target_system, m.target_component,
        mavutil.mavlink.MAV_FRAME_BODY_OFFSET_NED,
        0b110111000111,  # ignore position, use velocity
        0, 0, 0,
        vx, vy, vz,
        0, 0, 0, 0, 0)


def generate_square_pattern(home_lat, home_lon, size_m):
    R = 6378137.0
    half = size_m / 2.0
    dlat = (half / R) * (180 / math.pi)
    dlon = (half / (R * math.cos(math.radians(home_lat)))) * (180 / math.pi)
    return [
        (home_lat + dlat, home_lon - dlon, "NW"),
        (home_lat + dlat, home_lon + dlon, "NE"),
        (home_lat - dlat, home_lon + dlon, "SE"),
        (home_lat - dlat, home_lon - dlon, "SW"),
    ]


def emergency_rtl(signum, frame):
    global mav
    print("\n\n  !!! Ctrl+C — TRIGGERING RTL !!!")
    if mav:
        mav.mav.command_long_send(
            mav.target_system, mav.target_component,
            mavutil.mavlink.MAV_CMD_DO_SET_MODE, 0,
            mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
            MODE_RTL, 0, 0, 0, 0, 0)
        print("  RTL command sent.")
    sys.exit(0)


# ── Main mission ──

def main():
    global mav, _stream_frame

    print()
    print("=" * 60)
    print("   DETECT & CENTER — Simplified Mission Test")
    print("   Fly waypoints → detect → center → hover → decide")
    print("=" * 60)
    print()
    print(f"  Altitude:       {TEST_ALT}m")
    print(f"  Pattern:        {PATTERN_SIZE}m square")
    print(f"  Speed:          {SPEED} m/s")
    print(f"  Confidence:     {CONF_THRESHOLD}")
    print(f"  Min detections: {MIN_DETECTIONS} consecutive frames")
    print(f"  Dry run:        {DRY_RUN}")
    print(f"  Headless:       {HEADLESS}")
    print(f"  Stream:         {STREAM}")
    print()

    # ── Start stream server ──
    if STREAM:
        try:
            server = HTTPServer(('0.0.0.0', STREAM_PORT), _StreamHandler)
            threading.Thread(target=server.serve_forever, daemon=True).start()
            pi_ip = "???"
            try:
                import subprocess
                result = subprocess.run(['hostname', '-I'], capture_output=True, text=True, timeout=3)
                pi_ip = result.stdout.strip().split()[0]
            except Exception:
                pass
            print(f"  [STREAM] http://{pi_ip}:{STREAM_PORT}/")
        except Exception as e:
            print(f"  [STREAM] Failed: {e}")

    # ── Load AI ──
    from vision import VisionSystem
    model_path = os.path.join(project_root, "best.tflite")
    print(f"  Loading AI model: {model_path}")
    eyes = VisionSystem(camera_index=0, model_path=model_path)
    if not eyes.using_ai:
        print("  [WARN] AI not loaded — will fly without detection")

    # Warmup
    warmup_frame = eyes.get_frame()
    if warmup_frame is not None and eyes.using_ai:
        eyes.detect_in_image(warmup_frame)
        print("  [OK] AI warmup done")

    # ── Safety confirmation ──
    if not DRY_RUN:
        print()
        print("  !! WARNING: This script WILL fly the drone !!")
        print("  !! RC kill switch: flip to STABILIZE/LOITER !!")
        print()
        print("  Press Enter to continue, Ctrl+C to abort...")
        try:
            input()
        except KeyboardInterrupt:
            print("\n  Aborted.")
            eyes.release()
            return

    signal.signal(signal.SIGINT, emergency_rtl)

    # ── Connect ──
    mav = connect()

    # ── GPS fix ──
    home_lat, home_lon = wait_for_gps(mav)
    if home_lat is None:
        print("  Cannot fly without GPS. Exiting.")
        eyes.release()
        mav.close()
        return

    # ── Generate waypoints ──
    waypoints = generate_square_pattern(home_lat, home_lon, PATTERN_SIZE)
    print(f"\n  Flight plan ({len(waypoints)} waypoints at {TEST_ALT}m):")
    for i, (wlat, wlon, label) in enumerate(waypoints):
        dist = distance_between(home_lat, home_lon, wlat, wlon)
        print(f"    WP{i+1} ({label}): ({wlat:.6f}, {wlon:.6f}) — {dist:.0f}m from home")

    if DRY_RUN:
        print("\n  [DRY RUN] GPS OK, AI OK, waypoints OK. Ready for real flight.")
        # Run detection loop briefly to verify CV works
        print("  [DRY RUN] Testing detection for 10 seconds...")
        t0 = time.time()
        det_count = 0
        frame_count = 0
        while time.time() - t0 < 10:
            frame = eyes.get_frame()
            if frame is None:
                continue
            frame_count += 1
            if eyes.using_ai:
                found, px, py, conf = eyes.detect_in_image(frame)
                if found:
                    det_count += 1
                    print(f"    DETECTED conf={conf:.2f} at ({px},{py})")
            if not HEADLESS:
                cv2.imshow("Dry Run", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        print(f"  [DRY RUN] {det_count} detections in {frame_count} frames")
        if not HEADLESS:
            cv2.destroyAllWindows()
        eyes.release()
        mav.close()
        return

    # ── Arm ──
    print(f"\n  ARMING...")
    if not set_mode(mav, MODE_GUIDED, "GUIDED"):
        print("  Could not set GUIDED. Exiting.")
        eyes.release()
        mav.close()
        return

    mav.mav.command_long_send(
        mav.target_system, mav.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0,
        1, 0, 0, 0, 0, 0, 0)

    armed = False
    for _ in range(10):
        ack = mav.recv_match(type='COMMAND_ACK', blocking=True, timeout=2)
        if ack and ack.command == mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM:
            if ack.result == 0:
                print("  [OK] Armed!")
                armed = True
            else:
                stxt = mav.recv_match(type='STATUSTEXT', blocking=True, timeout=1)
                reason = stxt.text if stxt else "unknown"
                print(f"  [FAIL] Arm rejected: {reason}")
            break
    if not armed:
        print("  Could not arm. Exiting.")
        eyes.release()
        mav.close()
        return

    # ── Takeoff ──
    print(f"\n  TAKEOFF to {TEST_ALT}m...")
    mav.mav.command_long_send(
        mav.target_system, mav.target_component,
        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0,
        0, 0, 0, 0, 0, 0, TEST_ALT)

    start = time.time()
    while time.time() - start < 30:
        lat, lon, alt = get_position(mav)
        if alt is not None:
            print(f"    alt={alt:.1f}m", end="\r")
            if alt >= TEST_ALT * 0.85:
                print(f"\n  [OK] Reached {alt:.1f}m")
                break
        time.sleep(0.5)

    mav.mav.command_long_send(
        mav.target_system, mav.target_component,
        mavutil.mavlink.MAV_CMD_DO_CHANGE_SPEED, 0,
        1, SPEED, -1, 0, 0, 0, 0)

    # ══════════════════════════════════════════════════════════════
    #  MAIN LOOP: fly waypoints + detect + center
    # ══════════════════════════════════════════════════════════════

    state = STATE_WAYPOINTS
    wp_index = 0
    consecutive_detections = 0
    consecutive_lost = 0
    total_detections = 0
    frame_count = 0
    center_start_time = 0

    print(f"\n{'='*60}")
    print(f"  MISSION STARTED — flying {len(waypoints)} waypoints")
    print(f"  Operator keys: 'l'=land  'r'=resume  'q'=RTL+quit")
    print(f"{'='*60}\n")

    try:
        while True:
            # ── Get frame + detect ──
            frame = eyes.get_frame()
            if frame is None:
                time.sleep(0.05)
                continue

            frame_count += 1
            h, w = frame.shape[:2]
            cx, cy = w // 2, h // 2

            found = False
            px, py, conf = 0, 0, 0.0
            if eyes.using_ai:
                found, px, py, conf = eyes.detect_in_image(frame)

            if found:
                total_detections += 1

            # ── Get telemetry ──
            lat, lon, alt = get_position(mav)

            # ── State machine ──

            if state == STATE_WAYPOINTS:
                # Flying waypoints — check for detections
                if found:
                    consecutive_detections += 1
                else:
                    consecutive_detections = 0

                # Trigger centering after N consecutive detections
                if consecutive_detections >= MIN_DETECTIONS:
                    state = STATE_CENTERING
                    center_start_time = time.time()
                    consecutive_lost = 0
                    print(f"\n  *** TARGET DETECTED *** conf={conf:.2f}")
                    print(f"  Switching to CENTERING...")
                    # Already in GUIDED mode, just start sending velocity commands
                    continue

                # Fly towards current waypoint
                if wp_index < len(waypoints):
                    wlat, wlon, label = waypoints[wp_index]
                    send_waypoint(mav, wlat, wlon, TEST_ALT)

                    if lat is not None:
                        dist = distance_between(lat, lon, wlat, wlon)
                        if dist < WAYPOINT_TOLERANCE:
                            print(f"  [OK] Reached WP{wp_index+1} ({label})")
                            wp_index += 1
                            if wp_index >= len(waypoints):
                                print(f"\n  All waypoints complete. Returning home...")
                                state = STATE_RTL
                else:
                    state = STATE_RTL

            elif state == STATE_CENTERING:
                # Send velocity commands to center target in frame
                if found:
                    consecutive_lost = 0

                    # Pixel offset from center, normalized to [-1, 1]
                    off_x = (px - cx) / (w / 2)   # positive = target is RIGHT
                    off_y = (py - cy) / (h / 2)   # positive = target is DOWN (BACK)

                    DEAD_ZONE = 0.15
                    MAX_VEL = 1.0  # m/s — slow and safe

                    vx = 0.0  # forward/back
                    vy = 0.0  # left/right

                    if abs(off_y) > DEAD_ZONE:
                        vx = -off_y * MAX_VEL  # negative because down in image = backward
                    if abs(off_x) > DEAD_ZONE:
                        vy = off_x * MAX_VEL

                    send_velocity(mav, vx, vy)

                    # Check if centered
                    if abs(off_x) <= DEAD_ZONE and abs(off_y) <= DEAD_ZONE:
                        state = STATE_HOVERING
                        # Stop movement
                        send_velocity(mav, 0, 0)
                        center_time = time.time() - center_start_time
                        print(f"\n  *** CENTERED *** in {center_time:.1f}s")
                        print(f"  Hovering above target.")
                        if lat is not None:
                            print(f"  GPS: ({lat:.6f}, {lon:.6f}) alt={alt:.1f}m")
                        print(f"  Press: 'l'=land  'r'=resume search  'q'=RTL")
                        continue

                    # Direction feedback
                    dirs = []
                    if off_x < -DEAD_ZONE: dirs.append("LEFT")
                    elif off_x > DEAD_ZONE: dirs.append("RIGHT")
                    if off_y < -DEAD_ZONE: dirs.append("FWD")
                    elif off_y > DEAD_ZONE: dirs.append("BACK")
                    dir_str = "+".join(dirs) if dirs else "~"

                    if frame_count % 10 == 0:
                        print(f"  CENTERING: {dir_str}  vx={vx:.2f} vy={vy:.2f}  conf={conf:.2f}")

                else:
                    consecutive_lost += 1
                    send_velocity(mav, 0, 0)  # hold position

                    if consecutive_lost > 20:  # ~5 seconds at 4fps
                        print(f"  Target lost for 5s — resuming waypoints")
                        state = STATE_WAYPOINTS
                        consecutive_detections = 0

            elif state == STATE_HOVERING:
                # Holding position — maintain center if target drifts
                if found:
                    off_x = (px - cx) / (w / 2)
                    off_y = (py - cy) / (h / 2)
                    DEAD_ZONE = 0.15
                    MAX_VEL = 0.5  # gentler corrections while hovering

                    vx, vy = 0.0, 0.0
                    if abs(off_y) > DEAD_ZONE:
                        vx = -off_y * MAX_VEL
                    if abs(off_x) > DEAD_ZONE:
                        vy = off_x * MAX_VEL
                    send_velocity(mav, vx, vy)
                else:
                    send_velocity(mav, 0, 0)

            elif state == STATE_LANDING:
                # Landing — just wait
                if alt is not None and alt < 0.5:
                    print(f"\n  [OK] Landed!")
                    break
                if frame_count % 20 == 0:
                    alt_str = f"{alt:.1f}m" if alt else "?"
                    print(f"  Landing... alt={alt_str}")

            elif state == STATE_RTL:
                # Return home and land
                send_waypoint(mav, home_lat, home_lon, TEST_ALT)
                if lat is not None:
                    dist = distance_between(lat, lon, home_lat, home_lon)
                    if dist < WAYPOINT_TOLERANCE:
                        print(f"  [OK] Back at home — landing")
                        set_mode(mav, MODE_LAND, "LAND")
                        state = STATE_LANDING

            # ── Draw overlay on frame ──
            # State indicator
            state_color = {
                STATE_WAYPOINTS: (255, 200, 0),   # cyan
                STATE_CENTERING: (0, 255, 255),    # yellow
                STATE_HOVERING: (0, 255, 0),       # green
                STATE_LANDING: (0, 165, 255),      # orange
                STATE_RTL: (0, 0, 255),            # red
            }.get(state, (255, 255, 255))

            cv2.putText(frame, state, (10, 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, state_color, 2)

            # Crosshair
            cv2.drawMarker(frame, (cx, cy), (0, 255, 255),
                           cv2.MARKER_CROSS, 20, 1)

            # Detection info
            if found:
                cv2.circle(frame, (int(px), int(py)), 15, (0, 255, 0), 2)
                cv2.line(frame, (cx, cy), (int(px), int(py)), (0, 255, 0), 2)
                cv2.putText(frame, f"conf={conf:.2f}", (int(px)+20, int(py)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

            # Telemetry bar
            alt_str = f"Alt:{alt:.1f}m" if alt else "Alt:?"
            wp_str = f"WP:{wp_index}/{len(waypoints)}" if state == STATE_WAYPOINTS else ""
            det_str = f"Det:{total_detections}"
            cv2.putText(frame, f"{alt_str}  {wp_str}  {det_str}",
                        (10, h - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)

            # Update stream
            if STREAM:
                with _stream_lock:
                    _stream_frame = frame

            # Display
            if not HEADLESS:
                cv2.imshow("Detect & Center", frame)
                key = cv2.waitKey(1) & 0xFF
            else:
                # Non-blocking key check not available in headless
                # Operator uses Ctrl+C for RTL
                key = 0xFF

            # ── Operator keys ──
            if key == ord('l'):
                print(f"\n  Operator: LAND")
                set_mode(mav, MODE_LAND, "LAND")
                state = STATE_LANDING
            elif key == ord('r'):
                print(f"\n  Operator: RESUME waypoints")
                state = STATE_WAYPOINTS
                consecutive_detections = 0
            elif key == ord('q'):
                print(f"\n  Operator: RTL")
                state = STATE_RTL

    except KeyboardInterrupt:
        print("\n  Ctrl+C — RTL")
        mav.mav.command_long_send(
            mav.target_system, mav.target_component,
            mavutil.mavlink.MAV_CMD_DO_SET_MODE, 0,
            mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
            MODE_RTL, 0, 0, 0, 0, 0)

    # ── Cleanup ──
    if not HEADLESS:
        cv2.destroyAllWindows()
    eyes.release()
    mav.close()

    print(f"\n{'='*60}")
    print(f"  MISSION COMPLETE")
    print(f"{'='*60}")
    print(f"  Frames:     {frame_count}")
    print(f"  Detections: {total_detections}")
    print(f"  Waypoints:  {wp_index}/{len(waypoints)} reached")
    print()


if __name__ == "__main__":
    main()
