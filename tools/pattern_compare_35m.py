#!/usr/bin/env python3
"""
Lawnmower vs Zian Spiral at FIXED 35m — Overlap Sweep Comparison
=================================================================

Generates both patterns at 35m altitude across 9 overlap values (0-40%),
simulates realistic drone physics, and produces ONE publication-quality
comparison figure.

Usage:
    cd v3/
    python tools/pattern_compare_35m.py

Output:
    tools/pattern_analysis/compare_35m.png
"""

import sys
import os
import math
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
import numpy as np

# ---------------------------------------------------------------------------
# Project imports
# ---------------------------------------------------------------------------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

import config

kml_path = os.path.join(PROJECT_ROOT, "flight_plans", "AENGM0074.kml")
if os.path.exists(kml_path):
    config.load_kml_zones(kml_path)

from tools.path_physics import (
    simulate_path, SimulationResult, gps_to_local, camera_footprint,
)
from planning import PathPlanner
from utils import GeoTransformer

# Zian's planner
ZIAN_DIR = os.path.join(PROJECT_ROOT, "Zian", "path_planner")
sys.path.insert(0, ZIAN_DIR)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pattern_analysis")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Shapely
try:
    from shapely.geometry import Polygon as ShapelyPolygon, LineString
    from shapely.ops import unary_union
    HAS_SHAPELY = True
except ImportError:
    HAS_SHAPELY = False
    print("[WARN] Shapely not installed. Coverage will be estimated.")

# ===========================================================================
#  Constants
# ===========================================================================
CANVAS_SIZE = 4800
ALTITUDE = 35.0
OVERLAPS = [0.0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40]

TARGET_REAL_RADIUS_M = config.TARGET_REAL_RADIUS_M
FOCAL_LENGTH_PX = config.FOCAL_LENGTH_MM * config.IMAGE_W / config.SENSOR_WIDTH_MM
PI_FPS = 4.8

# Colors
COLOR_LM = "#2196F3"
COLOR_SP = "#FF9800"

# ===========================================================================
#  Coordinate helpers
# ===========================================================================
def _ref_point():
    lats = [p[0] for p in config.SEARCH_AREA_GPS]
    lons = [p[1] for p in config.SEARCH_AREA_GPS]
    return sum(lats) / len(lats), sum(lons) / len(lons)

REF_LAT, REF_LON = _ref_point()


def search_poly_local():
    return [gps_to_local(lat, lon, REF_LAT, REF_LON)
            for lat, lon in config.SEARCH_AREA_GPS]


# ===========================================================================
#  Strip spacing
# ===========================================================================
def compute_strip_spacing(altitude, overlap):
    footprint_w, footprint_h = camera_footprint(altitude)
    strip_spacing = footprint_h * (1.0 - overlap)
    return strip_spacing, footprint_w, footprint_h


# ===========================================================================
#  Lawnmower generation
# ===========================================================================
def generate_lawnmower_wps(altitude, overlap):
    geo = GeoTransformer(CANVAS_SIZE)
    search_px = [geo.gps_to_pixels(lat, lon) for lat, lon in config.SEARCH_AREA_GPS]
    planner = PathPlanner(geo, search_px)
    planner._no_turn = True
    # PathPlanner._no_turn forces overlap=0 internally. We override this by
    # setting a custom attribute that we read via a monkey-patch on the method.
    planner._overlap_val = overlap

    # Monkey-patch the generate method to inject our overlap
    import types

    def _patched_generate(self, map_w, map_h, drone_gps=None, alt_override=None):
        """Generate lawnmower with custom overlap (patched for comparison)."""
        import cv2
        if len(self.search_polygon) < 3:
            return []
        search_alt = alt_override or config.TARGET_ALT
        print(f"[PLANNER] Calculating Optimum Path (alt={search_alt:.0f}m)")

        mask = np.zeros((map_h, map_w), dtype=np.uint8)
        poly_pts = np.array([self.search_polygon], dtype=np.int32)
        cv2.fillPoly(mask, poly_pts, 255)
        self.virtual_polygon = poly_pts.reshape(-1, 1, 2)

        rect = cv2.minAreaRect(poly_pts[0])
        (center, size, angle) = rect
        scan_angle = angle + 90 if size[0] < size[1] else angle
        self.last_scan_angle = scan_angle

        rotation_mat = cv2.getRotationMatrix2D(center, scan_angle, 1.0)
        inverse_rotation = cv2.invertAffineTransform(rotation_mat)
        rotated_mask = cv2.warpAffine(mask, rotation_mat, (map_w, map_h))

        # Use footprint HEIGHT with our custom overlap
        ground_footprint_w = (config.SENSOR_WIDTH_MM * search_alt) / config.FOCAL_LENGTH_MM
        aspect = config.IMAGE_H / config.IMAGE_W
        ground_footprint_h = ground_footprint_w * aspect
        swath_m = ground_footprint_h * (1.0 - self._overlap_val)
        strip_spacing_px = max(1, int(swath_m * self.pix_per_m))

        points = cv2.findNonZero(rotated_mask)
        if points is None:
            return []
        bbox_x, bbox_y, bbox_w, bbox_h = cv2.boundingRect(points)

        all_strips = []
        inset_px = strip_spacing_px // 3
        bottom_limit = bbox_y + bbox_h - inset_px
        prev_scan_y = -999

        scan_lines = list(range(bbox_y + inset_px, bbox_y + bbox_h, strip_spacing_px))
        if not scan_lines or scan_lines[-1] < bottom_limit:
            scan_lines.append(bottom_limit)

        for scan_y in scan_lines:
            scan_y = min(scan_y, bottom_limit)
            if scan_y == prev_scan_y:
                continue
            prev_scan_y = scan_y
            row = rotated_mask[scan_y, :]
            filled_cols = np.where(row == 255)[0]
            if len(filled_cols) > 0:
                x_start = filled_cols[0] + inset_px
                x_end = filled_cols[-1] - inset_px
                if x_end > x_start:
                    all_strips.append([(x_start, scan_y), (x_end, scan_y)])
                else:
                    x_mid = (filled_cols[0] + filled_cols[-1]) // 2
                    all_strips.append([(x_mid, scan_y), (x_mid, scan_y)])

        direction = 1
        if drone_gps and all_strips:
            drone_px = self.geo.gps_to_pixels(drone_gps[0], drone_gps[1])
            def _sq_dist_to_map(rotated_pt):
                pt_arr = np.array([[rotated_pt]], dtype=np.float32)
                map_pt = cv2.transform(pt_arr, inverse_rotation)[0][0]
                return (map_pt[0] - drone_px[0]) ** 2 + (map_pt[1] - drone_px[1]) ** 2
            first_strip = all_strips[0]
            last_strip = all_strips[-1]
            d_top_left = _sq_dist_to_map(first_strip[0])
            d_top_right = _sq_dist_to_map(first_strip[1])
            d_bot_left = _sq_dist_to_map(last_strip[0])
            d_bot_right = _sq_dist_to_map(last_strip[1])
            min_dist = min(d_top_left, d_top_right, d_bot_left, d_bot_right)
            if min_dist == d_bot_left or min_dist == d_bot_right:
                all_strips.reverse()
                d_left = _sq_dist_to_map(all_strips[0][0])
                d_right = _sq_dist_to_map(all_strips[0][1])
            else:
                d_left = d_top_left
                d_right = d_top_right
            if d_right < d_left:
                direction = -1

        waypoints = []
        for strip in all_strips:
            if direction == -1:
                pt_start, pt_end = strip[1], strip[0]
            else:
                pt_start, pt_end = strip[0], strip[1]
            pts_rot = np.array([[pt_start, pt_end]], dtype=np.float32)
            pts_orig = cv2.transform(pts_rot, inverse_rotation)[0]
            waypoints.append(self.geo.pixels_to_gps(pts_orig[0][0], pts_orig[0][1]))
            waypoints.append(self.geo.pixels_to_gps(pts_orig[1][0], pts_orig[1][1]))
            direction *= -1

        if len(waypoints) >= 2:
            deduped = [waypoints[0]]
            for wp in waypoints[1:]:
                if abs(wp[0] - deduped[-1][0]) > 1e-9 or abs(wp[1] - deduped[-1][1]) > 1e-9:
                    deduped.append(wp)
            waypoints = deduped

        return waypoints

    planner.generate_search_pattern = types.MethodType(_patched_generate, planner)
    wps = planner.generate_search_pattern(
        CANVAS_SIZE, CANVAS_SIZE,
        drone_gps=config.TAKEOFF_GPS,
        alt_override=altitude,
    )
    return wps


# ===========================================================================
#  Zian spiral generation
# ===========================================================================
def generate_zian_spiral_wps(altitude, overlap):
    strip_spacing, footprint_w, footprint_h = compute_strip_spacing(altitude, overlap)
    import perimeter_planner as zpp
    zpp.HALF_SWATH = footprint_h / 3.0
    zpp.SWATH = footprint_h * (1.0 - overlap)
    waypoints_dicts = zpp.plan()
    wps = []
    for wp in waypoints_dicts:
        if wp["name"] == "enter":
            continue
        wps.append((wp["lat"], wp["lon"]))
    return wps


# ===========================================================================
#  Coverage (Shapely)
# ===========================================================================
def compute_coverage_shapely(waypoints_gps, footprint_h, search_polygon_gps):
    if not HAS_SHAPELY or len(waypoints_gps) < 2:
        return 0.0
    search_local = [gps_to_local(lat, lon, REF_LAT, REF_LON)
                    for lat, lon in search_polygon_gps]
    search_poly = ShapelyPolygon(search_local)
    if not search_poly.is_valid:
        search_poly = search_poly.buffer(0)
    wps_local = [gps_to_local(lat, lon, REF_LAT, REF_LON)
                 for lat, lon in waypoints_gps]
    half_buf = footprint_h / 2.0
    buffers = []
    for i in range(len(wps_local) - 1):
        seg = LineString([wps_local[i], wps_local[i + 1]])
        if seg.length > 0.01:
            buffers.append(seg.buffer(half_buf, cap_style=2))
    if not buffers:
        return 0.0
    covered = unary_union(buffers)
    covered_in_poly = covered.intersection(search_poly)
    poly_area = search_poly.area
    if poly_area < 1.0:
        return 0.0
    return covered_in_poly.area / poly_area


# ===========================================================================
#  Detection probability
# ===========================================================================
def sigmoid(x, midpoint=12.0, steepness=0.5):
    return 1.0 / (1.0 + math.exp(-steepness * (x - midpoint)))


def compute_detection_prob(altitude, avg_speed, footprint_w):
    pixel_size = (TARGET_REAL_RADIUS_M * 2 * FOCAL_LENGTH_PX) / altitude
    p_single = sigmoid(pixel_size)
    blur = 1.0 / (1.0 + 0.008 * avg_speed ** 2)
    if avg_speed < 0.01:
        effective_frames = PI_FPS * 10
    else:
        time_in_view = footprint_w / avg_speed
        effective_frames = time_in_view * PI_FPS * blur
    p_detect = 1.0 - (1.0 - p_single) ** max(effective_frames, 1)
    return p_detect


# ===========================================================================
#  Directional NFZ time
# ===========================================================================
def compute_directional_nfz_time(sim_result, sssi_polygon_gps):
    if not sssi_polygon_gps or len(sssi_polygon_gps) < 3:
        return 0.0, 0.0
    nfz_local = np.array([gps_to_local(lat, lon, REF_LAT, REF_LON)
                          for lat, lon in sssi_polygon_gps])
    directional_time = 0.0
    total_time = 0.0
    points = sim_result.points
    if len(points) < 2:
        return 0.0, 0.0
    for i in range(1, len(points)):
        pt = points[i]
        prev_pt = points[i - 1]
        dt = pt.cumulative_time_s - prev_pt.cumulative_time_s
        total_time += dt
        if pt.dist_to_nfz_m > 40.0:
            continue
        heading_rad = math.radians(pt.heading_deg)
        hx = math.sin(heading_rad)
        hy = math.cos(heading_rad)
        px, py = pt.x_m, pt.y_m
        min_dist = float("inf")
        nearest_x, nearest_y = 0, 0
        n = len(nfz_local)
        for j in range(n):
            ax, ay = nfz_local[j]
            bx, by = nfz_local[(j + 1) % n]
            dx, dy = bx - ax, by - ay
            len_sq = dx * dx + dy * dy
            if len_sq < 1e-12:
                cx, cy = ax, ay
            else:
                t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / len_sq))
                cx, cy = ax + t * dx, ay + t * dy
            d = math.hypot(px - cx, py - cy)
            if d < min_dist:
                min_dist = d
                nearest_x, nearest_y = cx, cy
        to_nfz_x = nearest_x - px
        to_nfz_y = nearest_y - py
        to_nfz_len = math.hypot(to_nfz_x, to_nfz_y)
        if to_nfz_len < 0.01:
            directional_time += dt
            continue
        to_nfz_x /= to_nfz_len
        to_nfz_y /= to_nfz_len
        cos_angle = hx * to_nfz_x + hy * to_nfz_y
        if cos_angle > 0.05:
            directional_time += dt
    return directional_time, (directional_time / total_time * 100) if total_time > 0 else 0.0


# ===========================================================================
#  Run one configuration
# ===========================================================================
def run_config(altitude, overlap, pattern_type):
    strip_spacing, footprint_w, footprint_h = compute_strip_spacing(altitude, overlap)
    if pattern_type == "lawnmower":
        wps = generate_lawnmower_wps(altitude, overlap)
    else:
        wps = generate_zian_spiral_wps(altitude, overlap)
    if not wps or len(wps) < 2:
        return None
    sim = simulate_path(
        waypoints_gps=wps,
        altitude_m=altitude,
        sssi_polygon_gps=config.SSSI_GPS,
        config_params={"speed_for_altitude": config.speed_for_altitude},
    )
    s = sim.summary
    coverage = compute_coverage_shapely(wps, footprint_h, config.SEARCH_AREA_GPS)
    p_detect = compute_detection_prob(altitude, s.avg_speed_mps, footprint_w)
    dir_nfz_time, dir_nfz_pct = compute_directional_nfz_time(sim, config.SSSI_GPS)
    return {
        "pattern": pattern_type,
        "altitude_m": altitude,
        "overlap": overlap,
        "strip_spacing_m": round(strip_spacing, 2),
        "footprint_w_m": round(footprint_w, 2),
        "footprint_h_m": round(footprint_h, 2),
        "waypoints": s.num_waypoints,
        "path_length_m": round(s.total_distance_m, 1),
        "mission_time_s": round(s.total_time_s, 1),
        "energy_wh": round(s.total_energy_wh, 2),
        "coverage_pct": round(coverage * 100, 1),
        "detection_prob": round(p_detect, 4),
        "nfz_time_s": round(s.nfz_time_s, 1),
        "nfz_time_pct": round(s.nfz_time_pct, 1),
        "nfz_dir_time_s": round(dir_nfz_time, 1),
        "nfz_dir_time_pct": round(dir_nfz_pct, 1),
        "avg_speed_mps": round(s.avg_speed_mps, 2),
        "max_speed_mps": round(s.max_speed_mps, 2),
        # Store sim and waypoints for map plotting
        "_sim": sim,
        "_wps": wps,
    }


# ===========================================================================
#  Composite score for "best" config
# ===========================================================================
def composite_score(r, all_at_35):
    """Normalize against all configs at 35m, then weighted blend."""
    def norm(val, key, invert=False):
        vals = [x[key] for x in all_at_35 if x is not None]
        mn, mx = min(vals), max(vals)
        if mx - mn < 1e-9:
            return 0.5
        n = (val - mn) / (mx - mn)
        return (1.0 - n) if invert else n

    cov_n = norm(r["coverage_pct"], "coverage_pct")
    time_n = norm(r["mission_time_s"], "mission_time_s", invert=True)
    energy_n = norm(r["energy_wh"], "energy_wh", invert=True)
    nfz_n = norm(r["nfz_dir_time_pct"], "nfz_dir_time_pct", invert=True)
    return 0.30 * cov_n + 0.25 * time_n + 0.25 * energy_n + 0.20 * nfz_n


# ===========================================================================
#  Plotting helpers
# ===========================================================================
def _plot_map(ax, result, title, search_gps, sssi_gps, footprint_h):
    """Plot path with speed heatmap on a map."""
    sim = result["_sim"]
    wps = result["_wps"]

    # Search polygon
    sp_local = [gps_to_local(lat, lon, REF_LAT, REF_LON)
                for lat, lon in search_gps]
    sp_x = [p[0] for p in sp_local] + [sp_local[0][0]]
    sp_y = [p[1] for p in sp_local] + [sp_local[0][1]]
    ax.plot(sp_x, sp_y, "g--", linewidth=1.5, label="Search area")

    # SSSI polygon
    if sssi_gps:
        nfz_local = [gps_to_local(lat, lon, REF_LAT, REF_LON)
                     for lat, lon in sssi_gps]
        nfz_x = [p[0] for p in nfz_local] + [nfz_local[0][0]]
        nfz_y = [p[1] for p in nfz_local] + [nfz_local[0][1]]
        ax.fill(nfz_x, nfz_y, color="red", alpha=0.2)
        ax.plot(nfz_x, nfz_y, "r-", linewidth=1.0, alpha=0.6, label="SSSI NFZ")

    # Camera swath strips (light blue)
    wps_local = [gps_to_local(lat, lon, REF_LAT, REF_LON) for lat, lon in wps]
    half_buf = footprint_h / 2.0
    if HAS_SHAPELY:
        for i in range(len(wps_local) - 1):
            seg = LineString([wps_local[i], wps_local[i + 1]])
            if seg.length > 0.5:
                buf = seg.buffer(half_buf, cap_style=2)
                if hasattr(buf, 'exterior'):
                    bx, by = buf.exterior.xy
                    ax.fill(bx, by, color="cyan", alpha=0.05)

    # Path colored by speed
    pts = sim.points
    if len(pts) > 1:
        speeds = [p.speed_mps for p in pts]
        xs = [p.x_m for p in pts]
        ys = [p.y_m for p in pts]
        vmin, vmax = 0, max(speeds) if max(speeds) > 0 else 1
        norm = Normalize(vmin=vmin, vmax=vmax)
        cmap = plt.cm.RdYlGn
        for i in range(len(pts) - 1):
            color = cmap(norm(speeds[i]))
            ax.plot([xs[i], xs[i+1]], [ys[i], ys[i+1]],
                    color=color, linewidth=1.2, solid_capstyle='round')

        # Colorbar
        sm = ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax, fraction=0.046, pad=0.04, shrink=0.8)
        cbar.set_label("Speed (m/s)", fontsize=8)
        cbar.ax.tick_params(labelsize=7)

    # Numbered waypoints
    for i, (lat, lon) in enumerate(wps):
        x, y = gps_to_local(lat, lon, REF_LAT, REF_LON)
        ax.plot(x, y, "o", color="white", markersize=4, markeredgecolor="black",
                markeredgewidth=0.5, zorder=5)
        if i % max(1, len(wps) // 10) == 0 or i == len(wps) - 1:
            ax.annotate(str(i), (x, y), fontsize=5, ha="center", va="bottom",
                        xytext=(0, 3), textcoords="offset points",
                        color="black", fontweight="bold")

    # Scale bar (50m)
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    bar_x = xlim[0] + (xlim[1] - xlim[0]) * 0.05
    bar_y = ylim[0] + (ylim[1] - ylim[0]) * 0.05
    ax.plot([bar_x, bar_x + 50], [bar_y, bar_y], "k-", linewidth=3)
    ax.text(bar_x + 25, bar_y + 2, "50m", ha="center", fontsize=7, fontweight="bold")

    # North arrow
    arr_x = xlim[1] - (xlim[1] - xlim[0]) * 0.08
    arr_y = ylim[1] - (ylim[1] - ylim[0]) * 0.15
    ax.annotate("N", xy=(arr_x, arr_y + 15), fontsize=9, fontweight="bold",
                ha="center", va="bottom")
    ax.annotate("", xy=(arr_x, arr_y + 14), xytext=(arr_x, arr_y),
                arrowprops=dict(arrowstyle="->", lw=1.5, color="black"))

    ax.set_aspect("equal")
    ax.set_title(title, fontsize=11, fontweight="bold")
    ax.set_xlabel("East (m)", fontsize=8)
    ax.set_ylabel("North (m)", fontsize=8)
    ax.tick_params(labelsize=7)
    ax.grid(True, alpha=0.2)


def _plot_bars(ax, lm_best, sp_best):
    """Grouped bar chart comparing 6 metrics."""
    metrics = [
        ("Time\n(s)", "mission_time_s", True),
        ("Energy\n(Wh)", "energy_wh", True),
        ("Coverage\n(%)", "coverage_pct", False),
        ("Path\n(m)", "path_length_m", True),
        ("NFZ\n(%)", "nfz_dir_time_pct", True),
        ("Waypoints", "waypoints", True),
    ]

    x = np.arange(len(metrics))
    width = 0.35

    lm_vals = [lm_best[m[1]] for m in metrics]
    sp_vals = [sp_best[m[1]] for m in metrics]

    # Normalize for display (relative bars)
    max_vals = [max(abs(lm_vals[i]), abs(sp_vals[i]), 0.001) for i in range(len(metrics))]
    lm_norm = [lm_vals[i] / max_vals[i] for i in range(len(metrics))]
    sp_norm = [sp_vals[i] / max_vals[i] for i in range(len(metrics))]

    bars1 = ax.bar(x - width/2, lm_norm, width, color=COLOR_LM, alpha=0.85,
                   edgecolor="white", linewidth=0.5, label="Lawnmower")
    bars2 = ax.bar(x + width/2, sp_norm, width, color=COLOR_SP, alpha=0.85,
                   edgecolor="white", linewidth=0.5, label="Spiral")

    # Value labels
    for i, (b1, b2) in enumerate(zip(bars1, bars2)):
        lv = lm_vals[i]
        sv = sp_vals[i]
        fmt = ".1f" if isinstance(lv, float) else "d"
        lm_str = f"{lv:{fmt}}"
        sp_str = f"{sv:{fmt}}"
        ax.text(b1.get_x() + b1.get_width()/2, b1.get_height() + 0.02,
                lm_str, ha="center", va="bottom", fontsize=7, fontweight="bold",
                color=COLOR_LM)
        ax.text(b2.get_x() + b2.get_width()/2, b2.get_height() + 0.02,
                sp_str, ha="center", va="bottom", fontsize=7, fontweight="bold",
                color=COLOR_SP)

        # Bold the winner
        lower_better = metrics[i][2]
        if lower_better:
            winner = "lm" if lv < sv else "sp"
        else:
            winner = "lm" if lv > sv else "sp"

    ax.set_xticks(x)
    ax.set_xticklabels([m[0] for m in metrics], fontsize=8)
    ax.set_ylabel("Relative Value", fontsize=8)
    ax.set_title("Metric Comparison (Best Configs)", fontsize=10, fontweight="bold")
    ax.legend(fontsize=8)
    ax.set_ylim(0, 1.35)
    ax.tick_params(labelsize=7)
    ax.grid(True, alpha=0.15, axis="y")


def _plot_radar(ax, lm_best, sp_best):
    """5-axis radar chart with actual values as labels."""
    categories = ["Coverage", "Speed\n(1/time)", "Efficiency\n(1/energy)",
                  "Safety\n(1-NFZ%)", "Detection"]

    def get_vals(r):
        cov = r["coverage_pct"] / 100.0
        inv_time = 300.0 / max(r["mission_time_s"], 1.0)
        inv_energy = 20.0 / max(r["energy_wh"], 0.1)
        safety = 1.0 - r["nfz_dir_time_pct"] / 100.0
        det = r["detection_prob"]
        return [min(cov, 1.0), min(inv_time, 1.0), min(inv_energy, 1.0),
                min(safety, 1.0), min(det, 1.0)]

    def get_labels(r):
        return [
            f"{r['coverage_pct']:.1f}%",
            f"{r['mission_time_s']:.0f}s",
            f"{r['energy_wh']:.1f}Wh",
            f"{100-r['nfz_dir_time_pct']:.1f}%",
            f"{r['detection_prob']:.3f}",
        ]

    N = len(categories)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    angles += angles[:1]

    lm_vals = get_vals(lm_best)
    sp_vals = get_vals(sp_best)
    lm_vals += lm_vals[:1]
    sp_vals += sp_vals[:1]

    lm_labels = get_labels(lm_best)
    sp_labels = get_labels(sp_best)

    ax.plot(angles, lm_vals, "o-", linewidth=2, color=COLOR_LM, label="Lawnmower",
            markersize=5)
    ax.fill(angles, lm_vals, alpha=0.15, color=COLOR_LM)
    ax.plot(angles, sp_vals, "s-", linewidth=2, color=COLOR_SP, label="Spiral",
            markersize=5)
    ax.fill(angles, sp_vals, alpha=0.15, color=COLOR_SP)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=8)
    ax.set_ylim(0, 1.1)
    ax.set_title("Performance Radar", fontsize=10, fontweight="bold", pad=15)
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1), fontsize=8)

    # Add value labels
    for i in range(N):
        angle = angles[i]
        r_lm = lm_vals[i] + 0.08
        r_sp = sp_vals[i] + 0.08
        ax.text(angle, r_lm, lm_labels[i], ha="center", va="center",
                fontsize=6, color=COLOR_LM, fontweight="bold")
        ax.text(angle, max(r_sp - 0.12, 0.05), sp_labels[i], ha="center", va="center",
                fontsize=6, color=COLOR_SP, fontweight="bold")


def _plot_sensitivity(ax, lm_results, sp_results):
    """Overlap sensitivity: coverage and mission time vs overlap."""
    # Top: coverage vs overlap
    lm_overlaps = [r["overlap"] * 100 for r in lm_results if r]
    lm_covs = [r["coverage_pct"] for r in lm_results if r]
    sp_overlaps = [r["overlap"] * 100 for r in sp_results if r]
    sp_covs = [r["coverage_pct"] for r in sp_results if r]

    lm_times = [r["mission_time_s"] for r in lm_results if r]
    sp_times = [r["mission_time_s"] for r in sp_results if r]

    ax.plot(lm_overlaps, lm_covs, "o-", color=COLOR_LM, linewidth=2,
            markersize=5, label="Lawnmower Cov.")
    ax.plot(sp_overlaps, sp_covs, "s-", color=COLOR_SP, linewidth=2,
            markersize=5, label="Spiral Cov.")
    ax.set_xlabel("Overlap (%)", fontsize=8)
    ax.set_ylabel("Coverage (%)", fontsize=8, color="black")
    ax.tick_params(labelsize=7)
    ax.grid(True, alpha=0.2)
    ax.set_title("Overlap Sensitivity", fontsize=10, fontweight="bold")

    # Second y-axis for time
    ax2 = ax.twinx()
    ax2.plot(lm_overlaps, lm_times, "^--", color=COLOR_LM, linewidth=1.5,
             markersize=4, alpha=0.6, label="LM Time")
    ax2.plot(sp_overlaps, sp_times, "v--", color=COLOR_SP, linewidth=1.5,
             markersize=4, alpha=0.6, label="Spiral Time")
    ax2.set_ylabel("Mission Time (s)", fontsize=8, color="gray")
    ax2.tick_params(labelsize=7, colors="gray")

    # Combined legend
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, fontsize=7, loc="lower right")


def _plot_summary_table(ax, lm_best, sp_best):
    """Render the comparison table."""
    ax.axis("off")

    def delta_str(lm_val, sp_val, lower_better=True, is_pct=False):
        if lm_val == sp_val or (lm_val == 0 and sp_val == 0):
            return "same"
        ref = lm_val if lm_val != 0 else 1
        pct = (sp_val - lm_val) / abs(ref) * 100
        if lower_better:
            if sp_val < lm_val:
                return f"{abs(pct):.0f}% less (S)"
            else:
                return f"{abs(pct):.0f}% more (L)"
        else:
            if sp_val > lm_val:
                return f"{abs(pct):.0f}% higher (S)"
            else:
                return f"{abs(pct):.0f}% higher (L)"

    footprint_str = f"{lm_best['footprint_w_m']:.1f} x {lm_best['footprint_h_m']:.1f}m"

    rows = [
        ("Altitude", f"{lm_best['altitude_m']:.0f}m", f"{sp_best['altitude_m']:.0f}m", "-"),
        ("Overlap", f"{lm_best['overlap']*100:.0f}%", f"{sp_best['overlap']*100:.0f}%", "-"),
        ("Strip spacing", f"{lm_best['strip_spacing_m']:.1f}m", f"{sp_best['strip_spacing_m']:.1f}m", "-"),
        ("Footprint", footprint_str, footprint_str, "same"),
        ("Waypoints", f"{lm_best['waypoints']}", f"{sp_best['waypoints']}",
         delta_str(lm_best['waypoints'], sp_best['waypoints'], True)),
        ("Path length", f"{lm_best['path_length_m']:.0f}m", f"{sp_best['path_length_m']:.0f}m",
         delta_str(lm_best['path_length_m'], sp_best['path_length_m'], True)),
        ("Mission time", f"{lm_best['mission_time_s']:.0f}s ({lm_best['mission_time_s']/60:.1f}min)",
         f"{sp_best['mission_time_s']:.0f}s ({sp_best['mission_time_s']/60:.1f}min)",
         delta_str(lm_best['mission_time_s'], sp_best['mission_time_s'], True)),
        ("Energy", f"{lm_best['energy_wh']:.1f} Wh", f"{sp_best['energy_wh']:.1f} Wh",
         delta_str(lm_best['energy_wh'], sp_best['energy_wh'], True)),
        ("Coverage", f"{lm_best['coverage_pct']:.1f}%", f"{sp_best['coverage_pct']:.1f}%",
         delta_str(lm_best['coverage_pct'], sp_best['coverage_pct'], False)),
        ("Detection prob", f"{lm_best['detection_prob']:.4f}", f"{sp_best['detection_prob']:.4f}", "-"),
        ("NFZ exposure", f"{lm_best['nfz_dir_time_pct']:.1f}%", f"{sp_best['nfz_dir_time_pct']:.1f}%",
         delta_str(lm_best['nfz_dir_time_pct'], sp_best['nfz_dir_time_pct'], True)),
        ("Avg speed", f"{lm_best['avg_speed_mps']:.2f} m/s", f"{sp_best['avg_speed_mps']:.2f} m/s", "-"),
    ]

    col_labels = ["Metric", "LAWNMOWER", "ZIAN SPIRAL", "DELTA"]
    cell_text = [[r[0], r[1], r[2], r[3]] for r in rows]

    table = ax.table(cellText=cell_text, colLabels=col_labels,
                     loc="center", cellLoc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1.0, 1.3)

    # Style header
    for j in range(4):
        table[0, j].set_facecolor("#37474F")
        table[0, j].set_text_props(color="white", fontweight="bold")

    # Highlight winners
    higher_better_keys = {"Coverage", "Detection prob"}
    lower_better_keys = {"Waypoints", "Path length", "Mission time", "Energy", "NFZ exposure"}

    for i, row in enumerate(rows):
        metric_name = row[0]
        bg = "#E3F2FD" if i % 2 == 0 else "white"
        for j in range(4):
            table[i + 1, j].set_facecolor(bg)

        # Bold the winner
        if metric_name in higher_better_keys:
            lm_val = lm_best.get(next((m[1] for m in [
                ("Coverage", "coverage_pct"), ("Detection prob", "detection_prob")
            ] if m[0] == metric_name), ""), 0)
            sp_val = sp_best.get(next((m[1] for m in [
                ("Coverage", "coverage_pct"), ("Detection prob", "detection_prob")
            ] if m[0] == metric_name), ""), 0)
            if lm_val > sp_val:
                table[i + 1, 1].set_text_props(fontweight="bold", color=COLOR_LM)
            elif sp_val > lm_val:
                table[i + 1, 2].set_text_props(fontweight="bold", color=COLOR_SP)
        elif metric_name in lower_better_keys:
            key_map = {"Waypoints": "waypoints", "Path length": "path_length_m",
                       "Mission time": "mission_time_s", "Energy": "energy_wh",
                       "NFZ exposure": "nfz_dir_time_pct"}
            key = key_map.get(metric_name, "")
            if key:
                lm_val = lm_best.get(key, 0)
                sp_val = sp_best.get(key, 0)
                if lm_val < sp_val:
                    table[i + 1, 1].set_text_props(fontweight="bold", color=COLOR_LM)
                elif sp_val < lm_val:
                    table[i + 1, 2].set_text_props(fontweight="bold", color=COLOR_SP)


# ===========================================================================
#  Main
# ===========================================================================
def main():
    print("=" * 66)
    print("  LAWNMOWER vs ZIAN SPIRAL @ 35m — OVERLAP SWEEP")
    print("=" * 66)

    lm_results = []
    sp_results = []
    all_results = []

    total = len(OVERLAPS) * 2
    done = 0

    for overlap in OVERLAPS:
        # Lawnmower
        done += 1
        print(f"\n[{done}/{total}] Lawnmower @ {ALTITUDE}m, {int(overlap*100)}% overlap")
        try:
            lm = run_config(ALTITUDE, overlap, "lawnmower")
        except Exception as e:
            print(f"  ERROR: {e}")
            lm = None

        # Spiral
        done += 1
        print(f"[{done}/{total}] Spiral    @ {ALTITUDE}m, {int(overlap*100)}% overlap")
        try:
            sp = run_config(ALTITUDE, overlap, "spiral")
        except Exception as e:
            print(f"  ERROR: {e}")
            sp = None

        lm_results.append(lm)
        sp_results.append(sp)
        if lm:
            all_results.append(lm)
        if sp:
            all_results.append(sp)

        # Print comparison
        if lm and sp:
            print(f"  LM: cov={lm['coverage_pct']:.1f}% time={lm['mission_time_s']:.0f}s "
                  f"energy={lm['energy_wh']:.1f}Wh nfz={lm['nfz_dir_time_pct']:.1f}%")
            print(f"  SP: cov={sp['coverage_pct']:.1f}% time={sp['mission_time_s']:.0f}s "
                  f"energy={sp['energy_wh']:.1f}Wh nfz={sp['nfz_dir_time_pct']:.1f}%")

    # Filter valid results
    valid_all = [r for r in all_results if r is not None]
    valid_lm = [r for r in lm_results if r is not None]
    valid_sp = [r for r in sp_results if r is not None]

    if not valid_lm or not valid_sp:
        print("\n  ERROR: Not enough valid results to compare.")
        return

    # Find best configs
    lm_best = max(valid_lm, key=lambda r: composite_score(r, valid_all))
    sp_best = max(valid_sp, key=lambda r: composite_score(r, valid_all))

    print("\n" + "=" * 66)
    print("  BEST CONFIGS")
    print("=" * 66)
    print(f"\n  Lawnmower: {int(lm_best['overlap']*100)}% overlap "
          f"(score={composite_score(lm_best, valid_all):.3f})")
    print(f"    Coverage={lm_best['coverage_pct']:.1f}%, "
          f"Time={lm_best['mission_time_s']:.0f}s, "
          f"Energy={lm_best['energy_wh']:.1f}Wh")
    print(f"\n  Spiral:    {int(sp_best['overlap']*100)}% overlap "
          f"(score={composite_score(sp_best, valid_all):.3f})")
    print(f"    Coverage={sp_best['coverage_pct']:.1f}%, "
          f"Time={sp_best['mission_time_s']:.0f}s, "
          f"Energy={sp_best['energy_wh']:.1f}Wh")

    # ── Print full comparison table ──
    print("\n" + "-" * 66)
    print(f"  {'':22s} {'LAWNMOWER':>14s}  {'ZIAN SPIRAL':>14s}  {'DELTA':>16s}")
    print("-" * 66)
    table_rows = [
        ("Altitude:", f"{lm_best['altitude_m']:.0f}m", f"{sp_best['altitude_m']:.0f}m", "-"),
        ("Overlap:", f"{int(lm_best['overlap']*100)}%", f"{int(sp_best['overlap']*100)}%", "-"),
        ("Strip spacing:", f"{lm_best['strip_spacing_m']:.1f}m", f"{sp_best['strip_spacing_m']:.1f}m", "-"),
        ("Footprint:", f"{lm_best['footprint_w_m']:.1f}x{lm_best['footprint_h_m']:.1f}m",
         f"{sp_best['footprint_w_m']:.1f}x{sp_best['footprint_h_m']:.1f}m", "same"),
        ("Waypoints:", f"{lm_best['waypoints']}", f"{sp_best['waypoints']}",
         f"{abs(sp_best['waypoints']-lm_best['waypoints'])} diff"),
        ("Path length:", f"{lm_best['path_length_m']:.0f}m", f"{sp_best['path_length_m']:.0f}m",
         f"{abs(sp_best['path_length_m']-lm_best['path_length_m']):.0f}m diff"),
        ("Mission time:", f"{lm_best['mission_time_s']:.0f}s ({lm_best['mission_time_s']/60:.1f}min)",
         f"{sp_best['mission_time_s']:.0f}s ({sp_best['mission_time_s']/60:.1f}min)", ""),
        ("Energy:", f"{lm_best['energy_wh']:.1f} Wh", f"{sp_best['energy_wh']:.1f} Wh", ""),
        ("Coverage:", f"{lm_best['coverage_pct']:.1f}%", f"{sp_best['coverage_pct']:.1f}%", ""),
        ("Detection prob:", f"{lm_best['detection_prob']:.4f}", f"{sp_best['detection_prob']:.4f}", "-"),
        ("NFZ exposure:", f"{lm_best['nfz_dir_time_pct']:.1f}%", f"{sp_best['nfz_dir_time_pct']:.1f}%", ""),
        ("Avg speed:", f"{lm_best['avg_speed_mps']:.2f} m/s", f"{sp_best['avg_speed_mps']:.2f} m/s", "-"),
    ]
    for label, lv, sv, delta in table_rows:
        print(f"  {label:22s} {lv:>14s}  {sv:>14s}  {delta:>16s}")
    print("-" * 66)

    # ── Generate figure ──
    print("\n  Generating publication figure...")

    fig = plt.figure(figsize=(18, 20), dpi=150)
    fig.patch.set_facecolor("white")

    # Main title
    fig.suptitle("Search Pattern Comparison at 35m Altitude",
                 fontsize=18, fontweight="bold", y=0.98)
    fig.text(0.5, 0.965,
             "Fenswood Farm Survey Area  --  IMX296 Camera (1456x1088)",
             ha="center", fontsize=12, color="gray", style="italic")

    # GridSpec layout: 3 rows
    gs = fig.add_gridspec(3, 3, height_ratios=[1.1, 0.8, 0.7],
                          hspace=0.35, wspace=0.35,
                          top=0.94, bottom=0.02, left=0.05, right=0.95)

    # Row 1: Two map plots
    ax_map_lm = fig.add_subplot(gs[0, 0:2])  # wider for lawnmower
    ax_map_sp = fig.add_subplot(gs[0, 2])     # spiral

    # Actually make them equal width
    ax_map_lm = fig.add_subplot(gs[0, 0])
    ax_map_sp = fig.add_subplot(gs[0, 1])

    # Make both maps share same axis limits
    _plot_map(ax_map_lm, lm_best,
              f"Lawnmower (best: {int(lm_best['overlap']*100)}% overlap)",
              config.SEARCH_AREA_GPS, config.SSSI_GPS, lm_best["footprint_h_m"])
    _plot_map(ax_map_sp, sp_best,
              f"Zian Spiral (best: {int(sp_best['overlap']*100)}% overlap)",
              config.SEARCH_AREA_GPS, config.SSSI_GPS, sp_best["footprint_h_m"])

    # Sync axis limits
    all_pts_lm = [(p.x_m, p.y_m) for p in lm_best["_sim"].points]
    all_pts_sp = [(p.x_m, p.y_m) for p in sp_best["_sim"].points]
    all_pts = all_pts_lm + all_pts_sp
    if all_pts:
        all_x = [p[0] for p in all_pts]
        all_y = [p[1] for p in all_pts]
        margin = 30
        xmin, xmax = min(all_x) - margin, max(all_x) + margin
        ymin, ymax = min(all_y) - margin, max(all_y) + margin
        ax_map_lm.set_xlim(xmin, xmax)
        ax_map_lm.set_ylim(ymin, ymax)
        ax_map_sp.set_xlim(xmin, xmax)
        ax_map_sp.set_ylim(ymin, ymax)

    # Third subplot in row 1: legend/info
    ax_info = fig.add_subplot(gs[0, 2])
    ax_info.axis("off")
    info_text = (
        f"Camera: IMX296\n"
        f"Resolution: {config.IMAGE_W}x{config.IMAGE_H}\n"
        f"Sensor: {config.SENSOR_WIDTH_MM}mm\n"
        f"Focal: {config.FOCAL_LENGTH_MM}mm\n\n"
        f"Altitude: {ALTITUDE:.0f}m\n"
        f"Footprint: {lm_best['footprint_w_m']:.1f}x{lm_best['footprint_h_m']:.1f}m\n\n"
        f"Base speed: {config.speed_for_altitude(ALTITUDE):.1f} m/s\n"
        f"NFZ buffer: 40m outer, 2m inner\n\n"
        f"Overlaps tested:\n"
        f"  {', '.join(f'{int(o*100)}%' for o in OVERLAPS)}\n\n"
        f"Scoring weights:\n"
        f"  Coverage:  30%\n"
        f"  Time:      25%\n"
        f"  Energy:    25%\n"
        f"  Safety:    20%"
    )
    ax_info.text(0.05, 0.95, info_text, transform=ax_info.transAxes,
                 fontsize=9, verticalalignment="top", fontfamily="monospace",
                 bbox=dict(boxstyle="round,pad=0.5", facecolor="#F5F5F5",
                           edgecolor="#BDBDBD", alpha=0.9))

    # Row 2: Three comparison charts
    ax_bars = fig.add_subplot(gs[1, 0])
    ax_radar = fig.add_subplot(gs[1, 1], polar=True)
    ax_sens = fig.add_subplot(gs[1, 2])

    _plot_bars(ax_bars, lm_best, sp_best)
    _plot_radar(ax_radar, lm_best, sp_best)
    _plot_sensitivity(ax_sens, valid_lm, valid_sp)

    # Row 3: Summary table
    ax_table = fig.add_subplot(gs[2, :])
    _plot_summary_table(ax_table, lm_best, sp_best)

    # Save
    out_path = os.path.join(OUTPUT_DIR, "compare_35m.png")
    fig.savefig(out_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  Figure saved: {out_path}")

    # Clean up internal keys before any JSON serialization
    for r in all_results:
        if r:
            r.pop("_sim", None)
            r.pop("_wps", None)

    print("\n" + "=" * 66)
    print("  DONE")
    print("=" * 66)


if __name__ == "__main__":
    main()
