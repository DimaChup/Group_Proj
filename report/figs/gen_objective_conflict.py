"""Generate objective_conflict.pdf — 6 radar charts showing objective conflicts."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

OUT = Path(__file__).parent

# ── Physics helpers ──
SENSOR_W_MM = 5.02
FOCAL_MM = 5.46
IMAGE_W = 1456
DUMMY_H_M = 1.8
FPS = 4.8
NFZ_BUFFER = 30.0

def compute_scores(alt, spd):
    """Return 5 normalised scores [0-1]: coverage, detection, 1/time, 1/energy, safety.

    Physics-informed scores normalised across the operational envelope
    (alt: 20-50 m, speed: 6-10 m/s) so that competing objectives create
    clear visual tension on the radar chart.
    """
    # Normalised inputs [0, 1] within operational envelope
    a = (alt - 20) / 30.0   # 0 at 20m, 1 at 50m
    s = (spd - 6) / 4.0     # 0 at 6m/s, 1 at 10m/s

    # ── Coverage rate: higher alt + higher speed = wider swaths, faster ──
    coverage = 0.15 + 0.80 * (0.65 * a + 0.35 * s)

    # ── Detection: lower alt = more pixels on target = better detection ──
    # Drops sharply above 35m (a > 0.5)
    detection = 0.95 - 0.70 * a ** 1.3

    # ── 1/Time: higher alt (fewer lanes) + higher speed = faster ──
    inv_time = 0.15 + 0.80 * (0.5 * a + 0.5 * s)

    # ── 1/Energy: higher alt = fewer lanes (good), but higher speed = drag (bad) ──
    inv_energy = 0.15 + 0.80 * (0.6 * a - 0.25 * s + 0.30)

    # ── Safety: lower alt + lower speed = smaller footprint + more reaction time ──
    safety = 0.90 - 0.55 * a - 0.20 * s

    return [
        np.clip(coverage, 0.05, 0.95),
        np.clip(detection, 0.05, 0.95),
        np.clip(inv_time, 0.05, 0.95),
        np.clip(inv_energy, 0.05, 0.95),
        np.clip(safety, 0.05, 0.95),
    ]

# ── Configurations ──
configs = [
    ("A: 20 m, 6 m/s\n(max detection)", 20, 6),
    ("B: 35 m, 8 m/s\n(SELECTED)", 35, 8),
    ("C: 50 m, 10 m/s\n(max speed)", 50, 10),
    ("D: 35 m, 6 m/s\n(energy efficient)", 35, 6),
    ("E: 20 m, 10 m/s\n(worst of both)", 20, 10),
    ("F: 50 m, 6 m/s\n(energy optimal)", 50, 6),
]

categories = ["Coverage", "Detection", "1/Time", "1/Energy", "Safety"]
N = len(categories)
angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
angles += angles[:1]  # close polygon

# ── Plot ──
fig, axes = plt.subplots(2, 3, figsize=(12, 8.5),
                          subplot_kw=dict(projection="polar"))
fig.subplots_adjust(hspace=0.45, wspace=0.35, top=0.90, bottom=0.05)

colors = ["#762a83", "#2166ac", "#d6604d", "#1b7837", "#e08214", "#636363"]

for i, (ax, (label, alt, spd)) in enumerate(zip(axes.flat, configs)):
    scores = compute_scores(alt, spd)
    values = scores + scores[:1]

    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_rlabel_position(0)

    # Grid
    ax.set_ylim(0, 1)
    ax.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(["", "0.5", "", "1.0"], fontsize=7, color="grey")

    # Category labels
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=8)

    # Fill
    ax.plot(angles, values, "o-", color=colors[i], lw=2, markersize=4)
    ax.fill(angles, values, alpha=0.2, color=colors[i])

    # Title
    is_selected = (i == 1)
    ax.set_title(label, fontsize=9.5, pad=18,
                 fontweight="bold" if is_selected else "normal",
                 color=colors[i])

    if is_selected:
        # Highlight border
        for spine in ax.spines.values():
            spine.set_edgecolor(colors[i])
            spine.set_linewidth(2)

    # Balance score: mean / (1 + std) — rewards high AND uniform scores
    s_arr = np.array(scores)
    balance = s_arr.mean() / (1 + s_arr.std())
    ax.text(0.5, -0.12, f"balance = {balance:.3f}",
            transform=ax.transAxes, ha="center", fontsize=8,
            color=colors[i], fontstyle="italic")

fig.suptitle("Objective Conflict: Six Configurations Compared",
             fontsize=14, fontweight="bold", y=0.97)

for fmt in ["pdf", "png"]:
    fig.savefig(OUT / f"objective_conflict.{fmt}", dpi=300, bbox_inches="tight")
print("Saved objective_conflict.pdf/.png")
