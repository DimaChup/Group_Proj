"""Generate decision flow figure for optimization strategy."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

# ── Colours ──
GREEN  = '#2E7D32'   # safety
GREEN_L = '#E8F5E9'
BLUE   = '#1565C0'   # detection
BLUE_L = '#E3F2FD'
GREY   = '#616161'   # secondary
GREY_L = '#F5F5F5'
DARK   = '#212121'
WHITE  = '#FFFFFF'
RESULT_BG = '#FFF8E1'
RESULT_BD = '#F9A825'

fig, ax = plt.subplots(figsize=(8.5, 11.5))
ax.set_xlim(0, 10)
ax.set_ylim(0, 14)
ax.axis('off')
fig.patch.set_facecolor(WHITE)

def rounded_box(x, y, w, h, fc, ec, lw=1.5, zorder=2):
    box = FancyBboxPatch((x, y), w, h,
                         boxstyle="round,pad=0.15",
                         facecolor=fc, edgecolor=ec, linewidth=lw,
                         zorder=zorder, transform=ax.transData)
    ax.add_patch(box)
    return box

def arrow_down(x, y_top, y_bot, color=DARK):
    ax.annotate('', xy=(x, y_bot), xytext=(x, y_top),
                arrowprops=dict(arrowstyle='->', color=color, lw=1.8),
                zorder=3)

# ═══════════════════════════════════════════
# TITLE
# ═══════════════════════════════════════════
ax.text(5, 13.4, 'Mission Objective: Find the Casualty Fastest',
        ha='center', va='center', fontsize=14, fontweight='bold',
        color=DARK, zorder=5)
# thin line under title
ax.plot([1.2, 8.8], [13.1, 13.1], color=GREY, lw=0.8, zorder=3)

# ═══════════════════════════════════════════
# ROW 1 — Priority hierarchy
# ═══════════════════════════════════════════
row1_y = 12.1
bw, bh = 3.2, 0.7

# Safety
rounded_box(0.8, row1_y, bw, bh, GREEN_L, GREEN, lw=2)
ax.text(0.8 + bw/2, row1_y + bh/2, 'SAFETY', ha='center', va='center',
        fontsize=11, fontweight='bold', color=GREEN)
ax.text(0.8 + bw/2, row1_y + bh/2 - 0.22, 'priority 1', ha='center', va='center',
        fontsize=8, color=GREEN, style='italic')

# Detection
rounded_box(6.0, row1_y, bw, bh, BLUE_L, BLUE, lw=2)
ax.text(6.0 + bw/2, row1_y + bh/2, 'DETECTION', ha='center', va='center',
        fontsize=11, fontweight='bold', color=BLUE)
ax.text(6.0 + bw/2, row1_y + bh/2 - 0.22, 'priority 2', ha='center', va='center',
        fontsize=8, color=BLUE, style='italic')

# Secondary row
sec_y = 11.35
sbw, sbh = 3.2, 0.5
rounded_box(0.8, sec_y, sbw, sbh, GREY_L, GREY, lw=1)
ax.text(0.8 + sbw/2, sec_y + sbh/2, 'TIME  (secondary)', ha='center', va='center',
        fontsize=9, color=GREY)
rounded_box(6.0, sec_y, sbw, sbh, GREY_L, GREY, lw=1)
ax.text(6.0 + sbw/2, sec_y + sbh/2, 'ENERGY  (secondary)', ha='center', va='center',
        fontsize=9, color=GREY)

# ═══════════════════════════════════════════
# ROW 2 — Decision chain
# ═══════════════════════════════════════════
chain_x = 1.0
chain_w = 8.0
box_h = 1.15
gap = 0.45   # space between boxes (includes arrow)

decisions = [
    ('Max detection altitude',   '63 m  (20 px minimum target)',   BLUE, BLUE_L),
    ('Apply 15% safety margin',  '35 m  operating altitude',       GREEN, GREEN_L),
    ('Max speed for 10+ frames', '8 m/s  (altitude-dependent)',    BLUE, BLUE_L),
    ('Energy-optimal scan angle','70°  (longest edge, 4 turns)',   GREY, GREY_L),
    ('NFZ margin (footprint + GPS)', '30 m buffer, 96% coverage', GREEN, GREEN_L),
]

top_y = 10.5
for i, (label, value, col, bg) in enumerate(decisions):
    y = top_y - i * (box_h + gap)
    rounded_box(chain_x, y, chain_w, box_h, bg, col, lw=1.8)

    # Step number circle
    circle = plt.Circle((chain_x + 0.45, y + box_h/2), 0.22,
                         fc=col, ec=col, zorder=4)
    ax.add_patch(circle)
    ax.text(chain_x + 0.45, y + box_h/2, str(i+1), ha='center', va='center',
            fontsize=10, fontweight='bold', color=WHITE, zorder=5)

    # Label
    ax.text(chain_x + 0.9, y + box_h/2 + 0.18, label,
            ha='left', va='center', fontsize=10, fontweight='bold', color=DARK, zorder=5)

    # Arrow + value
    ax.text(chain_x + 0.9, y + box_h/2 - 0.2, '→  ' + value,
            ha='left', va='center', fontsize=10, color=col, zorder=5,
            fontweight='semibold')

    # Arrow to next box
    if i < len(decisions) - 1:
        arrow_down(5, y, y - gap + 0.05, color=col)

# ═══════════════════════════════════════════
# ROW 3 — Result box
# ═══════════════════════════════════════════
res_y = top_y - len(decisions) * (box_h + gap) - 0.15
res_h = 1.1
arrow_down(5, res_y + res_h + gap + 0.1, res_y + res_h + 0.05, color=DARK)

rounded_box(chain_x, res_y, chain_w, res_h, RESULT_BG, RESULT_BD, lw=2.5)
ax.text(5, res_y + res_h/2 + 0.22, 'Selected Configuration',
        ha='center', va='center', fontsize=11, fontweight='bold', color=DARK, zorder=5)
ax.text(5, res_y + res_h/2 - 0.18,
        '35 m  ·  8 m/s  ·  70°  ·  20% overlap',
        ha='center', va='center', fontsize=10, color=DARK, zorder=5)
ax.text(5, res_y + res_h/2 - 0.52,
        '12.6 Wh   |   112 s   |   92% detection probability',
        ha='center', va='center', fontsize=9, color=GREY, zorder=5)

# ── Legend ──
leg_y = res_y - 0.6
for cx, col, lbl in [(2.0, GREEN, 'Safety'), (5.0, BLUE, 'Detection'), (7.8, GREY, 'Secondary')]:
    ax.plot(cx - 0.25, leg_y, 's', color=col, markersize=8)
    ax.text(cx + 0.0, leg_y, lbl, va='center', fontsize=8, color=col)

plt.tight_layout(pad=0.3)
fig.savefig(r'c:\Users\Bristol\Desktop\AI for Robotics\v3\report\figs\decision_flow.pdf',
            bbox_inches='tight', dpi=300)
fig.savefig(r'c:\Users\Bristol\Desktop\AI for Robotics\v3\report\figs\decision_flow.png',
            bbox_inches='tight', dpi=300)
print('Saved decision_flow.pdf and decision_flow.png')
