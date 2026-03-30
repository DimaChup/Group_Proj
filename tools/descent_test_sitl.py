"""
Systematic SITL descent test.
Flies drone to different locations at 50m, commands descent to 3m,
measures if it actually reaches 3m.

Requires: SITL running (Mission Planner or mavproxy)
Usage: python tools/descent_test_sitl.py
"""
import sys, os, time, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pymavlink import mavutil
import config

# ── Test locations (lat, lon) — spread across the search area ──────
HOME = (51.423406, -2.671446)
TEST_LOCATIONS = [
    ("Center of search",     51.42330, -2.66950),
    ("East edge",            51.42330, -2.66850),
    ("West near NFZ",        51.42330, -2.67050),
    ("North edge",           51.42380, -2.66950),
    ("South edge",           51.42290, -2.66950),
    ("NE corner",            51.42380, -2.66850),
    ("SW corner",            51.42290, -2.67050),
    ("Far east",             51.42330, -2.66800),
    ("Near takeoff",         51.42340, -2.67100),
]

START_ALT = 50.0
TARGET_ALT = 3.0
TIMEOUT = 120  # seconds per test
SETTLE_TIME = 5  # seconds to wait after reaching position

def connect():
    print("Connecting to SITL...")
    master = mavutil.mavlink_connection('udp:127.0.0.1:14550')
    master.wait_heartbeat()
    print(f"  Connected: system {master.target_system}, component {master.target_component}")
    # Request data streams
    master.mav.request_data_stream_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_DATA_STREAM_ALL, 10, 1)
    return master

def get_telemetry(master):
    """Get current lat, lon, alt, speed."""
    master.recv_match(type='GLOBAL_POSITION_INT', blocking=True, timeout=2)
    msg = master.messages.get('GLOBAL_POSITION_INT')
    if msg:
        return (msg.lat / 1e7, msg.lon / 1e7, msg.relative_alt / 1000.0)
    return (0, 0, 0)

def set_mode(master, mode_name):
    mode_map = {"GUIDED": 4, "STABILIZE": 0, "LAND": 9, "LOITER": 5}
    mode_id = mode_map.get(mode_name, 4)
    master.mav.command_long_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_DO_SET_MODE, 0,
        mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
        mode_id, 0, 0, 0, 0, 0)
    ack = master.recv_match(type='COMMAND_ACK', blocking=True, timeout=2)
    time.sleep(0.5)

def arm_and_takeoff(master, alt):
    print(f"  Arming and taking off to {alt}m...")
    set_mode(master, "GUIDED")
    time.sleep(1)
    # Arm
    master.mav.command_long_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0,
        1, 0, 0, 0, 0, 0, 0)
    master.recv_match(type='COMMAND_ACK', blocking=True, timeout=3)
    time.sleep(1)
    # Takeoff
    master.mav.command_long_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0,
        0, 0, 0, 0, 0, 0, alt)
    # Wait for altitude
    t0 = time.time()
    while time.time() - t0 < 60:
        lat, lon, cur_alt = get_telemetry(master)
        if cur_alt > alt - 2.0:
            print(f"  Reached {cur_alt:.1f}m")
            time.sleep(2)
            return True
        time.sleep(0.5)
    print(f"  TIMEOUT waiting for takeoff alt")
    return False

def fly_to(master, lat, lon, alt, timeout=60):
    """Fly to position and wait until close."""
    print(f"  Flying to ({lat:.6f}, {lon:.6f}) at {alt:.0f}m...")
    t0 = time.time()
    while time.time() - t0 < timeout:
        master.mav.set_position_target_global_int_send(
            0, master.target_system, master.target_component,
            mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
            0b110111111000,
            int(lat * 1e7), int(lon * 1e7), alt,
            0, 0, 0, 0, 0, 0, 0, 0)
        cur_lat, cur_lon, cur_alt = get_telemetry(master)
        dist = math.sqrt(((cur_lat - lat) * 111320)**2 +
                         ((cur_lon - lon) * 111320 * math.cos(math.radians(lat)))**2)
        if dist < 3.0 and abs(cur_alt - alt) < 3.0:
            print(f"  Arrived: dist={dist:.1f}m alt={cur_alt:.1f}m")
            time.sleep(SETTLE_TIME)
            return True
        time.sleep(0.5)
    print(f"  TIMEOUT flying to position")
    return False

def test_descent(master, lat, lon, start_alt, target_alt):
    """Command descent from start_alt to target_alt and measure result."""
    # Set high speed so it doesn't bottleneck
    master.mav.command_long_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_DO_CHANGE_SPEED, 0,
        1, 15.0, -1, 0, 0, 0, 0)
    time.sleep(0.5)

    print(f"  Commanding descent to {target_alt}m...")
    t0 = time.time()
    min_alt = start_alt
    alt_log = []

    while time.time() - t0 < TIMEOUT:
        # Send position target at target altitude (same as APPROACH does)
        master.mav.set_position_target_global_int_send(
            0, master.target_system, master.target_component,
            mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
            0b110111111000,
            int(lat * 1e7), int(lon * 1e7), target_alt,
            0, 0, 0, 0, 0, 0, 0, 0)

        cur_lat, cur_lon, cur_alt = get_telemetry(master)
        min_alt = min(min_alt, cur_alt)
        elapsed = time.time() - t0

        if int(elapsed * 2) % 10 == 0:  # log every 5s
            alt_log.append((elapsed, cur_alt))
            print(f"    t={elapsed:5.1f}s  alt={cur_alt:6.1f}m")

        if cur_alt < target_alt + 1.0:
            print(f"  SUCCESS: reached {cur_alt:.1f}m in {elapsed:.1f}s")
            return True, elapsed, min_alt, alt_log

        # Detect stall (altitude not changing for 15s)
        if len(alt_log) >= 3:
            recent = [a for t, a in alt_log[-3:]]
            if max(recent) - min(recent) < 0.5:
                print(f"  STALLED at {cur_alt:.1f}m (no change for ~15s)")
                return False, elapsed, min_alt, alt_log

        time.sleep(0.5)

    cur_lat, cur_lon, cur_alt = get_telemetry(master)
    print(f"  TIMEOUT at {cur_alt:.1f}m")
    return False, TIMEOUT, min_alt, alt_log

def test_descent_with_speed(master, lat, lon, start_alt, target_alt, speed):
    """Same as test_descent but sets a specific speed first."""
    master.mav.command_long_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_DO_CHANGE_SPEED, 0,
        1, speed, -1, 0, 0, 0, 0)
    time.sleep(1)
    return test_descent(master, lat, lon, start_alt, target_alt)

def reset_to_home(master):
    """RTL and disarm for next test."""
    set_mode(master, "LAND")
    time.sleep(5)
    # Wait for landing
    t0 = time.time()
    while time.time() - t0 < 60:
        lat, lon, alt = get_telemetry(master)
        if alt < 1.0:
            time.sleep(3)
            # Disarm
            master.mav.command_long_send(
                master.target_system, master.target_component,
                mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0,
                0, 0, 0, 0, 0, 0, 0)
            time.sleep(2)
            return
        time.sleep(1)

def main():
    master = connect()

    results = []
    print("\n" + "="*70)
    print("  SYSTEMATIC DESCENT TEST — SITL")
    print("  Tests descent from 50m to 3m at different locations")
    print("="*70)

    for name, lat, lon in TEST_LOCATIONS:
        print(f"\n--- TEST: {name} ({lat:.5f}, {lon:.5f}) ---")

        # Arm and takeoff
        if not arm_and_takeoff(master, START_ALT):
            results.append((name, False, 0, START_ALT, "takeoff failed"))
            reset_to_home(master)
            continue

        # Fly to test location
        if not fly_to(master, lat, lon, START_ALT):
            results.append((name, False, 0, START_ALT, "fly-to failed"))
            reset_to_home(master)
            continue

        # Test 1: descent with speed=15 (our fix)
        ok, elapsed, min_alt, log = test_descent(master, lat, lon, START_ALT, TARGET_ALT)
        results.append((name, ok, elapsed, min_alt, "speed=15"))

        # Reset
        reset_to_home(master)
        time.sleep(5)

    # Summary
    print("\n\n" + "="*70)
    print("  RESULTS SUMMARY")
    print("="*70)
    print(f"  {'Location':<25} {'Result':^8} {'Time':>6} {'Min Alt':>8} {'Notes'}")
    print("-"*70)
    for name, ok, t, alt, notes in results:
        status = "OK" if ok else "FAIL"
        print(f"  {name:<25} {status:^8} {t:5.1f}s {alt:7.1f}m  {notes}")

    failed = [r for r in results if not r[1]]
    print(f"\n  {len(results) - len(failed)}/{len(results)} passed")
    if failed:
        print(f"  FAILED locations:")
        for name, _, _, alt, _ in failed:
            print(f"    - {name} (stuck at {alt:.1f}m)")

if __name__ == "__main__":
    main()
