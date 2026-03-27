"""Generate TWO state machine diagrams:
  1. state_machine_simple.pdf — 10-state simplified (matches existing style)
  2. state_machine_full.pdf  — all 19 states grouped by phase with coloured backgrounds

Run: python report/figs/gen_state_machine_full.py
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np

# ── Colour palette ──────────────────────────────────────────────────
GREY       = '#95a5a6'
GREY_LIGHT = '#ecf0f1'
BLUE_LIGHT = '#d6eaf8'
BLUE       = '#3498db'
BLUE_DARK  = '#2980b9'
ORANGE     = '#e67e22'
ORANGE_DARK= '#d35400'
ORANGE_LIGHT='#fdebd0'
GREEN      = '#2ecc71'
GREEN_DARK = '#27ae60'
RED        = '#e74c3c'
RED_DARK   = '#c0392b'
RED_LIGHT  = '#fadbd8'
YELLOW     = '#f9e79f'
WHITE      = '#ffffff'
TEXT_DARK  = '#2c3e50'

OUT = 'c:/Users/Bristol/Desktop/AI for Robotics/v3/report/figs/'

# ════════════════════════════════════════════════════════════════════
#  HELPERS
# ════════════════════════════════════════════════════════════════════

def draw_box(ax, cx, cy, w, h, text, color, text_color='white', fontsize=8.5,
             bold=True):
    box = FancyBboxPatch((cx - w/2, cy - h/2), w, h,
                         boxstyle="round,pad=0.08", linewidth=1.2,
                         edgecolor='white', facecolor=color, zorder=4)
    ax.add_patch(box)
    ax.text(cx, cy, text, ha='center', va='center', fontsize=fontsize,
            fontweight='bold' if bold else 'normal', color=text_color, zorder=5)

def draw_phase_bg(ax, x, y, w, h, label, color, label_fontsize=7.5):
    """Rounded rectangle phase background with label in top-left."""
    bg = FancyBboxPatch((x, y), w, h,
                        boxstyle="round,pad=0.15", linewidth=0.8,
                        edgecolor='#bbb', facecolor=color, alpha=0.45, zorder=1)
    ax.add_patch(bg)
    ax.text(x + 0.15, y + h - 0.15, label, ha='left', va='top',
            fontsize=label_fontsize, fontweight='bold', color='#555', zorder=2)

def arrow(ax, x1, y1, x2, y2, label='', color='#555', lw=1.2, fontsize=7,
          label_offset=(0, 0), rad=0, style='->', linestyle='-'):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle=style, color=color, lw=lw,
                                linestyle=linestyle,
                                connectionstyle=f'arc3,rad={rad}'),
                zorder=3)
    if label:
        mx = (x1 + x2) / 2 + label_offset[0]
        my = (y1 + y2) / 2 + label_offset[1]
        ax.text(mx, my, label, ha='center', va='center', fontsize=fontsize,
                color=color, fontstyle='italic', zorder=6,
                bbox=dict(boxstyle='round,pad=0.08', facecolor='white',
                          edgecolor='none', alpha=0.9))

# ════════════════════════════════════════════════════════════════════
#  1) SIMPLIFIED (matches existing diagram, re-exported as _simple)
# ════════════════════════════════════════════════════════════════════

def gen_simple():
    fig, ax = plt.subplots(1, 1, figsize=(10, 7))
    ax.set_xlim(-0.5, 10.5)
    ax.set_ylim(-1.5, 8.5)
    ax.set_aspect('equal')
    ax.axis('off')

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
    for name, (cx, cy) in positions.items():
        draw_box(ax, cx, cy, bw, bh, name, colors[name], fontsize=9)

    main_flow = [('INIT','TAKEOFF'),('TAKEOFF','SEARCH'),('SEARCH','CENTERING'),
                 ('CENTERING','VERIFY'),('APPROACH','LANDING'),('LANDING','DONE')]
    for a, b in main_flow:
        x1,y1 = positions[a]; x2,y2 = positions[b]
        arrow(ax, x1, y1-bh/2, x2, y2+bh/2)

    # VERIFY -> APPROACH (Y)
    vx,vy = positions['VERIFY']; ax_,ay = positions['APPROACH']
    arrow(ax, vx, vy-bh/2, ax_, ay+bh/2, label='Confirmed [Y]', color=GREEN_DARK,
          label_offset=(0.05, 0.15))

    # VERIFY -> SEARCH (N) — curved left
    arrow(ax, vx-bw/2, vy, 0.3, vy, color=ORANGE_DARK, lw=1.1)
    ax.annotate('', xy=(0.3, positions['SEARCH'][1]), xytext=(0.3, vy),
                arrowprops=dict(arrowstyle='->', color=ORANGE_DARK, lw=1.1), zorder=2)
    ax.annotate('', xy=(positions['SEARCH'][0]-bw/2, positions['SEARCH'][1]),
                xytext=(0.3, positions['SEARCH'][1]),
                arrowprops=dict(arrowstyle='->', color=ORANGE_DARK, lw=1.1), zorder=2)
    ax.text(-0.05, (vy+positions['SEARCH'][1])/2, 'Rejected\n[N]', ha='center',
            va='center', fontsize=7.5, color=ORANGE_DARK, fontstyle='italic',
            bbox=dict(boxstyle='round,pad=0.1', facecolor='white', edgecolor='none', alpha=0.85), zorder=5)

    # SEARCH->CENTERING label
    arrow(ax, positions['SEARCH'][0], positions['SEARCH'][1]-bh/2,
          positions['CENTERING'][0], positions['CENTERING'][1]+bh/2,
          label='Detection', color=BLUE_DARK, label_offset=(0.05,0.15))

    # Any -> MANUAL
    ax.annotate('', xy=(positions['MANUAL'][0]-bw/2, positions['MANUAL'][1]),
                xytext=(positions['SEARCH'][0]+bw/2+0.15, positions['SEARCH'][1]),
                arrowprops=dict(arrowstyle='->', color=RED_DARK, lw=1.1,
                                linestyle='dashed', connectionstyle='arc3,rad=-0.15'), zorder=2)
    ax.text(4.85, 5.7, 'M key\n(override)', ha='center', va='center', fontsize=7,
            color=RED_DARK, fontstyle='italic',
            bbox=dict(boxstyle='round,pad=0.1', facecolor='white', edgecolor='none', alpha=0.85), zorder=5)

    ax.annotate('', xy=(positions['SEARCH'][0]+bw/2+0.15, positions['SEARCH'][1]-0.3),
                xytext=(positions['MANUAL'][0]-bw/2, positions['MANUAL'][1]-0.2),
                arrowprops=dict(arrowstyle='->', color=RED_DARK, lw=1.1,
                                linestyle='dashed', connectionstyle='arc3,rad=-0.15'), zorder=2)
    ax.text(4.85, 4.45, 'M key\n(resume)', ha='center', va='center', fontsize=7,
            color=RED_DARK, fontstyle='italic',
            bbox=dict(boxstyle='round,pad=0.1', facecolor='white', edgecolor='none', alpha=0.85), zorder=5)

    # RTL annotation (firmware behaviour, not a state)
    ax.text(7.0, 2.7, 'Link loss / RC kill\n  RTL (firmware)', ha='center',
            va='center', fontsize=7.5, color=RED, fontstyle='italic',
            bbox=dict(boxstyle='round,pad=0.15', facecolor='#fadbd8',
                      edgecolor=RED, alpha=0.8, linewidth=0.8), zorder=5)
    ax.annotate('', xy=(5.95, 2.7),
                xytext=(positions['VERIFY'][0]+bw/2+0.15, positions['VERIFY'][1]),
                arrowprops=dict(arrowstyle='->', color=RED, lw=1.1,
                                linestyle='dotted', connectionstyle='arc3,rad=0.15'), zorder=2)

    legend_items = [
        mpatches.Patch(color=GREEN, label='Start / End'),
        mpatches.Patch(color=BLUE, label='Autonomous'),
        mpatches.Patch(color=ORANGE, label='Operator decision'),
        mpatches.Patch(color=RED, label='Safety override'),
    ]
    ax.legend(handles=legend_items, loc='upper right', fontsize=8, frameon=True,
              fancybox=True, framealpha=0.9, edgecolor='#cccccc')

    plt.tight_layout()
    plt.savefig(OUT + 'state_machine_simple.pdf', bbox_inches='tight', dpi=300)
    plt.savefig(OUT + 'state_machine_simple.png', bbox_inches='tight', dpi=300)
    plt.close()
    print("OK: state_machine_simple.pdf + .png")


# ════════════════════════════════════════════════════════════════════
#  2) COMPLETE — all 19 states with phase groupings
# ════════════════════════════════════════════════════════════════════

def gen_full():
    fig, ax = plt.subplots(1, 1, figsize=(14, 12))
    ax.set_xlim(-1.5, 14.5)
    ax.set_ylim(-2.5, 12.5)
    ax.set_aspect('equal')
    ax.axis('off')

    bw, bh = 2.0, 0.52

    # ── Positions ───────────────────────────────────────────────
    # Column 1: main downward flow (left)
    # Column 2: engagement/verify (centre)
    # Column 3: recovery / safety (right)

    P = {
        # Startup (col 1, top)
        'INIT':              (1.5, 11.5),
        'CONNECTING':        (1.5, 10.5),
        'ARMING':            (1.5,  9.5),
        'TAKEOFF':           (1.5,  8.5),

        # Transit (col 1, middle)
        'PRE_WAYPOINTS':     (1.5,  7.2),
        'TRANSIT_TO_SEARCH': (1.5,  6.2),

        # Search (col 1, lower)
        'SEARCH':            (1.5,  4.7),

        # Engagement (col 2)
        'CENTERING':         (5.5,  4.7),
        'DESCENDING':        (5.5,  3.7),
        'VERIFY':            (5.5,  2.7),
        'HOVER_TARGET':      (5.5,  1.5),

        # Confirmed path (bottom row)
        'APPROACH':          (5.5,  0.0),
        'LANDING':           (5.5, -1.2),
        'DONE':              (5.5, -2.0),

        # Recovery (col 3, right)
        'RETURN_TO_SEARCH':  (9.5,  4.7),
        'RETURN_FROM_MANUAL':(9.5,  6.2),
        'RETURN_TRANSIT':    (9.5,  2.7),
        'RETURN_HOME':       (9.5,  1.5),

        # Fallback
        'HOVER':             (1.5,  3.3),

        # Safety (far right)
        'MANUAL':            (12.5, 7.5),
    }

    # ── Phase backgrounds ───────────────────────────────────────
    # (x, y_bottom, w, h)
    draw_phase_bg(ax, -0.1, 8.0, 3.2, 4.2, 'Startup', GREY_LIGHT)
    draw_phase_bg(ax, -0.1, 5.7, 3.2, 2.0, 'Transit', BLUE_LIGHT)
    draw_phase_bg(ax, -0.1, 4.15, 3.2, 1.15, 'Search', '#d5f5e3')
    draw_phase_bg(ax, 3.9, -0.55, 3.2, 6.0, 'Engagement', ORANGE_LIGHT)
    draw_phase_bg(ax, 7.9, 1.0, 3.2, 5.9, 'Recovery', YELLOW)
    draw_phase_bg(ax, 11.0, 6.9, 3.2, 1.5, 'Safety', RED_LIGHT)

    # ── State colours ───────────────────────────────────────────
    C = {
        'INIT': GREY, 'CONNECTING': GREY, 'ARMING': GREY, 'TAKEOFF': GREY,
        'PRE_WAYPOINTS': BLUE, 'TRANSIT_TO_SEARCH': BLUE,
        'SEARCH': GREEN_DARK,
        'CENTERING': ORANGE, 'DESCENDING': ORANGE, 'VERIFY': ORANGE,
        'HOVER_TARGET': ORANGE,
        'HOVER': GREY,
        'APPROACH': BLUE, 'LANDING': BLUE, 'DONE': GREEN,
        'RETURN_TO_SEARCH': '#f1c40f', 'RETURN_FROM_MANUAL': '#f1c40f',
        'RETURN_TRANSIT': '#f1c40f', 'RETURN_HOME': '#f1c40f',
        'MANUAL': RED,
    }

    # Draw all state boxes
    for name, (cx, cy) in P.items():
        tc = 'white'
        if name in ('RETURN_TO_SEARCH','RETURN_FROM_MANUAL','RETURN_TRANSIT','RETURN_HOME'):
            tc = TEXT_DARK
        label = name.replace('_', '_\n') if len(name) > 14 else name
        # Wider box for long names
        w = bw + 0.4 if len(name) > 14 else bw
        draw_box(ax, cx, cy, w, bh, label, C[name], text_color=tc, fontsize=7.5)

    # ── Arrows — main startup flow ──────────────────────────────
    startup_flow = [('INIT','CONNECTING'), ('CONNECTING','ARMING'),
                    ('ARMING','TAKEOFF')]
    for a, b in startup_flow:
        x1,y1 = P[a]; x2,y2 = P[b]
        arrow(ax, x1, y1-bh/2, x2, y2+bh/2, color=GREY)

    # TAKEOFF -> PRE_WAYPOINTS
    arrow(ax, P['TAKEOFF'][0], P['TAKEOFF'][1]-bh/2,
          P['PRE_WAYPOINTS'][0], P['PRE_WAYPOINTS'][1]+bh/2, color=BLUE_DARK)

    # Transit
    arrow(ax, P['PRE_WAYPOINTS'][0], P['PRE_WAYPOINTS'][1]-bh/2,
          P['TRANSIT_TO_SEARCH'][0], P['TRANSIT_TO_SEARCH'][1]+bh/2, color=BLUE_DARK)

    # TRANSIT -> SEARCH
    arrow(ax, P['TRANSIT_TO_SEARCH'][0], P['TRANSIT_TO_SEARCH'][1]-bh/2,
          P['SEARCH'][0], P['SEARCH'][1]+bh/2, color=BLUE_DARK)

    # HOVER fallback (no waypoints generated — error state)
    arrow(ax, P['SEARCH'][0], P['SEARCH'][1]-bh/2,
          P['HOVER'][0], P['HOVER'][1]+bh/2,
          label='No WPs', color=GREY, linestyle='--', fontsize=6.5,
          label_offset=(0.6, 0.15))

    # ── SEARCH -> CENTERING (detection) ─────────────────────────
    arrow(ax, P['SEARCH'][0]+bw/2, P['SEARCH'][1],
          P['CENTERING'][0]-bw/2, P['CENTERING'][1],
          label='Detection', color=ORANGE_DARK, label_offset=(0, 0.25))

    # ── Engagement flow ─────────────────────────────────────────
    arrow(ax, P['CENTERING'][0], P['CENTERING'][1]-bh/2,
          P['DESCENDING'][0], P['DESCENDING'][1]+bh/2, color=ORANGE_DARK)
    arrow(ax, P['DESCENDING'][0], P['DESCENDING'][1]-bh/2,
          P['VERIFY'][0], P['VERIFY'][1]+bh/2, color=ORANGE_DARK)

    # VERIFY -> HOVER_TARGET (Y confirmed, averaging GPS)
    arrow(ax, P['VERIFY'][0], P['VERIFY'][1]-bh/2,
          P['HOVER_TARGET'][0], P['HOVER_TARGET'][1]+bh/2,
          label='Y (confirm)', color=GREEN_DARK, label_offset=(0.1, 0.15))

    # HOVER_TARGET -> APPROACH (side selected)
    arrow(ax, P['HOVER_TARGET'][0], P['HOVER_TARGET'][1]-bh/2,
          P['APPROACH'][0], P['APPROACH'][1]+bh/2,
          label='Side selected', color=BLUE_DARK, label_offset=(0.1, 0.15))

    # APPROACH -> LANDING
    arrow(ax, P['APPROACH'][0], P['APPROACH'][1]-bh/2,
          P['LANDING'][0], P['LANDING'][1]+bh/2,
          color=BLUE_DARK)

    # LANDING -> DONE
    arrow(ax, P['LANDING'][0], P['LANDING'][1]-bh/2,
          P['DONE'][0], P['DONE'][1]+bh/2,
          color=GREEN_DARK)

    # ── Rejected [N] → RETURN_TO_SEARCH → SEARCH ───────────────
    arrow(ax, P['VERIFY'][0]+bw/2, P['VERIFY'][1]-0.1,
          P['RETURN_TO_SEARCH'][0]-bw/2-0.2, P['RETURN_TO_SEARCH'][1]-0.1,
          label='N (reject)', color=ORANGE_DARK, label_offset=(0, -0.3), rad=0.2)

    # I (interest) → RETURN_TO_SEARCH
    arrow(ax, P['VERIFY'][0]+bw/2, P['VERIFY'][1]+0.1,
          P['RETURN_TO_SEARCH'][0]-bw/2-0.2, P['RETURN_TO_SEARCH'][1]+0.1,
          label='I (interest)', color='#8e44ad', label_offset=(0, 0.3), rad=-0.2)

    # RETURN_TO_SEARCH -> SEARCH (loop back)
    arrow(ax, P['RETURN_TO_SEARCH'][0]-bw/2-0.2, P['RETURN_TO_SEARCH'][1],
          P['SEARCH'][0]+bw/2, P['SEARCH'][1],
          label='Resume\nsearch', color='#d4ac0d', label_offset=(0.5, 0.25))

    # ── HOVER_TARGET -> RETURN_TRANSIT -> RETURN_HOME -> LANDING
    arrow(ax, P['HOVER_TARGET'][0]+bw/2, P['HOVER_TARGET'][1],
          P['RETURN_TRANSIT'][0]-bw/2-0.2, P['RETURN_TRANSIT'][1],
          label='Deploy done\n(15 s)', color='#d4ac0d', label_offset=(0, 0.25))

    arrow(ax, P['RETURN_TRANSIT'][0], P['RETURN_TRANSIT'][1]-bh/2,
          P['RETURN_HOME'][0], P['RETURN_HOME'][1]+bh/2,
          color='#d4ac0d')

    # RETURN_HOME -> LANDING (curve left toward LANDING column)
    arrow(ax, P['RETURN_HOME'][0]-bw/2-0.2, P['RETURN_HOME'][1],
          P['LANDING'][0]+bw/2, P['LANDING'][1],
          color=BLUE_DARK, rad=-0.3)

    # ── MANUAL (M key from any state) ───────────────────────────
    # Dashed arrow from centre of main flow toward MANUAL
    arrow(ax, P['SEARCH'][0]+bw/2+0.2, P['SEARCH'][1]+0.6,
          P['MANUAL'][0]-bw/2, P['MANUAL'][1]-0.1,
          label='M key\n(any state)', color=RED_DARK, label_offset=(-0.5, 0.3),
          linestyle='--', rad=-0.1)

    # MANUAL -> RETURN_FROM_MANUAL
    arrow(ax, P['MANUAL'][0]-bw/2, P['MANUAL'][1]-0.2,
          P['RETURN_FROM_MANUAL'][0]+bw/2+0.2, P['RETURN_FROM_MANUAL'][1]+0.15,
          label='M key\n(resume)', color=RED_DARK, label_offset=(0, 0.3),
          linestyle='--', rad=0.15)

    # RETURN_FROM_MANUAL -> previous state (could be any state, shown toward search area)
    arrow(ax, P['RETURN_FROM_MANUAL'][0]-bw/2-0.2, P['RETURN_FROM_MANUAL'][1]-0.15,
          P['TRANSIT_TO_SEARCH'][0]+bw/2, P['TRANSIT_TO_SEARCH'][1]+0.15,
          label='Resume\nprevious', color='#d4ac0d', label_offset=(0.5, 0.25))

    # ── Timeout transitions (dashed) ─────────────────────────────
    # CENTERING -> SEARCH (60s timeout)
    arrow(ax, P['CENTERING'][0]-bw/2, P['CENTERING'][1]+0.1,
          P['SEARCH'][0]+bw/2, P['SEARCH'][1]-0.1,
          label='60 s\ntimeout', color=GREY, label_offset=(0, -0.3),
          linestyle='--', fontsize=6.5, rad=-0.15)

    # VERIFY -> SEARCH (120s timeout — curved left through search column)
    arrow(ax, P['VERIFY'][0]-bw/2, P['VERIFY'][1],
          P['SEARCH'][0]+bw/2, P['SEARCH'][1]-0.2,
          label='120 s\ntimeout', color=GREY, label_offset=(-0.3, 0.3),
          linestyle='--', fontsize=6.5, rad=0.3)

    # HOVER -> DONE (60s timeout)
    arrow(ax, P['HOVER'][0]+bw/2, P['HOVER'][1]-0.1,
          P['DONE'][0]-bw/2, P['DONE'][1]+0.1,
          label='60 s', color=GREY, label_offset=(0, -0.25),
          linestyle='--', fontsize=6.5, rad=0.3)

    # VERIFY -> CENTERING (N/I with queued target)
    arrow(ax, P['VERIFY'][0]+0.3, P['VERIFY'][1]+bh/2,
          P['CENTERING'][0]+0.3, P['CENTERING'][1]-bh/2,
          label='N/I +\nqueue', color=ORANGE_DARK, label_offset=(0.55, 0),
          fontsize=6.5, rad=-0.3)

    # ── Search exhausted -> DONE (via left side) ────────────────
    # Down from SEARCH, curve around to DONE
    sx, sy = P['SEARCH']
    dx, dy = P['DONE']
    # Draw a path: SEARCH bottom -> down -> right to DONE
    ax.annotate('', xy=(dx - bw/2, dy),
                xytext=(sx, sy - bh/2),
                arrowprops=dict(arrowstyle='->', color=BLUE_DARK, lw=1.2,
                                connectionstyle='arc3,rad=0.5'), zorder=3)
    ax.text(0.5, 1.5, 'All waypoints\nexhausted', ha='center', va='center',
            fontsize=7, color=BLUE_DARK, fontstyle='italic',
            bbox=dict(boxstyle='round,pad=0.08', facecolor='white',
                      edgecolor='none', alpha=0.9), zorder=6)

    # ── RTL annotation ──────────────────────────────────────────
    ax.text(12.5, 6.2, 'Link loss / RC kill\n  RTL (firmware)', ha='center',
            va='center', fontsize=7.5, color=RED, fontstyle='italic',
            bbox=dict(boxstyle='round,pad=0.15', facecolor=RED_LIGHT,
                      edgecolor=RED, alpha=0.8, linewidth=0.8), zorder=6)

    # ── Legend ──────────────────────────────────────────────────
    legend_items = [
        mpatches.Patch(color=GREY,       label='Startup'),
        mpatches.Patch(color=BLUE,       label='Transit / Autonomous'),
        mpatches.Patch(color=GREEN_DARK, label='Search'),
        mpatches.Patch(color=ORANGE,     label='Engagement / Verify'),
        mpatches.Patch(color='#f1c40f',  label='Recovery'),
        mpatches.Patch(color=RED,        label='Safety (Manual)'),
    ]
    ax.legend(handles=legend_items, loc='upper left', fontsize=8, frameon=True,
              fancybox=True, framealpha=0.95, edgecolor='#cccccc',
              bbox_to_anchor=(-0.08, 1.02))

    plt.tight_layout()
    plt.savefig(OUT + 'state_machine_full.pdf', bbox_inches='tight', dpi=300)
    plt.savefig(OUT + 'state_machine_full.png', bbox_inches='tight', dpi=300)
    plt.close()
    print("OK: state_machine_full.pdf + .png")


# ════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    gen_simple()
    gen_full()
    print("Done — both diagrams generated.")
