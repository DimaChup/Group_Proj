"""Chart 11: Estimator Comparison — CEP50 for 4 GPS estimation methods.

Values from simulation testing (simple_simulator.py) and DJI video analysis
(video_test.py).  GPS error model: N(0,3m) isotropic + 100-200ms timing lag
at 5-10 m/s flight speed.
"""
import numpy as np
import matplotlib.pyplot as plt

np.random.seed(42)

# --- Styling ---
TEXT_DARK = '#2c3e50'
BLUE = '#2980b9'
ORANGE = '#e67e22'
GREEN = '#27ae60'
GREY = '#7f8c8d'

plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 10,
    'axes.labelcolor': TEXT_DARK,
    'text.color': TEXT_DARK,
    'axes.edgecolor': '#cccccc',
    'xtick.color': TEXT_DARK,
    'ytick.color': TEXT_DARK,
})

# --- Measured / documented values ---
# From simple_simulator.py testing and DJI video analysis (CEP50 in metres)
labels = [
    'Rolling Average\n(last 10)',
    'Cumulative\nAverage',
    'Kalman\nFilter',
    'Inverse Variance\nWeighted',
]

cep50_values = [4.5, 3.2, 2.8, 2.3]
# 95% confidence intervals from bootstrap resampling of simulation runs
cep50_errs = np.array([
    [0.8, 0.9],   # Rolling: [3.7, 5.4]
    [0.5, 0.6],   # Cumulative: [2.7, 3.8]
    [0.4, 0.5],   # Kalman: [2.4, 3.3]
    [0.3, 0.4],   # IVW: [2.0, 2.7]
]).T

# --- Plot ---
fig, ax = plt.subplots(1, 1, figsize=(7, 4.5))

colors = ['#bdc3c7', '#bdc3c7', '#bdc3c7', ORANGE]
edge_colors = [GREY, GREY, GREY, '#d35400']
hatches = ['', '', '', '']

bars = ax.bar(range(len(labels)), cep50_values, color=colors, edgecolor=edge_colors,
              linewidth=1.5, width=0.6, zorder=3)
ax.errorbar(range(len(labels)), cep50_values, yerr=cep50_errs, fmt='none',
            ecolor=TEXT_DARK, capsize=5, capthick=1.5, linewidth=1.5, zorder=4)

# Highlight selected method
bars[-1].set_edgecolor('#d35400')
bars[-1].set_linewidth(2.5)

# Value labels on bars
for i, (v, label) in enumerate(zip(cep50_values, labels)):
    ax.text(i, v + 0.25, f'{v:.1f} m', ha='center', va='bottom',
            fontsize=10, fontweight='bold', color=TEXT_DARK, zorder=5)

# "Selected" annotation
ax.annotate('Selected', xy=(3, cep50_values[3] + 0.6),
            fontsize=9, fontweight='bold', color='#d35400', ha='center',
            va='bottom',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#fef9e7',
                      edgecolor='#d35400', linewidth=1.2))

ax.set_xticks(range(len(labels)))
ax.set_xticklabels(labels, fontsize=9)
ax.set_ylabel('CEP50 Error (m)', fontsize=11)
ax.set_title('GPS Estimation Method Comparison', fontsize=13,
             fontweight='bold', color=TEXT_DARK, pad=12)

ax.set_ylim(0, max(cep50_values) + 1.5)
ax.grid(axis='y', alpha=0.2, zorder=0)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()
plt.savefig('estimator_comparison.pdf', bbox_inches='tight', dpi=300)
plt.savefig('estimator_comparison.png', bbox_inches='tight', dpi=200)
print('Saved estimator_comparison.pdf')
