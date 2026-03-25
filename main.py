# main.py
from pymavlink import mavutil
import time
import math
import cv2
import numpy as np
import csv
from datetime import datetime
import sys
import os
import threading

# --- Import Config with Safety Check ---
try:
    import config
    # Verify it's the correct config file by checking for a known attribute
    if not hasattr(config, 'MODE'):
        print("[ERROR] Loaded the wrong 'config' module!")
        print(f"Path loaded: {config.__file__}")
        print("Please rename your local 'config.py' to 'flight_config.py' to avoid conflicts.")
        sys.exit(1)
except ImportError:
    print("[ERROR] Could not import 'config.py'. Make sure it exists in the same folder.")
    sys.exit(1)

from states import State
from utils import GeoTransformer
from planning import PathPlanner
from vision import VisionSystem

# --- Extracted modules ---
# Choose state machine: default or no-descend variant
if "--no-descend" in sys.argv:
    from state_machine_no_descend import StateHandlersMixin
    print("[CONFIG] Using NO-DESCEND state machine (verify at search altitude)")
else:
    from state_machine import StateHandlersMixin
from navigation import NavigationController
from stream_server import (start_stream_server, set_stream_frame,
                           get_stream_frame, cmd_queue as stream_cmd_queue)
from gps_utils import gps_distance, calculate_target_from_pixels, landing_offset_7_5m

# Conditional Import for Simulation
if config.MODE == "SIMULATION":
    from simulator.simulation import SimulationEnvironment

# --- CLI FLAGS ---
# Model:      --model models/best2.tflite   (default: best.tflite)
# Dry-run:    --dry-run                      (skip GPS/arm, show pattern, print commands)
# Pattern:    --pattern spiral               (default: lawnmower)
# Stream:     --stream-port 8090 --stream-res 320x240 --stream-fps 5 --stream-quality 50
# No stream:  --no-stream
REAL_CANVAS_SIZE = 4800  # Virtual canvas size (pixels) for planner in REAL mode

DRY_RUN = "--dry-run" in sys.argv
MODEL_PATH = "best.tflite"
SEARCH_PATTERN = "lawnmower"
PRELOAD_SEARCH = "--search-area" in sys.argv  # skip polygon drawing, use KML survey area
PRE_WAYPOINTS_FILE = None  # --waypoints waypoints.json -> fly these BEFORE search pattern
TRANSIT_FILE = None        # --transit transit.json -> pre-drawn transit path (visualized + flown)
STREAM_ENABLED = "--no-stream" not in sys.argv
STREAM_PORT = 8090
STREAM_W, STREAM_H = 320, 240
STREAM_FPS = 5
STREAM_QUALITY = 50
SIM_SPEED = 1  # SITL speedup multiplier (default 1x real-time, use --speed 5 for faster)
NO_TURN = "--no-turn" in sys.argv  # Quadcopter strafes between waypoints (no yaw rotation)
NO_DESCEND = "--no-descend" in sys.argv  # Stay at search altitude, don't descend to verify
NFZ_REPEL = "--nfz-repel" in sys.argv   # Enable SSSI no-fly zone repulsion (potential field)
NFZ_SLOW = "--nfz-slow" in sys.argv     # Velocity toward waypoint at capped speed (20m zone)
NFZ_CARROT = "--nfz-carrot" in sys.argv  # Carrot-on-stick: nearby position target (20m zone)
NFZ_ARROWS = "--arrows" in sys.argv      # Draw vector field arrows in NFZ buffer zone
SMOOTH_BEZIER = "--smooth-bezier" in sys.argv  # Bezier curves at turns (smooth arcs)
SMOOTH_EXTRA = "--smooth-extra" in sys.argv    # Extra waypoints at turns (wider arc)
BEACON_DELAY = 0  # --beacon-delay N: simulate PLB signal N seconds after SEARCH begins (0=disabled)

for _i, _arg in enumerate(sys.argv):
    if _arg == "--model" and _i + 1 < len(sys.argv):
        MODEL_PATH = sys.argv[_i + 1]
    elif _arg == "--pattern" and _i + 1 < len(sys.argv):
        SEARCH_PATTERN = sys.argv[_i + 1]
    elif _arg == "--stream-port" and _i + 1 < len(sys.argv):
        STREAM_PORT = int(sys.argv[_i + 1])
    elif _arg == "--stream-res" and _i + 1 < len(sys.argv):
        _parts = sys.argv[_i + 1].split("x")
        STREAM_W, STREAM_H = int(_parts[0]), int(_parts[1])
    elif _arg == "--stream-fps" and _i + 1 < len(sys.argv):
        STREAM_FPS = int(sys.argv[_i + 1])
    elif _arg == "--stream-quality" and _i + 1 < len(sys.argv):
        STREAM_QUALITY = int(sys.argv[_i + 1])
    elif _arg == "--waypoints" and _i + 1 < len(sys.argv):
        PRE_WAYPOINTS_FILE = sys.argv[_i + 1]
    elif _arg == "--transit" and _i + 1 < len(sys.argv):
        TRANSIT_FILE = sys.argv[_i + 1]
    elif _arg == "--speed" and _i + 1 < len(sys.argv):
        SIM_SPEED = float(sys.argv[_i + 1])
    elif _arg == "--alt" and _i + 1 < len(sys.argv):
        config.TARGET_ALT = float(sys.argv[_i + 1])
    elif _arg == "--beacon-delay" and _i + 1 < len(sys.argv):
        BEACON_DELAY = float(sys.argv[_i + 1])

if DRY_RUN:
    print("=" * 60)
    print("  DRY-RUN MODE — No arming, no flying, no GPS needed")
    print("  Shows lawnmower pattern, prints commands, tests pipeline")
    print("=" * 60)

# Detect if display is available
HEADLESS = "--headless" in sys.argv
if not HEADLESS:
    try:
        # Test if we can create a window (fails over SSH/PuTTY without X11)
        _test_ok = os.environ.get('DISPLAY', '') != '' or sys.platform == 'win32'
        if not _test_ok:
            HEADLESS = True
    except Exception:
        HEADLESS = True

def _terminal_input_thread():
    """Read keypresses from terminal (works over PuTTY/SSH).
    Feeds into stream_cmd_queue so both terminal and browser share one queue."""
    import select
    if sys.platform == 'win32':
        import msvcrt
        while True:
            if msvcrt.kbhit():
                ch = msvcrt.getch()
                stream_cmd_queue.put(ch[0])
            time.sleep(0.05)
    else:
        import tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setcbreak(fd)
            while True:
                if select.select([sys.stdin], [], [], 0.05)[0]:
                    ch = sys.stdin.read(1)
                    if ch:
                        stream_cmd_queue.put(ord(ch))
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


class VisualFlightMission(StateHandlersMixin):
    def __init__(self):
        print(f"--- INITIALIZING IN {config.MODE} MODE ---")

        # 1. Initialize Geo & Map Tools
        if config.MODE == "SIMULATION":
            self.sim = SimulationEnvironment(GeoTransformer(map_w_px=100)) # Temp init
            self.geo = GeoTransformer(map_w_px=self.sim.map_w)
            self.sim.geo = self.geo # Sync geo tool
            # Returns only Target and Search Poly
            # Pre-load search polygon from KML if --search-area flag used
            preload_gps = None
            preload_transit = None
            if PRELOAD_SEARCH:
                if not config.load_kml_zones():
                    print("[WARN] KML load failed — using fallback SEARCH_AREA_GPS from config.py")
                preload_gps = config.SEARCH_AREA_GPS
                print(f"  Pre-loading search polygon from KML: {len(preload_gps)} points")
            # Load transit path from JSON for preloading onto setup map
            if TRANSIT_FILE:
                import json
                try:
                    with open(TRANSIT_FILE) as f:
                        data = json.load(f)
                    preload_transit = []
                    for wp in data:
                        if isinstance(wp, dict):
                            preload_transit.append((wp["lat"], wp["lon"]))
                        else:
                            preload_transit.append((wp[0], wp[1]))
                    print(f"  Pre-loading transit path: {len(preload_transit)} points from {TRANSIT_FILE}")
                except Exception as e:
                    print(f"WARNING: Failed to load transit from {TRANSIT_FILE}: {e}")
            self.target_px, self.tgt_type, self.search_poly, transit_px, focus_px = self.sim.setup_on_map(
                preload_polygon_gps=preload_gps, preload_transit_gps=preload_transit)

            # Store drawn focus polygon as GPS (PLB beacon area) + save to JSON
            if focus_px and len(focus_px) >= 3:
                config.FOCUS_AREA_GPS = [self.geo.pixels_to_gps(px[0], px[1]) for px in focus_px]
                print(f"  Focus Area drawn: {len(config.FOCUS_AREA_GPS)} points (PLB beacon redirect)")
                # Save to flight_plans/focus_area.json for mid-flight reloading
                import json
                fa_data = [{"lat": pt[0], "lon": pt[1], "label": f"F{i+1}"}
                           for i, pt in enumerate(config.FOCUS_AREA_GPS)]
                with open("flight_plans/focus_area.json", "w") as f:
                    json.dump(fa_data, f, indent=2)
                print(f"  Saved to flight_plans/focus_area.json")

            # Store drawn transit waypoints (pixels -> GPS, applied after pre_waypoints init)
            # Only save if NOT preloaded from file (avoid double-adding)
            if transit_px and not preload_transit:
                self._drawn_transit_gps = [self.geo.pixels_to_gps(px[0], px[1]) for px in transit_px]
                print(f"  Transit path drawn: {len(self._drawn_transit_gps)} waypoints")
            else:
                self._drawn_transit_gps = []

            self.eyes = VisionSystem(camera_index=None, model_path=MODEL_PATH)
            if self.tgt_type == "dummy": self.eyes.using_ai = True
            else: self.eyes.using_ai = False

        else: # REAL MODE
            self.sim = None

            # Try to show map for interactive polygon drawing
            self.search_poly = self._setup_real_search_area()

            cam_idx = None if DRY_RUN else config.REAL_CAMERA_INDEX
            self.eyes = VisionSystem(camera_index=cam_idx, model_path=MODEL_PATH)
            self.eyes.using_ai = True
            print("Vision System: Real Camera Initialized")

        # 2. Geofence (only with --nfz-repel flag)
        self.geofence = None
        if (NFZ_REPEL or NFZ_SLOW or NFZ_CARROT) and config.SSSI_GPS and len(config.SSSI_GPS) >= 3:
            from geofence import NFZGeofence
            self.geofence = NFZGeofence(self.geo)
            print(f"[GEOFENCE] Active — SSSI {len(config.SSSI_GPS)} corners, "
                  f"hard={self.geofence.HARD_BOUNDARY}m, soft={self.geofence.SOFT_BOUNDARY}m")

        # 3. Planner
        self.planner = PathPlanner(self.geo, self.search_poly)
        self.planner._no_turn = NO_TURN

        # Search waypoints generated after pre_waypoints are known (need transit endpoint)

        # 3. Connection
        self.master = None
        self.last_req = 0
        self.last_heartbeat = 0

        # 4. Navigation controller (created after master, updated when master connects)
        self.nav = None  # Set after self.master is established in _handle_init

        # 5. State & Telemetry
        self.state = State.INIT
        self.previous_state = State.HOVER
        self.state_start_time = time.time()  # FIX 5: track time in current state
        self.connect_start_time = 0          # FIX 4: heartbeat timeout tracking
        self.gps_fix_ok = False              # FIX 1: GPS lock validated before arming
        self._last_gps_status_print = 0      # FIX 1: throttle GPS status prints
        self._last_mode_warn = -1            # FIX 6: RC failsafe mode change detection
        self._arming_timeout_warned = False   # FIX 5: warn once per entry
        self._takeoff_timeout_warned = False
        self._centering_timeout_warned = False
        self._descending_timeout_warned = False
        self._last_log_time = 0              # Throttle CSV logging to ~1 Hz
        self._servo_released = False         # Payload servo state
        # Start at takeoff point if KML loaded, otherwise map origin
        if config.TAKEOFF_GPS:
            self.lat = config.TAKEOFF_GPS[0]
            self.lon = config.TAKEOFF_GPS[1]
        else:
            self.lat = config.REF_LAT
            self.lon = config.REF_LON
        # Remember home for return-to-launch
        self.home_lat = self.lat
        self.home_lon = self.lon
        self.return_wp_index = 0
        self.alt = 0.0
        self.vx = 0; self.vy = 0; self.vz = 0
        self.roll = 0; self.pitch = 0; self.yaw = 0

        # 6. Mission Data
        if not hasattr(self, 'waypoints'):
            self.waypoints = []
        self.wp_index = 0

        # Target Data
        self.target_lat = 0; self.target_lon = 0
        self.landing_lat = 0; self.landing_lon = 0
        self.current_conf = 0.0
        self.final_dist = 0.0 # Store final accuracy distance
        self.rejected_targets = []  # [(lat, lon), ...] — skip detections near these
        self.departure_lat = 0     # where drone left the search path to investigate
        self.departure_lon = 0
        self.manual_departure_lat = 0  # where manual mode was engaged
        self.manual_departure_lon = 0
        self.manual_departure_alt = 0
        # Rescan at lower altitude if nothing found (drop 20% each pass)
        self.max_rescan_passes = 3      # up to 3 rescans before giving up
        self.rescan_pass = 0            # 0 = first pass, 1+ = rescan

        # Pre-planned waypoints (fly before search)
        self.pre_waypoints = []
        self.pre_wp_index = 0

        def _load_waypoints_json(path):
            """Load waypoints from JSON — supports [{lat,lon},...] and [[lat,lon],...]"""
            import json
            wps = []
            with open(path) as f:
                data = json.load(f)
            for wp in data:
                if isinstance(wp, dict):
                    wps.append((wp["lat"], wp["lon"]))
                else:
                    wps.append((wp[0], wp[1]))
            return wps

        # Source 1: --waypoints flag
        if PRE_WAYPOINTS_FILE:
            try:
                wps = _load_waypoints_json(PRE_WAYPOINTS_FILE)
                self.pre_waypoints.extend(wps)
                print(f"  Pre-waypoints loaded: {len(wps)} from {PRE_WAYPOINTS_FILE}")
            except Exception as e:
                print(f"WARNING: Failed to load {PRE_WAYPOINTS_FILE}: {e}")
        # Source 2: --transit flag
        if TRANSIT_FILE:
            try:
                wps = _load_waypoints_json(TRANSIT_FILE)
                self.pre_waypoints.extend(wps)
                print(f"  Transit path loaded: {len(wps)} from {TRANSIT_FILE}")
            except Exception as e:
                print(f"WARNING: Failed to load {TRANSIT_FILE}: {e}")
        # Source 3: drawn on map during setup
        if hasattr(self, '_drawn_transit_gps') and self._drawn_transit_gps:
            self.pre_waypoints.extend(self._drawn_transit_gps)

        if self.pre_waypoints:
            print(f"  Total transit waypoints: {len(self.pre_waypoints)}")

        # Pre-generate search waypoints for visualization
        # Uses transit endpoint as start reference so search starts where transit ends
        if self.search_poly and len(self.search_poly) >= 3:
            if config.MODE == "SIMULATION":
                canvas_w, canvas_h = self.sim.map_w, self.sim.map_h
            else:
                canvas_w, canvas_h = REAL_CANVAS_SIZE, REAL_CANVAS_SIZE
            start_ref = self.pre_waypoints[-1] if self.pre_waypoints else None
            if SEARCH_PATTERN == "spiral":
                self.waypoints = self.planner.generate_spiral_pattern(canvas_w, canvas_h, start_ref)
            else:
                self.waypoints = self.planner.generate_search_pattern(canvas_w, canvas_h, start_ref)
            print(f"  Search pattern ({SEARCH_PATTERN}): {len(self.waypoints)} waypoints (start from {'transit endpoint' if start_ref else 'default'})")

        # Helper vars
        self.view_w_px = 100
        self.view_h_px = 100
        self.zoom_level = 1.0
        self.last_speed_req = 0
        self.waiting_for_confirmation = False
        self.selecting_landing_side = False

        # Logging
        self.log_file = open(config.LOG_FILE, 'w', newline='')
        self.logger = csv.writer(self.log_file)
        self.logger.writerow(["Timestamp", "State", "Lat", "Lon", "Alt", "Target_Conf"])

    def _setup_real_search_area(self):
        """Load search area from search_area.json, config GPS, or interactive drawing."""
        self.geo = GeoTransformer(map_w_px=REAL_CANVAS_SIZE)

        # Priority 1: search_area.json (created by draw_search_area.py on laptop)
        sa_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "flight_plans", "search_area.json")
        if os.path.exists(sa_file):
            import json
            with open(sa_file, "r") as f:
                data = json.load(f)
            if data and len(data) >= 3:
                gps_coords = [(pt["lat"], pt["lon"]) for pt in data]
                poly = [self.geo.gps_to_pixels(lat, lon) for lat, lon in gps_coords]
                print(f"[REAL] Search area loaded from search_area.json: {len(poly)} points")
                for pt in data:
                    print(f"    {pt.get('label','')}: ({pt['lat']:.6f}, {pt['lon']:.6f})")
                return poly

        # Priority 2: SEARCH_AREA_GPS from config.py / KML
        if hasattr(config, 'SEARCH_AREA_GPS') and len(config.SEARCH_AREA_GPS) >= 3:
            poly = [self.geo.gps_to_pixels(lat, lon) for lat, lon in config.SEARCH_AREA_GPS]
            print(f"[REAL] Search area loaded from config: {len(poly)} GPS corners")
            return poly

        print("[REAL] No search area defined — no search pattern")
        print("  Either:")
        print("    1. Run draw_search_area.py on laptop to create search_area.json")
        print("    2. Set SEARCH_AREA_GPS in config.py")
        return []

    # ── Telemetry ──────────────────────────────────────────────────────

    def update_telemetry(self):
        if not self.master: return
        while True:
            msg = self.master.recv_match(blocking=False)
            if not msg: break
            if msg.get_type() == 'GLOBAL_POSITION_INT':
                self.lat = msg.lat / 1e7
                self.lon = msg.lon / 1e7
                self.alt = msg.relative_alt / 1000.0
                self.vx = msg.vx / 100.0; self.vy = msg.vy / 100.0; self.vz = msg.vz / 100.0
            elif msg.get_type() == 'ATTITUDE':
                self.roll = msg.roll; self.pitch = msg.pitch; self.yaw = msg.yaw
            elif msg.get_type() == 'HEARTBEAT':
                # Only accept heartbeats from autopilot, not mavproxy GCS
                if msg.type != mavutil.mavlink.MAV_TYPE_GCS:
                    self.last_heartbeat = time.time()
                    # Set target system from first autopilot heartbeat
                    if self.master.target_system == 0:
                        self.master.target_system = msg.get_srcSystem()
                        self.master.target_component = msg.get_srcComponent()
                        print(f"[LINK] Autopilot found: system {self.master.target_system}")
                    # FIX 6: RC failsafe / unexpected mode change detection
                    if hasattr(msg, 'custom_mode'):
                        current_mode = msg.custom_mode
                        COPTER_MODES = {0:'STABILIZE',2:'ALT_HOLD',3:'AUTO',4:'GUIDED',
                                        5:'LOITER',6:'RTL',9:'LAND',16:'POSHOLD'}
                        if self.state not in (State.MANUAL, State.DONE, State.INIT, State.CONNECTING):
                            if current_mode != 4:  # Not GUIDED
                                mode_name = COPTER_MODES.get(current_mode, f"MODE_{current_mode}")
                                if self._last_mode_warn != current_mode:
                                    print(f"WARNING: Cube switched to {mode_name} (not GUIDED). RC override or failsafe?")
                                    self._last_mode_warn = current_mode

    # ── GPS math wrappers (delegate to gps_utils) ─────────────────────
    # The state handler mixin calls self.calculate_target_gps() and
    # self.calculate_landing_spot() — these thin wrappers keep that interface.

    def calculate_target_gps(self, u, v):
        """Convert pixel detection to estimated GPS position (wrapper around gps_utils)."""
        self.target_lat, self.target_lon = calculate_target_from_pixels(
            u, v,
            drone_alt=self.alt,
            drone_yaw=self.yaw,
            drone_lat=self.lat,
            drone_lon=self.lon,
            image_w=config.IMAGE_W,
            image_h=config.IMAGE_H,
            sensor_width_mm=config.SENSOR_WIDTH_MM,
            focal_length_mm=config.FOCAL_LENGTH_MM)
        print(f"[VISION] Target GPS: {self.target_lat:.6f}, {self.target_lon:.6f}")

    def calculate_landing_spot(self, direction_key):
        """Calculate a landing point 7.5m from target (wrapper around gps_utils)."""
        self.landing_lat, self.landing_lon = landing_offset_7_5m(
            self.target_lat, self.target_lon, direction_key)
        print(f"Landing Spot Selected: {direction_key.upper()} of Target")

    # ── Dashboard / HUD ────────────────────────────────────────────────

    def update_dashboard(self):
        found = False; u = 0; v = 0; conf = 0.0
        frame = None

        # 1. GET IMAGE FRAME
        if config.MODE == "SIMULATION":
            px, py = self.geo.gps_to_pixels(self.lat, self.lon)
            frame, self.view_w_px, self.view_h_px = self.sim.get_drone_view(px, py, self.alt, self.yaw)
        else:
            frame = self.eyes.get_frame()
            if frame is None:
                frame = np.zeros((config.IMAGE_H, config.IMAGE_W, 3), dtype=np.uint8)

        # 2. PROCESS FRAME
        found, u, v, conf = self.eyes.process_frame_manually(frame)
        self.current_conf = conf

        # 3. DRAW HUD
        cx, cy = config.IMAGE_W // 2, config.IMAGE_H // 2
        cv2.line(frame, (cx - 20, cy), (cx + 20, cy), (0, 255, 255), 2)
        cv2.line(frame, (cx, cy - 20), (cx, cy + 20), (0, 255, 255), 2)

        if found:
            cv2.circle(frame, (u, v), 15, (0, 255, 0), 2)
            cv2.line(frame, (u, v), (cx, cy), (0, 255, 0), 2)
            cv2.putText(frame, f"TGT {conf:.2f}", (u+10, v), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)

        # --- INFO PANEL ---
        # Basic Stats
        cv2.putText(frame, f"MODE: {config.MODE}", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        cv2.putText(frame, f"STATE: {self.state}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        cv2.putText(frame, f"ALT: {self.alt:.1f}m", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        model_name = os.path.basename(os.path.dirname(MODEL_PATH)) + "/" + os.path.basename(MODEL_PATH) if "/" in MODEL_PATH or "\\" in MODEL_PATH else os.path.basename(MODEL_PATH)
        cv2.putText(frame, f"MODEL: {model_name}", (10, 170), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

        # Current Position (Always displayed)
        ground_speed = math.sqrt(getattr(self, 'vx', 0)**2 + getattr(self, 'vy', 0)**2)
        cv2.putText(frame, f"POS: {self.lat:.6f}, {self.lon:.6f}  SPD: {ground_speed:.1f}m/s", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        # Target Location (If found/narrowing down)
        if self.target_lat != 0:
            cv2.putText(frame, f"TARGET: {self.target_lat:.6f}, {self.target_lon:.6f}", (10, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Landing Location (If determined)
        if self.landing_lat != 0:
            cv2.putText(frame, f"LANDING: {self.landing_lat:.6f}, {self.landing_lon:.6f}", (10, 170), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

        # Hover + two-stage servo release status
        if self.state == State.HOVER_TARGET:
            elapsed = time.time() - self.state_start_time
            remaining = max(0, 15.0 - elapsed)

            if elapsed < 3.0:
                # Waiting for stage 1
                cv2.putText(frame, f"HOVERING — waiting ({3.0-elapsed:.0f}s)", (cx - 200, cy + 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            elif elapsed < 6.0:
                # Stage 1 done, waiting for stage 2
                if int(elapsed * 3) % 2 == 0:
                    cv2.putText(frame, "PHASE 1 RELEASED", (cx - 180, cy - 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 165, 255), 3)
                cv2.putText(frame, f"Phase 2 in {6.0-elapsed:.0f}s", (cx - 100, cy + 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            elif elapsed < 15.0:
                # Both stages done, waiting to depart
                if int(elapsed * 3) % 2 == 0:
                    cv2.putText(frame, "PHASE 2 RELEASED", (cx - 180, cy - 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
                cv2.putText(frame, f"Departing in {15.0-elapsed:.0f}s", (cx - 120, cy + 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        # Manual mode indicator
        if self.state == State.MANUAL:
            cv2.putText(frame, "MANUAL OVERRIDE", (cx - 150, cy - 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 165, 255), 3)
            cv2.putText(frame, "WASD=fly R/F=alt Q/E=yaw M=resume", (cx - 220, cy + 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2)

        # Final Result (After Landing)
        if self.state == State.DONE:
             cv2.putText(frame, f"FINAL ERROR: {self.final_dist:.2f} m", (cx - 150, cy), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)


        if self.waiting_for_confirmation:
             if self.selecting_landing_side:
                 cv2.putText(frame, "SELECT LANDING SIDE:", (cx - 200, cy + 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                 cv2.putText(frame, "N: North | S: South", (cx - 200, cy + 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                 cv2.putText(frame, "W: West  | E: East", (cx - 200, cy + 120), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
             else:
                 cv2.putText(frame, "Y=Confirm  N=Reject  I=Interest", (cx - 200, cy + 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        # Items of interest list on camera HUD
        if hasattr(self, 'items_of_interest') and self.items_of_interest:
            y_off = frame.shape[0] - 30 * len(self.items_of_interest) - 10
            for idx, item in enumerate(self.items_of_interest):
                label = f"I{idx+1}: ({item['lat']:.5f}, {item['lon']:.5f})"
                cv2.putText(frame, label, (10, y_off + idx * 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 100, 0), 2)

        # Servo release animation during HOVER_TARGET only
        # Synced to actual servo timeline: 0-3s wait, 3s=stage1 fast drop, 6s=stage2 rope gone, 15s=depart
        if self.state == State.HOVER_TARGET and hasattr(self, '_hover_elapsed'):
            elapsed = self._hover_elapsed
            h, w = frame.shape[:2]
            # Animation panel (bottom-right, 250x180)
            ax, ay, aw, ah = w - 270, h - 200, 250, 180
            # Sky + ground
            cv2.rectangle(frame, (ax, ay), (ax+aw, ay+ah), (180, 130, 80), -1)
            ground_y = ay + ah - 25
            cv2.rectangle(frame, (ax, ground_y), (ax+aw, ay+ah), (50, 120, 50), -1)
            cv2.rectangle(frame, (ax, ay), (ax+aw, ay+ah), (255, 255, 255), 1)

            drone_x = ax + aw // 2
            drone_y = ay + 35

            def draw_drone(dx, dy):
                cv2.rectangle(frame, (dx-25, dy-5), (dx+25, dy+5), (200, 200, 200), -1)
                cv2.line(frame, (dx-30, dy-8), (dx-15, dy-8), (180, 180, 180), 2)
                cv2.line(frame, (dx+15, dy-8), (dx+30, dy-8), (180, 180, 180), 2)

            def draw_package(px, py):
                cv2.rectangle(frame, (px-10, py), (px+10, py+14), (0, 0, 220), -1)

            if elapsed < 3.0:
                # 0-3s: Hovering, package hanging from rope, waiting
                pkg_y = drone_y + 45
                draw_drone(drone_x, drone_y)
                cv2.line(frame, (drone_x, drone_y+5), (drone_x, pkg_y), (150, 150, 150), 2)
                draw_package(drone_x, pkg_y)
                cv2.putText(frame, f"HOVERING ({elapsed:.0f}s)", (ax+10, ay+18),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)
            elif elapsed < 4.0:
                # 3-4s: STAGE 1 — fast drop! Package falls to ground in ~1s
                progress = (elapsed - 3.0) / 1.0  # 1 second drop
                pkg_y_start = drone_y + 45
                pkg_y = int(pkg_y_start + progress * (ground_y - pkg_y_start - 16))
                draw_drone(drone_x, drone_y)
                cv2.line(frame, (drone_x, drone_y+5), (drone_x, pkg_y), (150, 150, 150), 2)
                draw_package(drone_x, pkg_y)
                cv2.putText(frame, "STAGE 1 — DROP!", (ax+10, ay+18),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 165, 255), 2)
            elif elapsed < 6.0:
                # 4-6s: Package on ground, rope still attached
                draw_drone(drone_x, drone_y)
                cv2.line(frame, (drone_x, drone_y+5), (drone_x, ground_y-16), (150, 150, 150), 2)
                draw_package(drone_x, ground_y - 16)
                cv2.putText(frame, "STAGE 1 — DEPLOYED", (ax+10, ay+18),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 165, 255), 1)
            elif elapsed < 7.0:
                # 6-7s: STAGE 2 — rope detaches (disappears)
                draw_drone(drone_x, drone_y)
                draw_package(drone_x, ground_y - 16)
                cv2.putText(frame, "STAGE 2 — DETACHED", (ax+10, ay+18),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)
                cv2.putText(frame, "OK", (drone_x+15, ground_y-5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 2)
            elif elapsed < 15.0:
                # 7-15s: Drone hovering, package on ground, waiting
                draw_drone(drone_x, drone_y)
                draw_package(drone_x, ground_y - 16)
                cv2.putText(frame, "OK", (drone_x+15, ground_y-5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 2)
                cv2.putText(frame, f"COMPLETE ({15-elapsed:.0f}s)", (ax+10, ay+18),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 1)
            else:
                # 15s+: Drone flies off (visible for 2s then gone)
                fly_progress = min(1.0, (elapsed - 15.0) / 2.0)
                dy = int(drone_y - fly_progress * 30)
                dx = int(drone_x + fly_progress * 60)
                draw_drone(dx, dy)
                draw_package(drone_x, ground_y - 16)
                cv2.putText(frame, "OK", (drone_x+15, ground_y-5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 2)
                cv2.putText(frame, "DEPARTING", (ax+10, ay+18),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 1)

            # Timeline bar with stage markers
            bar_y = ay + ah - 10
            cv2.rectangle(frame, (ax+5, bar_y), (ax+aw-5, bar_y+6), (80, 80, 80), -1)
            progress = min(1.0, elapsed / 15.0)
            cv2.rectangle(frame, (ax+5, bar_y), (ax+5+int((aw-10)*progress), bar_y+5), (0, 255, 0), -1)

        # 4. COMPOSITE VIEW
        final_display = frame
        if config.MODE == "SIMULATION":
             god_frame = self.sim.get_god_view(
                px, py, self.yaw, self.view_w_px, self.view_h_px, self.zoom_level,
                self.planner.virtual_polygon, self.search_poly,
                (self.target_lat, self.target_lon), (self.landing_lat, self.landing_lon), self.geo,
                search_wps=self.waypoints, search_wp_index=self.wp_index,
                transit_wps_gps=self.pre_waypoints, transit_wp_index=self.pre_wp_index,
                current_state=self.state, rescan_pass=self.rescan_pass,
                items_of_interest=getattr(self, 'items_of_interest', None),
                rejected_targets=getattr(self, 'rejected_targets', None),
                nfz_buffer_m=(20.0 if (NFZ_SLOW or NFZ_CARROT) else self.geofence.SOFT_BOUNDARY) if self.geofence else 0,
                nfz_repulsion_vec=getattr(self, '_last_repulsion_vec', None),
                nfz_arrows=NFZ_ARROWS
            )


             h_scale = frame.shape[0] / god_frame.shape[0]
             god_resized = cv2.resize(god_frame, (int(god_frame.shape[1]*h_scale), frame.shape[0]))
             final_display = np.hstack((god_resized, frame))

        # Update stream for ground station (frame with HUD, before composite)
        if STREAM_ENABLED:
            set_stream_frame(frame)

        if not HEADLESS:
            cv2.imshow("Mission Dashboard", final_display)
        return found, u, v

    # ── Main loop ──────────────────────────────────────────────────────

    def run(self):
        print("Starting Mission Loop...")
        if STREAM_ENABLED:
            start_stream_server(port=STREAM_PORT, stream_w=STREAM_W,
                                stream_h=STREAM_H, stream_fps=STREAM_FPS,
                                stream_quality=STREAM_QUALITY)
        else:
            print("[STREAM] Disabled (--no-stream)")

        # Start terminal input thread (works over PuTTY/SSH)
        _input_thread = threading.Thread(target=_terminal_input_thread, daemon=True)
        _input_thread.start()

        if not HEADLESS:
            cv2.namedWindow("Mission Dashboard", cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
            if config.MODE == "SIMULATION":
                cv2.setMouseCallback("Mission Dashboard", self.on_dashboard_mouse)
        else:
            print("[HEADLESS] No display — use browser buttons or terminal keys (Y/N/M/E/W/S)")
            print(f"[HEADLESS] Browser: http://localhost:{STREAM_PORT}/")

        # State -> handler dispatch table
        _dispatch = {
            State.INIT:               self._handle_init,
            State.CONNECTING:         self._handle_connecting,
            State.ARMING:             self._handle_arming,
            State.TAKEOFF:            self._handle_takeoff,
            State.PRE_WAYPOINTS:      self._handle_pre_waypoints,
            State.TRANSIT_TO_SEARCH:  self._handle_transit_to_search,
            State.SEARCH:             self._handle_search,
            State.CENTERING:          self._handle_centering,
            State.DESCENDING:         self._handle_descending,
            State.VERIFY:             self._handle_verify,
            State.HOVER:              self._handle_hover,
            State.APPROACH:           self._handle_approach,
            State.HOVER_TARGET:       self._handle_hover_target,
            State.RETURN_TO_SEARCH:   self._handle_return_to_search,
            State.RETURN_FROM_MANUAL: self._handle_return_from_manual,
            State.RETURN_TRANSIT:     self._handle_return_transit,
            State.RETURN_HOME:        self._handle_return_home,
            State.LANDING:            self._handle_landing,
            # MANUAL and DONE have no handler — keys handle MANUAL, DONE is terminal
        }

        import queue as _queue
        key = -1
        while True:
            self.update_telemetry()
            target_found, px_u, px_v = self.update_dashboard()

            # Log data (~once per second)
            now = time.time()
            if now - self._last_log_time > 1.0:
                self.logger.writerow([datetime.now(), self.state, self.lat, self.lon, self.alt, self.current_conf])
                self.log_file.flush()
                self._last_log_time = now

            # Process key/button inputs (manual override, WASD, verify Y/N)
            self._handle_keys(key, target_found, px_u, px_v)

            # Dispatch to current state handler
            handler = _dispatch.get(self.state)
            if handler:
                handler(target_found, px_u, px_v, key)

            # Geofence check (runs after state dispatch)
            self._last_repulsion_vec = None
            if self.geofence and self.master and self.lat != 0 and self.state not in (
                    State.INIT, State.CONNECTING, State.ARMING, State.TAKEOFF,
                    State.LANDING, State.DONE):
                nfz_dist, nfz_inside = self.geofence.distance_to_boundary(self.lat, self.lon)
                if nfz_inside and self.state != State.MANUAL:
                    print(f"[GEOFENCE] INSIDE NFZ! Switching to MANUAL — fly out!")
                    self.previous_state = self.state
                    self._set_state(State.MANUAL)
                # NFZ_SLOW: velocity toward waypoint at capped speed (20m zone, SEARCH only)
                elif NFZ_SLOW and not nfz_inside and nfz_dist < 20.0 and self.state == State.SEARCH:
                    ratio = nfz_dist / 20.0
                    max_speed = 0.3 + ratio * (3.0 - 0.3)  # 0.3 at boundary → 3.0 at 20m edge
                    if hasattr(self, 'waypoints') and self.wp_index < len(self.waypoints) and self.nav:
                        wp = self.waypoints[self.wp_index]
                        lat_m = 111320.0
                        lon_m = 111320.0 * math.cos(math.radians(self.lat))
                        dn = (wp[0] - self.lat) * lat_m
                        de = (wp[1] - self.lon) * lon_m
                        dist_wp = math.sqrt(dn**2 + de**2)
                        if dist_wp > 0.5:
                            self.nav.send_velocity(dn / dist_wp * max_speed, de / dist_wp * max_speed, 0, current_yaw=0.0)
                        else:
                            self.nav.send_velocity(0, 0, 0, current_yaw=0.0)
                    off_lat, off_lon = self.geofence.repulsive_offset(self.lat, self.lon)
                    if abs(off_lat) > 1e-8 or abs(off_lon) > 1e-8:
                        self._last_repulsion_vec = (off_lat, off_lon)

                # NFZ_CARROT: speed-cap scalar field (20m zone, ALL states)
                # Direction comes from normal navigation — only speed is capped
                elif NFZ_CARROT and not nfz_inside and nfz_dist < 20.0:
                    ratio = nfz_dist / 20.0
                    max_speed = 0.3 + ratio * (3.0 - 0.3)  # 0.3 at boundary → 3.0 at 20m edge
                    self.nav.last_speed_req = 0  # bypass 3s throttle
                    self.nav.set_speed(max_speed)

                # NFZ_REPEL: push away (8m zone)
                elif NFZ_REPEL and not nfz_inside and nfz_dist < self.geofence.SOFT_BOUNDARY:
                    off_lat, off_lon = self.geofence.repulsive_offset(self.lat, self.lon)
                    if abs(off_lat) > 1e-8 or abs(off_lon) > 1e-8:
                        self._last_repulsion_vec = (off_lat, off_lon)
                        urgency = (1.0 - nfz_dist / self.geofence.SOFT_BOUNDARY) ** 2  # quadratic
                        nudge_speed = 10.0 * urgency
                        lat_m = 111320.0
                        lon_m = 111320.0 * math.cos(math.radians(self.lat))
                        push_n = -off_lat * lat_m
                        push_e = -off_lon * lon_m
                        mag = math.sqrt(push_n**2 + push_e**2)
                        if mag > 0.01 and self.nav:
                            vn = push_n / mag * nudge_speed
                            ve = push_e / mag * nudge_speed
                            self.nav.send_velocity(vn, ve, 0, current_yaw=0.0)

            # Exit loop when mission is complete (show final frame for 3s then quit)
            if self.state == State.DONE:
                if not HEADLESS:
                    cv2.waitKey(3000)
                else:
                    time.sleep(3.0)
                break

            # Read key from cv2 (if display) or command queue (terminal/HTTP)
            key = -1
            if not HEADLESS:
                key = cv2.waitKey(20) & 0xFF
                if key == 27: break
            else:
                time.sleep(0.02)
            # Drain command queue (from terminal keys or browser buttons)
            try:
                while True:
                    queued_key = stream_cmd_queue.get_nowait()
                    key = queued_key  # last one wins this frame
            except _queue.Empty:
                pass
            if key == 27: break

    def on_dashboard_mouse(self, event, x, y, flags, param):
        if event == cv2.EVENT_MOUSEWHEEL:
            if flags > 0: self.zoom_level = min(self.zoom_level * 1.2, 20.0)
            else: self.zoom_level = max(self.zoom_level / 1.2, 1.0)


def _dry_run(mission):
    """Dry-run mode: generate lawnmower pattern from SEARCH_AREA_GPS, display it, exit.
    No Cube connection, no GPS, no arming. Tests the planning pipeline only."""
    print()
    print("=" * 60)
    print("  DRY-RUN: Generating lawnmower search pattern")
    print("=" * 60)

    # Use SEARCH_AREA_GPS coordinates
    if not mission.search_poly or len(mission.search_poly) < 3:
        print("  ERROR: No search polygon defined!")
        print("  Set SEARCH_AREA_GPS in config.py with at least 3 GPS corners.")
        return

    # Show search area GPS corners
    print(f"\n  Search area ({len(mission.search_poly)} corners):")
    for i, pt in enumerate(mission.search_poly):
        gps = mission.geo.pixels_to_gps(pt[0], pt[1]) if hasattr(pt, '__len__') else (0, 0)
        print(f"    Corner {i+1}: pixel=({pt[0]:.0f}, {pt[1]:.0f})  GPS=({gps[0]:.6f}, {gps[1]:.6f})")

    # Generate pattern from current position (use REF_LAT/LON as "drone position")
    drone_gps = (config.REF_LAT, config.REF_LON)
    print(f"\n  Drone start position (config REF): ({drone_gps[0]:.6f}, {drone_gps[1]:.6f})")
    print(f"  Target altitude: {config.TARGET_ALT}m")
    print(f"  Search speed: {config.SEARCH_SPEED_MPS} m/s")
    print(f"  Transit speed: {config.TRANSIT_SPEED_MPS} m/s")
    print(f"  Model: {MODEL_PATH}")

    canvas_w, canvas_h = REAL_CANVAS_SIZE, REAL_CANVAS_SIZE
    print(f"  Search pattern: {SEARCH_PATTERN}")
    if SEARCH_PATTERN == "spiral":
        waypoints = mission.planner.generate_spiral_pattern(canvas_w, canvas_h, drone_gps)
    else:
        waypoints = mission.planner.generate_search_pattern(canvas_w, canvas_h, drone_gps)

    if not waypoints:
        print("\n  ERROR: No waypoints generated! Check search polygon.")
        return

    print(f"\n  Generated {len(waypoints)} waypoints:")
    total_dist = 0
    for i, wp in enumerate(waypoints):
        if i > 0:
            prev = waypoints[i - 1]
            d = 111320 * math.sqrt(
                (wp[0] - prev[0]) ** 2 +
                ((wp[1] - prev[1]) * math.cos(math.radians(wp[0]))) ** 2)
            total_dist += d
        marker = " ← START" if i == 0 else (" ← END" if i == len(waypoints) - 1 else "")
        print(f"    WP {i+1:3d}: ({wp[0]:.6f}, {wp[1]:.6f}){marker}")

    # Distance from drone to first waypoint
    wp0 = waypoints[0]
    transit_dist = 111320 * math.sqrt(
        (wp0[0] - drone_gps[0]) ** 2 +
        ((wp0[1] - drone_gps[1]) * math.cos(math.radians(drone_gps[0]))) ** 2)

    print(f"\n  Transit to start: {transit_dist:.0f}m ({transit_dist/config.TRANSIT_SPEED_MPS:.0f}s at {config.TRANSIT_SPEED_MPS} m/s)")
    print(f"  Search path length: {total_dist:.0f}m ({total_dist/config.SEARCH_SPEED_MPS:.0f}s at {config.SEARCH_SPEED_MPS} m/s)")
    total_time = transit_dist / config.TRANSIT_SPEED_MPS + total_dist / config.SEARCH_SPEED_MPS
    print(f"  Estimated flight time: {total_time:.0f}s ({total_time/60:.1f} min)")

    # Simulate the state machine transitions (print only)
    print(f"\n  State machine walkthrough:")
    print(f"    INIT -> connect to {config.CONNECTION_STR}")
    print(f"    CONNECTING -> wait for heartbeat")
    print(f"    ARMING -> wait for GPS fix (fix_type>=3, sats>=6)")
    print(f"    ARMING -> set GUIDED mode")
    print(f"    ARMING -> arm motors")
    print(f"    TAKEOFF -> climb to {config.TARGET_ALT}m")
    print(f"    TRANSIT_TO_SEARCH -> fly to WP 1 ({waypoints[0][0]:.6f}, {waypoints[0][1]:.6f})")
    print(f"    SEARCH -> fly {len(waypoints)} waypoints in lawnmower pattern")
    print(f"    (on detection) CENTERING -> center target in camera frame")
    print(f"    DESCENDING -> descend to {config.VERIFY_ALT}m")
    print(f"    VERIFY -> operator confirms Y/N")
    print(f"    APPROACH -> fly to landing point")
    print(f"    LANDING -> land and disarm")

    # Try to visualize on map if available
    map_img = cv2.imread(config.MAP_FILE)
    if map_img is not None:
        vis = map_img.copy()
        # Draw search polygon
        poly_pts = np.array(mission.search_poly, np.int32)
        cv2.polylines(vis, [poly_pts], True, (0, 255, 0), 2)

        # Draw waypoints
        for i, wp in enumerate(waypoints):
            px = mission.geo.gps_to_pixels(wp[0], wp[1])
            pt = (int(px[0]), int(px[1]))
            color = (0, 0, 255) if i == 0 else ((255, 0, 0) if i == len(waypoints) - 1 else (255, 255, 0))
            cv2.circle(vis, pt, 4, color, -1)
            if i > 0:
                prev_px = mission.geo.gps_to_pixels(waypoints[i-1][0], waypoints[i-1][1])
                cv2.line(vis, (int(prev_px[0]), int(prev_px[1])), pt, (255, 255, 0), 1)

        # Draw drone start
        drone_px = mission.geo.gps_to_pixels(drone_gps[0], drone_gps[1])
        cv2.drawMarker(vis, (int(drone_px[0]), int(drone_px[1])), (0, 255, 255),
                        cv2.MARKER_DIAMOND, 15, 2)

        # Labels
        cv2.putText(vis, "DRY-RUN: Lawnmower Pattern", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.putText(vis, f"{len(waypoints)} WPs, {total_dist:.0f}m, ~{total_time/60:.1f}min",
                    (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        cv2.putText(vis, "Green=polygon  Yellow=path  Red=start  Blue=end  Diamond=drone",
                    (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

        # Scale for display
        max_h = 900
        scale = min(1.0, max_h / vis.shape[0])
        if scale < 1.0:
            vis = cv2.resize(vis, (int(vis.shape[1] * scale), int(vis.shape[0] * scale)))

        cv2.imshow("Dry-Run: Search Pattern", vis)
        print(f"\n  Map visualization shown. Press any key to close.")
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        # Save image
        out_path = "dry_run_pattern.jpg"
        cv2.imwrite(out_path, vis)
        print(f"  Pattern saved to: {out_path}")
    else:
        print(f"\n  (No map.jpg found — skipping visualization)")

    print()
    print("  DRY-RUN COMPLETE. No commands were sent.")
    print("  To fly for real: python main.py (without --dry-run)")
    print("=" * 60)


if __name__ == "__main__":
    mission = VisualFlightMission()
    if DRY_RUN:
        _dry_run(mission)
    else:
        try:
            mission.run()
        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError) as e:
            print(f"\n[LINK LOST] Connection to Cube dropped: {e}")
            print("  If SITL: restart Mission Planner simulation")
            print("  If real: check mavproxy and serial cable")
        except KeyboardInterrupt:
            print("\n[USER] Mission aborted by Ctrl+C")
        finally:
            if hasattr(mission, 'log_file') and mission.log_file:
                mission.log_file.close()
            cv2.destroyAllWindows()
