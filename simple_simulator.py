# simple_simulator.py
# MVP before main.py — connects to SITL/Cube, you fly with keyboard,
# CV runs and estimates target GPS. Like having an RC controller.
#
# Keyboard = RC sticks (fully manual):
#   SPACE = arm/disarm
#   W/S   = forward/back    A/D = left/right
#   Q/E   = yaw left/right  R/F = throttle up/down
#   C     = auto-fly to target GPS estimate (GPS-based centering)
#   V     = visual servo — pixel-based centering (no GPS needed)
#   L     = emergency land (only automation)
#   ESC   = quit
#
# SIMULATION: python simple_simulator.py
#   - Place dummy on map, fly with keyboard, CV estimates GPS
#
# REAL (future): set DRONE_MODE=REAL && python simple_simulator.py
#   - Real camera, real Cube, pilot uses RC (keyboard disabled)
#
# Optional flags (simulate Pi conditions):
#   --fps 4         Throttle CV to 4 FPS (default: unlimited)
#   --tflite        Force TFLite backend instead of Ultralytics
#   --gps-drift 3   Simulate +/-3m GPS wander (default: off)
#   --shake 5       Simulate camera shake from motor vibration (default: off)
#
# Stepping stone to main.py — same MAVLink, same CV, same GPS math.
#
from pymavlink import mavutil
import cv2
import numpy as np
import math
import sys
import time
import argparse

import config
from utils import GeoTransformer
from vision import VisionSystem

if config.MODE == "SIMULATION":
    from simulation import SimulationEnvironment


class SimpleMission:
    def __init__(self, fps_limit=0, force_tflite=False, gps_drift=0.0, shake=0):
        print(f"=== SIMPLE SIMULATOR ({config.MODE} MODE) ===")
        print("Manual flight + CV detection + GPS estimation")
        if fps_limit > 0:
            print(f"  CV throttle: {fps_limit} FPS")
        if force_tflite:
            print(f"  Backend: TFLite (forced)")
        if gps_drift > 0:
            print(f"  GPS drift: +/-{gps_drift:.1f}m (simulated)")
        if shake > 0:
            print(f"  Camera shake: {shake}px (motor vibration)")
        print()

        # Force TFLite: hide ultralytics AND ensure TFLite interpreter is loaded
        self._ultralytics_hidden = False
        if force_tflite:
            import vision as _vis
            self._orig_yolo = _vis.YOLO
            self._orig_tflite = _vis.TFLiteInterpreter
            _vis.YOLO = None
            # TFLite imports are skipped when Ultralytics is present, so load now
            if _vis.TFLiteInterpreter is None:
                for _try_import in [
                    lambda: __import__('tflite_runtime.interpreter', fromlist=['Interpreter']).Interpreter,
                    lambda: __import__('ai_edge_litert.interpreter', fromlist=['Interpreter']).Interpreter,
                    lambda: __import__('tensorflow').lite.Interpreter,
                ]:
                    try:
                        _vis.TFLiteInterpreter = _try_import()
                        break
                    except (ImportError, AttributeError):
                        continue
                if _vis.TFLiteInterpreter is None:
                    print("WARNING: --tflite requested but no TFLite backend found!")
                    print("  Install one of: tflite-runtime, ai-edge-litert, tensorflow")
                    print("  Falling back to Ultralytics")
                    _vis.YOLO = self._orig_yolo
                    force_tflite = False
            self._ultralytics_hidden = force_tflite

        # --- Setup map/camera (same as main.py) ---
        if config.MODE == "SIMULATION":
            self.sim = SimulationEnvironment(GeoTransformer(map_w_px=100))
            self.geo = GeoTransformer(map_w_px=self.sim.map_w)
            self.sim.geo = self.geo

            # Interactive setup: place dummy + draw search area
            self.target_px, self.tgt_type, self.search_poly = self.sim.setup_on_map()

            self.eyes = VisionSystem(camera_index=None, model_path="best.tflite")
            self.eyes.using_ai = (self.tgt_type == "dummy")

            # Store actual target GPS for accuracy comparison
            self.actual_gps = self.geo.pixels_to_gps(self.target_px[0], self.target_px[1])
            print(f"Target actual GPS: {self.actual_gps[0]:.6f}, {self.actual_gps[1]:.6f}")
        else:
            self.sim = None
            self.geo = GeoTransformer(map_w_px=4800)
            self.search_poly = []
            self.eyes = VisionSystem(camera_index=config.REAL_CAMERA_INDEX, model_path="best.tflite")
            self.eyes.using_ai = True
            self.actual_gps = None  # no ground truth in real mode
            print("Real mode: no ground truth — GPS estimates only")

        # Restore vision module state
        if self._ultralytics_hidden:
            import vision as _vis
            _vis.YOLO = self._orig_yolo
            _vis.TFLiteInterpreter = self._orig_tflite

        # --- MAVLink connection ---
        self.master = None
        self.last_heartbeat = 0
        self.last_req = 0

        # --- Telemetry ---
        # true_lat/true_lon = actual drone position (for camera/map rendering)
        # lat/lon = what the drone's GPS reports (true + drift, for estimation math)
        self.true_lat = config.REF_LAT
        self.true_lon = config.REF_LON
        self.lat = config.REF_LAT
        self.lon = config.REF_LON
        self.alt = 0.0
        self.yaw = 0.0
        self.roll = 0.0
        self.pitch = 0.0
        self.vx = 0.0; self.vy = 0.0; self.vz = 0.0
        self.groundspeed = 0.0

        # --- State ---
        self.state = "INIT"  # INIT → CONNECTING → FLYING (that's it — you fly manually)

        # --- Detection/GPS estimation ---
        self.estimated_gps = None       # latest single estimate
        self.best_gps = None            # best estimate (weighted average)
        self.best_gps_error_m = None    # error of best estimate
        self.gps_error_m = None         # error of latest estimate
        self.detection_count = 0
        self.frame_count = 0
        self.current_conf = 0.0

        # Multi-observation averaging
        self.gps_observations = []      # list of (lat, lon, weight)
        self.centre_snap = False        # True when target is dead centre
        self.CENTRE_THRESHOLD_PX = 30   # pixels from centre to snap

        # CV throttle (0 = unlimited, use --fps to limit)
        self.cv_interval = (1.0 / fps_limit) if fps_limit > 0 else 0
        self.last_cv_time = 0

        # GPS drift simulation (slow random walk, like real GPS)
        self.gps_drift_max = gps_drift      # max drift in metres (0 = off)
        self.drift_north = 0.0              # current drift offset (metres)
        self.drift_east = 0.0
        self.last_drift_time = 0

        # Camera shake simulation (motor vibration, random pixel jitter)
        self.shake_px = shake  # max shake in pixels (0 = off)

        # --- Flight data recording (press B to start/stop) ---
        # Three buckets, all recording (lat, lon) of estimated dummy position:
        #   C mode: GPS EST (weighted avg) — best estimate with GPS-only centering
        #   V mode GPS EST: GPS EST (weighted avg) — improved by centre-snap observations
        #   V mode drone GPS: drone's own GPS — raw proxy (drone is above dummy)
        self.recording = False
        self.c_mode_data = []       # GPS EST during C mode
        self.v_est_data = []        # GPS EST during V mode (improved by centre-snaps)
        self.v_drone_data = []      # drone's own GPS during V mode (raw GPS proxy)
        self.record_interval = 0.3
        self.last_record_time = 0

        # --- Locked estimate (press G while V is centred) ---
        # G starts 30s averaging, then auto-locks
        self.locking = False          # True during 30s collection
        self.lock_start_time = 0
        self.lock_duration = 30       # seconds to average
        self.lock_samples = []        # list of (lat, lon) collected during lock period
        self.locked_gps = None        # (lat, lon) — averaged drone GPS over 30s
        self.locked_est = None        # (lat, lon) — GPS EST at end of lock
        self.locked_error_gps = None  # metres from true (averaged GPS)
        self.locked_error_est = None  # metres from true (GPS EST)

        # --- Offset landing (press L after G lock) ---
        self.landing_offset_m = 7.5   # metres away from dummy to land
        self.landing_target = None     # (lat, lon) — calculated landing coordinate
        self.landing_phase = None      # None, "flying_to", "descending", "landed"
        self.landed_pos = None         # (true_lat, true_lon) — where we actually touched down

        # --- Display ---
        self.view_w_px = 100
        self.view_h_px = 100
        self.zoom_level = 1.0

        # --- Keyboard flight ---
        self.armed = False
        self.fly_speed = 3.0      # m/s for WASD
        self.climb_rate = 2.0     # m/s for R/F
        self.yaw_rate = 30.0      # deg/s for Q/E
        self.centering = False    # True when C pressed (auto-fly to target GPS)
        self.visual_servo = False # True when V pressed (pixel-based centering)
        self.servo_kp = 0.005    # proportional gain: pixel error → m/s
        self.servo_max_speed = 2.0  # max velocity from visual servo (m/s)
        self.servo_alpha = 0.3   # EMA smoothing (0=ignore new, 1=no smoothing)
        self.smooth_u = None     # smoothed target pixel x
        self.smooth_v = None     # smoothed target pixel y
        self.servo_fallback = False  # True when visual servo lost target, using GPS

    def update_telemetry(self):
        """Read all pending MAVLink messages — same as main.py."""
        if not self.master:
            return
        while True:
            msg = self.master.recv_match(blocking=False)
            if not msg:
                break
            mtype = msg.get_type()
            if mtype == 'GLOBAL_POSITION_INT':
                self.true_lat = msg.lat / 1e7
                self.true_lon = msg.lon / 1e7
                self.lat = self.true_lat
                self.lon = self.true_lon
                self.alt = msg.relative_alt / 1000.0
                self.vx = msg.vx / 100.0
                self.vy = msg.vy / 100.0
                self.vz = msg.vz / 100.0
            elif mtype == 'ATTITUDE':
                self.roll = msg.roll
                self.pitch = msg.pitch
                self.yaw = msg.yaw
            elif mtype == 'VFR_HUD':
                self.groundspeed = msg.groundspeed
            elif mtype == 'HEARTBEAT':
                if msg.type != mavutil.mavlink.MAV_TYPE_GCS:
                    self.last_heartbeat = time.time()
                    self.armed = self.master.motors_armed()
                    if self.master.target_system == 0:
                        self.master.target_system = msg.get_srcSystem()
                        self.master.target_component = msg.get_srcComponent()
                        print(f"[LINK] Autopilot found: system {self.master.target_system}")

        # Apply simulated GPS drift (slow random walk)
        # Drift only affects self.lat/lon (what drone "thinks"), not true_lat/lon (physical position)
        if self.gps_drift_max > 0:
            import random
            now = time.time()
            dt = now - self.last_drift_time if self.last_drift_time > 0 else 0.1
            self.last_drift_time = now
            # Random walk step (~0.3m/s wander speed, mean-reverting)
            wander = 0.3 * dt
            self.drift_north += random.gauss(0, wander) - self.drift_north * 0.05 * dt
            self.drift_east += random.gauss(0, wander) - self.drift_east * 0.05 * dt
            # Clamp to max drift
            mag = math.sqrt(self.drift_north**2 + self.drift_east**2)
            if mag > self.gps_drift_max:
                scale = self.gps_drift_max / mag
                self.drift_north *= scale
                self.drift_east *= scale
            # Apply drift to GPS reading only (true position unchanged)
            R = 6378137.0
            self.lat = self.true_lat + (self.drift_north / R) * (180 / math.pi)
            self.lon = self.true_lon + (self.drift_east / (R * math.cos(math.radians(self.true_lat)))) * (180 / math.pi)

    def calculate_target_gps(self, u, v):
        """Convert pixel detection (u,v) to estimated GPS.
        Uses centre-snap when target is near image centre,
        and weighted averaging across multiple observations."""
        Cx = config.IMAGE_W / 2
        Cy = config.IMAGE_H / 2

        # Distance from image centre (pixels)
        dist_from_centre = math.sqrt((u - Cx)**2 + (v - Cy)**2)

        # Centre-snap: target is directly below drone
        if dist_from_centre < self.CENTRE_THRESHOLD_PX:
            est_lat = self.lat
            est_lon = self.lon
            weight = 10.0  # highest confidence
            self.centre_snap = True
        else:
            # Standard pixel-to-GPS math
            gsd_m = (config.SENSOR_WIDTH_MM * self.alt) / (config.FOCAL_LENGTH_MM * config.IMAGE_W)
            delta_x_px = u - Cx
            delta_y_px = v - Cy
            fwd_m = -delta_y_px * gsd_m
            right_m = delta_x_px * gsd_m
            offset_n = fwd_m * math.cos(self.yaw) - right_m * math.sin(self.yaw)
            offset_e = fwd_m * math.sin(self.yaw) + right_m * math.cos(self.yaw)
            R_EARTH = 6378137.0
            dLat = (offset_n / R_EARTH) * (180 / math.pi)
            dLon = (offset_e / (R_EARTH * math.cos(math.radians(self.lat)))) * (180 / math.pi)
            est_lat = self.lat + dLat
            est_lon = self.lon + dLon
            # Weight: closer to centre = higher weight (max 5 at centre, min 1 at edge)
            max_dist = math.sqrt(Cx**2 + Cy**2)
            weight = 1.0 + 4.0 * (1.0 - dist_from_centre / max_dist)
            self.centre_snap = False

        self.estimated_gps = (est_lat, est_lon)

        # Add to observations (keep last 50)
        self.gps_observations.append((est_lat, est_lon, weight))
        if len(self.gps_observations) > 50:
            self.gps_observations = self.gps_observations[-50:]

        # Weighted average of all observations = best estimate
        total_w = sum(w for _, _, w in self.gps_observations)
        avg_lat = sum(lat * w for lat, _, w in self.gps_observations) / total_w
        avg_lon = sum(lon * w for _, lon, w in self.gps_observations) / total_w
        self.best_gps = (avg_lat, avg_lon)

        # Calculate errors if we know ground truth
        if self.actual_gps:
            self.gps_error_m = self._gps_distance(
                est_lat, est_lon, self.actual_gps[0], self.actual_gps[1])
            self.best_gps_error_m = self._gps_distance(
                avg_lat, avg_lon, self.actual_gps[0], self.actual_gps[1])

        return est_lat, est_lon

    def _gps_distance(self, lat1, lon1, lat2, lon2):
        """Haversine distance in metres."""
        R = 6378137.0
        dLat = math.radians(lat2 - lat1)
        dLon = math.radians(lon2 - lon1)
        a = (math.sin(dLat/2)**2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dLon/2)**2)
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    def send_velocity(self, vx, vy, vz, yaw_rate=0):
        """Send velocity command to drone (NED frame, yaw rate in deg/s).
        vx=forward, vy=right, vz=down (NED convention)."""
        if not self.master:
            return
        # Convert body-frame velocities to NED using current yaw
        cos_yaw = math.cos(self.yaw)
        sin_yaw = math.sin(self.yaw)
        vx_ned = vx * cos_yaw - vy * sin_yaw
        vy_ned = vx * sin_yaw + vy * cos_yaw

        self.master.mav.set_position_target_local_ned_send(
            0, self.master.target_system, self.master.target_component,
            mavutil.mavlink.MAV_FRAME_LOCAL_NED,
            0b010111000111,  # ignore position, use velocity + yaw rate
            0, 0, 0,          # position (ignored)
            vx_ned, vy_ned, vz,  # velocity NED
            0, 0, 0,          # acceleration (ignored)
            0, math.radians(yaw_rate))  # yaw, yaw_rate

    def send_arm(self, arm=True):
        """Arm or disarm."""
        if not self.master:
            return
        # Set GUIDED mode first
        self.master.mav.command_long_send(
            self.master.target_system, self.master.target_component,
            mavutil.mavlink.MAV_CMD_DO_SET_MODE, 0,
            mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
            4, 0, 0, 0, 0, 0)  # 4 = GUIDED
        self.master.mav.command_long_send(
            self.master.target_system, self.master.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0,
            1 if arm else 0, 0, 0, 0, 0, 0, 0)
        print(f"[CMD] {'ARM' if arm else 'DISARM'} sent")

    def send_to_gps(self, target_lat, target_lon):
        """Fly toward a GPS position (for auto-centering)."""
        if not self.master:
            return
        self.master.mav.set_position_target_global_int_send(
            0, self.master.target_system, self.master.target_component,
            mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
            0b110111111000,  # use position only
            int(target_lat * 1e7), int(target_lon * 1e7), self.alt,
            0, 0, 0, 0, 0, 0, 0, 0)

    def send_land(self):
        """Land at current position."""
        if not self.master:
            return
        self.master.mav.command_long_send(
            self.master.target_system, self.master.target_component,
            mavutil.mavlink.MAV_CMD_NAV_LAND, 0,
            0, 0, 0, 0, 0, 0, 0)
        print("[CMD] LAND sent")

    def get_frame_and_detect(self):
        """Get camera frame + run CV — returns (frame, found, u, v, conf).
        CV inference is throttled to ~4 FPS to match Pi's real speed."""
        if config.MODE == "SIMULATION":
            # Camera uses TRUE position (where drone physically is, not drifted GPS)
            px, py = self.geo.gps_to_pixels(self.true_lat, self.true_lon)
            # Apply camera shake (random pixel jitter from motor vibration)
            # Shake is ANGULAR (fixed camera pixels), not fixed ground distance.
            # Convert desired camera-pixel shake to map-pixel shake using altitude.
            # At high alt: camera zoomed out → need MORE map pixels for same camera shake
            # At low alt: camera zoomed in → need FEWER map pixels for same camera shake
            if self.shake_px > 0:
                import random
                fov = 2 * math.atan(config.SENSOR_WIDTH_MM / (2 * config.FOCAL_LENGTH_MM))
                safe_alt = max(1.0, self.alt)
                ground_w = 2 * safe_alt * math.tan(fov / 2)
                view_w_map_px = ground_w * self.geo.pix_per_m
                # 1 camera pixel = view_w_map_px / IMAGE_W map pixels
                cam_to_map = view_w_map_px / config.IMAGE_W
                map_shake = self.shake_px * cam_to_map
                px = int(px + random.gauss(0, map_shake * 0.5))
                py = int(py + random.gauss(0, map_shake * 0.5))
            frame, self.view_w_px, self.view_h_px = self.sim.get_drone_view(
                px, py, self.alt, self.yaw)
        else:
            frame = self.eyes.get_frame()
            if frame is None:
                frame = np.zeros((config.IMAGE_H, config.IMAGE_W, 3), dtype=np.uint8)

        # Throttle CV inference (--fps flag, 0 = unlimited)
        if self.cv_interval > 0:
            now = time.time()
            if now - self.last_cv_time < self.cv_interval:
                # Skip inference, return last result
                if hasattr(self, '_last_detection'):
                    return frame, *self._last_detection
                return frame, False, 0, 0, 0.0
            self.last_cv_time = now

        found, u, v, conf = self.eyes.process_frame_manually(frame)
        self.current_conf = conf
        self._last_detection = (found, u, v, conf)
        return frame, found, u, v, conf

    def draw_hud(self, frame, found, u, v, conf):
        """Draw HUD overlay on camera frame."""
        cx, cy = config.IMAGE_W // 2, config.IMAGE_H // 2

        # Crosshair
        cv2.line(frame, (cx - 20, cy), (cx + 20, cy), (0, 255, 255), 2)
        cv2.line(frame, (cx, cy - 20), (cx, cy + 20), (0, 255, 255), 2)

        # Detection marker
        if found:
            cv2.circle(frame, (u, v), 15, (0, 255, 0), 2)
            cv2.line(frame, (u, v), (cx, cy), (0, 255, 0), 2)
            cv2.putText(frame, f"TGT {conf:.2f}", (u + 10, v),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 3)

        # Info panel
        armed_str = "ARMED" if self.armed else "DISARMED"
        armed_color = (0, 0, 255) if self.armed else (100, 100, 100)
        cv2.putText(frame, armed_str, (config.IMAGE_W - 130, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, armed_color, 3)
        cv2.putText(frame, f"MODE: {config.MODE}", (10, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 3)
        cv2.putText(frame, f"ALT: {self.alt:.1f}m  SPD: {self.groundspeed:.1f}m/s  YAW: {math.degrees(self.yaw):.0f}",
                    (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 0), 2)
        cv2.putText(frame, f"Detections: {self.detection_count}/{self.frame_count}",
                    (10, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)

        # Centering / visual servo indicator
        if self.visual_servo:
            if self.servo_fallback:
                cv2.putText(frame, "V: GPS FALLBACK", (config.IMAGE_W - 230, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 3)
            else:
                cv2.putText(frame, "VISUAL SERVO", (config.IMAGE_W - 200, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 3)
        elif self.centering:
            cv2.putText(frame, "GPS CENTRE", (config.IMAGE_W - 170, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 3)

        # Centre-snap indicator
        if self.centre_snap:
            cv2.putText(frame, "SNAP", (cx + 25, cy - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 3)
            cv2.circle(frame, (cx, cy), 25, (0, 255, 255), 2)

        # Recording indicator
        if self.recording:
            mode_name = "V" if self.visual_servo else ("C" if self.centering else "---")
            n_samples = len(self.v_est_data) if self.visual_servo else len(self.c_mode_data)
            cv2.putText(frame, f"REC [{mode_name}] {n_samples}",
                        (config.IMAGE_W - 160, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            # Blinking red dot
            if int(time.time() * 2) % 2:
                cv2.circle(frame, (config.IMAGE_W - 170, 75), 6, (0, 0, 255), -1)

        # Controls hint at bottom
        cv2.putText(frame, "SPC:arm WASD:fly QE:yaw RF:alt C:gps V:vision G:lock B:rec L:land",
                    (10, config.IMAGE_H - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (180, 180, 180), 2)

        # ========== DUMMY POSITION PANEL (left side) ==========
        y = 170
        n_obs = len(self.gps_observations)

        cv2.putText(frame, "--- DUMMY ---", (10, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 2)
        y += 20

        # Actual dummy position (ground truth — orange)
        if self.actual_gps:
            cv2.putText(frame, f"ACTUAL:    {self.actual_gps[0]:.6f}, {self.actual_gps[1]:.6f}",
                        (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 128, 255), 2)
            y += 20

        # GPS-only estimate (weighted avg from flyover detections — cyan)
        if self.best_gps:
            cv2.putText(frame, f"GPS EST:   {self.best_gps[0]:.6f}, {self.best_gps[1]:.6f}",
                        (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
            y += 18
            if self.actual_gps and self.best_gps_error_m is not None:
                err_color = ((0, 255, 0) if self.best_gps_error_m < 3
                             else (0, 128, 255) if self.best_gps_error_m < 10
                             else (0, 0, 255))
                cv2.putText(frame, f"  error: {self.best_gps_error_m:.2f}m  ({n_obs} obs" +
                            (", SNAP" if self.centre_snap else "") + ")",
                            (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.45, err_color, 2)
                y += 18

        # Latest single detection estimate (green)
        if self.estimated_gps:
            cv2.putText(frame, f"LATEST:    {self.estimated_gps[0]:.6f}, {self.estimated_gps[1]:.6f}",
                        (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            y += 18
            if self.actual_gps and self.gps_error_m is not None:
                cv2.putText(frame, f"  error: {self.gps_error_m:.2f}m",
                            (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 2)
                y += 18

        # ========== DRONE POSITION PANEL (left side) ==========
        y += 8
        cv2.putText(frame, "--- DRONE ---", (10, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 2)
        y += 20

        # Drone GPS position (what Cube reports — white, may be drifted)
        cv2.putText(frame, f"GPS POS:   {self.lat:.6f}, {self.lon:.6f}",
                    (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        y += 20

        # Drone TRUE position (where it physically is — only in sim with drift)
        if self.gps_drift_max > 0:
            cv2.putText(frame, f"TRUE POS:  {self.true_lat:.6f}, {self.true_lon:.6f}",
                        (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 128), 2)
            y += 18
            drift_m = math.sqrt(self.drift_north**2 + self.drift_east**2)
            cv2.putText(frame, f"  GPS drift: {drift_m:.1f}m",
                        (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)
            y += 20

        # Distance from drone TRUE position to ACTUAL dummy position
        if self.actual_gps:
            drone_to_dummy = self._gps_distance(
                self.true_lat, self.true_lon, self.actual_gps[0], self.actual_gps[1])
            dtd_color = ((0, 255, 0) if drone_to_dummy < 3
                         else (0, 128, 255) if drone_to_dummy < 10
                         else (0, 0, 255))
            cv2.putText(frame, f"DRONE->DUMMY: {drone_to_dummy:.2f}m",
                        (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, dtd_color, 2)
            y += 20

        # ========== LOCKING / LOCKED ESTIMATE (press G) ==========
        if self.locking:
            elapsed = time.time() - self.lock_start_time
            remaining = max(0, self.lock_duration - elapsed)
            n = len(self.lock_samples)
            y += 5
            # Blinking indicator
            if int(time.time() * 2) % 2:
                cv2.putText(frame, f"LOCKING... {remaining:.0f}s  ({n} samples)",
                            (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 255), 2)
            else:
                cv2.putText(frame, f"LOCKING... {remaining:.0f}s  ({n} samples)",
                            (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 0, 255), 2)
            y += 20
        elif self.locked_gps:
            y += 5
            cv2.putText(frame, f"--- LOCKED ({len(self.lock_samples)} samples, {self.lock_duration}s) ---",
                        (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 0, 255), 2)
            y += 18
            cv2.putText(frame, f"Avg GPS: {self.locked_gps[0]:.6f}, {self.locked_gps[1]:.6f}  err: {self.locked_error_gps:.2f}m",
                        (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 255), 2)
            y += 16
            if self.locked_est:
                cv2.putText(frame, f"GPS EST: {self.locked_est[0]:.6f}, {self.locked_est[1]:.6f}  err: {self.locked_error_est:.2f}m",
                            (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 2)
                y += 16
            y += 5

        # ========== LANDING STATUS ==========
        if self.landing_phase:
            y += 3
            if self.landing_phase == "flying_to":
                cv2.putText(frame, "LANDING: Flying to 7.5m offset...",
                            (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 200, 255), 2)
            elif self.landing_phase == "descending":
                cv2.putText(frame, "LANDING: Descending...",
                            (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 200, 255), 2)
            elif self.landing_phase == "landed" and self.landed_pos and self.actual_gps:
                landed_to_dummy = self._gps_distance(
                    self.landed_pos[0], self.landed_pos[1],
                    self.actual_gps[0], self.actual_gps[1])
                cv2.putText(frame, f"LANDED {landed_to_dummy:.1f}m from dummy (wanted {self.landing_offset_m}m)",
                            (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            y += 20

        # ========== SIM FLAGS (left side) ==========
        if self.shake_px > 0:
            fov = 2 * math.atan(config.SENSOR_WIDTH_MM / (2 * config.FOCAL_LENGTH_MM))
            safe_alt = max(1.0, self.alt)
            gsd = (2 * safe_alt * math.tan(fov / 2)) / config.IMAGE_W
            ground_cm = self.shake_px * gsd * 100
            cv2.putText(frame, f"SHAKE: {self.shake_px}px = {ground_cm:.0f}cm on ground",
                        (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)

        return frame

    def run(self):
        """Main loop — state machine: INIT → CONNECTING → FLYING.
        YOU arm and take off manually (RC / Mission Planner).
        Script just reads telemetry + runs CV + estimates GPS."""
        print("Starting mission loop...")
        cv2.namedWindow("Simple Simulator")

        if config.MODE == "SIMULATION":
            cv2.setMouseCallback("Simple Simulator", self._mouse_cb)

        while True:
            self.update_telemetry()

            # Get frame + detect once connected
            frame = None
            found = False; u = 0; v = 0; conf = 0.0

            if self.state == "FLYING":
                self.frame_count += 1
                frame, found, u, v, conf = self.get_frame_and_detect()
                if found:
                    self.detection_count += 1
                    self.calculate_target_gps(u, v)
                    snap_str = " SNAP!" if self.centre_snap else ""
                    best_str = (f" best:{self.best_gps_error_m:.2f}m"
                                if self.best_gps_error_m is not None else "")
                    print(f"[CV] #{self.detection_count}: "
                          f"({u},{v}) conf {conf:.2f}{snap_str} → "
                          f"err {self.gps_error_m:.2f}m{best_str}"
                          if self.gps_error_m else
                          f"[CV] #{self.detection_count}: ({u},{v}) conf {conf:.2f}")

                # Auto-centering: fly toward best estimate (GPS-based)
                if self.centering and self.best_gps and self.master:
                    if found:
                        self.send_to_gps(self.best_gps[0], self.best_gps[1])
                    else:
                        self.send_to_gps(self.best_gps[0], self.best_gps[1])

                # Visual servo: vision when available, GPS fallback when lost
                if self.visual_servo and self.master:
                    if found:
                        self.servo_fallback = False
                        # Smooth detection position (EMA filter to reduce shake noise)
                        if self.smooth_u is None:
                            self.smooth_u = float(u)
                            self.smooth_v = float(v)
                        else:
                            self.smooth_u = self.servo_alpha * u + (1 - self.servo_alpha) * self.smooth_u
                            self.smooth_v = self.servo_alpha * v + (1 - self.servo_alpha) * self.smooth_v

                        cx = config.IMAGE_W / 2
                        cy = config.IMAGE_H / 2
                        err_x = self.smooth_u - cx  # positive = target is right
                        err_y = self.smooth_v - cy  # positive = target is below

                        # Proportional control: pixel offset → velocity
                        vel_right = self.servo_kp * err_x
                        vel_fwd = -self.servo_kp * err_y  # image y is inverted
                        # Clamp speed
                        speed = math.sqrt(vel_fwd**2 + vel_right**2)
                        if speed > self.servo_max_speed:
                            scale = self.servo_max_speed / speed
                            vel_fwd *= scale
                            vel_right *= scale
                        self.send_velocity(vel_fwd, vel_right, 0)

                        if abs(err_x) < 15 and abs(err_y) < 15:
                            print(f"[VSERVO] CENTRED! pixel err: ({err_x:.0f}, {err_y:.0f})")
                    else:
                        # Target lost — fall back to GPS estimate
                        self.servo_fallback = True
                        if self.best_gps:
                            self.send_to_gps(self.best_gps[0], self.best_gps[1])
                        else:
                            self.send_velocity(0, 0, 0)

                # --- Offset landing sequence ---
                if self.landing_phase == "flying_to" and self.landing_target and self.master:
                    self.send_to_gps(self.landing_target[0], self.landing_target[1])
                    # Check if close enough to start descending
                    dist_to_land = self._gps_distance(
                        self.true_lat, self.true_lon,
                        self.landing_target[0], self.landing_target[1])
                    if dist_to_land < 3.0 and self.groundspeed < 1.0:
                        self.landing_phase = "descending"
                        print(f"[LAND] Arrived at landing point ({dist_to_land:.1f}m). Descending...")
                        self.send_land()
                elif self.landing_phase == "descending":
                    if self.alt < 0.5:
                        self.landing_phase = "landed"
                        self.landed_pos = (self.true_lat, self.true_lon)
                        # Calculate all errors
                        landed_to_dummy = self._gps_distance(
                            self.landed_pos[0], self.landed_pos[1],
                            self.actual_gps[0], self.actual_gps[1])
                        landed_to_target = self._gps_distance(
                            self.landed_pos[0], self.landed_pos[1],
                            self.landing_target[0], self.landing_target[1])
                        est_to_actual = self.locked_error_gps if self.locked_error_gps else 0
                        print(f"\n{'='*50}")
                        print(f"  LANDING REPORT")
                        print(f"{'='*50}")
                        print(f"  Dummy (actual):     {self.actual_gps[0]:.6f}, {self.actual_gps[1]:.6f}")
                        print(f"  Dummy (estimate):   {self.locked_gps[0]:.6f}, {self.locked_gps[1]:.6f}  (err: {est_to_actual:.2f}m)")
                        print(f"  Landing target:     {self.landing_target[0]:.6f}, {self.landing_target[1]:.6f}  ({self.landing_offset_m}m north of estimate)")
                        print(f"  Actual landed at:   {self.landed_pos[0]:.6f}, {self.landed_pos[1]:.6f}")
                        print(f"  ---")
                        print(f"  Landing GPS error:  {landed_to_target:.2f}m  (how far from target coordinate)")
                        print(f"  Distance to dummy:  {landed_to_dummy:.2f}m  (wanted {self.landing_offset_m}m)")
                        print(f"  Off by:             {abs(landed_to_dummy - self.landing_offset_m):.2f}m  from intended {self.landing_offset_m}m")
                        print(f"{'='*50}")

                # --- G lock: collect GPS samples for 30s then auto-lock ---
                # ONLY collect when centre-snap is active (target confirmed at centre)
                if self.locking and self.visual_servo:
                    elapsed = time.time() - self.lock_start_time
                    if found and self.centre_snap:
                        self.lock_samples.append((self.lat, self.lon))
                    # Check if done
                    if elapsed >= self.lock_duration:
                        self.locking = False
                        n = len(self.lock_samples)
                        if n == 0:
                            print(f"[LOCK] FAILED — 0 snap samples in {self.lock_duration}s "
                                  "(target wasn't centred). Try again.")
                        else:
                            # Average all collected GPS readings (only from snaps)
                            avg_lat = sum(s[0] for s in self.lock_samples) / n
                            avg_lon = sum(s[1] for s in self.lock_samples) / n
                            self.locked_gps = (avg_lat, avg_lon)
                            self.locked_error_gps = self._gps_distance(
                                avg_lat, avg_lon, self.actual_gps[0], self.actual_gps[1])
                            # Also snapshot GPS EST at this moment
                            if self.best_gps:
                                self.locked_est = (self.best_gps[0], self.best_gps[1])
                                self.locked_error_est = self._gps_distance(
                                    self.best_gps[0], self.best_gps[1],
                                    self.actual_gps[0], self.actual_gps[1])
                            print(f"\n[LOCK] === LOCKED after {self.lock_duration}s ({n} snap samples) ===")
                            print(f"[LOCK] Avg GPS:  {avg_lat:.6f}, {avg_lon:.6f}  "
                                  f"(error: {self.locked_error_gps:.2f}m)")
                            if self.locked_est:
                                print(f"[LOCK] GPS EST:  {self.locked_est[0]:.6f}, {self.locked_est[1]:.6f}  "
                                      f"(error: {self.locked_error_est:.2f}m)")
                            print(f"[LOCK] ACTUAL:   {self.actual_gps[0]:.6f}, {self.actual_gps[1]:.6f}")
                elif self.locking and not self.visual_servo:
                    # V mode turned off during lock — cancel
                    self.locking = False
                    self.lock_samples = []
                    print("[LOCK] Cancelled — V mode was turned off")

                # --- Record data when B is active ---
                if self.recording and self.actual_gps:
                    now_rec = time.time()
                    if now_rec - self.last_record_time >= self.record_interval:
                        self.last_record_time = now_rec
                        if self.visual_servo:
                            if self.best_gps:
                                self.v_est_data.append((self.best_gps[0], self.best_gps[1]))
                            self.v_drone_data.append((self.lat, self.lon))
                        elif self.centering and self.best_gps:
                            self.c_mode_data.append((self.best_gps[0], self.best_gps[1]))

            # Build display
            if frame is not None:
                frame = self.draw_hud(frame, found, u, v, conf)
            else:
                # Blank frame with status
                frame = np.zeros((config.IMAGE_H, config.IMAGE_W, 3), dtype=np.uint8)
                cv2.putText(frame, f"STATE: {self.state}", (10, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 0), 2)
                cv2.putText(frame, f"Waiting for connection...", (10, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 1)
                cv2.putText(frame, f"SPC=arm  R=throttle up  WASD=fly  L=land", (10, 140),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

            # Composite with god view (simulation only)
            if config.MODE == "SIMULATION" and self.sim:
                # God view uses TRUE position (where drone physically is on the map)
                px, py = self.geo.gps_to_pixels(self.true_lat, self.true_lon)
                # Show best estimate on god view (or latest if no average yet)
                show_gps = self.best_gps if self.best_gps else (
                    self.estimated_gps if self.estimated_gps else (0, 0))
                god_frame = self.sim.get_god_view(
                    px, py, self.yaw, self.view_w_px, self.view_h_px,
                    self.zoom_level, np.array([], np.int32), self.search_poly,
                    show_gps, (0, 0), self.geo)
                h_scale = frame.shape[0] / god_frame.shape[0]
                god_resized = cv2.resize(god_frame,
                    (int(god_frame.shape[1] * h_scale), frame.shape[0]))
                final = np.hstack((god_resized, frame))
            else:
                final = frame

            cv2.imshow("Simple Simulator", final)

            # ─── STATE MACHINE ───
            if self.state == "INIT":
                if time.time() - self.last_req > 1.0:
                    try:
                        print(f"Connecting to {config.CONNECTION_STR}...")
                        self.master = mavutil.mavlink_connection(config.CONNECTION_STR)
                        self.state = "CONNECTING"
                    except Exception as e:
                        print(f"Connection fail: {e}")
                    self.last_req = time.time()

            elif self.state == "CONNECTING":
                if self.last_heartbeat > 0:
                    print("Heartbeat received. Requesting data streams...")
                    self.master.mav.request_data_stream_send(
                        self.master.target_system, self.master.target_component,
                        mavutil.mavlink.MAV_DATA_STREAM_ALL, 10, 1)
                    print()
                    print("=== CONNECTED — Keyboard RC ready ===")
                    print("  SPACE = arm/disarm")
                    print("  R/F = throttle up/down (R to lift off)")
                    print("  W/S = forward/back   A/D = left/right")
                    print("  Q/E = yaw left/right")
                    print("  C = GPS centering (fly to estimate, WASD cancels)")
                    print("  V = visual servo (pixel-based centering, WASD cancels)")
                    print("  L = emergency land   ESC = quit")
                    print()
                    self.state = "FLYING"

            elif self.state == "FLYING":
                pass  # telemetry + CV handled above

            # ─── KEY HANDLING (keyboard = RC controller) ───
            key = cv2.waitKey(20) & 0xFF
            if key == 27:  # ESC
                break
            elif key == ord(' '):  # SPACE = arm/disarm toggle
                self.armed = not self.armed
                self.send_arm(self.armed)
            elif key == ord('l') or key == ord('L'):
                if self.locked_gps and self.landing_phase is None:
                    # Calculate landing point 7.5m north of estimated dummy position
                    R = 6371000
                    est_lat, est_lon = self.locked_gps
                    offset_lat = self.landing_offset_m / R * (180 / math.pi)
                    land_lat = est_lat + offset_lat
                    land_lon = est_lon
                    self.landing_target = (land_lat, land_lon)
                    self.landing_phase = "flying_to"
                    self.centering = False
                    self.visual_servo = False
                    print(f"\n[LAND] Landing {self.landing_offset_m}m north of estimated dummy")
                    print(f"[LAND] Target: {land_lat:.6f}, {land_lon:.6f}")
                    print(f"[LAND] Flying to landing point...")
                elif self.landing_phase == "landed":
                    print("[LAND] Already landed.")
                else:
                    self.send_land()  # emergency land (no G lock)
            elif key == ord('b') or key == ord('B'):  # toggle recording
                self.recording = not self.recording
                if self.recording:
                    mode_name = "V" if self.visual_servo else ("C" if self.centering else "manual")
                    print(f"[REC] Recording STARTED ({mode_name} mode)")
                else:
                    print(f"[REC] Recording STOPPED — C:{len(self.c_mode_data)}, V est:{len(self.v_est_data)}, V drone:{len(self.v_drone_data)} samples")
            elif key == ord('g') or key == ord('G'):  # lock GPS estimate
                if self.locking:
                    # Cancel ongoing lock
                    self.locking = False
                    self.lock_samples = []
                    print("[LOCK] Cancelled")
                elif self.visual_servo and self.actual_gps:
                    # Start 30s averaging
                    self.locking = True
                    self.lock_start_time = time.time()
                    self.lock_samples = []
                    self.locked_gps = None
                    self.locked_est = None
                    print(f"[LOCK] Averaging for {self.lock_duration}s... keep V mode on")
                else:
                    print("[LOCK] Centre on dummy with V mode first, then press G to lock")
            elif self.state == "FLYING" and self.master:
                if key == ord('c') or key == ord('C'):  # toggle GPS centering
                    if self.best_gps:
                        self.centering = not self.centering
                        self.visual_servo = False  # can't have both
                        if self.centering:
                            print(f"[GPS] Centering on {self.best_gps[0]:.6f}, {self.best_gps[1]:.6f}")
                        else:
                            print("[GPS] Manual control resumed")
                    else:
                        print("[GPS] No target detected yet — fly closer first")
                elif key == ord('v') or key == ord('V'):  # toggle visual servo
                    self.visual_servo = not self.visual_servo
                    self.centering = False  # can't have both
                    if self.visual_servo:
                        self.smooth_u = None  # reset filter for fresh start
                        self.smooth_v = None
                        print("[VSERVO] Visual servo ON — using pixel offset to centre")
                    else:
                        print("[VSERVO] Visual servo OFF — manual control")
                elif key in (ord('w'), ord('s'), ord('a'), ord('d'),
                             ord('q'), ord('e'), ord('r'), ord('f')):
                    # Any manual input cancels centering / visual servo
                    if self.centering or self.visual_servo:
                        self.centering = False
                        self.visual_servo = False
                        print("[MANUAL] Override — auto modes cancelled")
                    # RC stick commands via velocity
                    if key == ord('w'):
                        self.send_velocity(self.fly_speed, 0, 0)
                    elif key == ord('s'):
                        self.send_velocity(-self.fly_speed, 0, 0)
                    elif key == ord('a'):
                        self.send_velocity(0, -self.fly_speed, 0)
                    elif key == ord('d'):
                        self.send_velocity(0, self.fly_speed, 0)
                    elif key == ord('r'):  # throttle up
                        if self.alt < 0.5 and self.armed:
                            self.master.mav.command_long_send(
                                self.master.target_system, self.master.target_component,
                                mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0,
                                0, 0, 0, 0, 0, 0, 2.0)
                            print("[RC] Lifting off...")
                        else:
                            self.send_velocity(0, 0, -self.climb_rate)
                    elif key == ord('f'):
                        self.send_velocity(0, 0, self.climb_rate)
                    elif key == ord('q'):
                        self.send_velocity(0, 0, 0, yaw_rate=-self.yaw_rate)
                    elif key == ord('e'):
                        self.send_velocity(0, 0, 0, yaw_rate=self.yaw_rate)

        # ─── SUMMARY ───
        cv2.destroyAllWindows()
        print()
        print("=== SESSION SUMMARY ===")
        print(f"  Frames processed: {self.frame_count}")
        print(f"  Detections: {self.detection_count}")
        n_obs = len(self.gps_observations)
        if self.best_gps:
            print(f"  GPS observations: {n_obs}")
            print(f"  Best estimate (weighted avg): {self.best_gps[0]:.6f}, {self.best_gps[1]:.6f}")
            if self.actual_gps and self.best_gps_error_m is not None:
                print(f"  Best estimate error: {self.best_gps_error_m:.2f} m")
        if self.estimated_gps:
            print(f"  Last single estimate: {self.estimated_gps[0]:.6f}, {self.estimated_gps[1]:.6f}")
            if self.actual_gps and self.gps_error_m is not None:
                print(f"  Last estimate error: {self.gps_error_m:.2f} m")
        if self.actual_gps:
            print(f"  Actual target GPS:  {self.actual_gps[0]:.6f}, {self.actual_gps[1]:.6f}")
        if not self.estimated_gps and not self.best_gps:
            print("  No detections occurred.")

        # ─── END-OF-FLIGHT CHART ───
        self._show_flight_chart()

    def _show_flight_chart(self):
        """Show end-of-flight scatter: estimated dummy positions for C vs V mode.
        Three datasets: C GPS EST, V GPS EST (improved by snaps), V drone GPS (raw proxy).
        True dummy at centre (0,0), plotted in metres offset."""
        c_data = self.c_mode_data
        v_est = self.v_est_data
        v_drone = self.v_drone_data

        if not c_data and not v_est and not v_drone:
            print("  No recorded data — press B during C or V mode to record.")
            return

        if not self.actual_gps:
            print("  No actual dummy position — can't generate chart.")
            return

        try:
            import matplotlib.pyplot as plt
            import matplotlib.patches as patches
        except ImportError:
            print("  matplotlib not installed — skipping chart.")
            return

        # Convert GPS coords to metres offset from true dummy position
        R = 6371000
        true_lat, true_lon = self.actual_gps

        def gps_to_metres(lat, lon):
            north = (lat - true_lat) * (math.pi / 180) * R
            east = (lon - true_lon) * (math.pi / 180) * R * math.cos(math.radians(true_lat))
            return east, north

        def dist(e, n): return math.sqrt(e**2 + n**2)

        c_pts = [gps_to_metres(la, lo) for la, lo in c_data]
        ve_pts = [gps_to_metres(la, lo) for la, lo in v_est]
        vd_pts = [gps_to_metres(la, lo) for la, lo in v_drone]

        c_err = [dist(e, n) for e, n in c_pts]
        ve_err = [dist(e, n) for e, n in ve_pts]
        vd_err = [dist(e, n) for e, n in vd_pts]

        # Print stats
        print("\n=== DUMMY POSITION ESTIMATE ACCURACY ===")
        if c_err:
            print(f"  C — GPS EST (GPS centering):     {min(c_err):.2f}-{max(c_err):.2f}m, "
                  f"avg {sum(c_err)/len(c_err):.2f}m, mean→true {dist(*[sum(x)/len(x) for x in zip(*c_pts)]):.2f}m  ({len(c_err)} samples)")
        if ve_err:
            print(f"  V — GPS EST (vision centering):   {min(ve_err):.2f}-{max(ve_err):.2f}m, "
                  f"avg {sum(ve_err)/len(ve_err):.2f}m, mean→true {dist(*[sum(x)/len(x) for x in zip(*ve_pts)]):.2f}m  ({len(ve_err)} samples)")
        if vd_err:
            print(f"  V — Drone GPS (raw, above dummy): {min(vd_err):.2f}-{max(vd_err):.2f}m, "
                  f"avg {sum(vd_err)/len(vd_err):.2f}m, mean→true {dist(*[sum(x)/len(x) for x in zip(*vd_pts)]):.2f}m  ({len(vd_err)} samples)")

        fig, axes = plt.subplots(1, 2, figsize=(15, 7))
        fig.suptitle("Where Does the System Think the Dummy Is?\n"
                     "(true dummy at centre, each dot = one recorded estimate)",
                     fontsize=12, fontweight="bold")

        # ===== LEFT: Scatter plot =====
        ax1 = axes[0]
        ax1.set_title("Estimated Dummy Positions")
        ax1.set_aspect("equal")

        # Reference circles
        for r in [0.5, 1, 2, 3, 5, 10]:
            circle = patches.Circle((0, 0), r, fill=False, linestyle="--",
                                     color="gray", alpha=0.4, linewidth=0.8)
            ax1.add_patch(circle)
            ax1.text(0.05, r + 0.08, f"{r}m", fontsize=7, color="gray")

        ax1.plot(0, 0, "r*", markersize=20, zorder=10, label="TRUE dummy position")

        max_r = 1

        # Helper to plot a dataset
        def plot_dataset(pts, errors, color, marker, label_prefix, ax):
            nonlocal max_r
            if not pts:
                return
            east = [p[0] for p in pts]
            north = [p[1] for p in pts]
            avg_err = sum(errors) / len(errors)
            ax.scatter(east, north, c=color, alpha=0.35, s=12, zorder=3)
            # Mean position
            me, mn = sum(east)/len(east), sum(north)/len(north)
            mean_dist = dist(me, mn)
            ax.plot(me, mn, marker, color=color, markersize=12, zorder=6,
                    markeredgecolor="black", markeredgewidth=0.5)
            ax.plot([], [], "o", color=color,
                    label=f"{label_prefix}: scatter {min(errors):.2f}-{max(errors):.2f}m, "
                          f"avg {avg_err:.2f}m\n    mean {mean_dist:.2f}m from true ({len(pts)} pts)")
            max_r = max(max_r, max(errors))

        plot_dataset(c_pts, c_err, "dodgerblue", "D",
                     "C: GPS EST (GPS centering)", ax1)
        plot_dataset(ve_pts, ve_err, "limegreen", "D",
                     "V: GPS EST (vision centering)", ax1)
        plot_dataset(vd_pts, vd_err, "orange", "s",
                     "V: Drone GPS (raw, above dummy)", ax1)

        lim = max(max_r * 1.3, 3)
        ax1.set_xlim(-lim, lim)
        ax1.set_ylim(-lim, lim)
        ax1.legend(loc="upper right", fontsize=7)
        ax1.set_xlabel("East (metres)")
        ax1.set_ylabel("North (metres)")
        ax1.grid(True, alpha=0.2)

        # ===== RIGHT: Histogram =====
        ax2 = axes[1]
        ax2.set_title("Error Distance Distribution")

        bins = 25
        if c_err:
            ax2.hist(c_err, bins=bins, alpha=0.4, color="dodgerblue",
                    label=f"C: GPS EST — avg {sum(c_err)/len(c_err):.2f}m", edgecolor="dodgerblue")
        if ve_err:
            ax2.hist(ve_err, bins=bins, alpha=0.4, color="limegreen",
                    label=f"V: GPS EST — avg {sum(ve_err)/len(ve_err):.2f}m", edgecolor="limegreen")
        if vd_err:
            ax2.hist(vd_err, bins=bins, alpha=0.4, color="orange",
                    label=f"V: Drone GPS — avg {sum(vd_err)/len(vd_err):.2f}m", edgecolor="orange")

        # Average lines
        if c_err:
            ax2.axvline(sum(c_err)/len(c_err), color="dodgerblue", linestyle="--", linewidth=2)
        if ve_err:
            ax2.axvline(sum(ve_err)/len(ve_err), color="limegreen", linestyle="--", linewidth=2)
        if vd_err:
            ax2.axvline(sum(vd_err)/len(vd_err), color="orange", linestyle="--", linewidth=2)

        ax2.set_xlabel("Error from True Dummy Position (metres)")
        ax2.set_ylabel("Frequency")
        ax2.legend(loc="upper right", fontsize=8)
        ax2.grid(True, alpha=0.2)

        plt.tight_layout()
        plt.show()

    def _mouse_cb(self, event, x, y, flags, param):
        """Zoom on scroll (simulation only)."""
        if event == cv2.EVENT_MOUSEWHEEL:
            if flags > 0:
                self.zoom_level = min(self.zoom_level * 1.2, 20.0)
            else:
                self.zoom_level = max(self.zoom_level / 1.2, 1.0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simple Simulator — manual flight + CV")
    parser.add_argument("--fps", type=float, default=0,
                        help="Throttle CV to N FPS (e.g. --fps 4 for Pi-like speed). Default: unlimited")
    parser.add_argument("--tflite", action="store_true",
                        help="Force TFLite backend instead of Ultralytics (match Pi inference)")
    parser.add_argument("--gps-drift", type=float, default=0, metavar="METRES",
                        help="Simulate GPS drift (e.g. --gps-drift 3 for +/-3m wander). Default: off")
    parser.add_argument("--shake", type=int, default=0, metavar="PIXELS",
                        help="Simulate camera shake from motor vibration (e.g. --shake 5). Default: off")
    args = parser.parse_args()
    mission = SimpleMission(fps_limit=args.fps, force_tflite=args.tflite, gps_drift=args.gps_drift, shake=args.shake)
    mission.run()
