"""Generate radar/spider chart comparing our SAR drone against industry benchmarks."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os

OUT = os.path.dirname(os.path.abspath(__file__))

# ── Style ──
plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 10,
    'axes.titlesize': 13,
    'axes.labelsize': 11,
    'figure.dpi': 300,
})

# ── Data (normalised to 0-10 scale) ──
dimensions = [
    'Detection\nAccuracy',
    'Inference\nSpeed',
    'GPS\nAccuracy',
    'Cost\nEfficiency',
    'Autonomy\nLevel',
    'Safety\nLayers',
    'Test\nCoverage',
    'Portability',
]

# Our system scores (0-10)
ours = [
    9.5,   # Detection: 99.5% mAP50 (near-perfect)
    4.0,   # Inference: 4.8 FPS TFLite / 9 FPS NCNN (CPU-only, no GPU)
    7.0,   # GPS: 1.8m CEP50 (good for consumer GPS)
    9.5,   # Cost: £150 compute vs £2000+ industry
    7.5,   # Autonomy: Sheridan Level 6 (supervised, operator confirm)
    9.0,   # Safety: 5-layer geofence + RC override + RTL + NFZ + altitude cap
    9.0,   # Test: 74 scripts + 127 unit tests + progressive flight ladder
    9.0,   # Portability: same code sim-to-real, 3 platforms, auto-detect
]

# Typical academic SAR system scores (0-10)
industry = [
    7.5,   # Detection: ~95% mAP50 typical
    7.0,   # Inference: 10-30 FPS (GPU-equipped, e.g. Jetson)
    7.0,   # GPS: 1-3m CEP50 (RTK sometimes)
    4.0,   # Cost: £2000+ (Jetson + thermal camera)
    6.0,   # Autonomy: varies Sheridan 4-8, often less structured
    4.0,   # Safety: 1-2 layers typical (geofence + RTL)
    4.5,   # Test: varies widely, often ad-hoc
    4.0,   # Portability: often separate sim/real codebases
]

# ── Radar chart ──
N = len(dimensions)
angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
angles += angles[:1]  # close the polygon

ours_vals = ours + ours[:1]
industry_vals = industry + industry[:1]

fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))

# Draw grid circles with labels
ax.set_ylim(0, 10)
ax.set_yticks([2, 4, 6, 8, 10])
ax.set_yticklabels(['2', '4', '6', '8', '10'], fontsize=8, color='#666666')
ax.set_rlabel_position(22.5)

# Gridline styling
ax.yaxis.grid(True, color='#CCCCCC', linewidth=0.5, linestyle='-')
ax.xaxis.grid(True, color='#CCCCCC', linewidth=0.5, linestyle='-')
ax.spines['polar'].set_visible(False)

# Set dimension labels
ax.set_xticks(angles[:-1])
ax.set_xticklabels(dimensions, fontsize=9, fontweight='bold', color='#333333')

# Plot industry baseline (grey dashed, behind)
ax.plot(angles, industry_vals, 'o',
        color='#888888', linewidth=1.5, linestyle='--',
        markersize=5, label='Typical Academic SAR', zorder=2)
ax.fill(angles, industry_vals, alpha=0.08, color='#888888', zorder=1)

# Plot our system (blue solid, on top)
ax.plot(angles, ours_vals, 'o-',
        color='#2166AC', linewidth=2.0,
        markersize=6, label='Our System', zorder=3)
ax.fill(angles, ours_vals, alpha=0.15, color='#2166AC', zorder=2)

# Add value annotations for our system
for i, (angle, val) in enumerate(zip(angles[:-1], ours)):
    offset_r = 0.6
    ax.text(angle, val + offset_r, f'{val:.1f}',
            ha='center', va='center', fontsize=7.5,
            color='#2166AC', fontweight='bold', zorder=5)

# Add value annotations for industry
for i, (angle, val) in enumerate(zip(angles[:-1], industry)):
    offset_r = -0.7
    ax.text(angle, val + offset_r, f'{val:.1f}',
            ha='center', va='center', fontsize=7,
            color='#888888', fontstyle='italic', zorder=5)

# Legend
ax.legend(loc='upper right', bbox_to_anchor=(1.28, 1.12),
          fontsize=9, framealpha=0.9, edgecolor='#CCCCCC')

# Title
ax.set_title('SAR Drone System Comparison\n(normalised 0\u201310 scale)',
             fontsize=14, fontweight='bold', pad=25, color='#222222')

plt.tight_layout()

# ── Save ──
for ext in ('pdf', 'png'):
    path = os.path.join(OUT, f'radar_comparison.{ext}')
    fig.savefig(path, dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print(f'Saved {path}')

plt.close()
