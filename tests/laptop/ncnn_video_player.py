#!/usr/bin/env python3
"""
NCNN Video Player — play video with NCNN detection on Pi.

Simple: reads video frame by frame, runs NCNN inference, shows result.
No threading, no complexity. Just camera-like playback with detection.

Usage on Pi:
    source ncnn_env/bin/activate
    python tests/laptop/ncnn_video_player.py

Controls:
    SPACE = pause/resume
    D = skip forward 5s
    A = skip back 5s
    T = toggle tiling
    Q = quit
"""
import sys
import os
import time

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, project_root)
os.chdir(project_root)

import cv2
import numpy as np

# NCNN detection
try:
    import ncnn
    HAS_NCNN = True
except ImportError:
    HAS_NCNN = False
    print("[!] ncnn not installed. Run: pip install ncnn")

VIDEO = "RealVideo/DJI_0001_1456x1088_cropped_30fps.mp4"
MODEL_DIR = "cv_models/sar_v2_1088/ncnn/best_ncnn_model"
CONF = 0.2

# CLI overrides
for i, arg in enumerate(sys.argv):
    if arg == "--video" and i + 1 < len(sys.argv):
        VIDEO = sys.argv[i + 1]
    elif arg == "--conf" and i + 1 < len(sys.argv):
        CONF = float(sys.argv[i + 1])
    elif arg == "--model" and i + 1 < len(sys.argv):
        MODEL_DIR = sys.argv[i + 1]


def load_ncnn_model(model_dir):
    """Load NCNN model directly — no vision.py dependency."""
    param = os.path.join(model_dir, "model.ncnn.param")
    binf = os.path.join(model_dir, "model.ncnn.bin")
    if not os.path.exists(param):
        print(f"[!] NCNN model not found: {param}")
        return None
    net = ncnn.Net()
    net.opt.num_threads = 4
    net.opt.use_vulkan_compute = False
    net.load_param(param)
    net.load_model(binf)
    # Warmup
    mat = ncnn.Mat(640, 640, 3)
    ex = net.create_extractor()
    ex.input("in0", mat)
    ex.extract("out0")
    return net


def detect_ncnn(net, frame, conf_thresh):
    """Run NCNN inference on frame. Returns (found, cx, cy, conf, x1, y1, x2, y2)."""
    h, w = frame.shape[:2]
    img = cv2.resize(frame, (640, 640))
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    mat_in = ncnn.Mat.from_pixels(img_rgb, ncnn.Mat.PixelType.PIXEL_RGB, 640, 640)
    mean_vals = [0.0, 0.0, 0.0]
    norm_vals = [1/255.0, 1/255.0, 1/255.0]
    mat_in.substract_mean_normalize(mean_vals, norm_vals)

    ex = net.create_extractor()
    ex.input("in0", mat_in)
    ret, mat_out = ex.extract("out0")

    output = np.array(mat_out)
    if output.ndim == 2:
        preds = output
    else:
        preds = output.reshape(-1, output.shape[-1]) if output.ndim == 3 else output

    if preds.shape[0] < preds.shape[-1]:
        preds = preds.T

    best_conf = 0.0
    best_det = None
    for det in preds:
        cls_id = int(np.argmax(det[4:]))
        conf = float(det[4 + cls_id])
        if conf > conf_thresh and conf > best_conf:
            best_conf = conf
            best_det = det

    if best_det is not None:
        raw_cx, raw_cy = best_det[0], best_det[1]
        raw_bw, raw_bh = best_det[2], best_det[3]
        # Auto-detect pixel vs normalized coords
        if raw_cx > 1.5:
            cx = int(raw_cx * w / 640)
            cy = int(raw_cy * h / 640)
            bw = int(raw_bw * w / 640)
            bh = int(raw_bh * h / 640)
        else:
            cx = int(raw_cx * w)
            cy = int(raw_cy * h)
            bw = int(raw_bw * w)
            bh = int(raw_bh * h)
        x1 = max(0, cx - bw // 2)
        y1 = max(0, cy - bh // 2)
        x2 = min(w, cx + bw // 2)
        y2 = min(h, cy + bh // 2)
        return True, cx, cy, best_conf, x1, y1, x2, y2

    return False, 0, 0, 0, 0, 0, 0, 0


def main():
    if not HAS_NCNN:
        return

    print("=" * 60)
    print("  NCNN VIDEO PLAYER")
    print(f"  Video: {VIDEO}")
    print(f"  Model: {MODEL_DIR}")
    print(f"  Conf:  {CONF}")
    print("=" * 60)

    if not os.path.exists(VIDEO):
        print(f"[!] Video not found: {VIDEO}")
        return

    print("Loading NCNN model...")
    net = load_ncnn_model(MODEL_DIR)
    if net is None:
        return
    print("NCNN loaded!")

    cap = cv2.VideoCapture(VIDEO)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    vid_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    vid_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration = total / fps
    print(f"Video: {vid_w}x{vid_h} @ {fps:.0f}fps, {total} frames, {duration:.0f}s")
    print("\nControls: SPACE=pause D=skip A=back T=tiling Q=quit")

    cv2.namedWindow("NCNN Video Player", cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)

    paused = False
    tiling = False
    det_count = 0
    frame_count = 0
    inf_times = []

    while True:
        if not paused:
            ret, frame = cap.read()
            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
            frame_count = int(cap.get(cv2.CAP_PROP_POS_FRAMES))

        display = frame.copy()

        # Detection
        t0 = time.perf_counter()
        if tiling:
            # 2x2 tiling
            th, tw = vid_h // 2, vid_w // 2
            for ty in range(2):
                for tx in range(2):
                    tile = display[ty*th:(ty+1)*th, tx*tw:(tx+1)*tw]
                    found, cx, cy, conf, x1, y1, x2, y2 = detect_ncnn(net, tile, CONF)
                    if found:
                        det_count += 1
                        ox, oy = tx * tw, ty * th
                        cv2.rectangle(display, (x1+ox, y1+oy), (x2+ox, y2+oy), (0, 255, 0), 2)
                        cv2.putText(display, f"{conf:.2f}", (x1+ox, y1+oy-10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        else:
            found, cx, cy, conf, x1, y1, x2, y2 = detect_ncnn(net, display, CONF)
            if found:
                det_count += 1
                cv2.rectangle(display, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(display, f"{conf:.2f}", (x1, y1-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                # Pink dot on detection center
                cv2.circle(display, (cx, cy), 8, (255, 0, 255), -1)
                cv2.circle(display, (cx, cy), 8, (255, 255, 255), 2)
                # Crosshair at frame center
                fcx, fcy = vid_w // 2, vid_h // 2
                cv2.line(display, (fcx - 20, fcy), (fcx + 20, fcy), (255, 255, 255), 1)
                cv2.line(display, (fcx, fcy - 20), (fcx, fcy + 20), (255, 255, 255), 1)
                # Pink line from center to detection
                cv2.line(display, (fcx, fcy), (cx, cy), (255, 0, 255), 2)

        dt = (time.perf_counter() - t0) * 1000
        inf_times.append(dt)
        if len(inf_times) > 30:
            inf_times.pop(0)
        avg_ms = sum(inf_times) / len(inf_times)
        eff_fps = 1000 / avg_ms if avg_ms > 0 else 0

        # HUD
        timestamp = frame_count / fps
        progress = frame_count / total if total > 0 else 0

        cv2.putText(display, "NCNN v2-1088", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        cv2.putText(display, f"FPS: {eff_fps:.1f} ({avg_ms:.0f}ms)", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0) if eff_fps > 8 else (0, 255, 255), 2)
        cv2.putText(display, f"Det: {det_count}  Tiling: {'ON' if tiling else 'OFF'}", (10, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(display, f"{timestamp:.1f}s / {duration:.1f}s ({progress*100:.0f}%)", (10, vid_h - 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

        # Progress bar
        bar_y = vid_h - 5
        cv2.rectangle(display, (0, bar_y), (vid_w, vid_h), (50, 50, 50), -1)
        cv2.rectangle(display, (0, bar_y), (int(vid_w * progress), vid_h), (0, 255, 0), -1)

        if paused:
            cv2.putText(display, "PAUSED", (vid_w//2 - 80, vid_h//2),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)

        # Resize if too big
        if vid_w > 1200:
            scale = 1000 / vid_w
            display = cv2.resize(display, (int(vid_w*scale), int(vid_h*scale)))

        cv2.imshow("NCNN Video Player", display)

        key = cv2.waitKey(1 if not paused else 50) & 0xFF
        if key == ord('q') or key == 27:
            break
        elif key == ord(' '):
            paused = not paused
        elif key == ord('t'):
            tiling = not tiling
            print(f"  Tiling: {'ON' if tiling else 'OFF'}")
            inf_times.clear()
        elif key == ord('d'):
            cap.set(cv2.CAP_PROP_POS_FRAMES, min(frame_count + int(fps*5), total-1))
        elif key == ord('a'):
            cap.set(cv2.CAP_PROP_POS_FRAMES, max(frame_count - int(fps*5), 0))

    cap.release()
    cv2.destroyAllWindows()

    print(f"\nFinal: {det_count} detections, avg {avg_ms:.0f}ms ({eff_fps:.1f} FPS)")


if __name__ == '__main__':
    main()
