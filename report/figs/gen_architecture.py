"""Chart 8: System Architecture Block Diagram."""
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.patches as mpatches

fig, ax = plt.subplots(1, 1, figsize=(11, 8))
ax.set_xlim(-0.5, 11)
ax.set_ylim(-0.5, 9.5)
ax.set_aspect('equal')
ax.axis('off')

# Colors
HW_BLUE = '#d6eaf8'
HW_BORDER = '#2980b9'
SW_GREEN = '#d5f5e3'
SW_BORDER = '#27ae60'
EXT_GREY = '#f2f3f4'
EXT_BORDER = '#7f8c8d'
ORANGE_BG = '#fdebd0'
ORANGE_BORDER = '#e67e22'
TEXT_DARK = '#2c3e50'
ARROW_COL = '#555555'

def box(ax, cx, cy, w, h, text, facecolor, edgecolor, fontsize=9, bold=True):
    b = FancyBboxPatch((cx - w/2, cy - h/2), w, h,
                       boxstyle="round,pad=0.1", linewidth=1.5,
                       edgecolor=edgecolor, facecolor=facecolor, zorder=3)
    ax.add_patch(b)
    fw = 'bold' if bold else 'normal'
    ax.text(cx, cy, text, ha='center', va='center', fontsize=fontsize,
            fontweight=fw, color=TEXT_DARK, zorder=4)

def arrow(ax, x1, y1, x2, y2, label='', color=ARROW_COL, lw=1.3, rad=0, fontsize=7.5, loff=(0, 0.15)):
    conn = f'arc3,rad={rad}' if rad else 'arc3,rad=0'
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color=color, lw=lw, connectionstyle=conn), zorder=2)
    if label:
        mx = (x1 + x2)/2 + loff[0]
        my = (y1 + y2)/2 + loff[1]
        ax.text(mx, my, label, ha='center', va='center', fontsize=fontsize,
                color=color, fontstyle='italic', zorder=5,
                bbox=dict(boxstyle='round,pad=0.08', facecolor='white', edgecolor='none', alpha=0.9))

def section_label(ax, cx, cy, text):
    ax.text(cx, cy, text, ha='center', va='center', fontsize=10,
            fontweight='bold', color='#7f8c8d', fontstyle='italic', zorder=5)

# === GROUND SEGMENT (top) ===
section_label(ax, 5.25, 9.0, 'Ground Segment')
box(ax, 2.5, 8.3, 2.8, 0.7, 'RC Transmitter\n(FrSky X9D)', EXT_GREY, EXT_BORDER)
box(ax, 8.0, 8.3, 2.8, 0.7, 'Ground Station\n(Browser UI)', EXT_GREY, EXT_BORDER)

# === AIRBORNE HARDWARE (middle) ===
# Big group box for drone
drone_box = FancyBboxPatch((0.3, 2.0), 10.2, 4.6, boxstyle="round,pad=0.15",
                            linewidth=2, edgecolor='#2c3e50', facecolor='#fafafa',
                            linestyle='--', zorder=1)
ax.add_patch(drone_box)
ax.text(5.4, 6.35, 'Airborne Platform', ha='center', va='center', fontsize=10,
        fontweight='bold', color=TEXT_DARK, zorder=5)

# Flight controller
box(ax, 2.5, 4.8, 2.5, 0.8, 'Cube Orange+\n(ArduPilot)', HW_BLUE, HW_BORDER, fontsize=9)

# Raspberry Pi
box(ax, 7.5, 4.8, 2.5, 0.8, 'Raspberry Pi 5\n(Companion)', HW_BLUE, HW_BORDER, fontsize=9)

# Camera
box(ax, 7.5, 3.1, 2.2, 0.65, 'IMX296\nGlobal Shutter', HW_BLUE, HW_BORDER, fontsize=8)

# Motors
box(ax, 2.5, 3.1, 2.2, 0.65, 'Motors / ESCs\n(x4)', HW_BLUE, HW_BORDER, fontsize=8)

# GPS
box(ax, 0.8, 3.8, 1.1, 0.5, 'GPS', HW_BLUE, HW_BORDER, fontsize=8)

# Buzzer
box(ax, 7.5, 2.15, 1.4, 0.45, 'Buzzer', HW_BLUE, HW_BORDER, fontsize=8)

# === SOFTWARE ON PI ===
sw_box = FancyBboxPatch((5.5, 5.85), 4.5, 0.55, boxstyle="round,pad=0.08",
                         linewidth=1, edgecolor=SW_BORDER, facecolor=SW_GREEN, zorder=2)
ax.add_patch(sw_box)
ax.text(7.75, 6.12, 'main.py  |  vision.py  |  planning.py  |  utils.py', ha='center', va='center',
        fontsize=7.5, fontweight='bold', color=TEXT_DARK, zorder=4, family='monospace')

# === ARROWS ===
# RC -> Cube (433 MHz)
arrow(ax, 2.5, 8.3 - 0.35, 2.5, 4.8 + 0.4, label='433 MHz\nRC link', color='#8e44ad', loff=(0.9, 0))

# Cube <-> Pi (UART / MAVProxy)
arrow(ax, 2.5 + 2.5/2, 4.8, 7.5 - 2.5/2, 4.8, label='UART / MAVProxy\n(MAVLink)', color=HW_BORDER)
# Bidirectional: add reverse arrow slightly offset
arrow(ax, 7.5 - 2.5/2, 4.65, 2.5 + 2.5/2, 4.65, color=HW_BORDER, lw=0.8)

# Pi <-> Camera (CSI)
arrow(ax, 7.5, 4.8 - 0.4, 7.5, 3.1 + 0.32, label='CSI-2', color=HW_BORDER, loff=(-0.55, 0))

# Cube -> Motors (PWM)
arrow(ax, 2.5, 4.8 - 0.4, 2.5, 3.1 + 0.32, label='PWM', color=HW_BORDER, loff=(-0.55, 0))

# GPS -> Cube
arrow(ax, 0.8 + 1.1/2, 3.8, 2.5 - 2.5/2, 4.5, label='UART', color=HW_BORDER, loff=(0, 0.15))

# Ground Station <-> Pi (WiFi)
arrow(ax, 8.0, 8.3 - 0.35, 7.5, 5.2 + 0.18, label='WiFi\n(MJPEG + HTTP)', color='#e67e22', loff=(0.9, 0))

# Pi -> Buzzer
arrow(ax, 7.5, 4.8 - 0.4, 7.5, 2.15 + 0.22, color=HW_BORDER, lw=0.8)

# Legend
legend_items = [
    mpatches.Patch(facecolor=HW_BLUE, edgecolor=HW_BORDER, label='Hardware'),
    mpatches.Patch(facecolor=SW_GREEN, edgecolor=SW_BORDER, label='Software (Pi)'),
    mpatches.Patch(facecolor=EXT_GREY, edgecolor=EXT_BORDER, label='Ground equipment'),
]
ax.legend(handles=legend_items, loc='lower right', fontsize=8, frameon=True,
          fancybox=True, framealpha=0.9, edgecolor='#cccccc')

plt.tight_layout()
plt.savefig('c:/Users/Bristol/Desktop/AI for Robotics/v3/report/figs/architecture.pdf',
            bbox_inches='tight', dpi=300)
plt.savefig('c:/Users/Bristol/Desktop/AI for Robotics/v3/report/figs/architecture.png',
            bbox_inches='tight', dpi=300)
print("OK: architecture.pdf")
