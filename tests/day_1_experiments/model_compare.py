#!/usr/bin/env python3
"""
Model Compare — Benchmark and compare all TFLite models

WHAT:    Loads every .tflite model found in the project (root best.tflite +
         models/ directory), runs N camera frames through each one, and prints
         a comparison table with inference speed, FPS, detection rate, and
         average confidence. Can also test a single specific model with the
         --model flag.
WHY:     Helps pick the best AI model for flight day conditions. Different
         models trade off speed vs accuracy — this script quantifies that
         tradeoff on the actual hardware with a live camera feed.
WHEN:    Run on the bench before flight (point camera at dummy on a table) or
         during manual flight with --model to test a specific model live. No
         Cube connection needed for bench mode.
WHERE:   Pi (primary, benchmarks real hardware speed) or laptop (development).
         Falls back to blank frames if no camera is available.
ENV:     Pi: pienv venv (opencv-headless, ai-edge-litert).
         Laptop: dev venv (ultralytics, opencv-python).
MODELS:  All .tflite files in project root and models/ directory. Also checks
         cv_models/ variants. All must have input [1,640,640,3] and output
         [1,5,8400] to be compatible.
RISK:    none — sends ZERO commands. Does not connect to the Cube at all.

USAGE:
    python tests/day_1_experiments/model_compare.py
    python tests/day_1_experiments/model_compare.py --frames 100
    python tests/day_1_experiments/model_compare.py --model models/human.tflite --headless --stream
    python tests/day_1_experiments/model_compare.py --list

FLAGS:
    --list           List all available .tflite models and exit
    --frames N       Number of frames per model (default 50)
    --model PATH     Test only this specific model (path relative to project root
                     or absolute)
    --headless       No cv2 window (required on Pi / PuTTY)

OUTPUT:
    - Terminal comparison table with columns: Model, Size, Avg ms, FPS,
      Detection%, Detections, Avg Confidence
    - Recommendation for best detection, best speed, and best balanced model
    - No CSV output (results are printed only)

BEST PRACTICES:
    - Point camera at the dummy for realistic detection rates (blank frames
      will show 0% detection for all models)
    - Use --frames 100 for more stable timing measurements
    - On Pi, close other processes to get clean benchmarks
    - After choosing a model: cp models/CHOSEN.tflite best.tflite

DEPENDENCIES:
    opencv-python (or opencv-python-headless), numpy, vision.py
    Optional: picamera2 (Pi camera), pymavlink (not used)
"""

import sys, os, time, math, glob
from datetime import datetime

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, project_root)

import cv2
import numpy as np

# ── CLI flags ────────────────────────────────────────────────────────────
HEADLESS = "--headless" in sys.argv
LIST_ONLY = "--list" in sys.argv
SPECIFIC_MODEL = None
FRAMES_PER_MODEL = 50

for _i, _a in enumerate(sys.argv):
    if _a == "--model" and _i + 1 < len(sys.argv):
        SPECIFIC_MODEL = sys.argv[_i + 1]
    elif _a == "--frames" and _i + 1 < len(sys.argv):
        FRAMES_PER_MODEL = int(sys.argv[_i + 1])

# ── Find all models ─────────────────────────────────────────────────────
def find_models():
    models = []
    # best.tflite in root
    root_model = os.path.join(project_root, "best.tflite")
    if os.path.exists(root_model):
        models.append(("best.tflite (root)", root_model))
    # models/ directory
    models_dir = os.path.join(project_root, "cv_models")
    if os.path.isdir(models_dir):
        for f in sorted(os.listdir(models_dir)):
            if f.endswith(".tflite"):
                models.append((f"cv_models/{f}", os.path.join(models_dir, f)))
    # cv_models/ subdirectories
    cv_dir = os.path.join(project_root, "cv_models")
    if os.path.isdir(cv_dir):
        for sub in sorted(os.listdir(cv_dir)):
            sub_path = os.path.join(cv_dir, sub)
            if os.path.isdir(sub_path):
                for f in sorted(os.listdir(sub_path)):
                    if f.endswith(".tflite"):
                        models.append((f"cv_models/{sub}/{f}", os.path.join(sub_path, f)))
    return models

def list_models():
    models = find_models()
    print(f"\n  Found {len(models)} TFLite model(s):\n")
    for name, path in models:
        size_mb = os.path.getsize(path) / (1024 * 1024)
        print(f"    {name:40s}  {size_mb:.1f} MB")
    print()
    if len(models) <= 1:
        print("  TIP: Export more models on laptop and copy to models/ folder:")
        print("    yolo export model=yolov8n.pt format=tflite     # COCO person detector")
        print("    yolo export model=yolov8s.pt format=tflite     # larger, more accurate")
        print("    yolo export model=best.pt format=tflite int8=True  # quantized, faster")
    print()

# ── Benchmark one model ─────────────────────────────────────────────────
def benchmark_model(model_path, model_name, camera, n_frames):
    """Run n_frames through a model, return stats dict."""
    from vision import VisionSystem

    print(f"\n  --- Testing: {model_name} ---")
    print(f"  Loading model...")

    try:
        eyes = VisionSystem(camera_index=None, model_path=model_path)
    except Exception as e:
        print(f"  FAILED to load: {e}")
        return None

    if not eyes.using_ai:
        print(f"  FAILED — model did not load")
        return None

    # Warmup
    dummy_img = np.zeros((480, 640, 3), dtype=np.uint8)
    eyes.detect_in_image(dummy_img)

    times = []
    detections = 0
    confidences = []

    print(f"  Running {n_frames} frames...")

    for i in range(n_frames):
        if hasattr(camera, 'read'):
            ret, frame = camera.read()
            if not ret or frame is None:
                frame = dummy_img  # fallback
        else:
            frame = dummy_img  # fallback

        t0 = time.time()
        found, px, py, conf = eyes.detect_in_image(frame)
        t1 = time.time()

        times.append((t1 - t0) * 1000)  # ms
        if found:
            detections += 1
            confidences.append(conf)

        if (i + 1) % 10 == 0:
            print(f"    {i+1}/{n_frames}  det={detections}  "
                  f"avg={sum(times)/len(times):.0f}ms")

    avg_ms = sum(times) / len(times)
    fps = 1000 / avg_ms if avg_ms > 0 else 0
    det_rate = 100 * detections / n_frames
    avg_conf = sum(confidences) / len(confidences) if confidences else 0

    result = {
        "name": model_name,
        "path": model_path,
        "size_mb": os.path.getsize(model_path) / (1024 * 1024),
        "avg_ms": avg_ms,
        "min_ms": min(times),
        "max_ms": max(times),
        "fps": fps,
        "detections": detections,
        "total_frames": n_frames,
        "det_rate": det_rate,
        "avg_conf": avg_conf,
    }

    print(f"  Result: {avg_ms:.0f}ms avg | {fps:.1f} FPS | "
          f"{det_rate:.0f}% det | conf={avg_conf:.3f}")

    return result

# ── Main ─────────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("  EXPERIMENT: Model Comparison")
    print("=" * 60)

    if LIST_ONLY:
        list_models()
        return

    models = find_models()
    if not models:
        print("  No .tflite models found!")
        print("  Put models in models/ folder or best.tflite in project root.")
        return

    # If specific model requested, only test that one
    if SPECIFIC_MODEL:
        path = os.path.join(project_root, SPECIFIC_MODEL)
        if not os.path.exists(path):
            path = SPECIFIC_MODEL  # try absolute path
        if not os.path.exists(path):
            print(f"  Model not found: {SPECIFIC_MODEL}")
            return
        models = [(os.path.basename(SPECIFIC_MODEL), path)]

    print(f"\n  Models to test: {len(models)}")
    print(f"  Frames per model: {FRAMES_PER_MODEL}")
    list_models()

    # Open camera once
    print("  Opening camera...")
    try:
        # Try picamera2 first (Pi)
        from picamera2 import Picamera2
        picam = Picamera2()
        cam_config = picam.create_preview_configuration(
            main={"size": (640, 480), "format": "RGB888"})
        picam.configure(cam_config)
        picam.start()
        time.sleep(1)

        class PiCamWrapper:
            def read(self):
                return True, picam.capture_array()
            def release(self):
                picam.stop()

        camera = PiCamWrapper()
        print("  Camera: picamera2")
    except ImportError:
        camera = cv2.VideoCapture(0)
        if not camera.isOpened():
            print("  WARNING: No camera — using blank frames")
            camera = None
        else:
            print("  Camera: OpenCV")

    # Fallback camera wrapper for no-camera scenarios
    class FakeCamera:
        def __init__(self):
            # Create a test image with some features
            self.frame = np.random.randint(50, 200, (480, 640, 3), dtype=np.uint8)
        def read(self):
            return True, self.frame.copy()
        def release(self):
            pass

    if camera is None:
        camera = FakeCamera()

    # Run benchmarks
    results = []
    for name, path in models:
        r = benchmark_model(path, name, camera, FRAMES_PER_MODEL)
        if r:
            results.append(r)

    # Cleanup camera
    if hasattr(camera, 'release'):
        camera.release()

    # ── Comparison table ─────────────────────────────────────────────────
    if not results:
        print("\n  No models tested successfully.")
        return

    print()
    print("=" * 90)
    print("  MODEL COMPARISON RESULTS")
    print("=" * 90)
    print(f"  {'Model':>30s}  {'Size':>6}  {'Avg ms':>7}  {'FPS':>5}  "
          f"{'Det%':>5}  {'Dets':>5}  {'Avg Conf':>9}")
    print("  " + "-" * 82)

    for r in results:
        print(f"  {r['name']:>30s}  {r['size_mb']:>5.1f}M  {r['avg_ms']:>6.0f}ms  "
              f"{r['fps']:>5.1f}  {r['det_rate']:>4.0f}%  "
              f"{r['detections']:>4}/{r['total_frames']}  {r['avg_conf']:>8.3f}")

    # Winner
    print()
    best_det = max(results, key=lambda r: r['det_rate'])
    best_fps = max(results, key=lambda r: r['fps'])

    if best_det == best_fps:
        print(f"  WINNER: {best_det['name']} (best detection AND speed)")
    else:
        print(f"  Best detection: {best_det['name']} ({best_det['det_rate']:.0f}%)")
        print(f"  Best speed:     {best_fps['name']} ({best_fps['fps']:.1f} FPS)")
        # Balance: highest det_rate among models with >= 3 FPS
        viable = [r for r in results if r['fps'] >= 3]
        if viable:
            balanced = max(viable, key=lambda r: r['det_rate'])
            print(f"  Best balanced:  {balanced['name']} "
                  f"({balanced['det_rate']:.0f}% @ {balanced['fps']:.1f} FPS)")

    print()
    print("  To use a model: cp cv_models/MODEL.tflite best.tflite")
    print("=" * 90)

    # Auto-save results to pi_data/benchmark_results.txt (append with timestamp)
    save_dir = os.path.join(project_root, "pi_data")
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, "benchmark_results.txt")
    try:
        import platform
        import socket
        with open(save_path, "a") as f:
            f.write(f"\n{'=' * 80}\n")
            f.write(f"  BENCHMARK — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"  Host: {socket.gethostname()}, Python: {platform.python_version()}, Arch: {platform.machine()}\n")
            f.write(f"  Frames per model: {args.frames}\n")
            f.write(f"{'=' * 80}\n")
            f.write(f"  {'Model':45s} {'Size':>6s} {'Avg ms':>8s} {'FPS':>8s} {'Det%':>6s} {'Conf':>8s}\n")
            f.write(f"  {'-'*45} {'-'*6} {'-'*8} {'-'*8} {'-'*6} {'-'*8}\n")
            for r in results:
                f.write(f"  {r['name']:45s} {r['size_mb']:5.1f}M {r['avg_ms']:8.1f} {r['fps']:8.1f} {r['det_rate']:5.0f}% {r['avg_conf']:8.3f}\n")
            f.write(f"\n")
        print(f"\n  Results saved to: {save_path}")
    except Exception as e:
        print(f"\n  [!] Could not save results: {e}")


if __name__ == "__main__":
    main()
