# Vision-to-GPS Estimation Pipeline

How the SAR drone converts a camera frame into a GPS coordinate for the dummy.

---

## 1. Pipeline Overview

```
Camera frame (1456x1088 BGR)
    |
    v
[Lens Undistortion] ── calibration_data.npz (optional, ~1.5ms)
    |
    v
[AI Detection] ── YOLOv8n TFLite (640x640 input, ~206ms on Pi 5)
    |
    v
(found, cx_px, cy_px, confidence)     ← pixel coords in original frame
    |
    v
[Normalise] ── norm_x = cx_px / frame_w,  norm_y = cy_px / frame_h
    |
    v
[Pixel-to-Ground Projection] ── uses focal length, altitude, yaw
    |
    v
(est_lat, est_lon)   ← single-frame GPS estimate
    |
    v
[DummyEstimator] ── inverse-variance weighted accumulation
    |
    v
[SmartEstimator] ── tightest-cluster lock (optional --smart-estimate)
    |
    v
FINAL COORDINATE  ← median of locked cluster
```

Each step is explained below.

---

## 2. Lens Undistortion

**What it does:** Removes barrel/pincushion distortion from the IMX296 global shutter camera so that straight lines in the real world appear straight in the image. Without it, objects near frame edges are slightly displaced, which shifts GPS estimates by a metre or two.

**How it works:**
- At startup, `VisionSystem.__init__()` looks for `calibration_data.npz` in the project root.
- If found, it loads `camera_matrix` and `dist_coeffs`, precomputes OpenCV remap matrices with `cv2.initUndistortRectifyMap()`.
- Every frame passes through `cv2.remap()` before AI inference (~1.5ms cost, negligible).
- All downstream code sees a clean, undistorted image.

**Config toggle:**
```python
# config.py
UNDISTORT_ENABLED = False  # Currently OFF — no valid calibration_data.npz on Pi
```

**How to recalibrate (checkerboard):**
1. Print a checkerboard pattern (e.g., calib.io 14x9 board, 13x8 inner corners, 28mm squares).
2. Hold it in front of the Pi camera at various angles and distances (10-20 images).
3. Run `tests/calibration/lens_calibrate.py` on the Pi.
4. It saves `calibration_data.npz` with camera matrix, distortion coefficients, and RMS error.
5. Set `UNDISTORT_ENABLED = True` in config.py.

**When it matters:** Mostly for detections near frame edges. The IMX296 has low distortion, so the effect is small (our bench test showed RMS 0.399). If you only care about detections near frame centre, you can leave it off.

---

## 3. FOV Calibration

Two values in `config.py` control the camera's field-of-view model:

```python
SENSOR_WIDTH_MM = 5.02    # IMX296 physical sensor width
FOCAL_LENGTH_MM = 5.46    # Calibrated 2026-03-11 (92cm visible at 1m height)
IMAGE_W = 1456            # Pi camera native resolution
IMAGE_H = 1088
```

**Derived quantities** (computed at startup in `passive_watch.py`):

| Quantity | Formula | Value |
|----------|---------|-------|
| HFOV (degrees) | `2 * atan(SENSOR_WIDTH_MM / (2 * FOCAL_LENGTH_MM))` | ~49.3 deg |
| VFOV (degrees) | `HFOV * IMAGE_H / IMAGE_W` | ~36.8 deg |
| Focal length (pixels) | `FOCAL_LENGTH_MM * IMAGE_W / SENSOR_WIDTH_MM` | ~1585 px |
| Ground width at altitude h | `h * SENSOR_WIDTH_MM / FOCAL_LENGTH_MM` | 0.92m per 1m alt |

**Why this matters for GPS accuracy:**

The focal length in pixels (`f_px`) is the single most important calibration value. Every GPS estimate uses it to convert "how many pixels from frame centre" into "how many metres on the ground." If `f_px` is wrong by 10%, every GPS estimate is wrong by 10% of its lateral offset.

**How to recalibrate:**
1. Place the camera at a known height (e.g., exactly 1.0m) looking straight down.
2. Measure how many centimetres of ground are visible across the frame width.
3. `FOCAL_LENGTH_MM = SENSOR_WIDTH_MM * height_m / visible_width_m`
4. Example: at 1m height, 92cm visible width: `5.02 * 1.0 / 0.92 = 5.46mm`

Alternatively, use `tools/fov_calibrate_video.py` with flight video: click a known-size object (dummy = 1.8m tall) at multiple altitudes to fit focal length.

---

## 4. GPS Estimation Math

This is the core projection from pixel coordinates to GPS. Found in `DummyEstimator.add_observation()` (passive_watch.py, line ~1028).

### Step 1: Pixel offset from frame centre

```python
dx_px = (norm_x - 0.5) * IMAGE_W    # positive = right of centre
dy_px = (norm_y - 0.5) * IMAGE_H    # positive = below centre
```

Where `norm_x = detection_cx / frame_width` (0 to 1).

### Step 2: Convert pixels to metres on the ground

```python
dx_m = dx_px * altitude / f_px
dy_m = dy_px * altitude / f_px
```

This is the pinhole camera model: ground distance = pixel distance x altitude / focal length (in pixels). Higher altitude = same pixel offset covers more ground = larger GPS offset.

### Step 3: Map camera axes to world axes

The camera points straight down. Top of image = drone forward direction.

```python
forward_m = -dy_m    # negative dy (above centre) = forward = North at yaw=0
right_m   =  dx_m    # positive dx (right of centre) = East at yaw=0
```

### Step 4: Rotate by drone yaw

```python
yaw_rad = radians(yaw_deg)
north_m = forward_m * cos(yaw_rad) - right_m * sin(yaw_rad)
east_m  = forward_m * sin(yaw_rad) + right_m * cos(yaw_rad)
```

Yaw = 0 means the drone faces North. Yaw = 90 means the drone faces East (so "forward" becomes East, "right" becomes South).

### Step 5: Convert metres to GPS offset

```python
lat_m_per_deg = 111320                                    # ~constant
lon_m_per_deg = 111320 * cos(radians(drone_lat))          # shrinks toward poles

est_lat = drone_lat + north_m / lat_m_per_deg
est_lon = drone_lon + east_m / lon_m_per_deg
```

### Step 6: Weighting

Each observation gets a weight for the running weighted average:

```python
weight = 1.0 / (altitude^2)
```

This means a detection at 10m altitude has **9x the weight** of one at 30m (lower altitude = larger target in frame = less projection error).

### Step 7: Centre-bonus

Detections near the centre of the frame have less lens distortion and less projection error (the pinhole model is most accurate directly below the camera).

```python
dist_from_centre = sqrt(dx_px^2 + dy_px^2)
max_dist = sqrt((IMAGE_W/2)^2 + (IMAGE_H/2)^2)    # corner distance

# If detection is within 30% of frame centre, boost weight up to 5x
centre_factor = 1.0 + 4.0 * max(0, 1.0 - dist_from_centre / (max_dist * 0.3))
weight *= centre_factor
```

A detection exactly at frame centre gets 5x weight. A detection at 30%+ of the diagonal gets 1x. This strongly favours flyover detections where the dummy is directly below the drone.

### Cumulative estimate

`DummyEstimator.get_estimate()` returns:
```python
(weighted_lat / total_weight,  weighted_lon / total_weight,  n_observations)
```

This is the inverse-variance weighted mean across all observations so far.

---

## 5. SmartEstimator (Tightest Cluster Lock)

The DummyEstimator gives a running weighted mean, but it can be pulled off by outliers (false positives, GPS lag errors). The SmartEstimator finds the tightest cluster of consistent estimates and locks onto it.

### How it works

1. **Accumulation:** Every detection that passes the confidence and class filters adds `(est_lat, est_lon, pixel_dist, frame)` to an internal list.

2. **Cluster search (after min_samples detections):** For every new detection, it runs `_find_tightest(min_samples)`:
   - Compute all pairwise GPS distances between estimates.
   - Start with the two closest estimates.
   - Greedily add the point that minimizes the maximum distance within the cluster.
   - Continue until the cluster has `min_samples` points.
   - Report the "spread" = max pairwise distance in the cluster.

3. **Lock condition:** If `spread < max_spread` (default 1.0m), the estimator **locks**. No more estimates are accepted. The locked cluster is frozen.

4. **Final coordinate:** `get_median()` returns the **median** latitude and longitude of the locked cluster (robust to outliers within the cluster).

5. **CEP50:** `get_cep50()` computes the median distance of cluster points from the median centre -- a measure of precision.

### Parameters

| Flag | Default | Effect |
|------|---------|--------|
| `--smart-min` | 5 | Minimum detections in the tightest cluster before it can lock |
| `--smart-radius` | 1.0 | Maximum spread (metres) for the cluster to be considered tight enough |

**Tuning guidance:**
- **Decrease `--smart-radius`** (e.g., 0.5m) for higher precision, but requires more consistent detections. May never lock if GPS noise is high.
- **Increase `--smart-radius`** (e.g., 2.0m) to lock sooner, at the cost of a less precise coordinate.
- **Increase `--smart-min`** (e.g., 10) for more confidence, but takes more flyovers to lock.
- **Decrease `--smart-min`** (e.g., 3) to lock faster, but more susceptible to correlated errors from a single pass.

### What happens on lock

- A result image is generated: the detection frame + a satellite map crop with a magenta star at the estimated coordinate.
- Saved to `<save-dir>/smart_detections/0001_<lat>_<lon>.png`.
- A "TARGET FOUND" banner appears on the live stream for 5 seconds.
- The coordinate is printed to the terminal.

---

## 6. Running passive_watch.py

### Basic usage (on Pi via SSH)

```bash
cd ~/dima/Group_Proj && source pienv/bin/activate

# Minimal — stream + save all detections
DISPLAY= python field_tools/passive_watch.py

# With SMART estimation (recommended for best coordinate)
DISPLAY= python field_tools/passive_watch.py --smart-estimate --smart-min 5 --smart-radius 1.0

# Lower confidence to catch more detections (operator reviews later)
DISPLAY= python field_tools/passive_watch.py --smart-estimate --conf 0.2

# Only detect persons (using COCO human.tflite model)
DISPLAY= python field_tools/passive_watch.py --model models/human.tflite --class-filter person
```

### All flags explained

| Flag | Default | What it does |
|------|---------|--------------|
| `--port 8090` | 8090 | HTTP server port for the browser dashboard |
| `--conf 0.4` | 0.4 | Minimum YOLO confidence threshold. Lower = more detections but more false positives |
| `--fps 5` | 5 | Max inference FPS throttle (largely irrelevant with threaded inference) |
| `--save-dir detections` | `detections/` | Directory for saved snapshots, JSON sidecars, and CSV log |
| `--no-save` | off | Disable all file saving (stream only) |
| `--no-mavlink` | off | Skip mavproxy connection. No GPS overlay or estimation. Use for laptop testing |
| `--model best.tflite` | `best.tflite` | Path to the TFLite model. Use `models/human.tflite` for COCO person detection |
| `--simple-names` | off | Simpler filenames: `0001_<lat>_<lon>.jpg` instead of `det_0001_<conf>_<lat>_<lon>.jpg`. No JSON sidecars |
| `--class-filter person` | all | Only process detections of this class. Comma-separated for multiple (e.g., `person,dog`). `other` matches non-standard classes |
| `--smart-estimate` | off | Enable SmartEstimator clustering. Saves a result image when the cluster locks |
| `--smart-min 5` | 5 | Minimum samples for SMART cluster lock |
| `--smart-radius 1.0` | 1.0 | Maximum spread (metres) for SMART lock |
| `--smart-dir <path>` | `<save-dir>/smart_detections/` | Custom output directory for SMART result images |
| `--fake` | off | Replay DJI video instead of live camera. Good for testing the pipeline on laptop |
| `--fake-video <path>` | `RealVideo/DJI_0001_1456x1088_cropped_30fps.mp4` | Video file for fake mode |
| `--fake-srt <path>` | `RealVideo/DJI_20260311172332_0001_V.SRT` | SRT telemetry file for fake mode |
| `--no-stream` | off | Disable the HTTP server entirely |

### Browser dashboard

Open `http://<PI_IP>:8090/` in a browser for:
- Live MJPEG video stream with detection overlay
- Latest and best detection thumbnails
- GPS bullseye scatter plot
- Satellite map with estimated position
- SMART grid (thumbnails of locked cluster frames)
- Model selector, confidence slider, class filter dropdown

### Prerequisites

On the Pi, mavproxy must be running for GPS telemetry:
```bash
sudo /opt/mavlink/mavlink-venv/bin/mavproxy.py \
  --master=/dev/ttyAMA0 --baudrate=921600 --streamrate=10 \
  --out=udpout:127.0.0.1:14550 --out=tcpin:0.0.0.0:5762
```

passive_watch.py connects to `udpin:0.0.0.0:14550` (read-only). It sends **zero commands** to the drone.

---

## 7. Output Files

### Per-detection output (normal mode)

For each detection above the confidence threshold:

| File | Format | Contents |
|------|--------|----------|
| `detections/det_0001_0.87_51.4234567_-2.6714567.jpg` | JPEG (85%) | Camera frame with detection overlay, GPS stamp, FOV info |
| `detections/det_0001_0.87_51.4234567_-2.6714567.json` | JSON | Structured metadata: timestamp, detection pixel coords, drone GPS/alt/yaw/sats, FOV params, cumulative estimate |
| `detections/detection_log.csv` | CSV (appended) | One row per detection: timestamp, frame, confidence, pixel x/y, drone GPS, altitude, sats, yaw, mode, estimate lat/lon, observation count, filename |

### SMART result output (--smart-estimate mode)

| File | Format | Contents |
|------|--------|----------|
| `detections/smart_detections/0001_<lat>_<lon>.png` | PNG (lossless) | Composite image: detection frame with "SMART COORDINATE" banner, GPS coordinate, spread/CEP50 stats, satellite map with magenta star at estimated position |

### Survey result output (after 100 detections)

| File | Format | Contents |
|------|--------|----------|
| `detections/RESULT_SURVEY_<lat>_<lon>.jpg` | JPEG (95%) | Composite with "SURVEY COMPLETE" banner and best-method coordinate |

The survey analysis (`compute_survey_analysis()`) computes the coordinate via multiple methods (simple mean, inverse-variance weighted mean, median, trimmed mean) and picks the one with the lowest CEP50.

---

## 8. Accuracy Factors

### Altitude (largest effect)

- **Lower is better.** At 10m altitude, 1 pixel = ~0.007m on the ground. At 30m, 1 pixel = ~0.019m.
- Weight scales as 1/altitude^2, so 10m observations dominate 30m ones.
- Below ~5m the dummy fills most of the frame and detection is reliable. Above ~35m it becomes a few pixels and may be missed.
- **Practical sweet spot:** 15-25m for reliable detection with reasonable GPS accuracy.

### Drone speed and GPS lag

- The GPS receiver has 100-200ms latency. At 5m/s, that's 0.5-1.0m position error along the flight direction.
- Faster flight = more GPS lag error. The lag causes a systematic bias (all estimates shifted in the direction of travel).
- **Mitigation:** Multiple passes from different directions average out the directional bias. The SMART estimator and weighted mean help, but cannot eliminate single-direction lag.
- **Best practice:** Fly slowly over the target area (5m/s or less) and make multiple passes from different headings.

### Detection position within frame

- **Centre = best.** The projection math is most accurate directly below the drone (zero off-axis angle).
- The centre-bonus gives 5x weight to centre detections, so the estimator self-corrects.
- Edge detections have more lens distortion (if undistortion is off) and more projection error from the flat-earth approximation at steep angles.

### Yaw accuracy

- The yaw angle rotates the pixel offset into North/East. A 5-degree yaw error at 20m lateral offset produces ~1.7m GPS error.
- Yaw comes from the Cube's magnetometer (ATTITUDE message). It is usually accurate to 1-3 degrees in flight.
- **If the drone is stationary on the ground**, yaw can drift significantly. Only trust yaw estimates from in-flight data.

### Lens distortion

- Uncorrected barrel distortion shifts edge detections outward, inflating the estimated offset.
- With the IMX296 (low distortion), the effect is small (~1-2% at frame edges).
- Enable undistortion (`UNDISTORT_ENABLED = True` + valid `calibration_data.npz`) for best results.

### Detection confidence

- Higher confidence detections tend to have more accurate bounding box centres.
- Low confidence detections may have shifted bounding boxes (partially occluded, edge of frame, motion blur).
- The pipeline does not weight by confidence (only by altitude and centrality). Consider raising `--conf` if you are getting many false positives that corrupt the estimate.

### Number of observations

- More detections = better estimate (averaging reduces random noise).
- The DummyEstimator weighted mean converges after ~20-30 observations.
- The SmartEstimator needs at least `--smart-min` observations that agree within `--smart-radius` metres.
- A single flyover typically yields 5-15 detections. Two passes from opposite directions are much better than one.

### Summary: getting the best coordinate

| Factor | What to do |
|--------|-----------|
| Altitude | Fly at 15-25m. Lower = better accuracy per detection |
| Speed | 5m/s or slower over the search area |
| Heading | Multiple passes from different directions (averages out GPS lag) |
| Centrality | Let the drone fly directly over the target if possible |
| Model | Use `cv_models/sar_v2_1088/best.tflite` (retrained, mAP50=0.995) |
| Confidence | Start with `--conf 0.2`, raise if too many false positives |
| SMART | Use `--smart-estimate --smart-min 5 --smart-radius 1.0` for a locked coordinate |
| Undistortion | Enable if `calibration_data.npz` exists and is valid |
| FOV calibration | Verify `FOCAL_LENGTH_MM` with a known-height measurement |
