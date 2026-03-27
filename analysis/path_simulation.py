"""
Path Strategy Comparison for SAR Drone Search Patterns.

Compares lawnmower, rotated lawnmower, spiral, and random-start lawnmower
strategies at 35m and 50m altitude using the real AENGM0074 survey polygon.

Outputs:
  analysis/path_comparison.png  — bar chart comparing metrics
  analysis/path_patterns.png    — all 4 patterns overlaid on polygon
"""

import sys
import os
import math
import numpy as np
import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon
from matplotlib.collections import PatchCollection

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

import config
from utils import GeoTransformer
from planning import PathPlanner

# ---------------------------------------------------------------------------
# Geo helpers
# ---------------------------------------------------------------------------

def gps_distance(p1, p2):
    """Haversine distance in metres between two (lat, lon) points."""
    R = 6371000
    lat1, lon1 = math.radians(p1[0]), math.radians(p1[1])
    lat2, lon2 = math.radians(p2[0]), math.radians(p2[1])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def path_length(wps):
    """Total path length in metres."""
    total = 0.0
    for i in range(len(wps) - 1):
        total += gps_distance(wps[i], wps[i + 1])
    return total


def count_turns(wps):
    """Count significant direction changes (> 30 deg)."""
    if len(wps) < 3:
        return 0
    turns = 0
    for i in range(1, len(wps) - 1):
        # Vectors
        v1 = (wps[i][0] - wps[i - 1][0], wps[i][1] - wps[i - 1][1])
        v2 = (wps[i + 1][0] - wps[i][0], wps[i + 1][1] - wps[i][1])
        mag1 = math.sqrt(v1[0] ** 2 + v1[1] ** 2)
        mag2 = math.sqrt(v2[0] ** 2 + v2[1] ** 2)
        if mag1 < 1e-12 or mag2 < 1e-12:
            continue
        cos_a = (v1[0] * v2[0] + v1[1] * v2[1]) / (mag1 * mag2)
        cos_a = max(-1.0, min(1.0, cos_a))
        angle = math.degrees(math.acos(cos_a))
        if angle > 30:
            turns += 1
    return turns


def polygon_area_m2(poly_gps):
    """Shoelace formula on GPS polygon (approximate, projects to metres)."""
    if len(poly_gps) < 3:
        return 0.0
    ref_lat = poly_gps[0][0]
    lat_m = 111132.954 - 559.822 * math.cos(2 * math.radians(ref_lat))
    lon_m = 111132.954 * math.cos(math.radians(ref_lat))
    xs = [(p[1] - poly_gps[0][1]) * lon_m for p in poly_gps]
    ys = [(p[0] - poly_gps[0][0]) * lat_m for p in poly_gps]
    n = len(xs)
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += xs[i] * ys[j] - xs[j] * ys[i]
    return abs(area) / 2.0


def estimate_coverage(wps, alt, poly_gps, map_w, map_h, geo):
    """Estimate coverage as fraction of polygon area swept by camera swath."""
    if len(wps) < 2:
        return 0.0

    # Ground swath width in metres
    ground_w = (config.SENSOR_WIDTH_MM * alt) / config.FOCAL_LENGTH_MM
    half_swath_px = int((ground_w / 2.0) * geo.pix_per_m)

    # Build polygon mask
    poly_px = [geo.gps_to_pixels(p[0], p[1]) for p in poly_gps]
    poly_mask = np.zeros((map_h, map_w), dtype=np.uint8)
    cv2.fillPoly(poly_mask, [np.array(poly_px, dtype=np.int32)], 255)
    poly_area_px = np.count_nonzero(poly_mask)
    if poly_area_px == 0:
        return 0.0

    # Draw swath along path
    swath_mask = np.zeros((map_h, map_w), dtype=np.uint8)
    for i in range(len(wps) - 1):
        p1 = geo.gps_to_pixels(wps[i][0], wps[i][1])
        p2 = geo.gps_to_pixels(wps[i + 1][0], wps[i + 1][1])
        cv2.line(swath_mask, p1, p2, 255, thickness=max(1, half_swath_px * 2))

    # Coverage = intersection / polygon area
    covered = cv2.bitwise_and(swath_mask, poly_mask)
    return np.count_nonzero(covered) / poly_area_px * 100.0


# ---------------------------------------------------------------------------
# Energy model
# ---------------------------------------------------------------------------

HOVER_POWER_W = 150.0
DRAG_COEFF_W = 50.0
REF_SPEED = 5.0
TURN_TIME_S = 4.0  # seconds per U-turn (decelerate + rotate + accelerate)
TURN_ENERGY_W = HOVER_POWER_W  # hovering during turn


def energy_joules(dist_m, speed_mps, n_turns):
    """Total energy estimate: hover + drag along path + turn hover."""
    if speed_mps < 0.1:
        speed_mps = 0.1
    flight_time = dist_m / speed_mps
    drag_power = DRAG_COEFF_W * (speed_mps / REF_SPEED) ** 2
    straight_energy = (HOVER_POWER_W + drag_power) * flight_time
    turn_energy = n_turns * TURN_TIME_S * TURN_ENERGY_W
    return straight_energy + turn_energy


# ---------------------------------------------------------------------------
# Strategy generators
# ---------------------------------------------------------------------------

MAP_W = 4000
MAP_H = 3000


def make_planner(poly_gps, geo):
    """Create a PathPlanner with the polygon in pixel coords."""
    poly_px = [geo.gps_to_pixels(p[0], p[1]) for p in poly_gps]
    return PathPlanner(geo, poly_px)


def strategy_lawnmower(poly_gps, geo, alt, drone_gps=None):
    """Standard lawnmower from planning.py."""
    planner = make_planner(poly_gps, geo)
    wps = planner.generate_search_pattern(MAP_W, MAP_H, drone_gps=drone_gps, alt_override=alt)
    return wps


def strategy_lawnmower_rotated(poly_gps, geo, alt, drone_gps=None):
    """Lawnmower rotated 90 degrees (perpendicular to optimal)."""
    # Rotate the polygon 90 deg around its centroid, plan, then rotate waypoints back
    clat = sum(p[0] for p in poly_gps) / len(poly_gps)
    clon = sum(p[1] for p in poly_gps) / len(poly_gps)

    lat_m = 111132.954 - 559.822 * math.cos(2 * math.radians(clat))
    lon_m = 111132.954 * math.cos(math.radians(clat))

    # Convert to local metres, rotate 90 deg, convert back
    def rotate_point(p, angle_deg):
        dx = (p[1] - clon) * lon_m
        dy = (p[0] - clat) * lat_m
        a = math.radians(angle_deg)
        rx = dx * math.cos(a) - dy * math.sin(a)
        ry = dx * math.sin(a) + dy * math.cos(a)
        return (clat + ry / lat_m, clon + rx / lon_m)

    rot_poly = [rotate_point(p, 90) for p in poly_gps]
    planner = make_planner(rot_poly, geo)
    rot_drone = rotate_point(drone_gps, 90) if drone_gps else None
    rot_wps = planner.generate_search_pattern(MAP_W, MAP_H, drone_gps=rot_drone, alt_override=alt)

    # Rotate waypoints back -90 deg
    wps = [rotate_point(p, -90) for p in rot_wps]
    return wps


def strategy_spiral(poly_gps, geo, alt, drone_gps=None):
    """Spiral inward from polygon edge."""
    planner = make_planner(poly_gps, geo)
    wps = planner.generate_spiral_pattern(MAP_W, MAP_H, drone_gps=drone_gps, alt_override=alt)
    return wps


def strategy_random_start(poly_gps, geo, alt, drone_gps=None):
    """Lawnmower starting from a different corner (use last polygon vertex as 'drone')."""
    # Pick a corner far from the default start
    far_corner = poly_gps[len(poly_gps) // 2]
    planner = make_planner(poly_gps, geo)
    wps = planner.generate_search_pattern(MAP_W, MAP_H, drone_gps=far_corner, alt_override=alt)
    return wps


STRATEGIES = [
    ("Lawnmower (optimal)", strategy_lawnmower),
    ("Lawnmower 90-deg", strategy_lawnmower_rotated),
    ("Spiral inward", strategy_spiral),
    ("Lawnmower (alt start)", strategy_random_start),
]

# ---------------------------------------------------------------------------
# Main simulation
# ---------------------------------------------------------------------------

def run_simulation():
    # Load KML zones
    kml_path = os.path.join(PROJECT_ROOT, "flight_plans", "AENGM0074.kml")
    if os.path.exists(kml_path):
        config.load_kml_zones(kml_path)
    else:
        # Try root
        kml_path2 = os.path.join(PROJECT_ROOT, "AENGM0074.kml")
        if os.path.exists(kml_path2):
            config.load_kml_zones(kml_path2)
        else:
            print("[WARN] KML not found, using fallback SEARCH_AREA_GPS")

    poly_gps = config.SEARCH_AREA_GPS
    takeoff = config.TAKEOFF_GPS or poly_gps[0]
    area_m2 = polygon_area_m2(poly_gps)

    geo = GeoTransformer(MAP_W)

    altitudes = [35, 50]
    results = {}  # (strategy_name, alt) -> dict of metrics

    print("=" * 80)
    print(f"SEARCH AREA: {len(poly_gps)} vertices, {area_m2:.0f} m^2 ({area_m2/10000:.2f} ha)")
    print(f"TAKEOFF: {takeoff}")
    print("=" * 80)

    for alt in altitudes:
        speed = config.speed_for_altitude(alt)
        swath_m = (config.SENSOR_WIDTH_MM * alt) / config.FOCAL_LENGTH_MM
        print(f"\n--- Altitude {alt}m | Speed {speed:.1f} m/s | Swath {swath_m:.1f}m ---")

        for name, func in STRATEGIES:
            wps = func(poly_gps, geo, alt, drone_gps=takeoff)
            dist = path_length(wps)
            turns = count_turns(wps)
            t_flight = dist / speed + turns * TURN_TIME_S if speed > 0 else 0
            energy = energy_joules(dist, speed, turns)
            coverage = estimate_coverage(wps, alt, poly_gps, MAP_W, MAP_H, geo)

            results[(name, alt)] = {
                "wps": wps,
                "dist_m": dist,
                "turns": turns,
                "speed_mps": speed,
                "time_s": t_flight,
                "energy_kJ": energy / 1000.0,
                "coverage_pct": coverage,
            }

            print(f"  {name:25s} | {len(wps):3d} wps | {dist:7.0f}m | "
                  f"{turns:2d} turns | {t_flight:5.0f}s ({t_flight/60:.1f}min) | "
                  f"{energy/1000:.1f} kJ | {coverage:5.1f}% cov")

    # ------------------------------------------------------------------
    # Print comparison table
    # ------------------------------------------------------------------
    print("\n" + "=" * 110)
    print(f"{'Strategy':25s} | {'Alt':>3s} | {'Dist (m)':>8s} | {'Turns':>5s} | "
          f"{'Time (s)':>8s} | {'Time (min)':>10s} | {'Energy (kJ)':>11s} | {'Coverage':>8s}")
    print("-" * 110)
    for alt in altitudes:
        for name, _ in STRATEGIES:
            r = results[(name, alt)]
            print(f"{name:25s} | {alt:3d} | {r['dist_m']:8.0f} | {r['turns']:5d} | "
                  f"{r['time_s']:8.0f} | {r['time_s']/60:10.1f} | {r['energy_kJ']:11.1f} | "
                  f"{r['coverage_pct']:7.1f}%")
        if alt != altitudes[-1]:
            print("-" * 110)
    print("=" * 110)

    # ------------------------------------------------------------------
    # Plot 1: Bar chart comparison (path_comparison.png)
    # ------------------------------------------------------------------
    out_dir = os.path.dirname(os.path.abspath(__file__))

    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle("Search Strategy Comparison", fontsize=16, fontweight="bold")

    metrics = [
        ("dist_m", "Path Length (m)", "Distance"),
        ("turns", "Number of Turns", "Turns"),
        ("time_s", "Flight Time (s)", "Time"),
        ("energy_kJ", "Energy (kJ)", "Energy"),
        ("coverage_pct", "Coverage (%)", "Coverage"),
    ]

    strategy_names = [n for n, _ in STRATEGIES]
    colors = ["#2196F3", "#FF9800", "#4CAF50", "#9C27B0"]
    x = np.arange(len(strategy_names))
    bar_w = 0.35

    for idx, (key, ylabel, title) in enumerate(metrics):
        ax = axes[idx // 3][idx % 3]
        vals_35 = [results[(n, 35)][key] for n in strategy_names]
        vals_50 = [results[(n, 50)][key] for n in strategy_names]

        bars1 = ax.bar(x - bar_w / 2, vals_35, bar_w, label="35m", color="#2196F3", alpha=0.85)
        bars2 = ax.bar(x + bar_w / 2, vals_50, bar_w, label="50m", color="#FF9800", alpha=0.85)

        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.set_xticks(x)
        ax.set_xticklabels([n.replace(" (optimal)", "\n(optimal)").replace(" (alt start)", "\n(alt start)")
                            for n in strategy_names], fontsize=8, ha="center")
        ax.legend(fontsize=8)

        # Add value labels
        for bar in bars1:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, h, f"{h:.0f}",
                    ha="center", va="bottom", fontsize=7)
        for bar in bars2:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, h, f"{h:.0f}",
                    ha="center", va="bottom", fontsize=7)

    # Hide unused subplot
    axes[1][2].axis("off")

    # Add summary text
    best_35 = min(strategy_names, key=lambda n: results[(n, 35)]["time_s"])
    best_50 = min(strategy_names, key=lambda n: results[(n, 50)]["time_s"])
    summary = (
        f"Polygon area: {area_m2:.0f} m$^2$ ({area_m2/10000:.2f} ha)\n"
        f"Fastest at 35m: {best_35} ({results[(best_35, 35)]['time_s']/60:.1f} min)\n"
        f"Fastest at 50m: {best_50} ({results[(best_50, 50)]['time_s']/60:.1f} min)\n"
        f"Energy model: hover {HOVER_POWER_W:.0f}W + drag {DRAG_COEFF_W:.0f}W*(v/5)$^2$\n"
        f"Turn penalty: {TURN_TIME_S:.0f}s hover per turn"
    )
    axes[1][2].text(0.1, 0.5, summary, transform=axes[1][2].transAxes,
                    fontsize=11, verticalalignment="center",
                    bbox=dict(boxstyle="round,pad=0.5", facecolor="lightyellow", alpha=0.8))

    plt.tight_layout()
    comparison_path = os.path.join(out_dir, "path_comparison.png")
    plt.savefig(comparison_path, dpi=150, bbox_inches="tight")
    print(f"\nSaved: {comparison_path}")
    plt.close()

    # ------------------------------------------------------------------
    # Plot 2: Path patterns overlaid on polygon (path_patterns.png)
    # ------------------------------------------------------------------
    fig, axes = plt.subplots(2, 4, figsize=(22, 11))
    fig.suptitle("Search Patterns on Survey Polygon", fontsize=16, fontweight="bold")

    # Convert polygon to local metres for plotting
    ref_lat = poly_gps[0][0]
    lat_m_scale = 111132.954 - 559.822 * math.cos(2 * math.radians(ref_lat))
    lon_m_scale = 111132.954 * math.cos(math.radians(ref_lat))

    def gps_to_local(p):
        return ((p[1] - poly_gps[0][1]) * lon_m_scale,
                (p[0] - poly_gps[0][0]) * lat_m_scale)

    poly_local = [gps_to_local(p) for p in poly_gps]
    poly_xs = [p[0] for p in poly_local] + [poly_local[0][0]]
    poly_ys = [p[1] for p in poly_local] + [poly_local[0][1]]

    path_colors = ["#2196F3", "#E91E63", "#4CAF50", "#FF9800"]

    for row, alt in enumerate(altitudes):
        for col, (name, _) in enumerate(STRATEGIES):
            ax = axes[row][col]
            r = results[(name, alt)]
            wps = r["wps"]

            # Polygon fill
            ax.fill(poly_xs, poly_ys, alpha=0.1, color="gray")
            ax.plot(poly_xs, poly_ys, "k-", linewidth=1.5, label="Polygon")

            # Path
            if wps:
                wp_local = [gps_to_local(p) for p in wps]
                wxs = [p[0] for p in wp_local]
                wys = [p[1] for p in wp_local]
                ax.plot(wxs, wys, "-", color=path_colors[col], linewidth=0.8, alpha=0.8)
                ax.plot(wxs[0], wys[0], "go", markersize=6, zorder=5, label="Start")
                ax.plot(wxs[-1], wys[-1], "rs", markersize=6, zorder=5, label="End")

            ax.set_title(f"{name}\n{alt}m | {r['dist_m']:.0f}m | {r['time_s']/60:.1f}min | {r['coverage_pct']:.0f}%",
                         fontsize=9)
            ax.set_aspect("equal")
            ax.set_xlabel("East (m)", fontsize=8)
            if col == 0:
                ax.set_ylabel("North (m)", fontsize=8)
            ax.tick_params(labelsize=7)
            if row == 0 and col == 0:
                ax.legend(fontsize=7, loc="upper left")

    plt.tight_layout()
    patterns_path = os.path.join(out_dir, "path_patterns.png")
    plt.savefig(patterns_path, dpi=150, bbox_inches="tight")
    print(f"Saved: {patterns_path}")
    plt.close()

    print("\nDone.")


if __name__ == "__main__":
    run_simulation()
