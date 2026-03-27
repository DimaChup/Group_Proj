"""Generate pareto_2d_composite.pdf — 2D Pareto frontier of 216 configs."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from pathlib import Path

OUT = Path(__file__).parent
rng = np.random.default_rng(42)

# ── Physics (from config.py) ──
SENSOR_W_MM = 5.02
FOCAL_MM = 5.46
IMAGE_W = 1456
DUMMY_H_M = 1.8
FPS = 4.8

# ── Parameter sweep: 6 altitudes x 6 speeds x 6 overlaps = 216 configs ──
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
            # Frames on target per pass
            n_frames = footprint_w / spd * FPS
            # Single-frame detection prob (sigmoid of pixel size)
            p_single = 0.95 / (1 + np.exp(-0.15 * (target_px - 15))) + 0.02
            # Multi-frame detection prob
            p_detect = 1 - (1 - p_single) ** max(n_frames, 1)
            # Coverage completeness (penalize large gaps)
            coverage = min(1.0, lane_spacing / footprint_w * 1.1)
            # Effectiveness = detection * coverage
            effectiveness = p_detect * coverage
            # Time cost (proportional to lanes * length / speed)
            area_w, area_l = 200, 300  # m
            n_lanes = area_w / lane_spacing
            total_dist = n_lanes * area_l
            time_s = total_dist / spd
            # Energy cost (proportional to time * power, higher speed = more power)
            power_factor = 1 + 0.02 * (spd - 6) ** 2  # quadratic drag
            energy = time_s * power_factor
            results.append({
                "alt": alt, "spd": spd, "ovl": ovl,
                "eff": effectiveness, "time": time_s, "energy": energy,
                "p_detect": p_detect, "coverage": coverage,
            })

# Normalize cost axes
eff = np.array([r["eff"] for r in results])
times = np.array([r["time"] for r in results])
energies = np.array([r["energy"] for r in results])
alts = np.array([r["alt"] for r in results])
spds = np.array([r["spd"] for r in results])

# Composite cost (normalized)
time_norm = (times - times.min()) / (times.max() - times.min())
energy_norm = (energies - energies.min()) / (energies.max() - energies.min())
cost = 0.5 * time_norm + 0.5 * energy_norm

# ── Pareto frontier ──
def pareto_front(x, y):
    """Return indices of Pareto-optimal points (max x, min y)."""
    idx = np.argsort(-x)  # sort by decreasing effectiveness
    front = []
    min_y = np.inf
    for i in idx:
        if y[i] < min_y:
            front.append(i)
            min_y = y[i]
    return sorted(front, key=lambda i: x[i])

pf_idx = pareto_front(eff, cost)
pf_x = eff[pf_idx]
pf_y = cost[pf_idx]

# ── Special configs ──
def find_config(alt_t, spd_t, ovl_t=0.15):
    for i, r in enumerate(results):
        if r["alt"] == alt_t and r["spd"] == spd_t and abs(r["ovl"] - ovl_t) < 0.01:
            return i
    return None

selected = find_config(35, 8)
fastest = find_config(50, 14)
efficient = find_config(50, 6)
best_det = find_config(20, 6)

# ── Plot ──
fig, ax = plt.subplots(figsize=(9, 6.5))

# Color by altitude
norm = Normalize(vmin=18, vmax=52)
cmap = plt.cm.RdYlBu_r  # blue=low alt, red=high

sc = ax.scatter(eff, cost, c=alts, cmap=cmap, norm=norm, s=28, alpha=0.55,
                edgecolors="none", zorder=2)
cb = plt.colorbar(sc, ax=ax, shrink=0.8, pad=0.02)
cb.set_label("Altitude (m)", fontsize=11)

# Pareto frontier
ax.plot(pf_x, pf_y, "k-", lw=2, alpha=0.7, zorder=3, label="Pareto frontier")
ax.scatter(pf_x, pf_y, c="none", edgecolors="k", s=50, lw=1.2, zorder=4)

# Mark special configs
def mark(idx, label, marker, color, offset, fontsize=9):
    if idx is None:
        return
    ax.scatter(eff[idx], cost[idx], marker=marker, s=200, c=color,
               edgecolors="k", lw=1.5, zorder=5)
    ax.annotate(label, (eff[idx], cost[idx]), textcoords="offset points",
                xytext=offset, fontsize=fontsize, fontweight="bold",
                color=color,
                arrowprops=dict(arrowstyle="-", color=color, lw=0.8))

mark(selected, "Selected\n(35 m, 8 m/s)", "*", "#2166ac", (-90, 25), fontsize=10)
mark(fastest, "Fastest\n(50 m, 14 m/s)", "D", "#d6604d", (-20, -30))
mark(efficient, "Energy-optimal\n(50 m, 6 m/s)", "s", "#1b7837", (-100, -8))
mark(best_det, "Best detection\n(20 m, 6 m/s)", "^", "#762a83", (-110, 10))

# Ideal point
ax.scatter(1.0, 0.0, marker="x", s=120, c="gold", lw=2, zorder=5)
ax.annotate("Ideal\npoint", (1.0, 0.0), textcoords="offset points",
            xytext=(-35, 12), fontsize=9, color="goldenrod", fontstyle="italic")

# Labels
ax.set_xlabel("Mission Effectiveness (coverage $\\times$ detection probability)", fontsize=11)
ax.set_ylabel("Mission Cost (normalised time + energy)", fontsize=11)
ax.set_title("Pareto Frontier: 216 Configuration Sweep", fontsize=13, fontweight="bold")
ax.set_xlim(-0.02, 1.05)
ax.set_ylim(-0.05, 1.05)

ax.text(0.5, -0.12,
        "Each dot = one (altitude, speed, overlap) configuration.  "
        "This 2D view collapses 5 objectives into 2 composite dimensions.",
        transform=ax.transAxes, ha="center", fontsize=9, color="grey",
        fontstyle="italic")

ax.legend(loc="upper left", fontsize=9, framealpha=0.9)
ax.grid(True, alpha=0.25)

for fmt in ["pdf", "png"]:
    fig.savefig(OUT / f"pareto_2d_composite.{fmt}", dpi=300, bbox_inches="tight")
print("Saved pareto_2d_composite.pdf/.png")
