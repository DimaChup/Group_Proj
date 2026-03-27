"""Generate sensitivity matrix heatmap and spider chart."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import os

OUT = os.path.dirname(os.path.abspath(__file__))

# ── Style ──
plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 10,
    'axes.titlesize': 13,
    'axes.labelsize': 11,
    'figure.dpi': 300,
})

# ═══════════════════════════════════════════════════════════
# 1. SENSITIVITY MATRIX HEATMAP
# ═══════════════════════════════════════════════════════════

inputs = [
    r'Altitude ($h$)',
    r'Ground speed ($v$)',
    r'Scan angle ($\theta$)',
    r'Overlap fraction ($\alpha$)',
    r'NFZ margin ($d_{\mathrm{nfz}}$)',
]

outputs = ['Coverage\n%', 'Detection\nP', 'Mission\nTime', 'Energy\n(Wh)', 'NFZ\nRisk']

values = np.array([
    [+0.6, -0.8, -0.5, -0.4, +0.3],
    [ 0.0, -0.4, -0.7, -0.3, +0.2],
    [+0.1,  0.0, +0.3, +0.4, +0.2],
    [+0.3, +0.1, +0.4, +0.4,  0.0],
    [-0.4,  0.0, +0.1, +0.1, -0.9],
])

notes = [
    ['wider\nlanes',   'smaller\ntarget', 'fewer\nlines',  'fewer lines\nmore drag', 'wider\nfootprint'],
    ['no\neffect',     'fewer\nframes',   'faster\ncover', 'less hover\ntime',       'less reaction\ntime'],
    ['minimal',        'no\neffect',      'turn\ncount',   'turn\ncount',            'NFZ\nproximity'],
    ['redundancy',     'marginal',        'more\nlines',   'more\nlines',            'no\neffect'],
    ['less\narea',     'no\neffect',      'marginal',      'marginal',               'much\nsafer'],
]

# Diverging colourmap: red (negative) ─ white (0) ─ green (positive)
cmap = mcolors.LinearSegmentedColormap.from_list(
    'RdWtGn',
    [(0.85, 0.22, 0.20), (1, 1, 1), (0.20, 0.66, 0.33)],
    N=256,
)
norm = mcolors.TwoSlopeNorm(vmin=-1, vcenter=0, vmax=1)

fig, ax = plt.subplots(figsize=(9.5, 5.5))
im = ax.imshow(values, cmap=cmap, norm=norm, aspect='auto')

ax.set_xticks(range(len(outputs)))
ax.set_xticklabels(outputs, fontsize=10, fontweight='bold')
ax.xaxis.tick_top()
ax.xaxis.set_label_position('top')

ax.set_yticks(range(len(inputs)))
ax.set_yticklabels(inputs, fontsize=10)

# Annotate cells: value + note
for i in range(len(inputs)):
    for j in range(len(outputs)):
        v = values[i, j]
        sign = '+' if v > 0 else ''
        txt = f'{sign}{v:.1f}\n{notes[i][j]}'
        color = 'white' if abs(v) > 0.65 else 'black'
        ax.text(j, i, txt, ha='center', va='center', fontsize=7.5,
                color=color, linespacing=1.15)

# Grid
for edge in range(len(inputs) + 1):
    ax.axhline(edge - 0.5, color='white', linewidth=1.5)
for edge in range(len(outputs) + 1):
    ax.axvline(edge - 0.5, color='white', linewidth=1.5)

ax.set_title('Sensitivity Matrix: Input Variables vs Performance Metrics',
             pad=32, fontsize=13, fontweight='bold')

# Arrow annotations: up-arrow meaning
ax.annotate(r'$\uparrow$ = increasing input improves metric (+green) or worsens it ($-$red)',
            xy=(0.5, -0.04), xycoords='axes fraction', ha='center', fontsize=8,
            color='#555555')

cbar = fig.colorbar(im, ax=ax, fraction=0.025, pad=0.04)
cbar.set_label('Influence strength', fontsize=9)
cbar.set_ticks([-1, -0.5, 0, 0.5, 1])

plt.tight_layout()
fig.savefig(os.path.join(OUT, 'sensitivity_matrix.pdf'), bbox_inches='tight')
fig.savefig(os.path.join(OUT, 'sensitivity_matrix.png'), bbox_inches='tight', dpi=300)
plt.close(fig)
print('Saved sensitivity_matrix.pdf + .png')


# ═══════════════════════════════════════════════════════════
# 2. SPIDER / RADAR CHART
# ═══════════════════════════════════════════════════════════

categories = ['Coverage', 'Detection', 'Time', 'Energy', 'NFZ Safety']
N = len(categories)

# Selected config scores (normalised 0-1, higher = better)
selected = [
    96 / 100,          # Coverage 96%
    92 / 99,           # Detection probability
    1 - (112 / 180),   # Time: 112s out of ~180s worst case → inverted (lower is better)
    1 - (15 / 25),     # Energy: 15 Wh out of ~25 Wh worst → inverted
    50 / 50,           # NFZ safety margin: 50m / 50m target
]

# Theoretical best
best = [1.0, 1.0, 1.0, 1.0, 1.0]

# Raw values for annotation
raw_selected = ['96%', '92%', '112 s', '15 Wh', '50 m']
raw_best     = ['100%', '99%', '60 s', '8.2 Wh', '50 m']

angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
# Close the polygon
selected += selected[:1]
best += best[:1]
angles += angles[:1]

fig, ax = plt.subplots(figsize=(6.5, 6.5), subplot_kw=dict(polar=True))

ax.plot(angles, best, 'o--', color='#999999', linewidth=1.2, markersize=5, label='Theoretical best')
ax.fill(angles, best, alpha=0.06, color='grey')

ax.plot(angles, selected, 'o-', color='#2166ac', linewidth=2, markersize=7, label='Selected config')
ax.fill(angles, selected, alpha=0.18, color='#2166ac')

# Category labels with raw values
label_lines = []
for i in range(N):
    label_lines.append(f'{categories[i]}\n{raw_selected[i]} / {raw_best[i]}')

ax.set_xticks(angles[:-1])
ax.set_xticklabels(label_lines, fontsize=9.5, fontweight='bold')

ax.set_ylim(0, 1.1)
ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8', '1.0'], fontsize=7, color='#888888')
ax.yaxis.grid(True, color='#cccccc', linestyle='--', linewidth=0.5)
ax.xaxis.grid(True, color='#cccccc', linewidth=0.5)

# Annotate selected values on the plot
for i in range(N):
    angle = angles[i]
    r = selected[i]
    ax.annotate(f'{r:.2f}', xy=(angle, r), fontsize=8, fontweight='bold',
                color='#2166ac', ha='center', va='bottom',
                xytext=(0, 8), textcoords='offset points')

ax.set_title('Selected Configuration Performance\n(35 m, 8 m/s, 70\u00b0, 20%, 30 m margin)',
             pad=28, fontsize=12, fontweight='bold')

ax.legend(loc='lower right', bbox_to_anchor=(1.25, -0.05), fontsize=9, framealpha=0.9)

plt.tight_layout()
fig.savefig(os.path.join(OUT, 'sensitivity_spider.pdf'), bbox_inches='tight')
fig.savefig(os.path.join(OUT, 'sensitivity_spider.png'), bbox_inches='tight', dpi=300)
plt.close(fig)
print('Saved sensitivity_spider.pdf + .png')
