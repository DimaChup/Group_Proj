#!/usr/bin/env python3
"""
APPROACH descent investigation — WHY won't ArduCopter go below ~3.7m in SITL?

Tests three methods at low altitude:
  1. send_global_target to 3.0m (same as main.py APPROACH state)
  2. send_global_target to 2.0m
  3. send_velocity(0, 0, 0.5) downward for 5 seconds

Connects to SITL at tcp:127.0.0.1:5762, arms, takes off to 50m, flies to a
point in the search area, then runs each descent experiment while printing
altitude every 0.5s.

USAGE:
    1. Start SITL in Mission Planner (--home=51.423406,-2.671446,50,155)
    2. python tests/laptop/test_approach_descent.py

DEPENDENCIES: pymavlink only (no project imports)
"""

import time
import math
from pymavlink import mavutil

# ── Config ──────────────────────────────────────────────────────────
CONN_STR = "tcp:127.0.0.1:5762"
TAKEOFF_ALT = 50.0
TARGET_LAT = 51.423500
TARGET_LON = -2.669500
SITL_SPEEDUP = 5


def connect():
    print(f"Connecting to {CONN_STR} ...")
    master = mavutil.mavlink_connection(CONN_STR)
    master.wait_heartbeat()
    print(f"Connected — sysid={master.target_system} compid={master.target_component}")
    return master


def set_sitl_speedup(master, speed):
    """Set SIM_SPEEDUP parameter."""
    master.mav.param_set_send(
        master.target_system, master.target_component,
        b"SIM_SPEEDUP", float(speed),
        mavutil.mavlink.MAV_PARAM_TYPE_REAL32)
    print(f"Set SIM_SPEEDUP={speed}")
    time.sleep(0.5)


def set_mode(master, mode_name):
    mode_map = master.mode_mapping()
    if mode_name not in mode_map:
        print(f"ERROR: mode '{mode_name}' not in mode_map: {list(mode_map.keys())}")
        return False
    mode_id = mode_map[mode_name]
    master.set_mode(mode_id)
    time.sleep(1)
    # Confirm
    master.recv_match(type="HEARTBEAT", blocking=True, timeout=3)
    print(f"Mode set to {mode_name} (id={mode_id})")
    return True


def get_alt(master):
    """Get relative altitude in meters from GLOBAL_POSITION_INT."""
    msg = master.recv_match(type="GLOBAL_POSITION_INT", blocking=True, timeout=3)
    if msg:
        return msg.relative_alt / 1000.0
    return None


def get_position(master):
    """Get (lat, lon, relative_alt) from GLOBAL_POSITION_INT."""
    msg = master.recv_match(type="GLOBAL_POSITION_INT", blocking=True, timeout=3)
    if msg:
        return msg.lat / 1e7, msg.lon / 1e7, msg.relative_alt / 1000.0
    return None, None, None


def drain_messages(master):
    """Drain buffered messages to get fresh data."""
    while master.recv_match(blocking=False):
        pass


def wait_for_alt(master, target_alt, tolerance=2.0, timeout=60):
    """Wait until within tolerance of target_alt."""
    t0 = time.time()
    while time.time() - t0 < timeout:
        drain_messages(master)
        alt = get_alt(master)
        if alt is not None:
            print(f"  alt={alt:.2f}m (target={target_alt:.1f}m)")
            if abs(alt - target_alt) < tolerance:
                return True
        time.sleep(0.5)
    print(f"  TIMEOUT waiting for alt={target_alt}m")
    return False


def arm_and_takeoff(master, alt):
    print(f"\n{'='*60}")
    print(f"ARMING + TAKEOFF to {alt}m")
    print(f"{'='*60}")

    set_mode(master, "GUIDED")

    # Arm
    master.mav.command_long_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
        0, 1, 0, 0, 0, 0, 0, 0)
    print("Arm command sent, waiting...")
    master.motors_armed_wait()
    print("ARMED")

    # Takeoff
    master.mav.command_long_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
        0, 0, 0, 0, 0, 0, 0, alt)
    print(f"Takeoff command sent (target {alt}m)")

    wait_for_alt(master, alt, tolerance=2.0, timeout=120)
    print(f"Takeoff complete")


def send_global_target(master, lat, lon, alt, vz=0):
    """Same as navigation.py send_global_target — position target with optional vz."""
    # mask: ignore vx,vy,ax,ay,az,yaw,yaw_rate; use x,y,z; conditionally use vz
    if vz != 0:
        mask = 0b110111000000  # use pos + vz, ignore yaw
    else:
        mask = 0b110111111000  # use pos only, ignore vel/accel/yaw
    master.mav.set_position_target_global_int_send(
        0, master.target_system, master.target_component,
        mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
        mask,
        int(lat * 1e7), int(lon * 1e7), alt,
        0, 0, vz,
        0, 0, 0,
        0, 0)


def send_velocity_ned(master, vx, vy, vz):
    """Send NED velocity command (vz positive = descend)."""
    mask = 0b110111000111  # use velocity only, ignore pos/accel/yaw
    master.mav.set_position_target_local_ned_send(
        0, master.target_system, master.target_component,
        mavutil.mavlink.MAV_FRAME_LOCAL_NED,
        mask,
        0, 0, 0,
        vx, vy, vz,
        0, 0, 0,
        0, 0)


def haversine_m(lat1, lon1, lat2, lon2):
    R = 6371000
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))


def fly_to_point(master, lat, lon, alt, timeout=120):
    print(f"\nFlying to ({lat}, {lon}) at {alt}m ...")
    t0 = time.time()
    while time.time() - t0 < timeout:
        send_global_target(master, lat, lon, alt)
        time.sleep(1)
        drain_messages(master)
        clat, clon, calt = get_position(master)
        if clat is not None:
            dist = haversine_m(clat, clon, lat, lon)
            print(f"  dist={dist:.1f}m  alt={calt:.1f}m")
            if dist < 3.0 and abs(calt - alt) < 2.0:
                print(f"Arrived at target point")
                return True
    print("TIMEOUT flying to point")
    return False


def read_param(master, name):
    """Read a parameter value."""
    master.mav.param_request_read_send(
        master.target_system, master.target_component,
        name.encode('utf-8'), -1)
    msg = master.recv_match(type="PARAM_VALUE", blocking=True, timeout=5)
    if msg and msg.param_id.rstrip('\x00') == name:
        return msg.param_value
    return None


def print_relevant_params(master):
    """Print params that might affect low-altitude behavior."""
    print(f"\n{'='*60}")
    print("RELEVANT PARAMETERS")
    print(f"{'='*60}")
    params = [
        "LAND_ALT_LOW",     # altitude at which landing speed changes
        "LAND_SPEED",       # final landing descent speed cm/s
        "LAND_SPEED_HIGH",  # initial landing descent speed cm/s
        "WPNAV_SPEED_DN",   # max descent speed cm/s in auto modes
        "WPNAV_SPEED_UP",   # max climb speed cm/s
        "PSC_VELZ_MAX",     # max vertical speed cm/s (position controller)
        "PILOT_SPEED_DN",   # pilot-commanded max descent cm/s
        "RTL_ALT",          # RTL altitude cm
        "RTL_ALT_FINAL",   # RTL final altitude cm
        "RNGFND_LANDING",   # use rangefinder for landing
        "SIM_SPEEDUP",
    ]
    for name in params:
        val = read_param(master, name)
        if val is not None:
            print(f"  {name:20s} = {val}")
        else:
            print(f"  {name:20s} = (not found)")


def monitor_alt(master, duration, label=""):
    """Print altitude every 0.5s for duration seconds. Returns list of (time, alt)."""
    print(f"\n--- Monitoring altitude for {duration}s{' — ' + label if label else ''} ---")
    readings = []
    t0 = time.time()
    while time.time() - t0 < duration:
        drain_messages(master)
        alt = get_alt(master)
        elapsed = time.time() - t0
        if alt is not None:
            readings.append((elapsed, alt))
            print(f"  t={elapsed:5.1f}s  alt={alt:.3f}m")
        time.sleep(0.5)
    return readings


# ── Main ────────────────────────────────────────────────────────────

def main():
    master = connect()
    set_sitl_speedup(master, SITL_SPEEDUP)
    print_relevant_params(master)

    arm_and_takeoff(master, TAKEOFF_ALT)
    fly_to_point(master, TARGET_LAT, TARGET_LON, TAKEOFF_ALT)

    # ── Experiment 1: Position target to 3.0m ────────────────────────
    print(f"\n{'='*60}")
    print("EXPERIMENT 1: send_global_target → 3.0m")
    print("(Same as main.py APPROACH state)")
    print(f"{'='*60}")

    t0 = time.time()
    while time.time() - t0 < 60:
        send_global_target(master, TARGET_LAT, TARGET_LON, 3.0)
        time.sleep(0.5)
        drain_messages(master)
        alt = get_alt(master)
        elapsed = time.time() - t0
        if alt is not None:
            print(f"  t={elapsed:5.1f}s  alt={alt:.3f}m  (target=3.0m)")
            # Check if stabilized (below 4m and not changing much)
            if alt < 4.0 and elapsed > 20:
                # Monitor for another 10s to confirm it's stuck
                print("  Alt below 4m for >20s — checking if stabilized...")
                readings = []
                for _ in range(20):
                    send_global_target(master, TARGET_LAT, TARGET_LON, 3.0)
                    time.sleep(0.5)
                    drain_messages(master)
                    a = get_alt(master)
                    if a: readings.append(a)
                if readings:
                    avg = sum(readings) / len(readings)
                    mn, mx = min(readings), max(readings)
                    print(f"  STABILIZED: avg={avg:.3f}m  min={mn:.3f}m  max={mx:.3f}m  spread={mx-mn:.3f}m")
                break

    # ── Experiment 2: Position target to 2.0m ────────────────────────
    print(f"\n{'='*60}")
    print("EXPERIMENT 2: send_global_target → 2.0m")
    print(f"{'='*60}")

    t0 = time.time()
    while time.time() - t0 < 40:
        send_global_target(master, TARGET_LAT, TARGET_LON, 2.0)
        time.sleep(0.5)
        drain_messages(master)
        alt = get_alt(master)
        elapsed = time.time() - t0
        if alt is not None:
            print(f"  t={elapsed:5.1f}s  alt={alt:.3f}m  (target=2.0m)")
            if alt < 3.0 and elapsed > 15:
                readings = []
                for _ in range(20):
                    send_global_target(master, TARGET_LAT, TARGET_LON, 2.0)
                    time.sleep(0.5)
                    drain_messages(master)
                    a = get_alt(master)
                    if a: readings.append(a)
                if readings:
                    avg = sum(readings) / len(readings)
                    mn, mx = min(readings), max(readings)
                    print(f"  STABILIZED: avg={avg:.3f}m  min={mn:.3f}m  max={mx:.3f}m  spread={mx-mn:.3f}m")
                break

    # ── Experiment 3: Position target to 1.0m ────────────────────────
    print(f"\n{'='*60}")
    print("EXPERIMENT 3: send_global_target → 1.0m")
    print(f"{'='*60}")

    t0 = time.time()
    while time.time() - t0 < 40:
        send_global_target(master, TARGET_LAT, TARGET_LON, 1.0)
        time.sleep(0.5)
        drain_messages(master)
        alt = get_alt(master)
        elapsed = time.time() - t0
        if alt is not None:
            print(f"  t={elapsed:5.1f}s  alt={alt:.3f}m  (target=1.0m)")
            if elapsed > 20:
                readings = []
                for _ in range(20):
                    send_global_target(master, TARGET_LAT, TARGET_LON, 1.0)
                    time.sleep(0.5)
                    drain_messages(master)
                    a = get_alt(master)
                    if a: readings.append(a)
                if readings:
                    avg = sum(readings) / len(readings)
                    mn, mx = min(readings), max(readings)
                    print(f"  STABILIZED: avg={avg:.3f}m  min={mn:.3f}m  max={mx:.3f}m  spread={mx-mn:.3f}m")
                break

    # ── Experiment 4: Velocity push downward ─────────────────────────
    print(f"\n{'='*60}")
    print("EXPERIMENT 4: send_velocity vz=+0.5 (descend) for 5s")
    print("Starting from current altitude")
    print(f"{'='*60}")

    # First go back up to 5m to have room
    print("Climbing to 5m first...")
    t0 = time.time()
    while time.time() - t0 < 20:
        send_global_target(master, TARGET_LAT, TARGET_LON, 5.0)
        time.sleep(0.5)
        drain_messages(master)
        alt = get_alt(master)
        if alt and abs(alt - 5.0) < 1.0:
            break

    print("Now pushing down with velocity...")
    t0 = time.time()
    while time.time() - t0 < 5:
        send_velocity_ned(master, 0, 0, 0.5)  # 0.5 m/s down in NED
        time.sleep(0.5)
        drain_messages(master)
        alt = get_alt(master)
        elapsed = time.time() - t0
        if alt is not None:
            print(f"  t={elapsed:5.1f}s  alt={alt:.3f}m  (vz=+0.5 descend)")

    # Continue monitoring after stopping velocity
    print("Velocity stopped — holding position...")
    monitor_alt(master, 5, "after velocity stop")

    # ── Experiment 5: Stronger velocity push ─────────────────────────
    print(f"\n{'='*60}")
    print("EXPERIMENT 5: send_velocity vz=+1.0 (descend faster) for 5s")
    print(f"{'='*60}")

    # Go back up to 5m
    t0 = time.time()
    while time.time() - t0 < 20:
        send_global_target(master, TARGET_LAT, TARGET_LON, 5.0)
        time.sleep(0.5)
        drain_messages(master)
        alt = get_alt(master)
        if alt and abs(alt - 5.0) < 1.0:
            break

    t0 = time.time()
    while time.time() - t0 < 5:
        send_velocity_ned(master, 0, 0, 1.0)  # 1.0 m/s down
        time.sleep(0.5)
        drain_messages(master)
        alt = get_alt(master)
        elapsed = time.time() - t0
        if alt is not None:
            print(f"  t={elapsed:5.1f}s  alt={alt:.3f}m  (vz=+1.0 descend)")

    monitor_alt(master, 5, "after fast velocity stop")

    # ── Experiment 6: Position + velocity combined ───────────────────
    print(f"\n{'='*60}")
    print("EXPERIMENT 6: send_global_target(alt=2.0, vz=+0.5) — position+velocity hint")
    print(f"{'='*60}")

    # Go back up to 5m
    t0 = time.time()
    while time.time() - t0 < 20:
        send_global_target(master, TARGET_LAT, TARGET_LON, 5.0)
        time.sleep(0.5)
        drain_messages(master)
        alt = get_alt(master)
        if alt and abs(alt - 5.0) < 1.0:
            break

    t0 = time.time()
    while time.time() - t0 < 30:
        send_global_target(master, TARGET_LAT, TARGET_LON, 2.0, vz=0.5)
        time.sleep(0.5)
        drain_messages(master)
        alt = get_alt(master)
        elapsed = time.time() - t0
        if alt is not None:
            print(f"  t={elapsed:5.1f}s  alt={alt:.3f}m  (target=2.0m, vz=+0.5)")
            if elapsed > 15:
                readings = []
                for _ in range(10):
                    send_global_target(master, TARGET_LAT, TARGET_LON, 2.0, vz=0.5)
                    time.sleep(0.5)
                    drain_messages(master)
                    a = get_alt(master)
                    if a: readings.append(a)
                if readings:
                    avg = sum(readings) / len(readings)
                    mn, mx = min(readings), max(readings)
                    print(f"  STABILIZED: avg={avg:.3f}m  min={mn:.3f}m  max={mx:.3f}m")
                break

    # ── Experiment 7: MAV_CMD_NAV_LAND ───────────────────────────────
    print(f"\n{'='*60}")
    print("EXPERIMENT 7: MAV_CMD_NAV_LAND at target point")
    print("(ArduCopter's native landing — should go all the way to ground)")
    print(f"{'='*60}")

    # Climb back up first
    t0 = time.time()
    while time.time() - t0 < 20:
        send_global_target(master, TARGET_LAT, TARGET_LON, 10.0)
        time.sleep(0.5)
        drain_messages(master)
        alt = get_alt(master)
        if alt and abs(alt - 10.0) < 1.5:
            break

    # Send LAND command
    master.mav.command_long_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_NAV_LAND,
        0,
        0, 0, 0, 0,
        TARGET_LAT, TARGET_LON, 0)
    print("LAND command sent")

    t0 = time.time()
    landed = False
    while time.time() - t0 < 60:
        time.sleep(0.5)
        drain_messages(master)
        alt = get_alt(master)
        elapsed = time.time() - t0
        if alt is not None:
            print(f"  t={elapsed:5.1f}s  alt={alt:.3f}m  (LANDING)")
            if alt < 0.3:
                print("  LANDED (alt < 0.3m)")
                landed = True
                break

    # ── Summary ──────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print("""
Questions answered:
1. Does send_global_target(alt=3.0) reach 3.0m or stop higher?
2. Does send_global_target(alt=2.0) go lower?
3. Does send_global_target(alt=1.0) go even lower?
4. Can velocity commands push below the position target floor?
5. Does stronger velocity (1.0 m/s) help?
6. Does position + velocity hint combined help?
7. Does MAV_CMD_NAV_LAND reach the ground?

If experiments 1-6 all stop at ~3.7m but experiment 7 lands:
  → ArduCopter's position controller has a minimum alt floor in GUIDED
  → The APPROACH state should use MAV_CMD_NAV_LAND instead
  → Or: the rangefinder/ground-effect sim prevents low guided hover

Check the parameter printout above for clues (LAND_ALT_LOW, etc.)
""")

    if not landed:
        # RTL as cleanup
        print("RTL for cleanup...")
        set_mode(master, "RTL")


if __name__ == "__main__":
    main()
