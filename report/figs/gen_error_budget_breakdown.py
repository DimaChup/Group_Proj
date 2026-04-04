#!/usr/bin/env python3
"""Generate GPS estimation error budget breakdown (two-panel horizontal bar chart).

Panel A: In-flight at 5 m/s — all error sources active.
Panel B: Hover lock — averaging + nadir eliminate several sources.
Annotations show which errors are reducible, eliminable, or irreducible.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path

# ── Style ──────────────────────────────────────────────────────────────────
plt.rcParams.update({
    "font.family":      "serif",
    "font.size":        10,
    "axes.titlesize":   12,
    "axes.labelsize":   10,
    "figure.dpi":       300,
    "savefig.dpi":      300,
    "savefig.bbox":     "tight",
    "axes.spines.top":  False,
    "axes.spines.right": False,
})

# ── Data ───────────────────────────────────────────────────────────────────
#                       label                   in-flight  hover    category
sources = [
    ("GPS receiver noise",      2.50, 1.50, "average"),
    ("Attitude / tilt",         0.80, 0.00, "hover"),
    ("GSD quantisation",        0.40, 0.40, "irreducible"),
    ("GPS timing lag",          0.30, 0.00, "hover"),
    ("Focal length cal.",       0.10, 0.10, "calibrate"),
    ("Lens distortion",         0.05, 0.05, "calibrate"),
]

names    = [s[0] for s in sources]
fly_vals = np.array([s[1] for s in sources])
hov_vals = np.array([s[2] for s in sources])
cats     = [s[3] for s in sources]

rss_fly  = np.sqrt(np.sum(fly_vals**2))
rss_hov  = np.sqrt(np.sum(hov_vals**2))

# ── Colours by magnitude ──────────────────────────────────────────────────
def mag_color(v):
    """Red > 1 m, orange > 0.2 m, yellow > 0.08 m, green otherwise."""
    if v >= 1.0:  return "#c0392b"
    if v >= 0.2:  return "#e67e22"
    if v >= 0.08: return "#f1c40f"
    return "#27ae60"

# Category edge colours for annotation markers
CAT_EDGE = {
    "average":     "#2980b9",
    "hover":       "#8e44ad",
    "calibrate":   "#16a085",
    "irreducible": "#7f8c8d",
}
CAT_LABEL = {
    "average":     "Reducible by averaging",
    "hover":       "Eliminated by hover",
    "calibrate":   "Fixed by calibration",
    "irreducible": "Irreducible (GSD)",
}
CAT_MARKER = {
    "average":     "\u25CB",   # open circle
    "hover":       "\u00D7",   # multiplication sign (safe in serif fonts)
    "calibrate":   "\u25B7",   # triangle right
    "irreducible": "\u25A0",   # filled square
}

# ── Figure ─────────────────────────────────────────────────────────────────
fig, (ax_a, ax_b) = plt.subplots(1, 2, figsize=(12, 4.8), sharey=True,
                                  gridspec_kw={"wspace": 0.08})

y_pos = np.arange(len(names))[::-1]   # top-down order (largest first)

def draw_panel(ax, vals, rss, title, show_ylabels=True):
    """Draw horizontal bar chart for one panel."""
    colors = [mag_color(v) for v in vals]
    bars = ax.barh(y_pos, vals, height=0.62, color=colors, edgecolor="white",
                   linewidth=0.6, zorder=3)

    # Value labels
    for i, (v, bar) in enumerate(zip(vals, bars)):
        if v > 0:
            ax.text(v + 0.04, y_pos[i], f"{v:.2f} m",
                    va="center", ha="left", fontsize=8.5, fontweight="bold",
                    color="#2c3e50")
            # Percentage
            pct = (v**2 / rss**2) * 100 if rss > 0 else 0
            if pct >= 1:
                ax.text(v + 0.04, y_pos[i] - 0.28, f"({pct:.0f}%)",
                        va="center", ha="left", fontsize=7.5, color="#7f8c8d")
        else:
            ax.text(0.02, y_pos[i], "0 m", va="center", ha="left",
                    fontsize=8.5, color="#95a5a6", style="italic")

        # Category marker on the left edge of the bar
        cat = cats[i]
        ax.text(-0.08, y_pos[i], CAT_MARKER[cat], va="center", ha="right",
                fontsize=9, color=CAT_EDGE[cat], fontweight="bold")

    # RSS total line
    ax.axvline(rss, color="#2c3e50", ls="--", lw=1.2, zorder=2)
    ax.text(rss + 0.04, y_pos[-1] - 0.8,
            f"RSS = {rss:.1f} m", fontsize=9, fontweight="bold",
            color="#2c3e50", va="top")

    ax.set_xlim(0, max(3.2, rss + 0.6))
    ax.set_xlabel("Error contribution (m)")
    ax.set_title(title, fontweight="bold", pad=10)
    ax.set_yticks(y_pos)
    if show_ylabels:
        ax.set_yticklabels(names, fontsize=9)
    else:
        ax.set_yticklabels([])
    ax.grid(axis="x", alpha=0.25, zorder=0)
    ax.set_axisbelow(True)

# Panel A — In-flight
draw_panel(ax_a, fly_vals, rss_fly,
           "(a)  Error Budget \u2014 In-Flight (5 m/s)", show_ylabels=True)

# Panel B — Hover lock
draw_panel(ax_b, hov_vals, rss_hov,
           "(b)  Error Budget \u2014 Hover Lock", show_ylabels=False)

# Improvement arrow between panels
fig.text(0.50, 0.12,
         f"\u2190  {((rss_fly - rss_hov) / rss_fly) * 100:.0f}% reduction  \u2192",
         ha="center", va="center", fontsize=10, fontweight="bold",
         color="#2980b9",
         bbox=dict(boxstyle="round,pad=0.35", fc="#eaf2f8", ec="#2980b9",
                   lw=1.2, alpha=0.9))

# ── Category legend ────────────────────────────────────────────────────────
legend_handles = []
for cat in ["average", "hover", "calibrate", "irreducible"]:
    patch = mpatches.Patch(
        facecolor="white", edgecolor=CAT_EDGE[cat], linewidth=1.5,
        label=f" {CAT_MARKER[cat]}  {CAT_LABEL[cat]}")
    legend_handles.append(patch)

fig.legend(handles=legend_handles, loc="lower center", ncol=4,
           fontsize=8.5, frameon=True, fancybox=True,
           edgecolor="#bdc3c7", facecolor="white",
           bbox_to_anchor=(0.5, -0.02))

# ── Save ───────────────────────────────────────────────────────────────────
out = Path(__file__).parent
fig.savefig(out / "error_budget_breakdown.pdf", bbox_inches="tight")
fig.savefig(out / "error_budget_breakdown.png", bbox_inches="tight")
print(f"Saved  error_budget_breakdown.pdf / .png  (RSS flight={rss_fly:.2f} m, hover={rss_hov:.2f} m)")
plt.close(fig)
