"""
Vision Performance Analysis Plots for MSc Report
=================================================
Generates publication-quality plots analysing detection performance
as a function of altitude, speed, and camera parameters.

Camera: IMX296 global shutter
  SENSOR_WIDTH_MM  = 5.02
  FOCAL_LENGTH_MM  = 5.46
  IMAGE_W, IMAGE_H = 1456, 1088
  Model input       = 640 x 640
  Inference FPS     = 4.8  (Pi 5, TFLite, XNNPACK)

Dummy height       = 1.8 m

Usage:
    python analysis/vision_performance_plots.py
"""

import os
import sys
import math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

# ── Camera & model parameters ──────────────────────────────────────────
SENSOR_WIDTH_MM  = 5.02
FOCAL_LENGTH_MM  = 5.46
IMAGE_W          = 1456          # sensor pixels (horizontal)
IMAGE_H          = 1088          # sensor pixels (vertical)
MODEL_INPUT      = 640           # YOLOv8 input size (px)
DUMMY_HEIGHT_M   = 1.8           # target height (metres)
FPS              = 4.8           # inference framerate on Pi 5
SHUTTER_S        = 1.0 / 1000   # 1/1000 s exposure

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)))

# ── Derived helpers ─────────────────────────────────────────────────────
HFOV_RAD = 2.0 * math.atan(SENSOR_WIDTH_MM / (2.0 * FOCAL_LENGTH_MM))
HFOV_DEG = math.degrees(HFOV_RAD)

# Sensor aspect ratio
ASPECT = IMAGE_W / IMAGE_H                     # ~1.338
VFOV_RAD = 2.0 * math.atan(math.tan(HFOV_RAD / 2.0) / ASPECT)

def ground_footprint(alt):
    """Return (width_m, height_m) of ground footprint at given altitude."""
    w = 2.0 * alt * math.tan(HFOV_RAD / 2.0)
    h = 2.0 * alt * math.tan(VFOV_RAD / 2.0)
    return w, h

def dummy_px_in_model(alt):
    """Dummy height in MODEL-INPUT pixels (640x640) at given altitude."""
    _, fov_h = ground_footprint(alt)
    # How many sensor pixels the dummy spans vertically
    sensor_px = (DUMMY_HEIGHT_M / fov_h) * IMAGE_H
    # Scale to model input
    scale = MODEL_INPUT / max(IMAGE_W, IMAGE_H)
    return sensor_px * scale

def motion_blur_px(speed, alt):
    """Motion blur in sensor pixels caused by ground-plane motion."""
    gw, _ = ground_footprint(alt)
    gsd = gw / IMAGE_W                         # metres per pixel
    displacement_m = speed * SHUTTER_S
    return displacement_m / gsd

def speed_for_altitude(alt):
    """Adaptive speed: 6 m/s at 20 m, linearly rising to 10 m/s at 50 m."""
    return np.clip(6.0 + (alt - 20.0) * (10.0 - 6.0) / (50.0 - 20.0), 6.0, 10.0)

def frames_in_view(speed, alt):
    """Number of frames the target is inside the FOV (along-track direction)."""
    gw, _ = ground_footprint(alt)
    time_in_view = gw / speed                   # seconds
    return time_in_view * FPS


# ── Style ───────────────────────────────────────────────────────────────
plt.rcParams.update({
    "font.family":       "serif",
    "font.size":         11,
    "axes.titlesize":    13,
    "axes.labelsize":    12,
    "legend.fontsize":   10,
    "figure.dpi":        200,
    "savefig.dpi":       200,
    "axes.grid":         True,
    "grid.alpha":        0.3,
})


# =====================================================================
#  PLOT 1 — Altitude vs Dummy Size in Pixels
# =====================================================================
def plot1_altitude_vs_px():
    alts = np.linspace(15, 80, 200)
    px   = np.array([dummy_px_in_model(a) for a in alts])

    threshold = 20.0
    # Find critical altitude
    idx = np.searchsorted(-px, -threshold)      # first index where px < threshold
    crit_alt = alts[idx] if idx < len(alts) else alts[-1]

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(alts, px, "b-", linewidth=2, label="Dummy height (model input)")
    ax.axhline(threshold, color="r", linestyle="--", linewidth=1.2,
               label=f"Detection threshold ({int(threshold)} px)")
    ax.axvline(crit_alt, color="grey", linestyle=":", linewidth=1,
               label=f"Critical altitude ({crit_alt:.0f} m)")
    ax.fill_between(alts, 0, px, where=(px < threshold),
                    color="red", alpha=0.08)
    ax.set_xlabel("Altitude (m)")
    ax.set_ylabel("Target height in 640x640 input (px)")
    ax.set_title("Target Size vs Altitude (YOLOv8n 640$\\times$640 input)")
    ax.set_xlim(15, 80)
    ax.set_ylim(0, max(px) * 1.1)
    ax.legend(loc="upper right")

    path = os.path.join(OUT_DIR, "plot1_altitude_vs_px.png")
    fig.savefig(path)
    plt.close(fig)
    print(f"  [1/5] {path}  (critical alt = {crit_alt:.1f} m)")


# =====================================================================
#  PLOT 2 — Speed vs Motion Blur
# =====================================================================
def plot2_speed_vs_blur():
    speeds = np.linspace(0, 20, 200)
    alts   = [20, 35, 50]
    colours = ["#2196F3", "#FF9800", "#E91E63"]

    fig, ax = plt.subplots(figsize=(7, 4.5))
    for alt, c in zip(alts, colours):
        blur = np.array([motion_blur_px(s, alt) for s in speeds])
        ax.plot(speeds, blur, color=c, linewidth=2, label=f"{alt} m altitude")

    ax.axhline(1.0, color="grey", linestyle="--", linewidth=1.2,
               label="1 px visible-blur threshold")
    ax.set_xlabel("Drone speed (m/s)")
    ax.set_ylabel("Motion blur (sensor pixels)")
    ax.set_title("Motion Blur vs Speed (1/1000 s exposure, global shutter)")
    ax.set_xlim(0, 20)
    ax.set_ylim(0, None)
    ax.legend(loc="upper left")

    path = os.path.join(OUT_DIR, "plot2_speed_vs_blur.png")
    fig.savefig(path)
    plt.close(fig)
    print(f"  [2/5] {path}")


# =====================================================================
#  PLOT 3 — Speed vs Frames in View
# =====================================================================
def plot3_speed_vs_frames():
    speeds = np.linspace(1, 15, 200)
    alts   = [20, 35, 50]
    colours = ["#2196F3", "#FF9800", "#E91E63"]

    fig, ax = plt.subplots(figsize=(7, 4.5))
    for alt, c in zip(alts, colours):
        fr = np.array([frames_in_view(s, alt) for s in speeds])
        ax.plot(speeds, fr, color=c, linewidth=2, label=f"{alt} m altitude")

    ax.axhline(3.0, color="green", linestyle="--", linewidth=1.2,
               label="3 frames (smart-detect threshold)")
    ax.axhline(1.0, color="red", linestyle="--", linewidth=1.2,
               label="1 frame (minimum)")
    ax.set_xlabel("Drone speed (m/s)")
    ax.set_ylabel("Frames target is visible")
    ax.set_title(f"Target Visibility Duration vs Speed ({FPS} FPS)")
    ax.set_xlim(1, 15)
    ax.set_ylim(0, None)
    ax.legend(loc="upper right")

    path = os.path.join(OUT_DIR, "plot3_speed_vs_frames.png")
    fig.savefig(path)
    plt.close(fig)
    print(f"  [3/5] {path}")


# =====================================================================
#  PLOT 4 — Altitude vs Ground Coverage per Second
# =====================================================================
def plot4_coverage():
    alts = np.linspace(15, 60, 200)

    swaths    = np.array([ground_footprint(a)[1] for a in alts])   # height dim
    widths    = np.array([ground_footprint(a)[0] for a in alts])
    speeds    = np.array([speed_for_altitude(a) for a in alts])
    coverage  = swaths * speeds                                     # m^2 / s

    fig, ax1 = plt.subplots(figsize=(7, 4.5))

    colour1 = "#2196F3"
    colour2 = "#E91E63"

    ax1.plot(alts, coverage, color=colour1, linewidth=2, label="Coverage rate")
    ax1.set_xlabel("Altitude (m)")
    ax1.set_ylabel("Ground coverage (m$^2$/s)", color=colour1)
    ax1.tick_params(axis="y", labelcolor=colour1)
    ax1.set_xlim(15, 60)

    ax2 = ax1.twinx()
    ax2.plot(alts, swaths, color=colour2, linewidth=1.5, linestyle="--",
             label="Swath width")
    ax2.set_ylabel("Swath width (m)", color=colour2)
    ax2.tick_params(axis="y", labelcolor=colour2)

    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

    ax1.set_title("Search Efficiency vs Altitude")

    path = os.path.join(OUT_DIR, "plot4_coverage.png")
    fig.savefig(path)
    plt.close(fig)
    print(f"  [4/5] {path}")


# =====================================================================
#  PLOT 5 — Detection Envelope (2D heatmap)
# =====================================================================
def plot5_detection_envelope():
    speeds = np.linspace(0.5, 15, 150)
    alts   = np.linspace(15, 60, 120)
    S, A   = np.meshgrid(speeds, alts)

    # Target size score (normalised 0-1, capped)
    px_size  = np.vectorize(dummy_px_in_model)(A)
    size_score = np.clip(px_size / 60.0, 0.0, 1.0)     # 60 px = "fully good"

    # Frames in view score
    fiv = np.vectorize(frames_in_view)(S, A)
    frame_score = np.clip(fiv / 5.0, 0.0, 1.0)          # 5 frames = "fully good"

    # Blur penalty
    blur = np.vectorize(motion_blur_px)(S, A)
    blur_frac = np.clip(blur / 5.0, 0.0, 1.0)           # 5 px = totally blurred
    blur_score = 1.0 - blur_frac

    # Combined score (geometric mean-ish)
    score = size_score * frame_score * blur_score

    # Custom red-yellow-green colourmap
    cmap = LinearSegmentedColormap.from_list(
        "det", [(0.85, 0.15, 0.15), (1.0, 0.85, 0.2), (0.15, 0.7, 0.3)])

    fig, ax = plt.subplots(figsize=(7.5, 5))
    im = ax.pcolormesh(S, A, score, cmap=cmap, shading="gouraud",
                       vmin=0, vmax=1)
    cb = fig.colorbar(im, ax=ax, label="Detection score")
    cb.set_ticks([0, 0.25, 0.5, 0.75, 1.0])

    # Contour at 0.5 ("marginal")
    cs = ax.contour(S, A, score, levels=[0.3, 0.5, 0.7],
                    colors=["white", "white", "white"],
                    linewidths=[0.8, 1.2, 0.8],
                    linestyles=[":", "-", ":"])
    ax.clabel(cs, fmt="%.1f", fontsize=9, colors="white")

    ax.set_xlabel("Drone speed (m/s)")
    ax.set_ylabel("Altitude (m)")
    ax.set_title("Detection Performance Envelope")

    path = os.path.join(OUT_DIR, "plot5_detection_envelope.png")
    fig.savefig(path)
    plt.close(fig)
    print(f"  [5/5] {path}")


# ── Main ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    print(f"Camera: {IMAGE_W}x{IMAGE_H}, HFOV={HFOV_DEG:.1f} deg, "
          f"sensor={SENSOR_WIDTH_MM} mm, f={FOCAL_LENGTH_MM} mm")
    print(f"Model input: {MODEL_INPUT}x{MODEL_INPUT}, FPS={FPS}, "
          f"shutter=1/{int(1/SHUTTER_S)} s")
    print(f"Output: {OUT_DIR}\n")

    plot1_altitude_vs_px()
    plot2_speed_vs_blur()
    plot3_speed_vs_frames()
    plot4_coverage()
    plot5_detection_envelope()

    print("\nAll plots saved.")
