"""Generate detection_subscore.pdf — Spider chart of detection sub-components."""
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
    'Model quality\n(mAP50)',
    'Target pixel\nsize',
    'Per-frame\nconfidence',
    'Frames on\ntarget',
    'Cumulative\n$P_{detect}$',
]
values = [0.995, 0.85, 0.94, 0.93, 0.99]
overall = 0.93

N = len(labels)
angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
values_closed = values + [values[0]]
angles_closed = angles + [angles[0]]

fig, ax = plt.subplots(figsize=(5.5, 5.5), subplot_kw=dict(polar=True))

# Start from top (90 degrees)
ax.set_theta_offset(np.pi / 2)
ax.set_theta_direction(-1)

ax.set_ylim(0, 1.18)
ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8', '1.0'], fontsize=7, color='#666666')
ax.set_rlabel_position(30)

ax.set_xticks(angles)
ax.set_xticklabels(labels, fontsize=9)

fill_color = '#27AE60'
ax.plot(angles_closed, values_closed, 'o-', linewidth=2, color=fill_color, markersize=6)
ax.fill(angles_closed, values_closed, alpha=0.20, color=fill_color)

# Value annotations with alignment that avoids label overlap
for i, (angle, val) in enumerate(zip(angles, values)):
    fmt = f'{val:.3f}' if val > 0.99 else f'{val:.2f}'
    # For left-side labels, shift value right; for right-side, shift left
    ha = 'center'
    offset_r = 0.13
    if i == 4:  # Cumulative P_detect (left side) - push value inward
        ha = 'right'
        offset_r = 0.08
    ax.text(angle, val + offset_r, fmt,
            ha=ha, va='center', fontsize=9, fontweight='bold', color='#1E8449')

ax.text(0, 0, f'{overall:.2f}', ha='center', va='center',
        fontsize=22, fontweight='bold', color=fill_color,
        transform=ax.transData)

ax.grid(color='#CCCCCC', linewidth=0.5)
ax.spines['polar'].set_color('#CCCCCC')

ax.set_title('Detection Score Decomposition', fontsize=13, fontweight='bold',
             pad=20, color='#1B2631')

for ext in ('pdf', 'png'):
    fig.savefig(OUT / f'detection_subscore.{ext}')
plt.close(fig)
print(f'Saved detection_subscore.pdf/.png to {OUT}')
