# Launch Configurations

All ways to launch `main.py` and `passive_watch.py` with different models and settings.

---

## 1. Available Models

| # | Name | Path | Size | Class | Training Data | Format |
|---|------|------|------|-------|---------------|--------|
| 1 | Original custom | `cv_models/custom_yolov8n.tflite` | 3.2 MB | dummy (class 0) | dataset_v1 (200 syn, 640) | TFLite f32 |
| 2 | SAR v2 TFLite | `cv_models/sar_v2_1088/best.tflite` | 11.7 MB | dummy (class 0) | dataset_v2 (366, 1088) | TFLite f32 |
| 3 | SAR v2 NCNN | `cv_models/sar_v2_1088/ncnn/` | ~6 MB | dummy (class 0) | dataset_v2 (366, 1088) | NCNN |
| 4 | COCO person | `cv_models/human.tflite` | 12.2 MB | person (class 0 of 80) | COCO dataset | TFLite f32 |
| 5 | Model 5 f32 | `cv_models/model_5/best_float32.tflite` | 11.8 MB | dummy (class 0) | dataset_v3 (700, 640) | TFLite f32 |
| 6 | Model 5 f16 | `cv_models/model_5/best_float16.tflite` | 6.0 MB | dummy (class 0) | dataset_v3 (700, 640) | TFLite f16 |
| 7 | Model 5 NCNN | `cv_models/model_5/ncnn/` | ~6 MB | dummy (class 0) | dataset_v3 (700, 640) | NCNN |

**Notes:**
- The COCO model detects "person" plus 79 other classes. All custom models detect "dummy" only.
- All TFLite models share the same input shape `[1,640,640,3]` and output shape `[1,5,8400]` -- they are drop-in replacements for each other.
- `best.tflite` in the project root is the **active model** used by all scripts when no `--model` flag is given. Swap it with any of the above using `cp`.
- NCNN models are loaded via the `ncnn` Python package and run ~4.5x faster than TFLite on Pi 5 (~72 ms vs ~327 ms).

---

## 2. main.py CLI Flags (Complete Reference)

| Flag | Argument | Default | Description |
|------|----------|---------|-------------|
| `--dry-run` | none | off | No arming, no flying, no GPS. Print waypoints and save pattern image. |
| `--headless` | none | auto on Pi | No cv2 windows. Auto-enabled when `$DISPLAY` is empty. |
| `--model` | `<path>` | `best.tflite` | Path to TFLite model file. |
| `--alt` | `<meters>` | 35 | Search altitude in metres. |
| `--speed` | `<factor>` | 1 | SITL speedup factor. Only affects SIMULATION mode. |
| `--conf` | `<0-1>` | 0.2 | Minimum YOLO confidence threshold. |
| `--transit` | `<file>` | `flight_plans/transit.json` | Transit waypoints JSON file. |
| `--beacon-delay` | `<seconds>` | 0 (off) | Auto-trigger PLB redirect after N seconds of search. |
| `--smart-detect` | none | off | Require consecutive confirmed frames before investigating. |
| `--center-verify` | none | off | GPS-average the target position after centering, before VERIFY. |
| `--spiral` | none | off | Use perimeter spiral pattern instead of lawnmower. |
| `--lock-yaw` | none | off | Maintain search heading throughout sweep (no yaw changes). |
| `--no-nfz` | none | off | Disable SSSI geofence. |
| `--nfz-total-speed` | none | off | Use total speed NFZ mode instead of directional (default). |
| `--no-stream` | none | off | Disable MJPEG stream server (port 8090). |

**Environment variables:**
- `DRONE_MODE=SIMULATION` or `DRONE_MODE=REAL` -- sets operating mode (default: SIMULATION).
- `DRONE_CONN=tcp:IP:PORT` -- override auto-detected connection string.
- `DRONE_BAUD=921600` -- override baud rate (default 921600).

---

## 3. main.py Launch Configurations

### Dry-run (no hardware needed)

Validates the search pattern and state machine without any GPS, Cube, or camera.

```bash
python main.py --dry-run
python main.py --dry-run --alt 20
python main.py --dry-run --alt 30 --spiral
python main.py --dry-run --model cv_models/model_5/best_float32.tflite
```

### Simulation on laptop (SITL required)

```bash
# Default simulation
set DRONE_MODE=SIMULATION
python main.py

# With specific model
python main.py --model cv_models/model_5/best_float32.tflite

# With f16 model (smaller, slightly less accurate)
python main.py --model cv_models/model_5/best_float16.tflite

# With COCO person detector (detects people instead of dummy)
python main.py --model cv_models/human.tflite

# Fast simulation with all safety features
python main.py --speed 5 --smart-detect --center-verify

# Beacon redirect test (triggers PLB after 5 minutes)
python main.py --speed 5 --beacon-delay 300

# Spiral search pattern
python main.py --spiral --alt 30

# Lower altitude, locked yaw
python main.py --alt 25 --lock-yaw

# Full options combined
python main.py --model cv_models/model_5/best_float32.tflite --alt 30 --speed 5 --conf 0.5 --smart-detect --center-verify
```

### Real mode on laptop (webcam + SITL)

```bash
set DRONE_MODE=REAL
python main.py
python main.py --model cv_models/model_5/best_float32.tflite --alt 25 --conf 0.5
python main.py --center-verify --smart-detect
```

### Real mode on Pi (headless over SSH)

```bash
source pienv/bin/activate
cd ~/sar-drone

# Default (auto-detects Cube on /dev/ttyAMA0)
python main.py --headless

# With model 5 float32
python main.py --headless --model cv_models/model_5/best_float32.tflite

# With model 5 float16 (faster inference, less memory)
python main.py --headless --model cv_models/model_5/best_float16.tflite

# With SAR v2 model
python main.py --headless --model cv_models/sar_v2_1088/best.tflite

# Conservative first flight (lower alt, higher confidence, no stream overhead)
python main.py --headless --alt 30 --conf 0.55 --no-stream

# Full safety features enabled
python main.py --headless --alt 30 --conf 0.5 --smart-detect --center-verify

# Spiral pattern at 25m
python main.py --headless --spiral --alt 25

# Disable geofence (only if testing outside SSSI area)
python main.py --headless --no-nfz

# Browser ground station available at: http://PI_IP:8090/
```

### Recommended first flight

```bash
python main.py --headless --alt 30 --conf 0.5 --smart-detect --center-verify --model cv_models/model_5/best_float32.tflite
```

This uses a conservative altitude (30m), requires higher confidence (0.5), needs consecutive detections before acting (`--smart-detect`), and averages GPS after centering (`--center-verify`).

---

## 4. passive_watch.py CLI Flags (Complete Reference)

Located at `field_tools/passive_watch.py`. Sends ZERO commands to the drone -- safe to run during any flight.

| Flag | Argument | Default | Description |
|------|----------|---------|-------------|
| `--port` | `<int>` | 8090 | HTTP stream server port. |
| `--conf` | `<float>` | 0.4 | Confidence threshold. |
| `--fps` | `<float>` | 5 | Max inference FPS. |
| `--model` | `<path>` | `best.tflite` | Path to TFLite model file. |
| `--save-dir` | `<dir>` | `detections` | Directory for detection snapshots. |
| `--no-save` | none | off | Stream only, don't save snapshots. |
| `--no-mavlink` | none | off | Skip mavproxy connection (no GPS overlay). |
| `--no-stream` | none | off | Disable HTTP stream server. |
| `--simple-names` | none | off | Clean filenames (no `det_` prefix, no JSON sidecars). |
| `--class-filter` | `<name>` | none | Only save detections matching this class name. |
| `--smart-estimate` | none | off | Accumulate central detections and save after N with median GPS. |
| `--smart-min` | `<int>` | 5 | Min central detections before saving SMART result. |
| `--smart-radius` | `<float>` | 1.0 | Max spread (metres) for SMART cluster grouping. |
| `--smart-dir` | `<dir>` | `<save-dir>/smart_detections/` | Custom directory for SMART result images. |
| `--fake` | none | off | Replay DJI video + SRT telemetry (no camera or mavproxy needed). |
| `--fake-video` | `<path>` | `RealVideo/DJI_0001_1456x1088_cropped_30fps.mp4` | Video file for fake mode. |
| `--fake-srt` | `<path>` | `RealVideo/DJI_20260311172332_0001_V.SRT` | SRT telemetry for fake mode. |

---

## 5. passive_watch.py Launch Configurations

### Fake mode on laptop (DJI video replay, no hardware)

```bash
# Basic replay with SMART estimation
python field_tools/passive_watch.py --fake --smart-estimate

# With model 5
python field_tools/passive_watch.py --fake --smart-estimate --model cv_models/model_5/best_float32.tflite

# With f16 model (faster)
python field_tools/passive_watch.py --fake --smart-estimate --model cv_models/model_5/best_float16.tflite

# With SAR v2 model
python field_tools/passive_watch.py --fake --smart-estimate --model cv_models/sar_v2_1088/best.tflite

# With COCO model (detect people instead of dummy)
python field_tools/passive_watch.py --fake --model cv_models/human.tflite --conf 0.2 --smart-estimate --class-filter "person"

# Lower confidence to catch more detections
python field_tools/passive_watch.py --fake --smart-estimate --conf 0.2

# Custom SMART parameters
python field_tools/passive_watch.py --fake --smart-estimate --smart-min 10 --smart-radius 2.0

# Stream only, no saving
python field_tools/passive_watch.py --fake --no-save
```

### Real mode on Pi (during manual RC flight)

```bash
source pienv/bin/activate
cd ~/sar-drone

# Basic with SMART estimation
python field_tools/passive_watch.py --smart-estimate

# With model 5 float32
python field_tools/passive_watch.py --smart-estimate --model cv_models/model_5/best_float32.tflite --conf 0.4

# With model 5 float16
python field_tools/passive_watch.py --smart-estimate --model cv_models/model_5/best_float16.tflite

# With stricter SMART clustering
python field_tools/passive_watch.py --smart-estimate --smart-radius 2.0 --smart-min 5

# Custom output directory (e.g. for a teammate)
python field_tools/passive_watch.py --model cv_models/model_5/best_float32.tflite --conf 0.4 --smart-estimate --smart-dir alex_results

# With class filter (COCO model, detect birds and people)
python field_tools/passive_watch.py --model cv_models/human.tflite --conf 0.2 --smart-estimate --class-filter "person,bird"

# Simple filenames for training data collection
python field_tools/passive_watch.py --simple-names --model cv_models/model_5/best_float32.tflite

# No GPS overlay (if mavproxy not running)
python field_tools/passive_watch.py --no-mavlink --smart-estimate

# Browser stream available at: http://PI_IP:8090/
```

---

## 6. Quick Model Swap (No Flags Needed)

All scripts default to `best.tflite` in the project root. Copy any model there to make it the default:

```bash
# Deploy model 5 float32 as default
cp cv_models/model_5/best_float32.tflite best.tflite

# Deploy model 5 float16 as default
cp cv_models/model_5/best_float16.tflite best.tflite

# Deploy SAR v2 as default
cp cv_models/sar_v2_1088/best.tflite best.tflite

# Deploy COCO person detector as default
cp cv_models/human.tflite best.tflite

# Deploy original custom model as default
cp cv_models/custom_yolov8n.tflite best.tflite
```

After swapping, restart any running script. No code changes needed.

---

## 7. Search Pattern Options

| Pattern | Flag | Description |
|---------|------|-------------|
| Lawnmower | *(default)* | Parallel strips with overlap based on camera FOV. Strip spacing auto-adjusts with `--alt`. |
| Spiral | `--spiral` | Perimeter spiral using Zian's planner. Falls back to built-in reimplementation. |

Both patterns auto-adjust strip spacing based on altitude and camera FOV:
- Lower `--alt` = narrower FOV footprint = tighter strips = more passes but larger dummy in frame.
- Higher `--alt` = wider FOV footprint = fewer passes but smaller dummy.

---

## 8. Key Parameters to Tune

| Parameter | Flag | Default | First Flight | Notes |
|-----------|------|---------|--------------|-------|
| Altitude | `--alt` | 35 m | 30 m | Lower = bigger dummy in frame, more passes |
| Speed | `--speed` | 1 (SITL only) | N/A | SITL speedup factor, not real flight speed |
| Confidence | `--conf` | 0.2 | 0.5 | Higher = fewer false positives |
| Smart detect | `--smart-detect` | off | on | Requires consecutive confirmed frames |
| Center verify | `--center-verify` | off | on | GPS-averages target after centering |
| Lock yaw | `--lock-yaw` | off | optional | Keeps heading fixed during sweep |
| Geofence | `--no-nfz` | on | keep on | Only disable if testing outside SSSI area |
| Stream | `--no-stream` | on | keep on | Disable to reduce CPU load on Pi |

### Config values in `config.py` (tune after real testing)

| Setting | Current Value | Notes |
|---------|---------------|-------|
| `TARGET_ALT` | 35.0 m | Override with `--alt` |
| `VERIFY_ALT` | 15.0 m | Descent altitude for close-up verification |
| `SEARCH_SPEED_MPS` | 10.0 m/s | Search pass speed (altitude-dependent) |
| `CONFIDENCE_THRESHOLD` | 0.2 | Override with `--conf` |
| `DETECT_CONFIRM_FRAMES` | 3 | Consecutive frames for `--smart-detect` |
| `SENSOR_WIDTH_MM` | 5.02 | IMX296 sensor |
| `FOCAL_LENGTH_MM` | 5.46 | Calibrated 2026-03-11 |
| `IMAGE_W` / `IMAGE_H` | 1456 / 1088 | IMX296 native resolution |
| `NFZ_HARD_BOUNDARY_M` | 3.0 m | Inside this = force MANUAL mode |
| `NFZ_WAYPOINT_BUFFER_M` | 30.0 m | Skip waypoints within this distance of NFZ |
