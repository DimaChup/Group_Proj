#!/usr/bin/env python3
"""
SITL-to-Real Mapping Verification — Interactive Visual Tests

Steps through each drone behavior and asks YOU to visually confirm it works.
Run on bench (no props) or in SITL. Each test is independent — skip with N.

Usage:
    SITL:  DRONE_MODE=SIMULATION python tests/flight/0d_mapping_test.py
    Bench: python tests/flight/0d_mapping_test.py

Tests:
    1. Direction flight (N/E/S/W) — does it move the right way?
    2. Yaw rotation — does it point the right direction?
    3. Speed changes — does it speed up/slow down?
    4. Mode changes — does Mission Planner show correct mode?
    5. Servo release — do you hear/see the servo move?
    6. Landing offset (N/E/S/W) — is the GPS offset correct?
    7. Altitude hold — does it stay at the right height?
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from pymavlink import mavutil
import config
import math

# ─── Helpers ───────────────────────────────────────────────────────────

def ask(question):
    """Ask user Y/N and return True/False."""
    while True:
        resp = input(f"\n  >>> {question} [Y/N/S(kip)]: ").strip().lower()
        if resp in ('y', 'yes'): return True
        if resp in ('n', 'no'): return False
        if resp in ('s', 'skip'): return None

def wait_heartbeat(master):
    print("  Waiting for heartbeat...")
    master.wait_heartbeat(timeout=10)
    print(f"  Heartbeat from system {master.target_system}")

def set_mode(master, mode_name):
    mode_map = {'GUIDED': 4, 'STABILIZE': 0, 'LOITER': 5, 'RTL': 6, 'LAND': 9}
    mode_id = mode_map.get(mode_name, 4)
    master.mav.set_mode_send(master.target_system,
        mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED, mode_id)
    time.sleep(1)

def arm(master):
    master.mav.command_long_send(master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, 1, 0, 0, 0, 0, 0, 0)
    time.sleep(2)

def disarm(master):
    master.mav.command_long_send(master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, 0, 0, 0, 0, 0, 0, 0)
    time.sleep(1)

def send_velocity(master, vn, ve, vd, duration=3):
    """Send velocity command for `duration` seconds."""
    end = time.time() + duration
    while time.time() < end:
        master.mav.set_position_target_local_ned_send(
            0, master.target_system, master.target_component,
            mavutil.mavlink.MAV_FRAME_LOCAL_NED,
            0b0000111111000111,  # velocity only
            0, 0, 0,
            vn, ve, vd,
            0, 0, 0, 0, 0)
        time.sleep(0.1)

def send_yaw(master, heading_deg):
    """Command drone to face a heading."""
    master.mav.command_long_send(master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_CONDITION_YAW, 0,
        heading_deg, 45, 1, 0, 0, 0, 0)  # 45 deg/s, CW, absolute
    time.sleep(3)

def send_servo(master, channel, pwm):
    """Send servo command."""
    master.mav.command_long_send(master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_DO_SET_SERVO, 0,
        channel, pwm, 0, 0, 0, 0, 0)
    time.sleep(1)

def get_heading(master):
    """Read current heading from telemetry."""
    msg = master.recv_match(type='VFR_HUD', blocking=True, timeout=3)
    if msg:
        return msg.heading
    return None

def get_position(master):
    """Read current GPS."""
    msg = master.recv_match(type='GLOBAL_POSITION_INT', blocking=True, timeout=3)
    if msg:
        return msg.lat / 1e7, msg.lon / 1e7, msg.relative_alt / 1000.0
    return None, None, None

def takeoff_if_sitl(master):
    """In SITL, arm and takeoff to 20m. On bench, just arm."""
    set_mode(master, 'GUIDED')
    time.sleep(1)
    arm(master)

    if os.environ.get('DRONE_MODE') == 'SIMULATION':
        print("  SITL: Taking off to 20m...")
        master.mav.command_long_send(master.target_system, master.target_component,
            mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 0, 0, 0, 20)
        time.sleep(10)
        print("  Airborne at ~20m")
    else:
        print("  Bench mode: armed (no takeoff)")


# ─── Tests ─────────────────────────────────────────────────────────────

results = []

def run_test(name, fn):
    print(f"\n{'='*60}")
    print(f"  TEST: {name}")
    print(f"{'='*60}")
    resp = ask(f"Run this test?")
    if resp is None or resp is False:
        results.append((name, "SKIPPED"))
        return
    try:
        passed = fn()
        if passed is True:
            results.append((name, "PASS"))
            print(f"  >>> PASS")
        elif passed is False:
            results.append((name, "FAIL"))
            print(f"  >>> FAIL")
        else:
            results.append((name, "SKIPPED"))
    except Exception as e:
        results.append((name, f"ERROR: {e}"))
        print(f"  >>> ERROR: {e}")


def test_direction_flight(master):
    """Fly N/E/S/W and ask user to confirm direction."""
    directions = [
        ("NORTH", 2, 0, 0),
        ("EAST",  0, 2, 0),
        ("SOUTH", -2, 0, 0),
        ("WEST",  0, -2, 0),
    ]
    all_pass = True
    for name, vn, ve, vd in directions:
        print(f"\n  Flying {name} for 3 seconds (2 m/s)...")
        send_velocity(master, vn, ve, vd, duration=3)
        # Stop
        send_velocity(master, 0, 0, 0, duration=1)
        r = ask(f"Did the drone move {name}?")
        if r is False:
            print(f"  !!! {name} direction MISMATCH")
            all_pass = False
        elif r is None:
            continue
    return all_pass


def test_yaw_rotation(master):
    """Point drone N/E/S/W and ask user to confirm heading."""
    headings = [
        ("NORTH", 0),
        ("EAST", 90),
        ("SOUTH", 180),
        ("WEST", 270),
    ]
    all_pass = True
    for name, deg in headings:
        print(f"\n  Yawing to {name} ({deg} deg)...")
        send_yaw(master, deg)
        actual = get_heading(master)
        print(f"  Telemetry heading: {actual} deg")
        r = ask(f"Is the drone pointing {name}? (telemetry says {actual} deg)")
        if r is False:
            all_pass = False
        elif r is None:
            continue
    return all_pass


def test_speed_change(master):
    """Fly at different speeds, ask user to confirm."""
    print("\n  Flying NORTH at 1 m/s for 3 seconds...")
    send_velocity(master, 1, 0, 0, duration=3)
    send_velocity(master, 0, 0, 0, duration=1)
    r1 = ask("Did the drone move slowly?")

    print("\n  Flying NORTH at 4 m/s for 3 seconds...")
    send_velocity(master, 4, 0, 0, duration=3)
    send_velocity(master, 0, 0, 0, duration=1)
    r2 = ask("Did the drone move noticeably faster?")

    if r1 is False or r2 is False:
        return False
    return True


def test_mode_changes(master):
    """Switch modes, ask user to confirm on Mission Planner."""
    modes = ['GUIDED', 'LOITER', 'STABILIZE', 'GUIDED']
    all_pass = True
    for mode in modes:
        print(f"\n  Switching to {mode}...")
        set_mode(master, mode)
        time.sleep(1)
        r = ask(f"Does Mission Planner / telemetry show {mode}?")
        if r is False:
            all_pass = False
    return all_pass


def test_servo(master):
    """Trigger servo and ask user to confirm."""
    channel = getattr(config, 'SERVO_CHANNEL', 9)
    pwm_close = getattr(config, 'SERVO_CLOSE_PWM', 1500)
    pwm_partial = getattr(config, 'SERVO_PARTIAL_PWM', 1300)
    pwm_full = getattr(config, 'SERVO_FULL_PWM', 1100)

    print(f"\n  Servo channel: {channel}")
    print(f"  PWM values: close={pwm_close}, partial={pwm_partial}, full={pwm_full}")

    print(f"\n  Sending CLOSE ({pwm_close})...")
    send_servo(master, channel, pwm_close)
    ask("Servo should be in CLOSED position. Ready for next?")

    print(f"\n  Sending PARTIAL release ({pwm_partial})...")
    send_servo(master, channel, pwm_partial)
    r1 = ask("Did the servo move to PARTIAL position?")

    print(f"\n  Sending FULL release ({pwm_full})...")
    send_servo(master, channel, pwm_full)
    r2 = ask("Did the servo move to FULL OPEN position?")

    print(f"\n  Resetting to CLOSED ({pwm_close})...")
    send_servo(master, channel, pwm_close)

    if r1 is False or r2 is False:
        return False
    return True


def test_landing_offset(master):
    """Calculate landing offsets and ask user to verify on map."""
    lat, lon, alt = get_position(master)
    if lat is None:
        print("  No GPS fix — skipping")
        return None

    print(f"\n  Current position: ({lat:.6f}, {lon:.6f}), alt={alt:.1f}m")

    # Calculate 7.5m offset in each direction
    lat_m = 111132.954
    lon_m = 111132.954 * math.cos(math.radians(lat))

    offsets = {
        'N': (lat + 7.5 / lat_m, lon),
        'S': (lat - 7.5 / lat_m, lon),
        'E': (lat, lon + 7.5 / lon_m),
        'W': (lat, lon - 7.5 / lon_m),
    }

    all_pass = True
    for direction, (olat, olon) in offsets.items():
        print(f"\n  Landing {direction}: ({olat:.6f}, {olon:.6f})")
        print(f"    Offset from current: {(olat-lat)*lat_m:.1f}m N, {(olon-lon)*lon_m:.1f}m E")
        r = ask(f"Does landing spot {direction} look correct (7.5m {direction} of current pos)?")
        if r is False:
            all_pass = False
    return all_pass


def test_altitude_hold(master):
    """Check altitude stability."""
    print("\n  Reading altitude 5 times over 5 seconds...")
    alts = []
    for i in range(5):
        _, _, alt = get_position(master)
        if alt is not None:
            alts.append(alt)
            print(f"    Sample {i+1}: {alt:.1f}m")
        time.sleep(1)

    if len(alts) < 3:
        print("  Not enough samples")
        return None

    spread = max(alts) - min(alts)
    avg = sum(alts) / len(alts)
    print(f"\n  Average: {avg:.1f}m, spread: {spread:.1f}m")
    r = ask(f"Altitude stable? (spread={spread:.1f}m, should be <2m)")
    return r


def test_climb_descend(master):
    """Climb and descend, ask user to confirm."""
    print("\n  Climbing 2 m/s for 3 seconds...")
    send_velocity(master, 0, 0, -2, duration=3)  # NED: -vd = climb
    send_velocity(master, 0, 0, 0, duration=1)
    r1 = ask("Did the drone climb?")

    print("\n  Descending 2 m/s for 3 seconds...")
    send_velocity(master, 0, 0, 2, duration=3)  # NED: +vd = descend
    send_velocity(master, 0, 0, 0, duration=1)
    r2 = ask("Did the drone descend?")

    if r1 is False or r2 is False:
        return False
    return True


# ─── Main ──────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  SITL-to-REAL MAPPING VERIFICATION")
    print("  Interactive visual confirmation tests")
    print("=" * 60)
    print()
    print("  This script tests each drone behavior and asks YOU")
    print("  to visually confirm it's correct.")
    print()
    print("  Works on:")
    print("    - SITL (watch god-view / Mission Planner)")
    print("    - Bench with Cube (watch Mission Planner, no props!)")
    print()

    conn_str = config.get_connection_string()
    print(f"  Connecting to: {conn_str}")
    master = mavutil.mavlink_connection(conn_str)
    wait_heartbeat(master)

    # Request data stream
    master.mav.request_data_stream_send(master.target_system, master.target_component,
        mavutil.mavlink.MAV_DATA_STREAM_ALL, 10, 1)
    time.sleep(1)

    is_sitl = os.environ.get('DRONE_MODE') == 'SIMULATION'
    if is_sitl:
        resp = ask("SITL detected. Arm and takeoff to 20m?")
        if resp:
            takeoff_if_sitl(master)
    else:
        print("\n  BENCH MODE — no takeoff. Some tests may be limited.")
        resp = ask("Arm the Cube? (NO PROPS!)")
        if resp:
            set_mode(master, 'GUIDED')
            arm(master)

    # Run tests
    run_test("1. Direction Flight (N/E/S/W)", lambda: test_direction_flight(master))
    run_test("2. Yaw Rotation (N/E/S/W)", lambda: test_yaw_rotation(master))
    run_test("3. Speed Changes (slow/fast)", lambda: test_speed_change(master))
    run_test("4. Climb / Descend", lambda: test_climb_descend(master))
    run_test("5. Mode Changes (GUIDED/LOITER/STABILIZE)", lambda: test_mode_changes(master))
    run_test("6. Servo Release (close/partial/full)", lambda: test_servo(master))
    run_test("7. Landing Offset (N/E/S/W, 7.5m)", lambda: test_landing_offset(master))
    run_test("8. Altitude Hold (stability)", lambda: test_altitude_hold(master))

    # Cleanup
    print("\n  Disarming...")
    set_mode(master, 'STABILIZE')
    disarm(master)

    # Summary
    print(f"\n{'='*60}")
    print("  RESULTS SUMMARY")
    print(f"{'='*60}")
    for name, result in results:
        icon = "PASS" if result == "PASS" else "FAIL" if result == "FAIL" else "SKIP" if result == "SKIPPED" else "ERR"
        print(f"  [{icon:4s}] {name}")

    passed = sum(1 for _, r in results if r == "PASS")
    failed = sum(1 for _, r in results if r == "FAIL")
    skipped = sum(1 for _, r in results if r == "SKIPPED")
    print(f"\n  {passed} passed, {failed} failed, {skipped} skipped")

    if failed > 0:
        print("\n  !!! SOME TESTS FAILED — investigate before flight !!!")
    elif passed > 0:
        print("\n  All tested items PASS — SITL maps to real correctly")

    print()


if __name__ == '__main__':
    main()
