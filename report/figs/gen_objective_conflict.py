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

    Physics-based but with normalisation tuned across the 20-50m, 6-10m/s envelope
    so that competing objectives create visible tension on the radar chart.
    """
    footprint_w = alt * SENSOR_W_MM / FOCAL_MM  # ground coverage width (m)
    lane_spacing = footprint_w * 0.85  # 15% overlap

    # ── Coverage rate: footprint * speed, normalised across envelope ──
    rate = footprint_w * spd
    # Range: ~110 (20m@6m/s) to ~460 (50m@10m/s)
    coverage = np.clip((rate - 100) / (470 - 100), 0.05, 1.0)

    # ── Detection: target pixel height drops with altitude ──
    target_px = DUMMY_H_M * FOCAL_MM / (alt * SENSOR_W_MM / IMAGE_W)
    # At 20m: ~52px (excellent), 35m: ~30px (good), 50m: ~21px (marginal)
    # Steep sigmoid centred at 30px — drops sharply above 35m
    detection = 0.97 / (1 + np.exp(-0.35 * (target_px - 32)))

    # ── 1/Time: fewer lanes and higher speed = faster ──
    area_w, area_l = 200, 300
    n_lanes = area_w / lane_spacing
    time_s = n_lanes * area_l / spd
    # Range: ~650s (50m@10m/s) to ~3850s (20m@6m/s)
    inv_time = np.clip(1 - (time_s - 600) / (4000 - 600), 0.05, 1.0)

    # ── 1/Energy: time * drag power; fast+many-lanes is worst ──
    drag = 1 + 0.06 * (spd - 6) ** 2  # quadratic drag penalty
    energy = time_s * drag
    # Range: ~700 (50m@6m/s) to ~6500 (20m@10m/s)
    inv_energy = np.clip(1 - (energy - 600) / (7000 - 600), 0.05, 1.0)

    # ── Safety: smaller footprint (low alt) + slower = safer near NFZ ──
    margin = NFZ_BUFFER - footprint_w / 2
    reaction = 1 - 0.05 * (spd - 4)  # penalty for high speed
    safety = np.clip(margin / NFZ_BUFFER * reaction, 0.05, 1.0)

    return [coverage, detection, inv_time, inv_energy, safety]

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
