#!/usr/bin/env python3
"""
NCNN Benchmark — compare NCNN vs TFLite inference speed on Pi.

WHAT:    Loads the NCNN model export, runs N frames, measures avg/min/max/FPS.
         Then does the same with TFLite for direct comparison.
WHY:     NCNN has ARM-optimized NEON SIMD kernels — expected 3-4x faster than TFLite.
WHEN:    After setting up ncnn_env on Pi. Before deciding whether to switch backend.
WHERE:   Pi 5 (primary target). Also works on laptop for sanity check.
ENV:     ncnn_env on Pi (pip install -r requirements/requirements_ncnn_pi.txt)
MODELS:  cv_models/sar_v2_1088/ncnn/ (model.ncnn.param + model.ncnn.bin)
RISK:    None — pure inference, ZERO commands, no camera needed.

SETUP ON PI:
    python3 -m venv --system-site-packages ncnn_env
    source ncnn_env/bin/activate
    pip install -r requirements/requirements_ncnn_pi.txt
    python tests/hardware/ncnn_benchmark.py

FLAGS:
    --frames N      Number of inference frames (default: 30)
    --model PATH    NCNN model directory (default: cv_models/sar_v2_1088/ncnn/best_ncnn_model)
    --tflite PATH   TFLite model for comparison (default: best.tflite)
    --no-tflite     Skip TFLite comparison
    --camera        Use live camera frames instead of synthetic
"""
import sys
import os
import time
import argparse
import statistics

# Add project root
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, project_root)
os.chdir(project_root)

import numpy as np
import cv2


def generate_test_frame(w=640, h=640):
    """Create a synthetic test frame with a dummy-like blob."""
    frame = np.random.randint(50, 150, (h, w, 3), dtype=np.uint8)
    # Add a bright rectangle (dummy-like)
    cv2.rectangle(frame, (280, 250), (360, 390), (0, 140, 255), -1)
    return frame


def get_camera_frame():
    """Capture one frame from Pi camera or webcam."""
    try:
        from picamera2 import Picamera2
        cam = Picamera2()
        cam.configure(cam.create_still_configuration(main={"size": (640, 480)}))
        cam.start()
        # Warmup
        for _ in range(5):
            cam.capture_array()
        frame = cam.capture_array()
        cam.stop()
        cam.close()
        # Resize to 640x640
        frame = cv2.resize(frame, (640, 640))
        return frame
    except ImportError:
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, frame = cap.read()
            cap.release()
            if ret:
                return cv2.resize(frame, (640, 640))
    return None


# ═══════════════════════════════════════════════════════
# NCNN INFERENCE
# ═══════════════════════════════════════════════════════
def benchmark_ncnn(model_dir, frames, test_frame):
    """Run NCNN inference benchmark."""
    try:
        import ncnn
    except ImportError:
        print("\n  [!] ncnn not installed. Run: pip install ncnn")
        return None

    param_path = os.path.join(model_dir, "model.ncnn.param")
    bin_path = os.path.join(model_dir, "model.ncnn.bin")

    if not os.path.exists(param_path):
        print(f"\n  [!] NCNN model not found at {model_dir}")
        return None

    print(f"\n  Loading NCNN model from {model_dir}...")
    net = ncnn.Net()
    # Optimize for Pi 5 (4 cores)
    net.opt.num_threads = 4
    net.opt.use_vulkan_compute = False  # CPU only on Pi
    net.load_param(param_path)
    net.load_model(bin_path)

    # Prepare input (640x640 RGB, normalized 0-1)
    h, w = test_frame.shape[:2]
    if h != 640 or w != 640:
        test_frame = cv2.resize(test_frame, (640, 640))

    # Convert BGR to RGB, normalize
    rgb = cv2.cvtColor(test_frame, cv2.COLOR_BGR2RGB)
    blob = rgb.astype(np.float32) / 255.0

    # NCNN input format
    mat_in = ncnn.Mat.from_pixels(rgb, ncnn.Mat.PixelType.PIXEL_RGB, 640, 640)

    # Normalize (same as YOLO: /255)
    norm_vals = [1/255.0, 1/255.0, 1/255.0]
    mean_vals = [0.0, 0.0, 0.0]
    mat_in.substract_mean_normalize(mean_vals, norm_vals)

    # Warmup (first run is slow — JIT compilation)
    print("  Warmup (first inference is slow)...")
    ex = net.create_extractor()
    ex.input("in0", mat_in)
    _ = ex.extract("out0")

    # Benchmark
    print(f"  Running {frames} frames...")
    times = []
    for i in range(frames):
        t0 = time.perf_counter()
        ex = net.create_extractor()
        ex.input("in0", mat_in)
        ret, out = ex.extract("out0")
        elapsed = (time.perf_counter() - t0) * 1000
        times.append(elapsed)
        if (i + 1) % 10 == 0:
            print(f"    {i+1}/{frames}  avg={statistics.mean(times):.1f}ms")

    return {
        'backend': 'NCNN',
        'avg_ms': statistics.mean(times),
        'min_ms': min(times),
        'max_ms': max(times),
        'std_ms': statistics.stdev(times) if len(times) > 1 else 0,
        'fps': 1000 / statistics.mean(times),
        'frames': frames,
    }


# ═══════════════════════════════════════════════════════
# TFLITE INFERENCE (for comparison)
# ═══════════════════════════════════════════════════════
def benchmark_tflite(model_path, frames, test_frame):
    """Run TFLite inference benchmark."""
    try:
        # Try ai-edge-litert first (Python 3.13+)
        try:
            from ai_edge_litert.interpreter import Interpreter
        except ImportError:
            from tflite_runtime.interpreter import Interpreter
    except ImportError:
        try:
            from tensorflow.lite.python.interpreter import Interpreter
        except ImportError:
            print("\n  [!] No TFLite backend available")
            return None

    if not os.path.exists(model_path):
        print(f"\n  [!] TFLite model not found: {model_path}")
        return None

    print(f"\n  Loading TFLite model: {model_path}...")
    interpreter = Interpreter(model_path=model_path, num_threads=4)
    interpreter.allocate_tensors()

    input_details = interpreter.get_input_details()
    input_shape = input_details[0]['shape']  # [1, 640, 640, 3]
    h, w = input_shape[1], input_shape[2]

    # Prepare input
    frame_resized = cv2.resize(test_frame, (w, h))
    input_data = frame_resized.astype(np.float32) / 255.0
    input_data = np.expand_dims(input_data, axis=0)

    # Warmup
    print("  Warmup...")
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()

    # Benchmark
    print(f"  Running {frames} frames...")
    times = []
    for i in range(frames):
        t0 = time.perf_counter()
        interpreter.set_tensor(input_details[0]['index'], input_data)
        interpreter.invoke()
        elapsed = (time.perf_counter() - t0) * 1000
        times.append(elapsed)
        if (i + 1) % 10 == 0:
            print(f"    {i+1}/{frames}  avg={statistics.mean(times):.1f}ms")

    return {
        'backend': 'TFLite',
        'avg_ms': statistics.mean(times),
        'min_ms': min(times),
        'max_ms': max(times),
        'std_ms': statistics.stdev(times) if len(times) > 1 else 0,
        'fps': 1000 / statistics.mean(times),
        'frames': frames,
    }


# ═══════════════════════════════════════════════════════
# REPORT
# ═══════════════════════════════════════════════════════
def print_results(results):
    """Print comparison table."""
    print("\n" + "=" * 70)
    print("  NCNN vs TFLite BENCHMARK RESULTS")
    print("=" * 70)
    print(f"  {'Backend':10s} {'Avg ms':>8s} {'Min ms':>8s} {'Max ms':>8s} {'Std ms':>8s} {'FPS':>8s}")
    print(f"  {'-'*10} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")

    for r in results:
        if r:
            print(f"  {r['backend']:10s} {r['avg_ms']:8.1f} {r['min_ms']:8.1f} "
                  f"{r['max_ms']:8.1f} {r['std_ms']:8.1f} {r['fps']:8.1f}")

    # Speedup
    if len(results) == 2 and all(r is not None for r in results):
        ncnn_r = next(r for r in results if r['backend'] == 'NCNN')
        tfl_r = next(r for r in results if r['backend'] == 'TFLite')
        speedup = tfl_r['avg_ms'] / ncnn_r['avg_ms']
        print(f"\n  Speedup: NCNN is {speedup:.1f}x faster than TFLite")
        if speedup > 2:
            print("  >> Worth switching to NCNN backend!")
        elif speedup > 1.3:
            print("  >> Moderate improvement. Consider switching.")
        else:
            print("  >> Minimal difference. Stick with TFLite.")

    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="NCNN vs TFLite benchmark")
    parser.add_argument('--frames', type=int, default=30, help='Frames per backend (default: 30)')
    parser.add_argument('--model', default='cv_models/sar_v2_1088/ncnn/best_ncnn_model',
                        help='NCNN model directory')
    parser.add_argument('--tflite', default='best.tflite', help='TFLite model path')
    parser.add_argument('--no-tflite', action='store_true', help='Skip TFLite comparison')
    parser.add_argument('--camera', action='store_true', help='Use live camera frame')
    args = parser.parse_args()

    print("=" * 70)
    print("  NCNN vs TFLite INFERENCE BENCHMARK")
    print("=" * 70)
    print(f"  Frames per test: {args.frames}")
    print(f"  NCNN model:      {args.model}")
    print(f"  TFLite model:    {args.tflite}")

    # Get test frame
    if args.camera:
        print("\n  Capturing camera frame...")
        test_frame = get_camera_frame()
        if test_frame is None:
            print("  [!] Camera not available, using synthetic frame")
            test_frame = generate_test_frame()
        else:
            print(f"  Camera frame: {test_frame.shape[1]}x{test_frame.shape[0]}")
    else:
        test_frame = generate_test_frame()
        print(f"  Using synthetic test frame: {test_frame.shape[1]}x{test_frame.shape[0]}")

    results = []

    # NCNN benchmark (inference only)
    ncnn_result = benchmark_ncnn(args.model, args.frames, test_frame)
    results.append(ncnn_result)

    # TFLite benchmark (inference only)
    if not args.no_tflite:
        tflite_result = benchmark_tflite(args.tflite, args.frames, test_frame)
        results.append(tflite_result)

    # Print inference-only comparison
    valid = [r for r in results if r is not None]
    if valid:
        print_results(valid)
    else:
        print("\n  [!] No benchmarks completed. Check model paths and dependencies.")

    # ═══════════════════════════════════════════════════════
    # FULL PIPELINE BENCHMARK (camera capture + preprocess + inference + draw)
    # ═══════════════════════════════════════════════════════
    if args.camera:
        print("\n" + "=" * 70)
        print("  FULL PIPELINE BENCHMARK (capture + preprocess + inference + draw)")
        print("=" * 70)

        from vision import VisionSystem

        pipeline_results = []

        # TFLite full pipeline
        if not args.no_tflite:
            print(f"\n  --- TFLite full pipeline ({args.tflite}) ---")
            try:
                vis_tfl = VisionSystem(camera_index=0, model_path=args.tflite)
                if vis_tfl.using_ai:
                    times_tfl = []
                    for i in range(args.frames):
                        t0 = time.perf_counter()
                        frame = vis_tfl.get_frame()
                        if frame is not None:
                            found, x, y, conf = vis_tfl.detect_in_image(frame)
                        elapsed = (time.perf_counter() - t0) * 1000
                        times_tfl.append(elapsed)
                        if (i + 1) % 10 == 0:
                            print(f"    {i+1}/{args.frames}  avg={statistics.mean(times_tfl):.1f}ms")
                    vis_tfl.release()
                    avg = statistics.mean(times_tfl)
                    pipeline_results.append({
                        'backend': 'TFLite-PIPE',
                        'avg_ms': avg,
                        'min_ms': min(times_tfl),
                        'max_ms': max(times_tfl),
                        'std_ms': statistics.stdev(times_tfl) if len(times_tfl) > 1 else 0,
                        'fps': 1000 / avg,
                        'frames': args.frames,
                    })
            except Exception as e:
                print(f"    [!] TFLite pipeline error: {e}")

        # NCNN full pipeline
        print(f"\n  --- NCNN full pipeline ({args.model}) ---")
        try:
            # Find tflite path for VisionSystem (it auto-finds ncnn dir)
            parent = os.path.dirname(os.path.dirname(args.model))
            tflite_for_ncnn = os.path.join(parent, "best.tflite")
            if not os.path.exists(tflite_for_ncnn):
                tflite_for_ncnn = args.tflite

            # Inject --backend ncnn
            if "--backend" not in sys.argv:
                sys.argv.extend(["--backend", "ncnn"])

            vis_ncnn = VisionSystem(camera_index=0, model_path=tflite_for_ncnn)
            if vis_ncnn.using_ai and vis_ncnn.backend_name == "ncnn":
                times_ncnn = []
                for i in range(args.frames):
                    t0 = time.perf_counter()
                    frame = vis_ncnn.get_frame()
                    if frame is not None:
                        found, x, y, conf = vis_ncnn.detect_in_image(frame)
                    elapsed = (time.perf_counter() - t0) * 1000
                    times_ncnn.append(elapsed)
                    if (i + 1) % 10 == 0:
                        print(f"    {i+1}/{args.frames}  avg={statistics.mean(times_ncnn):.1f}ms")
                vis_ncnn.release()
                avg = statistics.mean(times_ncnn)
                pipeline_results.append({
                    'backend': 'NCNN-PIPE',
                    'avg_ms': avg,
                    'min_ms': min(times_ncnn),
                    'max_ms': max(times_ncnn),
                    'std_ms': statistics.stdev(times_ncnn) if len(times_ncnn) > 1 else 0,
                    'fps': 1000 / avg,
                    'frames': args.frames,
                })
            else:
                print(f"    [!] NCNN backend not loaded (got: {vis_ncnn.backend_name})")
        except Exception as e:
            print(f"    [!] NCNN pipeline error: {e}")

        # Remove injected args
        if "--backend" in sys.argv:
            try:
                idx = sys.argv.index("--backend")
                sys.argv.pop(idx)
                sys.argv.pop(idx)
            except (ValueError, IndexError):
                pass

        # Print full pipeline comparison
        if pipeline_results:
            print("\n" + "=" * 70)
            print("  FULL PIPELINE RESULTS (camera + preprocess + inference + draw)")
            print("=" * 70)
            print(f"  {'Backend':12s} {'Avg ms':>8s} {'Min ms':>8s} {'Max ms':>8s} {'Std ms':>8s} {'FPS':>8s}")
            print(f"  {'-'*12} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")
            for r in pipeline_results:
                print(f"  {r['backend']:12s} {r['avg_ms']:8.1f} {r['min_ms']:8.1f} "
                      f"{r['max_ms']:8.1f} {r['std_ms']:8.1f} {r['fps']:8.1f}")

            # Compare inference vs pipeline
            print("\n  INFERENCE vs FULL PIPELINE:")
            for pr in pipeline_results:
                base = pr['backend'].replace('-PIPE', '')
                inf_r = next((r for r in valid if r['backend'] == base), None)
                if inf_r:
                    overhead = pr['avg_ms'] - inf_r['avg_ms']
                    print(f"    {base}: inference {inf_r['avg_ms']:.0f}ms → pipeline {pr['avg_ms']:.0f}ms "
                          f"(+{overhead:.0f}ms overhead, {overhead/pr['avg_ms']*100:.0f}% of total)")
            print("=" * 70)

    # Auto-save to pi_data
    save_dir = os.path.join(project_root, "pi_data")
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, "benchmark_results.txt")
    try:
        import platform, socket
        from datetime import datetime
        with open(save_path, "a") as f:
            f.write(f"\n{'=' * 80}\n")
            f.write(f"  NCNN BENCHMARK — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"  Host: {socket.gethostname()}, Python: {platform.python_version()}, Arch: {platform.machine()}\n")
            f.write(f"{'=' * 80}\n")
            f.write(f"  {'Backend':12s} {'Avg ms':>8s} {'FPS':>8s} {'Type':>12s}\n")
            f.write(f"  {'-'*12} {'-'*8} {'-'*8} {'-'*12}\n")
            for r in valid:
                f.write(f"  {r['backend']:12s} {r['avg_ms']:8.1f} {r['fps']:8.1f} {'inference':>12s}\n")
            if args.camera and 'pipeline_results' in dir() and pipeline_results:
                for r in pipeline_results:
                    f.write(f"  {r['backend']:12s} {r['avg_ms']:8.1f} {r['fps']:8.1f} {'full pipeline':>12s}\n")
            f.write("\n")
        print(f"\n  Results saved to: {save_path}")
    except Exception as e:
        print(f"\n  [!] Could not save results: {e}")


if __name__ == '__main__':
    main()
