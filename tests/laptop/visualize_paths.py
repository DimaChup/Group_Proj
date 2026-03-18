#!/usr/bin/env python3
"""
visualize_paths.py — Lawnmower Path Planning Visualization

WHAT:    Generates a single image showing the lawnmower search pattern for 5
         different polygon shapes: irregular pentagon, narrow corridor, L-shape,
         triangle, and the actual project survey area from config.py. Each cell
         shows the polygon, scan lines (cyan), transitions (yellow), start/end
         markers, and statistics (waypoint count, strip count, total distance).
         A 6th cell explains the algorithm.
WHY:     Visual proof that the PathPlanner handles arbitrary polygon shapes
         correctly. Useful for the project report and for verifying the
         algorithm before flight day.
WHEN:    When modifying planning.py, for report figures, or to verify search
         pattern geometry.
WHERE:   Laptop only (requires display and project imports).
ENV:     "venv" (needs opencv-python, numpy, and project modules config/planning/utils)
MODELS:  None (no AI inference).
RISK:    None — generates an image, no side effects.

USAGE:
    python tests/laptop/visualize_paths.py

FLAGS:
    None.

OUTPUT:
    path_planning_demo.jpg — 3x2 grid image saved to project root.
    Also displays the image in a window (press any key to close).

BEST PRACTICES:
    - Run after any changes to planning.py to verify pattern generation
    - Check that the project survey area (cell 5) matches expected shape

DEPENDENCIES:
    opencv-python, numpy, config.py, planning.py, utils.py
"""
import sys
import os
import math
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import cv2
import numpy as np
import config
from planning import PathPlanner
from utils import GeoTransformer

# ── Image settings ──
CELL_W = 600
CELL_H = 500
MARGIN = 40
COLS = 3
ROWS = 2

# ── Generate 5 different polygon shapes (in pixel coords within each cell) ──
def make_polygons():
    """Return 5 distinct polygon shapes as pixel coords within a cell."""
    cx, cy = CELL_W // 2, CELL_H // 2
    polys = []

    # 1. Irregular pentagon (real-world-like survey area)
    polys.append({
        "name": "Irregular Pentagon",
        "pts": [
            (120, 80), (480, 100), (500, 350), (300, 440), (80, 380)
        ]
    })

    # 2. Long narrow rectangle (corridor search)
    polys.append({
        "name": "Narrow Corridor",
        "pts": [
            (50, 180), (550, 150), (560, 300), (40, 330)
        ]
    })

    # 3. L-shape
    polys.append({
        "name": "L-Shape",
        "pts": [
            (80, 60), (300, 60), (300, 220), (500, 220),
            (500, 420), (80, 420)
        ]
    })

    # 4. Triangle
    polys.append({
        "name": "Triangle",
        "pts": [
            (300, 50), (550, 430), (50, 400)
        ]
    })

    # 5. Actual project polygon (from config.py SEARCH_AREA_GPS)
    polys.append({
        "name": "Project Survey Area",
        "pts": None  # Will be computed from GPS
    })

    return polys


def gps_poly_to_pixels(gps_pts, cell_w, cell_h, margin=40):
    """Convert GPS polygon to pixel coords fitting within a cell."""
    lats = [p[0] for p in gps_pts]
    lons = [p[1] for p in gps_pts]

    lat_min, lat_max = min(lats), max(lats)
    lon_min, lon_max = min(lons), max(lons)

    # Scale to fit cell with margin
    w = cell_w - 2 * margin
    h = cell_h - 2 * margin

    if lat_max == lat_min:
        lat_max += 0.001
    if lon_max == lon_min:
        lon_max += 0.001

    scale_x = w / (lon_max - lon_min)
    scale_y = h / (lat_max - lat_min)
    scale = min(scale_x, scale_y)

    pts = []
    for lat, lon in gps_pts:
        x = margin + (lon - lon_min) * scale
        y = margin + (lat_max - lat) * scale  # flip Y
        pts.append((int(x), int(y)))

    return pts


def run_planner_on_polygon(pixel_pts, map_w, map_h):
    """
    Run the actual PathPlanner on a pixel polygon.
    Returns list of waypoint pixel coords.
    """
    # Create a temporary GeoTransformer that maps pixels 1:1 to meters
    # We override config values temporarily
    orig_map_width = config.MAP_WIDTH_METERS
    orig_ref_lat = config.REF_LAT
    orig_ref_lon = config.REF_LON

    # Set 1 pixel = 1 meter for simplicity
    config.MAP_WIDTH_METERS = map_w
    config.REF_LAT = 0.0
    config.REF_LON = 0.0

    geo = GeoTransformer(map_w)

    planner = PathPlanner(geo, pixel_pts)
    wps_gps = planner.generate_search_pattern(map_w, map_h)

    # Convert GPS waypoints back to pixels
    wps_px = []
    for lat, lon in wps_gps:
        px = geo.gps_to_pixels(lat, lon)
        wps_px.append(px)

    virtual_poly = planner.virtual_polygon

    # Restore config
    config.MAP_WIDTH_METERS = orig_map_width
    config.REF_LAT = orig_ref_lat
    config.REF_LON = orig_ref_lon

    return wps_px, virtual_poly


def draw_cell(img, x_off, y_off, name, pixel_pts, cell_w, cell_h):
    """Draw one polygon + its lawnmower path in a cell."""
    # Cell background
    cv2.rectangle(img, (x_off, y_off), (x_off + cell_w, y_off + cell_h), (30, 30, 30), -1)
    cv2.rectangle(img, (x_off, y_off), (x_off + cell_w, y_off + cell_h), (80, 80, 80), 1)

    # Title
    cv2.putText(img, name, (x_off + 10, y_off + 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

    if not pixel_pts or len(pixel_pts) < 3:
        cv2.putText(img, "Invalid polygon", (x_off + 100, y_off + cell_h // 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        return

    # Offset pixel pts into cell position
    pts_offset = [(x + x_off, y + y_off) for x, y in pixel_pts]

    # Draw polygon fill (semi-transparent)
    overlay = img.copy()
    pts_arr = np.array([pts_offset], dtype=np.int32)
    cv2.fillPoly(overlay, pts_arr, (40, 80, 40))
    cv2.addWeighted(overlay, 0.3, img, 0.7, 0, img)

    # Draw polygon outline
    cv2.polylines(img, pts_arr, True, (0, 200, 0), 2)

    # Draw vertices
    for px, py in pts_offset:
        cv2.circle(img, (px, py), 4, (0, 255, 0), -1)

    # Run planner
    wps_px, _ = run_planner_on_polygon(
        [(x, y) for x, y in pixel_pts],  # local coords
        cell_w, cell_h
    )

    if not wps_px:
        cv2.putText(img, "No path generated", (x_off + 100, y_off + cell_h // 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        return

    # Offset waypoints into cell
    wps_offset = [(x + x_off, y + y_off) for x, y in wps_px]

    # Draw path lines
    for i in range(len(wps_offset) - 1):
        p1 = wps_offset[i]
        p2 = wps_offset[i + 1]

        # Alternate colors: scan lines = cyan, transitions = yellow
        if i % 2 == 0:
            color = (255, 200, 0)  # cyan (scan)
            thickness = 2
        else:
            color = (0, 200, 255)  # yellow (transition)
            thickness = 1

        cv2.line(img, (int(p1[0]), int(p1[1])), (int(p2[0]), int(p2[1])), color, thickness)

    # Draw start and end markers
    if wps_offset:
        cv2.circle(img, (int(wps_offset[0][0]), int(wps_offset[0][1])), 8, (0, 255, 0), -1)
        cv2.putText(img, "S", (int(wps_offset[0][0]) - 5, int(wps_offset[0][1]) + 4),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)

        cv2.circle(img, (int(wps_offset[-1][0]), int(wps_offset[-1][1])), 8, (0, 0, 255), -1)
        cv2.putText(img, "E", (int(wps_offset[-1][0]) - 5, int(wps_offset[-1][1]) + 4),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

    # Stats
    n_wps = len(wps_px)
    total_dist = 0
    for i in range(len(wps_px) - 1):
        dx = wps_px[i + 1][0] - wps_px[i][0]
        dy = wps_px[i + 1][1] - wps_px[i][1]
        total_dist += math.sqrt(dx * dx + dy * dy)

    n_strips = n_wps // 2
    cv2.putText(img, f"WPs: {n_wps}  Strips: {n_strips}  Dist: {total_dist:.0f}px",
                (x_off + 10, y_off + cell_h - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 150), 1)


def main():
    polys = make_polygons()

    # Compute project polygon pixels
    config.load_kml_zones()
    gps_pts = config.SEARCH_AREA_GPS
    if gps_pts and len(gps_pts) >= 3:
        polys[4]["pts"] = gps_poly_to_pixels(gps_pts, CELL_W, CELL_H)

    # Create canvas
    total_w = COLS * CELL_W + (COLS + 1) * MARGIN
    total_h = ROWS * CELL_H + (ROWS + 1) * MARGIN + 60  # extra for title
    img = np.zeros((total_h, total_w, 3), dtype=np.uint8)
    img[:] = (20, 20, 20)

    # Title
    cv2.putText(img, "SAR Drone — Lawnmower Path Planning: 5 Polygon Shapes",
                (MARGIN, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

    # Legend
    cv2.line(img, (MARGIN, 55), (MARGIN + 30, 55), (255, 200, 0), 2)
    cv2.putText(img, "Scan lines", (MARGIN + 35, 59), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
    cv2.line(img, (MARGIN + 140, 55), (MARGIN + 170, 55), (0, 200, 255), 1)
    cv2.putText(img, "Transitions", (MARGIN + 175, 59), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
    cv2.circle(img, (MARGIN + 290, 55), 6, (0, 255, 0), -1)
    cv2.putText(img, "Start", (MARGIN + 300, 59), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
    cv2.circle(img, (MARGIN + 360, 55), 6, (0, 0, 255), -1)
    cv2.putText(img, "End", (MARGIN + 370, 59), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)

    # Draw each polygon cell
    for i, poly in enumerate(polys):
        col = i % COLS
        row = i // COLS
        x_off = MARGIN + col * (CELL_W + MARGIN)
        y_off = 70 + MARGIN + row * (CELL_H + MARGIN)

        draw_cell(img, x_off, y_off, poly["name"], poly["pts"], CELL_W, CELL_H)

    # 6th cell: info/summary
    col = 2
    row = 1
    x_off = MARGIN + col * (CELL_W + MARGIN)
    y_off = 70 + MARGIN + row * (CELL_H + MARGIN)
    cv2.rectangle(img, (x_off, y_off), (x_off + CELL_W, y_off + CELL_H), (30, 30, 30), -1)
    cv2.rectangle(img, (x_off, y_off), (x_off + CELL_W, y_off + CELL_H), (80, 80, 80), 1)

    info_lines = [
        "Path Planning Algorithm",
        "",
        "1. Fill polygon as binary mask",
        "2. Find minimum-area bounding rect",
        "3. Rotate mask to align with longest edge",
        "4. Scan horizontal strips (lawnmower)",
        f"5. Strip width = FOV * (1 - overlap)",
        f"   FOV = {config.SENSOR_WIDTH_MM}mm * {config.TARGET_ALT}m",
        f"       / {config.FOCAL_LENGTH_MM}mm = {config.SENSOR_WIDTH_MM * config.TARGET_ALT / config.FOCAL_LENGTH_MM:.1f}m",
        f"   Overlap = 20%",
        f"   Step = {config.SENSOR_WIDTH_MM * config.TARGET_ALT / config.FOCAL_LENGTH_MM * 0.8:.1f}m",
        "6. Inverse-rotate waypoints back",
        "7. Optimise start corner (closest to drone)",
        "",
        "Adapts to ANY convex/concave polygon.",
        "Rotation minimises total path length.",
    ]

    for j, line in enumerate(info_lines):
        color = (0, 200, 255) if j == 0 else (180, 180, 180)
        scale = 0.6 if j == 0 else 0.42
        cv2.putText(img, line, (x_off + 15, y_off + 30 + j * 25),
                    cv2.FONT_HERSHEY_SIMPLEX, scale, color, 1)

    # Save
    out_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                            "path_planning_demo.jpg")
    cv2.imwrite(out_path, img, [cv2.IMWRITE_JPEG_QUALITY, 95])
    print(f"Saved: {out_path}")
    print(f"Image size: {total_w}x{total_h}")

    # Also try to show
    try:
        cv2.imshow("Path Planning Demo", img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    except Exception:
        pass


if __name__ == "__main__":
    main()
