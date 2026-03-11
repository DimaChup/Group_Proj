# Computer Vision Guide

How the vision system works, how to improve it, and how to swap models — without breaking anything else.

---

## PRIORITY CHECKLIST — Things To Do Before Flight Day

This is the CV to-do list. Work through it top to bottom.

### 1. Get a Good Model

Current model (`best.tflite`) was trained on **synthetic composites** — map.jpg with dummy.png pasted on top. This is okay for proving the pipeline works but will likely struggle with:
- Real grass / real lighting / real shadows
- Different dummy poses (lying, sitting, fetal position)
- Different clothing colors (current training is one outfit)
- Partially occluded targets (arm behind bush, half in shadow)
- Similar-looking objects (bags, logs, clothing on ground)

**Options to improve:**

```
[ ] OPTION A: Retrain on real images (HIGHEST IMPACT)
    - Collect real photos of dummy on grass from Pi camera
    - Different poses: lying flat, curled up, arms out, face down
    - Different clothes: bright, dark, camo, high-vis
    - Different backgrounds: short grass, long grass, dirt, path edge
    - Different heights: take photos from 5m, 10m, 15m, 20m, 25m, 30m
    - Different lighting: sunny, overcast, morning, afternoon
    - Label with Roboflow (roboflow.com) or CVAT (cvat.ai)
    - Retrain: yolo detect train model=yolov8n.pt data=dataset.yaml epochs=100
    - Export: yolo export model=best.pt format=tflite
    - Benchmark old vs new on Pi: tests/hardware/benchmark.py

[ ] OPTION B: Use a pre-trained person/human detector
    - YOLO COCO models already detect "person" class (class 0)
    - Download: yolov8n.pt (already trained on 80 classes including person)
    - Export to TFLite: yolo export model=yolov8n.pt format=tflite
    - Pros: detects real humans immediately, no training needed
    - Cons: also detects people who aren't the target, may be less
      sensitive to a "dummy" that doesn't look exactly like a real person
    - Could use as a SECOND model alongside custom dummy model
    - Test: load both, if either detects → flag it

[ ] OPTION C: Try a bigger model if nano struggles at altitude
    - YOLOv8s (small) — bigger, slower, more accurate
    - YOLOv8m (medium) — even bigger
    - Benchmark on Pi to check speed is acceptable (< 300ms)
    - See "Model Size" section below for comparison

[ ] OPTION D: Data augmentation in training pipeline
    - generate_dataset.py already creates synthetic composites
    - Add: brightness variation, contrast, blur, rotation
    - Add: scale variation (simulate different altitudes)
    - Add: noise (simulate real camera)
    - This improves model robustness without collecting real data k
```

### 2. Calibrate Flight Parameters for Detection

These must be determined by real testing. No way to know from simulation.

```
[ ] Max detection altitude — at what height does the model stop detecting?
    - Run tests/flight/1_passive_flight.py during manual RC flight
    - Hover at 5m, 10m, 15m, 20m, 25m, 30m over dummy
    - Record: detected Y/N, confidence, at each altitude
    - Result → update TARGET_ALT in config.py

[ ] Max flight speed for detection — how fast before smear kills detection?
    - Run tests/flight/1_passive_flight.py during manual flight
    - Fly over dummy at 2, 3, 5, 7, 10 m/s
    - Check /ai-snapshot or /stream-ai on tests/diagnostics/camera_stream_fast.py for blur
    - Record: detected Y/N, confidence, blur level at each speed
    - Result → update SEARCH_SPEED_MPS in config.py

[ ] Optimal confidence threshold — balance false positives vs missed targets
    - Currently 0.4 in vision.py (lines 174 and 197)
    - After passive flight: review logs
    - Too many false positives? → raise to 0.5 or 0.6
    - Missing real targets? → lower to 0.3
    - Result → update threshold in vision.py

[ ] FOV calibration — so GPS offset math is accurate
    - Run fov_calibrate.py on bench with known object at known distance
    - Result → update SENSOR_WIDTH_MM and FOCAL_LENGTH_MM in config.py

[ ] FPS vs speed calculation
    - AI processes ~4 fps on Pi
    - At 5 m/s: drone moves 1.25m between frames
    - At 3 m/s: drone moves 0.75m between frames
    - Ground coverage at 30m alt ≈ 25m wide → good overlap at 3-5 m/s
    - If detection unreliable → slow down or lower altitude
```

### 3. GPS Coordinate Fallback (Skip CV, Test Flight Sequence)

For testing the flight/landing sequence even if CV fails:

```
[ ] Add --target-gps flag to main.py or create test script
    - Give it dummy GPS coordinates directly: --target-gps 51.4545,-2.6030
    - Drone takes off, flies to those coordinates, descends, lands
    - No camera needed, no detection needed
    - Proves: takeoff, navigation, descent, landing all work
    - Use tests/flight/2_waypoints.py for basic version (already exists)
    - Could extend tests/flight/3_auto_detect.py with --force-target 51.4545,-2.6030

[ ] This lets you test the full landing sequence without relying on CV
    - Useful if outdoor CV testing shows model can't detect from altitude
    - Still demonstrates autonomous navigation for the project
```

### 4. Multi-Frame Confirmation

Avoid acting on a single false positive:

```
[x] tests/flight/3_auto_detect.py already requires --min-detections consecutive detections
    - Default: 2 consecutive detections before switching to GUIDED
    - Adjustable: --min-detections 3 or 4 for more safety
[ ] Consider adding same logic to main.py SEARCH → CENTERING transition
    - Currently triggers on single detection (risky for false positives)
```

---

## Current State

| What | Status | Notes |
|------|--------|-------|
| Model loads on Pi | WORKING | TFLite backend, ~250ms inference |
| Detection on bench | WORKING | 0.966 confidence on printed dummy |
| Camera color fix | DONE | BGR passthrough, no cvtColor needed |
| Detection with corrected colors | NOT TESTED | Need to push code + test on Pi |
| Detection from real altitude | NOT TESTED | Passive flight test needed |
| Detection at flight speed | NOT TESTED | Motion blur unknown |
| Pre-trained person model | NOT TESTED | Could be a quick win |
| Model retrained on real images | NOT DONE | Need real aerial images first |

---

## The Journey: Basic → Working → Optimised

Get it working first with defaults. Then measure. Then improve. Don't skip ahead.

### Stage 1: Get Basic Detection Running on Pi

Goal: AI detects a dummy held in front of the camera. Nothing fancy.

```
[x] Pi set up, venv activated, dependencies installed (PI_SETUP.md)
[x] Camera gives frames                        → tests/laptop/test_camera.py
[x] AI loads and detects dummy on bench         → tests/laptop/test_cv.py --headless
[x] Note inference speed (just observe for now) → tests/hardware/benchmark.py
    Result: 256ms avg, 3.9 FPS, 50/50 detection, 0.966 confidence
```

### Stage 2: Measure Everything (Before First Flight)

Goal: know your numbers so you can make informed decisions.

```
[ ] Best resolution that still detects          → tests/hardware/cv_benchmark.py (resolution test planned)
    Result: ___x___ at ___ms
[ ] Camera FPS vs pipeline FPS                  → tests/hardware/cv_benchmark.py
    Camera: ___fps, Pipeline: ___fps
[ ] Bench FOV check (camera over ruler)         → fov_calibrate.py
    Measured FOV matches config? Y/N
    If N → update SENSOR_WIDTH_MM or FOCAL_LENGTH_MM in config.py
```

### Stage 3: First Flight Data Collection

Goal: find out what simulation couldn't tell you.

```
[ ] Manual flight (pilot on RC, Pi logging passively)
    → tests/flight/1_passive_flight.py --headless
[ ] Save frames at 5m, 10m, 15m, 20m, 25m, 30m
[ ] At what altitude does detection first fail?    → ___m
[ ] At what speed does motion blur kill detection? → ___m/s
[ ] Any false positives? What triggered them?      → note: ___
[ ] Real FOV at altitude                           → tests/calibration/alt_test.py
```

Update config.py with findings:
```python
TARGET_ALT = ___     # highest altitude where detection works reliably
VERIFY_ALT = ___     # lower altitude for close-up confirmation
SEARCH_SPEED_MPS = ___  # fastest speed with reliable detection
```

### Stage 4: Optimise (Iterate After Each Flight)

Now you have real data. Improve one thing at a time.

```
OPTION A — Better training data (biggest impact):
  [ ] Collect real aerial frames from flights
  [ ] Label with Roboflow or CVAT
  [ ] Retrain: yolo detect train model=yolov8n.pt data=dataset.yaml epochs=100
  [ ] Export: yolo export model=best.pt format=tflite
  [ ] Copy new best.tflite to Pi
  [ ] Benchmark old vs new: tests/hardware/benchmark.py
  [ ] Keep whichever is better

OPTION B — Try pre-trained COCO person detector:
  [ ] Export yolov8n.pt (COCO) to TFLite
  [ ] Test on Pi — does it detect people from altitude?
  [ ] Compare: custom dummy model vs COCO person model
  [ ] Consider running both

OPTION C — Try a bigger model (if nano struggles at altitude):
  [ ] Train YOLOv8s instead of YOLOv8n
  [ ] Export to tflite, benchmark on Pi
  [ ] Is it fast enough? (< 300ms target)
  [ ] If yes and detects better → keep it

OPTION D — Tune confidence threshold:
  [ ] Too many false positives? → raise threshold (0.4 → 0.5 or 0.6)
  [ ] Missing real targets? → lower threshold (0.4 → 0.3)
  [ ] Change in vision.py lines 174 and 197

OPTION E — Tune flight parameters:
  [ ] AI too slow for flight speed? → lower SEARCH_SPEED_MPS in config.py
  [ ] Detection only works close? → lower TARGET_ALT
  [ ] Blur killing detection? → lower speed or increase shutter speed
```

The loop: **fly → measure → adjust one thing → fly again → repeat**

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
| Architecture | YOLOv8n (nano) |
| Input | 640x640x3 RGB, float32, normalised 0-1 |
| Output | [1, 5+nclass, num_detections] — YOLOv8 format |
| Confidence threshold | 0.4 (hardcoded in vision.py) |
| Backend on Pi | TFLite runtime (ai-edge-litert on Python 3.13) |
| Backend on laptop | Ultralytics YOLO |
| Training data | Synthetic composites (map.jpg + dummy.png) |
| Pi inference speed | ~250ms per frame (~4 FPS) |

### Model Size Comparison

| Model | .tflite size | Pi speed (approx) | Accuracy |
|-------|-------------|-------------------|----------|
| YOLOv8n (nano) | ~6 MB | ~250ms | Good for close range |
| YOLOv8s (small) | ~22 MB | ~400-600ms | Better at distance |
| YOLOv8m (medium) | ~50 MB | ~800ms+ | Best accuracy |
| COCO yolov8n (pre-trained) | ~6 MB | ~250ms | Detects "person" class |

### Speed vs Flight Coverage

| AI FPS | Drone speed | Distance between frames | Coverage gap? |
|--------|------------|------------------------|--------------|
| 4 fps | 3 m/s | 0.75m | No — good overlap |
| 4 fps | 5 m/s | 1.25m | Marginal — might miss |
| 4 fps | 7 m/s | 1.75m | Risky — could miss target |
| 4 fps | 10 m/s | 2.5m | Likely to miss |

At 30m altitude the camera sees ~25m of ground width, so even at 5 m/s each frame overlaps significantly. But the dummy is small (~46px tall at 30m) so you want multiple frames looking at it.

**Recommendation**: Start with 3 m/s search speed. Increase after testing.

### CRITICAL: Model Architecture = FPS

**The model architecture (nano/small/medium) determines your FPS. This cannot be changed
without changing the model.** Training a nano model on better data gives you the same ~4 fps
but better detection. Switching to small gives better accuracy but halves your FPS.

| What you change | Effect on FPS | Effect on accuracy |
|----------------|--------------|-------------------|
| Better training data (same nano) | NO CHANGE (~4 fps) | BETTER |
| Different confidence threshold | NO CHANGE (~4 fps) | Trades FP vs FN |
| Lower camera resolution | Slight improvement | Possibly worse |
| Switch to YOLOv8s (small) | HALVED (~2 fps) | Better at distance |
| Switch to YOLOv8m (medium) | QUARTERED (~1 fps) | Best accuracy |
| INT8 quantization | ~2x faster (~8 fps) | Slightly worse |

**Best strategy: stick with nano, train on better data. Only switch to small if nano
genuinely can't detect at your target altitude.**

### Resolution, FPS, and Inference Pipeline — How It All Fits Together

Understanding this prevents wasting time on the wrong optimisation.

**The pipeline:**
```
Camera (640x480 BGR) → vision.py resizes to 640x640 RGB → TFLite inference (~250ms) → result
```

**Key insight: camera resolution does NOT affect inference speed.** The model always processes
a 640x640 image regardless of what the camera captures. Changing camera resolution only changes
the resize step (< 1ms), not the inference step (250ms).

| Camera resolution | What happens | Inference time | Detection quality |
|-------------------|-------------|----------------|-------------------|
| 320x240 | Upscaled to 640x640 | ~250ms (same) | Worse — less detail fed in |
| 640x480 | Slight stretch to 640x640 | ~250ms (same) | Good — close to model input |
| 1280x960 | Downscaled to 640x640 | ~250ms (same) | Same — extra detail lost in resize |

**Current choice: 640x480.** Closest to model input (640x640) with minimal wasted computation.
No benefit to going higher because the model discards the extra resolution. Going lower loses
detail that the model could use for small/distant targets.

**Where the time goes (per frame):**
```
Camera capture:     ~33ms  (30fps capable)
Resize to 640x640:   <1ms
BGR→RGB conversion:  <1ms
TFLite inference:  ~250ms  ← THIS IS THE BOTTLENECK
Post-processing:     <1ms
─────────────────────────
Total:             ~255ms  → ~4 fps
```

**Ways to speed up inference (researched 2026-03-11, see Inference Optimization section below):**

| Approach | Actual Pi 5 Speed | Speedup | Cost | Trade-off |
|----------|------------------|---------|------|-----------|
| **NCNN export (same model)** | **~83ms (12 FPS)** | **3x** | Free | Needs ultralytics on Pi or ncnn bindings |
| YOLO11n/26n + NCNN | ~68-80ms (15 FPS) | 3.5x | Free | Better accuracy too (+3 mAP) |
| ONNX Runtime | ~170ms (6 FPS) | 1.5x | Free | Middle ground |
| INT8 TFLite | ~250ms (4 FPS) | **1x (NO gain)** | Free | Known Pi 5 issue — skip this |
| Smaller input (320x320) | ~40-50ms est. | ~5x | Free | Risky — small targets lost at altitude |
| Hailo-8L AI HAT+ | ~16ms (60 FPS) | **15x** | $70 | Hardware purchase + model conversion |
| Coral USB TPU | Worse than current | 0x | $60 | **Dead product — DO NOT BUY** |

**Current decision: 640x480 camera, 640x640 model input, ~4fps is acceptable for first flight.**
At 3 m/s search speed, the drone moves 0.75m between frames — plenty of overlap for a target
that's in view for ~25m of ground width.

**Upgrade path (priority order):**
1. [ ] **NCNN export** — 3x speedup for free. `yolo export model=best.pt format=ncnn`
2. [ ] **YOLO11n or YOLO26n** — newer architecture, faster + more accurate than YOLOv8n
3. [ ] **Hailo-8L** ($70) — 15x speedup, official Pi product. Post-first-flight upgrade.
4. [x] ~~INT8 TFLite~~ — confirmed no speedup on Pi 5 ARM CPU. Skip.
5. [x] ~~Coral USB TPU~~ — discontinued, 1-2 FPS on YOLO, Python 3.13 incompatible. Skip.

---

## How to Systematically Test Models

This is the procedure for comparing models on real hardware. Follow it every time you
want to evaluate a new model.

### Step 1: Bench Test (indoors, no flight)

For each model you want to test:

```bash
# Copy model to Pi
scp new_model.tflite pi@<IP>:~/dima/Group_Proj/

# SSH to Pi
ssh pi@<IP>
cd ~/dima/Group_Proj
source pienv/bin/activate

# A) Speed benchmark — how fast is inference?
#    Place printed dummy in front of camera
python tests/hardware/benchmark.py
# Record: avg_ms, fps, detection_rate, avg_confidence

# B) Live detection test — does it detect reliably?
python tests/laptop/test_cv.py --headless
# Observe: does it detect? At what distance? False positives?

# C) Stream test — watch what AI sees in real-time
python tests/diagnostics/camera_stream_fast.py --with-detection --headless
# Open http://<PI_IP>:8090/ on laptop
# Open http://<PI_IP>:8090/stream-ai to see AI input frames
# Move dummy around — does it track? At what range does it lose it?
```

**Record results in this table:**

```
| Model | File | Size | Avg ms | FPS | Det rate | Avg conf | Notes |
|-------|------|------|--------|-----|----------|----------|-------|
| Current (custom nano) | best.tflite | 6MB | 250ms | 4.0 | 100% | 0.966 | bench, printed dummy |
| COCO nano | yolov8n.tflite | 6MB | ___ms | ___ | ___% | _____ | |
| Custom small | best_s.tflite | 22MB | ___ms | ___ | ___% | _____ | |
| Retrained nano | best_v2.tflite | 6MB | ___ms | ___ | ___% | _____ | |
```

### Step 2: Static Altitude Test (outdoor, no flight)

Hold the Pi camera above the dummy at known heights. This tells you max detection
altitude before you fly.

```bash
# Run detection with stream so you can see results on laptop
python tests/diagnostics/camera_stream_fast.py --with-detection --headless
```

**Procedure:**
1. Place dummy on ground (grass, realistic surface)
2. Hold Pi + camera at 2m above dummy → record: detected Y/N, confidence
3. Repeat at 3m, 5m, 7m, 10m (use a ladder or balcony)
4. Note the height where detection fails

**Record results:**

```
| Model | 2m | 3m | 5m | 7m | 10m | Max reliable height |
|-------|-----|-----|-----|-----|------|-------------------|
| Current nano | Y/0.96 | Y/___ | Y/___ | ?/___ | ?/___ | ___m |
| COCO nano | Y/___ | Y/___ | ?/___ | ?/___ | ?/___ | ___m |
```

### Step 3: Passive Flight Test (outdoor, real flight)

This is the real test. Pilot flies manually, Pi logs detections.

```bash
# Start mavproxy first (Terminal 1)
sudo /opt/mavlink/mavlink-venv/bin/mavproxy.py \
  --master=/dev/ttyAMA0 --baudrate=921600 --streamrate=10 \
  --out=udpout:127.0.0.1:14550 --out=tcpin:0.0.0.0:5762

# Run passive flight (Terminal 2)
python tests/flight/1_passive_flight.py --headless
```

**Procedure:**
1. Place dummy on ground in open area
2. Pilot takes off, hovers at 10m directly above dummy
3. Hold for 30 seconds → record detection rate + confidence
4. Climb to 15m → hold 30 seconds → record
5. Climb to 20m, 25m, 30m → same
6. Fly over dummy at 3 m/s at 15m → record (tests motion blur)
7. Fly over at 5 m/s → record
8. Fly over at 7 m/s → record

**Record results:**

```
| Model | Hover 10m | Hover 15m | Hover 20m | Hover 25m | Hover 30m |
|-------|-----------|-----------|-----------|-----------|-----------|
| Current | ___% | ___% | ___% | ___% | ___% |

| Model | 3 m/s @15m | 5 m/s @15m | 7 m/s @15m |
|-------|------------|------------|------------|
| Current | ___% | ___% | ___% |
```

**After the flight:**
- Review `passive_flight_log.csv` — all detections with GPS, altitude, confidence
- Press 's' during flight to save snapshots → use for retraining
- Check /ai-snapshot frames for motion blur

### Step 4: Compare and Decide

After testing multiple models with the same procedure:

```
DECISION MATRIX:
                    | Speed | Hover det | Moving det | False pos |
Current custom nano | 4 fps | ___% @20m | ___% @5m/s | ___/min   |
COCO nano           | 4 fps | ___% @20m | ___% @5m/s | ___/min   |
Retrained nano      | 4 fps | ___% @20m | ___% @5m/s | ___/min   |
Custom small        | 2 fps | ___% @20m | ___% @5m/s | ___/min   |

WINNER: __________ (best hover detection + acceptable speed + low false pos)
```

Then:
```bash
# Make the winner the active model
cp winning_model.tflite best.tflite
git add best.tflite && git commit -m "swap to better model"
git push  # then pull on Pi
```

### Step 5: Iterate

After each flight day:
1. Collect saved frames (snapshots from passive flight)
2. Label in Roboflow (draw bounding boxes)
3. Add to training dataset
4. Retrain nano model
5. Go back to Step 1

Each iteration makes the model better because it's trained on **real data from your
actual camera at your actual flight altitudes**.

---

## Settings: Preliminary → Calibrated

Everything starts with preliminary defaults. After real testing, calibrate to optimal values.

### Preliminary Settings (current)

| Setting | Default | Where | Calibrate with |
|---------|---------|-------|---------------|
| Camera resolution | 640x480 | `config.py` IMAGE_W/IMAGE_H | tests/hardware/cv_benchmark.py (resolution test planned) |
| Model | best.tflite (YOLOv8n) | vision.py constructor | tests/hardware/benchmark.py |
| Confidence threshold | 0.4 | vision.py lines 174, 197 | Passive flight data |
| Sensor width | 5.02mm | `config.py` SENSOR_WIDTH_MM | fov_calibrate.py |
| Focal length | 6.0mm | `config.py` FOCAL_LENGTH_MM | fov_calibrate.py |
| Search altitude | 30m | `config.py` TARGET_ALT | Passive flight data |
| Verify altitude | 15m | `config.py` VERIFY_ALT | Passive flight data |
| Search speed | 5 m/s | `config.py` SEARCH_SPEED_MPS | Passive flight data |

---

## How to Swap a Model

Just replace `best.tflite`:

```bash
# On laptop: export new model
yolo export model=runs/detect/train/weights/best.pt format=tflite

# Copy to Pi
scp best.tflite pi@<IP>:~/dima/Group_Proj/

# Test it
python tests/hardware/benchmark.py   # speed + detection
```

No code changes needed. The model file name is set in one place — when `VisionSystem` is constructed.

### To try a COCO person detector:

```bash
# On laptop
pip install ultralytics
yolo export model=yolov8n.pt format=tflite
# This exports the standard COCO model (80 classes including "person")

# Copy to Pi as a separate file
scp yolov8n.tflite pi@<IP>:~/dima/Group_Proj/

# Test with benchmark
python tests/hardware/benchmark.py  # point at real person or dummy
```

Note: COCO model outputs 80 classes. Person is class 0. You'd need to modify vision.py to filter for class 0 only if using COCO model, or just take the highest confidence detection regardless of class.

---

## Training Data: What Makes a Good Dataset

### What to collect

| Category | Examples | Why it matters |
|----------|----------|---------------|
| **Poses** | Lying flat, curled up, face down, arms out, sitting | Dummy might land in any position |
| **Clothing** | Bright, dark, camo, high-vis, mixed | Can't assume one color |
| **Backgrounds** | Short grass, tall grass, dirt, path, concrete | Avoid model only learning "green = target" |
| **Altitudes** | 5m, 10m, 15m, 20m, 25m, 30m | Different apparent sizes |
| **Lighting** | Sunny, overcast, shadowed, morning, afternoon | Real conditions vary |
| **Angles** | Directly above, slight tilt, edge of frame | Drone won't always be perfectly overhead |
| **Negatives** | Empty grass, bags, logs, clothing piles | Teach model what is NOT a target |

### How many images?

- **Minimum**: 100 labeled images (50 positive, 50 negative)
- **Good**: 300-500 labeled images
- **Best**: 1000+ with good variety

### Quick dataset from passive flight

During `tests/flight/1_passive_flight.py`, press 's' to save snapshots. After the flight, label them in Roboflow. This gives you real aerial training data with zero extra effort.

---

## IMPORTANT: IMX296 Global Shutter Camera Color Fix

The IMX296 sensor outputs **BGR data** despite picamera2 labeling the format as RGB888.
This means `cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)` **must NOT be used** — it double-swaps
the channels, causing a blue tint on all images.

**If you add a new test script with picamera2**: Do NOT add color conversion. Just use the
raw frame. See `vision.py` get_frame() for the reference implementation.

---

## CV Test Scripts Reference

| Script | What it tests | When to use |
|--------|--------------|-------------|
| `tests/laptop/test_camera.py` | Camera gives frames | After changing camera/resolution |
| `tests/laptop/test_cv.py` | Live detection with display | Quick visual check |
| `tests/hardware/benchmark.py` | Speed + accuracy on static image | After swapping model |
| `tests/hardware/cv_benchmark.py` | FPS, pipeline bottleneck, blur | After changing camera settings |
| `tests/hardware/cv_benchmark.py (resolution test planned)` | Resolution vs speed vs detection | Finding optimal resolution |
| `tests/calibration/fov_calibrate.py` | FOV on bench (camera over ruler) | After changing lens/camera |
| `tests/calibration/fov_calibrate.py` | FOV calibration | Before flight |
| `tests/diagnostics/camera_stream_fast.py` | Stream + /ai-snapshot for blur check | Check what AI sees in real-time |
| `tests/flight/1_passive_flight.py` | Full passive detection during flight | Calibrate altitude + speed |
| `tests/flight/3_auto_detect.py` | AUTO waypoints + detect & hover | Test detection → action link |
| `tests/laptop/debug_tflite.py` | Raw TFLite output inspection | Debugging model output format |

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
                             ├── 1_passive_flight uses x,y for guidance overlay
                             ├── 3_auto_detect uses x,y for GPS + centering
                             ├── benchmark.py uses timing for benchmark
                             └── last_bbox_w/h used for FOV calibration

config.py
─────────
IMAGE_W, IMAGE_H     →      Camera resolution
SENSOR_WIDTH_MM      →      FOV calculation (GPS offset math in main.py)
FOCAL_LENGTH_MM      →      FOV calculation (GPS offset math in main.py)
```

Vision doesn't know about GPS, altitudes, search patterns, or the Cube. It just says "I see something at pixel (x, y) with confidence c." The rest of the system decides what to do with that.

---

## GPS Estimation: Error Sources, Compensation, and Best Practices

This section documents how the simulator estimates the dummy's GPS position from CV
detections, what errors affect the estimate, and what to watch out for in real flights.

### How Position Estimation Works

Every time CV detects the dummy in a frame, the system calculates its GPS position:

```
1. CV reports pixel coordinates (x, y) of dummy centre in the 640x480 frame
2. Pixel offset from frame centre = (x - 320, y - 240)
3. Ground Sample Distance (GSD) = (altitude * sensor_width) / (focal_length * image_width)
   GSD tells us how many metres each pixel represents on the ground
4. Ground offset in metres = pixel_offset * GSD
5. Rotate by drone yaw to get north/east offset
6. Add to drone GPS position → estimated dummy GPS
```

Each detection produces one GPS estimate. We collect many of these and average them
(weighted by quality) to get the best estimate.

### Three Estimation Methods (implemented in simple_simulator.py)

| Method | How it works | Marker | Best for |
|--------|-------------|--------|----------|
| **Rolling 50** | Weighted average of last 50 observations | Green circle | Quick convergence, forgets old data |
| **Running total** | Weighted average of ALL observations ever | Square "T" | Long-term accuracy, most stable |
| **Kalman filter** | Bayesian filter with uncertainty tracking | Triangle "K" | Optimal filtering (needs tuning) |

**Running total average is recommended as the primary estimate.** It's the simplest, most
stable, and performs best with many observations. The rolling 50 is useful early on (before
50 observations) and the Kalman filter is kept for comparison/experimentation.

### Error Sources

| Error source | Magnitude | Type | Averages out? | Compensation |
|-------------|-----------|------|---------------|-------------|
| **GPS drift** | ±2-3m | Random | YES | More observations → drift cancels out |
| **Altitude noise** | ±1m | Random | YES | Many readings average to true altitude |
| **Yaw noise** | ±3° | Random | YES | Offset rotations cancel over many frames |
| **Camera shake/vibration** | ±5-20px | Random | YES | EMA smoothing + many observations |
| **Motion blur** | Shifts centre ±px | Random | YES | Slower flight speed helps, still averages |
| **CV bounding box jitter** | ±5-10px | Random | YES | Inherent noise in detection, averages out |
| **FOV calibration** | Scales ALL estimates | **SYSTEMATIC** | **NO** | Must calibrate SENSOR_WIDTH_MM and FOCAL_LENGTH_MM |

**Key insight**: All random errors average out with enough observations. The ONLY error that
doesn't average out is **FOV calibration error** — if your sensor width or focal length is
wrong, every single estimate is biased in the same direction. This is the one thing you MUST
get right.

### FOV Calibration (Critical)

If FOV is miscalibrated, GSD is wrong, and every pixel-to-GPS conversion has a systematic
bias. For example:
- FOV 5% too wide → all estimates are 5% further from drone than reality
- FOV 5% too narrow → all estimates are 5% closer than reality

**How to calibrate:**
1. Run `tests/calibration/fov_calibrate.py` on bench
2. Place object at known distance, measure pixel size
3. Calculate true SENSOR_WIDTH_MM and FOCAL_LENGTH_MM
4. Update `config.py`

**Simulation flag**: `--fov-error 5` introduces ±5% random FOV error to test sensitivity.

### Inverse Variance Weighting (Altitude-Dependent)

Lower altitude = better estimate. Position error is proportional to altitude (larger GSD =
each pixel covers more ground = more error per pixel of jitter). We weight observations by
inverse variance:

```
weight_factor = (30 / altitude)²
```

| Altitude | Weight factor | Meaning |
|----------|--------------|---------|
| 30m | 1x | Baseline weight |
| 20m | 2.25x | 2.25x more trusted than 30m |
| 15m | 4x | 4x more trusted |
| 10m | 9x | 9x more trusted |

This means a few observations at 10m altitude are worth many observations at 30m. When
investigating (hovering at 15m), the estimate converges much faster than during a high-altitude
flyby.

Additionally, centre-snap observations (target confirmed at frame centre, pixel offset ≈ 0)
get a 10x bonus weight because there's no pixel-to-ground conversion error — the target is
directly below the drone.

### Altitude Test Results (Simulation)

Run with `H` key in simple_simulator.py. Hovers at each altitude for 10 seconds:

```
Altitude | Rolling 50 error | Total avg error | Kalman error
---------|-------------------|-----------------|-------------
  30m    |    ~2-4m          |    ~2-4m        |   ~3-5m
  25m    |    ~1.5-3m        |    ~1.5-3m      |   ~2-4m
  20m    |    ~1-2m          |    ~1-2m        |   ~1.5-3m
  15m    |    ~0.5-1.5m      |    ~0.5-1m      |   ~1-2m
  10m    |    ~0.3-0.8m      |    ~0.3-0.6m    |   ~0.5-1m
```

**Lower altitude = better estimate.** This is expected — fewer metres per pixel, less error
amplification. The investigate hover at 15m typically produces sub-metre estimates.

### Simulation vs Reality

The simulation has a known limitation: at low altitude, the drone camera view is created by
cropping a small region of map.jpg and upscaling to 640x480. This means low-altitude images
are pixelated (few source pixels stretched). In reality, the camera always captures fresh
640x480 regardless of altitude — the image quality at low altitude is actually BETTER than
the simulation shows. **Simulation results are therefore conservative** — real flights should
produce equal or better estimates.

### Spatial Clustering

When multiple targets exist on the ground, observations are grouped into clusters by GPS
distance. Observations within `CLUSTER_THRESHOLD_M` (default 30m, configurable with
`--cluster-dist`) of an existing cluster get added to it. Otherwise, a new cluster is created.

Each cluster maintains its own rolling 50, total average, and Kalman filter independently.
Clusters get permanent IDs (never shift when others are classified/removed).

### Operational Flow (First Flight)

```
1. Fly search pattern manually at 20-30m
2. CV detects something → observations accumulate → cluster estimate appears
3. Press N → drone flies to cluster's total average position, descends to 15m
4. Hover and observe:
   - Estimate refines (lower altitude = higher-weight observations)
   - Detection counter shows consistency: "Detections: 14 in cluster"
   - Camera feed shows what drone sees
5. Classify:
   - Y = real dummy → press L to land 7.5m away
   - I = item of interest → logged, estimate reset, resume flying
   - X = false positive → discarded, estimate reset, resume flying
6. If Y → L → drone flies to 7.5m north of estimate → auto-lands
```

### What to Watch Out For

1. **FOV calibration**: The one thing that MUST be right. Calibrate before flight.
2. **Wind**: Causes position oscillation. More observations help, but strong wind means
   the drone's reported GPS is noisier. ArduCopter's EKF handles this internally.
3. **Altitude reading**: Baro can drift. If altitude is wrong, GSD is wrong, estimate is
   wrong. Check altitude matches reality.
4. **Magnetic interference**: Bad compass → bad yaw → rotated estimates. Calibrate compass.
5. **Low detection rate at altitude**: If dummy is only detected in 10% of frames, estimates
   are sparse and noisy. Lower altitude or improve model.
6. **Sun glare / shadows**: Can cause false positives or missed detections. Test in actual
   flight conditions.

### Simulation Flags for Testing

```bash
python simple_simulator.py \
  --fps 4           \  # Limit CV to 4fps (match Pi speed)
  --tflite           \  # Use TFLite backend (match Pi)
  --gps-drift 2.5    \  # ±2.5m GPS random walk
  --alt-noise 1      \  # ±1m altitude noise
  --yaw-noise 3      \  # ±3° yaw noise
  --fov-error 5      \  # ±5% FOV calibration error
  --shake 5          \  # ±5px camera shake
  --cluster-dist 15  \  # 15m cluster grouping threshold
```

---

## Edge vs Offload: On-Board Pi Inference vs Ground Station Laptop

**Decision: On-board inference on Pi is the correct architecture. Do NOT put offloaded
inference in the flight control loop.**

### Research Summary (2026-03-11)

We investigated whether streaming video from Pi to the laptop and running faster inference
there (Ultralytics + GPU) would beat running TFLite on Pi. Key findings:

| Approach | End-to-end latency | FPS | WiFi needed? |
|----------|-------------------|-----|:---:|
| **Pi TFLite (current)** | **250ms** | 4 | No |
| Offload via MJPEG → laptop GPU | 200-250ms | 4-5 | Yes |
| Offload via H.264/GStreamer → laptop | 150-200ms | 10-15 | Yes |
| Pi + Coral USB TPU | >250ms (1-2 FPS) | 1-2 | Dead product — skip |
| **Pi + NCNN export** | **~83ms** | **12** | No |
| Pi + Hailo-8L ($70) | ~16ms | 60 | No |

**Key insight**: the network round-trip (encoding + WiFi + decoding) eats what you save on
compute. CMU's SteelEagle project (2024) measured this — their optimized offload loop was
380ms, worse than our on-board 250ms.

### Why On-Board Wins for Active Flight Control

1. **WiFi dropout during centering/landing is catastrophic.** Outdoors with terrain, multipath
   drops happen even at 50m. On-board inference keeps working regardless.
2. **4 FPS is adequate for our mission.** At hover (centering/descent), drone barely moves
   between frames. At 5 m/s search speed, 1.25m per frame — target is in view for ~25m
   ground width.
3. **Offload latency ≈ on-board latency.** Adding WiFi dependency for ~zero speed gain.

### Where Offload IS Useful

**Operator monitoring only.** Stream annotated video to laptop for situational awareness.
This is what `pi_flight.py` already does (MJPEG on port 8090). If WiFi drops, operator loses
video but drone continues safely. This is a display function, not a control function.

### Hybrid Architecture (Recommended)

```
Pi (on-board, safety-critical)     Laptop (monitoring, advisory)
├─ Camera capture                  ├─ Browser dashboard (pi_flight.py)
├─ TFLite inference (4 FPS)        ├─ MJPEG video stream
├─ GPS estimation + clustering     ├─ Operator confirms Y/N
├─ MAVLink flight commands         └─ Mission Planner (map + telemetry)
└─ Autonomous if WiFi drops
```

Pi handles all detection and control. Laptop is for the operator to watch and confirm.
WiFi dropout = operator blind but drone safe (RTL or hold position).

### If You Want Faster On-Board Inference (Future)

| Upgrade | Expected speedup | Effort | Cost |
|---------|-----------------|--------|------|
| NCNN export format | ~1.5-2x | Low | Free |
| INT8 quantization | ~2x | Low | Free |
| Coral USB TPU | **Dead product — skip** | - | - |
| Hailo-8L AI HAT+ | ~15x (16ms, 60 FPS) | Medium | $70 |

See "Inference Optimization" section below for details on each approach.

### References

- CMU SteelEagle (2024): drone video stream latency benchmarks
- CMU OODA Loop of Cloudlet-based Autonomous Drones (2024)
- CoDrone (2024): hybrid edge/cloud drone navigation
- DeepBrain (2020): cloud computation offloading for drones evaluation

---

### SAR Industry Best Practice (Confirmed by Research)

The pixel-to-GPS projection with weighted averaging approach used here is the **standard
method** in commercial SAR drone systems. Key findings:
- 5-10m accuracy is considered "good enough" for SAR (guides ground teams to area)
- 1-3m is excellent (direct approach possible)
- Sub-metre is overkill for SAR operations
- Multiple observations from different positions/altitudes improve accuracy
- Lower altitude observations are more valuable (smaller GSD)
- FOV calibration is the primary source of systematic error
- ArduCopter's EKF provides ±1-2m navigation accuracy with standard GPS

---

## Inference Optimization — Full Research (2026-03-11)

Comprehensive benchmarks and research into the fastest possible inference on Raspberry Pi 5.
All numbers verified against published benchmarks and academic papers.

### Master Comparison Table

| Approach | Pi 5 Speed | FPS | mAP | Cost | Effort | Status |
|----------|-----------|-----|-----|------|--------|--------|
| **YOLOv8n TFLite FP32 (current)** | **250ms** | **4** | 37.3 | - | - | Working |
| YOLOv8n TFLite INT8 | 250ms | 4 | ~37 | Free | Low | **No speedup — skip** |
| YOLOv8n ONNX Runtime | ~170ms | 6 | 37.3 | Free | Medium | Untested on Pi |
| **YOLOv8n NCNN** | **~83ms** | **12** | **37.3** | **Free** | **Low-Med** | **Best free upgrade** |
| **YOLO11n NCNN** | **~80ms** | **12** | **39.5** | **Free** | **Low-Med** | **Recommended** |
| **YOLO26n NCNN** | **~68ms** | **15** | **40.1** | **Free** | **Low-Med** | **Best accuracy+speed** |
| YOLO26n OpenVINO | ~71ms | 14 | 40.1 | Free | Medium | Alternative to NCNN |
| EfficientDet Lite0 INT8 | ~78ms | 13 | 25.6 | Free | Medium | Lower accuracy |
| NanoDet-Plus NCNN | ~30ms | 33 | 30-34 | Free | Medium | Ultra-fast, low accuracy |
| YOLO-Fastest V2 NCNN | ~25ms | 40 | 19-24 | Free | Hard | Too inaccurate for SAR |
| SSD MobileNet V1 INT8 | ~40ms | 25 | 21 | Free | Medium | Too inaccurate for SAR |
| RT-DETR (transformer) | Too slow | <1 | 53+ | Free | - | Needs GPU — skip on Pi |
| **Hailo-8L AI HAT+** | **~16ms** | **60** | **same** | **$70** | **Medium** | **Best hardware upgrade** |
| Hailo-8 AI HAT+ (26T) | ~10ms | 100+ | same | $110 | Medium | Overkill |
| Coral USB TPU | >250ms | 1-2 | - | $60 | High | **Dead — DO NOT BUY** |

### Tier 1: Free Software Optimizations

#### NCNN Export (PRIMARY RECOMMENDATION)

NCNN is Tencent's inference framework, purpose-built for ARM with hand-tuned NEON SIMD kernels.
It is consistently the fastest CPU-only format on Raspberry Pi across all benchmarks.

**How to export (on laptop):**
```bash
yolo export model=best.pt format=ncnn
# Creates: best_ncnn_model/ folder with .param and .bin files
```

**How to run (on Pi with ultralytics):**
```python
from ultralytics import YOLO
model = YOLO("best_ncnn_model")
results = model.predict(source=frame, conf=0.4)
```

**Practical concerns for our project:**
- Requires `ultralytics` installed on Pi (pulls PyTorch, ~2GB)
- Python 3.13 compatibility unverified (tested on 3.11)
- Alternative: `pip install ncnn` for lightweight bindings (but need custom postprocessing)
- First inference after load takes ~17s (warmup). Do a dummy inference before mission loop.
- INT8 quantization does NOT help with NCNN on ARM — use FP32 only.

**Benchmarked numbers (Ultralytics official, Pi 5, 640x640):**
- YOLO26n NCNN: 68ms | TFLite: 251ms → **3.7x faster**
- YOLO26s NCNN: 168ms | TFLite: 805ms → **4.8x faster**

#### YOLO11n / YOLO26n (Model Architecture Upgrade)

Newer YOLO architectures are faster AND more accurate than YOLOv8n:
- YOLO11n: 22% fewer params, 39.5 mAP (vs 37.3), ~80ms NCNN
- YOLO26n: latest, 40.1 mAP, ~68ms NCNN — **15% faster than YOLO11n**

Same Ultralytics training pipeline. To retrain custom model on newer architecture:
```bash
yolo detect train model=yolo11n.pt data=dataset.yaml epochs=100
yolo export model=runs/detect/train/weights/best.pt format=ncnn
```

#### Smaller Input Resolution

Reducing from 640x640 to 480x480 or 320x320 gives ~1.5-2x additional speedup.
**CAUTION**: At 30m altitude, dummy is ~46px tall at 640x640 → ~23px at 320x320.
Detection becomes unreliable below ~30px. Test carefully before committing.

```bash
yolo export model=best.pt format=ncnn imgsz=480  # compromise
```

### Tier 2: Hardware Accelerators

#### Hailo-8L AI HAT+ ($70) — RECOMMENDED FUTURE UPGRADE

The official Raspberry Pi AI accelerator. 13 TOPS via PCIe.

**Real-world Pi 5 numbers:**
- YOLOv8n: ~60 FPS (~16ms) single stream
- YOLOv8s: ~80 FPS (~12ms) — more accurate model, STILL faster than current
- YOLOv8m: ~16 FPS (~62ms) — medium model feasible

**Setup:**
1. Plug AI HAT+ onto Pi 5 PCIe connector
2. `sudo apt update && sudo apt full-upgrade`
3. Enable PCIe Gen3: `sudo raspi-config` → Advanced → PCIe Speed → Yes
4. Clone hailo-rpi5-examples, run installer
5. Convert model: ONNX → Hailo DFC → .hef file (pre-converted YOLOv8 available in Model Zoo)

**For custom models:** Export to ONNX, use Hailo Dataflow Compiler (runs on x86 Linux) to
produce .hef file. Pre-converted YOLOv8n/s/m available in Hailo Model Zoo — no conversion
needed for COCO person detection.

**vision.py integration:** Would need a third backend (Hailo HEF) alongside TFLite and
Ultralytics. Same `detect_in_image()` interface.

**Verdict:** Best upgrade path post-first-flight. $70 for 15x speedup. Official Pi product
with active support. But adds complexity — don't rush before flight day.

#### Coral USB TPU — DO NOT BUY

- Discontinued by Google (July 2025, repo archived)
- Only 1-2 FPS on YOLO (worse than CPU-only TFLite!)
- YOLOv8 layers partially fall back to CPU, USB transfer overhead kills it
- PyCoral only supports Python 3.6-3.9 (your Pi runs 3.13)
- Software ecosystem is dead, no updates

#### Alternative Ultra-Lightweight Models (Niche Use)

If you ever need 30+ FPS and can tolerate lower accuracy:
- **NanoDet-Plus NCNN**: ~30ms, 33 FPS, 980KB model, mAP ~30-34
- **YOLO-Fastest V2 NCNN**: ~25ms, 40 FPS, 666KB model, mAP ~19-24

These are too inaccurate for detecting a small dummy from 15-30m altitude but could work
for close-range (<10m) or large/distinctive targets. Training pipelines are more complex
than Ultralytics (NanoDet: PyTorch configs, YOLO-Fastest: Darknet C code).

### Action Plan (Priority Order)

**Before first flight (current TFLite is fine):**
1. Fly with current 4 FPS setup — it works, it's tested, don't risk changes

**After first flight (optimize based on real data):**
1. [ ] Export current best.pt to NCNN on laptop: `yolo export model=best.pt format=ncnn`
2. [ ] Test `pip install ultralytics` on Pi (Python 3.13 compatibility check)
3. [ ] If ultralytics works: benchmark NCNN vs TFLite on Pi with tests/hardware/benchmark.py
4. [ ] If 3x speedup confirmed: add NCNN backend to vision.py
5. [ ] Train YOLO11n or YOLO26n on your custom data for additional accuracy gain
6. [ ] Consider Hailo-8L ($70) if project continues and you want 60 FPS

### Sources

- Ultralytics Raspberry Pi Guide (official benchmarks): docs.ultralytics.com/guides/raspberry-pi/
- Ultralytics NCNN Export Docs: docs.ultralytics.com/integrations/ncnn/
- Qengineering YoloV8-ncnn-Raspberry-Pi-4 (bare-metal C++): github.com/Qengineering
- CMU SteelEagle (2024): drone video stream latency benchmarks
- Benchmarking Deep Learning on Edge Devices (arXiv 2409.16808)
- Real-Time Object Detection with Quantized YOLO on RPi5 (Research Square)
- YOLO11 on Raspberry Pi (LearnOpenCV)
- Jeff Geerling: Testing Pi AI Kit (13 TOPS, $70)
- Seeed Studio: Pi AI Kit vs Coral comparison
- Hailo Community: YOLOv8n real performance on Pi 5
- NanoDet GitHub: RangiLyu/nanodet
- Google Coral archived: PyCoral Python 3.13 incompatible
