"""
Optimization variable dependency/influence network diagram.
Shows how decision variables flow through derived quantities to performance metrics.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

fig, ax = plt.subplots(1, 1, figsize=(16, 11))
ax.set_xlim(-0.5, 10.5)
ax.set_ylim(-0.5, 10.5)
ax.axis('off')

# ── Colours ──────────────────────────────────────────────────────────────
COL_INPUT  = '#4A90D9'   # blue
COL_MID    = '#FFFFFF'   # white
COL_GOOD   = '#5CB85C'   # green  (maximise)
COL_BAD    = '#D9534F'   # red    (minimise)
EDGE_INPUT = '#2C5F8A'
EDGE_MID   = '#888888'
TEXT_INPUT  = 'white'
TEXT_MID    = 'black'
TEXT_OUT    = 'white'

# ── Node specs: (x, y, label, colour, edge_colour, text_colour, w, h) ───
nodes = {}

def add(key, x, y, label, col, ecol, tcol, w=1.4, h=0.48):
    nodes[key] = dict(x=x, y=y, label=label, col=col, ecol=ecol, tcol=tcol, w=w, h=h)

# --- Decision variables (left column, x≈0.8) ---
add('h',     0.9, 8.5, 'Altitude  $h$',         COL_INPUT, EDGE_INPUT, TEXT_INPUT, 1.5)
add('theta', 0.9, 6.8, 'Scan angle  $\\theta$',  COL_INPUT, EDGE_INPUT, TEXT_INPUT, 1.5)
add('v',     0.9, 5.1, 'Ground speed  $v$',      COL_INPUT, EDGE_INPUT, TEXT_INPUT, 1.5)
add('alpha', 0.9, 3.4, 'Overlap  $\\alpha$',      COL_INPUT, EDGE_INPUT, TEXT_INPUT, 1.5)
add('dnfz',  0.9, 1.7, 'NFZ margin  $d_{nfz}$',  COL_INPUT, EDGE_INPUT, TEXT_INPUT, 1.5)

# --- Derived quantities (middle columns, x≈4–6) ---
add('footprint', 4.2, 9.2, 'Ground footprint\n$w_s h / f$',       COL_MID, EDGE_MID, TEXT_MID, 1.6, 0.55)
add('lane_sp',   4.2, 7.5, 'Lane spacing\n$W(1-\\alpha)$',        COL_MID, EDGE_MID, TEXT_MID, 1.6, 0.55)
add('scan_n',    6.2, 7.5, 'Scan lines\n$N_{lines}$',             COL_MID, EDGE_MID, TEXT_MID, 1.4, 0.55)
add('tgt_px',    4.2, 5.8, 'Target pixels\n$h_{dummy} f_{px}/h$', COL_MID, EDGE_MID, TEXT_MID, 1.6, 0.55)
add('gsd',       4.2, 4.3, 'GSD\n(m/px)',                         COL_MID, EDGE_MID, TEXT_MID, 1.2, 0.55)
add('frames',    6.2, 5.8, 'Frames on\ntarget',                   COL_MID, EDGE_MID, TEXT_MID, 1.4, 0.55)
add('blur',      6.2, 4.3, 'Motion blur\n$v t_{exp}/GSD$',        COL_MID, EDGE_MID, TEXT_MID, 1.5, 0.55)
add('path_l',    6.2, 9.2, 'Path length\n(total m)',              COL_MID, EDGE_MID, TEXT_MID, 1.4, 0.55)
add('uturns',    7.8, 7.5, 'U-turns\n$N_{turns}$',                COL_MID, EDGE_MID, TEXT_MID, 1.2, 0.55)
add('tnfz',      4.2, 1.7, 'Time near\nNFZ',                      COL_MID, EDGE_MID, TEXT_MID, 1.3, 0.55)

# --- Performance metrics (right column, x≈9.3) ---
add('coverage',  9.3, 8.8, 'Coverage %\n(maximise)',     COL_GOOD, '#3D8B3D', TEXT_OUT, 1.5, 0.55)
add('det_prob',  9.3, 6.2, 'Detection\nprobability\n(maximise)', COL_GOOD, '#3D8B3D', TEXT_OUT, 1.5, 0.68)
add('time_m',    9.3, 4.3, 'Mission time\n(minimise)',   COL_BAD,  '#A33', TEXT_OUT, 1.5, 0.55)
add('energy',    9.3, 2.6, 'Energy use\n(minimise)',     COL_BAD,  '#A33', TEXT_OUT, 1.5, 0.55)
add('nfz_risk',  9.3, 1.0, 'NFZ risk\n(minimise)',      COL_BAD,  '#A33', TEXT_OUT, 1.5, 0.55)

# ── Draw nodes ───────────────────────────────────────────────────────────
for k, n in nodes.items():
    box = FancyBboxPatch(
        (n['x'] - n['w']/2, n['y'] - n['h']/2), n['w'], n['h'],
        boxstyle="round,pad=0.08", facecolor=n['col'],
        edgecolor=n['ecol'], linewidth=1.5, zorder=3
    )
    ax.add_patch(box)
    ax.text(n['x'], n['y'], n['label'], ha='center', va='center',
            fontsize=8, color=n['tcol'], fontweight='bold', zorder=4)

# ── Edges: (from, to, strength) ─────────────────────────────────────────
#   strength: 'strong' (thick, dark), 'medium', 'weak' (thin, light)
edges = [
    # h chains
    ('h', 'footprint', 'strong'),
    ('h', 'tgt_px',    'strong'),
    ('h', 'gsd',       'strong'),

    # footprint chains
    ('footprint', 'lane_sp',  'strong'),
    ('footprint', 'frames',   'medium'),

    # lane spacing chains
    ('lane_sp', 'scan_n',    'strong'),
    ('lane_sp', 'coverage',  'medium'),

    # scan lines
    ('scan_n', 'path_l',    'strong'),
    ('scan_n', 'uturns',    'strong'),

    # path length
    ('path_l', 'time_m',    'strong'),
    ('path_l', 'energy',    'strong'),

    # U-turns
    ('uturns', 'energy',    'medium'),
    ('uturns', 'time_m',    'weak'),

    # target pixels → detection
    ('tgt_px', 'det_prob',  'strong'),

    # GSD → blur
    ('gsd', 'blur',         'medium'),

    # blur → detection
    ('blur', 'det_prob',    'strong'),

    # frames → detection
    ('frames', 'det_prob',  'medium'),

    # v chains
    ('v', 'frames',   'strong'),
    ('v', 'blur',     'strong'),
    ('v', 'time_m',   'medium'),

    # theta
    ('theta', 'scan_n',  'strong'),

    # alpha
    ('alpha', 'lane_sp',  'strong'),
    ('alpha', 'coverage', 'medium'),

    # d_nfz
    ('dnfz', 'tnfz',     'strong'),
    ('tnfz', 'energy',   'weak'),
    ('tnfz', 'nfz_risk', 'strong'),
    ('dnfz', 'nfz_risk', 'medium'),
]

# Style map
style_map = {
    'strong': dict(lw=2.2, color='#333333', alpha=0.85),
    'medium': dict(lw=1.4, color='#666666', alpha=0.65),
    'weak':   dict(lw=0.8, color='#999999', alpha=0.45),
}

def node_border(key, side):
    """Return connection point on the node border."""
    n = nodes[key]
    cx, cy = n['x'], n['y']
    hw, hh = n['w']/2, n['h']/2
    if side == 'r':
        return cx + hw, cy
    elif side == 'l':
        return cx - hw, cy
    elif side == 't':
        return cx, cy + hh
    elif side == 'b':
        return cx, cy - hh
    return cx, cy

def pick_sides(k1, k2):
    """Choose which side of each box to connect from/to."""
    n1, n2 = nodes[k1], nodes[k2]
    dx = n2['x'] - n1['x']
    dy = n2['y'] - n1['y']
    # Mostly horizontal
    if abs(dx) > abs(dy) * 0.5:
        s1 = 'r' if dx > 0 else 'l'
        s2 = 'l' if dx > 0 else 'r'
    else:
        s1 = 't' if dy > 0 else 'b'
        s2 = 'b' if dy > 0 else 't'
    return s1, s2

# Custom curvature overrides for long/crossing edges
custom_rad = {
    ('v', 'time_m'):    0.25,
    ('v', 'blur'):      0.15,
    ('v', 'frames'):    0.12,
    ('h', 'gsd'):       -0.15,
    ('h', 'tgt_px'):    -0.10,
    ('dnfz', 'nfz_risk'): -0.20,
    ('tnfz', 'energy'):  0.20,
    ('alpha', 'coverage'): -0.30,
    ('uturns', 'time_m'): 0.15,
}

for src, dst, strength in edges:
    s = style_map[strength]
    s1, s2 = pick_sides(src, dst)
    x1, y1 = node_border(src, s1)
    x2, y2 = node_border(dst, s2)

    rad = custom_rad.get((src, dst), 0.08)

    arrow = FancyArrowPatch(
        (x1, y1), (x2, y2),
        arrowstyle='-|>',
        mutation_scale=12,
        linewidth=s['lw'],
        color=s['color'],
        alpha=s['alpha'],
        connectionstyle=f'arc3,rad={rad}',
        zorder=2,
        shrinkA=2, shrinkB=2,
    )
    ax.add_patch(arrow)

# ── Column headers ───────────────────────────────────────────────────────
ax.text(0.9, 10.1, 'Decision Variables', ha='center', va='center',
        fontsize=11, fontweight='bold', color=EDGE_INPUT)
ax.text(5.2, 10.1, 'Derived Quantities', ha='center', va='center',
        fontsize=11, fontweight='bold', color='#555')
ax.text(9.3, 10.1, 'Performance Metrics', ha='center', va='center',
        fontsize=11, fontweight='bold', color='#3D8B3D')

# ── Legend ───────────────────────────────────────────────────────────────
legend_y = 0.15
for i, (sname, sdict) in enumerate(style_map.items()):
    xoff = 3.0 + i * 2.5
    ax.annotate('', xy=(xoff + 0.8, legend_y), xytext=(xoff, legend_y),
                arrowprops=dict(arrowstyle='-|>', lw=sdict['lw'],
                                color=sdict['color'], alpha=sdict['alpha'],
                                mutation_scale=10))
    ax.text(xoff + 0.9, legend_y, sname, va='center', fontsize=8, color='#444')

# Title
fig.suptitle('Optimisation Variable Dependency Network', fontsize=14, fontweight='bold', y=0.97)

plt.tight_layout(rect=[0, 0.02, 1, 0.95])

# Save
fig.savefig(r'c:\Users\Bristol\Desktop\AI for Robotics\v3\report\figs\optimization_network.pdf',
            bbox_inches='tight', dpi=300)
fig.savefig(r'c:\Users\Bristol\Desktop\AI for Robotics\v3\report\figs\optimization_network.png',
            bbox_inches='tight', dpi=300)
print('Saved optimization_network.pdf and .png')
