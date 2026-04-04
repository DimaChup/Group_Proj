"""Heading-Dependent GPS Estimation Bias — Single-Pass vs Multi-Pass Cancellation."""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Ellipse, FancyArrowPatch
from pathlib import Path

np.random.seed(42)

# --- Styling ---
TEXT_DARK = '#2c3e50'
BLUE = '#2980b9'
ORANGE = '#e67e22'
GREEN = '#27ae60'
RED = '#c0392b'
GREY = '#7f8c8d'
LIGHT_GREY = '#bdc3c7'

plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 10,
    'axes.labelcolor': TEXT_DARK,
    'text.color': TEXT_DARK,
    'axes.edgecolor': '#cccccc',
    'xtick.color': TEXT_DARK,
    'ytick.color': TEXT_DARK,
})

# --- Shared parameters ---
heading_deg = 155  # flight heading from North (clockwise)
heading_rad = np.radians(heading_deg)
# In our plot coordinate system: x = East, y = North
# heading 155 from North -> dx = sin(155), dy = cos(155)
dir_x = np.sin(heading_rad)   #  0.42
dir_y = np.cos(heading_rad)   # -0.91
perp_x = -dir_y               #  0.91
perp_y = dir_x                #  0.42

# GPS timing lag bias: 100-200ms at 5 m/s = 0.5-1.0m along track
lag_bias = 0.75  # metres along flight direction (mean)

# Noise model: elongated along flight direction due to velocity-correlated errors
along_std = 2.2   # along flight direction
cross_std = 1.0   # perpendicular to flight direction


def generate_pass(heading_deg, n=30):
    """Generate GPS estimates with heading-dependent bias and anisotropic noise."""
    h_rad = np.radians(heading_deg)
    dx = np.sin(h_rad)
    dy = np.cos(h_rad)
    px = -dy
    py = dx

    # Along-track and cross-track noise
    along = np.random.normal(lag_bias, along_std, n)
    cross = np.random.normal(0, cross_std, n)

    x = along * dx + cross * px
    y = along * dy + cross * py
    return x, y


def cep50(x, y, cx=0, cy=0):
    """Compute CEP50 (circular error probable, 50th percentile radius)."""
    dists = np.sqrt((x - cx)**2 + (y - cy)**2)
    return np.median(dists)


def draw_range_rings(ax, radii, color=LIGHT_GREY, ls='--', lw=0.7):
    for r in radii:
        circle = Circle((0, 0), r, fill=False, color=color, ls=ls, lw=lw, zorder=1)
        ax.add_patch(circle)
        ax.text(r * 0.707 + 0.15, r * 0.707 + 0.15, f'{r}m',
                fontsize=7, color=GREY, ha='left', va='bottom')


def draw_heading_arrow(ax, heading_deg, color, label, length=6.5, offset=0):
    """Draw an arrow from near origin showing flight direction."""
    h_rad = np.radians(heading_deg)
    dx = np.sin(h_rad)
    dy = np.cos(h_rad)
    # Offset perpendicular to heading for visibility
    px = -dy * offset
    py = dx * offset
    start_x = -2.0 * dx + px
    start_y = -2.0 * dy + py
    end_x = start_x + length * dx
    end_y = start_y + length * dy
    ax.annotate('', xy=(end_x, end_y), xytext=(start_x, start_y),
                arrowprops=dict(arrowstyle='->', color=color, lw=1.8, ls='-'))
    # Label at midpoint, offset perpendicular
    mid_x = (start_x + end_x) / 2 + 0.6 * (-dy)
    mid_y = (start_y + end_y) / 2 + 0.6 * dx
    ax.text(mid_x, mid_y, label, fontsize=8, color=color,
            ha='center', va='center', rotation=90 - heading_deg,
            fontweight='bold')


def draw_bias_ellipse(ax, cx, cy, heading_deg, along_r, cross_r, color, alpha=0.15):
    """Draw a bias ellipse oriented along the heading."""
    # Matplotlib Ellipse angle is counter-clockwise from x-axis
    # Our heading is clockwise from North (y-axis)
    # Angle from x-axis = 90 - heading
    angle = 90 - heading_deg
    ell = Ellipse((cx, cy), width=2*cross_r, height=2*along_r,
                  angle=angle, fill=True, facecolor=color, edgecolor=color,
                  alpha=alpha, lw=1.5, ls='--', zorder=2)
    ax.add_patch(ell)
    # Also draw outline
    ell2 = Ellipse((cx, cy), width=2*cross_r, height=2*along_r,
                   angle=angle, fill=False, edgecolor=color,
                   alpha=0.5, lw=1.2, ls='--', zorder=2)
    ax.add_patch(ell2)


# ============================================================
# Generate data
# ============================================================
n_pts = 30

# Panel A: single pass at 155 deg
x1, y1 = generate_pass(155, n_pts)
centroid1_x, centroid1_y = np.mean(x1), np.mean(y1)
cep50_single = cep50(x1, y1)

# Panel B: two passes
x_p1, y_p1 = generate_pass(155, n_pts)
x_p2, y_p2 = generate_pass(335, n_pts)  # return leg
centroid_p1_x, centroid_p1_y = np.mean(x_p1), np.mean(y_p1)
centroid_p2_x, centroid_p2_y = np.mean(x_p2), np.mean(y_p2)
x_all = np.concatenate([x_p1, x_p2])
y_all = np.concatenate([y_p1, y_p2])
centroid_all_x, centroid_all_y = np.mean(x_all), np.mean(y_all)
cep50_p1 = cep50(x_p1, y_p1)
cep50_combined = cep50(x_all, y_all, centroid_all_x, centroid_all_y)

# ============================================================
# Figure
# ============================================================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.5))

lim = 7.5

# ============================================================
# Panel A: Single-Pass Heading Bias
# ============================================================
ax = ax1
ax.set_title('(a) Single-Pass Heading Bias', fontsize=12, fontweight='bold', pad=10)

# Range rings
draw_range_rings(ax, [2, 5])

# Scatter
ax.scatter(x1, y1, s=28, c=BLUE, alpha=0.7, edgecolors='white', linewidths=0.3, zorder=5,
           label='GPS estimates')

# True position
ax.plot(0, 0, 'x', color=RED, markersize=10, markeredgewidth=2.5, zorder=10)
ax.text(0.3, 0.3, 'True position', fontsize=8, color=RED, fontweight='bold', zorder=10)

# Centroid
ax.plot(centroid1_x, centroid1_y, 'D', color=BLUE, markersize=8, markeredgecolor='white',
        markeredgewidth=1, zorder=8, label=f'Centroid (bias = {np.sqrt(centroid1_x**2+centroid1_y**2):.1f}m)')

# CEP50 circle
cep_circle = Circle((centroid1_x, centroid1_y), cep50_single, fill=False,
                     color=GREEN, lw=1.5, ls='-', zorder=4)
ax.add_patch(cep_circle)
ax.text(centroid1_x + cep50_single * 0.707 + 0.2,
        centroid1_y + cep50_single * 0.707 + 0.2,
        f'CEP50 = {cep50_single:.1f}m', fontsize=8, color=GREEN, fontweight='bold')

# Bias ellipse (1-sigma)
draw_bias_ellipse(ax, centroid1_x, centroid1_y, 155, along_std, cross_std, BLUE)

# Flight direction arrow
draw_heading_arrow(ax, 155, GREY, 'Heading 155\u00b0', length=7, offset=0.5)

# Annotation
ax.annotate('GPS timing lag: 100\u2013200 ms\nat 5 m/s \u2192 0.5\u20131.0 m along-track shift',
            xy=(centroid1_x, centroid1_y), xytext=(-6.5, 5.5),
            fontsize=8, color=TEXT_DARK, style='italic',
            arrowprops=dict(arrowstyle='->', color=GREY, lw=1),
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#f8f8f8', edgecolor=GREY, alpha=0.9))

ax.set_xlim(-lim, lim)
ax.set_ylim(-lim, lim)
ax.set_aspect('equal')
ax.set_xlabel('East (m)', fontsize=10)
ax.set_ylabel('North (m)', fontsize=10)
ax.axhline(0, color=LIGHT_GREY, lw=0.5, zorder=0)
ax.axvline(0, color=LIGHT_GREY, lw=0.5, zorder=0)
ax.legend(loc='lower left', fontsize=8, framealpha=0.9)
ax.grid(True, alpha=0.15)

# ============================================================
# Panel B: Multi-Pass Cancellation
# ============================================================
ax = ax2
ax.set_title('(b) Multi-Pass Cancellation', fontsize=12, fontweight='bold', pad=10)

# Range rings
draw_range_rings(ax, [2, 5])

# Scatter — pass 1
ax.scatter(x_p1, y_p1, s=28, c=BLUE, alpha=0.6, edgecolors='white', linewidths=0.3,
           zorder=5, label=f'Pass 1 (155\u00b0)')

# Scatter — pass 2
ax.scatter(x_p2, y_p2, s=28, c=ORANGE, alpha=0.6, edgecolors='white', linewidths=0.3,
           zorder=5, label=f'Pass 2 (335\u00b0)')

# True position
ax.plot(0, 0, 'x', color=RED, markersize=10, markeredgewidth=2.5, zorder=10)
ax.text(0.3, 0.3, 'True position', fontsize=8, color=RED, fontweight='bold', zorder=10)

# Pass 1 centroid
ax.plot(centroid_p1_x, centroid_p1_y, 'D', color=BLUE, markersize=7,
        markeredgecolor='white', markeredgewidth=1, zorder=8)

# Pass 2 centroid
ax.plot(centroid_p2_x, centroid_p2_y, 'D', color=ORANGE, markersize=7,
        markeredgecolor='white', markeredgewidth=1, zorder=8)

# Combined centroid
ax.plot(centroid_all_x, centroid_all_y, '*', color=GREEN, markersize=16,
        markeredgecolor='white', markeredgewidth=0.8, zorder=9,
        label=f'Combined centroid ({np.sqrt(centroid_all_x**2+centroid_all_y**2):.1f}m from true)')

# CEP50 for pass 1 only (dashed)
cep_p1 = Circle((centroid_p1_x, centroid_p1_y), cep50_p1, fill=False,
                 color=BLUE, lw=1.2, ls=':', zorder=4)
ax.add_patch(cep_p1)
ax.text(centroid_p1_x - cep50_p1 - 0.8, centroid_p1_y - 0.3,
        f'Pass 1\nCEP50={cep50_p1:.1f}m', fontsize=7, color=BLUE, ha='right')

# CEP50 for combined
cep_comb = Circle((centroid_all_x, centroid_all_y), cep50_combined, fill=False,
                   color=GREEN, lw=1.8, ls='-', zorder=4)
ax.add_patch(cep_comb)
ax.text(centroid_all_x + cep50_combined * 0.707 + 0.2,
        centroid_all_y + cep50_combined * 0.707 + 0.2,
        f'Combined\nCEP50={cep50_combined:.1f}m', fontsize=8, color=GREEN, fontweight='bold')

# Bias ellipses
draw_bias_ellipse(ax, centroid_p1_x, centroid_p1_y, 155, along_std * 0.8, cross_std * 0.8, BLUE, alpha=0.08)
draw_bias_ellipse(ax, centroid_p2_x, centroid_p2_y, 335, along_std * 0.8, cross_std * 0.8, ORANGE, alpha=0.08)

# Flight direction arrows
draw_heading_arrow(ax, 155, BLUE, '155\u00b0', length=6, offset=0.8)
draw_heading_arrow(ax, 335, ORANGE, '335\u00b0', length=6, offset=0.8)

# Annotation
ax.annotate('Lawnmower alternating legs\ncancel heading bias',
            xy=(centroid_all_x, centroid_all_y), xytext=(3.0, 5.5),
            fontsize=8, color=TEXT_DARK, style='italic', fontweight='bold',
            arrowprops=dict(arrowstyle='->', color=GREEN, lw=1.2),
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#f0faf0', edgecolor=GREEN, alpha=0.9))

ax.set_xlim(-lim, lim)
ax.set_ylim(-lim, lim)
ax.set_aspect('equal')
ax.set_xlabel('East (m)', fontsize=10)
ax.set_ylabel('North (m)', fontsize=10)
ax.axhline(0, color=LIGHT_GREY, lw=0.5, zorder=0)
ax.axvline(0, color=LIGHT_GREY, lw=0.5, zorder=0)
ax.legend(loc='lower left', fontsize=8, framealpha=0.9)
ax.grid(True, alpha=0.15)

# ============================================================
# Save
# ============================================================
fig.tight_layout(w_pad=2.5)

out = Path(__file__).parent
fig.savefig(out / 'heading_bias.pdf', dpi=300, bbox_inches='tight')
fig.savefig(out / 'heading_bias.png', dpi=300, bbox_inches='tight')
print(f'Saved heading_bias.pdf and .png to {out}')
plt.show()
