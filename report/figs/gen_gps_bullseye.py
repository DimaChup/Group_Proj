"""Chart 10: GPS Bullseye Plot — Target GPS Estimation Accuracy."""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

np.random.seed(42)

# --- Styling ---
TEXT_DARK = '#2c3e50'
BLUE = '#2980b9'
ORANGE = '#e67e22'
GREEN = '#27ae60'
RED = '#c0392b'
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

fig, ax = plt.subplots(1, 1, figsize=(6, 6))

# --- Simulate GPS estimates ---
# True target at origin
n_estimates = 50

# GPS noise: isotropic ~N(0, 3m) + directional bias from timing lag
# Flight heading ~155 deg (from config), lag 150ms at ~7 m/s = 1.05m forward bias
heading_rad = np.radians(155)
lag_bias = 0.8  # metres forward along flight direction (after IVW correction)
bias_x = lag_bias * np.sin(heading_rad)
bias_y = lag_bias * np.cos(heading_rad)

# Anisotropic noise: more spread along flight direction
along_std = 2.8   # along flight direction (tuned to give CEP50 ~ 2.3m)
across_std = 1.5  # perpendicular

# Generate in flight-aligned frame, then rotate
along_noise = np.random.normal(0, along_std, n_estimates)
across_noise = np.random.normal(0, across_std, n_estimates)

# Rotate from flight frame to map frame
cos_h, sin_h = np.cos(heading_rad), np.sin(heading_rad)
x_est = along_noise * sin_h + across_noise * cos_h + bias_x
y_est = along_noise * cos_h - across_noise * sin_h + bias_y

# Compute centroid and CEP
centroid_x, centroid_y = np.mean(x_est), np.mean(y_est)
distances = np.sqrt(x_est**2 + y_est**2)
cep50 = np.percentile(distances, 50)
cep95 = np.percentile(distances, 95)

# --- Concentric range rings ---
ring_radii = [2, 5, 10, 15]
for r in ring_radii:
    circle = Circle((0, 0), r, fill=False, linestyle='--', linewidth=0.8,
                     edgecolor='#bdc3c7', zorder=1)
    ax.add_patch(circle)
    # Label at top of circle
    ax.text(0, r + 0.3, f'{r} m', ha='center', va='bottom', fontsize=7.5,
            color=GREY, zorder=5)

# --- CEP circles ---
cep50_circle = Circle((0, 0), cep50, fill=False, linestyle='-', linewidth=2.0,
                       edgecolor=ORANGE, zorder=2, label=f'CEP50 = {cep50:.1f} m')
ax.add_patch(cep50_circle)

cep95_circle = Circle((0, 0), cep95, fill=False, linestyle='-.', linewidth=1.5,
                       edgecolor=RED, zorder=2, label=f'CEP95 = {cep95:.1f} m')
ax.add_patch(cep95_circle)

# --- Scatter estimates ---
ax.scatter(x_est, y_est, c=BLUE, s=25, alpha=0.6, edgecolors='white',
           linewidths=0.4, zorder=4, label='GPS estimates')

# --- True position ---
ax.plot(0, 0, '+', color=GREEN, markersize=18, markeredgewidth=3, zorder=6,
        label='True position')

# --- Cluster centroid ---
ax.plot(centroid_x, centroid_y, '*', color=RED, markersize=16, markeredgewidth=0.5,
        zorder=6, label=f'Centroid ({centroid_x:+.1f}, {centroid_y:+.1f}) m')

# --- Bias arrow ---
ax.annotate('', xy=(bias_x * 3, bias_y * 3), xytext=(0, 0),
            arrowprops=dict(arrowstyle='->', color=ORANGE, lw=1.5, linestyle='-'),
            zorder=3)
ax.text(bias_x * 3.3, bias_y * 3.3, f'Flight direction\n(heading {155}\u00b0)',
        fontsize=7.5, color=ORANGE, ha='center', va='top', zorder=5)

# --- Formatting ---
lim = 17
ax.set_xlim(-lim, lim)
ax.set_ylim(-lim, lim)
ax.set_aspect('equal')
ax.set_xlabel('East offset (m)', fontsize=11)
ax.set_ylabel('North offset (m)', fontsize=11)
ax.set_title('Target GPS Estimation Accuracy', fontsize=13, fontweight='bold',
             color=TEXT_DARK, pad=12)

ax.axhline(0, color='#dddddd', linewidth=0.5, zorder=0)
ax.axvline(0, color='#dddddd', linewidth=0.5, zorder=0)

ax.legend(loc='upper left', fontsize=8.5, framealpha=0.9, edgecolor='#cccccc')
ax.grid(True, alpha=0.15, zorder=0)

plt.tight_layout()
plt.savefig('gps_bullseye.pdf', bbox_inches='tight', dpi=300)
plt.savefig('gps_bullseye.png', bbox_inches='tight', dpi=200)
print('Saved gps_bullseye.pdf')
