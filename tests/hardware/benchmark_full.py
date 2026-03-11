#!/usr/bin/env python3
"""
Full CV Benchmark — runs all comparisons in one go.
Tests: with/without undistortion, with/without camera, all models.

Usage on Pi:
    python tests/hardware/benchmark_full.py
"""
import sys, os, time, glob
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, project_root)
os.chdir(project_root)

import cv2
import numpy as np

N = 30  # inferences per test

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

def run_benchmark(label, model_path, frame, undistort_enabled):
    """Run N inferences and return stats dict."""
    # Temporarily rename calibration file to disable undistortion
    calib = os.path.join(project_root, "calibration_data.npz")
    calib_bak = calib + ".bak"
    hidden = False
    if not undistort_enabled and os.path.exists(calib):
        os.rename(calib, calib_bak)
        hidden = True

    try:
        from vision import VisionSystem
        # Reload module to pick up calibration change
        import importlib, vision
        importlib.reload(vision)
        from vision import VisionSystem

        eyes = VisionSystem(camera_index=None, model_path=model_path)
        if not eyes.using_ai:
            return None

        has_undistort = eyes._undistort_map1 is not None
        backend = "TFLite" if eyes._use_tflite_direct else "Ultralytics"

        # Warmup
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
        return {
            "label": label,
            "backend": backend,
            "model": os.path.basename(model_path),
            "undistort": has_undistort,
            "avg_ms": avg,
            "min_ms": min(times),
            "max_ms": max(times),
            "fps": 1000.0 / avg,
            "detections": detections,
            "total": N,
            "avg_conf": sum(confs) / len(confs) if confs else 0,
        }
    finally:
        if hidden and os.path.exists(calib_bak):
            os.rename(calib_bak, calib)


def main():
    print("=" * 62)
    print("        FULL CV BENCHMARK — All Comparisons")
    print("=" * 62)

    frame = create_test_image()
    print(f"  Test image: 640x480 (dummy on green)")
    print(f"  Inferences per test: {N}")

    # Find all models
    models = ["best.tflite"]
    for f in sorted(glob.glob("models/*.tflite")):
        if os.path.basename(f) not in [os.path.basename(m) for m in models]:
            models.append(f)

    has_calib = os.path.exists("calibration_data.npz")
    print(f"  Calibration file: {'YES' if has_calib else 'NO'}")
    print(f"  Models found: {[os.path.basename(m) for m in models]}")
    print()

    results = []

    for model_path in models:
        if not os.path.exists(model_path):
            print(f"  [SKIP] {model_path} not found")
            continue

        model_name = os.path.basename(model_path)
        size_mb = os.path.getsize(model_path) / (1024 * 1024)

        # Test WITHOUT undistortion
        print(f"  Testing {model_name} ({size_mb:.1f}MB) WITHOUT undistortion...")
        r = run_benchmark(f"{model_name} (no undistort)", model_path, frame, undistort_enabled=False)
        if r:
            results.append(r)

        # Test WITH undistortion (only if calibration exists)
        if has_calib:
            print(f"  Testing {model_name} ({size_mb:.1f}MB) WITH undistortion...")
            r = run_benchmark(f"{model_name} (undistorted)", model_path, frame, undistort_enabled=True)
            if r:
                results.append(r)

    # ── Results Table ──
    if not results:
        print("\n  No results! Check model files.")
        return

    print()
    print("=" * 62)
    print("  RESULTS")
    print("=" * 62)
    print()
    print(f"  {'Test':<35} {'Avg ms':>7} {'FPS':>6} {'Det':>5} {'Conf':>6}")
    print(f"  {'─'*35} {'─'*7} {'─'*6} {'─'*5} {'─'*6}")

    for r in results:
        det_str = f"{r['detections']}/{r['total']}"
        print(f"  {r['label']:<35} {r['avg_ms']:>6.1f}ms {r['fps']:>5.1f} {det_str:>5} {r['avg_conf']:>5.3f}")

    # ── Undistortion cost ──
    if has_calib:
        print()
        for model_path in models:
            model_name = os.path.basename(model_path)
            without = [r for r in results if r['model'] == model_name and not r['undistort']]
            with_ud = [r for r in results if r['model'] == model_name and r['undistort']]
            if without and with_ud:
                cost = with_ud[0]['avg_ms'] - without[0]['avg_ms']
                print(f"  Undistortion cost ({model_name}): {cost:+.1f}ms")

    print()
    print(f"  Backend: {results[0]['backend']}")
    print()

if __name__ == "__main__":
    main()
