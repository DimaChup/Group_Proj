"""Generate estimation approach comparison (bubble chart) and frame budget analysis."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

OUT = Path(__file__).parent

# ── Style ──────────────────────────────────────────────────────────────────
plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "DejaVu Serif"],
    "font.size": 9,
    "axes.labelsize": 10,
    "axes.titlesize": 11,
    "legend.fontsize": 8,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "axes.linewidth": 0.6,
    "xtick.major.width": 0.5,
    "ytick.major.width": 0.5,
})

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 4.8))

# ══════════════════════════════════════════════════════════════════════════
# Panel 1: Approach Comparison Bubble Chart
# ══════════════════════════════════════════════════════════════════════════

# Approaches: (name, compute 0-10, accuracy 0-10, complexity_bubble, color, label_offset)
approaches = [
    # Our approaches (green)
    ("Direct\nGeoreferencing",   1.5, 5.0,  250, "#2ca02c", ( 0.3,  0.4)),
    ("Hover-and-Lock",           2.0, 7.5,  300, "#2ca02c", ( 0.3,  0.0)),
    # Viable alternatives (blue)
    ("Kalman Filter",            4.5, 6.5,  500, "#3182bd", ( 0.3,  0.3)),
    ("Multi-frame\nTriangulation", 5.5, 8.0, 700, "#3182bd", ( 0.3, -0.9)),
    ("Template\nTracking",       4.0, 5.5,  500, "#3182bd", ( 0.3,  0.3)),
    # Not suitable (grey)
    ("Visual SLAM",              8.5, 9.0, 1000, "#888888", ( 0.3,  0.0)),
    ("Bundle\nAdjustment",       9.0, 9.2,  900, "#888888", (-3.0, -0.8)),
]

for name, x, y, size, color, (dx, dy) in approaches:
    alpha = 0.75 if color != "#888888" else 0.45
    edge = "#1a7a1a" if color == "#2ca02c" else ("#1f5f9e" if color == "#3182bd" else "#555555")
    ax1.scatter(x, y, s=size, c=color, alpha=alpha, edgecolors=edge,
                linewidths=1.0, zorder=5)
    ax1.annotate(name, (x, y), xytext=(x + dx, y + dy),
                 fontsize=7.5, ha="left", va="center",
                 arrowprops=dict(arrowstyle="-", color="#666666", lw=0.4)
                 if (abs(dx) > 0.5 or abs(dy) > 0.5) else None)

# Highlight our operating region
from matplotlib.patches import FancyBboxPatch
rect = FancyBboxPatch((0.5, 4.0), 2.5, 4.5, boxstyle="round,pad=0.3",
                       facecolor="#2ca02c", alpha=0.08, edgecolor="#2ca02c",
                       linestyle="--", linewidth=1.0, zorder=1)
ax1.add_patch(rect)
ax1.text(1.75, 4.3, "Our operating\nregion", fontsize=7, color="#1a7a1a",
         ha="center", va="bottom", fontstyle="italic")

# Legend bubbles for complexity
for s_val, label, ypos in [(250, "Low", 1.8), (550, "Medium", 1.2), (900, "High", 0.4)]:
    ax1.scatter(8.2, ypos, s=s_val, c="white", edgecolors="#666666", linewidths=0.6, zorder=5)
    ax1.text(9.1, ypos, label, fontsize=7, va="center")
ax1.text(8.6, 2.5, "Complexity", fontsize=7.5, ha="center", fontweight="bold")

# Category legend
from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], marker='o', color='w', markerfacecolor='#2ca02c',
           markersize=9, label='Our approach', markeredgecolor='#1a7a1a', markeredgewidth=0.8),
    Line2D([0], [0], marker='o', color='w', markerfacecolor='#3182bd',
           markersize=9, label='Viable alternative', markeredgecolor='#1f5f9e', markeredgewidth=0.8),
    Line2D([0], [0], marker='o', color='w', markerfacecolor='#888888',
           markersize=9, label='Not suitable (Pi 5)', markeredgecolor='#555555', markeredgewidth=0.8),
]
ax1.legend(handles=legend_elements, loc="upper left", frameon=True, framealpha=0.9,
           edgecolor="#cccccc", fontsize=7.5)

ax1.set_xlabel("Computational Cost")
ax1.set_ylabel("Geolocation Accuracy")
ax1.set_xlim(0, 10.5)
ax1.set_ylim(0, 10.5)
ax1.set_xticks([0, 2.5, 5, 7.5, 10])
ax1.set_xticklabels(["None", "Low", "Medium", "High", "Very High"], fontsize=7.5)
ax1.set_yticks([0, 2.5, 5, 7.5, 10])
ax1.set_yticklabels(["None", "Low", "Medium", "High", "Very High"], fontsize=7.5)
ax1.set_title("(a) Target Geolocation Approaches", fontweight="bold")
ax1.grid(True, alpha=0.2, linewidth=0.4)

# ══════════════════════════════════════════════════════════════════════════
# Panel 2: Frame Budget Analysis
# ══════════════════════════════════════════════════════════════════════════

speeds = np.linspace(1, 10, 200)
fov_width = 32.0  # metres at 35m altitude (54.4 deg HFOV)
fps_values = [2, 3, 5, 10, 15]
colors_fps = ["#d62728", "#e6820e", "#2ca02c", "#3182bd", "#7b4fbd"]

# Shade sufficient zone (>10 frames)
ax2.axhspan(10, 250, color="#2ca02c", alpha=0.06, zorder=0)
ax2.axhline(10, color="#2ca02c", ls="--", lw=0.8, alpha=0.5)
ax2.text(9.6, 11.5, "Sufficient (>10 frames)", fontsize=7, color="#2ca02c",
         ha="right", va="bottom", fontstyle="italic")

# Shade insufficient zone (<5 frames)
ax2.axhspan(0, 5, color="#d62728", alpha=0.04, zorder=0)
ax2.axhline(5, color="#d62728", ls=":", lw=0.6, alpha=0.4)
ax2.text(9.6, 3.8, "Insufficient (<5)", fontsize=6.5, color="#d62728",
         ha="right", va="top", fontstyle="italic")

for fps, color in zip(fps_values, colors_fps):
    # Time in FOV = fov_width / speed; frames = time * fps
    frames = (fov_width / speeds) * fps
    ax2.plot(speeds, frames, color=color, linewidth=1.5, label=f"{fps} FPS", zorder=4)

# Our operating point: 5 m/s, ~3 FPS
our_speed = 5.0
our_fps = 3.0
our_frames = (fov_width / our_speed) * our_fps  # 32/5 * 3 = 19.2
ax2.plot(our_speed, our_frames, marker="*", markersize=14, color="#2ca02c",
         markeredgecolor="black", markeredgewidth=0.8, zorder=10)
ax2.annotate(f"Our design point\n({our_speed:.0f} m/s, {our_fps:.0f} FPS, "
             f"{our_frames:.0f} frames)",
             xy=(our_speed, our_frames), xytext=(6.5, our_frames + 18),
             fontsize=7.5, ha="center", fontweight="bold", color="#1a7a1a",
             arrowprops=dict(arrowstyle="->", color="#1a7a1a", lw=1.0,
                             connectionstyle="arc3,rad=-0.2"))

# FOV annotation
ax2.annotate("", xy=(1.0, 150), xytext=(5.0, 150),
             arrowprops=dict(arrowstyle="<->", color="#555555", lw=0.8))
ax2.text(3.0, 155, f"FOV width = {fov_width:.0f} m\n(at 35 m altitude, 54.4\u00b0 HFOV)",
         fontsize=7, ha="center", va="bottom", color="#555555")

ax2.set_xlabel("Drone Speed (m/s)")
ax2.set_ylabel("Frames Available per Target Pass")
ax2.set_xlim(1, 10)
ax2.set_ylim(0, 170)
ax2.set_title("(b) Frame Budget vs. Speed", fontweight="bold")
ax2.legend(loc="upper right", frameon=True, framealpha=0.9, edgecolor="#cccccc",
           fontsize=7.5, title="Inference Rate", title_fontsize=8)
ax2.grid(True, alpha=0.2, linewidth=0.4)

# ── Save ───────────────────────────────────────────────────────────────────
fig.tight_layout(w_pad=2.5)
for ext in ("pdf", "png"):
    fig.savefig(OUT / f"estimation_comparison.{ext}", bbox_inches="tight")
print(f"Saved: {OUT / 'estimation_comparison.pdf'}")
print(f"Saved: {OUT / 'estimation_comparison.png'}")
plt.close(fig)
