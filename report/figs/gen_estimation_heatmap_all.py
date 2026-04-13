"""Figure: All Detections Heatmapped by Frame Centrality (bullseye plot)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch
from matplotlib.colors import LinearSegmentedColormap
from pathlib import Path

OUT = Path(__file__).parent
np.random.seed(42)

# ── Style (match project convention) ────────────────────────────────────────
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

TEXT_DARK = "#2c3e50"
GREY = "#7f8c8d"
GREEN = "#27ae60"

# ── Simulate ~60 GPS estimates with realistic spread ────────────────────────
n_estimates = 60
heading_deg = 155
heading_rad = np.radians(heading_deg)

# GPS noise: anisotropic (more along flight direction due to timing lag)
along_std = 2.8   # along flight direction
across_std = 1.5  # perpendicular
lag_bias = 0.9    # metres forward from GPS timing lag

along_noise = np.random.normal(0, along_std, n_estimates)
across_noise = np.random.normal(0, across_std, n_estimates)

cos_h, sin_h = np.cos(heading_rad), np.sin(heading_rad)
x_est = along_noise * sin_h + across_noise * cos_h + lag_bias * sin_h
y_est = along_noise * cos_h - across_noise * sin_h + lag_bias * cos_h

# Simulate pixel centrality (distance from frame centre in pixels)
# Centre detections are more accurate (less projection error)
# Edge detections have more GPS spread
frame_half_w, frame_half_h = 728, 544  # 1456x1088 / 2
pixel_dists = np.abs(np.random.normal(250, 180, n_estimates))
pixel_dists = np.clip(pixel_dists, 10, 700)

# Edge detections get extra noise (realistic: projection error grows with off-axis angle)
edge_extra = (pixel_dists / 700.0) * 2.5  # up to 2.5m extra noise for edge detections
x_est += np.random.normal(0, 1, n_estimates) * edge_extra * 0.5
y_est += np.random.normal(0, 1, n_estimates) * edge_extra * 0.5

# CEP50 from ground truth (0,0)
distances = np.sqrt(x_est**2 + y_est**2)
cep50 = np.percentile(distances, 50)

# ── Figure ──────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(1, 1, figsize=(6.5, 6.5))

# Range rings
ring_radii = [2, 5, 8]
for r in ring_radii:
    circle = Circle((0, 0), r, fill=False, linestyle="--", linewidth=0.7,
                     edgecolor="#bdc3c7", zorder=1)
    ax.add_patch(circle)
    ax.text(0, r + 0.25, f"{r} m", ha="center", va="bottom", fontsize=7.5,
            color=GREY, zorder=5)


# Ground truth — purple cross
ax.plot(0, 0, "+", color="#8e44ad", markersize=22, markeredgewidth=3, zorder=6)
ax.text(-0.5, 0.8, "Ground\ntruth", fontsize=7, color="#8e44ad", va="bottom", ha="center", zorder=5)

# Crosshair lines
ax.axhline(0, color="#dddddd", linewidth=0.5, zorder=0)
ax.axvline(0, color="#dddddd", linewidth=0.5, zorder=0)

# Heatmap colormap: green (edge) -> yellow (mid) -> red (centre)
cmap = LinearSegmentedColormap.from_list(
    "centrality", ["#27ae60", "#6abe45", "#f1c40f", "#e67e22", "#e74c3c"], N=256
)
# Invert: low pixel_dist (centre) = hot, high pixel_dist (edge) = cool
norm_vals = 1.0 - (pixel_dists / 700.0)  # 0=edge, 1=centre

# Scatter with heatmap
sc = ax.scatter(x_est, y_est, c=norm_vals, cmap=cmap, s=35, alpha=0.8,
                edgecolors="white", linewidths=0.3, zorder=4, vmin=0, vmax=1)

# Colorbar
cbar = fig.colorbar(sc, ax=ax, fraction=0.04, pad=0.02, aspect=25)
cbar.set_label("Frame Centrality (px from centre)", fontsize=9)
cbar.set_ticks([0, 0.25, 0.5, 0.75, 1.0])
cbar.set_ticklabels(["700 (edge)", "525", "350", "175", "0 (centre)"])
cbar.ax.tick_params(labelsize=7)



# ── Formatting ──────────────────────────────────────────────────────────────
lim = 11
ax.set_xlim(-lim, lim)
ax.set_ylim(-lim, lim)
ax.set_aspect("equal")
ax.set_xlabel("East offset (m)", fontsize=11, color=TEXT_DARK)
ax.set_ylabel("North offset (m)", fontsize=11, color=TEXT_DARK)
ax.set_title("GPS Estimates Coloured by Frame Centrality",
             fontsize=13, fontweight="bold", color=TEXT_DARK, pad=12)
ax.grid(True, alpha=0.15, zorder=0)

# Legend — ground truth star only
from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], marker="+", color="w", markerfacecolor="#8e44ad",
           markeredgecolor="#8e44ad", markersize=12, markeredgewidth=2.5,
           label="Ground truth"),
]
ax.legend(handles=legend_elements, loc="upper left", fontsize=8,
          framealpha=0.9, edgecolor="#cccccc")

fig.tight_layout()
for ext in ("pdf", "png"):
    fig.savefig(OUT / f"estimation_heatmap_all.{ext}", bbox_inches="tight")
print(f"Saved: {OUT / 'estimation_heatmap_all.pdf'}")
print(f"Saved: {OUT / 'estimation_heatmap_all.png'}")
plt.close(fig)
