"""Vision Pipeline: Full horizontal flow from camera capture to GPS estimation."""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np

# ---------------------------------------------------------------------------
# Layout: two rows of boxes connected by arrows
#   Row 1 (top):    Camera → Undistort → Resize → YOLOv8n → NMS
#   Row 2 (bottom): Rescale ← GSD ← Attitude ← GPS Est
#   A curved arrow connects row 1 end to row 2 start
# ---------------------------------------------------------------------------

fig, ax = plt.subplots(1, 1, figsize=(14, 5.0))
ax.set_xlim(-0.3, 14.3)
ax.set_ylim(-3.6, 2.6)
ax.set_aspect('equal')
ax.axis('off')

# -- Colour palette (blue → purple → green gradient) -----------------------
COLORS = {
    'capture':   ('#dbeafe', '#3b82f6'),   # light blue / blue border
    'preproc':   ('#e0d4f5', '#7c3aed'),   # light purple / purple border
    'ai':        ('#ede0f7', '#9333ea'),   # lavender / deep purple border
    'nms':       ('#ede0f7', '#9333ea'),
    'rescale':   ('#d1fae5', '#059669'),   # light green / green border
    'geo':       ('#d1fae5', '#059669'),
    'output':    ('#bbf7d0', '#16a34a'),   # brighter green / darker green
}

ARROW_COL = '#64748b'
TEXT_DARK  = '#1e293b'
TIMING_COL = '#64748b'
ACCENT     = '#dc2626'
NOTE_COL   = '#6b7280'

# -- Stage definitions ------------------------------------------------------
# (label, subtitle, timing, color_key)
row1 = [
    ('Camera\nCapture',      '1456x1088 BGR\nIMX296 global shutter', '',          'capture'),
    ('Lens\nUndistortion',   'cv2.remap\npre-computed maps',         '~1.5 ms',  'preproc'),
    ('Resize\n640x640',      'Letterbox\naspect-preserving',         '~0.3 ms',  'preproc'),
    ('YOLOv8n\nInference',   'TFLite / NCNN\nbackend',              '206 / 72 ms', 'ai'),
    ('NMS +\nThreshold',     'conf > 0.4\ntop-k filtering',         '~0.2 ms',  'nms'),
]

row2 = [
    ('Rescale to\nOriginal',    '640 -> 1456x1088\npixel coords',       '~0.1 ms',  'rescale'),
    ('GSD\nCalculation',        'px -> metres\nalt + FOV',              '',          'geo'),
    ('Attitude\nCompensation',  r'$R = R_z R_y R_x$' + '\nray-trace',  '',          'geo'),
    ('GPS\nEstimation',         'drone GPS + offset\n-> target GPS',    '',          'output'),
]

bw, bh = 2.2, 1.15          # box width, height
x_spacing = 2.7             # centre-to-centre
y_row1 = 1.0
y_row2 = -1.8

# -- Helper: draw one row of boxes -----------------------------------------
def draw_row(stages, y_centre, x_start, direction=1):
    """Draw boxes and return list of (cx, cy) centres."""
    centres = []
    for i, (label, subtitle, timing, ckey) in enumerate(stages):
        cx = x_start + i * x_spacing * direction
        cy = y_centre
        fill, border = COLORS[ckey]
        box = FancyBboxPatch((cx - bw/2, cy - bh/2), bw, bh,
                             boxstyle="round,pad=0.14", linewidth=1.8,
                             edgecolor=border, facecolor=fill, zorder=3)
        ax.add_patch(box)
        # Stage name
        ax.text(cx, cy + 0.18, label, ha='center', va='center', fontsize=9,
                fontweight='bold', color=TEXT_DARK, zorder=4)
        # Subtitle (smaller, below name)
        ax.text(cx, cy - 0.35, subtitle, ha='center', va='center', fontsize=6.5,
                color=NOTE_COL, zorder=4, linespacing=1.2)
        # Timing below box
        if timing:
            ax.text(cx, cy - bh/2 - 0.22, timing, ha='center', va='top', fontsize=7.5,
                    color=TIMING_COL, fontstyle='italic', zorder=4)
        centres.append((cx, cy))
    return centres

# -- Draw rows --------------------------------------------------------------
x_start_r1 = 1.3
x_start_r2 = x_start_r1 + (len(row1) - 1) * x_spacing  # start from right

c1 = draw_row(row1, y_row1, x_start_r1, direction=1)
c2 = draw_row(row2, y_row2, x_start_r2, direction=-1)

# -- Arrows within rows -----------------------------------------------------
def row_arrows(centres, direction=1):
    for i in range(len(centres) - 1):
        x1 = centres[i][0] + bw/2 * direction
        x2 = centres[i+1][0] - bw/2 * direction
        cy = centres[i][1]
        ax.annotate('', xy=(x2, cy), xytext=(x1, cy),
                    arrowprops=dict(arrowstyle='->', color=ARROW_COL, lw=1.6),
                    zorder=2)

row_arrows(c1, direction=1)
row_arrows(c2, direction=-1)

# -- Curved arrow connecting row 1 end to row 2 start ----------------------
# From bottom of last row1 box to top of first row2 box (rightmost)
r1_last = c1[-1]
r2_first = c2[0]

ax.annotate('',
            xy=(r2_first[0] + bw/2 + 0.1, r2_first[1] + bh/2 * 0.3),
            xytext=(r1_last[0] + bw/2 + 0.1, r1_last[1] - bh/2 * 0.3),
            arrowprops=dict(arrowstyle='->', color=ARROW_COL, lw=1.6,
                            connectionstyle='arc3,rad=0.35'),
            zorder=2)

# -- Title ------------------------------------------------------------------
ax.text(7.0, 2.35, 'Vision System Pipeline: Camera Capture to Target GPS',
        ha='center', va='center', fontsize=13, fontweight='bold', color=TEXT_DARK)

# -- Key metrics annotation bar at bottom -----------------------------------
metrics = [
    ('TFLite: 206 ms / 4.8 FPS', ACCENT),
    ('NCNN: 72 ms / 13.9 FPS', '#059669'),
    ('GPS accuracy: ~0.3 m CEP', '#7c3aed'),
]
x_met = 2.5
for txt, col in metrics:
    ax.text(x_met, -3.25, txt, ha='center', va='center', fontsize=8.5,
            fontweight='bold', color=col,
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                      edgecolor=col, linewidth=1.0, alpha=0.9))
    x_met += 4.2

# -- Row labels (left side) ------------------------------------------------
ax.text(-0.1, y_row1, 'Detection', ha='right', va='center', fontsize=8,
        color=TIMING_COL, fontstyle='italic', rotation=90)
ax.text(-0.1, y_row2, 'Localisation', ha='right', va='center', fontsize=8,
        color=TIMING_COL, fontstyle='italic', rotation=90)

# -- Save -------------------------------------------------------------------
plt.tight_layout()
out_base = 'c:/Users/Bristol/Desktop/AI for Robotics/v3/report/figs/vision_pipeline'
plt.savefig(out_base + '.pdf', bbox_inches='tight', dpi=300)
plt.savefig(out_base + '.png', bbox_inches='tight', dpi=300)
print(f"OK: vision_pipeline.pdf + .png")
