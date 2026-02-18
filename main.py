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

# --- GS Camera Stream (MJPEG over HTTP) ---
STREAM_PORT = 8090
STREAM_W, STREAM_H = 320, 240
STREAM_FPS = 5
STREAM_QUALITY = 50
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
            html = '<html><body style="background:#111;text-align:center">'
            html += '<h2 style="color:#fff;font-family:monospace">SAR Drone Mission Feed</h2>'
            html += '<img src="/stream" style="max-width:100%;border:2px solid #0f0"/></body></html>'
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
            
            self.eyes = VisionSystem(camera_index=None, model_path="best.tflite")
            if self.tgt_type == "dummy": self.eyes.using_ai = True
            else: self.eyes.using_ai = False
            
        else: # REAL MODE
            self.sim = None

            # Try to show map for interactive polygon drawing
            self.search_poly = self._setup_real_search_area()

            self.eyes = VisionSystem(camera_index=config.REAL_CAMERA_INDEX, model_path="best.tflite")
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
                    self.state = State.MANUAL
                else:
                    print("Resuming Automation...")
                    if target_found: self.state = State.CENTERING
                    else: self.state = self.previous_state
            
            if self.state == State.VERIFY:
                if self.selecting_landing_side:
                    if key in [ord('n'), ord('e'), ord('w'), ord('s'), ord('N'), ord('E'), ord('W'), ord('S')]:
                        self.calculate_landing_spot(chr(key).lower())
                        self.selecting_landing_side = False
                        self.waiting_for_confirmation = False
                        self.state = State.APPROACH
                else:
                    if key == ord('y') or key == ord('Y'):
                        print("USER CONFIRMED TARGET. SELECT LANDING SIDE (N/E/W/S).")
                        self.selecting_landing_side = True
                    elif key == ord('n') or key == ord('N'):
                        print("USER REJECTED TARGET. RESUMING SEARCH.")
                        self.waiting_for_confirmation = False
                        self.state = State.SEARCH

            # --- STATE MACHINE ---
            if self.state == State.INIT:
                if time.time() - self.last_req > 1.0:
                    try:
                        print(f"Connecting to {config.CONNECTION_STR}...")
                        self.master = mavutil.mavlink_connection(config.CONNECTION_STR)
                        self.state = State.CONNECTING
                    except Exception as e: print(f"Connection fail: {e}")
                    self.last_req = time.time()

            elif self.state == State.CONNECTING:
                if self.last_heartbeat > 0:
                    print("Heartbeat. Requesting Data Stream...")
                    self.master.mav.request_data_stream_send(
                        self.master.target_system, self.master.target_component,
                        mavutil.mavlink.MAV_DATA_STREAM_ALL, 10, 1)
                    self.state = State.ARMING

            elif self.state == State.ARMING:
                if self.master.motors_armed():
                    print("Armed! Taking Off...")
                    self.master.mav.command_long_send(
                        self.master.target_system, self.master.target_component,
                        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 0, 0, 0, config.TARGET_ALT)
                    self.state = State.TAKEOFF
                elif time.time() - self.last_req > 2.0:
                    # Set GUIDED mode (4) — use command_long which works reliably via mavproxy
                    self.master.mav.command_long_send(
                        self.master.target_system, self.master.target_component,
                        mavutil.mavlink.MAV_CMD_DO_SET_MODE, 0,
                        mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
                        4, 0, 0, 0, 0, 0)  # 4 = GUIDED
                    self.master.mav.command_long_send(
                        self.master.target_system, self.master.target_component,
                        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, 1, 0, 0, 0, 0, 0, 0)
                    self.last_req = time.time()

            elif self.state == State.TAKEOFF:
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
                        self.state = State.TRANSIT_TO_SEARCH
                        self.last_speed_req = 0 
                    else:
                        print("No Waypoints generated.")
                        self.state = State.HOVER

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
                    self.state = State.SEARCH
                    self.wp_index = 0 # Start from index 0

            elif self.state == State.SEARCH:
                self.set_speed(config.SEARCH_SPEED_MPS)
                if target_found:
                    print("TARGET DETECTED!")
                    self.calculate_target_gps(px_u, px_v)
                    self.state = State.CENTERING
                elif self.wp_index < len(self.waypoints):
                    target = self.waypoints[self.wp_index]
                    if time.time() - self.last_req > 2.0:
                        self.send_global_target(target[0], target[1], config.TARGET_ALT)
                        self.last_req = time.time()
                    if self.get_dist_to_point(target[0], target[1]) < 2.0:
                        self.wp_index += 1
                else:
                    self.state = State.DONE

            elif self.state == State.CENTERING:
                 if target_found: self.calculate_target_gps(px_u, px_v)
                 if time.time() - self.last_req > 0.2:
                     self.send_global_target(self.target_lat, self.target_lon, config.TARGET_ALT)
                     self.last_req = time.time()
                 if self.get_dist_to_target() < 1.0:
                     self.state = State.DESCENDING

            elif self.state == State.DESCENDING:
                 if target_found: self.calculate_target_gps(px_u, px_v)
                 if time.time() - self.last_req > 0.5:
                     self.send_global_target(self.target_lat, self.target_lon, config.VERIFY_ALT)
                     self.last_req = time.time()
                 if self.alt <= config.VERIFY_ALT + 1.0:
                     self.state = State.VERIFY

            elif self.state == State.VERIFY:
                self.waiting_for_confirmation = True
                self.send_global_target(self.target_lat, self.target_lon, config.VERIFY_ALT)

            elif self.state == State.APPROACH:
                self.send_global_target(self.landing_lat, self.landing_lon, config.VERIFY_ALT)
                if self.get_dist_to_point(self.landing_lat, self.landing_lon) < 1.0:
                    self.state = State.LANDING

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
                    self.state = State.DONE
                else:
                    self.send_global_target(self.landing_lat, self.landing_lon, 0) 

            key = cv2.waitKey(20) & 0xFF
            if key == 27: break

    def on_dashboard_mouse(self, event, x, y, flags, param):
        if event == cv2.EVENT_MOUSEWHEEL:
            if flags > 0: self.zoom_level = min(self.zoom_level * 1.2, 20.0)
            else: self.zoom_level = max(self.zoom_level / 1.2, 1.0)
            
    def send_global_target(self, lat, lon, alt):
        self.master.mav.set_position_target_global_int_send(
             0, self.master.target_system, self.master.target_component,
             mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
             0b110111111000, int(lat * 1e7), int(lon * 1e7), alt, 0, 0, 0, 0, 0, 0, 0, 0)
             
    def get_dist_to_target(self): return self.get_dist_to_point(self.target_lat, self.target_lon)
    def get_dist_to_point(self, t_lat, t_lon):
        lat_scale = 111132.0 
        return math.sqrt(((self.lat-t_lat)*lat_scale)**2 + ((self.lon-t_lon)*lat_scale*0.62)**2)

if __name__ == "__main__":
    mission = VisualFlightMission()
    mission.run()