"""Generate top-3 path configurations from 216-config sweep, overlaid on search area."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon, FancyArrowPatch
from shapely.geometry import Polygon, LineString, MultiLineString
from shapely import affinity
import math, os

# ── GPS coordinates from config.py ──────────────────────────────────────────
SEARCH_AREA_GPS = [
    (51.42326956502679, -2.670948345438704),
    (51.42287025017865, -2.670045428650557),
    (51.42336622593724, -2.668169295906676),
    (51.42421477437771, -2.668809768621569),
    (51.42354069739116, -2.671277780473196),
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
FLIGHT_AREA_GPS = [
    (51.42342595349562, -2.671720766408759),
    (51.42124623420381, -2.670134027271237),
    (51.42244011936099, -2.66568781888585),
    (51.42469179370701, -2.667060227266051),
]
TAKEOFF_GPS = (51.42340640206451, -2.671446029622069)

# ── Conversion: GPS -> local metres ─────────────────────────────────────────
REF_LAT = np.mean([p[0] for p in SEARCH_AREA_GPS])
REF_LON = np.mean([p[1] for p in SEARCH_AREA_GPS])
M_PER_DEG_LAT = 111320.0
M_PER_DEG_LON = 111320.0 * math.cos(math.radians(REF_LAT))

def gps_to_m(lat, lon):
    return ((lon - REF_LON) * M_PER_DEG_LON, (lat - REF_LAT) * M_PER_DEG_LAT)

search_m  = [gps_to_m(*p) for p in SEARCH_AREA_GPS]
sssi_m    = [gps_to_m(*p) for p in SSSI_GPS]
flight_m  = [gps_to_m(*p) for p in FLIGHT_AREA_GPS]
takeoff_m = gps_to_m(*TAKEOFF_GPS)

search_poly = Polygon(search_m)
sssi_poly   = Polygon(sssi_m)

# ── NFZ buffer ──────────────────────────────────────────────────────────────
NFZ_BUFFER_M = 30.0
sssi_buffered = sssi_poly.buffer(NFZ_BUFFER_M)

# ── Lawnmower path generator (fixed line count) ────────────────────────────
def generate_lawnmower(polygon, angle_deg, n_lines):
    """Generate exactly n_lines scan lines inside polygon at the given angle.

    Evenly spaces n_lines across the polygon extent along the scan direction.
    Returns list of LineString segments in zigzag order.
    """
    # Rotate polygon so scan direction becomes horizontal
    centroid = polygon.centroid
    rotated = affinity.rotate(polygon, -angle_deg, origin=centroid)
    minx, miny, maxx, maxy = rotated.bounds

    # Evenly space n_lines across the y-extent
    inset = (maxy - miny) * 0.06  # small edge inset
    ys = np.linspace(miny + inset, maxy - inset, n_lines)

    scan_lines = []
    for y_val in ys:
        line = LineString([(minx - 20, y_val), (maxx + 20, y_val)])
        clipped = rotated.intersection(line)
        if clipped.is_empty:
            continue
        if isinstance(clipped, LineString):
            scan_lines.append(clipped)
        elif isinstance(clipped, MultiLineString):
            # Take the longest segment
            longest = max(clipped.geoms, key=lambda g: g.length)
            scan_lines.append(longest)

    # Rotate back and zigzag
    result = []
    for i, seg in enumerate(scan_lines):
        rotated_back = affinity.rotate(seg, angle_deg, origin=centroid)
        if i % 2 == 1:
            rotated_back = LineString(rotated_back.coords[::-1])
        result.append(rotated_back)

    return result


def build_full_path(scan_lines, takeoff):
    """Connect scan lines into full path. Returns (scan_segs, turn_segs)."""
    if not scan_lines:
        return [], []

    turn_segments = []

    # Transit: takeoff -> first scan line start
    first_start = list(scan_lines[0].coords)[0]
    turn_segments.append(LineString([takeoff, first_start]))

    # Turns between scan lines
    for i in range(len(scan_lines) - 1):
        end_curr  = list(scan_lines[i].coords)[-1]
        start_nxt = list(scan_lines[i + 1].coords)[0]
        turn_segments.append(LineString([end_curr, start_nxt]))

    # Transit: last scan line end -> takeoff
    last_end = list(scan_lines[-1].coords)[-1]
    turn_segments.append(LineString([last_end, takeoff]))

    return scan_lines, turn_segments


# ── Top 3 configurations ────────────────────────────────────────────────────
configs = [
    {
        "rank": 1, "label": "SELECTED",
        "alt": 35, "angle": 70, "speed": 8.0,
        "score": 0.87, "scan_lines": 5, "turns": 4,
        "energy": 12.6, "time": 112,
        "color": "#2166ac", "color_turn": "#92c5de",
    },
    {
        "rank": 2, "label": "",
        "alt": 30, "angle": 65, "speed": 7.3,
        "score": 0.85, "scan_lines": 6, "turns": 5,
        "energy": 14.1, "time": 128,
        "color": "#e66101", "color_turn": "#fdb863",
    },
    {
        "rank": 3, "label": "",
        "alt": 40, "angle": 75, "speed": 8.7,
        "score": 0.84, "scan_lines": 4, "turns": 3,
        "energy": 11.2, "time": 95,
        "color": "#1b7837", "color_turn": "#a6dba0",
    },
]

# ── Generate figure ─────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(15.5, 5.8), dpi=150)
fig.suptitle("Top 3 Configurations from 216-Configuration Sweep",
             fontsize=13, fontweight="bold", y=0.98)

# Compute common axis limits
all_x = [p[0] for p in search_m + flight_m]
all_y = [p[1] for p in search_m + flight_m]
pad = 25
xlims = (min(all_x) - pad, max(all_x) + pad)
ylims = (min(all_y) - pad, max(all_y) + pad)

for ax, cfg in zip(axes, configs):

    # ── Background layers ───────────────────────────────────────────────────
    # Flight boundary (outermost)
    flight_patch = MplPolygon(flight_m, closed=True,
                              facecolor="#fafafa", edgecolor="#aaaaaa",
                              linewidth=0.7, linestyle="--", zorder=0,
                              label="Flight boundary")
    ax.add_patch(flight_patch)

    # Search area polygon
    search_patch = MplPolygon(search_m, closed=True,
                              facecolor="#e8eef5", edgecolor="black",
                              linewidth=1.3, zorder=1, label="Search area")
    ax.add_patch(search_patch)

    # NFZ buffer zone (hatched ring)
    if sssi_buffered.geom_type == 'Polygon':
        buf_coords = list(sssi_buffered.exterior.coords)
        buf_patch = MplPolygon(buf_coords, closed=True,
                               facecolor="#ffcccc30", edgecolor="#cc0000",
                               linewidth=0.7, linestyle=":", zorder=2,
                               label=f"NFZ buffer ({NFZ_BUFFER_M:.0f} m)")
        ax.add_patch(buf_patch)

    # SSSI polygon (solid red fill)
    sssi_patch = MplPolygon(sssi_m, closed=True,
                            facecolor="#ff000020", edgecolor="#cc0000",
                            linewidth=1.3, hatch="///", zorder=3,
                            label="SSSI (NFZ)")
    ax.add_patch(sssi_patch)

    # ── Generate and plot path ──────────────────────────────────────────────
    scan_lines = generate_lawnmower(search_poly, cfg["angle"], cfg["scan_lines"])
    scan_segs, turn_segs = build_full_path(scan_lines, takeoff_m)

    # Scan passes
    for i, seg in enumerate(scan_segs):
        xs, ys = seg.xy
        lbl = "Scan pass" if i == 0 else None
        ax.plot(xs, ys, color=cfg["color"], linewidth=2.2, solid_capstyle="round",
                zorder=5, label=lbl)

        # Direction arrow at midpoint of each scan line
        coords_list = list(seg.coords)
        n_pts = len(coords_list)
        if n_pts >= 2:
            idx = n_pts // 2
            x0, y0 = coords_list[idx - 1]
            x1, y1 = coords_list[idx]
            ax.annotate("",
                        xy=(x1, y1),
                        xytext=(x0, y0),
                        arrowprops=dict(arrowstyle="-|>", color=cfg["color"],
                                        lw=1.8, mutation_scale=12),
                        zorder=7)

    # Turn / transit dashes
    for i, seg in enumerate(turn_segs):
        xs, ys = seg.xy
        lbl = "Turn / transit" if i == 0 else None
        ax.plot(xs, ys, color=cfg["color_turn"], linewidth=1.0,
                linestyle="--", zorder=4, label=lbl)

    # Waypoint dots at scan-line endpoints
    for seg in scan_segs:
        for pt in [seg.coords[0], seg.coords[-1]]:
            ax.plot(pt[0], pt[1], 'o', color=cfg["color"], markersize=3.5,
                    zorder=8, markeredgecolor="white", markeredgewidth=0.4)

    # ── Takeoff marker ──────────────────────────────────────────────────────
    ax.plot(*takeoff_m, marker="^", color="black", markersize=11, zorder=10,
            markeredgecolor="white", markeredgewidth=1.0, label="Take-off")

    # ── Panel title ─────────────────────────────────────────────────────────
    rank_str = f"#{cfg['rank']}"
    if cfg["label"]:
        rank_str += f"  {cfg['label']}"
    ax.set_title(rank_str, fontsize=11, fontweight="bold",
                 color=cfg["color"], pad=8)

    # ── Metrics text box ────────────────────────────────────────────────────
    metrics = (
        f"Alt: {cfg['alt']} m    Angle: {cfg['angle']}\u00b0    Speed: {cfg['speed']} m/s\n"
        f"Score: {cfg['score']:.2f}    Lines: {cfg['scan_lines']}    Turns: {cfg['turns']}\n"
        f"Energy: {cfg['energy']} Wh    Time: {cfg['time']} s"
    )
    ax.text(0.03, 0.03, metrics, transform=ax.transAxes,
            fontsize=7.5, fontfamily="monospace",
            verticalalignment="bottom",
            bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
                      edgecolor="grey", alpha=0.92),
            zorder=20)

    # ── Axis formatting ─────────────────────────────────────────────────────
    ax.set_aspect("equal")
    ax.set_xlabel("East (m)", fontsize=8)
    if cfg["rank"] == 1:
        ax.set_ylabel("North (m)", fontsize=8)
    ax.tick_params(labelsize=7)
    ax.set_xlim(xlims)
    ax.set_ylim(ylims)
    ax.grid(True, alpha=0.15, linewidth=0.5)

# ── Shared legend beneath figure ────────────────────────────────────────────
handles, labels = axes[0].get_legend_handles_labels()
fig.legend(handles, labels, loc="lower center", ncol=6, fontsize=7.5,
           frameon=True, framealpha=0.9, edgecolor="grey",
           bbox_to_anchor=(0.5, -0.01))

plt.tight_layout(rect=[0, 0.04, 1, 0.95])

out_dir = os.path.dirname(os.path.abspath(__file__))
plt.savefig(os.path.join(out_dir, "top3_paths.pdf"), bbox_inches="tight")
plt.savefig(os.path.join(out_dir, "top3_paths.png"), bbox_inches="tight", dpi=200)
print("Saved top3_paths.pdf and top3_paths.png")
