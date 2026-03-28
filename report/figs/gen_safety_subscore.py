"""Generate safety_subscore.pdf — Spider chart of safety sub-components."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

OUT = Path(__file__).parent

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

# ── Data ──
labels = [
    'NFZ margin\nadequacy',
    'Waypoint\nfiltering',
    'Speed scalar\nfield',
    'Repulsive\nvector field',
    'Hard\nboundary',
    'RC kill\nswitch',
]
values = [1.0, 1.0, 0.9, 0.85, 1.0, 1.0]
overall = 0.96

N = len(labels)
angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
# Close the polygon
values_closed = values + [values[0]]
angles_closed = angles + [angles[0]]

fig, ax = plt.subplots(figsize=(5.5, 5.5), subplot_kw=dict(polar=True))

# Start from top (90 degrees)
ax.set_theta_offset(np.pi / 2)
ax.set_theta_direction(-1)

# Draw gridlines at 0.2 increments
ax.set_ylim(0, 1.18)
ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8', '1.0'], fontsize=7, color='#666666')
ax.set_rlabel_position(30)

# Set axis labels
ax.set_xticks(angles)
ax.set_xticklabels(labels, fontsize=9)

# Fill color
fill_color = '#2E86C1'
ax.plot(angles_closed, values_closed, 'o-', linewidth=2, color=fill_color, markersize=6)
ax.fill(angles_closed, values_closed, alpha=0.20, color=fill_color)

# Annotate each vertex with its value
for angle, val in zip(angles, values):
    ax.text(angle, val + 0.12, f'{val:.2f}', ha='center', va='center',
            fontsize=9, fontweight='bold', color='#1A5276')

# Center score
ax.text(0, 0, f'{overall:.2f}', ha='center', va='center',
        fontsize=22, fontweight='bold', color=fill_color,
        transform=ax.transData)

# Grid styling
ax.grid(color='#CCCCCC', linewidth=0.5)
ax.spines['polar'].set_color('#CCCCCC')

ax.set_title('Safety Score Decomposition', fontsize=13, fontweight='bold',
             pad=20, color='#1B2631')

for ext in ('pdf', 'png'):
    fig.savefig(OUT / f'safety_subscore.{ext}')
plt.close(fig)
print(f'Saved safety_subscore.pdf/.png to {OUT}')
