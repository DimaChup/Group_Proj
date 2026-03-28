"""Generate scoring_overview.pdf — Infographic showing constraint vs optimized dimensions."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from pathlib import Path

OUT = Path(__file__).parent

plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 9,
    'axes.titlesize': 12,
    'axes.labelsize': 10,
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.15,
})

fig, ax = plt.subplots(figsize=(10, 5.5))
ax.set_xlim(0, 10)
ax.set_ylim(0, 6)
ax.axis('off')

# ── Title ──
ax.text(5, 5.5, 'Mission Scoring Framework', ha='center', va='center',
        fontsize=15, fontweight='bold', color='#1B2631')

# ── Constraint row (top) ──
constraint_color = '#2E86C1'
constraint_bg = '#D6EAF8'

# "CONSTRAINTS (pass/fail)" label
ax.text(1.0, 4.55, 'CONSTRAINTS', ha='center', va='center',
        fontsize=11, fontweight='bold', color=constraint_color)
ax.text(1.0, 4.15, '(pass / fail)', ha='center', va='center',
        fontsize=9, color='#5B7FA5', style='italic')

# Safety box
box_s = FancyBboxPatch((2.3, 3.85), 2.8, 1.1, boxstyle="round,pad=0.15",
                         facecolor=constraint_bg, edgecolor=constraint_color, linewidth=1.5)
ax.add_patch(box_s)
ax.text(3.7, 4.65, 'Safety', ha='center', va='center',
        fontsize=12, fontweight='bold', color=constraint_color)
ax.text(3.7, 4.2, r'$\checkmark$ PASS  (score = 0.96)', ha='center', va='center',
        fontsize=9, color='#1A5276')

# Time box
box_t = FancyBboxPatch((5.8, 3.85), 2.8, 1.1, boxstyle="round,pad=0.15",
                         facecolor=constraint_bg, edgecolor=constraint_color, linewidth=1.5)
ax.add_patch(box_t)
ax.text(7.2, 4.65, 'Time', ha='center', va='center',
        fontsize=12, fontweight='bold', color=constraint_color)
ax.text(7.2, 4.2, r'$\checkmark$ PASS  (must be < 300 s)', ha='center', va='center',
        fontsize=9, color='#1A5276')

# ── Optimized row (bottom) ──
opt_color = '#27AE60'
opt_bg = '#D5F5E3'

ax.text(1.0, 2.75, 'OPTIMIZED', ha='center', va='center',
        fontsize=11, fontweight='bold', color=opt_color)
ax.text(1.0, 2.35, '(continuous 0\u20131)', ha='center', va='center',
        fontsize=9, color='#52876E', style='italic')

# Detection box
dims = [
    ('Detection', 0.93, 0.40),
    ('Coverage',  0.96, 0.35),
    ('Energy',    0.89, 0.25),
]
x_positions = [2.3, 4.6, 6.9]
for (name, score, weight), xp in zip(dims, x_positions):
    box = FancyBboxPatch((xp, 2.05), 1.9, 1.1, boxstyle="round,pad=0.15",
                          facecolor=opt_bg, edgecolor=opt_color, linewidth=1.5)
    ax.add_patch(box)
    ax.text(xp + 0.95, 2.85, name, ha='center', va='center',
            fontsize=11, fontweight='bold', color=opt_color)
    ax.text(xp + 0.95, 2.4, f'{score:.2f}  (w = {weight:.2f})',
            ha='center', va='center', fontsize=9, color='#1E8449')

# ── Arrow + composite formula ──
# Horizontal line
ax.annotate('', xy=(8.5, 1.3), xytext=(1.5, 1.3),
            arrowprops=dict(arrowstyle='->', color='#566573', lw=1.5))

# Formula
formula = (r'$\mathrm{Composite} = 0.40 \times \mathrm{Det.} '
           r'+ 0.35 \times \mathrm{Cov.} '
           r'+ 0.25 \times \mathrm{Energy}$')
ax.text(5.0, 1.05, formula, ha='center', va='center',
        fontsize=11, color='#1B2631')

# Result
result_box = FancyBboxPatch((3.5, 0.15), 3.0, 0.65, boxstyle="round,pad=0.12",
                              facecolor='#F9E79F', edgecolor='#D4AC0D', linewidth=2)
ax.add_patch(result_box)
ax.text(5.0, 0.48, '= 0.93', ha='center', va='center',
        fontsize=16, fontweight='bold', color='#7D6608')

# ── Footnote ──
ax.text(5.0, -0.15, 'Safety and Time are thresholds, not weights --- you either pass or fail.',
        ha='center', va='center', fontsize=8, color='#7F8C8D', style='italic')

for ext in ('pdf', 'png'):
    fig.savefig(OUT / f'scoring_overview.{ext}')
plt.close(fig)
print(f'Saved scoring_overview.pdf/.png to {OUT}')
