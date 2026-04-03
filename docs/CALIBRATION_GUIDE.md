# Calibration Guide

All calibrations that affect GPS estimation accuracy in the SAR drone system.
Run these before flight to ensure the drone can accurately estimate target positions.

---

## Quick Reference

| Calibration | Script | Output | Config Parameter | Current Value | Last Calibrated |
|-------------|--------|--------|------------------|---------------|-----------------|
| Lens distortion | `tests/calibration/lens_calibrate.py` | `calibration_data.npz` | `UNDISTORT_ENABLED` | `False` | 2026-03-11 (RMS 0.399) |
| FOV (bench) | `tests/calibration/fov_calibrate.py` | terminal output | `FOCAL_LENGTH_MM` | 5.46 | 2026-03-11 |
| FOV (video) | `tools/fov_calibrate_video.py` | terminal output | HFOV for video scripts | 54.4 deg | 2026-03-16 |
| FOV (in-flight) | `tests/calibration/alt_test.py` | terminal output | `FOCAL_LENGTH_MM` or `SENSOR_WIDTH_MM` | -- | Not yet done |
| GPS estimate | `tests/calibration/gps_estimate_calibrate.py` | terminal output | `FOCAL_LENGTH_MM` | 5.46 | Not yet done |
| GPS estimate (GUI) | `tests/calibration/gps_calibrate_gui.py` | terminal output | `FOCAL_LENGTH_MM` | 5.46 | Not yet done |
| GPS ground truth | `tests/calibration/gps_ground_truth.py` | `ground_truth_*.txt` | validates entire pipeline | -- | Not yet done |

---

## 1. Lens Distortion Calibration (Checkerboard)

Corrects barrel/pincushion distortion from the camera lens. Detections near frame edges
will have incorrect GPS estimates without this correction.

### Script

```bash
# Interactive (with display)
python tests/calibration/lens_calibrate.py

# Headless (Pi over SSH, auto-captures every 3s)
python tests/calibration/lens_calibrate.py --headless

# Custom checkerboard size (default: 13x8 inner corners for calib.io 14x9 board)
python tests/calibration/lens_calibrate.py --board 9x6

# Verify existing calibration (live undistorted feed)
python tests/calibration/lens_calibrate.py --load
```

### What You Need

- Printed checkerboard pattern on stiff cardboard (no warping)
- Recommended: calib.io 14x9 board with 28mm squares (has rounded corners for better detection)
- Camera (Pi camera or laptop webcam)

### Procedure

1. Print a checkerboard and mount it on flat cardboard
2. Run the script
3. Hold the checkerboard in front of the camera at various angles and positions
4. Press SPACE to capture when "BOARD FOUND" appears (green text)
5. Capture 10-20 images covering different angles, distances, and frame positions
6. Include captures where the board is near frame edges (distortion is worst there)
7. Press C to compute calibration
8. Review RMS error: < 0.5 is good, < 1.0 is acceptable

### Output

- **File**: `calibration_data.npz` in the project root
- **Contents**: `camera_matrix` (fx, fy, cx, cy), `dist_coeffs` (k1, k2, p1, p2, k3), `rms_error`, `image_size`
- **Where it goes**: `vision.py` auto-loads this file at startup and applies `cv2.remap()` to every frame (~1.5ms overhead)
- **Config**: Set `UNDISTORT_ENABLED = True` in `config.py` to enable undistortion

### When to Recalibrate

- Camera or lens changed
- Camera mount changed (different focal distance)
- File becomes corrupted (empty/zero-size file causes black frames -- delete it and re-run)

### Current Values

- Calibrated 2026-03-11 on Pi with IMX296 global shutter camera
- RMS reprojection error: 0.399
- Board used: calib.io 14x9 (13x8 inner corners), 28mm squares
- `UNDISTORT_ENABLED = False` in config.py (the NPZ on the Pi was corrupted; IMX296 distortion is minimal so this is optional)
- The calibration file stays on the Pi only (not committed to git)

### Notes

- If `calibration_data.npz` is empty or corrupted, vision.py will produce mangled frames. Delete the file and everything works fine without it.
- IMX296 is a global shutter sensor with minimal distortion. Undistortion is a nice-to-have, not critical.
- Cost: ~1.5ms per frame on Pi 5 (negligible compared to ~206ms inference).

---

## 2. FOV Calibration -- Bench (Ruler Method)

Determines the camera's focal length by measuring how wide the camera's view is at a known
height. This is the most important calibration for GPS estimation accuracy.

### Script

```bash
# With display (shows live camera feed with crosshair + edge markers)
python tests/calibration/fov_calibrate.py

# Headless (terminal prompts only, for SSH)
python tests/calibration/fov_calibrate.py --headless
```

**Quick version** (single measurement, simpler output):

```bash
python tests/calibration/fov_test_simple.py
python tests/calibration/fov_test_simple.py --headless
```

### What You Need

- Tape measure or ruler on the floor
- Camera (Pi camera or laptop webcam)
- Flat surface

### Procedure

1. Place a tape measure flat on the floor
2. Hold the camera pointing **straight down** at a known height (e.g. 50cm, 100cm, 150cm)
3. Look at the live feed (or mentally note) how much of the ruler is visible left-to-right edge
4. Press C to capture (or Q for manual entry mode)
5. Enter the camera height (cm) and visible ruler width (cm)
6. Repeat at 2-3 different heights for consistency verification
7. Press Enter with empty input when done

### The Math

```
FOCAL_LENGTH_MM = (SENSOR_WIDTH_MM * height_mm) / visible_width_mm
```

The script computes this for each measurement, checks consistency (spread < 0.3mm is excellent),
and shows the impact of miscalibration at flight altitudes.

### Output

- Terminal printout with calibrated `FOCAL_LENGTH_MM` value
- Consistency analysis across measurements (spread, std deviation)
- Error table at flight altitudes (10-30m)
- Optional `fov_capture.jpg` (press C during live view)

### Where the Value Goes

Update `config.py`:

```python
FOCAL_LENGTH_MM = 5.46  # calibrated YYYY-MM-DD
```

### When to Recalibrate

- Camera or lens changed
- Camera resolution changed (`IMAGE_W`, `IMAGE_H`)
- GPS estimates are consistently offset in one direction
- After changing camera mount or focus

### Current Values

- `SENSOR_WIDTH_MM = 5.02` (IMX296 datasheet, fixed)
- `FOCAL_LENGTH_MM = 5.46` (calibrated 2026-03-11, 92cm visible at 1m height)
- `IMAGE_W = 1456`, `IMAGE_H = 1088` (IMX296 native resolution)
- Horizontal FOV: ~49.3 degrees (computed from sensor width and focal length)

### Impact of Error

A 10% error in `FOCAL_LENGTH_MM` produces a 10% error in GPS estimation:

| Altitude | 10% focal error -> Position error |
|----------|-----------------------------------|
| 10m | ~0.9m |
| 20m | ~1.8m |
| 30m | ~2.7m |

---

## 3. FOV Calibration -- Video (DJI Footage)

Calibrates FOV using recorded DJI flight video with SRT telemetry. Click on a known-size
object (the dummy, 1.8m tall) at different altitudes to compute focal length in pixels.

### Script

```bash
python tools/fov_calibrate_video.py RealVideo/DJI_0001_1456x1088_cropped_30fps.mp4
python tools/fov_calibrate_video.py RealVideo/DJI_0001_1456x1088_cropped_30fps.mp4 --known-height 1.8
```

### What You Need

- DJI flight video with SRT telemetry (must use 30fps version for correct SRT sync)
- Video must show a known-size object at multiple altitudes

### Procedure

1. Run the script with the video path
2. Use the trackbar to scrub to a frame where the dummy is clearly visible
3. Right-click the TOP of the dummy, then right-click the BOTTOM
4. The script records pixel height + altitude from SRT telemetry, calculates focal length
5. Repeat at 3-5 different altitudes for consistency
6. Scroll wheel to zoom in for precise clicking
7. Press Q to quit and see final calibration

### The Math

```
focal_length_px = (pixel_height * altitude) / known_object_height
HFOV = 2 * atan(image_width / (2 * focal_length_px))
```

The `pixel * altitude` product should be constant across all altitudes. Spread > 5% suggests
measurement or altitude errors.

### Output

- Calibrated HFOV in degrees
- Focal length in pixels (with standard deviation)
- Consistency check: correlation between focal length and altitude (should be near 0)
- Per-sample breakdown table

### Where the Value Goes

This calibrates the FOV for video analysis scripts (`tests/laptop/video_test.py`,
`tests/laptop/video_test_compare.py`). Update the HFOV value in those scripts:

```python
fov_h = 54.4  # calibrated from DJI video
```

**Note**: This is for the DJI camera, not the Pi camera. The Pi camera FOV is calibrated
separately with `fov_calibrate.py` (bench method).

### When to Recalibrate

- Different video crop or resolution
- Different DJI camera or lens
- Different known object used for calibration

### Current Values

- DJI cropped video (1456x1088): HFOV = 54.4 degrees
- Focal length: 1416 px (+/- 41 px)
- Dummy height: 1.8m
- 9 samples across 15-50m altitude
- Calibrated 2026-03-16

### Important: SRT Sync

**MUST use the 30fps video** (`DJI_0001_1456x1088_cropped_30fps.mp4`). The 6fps videos have
a frame count mismatch with SRT entries and give wrong altitude data.

---

## 4. GPS Estimate Calibration (Focal Length from Detections)

Validates and corrects `FOCAL_LENGTH_MM` by placing a target at a known distance from the
camera and comparing the AI detection's estimated position against the actual position.

### Scripts

**Terminal version** (works over SSH):

```bash
python tests/calibration/gps_estimate_calibrate.py
python tests/calibration/gps_estimate_calibrate.py --no-mavlink     # manual altitude input
python tests/calibration/gps_estimate_calibrate.py --model cv_models/sar_v2_1088/best.tflite
```

**GUI version** (needs display, step-by-step with progress bar):

```bash
python tests/calibration/gps_calibrate_gui.py
python tests/calibration/gps_calibrate_gui.py --no-mavlink
python tests/calibration/gps_calibrate_gui.py --model cv_models/human.tflite
```

### What You Need

- Camera with AI model loaded (best.tflite or human.tflite)
- Target/dummy visible to the AI detector
- Tape measure
- Optional: mavproxy running (for altitude from Cube barometer)

### Procedure

1. Hold the camera pointing down at a known height (e.g. 1.5m)
2. Place the target at a known horizontal offset from directly below the camera
3. Enter height (m) and offset distance (m) when prompted
4. Script captures 10 frames, averages detection pixel positions
5. Computes what distance the current focal length predicts vs. actual
6. Calculates corrected focal length
7. Repeat 3-4 times at different distances
8. Press Ctrl+C (terminal) or Q (GUI) for weighted average summary

### The Math

```
estimated_distance = pixel_offset_from_center * height / focal_length_px
focal_length_px = pixel_offset * height / actual_distance
FOCAL_LENGTH_MM = focal_length_px * SENSOR_WIDTH_MM / IMAGE_W
```

Weighted average uses confidence / spread as weights (high confidence + low spread = more reliable).

### Output

- Per-measurement: actual vs estimated distance, error in metres and percent
- Corrected `FOCAL_LENGTH_MM` (weighted average across measurements)
- Expected accuracy table at flight altitudes (10-50m)

### Where the Value Goes

Update `config.py`:

```python
FOCAL_LENGTH_MM = X.XX  # calibrated YYYY-MM-DD (GPS estimate calibration)
```

### When to Recalibrate

- After changing camera, lens, or resolution
- After changing the AI model (detection center may shift slightly)
- If GPS estimates during passive_watch.py are consistently off
- After lens calibration changes

### GUI Controls (gps_calibrate_gui.py only)

| Key | Action |
|-----|--------|
| H | Enter camera height (type number + Enter) |
| D | Enter target distance (type number + Enter) |
| SPACE | Capture 10 frames |
| N | Next measurement |
| Q | Show summary / quit |

### Current Values

- `FOCAL_LENGTH_MM = 5.46` (from bench FOV calibration, not yet validated with this script)
- GPS estimate calibration has not been run in the field yet

---

## 5. GPS Ground Truth

Validates the **entire pipeline end-to-end**: camera detection -> pixel position -> FOV math
-> GPS estimate. Compares AI-estimated target position against the drone's actual GPS when
hovering directly over the target.

### Script

```bash
python tests/calibration/gps_ground_truth.py
python tests/calibration/gps_ground_truth.py --connect udpin:0.0.0.0:14550
python tests/calibration/gps_ground_truth.py --cv-estimate 51.4234 -2.6714
```

### What You Need

- Flying drone with GPS fix (or SITL)
- mavproxy running
- Known target position on the ground
- CV estimate from passive_watch.py (optional, enter with `--cv-estimate` or press E)

### Procedure

1. Run passive_watch.py first to build a CV estimate of the target position
2. Start this script (alongside or after passive_watch)
3. Fly the drone directly over the target
4. Hover for 5+ seconds to let GPS settle
5. Press T to mark the current GPS as ground truth
6. Repeat from 3-5 different passes for a robust average
7. If you have a CV estimate, enter it with `--cv-estimate LAT LON` or press E
8. Press Q to quit and see summary

### Controls

| Key | Action |
|-----|--------|
| T | Mark current GPS as ground truth |
| E | Enter CV estimate manually (lat lon) |
| R | Reset all marks |
| Q | Quit and show summary |

### Output

- **File**: `ground_truth_YYYYMMDD_HHMMSS.txt`
- **Contents**: All ground truth marks, average position, GPS spread (max/mean), CV estimate error
- **Terminal**: Live GPS display with satellites, fix type, altitude

### Where the Value Goes

This script does not directly produce a config value. It validates the accuracy of the
full GPS estimation pipeline. If the error is large (> 5m), investigate:

1. FOV calibration (`FOCAL_LENGTH_MM`) -- re-run bench or estimate calibration
2. GPS timing lag (100-200ms latency at 5m/s = 1m error along flight direction)
3. Camera tilt (not pointing straight down)
4. Altitude accuracy (barometer drift)

### When to Run

- After completing FOV and lens calibration
- During flight testing (Step 3: passive flight)
- After any change to `FOCAL_LENGTH_MM`, `SENSOR_WIDTH_MM`, or `IMAGE_W`/`IMAGE_H`

### Current Values

- Not yet run in the field
- Expected accuracy: CEP50 ~2-3m at 30m altitude (from DJI video analysis)
- GPS timing lag contributes ~1m error at 5m/s flight speed

### Note

This script requires a Unix terminal for keyboard input (Pi or WSL). On Windows, keyboard
input is not supported (use SITL + WSL instead).

---

## 6. Altitude Test (In-Flight FOV Validation)

Validates bench FOV calibration at real flight altitudes using barometric altitude from the
Cube. Catches errors that bench calibration cannot (barometric drift, camera vibration).

### Script

```bash
# Auto-detect connection
python tests/calibration/alt_test.py

# Explicit connection
python tests/calibration/alt_test.py tcp:127.0.0.1:5762
python tests/calibration/alt_test.py /dev/ttyAMA0 921600

# Headless
python tests/calibration/alt_test.py --headless
```

### What You Need

- Flying drone with Cube connected via mavproxy (or SITL)
- Ground markers at known distances (placed before takeoff)
- Camera (for live view, optional)

### Procedure

1. Before takeoff: place 2-3 markers on the ground at known distances apart
2. Take off and hover at first altitude (e.g. 10m)
3. Press SPACE to record the barometric altitude
4. Enter the ground width visible in the camera (metres, estimated from markers)
5. Climb to second altitude (e.g. 20m), repeat
6. Press Q when done

### The Math

```
measured_FOV = 2 * atan((visible_width / 2) / altitude)
```

Compares measured FOV against config.py prediction. Consistency between altitudes validates
the calibration. Spread > 5 degrees between altitudes means re-measure.

### Output

- Measured FOV at each altitude vs config prediction
- Suggested `SENSOR_WIDTH_MM` or `FOCAL_LENGTH_MM` correction
- Corrected footprint table (5-30m altitudes)

### Where the Value Goes

If the in-flight FOV differs from config by > 2 degrees, update `config.py`:

```python
FOCAL_LENGTH_MM = X.XX  # corrected from in-flight calibration YYYY-MM-DD
# OR
SENSOR_WIDTH_MM = X.XX  # corrected from in-flight calibration YYYY-MM-DD
```

Only change ONE parameter -- keep the other at its known value (sensor width from datasheet
is more reliable, so prefer adjusting focal length).

### When to Run

- After bench FOV calibration, during first flight test
- If GPS estimates at altitude are consistently wrong despite good bench calibration
- After changing camera mount or focus

### Current Values

- Not yet run in flight
- Bench calibration: `FOCAL_LENGTH_MM = 5.46`, `SENSOR_WIDTH_MM = 5.02`

---

## Calibration Order

Run calibrations in this order for best results:

1. **Lens calibration** (once per camera, on the bench)
2. **FOV bench calibration** (on the bench, ruler + known height)
3. **GPS estimate calibration** (on the bench, target at known offset)
4. **Altitude test** (in flight, validates bench values at real altitude)
5. **GPS ground truth** (in flight, validates entire pipeline end-to-end)
6. **FOV video calibration** (post-flight, from DJI footage -- for video analysis only)

Steps 1-3 can be done indoors before any flight. Steps 4-5 require actual flight or SITL.

---

## Config Parameters Summary

All camera/optics parameters in `config.py`:

```python
SENSOR_WIDTH_MM = 5.02          # IMX296 datasheet (fixed, do not change unless sensor changes)
FOCAL_LENGTH_MM = 5.46          # Calibrated 2026-03-11 (92cm visible at 1m)
IMAGE_W = 1456                  # IMX296 native width
IMAGE_H = 1088                  # IMX296 native height
UNDISTORT_ENABLED = False       # Set True when valid calibration_data.npz exists
```

### How These Affect GPS Estimation

The pixel-to-ground conversion uses:

```
ground_sample_distance = (SENSOR_WIDTH_MM * altitude) / (FOCAL_LENGTH_MM * IMAGE_W)
ground_offset = pixel_offset_from_center * ground_sample_distance
```

| Parameter | Effect if wrong |
|-----------|----------------|
| `FOCAL_LENGTH_MM` too high | GPS estimates too close to drone (undershoot) |
| `FOCAL_LENGTH_MM` too low | GPS estimates too far from drone (overshoot) |
| `SENSOR_WIDTH_MM` wrong | Same effect as focal length error (inversely) |
| `IMAGE_W`/`IMAGE_H` wrong | Scaling error in pixel-to-ground conversion |
| Undistortion disabled | Edge detections shifted by 1-3 pixels (minor at flight altitude) |

---

## Troubleshooting

### GPS estimates consistently offset in one direction

- Re-run FOV bench calibration (`fov_calibrate.py`)
- Check camera is pointing straight down (tilt causes systematic bias)
- Check GPS timing lag: at 5m/s, 200ms lag = 1m error along flight direction

### GPS estimates scattered (high CEP)

- Check GPS satellite count (need 8+ for good accuracy)
- Average multiple passes over the target
- GPS timing lag causes diagonal spread in estimates

### calibration_data.npz causes black/mangled frames

- Delete the file: `rm calibration_data.npz`
- Set `UNDISTORT_ENABLED = False` in config.py
- Re-run lens calibration if you want undistortion

### Detection works on bench but not in flight

- This is not a calibration issue -- check altitude, exposure, motion blur
- See `docs/CV_GUIDE.md` for CV optimization

### FOV bench vs flight values disagree

- Bench calibration is usually more reliable (controlled conditions)
- In-flight measurements are approximate (hard to estimate visible ground width)
- If spread between altitudes is > 5 degrees, re-measure
- Prefer the bench value unless flight data is clearly better
