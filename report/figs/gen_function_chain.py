"""Generate function_chain.pdf — detection probability as a function DAG."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path

OUT = Path(__file__).parent

fig, ax = plt.subplots(figsize=(14, 8.5))
ax.set_xlim(-1, 14)
ax.set_ylim(-1.2, 8.5)
ax.axis("off")

# Colors
C_CTRL = "#2166ac"   # controllable parameters (blue)
C_FIXED = "#808080"  # fixed parameters (grey)
C_INTER = "#f4a582"  # intermediate quantities (orange)
C_OUT = "#b2182b"    # output (red)

def box(x, y, w, h, text, eq, color, fontsize=9.5, eq_fs=8.5):
    """Draw a rounded box with label and equation."""
    rect = mpatches.FancyBboxPatch(
        (x - w/2, y - h/2), w, h,
        boxstyle="round,pad=0.12", facecolor=color, edgecolor="#404040",
        lw=1.3, alpha=0.92, zorder=2)
    ax.add_patch(rect)
    ax.text(x, y + 0.18, text, ha="center", va="center",
            fontsize=fontsize, fontweight="bold", zorder=3, color="#1a1a1a")
    if eq:
        ax.text(x, y - 0.25, eq, ha="center", va="center",
                fontsize=eq_fs, zorder=3, color="#404040", fontstyle="italic",
                family="serif")

def param(x, y, text, color):
    """Draw a small parameter ellipse."""
    ell = mpatches.Ellipse((x, y), 1.7, 0.7, facecolor=color, edgecolor="#505050",
                            lw=1, alpha=0.85, zorder=2)
    ax.add_patch(ell)
    ax.text(x, y, text, ha="center", va="center", fontsize=8.5, zorder=3,
            fontweight="bold", color="white" if color == C_CTRL else "#1a1a1a")

def arrow(x1, y1, x2, y2, rad=0.0, color="#404040", lw=1.2, dashed=False):
    style = f"arc3,rad={rad}" if rad != 0 else "arc3,rad=0.0"
    props = dict(arrowstyle="-|>", color=color, lw=lw,
                 connectionstyle=style)
    if dashed:
        props["linestyle"] = (0, (4, 3))
        props["alpha"] = 0.6
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=props, zorder=1)

# ══════════════════════════════════════════════════════════════
#  Layout: tree flows top-down with minimal crossings
#
#  Level 0 (y=7.5):  P_detect
#  Level 1 (y=5.5):  n_frames          p_single
#  Level 2 (y=3.5):  W_foot   |   s_px       blur
#  Level 3 (y=1.5):  params grouped under their parent boxes
#  Level 4 (y=0.0):  extra fixed params
# ══════════════════════════════════════════════════════════════

# ── Level 0: Output ──
box(6.5, 7.5, 3.5, 1.0, r"$P_{\mathrm{detect}}$",
    r"$1 - (1-p)^{n}$", C_OUT, fontsize=12, eq_fs=10)

# ── Level 1 ──
box(3, 5.5, 3.0, 1.0, r"$n_{\mathrm{frames}}$",
    r"$\frac{W_{\mathrm{foot}}}{v} \cdot f_{\!\mathrm{ps}}$", C_INTER)
box(10, 5.5, 3.0, 1.0, r"$p_{\mathrm{single}}$",
    r"$\sigma(s_{\mathrm{px}},\; \beta_{\mathrm{blur}},\; c_{\min})$", C_INTER)

arrow(3, 6.0, 5.5, 7.0)
arrow(10, 6.0, 7.5, 7.0)

# ── Level 2 ──
# W_foot feeds n_frames (left side)
box(1.5, 3.5, 2.5, 1.0, r"$W_{\mathrm{foot}}$",
    r"$h \cdot \frac{w_s}{f}$", C_INTER)
# s_px feeds p_single (right side)
box(8.5, 3.5, 2.8, 1.0, r"$s_{\mathrm{px}}$",
    r"$\frac{H_t \cdot f}{h \cdot (w_s / W_{\mathrm{img}})}$", C_INTER)
# blur feeds p_single (right side)
box(12, 3.5, 2.2, 1.0, r"$\beta_{\mathrm{blur}}$",
    r"$\frac{v \cdot t_{\exp}}{h} \cdot f_{\mathrm{px}}$", C_INTER)

# Level 2 -> Level 1
arrow(1.5, 4.0, 2.3, 5.0)    # W_foot -> n_frames
arrow(8.5, 4.0, 9.3, 5.0)    # s_px -> p_single
arrow(12, 4.0, 10.7, 5.0)    # blur -> p_single

# ── Level 3: Leaf parameters ──
# Group under parent boxes to minimise crossings

# Under W_foot (left): altitude, focal, sensor
param(0.3, 1.5, "altitude $h$", C_CTRL)
param(1.5, 1.5, "focal $f$", C_FIXED)
param(2.8, 1.5, "sensor $w_s$", C_FIXED)

# Middle: speed, FPS feed n_frames directly
param(4.2, 1.5, "speed $v$", C_CTRL)
param(5.5, 1.5, r"FPS $f_{\mathrm{ps}}$", C_FIXED)

# Under s_px: altitude (shared), focal (shared), sensor (shared), H_t
param(7.5, 1.5, r"$H_t$ (dummy)", C_FIXED)

# Under blur (right): speed (shared), t_exp
param(11.0, 1.5, r"$t_{\exp}$", C_FIXED)
param(12.8, 1.5, r"overlap $\eta$", C_CTRL)

# ── Arrows: params -> Level 2 boxes ──
# altitude -> W_foot, s_px, blur
arrow(0.3, 1.85, 1.0, 3.0, rad=0.0, color=C_CTRL)     # alt -> W_foot (direct)
arrow(0.3, 1.85, 7.8, 3.0, rad=-0.15, color=C_CTRL, dashed=True)    # alt -> s_px
arrow(0.3, 1.85, 11.5, 3.0, rad=-0.12, color=C_CTRL, dashed=True)  # alt -> blur

# focal -> W_foot, s_px
arrow(1.5, 1.85, 1.5, 3.0)                              # focal -> W_foot (direct)
arrow(1.5, 1.85, 8.0, 3.0, rad=-0.12, dashed=True)      # focal -> s_px

# sensor -> W_foot, s_px
arrow(2.8, 1.85, 2.0, 3.0)                              # sensor -> W_foot
arrow(2.8, 1.85, 8.3, 3.0, rad=-0.10, dashed=True)      # sensor -> s_px

# speed -> n_frames, blur
arrow(4.2, 1.85, 3.5, 5.0, rad=0.0, color=C_CTRL)      # speed -> n_frames (direct)
arrow(4.2, 1.85, 11.8, 3.0, rad=-0.10, color=C_CTRL, dashed=True)  # speed -> blur

# FPS -> n_frames
arrow(5.5, 1.85, 3.8, 5.0, rad=0.0)                     # fps -> n_frames

# H_t -> s_px
arrow(7.5, 1.85, 8.5, 3.0)                              # dummy_h -> s_px

# t_exp -> blur
arrow(11.0, 1.85, 12.0, 3.0)                            # t_exp -> blur

# ── Annotation: shared parameters ──
# Small note showing altitude and speed affect multiple quantities
ax.text(0.3, 0.7, "affects 3\nquantities", ha="center", va="center",
        fontsize=7, color=C_CTRL, fontstyle="italic")
ax.text(4.2, 0.7, "affects 2\nquantities", ha="center", va="center",
        fontsize=7, color=C_CTRL, fontstyle="italic")

# ── Legend ──
legend_items = [
    mpatches.Patch(facecolor=C_CTRL, edgecolor="#404040",
                   label="Controllable parameter (design choice)"),
    mpatches.Patch(facecolor=C_FIXED, edgecolor="#404040",
                   label="Fixed parameter (hardware / environment)"),
    mpatches.Patch(facecolor=C_INTER, edgecolor="#404040",
                   label="Intermediate quantity"),
    mpatches.Patch(facecolor=C_OUT, edgecolor="#404040",
                   label="Mission objective"),
]
ax.legend(handles=legend_items, loc="lower center", fontsize=9, framealpha=0.9,
          ncol=2, bbox_to_anchor=(0.5, -0.06))

ax.set_title("Detection Probability: Functional Dependency Chain",
             fontsize=14, fontweight="bold", pad=15)

for fmt in ["pdf", "png"]:
    fig.savefig(OUT / f"function_chain.{fmt}", dpi=300, bbox_inches="tight")
print("Saved function_chain.pdf/.png")
