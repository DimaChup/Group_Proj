# Pre-Flight Calibration & Testing Checklist

Print this. Follow top to bottom. Tick boxes as you go.

---

## 1. Hardware Health (5 min)

```bash
# Camera works?
python tests/laptop/test_camera.py

# AI model loads + detects?
python tests/laptop/test_cv.py --camera

# Cube heartbeat + GPS + battery?
python tests/laptop/test_cube.py

# Full system check (camera + Cube + AI)
python preflight.py
```

- [ ] Camera returns frames (no black/mangled images)
- [ ] AI model loads, detects dummy in frame
- [ ] Cube heartbeat received
- [ ] Battery voltage > 14.8V (4S) or > 22.2V (6S)
- [ ] GPS fix type >= 3, satellites >= 10, HDOP < 1.5

```bash
# GPS health (wait for convergence)
python tests/hardware/gps_health.py
```

---

## 2. FOV / Focal Length Calibration (10 min)

This is the **most important calibration** -- directly controls pixel-to-GPS accuracy.

### Current values
```
SENSOR_WIDTH_MM  = 5.02   (IMX296 datasheet, fixed)
FOCAL_LENGTH_MM  = 5.46   (calibrated 2026-03-11)
IMAGE_W          = 1456   (IMX296 native)
IMAGE_H          = 1088   (IMX296 native)
```

### Procedure
1. Place camera pointing **straight down** at EXACTLY 1m above a ruler/tape
2. Measure visible width in the frame (left edge to right edge)
3. Expected: ~92cm (based on current FOCAL_LENGTH_MM = 5.46)

```bash
# Interactive (with display)
python tests/calibration/fov_calibrate.py

# Headless (Pi over SSH)
python tests/calibration/fov_calibrate.py --headless

# Quick single measurement
python tests/calibration/fov_test_simple.py
```

### If visible width differs from 92cm
```
FOCAL_LENGTH_MM = (SENSOR_WIDTH_MM * height_mm) / visible_width_mm
                = (5.02 * 1000) / visible_width_mm
```

Example: see 85cm -> FOCAL_LENGTH_MM = 5020 / 850 = 5.91

- [ ] Measured visible width at 1m: ______ cm
- [ ] Computed FOCAL_LENGTH_MM: ______
- [ ] Updated config.py (if changed)
- [ ] Repeat at 50cm and 150cm -- values should agree within 0.3mm

### Impact of error

| Altitude | 10% focal length error = position error |
|----------|----------------------------------------|
| 10m      | 0.9m                                   |
| 20m      | 1.8m                                   |
| 35m      | 3.2m                                   |

---

## 3. Altitude Error Measurement (5 min)

ArduCopter reports altitude from **barometer** (relative to arm point). Baro drifts with temperature and pressure.

### Procedure
1. Arm the drone on flat ground (altitude reads 0m)
2. Wait 5 minutes, note altitude reading
3. If drift > 0.5m, recalibrate baro in Mission Planner (Initial Setup > Mandatory > Accel Calibration)

```bash
# Live altitude + GPS display
python tests/hardware/gps_test.py
```

- [ ] Altitude drift after 5 min on ground: ______ m
- [ ] Drift < 0.5m? (if not, recalibrate baro)

### Impact
```
At 35m altitude:
  1m baro error = 2.9% GSD error = ~0.9m ground position error at frame edge
  2m baro error = 5.7% GSD error = ~1.8m ground position error at frame edge
```

---

## 4. GPS Error Measurement (5 min)

GPS position has ~2-3m CEP (circular error probable). This is the **floor** of target accuracy.

### Procedure
1. Place drone at a **known** GPS position (e.g., Take-Off Location: 51.423406, -2.671446)
2. Record reported GPS for 60 seconds
3. Check spread

```bash
# Automated GPS drift measurement (60s, CSV output)
python tests/day_1_experiments/gps_drift.py
```

- [ ] CEP50 (50% of readings within this radius): ______ m
- [ ] CEP95 (95% of readings within this radius): ______ m
- [ ] Max deviation: ______ m
- [ ] Satellite count: ______
- [ ] CEP50 < 3m? (expected with Here 3+)

### Impact
GPS error adds **directly** to target estimation error. If CEP50 = 2m, your target estimate can never be better than 2m even with perfect FOV calibration.

---

## 5. Pixel-to-GPS Pipeline Verification (10 min)

The full chain: **detection pixel -> GSD -> offset metres -> target GPS**

### The math at current config
```
GSD = (SENSOR_WIDTH_MM * altitude) / (FOCAL_LENGTH_MM * IMAGE_W)
    = (5.02 * 35) / (5.46 * 1456)
    = 0.0221 m/pixel

Full frame width on ground = 1456 * 0.0221 = 32.2m
Full frame height on ground = 1088 * 0.0221 = 24.0m
```

### Bench verification (no flight needed)
```bash
# Terminal version (works over SSH)
python tests/calibration/gps_estimate_calibrate.py

# GUI version (needs display)
python tests/calibration/gps_calibrate_gui.py

# Without Cube (manual altitude input)
python tests/calibration/gps_estimate_calibrate.py --no-mavlink
```

### Procedure
1. Hold camera pointing down at known height (e.g., 1.5m)
2. Place dummy at known horizontal offset from directly below camera
3. Enter height and offset when prompted
4. Script compares estimated vs actual distance
5. Repeat 3-4 times at different offsets
6. Ctrl+C for weighted average summary

- [ ] Estimated distance vs actual: error < 10%
- [ ] If error > 10%, script outputs corrected FOCAL_LENGTH_MM
- [ ] Updated config.py (if needed)

### In-flight verification (during passive flight)
```bash
# Full end-to-end: hover over target, compare CV estimate vs actual GPS
python tests/calibration/gps_ground_truth.py
```

---

## 6. Lens Undistortion (optional, 5 min)

IMX296 has minimal distortion (RMS 0.399). **Skip unless edge accuracy matters.**

```bash
# Calibrate (needs checkerboard, calib.io 14x9 board)
python tests/calibration/lens_calibrate.py

# Headless
python tests/calibration/lens_calibrate.py --headless

# Verify existing calibration
python tests/calibration/lens_calibrate.py --load
```

- [ ] calibration_data.npz exists and is not empty (check file size > 1KB)
- [ ] If corrupt/empty, DELETE it: `rm calibration_data.npz`
- [ ] UNDISTORT_ENABLED in config.py matches npz state (True if valid npz, False if missing)
- [ ] Cost: ~1.5ms/frame (negligible)

---

## 7. Camera Color Check (2 min)

IMX296 outputs **BGR** despite picamera2 labeling it RGB888.

- [ ] Stream looks natural (skin tones correct, sky is blue not orange)
- [ ] Do **NOT** add `cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)` -- it is already BGR

```bash
# Quick visual check
python tests/diagnostics/camera_stream.py
# Open http://PI_IP:8090 in browser
```

---

## 8. Detection Confidence Threshold (5 min)

Current: `CONFIDENCE_THRESHOLD = 0.2` in config.py

```bash
# Run passive watch, check detection quality
python passive_watch.py

# With specific model
python passive_watch.py --model cv_models/sar_v2_1088/best.tflite
```

- [ ] False positive rate acceptable at current threshold
- [ ] Real targets detected at expected range
- [ ] For flight day: start at 0.3, lower to 0.2 if missing targets

---

## 9. Inference Speed Check (2 min)

```bash
# Benchmark (50 runs, timing report)
python tests/hardware/benchmark.py

# Comprehensive benchmark (all models, system info)
python tests/hardware/benchmark_full.py
```

- [ ] Inference time: ______ ms (target: < 250ms for TFLite, < 100ms for NCNN)
- [ ] FPS: ______ (target: > 4 FPS)

---

## 10. End-to-End Dry Run (2 min)

```bash
python main.py --dry-run
python main.py --dry-run --alt 20    # check at different altitude
```

- [ ] KML zones loaded (search area, flight area, SSSI)
- [ ] Lawnmower waypoints generated (check count and spacing)
- [ ] Geofence active (no waypoints inside SSSI)
- [ ] `dry_run_pattern.jpg` saved and looks correct
- [ ] No import errors or config warnings

---

## Quick Reference: Error Budget

| Source | Typical Error | Controllable? | How to Reduce |
|--------|--------------|---------------|---------------|
| GPS position | 2-3m CEP | No | Wait for more sats, use RTK |
| Altitude (baro) | 0.5-1m | Partially | Recalibrate before flight |
| FOV / focal length | 0-5% if calibrated | Yes | Bench calibration at 1m |
| Lens distortion | < 0.5m at edges | Optional | Checkerboard calibration |
| Camera tilt | 0-2m if tilted | Yes | Mount camera straight down |
| GPS timing lag | ~1m at 5m/s | Known | Average multiple passes |
| **TOTAL (RSS)** | **~3-4m CEP** | | **~2.3m CEP measured** |

### GSD Table (metres per pixel at each altitude)

| Altitude | GSD (m/px) | Frame width (m) | Frame height (m) |
|----------|-----------|-----------------|-------------------|
| 10m | 0.0063 | 9.2 | 6.9 |
| 15m | 0.0095 | 13.8 | 10.3 |
| 20m | 0.0126 | 18.4 | 13.7 |
| 25m | 0.0158 | 23.0 | 17.2 |
| 30m | 0.0189 | 27.6 | 20.6 |
| 35m | 0.0221 | 32.2 | 24.0 |
| 40m | 0.0252 | 36.7 | 27.4 |
| 50m | 0.0315 | 45.9 | 34.3 |

Formula: `GSD = (5.02 * alt) / (5.46 * 1456)`

---

## Config Values to Update After Calibration

```python
# config.py -- fill in measured values
SENSOR_WIDTH_MM  = 5.02    # IMX296 datasheet (don't change)
FOCAL_LENGTH_MM  = ____    # From step 2 (bench FOV) or step 5 (GPS estimate)
IMAGE_W          = 1456    # IMX296 native (don't change)
IMAGE_H          = 1088    # IMX296 native (don't change)
TARGET_ALT       = ____    # Search altitude, lower if detection poor from 35m
CONFIDENCE_THRESHOLD = ____ # From step 8
UNDISTORT_ENABLED = ____   # True if valid calibration_data.npz, False otherwise
```
