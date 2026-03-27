# main.py — Mission Orchestrator (state machine, telemetry, HUD, dry-run)
from pymavlink import mavutil
import time, math, cv2, csv, sys, os, threading
import numpy as np
from datetime import datetime

try:
    import config
    if not hasattr(config, 'MODE'):
        print("[ERROR] Wrong 'config' module! Rename local config.py to avoid conflict.")
        sys.exit(1)
except ImportError:
    print("[ERROR] Could not import 'config.py'.")
    sys.exit(1)

from states import State
from utils import GeoTransformer
from planning import PathPlanner
from vision import VisionSystem
from state_machine import StateHandlersMixin
from navigation import NavigationController
from stream_server import (start_stream_server, set_stream_frame,
                           get_stream_frame, cmd_queue as stream_cmd_queue)
from gps_utils import calculate_target_from_pixels, landing_offset_7_5m

if config.MODE == "SIMULATION":
    from simulator.simulation import SimulationEnvironment

# ── CLI flags & config ────────────────────────────────────────────────
REAL_CANVAS_SIZE = 4800
DRY_RUN = "--dry-run" in sys.argv
MODEL_PATH = "best.tflite"
TRANSIT_FILE = "flight_plans/transit.json"
_TRANSIT_EXPLICIT = False
STREAM_ENABLED = "--no-stream" not in sys.argv
STREAM_PORT = 8090
STREAM_W, STREAM_H = 320, 240
STREAM_FPS = 5
STREAM_QUALITY = 50
SIM_SPEED = 1
CENTER_VERIFY = "--center-verify" in sys.argv
SMART_DETECT = "--smart-detect" in sys.argv
NO_NFZ = "--no-nfz" in sys.argv
BEACON_DELAY = 0

for _i, _arg in enumerate(sys.argv):
    if _arg == "--model" and _i + 1 < len(sys.argv):        MODEL_PATH = sys.argv[_i + 1]
    elif _arg == "--transit" and _i + 1 < len(sys.argv):     TRANSIT_FILE = sys.argv[_i + 1]; _TRANSIT_EXPLICIT = True
    elif _arg == "--speed" and _i + 1 < len(sys.argv):       SIM_SPEED = float(sys.argv[_i + 1])
    elif _arg == "--alt" and _i + 1 < len(sys.argv):         config.TARGET_ALT = float(sys.argv[_i + 1])
    elif _arg == "--beacon-delay" and _i + 1 < len(sys.argv): BEACON_DELAY = float(sys.argv[_i + 1])

if DRY_RUN:
    print("=" * 60)
    print("  DRY-RUN MODE — No arming, no flying, no GPS needed")
    print("=" * 60)

HEADLESS = "--headless" in sys.argv
if not HEADLESS:
    try:
        if os.environ.get('DISPLAY', '') == '' and sys.platform != 'win32':
            HEADLESS = True
    except Exception:
        HEADLESS = True


def _terminal_input_thread():
    """Read keypresses from terminal (PuTTY/SSH). Feeds into stream_cmd_queue."""
    import select
    if sys.platform == 'win32':
        import msvcrt
        while True:
            if msvcrt.kbhit():
                stream_cmd_queue.put(msvcrt.getch()[0])
            time.sleep(0.05)
    else:
        import tty, termios
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setcbreak(fd)
            while True:
                if select.select([sys.stdin], [], [], 0.05)[0]:
                    ch = sys.stdin.read(1)
                    if ch: stream_cmd_queue.put(ord(ch))
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)


# ── Servo animation helper ───────────────────────────────────────────

def _draw_servo_animation(frame, elapsed):
    """Draw payload drop animation in bottom-right corner during HOVER_TARGET."""
    h, w = frame.shape[:2]
    ax, ay, aw, ah = w - 270, h - 200, 250, 180
    ground_y = ay + ah - 25
    drone_x, drone_y = ax + aw // 2, ay + 35

    # Background
    cv2.rectangle(frame, (ax, ay), (ax+aw, ay+ah), (180, 130, 80), -1)
    cv2.rectangle(frame, (ax, ground_y), (ax+aw, ay+ah), (50, 120, 50), -1)
    cv2.rectangle(frame, (ax, ay), (ax+aw, ay+ah), (255, 255, 255), 1)

    def draw_drone(dx, dy):
        cv2.rectangle(frame, (dx-25, dy-5), (dx+25, dy+5), (200, 200, 200), -1)
        cv2.line(frame, (dx-30, dy-8), (dx-15, dy-8), (180, 180, 180), 2)
        cv2.line(frame, (dx+15, dy-8), (dx+30, dy-8), (180, 180, 180), 2)

    def draw_pkg(px, py):
        cv2.rectangle(frame, (px-10, py), (px+10, py+14), (0, 0, 220), -1)

    if elapsed < 3.0:
        pkg_y = drone_y + 45
        draw_drone(drone_x, drone_y)
        cv2.line(frame, (drone_x, drone_y+5), (drone_x, pkg_y), (150, 150, 150), 2)
        draw_pkg(drone_x, pkg_y)
        label, color = f"HOVERING ({elapsed:.0f}s)", (255, 255, 255)
    elif elapsed < 4.0:
        progress = (elapsed - 3.0)
        pkg_y = int((drone_y + 45) + progress * (ground_y - (drone_y + 45) - 16))
        draw_drone(drone_x, drone_y)
        cv2.line(frame, (drone_x, drone_y+5), (drone_x, pkg_y), (150, 150, 150), 2)
        draw_pkg(drone_x, pkg_y)
        label, color = "STAGE 1 — DROP!", (0, 165, 255)
    elif elapsed < 6.0:
        draw_drone(drone_x, drone_y)
        cv2.line(frame, (drone_x, drone_y+5), (drone_x, ground_y-16), (150, 150, 150), 2)
        draw_pkg(drone_x, ground_y - 16)
        label, color = "STAGE 1 — DEPLOYED", (0, 165, 255)
    elif elapsed < 7.0:
        draw_drone(drone_x, drone_y)
        draw_pkg(drone_x, ground_y - 16)
        cv2.putText(frame, "OK", (drone_x+15, ground_y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0,255,0), 2)
        label, color = "STAGE 2 — DETACHED", (0, 0, 255)
    elif elapsed < 15.0:
        draw_drone(drone_x, drone_y)
        draw_pkg(drone_x, ground_y - 16)
        cv2.putText(frame, "OK", (drone_x+15, ground_y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0,255,0), 2)
        label, color = f"COMPLETE ({15-elapsed:.0f}s)", (0, 255, 0)
    else:
        fp = min(1.0, (elapsed - 15.0) / 2.0)
        draw_drone(int(drone_x + fp * 60), int(drone_y - fp * 30))
        draw_pkg(drone_x, ground_y - 16)
        cv2.putText(frame, "OK", (drone_x+15, ground_y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0,255,0), 2)
        label, color = "DEPARTING", (0, 255, 0)

    cv2.putText(frame, label, (ax+10, ay+18), cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1)
    # Timeline bar
    bar_y = ay + ah - 10
    cv2.rectangle(frame, (ax+5, bar_y), (ax+aw-5, bar_y+6), (80, 80, 80), -1)
    prog = min(1.0, elapsed / 15.0)
    cv2.rectangle(frame, (ax+5, bar_y), (ax+5+int((aw-10)*prog), bar_y+5), (0, 255, 0), -1)


# ══════════════════════════════════════════════════════════════════════

class VisualFlightMission(StateHandlersMixin):
    def __init__(self):
        print(f"--- INITIALIZING IN {config.MODE} MODE ---")

        if not config.load_kml_zones():
            print("[WARN] KML load failed — using fallback GPS from config.py")

        # Simulation or Real setup
        if config.MODE == "SIMULATION":
            self.sim = SimulationEnvironment(GeoTransformer(map_w_px=100))
            self.geo = GeoTransformer(map_w_px=self.sim.map_w)
            self.sim.geo = self.geo
            preload_gps = config.SEARCH_AREA_GPS
            preload_transit = self._load_transit_from_file()
            self.target_px, self.tgt_type, self.search_poly, transit_px, focus_px = \
                self.sim.setup_on_map(preload_polygon_gps=preload_gps, preload_transit_gps=preload_transit)

            if focus_px and len(focus_px) >= 3:
                config.FOCUS_AREA_GPS = [self.geo.pixels_to_gps(px[0], px[1]) for px in focus_px]
                import json
                os.makedirs("flight_plans", exist_ok=True)
                with open("flight_plans/focus_area.json", "w") as f:
                    json.dump([{"lat": pt[0], "lon": pt[1], "label": f"F{i+1}"}
                               for i, pt in enumerate(config.FOCUS_AREA_GPS)], f, indent=2)
                print(f"  Focus Area: {len(config.FOCUS_AREA_GPS)} points saved")

            self._drawn_transit_gps = (
                [self.geo.pixels_to_gps(px[0], px[1]) for px in transit_px]
                if transit_px and not preload_transit else [])

            self.eyes = VisionSystem(camera_index=None, model_path=MODEL_PATH)
            self.eyes.using_ai = (self.tgt_type == "dummy") and self.eyes.model is not None
        else:
            self.sim = None
            self.search_poly = self._setup_real_search_area()
            cam_idx = None if DRY_RUN else config.REAL_CAMERA_INDEX
            self.eyes = VisionSystem(camera_index=cam_idx, model_path=MODEL_PATH)
            self.eyes.using_ai = True

        # Geofence
        self.geofence = None
        if not NO_NFZ and config.SSSI_GPS and len(config.SSSI_GPS) >= 3:
            from geofence import NFZGeofence
            self.geofence = NFZGeofence(self.geo)
            print(f"[GEOFENCE] Active — {len(config.SSSI_GPS)} corners, "
                  f"hard={self.geofence.HARD_BOUNDARY}m, soft={self.geofence.SOFT_BOUNDARY}m")

        # Planner
        self.planner = PathPlanner(self.geo, self.search_poly)
        self.planner._no_turn = True

        # Connection
        self.master = None
        self.last_req = 0
        self.last_heartbeat = 0
        self.nav = None

        # State & telemetry
        self.state = State.INIT
        self.previous_state = State.HOVER
        self.state_start_time = time.time()
        self.connect_start_time = 0
        self.gps_fix_ok = False
        self.gps_fix_type = 0
        self.gps_satellites = 0
        self._gps_degraded_time = 0       # when fix first dropped below 3D
        self._gps_warn_printed = 0        # throttle warnings
        self._last_gps_status_print = 0
        self._last_mode_warn = -1
        self._arming_timeout_warned = False
        self._takeoff_timeout_warned = False
        self._centering_timeout_warned = False
        self._descending_timeout_warned = False
        self._last_log_time = 0
        self._servo_released = False
        self._camera_none_count = 0
        self._last_camera_warn = 0

        if config.TAKEOFF_GPS:
            self.lat, self.lon = config.TAKEOFF_GPS[0], config.TAKEOFF_GPS[1]
        else:
            self.lat, self.lon = config.REF_LAT, config.REF_LON
        self.home_lat, self.home_lon = self.lat, self.lon
        self.return_wp_index = 0
        self.alt = 0.0
        self.vx = 0; self.vy = 0; self.vz = 0
        self.roll = 0; self.pitch = 0; self.yaw = 0

        # Mission data
        if not hasattr(self, 'waypoints'): self.waypoints = []
        self.wp_index = 0
        self.target_lat = 0; self.target_lon = 0
        self.landing_lat = 0; self.landing_lon = 0
        self.current_conf = 0.0
        self.final_dist = 0.0
        self.rejected_targets = []
        self.departure_lat = 0; self.departure_lon = 0
        self.manual_departure_lat = 0; self.manual_departure_lon = 0; self.manual_departure_alt = 0
        self.max_rescan_passes = config.MAX_RESCAN_PASSES
        self.rescan_pass = 0

        # Pre-planned waypoints (transit before search)
        self.pre_waypoints = []
        self.pre_wp_index = 0
        if TRANSIT_FILE and os.path.exists(TRANSIT_FILE):
            try:
                wps = self._load_waypoints_json(TRANSIT_FILE)
                self.pre_waypoints.extend(wps)
                print(f"  Transit: {len(wps)} points from {TRANSIT_FILE}")
            except Exception as e:
                print(f"WARNING: Failed to load {TRANSIT_FILE}: {e}")
        if hasattr(self, '_drawn_transit_gps') and self._drawn_transit_gps:
            self.pre_waypoints.extend(self._drawn_transit_gps)

        # Generate search waypoints
        if self.search_poly and len(self.search_poly) >= 3:
            cw = self.sim.map_w if config.MODE == "SIMULATION" else REAL_CANVAS_SIZE
            ch = self.sim.map_h if config.MODE == "SIMULATION" else REAL_CANVAS_SIZE
            start_ref = self.pre_waypoints[-1] if self.pre_waypoints else None
            self.waypoints = self.planner.generate_search_pattern(cw, ch, start_ref)
            print(f"  Search: {len(self.waypoints)} waypoints")

        # UI helpers
        self.view_w_px = 100; self.view_h_px = 100; self.zoom_level = 1.0
        self.waiting_for_confirmation = False
        self.selecting_landing_side = False

        # CSV logging
        os.makedirs(os.path.dirname(config.LOG_FILE) or ".", exist_ok=True)
        self.log_file = open(config.LOG_FILE, 'w', newline='')
        self.logger = csv.writer(self.log_file)
        self.logger.writerow(["Timestamp", "State", "Lat", "Lon", "Alt", "Target_Conf"])

    @staticmethod
    def _load_waypoints_json(path):
        """Load waypoints from JSON — supports [{lat,lon},...] and [[lat,lon],...]."""
        import json
        with open(path) as f:
            data = json.load(f)
        return [(wp["lat"], wp["lon"]) if isinstance(wp, dict) else (wp[0], wp[1])
                for wp in data]

    def _load_transit_from_file(self):
        """Load transit waypoints from JSON file (simulation preload)."""
        if not TRANSIT_FILE or not os.path.exists(TRANSIT_FILE):
            return None
        try:
            wps = self._load_waypoints_json(TRANSIT_FILE)
            print(f"  Transit path: {len(wps)} points from {TRANSIT_FILE}")
            return wps
        except Exception as e:
            print(f"WARNING: Failed to load transit from {TRANSIT_FILE}: {e}")
            return None

    def _setup_real_search_area(self):
        """Load search area from search_area.json, config GPS, or fallback."""
        self.geo = GeoTransformer(map_w_px=REAL_CANVAS_SIZE)
        sa_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "flight_plans", "search_area.json")
        if os.path.exists(sa_file):
            import json
            with open(sa_file, "r") as f:
                data = json.load(f)
            if data and len(data) >= 3:
                gps_coords = [(pt["lat"], pt["lon"]) for pt in data]
                poly = [self.geo.gps_to_pixels(lat, lon) for lat, lon in gps_coords]
                print(f"[REAL] Search area: {len(poly)} points from search_area.json")
                return poly
        if hasattr(config, 'SEARCH_AREA_GPS') and len(config.SEARCH_AREA_GPS) >= 3:
            poly = [self.geo.gps_to_pixels(lat, lon) for lat, lon in config.SEARCH_AREA_GPS]
            print(f"[REAL] Search area: {len(poly)} points from config/KML")
            return poly
        print("[REAL] No search area — run draw_search_area.py or set SEARCH_AREA_GPS")
        return []

    # ── Telemetry ─────────────────────────────────────────────────────

    def update_telemetry(self):
        if not self.master: return
        while True:
            try:
                msg = self.master.recv_match(blocking=False)
            except (ConnectionResetError, ConnectionAbortedError,
                    BrokenPipeError, OSError) as e:
                print(f"\n[LINK LOST] recv_match failed: {e}")
                self._emergency_rtl(reason=str(e))
                self.state = State.DONE
                return
            if not msg: break
            mtype = msg.get_type()
            if mtype == 'GLOBAL_POSITION_INT':
                self.lat = msg.lat / 1e7; self.lon = msg.lon / 1e7
                self.alt = msg.relative_alt / 1000.0
                self.vx = msg.vx / 100.0; self.vy = msg.vy / 100.0; self.vz = msg.vz / 100.0
            elif mtype == 'ATTITUDE':
                self.roll = msg.roll; self.pitch = msg.pitch; self.yaw = msg.yaw
            elif mtype == 'HEARTBEAT' and msg.type != mavutil.mavlink.MAV_TYPE_GCS:
                self.last_heartbeat = time.time()
                if self.master.target_system == 0:
                    self.master.target_system = msg.get_srcSystem()
                    self.master.target_component = msg.get_srcComponent()
                    print(f"[LINK] Autopilot found: system {self.master.target_system}")
                if hasattr(msg, 'custom_mode') and self.state not in (
                        State.MANUAL, State.DONE, State.INIT, State.CONNECTING):
                    if msg.custom_mode != 4 and self._last_mode_warn != msg.custom_mode:
                        modes = {0:'STABILIZE',2:'ALT_HOLD',3:'AUTO',4:'GUIDED',
                                 5:'LOITER',6:'RTL',9:'LAND',16:'POSHOLD'}
                        print(f"WARNING: Cube in {modes.get(msg.custom_mode, f'MODE_{msg.custom_mode}')} (not GUIDED)")
                        self._last_mode_warn = msg.custom_mode

    # ── GPS math wrappers ─────────────────────────────────────────────

    def calculate_target_gps(self, u, v):
        self.target_lat, self.target_lon = calculate_target_from_pixels(
            u, v, self.alt, self.yaw, self.lat, self.lon,
            config.IMAGE_W, config.IMAGE_H, config.SENSOR_WIDTH_MM, config.FOCAL_LENGTH_MM)
        print(f"[VISION] Target GPS: {self.target_lat:.6f}, {self.target_lon:.6f}")

    def calculate_landing_spot(self, direction_key):
        self.landing_lat, self.landing_lon = landing_offset_7_5m(
            self.target_lat, self.target_lon, direction_key)
        print(f"Landing Spot: {direction_key.upper()} of target")

    # ── Dashboard / HUD ───────────────────────────────────────────────

    def update_dashboard(self):
        found = False; u = 0; v = 0; conf = 0.0

        # Get frame
        if config.MODE == "SIMULATION":
            px, py = self.geo.gps_to_pixels(self.lat, self.lon)
            frame, self.view_w_px, self.view_h_px = self.sim.get_drone_view(px, py, self.alt, self.yaw)
        else:
            frame = self.eyes.get_frame()
            if frame is None:
                frame = np.zeros((config.IMAGE_H, config.IMAGE_W, 3), dtype=np.uint8)

        found, u, v, conf = self.eyes.process_frame_manually(frame)
        self.current_conf = conf

        # HUD overlay
        cx, cy = config.IMAGE_W // 2, config.IMAGE_H // 2
        cv2.line(frame, (cx-20, cy), (cx+20, cy), (0,255,255), 2)
        cv2.line(frame, (cx, cy-20), (cx, cy+20), (0,255,255), 2)
        if found:
            cv2.circle(frame, (u,v), 15, (0,255,0), 2)
            cv2.line(frame, (u,v), (cx,cy), (0,255,0), 2)
            cv2.putText(frame, f"TGT {conf:.2f}", (u+10,v), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)

        # Info panel
        F = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, f"MODE: {config.MODE}", (10,20), F, 0.6, (0,0,255), 2)
        cv2.putText(frame, f"STATE: {self.state}", (10,50), F, 0.6, (255,255,0), 2)
        cv2.putText(frame, f"ALT: {self.alt:.1f}m", (10,80), F, 0.6, (255,255,0), 2)
        spd = math.sqrt(self.vx**2 + self.vy**2)
        cv2.putText(frame, f"POS: {self.lat:.6f}, {self.lon:.6f}  SPD: {spd:.1f}m/s", (10,110), F, 0.6, (255,255,255), 2)
        if self.target_lat != 0:
            cv2.putText(frame, f"TARGET: {self.target_lat:.6f}, {self.target_lon:.6f}", (10,140), F, 0.6, (0,255,0), 2)
        if self.landing_lat != 0:
            cv2.putText(frame, f"LANDING: {self.landing_lat:.6f}, {self.landing_lon:.6f}", (10,170), F, 0.6, (0,255,255), 2)
        mname = os.path.basename(MODEL_PATH)
        cv2.putText(frame, f"MODEL: {mname}", (10,170 if self.landing_lat == 0 else 200), F, 0.6, (0,255,255), 2)

        # State-specific HUD
        if self.state == State.HOVER_TARGET:
            elapsed = time.time() - self.state_start_time
            rem = max(0, 15.0 - elapsed)
            if elapsed < 3.0:
                cv2.putText(frame, f"HOVERING — waiting ({3.0-elapsed:.0f}s)", (cx-200, cy+60), F, 0.8, (0,255,255), 2)
            elif elapsed < 6.0:
                if int(elapsed*3)%2==0:
                    cv2.putText(frame, "PHASE 1 RELEASED", (cx-180, cy-30), F, 1.2, (0,165,255), 3)
                cv2.putText(frame, f"Phase 2 in {6.0-elapsed:.0f}s", (cx-100, cy+60), F, 0.7, (255,255,255), 2)
            elif elapsed < 15.0:
                if int(elapsed*3)%2==0:
                    cv2.putText(frame, "PHASE 2 RELEASED", (cx-180, cy-30), F, 1.2, (0,0,255), 3)
                cv2.putText(frame, f"Departing in {15.0-elapsed:.0f}s", (cx-120, cy+60), F, 0.7, (0,255,255), 2)

        if self.state == State.MANUAL:
            cv2.putText(frame, "MANUAL OVERRIDE", (cx-150, cy-30), F, 1.0, (0,165,255), 3)
            cv2.putText(frame, "WASD=fly R/F=alt Q/E=yaw M=resume", (cx-220, cy+20), F, 0.6, (0,165,255), 2)

        if self.state == State.DONE:
            cv2.putText(frame, f"FINAL ERROR: {self.final_dist:.2f} m", (cx-150, cy), F, 1.0, (0,0,255), 3)

        if self.waiting_for_confirmation:
            if self.selecting_landing_side:
                cv2.putText(frame, "SELECT LANDING SIDE:", (cx-200, cy+60), F, 0.8, (0,255,255), 2)
                cv2.putText(frame, "N/S/W/E", (cx-60, cy+90), F, 0.8, (0,255,255), 2)
            else:
                cv2.putText(frame, "Y=Confirm  N=Reject  I=Interest", (cx-200, cy+80), F, 0.8, (0,0,255), 2)

        if hasattr(self, 'items_of_interest') and self.items_of_interest:
            y_off = frame.shape[0] - 30 * len(self.items_of_interest) - 10
            for idx, item in enumerate(self.items_of_interest):
                cv2.putText(frame, f"I{idx+1}: ({item['lat']:.5f}, {item['lon']:.5f})",
                            (10, y_off + idx*30), F, 0.6, (255,100,0), 2)

        # Servo animation (HOVER_TARGET only)
        if self.state == State.HOVER_TARGET and hasattr(self, '_hover_elapsed'):
            _draw_servo_animation(frame, self._hover_elapsed)

        # Composite view (simulation: god view + camera side by side)
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
                nfz_buffer_m=config.NFZ_SLOW_ZONE_M if self.geofence else 0,
                nfz_repulsion_vec=getattr(self, '_last_repulsion_vec', None),
            )
            h_scale = frame.shape[0] / god_frame.shape[0]
            god_resized = cv2.resize(god_frame, (int(god_frame.shape[1]*h_scale), frame.shape[0]))
            final_display = np.hstack((god_resized, frame))

        if STREAM_ENABLED:
            set_stream_frame(frame)
        if not HEADLESS:
            cv2.imshow("Mission Dashboard", final_display)
        return found, u, v

    # ── Main loop ─────────────────────────────────────────────────────

    def run(self):
        print("Starting Mission Loop...")
        if STREAM_ENABLED:
            srv = start_stream_server(port=STREAM_PORT, stream_w=STREAM_W, stream_h=STREAM_H,
                                      stream_fps=STREAM_FPS, stream_quality=STREAM_QUALITY)
            if srv is None:
                print("=" * 60)
                print("WARNING: Stream server failed to start!")
                print("  No video feed or web buttons available.")
                print("  Kill any other script using the port and restart.")
                print("=" * 60)

        threading.Thread(target=_terminal_input_thread, daemon=True).start()

        if not HEADLESS:
            cv2.namedWindow("Mission Dashboard", cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
            if config.MODE == "SIMULATION":
                cv2.setMouseCallback("Mission Dashboard", self.on_dashboard_mouse)
        else:
            print(f"[HEADLESS] Browser: http://localhost:{STREAM_PORT}/")

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
        }

        import queue as _queue
        key = -1
        while True:
            self.update_telemetry()
            target_found, px_u, px_v = self.update_dashboard()

            # Log ~1 Hz
            now = time.time()
            if now - self._last_log_time > 1.0:
                self.logger.writerow([datetime.now(), self.state, self.lat, self.lon, self.alt, self.current_conf])
                self.log_file.flush()
                self._last_log_time = now

            self._handle_keys(key, target_found, px_u, px_v)

            handler = _dispatch.get(self.state)
            if handler:
                handler(target_found, px_u, px_v, key)

            # Geofence enforcement
            self._last_repulsion_vec = None
            if (self.geofence and self.master and self.lat != 0
                    and self.state not in (State.INIT, State.CONNECTING, State.ARMING,
                                           State.TAKEOFF, State.LANDING, State.DONE)):
                self._enforce_geofence()

            if self.state == State.DONE:
                (cv2.waitKey(3000) if not HEADLESS else time.sleep(3.0))
                break

            key = -1
            if not HEADLESS:
                key = cv2.waitKey(20) & 0xFF
                if key == 27: break
            else:
                time.sleep(0.02)
            try:
                while True:
                    key = stream_cmd_queue.get_nowait()
            except _queue.Empty:
                pass
            if key == 27: break

    def _enforce_geofence(self):
        """NFZ speed cap + inner polygon repulsion."""
        nfz_dist, nfz_inside = self.geofence.distance_to_boundary(self.lat, self.lon)

        if nfz_inside and self.state != State.MANUAL:
            print(f"[GEOFENCE] INSIDE NFZ! Switching to MANUAL")
            if self.state != State.RETURN_FROM_MANUAL:
                self.previous_state = self.state
                self.manual_departure_lat = self.lat
                self.manual_departure_lon = self.lon
                self.manual_departure_alt = self.alt
            self._set_state(State.MANUAL)
            if self.nav: self.nav.send_velocity(0, 0, 0)
            return

        if not nfz_inside and nfz_dist < config.NFZ_SLOW_ZONE_M:
            ratio = nfz_dist / config.NFZ_SLOW_ZONE_M
            max_spd = config.NFZ_MIN_SPEED_MPS + ratio * (config.NFZ_ZONE_MAX_SPEED_MPS - config.NFZ_MIN_SPEED_MPS)
            self.nav.last_speed_req = 0
            self.nav.set_speed(max_spd)

        if self.nav:
            signed_dist = nfz_dist if not nfz_inside else -nfz_dist
            dist_to_inner = signed_dist + config.NFZ_INNER_OFFSET_M
            if 0 < dist_to_inner < config.NFZ_INNER_RANGE_M:
                off_lat, off_lon = self.geofence.repulsive_offset(self.lat, self.lon)
                if abs(off_lat) > 1e-8 or abs(off_lon) > 1e-8:
                    self._last_repulsion_vec = (off_lat, off_lon)
                    lat_m = 111320.0
                    lon_m = 111320.0 * math.cos(math.radians(self.lat))
                    push_n, push_e = -off_lat * lat_m, -off_lon * lon_m
                    if nfz_inside:
                        push_n, push_e = -push_n, -push_e
                    mag = math.sqrt(push_n**2 + push_e**2)
                    if mag > 0.01:
                        s = config.NFZ_PUSH_SPEED_MPS
                        self.nav.send_velocity(push_n/mag*s, push_e/mag*s, 0, current_yaw=0.0)

    def _emergency_rtl(self, reason="unknown"):
        """Best-effort RTL when the link is degraded. Warns operator loudly."""
        print("=" * 60)
        print(f"  EMERGENCY: Attempting RTL  —  {reason}")
        print("  If RTL fails, ArduCopter GCS failsafe should trigger RTL")
        print("  RC kill switch is always available")
        print("=" * 60)
        try:
            if self.master:
                # Try setting RTL mode directly via MAVLink (mode 6)
                self.master.mav.command_long_send(
                    self.master.target_system, self.master.target_component,
                    mavutil.mavlink.MAV_CMD_DO_SET_MODE, 0,
                    mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
                    6, 0, 0, 0, 0, 0)  # 6 = RTL
                print("[EMERGENCY] RTL command sent")
        except Exception as e2:
            print(f"[EMERGENCY] RTL send failed: {e2}")
            print("[EMERGENCY] Relying on ArduCopter GCS failsafe (FS_GCS_ENABLE)")

    def on_dashboard_mouse(self, event, x, y, flags, param):
        if event == cv2.EVENT_MOUSEWHEEL:
            if flags > 0: self.zoom_level = min(self.zoom_level * 1.2, 20.0)
            else: self.zoom_level = max(self.zoom_level / 1.2, 1.0)


# ── Dry-run ───────────────────────────────────────────────────────────

def _dry_run(mission):
    """Visualize search pattern without flying. No Cube needed."""
    print("\n" + "=" * 60)
    print("  DRY-RUN: Generating lawnmower search pattern")
    print("=" * 60)

    if not mission.search_poly or len(mission.search_poly) < 3:
        print("  ERROR: No search polygon. Set SEARCH_AREA_GPS in config.py.")
        return

    print(f"\n  Search area: {len(mission.search_poly)} corners")
    for i, pt in enumerate(mission.search_poly):
        gps = mission.geo.pixels_to_gps(pt[0], pt[1]) if hasattr(pt, '__len__') else (0, 0)
        print(f"    {i+1}: ({gps[0]:.6f}, {gps[1]:.6f})")

    drone_gps = (config.REF_LAT, config.REF_LON)
    print(f"\n  Start: ({drone_gps[0]:.6f}, {drone_gps[1]:.6f})  Alt: {config.TARGET_ALT}m  Speed: {config.SEARCH_SPEED_MPS}m/s")

    waypoints = mission.planner.generate_search_pattern(REAL_CANVAS_SIZE, REAL_CANVAS_SIZE, drone_gps)
    if not waypoints:
        print("  ERROR: No waypoints generated!")
        return

    total_dist = 0
    for i in range(1, len(waypoints)):
        prev = waypoints[i-1]; wp = waypoints[i]
        total_dist += 111320 * math.sqrt(
            (wp[0]-prev[0])**2 + ((wp[1]-prev[1])*math.cos(math.radians(wp[0])))**2)

    print(f"  {len(waypoints)} waypoints, {total_dist:.0f}m search path")
    for i, wp in enumerate(waypoints):
        tag = " <START" if i == 0 else (" <END" if i == len(waypoints)-1 else "")
        print(f"    WP {i+1:3d}: ({wp[0]:.6f}, {wp[1]:.6f}){tag}")

    wp0 = waypoints[0]
    transit_dist = 111320 * math.sqrt(
        (wp0[0]-drone_gps[0])**2 + ((wp0[1]-drone_gps[1])*math.cos(math.radians(drone_gps[0])))**2)
    total_time = transit_dist/config.TRANSIT_SPEED_MPS + total_dist/config.SEARCH_SPEED_MPS
    print(f"\n  Transit: {transit_dist:.0f}m  Search: {total_dist:.0f}m  Total: {total_time:.0f}s ({total_time/60:.1f}min)")

    # State machine walkthrough
    print(f"\n  States: INIT->CONNECT->ARM(GPS>=3,sats>=6)->TAKEOFF({config.TARGET_ALT}m)")
    print(f"    ->SEARCH({len(waypoints)}wp)->CENTERING->DESCEND({config.VERIFY_ALT}m)->VERIFY->LAND")

    # Map visualization
    map_img = cv2.imread(config.MAP_FILE)
    if map_img is not None:
        vis = map_img.copy()
        cv2.polylines(vis, [np.array(mission.search_poly, np.int32)], True, (0,255,0), 2)
        for i, wp in enumerate(waypoints):
            pt = tuple(int(c) for c in mission.geo.gps_to_pixels(wp[0], wp[1]))
            color = (0,0,255) if i==0 else ((255,0,0) if i==len(waypoints)-1 else (255,255,0))
            cv2.circle(vis, pt, 4, color, -1)
            if i > 0:
                prev = tuple(int(c) for c in mission.geo.gps_to_pixels(waypoints[i-1][0], waypoints[i-1][1]))
                cv2.line(vis, prev, pt, (255,255,0), 1)
        dp = tuple(int(c) for c in mission.geo.gps_to_pixels(*drone_gps))
        cv2.drawMarker(vis, dp, (0,255,255), cv2.MARKER_DIAMOND, 15, 2)
        cv2.putText(vis, f"DRY-RUN: {len(waypoints)} WPs, {total_dist:.0f}m, ~{total_time/60:.1f}min",
                    (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
        scale = min(1.0, 900 / vis.shape[0])
        if scale < 1.0:
            vis = cv2.resize(vis, (int(vis.shape[1]*scale), int(vis.shape[0]*scale)))
        if not HEADLESS:
            cv2.imshow("Dry-Run: Search Pattern", vis)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        cv2.imwrite("dry_run_pattern.jpg", vis)
        print(f"  Saved: dry_run_pattern.jpg")
    else:
        print("  (No map.jpg — skipping visualization)")

    print(f"\n  DRY-RUN COMPLETE. No commands sent.")
    print("=" * 60)


if __name__ == "__main__":
    mission = VisualFlightMission()
    if DRY_RUN:
        _dry_run(mission)
    else:
        try:
            mission.run()
        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError) as e:
            print(f"\n[LINK LOST] {e}")
        except KeyboardInterrupt:
            print("\n[USER] Aborted")
        finally:
            if hasattr(mission, 'log_file') and mission.log_file:
                mission.log_file.close()
            if not HEADLESS:
                cv2.destroyAllWindows()
