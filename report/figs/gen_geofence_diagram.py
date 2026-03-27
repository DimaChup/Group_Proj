#!/usr/bin/env python3
"""Generate geofence/NFZ protection diagram for the report.

Shows:
  - Flight Area, Search Area, SSSI polygons (actual GPS coordinates)
  - Three-layer protection: speed ramp, repulsive force, hard boundary
  - Repulsive force arrows
  - Speed profile annotation
  - Drone trajectory deflection example
  - Two-panel: without vs with geofence

Output: report/figs/geofence_diagram.pdf + .png
Dependencies: numpy, matplotlib (no shapely needed)
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon, FancyArrowPatch
from matplotlib.lines import Line2D
from matplotlib.path import Path as MplPath
import matplotlib.patheffects as pe

# ── Actual coordinates from config.py ──────────────────────────────

SEARCH_AREA_GPS = [
    (51.42326956502679, -2.670948345438704),
    (51.42287025017865, -2.670045428650557),
    (51.42336622593724, -2.668169295906676),
    (51.42421477437771, -2.668809768621569),
    (51.42354069739116, -2.671277780473196),
]
FLIGHT_AREA_GPS = [
    (51.42342595349562, -2.671720766408759),
    (51.42124623420381, -2.670134027271237),
    (51.42244011936099, -2.66568781888585),
    (51.42469179370701, -2.667060227266051),
]
SSSI_GPS = [
    (51.42353586816967, -2.671451754138619),
    (51.42215640321154, -2.669768242108598),
    (51.42267105383615, -2.667705438815299),
    (51.42335592245168, -2.668164601092489),
    (51.42286082606338, -2.670043418345824),
    (51.42326667015552, -2.670965419051837),
    (51.42356862274763, -2.671324297543731),
]
TAKEOFF_GPS = (51.42340640206451, -2.671446029622069)

# NFZ parameters from config.py
NFZ_HARD_BOUNDARY_M = 3.0
NFZ_SLOW_ZONE_M = 20.0
NFZ_INNER_OFFSET_M = 20.0
NFZ_INNER_RANGE_M = 23.0
NFZ_PUSH_SPEED_MPS = 3.0
NFZ_MIN_SPEED_MPS = 0.3
NFZ_ZONE_MAX_SPEED_MPS = 3.0
SEARCH_SPEED_MPS = 10.0

# ── GPS to local metres ────────────────────────────────────────────

REF_LAT = np.mean([p[0] for p in FLIGHT_AREA_GPS])
REF_LON = np.mean([p[1] for p in FLIGHT_AREA_GPS])
M_PER_DEG_LAT = 111320.0
M_PER_DEG_LON = 111320.0 * np.cos(np.radians(REF_LAT))


def gps_to_m(lat, lon):
    return ((lon - REF_LON) * M_PER_DEG_LON, (lat - REF_LAT) * M_PER_DEG_LAT)


def poly_to_m(gps_list):
    return np.array([gps_to_m(lat, lon) for lat, lon in gps_list])


flight_m = poly_to_m(FLIGHT_AREA_GPS)
search_m = poly_to_m(SEARCH_AREA_GPS)
sssi_m = poly_to_m(SSSI_GPS)
takeoff_m = np.array(gps_to_m(*TAKEOFF_GPS))


# ── Pure-numpy polygon buffering ───────────────────────────────────

def buffer_polygon_numpy(coords, distance, n_arc=8):
    """Buffer a polygon outward by distance metres using offset edges + arc joins."""
    n = len(coords)
    centroid = coords.mean(axis=0)

    # Ensure counter-clockwise winding
    cross_sum = 0.0
    for i in range(n):
        j = (i + 1) % n
        cross_sum += (coords[j, 0] - coords[i, 0]) * (coords[j, 1] + coords[i, 1])
    if cross_sum > 0:
        coords = coords[::-1]

    # Compute outward normals for each edge
    normals = []
    for i in range(n):
        j = (i + 1) % n
        edge = coords[j] - coords[i]
        normal = np.array([edge[1], -edge[0]])
        norm_len = np.linalg.norm(normal)
        if norm_len > 1e-10:
            normal /= norm_len
        mid = (coords[i] + coords[j]) / 2
        if np.dot(normal, mid - centroid) < 0:
            normal = -normal
        normals.append(normal)

    # Build buffered polygon
    buffered = []
    for i in range(n):
        prev_i = (i - 1) % n
        n1 = normals[prev_i]
        n2 = normals[i]
        p = coords[i]
        p1 = p + n1 * distance
        p2 = p + n2 * distance
        angle1 = np.arctan2(n1[1], n1[0])
        angle2 = np.arctan2(n2[1], n2[0])
        diff = angle2 - angle1
        if diff > np.pi:
            diff -= 2 * np.pi
        elif diff < -np.pi:
            diff += 2 * np.pi

        if abs(diff) < 0.05:
            buffered.append((p1 + p2) / 2)
        elif diff > 0:
            for k in range(n_arc + 1):
                t = k / n_arc
                angle = angle1 + t * diff
                buffered.append(p + distance * np.array([np.cos(angle), np.sin(angle)]))
        else:
            buffered.append(p1)
            buffered.append(p2)

    return np.array(buffered)


# Buffer zones
sssi_hard = buffer_polygon_numpy(sssi_m.copy(), NFZ_HARD_BOUNDARY_M)
sssi_repulsive = buffer_polygon_numpy(sssi_m.copy(), NFZ_INNER_RANGE_M)
sssi_slow = buffer_polygon_numpy(sssi_m.copy(), NFZ_SLOW_ZONE_M)

# ── Colour palette ─────────────────────────────────────────────────

COL_FLIGHT = "#2563EB"       # bright blue
COL_SEARCH = "#16A34A"       # green
COL_SSSI = "#DC2626"         # red
COL_SSSI_FILL = "#FCA5A5"    # light red
COL_HARD = "#7F1D1D"         # very dark red
COL_REPULSIVE = "#EA580C"    # orange-red
COL_SLOW = "#F59E0B"         # amber/orange
COL_DRONE = "#4F46E5"        # indigo
COL_ARROW = "#B91C1C"        # dark red for arrows
COL_BG = "#FAFAF9"
COL_VIOLATION = "#EF4444"    # bright red for violations


def _compute_outward_normals(poly, samples_per_edge=2):
    """Compute outward-pointing unit normals at sampled boundary points."""
    n = len(poly)
    centroid = poly.mean(axis=0)
    points = []
    normals = []

    for i in range(n):
        j = (i + 1) % n
        p1 = poly[i]
        p2 = poly[j]
        edge = p2 - p1
        edge_len = np.linalg.norm(edge)
        if edge_len < 1e-6:
            continue
        normal = np.array([edge[1], -edge[0]])
        normal /= np.linalg.norm(normal)
        mid = (p1 + p2) / 2
        if np.dot(normal, mid - centroid) < 0:
            normal = -normal
        for frac in np.linspace(0.2, 0.8, samples_per_edge):
            pt = p1 + frac * edge
            points.append(pt)
            normals.append(normal)

    return np.array(points), np.array(normals)


def _draw_zones(ax):
    """Draw the three protection zones with distinct visual styles."""
    # Layer 3: Speed ramp zone (outermost) - amber dashed
    slow_patch = MplPolygon(sssi_slow, closed=True, fill=True,
                            facecolor="#FEF3C7", edgecolor=COL_SLOW,
                            linewidth=1.8, linestyle=(0, (8, 4)), alpha=0.45,
                            label="Speed Ramp Zone")
    ax.add_patch(slow_patch)

    # Layer 2: Repulsive force zone - orange dashed
    rep_patch = MplPolygon(sssi_repulsive, closed=True, fill=True,
                           facecolor="#FFEDD5", edgecolor=COL_REPULSIVE,
                           linewidth=2.0, linestyle=(0, (5, 3)), alpha=0.55,
                           label="Repulsive Zone")
    ax.add_patch(rep_patch)

    # Layer 1: Hard boundary (innermost buffer) - dark red solid
    hard_patch = MplPolygon(sssi_hard, closed=True, fill=True,
                            facecolor="#FEE2E2", edgecolor=COL_HARD,
                            linewidth=2.5, linestyle="-", alpha=0.7,
                            label="Hard Boundary")
    ax.add_patch(hard_patch)


def _draw_sssi(ax):
    """Draw the SSSI polygon prominently with hatching."""
    sssi_patch = MplPolygon(sssi_m, closed=True, fill=True,
                            facecolor=COL_SSSI_FILL, edgecolor=COL_SSSI,
                            linewidth=3.0, hatch="////", alpha=0.85)
    ax.add_patch(sssi_patch)

    # Bold SSSI label
    cx = np.mean(sssi_m[:, 0])
    cy = np.mean(sssi_m[:, 1])
    ax.text(cx, cy, "SSSI\nNo-Fly\nZone", ha="center", va="center",
            fontsize=10, fontweight="bold", color="#7F1D1D",
            path_effects=[pe.withStroke(linewidth=4, foreground="white")])


def _draw_field(ax):
    """Draw flight area and search area boundaries."""
    fa = MplPolygon(flight_m, closed=True, fill=False,
                    edgecolor=COL_FLIGHT, linewidth=2.0, linestyle="--",
                    zorder=3)
    ax.add_patch(fa)

    sa = MplPolygon(search_m, closed=True, fill=False,
                    edgecolor=COL_SEARCH, linewidth=2.5, linestyle="-",
                    zorder=3)
    ax.add_patch(sa)

    # Takeoff marker
    ax.plot(*takeoff_m, "^", color=COL_DRONE, markersize=12, zorder=10,
            markeredgecolor="white", markeredgewidth=1.5)
    ax.annotate("Take-Off", takeoff_m, textcoords="offset points",
                xytext=(10, -14), fontsize=8, color=COL_DRONE, fontweight="bold",
                path_effects=[pe.withStroke(linewidth=2, foreground="white")])


def _set_axes(ax, title):
    """Configure axes bounds and labels."""
    ax.set_facecolor(COL_BG)
    ax.set_aspect("equal")
    ax.set_xlabel("East (m)", fontsize=10)
    ax.set_ylabel("North (m)", fontsize=10)
    ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    ax.tick_params(labelsize=8)

    all_pts = np.vstack([flight_m, search_m, sssi_m])
    pad = 35
    ax.set_xlim(all_pts[:, 0].min() - pad, all_pts[:, 0].max() + pad)
    ax.set_ylim(all_pts[:, 1].min() - pad, all_pts[:, 1].max() + pad)


def _draw_repulsive_arrows(ax):
    """Draw bold repulsive force arrows pointing away from SSSI boundary.

    Uses the buffered hard-boundary polygon (3m offset) as the base, so
    arrows start cleanly outside the SSSI hatching area.
    """
    # Use the hard boundary (3m buffer) as base for cleaner arrow origins
    points, normals = _compute_outward_normals(sssi_hard, samples_per_edge=3)

    # Also check that arrow tip stays inside the slow zone (for visual neatness)
    sssi_path = MplPath(np.vstack([sssi_m, sssi_m[0:1]]))

    for pt, normal in zip(points, normals):
        start_offset = 4
        arrow_len = 12
        sx = pt[0] + normal[0] * start_offset
        sy = pt[1] + normal[1] * start_offset

        # Skip arrows whose start is inside the SSSI (concave polygon issue)
        if sssi_path.contains_point([sx, sy]):
            continue

        dx = normal[0] * arrow_len
        dy = normal[1] * arrow_len

        ax.annotate("", xy=(sx + dx, sy + dy), xytext=(sx, sy),
                    arrowprops=dict(arrowstyle="-|>", color=COL_ARROW,
                                    lw=2.5, mutation_scale=20,
                                    shrinkA=0, shrinkB=0),
                    zorder=7)


def _draw_drone_path_deflected(ax):
    """Draw drone trajectory being deflected by the repulsive force, with
    a ghost straight-line 'would have gone' path for contrast."""
    sssi_centroid = np.mean(sssi_m, axis=0)

    t = np.linspace(0, 1, 100)

    # Deflected path: approaches SSSI from south-east, curves north around it
    start = sssi_centroid + np.array([70, -50])
    end = sssi_centroid + np.array([50, 80])
    ctrl = sssi_centroid + np.array([35, 15])

    # Quadratic Bezier
    path_x = (1-t)**2 * start[0] + 2*(1-t)*t * ctrl[0] + t**2 * end[0]
    path_y = (1-t)**2 * start[1] + 2*(1-t)*t * ctrl[1] + t**2 * end[1]

    # Ghost line: where it WOULD have gone without geofence (straight, dashed)
    ax.plot([start[0], end[0]], [start[1], end[1]],
            color="#9CA3AF", linewidth=1.8, linestyle=(0, (4, 4)), alpha=0.6, zorder=5)
    # Place label near the start of the ghost line, away from SSSI
    ax.text(start[0] - 5, start[1] + 10,
            "Without\ngeofence", ha="right", va="bottom", fontsize=7,
            color="#6B7280", fontstyle="italic",
            bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.8,
                      edgecolor="#9CA3AF", linewidth=0.5))

    # Deflected path - bold indigo with white outline for clarity
    ax.plot(path_x, path_y, color="white", linewidth=5.0, linestyle="-",
            zorder=7, alpha=0.8)  # white outline
    ax.plot(path_x, path_y, color=COL_DRONE, linewidth=3.0, linestyle="-",
            zorder=8, alpha=0.95)

    # Drone position dots
    for idx in [0, 25, 50, 75, 98]:
        ax.plot(path_x[idx], path_y[idx], "o", color=COL_DRONE, markersize=8,
                zorder=9, markeredgecolor="white", markeredgewidth=2.0)

    # Direction arrows along the path
    for mid in [18, 48, 72]:
        ax.annotate("", xy=(path_x[mid+6], path_y[mid+6]),
                    xytext=(path_x[mid], path_y[mid]),
                    arrowprops=dict(arrowstyle="-|>", color=COL_DRONE, lw=3.0,
                                    mutation_scale=18),
                    zorder=9)

    # Label with clear background
    ax.annotate("Deflected\ntrajectory",
                xy=(path_x[75], path_y[75]),
                textcoords="offset points", xytext=(22, 12),
                fontsize=9, color=COL_DRONE, fontstyle="italic", fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.85,
                          edgecolor=COL_DRONE, linewidth=0.8),
                arrowprops=dict(arrowstyle="-|>", color=COL_DRONE, lw=1.2),
                zorder=10)


def _draw_lawnmower_through_sssi(ax):
    """Draw a lawnmower pattern that crosses the SSSI (no-geofence case)."""
    y_min = search_m[:, 1].min() + 5
    y_max = search_m[:, 1].max() - 5
    x_min = search_m[:, 0].min() + 5
    x_max = search_m[:, 0].max() - 5

    spacing = 18
    ys = np.arange(y_min, y_max, spacing)
    path_x, path_y = [], []
    for i, y in enumerate(ys):
        if i % 2 == 0:
            path_x.extend([x_min, x_max])
            path_y.extend([y, y])
        else:
            path_x.extend([x_max, x_min])
            path_y.extend([y, y])

    # Draw the full path in indigo first
    ax.plot(path_x, path_y, color=COL_DRONE, linewidth=1.8, alpha=0.5, zorder=6)

    # Mark violations: test sample points along each segment
    sssi_path = MplPath(np.vstack([sssi_m, sssi_m[0:1]]))
    violation_count = 0
    for i in range(0, len(path_x)-1):
        xs_seg = np.linspace(path_x[i], path_x[i+1], 30)
        ys_seg = np.linspace(path_y[i], path_y[i+1], 30)
        inside = sssi_path.contains_points(np.column_stack([xs_seg, ys_seg]))
        if np.any(inside):
            # Draw the violating segment thick and red
            ax.plot([path_x[i], path_x[i+1]], [path_y[i], path_y[i+1]],
                    color=COL_VIOLATION, linewidth=5.0, alpha=0.9, zorder=7)
            # Big X markers at violation points
            mx = (path_x[i] + path_x[i+1]) / 2
            my = (path_y[i] + path_y[i+1]) / 2
            ax.plot(mx, my, "X", color="#B91C1C", markersize=16,
                    markeredgewidth=3.5, markeredgecolor="white", zorder=8)
            violation_count += 1

    # Add danger annotation in upper-right area of panel (a), pointing to a violation
    if violation_count > 0:
        # Find a middle violation point
        viol_pts = []
        for i in range(0, len(path_x)-1):
            xs_seg = np.linspace(path_x[i], path_x[i+1], 20)
            ys_seg = np.linspace(path_y[i], path_y[i+1], 20)
            inside = sssi_path.contains_points(np.column_stack([xs_seg, ys_seg]))
            if np.any(inside):
                viol_pts.append(((path_x[i] + path_x[i+1]) / 2,
                                 (path_y[i] + path_y[i+1]) / 2))
        if viol_pts:
            # Pick middle violation for annotation target
            vp = viol_pts[len(viol_pts) // 2]
            ax.annotate(f"{violation_count} path segments\nenter SSSI",
                        xy=vp, textcoords="offset points",
                        xytext=(60, 35), fontsize=8.5, color="#B91C1C",
                        fontweight="bold",
                        bbox=dict(boxstyle="round,pad=0.3", facecolor="#FEF2F2",
                                  edgecolor="#B91C1C", linewidth=1.0, alpha=0.95),
                        arrowprops=dict(arrowstyle="-|>", color="#B91C1C", lw=1.5,
                                        connectionstyle="arc3,rad=0.2"),
                        zorder=10)


def _draw_lawnmower_avoiding_sssi(ax):
    """Draw a lawnmower pattern that avoids the SSSI with geofence."""
    y_min = search_m[:, 1].min() + 5
    y_max = search_m[:, 1].max() - 5
    x_min = search_m[:, 0].min() + 5
    x_max = search_m[:, 0].max() - 5

    spacing = 18
    ys = np.arange(y_min, y_max, spacing)

    sssi_buf_path = MplPath(np.vstack([sssi_slow, sssi_slow[0:1]]))

    for i, y in enumerate(ys):
        if i % 2 == 0:
            xs = np.linspace(x_min, x_max, 200)
        else:
            xs = np.linspace(x_max, x_min, 200)

        inside = sssi_buf_path.contains_points(np.column_stack([xs, np.full_like(xs, y)]))
        seg_xs, seg_ys = [], []
        for j, (x, is_in) in enumerate(zip(xs, inside)):
            if not is_in:
                seg_xs.append(x)
                seg_ys.append(y)
            else:
                if len(seg_xs) > 1:
                    ax.plot(seg_xs, seg_ys, color=COL_DRONE, linewidth=2.0, alpha=0.7, zorder=6)
                seg_xs, seg_ys = [], []
        if len(seg_xs) > 1:
            ax.plot(seg_xs, seg_ys, color=COL_DRONE, linewidth=2.0, alpha=0.7, zorder=6)


# ── Speed profile ─────────────────────────────────────────────────

def draw_speed_inset(ax):
    """Draw speed vs distance-from-NFZ profile."""
    ax.set_facecolor("#FAFAF9")

    dist = np.linspace(0, NFZ_SLOW_ZONE_M + 10, 300)
    speed = np.zeros_like(dist)

    for i, d in enumerate(dist):
        if d < NFZ_HARD_BOUNDARY_M:
            speed[i] = 0  # MANUAL mode
        elif d < NFZ_SLOW_ZONE_M:
            ratio = d / NFZ_SLOW_ZONE_M
            speed[i] = NFZ_MIN_SPEED_MPS + ratio * (NFZ_ZONE_MAX_SPEED_MPS - NFZ_MIN_SPEED_MPS)
        else:
            speed[i] = SEARCH_SPEED_MPS

    # Fill zones with distinct colours
    # Zone 1: MANUAL (0 to 3m)
    mask_manual = dist < NFZ_HARD_BOUNDARY_M
    ax.fill_between(dist, 0, speed, where=mask_manual,
                    alpha=0.25, color=COL_HARD, zorder=2)
    # Zone 2: Speed ramp (3 to 20m)
    mask_ramp = (dist >= NFZ_HARD_BOUNDARY_M) & (dist < NFZ_SLOW_ZONE_M)
    ax.fill_between(dist, 0, speed, where=mask_ramp,
                    alpha=0.15, color=COL_REPULSIVE, zorder=2)
    # Zone 3: Normal (20m+)
    mask_normal = dist >= NFZ_SLOW_ZONE_M
    ax.fill_between(dist, 0, speed, where=mask_normal,
                    alpha=0.08, color=COL_SEARCH, zorder=2)

    # Speed line
    ax.plot(dist, speed, color=COL_REPULSIVE, linewidth=2.5, zorder=5)

    # Zone boundary lines
    ax.axvline(NFZ_HARD_BOUNDARY_M, color=COL_HARD, linewidth=2.0, linestyle=":",
               label=f"Hard boundary ({NFZ_HARD_BOUNDARY_M:.0f} m)", zorder=3)
    ax.axvline(NFZ_SLOW_ZONE_M, color=COL_SLOW, linewidth=2.0, linestyle=":",
               label=f"Slow zone edge ({NFZ_SLOW_ZONE_M:.0f} m)", zorder=3)

    # Zone labels with background boxes
    ax.text(NFZ_HARD_BOUNDARY_M / 2, SEARCH_SPEED_MPS * 0.75,
            "MANUAL\nmode",
            ha="center", va="center", fontsize=7, color=COL_HARD, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.9,
                      edgecolor=COL_HARD, linewidth=0.8))
    ax.text((NFZ_HARD_BOUNDARY_M + NFZ_SLOW_ZONE_M) / 2, SEARCH_SPEED_MPS * 0.5,
            "Speed\nRamp",
            ha="center", va="center", fontsize=7, color=COL_REPULSIVE, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.9,
                      edgecolor=COL_REPULSIVE, linewidth=0.8))
    ax.text(NFZ_SLOW_ZONE_M + 5, SEARCH_SPEED_MPS * 0.75,
            "Normal\nspeed",
            ha="center", va="center", fontsize=7, color=COL_SEARCH, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.9,
                      edgecolor=COL_SEARCH, linewidth=0.8))

    # Speed annotations with lines
    ax.annotate(f"{SEARCH_SPEED_MPS:.0f} m/s",
                xy=(NFZ_SLOW_ZONE_M + 2, SEARCH_SPEED_MPS),
                fontsize=8, color="#374151", fontweight="bold",
                path_effects=[pe.withStroke(linewidth=2, foreground="white")])
    ax.annotate(f"{NFZ_ZONE_MAX_SPEED_MPS:.0f} m/s",
                xy=(NFZ_SLOW_ZONE_M - 1, NFZ_ZONE_MAX_SPEED_MPS + 0.3),
                fontsize=7.5, color="#374151", ha="right")
    ax.annotate(f"{NFZ_MIN_SPEED_MPS} m/s",
                xy=(NFZ_HARD_BOUNDARY_M + 1.5, NFZ_MIN_SPEED_MPS + 0.5),
                fontsize=7.5, color="#374151")

    # Horizontal reference lines
    ax.axhline(SEARCH_SPEED_MPS, color="#D1D5DB", linewidth=0.8, linestyle="--", zorder=1)
    ax.axhline(NFZ_ZONE_MAX_SPEED_MPS, color="#D1D5DB", linewidth=0.8, linestyle="--", zorder=1)

    ax.set_xlabel("Distance from NFZ boundary (m)", fontsize=9)
    ax.set_ylabel("Max speed (m/s)", fontsize=9)
    ax.set_title("(c) Speed Reduction Profile", fontsize=11, fontweight="bold")
    ax.set_xlim(0, NFZ_SLOW_ZONE_M + 12)
    ax.set_ylim(0, SEARCH_SPEED_MPS + 1.5)
    ax.tick_params(labelsize=8)
    ax.legend(fontsize=7, loc="center right")
    ax.grid(True, alpha=0.2, zorder=0)


# ── Main figure ────────────────────────────────────────────────────

fig = plt.figure(figsize=(14, 10), dpi=150)

gs = fig.add_gridspec(2, 2, height_ratios=[2.2, 1], hspace=0.32, wspace=0.28,
                      left=0.06, right=0.97, top=0.92, bottom=0.06)

# ── Panel (a): Without geofence ───────────────────────────────────
ax1 = fig.add_subplot(gs[0, 0])
_draw_field(ax1)
_draw_sssi(ax1)
_draw_lawnmower_through_sssi(ax1)
_set_axes(ax1, "(a) Without Geofence")

# Warning banner at bottom
ax1.text(0.5, 0.02, "Lawnmower path crosses SSSI boundary",
         transform=ax1.transAxes, ha="center", fontsize=9,
         color=COL_VIOLATION, fontstyle="italic", fontweight="bold",
         bbox=dict(boxstyle="round,pad=0.4", facecolor="#FEF2F2",
                   edgecolor=COL_VIOLATION, linewidth=1.5, alpha=0.95))

# ── Panel (b): With geofence ─────────────────────────────────────
ax2 = fig.add_subplot(gs[0, 1])
_draw_field(ax2)
_draw_zones(ax2)
_draw_sssi(ax2)
_draw_repulsive_arrows(ax2)
_draw_drone_path_deflected(ax2)
_set_axes(ax2, "(b) With Three-Layer Geofence Protection")

# Legend
legend_elements = [
    Line2D([0], [0], color=COL_FLIGHT, linewidth=2.0, linestyle="--",
           label="Flight Area"),
    Line2D([0], [0], color=COL_SEARCH, linewidth=2.5,
           label="Search Area"),
    MplPolygon([(0,0)], closed=True, facecolor=COL_SSSI_FILL, edgecolor=COL_SSSI,
               linewidth=2.5, hatch="////", label="SSSI (No-Fly Zone)"),
    Line2D([0], [0], color=COL_SLOW, linewidth=1.8, linestyle="--",
           label=f"Speed Ramp ({NFZ_SLOW_ZONE_M:.0f} m)"),
    Line2D([0], [0], color=COL_REPULSIVE, linewidth=2.0, linestyle="--",
           label=f"Repulsive Zone ({NFZ_INNER_RANGE_M:.0f} m)"),
    Line2D([0], [0], color=COL_HARD, linewidth=2.5,
           label=f"Hard Boundary ({NFZ_HARD_BOUNDARY_M:.0f} m)"),
    Line2D([0], [0], color=COL_DRONE, linewidth=3.0,
           label="Drone trajectory"),
    Line2D([0], [0], color=COL_ARROW, linewidth=2.0, marker=">", markersize=8,
           linestyle="none", label="Repulsive force"),
]

ax2.legend(handles=legend_elements, loc="lower left", fontsize=7.5,
           framealpha=0.95, edgecolor="#9CA3AF", fancybox=True,
           borderpad=0.8, handlelength=2.0)

# ── Panel (c): Speed profile ─────────────────────────────────────
ax3 = fig.add_subplot(gs[1, 0])
draw_speed_inset(ax3)

# ── Panel (d): Protection layer summary table ─────────────────────
ax4 = fig.add_subplot(gs[1, 1])
ax4.axis("off")

summary_text = [
    ("Layer", "Distance", "Action", "Mechanism"),
    ("1. Speed Ramp", f"< {NFZ_SLOW_ZONE_M:.0f} m",
     f"{NFZ_MIN_SPEED_MPS}--{NFZ_ZONE_MAX_SPEED_MPS} m/s", "Linear speed cap"),
    ("2. Repulsive Force", f"< {NFZ_INNER_RANGE_M:.0f} m",
     f"{NFZ_PUSH_SPEED_MPS:.0f} m/s push", "Potential-field vector"),
    ("3. Auto-MANUAL", f"< {NFZ_HARD_BOUNDARY_M:.0f} m",
     "Full stop", "Mode switch to MANUAL"),
    ("0. Waypoint Filter", f"< 30 m",
     "Skip waypoint", "Plan-time removal"),
]

table = ax4.table(
    cellText=[row for row in summary_text[1:]],
    colLabels=summary_text[0],
    cellLoc="center",
    loc="center",
    colWidths=[0.22, 0.18, 0.25, 0.30],
)
table.auto_set_font_size(False)
table.set_fontsize(8.5)
table.scale(1.0, 1.7)

for j in range(4):
    cell = table[0, j]
    cell.set_facecolor("#1F2937")
    cell.set_text_props(color="white", fontweight="bold", fontsize=9)

row_colors = ["#FFF7ED", "#FEF2F2", "#FEE2E2", "#EFF6FF"]
for i in range(1, 5):
    for j in range(4):
        table[i, j].set_facecolor(row_colors[i-1])
        table[i, j].set_edgecolor("#D1D5DB")

ax4.set_title("(d) Protection Layer Summary", fontsize=11, fontweight="bold", pad=18)

# Suptitle
fig.suptitle("Geofence / NFZ Protection System", fontsize=15, fontweight="bold", y=0.97)

# Save
out_path = r"c:\Users\Bristol\Desktop\AI for Robotics\v3\report\figs\geofence_diagram.pdf"
fig.savefig(out_path, format="pdf", bbox_inches="tight", dpi=300)
print(f"Saved: {out_path}")

out_png = out_path.replace(".pdf", ".png")
fig.savefig(out_png, format="png", bbox_inches="tight", dpi=200)
print(f"Saved: {out_png}")
