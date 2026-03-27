"""Simplified System Overview — 1-line block diagram."""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch

# --- Styling ---
TEXT_DARK = '#2c3e50'
BLUE = '#2980b9'
ORANGE = '#e67e22'
GREEN = '#27ae60'
GREY = '#7f8c8d'
LIGHT_BLUE = '#d6eaf8'
LIGHT_ORANGE = '#fdebd0'
LIGHT_GREEN = '#d5f5e3'
LIGHT_GREY = '#f2f3f4'

plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 10,
    'text.color': TEXT_DARK,
})

fig, ax = plt.subplots(figsize=(10, 4))
ax.set_xlim(-0.5, 10.5)
ax.set_ylim(-1.5, 3.5)
ax.set_aspect('equal')
ax.axis('off')

# --- Box definitions ---
box_h = 0.9
box_w = 1.6

def draw_box(x, y, w, h, label, sublabel, facecolor, edgecolor, fontsize=11):
    rect = mpatches.FancyBboxPatch(
        (x - w/2, y - h/2), w, h,
        boxstyle="round,pad=0.12",
        facecolor=facecolor, edgecolor=edgecolor, linewidth=1.8
    )
    ax.add_patch(rect)
    ax.text(x, y + 0.08, label, ha='center', va='center',
            fontsize=fontsize, fontweight='bold', color=TEXT_DARK)
    if sublabel:
        ax.text(x, y - 0.25, sublabel, ha='center', va='center',
                fontsize=7, color=GREY, style='italic')

def draw_arrow(x1, y1, x2, y2, label=None, color=TEXT_DARK, style='->', lw=1.5):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle=style, color=color, lw=lw))
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mx, my + 0.2, label, ha='center', va='center',
                fontsize=8, color=color, style='italic')

# --- Main data flow (middle row, y=1.5) ---
# Camera -> Pi 5 -> Cube -> Motors
cam_x, pi_x, cube_x, motor_x = 1.5, 4.0, 6.5, 9.0
main_y = 1.5

draw_box(cam_x, main_y, box_w, box_h, 'Camera', 'IMX296 global', LIGHT_BLUE, BLUE)
draw_box(pi_x, main_y, box_w, box_h, 'Pi 5', 'YOLOv8n TFLite', LIGHT_ORANGE, ORANGE)
draw_box(cube_x, main_y, box_w, box_h, 'Cube', 'ArduPilot', LIGHT_GREEN, GREEN)
draw_box(motor_x, main_y, box_w, box_h, 'Motors', '4x ESC', LIGHT_GREY, GREY)

# Main flow arrows
draw_arrow(cam_x + box_w/2 + 0.05, main_y, pi_x - box_w/2 - 0.05, main_y,
           'frames', BLUE)
draw_arrow(pi_x + box_w/2 + 0.05, main_y, cube_x - box_w/2 - 0.05, main_y,
           'MAVLink', ORANGE)
draw_arrow(cube_x + box_w/2 + 0.05, main_y, motor_x - box_w/2 - 0.05, main_y,
           'PWM', GREEN)

# --- Below: Browser <- WiFi <- Pi 5 ---
browser_x = 1.5
browser_y = -0.2

draw_box(browser_x, browser_y, box_w, box_h, 'Browser', 'ground station', LIGHT_BLUE, BLUE)

draw_arrow(pi_x, main_y - box_h/2 - 0.05, pi_x, browser_y + box_h/2 + 0.35,
           '', BLUE, lw=1.2)
draw_arrow(pi_x, browser_y + box_h/2 + 0.3, browser_x + box_w/2 + 0.05, browser_y,
           'WiFi / MJPEG', BLUE, lw=1.2)

# --- Above: RC -> Cube ---
rc_x = 6.5
rc_y = 3.0

draw_box(rc_x, rc_y, box_w * 0.9, box_h * 0.85, 'RC Tx', 'kill switch', LIGHT_GREY, GREY, fontsize=10)

draw_arrow(rc_x, rc_y - box_h * 0.85/2 - 0.05, cube_x, main_y + box_h/2 + 0.05,
           'SBUS', GREY, lw=1.2)

# --- GPS above Cube ---
gps_x = 8.5
gps_y = 3.0
draw_box(gps_x, gps_y, box_w * 0.8, box_h * 0.75, 'GPS', 'u-blox M9N', LIGHT_GREEN, GREEN, fontsize=10)
draw_arrow(gps_x, gps_y - box_h * 0.75/2 - 0.05, cube_x + 0.3, main_y + box_h/2 + 0.05,
           '', GREEN, lw=1.2)

ax.set_title('System Overview', fontsize=14, fontweight='bold',
             color=TEXT_DARK, pad=20)

plt.tight_layout()
plt.savefig('system_overview_simple.pdf', bbox_inches='tight', dpi=300)
plt.savefig('system_overview_simple.png', bbox_inches='tight', dpi=300)
print("Saved system_overview_simple.pdf + .png")
