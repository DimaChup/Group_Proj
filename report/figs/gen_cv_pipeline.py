"""Chart 7: CV Detection Pipeline Flow."""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch

fig, ax = plt.subplots(1, 1, figsize=(12, 2.8))
ax.set_xlim(-0.5, 12.5)
ax.set_ylim(-0.8, 2.2)
ax.set_aspect('equal')
ax.axis('off')

# Colors
LIGHT_BLUE = '#d6eaf8'
BORDER_BLUE = '#2980b9'
ARROW_COL = '#555555'
TEXT_DARK = '#2c3e50'
TIMING_COL = '#7f8c8d'
ACCENT = '#e67e22'

steps = [
    ('Camera\nFrame', '1456x1088', 0.8),
    ('Lens\nUndistort', '1.5 ms', 2.8),
    ('Resize to\n640x640', '0.3 ms', 4.8),
    ('YOLOv8n\nTFLite', '196 ms', 6.8),
    ('NMS\nFilter', 'conf > 0.2', 8.8),
    ('Detection\n(x, y, conf)', 'Output', 10.8),
]

bw, bh = 1.55, 1.0

for label, timing, cx in steps:
    cy = 0.7
    color = LIGHT_BLUE if label != 'Detection\n(x, y, conf)' else '#d5f5e3'
    border = BORDER_BLUE if label != 'Detection\n(x, y, conf)' else '#27ae60'
    box = FancyBboxPatch((cx - bw/2, cy - bh/2), bw, bh,
                         boxstyle="round,pad=0.12", linewidth=1.5,
                         edgecolor=border, facecolor=color, zorder=3)
    ax.add_patch(box)
    ax.text(cx, cy + 0.05, label, ha='center', va='center', fontsize=9,
            fontweight='bold', color=TEXT_DARK, zorder=4)
    ax.text(cx, cy - bh/2 - 0.2, timing, ha='center', va='center', fontsize=8,
            color=TIMING_COL, fontstyle='italic', zorder=4)

# Arrows between steps
for i in range(len(steps) - 1):
    x1 = steps[i][2] + bw/2
    x2 = steps[i+1][2] - bw/2
    cy = 0.7
    ax.annotate('', xy=(x2, cy), xytext=(x1, cy),
                arrowprops=dict(arrowstyle='->', color=ARROW_COL, lw=1.5), zorder=2)

# Title
ax.text(6.0, 1.85, 'Computer Vision Detection Pipeline', ha='center', va='center',
        fontsize=12, fontweight='bold', color=TEXT_DARK)

# Total time annotation
ax.annotate('Total: ~198 ms per frame (5.1 FPS)', xy=(6.0, -0.55),
            ha='center', va='center', fontsize=9, color=ACCENT, fontweight='bold')

plt.tight_layout()
plt.savefig('c:/Users/Bristol/Desktop/AI for Robotics/v3/report/figs/cv_pipeline.pdf',
            bbox_inches='tight', dpi=300)
plt.savefig('c:/Users/Bristol/Desktop/AI for Robotics/v3/report/figs/cv_pipeline.png',
            bbox_inches='tight', dpi=300)
print("OK: cv_pipeline.pdf")
