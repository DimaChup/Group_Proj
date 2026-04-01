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
import config


# ─── Distortion / Undistortion ───

def create_synthetic_distortion_maps(h, w, k1=0.15, k2=0.02):
    """Create barrel distortion + undistortion maps (simulates Pi fisheye)."""
    cx, cy = w / 2.0, h / 2.0
    f = max(w, h)
    mtx = np.array([[f, 0, cx], [0, f, cy], [0, 0, 1]], dtype=np.float32)
    dist = np.array([k1, k2, 0, 0, 0], dtype=np.float32)
    new_mtx, _ = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 0, (w, h))
    # Undistortion map (removes distortion)
    undist_map1, undist_map2 = cv2.initUndistortRectifyMap(
        mtx, dist, None, new_mtx, (w, h), cv2.CV_16SC2)
    # Distortion map (adds distortion — use negative coefficients)
    dist_neg = np.array([-k1, -k2, 0, 0, 0], dtype=np.float32)
    dist_map1, dist_map2 = cv2.initUndistortRectifyMap(
        mtx, dist_neg, None, new_mtx, (w, h), cv2.CV_16SC2)
    return dist_map1, dist_map2, undist_map1, undist_map2


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


def _get_config_fov():
    """Get HFOV in degrees from config.py."""
    return 2 * math.degrees(math.atan(config.SENSOR_WIDTH_MM / (2 * config.FOCAL_LENGTH_MM)))

def estimate_target_gps(drone_lat, drone_lon, alt, yaw, pixel_x, pixel_y, img_w, img_h, fov_h=None):
    """Estimate target GPS from drone position + pixel offset. Returns (lat, lon)."""
    if fov_h is None:
        fov_h = _get_config_fov()
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
    parser = argparse.ArgumentParser(description="Run video with tiled detection")
    parser.add_argument("video", help="Path to video file")
    parser.add_argument("--model", default="cv_models/human.tflite", help="Model 1 (default: COCO human)")
    parser.add_argument("--model2", default="best.tflite", help="Model 2 (default: original dummy)")
    parser.add_argument("--model3", default="cv_models/sar_v2_1088/best.tflite", help="Model 3 (default: v2 retrained)")
    parser.add_argument("--model4", default="cv_models/sar_v2_1088/best.tflite", help="Model 4 (NCNN backend)")
    parser.add_argument("--smart-estimate", action='store_true', help="Show SMART median estimate from central detections")
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

    # Load all models (model4 uses NCNN backend)
    models = {}
    model_names = {}
    model_list = [
        (args.model, "Model 1 (TFLite)", None),
        (args.model2, "Model 2 (TFLite)", None),
        (args.model3, "Model 3 (TFLite)", None),
        (args.model4, "Model 4 (NCNN)", "ncnn"),
    ]
    for i, (path, label, backend) in enumerate(model_list):
        if os.path.exists(path):
            v = VisionSystem(camera_index=None, model_path=path, backend=backend)
            if v.using_ai:
                models[i] = v
                sz = os.path.getsize(path)/1024/1024 if os.path.isfile(path) else 0
                model_names[i] = f"{label}: {os.path.basename(path)} ({sz:.1f}MB) [{v.backend_name}]"
                print(f"  Loaded {model_names[i]}")
            else:
                print(f"  Failed to load {path} ({label})")
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
    print("Controls: SPACE=pause  Q=quit  A/D=skip 5s  +/-=speed  T=toggle tiling  F=toggle full-speed playback")
    print()

    writer = None
    if args.save:
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(args.save, fourcc, fps, (disp_w, disp_h))
        print(f"Saving to: {args.save}")

    # GPS scatter plot of all target estimates
    target_estimates = []  # list of (lat, lon, conf, frame_num, center_dist, alt)
    smart_frames = []     # list of (frame, center_dist_m, est_lat, est_lon, fnum) — first 10 central
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

    plot_size = 500
    # True dummy position (ground truth for accuracy comparison)
    TRUE_DUMMY_LAT = 51.42339
    TRUE_DUMMY_LON = -2.671538

    def heat_color(val):
        """0.0=green, 1.0=red. Returns BGR tuple."""
        g = int(255 * max(0, 1 - val))
        r = int(255 * min(1, val))
        return (0, g, r)

    def draw_smart_bullseye():
        """SMART mode: bullseye centered on true position, only first 10 central detections."""
        plot = np.zeros((plot_size, plot_size, 3), dtype=np.uint8)
        central = [e for e in target_estimates if e[4] < 4.0][:10]
        n_central = len([e for e in target_estimates if e[4] < 4.0])
        n_total = len(target_estimates)

        # Title
        cv2.putText(plot, f"SMART ESTIMATE ({len(central)}/10 central)", (10, 25),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 0, 255), 2)
        cv2.putText(plot, f"Total: {n_total} detections, {n_central} within 4m of center",
                   (10, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (150, 150, 150), 1)

        if not central:
            cv2.putText(plot, "Waiting for central detections...", (60, plot_size // 2),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.55, (150, 0, 150), 1)
            return plot

        # Convert estimates to meters from TRUE position (origin)
        pts_m = []
        for lat, lon, conf, fnum, cdist, alt in central:
            n = (lat - TRUE_DUMMY_LAT) * 111320
            e = (lon - TRUE_DUMMY_LON) * 111320 * math.cos(math.radians(TRUE_DUMMY_LAT))
            pts_m.append((e, n, cdist, conf))

        # Auto-scale: tight fit around actual data with 30% margin
        pts_dists = [math.sqrt(p[0]**2 + p[1]**2) for p in pts_m]
        max_d = max(pts_dists) * 1.3 if pts_dists else 5.0
        max_d = max(max_d, 1.0)  # at least 1m range
        margin = 70
        usable = plot_size - 2 * margin
        scale = usable / (2 * max_d)
        cx, cy = plot_size // 2, plot_size // 2 + 10  # slight offset for title

        # Bullseye rings (1m, 2m, 3m, 5m, 10m)
        for r_m in [1, 2, 3, 5, 10]:
            r_px = int(r_m * scale)
            if r_px > 5 and r_px < usable // 2:
                cv2.circle(plot, (cx, cy), r_px, (40, 40, 40), 1)
                cv2.putText(plot, f"{r_m}m", (cx + r_px + 3, cy - 3),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.3, (80, 80, 80), 1)

        # Grid lines
        cv2.line(plot, (margin, cy), (plot_size - margin, cy), (50, 50, 50), 1)
        cv2.line(plot, (cx, margin), (cx, plot_size - margin), (50, 50, 50), 1)
        cv2.putText(plot, "N", (cx - 4, margin - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (100, 100, 100), 1)
        cv2.putText(plot, "E", (plot_size - margin + 5, cy + 4), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (100, 100, 100), 1)

        # TRUE position = ORIGIN (yellow crosshair)
        cv2.drawMarker(plot, (cx, cy), (0, 255, 255), cv2.MARKER_CROSS, 25, 3)
        cv2.circle(plot, (cx, cy), 5, (0, 255, 255), -1)

        # Plot the 10 central detection estimates with distance lines
        for i, (e_m, n_m, cdist, conf) in enumerate(pts_m):
            px = cx + int(e_m * scale)
            py = cy - int(n_m * scale)
            # Thin gray line from dot to center (true position)
            cv2.line(plot, (cx, cy), (px, py), (70, 70, 70), 1)
            # Bigger dots, color by index
            brightness = int(255 * (1 - i * 0.05))
            cv2.circle(plot, (px, py), 8, (brightness, brightness, 0), -1)
            cv2.circle(plot, (px, py), 8, (255, 255, 255), 2)
            # Distance label
            d_m = math.sqrt(e_m**2 + n_m**2)
            cv2.putText(plot, f"{i+1}({d_m:.1f}m)", (px + 10, py + 4),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.3, (200, 200, 200), 1)

        # Compute median
        if len(central) >= 10:
            m_lats = sorted(e[0] for e in central)
            m_lons = sorted(e[1] for e in central)
            mid = len(m_lats) // 2
            med_lat = (m_lats[mid-1] + m_lats[mid]) / 2 if len(m_lats) % 2 == 0 else m_lats[mid]
            med_lon = (m_lons[mid-1] + m_lons[mid]) / 2 if len(m_lons) % 2 == 0 else m_lons[mid]
            med_n = (med_lat - TRUE_DUMMY_LAT) * 111320
            med_e = (med_lon - TRUE_DUMMY_LON) * 111320 * math.cos(math.radians(TRUE_DUMMY_LAT))
            med_px = cx + int(med_e * scale)
            med_py = cy - int(med_n * scale)
            # Magenta diamond for median
            pts_diamond = np.array([[med_px, med_py-10], [med_px+10, med_py],
                                    [med_px, med_py+10], [med_px-10, med_py]], np.int32)
            cv2.polylines(plot, [pts_diamond], True, (255, 0, 255), 2)
            cv2.circle(plot, (med_px, med_py), 3, (255, 0, 255), -1)

            med_err = math.sqrt(med_n**2 + med_e**2)
            cv2.putText(plot, f"MEDIAN: {med_lat:.7f}, {med_lon:.7f}", (10, plot_size - 55),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 0, 255), 2)
            cv2.putText(plot, f"Error from TRUE: {med_err:.2f}m", (10, plot_size - 35),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 0, 255), 1)
        else:
            cv2.putText(plot, f"Need {10 - len(central)} more central detections...",
                       (10, plot_size - 35), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (150, 0, 150), 1)

        # True position label
        cv2.putText(plot, f"ORIGIN = TRUE: {TRUE_DUMMY_LAT:.5f}, {TRUE_DUMMY_LON:.5f}",
                   (10, plot_size - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 255), 1)

        return plot

    def draw_gps_plot_by_center():
        """GPS scatter colored by distance from image center."""
        plot = np.zeros((plot_size, plot_size, 3), dtype=np.uint8)
        plot_data = target_estimates

        if not plot_data:
            cv2.putText(plot, "No detections yet", (80, plot_size // 2),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 100), 1)
            return plot

        lats = [e[0] for e in plot_data]
        lons = [e[1] for e in plot_data]
        mean_lat = sum(lats) / len(lats)
        mean_lon = sum(lons) / len(lons)

        # Center plot on TRUE position (yellow cross = origin)
        center_lat = TRUE_DUMMY_LAT
        center_lon = TRUE_DUMMY_LON

        pts_m = []
        for lat, lon, conf, fnum, cdist, alt in plot_data:
            north = (lat - center_lat) * 111320
            east = (lon - center_lon) * 111320 * math.cos(math.radians(center_lat))
            pts_m.append((east, north, cdist, alt))

        # Auto-scale: 95th percentile to avoid outliers stretching the plot
        all_dists = sorted(math.sqrt(p[0]**2 + p[1]**2) for p in pts_m)
        p95 = all_dists[int(len(all_dists) * 0.95)] if all_dists else 20.0
        max_range = max(p95 * 2.5, 10.0)  # margin around cluster
        margin = 60
        usable = plot_size - 2 * margin
        scale = usable / max_range

        # Grid with meter labels
        grid_step = 1 if max_range < 10 else (5 if max_range < 50 else 10)
        for d in range(-int(max_range), int(max_range) + 1, grid_step):
            px = int(plot_size / 2 + d * scale)
            py = int(plot_size / 2 - d * scale)
            if margin < px < plot_size - margin:
                cv2.line(plot, (px, margin), (px, plot_size - margin), (30, 30, 30), 1)
                if d != 0:
                    cv2.putText(plot, f"{d}m", (px - 8, margin - 5),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.25, (80, 80, 80), 1)
            if margin < py < plot_size - margin:
                cv2.line(plot, (margin, py), (plot_size - margin, py), (30, 30, 30), 1)

        # Crosshair at mean
        cv2.line(plot, (plot_size // 2 - 12, plot_size // 2), (plot_size // 2 + 12, plot_size // 2), (80, 80, 80), 1)
        cv2.line(plot, (plot_size // 2, plot_size // 2 - 12), (plot_size // 2, plot_size // 2 + 12), (80, 80, 80), 1)

        # Plot points colored by center distance (bigger, clearer)
        # Normalize center_dist for color: 0m=green, 4m+=red
        for east, north, cdist, alt in pts_m:
            px = int(plot_size / 2 + east * scale)
            py = int(plot_size / 2 - north * scale)
            color_val = min(1.0, cdist / 8.0)  # 0m=green, 8m=red
            color = heat_color(color_val)
            cv2.circle(plot, (px, py), 3, color, -1)

        # TRUE position = CENTER = yellow cross (same as bullseye)
        t_cx, t_cy = plot_size // 2, plot_size // 2
        cv2.drawMarker(plot, (t_cx, t_cy), (0, 255, 255), cv2.MARKER_CROSS, 25, 3)
        cv2.circle(plot, (t_cx, t_cy), 5, (0, 255, 255), -1)
        # Bullseye rings from true position
        for r_m in [1, 2, 3, 5, 10]:
            r_px = int(r_m * scale)
            if r_px > 5 and r_px < usable // 2:
                cv2.circle(plot, (t_cx, t_cy), r_px, (50, 50, 50), 1)
                cv2.putText(plot, f"{r_m}m", (t_cx + r_px + 2, t_cy - 2),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.25, (80, 80, 80), 1)
        # Compute weighted mean FIRST (needed for both marker + header)
        wm_lat = mean_lat
        wm_lon = mean_lon
        wm_err = 0
        if target_estimates:
            w_total = 0
            w_lat = 0
            w_lon = 0
            for lat, lon, conf, fnum, cdist, alt in target_estimates:
                w = 1.0 / max(0.1, cdist) ** 2
                w_lat += lat * w
                w_lon += lon * w
                w_total += w
            if w_total > 0:
                wm_lat = w_lat / w_total
                wm_lon = w_lon / w_total
                wm_err = math.sqrt(((wm_lat - TRUE_DUMMY_LAT) * 111320)**2 +
                          ((wm_lon - TRUE_DUMMY_LON) * 111320 * math.cos(math.radians(TRUE_DUMMY_LAT)))**2)

        # PLAIN MEAN marker (green square) + error
        m_north = (mean_lat - center_lat) * 111320
        m_east = (mean_lon - center_lon) * 111320 * math.cos(math.radians(center_lat))
        m_px = int(plot_size / 2 + m_east * scale)
        m_py = int(plot_size / 2 - m_north * scale)
        mean_err_m = math.sqrt(m_north**2 + m_east**2)
        if margin < m_px < plot_size - margin and margin < m_py < plot_size - margin:
            cv2.rectangle(plot, (m_px - 8, m_py - 8), (m_px + 8, m_py + 8), (0, 255, 0), 2)
            cv2.putText(plot, f"{mean_err_m:.1f}m", (m_px + 12, m_py - 2),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)

        # WEIGHTED MEAN marker (cyan diamond) + error
        if target_estimates and wm_err > 0:
            wm_north = (wm_lat - center_lat) * 111320
            wm_east = (wm_lon - center_lon) * 111320 * math.cos(math.radians(center_lat))
            wm_px = int(plot_size / 2 + wm_east * scale)
            wm_py = int(plot_size / 2 - wm_north * scale)
            if margin < wm_px < plot_size - margin and margin < wm_py < plot_size - margin:
                pts_d = np.array([[wm_px, wm_py-10], [wm_px+10, wm_py],
                                  [wm_px, wm_py+10], [wm_px-10, wm_py]], np.int32)
                cv2.polylines(plot, [pts_d], True, (0, 255, 255), 2)
                cv2.putText(plot, f"{wm_err:.1f}m", (wm_px + 12, wm_py + 5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)

        # Stats
        dists_m = [math.sqrt(p[0]**2 + p[1]**2) for p in pts_m]
        cep50 = sorted(dists_m)[len(dists_m) // 2] if len(dists_m) > 1 else 0

        # Compute all 5 errors from TRUE position
        # 1. Mean
        mean_err_m = math.sqrt(((mean_lat - TRUE_DUMMY_LAT) * 111320)**2 +
                     ((mean_lon - TRUE_DUMMY_LON) * 111320 * math.cos(math.radians(TRUE_DUMMY_LAT)))**2)
        # 2. Weighted (already computed above)
        # 3. Median
        s_lats = sorted(lats)
        s_lons = sorted(lons)
        mid = len(s_lats) // 2
        med_lat = (s_lats[mid-1] + s_lats[mid]) / 2 if len(s_lats) % 2 == 0 else s_lats[mid]
        med_lon = (s_lons[mid-1] + s_lons[mid]) / 2 if len(s_lons) % 2 == 0 else s_lons[mid]
        med_err = math.sqrt(((med_lat - TRUE_DUMMY_LAT) * 111320)**2 +
                   ((med_lon - TRUE_DUMMY_LON) * 111320 * math.cos(math.radians(TRUE_DUMMY_LAT)))**2)
        # 4. Best estimate (most central detection)
        best_est_err = 0
        drone_gps_err = 0
        if target_estimates:
            best = min(target_estimates, key=lambda e: e[4])
            best_est_err = math.sqrt(((best[0] - TRUE_DUMMY_LAT) * 111320)**2 +
                           ((best[1] - TRUE_DUMMY_LON) * 111320 * math.cos(math.radians(TRUE_DUMMY_LAT)))**2)
            # 5. Drone GPS during best detection
            t_data_best = telem.get(best[3])  # fnum
            if t_data_best:
                drone_gps_err = math.sqrt(((t_data_best['lat'] - TRUE_DUMMY_LAT) * 111320)**2 +
                                 ((t_data_best['lon'] - TRUE_DUMMY_LON) * 111320 * math.cos(math.radians(TRUE_DUMMY_LAT)))**2)

        # Clean stats panel — all 5 errors clearly listed
        cv2.rectangle(plot, (0, 0), (plot_size, 135), (0, 0, 0), -1)
        cv2.putText(plot, f"N={len(plot_data)} | Origin = TRUE | CEP50: {cep50:.1f}m", (8, 16),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.35, (150, 150, 150), 1)
        y = 38
        cv2.putText(plot, f"1. Mean:       {mean_err_m:.2f}m", (8, y), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 255, 0), 1)       # GREEN
        cv2.putText(plot, f"2. Weighted:   {wm_err:.2f}m", (8, y+20), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255, 255, 0), 1)  # CYAN-BLUE
        cv2.putText(plot, f"3. Median:     {med_err:.2f}m", (8, y+40), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255, 0, 255), 1)  # MAGENTA
        cv2.putText(plot, f"4. Best Est:   {best_est_err:.2f}m", (8, y+60), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 140, 255), 1)  # ORANGE
        cv2.putText(plot, f"5. Drone GPS:  {drone_gps_err:.2f}m", (8, y+80), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 0, 255), 1)  # RED

        # Bottom stats
        max_spread = max(dists_m) if dists_m else 0
        cv2.putText(plot, f"N={len(plot_data)} | Grid={grid_step}m | Max spread: {max_spread:.1f}m", (8, plot_size - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.35, (100, 100, 100), 1)

        # Disable old smart block
        central = []
        if len(central) >= 10:
            c_lats = sorted(e[0] for e in central)
            c_lons = sorted(e[1] for e in central)
            mid = len(c_lats) // 2
            s_lat = (c_lats[mid-1] + c_lats[mid]) / 2 if len(c_lats) % 2 == 0 else c_lats[mid]
            s_lon = (c_lons[mid-1] + c_lons[mid]) / 2 if len(c_lons) % 2 == 0 else c_lons[mid]
            s_dists = sorted(math.sqrt(((e[0]-s_lat)*111320)**2 +
                       ((e[1]-s_lon)*111320*math.cos(math.radians(s_lat)))**2)
                       for e in central)
            s_cep = s_dists[len(s_dists)//2]
            cv2.putText(plot, f"SMART({len(central)}): {s_lat:.6f}, {s_lon:.6f} CEP:{s_cep:.1f}m",
                       (8, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.40, (255, 0, 255), 2)
            # Magenta diamond marker
            s_n = (s_lat - mean_lat) * 111320
            s_e = (s_lon - mean_lon) * 111320 * math.cos(math.radians(mean_lat))
            s_px = margin + int(usable / 2 + (s_e / max(1, max_range)) * usable / 2)
            s_py = margin + int(usable / 2 - (s_n / max(1, max_range)) * usable / 2)
            if margin < s_px < plot_size - margin and margin < s_py < plot_size - margin:
                pts = np.array([[s_px, s_py-8], [s_px+8, s_py], [s_px, s_py+8], [s_px-8, s_py]], np.int32)
                cv2.polylines(plot, [pts], True, (255, 0, 255), 2)
        elif len(central) > 0:
            cv2.putText(plot, f"SMART: {len(central)}/10 central...",
                       (8, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (150, 0, 150), 1)

        # Color bar legend on right
        bar_x = plot_size - 25
        for i in range(margin, plot_size - margin):
            val = (i - margin) / usable
            c = heat_color(val)
            cv2.line(plot, (bar_x, i), (bar_x + 15, i), c, 1)
        cv2.putText(plot, "ctr", (bar_x - 5, margin - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 255, 0), 1)
        cv2.putText(plot, "edge", (bar_x - 10, plot_size - margin + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 255), 1)

        return plot

    def draw_error_convergence():
        """Running mean vs weighted mean error over detection count."""
        plot = np.zeros((plot_size, plot_size, 3), dtype=np.uint8)
        cv2.putText(plot, "Error vs # Detections", (8, 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)
        cv2.putText(plot, "mean | weighted | median | best est | drone gps", (8, 40),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.28, (150, 150, 150), 1)

        if len(target_estimates) < 2:
            cv2.putText(plot, "Waiting for detections...", (60, plot_size // 2),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 100), 1)
            return plot

        # Compute running mean, weighted mean, and median error at each step
        mean_errors = []
        weighted_errors = []
        median_errors = []
        r_lat = r_lon = 0
        w_lat = w_lon = w_total = 0
        all_lats = []
        all_lons = []

        for i, (lat, lon, conf, fnum, cdist, alt) in enumerate(target_estimates):
            all_lats.append(lat)
            all_lons.append(lon)

            # Running mean
            r_lat += lat
            r_lon += lon
            m_lat = r_lat / (i + 1)
            m_lon = r_lon / (i + 1)
            m_err = math.sqrt(((m_lat - TRUE_DUMMY_LAT) * 111320)**2 +
                     ((m_lon - TRUE_DUMMY_LON) * 111320 * math.cos(math.radians(TRUE_DUMMY_LAT)))**2)
            mean_errors.append(m_err)

            # Running weighted mean
            w = 1.0 / max(0.1, cdist) ** 2
            w_lat += lat * w
            w_lon += lon * w
            w_total += w
            wm_lat_r = w_lat / w_total
            wm_lon_r = w_lon / w_total
            wm_err = math.sqrt(((wm_lat_r - TRUE_DUMMY_LAT) * 111320)**2 +
                      ((wm_lon_r - TRUE_DUMMY_LON) * 111320 * math.cos(math.radians(TRUE_DUMMY_LAT)))**2)
            weighted_errors.append(wm_err)

            # Running median
            s_lats = sorted(all_lats)
            s_lons = sorted(all_lons)
            mid = len(s_lats) // 2
            md_lat = (s_lats[mid-1] + s_lats[mid]) / 2 if len(s_lats) % 2 == 0 else s_lats[mid]
            md_lon = (s_lons[mid-1] + s_lons[mid]) / 2 if len(s_lons) % 2 == 0 else s_lons[mid]
            md_err = math.sqrt(((md_lat - TRUE_DUMMY_LAT) * 111320)**2 +
                      ((md_lon - TRUE_DUMMY_LON) * 111320 * math.cos(math.radians(TRUE_DUMMY_LAT)))**2)
            median_errors.append(md_err)

        # Best Est and Drone GPS — single values, drawn as horizontal lines
        best_est_err_val = 0
        drone_gps_err_val = 0
        if target_estimates:
            best = min(target_estimates, key=lambda e: e[4])
            best_est_err_val = math.sqrt(((best[0] - TRUE_DUMMY_LAT) * 111320)**2 +
                               ((best[1] - TRUE_DUMMY_LON) * 111320 * math.cos(math.radians(TRUE_DUMMY_LAT)))**2)
            t_best = telem.get(best[3])
            if t_best:
                drone_gps_err_val = math.sqrt(((t_best['lat'] - TRUE_DUMMY_LAT) * 111320)**2 +
                                     ((t_best['lon'] - TRUE_DUMMY_LON) * 111320 * math.cos(math.radians(TRUE_DUMMY_LAT)))**2)

        # Plot axes
        margin_l = 50
        margin_b = 40
        margin_t = 50
        margin_r = 10
        pw = plot_size - margin_l - margin_r
        ph = plot_size - margin_t - margin_b

        n = len(mean_errors)
        max_err = max(max(mean_errors), max(weighted_errors), max(median_errors),
                      best_est_err_val, drone_gps_err_val, 1.0)
        max_err = min(max_err, 50.0)  # cap at 50m

        # Y axis labels
        for y_m in range(0, int(max_err) + 2, max(1, int(max_err / 5))):
            y_px = margin_t + ph - int(y_m / max_err * ph)
            if margin_t < y_px < plot_size - margin_b:
                cv2.line(plot, (margin_l, y_px), (plot_size - margin_r, y_px), (30, 30, 30), 1)
                cv2.putText(plot, f"{y_m}m", (5, y_px + 4),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.3, (100, 100, 100), 1)

        # X axis
        cv2.line(plot, (margin_l, plot_size - margin_b), (plot_size - margin_r, plot_size - margin_b), (60, 60, 60), 1)
        cv2.putText(plot, f"detections (N={n})", (plot_size // 2 - 40, plot_size - 8),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.3, (100, 100, 100), 1)

        # Draw lines
        for i in range(1, n):
            x1 = margin_l + int((i - 1) / max(1, n - 1) * pw)
            x2 = margin_l + int(i / max(1, n - 1) * pw)
            # Mean (green)
            y1 = margin_t + ph - int(min(mean_errors[i-1], max_err) / max_err * ph)
            y2 = margin_t + ph - int(min(mean_errors[i], max_err) / max_err * ph)
            cv2.line(plot, (x1, y1), (x2, y2), (0, 255, 0), 2)
            # Weighted (cyan)
            y1 = margin_t + ph - int(min(weighted_errors[i-1], max_err) / max_err * ph)
            y2 = margin_t + ph - int(min(weighted_errors[i], max_err) / max_err * ph)
            cv2.line(plot, (x1, y1), (x2, y2), (255, 255, 0), 2)  # CYAN-BLUE
            # Median (magenta)
            y1 = margin_t + ph - int(min(median_errors[i-1], max_err) / max_err * ph)
            y2 = margin_t + ph - int(min(median_errors[i], max_err) / max_err * ph)
            cv2.line(plot, (x1, y1), (x2, y2), (255, 0, 255), 2)

        # Best Est horizontal line (orange dashed)
        if best_est_err_val > 0:
            by = margin_t + ph - int(min(best_est_err_val, max_err) / max_err * ph)
            if margin_t < by < plot_size - margin_b:
                for dx in range(margin_l, plot_size - margin_r, 8):
                    cv2.line(plot, (dx, by), (min(dx + 4, plot_size - margin_r), by), (0, 140, 255), 1)  # ORANGE

        # Drone GPS horizontal line (yellow dashed)
        if drone_gps_err_val > 0:
            dy = margin_t + ph - int(min(drone_gps_err_val, max_err) / max_err * ph)
            if margin_t < dy < plot_size - margin_b:
                for dx in range(margin_l, plot_size - margin_r, 8):
                    cv2.line(plot, (dx, dy), (min(dx + 4, plot_size - margin_r), dy), (0, 0, 255), 1)  # RED

        # Final values — all 5
        cv2.putText(plot, f"Mean: {mean_errors[-1]:.2f}m", (margin_l + 5, margin_t + 12),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 0), 1)
        cv2.putText(plot, f"Weighted: {weighted_errors[-1]:.2f}m", (margin_l + 5, margin_t + 27),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 0), 1)
        cv2.putText(plot, f"Median: {median_errors[-1]:.2f}m", (margin_l + 5, margin_t + 42),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 0, 255), 1)
        cv2.putText(plot, f"Best Est: {best_est_err_val:.2f}m", (margin_l + 5, margin_t + 57),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 140, 255), 1)
        cv2.putText(plot, f"Drone GPS: {drone_gps_err_val:.2f}m", (margin_l + 5, margin_t + 72),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

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
    use_tiling = [False]  # default: single pass (T to toggle tiling)

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
                fov_h_rad = math.radians(_get_config_fov())
                ground_w = 2 * t_data['rel_alt'] * math.tan(fov_h_rad / 2)
                ground_h = ground_w * vid_h / vid_w
                dx_px = dets[0][0] - vid_w / 2
                dy_px = dets[0][1] - vid_h / 2
                dx_m = dx_px / vid_w * ground_w
                dy_m = dy_px / vid_h * ground_h
                offset_m = math.sqrt(dx_m**2 + dy_m**2)
                lines.append(f"OFFSET {offset_m:.1f}m from center ({dx_m:.1f}m E, {dy_m:.1f}m S)")
                # center_dist in METERS (for smart estimate 4m threshold)
                center_dist = offset_m
                target_estimates.append((t_lat, t_lon, dets[0][4], fnum, center_dist, t_data['rel_alt']))
                # Store frame for smart estimate grid (first 10 central only)
                if args.smart_estimate and center_dist < 4.0 and len(smart_frames) < 10:
                    smart_frames.append((snap_clean.copy(), center_dist, t_lat, t_lon, fnum))
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
    # F key: toggle RAW (30fps, no processing) vs VISION (undistorted, inference synced)
    display_mode = [0]  # 0=RAW, 1=VISION
    DISPLAY_MODES = ["RAW (30fps)", "VISION (undistorted)"]
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
    best_zoom = [1.0]
    best_zoom_center = [disp_w // 2, 300]
    best_drag = [None]
    latest_zoom = [1.0]
    latest_zoom_center = [disp_w // 2, 300]
    latest_drag = [None]
    gps_zoom = [1.0]
    gps_zoom_center = [500, 250]
    gps_drag = [None]

    def _apply_win_zoom(img, zlevel, zcenter):
        """Apply zoom to any window image."""
        if zlevel <= 1.01:
            return img
        h, w = img.shape[:2]
        hw, hh = int(w / (2 * zlevel)), int(h / (2 * zlevel))
        cx = max(hw, min(w - hw, zcenter[0]))
        cy = max(hh, min(h - hh, zcenter[1]))
        zcenter[0], zcenter[1] = cx, cy
        crop = img[cy - hh:cy + hh, cx - hw:cx + hw]
        return cv2.resize(crop, (w, h), interpolation=cv2.INTER_LINEAR)

    def on_best_mouse(event, mx, my, flags, param):
        if event == cv2.EVENT_MOUSEWHEEL:
            if flags > 0:
                best_zoom[0] = min(best_zoom[0] * 1.3, 10.0)
            else:
                best_zoom[0] = max(best_zoom[0] / 1.3, 1.0)
            return
        if event == cv2.EVENT_LBUTTONDOWN and best_zoom[0] > 1.01:
            best_drag[0] = (mx, my, best_zoom_center[0], best_zoom_center[1])
            return
        if event == cv2.EVENT_MOUSEMOVE and best_drag[0] and (flags & cv2.EVENT_FLAG_LBUTTON):
            sx, sy, ocx, ocy = best_drag[0]
            best_zoom_center[0] = max(0, min(disp_w, int(ocx + sx - mx)))
            best_zoom_center[1] = max(0, min(1000, int(ocy + sy - my)))
            return
        if event == cv2.EVENT_LBUTTONUP:
            best_drag[0] = None
            return
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
                    fov_h_rad = math.radians(_get_config_fov())
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

    # FOV Calibration state (B key toggles)
    calibration_mode = [False]
    calib_click_pts = []
    calib_measurements = []  # list of (alt, vid_px_dist, f_px, fov_deg)
    zoom_level = [1.0]
    zoom_center = [disp_w // 2, disp_h // 2]

    # Video pixel dimensions for calibration math
    vid_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    vid_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    disp_scale = disp_w / vid_w  # display pixels per video pixel

    # Distortion toggle (O key): 0=RAW, 1=UNDISTORTED
    distortion_mode = [0]
    DIST_MODES = ["RAW", "UNDISTORTED"]
    _dist_map1 = _dist_map2 = _undist_map1 = _undist_map2 = None

    # Try real calibration file first, fall back to synthetic
    _calib_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__)))), "calibration_data.npz")
    if os.path.exists(_calib_path):
        try:
            _calib = np.load(_calib_path)
            _mtx = _calib["camera_matrix"]
            _dist = _calib["dist_coeffs"]
            _new_mtx, _ = cv2.getOptimalNewCameraMatrix(_mtx, _dist, (vid_w, vid_h), 0, (vid_w, vid_h))
            _undist_map1, _undist_map2 = cv2.initUndistortRectifyMap(
                _mtx, _dist, None, _new_mtx, (vid_w, vid_h), cv2.CV_16SC2)
            # For distort mode, use negative coefficients
            _dist_neg = -_dist.copy()
            _dist_map1, _dist_map2 = cv2.initUndistortRectifyMap(
                _mtx, _dist_neg, None, _new_mtx, (vid_w, vid_h), cv2.CV_16SC2)
            print(f"[DISTORTION] Real calibration loaded (RMS={float(_calib['rms_error']):.3f}). Press O to toggle.")
        except Exception as e:
            print(f"[DISTORTION] Calibration load failed: {e} — using synthetic")
            _dist_map1, _dist_map2, _undist_map1, _undist_map2 = create_synthetic_distortion_maps(vid_h, vid_w)
    else:
        _dist_map1, _dist_map2, _undist_map1, _undist_map2 = create_synthetic_distortion_maps(vid_h, vid_w)
        print(f"[DISTORTION] Synthetic barrel distortion ready. Press O to toggle.")

    def correct_mouse_coords(window_name, mx, my, img_w, img_h):
        """Convert window mouse coords to image coords (handles resized WINDOW_NORMAL)."""
        try:
            _, _, win_w, win_h = cv2.getWindowImageRect(window_name)
            if win_w > 0 and win_h > 0:
                return int(mx * img_w / win_w), int(my * img_h / win_h)
        except cv2.error:
            pass
        return mx, my

    def screen_to_display(sx, sy):
        """Convert screen coords to display coords (accounting for zoom)."""
        z = zoom_level[0]
        cx, cy = zoom_center
        half_w, half_h = disp_w / (2 * z), disp_h / (2 * z)
        return cx - half_w + sx / z, cy - half_h + sy / z

    def apply_zoom(img):
        """Crop and scale image for zoom."""
        z = zoom_level[0]
        if z <= 1.01:
            return img
        h, w = img.shape[:2]
        cx, cy = zoom_center
        half_w, half_h = int(w / (2 * z)), int(h / (2 * z))
        cx = max(half_w, min(w - half_w, cx))
        cy = max(half_h, min(h - half_h, cy))
        zoom_center[0], zoom_center[1] = cx, cy
        crop = img[cy - half_h:cy + half_h, cx - half_w:cx + half_w]
        return cv2.resize(crop, (w, h), interpolation=cv2.INTER_LINEAR)

    _drag_start = [None]  # for pan dragging in zoom mode
    _mouse_pos = [0, 0]  # live mouse position in image coords

    def on_video_mouse(event, mx, my, flags, param):
        # Mouse coords from OpenCV are relative to the rendered image
        # getWindowImageRect returns (x_offset, y_offset, rendered_w, rendered_h)
        try:
            rx, ry, rw, rh = cv2.getWindowImageRect(win)
            if rw > 0 and rh > 0:
                # mx, my are in client area; subtract image offset, then scale to image dims
                ix = float((mx - rx) * disp_w) / rw
                iy = float((my - ry) * disp_h) / rh
                # Clamp to valid range
                ix = max(0.0, min(float(disp_w), ix))
                iy = max(0.0, min(float(disp_h), iy))
            else:
                ix, iy = float(mx), float(my)
        except cv2.error:
            ix, iy = float(mx), float(my)
        _mouse_pos[0], _mouse_pos[1] = int(ix), int(iy)

        if calibration_mode[0]:
            # CALIBRATION MODE
            if event == cv2.EVENT_MOUSEWHEEL:
                if flags > 0:
                    zoom_level[0] = min(zoom_level[0] * 1.3, 10.0)
                else:
                    zoom_level[0] = max(zoom_level[0] / 1.3, 1.0)
                dx, dy = screen_to_display(ix, iy)
                zoom_center[0] = max(0, min(disp_w, int(dx)))
                zoom_center[1] = max(0, min(disp_h, int(dy)))
                return

            # Left-click drag to pan when zoomed
            if event == cv2.EVENT_LBUTTONDOWN and zoom_level[0] > 1.01:
                _drag_start[0] = (ix, iy, zoom_center[0], zoom_center[1])
                return
            if event == cv2.EVENT_MOUSEMOVE and _drag_start[0] is not None and (flags & cv2.EVENT_FLAG_LBUTTON):
                sx, sy, ocx, ocy = _drag_start[0]
                dx = (sx - ix)
                dy = (sy - iy)
                zoom_center[0] = max(0, min(disp_w, int(ocx + dx)))
                zoom_center[1] = max(0, min(disp_h, int(ocy + dy)))
                return
            if event == cv2.EVENT_LBUTTONUP:
                _drag_start[0] = None
                return

            if event == cv2.EVENT_RBUTTONDOWN:
                dx, dy = screen_to_display(ix, iy)
                calib_click_pts.append((dx, dy))
                if len(calib_click_pts) == 2:
                    p1, p2 = calib_click_pts
                    disp_px_dist = math.sqrt((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)
                    vid_px_dist = disp_px_dist / disp_scale
                    alt = last_alt[0]
                    if alt < 1:
                        print("  No altitude data!")
                        calib_click_pts.clear()
                        return
                    f_px = vid_px_dist * alt / 1.8
                    fov_h = 2 * math.degrees(math.atan(vid_w / (2 * f_px)))
                    calib_measurements.append((alt, vid_px_dist, f_px, fov_h))
                    print(f"  CALIB #{len(calib_measurements)}: alt={alt:.1f}m  {vid_px_dist:.0f}px  f={f_px:.0f}px  FOV={fov_h:.1f}deg")
                    if len(calib_measurements) > 1:
                        f_avg = sum(m[2] for m in calib_measurements) / len(calib_measurements)
                        print(f"    Average: f={f_avg:.0f}px  FOV={2*math.degrees(math.atan(vid_w/(2*f_avg))):.1f}deg")
                    calib_click_pts.clear()
                elif len(calib_click_pts) > 2:
                    calib_click_pts.clear()
            elif event == cv2.EVENT_MBUTTONDOWN:
                calib_click_pts.clear()
        else:
            # NORMAL MEASURE MODE
            if event == cv2.EVENT_RBUTTONDOWN:
                vid_measure_pts.append((ix, iy))
                if len(vid_measure_pts) == 2:
                    p1, p2 = vid_measure_pts
                    px_dist = math.sqrt((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)
                    alt = last_alt[0]
                    fov_h_rad = math.radians(_get_config_fov())
                    ground_w = 2 * alt * math.tan(fov_h_rad / 2)
                    m_per_disp_px = ground_w / disp_w
                    m_dist = px_dist * m_per_disp_px
                    vid_measure_result[0] = (p1, p2, px_dist, m_dist, alt)
                    print(f"  VIDEO MEASURE: {px_dist:.0f} img-px = {m_dist:.2f}m (at {alt:.1f}m alt)")
                    vid_measure_pts.clear()
                elif len(vid_measure_pts) > 2:
                    vid_measure_pts.clear()
            elif event == cv2.EVENT_MBUTTONDOWN or event == cv2.EVENT_LBUTTONDOWN:
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

            # Undistort at input — BEFORE anything sees this frame
            # Display, AI, GPS estimation all get the same undistorted image
            if config.UNDISTORT_ENABLED and _undist_map1 is not None:
                frame = cv2.remap(frame, _undist_map1, _undist_map2, cv2.INTER_LINEAR)

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
        _render_start = time.time()  # measure rendering time for smooth playback

        # === DISPLAY ===
        if frame is not None:
            # Show the weather-affected frame so user sees what the model sees
            # F=VISION shows AI-processed frame (undistorted + boxes), F=RAW shows raw
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
                    f"Lens: {DIST_MODES[distortion_mode[0]]} (O=toggle)",
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
                snap_with_info = _apply_win_zoom(snap_with_info, latest_zoom[0], latest_zoom_center)
                cv2.imshow("Latest Detection", snap_with_info)
                def _on_latest_mouse(event, mx, my, flags, param):
                    if event == cv2.EVENT_MOUSEWHEEL:
                        if flags > 0:
                            latest_zoom[0] = min(latest_zoom[0] * 1.3, 10.0)
                        else:
                            latest_zoom[0] = max(latest_zoom[0] / 1.3, 1.0)
                    elif event == cv2.EVENT_LBUTTONDOWN and latest_zoom[0] > 1.01:
                        latest_drag[0] = (mx, my, latest_zoom_center[0], latest_zoom_center[1])
                    elif event == cv2.EVENT_MOUSEMOVE and latest_drag[0] and (flags & cv2.EVENT_FLAG_LBUTTON):
                        sx, sy, ocx, ocy = latest_drag[0]
                        latest_zoom_center[0] = max(0, min(1000, int(ocx + sx - mx)))
                        latest_zoom_center[1] = max(0, min(1000, int(ocy + sy - my)))
                    elif event == cv2.EVENT_LBUTTONUP:
                        latest_drag[0] = None
                cv2.setMouseCallback("Latest Detection", _on_latest_mouse)

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
                p1i, p2i = (int(p1[0]), int(p1[1])), (int(p2[0]), int(p2[1]))
                cv2.line(disp, p1i, p2i, (0, 255, 255), 2)
                cv2.circle(disp, p1i, 4, (0, 255, 255), -1)
                cv2.circle(disp, p2i, 4, (0, 255, 255), -1)
                mid = ((p1i[0]+p2i[0])//2, (p1i[1]+p2i[1])//2)
                cv2.putText(disp, f"{m_d:.2f}m (at {m_alt:.0f}m)", (mid[0]+8, mid[1]-8),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 2)
            if len(vid_measure_pts) == 1:
                pt = (int(vid_measure_pts[0][0]), int(vid_measure_pts[0][1]))
                cv2.circle(disp, pt, 4, (0, 255, 255), -1)

            # HUD bar at bottom of video
            bar_y = disp_h - 30
            cv2.rectangle(disp, (0, bar_y), (disp_w, disp_h), (0, 0, 0), -1)
            progress = frame_num / total_frames
            cv2.rectangle(disp, (0, bar_y), (int(disp_w * progress), bar_y + 4), (0, 200, 200), -1)
            mode = f"TILE {args.tile_size}px" if use_tiling[0] else "SINGLE 640"
            _model_paths = [args.model, args.model2, args.model3, args.model4]
            _cur_path = _model_paths[active_model[0]] if active_model[0] < len(_model_paths) else _model_paths[0]
            m_name = os.path.basename(os.path.dirname(_cur_path)) or "root"
            m_file = os.path.basename(_cur_path)
            model_tag = f"{m_name}/{m_file}" if m_name != "root" else m_file
            model_num = active_model[0] + 1
            n_models = len(models)
            eff_name = EFFECTS[active_effect[0]].upper()
            eff_str = f" | WX: {eff_name} {effect_intensity[0]:.0%}" if eff_name != "NONE" else ""
            fps_val = 1000.0 / dt if dt > 0 else 0
            play_mode = DISPLAY_MODES[display_mode[0]]
            # Time as MM:SS
            t_min, t_sec = int(timestamp // 60), timestamp % 60
            d_min, d_sec = int(duration // 60), duration % 60
            time_str = f"{t_min}:{t_sec:04.1f} / {d_min}:{d_sec:04.1f}"
            # Line 1: time + speed (bigger, more visible)
            line1 = f"{time_str}  |  {speed:.1f}x  |  {play_mode}  |  [{model_tag}] ({model_num}/{n_models})"
            # Line 2: technical info
            line2 = f"{dt:.0f}ms {fps_val:.1f}fps | Det: {det_count[0]} | Conf>={args.conf:.2f} | {mode} | M=model F=speed C=clear X=best [/]=conf{eff_str}"
            cv2.rectangle(disp, (0, disp_h - 50), (disp_w, disp_h), (0, 0, 0), -1)
            cv2.putText(disp, line1, (10, disp_h - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)
            cv2.putText(disp, line2, (10, disp_h - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.40, (160, 160, 160), 1)

            # Weather effect badge (top-right)
            if EFFECTS[active_effect[0]] != "none":
                badge = f"WX: {eff_name} ({effect_intensity[0]:.0%})"
                badge_w = len(badge) * 11 + 16
                cv2.rectangle(disp, (disp_w - badge_w, 0), (disp_w, 28), (0, 0, 120), -1)
                cv2.putText(disp, badge, (disp_w - badge_w + 8, 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 200, 255), 1)

            # Calibration mode: zoom FIRST, then draw overlay on top
            if calibration_mode[0]:
                disp = apply_zoom(disp)

                # Draw click points (in zoomed screen space)
                z = zoom_level[0]
                cx_z, cy_z = zoom_center
                hw = disp_w / (2 * z)
                hh = disp_h / (2 * z)
                for pt in calib_click_pts:
                    if z > 1.01:
                        sp_x = int((pt[0] - (cx_z - hw)) * z)
                        sp_y = int((pt[1] - (cy_z - hh)) * z)
                    else:
                        sp_x, sp_y = int(pt[0]), int(pt[1])
                    cv2.circle(disp, (sp_x, sp_y), 6, (0, 255, 255), -1)
                    cv2.circle(disp, (sp_x, sp_y), 8, (255, 255, 255), 2)
                if len(calib_click_pts) == 1:
                    cv2.putText(disp, "Now click FEET of dummy", (10, 100),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

                # Header (drawn after zoom so text is always readable)
                z_str = f"  Zoom: {z:.1f}x" if z > 1.01 else ""
                _calib_h = 100 if calib_measurements else 60
                cv2.rectangle(disp, (0, 0), (disp_w, _calib_h), (0, 0, 0), -1)
                cv2.putText(disp, f"CALIBRATION  Alt: {last_alt[0]:.1f}m{z_str}  Frame: {frame_num}", (8, 24),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                cv2.putText(disp, "Right-click HEAD then FEET | Scroll=zoom | Drag=pan | B=exit", (8, 48),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)
                if calib_measurements:
                    f_avg = sum(m[2] for m in calib_measurements) / len(calib_measurements)
                    fov_avg = 2 * math.degrees(math.atan(vid_w / (2 * f_avg)))
                    f_vals = [m[2] for m in calib_measurements]
                    spread = (max(f_vals) - min(f_vals)) / f_avg * 100 if f_avg > 0 else 0
                    color = (0, 255, 0) if spread < 5 else ((0, 200, 255) if spread < 15 else (0, 0, 255))
                    # Focal length + FOV
                    cv2.putText(disp, f"f={f_avg:.0f}px  FOV={fov_avg:.1f}deg  spread={spread:.1f}%  ({len(calib_measurements)} samples)", (8, 72),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                    # Config.py value (for Pi camera: f_mm = f_px * 5.02 / 1456)
                    f_mm_pi = f_avg * 5.02 / 1456
                    cv2.putText(disp, f"config.py: FOCAL_LENGTH_MM = {f_mm_pi:.2f}  (if Pi camera)", (8, 94),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 0), 1)

            # Debug: draw mouse crosshair so we can verify coord accuracy
            _mx, _my = _mouse_pos
            if 0 < _mx < disp_w and 0 < _my < disp_h:
                cv2.line(disp, (_mx - 8, _my), (_mx + 8, _my), (0, 0, 255), 1)
                cv2.line(disp, (_mx, _my - 8), (_mx, _my + 8), (0, 0, 255), 1)

            if writer:
                writer.write(disp)
            cv2.imshow(win, disp)

            # GPS plots window (center distance + altitude side by side)
            if args.smart_estimate:
                plot_smart = draw_smart_bullseye()
                plot_center = draw_gps_plot_by_center()
                plot_alt = draw_gps_plot_by_alt()
                sep = np.zeros((plot_size, 2, 3), dtype=np.uint8)
                sep[:] = (60, 60, 60)
                plot_conv = draw_error_convergence()
                gps_combined = np.hstack([plot_smart, sep, plot_center, sep.copy(), plot_conv, sep.copy(), plot_alt])
            else:
                plot_center = draw_gps_plot_by_center()
                plot_alt = draw_gps_plot_by_alt()
                sep = np.zeros((plot_size, 2, 3), dtype=np.uint8)
                sep[:] = (60, 60, 60)
                gps_combined = np.hstack([plot_center, sep, plot_alt])
            gps_combined = _apply_win_zoom(gps_combined, gps_zoom[0], gps_zoom_center)
            cv2.imshow("Target GPS Estimates", gps_combined)

            def _on_gps_mouse(event, mx, my, flags, param):
                if event == cv2.EVENT_MOUSEWHEEL:
                    if flags > 0:
                        gps_zoom[0] = min(gps_zoom[0] * 1.3, 10.0)
                    else:
                        gps_zoom[0] = max(gps_zoom[0] / 1.3, 1.0)
                elif event == cv2.EVENT_LBUTTONDOWN and gps_zoom[0] > 1.01:
                    gps_drag[0] = (mx, my, gps_zoom_center[0], gps_zoom_center[1])
                elif event == cv2.EVENT_MOUSEMOVE and gps_drag[0] and (flags & cv2.EVENT_FLAG_LBUTTON):
                    sx, sy, ocx, ocy = gps_drag[0]
                    gps_zoom_center[0] = max(0, min(2000, int(ocx + sx - mx)))
                    gps_zoom_center[1] = max(0, min(1000, int(ocy + sy - my)))
                elif event == cv2.EVENT_LBUTTONUP:
                    gps_drag[0] = None
            cv2.setMouseCallback("Target GPS Estimates", _on_gps_mouse)

            # Smart frames grid (first 10 central detections)
            if args.smart_estimate and smart_frames:
                thumb_w, thumb_h = 240, 180
                cols = 5
                rows = 2
                grid = np.zeros((rows * thumb_h, cols * thumb_w, 3), dtype=np.uint8)
                for i, (sf, sd, slat, slon, sfnum) in enumerate(smart_frames):
                    r, c = i // cols, i % cols
                    thumb = cv2.resize(sf, (thumb_w, thumb_h))
                    # Label: frame number + distance from center
                    cv2.rectangle(thumb, (0, thumb_h - 22), (thumb_w, thumb_h), (0, 0, 0), -1)
                    cv2.putText(thumb, f"#{i+1} f{sfnum} {sd:.1f}m", (4, thumb_h - 6),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 255), 1)
                    # Border: green if within 2m, yellow if within 4m
                    bcolor = (0, 255, 0) if sd < 2.0 else (0, 200, 255)
                    cv2.rectangle(thumb, (0, 0), (thumb_w - 1, thumb_h - 1), bcolor, 2)
                    grid[r * thumb_h:(r + 1) * thumb_h, c * thumb_w:(c + 1) * thumb_w] = thumb
                cv2.imshow("SMART Frames (10 central)", grid)

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
                bs_resized = _apply_win_zoom(bs_resized, best_zoom[0], best_zoom_center)
                cv2.imshow(best_win, bs_resized)
                cv2.setMouseCallback(best_win, on_best_mouse)

        # Adaptive timing: subtract rendering time from target interval
        _render_ms = (time.time() - _render_start) * 1000
        if display_mode[0] == 0:  # RAW: play at video fps
            _target_ms = 1000.0 / fps / speed
            delay = max(1, int(_target_ms - _render_ms))
        elif not paused:
            delay = max(1, int((1000 / fps) / speed))
        else:
            delay = 50
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
        elif key == ord('f'):
            display_mode[0] = 1 - display_mode[0]
            print(f"  Display: {DISPLAY_MODES[display_mode[0]]}")
        elif key == ord('c'):
            target_estimates.clear()
            smart_frames.clear()
            det_count[0] = 0
            best_snapshot[0] = None
            best_center_dist[0] = 999.0
            print("  CLEARED all: GPS estimates, smart frames, best detection")
        elif key == ord('x'):
            best_snapshot[0] = None
            best_center_dist[0] = 999.0
            print("  CLEARED best detection — will pick new best from now")
        elif key == ord('b'):
            calibration_mode[0] = not calibration_mode[0]
            if calibration_mode[0]:
                paused = True
                zoom_level[0] = 1.0
                calib_click_pts.clear()
                # Force undistortion on during calibration
                if _undist_map1 is not None:
                    distortion_mode[0] = 1  # UNDISTORTED
                print("\n  CALIBRATION MODE ON (undistortion forced) — Right-click HEAD then FEET. Scroll=zoom. B=exit.")
            else:
                zoom_level[0] = 1.0
                calib_click_pts.clear()
                if calib_measurements:
                    f_avg = sum(m[2] for m in calib_measurements) / len(calib_measurements)
                    fov_avg = 2 * math.degrees(math.atan(vid_w / (2 * f_avg)))
                    f_mm_new = f_avg * config.SENSOR_WIDTH_MM / vid_w
                    print(f"\n  CALIBRATION RESULT: f={f_avg:.0f}px  FOV={fov_avg:.1f}deg  ({len(calib_measurements)} samples)")
                    print(f"  FOCAL_LENGTH_MM: {config.FOCAL_LENGTH_MM:.2f} -> {f_mm_new:.2f}")
                    # Update config.py automatically
                    try:
                        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "config.py")
                        with open(config_path, 'r') as f:
                            cfg_text = f.read()
                        import re
                        cfg_text = re.sub(
                            r'FOCAL_LENGTH_MM\s*=\s*[\d.]+',
                            f'FOCAL_LENGTH_MM = {f_mm_new:.2f}',
                            cfg_text)
                        with open(config_path, 'w') as f:
                            f.write(cfg_text)
                        config.FOCAL_LENGTH_MM = f_mm_new
                        print(f"  UPDATED config.py: FOCAL_LENGTH_MM = {f_mm_new:.2f}")
                        print(f"  NOTE: This is correct ONLY if video was from Pi camera (49 deg FOV)")
                        print(f"        DJI video gives DJI focal length — do NOT use for Pi config!")
                    except Exception as e:
                        print(f"  Could not update config.py: {e}")
                        print(f"  Manually set: FOCAL_LENGTH_MM = {f_mm_new:.2f}")
                print("  CALIBRATION MODE OFF")
        elif key == ord('o'):
            # Toggle undistortion in vision.py
            if vs and hasattr(vs, 'undistort_enabled'):
                vs.undistort_enabled = not vs.undistort_enabled
                if vs.undistort_enabled:
                    vs._init_undistortion(vid_w, vid_h)
                    status = "ON"
                else:
                    vs._undistort_map1 = None
                    vs._undistort_map2 = None
                    status = "OFF"
                print(f"  UNDISTORTION: {status}")
                # Also toggle for all loaded models
                for m in models.values():
                    m.undistort_enabled = vs.undistort_enabled
                    if vs.undistort_enabled:
                        m._init_undistortion(vid_w, vid_h)
                    else:
                        m._undistort_map1 = None
                        m._undistort_map2 = None
        elif key == 82 or key == ord('['):  # up arrow or [
            args.conf = min(args.conf + 0.05, 0.95)
            print(f"  Confidence threshold: {args.conf:.2f}")
        elif key == 84 or key == ord(']'):  # down arrow or ]
            args.conf = max(args.conf - 0.05, 0.05)
            print(f"  Confidence threshold: {args.conf:.2f}")

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
