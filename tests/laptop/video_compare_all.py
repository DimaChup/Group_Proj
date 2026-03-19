#!/usr/bin/env python3
"""
Video Compare All — cycle through 3 backends on DJI video with M key.

Models:
  1. Original TFLite (best.tflite)
  2. v2-1088 TFLite
  3. v2-1088 NCNN (if available)

Controls:
  M = next model/backend
  T = toggle tiling
  SPACE = pause/resume
  A/D = skip 5s back/forward
  +/- = speed up/slow down
  Q = quit

Usage on Pi:
  source ncnn_env/bin/activate
  python tests/laptop/video_compare_all.py
"""
import sys
import os
import time
import numpy as np

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, project_root)
os.chdir(project_root)

import cv2
from vision import VisionSystem

# --- Config ---
VIDEO = "RealVideo/DJI_0001_1456x1088_cropped_30fps.mp4"
CONF = 0.2
MODES = [
    {"path": None, "label": "RAW VIDEO (no AI)", "backend": None},
    {"path": "best.tflite", "label": "Original TFLite", "backend": "tflite"},
    {"path": "cv_models/sar_v2_1088/best.tflite", "label": "v2-1088 TFLite", "backend": "tflite"},
    {"path": "cv_models/sar_v2_1088/best.tflite", "label": "v2-1088 NCNN", "backend": "ncnn"},
]

# CLI overrides
for i, arg in enumerate(sys.argv):
    if arg == "--video" and i + 1 < len(sys.argv):
        VIDEO = sys.argv[i + 1]
    elif arg == "--conf" and i + 1 < len(sys.argv):
        CONF = float(sys.argv[i + 1])

if not os.path.exists(VIDEO):
    print(f"[!] Video not found: {VIDEO}")
    print("    Upload with: scp ... flightlab-user@PI_IP:~/dima/Group_Proj/RealVideo/")
    sys.exit(1)


def load_model(model_info):
    """Load a VisionSystem with the specified backend."""
    # Inject/remove --backend ncnn from sys.argv
    if "--backend" in sys.argv:
        idx = sys.argv.index("--backend")
        sys.argv.pop(idx)
        sys.argv.pop(idx)

    if model_info["backend"] == "ncnn":
        sys.argv.extend(["--backend", "ncnn"])

    vis = VisionSystem(camera_index=None, model_path=model_info["path"])
    return vis


def main():
    print("=" * 60)
    print("  VIDEO COMPARE ALL — 4 modes, M to cycle")
    print("=" * 60)
    print(f"  Video: {VIDEO}")
    print(f"  Conf:  {CONF}")
    for i, m in enumerate(MODES):
        label = m['path'] or 'no AI'
        print(f"  [{i+1}] {m['label']} ({label})")
    print()
    print("  Controls: M=next mode  T=tiling  SPACE=pause  A/D=skip  Q=quit")
    print("=" * 60)

    cap = cv2.VideoCapture(VIDEO)
    if not cap.isOpened():
        print(f"[!] Cannot open video: {VIDEO}")
        return

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    video_fps = cap.get(cv2.CAP_PROP_FPS) or 30
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"  Video: {width}x{height} @ {video_fps:.0f}fps, {total_frames} frames")

    # Start in RAW mode (no AI)
    current_idx = 0
    vis = None
    print(f"\n  Mode: {MODES[current_idx]['label']}")

    paused = False
    tiling = False
    frame_num = 0
    det_count = 0
    fps_times = []
    raw_mode = True  # Start in raw mode

    while True:
        if not paused:
            ret, frame = cap.read()
            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
            frame_num = int(cap.get(cv2.CAP_PROP_POS_FRAMES))

        display = frame.copy()

        # Run detection (skip in RAW mode)
        t0 = time.time()
        mode_info = MODES[current_idx]
        raw_mode = mode_info['backend'] is None

        if not raw_mode and vis is not None and vis.using_ai:
            if tiling:
                h, w = display.shape[:2]
                tile_h, tile_w = h // 2, w // 2
                for ty in range(2):
                    for tx in range(2):
                        tile = display[ty*tile_h:(ty+1)*tile_h, tx*tile_w:(tx+1)*tile_w].copy()
                        found, dx, dy, conf = vis.detect_in_image(tile)
                        if found:
                            det_count += 1
            else:
                found, dx, dy, conf = vis.detect_in_image(display)
                if found:
                    det_count += 1

        elapsed_ms = (time.time() - t0) * 1000
        fps_times.append(elapsed_ms)
        if len(fps_times) > 30:
            fps_times.pop(0)
        avg_ms = sum(fps_times) / len(fps_times)
        eff_fps = 1000 / avg_ms if avg_ms > 0 else 0

        # HUD
        mode_label = MODES[current_idx]['label']
        mode_num = f"[{current_idx+1}/{len(MODES)}]"

        # Mode label (big, top)
        color = (0, 200, 255) if not raw_mode else (255, 255, 255)
        cv2.putText(display, f"{mode_num} {mode_label} (M=next)", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        if raw_mode:
            cv2.putText(display, f"Video FPS: {video_fps:.0f} (raw, no AI)", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        else:
            backend = vis.backend_name if vis else "none"
            cv2.putText(display, f"Backend: {backend}", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
            fps_color = (0, 255, 0) if eff_fps > 10 else (0, 255, 255) if eff_fps > 5 else (0, 0, 255)
            cv2.putText(display, f"Effective FPS: {eff_fps:.1f} ({avg_ms:.0f}ms/frame)", (10, 90),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, fps_color, 2)
            cv2.putText(display, f"Tiling: {'ON' if tiling else 'OFF'} (T)", (10, 120),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            cv2.putText(display, f"Detections: {det_count}  Conf: {CONF}", (10, 145),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

        # Frame counter (always shown)
        progress = frame_num / total_frames if total_frames > 0 else 0
        cv2.putText(display, f"Frame: {frame_num}/{total_frames} ({progress*100:.0f}%)", (10, height - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        # Progress bar
        bar_w = width - 20
        cv2.rectangle(display, (10, height - 10), (10 + bar_w, height - 5), (50, 50, 50), -1)
        cv2.rectangle(display, (10, height - 10), (10 + int(bar_w * progress), height - 5), (0, 255, 0), -1)

        if paused:
            cv2.putText(display, "PAUSED", (width//2 - 80, height//2),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)

        # Resize for display if too large
        if width > 1200:
            scale = 1000 / width
            display = cv2.resize(display, (int(width*scale), int(height*scale)))

        cv2.imshow("Video Compare All", display)

        # Wait: raw mode = 33ms (30fps), AI mode = 1ms (as fast as model allows)
        wait_ms = int(1000 / video_fps) if raw_mode else 1
        if paused:
            wait_ms = 50
        key = cv2.waitKey(wait_ms) & 0xFF

        if key == ord('q') or key == 27:
            break
        elif key == ord(' '):
            paused = not paused
        elif key == ord('m'):
            current_idx = (current_idx + 1) % len(MODES)
            mode_info = MODES[current_idx]
            print(f"\n  Switching to: {mode_info['label']}...")
            if mode_info['backend'] is None:
                vis = None
                print("  RAW mode — no AI, full video speed")
            else:
                vis = load_model(mode_info)
                print(f"  Backend: {vis.backend_name}")
            fps_times.clear()
            det_count = 0
        elif key == ord('t'):
            tiling = not tiling
            print(f"  Tiling: {'ON' if tiling else 'OFF'}")
            fps_times.clear()
        elif key == ord('d'):
            pos = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
            cap.set(cv2.CAP_PROP_POS_FRAMES, min(pos + int(video_fps * 5), total_frames - 1))
        elif key == ord('a'):
            pos = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
            cap.set(cv2.CAP_PROP_POS_FRAMES, max(pos - int(video_fps * 5), 0))
        elif key == ord('+') or key == ord('='):
            video_fps = min(120, video_fps * 1.5)
            print(f"  Playback speed: {video_fps:.0f} FPS")
        elif key == ord('-'):
            video_fps = max(1, video_fps / 1.5)
            print(f"  Playback speed: {video_fps:.0f} FPS")

    cap.release()
    cv2.destroyAllWindows()
    print("\nDone.")


if __name__ == '__main__':
    main()
