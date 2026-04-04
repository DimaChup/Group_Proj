"""Generate progressive GPS accuracy improvement bar chart."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path

OUT = Path(__file__).parent

# Data
phases = [
    "Measured (DJI video)",
    "Phase 3: HOVER LOCK\n(nadir)",
    "Phase 2: CENTERING\n(approaching)",
    "Phase 1: SEARCH\n(tilt compensation)",
    "Phase 1: SEARCH\n(single flyover)",
]
ceps = [2.3, 1.8, 2.5, 3.5, 7.0]
colors = ["#3182bd", "#2ca02c", "#f0e442", "#e6820e", "#d62728"]
hatches = ["//", "", "", "", ""]

fig, ax = plt.subplots(figsize=(8, 4.2))

# R07 requirement zone (5-10m shaded green)
ax.axvspan(5.0, 10.0, color="#2ca02c", alpha=0.10, zorder=0)
ax.axvline(10.0, color="#2ca02c", ls="--", lw=1.0, alpha=0.5)
ax.axvline(5.0, color="#2ca02c", ls="--", lw=1.0, alpha=0.5)
ax.text(7.5, len(phases) - 0.15, "R07 requirement\n(5\u201310 m)",
        ha="center", va="top", fontsize=7.5, color="#2ca02c", fontstyle="italic")

y = np.arange(len(phases))
bars = ax.barh(y, ceps, height=0.55, color=colors, edgecolor="black", linewidth=0.6, zorder=3)

# Dashed edge for measured bar
bars[0].set_linestyle("--")
bars[0].set_edgecolor("#3182bd")
bars[0].set_linewidth(1.5)

# Annotations: CEP value + improvement factor relative to worst (7.0m)
baseline = 7.0
for i, (bar, cep) in enumerate(zip(bars, ceps)):
    factor = baseline / cep
    label = f"{cep:.1f} m"
    if factor > 1.05:
        label += f"  ({factor:.1f}x improvement)"
    ax.text(bar.get_width() + 0.15, bar.get_y() + bar.get_height() / 2,
            label, va="center", ha="left", fontsize=9, fontweight="bold")

ax.set_yticks(y)
ax.set_yticklabels(phases, fontsize=9)
ax.set_xlabel("CEP50 (metres)", fontsize=11)
ax.set_xlim(0, 11.5)
ax.invert_yaxis()
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.grid(axis="x", alpha=0.3, zorder=0)
ax.set_title("GPS Estimation Accuracy by Mission Phase", fontsize=12, fontweight="bold", pad=10)

plt.tight_layout()
fig.savefig(OUT / "progressive_accuracy.pdf", bbox_inches="tight")
fig.savefig(OUT / "progressive_accuracy.png", bbox_inches="tight", dpi=200)
plt.close()
print("Saved progressive_accuracy.pdf and .png")
