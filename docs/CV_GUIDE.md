# Computer Vision Guide

How the vision system works, how to improve it, and how to swap models — without breaking anything else.

---

## Architecture: Modular by Design

```
┌─────────────────────────────────────────────────────────┐
│  vision.py  (THE ONLY FILE THAT TOUCHES CV)             │
│                                                         │
│  VisionSystem                                           │
│    ├── __init__(camera_index, model_path)                │
│    ├── get_frame() → frame                              │
│    ├── detect_in_image(frame) → found, x, y, confidence │
│    ├── last_bbox_w, last_bbox_h                         │
│    └── release()                                        │
└────────────────────────┬────────────────────────────────┘
                         │
            Everything else calls this interface:
                         │
         ┌───────────────┼───────────────┐
         │               │               │
    main.py        test scripts     calibration
  (full mission)   (pi_2, pi_3,    (pi_6, pi_7,
                    pi_4, pi_8)     pi_8, pi_9)
```

**The rule**: only `vision.py` knows about models, inference, preprocessing. Everything else just calls `detect_in_image(frame)` and gets back `(found, x, y, confidence)`. You can change anything inside vision.py without touching any other file.

---

## The Interface

```python
eyes = VisionSystem(camera_index=0, model_path="best.tflite")

# Get a camera frame
frame = eyes.get_frame()

# Run detection
found, x, y, conf = eyes.detect_in_image(frame)
# found: bool  — was something detected?
# x, y: int    — pixel coordinates of detection centre
# conf: float  — confidence 0.0 to 1.0
# Also: eyes.last_bbox_w, eyes.last_bbox_h — bounding box size in pixels

# Cleanup
eyes.release()
```

As long as this interface stays the same, you can change the model, the preprocessing, the postprocessing — and nothing else breaks.

---

## Current Model

| Property | Value |
|----------|-------|
| File | `best.tflite` |
| Architecture | YOLOv8 (likely nano) |
| Input | 640x640x3 RGB, float32, normalised 0-1 |
| Output | [1, 5+nclass, num_detections] — YOLOv8 format |
| Confidence threshold | 0.4 (hardcoded in vision.py) |
| Backend on Pi | TFLite runtime |
| Backend on laptop | Ultralytics YOLO |

---

## Settings: Preliminary → Calibrated

Everything starts with preliminary defaults that work. After real testing, you calibrate to optimal values.

### Preliminary Settings (what we start with)

These are in `config.py` right now — sensible guesses, good enough to get running:

| Setting | Default | Where |
|---------|---------|-------|
| Camera resolution | 640x480 | `config.py` IMAGE_W/IMAGE_H |
| Camera FPS | 30 | `vision.py` line 41 |
| Model | best.tflite (YOLOv8n) | `vision.py` constructor |
| Confidence threshold | 0.4 | `vision.py` lines 117, 140 |
| Sensor width | 5.02mm | `config.py` SENSOR_WIDTH_MM |
| Focal length | 6.0mm | `config.py` FOCAL_LENGTH_MM |
| Search altitude | 30m | `config.py` TARGET_ALT |
| Verify altitude | 15m | `config.py` VERIFY_ALT |

### Calibration Scripts (find the real optimal values)

| What to calibrate | Script | When to run | What it changes |
|-------------------|--------|-------------|-----------------|
| Resolution vs speed vs detection | `pi_9_resolution_test.py` | Bench (Phase 1) | `IMAGE_W`, `IMAGE_H` |
| Pipeline FPS + blur impact | `pi_8_camera_test.py` | Bench (Phase 1) | Camera settings, flight speed |
| Bench FOV check | `pi_6_fov_test.py` | Bench (Phase 1) | `SENSOR_WIDTH_MM` or `FOCAL_LENGTH_MM` |
| Real FOV at altitude | `pi_7_alt_test.py` | Flight Day 1 | `SENSOR_WIDTH_MM` or `FOCAL_LENGTH_MM` |
| Max detection altitude | `pi_2_detect.py --headless` | Flight Day 1 | `TARGET_ALT`, `VERIFY_ALT` |
| Confidence threshold | Manual (from flight data) | After Flight Day 1 | Threshold in `vision.py` |
| Model choice (n/s/m) | `pi_3_benchmark.py` | After retraining | `best.tflite` file |

### Calibration Flow

```
PHASE 1 — BENCH (preliminary → good enough):
  pi_9  →  find best resolution         →  update IMAGE_W/IMAGE_H
  pi_8  →  measure FPS + blur           →  note: is blur a problem?
  pi_6  →  bench FOV check              →  rough SENSOR_WIDTH/FOCAL_LENGTH check
  pi_3  →  benchmark speed              →  is it < 200ms? If not, lower resolution

PHASE 2 — FLIGHT DAY 1 (good enough → calibrated):
  hover at 5m-30m  →  find max detection altitude  →  update TARGET_ALT, VERIFY_ALT
  hover at 2 heights  →  measure real footprint    →  update SENSOR_WIDTH or FOCAL_LENGTH
  fly over dummy  →  check false positives/negatives  →  tune confidence threshold

PHASE 3 — ITERATE (calibrated → optimised):
  collect aerial frames  →  retrain model  →  new best.tflite
  benchmark new vs old   →  keep the better one
  repeat until detection is reliable at needed altitude
```

Each phase makes the settings more accurate. You never need to touch code — just update `config.py` values and swap `best.tflite`.

---

## How to Swap a Model

Just replace `best.tflite`:

```bash
# On laptop: export new model
yolo export model=runs/detect/train/weights/best.pt format=tflite

# Copy to Pi
scp best.tflite pi@<IP>:~/sar-drone/

# Test it
python tests/pi_3_benchmark.py   # speed + detection
```

No code changes needed. The model file name is set in one place — when `VisionSystem` is constructed.

---

## What to Improve (in order of impact)

### 1. Training Data (biggest impact)

The model is only as good as what it was trained on.

**What helps most:**
- Real aerial images from the Pi camera at different altitudes
- Different lighting: sun, shadow, overcast, morning, afternoon
- Different backgrounds: grass, concrete, dirt, mixed
- Different angles: directly above, slightly off-centre
- Partially occluded dummy (edge of frame, partial cover)

**How to collect:**
- During bench testing: save frames from pi_2_detect.py
- During flight day 1: save frames at each altitude (step 8)
- Any time you run the camera: save interesting frames

**How to label:**
- Use [Roboflow](https://roboflow.com) (free tier) or [CVAT](https://cvat.ai) (open source)
- Draw bounding box around the dummy in each image
- Export in YOLO format (Roboflow does this automatically)

**How to retrain:**
```bash
# On laptop (needs ultralytics installed)
yolo detect train model=yolov8n.pt data=dataset.yaml epochs=100 imgsz=640

# Export to TFLite
yolo export model=runs/detect/train/weights/best.pt format=tflite

# Compare old vs new
python tests/pi_3_benchmark.py old_model.tflite
python tests/pi_3_benchmark.py best.tflite
```

### 2. Model Size (speed vs accuracy trade-off)

| Model | .tflite size | Pi speed (approx) | Accuracy |
|-------|-------------|-------------------|----------|
| YOLOv8n (nano) | ~6 MB | ~80-150ms | Good for close range |
| YOLOv8s (small) | ~22 MB | ~200-400ms | Better at distance |
| YOLOv8m (medium) | ~50 MB | ~500ms+ | Best accuracy |

Start with nano. If detection fails at needed altitudes but speed is fine, try small.

**To train a different size:**
```bash
yolo detect train model=yolov8s.pt data=dataset.yaml epochs=100 imgsz=640
```

### 3. Camera Resolution (config.py)

Lower resolution = faster pipeline but potentially worse detection.

```python
# config.py
IMAGE_W = 640   # try 480 or 320
IMAGE_H = 480   # try 360 or 240
```

Use `tests/pi_9_resolution_test.py` to find the sweet spot.

### 4. Confidence Threshold

Currently hardcoded at 0.4 in vision.py (lines 117 and 140).

- **Lower (0.3)**: catches more, but more false positives
- **Higher (0.6)**: fewer false positives, but might miss targets at distance

After flight testing, tune based on your false positive vs false negative rates.

### 5. Camera Settings (hardware level)

- **Shutter speed**: faster = less motion blur, but darker image
- **Gain/ISO**: higher = brighter but more noise
- **Global shutter camera**: eliminates rolling shutter blur entirely (Pi GS Camera)

Use `tests/pi_8_camera_test.py` to measure blur impact on detection.

---

## Testing Workflow

After any CV change, run this sequence:

```bash
# 1. Does it still detect?
python tests/pi_2_detect.py --headless

# 2. Speed ok?
python tests/pi_3_benchmark.py

# 3. Full pipeline (if Cube connected)
python tests/pi_4_detect_and_log.py
```

For comparing two models side by side:
```bash
python tests/pi_3_benchmark.py old_best.tflite
python tests/pi_3_benchmark.py best.tflite
# Compare: speed, detection rate, avg confidence, avg position
```

---

## CV Test Scripts Reference

| Script | What it tests | When to use |
|--------|--------------|-------------|
| `pi_1_camera.py` | Camera gives frames | After changing camera/resolution |
| `pi_2_detect.py` | Live detection with display | Quick visual check |
| `pi_3_benchmark.py` | Speed + accuracy on static image | After swapping model |
| `pi_8_camera_test.py` | FPS, pipeline bottleneck, blur | After changing camera settings |
| `pi_9_resolution_test.py` | Resolution vs speed vs detection | Finding optimal resolution |
| `pi_6_fov_test.py` | FOV on bench (camera over ruler) | After changing lens/camera |
| `debug_tflite.py` | Raw TFLite output inspection | Debugging model output format |

---

## How Vision Connects to the Rest

```
vision.py                    main.py / test scripts
─────────                    ──────────────────────
get_frame()          →       Gets camera image
detect_in_image()    →       Returns (found, x, y, conf)
                             │
                             ├── main.py uses x,y to calculate GPS offset
                             ├── main.py uses conf to decide: detect or ignore
                             ├── pi_4 uses x,y for LEFT/RIGHT/CENTRED guidance
                             ├── pi_3 uses timing for benchmark
                             └── last_bbox_w/h used for FOV calibration

config.py
─────────
IMAGE_W, IMAGE_H     →      Camera resolution
SENSOR_WIDTH_MM      →      FOV calculation (not used by vision.py directly)
FOCAL_LENGTH_MM      →      FOV calculation (not used by vision.py directly)
```

Vision doesn't know about GPS, altitudes, search patterns, or the Cube. It just says "I see something at pixel (x, y) with confidence c." The rest of the system decides what to do with that.

---

## Improvement Checklist

```
BEFORE FIRST FLIGHT:
  [ ] Current model detects dummy on bench (pi_2)
  [ ] Speed < 200ms (pi_3)
  [ ] Best resolution found (pi_9)

AFTER FIRST FLIGHT:
  [ ] Save frames from different altitudes
  [ ] Note: at what altitude did detection fail?
  [ ] Note: any false positives? What triggered them?

IMPROVE CYCLE:
  [ ] Collect + label new aerial images
  [ ] Retrain: yolo detect train ...
  [ ] Export: yolo export ... format=tflite
  [ ] Copy new best.tflite to Pi
  [ ] Benchmark: pi_3 — compare speed + detection vs old model
  [ ] If better → keep. If worse → revert.

ADVANCED (later):
  [ ] Try YOLOv8s if nano struggles at altitude
  [ ] Tune confidence threshold based on flight data
  [ ] Try global shutter camera if blur is a problem
  [ ] Consider multi-frame confirmation (detect on N consecutive frames)
```
