#!/usr/bin/env python3
"""Generate dataset composition donut charts: v1 vs v2."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
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

# --- Data from 12_model_training.tex ---
# v1: 200 synthetic only, 640x640, mAP50 ~0.95
# v2: 300 synthetic + 16 real + 50 negative = 366, 1088x1088, mAP50 = 0.995

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.0, 3.5))

colors = ['#3498db', '#e74c3c', '#95a5a6']  # synthetic, real, negative
labels_full = ['Synthetic', 'Real', 'Negative']

# --- v1 donut ---
v1_sizes = [200]
v1_labels = ['Synthetic\n200']
v1_colors = ['#3498db']

wedges1, texts1 = ax1.pie(
    v1_sizes, labels=None, colors=v1_colors,
    startangle=90, wedgeprops=dict(width=0.4, edgecolor='white', linewidth=2),
)

# Center text
ax1.text(0, 0.08, '200', fontsize=18, fontweight='bold', ha='center', va='center', color='#2c3e50')
ax1.text(0, -0.15, 'images', fontsize=9, ha='center', va='center', color='#7f8c8d')

# Label outside
ax1.text(0, -0.75, 'Synthetic only', fontsize=9, ha='center', color='#3498db', fontstyle='italic')

ax1.set_title('v1 Dataset (640$\\times$640)', fontsize=11, pad=12)

# mAP below
ax1.text(0, -1.1, 'mAP$_{50}$ $\\approx$ 0.95', fontsize=12, fontweight='bold',
         ha='center', va='center', color='#7f8c8d',
         bbox=dict(boxstyle='round,pad=0.3', facecolor='#f8f9fa', edgecolor='#dee2e6'))

# --- v2 donut ---
v2_sizes = [300, 16, 50]
v2_pcts = [s/366*100 for s in v2_sizes]

wedges2, texts2 = ax2.pie(
    v2_sizes, labels=None, colors=colors,
    startangle=90, wedgeprops=dict(width=0.4, edgecolor='white', linewidth=2),
    autopct=None,
)

# Add percentage labels on wedges
angles = [(w.theta1 + w.theta2) / 2 for w in wedges2]
for i, (angle, size, pct) in enumerate(zip(angles, v2_sizes, v2_pcts)):
    x = 0.8 * np.cos(np.radians(angle))
    y = 0.8 * np.sin(np.radians(angle))
    label = f'{labels_full[i]}\n{size} ({pct:.0f}%)'
    if i == 1:  # real is small wedge
        label = f'{labels_full[i]}\n{size} ({pct:.1f}%)'
    ax2.text(x, y, label, ha='center', va='center', fontsize=7.5, fontweight='bold', color='white')

# Center text
ax2.text(0, 0.08, '366', fontsize=18, fontweight='bold', ha='center', va='center', color='#2c3e50')
ax2.text(0, -0.15, 'images', fontsize=9, ha='center', va='center', color='#7f8c8d')

ax2.set_title('v2 Dataset (1088$\\times$1088)', fontsize=11, pad=12)

# mAP below
ax2.text(0, -1.1, 'mAP$_{50}$ = 0.995', fontsize=12, fontweight='bold',
         ha='center', va='center', color='#27ae60',
         bbox=dict(boxstyle='round,pad=0.3', facecolor='#eafaf1', edgecolor='#27ae60'))

# Arrow between donuts
fig.text(0.50, 0.55, '\u2192', fontsize=28, ha='center', va='center', color='#2c3e50', fontweight='bold')
fig.text(0.50, 0.44, '+real data\n+negatives\n+higher res', fontsize=7.5, ha='center', va='center',
         color='#7f8c8d', fontstyle='italic')

plt.tight_layout(w_pad=3.0)
plt.savefig('dataset_composition.pdf')
plt.savefig('dataset_composition.png')
print('Saved dataset_composition.pdf + .png')
