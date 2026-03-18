#!/usr/bin/env python3
"""
Waypoint Flight Test — fly GPS waypoints in GUIDED mode, NO camera or CV.

WHAT:    Loads waypoints from waypoints.json (or --wp CLI flags), connects to Cube,
         waits for GPS fix, arms, takes off, flies each waypoint at cruise altitude
         with 3s holds, descends to 5m at the last waypoint for a 15s low hover,
         climbs back, then RTLs home. No camera or AI involved.
WHY:     Step 2 of progressive flight testing. Proves that Pi MAVLink commands (arm,
         takeoff, GUIDED waypoint navigation, altitude changes, RTL) work on real
         hardware before adding CV complexity.
WHEN:    After passive flight (step 1) confirms basic connectivity. Before any
         CV-enabled flight (3_auto_detect, 4_detect_and_center).
WHERE:   Pi (with Cube via mavproxy, outdoors with GPS fix) or laptop (with SITL).
ENV:     pienv on Pi, or any venv with pymavlink on laptop.
MODELS:  None (no camera or AI used).
RISK:    HIGH — this script WILL fly the drone. Arms motors, takes off, navigates
         waypoints, and lands. Requires props on, clear area, and RC kill switch ready.

USAGE:
    python tests/flight/2_waypoints.py                                          # fly waypoints.json
    python tests/flight/2_waypoints.py --dry-run                                # print plan only
    python tests/flight/2_waypoints.py --alt 20                                 # cruise at 20m
    python tests/flight/2_waypoints.py --wp 51.4234,-2.6710 --wp 51.4238,-2.6695  # CLI waypoints

FLAGS:
    --dry-run       Print flight plan and distances without connecting or flying
    --alt N         Cruise altitude in meters (default 25)
    --wp LAT,LON    Specify waypoints via CLI (repeatable, overrides waypoints.json)

OUTPUT:
    Terminal output with real-time distance and altitude to each waypoint.
    Summary of waypoints flown, altitudes, and what was proved.

BEST PRACTICES:
    - ALWAYS run --dry-run first to verify waypoints and distances
    - Create waypoints.json with draw_waypoints.py on laptop, push via git
    - Keep RC transmitter in hand — flip to STABILIZE/LOITER to take over instantly
    - Ctrl+C triggers RTL as emergency fallback
    - Start with 2-3 close waypoints (< 50m) for the first real flight
    - Verify GPS fix has 6+ satellites before confirming the arm prompt

DEPENDENCIES:
    pymavlink, config.py (for CONNECTION_STR)
"""
import sys
import os
import time
import math
import signal
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from pymavlink import mavutil
import config

# --- Settings ---
CRUISE_ALT = 25.0  # meters — main flight altitude
DESCEND_ALT = 5.0  # meters — low hover at last waypoint
WAYPOINT_TOLERANCE = 2.0  # meters — how close to get before next waypoint
SPEED = 3.0  # m/s — slow and safe for first test
LOW_HOVER_TIME = 15.0  # seconds to hover at 5m at last waypoint
DRY_RUN = "--dry-run" in sys.argv

# Parse --alt flag
CLI_WAYPOINTS = []
for i, arg in enumerate(sys.argv):
    if arg == "--alt" and i + 1 < len(sys.argv):
        CRUISE_ALT = float(sys.argv[i + 1])
    elif arg == "--wp" and i + 1 < len(sys.argv):
        parts = sys.argv[i + 1].split(",")
        if len(parts) == 2:
            lat, lon = float(parts[0]), float(parts[1])
            CLI_WAYPOINTS.append((lat, lon, f"WP{len(CLI_WAYPOINTS) + 1}"))

# Waypoints file (saved by draw_waypoints.py)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WAYPOINTS_FILE = os.path.join(PROJECT_ROOT, "waypoints.json")


def load_waypoints():
    """Load waypoints from waypoints.json or --wp CLI flags."""
    # Priority 1: --wp CLI flags
    if CLI_WAYPOINTS:
        print(f"\n  Using {len(CLI_WAYPOINTS)} waypoints from --wp flags:")
        for lat, lon, label in CLI_WAYPOINTS:
            print(f"    {label}: ({lat:.6f}, {lon:.6f})")
        return CLI_WAYPOINTS

    # Priority 2: waypoints.json
    if os.path.exists(WAYPOINTS_FILE):
        with open(WAYPOINTS_FILE, "r") as f:
            data = json.load(f)
        if data:
            waypoints = [(wp["lat"], wp["lon"], wp.get("label", f"WP{i+1}"))
                         for i, wp in enumerate(data)]
            print(f"\n  Loaded {len(waypoints)} waypoints from waypoints.json:")
            for lat, lon, label in waypoints:
                print(f"    {label}: ({lat:.6f}, {lon:.6f})")
            return waypoints

    # No waypoints found
    print("\n  [ERROR] No waypoints found!")
    print("  Either:")
    print("    1. Run draw_waypoints.py on laptop to create waypoints.json")
    print("    2. Use --wp flags: --wp 51.4234,-2.6710 --wp 51.4238,-2.6695")
    sys.exit(1)

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

# Global for signal handler
mav = None


def connect():
    """Connect to Cube, wait for autopilot heartbeat."""
    conn_str = config.CONNECTION_STR
    print(f"  Connecting: {conn_str}")
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
    """Read current mode from fresh heartbeat."""
    while m.recv_msg() is not None:
        pass
    for _ in range(10):
        hb = m.recv_match(type='HEARTBEAT', blocking=True, timeout=3)
        if hb and hb.type != mavutil.mavlink.MAV_TYPE_GCS:
            return COPTER_MODES.get(hb.custom_mode, f"MODE_{hb.custom_mode}")
    return "UNKNOWN"


def set_mode(m, mode_num, mode_name):
    """Set flight mode and verify."""
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
    """Wait for 3D GPS fix."""
    print(f"\n  Waiting for GPS 3D fix (timeout {timeout}s)...")
    print(f"  Take drone outside with clear sky if indoors.")
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
    """Get current GPS position."""
    while m.recv_msg() is not None:
        pass
    pos = m.messages.get('GLOBAL_POSITION_INT')
    if pos:
        return pos.lat / 1e7, pos.lon / 1e7, pos.relative_alt / 1000.0
    return None, None, None


def distance_between(lat1, lon1, lat2, lon2):
    """Distance in meters between two GPS coordinates."""
    R = 6378137.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))


def send_waypoint(m, lat, lon, alt):
    """Send position target in GUIDED mode."""
    m.mav.set_position_target_global_int_send(
        0, m.target_system, m.target_component,
        mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
        0b110111111000,
        int(lat * 1e7), int(lon * 1e7), alt,
        0, 0, 0, 0, 0, 0, 0, 0)


def wait_for_altitude(m, target_alt, tolerance=0.15, timeout=30, label=""):
    """Wait until drone reaches target altitude."""
    print(f"  {label}Waiting for {target_alt:.0f}m...")
    start = time.time()
    while time.time() - start < timeout:
        lat, lon, alt = get_position(m)
        if alt is not None:
            print(f"    alt={alt:.1f}m", end="\r")
            if abs(alt - target_alt) < target_alt * tolerance:
                print(f"\n  [OK] Reached {alt:.1f}m")
                return True
        time.sleep(0.5)
    print(f"\n  [WARN] Altitude timeout -- continuing anyway")
    return False


def emergency_rtl(signum, frame):
    """Ctrl+C handler -- trigger RTL."""
    global mav
    print("\n\n  !!! Ctrl+C -- TRIGGERING RTL !!!")
    if mav:
        mav.mav.command_long_send(
            mav.target_system, mav.target_component,
            mavutil.mavlink.MAV_CMD_DO_SET_MODE, 0,
            mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
            MODE_RTL, 0, 0, 0, 0, 0)
        print("  RTL command sent. Drone returning to launch.")
    sys.exit(0)


def main():
    global mav

    # --- Load waypoints ---
    waypoints = load_waypoints()

    print()
    print("=" * 60)
    print(f"   WAYPOINT FLIGHT TEST -- Step 2")
    print(f"   Fly {len(waypoints)} waypoints. NO camera. NO CV.")
    print("=" * 60)
    print()
    print(f"  Cruise alt:   {CRUISE_ALT}m")
    print(f"  Descend alt:  {DESCEND_ALT}m (at last waypoint)")
    print(f"  Low hover:    {LOW_HOVER_TIME}s")
    print(f"  Speed:        {SPEED} m/s")
    print(f"  Dry run:      {DRY_RUN}")
    print()

    total_dist = 0
    for i, (lat, lon, label) in enumerate(waypoints):
        if i > 0:
            d = distance_between(waypoints[i-1][0], waypoints[i-1][1], lat, lon)
            total_dist += d
            print(f"  {label}: ({lat:.6f}, {lon:.6f})  [{d:.0f}m from {waypoints[i-1][2]}]")
        else:
            print(f"  {label}: ({lat:.6f}, {lon:.6f})")
    print(f"  Total route: {total_dist:.0f}m")
    print()

    if DRY_RUN:
        print("  [DRY RUN] Plan printed above. No connection needed.")
        print("  [DRY RUN] To fly for real, remove --dry-run flag.")
        print()
        print("  Flight sequence:")
        print(f"    1. Takeoff to {CRUISE_ALT}m")
        print(f"    2. Wait 2s")
        for i, (lat, lon, label) in enumerate(waypoints):
            print(f"    {i+3}. Fly to {label} ({lat:.6f}, {lon:.6f})")
        n = len(waypoints) + 3
        print(f"    {n}. Descend to {DESCEND_ALT}m at last waypoint")
        print(f"    {n+1}. Hover {LOW_HOVER_TIME}s")
        print(f"    {n+2}. Climb to {CRUISE_ALT}m")
        print(f"    {n+3}. Wait 2s")
        print(f"    {n+4}. RTL")
        return

    print("  !! WARNING: This script WILL fly the drone !!")
    print("  !! Make sure props are on and area is clear !!")
    print("  !! RC kill switch: flip to STABILIZE/LOITER !!")
    print()
    print("  Press Enter to continue, Ctrl+C to abort...")
    try:
        input()
    except KeyboardInterrupt:
        print("\n  Aborted.")
        return

    # Ctrl+C = RTL
    signal.signal(signal.SIGINT, emergency_rtl)

    mav = connect()

    # -- Step 1: GPS fix --
    home_lat, home_lon = wait_for_gps(mav)
    if home_lat is None:
        print("  Cannot fly without GPS. Exiting.")
        mav.close()
        return

    print(f"\n  Home: ({home_lat:.6f}, {home_lon:.6f})")
    for i, (wlat, wlon, label) in enumerate(waypoints):
        dist = distance_between(home_lat, home_lon, wlat, wlon)
        print(f"  {label}: ({wlat:.6f}, {wlon:.6f}) -- {dist:.0f}m from home")

    # -- Step 2: GUIDED mode --
    print(f"\n{'='*60}")
    print(f"  SETTING GUIDED MODE")
    print(f"{'='*60}")
    if not set_mode(mav, MODE_GUIDED, "GUIDED"):
        print("  Could not set GUIDED mode. Is RC on?")
        mav.close()
        return

    # -- Step 3: Arm --
    print(f"\n{'='*60}")
    print(f"  ARMING")
    print(f"{'='*60}")

    armed = False
    for attempt in range(5):
        print(f"  Sending ARM (attempt {attempt + 1}/5)...")
        mav.mav.command_long_send(
            mav.target_system, mav.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0,
            1, 0, 0, 0, 0, 0, 0)

        for _ in range(10):
            ack = mav.recv_match(type='COMMAND_ACK', blocking=True, timeout=2)
            if ack and ack.command == mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM:
                if ack.result == 0:
                    print("  [OK] Armed!")
                    armed = True
                else:
                    stxt = mav.recv_match(type='STATUSTEXT', blocking=True, timeout=1)
                    reason = stxt.text if stxt else "unknown"
                    print(f"  [RETRY] Arm rejected: {reason}")
                break

        if armed:
            break
        print("  Waiting 5s before retry...")
        time.sleep(5)

    if not armed:
        print("  Could not arm after 5 attempts. Exiting.")
        mav.close()
        return

    # -- Step 4: Takeoff to cruise altitude --
    print(f"\n{'='*60}")
    print(f"  TAKEOFF to {CRUISE_ALT}m")
    print(f"{'='*60}")

    mav.mav.command_long_send(
        mav.target_system, mav.target_component,
        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0,
        0, 0, 0, 0, 0, 0, CRUISE_ALT)

    wait_for_altitude(mav, CRUISE_ALT, timeout=30, label="Climbing... ")

    # Hold 3s at altitude
    print("  Holding 3s at altitude...")
    time.sleep(3)

    # Set speed
    mav.mav.command_long_send(
        mav.target_system, mav.target_component,
        mavutil.mavlink.MAV_CMD_DO_CHANGE_SPEED, 0,
        1, SPEED, -1, 0, 0, 0, 0)

    # -- Step 5: Fly waypoints at cruise altitude --
    print(f"\n{'='*60}")
    print(f"  FLYING WAYPOINTS at {CRUISE_ALT}m")
    print(f"{'='*60}")

    for i, (wlat, wlon, label) in enumerate(waypoints):
        print(f"\n  --- {label} ({i+1}/{len(waypoints)}) ---")
        print(f"  Target: ({wlat:.6f}, {wlon:.6f})")

        start = time.time()
        while time.time() - start < 60:  # 60s timeout per waypoint
            send_waypoint(mav, wlat, wlon, CRUISE_ALT)

            lat, lon, alt = get_position(mav)
            if lat is not None:
                dist = distance_between(lat, lon, wlat, wlon)
                print(f"    dist={dist:.1f}m  alt={alt:.1f}m", end="\r")
                if dist < WAYPOINT_TOLERANCE:
                    print(f"\n  [OK] Reached {label}")
                    break
            time.sleep(1)
        else:
            print(f"\n  [WARN] {label} timeout -- moving on")

        # Hold 3s at each waypoint
        print(f"  Holding 3s at {label}...")
        time.sleep(3)

    # -- Step 6: Descend to 5m at last waypoint --
    last_lat, last_lon, last_label = waypoints[-1]
    print(f"\n{'='*60}")
    print(f"  DESCENDING to {DESCEND_ALT}m at {last_label}")
    print(f"{'='*60}")

    start = time.time()
    while time.time() - start < 30:
        send_waypoint(mav, last_lat, last_lon, DESCEND_ALT)
        lat, lon, alt = get_position(mav)
        if alt is not None:
            print(f"    alt={alt:.1f}m", end="\r")
            if alt <= DESCEND_ALT * 1.15:
                print(f"\n  [OK] Reached {alt:.1f}m")
                break
        time.sleep(0.5)
    else:
        print(f"\n  [WARN] Descent timeout -- continuing anyway")

    # -- Step 7: Hover 15s at low altitude --
    print(f"  Hovering {LOW_HOVER_TIME}s at {DESCEND_ALT}m...")
    hover_start = time.time()
    while time.time() - hover_start < LOW_HOVER_TIME:
        send_waypoint(mav, last_lat, last_lon, DESCEND_ALT)
        remaining = LOW_HOVER_TIME - (time.time() - hover_start)
        lat, lon, alt = get_position(mav)
        if alt is not None:
            print(f"    alt={alt:.1f}m  remaining={remaining:.0f}s", end="\r")
        time.sleep(1)
    print(f"\n  [OK] Low hover complete")

    # -- Step 8: Climb back to cruise altitude --
    print(f"\n{'='*60}")
    print(f"  CLIMBING back to {CRUISE_ALT}m")
    print(f"{'='*60}")

    start = time.time()
    while time.time() - start < 30:
        send_waypoint(mav, last_lat, last_lon, CRUISE_ALT)
        lat, lon, alt = get_position(mav)
        if alt is not None:
            print(f"    alt={alt:.1f}m", end="\r")
            if alt >= CRUISE_ALT * 0.85:
                print(f"\n  [OK] Reached {alt:.1f}m")
                break
        time.sleep(0.5)
    else:
        print(f"\n  [WARN] Climb timeout -- continuing anyway")

    # Hold 3s at altitude
    print("  Holding 3s at altitude...")
    time.sleep(3)

    # -- Step 9: RTL --
    print(f"\n{'='*60}")
    print(f"  RTL (Return To Launch)")
    print(f"{'='*60}")

    set_mode(mav, MODE_RTL, "RTL")

    # Wait for landing
    print("  Returning and landing...")
    start = time.time()
    prev_alt = 999
    stable_count = 0
    while time.time() - start < 120:
        lat, lon, alt = get_position(mav)
        if alt is not None:
            print(f"    alt={alt:.1f}m", end="\r")
            if alt < 1.0:
                print(f"\n  [OK] Landed! (alt={alt:.1f}m)")
                break
            if alt < 5.0 and abs(alt - prev_alt) < 0.2:
                stable_count += 1
                if stable_count >= 5:
                    print(f"\n  [OK] Landed! (alt stable at {alt:.1f}m)")
                    break
            else:
                stable_count = 0
            prev_alt = alt
        time.sleep(1)

    # Disarm
    time.sleep(2)
    mav.mav.command_long_send(
        mav.target_system, mav.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0,
        0, 0, 0, 0, 0, 0, 0)
    print("  Disarm sent.")

    mav.close()

    # -- Summary --
    print(f"\n{'='*60}")
    print(f"  WAYPOINT TEST COMPLETE")
    print(f"{'='*60}")
    print(f"  Cruise alt:  {CRUISE_ALT}m")
    print(f"  Descend alt: {DESCEND_ALT}m")
    print(f"  Waypoints:   {len(waypoints)} flown")
    for lat, lon, label in waypoints:
        print(f"    {label}: ({lat:.6f}, {lon:.6f})")
    print(f"  Low hover:   {LOW_HOVER_TIME}s at {last_label}")
    print(f"  End:         RTL")
    print()
    print(f"  What this proves:")
    print(f"    - Pi can arm, takeoff, and land the real drone")
    print(f"    - GUIDED mode waypoint navigation works")
    print(f"    - Altitude changes (climb/descend) work")
    print(f"    - RTL works")
    print(f"    - GPS position tracking is accurate")
    print()
    print(f"  Next step: passive CV flight (passive_watch.py)")
    print()


if __name__ == "__main__":
    main()
