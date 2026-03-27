"""Generate N2 (Design Structure Matrix) diagram for search mission design variables."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os

# ── Variable definitions (processing order) ──────────────────────────────
labels = [
    "Target size",           # 0  fixed
    "Altitude h",            # 1  decision
    "Focal length f",        # 2  fixed
    "Ground\nfootprint",     # 3  derived
    "GSD",                   # 4  derived
    "Target\npixels",        # 5  derived
    "Speed v",               # 6  decision
    "Motion\nblur",          # 7  derived
    "Frames on\ntarget",     # 8  derived
    "Detection\nprobability",# 9  objective (maximize) GREEN
    "Scan angle",            # 10 decision
    "Lane\nspacing",         # 11 derived
    "Scan lines",            # 12 derived
    "Path length",           # 13 derived
    "Energy",                # 14 objective (minimize) RED
    "NFZ margin",            # 15 decision
    "Coverage %",            # 16 objective (maximize) GREEN
    "Mission\ntime",         # 17 objective (minimize) RED
]

short_labels = [
    "Target\nsize",
    "Altitude\nh",
    "Focal\nlength f",
    "Ground\nfootprint",
    "GSD",
    "Target\npixels",
    "Speed\nv",
    "Motion\nblur",
    "Frames\non target",
    "Detection\nprob.",
    "Scan\nangle \u03b8",
    "Lane\nspacing",
    "Scan\nlines",
    "Path\nlength",
    "Energy",
    "NFZ\nmargin",
    "Coverage\n%",
    "Mission\ntime",
]

N = len(labels)

# Diagonal colours
# blue=decision, grey=fixed, white=derived, green=max objective, red=min objective
BLUE   = "#4A90D9"
GREY   = "#B0B0B0"
WHITE  = "#FFFFFF"
GREEN  = "#5CB85C"
RED    = "#D9534F"

diag_colors = [
    GREY,   # 0  target size (fixed)
    BLUE,   # 1  altitude (decision)
    GREY,   # 2  focal length (fixed)
    WHITE,  # 3  footprint (derived)
    WHITE,  # 4  GSD (derived)
    WHITE,  # 5  target pixels (derived)
    BLUE,   # 6  speed (decision)
    WHITE,  # 7  motion blur (derived)
    WHITE,  # 8  frames on target (derived)
    GREEN,  # 9  detection probability (maximize)
    BLUE,   # 10 scan angle (decision)
    WHITE,  # 11 lane spacing (derived)
    WHITE,  # 12 scan lines (derived)
    WHITE,  # 13 path length (derived)
    RED,    # 14 energy (minimize)
    BLUE,   # 15 NFZ margin (decision)
    GREEN,  # 16 coverage (maximize)
    RED,    # 17 mission time (minimize)
]

# ── Dependency matrix ────────────────────────────────────────────────────
# dep[i][j] = True means variable i feeds INTO variable j
# i.e. row i provides data used by column j
# If j > i  → feedforward (above diagonal when viewed as row=source, col=dest)
# If j < i  → feedback (below diagonal)

dep = np.zeros((N, N), dtype=bool)

# Target size (0) feeds into: target pixels (5)
dep[0, 5] = True

# Altitude (1) feeds into: footprint (3), GSD (4), target pixels (5), speed (6)
dep[1, 3] = True
dep[1, 4] = True
dep[1, 5] = True
dep[1, 6] = True  # speed depends on altitude (altitude-dependent)

# Focal length (2) feeds into: footprint (3), GSD (4), target pixels (5)
dep[2, 3] = True
dep[2, 4] = True
dep[2, 5] = True

# Ground footprint (3) feeds into: frames on target (8), lane spacing (11)
dep[3, 8] = True
dep[3, 11] = True

# GSD (4) feeds into: motion blur (7)
dep[4, 7] = True

# Target pixels (5) feeds into: detection probability (9)
dep[5, 9] = True

# Speed (6) feeds into: motion blur (7), frames on target (8), energy (14), mission time (17)
dep[6, 7] = True
dep[6, 8] = True
dep[6, 14] = True
dep[6, 17] = True

# Motion blur (7) feeds into: detection probability (9)
dep[7, 9] = True

# Frames on target (8) feeds into: detection probability (9)
dep[8, 9] = True

# Detection probability (9) feeds back into: altitude (1) — feedback loop
dep[9, 1] = True   # FEEDBACK: if detection is poor, change altitude

# Scan angle (10) feeds into: scan lines (12), path length (13)
dep[10, 12] = True
dep[10, 13] = True

# Lane spacing (11) feeds into: scan lines (12), coverage (16)
dep[11, 12] = True
dep[11, 16] = True

# Scan lines (12) feeds into: path length (13), coverage (16)
dep[12, 13] = True
dep[12, 16] = True

# Path length (13) feeds into: energy (14), mission time (17)
dep[13, 14] = True
dep[13, 17] = True

# Energy (14) feeds back into: speed (6) — feedback: energy constraint limits speed
dep[14, 6] = True   # FEEDBACK

# NFZ margin (15) feeds into: coverage (16), scan lines (12)
dep[15, 16] = True
dep[15, 12] = True

# Coverage (16) feeds back into: scan angle (10) — feedback: adjust angle if coverage insufficient
dep[16, 10] = True  # FEEDBACK

# Mission time (17) feeds back into: speed (6) — feedback: adjust speed if time exceeds limit
dep[17, 6] = True   # FEEDBACK

# ── Plotting ─────────────────────────────────────────────────────────────
CELL = 0.62
fig_size = N * CELL + 2.5
fig, ax = plt.subplots(figsize=(fig_size, fig_size))

# Colours for off-diagonal marks
FEED_FWD = "#2C3E50"   # dark — feedforward (above diagonal from row perspective)
FEED_BACK = "#E74C3C"  # red  — feedback (below diagonal from row perspective)

for i in range(N):
    for j in range(N):
        x = j
        y = N - 1 - i   # flip so row 0 is at top

        if i == j:
            # Diagonal cell
            rect = mpatches.FancyBboxPatch(
                (x + 0.05, y + 0.05), 0.9, 0.9,
                boxstyle="round,pad=0.02",
                facecolor=diag_colors[i], edgecolor="#333333", linewidth=0.8
            )
            ax.add_patch(rect)
            txt_color = "white" if diag_colors[i] in (BLUE, RED, GREEN) else "#222222"
            ax.text(x + 0.5, y + 0.5, short_labels[i],
                    ha="center", va="center", fontsize=5.5, fontweight="bold",
                    color=txt_color, linespacing=1.1)
        else:
            # Off-diagonal: draw cell border lightly
            rect = mpatches.Rectangle(
                (x, y), 1, 1,
                facecolor="#FAFAFA", edgecolor="#DDDDDD", linewidth=0.3
            )
            ax.add_patch(rect)

            if dep[i, j]:
                # row i feeds column j
                # In N2 convention: above diagonal (j > i) = feedforward
                #                   below diagonal (j < i) = feedback
                if j > i:
                    color = FEED_FWD
                    marker_size = 6
                else:
                    color = FEED_BACK
                    marker_size = 7
                ax.plot(x + 0.5, y + 0.5, "o", color=color,
                        markersize=marker_size, markeredgecolor=color,
                        markeredgewidth=0.5)

# Grid lines on diagonal
for k in range(N + 1):
    ax.axhline(k, color="#AAAAAA", linewidth=0.4, zorder=0)
    ax.axvline(k, color="#AAAAAA", linewidth=0.4, zorder=0)

# Axis labels (variable numbers)
for i in range(N):
    # Top labels (column headers) — numbers
    ax.text(i + 0.5, N + 0.25, str(i + 1), ha="center", va="bottom",
            fontsize=6.5, fontweight="bold", color="#555555")
    # Left labels (row headers) — numbers
    ax.text(-0.25, N - 1 - i + 0.5, str(i + 1), ha="right", va="center",
            fontsize=6.5, fontweight="bold", color="#555555")

ax.set_xlim(-0.5, N)
ax.set_ylim(-0.5, N + 0.6)
ax.set_aspect("equal")
ax.axis("off")

# Title
ax.text(N / 2, N + 1.4,
        r"N$^2$ Dependency Diagram — Search Mission Design Variables",
        ha="center", va="center", fontsize=12, fontweight="bold")

# Legend (below the matrix)
legend_y = -1.8
legend_items = [
    (BLUE,  "Decision variable"),
    (GREY,  "Fixed / calibrated"),
    (WHITE, "Derived / computed"),
    (GREEN, "Objective (maximise)"),
    (RED,   "Objective (minimise)"),
]
spacing = N / (len(legend_items))
for idx, (col, label) in enumerate(legend_items):
    cx = idx * spacing + spacing / 2
    rect = mpatches.FancyBboxPatch(
        (cx - 0.35, legend_y - 0.25), 0.7, 0.5,
        boxstyle="round,pad=0.05",
        facecolor=col, edgecolor="#333333", linewidth=0.6
    )
    ax.add_patch(rect)
    ax.text(cx, legend_y - 0.65, label, ha="center", va="top",
            fontsize=6.5, color="#333333")

# Dot legend
dot_y = legend_y - 1.5
ax.plot(N / 2 - 2.5, dot_y, "o", color=FEED_FWD, markersize=6)
ax.text(N / 2 - 2.0, dot_y, "Feedforward", ha="left", va="center", fontsize=7, color="#333333")
ax.plot(N / 2 + 1.0, dot_y, "o", color=FEED_BACK, markersize=7)
ax.text(N / 2 + 1.5, dot_y, "Feedback", ha="left", va="center", fontsize=7, color="#333333")

# Variable key (compact, two columns)
key_y_start = legend_y - 2.5
ax.text(0, key_y_start, "Variable key:", fontsize=7, fontweight="bold", color="#333333")
key_labels_full = [
    "1. Target size (1.8 m)",
    "2. Altitude h",
    "3. Focal length (5.46 mm)",
    "4. Ground footprint",
    "5. GSD",
    "6. Target pixels",
    "7. Speed v",
    "8. Motion blur",
    "9. Frames on target",
    "10. Detection probability",
    "11. Scan angle \u03b8",
    "12. Lane spacing",
    "13. Scan lines",
    "14. Path length",
    "15. Energy",
    "16. NFZ margin",
    "17. Coverage %",
    "18. Mission time",
]
col1 = key_labels_full[:9]
col2 = key_labels_full[9:]
for idx, txt in enumerate(col1):
    ax.text(0.2, key_y_start - 0.55 - idx * 0.45, txt,
            fontsize=5.8, color="#555555", family="monospace")
for idx, txt in enumerate(col2):
    ax.text(N / 2 + 0.2, key_y_start - 0.55 - idx * 0.45, txt,
            fontsize=5.8, color="#555555", family="monospace")

ax.set_ylim(key_y_start - 5.0, N + 1.8)

plt.tight_layout()

out_dir = os.path.dirname(os.path.abspath(__file__))
plt.savefig(os.path.join(out_dir, "n2_diagram.pdf"), bbox_inches="tight", dpi=300)
plt.savefig(os.path.join(out_dir, "n2_diagram.png"), bbox_inches="tight", dpi=300)
print("Saved n2_diagram.pdf and n2_diagram.png")
