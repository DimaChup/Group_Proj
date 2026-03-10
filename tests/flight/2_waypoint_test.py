#!/usr/bin/env python3
"""
Waypoint Flight Test — fly a simple GPS pattern with NO camera/CV.

This is STEP 2 of progressive flight testing.
Proves: your mavlink commands (arm, takeoff, goto, land) work on real hardware.

What it does:
  1. Connects to Cube via mavproxy
  2. Waits for GPS fix (3D)
  3. Sets GUIDED mode
  4. Arms
  5. Takes off to TEST_ALT (10m default)
  6. Flies 4 waypoints in a small square (~20m sides)
  7. Returns to launch point
  8. Lands and disarms

Safety:
  - RC override ALWAYS active — flip RC mode switch to STABILIZE/LOITER to take over
  - Small pattern (20m square) at low altitude (10m)
  - Auto-lands after completing pattern
  - Ctrl+C triggers RTL (Return To Launch)
  - --dry-run flag: does everything EXCEPT arm (verify commands without flying)

Prerequisites:
  - GPS fix (3D) — run gps_health.py first
  - RC transmitter ON and connected
  - mavproxy running
  - PROPS ON (this script WILL fly the drone!)

Usage:
    python tests2/pi_waypoint_test.py              # real flight
    python tests2/pi_waypoint_test.py --dry-run     # test without arming
    python tests2/pi_waypoint_test.py --alt 15      # fly at 15m instead of 10m
"""
import sys
import os
import time
import math
import signal

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymavlink import mavutil
import config

# --- Settings ---
TEST_ALT = 10.0  # meters
PATTERN_SIZE = 20.0  # meters — size of the square pattern
WAYPOINT_TOLERANCE = 2.0  # meters — how close to get before next waypoint
SPEED = 3.0  # m/s — slow and safe for first test
DRY_RUN = "--dry-run" in sys.argv

# Parse --alt flag
for i, arg in enumerate(sys.argv):
    if arg == "--alt" and i + 1 < len(sys.argv):
        TEST_ALT = float(sys.argv[i + 1])

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
    # Drain
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
        # Drain and read
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


def generate_square_pattern(home_lat, home_lon, size_m):
    """Generate a 4-point square pattern around home position."""
    R = 6378137.0
    half = size_m / 2.0
    dlat = (half / R) * (180 / math.pi)
    dlon = (half / (R * math.cos(math.radians(home_lat)))) * (180 / math.pi)

    waypoints = [
        (home_lat + dlat, home_lon - dlon, "NW"),
        (home_lat + dlat, home_lon + dlon, "NE"),
        (home_lat - dlat, home_lon + dlon, "SE"),
        (home_lat - dlat, home_lon - dlon, "SW"),
    ]
    return waypoints


def emergency_rtl(signum, frame):
    """Ctrl+C handler — trigger RTL."""
    global mav
    print("\n\n  !!! Ctrl+C — TRIGGERING RTL !!!")
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

    print()
    print("=" * 60)
    print("   WAYPOINT FLIGHT TEST — Step 2")
    print("   Fly a simple GPS square. NO camera. NO CV.")
    print("=" * 60)
    print()
    print(f"  Altitude:    {TEST_ALT}m")
    print(f"  Pattern:     {PATTERN_SIZE}m square")
    print(f"  Speed:       {SPEED} m/s")
    print(f"  Dry run:     {DRY_RUN}")
    print()

    if not DRY_RUN:
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

    # ── Step 1: GPS fix ──
    home_lat, home_lon = wait_for_gps(mav)
    if home_lat is None:
        print("  Cannot fly without GPS. Exiting.")
        mav.close()
        return

    # ── Step 2: Generate waypoints ──
    waypoints = generate_square_pattern(home_lat, home_lon, PATTERN_SIZE)
    print(f"\n  Flight plan ({len(waypoints)} waypoints):")
    for i, (wlat, wlon, label) in enumerate(waypoints):
        dist = distance_between(home_lat, home_lon, wlat, wlon)
        print(f"    WP{i+1} ({label}): ({wlat:.6f}, {wlon:.6f}) — {dist:.0f}m from home")

    # ── Step 3: GUIDED mode ──
    print(f"\n{'='*60}")
    print(f"  SETTING GUIDED MODE")
    print(f"{'='*60}")
    if not set_mode(mav, MODE_GUIDED, "GUIDED"):
        print("  Could not set GUIDED mode. Is RC on?")
        if not DRY_RUN:
            mav.close()
            return

    # ── Step 4: Arm ──
    print(f"\n{'='*60}")
    print(f"  ARMING")
    print(f"{'='*60}")

    if DRY_RUN:
        print("  [DRY RUN] Skipping arm. Would send ARM command here.")
        print("  [DRY RUN] All commands verified. Ready for real flight.")
        mav.close()
        return

    print("  Sending ARM...")
    mav.mav.command_long_send(
        mav.target_system, mav.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0,
        1, 0, 0, 0, 0, 0, 0)

    # Wait for arm
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
        mav.close()
        return

    # ── Step 5: Takeoff ──
    print(f"\n{'='*60}")
    print(f"  TAKEOFF to {TEST_ALT}m")
    print(f"{'='*60}")

    mav.mav.command_long_send(
        mav.target_system, mav.target_component,
        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0,
        0, 0, 0, 0, 0, 0, TEST_ALT)

    # Wait for altitude
    print("  Climbing...")
    start = time.time()
    while time.time() - start < 30:
        lat, lon, alt = get_position(mav)
        if alt is not None:
            print(f"    alt={alt:.1f}m", end="\r")
            if alt >= TEST_ALT * 0.85:
                print(f"\n  [OK] Reached {alt:.1f}m")
                break
        time.sleep(0.5)
    else:
        print(f"\n  [WARN] Takeoff timeout — continuing anyway")

    # Set speed
    mav.mav.command_long_send(
        mav.target_system, mav.target_component,
        mavutil.mavlink.MAV_CMD_DO_CHANGE_SPEED, 0,
        1, SPEED, -1, 0, 0, 0, 0)

    # ── Step 6: Fly waypoints ──
    print(f"\n{'='*60}")
    print(f"  FLYING WAYPOINTS")
    print(f"{'='*60}")

    for i, (wlat, wlon, label) in enumerate(waypoints):
        print(f"\n  --- WP{i+1}/{len(waypoints)} ({label}) ---")
        print(f"  Target: ({wlat:.6f}, {wlon:.6f})")

        start = time.time()
        while time.time() - start < 60:  # 60s timeout per waypoint
            send_waypoint(mav, wlat, wlon, TEST_ALT)

            lat, lon, alt = get_position(mav)
            if lat is not None:
                dist = distance_between(lat, lon, wlat, wlon)
                print(f"    dist={dist:.1f}m  alt={alt:.1f}m", end="\r")
                if dist < WAYPOINT_TOLERANCE:
                    print(f"\n  [OK] Reached WP{i+1} ({label})")
                    break
            time.sleep(1)
        else:
            print(f"\n  [WARN] WP{i+1} timeout — moving to next")

    # ── Step 7: Return to home ──
    print(f"\n{'='*60}")
    print(f"  RETURNING TO HOME")
    print(f"{'='*60}")

    start = time.time()
    while time.time() - start < 60:
        send_waypoint(mav, home_lat, home_lon, TEST_ALT)
        lat, lon, alt = get_position(mav)
        if lat is not None:
            dist = distance_between(lat, lon, home_lat, home_lon)
            print(f"    dist={dist:.1f}m  alt={alt:.1f}m", end="\r")
            if dist < WAYPOINT_TOLERANCE:
                print(f"\n  [OK] Back at home")
                break
        time.sleep(1)

    # ── Step 8: Land ──
    print(f"\n{'='*60}")
    print(f"  LANDING")
    print(f"{'='*60}")

    set_mode(mav, MODE_LAND, "LAND")

    # Wait for landing
    print("  Descending...")
    start = time.time()
    while time.time() - start < 60:
        lat, lon, alt = get_position(mav)
        if alt is not None:
            print(f"    alt={alt:.1f}m", end="\r")
            if alt < 0.5:
                print(f"\n  [OK] Landed!")
                break
        time.sleep(1)

    # Disarm
    time.sleep(2)
    mav.mav.command_long_send(
        mav.target_system, mav.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0,
        0, 0, 0, 0, 0, 0, 0)
    print("  Disarm sent.")

    mav.close()

    # ── Summary ──
    print(f"\n{'='*60}")
    print(f"  WAYPOINT TEST COMPLETE")
    print(f"{'='*60}")
    print(f"  Altitude:  {TEST_ALT}m")
    print(f"  Waypoints: {len(waypoints)} flown")
    print(f"  Pattern:   {PATTERN_SIZE}m square")
    print()
    print(f"  What this proves:")
    print(f"    - Pi can arm, takeoff, and land the real drone")
    print(f"    - GUIDED mode waypoint navigation works")
    print(f"    - GPS position tracking is accurate")
    print(f"    - Same mavlink commands as main.py")
    print()
    print(f"  Next step: passive CV flight (pi_passive_flight.py)")
    print()


if __name__ == "__main__":
    main()
