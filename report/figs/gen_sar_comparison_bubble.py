#!/usr/bin/env python3
"""Generate SAR system comparison bubble chart."""

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

# --- Data from evaluation.tex Tab. sar-comparison ---
# System, Platform, FPS, mAP50, GPS_acc (CEP50 m, lower=better), Cost (GBP est.)
systems = [
    ('This project',       4.8,  0.995, 2.3,  565),
    ('AUSPEX\n(2025)',     30.0, 0.89,  5.0,  3500),   # Jetson Orin setup ~£3500
    ('Sambolek\n(2021)',   22.0, 0.81,  None, 2000),    # Jetson TX2 setup ~£2000
    ('Drones+YOLO\n(2025)', 12.0, 0.91, None, 1200),   # Jetson Nano setup ~£1200
    ('SearchWing\n(2024)',  5.0, 0.78,  10.0, 800),     # Companion PC ~£800
]

fig, ax = plt.subplots(figsize=(6.5, 4.5))

# Bubble size: inversely proportional to cost (cheaper = bigger bubble = better)
# Scale so they're visible
max_cost = max(s[4] for s in systems)
for name, fps, mAP, gps, cost in systems:
    # Bubble area proportional to cost (bigger cost = bigger bubble, but annotated)
    size = (cost / 100) * 8  # scale factor for visibility
    size = max(size, 60)

    if name.startswith('This'):
        color = '#2ecc71'
        edge = '#27ae60'
        zorder = 5
        alpha = 0.85
    else:
        color = '#3498db'
        edge = '#2980b9'
        zorder = 3
        alpha = 0.6

    ax.scatter(fps, mAP, s=size, c=color, edgecolors=edge, linewidth=1.5,
               alpha=alpha, zorder=zorder)

    # Label with name and cost
    offset_x = 0.8
    offset_y = 0.008
    ha = 'left'

    # Custom positioning to avoid overlaps
    if name.startswith('This'):
        offset_x = 1.5
        offset_y = 0.01
        ha = 'left'
    elif 'AUSPEX' in name:
        offset_x = -1.5
        offset_y = -0.02
        ha = 'right'
    elif 'Sambolek' in name:
        offset_x = 1.0
        offset_y = 0.005
    elif 'Drones' in name:
        offset_x = 1.0
        offset_y = -0.015

    ax.annotate(f'{name}\n\u00a3{cost:,}',
                xy=(fps, mAP),
                xytext=(fps + offset_x, mAP + offset_y),
                fontsize=8, ha=ha, va='center',
                arrowprops=dict(arrowstyle='-', color='#7f8c8d', lw=0.6),
                bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor='#bdc3c7', alpha=0.8))

# Highlight our system's quadrant
ax.axhline(y=0.90, color='#e74c3c', linestyle=':', alpha=0.4, zorder=1)
ax.axvline(x=10, color='#e74c3c', linestyle=':', alpha=0.4, zorder=1)

# Quadrant label
ax.text(2.0, 0.965, 'Low-cost,\nhigh-accuracy', fontsize=8, fontstyle='italic',
        color='#27ae60', ha='center', alpha=0.7,
        bbox=dict(boxstyle='round,pad=0.2', facecolor='#eafaf1', edgecolor='none', alpha=0.5))

ax.text(25, 0.76, 'High-cost,\nhigh-speed', fontsize=8, fontstyle='italic',
        color='#2980b9', ha='center', alpha=0.7,
        bbox=dict(boxstyle='round,pad=0.2', facecolor='#ebf5fb', edgecolor='none', alpha=0.5))

ax.set_xlabel('Inference speed (FPS)', fontsize=11)
ax.set_ylabel('Detection accuracy (mAP$_{50}$)', fontsize=11)
ax.set_xlim(0, 35)
ax.set_ylim(0.72, 1.02)
ax.grid(alpha=0.25, zorder=0)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()
plt.savefig('sar_comparison_bubble.pdf')
plt.savefig('sar_comparison_bubble.png')
print('Saved sar_comparison_bubble.pdf + .png')
