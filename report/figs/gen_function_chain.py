"""Generate function_chain.pdf — detection probability as a function DAG."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path

OUT = Path(__file__).parent

fig, ax = plt.subplots(figsize=(13, 7.5))
ax.set_xlim(-0.5, 12.5)
ax.set_ylim(-0.5, 7.5)
ax.axis("off")

# Colors
C_CTRL = "#2166ac"   # controllable parameters (blue)
C_FIXED = "#999999"  # fixed parameters (grey)
C_INTER = "#f4a582"  # intermediate quantities (orange)
C_OUT = "#b2182b"    # output (red)
C_BG = "#f7f7f7"

def box(x, y, w, h, text, eq, color, fontsize=9.5, eq_fs=8.5):
    """Draw a rounded box with label and equation."""
    rect = mpatches.FancyBboxPatch(
        (x - w/2, y - h/2), w, h,
        boxstyle="round,pad=0.12", facecolor=color, edgecolor="#404040",
        lw=1.3, alpha=0.92, zorder=2)
    ax.add_patch(rect)
    ax.text(x, y + 0.15, text, ha="center", va="center",
            fontsize=fontsize, fontweight="bold", zorder=3, color="#1a1a1a")
    if eq:
        ax.text(x, y - 0.25, eq, ha="center", va="center",
                fontsize=eq_fs, zorder=3, color="#404040", fontstyle="italic",
                family="serif")

def param(x, y, text, color):
    """Draw a small parameter ellipse."""
    ell = mpatches.Ellipse((x, y), 1.6, 0.7, facecolor=color, edgecolor="#606060",
                            lw=1, alpha=0.85, zorder=2)
    ax.add_patch(ell)
    ax.text(x, y, text, ha="center", va="center", fontsize=8.5, zorder=3,
            fontweight="bold", color="white" if color == C_CTRL else "#1a1a1a")

def arrow(x1, y1, x2, y2):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color="#404040", lw=1.3,
                                connectionstyle="arc3,rad=0.0"),
                zorder=1)

# ── Level 0: Output ──
box(6, 7, 3.2, 0.9, r"$P_{\mathrm{detect}}$",
    r"$1 - (1-p)^{n}$", C_OUT, fontsize=11, eq_fs=10)

# ── Level 1: n_frames and p_single ──
box(3, 5.2, 2.8, 0.9, r"$n_{\mathrm{frames}}$",
    r"$\frac{W_{\mathrm{foot}}}{v} \cdot f_{\!\mathrm{ps}}$", C_INTER)
box(9, 5.2, 2.8, 0.9, r"$p_{\mathrm{single}}$",
    r"$\sigma(s_{\mathrm{px}}, \beta, c_{\min})$", C_INTER)

arrow(3, 5.65, 5.2, 6.55)
arrow(9, 5.65, 6.8, 6.55)

# ── Level 2: footprint, speed, fps | pixel_size, blur, conf ──
box(1.2, 3.2, 2.4, 0.9, r"$W_{\mathrm{foot}}$",
    r"$h \cdot \frac{w_s}{f}$", C_INTER)
box(4.8, 3.2, 2.4, 0.9, r"$s_{\mathrm{px}}$",
    r"$\frac{H_t \cdot f}{h \cdot w_s / W_{\mathrm{img}}}$", C_INTER)
box(8.5, 3.2, 2.2, 0.9, r"$\beta_{\mathrm{blur}}$",
    r"$\frac{v \cdot t_{\exp}}{h} \cdot f_{\mathrm{px}}$", C_INTER)

arrow(1.2, 3.65, 2.3, 4.75)
arrow(4.8, 3.65, 3.5, 4.75)
arrow(4.8, 3.65, 8.3, 4.75)
arrow(8.5, 3.65, 9.5, 4.75)

# ── Level 3: Leaf parameters ──
# Controllable (blue)
param(0.8, 1.2, "altitude h", C_CTRL)
param(3.5, 1.2, "speed v", C_CTRL)
param(6.5, 1.2, r"overlap $\eta$", C_CTRL)

# Fixed (grey)
param(9.5, 1.2, r"focal $f$", C_FIXED)
param(11.5, 1.2, r"sensor $w_s$", C_FIXED)
param(5.0, 0.0, r"FPS $f_{\mathrm{ps}}$", C_FIXED)
param(8.0, 0.0, r"$t_{\exp}$", C_FIXED)
param(11.0, 0.0, r"$H_t$ (dummy)", C_FIXED)

# Arrows from params to boxes
arrow(0.8, 1.55, 1.0, 2.75)   # alt -> footprint
arrow(0.8, 1.55, 4.3, 2.75)   # alt -> pixel_size
arrow(0.8, 1.55, 8.0, 2.75)   # alt -> blur
arrow(3.5, 1.55, 3.0, 4.75)   # speed -> n_frames
arrow(3.5, 1.55, 8.2, 2.75)   # speed -> blur
arrow(9.5, 1.55, 1.5, 2.75)   # focal -> footprint
arrow(9.5, 1.55, 5.2, 2.75)   # focal -> pixel_size
arrow(11.5, 1.55, 1.8, 2.75)  # sensor -> footprint
arrow(11.5, 1.55, 5.5, 2.75)  # sensor -> pixel_size
arrow(5.0, 0.35, 3.2, 4.75)   # fps -> n_frames
arrow(8.0, 0.35, 8.5, 2.75)   # t_exp -> blur
arrow(11.0, 0.35, 5.3, 2.75)  # dummy_h -> pixel_size

# ── Legend ──
legend_items = [
    mpatches.Patch(facecolor=C_CTRL, edgecolor="#404040", label="Controllable parameter"),
    mpatches.Patch(facecolor=C_FIXED, edgecolor="#404040", label="Fixed parameter"),
    mpatches.Patch(facecolor=C_INTER, edgecolor="#404040", label="Intermediate quantity"),
    mpatches.Patch(facecolor=C_OUT, edgecolor="#404040", label="Mission objective"),
]
ax.legend(handles=legend_items, loc="lower left", fontsize=9, framealpha=0.9,
          ncol=2, bbox_to_anchor=(0.0, -0.02))

ax.set_title("Detection Probability: Functional Dependency Chain",
             fontsize=14, fontweight="bold", pad=15)

for fmt in ["pdf", "png"]:
    fig.savefig(OUT / f"function_chain.{fmt}", dpi=300, bbox_inches="tight")
print("Saved function_chain.pdf/.png")
