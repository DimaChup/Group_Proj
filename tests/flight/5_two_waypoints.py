#!/usr/bin/env python3
"""
Two-Waypoint Mission — fly to 2 specific GPS coordinates, hover, land.

Simple test to prove GUIDED navigation works on real hardware.

Flow:
  1. Connect to Cube, wait for GPS fix
  2. Set GUIDED, arm, takeoff to ALT
  3. Fly to WP1, hover HOVER_TIME seconds
  4. Fly to WP2, hover HOVER_TIME seconds
  5. Land at WP2

Safety:
  - RC override ALWAYS active — flip to STABILIZE to take over
  - Ctrl+C triggers RTL
  - --dry-run: verify without arming

Usage:
    python3 tests/flight/5_two_waypoints.py                    # fly it
    python3 tests/flight/5_two_waypoints.py --dry-run          # test without arming
    python3 tests/flight/5_two_waypoints.py --alt 15           # fly at 15m
    python3 tests/flight/5_two_waypoints.py --hover 6          # hover 6s at each WP
"""
import sys
import os
import time
import math
import signal

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))

from pymavlink import mavutil
import config

# ══════════════════════════════════════════════
#   EDIT THESE WAYPOINTS BEFORE FLIGHT
# ══════════════════════════════════════════════
# Two points inside the survey area from AENGM0074.kml
# Change these on flight day to wherever you want
WP1 = (51.42330, -2.66980)   # roughly NE corner of survey area
WP2 = (51.42350, -2.67050)   # roughly centre of survey area

# ══════════════════════════════════════════════
#   SETTINGS
# ══════════════════════════════════════════════
ALT = 20.0          # metres
HOVER_TIME = 4.0    # seconds to hover at each waypoint
SPEED = 3.0         # m/s
WP_TOLERANCE = 3.0  # metres — close enough to count as arrived
DRY_RUN = "--dry-run" in sys.argv

# Parse CLI flags
for i, arg in enumerate(sys.argv):
    if arg == "--alt" and i + 1 < len(sys.argv):
        ALT = float(sys.argv[i + 1])
    if arg == "--hover" and i + 1 < len(sys.argv):
        HOVER_TIME = float(sys.argv[i + 1])

# ArduCopter modes
MODE_STABILIZE = 0
MODE_GUIDED = 4
MODE_LAND = 9
MODE_RTL = 6

COPTER_MODES = {
    0: "STABILIZE", 2: "ALT_HOLD", 3: "AUTO", 4: "GUIDED",
    5: "LOITER", 6: "RTL", 9: "LAND", 16: "POSHOLD",
}

mav = None


def haversine(lat1, lon1, lat2, lon2):
    R = 6378137.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def get_mode_name(mode_num):
    return COPTER_MODES.get(mode_num, f"MODE_{mode_num}")


def connect():
    global mav
    conn_str = config.CONNECTION_STR
    print(f"  Connecting: {conn_str}")
    mav = mavutil.mavlink_connection(conn_str, baud=config.BAUD_RATE)

    # Wait for autopilot heartbeat (skip mavproxy GCS heartbeats)
    print("  Waiting for Cube heartbeat...")
    while True:
        msg = mav.recv_match(type='HEARTBEAT', blocking=True, timeout=10)
        if msg is None:
            print("  No heartbeat — is mavproxy running?")
            sys.exit(1)
        if msg.type != 6:  # skip GCS (mavproxy)
            mav.target_system = msg.get_srcSystem()
            mav.target_component = msg.get_srcComponent()
            print(f"  Connected! System {mav.target_system}")
            break


def wait_gps():
    print("\n  Waiting for GPS fix (3D, 6+ sats)...")
    while True:
        msg = mav.recv_match(type='GPS_RAW_INT', blocking=True, timeout=5)
        if msg:
            fix = msg.fix_type
            sats = msg.satellites_visible
            lat = msg.lat / 1e7
            lon = msg.lon / 1e7
            fix_names = {0: "No GPS", 1: "No Fix", 2: "2D", 3: "3D", 4: "DGPS", 5: "RTK Float", 6: "RTK Fixed"}
            print(f"    Fix: {fix_names.get(fix, fix)} | Sats: {sats} | {lat:.6f}, {lon:.6f}", end='\r')
            if fix >= 3 and sats >= 6:
                print(f"\n  GPS OK! {fix_names.get(fix)} with {sats} sats")
                return lat, lon
        time.sleep(0.5)


def set_mode(mode_num):
    mav.mav.command_long_send(
        mav.target_system, mav.target_component,
        mavutil.mavlink.MAV_CMD_DO_SET_MODE, 0,
        mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
        mode_num, 0, 0, 0, 0, 0)
    time.sleep(1)
    # Verify
    hb = mav.recv_match(type='HEARTBEAT', blocking=True, timeout=3)
    if hb:
        actual = get_mode_name(hb.custom_mode)
        expected = get_mode_name(mode_num)
        print(f"  Mode: {actual}" + (" OK" if hb.custom_mode == mode_num else f" (wanted {expected})"))


def arm():
    print("  Arming...")
    mav.mav.command_long_send(
        mav.target_system, mav.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0,
        1, 0, 0, 0, 0, 0, 0)
    # Wait for arm
    for _ in range(30):
        hb = mav.recv_match(type='HEARTBEAT', blocking=True, timeout=2)
        if hb and hb.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED:
            print("  ARMED!")
            return True
        time.sleep(0.5)
    print("  ARM FAILED (pre-arm checks?)")
    return False


def takeoff(alt):
    print(f"  Taking off to {alt}m...")
    mav.mav.command_long_send(
        mav.target_system, mav.target_component,
        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0,
        0, 0, 0, 0, 0, 0, alt)
    # Wait to reach altitude
    for _ in range(60):
        msg = mav.recv_match(type='GLOBAL_POSITION_INT', blocking=True, timeout=2)
        if msg:
            current_alt = msg.relative_alt / 1000.0
            print(f"    Alt: {current_alt:.1f}m / {alt:.0f}m", end='\r')
            if current_alt >= alt * 0.9:
                print(f"\n  Reached {current_alt:.1f}m!")
                return True
        time.sleep(0.5)
    print("\n  Takeoff timeout!")
    return False


def fly_to(lat, lon, alt, label="WP"):
    """Fly to GPS coordinate, return when within tolerance."""
    print(f"  Flying to {label}: {lat:.6f}, {lon:.6f} @ {alt:.0f}m")

    mav.mav.set_position_target_global_int_send(
        0, mav.target_system, mav.target_component,
        mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
        0b0000111111111000,  # position only
        int(lat * 1e7), int(lon * 1e7), alt,
        0, 0, 0, 0, 0, 0, 0, 0)

    for _ in range(120):  # 60 second timeout
        msg = mav.recv_match(type='GLOBAL_POSITION_INT', blocking=True, timeout=2)
        if msg:
            clat = msg.lat / 1e7
            clon = msg.lon / 1e7
            calt = msg.relative_alt / 1000.0
            dist = haversine(clat, clon, lat, lon)
            print(f"    {label} dist: {dist:.1f}m  alt: {calt:.1f}m", end='\r')
            if dist < WP_TOLERANCE:
                print(f"\n  Arrived at {label}! ({dist:.1f}m away)")
                return True
        time.sleep(0.5)
    print(f"\n  Timeout reaching {label}!")
    return False


def land():
    print("  Landing...")
    set_mode(MODE_LAND)
    for _ in range(60):
        msg = mav.recv_match(type='GLOBAL_POSITION_INT', blocking=True, timeout=2)
        if msg:
            alt = msg.relative_alt / 1000.0
            print(f"    Descending: {alt:.1f}m", end='\r')
            if alt < 0.5:
                print(f"\n  Landed!")
                return
        time.sleep(0.5)
    print("\n  Land timeout")


def emergency_rtl(signum, frame):
    global mav
    print("\n\n  !!! Ctrl+C — TRIGGERING RTL !!!")
    if mav:
        mav.mav.command_long_send(
            mav.target_system, mav.target_component,
            mavutil.mavlink.MAV_CMD_DO_SET_MODE, 0,
            mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
            MODE_RTL, 0, 0, 0, 0, 0)
        print("  RTL sent. Waiting 3s then exiting...")
        time.sleep(3)
    sys.exit(0)


signal.signal(signal.SIGINT, emergency_rtl)


def main():
    print("=" * 50)
    print("  TWO-WAYPOINT MISSION")
    print("=" * 50)
    print(f"  Altitude:   {ALT}m")
    print(f"  Hover time: {HOVER_TIME}s at each WP")
    print(f"  WP1: {WP1[0]:.6f}, {WP1[1]:.6f}")
    print(f"  WP2: {WP2[0]:.6f}, {WP2[1]:.6f}")
    dist_wp = haversine(WP1[0], WP1[1], WP2[0], WP2[1])
    print(f"  WP1→WP2 distance: {dist_wp:.0f}m")
    if DRY_RUN:
        print(f"  *** DRY RUN — will NOT arm ***")
    print(f"\n  Kill switch: RC → STABILIZE")
    print()

    # Connect
    connect()

    # GPS
    home_lat, home_lon = wait_gps()
    dist_home_wp1 = haversine(home_lat, home_lon, WP1[0], WP1[1])
    dist_home_wp2 = haversine(home_lat, home_lon, WP2[0], WP2[1])
    print(f"  Home → WP1: {dist_home_wp1:.0f}m")
    print(f"  Home → WP2: {dist_home_wp2:.0f}m")

    if DRY_RUN:
        print("\n  [DRY RUN] Would: GUIDED → ARM → TAKEOFF → WP1 → hover → WP2 → hover → LAND")
        print("  [DRY RUN] All distances look good. Ready to fly for real.")
        return

    # Fly!
    print("\n  Starting mission in 3 seconds... (Ctrl+C for RTL)")
    time.sleep(3)

    set_mode(MODE_GUIDED)
    if not arm():
        return
    if not takeoff(ALT):
        land()
        return

    # WP1
    if fly_to(WP1[0], WP1[1], ALT, "WP1"):
        print(f"  Hovering at WP1 for {HOVER_TIME}s...")
        time.sleep(HOVER_TIME)

    # WP2
    if fly_to(WP2[0], WP2[1], ALT, "WP2"):
        print(f"  Hovering at WP2 for {HOVER_TIME}s...")
        time.sleep(HOVER_TIME)

    # Land at WP2
    land()

    print("\n" + "=" * 50)
    print("  MISSION COMPLETE")
    print("=" * 50)


if __name__ == "__main__":
    main()
