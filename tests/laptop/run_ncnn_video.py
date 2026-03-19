#!/usr/bin/env python3
"""
Run NCNN model on DJI video — headless, logs to terminal + CSV.
No display needed. Works over PuTTY.

Usage: python tests/laptop/run_ncnn_video.py
"""
import sys
import os
import time

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, project_root)
os.chdir(project_root)

# Force NCNN backend
if "--backend" not in sys.argv:
    sys.argv.extend(["--backend", "ncnn"])

import cv2
from vision import VisionSystem

VIDEO = "RealVideo/DJI_0001_1456x1088_cropped_30fps.mp4"
MODEL = "cv_models/sar_v2_1088/best.tflite"
CONF = 0.2

print("=" * 60)
print("  NCNN VIDEO TEST — headless")
print(f"  Video: {VIDEO}")
print(f"  Model: {MODEL}")
print(f"  Conf:  {CONF}")
print("=" * 60)

if not os.path.exists(VIDEO):
    print(f"[!] Video not found: {VIDEO}")
    sys.exit(1)

print("\nLoading NCNN model...")
vis = VisionSystem(camera_index=None, model_path=MODEL)
print(f"Backend: {vis.backend_name}")
print(f"AI loaded: {vis.using_ai}")

if not vis.using_ai:
    print("[!] Model not loaded")
    sys.exit(1)

cap = cv2.VideoCapture(VIDEO)
fps = cap.get(cv2.CAP_PROP_FPS)
total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print(f"Video: {w}x{h} @ {fps:.0f}fps, {total} frames, {total/fps:.0f}s")

det_count = 0
frame_count = 0
times = []

print(f"\nProcessing every 3rd frame...")
print(f"{'Frame':>8s} {'Time ms':>8s} {'FPS':>6s} {'Det':>4s} {'Conf':>6s}")
print("-" * 40)

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_count += 1

        # Process every 3rd frame
        if frame_count % 3 != 0:
            continue

        t0 = time.perf_counter()
        found, x, y, conf = vis.detect_in_image(frame)
        dt = (time.perf_counter() - t0) * 1000
        times.append(dt)

        if found and conf >= CONF:
            det_count += 1

        if len(times) % 10 == 0:
            avg = sum(times[-30:]) / len(times[-30:])
            efps = 1000 / avg if avg > 0 else 0
            det_str = f"{conf:.2f}" if found else "miss"
            print(f"{frame_count:8d} {avg:8.1f} {efps:6.1f} {det_count:4d} {det_str:>6s}")

except KeyboardInterrupt:
    print("\nStopped.")

cap.release()

avg_ms = sum(times) / len(times) if times else 0
efps = 1000 / avg_ms if avg_ms > 0 else 0

print(f"\n{'=' * 60}")
print(f"  RESULTS")
print(f"  Frames processed: {len(times)}")
print(f"  Detections: {det_count} ({det_count/len(times)*100:.0f}%)" if times else "  No frames")
print(f"  Avg inference: {avg_ms:.1f}ms ({efps:.1f} FPS)")
print(f"  Backend: {vis.backend_name}")
print(f"{'=' * 60}")

# Auto-save
save_path = os.path.join(project_root, "pi_data", "ncnn_video_test.txt")
os.makedirs(os.path.dirname(save_path), exist_ok=True)
try:
    from datetime import datetime
    import socket, platform
    with open(save_path, "a") as f:
        f.write(f"\n{'=' * 60}\n")
        f.write(f"  NCNN VIDEO TEST — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"  Host: {socket.gethostname()}, Arch: {platform.machine()}\n")
        f.write(f"  Backend: {vis.backend_name}, Model: {MODEL}\n")
        f.write(f"  Frames: {len(times)}, Detections: {det_count}\n")
        f.write(f"  Avg: {avg_ms:.1f}ms ({efps:.1f} FPS)\n")
        f.write(f"{'=' * 60}\n")
    print(f"\nSaved to {save_path}")
except:
    pass
