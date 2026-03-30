"""
Simple state machine test.
Follows transit.json waypoints → descends to 3m at last WP → hovers 10s →
climbs back → follows same path in reverse → lands at home.

Usage: python simple_state.py [--alt 25]
Requires: SITL running on udp:127.0.0.1:14550
"""
import sys, os, time, math, json
from pymavlink import mavutil

ALT = 25.0
for i, a in enumerate(sys.argv):
    if a == "--alt" and i + 1 < len(sys.argv):
        ALT = float(sys.argv[i + 1])

CONNECTION = "udp:127.0.0.1:14550"
DESCEND_ALT = 3.0
HOVER_TIME = 10.0

# Load transit waypoints
transit_path = os.path.join(os.path.dirname(__file__), "flight_plans", "transit.json")
with open(transit_path) as f:
    raw = json.load(f)
WAYPOINTS = [(wp["lat"], wp["lon"]) for wp in raw]
print(f"Loaded {len(WAYPOINTS)} transit waypoints from {transit_path}")

# ── Helpers ──────────────────────────────────────────────────────────

def get_pos(master):
    master.recv_match(type='GLOBAL_POSITION_INT', blocking=True, timeout=2)
    m = master.messages.get('GLOBAL_POSITION_INT')
    if m:
        return m.lat / 1e7, m.lon / 1e7, m.relative_alt / 1000.0
    return 0, 0, 0

def dist_to(master, lat, lon):
    clat, clon, _ = get_pos(master)
    return math.sqrt(((clat - lat) * 111320)**2 +
                     ((clon - lon) * 111320 * math.cos(math.radians(clat)))**2)

def yaw_to(master, lat, lon):
    clat, clon, _ = get_pos(master)
    dy = (lat - clat) * 111320
    dx = (lon - clon) * 111320 * math.cos(math.radians(clat))
    return math.atan2(dx, dy)

def send_target(master, lat, lon, alt, yaw=None, vz=0):
    if yaw is not None:
        mask = 0b100111000000 if vz != 0 else 0b100111111000
        master.mav.set_position_target_global_int_send(
            0, master.target_system, master.target_component,
            mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
            mask, int(lat * 1e7), int(lon * 1e7), alt,
            0, 0, vz, 0, 0, 0, yaw, 0)
    else:
        mask = 0b110111000000 if vz != 0 else 0b110111111000
        master.mav.set_position_target_global_int_send(
            0, master.target_system, master.target_component,
            mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
            mask, int(lat * 1e7), int(lon * 1e7), alt,
            0, 0, vz, 0, 0, 0, 0, 0)

def set_speed(master, speed):
    master.mav.command_long_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_DO_CHANGE_SPEED, 0,
        1, speed, -1, 0, 0, 0, 0)

def set_mode(master, mode_id):
    master.mav.command_long_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_DO_SET_MODE, 0,
        mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
        mode_id, 0, 0, 0, 0, 0)
    master.recv_match(type='COMMAND_ACK', blocking=True, timeout=2)

def wait_alt(master, target, tolerance=2.0, timeout=60):
    t0 = time.time()
    while time.time() - t0 < timeout:
        _, _, alt = get_pos(master)
        if abs(alt - target) < tolerance:
            return True
        time.sleep(0.5)
    return False

def fly_to_wp(master, lat, lon, alt, label="WP", radius=3.0, timeout=120):
    """Fly to waypoint, yaw toward it, wait until within radius."""
    t0 = time.time()
    while time.time() - t0 < timeout:
        yaw = yaw_to(master, lat, lon)
        send_target(master, lat, lon, alt, yaw=yaw)
        d = dist_to(master, lat, lon)
        _, _, cur_alt = get_pos(master)
        print(f"  {label}: dist={d:.1f}m  alt={cur_alt:.1f}m", end='\r')
        if d < radius:
            print(f"  {label}: REACHED ({d:.1f}m, alt={cur_alt:.1f}m)          ")
            return True
        time.sleep(0.5)
    print(f"  {label}: TIMEOUT                              ")
    return False

# ── Main ─────────────────────────────────────────────────────────────

def main():
    print(f"\n{'='*60}")
    print(f"  Simple State Machine Test")
    print(f"  Transit → Descend 3m → Hover 10s → Climb → Reverse → Land")
    print(f"  Altitude: {ALT}m  |  Waypoints: {len(WAYPOINTS)}")
    print(f"{'='*60}\n")

    print("Connecting...")
    master = mavutil.mavlink_connection(CONNECTION)
    master.wait_heartbeat()
    print(f"Connected (sys={master.target_system})")

    master.mav.request_data_stream_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_DATA_STREAM_ALL, 10, 1)
    time.sleep(1)

    # Save home position
    home_lat, home_lon, _ = get_pos(master)
    print(f"Home: ({home_lat:.6f}, {home_lon:.6f})")

    # ── 1. ARM + TAKEOFF ──
    print(f"\n[1/7] ARM + TAKEOFF to {ALT}m")
    set_mode(master, 4)  # GUIDED
    time.sleep(1)
    master.mav.command_long_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0,
        1, 0, 0, 0, 0, 0, 0)
    master.recv_match(type='COMMAND_ACK', blocking=True, timeout=3)
    time.sleep(1)
    master.mav.command_long_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0,
        0, 0, 0, 0, 0, 0, ALT)
    if not wait_alt(master, ALT, 3.0, 60):
        print("  TAKEOFF TIMEOUT!")
        return
    print(f"  Airborne at {ALT}m")
    time.sleep(3)

    # ── 2. FLY TRANSIT FORWARD ──
    print(f"\n[2/7] TRANSIT FORWARD ({len(WAYPOINTS)} waypoints)")
    set_speed(master, 15.0)
    for i, (wlat, wlon) in enumerate(WAYPOINTS):
        fly_to_wp(master, wlat, wlon, ALT, label=f"T{i+1}")
        time.sleep(1)

    # ── 3. DESCEND TO 3m ──
    last_wp = WAYPOINTS[-1]
    print(f"\n[3/7] DESCENDING to {DESCEND_ALT}m")
    set_speed(master, 15.0)
    t0 = time.time()
    while time.time() - t0 < 60:
        _, _, alt = get_pos(master)
        alt_err = alt - DESCEND_ALT
        if alt_err > 0.5:
            vz = min(0.5 * alt_err, 1.5)
        elif alt_err < -0.5:
            vz = max(0.5 * alt_err, -1.5)
        else:
            vz = 0
        send_target(master, last_wp[0], last_wp[1], DESCEND_ALT, vz=vz)
        print(f"  DESCENT: alt={alt:.1f}m  vz={vz:.1f}  err={alt_err:.1f}m", end='\r')
        if abs(alt_err) < 1.0:
            print(f"\n  Reached {alt:.1f}m")
            break
        time.sleep(0.3)
    else:
        _, _, alt = get_pos(master)
        print(f"\n  TIMEOUT at {alt:.1f}m!")

    # ── 4. HOVER 10s ──
    print(f"\n[4/7] HOVERING at {DESCEND_ALT}m for {HOVER_TIME}s")
    t0 = time.time()
    while time.time() - t0 < HOVER_TIME:
        send_target(master, last_wp[0], last_wp[1], DESCEND_ALT)
        _, _, alt = get_pos(master)
        remaining = HOVER_TIME - (time.time() - t0)
        print(f"  HOVER: alt={alt:.1f}m  remaining={remaining:.0f}s", end='\r')
        time.sleep(0.3)
    print(f"\n  Hover complete")

    # ── 5. CLIMB BACK ──
    print(f"\n[5/7] CLIMBING to {ALT}m")
    set_speed(master, 15.0)
    t0 = time.time()
    while time.time() - t0 < 60:
        _, _, alt = get_pos(master)
        vz = -2.5 if alt < ALT - 2.0 else 0
        send_target(master, last_wp[0], last_wp[1], ALT, vz=vz)
        print(f"  CLIMB: alt={alt:.1f}m  vz={vz}", end='\r')
        if alt > ALT - 3.0:
            print(f"\n  Reached {alt:.1f}m")
            break
        time.sleep(0.5)
    else:
        _, _, alt = get_pos(master)
        print(f"\n  TIMEOUT at {alt:.1f}m!")

    # ── 6. REVERSE TRANSIT ──
    reverse_wps = list(reversed(WAYPOINTS))
    print(f"\n[6/7] TRANSIT REVERSE ({len(reverse_wps)} waypoints)")
    set_speed(master, 15.0)
    for i, (wlat, wlon) in enumerate(reverse_wps):
        fly_to_wp(master, wlat, wlon, ALT, label=f"R{i+1}")
        time.sleep(1)

    # ── 7. RETURN HOME + LAND ──
    print(f"\n[7/7] RETURN HOME + LAND")
    fly_to_wp(master, home_lat, home_lon, ALT, label="HOME", radius=5.0)

    master.mav.command_long_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_NAV_LAND, 0,
        0, 0, 0, 0, 0, 0, 0)
    t0 = time.time()
    while time.time() - t0 < 60:
        _, _, alt = get_pos(master)
        print(f"  LANDING: alt={alt:.1f}m", end='\r')
        if alt < 0.5:
            print(f"\n  Touchdown!")
            break
        time.sleep(0.5)

    print(f"\n{'='*60}")
    print(f"  DONE")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
