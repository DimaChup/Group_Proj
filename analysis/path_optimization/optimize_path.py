#!/usr/bin/env python3
"""
Path Optimization Analysis for SAR Drone Lawnmower Search Pattern
=================================================================

University of Bristol MSc project (AENGM0074).

Computes the optimal altitude and scan angle for a lawnmower search pattern
over the survey polygon, considering:
  - Camera footprint geometry (sensor, focal length, altitude)
  - Altitude-dependent speed (slower at low alt for less blur)
  - NFZ (SSSI) slowdown zones (speed ramps near no-fly boundary)
  - Energy model (hover power + drag-proportional movement power)
  - U-turn penalties (deceleration + reacceleration at each turn end)

Reads real polygon geometry from the project's KML file (AENGM0074.kml).

Usage:
    cd v3/
    python analysis/path_optimization/optimize_path.py

Outputs:
    - Console table of results for every altitude
    - 4 matplotlib plots saved to analysis/path_optimization/
    - Optimal configuration summary

Author: SAR Drone Team (auto-generated analysis)
"""

import sys
import os
import math
import numpy as np
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend (no GUI needed)
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon
from matplotlib.collections import PatchCollection

# ---------------------------------------------------------------------------
# Add project root to path so we can import config
# ---------------------------------------------------------------------------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, PROJECT_ROOT)
import config

# Load the KML zones (SSSI, survey area, etc.)
kml_path = os.path.join(PROJECT_ROOT, "flight_plans", "AENGM0074.kml")
config.load_kml_zones(kml_path)

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))


# ===========================================================================
#  1. CONSTANTS FROM CONFIG
# ===========================================================================

SENSOR_W_MM   = config.SENSOR_WIDTH_MM     # 5.02 mm
FOCAL_LEN_MM  = config.FOCAL_LENGTH_MM     # 5.46 mm
IMAGE_W       = config.IMAGE_W             # 1456 px
IMAGE_H       = config.IMAGE_H             # 1088 px
OVERLAP        = 0.20                       # 20% overlap between scan lines

# NFZ parameters
NFZ_SLOW_ZONE_M     = config.NFZ_SLOW_ZONE_M       # 20 m
NFZ_MIN_SPEED_MPS   = config.NFZ_MIN_SPEED_MPS      # 0.3 m/s
NFZ_ZONE_MAX_SPEED  = config.NFZ_ZONE_MAX_SPEED_MPS # 3.0 m/s

# Energy model parameters (simplified quadcopter)
HOVER_POWER_W    = 150.0   # Watts — constant power to stay airborne
DRAG_COEFF_W     = 50.0    # Watts at reference speed (5 m/s)
DRAG_REF_SPEED   = 5.0     # m/s — reference speed for drag coefficient
U_TURN_TIME_S    = 2.0     # seconds per U-turn (decel + reaccel)

# Altitudes to evaluate
ALTITUDES = [20, 25, 30, 35, 40, 50]

# Scan angle sweep: 0 to 175 degrees in 5-degree steps
ANGLE_STEPS = list(range(0, 180, 5))

# Earth radius for local coordinate conversion
EARTH_R = 6371000.0  # metres


# ===========================================================================
#  2. COORDINATE CONVERSION UTILITIES
# ===========================================================================

def gps_to_local(lat, lon, ref_lat, ref_lon):
    """Convert GPS (lat, lon) to local (x_east, y_north) in metres."""
    lat_r = math.radians(ref_lat)
    dy = (lat - ref_lat) * (math.pi / 180.0) * EARTH_R
    dx = (lon - ref_lon) * (math.pi / 180.0) * EARTH_R * math.cos(lat_r)
    return dx, dy


def polygon_gps_to_local(gps_pts, ref_lat, ref_lon):
    """Convert list of (lat, lon) to numpy array of (x, y) in local metres."""
    return np.array([gps_to_local(lat, lon, ref_lat, ref_lon) for lat, lon in gps_pts])


# ===========================================================================
#  3. GEOMETRY HELPERS
# ===========================================================================

def polygon_area(pts):
    """Shoelace formula for polygon area. pts is Nx2 numpy array."""
    n = len(pts)
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += pts[i, 0] * pts[j, 1]
        area -= pts[j, 0] * pts[i, 1]
    return abs(area) / 2.0


def rotate_points(pts, angle_deg, cx, cy):
    """Rotate points around (cx, cy) by angle_deg (counterclockwise)."""
    theta = math.radians(angle_deg)
    cos_t, sin_t = math.cos(theta), math.sin(theta)
    shifted = pts - np.array([cx, cy])
    rotated = np.column_stack([
        shifted[:, 0] * cos_t - shifted[:, 1] * sin_t,
        shifted[:, 0] * sin_t + shifted[:, 1] * cos_t,
    ])
    return rotated + np.array([cx, cy])


def point_to_polygon_dist(px, py, poly):
    """Minimum distance from point (px, py) to polygon edges.

    Positive = outside, negative = inside (signed distance).
    For our NFZ check we only need the unsigned minimum distance to edges.
    """
    n = len(poly)
    min_dist = float("inf")
    for i in range(n):
        j = (i + 1) % n
        ax, ay = poly[i]
        bx, by = poly[j]
        # Project point onto edge segment
        dx, dy = bx - ax, by - ay
        if dx == 0 and dy == 0:
            dist = math.hypot(px - ax, py - ay)
        else:
            t = max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
            proj_x = ax + t * dx
            proj_y = ay + t * dy
            dist = math.hypot(px - proj_x, py - proj_y)
        min_dist = min(min_dist, dist)
    return min_dist


def point_in_polygon(px, py, poly):
    """Ray-casting test for point inside polygon."""
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


def segment_nfz_time(x1, y1, x2, y2, nfz_poly, search_speed, num_samples=50):
    """Compute time to traverse segment (x1,y1)-(x2,y2) accounting for NFZ slowdown.

    For each sample point along the segment, compute distance to NFZ boundary.
    If within NFZ_SLOW_ZONE_M, speed is reduced according to the ramp:
        speed = NFZ_MIN_SPEED + (dist / NFZ_SLOW_ZONE_M) * (NFZ_ZONE_MAX_SPEED - NFZ_MIN_SPEED)
    If inside the NFZ, speed = NFZ_MIN_SPEED (absolute minimum).

    Returns (time_no_nfz, time_with_nfz) in seconds.
    """
    seg_len = math.hypot(x2 - x1, y2 - y1)
    if seg_len < 0.01:
        return 0.0, 0.0

    time_no_nfz = seg_len / search_speed

    # Sample points along segment
    ds = seg_len / num_samples
    total_time = 0.0

    for k in range(num_samples):
        t = (k + 0.5) / num_samples
        px = x1 + t * (x2 - x1)
        py = y1 + t * (y2 - y1)

        # Distance to NFZ boundary
        dist = point_to_polygon_dist(px, py, nfz_poly)

        # Check if inside NFZ
        if point_in_polygon(px, py, nfz_poly):
            # Inside NFZ: minimum speed
            effective_speed = NFZ_MIN_SPEED_MPS
        elif dist < NFZ_SLOW_ZONE_M:
            # In slow zone: linear ramp from MIN at boundary to MAX at outer edge
            ratio = dist / NFZ_SLOW_ZONE_M
            effective_speed = NFZ_MIN_SPEED_MPS + ratio * (NFZ_ZONE_MAX_SPEED - NFZ_MIN_SPEED_MPS)
            # Cap at search speed (slow zone max may be less than search speed)
            effective_speed = min(effective_speed, search_speed)
        else:
            effective_speed = search_speed

        total_time += ds / max(effective_speed, 0.1)

    return time_no_nfz, total_time


# ===========================================================================
#  4. CAMERA FOOTPRINT
# ===========================================================================

def camera_footprint(alt):
    """Compute ground footprint at given altitude.

    Returns (ground_width_m, ground_height_m, swath_m).
    swath_m is the perpendicular spacing between scan lines (with overlap).
    """
    ground_w = (SENSOR_W_MM * alt) / FOCAL_LEN_MM
    ground_h = ground_w * (IMAGE_H / IMAGE_W)
    swath = ground_h * (1.0 - OVERLAP)  # Spacing uses height (perpendicular to flight)
    return ground_w, ground_h, swath


# ===========================================================================
#  5. LAWNMOWER PATTERN GENERATOR (pure geometry, no cv2 dependency)
# ===========================================================================

def generate_lawnmower(search_poly, scan_angle_deg, swath_m):
    """Generate lawnmower scan lines over a polygon at a given angle.

    Args:
        search_poly: Nx2 numpy array of polygon vertices in local metres
        scan_angle_deg: angle of scan lines (0 = East-West, 90 = North-South)
        swath_m: perpendicular spacing between scan lines

    Returns:
        list of ((x1,y1), (x2,y2)) line segments in local metres
    """
    if len(search_poly) < 3 or swath_m < 0.1:
        return []

    # Centroid for rotation
    cx = np.mean(search_poly[:, 0])
    cy = np.mean(search_poly[:, 1])

    # Rotate polygon so scan lines are horizontal
    rotated = rotate_points(search_poly, -scan_angle_deg, cx, cy)

    # Bounding box of rotated polygon
    y_min = np.min(rotated[:, 1])
    y_max = np.max(rotated[:, 1])

    # Generate horizontal scan lines in rotated frame
    margin = swath_m * 0.33  # Small inset from edges
    scan_lines_y = []
    y = y_min + margin
    while y < y_max - margin:
        scan_lines_y.append(y)
        y += swath_m
    # Ensure the last line covers the edge
    if scan_lines_y and (y_max - margin - scan_lines_y[-1]) > swath_m * 0.3:
        scan_lines_y.append(y_max - margin)

    # For each scan line, find intersection with the rotated polygon
    segments = []
    n = len(rotated)
    for sy in scan_lines_y:
        # Find all x-intersections of horizontal line y=sy with polygon edges
        intersections = []
        for i in range(n):
            j = (i + 1) % n
            y1, y2 = rotated[i, 1], rotated[j, 1]
            x1, x2 = rotated[i, 0], rotated[j, 0]

            # Check if edge crosses y=sy
            if (y1 <= sy < y2) or (y2 <= sy < y1):
                # Linear interpolation for x at y=sy
                if abs(y2 - y1) < 1e-10:
                    continue
                t = (sy - y1) / (y2 - y1)
                x_int = x1 + t * (x2 - x1)
                intersections.append(x_int)

        if len(intersections) < 2:
            continue

        intersections.sort()

        # Take pairs of intersections as entry/exit points
        for k in range(0, len(intersections) - 1, 2):
            x_start = intersections[k] + margin
            x_end = intersections[k + 1] - margin
            if x_end <= x_start:
                continue

            # Un-rotate back to local frame
            pts = np.array([[x_start, sy], [x_end, sy]])
            original = rotate_points(pts, scan_angle_deg, cx, cy)
            segments.append(((original[0, 0], original[0, 1]),
                             (original[1, 0], original[1, 1])))

    return segments


def compute_path_metrics(segments, search_speed, nfz_poly):
    """Compute total path length, time, and energy for a set of scan line segments.

    Accounts for:
    - Scan line traversal at search speed (or reduced speed near NFZ)
    - U-turn transit between consecutive scan lines
    - U-turn decel/accel penalty

    Returns dict with all metrics.
    """
    if not segments:
        return {
            "num_lines": 0, "path_length_m": 0, "time_s": 0,
            "time_nfz_s": 0, "energy_Wh": 0, "energy_nfz_Wh": 0,
        }

    num_lines = len(segments)
    total_scan_length = 0.0
    total_transit_length = 0.0
    total_time_no_nfz = 0.0
    total_time_with_nfz = 0.0
    num_u_turns = max(0, num_lines - 1)

    has_nfz = len(nfz_poly) >= 3

    for i, ((x1, y1), (x2, y2)) in enumerate(segments):
        seg_len = math.hypot(x2 - x1, y2 - y1)
        total_scan_length += seg_len

        t_no_nfz = seg_len / max(search_speed, 0.1)
        total_time_no_nfz += t_no_nfz

        if has_nfz:
            _, t_nfz = segment_nfz_time(x1, y1, x2, y2, nfz_poly, search_speed)
            total_time_with_nfz += t_nfz
        else:
            total_time_with_nfz += t_no_nfz

        # Transit to next scan line (U-turn)
        if i < num_lines - 1:
            (nx1, ny1), (nx2, ny2) = segments[i + 1]
            # Connect end of current segment to start of next
            # Lawnmower alternates direction, so connect:
            #   even line: end (x2,y2) -> next start (nx1,ny1)
            #   odd line: end (x2,y2) -> next start (nx1,ny1)
            # The generator already handles zigzag within segments,
            # but we need to connect the end of line i to start of line i+1
            # In a standard lawnmower, consecutive lines alternate direction.
            if i % 2 == 0:
                # Even line goes left->right, next goes right->left
                transit_len = math.hypot(nx2 - x2, ny2 - y2)
            else:
                # Odd line goes right->left, next goes left->right
                transit_len = math.hypot(nx1 - x1, ny1 - y1)

            total_transit_length += transit_len

    # U-turn time: transit distance at search speed + decel/accel penalty
    transit_time = total_transit_length / max(search_speed, 0.1)
    u_turn_penalty_time = num_u_turns * U_TURN_TIME_S

    # Total times
    time_no_nfz = total_time_no_nfz + transit_time + u_turn_penalty_time
    time_with_nfz = total_time_with_nfz + transit_time + u_turn_penalty_time

    total_path = total_scan_length + total_transit_length

    # Energy model
    # E = P_hover * t_total + integral(P_drag * dt) over scan segments
    # P_drag = DRAG_COEFF_W * (v / DRAG_REF_SPEED)^2
    # For scan at constant speed: E_drag_scan = DRAG_COEFF_W * (v/v_ref)^2 * t_scan
    # For U-turns (hover): E_drag_uturn = 0 (no forward movement)

    drag_power_scan = DRAG_COEFF_W * (search_speed / DRAG_REF_SPEED) ** 2

    # Without NFZ
    energy_no_nfz_J = (HOVER_POWER_W * time_no_nfz
                       + drag_power_scan * (total_time_no_nfz + transit_time)
                       + HOVER_POWER_W * 0)  # U-turn penalty is just hover
    energy_no_nfz_Wh = energy_no_nfz_J / 3600.0

    # With NFZ: drag energy is harder because speed varies.
    # Approximate: use the ratio of NFZ time to no-NFZ time as a scaling factor.
    # In slow zones, speed is lower, so drag power is lower but time is longer.
    # For a proper calculation we would integrate P_drag(v(t)) * dt,
    # but since P_drag ~ v^2 and v is reduced, and time ~ 1/v:
    #   integral(v^2 * dt) where dt = ds/v  =>  integral(v * ds) = speed * distance
    # So drag energy = DRAG_COEFF_W / v_ref^2 * integral(v^2 * ds/v)
    #               = DRAG_COEFF_W / v_ref^2 * integral(v * ds)
    # For constant speed segment: integral(v * ds) = v * L
    # For NFZ segment with varying v: we approximate with search_speed * L (conservative)
    # because the drone still covers the same distance, just slower.
    # Actually: E_drag = integral(P_drag * dt) = integral(c * v^2 * ds / v) = c * integral(v * ds)
    # In slow zone, v is reduced, so v * ds < v_search * ds. Less drag energy.
    # Hover energy dominates when speed is low.
    energy_nfz_J = (HOVER_POWER_W * time_with_nfz
                    + drag_power_scan * (total_time_no_nfz + transit_time))  # drag approx same distance
    energy_nfz_Wh = energy_nfz_J / 3600.0

    return {
        "num_lines": num_lines,
        "path_length_m": total_path,
        "scan_length_m": total_scan_length,
        "transit_length_m": total_transit_length,
        "num_u_turns": num_u_turns,
        "time_s": time_no_nfz,
        "time_nfz_s": time_with_nfz,
        "energy_Wh": energy_no_nfz_Wh,
        "energy_nfz_Wh": energy_nfz_Wh,
    }


# ===========================================================================
#  6. MAIN ANALYSIS
# ===========================================================================

def run_analysis():
    """Run the full path optimization analysis."""

    print("=" * 80)
    print("  SAR DRONE PATH OPTIMIZATION ANALYSIS")
    print("  University of Bristol MSc AENGM0074")
    print("=" * 80)

    # -----------------------------------------------------------------------
    # Load polygons
    # -----------------------------------------------------------------------
    survey_gps = config.SEARCH_AREA_GPS
    sssi_gps = config.SSSI_GPS
    takeoff_gps = config.TAKEOFF_GPS

    if len(survey_gps) < 3:
        print("ERROR: Survey area has fewer than 3 points. Check KML file.")
        sys.exit(1)

    # Reference point: centroid of survey area
    ref_lat = np.mean([p[0] for p in survey_gps])
    ref_lon = np.mean([p[1] for p in survey_gps])

    survey_local = polygon_gps_to_local(survey_gps, ref_lat, ref_lon)
    sssi_local = polygon_gps_to_local(sssi_gps, ref_lat, ref_lon) if len(sssi_gps) >= 3 else np.array([])

    survey_area_m2 = polygon_area(survey_local)

    print(f"\nSurvey polygon: {len(survey_gps)} vertices")
    print(f"Survey area:    {survey_area_m2:.0f} m^2 ({survey_area_m2/10000:.3f} hectares)")
    print(f"SSSI polygon:   {len(sssi_gps)} vertices")
    if takeoff_gps:
        print(f"Take-off:       ({takeoff_gps[0]:.6f}, {takeoff_gps[1]:.6f})")
    print(f"\nCamera: {SENSOR_W_MM} mm sensor, {FOCAL_LEN_MM} mm focal length")
    print(f"Image:  {IMAGE_W} x {IMAGE_H} px, overlap: {OVERLAP*100:.0f}%")
    print(f"NFZ slow zone: {NFZ_SLOW_ZONE_M} m, min speed: {NFZ_MIN_SPEED_MPS} m/s")
    print(f"Energy: P_hover={HOVER_POWER_W}W, P_drag={DRAG_COEFF_W}W @ {DRAG_REF_SPEED}m/s")
    print(f"U-turn penalty: {U_TURN_TIME_S} s per turn")

    # -----------------------------------------------------------------------
    # Print footprint table
    # -----------------------------------------------------------------------
    print("\n" + "-" * 70)
    print("CAMERA FOOTPRINT BY ALTITUDE")
    print("-" * 70)
    print(f"{'Alt (m)':>8} {'Gnd Width (m)':>14} {'Gnd Height (m)':>15} {'Swath (m)':>10} {'Speed (m/s)':>12}")
    for alt in ALTITUDES:
        gw, gh, sw = camera_footprint(alt)
        spd = config.speed_for_altitude(alt)
        print(f"{alt:>8} {gw:>14.1f} {gh:>15.1f} {sw:>10.1f} {spd:>12.1f}")

    # -----------------------------------------------------------------------
    # Sweep altitudes and angles
    # -----------------------------------------------------------------------
    # For each altitude, find the best scan angle
    results = []  # One entry per altitude (best angle for that altitude)
    all_results = []  # Every (altitude, angle) combo

    print("\n" + "-" * 70)
    print("SCANNING ALL ALTITUDE x ANGLE COMBINATIONS...")
    print("-" * 70)

    for alt in ALTITUDES:
        gw, gh, swath = camera_footprint(alt)
        search_speed = config.speed_for_altitude(alt)

        best_for_alt = None
        best_energy = float("inf")

        for angle in ANGLE_STEPS:
            segments = generate_lawnmower(survey_local, angle, swath)
            metrics = compute_path_metrics(segments, search_speed, sssi_local)
            metrics["altitude"] = alt
            metrics["scan_angle"] = angle
            metrics["search_speed"] = search_speed
            metrics["ground_width_m"] = gw
            metrics["ground_height_m"] = gh
            metrics["swath_m"] = swath
            all_results.append(metrics)

            # Minimize energy with NFZ as primary criterion
            if metrics["energy_nfz_Wh"] < best_energy and metrics["num_lines"] > 0:
                best_energy = metrics["energy_nfz_Wh"]
                best_for_alt = metrics

        if best_for_alt:
            results.append(best_for_alt)

    # -----------------------------------------------------------------------
    # Results table (best angle per altitude)
    # -----------------------------------------------------------------------
    print("\n" + "=" * 120)
    print("OPTIMAL SCAN ANGLE PER ALTITUDE (minimizing energy with NFZ)")
    print("=" * 120)
    header = (f"{'Alt':>4} {'Angle':>6} {'Lines':>6} {'Path (m)':>9} "
              f"{'Speed':>6} {'Time':>7} {'Time+NFZ':>9} "
              f"{'Energy':>8} {'E+NFZ':>8} {'Swath':>6} {'GndW':>6}")
    print(header)
    print("-" * 120)

    for r in results:
        print(f"{r['altitude']:>4}m {r['scan_angle']:>5}d {r['num_lines']:>6} "
              f"{r['path_length_m']:>9.0f} {r['search_speed']:>5.1f} "
              f"{r['time_s']:>6.0f}s {r['time_nfz_s']:>8.0f}s "
              f"{r['energy_Wh']:>7.1f}Wh {r['energy_nfz_Wh']:>7.1f}Wh "
              f"{r['swath_m']:>5.1f}m {r['ground_width_m']:>5.1f}m")

    # -----------------------------------------------------------------------
    # Find global optima
    # -----------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("OPTIMAL CONFIGURATIONS")
    print("=" * 80)

    # Best for energy (with NFZ)
    best_energy = min(results, key=lambda r: r["energy_nfz_Wh"])
    print(f"\nMinimum ENERGY (with NFZ slowdown):")
    print(f"  Altitude:   {best_energy['altitude']} m")
    print(f"  Scan angle: {best_energy['scan_angle']} deg")
    print(f"  Energy:     {best_energy['energy_nfz_Wh']:.1f} Wh")
    print(f"  Time:       {best_energy['time_nfz_s']:.0f} s ({best_energy['time_nfz_s']/60:.1f} min)")
    print(f"  Scan lines: {best_energy['num_lines']}")
    print(f"  Path:       {best_energy['path_length_m']:.0f} m")

    # Best for time (with NFZ)
    best_time = min(results, key=lambda r: r["time_nfz_s"])
    print(f"\nMinimum TIME (with NFZ slowdown):")
    print(f"  Altitude:   {best_time['altitude']} m")
    print(f"  Scan angle: {best_time['scan_angle']} deg")
    print(f"  Time:       {best_time['time_nfz_s']:.0f} s ({best_time['time_nfz_s']/60:.1f} min)")
    print(f"  Energy:     {best_time['energy_nfz_Wh']:.1f} Wh")
    print(f"  Scan lines: {best_time['num_lines']}")
    print(f"  Path:       {best_time['path_length_m']:.0f} m")

    # Best for energy without NFZ
    best_energy_clean = min(results, key=lambda r: r["energy_Wh"])
    print(f"\nMinimum ENERGY (without NFZ):")
    print(f"  Altitude:   {best_energy_clean['altitude']} m")
    print(f"  Scan angle: {best_energy_clean['scan_angle']} deg")
    print(f"  Energy:     {best_energy_clean['energy_Wh']:.1f} Wh")
    print(f"  Time:       {best_energy_clean['time_s']:.0f} s ({best_energy_clean['time_s']/60:.1f} min)")

    # Energy-time tradeoff: Pareto front
    # For each altitude, also report time/energy ratio
    print(f"\nENERGY EFFICIENCY (Wh per minute of search):")
    for r in results:
        eff = r["energy_nfz_Wh"] / (r["time_nfz_s"] / 60.0) if r["time_nfz_s"] > 0 else 0
        print(f"  {r['altitude']:>3}m: {eff:.2f} Wh/min  "
              f"(coverage rate: {survey_area_m2 / r['time_nfz_s']:.1f} m^2/s)")

    # -----------------------------------------------------------------------
    # Generate plots
    # -----------------------------------------------------------------------
    print(f"\nGenerating plots to: {OUTPUT_DIR}/")

    fig_width, fig_height = 10, 7

    # --- Plot 1: Energy vs Altitude ---
    fig1, ax1 = plt.subplots(figsize=(fig_width, fig_height))
    alts = [r["altitude"] for r in results]
    energy_clean = [r["energy_Wh"] for r in results]
    energy_nfz = [r["energy_nfz_Wh"] for r in results]

    ax1.plot(alts, energy_clean, "b-o", linewidth=2, markersize=8, label="Without NFZ slowdown")
    ax1.plot(alts, energy_nfz, "r-s", linewidth=2, markersize=8, label="With NFZ slowdown")
    ax1.fill_between(alts, energy_clean, energy_nfz, alpha=0.15, color="red", label="NFZ energy penalty")
    ax1.set_xlabel("Altitude (m)", fontsize=12)
    ax1.set_ylabel("Total Energy (Wh)", fontsize=12)
    ax1.set_title("Search Energy vs Altitude\n(best scan angle per altitude)", fontsize=14)
    ax1.legend(fontsize=11)
    ax1.grid(True, alpha=0.3)
    ax1.set_xticks(alts)

    # Annotate optimal
    best_idx = energy_nfz.index(min(energy_nfz))
    ax1.annotate(f"Optimal: {alts[best_idx]}m\n{energy_nfz[best_idx]:.1f} Wh",
                 xy=(alts[best_idx], energy_nfz[best_idx]),
                 xytext=(alts[best_idx] + 3, energy_nfz[best_idx] + 0.5),
                 fontsize=10, fontweight="bold",
                 arrowprops=dict(arrowstyle="->", color="red"),
                 bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow"))

    fig1.tight_layout()
    fig1.savefig(os.path.join(OUTPUT_DIR, "plot1_energy_vs_altitude.png"), dpi=150)
    print("  Saved: plot1_energy_vs_altitude.png")

    # --- Plot 2: Time vs Altitude ---
    fig2, ax2 = plt.subplots(figsize=(fig_width, fig_height))
    time_clean = [r["time_s"] / 60.0 for r in results]
    time_nfz = [r["time_nfz_s"] / 60.0 for r in results]

    ax2.plot(alts, time_clean, "b-o", linewidth=2, markersize=8, label="Without NFZ slowdown")
    ax2.plot(alts, time_nfz, "r-s", linewidth=2, markersize=8, label="With NFZ slowdown")
    ax2.fill_between(alts, time_clean, time_nfz, alpha=0.15, color="red", label="NFZ time penalty")
    ax2.set_xlabel("Altitude (m)", fontsize=12)
    ax2.set_ylabel("Total Search Time (minutes)", fontsize=12)
    ax2.set_title("Search Time vs Altitude\n(best scan angle per altitude)", fontsize=14)
    ax2.legend(fontsize=11)
    ax2.grid(True, alpha=0.3)
    ax2.set_xticks(alts)

    # Annotate optimal
    best_idx_t = time_nfz.index(min(time_nfz))
    ax2.annotate(f"Optimal: {alts[best_idx_t]}m\n{time_nfz[best_idx_t]:.1f} min",
                 xy=(alts[best_idx_t], time_nfz[best_idx_t]),
                 xytext=(alts[best_idx_t] + 3, time_nfz[best_idx_t] + 0.3),
                 fontsize=10, fontweight="bold",
                 arrowprops=dict(arrowstyle="->", color="red"),
                 bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow"))

    fig2.tight_layout()
    fig2.savefig(os.path.join(OUTPUT_DIR, "plot2_time_vs_altitude.png"), dpi=150)
    print("  Saved: plot2_time_vs_altitude.png")

    # --- Plot 3: Best Scan Angle vs Altitude ---
    fig3, ax3 = plt.subplots(figsize=(fig_width, fig_height))
    best_angles = [r["scan_angle"] for r in results]

    ax3.bar(alts, best_angles, width=3, color="steelblue", edgecolor="black", alpha=0.8)
    ax3.set_xlabel("Altitude (m)", fontsize=12)
    ax3.set_ylabel("Optimal Scan Angle (degrees)", fontsize=12)
    ax3.set_title("Optimal Scan Angle vs Altitude\n(angle minimizing energy with NFZ)", fontsize=14)
    ax3.set_xticks(alts)
    ax3.set_ylim(0, 180)
    ax3.grid(True, alpha=0.3, axis="y")

    # Add value labels on bars
    for a, ang in zip(alts, best_angles):
        ax3.text(a, ang + 3, f"{ang}d", ha="center", va="bottom", fontsize=11, fontweight="bold")

    fig3.tight_layout()
    fig3.savefig(os.path.join(OUTPUT_DIR, "plot3_scan_angle_vs_altitude.png"), dpi=150)
    print("  Saved: plot3_scan_angle_vs_altitude.png")

    # --- Plot 4: Number of Scan Lines vs Altitude ---
    fig4, ax4 = plt.subplots(figsize=(fig_width, fig_height))
    num_lines = [r["num_lines"] for r in results]

    ax4.plot(alts, num_lines, "g-^", linewidth=2, markersize=10, label="Scan lines")
    ax4.set_xlabel("Altitude (m)", fontsize=12)
    ax4.set_ylabel("Number of Scan Lines", fontsize=12)
    ax4.set_title("Scan Lines Required vs Altitude\n(at optimal scan angle)", fontsize=14)
    ax4.grid(True, alpha=0.3)
    ax4.set_xticks(alts)

    # Add secondary axis: swath width
    ax4b = ax4.twinx()
    swaths = [r["swath_m"] for r in results]
    ax4b.plot(alts, swaths, "m--D", linewidth=1.5, markersize=7, alpha=0.7, label="Swath width")
    ax4b.set_ylabel("Swath Width (m)", fontsize=12, color="purple")
    ax4b.tick_params(axis="y", labelcolor="purple")

    # Combined legend
    lines1, labels1 = ax4.get_legend_handles_labels()
    lines2, labels2 = ax4b.get_legend_handles_labels()
    ax4.legend(lines1 + lines2, labels1 + labels2, fontsize=11, loc="upper right")

    fig4.tight_layout()
    fig4.savefig(os.path.join(OUTPUT_DIR, "plot4_scan_lines_vs_altitude.png"), dpi=150)
    print("  Saved: plot4_scan_lines_vs_altitude.png")

    # --- Plot 5: Energy heatmap (altitude x angle) ---
    fig5, ax5 = plt.subplots(figsize=(12, 8))

    # Build 2D array: rows=altitudes, cols=angles
    energy_grid = np.full((len(ALTITUDES), len(ANGLE_STEPS)), np.nan)
    for entry in all_results:
        ai = ALTITUDES.index(entry["altitude"])
        aj = ANGLE_STEPS.index(entry["scan_angle"])
        energy_grid[ai, aj] = entry["energy_nfz_Wh"]

    im = ax5.imshow(energy_grid, aspect="auto", origin="lower",
                    extent=[ANGLE_STEPS[0] - 2.5, ANGLE_STEPS[-1] + 2.5,
                            ALTITUDES[0] - 2.5, ALTITUDES[-1] + 2.5],
                    cmap="viridis_r", interpolation="bilinear")
    cbar = fig5.colorbar(im, ax=ax5, label="Energy (Wh)")
    ax5.set_xlabel("Scan Angle (degrees)", fontsize=12)
    ax5.set_ylabel("Altitude (m)", fontsize=12)
    ax5.set_title("Energy Heatmap: Altitude x Scan Angle\n(darker = less energy = better)", fontsize=14)
    ax5.set_yticks(ALTITUDES)

    # Mark optimal point
    global_best = min(all_results, key=lambda r: r["energy_nfz_Wh"])
    ax5.plot(global_best["scan_angle"], global_best["altitude"], "r*",
             markersize=20, markeredgecolor="white", markeredgewidth=1.5)
    # Place annotation below the star if near top edge, otherwise above
    txt_y_offset = -8 if global_best["altitude"] >= ALTITUDES[-1] - 5 else 5
    ax5.annotate(f"Best: {global_best['altitude']}m, {global_best['scan_angle']}d\n{global_best['energy_nfz_Wh']:.1f} Wh",
                 xy=(global_best["scan_angle"], global_best["altitude"]),
                 xytext=(global_best["scan_angle"] + 25, global_best["altitude"] + txt_y_offset),
                 fontsize=10, fontweight="bold", color="white",
                 arrowprops=dict(arrowstyle="->", color="white", linewidth=2),
                 bbox=dict(boxstyle="round,pad=0.3", facecolor="black", alpha=0.7))

    fig5.tight_layout()
    fig5.savefig(os.path.join(OUTPUT_DIR, "plot5_energy_heatmap.png"), dpi=150)
    print("  Saved: plot5_energy_heatmap.png")

    # --- Plot 6: Survey area with NFZ and sample lawnmower pattern ---
    fig6, axes6 = plt.subplots(1, 2, figsize=(16, 8))

    # Left: overview map
    ax6a = axes6[0]
    survey_closed = np.vstack([survey_local, survey_local[0]])
    ax6a.plot(survey_closed[:, 0], survey_closed[:, 1], "b-", linewidth=2, label="Survey area")
    ax6a.fill(survey_local[:, 0], survey_local[:, 1], alpha=0.1, color="blue")

    if len(sssi_local) >= 3:
        sssi_closed = np.vstack([sssi_local, sssi_local[0]])
        ax6a.plot(sssi_closed[:, 0], sssi_closed[:, 1], "r-", linewidth=2, label="SSSI (NFZ)")
        ax6a.fill(sssi_local[:, 0], sssi_local[:, 1], alpha=0.15, color="red")

        # Draw NFZ buffer zone
        # Approximate by offsetting each vertex outward (simplified)
        centroid_nfz = np.mean(sssi_local, axis=0)
        buffer_pts = []
        for pt in sssi_local:
            direction = pt - centroid_nfz
            dist = np.linalg.norm(direction)
            if dist > 0:
                buffer_pts.append(pt + direction / dist * NFZ_SLOW_ZONE_M)
            else:
                buffer_pts.append(pt)
        buffer_pts = np.array(buffer_pts)
        buffer_closed = np.vstack([buffer_pts, buffer_pts[0]])
        ax6a.plot(buffer_closed[:, 0], buffer_closed[:, 1], "r--", linewidth=1, alpha=0.5,
                  label=f"NFZ buffer ({NFZ_SLOW_ZONE_M}m)")

    if takeoff_gps:
        to_local = gps_to_local(takeoff_gps[0], takeoff_gps[1], ref_lat, ref_lon)
        ax6a.plot(to_local[0], to_local[1], "g^", markersize=12, label="Take-off")

    ax6a.set_xlabel("East (m)", fontsize=11)
    ax6a.set_ylabel("North (m)", fontsize=11)
    ax6a.set_title("Survey Area Overview", fontsize=13)
    ax6a.legend(fontsize=9)
    ax6a.set_aspect("equal")
    ax6a.grid(True, alpha=0.3)

    # Right: lawnmower pattern at optimal altitude
    ax6b = axes6[1]
    opt = best_energy
    _, _, opt_swath = camera_footprint(opt["altitude"])
    opt_segments = generate_lawnmower(survey_local, opt["scan_angle"], opt_swath)

    # Draw polygon
    survey_closed = np.vstack([survey_local, survey_local[0]])
    ax6b.plot(survey_closed[:, 0], survey_closed[:, 1], "b-", linewidth=2)
    ax6b.fill(survey_local[:, 0], survey_local[:, 1], alpha=0.05, color="blue")

    if len(sssi_local) >= 3:
        sssi_closed = np.vstack([sssi_local, sssi_local[0]])
        ax6b.fill(sssi_local[:, 0], sssi_local[:, 1], alpha=0.15, color="red")
        ax6b.plot(sssi_closed[:, 0], sssi_closed[:, 1], "r-", linewidth=1.5)

    # Draw scan lines
    colors = plt.cm.cool(np.linspace(0, 1, len(opt_segments)))
    for i, ((x1, y1), (x2, y2)) in enumerate(opt_segments):
        ax6b.plot([x1, x2], [y1, y2], color=colors[i], linewidth=1.5, alpha=0.8)
        # Draw U-turn connections
        if i < len(opt_segments) - 1:
            (nx1, ny1), (nx2, ny2) = opt_segments[i + 1]
            if i % 2 == 0:
                ax6b.plot([x2, nx2], [y2, ny2], "k--", linewidth=0.5, alpha=0.4)
            else:
                ax6b.plot([x1, nx1], [y1, ny1], "k--", linewidth=0.5, alpha=0.4)

    ax6b.set_xlabel("East (m)", fontsize=11)
    ax6b.set_ylabel("North (m)", fontsize=11)
    ax6b.set_title(f"Optimal Lawnmower Pattern\n"
                   f"Alt={opt['altitude']}m, Angle={opt['scan_angle']}d, "
                   f"{opt['num_lines']} lines, {opt['energy_nfz_Wh']:.1f} Wh",
                   fontsize=13)
    ax6b.set_aspect("equal")
    ax6b.grid(True, alpha=0.3)

    fig6.tight_layout()
    fig6.savefig(os.path.join(OUTPUT_DIR, "plot6_survey_and_pattern.png"), dpi=150)
    print("  Saved: plot6_survey_and_pattern.png")

    # -----------------------------------------------------------------------
    # Detailed breakdown for each altitude
    # -----------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("DETAILED BREAKDOWN PER ALTITUDE")
    print("=" * 80)

    for r in results:
        nfz_penalty_pct = ((r["time_nfz_s"] - r["time_s"]) / r["time_s"] * 100
                           if r["time_s"] > 0 else 0)
        coverage_rate = survey_area_m2 / r["time_nfz_s"] if r["time_nfz_s"] > 0 else 0
        print(f"\n  Altitude {r['altitude']}m (speed {r['search_speed']:.1f} m/s):")
        print(f"    Scan angle:      {r['scan_angle']} deg")
        print(f"    Ground footprint: {r['ground_width_m']:.1f} x {r['ground_height_m']:.1f} m")
        print(f"    Swath spacing:   {r['swath_m']:.1f} m")
        print(f"    Scan lines:      {r['num_lines']}")
        print(f"    Scan length:     {r['scan_length_m']:.0f} m")
        print(f"    Transit length:  {r['transit_length_m']:.0f} m")
        print(f"    Total path:      {r['path_length_m']:.0f} m")
        print(f"    U-turns:         {r['num_u_turns']}")
        print(f"    Time (no NFZ):   {r['time_s']:.0f} s ({r['time_s']/60:.1f} min)")
        print(f"    Time (with NFZ): {r['time_nfz_s']:.0f} s ({r['time_nfz_s']/60:.1f} min)")
        print(f"    NFZ penalty:     +{nfz_penalty_pct:.1f}%")
        print(f"    Energy (no NFZ): {r['energy_Wh']:.1f} Wh")
        print(f"    Energy (w/ NFZ): {r['energy_nfz_Wh']:.1f} Wh")
        print(f"    Coverage rate:   {coverage_rate:.1f} m^2/s")

    # -----------------------------------------------------------------------
    # Summary recommendation
    # -----------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("RECOMMENDATION")
    print("=" * 80)
    print(f"""
For the SAR survey of {survey_area_m2:.0f} m^2 ({survey_area_m2/10000:.3f} ha) near Bristol:

  OPTIMAL ALTITUDE:  {best_energy['altitude']} m
  OPTIMAL ANGLE:     {best_energy['scan_angle']} degrees
  SEARCH SPEED:      {best_energy['search_speed']:.1f} m/s
  EXPECTED TIME:     {best_energy['time_nfz_s']/60:.1f} minutes (with NFZ slowdown)
  EXPECTED ENERGY:   {best_energy['energy_nfz_Wh']:.1f} Wh
  SCAN LINES:        {best_energy['num_lines']}
  TOTAL PATH:        {best_energy['path_length_m']:.0f} m

Higher altitudes ({ALTITUDES[-1]}m) cover more ground per pass but fly faster,
so the trade-off depends on battery capacity vs detection reliability.
Lower altitudes ({ALTITUDES[0]}m) give better detection but need more scan lines.

The current config (TARGET_ALT = {config.TARGET_ALT}m) uses
{config.speed_for_altitude(config.TARGET_ALT):.1f} m/s search speed.
""")

    print("Analysis complete. Plots saved to:")
    for f in sorted(os.listdir(OUTPUT_DIR)):
        if f.endswith(".png"):
            print(f"  {os.path.join(OUTPUT_DIR, f)}")

    plt.close("all")


# ===========================================================================
#  ENTRY POINT
# ===========================================================================

if __name__ == "__main__":
    run_analysis()
