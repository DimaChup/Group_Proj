# Video Analysis Setup & Guide

## Quick Start

```bash
# Activate test_env (has Ultralytics + TFLite)
test_env\Scripts\activate

# Run video detection test (use 30fps video ONLY)
python tests/laptop/video_test.py "RealVideo/DJI_0001_1456x1088_cropped_30fps.mp4" --model best.tflite

# Compare two models side by side
python tests/laptop/video_test_compare.py "RealVideo/DJI_0001_1456x1088_cropped_30fps.mp4"
```

---

## Available Videos

All DJI flight recordings are in `RealVideo/`:

| File | Resolution | FPS | Use for analysis? | Notes |
|------|-----------|-----|-------------------|-------|
| **DJI_0001_1456x1088_cropped_30fps.mp4** | 1456x1088 | 30 | **YES — use this** | SRT synced, correct altitude/GPS |
| DJI_20260311172332_0001_V.MP4 | 3840x2160 | 30 | Original only | Raw 4K, too large for detection |
| DJI_0001_1456x1088_6fps.mp4 | 1456x1088 | 6 | NO | SRT out of sync |
| DJI_0001_1456x1088_cropped_6fps.mp4 | 1456x1088 | 6 | NO | SRT out of sync |
| DJI_0001_1456x1088_padded_6fps.mp4 | 1456x1088 | 6 | NO | SRT out of sync |
| DJI_0001_1456x819_6fps.mp4 | 1456x819 | 6 | NO | SRT out of sync |
| DJI_0001_640x360_6fps.mp4 | 640x360 | 6 | NO | SRT out of sync, low res |
| DJI_20260311172721_0002_V.MP4 | 3840x2160 | 30 | Separate flight | Different flight, has own .SRT |

**SRT telemetry files:**
- `DJI_20260311172332_0001_V.SRT` — GPS, altitude, speed for flight 1
- `DJI_20260311172721_0002_V.SRT` — GPS, altitude, speed for flight 2

---

## CRITICAL: SRT Sync Explanation

DJI SRT telemetry files contain one entry per frame at the **original recording framerate (30fps)**. The SRT for flight 1 has **6854 entries** matching the 6854 frames of the original 30fps video.

**Why 6fps breaks:**
- A 6fps version has only ~1370 frames (every 5th frame kept)
- But the SRT still has 6854 entries
- Frame N in the 6fps video should map to SRT entry N*5, but video_test.py reads SRT entry N
- Result: altitude reads wrong (e.g., shows 15m when actually at 40m), GPS coordinates wrong
- **All GPS estimation and altitude overlays will be incorrect with 6fps video**

**Rule: Always use `DJI_0001_1456x1088_cropped_30fps.mp4` for any analysis that uses telemetry.**

The 6fps versions were created for quick visual preview only (smaller file, faster scrubbing). They are fine for eyeballing detections but NOT for quantitative analysis.

---

## video_test.py — Full Video Replay

```bash
python tests/laptop/video_test.py "RealVideo/DJI_0001_1456x1088_cropped_30fps.mp4" --model best.tflite
```

### Windows

The script opens 4 separate windows (all resizable, proportions preserved):

1. **Video Detection Test** — Main video with:
   - Detection bounding boxes (green) with confidence labels
   - Scale bar showing 1m reference at current altitude
   - Telemetry overlay: altitude, speed, GPS, frame number
   - Tiling grid overlay (when tiling enabled)

2. **Latest Detection** — Snapshot of most recent inference:
   - Clean detection image with bounding box
   - Text info below: confidence, altitude, frame number

3. **Best Detection (most central)** — Best detection found so far:
   - The detection closest to frame center (most reliable for GPS estimation)
   - Left-click twice to measure distance on this image

4. **Target GPS Estimates** — Two scatter plots:
   - Left: estimates colored by distance from center (closer = more accurate)
   - Right: estimates colored by altitude (shows detection altitude range)

### Keyboard Controls

| Key | Action |
|-----|--------|
| SPACE | Pause / resume playback |
| T | Toggle tiling on/off (tiling = 640px tiles with 25% overlap, ~6 tiles per frame) |
| A | Skip 5 seconds backward |
| D | Skip 5 seconds forward |
| + / = | Speed up playback |
| - | Slow down playback |
| Q | Quit |

### Mouse Controls

| Action | What it does |
|--------|-------------|
| Right-click twice on main video | Measure distance between two points (meters at current altitude) |
| Middle-click on main video | Clear measurement line |
| Drag window corner | Resize (proportions preserved) |

### Tiling Mode

When tiling is ON (press T):
- Frame is split into ~6 overlapping 640x640 tiles (25% overlap)
- Each tile is run through the model independently
- Better for detecting small objects at altitude (dummy might be <20px in full frame)
- Slower (~1000ms per frame on laptop CPU vs ~200ms for single pass)
- Detection boxes are mapped back to full-frame coordinates

### Command-Line Options

```bash
python tests/laptop/video_test.py VIDEO_PATH [--model MODEL_PATH] [--conf THRESHOLD]
```

| Flag | Default | Description |
|------|---------|-------------|
| `--model` | `best.tflite` | Path to TFLite model |
| `--conf` | `0.3` | Confidence threshold |

---

## video_test_compare.py — A/B Model Comparison

```bash
python tests/laptop/video_test_compare.py "RealVideo/DJI_0001_1456x1088_cropped_30fps.mp4"
```

Plays the same video with two models loaded. Press **M** to switch between them live. Useful for comparing:
- Original `best.tflite` vs retrained `cv_models/sar_v2_1088/best.tflite`
- Different confidence thresholds
- Detection consistency across models

The current model name is shown in the window title / overlay.

---

## FOV Calibration

### Current Calibration (2026-03-16)

| Parameter | Value | Method |
|-----------|-------|--------|
| HFOV | 54.4 deg | Calibrated from DJI cropped video |
| Focal length | 1416 px (+/- 41) | 9 samples across 15-50m |
| Frame size | 1456x1088 | Cropped from 3840x2160 |
| Known reference | 1.8m dummy height | Measured on ground |
| Validation | Dummy measures 1.7-1.9m at all altitudes | Consistent within noise |

### How to Recalibrate

```bash
python tools/fov_calibrate_video.py "RealVideo/DJI_0001_1456x1088_cropped_30fps.mp4" --known-height 1.8
```

**Procedure:**
1. Scroll through video to find frames where the dummy is visible
2. At each altitude, right-click the **top** of the dummy, then right-click the **bottom**
3. The tool records the pixel height and altitude for each sample
4. Repeat at multiple altitudes (15m, 25m, 35m, 50m) for robust calibration
5. Press Q to see results (focal length, HFOV, per-sample errors)

**Important:** This FOV is for the **cropped DJI video** (1456x1088 from 3840x2160 4K). The Pi camera (IMX296) has a different FOV — use `tests/calibration/fov_calibrate.py` for Pi camera calibration.

---

## Scale Bar and Measure Tool

### Scale Bar
The main video window shows a 1m scale bar in the bottom-left corner. This uses:
- Current altitude from SRT telemetry
- Calibrated FOV (54.4 deg HFOV)
- Frame width (1456 px)

Formula: `pixels_per_meter = focal_length_px / altitude_m`

### Measure Tool
Right-click twice on the main video to measure real-world distance between two points:
1. First right-click: sets start point (green dot)
2. Second right-click: sets end point (red dot), shows distance in meters
3. Distance calculated using altitude and FOV: `distance_m = pixel_distance / pixels_per_meter`
4. Middle-click to clear the measurement

---

## Models Available for Testing

| Model | Location | Size | Training | Notes |
|-------|----------|------|----------|-------|
| best.tflite | project root | 3.3MB | v1: 200 synthetic 640x640 | Original, current active model |
| **sar_v2_1088** | cv_models/sar_v2_1088/ | 11.7MB | **v2: 300 syn + 16 real + 50 neg at 1088** | **Best model, retrained** |
| sar_640 | cv_models/sar_640/ | ~12MB | Improved synthetic at 640 | Earlier experiment |
| sar_1280 | cv_models/sar_1280/ | ~13MB | Improved synthetic at 1280 | Earlier experiment |
| human.tflite | models/ | 13MB | COCO pretrained (80 classes) | Person detector backup |

### Testing a different model:
```bash
# With video_test.py
python tests/laptop/video_test.py "RealVideo/DJI_0001_1456x1088_cropped_30fps.mp4" --model cv_models/sar_v2_1088/best.tflite

# With video_test_compare.py (edit model paths in script, or use --model flags)
python tests/laptop/video_test_compare.py "RealVideo/DJI_0001_1456x1088_cropped_30fps.mp4"
```

---

## Model Comparison Workflow

To systematically compare models:

1. **Run video_test.py with model A**, note: detection count, confidence range, false positives, altitude range of detections
2. **Run video_test.py with model B**, note same metrics
3. **Or use video_test_compare.py** to switch live with M key
4. Check GPS scatter plots — tighter cluster = more consistent model
5. Check detection at high altitude (>35m) — this is the hardest case

Key metrics to compare:
- **Detection rate**: how many frames have a detection?
- **Confidence range**: are detections high-confidence (>0.7) or borderline (0.3-0.5)?
- **False positives**: detections when dummy is NOT in frame
- **Max detection altitude**: highest altitude where dummy is reliably detected
- **GPS cluster tightness**: CEP50 of estimated target positions

---

## Troubleshooting

### "Altitude shows 0" or wrong values
- You are using a 6fps video. Switch to 30fps: `DJI_0001_1456x1088_cropped_30fps.mp4`

### No detections at all
- Check confidence threshold (try `--conf 0.2`)
- Check model path is correct
- Try enabling tiling (press T) — small objects may be missed in full-frame mode

### Very slow playback
- Tiling mode is ~5x slower than single-pass. Press T to toggle off.
- Detection runs on CPU (no GPU acceleration in TFLite on Windows)
- Expected: ~200ms single-pass, ~1000ms tiled per frame on laptop

### Scale bar looks wrong
- FOV may need recalibration if using a different video crop
- Run `tools/fov_calibrate_video.py` to recalibrate

### GPS estimates are scattered
- Normal for moving drone — GPS has 100-200ms latency causing ~1m error at 5m/s
- Detections from near-center of frame are most accurate
- Multiple passes and averaging improve accuracy

---

## Helper Modules (tests/laptop/video_tools/)

These are imported by video_test.py and video_test_compare.py:

| Module | Purpose |
|--------|---------|
| detect_fullres.py | Full-resolution single-pass detection |
| detect_tiling.py | Tiled detection (640px tiles with overlap) |
| video_tiling.py | Video frame tiling utilities |
| video_test_baseline.py | Baseline detection logic |
| zoom_detect_baseline.py | Zoom-based detection baseline |

These are internal modules — you should not need to run them directly.

---

## Working Configuration (verified 2026-03-16)

| Setting | Value | Notes |
|---------|-------|-------|
| Video | `DJI_0001_1456x1088_cropped_30fps.mp4` | MUST use 30fps for SRT sync |
| Resolution | 1456x1088 | Cropped from 3840x2160 DJI 4K |
| Model | `best.tflite` (3.3MB YOLOv8n) | Or `cv_models/sar_v2_1088/best.tflite` |
| Tiling | 640px, 25% overlap | ~6 tiles per frame, press T to toggle |
| FOV | 54.4 deg HFOV | Calibrated from 9 samples across 15-50m |
| Confidence | 0.3 | Default, catches most detections |
| Environment | `test_env` venv | Has Ultralytics backend for TFLite |
| Inference | ~200ms single / ~1000ms tiled | Laptop CPU |
