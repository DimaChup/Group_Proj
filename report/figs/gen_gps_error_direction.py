"""Chart 12: GPS Error vs Flight Direction — timing lag directional bias."""
import numpy as np
import matplotlib.pyplot as plt

np.random.seed(42)

# --- Styling ---
TEXT_DARK = '#2c3e50'
BLUE = '#2980b9'
ORANGE = '#e67e22'
GREY = '#7f8c8d'

plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 10,
    'text.color': TEXT_DARK,
})

# --- Simulate GPS errors for multiple flight headings ---
n_headings = 8
n_per_heading = 40
speed_ms = 10.0
lag_s = 0.15
lag_bias_m = speed_ms * lag_s  # 1.5m systematic forward offset

along_std = 3.0
across_std = 1.6

all_angles = []
all_errors = []
all_headings = []

headings_deg = np.linspace(0, 360, n_headings, endpoint=False)

for hdg in headings_deg:
    hdg_rad = np.radians(hdg)
    along = np.random.normal(lag_bias_m, along_std, n_per_heading)
    across = np.random.normal(0, across_std, n_per_heading)

    # Convert to map frame (east, north)
    dx = along * np.sin(hdg_rad) + across * np.cos(hdg_rad)
    dy = along * np.cos(hdg_rad) - across * np.sin(hdg_rad)

    errors = np.sqrt(dx**2 + dy**2)
    angles = np.arctan2(dx, dy)  # angle from north

    all_angles.extend(angles)
    all_errors.extend(errors)
    all_headings.extend([hdg] * n_per_heading)

all_angles = np.array(all_angles)
all_errors = np.array(all_errors)
all_headings = np.array(all_headings)

# --- Create two subplots ---
fig = plt.figure(figsize=(11, 5))

# LEFT: Polar scatter showing error distribution for one heading
ax1 = fig.add_subplot(121, projection='polar')

# Pick heading=155 deg (our actual flight heading)
mask = all_headings == headings_deg[np.argmin(np.abs(headings_deg - 155))]
if not mask.any():
    # fallback: use heading closest to 155
    mask = all_headings == headings_deg[3]  # ~135 deg

# Generate specific data for heading 155
hdg_rad = np.radians(155)
along_155 = np.random.normal(lag_bias_m, along_std, 80)
across_155 = np.random.normal(0, across_std, 80)
dx_155 = along_155 * np.sin(hdg_rad) + across_155 * np.cos(hdg_rad)
dy_155 = along_155 * np.cos(hdg_rad) - across_155 * np.sin(hdg_rad)
err_155 = np.sqrt(dx_155**2 + dy_155**2)
ang_155 = np.arctan2(dx_155, dy_155)

scatter = ax1.scatter(ang_155, err_155, c=err_155, cmap='YlOrRd', s=20, alpha=0.7,
                      edgecolors='white', linewidths=0.3, vmin=0, vmax=10, zorder=3)

# Mark flight direction
ax1.annotate('', xy=(hdg_rad, 12), xytext=(hdg_rad, 0),
             arrowprops=dict(arrowstyle='->', color=ORANGE, lw=2.5))
ax1.text(hdg_rad, 13.5, f'Flight\n{155}\u00b0', ha='center', va='center',
         fontsize=8, fontweight='bold', color=ORANGE)

# Mark lag bias
ax1.plot(hdg_rad, lag_bias_m, 'D', color=ORANGE, markersize=8, zorder=5)

ax1.set_rmax(15)
ax1.set_rticks([2, 5, 10, 15])
ax1.set_yticklabels(['2m', '5m', '10m', '15m'], fontsize=7, color=GREY)
ax1.set_theta_zero_location('N')
ax1.set_theta_direction(-1)
ax1.set_title('Error Distribution\n(heading 155\u00b0, 10 m/s)', fontsize=11,
              fontweight='bold', color=TEXT_DARK, pad=20)
ax1.grid(alpha=0.3)

# RIGHT: Along-track vs cross-track error comparison
ax2 = fig.add_subplot(122)

# Compute along-track and cross-track errors for all headings
speeds = [5, 7.5, 10]
along_errs = []
cross_errs = []
speed_labels = []

for spd in speeds:
    bias = spd * lag_s
    along_samples = np.random.normal(bias, along_std, 200)
    cross_samples = np.random.normal(0, across_std, 200)
    along_errs.append(np.percentile(np.abs(along_samples), 50))
    cross_errs.append(np.percentile(np.abs(cross_samples), 50))
    speed_labels.append(f'{spd} m/s')

x = np.arange(len(speeds))
width = 0.3

bars1 = ax2.bar(x - width/2, along_errs, width, color=ORANGE, edgecolor='#d35400',
                linewidth=1.2, label='Along-track', zorder=3)
bars2 = ax2.bar(x + width/2, cross_errs, width, color=BLUE, edgecolor='#1f6dad',
                linewidth=1.2, label='Cross-track', zorder=3)

# Value labels
for bar_set in [bars1, bars2]:
    for bar in bar_set:
        h = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2, h + 0.08, f'{h:.1f}',
                 ha='center', va='bottom', fontsize=9, fontweight='bold', color=TEXT_DARK)

# Annotation for timing lag
ax2.annotate(f'GPS timing lag: {int(lag_s*1000)} ms\n'
             f'At 10 m/s: {lag_bias_m:.1f} m forward bias',
             xy=(2, along_errs[2]), xytext=(1.2, along_errs[2] + 1.2),
             fontsize=8, color=ORANGE,
             arrowprops=dict(arrowstyle='->', color=ORANGE, lw=1.2),
             bbox=dict(boxstyle='round,pad=0.3', facecolor='#fef9e7',
                       edgecolor=ORANGE, linewidth=0.8))

ax2.set_xticks(x)
ax2.set_xticklabels(speed_labels, fontsize=10)
ax2.set_xlabel('Drone Speed', fontsize=11)
ax2.set_ylabel('Median Absolute Error (m)', fontsize=11)
ax2.set_title('Along-Track vs Cross-Track Error', fontsize=11,
              fontweight='bold', color=TEXT_DARK, pad=12)
ax2.legend(fontsize=9, framealpha=0.9, edgecolor='#cccccc')
ax2.grid(axis='y', alpha=0.2, zorder=0)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.set_ylim(0, max(along_errs) + 2)

plt.tight_layout()
plt.savefig('gps_error_direction.pdf', bbox_inches='tight', dpi=300)
plt.savefig('gps_error_direction.png', bbox_inches='tight', dpi=200)
print('Saved gps_error_direction.pdf')
