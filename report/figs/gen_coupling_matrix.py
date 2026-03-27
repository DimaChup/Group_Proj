"""
Generate coupling matrix and altitude-speed tradeoff figures.
Output: coupling_matrix.pdf/.png, altitude_speed_tradeoff.pdf/.png
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.patches import FancyBboxPatch
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ── Style ──────────────────────────────────────────────────────────────
plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 9,
    'axes.titlesize': 12,
    'axes.labelsize': 10,
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.15,
})

# ══════════════════════════════════════════════════════════════════════
# FIGURE 1 — Variable Coupling Matrix
# ══════════════════════════════════════════════════════════════════════

variables = [
    r'Altitude $h$',
    r'Speed $v$',
    r'Scan angle $\theta$',
    r'Overlap $\alpha$',
    r'NFZ margin $d_{\mathrm{nfz}}$',
]
short = ['h', 'v', r'\theta', r'\alpha', r'd_{\mathrm{nfz}}']

# Diagonal labels
diag_labels = [
    'Detection\nceiling',
    'Frame\ncount',
    'Turn\ncount',
    'Redundancy',
    'Safety\nmargin',
]

# Coupling strengths: 0=self, 1=weak, 2=medium, 3=strong
# Matrix[row][col]  (symmetric)
strength = np.array([
    [0, 3, 1, 2, 2],
    [3, 0, 1, 1, 2],
    [1, 1, 0, 1, 2],
    [2, 1, 1, 0, 1],
    [2, 2, 2, 1, 0],
])

# Off-diagonal annotations: (strength_word, metric_affected)
annotations = {
    (0,1): ('Strong', 'Coverage rate\n+ detection prob.'),
    (0,2): ('Weak',   'Scan\nefficiency'),
    (0,3): ('Medium', 'Lane\nspacing'),
    (0,4): ('Medium', 'Footprint\nintrusion'),
    (1,2): ('Weak',   'Independent'),
    (1,3): ('Weak',   'Independent'),
    (1,4): ('Medium', 'Reaction\ndistance'),
    (2,3): ('Weak',   'Independent'),
    (2,4): ('Medium', 'NFZ\nproximity'),
    (3,4): ('Weak',   'Independent'),
}
# Fill symmetric
for (r, c), v in list(annotations.items()):
    annotations[(c, r)] = v

# Color map: white (self) → light (weak) → dark (strong)
cmap_data = {
    0: '#F0F0F0',   # self / diagonal
    1: '#D4E8D4',   # weak  — light green
    2: '#F5C77E',   # medium — amber
    3: '#D9534F',   # strong — red-ish
}

n = len(variables)
fig, ax = plt.subplots(figsize=(8.5, 7.5))
ax.set_xlim(-0.5, n - 0.5)
ax.set_ylim(n - 0.5, -0.5)
ax.set_aspect('equal')
ax.set_xticks(range(n))
ax.set_yticks(range(n))
ax.set_xticklabels(variables, fontsize=8.5, ha='center')
ax.set_yticklabels(variables, fontsize=8.5)
ax.tick_params(length=0)

# Move x-axis labels to top
ax.xaxis.tick_top()
ax.xaxis.set_label_position('top')

for spine in ax.spines.values():
    spine.set_visible(False)

for i in range(n):
    for j in range(n):
        s = strength[i, j]
        color = cmap_data[s]
        rect = FancyBboxPatch(
            (j - 0.48, i - 0.48), 0.96, 0.96,
            boxstyle='round,pad=0.02',
            facecolor=color, edgecolor='#888888', linewidth=0.6,
        )
        ax.add_patch(rect)

        if i == j:
            # Diagonal
            ax.text(j, i - 0.12, f'${short[i]}$', ha='center', va='center',
                    fontsize=10, fontweight='bold', color='#333333')
            ax.text(j, i + 0.18, diag_labels[i], ha='center', va='center',
                    fontsize=7, color='#555555', style='italic')
        else:
            word, metric = annotations[(i, j)]
            weight_color = {'Strong': '#8B0000', 'Medium': '#7A5200', 'Weak': '#2E6B2E'}
            ax.text(j, i - 0.18, word, ha='center', va='center',
                    fontsize=7.5, fontweight='bold', color=weight_color[word])
            ax.text(j, i + 0.15, metric, ha='center', va='center',
                    fontsize=6.2, color='#333333', linespacing=1.1)

# Legend
from matplotlib.patches import Patch
legend_patches = [
    Patch(facecolor=cmap_data[3], edgecolor='#888', label='Strong coupling'),
    Patch(facecolor=cmap_data[2], edgecolor='#888', label='Medium coupling'),
    Patch(facecolor=cmap_data[1], edgecolor='#888', label='Weak / independent'),
    Patch(facecolor=cmap_data[0], edgecolor='#888', label='Self (primary metric)'),
]
ax.legend(handles=legend_patches, loc='lower center', ncol=4, fontsize=7.5,
          frameon=True, framealpha=0.9, edgecolor='#CCCCCC',
          bbox_to_anchor=(0.5, -0.06))

ax.set_title('Variable Coupling Matrix — Pairwise Interaction Effects',
             fontsize=12, fontweight='bold', pad=14, y=1.08)

for fmt in ['pdf', 'png']:
    fig.savefig(os.path.join(OUT_DIR, f'coupling_matrix.{fmt}'))
print('Saved coupling_matrix.pdf/.png')
plt.close(fig)


# ══════════════════════════════════════════════════════════════════════
# FIGURE 2 — Altitude–Speed Trade-off
# ══════════════════════════════════════════════════════════════════════

# Physical model parameters
SEARCH_AREA_M2 = 18000        # ~18 000 m² survey polygon
HFOV_DEG = 54.4               # calibrated camera HFOV
OVERLAP_FRAC = 0.20           # 20 % overlap
DUMMY_HEIGHT_M = 1.8          # target size
BASELINE_DET_PROB = 0.995     # mAP50 at optimal conditions
ENERGY_HOVER_W = 350          # hover power (W) — typical quad
ENERGY_SPEED_COEFF = 8        # extra W per (m/s)² for forward flight

alt = np.linspace(20, 50, 200)
spd = np.linspace(5, 15, 200)
H, V = np.meshgrid(alt, spd)

# Swath width (m)
swath = 2 * H * np.tan(np.radians(HFOV_DEG / 2))
lane_spacing = swath * (1 - OVERLAP_FRAC)

# Coverage rate (m²/s)
cov_rate = lane_spacing * V

# Coverage time (s) for entire area
cov_time = SEARCH_AREA_M2 / cov_rate

# Detection probability model:
#   - degrades with altitude (GSD grows → fewer pixels on target)
#   - degrades with speed (motion blur, fewer frames on target)
gsd = H / 640.0  # ground sampling distance proxy (px pitch at altitude)
pixels_on_target = DUMMY_HEIGHT_M / gsd
# Sigmoid: near 1.0 when pixels_on_target > ~15, drops toward 0 below ~5
det_alt = 1.0 / (1.0 + np.exp(-0.6 * (pixels_on_target - 8)))

# Speed penalty: dwell time on target decreases
dwell_frames = swath / V / 0.208  # frames while target in FOV (208ms per frame)
det_speed = 1.0 - np.exp(-0.3 * dwell_frames)

det_prob = BASELINE_DET_PROB * det_alt * det_speed

# Energy efficiency (m² per Wh)
power = ENERGY_HOVER_W + ENERGY_SPEED_COEFF * V**2
energy_eff = cov_rate / power * 3600  # m² per Wh

# Normalise each to [0, 1] for composite
def norm01(x):
    return (x - x.min()) / (x.max() - x.min())

composite = (
    0.40 * norm01(det_prob) +
    0.35 * norm01(cov_rate) +
    0.25 * norm01(energy_eff)
)

# ── Plot ───────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(8, 6))

# Main heatmap
cf = ax.contourf(H, V, composite, levels=30, cmap='RdYlGn')
cb = fig.colorbar(cf, ax=ax, label='Composite score (detection + coverage + energy)',
                  pad=0.02)
cb.ax.tick_params(labelsize=8)

# Detection probability contours
det_levels = [0.90, 0.95, 0.99]
cs_det = ax.contour(H, V, det_prob, levels=det_levels,
                     colors=['#1a1aff', '#0000cc', '#000088'],
                     linewidths=1.4, linestyles='--')
ax.clabel(cs_det, fmt={0.90: r'$P_d$=90%', 0.95: r'$P_d$=95%', 0.99: r'$P_d$=99%'},
          fontsize=7.5, inline_spacing=3)

# Coverage time contours
time_levels = [120, 180]
cs_time = ax.contour(H, V, cov_time, levels=time_levels,
                      colors=['#cc6600', '#994d00'],
                      linewidths=1.4, linestyles='-.')
ax.clabel(cs_time, fmt={120: r'$t_{cov}$=120 s', 180: r'$t_{cov}$=180 s'},
          fontsize=7.5, inline_spacing=3)

# Operating point
op_h, op_v = 35, 8
ax.plot(op_h, op_v, marker='*', markersize=16, color='black',
        markeredgecolor='white', markeredgewidth=1.0, zorder=10)
ax.annotate(f'Selected\n({op_h} m, {op_v} m/s)', xy=(op_h, op_v),
            xytext=(op_h + 4, op_v - 2.2),
            fontsize=8.5, fontweight='bold',
            arrowprops=dict(arrowstyle='->', color='black', lw=1.2),
            bbox=dict(boxstyle='round,pad=0.3', fc='white', ec='black', alpha=0.85))

# Proxy artists for legend
from matplotlib.lines import Line2D
legend_elems = [
    Line2D([0], [0], color='#1a1aff', ls='--', lw=1.4, label='Detection probability'),
    Line2D([0], [0], color='#cc6600', ls='-.', lw=1.4, label='Coverage time'),
    Line2D([0], [0], marker='*', color='black', markersize=12, ls='None',
           markeredgecolor='white', label='Operating point'),
]
ax.legend(handles=legend_elems, loc='upper left', fontsize=8, framealpha=0.9,
          edgecolor='#CCCCCC')

ax.set_xlabel('Altitude $h$ (m)')
ax.set_ylabel('Ground speed $v$ (m/s)')
ax.set_title('Altitude–Speed Trade-off: Composite Mission Score',
             fontsize=12, fontweight='bold')
ax.grid(True, alpha=0.25, linewidth=0.5)

for fmt in ['pdf', 'png']:
    fig.savefig(os.path.join(OUT_DIR, f'altitude_speed_tradeoff.{fmt}'))
print('Saved altitude_speed_tradeoff.pdf/.png')
plt.close(fig)
