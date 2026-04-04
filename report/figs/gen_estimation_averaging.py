"""Figure: Running Average Convergence (2 panels) — All Estimates vs SMART Lock."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle
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
GREEN = "#27ae60"

# ── Simulate ~60 GPS estimates (same data as heatmap figure) ────────────────
n_estimates = 60
heading_rad = np.radians(155)
along_std, across_std = 2.8, 1.5
lag_bias = 0.9

along_noise = np.random.normal(0, along_std, n_estimates)
across_noise = np.random.normal(0, across_std, n_estimates)
cos_h, sin_h = np.cos(heading_rad), np.sin(heading_rad)

x_est = along_noise * sin_h + across_noise * cos_h + lag_bias * sin_h
y_est = along_noise * cos_h - across_noise * sin_h + lag_bias * cos_h

# Pixel centrality
pixel_dists = np.abs(np.random.normal(250, 180, n_estimates))
pixel_dists = np.clip(pixel_dists, 10, 700)
edge_extra = (pixel_dists / 700.0) * 2.5
x_est += np.random.normal(0, 1, n_estimates) * edge_extra * 0.5
y_est += np.random.normal(0, 1, n_estimates) * edge_extra * 0.5

# ── Running average positions ───────────────────────────────────────────────
milestones = [1, 3, 5, 8, 10, 15, 20, 30, 45, 60]
milestones = [m for m in milestones if m <= n_estimates]

running_x = []
running_y = []
for m in milestones:
    running_x.append(np.mean(x_est[:m]))
    running_y.append(np.mean(y_est[:m]))

# ── SMART cluster: find tightest 10 points ──────────────────────────────────
from itertools import combinations

def find_tightest_cluster(x, y, k=10):
    """Find the k points with smallest max pairwise distance."""
    n = len(x)
    if n <= k:
        return np.arange(n)
    # Greedy: start with closest pair, add point minimising max spread
    dists = np.sqrt((x[:, None] - x[None, :])**2 + (y[:, None] - y[None, :])**2)
    # Find closest pair
    np.fill_diagonal(dists, np.inf)
    i, j = np.unravel_index(np.argmin(dists), dists.shape)
    cluster = [i, j]
    remaining = set(range(n)) - {i, j}
    while len(cluster) < k:
        best_idx = None
        best_spread = np.inf
        for r in remaining:
            trial = cluster + [r]
            spread = max(dists[a, b] for a in trial for b in trial if a != b)
            if spread < best_spread:
                best_spread = spread
                best_idx = r
        cluster.append(best_idx)
        remaining.remove(best_idx)
    return np.array(cluster)

smart_k = 10
smart_indices = find_tightest_cluster(x_est, y_est, smart_k)
smart_x = x_est[smart_indices]
smart_y = y_est[smart_indices]
smart_centroid_x = np.median(smart_x)
smart_centroid_y = np.median(smart_y)
smart_spread = max(np.sqrt((smart_x[i] - smart_x[j])**2 + (smart_y[i] - smart_y[j])**2)
                   for i in range(len(smart_x)) for j in range(len(smart_x)) if i != j)
smart_dists = np.sqrt((smart_x - smart_centroid_x)**2 + (smart_y - smart_centroid_y)**2)
smart_cep50 = np.percentile(smart_dists, 50)

# All-estimate CEP50
all_dists = np.sqrt(x_est**2 + y_est**2)
all_cep50 = np.percentile(all_dists, 50)

# Final running average CEP50
final_rx, final_ry = running_x[-1], running_y[-1]
final_err = np.sqrt(final_rx**2 + final_ry**2)

# ── Figure: 2 panels ────────────────────────────────────────────────────────
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.8))

# ══════════════════════════════════════════════════════════════════════════════
# Panel A: All Individual Estimates + Running Average Path
# ══════════════════════════════════════════════════════════════════════════════
lim_a = 10

# Range rings
for r in [2, 5, 8]:
    ax1.add_patch(Circle((0, 0), r, fill=False, ls="--", lw=0.7,
                          edgecolor="#bdc3c7", zorder=1))
    ax1.text(0, r + 0.2, f"{r} m", ha="center", va="bottom", fontsize=7, color=GREY)

# Grey individual estimates
ax1.scatter(x_est, y_est, c="#cccccc", s=18, alpha=0.5, edgecolors="#aaaaaa",
            linewidths=0.2, zorder=2, label=f"Individual estimates (N={n_estimates})")

# Ground truth
ax1.plot(0, 0, "+", color=GREEN, markersize=20, markeredgewidth=3, zorder=8)
ax1.axhline(0, color="#dddddd", lw=0.5, zorder=0)
ax1.axvline(0, color="#dddddd", lw=0.5, zorder=0)

# Running average path
ax1.plot(running_x, running_y, "-", color="#555555", linewidth=1.0, alpha=0.6, zorder=5)

# Milestone dots with gradient: red (early) -> green (converged)
cmap_conv = plt.cm.RdYlGn
for i, (mx, my, m) in enumerate(zip(running_x, running_y, milestones)):
    frac = i / max(len(milestones) - 1, 1)
    color = cmap_conv(frac)
    size = 80 if i == 0 else (60 if i < 3 else (45 if i < 6 else 35))
    if i == len(milestones) - 1:
        size = 90
        color = "#27ae60"
    ax1.scatter(mx, my, c=[color], s=size, edgecolors="black", linewidths=0.6,
                zorder=7)
    # Label key milestones
    if m in [1, 5, 10, 15, 60] or m == milestones[-1]:
        err = np.sqrt(mx**2 + my**2)
        offset_x = 0.4 if mx >= 0 else -0.4
        offset_y = 0.4
        ha = "left" if mx >= 0 else "right"
        ax1.annotate(f"N={m}\n({err:.1f} m)",
                     xy=(mx, my), xytext=(mx + offset_x, my + offset_y),
                     fontsize=6.5, ha=ha, color=TEXT_DARK, zorder=9,
                     arrowprops=dict(arrowstyle="-", color="#888888", lw=0.4))

# CEP50 for final running average (from ground truth)
final_dists_from_centroid = np.sqrt((x_est - final_rx)**2 + (y_est - final_ry)**2)
ax1.add_patch(Circle((0, 0), all_cep50, fill=False, ls="-", lw=1.8,
                      edgecolor="#e67e22", zorder=3, label=f"CEP50 = {all_cep50:.1f} m"))

ax1.set_xlim(-lim_a, lim_a)
ax1.set_ylim(-lim_a, lim_a)
ax1.set_aspect("equal")
ax1.set_xlabel("East offset (m)", color=TEXT_DARK)
ax1.set_ylabel("North offset (m)", color=TEXT_DARK)
ax1.set_title("(a) Running Average Convergence", fontweight="bold", color=TEXT_DARK)
ax1.grid(True, alpha=0.15, zorder=0)

legend_a = [
    Line2D([0], [0], marker="o", color="w", markerfacecolor="#cccccc",
           markersize=6, label=f"All estimates (N={n_estimates})"),
    Line2D([0], [0], marker="o", color="w", markerfacecolor="#d62728",
           markeredgecolor="k", markeredgewidth=0.5, markersize=8,
           label="Early average (noisy)"),
    Line2D([0], [0], marker="o", color="w", markerfacecolor="#27ae60",
           markeredgecolor="k", markeredgewidth=0.5, markersize=8,
           label="Converged average"),
    Line2D([0], [0], marker="+", color="w", markeredgecolor=GREEN,
           markersize=12, markeredgewidth=2.5, label="Ground truth"),
    Line2D([0], [0], ls="-", color="#e67e22", lw=1.8,
           label=f"CEP50 = {all_cep50:.1f} m"),
]
ax1.legend(handles=legend_a, loc="upper left", fontsize=7, framealpha=0.9,
           edgecolor="#cccccc")

# ══════════════════════════════════════════════════════════════════════════════
# Panel B: SMART Locked Cluster
# ══════════════════════════════════════════════════════════════════════════════
lim_b = 6

# Range rings
for r in [1, 2, 4]:
    ax2.add_patch(Circle((0, 0), r, fill=False, ls="--", lw=0.7,
                          edgecolor="#bdc3c7", zorder=1))
    ax2.text(0, r + 0.1, f"{r} m", ha="center", va="bottom", fontsize=7, color=GREY)

# Ground truth
ax2.plot(0, 0, "+", color=GREEN, markersize=20, markeredgewidth=3, zorder=8)
ax2.axhline(0, color="#dddddd", lw=0.5, zorder=0)
ax2.axvline(0, color="#dddddd", lw=0.5, zorder=0)

# Grey rejected outliers
rejected_mask = np.ones(n_estimates, dtype=bool)
rejected_mask[smart_indices] = False
ax2.scatter(x_est[rejected_mask], y_est[rejected_mask], c="#dddddd", s=15,
            alpha=0.35, edgecolors="#bbbbbb", linewidths=0.2, zorder=2,
            label=f"Rejected ({n_estimates - smart_k})")

# SMART cluster points (bold coloured)
sc_colors = plt.cm.viridis(np.linspace(0.2, 0.9, smart_k))
ax2.scatter(smart_x, smart_y, c=sc_colors, s=55, edgecolors="black",
            linewidths=0.6, zorder=6, label=f"SMART cluster (N={smart_k})")

# SMART cluster circle (max spread radius from centroid)
cluster_radius = smart_spread / 2
ax2.add_patch(Circle((smart_centroid_x, smart_centroid_y), cluster_radius,
                      fill=True, facecolor="#3182bd", alpha=0.08,
                      edgecolor="#3182bd", ls="-", lw=1.5, zorder=3))

# CEP50 for SMART
ax2.add_patch(Circle((0, 0), smart_cep50, fill=False, ls="-", lw=1.8,
                      edgecolor="#e67e22", zorder=4))

# SMART centroid star
ax2.plot(smart_centroid_x, smart_centroid_y, "*", color="#c0392b",
         markersize=18, markeredgewidth=0.5, zorder=9)

# Label
centroid_err = np.sqrt(smart_centroid_x**2 + smart_centroid_y**2)
ax2.text(smart_centroid_x + 0.3, smart_centroid_y - 0.3,
         f"SMART centroid\nerror = {centroid_err:.1f} m",
         fontsize=7, color="#c0392b", zorder=9)

# Info box
info_text = (f"SMART lock: {smart_k} samples\n"
             f"Spread = {smart_spread:.1f} m\n"
             f"CEP50 = {smart_cep50:.1f} m")
ax2.text(0.97, 0.03, info_text, transform=ax2.transAxes, fontsize=7.5,
         va="bottom", ha="right", color=TEXT_DARK,
         bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
                   edgecolor="#cccccc", alpha=0.9), zorder=10)

ax2.set_xlim(-lim_b, lim_b)
ax2.set_ylim(-lim_b, lim_b)
ax2.set_aspect("equal")
ax2.set_xlabel("East offset (m)", color=TEXT_DARK)
ax2.set_ylabel("North offset (m)", color=TEXT_DARK)
ax2.set_title("(b) SMART Tightest-Cluster Lock", fontweight="bold", color=TEXT_DARK)
ax2.grid(True, alpha=0.15, zorder=0)

legend_b = [
    Line2D([0], [0], marker="o", color="w", markerfacecolor="#dddddd",
           markersize=6, label=f"Rejected outliers ({n_estimates - smart_k})"),
    Line2D([0], [0], marker="o", color="w", markerfacecolor="#3182bd",
           markeredgecolor="k", markeredgewidth=0.5, markersize=8,
           label=f"SMART cluster (N={smart_k})"),
    Line2D([0], [0], marker="*", color="w", markerfacecolor="#c0392b",
           markersize=12, label="SMART centroid"),
    Line2D([0], [0], marker="+", color="w", markeredgecolor=GREEN,
           markersize=12, markeredgewidth=2.5, label="Ground truth"),
    Line2D([0], [0], ls="-", color="#e67e22", lw=1.8,
           label=f"CEP50 = {smart_cep50:.1f} m"),
]
ax2.legend(handles=legend_b, loc="upper left", fontsize=7, framealpha=0.9,
           edgecolor="#cccccc")

fig.tight_layout(w_pad=2.0)
for ext in ("pdf", "png"):
    fig.savefig(OUT / f"estimation_averaging.{ext}", bbox_inches="tight")
print(f"Saved: {OUT / 'estimation_averaging.pdf'}")
print(f"Saved: {OUT / 'estimation_averaging.png'}")
plt.close(fig)
