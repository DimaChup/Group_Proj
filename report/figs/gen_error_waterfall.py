#!/usr/bin/env python3
"""Generate error budget waterfall chart for GPS estimation accuracy."""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path

# ── Error sources (metres) ──────────────────────────────────────────────
#                          name,                   in-flight,  hover
# Hover values: GPS averaging reduces noise, timing lag = 0 (stationary),
# roll/pitch minimal in still air.  RSS targets: ~2.7 m flight, ~1.8 m hover.
sources = [
    ("GPS receiver\nnoise",          2.50, 1.50),   # averaging during hover
    ("Barometric\naltitude",         0.50, 0.50),
    ("GPS timing\nlag",              0.50, 0.00),   # stationary → zero
    ("Compass /\nyaw",               0.40, 0.40),
    ("Roll / pitch\n(compensated)",  0.30, 0.30),
    ("FOV\ncalibration",            0.20, 0.20),
    ("Lens\ndistortion",            0.10, 0.10),
    ("Detection\npixel",            0.05, 0.05),
]

names      = [s[0] for s in sources]
vals_fly   = np.array([s[1] for s in sources])
vals_hover = np.array([s[2] for s in sources])

rss_fly   = np.sqrt(np.sum(vals_fly**2))
rss_hover = np.sqrt(np.sum(vals_hover**2))

# ── Colour thresholds ──────────────────────────────────────────────────
def bar_color(v):
    if v >= 1.0:   return "#d62728"   # red   – dominant
    if v >= 0.3:   return "#ff7f0e"   # orange – medium
    return "#2ca02c"                   # green – small


# ── Figure ──────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 5.5))

n = len(names)
x = np.arange(n + 2)          # sources + 2 RSS totals
width = 0.62

# Cumulative bottom for the waterfall (stacked ascending)
cum = np.zeros(n)
for i in range(1, n):
    cum[i] = cum[i - 1] + vals_fly[i - 1]

# Draw individual source bars (floating)
for i in range(n):
    color = bar_color(vals_fly[i])
    ax.bar(x[i], vals_fly[i], width, bottom=cum[i], color=color,
           edgecolor="white", linewidth=0.6, zorder=3)
    # Value label
    cy = cum[i] + vals_fly[i] / 2
    ax.text(x[i], cy, f"{vals_fly[i]:.2f} m",
            ha="center", va="center", fontsize=8, fontweight="bold",
            color="white" if vals_fly[i] >= 0.3 else "black")

# Connector lines between bars
for i in range(n - 1):
    top = cum[i] + vals_fly[i]
    ax.plot([x[i] + width/2, x[i+1] - width/2], [top, top],
            color="#999999", linewidth=0.8, linestyle="--", zorder=2)

# ── RSS total bars ──────────────────────────────────────────────────────
rss_x_fly  = x[n]
rss_x_hov  = x[n + 1]

ax.bar(rss_x_fly,  rss_fly,  width, color="#1f77b4",
       edgecolor="white", linewidth=0.6, zorder=3)
ax.bar(rss_x_hov,  rss_hover, width, color="#17becf",
       edgecolor="white", linewidth=0.6, zorder=3)

ax.text(rss_x_fly, rss_fly / 2, f"{rss_fly:.2f} m",
        ha="center", va="center", fontsize=9, fontweight="bold", color="white")
ax.text(rss_x_hov, rss_hover / 2, f"{rss_hover:.2f} m",
        ha="center", va="center", fontsize=9, fontweight="bold", color="white")

# ── Axes & labels ───────────────────────────────────────────────────────
all_labels = names + ["In-flight\nRSS total", "Hover\nRSS total"]
ax.set_xticks(x)
ax.set_xticklabels(all_labels, fontsize=8)
ax.set_ylabel("Error contribution (m)", fontsize=10)
ax.set_title("GPS Estimation Error Budget — Waterfall Breakdown", fontsize=12,
             fontweight="bold", pad=12)

# y-axis
ax.set_ylim(0, cum[-1] + vals_fly[-1] + 0.3)
ax.yaxis.grid(True, linestyle=":", alpha=0.4, zorder=0)
ax.set_axisbelow(True)

# Legend
legend_patches = [
    mpatches.Patch(color="#d62728", label="Dominant  (>= 1.0 m)"),
    mpatches.Patch(color="#ff7f0e", label="Medium   (0.3 -- 1.0 m)"),
    mpatches.Patch(color="#2ca02c", label="Small     (< 0.3 m)"),
    mpatches.Patch(color="#1f77b4", label="In-flight RSS total"),
    mpatches.Patch(color="#17becf", label="Hover RSS total"),
]
ax.legend(handles=legend_patches, fontsize=8, loc="upper left",
          framealpha=0.9, edgecolor="#cccccc")

# Divider before RSS columns
ax.axvline(x[n] - 0.55, color="#bbbbbb", linewidth=0.8, linestyle="-", zorder=1)

# Annotation: RSS formula
ax.annotate(
    r"$\mathrm{RSS} = \sqrt{\sum \sigma_i^2}$",
    xy=(rss_x_fly, rss_fly + 0.05), xytext=(rss_x_fly - 0.3, rss_fly + 0.55),
    fontsize=9, ha="center",
    arrowprops=dict(arrowstyle="->", color="#555555", lw=0.8),
    bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#999999", alpha=0.9),
)

plt.tight_layout()

# ── Save ────────────────────────────────────────────────────────────────
out_dir = Path(__file__).parent
fig.savefig(out_dir / "error_waterfall.pdf", bbox_inches="tight")
fig.savefig(out_dir / "error_waterfall.png", bbox_inches="tight", dpi=200)
print(f"Saved error_waterfall.pdf and error_waterfall.png to {out_dir}")
plt.close(fig)
