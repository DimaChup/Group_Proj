#!/usr/bin/env python3
"""
GPS Cluster Comparison — Run detection over full DJI video with different settings,
compare GPS estimate clusters.

Tests combinations of:
  - Undistortion ON / OFF
  - Different FOV values
  - COCO human model

Outputs: comparison plot showing GPS scatter for each configuration.
"""
import sys
import os
import time
import math
import csv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import cv2
import numpy as np
import config

# ── SRT parser (same as video_test_compare) ──
def parse_srt(srt_path):
    import re
    with open(srt_path, 'r') as f:
        text = f.read()
    entries = {}
    blocks = re.split(r'\n\n+', text.strip())
    frame = 0
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) < 3:
            continue
        try:
            int(lines[0])
        except ValueError:
            continue
        frame += 1
        data_line = ' '.join(lines[2:])
        lat = lon = alt = yaw = pitch = 0.0
        for pattern, key in [
            (r'\[latitude:\s*([-\d.]+)\]', 'lat'),
            (r'\[longitude:\s*([-\d.]+)\]', 'lon'),
            (r'\[rel_alt:\s*([-\d.]+)', 'rel_alt'),
            (r'\[abs_alt:\s*([-\d.]+)', 'abs_alt'),
        ]:
            m = re.search(pattern, data_line)
            if m:
                if key == 'lat': lat = float(m.group(1))
                elif key == 'lon': lon = float(m.group(1))
                elif key == 'rel_alt': alt = float(m.group(1))
        # Yaw from gb_yaw
        m = re.search(r'gb_yaw:\s*([-\d.]+)', data_line)
        if m: yaw = float(m.group(1))
        m = re.search(r'gb_pitch:\s*([-\d.]+)', data_line)
        if m: pitch = float(m.group(1))
        entries[frame] = {'lat': lat, 'lon': lon, 'rel_alt': alt, 'yaw': yaw, 'pitch': pitch}
    return entries


def estimate_gps(drone_lat, drone_lon, alt, yaw, px, py, img_w, img_h, fov_h_deg):
    fov_h_rad = math.radians(fov_h_deg)
    ground_w = 2 * alt * math.tan(fov_h_rad / 2)
    ground_h = ground_w * img_h / img_w
    dx_m = (px - img_w / 2) / img_w * ground_w
    dy_m = -(py - img_h / 2) / img_h * ground_h
    yaw_rad = math.radians(yaw)
    north = dy_m * math.cos(yaw_rad) - dx_m * math.sin(yaw_rad)
    east = dy_m * math.sin(yaw_rad) + dx_m * math.cos(yaw_rad)
    R = 6378137.0
    d_lat = (north / R) * (180 / math.pi)
    d_lon = (east / (R * math.cos(math.radians(drone_lat)))) * (180 / math.pi)
    return drone_lat + d_lat, drone_lon + d_lon


def run_detection_pass(video_path, srt_path, model_path, fov_deg, undistort_maps=None, label="", conf_thresh=0.3):
    """Run detection over entire video, return list of (est_lat, est_lon, conf, alt)."""
    from vision import VisionSystem

    print(f"\n  Running: {label}")
    print(f"    Model: {os.path.basename(model_path)}")
    print(f"    FOV: {fov_deg:.1f} deg")
    print(f"    Undistort: {'ON' if undistort_maps else 'OFF'}")

    vs = VisionSystem(camera_index=None, model_path=model_path, undistort=False)
    if not vs.using_ai:
        print(f"    FAILED to load model!")
        return []

    cap = cv2.VideoCapture(video_path)
    telem = parse_srt(srt_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    vid_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    vid_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    estimates = []
    det_count = 0
    frame_num = 0
    every = 10  # process every 10th frame (faster, still enough samples)

    t0 = time.time()
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_num += 1

        if frame_num % every != 0:
            continue

        # Apply undistortion at input level
        if undistort_maps is not None:
            frame = cv2.remap(frame, undistort_maps[0], undistort_maps[1], cv2.INTER_LINEAR)

        # Resize for detection
        det_h = int(vid_h * 640 / vid_w)
        det_frame = cv2.resize(frame, (640, det_h))
        found, x, y, conf = vs.detect_in_image(det_frame)

        if found and conf >= conf_thresh:
            det_count += 1
            # Scale coords back to video resolution
            scale_x = vid_w / 640
            scale_y = vid_h / det_h
            px = x * scale_x
            py = y * scale_y

            t_data = telem.get(frame_num)
            if t_data and t_data['lat'] != 0:
                est_lat, est_lon = estimate_gps(
                    t_data['lat'], t_data['lon'], t_data['rel_alt'],
                    t_data['yaw'], px, py, vid_w, vid_h, fov_deg)
                estimates.append((est_lat, est_lon, conf, t_data['rel_alt']))

        # Progress
        if frame_num % 300 == 0:
            elapsed = time.time() - t0
            pct = 100 * frame_num / total_frames
            print(f"    {pct:.0f}% ({frame_num}/{total_frames}) — {det_count} detections — {elapsed:.1f}s")

    cap.release()
    elapsed = time.time() - t0
    print(f"    Done: {det_count} detections in {elapsed:.1f}s")
    return estimates


def plot_comparison(results, output_path="gps_cluster_comparison.png"):
    """Create beautiful comparison plot of GPS clusters."""
    n = len(results)
    cols = min(3, n)
    rows = (n + cols - 1) // cols

    fig_w = 400 * cols
    fig_h = 400 * rows + 60
    fig = np.zeros((fig_h, fig_w, 3), dtype=np.uint8)
    fig[:] = (30, 30, 30)

    # Title
    cv2.putText(fig, "GPS Estimate Cluster Comparison", (fig_w // 2 - 250, 35),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)

    for idx, (label, estimates) in enumerate(results):
        row = idx // cols
        col = idx % cols
        ox = col * 400
        oy = row * 400 + 60

        # Background
        cv2.rectangle(fig, (ox + 5, oy + 5), (ox + 395, oy + 395), (50, 50, 50), -1)
        cv2.rectangle(fig, (ox + 5, oy + 5), (ox + 395, oy + 395), (100, 100, 100), 1)

        # Label
        cv2.putText(fig, label, (ox + 15, oy + 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

        if not estimates:
            cv2.putText(fig, "No detections", (ox + 100, oy + 200),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1)
            continue

        lats = [e[0] for e in estimates]
        lons = [e[1] for e in estimates]
        confs = [e[2] for e in estimates]

        # Stats
        mean_lat = sum(lats) / len(lats)
        mean_lon = sum(lons) / len(lons)

        # CEP50 (circular error probable — median distance from mean)
        dists = []
        for lat, lon in zip(lats, lons):
            dn = (lat - mean_lat) * 111320
            de = (lon - mean_lon) * 111320 * math.cos(math.radians(mean_lat))
            dists.append(math.sqrt(dn**2 + de**2))
        dists.sort()
        cep50 = dists[len(dists) // 2] if dists else 0
        max_spread = max(dists) if dists else 0

        # Plot area
        plot_x = ox + 20
        plot_y = oy + 40
        plot_w = 360
        plot_h = 280

        # Grid (auto-scale)
        if max_spread > 0:
            grid_m = max_spread * 1.3
        else:
            grid_m = 10

        # Draw grid
        for i in range(5):
            gy = plot_y + int(plot_h * i / 4)
            cv2.line(fig, (plot_x, gy), (plot_x + plot_w, gy), (60, 60, 60), 1)
            gx = plot_x + int(plot_w * i / 4)
            cv2.line(fig, (gx, plot_y), (gx, plot_y + plot_h), (60, 60, 60), 1)

        # Grid labels
        cv2.putText(fig, f"{grid_m:.0f}m", (plot_x + plot_w - 35, plot_y + plot_h + 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.3, (150, 150, 150), 1)

        # Plot points
        for lat, lon, conf in zip(lats, lons, confs):
            dn = (lat - mean_lat) * 111320
            de = (lon - mean_lon) * 111320 * math.cos(math.radians(mean_lat))

            px = plot_x + int(plot_w / 2 + (de / grid_m) * (plot_w / 2))
            py_pt = plot_y + int(plot_h / 2 - (dn / grid_m) * (plot_h / 2))

            # Color by confidence (green=high, red=low)
            g = int(255 * min(1, conf))
            r = int(255 * (1 - min(1, conf)))
            cv2.circle(fig, (px, py_pt), 3, (0, g, r), -1)

        # Mean marker (white cross)
        cx = plot_x + plot_w // 2
        cy = plot_y + plot_h // 2
        cv2.line(fig, (cx - 8, cy), (cx + 8, cy), (255, 255, 255), 2)
        cv2.line(fig, (cx, cy - 8), (cx, cy + 8), (255, 255, 255), 2)

        # Stats text
        stats_y = oy + 335
        cv2.putText(fig, f"N={len(estimates)}  CEP50={cep50:.1f}m  Max={max_spread:.1f}m",
                    (ox + 15, stats_y), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
        cv2.putText(fig, f"Mean: {mean_lat:.6f}, {mean_lon:.6f}",
                    (ox + 15, stats_y + 18), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (150, 150, 150), 1)

        # Color indicator
        color = (0, 255, 0) if cep50 < 5 else ((0, 200, 255) if cep50 < 10 else (0, 0, 255))
        cv2.circle(fig, (ox + 375, oy + 20), 8, color, -1)

    cv2.imwrite(output_path, fig)
    print(f"\n  Saved comparison plot: {output_path}")
    return fig


def main():
    video = "RealVideo/DJI_0001_1456x1088_cropped_30fps.mp4"
    srt = "RealVideo/DJI_20260311172332_0001_V.SRT"
    model = "cv_models/human.tflite"

    if not os.path.exists(video):
        print(f"Video not found: {video}")
        return
    if not os.path.exists(srt):
        print(f"SRT not found: {srt}")
        return

    # Load undistortion maps
    undist_maps = None
    calib_path = "calibration_data.npz"
    if os.path.exists(calib_path):
        try:
            calib = np.load(calib_path)
            mtx = calib["camera_matrix"]
            dist = calib["dist_coeffs"]
            new_mtx, _ = cv2.getOptimalNewCameraMatrix(mtx, dist, (1456, 1088), 0, (1456, 1088))
            m1, m2 = cv2.initUndistortRectifyMap(mtx, dist, None, new_mtx, (1456, 1088), cv2.CV_16SC2)
            undist_maps = (m1, m2)
            print(f"Loaded calibration: k1={dist[0][0]:.2f}")
        except Exception as e:
            print(f"Calibration load failed: {e}")

    # FOV values to test
    fov_dji = 54.4  # calibrated for DJI
    fov_pi = 2 * math.degrees(math.atan(config.SENSOR_WIDTH_MM / (2 * config.FOCAL_LENGTH_MM)))

    print("=" * 60)
    print("  GPS CLUSTER COMPARISON")
    print(f"  Video: {video}")
    print(f"  Model: {model}")
    print(f"  FOV DJI: {fov_dji:.1f} deg")
    print(f"  FOV Pi (config): {fov_pi:.1f} deg")
    print(f"  Undistortion: {'available' if undist_maps else 'not available'}")
    print("=" * 60)

    results = []

    # Test 1: No undistortion, DJI FOV
    est = run_detection_pass(video, srt, model, fov_dji, None,
                             f"RAW + DJI FOV ({fov_dji:.0f}deg)")
    results.append((f"RAW + DJI FOV ({fov_dji:.0f}°)", est))

    # Test 2: No undistortion, Pi FOV
    est = run_detection_pass(video, srt, model, fov_pi, None,
                             f"RAW + Pi FOV ({fov_pi:.0f}deg)")
    results.append((f"RAW + Pi FOV ({fov_pi:.0f}°)", est))

    # Test 3: Undistortion ON, DJI FOV
    if undist_maps:
        est = run_detection_pass(video, srt, model, fov_dji, undist_maps,
                                 f"UNDISTORT + DJI FOV ({fov_dji:.0f}deg)")
        results.append((f"UNDIST + DJI FOV ({fov_dji:.0f}°)", est))

    # Test 4: Undistortion ON, Pi FOV
    if undist_maps:
        est = run_detection_pass(video, srt, model, fov_pi, undist_maps,
                                 f"UNDISTORT + Pi FOV ({fov_pi:.0f}deg)")
        results.append((f"UNDIST + Pi FOV ({fov_pi:.0f}°)", est))

    # Plot comparison
    fig = plot_comparison(results)

    # Show it
    cv2.namedWindow("GPS Cluster Comparison", cv2.WINDOW_NORMAL)
    cv2.imshow("GPS Cluster Comparison", fig)
    print("\n  Press any key to close...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
