#!/usr/bin/env python3
"""Generate geofence/NFZ protection diagram for the report.

Shows:
  - Flight Area, Search Area, SSSI polygons (actual GPS coordinates)
  - Three-layer protection: speed ramp, repulsive force, hard boundary
  - Repulsive force arrows
  - Speed profile annotation
  - Drone trajectory deflection example
  - Two-panel: without vs with geofence

Output: report/figs/geofence_diagram.pdf
Dependencies: numpy, matplotlib (no shapely needed)
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon
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
    """Buffer a polygon outward by distance metres using offset edges + arc joins.

    Pure numpy implementation -- no shapely needed.
    """
    n = len(coords)
    centroid = coords.mean(axis=0)

    # Ensure counter-clockwise winding (outward normals point away from centroid)
    cross_sum = 0.0
    for i in range(n):
        j = (i + 1) % n
        cross_sum += (coords[j, 0] - coords[i, 0]) * (coords[j, 1] + coords[i, 1])
    if cross_sum > 0:  # clockwise -- reverse
        coords = coords[::-1]

    # Compute outward normals for each edge
    normals = []
    for i in range(n):
        j = (i + 1) % n
        edge = coords[j] - coords[i]
        normal = np.array([edge[1], -edge[0]])  # rotate 90 deg CW
        norm_len = np.linalg.norm(normal)
        if norm_len > 1e-10:
            normal /= norm_len
        # Check normal points outward (away from centroid)
        mid = (coords[i] + coords[j]) / 2
        if np.dot(normal, mid - centroid) < 0:
            normal = -normal
        normals.append(normal)

    # Build buffered polygon: offset each vertex + arc at corners
    buffered = []
    for i in range(n):
        prev_i = (i - 1) % n
        n1 = normals[prev_i]  # normal of incoming edge
        n2 = normals[i]       # normal of outgoing edge

        # Offset vertex along both normals
        p = coords[i]
        p1 = p + n1 * distance
        p2 = p + n2 * distance

        # Arc from n1 to n2 around vertex
        angle1 = np.arctan2(n1[1], n1[0])
        angle2 = np.arctan2(n2[1], n2[0])

        # Go the short way around (outward arc)
        diff = angle2 - angle1
        if diff > np.pi:
            diff -= 2 * np.pi
        elif diff < -np.pi:
            diff += 2 * np.pi

        if abs(diff) < 0.05:
            # Nearly parallel -- just add the midpoint
            buffered.append((p1 + p2) / 2)
        elif diff > 0:
            # Convex corner -- add arc
            for k in range(n_arc + 1):
                t = k / n_arc
                angle = angle1 + t * diff
                buffered.append(p + distance * np.array([np.cos(angle), np.sin(angle)]))
        else:
            # Concave corner -- add intersection or just the two points
            buffered.append(p1)
            buffered.append(p2)

    return np.array(buffered)


def point_in_polygon(px, py, poly):
    """Ray-casting point-in-polygon test. Returns True if (px, py) is inside poly."""
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


# Buffer zones
sssi_hard = buffer_polygon_numpy(sssi_m.copy(), NFZ_HARD_BOUNDARY_M)
sssi_repulsive = buffer_polygon_numpy(sssi_m.copy(), NFZ_INNER_RANGE_M)
sssi_slow = buffer_polygon_numpy(sssi_m.copy(), NFZ_SLOW_ZONE_M)

# ── Colour palette ─────────────────────────────────────────────────

COL_FLIGHT = "#3B82F6"      # blue
COL_SEARCH = "#22C55E"      # green
COL_SSSI = "#DC2626"        # red
COL_SSSI_FILL = "#FCA5A5"   # light red
COL_HARD = "#991B1B"        # dark red
COL_REPULSIVE = "#EA580C"   # orange-red
COL_SLOW = "#F97316"        # orange
COL_DRONE = "#6366F1"       # indigo
COL_ARROW = "#B91C1C"       # dark red for arrows
COL_BG = "#FAFAF9"


def _compute_outward_normals(poly):
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
        # Outward normal
        normal = np.array([edge[1], -edge[0]])
        normal /= np.linalg.norm(normal)
        mid = (p1 + p2) / 2
        if np.dot(normal, mid - centroid) < 0:
            normal = -normal
        # Sample at 1/3 and 2/3 along edge
        for frac in [0.33, 0.67]:
            pt = p1 + frac * edge
            points.append(pt)
            normals.append(normal)

    return np.array(points), np.array(normals)


def draw_main_panel(ax, show_geofence=True, show_path=True, title=""):
    """Draw the field layout with optional geofence layers."""
    ax.set_facecolor(COL_BG)

    # Flight area
    fa = MplPolygon(flight_m, closed=True, fill=False,
                    edgecolor=COL_FLIGHT, linewidth=1.5, linestyle="--")
    ax.add_patch(fa)

    # Search area
    sa = MplPolygon(search_m, closed=True, fill=False,
                    edgecolor=COL_SEARCH, linewidth=2.0, linestyle="-")
    ax.add_patch(sa)

    if show_geofence:
        # Layer 3: Speed ramp zone (outermost)
        slow_patch = MplPolygon(sssi_slow, closed=True, fill=True,
                                facecolor="#FFF7ED", edgecolor=COL_SLOW,
                                linewidth=1.2, linestyle="--", alpha=0.6)
        ax.add_patch(slow_patch)

        # Layer 2: Repulsive force zone
        rep_patch = MplPolygon(sssi_repulsive, closed=True, fill=True,
                               facecolor="#FEF2F2", edgecolor=COL_REPULSIVE,
                               linewidth=1.2, linestyle="--", alpha=0.6)
        ax.add_patch(rep_patch)

        # Layer 1: Hard boundary (innermost buffer)
        hard_patch = MplPolygon(sssi_hard, closed=True, fill=True,
                                facecolor="#FEE2E2", edgecolor=COL_HARD,
                                linewidth=2.0, linestyle="-", alpha=0.7)
        ax.add_patch(hard_patch)

    # SSSI polygon (hatched)
    sssi_patch = MplPolygon(sssi_m, closed=True, fill=True,
                            facecolor=COL_SSSI_FILL, edgecolor=COL_SSSI,
                            linewidth=2.5, hatch="///", alpha=0.8)
    ax.add_patch(sssi_patch)

    # SSSI label
    cx = np.mean(sssi_m[:, 0])
    cy = np.mean(sssi_m[:, 1])
    ax.text(cx, cy, "SSSI\nNo-Fly\nZone", ha="center", va="center",
            fontsize=9, fontweight="bold", color=COL_HARD,
            path_effects=[pe.withStroke(linewidth=3, foreground="white")])

    # Takeoff marker
    ax.plot(*takeoff_m, "^", color=COL_DRONE, markersize=10, zorder=10)
    ax.annotate("Take-Off", takeoff_m, textcoords="offset points",
                xytext=(8, -12), fontsize=7, color=COL_DRONE, fontweight="bold")

    if show_geofence and show_path:
        _draw_repulsive_arrows(ax)
        _draw_drone_path(ax)

    ax.set_aspect("equal")
    ax.set_xlabel("East (m)", fontsize=9)
    ax.set_ylabel("North (m)", fontsize=9)
    ax.set_title(title, fontsize=11, fontweight="bold", pad=10)
    ax.tick_params(labelsize=8)

    # Bounds with padding
    all_pts = np.vstack([flight_m, search_m, sssi_m])
    pad = 30
    ax.set_xlim(all_pts[:, 0].min() - pad, all_pts[:, 0].max() + pad)
    ax.set_ylim(all_pts[:, 1].min() - pad, all_pts[:, 1].max() + pad)


def _draw_repulsive_arrows(ax):
    """Draw repulsive force arrows pointing away from SSSI boundary."""
    points, normals = _compute_outward_normals(sssi_m)

    for pt, normal in zip(points, normals):
        start_offset = NFZ_HARD_BOUNDARY_M + 3
        arrow_len = 14
        sx = pt[0] + normal[0] * start_offset
        sy = pt[1] + normal[1] * start_offset
        ex = sx + normal[0] * arrow_len
        ey = sy + normal[1] * arrow_len

        ax.annotate("", xy=(ex, ey), xytext=(sx, sy),
                    arrowprops=dict(arrowstyle="-|>", color=COL_ARROW,
                                    lw=2.0, mutation_scale=16),
                    zorder=5)


def _draw_drone_path(ax):
    """Draw an example drone trajectory being deflected by the repulsive force."""
    sssi_centroid = np.mean(sssi_m, axis=0)

    t = np.linspace(0, 1, 80)

    # Path stays inside flight area: approaches SSSI from the east, curves north
    start = sssi_centroid + np.array([50, -30])
    end = sssi_centroid + np.array([40, 60])
    ctrl = sssi_centroid + np.array([28, 15])

    # Quadratic Bezier
    path_x = (1-t)**2 * start[0] + 2*(1-t)*t * ctrl[0] + t**2 * end[0]
    path_y = (1-t)**2 * start[1] + 2*(1-t)*t * ctrl[1] + t**2 * end[1]

    ax.plot(path_x, path_y, color=COL_DRONE, linewidth=2.5, linestyle="-",
            zorder=8, alpha=0.9)

    # Drone dots along path
    for idx in [0, 20, 40, 60, 78]:
        ax.plot(path_x[idx], path_y[idx], "o", color=COL_DRONE, markersize=6,
                zorder=9, markeredgecolor="white", markeredgewidth=1.0)

    # Direction arrows at two points along path
    for mid in [25, 55]:
        ax.annotate("", xy=(path_x[mid+4], path_y[mid+4]),
                    xytext=(path_x[mid], path_y[mid]),
                    arrowprops=dict(arrowstyle="-|>", color=COL_DRONE, lw=2.5),
                    zorder=9)

    ax.annotate("Drone path\n(deflected by\nrepulsive force)",
                xy=(path_x[45], path_y[45]),
                textcoords="offset points", xytext=(15, 5),
                fontsize=7.5, color=COL_DRONE, fontstyle="italic", fontweight="bold",
                path_effects=[pe.withStroke(linewidth=3, foreground="white")])


def _draw_lawnmower_through_sssi(ax):
    """Draw a simple lawnmower pattern that crosses the SSSI (no-geofence case)."""
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

    ax.plot(path_x, path_y, color=COL_DRONE, linewidth=1.5, alpha=0.7, zorder=6)

    # Mark violations: test multiple sample points along each segment
    sssi_path = MplPath(np.vstack([sssi_m, sssi_m[0:1]]))
    for i in range(0, len(path_x)-1):
        # Sample 20 points along each segment
        xs_seg = np.linspace(path_x[i], path_x[i+1], 20)
        ys_seg = np.linspace(path_y[i], path_y[i+1], 20)
        inside = sssi_path.contains_points(np.column_stack([xs_seg, ys_seg]))
        if np.any(inside):
            # Draw the violating segment thicker and red
            ax.plot([path_x[i], path_x[i+1]], [path_y[i], path_y[i+1]],
                    color="#EF4444", linewidth=4.0, alpha=0.9, zorder=7)
            # Big X markers where it enters SSSI
            mx = (path_x[i] + path_x[i+1]) / 2
            my = (path_y[i] + path_y[i+1]) / 2
            ax.plot(mx, my, "X", color="#DC2626", markersize=14,
                    markeredgewidth=3, markeredgecolor="white", zorder=8)


def _draw_lawnmower_avoiding_sssi(ax):
    """Draw a lawnmower pattern that avoids the SSSI with geofence (used on right panel)."""
    y_min = search_m[:, 1].min() + 5
    y_max = search_m[:, 1].max() - 5
    x_min = search_m[:, 0].min() + 5
    x_max = search_m[:, 0].max() - 5

    spacing = 18
    ys = np.arange(y_min, y_max, spacing)

    # Use matplotlib Path to test point-in-polygon for the buffer zone
    sssi_buf_path = MplPath(np.vstack([sssi_slow, sssi_slow[0:1]]))

    for i, y in enumerate(ys):
        if i % 2 == 0:
            xs = np.linspace(x_min, x_max, 200)
        else:
            xs = np.linspace(x_max, x_min, 200)

        # Find segments outside the buffer
        inside = sssi_buf_path.contains_points(np.column_stack([xs, np.full_like(xs, y)]))
        seg_xs, seg_ys = [], []
        for j, (x, is_in) in enumerate(zip(xs, inside)):
            if not is_in:
                seg_xs.append(x)
                seg_ys.append(y)
            else:
                if len(seg_xs) > 1:
                    ax.plot(seg_xs, seg_ys, color=COL_DRONE, linewidth=1.5, alpha=0.7, zorder=6)
                seg_xs, seg_ys = [], []
        if len(seg_xs) > 1:
            ax.plot(seg_xs, seg_ys, color=COL_DRONE, linewidth=1.5, alpha=0.7, zorder=6)


# ── Speed profile inset ────────────────────────────────────────────

def draw_speed_inset(ax):
    """Draw speed vs distance-from-NFZ profile."""
    ax.set_facecolor("#FAFAF9")

    dist = np.linspace(0, NFZ_SLOW_ZONE_M + 10, 200)
    speed = np.zeros_like(dist)

    for i, d in enumerate(dist):
        if d < NFZ_HARD_BOUNDARY_M:
            speed[i] = 0  # MANUAL mode
        elif d < NFZ_SLOW_ZONE_M:
            ratio = d / NFZ_SLOW_ZONE_M
            speed[i] = NFZ_MIN_SPEED_MPS + ratio * (NFZ_ZONE_MAX_SPEED_MPS - NFZ_MIN_SPEED_MPS)
        else:
            speed[i] = SEARCH_SPEED_MPS

    ax.fill_between(dist, 0, speed, alpha=0.15, color=COL_REPULSIVE)
    ax.plot(dist, speed, color=COL_REPULSIVE, linewidth=2)

    # Zone boundaries
    ax.axvline(NFZ_HARD_BOUNDARY_M, color=COL_HARD, linewidth=1.5, linestyle=":",
               label=f"Hard ({NFZ_HARD_BOUNDARY_M:.0f} m)")
    ax.axvline(NFZ_SLOW_ZONE_M, color=COL_SLOW, linewidth=1.5, linestyle=":",
               label=f"Slow zone ({NFZ_SLOW_ZONE_M:.0f} m)")

    # Zone labels
    ax.text(NFZ_HARD_BOUNDARY_M / 2, SEARCH_SPEED_MPS * 0.85, "AUTO\n$\\rightarrow$\nMANUAL",
            ha="center", va="center", fontsize=6, color=COL_HARD, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.8))
    ax.text((NFZ_HARD_BOUNDARY_M + NFZ_SLOW_ZONE_M) / 2, SEARCH_SPEED_MPS * 0.55,
            "Speed\nRamp", ha="center", va="center", fontsize=6,
            color=COL_REPULSIVE, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.8))
    ax.text(NFZ_SLOW_ZONE_M + 5, SEARCH_SPEED_MPS * 0.85, "Normal\nSpeed",
            ha="center", va="center", fontsize=6, color=COL_SEARCH, fontweight="bold")

    # Speed annotations
    ax.annotate(f"{SEARCH_SPEED_MPS:.0f} m/s", xy=(NFZ_SLOW_ZONE_M + 2, SEARCH_SPEED_MPS),
                fontsize=7, color="#374151")
    ax.annotate(f"{NFZ_ZONE_MAX_SPEED_MPS:.0f} m/s",
                xy=(NFZ_SLOW_ZONE_M - 1, NFZ_ZONE_MAX_SPEED_MPS),
                fontsize=7, color="#374151", ha="right")
    ax.annotate(f"{NFZ_MIN_SPEED_MPS} m/s",
                xy=(NFZ_HARD_BOUNDARY_M + 1, NFZ_MIN_SPEED_MPS + 0.3),
                fontsize=7, color="#374151")

    ax.set_xlabel("Distance from NFZ boundary (m)", fontsize=8)
    ax.set_ylabel("Max speed (m/s)", fontsize=8)
    ax.set_title("(c) Speed Reduction Profile", fontsize=9, fontweight="bold")
    ax.set_xlim(0, NFZ_SLOW_ZONE_M + 12)
    ax.set_ylim(0, SEARCH_SPEED_MPS + 1)
    ax.tick_params(labelsize=7)
    ax.legend(fontsize=6, loc="lower right")
    ax.grid(True, alpha=0.3)


# ── Main figure ────────────────────────────────────────────────────

fig = plt.figure(figsize=(14, 10), dpi=150)

gs = fig.add_gridspec(2, 2, height_ratios=[2.2, 1], hspace=0.30, wspace=0.25,
                      left=0.06, right=0.97, top=0.93, bottom=0.05)

# Top-left: Without geofence
ax1 = fig.add_subplot(gs[0, 0])
draw_main_panel(ax1, show_geofence=False, show_path=False,
                title="(a) Without Geofence")
_draw_lawnmower_through_sssi(ax1)
ax1.text(0.5, 0.02, "Lawnmower path crosses SSSI boundary",
         transform=ax1.transAxes, ha="center", fontsize=8,
         color="#EF4444", fontstyle="italic", fontweight="bold",
         bbox=dict(boxstyle="round,pad=0.3", facecolor="#FEF2F2", edgecolor="#EF4444",
                   alpha=0.9))

# Top-right: With geofence (full diagram)
ax2 = fig.add_subplot(gs[0, 1])
draw_main_panel(ax2, show_geofence=True, show_path=True,
                title="(b) With Three-Layer Geofence Protection")

# Bottom-left: Speed profile
ax3 = fig.add_subplot(gs[1, 0])
draw_speed_inset(ax3)

# Bottom-right: Protection layers summary table
ax4 = fig.add_subplot(gs[1, 1])
ax4.axis("off")

summary_text = [
    ("Layer", "Distance", "Action", "Mechanism"),
    ("1. Speed Ramp", f"< {NFZ_SLOW_ZONE_M:.0f} m", f"{NFZ_MIN_SPEED_MPS}--{NFZ_ZONE_MAX_SPEED_MPS} m/s",
     "Linear speed cap"),
    ("2. Repulsive Force", f"< {NFZ_INNER_RANGE_M:.0f} m", f"{NFZ_PUSH_SPEED_MPS:.0f} m/s push",
     "Potential-field vector"),
    ("3. Auto-MANUAL", f"< {NFZ_HARD_BOUNDARY_M:.0f} m", "Full stop",
     "Mode switch to MANUAL"),
    ("0. Waypoint Filter", f"< 30 m", "Skip waypoint",
     "Plan-time removal"),
]

table = ax4.table(
    cellText=[row for row in summary_text[1:]],
    colLabels=summary_text[0],
    cellLoc="center",
    loc="center",
    colWidths=[0.22, 0.18, 0.25, 0.30],
)
table.auto_set_font_size(False)
table.set_fontsize(8)
table.scale(1.0, 1.6)

for j in range(4):
    cell = table[0, j]
    cell.set_facecolor("#1F2937")
    cell.set_text_props(color="white", fontweight="bold")

row_colors = ["#FFF7ED", "#FEF2F2", "#FEE2E2", "#F0F9FF"]
for i in range(1, 5):
    for j in range(4):
        table[i, j].set_facecolor(row_colors[i-1])
        table[i, j].set_edgecolor("#D1D5DB")

ax4.set_title("(d) Protection Layer Summary", fontsize=10, fontweight="bold", pad=15)

# Legend for top-right plot
legend_elements = [
    Line2D([0], [0], color=COL_FLIGHT, linewidth=1.5, linestyle="--", label="Flight Area"),
    Line2D([0], [0], color=COL_SEARCH, linewidth=2.0, label="Search Area"),
    MplPolygon([(0,0)], closed=True, facecolor=COL_SSSI_FILL, edgecolor=COL_SSSI,
               linewidth=2, hatch="///", label="SSSI (No-Fly)"),
    Line2D([0], [0], color=COL_SLOW, linewidth=1.2, linestyle="--",
           label=f"Speed Ramp Zone ({NFZ_SLOW_ZONE_M:.0f} m)"),
    Line2D([0], [0], color=COL_REPULSIVE, linewidth=1.2, linestyle="--",
           label=f"Repulsive Force ({NFZ_INNER_RANGE_M:.0f} m)"),
    Line2D([0], [0], color=COL_HARD, linewidth=2.0,
           label=f"Auto-MANUAL ({NFZ_HARD_BOUNDARY_M:.0f} m)"),
    Line2D([0], [0], color=COL_DRONE, linewidth=2.0, label="Drone trajectory"),
    Line2D([0], [0], color=COL_ARROW, linewidth=1.5, marker=">", markersize=6,
           label="Repulsive force vectors"),
]

ax2.legend(handles=legend_elements, loc="lower right", fontsize=7,
           framealpha=0.9, edgecolor="#D1D5DB", fancybox=True)

fig.suptitle("Geofence / NFZ Protection System", fontsize=14, fontweight="bold", y=0.97)

# Save
out_path = r"c:\Users\Bristol\Desktop\AI for Robotics\v3\report\figs\geofence_diagram.pdf"
fig.savefig(out_path, format="pdf", bbox_inches="tight", dpi=300)
print(f"Saved: {out_path}")

out_png = out_path.replace(".pdf", ".png")
fig.savefig(out_png, format="png", bbox_inches="tight", dpi=200)
print(f"Saved: {out_png}")
