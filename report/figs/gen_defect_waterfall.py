#!/usr/bin/env python3
"""Generate defect discovery tier waterfall chart."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'DejaVu Serif'],
    'font.size': 10,
    'axes.labelsize': 11,
    'axes.titlesize': 12,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.05,
})

# --- Data from evaluation_detail.tex Tab. bug-cost ---
# Tier 1 (SITL simulation): 5 defects, 1.5 hr total
# Tier 2 (Pi bench): 7 defects, 4.7 hr total (6 listed + TFLite bbox fix)
# Tier 3 proxy (DJI video): 1 defect (GPS timing lag)
# Tiers 4-5: 0 (no flight occurred)

tiers = [
    'Tier 1\nSITL Simulation',
    'Tier 2\nPi Bench Testing',
    'Tier 3 Proxy\nDJI Video Analysis',
    'Tier 4\u20135\nOutdoor Flight',
]

defects = [5, 7, 1, 0]
fix_hours = [1.5, 4.7, 0, 0]  # GPS lag: mitigated, no fix time
cumulative = np.cumsum(defects)
total = sum(defects)

# Severity: mission-critical vs moderate
# Mission-critical (from evaluation.tex): geofence sign, repulsive force reversed,
# BGR inversion, TFLite bbox, barometric drift, duplicate target, centering timeout = 7
# Moderate: FOV miscalib, pyserial, tflite-runtime, camera conflict, self.investigating, GPS lag = 6
critical = [3, 3, 1, 0]   # per tier
moderate = [2, 4, 0, 0]

colors_crit = '#e74c3c'
colors_mod = '#f39c12'
colors_cum = '#2c3e50'

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.0, 3.5), gridspec_kw={'width_ratios': [1.3, 1]})

# --- Left panel: stacked bar by severity ---
x = np.arange(len(tiers))
w = 0.55

bars_mod = ax1.bar(x, moderate, w, color=colors_mod, edgecolor='white', linewidth=0.8,
                   label='Moderate', zorder=3)
bars_crit = ax1.bar(x, critical, w, bottom=moderate, color=colors_crit, edgecolor='white',
                    linewidth=0.8, label='Mission-critical', zorder=3)

# Labels on bars
for i, (m, c) in enumerate(zip(moderate, critical)):
    total_i = m + c
    if total_i > 0:
        ax1.text(i, total_i + 0.15, str(total_i), ha='center', va='bottom',
                 fontweight='bold', fontsize=11, color=colors_cum)

ax1.set_xticks(x)
ax1.set_xticklabels(tiers, fontsize=8.5)
ax1.set_ylabel('Defects discovered', fontsize=11)
ax1.set_ylim(0, 9)
ax1.legend(fontsize=8.5, loc='upper right', framealpha=0.9)
ax1.grid(axis='y', alpha=0.3, zorder=0)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.set_title('(a) Defects by tier and severity', fontsize=10.5, pad=8)

# Annotate: % caught before flight
pct = sum(defects[:3]) / max(total, 1) * 100
ax1.annotate(f'{pct:.0f}% caught\nbefore flight',
             xy=(2.3, 2), fontsize=9, fontweight='bold', color='#27ae60',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='#eafaf1', edgecolor='#27ae60', alpha=0.9))

# --- Right panel: estimated cost comparison ---
# Fix time at bench vs hypothetical flight cost
tier_labels = ['Tier 1\n(sim)', 'Tier 2\n(bench)', 'Tier 3\n(proxy)']
actual_hours = [1.5, 4.7, 0.0]
# If discovered in flight: geofence -> crash (£1000+), BGR -> mission fail (4hr rework), etc
hypothetical_hours = [12, 40, 4]  # estimated hours + hardware cost equivalent

x2 = np.arange(len(tier_labels))
w2 = 0.35

bars_actual = ax2.bar(x2 - w2/2, actual_hours, w2, color='#27ae60', edgecolor='white',
                      label='Actual fix time', zorder=3)
bars_hypo = ax2.bar(x2 + w2/2, hypothetical_hours, w2, color='#e74c3c', edgecolor='white',
                    label='Est. flight-day cost', zorder=3)

for i, (a, h) in enumerate(zip(actual_hours, hypothetical_hours)):
    if a > 0:
        ax2.text(i - w2/2, a + 0.5, f'{a:.1f}h', ha='center', fontsize=8, color='#27ae60', fontweight='bold')
    if h > 0:
        ax2.text(i + w2/2, h + 0.5, f'{h}h', ha='center', fontsize=8, color='#e74c3c', fontweight='bold')

ax2.set_xticks(x2)
ax2.set_xticklabels(tier_labels, fontsize=8.5)
ax2.set_ylabel('Resolution time (hours)', fontsize=11)
ax2.legend(fontsize=7.5, loc='upper right', framealpha=0.9)
ax2.grid(axis='y', alpha=0.3, zorder=0)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.set_title('(b) Fix cost: actual vs. hypothetical', fontsize=10.5, pad=8)

plt.tight_layout()
plt.savefig('defect_waterfall.pdf')
plt.savefig('defect_waterfall.png')
print('Saved defect_waterfall.pdf + .png')
