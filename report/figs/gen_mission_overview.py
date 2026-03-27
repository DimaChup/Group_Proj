"""Generate mission overview figure showing flight plan on Fenswood Wilderness."""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
from shapely.geometry import Polygon, LineString, Point
import math

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

FOCUS_AREA_GPS = [
    (51.42330493862503, -2.669823704225677),
    (51.42344370699984, -2.669496195078445),
    (51.42352782091507, -2.669800245046278),
    (51.42334972740506, -2.67001828046102),
]

# ── Config values ───────────────────────────────────────────────────
TARGET_ALT = 35.0
SENSOR_WIDTH_MM = 5.02
FOCAL_LENGTH_MM = 5.46


# ── GPS to local metres (East, North) from TOL ─────────────────────
def gps_to_en(lat, lon, ref_lat=TAKEOFF_GPS[0], ref_lon=TAKEOFF_GPS[1]):
    R = 6371000.0
    north = math.radians(lat - ref_lat) * R
    east = math.radians(lon - ref_lon) * R * math.cos(math.radians(ref_lat))
    return east, north


def poly_to_en(coords):
    return np.array([gps_to_en(c[0], c[1]) for c in coords])


# ── Generate lawnmower pattern properly ─────────────────────────────
def generate_lawnmower(search_en, alt=TARGET_ALT):
    """Lawnmower pattern aligned to longest edge of search polygon."""
    ground_w = (SENSOR_WIDTH_MM * alt) / FOCAL_LENGTH_MM
    overlap = 0.2
    swath = ground_w * (1.0 - overlap)

    # Find longest edge
    n = len(search_en)
    best_len, best_angle = 0, 0
    for i in range(n):
        j = (i + 1) % n
        dx = search_en[j][0] - search_en[i][0]
        dy = search_en[j][1] - search_en[i][1]
        edge_len = math.hypot(dx, dy)
        if edge_len > best_len:
            best_len = edge_len
            best_angle = math.atan2(dy, dx)

    # Rotate polygon so longest edge is horizontal
    cos_a, sin_a = math.cos(-best_angle), math.sin(-best_angle)
    rotated = np.array([(e*cos_a - n_*sin_a, e*sin_a + n_*cos_a)
                        for e, n_ in search_en])
    poly_rot = Polygon(rotated)

    min_n, max_n = rotated[:, 1].min(), rotated[:, 1].max()
    min_e, max_e = rotated[:, 0].min(), rotated[:, 0].max()

    # Generate scan lines with small inset
    inset = swath * 0.15
    scan_ys = []
    y = min_n + inset
    while y < max_n - inset + 0.1:
        scan_ys.append(y)
        y += swath

    strips = []
    for sy in scan_ys:
        line = LineString([(min_e - 10, sy), (max_e + 10, sy)])
        inter = poly_rot.intersection(line)
        if inter.is_empty:
            continue
        geoms = [inter] if inter.geom_type == 'LineString' else list(inter.geoms)
        for seg in geoms:
            if seg.geom_type != 'LineString':
                continue
            coords = list(seg.coords)
            if len(coords) >= 2:
                strips.append((coords[0][0] + inset, sy,
                               coords[-1][0] - inset, sy))

    # Un-rotate
    cos_b, sin_b = math.cos(best_angle), math.sin(best_angle)

    def unrot(re, rn):
        return re*cos_b - rn*sin_b, re*sin_b + rn*cos_b

    waypoints = []
    direction = 1
    for x1, y1, x2, y2 in strips:
        if direction == 1:
            s, e = (x1, y1), (x2, y2)
        else:
            s, e = (x2, y2), (x1, y1)
        waypoints.append(unrot(*s))
        waypoints.append(unrot(*e))
        direction *= -1

    return waypoints


# ── Convert all polygons ────────────────────────────────────────────
search_en = poly_to_en(SEARCH_AREA_GPS)
flight_en = poly_to_en(FLIGHT_AREA_GPS)
sssi_en = poly_to_en(SSSI_GPS)
focus_en = poly_to_en(FOCUS_AREA_GPS)

# Generate lawnmower
lawn_wps = generate_lawnmower(search_en)

# Place target inside search area, well away from edges and SSSI
search_poly = Polygon(search_en)
cx, cy = search_poly.centroid.x, search_poly.centroid.y
# Shift toward the north-east part of the search area (away from SSSI)
target_en = np.array([cx + 50, cy + 30])
if not search_poly.contains(Point(target_en)):
    target_en = np.array([cx + 30, cy + 20])
if not search_poly.contains(Point(target_en)):
    target_en = np.array([cx, cy])

# Detection cluster (GPS estimates with noise)
np.random.seed(42)
cluster = target_en + np.random.randn(12, 2) * 2.5

# Offset landing point (7.5m east of target — perpendicular to avoid overlap)
landing_en = target_en + np.array([7.5, 0.0])


# ── Plot ────────────────────────────────────────────────────────────
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
    'font.size': 9,
})

fig, ax = plt.subplots(1, 1, figsize=(7.5, 6.5), dpi=200)

# Set axis limits first
all_e = np.concatenate([flight_en[:, 0], search_en[:, 0], sssi_en[:, 0], [0]])
all_n = np.concatenate([flight_en[:, 1], search_en[:, 1], sssi_en[:, 1], [0]])
margin = 35
ax.set_xlim(all_e.min() - margin, all_e.max() + margin)
ax.set_ylim(all_n.min() - margin, all_n.max() + margin)

# 1. Flight Area boundary — blue dashed
flight_closed = np.vstack([flight_en, flight_en[0]])
ax.plot(flight_closed[:, 0], flight_closed[:, 1], color='#2266bb',
        linestyle='--', linewidth=1.3, zorder=2)

# 2. SSSI No-Fly Zone — red hatched
sssi_patch = plt.Polygon(sssi_en, closed=True, facecolor='#ff000015',
                         edgecolor='#cc0000', linewidth=1.4, linestyle='-',
                         hatch='////', zorder=3)
ax.add_patch(sssi_patch)

# 3. Search Area — green fill
search_patch = plt.Polygon(search_en, closed=True, facecolor='#22aa2218',
                           edgecolor='#117711', linewidth=1.6, linestyle='-',
                           zorder=4)
ax.add_patch(search_patch)

# 4. Focus Area — orange dashed
focus_patch = plt.Polygon(focus_en, closed=True, facecolor='#ff880025',
                          edgecolor='#cc6600', linewidth=1.2, linestyle='--',
                          zorder=4)
ax.add_patch(focus_patch)

# 5. Lawnmower search path
if lawn_wps:
    lx = [p[0] for p in lawn_wps]
    ly = [p[1] for p in lawn_wps]
    ax.plot(lx, ly, '-', color='#4477cc', linewidth=0.65, alpha=0.75, zorder=5)

    # Direction arrows on every scan line (midpoint of each strip)
    for i in range(0, len(lawn_wps) - 1, 2):
        x1, y1 = lawn_wps[i]
        x2, y2 = lawn_wps[i + 1]
        dx, dy = x2 - x1, y2 - y1
        length = math.hypot(dx, dy)
        if length > 8:
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            ax.annotate('', xy=(mx + dx*0.08, my + dy*0.08),
                       xytext=(mx - dx*0.08, my - dy*0.08),
                       arrowprops=dict(arrowstyle='->', color='#4477cc',
                                       lw=0.7, mutation_scale=8), zorder=5)

# 6. Transit: TOL to first waypoint (dotted)
if lawn_wps:
    ax.plot([0, lawn_wps[0][0]], [0, lawn_wps[0][1]], ':',
            color='#4477cc', linewidth=0.9, alpha=0.5, zorder=5)

# 7. Take-Off Location
ax.plot(0, 0, '*', color='#eeaa00', markersize=16, markeredgecolor='black',
        markeredgewidth=0.7, zorder=11)
ax.annotate('TOL', xy=(0, 0), xytext=(6, 6), fontsize=8.5, fontweight='bold',
           color='#775500', zorder=11)

# 8. Target
ax.plot(target_en[0], target_en[1], 'X', color='#cc0000', markersize=11,
        markeredgewidth=2.5, zorder=10)

# 9. Detection cluster
ax.scatter(cluster[:, 0], cluster[:, 1], c='#ff8800', s=18, alpha=0.75,
           edgecolors='#cc5500', linewidth=0.5, zorder=9)

# 10. Offset landing point
ax.plot(landing_en[0], landing_en[1], 'D', color='#22bb44', markersize=9,
        markeredgecolor='black', markeredgewidth=0.7, zorder=10)
# Label with arrow — place below and to the right
ax.annotate('Landing\n(7.5 m offset)', xy=(landing_en[0], landing_en[1]),
           xytext=(landing_en[0] + 18, landing_en[1] - 20),
           fontsize=7, color='#116622', fontweight='bold',
           arrowprops=dict(arrowstyle='->', color='#116622', lw=0.7,
                          connectionstyle='arc3,rad=-0.2'),
           zorder=11)

# 10b. Line connecting target to landing (7.5m offset visualization)
ax.plot([target_en[0], landing_en[0]], [target_en[1], landing_en[1]],
        '-', color='#22bb44', linewidth=1.0, alpha=0.6, zorder=9)
# Small "7.5 m" label on the connecting line
mid_tl = (target_en + landing_en) / 2
ax.text(mid_tl[0], mid_tl[1] + 3, '7.5 m', fontsize=5.5, color='#116622',
        ha='center', va='bottom', zorder=9)

# 11. RTL path — dashed grey
ax.plot([landing_en[0], 0], [landing_en[1], 0], '--', color='#888888',
        linewidth=0.9, alpha=0.55, zorder=6)
rtl_mx, rtl_my = landing_en[0] * 0.45, landing_en[1] * 0.45
ax.annotate('RTL', xy=(rtl_mx, rtl_my), fontsize=7, color='#777777',
           fontweight='bold', ha='left', va='bottom', zorder=6,
           bbox=dict(boxstyle='round,pad=0.15', fc='white', ec='none', alpha=0.7))

# ── North arrow ─────────────────────────────────────────────────────
xlim, ylim = ax.get_xlim(), ax.get_ylim()
na_x = xlim[1] - 22
na_y = ylim[1] - 18
na_len = 20
ax.annotate('', xy=(na_x, na_y), xytext=(na_x, na_y - na_len),
           arrowprops=dict(arrowstyle='->', lw=1.8, color='black'), zorder=15)
ax.text(na_x, na_y + 3.5, 'N', ha='center', va='bottom', fontsize=11,
        fontweight='bold', zorder=15)

# ── Scale bar (50 m) ────────────────────────────────────────────────
sb_x = xlim[0] + 15
sb_y = ylim[0] + 14
sb_len = 50
ax.plot([sb_x, sb_x + sb_len], [sb_y, sb_y], 'k-', linewidth=2.5, zorder=15)
ax.plot([sb_x, sb_x], [sb_y - 2, sb_y + 2], 'k-', linewidth=1.5, zorder=15)
ax.plot([sb_x + sb_len, sb_x + sb_len], [sb_y - 2, sb_y + 2], 'k-',
        linewidth=1.5, zorder=15)
ax.text(sb_x + sb_len/2, sb_y + 4, '50 m', ha='center', va='bottom',
        fontsize=8, fontweight='bold', zorder=15)

# ── Axis formatting ─────────────────────────────────────────────────
ax.set_xlabel('East (m)', fontsize=10, labelpad=6)
ax.set_ylabel('North (m)', fontsize=10, labelpad=6)
ax.set_title('Mission Overview \u2014 Fenswood Wilderness Site', fontsize=12,
             fontweight='bold', pad=10)
ax.set_aspect('equal')
ax.grid(True, alpha=0.12, linewidth=0.4, color='#555555')
ax.tick_params(labelsize=8)

# ── Legend ───────────────────────────────────────────────────────────
legend_elements = [
    Line2D([0], [0], color='#2266bb', linestyle='--', lw=1.3,
           label='Flight area boundary'),
    mpatches.Patch(facecolor='#22aa2218', edgecolor='#117711', lw=1.5,
                   label='Search area'),
    mpatches.Patch(facecolor='#ff000015', edgecolor='#cc0000', lw=1.4,
                   hatch='////', label='SSSI no-fly zone'),
    mpatches.Patch(facecolor='#ff880025', edgecolor='#cc6600', lw=1.2,
                   linestyle='--', label='Focus area (PLB)'),
    Line2D([0], [0], color='#4477cc', lw=0.8, label='Search pattern'),
    Line2D([0], [0], marker='*', color='w', markerfacecolor='#eeaa00',
           markeredgecolor='black', markersize=11, label='Take-off location'),
    Line2D([0], [0], marker='X', color='#cc0000', markersize=8,
           markeredgewidth=2, linestyle='None', label='Target (simulated)'),
    Line2D([0], [0], marker='o', color='#ff8800', markersize=5,
           linestyle='None', label='GPS estimates'),
    Line2D([0], [0], marker='D', color='#22bb44', markeredgecolor='black',
           markersize=6, linestyle='None', label='Landing (7.5 m offset)'),
    Line2D([0], [0], color='#888888', linestyle='--', lw=1.0, label='RTL path'),
]
ax.legend(handles=legend_elements, loc='lower right', fontsize=6.5,
          framealpha=0.92, edgecolor='#cccccc', ncol=2, handletextpad=0.5,
          columnspacing=1.0)

plt.tight_layout()

# ── Save ─────────────────────────────────────────────────────────────
out = r'c:\Users\Bristol\Desktop\AI for Robotics\v3\report\figs'
plt.savefig(f'{out}/mission_overview.pdf', bbox_inches='tight', dpi=300)
plt.savefig(f'{out}/mission_overview.png', bbox_inches='tight', dpi=200)
print(f"Saved to {out}/mission_overview.pdf and .png")
print(f"  Lawnmower: {len(lawn_wps)} waypoints, {len(lawn_wps)//2} strips")
print(f"  Swath: {(SENSOR_WIDTH_MM * TARGET_ALT / FOCAL_LENGTH_MM) * 0.8:.1f} m")
print(f"  Target at: E={target_en[0]:.1f}, N={target_en[1]:.1f}")
print(f"  Landing at: E={landing_en[0]:.1f}, N={landing_en[1]:.1f}")
plt.close()
