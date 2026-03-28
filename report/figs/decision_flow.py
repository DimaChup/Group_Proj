"""Generate decision flow figure for optimization strategy — 9-step version with Phase A/B."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
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
PHASE_A_COL = '#1565C0'
PHASE_B_COL = '#6A1B9A'

fig, ax = plt.subplots(figsize=(8.5, 13))
ax.set_xlim(0, 11)
ax.set_ylim(0, 16.5)
ax.axis('off')
fig.patch.set_facecolor(WHITE)

def rounded_box(x, y, w, h, fc, ec, lw=1.5, zorder=2):
    box = FancyBboxPatch((x, y), w, h,
                         boxstyle="round,pad=0.10",
                         facecolor=fc, edgecolor=ec, linewidth=lw,
                         zorder=zorder, transform=ax.transData)
    ax.add_patch(box)
    return box

def arrow_down(x, y_top, y_bot, color=DARK):
    ax.annotate('', xy=(x, y_bot), xytext=(x, y_top),
                arrowprops=dict(arrowstyle='->', color=color, lw=1.3),
                zorder=3)

# ═══════════════════════════════════════════════════════════════════════
# TITLE
# ═══════════════════════════════════════════════════════════════════════
ax.text(5.5, 16.1, 'SAR Drone: Search Parameter Decision Flow',
        ha='center', va='center', fontsize=14, fontweight='bold',
        color=DARK, zorder=5)
ax.plot([1.0, 10.0], [15.8, 15.8], color=GREY, lw=0.7, zorder=3)

# ═══════════════════════════════════════════════════════════════════════
# ROW 1 — Priority hierarchy
# ═══════════════════════════════════════════════════════════════════════
row1_y = 15.0
bw, bh = 3.4, 0.55

# Safety
rounded_box(1.0, row1_y, bw, bh, GREEN_L, GREEN, lw=2)
ax.text(1.0 + bw/2, row1_y + bh/2 + 0.02, 'SAFETY', ha='center', va='center',
        fontsize=10, fontweight='bold', color=GREEN)
ax.text(1.0 + bw/2, row1_y + bh/2 - 0.19, 'priority 1', ha='center', va='center',
        fontsize=7.5, color=GREEN, style='italic')

# Detection
rounded_box(6.6, row1_y, bw, bh, BLUE_L, BLUE, lw=2)
ax.text(6.6 + bw/2, row1_y + bh/2 + 0.02, 'DETECTION', ha='center', va='center',
        fontsize=10, fontweight='bold', color=BLUE)
ax.text(6.6 + bw/2, row1_y + bh/2 - 0.19, 'priority 2', ha='center', va='center',
        fontsize=7.5, color=BLUE, style='italic')

# Secondary row
sec_y = 14.35
sbw, sbh = 3.4, 0.38
rounded_box(1.0, sec_y, sbw, sbh, GREY_L, GREY, lw=1)
ax.text(1.0 + sbw/2, sec_y + sbh/2, 'TIME  (secondary)', ha='center', va='center',
        fontsize=8, color=GREY)
rounded_box(6.6, sec_y, sbw, sbh, GREY_L, GREY, lw=1)
ax.text(6.6 + sbw/2, sec_y + sbh/2, 'ENERGY  (secondary)', ha='center', va='center',
        fontsize=8, color=GREY)

# ═══════════════════════════════════════════════════════════════════════
# DECISION CHAIN — 9 steps in two phases
# ═══════════════════════════════════════════════════════════════════════
chain_x = 1.6
chain_w = 7.8
box_h = 0.82
gap = 0.22

# (label, value, colour, bg_colour)
decisions = [
    # Phase A: Measure (Steps 1-4)
    ('Train reliable vision model',        'mAP50 = 0.995 (retrained YOLOv8n)',    BLUE,  BLUE_L),
    ('Find max detection altitude',        '63 m ceiling  (20 px minimum target)', BLUE,  BLUE_L),
    ('Apply 15% safety margin',            '35 m operating alt  (36 px target height)', GREEN, GREEN_L),
    ('Max speed for 10+ frames',           '8 m/s  (14 frames, >99.97% detection)',    BLUE,  BLUE_L),
    # Phase B: Optimise (Steps 5-9)
    ('Choose search pattern type',         'Lawnmower  (coverage guarantee)',      GREY,  GREY_L),
    ('Fixed heading vs. yaw-to-face',      'Fixed heading  (3\u20135% energy saving)',  GREY,  GREY_L),
    ('Energy-optimal scan angle',          '70\u00b0  (longest edge, 5 U-turns)',   GREY,  GREY_L),
    ('NFZ safety margin',                  '30 m buffer  (1.5\u00d7 RSS, 96% coverage)',  GREEN, GREEN_L),
    ('Set swath overlap',                  '20%  (covers 4.6 m lane error)',       GREY,  GREY_L),
]

phase_a_steps = 4  # Steps 1-4
top_y = 13.5

# Draw phase bracket labels on the left
phase_a_top = top_y + box_h
phase_a_bot = top_y - (phase_a_steps - 1) * (box_h + gap)
phase_b_top = top_y - phase_a_steps * (box_h + gap) + box_h
phase_b_bot = top_y - (len(decisions) - 1) * (box_h + gap)

bracket_x = 0.65

# Phase A bracket
mid_a = (phase_a_top + phase_a_bot) / 2
ax.plot([bracket_x, bracket_x], [phase_a_bot, phase_a_top], color=PHASE_A_COL, lw=2.5, zorder=4)
ax.plot([bracket_x, bracket_x + 0.22], [phase_a_top, phase_a_top], color=PHASE_A_COL, lw=2.5, zorder=4)
ax.plot([bracket_x, bracket_x + 0.22], [phase_a_bot, phase_a_bot], color=PHASE_A_COL, lw=2.5, zorder=4)
ax.text(bracket_x - 0.15, mid_a, 'Phase A\nMeasure', ha='center', va='center',
        fontsize=7.5, fontweight='bold', color=PHASE_A_COL, rotation=90, zorder=5)

# Phase B bracket
mid_b = (phase_b_top + phase_b_bot) / 2
ax.plot([bracket_x, bracket_x], [phase_b_bot, phase_b_top], color=PHASE_B_COL, lw=2.5, zorder=4)
ax.plot([bracket_x, bracket_x + 0.22], [phase_b_top, phase_b_top], color=PHASE_B_COL, lw=2.5, zorder=4)
ax.plot([bracket_x, bracket_x + 0.22], [phase_b_bot, phase_b_bot], color=PHASE_B_COL, lw=2.5, zorder=4)
ax.text(bracket_x - 0.15, mid_b, 'Phase B\nOptimise', ha='center', va='center',
        fontsize=7.5, fontweight='bold', color=PHASE_B_COL, rotation=90, zorder=5)

# Thin horizontal separator between phases
sep_y = top_y - phase_a_steps * (box_h + gap) + box_h + gap / 2 + 0.02
ax.plot([chain_x + 0.3, chain_x + chain_w - 0.3], [sep_y, sep_y],
        color=GREY, lw=0.6, ls='--', zorder=3)

for i, (label, value, col, bg) in enumerate(decisions):
    y = top_y - i * (box_h + gap)
    rounded_box(chain_x, y, chain_w, box_h, bg, col, lw=1.5)

    # Step number circle
    circle = plt.Circle((chain_x + 0.38, y + box_h/2), 0.18,
                         fc=col, ec=col, zorder=4)
    ax.add_patch(circle)
    ax.text(chain_x + 0.38, y + box_h/2, str(i+1), ha='center', va='center',
            fontsize=8.5, fontweight='bold', color=WHITE, zorder=5)

    # Label
    ax.text(chain_x + 0.75, y + box_h/2 + 0.15, label,
            ha='left', va='center', fontsize=9, fontweight='bold', color=DARK, zorder=5)

    # Arrow + value
    ax.text(chain_x + 0.75, y + box_h/2 - 0.15, '\u2192  ' + value,
            ha='left', va='center', fontsize=8.5, color=col, zorder=5,
            fontweight='semibold')

    # Arrow to next box
    if i < len(decisions) - 1:
        arrow_down(5.5, y, y - gap + 0.02, color=col)

# ═══════════════════════════════════════════════════════════════════════
# RESULT BOX
# ═══════════════════════════════════════════════════════════════════════
last_y = top_y - (len(decisions) - 1) * (box_h + gap)
res_y = last_y - gap - 1.15
res_h = 1.10
arrow_down(5.5, last_y, res_y + res_h + 0.04, color=DARK)

rounded_box(chain_x, res_y, chain_w, res_h, RESULT_BG, RESULT_BD, lw=2.5)
ax.text(5.5, res_y + res_h - 0.18, 'Selected Configuration',
        ha='center', va='center', fontsize=11, fontweight='bold', color=DARK, zorder=5)
ax.text(5.5, res_y + res_h/2 + 0.02,
        '35 m  |  8 m/s  |  lawnmower  |  70\u00b0  |  20% overlap  |  30 m NFZ',
        ha='center', va='center', fontsize=9, color=DARK, zorder=5)
ax.text(5.5, res_y + res_h/2 - 0.30,
        '12.6 Wh   |   112 s   |   92% detection probability',
        ha='center', va='center', fontsize=8.5, color=GREY, zorder=5)
# 15% margin callout
ax.text(5.5, res_y + 0.12,
        '15% safety margin applied to all empirical limits',
        ha='center', va='center', fontsize=7.5, color=GREEN, fontweight='bold',
        style='italic', zorder=5)

# ── Legend ──
leg_y = res_y - 0.45
for cx, col, lbl in [(2.5, GREEN, 'Safety'), (5.0, BLUE, 'Detection'), (7.5, GREY, 'Secondary')]:
    ax.plot(cx - 0.25, leg_y, 's', color=col, markersize=7)
    ax.text(cx + 0.0, leg_y, lbl, va='center', fontsize=7.5, color=col)

plt.tight_layout(pad=0.3)
fig.savefig(r'c:\Users\Bristol\Desktop\AI for Robotics\v3\report\figs\decision_flow.pdf',
            bbox_inches='tight', dpi=300)
fig.savefig(r'c:\Users\Bristol\Desktop\AI for Robotics\v3\report\figs\decision_flow.png',
            bbox_inches='tight', dpi=300)
print('Saved decision_flow.pdf and decision_flow.png')
