"""Centrality Weighting — Detection position weight and GPS estimation error."""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Ellipse
from matplotlib.colors import Normalize
from matplotlib import cm
import os

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

# --- Constants ---
IMG_W, IMG_H = 1456, 1088
CX, CY = IMG_W / 2, IMG_H / 2
MAX_DIST = np.sqrt(CX**2 + CY**2)  # corner distance ~910 px

# --- Helper: centre bonus function ---
def centre_bonus(x, y, cx=CX, cy=CY):
    """Return multiplicative centre bonus (5x at centre, 0.2x at edge)."""
    dist = np.sqrt((x - cx)**2 + (y - cy)**2)
    frac = dist / MAX_DIST  # 0 at centre, 1 at corner
    # Smooth decay: 5 * exp(-3*frac^2) clamped to [0.2, 5.0]
    bonus = 5.0 * np.exp(-4.0 * frac**2)
    return np.clip(bonus, 0.2, 5.0)


def compute_weight(x, y, alt_m=35):
    """Combined weight: (1/h^2) * centre_bonus. Normalised for display."""
    inv_h2 = 1.0 / (alt_m ** 2)
    return inv_h2 * centre_bonus(x, y)


# =====================================================================
# Figure
# =====================================================================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.5, 5.5),
                                gridspec_kw={'width_ratios': [1, 1.15]})
fig.subplots_adjust(wspace=0.32, left=0.06, right=0.96, top=0.90, bottom=0.12)

# =====================================================================
# Panel A: Detection Position vs Weight
# =====================================================================

# Draw frame outline
frame_rect = Rectangle((0, 0), IMG_W, IMG_H, linewidth=1.5,
                        edgecolor=TEXT_DARK, facecolor='#f7f9fb')
ax1.add_patch(frame_rect)

# Concentric zone ellipses (20%, 60%, 100% of half-diag)
zone_specs = [
    (0.20, GREEN, '0.15', r'$5\times$ bonus'),
    (0.55, '#f39c12', '0.08', r'$1\times$'),
    (0.90, RED, '0.06', r'$0.2\times$'),
]
for frac, color, alpha, label in zone_specs:
    ew = frac * IMG_W
    eh = frac * IMG_H
    ellipse = Ellipse((CX, CY), ew, eh, linewidth=1.2,
                       edgecolor=color, facecolor=color,
                       alpha=float(alpha), linestyle='--')
    ax1.add_patch(ellipse)

# Generate scattered detection points (biased slightly toward centre — realistic)
n_pts = 45
# Mix: 60% uniform, 40% gaussian near centre
n_uniform = int(n_pts * 0.55)
n_gauss = n_pts - n_uniform

x_uni = np.random.uniform(30, IMG_W - 30, n_uniform)
y_uni = np.random.uniform(30, IMG_H - 30, n_uniform)
x_gauss = np.clip(np.random.normal(CX, IMG_W * 0.25, n_gauss), 30, IMG_W - 30)
y_gauss = np.clip(np.random.normal(CY, IMG_H * 0.25, n_gauss), 30, IMG_H - 30)

det_x = np.concatenate([x_uni, x_gauss])
det_y = np.concatenate([y_uni, y_gauss])

# Compute weights for colour
weights = np.array([centre_bonus(xi, yi) for xi, yi in zip(det_x, det_y)])
norm = Normalize(vmin=0.2, vmax=5.0)
cmap = cm.RdYlGn  # red (low) -> yellow -> green (high)

scatter = ax1.scatter(det_x, det_y, c=weights, cmap=cmap, norm=norm,
                      s=55, edgecolors='white', linewidths=0.6, zorder=5)

# Colorbar
cbar = fig.colorbar(scatter, ax=ax1, shrink=0.75, pad=0.02, aspect=25)
cbar.set_label('Centre Weight', fontsize=9)
cbar.ax.tick_params(labelsize=8)

# Zone labels
ax1.text(CX, CY + 35, r'$5\times$', ha='center', va='center',
         fontsize=10, fontweight='bold', color=GREEN, zorder=6)
ax1.text(CX + IMG_W * 0.22, CY - IMG_H * 0.20, r'$1\times$', ha='center',
         fontsize=9, color='#d68910', zorder=6)
ax1.text(IMG_W - 70, 50, r'$0.2\times$', ha='center',
         fontsize=9, color=RED, zorder=6)

# Crosshair at centre
ax1.axhline(CY, color=GREY, linewidth=0.5, linestyle=':', alpha=0.5)
ax1.axvline(CX, color=GREY, linewidth=0.5, linestyle=':', alpha=0.5)

# Formula annotation
ax1.text(IMG_W * 0.02, -70,
         r'$w_i = \frac{1}{h_i^2} \times \mathrm{centre\_bonus}(x, y)$',
         fontsize=11, color=TEXT_DARK, ha='left', va='top',
         bbox=dict(boxstyle='round,pad=0.3', facecolor='#eaf2f8',
                   edgecolor='#aab7c4', alpha=0.9))

ax1.set_xlim(-10, IMG_W + 10)
ax1.set_ylim(-100, IMG_H + 40)
ax1.set_xlabel('Pixel $x$', fontsize=10)
ax1.set_ylabel('Pixel $y$', fontsize=10)
ax1.set_title('(a)  Detection Position vs Weight', fontsize=11,
              fontweight='bold', pad=8)
ax1.set_aspect('equal')
ax1.tick_params(labelsize=8)

# =====================================================================
# Panel B: Estimate Error vs Pixel Distance from Centre
# =====================================================================

ALT = 35  # metres
HFOV_DEG = 54.4  # calibrated for 1456x1088
FOCAL_PX = 1416  # calibrated focal length in pixels

# Simulate: error grows with off-nadir angle
n_sim = 120
pix_dist = np.random.uniform(0, 720, n_sim)  # pixel distance from centre

# Error model: quadratic + noise
# Off-nadir angle: theta = atan(pix_dist / focal_px)
# Projection error ~ ALT * tan(theta) - ALT * theta  (grows quadratically)
# Plus GPS noise floor ~1.5m, plus random component
theta = np.arctan2(pix_dist, FOCAL_PX)
# Ground distance from nadir point
ground_dist = ALT * np.tan(theta)
# Projection error: difference between flat-earth approx and actual
# Simplified: error ~ k * (pix_dist/max_dist)^2 * ALT_factor + noise
base_error = 1.2 + 6.5 * (pix_dist / 720)**2
noise = np.abs(np.random.normal(0, 0.6 + 1.5 * (pix_dist / 720), n_sim))
gps_error = base_error + noise

# Fit quadratic
coeffs = np.polyfit(pix_dist, gps_error, 2)
fit_x = np.linspace(0, 720, 200)
fit_y = np.polyval(coeffs, fit_x)

# Zone boundaries
RELIABLE = 200   # px
MARGINAL = 500   # px

# Shade zones
ax2.axvspan(0, RELIABLE, alpha=0.12, color=GREEN, zorder=0)
ax2.axvspan(RELIABLE, MARGINAL, alpha=0.10, color='#f1c40f', zorder=0)
ax2.axvspan(MARGINAL, 750, alpha=0.10, color=RED, zorder=0)

# Zone labels (top)
ax2.text(RELIABLE / 2, 9.5, 'Reliable', ha='center', fontsize=8,
         color=GREEN, fontweight='bold', alpha=0.8)
ax2.text((RELIABLE + MARGINAL) / 2, 9.5, 'Marginal', ha='center', fontsize=8,
         color='#d4a017', fontweight='bold', alpha=0.8)
ax2.text((MARGINAL + 720) / 2, 9.5, 'Edge', ha='center', fontsize=8,
         color=RED, fontweight='bold', alpha=0.8)

# Vertical dashed lines
ax2.axvline(RELIABLE, color=GREEN, linewidth=1.0, linestyle='--', alpha=0.7)
ax2.axvline(MARGINAL, color='#d4a017', linewidth=1.0, linestyle='--', alpha=0.7)

# Scatter points
colors = np.where(pix_dist < RELIABLE, GREEN,
          np.where(pix_dist < MARGINAL, '#f39c12', RED))
ax2.scatter(pix_dist, gps_error, c=colors, s=22, alpha=0.6,
            edgecolors='white', linewidths=0.3, zorder=3)

# Fit line
ax2.plot(fit_x, fit_y, color=BLUE, linewidth=2.0, linestyle='-',
         label='Quadratic fit', zorder=4)

# Ground distance annotations at 35m altitude
# ground_dist = ALT * tan(atan(pix_dist / FOCAL_PX))
for px_val in [0, 200, 500, 720]:
    gd = ALT * np.tan(np.arctan2(px_val, FOCAL_PX))
    ax2.annotate(f'{gd:.1f} m',
                 xy=(px_val, -0.3), xycoords=('data', 'data'),
                 fontsize=7, color=GREY, ha='center', va='top')

# Secondary x-axis label for ground distance
ax2.text(360, -1.8, 'Ground distance from nadir at 35 m altitude',
         ha='center', fontsize=8, color=GREY, style='italic')

# Error sources annotation
ax2.annotate('Error sources:\n'
             '  1. Off-nadir projection\n'
             '  2. Lens distortion\n'
             '  3. GSD variation',
             xy=(530, 3.0), fontsize=7.5, color=TEXT_DARK,
             bbox=dict(boxstyle='round,pad=0.4', facecolor='#fef9e7',
                       edgecolor='#f0e6c0', alpha=0.9),
             zorder=5)

ax2.set_xlim(-10, 740)
ax2.set_ylim(-0.5, 10.5)
ax2.set_xlabel('Pixel Distance from Image Centre (px)', fontsize=10)
ax2.set_ylabel('GPS Estimation Error (m)', fontsize=10)
ax2.set_title('(b)  Estimate Error vs Distance from Centre', fontsize=11,
              fontweight='bold', pad=8)
ax2.legend(loc='upper left', fontsize=8, framealpha=0.9)
ax2.tick_params(labelsize=8)
ax2.grid(True, alpha=0.2, linewidth=0.5)

# =====================================================================
# Save
# =====================================================================
out_dir = os.path.dirname(os.path.abspath(__file__))
for ext in ('pdf', 'png'):
    path = os.path.join(out_dir, f'centrality_weighting.{ext}')
    fig.savefig(path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f'Saved: {path}')

plt.close(fig)
