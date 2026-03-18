# state_machine.py — State handler mixin for VisualFlightMission
#
# Contains all 18 _handle_* methods plus helper methods (_set_state,
# _current_search_alt, get_dist_to_target, get_dist_to_point, _gps_dist).
#
# Navigation calls go through self.nav (a NavigationController instance)
# rather than calling self.send_global_target() etc. directly.
#
# All other state (self.lat, self.lon, self.alt, self.state, self.waypoints,
# self.master, etc.) is accessed via self — inherited by VisualFlightMission.

from states import State
from navigation import NavigationController
import config
import time
import math

# These module-level constants are imported from main.py's namespace.
# The mixin accesses them via the module globals that main.py sets up.
# We import them lazily to avoid circular imports.
_REAL_CANVAS_SIZE = 4800
_SIM_SPEED = None  # set at runtime from main module


def _get_main_globals():
    """Lazy import of main module globals to avoid circular imports."""
    import main
    return {
        'REAL_CANVAS_SIZE': getattr(main, 'REAL_CANVAS_SIZE', 4800),
        'SIM_SPEED': getattr(main, 'SIM_SPEED', 1),
        'NO_TURN': getattr(main, 'NO_TURN', False),
        'SEARCH_PATTERN': getattr(main, 'SEARCH_PATTERN', 'lawnmower'),
    }


class StateHandlersMixin:
    """Mixin providing all state handler methods for the mission state machine.

    Expects the consuming class to have:
      - self.nav: NavigationController with send_global_target(), send_velocity(), set_speed()
      - self.master: pymavlink connection
      - self.state, self.lat, self.lon, self.alt, self.yaw: telemetry
      - self.waypoints, self.wp_index: search pattern data
      - self.target_lat, self.target_lon: detected target position
      - self.landing_lat, self.landing_lon: computed landing spot
      - self.eyes: VisionSystem
      - self.planner: PathPlanner
      - self.sim: SimulationEnvironment (SIMULATION mode only)
      - self.geo: GeoTransformer
      - Various state flags (see __init__ in main.py)
    """

    # ── State transition ──────────────────────────────────────────────

    def _set_state(self, new_state):
        """Change state and reset state timer (FIX 5: state timeouts)."""
        self.state = new_state
        self.state_start_time = time.time()
        # Reset per-state timeout warnings
        self._arming_timeout_warned = False
        self._takeoff_timeout_warned = False
        self._centering_timeout_warned = False
        self._descending_timeout_warned = False
        self._land_cmd_sent = False

    # ── Helper methods ────────────────────────────────────────────────

    def _current_search_alt(self):
        """Return search altitude for current pass (initial or rescan)."""
        if self.rescan_pass == 0:
            return config.TARGET_ALT
        return getattr(self, '_rescan_alt', config.TARGET_ALT)

    def get_dist_to_target(self):
        return self.get_dist_to_point(self.target_lat, self.target_lon)

    def get_dist_to_point(self, t_lat, t_lon):
        lat_scale = 111132.0
        return math.sqrt(((self.lat - t_lat) * lat_scale) ** 2 +
                         ((self.lon - t_lon) * lat_scale * math.cos(math.radians(self.lat))) ** 2)

    @staticmethod
    def _gps_dist(lat1, lon1, lat2, lon2):
        """Distance in meters between two GPS points."""
        s = 111132.0
        return math.sqrt(((lat1 - lat2) * s) ** 2 +
                         ((lon1 - lon2) * s * math.cos(math.radians(lat1))) ** 2)

    # ── Per-state handler methods ─────────────────────────────────────
    # Each method corresponds to one state in the mission state machine.
    # They are called from run() via a dispatch dict. Navigation calls
    # go through self.nav instead of self directly.

    def _handle_init(self, target_found, px_u, px_v, key):
        from pymavlink import mavutil
        if time.time() - self.last_req > 1.0:
            try:
                print(f"Connecting to {config.CONNECTION_STR}...")
                self.master = mavutil.mavlink_connection(config.CONNECTION_STR)
                g = _get_main_globals()
                self.nav = NavigationController(
                    self.master,
                    no_turn=g['NO_TURN'],
                    get_yaw=lambda: self.yaw)
                self.connect_start_time = time.time()  # FIX 4: start heartbeat timeout
                self._set_state(State.CONNECTING)
            except Exception as e:
                print(f"Connection fail: {e}")
            self.last_req = time.time()

    def _handle_connecting(self, target_found, px_u, px_v, key):
        from pymavlink import mavutil
        g = _get_main_globals()
        SIM_SPEED = g['SIM_SPEED']
        # FIX 4: Heartbeat timeout warning
        if self.connect_start_time > 0 and self.last_heartbeat == 0:
            elapsed = time.time() - self.connect_start_time
            if elapsed > 15 and int(elapsed) % 15 == 0 and time.time() - self.last_req > 5:
                print(f"ERROR: No heartbeat from Cube in {int(elapsed)}s. Is mavproxy running?")
                self.last_req = time.time()
        if self.last_heartbeat > 0:
            print("Heartbeat. Requesting Data Stream...")
            self.master.mav.request_data_stream_send(
                self.master.target_system, self.master.target_component,
                mavutil.mavlink.MAV_DATA_STREAM_ALL, 10, 1)
            # Set SITL speedup (only affects simulation, ignored by real Cube)
            if config.MODE == "SIMULATION":
                self.master.mav.param_set_send(
                    self.master.target_system, self.master.target_component,
                    b'SIM_SPEEDUP', SIM_SPEED, mavutil.mavlink.MAV_PARAM_TYPE_REAL32)
                print(f"  SITL speedup set to {SIM_SPEED}x")
            self._set_state(State.ARMING)

    def _handle_arming(self, target_found, px_u, px_v, key):
        from pymavlink import mavutil
        # FIX 5: Arming timeout warning
        arming_elapsed = time.time() - self.state_start_time
        if arming_elapsed > 120 and not self._arming_timeout_warned:
            print("ARMING TIMEOUT: Pre-arm checks may be failing. Check Mission Planner for details.")
            self._arming_timeout_warned = True

        # FIX 1: Wait for GPS fix before attempting to arm
        if not self.gps_fix_ok:
            gps_msg = self.master.recv_match(type='GPS_RAW_INT', blocking=False)
            if gps_msg:
                fix_type = gps_msg.fix_type
                sats = gps_msg.satellites_visible
                if fix_type >= 3 and sats >= 6:
                    self.gps_fix_ok = True
                    # FIX 2: Update position from real GPS (replaces config REF_LAT/REF_LON)
                    self.lat = gps_msg.lat / 1e7
                    self.lon = gps_msg.lon / 1e7
                    # Update home position to actual takeoff location (not config)
                    self.home_lat = self.lat
                    self.home_lon = self.lon
                    print(f"GPS FIX OK — fix_type={fix_type}, sats={sats}, lat={self.lat:.6f}, lon={self.lon:.6f}")
                    print(f"  Home position set to actual GPS: ({self.home_lat:.6f}, {self.home_lon:.6f})")
                elif time.time() - self._last_gps_status_print > 5.0:
                    print(f"Waiting for GPS fix... (fix_type={fix_type}, sats={sats})")
                    self._last_gps_status_print = time.time()
            elif time.time() - self._last_gps_status_print > 5.0:
                print("Waiting for GPS fix... (no GPS_RAW_INT yet)")
                self._last_gps_status_print = time.time()
            # Don't proceed to arm until GPS fix is acquired
        elif self.master.motors_armed():
            print("Armed! Taking Off...")
            self.master.mav.command_long_send(
                self.master.target_system, self.master.target_component,
                mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 0, 0, 0, config.TARGET_ALT)
            self._set_state(State.TAKEOFF)
        elif time.time() - self.last_req > 3.0:
            # Set GUIDED mode (4) — use command_long which works reliably via mavproxy
            self.master.mav.command_long_send(
                self.master.target_system, self.master.target_component,
                mavutil.mavlink.MAV_CMD_DO_SET_MODE, 0,
                mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
                4, 0, 0, 0, 0, 0)  # 4 = GUIDED
            # Check SET_MODE acknowledgement (short timeout to avoid blocking main loop)
            mode_ack = self.master.recv_match(type='COMMAND_ACK', blocking=True, timeout=1)
            if mode_ack:
                if mode_ack.result != 0:
                    print(f"SET_MODE REJECTED: result={mode_ack.result}")
                else:
                    print("SET_MODE (GUIDED) accepted")
            # Small delay to let mode switch settle before arming
            time.sleep(0.5)
            self.master.mav.command_long_send(
                self.master.target_system, self.master.target_component,
                mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, 1, 0, 0, 0, 0, 0, 0)
            arm_ack = self.master.recv_match(type='COMMAND_ACK', blocking=True, timeout=1)
            if arm_ack:
                if arm_ack.result != 0:
                    print(f"ARM REJECTED: result={arm_ack.result}")
                else:
                    print("ARM command accepted")
            self.last_req = time.time()

    def _handle_takeoff(self, target_found, px_u, px_v, key):
        g = _get_main_globals()
        REAL_CANVAS_SIZE = g['REAL_CANVAS_SIZE']
        SEARCH_PATTERN = g['SEARCH_PATTERN']
        # If drone disarmed itself, retry in SIMULATION only (unsafe for real hardware)
        if self.master and not self.master.motors_armed():
            if config.MODE == "SIMULATION":
                print("Drone disarmed during takeoff — retrying arm sequence...")
                self._set_state(State.ARMING)
            else:
                print("DRONE DISARMED — safety stop. Re-arm manually via RC.")
                self._set_state(State.DONE)
        # FIX 5: Takeoff timeout warning
        elif time.time() - self.state_start_time > 60 and not self._takeoff_timeout_warned:
            print("TAKEOFF TIMEOUT: Drone may not be climbing. Check motors and GPS.")
            self._takeoff_timeout_warned = True
        elif self.alt >= config.TARGET_ALT * 0.90:
            print("Target Altitude Reached.")

            if config.MODE == "SIMULATION":
                canvas_w, canvas_h = self.sim.map_w, self.sim.map_h
            else:
                canvas_w, canvas_h = REAL_CANVAS_SIZE, REAL_CANVAS_SIZE  # virtual canvas for planner

            # Use transit endpoint as start reference if transit path exists
            if self.pre_waypoints:
                start_gps = self.pre_waypoints[-1]
            else:
                start_gps = (self.lat, self.lon)

            if SEARCH_PATTERN == "spiral":
                self.waypoints = self.planner.generate_spiral_pattern(
                    canvas_w, canvas_h, start_gps)
            else:
                self.waypoints = self.planner.generate_search_pattern(
                    canvas_w, canvas_h, start_gps)

            # Fly pre-planned waypoints first (if any)
            if self.pre_waypoints:
                print(f"Flying {len(self.pre_waypoints)} pre-planned waypoints first.")
                self.pre_wp_index = 0
                self._set_state(State.PRE_WAYPOINTS)
                self.last_speed_req = 0
            elif self.waypoints:
                print(f"Path generated. Transiting to start point: {self.waypoints[0]}")
                self._set_state(State.TRANSIT_TO_SEARCH)
                self.last_speed_req = 0
            else:
                print("No Waypoints generated.")
                self._set_state(State.HOVER)

    def _handle_pre_waypoints(self, target_found, px_u, px_v, key):
        # Fly pre-planned waypoints before starting search
        self.nav.set_speed(config.TRANSIT_SPEED_MPS)
        if self.pre_wp_index < len(self.pre_waypoints):
            wp = self.pre_waypoints[self.pre_wp_index]
            if time.time() - self.last_req > 2.0:
                self.nav.send_global_target(wp[0], wp[1], config.TARGET_ALT)
                self.last_req = time.time()
            if self.get_dist_to_point(wp[0], wp[1]) < 2.0:
                self.pre_wp_index += 1
                print(f"Pre-waypoint {self.pre_wp_index}/{len(self.pre_waypoints)} reached.")
        else:
            print("All pre-waypoints complete. Starting search pattern.")
            if self.waypoints:
                self._set_state(State.TRANSIT_TO_SEARCH)
            else:
                print("No search waypoints generated.")
                self._set_state(State.HOVER)

    def _handle_return_from_manual(self, target_found, px_u, px_v, key):
        # Fly back to where manual was engaged, then resume previous state
        self.nav.set_speed(config.TRANSIT_SPEED_MPS)
        if time.time() - self.last_req > 2.0:
            self.nav.send_global_target(self.manual_departure_lat,
                                        self.manual_departure_lon,
                                        self.manual_departure_alt)
            self.last_req = time.time()
        if self.get_dist_to_point(self.manual_departure_lat, self.manual_departure_lon) < 3.0:
            print(f"Back at manual departure point. Resuming {self.previous_state}.")
            self.last_req = 0  # force immediate waypoint send on resume
            self._set_state(self.previous_state)

    def _handle_transit_to_search(self, target_found, px_u, px_v, key):
        # Fly to the first waypoint of the search grid (Optimal Entry Point)
        self.nav.set_speed(config.TRANSIT_SPEED_MPS)

        target = self.waypoints[0]
        if time.time() - self.last_req > 2.0:
            self.nav.send_global_target(target[0], target[1], config.TARGET_ALT)
            self.last_req = time.time()

        # Check arrival
        if self.get_dist_to_point(target[0], target[1]) < 2.0:
            print("Reached Search Start Point. Beginning Pattern.")
            self._set_state(State.SEARCH)
            self.wp_index = 0  # Start from index 0

    def _handle_return_to_search(self, target_found, px_u, px_v, key):
        # Climb to search altitude and fly back to where we departed the search path
        search_alt = self._current_search_alt()
        self.nav.set_speed(config.TRANSIT_SPEED_MPS)
        if time.time() - self.last_req > 2.0:
            self.nav.send_global_target(self.departure_lat, self.departure_lon, search_alt)
            self.last_req = time.time()
        if self.get_dist_to_point(self.departure_lat, self.departure_lon) < 3.0 and self.alt > search_alt * 0.85:
            print("Back at departure point. Resuming search pattern.")
            self.departure_lat = 0
            self.departure_lon = 0
            self._set_state(State.SEARCH)

    def _handle_search(self, target_found, px_u, px_v, key):
        g = _get_main_globals()
        REAL_CANVAS_SIZE = g['REAL_CANVAS_SIZE']
        self.nav.set_speed(config.SEARCH_SPEED_MPS)
        if target_found:
            self.calculate_target_gps(px_u, px_v)
            # Skip if detection is near a previously rejected target (within 20m)
            near_rejected = False
            for rej_lat, rej_lon in self.rejected_targets:
                d = self._gps_dist(self.target_lat, self.target_lon, rej_lat, rej_lon)
                if d < 20.0:
                    near_rejected = True
                    break
            if not near_rejected:
                print("TARGET DETECTED!")
                # Remember where we left the search path
                self.departure_lat = self.lat
                self.departure_lon = self.lon
                self._set_state(State.CENTERING)
        # Fly to next waypoint (runs when no new target, or target was rejected)
        if self.state == State.SEARCH:
            if self.wp_index < len(self.waypoints):
                target = self.waypoints[self.wp_index]
                if time.time() - self.last_req > 2.0:
                    self.nav.send_global_target(target[0], target[1], self._current_search_alt())
                    self.last_req = time.time()
                if self.get_dist_to_point(target[0], target[1]) < 2.0:
                    self.wp_index += 1
            elif self.rescan_pass < self.max_rescan_passes:
                # Drop altitude by 20% and rescan from current position
                current_alt = self._current_search_alt()
                new_alt = current_alt * 0.8
                self.rescan_pass += 1
                self._rescan_alt = new_alt  # store for _current_search_alt
                print(f"\n{'=' * 50}")
                print(f"  SEARCH COMPLETE — nothing confirmed.")
                print(f"  Dropping from {current_alt:.0f}m to {new_alt:.0f}m (pass {self.rescan_pass + 1})")
                print(f"{'=' * 50}")
                # Regenerate lawnmower from current position at new altitude
                if config.MODE == "SIMULATION":
                    canvas_w, canvas_h = self.sim.map_w, self.sim.map_h
                else:
                    canvas_w, canvas_h = REAL_CANVAS_SIZE, REAL_CANVAS_SIZE
                # Start from where we are now (end of previous pattern)
                self.waypoints = self.planner.generate_search_pattern(
                    canvas_w, canvas_h, (self.lat, self.lon), alt_override=new_alt)
                self.wp_index = 0
                self.rejected_targets.clear()  # fresh eyes at new altitude
                # Stay in SEARCH — just descend and continue (no transit back)
                self._set_state(State.SEARCH)
            else:
                self._set_state(State.DONE)

    def _handle_centering(self, target_found, px_u, px_v, key):
        # FIX 5: Centering timeout — go back to SEARCH
        if time.time() - self.state_start_time > 60 and not self._centering_timeout_warned:
            print("CENTERING TIMEOUT: Lost target or can't converge. Resuming search.")
            self._centering_timeout_warned = True
            self._set_state(State.SEARCH)
            return
        if target_found:
            self.calculate_target_gps(px_u, px_v)
        if time.time() - self.last_req > 0.2:
            self.nav.send_global_target(self.target_lat, self.target_lon, config.TARGET_ALT)
            self.last_req = time.time()
        if self.get_dist_to_target() < 1.0:
            self._set_state(State.DESCENDING)

    def _handle_descending(self, target_found, px_u, px_v, key):
        # FIX 5: Descending timeout warning
        if time.time() - self.state_start_time > 60 and not self._descending_timeout_warned:
            print("DESCENDING TIMEOUT: Drone may not be descending. Check altitude hold.")
            self._descending_timeout_warned = True
        if target_found:
            self.calculate_target_gps(px_u, px_v)
        if time.time() - self.last_req > 0.5:
            self.nav.send_global_target(self.target_lat, self.target_lon, config.VERIFY_ALT)
            self.last_req = time.time()
        if self.alt <= config.VERIFY_ALT + 1.0:
            self._set_state(State.VERIFY)
            print()
            print("=" * 50)
            print("  VERIFY: Is this the target?")
            print("  Press Y to confirm, N to reject")
            print("  (terminal key or browser button)")
            print("=" * 50)

    def _handle_verify(self, target_found, px_u, px_v, key):
        self.waiting_for_confirmation = True
        self.nav.send_global_target(self.target_lat, self.target_lon, config.VERIFY_ALT)

    def _handle_hover(self, target_found, px_u, px_v, key):
        # HOVER is a fallback when no waypoints exist. Timeout after 60s -> DONE.
        elapsed = time.time() - self.state_start_time
        if elapsed > 60.0:
            print("HOVER TIMEOUT (60s): No waypoints to fly. Ending mission.")
            self._set_state(State.DONE)

    def _handle_approach(self, target_found, px_u, px_v, key):
        # Fly to landing spot and descend to 3m (low enough to see, high enough not to auto-land)
        if time.time() - self.last_req > 0.5:
            self.nav.send_global_target(self.landing_lat, self.landing_lon, 3.0)
            self.last_req = time.time()
        if self.get_dist_to_point(self.landing_lat, self.landing_lon) < 2.0 and self.alt < 4.0:
            print("Hovering at 3m above target for 15 seconds...")
            self._set_state(State.HOVER_TARGET)

    def _handle_hover_target(self, target_found, px_u, px_v, key):
        from pymavlink import mavutil
        # Hold at 3m: wait 5s -> release servo -> wait 10 more s -> return
        self.nav.send_global_target(self.landing_lat, self.landing_lon, 3.0)
        elapsed = time.time() - self.state_start_time
        # Release servo at 5 seconds
        if elapsed >= 5.0 and not self._servo_released:
            self._servo_released = True
            print("  SERVO RELEASE — dropping payload")
            if self.master:
                # MAV_CMD_DO_SET_SERVO: servo channel 9, PWM 1100 (open)
                self.master.mav.command_long_send(
                    self.master.target_system, self.master.target_component,
                    mavutil.mavlink.MAV_CMD_DO_SET_SERVO, 0,
                    9, 1100, 0, 0, 0, 0, 0)
        if elapsed > 15.0:
            self._servo_released = False
            print(f"Hover complete ({elapsed:.0f}s). Climbing and returning home.")
            if self.pre_waypoints:
                # Retrace transit path in reverse
                self.return_wp_index = len(self.pre_waypoints) - 1
                self._set_state(State.RETURN_TRANSIT)
            else:
                # No transit path — go straight home
                self._set_state(State.RETURN_HOME)

    def _handle_return_transit(self, target_found, px_u, px_v, key):
        # Fly transit path in reverse at search altitude
        self.nav.set_speed(config.TRANSIT_SPEED_MPS)
        if self.return_wp_index >= 0:
            wp = self.pre_waypoints[self.return_wp_index]
            if time.time() - self.last_req > 2.0:
                self.nav.send_global_target(wp[0], wp[1], config.TARGET_ALT)
                self.last_req = time.time()
            if self.get_dist_to_point(wp[0], wp[1]) < 2.0:
                print(f"Return transit WP {len(self.pre_waypoints) - self.return_wp_index}/{len(self.pre_waypoints)} reached.")
                self.return_wp_index -= 1
        else:
            print("Transit path retraced. Returning to launch point.")
            self._set_state(State.RETURN_HOME)

    def _handle_return_home(self, target_found, px_u, px_v, key):
        # Fly back to takeoff/home position
        self.nav.set_speed(config.TRANSIT_SPEED_MPS)
        if time.time() - self.last_req > 2.0:
            self.nav.send_global_target(self.home_lat, self.home_lon, config.TARGET_ALT)
            self.last_req = time.time()
        if self.get_dist_to_point(self.home_lat, self.home_lon) < 2.0:
            print("Home reached. Landing.")
            self._set_state(State.LANDING)

    def _handle_landing(self, target_found, px_u, px_v, key):
        from pymavlink import mavutil
        if self.alt < 0.3:
            print("Touchdown. Disarming.")
            self.master.mav.command_long_send(
                self.master.target_system, self.master.target_component,
                mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, 0, 0, 0, 0, 0, 0, 0)

            # Calculate final error from target
            lat_scale = 111132.0
            final_error = math.sqrt(((self.lat - self.home_lat) * lat_scale) ** 2 +
                                    ((self.lon - self.home_lon) * lat_scale * math.cos(math.radians(self.lat))) ** 2)
            self.final_dist = final_error
            print(f"MISSION COMPLETE. Landed {self.final_dist:.2f}m from home.")
            self._set_state(State.DONE)
        elif not getattr(self, '_land_cmd_sent', False):
            # Send MAV_CMD_NAV_LAND once — proper controlled descent
            # ArduCopter handles throttle, ground detection, and auto-disarm
            self.master.mav.command_long_send(
                self.master.target_system, self.master.target_component,
                mavutil.mavlink.MAV_CMD_NAV_LAND, 0,
                0, 0, 0, 0,
                int(self.home_lat * 1e7), int(self.home_lon * 1e7), 0)
            self._land_cmd_sent = True
            self._land_cmd_time = time.time()
            print("  MAV_CMD_NAV_LAND sent")
        elif getattr(self, '_land_cmd_sent', False):
            # Retry if not descending after 5s (command may have been rejected)
            elapsed = time.time() - getattr(self, '_land_cmd_time', time.time())
            if elapsed > 5.0 and self.alt > 1.0:
                print("  LAND not descending — retrying MAV_CMD_NAV_LAND")
                self.master.mav.command_long_send(
                    self.master.target_system, self.master.target_component,
                    mavutil.mavlink.MAV_CMD_NAV_LAND, 0,
                    0, 0, 0, 0,
                    int(self.home_lat * 1e7), int(self.home_lon * 1e7), 0)
                self._land_cmd_time = time.time()

    # ── Key input handling ────────────────────────────────────────────

    def _handle_keys(self, key, target_found, px_u, px_v):
        """Process keyboard/button input: manual override toggle, WASD flight,
        VERIFY confirmations.  Called once per loop iteration from run()."""

        # M key: toggle manual override
        if key == ord('m') or key == ord('M'):
            if self.state != State.MANUAL:
                print("!!! MANUAL CONTROL OVERRIDE !!!")
                print("  WASD=move  R/F=up/down  Q/E=yaw  M=resume auto")
                # Don't overwrite previous_state if we're already returning from manual
                if self.state != State.RETURN_FROM_MANUAL:
                    self.previous_state = self.state
                    self.manual_departure_lat = self.lat
                    self.manual_departure_lon = self.lon
                    self.manual_departure_alt = self.alt
                self._set_state(State.MANUAL)
            else:
                if target_found:
                    # Detection during manual — go investigate immediately
                    print("Target detected during manual flight — investigating!")
                    self.calculate_target_gps(px_u, px_v)
                    self._set_state(State.CENTERING)
                else:
                    # No detection — return to departure point first
                    dist_from_departure = self.get_dist_to_point(
                        self.manual_departure_lat, self.manual_departure_lon)
                    if dist_from_departure > 5.0:
                        print(f"Returning to manual departure point ({dist_from_departure:.0f}m away)...")
                        self._set_state(State.RETURN_FROM_MANUAL)
                    else:
                        print("Resuming Automation...")
                        self.last_req = 0  # force immediate waypoint send
                        self._set_state(self.previous_state)

        # MANUAL mode — WASD flight controls
        if self.state == State.MANUAL and self.master:
            fly_speed = 5.0   # m/s
            climb_rate = 2.0  # m/s
            yaw_rate = 30.0   # deg/s
            if key == ord('w') or key == ord('W'):
                self.nav.send_velocity(fly_speed, 0, 0)
            elif key == ord('s') or key == ord('S'):
                self.nav.send_velocity(-fly_speed, 0, 0)
            elif key == ord('a') or key == ord('A'):
                self.nav.send_velocity(0, -fly_speed, 0)
            elif key == ord('d') or key == ord('D'):
                self.nav.send_velocity(0, fly_speed, 0)
            elif key == ord('r') or key == ord('R'):
                self.nav.send_velocity(0, 0, -climb_rate)
            elif key == ord('f') or key == ord('F'):
                self.nav.send_velocity(0, 0, climb_rate)
            elif key == ord('q') or key == ord('Q'):
                self.nav.send_velocity(0, 0, 0, yaw_rate=-yaw_rate)
            elif key == ord('e') or key == ord('E'):
                self.nav.send_velocity(0, 0, 0, yaw_rate=yaw_rate)

        # VERIFY state — Y/N confirmation and landing side selection
        if self.state == State.VERIFY:
            if self.selecting_landing_side:
                if key in [ord('n'), ord('e'), ord('w'), ord('s'), ord('N'), ord('E'), ord('W'), ord('S')]:
                    self.calculate_landing_spot(chr(key).lower())
                    self.selecting_landing_side = False
                    self.waiting_for_confirmation = False
                    self._set_state(State.APPROACH)
            else:
                if key == ord('y') or key == ord('Y'):
                    print()
                    print("USER CONFIRMED TARGET. SELECT LANDING SIDE:")
                    print("  N=North  E=East  S=South  W=West")
                    self.selecting_landing_side = True
                elif key == ord('n') or key == ord('N'):
                    self.rejected_targets.append((self.target_lat, self.target_lon))
                    print(f"USER REJECTED TARGET at ({self.target_lat:.6f}, {self.target_lon:.6f}). RESUMING.")
                    self.waiting_for_confirmation = False
                    self.target_lat = 0
                    self.target_lon = 0
                    self.last_req = 0  # force immediate command
                    # If we came from manual flight, return to manual departure
                    if self.manual_departure_lat != 0 and self.previous_state == State.MANUAL:
                        print(f"  Returning to manual departure point")
                        self._set_state(State.RETURN_FROM_MANUAL)
                    # If we came from search, return to search departure
                    elif self.departure_lat != 0:
                        print(f"  Returning to search departure point")
                        self._set_state(State.RETURN_TO_SEARCH)
                    else:
                        self._set_state(State.SEARCH)
