#!/usr/bin/env python3
"""
Test TFLite inference on laptop — same code path the Pi uses.
No Ultralytics. Loads best.tflite directly via tflite-runtime.

Modes:
  python tests/test_tflite_laptop.py              # live webcam
  python tests/test_tflite_laptop.py --synthetic   # synthetic images from map.jpg + dummy.png

Press 'q' to quit, 's' to save a frame.
"""
import sys
import os
import time
import math
import cv2
import numpy as np

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

SYNTHETIC = "--synthetic" in sys.argv
MODEL_PATH = os.path.join(project_root, "best.tflite")

# ── Load TFLite (same fallback chain as vision.py) ───────────────────────
Interpreter = None
try:
    from tflite_runtime.interpreter import Interpreter as _I
    Interpreter = _I
    print("[OK] Backend: tflite-runtime")
except ImportError:
    try:
        from ai_edge_litert.interpreter import Interpreter as _I
        Interpreter = _I
        print("[OK] Backend: ai_edge_litert")
    except ImportError:
        try:
            import tensorflow as tf
            Interpreter = tf.lite.Interpreter
            print("[OK] Backend: tensorflow.lite")
        except ImportError:
            print("[FAIL] No TFLite backend found.")
            print("       Install one of: tflite-runtime, tensorflow")
            print("       pip install tflite-runtime")
            sys.exit(1)

if not os.path.exists(MODEL_PATH):
    print(f"[FAIL] Model not found: {MODEL_PATH}")
    sys.exit(1)

# ── Load model ───────────────────────────────────────────────────────────
print(f"[INFO] Loading: {MODEL_PATH}")
interpreter = Interpreter(model_path=MODEL_PATH)
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
input_shape = input_details[0]['shape']
input_dtype = input_details[0]['dtype']

print(f"[OK] Model loaded. Input: {input_shape} dtype={input_dtype}")


def detect_tflite(frame, conf_threshold=0.4):
    """Run TFLite inference — identical logic to vision.py TFLite path."""
    h, w = frame.shape[:2]
    input_h, input_w = input_shape[1], input_shape[2]

    # Preprocess: BGR->RGB, resize, normalize
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (input_w, input_h))
    if input_dtype == np.float32:
        img = img.astype(np.float32) / 255.0
    img = np.expand_dims(img, axis=0)

    # Inference
    interpreter.set_tensor(input_details[0]['index'], img)
    interpreter.invoke()
    output = interpreter.get_tensor(output_details[0]['index'])

    # Parse YOLOv8 output: [1, 5+nclass, num_detections]
    preds = output[0]
    if preds.shape[0] < preds.shape[-1]:
        preds = preds.T  # -> [num_detections, 5+nclass]

    # Find best detection
    best_conf = 0.0
    best_det = None
    for det in preds:
        conf = float(np.max(det[4:]))
        if conf > conf_threshold and conf > best_conf:
            best_conf = conf
            best_det = det

    if best_det is not None:
        cx = int(best_det[0] * w)
        cy = int(best_det[1] * h)
        bw = int(best_det[2] * w)
        bh = int(best_det[3] * h)
        x1, y1 = cx - bw // 2, cy - bh // 2
        x2, y2 = cx + bw // 2, cy + bh // 2
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, f"TFLite {best_conf:.2f}", (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        return True, cx, cy, best_conf, bw, bh

    return False, 0, 0, 0.0, 0, 0


# ── Synthetic image generation ───────────────────────────────────────────

def make_synthetic_frame(alt_m):
    """Generate a frame as if camera is looking down from alt_m meters."""
    import config

    map_path = os.path.join(project_root, config.MAP_FILE)
    dummy_path = os.path.join(project_root, config.DUMMY_FILE)

    if not os.path.exists(map_path) or not os.path.exists(dummy_path):
        print(f"[FAIL] Need {map_path} and {dummy_path} for synthetic mode")
        sys.exit(1)

    map_img = cv2.imread(map_path)
    dummy_img = cv2.imread(dummy_path, cv2.IMREAD_UNCHANGED)
    map_h, map_w = map_img.shape[:2]

    # FOV math (same as simulation.py)
    fov = 2 * math.atan(config.SENSOR_WIDTH_MM / (2 * config.FOCAL_LENGTH_MM))
    ground_w = 2 * alt_m * math.tan(fov / 2)
    px_per_m = config.IMAGE_W / ground_w

    # Dummy size on screen
    dummy_h_screen = int(config.DUMMY_HEIGHT_M * px_per_m)
    dummy_w_screen = max(1, int(dummy_h_screen * 0.4))

    # Crop a region from the map
    crop_w = int(ground_w * (map_w / config.MAP_WIDTH_METERS))
    crop_h = int(crop_w * (config.IMAGE_H / config.IMAGE_W))

    cx = map_w // 2
    cy = map_h // 2
    x1 = max(0, cx - crop_w // 2)
    y1 = max(0, cy - crop_h // 2)
    x2 = min(map_w, x1 + crop_w)
    y2 = min(map_h, y1 + crop_h)

    crop = map_img[y1:y2, x1:x2]
    frame = cv2.resize(crop, (config.IMAGE_W, config.IMAGE_H))

    # Paste dummy in centre
    if dummy_h_screen > 3 and dummy_w_screen > 3:
        dummy_resized = cv2.resize(dummy_img, (dummy_w_screen, dummy_h_screen))
        px = config.IMAGE_W // 2 - dummy_w_screen // 2
        py = config.IMAGE_H // 2 - dummy_h_screen // 2

        if dummy_resized.shape[2] == 4:
            alpha = dummy_resized[:, :, 3] / 255.0
            for c in range(3):
                roi = frame[py:py + dummy_h_screen, px:px + dummy_w_screen, c].astype(float)
                frame[py:py + dummy_h_screen, px:px + dummy_w_screen, c] = \
                    (alpha * dummy_resized[:, :, c] + (1 - alpha) * roi).astype(np.uint8)
        else:
            frame[py:py + dummy_h_screen, px:px + dummy_w_screen] = dummy_resized

    return frame, dummy_h_screen


# ── Main loop ────────────────────────────────────────────────────────────

if SYNTHETIC:
    print("\n=== SYNTHETIC MODE — altitude sweep ===\n")
    altitudes = [5, 10, 15, 20, 25, 30, 35, 40, 50]
    results = []

    for alt in altitudes:
        frame, expected_px = make_synthetic_frame(alt)
        t0 = time.time()
        found, x, y, conf, bw, bh = detect_tflite(frame)
        ms = (time.time() - t0) * 1000

        status = f"DETECTED conf={conf:.2f} bbox={bw}x{bh}" if found else "not detected"
        print(f"  {alt:3d}m  (dummy ~{expected_px}px)  {ms:.0f}ms  {status}")
        results.append({"alt": alt, "found": found, "conf": conf, "ms": ms, "expected_px": expected_px})

        # Show frame
        label = f"{alt}m - {'DETECTED' if found else 'MISS'}"
        cv2.putText(frame, label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        cv2.imshow("TFLite Synthetic Test", frame)
        cv2.waitKey(500)

    # Summary
    detected = [r for r in results if r["found"]]
    max_alt = max(r["alt"] for r in detected) if detected else 0
    avg_ms = sum(r["ms"] for r in results) / len(results)

    print(f"\n{'=' * 50}")
    print(f"  Max detection altitude: {max_alt}m")
    print(f"  Detected at: {len(detected)}/{len(results)} altitudes")
    print(f"  Avg inference: {avg_ms:.0f}ms")
    print(f"{'=' * 50}\n")

    cv2.waitKey(0)
    cv2.destroyAllWindows()

else:
    print("\n=== WEBCAM MODE — point at dummy printout ===")
    print("  'q' = quit, 's' = save frame\n")

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[FAIL] Cannot open webcam")
        sys.exit(1)

    frame_count = 0
    detect_count = 0
    total_ms = 0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                continue

            frame_count += 1
            t0 = time.time()
            found, x, y, conf, bw, bh = detect_tflite(frame)
            ms = (time.time() - t0) * 1000
            total_ms += ms

            if found:
                detect_count += 1

            avg_ms = total_ms / frame_count
            fps = 1000.0 / avg_ms if avg_ms > 0 else 0

            cv2.putText(frame, f"TFLite Direct | {ms:.0f}ms | {fps:.1f}fps",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            cv2.putText(frame, f"Detections: {detect_count}/{frame_count}",
                        (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

            if found:
                cv2.putText(frame, f"TARGET ({conf:.2f}) bbox={bw}x{bh}",
                            (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            cv2.imshow("TFLite Laptop Test", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                path = f"tflite_frame_{frame_count:04d}.jpg"
                cv2.imwrite(path, frame)
                print(f"  Saved: {path}")

    except KeyboardInterrupt:
        pass

    cap.release()
    cv2.destroyAllWindows()

    avg_ms = total_ms / max(1, frame_count)
    print(f"\n{'=' * 50}")
    print(f"  Frames:     {frame_count}")
    print(f"  Detections: {detect_count}")
    print(f"  Avg time:   {avg_ms:.0f}ms")
    print(f"  Avg FPS:    {1000/avg_ms:.1f}" if avg_ms > 0 else "  Avg FPS:    N/A")
    print(f"{'=' * 50}\n")
