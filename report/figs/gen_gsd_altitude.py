"""Generate gsd_altitude.pdf — GSD and dummy pixel size vs altitude."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from pathlib import Path

OUT = Path(__file__).parent

# ── Camera & model parameters (from config.py) ──
SENSOR_W_MM = 5.02          # IMX296 sensor width (mm)
FOCAL_MM = 5.46             # Calibrated focal length (mm)
IMAGE_W = 1456              # Native image width (px)
IMAGE_H = 1088              # Native image height (px)
MODEL_INPUT = 640           # YOLOv8 input resolution (px)
DUMMY_H_M = 1.8             # Dummy height / length when lying (m)
DUMMY_W_M = 0.5             # Dummy width (m)
SEARCH_ALT = 35.0           # Chosen search altitude (m)

alt = np.linspace(10, 50, 300)

# ── Derived quantities ──
# Ground Sample Distance: size of one pixel on the ground (m/px)
#   GSD = (sensor_width * altitude) / (focal_length * image_width)
gsd_m = (SENSOR_W_MM * alt) / (FOCAL_MM * IMAGE_W)  # m/px
gsd_cm = gsd_m * 100  # cm/px

# Ground footprint
footprint_w = alt * SENSOR_W_MM / FOCAL_MM  # m
footprint_h = footprint_w * IMAGE_H / IMAGE_W  # m

# Dummy size in native image pixels (along longest axis = height/length)
dummy_px_native = DUMMY_H_M / gsd_m  # px in native image
dummy_px_width = DUMMY_W_M / gsd_m   # px in native image (width)

# After resize to model input (640x640), pixels shrink proportionally
scale_factor = MODEL_INPUT / IMAGE_W  # 640/1456 = 0.44
dummy_px_model = dummy_px_native * scale_factor
dummy_px_model_w = dummy_px_width * scale_factor

# Dummy area in model input (approximate bounding box)
dummy_area_model = dummy_px_model * dummy_px_model_w

# ── Threshold calculations ──
# Minimum detectable: dummy < 5px in model input
# "Missed" threshold in GSD: when dummy_px_model < 5
alt_missed = DUMMY_H_M * FOCAL_MM * IMAGE_W / (SENSOR_W_MM * 5 / scale_factor)
alt_marginal = DUMMY_H_M * FOCAL_MM * IMAGE_W / (SENSOR_W_MM * 10 / scale_factor)
alt_reliable = DUMMY_H_M * FOCAL_MM * IMAGE_W / (SENSOR_W_MM * 20 / scale_factor)

# ── Figure ──
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.2), sharey=False)
fig.subplots_adjust(wspace=0.35, left=0.08, right=0.95, top=0.88, bottom=0.13)

# Colour palette
C_GSD = "#2166ac"
C_DUMMY = "#d62728"
C_DUMMY_W = "#ff7f0e"
C_SEARCH = "#333333"
C_RELIABLE = "#1b7837"
C_MARGINAL = "#e08214"
C_MISSED = "#b2182b"

# ═══════════════════════════════════════════════════════
# LEFT: GSD vs altitude
# ═══════════════════════════════════════════════════════
ax1.plot(alt, gsd_cm, color=C_GSD, linewidth=2.2, label="GSD (cm/px)")
ax1.set_xlabel("Altitude (m)", fontsize=11)
ax1.set_ylabel("Ground Sample Distance (cm/px)", fontsize=11, color=C_GSD)
ax1.tick_params(axis="y", labelcolor=C_GSD)
ax1.set_xlim(10, 50)
ax1.set_ylim(0, max(gsd_cm) * 1.15)
ax1.grid(True, alpha=0.3, linestyle="--")

# Secondary y-axis: ground footprint width
ax1b = ax1.twinx()
ax1b.plot(alt, footprint_w, color="#984ea3", linewidth=1.8, linestyle="--",
          label="Footprint width (m)")
ax1b.set_ylabel("Ground footprint width (m)", fontsize=11, color="#984ea3")
ax1b.tick_params(axis="y", labelcolor="#984ea3")

# Search altitude marker
ax1.axvline(SEARCH_ALT, color=C_SEARCH, linestyle=":", linewidth=1.5, alpha=0.7)
gsd_at_search = (SENSOR_W_MM * SEARCH_ALT) / (FOCAL_MM * IMAGE_W) * 100
ax1.annotate(f"Search alt\n{SEARCH_ALT:.0f} m\nGSD={gsd_at_search:.2f} cm/px",
             xy=(SEARCH_ALT, gsd_at_search), xytext=(SEARCH_ALT + 4, gsd_at_search + 0.15),
             fontsize=8.5, ha="left",
             arrowprops=dict(arrowstyle="->", color=C_SEARCH, lw=1.2),
             bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor=C_SEARCH, alpha=0.9))

# Combined legend
lines1, labels1 = ax1.get_legend_handles_labels()
lines1b, labels1b = ax1b.get_legend_handles_labels()
ax1.legend(lines1 + lines1b, labels1 + labels1b, loc="upper left", fontsize=9,
           framealpha=0.9)

ax1.set_title("Ground Sample Distance", fontsize=12, fontweight="bold", pad=10)

# ═══════════════════════════════════════════════════════
# RIGHT: Dummy pixel size vs altitude (in model input space)
# ═══════════════════════════════════════════════════════

# Shade zones
ax2.axhspan(0, 5, color=C_MISSED, alpha=0.08)
ax2.axhspan(5, 10, color=C_MARGINAL, alpha=0.08)
ax2.axhspan(10, 20, color=C_MARGINAL, alpha=0.05)
ax2.axhspan(20, max(dummy_px_model) * 1.15, color=C_RELIABLE, alpha=0.05)

ax2.plot(alt, dummy_px_model, color=C_DUMMY, linewidth=2.2,
         label=f"Dummy length ({DUMMY_H_M} m)")
ax2.plot(alt, dummy_px_model_w, color=C_DUMMY_W, linewidth=1.8, linestyle="--",
         label=f"Dummy width ({DUMMY_W_M} m)")

# Threshold lines
ax2.axhline(20, color=C_RELIABLE, linestyle="-", linewidth=1, alpha=0.6)
ax2.axhline(10, color=C_MARGINAL, linestyle="-", linewidth=1, alpha=0.6)
ax2.axhline(5, color=C_MISSED, linestyle="-", linewidth=1, alpha=0.6)

# Zone labels on right edge
ax2.text(50.3, 30, "Reliable\n(>20 px)", fontsize=8, color=C_RELIABLE,
         va="center", fontweight="bold")
ax2.text(50.3, 15, "Marginal\n(10-20 px)", fontsize=8, color=C_MARGINAL,
         va="center", fontweight="bold")
ax2.text(50.3, 7.5, "Difficult\n(5-10 px)", fontsize=8, color=C_MISSED,
         va="center", alpha=0.7)
ax2.text(50.3, 2.5, "Missed\n(<5 px)", fontsize=8, color=C_MISSED,
         va="center", fontweight="bold")

# Search altitude marker
ax2.axvline(SEARCH_ALT, color=C_SEARCH, linestyle=":", linewidth=1.5, alpha=0.7)
dummy_at_search = DUMMY_H_M / ((SENSOR_W_MM * SEARCH_ALT) / (FOCAL_MM * IMAGE_W)) * scale_factor
dummy_w_at_search = DUMMY_W_M / ((SENSOR_W_MM * SEARCH_ALT) / (FOCAL_MM * IMAGE_W)) * scale_factor
ax2.annotate(f"At {SEARCH_ALT:.0f} m:\n{dummy_at_search:.0f} px x {dummy_w_at_search:.0f} px",
             xy=(SEARCH_ALT, dummy_at_search),
             xytext=(SEARCH_ALT - 8, dummy_at_search + 8),
             fontsize=8.5, ha="center",
             arrowprops=dict(arrowstyle="->", color=C_SEARCH, lw=1.2),
             bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                       edgecolor=C_SEARCH, alpha=0.9))

# Sweet spot shading
sweet_lo, sweet_hi = 20, 35
ax2.axvspan(sweet_lo, sweet_hi, color=C_RELIABLE, alpha=0.08, zorder=0)
ax2.text((sweet_lo + sweet_hi) / 2, max(dummy_px_model) * 0.95,
         "Sweet spot", fontsize=9, ha="center", color=C_RELIABLE,
         fontweight="bold", fontstyle="italic",
         bbox=dict(boxstyle="round,pad=0.2", facecolor="white",
                   edgecolor=C_RELIABLE, alpha=0.8))

ax2.set_xlabel("Altitude (m)", fontsize=11)
ax2.set_ylabel("Dummy size in model input (px)", fontsize=11)
ax2.set_xlim(10, 50)
ax2.set_ylim(0, max(dummy_px_model) * 1.15)
ax2.grid(True, alpha=0.3, linestyle="--")
ax2.legend(loc="upper right", fontsize=9, framealpha=0.9)
ax2.set_title("Target Size at Model Input (640x640)", fontsize=12,
              fontweight="bold", pad=10)

# ── Subtitle with key numbers ──
fig.text(0.5, 0.96,
         f"Camera: {IMAGE_W}x{IMAGE_H} px  |  f = {FOCAL_MM} mm  |  "
         f"sensor = {SENSOR_W_MM} mm  |  model input: {MODEL_INPUT}x{MODEL_INPUT}",
         ha="center", fontsize=9, color="#666666", fontstyle="italic")

# ── Save ──
for fmt in ("pdf", "png"):
    fig.savefig(OUT / f"gsd_altitude.{fmt}", dpi=300, bbox_inches="tight")
    print(f"Saved {OUT / f'gsd_altitude.{fmt}'}")

plt.close()

# ── Print key values ──
print(f"\n{'Alt (m)':>8} {'GSD (cm/px)':>12} {'Footprint (m)':>14} "
      f"{'Dummy len (px)':>15} {'Dummy wid (px)':>15}")
print("-" * 70)
for a in [10, 15, 20, 25, 30, 35, 40, 45, 50]:
    g = (SENSOR_W_MM * a) / (FOCAL_MM * IMAGE_W) * 100
    fp = a * SENSOR_W_MM / FOCAL_MM
    dl = DUMMY_H_M / (g / 100) * scale_factor
    dw = DUMMY_W_M / (g / 100) * scale_factor
    marker = " <-- SEARCH" if a == 35 else ""
    print(f"{a:>8.0f} {g:>12.2f} {fp:>14.1f} {dl:>15.1f} {dw:>15.1f}{marker}")
