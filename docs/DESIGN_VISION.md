# Design Rationale: Computer Vision Subsystem

This document describes the design decisions behind the vision subsystem of the SAR drone, intended for inclusion in the MSc project report (AENGM0074). All benchmarks are from measured hardware testing on the Raspberry Pi 5.

---

## 1. YOLOv8n Model Selection

YOLOv8 was selected as the object detection architecture for its single-stage design, which provides real-time inference without the two-pass overhead of region-proposal networks. Within the YOLOv8 family, the **nano variant (YOLOv8n)** was chosen to meet the computational constraints of the Raspberry Pi 5 CPU.

| Variant | Parameters | TFLite Size | Est. Pi 5 Inference | Rationale |
|---------|-----------|-------------|---------------------|-----------|
| YOLOv8n | 3.2M | 3.2 MB | ~206 ms (4.8 FPS) | **Selected** -- fast enough for search |
| YOLOv8s | 11.2M | ~22 MB | ~400 ms (2.5 FPS) | Higher accuracy, but halves frame rate |
| YOLOv8m | 25.9M | ~50 MB | ~800 ms (1.2 FPS) | Too slow for real-time search |

**Measured benchmarks (Pi 5, TFLite, XNNPACK CPU, 2026-03-11):**
- Average inference: **206.5 ms** per frame (4.8 FPS)
- Detection rate: 50/50 frames with dummy present
- Average confidence: 0.966
- Model file: 3.2 MB float32 TFLite

**Frame spacing analysis.** At the search altitude speed of 6 m/s (`SPEED_AT_LOW` in `config.py`) and 4.8 FPS, the drone moves approximately **1.25 m between frames**. Given the camera's ground footprint at 35 m altitude (approximately 47 m x 35 m from the GSD calculation), each frame covers substantial area with significant overlap to the previous frame. A target occupying even 2 m of ground extent will appear in multiple consecutive frames, making the detection rate acceptable despite the relatively low frame rate.

The tradeoff is explicit: YOLOv8s would improve detection at the margins (unusual angles, partial occlusion, extreme altitude), but at 2.5 FPS and 6 m/s the drone would move 2.4 m between frames, reducing the number of frames in which a target appears. For a binary search task (single dummy in a field), nano-class detection rates proved sufficient.

---

## 2. Dual Backend Architecture

The vision subsystem (`vision.py`) implements a platform-adaptive backend selection to support development on a GPU-equipped laptop and deployment on the Pi without code changes.

**Backend priority chain:**

1. **Ultralytics YOLO** (laptop) -- full framework with GPU acceleration, automatic output parsing, rich debugging. Used during development and simulation.
2. **TFLite** (Pi) -- lightweight CPU-optimized runtime via `tflite-runtime` or `ai-edge-litert` (required on Python 3.13 where `tflite-runtime` is broken). Parses raw YOLOv8 output tensors manually.
3. **NCNN** (experimental) -- ARM-optimized inference engine. Available as a fallback, activated with `--backend ncnn`.

**Auto-detection logic** (from `vision.py`, lines 7-38):

```python
YOLO = None
try:
    from ultralytics import YOLO as _YOLO
    YOLO = _YOLO
except ImportError:
    pass

TFLiteInterpreter = None
if YOLO is None:
    try:
        from tflite_runtime.interpreter import Interpreter
        TFLiteInterpreter = Interpreter
    except ImportError:
        # fallback to ai-edge-litert or tensorflow.lite
```

The backend is selected at import time based on which packages are installed. On the laptop, `ultralytics` is present and takes priority. On the Pi, only `ai-edge-litert` is installed, so TFLite is used. No environment variables or flags are needed.

**Unified interface.** All backends expose the same function signature:

```python
detect_in_image(frame) -> (found: bool, x: int, y: int, conf: float)
```

Where `x, y` is the pixel centre of the highest-confidence detection and `conf` is its confidence score. All other modules (state machine, GPS estimation, ground station) call only this interface and are completely backend-agnostic. This separation means the model, preprocessing pipeline, or inference engine can be changed without modifying any other file in the system.

---

## 3. TFLite Coordinate Convention

YOLOv8 TFLite exports produce raw output tensors of shape `[1, 5+nclass, 8400]`, where each of the 8400 anchor predictions contains `[cx, cy, w, h, class_conf...]`. The coordinate values may be either:

- **Normalized** (0.0 to 1.0), representing fractions of the 640x640 input tensor dimensions
- **Pixel coordinates** (0 to 640), representing absolute positions in the input tensor

This ambiguity arises from differences in export toolchains and model versions. We implemented a runtime guard that checks whether coordinate values exceed 1.5:

```python
if raw_cx > 1.5:
    # Pixel coords -- scale from 640x640 to actual frame size
    cx = int(raw_cx * w / 640)
    cy = int(raw_cy * h / 640)
else:
    # Normalized coords -- scale to frame size
    cx = int(raw_cx * w)
    cy = int(raw_cy * h)
```

This guard is implemented in both the NCNN backend (lines 275-286 of `vision.py`) and was validated against the TFLite backend where coordinates are consistently normalized. The threshold of 1.5 provides a safe margin: normalized values never exceed 1.0, while pixel coordinates in a 640x640 tensor are always integers >= 0. Without this guard, pixel-coordinate outputs would produce bounding boxes clustered in the top-left corner of the frame (since values like 320 would be interpreted as 320x the frame width).

---

## 4. Camera Considerations

The **Sony IMX296 global shutter** sensor was selected for the Pi camera module. The global shutter is critical for aerial robotics: unlike rolling shutter sensors (which read rows sequentially and produce skew/wobble artifacts on moving platforms), the IMX296 exposes all pixels simultaneously. This eliminates motion-induced geometric distortion during flight, particularly during yaw manoeuvres and in crosswind conditions.

**BGR output anomaly.** During hardware integration, we discovered that the IMX296 outputs pixel data in BGR channel order despite the picamera2 `RGB888` format label. This was identified by testing all six channel permutations against known colour targets. The practical consequence is that **no `cv2.cvtColor` conversion is applied** -- the data arrives in OpenCV's native BGR format and is used directly. Adding a conversion (as would be expected from the "RGB888" label) would swap red and blue channels, degrading detection accuracy on colour-sensitive features.

From `vision.py`, line 402-404:
```python
frame = self._picam.capture_array()
# IMX296 Global Shutter: sensor outputs BGR despite RGB888 label
# No conversion needed -- data is already in OpenCV's BGR format
```

**Resolution.** The native sensor resolution of **1456 x 1088 pixels** is used for capture (`IMAGE_W = 1456`, `IMAGE_H = 1088` in `config.py`). The full-resolution frame is passed to `detect_in_image()`, which internally resizes to the model's 640x640 input tensor. This preserves maximum detail for the operator's video stream while the model receives a downscaled version for inference.

---

## 5. Lens Undistortion

Barrel distortion from the IMX296 lens module was calibrated using a printed checkerboard pattern (calib.io, 14x9 board, 13x8 inner corners, 28 mm square size). The calibration achieved an **RMS reprojection error of 0.399 pixels**, indicating good fit.

**Implementation.** Undistortion remap maps are precomputed once at startup using `cv2.initUndistortRectifyMap()` and stored as class attributes. Every frame passes through `cv2.remap()` before inference:

```python
# Precomputed at __init__ (one-time cost)
new_mtx, _ = cv2.getOptimalNewCameraMatrix(mtx, dist, (img_w, img_h), 0, (img_w, img_h))
self._undistort_map1, self._undistort_map2 = cv2.initUndistortRectifyMap(
    mtx, dist, None, new_mtx, (img_w, img_h), cv2.CV_16SC2)

# Per-frame (in detect_in_image)
frame = cv2.remap(frame, self._undistort_map1, self._undistort_map2, cv2.INTER_LINEAR)
```

**Performance cost: approximately 1.5 ms per frame** (measured on Pi 5), which is negligible relative to the 206 ms inference time. The `alpha=0` parameter in `getOptimalNewCameraMatrix` crops the undistorted image to remove black borders, so no pixels are wasted.

Because undistortion is applied inside `vision.py`'s `detect_in_image()`, all scripts that use the vision system (main.py, pi_flight.py, passive_watch.py) benefit automatically without any code changes. The `calibration_data.npz` file must be present in the project root; if absent, undistortion is silently skipped.

---

## 6. Model Retraining (v2)

The initial YOLOv8n model was trained on purely synthetic data at 640x640 resolution. The **v2 model** was retrained on a mixed dataset at the camera's native aspect ratio to improve real-world performance.

**Dataset composition (366 images at 1456x1088):**

| Category | Count | Source | Purpose |
|----------|-------|--------|---------|
| Synthetic | 300 | `generate_dataset_v2.py` | dummy.png composited on DJI video frame backgrounds |
| Real | 16 | `tools/label_tool.py --full` | Manually labelled frames from DJI flight video |
| Negatives | 50 | DJI video frames (no dummy) | Reduce false positive rate |

**Synthetic data generation.** The `generate_dataset_v2.py` script composites the dummy image onto background crops extracted from real DJI flight footage. The dummy is scaled according to the altitude-dependent ground sample distance so that its apparent size matches what the camera would see at each altitude. Augmentations include brightness, contrast, Gaussian blur, rotation, and scale variation.

**Real data labelling.** `tools/label_tool.py --full` replays the DJI video at native 1456x1088 resolution and allows click-drag bounding box annotation. The `--full` flag is critical: without it, frames are squished to 640x640 for display, which produces labels that do not map correctly to the native aspect ratio.

**Training configuration (Google Colab, T4 GPU):**
- Image size: 1088 (YOLO internally pads to maintain aspect ratio)
- Epochs: 150
- Batch size: 8
- Architecture: YOLOv8n (same as v1)

**Results:**
- mAP50: **0.995**
- Export: TFLite float32, 11.7 MB
- Input tensor: `[1, 640, 640, 3]` (identical to v1)
- Output tensor: `[1, 5, 8400]` (identical to v1)

The v2 model is a **drop-in replacement** -- same input/output shapes, same inference pipeline, same speed on Pi. Deployment requires only copying the file:
```bash
cp cv_models/sar_v2_1088/best.tflite best.tflite
```

---

## 7. Confidence Threshold

The confidence threshold is set to **0.1** (`CONFIDENCE_THRESHOLD` in `config.py`). This is deliberately very low.

**Rationale.** The system operates in a human-in-the-loop SAR workflow where the cost of a missed detection (failing to find a casualty) far outweighs the cost of a false positive (operator dismisses an incorrect detection with one keypress). The threshold is set low to maximise recall at the expense of precision. The operator acts as the final classifier, reviewing each detection via the ground station interface and responding with:
- **Y** -- confirm as target (trigger descent/approach)
- **N** -- reject as false positive
- **I** -- mark as point of interest (revisit later)
- **X** -- dismiss

A higher threshold (e.g., 0.5 or 0.7) would reduce operator workload from false positives but risks missing the actual target when viewed at an oblique angle, partially occluded by vegetation, or at the edge of the frame where model confidence naturally drops. In a SAR context, this is an unacceptable tradeoff.

False positive management is handled downstream by the detection queue deduplication system, which clusters detections spatially and presents them in confidence-ranked order. Rejected targets are tracked by GPS coordinate, and future detections within `REJECTED_TARGET_RADIUS_M = 5.0 m` of a rejected position are automatically suppressed.

---

## 8. Single Detection Per Frame

`detect_in_image()` returns only the **highest-confidence detection** from each frame, regardless of how many objects the model identifies.

**Justification.** The mission scenario specifies a single casualty (dummy) in the search area. Returning multiple detections per frame would complicate the state machine (which detection to centre on? how to prioritise?) without operational benefit. The YOLOv8 output tensor contains 8400 anchor predictions; iterating all of them and selecting the maximum confidence is computationally trivial.

**Multi-target handling across frames.** While each frame yields at most one detection, the mission operates over hundreds of frames across the search pattern. Detections from different frames are accumulated in a **detection queue** that clusters observations by GPS position. When multiple distinct targets exist in the search area (e.g., dummy + cone + false positive), they appear as separate spatial clusters and are investigated sequentially. The queue ranks clusters by total accumulated confidence and presents them to the operator one at a time.

---

## 9. GPS Estimation from Pixel Coordinates

When the vision system detects a target at pixel coordinates `(px, py)` in the camera frame, the system estimates the target's GPS position using the following pipeline:

**Step 1: Ground Sample Distance (GSD).**

```
GSD = (SENSOR_WIDTH_MM * altitude_m) / (FOCAL_LENGTH_MM * IMAGE_W)
```

With the calibrated values from `config.py`:
- `SENSOR_WIDTH_MM = 5.02` (IMX296 sensor width)
- `FOCAL_LENGTH_MM = 5.46` (calibrated 2026-03-11, 92 cm visible at 1 m height)
- `IMAGE_W = 1456` pixels

At `TARGET_ALT = 35 m`, GSD = (5.02 * 35) / (5.46 * 1456) = **0.0221 m/pixel** (22.1 mm per pixel).

**Step 2: Pixel offset to metres.**

```
offset_x_m = (px - IMAGE_W / 2) * GSD
offset_y_m = (py - IMAGE_H / 2) * GSD
```

The offset is measured from the frame centre (directly below the drone, assuming a nadir-pointing camera).

**Step 3: Rotate by drone heading.**

The pixel-frame offsets are in camera coordinates (x = right, y = down). These are rotated by the drone's current yaw heading to convert to North-East coordinates:

```
offset_north = offset_x_m * cos(yaw) - offset_y_m * sin(yaw)
offset_east  = offset_x_m * sin(yaw) + offset_y_m * cos(yaw)
```

**Step 4: GPS offset.**

```
target_lat = drone_lat + offset_north / 111132.954
target_lon = drone_lon + offset_east / (111132.954 * cos(drone_lat))
```

**Accuracy.** At 35 m altitude, a 1-pixel error in detection centre corresponds to 22 mm on the ground -- negligible. The dominant error sources are:

1. **GPS receiver latency** (~100-200 ms) -- at 6 m/s, this introduces ~1 m along-track error
2. **GPS position noise** -- civilian GPS CEP50 is typically 2-3 m
3. **Attitude uncertainty** -- pitch/roll errors tilt the projection axis
4. **Focal length calibration** -- the 5.46 mm value has measurement uncertainty of approximately +/-0.1 mm

From DJI flight video analysis with the v2 model, the measured estimation scatter was CEP50 = 2.3 m with maximum outlier at 16.5 m (attributed to GPS timing lag at high speed). Accuracy improves as the drone descends for verification, since the GSD decreases and pixel errors map to smaller ground distances.

---

## 10. Future Work

Several improvements have been identified and partially prototyped but not yet deployed:

**NCNN backend.** An NCNN export of the v2 model exists at `cv_models/sar_v2_1088/ncnn/`. NCNN is optimised for ARM NEON instructions on the Pi 5's Cortex-A76 cores and is expected to achieve approximately **15 FPS** (65 ms per frame) -- a 3x improvement over TFLite. The NCNN backend is implemented in `vision.py` but requires `--backend ncnn` to activate and has not been benchmarked on the Pi.

**FP16 XNNPACK.** The Pi 5's Cortex-A76 cores support native FP16 (half-precision) arithmetic. TFLite's XNNPACK delegate can exploit this with a float16 quantised model, potentially achieving a **2x speedup** (~100 ms, 10 FPS) with minimal accuracy loss. This requires re-exporting the model with `half=True`.

**Threaded pipeline.** Currently, frame capture and inference are sequential: capture waits for inference to complete before grabbing the next frame. A producer-consumer threading model (capture thread fills a buffer, inference thread processes latest frame) would overlap these operations, improving effective throughput by an estimated 20-30%.

**Multi-class detection.** The current model detects a single class ("dummy"). A multi-class model trained on dummy, person, and traffic cone would allow automatic classification without operator intervention. The vision system already supports multi-class output parsing and displays class names from COCO labels when using the human.tflite backup model.

**Resolution tuning.** The model accepts 640x640 input regardless of capture resolution. Exporting at 416x416 or 320x320 would reduce inference time proportionally (inference scales roughly with pixel count) at the cost of detection range. This tradeoff could be altitude-adaptive: use 640x640 at high altitude (small targets) and 320x320 during descent (large targets, speed matters more).

---

## References to Source Files

| File | Role |
|------|------|
| `vision.py` | All CV/AI code. Dual backend, lens undistortion, detection interface |
| `config.py` | Camera parameters, confidence threshold, speed/altitude settings |
| `utils.py` | GPS-pixel conversions (GeoTransformer class) |
| `cv_models/sar_v2_1088/` | Retrained v2 model (TFLite + NCNN + .pt weights) |
| `generate_dataset_v2.py` | Synthetic dataset generation at 1456x1088 |
| `tools/label_tool.py` | Real frame labelling tool |
| `tools/fov_calibrate_video.py` | FOV calibration from flight video |
| `calibration_data.npz` | Lens distortion coefficients (Pi only, not in git) |
