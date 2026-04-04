#!/usr/bin/env python3
"""Generate module dependency diagram with LOC coloring."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'DejaVu Serif'],
    'font.size': 10,
    'axes.labelsize': 11,
    'axes.titlesize': 12,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.05,
})

# --- Module data (from wc -l and CLAUDE.md architecture) ---
modules = {
    'config':        {'loc': 290,  'layer': 'config',         'pos': (0.5, 0.85)},
    'states':        {'loc': 22,   'layer': 'config',         'pos': (0.5, 0.65)},
    'utils':         {'loc': 170,  'layer': 'independent',    'pos': (0.2, 0.45)},
    'vision':        {'loc': 774,  'layer': 'independent',    'pos': (0.5, 0.45)},
    'planning':      {'loc': 335,  'layer': 'independent',    'pos': (0.8, 0.45)},
    'state_machine': {'loc': 1182, 'layer': 'orchestration',  'pos': (0.5, 0.15)},
}

# Dependencies (from -> to means "from imports to")
dependencies = [
    ('state_machine', 'config'),
    ('state_machine', 'states'),
    ('state_machine', 'utils'),
    ('state_machine', 'vision'),
    ('state_machine', 'planning'),
    ('vision', 'config'),
    ('planning', 'config'),
    ('utils', 'config'),
    ('planning', 'utils'),
]

# Layer colors
layer_colors = {
    'config':        '#f8f9fa',
    'independent':   '#ebf5fb',
    'orchestration': '#fef9e7',
}

# LOC -> color intensity (darker = more code)
def loc_to_color(loc):
    """Map LOC to a color on a blue-orange gradient."""
    max_loc = 1200
    t = min(loc / max_loc, 1.0)
    # Blue (small) -> Orange (large)
    r = int(52 + t * (230 - 52))
    g = int(152 + t * (126 - 152))
    b = int(219 + t * (34 - 219))
    return f'#{r:02x}{g:02x}{b:02x}'

fig, ax = plt.subplots(figsize=(7.0, 5.5))
ax.set_xlim(-0.05, 1.05)
ax.set_ylim(-0.02, 1.02)
ax.set_aspect('equal')
ax.axis('off')

# Draw layer backgrounds
layer_rects = {
    'config':        (0.05, 0.72, 0.90, 0.28),
    'independent':   (0.05, 0.32, 0.90, 0.28),
    'orchestration': (0.05, 0.02, 0.90, 0.22),
}
layer_labels = {
    'config':        'Configuration Layer',
    'independent':   'Independent Modules',
    'orchestration': 'Orchestration Layer',
}

for layer, (lx, ly, lw, lh) in layer_rects.items():
    rect = mpatches.FancyBboxPatch((lx, ly), lw, lh, boxstyle='round,pad=0.02',
                                    facecolor=layer_colors[layer], edgecolor='#dee2e6',
                                    linewidth=1.0, alpha=0.7, zorder=0)
    ax.add_patch(rect)
    ax.text(lx + 0.02, ly + lh - 0.03, layer_labels[layer],
            fontsize=8, fontstyle='italic', color='#7f8c8d', va='top')

# Draw dependency arrows first (behind nodes)
for src, dst in dependencies:
    x1, y1 = modules[src]['pos']
    x2, y2 = modules[dst]['pos']
    # Shorten arrow to not overlap with box
    dx = x2 - x1
    dy = y2 - y1
    dist = np.sqrt(dx**2 + dy**2)
    # Shorten by box radius
    shrink = 0.06
    ratio_start = shrink / dist
    ratio_end = shrink / dist
    ax.annotate('', xy=(x2 - dx*ratio_end, y2 - dy*ratio_end),
                xytext=(x1 + dx*ratio_start, y1 + dy*ratio_start),
                arrowprops=dict(arrowstyle='->', color='#adb5bd', lw=1.2,
                               connectionstyle='arc3,rad=0.05'),
                zorder=1)

# Draw module boxes
for name, info in modules.items():
    x, y = info['pos']
    loc = info['loc']
    color = loc_to_color(loc)

    # Box size proportional to LOC (subtle)
    w = 0.12 + (loc / 1200) * 0.06
    h = 0.07 + (loc / 1200) * 0.02

    box = mpatches.FancyBboxPatch((x - w/2, y - h/2), w, h,
                                   boxstyle='round,pad=0.01',
                                   facecolor=color, edgecolor='#2c3e50',
                                   linewidth=1.5, zorder=3)
    ax.add_patch(box)

    # Module name
    display_name = name.replace('_', '\n')
    fontsize = 9 if len(name) <= 8 else 7.5
    text_color = 'white' if loc > 400 else '#2c3e50'
    ax.text(x, y + 0.008, display_name, ha='center', va='center',
            fontsize=fontsize, fontweight='bold', color=text_color, zorder=4)

    # LOC label below box
    ax.text(x, y - h/2 - 0.025, f'{loc} LOC', ha='center', va='top',
            fontsize=7, color='#7f8c8d', zorder=4)

# Colorbar legend
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.cm as cm

# Create a small colorbar
cax = fig.add_axes([0.78, 0.12, 0.03, 0.2])
gradient = np.linspace(0, 1, 256).reshape(-1, 1)
colors_list = [loc_to_color(int(t * 1200)) for t in np.linspace(0, 1, 256)]
from matplotlib.colors import ListedColormap
cmap = ListedColormap(colors_list)
cax.imshow(gradient, aspect='auto', cmap=cmap, origin='lower')
cax.set_xticks([])
cax.set_yticks([0, 128, 255])
cax.set_yticklabels(['0', '600', '1200'], fontsize=7)
cax.set_ylabel('Lines of code', fontsize=8, labelpad=2)

# Arrow meaning
ax.text(0.95, 0.01, 'Arrow: imports from', fontsize=7, ha='right', va='bottom',
        color='#adb5bd', fontstyle='italic')

plt.savefig('module_dependencies.pdf')
plt.savefig('module_dependencies.png')
print('Saved module_dependencies.pdf + .png')
