#!/usr/bin/env python3
"""
TFLite Video Player — play video with TFLite detection on Pi.

Same as ncnn_video_player.py but uses TFLite backend.
Compare side by side: run this, note FPS, then run ncnn_video_player.py.

Usage on Pi:
    source pienv/bin/activate  (or ncnn_env)
    python tests/laptop/tflite_video_player.py

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

# TFLite detection
TFLiteInterpreter = None
try:
    from ai_edge_litert.interpreter import Interpreter
    TFLiteInterpreter = Interpreter
except ImportError:
    try:
        from tflite_runtime.interpreter import Interpreter
        TFLiteInterpreter = Interpreter
    except ImportError:
        try:
            import tensorflow as tf
            TFLiteInterpreter = tf.lite.Interpreter
        except ImportError:
            print("[!] No TFLite backend. Install ai-edge-litert or tflite-runtime")

VIDEO = "RealVideo/DJI_0001_1456x1088_cropped_30fps.mp4"
MODEL = "cv_models/sar_v2_1088/best.tflite"
CONF = 0.2

for i, arg in enumerate(sys.argv):
    if arg == "--video" and i + 1 < len(sys.argv):
        VIDEO = sys.argv[i + 1]
    elif arg == "--conf" and i + 1 < len(sys.argv):
        CONF = float(sys.argv[i + 1])
    elif arg == "--model" and i + 1 < len(sys.argv):
        MODEL = sys.argv[i + 1]


def load_tflite_model(model_path):
    """Load TFLite model directly."""
    if TFLiteInterpreter is None:
        return None, None, None
    interpreter = TFLiteInterpreter(model_path=model_path, num_threads=4)
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    return interpreter, input_details, output_details


def detect_tflite(interpreter, input_details, output_details, frame, conf_thresh):
    """Run TFLite inference. Returns (found, cx, cy, conf, x1, y1, x2, y2)."""
    h, w = frame.shape[:2]
    input_shape = input_details[0]['shape']
    input_h, input_w = input_shape[1], input_shape[2]

    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (input_w, input_h))
    img = img.astype(np.float32) / 255.0
    img = np.expand_dims(img, axis=0)

    interpreter.set_tensor(input_details[0]['index'], img)
    interpreter.invoke()
    output = interpreter.get_tensor(output_details[0]['index'])

    preds = output[0]
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
        cx = int(best_det[0] * w)
        cy = int(best_det[1] * h)
        bw = int(best_det[2] * w)
        bh = int(best_det[3] * h)
        x1 = max(0, cx - bw // 2)
        y1 = max(0, cy - bh // 2)
        x2 = min(w, cx + bw // 2)
        y2 = min(h, cy + bh // 2)
        return True, cx, cy, best_conf, x1, y1, x2, y2

    return False, 0, 0, 0, 0, 0, 0, 0


def main():
    if TFLiteInterpreter is None:
        return

    print("=" * 60)
    print("  TFLITE VIDEO PLAYER")
    print(f"  Video: {VIDEO}")
    print(f"  Model: {MODEL}")
    print(f"  Conf:  {CONF}")
    print("=" * 60)

    if not os.path.exists(VIDEO):
        print(f"[!] Video not found: {VIDEO}")
        return

    if not os.path.exists(MODEL):
        print(f"[!] Model not found: {MODEL}")
        return

    print("Loading TFLite model...")
    interpreter, input_details, output_details = load_tflite_model(MODEL)
    if interpreter is None:
        print("[!] Failed to load model")
        return
    print(f"TFLite loaded! Input: {input_details[0]['shape']}")

    cap = cv2.VideoCapture(VIDEO)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    vid_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    vid_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration = total / fps
    print(f"Video: {vid_w}x{vid_h} @ {fps:.0f}fps, {total} frames, {duration:.0f}s")
    print("\nControls: SPACE=pause D=skip A=back T=tiling Q=quit")

    cv2.namedWindow("TFLite Video Player", cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)

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

        t0 = time.perf_counter()
        if tiling:
            th, tw = vid_h // 2, vid_w // 2
            for ty in range(2):
                for tx in range(2):
                    tile = display[ty*th:(ty+1)*th, tx*tw:(tx+1)*tw]
                    found, cx, cy, conf, x1, y1, x2, y2 = detect_tflite(
                        interpreter, input_details, output_details, tile, CONF)
                    if found:
                        det_count += 1
                        ox, oy = tx * tw, ty * th
                        cv2.rectangle(display, (x1+ox, y1+oy), (x2+ox, y2+oy), (0, 255, 0), 2)
                        cv2.putText(display, f"{conf:.2f}", (x1+ox, y1+oy-10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        else:
            found, cx, cy, conf, x1, y1, x2, y2 = detect_tflite(
                interpreter, input_details, output_details, display, CONF)
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

        timestamp = frame_count / fps
        progress = frame_count / total if total > 0 else 0

        cv2.putText(display, "TFLite v2-1088", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        cv2.putText(display, f"FPS: {eff_fps:.1f} ({avg_ms:.0f}ms)", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0) if eff_fps > 5 else (0, 255, 255), 2)
        cv2.putText(display, f"Det: {det_count}  Tiling: {'ON' if tiling else 'OFF'}", (10, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(display, f"{timestamp:.1f}s / {duration:.1f}s ({progress*100:.0f}%)", (10, vid_h - 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

        bar_y = vid_h - 5
        cv2.rectangle(display, (0, bar_y), (vid_w, vid_h), (50, 50, 50), -1)
        cv2.rectangle(display, (0, bar_y), (int(vid_w * progress), vid_h), (0, 255, 0), -1)

        if paused:
            cv2.putText(display, "PAUSED", (vid_w//2 - 80, vid_h//2),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)

        if vid_w > 1200:
            scale = 1000 / vid_w
            display = cv2.resize(display, (int(vid_w*scale), int(vid_h*scale)))

        cv2.imshow("TFLite Video Player", display)

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
