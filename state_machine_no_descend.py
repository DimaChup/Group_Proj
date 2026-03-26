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
import sys

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
        'BEACON_DELAY': getattr(main, 'BEACON_DELAY', 0),
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

    # ── Smart-detect deduplication helper ──────────────────────────────

    def _is_near_known(self, lat, lon):
        """Check if position is near any rejected, IOI, or queued target."""
        r = config.REJECTED_TARGET_RADIUS_M
        for rej_lat, rej_lon in self.rejected_targets:
            if self._gps_dist(lat, lon, rej_lat, rej_lon) < r:
                return True
        for item in getattr(self, 'items_of_interest', []):
            if self._gps_dist(lat, lon, item['lat'], item['lon']) < r:
                return True
        for q_item in getattr(self, '_detect_queue', []):
            if self._gps_dist(lat, lon, q_item[0], q_item[1]) < r:
                return True
        return False

    def _is_inside_nfz(self, lat, lon):
        """Check if position is inside the NFZ — never investigate targets there."""
        if hasattr(self, 'geofence') and self.geofence:
            _, inside = self.geofence.distance_to_boundary(lat, lon)
            return inside
        return False

    def _is_outside_search_area(self, lat, lon):
        """Check if position is outside the current search polygon — ignore detections there."""
        if hasattr(self, 'planner') and self.planner and hasattr(self.planner, 'search_polygon'):
            poly = self.planner.search_polygon
            if poly and len(poly) >= 3:
                import cv2
                import numpy as np
                pt = self.planner.geo.gps_to_pixels(lat, lon)
                contour = np.array(poly, dtype=np.float32).reshape(-1, 1, 2)
                result = cv2.pointPolygonTest(contour, (float(pt[0]), float(pt[1])), False)
                return result < 0  # negative = outside
        return False  # no polygon = don't filter

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
                    no_turn=True,
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
            # Send takeoff command only — do NOT send position targets yet,
            # as SET_POSITION_TARGET cancels the NAV_TAKEOFF climb sequence
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

        # Retry arming in SIMULATION if disarmed; safety stop in REAL mode
        if self.master and not self.master.motors_armed():
            if config.MODE == "SIMULATION":
                print("Drone disarmed during takeoff — retrying arm sequence...")
                self._set_state(State.ARMING)
                return
            else:
                print("DRONE DISARMED — safety stop. Re-arm manually via RC.")
                self._set_state(State.DONE)
                return

        if time.time() - self.state_start_time > 60 and not self._takeoff_timeout_warned:
            print("TAKEOFF TIMEOUT: Drone may not be climbing. Check motors and GPS.")
            self._takeoff_timeout_warned = True

        if self.alt >= config.TARGET_ALT * 0.90:
            print("Target Altitude Reached.")

            if config.MODE == "SIMULATION":
                canvas_w, canvas_h = self.sim.map_w, self.sim.map_h
            else:
                canvas_w, canvas_h = REAL_CANVAS_SIZE, REAL_CANVAS_SIZE

            start_gps = self.pre_waypoints[-1] if self.pre_waypoints else (self.lat, self.lon)
            self.waypoints = self.planner.generate_search_pattern(canvas_w, canvas_h, start_gps)

            # Fly transit waypoints first, then search pattern
            if self.pre_waypoints:
                print(f"Flying {len(self.pre_waypoints)} transit waypoints first.")
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

        # Orient drone once: yaw aligned to scan direction + diagonal offset.
        # The diagonal offset rotates the camera so its diagonal (longest dimension)
        # is perpendicular to the scan direction, maximising ground coverage per pass.
        if not getattr(self, '_search_yaw_done', False):
            if hasattr(self.planner, 'last_scan_angle'):
                from pymavlink import mavutil
                if not getattr(self, '_search_yaw_sent', False):
                    if len(self.waypoints) >= 2:
                        wp0 = self.waypoints[0]
                        wp1 = self.waypoints[1]
                        dlat = wp1[0] - wp0[0]
                        dlon = wp1[1] - wp0[1]
                        yaw_deg = math.degrees(math.atan2(dlon * math.cos(math.radians(wp0[0])), dlat)) % 360
                    else:
                        yaw_deg = self.planner.last_scan_angle
                    # Diagonal offset: configurable or auto-computed from camera aspect
                    if config.DIAGONAL_YAW_OFFSET_DEG is not None:
                        diag_offset = config.DIAGONAL_YAW_OFFSET_DEG
                    else:
                        diag_offset = math.degrees(math.atan2(config.IMAGE_W, config.IMAGE_H))
                    yaw_deg = (yaw_deg + diag_offset) % 360
                    self.master.mav.command_long_send(
                        self.master.target_system, self.master.target_component,
                        mavutil.mavlink.MAV_CMD_CONDITION_YAW, 0,
                        yaw_deg, 45, 1, 0, 0, 0, 0)
                    self._search_yaw_sent = True
                    self._search_yaw_target = yaw_deg
                    self._search_yaw_time = time.time()
                    print(f"[YAW] Orienting to {yaw_deg:.0f} deg (diagonal alignment)...")
                    return
                else:
                    yaw_error = abs(math.degrees(self.yaw) - self._search_yaw_target) % 360
                    if yaw_error > 180: yaw_error = 360 - yaw_error
                    if yaw_error < 10 or time.time() - self._search_yaw_time > 5.0:
                        self._search_yaw_done = True
                        print(f"[YAW] Aligned. Starting search pattern.")
                    else:
                        return

        # Speed depends on altitude (slower low = less blur) and focus area
        if getattr(self, '_beacon_triggered', False):
            search_speed = min(config.FOCUS_SEARCH_SPEED_MPS, config.speed_for_altitude(self.alt))
        else:
            search_speed = config.speed_for_altitude(self.alt)
        self.nav.set_speed(search_speed)

        # Auto-trigger PLB beacon after delay (--beacon-delay N)
        beacon_delay = g.get('BEACON_DELAY', 0)
        if beacon_delay > 0 and not getattr(self, '_beacon_triggered', False):
            # Track when SEARCH first started
            if not hasattr(self, '_search_first_start'):
                self._search_first_start = time.time()
            if time.time() - self._search_first_start >= beacon_delay:
                self._trigger_beacon_redirect()

        # --- Detection logic ---
        import __main__ as _main
        smart_detect = getattr(_main, 'SMART_DETECT', False)

        # Detection queue: all detections are queued and investigated in order
        if not hasattr(self, '_detect_queue'):
            self._detect_queue = []
            self._consecutive_detect_count = 0

        if target_found:
            self.calculate_target_gps(px_u, px_v)
            # Ignore detections inside NFZ or outside search area
            if self._is_inside_nfz(self.target_lat, self.target_lon) or \
               self._is_outside_search_area(self.target_lat, self.target_lon):
                target_found = False
                self._consecutive_detect_count = 0
            # Ignore detections near already-known targets (rejected / items of interest)
            elif self._is_near_known(self.target_lat, self.target_lon):
                self._consecutive_detect_count = 0
            else:
                conf = getattr(self, 'current_conf', 0.5)
                if smart_detect:
                    # Multi-frame confirmation (opt-in): require N consecutive frames
                    self._consecutive_detect_count += 1
                    if self._consecutive_detect_count >= config.DETECT_CONFIRM_FRAMES:
                        print(f"[SMART] Confirmed ({self._consecutive_detect_count} frames) at ({self.target_lat:.6f}, {self.target_lon:.6f}) conf={conf:.2f}")
                        self._detect_queue.append((self.target_lat, self.target_lon, conf))
                        self._consecutive_detect_count = 0
                else:
                    # Single-frame trigger (default): queue if not already queued nearby
                    if not self._is_near_known(self.target_lat, self.target_lon):
                        print("TARGET DETECTED!")
                        self._detect_queue.append((self.target_lat, self.target_lon, conf))
        else:
            self._consecutive_detect_count = 0

        # Fly to next waypoint (runs when no new target, or target was rejected)
        if self.state == State.SEARCH:
            # If queue has items, pop and go investigate
            if getattr(self, '_detect_queue', None) and len(self._detect_queue) > 0:
                q_lat, q_lon, q_conf = self._detect_queue.pop(0)
                print(f"Investigating target at ({q_lat:.6f}, {q_lon:.6f}) conf={q_conf:.2f} — {len(self._detect_queue)} remaining")
                self.target_lat = q_lat
                self.target_lon = q_lon
                self.departure_lat = self.lat
                self.departure_lon = self.lon
                self._locked_target = (q_lat, q_lon)
                self._set_state(State.CENTERING)
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
                new_alt = max(config.RESCAN_ALT_FLOOR_M, current_alt * config.RESCAN_ALT_FACTOR)
                if new_alt <= config.RESCAN_ALT_FLOOR_M:
                    print(f"WARNING: Rescan altitude hit {config.RESCAN_ALT_FLOOR_M}m floor. Ending mission.")
                    self._set_state(State.DONE)
                    return
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
                # Re-orient yaw for new pass (waypoints may change direction)
                self._search_yaw_done = False
                self._search_yaw_sent = False
                # Keep rejected targets across passes (N = false positive, don't revisit)
                # Stay in SEARCH — just descend and continue (no transit back)
                self._set_state(State.SEARCH)
            else:
                self._set_state(State.DONE)

    def _handle_centering(self, target_found, px_u, px_v, key):
        # NO-DESCEND variant: center at current altitude, then VERIFY
        import __main__ as _main
        center_verify = getattr(_main, 'CENTER_VERIFY', False)
        smart_detect = getattr(_main, 'SMART_DETECT', False)

        if time.time() - self.state_start_time > 60 and not self._centering_timeout_warned:
            print("CENTERING TIMEOUT: Lost target or can't converge. Resuming search.")
            self._centering_timeout_warned = True
            self._set_state(State.SEARCH)
            return
        if target_found:
            self.calculate_target_gps(px_u, px_v)
            # Target lock: only refine if within lock radius, queue others
            locked = getattr(self, '_locked_target', None)
            if locked:
                dist_to_locked = self._gps_dist(self.target_lat, self.target_lon, locked[0], locked[1])
                if dist_to_locked <= config.DETECT_LOCK_RADIUS_M:
                    # Within lock radius — refine locked target
                    self._locked_target = (self.target_lat, self.target_lon)
                else:
                    # Outside lock radius — queue it if new and not in NFZ
                    if not self._is_inside_nfz(self.target_lat, self.target_lon) and \
                       not self._is_near_known(self.target_lat, self.target_lon):
                        _detect_queue = getattr(self, '_detect_queue', [])
                        c = getattr(self, 'current_conf', 0.5)
                        _detect_queue.append((self.target_lat, self.target_lon, c))
                        self._detect_queue = _detect_queue
                        print(f"New target during CENTERING queued at ({self.target_lat:.6f}, {self.target_lon:.6f})")
                    # Restore locked target for navigation
                    self.target_lat, self.target_lon = locked
        if time.time() - self.last_req > 0.2:
            self.nav.send_global_target(self.target_lat, self.target_lon, self.alt)
            self.last_req = time.time()
        if self.get_dist_to_target() < 1.0:
            if center_verify:
                # --center-verify: start GPS averaging + VERIFY immediately
                self._gps_avg_start = time.time()
                self._gps_avg_samples = []
                self._trig_estimate = (self.target_lat, self.target_lon)
                self._confirmed_y = False
                print()
                print(f"[CENTERING] Centered above target — GPS averaging started")
                print(f"  Trig estimate: ({self.target_lat:.6f}, {self.target_lon:.6f})")
            else:
                # Default: no GPS averaging
                self._gps_avg_start = None
                self._gps_avg_samples = None
                self._confirmed_y = False
            self._set_state(State.VERIFY)
            print()
            print("=" * 50)
            print(f"  VERIFY (at {self.alt:.0f}m — no-descend mode)")
            print("  Is this the target?")
            print("  Y=Confirm  N=Reject  I=Item of Interest")
            print("  (terminal key or browser button)")
            print("=" * 50)

    def _handle_descending(self, target_found, px_u, px_v, key):
        # NO-DESCEND variant: this state should never be reached
        # but if it is, go straight to VERIFY
        self._set_state(State.VERIFY)

    def _handle_verify(self, target_found, px_u, px_v, key):
        self.waiting_for_confirmation = True
        # Timeout after 120s — operator didn't respond, reject and resume search
        if time.time() - self.state_start_time > 120:
            print("WARNING: VERIFY timeout (120s). No operator response — rejecting target.")
            self.rejected_targets.append((self.target_lat, self.target_lon))
            self.waiting_for_confirmation = False
            self._set_state(State.SEARCH)
            return
        # Stay at CURRENT altitude — hold position, don't climb or descend
        self.nav.send_global_target(self.target_lat, self.target_lon, self.alt)
        # Collect GPS samples for averaging (started in CENTERING)
        if getattr(self, '_gps_avg_samples', None) is not None:
            self._gps_avg_samples.append((self.lat, self.lon))
        # If Y was pressed, wait for 10s of averaging then finalize
        if getattr(self, '_confirmed_y', False) and hasattr(self, '_gps_avg_start'):
            elapsed = time.time() - self._gps_avg_start
            if elapsed >= 10.0 and len(self._gps_avg_samples) > 0:
                avg_lat = sum(s[0] for s in self._gps_avg_samples) / len(self._gps_avg_samples)
                avg_lon = sum(s[1] for s in self._gps_avg_samples) / len(self._gps_avg_samples)
                lat_m = 111320.0
                lon_m = 111320.0 * math.cos(math.radians(avg_lat))
                err = math.sqrt(((avg_lat - self.target_lat) * lat_m)**2 +
                                ((avg_lon - self.target_lon) * lon_m)**2)
                print(f"\n[GPS AVG] {len(self._gps_avg_samples)} samples over {elapsed:.1f}s")
                print(f"  Trig estimate:    ({self._trig_estimate[0]:.6f}, {self._trig_estimate[1]:.6f})")
                print(f"  Centered average: ({avg_lat:.6f}, {avg_lon:.6f})")
                print(f"  Difference: {err:.1f}m")
                # Use centered average as final position
                self.target_lat = avg_lat
                self.target_lon = avg_lon
                self._confirmed_y = False
                self._gps_avg_samples = None
                print(f"\nUSER CONFIRMED TARGET. SELECT LANDING SIDE:")
                print(f"  N=North  E=East  S=South  W=West")
                self.selecting_landing_side = True

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
        # Hold at 3m: two-stage servo release, then return
        # Timeline: 0s=arrive → 3s=stage1 → 6s=stage2 → 15s=depart
        self.nav.send_global_target(self.landing_lat, self.landing_lon, 3.0)
        elapsed = time.time() - self.state_start_time
        self._hover_elapsed = elapsed
        elapsed = time.time() - self.state_start_time

        # Servo config (confirm channel + PWM on real drone!)
        SERVO_CHANNEL = 9
        SERVO_CLOSED = 1500
        SERVO_STAGE1 = 1300
        SERVO_STAGE2 = 1100

        # Stage 1: partial release at 3 seconds
        if elapsed >= 3.0 and not hasattr(self, '_servo_stage1_done'):
            self._servo_stage1_done = True
            print(f"  SERVO STAGE 1 — partial release (ch{SERVO_CHANNEL}, PWM {SERVO_STAGE1})")
            if self.master:
                self.master.mav.command_long_send(
                    self.master.target_system, self.master.target_component,
                    mavutil.mavlink.MAV_CMD_DO_SET_SERVO, 0,
                    SERVO_CHANNEL, SERVO_STAGE1, 0, 0, 0, 0, 0)

        # Stage 2: full release at 6 seconds
        if elapsed >= 6.0 and not self._servo_released:
            self._servo_released = True
            print(f"  SERVO STAGE 2 — full release (ch{SERVO_CHANNEL}, PWM {SERVO_STAGE2})")
            if self.master:
                self.master.mav.command_long_send(
                    self.master.target_system, self.master.target_component,
                    mavutil.mavlink.MAV_CMD_DO_SET_SERVO, 0,
                    SERVO_CHANNEL, SERVO_STAGE2, 0, 0, 0, 0, 0)

        if elapsed > 15.0:
            # Close servo before departing
            if self.master:
                self.master.mav.command_long_send(
                    self.master.target_system, self.master.target_component,
                    mavutil.mavlink.MAV_CMD_DO_SET_SERVO, 0,
                    SERVO_CHANNEL, SERVO_CLOSED, 0, 0, 0, 0, 0)
            self._servo_released = False
            if hasattr(self, '_servo_stage1_done'):
                del self._servo_stage1_done
            print(f"Hover complete ({elapsed:.0f}s). Climbing and returning home.")
            # Climb back to transit altitude before returning
            if self.master:
                self.nav.send_global_target(self.lat, self.lon, self._current_search_alt())
                self._climb_start = time.time()
            if self.pre_waypoints:
                # Retrace transit path in reverse
                self.return_wp_index = len(self.pre_waypoints) - 1
                self._set_state(State.RETURN_TRANSIT)
            else:
                # No transit path — go straight home
                self._set_state(State.RETURN_HOME)

    def _handle_return_transit(self, target_found, px_u, px_v, key):
        # Climb to the altitude we were searching at before returning
        return_alt = self._current_search_alt()
        if self.alt < return_alt - 3.0:
            if time.time() - self.last_req > 2.0:
                self.nav.send_global_target(self.lat, self.lon, return_alt)
                self.last_req = time.time()
            return  # wait until we've climbed
        # Fly transit path in reverse at search altitude
        self.nav.set_speed(config.TRANSIT_SPEED_MPS)
        if self.return_wp_index >= 0:
            wp = self.pre_waypoints[self.return_wp_index]
            if time.time() - self.last_req > 2.0:
                self.nav.send_global_target(wp[0], wp[1], return_alt)
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
        # Require 3 consecutive frames below 0.3m (barometer noise filter)
        if self.alt < 0.3:
            self._touchdown_count = getattr(self, '_touchdown_count', 0) + 1
        else:
            self._touchdown_count = 0
        if self._touchdown_count >= 3:
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
            self._land_retries = 0
            print("  MAV_CMD_NAV_LAND sent")
        elif getattr(self, '_land_cmd_sent', False):
            # Retry if not descending after 5s (command may have been rejected)
            elapsed = time.time() - getattr(self, '_land_cmd_time', time.time())
            if elapsed > 5.0 and self.alt > 1.0:
                self._land_retries = getattr(self, '_land_retries', 0) + 1
                if self._land_retries >= 5:
                    print("WARNING: LAND failed after 5 retries. Force disarming.")
                    self.master.mav.command_long_send(
                        self.master.target_system, self.master.target_component,
                        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0,
                        0, 21196, 0, 0, 0, 0, 0)  # 21196 = force disarm
                    self._set_state(State.DONE)
                    return
                print(f"  LAND not descending — retrying MAV_CMD_NAV_LAND ({self._land_retries}/5)")
                self.master.mav.command_long_send(
                    self.master.target_system, self.master.target_component,
                    mavutil.mavlink.MAV_CMD_NAV_LAND, 0,
                    0, 0, 0, 0,
                    int(self.home_lat * 1e7), int(self.home_lon * 1e7), 0)
                self._land_cmd_time = time.time()

    # ── PLB beacon redirect ────────────────────────────────────────────

    def _trigger_beacon_redirect(self):
        """Simulate PLB signal: switch search to Focus Area polygon.
        Priority: 1) focus_area.json on disk (re-read, may be updated mid-flight)
                  2) drawn polygon (already in config.FOCUS_AREA_GPS)
                  3) KML Focus Area (loaded at startup)
        """
        if getattr(self, '_beacon_triggered', False):
            return  # already redirected

        # Try to load/reload from JSON file (allows mid-flight coord updates)
        import json, os
        fa_path = "flight_plans/focus_area.json"
        if os.path.exists(fa_path):
            try:
                with open(fa_path, encoding='utf-8') as f:
                    data = json.load(f)
                loaded = []
                for wp in data:
                    if isinstance(wp, dict):
                        loaded.append((wp["lat"], wp["lon"]))
                    else:
                        loaded.append((wp[0], wp[1]))
                if len(loaded) >= 3:
                    config.FOCUS_AREA_GPS = loaded
                    print(f"[PLB] Loaded focus_area.json: {len(loaded)} points")
            except Exception as e:
                print(f"[PLB] Failed to read {fa_path}: {e}")

        if not config.FOCUS_AREA_GPS or len(config.FOCUS_AREA_GPS) < 3:
            print("[PLB] No Focus Area defined — ignoring beacon")
            return

        self._beacon_triggered = True
        self._search_yaw_done = False  # re-orient for focus area
        self._search_yaw_sent = False
        print()
        print("=" * 50)
        print("  [PLB] BEACON SIGNAL RECEIVED!")
        print(f"  Redirecting to Focus Area ({len(config.FOCUS_AREA_GPS)} points)")
        print("=" * 50)
        print()

        # Swap search polygon to focus area
        g = _get_main_globals()
        REAL_CANVAS_SIZE = g['REAL_CANVAS_SIZE']
        focus_poly_px = [self.geo.gps_to_pixels(lat, lon) for lat, lon in config.FOCUS_AREA_GPS]
        self.planner.search_polygon = focus_poly_px
        self.planner._focus_area = True  # tight margins for focus area coverage
        self.search_poly = focus_poly_px

        # Regenerate lawnmower for the smaller area
        if config.MODE == "SIMULATION":
            canvas_w, canvas_h = g.get('sim_w', REAL_CANVAS_SIZE), g.get('sim_h', REAL_CANVAS_SIZE)
            if hasattr(self, 'sim') and self.sim:
                canvas_w, canvas_h = self.sim.map_w, self.sim.map_h
        else:
            canvas_w, canvas_h = REAL_CANVAS_SIZE, REAL_CANVAS_SIZE

        self.waypoints = self.planner.generate_search_pattern(
            canvas_w, canvas_h, (self.lat, self.lon))
        self.wp_index = 0
        self.rescan_pass = 0
        # Keep rejected targets — N-marked items stay rejected across area switch
        print(f"  New search pattern: {len(self.waypoints)} waypoints")
        print(f"  Searching Focus Area at current altitude")
        print(f"  Flying to Focus Area from current position...")

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
                # Immediately stop — override ArduCopter's last position target
                if self.nav:
                    self.nav.send_velocity(0, 0, 0)
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

        # K key: clear rejected/ignored targets (re-enables detection in those areas)
        if key == ord('k') or key == ord('K'):
            n_rej = len(self.rejected_targets)
            n_ioi = len(getattr(self, 'items_of_interest', []))
            self.rejected_targets.clear()
            if hasattr(self, 'items_of_interest'):
                self.items_of_interest.clear()
            print(f"[RESET] Cleared {n_rej} rejected + {n_ioi} items of interest. All areas re-enabled.")

        # B key: simulate PLB beacon signal — redirect to Focus Area
        if (key == ord('b') or key == ord('B')) and self.state == State.SEARCH:
            self._trigger_beacon_redirect()

        # MANUAL mode — WASD flight controls
        if self.state == State.MANUAL and self.master:
            fly_speed = config.MANUAL_FLY_SPEED_MPS
            climb_rate = config.MANUAL_CLIMB_RATE_MPS
            yaw_rate = config.MANUAL_YAW_RATE_DEGS
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
                # Yaw left (relative, counterclockwise)
                from pymavlink import mavutil
                self.master.mav.command_long_send(
                    self.master.target_system, self.master.target_component,
                    mavutil.mavlink.MAV_CMD_CONDITION_YAW, 0,
                    config.MANUAL_YAW_STEP_DEG, yaw_rate, -1, 1, 0, 0, 0)
            elif key == ord('e') or key == ord('E'):
                # Yaw right (relative, clockwise)
                from pymavlink import mavutil
                self.master.mav.command_long_send(
                    self.master.target_system, self.master.target_component,
                    mavutil.mavlink.MAV_CMD_CONDITION_YAW, 0,
                    config.MANUAL_YAW_STEP_DEG, yaw_rate, 1, 1, 0, 0, 0)

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
                    if getattr(self, '_gps_avg_start', None):
                        # --center-verify: wait for 10s GPS averaging
                        elapsed = time.time() - self._gps_avg_start
                        remaining = max(0, 10.0 - elapsed)
                        self._confirmed_y = True
                        if remaining > 0:
                            print(f"\n  Y confirmed — averaging GPS for {remaining:.0f}s more...")
                        # _handle_verify will finalize when 10s elapsed
                    else:
                        # Default: immediate confirm, no averaging
                        print()
                        print("USER CONFIRMED TARGET. SELECT LANDING SIDE:")
                        print("  N=North  E=East  S=South  W=West")
                        self.selecting_landing_side = True
                elif key == ord('i') or key == ord('I'):
                    # Item of interest — log position, mark on map, continue search
                    if not hasattr(self, 'items_of_interest'):
                        self.items_of_interest = []
                    self.items_of_interest.append({
                        'lat': self.target_lat,
                        'lon': self.target_lon,
                        'alt': self.alt,
                        'time': time.time(),
                    })
                    idx = len(self.items_of_interest)
                    print(f"\n  ITEM OF INTEREST #{idx} logged at ({self.target_lat:.6f}, {self.target_lon:.6f})")
                    print(f"  Marked on map (blue). Continuing search.\n")
                    self.waiting_for_confirmation = False
                    self.target_lat = 0
                    self.target_lon = 0
                    self.last_req = 0
                    # If queue has items, go directly to next target
                    if getattr(self, '_detect_queue', None) and len(self._detect_queue) > 0:
                        q_lat, q_lon, _qc = self._detect_queue.pop(0)
                        print(f"Next queued target at ({q_lat:.6f}, {q_lon:.6f}) — {len(self._detect_queue)} remaining")
                        self.target_lat = q_lat
                        self.target_lon = q_lon
                        self.departure_lat = self.lat  # update departure to current pos
                        self.departure_lon = self.lon
                        self._locked_target = (q_lat, q_lon)
                        self._set_state(State.CENTERING)
                    elif self.departure_lat != 0:
                        self._set_state(State.RETURN_TO_SEARCH)
                    else:
                        self._set_state(State.SEARCH)
                elif key == ord('n') or key == ord('N'):
                    self.rejected_targets.append((self.target_lat, self.target_lon))
                    print(f"USER REJECTED TARGET at ({self.target_lat:.6f}, {self.target_lon:.6f}). RESUMING.")
                    self.waiting_for_confirmation = False
                    self.target_lat = 0
                    self.target_lon = 0
                    self.last_req = 0  # force immediate command
                    # If queue has items, go directly to next target
                    if getattr(self, '_detect_queue', None) and len(self._detect_queue) > 0:
                        q_lat, q_lon, _qc = self._detect_queue.pop(0)
                        print(f"Next queued target at ({q_lat:.6f}, {q_lon:.6f}) — {len(self._detect_queue)} remaining")
                        self.target_lat = q_lat
                        self.target_lon = q_lon
                        self.departure_lat = self.lat  # update departure to current pos
                        self.departure_lon = self.lon
                        self._locked_target = (q_lat, q_lon)
                        self._set_state(State.CENTERING)
                    # If we came from manual flight, return to manual departure
                    elif self.manual_departure_lat != 0 and self.previous_state == State.MANUAL:
                        print(f"  Returning to manual departure point")
                        self._set_state(State.RETURN_FROM_MANUAL)
                    # If we came from search, return to search departure
                    elif self.departure_lat != 0:
                        print(f"  Returning to search departure point")
                        self._set_state(State.RETURN_TO_SEARCH)
                    else:
                        self._set_state(State.SEARCH)
