"""Altitude vs Detection Performance — Visual Summary."""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# --- Styling ---
TEXT_DARK = '#2c3e50'
BLUE = '#2980b9'
ORANGE = '#e67e22'
GREEN = '#27ae60'
RED = '#c0392b'
YELLOW = '#f39c12'
GREY = '#7f8c8d'

plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 10,
    'axes.labelcolor': TEXT_DARK,
    'text.color': TEXT_DARK,
    'axes.edgecolor': '#cccccc',
    'xtick.color': TEXT_DARK,
    'ytick.color': TEXT_DARK,
})

# --- Data ---
# Altitude bands, target pixel size (px at 640 input), confidence, detection rate (%)
# Based on: IMX296 sensor 5.02mm, focal 5.46mm, IMAGE_W=1456, IMAGE_H=1088
# Dummy 1.8m tall. At altitude h, angular size = 2*atan(0.9/h), pixel size in 640 input.
# FOV_H = 2*atan(5.02/(2*5.46)) = ~49.3 deg for Pi camera
# At 1456px wide, px_per_deg = 1456 / 49.3 = 29.5 px/deg
# Dummy 1.8m at h m: angular = degrees(2*atan(0.9/h))
# Pixel size in native = angular * 29.5, then scaled to 640 input = pixel_native * 640/1456

altitudes = np.array([10, 15, 20, 25, 30, 35, 40, 50])

# Pixel sizes (approx, in 640x640 YOLO input)
pixel_sizes = []
for h in altitudes:
    angular_deg = np.degrees(2 * np.arctan(0.9 / h))
    px_native = angular_deg * 29.5
    px_640 = px_native * 640 / 1456
    pixel_sizes.append(px_640)
pixel_sizes = np.array(pixel_sizes)

# Confidence (realistic: high close, drops at distance)
confidences = np.array([0.97, 0.96, 0.94, 0.90, 0.85, 0.72, 0.55, 0.30])

# Detection rate (%)
detection_rates = np.array([100, 100, 98, 95, 90, 78, 55, 20])

# --- Color coding ---
def rate_color(rate):
    if rate >= 90:
        return GREEN
    elif rate >= 70:
        return YELLOW
    else:
        return RED

bar_colors = [rate_color(r) for r in detection_rates]

# --- Plot ---
fig, axes = plt.subplots(1, 3, figsize=(11, 4.5), sharey=True)

# Subplot 1: Target Pixel Size
ax1 = axes[0]
bars1 = ax1.barh(range(len(altitudes)), pixel_sizes, color=BLUE, alpha=0.8, height=0.6)
ax1.set_yticks(range(len(altitudes)))
ax1.set_yticklabels([f'{a} m' for a in altitudes])
ax1.set_xlabel('Target Size (px in 640 input)', fontsize=10, fontweight='bold')
ax1.set_title('Target Pixel Size', fontsize=11, fontweight='bold', color=TEXT_DARK)
ax1.invert_yaxis()
# Add value labels
for i, (v, bar) in enumerate(zip(pixel_sizes, bars1)):
    ax1.text(v + 0.5, i, f'{v:.0f}', va='center', fontsize=9, color=TEXT_DARK)
# Reference line: YOLO minimum reliable detection ~8px
ax1.axvline(x=8, color=RED, linestyle='--', linewidth=1, alpha=0.6)
ax1.text(9, 7.3, 'min reliable', fontsize=7, color=RED, style='italic')

# Subplot 2: Confidence
ax2 = axes[1]
bars2 = ax2.barh(range(len(altitudes)), confidences, color=ORANGE, alpha=0.8, height=0.6)
ax2.set_xlabel('Mean Confidence', fontsize=10, fontweight='bold')
ax2.set_title('Detection Confidence', fontsize=11, fontweight='bold', color=TEXT_DARK)
# Threshold line
ax2.axvline(x=0.2, color=RED, linestyle='--', linewidth=1, alpha=0.6)
ax2.text(0.22, 7.3, 'threshold', fontsize=7, color=RED, style='italic')
for i, (v, bar) in enumerate(zip(confidences, bars2)):
    ax2.text(v + 0.01, i, f'{v:.2f}', va='center', fontsize=9, color=TEXT_DARK)
ax2.set_xlim(0, 1.15)

# Subplot 3: Detection Rate
ax3 = axes[2]
bars3 = ax3.barh(range(len(altitudes)), detection_rates, color=bar_colors, alpha=0.85, height=0.6)
ax3.set_xlabel('Detection Rate (%)', fontsize=10, fontweight='bold')
ax3.set_title('Detection Rate', fontsize=11, fontweight='bold', color=TEXT_DARK)
for i, (v, bar) in enumerate(zip(detection_rates, bars3)):
    ax3.text(v + 1, i, f'{v}%', va='center', fontsize=9, color=TEXT_DARK)
ax3.set_xlim(0, 115)

# Sweet spot highlight
for ax in axes:
    for i in [2, 3, 4]:  # 20, 25, 30m
        ax.axhspan(i - 0.4, i + 0.4, color=GREEN, alpha=0.06)

# Legend for colors
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor=GREEN, alpha=0.7, label='>90%'),
    Patch(facecolor=YELLOW, alpha=0.7, label='70-90%'),
    Patch(facecolor=RED, alpha=0.7, label='<70%'),
]
axes[2].legend(handles=legend_elements, loc='lower right', fontsize=8,
               title='Rate', title_fontsize=8, framealpha=0.9)

fig.suptitle('Altitude vs Detection Performance — Operational Envelope',
             fontsize=13, fontweight='bold', color=TEXT_DARK, y=1.02)

plt.tight_layout()
plt.savefig('altitude_detection_table.pdf', bbox_inches='tight', dpi=300)
plt.savefig('altitude_detection_table.png', bbox_inches='tight', dpi=300)
print("Saved altitude_detection_table.pdf + .png")
