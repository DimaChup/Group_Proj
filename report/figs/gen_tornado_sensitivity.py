"""Generate tornado diagram: parameter sensitivity of composite mission score."""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

# --- Data (sorted by swing, largest first) ---
baseline = 0.87

params = [
    ("Altitude (35 m)",      0.91, 0.82),
    ("NFZ margin (30 m)",    0.89, 0.85),
    ("Overlap (20%)",        0.88, 0.85),
    ("Scan angle (70\u00b0)",0.83, 0.85),
    ("Speed (8 m/s)",        0.85, 0.84),
]

labels   = [p[0] for p in params]
lo_vals  = [p[1] for p in params]   # score when param decreased by 20%
hi_vals  = [p[2] for p in params]   # score when param increased by 20%

y_pos = np.arange(len(labels))

fig, ax = plt.subplots(figsize=(8, 3.8))

for i, (label, lo, hi) in enumerate(params):
    # Bar from baseline to lo_val (param -20%)
    left_start = min(baseline, lo)
    left_width = abs(lo - baseline)
    color_lo = "#2166ac" if lo > baseline else "#b2182b"
    ax.barh(i, left_width, left=left_start, height=0.55, color=color_lo,
            edgecolor="white", linewidth=0.5)

    # Bar from baseline to hi_val (param +20%)
    right_start = min(baseline, hi)
    right_width = abs(hi - baseline)
    color_hi = "#2166ac" if hi > baseline else "#b2182b"
    ax.barh(i, right_width, left=right_start, height=0.55, color=color_hi,
            edgecolor="white", linewidth=0.5)

    # Annotate values at bar ends
    lo_x = lo - 0.003 if lo < baseline else lo + 0.003
    hi_x = hi + 0.003 if hi > baseline else hi - 0.003
    ha_lo = "right" if lo < baseline else "left"
    ha_hi = "left"  if hi > baseline else "right"
    ax.text(lo_x, i, f"{lo:.2f}", va="center", ha=ha_lo, fontsize=8, color="#333333")
    ax.text(hi_x, i, f"{hi:.2f}", va="center", ha=ha_hi, fontsize=8, color="#333333")

    # Swing annotation on right margin
    swing = abs(hi - lo)
    ax.text(0.965, i, f"\u0394 = {swing:.2f}", va="center", ha="right",
            fontsize=8, color="#555555", transform=ax.get_yaxis_transform())

# Baseline vertical line
ax.axvline(baseline, color="#333333", linewidth=1.2, linestyle="--", zorder=3)
ax.text(baseline, len(labels) - 0.05, f"Baseline = {baseline:.2f}",
        ha="center", va="bottom", fontsize=9, fontweight="bold", color="#333333")

# Legend
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor="#2166ac", label="Score improves"),
    Patch(facecolor="#b2182b", label="Score worsens"),
]
ax.legend(handles=legend_elements, loc="lower right", fontsize=8, framealpha=0.9)

# Axes
ax.set_yticks(y_pos)
ax.set_yticklabels(labels, fontsize=9)
ax.invert_yaxis()
ax.set_xlabel("Composite Mission Score", fontsize=10)
ax.set_title("Tornado Diagram: Parameter Sensitivity of Composite Mission Score",
             fontsize=11, fontweight="bold", pad=10)
ax.set_xlim(0.79, 0.95)
ax.xaxis.set_major_locator(mticker.MultipleLocator(0.02))
ax.xaxis.set_minor_locator(mticker.MultipleLocator(0.01))
ax.tick_params(axis="x", labelsize=9)
ax.grid(axis="x", alpha=0.3, linewidth=0.5)
ax.set_axisbelow(True)

# Subtitle with parameter variation note
fig.text(0.5, -0.02, "Each parameter varied \u00b120% from baseline; others held fixed",
         ha="center", fontsize=8, color="#666666", style="italic")

plt.tight_layout()

out = r"c:\Users\Bristol\Desktop\AI for Robotics\v3\report\figs\tornado_sensitivity"
fig.savefig(out + ".pdf", bbox_inches="tight", dpi=300)
fig.savefig(out + ".png", bbox_inches="tight", dpi=300)
print(f"Saved {out}.pdf and .png")
