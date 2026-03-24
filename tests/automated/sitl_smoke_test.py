#!/usr/bin/env python3
"""
SITL Smoke Test — verifies the MAVLink command layer works in SITL.

Connects to SITL, arms, takes off, flies waypoints, tests yaw and velocity
commands, lands, and disarms. Each step has a 30s timeout and prints PASS/FAIL.

Requirements:
  - SITL running (Mission Planner or mavproxy)
  - Connection at tcp:127.0.0.1:5762 (or pass --conn <string>)

Usage:
  python tests/automated/sitl_smoke_test.py
  python tests/automated/sitl_smoke_test.py --conn tcp:127.0.0.1:5762

No camera, no vision, no cv2 — pure pymavlink.
"""

import sys
import os
import time
import math
import argparse

# Add project root so we can import config if needed
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from pymavlink import mavutil

# ── Configuration ──────────────────────────────────────────────────────────

TAKEOFF_ALT = 20.0         # meters
WAYPOINT_ACCEPT_RADIUS = 3.0  # meters — "close enough" to a waypoint
YAW_TOLERANCE = 15.0       # degrees
TIMEOUT = 30.0             # seconds per test step
HOME_LAT = 51.423406       # SITL home from AENGM0074.kml
HOME_LON = -2.671446

# Three waypoints forming a small triangle near the SITL home
WAYPOINTS = [
    (51.42360, -2.67140),  # ~25m NE of home
    (51.42360, -2.67180),  # ~25m NW
    (51.42340, -2.67160),  # back near home
]


# ── Helpers ────────────────────────────────────────────────────────────────

def gps_distance(lat1, lon1, lat2, lon2):
    """Haversine distance in meters between two GPS points."""
    R = 6371000
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def wait_heartbeat(conn, timeout=10):
    """Wait for first heartbeat from autopilot."""
    start = time.time()
    while time.time() - start < timeout:
        msg = conn.recv_match(type="HEARTBEAT", blocking=True, timeout=2)
        if msg and msg.get_srcSystem() != 255:
            return msg
    return None


def get_position(conn):
    """Get current lat, lon, alt from GLOBAL_POSITION_INT."""
    msg = conn.recv_match(type="GLOBAL_POSITION_INT", blocking=True, timeout=5)
    if msg:
        return msg.lat / 1e7, msg.lon / 1e7, msg.relative_alt / 1000.0
    return None, None, None


def get_heading(conn):
    """Get current heading in degrees from VFR_HUD."""
    msg = conn.recv_match(type="VFR_HUD", blocking=True, timeout=5)
    if msg:
        return msg.heading
    return None


def wait_for_ack(conn, command, timeout=10):
    """Wait for COMMAND_ACK for a specific MAV_CMD. Returns True if accepted."""
    start = time.time()
    while time.time() - start < timeout:
        msg = conn.recv_match(type="COMMAND_ACK", blocking=True, timeout=2)
        if msg and msg.command == command:
            return msg.result == 0  # MAV_RESULT_ACCEPTED
    return False


def set_mode(conn, mode_name):
    """Set flight mode by name (e.g. 'GUIDED', 'LAND'). Returns True on success."""
    mode_map = conn.mode_mapping()
    if mode_name not in mode_map:
        return False
    mode_id = mode_map[mode_name]
    conn.set_mode(mode_id)
    # Verify mode changed
    start = time.time()
    while time.time() - start < 10:
        hb = conn.recv_match(type="HEARTBEAT", blocking=True, timeout=2)
        if hb and hb.custom_mode == mode_id:
            return True
    return False


def send_goto(conn, lat, lon, alt):
    """Send a MAV_CMD_NAV_WAYPOINT position target in GUIDED mode."""
    conn.mav.set_position_target_global_int_send(
        0,                          # timestamp (not used)
        conn.target_system,
        conn.target_component,
        mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
        0b0000111111111000,         # position only (ignore velocity/accel/yaw)
        int(lat * 1e7),
        int(lon * 1e7),
        alt,
        0, 0, 0,                    # vx, vy, vz
        0, 0, 0,                    # afx, afy, afz
        0, 0                        # yaw, yaw_rate
    )


def send_yaw(conn, heading_deg):
    """Command yaw to absolute heading (degrees, 0=North, CW positive)."""
    conn.mav.command_long_send(
        conn.target_system,
        conn.target_component,
        mavutil.mavlink.MAV_CMD_CONDITION_YAW,
        0,
        heading_deg,   # target heading
        25,            # deg/s rotation speed
        1,             # 1 = clockwise
        0,             # 0 = absolute heading
        0, 0, 0
    )


def send_velocity(conn, vx, vy, vz):
    """Send velocity command in NED frame (m/s). vz positive = down."""
    conn.mav.set_position_target_global_int_send(
        0,
        conn.target_system,
        conn.target_component,
        mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
        0b0000111111000111,         # velocity only (ignore position/accel/yaw)
        0, 0, 0,                    # lat, lon, alt (ignored)
        vx, vy, vz,
        0, 0, 0,
        0, 0
    )


# ── Test runner ────────────────────────────────────────────────────────────

class SITLSmokeTest:
    """Runs each test step, tracks pass/fail."""

    def __init__(self, conn_str):
        self.conn_str = conn_str
        self.conn = None
        self.results = []   # list of (test_name, passed, detail)

    def record(self, name, passed, detail=""):
        status = "PASS" if passed else "FAIL"
        self.results.append((name, passed, detail))
        print(f"  [{status}] {name}" + (f" — {detail}" if detail else ""))

    def connect(self):
        """Step 0: Connect to SITL."""
        print(f"\nConnecting to {self.conn_str} ...")
        try:
            self.conn = mavutil.mavlink_connection(self.conn_str)
        except Exception as e:
            self.record("Connect", False, str(e))
            return False
        self.record("Connect", True)
        return True

    def test_heartbeat(self):
        """Step 1: Verify heartbeat received."""
        print("\n[1] Waiting for heartbeat ...")
        hb = wait_heartbeat(self.conn, timeout=15)
        self.record("Heartbeat", hb is not None,
                     f"system {hb.get_srcSystem()}" if hb else "timeout")
        return hb is not None

    def test_set_guided(self):
        """Step 2: Set GUIDED mode."""
        print("\n[2] Setting GUIDED mode ...")
        ok = set_mode(self.conn, "GUIDED")
        self.record("GUIDED mode", ok)
        return ok

    def test_arm(self):
        """Step 3: Arm motors."""
        print("\n[3] Arming ...")
        self.conn.arducopter_arm()
        ok = wait_for_ack(self.conn,
                          mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
                          timeout=15)
        if ok:
            # Double-check armed flag in heartbeat
            time.sleep(1)
            hb = self.conn.recv_match(type="HEARTBEAT", blocking=True, timeout=5)
            armed = hb and (hb.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED)
            self.record("Arm", bool(armed))
            return bool(armed)
        self.record("Arm", False, "ACK not received")
        return False

    def test_takeoff(self):
        """Step 4: Takeoff and wait for target altitude."""
        print(f"\n[4] Taking off to {TAKEOFF_ALT}m ...")
        self.conn.mav.command_long_send(
            self.conn.target_system,
            self.conn.target_component,
            mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
            0,
            0, 0, 0, 0, 0, 0,
            TAKEOFF_ALT
        )
        # Wait until within 2m of target altitude
        start = time.time()
        while time.time() - start < TIMEOUT:
            _, _, alt = get_position(self.conn)
            if alt is not None and alt >= TAKEOFF_ALT - 2.0:
                self.record("Takeoff", True, f"reached {alt:.1f}m")
                return True
            time.sleep(0.5)
        _, _, alt = get_position(self.conn)
        self.record("Takeoff", False, f"only reached {alt:.1f}m" if alt else "no GPS")
        return False

    def test_waypoints(self):
        """Step 5: Fly to 3 waypoints and verify arrival at each."""
        print(f"\n[5] Flying {len(WAYPOINTS)} waypoints ...")
        all_ok = True
        for i, (lat, lon) in enumerate(WAYPOINTS):
            wp_name = f"Waypoint {i+1} ({lat:.5f}, {lon:.5f})"
            print(f"     -> {wp_name}")
            send_goto(self.conn, lat, lon, TAKEOFF_ALT)

            start = time.time()
            arrived = False
            while time.time() - start < TIMEOUT:
                cur_lat, cur_lon, _ = get_position(self.conn)
                if cur_lat is not None:
                    dist = gps_distance(cur_lat, cur_lon, lat, lon)
                    if dist < WAYPOINT_ACCEPT_RADIUS:
                        arrived = True
                        break
                time.sleep(0.5)

            self.record(wp_name, arrived,
                        f"dist={dist:.1f}m" if arrived else "timeout")
            if not arrived:
                all_ok = False
        return all_ok

    def test_yaw(self):
        """Step 6: Command yaw to N, E, S, W and verify heading."""
        print("\n[6] Testing yaw commands ...")
        targets = [("North", 0), ("East", 90), ("South", 180), ("West", 270)]
        all_ok = True

        for name, target_hdg in targets:
            send_yaw(self.conn, target_hdg)
            start = time.time()
            ok = False
            actual = None

            while time.time() - start < TIMEOUT:
                actual = get_heading(self.conn)
                if actual is not None:
                    # Handle 0/360 wraparound
                    diff = abs(actual - target_hdg)
                    if diff > 180:
                        diff = 360 - diff
                    if diff < YAW_TOLERANCE:
                        ok = True
                        break
                time.sleep(0.3)

            self.record(f"Yaw {name} ({target_hdg}deg)", ok,
                        f"actual={actual}deg" if actual else "no data")
            if not ok:
                all_ok = False
        return all_ok

    def test_velocity(self):
        """Step 7: Send velocity commands and verify position changes."""
        print("\n[7] Testing velocity commands ...")
        # Test: fly North for 3 seconds, check latitude increased
        directions = [
            ("North (vx=+3)", 3, 0, 0, "lat", 1),     # vx>0 = north = lat increases
            ("East (vy=+3)",  0, 3, 0, "lon", 1),     # vy>0 = east  = lon increases
        ]
        all_ok = True

        for name, vx, vy, vz, axis, sign in directions:
            # Record start position
            start_lat, start_lon, _ = get_position(self.conn)
            if start_lat is None:
                self.record(f"Velocity {name}", False, "no GPS at start")
                all_ok = False
                continue

            # Send velocity for 3 seconds
            end_time = time.time() + 3.0
            while time.time() < end_time:
                send_velocity(self.conn, vx, vy, vz)
                time.sleep(0.2)

            # Stop
            send_velocity(self.conn, 0, 0, 0)
            time.sleep(1)

            # Check position moved in the right direction
            end_lat, end_lon, _ = get_position(self.conn)
            if end_lat is None:
                self.record(f"Velocity {name}", False, "no GPS at end")
                all_ok = False
                continue

            if axis == "lat":
                delta = (end_lat - start_lat) * sign
                moved = delta > 0.000001  # ~0.1m
            else:
                delta = (end_lon - start_lon) * sign
                moved = delta > 0.000001

            dist = gps_distance(start_lat, start_lon, end_lat, end_lon)
            self.record(f"Velocity {name}", moved, f"moved {dist:.1f}m")
            if not moved:
                all_ok = False

        return all_ok

    def test_land(self):
        """Step 8: Command LAND and verify altitude decreases."""
        print("\n[8] Landing ...")
        ok = set_mode(self.conn, "LAND")
        if not ok:
            self.record("Land command", False, "could not set LAND mode")
            return False

        # Wait for altitude to drop below 2m
        start = time.time()
        while time.time() - start < 60:  # landing can take a while
            _, _, alt = get_position(self.conn)
            if alt is not None and alt < 2.0:
                self.record("Land", True, f"alt={alt:.1f}m")
                return True
            time.sleep(1)

        _, _, alt = get_position(self.conn)
        self.record("Land", False, f"alt still {alt:.1f}m" if alt else "no GPS")
        return False

    def test_disarm(self):
        """Step 9: Wait for auto-disarm after landing."""
        print("\n[9] Waiting for disarm ...")
        start = time.time()
        while time.time() - start < TIMEOUT:
            hb = self.conn.recv_match(type="HEARTBEAT", blocking=True, timeout=2)
            if hb:
                armed = hb.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED
                if not armed:
                    self.record("Disarm", True)
                    return True
            time.sleep(0.5)
        self.record("Disarm", False, "still armed after timeout")
        return False

    def test_landing_distance(self):
        """Step 10: Check landing position is close to home."""
        print("\n[10] Checking landing distance from home ...")
        lat, lon, _ = get_position(self.conn)
        if lat is None:
            self.record("Landing distance", False, "no GPS")
            return False
        dist = gps_distance(lat, lon, HOME_LAT, HOME_LON)
        ok = dist < 5.0
        self.record("Landing distance < 5m", ok, f"{dist:.1f}m from home")
        return ok

    def run_all(self):
        """Run the full test sequence."""
        print("=" * 60)
        print("  SITL SMOKE TEST")
        print("=" * 60)

        # Connect
        if not self.connect():
            self.print_summary()
            return

        # Run tests in order — each depends on the previous
        steps = [
            self.test_heartbeat,
            self.test_set_guided,
            self.test_arm,
            self.test_takeoff,
            self.test_waypoints,
            self.test_yaw,
            self.test_velocity,
            self.test_land,
            self.test_disarm,
            self.test_landing_distance,
        ]

        for step in steps:
            try:
                ok = step()
            except Exception as e:
                self.record(step.__doc__.strip(), False, f"exception: {e}")
                ok = False
            # If arm or takeoff fails, no point continuing
            if not ok and step in (self.test_heartbeat, self.test_set_guided,
                                    self.test_arm, self.test_takeoff):
                print("\n  ** Critical step failed — aborting remaining tests **")
                break

        self.print_summary()

    def print_summary(self):
        """Print final results summary."""
        print("\n" + "=" * 60)
        passed = sum(1 for _, p, _ in self.results if p)
        total = len(self.results)
        print(f"  RESULTS: {passed}/{total} tests passed")
        print("=" * 60)

        for name, ok, detail in self.results:
            status = "PASS" if ok else "FAIL"
            line = f"  [{status}] {name}"
            if detail:
                line += f" — {detail}"
            print(line)

        print("=" * 60)
        if passed == total:
            print("  ALL TESTS PASSED")
        else:
            print(f"  {total - passed} TEST(S) FAILED")
        print("=" * 60)


# ── Main ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SITL smoke test")
    parser.add_argument("--conn", default="tcp:127.0.0.1:5762",
                        help="MAVLink connection string (default: tcp:127.0.0.1:5762)")
    args = parser.parse_args()

    test = SITLSmokeTest(args.conn)
    test.run_all()
