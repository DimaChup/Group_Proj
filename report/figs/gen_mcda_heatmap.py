#!/usr/bin/env python3
"""Generate consolidated MCDA heatmap for design rationale section.

Reads the four MCDA trade studies from design_rationale.tex and produces
a single figure with four sub-panels, colour-coded by weighted score.
Winner highlighted with a bold border.

Output: report/figs/mcda_heatmap.pdf and .png
"""

import pathlib
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap

# ── Data from design_rationale.tex ──────────────────────────────────────

decisions = {
    "Companion Computer": {
        "criteria": [
            ("Unit cost",              0.20),
            ("Power consumption",      0.10),
            ("GPIO / CSI interface",   0.15),
            ("Community & docs",       0.20),
            ("Python 3.13 compat.",    0.20),
            ("TFLite / edge-AI",       0.15),
        ],
        "alternatives": ["Pi 5", "Jetson Nano", "Intel NCS2"],
        "scores": [
            [5, 3, 4],   # cost
            [4, 3, 3],   # power
            [5, 4, 1],   # GPIO
            [5, 4, 2],   # community
            [5, 3, 2],   # python
            [5, 4, 2],   # tflite
        ],
        "totals": [4.90, 3.50, 2.35],
        "winner": 0,
    },
    "Detection Model": {
        "criteria": [
            ("Inference speed",        0.30),
            ("Detection accuracy",     0.25),
            ("Model size",             0.15),
            ("TFLite export",          0.15),
            ("Training data req.",     0.15),
        ],
        "alternatives": ["YOLOv8n", "YOLOv8s", "SSD\nMobileNet"],
        "scores": [
            [5, 3, 5],   # speed
            [4, 5, 3],   # accuracy
            [5, 3, 5],   # size
            [5, 5, 4],   # export
            [5, 4, 4],   # training
        ],
        "totals": [4.75, 3.95, 4.20],
        "winner": 0,
    },
    "Communication": {
        "criteria": [
            ("Latency",                0.20),
            ("Reliability",            0.25),
            ("Multi-consumer",         0.20),
            ("Python 3.13 compat.",    0.20),
            ("Complexity",             0.15),
        ],
        "alternatives": ["Direct\nSerial", "MAVProxy\nBridge", "ROS 2"],
        "scores": [
            [5, 4, 3],   # latency
            [2, 5, 4],   # reliability
            [1, 5, 5],   # multi-consumer
            [1, 5, 3],   # python
            [5, 4, 1],   # complexity
        ],
        "totals": [2.65, 4.65, 3.35],
        "winner": 1,
    },
    "Search Pattern": {
        "criteria": [
            ("Coverage guarantee",     0.30),
            ("Path efficiency",        0.20),
            ("Implementability",       0.20),
            ("Wind robustness",        0.15),
            ("SAR compliance",         0.15),
        ],
        "alternatives": ["Lawn-\nmower", "Spiral", "Expanding\nSquare"],
        "scores": [
            [5, 3, 4],   # coverage
            [4, 3, 3],   # path
            [5, 3, 4],   # implement
            [4, 3, 3],   # wind
            [5, 3, 4],   # SAR
        ],
        "totals": [4.65, 3.00, 3.65],
        "winner": 0,
    },
}

# ── Colour map: red (1) → yellow (3) → green (5) ───────────────────────

cmap = LinearSegmentedColormap.from_list(
    "mcda",
    [(0.0, "#d32f2f"),    # 1 = poor  (red)
     (0.25, "#f57c00"),   # 2 = below average (orange)
     (0.5,  "#fdd835"),   # 3 = average (yellow)
     (0.75, "#8bc34a"),   # 4 = good (light green)
     (1.0,  "#2e7d32")],  # 5 = excellent (dark green)
)

# ── Figure layout ───────────────────────────────────────────────────────

fig, axes = plt.subplots(2, 2, figsize=(11.5, 9.5),
                         gridspec_kw={"hspace": 0.45, "wspace": 0.32})
fig.suptitle("Multi-Criteria Decision Analysis — Design Trade Studies",
             fontsize=14, fontweight="bold", y=0.97)

for ax, (title, d) in zip(axes.flat, decisions.items()):
    scores = np.array(d["scores"], dtype=float)
    n_crit, n_alt = scores.shape
    weights = [w for _, w in d["criteria"]]
    criteria_labels = [f"{name}\n(w={w:.2f})" for name, w in d["criteria"]]

    # Draw heatmap
    im = ax.imshow(scores, cmap=cmap, vmin=1, vmax=5, aspect="auto",
                   origin="upper")

    # Annotate cells
    for i in range(n_crit):
        for j in range(n_alt):
            val = int(scores[i, j])
            text_color = "white" if val <= 2 else "black"
            ax.text(j, i, str(val), ha="center", va="center",
                    fontsize=11, fontweight="bold", color=text_color)

    # Add weighted total row below the heatmap
    for j, total in enumerate(d["totals"]):
        is_winner = (j == d["winner"])
        ax.text(j, n_crit + 0.15, f"{total:.2f}",
                ha="center", va="top",
                fontsize=10,
                fontweight="bold" if is_winner else "normal",
                color="#1b5e20" if is_winner else "#555555")

    # Highlight winner column
    w = d["winner"]
    rect = mpatches.FancyBboxPatch(
        (w - 0.48, -0.48), 0.96, n_crit - 0.04,
        boxstyle="round,pad=0.02",
        linewidth=2.5, edgecolor="#1b5e20", facecolor="none",
        zorder=5,
    )
    ax.add_patch(rect)

    # Mark winner with a star above the column
    ax.text(w, -0.72, "\u2605 SELECTED", ha="center", va="bottom",
            fontsize=8, fontweight="bold", color="#1b5e20")

    # Labels
    ax.set_xticks(range(n_alt))
    ax.set_xticklabels(d["alternatives"], fontsize=8.5, fontweight="bold")
    ax.xaxis.set_ticks_position("bottom")
    ax.set_yticks(range(n_crit))
    ax.set_yticklabels(criteria_labels, fontsize=7.5)
    ax.set_title(title, fontsize=11, fontweight="bold", pad=18)
    ax.tick_params(length=0)

    # Weighted-total label
    ax.text(-0.55, n_crit + 0.15, "Weighted\ntotal",
            ha="right", va="top", fontsize=7.5, fontstyle="italic",
            color="#555555")

# Colour bar
cbar_ax = fig.add_axes([0.25, 0.015, 0.50, 0.018])
cbar = fig.colorbar(
    plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(1, 5)),
    cax=cbar_ax, orientation="horizontal",
)
cbar.set_ticks([1, 2, 3, 4, 5])
cbar.set_ticklabels(["1 — Poor", "2", "3 — Average", "4", "5 — Excellent"])
cbar.ax.tick_params(labelsize=8)

# ── Save ────────────────────────────────────────────────────────────────

out_dir = pathlib.Path(__file__).parent
fig.savefig(out_dir / "mcda_heatmap.pdf", bbox_inches="tight", dpi=300)
fig.savefig(out_dir / "mcda_heatmap.png", bbox_inches="tight", dpi=300)
print(f"Saved: {out_dir / 'mcda_heatmap.pdf'}")
print(f"Saved: {out_dir / 'mcda_heatmap.png'}")
plt.close(fig)
