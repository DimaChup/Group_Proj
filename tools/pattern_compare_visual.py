#!/usr/bin/env python3
"""
Optimal Pattern Comparison — Publication-Quality Visual
========================================================

Generates a single comparison figure showing the two optimal search patterns
(Lawnmower 35m/0% overlap vs Zian Spiral 50m/0% overlap) side by side with
speed heatmaps, camera footprints, metrics bar chart, and radar chart.

Usage:
    cd v3/
    python tools/pattern_compare_visual.py

Output:
    tools/pattern_analysis/optimal_comparison.png
"""

import sys
import os
import math
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch
from matplotlib.collections import PatchCollection
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
    simulate_path, gps_to_local, camera_footprint,
)
from planning import PathPlanner
from utils import GeoTransformer

# Zian's planner
ZIAN_DIR = os.path.join(PROJECT_ROOT, "Zian", "path_planner")
sys.path.insert(0, ZIAN_DIR)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pattern_analysis")
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ===========================================================================
#  Constants
# ===========================================================================
CANVAS_SIZE = 4800

# Colours
CLR_LAWNMOWER = "#2196F3"
CLR_SPIRAL = "#FF9800"
CLR_NFZ = "#D32F2F"
CLR_SEARCH = "#4CAF50"
CLR_SWATH = "#64B5F6"

# Reference point (centroid of search area)
_lats = [p[0] for p in config.SEARCH_AREA_GPS]
_lons = [p[1] for p in config.SEARCH_AREA_GPS]
REF_LAT = sum(_lats) / len(_lats)
REF_LON = sum(_lons) / len(_lons)


# ===========================================================================
#  Pattern generation
# ===========================================================================
def generate_lawnmower_wps(altitude):
    """Generate lawnmower waypoints via PathPlanner."""
    geo = GeoTransformer(CANVAS_SIZE)
    search_px = [geo.gps_to_pixels(lat, lon) for lat, lon in config.SEARCH_AREA_GPS]
    planner = PathPlanner(geo, search_px)
    planner._no_turn = True
    wps = planner.generate_search_pattern(
        CANVAS_SIZE, CANVAS_SIZE,
        drone_gps=config.TAKEOFF_GPS,
        alt_override=altitude,
    )
    return wps


def generate_zian_spiral_wps(altitude):
    """Generate Zian perimeter spiral waypoints."""
    _, footprint_h = camera_footprint(altitude)
    import perimeter_planner as zpp
    zpp.HALF_SWATH = footprint_h / 3.0
    zpp.SWATH = footprint_h
    waypoints_dicts = zpp.plan()
    wps = []
    for wp in waypoints_dicts:
        if wp["name"] == "enter":
            continue
        wps.append((wp["lat"], wp["lon"]))
    return wps


def to_local(gps_pts):
    """Convert list of (lat, lon) to local (x_east, y_north) metres."""
    return [gps_to_local(lat, lon, REF_LAT, REF_LON) for lat, lon in gps_pts]


# ===========================================================================
#  Scale bar helper
# ===========================================================================
def draw_scale_bar(ax, length_m=50, loc="lower left"):
    """Draw a scale bar on the axes."""
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    range_x = xlim[1] - xlim[0]
    range_y = ylim[1] - ylim[0]

    if "left" in loc:
        x0 = xlim[0] + 0.06 * range_x
    else:
        x0 = xlim[1] - 0.06 * range_x - length_m

    if "lower" in loc:
        y0 = ylim[0] + 0.06 * range_y
    else:
        y0 = ylim[1] - 0.06 * range_y

    ax.plot([x0, x0 + length_m], [y0, y0], color="black", linewidth=2.5,
            solid_capstyle="butt")
    # End ticks
    tick_h = range_y * 0.012
    ax.plot([x0, x0], [y0 - tick_h, y0 + tick_h], color="black", linewidth=1.5)
    ax.plot([x0 + length_m, x0 + length_m], [y0 - tick_h, y0 + tick_h],
            color="black", linewidth=1.5)
    ax.text(x0 + length_m / 2, y0 + tick_h * 2.5, f"{length_m} m",
            ha="center", va="bottom", fontsize=8, fontweight="bold")


def draw_north_arrow(ax):
    """Draw a north arrow in the upper-right corner."""
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    range_x = xlim[1] - xlim[0]
    range_y = ylim[1] - ylim[0]

    cx = xlim[1] - 0.07 * range_x
    cy = ylim[1] - 0.08 * range_y
    arrow_len = 0.06 * range_y

    ax.annotate("", xy=(cx, cy), xytext=(cx, cy - arrow_len),
                arrowprops=dict(arrowstyle="-|>", color="black", lw=1.5))
    ax.text(cx, cy + arrow_len * 0.15, "N", ha="center", va="bottom",
            fontsize=9, fontweight="bold")


# ===========================================================================
#  Map plot (one pattern)
# ===========================================================================
def plot_pattern_map(ax, wps_gps, sim_result, altitude, footprint_w, footprint_h,
                     title, pattern_color):
    """Plot a single pattern on the given axes with speed heatmap and swath."""
    # Convert zones to local
    search_local = to_local(config.SEARCH_AREA_GPS)
    sssi_local = to_local(config.SSSI_GPS)
    wps_local = to_local(wps_gps)

    # --- SSSI / NFZ polygon ---
    sssi_xy = np.array(sssi_local + [sssi_local[0]])
    nfz_patch = mpatches.Polygon(sssi_xy, closed=True,
                                  facecolor=CLR_NFZ, alpha=0.15,
                                  edgecolor=CLR_NFZ, linewidth=1.5,
                                  linestyle="-", label="SSSI (NFZ)")
    ax.add_patch(nfz_patch)

    # --- Search polygon boundary ---
    search_xy = np.array(search_local + [search_local[0]])
    ax.plot(search_xy[:, 0], search_xy[:, 1], color=CLR_SEARCH,
            linewidth=2, linestyle="--", label="Search area", zorder=3)

    # --- Camera footprint swath along path ---
    points = sim_result.points
    swath_patches = []
    step = max(1, len(points) // 80)  # ~80 rectangles along path
    for i in range(0, len(points) - 1, step):
        pt = points[i]
        heading_rad = math.radians(pt.heading_deg)
        cx, cy = pt.x_m, pt.y_m

        # Rectangle corners (footprint_w along-track, footprint_h cross-track)
        hw = footprint_w / 2.0
        hh = footprint_h / 2.0

        cos_h = math.cos(heading_rad)
        sin_h = math.sin(heading_rad)

        # Local rectangle corners (along = heading, cross = perpendicular)
        corners_local = [(-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)]
        corners_world = []
        for dx, dy in corners_local:
            rx = cx + dx * sin_h + dy * cos_h
            ry = cy + dx * cos_h - dy * sin_h
            corners_world.append((rx, ry))

        patch = mpatches.Polygon(corners_world, closed=True)
        swath_patches.append(patch)

    if swath_patches:
        pc = PatchCollection(swath_patches, facecolor=CLR_SWATH, alpha=0.05,
                             edgecolor="none")
        ax.add_collection(pc)

    # --- Speed-coloured path ---
    cmap = plt.cm.RdYlGn
    speeds = np.array([pt.speed_mps for pt in points])
    xs = np.array([pt.x_m for pt in points])
    ys = np.array([pt.y_m for pt in points])

    speed_max = max(speeds.max(), 1.0)
    norm = Normalize(vmin=0, vmax=speed_max)

    # Draw as coloured line segments
    for i in range(len(xs) - 1):
        color = cmap(norm(speeds[i]))
        ax.plot([xs[i], xs[i + 1]], [ys[i], ys[i + 1]],
                color=color, linewidth=2.0, solid_capstyle="round", zorder=4)

    # --- Waypoints as white dots ---
    wp_x = [p[0] for p in wps_local]
    wp_y = [p[1] for p in wps_local]
    ax.scatter(wp_x, wp_y, s=28, c="white", edgecolors="black",
               linewidths=0.8, zorder=6)
    for idx, (wx, wy) in enumerate(wps_local):
        ax.annotate(str(idx + 1), (wx, wy), fontsize=5.5, ha="center", va="center",
                    fontweight="bold", zorder=7)

    # --- Start / end markers ---
    ax.scatter([wp_x[0]], [wp_y[0]], s=80, c=CLR_SEARCH, marker="D",
               edgecolors="black", linewidths=1, zorder=8, label="Start")
    ax.scatter([wp_x[-1]], [wp_y[-1]], s=80, c=CLR_NFZ, marker="D",
               edgecolors="black", linewidths=1, zorder=8, label="End")

    # --- Formatting ---
    ax.set_aspect("equal")
    ax.set_title(title, fontsize=11, fontweight="bold", pad=8)
    ax.set_xlabel("East (m)", fontsize=9)
    ax.set_ylabel("North (m)", fontsize=9)
    ax.tick_params(labelsize=8)
    ax.grid(True, alpha=0.15, linewidth=0.5)

    # Expand limits slightly
    all_x = list(search_xy[:, 0]) + list(xs)
    all_y = list(search_xy[:, 1]) + list(ys)
    margin = 20
    ax.set_xlim(min(all_x) - margin, max(all_x) + margin)
    ax.set_ylim(min(all_y) - margin, max(all_y) + margin)

    draw_scale_bar(ax, length_m=50)
    draw_north_arrow(ax)

    # Speed colorbar
    sm = ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, fraction=0.035, pad=0.04, shrink=0.75)
    cbar.set_label("Speed (m/s)", fontsize=8)
    cbar.ax.tick_params(labelsize=7)

    return ax


# ===========================================================================
#  Bar chart (normalised metrics comparison)
# ===========================================================================
def plot_metrics_bars(ax, lm_data, sp_data):
    """Side-by-side bar chart of key metrics, normalised."""
    metrics = [
        ("Time\n(s)", "mission_time_s", False),
        ("Energy\n(Wh)", "energy_wh", False),
        ("Coverage\n(%)", "coverage_pct", True),
        ("Path\n(m)", "path_length_m", False),
        ("NFZ exp.\n(%)", "nfz_dir_time_pct", False),
        ("Waypoints", "waypoints", False),
    ]

    labels = []
    lm_vals = []
    sp_vals = []

    for label, key, _ in metrics:
        labels.append(label)
        lm_vals.append(lm_data[key])
        sp_vals.append(sp_data[key])

    # Normalise each metric to percentage of the WORSE (larger) value
    lm_norm = []
    sp_norm = []
    for i, (label, key, higher_better) in enumerate(metrics):
        max_val = max(lm_vals[i], sp_vals[i], 1e-9)
        lm_norm.append(lm_vals[i] / max_val * 100)
        sp_norm.append(sp_vals[i] / max_val * 100)

    x = np.arange(len(labels))
    width = 0.32

    bars_lm = ax.bar(x - width / 2, lm_norm, width, color=CLR_LAWNMOWER,
                      edgecolor="white", linewidth=0.5, label="Lawnmower", zorder=3)
    bars_sp = ax.bar(x + width / 2, sp_norm, width, color=CLR_SPIRAL,
                      edgecolor="white", linewidth=0.5, label="Spiral", zorder=3)

    # Value labels on bars
    for bar, val in zip(bars_lm, lm_vals):
        fmt = f"{val:.0f}" if val >= 10 else f"{val:.1f}"
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1.5,
                fmt, ha="center", va="bottom", fontsize=7, fontweight="bold",
                color=CLR_LAWNMOWER)

    for bar, val in zip(bars_sp, sp_vals):
        fmt = f"{val:.0f}" if val >= 10 else f"{val:.1f}"
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1.5,
                fmt, ha="center", va="bottom", fontsize=7, fontweight="bold",
                color=CLR_SPIRAL)

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylabel("% of worst value", fontsize=9)
    ax.set_title("Key Metrics Comparison", fontsize=11, fontweight="bold", pad=8)
    ax.legend(fontsize=8, loc="upper right")
    ax.set_ylim(0, 115)
    ax.grid(axis="y", alpha=0.2, linewidth=0.5)
    ax.tick_params(labelsize=8)


# ===========================================================================
#  Radar / spider chart
# ===========================================================================
def plot_radar(ax, lm_data, sp_data):
    """5-axis spider chart comparing both patterns."""
    categories = ["Coverage", "Speed\n(1/time)", "Efficiency\n(1/energy)",
                   "Safety\n(1-NFZ%)", "Detection"]
    N = len(categories)

    def normalise(d):
        cov = d["coverage_pct"] / 100.0
        det = d["detection_prob"]
        inv_time = 1.0 / max(d["mission_time_s"], 1.0) * 300
        inv_energy = 1.0 / max(d["energy_wh"], 0.1) * 20
        safety = 1.0 - d["nfz_dir_time_pct"] / 100.0
        return [cov, min(inv_time, 1.0), min(inv_energy, 1.0), safety, det]

    lm_vals = normalise(lm_data)
    sp_vals = normalise(sp_data)

    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    angles += angles[:1]
    lm_vals += lm_vals[:1]
    sp_vals += sp_vals[:1]

    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)

    ax.plot(angles, lm_vals, "o-", linewidth=2, color=CLR_LAWNMOWER,
            markersize=5, label="Lawnmower", zorder=4)
    ax.fill(angles, lm_vals, alpha=0.12, color=CLR_LAWNMOWER)
    ax.plot(angles, sp_vals, "s-", linewidth=2, color=CLR_SPIRAL,
            markersize=5, label="Spiral", zorder=4)
    ax.fill(angles, sp_vals, alpha=0.12, color=CLR_SPIRAL)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=8.5)
    ax.set_ylim(0, 1.05)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(["0.2", "0.4", "0.6", "0.8", "1.0"], fontsize=7,
                        color="grey")
    ax.set_title("Multi-Criteria Radar", fontsize=11, fontweight="bold",
                  pad=18, y=1.05)
    ax.legend(fontsize=8, loc="upper right", bbox_to_anchor=(1.25, 1.12))
    ax.grid(True, alpha=0.3, linewidth=0.5)


# ===========================================================================
#  Summary text box
# ===========================================================================
def add_summary_text(fig, lm, sp):
    """Add a text summary strip at the bottom of the figure."""
    # Compute percentage differences
    time_diff = (1 - sp["mission_time_s"] / lm["mission_time_s"]) * 100
    energy_diff = (1 - sp["energy_wh"] / lm["energy_wh"]) * 100
    nfz_diff = (1 - sp["nfz_dir_time_pct"] / lm["nfz_dir_time_pct"]) * 100 if lm["nfz_dir_time_pct"] > 0 else 0

    left_lines = [
        f"LAWNMOWER  (35 m,  0% overlap)",
        f"Coverage:      {lm['coverage_pct']:.1f}%",
        f"Time:          {lm['mission_time_s']:.0f} s  ({lm['mission_time_s']/60:.1f} min)",
        f"Energy:        {lm['energy_wh']:.1f} Wh",
        f"NFZ exposure:  {lm['nfz_dir_time_pct']:.1f}%",
        f"Waypoints:     {lm['waypoints']}",
    ]

    right_lines = [
        f"ZIAN SPIRAL  (50 m,  0% overlap)",
        f"Coverage:      {sp['coverage_pct']:.1f}%",
        f"Time:          {sp['mission_time_s']:.0f} s  ({sp['mission_time_s']/60:.1f} min)   [{time_diff:.0f}% faster]",
        f"Energy:        {sp['energy_wh']:.1f} Wh   [{energy_diff:.0f}% less]",
        f"NFZ exposure:  {sp['nfz_dir_time_pct']:.1f}%   [{nfz_diff:.0f}% less]",
        f"Waypoints:     {sp['waypoints']}",
    ]

    left_text = "\n".join(left_lines)
    right_text = "\n".join(right_lines)

    fig.text(0.26, 0.025, left_text, ha="center", va="bottom",
             fontsize=8.5, fontfamily="monospace", color=CLR_LAWNMOWER,
             fontweight="bold",
             bbox=dict(boxstyle="round,pad=0.5", facecolor="#E3F2FD",
                       edgecolor=CLR_LAWNMOWER, alpha=0.9))

    fig.text(0.74, 0.025, right_text, ha="center", va="bottom",
             fontsize=8.5, fontfamily="monospace", color="#E65100",
             fontweight="bold",
             bbox=dict(boxstyle="round,pad=0.5", facecolor="#FFF3E0",
                       edgecolor=CLR_SPIRAL, alpha=0.9))


# ===========================================================================
#  Main
# ===========================================================================
def main():
    print("Generating optimal pattern comparison figure...")

    # --- Load pre-computed results ---
    json_path = os.path.join(OUTPUT_DIR, "compare_v2.json")
    with open(json_path, "r") as f:
        data = json.load(f)

    # Find lawnmower 35m/0% and spiral 50m/0%
    lm_data = None
    sp_data = None
    for r in data["results"]:
        if (r["pattern"] == "lawnmower" and r["altitude_m"] == 35
                and r["overlap"] == 0.0):
            lm_data = r
        if (r["pattern"] == "spiral" and r["altitude_m"] == 50
                and r["overlap"] == 0.0):
            sp_data = r

    if lm_data is None or sp_data is None:
        print("ERROR: Could not find required configs in compare_v2.json")
        sys.exit(1)

    print(f"  Lawnmower: 35m, 0% overlap  ({lm_data['coverage_pct']}% coverage)")
    print(f"  Spiral:    50m, 0% overlap  ({sp_data['coverage_pct']}% coverage)")

    # --- Generate waypoints ---
    print("  Generating lawnmower waypoints...")
    lm_wps = generate_lawnmower_wps(35)
    print(f"    {len(lm_wps)} waypoints")

    print("  Generating spiral waypoints...")
    sp_wps = generate_zian_spiral_wps(50)
    print(f"    {len(sp_wps)} waypoints")

    # --- Simulate physics ---
    print("  Simulating lawnmower physics...")
    lm_sim = simulate_path(
        waypoints_gps=lm_wps,
        altitude_m=35,
        sssi_polygon_gps=config.SSSI_GPS,
        config_params={"speed_for_altitude": config.speed_for_altitude},
    )

    print("  Simulating spiral physics...")
    sp_sim = simulate_path(
        waypoints_gps=sp_wps,
        altitude_m=50,
        sssi_polygon_gps=config.SSSI_GPS,
        config_params={"speed_for_altitude": config.speed_for_altitude},
    )

    # --- Camera footprints ---
    lm_fw, lm_fh = camera_footprint(35)
    sp_fw, sp_fh = camera_footprint(50)

    # =======================================================================
    #  Build the figure
    # =======================================================================
    print("  Building figure...")

    fig = plt.figure(figsize=(16, 14), facecolor="white")

    # GridSpec: 2 rows, 2 cols + bottom strip
    gs = fig.add_gridspec(2, 2, hspace=0.32, wspace=0.30,
                          top=0.93, bottom=0.16, left=0.06, right=0.96)

    # Row 1: Map plots
    ax_lm = fig.add_subplot(gs[0, 0])
    ax_sp = fig.add_subplot(gs[0, 1])

    # Row 2: Bar chart + Radar
    ax_bar = fig.add_subplot(gs[1, 0])
    ax_radar = fig.add_subplot(gs[1, 1], polar=True)

    # --- Plot maps ---
    plot_pattern_map(ax_lm, lm_wps, lm_sim, 35, lm_fw, lm_fh,
                     "Lawnmower \u2014 35 m,  0% overlap", CLR_LAWNMOWER)
    plot_pattern_map(ax_sp, sp_wps, sp_sim, 50, sp_fw, sp_fh,
                     "Zian Spiral \u2014 50 m,  0% overlap", CLR_SPIRAL)

    # --- Plot charts ---
    plot_metrics_bars(ax_bar, lm_data, sp_data)
    plot_radar(ax_radar, lm_data, sp_data)

    # --- Summary text ---
    add_summary_text(fig, lm_data, sp_data)

    # --- Supertitle ---
    fig.suptitle("Search Pattern Comparison: Lawnmower vs Perimeter Spiral",
                 fontsize=14, fontweight="bold", y=0.97)

    # --- Save ---
    out_path = os.path.join(OUTPUT_DIR, "optimal_comparison.png")
    fig.savefig(out_path, dpi=150, facecolor="white", bbox_inches="tight")
    plt.close(fig)
    print(f"\n  Saved: {out_path}")
    print("  Done.")


if __name__ == "__main__":
    main()
