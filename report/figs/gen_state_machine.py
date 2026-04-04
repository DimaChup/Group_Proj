"""State Machine Diagram — SAR Drone Mission.

Generates a professional directed-graph figure showing all mission states
and transitions.  Pure matplotlib (no graphviz dependency).

States: INIT -> CONNECTING -> ARMING -> TAKEOFF -> TRANSIT_TO_SEARCH ->
        SEARCH -> CENTERING -> DESCENDING -> VERIFY -> APPROACH -> LANDING -> DONE
Plus:   MANUAL (override from any state), RETURN_TRANSIT (resume after reject)

Output: state_machine_generated.pdf / .png
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import os

# ── Palette ──────────────────────────────────────────────────────────────
C_GREEN      = "#27ae60"
C_GREEN_LT   = "#2ecc71"
C_BLUE       = "#2980b9"
C_BLUE_LT    = "#3498db"
C_ORANGE     = "#d35400"
C_ORANGE_LT  = "#e67e22"
C_RED        = "#c0392b"
C_RED_LT     = "#e74c3c"
C_PURPLE     = "#6c3483"
C_PURPLE_LT  = "#af7ac5"
C_GREY       = "#7f8c8d"
C_BG         = "#ffffff"
C_TEXT       = "#2c3e50"
C_ARROW      = "#4a4a4a"

# ── State definitions ────────────────────────────────────────────────────
CAT_COLORS = {
    "start":  (C_GREEN_LT,  C_GREEN),
    "flight": (C_BLUE_LT,   C_BLUE),
    "detect": (C_ORANGE_LT, C_ORANGE),
    "safety": (C_RED_LT,    C_RED),
    "end":    (C_GREEN_LT,  C_GREEN),
}

# (display_name, category, key)
STATES = [
    ("INIT",              "start",  "INIT"),
    ("CONNECTING",        "start",  "CONNECTING"),
    ("ARMING",            "start",  "ARMING"),
    ("TAKEOFF",           "flight", "TAKEOFF"),
    ("TRANSIT TO\nSEARCH","flight", "TRANSIT"),
    ("SEARCH",            "flight", "SEARCH"),
    ("CENTERING",         "detect", "CENTERING"),
    ("DESCENDING",        "detect", "DESCENDING"),
    ("VERIFY",            "detect", "VERIFY"),
    ("APPROACH",          "flight", "APPROACH"),
    ("LANDING",           "flight", "LANDING"),
    ("DONE",              "end",    "DONE"),
]

# ── Layout ───────────────────────────────────────────────────────────────
FIG_W, FIG_H = 9, 13.5
BOX_W, BOX_H = 2.0, 0.58
X_MAIN = 3.5
Y_TOP  = 12.2
DY     = 1.02

positions = {}
for i, (_, _, key) in enumerate(STATES):
    positions[key] = (X_MAIN, Y_TOP - i * DY)

# MANUAL to the right
positions["MANUAL"] = (X_MAIN + 4.0, Y_TOP - 5 * DY)
# RETURN_TRANSIT small annotation
positions["RETURN_TRANSIT"] = (X_MAIN + 4.0, Y_TOP - 8 * DY - 0.15)

# ── Drawing helpers ──────────────────────────────────────────────────────

def draw_state(ax, cx, cy, text, category, highlight=False):
    fill, edge = CAT_COLORS[category]
    lw = 2.4 if highlight else 1.5
    shadow = FancyBboxPatch(
        (cx - BOX_W / 2 + 0.04, cy - BOX_H / 2 - 0.04), BOX_W, BOX_H,
        boxstyle="round,pad=0.10", linewidth=0,
        edgecolor="none", facecolor="#00000015", zorder=2,
    )
    ax.add_patch(shadow)
    box = FancyBboxPatch(
        (cx - BOX_W / 2, cy - BOX_H / 2), BOX_W, BOX_H,
        boxstyle="round,pad=0.10", linewidth=lw,
        edgecolor=edge, facecolor=fill, zorder=3,
    )
    ax.add_patch(box)
    fs = 9.5 if "\n" not in text else 8
    ax.text(cx, cy, text, ha="center", va="center",
            fontsize=fs, fontweight="bold", color="white",
            family="sans-serif", zorder=4)


def arrow(ax, x1, y1, x2, y2, rad=0.0, color=C_ARROW,
          lw=1.3, style="->", ls="-"):
    ax.annotate(
        "", xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(
            arrowstyle=style, color=color, lw=lw,
            connectionstyle=f"arc3,rad={rad}",
            linestyle=ls, shrinkA=0, shrinkB=0,
        ),
        zorder=2,
    )


def label(ax, x, y, text, color=C_TEXT, fs=7.5, italic=True, bg="white", alpha=0.9):
    ax.text(x, y, text, ha="center", va="center", fontsize=fs,
            color=color, fontstyle="italic" if italic else "normal",
            family="sans-serif", zorder=6,
            bbox=dict(boxstyle="round,pad=0.10", facecolor=bg,
                      edgecolor="none", alpha=alpha))


# ── Create figure ────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(FIG_W, FIG_H), facecolor=C_BG)
ax.set_xlim(-0.3, FIG_W + 0.3)
ax.set_ylim(-0.6, FIG_H)
ax.set_aspect("equal")
ax.axis("off")
fig.patch.set_facecolor(C_BG)

# ── Draw all state boxes ─────────────────────────────────────────────────
for disp, cat, key in STATES:
    cx, cy = positions[key]
    draw_state(ax, cx, cy, disp, cat,
               highlight=(key in ("SEARCH", "VERIFY")))

# MANUAL box
mx, my = positions["MANUAL"]
draw_state(ax, mx, my, "MANUAL", "safety", highlight=True)

# ── Main-flow arrows ─────────────────────────────────────────────────────
main_transitions = [
    ("INIT",       "CONNECTING",  ""),
    ("CONNECTING", "ARMING",      "heartbeat"),
    ("ARMING",     "TAKEOFF",     "armed"),
    ("TAKEOFF",    "TRANSIT",     "alt reached"),
    ("TRANSIT",    "SEARCH",      "at search area"),
    ("SEARCH",     "CENTERING",   "target detected"),
    ("CENTERING",  "DESCENDING",  "centred"),
    ("DESCENDING", "VERIFY",      "at verify alt"),
    ("APPROACH",   "LANDING",     "near target"),
    ("LANDING",    "DONE",        "disarmed"),
]

for src, dst, lbl in main_transitions:
    sx, sy = positions[src]
    dx, dy = positions[dst]
    arrow(ax, sx, sy - BOX_H / 2, dx, dy + BOX_H / 2, color=C_ARROW)
    if lbl:
        label(ax, (sx + dx) / 2 + 1.20, (sy - BOX_H / 2 + dy + BOX_H / 2) / 2,
              lbl, color="#444444", fs=7.5)

# ── VERIFY -> APPROACH  (operator confirms) ──────────────────────────────
vx, vy = positions["VERIFY"]
apx, apy = positions["APPROACH"]
arrow(ax, vx, vy - BOX_H / 2, apx, apy + BOX_H / 2, color=C_GREEN)
label(ax, (vx + apx) / 2 + 1.20, (vy - BOX_H / 2 + apy + BOX_H / 2) / 2,
      "confirmed [Y]", color=C_GREEN, fs=7.5)

# ── VERIFY -> SEARCH  (rejected N) — route left ─────────────────────────
sx_s, sy_s = positions["SEARCH"]
left_x = X_MAIN - BOX_W / 2 - 0.7

arrow(ax, vx - BOX_W / 2, vy, left_x, vy, color=C_ORANGE, lw=1.4)
arrow(ax, left_x, vy, left_x, sy_s, color=C_ORANGE, lw=1.4)
arrow(ax, left_x, sy_s, sx_s - BOX_W / 2, sy_s, color=C_ORANGE, lw=1.4)
label(ax, left_x - 0.5, (vy + sy_s) / 2, "rejected\n[N]", color=C_ORANGE, fs=7.5)

# ── SEARCH end-of-pattern -> LANDING (RTL) — far left ───────────────────
far_left = X_MAIN - BOX_W / 2 - 1.6
lx, ly = positions["LANDING"]

arrow(ax, sx_s - BOX_W / 2, sy_s - 0.1, far_left, sy_s - 0.1, color=C_GREY, lw=1.0, ls="--")
arrow(ax, far_left, sy_s - 0.1, far_left, ly, color=C_GREY, lw=1.0, ls="--")
arrow(ax, far_left, ly, lx - BOX_W / 2, ly, color=C_GREY, lw=1.0, ls="--")
label(ax, far_left - 0.55, (sy_s + ly) / 2, "pattern\ncomplete\n(RTL)", color=C_GREY, fs=6.5)

# ── MANUAL override arrows ──────────────────────────────────────────────
# Any -> MANUAL (dashed)
arrow(ax, positions["SEARCH"][0] + BOX_W / 2, positions["SEARCH"][1] + 0.06,
      mx - BOX_W / 2, my + 0.06,
      rad=-0.08, color=C_RED, lw=1.6, ls="--")
label(ax, (positions["SEARCH"][0] + BOX_W / 2 + mx - BOX_W / 2) / 2,
      my + 0.50, "RC override /\nM key (any state)", color=C_RED, fs=7)

# MANUAL -> resume (dashed)
arrow(ax, mx - BOX_W / 2, my - 0.06,
      positions["SEARCH"][0] + BOX_W / 2, positions["SEARCH"][1] - 0.06,
      rad=-0.08, color=C_RED, lw=1.6, ls="--")
label(ax, (positions["SEARCH"][0] + BOX_W / 2 + mx - BOX_W / 2) / 2,
      my - 0.50, "resume mission", color=C_RED, fs=7)

# ── RETURN_TRANSIT annotation ────────────────────────────────────────────
rtx, rty = positions["RETURN_TRANSIT"]
ax.text(rtx, rty, "RETURN\nTRANSIT", ha="center", va="center", fontsize=8,
        color=C_PURPLE, fontweight="bold", family="sans-serif", zorder=6,
        bbox=dict(boxstyle="round,pad=0.14", facecolor="#e8daef",
                  edgecolor=C_PURPLE, alpha=0.7, linewidth=1.2))
# dotted from VERIFY right to RETURN_TRANSIT
arrow(ax, vx + BOX_W / 2, vy - 0.05, rtx - 1.0, rty + 0.25,
      rad=0.25, color=C_PURPLE, lw=1.0, ls=":")
label(ax, rtx - 0.1, rty + 0.65, "if far from\nsearch area", color=C_PURPLE, fs=6.5)

# ── Safety annotations ──────────────────────────────────────────────────
# Geofence
gf_x, gf_y = mx, my + 1.5
ax.text(gf_x, gf_y, "Geofence breach\nemergency RTL", ha="center",
        va="center", fontsize=7.5, color=C_RED, fontstyle="italic",
        family="sans-serif", zorder=5,
        bbox=dict(boxstyle="round,pad=0.15", facecolor="#fadbd8",
                  edgecolor=C_RED, alpha=0.85, linewidth=1.0))
arrow(ax, gf_x, gf_y - 0.32, mx, my + BOX_H / 2,
      color=C_RED, lw=1.0, ls=":")

# Link loss
ll_x, ll_y = mx, my - 1.5
ax.text(ll_x, ll_y, "Link loss / RC kill\nRTL (firmware)", ha="center",
        va="center", fontsize=7.5, color=C_RED, fontstyle="italic",
        family="sans-serif", zorder=5,
        bbox=dict(boxstyle="round,pad=0.15", facecolor="#fadbd8",
                  edgecolor=C_RED, alpha=0.85, linewidth=1.0))
arrow(ax, mx, my - BOX_H / 2, ll_x, ll_y + 0.32,
      color=C_RED, lw=1.0, ls=":")

# ── Legend ───────────────────────────────────────────────────────────────
legend_items = [
    mpatches.Patch(facecolor=C_GREEN_LT,  edgecolor=C_GREEN,  linewidth=1.5,
                   label="Initialisation / End"),
    mpatches.Patch(facecolor=C_BLUE_LT,   edgecolor=C_BLUE,   linewidth=1.5,
                   label="Autonomous flight"),
    mpatches.Patch(facecolor=C_ORANGE_LT, edgecolor=C_ORANGE,  linewidth=1.5,
                   label="Detection / Verification"),
    mpatches.Patch(facecolor=C_RED_LT,    edgecolor=C_RED,     linewidth=1.5,
                   label="Safety override"),
]
ax.legend(handles=legend_items, loc="lower right", fontsize=8.5, frameon=True,
          fancybox=True, framealpha=0.95, edgecolor="#cccccc",
          title="State categories", title_fontsize=9,
          bbox_to_anchor=(0.98, 0.02))

# ── Title ────────────────────────────────────────────────────────────────
ax.text(X_MAIN, Y_TOP + 0.6, "SAR Drone Mission State Machine",
        ha="center", va="center", fontsize=15, fontweight="bold",
        color=C_TEXT, family="sans-serif", zorder=10)

# ── Save ─────────────────────────────────────────────────────────────────
out_dir = os.path.dirname(os.path.abspath(__file__))
for ext, dpi in [("pdf", 300), ("png", 150)]:
    path = os.path.join(out_dir, f"state_machine_generated.{ext}")
    fig.savefig(path, bbox_inches="tight", dpi=dpi, facecolor=C_BG)
    print(f"OK: {path}")

plt.close(fig)
