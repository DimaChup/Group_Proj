"""Charts: Search path planning optimisation for SAR drone report.

Generates:
  energy_efficiency.pdf       — Pareto frontier: mission time vs energy consumption
  nfz_margin_altitude.pdf     — NFZ safety margin vs altitude
  rotation_comparison.pdf     — 3-panel scan angle comparison (0, 70, 45 degrees)
  speed_detection_energy.pdf  — 3-axis speed/detection/energy tradeoff
"""
import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D

# --- Styling (matches project charts) ---
TEXT_DARK = '#2c3e50'
BLUE = '#2980b9'
ORANGE = '#e67e22'
GREEN = '#27ae60'
RED = '#c0392b'
GREY = '#7f8c8d'
PURPLE = '#8e44ad'
TEAL = '#16a085'

plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 10,
    'axes.labelcolor': TEXT_DARK,
    'text.color': TEXT_DARK,
    'axes.edgecolor': '#cccccc',
    'xtick.color': TEXT_DARK,
    'ytick.color': TEXT_DARK,
})

# --- Sensor & mission parameters (from config.py) ---
SENSOR_WIDTH_MM = 5.02
FOCAL_LENGTH_MM = 5.46
IMAGE_W = 1456
IMAGE_H = 1088

# Search area approximate dimensions (from GPS polygon)
# Polygon bounding box ~ 290m x 130m, area ~ 28,000 m^2
SEARCH_AREA_M2 = 28000.0
POLY_LENGTH_M = 290.0   # longest axis
POLY_WIDTH_M = 130.0     # perpendicular extent

# Drone power model (typical small SAR quadcopter)
HOVER_POWER_W = 180.0       # watts in hover
SPEED_POWER_COEFF = 1.8     # additional W per (m/s)^2 (parasitic drag)
TURN_ENERGY_J = 15.0        # energy per U-turn (decel + accel)

# NFZ parameters (from config.py)
NFZ_WAYPOINT_BUFFER_M = 30.0
NFZ_SLOW_ZONE_M = 20.0


def footprint_width(alt):
    """Camera ground footprint width in metres."""
    return (SENSOR_WIDTH_MM * alt) / FOCAL_LENGTH_MM


def footprint_height(alt):
    """Camera ground footprint height in metres."""
    aspect = IMAGE_H / IMAGE_W
    return footprint_width(alt) * aspect


def swath_width(alt, overlap=0.2):
    """Effective scan strip spacing after overlap."""
    return footprint_width(alt) * (1.0 - overlap)


def num_strips(alt, poly_width=POLY_WIDTH_M, overlap=0.2):
    """Number of parallel scan strips needed."""
    sw = swath_width(alt, overlap)
    return max(1, math.ceil(poly_width / sw))


def path_length(alt, poly_length=POLY_LENGTH_M, poly_width=POLY_WIDTH_M, overlap=0.2):
    """Total path length (scan lines + turns)."""
    n = num_strips(alt, poly_width, overlap)
    scan_dist = n * poly_length
    turn_dist = (n - 1) * swath_width(alt, overlap)  # lateral transition
    return scan_dist + turn_dist


def mission_time(alt, speed, poly_length=POLY_LENGTH_M, poly_width=POLY_WIDTH_M):
    """Mission time in seconds."""
    dist = path_length(alt, poly_length, poly_width)
    n = num_strips(alt, poly_width)
    turn_time = (n - 1) * 3.0  # ~3s per U-turn (decel + rotate + accel)
    return dist / speed + turn_time


def energy_consumption(alt, speed, poly_length=POLY_LENGTH_M, poly_width=POLY_WIDTH_M):
    """Energy in Wh."""
    t = mission_time(alt, speed, poly_length, poly_width)
    power = HOVER_POWER_W + SPEED_POWER_COEFF * speed**2
    n = num_strips(alt, poly_width)
    turn_energy = (n - 1) * TURN_ENERGY_J
    return (power * t + turn_energy) / 3600.0


def coverage_pct(alt, overlap=0.2):
    """Coverage percentage (100% if swath covers width, degrades at very high alt
    where fewer strips may leave gaps at polygon edges)."""
    sw = swath_width(alt, overlap)
    n = num_strips(alt, POLY_WIDTH_M, overlap)
    covered = n * sw
    return min(100.0, (covered / POLY_WIDTH_M) * 100.0)


def detection_prob(speed, alt=35.0):
    """Detection probability per flyover pass (models blur + dwell time).
    At low speed: high prob. At high speed: target crosses FOV too fast + blur."""
    # Dwell time: how long target is in FOV
    fw = footprint_width(alt)
    dwell = fw / np.maximum(speed, 0.1)  # seconds target in view

    # Frames available (4.8 FPS on Pi)
    fps = 4.8
    frames = dwell * fps

    # Detection per frame (blur-dependent)
    t_exp = 1/100  # rolling shutter worst case
    pm = speed * t_exp * FOCAL_LENGTH_MM * IMAGE_W / (SENSOR_WIDTH_MM * alt)
    blur_factor = np.exp(-0.012 * np.maximum(pm - 1.0, 0)**2)
    per_frame = 0.95 * blur_factor

    # P(detect in N frames) = 1 - (1 - p)^N
    p_detect = 1.0 - (1.0 - per_frame)**np.maximum(frames, 1)
    return p_detect * 100.0


# =========================================================================
# Chart 1: Energy efficiency Pareto frontier
# =========================================================================
altitudes_range = np.arange(20, 51, 5)
speeds_range = np.arange(5, 16, 1)

configs = []
for alt in altitudes_range:
    for spd in speeds_range:
        t = mission_time(alt, spd)
        e = energy_consumption(alt, spd)
        c = coverage_pct(alt)
        configs.append((alt, spd, t, e, c))

configs = np.array(configs)
times = configs[:, 2]
energies = configs[:, 3]
coverages = configs[:, 4]

# Pareto frontier (non-dominated in time AND energy)
pareto_mask = np.zeros(len(configs), dtype=bool)
for i in range(len(configs)):
    dominated = False
    for j in range(len(configs)):
        if i != j and times[j] <= times[i] and energies[j] <= energies[i]:
            if times[j] < times[i] or energies[j] < energies[i]:
                dominated = True
                break
    if not dominated:
        pareto_mask[i] = True

pareto_pts = configs[pareto_mask]
pareto_sorted = pareto_pts[np.argsort(pareto_pts[:, 2])]  # sort by time

fig1, ax1 = plt.subplots(figsize=(8, 5.5))

# Color by coverage
norm = plt.Normalize(vmin=88, vmax=100)
cmap = plt.cm.RdYlGn

sc = ax1.scatter(times, energies, c=coverages, cmap=cmap, norm=norm,
                 s=50, alpha=0.7, edgecolors='white', linewidth=0.5, zorder=3)

# Pareto frontier line
ax1.plot(pareto_sorted[:, 2], pareto_sorted[:, 3], color=TEXT_DARK,
         linewidth=1.5, linestyle='--', alpha=0.6, zorder=4, label='Pareto frontier')

# Highlight selected configuration (35m, 8m/s)
sel_t = mission_time(35, 8)
sel_e = energy_consumption(35, 8)
ax1.scatter([sel_t], [sel_e], marker='*', s=300, color=ORANGE, edgecolors=TEXT_DARK,
            linewidth=1.2, zorder=6, label='Selected (35 m, 8 m/s)')

# Label key points
# Fastest
fastest_idx = np.argmin(times)
ax1.annotate('Fastest\n(50 m, 15 m/s)',
             xy=(times[fastest_idx], energies[fastest_idx]),
             xytext=(times[fastest_idx] + 15, energies[fastest_idx] + 0.3),
             fontsize=8, color=RED, fontweight='bold',
             arrowprops=dict(arrowstyle='->', color=RED, lw=1), ha='left')

# Most efficient
efficient_idx = np.argmin(energies)
ax1.annotate('Most efficient\n(50 m, 5 m/s)',
             xy=(times[efficient_idx], energies[efficient_idx]),
             xytext=(times[efficient_idx] - 15, energies[efficient_idx] - 0.3),
             fontsize=8, color=GREEN, fontweight='bold',
             arrowprops=dict(arrowstyle='->', color=GREEN, lw=1), ha='right')

# Selected
ax1.annotate('Selected\n(balanced)',
             xy=(sel_t, sel_e),
             xytext=(sel_t + 25, sel_e + 0.4),
             fontsize=9, color=ORANGE, fontweight='bold',
             arrowprops=dict(arrowstyle='->', color=ORANGE, lw=1.2), ha='left')

cbar = plt.colorbar(sc, ax=ax1, shrink=0.8, pad=0.02)
cbar.set_label('Coverage (%)', fontsize=10)

ax1.set_xlabel('Mission Time (s)', fontsize=11)
ax1.set_ylabel('Energy Consumption (Wh)', fontsize=11)
ax1.set_title('Search Configuration: Mission Time vs Energy Consumption',
              fontsize=12, fontweight='bold', color=TEXT_DARK, pad=10)
ax1.legend(loc='upper left', fontsize=9, framealpha=0.9, edgecolor='#cccccc')
ax1.grid(True, alpha=0.15, zorder=0)

plt.tight_layout()
plt.savefig('energy_efficiency.pdf', bbox_inches='tight', dpi=300)
plt.savefig('energy_efficiency.png', bbox_inches='tight', dpi=200)
print('Saved energy_efficiency.pdf + .png')
plt.close()


# =========================================================================
# Chart 2: NFZ safety margin vs altitude
# =========================================================================
alts_nfz = np.linspace(10, 50, 200)
footprint_radius = footprint_width(alts_nfz) / 2.0

buffer_total = NFZ_WAYPOINT_BUFFER_M + NFZ_SLOW_ZONE_M  # 30 + 20 = 50m
margin = buffer_total - footprint_radius

fig2, ax2 = plt.subplots(figsize=(8, 5))

# Camera footprint radius
ax2.plot(alts_nfz, footprint_radius, color=BLUE, linewidth=2.2,
         label='Camera footprint radius', zorder=3)

# Buffer line
ax2.axhline(y=buffer_total, color=GREEN, linewidth=2, linestyle='--',
            label=f'Total buffer ({NFZ_WAYPOINT_BUFFER_M:.0f}m waypoint + {NFZ_SLOW_ZONE_M:.0f}m speed ramp)',
            zorder=3)

# Margin
ax2.plot(alts_nfz, margin, color=ORANGE, linewidth=2, linestyle='-.',
         label='Safety margin (buffer - footprint radius)', zorder=3)

# Shade safe vs unsafe
ax2.fill_between(alts_nfz, footprint_radius, buffer_total,
                 where=margin > 0, alpha=0.12, color=GREEN, zorder=1,
                 label='Safe zone')
ax2.fill_between(alts_nfz, footprint_radius, buffer_total,
                 where=margin <= 0, alpha=0.12, color=RED, zorder=1,
                 label='Footprint enters SSSI')

# Operating point at 35m
fp_at_35 = footprint_width(35) / 2.0
margin_at_35 = buffer_total - fp_at_35
ax2.scatter([35], [fp_at_35], marker='o', s=100, color=ORANGE,
            edgecolors=TEXT_DARK, linewidth=1.5, zorder=5)
ax2.annotate(f'Operating point\n(35 m, margin = {margin_at_35:.1f} m)',
             xy=(35, fp_at_35), xytext=(38, fp_at_35 + 8),
             fontsize=9, color=ORANGE, fontweight='bold',
             arrowprops=dict(arrowstyle='->', color=ORANGE, lw=1.2),
             ha='left')

# Critical altitude where margin = 0
if np.any(margin <= 0):
    crit_alt = alts_nfz[np.argmin(np.abs(margin))]
    ax2.axvline(x=crit_alt, color=RED, linewidth=1, linestyle=':', alpha=0.6)
    ax2.text(crit_alt + 0.5, 5, f'Critical: {crit_alt:.0f} m',
             fontsize=8, color=RED, rotation=90, va='bottom')

# Waypoint buffer component
ax2.axhline(y=NFZ_WAYPOINT_BUFFER_M, color=GREY, linewidth=1, linestyle=':',
            alpha=0.5)
ax2.text(11, NFZ_WAYPOINT_BUFFER_M + 0.8, f'Waypoint buffer ({NFZ_WAYPOINT_BUFFER_M:.0f} m)',
         fontsize=8, color=GREY, fontstyle='italic')

ax2.set_xlabel('Altitude (m)', fontsize=11)
ax2.set_ylabel('Distance from NFZ Boundary (m)', fontsize=11)
ax2.set_title('NFZ Safety Margin vs Altitude',
              fontsize=12, fontweight='bold', color=TEXT_DARK, pad=10)
ax2.set_xlim(10, 50)
ax2.set_ylim(0, 60)
ax2.legend(loc='upper left', fontsize=8.5, framealpha=0.9, edgecolor='#cccccc')
ax2.grid(True, alpha=0.15, zorder=0)

plt.tight_layout()
plt.savefig('nfz_margin_altitude.pdf', bbox_inches='tight', dpi=300)
plt.savefig('nfz_margin_altitude.png', bbox_inches='tight', dpi=200)
print('Saved nfz_margin_altitude.pdf + .png')
plt.close()


# =========================================================================
# Chart 3: Rotation comparison (3-panel)
# =========================================================================
# Search area polygon (from config.py GPS coords, converted to local metres)
# Use GPS → local offset from centroid
SEARCH_GPS = [
    (51.42326956502679, -2.670948345438704),
    (51.42287025017865, -2.670045428650557),
    (51.42336622593724, -2.668169295906676),
    (51.42421477437771, -2.668809768621569),
    (51.42354069739116, -2.671277780473196),
]

# SSSI polygon (for NFZ display)
SSSI_GPS = [
    (51.42353586816967, -2.671451754138619),
    (51.42215640321154, -2.669768242108598),
    (51.42267105383615, -2.667705438815299),
    (51.42335592245168, -2.668164601092489),
    (51.42286082606338, -2.670043418345824),
    (51.42326667015552, -2.670965419051837),
    (51.42356862274763, -2.671324297543731),
]

# Convert GPS to local metres (relative to centroid)
def gps_to_local(gps_pts):
    """Convert GPS coords to local x,y in metres (origin = centroid)."""
    lats = [p[0] for p in gps_pts]
    lons = [p[1] for p in gps_pts]
    clat = np.mean(lats)
    clon = np.mean(lons)
    m_per_deg_lat = 111320.0
    m_per_deg_lon = 111320.0 * math.cos(math.radians(clat))
    xy = []
    for lat, lon in gps_pts:
        x = (lon - clon) * m_per_deg_lon
        y = (lat - clat) * m_per_deg_lat
        xy.append((x, y))
    return np.array(xy), clat, clon


search_xy, clat, clon = gps_to_local(SEARCH_GPS)

# Also convert SSSI to same coordinate frame
m_per_deg_lat = 111320.0
m_per_deg_lon_val = 111320.0 * math.cos(math.radians(clat))
sssi_xy = np.array([
    ((lon - clon) * m_per_deg_lon_val, (lat - clat) * m_per_deg_lat)
    for lat, lon in SSSI_GPS
])


def generate_lawnmower(polygon_xy, angle_deg, alt=35.0, overlap=0.2):
    """Generate lawnmower waypoints for a polygon at given scan angle."""
    # Rotate polygon to align scan direction with x-axis
    theta = math.radians(-angle_deg)
    cos_t, sin_t = math.cos(theta), math.sin(theta)

    rotated = np.array([(x*cos_t - y*sin_t, x*sin_t + y*cos_t) for x, y in polygon_xy])

    # Bounding box in rotated frame
    x_min, y_min = rotated.min(axis=0)
    x_max, y_max = rotated.max(axis=0)

    # Strip spacing
    sw = swath_width(alt, overlap)

    # Generate scan lines
    strips = []
    y = y_min + sw/3
    while y < y_max - sw/3:
        # Find intersection of scan line with polygon edges
        intersections = []
        n = len(rotated)
        for i in range(n):
            p1 = rotated[i]
            p2 = rotated[(i+1) % n]
            if (p1[1] <= y <= p2[1]) or (p2[1] <= y <= p1[1]):
                if abs(p2[1] - p1[1]) > 1e-10:
                    t = (y - p1[1]) / (p2[1] - p1[1])
                    x_int = p1[0] + t * (p2[0] - p1[0])
                    intersections.append(x_int)
        if len(intersections) >= 2:
            intersections.sort()
            strips.append((intersections[0], y, intersections[-1], y))
        y += sw

    # Zigzag connection and un-rotate
    waypoints = []
    for i, (x1, y1, x2, y2) in enumerate(strips):
        if i % 2 == 0:
            pts = [(x1, y1), (x2, y2)]
        else:
            pts = [(x2, y2), (x1, y1)]
        for rx, ry in pts:
            # Inverse rotate
            ox = rx*cos_t + ry*sin_t
            oy = -rx*sin_t + ry*cos_t
            waypoints.append((ox, oy))

    return waypoints, len(strips)


def path_total_length(waypoints):
    """Total path length from waypoint list."""
    total = 0
    for i in range(1, len(waypoints)):
        dx = waypoints[i][0] - waypoints[i-1][0]
        dy = waypoints[i][1] - waypoints[i-1][1]
        total += math.sqrt(dx*dx + dy*dy)
    return total


angles = [0, 20, 90]
titles = [
    r'$0\degree$ (N--S)',
    r'$20\degree$ (longest edge)',
    r'$90\degree$ (E--W)',
]

fig3, axes3 = plt.subplots(1, 3, figsize=(14, 5))

for idx, (angle, title) in enumerate(zip(angles, titles)):
    ax = axes3[idx]
    wps, n_strips = generate_lawnmower(search_xy, angle)
    total_len = path_total_length(wps)
    n_turns = max(0, n_strips - 1)

    # Draw search polygon
    poly_closed = np.vstack([search_xy, search_xy[0:1]])
    ax.fill(poly_closed[:, 0], poly_closed[:, 1], alpha=0.08, color=BLUE)
    ax.plot(poly_closed[:, 0], poly_closed[:, 1], color=BLUE, linewidth=1.5,
            zorder=3)

    # Draw SSSI polygon
    sssi_closed = np.vstack([sssi_xy, sssi_xy[0:1]])
    ax.fill(sssi_closed[:, 0], sssi_closed[:, 1], alpha=0.15, color=RED)
    ax.plot(sssi_closed[:, 0], sssi_closed[:, 1], color=RED, linewidth=1.2,
            linestyle='--', zorder=3, alpha=0.7)

    # Draw path
    if len(wps) >= 2:
        wpx = [w[0] for w in wps]
        wpy = [w[1] for w in wps]
        ax.plot(wpx, wpy, color=ORANGE, linewidth=1.2, alpha=0.85, zorder=4)

        # Start/end markers
        ax.scatter([wpx[0]], [wpy[0]], marker='^', s=80, color=GREEN,
                   edgecolors=TEXT_DARK, linewidth=1, zorder=5, label='Start')
        ax.scatter([wpx[-1]], [wpy[-1]], marker='s', s=60, color=RED,
                   edgecolors=TEXT_DARK, linewidth=1, zorder=5, label='End')

    # Annotations
    info_text = f'{n_turns} turns\n{total_len:.0f} m path'
    ax.text(0.97, 0.03, info_text, transform=ax.transAxes,
            fontsize=10, fontweight='bold', color=TEXT_DARK,
            ha='right', va='bottom',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                      edgecolor='#cccccc', alpha=0.9))

    # Highlight if this is the selected one
    if angle == 20:
        ax.set_title(title + ' [selected]', fontsize=11, fontweight='bold',
                     color=ORANGE, pad=8)
        for spine in ax.spines.values():
            spine.set_edgecolor(ORANGE)
            spine.set_linewidth(2)
    else:
        ax.set_title(title, fontsize=11, fontweight='bold', color=TEXT_DARK, pad=8)

    ax.set_aspect('equal')
    ax.grid(True, alpha=0.15, zorder=0)
    ax.set_xlabel('East (m)', fontsize=10)
    if idx == 0:
        ax.set_ylabel('North (m)', fontsize=10)

# Shared legend
handles = [
    mpatches.Patch(facecolor=BLUE, alpha=0.15, edgecolor=BLUE, label='Search area'),
    mpatches.Patch(facecolor=RED, alpha=0.15, edgecolor=RED, label='SSSI (NFZ)'),
    Line2D([0], [0], color=ORANGE, linewidth=1.5, label='Flight path'),
    Line2D([0], [0], marker='^', color='w', markerfacecolor=GREEN,
           markersize=8, label='Start'),
    Line2D([0], [0], marker='s', color='w', markerfacecolor=RED,
           markersize=7, label='End'),
]
fig3.legend(handles=handles, loc='lower center', ncol=5, fontsize=9,
            framealpha=0.9, edgecolor='#cccccc', bbox_to_anchor=(0.5, -0.02))

fig3.suptitle('Scan Angle Comparison: Impact on Path Length and Turn Count',
              fontsize=13, fontweight='bold', color=TEXT_DARK, y=1.01)

plt.tight_layout()
plt.savefig('rotation_comparison.pdf', bbox_inches='tight', dpi=300)
plt.savefig('rotation_comparison.png', bbox_inches='tight', dpi=200)
print('Saved rotation_comparison.pdf + .png')
plt.close()


# =========================================================================
# Chart 4: Speed vs detection probability vs energy per area
# =========================================================================
speeds_sweep = np.linspace(3, 15, 200)

det_prob = detection_prob(speeds_sweep, alt=35.0)

# Energy per unit area (Wh/m^2) — energy for full mission / search area
energy_per_area = np.array([
    energy_consumption(35, s) / SEARCH_AREA_M2 * 1e4  # scale to Wh per hectare
    for s in speeds_sweep
])

fig4, ax4a = plt.subplots(figsize=(8, 5.5))

# Left axis: detection probability
color_det = BLUE
ax4a.plot(speeds_sweep, det_prob, color=color_det, linewidth=2.2,
          label='Detection probability', zorder=3)
ax4a.set_xlabel('Ground Speed (m/s)', fontsize=11)
ax4a.set_ylabel('Detection Probability per Flyover (%)', fontsize=11,
                color=color_det)
ax4a.tick_params(axis='y', labelcolor=color_det)
ax4a.set_ylim(50, 102)

# Right axis: energy per area
ax4b = ax4a.twinx()
color_eng = RED
ax4b.plot(speeds_sweep, energy_per_area, color=color_eng, linewidth=2.2,
          linestyle='--', label='Energy per hectare', zorder=3)
ax4b.set_ylabel('Energy per Hectare (Wh/ha)', fontsize=11, color=color_eng)
ax4b.tick_params(axis='y', labelcolor=color_eng)

# Altitude-dependent speed range (6-10 m/s at 20-50m)
ax4a.axvspan(6, 10, alpha=0.10, color=GREEN, zorder=1)
ax4a.text(8, 53, 'Altitude-dependent\nspeed range\n(6\u201310 m/s)',
          fontsize=9, color=GREEN, ha='center', va='bottom',
          fontweight='bold', alpha=0.8)

# Sweet spot marker
sweet_speed = 8.0
sweet_det = detection_prob(sweet_speed, 35.0)
sweet_eng = energy_consumption(35, sweet_speed) / SEARCH_AREA_M2 * 1e4
ax4a.scatter([sweet_speed], [sweet_det], marker='*', s=250, color=ORANGE,
             edgecolors=TEXT_DARK, linewidth=1.2, zorder=6)
ax4a.annotate(f'Operating point\n({sweet_speed:.0f} m/s, {sweet_det:.0f}%)',
              xy=(sweet_speed, sweet_det),
              xytext=(sweet_speed + 2.5, sweet_det - 8),
              fontsize=9, color=ORANGE, fontweight='bold',
              arrowprops=dict(arrowstyle='->', color=ORANGE, lw=1.2),
              ha='left')

# Threshold lines
ax4a.axhline(y=90, color=GREY, linewidth=1, linestyle=':', alpha=0.5)
ax4a.text(14.5, 90.5, '90% threshold', fontsize=8, color=GREY,
          ha='right', fontstyle='italic')

# Combined legend
lines_a, labels_a = ax4a.get_legend_handles_labels()
lines_b, labels_b = ax4b.get_legend_handles_labels()
ax4a.legend(lines_a + lines_b, labels_a + labels_b,
            loc='upper right', fontsize=9, framealpha=0.9, edgecolor='#cccccc')

ax4a.set_title('Speed--Detection--Energy Tradeoff at 35 m Altitude',
               fontsize=12, fontweight='bold', color=TEXT_DARK, pad=10)
ax4a.set_xlim(3, 15)
ax4a.grid(True, alpha=0.15, zorder=0)

plt.tight_layout()
plt.savefig('speed_detection_energy.pdf', bbox_inches='tight', dpi=300)
plt.savefig('speed_detection_energy.png', bbox_inches='tight', dpi=200)
print('Saved speed_detection_energy.pdf + .png')
plt.close()

print('\nAll 4 path planning charts generated.')
