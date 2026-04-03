# Pre-Flight Calibration and Testing Sequence

**From "drone assembled" to "ready for main.py" -- follow in order, never skip steps.**

Each step builds on the previous one. A failure at any step means STOP and fix before continuing.
Print this document and tick off each checkbox at the field.

---

## Phase 1: Bench (Indoors, No Props)

Everything in this phase can be done indoors on a desk. No GPS needed, no flying.
Props OFF (or better, not attached).

---

### Step 1: Camera Test

**Purpose:** Verify the camera gives frames and colours are correct.

```bash
# On Pi:
source pienv/bin/activate
cd ~/dima/Group_Proj
python tests/laptop/test_camera.py
# Or headless (SSH):
python -c "import cv2; c=cv2.VideoCapture(0); ok,f=c.read(); print('OK' if ok else 'FAIL', f.shape if ok else ''); c.release()"
```

**Check:**
```
[ ] Camera opens without error
[ ] Frame shape is correct (1088, 1456, 3) for IMX296
[ ] Colours look natural (IMX296 outputs BGR -- no cvtColor needed)
[ ] No black/mangled frames
```

**Go/No-Go:** Camera must produce clear, correctly-coloured frames.

**If it fails:**
- `Camera not found` -- check ribbon cable, run `libcamera-hello` to test outside Python
- Black frames -- check `calibration_data.npz` is not corrupt (delete it if in doubt)
- Wrong colours -- do NOT add `cv2.cvtColor`; IMX296 outputs BGR despite RGB888 label
- Wrong resolution -- check `IMAGE_W`/`IMAGE_H` in config.py match camera native res

---

### Step 2: Lens Calibration (Optional)

**Purpose:** Correct barrel/pincushion distortion for edge detections. IMX296 has minimal distortion, so this step is optional.

```bash
# On Pi (with display):
python tests/calibration/lens_calibrate.py

# Headless (SSH, auto-captures every 3s):
python tests/calibration/lens_calibrate.py --headless

# Custom board (default is 13x8 inner corners for calib.io 14x9 board):
python tests/calibration/lens_calibrate.py --board 9x6
```

**What you need:** Printed checkerboard on stiff flat cardboard.

**Procedure:**
1. Hold checkerboard in front of camera at various angles and positions
2. Press SPACE when "BOARD FOUND" appears (green text)
3. Capture 10-20 images, including near frame edges
4. Press C to compute calibration

**Check:**
```
[ ] calibration_data.npz created in project root
[ ] RMS reprojection error < 0.5 (good) or < 1.0 (acceptable)
[ ] Verify with: python tests/calibration/lens_calibrate.py --load
```

**Go/No-Go:** RMS < 1.0 if you need undistortion. Otherwise skip this step entirely.

**If it fails:**
- Board not detected -- ensure flat surface, good lighting, try `--board 9x6` for different board
- RMS > 1.0 -- recapture with board at more diverse angles, ensure board is perfectly flat
- Corrupt NPZ causes black frames -- delete `calibration_data.npz`, set `UNDISTORT_ENABLED = False` in config.py

---

### Step 3: FOV Calibration (Bench)

**Purpose:** Determine FOCAL_LENGTH_MM for accurate GPS estimation. This is the MOST IMPORTANT calibration.

```bash
# On Pi:
python tests/calibration/fov_calibrate.py --headless

# Or the simpler version:
python tests/calibration/fov_test_simple.py --headless
```

**What you need:** Tape measure or ruler on a flat surface.

**Procedure:**
1. Place tape measure flat on the floor
2. Hold camera pointing **straight down** at a known height (e.g. 50cm, 100cm)
3. Note how many cm are visible edge-to-edge in the camera view
4. Enter height (cm) and visible width (cm) when prompted
5. Repeat at 2-3 different heights for consistency check

**Check:**
```
[ ] At least 2 measurements taken at different heights
[ ] Spread between measurements < 0.3mm (excellent) or < 0.5mm (acceptable)
[ ] Script reports FOCAL_LENGTH_MM = ____ (write it down)
[ ] Updated config.py: FOCAL_LENGTH_MM = ____
```

**Go/No-Go:** Measurements at different heights agree within 0.5mm. If spread is larger, re-measure (camera was probably not straight down).

**If it fails:**
- Inconsistent results -- ensure camera is perfectly vertical (use spirit level or phone inclinometer)
- Very different from 5.46 -- check SENSOR_WIDTH_MM is 5.02 (IMX296 datasheet)
- Impact of error: 10% focal length error = 10% GPS estimation error (2.7m at 30m altitude)

**Current known-good value:** `FOCAL_LENGTH_MM = 5.46` (calibrated 2026-03-11)

---

### Step 4: AI Model Test

**Purpose:** Verify the AI model loads and detects on a static image.

```bash
# Quick benchmark (50 inferences, timing + detection rate):
python tests/hardware/benchmark.py

# Or with a specific image:
python tests/hardware/benchmark.py dummy.png

# Test with the camera live:
python tests/laptop/test_cv.py --camera
```

**Check:**
```
[ ] Model loads without error (best.tflite)
[ ] Detection rate: ____/50 (should be 50/50 on test image)
[ ] Average confidence: ____ (should be > 0.8 on test image)
[ ] Average inference time: ____ms (expect ~200ms TFLite on Pi 5)
[ ] FPS: ____ (expect ~4-5 FPS on Pi 5 with TFLite)
```

**Go/No-Go:** Model loads, detects on test image with >0.5 confidence. Inference < 500ms.

**If it fails:**
- Model not found -- check `best.tflite` exists in project root
- No detections -- swap model: `cp cv_models/sar_v2_1088/best.tflite best.tflite`
- Very slow -- try NCNN backend: install `ncnn` package, vision.py auto-selects
- Import error on Pi -- ensure `ai-edge-litert` installed (replaces tflite-runtime on Python 3.13)

---

### Step 5: Cube Heartbeat and Commands

**Purpose:** Verify bidirectional communication between Pi and Cube.

**Prerequisites:** Mavproxy must be running in a separate terminal.

```bash
# Terminal 1 -- start mavproxy (keep running):
sudo /opt/mavlink/mavlink-venv/bin/mavproxy.py \
  --master=/dev/ttyAMA0 --baudrate=921600 --streamrate=10 \
  --out=udpout:127.0.0.1:14550 --out=tcpin:0.0.0.0:5762

# Terminal 2 -- run command test:
python tests/flight/0a_cube_commands.py
```

**Check:**
```
[ ] Mavproxy shows "heartbeat from" messages
[ ] Mode change test: PASS (GUIDED -> STABILIZE and back)
[ ] Arm command test: PASS (rejected on bench without GPS = still PASS, proves command reached Cube)
[ ] Parameter read test: PASS
[ ] Home position test: PASS
[ ] Buzzer test: PASS (listen for beeps from Cube)
[ ] Overall: >= 3/5 tests pass
```

**Go/No-Go:** At least 3/5 tests pass. Mode change and buzzer are the most important.

**If it fails:**
- No heartbeat -- check serial wiring (TX/RX, ground), baud rate 921600, `/dev/ttyAMA0` exists
- Commands rejected -- check mavproxy `--out=udpout:127.0.0.1:14550` matches config.py CONNECTION_STR
- See `docs/CONNECTIVITY.md` for full debugging guide

---

### Step 5b: Bench Mission Sequence

**Purpose:** Exercise the full mission command sequence (mode changes, arm, takeoff, waypoints, land) WITHOUT flying.

```bash
python tests/flight/0b_bench_mission.py              # skip arm (safe)
python tests/flight/0b_bench_mission.py --with-arm   # also try arming (will be rejected without GPS)
```

**Check:**
```
[ ] GUIDED mode switch: PASS
[ ] STABILIZE mode switch: PASS
[ ] LOITER mode switch: PASS
[ ] ARM command: PASS (rejection = PASS on bench)
[ ] TAKEOFF command: PASS (rejection = PASS on bench)
[ ] WAYPOINT command: PASS
[ ] LAND command: PASS
[ ] Return to STABILIZE: PASS
```

**Go/No-Go:** All mode switches succeed. Arm/takeoff rejections are expected on bench.

---

### Step 5c: Vision-to-GPS Pipeline Test

**Purpose:** Verify the full feedback loop: camera -> detect -> pixel-to-GPS -> guidance direction. ZERO commands sent.

```bash
python tests/flight/0c_feedback_test.py              # with display
python tests/flight/0c_feedback_test.py --headless   # SSH mode
```

**Procedure:** Print the dummy image and hold the camera above it at ~1m height.

**Check:**
```
[ ] AI detects the dummy in live camera feed
[ ] Pixel coordinates reported (should be near frame center when dummy is centered)
[ ] Guidance direction makes sense (UP/DOWN/LEFT/RIGHT relative to dummy position)
[ ] Metre offsets are reasonable for the height (~0.5m offset at 1m height = correct)
[ ] Frame-to-frame drift < 0.5m when stationary
[ ] GPS estimate changes when you move the camera sideways
```

**Go/No-Go:** Detections appear, guidance directions are correct, drift < 0.5m.

**If it fails:**
- No detections -- go back to Step 4
- Wrong directions -- check FOCAL_LENGTH_MM (Step 3)
- Large drift -- check image resolution matches `IMAGE_W`/`IMAGE_H` in config.py

---

### Step 6: Servo Test (If Applicable)

**Purpose:** Verify payload release servo responds to PWM commands.

```bash
python tests/flight/0f_servo_test.py           # interactive (confirm each position)
python tests/flight/0f_servo_test.py --auto    # automated full sequence
python tests/flight/0f_servo_test.py --channel 10  # custom channel
```

**Check:**
```
[ ] CLOSE position: servo moves, click/whir audible
[ ] PARTIAL position: servo moves to intermediate
[ ] FULL position: servo moves to full open
[ ] Deploy sequence (3s -> partial -> 3s -> full -> close): all positions work
```

**Go/No-Go:** All 3 positions respond. If no servo, skip this step.

**If it fails:**
- No movement -- check channel matches `SERVOx_FUNCTION` in Mission Planner
- Check AUX rail has power (BEC connected)
- Check servo wiring: signal (white/orange), V+ (red), GND (brown/black)

---

### Step 7: RC Override Test

**Purpose:** Prove that the RC transmitter ALWAYS overrides Python scripts.

```bash
# Start any script that sends commands:
python tests/flight/0a_cube_commands.py
# OR
python pi_flight.py --fps 4
```

**Procedure:**
1. With script running, flip RC to STABILIZE
2. Check Mission Planner: mode should show STABILIZE (not what the script wants)
3. Flip RC back to GUIDED
4. Script should be able to send commands again

**Check:**
```
[ ] RC to STABILIZE overrides script commands
[ ] Mission Planner confirms mode change matches RC
[ ] Script cannot fight the RC (pilot always wins)
[ ] Flipping back allows script to resume
```

**Go/No-Go:** RC ALWAYS wins. If the script can override the RC, do NOT fly.

---

## Phase 2: Outdoors (No Props)

Move the assembled drone outdoors. Props still OFF. Need clear sky view for GPS.

---

### Step 8: GPS Fix

**Purpose:** Verify GPS gets a 3D lock with sufficient satellites.

```bash
python tests/hardware/gps_test.py
```

**Check:**
```
[ ] GPS_RAW_INT messages arriving (not "no GPS data")
[ ] fix_type = 3 (3D fix) -- may take 1-5 minutes cold start
[ ] Satellites >= 8 (minimum 6 for safe flight)
[ ] HDOP < 2.0 (good accuracy)
[ ] Here 3+ LED = flashing GREEN (not blue)
[ ] Lat/Lon values look reasonable for your location
```

**Go/No-Go:** fix_type = 3 AND satellites >= 8. Do NOT fly with < 6 satellites.

**If it fails:**
- Satellites = 0 -- you are indoors or GPS antenna is blocked/disconnected
- fix_type stays at 0 or 1 -- move to more open area, away from buildings/trees
- Takes > 15 minutes -- power cycle for cold start, check GPS_TYPE parameter in Mission Planner
- Here 3+ LED stays blue -- no lock yet, keep waiting
- Check GPS wiring and configuration with `docs/CONNECTIVITY.md`

---

### Step 9: GPS Estimate Calibration

**Purpose:** Validate that FOCAL_LENGTH_MM gives correct GPS estimates by placing a target at a known position and comparing.

```bash
# Terminal version (works over SSH):
python tests/calibration/gps_estimate_calibrate.py
python tests/calibration/gps_estimate_calibrate.py --no-mavlink   # manual altitude input

# GUI version (needs display):
python tests/calibration/gps_calibrate_gui.py
```

**Procedure:**
1. Hold camera pointing down at known height (e.g. 1.5m)
2. Place dummy at a known horizontal offset from directly below camera (e.g. 0.5m to the side)
3. Enter height (m) and offset distance (m) when prompted
4. Script captures 10 frames, computes estimated vs actual distance
5. Repeat 3-4 times at different offsets
6. Press Ctrl+C for weighted average summary

**Check:**
```
[ ] Estimated distance matches actual within 15%
[ ] Corrected FOCAL_LENGTH_MM: ____ (compare with bench value from Step 3)
[ ] If correction > 10%, update config.py with new value
```

**Go/No-Go:** Estimated distance within 20% of actual. If worse, re-run FOV bench calibration (Step 3).

**If it fails:**
- Large error (>30%) -- FOCAL_LENGTH_MM is wrong, re-run Step 3 more carefully
- Inconsistent across measurements -- camera tilt, move it to be more vertical
- No detections -- go back to Step 4, check model works outdoors

---

### Step 10: Compass and Heading Check

**Purpose:** Verify heading/yaw matches a known direction (affects GPS estimate bearing).

```bash
# Use diagnostics to see live heading:
python tests/diagnostics/diagnostics.py

# Or check in Mission Planner: Flight Data -> heading display
```

**Procedure:**
1. Point the drone's nose toward a known direction (e.g. use phone compass for North)
2. Read heading from diagnostics or Mission Planner

**Check:**
```
[ ] Heading approximately matches known direction (within 10 degrees)
[ ] Heading changes when you rotate the drone
[ ] No erratic compass jumps (if jumps: calibrate compass in Mission Planner)
```

**Go/No-Go:** Heading is consistent and within 10 degrees of known direction. Compass calibration needed if erratic.

**If it fails:**
- Erratic readings -- calibrate compass in Mission Planner (Initial Setup -> Mandatory Hardware -> Compass)
- Consistent offset -- check COMPASS_DEC (magnetic declination) in Mission Planner
- Not changing when rotated -- wrong compass source selected, check COMPASS_USE parameters

---

## Phase 3: Progressive Flights

Props ON. Battery connected. RC pilot ready with kill switch. Follow the numbered order strictly.

**Safety rules for ALL flight steps:**
- RC pilot's hand is ALWAYS on the kill switch (STABILIZE mode switch)
- Spotter watches for obstacles, people, and drone behaviour
- Brief everyone on abort procedure: RC to STABILIZE = instant manual control
- First flight of the day: hover at 2m for 30s, check stability before climbing

---

### Step 11: Mission Planner AUTO Flight (No Custom Code)

**Purpose:** Prove the drone flies, GPS navigation works, RTL works. YOUR CODE IS NOT INVOLVED.

**Procedure:**
1. In Mission Planner: Plan tab -> add 4 waypoints in a square, 10-15m altitude
2. Upload waypoints to Cube (Write WPs button)
3. Arm via RC transmitter
4. Switch to AUTO mode on RC
5. Watch drone fly the square pattern
6. Let it complete and RTL, or switch to RTL manually

```
[ ] Waypoints uploaded to Cube
[ ] Drone arms and takes off
[ ] Flies to first waypoint and follows the pattern
[ ] GPS track in Mission Planner matches planned route
[ ] Drone stable in flight (no oscillation, no toilet-bowling)
[ ] RTL lands within 2m of launch point
```

**Go/No-Go:** Drone completes the pattern and lands safely. Stable flight, good GPS track.

**If it fails:**
- Won't arm -- check pre-arm messages in Mission Planner (GPS lock? battery? calibration?)
- Toilet-bowling -- compass interference, needs compass calibration away from metal
- Drifts badly -- poor GPS, wait for more satellites, check HDOP < 2.0
- Oscillation -- PID tuning needed (out of scope, use Mission Planner auto-tune)
- **Do NOT continue to Step 12 until this passes**

---

### Step 12: Waypoint Script (Your Code, No CV)

**Purpose:** Prove your MAVLink commands (arm, takeoff, GUIDED waypoints, RTL) work on real hardware. No camera, no AI.

```bash
# ALWAYS dry-run first:
python tests/flight/2_waypoints.py --dry-run

# Then real flight:
python tests/flight/2_waypoints.py --alt 10
# Or with custom waypoints:
python tests/flight/2_waypoints.py --alt 10 --wp 51.4234,-2.6710 --wp 51.4238,-2.6695
```

**Check:**
```
[ ] Dry-run prints sensible waypoints and distances
[ ] Drone arms via script
[ ] Takes off to target altitude (10m)
[ ] Navigates to each waypoint in GUIDED mode
[ ] Holds at each waypoint for 3s
[ ] RTL lands safely at launch point
[ ] Ctrl+C triggers RTL (test emergency exit)
```

**Go/No-Go:** Drone completes all waypoints and lands safely. Script commands match expected behaviour.

**If it fails:**
- Arm rejected -- check GPS fix (Step 8), battery voltage, pre-arm messages
- Takes off but won't navigate -- check CONNECTION_STR in config.py matches mavproxy output
- Goes to wrong location -- check waypoints.json coordinates (use draw_waypoints.py on laptop)
- Ctrl+C doesn't trigger RTL -- restart mavproxy, check UDP port
- **Do NOT continue to Step 13 until this passes**

---

### Step 13: Passive CV Flight (Pilot Flies, Pi Detects, ZERO Commands)

**Purpose:** Measure real-world CV detection performance. Pi sends ZERO commands -- pilot has full authority.

```bash
# On Pi:
python tests/flight/1_passive_flight.py --headless --stream

# On laptop browser:
# http://<PI_IP>:8090
```

**Procedure:**
1. Place dummy on flat open ground, note its GPS from Mission Planner
2. Pilot takes off, hovers at 10m directly above dummy for 30s
3. Climb to 15m, hold 30s
4. Climb to 20m, hold 30s
5. Climb to 25m, hold 30s
6. Climb to 30m, hold 30s
7. Fly over dummy at 3 m/s, 5 m/s, 7 m/s at 15m altitude

**Check:**
```
[ ] Video stream visible in browser at http://PI_IP:8090
[ ] Detection overlay appears when dummy is in frame
[ ] Buzzer beeps on detection (audible confirmation)
```

**Record results:**

| Altitude | Detected? | Confidence | Notes |
|----------|-----------|------------|-------|
| 10m      |           |            |       |
| 15m      |           |            |       |
| 20m      |           |            |       |
| 25m      |           |            |       |
| 30m      |           |            |       |

| Speed @15m | Detected? | Motion blur? | Notes |
|------------|-----------|--------------|-------|
| 3 m/s      |           |              |       |
| 5 m/s      |           |              |       |
| 7 m/s      |           |              |       |

**After landing:**
```bash
# Review the CSV log:
cat passive_flight_log.csv
```

```
[ ] Max reliable detection altitude = ____m
[ ] Max detection speed = ____ m/s
[ ] False positives observed = ____ (note what triggered them)
[ ] Updated config.py: TARGET_ALT = ____ (max reliable detection altitude - 5m margin)
[ ] Updated config.py: SEARCH_SPEED_MPS = ____ (max detection speed - 1 m/s margin)
```

**Go/No-Go:** CV detects dummy reliably at some altitude with > 0.4 confidence.

**If it fails:**
- No detections at any altitude -- swap model: `cp cv_models/sar_v2_1088/best.tflite best.tflite`
- Low confidence -- lower threshold in vision.py (0.4 -> 0.3 -> 0.25)
- Only detects below 10m -- use lower search altitude, consider larger/brighter dummy
- Many false positives -- raise confidence threshold, consider `--smart-detect` flag in main.py
- **Do NOT continue to Step 14 until you have reliable detection at some altitude**

---

### Step 14: Autonomous Search + CV Logging Only (No Action on Detection)

**Purpose:** Fly the search pattern autonomously with CV running, but detection triggers logging only -- no mode switch, no descent, no landing.

```bash
# Dry-run first (no Cube needed):
python main.py --dry-run

# Then with --dry-run detection mode (AUTO + detect but don't act):
python tests/flight/3_auto_detect.py --dry-run --headless --stream

# Or full auto-detect (switches to GUIDED hover on detection, but no descent):
python tests/flight/3_auto_detect.py --headless --stream --timeout 15
```

**Check:**
```
[ ] Dry-run waypoints cover the intended search area
[ ] Drone flies the pattern autonomously (AUTO or GUIDED waypoints)
[ ] CV detections logged when flying over dummy
[ ] --dry-run mode: detections logged but ZERO commands sent
[ ] Full mode: switches to GUIDED hover on detection, resumes after timeout
[ ] GPS estimate of target is within 5m of known position
[ ] RC override to STABILIZE works at any time during auto flight
```

**Go/No-Go:** Search pattern covers the area. CV detects from search altitude. GPS estimate within 10m of actual.

**If it fails:**
- Pattern misses the dummy -- adjust SEARCH_AREA_GPS in config.py, re-run `--dry-run`
- Detects but GPS estimate is way off -- re-run FOV calibration (Step 3 or Step 9)
- Too many false positives triggering mode switch -- increase `--min-detections` or `--min-conf`
- Mode switch doesn't work -- check RC is in a mode the script can override (not STABILIZE)

---

### Step 15: Full Autonomous Mission

**Purpose:** Everything enabled -- search, detect, centre, descend, verify, land.

```bash
# Final dry-run verification:
python main.py --dry-run --model cv_models/sar_v2_1088/best.tflite

# Full mission:
python main.py --headless --model cv_models/sar_v2_1088/best.tflite --smart-detect

# Or with pi_flight.py dashboard:
python pi_flight.py --fps 4

# Laptop browser:
# http://<PI_IP>:8090
```

**Procedure (with pi_flight.py):**
1. Pilot flies over target area on RC
2. Detection alert appears in browser, cluster shown on GPS grid
3. Press N in browser to investigate (drone flies to estimate in GUIDED)
4. Drone descends, camera shows live view
5. Classify: Y (confirm dummy), I (item of interest), X (false positive)
6. If Y: press L to land 7.5m north of estimate
7. Measure actual landing distance from dummy

**Procedure (with main.py):**
1. Drone arms, takes off, flies lawnmower pattern
2. On detection: centres on target, descends to VERIFY_ALT
3. Operator confirms Y (real) or N (false positive) via terminal/browser
4. If Y: approaches and lands near target
5. If N: resumes search pattern

**Check:**
```
[ ] Drone completes search pattern at TARGET_ALT
[ ] Detection triggers investigation (centres on target)
[ ] Descent to verify altitude works smoothly
[ ] Operator can confirm/reject via browser or terminal
[ ] Landing within 10m of target
[ ] RC kill switch works at every phase
```

**Record:**
```
GPS estimate error:      ____m (compare estimate vs known dummy GPS)
Landing distance:        ____m (measure with tape from dummy to landing spot)
Total mission time:      ____min
Batteries used:          ____
False positives:         ____
```

---

## After All Testing: Record Results and Update Config

```
FOV calibration:
  FOCAL_LENGTH_MM = ____

CV performance:
  Max detection altitude   = ____m
  Max detection speed      = ____ m/s
  Avg confidence at best   = ____
  Inference FPS on Pi      = ____
  False positives          = ____

GPS estimation:
  CEP50 (50% of estimates within) = ____m
  Max error observed               = ____m

Landing accuracy:
  Landing distance from target     = ____m

Config updates:
  [ ] TARGET_ALT = ____
  [ ] VERIFY_ALT = ____
  [ ] SEARCH_SPEED_MPS = ____
  [ ] FOCAL_LENGTH_MM = ____
  [ ] Confidence threshold = ____ (in vision.py)

Commit and push:
  git add config.py && git commit -m "field calibration results" && git push
```

---

## Quick Reference: Phase Summary

| Phase | Steps | Location | Props | Risk | Time |
|-------|-------|----------|-------|------|------|
| 1. Bench | 1-7 | Indoors | OFF | None | ~30 min |
| 2. Outdoors | 8-10 | Field | OFF | None | ~15 min |
| 3. Flights | 11-15 | Field | ON | Escalating | ~2 hrs |

| Step | Script | Sends Commands? | Flies? |
|------|--------|-----------------|--------|
| 1. Camera | test_camera.py | No | No |
| 2. Lens cal | lens_calibrate.py | No | No |
| 3. FOV cal | fov_calibrate.py | No | No |
| 4. AI model | benchmark.py | No | No |
| 5. Cube cmds | 0a_cube_commands.py | Yes (mode only) | No |
| 5b. Bench mission | 0b_bench_mission.py | Yes (mode only) | No |
| 5c. Vision pipeline | 0c_feedback_test.py | No (read-only) | No |
| 6. Servo | 0f_servo_test.py | Yes (servo PWM) | No |
| 7. RC override | 0a_cube_commands.py + RC | Yes | No |
| 8. GPS fix | gps_test.py | No | No |
| 9. GPS estimate cal | gps_estimate_calibrate.py | No | No |
| 10. Compass | diagnostics.py | No | No |
| 11. MP AUTO | Mission Planner only | No (MP handles) | YES |
| 12. Waypoints | 2_waypoints.py | YES | YES |
| 13. Passive CV | 1_passive_flight.py | No (buzzer only) | YES (pilot) |
| 14. Auto detect | 3_auto_detect.py | Yes (mode switch) | YES |
| 15. Full mission | main.py / pi_flight.py | YES (everything) | YES |
