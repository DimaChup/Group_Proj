"""
video_test_compare.py — A/B Model Comparison on DJI Flight Video

WHAT:    Same as video_test.py (tiled detection, SRT telemetry, GPS estimation,
         scatter plots, measure tool, CSV logging) but loads TWO models and lets
         you switch between them live with the M key. The HUD shows which model
         is active. Useful for comparing detection performance (confidence, miss
         rate, GPS accuracy) between model variants on identical footage.
WHY:     Enables direct A/B comparison of different YOLO models on the same
         flight video. Switch instantly between e.g. the original 640-trained
         model and the v2 1088-retrained model to see which detects better at
         various altitudes and positions.
WHEN:    After training a new model, to compare it against the baseline on real
         flight footage. When deciding which model to deploy on Pi.
WHERE:   Laptop only (requires display for multi-window visualization).
ENV:     "test_env" (needs both ultralytics and tflite for VisionSystem)
MODELS:  Two models: --model (default best.tflite) and --model2 (default
         cv_models/sar_v2_1088/best.tflite). Press M to switch live.
RISK:    None — offline video analysis, no commands sent.

USAGE:
    python tests/laptop/video_test_compare.py "RealVideo/DJI_0001_1456x1088_cropped_30fps.mp4"
    python tests/laptop/video_test_compare.py "RealVideo/DJI_0001_1456x1088_cropped_30fps.mp4" --model best.tflite --model2 cv_models/sar_v2_1088/best.tflite

FLAGS:
    video               Path to video file (positional, required)
    --model PATH        Model 1 path (default: best.tflite)
    --model2 PATH       Model 2 path (default: cv_models/sar_v2_1088/best.tflite)
    --save PATH         Save output video to file
    --conf FLOAT        Confidence threshold (default: 0.3)
    --every N           Run AI every Nth frame (default: 3)
    --tile-size N       Tile size in pixels (default: 640)
    --display-width N   Display window width (default: 960)
    --srt PATH          SRT telemetry file (auto-detected if not set)

OUTPUT:
    Multi-window display: video + detections, GPS scatter plots, best snapshot.
    CSV file: <video_name>_detections.csv with per-detection GPS estimates.
    Console: active model name, detection count, CEP50 on exit.

BEST PRACTICES:
    - MUST use 30fps video (DJI_0001_1456x1088_cropped_30fps.mp4)
    - Press M to switch models — note detection differences
    - GPS estimates accumulate across both models (same CSV)
    - Compare confidence levels and miss rates between models

DEPENDENCIES:
    opencv-python, numpy, vision.py (VisionSystem), csv, threading
"""
import sys, os, time, argparse, threading, csv
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import cv2
import numpy as np
import re, math
from vision import VisionSystem


# ─── SRT telemetry parser ───

def parse_srt(srt_path):
    """Parse DJI SRT file → dict of frame_num → {lat, lon, rel_alt, abs_alt, yaw, pitch}"""
    with open(srt_path, 'r') as f:
        text = f.read()
    entries = re.findall(
        r'FrameCnt:\s*(\d+)[\s\S]*?'
        r'latitude:\s*([\d.-]+)\][\s\S]*?'
        r'longitude:\s*([\d.-]+)\][\s\S]*?'
        r'rel_alt:\s*([\d.-]+)\s+abs_alt:\s*([\d.-]+)\][\s\S]*?'
        r'gb_yaw:\s*([\d.-]+)\s+gb_pitch:\s*([\d.-]+)',
        text
    )
    telem = {}
    for e in entries:
        telem[int(e[0])] = {
            'lat': float(e[1]), 'lon': float(e[2]),
            'rel_alt': float(e[3]), 'abs_alt': float(e[4]),
            'yaw': float(e[5]), 'pitch': float(e[6])
        }
    return telem


def find_srt(video_path):
    """Try to find matching SRT file for a video."""
    base = os.path.splitext(video_path)[0]
    # Direct match
    for ext in ['.SRT', '.srt']:
        if os.path.exists(base + ext):
            return base + ext
    # DJI naming: video might be cropped/renamed, look for original SRT
    vdir = os.path.dirname(video_path)
    for f in os.listdir(vdir):
        if f.upper().endswith('.SRT'):
            return os.path.join(vdir, f)
    return None


def estimate_target_gps(drone_lat, drone_lon, alt, yaw, pixel_x, pixel_y, img_w, img_h, fov_h=54.4):
    """Estimate target GPS from drone position + pixel offset. Returns (lat, lon)."""
    fov_h_rad = math.radians(fov_h)
    ground_w = 2 * alt * math.tan(fov_h_rad / 2)
    ground_h = ground_w * img_h / img_w
    # Pixel offset from center in meters
    dx_m = (pixel_x - img_w / 2) / img_w * ground_w
    dy_m = -(pixel_y - img_h / 2) / img_h * ground_h  # negative because y is down
    # Rotate by yaw
    yaw_rad = math.radians(yaw)
    north_m = dy_m * math.cos(yaw_rad) - dx_m * math.sin(yaw_rad)
    east_m = dy_m * math.sin(yaw_rad) + dx_m * math.cos(yaw_rad)
    # Convert to GPS offset
    target_lat = drone_lat + north_m / 111320.0
    target_lon = drone_lon + east_m / (111320.0 * math.cos(math.radians(drone_lat)))
    return target_lat, target_lon


# ─── Tiling helpers (from zoom_detect.py) ───

def tile_detect(vs, frame, tile_size=640, overlap=0.25, conf_thresh=0.3):
    """Split frame into overlapping tiles, detect in each, merge with NMS."""
    h, w = frame.shape[:2]
    stride = int(tile_size * (1 - overlap))
    detections = []

    for y0 in range(0, h - tile_size // 2, stride):
        for x0 in range(0, w - tile_size // 2, stride):
            x1 = min(x0, w - tile_size)
            y1 = min(y0, h - tile_size)
            x2 = min(x1 + tile_size, w)
            y2 = min(y1 + tile_size, h)
            x1, y1 = max(0, x1), max(0, y1)

            tile = frame[y1:y2, x1:x2].copy()
            th, tw = tile.shape[:2]
            # Pad to square to avoid stretch distortion in YOLO
            if tw != th:
                sq = max(tw, th)
                padded = np.zeros((sq, sq, 3), dtype=tile.dtype)
                padded[:th, :tw] = tile
                found, tx, ty, conf = vs.detect_in_image(padded)
                # Only accept if detection is within the real tile area
                if found and conf >= conf_thresh and tx < tw and ty < th:
                    bw = vs.last_bbox_w
                    bh = vs.last_bbox_h
                    detections.append((x1 + tx, y1 + ty, bw, bh, conf))
            else:
                found, tx, ty, conf = vs.detect_in_image(tile)
                if found and conf >= conf_thresh:
                    bw = vs.last_bbox_w
                    bh = vs.last_bbox_h
                    detections.append((x1 + tx, y1 + ty, bw, bh, conf))

    if len(detections) > 1:
        detections = nms(detections, iou_thresh=0.3)
    return detections


def nms(dets, iou_thresh=0.3):
    boxes = [(cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2, conf)
             for cx, cy, w, h, conf in dets]
    boxes.sort(key=lambda b: b[4], reverse=True)
    keep = []
    while boxes:
        best = boxes.pop(0)
        keep.append(best)
        boxes = [b for b in boxes if iou_calc(best, b) < iou_thresh]
    return [((x1 + x2) // 2, (y1 + y2) // 2, x2 - x1, y2 - y1, conf)
            for x1, y1, x2, y2, conf in keep]


def iou_calc(a, b):
    xi1, yi1 = max(a[0], b[0]), max(a[1], b[1])
    xi2, yi2 = min(a[2], b[2]), min(a[3], b[3])
    inter = max(0, xi2 - xi1) * max(0, yi2 - yi1)
    area_a = (a[2] - a[0]) * (a[3] - a[1])
    area_b = (b[2] - b[0]) * (b[3] - b[1])
    union = area_a + area_b - inter
    return inter / union if union > 0 else 0


def main():
    # Force NCNN backend before argparse
    _ncnn_injected = False
    if "--backend" not in sys.argv:
        sys.argv.extend(["--backend", "ncnn"])
        _ncnn_injected = True

    parser = argparse.ArgumentParser(description="NCNN video detection (v2-1088 model)")
    parser.add_argument("video", nargs="?", default="RealVideo/DJI_0001_1456x1088_cropped_30fps.mp4", help="Video file")
    parser.add_argument("--model", default="cv_models/sar_v2_1088/best.tflite", help="Model 1 (NCNN)")
    parser.add_argument("--model2", default="cv_models/sar_v2_1088/best.tflite", help="Model 2 (NCNN)")
    parser.add_argument("--backend", default="ncnn", help=argparse.SUPPRESS)  # absorb the injected flag
    parser.add_argument("--save", default=None, help="Save output video to file")
    parser.add_argument("--conf", type=float, default=0.3, help="Confidence threshold (default 0.3)")
    parser.add_argument("--every", type=int, default=3, help="Run AI every Nth frame (default 3)")
    parser.add_argument("--tile-size", type=int, default=640, help="Tile size (default 640)")
    parser.add_argument("--display-width", type=int, default=960, help="Display window width (default 960)")
    parser.add_argument("--srt", default=None, help="SRT telemetry file (auto-detected if not set)")
    args = parser.parse_args()

    if not os.path.exists(args.video):
        print(f"Video not found: {args.video}")
        return

    # Show loading screen immediately
    win = "Video Detection Test"
    cv2.namedWindow(win, cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
    splash = np.zeros((200, 500, 3), dtype=np.uint8)
    cv2.putText(splash, f"Loading {os.path.basename(args.model)}...", (30, 110),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (200, 200, 200), 2)
    cv2.imshow(win, splash)
    cv2.waitKey(1)

    # Load both models
    models = {}
    model_names = {}
    for i, (path, label) in enumerate([(args.model, "Model 1"), (args.model2, "Model 2")]):
        if os.path.exists(path):
            v = VisionSystem(camera_index=None, model_path=path)
            if v.using_ai:
                models[i] = v
                model_names[i] = f"{label}: {os.path.basename(path)} ({os.path.getsize(path)/1024/1024:.1f}MB)"
                print(f"  Loaded {model_names[i]}")
            else:
                print(f"  Failed to load {path}")
        else:
            print(f"  {path} not found, skipping")

    if not models:
        print("No models loaded!")
        return

    active_model = [0]  # index into models dict
    vs = models[active_model[0]]
    print(f"\nActive: {model_names[active_model[0]]}")
    print(f"Press M to switch models\n")

    cap = cv2.VideoCapture(args.video)
    if not cap.isOpened():
        print(f"Cannot open video: {args.video}")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    vid_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    vid_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration = total_frames / fps if fps > 0 else 0

    disp_scale = args.display_width / vid_w
    disp_w = args.display_width
    disp_h = int(vid_h * disp_scale)

    # Load SRT telemetry
    srt_path = args.srt or find_srt(args.video)
    telem = {}
    if srt_path and os.path.exists(srt_path):
        telem = parse_srt(srt_path)
        print(f"SRT loaded: {srt_path} ({len(telem)} entries)")
    else:
        print("No SRT file found — no telemetry overlay")

    print(f"Video: {vid_w}x{vid_h} @ {fps:.1f}fps, {total_frames} frames ({duration:.1f}s)")
    print(f"Model: {args.model}")
    print(f"Tiling: {args.tile_size}px (every {args.every} frames)")
    print(f"Display at: {disp_w}x{disp_h}")
    print("Controls: SPACE=pause  Q=quit  A/D=skip 5s  +/-=speed  T=toggle tiling")
    print()

    writer = None
    if args.save:
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(args.save, fourcc, fps, (disp_w, disp_h))
        print(f"Saving to: {args.save}")

    # GPS scatter plot of all target estimates
    target_estimates = []  # list of (lat, lon, conf, frame_num, center_dist, alt)
    best_snapshot = [None]  # snapshot of the most central detection
    best_center_dist = [999.0]
    # CSV log for later analysis
    csv_path = os.path.splitext(args.video)[0] + "_detections.csv"
    csv_file = open(csv_path, 'w', newline='')
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow([
        'frame', 'timestamp_s', 'conf',
        'det_px_x', 'det_px_y', 'det_w', 'det_h',
        'center_dist', 'drone_lat', 'drone_lon', 'drone_alt_m', 'drone_yaw',
        'target_lat', 'target_lon'
    ])
    print(f"CSV log: {csv_path}")

    plot_size = 400

    def heat_color(val):
        """0.0=green, 1.0=red. Returns BGR tuple."""
        g = int(255 * max(0, 1 - val))
        r = int(255 * min(1, val))
        return (0, g, r)

    def draw_gps_plot_by_center():
        """GPS scatter colored by distance from image center."""
        plot = np.zeros((plot_size, plot_size, 3), dtype=np.uint8)
        if not target_estimates:
            cv2.putText(plot, "No detections yet", (80, plot_size // 2),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 100), 1)
            return plot

        lats = [e[0] for e in target_estimates]
        lons = [e[1] for e in target_estimates]
        mean_lat = sum(lats) / len(lats)
        mean_lon = sum(lons) / len(lons)

        pts_m = []
        for lat, lon, conf, fnum, cdist, alt in target_estimates:
            north = (lat - mean_lat) * 111320
            east = (lon - mean_lon) * 111320 * math.cos(math.radians(mean_lat))
            pts_m.append((east, north, cdist, alt))

        max_range = max(max(abs(p[0]) for p in pts_m) * 2, max(abs(p[1]) for p in pts_m) * 2, 20.0)
        margin = 50
        usable = plot_size - 2 * margin
        scale = usable / max_range

        # Grid
        grid_step = 5 if max_range < 50 else 10
        for d in range(-int(max_range), int(max_range) + 1, grid_step):
            px = int(plot_size / 2 + d * scale)
            py = int(plot_size / 2 - d * scale)
            if margin < px < plot_size - margin:
                cv2.line(plot, (px, margin), (px, plot_size - margin), (25, 25, 25), 1)
            if margin < py < plot_size - margin:
                cv2.line(plot, (margin, py), (plot_size - margin, py), (25, 25, 25), 1)

        # Crosshair
        cv2.line(plot, (plot_size // 2 - 8, plot_size // 2), (plot_size // 2 + 8, plot_size // 2), (60, 60, 60), 1)
        cv2.line(plot, (plot_size // 2, plot_size // 2 - 8), (plot_size // 2, plot_size // 2 + 8), (60, 60, 60), 1)

        # Plot points colored by center distance
        for east, north, cdist, alt in pts_m:
            px = int(plot_size / 2 + east * scale)
            py = int(plot_size / 2 - north * scale)
            color = heat_color(min(1.0, cdist))  # 0=center=green, 1=edge=red
            cv2.circle(plot, (px, py), 5, color, -1)
            cv2.circle(plot, (px, py), 5, (255, 255, 255), 1)

        # Stats
        dists_m = [math.sqrt(p[0]**2 + p[1]**2) for p in pts_m]
        cep50 = sorted(dists_m)[len(dists_m) // 2] if len(dists_m) > 1 else 0

        # Labels
        cv2.putText(plot, "Color = distance from image center", (8, 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.40, (150, 150, 150), 1)
        cv2.putText(plot, "GREEN=center  RED=edge", (8, 40),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.40, (150, 150, 150), 1)
        max_spread = max(dists_m) if dists_m else 0
        mean_err = sum(dists_m) / len(dists_m) if dists_m else 0
        cv2.putText(plot, f"N={len(target_estimates)}  Grid={grid_step}m", (8, plot_size - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.35, (100, 100, 100), 1)
        cv2.putText(plot, f"CEP50: {cep50:.1f}m | Max: {max_spread:.1f}m | Avg: {mean_err:.1f}m", (8, plot_size - 28),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.40, (0, 200, 255), 1)
        cv2.putText(plot, f"Mean: {mean_lat:.6f}, {mean_lon:.6f}", (8, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.40, (0, 255, 0), 1)

        # Color bar legend on right
        bar_x = plot_size - 25
        for i in range(margin, plot_size - margin):
            val = (i - margin) / usable
            c = heat_color(val)
            cv2.line(plot, (bar_x, i), (bar_x + 15, i), c, 1)
        cv2.putText(plot, "ctr", (bar_x - 5, margin - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 255, 0), 1)
        cv2.putText(plot, "edge", (bar_x - 10, plot_size - margin + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 255), 1)

        # Best estimate — lowest center_dist
        if len(target_estimates) > 2:
            best = min(target_estimates, key=lambda e: e[4])  # min center_dist
            b_lat, b_lon, b_conf, b_fnum, b_cdist, b_alt = best
            b_north = (b_lat - mean_lat) * 111320
            b_east = (b_lon - mean_lon) * 111320 * math.cos(math.radians(mean_lat))
            bpx = int(plot_size / 2 + b_east * scale)
            bpy = int(plot_size / 2 - b_north * scale)
            # Star marker for best estimate
            cv2.drawMarker(plot, (bpx, bpy), (255, 255, 0), cv2.MARKER_STAR, 18, 2)
            cv2.putText(plot, f"BEST EST: {b_lat:.6f}, {b_lon:.6f}", (8, 80),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.38, (255, 255, 0), 1)
            cv2.putText(plot, f"Frame {b_fnum} | Alt {b_alt:.0f}m | CtrDist {b_cdist:.2f}", (8, 98),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.36, (255, 255, 0), 1)

            # DRONE GPS at most central frame — "true" dummy position
            drone_data = telem.get(b_fnum)
            if drone_data:
                d_north = (drone_data['lat'] - mean_lat) * 111320
                d_east = (drone_data['lon'] - mean_lon) * 111320 * math.cos(math.radians(mean_lat))
                dpx = int(plot_size / 2 + d_east * scale)
                dpy = int(plot_size / 2 - d_north * scale)
                cv2.drawMarker(plot, (dpx, dpy), (255, 0, 255), cv2.MARKER_DIAMOND, 20, 3)
                cv2.circle(plot, (dpx, dpy), 25, (255, 0, 255), 2)
                cv2.putText(plot, f"DRONE GPS: {drone_data['lat']:.6f}, {drone_data['lon']:.6f}", (8, 116),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.38, (255, 0, 255), 1)

        return plot

    def draw_gps_plot_by_alt():
        """GPS scatter colored by altitude."""
        plot = np.zeros((plot_size, plot_size, 3), dtype=np.uint8)
        if not target_estimates:
            cv2.putText(plot, "No detections yet", (80, plot_size // 2),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 100), 1)
            return plot

        lats = [e[0] for e in target_estimates]
        lons = [e[1] for e in target_estimates]
        alts = [e[5] for e in target_estimates]
        mean_lat = sum(lats) / len(lats)
        mean_lon = sum(lons) / len(lons)
        min_alt = min(alts)
        max_alt = max(alts)
        alt_range = max(max_alt - min_alt, 1.0)

        pts_m = []
        for lat, lon, conf, fnum, cdist, alt in target_estimates:
            north = (lat - mean_lat) * 111320
            east = (lon - mean_lon) * 111320 * math.cos(math.radians(mean_lat))
            pts_m.append((east, north, cdist, alt))

        max_range = max(max(abs(p[0]) for p in pts_m) * 2, max(abs(p[1]) for p in pts_m) * 2, 20.0)
        margin = 50
        usable = plot_size - 2 * margin
        scale = usable / max_range

        # Grid
        grid_step = 5 if max_range < 50 else 10
        for d in range(-int(max_range), int(max_range) + 1, grid_step):
            px = int(plot_size / 2 + d * scale)
            py = int(plot_size / 2 - d * scale)
            if margin < px < plot_size - margin:
                cv2.line(plot, (px, margin), (px, plot_size - margin), (25, 25, 25), 1)
            if margin < py < plot_size - margin:
                cv2.line(plot, (margin, py), (plot_size - margin, py), (25, 25, 25), 1)

        # Crosshair
        cv2.line(plot, (plot_size // 2 - 8, plot_size // 2), (plot_size // 2 + 8, plot_size // 2), (60, 60, 60), 1)
        cv2.line(plot, (plot_size // 2, plot_size // 2 - 8), (plot_size // 2, plot_size // 2 + 8), (60, 60, 60), 1)

        # Plot points colored by altitude (low=green, high=red)
        for east, north, cdist, alt in pts_m:
            px = int(plot_size / 2 + east * scale)
            py = int(plot_size / 2 - north * scale)
            alt_norm = (alt - min_alt) / alt_range
            color = heat_color(alt_norm)
            cv2.circle(plot, (px, py), 5, color, -1)
            cv2.circle(plot, (px, py), 5, (255, 255, 255), 1)

        # Stats
        dists_m = [math.sqrt(p[0]**2 + p[1]**2) for p in pts_m]
        cep50 = sorted(dists_m)[len(dists_m) // 2] if len(dists_m) > 1 else 0

        # Labels
        cv2.putText(plot, "Color = drone altitude (AGL)", (8, 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.40, (150, 150, 150), 1)
        cv2.putText(plot, f"GREEN={min_alt:.0f}m  RED={max_alt:.0f}m", (8, 40),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.40, (150, 150, 150), 1)
        max_spread = max(dists_m) if dists_m else 0
        mean_err = sum(dists_m) / len(dists_m) if dists_m else 0
        cv2.putText(plot, f"N={len(target_estimates)}  Grid={grid_step}m", (8, plot_size - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.35, (100, 100, 100), 1)
        cv2.putText(plot, f"CEP50: {cep50:.1f}m | Max: {max_spread:.1f}m | Avg: {mean_err:.1f}m", (8, plot_size - 28),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.40, (0, 200, 255), 1)
        cv2.putText(plot, f"Mean: {mean_lat:.6f}, {mean_lon:.6f}", (8, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.40, (0, 255, 0), 1)

        # Color bar legend on right
        bar_x = plot_size - 25
        for i in range(margin, plot_size - margin):
            val = (i - margin) / usable
            c = heat_color(val)
            cv2.line(plot, (bar_x, i), (bar_x + 15, i), c, 1)
        cv2.putText(plot, f"{min_alt:.0f}m", (bar_x - 12, margin - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 255, 0), 1)
        cv2.putText(plot, f"{max_alt:.0f}m", (bar_x - 12, plot_size - margin + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 255), 1)

        # Best estimate — lowest center_dist (same as center plot)
        if len(target_estimates) > 2:
            best = min(target_estimates, key=lambda e: e[4])
            b_lat, b_lon, b_conf, b_fnum, b_cdist, b_alt = best
            b_north = (b_lat - mean_lat) * 111320
            b_east = (b_lon - mean_lon) * 111320 * math.cos(math.radians(mean_lat))
            bpx = int(plot_size / 2 + b_east * scale)
            bpy = int(plot_size / 2 - b_north * scale)
            cv2.drawMarker(plot, (bpx, bpy), (255, 255, 0), cv2.MARKER_STAR, 18, 2)
            cv2.putText(plot, f"BEST EST: {b_lat:.6f}, {b_lon:.6f}", (8, 80),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.38, (255, 255, 0), 1)
            cv2.putText(plot, f"Frame {b_fnum} | Alt {b_alt:.0f}m | CtrDist {b_cdist:.2f}", (8, 98),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.36, (255, 255, 0), 1)

            # DRONE GPS at most central frame
            drone_data = telem.get(b_fnum)
            if drone_data:
                d_north = (drone_data['lat'] - mean_lat) * 111320
                d_east = (drone_data['lon'] - mean_lon) * 111320 * math.cos(math.radians(mean_lat))
                dpx = int(plot_size / 2 + d_east * scale)
                dpy = int(plot_size / 2 - d_north * scale)
                cv2.drawMarker(plot, (dpx, dpy), (255, 0, 255), cv2.MARKER_DIAMOND, 20, 3)
                cv2.circle(plot, (dpx, dpy), 25, (255, 0, 255), 2)
                cv2.putText(plot, f"DRONE GPS: {drone_data['lat']:.6f}, {drone_data['lon']:.6f}", (8, 116),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.38, (255, 0, 255), 1)

        return plot

    # Threaded tiling inference
    ai_lock = threading.Lock()
    ai_result = {"dets": [], "dt": 0, "busy": False, "frame_num": -1, "snapshot": None, "info_lines": []}
    det_count = [0]
    use_tiling = [True]

    def make_snapshot(frame_copy, dets, fnum, dt):
        """Draw detection boxes + telemetry on a snapshot of the inference frame."""
        snap = frame_copy.copy()
        h_snap, w_snap = snap.shape[:2]
        # Crosshair at image center
        img_cx, img_cy = w_snap // 2, h_snap // 2
        cv2.line(snap, (img_cx - 30, img_cy), (img_cx + 30, img_cy), (0, 255, 255), 2)
        cv2.line(snap, (img_cx, img_cy - 30), (img_cx, img_cy + 30), (0, 255, 255), 2)

        for cx, cy, w, h, conf in dets:
            cv2.rectangle(snap, (cx - w // 2, cy - h // 2), (cx + w // 2, cy + h // 2), (0, 255, 0), 4)
            cls_label = getattr(vs, 'last_class_name', '') or ''
            det_label = f"{conf:.2f} [{cls_label}]" if cls_label else f"{conf:.2f}"
            cv2.putText(snap, det_label, (cx - w // 2, cy - h // 2 - 15),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
            # Pink dot at detection center
            cv2.circle(snap, (cx, cy), 10, (255, 0, 255), -1)
            cv2.circle(snap, (cx, cy), 10, (255, 255, 255), 2)
            # Bright line from image center to detection center
            cv2.line(snap, (img_cx, img_cy), (cx, cy), (255, 0, 255), 3)
            # Distance label at midpoint of line
            mid_x = (img_cx + cx) // 2
            mid_y = (img_cy + cy) // 2
            px_dist = math.sqrt((cx - img_cx)**2 + (cy - img_cy)**2)
            cv2.putText(snap, f"{px_dist:.0f}px", (mid_x + 10, mid_y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 255), 2)
        # Save clean version (no text banner) for display
        snap_clean = snap.copy()

        # Track best (most central) snapshot (clean, no banner)
        if dets:
            t_data = telem.get(fnum)
            if t_data:
                cx_norm = (dets[0][0] - vid_w / 2) / (vid_w / 2)
                cy_norm = (dets[0][1] - vid_h / 2) / (vid_h / 2)
                center_dist = math.sqrt(cx_norm**2 + cy_norm**2)
                if center_dist < best_center_dist[0]:
                    best_center_dist[0] = center_dist
                    best_snapshot[0] = snap_clean.copy()

        # Build text lines for bottom banner
        lines = [f"Frame {fnum} | {dt:.0f}ms"]
        t_data = telem.get(fnum)
        if t_data:
            lines.append(f"DRONE  Alt: {t_data['rel_alt']:.1f}m   Yaw: {t_data['yaw']:.0f}")
            lines.append(f"DRONE  {t_data['lat']:.6f}, {t_data['lon']:.6f}")
            if dets:
                t_lat, t_lon = estimate_target_gps(
                    t_data['lat'], t_data['lon'], t_data['rel_alt'],
                    t_data['yaw'], dets[0][0], dets[0][1], vid_w, vid_h
                )
                lines.append(f"TARGET {t_lat:.6f}, {t_lon:.6f}")
                # Calculate offset from center in meters
                fov_h_rad = math.radians(54.4)
                ground_w = 2 * t_data['rel_alt'] * math.tan(fov_h_rad / 2)
                ground_h = ground_w * vid_h / vid_w
                dx_px = dets[0][0] - vid_w / 2
                dy_px = dets[0][1] - vid_h / 2
                dx_m = dx_px / vid_w * ground_w
                dy_m = dy_px / vid_h * ground_h
                offset_m = math.sqrt(dx_m**2 + dy_m**2)
                lines.append(f"OFFSET {offset_m:.1f}m from center ({dx_m:.1f}m E, {dy_m:.1f}m S)")
                # Distance from image center (0=center, 1=corner)
                cx_norm = (dets[0][0] - vid_w / 2) / (vid_w / 2)
                cy_norm = (dets[0][1] - vid_h / 2) / (vid_h / 2)
                center_dist = math.sqrt(cx_norm**2 + cy_norm**2)
                target_estimates.append((t_lat, t_lon, dets[0][4], fnum, center_dist, t_data['rel_alt']))
                # Write to CSV
                csv_writer.writerow([
                    fnum, f"{fnum / fps:.2f}", f"{dets[0][4]:.3f}",
                    dets[0][0], dets[0][1], dets[0][2], dets[0][3],
                    f"{center_dist:.3f}",
                    f"{t_data['lat']:.7f}", f"{t_data['lon']:.7f}",
                    f"{t_data['rel_alt']:.1f}", f"{t_data['yaw']:.1f}",
                    f"{t_lat:.7f}", f"{t_lon:.7f}"
                ])
                csv_file.flush()
        # Draw black banner at bottom with large text
        line_h = 50
        banner_h = line_h * len(lines) + 20
        cv2.rectangle(snap, (0, h_snap - banner_h), (w_snap, h_snap), (0, 0, 0), -1)
        for i, line in enumerate(lines):
            if "TARGET" in line:
                color = (0, 255, 0)
            elif "DRONE" in line:
                color = (200, 200, 200)
            else:
                color = (0, 255, 255)
            y_pos = h_snap - banner_h + 40 + i * line_h
            cv2.putText(snap, line, (15, y_pos),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.3, color, 3)
        return snap_clean, lines

    def run_tiled_inference(frame_copy, fnum):
        t0 = time.perf_counter()
        dets = tile_detect(vs, frame_copy, args.tile_size, overlap=0.25, conf_thresh=args.conf)
        dt = (time.perf_counter() - t0) * 1000
        if dets:
            det_count[0] += 1
        snap_clean, info_lines = make_snapshot(frame_copy, dets, fnum, dt)
        with ai_lock:
            ai_result["dets"] = dets
            ai_result["dt"] = dt
            ai_result["frame_num"] = fnum
            ai_result["snapshot"] = snap_clean
            ai_result["info_lines"] = info_lines
            ai_result["busy"] = False

    def run_single_inference(frame_copy, fnum):
        infer_frame = cv2.resize(frame_copy, (640, int(vid_h * 640 / vid_w)))
        t0 = time.perf_counter()
        found, x, y, conf = vs.detect_in_image(infer_frame)
        dt = (time.perf_counter() - t0) * 1000
        dets = []
        if found and conf >= args.conf:
            scale = vid_w / 640
            bw = vs.last_bbox_w * scale
            bh = vs.last_bbox_h * scale
            dets = [(int(x * scale), int(y * scale), int(bw), int(bh), conf)]
            det_count[0] += 1
        snap_clean, info_lines = make_snapshot(frame_copy, dets, fnum, dt)
        with ai_lock:
            ai_result["dets"] = dets
            ai_result["dt"] = dt
            ai_result["frame_num"] = fnum
            ai_result["snapshot"] = snap_clean
            ai_result["info_lines"] = info_lines
            ai_result["busy"] = False

    # ── Weather / lighting simulation effects ──────────────────────────
    # Press W to cycle effects, E to increase intensity, R to decrease
    EFFECTS = [
        "none",
        "overcast",      # reduced brightness + contrast
        "bright_sun",    # high brightness + slight washout
        "dusk",          # warm orange tint + darkened
        "fog",           # white haze overlay
        "rain",          # dark + streaks + slight blur
        "night",         # very dark + blue tint
        "shadow",        # patchy dark areas (partial shade)
        "snow_glare",    # bright + blue-white tint
    ]
    active_effect = [0]     # index into EFFECTS
    effect_intensity = [0.5]  # 0.0-1.0
    print("Weather:  W=cycle effect  E=increase intensity  R=decrease intensity")
    print(f"Effects:  {', '.join(EFFECTS)}")

    def apply_weather_effect(img):
        """Apply weather/lighting effect to frame BEFORE feeding to model."""
        effect = EFFECTS[active_effect[0]]
        intensity = effect_intensity[0]
        if effect == "none":
            return img

        out = img.astype(np.float32)
        h, w = out.shape[:2]

        if effect == "overcast":
            # Reduce brightness and contrast
            out = out * (1.0 - 0.4 * intensity) + 20 * intensity
            # Slight desaturation
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            gray3 = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR).astype(np.float32)
            out = out * (1.0 - 0.3 * intensity) + gray3 * 0.3 * intensity

        elif effect == "bright_sun":
            # High brightness + slight washout
            out = out * (1.0 + 0.5 * intensity) + 30 * intensity

        elif effect == "dusk":
            # Warm orange tint + darkened
            out *= (1.0 - 0.5 * intensity)
            out[:, :, 2] += 40 * intensity  # red
            out[:, :, 1] += 15 * intensity  # slight green
            out[:, :, 0] -= 20 * intensity  # less blue

        elif effect == "fog":
            # White haze overlay
            fog_layer = np.full_like(out, 220)
            out = out * (1.0 - 0.6 * intensity) + fog_layer * 0.6 * intensity
            # Slight blur
            ksize = int(3 + 4 * intensity) | 1  # odd kernel
            out = cv2.GaussianBlur(out, (ksize, ksize), 0)

        elif effect == "rain":
            # Darken + motion blur streaks + noise
            out *= (1.0 - 0.3 * intensity)
            # Vertical streaks
            num_streaks = int(200 * intensity)
            for _ in range(num_streaks):
                x = np.random.randint(0, w)
                y = np.random.randint(0, h)
                length = np.random.randint(10, 40)
                cv2.line(out, (x, y), (x + np.random.randint(-2, 3), y + length),
                        (180, 180, 200), 1, cv2.LINE_AA)
            # Slight blur (wet lens)
            ksize = int(1 + 2 * intensity) | 1
            out = cv2.GaussianBlur(out, (ksize, ksize), 0)

        elif effect == "night":
            # Very dark + blue tint
            out *= (0.15 + 0.15 * (1 - intensity))
            out[:, :, 0] += 15 * intensity  # blue tint
            # Add noise
            noise = np.random.normal(0, 8 * intensity, out.shape).astype(np.float32)
            out += noise

        elif effect == "shadow":
            # Patchy dark areas (partial shade from clouds/trees)
            shadow_mask = np.ones((h, w), dtype=np.float32)
            num_shadows = int(3 + 5 * intensity)
            for _ in range(num_shadows):
                cx = np.random.randint(0, w)
                cy = np.random.randint(0, h)
                rx = np.random.randint(w // 6, w // 3)
                ry = np.random.randint(h // 6, h // 3)
                cv2.ellipse(shadow_mask, (cx, cy), (rx, ry), 0, 0, 360,
                           0.4 + 0.3 * (1 - intensity), -1)
            shadow_mask = cv2.GaussianBlur(shadow_mask, (51, 51), 0)
            out *= shadow_mask[:, :, np.newaxis]

        elif effect == "snow_glare":
            # Bright + blue-white tint
            out *= (1.0 + 0.3 * intensity)
            out[:, :, 0] += 30 * intensity  # blue
            out[:, :, 1] += 20 * intensity  # green
            out[:, :, 2] += 10 * intensity  # less red

        return np.clip(out, 0, 255).astype(np.uint8)

    paused = False
    speed = 1.0
    frame_num = 0
    frame = None
    need_detect = [False]  # flag to trigger detection on current frame

    def on_trackbar(pos):
        nonlocal frame, frame_num
        cap.set(cv2.CAP_PROP_POS_FRAMES, pos)
        ret, f = cap.read()
        if ret:
            frame = f
            frame_num = pos
            need_detect[0] = True
    cv2.createTrackbar("Position", win, 0, total_frames - 1, on_trackbar)

    bs_scale = 1.0  # for measure tool

    # Measure tool on best detection window
    best_win = "Best Detection (most central)"
    measure_pts = []
    measure_result = [None]

    def on_best_mouse(event, mx, my, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            # Correct for window resize
            if best_snapshot[0] is not None:
                bs = best_snapshot[0]
                bs_h_disp = int(bs.shape[0] * disp_w / bs.shape[1])
                ix, iy = correct_mouse_coords(best_win, mx, my, disp_w, bs_h_disp)
            else:
                ix, iy = mx, my
            measure_pts.append((ix, iy))
            if len(measure_pts) == 2:
                p1, p2 = measure_pts
                px_dist = math.sqrt((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)
                best_est = min(target_estimates, key=lambda e: e[4]) if target_estimates else None
                if best_est:
                    b_alt = best_est[5]
                    fov_h_rad = math.radians(54.4)
                    ground_w = 2 * b_alt * math.tan(fov_h_rad / 2)
                    m_per_disp_px = ground_w / (vid_w * bs_scale) if bs_scale else ground_w / vid_w
                    m_dist = px_dist * m_per_disp_px
                    measure_result[0] = (p1, p2, px_dist, m_dist)
                    print(f"  MEASURE: {px_dist:.0f}px = {m_dist:.2f}m (at {b_alt:.1f}m alt)")
                measure_pts.clear()
            elif len(measure_pts) > 2:
                measure_pts.clear()
        elif event == cv2.EVENT_RBUTTONDOWN:
            measure_pts.clear()
            measure_result[0] = None

    # Read first frame
    ret, frame = cap.read()
    if not ret:
        print("Cannot read first frame")
        return

    # Measure tool on main video (right-click to place points)
    vid_measure_pts = []
    vid_measure_result = [None]
    last_alt = [20.0]  # track latest altitude for scale

    def correct_mouse_coords(window_name, mx, my, img_w, img_h):
        """Convert window mouse coords to image coords (handles resized WINDOW_NORMAL)."""
        try:
            _, _, win_w, win_h = cv2.getWindowImageRect(window_name)
            if win_w > 0 and win_h > 0:
                return int(mx * img_w / win_w), int(my * img_h / win_h)
        except cv2.error:
            pass
        return mx, my

    def on_video_mouse(event, mx, my, flags, param):
        # Correct for window resize
        ix, iy = correct_mouse_coords(win, mx, my, disp_w, disp_h)
        if event == cv2.EVENT_RBUTTONDOWN:
            vid_measure_pts.append((ix, iy))
            if len(vid_measure_pts) == 2:
                p1, p2 = vid_measure_pts
                px_dist = math.sqrt((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)
                # Lock altitude at measurement time
                alt = last_alt[0]
                fov_h_rad = math.radians(54.4)
                ground_w = 2 * alt * math.tan(fov_h_rad / 2)
                m_per_disp_px = ground_w / disp_w
                m_dist = px_dist * m_per_disp_px
                vid_measure_result[0] = (p1, p2, px_dist, m_dist, alt)
                print(f"  VIDEO MEASURE: {px_dist:.0f} img-px = {m_dist:.2f}m (at {alt:.1f}m alt, FOV 49 deg)")
                vid_measure_pts.clear()
            elif len(vid_measure_pts) > 2:
                vid_measure_pts.clear()
        elif event == cv2.EVENT_MBUTTONDOWN:
            vid_measure_pts.clear()
            vid_measure_result[0] = None

    cv2.setMouseCallback(win, on_video_mouse)

    # Create resizable windows for all panels
    cv2.namedWindow("Latest Detection", cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
    cv2.namedWindow("Target GPS Estimates", cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
    cv2.namedWindow(best_win, cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)

    while True:
        if not paused:
            ret, frame = cap.read()
            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
            frame_num = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
            try:
                cv2.setTrackbarPos("Position", win, frame_num)
            except cv2.error:
                pass
            need_detect[0] = True

        # Submit to inference when needed and not busy
        if need_detect[0] and not ai_result["busy"] and frame is not None:
            need_detect[0] = False
            ai_result["busy"] = True
            # Apply weather effect before feeding to model
            frame_for_ai = apply_weather_effect(frame.copy())
            if use_tiling[0]:
                t = threading.Thread(target=run_tiled_inference, args=(frame_for_ai, frame_num), daemon=True)
            else:
                t = threading.Thread(target=run_single_inference, args=(frame_for_ai, frame_num), daemon=True)
            t.start()

        timestamp = frame_num / fps if fps > 0 else 0

        # === DISPLAY ===
        if frame is not None:
            # Show the weather-affected frame so user sees what the model sees
            disp_frame = apply_weather_effect(frame) if EFFECTS[active_effect[0]] != "none" else frame
            disp = cv2.resize(disp_frame, (disp_w, disp_h))

            with ai_lock:
                dets = ai_result["dets"]
                dt = ai_result["dt"]
                det_frame = ai_result["frame_num"]
                snapshot = ai_result["snapshot"]

            stale = abs(frame_num - det_frame) > 30
            for cx, cy, w, h, conf in ([] if stale else dets):
                x1 = int((cx - w / 2) * disp_scale)
                y1 = int((cy - h / 2) * disp_scale)
                x2 = int((cx + w / 2) * disp_scale)
                y2 = int((cy + h / 2) * disp_scale)
                cv2.rectangle(disp, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cls_label = getattr(vs, 'last_class_name', '') or ''
                det_text = f"{conf:.2f} [{cls_label}]" if cls_label else f"{conf:.2f}"
                cv2.putText(disp, det_text, (x1, y1 - 8),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                dcx = int(cx * disp_scale)
                dcy = int(cy * disp_scale)
                cv2.circle(disp, (dcx, dcy), 5, (255, 0, 255), -1)
                cv2.circle(disp, (dcx, dcy), 5, (255, 255, 255), 1)

            # Crosshair
            cx_disp = disp_w // 2
            cy_disp = disp_h // 2
            cv2.line(disp, (cx_disp - 20, cy_disp), (cx_disp + 20, cy_disp), (0, 200, 200), 1)
            cv2.line(disp, (cx_disp, cy_disp - 20), (cx_disp, cy_disp + 20), (0, 200, 200), 1)

            # Telemetry overlay (top-left of video)
            t_data = telem.get(frame_num)
            if t_data:
                telem_lines = [
                    f"Alt: {t_data['rel_alt']:.1f}m (AGL)",
                    f"GPS: {t_data['lat']:.6f}, {t_data['lon']:.6f}",
                    f"Yaw: {t_data['yaw']:.0f}  Pitch: {t_data['pitch']:.0f}",
                ]
                if dets and not stale:
                    cx_det, cy_det = dets[0][0], dets[0][1]
                    t_lat, t_lon = estimate_target_gps(
                        t_data['lat'], t_data['lon'], t_data['rel_alt'],
                        t_data['yaw'], cx_det, cy_det, vid_w, vid_h
                    )
                    telem_lines.append(f"TARGET: {t_lat:.6f}, {t_lon:.6f}")
                box_h = 22 * len(telem_lines) + 8
                cv2.rectangle(disp, (0, 0), (320, box_h), (0, 0, 0), -1)
                for i, line in enumerate(telem_lines):
                    color = (0, 255, 0) if "TARGET" in line else (200, 200, 200)
                    cv2.putText(disp, line, (8, 20 + i * 22),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1)

            # Latest snapshot in its own window — image + info text below
            if snapshot is not None and dets:
                snap_disp_w = disp_w // 2
                snap_disp_h = int(snapshot.shape[0] * snap_disp_w / snapshot.shape[1])
                snap_resized = cv2.resize(snapshot, (snap_disp_w, snap_disp_h))
                # Build info strip below image
                info_lines = ai_result.get("info_lines", [])
                info_h = max(20 * len(info_lines) + 10, 10)
                info_strip = np.zeros((info_h, snap_disp_w, 3), dtype=np.uint8)
                for i, line in enumerate(info_lines):
                    if "TARGET" in line:
                        color = (0, 255, 0)
                    elif "DRONE" in line:
                        color = (200, 200, 200)
                    elif "OFFSET" in line:
                        color = (0, 200, 255)
                    else:
                        color = (0, 255, 255)
                    cv2.putText(info_strip, line, (8, 16 + i * 20),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.42, color, 1)
                snap_with_info = np.vstack([snap_resized, info_strip])
                cv2.imshow("Latest Detection", snap_with_info)

            # Update altitude for scale calculations
            # SRT telemetry may not have every frame — find closest
            t_data_scale = telem.get(frame_num)
            if not t_data_scale:
                # Search nearby frames (SRT entries may be sparse)
                for offset in range(1, 30):
                    t_data_scale = telem.get(frame_num - offset) or telem.get(frame_num + offset)
                    if t_data_scale:
                        break
            if t_data_scale and t_data_scale['rel_alt'] > 1:
                last_alt[0] = t_data_scale['rel_alt']

            # Scale bar (bottom-right) — shows what 1m looks like at current altitude
            alt_now = last_alt[0]
            fov_h_scale = math.radians(54.4)
            ground_w_now = 2 * alt_now * math.tan(fov_h_scale / 2)
            px_per_m = disp_w / ground_w_now if ground_w_now > 0 else 1
            scale_1m = int(px_per_m)
            if scale_1m > 5:
                sx1 = disp_w - scale_1m - 20
                sy1 = disp_h - 55
                sx2 = disp_w - 20
                cv2.line(disp, (sx1, sy1), (sx2, sy1), (255, 255, 255), 2)
                cv2.line(disp, (sx1, sy1 - 5), (sx1, sy1 + 5), (255, 255, 255), 2)
                cv2.line(disp, (sx2, sy1 - 5), (sx2, sy1 + 5), (255, 255, 255), 2)
                cv2.putText(disp, f"1m ({alt_now:.0f}m alt)", (sx1, sy1 - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.38, (255, 255, 255), 1)

            # Draw measure line on main video — uses altitude locked at click time
            if vid_measure_result[0]:
                p1, p2, px_d, m_d, m_alt = vid_measure_result[0]
                cv2.line(disp, p1, p2, (0, 255, 255), 2)
                cv2.circle(disp, p1, 4, (0, 255, 255), -1)
                cv2.circle(disp, p2, 4, (0, 255, 255), -1)
                mid = ((p1[0]+p2[0])//2, (p1[1]+p2[1])//2)
                cv2.putText(disp, f"{m_d:.2f}m (at {m_alt:.0f}m)", (mid[0]+8, mid[1]-8),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 2)
            if len(vid_measure_pts) == 1:
                cv2.circle(disp, vid_measure_pts[0], 4, (0, 255, 255), -1)

            # HUD bar at bottom of video
            bar_y = disp_h - 30
            cv2.rectangle(disp, (0, bar_y), (disp_w, disp_h), (0, 0, 0), -1)
            progress = frame_num / total_frames
            cv2.rectangle(disp, (0, bar_y), (int(disp_w * progress), bar_y + 4), (0, 200, 200), -1)
            mode = f"TILE {args.tile_size}px" if use_tiling[0] else "SINGLE 640"
            m_name = os.path.basename(os.path.dirname(args.model if active_model[0] == 0 else args.model2)) or "root"
            m_file = os.path.basename(args.model if active_model[0] == 0 else args.model2)
            model_tag = f"{m_name}/{m_file}" if m_name != "root" else m_file
            eff_name = EFFECTS[active_effect[0]].upper()
            eff_str = f" | WX: {eff_name} {effect_intensity[0]:.0%}" if eff_name != "NONE" else ""
            info = f"{timestamp:.1f}s / {duration:.1f}s | {dt:.0f}ms | Det: {det_count[0]} | {mode} | {speed:.1f}x | [{model_tag}] M=switch{eff_str}"
            cv2.putText(disp, info, (10, disp_h - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (200, 200, 200), 1)

            # Weather effect badge (top-right)
            if EFFECTS[active_effect[0]] != "none":
                badge = f"WX: {eff_name} ({effect_intensity[0]:.0%})"
                badge_w = len(badge) * 11 + 16
                cv2.rectangle(disp, (disp_w - badge_w, 0), (disp_w, 28), (0, 0, 120), -1)
                cv2.putText(disp, badge, (disp_w - badge_w + 8, 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 200, 255), 1)

            if writer:
                writer.write(disp)
            cv2.imshow(win, disp)

            # GPS plots window (center distance + altitude side by side)
            plot_center = draw_gps_plot_by_center()
            plot_alt = draw_gps_plot_by_alt()
            sep = np.zeros((plot_size, 2, 3), dtype=np.uint8)
            sep[:] = (60, 60, 60)
            gps_combined = np.hstack([plot_center, sep, plot_alt])
            cv2.imshow("Target GPS Estimates", gps_combined)

            # Best detection window
            if best_snapshot[0] is not None:
                bs = best_snapshot[0]
                bs_h_disp = int(bs.shape[0] * disp_w / bs.shape[1])
                bs_resized = cv2.resize(bs, (disp_w, bs_h_disp))
                bs_scale = disp_w / bs.shape[1]
                # Draw measurement line
                if measure_result[0]:
                    p1, p2, px_d, m_d = measure_result[0]
                    cv2.line(bs_resized, p1, p2, (0, 255, 255), 2)
                    cv2.circle(bs_resized, p1, 4, (0, 255, 255), -1)
                    cv2.circle(bs_resized, p2, 4, (0, 255, 255), -1)
                    mid = ((p1[0]+p2[0])//2, (p1[1]+p2[1])//2)
                    cv2.putText(bs_resized, f"{m_d:.2f}m", (mid[0]+8, mid[1]-8),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                if len(measure_pts) == 1:
                    cv2.circle(bs_resized, measure_pts[0], 4, (0, 255, 255), -1)
                cv2.imshow(best_win, bs_resized)
                cv2.setMouseCallback(best_win, on_best_mouse)

        delay = max(1, int((1000 / fps) / speed)) if not paused else 50
        key = cv2.waitKey(delay) & 0xFF

        if key == ord('q'):
            break
        elif key == ord(' '):
            paused = not paused
        elif key == ord('t'):
            use_tiling[0] = not use_tiling[0]
            print(f"  Tiling: {'ON' if use_tiling[0] else 'OFF'}")
        elif key == ord('m'):
            # Switch model
            available = sorted(models.keys())
            if len(available) > 1:
                idx = available.index(active_model[0])
                active_model[0] = available[(idx + 1) % len(available)]
                vs = models[active_model[0]]
                print(f"  SWITCHED TO: {model_names[active_model[0]]}")
            else:
                print("  Only one model loaded")
        elif key == ord('d') or key == 83:
            new_pos = min(frame_num + int(fps * 5), total_frames - 1)
            cap.set(cv2.CAP_PROP_POS_FRAMES, new_pos)
        elif key == ord('a') or key == 81:
            new_pos = max(frame_num - int(fps * 5), 0)
            cap.set(cv2.CAP_PROP_POS_FRAMES, new_pos)
        elif key == ord('+') or key == ord('='):
            speed = min(speed + 0.5, 8.0)
        elif key == ord('-'):
            speed = max(speed - 0.5, 0.5)
        elif key == ord('w'):
            active_effect[0] = (active_effect[0] + 1) % len(EFFECTS)
            print(f"  WEATHER: {EFFECTS[active_effect[0]]} ({effect_intensity[0]:.0%})")
        elif key == ord('e'):
            effect_intensity[0] = min(effect_intensity[0] + 0.1, 1.0)
            print(f"  INTENSITY: {effect_intensity[0]:.0%}")
        elif key == ord('r'):
            effect_intensity[0] = max(effect_intensity[0] - 0.1, 0.1)
            print(f"  INTENSITY: {effect_intensity[0]:.0%}")

    cap.release()
    if writer:
        writer.release()
    csv_file.close()
    cv2.destroyAllWindows()
    print(f"Detection data saved to: {csv_path}")

    print(f"\n{'=' * 50}")
    processed = frame_num // max(1, args.every)
    print(f"Frames processed by AI: ~{processed}")
    print(f"Frames with detections: {det_count[0]} ({100 * det_count[0] / max(1, processed):.1f}%)")
    if target_estimates:
        lats = [e[0] for e in target_estimates]
        lons = [e[1] for e in target_estimates]
        print(f"Target estimates: {len(target_estimates)}")
        print(f"Mean target GPS: {sum(lats)/len(lats):.6f}, {sum(lons)/len(lons):.6f}")
        dists = []
        ml, mlo = sum(lats)/len(lats), sum(lons)/len(lons)
        for lat, lon, _, _, _, _ in target_estimates:
            n = (lat - ml) * 111320
            e = (lon - mlo) * 111320 * math.cos(math.radians(ml))
            dists.append(math.sqrt(n**2 + e**2))
        print(f"CEP50: {sorted(dists)[len(dists)//2]:.1f}m  Max spread: {max(dists):.1f}m")

if __name__ == "__main__":
    main()
