"""Figure: Estimation Error vs Detection Count for Different Aggregation Methods."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D
from pathlib import Path

OUT = Path(__file__).parent
np.random.seed(42)

# ── Style ────────────────────────────────────────────────────────────────────
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

# ── Generate base pool of ~60 GPS estimates (same model as other figures) ───
n_pool = 60
heading_rad = np.radians(155)
along_std, across_std = 2.8, 1.5
lag_bias = 0.9

along_noise = np.random.normal(0, along_std, n_pool)
across_noise = np.random.normal(0, across_std, n_pool)
cos_h, sin_h = np.cos(heading_rad), np.sin(heading_rad)

x_pool = along_noise * sin_h + across_noise * cos_h + lag_bias * sin_h
y_pool = along_noise * cos_h - across_noise * sin_h + lag_bias * cos_h

# Pixel centrality per estimate
pixel_dists = np.abs(np.random.normal(250, 180, n_pool))
pixel_dists = np.clip(pixel_dists, 10, 700)
edge_extra = (pixel_dists / 700.0) * 2.5
x_pool += np.random.normal(0, 1, n_pool) * edge_extra * 0.5
y_pool += np.random.normal(0, 1, n_pool) * edge_extra * 0.5

# Confidence per estimate (higher for centre detections)
confidences = 0.95 - 0.3 * (pixel_dists / 700.0) + np.random.normal(0, 0.05, n_pool)
confidences = np.clip(confidences, 0.4, 0.99)

# ── Compute errors for each method at each N, 5 trials ─────────────────────
N_values = list(range(1, 26))
n_trials = 5

methods = {
    "Simple mean": {"color": "#d62728", "marker": "o"},
    "IVW":         {"color": "#3182bd", "marker": "s"},
    "IVW + centre bonus": {"color": "#2ca02c", "marker": "D"},
    "Median":      {"color": "#7b4fbd", "marker": "^"},
}

results = {name: {"N": [], "errors": [], "confs": []} for name in methods}

rng = np.random.RandomState(42)

for N in N_values:
    for trial in range(n_trials):
        # Sample N estimates from the pool
        indices = rng.choice(n_pool, size=min(N, n_pool), replace=False)
        xs = x_pool[indices]
        ys = y_pool[indices]
        pds = pixel_dists[indices]
        cfs = confidences[indices]

        mean_conf = np.mean(cfs)

        # 1. Simple mean
        sx, sy = np.mean(xs), np.mean(ys)
        err = np.sqrt(sx**2 + sy**2)
        results["Simple mean"]["N"].append(N)
        results["Simple mean"]["errors"].append(err)
        results["Simple mean"]["confs"].append(mean_conf)

        # 2. Inverse Variance Weighting (weight = 1/sigma^2, sigma ~ pixel_dist)
        sigmas = np.maximum(pds, 10.0)
        weights = 1.0 / (sigmas**2)
        weights /= weights.sum()
        wx, wy = np.sum(xs * weights), np.sum(ys * weights)
        err = np.sqrt(wx**2 + wy**2)
        results["IVW"]["N"].append(N)
        results["IVW"]["errors"].append(err)
        results["IVW"]["confs"].append(mean_conf)

        # 3. IVW + centre bonus (extra weight for detections near frame centre)
        centre_bonus = np.exp(-pds / 200.0)  # exponential boost for centre detections
        weights2 = (1.0 / (sigmas**2)) * (1.0 + 2.0 * centre_bonus)
        weights2 /= weights2.sum()
        cx, cy = np.sum(xs * weights2), np.sum(ys * weights2)
        err = np.sqrt(cx**2 + cy**2)
        results["IVW + centre bonus"]["N"].append(N)
        results["IVW + centre bonus"]["errors"].append(err)
        results["IVW + centre bonus"]["confs"].append(mean_conf)

        # 4. Median
        mx, my = np.median(xs), np.median(ys)
        err = np.sqrt(mx**2 + my**2)
        results["Median"]["N"].append(N)
        results["Median"]["errors"].append(err)
        results["Median"]["confs"].append(mean_conf)

# ── Figure ──────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(1, 1, figsize=(8, 5.5))

# Reliable operating zone (shaded green: N>=10 AND error<2m)
rect = Rectangle((10, 0), 15, 2, facecolor="#2ca02c", alpha=0.07, zorder=0)
ax.add_patch(rect)
ax.text(17.5, 0.15, "Reliable operating zone", fontsize=7.5, color="#1a7a1a",
        ha="center", va="bottom", fontstyle="italic", zorder=1)

# Threshold lines
ax.axhline(2.0, color="#2ca02c", ls="--", lw=1.0, alpha=0.6, zorder=1)
ax.text(25.3, 2.05, "Actionable\naccuracy (2 m)", fontsize=7, color="#2ca02c",
        va="bottom", ha="left", zorder=1)

ax.axvline(10, color="#3182bd", ls=":", lw=1.0, alpha=0.5, zorder=1)

# Plot each method
for name, props in methods.items():
    data = results[name]
    N_arr = np.array(data["N"])
    err_arr = np.array(data["errors"])
    conf_arr = np.array(data["confs"])

    # Scatter individual trials (heatmapped by confidence)
    norm_conf = (conf_arr - conf_arr.min()) / max(conf_arr.max() - conf_arr.min(), 0.01)
    # Use method color with varying alpha for confidence
    rgba = np.zeros((len(N_arr), 4))
    base_rgb = plt.cm.colors.to_rgb(props["color"])
    rgba[:, 0] = base_rgb[0]
    rgba[:, 1] = base_rgb[1]
    rgba[:, 2] = base_rgb[2]
    rgba[:, 3] = 0.25 + 0.55 * norm_conf  # alpha range 0.25-0.8

    ax.scatter(N_arr, err_arr, c=rgba, s=20, marker=props["marker"],
               edgecolors="none", zorder=4)

    # Median line through trials
    median_errors = []
    for N in N_values:
        mask = N_arr == N
        median_errors.append(np.median(err_arr[mask]))

    ax.plot(N_values, median_errors, color=props["color"], linewidth=1.8,
            alpha=0.85, zorder=5, label=name)

# Fix the SMART threshold text position after axis limits are set
ax.set_xlim(0.5, 25.5)
ax.set_ylim(0, 9)
ax.text(10.2, 8.5, "SMART\nthreshold", fontsize=7, color="#3182bd",
        va="top", ha="left", zorder=6)

# ── Formatting ──────────────────────────────────────────────────────────────
ax.set_xlabel("Number of Detections Used", fontsize=11, color=TEXT_DARK)
ax.set_ylabel("Error from Ground Truth (m)", fontsize=11, color=TEXT_DARK)
ax.set_title("Estimation Error vs. Detection Count by Aggregation Method",
             fontsize=12, fontweight="bold", color=TEXT_DARK, pad=12)
ax.grid(True, alpha=0.15, zorder=0)

# Legend
legend_elements = [
    Line2D([0], [0], color="#d62728", marker="o", markersize=5, lw=1.8,
           label="Simple mean"),
    Line2D([0], [0], color="#3182bd", marker="s", markersize=5, lw=1.8,
           label="Inverse variance weighting"),
    Line2D([0], [0], color="#2ca02c", marker="D", markersize=5, lw=1.8,
           label="IVW + centre bonus"),
    Line2D([0], [0], color="#7b4fbd", marker="^", markersize=5, lw=1.8,
           label="Median"),
]
ax.legend(handles=legend_elements, loc="upper right", fontsize=8,
          framealpha=0.9, edgecolor="#cccccc")

# Note about scatter opacity
ax.text(0.02, 0.02, "Dot opacity indicates estimate confidence\n(darker = higher confidence)",
        transform=ax.transAxes, fontsize=7, color=GREY, va="bottom", ha="left",
        fontstyle="italic")

fig.tight_layout()
for ext in ("pdf", "png"):
    fig.savefig(OUT / f"estimation_error_vs_detections.{ext}", bbox_inches="tight")
print(f"Saved: {OUT / 'estimation_error_vs_detections.pdf'}")
print(f"Saved: {OUT / 'estimation_error_vs_detections.png'}")
plt.close(fig)
