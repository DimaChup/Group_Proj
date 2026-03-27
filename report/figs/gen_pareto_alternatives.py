"""
Generate 4 alternative Pareto visualizations:
  1. pareto_curve.pdf        — Classic 2D Pareto curve (detection prob vs mission time)
  2. pareto_3d.pdf           — 3D Pareto (detection, time, energy; color=coverage)
  3. pareto_parallel.pdf     — Parallel coordinates (all 5 objectives)
  4. pareto_tradeoff_simple.pdf — Ultra-clean 5-7 key configs
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.collections import LineCollection
from mpl_toolkits.mplot3d import Axes3D
from pathlib import Path

OUT = Path(__file__).parent

# ── Shared physics model ──
# More realistic detection model that accounts for:
# - Target pixel size decreasing with altitude
# - Motion blur at higher speeds
# - Single-pass vs multi-frame probability
# - Realistic GSD-based detection thresholds
SENSOR_W_MM = 5.02
FOCAL_MM = 5.46
IMAGE_W = 1456
DUMMY_H_M = 1.8
FPS = 4.8

altitudes = np.array([20, 25, 30, 35, 40, 50])
speeds = np.array([4, 6, 8, 10, 12, 14])
overlaps = np.array([0.05, 0.10, 0.15, 0.20, 0.25, 0.30])

results = []
for alt in altitudes:
    for spd in speeds:
        for ovl in overlaps:
            footprint_w = alt * SENSOR_W_MM / FOCAL_MM
            lane_spacing = footprint_w * (1 - ovl)
            target_px = DUMMY_H_M * FOCAL_MM / (alt * SENSOR_W_MM / IMAGE_W)
            n_frames = footprint_w / spd * FPS

            # More realistic single-frame detection:
            # - Sigmoid centered at ~40px (need decent pixel coverage)
            # - Motion blur penalty: faster = lower confidence
            # - Steeper falloff so high altitudes genuinely hurt
            blur_penalty = 1.0 / (1 + 0.008 * spd**2)  # drops to ~0.6 at 14 m/s
            p_single = 0.92 / (1 + np.exp(-0.08 * (target_px - 40))) * blur_penalty

            # Multi-frame: fewer effective frames at high speed (blur reduces useful ones)
            effective_frames = max(n_frames * blur_penalty, 0.5)
            p_detect = 1 - (1 - p_single) ** effective_frames

            # Coverage: fraction of area actually scanned
            coverage = min(1.0, lane_spacing / footprint_w * 1.1)

            area_w, area_l = 200, 300
            n_lanes = area_w / lane_spacing
            total_dist = n_lanes * area_l
            time_s = total_dist / spd
            power_factor = 1 + 0.02 * (spd - 6) ** 2
            energy_wh = time_s * power_factor / 3600 * 350  # ~350W hover

            # Safety: low altitude = obstacle risk, high speed = less control margin
            safety = 1.0 - 0.3 * np.clip((30 - alt) / 30, 0, 1) \
                         - 0.3 * np.clip((spd - 8) / 8, 0, 1)
            results.append({
                "alt": alt, "spd": spd, "ovl": ovl,
                "p_detect": p_detect, "coverage": coverage,
                "time": time_s, "energy": energy_wh, "safety": safety,
            })

# Arrays
p_detect = np.array([r["p_detect"] for r in results])
coverage = np.array([r["coverage"] for r in results])
times = np.array([r["time"] for r in results])
energies = np.array([r["energy"] for r in results])
safety = np.array([r["safety"] for r in results])
alts = np.array([r["alt"] for r in results])
spds = np.array([r["spd"] for r in results])

def find_config(alt_t, spd_t, ovl_t=0.15):
    for i, r in enumerate(results):
        if r["alt"] == alt_t and r["spd"] == spd_t and abs(r["ovl"] - ovl_t) < 0.01:
            return i
    return None

selected = find_config(35, 8)

# ── Pareto utilities ──
def is_dominated_2d(x, y, i, maximize_x=True, minimize_y=True):
    """Check if point i is dominated by any other point."""
    for j in range(len(x)):
        if j == i:
            continue
        better_x = (x[j] > x[i]) if maximize_x else (x[j] < x[i])
        better_y = (y[j] < y[i]) if minimize_y else (y[j] > y[i])
        eq_x = np.isclose(x[j], x[i])
        eq_y = np.isclose(y[j], y[i])
        if (better_x and (better_y or eq_y)) or (better_y and (better_x or eq_x)):
            return True
    return False

def pareto_front_2d(x, y):
    """Return indices of non-dominated points (max x, min y)."""
    idx = np.argsort(-x)
    front = []
    min_y = np.inf
    for i in idx:
        if y[i] < min_y:
            front.append(i)
            min_y = y[i]
    return sorted(front, key=lambda i: x[i])

def pareto_front_nd(objectives, directions):
    """N-dimensional Pareto front. directions: 1=maximize, -1=minimize."""
    n = len(objectives[0])
    obj = np.array(objectives).T  # (n_points, n_objectives)
    # Flip minimize objectives so all are maximize
    for j, d in enumerate(directions):
        if d == -1:
            obj[:, j] = -obj[:, j]
    front = []
    for i in range(n):
        dominated = False
        for j in range(n):
            if i == j:
                continue
            if np.all(obj[j] >= obj[i]) and np.any(obj[j] > obj[i]):
                dominated = True
                break
        if not dominated:
            front.append(i)
    return front


# ============================================================
# FIGURE 1: pareto_curve.pdf — Classic 2D Pareto curve
# ============================================================
print("Generating pareto_curve...")
fig1, ax1 = plt.subplots(figsize=(8, 5.5))

pf1_idx = pareto_front_2d(p_detect, times)
pf1_x = p_detect[pf1_idx]
pf1_y = times[pf1_idx]

# All points colored by altitude
norm_alt = Normalize(vmin=18, vmax=52)
cmap_alt = plt.cm.RdYlBu_r
sc1 = ax1.scatter(p_detect, times, c=alts, cmap=cmap_alt, norm=norm_alt,
                  s=22, alpha=0.4, edgecolors="none", zorder=2)
cb1 = plt.colorbar(sc1, ax=ax1, shrink=0.8, pad=0.02)
cb1.set_label("Altitude (m)", fontsize=10)

# Pareto curve — smooth line through non-dominated points
ax1.plot(pf1_x, pf1_y, "k-", lw=2.5, alpha=0.8, zorder=3, label="Pareto frontier")
ax1.scatter(pf1_x, pf1_y, c=alts[pf1_idx], cmap=cmap_alt, norm=norm_alt,
            s=70, edgecolors="k", lw=1.2, zorder=4)

# Selected point
if selected is not None:
    ax1.scatter(p_detect[selected], times[selected], marker="*", s=350,
                c="#2166ac", edgecolors="k", lw=1.5, zorder=6)
    ax1.annotate("Selected\n(35 m, 8 m/s)",
                 (p_detect[selected], times[selected]),
                 textcoords="offset points", xytext=(-95, 35), fontsize=10,
                 fontweight="bold", color="#2166ac",
                 arrowprops=dict(arrowstyle="->", color="#2166ac", lw=1.2))

# Utopia point (max detection, min time) — placed in empty bottom-right
utopia_time = times.min() * 0.5
ax1.scatter(1.0, utopia_time, marker="x", s=150, c="gold", lw=3, zorder=5)
ax1.annotate("Utopia point\n(unreachable)",
             (1.0, utopia_time), textcoords="offset points", xytext=(-110, -20),
             fontsize=9, color="goldenrod", fontstyle="italic",
             arrowprops=dict(arrowstyle="->", color="goldenrod", lw=1.0, ls="--"))

# Annotation along the curve — place below title, away from legend
ax1.text(0.55, 0.93,
         r"$\longrightarrow$ Better detection (lower altitude) costs more time",
         transform=ax1.transAxes, ha="center", fontsize=9, color="grey",
         fontstyle="italic")

ax1.set_xlabel("Detection Probability", fontsize=11)
ax1.set_ylabel("Mission Time (s)", fontsize=11)
ax1.set_title("Pareto Frontier: Detection Probability vs Mission Time",
              fontsize=13, fontweight="bold")
ax1.legend(loc="upper left", fontsize=9, framealpha=0.9)
ax1.grid(True, alpha=0.25)

# Ensure x-axis uses plain format, not scientific notation
ax1.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.2f}"))

for fmt in ["pdf", "png"]:
    fig1.savefig(OUT / f"pareto_curve.{fmt}", dpi=300, bbox_inches="tight")
plt.close(fig1)
print("  Saved pareto_curve.pdf/.png")


# ============================================================
# FIGURE 2: pareto_3d.pdf — 3D Pareto surface
# ============================================================
print("Generating pareto_3d...")
fig2 = plt.figure(figsize=(10, 7.5))
ax2 = fig2.add_subplot(111, projection="3d")

# Non-dominated in 3D (max detection, min time, min energy)
pf3_idx = pareto_front_nd([p_detect, times, energies], [1, -1, -1])
dominated_mask = np.ones(len(results), dtype=bool)
dominated_mask[pf3_idx] = False

# Dominated points (small, transparent)
ax2.scatter(p_detect[dominated_mask], times[dominated_mask], energies[dominated_mask],
            c=coverage[dominated_mask], cmap="YlGn", s=15, alpha=0.25,
            edgecolors="none", vmin=0.3, vmax=1.0)

# Pareto-optimal points (larger, outlined)
sc2 = ax2.scatter(p_detect[pf3_idx], times[pf3_idx], energies[pf3_idx],
                  c=coverage[pf3_idx], cmap="YlGn", s=60, alpha=0.85,
                  edgecolors="k", lw=0.5, vmin=0.3, vmax=1.0, zorder=5)

# Selected point
if selected is not None:
    ax2.scatter([p_detect[selected]], [times[selected]], [energies[selected]],
                marker="*", s=400, c="#2166ac", edgecolors="k", lw=1.5, zorder=10)
    # Place label above with vertical offset in energy axis
    ax2.text(p_detect[selected], times[selected],
             energies[selected] + (energies.max() - energies.min()) * 0.15,
             "Selected\n(35 m, 8 m/s)", fontsize=9, fontweight="bold",
             color="#2166ac", ha="center")

cb2 = fig2.colorbar(sc2, ax=ax2, shrink=0.55, pad=0.1)
cb2.set_label("Coverage", fontsize=10)

ax2.set_xlabel("Detection Prob.", fontsize=9, labelpad=6)
ax2.set_ylabel("Mission Time (s)", fontsize=9, labelpad=6)
ax2.set_zlabel("Energy (Wh)", fontsize=9, labelpad=6)
ax2.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.2f}"))
ax2.tick_params(axis='x', labelsize=7, pad=2)
ax2.tick_params(axis='y', labelsize=7, pad=2)
ax2.tick_params(axis='z', labelsize=7, pad=2)
ax2.set_title("3D Objective Space (4th dimension: colour = coverage)",
              fontsize=12, fontweight="bold", pad=10)
ax2.view_init(elev=25, azim=-45)

for fmt in ["pdf", "png"]:
    fig2.savefig(OUT / f"pareto_3d.{fmt}", dpi=300, bbox_inches="tight")
plt.close(fig2)
print("  Saved pareto_3d.pdf/.png")


# ============================================================
# FIGURE 3: pareto_parallel.pdf — Parallel coordinates
# ============================================================
print("Generating pareto_parallel...")
fig3, ax3 = plt.subplots(figsize=(10, 5.5))

# 5 axes: Coverage, Detection, 1/Time (speed), 1/Energy (efficiency), Safety
# All normalized to [0, 1] where 1 = better
dim_labels = ["Coverage", "Detection\nProbability", "Speed\n(1/time)",
              "Efficiency\n(1/energy)", "Safety"]

raw_dims = np.column_stack([
    coverage,
    p_detect,
    1.0 / times,
    1.0 / energies,
    safety,
])

# Normalize each dimension to [0, 1]
dims_min = raw_dims.min(axis=0)
dims_max = raw_dims.max(axis=0)
dims_norm = (raw_dims - dims_min) / (dims_max - dims_min + 1e-12)

n_dims = dims_norm.shape[1]
x_positions = np.arange(n_dims)

# Pareto front in 5D (all maximize after inversion)
pf5_idx = set(pareto_front_nd(
    [coverage, p_detect, 1.0/times, 1.0/energies, safety],
    [1, 1, 1, 1, 1]
))

# Draw axes
for i in range(n_dims):
    ax3.axvline(i, color="k", lw=1.2, alpha=0.5)
    ax3.text(i, -0.08, dim_labels[i], ha="center", va="top", fontsize=9,
             fontweight="bold", transform=ax3.get_xaxis_transform())

# Draw lines for each configuration
for i in range(len(results)):
    y_vals = dims_norm[i]
    if i == selected:
        continue  # draw last
    if i in pf5_idx:
        ax3.plot(x_positions, y_vals, c="#e67e22", alpha=0.5, lw=1.2, zorder=3)
    else:
        ax3.plot(x_positions, y_vals, c="lightgrey", alpha=0.3, lw=0.5, zorder=1)

# Pareto legend line
ax3.plot([], [], c="#e67e22", lw=2, alpha=0.7, label=f"Pareto-optimal ({len(pf5_idx)} configs)")
ax3.plot([], [], c="lightgrey", lw=1.5, alpha=0.6, label=f"Dominated ({len(results)-len(pf5_idx)} configs)")

# Selected configuration (thick blue, on top)
if selected is not None:
    y_sel = dims_norm[selected]
    ax3.plot(x_positions, y_sel, c="#2166ac", lw=3.5, zorder=5,
             label="Selected (35 m, 8 m/s)")
    ax3.scatter(x_positions, y_sel, c="#2166ac", s=60, zorder=6, edgecolors="white", lw=1.2)

ax3.set_xlim(-0.3, n_dims - 0.7)
ax3.set_ylim(-0.05, 1.1)
ax3.set_xticks(x_positions)
ax3.set_xticklabels([""] * n_dims)  # labels drawn manually above
ax3.set_ylabel("Normalised Score (higher = better)", fontsize=10)
ax3.set_title("Parallel Coordinates: 216 Configurations Across 5 Objectives",
              fontsize=12, fontweight="bold")
ax3.legend(loc="upper right", fontsize=9, framealpha=0.9)

# Add scale ticks on each axis — show real-world values
for i in range(n_dims):
    for val in [0.0, 0.5, 1.0]:
        real_val = dims_min[i] + val * (dims_max[i] - dims_min[i])
        if i == 2:    # 1/time axis — show as time (s)
            if real_val > 0:
                label = f"{1.0/real_val:.0f}s"
            else:
                label = ""
        elif i == 3:  # 1/energy axis — show as energy (Wh)
            if real_val > 0:
                label = f"{1.0/real_val:.0f}Wh"
            else:
                label = ""
        else:
            label = f"{real_val:.2f}"
        ax3.text(i + 0.07, val, label, fontsize=7, color="grey", va="center")

for fmt in ["pdf", "png"]:
    fig3.savefig(OUT / f"pareto_parallel.{fmt}", dpi=300, bbox_inches="tight")
plt.close(fig3)
print("  Saved pareto_parallel.pdf/.png")


# ============================================================
# FIGURE 4: pareto_tradeoff_simple.pdf — Ultra-clean summary
# ============================================================
print("Generating pareto_tradeoff_simple...")
fig4, ax4 = plt.subplots(figsize=(8, 5.5))

# Composite axes
time_norm = (times - times.min()) / (times.max() - times.min())
energy_norm = (energies - energies.min()) / (energies.max() - energies.min())
mission_cost = 0.5 * time_norm + 0.5 * energy_norm
mission_effectiveness = p_detect * coverage

# 5 key well-spaced configurations (removed 20/8 and 50/10 to avoid overlap)
key_configs = [
    (20, 4,  0.15, "20 m, 4 m/s\n(max reliability)",  "^",  "#762a83", 140),
    (25, 8,  0.15, "25 m, 8 m/s",                      "o",  "#9970ab",  80),
    (35, 8,  0.15, "35 m, 8 m/s\n(SELECTED)",          "*",  "#2166ac", 300),
    (40, 10, 0.15, "40 m, 10 m/s",                     "s",  "#5aae61",  80),
    (50, 14, 0.15, "50 m, 14 m/s\n(fastest)",          "D",  "#d73027", 140),
]

key_indices = []
key_labels = []
key_markers = []
key_colors = []
key_sizes = []
for alt_t, spd_t, ovl_t, label, mkr, clr, sz in key_configs:
    idx = find_config(alt_t, spd_t, ovl_t)
    if idx is not None:
        key_indices.append(idx)
        key_labels.append(label)
        key_markers.append(mkr)
        key_colors.append(clr)
        key_sizes.append(sz)

ki = np.array(key_indices)
kx = mission_effectiveness[ki]
ky = mission_cost[ki]

# Connect with dashed line (approximate trade-off curve)
order = np.argsort(kx)
ax4.plot(kx[order], ky[order], "k--", lw=1.5, alpha=0.4, zorder=2)

# Label offsets — manually tuned to avoid overlap
label_offsets = [
    (-85, 10),    # 20,4  — far left (away from "Expensive but reliable")
    (-80, -20),   # 25,8  — far left
    (15, 25),     # 35,8  selected — top right
    (15, -25),    # 40,10 — bottom right
    (-10, -30),   # 50,14 — below
]

for j in range(len(ki)):
    ax4.scatter(kx[j], ky[j], marker=key_markers[j], s=key_sizes[j],
                c=key_colors[j], edgecolors="k", lw=1.2, zorder=5)
    ax4.annotate(key_labels[j],
                 (kx[j], ky[j]),
                 textcoords="offset points", xytext=label_offsets[j],
                 fontsize=8.5, ha="center",
                 fontweight="bold" if "SELECTED" in key_labels[j] else "normal",
                 color=key_colors[j],
                 arrowprops=dict(arrowstyle="-", color=key_colors[j], lw=0.8))

# Arrow: expensive-reliable to cheap-risky
ax4.annotate("", xy=(kx[order[0]] - 0.015, ky[order[0]] + 0.015),
             xytext=(kx[order[-1]] + 0.015, ky[order[-1]] - 0.015),
             arrowprops=dict(arrowstyle="<->", color="grey", lw=1.8, ls="-"))
ax4.text(0.15, 0.12, "Cheap but risky", fontsize=9, color="grey",
         fontstyle="italic", transform=ax4.transAxes, ha="center")
ax4.text(0.85, 0.95, "Expensive but reliable", fontsize=9, color="grey",
         fontstyle="italic", transform=ax4.transAxes, ha="center")

# Best compromise highlight
if selected is not None:
    from matplotlib.patches import FancyBboxPatch
    sel_x = mission_effectiveness[selected]
    sel_y = mission_cost[selected]
    rect = FancyBboxPatch((sel_x - 0.025, sel_y - 0.04), 0.05, 0.08,
                          boxstyle="round,pad=0.015", facecolor="#2166ac",
                          alpha=0.10, edgecolor="#2166ac", lw=1.5, ls="--", zorder=1)
    ax4.add_patch(rect)

ax4.set_xlabel("Mission Effectiveness (detection $\\times$ coverage)", fontsize=11)
ax4.set_ylabel("Mission Cost (normalised time + energy)", fontsize=11)
ax4.set_title("Trade-off Summary: Key Configurations", fontsize=13, fontweight="bold")
ax4.grid(True, alpha=0.2)
ax4.set_xlim(min(kx) - 0.06, max(kx) + 0.06)
ax4.set_ylim(min(ky) - 0.1, max(ky) + 0.15)

for fmt in ["pdf", "png"]:
    fig4.savefig(OUT / f"pareto_tradeoff_simple.{fmt}", dpi=300, bbox_inches="tight")
plt.close(fig4)
print("  Saved pareto_tradeoff_simple.pdf/.png")

print("\nAll 4 Pareto figures generated successfully.")
