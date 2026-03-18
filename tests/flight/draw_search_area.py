#!/usr/bin/env python3
"""
Draw Search Area — interactively draw a search polygon on map.jpg and save as JSON.

WHAT:    Opens map.jpg with KML zone overlays (survey area, flight boundary, SSSI no-fly
         zone, takeoff point). Left-click to add polygon corners, right-click to undo,
         SPACE/ENTER to save. Outputs search_area.json with GPS coordinates for each
         corner, consumed by main.py and pi_flight.py for lawnmower pattern generation.
WHY:     Separates the interactive polygon drawing step (requires a screen) from the
         headless Pi flight scripts. Draw on laptop, push JSON via git, Pi loads it
         without needing a display.
WHEN:    Before any flight that uses main.py or pi_flight.py search patterns. Run once
         on laptop, push search_area.json, reuse across flights.
WHERE:   Laptop only (requires display for mouse interaction and map.jpg).
ENV:     Dev venv on laptop (needs opencv-python, numpy). NOT for Pi.
MODELS:  None (no AI used).
RISK:    None — pure GUI tool, no drone connection, no commands.

USAGE:
    python tests/flight/draw_search_area.py

FLAGS:
    None

OUTPUT:
    search_area.json in project root — array of {lat, lon, label} objects defining
    the search polygon corners.

BEST PRACTICES:
    - Draw inside the KML flight area (green outline) and outside the SSSI (red)
    - Minimum 3 corners required to save
    - Yellow outline shows the KML survey area for reference
    - After saving, git push and git pull on Pi before flight

DEPENDENCIES:
    opencv-python, numpy, config.py, utils.py (GeoTransformer)
"""
import sys
import os
import json
import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import config
from utils import GeoTransformer

# Preserve map calibration origin
_saved_ref_lat, _saved_ref_lon = config.REF_LAT, config.REF_LON
config.load_kml_zones()
config.REF_LAT, config.REF_LON = _saved_ref_lat, _saved_ref_lon

# Output file (project root)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT_FILE = os.path.join(PROJECT_ROOT, "search_area.json")

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

polygon = []
done = [False]


def mouse_cb(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        fx, fy = x / scale, y / scale
        lat, lon = geo.pixels_to_gps(fx, fy)
        label = f"P{len(polygon) + 1}"
        polygon.append({"lat": lat, "lon": lon, "label": label})
        print(f"  + {label}: ({lat:.6f}, {lon:.6f})")
    elif event == cv2.EVENT_RBUTTONDOWN:
        if polygon:
            removed = polygon.pop()
            print(f"  - Removed {removed['label']}")


win = "Draw Search Area (LEFT=add, RIGHT=undo, SPACE=save)"
cv2.namedWindow(win, cv2.WINDOW_AUTOSIZE)
cv2.setMouseCallback(win, mouse_cb)

print()
print("  LEFT-CLICK: add polygon corner")
print("  RIGHT-CLICK: undo last")
print("  SPACE/ENTER: save to search_area.json")
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

    # Draw polygon being built
    for i, pt in enumerate(polygon):
        px, py = geo.gps_to_pixels(pt["lat"], pt["lon"])
        px, py = int(px * scale), int(py * scale)
        color = (0, 255, 0)
        cv2.circle(disp, (px, py), 6, color, -1)
        cv2.putText(disp, pt["label"], (px + 10, py - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        if i > 0:
            prev = polygon[i - 1]
            ppx, ppy = geo.gps_to_pixels(prev["lat"], prev["lon"])
            ppx, ppy = int(ppx * scale), int(ppy * scale)
            cv2.line(disp, (ppx, ppy), (px, py), (0, 255, 0), 2)
    # Close polygon visually
    if len(polygon) >= 3:
        first = polygon[0]
        last = polygon[-1]
        fpx, fpy = geo.gps_to_pixels(first["lat"], first["lon"])
        lpx, lpy = geo.gps_to_pixels(last["lat"], last["lon"])
        fpx, fpy = int(fpx * scale), int(fpy * scale)
        lpx, lpy = int(lpx * scale), int(lpy * scale)
        cv2.line(disp, (lpx, lpy), (fpx, fpy), (0, 255, 0), 1)

    # Legend
    cv2.putText(disp, "LEFT=add  RIGHT=undo  SPACE=save  ESC=cancel",
                (10, disp_h - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    cv2.putText(disp, f"Polygon corners: {len(polygon)}  Yellow=KML survey Green=your polygon Red=SSSI/NFZ",
                (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)

    cv2.imshow(win, disp)
    key = cv2.waitKey(50) & 0xFF
    if key == 32 and len(polygon) >= 3:  # SPACE
        done[0] = True
    elif key == 13 and len(polygon) >= 3:  # ENTER
        done[0] = True
    elif key == 27:  # ESC
        polygon.clear()
        done[0] = True

cv2.destroyAllWindows()

if len(polygon) < 3:
    print("  Need at least 3 points. Nothing saved.")
    sys.exit(0)

# Save
with open(OUT_FILE, "w") as f:
    json.dump(polygon, f, indent=2)

print(f"\n  Saved {len(polygon)}-point search area to {OUT_FILE}")
print(f"  Push to git, pull on Pi, then run:")
print(f"    python main.py")
print(f"    python pi_flight.py")
