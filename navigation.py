# navigation.py — MAVLink navigation commands
# Wraps all MAVLink command construction in one place.
# Every method uses the EXACT same message format, type_mask, and coordinate
# frame as the original inline code in main.py.

import math
import time
from pymavlink import mavutil

from gps_utils import gps_distance

# ArduCopter custom mode numbers
# https://ardupilot.org/copter/docs/parameters.html#fltmode1
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
    """Thin wrapper around pymavlink MAVLink navigation commands.

    All methods match the exact message construction previously inlined in
    main.py — same type_mask values, same coordinate frames, same parameter
    order.  No protocol changes.

    Parameters
    ----------
    master : mavutil.mavlink_connection
        Active pymavlink connection to the autopilot (Cube / SITL).
    """

    def __init__(self, master):
        self.master = master
        # Throttles (callers can read/write these directly)
        self.last_speed_req = 0.0

    # ── Position commands ────────────────────────────────────────────

    def send_global_target(self, lat, lon, alt, yaw=None):
        """Send a SET_POSITION_TARGET_GLOBAL_INT to fly to (lat, lon, alt).

        Coordinate frame: MAV_FRAME_GLOBAL_RELATIVE_ALT_INT (altitude is
        meters above home).

        Parameters
        ----------
        lat, lon : float
            Target latitude / longitude in degrees.
        alt : float
            Target altitude in meters (relative to home).
        yaw : float or None
            If provided, the drone holds this yaw (radians) and strafes to
            the waypoint without rotating (NO_TURN behaviour).  If None the
            drone rotates to face the next waypoint (default ArduCopter
            behaviour).
        """
        if yaw is not None:
            # Hold current yaw — quadcopter strafes to waypoint without rotating
            # type_mask: bit 10 cleared = yaw field USED, bit 11 set = yaw_rate ignored
            self.master.mav.set_position_target_global_int_send(
                0, self.master.target_system, self.master.target_component,
                mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
                0b100111111000, int(lat * 1e7), int(lon * 1e7), alt,
                0, 0, 0, 0, 0, 0, yaw, 0)
        else:
            # Default: drone rotates to face next waypoint
            self.master.mav.set_position_target_global_int_send(
                0, self.master.target_system, self.master.target_component,
                mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
                0b110111111000, int(lat * 1e7), int(lon * 1e7), alt,
                0, 0, 0, 0, 0, 0, 0, 0)

    def send_velocity(self, vx, vy, vz, yaw_rate=0, current_yaw=0.0):
        """Send a velocity command in the body frame.

        Body-frame inputs are rotated into NED using *current_yaw* before
        being packed into SET_POSITION_TARGET_LOCAL_NED.

        Parameters
        ----------
        vx : float   Forward speed (m/s, positive = nose direction).
        vy : float   Rightward speed (m/s, positive = starboard).
        vz : float   Downward speed (m/s, positive = descend — NED convention).
        yaw_rate : float  Yaw rate in deg/s (positive = CW).
        current_yaw : float  Current heading in radians (needed for body→NED rotation).
        """
        if not self.master:
            return
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
        """Send MAV_CMD_DO_CHANGE_SPEED (throttled to once per 3 s).

        Parameters
        ----------
        speed_mps : float
            Desired ground speed in m/s.
        """
        if time.time() - self.last_speed_req < 3.0:
            return
        self.master.mav.command_long_send(
            self.master.target_system, self.master.target_component,
            mavutil.mavlink.MAV_CMD_DO_CHANGE_SPEED, 0,
            1, speed_mps, -1, 0, 0, 0, 0)
        self.last_speed_req = time.time()

    # ── Arm / Takeoff / Land ─────────────────────────────────────────

    def request_arm(self):
        """Send MAV_CMD_COMPONENT_ARM_DISARM (arm=1).

        Returns the COMMAND_ACK result code, or None if no ACK within 1 s.
        """
        self.master.mav.command_long_send(
            self.master.target_system, self.master.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0,
            1, 0, 0, 0, 0, 0, 0)
        ack = self.master.recv_match(type='COMMAND_ACK', blocking=True, timeout=1)
        if ack:
            return ack.result
        return None

    def request_takeoff(self, alt):
        """Send MAV_CMD_NAV_TAKEOFF to the given altitude (meters AGL).

        Parameters
        ----------
        alt : float
            Target takeoff altitude in meters (relative to home).
        """
        self.master.mav.command_long_send(
            self.master.target_system, self.master.target_component,
            mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0,
            0, 0, 0, 0, 0, 0, alt)

    def send_land(self, lat=0, lon=0):
        """Send MAV_CMD_NAV_LAND at the given GPS position.

        ArduCopter handles throttle, ground detection, and auto-disarm.

        Parameters
        ----------
        lat, lon : float
            Landing coordinates in degrees.  Pass 0, 0 to land at the
            current position (ArduCopter default).
        """
        self.master.mav.command_long_send(
            self.master.target_system, self.master.target_component,
            mavutil.mavlink.MAV_CMD_NAV_LAND, 0,
            0, 0, 0, 0,
            int(lat * 1e7), int(lon * 1e7), 0)

    # ── Mode changes ─────────────────────────────────────────────────

    def set_mode(self, mode_name):
        """Set ArduCopter flight mode by name (e.g. 'GUIDED', 'RTL', 'LAND').

        Uses MAV_CMD_DO_SET_MODE with MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
        which is the same method used in main.py for setting GUIDED mode.

        Parameters
        ----------
        mode_name : str
            One of the ArduCopter mode names: STABILIZE, ALT_HOLD, AUTO,
            GUIDED, LOITER, RTL, LAND, POSHOLD, BRAKE, etc.

        Returns
        -------
        int or None
            COMMAND_ACK result code (0 = accepted), or None if no ACK
            within 1 s.

        Raises
        ------
        ValueError
            If *mode_name* is not a recognised ArduCopter mode.
        """
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
        """Request all data streams at the given rate.

        Parameters
        ----------
        rate_hz : int
            Requested stream rate in Hz (default 10).
        """
        self.master.mav.request_data_stream_send(
            self.master.target_system, self.master.target_component,
            mavutil.mavlink.MAV_DATA_STREAM_ALL, rate_hz, 1)
