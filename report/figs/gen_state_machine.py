"""Chart 6: Simplified State Machine Diagram for SAR drone mission."""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

fig, ax = plt.subplots(1, 1, figsize=(10, 7))
ax.set_xlim(-0.5, 10.5)
ax.set_ylim(-1.5, 8.5)
ax.set_aspect('equal')
ax.axis('off')

# Colors
GREEN = '#2ecc71'
GREEN_DARK = '#27ae60'
BLUE = '#3498db'
BLUE_DARK = '#2980b9'
ORANGE = '#e67e22'
ORANGE_DARK = '#d35400'
RED = '#e74c3c'
RED_DARK = '#c0392b'
GREY = '#95a5a6'
WHITE = '#ffffff'
TEXT_DARK = '#2c3e50'

def draw_box(ax, cx, cy, w, h, text, color, text_color='white', fontsize=9):
    box = FancyBboxPatch((cx - w/2, cy - h/2), w, h,
                         boxstyle="round,pad=0.1", linewidth=1.2,
                         edgecolor=color, facecolor=color, zorder=3)
    ax.add_patch(box)
    ax.text(cx, cy, text, ha='center', va='center', fontsize=fontsize,
            fontweight='bold', color=text_color, zorder=4)

def draw_arrow(ax, x1, y1, x2, y2, label='', color='#555555', style='->', lw=1.3, fontsize=7.5, label_offset=(0, 0.18)):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle=style, color=color, lw=lw,
                                connectionstyle='arc3,rad=0'),
                zorder=2)
    if label:
        mx = (x1 + x2) / 2 + label_offset[0]
        my = (y1 + y2) / 2 + label_offset[1]
        ax.text(mx, my, label, ha='center', va='center', fontsize=fontsize,
                color=color, fontstyle='italic', zorder=5,
                bbox=dict(boxstyle='round,pad=0.1', facecolor='white', edgecolor='none', alpha=0.85))

# Main flow (vertical, left side) — positions
bw, bh = 1.8, 0.55
positions = {
    'INIT':       (2.5, 7.5),
    'TAKEOFF':    (2.5, 6.3),
    'SEARCH':     (2.5, 5.1),
    'CENTERING':  (2.5, 3.9),
    'VERIFY':     (2.5, 2.7),
    'APPROACH':   (2.5, 1.5),
    'LANDING':    (2.5, 0.3),
    'DONE':       (2.5, -0.9),
    'MANUAL':     (7.0, 5.1),
}
colors = {
    'INIT': GREEN, 'TAKEOFF': BLUE, 'SEARCH': BLUE,
    'CENTERING': BLUE, 'VERIFY': ORANGE, 'APPROACH': BLUE,
    'LANDING': BLUE, 'DONE': GREEN, 'MANUAL': RED,
}

# Draw boxes
for name, (cx, cy) in positions.items():
    draw_box(ax, cx, cy, bw, bh, name, colors[name])

# Main flow arrows (down)
main_flow = [('INIT', 'TAKEOFF'), ('TAKEOFF', 'SEARCH'), ('SEARCH', 'CENTERING'),
             ('CENTERING', 'VERIFY'), ('APPROACH', 'LANDING'), ('LANDING', 'DONE')]
for a, b in main_flow:
    x1, y1 = positions[a]
    x2, y2 = positions[b]
    draw_arrow(ax, x1, y1 - bh/2, x2, y2 + bh/2)

# VERIFY -> APPROACH (Y)
vx, vy = positions['VERIFY']
ax_, ay = positions['APPROACH']
draw_arrow(ax, vx, vy - bh/2, ax_, ay + bh/2, label='Confirmed [Y]', color=GREEN_DARK, label_offset=(0.05, 0.15))

# VERIFY -> SEARCH (N) — curved arrow on the left
draw_arrow(ax, vx - bw/2, vy, 0.3, vy, color=ORANGE_DARK, lw=1.1)
ax.annotate('', xy=(0.3, positions['SEARCH'][1]),
            xytext=(0.3, vy),
            arrowprops=dict(arrowstyle='->', color=ORANGE_DARK, lw=1.1), zorder=2)
ax.annotate('', xy=(positions['SEARCH'][0] - bw/2, positions['SEARCH'][1]),
            xytext=(0.3, positions['SEARCH'][1]),
            arrowprops=dict(arrowstyle='->', color=ORANGE_DARK, lw=1.1), zorder=2)
ax.text(-0.05, (vy + positions['SEARCH'][1])/2, 'Rejected\n[N]', ha='center', va='center',
        fontsize=7.5, color=ORANGE_DARK, fontstyle='italic',
        bbox=dict(boxstyle='round,pad=0.1', facecolor='white', edgecolor='none', alpha=0.85), zorder=5)

# SEARCH -> CENTERING label
draw_arrow(ax, positions['SEARCH'][0], positions['SEARCH'][1] - bh/2,
           positions['CENTERING'][0], positions['CENTERING'][1] + bh/2,
           label='Detection', color=BLUE_DARK, label_offset=(0.05, 0.15))

# Any state -> MANUAL (dashed from main column)
ax.annotate('', xy=(positions['MANUAL'][0] - bw/2, positions['MANUAL'][1]),
            xytext=(positions['SEARCH'][0] + bw/2 + 0.15, positions['SEARCH'][1]),
            arrowprops=dict(arrowstyle='->', color=RED_DARK, lw=1.1,
                            linestyle='dashed', connectionstyle='arc3,rad=-0.15'), zorder=2)
ax.text(4.85, 5.7, 'M key\n(override)', ha='center', va='center', fontsize=7, color=RED_DARK,
        fontstyle='italic', bbox=dict(boxstyle='round,pad=0.1', facecolor='white', edgecolor='none', alpha=0.85), zorder=5)

# MANUAL -> return (dashed back)
ax.annotate('', xy=(positions['SEARCH'][0] + bw/2 + 0.15, positions['SEARCH'][1] - 0.3),
            xytext=(positions['MANUAL'][0] - bw/2, positions['MANUAL'][1] - 0.2),
            arrowprops=dict(arrowstyle='->', color=RED_DARK, lw=1.1,
                            linestyle='dashed', connectionstyle='arc3,rad=-0.15'), zorder=2)
ax.text(4.85, 4.45, 'M key\n(resume)', ha='center', va='center', fontsize=7, color=RED_DARK,
        fontstyle='italic', bbox=dict(boxstyle='round,pad=0.1', facecolor='white', edgecolor='none', alpha=0.85), zorder=5)

# RTL annotation (firmware behaviour, not a state)
ax.text(7.0, 2.7, 'Link loss / RC kill\n  RTL (firmware)', ha='center',
        va='center', fontsize=7.5, color=RED, fontstyle='italic',
        bbox=dict(boxstyle='round,pad=0.15', facecolor='#fadbd8',
                  edgecolor=RED, alpha=0.8, linewidth=0.8), zorder=5)
ax.annotate('', xy=(5.95, 2.7),
            xytext=(positions['VERIFY'][0] + bw/2 + 0.15, positions['VERIFY'][1]),
            arrowprops=dict(arrowstyle='->', color=RED, lw=1.1,
                            linestyle='dotted', connectionstyle='arc3,rad=0.15'), zorder=2)

# Legend
legend_items = [
    mpatches.Patch(color=GREEN, label='Start / End'),
    mpatches.Patch(color=BLUE, label='Autonomous'),
    mpatches.Patch(color=ORANGE, label='Operator decision'),
    mpatches.Patch(color=RED, label='Safety override'),
]
ax.legend(handles=legend_items, loc='upper right', fontsize=8, frameon=True,
          fancybox=True, framealpha=0.9, edgecolor='#cccccc')

plt.tight_layout()
plt.savefig('c:/Users/Bristol/Desktop/AI for Robotics/v3/report/figs/state_machine.pdf',
            bbox_inches='tight', dpi=300)
plt.savefig('c:/Users/Bristol/Desktop/AI for Robotics/v3/report/figs/state_machine.png',
            bbox_inches='tight', dpi=300)
print("OK: state_machine.pdf")
