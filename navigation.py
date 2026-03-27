"""MAVLink navigation commands for ArduCopter."""

import math
import time
from pymavlink import mavutil


COPTER_MODES = {
    "STABILIZE": 0,
    "ACRO":      1,
    "ALT_HOLD":  2,
    "AUTO":      3,
    "GUIDED":    4,
    "LOITER":    5,
    "RTL":       6,
    "CIRCLE":    7,
    "LAND":      9,
    "DRIFT":    11,
    "SPORT":    13,
    "POSHOLD":  16,
    "BRAKE":    17,
}


class NavigationController:
    """Thin wrapper around pymavlink MAVLink navigation commands."""

    def __init__(self, master, no_turn=False, get_yaw=None):
        self.master = master
        self.no_turn = no_turn
        self._get_yaw = get_yaw
        self.last_speed_req = 0.0

    # ── Position commands ────────────────────────────────────────────

    def send_global_target(self, lat, lon, alt, yaw=None):
        """Fly to (lat, lon, alt) via SET_POSITION_TARGET_GLOBAL_INT (relative-alt frame)."""
        if math.isnan(lat) or math.isnan(lon) or math.isnan(alt):
            print(f"WARNING: NaN in target position (lat={lat}, lon={lon}, alt={alt}) — skipping")
            return
        if lat < -90 or lat > 90 or lon < -180 or lon > 180:
            print(f"WARNING: GPS out of bounds (lat={lat}, lon={lon}) — skipping")
            return
        if alt < 0 or alt > 400:
            print(f"WARNING: altitude out of range ({alt}m) — skipping")
            return

        if yaw is None and self.no_turn and self._get_yaw is not None:
            yaw = self._get_yaw()

        if yaw is not None:
            self.master.mav.set_position_target_global_int_send(
                0, self.master.target_system, self.master.target_component,
                mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
                0b100111111000, int(lat * 1e7), int(lon * 1e7), alt,
                0, 0, 0, 0, 0, 0, yaw, 0)
        else:
            self.master.mav.set_position_target_global_int_send(
                0, self.master.target_system, self.master.target_component,
                mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
                0b110111111000, int(lat * 1e7), int(lon * 1e7), alt,
                0, 0, 0, 0, 0, 0, 0, 0)

    def send_velocity(self, vx, vy, vz, yaw_rate=0, current_yaw=None):
        """Send body-frame velocity command, rotated to NED before transmission."""
        if not self.master:
            return
        if current_yaw is None:
            current_yaw = self._get_yaw() if self._get_yaw is not None else 0.0
        cos_yaw = math.cos(current_yaw)
        sin_yaw = math.sin(current_yaw)
        vx_ned = vx * cos_yaw - vy * sin_yaw
        vy_ned = vx * sin_yaw + vy * cos_yaw
        self.master.mav.set_position_target_local_ned_send(
            0, self.master.target_system, self.master.target_component,
            mavutil.mavlink.MAV_FRAME_LOCAL_NED,
            0b010111000111, 0, 0, 0,
            vx_ned, vy_ned, vz, 0, 0, 0, 0, math.radians(yaw_rate))

    # ── Speed ────────────────────────────────────────────────────────

    def set_speed(self, speed_mps):
        """Send MAV_CMD_DO_CHANGE_SPEED (throttled to once per 3 s)."""
        if time.time() - self.last_speed_req < 3.0:
            return
        self.master.mav.command_long_send(
            self.master.target_system, self.master.target_component,
            mavutil.mavlink.MAV_CMD_DO_CHANGE_SPEED, 0,
            1, speed_mps, -1, 0, 0, 0, 0)
        self.last_speed_req = time.time()

    # ── Arm / Takeoff / Land ─────────────────────────────────────────

    def request_arm(self):
        """Send arm command; return COMMAND_ACK result or None on timeout."""
        self.master.mav.command_long_send(
            self.master.target_system, self.master.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0,
            1, 0, 0, 0, 0, 0, 0)
        ack = self.master.recv_match(type='COMMAND_ACK', blocking=True, timeout=1)
        if ack:
            return ack.result
        return None

    def request_takeoff(self, alt):
        """Send MAV_CMD_NAV_TAKEOFF to the given altitude in meters AGL."""
        if alt <= 0:
            print(f"WARNING: invalid takeoff altitude ({alt}m) — must be positive")
            return
        self.master.mav.command_long_send(
            self.master.target_system, self.master.target_component,
            mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0,
            0, 0, 0, 0, 0, 0, alt)

    def send_land(self, lat=0, lon=0):
        """Send MAV_CMD_NAV_LAND at (lat, lon) in degrees; (0, 0) lands at current position."""
        self.master.mav.command_long_send(
            self.master.target_system, self.master.target_component,
            mavutil.mavlink.MAV_CMD_NAV_LAND, 0,
            0, 0, 0, 0,
            lat, lon, 0)

    # ── Mode changes ─────────────────────────────────────────────────

    def set_mode(self, mode_name):
        """Set ArduCopter flight mode by name; return COMMAND_ACK result or None."""
        key = mode_name.upper()
        if key not in COPTER_MODES:
            raise ValueError(
                f"Unknown ArduCopter mode '{mode_name}'. "
                f"Known modes: {', '.join(sorted(COPTER_MODES))}")
        mode_id = COPTER_MODES[key]
        self.master.mav.command_long_send(
            self.master.target_system, self.master.target_component,
            mavutil.mavlink.MAV_CMD_DO_SET_MODE, 0,
            mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
            mode_id, 0, 0, 0, 0, 0)
        ack = self.master.recv_match(type='COMMAND_ACK', blocking=True, timeout=1)
        if ack:
            return ack.result
        return None

    # ── Data streams ─────────────────────────────────────────────────

    def request_data_stream(self, rate_hz=10):
        """Request all MAVLink data streams at the given rate in Hz."""
        self.master.mav.request_data_stream_send(
            self.master.target_system, self.master.target_component,
            mavutil.mavlink.MAV_DATA_STREAM_ALL, rate_hz, 1)
