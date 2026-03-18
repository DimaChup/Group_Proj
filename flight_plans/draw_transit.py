#!/usr/bin/env python3
"""
Draw Transit Path — interactively draw the takeoff-to-search-area route on map.jpg.

WHAT:    Opens map.jpg with KML zone overlays and lets you draw a transit path (the
         route flown from takeoff to the search area entry point). Left-click to add
         transit waypoints, right-click to undo, SPACE/ENTER to save. Outputs
         transit.json consumed by main.py as the pre-search transit route.
WHY:     The search area may not start at the takeoff point. This tool lets you plan
         a safe transit route that avoids the SSSI no-fly zone and stays within the
         flight boundary. Separates planning (laptop, with display) from execution
         (Pi, headless).
WHEN:    Before flights that use main.py with a transit route. Run once on laptop,
         push transit.json via git.
WHERE:   Laptop only (requires display for mouse interaction and map.jpg).
ENV:     Dev venv on laptop (needs opencv-python, numpy). NOT for Pi.
MODELS:  None (no AI used).
RISK:    None — pure GUI tool, no drone connection, no commands.

USAGE:
    python tests/flight/draw_transit.py

FLAGS:
    None

OUTPUT:
    transit.json in project root — array of {lat, lon, label} objects defining
    transit waypoints in order (T1, T2, ...).

BEST PRACTICES:
    - Plan the route to avoid the SSSI no-fly zone (red outline)
    - Keep within the flight boundary (green outline)
    - Start near the takeoff point (red star) and end near the search area entry
    - After saving, use with: python main.py --search-area --transit transit.json

DEPENDENCIES:
    opencv-python, numpy, config.py, utils.py (GeoTransformer)
"""
import sys
import os
import json
import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from utils import GeoTransformer

# Preserve map calibration origin
_saved_ref_lat, _saved_ref_lon = config.REF_LAT, config.REF_LON
config.load_kml_zones()
config.REF_LAT, config.REF_LON = _saved_ref_lat, _saved_ref_lon

# Output file (project root)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_FILE = os.path.join(PROJECT_ROOT, "flight_plans", "transit.json")

map_path = os.path.join(PROJECT_ROOT, config.MAP_FILE)
if not os.path.exists(map_path):
    print(f"  [ERROR] map.jpg not found at {map_path}")
    sys.exit(1)

img_full = cv2.imread(map_path)
img_h, img_w = img_full.shape[:2]
geo = GeoTransformer(img_w)

# Scale for display
max_display = 900
scale = min(max_display / img_w, max_display / img_h)
disp_w, disp_h = int(img_w * scale), int(img_h * scale)

clicked = []
done = [False]


def mouse_cb(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        fx, fy = x / scale, y / scale
        lat, lon = geo.pixels_to_gps(fx, fy)
        label = f"T{len(clicked) + 1}"
        clicked.append({"lat": lat, "lon": lon, "label": label})
        print(f"  + {label}: ({lat:.6f}, {lon:.6f})")
    elif event == cv2.EVENT_RBUTTONDOWN:
        if clicked:
            removed = clicked.pop()
            print(f"  - Removed {removed['label']}")


win = "Draw Transit Path (LEFT=add, RIGHT=undo, SPACE=save)"
cv2.namedWindow(win, cv2.WINDOW_AUTOSIZE)
cv2.setMouseCallback(win, mouse_cb)

print()
print("  Draw the transit path (flown BEFORE search pattern)")
print("  LEFT-CLICK: add transit waypoint")
print("  RIGHT-CLICK: undo last")
print("  SPACE/ENTER: save to transit.json")
print("  ESC: cancel")
print()

while not done[0]:
    disp = cv2.resize(img_full, (disp_w, disp_h))

    # Draw KML zones
    if config.SEARCH_AREA_GPS:
        pts = [geo.gps_to_pixels(lat, lon) for lat, lon in config.SEARCH_AREA_GPS]
        pts_scaled = [(int(px * scale), int(py * scale)) for px, py in pts]
        cv2.polylines(disp, [np.array(pts_scaled)], True, (0, 255, 255), 1)

    if config.FLIGHT_AREA_GPS:
        pts = [geo.gps_to_pixels(lat, lon) for lat, lon in config.FLIGHT_AREA_GPS]
        pts_scaled = [(int(px * scale), int(py * scale)) for px, py in pts]
        cv2.polylines(disp, [np.array(pts_scaled)], True, (0, 255, 0), 1)

    if config.SSSI_GPS:
        pts = [geo.gps_to_pixels(lat, lon) for lat, lon in config.SSSI_GPS]
        pts_scaled = [(int(px * scale), int(py * scale)) for px, py in pts]
        cv2.polylines(disp, [np.array(pts_scaled)], True, (0, 0, 255), 2)
        cx = sum(p[0] for p in pts_scaled) // len(pts_scaled)
        cy = sum(p[1] for p in pts_scaled) // len(pts_scaled)
        cv2.putText(disp, "SSSI NFZ", (cx - 30, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)

    if config.TAKEOFF_GPS:
        tx, ty = geo.gps_to_pixels(config.TAKEOFF_GPS[0], config.TAKEOFF_GPS[1])
        tx, ty = int(tx * scale), int(ty * scale)
        cv2.drawMarker(disp, (tx, ty), (0, 0, 255), cv2.MARKER_STAR, 15, 2)
        cv2.putText(disp, "TAKEOFF", (tx + 10, ty - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)

    # Draw transit waypoints (cyan)
    for i, wp in enumerate(clicked):
        px, py = geo.gps_to_pixels(wp["lat"], wp["lon"])
        px, py = int(px * scale), int(py * scale)
        cv2.circle(disp, (px, py), 8, (255, 255, 0), -1)
        cv2.putText(disp, wp["label"], (px + 12, py - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
        if i > 0:
            prev = clicked[i - 1]
            ppx, ppy = geo.gps_to_pixels(prev["lat"], prev["lon"])
            ppx, ppy = int(ppx * scale), int(ppy * scale)
            cv2.line(disp, (ppx, ppy), (px, py), (255, 255, 0), 2)

    # Legend
    cv2.putText(disp, "LEFT=add  RIGHT=undo  SPACE=save  ESC=cancel",
                (10, disp_h - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    cv2.putText(disp, f"Transit: {len(clicked)}  Yellow=survey Green=flight Red=SSSI/NFZ",
                (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 0), 1)

    cv2.imshow(win, disp)
    key = cv2.waitKey(50) & 0xFF
    if key == 32 and clicked:  # SPACE
        done[0] = True
    elif key == 13 and clicked:  # ENTER
        done[0] = True
    elif key == 27:  # ESC
        clicked.clear()
        done[0] = True

cv2.destroyAllWindows()

if not clicked:
    print("  No waypoints. Nothing saved.")
    sys.exit(0)

# Save
with open(OUT_FILE, "w") as f:
    json.dump(clicked, f, indent=2)

print(f"\n  Saved {len(clicked)} transit waypoints to {OUT_FILE}")
print(f"  Use with main.py:")
print(f"    python main.py --search-area --transit transit.json")
