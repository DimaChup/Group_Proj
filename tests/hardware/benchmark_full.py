#!/usr/bin/env python3
"""
Comprehensive CV Benchmark — full system profiling for inference optimization.

WHAT:    Runs a 6-section benchmark covering: (1) system info (CPU, RAM, temp,
         available backends, HW accelerators), (2) preprocessing timing (resize,
         normalize, undistort at multiple resolutions), (3) camera capture timing
         (optional, picamera2 or OpenCV), (4) TFLite inference on all .tflite
         models with/without lens undistortion, (5) ONNX/OpenCV DNN backends
         if .onnx models exist, (6) threading overhead (direct vs threaded
         inference). Ends with a results summary table, time budget breakdown,
         and improvement opportunities.
WHY:     Collects every datapoint needed to plan CV speed improvements: which
         model is fastest, how much undistortion costs, whether threading helps,
         what backends are available, and where the bottleneck is (capture vs
         preprocessing vs inference). Essential before optimizing for flight.
WHEN:    After initial Pi setup to establish baseline. After overclocking, model
         changes, or backend installs (NCNN, ONNX). Before flight to verify
         performance meets requirements (~5 FPS minimum).
WHERE:   Primarily Pi (reads /proc/cpuinfo, thermal zones, etc.), but sections
         1-2 and 4-6 work on laptop too (Linux-specific system info will show
         "unknown" on Windows).
ENV:     pienv on Pi, dev venv on laptop. All backends optional — tests whatever
         is installed (tflite-runtime, ai-edge-litert, ultralytics, onnxruntime, ncnn).
MODELS:  best.tflite + all .tflite files in models/ directory. Also tests .onnx
         models if present in project root or models/ directory.
RISK:    none — pure computation, no drone commands, no MAVLink connection.

USAGE:
    python tests/hardware/benchmark_full.py
    python tests/hardware/benchmark_full.py --camera

FLAGS:
    --camera    Include camera capture timing (Section 3). Opens picamera2 or
                OpenCV camera for 30 frame captures. Omit if no camera available.

OUTPUT:
    Terminal: 6-section report with timing tables, then a summary table comparing
    all models/configs. Includes time budget breakdown (camera + preproc + inference)
    and specific improvement recommendations (NCNN, threading, Hailo, resolution).

BEST PRACTICES:
    - Run with --camera on Pi to get full pipeline timing
    - Close other processes for stable numbers (especially browser/X11)
    - Run multiple times and compare — Pi 5 can throttle under sustained load
    - Check CPU temp in output — throttling starts at 80C on Pi 5
    - Save output to a file for comparison: python benchmark_full.py | tee bench_results.txt

DEPENDENCIES:
    opencv-python (or opencv-python-headless), numpy, vision.py (project module).
    Optional: onnxruntime, ncnn (pyncnn) — tested if installed.
"""
import sys, os, time, glob, platform, subprocess
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, project_root)
os.chdir(project_root)

import cv2
import numpy as np

N = 30  # inferences per test
USE_CAMERA = "--camera" in sys.argv


# ═══════════════════════════════════════════════════════════════
#  SECTION 1: System Information
# ═══════════════════════════════════════════════════════════════

def get_system_info():
    """Collect all hardware/software info relevant to CV performance."""
    info = {}

    # Platform
    info["platform"] = platform.platform()
    info["machine"] = platform.machine()
    info["python"] = platform.python_version()
    info["opencv"] = cv2.__version__
    info["numpy"] = np.__version__

    # CPU info
    try:
        with open("/proc/cpuinfo", "r") as f:
            cpuinfo = f.read()
        # Get model name
        for line in cpuinfo.split("\n"):
            if "model name" in line.lower() or "Model" in line:
                info["cpu"] = line.split(":")[-1].strip()
                break
        # Count cores
        info["cpu_cores"] = cpuinfo.count("processor\t:")
    except Exception:
        info["cpu"] = platform.processor() or "unknown"
        info["cpu_cores"] = os.cpu_count()

    # CPU frequency
    try:
        with open("/sys/devices/system/cpu/cpu0/cpufreq/scaling_max_freq", "r") as f:
            info["cpu_max_mhz"] = int(f.read().strip()) // 1000
        with open("/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq", "r") as f:
            info["cpu_cur_mhz"] = int(f.read().strip()) // 1000
    except Exception:
        info["cpu_max_mhz"] = "unknown"
        info["cpu_cur_mhz"] = "unknown"

    # CPU temperature
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            info["cpu_temp_c"] = int(f.read().strip()) / 1000.0
    except Exception:
        info["cpu_temp_c"] = "unknown"

    # RAM
    try:
        with open("/proc/meminfo", "r") as f:
            meminfo = f.read()
        for line in meminfo.split("\n"):
            if line.startswith("MemTotal:"):
                kb = int(line.split()[1])
                info["ram_mb"] = kb // 1024
            elif line.startswith("MemAvailable:"):
                kb = int(line.split()[1])
                info["ram_avail_mb"] = kb // 1024
    except Exception:
        info["ram_mb"] = "unknown"
        info["ram_avail_mb"] = "unknown"

    # Check for hardware accelerators
    info["accelerators"] = []
    # Hailo
    try:
        result = subprocess.run(["hailortcli", "fw-control", "identify"],
                                capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            info["accelerators"].append(f"Hailo: {result.stdout.strip()}")
    except Exception:
        pass
    # Coral TPU
    try:
        result = subprocess.run(["lsusb"], capture_output=True, text=True, timeout=5)
        if "Global Unichip" in result.stdout or "Google" in result.stdout:
            info["accelerators"].append("Coral USB TPU detected")
    except Exception:
        pass
    if not info["accelerators"]:
        info["accelerators"] = ["None (CPU only)"]

    # Available backends
    info["backends"] = []
    try:
        from tflite_runtime.interpreter import Interpreter
        info["backends"].append("tflite-runtime")
    except ImportError:
        pass
    try:
        from ai_edge_litert.interpreter import Interpreter
        info["backends"].append("ai-edge-litert")
    except ImportError:
        pass
    try:
        from ultralytics import YOLO
        info["backends"].append("ultralytics")
    except ImportError:
        pass
    try:
        import ncnn
        info["backends"].append(f"ncnn (pyncnn)")
    except ImportError:
        pass
    try:
        import onnxruntime as ort
        providers = ort.get_available_providers()
        info["backends"].append(f"onnxruntime ({', '.join(providers)})")
    except ImportError:
        pass

    # Check NCNN availability via command line
    try:
        result = subprocess.run(["ncnn2mem"], capture_output=True, text=True, timeout=5)
        info["backends"].append("ncnn-tools (CLI)")
    except Exception:
        pass

    # OpenCV build info (NEON, threading)
    build = cv2.getBuildInformation()
    info["cv2_neon"] = "NEON" in build
    info["cv2_threads"] = "TBB" in build or "OpenMP" in build or "pthreads" in build
    # Check for DNN backends
    info["cv2_dnn_backends"] = []
    if "OPENCV_DNN" in build:
        info["cv2_dnn_backends"].append("OpenCV DNN")

    return info


def print_system_info(info):
    print("=" * 65)
    print("  SECTION 1: SYSTEM INFORMATION")
    print("=" * 65)
    print(f"  Platform:      {info['platform']}")
    print(f"  Architecture:  {info['machine']}")
    print(f"  Python:        {info['python']}")
    print(f"  OpenCV:        {info['opencv']} (NEON: {info['cv2_neon']}, Threading: {info['cv2_threads']})")
    print(f"  NumPy:         {info['numpy']}")
    print(f"  CPU:           {info.get('cpu', 'unknown')}")
    print(f"  CPU cores:     {info['cpu_cores']}")
    print(f"  CPU freq:      {info.get('cpu_cur_mhz', '?')} / {info.get('cpu_max_mhz', '?')} MHz")
    print(f"  CPU temp:      {info.get('cpu_temp_c', '?')}°C")
    print(f"  RAM:           {info.get('ram_avail_mb', '?')} / {info.get('ram_mb', '?')} MB available")
    print(f"  Accelerators:  {', '.join(info['accelerators'])}")
    print(f"  AI backends:   {', '.join(info['backends']) if info['backends'] else 'NONE'}")
    print()


# ═══════════════════════════════════════════════════════════════
#  SECTION 2: Preprocessing Benchmark
# ═══════════════════════════════════════════════════════════════

def benchmark_preprocessing(frame):
    """Time each preprocessing step separately."""
    results = {}
    h, w = frame.shape[:2]

    # 1. BGR→RGB conversion
    times = []
    for _ in range(N):
        t = time.time()
        _ = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        times.append((time.time() - t) * 1000)
    results["BGR→RGB"] = sum(times) / len(times)

    # 2. Resize to different resolutions
    for target in [(640, 640), (416, 416), (320, 320), (256, 256)]:
        times = []
        for _ in range(N):
            t = time.time()
            _ = cv2.resize(frame, target)
            times.append((time.time() - t) * 1000)
        results[f"Resize→{target[0]}x{target[1]}"] = sum(times) / len(times)

    # 3. Normalize (uint8→float32 /255)
    img_resized = cv2.resize(frame, (640, 640))
    times = []
    for _ in range(N):
        t = time.time()
        _ = img_resized.astype(np.float32) / 255.0
        times.append((time.time() - t) * 1000)
    results["Normalize float32"] = sum(times) / len(times)

    # 4. Undistortion (remap)
    calib_path = os.path.join(project_root, "calibration_data.npz")
    if os.path.exists(calib_path):
        calib = np.load(calib_path)
        mtx, dist = calib["camera_matrix"], calib["dist_coeffs"]
        new_mtx, _ = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 0, (w, h))
        map1, map2 = cv2.initUndistortRectifyMap(mtx, dist, None, new_mtx, (w, h), cv2.CV_16SC2)
        times = []
        for _ in range(N):
            t = time.time()
            _ = cv2.remap(frame, map1, map2, cv2.INTER_LINEAR)
            times.append((time.time() - t) * 1000)
        results["Undistort (remap)"] = sum(times) / len(times)

    # 5. np.expand_dims (batch dim)
    img_f32 = img_resized.astype(np.float32) / 255.0
    times = []
    for _ in range(N):
        t = time.time()
        _ = np.expand_dims(img_f32, axis=0)
        times.append((time.time() - t) * 1000)
    results["expand_dims"] = sum(times) / len(times)

    # 6. Full pipeline: undistort + cvtColor + resize + normalize + expand
    times = []
    for _ in range(N):
        t = time.time()
        f = frame.copy()
        if os.path.exists(calib_path):
            f = cv2.remap(f, map1, map2, cv2.INTER_LINEAR)
        f = cv2.cvtColor(f, cv2.COLOR_BGR2RGB)
        f = cv2.resize(f, (640, 640))
        f = f.astype(np.float32) / 255.0
        f = np.expand_dims(f, axis=0)
        times.append((time.time() - t) * 1000)
    results["FULL PIPELINE (640)"] = sum(times) / len(times)

    # 7. Full pipeline at 320x320
    times = []
    for _ in range(N):
        t = time.time()
        f = frame.copy()
        if os.path.exists(calib_path):
            f = cv2.remap(f, map1, map2, cv2.INTER_LINEAR)
        f = cv2.cvtColor(f, cv2.COLOR_BGR2RGB)
        f = cv2.resize(f, (320, 320))
        f = f.astype(np.float32) / 255.0
        f = np.expand_dims(f, axis=0)
        times.append((time.time() - t) * 1000)
    results["FULL PIPELINE (320)"] = sum(times) / len(times)

    return results


def print_preprocessing(results):
    print("=" * 65)
    print("  SECTION 2: PREPROCESSING TIMING (per frame)")
    print("=" * 65)
    total = 0
    for name, ms in results.items():
        bar = "█" * int(ms * 2) if ms < 30 else "█" * 60
        print(f"  {name:<25} {ms:>6.2f}ms  {bar}")
        if not name.startswith("FULL"):
            total += ms
    print()


# ═══════════════════════════════════════════════════════════════
#  SECTION 3: Camera Capture Timing
# ═══════════════════════════════════════════════════════════════

def benchmark_camera():
    """Time camera capture (if --camera flag)."""
    if not USE_CAMERA:
        return None

    print("=" * 65)
    print("  SECTION 3: CAMERA CAPTURE TIMING")
    print("=" * 65)

    # Try picamera2 first, then OpenCV
    cam = None
    cam_type = None
    try:
        from picamera2 import Picamera2
        picam = Picamera2()
        picam.configure(picam.create_preview_configuration(
            main={"size": (640, 480), "format": "RGB888"}))
        picam.start()
        time.sleep(1)
        class PiCam:
            def read(self):
                return True, picam.capture_array()
            def release(self):
                picam.stop()
        cam = PiCam()
        cam_type = "picamera2"
    except Exception:
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            cam = cap
            cam_type = "OpenCV"

    if cam is None:
        print("  No camera available")
        return None

    print(f"  Camera: {cam_type}")

    # Warmup
    for _ in range(5):
        cam.read()

    times = []
    for _ in range(N):
        t = time.time()
        ret, frame = cam.read()
        times.append((time.time() - t) * 1000)

    cam.release()

    avg = sum(times) / len(times)
    print(f"  Capture avg:  {avg:.1f}ms ({1000/avg:.1f} FPS)")
    print(f"  Capture min:  {min(times):.1f}ms")
    print(f"  Capture max:  {max(times):.1f}ms")
    print()
    return {"avg_ms": avg, "fps": 1000/avg, "type": cam_type}


# ═══════════════════════════════════════════════════════════════
#  SECTION 4: Inference Benchmark (all models, with/without undistortion)
# ═══════════════════════════════════════════════════════════════

def create_test_image():
    bg = np.zeros((480, 640, 3), dtype=np.uint8)
    bg[:] = (34, 139, 34)
    if os.path.exists("dummy.png"):
        dummy = cv2.imread("dummy.png", cv2.IMREAD_UNCHANGED)
        if dummy is not None:
            h, w = dummy.shape[:2]
            scale = 180 / h
            resized = cv2.resize(dummy, (int(w * scale), 180))
            dh, dw = resized.shape[:2]
            y_off = 480 - dh - 20
            x_off = 320 - dw // 2
            if resized.shape[2] == 4:
                alpha = resized[:, :, 3] / 255.0
                for c in range(3):
                    bg[y_off:y_off+dh, x_off:x_off+dw, c] = (
                        (1 - alpha) * bg[y_off:y_off+dh, x_off:x_off+dw, c] +
                        alpha * resized[:, :, c])
    return bg


def run_inference(label, model_path, frame, undistort_enabled):
    """Run N inferences and return stats dict."""
    calib = os.path.join(project_root, "calibration_data.npz")
    calib_bak = calib + ".bak"
    hidden = False
    if not undistort_enabled and os.path.exists(calib):
        os.rename(calib, calib_bak)
        hidden = True

    try:
        import importlib, vision
        importlib.reload(vision)
        from vision import VisionSystem

        eyes = VisionSystem(camera_index=None, model_path=model_path)
        if not eyes.using_ai:
            return None

        has_undistort = eyes._undistort_map1 is not None
        backend = "TFLite" if eyes._use_tflite_direct else "Ultralytics"

        # Get model input shape
        input_shape = "unknown"
        if hasattr(eyes, '_input_shape'):
            input_shape = f"{eyes._input_shape[1]}x{eyes._input_shape[2]}"

        # Warmup (3 runs)
        for _ in range(3):
            eyes.detect_in_image(frame.copy())

        times = []
        detections = 0
        confs = []
        for _ in range(N):
            start = time.time()
            found, x, y, conf = eyes.detect_in_image(frame.copy())
            times.append((time.time() - start) * 1000)
            if found:
                detections += 1
                confs.append(conf)

        avg = sum(times) / len(times)
        # Percentiles
        sorted_times = sorted(times)
        p50 = sorted_times[len(sorted_times) // 2]
        p95 = sorted_times[int(len(sorted_times) * 0.95)]

        return {
            "label": label,
            "backend": backend,
            "model": os.path.basename(model_path),
            "model_size_mb": os.path.getsize(model_path) / (1024 * 1024),
            "input_shape": input_shape,
            "undistort": has_undistort,
            "avg_ms": avg,
            "min_ms": min(times),
            "max_ms": max(times),
            "p50_ms": p50,
            "p95_ms": p95,
            "fps": 1000.0 / avg,
            "detections": detections,
            "total": N,
            "avg_conf": sum(confs) / len(confs) if confs else 0,
        }
    finally:
        if hidden and os.path.exists(calib_bak):
            os.rename(calib_bak, calib)


# ═══════════════════════════════════════════════════════════════
#  SECTION 5: ONNX / OpenCV DNN Benchmark (if available)
# ═══════════════════════════════════════════════════════════════

def benchmark_onnx(frame):
    """Try ONNX runtime if available and .onnx model exists."""
    results = []
    onnx_models = glob.glob("*.onnx") + glob.glob("models/*.onnx")
    if not onnx_models:
        return results

    try:
        import onnxruntime as ort
    except ImportError:
        return results

    for model_path in onnx_models:
        model_name = os.path.basename(model_path)
        size_mb = os.path.getsize(model_path) / (1024 * 1024)
        print(f"  Testing ONNX: {model_name} ({size_mb:.1f}MB)...")

        try:
            sess = ort.InferenceSession(model_path)
            input_info = sess.get_inputs()[0]
            input_shape = input_info.shape  # e.g. [1, 3, 640, 640]
            input_name = input_info.name

            # Prepare input
            h, w = input_shape[2], input_shape[3]
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = cv2.resize(img, (w, h))
            img = img.astype(np.float32) / 255.0
            img = np.transpose(img, (2, 0, 1))  # HWC→CHW
            img = np.expand_dims(img, axis=0)

            # Warmup
            sess.run(None, {input_name: img})

            times = []
            for _ in range(N):
                t = time.time()
                sess.run(None, {input_name: img})
                times.append((time.time() - t) * 1000)

            avg = sum(times) / len(times)
            results.append({
                "label": f"{model_name} (ONNX)",
                "backend": f"onnxruntime ({', '.join(ort.get_available_providers())})",
                "model": model_name,
                "model_size_mb": size_mb,
                "input_shape": f"{h}x{w}",
                "avg_ms": avg,
                "min_ms": min(times),
                "max_ms": max(times),
                "fps": 1000.0 / avg,
            })
        except Exception as e:
            print(f"    ONNX failed: {e}")

    return results


def benchmark_cv_dnn(frame):
    """Try OpenCV DNN with ONNX models."""
    results = []
    onnx_models = glob.glob("*.onnx") + glob.glob("models/*.onnx")
    if not onnx_models:
        return results

    for model_path in onnx_models:
        model_name = os.path.basename(model_path)
        size_mb = os.path.getsize(model_path) / (1024 * 1024)
        print(f"  Testing OpenCV DNN: {model_name} ({size_mb:.1f}MB)...")

        try:
            net = cv2.dnn.readNetFromONNX(model_path)
            blob = cv2.dnn.blobFromImage(frame, 1/255.0, (640, 640), swapRB=True, crop=False)

            # Warmup
            net.setInput(blob)
            net.forward()

            times = []
            for _ in range(N):
                net.setInput(blob)
                t = time.time()
                net.forward()
                times.append((time.time() - t) * 1000)

            avg = sum(times) / len(times)
            results.append({
                "label": f"{model_name} (cv2.dnn)",
                "backend": "OpenCV DNN",
                "model": model_name,
                "model_size_mb": size_mb,
                "input_shape": "640x640",
                "avg_ms": avg,
                "min_ms": min(times),
                "max_ms": max(times),
                "fps": 1000.0 / avg,
            })
        except Exception as e:
            print(f"    cv2.dnn failed: {e}")

    return results


# ═══════════════════════════════════════════════════════════════
#  SECTION 6: Threading Overhead Test
# ═══════════════════════════════════════════════════════════════

def benchmark_threading(frame):
    """Test if running inference in a thread adds overhead."""
    import threading, queue

    from vision import VisionSystem
    eyes = VisionSystem(camera_index=None, model_path="best.tflite")
    if not eyes.using_ai:
        return None

    # Warmup
    eyes.detect_in_image(frame.copy())

    # Direct (same thread)
    times_direct = []
    for _ in range(N):
        t = time.time()
        eyes.detect_in_image(frame.copy())
        times_direct.append((time.time() - t) * 1000)

    # Via thread
    result_q = queue.Queue()
    def infer_thread(f):
        t = time.time()
        eyes.detect_in_image(f)
        result_q.put((time.time() - t) * 1000)

    times_thread = []
    for _ in range(N):
        t = threading.Thread(target=infer_thread, args=(frame.copy(),))
        t.start()
        t.join()
        times_thread.append(result_q.get())

    return {
        "direct_avg_ms": sum(times_direct) / len(times_direct),
        "thread_avg_ms": sum(times_thread) / len(times_thread),
    }


# ═══════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    print()
    print("╔" + "═" * 63 + "╗")
    print("║     COMPREHENSIVE CV BENCHMARK — System + Inference + Extras    ║")
    print("╚" + "═" * 63 + "╝")
    print()

    # ── Section 1: System Info ──
    info = get_system_info()
    print_system_info(info)

    # ── Section 2: Preprocessing ──
    frame = create_test_image()
    print(f"  Test image: 640x480 (dummy on green), {N} iterations each\n")
    preproc = benchmark_preprocessing(frame)
    print_preprocessing(preproc)

    # ── Section 3: Camera (optional) ──
    cam_result = benchmark_camera()

    # ── Section 4: Inference (all models) ──
    print("=" * 65)
    print("  SECTION 4: INFERENCE BENCHMARK")
    print("=" * 65)

    models = ["best.tflite"]
    for f in sorted(glob.glob("models/*.tflite")):
        if os.path.basename(f) not in [os.path.basename(m) for m in models]:
            models.append(f)
    # Also check for .onnx
    onnx_models = glob.glob("*.onnx") + glob.glob("models/*.onnx")

    has_calib = os.path.exists("calibration_data.npz")
    print(f"  Calibration: {'YES (RMS loaded at init)' if has_calib else 'NO'}")
    print(f"  TFLite models: {[os.path.basename(m) for m in models]}")
    print(f"  ONNX models: {[os.path.basename(m) for m in onnx_models]}")
    print()

    results = []

    for model_path in models:
        if not os.path.exists(model_path):
            print(f"  [SKIP] {model_path} not found")
            continue
        model_name = os.path.basename(model_path)
        size_mb = os.path.getsize(model_path) / (1024 * 1024)

        print(f"  Testing {model_name} ({size_mb:.1f}MB) WITHOUT undistortion...")
        r = run_inference(f"{model_name} (no undistort)", model_path, frame, False)
        if r:
            results.append(r)

        if has_calib:
            print(f"  Testing {model_name} ({size_mb:.1f}MB) WITH undistortion...")
            r = run_inference(f"{model_name} (undistorted)", model_path, frame, True)
            if r:
                results.append(r)

    # ── Section 5: ONNX + cv2.dnn ──
    if onnx_models:
        print()
        print("=" * 65)
        print("  SECTION 5: ALTERNATIVE BACKENDS")
        print("=" * 65)
        onnx_results = benchmark_onnx(frame)
        dnn_results = benchmark_cv_dnn(frame)
    else:
        onnx_results = []
        dnn_results = []

    # ── Section 6: Threading ──
    print()
    print("=" * 65)
    print("  SECTION 6: THREADING OVERHEAD")
    print("=" * 65)
    thread_result = benchmark_threading(frame)
    if thread_result:
        overhead = thread_result["thread_avg_ms"] - thread_result["direct_avg_ms"]
        print(f"  Direct call:   {thread_result['direct_avg_ms']:.1f}ms")
        print(f"  Via thread:    {thread_result['thread_avg_ms']:.1f}ms")
        print(f"  Overhead:      {overhead:+.1f}ms")
        print(f"  Verdict:       {'Negligible' if abs(overhead) < 5 else 'Significant'} "
              f"— {'threaded pipeline viable' if abs(overhead) < 5 else 'avoid threading'}")
    print()

    # ═══════════════════════════════════════════════════════════
    #  RESULTS SUMMARY
    # ═══════════════════════════════════════════════════════════
    print()
    print("╔" + "═" * 63 + "╗")
    print("║                    RESULTS SUMMARY                             ║")
    print("╚" + "═" * 63 + "╝")
    print()

    if results:
        print(f"  {'Test':<35} {'Avg':>6} {'P50':>6} {'P95':>6} {'FPS':>5} {'Det':>5} {'Conf':>5}")
        print(f"  {'─'*35} {'─'*6} {'─'*6} {'─'*6} {'─'*5} {'─'*5} {'─'*5}")
        for r in results:
            det_str = f"{r['detections']}/{r['total']}"
            print(f"  {r['label']:<35} {r['avg_ms']:>5.0f}ms {r['p50_ms']:>5.0f}ms "
                  f"{r['p95_ms']:>5.0f}ms {r['fps']:>4.1f} {det_str:>5} {r['avg_conf']:>4.2f}")

    if onnx_results:
        print()
        for r in onnx_results:
            print(f"  {r['label']:<35} {r['avg_ms']:>5.0f}ms {'':>6} {'':>6} {r['fps']:>4.1f}")
    if dnn_results:
        for r in dnn_results:
            print(f"  {r['label']:<35} {r['avg_ms']:>5.0f}ms {'':>6} {'':>6} {r['fps']:>4.1f}")

    # Undistortion cost
    if has_calib and results:
        print()
        for model_path in models:
            model_name = os.path.basename(model_path)
            without = [r for r in results if r['model'] == model_name and not r['undistort']]
            with_ud = [r for r in results if r['model'] == model_name and r['undistort']]
            if without and with_ud:
                cost = with_ud[0]['avg_ms'] - without[0]['avg_ms']
                print(f"  Undistortion cost ({model_name}): {cost:+.1f}ms")

    # ── Time budget breakdown ──
    if results:
        best = min(results, key=lambda r: r['avg_ms'])
        print()
        print("  ── TIME BUDGET (best config) ──")
        preproc_ms = preproc.get("FULL PIPELINE (640)", 0)
        infer_ms = best['avg_ms']
        cam_ms = cam_result['avg_ms'] if cam_result else 0
        total = cam_ms + infer_ms
        print(f"  Camera capture:     {cam_ms:>6.1f}ms" if cam_result else "  Camera capture:     not tested (use --camera)")
        print(f"  Preprocessing:      {preproc_ms:>6.1f}ms (included in inference)")
        print(f"  Inference:          {infer_ms:>6.1f}ms (includes preproc)")
        print(f"  ─────────────────────────────")
        print(f"  Total per frame:    {total:>6.1f}ms = {1000/total:.1f} FPS" if cam_result
              else f"  Inference only:     {infer_ms:>6.1f}ms = {1000/infer_ms:.1f} FPS")

    # ── Improvement opportunities ──
    print()
    print("  ── IMPROVEMENT OPPORTUNITIES ──")
    if results:
        best_fps = max(r['fps'] for r in results)
        print(f"  Current best:       {best_fps:.1f} FPS ({1000/best_fps:.0f}ms)")
    print(f"  Input resolution:   640x640 (try 320x320 for ~4x faster preproc)")
    print(f"  Backends available: {', '.join(info['backends'])}")
    missing = []
    if "ncnn" not in str(info['backends']).lower():
        missing.append("NCNN (expected ~3x faster)")
    if "onnxruntime" not in str(info['backends']).lower():
        missing.append("ONNX Runtime")
    if missing:
        print(f"  NOT installed:      {', '.join(missing)}")
    if "None" in str(info['accelerators']):
        print(f"  No HW accelerator:  Hailo-8L ($70) would give ~60 FPS")
    if thread_result and abs(thread_result["thread_avg_ms"] - thread_result["direct_avg_ms"]) < 5:
        print(f"  Threading:          Viable — can overlap capture + inference")
    print()

    # ── Backend: ──
    if results:
        print(f"  Backend used: {results[0]['backend']}")
        if results[0].get('input_shape'):
            print(f"  Model input:  {results[0]['input_shape']}")
    print()


if __name__ == "__main__":
    main()
