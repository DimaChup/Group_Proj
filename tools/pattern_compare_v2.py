#!/usr/bin/env python3
"""
Lawnmower vs Zian Spiral — Fair Pattern Comparison (v2)
=======================================================

Generates both patterns at multiple altitude/overlap configs, simulates
realistic drone physics via path_physics.simulate_path(), computes Shapely-
based coverage, detection probability, and directional NFZ time.

Usage:
    cd v3/
    python tools/pattern_compare_v2.py

Outputs:
    tools/pattern_analysis/compare_v2.json
    tools/pattern_analysis/pareto_overlay.png
    tools/pattern_analysis/radar_chart.png
    tools/pattern_analysis/coverage_vs_time.png
    tools/pattern_analysis/summary_table.png
"""

import sys
import os
import math
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
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

# Zian's planner lives in a subdirectory with its own imports
ZIAN_DIR = os.path.join(PROJECT_ROOT, "Zian", "path_planner")
sys.path.insert(0, ZIAN_DIR)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pattern_analysis")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Shapely (for coverage)
# ---------------------------------------------------------------------------
try:
    from shapely.geometry import Polygon as ShapelyPolygon, LineString, MultiPolygon
    from shapely.ops import unary_union
    HAS_SHAPELY = True
except ImportError:
    HAS_SHAPELY = False
    print("[WARN] Shapely not installed. Coverage will be estimated, not exact.")


# ===========================================================================
#  Constants
# ===========================================================================
CANVAS_SIZE = 4800
ALTITUDES = [20, 25, 30, 35, 40, 50]
OVERLAPS = [0.0, 0.10, 0.20, 0.30]

# Detection model constants
TARGET_REAL_RADIUS_M = config.TARGET_REAL_RADIUS_M
FOCAL_LENGTH_PX = config.FOCAL_LENGTH_MM * config.IMAGE_W / config.SENSOR_WIDTH_MM
PI_FPS = 4.8  # from Pi benchmark


# ===========================================================================
#  Coordinate helpers
# ===========================================================================
def _ref_point():
    """Centroid of search area as reference."""
    lats = [p[0] for p in config.SEARCH_AREA_GPS]
    lons = [p[1] for p in config.SEARCH_AREA_GPS]
    return sum(lats) / len(lats), sum(lons) / len(lons)


REF_LAT, REF_LON = _ref_point()


def search_poly_local():
    """Search area polygon in local metres (x_east, y_north)."""
    return [gps_to_local(lat, lon, REF_LAT, REF_LON)
            for lat, lon in config.SEARCH_AREA_GPS]


# ===========================================================================
#  Strip spacing helper
# ===========================================================================
def compute_strip_spacing(altitude, overlap):
    """Compute strip spacing using footprint HEIGHT (not width)."""
    footprint_w, footprint_h = camera_footprint(altitude)
    strip_spacing = footprint_h * (1.0 - overlap)
    return strip_spacing, footprint_w, footprint_h


# ===========================================================================
#  Lawnmower generation (via PathPlanner)
# ===========================================================================
def generate_lawnmower_wps(altitude, overlap):
    """Generate lawnmower waypoints using PathPlanner with _no_turn=True.

    Returns list of (lat, lon) tuples.
    """
    geo = GeoTransformer(CANVAS_SIZE)
    search_px = [geo.gps_to_pixels(lat, lon) for lat, lon in config.SEARCH_AREA_GPS]
    planner = PathPlanner(geo, search_px)
    planner._no_turn = True

    # PathPlanner uses config values internally, but we need to override altitude
    wps = planner.generate_search_pattern(
        CANVAS_SIZE, CANVAS_SIZE,
        drone_gps=config.TAKEOFF_GPS,
        alt_override=altitude,
    )
    return wps


# ===========================================================================
#  Zian spiral generation (via perimeter_planner.plan())
# ===========================================================================
def generate_zian_spiral_wps(altitude, overlap):
    """Generate Zian's perimeter spiral, patching HALF_SWATH/SWATH to match
    the lawnmower's strip spacing.

    Returns list of (lat, lon) tuples (skipping the 'enter' waypoint).
    """
    strip_spacing, _, _ = compute_strip_spacing(altitude, overlap)

    # Patch Zian's module globals before calling plan()
    import perimeter_planner as zpp
    zpp.HALF_SWATH = strip_spacing / 2.0
    zpp.SWATH = strip_spacing

    waypoints_dicts = zpp.plan()

    # Skip the "enter" waypoint — it's a transit point, not part of search
    wps = []
    for wp in waypoints_dicts:
        if wp["name"] == "enter":
            continue
        wps.append((wp["lat"], wp["lon"]))

    return wps


# ===========================================================================
#  Coverage calculation (Shapely)
# ===========================================================================
def compute_coverage_shapely(waypoints_gps, footprint_h, search_polygon_gps):
    """Compute area coverage by buffering path segments by footprint_h/2.

    Returns coverage ratio (0..1).
    """
    if not HAS_SHAPELY or len(waypoints_gps) < 2:
        return 0.0

    # Convert everything to local metres
    search_local = [gps_to_local(lat, lon, REF_LAT, REF_LON)
                    for lat, lon in search_polygon_gps]
    search_poly = ShapelyPolygon(search_local)
    if not search_poly.is_valid:
        search_poly = search_poly.buffer(0)

    wps_local = [gps_to_local(lat, lon, REF_LAT, REF_LON)
                 for lat, lon in waypoints_gps]

    # Buffer each segment by footprint_h / 2
    half_buf = footprint_h / 2.0
    buffers = []
    for i in range(len(wps_local) - 1):
        seg = LineString([wps_local[i], wps_local[i + 1]])
        if seg.length > 0.01:
            buffers.append(seg.buffer(half_buf, cap_style=2))  # flat caps

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
    """Sigmoid function for single-frame detection probability."""
    return 1.0 / (1.0 + math.exp(-steepness * (x - midpoint)))


def compute_detection_prob(altitude, avg_speed, footprint_w):
    """Compute probability of detecting the target during a single pass."""
    # Pixel size of the target
    pixel_size = (TARGET_REAL_RADIUS_M * 2 * FOCAL_LENGTH_PX) / altitude
    p_single = sigmoid(pixel_size)

    # Motion blur penalty
    blur = 1.0 / (1.0 + 0.008 * avg_speed ** 2)

    # Number of effective frames while target is in view
    if avg_speed < 0.01:
        effective_frames = PI_FPS * 10  # cap at 10 seconds of hovering
    else:
        time_in_view = footprint_w / avg_speed
        effective_frames = time_in_view * PI_FPS * blur

    p_detect = 1.0 - (1.0 - p_single) ** max(effective_frames, 1)
    return p_detect


# ===========================================================================
#  Directional NFZ time
# ===========================================================================
def compute_directional_nfz_time(sim_result, sssi_polygon_gps):
    """Recompute NFZ time counting only time where drone is flying TOWARD NFZ.

    Uses cos_angle between heading and toward-NFZ vector.
    If cos_angle <= 0.05 (flying parallel/away), that time doesn't count.
    """
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

        if pt.dist_to_nfz_m > 40.0:  # outside buffer, skip
            continue

        # Heading vector (from heading_deg, 0=north CW)
        heading_rad = math.radians(pt.heading_deg)
        hx = math.sin(heading_rad)  # east component
        hy = math.cos(heading_rad)  # north component

        # Vector toward nearest NFZ point
        px, py = pt.x_m, pt.y_m
        min_dist = float("inf")
        nearest_x, nearest_y = 0, 0
        n = len(nfz_local)
        for j in range(n):
            ax, ay = nfz_local[j]
            bx, by = nfz_local[(j + 1) % n]
            # Project onto segment
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

        # Direction toward NFZ
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
    """Run a single pattern config and return metrics dict."""
    strip_spacing, footprint_w, footprint_h = compute_strip_spacing(altitude, overlap)

    # Generate waypoints
    if pattern_type == "lawnmower":
        wps = generate_lawnmower_wps(altitude, overlap)
    else:
        wps = generate_zian_spiral_wps(altitude, overlap)

    if not wps or len(wps) < 2:
        return None

    # Simulate physics
    sim = simulate_path(
        waypoints_gps=wps,
        altitude_m=altitude,
        sssi_polygon_gps=config.SSSI_GPS,
        config_params={"speed_for_altitude": config.speed_for_altitude},
    )

    s = sim.summary

    # Coverage
    coverage = compute_coverage_shapely(wps, footprint_h, config.SEARCH_AREA_GPS)

    # Detection probability
    p_detect = compute_detection_prob(altitude, s.avg_speed_mps, footprint_w)

    # Directional NFZ time
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
    }


# ===========================================================================
#  Console table
# ===========================================================================
def print_comparison(lm_result, sp_result, altitude, overlap):
    """Print side-by-side comparison table."""
    if lm_result is None or sp_result is None:
        return

    metrics = [
        ("Waypoints",       "waypoints",       "{:>10d}"),
        ("Path length (m)", "path_length_m",    "{:>10,.1f}"),
        ("Mission time (s)","mission_time_s",   "{:>10,.1f}"),
        ("Energy (Wh)",     "energy_wh",        "{:>10.2f}"),
        ("Coverage (%)",    "coverage_pct",     "{:>10.1f}"),
        ("Detection prob",  "detection_prob",   "{:>10.4f}"),
        ("NFZ time (s)",    "nfz_time_s",       "{:>10.1f}"),
        ("NFZ time (%)",    "nfz_time_pct",     "{:>10.1f}"),
        ("NFZ dir time (s)","nfz_dir_time_s",   "{:>10.1f}"),
        ("NFZ dir time (%)", "nfz_dir_time_pct","{:>10.1f}"),
        ("Avg speed (m/s)", "avg_speed_mps",    "{:>10.2f}"),
    ]

    # Determine winner for each metric
    # Higher is better: coverage, detection_prob, avg_speed, waypoints (fewer is better)
    # Lower is better: path_length, mission_time, energy, nfz_time
    higher_better = {"coverage_pct", "detection_prob"}
    lower_better = {"path_length_m", "mission_time_s", "energy_wh",
                    "nfz_time_s", "nfz_time_pct", "nfz_dir_time_s", "nfz_dir_time_pct"}
    # waypoints and avg_speed are informational

    lm_wins = 0
    sp_wins = 0
    scorable = higher_better | lower_better

    print(f"\n  Config: {altitude}m altitude, {int(overlap*100)}% overlap")
    print(f"  +{'':->20}+{'':->12}+{'':->12}+")
    print(f"  | {'Metric':<18} | {'Lawnmower':>10} | {'Spiral':>10} |")
    print(f"  +{'':->20}+{'':->12}+{'':->12}+")

    for label, key, fmt in metrics:
        lv = lm_result[key]
        sv = sp_result[key]
        lm_str = fmt.format(lv)
        sp_str = fmt.format(sv)

        if key in scorable:
            if key in higher_better:
                if lv > sv:
                    lm_wins += 1
                elif sv > lv:
                    sp_wins += 1
            else:
                if lv < sv:
                    lm_wins += 1
                elif sv < lv:
                    sp_wins += 1

        print(f"  | {label:<18} | {lm_str} | {sp_str} |")

    print(f"  +{'':->20}+{'':->12}+{'':->12}+")
    total = lm_wins + sp_wins
    if lm_wins > sp_wins:
        print(f"  Winner: Lawnmower ({lm_wins}/{total} metrics)")
    elif sp_wins > lm_wins:
        print(f"  Winner: Spiral ({sp_wins}/{total} metrics)")
    else:
        print(f"  Tie ({lm_wins}/{total} each)")


# ===========================================================================
#  Plots
# ===========================================================================
def plot_pareto(results, out_dir):
    """Pareto frontier: x=mission_time, y=energy, color=coverage."""
    fig, ax = plt.subplots(figsize=(10, 7))

    for pattern, marker, color_base in [("lawnmower", "o", "Blues"),
                                         ("spiral", "s", "Oranges")]:
        subset = [r for r in results if r["pattern"] == pattern]
        if not subset:
            continue
        times = [r["mission_time_s"] for r in subset]
        energies = [r["energy_wh"] for r in subset]
        coverages = [r["coverage_pct"] for r in subset]

        sc = ax.scatter(times, energies, c=coverages, cmap=color_base,
                        marker=marker, s=80, edgecolors="k", linewidths=0.5,
                        vmin=50, vmax=100, label=pattern.capitalize(), alpha=0.8)

        # Draw Pareto frontier
        indexed = sorted(zip(times, energies), key=lambda x: x[0])
        frontier = []
        min_e = float("inf")
        for t, e in indexed:
            if e < min_e:
                frontier.append((t, e))
                min_e = e
        if len(frontier) > 1:
            fx, fy = zip(*frontier)
            ax.plot(fx, fy, linestyle="--", linewidth=1.5,
                    color="navy" if pattern == "lawnmower" else "darkorange",
                    alpha=0.7)

    cbar = fig.colorbar(sc, ax=ax)
    cbar.set_label("Coverage (%)")
    ax.set_xlabel("Mission Time (s)")
    ax.set_ylabel("Energy (Wh)")
    ax.set_title("Pareto Frontier: Mission Time vs Energy (color=Coverage)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "pareto_overlay.png"), dpi=150)
    plt.close(fig)


def plot_radar(lm_best, sp_best, out_dir):
    """5-axis spider chart comparing best config of each pattern."""
    if lm_best is None or sp_best is None:
        return

    categories = ["Coverage", "Detection", "1/Time", "1/Energy", "Safety"]
    N = len(categories)

    def normalize(results):
        cov = results["coverage_pct"] / 100.0
        det = results["detection_prob"]
        # Invert time and energy (lower is better -> higher normalized value)
        inv_time = 1.0 / max(results["mission_time_s"], 1.0) * 300  # scale
        inv_energy = 1.0 / max(results["energy_wh"], 0.1) * 20  # scale
        safety = 1.0 - results["nfz_dir_time_pct"] / 100.0
        vals = [cov, det, min(inv_time, 1.0), min(inv_energy, 1.0), safety]
        return vals

    lm_vals = normalize(lm_best)
    sp_vals = normalize(sp_best)

    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    angles += angles[:1]
    lm_vals += lm_vals[:1]
    sp_vals += sp_vals[:1]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    ax.plot(angles, lm_vals, "o-", linewidth=2, color="steelblue", label="Lawnmower")
    ax.fill(angles, lm_vals, alpha=0.15, color="steelblue")
    ax.plot(angles, sp_vals, "s-", linewidth=2, color="darkorange", label="Spiral")
    ax.fill(angles, sp_vals, alpha=0.15, color="darkorange")

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories)
    ax.set_ylim(0, 1.05)
    ax.set_title("Best Config Comparison (Radar)", pad=20)
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1))
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "radar_chart.png"), dpi=150)
    plt.close(fig)


def plot_coverage_vs_time(results, out_dir):
    """Coverage % vs mission time for both patterns."""
    fig, ax = plt.subplots(figsize=(10, 6))

    for pattern, marker, color in [("lawnmower", "o", "steelblue"),
                                    ("spiral", "s", "darkorange")]:
        subset = [r for r in results if r["pattern"] == pattern]
        if not subset:
            continue
        times = [r["mission_time_s"] for r in subset]
        covs = [r["coverage_pct"] for r in subset]
        alts = [r["altitude_m"] for r in subset]

        ax.scatter(times, covs, c=color, marker=marker, s=60,
                   edgecolors="k", linewidths=0.5, alpha=0.7,
                   label=pattern.capitalize())

        # Annotate a few points with altitude
        for t, c, a in zip(times, covs, alts):
            if a in [20, 35, 50]:
                ax.annotate(f"{a}m", (t, c), fontsize=7, alpha=0.6,
                            xytext=(5, 5), textcoords="offset points")

    ax.set_xlabel("Mission Time (s)")
    ax.set_ylabel("Coverage (%)")
    ax.set_title("Coverage vs Mission Time")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "coverage_vs_time.png"), dpi=150)
    plt.close(fig)


def plot_summary_table(lm_best, sp_best, out_dir):
    """Render a comparison table as an image."""
    if lm_best is None or sp_best is None:
        return

    rows = [
        ("Altitude (m)",     f"{lm_best['altitude_m']}",     f"{sp_best['altitude_m']}"),
        ("Overlap",          f"{int(lm_best['overlap']*100)}%", f"{int(sp_best['overlap']*100)}%"),
        ("Waypoints",        f"{lm_best['waypoints']}",      f"{sp_best['waypoints']}"),
        ("Path length (m)",  f"{lm_best['path_length_m']:.0f}", f"{sp_best['path_length_m']:.0f}"),
        ("Mission time (s)", f"{lm_best['mission_time_s']:.0f}", f"{sp_best['mission_time_s']:.0f}"),
        ("Energy (Wh)",      f"{lm_best['energy_wh']:.1f}",  f"{sp_best['energy_wh']:.1f}"),
        ("Coverage (%)",     f"{lm_best['coverage_pct']:.1f}", f"{sp_best['coverage_pct']:.1f}"),
        ("Detection prob",   f"{lm_best['detection_prob']:.3f}", f"{sp_best['detection_prob']:.3f}"),
        ("NFZ dir time (s)", f"{lm_best['nfz_dir_time_s']:.0f}", f"{sp_best['nfz_dir_time_s']:.0f}"),
        ("Avg speed (m/s)",  f"{lm_best['avg_speed_mps']:.1f}", f"{sp_best['avg_speed_mps']:.1f}"),
    ]

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.axis("off")
    ax.set_title("Best Configuration Comparison", fontsize=14, fontweight="bold", pad=15)

    col_labels = ["Metric", "Lawnmower", "Spiral"]
    cell_text = [[r[0], r[1], r[2]] for r in rows]

    table = ax.table(cellText=cell_text, colLabels=col_labels,
                     loc="center", cellLoc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.0, 1.4)

    # Style header
    for j in range(3):
        table[0, j].set_facecolor("#4472C4")
        table[0, j].set_text_props(color="white", fontweight="bold")

    # Alternate row colors
    for i in range(1, len(rows) + 1):
        color = "#D6E4F0" if i % 2 == 0 else "white"
        for j in range(3):
            table[i, j].set_facecolor(color)

    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "summary_table.png"), dpi=150, bbox_inches="tight")
    plt.close(fig)


# ===========================================================================
#  Score for "best" config selection
# ===========================================================================
def composite_score(r):
    """Higher is better. Weighted blend of coverage, detection, speed, safety."""
    cov = r["coverage_pct"] / 100.0
    det = r["detection_prob"]
    # Penalize long missions
    time_score = max(0, 1.0 - r["mission_time_s"] / 600.0)
    safety = 1.0 - r["nfz_dir_time_pct"] / 100.0
    return 0.35 * cov + 0.25 * det + 0.20 * time_score + 0.20 * safety


# ===========================================================================
#  Main
# ===========================================================================
def main():
    print("=" * 62)
    print("  LAWNMOWER vs ZIAN SPIRAL -- PATTERN COMPARISON")
    print("=" * 62)

    all_results = []
    lm_results = []
    sp_results = []

    total_configs = len(ALTITUDES) * len(OVERLAPS) * 2
    done = 0

    for altitude in ALTITUDES:
        for overlap in OVERLAPS:
            # --- Lawnmower ---
            done += 1
            print(f"\n[{done}/{total_configs}] Lawnmower @ {altitude}m, {int(overlap*100)}% overlap")
            try:
                lm = run_config(altitude, overlap, "lawnmower")
            except Exception as e:
                print(f"  ERROR: {e}")
                lm = None

            # --- Spiral ---
            done += 1
            print(f"[{done}/{total_configs}] Spiral    @ {altitude}m, {int(overlap*100)}% overlap")
            try:
                sp = run_config(altitude, overlap, "spiral")
            except Exception as e:
                print(f"  ERROR: {e}")
                sp = None

            if lm:
                all_results.append(lm)
                lm_results.append(lm)
            if sp:
                all_results.append(sp)
                sp_results.append(sp)

            # Print side-by-side comparison for this config
            print_comparison(lm, sp, altitude, overlap)

    # --- Summary ---
    print("\n" + "=" * 62)
    print("  OVERALL SUMMARY")
    print("=" * 62)

    if lm_results:
        lm_best = max(lm_results, key=composite_score)
        print(f"\n  Best lawnmower: {lm_best['altitude_m']}m, "
              f"{int(lm_best['overlap']*100)}% overlap "
              f"(score={composite_score(lm_best):.3f})")
        print(f"    Coverage={lm_best['coverage_pct']:.1f}%, "
              f"Time={lm_best['mission_time_s']:.0f}s, "
              f"Energy={lm_best['energy_wh']:.1f}Wh, "
              f"P(detect)={lm_best['detection_prob']:.3f}")
    else:
        lm_best = None

    if sp_results:
        sp_best = max(sp_results, key=composite_score)
        print(f"\n  Best spiral:    {sp_best['altitude_m']}m, "
              f"{int(sp_best['overlap']*100)}% overlap "
              f"(score={composite_score(sp_best):.3f})")
        print(f"    Coverage={sp_best['coverage_pct']:.1f}%, "
              f"Time={sp_best['mission_time_s']:.0f}s, "
              f"Energy={sp_best['energy_wh']:.1f}Wh, "
              f"P(detect)={sp_best['detection_prob']:.3f}")
    else:
        sp_best = None

    # --- Save JSON ---
    json_path = os.path.join(OUTPUT_DIR, "compare_v2.json")
    with open(json_path, "w") as f:
        json.dump({
            "configs": {
                "altitudes": ALTITUDES,
                "overlaps": OVERLAPS,
                "canvas_size": CANVAS_SIZE,
                "pi_fps": PI_FPS,
            },
            "results": all_results,
            "best_lawnmower": lm_best,
            "best_spiral": sp_best,
        }, f, indent=2)
    print(f"\n  Results saved: {json_path}")

    # --- Plots ---
    print("  Generating plots...")
    plot_pareto(all_results, OUTPUT_DIR)
    plot_radar(lm_best, sp_best, OUTPUT_DIR)
    plot_coverage_vs_time(all_results, OUTPUT_DIR)
    plot_summary_table(lm_best, sp_best, OUTPUT_DIR)
    print(f"  Plots saved to: {OUTPUT_DIR}/")

    print("\n" + "=" * 62)
    print("  DONE")
    print("=" * 62)


if __name__ == "__main__":
    main()
