"""Attitude Compensation Before/After — GPS estimation error scatter plot."""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

np.random.seed(42)

# --- Styling (matches project convention) ---
TEXT_DARK = '#2c3e50'
RED = '#c0392b'
GREEN = '#27ae60'
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

N = 200
heading_deg = 155  # flight heading from config
heading_rad = np.radians(heading_deg)

# ── Left panel: WITHOUT compensation (nadir assumption) ──
# Anisotropic error elongated along flight heading
# Tuned so CEP50 ~ 6.2m (median radial distance)
sigma_along = 8.0   # metres along flight direction
sigma_across = 4.0  # metres perpendicular
along = np.random.normal(0, sigma_along, N)
across = np.random.normal(0, sigma_across, N)
# Rotate from flight-aligned frame to map frame (East/North)
cos_h, sin_h = np.cos(heading_rad), np.sin(heading_rad)
x_no = along * sin_h + across * cos_h
y_no = along * cos_h - across * sin_h

dist_no = np.sqrt(x_no**2 + y_no**2)
cep50_no = np.percentile(dist_no, 50)
cep95_no = np.percentile(dist_no, 95)

# ── Right panel: WITH compensation (ray-trace correction) ──
# Isotropic residual from IMU noise only
sigma_comp = 0.25
x_yes = np.random.normal(0, sigma_comp, N)
y_yes = np.random.normal(0, sigma_comp, N)

dist_yes = np.sqrt(x_yes**2 + y_yes**2)
cep50_yes = np.percentile(dist_yes, 50)
cep95_yes = np.percentile(dist_yes, 95)

# ── Figure ──
fig, (ax_l, ax_r) = plt.subplots(1, 2, figsize=(11, 5))

for ax, x, y, cep50, cep95, colour, title, label_side in [
    (ax_l, x_no, y_no, cep50_no, cep95_no, RED,   'Nadir assumption', 'left'),
    (ax_r, x_yes, y_yes, cep50_yes, cep95_yes, GREEN, 'Ray-trace correction', 'right'),
]:
    # Determine axis limits from data
    if label_side == 'left':
        lim = 18
    else:
        lim = 1.0

    # Range rings
    if label_side == 'left':
        rings = [5, 10, 15]
    else:
        rings = [0.2, 0.5, 0.8]
    for r in rings:
        c = Circle((0, 0), r, fill=False, linestyle='--', linewidth=0.7,
                   edgecolor='#bdc3c7', zorder=1)
        ax.add_patch(c)
        ax.text(0, r + lim * 0.025, f'{r} m', ha='center', va='bottom',
                fontsize=7, color=GREY, zorder=5)

    # CEP circles
    c50 = Circle((0, 0), cep50, fill=False, linestyle='-', linewidth=2.0,
                 edgecolor=colour, zorder=2, label=f'CEP50 = {cep50:.1f} m')
    ax.add_patch(c50)
    c95 = Circle((0, 0), cep95, fill=False, linestyle='-.', linewidth=1.3,
                 edgecolor=colour, alpha=0.5, zorder=2, label=f'CEP95 = {cep95:.1f} m')
    ax.add_patch(c95)

    # Scatter
    ax.scatter(x, y, c=colour, s=14, alpha=0.5, edgecolors='white',
               linewidths=0.3, zorder=4)

    # True position crosshair
    ax.plot(0, 0, '+', color='#2c3e50', markersize=14, markeredgewidth=2.5, zorder=6)

    # CEP annotation box
    box_y = -lim * 0.82
    ax.text(0, box_y, f'CEP50 = {cep50:.1f} m\nCEP95 = {cep95:.1f} m',
            ha='center', va='center', fontsize=10, fontweight='bold', color=colour,
            bbox=dict(boxstyle='round,pad=0.4', facecolor='white', edgecolor=colour,
                      alpha=0.9),
            zorder=7)

    # Formatting
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_aspect('equal')
    ax.set_xlabel('East offset (m)', fontsize=10)
    ax.set_ylabel('North offset (m)', fontsize=10)
    ax.set_title(title, fontsize=12, fontweight='bold', color=TEXT_DARK, pad=10)
    ax.axhline(0, color='#dddddd', linewidth=0.5, zorder=0)
    ax.axvline(0, color='#dddddd', linewidth=0.5, zorder=0)
    ax.legend(loc='upper left', fontsize=8, framealpha=0.9, edgecolor='#cccccc')
    ax.grid(True, alpha=0.15, zorder=0)

# Flight heading arrow on left panel
arrow_len = 8
ax_l.annotate('', xy=(arrow_len * sin_h, arrow_len * cos_h), xytext=(0, 0),
              arrowprops=dict(arrowstyle='->', color='#e67e22', lw=1.5),
              zorder=3)
ax_l.text(arrow_len * sin_h * 1.15, arrow_len * cos_h * 1.15,
          f'Flight heading\n({heading_deg}\u00b0)',
          fontsize=7.5, color='#e67e22', ha='center', va='top', zorder=5)

fig.suptitle('GPS Estimation Error: Attitude Compensation',
             fontsize=14, fontweight='bold', color=TEXT_DARK, y=0.98)

plt.tight_layout(rect=[0, 0, 1, 0.94])
plt.savefig('attitude_compensation.pdf', bbox_inches='tight', dpi=300)
plt.savefig('attitude_compensation.png', bbox_inches='tight', dpi=200)
print('Saved attitude_compensation.pdf and attitude_compensation.png')
