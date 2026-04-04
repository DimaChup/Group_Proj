"""System Architecture Block Diagram — SAR Drone.

Professional hierarchical layout with colour-coded blocks, data-flow arrows,
and interface labels.  Raspberry Pi 5 as central hub.

Colours: blue = compute, green = sensors, orange = communication, grey = ground/actuators.
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch

# ── figure ────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(14, 10.5))
ax.set_xlim(-0.5, 13.5)
ax.set_ylim(-1.0, 11)
ax.set_aspect("equal")
ax.axis("off")

# ── palette ───────────────────────────────────────────────────────────
COMPUTE_BG = "#dbeafe";  COMPUTE_EC = "#2563eb"
SENSOR_BG  = "#d1fae5";  SENSOR_EC  = "#059669"
COMMS_BG   = "#ffedd5";  COMMS_EC   = "#ea580c"
GROUND_BG  = "#f3f4f6";  GROUND_EC  = "#6b7280"
SW_BG      = "#ede9fe";  SW_EC      = "#7c3aed"
TEXT       = "#1e293b"
ARROW      = "#475569"

# ── helpers ───────────────────────────────────────────────────────────
def block(cx, cy, w, h, lines, bg, ec, fs=9, bold=True):
    b = FancyBboxPatch((cx - w/2, cy - h/2), w, h,
                       boxstyle="round,pad=0.12", lw=1.8,
                       edgecolor=ec, facecolor=bg, zorder=3)
    ax.add_patch(b)
    ax.text(cx, cy, "\n".join(lines), ha="center", va="center",
            fontsize=fs, fontweight="bold" if bold else "normal",
            color=TEXT, zorder=4, linespacing=1.35)

def arr(x1, y1, x2, y2, label="", color=ARROW, lw=1.4, rad=0,
        fs=7.5, loff=(0, 0.18), bidir=False):
    conn = f"arc3,rad={rad}"
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw,
                                connectionstyle=conn, mutation_scale=12),
                zorder=2)
    if bidir:
        ax.annotate("", xy=(x1, y1), xytext=(x2, y2),
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=lw*0.7,
                                   connectionstyle=conn, mutation_scale=10),
                    zorder=2)
    if label:
        mx = (x1+x2)/2 + loff[0];  my = (y1+y2)/2 + loff[1]
        ax.text(mx, my, label, ha="center", va="center", fontsize=fs,
                color=color, fontstyle="italic", zorder=6,
                bbox=dict(boxstyle="round,pad=0.1", fc="white",
                          ec="none", alpha=0.95))

# ═══════════════════════════════════════════════════════════════════════
#  LAYOUT — top to bottom
#  Row 5  y~10.0   Ground Segment label
#  Row 4  y~9.2    RC Tx / Ground Station
#  ----   y~8.4    airborne envelope top
#  Row 3  y~7.3    MAVProxy bridge
#  Row 2  y~6.0    Cube  |  Raspberry Pi
#  Row 1  y~4.3    Software modules on Pi
#  Row 0  y~2.8    Sensors / AI model
#  Row -1 y~1.3    Actuators
#  ----   y~0.6    airborne envelope bottom
# ═══════════════════════════════════════════════════════════════════════

# ── Ground Segment ───────────────────────────────────────────────────
ax.text(6.25, 10.3, "Ground Segment", ha="center", va="center",
        fontsize=11, fontweight="bold", color="#64748b", fontstyle="italic")

block(2.8, 9.5, 2.6, 0.8,
      ["RC Transmitter", "(Pilot Override / Kill)"], GROUND_BG, GROUND_EC, fs=8.5)
block(9.8, 9.5, 2.8, 0.8,
      ["Ground Station", "(Laptop Browser)"], GROUND_BG, GROUND_EC, fs=8.5)

# ── Airborne envelope ────────────────────────────────────────────────
env = FancyBboxPatch((0.3, 0.4), 12.7, 8.0, boxstyle="round,pad=0.18",
                      lw=2.2, ec="#334155", fc="#f8fafc", ls="--", zorder=1)
ax.add_patch(env)
ax.text(6.4, 8.1, "Airborne Platform (Quadcopter)", ha="center",
        va="center", fontsize=11.5, fontweight="bold", color=TEXT, zorder=5)

# ── Cube Orange+ ─────────────────────────────────────────────────────
cube_cx, cube_cy = 2.8, 6.0
block(cube_cx, cube_cy, 2.8, 1.2,
      ["Cube Orange+", "ArduCopter 4.x"], COMPUTE_BG, COMPUTE_EC, fs=10)

# ── MAVProxy ─────────────────────────────────────────────────────────
mavp_cx, mavp_cy = 5.8, 7.2
block(mavp_cx, mavp_cy, 1.7, 0.55,
      ["MAVProxy"], COMMS_BG, COMMS_EC, fs=8)

# ── Raspberry Pi 5 ───────────────────────────────────────────────────
pi_cx, pi_cy = 9.3, 6.0
pi_w, pi_h = 4.8, 1.2
pi_box = FancyBboxPatch((pi_cx - pi_w/2, pi_cy - pi_h/2), pi_w, pi_h,
                         boxstyle="round,pad=0.14", lw=2.4,
                         ec=COMPUTE_EC, fc=COMPUTE_BG, zorder=3)
ax.add_patch(pi_box)
ax.text(pi_cx, pi_cy + 0.25, "Raspberry Pi 5", ha="center", va="center",
        fontsize=11, fontweight="bold", color=TEXT, zorder=4)
ax.text(pi_cx, pi_cy - 0.22, "Companion Computer  \u00b7  Python 3.13",
        ha="center", va="center", fontsize=7.5, color="#475569", zorder=4)

# ── Software modules row ─────────────────────────────────────────────
sw_y = 4.3
sw_h = 0.7
mods = [
    (7.3,  "State\nMachine"),
    (8.65, "Vision\nPipeline"),
    (10.0, "Web\nDashboard"),
    (11.35,"MAVLink\nClient"),
]
# background band for SW modules
sw_band = FancyBboxPatch((6.55, sw_y - sw_h/2 - 0.15), 5.55, sw_h + 0.3,
                          boxstyle="round,pad=0.08", lw=1.0,
                          ec=SW_EC, fc="#f5f3ff", ls=":", zorder=2, alpha=0.5)
ax.add_patch(sw_band)
ax.text(6.7, sw_y + sw_h/2 + 0.25, "Python Software Stack",
        ha="left", va="bottom", fontsize=7, color=SW_EC,
        fontstyle="italic", zorder=5)
for mx, txt in mods:
    block(mx, sw_y, 1.15, sw_h, [txt], SW_BG, SW_EC, fs=7)

# ── YOLOv8n (under Vision) ───────────────────────────────────────────
block(8.65, 2.9, 1.4, 0.6,
      ["YOLOv8n AI", "TFLite / NCNN"], COMPUTE_BG, COMPUTE_EC, fs=7.5)

# ── Sensors ───────────────────────────────────────────────────────────
block(10.8, 2.9, 1.6, 0.6,
      ["IMX296 Camera", "1456\u00d71088 GS"], SENSOR_BG, SENSOR_EC, fs=7.5)

block(1.0, 4.6, 1.3, 0.55,
      ["GPS Module", "(u-blox)"], SENSOR_BG, SENSOR_EC, fs=7.5)

block(1.0, 3.7, 1.3, 0.55,
      ["IMU / Baro", "(EKF)"], SENSOR_BG, SENSOR_EC, fs=7.5)

block(4.5, 3.7, 1.3, 0.55,
      ["RC Receiver", "(SBUS)"], SENSOR_BG, SENSOR_EC, fs=7.5)

# ── Actuators ─────────────────────────────────────────────────────────
block(2.0, 1.5, 2.0, 0.7,
      ["Motors / ESCs", "(\u00d74)"], GROUND_BG, GROUND_EC, fs=8.5)

block(4.8, 1.5, 1.4, 0.6,
      ["Buzzer"], GROUND_BG, GROUND_EC, fs=8.5)

# ═══════════════════════════════════════════════════════════════════════
#  ARROWS
# ═══════════════════════════════════════════════════════════════════════

# --- Ground → Airborne ---
# RC Tx → RC Receiver (433 MHz)
arr(2.8, 9.5 - 0.4, 4.5, 3.7 + 0.28,
    label="433 MHz", color="#7c3aed", lw=1.3, loff=(0.9, 0.2))

# Ground Station ↔ Pi (WiFi)
arr(9.8, 9.5 - 0.4, 9.8, pi_cy + pi_h/2 + 0.05,
    label="WiFi / HTTP\nMJPEG :8090", color=COMMS_EC, bidir=True,
    loff=(1.3, 0))

# --- Cube ↔ MAVProxy ↔ Pi ---
arr(cube_cx + 1.4, 6.4, mavp_cx - 0.85, mavp_cy,
    label="Serial\n921600 baud", color=COMMS_EC, bidir=True,
    loff=(0, 0.35))

arr(mavp_cx + 0.85, mavp_cy, pi_cx - pi_w/2 + 0.1, 6.4,
    label="UDP :14550", color=COMMS_EC, bidir=True,
    loff=(0, 0.35))

# --- Sensors → Cube ---
# GPS → Cube
arr(1.0 + 0.65, 4.6, cube_cx - 1.4, 5.4,
    label="UART", color=SENSOR_EC, loff=(0.0, 0.2))

# IMU → Cube
arr(1.0 + 0.65, 3.7, cube_cx - 1.4, 5.4,
    label="SPI", color=SENSOR_EC, loff=(-0.5, 0.3))

# RC Rx → Cube
arr(4.5 - 0.3, 3.7 + 0.28, cube_cx + 0.5, 5.4,
    label="SBUS", color=SENSOR_EC, loff=(-0.5, 0.18))

# --- Cube → Actuators ---
# Cube → Motors
arr(cube_cx - 0.3, 5.4, 2.0, 1.5 + 0.35,
    label="PWM", color=GROUND_EC, loff=(-0.6, 0))

# Cube → Buzzer
arr(cube_cx + 1.0, 5.4, 4.8, 1.5 + 0.3,
    label="MAVLink", color=GROUND_EC, loff=(0.5, 0.2))

# --- Pi internals ---
# Pi → SW modules (vertical connectors)
for mx in [7.2, 8.5, 9.8, 11.1]:
    arr(mx, pi_cy - pi_h/2, mx, sw_y + sw_h/2,
        color=COMPUTE_EC, lw=0.7)

# Vision → YOLOv8n
arr(8.5, sw_y - sw_h/2, 8.5, 2.9 + 0.3,
    label="Inference\n~70 ms (NCNN)", color=COMPUTE_EC, loff=(-0.95, 0), lw=1.1)

# Camera → Pi
arr(10.5, 2.9 + 0.3, 10.5, pi_cy - pi_h/2 - 0.05,
    label="CSI-2", color=SENSOR_EC, loff=(0.55, 0))

# ═══════════════════════════════════════════════════════════════════════
#  LEGEND
# ═══════════════════════════════════════════════════════════════════════
legend_patches = [
    mpatches.Patch(fc=COMPUTE_BG, ec=COMPUTE_EC, lw=1.5, label="Compute"),
    mpatches.Patch(fc=SENSOR_BG, ec=SENSOR_EC, lw=1.5, label="Sensors"),
    mpatches.Patch(fc=COMMS_BG, ec=COMMS_EC, lw=1.5, label="Communication"),
    mpatches.Patch(fc=SW_BG, ec=SW_EC, lw=1.5, label="Software (Pi)"),
    mpatches.Patch(fc=GROUND_BG, ec=GROUND_EC, lw=1.5, label="Ground / Actuators"),
]
ax.legend(handles=legend_patches, loc="lower left", fontsize=8,
          frameon=True, fancybox=True, framealpha=0.95,
          edgecolor="#d1d5db", ncol=3, columnspacing=1.2)

# ── save ──────────────────────────────────────────────────────────────
out = "c:/Users/Bristol/Desktop/AI for Robotics/v3/report/figs/system_architecture"
plt.tight_layout()
plt.savefig(out + ".pdf", bbox_inches="tight", dpi=300)
plt.savefig(out + ".png", bbox_inches="tight", dpi=300)
print(f"OK: {out}.pdf  and  {out}.png")
