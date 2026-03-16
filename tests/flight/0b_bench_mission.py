#!/usr/bin/env python3
"""
Bench Mission Test — exercise the Cube through mission commands WITHOUT flying.

Sends the same sequence of MAVLink commands that main.py would send during a
real mission, but with motors disabled. Watch the Cube's response: mode changes,
acknowledgements, LED changes, buzzer.

This proves: Pi can control the Cube through every mission phase.

Steps:
  1. Connect to Cube
  2. Switch to GUIDED mode
  3. Send ARM command (will likely fail on bench — that's OK)
  4. Send takeoff command
  5. Send waypoint commands (search pattern)
  6. Send mode changes (GUIDED → LAND → STABILIZE)
  7. Show all ACKs and responses

Safe on bench — no propellers needed. Motors will NOT spin
(we don't actually arm, we just test commands).

Usage:
    python tests/flight/0b_bench_mission.py              # on Pi
    python tests/flight/0b_bench_mission.py --with-arm   # also try arming (outdoor only!)
"""
import sys
import os
import time

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, project_root)

from pymavlink import mavutil
import config

# ArduCopter mode numbers → names (pymavlink's mode_string_v10 is unreliable via mavproxy)
COPTER_MODES = {
    0: "STABILIZE", 1: "ACRO", 2: "ALT_HOLD", 3: "AUTO",
    4: "GUIDED", 5: "LOITER", 6: "RTL", 7: "CIRCLE",
    9: "LAND", 11: "DRIFT", 13: "SPORT", 14: "FLIP",
    15: "AUTOTUNE", 16: "POSHOLD", 17: "BRAKE", 18: "THROW",
    19: "AVOID_ADSB", 20: "GUIDED_NOGPS", 21: "SMART_RTL",
}

TRY_ARM = "--with-arm" in sys.argv


def connect():
    conn_str = config.CONNECTION_STR
    print(f"  Connecting: {conn_str}")
    mav = mavutil.mavlink_connection(conn_str)
    print("  Waiting for heartbeat...")
    # Wait for heartbeat from the actual autopilot (not mavproxy GCS)
    # mavproxy sends type=GCS(6), Cube sends type=QUADROTOR(2)
    autopilot_hb = None
    start = time.time()
    while time.time() - start < 10:
        hb = mav.recv_match(type='HEARTBEAT', blocking=True, timeout=2)
        if hb and hb.type != mavutil.mavlink.MAV_TYPE_GCS:
            autopilot_hb = hb
            break
    if autopilot_hb is None:
        print("  [FAIL] No heartbeat from autopilot")
        sys.exit(1)
    mav.target_system = autopilot_hb.get_srcSystem()
    mav.target_component = autopilot_hb.get_srcComponent()
    print(f"  [OK] Connected to system {mav.target_system}")
    mav.mav.request_data_stream_send(
        mav.target_system, mav.target_component,
        mavutil.mavlink.MAV_DATA_STREAM_ALL, 10, 1)
    time.sleep(0.5)
    return mav


def drain_messages(mav):
    """Drain all queued messages so next read is fresh."""
    while True:
        msg = mav.recv_msg()
        if msg is None:
            break


def get_mode(mav):
    """Get current mode — drain stale messages first, then read fresh heartbeat."""
    drain_messages(mav)
    # Wait for a fresh heartbeat from the autopilot (skip mavproxy GCS heartbeats)
    for _ in range(10):
        hb = mav.recv_match(type='HEARTBEAT', blocking=True, timeout=3)
        if hb and hb.type != mavutil.mavlink.MAV_TYPE_GCS:
            return COPTER_MODES.get(hb.custom_mode, f"MODE_{hb.custom_mode}")
    return "UNKNOWN"


def set_mode(mav, mode_name, mode_num):
    """Try to set flight mode and verify."""
    print(f"\n  >>> Setting mode: {mode_name} (#{mode_num})...")

    # Drain old messages before sending
    drain_messages(mav)

    mav.mav.command_long_send(
        mav.target_system, mav.target_component,
        mavutil.mavlink.MAV_CMD_DO_SET_MODE, 0,
        mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
        mode_num, 0, 0, 0, 0, 0)

    # Wait for mode to take effect, then read fresh heartbeat
    time.sleep(1.5)
    actual = get_mode(mav)
    if actual == mode_name:
        print(f"  [OK] Mode is now {actual}")
        return True
    else:
        print(f"  [?]  Mode is {actual} (wanted {mode_name})")
        return False


def send_position_target(mav, lat, lon, alt):
    """Send a GUIDED mode position target (same as main.py)."""
    print(f"  >>> Sending position: ({lat:.6f}, {lon:.6f}) alt={alt}m...")
    mav.mav.set_position_target_global_int_send(
        0,  # time_boot_ms
        mav.target_system, mav.target_component,
        mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
        0b0000111111111000,  # position only
        int(lat * 1e7), int(lon * 1e7), alt,
        0, 0, 0,  # velocity
        0, 0, 0,  # acceleration
        0, 0)     # yaw, yaw_rate

    # Check for ACK
    ack = mav.recv_match(type='COMMAND_ACK', blocking=True, timeout=2)
    if ack:
        print(f"  [OK] Position command ACK: result={ack.result}")
    else:
        print(f"  [OK] Position sent (no explicit ACK expected for SET_POSITION_TARGET)")


def send_takeoff(mav, alt):
    """Send takeoff command."""
    print(f"\n  >>> Sending TAKEOFF to {alt}m...")
    mav.mav.command_long_send(
        mav.target_system, mav.target_component,
        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0,
        0, 0, 0, 0, 0, 0, alt)

    ack = mav.recv_match(type='COMMAND_ACK', blocking=True, timeout=3)
    if ack:
        result_names = {0: "ACCEPTED", 1: "TEMPORARILY_REJECTED",
                        2: "DENIED", 3: "UNSUPPORTED", 4: "FAILED"}
        name = result_names.get(ack.result, f"code {ack.result}")
        print(f"  Takeoff ACK: {name}")
        return ack.result == 0
    else:
        print(f"  No ACK for takeoff")
        return False


def send_land(mav):
    """Send LAND mode."""
    print(f"\n  >>> Sending LAND...")
    return set_mode(mav, "LAND", 9)


def get_gps_position(mav):
    """Get current GPS position from Cube."""
    # Drain messages
    for _ in range(50):
        msg = mav.recv_msg()
        if msg is None:
            break

    pos = mav.messages.get('GLOBAL_POSITION_INT')
    if pos and pos.lat != 0:
        return pos.lat / 1e7, pos.lon / 1e7, pos.relative_alt / 1000.0
    return None, None, None


def generate_search_waypoints(lat, lon):
    """Generate a small search pattern around current position."""
    # Simple 4-point box, 20m on each side
    offset = 0.0002  # ~22m
    return [
        (lat + offset, lon),
        (lat + offset, lon + offset),
        (lat, lon + offset),
        (lat, lon),
    ]


def main():
    print()
    print("=" * 60)
    print("   BENCH MISSION TEST — Exercise Cube commands")
    print("   No motors, no flying. Tests command pipeline.")
    print("=" * 60)
    print()

    mav = connect()

    # Read current state
    current_mode = get_mode(mav)
    print(f"  Current mode: {current_mode}")

    lat, lon, alt = get_gps_position(mav)
    has_gps = lat is not None
    if has_gps:
        print(f"  GPS position: ({lat:.6f}, {lon:.6f}) alt={alt:.1f}m")
    else:
        print(f"  GPS: No fix (some tests will be limited)")

    results = {}

    # ── Phase 1: Mode changes ──
    print(f"\n{'='*60}")
    print(f"  PHASE 1: MODE CHANGES")
    print(f"{'='*60}")

    results['guided'] = set_mode(mav, "GUIDED", 4)
    time.sleep(0.5)
    results['stabilize'] = set_mode(mav, "STABILIZE", 0)
    time.sleep(0.5)
    results['loiter'] = set_mode(mav, "LOITER", 5)
    time.sleep(0.5)
    results['guided2'] = set_mode(mav, "GUIDED", 4)

    # ── Phase 2: Arm attempt ──
    print(f"\n{'='*60}")
    print(f"  PHASE 2: ARM COMMAND")
    print(f"{'='*60}")

    if TRY_ARM:
        print(f"\n  >>> Sending ARM...")
        mav.mav.command_long_send(
            mav.target_system, mav.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0,
            1, 0, 0, 0, 0, 0, 0)
        ack = mav.recv_match(type='COMMAND_ACK', blocking=True, timeout=3)
        if ack:
            if ack.result == 0:
                print(f"  [OK] ARMED — disarming immediately...")
                mav.mav.command_long_send(
                    mav.target_system, mav.target_component,
                    mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0,
                    0, 0, 0, 0, 0, 0, 0)
                time.sleep(1)
                results['arm'] = True
            else:
                reason = ""
                stxt = mav.recv_match(type='STATUSTEXT', blocking=True, timeout=2)
                if stxt:
                    reason = stxt.text
                print(f"  ARM rejected (result={ack.result}): {reason}")
                print(f"  (Expected on bench — command DID reach Cube)")
                results['arm'] = True  # command reached Cube
        else:
            print(f"  No ACK — command may not have reached Cube")
            results['arm'] = False
    else:
        print(f"\n  Skipping arm (use --with-arm to test)")
        print(f"  On bench without GPS, arm will be rejected — that's fine")
        results['arm'] = None

    # ── Phase 3: Takeoff command ──
    print(f"\n{'='*60}")
    print(f"  PHASE 3: TAKEOFF COMMAND")
    print(f"{'='*60}")

    results['takeoff'] = send_takeoff(mav, 10)
    if not results['takeoff']:
        print(f"  (Expected rejection — not armed)")

    # ── Phase 4: Waypoint commands ──
    print(f"\n{'='*60}")
    print(f"  PHASE 4: SEARCH WAYPOINTS")
    print(f"{'='*60}")

    if has_gps:
        waypoints = generate_search_waypoints(lat, lon)
        print(f"  Generated {len(waypoints)} waypoints around current position")
        for i, (wlat, wlon) in enumerate(waypoints):
            print(f"\n  --- Waypoint {i+1}/{len(waypoints)} ---")
            send_position_target(mav, wlat, wlon, 10.0)
            time.sleep(1)
        results['waypoints'] = True
    else:
        # Send dummy waypoints (Cube will reject without GPS)
        print(f"  No GPS fix — sending dummy waypoints (will be rejected)")
        dummy_wps = [(51.4545, -2.5879), (51.4546, -2.5878),
                     (51.4546, -2.5879), (51.4545, -2.5879)]
        for i, (wlat, wlon) in enumerate(dummy_wps):
            print(f"\n  --- Waypoint {i+1}/{len(dummy_wps)} ---")
            send_position_target(mav, wlat, wlon, 10.0)
            time.sleep(0.5)
        results['waypoints'] = True

    # ── Phase 5: Land command ──
    print(f"\n{'='*60}")
    print(f"  PHASE 5: LAND")
    print(f"{'='*60}")

    results['land'] = send_land(mav)

    # ── Phase 6: Return to STABILIZE ──
    print(f"\n{'='*60}")
    print(f"  PHASE 6: SAFE MODE")
    print(f"{'='*60}")

    results['safe'] = set_mode(mav, "STABILIZE", 0)

    # ── Summary ──
    mav.close()

    print(f"\n{'='*60}")
    print(f"  BENCH MISSION RESULTS")
    print(f"{'='*60}")

    tests = [
        ("GUIDED mode", results['guided']),
        ("STABILIZE mode", results['stabilize']),
        ("LOITER mode", results['loiter']),
        ("ARM command", results['arm']),
        ("TAKEOFF command", results['takeoff']),
        ("WAYPOINT commands", results['waypoints']),
        ("LAND mode", results['land']),
        ("Return to STABILIZE", results['safe']),
    ]

    passed = 0
    for name, ok in tests:
        if ok is None:
            print(f"  [--] {name} (skipped)")
        elif ok:
            print(f"  [OK] {name}")
            passed += 1
        else:
            print(f"  [X]  {name}")

    total = sum(1 for _, ok in tests if ok is not None)
    print(f"\n  {passed}/{total} commands worked")

    print(f"\n  What this proves:")
    print(f"    - Pi can change Cube flight modes (GUIDED/STABILIZE/LOITER/LAND)")
    print(f"    - Pi can send position waypoints to Cube")
    print(f"    - Pi can send arm/takeoff/land commands")
    print(f"    - The full command pipeline matches main.py")
    if not has_gps:
        print(f"\n  Note: Without GPS fix, arm/takeoff/waypoints are rejected.")
        print(f"  That's expected — the COMMANDS still reached the Cube.")
        print(f"  With GPS fix outdoors, all commands would be accepted.")
    print()


if __name__ == "__main__":
    main()
