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
from http.server import HTTPServer, BaseHTTPRequestHandler

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

# Conditional Import for Simulation
if config.MODE == "SIMULATION":
    from simulation import SimulationEnvironment

# --- CLI FLAGS ---
# Model:      --model models/best2.tflite   (default: best.tflite)
# Dry-run:    --dry-run                      (skip GPS/arm, show pattern, print commands)
# Stream:     --stream-port 8090 --stream-res 320x240 --stream-fps 5 --stream-quality 50
# No stream:  --no-stream
DRY_RUN = "--dry-run" in sys.argv
MODEL_PATH = config.MODEL_PATH
STREAM_ENABLED = "--no-stream" not in sys.argv
STREAM_PORT = 8090
STREAM_W, STREAM_H = 320, 240
STREAM_FPS = 5
STREAM_QUALITY = 50

for _i, _arg in enumerate(sys.argv):
    if _arg == "--model" and _i + 1 < len(sys.argv):
        MODEL_PATH = sys.argv[_i + 1]
    elif _arg == "--stream-port" and _i + 1 < len(sys.argv):
        STREAM_PORT = int(sys.argv[_i + 1])
    elif _arg == "--stream-res" and _i + 1 < len(sys.argv):
        _parts = sys.argv[_i + 1].split("x")
        STREAM_W, STREAM_H = int(_parts[0]), int(_parts[1])
    elif _arg == "--stream-fps" and _i + 1 < len(sys.argv):
        STREAM_FPS = int(sys.argv[_i + 1])
    elif _arg == "--stream-quality" and _i + 1 < len(sys.argv):
        STREAM_QUALITY = int(sys.argv[_i + 1])

if DRY_RUN:
    print("=" * 60)
    print("  DRY-RUN MODE — No arming, no flying, no GPS needed")
    print("  Shows lawnmower pattern, prints commands, tests pipeline")
    print("=" * 60)

_stream_frame = None
_stream_lock = threading.Lock()

class _StreamHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/stream':
            self.send_response(200)
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=frame')
            self.end_headers()
            while True:
                with _stream_lock:
                    f = _stream_frame
                if f is None:
                    time.sleep(0.1)
                    continue
                small = cv2.resize(f, (STREAM_W, STREAM_H))
                _, jpeg = cv2.imencode('.jpg', small, [cv2.IMWRITE_JPEG_QUALITY, STREAM_QUALITY])
                data = jpeg.tobytes()
                try:
                    self.wfile.write(b'--frame\r\n')
                    self.wfile.write(b'Content-Type: image/jpeg\r\n')
                    self.wfile.write(f'Content-Length: {len(data)}\r\n\r\n'.encode())
                    self.wfile.write(data)
                    self.wfile.write(b'\r\n')
                except (BrokenPipeError, ConnectionResetError):
                    break
                time.sleep(1.0 / STREAM_FPS)
        elif self.path == '/':
            html = f'<html><body style="background:#111;text-align:center;font-family:monospace">'
            html += f'<h2 style="color:#fff">SAR Drone Mission Feed</h2>'
            html += f'<img src="/stream" style="max-width:100%;border:2px solid #0f0"/>'
            html += f'<p style="color:#aaa">{STREAM_W}x{STREAM_H} | {STREAM_FPS} fps | Quality {STREAM_QUALITY}%</p>'
            html += f'</body></html>'
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode())
        else:
            self.send_response(404)
            self.end_headers()
    def log_message(self, format, *args):
        pass

def _start_stream_server():
    """Start MJPEG server in background thread."""
    if not STREAM_ENABLED:
        print("[STREAM] Disabled (--no-stream)")
        return None
    try:
        server = HTTPServer(('0.0.0.0', STREAM_PORT), _StreamHandler)
        server_thread = threading.Thread(target=server.serve_forever, daemon=True)
        server_thread.start()
        # Get IP for display
        pi_ip = "localhost"
        try:
            import subprocess
            result = subprocess.run(['hostname', '-I'], capture_output=True, text=True, timeout=3)
            pi_ip = result.stdout.strip().split()[0]
        except Exception:
            pass
        print(f"[STREAM] Live feed: http://{pi_ip}:{STREAM_PORT}/")
        print(f"[STREAM] Settings: {STREAM_W}x{STREAM_H} @ {STREAM_FPS}fps, quality {STREAM_QUALITY}%")
        return server
    except Exception as e:
        print(f"[STREAM] Failed to start: {e}")
        return None


class VisualFlightMission:
    def __init__(self):
        print(f"--- INITIALIZING IN {config.MODE} MODE ---")
        
        # 1. Initialize Geo & Map Tools
        if config.MODE == "SIMULATION":
            self.sim = SimulationEnvironment(GeoTransformer(map_w_px=100)) # Temp init
            self.geo = GeoTransformer(map_w_px=self.sim.map_w)
            self.sim.geo = self.geo # Sync geo tool
            # Returns only Target and Search Poly
            self.target_px, self.tgt_type, self.search_poly = self.sim.setup_on_map()
            
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

        # 2. Planner
        self.planner = PathPlanner(self.geo, self.search_poly)

        # 3. Connection
        self.master = None
        self.last_req = 0
        self.last_heartbeat = 0

        # 4. State & Telemetry
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
        self.lat = config.REF_LAT
        self.lon = config.REF_LON
        self.alt = 0.0
        self.vx = 0; self.vy = 0; self.vz = 0
        self.roll = 0; self.pitch = 0; self.yaw = 0
        
        # 5. Mission Data
        self.waypoints = []
        self.wp_index = 0
        
        # Target Data
        self.target_lat = 0; self.target_lon = 0
        self.landing_lat = 0; self.landing_lon = 0
        self.current_conf = 0.0
        self.final_dist = 0.0 # Store final accuracy distance
        
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
        """Interactive polygon drawing for REAL mode. Falls back to config GPS if no map."""
        # Try loading the map for interactive drawing
        map_img = cv2.imread(config.MAP_FILE)
        if map_img is not None:
            map_h, map_w = map_img.shape[:2]
            self.geo = GeoTransformer(map_w_px=map_w)

            # Scale for display
            MAX_H = 800
            scale = min(1.0, MAX_H / map_h)
            display = cv2.resize(map_img, (int(map_w * scale), int(map_h * scale)))

            polygon = []
            closed = False

            def mouse_cb(event, x, y, flags, param):
                nonlocal closed
                real_x, real_y = int(x / scale), int(y / scale)
                if event == cv2.EVENT_LBUTTONDOWN and not closed:
                    polygon.append((real_x, real_y))
                elif event == cv2.EVENT_RBUTTONDOWN and len(polygon) >= 3:
                    closed = True

                # Redraw
                vis = display.copy()
                if polygon:
                    pts = np.array([[int(p[0]*scale), int(p[1]*scale)] for p in polygon], np.int32)
                    cv2.polylines(vis, [pts], closed, (0, 255, 0), 2)
                    for p in pts:
                        cv2.circle(vis, tuple(p), 4, (0, 255, 0), -1)
                cv2.imshow("Draw Search Area", vis)

            cv2.namedWindow("Draw Search Area")
            cv2.imshow("Draw Search Area", display)
            cv2.setMouseCallback("Draw Search Area", mouse_cb)
            print("--- REAL MODE SEARCH AREA ---")
            print("Left-Click: add polygon points")
            print("Right-Click: close polygon")
            print("Press any key: start mission")
            print("Press ESC: use SEARCH_AREA_GPS from config.py instead")
            key = cv2.waitKey(0) & 0xFF
            cv2.destroyWindow("Draw Search Area")

            if closed and len(polygon) >= 3:
                # Convert drawn polygon to GPS and print for future config use
                print(f"[REAL] Search polygon drawn: {len(polygon)} points")
                gps_coords = [self.geo.pixels_to_gps(p[0], p[1]) for p in polygon]
                print("[REAL] GPS coordinates (copy to config.py SEARCH_AREA_GPS):")
                for lat, lon in gps_coords:
                    print(f"    ({lat:.6f}, {lon:.6f}),")
                return polygon

            if key == 27:
                print("[REAL] Skipped drawing — using SEARCH_AREA_GPS from config.py")

        # Fallback: use GPS coordinates from config.py
        self.geo = GeoTransformer(map_w_px=4800)
        if hasattr(config, 'SEARCH_AREA_GPS') and len(config.SEARCH_AREA_GPS) >= 3:
            poly = [self.geo.gps_to_pixels(lat, lon) for lat, lon in config.SEARCH_AREA_GPS]
            print(f"[REAL] Search area loaded from config: {len(poly)} GPS corners")
            return poly
        print("[REAL] No search area defined — no search pattern")
        return []

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

    def calculate_target_gps(self, u, v):
        Cx = config.IMAGE_W / 2; Cy = config.IMAGE_H / 2
        gsd_m = (config.SENSOR_WIDTH_MM * self.alt) / (config.FOCAL_LENGTH_MM * config.IMAGE_W)
        delta_x_px = u - Cx; delta_y_px = v - Cy 
        
        fwd_m = -delta_y_px * gsd_m
        right_m = delta_x_px * gsd_m
        offset_n = fwd_m * math.cos(self.yaw) - right_m * math.sin(self.yaw)
        offset_e = fwd_m * math.sin(self.yaw) + right_m * math.cos(self.yaw)
        
        R_EARTH = 6378137.0
        dLat = (offset_n / R_EARTH) * (180 / math.pi)
        dLon = (offset_e / (R_EARTH * math.cos(math.radians(self.lat)))) * (180 / math.pi)
        self.target_lat = self.lat + dLat
        self.target_lon = self.lon + dLon
        print(f"[VISION] Target GPS: {self.target_lat:.6f}, {self.target_lon:.6f}")

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
        
        # Current Position (Always displayed)
        cv2.putText(frame, f"POS: {self.lat:.6f}, {self.lon:.6f}", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        # Target Location (If found/narrowing down)
        if self.target_lat != 0:
            cv2.putText(frame, f"TARGET: {self.target_lat:.6f}, {self.target_lon:.6f}", (10, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Landing Location (If determined)
        if self.landing_lat != 0:
            cv2.putText(frame, f"LANDING: {self.landing_lat:.6f}, {self.landing_lon:.6f}", (10, 170), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

        # Final Result (After Landing)
        if self.state == State.DONE:
             cv2.putText(frame, f"FINAL ERROR: {self.final_dist:.2f} m", (cx - 150, cy), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)

        
        if self.waiting_for_confirmation:
             if self.selecting_landing_side:
                 cv2.putText(frame, "SELECT LANDING SIDE:", (cx - 200, cy + 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                 cv2.putText(frame, "N: North | S: South", (cx - 200, cy + 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                 cv2.putText(frame, "W: West  | E: East", (cx - 200, cy + 120), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
             else:
                 cv2.putText(frame, "CONFIRM TARGET? (Y/N)", (cx - 150, cy + 80), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)

        # 4. COMPOSITE VIEW
        final_display = frame
        if config.MODE == "SIMULATION":
             god_frame = self.sim.get_god_view(
                px, py, self.yaw, self.view_w_px, self.view_h_px, self.zoom_level,
                self.planner.virtual_polygon, self.search_poly,
                (self.target_lat, self.target_lon), (self.landing_lat, self.landing_lon), self.geo
            )
             h_scale = frame.shape[0] / god_frame.shape[0]
             god_resized = cv2.resize(god_frame, (int(god_frame.shape[1]*h_scale), frame.shape[0]))
             final_display = np.hstack((god_resized, frame))

        # Update stream for ground station (frame with HUD, before composite)
        if STREAM_ENABLED:
            global _stream_frame
            with _stream_lock:
                _stream_frame = frame

        cv2.imshow("Mission Dashboard", final_display)
        return found, u, v

    def set_speed(self, speed_mps):
        if time.time() - self.last_speed_req < 3.0: return
        self.master.mav.command_long_send(
            self.master.target_system, self.master.target_component,
            mavutil.mavlink.MAV_CMD_DO_CHANGE_SPEED, 0, 1, speed_mps, -1, 0, 0, 0, 0)
        self.last_speed_req = time.time()

    def calculate_landing_spot(self, direction_key):
        R_EARTH = 6378137.0
        offset_dist = 7.5 # meters
        dLat = 0
        dLon = 0
        
        if direction_key == 'n': # North
            dLat = (offset_dist / R_EARTH) * (180/math.pi)
        elif direction_key == 's': # South
            dLat = -(offset_dist / R_EARTH) * (180/math.pi)
        elif direction_key == 'e': # East
            dLon = (offset_dist / (R_EARTH * math.cos(math.radians(self.target_lat)))) * (180/math.pi)
        elif direction_key == 'w': # West
            dLon = -(offset_dist / (R_EARTH * math.cos(math.radians(self.target_lat)))) * (180/math.pi)
            
        self.landing_lat = self.target_lat + dLat
        self.landing_lon = self.target_lon + dLon
        print(f"Landing Spot Selected: {direction_key.upper()} of Target")

    def run(self):
        print("Starting Mission Loop...")
        _start_stream_server()
        cv2.namedWindow("Mission Dashboard")
        if config.MODE == "SIMULATION":
            cv2.setMouseCallback("Mission Dashboard", self.on_dashboard_mouse)
        
        key = -1 
        while True:
            self.update_telemetry()
            target_found, px_u, px_v = self.update_dashboard()
            
            # Log Data
            if time.time() % 1.0 < 0.1: 
                self.logger.writerow([datetime.now(), self.state, self.lat, self.lon, self.alt, self.current_conf])
            
            # --- KEY INPUTS ---
            if key == ord('m') or key == ord('M'):
                if self.state != State.MANUAL:
                    print("!!! MANUAL CONTROL OVERRIDE !!!")
                    self.previous_state = self.state
                    self._set_state(State.MANUAL)
                else:
                    print("Resuming Automation...")
                    if target_found: self._set_state(State.CENTERING)
                    else: self._set_state(self.previous_state)
            
            if self.state == State.VERIFY:
                if self.selecting_landing_side:
                    if key in [ord('n'), ord('e'), ord('w'), ord('s'), ord('N'), ord('E'), ord('W'), ord('S')]:
                        self.calculate_landing_spot(chr(key).lower())
                        self.selecting_landing_side = False
                        self.waiting_for_confirmation = False
                        self._set_state(State.APPROACH)
                else:
                    if key == ord('y') or key == ord('Y'):
                        print("USER CONFIRMED TARGET. SELECT LANDING SIDE (N/E/W/S).")
                        self.selecting_landing_side = True
                    elif key == ord('n') or key == ord('N'):
                        print("USER REJECTED TARGET. RESUMING SEARCH.")
                        self.waiting_for_confirmation = False
                        self._set_state(State.SEARCH)

            # --- STATE MACHINE ---
            if self.state == State.INIT:
                if time.time() - self.last_req > 1.0:
                    try:
                        print(f"Connecting to {config.CONNECTION_STR}...")
                        self.master = mavutil.mavlink_connection(config.CONNECTION_STR)
                        self.connect_start_time = time.time()  # FIX 4: start heartbeat timeout
                        self._set_state(State.CONNECTING)
                    except Exception as e: print(f"Connection fail: {e}")
                    self.last_req = time.time()

            elif self.state == State.CONNECTING:
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
                    self._set_state(State.ARMING)

            elif self.state == State.ARMING:
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
                            print(f"GPS FIX OK — fix_type={fix_type}, sats={sats}, lat={self.lat:.6f}, lon={self.lon:.6f}")
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
                elif time.time() - self.last_req > 2.0:
                    # Set GUIDED mode (4) — use command_long which works reliably via mavproxy
                    self.master.mav.command_long_send(
                        self.master.target_system, self.master.target_component,
                        mavutil.mavlink.MAV_CMD_DO_SET_MODE, 0,
                        mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
                        4, 0, 0, 0, 0, 0)  # 4 = GUIDED
                    # FIX 3: Check SET_MODE acknowledgement
                    mode_ack = self.master.recv_match(type='COMMAND_ACK', blocking=True, timeout=3)
                    if mode_ack:
                        if mode_ack.result != 0:
                            print(f"SET_MODE REJECTED: result={mode_ack.result}")
                        else:
                            print("SET_MODE (GUIDED) accepted")
                    self.master.mav.command_long_send(
                        self.master.target_system, self.master.target_component,
                        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, 1, 0, 0, 0, 0, 0, 0)
                    # FIX 3: Check ARM acknowledgement
                    arm_ack = self.master.recv_match(type='COMMAND_ACK', blocking=True, timeout=3)
                    if arm_ack:
                        if arm_ack.result != 0:
                            print(f"ARM REJECTED: result={arm_ack.result}")
                        else:
                            print("ARM command accepted")
                    self.last_req = time.time()

            elif self.state == State.TAKEOFF:
                # FIX 5: Takeoff timeout warning
                if time.time() - self.state_start_time > 60 and not self._takeoff_timeout_warned:
                    print("TAKEOFF TIMEOUT: Drone may not be climbing. Check motors and GPS.")
                    self._takeoff_timeout_warned = True
                if self.alt >= config.TARGET_ALT * 0.90:
                    print("Target Altitude Reached.")

                    if config.MODE == "SIMULATION":
                        canvas_w, canvas_h = self.sim.map_w, self.sim.map_h
                    else:
                        canvas_w, canvas_h = 4800, 4800  # virtual canvas for planner

                    self.waypoints = self.planner.generate_search_pattern(
                        canvas_w, canvas_h, (self.lat, self.lon))

                    if self.waypoints:
                        # NEW LOGIC: Go to TRANSIT first, then SEARCH
                        print(f"Path generated. Transiting to start point: {self.waypoints[0]}")
                        self._set_state(State.TRANSIT_TO_SEARCH)
                        self.last_speed_req = 0
                    else:
                        print("No Waypoints generated.")
                        self._set_state(State.HOVER)

            elif self.state == State.TRANSIT_TO_SEARCH:
                # Fly to the first waypoint of the search grid (Optimal Entry Point)
                self.set_speed(config.TRANSIT_SPEED_MPS)
                
                target = self.waypoints[0]
                if time.time() - self.last_req > 2.0:
                    self.send_global_target(target[0], target[1], config.TARGET_ALT)
                    self.last_req = time.time()
                
                # Check arrival
                if self.get_dist_to_point(target[0], target[1]) < 2.0:
                    print("Reached Search Start Point. Beginning Pattern.")
                    self._set_state(State.SEARCH)
                    self.wp_index = 0 # Start from index 0

            elif self.state == State.SEARCH:
                self.set_speed(config.SEARCH_SPEED_MPS)
                if target_found:
                    print("TARGET DETECTED!")
                    self.calculate_target_gps(px_u, px_v)
                    self._set_state(State.CENTERING)
                elif self.wp_index < len(self.waypoints):
                    target = self.waypoints[self.wp_index]
                    if time.time() - self.last_req > 2.0:
                        self.send_global_target(target[0], target[1], config.TARGET_ALT)
                        self.last_req = time.time()
                    if self.get_dist_to_point(target[0], target[1]) < 2.0:
                        self.wp_index += 1
                else:
                    self._set_state(State.DONE)

            elif self.state == State.CENTERING:
                 # FIX 5: Centering timeout — go back to SEARCH
                 if time.time() - self.state_start_time > 60 and not self._centering_timeout_warned:
                     print("CENTERING TIMEOUT: Lost target or can't converge. Resuming search.")
                     self._centering_timeout_warned = True
                     self._set_state(State.SEARCH)
                 if target_found: self.calculate_target_gps(px_u, px_v)
                 if time.time() - self.last_req > 0.2:
                     self.send_global_target(self.target_lat, self.target_lon, config.TARGET_ALT)
                     self.last_req = time.time()
                 if self.get_dist_to_target() < 1.0:
                     self._set_state(State.DESCENDING)

            elif self.state == State.DESCENDING:
                 # FIX 5: Descending timeout warning
                 if time.time() - self.state_start_time > 60 and not self._descending_timeout_warned:
                     print("DESCENDING TIMEOUT: Drone may not be descending. Check altitude hold.")
                     self._descending_timeout_warned = True
                 if target_found: self.calculate_target_gps(px_u, px_v)
                 if time.time() - self.last_req > 0.5:
                     self.send_global_target(self.target_lat, self.target_lon, config.VERIFY_ALT)
                     self.last_req = time.time()
                 if self.alt <= config.VERIFY_ALT + 1.0:
                     self._set_state(State.VERIFY)

            elif self.state == State.VERIFY:
                self.waiting_for_confirmation = True
                self.send_global_target(self.target_lat, self.target_lon, config.VERIFY_ALT)

            elif self.state == State.APPROACH:
                self.send_global_target(self.landing_lat, self.landing_lon, config.VERIFY_ALT)
                if self.get_dist_to_point(self.landing_lat, self.landing_lon) < 1.0:
                    self._set_state(State.LANDING)

            elif self.state == State.LANDING:
                if self.alt < 0.3:
                    print("Touchdown. Disarming.")
                    self.master.mav.command_long_send(
                        self.master.target_system, self.master.target_component,
                        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, 0, 0, 0, 0, 0, 0, 0)
                    
                    # Calculate final error
                    lat_scale = 111132.0 
                    final_error = math.sqrt(((self.lat-self.target_lat)*lat_scale)**2 + ((self.lon-self.target_lon)*lat_scale*0.62)**2)
                    self.final_dist = final_error
                    print(f"MISSION COMPLETE. Final Error: {self.final_dist:.2f} m")
                    self._set_state(State.DONE)
                else:
                    self.send_global_target(self.landing_lat, self.landing_lon, 0) 

            key = cv2.waitKey(20) & 0xFF
            if key == 27: break

    def on_dashboard_mouse(self, event, x, y, flags, param):
        if event == cv2.EVENT_MOUSEWHEEL:
            if flags > 0: self.zoom_level = min(self.zoom_level * 1.2, 20.0)
            else: self.zoom_level = max(self.zoom_level / 1.2, 1.0)
            
    def _set_state(self, new_state):
        """Change state and reset state timer (FIX 5: state timeouts)."""
        self.state = new_state
        self.state_start_time = time.time()
        # Reset per-state timeout warnings
        self._arming_timeout_warned = False
        self._takeoff_timeout_warned = False
        self._centering_timeout_warned = False
        self._descending_timeout_warned = False

    def send_global_target(self, lat, lon, alt):
        self.master.mav.set_position_target_global_int_send(
             0, self.master.target_system, self.master.target_component,
             mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
             0b110111111000, int(lat * 1e7), int(lon * 1e7), alt, 0, 0, 0, 0, 0, 0, 0, 0)
             
    def get_dist_to_target(self): return self.get_dist_to_point(self.target_lat, self.target_lon)
    def get_dist_to_point(self, t_lat, t_lon):
        lat_scale = 111132.0 
        return math.sqrt(((self.lat-t_lat)*lat_scale)**2 + ((self.lon-t_lon)*lat_scale*0.62)**2)

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

    canvas_w, canvas_h = 4800, 4800
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
    print(f"    INIT → connect to {config.CONNECTION_STR}")
    print(f"    CONNECTING → wait for heartbeat")
    print(f"    ARMING → wait for GPS fix (fix_type>=3, sats>=6)")
    print(f"    ARMING → set GUIDED mode")
    print(f"    ARMING → arm motors")
    print(f"    TAKEOFF → climb to {config.TARGET_ALT}m")
    print(f"    TRANSIT_TO_SEARCH → fly to WP 1 ({waypoints[0][0]:.6f}, {waypoints[0][1]:.6f})")
    print(f"    SEARCH → fly {len(waypoints)} waypoints in lawnmower pattern")
    print(f"    (on detection) CENTERING → center target in camera frame")
    print(f"    DESCENDING → descend to {config.VERIFY_ALT}m")
    print(f"    VERIFY → operator confirms Y/N")
    print(f"    APPROACH → fly to landing point")
    print(f"    LANDING → land and disarm")

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
        mission.run()