#!/usr/bin/env python3
"""
Live map viewer — watch drone fly on map.jpg in real-time.

Runs on LAPTOP, connects to Pi's mavproxy TCP output.
Shows drone position, camera footprint, coverage overlay, zones, waypoints.
Scroll to zoom in/out (centred on drone). Same style as simulation god view.

Usage:
    python tests/flight/live_map.py                          # connect to SITL locally
    python tests/flight/live_map.py --host 192.168.1.121     # connect to Pi's mavproxy
    python tests/flight/live_map.py --port 5763              # different TCP port

Requires: mavproxy running on Pi with --out=tcpin:0.0.0.0:5762
Multiple clients (Mission Planner + this) can connect simultaneously.
"""
import sys
import os
import json
import time
import math
import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from pymavlink import mavutil
import config
from utils import GeoTransformer

# Preserve map calibration origin
_saved_ref_lat, _saved_ref_lon = config.REF_LAT, config.REF_LON
config.load_kml_zones()
config.REF_LAT, config.REF_LON = _saved_ref_lat, _saved_ref_lon

# Parse CLI
HOST = "127.0.0.1"
PORT = 5762
for i, arg in enumerate(sys.argv):
    if arg == "--host" and i + 1 < len(sys.argv):
        HOST = sys.argv[i + 1]
    elif arg == "--port" and i + 1 < len(sys.argv):
        PORT = int(sys.argv[i + 1])

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load map
map_path = os.path.join(PROJECT_ROOT, config.MAP_FILE)
if not os.path.exists(map_path):
    print(f"  [ERROR] map.jpg not found at {map_path}")
    sys.exit(1)

img_full = cv2.imread(map_path)
img_h, img_w = img_full.shape[:2]
geo = GeoTransformer(img_w)

# Display size
DISPLAY_H = 700

# Load waypoints.json if exists
waypoints = []
wp_file = os.path.join(PROJECT_ROOT, "waypoints.json")
if os.path.exists(wp_file):
    with open(wp_file, "r") as f:
        wp_data = json.load(f)
    waypoints = [(wp["lat"], wp["lon"], wp.get("label", f"WP{i+1}"))
                 for i, wp in enumerate(wp_data)]

# Load search_area.json if exists
search_area = []
sa_file = os.path.join(PROJECT_ROOT, "search_area.json")
if os.path.exists(sa_file):
    with open(sa_file, "r") as f:
        sa_data = json.load(f)
    search_area = [(pt["lat"], pt["lon"]) for pt in sa_data]

# Coverage overlay (same size as full map, accumulates yellow)
coverage_overlay = np.zeros_like(img_full)

# Zoom state
zoom_level = 1.0
MIN_ZOOM = 1.0
MAX_ZOOM = 8.0

# Drone state
drone_px = img_w // 2
drone_py = img_h // 2

def on_mouse(event, x, y, flags, param):
    global zoom_level
    if event == cv2.EVENT_MOUSEWHEEL:
        if flags > 0:
            zoom_level = min(MAX_ZOOM, zoom_level * 1.2)
        else:
            zoom_level = max(MIN_ZOOM, zoom_level / 1.2)


# Connect
conn_str = f"tcp:{HOST}:{PORT}"
print(f"  Connecting to {conn_str}...")
print(f"  (Make sure mavproxy has --out=tcpin:0.0.0.0:{PORT})")
print()

try:
    mav = mavutil.mavlink_connection(conn_str)
except Exception as e:
    print(f"  [ERROR] Cannot connect: {e}")
    sys.exit(1)

print("  Waiting for heartbeat...")
mav.wait_heartbeat(timeout=15)
print(f"  [OK] Connected to system {mav.target_system}")

# Request data stream
mav.mav.request_data_stream_send(
    mav.target_system, mav.target_component,
    mavutil.mavlink.MAV_DATA_STREAM_ALL, 4, 1)

win = "Live Map (SCROLL=zoom, ESC=quit)"
cv2.namedWindow(win, cv2.WINDOW_AUTOSIZE)
cv2.setMouseCallback(win, on_mouse)

print()
print("  Live map running. SCROLL=zoom, ESC to quit.")
print()

while True:
    # Drain messages
    while mav.recv_msg() is not None:
        pass

    # --- Build display map (full resolution, then crop+resize) ---
    display_map = img_full.copy()

    # Blend coverage (yellow tint, same as simulation)
    cv2.addWeighted(coverage_overlay, 0.2, display_map, 1.0, 0, display_map)

    # Draw KML zones
    if config.SEARCH_AREA_GPS:
        pts = np.array([geo.gps_to_pixels(lat, lon) for lat, lon in config.SEARCH_AREA_GPS], np.int32)
        cv2.polylines(display_map, [pts], True, (0, 255, 255), 2)

    if config.FLIGHT_AREA_GPS:
        pts = np.array([geo.gps_to_pixels(lat, lon) for lat, lon in config.FLIGHT_AREA_GPS], np.int32)
        cv2.polylines(display_map, [pts], True, (0, 255, 0), 2)

    if config.SSSI_GPS:
        pts = np.array([geo.gps_to_pixels(lat, lon) for lat, lon in config.SSSI_GPS], np.int32)
        cv2.polylines(display_map, [pts], True, (0, 0, 255), 3)
        cx = sum(p[0] for p in pts) // len(pts)
        cy = sum(p[1] for p in pts) // len(pts)
        cv2.putText(display_map, "SSSI NFZ", (cx - 40, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    # Draw custom search area (from search_area.json)
    if search_area:
        pts = np.array([geo.gps_to_pixels(lat, lon) for lat, lon in search_area], np.int32)
        cv2.polylines(display_map, [pts], True, (0, 200, 0), 2)

    # Draw takeoff point
    if config.TAKEOFF_GPS:
        tx, ty = geo.gps_to_pixels(config.TAKEOFF_GPS[0], config.TAKEOFF_GPS[1])
        cv2.drawMarker(display_map, (tx, ty), (0, 0, 255), cv2.MARKER_STAR, 20, 2)
        cv2.putText(display_map, "TAKEOFF", (tx + 12, ty - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    # Draw waypoints
    for i, (lat, lon, label) in enumerate(waypoints):
        px, py = geo.gps_to_pixels(lat, lon)
        color = (0, 165, 255)
        cv2.circle(display_map, (px, py), 8, color, -1)
        cv2.putText(display_map, label, (px + 12, py - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        if i > 0:
            prev_lat, prev_lon, _ = waypoints[i - 1]
            ppx, ppy = geo.gps_to_pixels(prev_lat, prev_lon)
            cv2.line(display_map, (ppx, ppy), (px, py), (255, 165, 0), 2)

    # Get drone position
    pos = mav.messages.get('GLOBAL_POSITION_INT')
    alt = 0
    hdg = 0
    lat_now = 0
    lon_now = 0
    if pos:
        lat_now = pos.lat / 1e7
        lon_now = pos.lon / 1e7
        alt = pos.relative_alt / 1000.0
        hdg = pos.hdg / 100.0 if pos.hdg != 65535 else 0

        drone_px, drone_py = geo.gps_to_pixels(lat_now, lon_now)

        # Camera footprint and coverage stamp
        if alt > 2.0:
            ground_w = alt * config.SENSOR_WIDTH_MM / config.FOCAL_LENGTH_MM
            ground_h = ground_w * config.IMAGE_H / config.IMAGE_W
            fp_w_px = ground_w * geo.pix_per_m
            fp_h_px = ground_h * geo.pix_per_m

            # Rotated box (same as simulation)
            rect = ((drone_px, drone_py), (fp_w_px, fp_h_px), hdg)
            box = np.int32(cv2.boxPoints(rect))

            # Stamp coverage (yellow, accumulates)
            cv2.fillPoly(coverage_overlay, [box], (255, 255, 0))

            # Draw current camera footprint outline (cyan)
            cv2.drawContours(display_map, [box], 0, (0, 255, 255), 2)

        # Draw drone (blue dot + heading arrow, same as simulation)
        cv2.circle(display_map, (drone_px, drone_py), 8, (255, 0, 0), -1)
        arrow_len = 25
        rad = math.radians(hdg)
        ax = int(drone_px + arrow_len * math.sin(rad))
        ay = int(drone_py - arrow_len * math.cos(rad))
        cv2.arrowedLine(display_map, (drone_px, drone_py), (ax, ay), (0, 255, 0), 2, tipLength=0.4)

    # --- Zoom and crop (centred on drone, same as simulation) ---
    if zoom_level > 1.0:
        crop_h = int(img_h / zoom_level)
        crop_w = int(img_w / zoom_level)
        x1 = max(0, min(img_w - crop_w, drone_px - crop_w // 2))
        y1 = max(0, min(img_h - crop_h, drone_py - crop_h // 2))
        display_map = display_map[y1:y1+crop_h, x1:x1+crop_w]

    # Resize to display
    base_scale = DISPLAY_H / display_map.shape[0]
    disp_w = int(display_map.shape[1] * base_scale)
    disp = cv2.resize(display_map, (disp_w, DISPLAY_H))

    # HUD overlay (on resized display)
    cov_pct = np.count_nonzero(coverage_overlay[:,:,1]) / (img_h * img_w) * 100
    cv2.putText(disp, f"ALT: {alt:.1f}m  HDG: {hdg:.0f}  ZOOM: {zoom_level:.1f}x  COV: {cov_pct:.1f}%",
                (10, DISPLAY_H - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    if lat_now:
        cv2.putText(disp, f"GPS: {lat_now:.6f}, {lon_now:.6f}",
                    (10, DISPLAY_H - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    cv2.putText(disp, f"LIVE MAP  |  {HOST}:{PORT}  |  SCROLL=zoom  ESC=quit",
                (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)

    cv2.imshow(win, disp)
    key = cv2.waitKey(100) & 0xFF
    if key == 27:  # ESC
        break

cv2.destroyAllWindows()
mav.close()
print("  Live map closed.")
