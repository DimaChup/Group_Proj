"""Generate 5-layer geofence system figure for SAR drone report."""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch
from shapely.geometry import Polygon as ShapelyPolygon
from pathlib import Path
import os

# ── GPS coordinates from config.py ──────────────────────────────
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
SEARCH_AREA_GPS = [
    (51.42326956502679, -2.670948345438704),
    (51.42287025017865, -2.670045428650557),
    (51.42336622593724, -2.668169295906676),
    (51.42421477437771, -2.668809768621569),
    (51.42354069739116, -2.671277780473196),
]
TAKEOFF_GPS = (51.42340640206451, -2.671446029622069)

# ── Coordinate conversion ───────────────────────────────────────
# Use centre of Flight Area as reference
all_lats = [p[0] for p in FLIGHT_AREA_GPS + SSSI_GPS + SEARCH_AREA_GPS]
all_lons = [p[1] for p in FLIGHT_AREA_GPS + SSSI_GPS + SEARCH_AREA_GPS]
ref_lat = np.mean(all_lats)
ref_lon = np.mean(all_lons)

M_PER_DEG_LAT = 111320.0
M_PER_DEG_LON = 111320.0 * np.cos(np.radians(ref_lat))

def gps_to_m(lat, lon):
    return ((lon - ref_lon) * M_PER_DEG_LON, (lat - ref_lat) * M_PER_DEG_LAT)

def poly_to_m(pts):
    return np.array([gps_to_m(p[0], p[1]) for p in pts])

flight_m = poly_to_m(FLIGHT_AREA_GPS)
sssi_m = poly_to_m(SSSI_GPS)
search_m = poly_to_m(SEARCH_AREA_GPS)
tol_m = np.array(gps_to_m(*TAKEOFF_GPS))

# ── 10m buffer around SSSI using Shapely ────────────────────────
sssi_poly = ShapelyPolygon(sssi_m)
buffer_poly = sssi_poly.buffer(10.0, resolution=32)
buffer_coords = np.array(buffer_poly.exterior.coords)

# 20m speed-ramp zone
speed_ramp_poly = sssi_poly.buffer(20.0, resolution=32)
speed_ramp_coords = np.array(speed_ramp_poly.exterior.coords)

# ── Sample drone trajectory (avoids SSSI + buffer) ──────────────
# Lawnmower-style path through the search area, curving away from SSSI
trajectory = np.array([
    gps_to_m(51.42415, -2.66900),   # top-right area
    gps_to_m(51.42400, -2.66870),
    gps_to_m(51.42380, -2.66870),   # turn
    gps_to_m(51.42380, -2.66930),
    gps_to_m(51.42360, -2.66930),   # turn
    gps_to_m(51.42360, -2.66870),
    gps_to_m(51.42340, -2.66870),   # turn
    gps_to_m(51.42340, -2.66960),
    gps_to_m(51.42320, -2.66960),   # turn — curves away from buffer
    gps_to_m(51.42320, -2.66900),
    gps_to_m(51.42300, -2.66900),   # turn
    gps_to_m(51.42300, -2.66960),
])

# ── Figure ──────────────────────────────────────────────────────
fig, ax = plt.subplots(1, 1, figsize=(8.5, 9.5))

# Layer 4: Speed ramp zone (outermost visual layer)
speed_ramp_patch = plt.Polygon(
    speed_ramp_coords, closed=True,
    facecolor='#FFE0B2', edgecolor='#FF9800', linewidth=1.2,
    linestyle=':', alpha=0.35, zorder=1,
    label='Speed ramp zone (20\u2009m)'
)
ax.add_patch(speed_ramp_patch)

# Layer 3: Repulsive field (10m buffer)
buffer_patch = plt.Polygon(
    buffer_coords, closed=True,
    facecolor='#FFCC80', edgecolor='#E65100', linewidth=1.8,
    linestyle='--', alpha=0.45, zorder=2,
    label='Repulsive field (10\u2009m buffer)'
)
ax.add_patch(buffer_patch)

# Layer 2: SSSI No-Fly Zone
sssi_closed = np.vstack([sssi_m, sssi_m[0]])
sssi_patch = plt.Polygon(
    sssi_m, closed=True,
    facecolor='#E53935', edgecolor='#B71C1C', linewidth=2.2,
    alpha=0.35, zorder=3,
    label='SSSI No-Fly Zone (RTL)'
)
ax.add_patch(sssi_patch)
# Hatching for emphasis
sssi_hatch = plt.Polygon(
    sssi_m, closed=True,
    facecolor='none', edgecolor='#B71C1C', linewidth=0.5,
    hatch='///', alpha=0.4, zorder=3
)
ax.add_patch(sssi_hatch)

# Layer 1: Flight Area boundary
flight_closed = np.vstack([flight_m, flight_m[0]])
ax.plot(flight_closed[:, 0], flight_closed[:, 1],
        color='#F9A825', linewidth=2.8, linestyle='-', zorder=4,
        label='Flight Area boundary (hard fence)')

# Search area
search_closed = np.vstack([search_m, search_m[0]])
ax.plot(search_closed[:, 0], search_closed[:, 1],
        color='#2E7D32', linewidth=2.0, linestyle='-', zorder=5,
        label='Survey Area')
search_patch = plt.Polygon(
    search_m, closed=True,
    facecolor='#4CAF50', edgecolor='none', alpha=0.12, zorder=1
)
ax.add_patch(search_patch)

# Take-off location
ax.plot(tol_m[0], tol_m[1], marker='*', markersize=16,
        color='#1565C0', markeredgecolor='black', markeredgewidth=0.8,
        zorder=8, label='Take-off location')

# Drone trajectory
ax.plot(trajectory[:, 0], trajectory[:, 1],
        color='#0D47A1', linewidth=1.6, linestyle='-', zorder=6, alpha=0.85,
        label='Sample search trajectory')
# Drone marker at trajectory start
ax.plot(trajectory[0, 0], trajectory[0, 1], marker='^', markersize=10,
        color='#0D47A1', markeredgecolor='white', markeredgewidth=1.0, zorder=7)
# Small arrows along trajectory
for i in range(0, len(trajectory) - 1, 2):
    mid_x = (trajectory[i, 0] + trajectory[i+1, 0]) / 2
    mid_y = (trajectory[i, 1] + trajectory[i+1, 1]) / 2
    dx = trajectory[i+1, 0] - trajectory[i, 0]
    dy = trajectory[i+1, 1] - trajectory[i, 1]
    norm = np.sqrt(dx**2 + dy**2)
    if norm > 0:
        ax.annotate('', xy=(mid_x + dx/norm*3, mid_y + dy/norm*3),
                     xytext=(mid_x, mid_y),
                     arrowprops=dict(arrowstyle='->', color='#0D47A1',
                                     lw=1.3), zorder=7)

# ── Layer 5: Altitude cap annotation ────────────────────────────
# Add a text box for the altitude cap (can't show vertical on 2D map)
bbox_props = dict(boxstyle='round,pad=0.4', facecolor='#E3F2FD',
                  edgecolor='#1565C0', linewidth=1.2, alpha=0.9)
ax.text(0.98, 0.02,
        'Layer 5: 50\u2009m altitude hard cap\n(enforced on all flight commands)',
        transform=ax.transAxes, fontsize=8.5, fontweight='bold',
        verticalalignment='bottom', horizontalalignment='right',
        bbox=bbox_props, zorder=10, color='#0D47A1')

# ── Annotations ─────────────────────────────────────────────────
# Label the SSSI
sssi_cx = np.mean(sssi_m[:, 0])
sssi_cy = np.mean(sssi_m[:, 1])
ax.text(sssi_cx, sssi_cy, 'SSSI\n(No-Fly)', fontsize=8, fontweight='bold',
        ha='center', va='center', color='#B71C1C', zorder=9, alpha=0.85)

# ── Repulsive force arrows (pointing away from SSSI) ────────────
# Sample a few points on the buffer boundary, draw arrows pointing outward
n_arrows = 6
for i in range(n_arrows):
    idx = int(i * len(buffer_coords) / n_arrows)
    bx, by = buffer_coords[idx]
    # Direction: from SSSI centroid outward
    dx_a = bx - sssi_cx
    dy_a = by - sssi_cy
    norm_a = np.sqrt(dx_a**2 + dy_a**2)
    if norm_a > 0:
        scale = 8
        ax.annotate('', xy=(bx + dx_a/norm_a*scale, by + dy_a/norm_a*scale),
                     xytext=(bx, by),
                     arrowprops=dict(arrowstyle='->', color='#E65100',
                                     lw=1.5, alpha=0.6), zorder=6)

# ── Legend ───────────────────────────────────────────────────────
legend = ax.legend(loc='upper left', fontsize=8, framealpha=0.92,
                   edgecolor='#999', fancybox=True,
                   title='Geofence Layers', title_fontsize=9)

# ── Axes ─────────────────────────────────────────────────────────
ax.set_xlabel('East (m)', fontsize=10)
ax.set_ylabel('North (m)', fontsize=10)
ax.set_title('Five-Layer Geofence Safety System', fontsize=13, fontweight='bold',
             pad=12)
ax.set_aspect('equal')
ax.grid(True, alpha=0.25, linewidth=0.5)
ax.tick_params(labelsize=8.5)

# Add scale bar
xlim = ax.get_xlim()
ylim = ax.get_ylim()
bar_len = 50  # metres
bar_x = xlim[0] + (xlim[1] - xlim[0]) * 0.72
bar_y = ylim[0] + (ylim[1] - ylim[0]) * 0.04
ax.plot([bar_x, bar_x + bar_len], [bar_y, bar_y], 'k-', linewidth=2.5, zorder=10)
ax.text(bar_x + bar_len / 2, bar_y + 3, f'{bar_len}\u2009m',
        ha='center', va='bottom', fontsize=8, fontweight='bold', zorder=10)

# North arrow
arr_x = xlim[0] + (xlim[1] - xlim[0]) * 0.95
arr_y = ylim[0] + (ylim[1] - ylim[0]) * 0.12
ax.annotate('N', xy=(arr_x, arr_y + 18), xytext=(arr_x, arr_y),
            arrowprops=dict(arrowstyle='->', lw=2, color='black'),
            fontsize=11, fontweight='bold', ha='center', va='bottom', zorder=10)

plt.tight_layout()

# ── Save ─────────────────────────────────────────────────────────
out_dir = Path(__file__).parent
fig.savefig(out_dir / 'geofence_layers.pdf', dpi=300, bbox_inches='tight')
fig.savefig(out_dir / 'geofence_layers.png', dpi=300, bbox_inches='tight')
print(f"Saved: {out_dir / 'geofence_layers.pdf'}")
print(f"Saved: {out_dir / 'geofence_layers.png'}")
plt.close(fig)
