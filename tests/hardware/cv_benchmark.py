#!/usr/bin/env python3
"""
CV Benchmark — live camera detection rate, speed, and motion blur testing.

WHAT:    Opens the camera and runs AI detection continuously, measuring real-world
         FPS, inference time, and detection rate. In blur mode, captures one frame
         and applies increasing horizontal motion blur (0-120 px kernel) to simulate
         drone flight at different speeds, reporting at which blur level detection fails.
WHY:     Tests detection performance under realistic conditions — live camera latency,
         real lighting, and motion blur. Answers: "Will AI detect the dummy from a
         moving drone at this speed?" Uses vision.py directly so results match main.py.
WHEN:    At the field before flight to verify camera+AI pipeline works. After changing
         camera settings (resolution, exposure). To determine max safe flight speed.
WHERE:   Both — Pi (with picamera2/TFLite) or laptop (with webcam/Ultralytics).
ENV:     pienv on Pi, dev venv on laptop. Needs camera access.
MODELS:  best.tflite (any YOLOv8 TFLite model in project root).
RISK:    none — read-only camera access, no drone commands.

USAGE:
    python tests/hardware/cv_benchmark.py
    python tests/hardware/cv_benchmark.py --headless
    python tests/hardware/cv_benchmark.py --blur
    python tests/hardware/cv_benchmark.py --blur --headless

FLAGS:
    --headless    No cv2.imshow display (for SSH/PuTTY sessions). Prints stats
                  to terminal every 20 frames instead.
    --blur        Motion blur test mode. Captures one frame, applies 8 blur levels,
                  reports detection survival at each level.

OUTPUT:
    Terminal report: FPS, inference time (avg/min/max), detection rate, confidence.
    In blur mode: table of blur levels vs detection success and confidence.
    With display: live video window with crosshair, FPS, and detection overlay.

BEST PRACTICES:
    - Point camera at the dummy/target before starting
    - Run --blur test to find the maximum drone speed where detection still works
    - Use --headless when running over SSH (no X11 forwarding needed)
    - Press Q or Esc to stop the live benchmark (or Ctrl+C in headless mode)

DEPENDENCIES:
    opencv-python (or opencv-python-headless), numpy, vision.py (project module)
"""
import sys
import os
import time
import numpy as np

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, project_root)

import cv2
from vision import VisionSystem

HEADLESS = "--headless" in sys.argv
BLUR_TEST = "--blur" in sys.argv
model_path = os.path.join(project_root, "best.tflite")


def run_live_benchmark(eyes):
    """Live camera benchmark — measures real detection performance."""
    print("\n  LIVE CAMERA BENCHMARK")
    print("  " + "=" * 50)
    print("  Point camera at dummy/target. Ctrl+C to stop.\n")

    if not HEADLESS:
        cv2.namedWindow("CV Benchmark", cv2.WINDOW_NORMAL)

    total_frames = 0
    total_detections = 0
    inference_times = []
    raw_times = []
    confs = []
    start = time.time()

    try:
        while True:
            # Time raw frame grab
            t0 = time.time()
            frame = eyes.get_frame()
            raw_ms = (time.time() - t0) * 1000

            if frame is None:
                time.sleep(0.01)
                continue

            total_frames += 1
            raw_times.append(raw_ms)

            # Time AI inference
            t1 = time.time()
            found, px, py, conf = eyes.detect_in_image(frame)
            inf_ms = (time.time() - t1) * 1000
            inference_times.append(inf_ms)

            if found:
                total_detections += 1
                confs.append(conf)

            # Display
            elapsed = time.time() - start
            fps = total_frames / elapsed if elapsed > 0 else 0
            det_rate = (total_detections / total_frames * 100) if total_frames > 0 else 0

            if not HEADLESS:
                # Crosshair
                h, w = frame.shape[:2]
                cv2.drawMarker(frame, (w // 2, h // 2), (255, 255, 255),
                               cv2.MARKER_CROSS, 20, 1)
                # Stats overlay
                cv2.putText(frame, f"FPS: {fps:.1f}  Inf: {inf_ms:.0f}ms",
                            (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                cv2.putText(frame, f"Det: {total_detections}/{total_frames} ({det_rate:.0f}%)",
                            (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                if found:
                    cv2.putText(frame, f"FOUND conf={conf:.2f} at ({px},{py})",
                                (10, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                cv2.imshow("CV Benchmark", frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == 27:
                    break
            else:
                # Headless: print every 20 frames
                if total_frames % 20 == 0:
                    avg_inf = np.mean(inference_times[-20:])
                    avg_conf = np.mean(confs[-20:]) if confs else 0
                    det_str = f"FOUND conf={conf:.2f}" if found else "---"
                    print(f"  #{total_frames:<5} FPS:{fps:.1f}  Inf:{avg_inf:.0f}ms  "
                          f"Det:{det_rate:.0f}%  {det_str}")

    except KeyboardInterrupt:
        pass

    if not HEADLESS:
        cv2.destroyAllWindows()

    # Results
    elapsed = time.time() - start
    print(f"\n  {'=' * 50}")
    print(f"  RESULTS ({elapsed:.1f}s)")
    print(f"  {'=' * 50}")
    print(f"  Frames:       {total_frames}")
    print(f"  Detections:   {total_detections} ({total_detections/max(1,total_frames)*100:.0f}%)")
    print(f"  FPS:          {total_frames/max(0.1,elapsed):.1f}")
    if inference_times:
        print(f"  Inference:    {np.mean(inference_times):.0f}ms avg, "
              f"{np.min(inference_times):.0f}ms min, {np.max(inference_times):.0f}ms max")
    if raw_times:
        print(f"  Frame grab:   {np.mean(raw_times):.1f}ms avg")
    if confs:
        print(f"  Confidence:   {np.mean(confs):.3f} avg, {np.max(confs):.3f} max")
    print()


def run_blur_benchmark(eyes):
    """Test how motion blur affects detection.

    Simulates different drone speeds by applying increasing amounts of
    motion blur to captured frames, then running detection on each.
    """
    print("\n  MOTION BLUR BENCHMARK")
    print("  " + "=" * 50)
    print("  Captures one frame, applies blur at different speeds.")
    print("  Shows how detection degrades with drone movement.\n")

    # Capture a clean frame
    print("  Capturing reference frame...")
    frame = None
    for _ in range(10):
        frame = eyes.get_frame()
        time.sleep(0.05)

    if frame is None:
        print("  FAIL: No camera frame")
        return

    # First check: does detection work on clean frame?
    found, px, py, conf = eyes.detect_in_image(frame.copy())
    if not found:
        print("  WARNING: No detection on clean frame — results may not be meaningful")
        print("  Point camera at dummy and try again.\n")

    # Simulate different speeds via motion blur kernel
    # kernel_size roughly maps to: pixels of smear per frame
    # At 4 FPS and 5m/s drone speed at 10m altitude:
    #   GSD ~= 0.008 m/px, so 5m/s = 625 px/s, at 4 FPS = ~156 px/frame smear
    # We test from 0 (stationary) to heavy blur
    blur_levels = [
        (0,  "Stationary (0 px)"),
        (3,  "Slow hover (3 px)"),
        (7,  "Walking speed (7 px)"),
        (15, "Light flight (15 px)"),
        (30, "Moderate (30 px)"),
        (50, "Fast flight (50 px)"),
        (80, "Very fast (80 px)"),
        (120, "Extreme (120 px)"),
    ]

    print(f"  {'Blur':<25} {'Detected':<10} {'Conf':<10} {'Inf(ms)':<10}")
    print(f"  {'-'*55}")

    results = []
    for kernel_size, label in blur_levels:
        test_frame = frame.copy()

        if kernel_size > 0:
            # Horizontal motion blur kernel
            kernel = np.zeros((kernel_size, kernel_size))
            kernel[kernel_size // 2, :] = 1.0 / kernel_size
            test_frame = cv2.filter2D(test_frame, -1, kernel)

        t0 = time.time()
        found, px, py, conf = eyes.detect_in_image(test_frame)
        ms = (time.time() - t0) * 1000

        det_str = f"YES ({conf:.2f})" if found else "NO"
        print(f"  {label:<25} {det_str:<10} {conf:.3f}     {ms:.0f}")
        results.append((kernel_size, label, found, conf, ms))

        if not HEADLESS:
            display = test_frame.copy()
            color = (0, 255, 0) if found else (0, 0, 255)
            cv2.putText(display, f"{label}: {'FOUND' if found else 'MISS'} conf={conf:.2f}",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            cv2.imshow("Blur Test", display)
            cv2.waitKey(500)

    if not HEADLESS:
        cv2.destroyAllWindows()

    # Summary
    detected = sum(1 for _, _, f, _, _ in results if f)
    print(f"\n  Detected in {detected}/{len(results)} blur levels")

    # Find max blur where detection still works
    max_blur = 0
    for ks, label, found, conf, ms in results:
        if found:
            max_blur = ks
    if max_blur > 0:
        print(f"  Max survivable blur: {max_blur} px")
    print()


def main():
    print()
    print("=" * 55)
    print("   CV BENCHMARK — using vision.py pipeline")
    print("   Same camera + AI as main.py")
    print("=" * 55)
    print()

    print(f"  Model: {model_path}")
    print(f"  Headless: {HEADLESS}")
    print(f"  Blur test: {BLUR_TEST}")

    eyes = VisionSystem(camera_index=0, model_path=model_path)

    if not eyes.using_ai:
        print("\n  FAIL: AI model not loaded. Cannot benchmark.")
        sys.exit(1)

    # Show what vision.py is doing
    try:
        import config
        print(f"  Flip 180: {getattr(config, 'CAMERA_FLIP_180', False)}")
        print(f"  Color correction: {getattr(config, 'CAMERA_COLOR_CORRECTION', False)}")
        print(f"  Resolution: {config.IMAGE_W}x{config.IMAGE_H}")
    except Exception:
        pass

    if BLUR_TEST:
        run_blur_benchmark(eyes)
    else:
        run_live_benchmark(eyes)

    eyes.release()


if __name__ == "__main__":
    main()
