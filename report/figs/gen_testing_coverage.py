"""Testing Coverage Chart: requirements verified at each testing ladder level."""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path

# --- Styling ---
TEXT_DARK = '#2c3e50'

plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 11,
    'axes.labelcolor': TEXT_DARK,
    'text.color': TEXT_DARK,
    'axes.edgecolor': '#cccccc',
    'xtick.color': TEXT_DARK,
    'ytick.color': TEXT_DARK,
})

# --- Data ---
TOTAL = 12

levels = [
    'Unit\nTests',
    'Dry\nRun',
    'SITL\nSimulation',
    'Bench\nTesting',
    'Easter\nField',
    'Real\nFlight',
]

verified = [8, 9, 12, 10, 10, 0]  # 0 = pending for Real Flight
pending_flag = [False, False, False, False, False, True]

# Requirements verified at each level (for annotation)
reqs_at_level = [
    'R01-R07, R09',
    '+R01 geofence',
    'All R01-R12',
    'R05, R09\nhardware',
    'FOV, GPS\noutdoors',
    'Pending\n(demo day)',
]

# Colour gradient: blue -> green -> orange
colours = ['#3498db', '#2eaadb', '#27ae60', '#f39c12', '#e67e22', '#bdc3c7']

# --- Plot ---
fig, ax = plt.subplots(figsize=(9, 5))

x = np.arange(len(levels))
bar_width = 0.6

bars = ax.bar(x, verified, width=bar_width, color=colours, edgecolor='white',
              linewidth=1.2, zorder=3)

# Hatch the pending bar
bars[-1].set_hatch('///')
bars[-1].set_edgecolor('#95a5a6')

# 100% coverage line
ax.axhline(y=TOTAL, color='#c0392b', linestyle='--', linewidth=1.5, zorder=2,
           label='100% coverage (12 requirements)')

# Value labels on bars
for i, (bar, v) in enumerate(zip(bars, verified)):
    if pending_flag[i]:
        label = 'TBD'
        y_pos = 1
    else:
        label = f'{v}/{TOTAL}'
        y_pos = v + 0.3
    ax.text(bar.get_x() + bar.get_width() / 2, y_pos, label,
            ha='center', va='bottom', fontweight='bold', fontsize=11,
            color=TEXT_DARK)

# Percentage labels inside bars
for i, (bar, v) in enumerate(zip(bars, verified)):
    if not pending_flag[i] and v > 1:
        pct = v / TOTAL * 100
        ax.text(bar.get_x() + bar.get_width() / 2, v / 2, f'{pct:.0f}%',
                ha='center', va='center', fontsize=10, color='white',
                fontweight='bold')

# Axes
ax.set_xticks(x)
ax.set_xticklabels(levels, fontsize=10)
ax.set_ylabel('Requirements Verified', fontsize=12)
ax.set_ylim(0, 14.5)
ax.set_yticks(range(0, 14, 2))
ax.yaxis.grid(True, linestyle=':', alpha=0.4, zorder=0)
ax.set_axisbelow(True)

# Legend
legend_elements = [
    mpatches.Patch(facecolor='#bdc3c7', hatch='///', edgecolor='#95a5a6',
                   label='Pending (demo day)'),
    plt.Line2D([0], [0], color='#c0392b', linestyle='--', linewidth=1.5,
               label='100% coverage (12 req.)'),
]
ax.legend(handles=legend_elements, loc='upper left', framealpha=0.9, fontsize=9)

# Title
ax.set_title('Requirements Verification Across Testing Levels',
             fontsize=13, fontweight='bold', pad=12)

# Arrow showing progression
ax.annotate('', xy=(4.6, 13.5), xytext=(0.4, 13.5),
            arrowprops=dict(arrowstyle='->', color='#7f8c8d', lw=1.5))
ax.text(2.5, 14.0, 'Progressive testing ladder', ha='center', va='center',
        fontsize=9, color='#7f8c8d', fontstyle='italic')

plt.tight_layout()

# --- Save ---
out_dir = Path(__file__).parent
fig.savefig(out_dir / 'testing_coverage.pdf', bbox_inches='tight', dpi=300)
fig.savefig(out_dir / 'testing_coverage.png', bbox_inches='tight', dpi=300)
print(f"Saved testing_coverage.pdf and testing_coverage.png to {out_dir}")
plt.close()
