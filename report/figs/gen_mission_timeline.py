"""Chart 9: Mission Timeline / Sequence with altitude profile."""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 4.5), height_ratios=[1.2, 1])
fig.subplots_adjust(hspace=0.08)

# Colors
COLORS = {
    'Takeoff':    '#2ecc71',
    'Transit':    '#3498db',
    'Search':     '#2980b9',
    'Detection':  '#e74c3c',
    'Centering':  '#9b59b6',
    'Verify':     '#e67e22',
    'Approach':   '#1abc9c',
    'Landing':    '#27ae60',
}
TEXT_DARK = '#2c3e50'
GRID_COL = '#ecf0f1'

# Timeline phases: (name, start_s, duration_s)
phases = [
    ('Takeoff',    0,   10),
    ('Transit',    10,  30),
    ('Search',     40,  120),
    ('Detection',  160, 5),
    ('Centering',  165, 15),
    ('Verify',     180, 30),
    ('Approach',   210, 20),
    ('Landing',    230, 10),
]

total_time = 240

# === TOP: Timeline bars ===
ax1.set_xlim(0, total_time)
ax1.set_ylim(-0.3, 1.5)
ax1.axis('off')

bar_y = 0.3
bar_h = 0.6

for name, start, dur in phases:
    rect = FancyBboxPatch((start, bar_y), dur, bar_h,
                          boxstyle="round,pad=0.02", linewidth=0.8,
                          edgecolor='white', facecolor=COLORS[name], zorder=3)
    ax1.add_patch(rect)
    # Label above
    cx = start + dur / 2
    fs = 7.5 if dur >= 15 else 6.5
    if dur >= 10:
        ax1.text(cx, bar_y + bar_h + 0.08, name, ha='center', va='bottom',
                fontsize=fs, fontweight='bold', color=TEXT_DARK, zorder=4)
    else:
        # Very short phases — label with leader line
        ax1.text(cx, bar_y + bar_h + 0.35, name, ha='center', va='bottom',
                fontsize=6.5, fontweight='bold', color=TEXT_DARK, zorder=4)
        ax1.plot([cx, cx], [bar_y + bar_h, bar_y + bar_h + 0.33], '-',
                color='#bbb', lw=0.7, zorder=2)
    # Time label inside bar
    if dur >= 15:
        time_str = f'{dur}s'
        ax1.text(cx, bar_y + bar_h/2, time_str, ha='center', va='center',
                fontsize=7, color='white', fontstyle='italic', zorder=4)

# Time ticks along bottom
for t in range(0, total_time + 1, 30):
    ax1.text(t, bar_y - 0.12, f'{t//60}:{t%60:02d}', ha='center', va='top',
            fontsize=7, color='#7f8c8d')
    ax1.plot([t, t], [bar_y - 0.02, bar_y], '-', color='#bbb', lw=0.5)

ax1.text(total_time / 2, 1.4, 'Typical Mission Timeline', ha='center', va='center',
        fontsize=12, fontweight='bold', color=TEXT_DARK)

# === BOTTOM: Altitude profile ===
ax2.set_xlim(0, total_time)
ax2.set_ylim(0, 42)
ax2.set_ylabel('Altitude (m)', fontsize=9, color=TEXT_DARK)
ax2.set_xlabel('Mission Time', fontsize=9, color=TEXT_DARK)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.spines['left'].set_color('#bbb')
ax2.spines['bottom'].set_color('#bbb')
ax2.tick_params(colors='#7f8c8d', labelsize=7)

# X ticks as mm:ss
xticks = list(range(0, total_time + 1, 30))
ax2.set_xticks(xticks)
ax2.set_xticklabels([f'{t//60}:{t%60:02d}' for t in xticks])

# Altitude profile data points
# Takeoff: 0->35m over 10s
# Transit: 35m
# Search: 35m
# Detection: 35m
# Centering: 35->15m over 15s
# Verify: 15m
# Approach: 15->5m over 20s
# Landing: 5->0m over 10s
t_pts = [0, 10, 40, 160, 165, 180, 210, 230, 240]
a_pts = [0, 35, 35, 35, 35, 15, 15, 5, 0]

# Smooth interpolation
t_smooth = np.linspace(0, 240, 500)
a_smooth = np.interp(t_smooth, t_pts, a_pts)

# Color the area under the curve by phase
for name, start, dur in phases:
    mask = (t_smooth >= start) & (t_smooth <= start + dur)
    ax2.fill_between(t_smooth[mask], 0, a_smooth[mask], alpha=0.25, color=COLORS[name])

ax2.plot(t_smooth, a_smooth, '-', color=TEXT_DARK, lw=2, zorder=5)

# Altitude annotations
ax2.axhline(y=35, color='#bbb', linestyle=':', lw=0.6, zorder=1)
ax2.text(total_time - 2, 36, '35 m (search)', ha='right', va='bottom', fontsize=7, color='#95a5a6')
ax2.axhline(y=15, color='#bbb', linestyle=':', lw=0.6, zorder=1)
ax2.text(total_time - 2, 16, '15 m (verify)', ha='right', va='bottom', fontsize=7, color='#95a5a6')

plt.savefig('c:/Users/Bristol/Desktop/AI for Robotics/v3/report/figs/mission_timeline.pdf',
            bbox_inches='tight', dpi=300)
plt.savefig('c:/Users/Bristol/Desktop/AI for Robotics/v3/report/figs/mission_timeline.png',
            bbox_inches='tight', dpi=300)
print("OK: mission_timeline.pdf")
