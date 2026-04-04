"""Development Timeline / Gantt Chart for SAR Drone Project."""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import numpy as np

# --- Style constants (match project conventions) ---
TEXT_DARK = '#2c3e50'
GRID_COL = '#ecf0f1'

# Category colours
CAT_COLORS = {
    'Software':      '#3498db',   # blue
    'Hardware':      '#2ecc71',   # green
    'Testing':       '#e67e22',   # orange
    'Documentation': '#9b59b6',   # purple
}

# --- Date range ---
start_date = datetime(2026, 2, 2)   # Week 1 Monday
end_date   = datetime(2026, 4, 26)  # end of Week 12

# Helper: week number to date range
def week(n):
    """Return (start, end) dates for project week n (1-indexed, Mon-Sun)."""
    s = start_date + timedelta(weeks=n - 1)
    e = s + timedelta(days=6)
    return s, e

def weeks(a, b):
    """Return (start_of_week_a, end_of_week_b)."""
    s = start_date + timedelta(weeks=a - 1)
    e = start_date + timedelta(weeks=b - 1, days=6)
    return s, e

# --- Tasks: (label, category, start_week, end_week) ---
tasks = [
    # Software
    ('Architecture & state machine design',   'Software', 1, 2),
    ('Simulation (SITL + lawnmower + CV)',     'Software', 3, 4),
    ('Headless mode & web ground station',     'Software', 5, 6),
    ('NCNN optimisation & code refactoring',   'Software', 9, 9),
    ('Safety improvements & bug fixes',        'Software', 10, 10),

    # Hardware
    ('Pi setup & camera testing',              'Hardware', 5, 6),
    ('TFLite inference on Pi verified',        'Hardware', 5, 6),
    ('Cube wiring & MAVLink bridge',           'Hardware', 6, 7),

    # Testing
    ('Bench testing (no props)',               'Testing', 7, 7),
    ('FOV & lens calibration',                 'Testing', 7, 7),
    ('DJI video analysis & FOV validation',    'Testing', 8, 8),
    ('Model retraining v2 (dataset v2)',        'Testing', 8, 8),
    ('Pi field testing & passive detection',   'Testing', 10, 10),
    ('Unit & integration tests (127 tests)',   'Testing', 11, 11),
    ('Demo day preparation',                   'Testing', 12, 12),

    # Documentation
    ('Design rationale & decisions log',       'Documentation', 2, 4),
    ('Flight day checklists & procedures',     'Documentation', 7, 8),
    ('Report writing & documentation blitz',   'Documentation', 11, 12),
]

# --- Milestones: (label, date, y_offset for stagger) ---
# Stagger vertically to avoid label overlap in dense regions
milestones = [
    ('State machine\ncomplete',        start_date + timedelta(weeks=1, days=4),  0),
    ('Simulation\nworking',            start_date + timedelta(weeks=3, days=4),  0),
    ('Pi camera\nverified',            start_date + timedelta(weeks=5, days=2),  0),
    ('Field\nday',                     datetime(2026, 3, 11),                   -1.2),
    ('Model v2\ntrained',             datetime(2026, 3, 16),                    0),
    ('NCNN 4.5x\nspeedup',           datetime(2026, 3, 20),                   -1.2),
    ('Safety\nvalidated',             datetime(2026, 3, 31),                    0),
    ('127 tests\npassing',            datetime(2026, 4, 3),                    -1.2),
    ('Demo\nday',                     datetime(2026, 4, 20),                    0),
]

# Hardware unavailable period
hw_unavail_start = start_date
hw_unavail_end   = start_date + timedelta(weeks=4, days=4)   # end of week 5 Fri

# --- Figure ---
fig, ax = plt.subplots(figsize=(14, 7.5))
fig.subplots_adjust(left=0.28, right=0.96, top=0.90, bottom=0.12)

n_tasks = len(tasks)
bar_height = 0.55

# Draw bars (bottom-up so first task is at top)
for i, (label, cat, sw, ew) in enumerate(tasks):
    y = n_tasks - 1 - i
    s, e = weeks(sw, ew)
    width = (e - s).days
    ax.barh(y, width, left=mdates.date2num(s), height=bar_height,
            color=CAT_COLORS[cat], edgecolor='white', linewidth=0.8,
            zorder=3, alpha=0.88)

# Hardware unavailable shading
ax.axvspan(mdates.date2num(hw_unavail_start), mdates.date2num(hw_unavail_end),
           color='#e74c3c', alpha=0.07, zorder=1, label='Hardware unavailable')
# Red border lines
for d in [hw_unavail_start, hw_unavail_end]:
    ax.axvline(mdates.date2num(d), color='#e74c3c', lw=0.8, ls='--', alpha=0.5, zorder=2)
# Label the shaded region
mid_hw = mdates.date2num(hw_unavail_start) + (mdates.date2num(hw_unavail_end) - mdates.date2num(hw_unavail_start)) / 2
ax.text(mid_hw, n_tasks - 0.3, 'Hardware unavailable',
        ha='center', va='bottom', fontsize=7.5, color='#c0392b',
        fontstyle='italic', zorder=5)

# Milestone diamonds — two rows to avoid overlap
milestone_base_y = -1.6
for label, date, y_off in milestones:
    x = mdates.date2num(date)
    diamond_y = milestone_base_y + y_off
    ax.plot(x, diamond_y, marker='D', markersize=7, color='#e74c3c',
            markeredgecolor=TEXT_DARK, markeredgewidth=0.6, zorder=6)
    # Connector line from diamond down to label
    label_y = diamond_y - 0.45
    ax.text(x, label_y, label, ha='center', va='top',
            fontsize=6.5, color=TEXT_DARK, fontweight='bold',
            linespacing=1.05, zorder=6)

# Milestone row label
ax.text(mdates.date2num(start_date) - 1, milestone_base_y, 'Milestones',
        ha='right', va='center', fontsize=8.5, fontweight='bold', color='#e74c3c')

# --- Axis formatting ---
ax.set_yticks(range(n_tasks))
ax.set_yticklabels([t[0] for t in reversed(tasks)], fontsize=8.5, color=TEXT_DARK)
ax.set_ylim(-5.0, n_tasks + 0.3)

ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=0))  # every Monday
ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
ax.xaxis.set_minor_locator(mdates.DayLocator())
ax.set_xlim(mdates.date2num(start_date - timedelta(days=1)),
            mdates.date2num(end_date + timedelta(days=1)))
plt.setp(ax.get_xticklabels(), rotation=45, ha='right', fontsize=7.5, color='#7f8c8d')
ax.tick_params(axis='y', left=False)

# Week labels along top
ax2 = ax.twiny()
ax2.set_xlim(ax.get_xlim())
week_ticks = []
week_labels = []
for w in range(1, 13):
    s, e = week(w)
    mid = mdates.date2num(s) + 3
    week_ticks.append(mid)
    week_labels.append(f'W{w}')
ax2.set_xticks(week_ticks)
ax2.set_xticklabels(week_labels, fontsize=7.5, color='#7f8c8d', fontweight='bold')
ax2.tick_params(top=False, length=0)
ax2.spines['top'].set_visible(False)

# Grid
ax.set_axisbelow(True)
for w in range(1, 13):
    s, _ = week(w)
    ax.axvline(mdates.date2num(s), color=GRID_COL, lw=0.5, zorder=0)
ax.grid(axis='y', color=GRID_COL, lw=0.5)

# Spines
for spine in ['top', 'right']:
    ax.spines[spine].set_visible(False)
ax.spines['left'].set_color('#ddd')
ax.spines['bottom'].set_color('#ddd')

# Legend
legend_handles = [
    mpatches.Patch(facecolor=CAT_COLORS['Software'], edgecolor='white', label='Software'),
    mpatches.Patch(facecolor=CAT_COLORS['Hardware'], edgecolor='white', label='Hardware'),
    mpatches.Patch(facecolor=CAT_COLORS['Testing'],  edgecolor='white', label='Testing'),
    mpatches.Patch(facecolor=CAT_COLORS['Documentation'], edgecolor='white', label='Documentation'),
    mpatches.Patch(facecolor='#e74c3c', alpha=0.15, edgecolor='#e74c3c',
                   linestyle='--', label='Hardware unavailable'),
    plt.Line2D([0], [0], marker='D', color='w', markerfacecolor='#e74c3c',
               markeredgecolor=TEXT_DARK, markersize=7, label='Milestone'),
]
ax.legend(handles=legend_handles, loc='lower right', fontsize=7.5,
          framealpha=0.9, edgecolor='#ddd', ncol=3)

# Title
ax.set_title('SAR Drone Development Timeline', fontsize=14, fontweight='bold',
             color=TEXT_DARK, pad=25)

# --- Save ---
out_base = 'c:/Users/Bristol/Desktop/AI for Robotics/v3/report/figs/development_timeline'
plt.savefig(f'{out_base}.pdf', bbox_inches='tight', dpi=300)
plt.savefig(f'{out_base}.png', bbox_inches='tight', dpi=300)
print('OK: development_timeline.pdf + .png')
