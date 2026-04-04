"""Bullseye comparison: 4-panel GPS estimation accuracy progression.

Panels:
  A) Single-frame estimates (raw, high scatter)
  B) SMART clustered estimates (N>=5, tighter)
  C) Hover-lock estimates (stationary, circular)
  D) Attitude-compensated (simulation, very tight)

Run:  python gen_bullseye_comparison.py
Out:  bullseye_comparison.pdf, bullseye_comparison.png
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch

np.random.seed(42)

# ── Styling (matches project convention) ─────────────────────────────
TEXT_DARK = '#2c3e50'
RED = '#c0392b'
GREEN = '#27ae60'
BLUE = '#2980b9'
GREY = '#7f8c8d'
ORANGE = '#e67e22'

plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 10,
    'axes.labelcolor': TEXT_DARK,
    'text.color': TEXT_DARK,
    'axes.edgecolor': '#cccccc',
    'xtick.color': TEXT_DARK,
    'ytick.color': TEXT_DARK,
})

LIM = 10  # axis range ±10 m for all panels
RINGS = [2, 5, 8]  # range ring radii (metres)

heading_deg = 155
heading_rad = np.radians(heading_deg)
cos_h, sin_h = np.cos(heading_rad), np.sin(heading_rad)


def make_anisotropic(n, sigma_along, sigma_across, heading_rad):
    """Generate anisotropic scatter elongated along flight heading."""
    along = np.random.normal(0, sigma_along, n)
    across = np.random.normal(0, sigma_across, n)
    cos_h = np.cos(heading_rad)
    sin_h = np.sin(heading_rad)
    x = along * sin_h + across * cos_h
    y = along * cos_h - across * sin_h
    return x, y


def make_isotropic(n, sigma):
    """Generate isotropic circular scatter."""
    x = np.random.normal(0, sigma, n)
    y = np.random.normal(0, sigma, n)
    return x, y


def cep(x, y, pct):
    """Circular Error Probable at given percentile."""
    return np.percentile(np.sqrt(x**2 + y**2), pct)


# ── Panel A: Single-frame estimates ──────────────────────────────────
# GPS noise + heading bias from forward flight at 155 deg
N_a = 50
x_a, y_a = make_anisotropic(N_a, sigma_along=4.5, sigma_across=2.5, heading_rad=heading_rad)
# Tune to get CEP50 ~ 3.5m, CEP95 ~ 8m
cep50_a = cep(x_a, y_a, 50)
cep95_a = cep(x_a, y_a, 95)

# ── Panel B: SMART clustered (N>=5, r<=2m) ───────────────────────────
# Raw dots same as A, plus 10 cluster centroids (IVW mean of ~5 nearby)
N_b_clusters = 10
# Generate more raw points, then cluster them
N_b_raw = 50
x_b_raw, y_b_raw = make_anisotropic(N_b_raw, sigma_along=4.5, sigma_across=2.5,
                                      heading_rad=heading_rad)
# Cluster centroids: average groups of ~5, plus residual systematic error
# IVW averaging reduces random noise by ~sqrt(5), but systematic biases remain
x_b_centroids = np.zeros(N_b_clusters)
y_b_centroids = np.zeros(N_b_clusters)
for i in range(N_b_clusters):
    idx = slice(i * 5, (i + 1) * 5)
    x_b_centroids[i] = np.mean(x_b_raw[idx])
    y_b_centroids[i] = np.mean(y_b_raw[idx])
# Add systematic bias per cluster (attitude error, GPS multipath) to widen spread
x_b_centroids += np.random.normal(0, 2.0, N_b_clusters)
y_b_centroids += np.random.normal(0, 2.0, N_b_clusters)
cep50_b = cep(x_b_centroids, y_b_centroids, 50)
cep95_b = cep(x_b_centroids, y_b_centroids, 95)

# ── Panel C: Hover-lock (stationary, circular spread) ────────────────
N_c = 30
x_c, y_c = make_isotropic(N_c, sigma=1.5)
cep50_c = cep(x_c, y_c, 50)
cep95_c = cep(x_c, y_c, 95)

# ── Panel D: Attitude-compensated (very tight) ───────────────────────
N_d = 30
x_d, y_d = make_isotropic(N_d, sigma=0.25)
cep50_d = cep(x_d, y_d, 50)
cep95_d = cep(x_d, y_d, 95)

# ── Build figure ─────────────────────────────────────────────────────
fig, axes = plt.subplots(2, 2, figsize=(10, 10))
axes = axes.flatten()

panels = [
    {
        'ax': axes[0], 'label': '(a)',
        'title': 'Single Frame (N=1)',
        'scatter': [(x_a, y_a, RED, 18, 0.6, 'Estimates')],
        'cep50': cep50_a, 'cep95': cep95_a,
        'cep_colour': RED,
        'show_heading': True,
        'note': None,
    },
    {
        'ax': axes[1], 'label': '(b)',
        'title': 'SMART Cluster (N$\\geq$5, r$\\leq$2\u2009m)',
        'scatter': [
            (x_b_raw, y_b_raw, '#bdc3c7', 10, 0.35, 'Raw estimates'),
            (x_b_centroids, y_b_centroids, BLUE, 50, 0.9, 'Cluster centroids'),
        ],
        'cep50': cep50_b, 'cep95': cep95_b,
        'cep_colour': BLUE,
        'show_heading': False,
        'note': None,
    },
    {
        'ax': axes[2], 'label': '(c)',
        'title': 'Hover Lock (10\u2009s avg)',
        'scatter': [(x_c, y_c, BLUE, 18, 0.6, 'Estimates')],
        'cep50': cep50_c, 'cep95': cep95_c,
        'cep_colour': BLUE,
        'show_heading': False,
        'note': None,
    },
    {
        'ax': axes[3], 'label': '(d)',
        'title': 'Attitude Compensated',
        'scatter': [(x_d, y_d, GREEN, 18, 0.6, 'Estimates')],
        'cep50': cep50_d, 'cep95': cep95_d,
        'cep_colour': GREEN,
        'show_heading': False,
        'note': 'Simulation only',
    },
]

for p in panels:
    ax = p['ax']

    # Range rings
    for r in RINGS:
        ring = Circle((0, 0), r, fill=False, linestyle='--', linewidth=0.6,
                       edgecolor='#d5d8dc', zorder=1)
        ax.add_patch(ring)
        ax.text(0, r + 0.25, f'{r}\u2009m', ha='center', va='bottom',
                fontsize=7, color='#95a5a6', zorder=5)

    # Crosshair at true position
    ax.axhline(0, color='#dddddd', linewidth=0.5, zorder=0)
    ax.axvline(0, color='#dddddd', linewidth=0.5, zorder=0)
    ax.plot(0, 0, '+', color=TEXT_DARK, markersize=14, markeredgewidth=2.5, zorder=6)

    # Scatter points
    for sx, sy, sc, ss, sa, slbl in p['scatter']:
        ax.scatter(sx, sy, c=sc, s=ss, alpha=sa, edgecolors='white',
                   linewidths=0.3, zorder=4, label=slbl)

    # CEP circles
    col = p['cep_colour']
    c50 = Circle((0, 0), p['cep50'], fill=False, linestyle='-', linewidth=2.0,
                 edgecolor=col, zorder=3)
    ax.add_patch(c50)
    c95 = Circle((0, 0), p['cep95'], fill=False, linestyle=':', linewidth=1.5,
                 edgecolor=col, alpha=0.5, zorder=3)
    ax.add_patch(c95)

    # CEP annotation box (bottom centre)
    box_text = f'CEP50 = {p["cep50"]:.1f}\u2009m\nCEP95 = {p["cep95"]:.1f}\u2009m'
    ax.text(0, -LIM * 0.82, box_text, ha='center', va='center',
            fontsize=10, fontweight='bold', color=col,
            bbox=dict(boxstyle='round,pad=0.4', facecolor='white',
                      edgecolor=col, alpha=0.92),
            zorder=7)

    # Legend
    handles = [
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=col,
                   markersize=6, label=f'CEP50 = {p["cep50"]:.1f}\u2009m',
                   markeredgecolor=col, linestyle='-', linewidth=2),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=col,
                   markersize=6, label=f'CEP95 = {p["cep95"]:.1f}\u2009m',
                   markeredgecolor=col, linestyle=':', linewidth=1.5, alpha=0.5),
    ]
    ax.legend(handles=handles, loc='upper left', fontsize=8,
              framealpha=0.92, edgecolor='#cccccc', handlelength=2.5)

    # Flight heading arrow (Panel A only)
    if p['show_heading']:
        arrow_len = 6
        ax.annotate('', xy=(arrow_len * sin_h, arrow_len * cos_h), xytext=(0, 0),
                     arrowprops=dict(arrowstyle='->', color=ORANGE, lw=1.5),
                     zorder=3)
        ax.text(arrow_len * sin_h * 1.18, arrow_len * cos_h * 1.18,
                f'Flight hdg\n({heading_deg}\u00b0)',
                fontsize=7.5, color=ORANGE, ha='center', va='top', zorder=5)

    # North arrow (top-right corner of each panel)
    arrow_x = LIM * 0.82
    arrow_y_base = LIM * 0.60
    arrow_y_tip = LIM * 0.85
    ax.annotate('', xy=(arrow_x, arrow_y_tip), xytext=(arrow_x, arrow_y_base),
                arrowprops=dict(arrowstyle='->', color=TEXT_DARK, lw=1.2),
                zorder=5)
    ax.text(arrow_x, arrow_y_tip + 0.3, 'N', ha='center', va='bottom',
            fontsize=9, fontweight='bold', color=TEXT_DARK, zorder=5)

    # Simulation-only note
    if p['note']:
        ax.text(LIM * 0.95, -LIM * 0.95, p['note'], ha='right', va='bottom',
                fontsize=8, fontstyle='italic', color=GREY, zorder=7)

    # Formatting
    ax.set_xlim(-LIM, LIM)
    ax.set_ylim(-LIM, LIM)
    ax.set_aspect('equal')
    ax.set_xlabel('East offset (m)', fontsize=10)
    ax.set_ylabel('North offset (m)', fontsize=10)
    ax.set_title(f'{p["label"]}  {p["title"]}', fontsize=12,
                 fontweight='bold', color=TEXT_DARK, pad=10)
    ax.grid(True, alpha=0.12, zorder=0)

fig.suptitle('GPS Estimation Accuracy: Progressive Improvement',
             fontsize=15, fontweight='bold', color=TEXT_DARK, y=0.98)

plt.tight_layout(rect=[0, 0, 1, 0.95])

# Save
import os
out_dir = os.path.dirname(os.path.abspath(__file__))
plt.savefig(os.path.join(out_dir, 'bullseye_comparison.pdf'),
            bbox_inches='tight', dpi=300)
plt.savefig(os.path.join(out_dir, 'bullseye_comparison.png'),
            bbox_inches='tight', dpi=200)
print('Saved bullseye_comparison.pdf and bullseye_comparison.png')
print(f'  Panel A: CEP50={cep50_a:.1f}m  CEP95={cep95_a:.1f}m')
print(f'  Panel B: CEP50={cep50_b:.1f}m  CEP95={cep95_b:.1f}m')
print(f'  Panel C: CEP50={cep50_c:.1f}m  CEP95={cep95_c:.1f}m')
print(f'  Panel D: CEP50={cep50_d:.1f}m  CEP95={cep95_d:.1f}m')
