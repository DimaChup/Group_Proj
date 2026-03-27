# Vision System Optimization and Benchmarking

**SAR Drone Project (AENGM0074) -- MSc Aerial Robotics**

This document presents a comprehensive analysis of the onboard computer vision system,
covering architecture decisions, model selection and training, hardware benchmarks,
detection envelope characterisation (motion blur, altitude limits, speed constraints),
GPS estimation accuracy, and future optimisation pathways. All numerical values are
drawn from measured benchmarks and calibrated parameters.

---

## 1. Vision System Architecture

### 1.1 Dual-Backend Design

The detection system (`vision.py`) implements a single public interface --
`detect_in_image(frame)` returning `(found, x, y, confidence)` -- backed by three
runtime engines selected automatically at startup:

| Priority | Backend | Runtime | Model Format | Typical Platform |
|:--------:|---------|---------|--------------|------------------|
| 0 | NCNN | ncnn (C++ via Python bindings) | `.param` + `.bin` | Pi 5 (ARM-optimised) |
| 1 | Ultralytics YOLO | PyTorch + Ultralytics | `.tflite` or `.pt` | Laptop (dev/GPU) |
| 2 | TFLite Direct | ai-edge-litert / tflite-runtime | `.tflite` | Pi 5 (production) |

Backend selection is automatic: vision.py attempts imports in priority order and uses
the first available. On the Raspberry Pi, Ultralytics is not installed (it pulls in
PyTorch at 2+ GB, unacceptable for a 4 GB embedded board), so inference falls through
to TFLite Direct. On the development laptop, Ultralytics provides GPU acceleration and
richer debugging output.

**Why this matters:** All mission scripts (`main.py`, `pi_flight.py`, `passive_watch.py`)
call `detect_in_image()` without knowing which backend is active. The model file
(`best.tflite`, 3.2 MB) is identical on both platforms. Swapping models requires only
copying a file -- no code changes.

### 1.2 Preprocessing Pipeline

Every frame passes through the same pipeline regardless of backend:

1. **Lens undistortion** (if `calibration_data.npz` exists): precomputed `cv2.remap()`
   maps, cost ~1.5 ms per frame.
2. **Colour conversion**: BGR to RGB (`cv2.cvtColor`).
3. **Resize**: bilinear interpolation from native resolution (1456 x 1088) to model
   input (640 x 640).
4. **Normalisation**: float32 division by 255 (TFLite/NCNN) or handled internally
   (Ultralytics).

### 1.3 Output Parsing

YOLOv8 TFLite output shape is `[1, 5, 8400]` -- transposed to `[8400, 5]` where each
row is `[cx, cy, w, h, class_conf]` in normalised coordinates. The highest-confidence
detection above `CONFIDENCE_THRESHOLD` is returned. Bounding box coordinates are scaled
back to the original frame dimensions for overlay drawing and GPS estimation.

---

## 2. Model Selection and Training

### 2.1 Why YOLOv8n

YOLOv8n (nano) was selected as the optimal trade-off between accuracy and inference
speed on the Raspberry Pi 5's Cortex-A76 CPU. The table below compares three YOLOv8
variants:

| Variant | Parameters | FLOPs (B) | COCO mAP50 | TFLite Size | Expected Pi 5 FPS |
|---------|:----------:|:---------:|:----------:|:-----------:|:-----------------:|
| YOLOv8n | 3.2 M | 8.7 | 37.3 | 3.2 -- 11.7 MB | **4.8** (measured) |
| YOLOv8s | 11.2 M | 28.6 | 44.9 | ~23 MB | ~1.5 (estimated) |
| YOLOv8m | 25.9 M | 78.9 | 50.2 | ~52 MB | ~0.6 (estimated) |

YOLOv8s would reduce throughput to approximately 1.5 FPS, cutting the number of frames
per target flyover from 11--17 down to 3--5. YOLOv8m would yield sub-1 FPS, making
real-time search impractical. YOLOv8n at 4.8 FPS provides 11--17 detection opportunities
per target pass (Section 6), which is more than sufficient given that a single detection
triggers investigation.

### 2.2 Training Data Evolution

| Version | Dataset | Resolution | Images | Real Frames | Negatives | mAP50 |
|---------|---------|:----------:|:------:|:-----------:|:---------:|:-----:|
| v1 (original) | Synthetic only (map.jpg backgrounds) | 640 x 640 | 200 | 0 | 0 | ~0.95 |
| **v2 (current)** | **Synthetic + real + negatives** | **1456 x 1088** | **366** | **16** | **50** | **0.995** |

**v2 training configuration (Google Colab, T4 GPU):**
- Base weights: `yolov8n.pt` (COCO pretrained)
- Training resolution: `imgsz=1088` (native camera resolution for better feature learning)
- Export resolution: `imgsz=640` (TFLite runtime always resizes to 640 x 640)
- Epochs: 150, batch size: 8, early stopping patience: 30
- Augmentation: rotation +/-20 deg, scale 0.7, mosaic 1.0, copy-paste 0.2, horizontal flip 0.5

### 2.3 Dataset Composition

The v2 dataset (`dataset_v2/`, 366 images at 1456 x 1088) comprises:

- **300 synthetic images**: dummy.png composited on real DJI flight video frame
  backgrounds. Altitude-correct scaling ensures the dummy pixel size matches what the
  camera would see at each simulated altitude (15--50 m). Augmentation includes random
  brightness (+/-30%), contrast (+/-20%), Gaussian blur (sigma 0--2), rotation, and
  scale variation.
- **16 real labelled frames**: extracted from DJI flight video at various altitudes
  using `tools/label_tool.py --full` (native resolution, no squishing to 640 x 640).
- **50 negative images**: real flight video frames containing no target. Empty label
  files teach the model to suppress false positives on grass, paths, and shadows.

### 2.4 Why Synthetic Data Works

Synthetic compositing is effective for this application because:

1. The backgrounds are real satellite/aerial imagery, not procedurally generated.
2. The altitude-correct scaling produces geometrically accurate training samples.
3. The single-class detection task (one target type on uniform grass) has low visual
   complexity compared to general object detection.
4. The 16 real frames anchor the model to actual camera characteristics (colour
   response, noise, compression artefacts).

The mAP50 of 0.995 on the v2 dataset (noting that train and validation sets overlap --
a known limitation) and consistent high-confidence detections (0.966 avg) on real Pi
hardware confirm that the synthetic-dominant approach generalises adequately for this
constrained domain.

---

## 3. Benchmark Results

### 3.1 Pi 5 Hardware Benchmarks

All benchmarks measured on Raspberry Pi 5 (4 GB), Python 3.13, ai-edge-litert with
XNNPACK CPU delegate. Input: 640 x 640 float32. Test image: synthetic frame with
dummy at known position.

| Model | Size | Undistort | Avg Inference (ms) | FPS | Detection Rate | Avg Confidence |
|-------|:----:|:---------:|:------------------:|:---:|:--------------:|:--------------:|
| best.tflite | 3.2 MB | No | 206.5 | 4.8 | 30/30 (100%) | 0.966 |
| best.tflite | 3.2 MB | Yes | 208.0 | 4.8 | 30/30 (100%) | 0.958 |
| best2.tflite | 3.2 MB | No | 199.1 | 5.0 | 30/30 (100%) | 0.966 |
| best2.tflite | 3.2 MB | Yes | 208.4 | 4.8 | 30/30 (100%) | 0.958 |
| custom_yolov8n.tflite | 3.2 MB | No | 206.3 | 4.8 | 30/30 (100%) | 0.966 |
| custom_yolov8n.tflite | 3.2 MB | Yes | 208.8 | 4.8 | 30/30 (100%) | 0.958 |

Notes:
- All three models are byte-identical copies (confirmed by identical confidence).
- Undistortion adds 1.5--2.5 ms -- negligible on a 206 ms baseline.
- The slight confidence drop with undistortion (0.966 to 0.958) is an artefact of
  running undistortion on a synthetic test image that was generated without lens
  distortion. On real distorted images, undistortion improves edge-region accuracy.
- Lens calibration: IMX296 sensor, calib.io 14x9 checkerboard (13x8 inner corners,
  28 mm squares), RMS reprojection error = 0.399.

### 3.2 Backend Comparison (Measured and Projected)

| Backend | Avg Inference (ms) | FPS | Status | Notes |
|---------|:------------------:|:---:|:------:|-------|
| TFLite (XNNPACK, FP32) | 206.5 | 4.8 | **Measured** | Current production backend |
| TFLite (XNNPACK, FP16) | ~100 | ~10 | Projected | Pi 5 ARMv8.2-A has native FP16 |
| NCNN (FP32) | ~68 | ~15 | Projected | ARM-optimised, export available |
| YOLO26n + NCNN | ~68 | ~15 | Projected | Newer architecture, +7% mAP |
| TFLite (INT8) | ~145 | ~7 | Projected | ~30% improvement over FP32 |

---

## 4. Motion Blur Analysis

### 4.1 Global Shutter Advantage

The Raspberry Pi Global Shutter Camera (IMX296) eliminates rolling-shutter artefacts
(skew, wobble, partial exposure) that affect CMOS sensors during motion. All rows are
exposed simultaneously, so the only blur source is translational motion during the
exposure window.

### 4.2 Blur Model

Motion blur on the ground plane:

```
blur_ground = v * t_exp                         [metres]
blur_pixels = blur_ground / GSD                  [pixels]
```

where:
- `v` = drone ground speed (m/s)
- `t_exp` = exposure time (seconds)
- `GSD` = ground sample distance = `(SENSOR_WIDTH_MM * altitude) / (FOCAL_LENGTH_MM * IMAGE_W)`

With `SENSOR_WIDTH_MM = 5.02`, `FOCAL_LENGTH_MM = 5.46`, `IMAGE_W = 1456`:

```
GSD = (5.02 * h) / (5.46 * 1456) = h * 6.315e-4    [m/px]
```

### 4.3 Blur at Operational Conditions

| Speed (m/s) | Exposure | Blur on Ground (mm) | Blur at 20 m (px) | Blur at 35 m (px) | Blur at 50 m (px) |
|:-----------:|:--------:|:-------------------:|:-----------------:|:-----------------:|:-----------------:|
| 6 | 1/500 s | 12 | 1.0 | 0.5 | 0.4 |
| 6 | 1/1000 s | 6 | 0.5 | 0.3 | 0.2 |
| 10 | 1/500 s | 20 | 1.6 | 0.9 | 0.6 |
| 10 | 1/1000 s | 10 | 0.8 | 0.5 | 0.3 |
| 15 | 1/500 s | 30 | 2.4 | 1.4 | 0.9 |
| 15 | 1/1000 s | 15 | 1.2 | 0.7 | 0.5 |

### 4.4 Blur Impact on Detection

At the operational speed profile (6--10 m/s, altitude-dependent) with 1/1000 s shutter
speed, motion blur is 0.2--0.8 pixels -- effectively sub-pixel and invisible to the
detector. Even at a conservative 1/500 s exposure, blur remains below 1.6 pixels at
the maximum speed.

Gaussian blur simulation on synthetic test images shows that even with a 3-pixel
kernel, detection confidence drops by less than 5%. The critical speed where blur
exceeds 1 pixel (at 35 m altitude, 1/1000 s) is approximately 30 m/s -- well above
the maximum drone speed of 15 m/s.

**Conclusion: Motion blur is not a limiting factor for detection performance.** The
global shutter combined with short exposure times freezes the image at any achievable
drone speed.

---

## 5. Altitude vs Detection Performance

### 5.1 Ground Footprint and GSD

The ground footprint width is derived from the thin-lens model:

```
footprint_W = SENSOR_WIDTH_MM * altitude / FOCAL_LENGTH_MM
footprint_H = footprint_W * (IMAGE_H / IMAGE_W)
GSD = footprint_W / IMAGE_W
```

| Altitude (m) | Footprint W (m) | Footprint H (m) | GSD (m/px) | Coverage Area (m^2) |
|:------------:|:---------------:|:---------------:|:----------:|:-------------------:|
| 20 | 18.4 | 13.7 | 0.0126 | 252 |
| 25 | 23.0 | 17.2 | 0.0158 | 396 |
| 30 | 27.6 | 20.6 | 0.0189 | 569 |
| 35 | 32.2 | 24.0 | 0.0221 | 773 |
| 40 | 36.8 | 27.5 | 0.0253 | 1012 |
| 50 | 46.0 | 34.3 | 0.0316 | 1578 |

### 5.2 Target Size in Image

The dummy target (1.8 m tall, 0.5 m wide, lying on ground) projects to the following
pixel sizes. Because the model input is 640 x 640 and the native frame is
1456 x 1088, the frame is resized by a factor of 640/1456 = 0.4396 horizontally and
640/1088 = 0.5882 vertically:

```
dummy_full_tall  = DUMMY_HEIGHT_M / GSD
dummy_model_tall = dummy_full_tall * (640 / IMAGE_H)
dummy_model_wide = (0.5 / GSD) * (640 / IMAGE_W)
```

| Altitude (m) | Full Frame (px) tall x wide | Model Input (px) tall x wide | Detectable? |
|:------------:|:---------------------------:|:----------------------------:|:-----------:|
| 20 | 143 x 40 | 84 x 18 | Yes -- large target |
| 25 | 114 x 32 | 67 x 14 | Yes -- comfortable |
| 30 | 95 x 26 | 56 x 12 | Yes -- solid |
| 35 | 81 x 23 | 48 x 10 | Yes -- adequate |
| 40 | 71 x 20 | 42 x 9 | Yes -- marginal width |
| 50 | 57 x 16 | 34 x 7 | Marginal -- height OK, width thin |

**Detection threshold:** YOLOv8n requires approximately 15--20 pixels in the smallest
dimension of its 640 x 640 input to reliably detect an object. The dummy's height
remains above this threshold even at 50 m (34 px). The width drops to 7 px at 50 m,
but because the model was trained on elongated figure shapes (lying-down dummy),
height is the dominant dimension for detection.

**Critical altitude:** The dummy height drops below 20 px in the model input at
approximately 85 m. Below 15 px (~100 m), detection would be unreliable. The
operational range of 20--50 m keeps the dummy at 34--84 px in the model input --
comfortably above the detection floor.

### 5.3 Multi-Pass Descent Strategy

The search begins at 50 m and descends if no detection occurs within the scan area.
Each rescan pass uses `RESCAN_ALT_FACTOR = 0.8` to reduce altitude:

```
Pass 1: 50 m   (dummy 34 px tall in model -- viable)
Pass 2: 40 m   (dummy 42 px tall -- comfortable)
Pass 3: 32 m   (dummy 52 px tall -- easy)
Floor:  15 m   (RESCAN_ALT_FLOOR_M -- dummy 100+ px tall)
```

Starting at 50 m rather than 35 m requires approximately 33% fewer scan lines and
permits 25% faster flight speed. Combined, the initial scan pass completes in roughly
60% of the time. The multi-pass strategy ensures that even if the first pass misses
a partially occluded or unusually oriented target, subsequent passes at lower altitude
provide increasingly favourable detection conditions.

### 5.4 DJI Video Validation

Analysis of DJI flight video (`DJI_0001_1456x1088_cropped_30fps.mp4`) with the
retrained v2 model confirmed reliable detection across 15--50 m altitude range. The
model consistently detected the dummy at altitudes up to 50 m with confidence above
0.4, validating the pixel-size analysis above.

---

## 6. Speed vs Frame Coverage

### 6.1 Frame Coverage Model

At 4.8 FPS, the distance the drone travels between consecutive frames is:

```
frame_gap = speed / FPS
```

The number of frames containing the target depends on how long it remains in the
camera's field of view:

```
time_in_view = footprint_H / speed
frames_in_view = time_in_view * FPS
```

The altitude-dependent speed profile from `config.py`:

```python
SPEED_AT_LOW  = 6.0   # m/s at 20 m altitude
SPEED_AT_HIGH = 10.0  # m/s at 50 m altitude
# Linear interpolation between (20 m, 6 m/s) and (50 m, 10 m/s)
```

### 6.2 Frames per Target Flyover

| Altitude (m) | Speed (m/s) | Frame Gap (m) | Footprint H (m) | Time in View (s) | Frames in View |
|:------------:|:-----------:|:-------------:|:---------------:|:----------------:|:--------------:|
| 20 | 6.0 | 1.25 | 13.7 | 2.28 | 11.0 |
| 25 | 6.7 | 1.39 | 17.2 | 2.57 | 12.3 |
| 30 | 7.3 | 1.53 | 20.6 | 2.82 | 13.5 |
| 35 | 8.0 | 1.67 | 24.0 | 3.00 | 14.4 |
| 40 | 8.7 | 1.80 | 27.5 | 3.16 | 15.2 |
| 50 | 10.0 | 2.08 | 34.3 | 3.43 | 16.5 |

The target appears in 11--17 frames at every operational altitude. Even at the fastest
configuration (10 m/s at 50 m), the target is visible for 3.4 seconds and captured in
approximately 16 frames. A single detection with confidence above 0.2 is sufficient to
trigger investigation.

### 6.3 Single-Frame Detection Threshold

For the target to appear in only 1 frame, the drone would need to traverse the entire
footprint height in one frame interval (1/4.8 = 0.208 s):

```
critical_speed = footprint_H * FPS
```

| Altitude (m) | Single-Frame Speed (m/s) | Notes |
|:------------:|:------------------------:|:------|
| 20 | 66 | Well beyond drone capability |
| 35 | 115 | Physically impossible |
| 50 | 165 | Physically impossible |

Frame coverage is never the limiting factor at any realistic drone speed.

### 6.4 Consecutive Frame Overlap

At 35 m altitude and 8 m/s, the frame gap is 1.67 m against a 24.0 m footprint
height. This gives:

```
overlap = 1 - (frame_gap / footprint_H) = 1 - (1.67 / 24.0) = 93%
```

Consecutive frames overlap by 93%, providing substantial redundancy for detection.

---

## 7. GPS Estimation Accuracy

### 7.1 Estimation Method

When a detection occurs, the target's GPS position is estimated by projecting the
pixel offset from frame centre through the camera model:

```
offset_x_m = (pixel_x - IMAGE_W/2) * GSD
offset_y_m = (pixel_y - IMAGE_H/2) * GSD
target_lat = drone_lat + offset_y_m / 111320
target_lon = drone_lon + offset_x_m / (111320 * cos(drone_lat))
```

This requires knowledge of the drone's current GPS position, altitude, and heading
(yaw) to rotate the pixel offset into the geographic frame.

### 7.2 Measured Accuracy from DJI Video Analysis

Analysis of 143 GPS estimates from DJI flight video replay:

| Metric | Value |
|--------|-------|
| CEP50 (50% circular error probable) | 2.3 m |
| Maximum error | 16.5 m |
| Error distribution | Diagonal spread along flight direction |

### 7.3 Error Sources

1. **GPS receiver latency (dominant):** The GPS receiver reports position with
   100--200 ms delay. At 5 m/s, a 200 ms lag produces a 1 m error in the flight
   direction. This creates the characteristic diagonal spread observed in the scatter
   plot -- estimates are biased along the direction of travel.

2. **Yaw uncertainty:** Heading accuracy from the magnetometer is typically +/-2--5 deg.
   At 50 m altitude, a 3 deg yaw error at the frame edge produces:
   ```
   lateral_error = footprint_W/2 * sin(3 deg) = 23 * 0.052 = 1.2 m
   ```

3. **Altitude error:** GPS altitude accuracy is typically 2x worse than horizontal
   (approximately +/-5 m). A 5 m altitude error at 35 m changes the GSD by 14%,
   producing proportional errors in the pixel-to-metre conversion.

4. **Lens distortion (corrected):** Barrel distortion shifts detections at frame edges.
   The calibrated undistortion (RMS = 0.399) corrects this to sub-pixel accuracy.

### 7.4 Accuracy Improvement Strategies

- **Vision centering:** Flying directly above the target eliminates pixel-offset errors.
  The CENTERING state in the state machine achieves this, reducing GPS estimation error
  to approximately 1 m (limited by GPS accuracy alone).
- **GPS averaging:** Collecting estimates over 10 seconds and computing the mean
  reduces random noise to below 0.5 m (law of large numbers, assuming independent
  errors from multiple frames).
- **GPS lag compensation:** Offsetting the reported position by `speed * lag_time`
  in the heading direction would remove the systematic bias, but requires calibrating
  the exact lag value.
- **Multi-pass averaging:** Estimates from opposite-direction scan lines partially
  cancel the directional bias, as the lag shifts estimates in opposite directions.

---

## 8. Confidence Threshold Tuning

### 8.1 Current Configuration

```python
CONFIDENCE_THRESHOLD = 0.2   # config.py line 98
```

### 8.2 Threshold Trade-off Analysis

| Threshold | False Positive Rate | Missed Target Risk | Best For |
|:---------:|:-------------------:|:------------------:|----------|
| 0.5+ | Very low | High (misses edge-of-frame, altitude limit) | Verification phase |
| 0.35--0.4 | Low | Medium | Bench testing, controlled conditions |
| 0.25--0.3 | Medium | Low | Video analysis default |
| **0.2** | **Higher** | **Very low** | **Search phase (current)** |

### 8.3 Cost Asymmetry Justification

The threshold is deliberately set low (0.2) because of the asymmetric cost structure:

- **False positive cost:** The drone diverts to investigate, the operator reviews the
  detection image and rejects it. Total cost: approximately 10--15 seconds.
- **Missed target cost:** The target is not detected on this scan line. The system
  must complete the remaining scan, potentially run a rescan at lower altitude,
  adding 2--5 minutes to the mission. In a real SAR scenario, a missed casualty
  could be life-threatening.

Given that a false positive costs 10 seconds and a missed detection costs minutes
(or worse), a low threshold that catches everything and relies on operator filtering
is the rational choice.

### 8.4 Smart-Detect (Optional Enhancement)

The `--smart-detect` flag enables multi-frame confirmation:

```python
DETECT_CONFIRM_FRAMES = 3   # config.py line 234
```

When enabled, the system requires 3 consecutive frames with detections before
triggering investigation. This suppresses transient false positives while the low
base threshold ensures weak but real detections accumulate across frames.

---

## 9. Lens Calibration

### 9.1 Calibration Method

Lens distortion was measured using a printed calibration target (calib.io 14x9
checkerboard, 13x8 inner corners, 28 mm square size) and OpenCV's camera calibration
pipeline (`cv2.findChessboardCornersSB` with robust fallback).

| Parameter | Value |
|-----------|-------|
| Camera | Raspberry Pi Global Shutter (IMX296) |
| Resolution | 1456 x 1088 |
| Calibration board | calib.io 14x9 (13x8 inner corners, 28 mm squares) |
| RMS reprojection error | 0.399 |
| Calibration file | `calibration_data.npz` (on Pi only, not in git) |

### 9.2 Implementation

vision.py precomputes the undistortion remap tables at initialisation:

```python
new_mtx, _ = cv2.getOptimalNewCameraMatrix(mtx, dist, (img_w, img_h), 0, (img_w, img_h))
map1, map2 = cv2.initUndistortRectifyMap(mtx, dist, None, new_mtx, (img_w, img_h), cv2.CV_16SC2)
```

Every frame is corrected via `cv2.remap(frame, map1, map2, cv2.INTER_LINEAR)` before
detection. The `alpha=0` parameter crops the result to valid pixels only (no black
borders).

### 9.3 Performance Impact

| Metric | Without Undistortion | With Undistortion | Delta |
|--------|:--------------------:|:-----------------:|:-----:|
| Inference time | 206.5 ms | 208.0 ms | +1.5 ms (+0.7%) |
| Detection confidence | 0.966 | 0.958 | -0.008 (test image artefact) |
| GPS estimation at edges | Biased outward | Corrected | Improved accuracy |

The 1.5 ms cost is negligible (0.7% of total frame time). The primary benefit is
improved GPS estimation accuracy for detections near frame edges, where barrel
distortion would otherwise shift the apparent position by several pixels.

---

## 10. Summary of Limiting Factors

| Factor | Limiting? | Reason |
|--------|:---------:|--------|
| Motion blur | **No** | Global shutter + short exposure = sub-pixel blur at all speeds |
| Target pixel size (altitude) | **Marginal at 50 m** | Dummy height 34 px in model input, above 20 px floor |
| Target pixel size (below 40 m) | **No** | Dummy height > 42 px in model input |
| Inference FPS | **No** | 4.8 FPS gives 11--17 frames per target flyover |
| Frame gap between frames | **No** | 93% frame overlap at 35 m altitude, 8 m/s |
| Drone speed | **No** | Max 10 m/s is far below ~66 m/s single-frame threshold |
| GPS estimation | **Yes** | CEP50 = 2.3 m, max 16.5 m, dominated by GPS receiver lag |

**The real operational limit is altitude, not speed or blur.** Above approximately 85 m,
the dummy height drops below 20 px in the model input and detection becomes unreliable.
The multi-pass descent strategy (50 m -> 40 m -> 32 m) provides a robust safety net
within the operational envelope.

The speed profile (`SPEED_AT_LOW = 6 m/s` at 20 m, `SPEED_AT_HIGH = 10 m/s` at 50 m)
is conservative relative to the detection envelope. Speed could be increased to 15+ m/s
without impacting detection, though this would degrade GPS estimation accuracy due to
the 100--200 ms GPS timing lag.

---

## 11. Future Vision Improvements

### 11.1 Inference Speed

| Improvement | Expected Gain | Effort | Status |
|-------------|:------------:|:------:|:------:|
| FP16 XNNPACK | ~2x (10 FPS) | Low (1--2 hrs) | Pi 5 has native FP16 (ARMv8.2-A) |
| Threaded capture + inference | +20--30% | Low (1 hr) | Producer-consumer, GIL not an issue |
| NCNN backend | ~3x (15 FPS) | Medium (2--3 hrs) | Export available in `cv_models/sar_v2_1088/ncnn/` |
| Overclock to 2.8 GHz | +15--20% | Low (15 min) | 3 lines in `/boot/firmware/config.txt` |
| Lower input resolution (416x416) | ~2x (8 FPS) | Low (30 min) | Accuracy impact on small targets |
| INT8 quantisation | ~30% | Medium (needs calibration images) | Needs 300+ representative frames |
| YOLO26n + NCNN | ~3x (15 FPS) + better accuracy | High (retraining) | +7% mAP over YOLOv8n |
| Hailo-8L accelerator | 80+ FPS | Hardware ($70) | Dedicated AI HAT for Pi 5 |

**Recommended priority:** FP16 XNNPACK first (highest impact, lowest effort), then
threaded pipeline, then NCNN. Combined, these three could reach 10--15 FPS -- a 2--3x
improvement over the current 4.8 FPS baseline.

### 11.2 Detection Quality

| Improvement | Impact | Effort |
|-------------|--------|--------|
| More real labelled frames (target: 50--100) | Reduces overfitting to synthetic data | Medium |
| Multiple dummy poses/clothing | Improves generalisation | Medium |
| Partially occluded training samples | Handles tall grass, shadows | Medium |
| Proper train/val split (80/20) | Gives meaningful validation metrics | Low |
| Multi-class detection (dummy + person + cone) | Broader target coverage | High (retraining + relabelling) |
| Tiled inference (640 px tiles with overlap) | Better detection of small targets at high altitude | Medium (implemented in video tools) |

### 11.3 GPS Accuracy

| Improvement | Impact | Effort |
|-------------|--------|--------|
| GPS lag compensation (speed * lag in heading direction) | Removes directional bias | Low |
| Kalman filter on target position estimates | Smooths noisy estimates | Medium (implemented in simulator) |
| RTK GPS module | Sub-centimetre positioning | High (hardware + cost) |
| Visual odometry (optical flow between frames) | Supplements GPS during fast manoeuvres | High |

---

## 12. Configuration Reference

All vision-related parameters from `config.py`:

```python
# Camera hardware
SENSOR_WIDTH_MM    = 5.02       # IMX296 sensor physical width
FOCAL_LENGTH_MM    = 5.46       # Calibrated: 92 cm visible at 1 m height
IMAGE_W            = 1456       # IMX296 native resolution (horizontal)
IMAGE_H            = 1088       # IMX296 native resolution (vertical)
CAMERA_FLIP_180    = True       # Camera mounted inverted on drone

# Detection
CONFIDENCE_THRESHOLD = 0.2     # Low threshold, operator filters FPs

# Speed profile (altitude-dependent)
SPEED_ALT_LOW      = 20.0      # Below this altitude: use SPEED_AT_LOW
SPEED_ALT_HIGH     = 50.0      # Above this altitude: use SPEED_AT_HIGH
SPEED_AT_LOW       = 6.0       # m/s at low altitude
SPEED_AT_HIGH      = 10.0      # m/s at high altitude
SEARCH_SPEED_MPS   = 10.0      # Default search speed
TRANSIT_SPEED_MPS  = 15.0      # Transit between waypoints

# Search strategy
TARGET_ALT         = 35.0      # Initial search altitude (m)
VERIFY_ALT         = 15.0      # Descent altitude for verification (m)
MAX_RESCAN_PASSES  = 3         # Number of altitude-drop rescans
RESCAN_ALT_FACTOR  = 0.8       # Altitude multiplier per rescan pass
RESCAN_ALT_FLOOR_M = 15.0      # Minimum rescan altitude

# Target specifications
DUMMY_HEIGHT_M     = 1.8       # Target height for pixel-size calculations
TARGET_REAL_RADIUS_M = 0.15    # 15 cm detection radius
```

---

## 13. Key Formulas

For reference in the report, the core optical and detection formulas:

**Ground sample distance:**
```
GSD = (SENSOR_WIDTH_MM * altitude) / (FOCAL_LENGTH_MM * IMAGE_W)
```

**Ground footprint:**
```
footprint_W = SENSOR_WIDTH_MM * altitude / FOCAL_LENGTH_MM
footprint_H = footprint_W * (IMAGE_H / IMAGE_W)
```

**Target size in model input:**
```
target_model_px = (target_real_m / GSD) * (640 / IMAGE_dim)
```

**Motion blur:**
```
blur_pixels = (speed * exposure_time) / GSD
```

**Frames per flyover:**
```
frames_in_view = (footprint_H / speed) * FPS
```

**Consecutive frame overlap:**
```
overlap = 1 - (speed / (FPS * footprint_H))
```

**GPS estimation from pixel offset:**
```
offset_m = (pixel - IMAGE/2) * GSD
target_lat = drone_lat + offset_y_m / 111320
target_lon = drone_lon + offset_x_m / (111320 * cos(lat))
```
