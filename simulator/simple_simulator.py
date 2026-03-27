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
#   --cluster-dist 15  Min distance between separate clusters (default: 30m)
#
# Stepping stone to main.py — same MAVLink, same CV, same GPS math.
#
from pymavlink import mavutil
import cv2
import numpy as np
import math
import sys
import os
import time
import argparse

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from utils import GeoTransformer
from vision import VisionSystem

if config.MODE == "SIMULATION":
    from simulation import SimulationEnvironment


class SimpleMission:
    def __init__(self, fps_limit=0, force_tflite=False, gps_drift=0.0, shake=0,
                 alt_noise=0.0, yaw_noise=0.0, fov_error=0.0, cluster_dist=30.0,
                 save_detections=False, det_dir="detections"):
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
        if alt_noise > 0:
            print(f"  Altitude noise: +/-{alt_noise:.1f}m (baro/GPS alt jitter)")
        if yaw_noise > 0:
            print(f"  Yaw noise: +/-{yaw_noise:.1f}deg (compass jitter)")
        if fov_error != 0:
            print(f"  FOV calibration error: {fov_error:+.0f}% (systematic bias)")
        if cluster_dist != 30.0:
            print(f"  Cluster distance: {cluster_dist:.0f}m (detections within this = same item)")
        self.save_detections = save_detections
        self.det_dir = det_dir
        self.saved_det_count = 0
        if save_detections:
            import os
            os.makedirs(det_dir, exist_ok=True)
            print(f"  Saving detections to: {det_dir}/")
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

            # Interactive setup: place dummies + draw search area
            targets_list, self.tgt_type, self.search_poly, _ = self.sim.setup_on_map()

            self.eyes = VisionSystem(camera_index=None, model_path="best.tflite")
            if self.eyes.model is not None:
                self.eyes.using_ai = True  # use AI when dummies are placed
            else:
                print("[WARN] AI model not loaded — detection disabled")

            # Multi-target: first target = real dummy (ground truth for landing accuracy)
            self.target_px = targets_list[0] if targets_list else None
            self.all_targets_px = targets_list
            self.actual_gps = self.geo.pixels_to_gps(self.target_px[0], self.target_px[1]) if self.target_px else None
            self.all_target_gps = [self.geo.pixels_to_gps(t[0], t[1]) for t in targets_list]
            if self.actual_gps:
                print(f"Real dummy GPS: {self.actual_gps[0]:.6f}, {self.actual_gps[1]:.6f}")
            print(f"Total targets placed: {len(targets_list)}")
        else:
            self.sim = None
            self.geo = GeoTransformer(map_w_px=4800)
            self.search_poly = []
            self.eyes = VisionSystem(camera_index=config.REAL_CAMERA_INDEX, model_path="best.tflite")
            if self.eyes.model is not None:
                self.eyes.using_ai = True
            else:
                print("[WARN] AI model not loaded — detection disabled")
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
        self.best_gps = None            # best estimate (active cluster's weighted avg)
        self.best_gps_error_m = None    # error of best estimate
        self.gps_error_m = None         # error of latest estimate
        self.detection_count = 0
        self.frame_count = 0
        self.current_conf = 0.0

        # Spatial clustering: separate detection groups
        self.detection_clusters = []    # list of cluster dicts (see _new_cluster)
        self.active_cluster_idx = None  # index into detection_clusters (most recently updated)
        self.CLUSTER_THRESHOLD_M = cluster_dist  # observations within Nm are same cluster
        self.gps_observations = []      # flat list for backward compat (scatter plot etc)
        self.centre_snap = False        # True when target is dead centre
        self.CENTRE_THRESHOLD_PX = 30   # pixels from centre to snap

        # --- Debug: intermediate values from last calculate_target_gps call ---
        self.dbg = {
            'u': 0, 'v': 0, 'dx_px': 0, 'dy_px': 0, 'dist_from_centre': 0,
            'true_alt': 0, 'noisy_alt': 0, 'true_yaw_deg': 0, 'noisy_yaw_deg': 0,
            'gsd_true': 0, 'gsd_noisy': 0, 'fwd_m': 0, 'right_m': 0,
            'offset_n': 0, 'offset_e': 0, 'weight': 0,
            'est_lat': 0, 'est_lon': 0, 'est_err': 0,
            'avg_lat': 0, 'avg_lon': 0, 'avg_err': 0,
            'snap': False, 'n_obs': 0,
        }

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

        # Pixel-to-GPS error sources (affect calculate_target_gps accuracy)
        self.alt_noise = alt_noise        # ±metres noise on altitude reading (baro jitter)
        self.yaw_noise = yaw_noise        # ±degrees noise on heading (compass jitter)
        self.fov_error_pct = fov_error    # % systematic FOV miscalibration (fixed bias)
        # Pre-compute FOV bias (fixed per session — represents miscalibrated camera)
        self.fov_scale = 1.0 + (fov_error / 100.0)  # e.g. 5% error → 1.05x

        # Resolution simulation — lower res = harder to detect + less precise pixel coords
        # 0=640x480 (full), 1=320x240 (half), 2=160x120 (quarter)
        self.resolution_idx = 0
        self.resolution_presets = [
            (config.IMAGE_W, config.IMAGE_H, "640x480"),
            (config.IMAGE_W // 2, config.IMAGE_H // 2, "320x240"),
            (config.IMAGE_W // 4, config.IMAGE_H // 4, "160x120"),
        ]
        self.show_cv_view = False  # toggle with T — show pixelated CV model view

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

        # --- Investigate mode (press N — fly 5m from estimate, descend to 15m) ---
        self.investigating = False
        self.investigate_target = None   # (lat, lon) — 5m offset from estimate
        self.investigate_phase = None    # None, "approaching", "descending", "observing"
        self.investigate_alt = 15.0      # target altitude for observation
        self.investigate_offset_m = 5.0  # stay 5m away from dummy estimate
        self.investigate_obs_start = 0   # observations count at start of investigate
        self.investigate_est_at_start = None  # EST error when N was pressed
        self.investigate_cluster_idx = None   # which cluster we're investigating

        # --- Pilot classification (Y/I/F during investigate observing) ---
        self.logged_items = []             # [{"type": "interest"/"false_pos", "gps": (lat,lon)}, ...]
        self.detection_cluster_count = 0   # total detections in current cluster (resets on classify)

        # --- Offset landing (press L after G lock) ---
        self.landing_offset_m = 7.5   # metres away from dummy to land
        self.landing_target = None     # (lat, lon) — calculated landing coordinate
        self.landing_phase = None      # None, "flying_to", "descending", "landed"
        self.landed_pos = None         # (true_lat, true_lon) — where we actually touched down
        self.landing_est_source = None # "G LOCK" or "GPS EST" — which estimate was used
        self.landing_est_pos = None    # (lat, lon) — the estimated dummy position used for landing

        # --- Altitude test (press H — hover at different altitudes, compare estimates) ---
        self.alt_test_active = False
        self.alt_test_altitudes = [30, 25, 20, 15, 10]  # metres
        self.alt_test_duration = 10  # seconds per altitude
        self.alt_test_step = 0
        self.alt_test_start_time = 0
        self.alt_test_results = []  # [{"alt": m, "n_obs": N, "rolling_err": m, "total_err": m, "kalman_err": m}, ...]
        self.alt_test_obs_start = 0
        self.alt_test_cluster_backup = None  # save cluster state before test

        # --- Display ---
        self.view_w_px = 100
        self.view_h_px = 100
        self.zoom_level = 1.0
        self.show_landing_zone = False  # toggle with trackbar — shows 5-10m donut on scatter
        self.scatter_zoom = 1.0        # scroll zoom for scatter plot (1.0 = default)
        self.scatter_pan_x = 0.0      # pan offset in metres (east)
        self.scatter_pan_y = 0.0      # pan offset in metres (north)
        self.scatter_ref_idx = 0      # which dummy the scatter is centred on (Tab to cycle)
        self._scatter_dragging = False
        self._scatter_drag_start = (0, 0)  # mouse pixel at drag start
        self._scatter_pan_start = (0.0, 0.0)  # pan offset at drag start
        self.scatter_px_per_m = 1.0       # updated each frame by draw_scatter()
        self.grid_split_x = 0         # x boundary between left/right panels (for mouse)
        self.grid_split_y = 0         # y boundary between top/bottom panels (for mouse)

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

    def _new_cluster(self):
        """Create a fresh detection cluster."""
        self._next_cluster_id = getattr(self, '_next_cluster_id', 0) + 1
        return {
            "id": self._next_cluster_id,  # permanent label (never changes)
            "observations": [],   # [(lat, lon, weight), ...] last 50
            "best_gps": None,     # (lat, lon) rolling weighted average (last 50)
            "total_gps": None,    # (lat, lon) running total weighted average (all time)
            "total_wlat": 0.0,   # running sum: lat * weight
            "total_wlon": 0.0,   # running sum: lon * weight
            "total_w": 0.0,      # running sum: weight
            "kalman_gps": None,   # (lat, lon) Kalman filter estimate
            "kalman_P": None,     # 2x2 covariance matrix (uncertainty)
            "detection_count": 0, # number of detections in this cluster
            "error_m": None,      # error vs actual dummy (sim only)
            "total_error_m": None, # error of total average vs actual (sim only)
            "kalman_error_m": None, # error of Kalman estimate vs actual (sim only)
        }

    def _cluster_label(self, cluster_or_idx):
        """Get permanent display label for a cluster (e.g. '#3')."""
        if isinstance(cluster_or_idx, dict):
            return f"#{cluster_or_idx.get('id', '?')}"
        if isinstance(cluster_or_idx, int) and cluster_or_idx < len(self.detection_clusters):
            return f"#{self.detection_clusters[cluster_or_idx].get('id', '?')}"
        return "#?"

    def _route_to_cluster(self, est_lat, est_lon, weight):
        """Add observation to nearest cluster or create a new one.
        Returns the cluster index that was updated."""
        # Find nearest existing cluster
        best_idx = None
        best_dist = float('inf')
        for i, c in enumerate(self.detection_clusters):
            if c["best_gps"]:
                d = self._gps_distance(est_lat, est_lon,
                                       c["best_gps"][0], c["best_gps"][1])
                if d < best_dist:
                    best_dist = d
                    best_idx = i

        # If nearest cluster is within threshold, add to it; else new cluster
        if best_idx is not None and best_dist < self.CLUSTER_THRESHOLD_M:
            cluster = self.detection_clusters[best_idx]
            idx = best_idx
        else:
            cluster = self._new_cluster()
            self.detection_clusters.append(cluster)
            idx = len(self.detection_clusters) - 1
            cid = cluster["id"]
            if best_idx is not None:
                print(f"[CLUSTER] New item #{cid} detected! (nearest was {best_dist:.0f}m away, threshold={self.CLUSTER_THRESHOLD_M}m)")
            else:
                print(f"[CLUSTER] First item #{cid} detected!")

        # Add observation
        cluster["observations"].append((est_lat, est_lon, weight))
        if len(cluster["observations"]) > 50:
            cluster["observations"] = cluster["observations"][-50:]
        cluster["detection_count"] += 1

        # Rolling average (last 50 observations)
        obs = cluster["observations"]
        total_w = sum(w for _, _, w in obs)
        avg_lat = sum(lat * w for lat, _, w in obs) / total_w
        avg_lon = sum(lon * w for _, lon, w in obs) / total_w
        cluster["best_gps"] = (avg_lat, avg_lon)

        # Running total average (all observations ever)
        cluster["total_wlat"] += est_lat * weight
        cluster["total_wlon"] += est_lon * weight
        cluster["total_w"] += weight
        cluster["total_gps"] = (cluster["total_wlat"] / cluster["total_w"],
                                cluster["total_wlon"] / cluster["total_w"])

        # Kalman filter update (static target, varying measurement noise)
        # Measurement noise: high weight = low noise, low weight = high noise
        # R = measurement variance (metres^2, converted to degrees^2)
        R_m2 = (3.0 / max(weight, 0.1)) ** 2  # weight 10 → 0.09m², weight 1 → 9m²
        R_EARTH = 6378137.0
        R_deg2 = (R_m2 / R_EARTH ** 2) * (180 / math.pi) ** 2  # convert m² to deg²
        z = np.array([est_lat, est_lon])  # measurement
        if cluster["kalman_P"] is None:
            # First observation: initialize state to measurement
            cluster["kalman_gps"] = (est_lat, est_lon)
            cluster["kalman_P"] = np.eye(2) * R_deg2 * 4  # start with high uncertainty
        else:
            # Predict: state doesn't change (static target), P grows slightly
            Q_deg2 = (0.1 / R_EARTH) ** 2 * (180 / math.pi) ** 2  # tiny process noise
            x = np.array(cluster["kalman_gps"])
            P = cluster["kalman_P"] + np.eye(2) * Q_deg2
            # Update
            R_mat = np.eye(2) * R_deg2
            S = P + R_mat                     # innovation covariance
            K = P @ np.linalg.inv(S)          # Kalman gain
            x = x + K @ (z - x)              # updated state
            P = (np.eye(2) - K) @ P           # updated covariance
            cluster["kalman_gps"] = (float(x[0]), float(x[1]))
            cluster["kalman_P"] = P

        # Error vs actual dummy (sim only)
        if self.actual_gps:
            cluster["error_m"] = self._gps_distance(
                avg_lat, avg_lon, self.actual_gps[0], self.actual_gps[1])
            cluster["total_error_m"] = self._gps_distance(
                cluster["total_gps"][0], cluster["total_gps"][1],
                self.actual_gps[0], self.actual_gps[1])
            if cluster["kalman_gps"]:
                cluster["kalman_error_m"] = self._gps_distance(
                    cluster["kalman_gps"][0], cluster["kalman_gps"][1],
                    self.actual_gps[0], self.actual_gps[1])

        return idx

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
            # Inverse variance weighting: error ∝ alt, variance ∝ alt², weight ∝ 1/alt²
            alt_factor = (30.0 / max(self.alt, 1.0)) ** 2  # 30m=1x, 15m=4x, 10m=9x
            weight = 10.0 * alt_factor  # centre-snap at 10m → weight 90
            self.centre_snap = True
            # Store debug values for dashboard
            self.dbg.update({
                'u': u, 'v': v, 'dx_px': u - Cx, 'dy_px': v - Cy,
                'dist_from_centre': dist_from_centre, 'snap': True, 'weight': weight,
                'true_alt': self.alt, 'noisy_alt': self.alt,
                'true_yaw_deg': math.degrees(self.yaw), 'noisy_yaw_deg': math.degrees(self.yaw),
                'gsd_true': 0, 'gsd_noisy': 0,
                'fwd_m': 0, 'right_m': 0, 'offset_n': 0, 'offset_e': 0,
            })
        else:
            # Standard pixel-to-GPS math
            # Apply simulated sensor noise (only affects this calculation, not flight)
            import random
            noisy_alt = self.alt
            if self.alt_noise > 0:
                noisy_alt = self.alt + random.gauss(0, self.alt_noise * 0.5)
                noisy_alt = max(0.5, noisy_alt)  # can't go negative
            noisy_yaw = self.yaw
            if self.yaw_noise > 0:
                noisy_yaw = self.yaw + math.radians(random.gauss(0, self.yaw_noise * 0.5))
            # FOV error: systematic bias in sensor/focal length calibration
            effective_sensor_w = config.SENSOR_WIDTH_MM * self.fov_scale

            gsd_m = (effective_sensor_w * noisy_alt) / (config.FOCAL_LENGTH_MM * config.IMAGE_W)
            gsd_true = (config.SENSOR_WIDTH_MM * self.alt) / (config.FOCAL_LENGTH_MM * config.IMAGE_W)
            delta_x_px = u - Cx
            delta_y_px = v - Cy
            fwd_m = -delta_y_px * gsd_m
            right_m = delta_x_px * gsd_m
            offset_n = fwd_m * math.cos(noisy_yaw) - right_m * math.sin(noisy_yaw)
            offset_e = fwd_m * math.sin(noisy_yaw) + right_m * math.cos(noisy_yaw)
            R_EARTH = 6378137.0
            dLat = (offset_n / R_EARTH) * (180 / math.pi)
            dLon = (offset_e / (R_EARTH * math.cos(math.radians(self.lat)))) * (180 / math.pi)
            est_lat = self.lat + dLat
            est_lon = self.lon + dLon
            # Weight: closer to centre = higher weight (max 5 at centre, min 1 at edge)
            max_dist = math.sqrt(Cx**2 + Cy**2)
            centre_weight = 1.0 + 4.0 * (1.0 - dist_from_centre / max_dist)
            # Inverse variance weighting: error ∝ alt, variance ∝ alt², weight ∝ 1/alt²
            alt_factor = (30.0 / max(self.alt, 1.0)) ** 2  # 30m=1x, 15m=4x, 10m=9x
            weight = centre_weight * alt_factor
            self.centre_snap = False
            # Store debug values for dashboard
            self.dbg.update({
                'u': u, 'v': v, 'dx_px': delta_x_px, 'dy_px': delta_y_px,
                'dist_from_centre': dist_from_centre, 'snap': False, 'weight': weight,
                'true_alt': self.alt, 'noisy_alt': noisy_alt,
                'true_yaw_deg': math.degrees(self.yaw),
                'noisy_yaw_deg': math.degrees(noisy_yaw),
                'gsd_true': gsd_true, 'gsd_noisy': gsd_m,
                'fwd_m': fwd_m, 'right_m': right_m,
                'offset_n': offset_n, 'offset_e': offset_e,
            })

        self.estimated_gps = (est_lat, est_lon)

        # During investigate: force observations to the investigated cluster
        # (skip distance routing — we KNOW which item we're looking at)
        if (self.investigating and self.investigate_cluster_idx is not None
                and self.investigate_cluster_idx < len(self.detection_clusters)):
            idx = self.investigate_cluster_idx
            cluster = self.detection_clusters[idx]
            cluster["observations"].append((est_lat, est_lon, weight))
            if len(cluster["observations"]) > 50:
                cluster["observations"] = cluster["observations"][-50:]
            cluster["detection_count"] += 1
            # Rolling average (last 50)
            obs = cluster["observations"]
            total_w = sum(w for _, _, w in obs)
            avg_lat = sum(lat * w for lat, _, w in obs) / total_w
            avg_lon = sum(lon * w for _, lon, w in obs) / total_w
            cluster["best_gps"] = (avg_lat, avg_lon)
            # Running total average (all time)
            cluster["total_wlat"] += est_lat * weight
            cluster["total_wlon"] += est_lon * weight
            cluster["total_w"] += weight
            cluster["total_gps"] = (cluster["total_wlat"] / cluster["total_w"],
                                    cluster["total_wlon"] / cluster["total_w"])
            # Kalman filter update
            R_m2 = (3.0 / max(weight, 0.1)) ** 2
            R_EARTH = 6378137.0
            R_deg2 = (R_m2 / R_EARTH ** 2) * (180 / math.pi) ** 2
            z = np.array([est_lat, est_lon])
            if cluster["kalman_P"] is None:
                cluster["kalman_gps"] = (est_lat, est_lon)
                cluster["kalman_P"] = np.eye(2) * R_deg2 * 4
            else:
                Q_deg2 = (0.1 / R_EARTH) ** 2 * (180 / math.pi) ** 2
                x = np.array(cluster["kalman_gps"])
                P = cluster["kalman_P"] + np.eye(2) * Q_deg2
                R_mat = np.eye(2) * R_deg2
                S = P + R_mat
                K = P @ np.linalg.inv(S)
                x = x + K @ (z - x)
                P = (np.eye(2) - K) @ P
                cluster["kalman_gps"] = (float(x[0]), float(x[1]))
                cluster["kalman_P"] = P
            if self.actual_gps:
                cluster["error_m"] = self._gps_distance(
                    avg_lat, avg_lon, self.actual_gps[0], self.actual_gps[1])
                cluster["total_error_m"] = self._gps_distance(
                    cluster["total_gps"][0], cluster["total_gps"][1],
                    self.actual_gps[0], self.actual_gps[1])
                if cluster["kalman_gps"]:
                    cluster["kalman_error_m"] = self._gps_distance(
                        cluster["kalman_gps"][0], cluster["kalman_gps"][1],
                        self.actual_gps[0], self.actual_gps[1])
        else:
            # Normal flight: route to nearest cluster or create new
            idx = self._route_to_cluster(est_lat, est_lon, weight)
        self.active_cluster_idx = idx
        cluster = self.detection_clusters[idx]

        # Keep flat list for scatter backward compat
        self.gps_observations.append((est_lat, est_lon, weight))
        if len(self.gps_observations) > 50:
            self.gps_observations = self.gps_observations[-50:]

        # best_gps = active cluster's weighted average
        avg_lat, avg_lon = cluster["best_gps"]
        self.best_gps = cluster["best_gps"]
        self.best_gps_error_m = cluster.get("error_m")

        # Calculate errors if we know ground truth
        if self.actual_gps:
            self.gps_error_m = self._gps_distance(
                est_lat, est_lon, self.actual_gps[0], self.actual_gps[1])

        # Store final debug values
        self.dbg.update({
            'est_lat': est_lat, 'est_lon': est_lon,
            'est_err': self.gps_error_m or 0,
            'avg_lat': avg_lat, 'avg_lon': avg_lon,
            'avg_err': self.best_gps_error_m or 0,
            'n_obs': len(self.gps_observations),
        })

        return est_lat, est_lon

    def _start_investigate(self, cluster_idx):
        """Start investigating a specific cluster by index."""
        cluster = self.detection_clusters[cluster_idx]
        # Use total average (best estimate), fall back to rolling 50
        target = cluster.get("total_gps") or cluster.get("best_gps")
        if not target:
            print(f"[INVESTIGATE] Cluster {self._cluster_label(cluster_idx)} has no position yet")
            return
        self._start_investigate_gps(target, cluster_idx)

    def _start_investigate_gps(self, gps, cluster_idx=None):
        """Start investigation at a GPS position."""
        est_lat, est_lon = gps
        self.investigating = True
        self.investigate_target = (est_lat, est_lon)
        self.investigate_phase = "approaching"
        self.investigate_obs_start = len(self.gps_observations)
        self.investigate_est_at_start = self.best_gps_error_m
        self.investigate_cluster_idx = cluster_idx
        self.centering = False
        self.visual_servo = False
        # Set best_gps to this cluster's estimate
        if cluster_idx is not None:
            self.active_cluster_idx = cluster_idx
            self.best_gps = self.detection_clusters[cluster_idx]["best_gps"]
        label = f"item {self._cluster_label(cluster_idx)}" if cluster_idx is not None else "estimate"
        n_det = self.detection_clusters[cluster_idx]["detection_count"] if cluster_idx is not None else "?"
        print(f"\n[INVESTIGATE] Flying to {label} ({n_det} detections)")
        print(f"[INVESTIGATE] Descend to {self.investigate_alt:.0f}m for closer look")
        print(f"[INVESTIGATE] N to cancel, WASD to override, 1-9 to switch item")

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

        # Resolution simulation: downscale frame before vision model
        # Lower res = fewer pixels for model to work with = harder to detect from altitude
        # Toggle T to see pixelated CV model view vs crisp full-res view
        res_w, res_h = config.IMAGE_W, config.IMAGE_H
        if self.resolution_idx > 0 and self.resolution_idx < len(self.resolution_presets):
            res_w, res_h, _ = self.resolution_presets[self.resolution_idx]
            det_frame = cv2.resize(frame, (res_w, res_h))
        else:
            det_frame = frame

        found, u, v, conf = self.eyes.process_frame_manually(det_frame)

        # Scale detection coords back to full-res for HUD
        if res_w != config.IMAGE_W:
            scale_x = config.IMAGE_W / res_w
            scale_y = config.IMAGE_H / res_h
            u = int(u * scale_x)
            v = int(v * scale_y)
            # T toggle: show pixelated CV view or crisp original
            if self.show_cv_view:
                frame = cv2.resize(det_frame, (config.IMAGE_W, config.IMAGE_H),
                                   interpolation=cv2.INTER_NEAREST)
            # Re-draw bounding box on display frame (model drew on det_frame which we discard)
            if found and hasattr(self.eyes, 'last_bbox_w'):
                bw = int(self.eyes.last_bbox_w * scale_x)
                bh = int(self.eyes.last_bbox_h * scale_y)
                x1, y1 = u - bw // 2, v - bh // 2
                x2, y2 = u + bw // 2, v + bh // 2
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"AI {conf:.2f}", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        self.current_conf = conf
        self._last_detection = (found, u, v, conf)
        return frame, found, u, v, conf

    def draw_hud(self, frame, found, u, v, conf):
        """Draw HUD overlay on camera frame."""
        cx, cy = config.IMAGE_W // 2, config.IMAGE_H // 2

        # Crosshair
        cv2.line(frame, (cx - 20, cy), (cx + 20, cy), (0, 255, 255), 2)
        cv2.line(frame, (cx, cy - 20), (cx, cy + 20), (0, 255, 255), 2)

        # Detection marker (current frame detection — green)
        if found:
            cv2.circle(frame, (u, v), 15, (0, 255, 0), 2)
            cv2.line(frame, (u, v), (cx, cy), (0, 255, 0), 2)
            cv2.putText(frame, f"TGT {conf:.2f}", (u + 10, v),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 3)

        # Projected GPS estimate marker on camera view (magenta diamond)
        # Shows where the system THINKS the dummy is, projected into camera space
        if self.best_gps and self.alt > 0.5 and config.MODE == "SIMULATION":
            # GPS estimate → map pixels
            est_mx, est_my = self.geo.gps_to_pixels(self.best_gps[0], self.best_gps[1])
            # Drone TRUE position → map pixels
            drn_mx, drn_my = self.geo.gps_to_pixels(self.true_lat, self.true_lon)
            # Offset in map pixels
            dx_map = est_mx - drn_mx
            dy_map = est_my - drn_my
            # Rotate by -yaw (camera is rotated relative to map)
            cos_y = math.cos(-self.yaw)
            sin_y = math.sin(-self.yaw)
            dx_rot = dx_map * cos_y - dy_map * sin_y
            dy_rot = dx_map * sin_y + dy_map * cos_y
            # Scale: map pixels → camera pixels
            fov = 2 * math.atan(config.SENSOR_WIDTH_MM / (2 * config.FOCAL_LENGTH_MM))
            ground_w = 2 * self.alt * math.tan(fov / 2)
            view_w_map = ground_w * self.geo.pix_per_m
            scale = config.IMAGE_W / view_w_map if view_w_map > 0 else 1
            cam_x = int(cx + dx_rot * scale)
            cam_y = int(cy + dy_rot * scale)
            # Draw if within frame (with margin)
            if -50 < cam_x < config.IMAGE_W + 50 and -50 < cam_y < config.IMAGE_H + 50:
                # Diamond shape
                sz = 10
                pts = np.array([(cam_x, cam_y - sz), (cam_x + sz, cam_y),
                                (cam_x, cam_y + sz), (cam_x - sz, cam_y)], np.int32)
                cv2.polylines(frame, [pts], True, (255, 0, 255), 2)
                cv2.putText(frame, "EST", (cam_x + 12, cam_y - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 255), 2)

        # Projected ACTUAL dummy position on camera view (orange dot — sim only)
        if self.actual_gps and self.alt > 0.5 and config.MODE == "SIMULATION":
            act_mx, act_my = self.geo.gps_to_pixels(self.actual_gps[0], self.actual_gps[1])
            drn_mx2, drn_my2 = self.geo.gps_to_pixels(self.true_lat, self.true_lon)
            dx_map = act_mx - drn_mx2
            dy_map = act_my - drn_my2
            cos_y = math.cos(-self.yaw)
            sin_y = math.sin(-self.yaw)
            dx_rot = dx_map * cos_y - dy_map * sin_y
            dy_rot = dx_map * sin_y + dy_map * cos_y
            fov = 2 * math.atan(config.SENSOR_WIDTH_MM / (2 * config.FOCAL_LENGTH_MM))
            ground_w = 2 * self.alt * math.tan(fov / 2)
            view_w_map = ground_w * self.geo.pix_per_m
            scale = config.IMAGE_W / view_w_map if view_w_map > 0 else 1
            act_cx = int(cx + dx_rot * scale)
            act_cy = int(cy + dy_rot * scale)
            if -50 < act_cx < config.IMAGE_W + 50 and -50 < act_cy < config.IMAGE_H + 50:
                cv2.circle(frame, (act_cx, act_cy), 8, (0, 128, 255), -1)  # filled orange
                cv2.circle(frame, (act_cx, act_cy), 12, (0, 128, 255), 2)  # orange ring
                cv2.putText(frame, "ACTUAL", (act_cx + 14, act_cy - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 128, 255), 2)

        # Info panel
        armed_str = "ARMED" if self.armed else "DISARMED"
        armed_color = (0, 0, 255) if self.armed else (100, 100, 100)
        cv2.putText(frame, armed_str, (config.IMAGE_W - 130, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, armed_color, 3)
        cv2.putText(frame, f"MODE: {config.MODE}", (10, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 3)
        cv2.putText(frame, f"ALT: {self.alt:.1f}m  SPD: {self.groundspeed:.1f}m/s  YAW: {math.degrees(self.yaw):.0f}",
                    (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 0), 2)
        n_clusters = len(self.detection_clusters)
        det_txt = f"Detections: {self.detection_count}/{self.frame_count}"
        if n_clusters > 0:
            det_txt += f"  Items: {n_clusters}"
            if self.active_cluster_idx is not None and self.active_cluster_idx < n_clusters:
                ac = self.detection_clusters[self.active_cluster_idx]
                det_txt += f"  ({self._cluster_label(self.active_cluster_idx)}: {ac['detection_count']}hits)"
        cv2.putText(frame, det_txt,
                    (10, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)
        # Show cluster list hint when multiple items detected
        if n_clusters > 1 and not self.investigating:
            ids = [str(cl.get("id", i+1)) for i, cl in enumerate(self.detection_clusters[:9])]
            hint = "Items " + ",".join(ids) + " | Keys 1-" + str(min(n_clusters, 9)) + " to investigate"
            cv2.putText(frame, hint, (10, 95),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)

        # CV model view indicator
        if self.show_cv_view and self.resolution_idx > 0:
            rw, rh, rn = self.resolution_presets[self.resolution_idx]
            cv2.putText(frame, f"CV VIEW [{rn}]", (config.IMAGE_W // 2 - 80, 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

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
        elif self.investigating:
            phase_str = self.investigate_phase.upper() if self.investigate_phase else "?"
            ci = self.investigate_cluster_idx
            ci_label = self._cluster_label(ci) if ci is not None else ""
            new_obs = len(self.gps_observations) - self.investigate_obs_start
            ci_det = self.detection_clusters[ci]["detection_count"] if ci is not None and ci < len(self.detection_clusters) else 0
            cv2.putText(frame, f"INVESTIGATE {ci_label}: {phase_str}", (config.IMAGE_W - 320, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 255), 3)
            cv2.putText(frame, f"+{new_obs} obs  {ci_det} hits",
                        (config.IMAGE_W - 200, 75),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 200, 255), 2)
            if self.investigate_phase == "observing":
                cv2.putText(frame, "Y=dummy  I=interest  X=false pos", (10, config.IMAGE_H - 15),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 2)

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

        # Logged items summary
        if self.logged_items:
            n_ioi = sum(1 for x in self.logged_items if x["type"] == "interest")
            n_fp = sum(1 for x in self.logged_items if x["type"] == "false_pos")
            parts = []
            if n_ioi: parts.append(f"{n_ioi} IOI")
            if n_fp: parts.append(f"{n_fp} FP")
            cv2.putText(frame, f"Logged: {', '.join(parts)}", (10, config.IMAGE_H - 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 0), 2)

        # Controls hint at bottom
        cv2.putText(frame, "SPC:arm WASD:fly QE:yaw RF:alt N:investigate C:gps V:vis L:land T:cv-view",
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

        # GPS-only estimate (weighted avg from flyover detections — magenta, matches EST diamond)
        if self.best_gps:
            cv2.putText(frame, f"GPS EST:   {self.best_gps[0]:.6f}, {self.best_gps[1]:.6f}",
                        (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)
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
                src = getattr(self, 'landing_est_source', '?')
                cv2.putText(frame, f"LANDING [{src}]: Flying to 7.5m offset...",
                            (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 200, 255), 2)
            elif self.landing_phase == "descending":
                cv2.putText(frame, "LANDING: Descending...",
                            (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 200, 255), 2)
            elif self.landing_phase == "landed" and self.landed_pos and self.actual_gps:
                src = getattr(self, 'landing_est_source', '?')
                # 1. Actual dummy vs estimated dummy
                est_pos = getattr(self, 'landing_est_pos', None)
                est_err = 0
                if est_pos:
                    est_err = self._gps_distance(est_pos[0], est_pos[1],
                                                  self.actual_gps[0], self.actual_gps[1])
                # 2. Landing target vs where we actually landed
                nav_err = 0
                if self.landing_target:
                    nav_err = self._gps_distance(self.landed_pos[0], self.landed_pos[1],
                                                  self.landing_target[0], self.landing_target[1])
                # 3. Where we landed vs actual dummy
                landed_to_dummy = self._gps_distance(
                    self.landed_pos[0], self.landed_pos[1],
                    self.actual_gps[0], self.actual_gps[1])
                cv2.putText(frame, f"--- LANDED [{src}] ---", (10, y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                y += 18
                # Estimate error
                e_col = (0, 255, 0) if est_err < 3 else (0, 128, 255) if est_err < 5 else (0, 0, 255)
                cv2.putText(frame, f"Est vs Actual dummy: {est_err:.2f}m",
                            (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.45, e_col, 2)
                y += 16
                # Navigation error
                n_col = (0, 255, 0) if nav_err < 2 else (0, 128, 255) if nav_err < 4 else (0, 0, 255)
                cv2.putText(frame, f"Target vs Actual landing: {nav_err:.2f}m",
                            (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.45, n_col, 2)
                y += 16
                # Final distance
                in_zone = 5 <= landed_to_dummy <= 10
                d_col = (0, 255, 0) if in_zone else (0, 0, 255)
                cv2.putText(frame, f"Landed {landed_to_dummy:.1f}m from dummy (target: {self.landing_offset_m}m)",
                            (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.45, d_col, 2)
            y += 20

        # ========== SIM FLAGS (left side) ==========
        flags_y = y
        if self.shake_px > 0:
            fov = 2 * math.atan(config.SENSOR_WIDTH_MM / (2 * config.FOCAL_LENGTH_MM))
            safe_alt = max(1.0, self.alt)
            gsd = (2 * safe_alt * math.tan(fov / 2)) / config.IMAGE_W
            ground_cm = self.shake_px * gsd * 100
            cv2.putText(frame, f"SHAKE: {self.shake_px}px = {ground_cm:.0f}cm on ground",
                        (10, flags_y), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)
            flags_y += 18
        if self.alt_noise > 0:
            cv2.putText(frame, f"ALT NOISE: +/-{self.alt_noise:.1f}m",
                        (10, flags_y), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)
            flags_y += 18
        if self.yaw_noise > 0:
            cv2.putText(frame, f"YAW NOISE: +/-{self.yaw_noise:.1f}deg",
                        (10, flags_y), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)
            flags_y += 18
        if self.fov_error_pct != 0:
            cv2.putText(frame, f"FOV ERROR: {self.fov_error_pct:+.0f}%",
                        (10, flags_y), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)
            flags_y += 18
        if self.resolution_idx > 0:
            res_w, res_h, res_name = self.resolution_presets[self.resolution_idx]
            cv2.putText(frame, f"RES: {res_name} (model sees {res_w}x{res_h})",
                        (10, flags_y), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)

        return frame

    def draw_dashboard(self):
        """Draw the error analysis dashboard — shows pixel-to-GPS pipeline with live values."""
        W, H = 700, 480
        dash = np.zeros((H, W, 3), dtype=np.uint8)
        d = self.dbg
        white = (255, 255, 255)
        grey = (150, 150, 150)
        green = (0, 255, 0)
        red = (0, 0, 255)
        cyan = (255, 255, 0)
        magenta = (255, 0, 255)
        orange = (0, 128, 255)
        y = 25

        def txt(text, x, yy, color=white, scale=0.45, thick=1):
            cv2.putText(dash, text, (x, yy), cv2.FONT_HERSHEY_SIMPLEX, scale, color, thick)

        def line():
            nonlocal y
            y += 3
            cv2.line(dash, (10, y), (W - 10, y), (60, 60, 60), 1)
            y += 12

        # Title
        txt("PIXEL-TO-GPS ESTIMATION PIPELINE", 10, y, cyan, 0.55, 2)
        y += 25

        # Step 1: CV detection
        txt("1. CV DETECTION", 10, y, green, 0.45, 2)
        if self.resolution_idx > 0:
            rw, rh, rn = self.resolution_presets[self.resolution_idx]
            txt(f"[{rn}]", 200, y, red, 0.4)
        y += 20
        txt(f"   pixel: ({d['u']}, {d['v']})   offset: ({d['dx_px']:.0f}, {d['dy_px']:.0f}) px", 10, y)
        y += 18
        txt(f"   dist from centre: {d['dist_from_centre']:.0f} px", 10, y)
        if d['snap']:
            txt("SNAP — using drone GPS directly", 250, y, cyan, 0.4)
        y += 5
        line()

        # Step 2: Altitude
        txt("2. ALTITUDE", 10, y, green, 0.45, 2)
        y += 20
        alt_diff = abs(d['noisy_alt'] - d['true_alt'])
        alt_color = red if alt_diff > 0.3 else white
        txt(f"   true: {d['true_alt']:.1f}m", 10, y)
        txt(f"   used: {d['noisy_alt']:.1f}m", 200, y, alt_color)
        if alt_diff > 0.01:
            txt(f"(+/-{alt_diff:.1f}m noise)", 350, y, red, 0.35)
        y += 5
        line()

        # Step 3: GSD
        txt("3. GSD (ground sample distance)", 10, y, green, 0.45, 2)
        y += 20
        txt(f"   GSD = sensor_w x alt / (focal x W)", 10, y, grey, 0.38)
        y += 18
        if not d['snap']:
            gsd_diff = abs(d['gsd_noisy'] - d['gsd_true'])
            gsd_color = red if gsd_diff > 0.001 else white
            txt(f"   true: {d['gsd_true']*100:.2f} cm/px", 10, y)
            txt(f"   used: {d['gsd_noisy']*100:.2f} cm/px", 200, y, gsd_color)
            if self.fov_error_pct != 0:
                txt(f"(FOV {self.fov_error_pct:+.0f}%)", 380, y, red, 0.35)
        else:
            txt("   (skipped — centre snap)", 10, y, cyan)
        y += 5
        line()

        # Step 4: Ground offset
        txt("4. GROUND OFFSET (metres)", 10, y, green, 0.45, 2)
        y += 20
        if not d['snap']:
            txt(f"   fwd:  {d['fwd_m']:+.2f}m   right: {d['right_m']:+.2f}m", 10, y)
        else:
            txt("   (skipped — centre snap)", 10, y, cyan)
        y += 5
        line()

        # Step 5: Yaw rotation
        txt("5. YAW ROTATION", 10, y, green, 0.45, 2)
        y += 20
        yaw_diff = abs(d['noisy_yaw_deg'] - d['true_yaw_deg'])
        yaw_color = red if yaw_diff > 0.5 else white
        txt(f"   true: {d['true_yaw_deg']:.1f}deg", 10, y)
        txt(f"   used: {d['noisy_yaw_deg']:.1f}deg", 200, y, yaw_color)
        if yaw_diff > 0.01:
            txt(f"(+/-{yaw_diff:.1f}deg noise)", 350, y, red, 0.35)
        y += 18
        if not d['snap']:
            txt(f"   north: {d['offset_n']:+.2f}m   east: {d['offset_e']:+.2f}m", 10, y)
        y += 5
        line()

        # Step 6: Drone GPS
        txt("6. DRONE GPS (reference point)", 10, y, green, 0.45, 2)
        y += 20
        txt(f"   {self.lat:.6f}, {self.lon:.6f}", 10, y)
        if self.gps_drift_max > 0:
            drift_m = math.sqrt(self.drift_north**2 + self.drift_east**2)
            txt(f"drift: {drift_m:.1f}m", 300, y, red, 0.4)
        y += 5
        line()

        # Step 7: This estimate
        txt("7. THIS ESTIMATE (single observation)", 10, y, orange, 0.45, 2)
        y += 20
        err_color = green if d['est_err'] < 2 else (orange if d['est_err'] < 5 else red)
        txt(f"   {d['est_lat']:.6f}, {d['est_lon']:.6f}", 10, y)
        txt(f"err: {d['est_err']:.2f}m", 300, y, err_color)
        txt(f"wt: {d['weight']:.0f}", 420, y, grey, 0.35)
        y += 5
        line()

        # Step 8: Averaged estimate
        txt("8. AVERAGED (weighted, last 50 obs)", 10, y, magenta, 0.45, 2)
        y += 20
        avg_color = green if d['avg_err'] < 2 else (orange if d['avg_err'] < 5 else red)
        txt(f"   {d['avg_lat']:.6f}, {d['avg_lon']:.6f}", 10, y)
        txt(f"err: {d['avg_err']:.2f}m", 300, y, avg_color)
        txt(f"({d['n_obs']} obs)", 420, y, grey, 0.35)
        y += 20

        # Improvement indicator
        if d['est_err'] > 0 and d['avg_err'] > 0:
            improvement = d['est_err'] - d['avg_err']
            if improvement > 0:
                txt(f"   Averaging reduces error by {improvement:.2f}m", 10, y, green, 0.4)
            else:
                txt(f"   Averaging adds {-improvement:.2f}m (old obs pulling avg)", 10, y, red, 0.4)
        y += 25

        # Slider values display
        cv2.line(dash, (10, y - 5), (W - 10, y - 5), (100, 100, 100), 1)
        txt("INTERACTIVE ERROR CONTROLS (use sliders above)", 10, y + 5, cyan, 0.4, 1)

        return dash

    def draw_scatter(self):
        """Draw live zoomed scatter: EST positions orbiting around ACTUAL (orange = origin).
        Optionally shows landing donut (5-10m zone, 7.5m target).
        Scroll to zoom in/out (when mouse is over scatter panel)."""
        S = 400  # square size
        scat = np.zeros((S, S, 3), dtype=np.uint8)
        cx, cy = S // 2, S // 2
        # Base scale: wider when landing zone visible, then apply scroll zoom
        base_scale = 12.0 if self.show_landing_zone else 5.0
        scale_m = base_scale / self.scatter_zoom  # zoom in = smaller scale = more detail
        px_per_m = (S / 2) / scale_m
        self.scatter_px_per_m = px_per_m  # store for mouse drag → metres conversion

        # Pan offset: shift the view centre (metres from ACTUAL dummy)
        pan_east = self.scatter_pan_x   # metres east of dummy = view centre
        pan_north = self.scatter_pan_y  # metres north of dummy = view centre

        # Helper: convert metres-from-dummy to scatter pixel
        def m_to_px(east_m, north_m):
            sx = int(cx + (east_m - pan_east) * px_per_m)
            sy = int(cy - (north_m - pan_north) * px_per_m)
            return sx, sy

        # Origin = ACTUAL dummy position — grid is anchored here
        ox, oy = m_to_px(0, 0)

        # Grid lines — centred on actual dummy, adaptive spacing based on zoom
        if scale_m <= 3:
            grid_step = 0.5
        elif scale_m <= 8:
            grid_step = 1
        else:
            grid_step = 2
        r = grid_step
        while r <= scale_m * 2:  # draw wider so grid visible when panned
            rpx = int(r * px_per_m)
            cv2.circle(scat, (ox, oy), rpx, (40, 40, 40), 1)
            r += grid_step
        cv2.line(scat, (ox, 0), (ox, S), (40, 40, 40), 1)
        cv2.line(scat, (0, oy), (S, oy), (40, 40, 40), 1)

        # Scale labels — anchored to origin
        label_vals = []
        r = grid_step
        while r <= scale_m * 2:
            label_vals.append(r)
            r += grid_step
        for r in label_vals[-4:]:  # show last 4 labels to avoid clutter
            rpx = int(r * px_per_m)
            label = f"{r:.0f}m" if r == int(r) else f"{r:.1f}m"
            cv2.putText(scat, label, (ox + 3, oy - rpx + 12),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.3, (80, 80, 80), 1)

        # Origin marker (orange dot + label showing which dummy)
        if 0 <= ox < S and 0 <= oy < S:
            cv2.circle(scat, (ox, oy), 6, (0, 128, 255), -1)
            n_dummies = len(self.all_target_gps) if hasattr(self, 'all_target_gps') else 1
            ref_idx = min(self.scatter_ref_idx, n_dummies - 1) if n_dummies > 1 else 0
            ref_label = f"DUMMY #{ref_idx+1}/{n_dummies}" if n_dummies > 1 else "ACTUAL"
            cv2.putText(scat, ref_label, (ox + 10, oy - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 128, 255), 1)

        # Landing donut: 5-10m zone with 7.5m target (centred on ACTUAL)
        if self.show_landing_zone:
            r_inner = int(5.0 * px_per_m)
            r_outer = int(10.0 * px_per_m)
            r_target = int(7.5 * px_per_m)
            if r_inner < S * 2:
                overlay = scat.copy()
                cv2.circle(overlay, (ox, oy), r_outer, (0, 40, 0), -1)
                cv2.circle(overlay, (ox, oy), r_inner, (0, 0, 0), -1)
                cv2.addWeighted(overlay, 0.4, scat, 0.6, 0, scat)
                self._draw_dashed_circle(scat, (ox, oy), r_inner, (100, 100, 100), 1)
                cv2.putText(scat, "5m min", (ox + r_inner + 3, oy - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.3, (100, 100, 100), 1)
                self._draw_dashed_circle(scat, (ox, oy), r_outer, (100, 100, 100), 1)
                cv2.putText(scat, "10m max", (ox + r_outer + 3, oy - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.3, (100, 100, 100), 1)
                self._draw_dashed_circle(scat, (ox, oy), r_target, (255, 255, 0), 2)
                cv2.putText(scat, "7.5m target", (ox + r_target + 3, oy + 12),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 0), 1)

        # Reference dummy: cycle with Tab key (scatter_ref_idx)
        ref_gps = None
        if hasattr(self, 'all_target_gps') and self.all_target_gps:
            idx = min(self.scatter_ref_idx, len(self.all_target_gps) - 1)
            ref_gps = self.all_target_gps[idx]
        elif self.actual_gps:
            ref_gps = self.actual_gps

        if not ref_gps:
            return scat

        R = 6371000
        true_lat, true_lon = ref_gps

        def gps_to_scatter(lat, lon):
            north = (lat - true_lat) * (math.pi / 180) * R
            east = (lon - true_lon) * (math.pi / 180) * R * math.cos(math.radians(true_lat))
            return m_to_px(east, north)

        # Plot ALL dummy positions (small markers — shows spatial layout)
        if hasattr(self, 'all_target_gps') and len(self.all_target_gps) > 1:
            for di, dgps in enumerate(self.all_target_gps):
                dx, dy = gps_to_scatter(dgps[0], dgps[1])
                if 0 <= dx < S and 0 <= dy < S:
                    is_ref = (di == min(self.scatter_ref_idx, len(self.all_target_gps) - 1))
                    if not is_ref:  # ref already drawn as origin
                        cv2.circle(scat, (dx, dy), 4, (0, 80, 160), -1)
                        cv2.putText(scat, f"D{di+1}", (dx + 6, dy - 3),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 80, 160), 1)

        # Plot recent individual observations (small dots, fade with age)
        # Green = flyby (weight 1-5), Cyan = centre-snap (weight 10)
        n = len(self.gps_observations)
        for i, (lat, lon, w) in enumerate(self.gps_observations):
            age = (n - i) / max(n, 1)
            alpha = int(80 + 175 * (1 - age))  # newer = brighter
            sx, sy = gps_to_scatter(lat, lon)
            if 0 <= sx < S and 0 <= sy < S:
                if w >= 10:
                    color = (alpha, alpha, 0)  # cyan = centre-snap (high weight)
                else:
                    color = (0, alpha, 0)      # green = flyby observation
                cv2.circle(scat, (sx, sy), 2, color, -1)

        # Plot cluster estimates (numbered diamonds)
        cluster_colors = [(255, 0, 255), (0, 200, 255), (255, 200, 0),
                          (0, 255, 200), (200, 0, 255), (255, 100, 100)]
        for ci, cl in enumerate(self.detection_clusters):
            if cl["best_gps"]:
                ex, ey = gps_to_scatter(cl["best_gps"][0], cl["best_gps"][1])
                if 0 <= ex < S and 0 <= ey < S:
                    sz = 8
                    color = cluster_colors[ci % len(cluster_colors)]
                    pts = np.array([(ex, ey - sz), (ex + sz, ey),
                                    (ex, ey + sz), (ex - sz, ey)], np.int32)
                    cv2.fillPoly(scat, [pts], color)
                    cid = cl.get("id", ci+1)
                    label = f"#{cid} ({cl['detection_count']})"
                    cv2.putText(scat, label, (ex + 10, ey - 3),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.35, color, 1)
                # Total average (small square, same color)
                if cl.get("total_gps"):
                    tx, ty = gps_to_scatter(cl["total_gps"][0], cl["total_gps"][1])
                    if 0 <= tx < S and 0 <= ty < S:
                        color = cluster_colors[ci % len(cluster_colors)]
                        cv2.rectangle(scat, (tx-4, ty-4), (tx+4, ty+4), color, 2)
                        cv2.putText(scat, "T", (tx + 6, ty + 4),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.3, color, 1)
                # Kalman filter (triangle, same color)
                if cl.get("kalman_gps"):
                    kx, ky = gps_to_scatter(cl["kalman_gps"][0], cl["kalman_gps"][1])
                    if 0 <= kx < S and 0 <= ky < S:
                        color = cluster_colors[ci % len(cluster_colors)]
                        tri = np.array([(kx, ky-5), (kx+4, ky+3), (kx-4, ky+3)], np.int32)
                        cv2.fillPoly(scat, [tri], color)
                        cv2.putText(scat, "K", (kx + 6, ky + 3),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.3, color, 1)

        # Plot G LOCK estimate (yellow star — 30s averaged GPS, most precise)
        if self.locked_gps:
            gx, gy = gps_to_scatter(self.locked_gps[0], self.locked_gps[1])
            if 0 <= gx < S and 0 <= gy < S:
                # Star shape
                sz = 10
                for angle_deg in range(0, 360, 72):
                    a1 = math.radians(angle_deg - 90)
                    a2 = math.radians(angle_deg - 90 + 36)
                    p1 = (int(gx + sz * math.cos(a1)), int(gy + sz * math.sin(a1)))
                    p2 = (int(gx + sz * 0.4 * math.cos(a2)), int(gy + sz * 0.4 * math.sin(a2)))
                    cv2.line(scat, p1, p2, (0, 255, 255), 2)
                cv2.putText(scat, "G LOCK", (gx + 12, gy - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)
                if self.locked_error_gps is not None:
                    cv2.putText(scat, f"{self.locked_error_gps:.2f}m", (gx + 12, gy + 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 255, 255), 1)

        # Plot drone position (blue)
        dsx, dsy = gps_to_scatter(self.true_lat, self.true_lon)
        if 0 <= dsx < S and 0 <= dsy < S:
            cv2.circle(scat, (dsx, dsy), 4, (255, 0, 0), -1)

        # Landing preview — where L WOULD land based on current best estimate
        # Shows as a hollow pink circle (preview) when not yet pressed L
        # Shows as solid pink X when L has been pressed (landing_target set)
        if self.landing_target:
            # L was pressed — show actual landing target (solid pink X)
            lx, ly = gps_to_scatter(self.landing_target[0], self.landing_target[1])
            if 0 <= lx < S and 0 <= ly < S:
                sz = 6
                cv2.line(scat, (lx - sz, ly - sz), (lx + sz, ly + sz), (180, 0, 255), 2)
                cv2.line(scat, (lx - sz, ly + sz), (lx + sz, ly - sz), (180, 0, 255), 2)
                cv2.putText(scat, "LAND", (lx + 8, ly - 3),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.35, (180, 0, 255), 1)
        elif self.show_landing_zone and self.landing_phase is None:
            # Preview: where L would land (7.5m north of best estimate)
            # Use total average from active cluster for landing preview
            est = self.locked_gps
            if not est:
                ci = self.active_cluster_idx
                if ci is not None and ci < len(self.detection_clusters):
                    est = self.detection_clusters[ci].get("total_gps")
            if not est:
                est = self.best_gps
            if est:
                preview_lat = est[0] + (self.landing_offset_m / R) * (180 / math.pi)
                preview_lon = est[1]
                px, py = gps_to_scatter(preview_lat, preview_lon)
                if 0 <= px < S and 0 <= py < S:
                    # Hollow circle with crosshair — "preview" style
                    cv2.circle(scat, (px, py), 7, (180, 0, 255), 1)
                    cv2.line(scat, (px - 4, py), (px + 4, py), (180, 0, 255), 1)
                    cv2.line(scat, (px, py - 4), (px, py + 4), (180, 0, 255), 1)
                    cv2.putText(scat, "L preview", (px + 10, py - 3),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.3, (180, 0, 255), 1)
                    # Distance from preview landing to actual dummy
                    preview_to_actual = self._gps_distance(preview_lat, preview_lon,
                                                           true_lat, true_lon)
                    cv2.putText(scat, f"{preview_to_actual:.1f}m from dummy",
                                (px + 10, py + 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.3, (180, 0, 255), 1)

        # Plot actual landed position (white square) + metrics when landed
        if self.landing_phase == "landed" and self.landed_pos:
            ax, ay = gps_to_scatter(self.landed_pos[0], self.landed_pos[1])
            if 0 <= ax < S and 0 <= ay < S:
                cv2.rectangle(scat, (ax - 5, ay - 5), (ax + 5, ay + 5), (255, 255, 255), 2)
                cv2.putText(scat, "LANDED", (ax + 8, ay - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1)
                # Distance from landed to actual dummy
                landed_dist = self._gps_distance(self.landed_pos[0], self.landed_pos[1],
                                                  true_lat, true_lon)
                cv2.putText(scat, f"{landed_dist:.1f}m", (ax + 8, ay + 8),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1)

        # Logged items (IOI = cyan diamond, FP = red X)
        for item in self.logged_items:
            gps = item.get("gps")
            if gps:
                ix, iy = gps_to_scatter(gps[0], gps[1])
                if 0 <= ix < S and 0 <= iy < S:
                    if item["type"] == "interest":
                        pts = np.array([(ix, iy-6), (ix+5, iy), (ix, iy+6), (ix-5, iy)], np.int32)
                        cv2.fillPoly(scat, [pts], (255, 255, 0))
                        cv2.putText(scat, "IOI", (ix + 8, iy + 4),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 0), 1)
                    else:
                        cv2.line(scat, (ix-4, iy-4), (ix+4, iy+4), (0, 0, 255), 2)
                        cv2.line(scat, (ix-4, iy+4), (ix+4, iy-4), (0, 0, 255), 2)

        # Title and error
        zone_str = " [LANDING ZONE]" if self.show_landing_zone else ""
        zoom_str = f" x{self.scatter_zoom:.1f}" if self.scatter_zoom != 1.0 else ""
        n_dummies = len(self.all_target_gps) if hasattr(self, 'all_target_gps') else 1
        ref_str = f" [D#{min(self.scatter_ref_idx, n_dummies-1)+1}/{n_dummies} Tab]" if n_dummies > 1 else ""
        cv2.putText(scat, f"SCATTER +/-{scale_m:.0f}m{ref_str}{zone_str}{zoom_str}", (10, 18),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
        # Show error for each cluster relative to the scatter reference dummy
        if self.best_gps and ref_gps:
            err = self._gps_distance(self.best_gps[0], self.best_gps[1],
                                     true_lat, true_lon)
            cv2.putText(scat, f"Active EST err: {err:.2f}m  ({n} obs)",
                        (10, S - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 255), 1)

        return scat

    def _draw_dashed_circle(self, img, center, radius, color, thickness=1, dash_len=12):
        """Draw a dashed circle using small arc segments."""
        if radius < 1:
            return
        circumference = 2 * math.pi * radius
        n_dashes = max(4, int(circumference / dash_len))
        for i in range(0, n_dashes, 2):
            start_angle = int(i * 360 / n_dashes)
            end_angle = int((i + 1) * 360 / n_dashes)
            cv2.ellipse(img, center, (radius, radius), 0, start_angle, end_angle, color, thickness)

    def _on_trackbar(self, val):
        """Callback for trackbar changes — reads all sliders and updates error params."""
        pass  # Values read directly in run loop

    def run(self):
        """Main loop — state machine: INIT → CONNECTING → FLYING.
        YOU arm and take off manually (RC / Mission Planner).
        Script just reads telemetry + runs CV + estimates GPS."""
        print("Starting mission loop...")
        cv2.namedWindow("Simple Simulator", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Simple Simulator", 1280, 720)  # default — drag edges to resize

        # --- Error control sliders (separate small window) ---
        cv2.namedWindow("Error Controls", cv2.WINDOW_NORMAL)
        cv2.createTrackbar("GPS Drift (x0.1m)", "Error Controls", int(self.gps_drift_max * 10), 50, self._on_trackbar)
        cv2.createTrackbar("Alt Noise (x0.1m)", "Error Controls", int(self.alt_noise * 10), 30, self._on_trackbar)
        cv2.createTrackbar("Yaw Noise (x0.1deg)", "Error Controls", int(self.yaw_noise * 10), 100, self._on_trackbar)
        cv2.createTrackbar("FOV Error (%-10 to +10)", "Error Controls", int(self.fov_error_pct + 10), 20, self._on_trackbar)
        cv2.createTrackbar("Shake (px)", "Error Controls", self.shake_px, 20, self._on_trackbar)
        cv2.createTrackbar("Landing Zone", "Error Controls", 0, 1, self._on_trackbar)
        cv2.createTrackbar("Resolution (0=640 1=320 2=160)", "Error Controls", 0, 2, self._on_trackbar)
        # Show a tiny placeholder so the window appears with sliders
        cv2.imshow("Error Controls", np.zeros((1, 400, 3), dtype=np.uint8))

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
                    self.detection_cluster_count += 1
                    self.calculate_target_gps(u, v)
                    snap_str = " SNAP!" if self.centre_snap else ""
                    best_str = (f" best:{self.best_gps_error_m:.2f}m"
                                if self.best_gps_error_m is not None else "")
                    print(f"[CV] #{self.detection_count}: "
                          f"({u},{v}) conf {conf:.2f}{snap_str} → "
                          f"err {self.gps_error_m:.2f}m{best_str}"
                          if self.gps_error_m else
                          f"[CV] #{self.detection_count}: ({u},{v}) conf {conf:.2f}")

                    # Save detection image with bbox + GPS in filename
                    if self.save_detections and frame is not None:
                        import os
                        det_frame = frame.copy()
                        box_size = 40
                        x1 = max(0, int(u) - box_size)
                        y1 = max(0, int(v) - box_size)
                        x2 = min(det_frame.shape[1], int(u) + box_size)
                        y2 = min(det_frame.shape[0], int(v) + box_size)
                        cv2.rectangle(det_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.putText(det_frame, f"conf={conf:.2f}", (x1, y1 - 8),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                        cv2.putText(det_frame, f"alt={self.alt:.1f}m  GPS=({self.lat:.6f},{self.lon:.6f})",
                                    (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                        ts_file = time.strftime("%Y%m%d_%H%M%S")
                        lat_s = f"{self.lat:.6f}".replace('-', 'n')
                        lon_s = f"{self.lon:.6f}".replace('-', 'n')
                        det_fname = f"{ts_file}_{lat_s}_{lon_s}_{conf:.2f}.jpg"
                        cv2.imwrite(os.path.join(self.det_dir, det_fname), det_frame)
                        self.saved_det_count += 1

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
                    # Check if close enough to start descending (real GPS gets within ~1-2m)
                    dist_to_land = self._gps_distance(
                        self.true_lat, self.true_lon,
                        self.landing_target[0], self.landing_target[1])
                    if dist_to_land < 1.5 and self.groundspeed < 0.5:
                        self.landing_phase = "descending"
                        print(f"[LAND] Arrived at landing point ({dist_to_land:.1f}m). Descending...")
                        self.send_land()
                elif self.landing_phase == "descending":
                    # Keep commanding target position during descent to hold over landing point
                    if self.landing_target and self.master:
                        self.send_to_gps(self.landing_target[0], self.landing_target[1])
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
                        # Get estimate info (source + position used for landing calc)
                        src = getattr(self, 'landing_est_source', 'unknown')
                        est_pos = getattr(self, 'landing_est_pos', self.locked_gps or self.best_gps)
                        est_to_actual = 0
                        if est_pos and self.actual_gps:
                            est_to_actual = self._gps_distance(
                                est_pos[0], est_pos[1], self.actual_gps[0], self.actual_gps[1])
                        print(f"\n{'='*50}")
                        print(f"  LANDING REPORT  (estimate source: {src})")
                        print(f"{'='*50}")
                        print(f"  Dummy (actual):     {self.actual_gps[0]:.6f}, {self.actual_gps[1]:.6f}")
                        if est_pos:
                            print(f"  Dummy (estimate):   {est_pos[0]:.6f}, {est_pos[1]:.6f}  (err: {est_to_actual:.2f}m)")
                        print(f"  Landing target:     {self.landing_target[0]:.6f}, {self.landing_target[1]:.6f}  ({self.landing_offset_m}m north of estimate)")
                        print(f"  Actual landed at:   {self.landed_pos[0]:.6f}, {self.landed_pos[1]:.6f}")
                        print(f"  ---")
                        print(f"  Estimate error:     {est_to_actual:.2f}m  (how far estimate was from real dummy)")
                        print(f"  Landing GPS error:  {landed_to_target:.2f}m  (how far from target coordinate)")
                        print(f"  Distance to dummy:  {landed_to_dummy:.2f}m  (wanted {self.landing_offset_m}m)")
                        print(f"  Off by:             {abs(landed_to_dummy - self.landing_offset_m):.2f}m  from intended {self.landing_offset_m}m")
                        print(f"{'='*50}")

                # --- Investigate mode (N key): fly 5m from estimate, descend to 15m ---
                if self.investigating and self.master:
                    if self.investigate_phase == "approaching":
                        self.send_to_gps(self.investigate_target[0], self.investigate_target[1])
                        dist_to_inv = self._gps_distance(
                            self.true_lat, self.true_lon,
                            self.investigate_target[0], self.investigate_target[1])
                        if dist_to_inv < 3.0 and self.groundspeed < 1.0:
                            self.investigate_phase = "descending"
                            print(f"[INVESTIGATE] Arrived nearby ({dist_to_inv:.1f}m). Descending to {self.investigate_alt:.0f}m...")
                            # Descend by sending position at lower altitude
                            self.master.mav.set_position_target_global_int_send(
                                0, self.master.target_system, self.master.target_component,
                                mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
                                0b110111111000,
                                int(self.investigate_target[0] * 1e7),
                                int(self.investigate_target[1] * 1e7),
                                self.investigate_alt,
                                0, 0, 0, 0, 0, 0, 0, 0)
                    elif self.investigate_phase == "descending":
                        # Hold position and descend
                        self.master.mav.set_position_target_global_int_send(
                            0, self.master.target_system, self.master.target_component,
                            mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
                            0b110111111000,
                            int(self.investigate_target[0] * 1e7),
                            int(self.investigate_target[1] * 1e7),
                            self.investigate_alt,
                            0, 0, 0, 0, 0, 0, 0, 0)
                        if abs(self.alt - self.investigate_alt) < 1.5:
                            self.investigate_phase = "observing"
                            new_obs = len(self.gps_observations) - self.investigate_obs_start
                            print(f"[INVESTIGATE] At {self.alt:.1f}m — OBSERVING. "
                                  f"({new_obs} new detections so far). "
                                  f"Fly around with WASD or press N to cancel.")
                    elif self.investigate_phase == "observing":
                        # Hold position — estimate improves in background, drone stays put
                        self.send_to_gps(self.investigate_target[0], self.investigate_target[1])
                        # Print periodic updates
                        new_obs = len(self.gps_observations) - self.investigate_obs_start
                        if new_obs > 0 and new_obs % 10 == 0 and self.best_gps_error_m is not None:
                            est_err_start = self.investigate_est_at_start or 0
                            improvement = est_err_start - self.best_gps_error_m
                            print(f"[INVESTIGATE] {new_obs} new obs, "
                                  f"EST err: {self.best_gps_error_m:.2f}m "
                                  f"({'improved' if improvement > 0 else 'same'} "
                                  f"by {abs(improvement):.2f}m)")

                        # --- Altitude test: auto-step through altitudes ---
                        if self.alt_test_active:
                            if self.alt_test_start_time == 0:
                                # Just arrived at this altitude
                                self.alt_test_start_time = time.time()
                                self.alt_test_obs_start = len(self.gps_observations)
                                # Reset cluster for clean measurement
                                self.detection_clusters = [self._new_cluster()]
                                self.active_cluster_idx = 0
                                self.investigate_cluster_idx = 0
                                alt = self.alt_test_altitudes[self.alt_test_step]
                                print(f"[ALT TEST] Hovering at {alt}m — collecting for {self.alt_test_duration}s...")

                            elapsed = time.time() - self.alt_test_start_time
                            if elapsed >= self.alt_test_duration:
                                # Record results for this altitude
                                alt = self.alt_test_altitudes[self.alt_test_step]
                                cl = self.detection_clusters[0] if self.detection_clusters else {}
                                n_obs = cl.get("detection_count", 0)
                                result = {
                                    "alt": alt,
                                    "n_obs": n_obs,
                                    "rolling_err": cl.get("error_m"),
                                    "total_err": cl.get("total_error_m"),
                                    "kalman_err": cl.get("kalman_error_m"),
                                }
                                self.alt_test_results.append(result)
                                e_r = f"{result['rolling_err']:.2f}m" if result['rolling_err'] else "N/A"
                                e_t = f"{result['total_err']:.2f}m" if result['total_err'] else "N/A"
                                e_k = f"{result['kalman_err']:.2f}m" if result['kalman_err'] else "N/A"
                                print(f"[ALT TEST] {alt}m: {n_obs} obs | R50={e_r} Total={e_t} Kalman={e_k}")

                                # Next altitude or finish
                                self.alt_test_step += 1
                                if self.alt_test_step < len(self.alt_test_altitudes):
                                    next_alt = self.alt_test_altitudes[self.alt_test_step]
                                    self.investigate_alt = next_alt
                                    self.investigate_phase = "descending"
                                    self.alt_test_start_time = 0
                                    print(f"[ALT TEST] Moving to {next_alt}m...")
                                else:
                                    # Done — print summary
                                    self.alt_test_active = False
                                    self.investigating = False
                                    self.investigate_phase = None
                                    print(f"\n{'='*60}")
                                    print(f"  ALTITUDE TEST RESULTS")
                                    print(f"{'='*60}")
                                    print(f"  {'ALT':>5}  {'OBS':>5}  {'ROLLING':>8}  {'TOTAL':>8}  {'KALMAN':>8}")
                                    print(f"  {'-'*5}  {'-'*5}  {'-'*8}  {'-'*8}  {'-'*8}")
                                    for r in self.alt_test_results:
                                        e_r = f"{r['rolling_err']:.2f}m" if r['rolling_err'] else "N/A"
                                        e_t = f"{r['total_err']:.2f}m" if r['total_err'] else "N/A"
                                        e_k = f"{r['kalman_err']:.2f}m" if r['kalman_err'] else "N/A"
                                        print(f"  {r['alt']:>4}m  {r['n_obs']:>5}  {e_r:>8}  {e_t:>8}  {e_k:>8}")
                                    print(f"{'='*60}")
                                    # Restore original clusters
                                    if hasattr(self, 'alt_test_saved_clusters'):
                                        self.detection_clusters = self.alt_test_saved_clusters
                                        self.active_cluster_idx = 0 if self.detection_clusters else None

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

            # --- Read slider values and update error parameters ---
            try:
                self.gps_drift_max = cv2.getTrackbarPos("GPS Drift (x0.1m)", "Error Controls") / 10.0
                self.alt_noise = cv2.getTrackbarPos("Alt Noise (x0.1m)", "Error Controls") / 10.0
                self.yaw_noise = cv2.getTrackbarPos("Yaw Noise (x0.1deg)", "Error Controls") / 10.0
                fov_raw = cv2.getTrackbarPos("FOV Error (%-10 to +10)", "Error Controls")
                self.fov_error_pct = fov_raw - 10
                self.fov_scale = 1.0 + (self.fov_error_pct / 100.0)
                self.shake_px = cv2.getTrackbarPos("Shake (px)", "Error Controls")
                self.show_landing_zone = cv2.getTrackbarPos("Landing Zone", "Error Controls") == 1
                self.resolution_idx = cv2.getTrackbarPos("Resolution (0=640 1=320 2=160)", "Error Controls")
            except cv2.error:
                pass  # window not ready yet

            # --- Build 2x2 grid (simulation only, else just camera) ---
            if config.MODE == "SIMULATION" and self.sim:
                PANEL_H = 480  # height of each panel in the grid

                # Top-left: God view
                px, py = self.geo.gps_to_pixels(self.true_lat, self.true_lon)
                show_gps = (0, 0)  # clusters handle EST display now
                show_landing = self.landing_target if self.landing_target else (0, 0)
                god_frame = self.sim.get_god_view(
                    px, py, self.yaw, self.view_w_px, self.view_h_px,
                    self.zoom_level, np.array([], np.int32), self.search_poly,
                    show_gps, show_landing, self.geo,
                    logged_items=self.logged_items,
                    detection_clusters=self.detection_clusters,
                    active_cluster_idx=self.active_cluster_idx)
                # Resize god view to PANEL_H height, keep aspect
                gh, gw = god_frame.shape[:2]
                god_w = int(gw * PANEL_H / gh)
                god_resized = cv2.resize(god_frame, (god_w, PANEL_H))

                # Top-right: Camera view (already PANEL_H if IMAGE_H == 480)
                cam = cv2.resize(frame, (config.IMAGE_W, PANEL_H))

                # Bottom-left: Scatter plot
                scatter = self.draw_scatter()
                scat_w = int(scatter.shape[1] * PANEL_H / scatter.shape[0])
                scatter_resized = cv2.resize(scatter, (scat_w, PANEL_H))

                # Bottom-right: Dashboard
                dashboard = self.draw_dashboard()
                dash_w = int(dashboard.shape[1] * PANEL_H / dashboard.shape[0])
                dash_resized = cv2.resize(dashboard, (dash_w, PANEL_H))

                # Match widths per row with padding
                top_w = god_w + config.IMAGE_W
                bot_w = scat_w + dash_w
                target_w = max(top_w, bot_w)

                # Pad rows to same width
                def pad_row(row, target_width):
                    h, w = row.shape[:2]
                    if w < target_width:
                        pad = np.zeros((h, target_width - w, 3), dtype=np.uint8)
                        return np.hstack((row, pad))
                    return row

                top_row = np.hstack((god_resized, cam))
                bot_row = np.hstack((scatter_resized, dash_resized))
                top_row = pad_row(top_row, target_w)
                bot_row = pad_row(bot_row, target_w)
                final = np.vstack((top_row, bot_row))

                # Store grid boundaries for mouse callback (scroll zoom routing)
                self.grid_split_x = scat_w  # left/right boundary in bottom row
                self.grid_split_y = PANEL_H  # top/bottom boundary
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
            elif key == ord('t') or key == ord('T'):  # toggle CV model view
                self.show_cv_view = not self.show_cv_view
                state = "ON — showing what CV model sees" if self.show_cv_view else "OFF — full resolution"
                print(f"[CV VIEW] {state}")
            elif key == 9:  # Tab = cycle scatter reference dummy
                if hasattr(self, 'all_target_gps') and len(self.all_target_gps) > 1:
                    self.scatter_ref_idx = (self.scatter_ref_idx + 1) % len(self.all_target_gps)
                    self.scatter_pan_x = 0.0  # reset pan when switching
                    self.scatter_pan_y = 0.0
                    print(f"[SCATTER] Reference: dummy #{self.scatter_ref_idx + 1} of {len(self.all_target_gps)}")
            elif key == ord('l') or key == ord('L'):
                # Pick best available estimate: G lock > GPS EST
                # NEVER uses actual dummy position — only what we've estimated
                est_source = None
                est_pos = None
                if self.locked_gps:
                    est_pos = self.locked_gps
                    est_source = "G LOCK"
                else:
                    # Use running total average from active cluster
                    ci = self.active_cluster_idx
                    if ci is not None and ci < len(self.detection_clusters):
                        cl = self.detection_clusters[ci]
                        if cl.get("total_gps"):
                            est_pos = cl["total_gps"]
                            est_source = "TOTAL AVG"
                    if not est_pos and self.best_gps:
                        est_pos = self.best_gps
                        est_source = "ROLLING 50"

                if est_pos and self.landing_phase is None:
                    R = 6371000
                    est_lat, est_lon = est_pos
                    offset_lat = self.landing_offset_m / R * (180 / math.pi)
                    land_lat = est_lat + offset_lat
                    land_lon = est_lon
                    self.landing_target = (land_lat, land_lon)
                    self.landing_phase = "flying_to"
                    self.landing_est_source = est_source
                    self.landing_est_pos = est_pos
                    self.centering = False
                    self.visual_servo = False
                    # Cancel investigate if active
                    if self.investigating:
                        self.investigating = False
                        self.investigate_phase = None
                        print("[INVESTIGATE] Cancelled — landing takes priority")
                    # Show estimate error if we know ground truth (sim only)
                    est_err_str = ""
                    if self.actual_gps:
                        est_err = self._gps_distance(est_lat, est_lon, self.actual_gps[0], self.actual_gps[1])
                        est_err_str = f"  (estimate error: {est_err:.2f}m)"
                    print(f"\n[LAND] Using {est_source} estimate: {est_lat:.6f}, {est_lon:.6f}{est_err_str}")
                    print(f"[LAND] Landing {self.landing_offset_m}m north of estimated dummy")
                    print(f"[LAND] Target: {land_lat:.6f}, {land_lon:.6f}")
                    print(f"[LAND] Flying to landing point...")
                elif self.landing_phase == "landed":
                    print("[LAND] Already landed.")
                elif not est_pos:
                    print("[LAND] No dummy estimate yet — detect target first (fly over, use C or V)")
                else:
                    self.send_land()  # emergency land during landing sequence
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
            elif key == ord('h') or key == ord('H'):  # altitude test
                if self.alt_test_active:
                    self.alt_test_active = False
                    print("[ALT TEST] Cancelled")
                elif self.master and self.armed and self.alt > 2:
                    # Need a target position — use active cluster total avg
                    ci = self.active_cluster_idx
                    target = None
                    if ci is not None and ci < len(self.detection_clusters):
                        cl = self.detection_clusters[ci]
                        target = cl.get("total_gps") or cl.get("best_gps")
                    if not target and self.best_gps:
                        target = self.best_gps
                    if target:
                        self.alt_test_active = True
                        self.alt_test_step = 0
                        self.alt_test_results = []
                        self.alt_test_target = target
                        # Reset cluster for clean per-altitude comparison
                        self.alt_test_saved_clusters = [dict(c) for c in self.detection_clusters]
                        alt = self.alt_test_altitudes[0]
                        print(f"\n[ALT TEST] Starting altitude comparison test")
                        print(f"[ALT TEST] Altitudes: {self.alt_test_altitudes}m, {self.alt_test_duration}s each")
                        print(f"[ALT TEST] Flying to target at {alt}m...")
                        # Create fresh test cluster
                        self.detection_clusters = [self._new_cluster()]
                        self.active_cluster_idx = 0
                        self.investigate_cluster_idx = 0
                        self.investigating = True
                        self.investigate_phase = "approaching"
                        self.investigate_target = target
                        self.investigate_alt = alt
                        self.alt_test_start_time = 0  # set when we reach altitude
                    else:
                        print("[ALT TEST] No target detected yet — fly past dummy first")
                else:
                    print("[ALT TEST] Need to be armed and airborne first")
            elif key == ord('n') or key == ord('N'):  # investigate — fly near estimate
                if self.investigating:
                    # Cancel investigation
                    self.investigating = False
                    self.investigate_phase = None
                    self.investigate_target = None
                    self.investigate_cluster_idx = None
                    print("[INVESTIGATE] Cancelled — manual control")
                elif self.active_cluster_idx is not None and self.master:
                    # Investigate the most recently active cluster
                    self._start_investigate(self.active_cluster_idx)
                elif self.best_gps and self.master:
                    # Fallback: investigate current best GPS
                    self._start_investigate_gps(self.best_gps)
                else:
                    print("[INVESTIGATE] No target detected yet — fly around first")
            elif ord('1') <= key <= ord('9'):
                # Number keys: investigate specific cluster
                cluster_num = key - ord('1')  # 0-indexed
                if cluster_num < len(self.detection_clusters):
                    if self.investigating:
                        self.investigating = False
                        self.investigate_phase = None
                        print(f"[INVESTIGATE] Switching to item {self._cluster_label(cluster_num)}")
                    self._start_investigate(cluster_num)
                else:
                    print(f"[INVESTIGATE] No item at position {cluster_num + 1} — only {len(self.detection_clusters)} in list")
            elif key == ord('y') or key == ord('Y'):
                # Confirm: this is the real dummy
                if self.investigating and self.investigate_phase == "observing":
                    ci = self.investigate_cluster_idx
                    n_det = self.detection_clusters[ci]["detection_count"] if ci is not None and ci < len(self.detection_clusters) else "?"
                    print(f"\n[CONFIRM] Pilot confirms: REAL DUMMY (item {self._cluster_label(ci)}, {n_det} detections)")
                    print(f"[CONFIRM] Estimate: {self.best_gps[0]:.6f}, {self.best_gps[1]:.6f}" if self.best_gps else "")
                    print("[CONFIRM] Press L to land 7.5m away")
                    # Remove other clusters (keep only confirmed one)
                    if ci is not None and ci < len(self.detection_clusters):
                        confirmed = self.detection_clusters[ci]
                        self.detection_clusters = [confirmed]
                        self.active_cluster_idx = 0
                        self.best_gps = confirmed["best_gps"]
                    self.investigating = False
                    self.investigate_phase = None
                    self.investigate_target = None
                    self.investigate_cluster_idx = None
            elif key == ord('i') or key == ord('I'):
                # Item of interest — log position and resume search
                if self.investigating and self.investigate_phase == "observing":
                    ci = self.investigate_cluster_idx
                    cluster = self.detection_clusters[ci] if ci is not None and ci < len(self.detection_clusters) else None
                    gps = cluster["best_gps"] if cluster else self.best_gps
                    n_det = cluster["detection_count"] if cluster else 0
                    if gps:
                        item = {"type": "interest", "gps": gps, "detections": n_det}
                        self.logged_items.append(item)
                        print(f"\n[LOG] Item {self._cluster_label(ci)} logged as INTEREST at {gps[0]:.6f}, {gps[1]:.6f}"
                              f" ({n_det} detections)")
                        # Remove classified cluster
                        if ci is not None and ci < len(self.detection_clusters):
                            self.detection_clusters.pop(ci)
                            self.active_cluster_idx = None
                        n_ioi = sum(1 for x in self.logged_items if x["type"] == "interest")
                        print(f"[LOG] Total: {n_ioi} IOI, {len(self.detection_clusters)} items remaining")
                    # Cancel investigate
                    self.investigating = False
                    self.investigate_phase = None
                    self.investigate_target = None
                    self.investigate_cluster_idx = None
                    # Update best_gps to next available cluster
                    if self.detection_clusters:
                        self.active_cluster_idx = 0
                        self.best_gps = self.detection_clusters[0]["best_gps"]
                    else:
                        self.best_gps = None
                        self.best_gps_error_m = None
            elif key == ord('x') or key == ord('X'):
                # False positive — discard and resume search (X not F, F=throttle down)
                if self.investigating and self.investigate_phase == "observing":
                    ci = self.investigate_cluster_idx
                    cluster = self.detection_clusters[ci] if ci is not None and ci < len(self.detection_clusters) else None
                    gps = cluster["best_gps"] if cluster else self.best_gps
                    n_det = cluster["detection_count"] if cluster else 0
                    # Log as false positive (for display on map)
                    if gps:
                        self.logged_items.append({"type": "false_pos", "gps": gps, "detections": n_det})
                    print(f"\n[DISCARD] Item {self._cluster_label(ci)} discarded as FALSE POSITIVE ({n_det} detections)")
                    # Remove classified cluster
                    if ci is not None and ci < len(self.detection_clusters):
                        self.detection_clusters.pop(ci)
                        self.active_cluster_idx = None
                    # Cancel investigate
                    self.investigating = False
                    self.investigate_phase = None
                    self.investigate_target = None
                    self.investigate_cluster_idx = None
                    # Update best_gps to next available cluster
                    if self.detection_clusters:
                        self.active_cluster_idx = 0
                        self.best_gps = self.detection_clusters[0]["best_gps"]
                    else:
                        self.best_gps = None
                        self.best_gps_error_m = None
                    print(f"[DISCARD] {len(self.detection_clusters)} items remaining")
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
                    # Any manual input cancels centering / visual servo / investigate
                    if self.centering or self.visual_servo or self.investigating:
                        self.centering = False
                        self.visual_servo = False
                        if self.investigating:
                            self.investigating = False
                            self.investigate_phase = None
                            print("[INVESTIGATE] Cancelled — manual override")
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
        if self.save_detections:
            print(f"  Detection images saved: {self.saved_det_count} in {self.det_dir}/")
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
        """Zoom on scroll, drag to pan — god view (top-left) or scatter (bottom-left)."""
        in_scatter = y > self.grid_split_y and x < self.grid_split_x

        if event == cv2.EVENT_MOUSEWHEEL:
            if in_scatter:
                # Scroll over scatter plot — zoom scatter
                if flags > 0:
                    self.scatter_zoom = min(self.scatter_zoom * 1.2, 10.0)
                else:
                    self.scatter_zoom = max(self.scatter_zoom / 1.2, 0.3)
            else:
                # Scroll over god view (or anywhere else) — zoom map
                if flags > 0:
                    self.zoom_level = min(self.zoom_level * 1.2, 20.0)
                else:
                    self.zoom_level = max(self.zoom_level / 1.2, 1.0)

        # Drag to pan scatter plot
        elif event == cv2.EVENT_LBUTTONDOWN and in_scatter:
            self._scatter_dragging = True
            self._scatter_drag_start = (x, y)
            self._scatter_pan_start = (self.scatter_pan_x, self.scatter_pan_y)

        elif event == cv2.EVENT_MOUSEMOVE and self._scatter_dragging:
            dx_px = x - self._scatter_drag_start[0]
            dy_px = y - self._scatter_drag_start[1]
            ppm = self.scatter_px_per_m if self.scatter_px_per_m > 0 else 1.0
            self.scatter_pan_x = self._scatter_pan_start[0] - dx_px / ppm
            self.scatter_pan_y = self._scatter_pan_start[1] + dy_px / ppm

        elif event == cv2.EVENT_LBUTTONUP:
            self._scatter_dragging = False


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
    parser.add_argument("--alt-noise", type=float, default=0, metavar="METRES",
                        help="Altitude reading noise (e.g. --alt-noise 1 for +/-1m jitter). Default: off")
    parser.add_argument("--yaw-noise", type=float, default=0, metavar="DEGREES",
                        help="Heading/compass noise (e.g. --yaw-noise 3 for +/-3deg jitter). Default: off")
    parser.add_argument("--fov-error", type=float, default=0, metavar="PERCENT",
                        help="FOV calibration error (e.g. --fov-error 5 for 5%% systematic bias). Default: off")
    parser.add_argument("--cluster-dist", type=float, default=30.0, metavar="METRES",
                        help="Min distance between separate detection clusters (default: 30m)")
    parser.add_argument("--save-detections", action="store_true",
                        help="Save detection frames with bbox + GPS to detections/ folder")
    parser.add_argument("--det-dir", type=str, default="detections",
                        help="Output folder for detection images (default: detections/)")
    args = parser.parse_args()
    mission = SimpleMission(fps_limit=args.fps, force_tflite=args.tflite, gps_drift=args.gps_drift,
                            shake=args.shake, alt_noise=args.alt_noise, yaw_noise=args.yaw_noise,
                            fov_error=args.fov_error, cluster_dist=args.cluster_dist,
                            save_detections=args.save_detections, det_dir=args.det_dir)
    mission.run()
