"""Pi-Side System Architecture Diagram.

Shows everything running on the Raspberry Pi 5 and connections to external systems.
Matches the visual style of gen_architecture.py for report consistency.
"""
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import matplotlib.patches as mpatches

fig, ax = plt.subplots(1, 1, figsize=(14, 9.5))
ax.set_xlim(-1.0, 14.0)
ax.set_ylim(-1.5, 10.0)
ax.set_aspect('equal')
ax.axis('off')

# ── Colour palette ──────────────────────────────────────────────
SW_BLUE     = '#d6eaf8'
SW_BORDER   = '#2980b9'
HW_GREEN    = '#d5f5e3'
HW_BORDER   = '#27ae60'
EXT_GREY    = '#f2f3f4'
EXT_BORDER  = '#7f8c8d'
COMM_ORANGE = '#e67e22'
RC_PURPLE   = '#8e44ad'
TEXT_DARK   = '#2c3e50'
PI_BG       = '#fafafa'
PI_BORDER   = '#2c3e50'
NOTE_BG     = '#fdebd0'

# ── Helper functions ────────────────────────────────────────────
def box(cx, cy, w, h, text, fc, ec, fontsize=9, bold=True):
    b = FancyBboxPatch((cx - w/2, cy - h/2), w, h,
                       boxstyle="round,pad=0.12", linewidth=1.5,
                       edgecolor=ec, facecolor=fc, zorder=3)
    ax.add_patch(b)
    ax.text(cx, cy, text, ha='center', va='center', fontsize=fontsize,
            fontweight='bold' if bold else 'normal', color=TEXT_DARK, zorder=4)

def arr(x1, y1, x2, y2, label='', color=COMM_ORANGE, lw=1.6,
        rad=0, fontsize=7, loff=(0, 0.2), style='->', label_bg='white'):
    conn = f'arc3,rad={rad}' if rad else 'arc3,rad=0'
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle=style, color=color, lw=lw,
                                connectionstyle=conn), zorder=2)
    if label:
        mx = (x1 + x2)/2 + loff[0]
        my = (y1 + y2)/2 + loff[1]
        ax.text(mx, my, label, ha='center', va='center', fontsize=fontsize,
                color=color, fontstyle='italic', zorder=5,
                bbox=dict(boxstyle='round,pad=0.1', facecolor=label_bg,
                          edgecolor='none', alpha=0.95))

def biarr(x1, y1, x2, y2, **kw):
    kw.setdefault('style', '<->')
    arr(x1, y1, x2, y2, **kw)

def note(cx, cy, text, fontsize=6.5):
    ax.text(cx, cy, text, ha='center', va='center', fontsize=fontsize,
            color=TEXT_DARK, fontstyle='italic', zorder=5,
            bbox=dict(boxstyle='round,pad=0.15', facecolor=NOTE_BG,
                      edgecolor=COMM_ORANGE, alpha=0.92, linewidth=0.8))

# ================================================================
#  RASPBERRY PI 5  (large rounded box)
# ================================================================
pi_x, pi_y, pi_w, pi_h = 3.0, 2.6, 8.0, 6.6
pi_box = FancyBboxPatch((pi_x, pi_y), pi_w, pi_h,
                         boxstyle="round,pad=0.25", linewidth=2.5,
                         edgecolor=PI_BORDER, facecolor=PI_BG, zorder=1)
ax.add_patch(pi_box)
ax.text(pi_x + pi_w/2, pi_y + pi_h - 0.28, 'Raspberry Pi 5',
        ha='center', va='center', fontsize=14, fontweight='bold',
        color=PI_BORDER, zorder=5)

# ── Software modules inside Pi ──────────────────────────────────

# Row 1 (top): vision + planning
vis_cx, vis_cy = 5.0, 7.6
box(vis_cx, vis_cy, 2.2, 0.75, 'vision.py\n(Camera + YOLOv8n)', SW_BLUE, SW_BORDER, fontsize=8)

plan_cx, plan_cy = 9.0, 7.6
box(plan_cx, plan_cy, 2.0, 0.75, 'planning.py\n(Lawnmower Gen)', SW_BLUE, SW_BORDER, fontsize=8)

# Row 2 (center): main.py — the orchestrator, biggest box
main_cx, main_cy = 7.0, 5.8
box(main_cx, main_cy, 2.8, 1.0, 'main.py\n(State Machine Orchestrator)', SW_BLUE, SW_BORDER, fontsize=9)

# Row 3 (bottom-ish): utils, geofence, config
util_cx, util_cy = 4.5, 4.2
box(util_cx, util_cy, 2.0, 0.7, 'utils.py\n(Pixel \u2192 GPS)', SW_BLUE, SW_BORDER, fontsize=8)

geo_cx, geo_cy = 9.4, 5.8
box(geo_cx, geo_cy, 1.6, 0.7, 'geofence.py\n(NFZ)', SW_BLUE, SW_BORDER, fontsize=8)

cfg_cx, cfg_cy = 9.4, 4.2
box(cfg_cx, cfg_cy, 1.5, 0.6, 'config.py', SW_BLUE, SW_BORDER, fontsize=7.5)

# Row 4 (bottom): stream server
stream_cx, stream_cy = 7.0, 3.3
box(stream_cx, stream_cy, 2.4, 0.65, 'Stream Server\n(MJPEG :8090)', SW_BLUE, SW_BORDER, fontsize=8)

# ── Internal arrows (blue, within Pi) ──────────────────────────

# vision -> main
arr(vis_cx + 0.6, vis_cy - 0.38, main_cx - 0.6, main_cy + 0.5,
    label='(found, x, y, conf)', color=SW_BORDER, fontsize=6.5,
    loff=(-0.6, 0.15), lw=1.3)

# planning -> main
arr(plan_cx - 0.5, plan_cy - 0.38, main_cx + 0.6, main_cy + 0.5,
    label='Waypoint list', color=SW_BORDER, fontsize=6.5,
    loff=(0.5, 0.15), lw=1.3)

# main <-> utils (two separate arrows, offset vertically to avoid overlap)
arr(main_cx - 1.2, main_cy - 0.25, util_cx + 0.7, util_cy + 0.38,
    label='Pixel coords', color=SW_BORDER, fontsize=6, loff=(-0.75, 0.2), lw=1.0)
arr(util_cx + 0.9, util_cy + 0.3, main_cx - 1.1, main_cy - 0.5,
    label='GPS estimate', color=SW_BORDER, fontsize=6, loff=(0.75, -0.2), lw=1.0)

# main -> geofence
biarr(main_cx + 1.4, main_cy, geo_cx - 0.8, geo_cy,
      label='Position\ncheck', color=SW_BORDER, fontsize=6, loff=(0, 0.32), lw=1.0)

# main -> stream_server
arr(main_cx, main_cy - 0.5, stream_cx, stream_cy + 0.32,
    label='Annotated\nframe', color=SW_BORDER, fontsize=6, loff=(0.65, 0), lw=1.0)

# ================================================================
#  EXTERNAL HARDWARE (outside Pi box)
# ================================================================

# IMX296 Camera — left, aligned with vision.py
cam_cx, cam_cy = 0.5, 7.6
box(cam_cx, cam_cy, 1.9, 0.85, 'IMX296\nGlobal Shutter', HW_GREEN, HW_BORDER, fontsize=9)

# MAVProxy — below Pi, center-left (runs on Pi but separate process)
mav_cx, mav_cy = 5.0, 0.8
box(mav_cx, mav_cy, 2.4, 0.8, 'MAVProxy\n(UDP/TCP Bridge)', HW_GREEN, HW_BORDER, fontsize=8.5)

# Cube Orange — far left bottom
cube_cx, cube_cy = 0.5, 0.8
box(cube_cx, cube_cy, 2.2, 0.85, 'Cube Orange+\n(ArduPilot)', HW_GREEN, HW_BORDER, fontsize=9)

# Mission Planner — bottom right
mp_cx, mp_cy = 9.5, 0.8
box(mp_cx, mp_cy, 2.4, 0.7, 'Mission Planner\n(Laptop)', EXT_GREY, EXT_BORDER, fontsize=8)

# Ground Station Browser — far right
gs_cx, gs_cy = 13.0, 3.3
box(gs_cx, gs_cy, 1.6, 0.85, 'Ground\nStation\n(Browser)', EXT_GREY, EXT_BORDER, fontsize=7.5)

# RC chain — far left, vertically stacked
rc_tx_cx, rc_tx_cy = -0.3, 4.5
box(rc_tx_cx, rc_tx_cy, 1.5, 0.7, 'RC\nTransmitter', EXT_GREY, EXT_BORDER, fontsize=7.5)

rc_rx_cx, rc_rx_cy = -0.3, 3.1
box(rc_rx_cx, rc_rx_cy, 1.5, 0.7, 'FrSky\nReceiver', EXT_GREY, EXT_BORDER, fontsize=7.5)

# ================================================================
#  EXTERNAL ARROWS (orange communication links)
# ================================================================

# Camera -> vision.py (CSI)
arr(cam_cx + 0.95, cam_cy, vis_cx - 1.1, vis_cy,
    label='CSI-2 ribbon cable\n1456\u00d71088 BGR frames', fontsize=7,
    loff=(0, 0.35), lw=2.0)

# Cube <-> MAVProxy (UART)
biarr(cube_cx + 1.1, cube_cy, mav_cx - 1.2, mav_cy,
      label='UART  921600 baud', fontsize=7, loff=(0, 0.35), lw=2.0)

# MAVProxy <-> main.py (UDP 14550)
biarr(mav_cx, mav_cy + 0.4, main_cx - 1.2, main_cy - 0.5,
      label='UDP :14550\n(MAVLink)', fontsize=7, loff=(-1.2, 0.1), lw=2.0)

# MAVProxy -> Mission Planner (TCP 5762)
arr(mav_cx + 1.2, mav_cy, mp_cx - 1.2, mp_cy,
    label='TCP :5762', fontsize=7, loff=(0, 0.3), lw=1.5)

# Stream server -> Ground Station (WiFi)
arr(stream_cx + 1.2, stream_cy, gs_cx - 0.8, gs_cy,
    label='WiFi HTTP\nMJPEG + detection overlay', fontsize=7,
    loff=(0.3, 0.35), lw=2.0)

# RC Transmitter -> Receiver (433 MHz)
arr(rc_tx_cx, rc_tx_cy - 0.35, rc_rx_cx, rc_rx_cy + 0.35,
    label='433 MHz', color=RC_PURPLE, fontsize=6.5, loff=(0.55, 0), lw=1.3)

# Receiver -> Cube (SBUS, route down and across)
arr(rc_rx_cx, rc_rx_cy - 0.35, cube_cx - 0.3, cube_cy + 0.42,
    label='SBUS', color=RC_PURPLE, fontsize=6.5, loff=(0.5, 0.0), lw=1.3,
    rad=-0.3)

# ── Data-flow annotation boxes ──────────────────────────────────

# Commands annotation (left of MAVLink link)
note(2.5, 2.2, 'Commands:\nGUIDED waypoints, arm,\ntakeoff, land, set mode')

# Telemetry annotation (right of MAVLink link)
note(9.5, 2.2, 'Telemetry:\nGPS, altitude, heading,\nbattery, flight mode')

# Thin lines connecting annotations to the MAVLink path
arr(2.5, 1.85, 4.0, 1.2, color='#bbb', lw=0.5, style='-')
arr(9.5, 1.85, 6.5, 1.3, color='#bbb', lw=0.5, style='-')

# ── Legend ───────────────────────────────────────────────────────
legend_items = [
    mpatches.Patch(facecolor=SW_BLUE,  edgecolor=SW_BORDER,
                   label='Software module (Pi)'),
    mpatches.Patch(facecolor=HW_GREEN, edgecolor=HW_BORDER,
                   label='Hardware / firmware'),
    mpatches.Patch(facecolor=EXT_GREY, edgecolor=EXT_BORDER,
                   label='External system'),
    mpatches.Patch(facecolor='white',  edgecolor=COMM_ORANGE,
                   label='Communication link', linewidth=1.5),
]
ax.legend(handles=legend_items, loc='upper right', fontsize=8.5, frameon=True,
          fancybox=True, framealpha=0.95, edgecolor='#cccccc',
          bbox_to_anchor=(1.0, 1.02))

plt.tight_layout()
out = 'c:/Users/Bristol/Desktop/AI for Robotics/v3/report/figs/pi_system'
plt.savefig(out + '.pdf', bbox_inches='tight', dpi=300)
plt.savefig(out + '.png', bbox_inches='tight', dpi=300)
print("OK: pi_system.pdf + pi_system.png")
