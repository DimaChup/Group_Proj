#!/usr/bin/env python3
"""
Search Pattern Comparison Tool with Drone Physics Simulation
=============================================================

University of Bristol MSc project (AENGM0074).

Generates multiple search pattern configurations (lawnmower at various angles,
spiral, different altitudes and overlaps) and simulates realistic drone physics
along each path including:
  - Momentum (acceleration/deceleration at 3 m/s^2)
  - NFZ slowdown zone (speed ramps near SSSI boundary)
  - U-turn penalties (decelerate to 0, rotate, accelerate)
  - Energy model (hover + drag integral along path)

Outputs:
  Console comparison table
  tools/pattern_analysis/results.json
  tools/pattern_analysis/3d_scatter.png
  tools/pattern_analysis/speed_heatmap.png
  tools/pattern_analysis/nfz_time_bars.png
  tools/pattern_analysis/pareto_frontier.png

Usage:
    cd v3/
    python tools/pattern_compare.py
"""

import sys
import os
import math
import json
import itertools
import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.patches import Polygon as MplPolygon
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

# ---------------------------------------------------------------------------
# Project imports
# ---------------------------------------------------------------------------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

import config

kml_path = os.path.join(PROJECT_ROOT, "flight_plans", "AENGM0074.kml")
if os.path.exists(kml_path):
    config.load_kml_zones(kml_path)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pattern_analysis")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ===========================================================================
#  Constants
# ===========================================================================
EARTH_R = 6_371_000.0
ACCEL_MPS2 = 3.0          # Typical quadcopter acceleration
U_TURN_ROTATE_S = 1.0     # Time to rotate heading at a U-turn
HOVER_POWER_W = 150.0     # Watts to hover
DRAG_COEFF_W = 50.0       # Drag power at reference speed
DRAG_REF_SPEED = 5.0      # m/s reference for drag coefficient
PHYSICS_DT = 0.1          # Simulation timestep (seconds)

SENSOR_W_MM = config.SENSOR_WIDTH_MM
FOCAL_LEN_MM = config.FOCAL_LENGTH_MM
IMAGE_W = config.IMAGE_W
IMAGE_H = config.IMAGE_H

NFZ_SLOW_ZONE_M = config.NFZ_SLOW_ZONE_M
NFZ_SCALAR_ZERO_M = config.NFZ_SCALAR_ZERO_M
NFZ_MIN_SPEED_MPS = config.NFZ_MIN_SPEED_MPS
NFZ_ZONE_MAX_SPEED = config.NFZ_ZONE_MAX_SPEED_MPS


# ===========================================================================
#  Coordinate Conversion
# ===========================================================================

def gps_to_local(lat, lon, ref_lat, ref_lon):
    """GPS to local (x_east, y_north) in metres."""
    lat_r = math.radians(ref_lat)
    dy = (lat - ref_lat) * (math.pi / 180.0) * EARTH_R
    dx = (lon - ref_lon) * (math.pi / 180.0) * EARTH_R * math.cos(lat_r)
    return dx, dy


def local_to_gps(x, y, ref_lat, ref_lon):
    """Local (x_east, y_north) in metres to GPS."""
    lat_r = math.radians(ref_lat)
    d_lat = y / (EARTH_R * math.pi / 180.0)
    d_lon = x / (EARTH_R * math.pi / 180.0 * math.cos(lat_r))
    return ref_lat + d_lat, ref_lon + d_lon


def polygon_gps_to_local(gps_pts, ref_lat, ref_lon):
    return np.array([gps_to_local(lat, lon, ref_lat, ref_lon)
                     for lat, lon in gps_pts])


# ===========================================================================
#  Geometry Helpers
# ===========================================================================

def polygon_area(pts):
    """Shoelace formula. pts is Nx2 numpy array."""
    n = len(pts)
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += pts[i, 0] * pts[j, 1] - pts[j, 0] * pts[i, 1]
    return abs(area) / 2.0


def rotate_points(pts, angle_deg, cx, cy):
    theta = math.radians(angle_deg)
    c, s = math.cos(theta), math.sin(theta)
    shifted = pts - np.array([cx, cy])
    rotated = np.column_stack([
        shifted[:, 0] * c - shifted[:, 1] * s,
        shifted[:, 0] * s + shifted[:, 1] * c,
    ])
    return rotated + np.array([cx, cy])


def point_to_polygon_dist(px, py, poly):
    """Unsigned minimum distance from point to polygon edges."""
    n = len(poly)
    min_dist = float("inf")
    for i in range(n):
        j = (i + 1) % n
        ax, ay = poly[i]
        bx, by = poly[j]
        dx, dy = bx - ax, by - ay
        if dx == 0 and dy == 0:
            dist = math.hypot(px - ax, py - ay)
        else:
            t = max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
            dist = math.hypot(px - (ax + t * dx), py - (ay + t * dy))
        min_dist = min(min_dist, dist)
    return min_dist


def point_in_polygon(px, py, poly):
    """Ray-casting point-in-polygon test."""
    n = len(poly)
    inside = False
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > py) != (yj > py)) and (px < (xj - xi) * (py - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


# ===========================================================================
#  NFZ Speed Scalar
# ===========================================================================

def nfz_speed_scalar(px, py, nfz_poly, cruise_speed):
    """Return the allowed speed at (px, py) given NFZ proximity.

    Inside NFZ -> NFZ_MIN_SPEED_MPS
    Within NFZ_SLOW_ZONE_M -> linear ramp from NFZ_MIN at boundary to
                               NFZ_ZONE_MAX at outer edge (capped at cruise)
    Outside -> cruise_speed
    """
    if len(nfz_poly) < 3:
        return cruise_speed

    if point_in_polygon(px, py, nfz_poly):
        return max(NFZ_MIN_SPEED_MPS, 0.1)

    dist = point_to_polygon_dist(px, py, nfz_poly)

    if dist < NFZ_SCALAR_ZERO_M:
        return max(NFZ_MIN_SPEED_MPS, 0.1)

    if dist < NFZ_SLOW_ZONE_M:
        ratio = (dist - NFZ_SCALAR_ZERO_M) / (NFZ_SLOW_ZONE_M - NFZ_SCALAR_ZERO_M)
        speed = NFZ_MIN_SPEED_MPS + ratio * (NFZ_ZONE_MAX_SPEED - NFZ_MIN_SPEED_MPS)
        return min(speed, cruise_speed)

    return cruise_speed


# ===========================================================================
#  Camera Footprint
# ===========================================================================

def camera_footprint(alt, overlap):
    """Return (ground_width_m, ground_height_m, swath_m) at given altitude."""
    gw = (SENSOR_W_MM * alt) / FOCAL_LEN_MM
    gh = gw * (IMAGE_H / IMAGE_W)
    swath = gh * (1.0 - overlap)
    return gw, gh, swath


# ===========================================================================
#  Lawnmower Generator (pure geometry, no cv2)
# ===========================================================================

def generate_lawnmower(search_poly, scan_angle_deg, swath_m):
    """Generate lawnmower waypoints over polygon at given angle.

    Returns list of (x, y) waypoints in local metres (zigzag connected).
    """
    if len(search_poly) < 3 or swath_m < 0.1:
        return []

    cx = np.mean(search_poly[:, 0])
    cy = np.mean(search_poly[:, 1])
    rotated = rotate_points(search_poly, -scan_angle_deg, cx, cy)

    y_min, y_max = np.min(rotated[:, 1]), np.max(rotated[:, 1])
    margin = swath_m * 0.33

    scan_ys = []
    y = y_min + margin
    while y < y_max - margin:
        scan_ys.append(y)
        y += swath_m
    if scan_ys and (y_max - margin - scan_ys[-1]) > swath_m * 0.3:
        scan_ys.append(y_max - margin)

    n = len(rotated)
    segments = []
    for sy in scan_ys:
        intersections = []
        for i in range(n):
            j = (i + 1) % n
            y1, y2 = rotated[i, 1], rotated[j, 1]
            x1, x2 = rotated[i, 0], rotated[j, 0]
            if (y1 <= sy < y2) or (y2 <= sy < y1):
                if abs(y2 - y1) < 1e-10:
                    continue
                t = (sy - y1) / (y2 - y1)
                intersections.append(x1 + t * (x2 - x1))
        if len(intersections) < 2:
            continue
        intersections.sort()
        for k in range(0, len(intersections) - 1, 2):
            xs = intersections[k] + margin
            xe = intersections[k + 1] - margin
            if xe > xs:
                pts = np.array([[xs, sy], [xe, sy]])
                orig = rotate_points(pts, scan_angle_deg, cx, cy)
                segments.append(((orig[0, 0], orig[0, 1]),
                                 (orig[1, 0], orig[1, 1])))

    # Connect segments into zigzag waypoints
    if not segments:
        return []

    waypoints = []
    direction = 1  # 1 = left-to-right first
    for i, ((x1, y1), (x2, y2)) in enumerate(segments):
        if direction == 1:
            waypoints.append((x1, y1))
            waypoints.append((x2, y2))
        else:
            waypoints.append((x2, y2))
            waypoints.append((x1, y1))
        direction *= -1

    return waypoints


# ===========================================================================
#  Spiral Generator (pure geometry)
# ===========================================================================

def generate_spiral(search_poly, swath_m):
    """Generate inward rectangular spiral waypoints over polygon.

    Returns list of (x, y) waypoints in local metres.
    """
    if len(search_poly) < 3 or swath_m < 0.1:
        return []

    cx = np.mean(search_poly[:, 0])
    cy = np.mean(search_poly[:, 1])

    # Find optimal rotation angle (longest edge axis-aligned)
    best_angle = 0
    best_aspect = 0
    for angle in range(0, 180, 5):
        rotated = rotate_points(search_poly, -angle, cx, cy)
        w = np.max(rotated[:, 0]) - np.min(rotated[:, 0])
        h = np.max(rotated[:, 1]) - np.min(rotated[:, 1])
        aspect = max(w, h) / max(min(w, h), 0.1)
        if aspect > best_aspect:
            best_aspect = aspect
            best_angle = angle

    rotated = rotate_points(search_poly, -best_angle, cx, cy)
    x_min, x_max = np.min(rotated[:, 0]), np.max(rotated[:, 0])
    y_min, y_max = np.min(rotated[:, 1]), np.max(rotated[:, 1])

    margin = swath_m * 0.5
    top = y_min + margin
    bottom = y_max - margin
    left = x_min + margin
    right = x_max - margin

    spiral_pts_rot = []
    while top < bottom and left < right:
        # Top edge: left -> right
        x = left
        while x <= right:
            spiral_pts_rot.append((x, top))
            x += swath_m
        spiral_pts_rot.append((right, top))
        top += swath_m

        # Right edge: top -> bottom
        y = top
        while y <= bottom:
            spiral_pts_rot.append((right, y))
            y += swath_m
        spiral_pts_rot.append((right, bottom))
        right -= swath_m

        # Bottom edge: right -> left
        if top < bottom:
            x = right
            while x >= left:
                spiral_pts_rot.append((x, bottom))
                x -= swath_m
            spiral_pts_rot.append((left, bottom))
            bottom -= swath_m

        # Left edge: bottom -> top
        if left < right:
            y = bottom
            while y >= top:
                spiral_pts_rot.append((left, y))
                y -= swath_m
            spiral_pts_rot.append((left, top))
            left += swath_m

    if not spiral_pts_rot:
        return []

    # Simplify: keep only significant direction-change points
    simplified = [spiral_pts_rot[0]]
    for i in range(1, len(spiral_pts_rot) - 1):
        p0 = spiral_pts_rot[i - 1]
        p1 = spiral_pts_rot[i]
        p2 = spiral_pts_rot[i + 1]
        # Keep if direction changes
        dx1 = p1[0] - p0[0]
        dy1 = p1[1] - p0[1]
        dx2 = p2[0] - p1[0]
        dy2 = p2[1] - p1[1]
        cross = abs(dx1 * dy2 - dy1 * dx2)
        if cross > 0.01:
            simplified.append(p1)
    simplified.append(spiral_pts_rot[-1])

    # Un-rotate
    pts_arr = np.array(simplified)
    original = rotate_points(pts_arr, best_angle, cx, cy)
    return [(p[0], p[1]) for p in original]


# ===========================================================================
#  Physics Simulation
# ===========================================================================

def simulate_path_physics(waypoints, cruise_speed, nfz_poly):
    """Simulate drone flying along waypoints with momentum and NFZ slowdown.

    Returns dict with:
      - total_time_s
      - total_energy_Wh
      - nfz_zone_time_s
      - nfz_entries (count of zone entry/exit transitions)
      - speed_profile: list of (x, y, speed) along the path
      - segment_speeds: list of (x1, y1, x2, y2, avg_speed) per segment
    """
    if len(waypoints) < 2:
        return _empty_result()

    dt = PHYSICS_DT
    total_time = 0.0
    total_energy_J = 0.0
    nfz_time = 0.0
    nfz_entries = 0
    in_nfz_zone = False

    speed_profile = []
    segment_speeds = []

    current_speed = 0.0  # Start from rest

    for seg_idx in range(len(waypoints) - 1):
        x1, y1 = waypoints[seg_idx]
        x2, y2 = waypoints[seg_idx + 1]
        seg_len = math.hypot(x2 - x1, y2 - y1)

        if seg_len < 0.01:
            continue

        # Detect if this is a U-turn (large direction change)
        is_u_turn = False
        if seg_idx > 0:
            px, py = waypoints[seg_idx - 1]
            dx_prev = x1 - px
            dy_prev = y1 - py
            dx_cur = x2 - x1
            dy_cur = y2 - y1
            mag_prev = math.hypot(dx_prev, dy_prev)
            mag_cur = math.hypot(dx_cur, dy_cur)
            if mag_prev > 0.1 and mag_cur > 0.1:
                cos_angle = (dx_prev * dx_cur + dy_prev * dy_cur) / (mag_prev * mag_cur)
                cos_angle = max(-1, min(1, cos_angle))
                angle_deg = math.degrees(math.acos(cos_angle))
                if angle_deg > 90:
                    is_u_turn = True

        # U-turn: decelerate to 0, rotate, then accelerate
        if is_u_turn:
            # Deceleration phase
            decel_time = current_speed / ACCEL_MPS2
            decel_energy = (HOVER_POWER_W) * decel_time  # hover during decel + some drag
            total_time += decel_time
            total_energy_J += decel_energy
            current_speed = 0.0

            # Rotation phase
            total_time += U_TURN_ROTATE_S
            total_energy_J += HOVER_POWER_W * U_TURN_ROTATE_S

        # Direction unit vector
        ux = (x2 - x1) / seg_len
        uy = (y2 - y1) / seg_len

        # Walk along segment with physics
        dist_along = 0.0
        seg_speed_samples = []

        while dist_along < seg_len:
            # Current position
            frac = dist_along / seg_len
            px = x1 + frac * (x2 - x1)
            py = y1 + frac * (y2 - y1)

            # Target speed at this position (NFZ + cruise)
            target_speed = nfz_speed_scalar(px, py, nfz_poly, cruise_speed)

            # Check remaining distance to end of segment for deceleration
            remaining = seg_len - dist_along
            # If next waypoint is a U-turn, we need to decelerate to 0
            need_stop = False
            if seg_idx < len(waypoints) - 2:
                nx, ny = waypoints[seg_idx + 2]
                dx_next = nx - x2
                dy_next = ny - y2
                dx_cur = x2 - x1
                dy_cur = y2 - y1
                mag_n = math.hypot(dx_next, dy_next)
                mag_c = math.hypot(dx_cur, dy_cur)
                if mag_n > 0.1 and mag_c > 0.1:
                    cos_a = (dx_cur * dx_next + dy_cur * dy_next) / (mag_c * mag_n)
                    cos_a = max(-1, min(1, cos_a))
                    if math.degrees(math.acos(cos_a)) > 90:
                        need_stop = True

            if need_stop:
                # Distance needed to decelerate to 0
                stop_dist = current_speed ** 2 / (2 * ACCEL_MPS2) if ACCEL_MPS2 > 0 else 0
                if remaining <= stop_dist:
                    target_speed = min(target_speed,
                                       math.sqrt(max(0, 2 * ACCEL_MPS2 * remaining)))

            # Accelerate or decelerate toward target
            if current_speed < target_speed:
                current_speed = min(target_speed, current_speed + ACCEL_MPS2 * dt)
            elif current_speed > target_speed:
                current_speed = max(target_speed, current_speed - ACCEL_MPS2 * dt)

            current_speed = max(current_speed, 0.05)  # Never fully stop mid-segment

            # NFZ zone tracking
            is_in_zone = (len(nfz_poly) >= 3 and
                          point_to_polygon_dist(px, py, nfz_poly) < NFZ_SLOW_ZONE_M)
            if is_in_zone and not in_nfz_zone:
                nfz_entries += 1
            in_nfz_zone = is_in_zone
            if is_in_zone:
                nfz_time += dt

            # Energy for this timestep
            drag_power = DRAG_COEFF_W * (current_speed / DRAG_REF_SPEED) ** 2
            power = HOVER_POWER_W + drag_power
            total_energy_J += power * dt
            total_time += dt

            # Advance
            step = current_speed * dt
            dist_along += step
            seg_speed_samples.append(current_speed)

            speed_profile.append((px, py, current_speed))

        # Store segment average speed
        avg_spd = np.mean(seg_speed_samples) if seg_speed_samples else cruise_speed
        segment_speeds.append((x1, y1, x2, y2, avg_spd))

    return {
        "total_time_s": total_time,
        "total_energy_Wh": total_energy_J / 3600.0,
        "nfz_zone_time_s": nfz_time,
        "nfz_entries": nfz_entries,
        "speed_profile": speed_profile,
        "segment_speeds": segment_speeds,
    }


def _empty_result():
    return {
        "total_time_s": 0, "total_energy_Wh": 0, "nfz_zone_time_s": 0,
        "nfz_entries": 0, "speed_profile": [], "segment_speeds": [],
    }


# ===========================================================================
#  Coverage Estimation
# ===========================================================================

def estimate_coverage(waypoints, alt, search_poly, overlap):
    """Estimate coverage % by rasterising swath along waypoints."""
    if len(waypoints) < 2 or len(search_poly) < 3:
        return 0.0

    gw, gh, _ = camera_footprint(alt, overlap)
    half_swath_m = gh / 2.0

    # Rasterise at 0.5m resolution
    res = 0.5
    x_min = np.min(search_poly[:, 0]) - 5
    y_min = np.min(search_poly[:, 1]) - 5
    x_max = np.max(search_poly[:, 0]) + 5
    y_max = np.max(search_poly[:, 1]) + 5
    nx = int((x_max - x_min) / res) + 1
    ny = int((y_max - y_min) / res) + 1

    if nx > 2000 or ny > 2000:
        res = 1.0
        nx = int((x_max - x_min) / res) + 1
        ny = int((y_max - y_min) / res) + 1

    poly_mask = np.zeros((ny, nx), dtype=np.uint8)
    swath_mask = np.zeros((ny, nx), dtype=np.uint8)

    # Fill polygon mask
    poly_px = [((p[0] - x_min) / res, (p[1] - y_min) / res)
               for p in search_poly]
    import cv2
    poly_arr = np.array([poly_px], dtype=np.int32)
    cv2.fillPoly(poly_mask, poly_arr, 1)

    # Draw swath along path
    thickness = max(1, int(half_swath_m * 2 / res))
    for i in range(len(waypoints) - 1):
        p1 = (int((waypoints[i][0] - x_min) / res),
              int((waypoints[i][1] - y_min) / res))
        p2 = (int((waypoints[i + 1][0] - x_min) / res),
              int((waypoints[i + 1][1] - y_min) / res))
        cv2.line(swath_mask, p1, p2, 1, thickness=thickness)

    covered = np.count_nonzero(poly_mask & swath_mask)
    total = np.count_nonzero(poly_mask)
    return (covered / total * 100.0) if total > 0 else 0.0


# ===========================================================================
#  Determine "auto" scan angle (longest edge alignment)
# ===========================================================================

def auto_scan_angle(search_poly):
    """Find the angle that aligns scan lines with the polygon's longest edge."""
    best_angle = 0
    best_len = 0
    n = len(search_poly)
    for i in range(n):
        j = (i + 1) % n
        dx = search_poly[j, 0] - search_poly[i, 0]
        dy = search_poly[j, 1] - search_poly[i, 1]
        edge_len = math.hypot(dx, dy)
        if edge_len > best_len:
            best_len = edge_len
            best_angle = math.degrees(math.atan2(dy, dx))
    # Normalize to 0-180 (scan lines are symmetric)
    best_angle = best_angle % 180
    return best_angle


# ===========================================================================
#  Main Analysis
# ===========================================================================

def run_analysis():
    print("=" * 80)
    print("  SEARCH PATTERN COMPARISON — Drone Physics Simulation")
    print("  University of Bristol MSc AENGM0074")
    print("=" * 80)

    # Load polygons
    survey_gps = config.SEARCH_AREA_GPS
    sssi_gps = config.SSSI_GPS

    ref_lat = np.mean([p[0] for p in survey_gps])
    ref_lon = np.mean([p[1] for p in survey_gps])

    survey_local = polygon_gps_to_local(survey_gps, ref_lat, ref_lon)
    sssi_local = polygon_gps_to_local(sssi_gps, ref_lat, ref_lon) if len(sssi_gps) >= 3 else []
    nfz_poly = list(map(tuple, sssi_local)) if len(sssi_local) >= 3 else []

    survey_area_m2 = polygon_area(survey_local)
    auto_angle = auto_scan_angle(survey_local)

    print(f"\nSurvey area:    {survey_area_m2:.0f} m^2 ({survey_area_m2 / 10000:.3f} ha)")
    print(f"SSSI vertices:  {len(sssi_gps)}")
    print(f"Auto scan angle: {auto_angle:.1f} deg")
    print(f"NFZ slow zone:  {NFZ_SLOW_ZONE_M}m, min speed: {NFZ_MIN_SPEED_MPS} m/s")
    print(f"Acceleration:   {ACCEL_MPS2} m/s^2")
    print(f"Physics dt:     {PHYSICS_DT}s")

    # Configuration matrix
    altitudes = [20, 28, 35, 50]
    overlaps = [0.0, 0.1, 0.2, 0.3]
    scan_angles_named = {
        "auto": auto_angle,
        "0": 0.0,
        "45": 45.0,
        "90": 90.0,
    }

    # Build all configurations
    configs = []

    # Lawnmower configurations: angle x altitude x overlap
    for angle_name, angle_val in scan_angles_named.items():
        for alt in altitudes:
            for ovlp in overlaps:
                configs.append({
                    "pattern": "lawnmower",
                    "angle_name": angle_name,
                    "angle_deg": angle_val,
                    "alt_m": alt,
                    "overlap": ovlp,
                    "label": f"LM-{angle_name}deg-{alt}m-{int(ovlp*100)}%ov",
                })

    # Spiral configurations: altitude x overlap
    for alt in altitudes:
        for ovlp in overlaps:
            configs.append({
                "pattern": "spiral",
                "angle_name": "n/a",
                "angle_deg": 0,
                "alt_m": alt,
                "overlap": ovlp,
                "label": f"Spiral-{alt}m-{int(ovlp*100)}%ov",
            })

    total = len(configs)
    print(f"\nTotal configurations to simulate: {total}")
    print("-" * 80)

    results = []

    for idx, cfg in enumerate(configs):
        alt = cfg["alt_m"]
        ovlp = cfg["overlap"]
        cruise_speed = config.speed_for_altitude(alt)
        _, _, swath = camera_footprint(alt, ovlp)

        # Generate pattern
        if cfg["pattern"] == "lawnmower":
            waypoints = generate_lawnmower(survey_local, cfg["angle_deg"], swath)
        else:
            waypoints = generate_spiral(survey_local, swath)

        if len(waypoints) < 2:
            print(f"  [{idx+1}/{total}] {cfg['label']:35s} — EMPTY (swath too large)")
            results.append({**cfg, "waypoints": [], "num_waypoints": 0,
                            "path_length_m": 0, "total_time_s": 0,
                            "total_energy_Wh": 0, "coverage_pct": 0,
                            "nfz_zone_time_s": 0, "nfz_entries": 0,
                            "cruise_speed_mps": cruise_speed})
            continue

        # Path length
        path_len = sum(math.hypot(waypoints[i+1][0] - waypoints[i][0],
                                   waypoints[i+1][1] - waypoints[i][1])
                       for i in range(len(waypoints) - 1))

        # Physics simulation
        sim = simulate_path_physics(waypoints, cruise_speed, nfz_poly)

        # Coverage
        cov = estimate_coverage(waypoints, alt, survey_local, ovlp)

        r = {
            **cfg,
            "num_waypoints": len(waypoints),
            "path_length_m": round(path_len, 1),
            "total_time_s": round(sim["total_time_s"], 1),
            "total_energy_Wh": round(sim["total_energy_Wh"], 2),
            "coverage_pct": round(cov, 1),
            "nfz_zone_time_s": round(sim["nfz_zone_time_s"], 1),
            "nfz_entries": sim["nfz_entries"],
            "cruise_speed_mps": cruise_speed,
            "segment_speeds": sim["segment_speeds"],
            "speed_profile": sim["speed_profile"],
        }
        results.append(r)

        if (idx + 1) % 10 == 0 or idx == total - 1:
            print(f"  [{idx+1}/{total}] {cfg['label']:35s} | "
                  f"{len(waypoints):3d} wps | {path_len:6.0f}m | "
                  f"{sim['total_time_s']:6.0f}s ({sim['total_time_s']/60:.1f}min) | "
                  f"{sim['total_energy_Wh']:5.1f} Wh | {cov:5.1f}% cov | "
                  f"NFZ: {sim['nfz_zone_time_s']:.0f}s, {sim['nfz_entries']} entries")

    # ==================================================================
    #  Console Table
    # ==================================================================
    print("\n" + "=" * 130)
    print(f"{'Label':35s} | {'Alt':>3s} | {'Ovlp':>4s} | {'WPs':>3s} | "
          f"{'Path(m)':>7s} | {'Time(s)':>7s} | {'min':>5s} | "
          f"{'Energy(Wh)':>10s} | {'Cov%':>5s} | {'NFZ(s)':>6s} | {'NFZx':>4s}")
    print("-" * 130)
    for r in results:
        if r["num_waypoints"] == 0:
            continue
        print(f"{r['label']:35s} | {r['alt_m']:3d} | "
              f"{int(r['overlap']*100):3d}% | {r['num_waypoints']:3d} | "
              f"{r['path_length_m']:7.0f} | {r['total_time_s']:7.0f} | "
              f"{r['total_time_s']/60:5.1f} | {r['total_energy_Wh']:10.1f} | "
              f"{r['coverage_pct']:5.1f} | {r['nfz_zone_time_s']:6.0f} | "
              f"{r['nfz_entries']:4d}")
    print("=" * 130)

    # ==================================================================
    #  Save JSON (without speed_profile and segment_speeds — too large)
    # ==================================================================
    json_results = []
    for r in results:
        jr = {k: v for k, v in r.items()
              if k not in ("speed_profile", "segment_speeds", "waypoints")}
        json_results.append(jr)

    json_path = os.path.join(OUTPUT_DIR, "results.json")
    with open(json_path, "w") as f:
        json.dump(json_results, f, indent=2)
    print(f"\nSaved: {json_path}")

    # ==================================================================
    #  Plots
    # ==================================================================
    valid = [r for r in results if r["num_waypoints"] > 0]

    # Colors by pattern type
    colors_map = {"lawnmower": "#2196F3", "spiral": "#FF5722"}

    # --- Plot 1: 3D Scatter (Time vs Energy vs Coverage) ---
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection="3d")

    for r in valid:
        c = colors_map[r["pattern"]]
        marker = "o" if r["pattern"] == "lawnmower" else "^"
        ax.scatter(r["total_time_s"] / 60, r["total_energy_Wh"],
                   r["coverage_pct"], c=c, marker=marker, s=40, alpha=0.7)

    ax.set_xlabel("Time (min)")
    ax.set_ylabel("Energy (Wh)")
    ax.set_zlabel("Coverage (%)")
    ax.set_title("Search Pattern Comparison:\nTime vs Energy vs Coverage")

    # Legend
    from matplotlib.lines import Line2D
    legend_els = [
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#2196F3",
               markersize=10, label="Lawnmower"),
        Line2D([0], [0], marker="^", color="w", markerfacecolor="#FF5722",
               markersize=10, label="Spiral"),
    ]
    ax.legend(handles=legend_els, loc="upper left")

    scatter_path = os.path.join(OUTPUT_DIR, "3d_scatter.png")
    plt.savefig(scatter_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {scatter_path}")

    # --- Plot 2: Speed Heatmap (best lawnmower + spiral at 35m, 20% overlap) ---
    fig, axes = plt.subplots(1, 2, figsize=(18, 8))

    # Find 35m, 20% overlap, auto-angle lawnmower and spiral
    heatmap_configs = [
        ("Lawnmower (auto, 35m, 20%)", "lawnmower", "auto", 35, 0.2),
        ("Spiral (35m, 20%)", "spiral", "n/a", 35, 0.2),
    ]

    for ax_idx, (title, pat, ang, alt, ovlp) in enumerate(heatmap_configs):
        ax = axes[ax_idx]
        target_r = None
        for r in valid:
            if (r["pattern"] == pat and r["angle_name"] == ang
                    and r["alt_m"] == alt and abs(r["overlap"] - ovlp) < 0.01):
                target_r = r
                break

        if target_r is None or not target_r.get("segment_speeds"):
            ax.set_title(f"{title} — NO DATA")
            continue

        # Draw survey polygon
        poly_xs = list(survey_local[:, 0]) + [survey_local[0, 0]]
        poly_ys = list(survey_local[:, 1]) + [survey_local[0, 1]]
        ax.fill(poly_xs, poly_ys, alpha=0.08, color="gray")
        ax.plot(poly_xs, poly_ys, "k-", linewidth=1.5, label="Survey")

        # Draw SSSI polygon
        if len(nfz_poly) >= 3:
            nfz_xs = [p[0] for p in nfz_poly] + [nfz_poly[0][0]]
            nfz_ys = [p[1] for p in nfz_poly] + [nfz_poly[0][1]]
            ax.fill(nfz_xs, nfz_ys, alpha=0.15, color="red")
            ax.plot(nfz_xs, nfz_ys, "r--", linewidth=1.5, label="SSSI NFZ")

        # Draw NFZ slow zone boundary (approximate)
        if len(nfz_poly) >= 3:
            # Sample points around NFZ at NFZ_SLOW_ZONE_M distance
            nfz_center_x = np.mean([p[0] for p in nfz_poly])
            nfz_center_y = np.mean([p[1] for p in nfz_poly])
            ax.annotate(f"Slow zone\n({NFZ_SLOW_ZONE_M}m)",
                        xy=(nfz_center_x, nfz_center_y),
                        fontsize=8, ha="center", color="red", alpha=0.7)

        # Color segments by speed
        segs = target_r["segment_speeds"]
        speeds = [s[4] for s in segs]
        if speeds:
            vmin = min(speeds)
            vmax = max(speeds)
            lines = [[(s[0], s[1]), (s[2], s[3])] for s in segs]
            lc = LineCollection(lines, cmap="RdYlGn", linewidths=2.5)
            lc.set_array(np.array(speeds))
            lc.set_clim(vmin, vmax)
            ax.add_collection(lc)
            cb = plt.colorbar(lc, ax=ax, shrink=0.7, pad=0.02)
            cb.set_label("Speed (m/s)")

        ax.set_title(title)
        ax.set_aspect("equal")
        ax.set_xlabel("East (m)")
        ax.set_ylabel("North (m)")
        ax.legend(fontsize=8, loc="upper right")

    plt.suptitle("Speed Heatmap Along Search Path\n"
                 "Green = fast (cruise), Red = slow (NFZ zone)",
                 fontsize=13, fontweight="bold")
    plt.tight_layout()
    heatmap_path = os.path.join(OUTPUT_DIR, "speed_heatmap.png")
    plt.savefig(heatmap_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {heatmap_path}")

    # --- Plot 3: NFZ Zone Time Bars (spiral vs lawnmower by altitude) ---
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Aggregate by pattern + altitude (use 20% overlap, auto angle for LM)
    nfz_data = {"lawnmower": {}, "spiral": {}}
    nfz_entries_data = {"lawnmower": {}, "spiral": {}}
    for r in valid:
        if abs(r["overlap"] - 0.2) > 0.01:
            continue
        if r["pattern"] == "lawnmower" and r["angle_name"] != "auto":
            continue
        nfz_data[r["pattern"]][r["alt_m"]] = r["nfz_zone_time_s"]
        nfz_entries_data[r["pattern"]][r["alt_m"]] = r["nfz_entries"]

    x = np.arange(len(altitudes))
    bar_w = 0.35

    lm_times = [nfz_data["lawnmower"].get(a, 0) for a in altitudes]
    sp_times = [nfz_data["spiral"].get(a, 0) for a in altitudes]
    lm_entries = [nfz_entries_data["lawnmower"].get(a, 0) for a in altitudes]
    sp_entries = [nfz_entries_data["spiral"].get(a, 0) for a in altitudes]

    ax1.bar(x - bar_w / 2, lm_times, bar_w, label="Lawnmower (auto)",
            color="#2196F3", alpha=0.85)
    ax1.bar(x + bar_w / 2, sp_times, bar_w, label="Spiral",
            color="#FF5722", alpha=0.85)
    ax1.set_ylabel("Time in NFZ slow zone (s)")
    ax1.set_title("NFZ Zone Time by Altitude")
    ax1.set_xticks(x)
    ax1.set_xticklabels([f"{a}m" for a in altitudes])
    ax1.legend()

    for i, (lt, st) in enumerate(zip(lm_times, sp_times)):
        ax1.text(i - bar_w / 2, lt + 0.5, f"{lt:.0f}s", ha="center", fontsize=8)
        ax1.text(i + bar_w / 2, st + 0.5, f"{st:.0f}s", ha="center", fontsize=8)

    ax2.bar(x - bar_w / 2, lm_entries, bar_w, label="Lawnmower (auto)",
            color="#2196F3", alpha=0.85)
    ax2.bar(x + bar_w / 2, sp_entries, bar_w, label="Spiral",
            color="#FF5722", alpha=0.85)
    ax2.set_ylabel("Number of NFZ zone entries")
    ax2.set_title("NFZ Zone Entries by Altitude")
    ax2.set_xticks(x)
    ax2.set_xticklabels([f"{a}m" for a in altitudes])
    ax2.legend()

    for i, (le, se) in enumerate(zip(lm_entries, sp_entries)):
        ax2.text(i - bar_w / 2, le + 0.2, str(le), ha="center", fontsize=8)
        ax2.text(i + bar_w / 2, se + 0.2, str(se), ha="center", fontsize=8)

    plt.suptitle("NFZ Impact: Lawnmower vs Spiral (20% overlap)",
                 fontsize=13, fontweight="bold")
    plt.tight_layout()
    nfz_path = os.path.join(OUTPUT_DIR, "nfz_time_bars.png")
    plt.savefig(nfz_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {nfz_path}")

    # --- Plot 4: Pareto Frontier (Time vs Energy, coverage as color) ---
    fig, ax = plt.subplots(figsize=(12, 8))

    times = np.array([r["total_time_s"] / 60 for r in valid])
    energies = np.array([r["total_energy_Wh"] for r in valid])
    coverages = np.array([r["coverage_pct"] for r in valid])

    # Separate by pattern
    for pat, marker in [("lawnmower", "o"), ("spiral", "^")]:
        mask = np.array([r["pattern"] == pat for r in valid])
        if not np.any(mask):
            continue
        sc = ax.scatter(times[mask], energies[mask], c=coverages[mask],
                        cmap="viridis", marker=marker, s=60, alpha=0.8,
                        edgecolors="k", linewidths=0.5,
                        vmin=0, vmax=100)

    cb = plt.colorbar(sc, ax=ax)
    cb.set_label("Coverage (%)")

    # Find and draw Pareto frontier
    # Pareto optimal: no other point has both lower time AND lower energy
    pareto_pts = []
    for i, r in enumerate(valid):
        dominated = False
        for j, r2 in enumerate(valid):
            if i == j:
                continue
            if (r2["total_time_s"] <= r["total_time_s"] and
                    r2["total_energy_Wh"] <= r["total_energy_Wh"] and
                    (r2["total_time_s"] < r["total_time_s"] or
                     r2["total_energy_Wh"] < r["total_energy_Wh"])):
                dominated = True
                break
        if not dominated:
            pareto_pts.append((r["total_time_s"] / 60, r["total_energy_Wh"],
                               r["label"]))

    if pareto_pts:
        pareto_pts.sort(key=lambda p: p[0])
        px = [p[0] for p in pareto_pts]
        py = [p[1] for p in pareto_pts]
        ax.plot(px, py, "r--", linewidth=1.5, alpha=0.7, label="Pareto frontier")

        # Label a few key Pareto points
        for i, (ppx, ppy, lbl) in enumerate(pareto_pts):
            if i % max(1, len(pareto_pts) // 5) == 0 or i == len(pareto_pts) - 1:
                short_label = lbl.replace("LM-", "").replace("Spiral-", "S:")
                ax.annotate(short_label, (ppx, ppy), fontsize=6,
                            textcoords="offset points", xytext=(5, 5),
                            alpha=0.8)

    # Legend
    legend_els = [
        Line2D([0], [0], marker="o", color="w", markerfacecolor="gray",
               markersize=10, label="Lawnmower"),
        Line2D([0], [0], marker="^", color="w", markerfacecolor="gray",
               markersize=10, label="Spiral"),
        Line2D([0], [0], linestyle="--", color="r", label="Pareto frontier"),
    ]
    ax.legend(handles=legend_els, loc="upper left")

    ax.set_xlabel("Total Search Time (min)")
    ax.set_ylabel("Total Energy (Wh)")
    ax.set_title("Pareto Frontier: Time vs Energy\n(color = coverage %)")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    pareto_path = os.path.join(OUTPUT_DIR, "pareto_frontier.png")
    plt.savefig(pareto_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {pareto_path}")

    # ==================================================================
    #  Summary: best configs
    # ==================================================================
    print("\n" + "=" * 80)
    print("  SUMMARY — BEST CONFIGURATIONS")
    print("=" * 80)

    # Best by time (with > 80% coverage)
    high_cov = [r for r in valid if r["coverage_pct"] >= 80]
    if high_cov:
        best_time = min(high_cov, key=lambda r: r["total_time_s"])
        print(f"\nFastest (>80% cov): {best_time['label']}")
        print(f"  Time: {best_time['total_time_s']:.0f}s ({best_time['total_time_s']/60:.1f} min)")
        print(f"  Energy: {best_time['total_energy_Wh']:.1f} Wh")
        print(f"  Coverage: {best_time['coverage_pct']:.1f}%")
        print(f"  NFZ time: {best_time['nfz_zone_time_s']:.0f}s, entries: {best_time['nfz_entries']}")

    # Best by energy (with > 80% coverage)
    if high_cov:
        best_energy = min(high_cov, key=lambda r: r["total_energy_Wh"])
        print(f"\nMost efficient (>80% cov): {best_energy['label']}")
        print(f"  Time: {best_energy['total_time_s']:.0f}s ({best_energy['total_time_s']/60:.1f} min)")
        print(f"  Energy: {best_energy['total_energy_Wh']:.1f} Wh")
        print(f"  Coverage: {best_energy['coverage_pct']:.1f}%")

    # Least NFZ impact
    with_nfz = [r for r in valid if r["nfz_zone_time_s"] > 0]
    if with_nfz:
        least_nfz = min(with_nfz, key=lambda r: r["nfz_zone_time_s"])
        print(f"\nLeast NFZ impact: {least_nfz['label']}")
        print(f"  NFZ time: {least_nfz['nfz_zone_time_s']:.0f}s, entries: {least_nfz['nfz_entries']}")

    # Best coverage
    best_cov = max(valid, key=lambda r: r["coverage_pct"])
    print(f"\nBest coverage: {best_cov['label']}")
    print(f"  Coverage: {best_cov['coverage_pct']:.1f}%")
    print(f"  Time: {best_cov['total_time_s']:.0f}s ({best_cov['total_time_s']/60:.1f} min)")

    print(f"\nAll results saved to: {OUTPUT_DIR}/")
    print("Done.")


if __name__ == "__main__":
    run_analysis()
