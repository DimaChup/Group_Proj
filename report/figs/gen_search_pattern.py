"""Generate lawnmower search pattern figure for SAR drone report.

Shows the boustrophedon coverage pattern over the Fenswood survey area with
camera footprint strips, direction arrows, transit path, and annotations.
"""

import math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch, Rectangle
from matplotlib.lines import Line2D
from matplotlib.collections import PatchCollection
from shapely.geometry import Polygon, LineString
import os

# ── GPS coordinates from config.py ──────────────────────────────────
TAKEOFF_GPS = (51.42340640206451, -2.671446029622069)

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

# ── Camera/flight parameters from config.py ─────────────────────────
SENSOR_WIDTH_MM = 5.02
FOCAL_LENGTH_MM = 5.46
TARGET_ALT = 35.0       # search altitude (m)
IMAGE_W = 1456
IMAGE_H = 1088
OVERLAP = 0.2           # 20% overlap between strips

# ── Coordinate conversion ───────────────────────────────────────────
REF_LAT = 51.4240       # approximate centre for conversion

def gps_to_metres(lat, lon, ref_lat=None, ref_lon=None):
    """Convert GPS to local metres (East, North) relative to reference."""
    if ref_lat is None:
        ref_lat = REF_LAT
    if ref_lon is None:
        ref_lon = -2.6695  # approximate centre
    lat_m = 111132.954 - 559.822 * math.cos(2 * math.radians(lat))
    lon_m = 111132.954 * math.cos(math.radians(lat))
    x = (lon - ref_lon) * lon_m
    y = (lat - ref_lat) * lat_m
    return x, y

def polygon_to_metres(gps_list):
    """Convert list of (lat, lon) to numpy array of (x_m, y_m)."""
    pts = np.array([gps_to_metres(lat, lon) for lat, lon in gps_list])
    return pts

# ── Lawnmower pattern generation (simplified from planning.py) ──────
def generate_lawnmower(search_pts_m, alt=TARGET_ALT):
    """Generate lawnmower waypoints in local metres.

    Aligns strips to the longest edge of the search polygon, applies 20%
    overlap, returns waypoints and strip metadata for visualisation.
    """
    poly = Polygon(search_pts_m)
    # Find minimum-area bounding rectangle
    min_rect = poly.minimum_rotated_rectangle
    coords = np.array(min_rect.exterior.coords[:-1])

    # Find longest edge -> scan direction
    edges = []
    for i in range(len(coords)):
        j = (i + 1) % len(coords)
        dx = coords[j][0] - coords[i][0]
        dy = coords[j][1] - coords[i][1]
        length = math.sqrt(dx**2 + dy**2)
        angle = math.atan2(dy, dx)
        edges.append((length, angle, i, j))
    edges.sort(key=lambda e: e[0], reverse=True)
    scan_angle = edges[0][1]  # angle of longest edge

    # Camera ground footprint
    ground_footprint_m = (SENSOR_WIDTH_MM * alt) / FOCAL_LENGTH_MM
    aspect = IMAGE_H / IMAGE_W
    cross_track_footprint = ground_footprint_m  # width perpendicular to flight
    along_track_footprint = ground_footprint_m * aspect  # along flight direction
    swath_m = cross_track_footprint * (1.0 - OVERLAP)

    # Rotation to align scan direction with x-axis
    cos_a = math.cos(-scan_angle)
    sin_a = math.sin(-scan_angle)

    def rotate(pts, angle):
        c, s = math.cos(angle), math.sin(angle)
        return np.column_stack([
            pts[:, 0] * c - pts[:, 1] * s,
            pts[:, 0] * s + pts[:, 1] * c
        ])

    def rotate_pt(x, y, angle):
        c, s = math.cos(angle), math.sin(angle)
        return x * c - y * s, x * s + y * c

    # Rotate polygon so scan lines are horizontal
    rot_pts = rotate(search_pts_m, -scan_angle)
    rot_poly = Polygon(rot_pts)

    min_x, min_y, max_x, max_y = rot_poly.bounds
    inset = swath_m / 3.0

    # Generate scan lines
    strips = []
    strip_centres_rot = []
    scan_ys = []
    y = min_y + inset
    while y < max_y - inset:
        scan_ys.append(y)
        y += swath_m
    # Ensure last strip near boundary
    if scan_ys and scan_ys[-1] < max_y - inset:
        scan_ys.append(max_y - inset)

    for sy in scan_ys:
        line = LineString([(min_x - 10, sy), (max_x + 10, sy)])
        intersection = line.intersection(rot_poly)
        if intersection.is_empty:
            continue
        if intersection.geom_type == 'MultiLineString':
            # Take longest segment
            segs = list(intersection.geoms)
            segs.sort(key=lambda s: s.length, reverse=True)
            intersection = segs[0]
        if intersection.geom_type == 'LineString':
            c = list(intersection.coords)
            x_start = c[0][0] + inset
            x_end = c[-1][0] - inset
            if x_end > x_start:
                strips.append(((x_start, sy), (x_end, sy)))
                strip_centres_rot.append(sy)

    # Build zigzag waypoints (in rotated space)
    direction = 1
    waypoints_rot = []
    for strip in strips:
        if direction == 1:
            waypoints_rot.append(strip[0])
            waypoints_rot.append(strip[1])
        else:
            waypoints_rot.append(strip[1])
            waypoints_rot.append(strip[0])
        direction *= -1

    # Un-rotate waypoints back to map space
    waypoints = []
    for wx, wy in waypoints_rot:
        rx, ry = rotate_pt(wx, wy, scan_angle)
        waypoints.append((rx, ry))

    return waypoints, strips, scan_angle, swath_m, cross_track_footprint, strip_centres_rot


# ── Main figure ─────────────────────────────────────────────────────
def main():
    # Convert all zones to metres
    search_m = polygon_to_metres(SEARCH_AREA_GPS)
    flight_m = polygon_to_metres(FLIGHT_AREA_GPS)
    sssi_m = polygon_to_metres(SSSI_GPS)
    takeoff_m = np.array(gps_to_metres(*TAKEOFF_GPS))

    # Generate pattern
    wps, strips, scan_angle, swath_m, footprint_m, strip_centres = \
        generate_lawnmower(search_m)

    # ── Figure setup ────────────────────────────────────────────────
    fig, ax = plt.subplots(1, 1, figsize=(8.5, 7.5), dpi=200)
    fig.patch.set_facecolor('white')
    ax.set_facecolor('#f5f5f0')
    ax.set_aspect('equal')

    # ── Flight area (outer boundary) ────────────────────────────────
    flight_poly = plt.Polygon(flight_m, closed=True, fill=False,
                               edgecolor='#888888', linewidth=1.0,
                               linestyle='--', label='Flight area')
    ax.add_patch(flight_poly)

    # ── SSSI no-fly zone ────────────────────────────────────────────
    sssi_poly = plt.Polygon(sssi_m, closed=True, fill=True,
                             facecolor='#ff000015', edgecolor='#cc0000',
                             linewidth=1.2, linestyle='-',
                             label='SSSI (no-fly zone)')
    ax.add_patch(sssi_poly)

    # ── Search area polygon ─────────────────────────────────────────
    search_poly = plt.Polygon(search_m, closed=True, fill=True,
                               facecolor='#2196F310', edgecolor='#1565C0',
                               linewidth=1.8, label='Survey area')
    ax.add_patch(search_poly)

    # ── Camera footprint strips (semi-transparent) ──────────────────
    cos_a = math.cos(scan_angle)
    sin_a = math.sin(scan_angle)
    half_w = footprint_m / 2.0

    search_shapely = Polygon(search_m)

    for i, (start_rot, end_rot) in enumerate(strips):
        # Strip corners in rotated space
        sy = start_rot[1]
        sx_start = start_rot[0]
        sx_end = end_rot[0]

        corners_rot = [
            (sx_start, sy - half_w),
            (sx_end, sy - half_w),
            (sx_end, sy + half_w),
            (sx_start, sy + half_w),
        ]
        # Un-rotate
        corners_m = []
        for cx, cy in corners_rot:
            rx = cx * math.cos(scan_angle) - cy * math.sin(scan_angle)
            ry = cx * math.sin(scan_angle) + cy * math.cos(scan_angle)
            corners_m.append((rx, ry))

        strip_poly_shapely = Polygon(corners_m)
        clipped = strip_poly_shapely.intersection(search_shapely)
        if clipped.is_empty:
            continue

        if clipped.geom_type == 'Polygon':
            polys_to_draw = [clipped]
        elif clipped.geom_type == 'MultiPolygon':
            polys_to_draw = list(clipped.geoms)
        else:
            continue

        for cp in polys_to_draw:
            coords = np.array(cp.exterior.coords)
            color = '#4CAF50' if i % 2 == 0 else '#66BB6A'
            strip_patch = plt.Polygon(coords, closed=True, fill=True,
                                       facecolor=color, alpha=0.12,
                                       edgecolor=color, linewidth=0.3)
            ax.add_patch(strip_patch)

    # ── Overlap regions ─────────────────────────────────────────────
    # Draw overlap between adjacent strips as darker shading
    for i in range(len(strips) - 1):
        sy1 = strips[i][0][1]
        sy2 = strips[i + 1][0][1]
        # Overlap region in rotated space
        overlap_top = sy2 - half_w
        overlap_bot = sy1 + half_w
        if overlap_bot > overlap_top:
            sx_start = min(strips[i][0][0], strips[i + 1][0][0])
            sx_end = max(strips[i][1][0], strips[i + 1][1][0])
            corners_rot = [
                (sx_start, overlap_top),
                (sx_end, overlap_top),
                (sx_end, overlap_bot),
                (sx_start, overlap_bot),
            ]
            corners_m = []
            for cx, cy in corners_rot:
                rx = cx * math.cos(scan_angle) - cy * math.sin(scan_angle)
                ry = cx * math.sin(scan_angle) + cy * math.cos(scan_angle)
                corners_m.append((rx, ry))

            ol_poly_shapely = Polygon(corners_m)
            clipped = ol_poly_shapely.intersection(search_shapely)
            if not clipped.is_empty and clipped.geom_type in ('Polygon', 'MultiPolygon'):
                geoms = [clipped] if clipped.geom_type == 'Polygon' else list(clipped.geoms)
                for cp in geoms:
                    coords = np.array(cp.exterior.coords)
                    ol_patch = plt.Polygon(coords, closed=True, fill=True,
                                            facecolor='#2E7D32', alpha=0.10,
                                            edgecolor='none')
                    ax.add_patch(ol_patch)

    # ── Flight path (waypoints connected) ───────────────────────────
    wp_arr = np.array(wps)
    ax.plot(wp_arr[:, 0], wp_arr[:, 1], color='#E65100', linewidth=1.2,
            solid_capstyle='round', zorder=5)

    # ── Direction arrows on path ────────────────────────────────────
    for i in range(0, len(wps) - 1, 1):
        x0, y0 = wps[i]
        x1, y1 = wps[i + 1]
        mx = (x0 + x1) / 2
        my = (y0 + y1) / 2
        dx = x1 - x0
        dy = y1 - y0
        seg_len = math.sqrt(dx**2 + dy**2)
        if seg_len < 5:
            continue  # skip short turn segments
        # Normalise arrow direction
        scale = min(8.0, seg_len * 0.15)
        ax.annotate('', xy=(mx + dx/seg_len * scale, my + dy/seg_len * scale),
                     xytext=(mx - dx/seg_len * scale, my - dy/seg_len * scale),
                     arrowprops=dict(arrowstyle='->', color='#E65100',
                                     lw=1.2, mutation_scale=10),
                     zorder=6)

    # ── Transit path (takeoff -> first waypoint) ────────────────────
    if len(wps) > 0:
        tx = [takeoff_m[0], wps[0][0]]
        ty = [takeoff_m[1], wps[0][1]]
        ax.plot(tx, ty, color='#7B1FA2', linewidth=1.5, linestyle='--',
                zorder=4, label='Transit path')
        # Arrow on transit
        mx = (tx[0] + tx[1]) / 2
        my = (ty[0] + ty[1]) / 2
        ddx = tx[1] - tx[0]
        ddy = ty[1] - ty[0]
        tlen = math.sqrt(ddx**2 + ddy**2)
        if tlen > 0:
            sc = 8.0
            ax.annotate('', xy=(mx + ddx/tlen*sc, my + ddy/tlen*sc),
                         xytext=(mx - ddx/tlen*sc, my - ddy/tlen*sc),
                         arrowprops=dict(arrowstyle='->', color='#7B1FA2',
                                         lw=1.5, mutation_scale=12),
                         zorder=6)

    # Return path (last waypoint -> takeoff)
    if len(wps) > 0:
        rx = [wps[-1][0], takeoff_m[0]]
        ry = [wps[-1][1], takeoff_m[1]]
        ax.plot(rx, ry, color='#7B1FA2', linewidth=1.0, linestyle=':',
                zorder=4)

    # ── Start / End / Takeoff markers ───────────────────────────────
    ax.plot(*takeoff_m, marker='*', color='#7B1FA2', markersize=14,
            markeredgecolor='white', markeredgewidth=0.8, zorder=8)
    ax.annotate('Take-off', xy=takeoff_m, xytext=(8, 8),
                textcoords='offset points', fontsize=7.5, color='#7B1FA2',
                fontweight='bold', zorder=9)

    ax.plot(*wps[0], marker='o', color='#2E7D32', markersize=8,
            markeredgecolor='white', markeredgewidth=1.0, zorder=8)
    ax.annotate('Start', xy=wps[0], xytext=(8, -12),
                textcoords='offset points', fontsize=7.5, color='#2E7D32',
                fontweight='bold', zorder=9)

    ax.plot(*wps[-1], marker='s', color='#C62828', markersize=7,
            markeredgecolor='white', markeredgewidth=1.0, zorder=8)
    ax.annotate('End', xy=wps[-1], xytext=(8, 6),
                textcoords='offset points', fontsize=7.5, color='#C62828',
                fontweight='bold', zorder=9)

    # ── Strip width annotation ──────────────────────────────────────
    # Annotate on the side showing strip spacing
    if len(strips) >= 2:
        # Pick two adjacent strip centres, un-rotate to show spacing
        sy1 = strips[0][0][1]
        sy2 = strips[1][0][1]
        # Midpoint of first strip in rotated space
        mid_x_rot = strips[0][1][0] + 15  # slightly past end

        # Un-rotate both points
        p1x = mid_x_rot * math.cos(scan_angle) - sy1 * math.sin(scan_angle)
        p1y = mid_x_rot * math.sin(scan_angle) + sy1 * math.cos(scan_angle)
        p2x = mid_x_rot * math.cos(scan_angle) - sy2 * math.sin(scan_angle)
        p2y = mid_x_rot * math.sin(scan_angle) + sy2 * math.cos(scan_angle)

        ax.annotate('', xy=(p2x, p2y), xytext=(p1x, p1y),
                     arrowprops=dict(arrowstyle='<->', color='#333333', lw=1.0),
                     zorder=7)

        strip_spacing_m = abs(sy2 - sy1) / 1.0  # already in metres
        mid_ann_x = (p1x + p2x) / 2
        mid_ann_y = (p1y + p2y) / 2
        ax.annotate(f'{strip_spacing_m:.1f} m\n(strip spacing)',
                     xy=(mid_ann_x, mid_ann_y), fontsize=6.5,
                     ha='left', va='center',
                     xytext=(12, 0), textcoords='offset points',
                     color='#333333',
                     bbox=dict(boxstyle='round,pad=0.3', fc='white',
                               ec='#cccccc', alpha=0.9),
                     zorder=9)

    # ── Footprint width annotation (full camera FOV) ────────────────
    ground_w = (SENSOR_WIDTH_MM * TARGET_ALT) / FOCAL_LENGTH_MM
    info_text = (
        f'Altitude: {TARGET_ALT:.0f} m\n'
        f'FOV width: {ground_w:.1f} m\n'
        f'Overlap: {OVERLAP*100:.0f}%\n'
        f'Strips: {len(strips)}\n'
        f'Waypoints: {len(wps)}'
    )
    ax.text(0.02, 0.02, info_text, transform=ax.transAxes,
            fontsize=7, fontfamily='monospace', verticalalignment='bottom',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white',
                      edgecolor='#999999', alpha=0.95),
            zorder=10)

    # ── Scale bar ───────────────────────────────────────────────────
    # Place in bottom-right
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    # Auto-pick scale bar length
    plot_width = xlim[1] - xlim[0]
    bar_len = 50  # 50m
    if plot_width < 150:
        bar_len = 25

    bar_x = xlim[1] - bar_len - 15
    bar_y = ylim[0] + (ylim[1] - ylim[0]) * 0.04

    ax.plot([bar_x, bar_x + bar_len], [bar_y, bar_y], color='black',
            linewidth=2.5, solid_capstyle='butt', zorder=10)
    ax.plot([bar_x, bar_x], [bar_y - 1.5, bar_y + 1.5], color='black',
            linewidth=1.5, zorder=10)
    ax.plot([bar_x + bar_len, bar_x + bar_len], [bar_y - 1.5, bar_y + 1.5],
            color='black', linewidth=1.5, zorder=10)
    ax.text(bar_x + bar_len / 2, bar_y + 3.5, f'{bar_len} m',
            ha='center', va='bottom', fontsize=7, fontweight='bold', zorder=10)

    # ── North arrow ─────────────────────────────────────────────────
    arrow_x = xlim[1] - 12
    arrow_y = ylim[1] - (ylim[1] - ylim[0]) * 0.05
    arrow_len = (ylim[1] - ylim[0]) * 0.08
    ax.annotate('', xy=(arrow_x, arrow_y), xytext=(arrow_x, arrow_y - arrow_len),
                arrowprops=dict(arrowstyle='->', color='black', lw=2.0,
                                mutation_scale=14),
                zorder=10)
    ax.text(arrow_x, arrow_y + 3, 'N', ha='center', va='bottom',
            fontsize=10, fontweight='bold', zorder=10)

    # ── Legend ──────────────────────────────────────────────────────
    legend_elements = [
        mpatches.Patch(facecolor='#2196F310', edgecolor='#1565C0',
                       linewidth=1.5, label='Survey area'),
        mpatches.Patch(facecolor='#ff000015', edgecolor='#cc0000',
                       linewidth=1.0, label='SSSI no-fly zone'),
        Line2D([0], [0], color='#888888', linewidth=1.0, linestyle='--',
               label='Flight area boundary'),
        Line2D([0], [0], color='#E65100', linewidth=1.2,
               label='Search path'),
        Line2D([0], [0], color='#7B1FA2', linewidth=1.5, linestyle='--',
               label='Transit (out)'),
        Line2D([0], [0], color='#7B1FA2', linewidth=1.0, linestyle=':',
               label='Transit (return)'),
        mpatches.Patch(facecolor='#4CAF50', alpha=0.15,
                       label='Camera footprint'),
        mpatches.Patch(facecolor='#2E7D32', alpha=0.15,
                       label=f'Overlap region ({OVERLAP*100:.0f}%)'),
        Line2D([0], [0], marker='*', color='#7B1FA2', markersize=10,
               linestyle='None', markeredgecolor='white', label='Take-off'),
        Line2D([0], [0], marker='o', color='#2E7D32', markersize=7,
               linestyle='None', markeredgecolor='white', label='Search start'),
        Line2D([0], [0], marker='s', color='#C62828', markersize=6,
               linestyle='None', markeredgecolor='white', label='Search end'),
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=6.5,
              framealpha=0.95, edgecolor='#cccccc', ncol=1,
              borderpad=0.6, labelspacing=0.4)

    # ── Labels and formatting ───────────────────────────────────────
    ax.set_xlabel('East (m)', fontsize=9)
    ax.set_ylabel('North (m)', fontsize=9)
    ax.set_title('Lawnmower Search Pattern — Fenswood Farm Survey Area',
                 fontsize=11, fontweight='bold', pad=10)
    ax.tick_params(labelsize=7.5)
    ax.grid(True, alpha=0.2, linewidth=0.5)

    # Add some padding
    margin = 20
    all_pts = np.vstack([search_m, flight_m, sssi_m, [takeoff_m]])
    ax.set_xlim(all_pts[:, 0].min() - margin, all_pts[:, 0].max() + margin)
    ax.set_ylim(all_pts[:, 1].min() - margin, all_pts[:, 1].max() + margin)

    plt.tight_layout()

    # ── Save ────────────────────────────────────────────────────────
    out_dir = os.path.dirname(os.path.abspath(__file__))
    for ext in ('pdf', 'png'):
        path = os.path.join(out_dir, f'search_pattern.{ext}')
        fig.savefig(path, dpi=300, bbox_inches='tight', facecolor='white')
        print(f'Saved: {path}')
    plt.close(fig)


if __name__ == '__main__':
    main()
