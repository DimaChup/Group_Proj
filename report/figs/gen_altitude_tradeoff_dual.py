"""Generate altitude_tradeoff_dual.pdf — two-panel altitude dilemma figure."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
from pathlib import Path

OUT = Path(__file__).parent

# ── Physics parameters (from config.py) ──
SENSOR_W_MM = 5.02
FOCAL_MM = 5.46
IMAGE_W = 1456
IMAGE_H = 1088
DUMMY_H_M = 1.8
SEARCH_SPEED = 8.0  # m/s nominal
FPS = 4.8  # Pi TFLite FPS
LANE_OVERLAP = 0.15

alt = np.linspace(15, 55, 200)

# ── Derived quantities ──
# Ground footprint width (m)
footprint_w = alt * SENSOR_W_MM / FOCAL_MM
footprint_h = footprint_w * IMAGE_H / IMAGE_W
# Coverage rate (m^2/s) = footprint_w * speed
coverage_rate = footprint_w * SEARCH_SPEED
# Lane count for 200m-wide area
area_width = 200.0
lane_spacing = footprint_w * (1 - LANE_OVERLAP)
lane_count = area_width / lane_spacing
# Energy per area (relative) — fewer lanes = less distance = less energy
# Proportional to lane_count (more lanes = more energy)
energy_per_area = lane_count / lane_count.max()  # normalized 0-1

# Target pixel size (px)
target_px = DUMMY_H_M * FOCAL_MM / (alt * SENSOR_W_MM / IMAGE_W)
# Detection confidence (empirical sigmoid drop)
conf = 0.95 / (1 + np.exp(0.12 * (alt - 40))) + 0.05
# NFZ footprint intrusion (higher alt = wider footprint = closer to NFZ edge)
nfz_intrusion = footprint_w / 2  # half-width extends toward NFZ
# GPS estimation error (scales with altitude — pixel error * alt / focal)
gps_err = alt * 2.0 / (FOCAL_MM / SENSOR_W_MM * IMAGE_W)  # ~2px error

# ── Figure ──
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.2), sharey=False)
fig.subplots_adjust(wspace=0.35, left=0.08, right=0.95, top=0.88, bottom=0.13)

colors_l = ["#2166ac", "#1b7837", "#e08214", "#984ea3"]
colors_r = ["#d6604d", "#762a83", "#e08214", "#2166ac"]

# LEFT: Benefits
ax1.set_title("Benefits of increasing altitude", fontsize=12, fontweight="bold", pad=10)
l1, = ax1.plot(alt, footprint_w, color=colors_l[0], lw=2.2, label="Ground footprint (m)")
l2, = ax1.plot(alt, coverage_rate / 10, color=colors_l[1], lw=2.2, ls="--",
               label=r"Coverage rate ($\times 10\,$m$^2$/s)")
l3, = ax1.plot(alt, (lane_count.max() - lane_count) / lane_count.max() * 50 + 10,
               color=colors_l[2], lw=2.2, ls="-.",
               label="Lane reduction (fewer passes)")
l4, = ax1.plot(alt, (1 - energy_per_area) * 40 + 10, color=colors_l[3], lw=2.2, ls=":",
               label=r"Energy saving (Wh/ha$^{-1}$)")
ax1.set_xlabel("Altitude (m)", fontsize=11)
ax1.set_ylabel("Benefit magnitude (mixed units)", fontsize=11)
ax1.legend(loc="upper left", fontsize=8.5, framealpha=0.9)
ax1.set_xlim(15, 55)
ax1.annotate("", xy=(52, ax1.get_ylim()[1]*0.85), xytext=(20, ax1.get_ylim()[1]*0.85),
             arrowprops=dict(arrowstyle="->", color="green", lw=1.5))
ax1.text(36, ax1.get_ylim()[1]*0.88, "higher = better", ha="center", fontsize=9,
         color="green", fontstyle="italic")
ax1.grid(True, alpha=0.3)

# RIGHT: Costs
ax2.set_title("Costs of increasing altitude", fontsize=12, fontweight="bold", pad=10)
ax2r = ax2.twinx()
c1, = ax2.plot(alt, target_px, color=colors_r[0], lw=2.2, label="Target size (px)")
c2, = ax2.plot(alt, conf * 100, color=colors_r[1], lw=2.2, ls="--",
               label="Detection confidence (%)")
c3, = ax2r.plot(alt, nfz_intrusion, color=colors_r[2], lw=2.2, ls="-.",
                label="NFZ intrusion risk (m)")
c4, = ax2r.plot(alt, gps_err, color=colors_r[3], lw=2.2, ls=":",
                label="GPS est. error (m)")
ax2.set_xlabel("Altitude (m)", fontsize=11)
ax2.set_ylabel("Pixel size / Confidence", fontsize=11)
ax2r.set_ylabel("Distance (m)", fontsize=11)
ax2.set_xlim(15, 55)
lines = [c1, c2, c3, c4]
labels = [l.get_label() for l in lines]
ax2.legend(lines, labels, loc="upper right", fontsize=8.5, framealpha=0.9)
ax2.annotate("", xy=(52, ax2.get_ylim()[1]*0.85), xytext=(20, ax2.get_ylim()[1]*0.85),
             arrowprops=dict(arrowstyle="->", color="red", lw=1.5))
ax2.text(36, ax2.get_ylim()[1]*0.88, "higher = worse", ha="center", fontsize=9,
         color="red", fontstyle="italic")
ax2.grid(True, alpha=0.3)

# Sweet spot line on both
for ax in [ax1, ax2]:
    ax.axvline(35, color="#404040", ls="--", lw=1.5, alpha=0.6)
    ymin, ymax = ax.get_ylim()
    ax.text(35.5, ymin + (ymax - ymin) * 0.05, "selected\n35 m",
            fontsize=9, color="#404040", fontstyle="italic", va="bottom")

fig.suptitle("The Altitude Dilemma: Competing Effects", fontsize=14, fontweight="bold", y=0.97)

for fmt in ["pdf", "png"]:
    fig.savefig(OUT / f"altitude_tradeoff_dual.{fmt}", dpi=300, bbox_inches="tight")
print("Saved altitude_tradeoff_dual.pdf/.png")
