"""Confusion Matrix for YOLOv8n SAR Detector (Validation Set)."""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# --- Styling ---
TEXT_DARK = '#2c3e50'
BLUE = '#2980b9'
ORANGE = '#e67e22'
GREEN = '#27ae60'
RED = '#c0392b'

plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 11,
    'axes.labelcolor': TEXT_DARK,
    'text.color': TEXT_DARK,
    'axes.edgecolor': '#cccccc',
    'xtick.color': TEXT_DARK,
    'ytick.color': TEXT_DARK,
})

fig, ax = plt.subplots(figsize=(5.5, 5))

# Confusion matrix values
# TP=989, FP=6, FN=11, TN=50 (from 50 negative images)
cm = np.array([[989, 6],
               [11,  50]])

labels = np.array([['TP\n989', 'FP\n6'],
                    ['FN\n11', 'TN\n50']])

# Color map: green diagonal, red off-diagonal
colors = np.array([[0.85, 0.15],
                    [0.15, 0.85]])

green_cmap = mcolors.LinearSegmentedColormap.from_list('gn', ['#ffffff', GREEN])
red_cmap = mcolors.LinearSegmentedColormap.from_list('rd', ['#ffffff', RED])

# Draw cells manually for dual-color scheme
for i in range(2):
    for j in range(2):
        on_diag = (i == j)
        cmap = green_cmap if on_diag else red_cmap
        intensity = colors[i, j]
        color = cmap(intensity)
        rect = plt.Rectangle((j, i), 1, 1, facecolor=color, edgecolor='white', linewidth=3)
        ax.add_patch(rect)
        # Value text
        ax.text(j + 0.5, i + 0.5, labels[i, j],
                ha='center', va='center', fontsize=16, fontweight='bold',
                color=TEXT_DARK)

ax.set_xlim(0, 2)
ax.set_ylim(0, 2)
ax.invert_yaxis()
ax.set_xticks([0.5, 1.5])
ax.set_xticklabels(['Dummy', 'Background'], fontsize=12)
ax.set_yticks([0.5, 1.5])
ax.set_yticklabels(['Dummy', 'Background'], fontsize=12)
ax.set_xlabel('Predicted Class', fontsize=13, fontweight='bold', labelpad=25)
ax.set_ylabel('True Class', fontsize=13, fontweight='bold', labelpad=10)
ax.tick_params(length=0)

# Metrics annotation
precision = 989 / (989 + 6)
recall = 989 / (989 + 11)
f1 = 2 * precision * recall / (precision + recall)
metrics_text = (f'Precision = {precision:.3f}    '
                f'Recall = {recall:.3f}    '
                f'F1 = {f1:.3f}')
fig.text(0.5, 0.06, metrics_text, ha='center', va='center',
         fontsize=10, style='italic', color=BLUE)

ax.set_title('YOLOv8n SAR Detector — Confusion Matrix (Validation Set)',
             fontsize=12, fontweight='bold', pad=15, color=TEXT_DARK)

plt.subplots_adjust(bottom=0.16)
plt.savefig('confusion_matrix.pdf', bbox_inches='tight', dpi=300)
plt.savefig('confusion_matrix.png', bbox_inches='tight', dpi=300)
print("Saved confusion_matrix.pdf + .png")
