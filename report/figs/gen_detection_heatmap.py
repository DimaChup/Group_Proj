"""Chart 13: Detection Heatmap Over Search Area with lawnmower pattern."""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon
from matplotlib.collections import LineCollection
from matplotlib.patches import Circle
import matplotlib.colors as mcolors

np.random.seed(42)

# --- Styling ---
TEXT_DARK = '#2c3e50'
BLUE = '#2980b9'
ORANGE = '#e67e22'
GREEN = '#27ae60'
RED = '#c0392b'
GREY = '#7f8c8d'

plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 10,
    'axes.labelcolor': TEXT_DARK,
    'text.color': TEXT_DARK,
    'axes.edgecolor': '#cccccc',
    'xtick.color': TEXT_DARK,
    'ytick.color': TEXT_DARK,
})

# --- Search area from config.py (converted to local metres from takeoff) ---
# Reference: takeoff at (51.42340640, -2.67144603)
ref_lat = 51.42340640
ref_lon = -2.67144603
lat_m = 111132.954 - 559.822 * np.cos(2 * np.radians(ref_lat))
lon_m = 111132.954 * np.cos(np.radians(ref_lat))

search_gps = [
    (51.42326956502679, -2.670948345438704),
    (51.42287025017865, -2.670045428650557),
    (51.42336622593724, -2.668169295906676),
    (51.42421477437771, -2.668809768621569),
    (51.42354069739116, -2.671277780473196),
]

def gps_to_local(lat, lon):
    """Convert GPS to local east/north metres from takeoff."""
    east = (lon - ref_lon) * lon_m
    north = (lat - ref_lat) * lat_m
    return east, north

poly_xy = np.array([gps_to_local(lat, lon) for lat, lon in search_gps])

# --- Generate lawnmower pattern ---
# Simplified: parallel E-W strips across the polygon
from matplotlib.path import Path as MplPath

poly_path = MplPath(poly_xy)
e_min, n_min = poly_xy.min(axis=0)
e_max, n_max = poly_xy.max(axis=0)

# Camera footprint at 35m altitude, 5.46mm focal length, 5.02mm sensor
alt = 35.0
focal_mm = 5.46
sensor_mm = 5.02
ground_width = alt * sensor_mm / focal_mm  # ~32m
strip_spacing = ground_width * 0.80  # 20% overlap

# Generate scan lines
scan_lines = []
n_current = n_min + strip_spacing / 2
direction = 1  # 1 = left-to-right, -1 = right-to-left

while n_current <= n_max:
    # Find intersections with polygon at this northing
    test_e = np.linspace(e_min - 5, e_max + 5, 500)
    inside = [poly_path.contains_point((e, n_current)) for e in test_e]
    inside_e = test_e[inside]

    if len(inside_e) > 2:
        e_start = inside_e.min() + 2
        e_end = inside_e.max() - 2
        if direction == 1:
            scan_lines.append([(e_start, n_current), (e_end, n_current)])
        else:
            scan_lines.append([(e_end, n_current), (e_start, n_current)])
        direction *= -1

    n_current += strip_spacing

# Build continuous path
path_points = []
for i, line in enumerate(scan_lines):
    path_points.append(line[0])
    path_points.append(line[1])

path_points = np.array(path_points)

# --- Place target ---
target_e, target_n = gps_to_local(51.42350, -2.66950)  # inside search area

# --- Compute detection confidence along path ---
# Confidence depends on distance to target and altitude
def detection_confidence(e, n, target_e, target_n, alt):
    """Simulate detection confidence based on proximity to target."""
    dist = np.sqrt((e - target_e)**2 + (n - target_n)**2)
    # Camera FOV radius at altitude
    fov_radius = ground_width / 2
    if dist > fov_radius * 1.2:
        return 0.0  # target not in frame
    # Confidence decreases with distance from frame center
    conf = 0.95 * np.exp(-0.5 * (dist / (fov_radius * 0.4))**2)
    conf += np.random.normal(0, 0.03)
    return np.clip(conf, 0, 0.99)

# Sample confidence along path at high resolution
n_samples = len(path_points)
conf_values = np.array([detection_confidence(p[0], p[1], target_e, target_n, alt)
                         for p in path_points])

# --- Detection cluster around target ---
n_detections = 12
det_offsets_e = np.random.normal(0, 1.8, n_detections)
det_offsets_n = np.random.normal(0, 1.8, n_detections)
det_e = target_e + det_offsets_e
det_n = target_n + det_offsets_n

# --- Plot ---
fig, ax = plt.subplots(1, 1, figsize=(8, 6.5))

# Search area polygon
poly_patch = MplPolygon(poly_xy, fill=True, facecolor='#eaf2f8', edgecolor=BLUE,
                        linewidth=2, linestyle='-', zorder=1, alpha=0.4,
                        label='Search area')
ax.add_patch(poly_patch)

# Lawnmower path colored by detection confidence
# Create colored line segments
for i in range(0, len(path_points) - 1):
    p1 = path_points[i]
    p2 = path_points[i + 1]
    c1 = conf_values[i]
    c2 = conf_values[i + 1]
    avg_conf = (c1 + c2) / 2

    if avg_conf > 0.3:
        color = plt.cm.RdYlGn(avg_conf)  # Green=high, Red=low
        lw = 2.5
    else:
        color = '#bdc3c7'
        lw = 1.2

    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=color, linewidth=lw,
            solid_capstyle='round', zorder=2)

# Draw thin grey path for full pattern visibility
for i in range(0, len(path_points) - 1):
    p1 = path_points[i]
    p2 = path_points[i + 1]
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color='#d5d8dc', linewidth=0.8,
            zorder=1, solid_capstyle='round')

# Re-draw colored segments on top
for i in range(0, len(path_points) - 1):
    p1 = path_points[i]
    p2 = path_points[i + 1]
    c1 = conf_values[i]
    c2 = conf_values[i + 1]
    avg_conf = (c1 + c2) / 2

    if avg_conf > 0.15:
        color = plt.cm.RdYlGn(min(avg_conf * 1.2, 1.0))
        lw = 2.5
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=color, linewidth=lw,
                solid_capstyle='round', zorder=3)

# Camera FOV circle at target
fov_circle = Circle((target_e, target_n), ground_width / 2, fill=False,
                     linestyle=':', linewidth=1.0, edgecolor=GREY, zorder=2)
ax.add_patch(fov_circle)
ax.text(target_e + ground_width / 2 + 1, target_n, 'Camera FOV\nat 35 m',
        fontsize=7.5, color=GREY, va='center')

# Detection cluster
ax.scatter(det_e, det_n, c='#e74c3c', s=30, alpha=0.7, edgecolors='white',
           linewidths=0.5, zorder=5, label='Detection estimates')

# Centroid of detections
cent_e, cent_n = np.mean(det_e), np.mean(det_n)
ax.plot(cent_e, cent_n, '*', color=RED, markersize=14, zorder=6,
        label='Estimated position')

# True target
ax.plot(target_e, target_n, '+', color=GREEN, markersize=16, markeredgewidth=3,
        zorder=6, label='True target')

# CEP50 circle around cluster
det_dists = np.sqrt((det_e - target_e)**2 + (det_n - target_n)**2)
cep50 = np.percentile(det_dists, 50)
cep_circle = Circle((target_e, target_n), cep50, fill=False, linestyle='-',
                     linewidth=1.5, edgecolor=ORANGE, zorder=4)
ax.add_patch(cep_circle)
ax.text(target_e + cep50 + 0.5, target_n - 1, f'CEP50\n{cep50:.1f} m',
        fontsize=8, color=ORANGE, fontweight='bold')

# Takeoff marker
to_e, to_n = gps_to_local(ref_lat, ref_lon)
ax.plot(to_e, to_n, 's', color=TEXT_DARK, markersize=8, zorder=5)
ax.text(to_e + 3, to_n, 'Take-off', fontsize=8, color=TEXT_DARK, va='center')

# Start/end arrows
ax.annotate('Start', xy=path_points[0], fontsize=8, color=BLUE, fontweight='bold',
            ha='right', va='bottom',
            xytext=(path_points[0][0] - 8, path_points[0][1] + 5),
            arrowprops=dict(arrowstyle='->', color=BLUE, lw=1.2))

# Colorbar for confidence
sm = plt.cm.ScalarMappable(cmap='RdYlGn', norm=mcolors.Normalize(0, 1))
sm.set_array([])
cbar = plt.colorbar(sm, ax=ax, shrink=0.6, aspect=20, pad=0.02)
cbar.set_label('Detection Confidence', fontsize=10)
cbar.set_ticks([0, 0.25, 0.5, 0.75, 1.0])

# --- Formatting ---
margin = 15
ax.set_xlim(e_min - margin, e_max + margin)
ax.set_ylim(n_min - margin, n_max + margin)
ax.set_aspect('equal')
ax.set_xlabel('East (m from take-off)', fontsize=11)
ax.set_ylabel('North (m from take-off)', fontsize=11)
ax.set_title('Detection Heatmap Over Search Area', fontsize=13,
             fontweight='bold', color=TEXT_DARK, pad=12)

ax.legend(loc='upper left', fontsize=8.5, framealpha=0.9, edgecolor='#cccccc')
ax.grid(True, alpha=0.15, zorder=0)

plt.tight_layout()
plt.savefig('detection_heatmap.pdf', bbox_inches='tight', dpi=300)
plt.savefig('detection_heatmap.png', bbox_inches='tight', dpi=200)
print('Saved detection_heatmap.pdf')
