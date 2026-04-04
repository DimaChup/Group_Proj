#!/usr/bin/env python3
"""Generate cost comparison bar chart: our system vs commercial platforms."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

# --- Style ---
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

# --- Data (from 03_hardware_platform.tex) ---
# Our system BOM breakdown
components = [
    ('Cube Orange+ FC', 180),
    ('Here3 GPS', 70),
    ('Raspberry Pi 5', 60),
    ('IMX296 Camera', 45),
    ('Motors + ESCs', 70),   # 40 + 30
    ('RC Tx/Rx', 40),
    ('Battery', 35),
    ('Frame (S500)', 30),
    ('Telemetry + misc.', 35),  # 20 + 15
]

comp_names = [c[0] for c in components]
comp_costs = [c[1] for c in components]
total_ours = sum(comp_costs)  # 565

# Commercial systems (from tex)
systems = ['This project\n(Pi 5 + RGB)', 'DJI Matrice 30T\n(thermal + RGB)', 'DJI Matrice 350 RTK\n(thermal payload)']
costs = [total_ours, 5800, 12000]
colors = ['#2ecc71', '#95a5a6', '#7f8c8d']
edge_colors = ['#27ae60', '#7f8c8d', '#5d6d7e']

fig, ax = plt.subplots(figsize=(6.5, 3.0))

bars = ax.barh(range(len(systems)), costs, color=colors, edgecolor=edge_colors,
               linewidth=1.2, height=0.55, zorder=3)

# Add cost labels
for i, (bar, cost) in enumerate(zip(bars, costs)):
    w = bar.get_width()
    if i == 0:
        # Inside the bar for our system
        ax.text(w - 30, bar.get_y() + bar.get_height()/2,
                f'\u00a3{cost:,}', ha='right', va='center',
                fontweight='bold', fontsize=11, color='white')
    else:
        ax.text(w + 80, bar.get_y() + bar.get_height()/2,
                f'\u00a3{cost:,}', ha='left', va='center',
                fontweight='bold', fontsize=11, color=edge_colors[i])

# Cost ratio annotations
for i in [1, 2]:
    ratio = costs[i] / costs[0]
    ax.annotate(f'{ratio:.0f}x', xy=(costs[0], i), xytext=(costs[0] + 400, i),
                fontsize=9, color='#e74c3c', fontweight='bold',
                arrowprops=dict(arrowstyle='->', color='#e74c3c', lw=1.2),
                va='center')

ax.set_yticks(range(len(systems)))
ax.set_yticklabels(systems, fontsize=9.5)
ax.set_xlabel('Total system cost (\u00a3 GBP)', fontsize=11)
ax.set_xlim(0, 14500)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'\u00a3{int(x):,}'))
ax.invert_yaxis()
ax.grid(axis='x', alpha=0.3, zorder=0)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()
plt.savefig('cost_comparison.pdf')
plt.savefig('cost_comparison.png')
print('Saved cost_comparison.pdf + .png')
