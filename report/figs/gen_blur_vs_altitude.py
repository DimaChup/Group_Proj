"""Charts: Motion blur vs altitude and detection envelope for SAR drone.

Generates:
  blur_vs_altitude.pdf  — pixel motion per frame vs altitude at various speeds/exposures
  detection_envelope.pdf — detection confidence vs altitude with blur degradation
"""
import numpy as np
import matplotlib.pyplot as plt

# --- Styling (matches project charts) ---
TEXT_DARK = '#2c3e50'
BLUE = '#2980b9'
ORANGE = '#e67e22'
GREEN = '#27ae60'
RED = '#c0392b'
GREY = '#7f8c8d'
PURPLE = '#8e44ad'

plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 10,
    'axes.labelcolor': TEXT_DARK,
    'text.color': TEXT_DARK,
    'axes.edgecolor': '#cccccc',
    'xtick.color': TEXT_DARK,
    'ytick.color': TEXT_DARK,
})

# --- Sensor parameters (from config.py) ---
SENSOR_WIDTH_MM = 5.02
FOCAL_LENGTH_MM = 5.46
IMAGE_W = 1456


def pixel_motion(v, h, t_exp):
    """Pixel displacement per frame due to ground motion.

    GSD = (sensor_width * h) / (focal_length * image_width)   [m/pixel]
    pixel_motion = v * t_exp / GSD
                 = v * t_exp * focal_length * image_width / (sensor_width * h)
    """
    return v * t_exp * FOCAL_LENGTH_MM * IMAGE_W / (SENSOR_WIDTH_MM * h)


# =========================================================================
# Chart 1: Pixel motion vs altitude
# =========================================================================
altitudes = np.linspace(5, 50, 200)
speeds = [5, 10, 15]
exposures = {'Exposure 1/100 s': 1/100, 'Exposure 1/500 s': 1/500}

fig, axes = plt.subplots(1, 2, figsize=(11, 4.8), sharey=False)

colors_speed = {5: GREEN, 10: BLUE, 15: RED}
linestyles_exp = {'1/100 s (rolling shutter)': '-', '1/500 s (global shutter)': '--'}

for idx, (exp_label, t_exp) in enumerate(exposures.items()):
    ax = axes[idx]
    for v in speeds:
        pm = pixel_motion(v, altitudes, t_exp)
        ax.plot(altitudes, pm, color=colors_speed[v], linewidth=2,
                linestyle='-', label=f'{v} m/s')

    # Blur threshold line
    ax.axhline(y=3, color=ORANGE, linewidth=1.5, linestyle=':', alpha=0.8)
    ax.text(48, 3.3, 'Blur threshold (3 px)', fontsize=8, color=ORANGE,
            ha='right', va='bottom', fontstyle='italic')

    # Operational envelope shading
    ax.axvspan(15, 40, alpha=0.07, color=BLUE, zorder=0)

    ax.set_xlabel('Altitude (m)', fontsize=11)
    ax.set_title(exp_label, fontsize=11, fontweight='bold', color=TEXT_DARK, pad=8)
    ax.legend(loc='upper right', fontsize=9, framealpha=0.9, edgecolor='#cccccc',
              title='Ground speed', title_fontsize=9)
    ax.grid(True, alpha=0.15, zorder=0)
    ax.set_xlim(5, 50)

axes[0].set_ylabel('Pixel motion per frame (px)', fontsize=11)

# Fix y-axis
y_max_slow = pixel_motion(15, 5, 1/100) * 1.1
axes[0].set_ylim(0, y_max_slow)
y_max_fast = pixel_motion(15, 5, 1/500) * 1.1
axes[1].set_ylim(0, y_max_fast)

# Add operational envelope label after ylim is set
for ax in axes:
    ax.text(27.5, ax.get_ylim()[1] * 0.92, 'Operational\nenvelope',
            fontsize=8, color=BLUE, ha='center', va='top', alpha=0.6)

fig.suptitle('Motion Blur: Pixel Displacement vs Altitude',
             fontsize=13, fontweight='bold', color=TEXT_DARK, y=1.02)

plt.tight_layout()
plt.savefig('blur_vs_altitude.pdf', bbox_inches='tight', dpi=300)
plt.savefig('blur_vs_altitude.png', bbox_inches='tight', dpi=200)
print('Saved blur_vs_altitude.pdf')
plt.close()


# =========================================================================
# Chart 2: Detection envelope with blur degradation
# =========================================================================
altitudes2 = np.linspace(5, 60, 300)

# Baseline detection confidence vs altitude (no blur, ideal)
# Model: high confidence 10-45m, drops off at extremes
# Below ~8m: target too large / partially out of frame
# Above ~50m: target too small (few pixels)
def base_confidence(h):
    """Idealised detection confidence vs altitude (no motion blur)."""
    # Target apparent size in pixels: dummy ~1.8m tall
    target_px = 1.8 * FOCAL_LENGTH_MM * IMAGE_W / (SENSOR_WIDTH_MM * h)
    # Peak around 15-35m where target is 30-80 px (good for YOLOv8 at 640 input)
    # Sigmoid rise from low altitude (target too big), Gaussian fall at high
    rise = 1 / (1 + np.exp(-0.8 * (h - 8)))       # rises past 8m
    fall = np.exp(-((h - 25) / 30)**2)              # gentle fall centred at 25m
    conf = 0.96 * rise * fall
    return np.clip(conf, 0, 0.98)


def blur_degradation(h, v, t_exp=1/100):
    """Confidence reduction factor due to motion blur.

    Blur smears the target across `pm` pixels.  When pm > ~2 px the
    bounding-box regressor and classifier both lose accuracy.
    Model: degradation = exp(-k * max(0, pm - 1)^2)
    """
    pm = pixel_motion(v, h, t_exp)
    # Below 1 px motion: no degradation
    excess = np.maximum(pm - 1.0, 0)
    return np.exp(-0.012 * excess**2)


fig2, ax2 = plt.subplots(figsize=(8, 5))

# Ideal (no blur)
conf_ideal = base_confidence(altitudes2)
ax2.plot(altitudes2, conf_ideal, color=BLUE, linewidth=2.2, label='No blur (ideal)',
         zorder=4)

# With blur at 10 m/s, 1/100s exposure
conf_10 = conf_ideal * blur_degradation(altitudes2, 10, 1/100)
ax2.plot(altitudes2, conf_10, color=ORANGE, linewidth=2, linestyle='--',
         label='10 m/s, 1/100 s exposure', zorder=3)

# With blur at 15 m/s, 1/100s exposure
conf_15 = conf_ideal * blur_degradation(altitudes2, 15, 1/100)
ax2.plot(altitudes2, conf_15, color=RED, linewidth=2, linestyle='-.',
         label='15 m/s, 1/100 s exposure', zorder=3)

# With global shutter at 10 m/s (nearly identical to ideal)
conf_gs = conf_ideal * blur_degradation(altitudes2, 10, 1/500)
ax2.plot(altitudes2, conf_gs, color=GREEN, linewidth=1.8, linestyle=':',
         label='10 m/s, global shutter (1/500 s)', zorder=3)

# Confidence threshold
ax2.axhline(y=0.2, color=GREY, linewidth=1.2, linestyle=':', alpha=0.7)
ax2.text(58, 0.22, 'Confidence\nthreshold (0.2)', fontsize=8, color=GREY,
         ha='right', va='bottom', fontstyle='italic')

# Operational envelope shading
ax2.axvspan(15, 40, alpha=0.08, color=BLUE, zorder=0,
            label='Operational envelope (15\u201340 m)')

# Annotate key insight
ax2.annotate('Blur significant\nbelow 15 m only',
             xy=(10, conf_15[np.argmin(np.abs(altitudes2 - 10))]),
             xytext=(18, 0.25),
             fontsize=9, color=RED, fontweight='bold',
             arrowprops=dict(arrowstyle='->', color=RED, lw=1.2),
             ha='left', va='center')

# Target size annotation (right side)
ax2_twin = ax2.twinx()
target_px = 1.8 * FOCAL_LENGTH_MM * IMAGE_W / (SENSOR_WIDTH_MM * altitudes2)
ax2_twin.plot(altitudes2, target_px, color=PURPLE, linewidth=1.2, alpha=0.4,
              linestyle='-')
ax2_twin.set_ylabel('Target size (pixels)', fontsize=10, color=PURPLE, alpha=0.6)
ax2_twin.tick_params(axis='y', colors=PURPLE)
ax2_twin.set_ylim(0, 200)
# Minimum detectable size
ax2_twin.axhline(y=10, color=PURPLE, linewidth=0.8, linestyle=':', alpha=0.3)
ax2_twin.text(58, 12, '~10 px min', fontsize=7, color=PURPLE, alpha=0.5,
              ha='right')

# Formatting
ax2.set_xlabel('Altitude (m)', fontsize=11)
ax2.set_ylabel('Detection Confidence', fontsize=11)
ax2.set_title('Detection Envelope: Confidence vs Altitude with Motion Blur',
              fontsize=13, fontweight='bold', color=TEXT_DARK, pad=12)
ax2.set_xlim(5, 60)
ax2.set_ylim(0, 1.05)
ax2.legend(loc='upper right', fontsize=8.5, framealpha=0.9, edgecolor='#cccccc')
ax2.grid(True, alpha=0.15, zorder=0)

plt.tight_layout()
plt.savefig('detection_envelope.pdf', bbox_inches='tight', dpi=300)
plt.savefig('detection_envelope.png', bbox_inches='tight', dpi=200)
print('Saved detection_envelope.pdf')
plt.close()
