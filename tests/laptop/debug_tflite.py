#!/usr/bin/env python3
"""
debug_tflite.py — Raw TFLite Model Output Inspector

WHAT:    Loads best.tflite directly and prints raw input/output tensor details
         (shapes, dtypes, value ranges). Creates a synthetic test image with
         dummy.png on a green background, runs inference, and displays the top
         10 detections sorted by confidence. Shows three different coordinate
         interpretation formulas to help debug bounding box coordinate issues.
WHY:     When detection coordinates are wrong (bbox in wrong position), this
         script reveals whether the raw output values are normalized (0-1) or
         pixel coordinates, and which interpretation formula is correct. Critical
         for debugging the TFLite parsing code in vision.py.
WHEN:    When detection bounding boxes appear in wrong positions. After exporting
         a new TFLite model. When debugging coordinate space mismatches.
WHERE:   Laptop only.
ENV:     "venv" (needs tflite-runtime or tensorflow, plus opencv and numpy)
MODELS:  best.tflite from project root (hardcoded path).
RISK:    None — diagnostic tool, read-only.

USAGE:
    python tests/laptop/debug_tflite.py

FLAGS:
    None.

OUTPUT:
    Console output: tensor shapes, dtypes, raw output ranges, top detections
    with cx/cy/w/h values, and coordinate interpretation comparison.
    Expected: dummy should be detected near center (~320, ~280).

BEST PRACTICES:
    - Run when detection boxes appear offset or scaled incorrectly
    - Compare the three coordinate formulas to find the correct one
    - Check that output shape matches expected [1, 5, 8400] for YOLOv8n

DEPENDENCIES:
    tflite-runtime (or tensorflow), opencv-python, numpy
"""
import sys
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, project_root)

import cv2
import numpy as np

# Load model directly
TFLiteInterpreter = None
try:
    from tflite_runtime.interpreter import Interpreter
    TFLiteInterpreter = Interpreter
except ImportError:
    try:
        import tensorflow as tf
        TFLiteInterpreter = tf.lite.Interpreter
    except ImportError:
        print("No TFLite backend")
        sys.exit(1)

interpreter = TFLiteInterpreter(model_path="best.tflite")
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

print(f"Input shape:  {input_details[0]['shape']}")
print(f"Input dtype:  {input_details[0]['dtype']}")
print(f"Output shape: {output_details[0]['shape']}")
print(f"Output dtype: {output_details[0]['dtype']}")
print(f"Num outputs:  {len(output_details)}")
for i, od in enumerate(output_details):
    print(f"  Output[{i}] shape={od['shape']} dtype={od['dtype']}")

# Create test image with dummy
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
                    alpha * resized[:, :, c]
                )

# Preprocess
input_shape = input_details[0]['shape']
input_h, input_w = input_shape[1], input_shape[2]
img = cv2.cvtColor(bg, cv2.COLOR_BGR2RGB)
img = cv2.resize(img, (input_w, input_h))
if input_details[0]['dtype'] == np.float32:
    img = img.astype(np.float32) / 255.0
img = np.expand_dims(img, axis=0)

# Run
interpreter.set_tensor(input_details[0]['index'], img)
interpreter.invoke()
output = interpreter.get_tensor(output_details[0]['index'])

print(f"\nRaw output shape: {output.shape}")
print(f"Raw output min: {output.min():.4f}  max: {output.max():.4f}")

preds = output[0]
print(f"preds shape before transpose: {preds.shape}")

if preds.shape[0] < preds.shape[-1]:
    preds = preds.T
    print(f"preds shape after transpose: {preds.shape}")

# Show top 5 detections by confidence
confs = []
for i, det in enumerate(preds):
    conf = float(np.max(det[4:]))
    if conf > 0.3:
        confs.append((i, det[:6], conf))

confs.sort(key=lambda x: x[2], reverse=True)
print(f"\nTop detections (conf > 0.3):")
print(f"{'idx':>5} {'cx':>8} {'cy':>8} {'w':>8} {'h':>8} {'conf':>8}")
for idx, vals, conf in confs[:10]:
    print(f"{idx:5d} {vals[0]:8.2f} {vals[1]:8.2f} {vals[2]:8.2f} {vals[3]:8.2f} {conf:8.4f}")

if confs:
    best = confs[0]
    cx_raw, cy_raw = best[1][0], best[1][1]
    print(f"\nBest detection raw values: cx={cx_raw:.4f}, cy={cy_raw:.4f}")
    print(f"Input size: {input_w}x{input_h}")
    print(f"Frame size: 640x480")

    # Current code: divides by input_w (assumes pixel coords)
    cx_current = int(cx_raw / input_w * 640)
    cy_current = int(cy_raw / input_h * 480)
    print(f"\nCurrent formula (div by input): ({cx_current}, {cy_current})")

    # Alt: values are already 0-1 normalized
    cx_norm = int(cx_raw * 640)
    cy_norm = int(cy_raw * 480)
    print(f"Alt formula (0-1 normalized):  ({cx_norm}, {cy_norm})")

    # Alt: values are already pixel coords in input space
    cx_pixel = int(cx_raw / input_w * 640)
    cy_pixel = int(cy_raw / input_h * 480)
    print(f"Alt formula (pixel in input):  ({cx_pixel}, {cy_pixel})")

    print(f"\nExpected: dummy is near center (~320, ~280)")
