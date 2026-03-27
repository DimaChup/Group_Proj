# Working5.8 Features & Changes Covered by Checklist

This document maps each test to the features/commits it validates.

---

## Code Refactoring (e5b312f - Current)

**Commits involved**:
- e5b312f: Refactor _handle_keys into 3 focused methods
- f75a58e: Refactor _handle_search into 4 focused methods
- 35e0ddb: Rename state_machine_no_descend → state_machine (sole variant)

**Files affected**:
- main.py (909 lines, was ~1800)
- state_machine.py (1062 lines, new extracted module)
- navigation.py (253 lines, new extracted module)
- gps_utils.py (122 lines, new extracted module)
- stream_server.py (225 lines, new extracted module)

**Tests validating**:
- TEST 15: Code refactoring validation (imports, runtime, performance)
- TEST 1: Full mission (end-to-end integration after refactoring)
- TEST 16: Stream server (new module, HTTP UI)

---

## Safety & Geofence (465d8db)

**Commit**:
- 465d8db: Fix: load KML in REAL mode (geofence was disabled!)
- dabe8c7: Fix: send_land float params, remove geofence int() cast

**Features**:
- KML-based geofence loading (SSSI_GPS from AENGM0074.kml)
- Speed capping near NFZ boundary (10m buffer, SPEED_CAP_NFZ=2-3 m/s)
- Repulsive force if inside SSSI (auto-manual mode)
- Geofence visualization in dry-run

**Tests validating**:
- TEST 4: Geofence enforcement (boundary check, repulsion, auto-manual)
- TEST 8: NFZ speed capping (gradient test at different distances)
- TEST 9: Detection outside search area (polygon filtering)
- TEST 13: Dry-run visualization (shows NFZ boundaries)

---

## Detection Pipeline (f06d88a, b90d4b5, 24a468f)

**Commits**:
- f06d88a: Fix: validate all detection queue pops (NFZ + search area + near-known checks)
- b90d4b5: Fix 3 detection pipeline bugs: dedup, NFZ check, stale departure
- 24a468f: Fix: check detection queue before resuming from manual — dummy first, then resume
- e874df6: Ignore detections outside search area — only investigate within polygon
- 50bbd04: Fix: return to scan line after queue empty, 3m reject radius, queue detections in manual mode
- 3714ce1: Increase reject radius back to 5m (3m too tight for GPS noise + angle shifts)

**Features**:
- Detection queue (multiframe storage)
- Polygon filtering (ignore detections outside search area)
- Deduplication (don't queue same dummy twice)
- Reject radius 5m (prevent loops on same target)
- Manual mode queueing (Y/N/I/X while paused)
- Queue persistence (resume with queue intact)

**Tests validating**:
- TEST 6: Manual override (M key, queue dummies while paused, resume with queue)
- TEST 7: Multiple dummies (queue ordering, visit all)
- TEST 9: Detection outside search area (ignored)
- TEST 18: Reject radius 5m (no re-investigation)
- TEST 19: Manual mode detection queue (persist across resume)
- TEST 21: Empty detection queue (resume search)

---

## Confidence Threshold Tuning (49cd80c)

**Commit**:
- 49cd80c: Confidence threshold 0.2 (was 0.1 — too low for real deployment)

**Features**:
- Confidence threshold in vision.py (0.2)
- Balances detection rate vs false positives
- Pre-calibrated for TFLite on Pi

**Tests validating**:
- TEST 17: Confidence threshold validation (real dummy detected, false positives rare)

---

## Manual Override & Keyboard Input (e5b312f)

**Refactored from original**:
- M key: toggle MANUAL mode
- Y/N/I/X keys: mark detections (yes/no/interest/false-positive)
- L key: land immediately

**Tests validating**:
- TEST 6: Manual override (M key workflow)
- TEST 19: Manual mode detection queue (Y key in manual)
- TEST 20: Rapid key presses (input robustness)

---

## Command-Line Flags

### --speed N (SIM_SPEED)
Purpose: Speedup SITL simulation (N=2 means 2x speed, N=5 means 5x speed)

Tests validating:
- TEST 1: --speed 5 (full mission at 5x)
- TEST 2: --smart-detect --speed 5
- TEST 3: --center-verify --speed 5

### --smart-detect
Purpose: Multi-frame confirmation (requires N consecutive frames to trigger)

Features:
- Accumulates detections over multiple frames
- Reduces false positive triggers
- Smooth state transitions

Tests validating:
- TEST 2: Smart detection (multi-frame confirmation)

### --center-verify
Purpose: Vision-based centering + GPS averaging (10s)

Features:
- Visual servo during CENTERING (moves dummy to frame center)
- Accumulates 10+ GPS fixes at 1Hz
- Improves landing accuracy

Tests validating:
- TEST 3: Center verify (vision centering + GPS averaging)

### --no-nfz
Purpose: Disable geofence for testing in constrained areas

Tests validating:
- TEST 5: Disable geofence (--no-nfz flag)

### --beacon-delay N
Purpose: Simulate PLB signal arriving N seconds after search begins

Features:
- Timer-based redirect trigger
- Replaces initial target with PLB location
- Tests multi-target switching

Tests validating:
- TEST 10: Beacon delay (PLB simulation)

### --transit <path>
Purpose: Use optimized transit path instead of lawnmower

Features:
- Loads custom waypoint JSON
- Replaces default lawnmower pattern
- Energy-optimized paths (future work)

Tests validating:
- TEST 11: Transit planning (custom path)

### --alt N
Purpose: Override TARGET_ALT for testing

Tests validating:
- TEST 12: Altitude override (--alt 20)

### --dry-run
Purpose: Print mission plan without flying or connecting to hardware

Features:
- No Cube connection needed
- No SITL required
- Generates visualization image (waypoints + search area)
- Prints state machine walkthrough
- Estimates time and energy

Tests validating:
- TEST 13: Dry-run mode (plan generation)
- TEST 15: Refactoring (imports without flying)

### --headless
Purpose: Disable GUI windows (for Pi or headless servers)

Features:
- No cv2.imshow/namedWindow/waitKey
- All output to terminal
- Web UI at http://localhost:8090
- HTTP buttons: Y/N/M/E/W/S

Tests validating:
- TEST 14: Headless mode (no windows, web UI only)

### --model <path>
Purpose: Override AI model file (e.g., best2.tflite, human.tflite)

Available models:
- best.tflite (default, 3.3MB custom)
- models/human.tflite (COCO person detector, 13MB)
- models/custom_yolov8n.tflite (baseline)
- cv_models/sar_v2_1088/best.tflite (retrained, 11.7MB)

Tests validating:
- Implicitly tested in TEST 1, TEST 15, TEST 13

---

## Web UI & Stream Server (8d192f4)

**Commits**:
- 8d192f4: stream_server: add allow_reuse_address (prevent restart failure after crash)

**Features**:
- MJPEG video stream on http://localhost:8090
- State info display (battery, GPS, altitude)
- Detection queue visualization
- Control buttons: Y/N/M/E/W/S (for headless or browser control)
- Responsive HTTP endpoint for commands

**Tests validating**:
- TEST 14: Headless mode (web UI)
- TEST 16: Stream server (HTTP buttons, video feed)

---

## Logging (implicit)

**Features**:
- flight_log.csv with telemetry
- Columns: timestamp, state, lat, lon, altitude, velocity, battery, detection confidence

**Tests validating**:
- TEST 22: Log file generation (CSV format, valid data)

---

## Summary Table

| Test | Feature | Commit(s) |
|------|---------|-----------|
| 1 | Full mission baseline | All |
| 2 | --smart-detect flag | b90d4b5, 24a468f |
| 3 | --center-verify flag | (vision.py feature, not main.py) |
| 4 | Geofence enforcement | 465d8db, dabe8c7 |
| 5 | --no-nfz flag | b26f6cf |
| 6 | Manual override (M key) | e5b312f, f75a58e |
| 7 | Multiple dummies queue | f06d88a, b90d4b5 |
| 8 | NFZ speed capping | 465d8db |
| 9 | Detection filtering | e874df6, f06d88a |
| 10 | --beacon-delay flag | (feature planned, test ready) |
| 11 | --transit flag | db481f2 (path simulation script) |
| 12 | --alt flag | (config override, already worked) |
| 13 | --dry-run flag | 1213407, 465d8db |
| 14 | --headless flag | (added in earlier session) |
| 15 | Code refactoring | e5b312f, f75a58e, 35e0ddb |
| 16 | Stream server | 8d192f4 |
| 17 | Confidence threshold | 49cd80c |
| 18 | Reject radius 5m | 3714ce1 |
| 19 | Manual mode queue persist | 24a468f |
| 20 | Rapid key presses | (robustness test) |
| 21 | Empty queue handling | 50bbd04 |
| 22 | Log file generation | (implicit) |

---

## Known Limitations / Future Work

Per CLAUDE.md CV Optimization section:

1. Beacon delay (TEST 10): Simulation feature, not yet integrated into state machine
2. FP16 quantization: Not yet enabled on Pi (possible 2x speedup)
3. NCNN backend: Export available, but not tested on Pi
4. INT8 quantization: Not viable on Pi 5 (NCNN support missing)
5. Multi-threading optimization: Pipeline can overlap capture + inference for +20-30% throughput

---

## Before Flight Day

1. Complete full 22-test checklist in simulation
2. Merge Working5.8 to MainOne2 (staging)
3. Pi deployment:
   - Pull MainOne2
   - Copy best.tflite (or retrained sar_v2_1088)
   - Run preflight.py to verify hardware
4. First flight: manual RC with passive detection (TEST 1_passive_flight.py)
5. Full autonomous: final mission with all safety systems enabled

---

Generated: 2026-03-27
