#!/usr/bin/env python3
"""Generate four-phase detection accuracy progression figure.

Shows how CEP50 improves through the mission phases:
  1. In-flight detection (3.5m) -> 2. Approach (2.5m) ->
  3. Hover lock (1.8m) -> 4. Verify (0.5m confirmed)

Visual: stepped descent with concentric CEP circles, colour gradient,
and annotated improvement factors.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import matplotlib.patheffects as pe
import numpy as np
from pathlib import Path

OUT = Path(__file__).parent

# ── Phase data ─────────────────────────────────────────────────────────
phases = [
    {
        "name": "IN-FLIGHT\nDETECTION",
        "cep": 3.5,
        "alt": "30 m AGL",
        "factor": "Tilt compensation",
        "detail": "Moving at 5 m/s\nOblique camera angle",
        "color": "#d62728",       # red
        "color_light": "#fee0d2",
    },
    {
        "name": "APPROACH",
        "cep": 2.5,
        "alt": "20 m AGL",
        "factor": "Closer range",
        "detail": "Reduced speed\nSmaller GSD",
        "color": "#e6820e",       # orange
        "color_light": "#fde0b5",
    },
    {
        "name": "HOVER LOCK",
        "cep": 1.8,
        "alt": "15 m AGL",
        "factor": "GPS averaging",
        "detail": "Stationary hover\nNadir geometry",
        "color": "#f0c800",       # gold-yellow
        "color_light": "#fff9c4",
    },
    {
        "name": "VERIFY",
        "cep": 0.5,
        "alt": "10 m AGL",
        "factor": "Human confirmation",
        "detail": "Operator visual check\nFinal lock",
        "color": "#2ca02c",       # green
        "color_light": "#c7e9c0",
    },
]

# ── Layout constants ───────────────────────────────────────────────────
fig = plt.figure(figsize=(11, 6.5))

# Two-panel layout: left = stepped diagram, right = bullseye comparison
gs = fig.add_gridspec(1, 2, width_ratios=[3, 2], wspace=0.05)
ax_left = fig.add_subplot(gs[0])
ax_right = fig.add_subplot(gs[1])

# =====================================================================
# LEFT PANEL — Stepped descent with info cards
# =====================================================================
n = len(phases)
step_h = 1.0        # vertical spacing between steps
card_w = 2.8
card_h = 0.72

# Y positions (descending)
y_positions = [3.2 - i * step_h for i in range(n)]
x_left_edge = 0.2
x_card = x_left_edge + 0.1

ax_left.set_xlim(-0.3, 4.8)
ax_left.set_ylim(-0.5, 4.2)
ax_left.set_aspect("equal")
ax_left.axis("off")

# Title
ax_left.text(2.3, 4.0, "Four-Phase Accuracy Progression",
             fontsize=14, fontweight="bold", ha="center", va="center",
             color="#222222")

# Draw downward arrow spine
arrow_x = 0.0
ax_left.annotate("", xy=(arrow_x, y_positions[-1] - 0.35),
                 xytext=(arrow_x, y_positions[0] + 0.35),
                 arrowprops=dict(arrowstyle="->, head_width=0.25, head_length=0.15",
                                 color="#888888", lw=2.0))
ax_left.text(arrow_x, y_positions[0] + 0.50, "Mission\nprogress",
             ha="center", va="bottom", fontsize=7, color="#888888",
             fontstyle="italic")

for i, (phase, y) in enumerate(zip(phases, y_positions)):
    # ── Phase number circle ──
    circle = plt.Circle((arrow_x, y), 0.18, color=phase["color"],
                         ec="white", lw=2, zorder=5)
    ax_left.add_patch(circle)
    ax_left.text(arrow_x, y, str(i + 1), ha="center", va="center",
                 fontsize=11, fontweight="bold", color="white", zorder=6)

    # ── Info card (rounded box) ──
    card = FancyBboxPatch((x_card, y - card_h / 2), card_w, card_h,
                          boxstyle="round,pad=0.08",
                          facecolor=phase["color_light"],
                          edgecolor=phase["color"], linewidth=1.5,
                          zorder=3)
    ax_left.add_patch(card)

    # Phase name (bold)
    ax_left.text(x_card + 0.15, y + 0.18, phase["name"],
                 fontsize=9, fontweight="bold", color=phase["color"],
                 va="center", ha="left", linespacing=0.85, zorder=4)

    # CEP50 value (large, right-aligned in card)
    ax_left.text(x_card + card_w - 0.15, y + 0.15,
                 f"{phase['cep']:.1f} m",
                 fontsize=16, fontweight="bold", color=phase["color"],
                 va="center", ha="right", zorder=4,
                 path_effects=[pe.withStroke(linewidth=2, foreground="white")])
    ax_left.text(x_card + card_w - 0.15, y - 0.05,
                 "CEP50", fontsize=7, color="#666666",
                 va="center", ha="right", zorder=4)

    # Improvement factor tag
    ax_left.text(x_card + 0.15, y - 0.18, phase["factor"],
                 fontsize=7.5, color="#444444", fontstyle="italic",
                 va="center", ha="left", zorder=4)

    # ── Connector from arrow to card ──
    ax_left.plot([arrow_x + 0.18, x_card], [y, y],
                 color=phase["color"], lw=1.2, ls="--", alpha=0.6, zorder=2)

    # ── Altitude label (small, right of card) ──
    ax_left.text(x_card + card_w + 0.12, y,
                 phase["alt"], fontsize=7, color="#777777",
                 va="center", ha="left")

# Improvement arrows between phases
for i in range(n - 1):
    y_top = y_positions[i] - card_h / 2 - 0.04
    y_bot = y_positions[i + 1] + card_h / 2 + 0.04
    mid_y = (y_top + y_bot) / 2
    cep_before = phases[i]["cep"]
    cep_after = phases[i + 1]["cep"]
    improvement = ((cep_before - cep_after) / cep_before) * 100

    ax_left.annotate("",
                     xy=(x_card + card_w / 2, y_bot),
                     xytext=(x_card + card_w / 2, y_top),
                     arrowprops=dict(arrowstyle="->", color="#888888",
                                     lw=1.0, ls="--"))
    ax_left.text(x_card + card_w / 2 + 0.55, mid_y,
                 f"-{improvement:.0f}%",
                 fontsize=8, fontweight="bold", color="#555555",
                 ha="left", va="center",
                 bbox=dict(boxstyle="round,pad=0.15", fc="white",
                           ec="#cccccc", alpha=0.85))

# =====================================================================
# RIGHT PANEL — Concentric CEP circles (bullseye)
# =====================================================================
ax_right.set_xlim(-5, 5)
ax_right.set_ylim(-5, 5)
ax_right.set_aspect("equal")
ax_right.axis("off")

ax_right.text(0, 4.6, "CEP50 Comparison",
              fontsize=12, fontweight="bold", ha="center", color="#222222")

# Draw concentric circles from largest to smallest
for phase in phases:
    r = phase["cep"]
    circle = plt.Circle((0, 0), r, facecolor=phase["color_light"],
                         edgecolor=phase["color"], linewidth=1.8,
                         alpha=0.55, zorder=2 + (4 - r))
    ax_right.add_patch(circle)

# Labels on circles — angles chosen to avoid overlap
label_angles = [30, 330, 150, 210]  # degrees, well separated
for phase, angle_deg in zip(phases, label_angles):
    r = phase["cep"]
    angle = np.radians(angle_deg)
    # Label at the edge of circle
    lx = r * np.cos(angle)
    ly = r * np.sin(angle)
    # Arrow target slightly inside
    tx = (r - 0.15) * np.cos(angle)
    ty = (r - 0.15) * np.sin(angle)
    # Text anchor outside
    offset = 0.6
    ox = (r + offset) * np.cos(angle)
    oy = (r + offset) * np.sin(angle)

    ha = "left" if np.cos(angle) >= 0 else "right"
    va = "bottom" if np.sin(angle) >= 0 else "top"

    ax_right.annotate(
        f"{phase['cep']:.1f} m",
        xy=(tx, ty), xytext=(ox, oy),
        fontsize=9, fontweight="bold", color=phase["color"],
        ha=ha, va=va,
        arrowprops=dict(arrowstyle="-", color=phase["color"],
                        lw=1.0, shrinkA=0, shrinkB=2),
        bbox=dict(boxstyle="round,pad=0.2", fc="white",
                  ec=phase["color"], alpha=0.9, lw=0.8),
        zorder=10,
    )

# Cross-hair at centre
for lw, alpha in [(1.5, 0.15), (0.5, 0.4)]:
    ax_right.axhline(0, color="black", lw=lw, alpha=alpha, zorder=1)
    ax_right.axvline(0, color="black", lw=lw, alpha=alpha, zorder=1)

# Small target dot
ax_right.plot(0, 0, "k+", markersize=12, markeredgewidth=1.5, zorder=11)
ax_right.text(0.2, -0.35, "Target", fontsize=7, color="#555555",
              ha="left", va="top", fontstyle="italic")

# Scale bar
ax_right.plot([-3.5, -2.5], [-4.4, -4.4], color="black", lw=2, zorder=10)
ax_right.text(-3.0, -4.6, "1 m", fontsize=8, ha="center", va="top",
              color="#333333")

# Legend (bottom right of bullseye)
legend_items = []
for phase in phases:
    legend_items.append(
        mpatches.Patch(facecolor=phase["color_light"],
                       edgecolor=phase["color"], linewidth=1.2,
                       label=phase["name"].replace("\n", " "))
    )
ax_right.legend(handles=legend_items, loc="lower right", fontsize=7.5,
                framealpha=0.9, edgecolor="#cccccc",
                bbox_to_anchor=(1.05, -0.02))

# ── Overall title ──────────────────────────────────────────────────────
fig.suptitle("", fontsize=1)  # placeholder — titles are in panels

plt.tight_layout(rect=[0, 0, 1, 0.97])

# ── Save ───────────────────────────────────────────────────────────────
fig.savefig(OUT / "four_phase_accuracy.pdf", bbox_inches="tight")
fig.savefig(OUT / "four_phase_accuracy.png", bbox_inches="tight", dpi=250)
plt.close(fig)
print(f"Saved four_phase_accuracy.pdf and four_phase_accuracy.png to {OUT}")
