# Flight Ladder — Progressive Test Steps from Bench to Full Mission

**The rule: never skip a step. Each step builds trust. If a step fails, fix it before moving on.**

This document consolidates the L2 critical path (from `dashboard/src/pages/mission-data.ts`),
the flight day checklist (`docs/FLIGHT_DAY_CHECKLIST.md`), and the pre-flight safety
checklist (`docs/PREFLIGHT_SAFETY.md`) into one authoritative progression ladder.

---

## How to Use This Document

1. Print it (or keep it open on a tablet).
2. Start at Step 0. Complete every checkbox.
3. At each GO/NO-GO gate, stop and evaluate honestly.
4. If a step fails, the "If it fails" section tells you what to do.
5. Record results in the spaces provided -- these feed into config.py and the report.

---

## Overview

| Phase | Steps | What It Covers |
|-------|-------|----------------|
| **A: Bench** | 0-2 | No props, no flying. Verify every subsystem. |
| **B: First Flight** | 3-5 | First time in the air. No custom code, then simple code. |
| **C: CV in the Air** | 6-8 | Prove detection works from altitude. Measure accuracy. |
| **D: Autonomous Search** | 9-11 | Drone flies itself. Search pattern, detect, confirm. |
| **E: Full Mission** | 12-14 | Landing, payload, PLB redirect, SSSI, full L2. |

**Estimated time:** 3-4 flight days minimum. Do not try to rush through all steps in one day.

**Batteries per day:** 3-4 recommended (each gives ~15-20 min flight).

---

## Phase A: Bench (No Props, No Flying)

### Step 0: Pre-Field Preparation (at home)

| Item | Check |
|------|-------|
| Code pushed to GitHub | `git add -A && git commit -m "flight day" && git push` |
| Dry-run passes | `python main.py --dry-run` -- waypoints: ____, est. time: ____ min |
| Unit tests pass | `python tests/run_all_tests.py` -- result: ____/____ |
| Model file correct | `ls -la best.tflite` -- size: ____ (expect 11.7MB for sar_v2_1088) |
| Config reviewed | TARGET_ALT=____ SEARCH_SPEED_MPS=____ CONFIDENCE_THRESHOLD=____ |
| SEARCH_AREA_GPS matches field | Compare with KML / Google Maps |
| Batteries charged | Drone LiPo, Pi power, RC TX, laptop |
| Packed | Laptop, RC TX, drone+Pi+camera, USB cable, phone, dummy, tape measure, this checklist |

**Status:** READY (can do at home before every flight day)

---

### Step 1: Component Health Check (bench, no props)

**What:** Verify every subsystem individually before combining them.

| Sub-step | Script | Pass Criteria |
|----------|--------|---------------|
| 1a. Network setup | `hostname -I` on Pi | Pi and laptop on same WiFi, Pi IP noted: ________ |
| 1b. Pull latest code | `cd ~/dima/Group_Proj && git pull` | No merge conflicts |
| 1c. Start mavproxy | See command below | No errors, "Waiting for heartbeat" then heartbeat received |
| 1d. Camera test | `python passive_watch.py --headless` + browser | Video stream visible at http://PI_IP:8090 |
| 1e. Cube heartbeat | `python tests/laptop/test_cube.py` | "Heartbeat received", system ID shown |
| 1f. AI model loads | `python tests/hardware/benchmark.py` | Model loads, inference runs, FPS: ____, confidence: ____ |
| 1g. Mission Planner | TCP -> PI_IP -> 5762 | Map shows drone position, telemetry bar visible |

**Mavproxy command (Pi Terminal 1 -- always first):**
```bash
sudo /opt/mavlink/mavlink-venv/bin/mavproxy.py \
  --master=/dev/ttyAMA0 --baudrate=921600 --streamrate=10 \
  --out=udpout:127.0.0.1:14550 --out=tcpin:0.0.0.0:5762
```

**Existing scripts:** `preflight.py`, `tests/laptop/test_cube.py`, `tests/hardware/benchmark.py`, `tests/diagnostics/diagnostics.py`

**GO/NO-GO:** All sub-steps green. If any fails, fix before proceeding.

**Status:** DONE (verified on bench 2026-03-11, 2026-03-31)

---

### Step 2: Safety Systems Verification (bench, no props)

**What:** Verify every safety mechanism before the drone leaves the ground.

| Sub-step | Script / Action | Pass Criteria |
|----------|-----------------|---------------|
| 2a. DISARM_DELAY = 0 | Mission Planner -> Config -> Full Parameter List | Set to 0 (prevents auto-disarm, see LL-06) |
| 2b. RC failsafe = RTL | Mission Planner -> Config -> Failsafe -> Radio | Radio failsafe set to RTL |
| 2c. GCS failsafe = RTL | Mission Planner -> Config -> Failsafe -> GCS | GCS failsafe set to RTL |
| 2d. Battery failsafe | Mission Planner -> Config -> Failsafe -> Battery | Voltage threshold set, action = RTL |
| 2e. RC kill switch test | Flip RC mode switch | MP shows STABILIZE when flipped, returns when released |
| 2f. RC override WITH script | `python tests/flight/0a_cube_commands.py` + flip RC | Script prints "RC OVERRIDE", sends ZERO commands |
| 2g. Bench command sequence | `python tests/flight/0b_bench_mission.py` | Full command sequence runs (no props, no arming) |
| 2h. Vision-GPS pipeline | `python tests/flight/0c_feedback_test.py` | Detection -> GPS estimate pipeline works end-to-end |
| 2i. Servo test (if payload) | `python tests/flight/0f_servo_test.py` | Tarot servo actuates on command, releases on command |
| 2j. FOV calibration | `python tests/calibration/fov_calibrate.py --headless` | FOCAL_LENGTH_MM = ____ (update config.py) |

**CRITICAL CHECK (2f):** If RC override does not immediately stop the script from sending
commands, **DO NOT FLY.** This is the mode-fighting prevention (LL-01). See `docs/PREFLIGHT_SAFETY.md`.

**Existing scripts:** `tests/flight/0a_cube_commands.py`, `0b_bench_mission.py`, `0c_feedback_test.py`, `0f_servo_test.py`, `tests/calibration/fov_calibrate.py`

**GO/NO-GO:** All safety systems verified. RC override proven to work with script running.

**Status:** PARTIAL (safety systems verified 2026-03-31, servo not yet tested)

---

## Phase B: First Flight (Props On, Simple Flights)

### Step 3: Outdoor GPS Lock

**What:** Take Pi + Cube outside, get 3D satellite lock. This gates ALL flight steps.

| Sub-step | Script | Pass Criteria |
|----------|--------|---------------|
| 3a. GPS tracking | `python tests/hardware/gps_test.py` | fix_type >= 3 (3D fix) |
| 3b. Satellite count | Same | sats >= 8 |
| 3c. HDOP | Same | HDOP < 2.0 |
| 3d. Here 3+ LED | Visual check | Flashing GREEN (not blue) |
| 3e. Position check | Compare MP lat/lon with known location | Within 5m of expected position |
| 3f. GPS noise floor | `python tests/day_1_experiments/gps_drift.py` | CEP50: ____ m, CEP95: ____ m (run while waiting) |

**Additional scripts:** `tests/hardware/gps_health.py` (step-by-step verification)

**Tips:**
- First outdoor lock can take 5-15 minutes. Be patient.
- Move to open area away from buildings/trees if struggling.
- Power cycle for cold start if needed.
- Blue LED = searching, Green = locked, Yellow = pre-arm fail.

**GO/NO-GO:** fix_type >= 3, sats >= 8, LED green.

**If it fails:** Move to more open area. Wait longer. Check antenna connection. Do not fly without GPS lock.

**Status:** TODO

---

### Step 4: Mission Planner AUTO Waypoints (no custom code)

**What:** First real flight. Upload a simple square pattern in Mission Planner. Switch to AUTO on RC. Drone flies pattern and RTLs. YOUR CODE IS NOT RUNNING.

| Sub-step | Action | Pass Criteria |
|----------|--------|---------------|
| 4a. Plan waypoints | MP -> Plan -> 4 waypoints, square, 10-15m altitude | Waypoints visible on map |
| 4b. Upload | MP -> Write WPs | "Waypoints sent" confirmation |
| 4c. Props on, area clear | Install props, clear 30m radius | All people behind safety line |
| 4d. Arm via RC | Throttle down-right (or button) | MP shows ARMED, motors spin |
| 4e. Switch to AUTO | RC mode switch -> AUTO | Drone takes off, flies pattern |
| 4f. Monitor flight | Watch drone + MP track | Stable flight, follows waypoints |
| 4g. RC kill switch test | Mid-flight: flip to STABILIZE briefly | Drone stops immediately, hovers |
| 4h. Resume or RTL | Flip back to AUTO or switch to RTL | Drone resumes or comes home |
| 4i. Landing | AUTO completes or RTL | Safe landing at launch point |

**Proves:** The aircraft flies. GPS navigation works. Cube is configured correctly. RTL works. RC kill switch is reliable. None of your Python code is involved.

**GO/NO-GO:** Drone completed pattern and landed safely. RC override tested mid-flight.

**If it fails:**
- Drift: tune PID/WPNAV params in Mission Planner.
- RC kill switch slow: STOP. Fix RC override before ANY autonomous code.
- Unstable flight: check prop direction, motor order, accelerometer calibration.
- Does not arm: check pre-arm messages in MP (GPS, compass, battery).

**Status:** TODO

---

### Step 5: Compass and Altitude Hold Verification

**What:** Two quick checks that are easy to miss but critical for autonomous flight.

| Sub-step | Action | Pass Criteria |
|----------|--------|---------------|
| 5a. Compass heading | Compare MP heading with phone compass | Within 10 degrees |
| 5b. Compass calibration | If >10 deg off: MP -> Initial Setup -> Compass -> Calibrate | Calibration succeeds, heading matches |
| 5c. Hover at 10m | Pilot takes off in LOITER, hovers at 10m for 30s | Altitude holds steady (+/- 1m on MP) |
| 5d. Altitude accuracy | Compare MP altitude with known reference | Barometric alt within 2m of expected |
| 5e. Wind response | Observe hover stability in current wind | Drone holds position in wind |

**Proves:** Compass is calibrated (critical for heading-based waypoint navigation). Altitude hold is stable (critical for search altitude consistency).

**GO/NO-GO:** Compass within 10 deg, altitude holds within 1m.

**If it fails:**
- Compass off: recalibrate outdoors, away from metal/electronics.
- Altitude drifts: check baro calibration, cover baro from wind.

**NOTE:** This step has no dedicated script. It uses manual RC flight in LOITER mode with Mission Planner monitoring. Could be combined with Step 4 if weather and battery allow.

**Status:** TODO (NEW -- not in original ladder)

---

### Step 6: Waypoint Test Script (your code, no CV)

**What:** Your MAVLink commands fly the drone. Arm, takeoff to 10m, fly 3-4 GPS waypoints, land. No camera, no AI, no decisions.

| Sub-step | Script | Pass Criteria |
|----------|--------|---------------|
| 6a. Draw waypoints on laptop | `python tests/flight/draw_waypoints.py` | waypoints.json created with 4 points |
| 6b. Dry-run | `python tests/flight/2_waypoints.py --dry-run` | Commands print but don't execute |
| 6c. Real flight | `python tests/flight/2_waypoints.py --alt 10` | Drone arms, takes off |
| 6d. Waypoint navigation | Monitor in MP | Drone visits all 4 waypoints |
| 6e. RC override mid-waypoint | Flip to STABILIZE during flight | Drone stops immediately |
| 6f. Resume | Flip back, restart script if needed | Drone completes or lands |
| 6g. Landing | Script commands landing | Safe landing at launch point |

**Proves:** Your MAVLink commands (arm, takeoff, goto, land) work on real hardware. RC override works with your code running.

**GO/NO-GO:** Drone completed waypoints and landed safely. RC override tested.

**If it fails:**
- Does not arm: check DISARM_DELAY, GPS fix, pre-arm messages.
- Wrong waypoints: verify waypoints.json coordinates match field.
- Overshoots waypoints: tune WPNAV_RADIUS in MP params.

**Status:** TODO

---

## Phase C: CV in the Air

### Step 7: Passive CV During Manual Flight

**What:** Pilot flies manually on RC over the dummy at various altitudes. Pi runs camera + AI, logs detections. Pi sends ZERO commands. This is the L1 (Manual MVP) product.

| Sub-step | Script | Pass Criteria |
|----------|--------|---------------|
| 7a. Start passive watch | `python passive_watch.py --headless --stream` | Stream at http://PI_IP:8090 |
| 7b. Place dummy | Flat open ground, note GPS: ____, ____ | No obstacles within 20m |
| 7c. Hover at 10m over dummy | Pilot flies, hold 30s | Detection: YES / NO, confidence: ____ |
| 7d. Hover at 15m | Hold 30s | Detection: YES / NO, confidence: ____ |
| 7e. Hover at 20m | Hold 30s | Detection: YES / NO, confidence: ____ |
| 7f. Hover at 25m | Hold 30s | Detection: YES / NO, confidence: ____ |
| 7g. Hover at 30m | Hold 30s | Detection: YES / NO, confidence: ____ |
| 7h. Flyover at 3 m/s (15m alt) | Fly over dummy | Detection: YES / NO, blur: ____ |
| 7i. Flyover at 5 m/s | Fly over dummy | Detection: YES / NO, blur: ____ |
| 7j. Flyover at 7 m/s | Fly over dummy | Detection: YES / NO, blur: ____ |

**Also run alongside (same flight, save battery):**
- `tests/day_1_experiments/altitude_sweep.py` -- structured CSV data
- `tests/day_1_experiments/speed_sweep.py` -- structured CSV data

**Results table:**

| Altitude | Detected? | Confidence | Notes |
|----------|-----------|------------|-------|
| 10m | | | |
| 15m | | | |
| 20m | | | |
| 25m | | | |
| 30m | | | |

| Speed @15m | Detected? | Blur? | Notes |
|------------|-----------|-------|-------|
| 3 m/s | | | |
| 5 m/s | | | |
| 7 m/s | | | |

**Proves:** CV actually works from the air, not just on the bench. Maximum reliable detection altitude and speed are known.

**GO/NO-GO:** CV detects dummy reliably at SOME altitude. If only below 15m, lower TARGET_ALT.

**If it fails (no detection at any altitude):**
1. Swap model: `cp cv_models/sar_v2_1088/best.tflite best.tflite`
2. Lower confidence: vision.py threshold 0.4 -> 0.3 -> 0.25
3. Try human.tflite (COCO person detector, 80 classes)
4. Try larger/brighter dummy
5. Fly lower (5m hover test)

**Config updates after this step:**
```
TARGET_ALT       = ____ m  (set to max reliable detection altitude)
SEARCH_SPEED_MPS = ____ m/s (set to max speed with reliable detection)
```

**Status:** TODO

---

### Step 8: Speed Test at Search Altitude

**What:** Fly at the TARGET_ALT determined in Step 7, at SEARCH_SPEED_MPS. Verify detection works at the actual search parameters -- not just hover.

| Sub-step | Action | Pass Criteria |
|----------|--------|---------------|
| 8a. Configure | Set TARGET_ALT and SEARCH_SPEED_MPS from Step 7 results | Config updated |
| 8b. Straight pass at search speed | Fly over dummy at TARGET_ALT, SEARCH_SPEED_MPS | At least 1 detection per pass |
| 8c. Multiple passes (3x) | 3 straight-line passes over dummy | Detection rate >= 2/3 passes |
| 8d. Diagonal pass | Fly across dummy at 45-degree angle | Detection? YES/NO |
| 8e. Review detection log | `cat passive_flight_log.csv` or saved images | Consistent detections at search params |

**Proves:** Detection works at the actual search speed and altitude combination that the autonomous mission will use. Not just hover, not just slow flyby -- the real parameters.

**GO/NO-GO:** Detects dummy in at least 2 out of 3 straight passes at search parameters.

**If it fails:** Lower SEARCH_SPEED_MPS or TARGET_ALT further. The lawnmower pattern will be slower but detection will be reliable.

**NOTE:** This step can be combined with Step 7 if battery allows. The key difference is testing at the COMBINED search parameters, not individual altitude/speed sweeps.

**Status:** TODO (NEW -- not in original ladder)

---

### Step 9: Geotagging Accuracy from Flyover

**What:** Fly over dummy without stopping. CV estimates GPS position from detection frames. Compare estimate vs actual dummy position.

| Sub-step | Script | Pass Criteria |
|----------|--------|---------------|
| 9a. Record dummy GPS | Walk to dummy with phone/MP | Known position: ____, ____ |
| 9b. Flyover (3 passes) | `passive_watch.py --headless --stream` + manual flight | 3+ detection events logged |
| 9c. Review estimates | Check saved detection images with GPS in filename | Estimate error: ____ m |
| 9d. Structured test | `python tests/calibration/gps_ground_truth.py` | CSV with estimate vs actual |
| 9e. Also run | `python tests/day_1_experiments/gps_accuracy.py` | Error per altitude in CSV |

**Proves:** Pixel-to-GPS conversion (GeoTransformer in utils.py) works from a moving flyover. Accuracy is known.

**GO/NO-GO:**
- Error < 3m: Excellent. Flyover geotagging may be sufficient (skip centering).
- Error 3-10m: Acceptable. Centering (Step 10) will refine.
- Error > 10m: FOV calibration is likely wrong. Re-run `tests/calibration/fov_calibrate.py`.

**Status:** TODO

---

### Step 10: CV Centering Accuracy

**What:** Hover above dummy, use visual servo to centre drone directly over target. Compare centred GPS with flyover estimate from Step 9.

| Sub-step | Script | Pass Criteria |
|----------|--------|---------------|
| 10a. Fly to detection area | Pilot or script | Drone near dummy at 15m |
| 10b. Auto-investigate | `pi_flight.py` -- press N in browser | Drone flies to GPS estimate |
| 10c. Visual servo centres | Watch stream: detection box moves to centre | Drone directly above dummy |
| 10d. Record centred GPS | Read from MP or dashboard | Centred position: ____, ____ |
| 10e. Compare with flyover | Step 9 estimate vs Step 10 centred | Centering error: ____ m |
| 10f. Compare with actual | Step 10 centred vs actual dummy GPS | Absolute error: ____ m |

**Also test with:** `tests/flight/4_detect_and_center.py`

**Proves:** Visual servo centering works in real flight. Centred position is more accurate than flyover estimate.

**Decision matrix after Steps 9 + 10:**

| Flyover Error | Centering Error | Decision |
|---------------|-----------------|----------|
| < 3m | < 2m | Either works. Use flyover (faster) |
| 3-10m | < 2m | Use centering to refine before landing |
| > 10m | < 2m | Fix FOV calibration. Use centering |
| Any | > 5m | Visual servo needs tuning |

**Status:** TODO

---

## Phase D: Autonomous Search

### Step 11: Fly Search Pattern (no CV action)

**What:** Drone flies the full lawnmower search pattern autonomously. CV logs but does NOT trigger any behaviour. Drone completes pattern and comes home.

| Sub-step | Script | Pass Criteria |
|----------|--------|---------------|
| 11a. Draw search area | `python tests/flight/draw_search_area.py` | search_area.json matches field |
| 11b. Preview pattern | `python main.py --dry-run` | Lawnmower covers area, no SSSI overlap |
| 11c. Autonomous search | `python main.py --headless --stream` (CV log only) | Drone takes off, follows pattern |
| 11d. Monitor | MP + http://PI_IP:8090 + `tests/flight/live_map.py` | Track matches planned pattern |
| 11e. CV detections logged | Review log after landing | Detections logged but not acted on |
| 11f. RTL on completion | Drone returns home after pattern complete | Safe landing at launch point |

**Proves:** Autonomous lawnmower pattern works in the real world. Drone can fly a search area and come home.

**GO/NO-GO:** Drone completed pattern and returned safely. Track matches planned lawnmower.

**If it fails:**
- Pattern gaps: tune overlap in planning.py.
- Waypoint drift: check WPNAV params, reduce speed.
- Does not complete: check battery, shorten search area.

**Status:** TODO

---

### Step 12: Search + Detect + Confirm (Y/X)

**What:** CV is active during search. Detection triggers investigation. Pilot confirms or rejects.

| Sub-step | Script | Pass Criteria |
|----------|--------|---------------|
| 12a. Start full system | `python main.py --headless --stream` on Pi | Dashboard at http://PI_IP:8090 |
| 12b. Search begins | Drone flies lawnmower | Pattern followed correctly |
| 12c. Detection occurs | CV spots dummy | Alert in browser dashboard |
| 12d. Press N (investigate) | Browser button | Drone flies to GPS estimate (GUIDED) |
| 12e. CV centering | Automatic | Detection box centres in frame |
| 12f. Pilot classifies | Y = dummy, X = false positive | Correct classification |
| 12g. If X: resume search | Drone returns to pattern | Search continues from where it left |
| 12h. If Y: proceed to landing | Drone ready for Step 13 | Position confirmed |

**Also use:** `pi_flight.py` for the browser dashboard.

**Proves:** Core detect-investigate-confirm loop works. Pilot can see detections and decide. CV centering refines position automatically.

**GO/NO-GO:** Dummy detected during search, correctly classified by pilot, investigation flew to correct area.

**If it fails:**
- Too many false positives: raise confidence threshold, or use `--smart-detect` flag.
- Detection missed during search: lower altitude or speed (from Step 7/8 results).
- Dashboard unresponsive: check WiFi, reduce stream quality.

**Status:** TODO

---

## Phase E: Full Mission

### Step 13: Offset Landing + Payload Delivery

**What:** After Y confirmation, drone flies to 7.5m offset and lands. Payload released.

| Sub-step | Script | Pass Criteria |
|----------|--------|---------------|
| 13a. Confirm target (Y) | Browser dashboard | Drone has confirmed target GPS |
| 13b. Press L (land) | Browser button | Drone flies to 7.5m offset |
| 13c. Descent | Automatic | Drone descends to ground |
| 13d. Landing | Automatic | Safe landing, no damage |
| 13e. Measure distance | Tape measure from dummy to drone | Distance: ____ m (must be 5-10m) |
| 13f. Payload release | MAV_CMD_DO_SET_SERVO | Payload released cleanly |
| 13g. RTL | Browser button or automatic | Drone returns to launch |

**Proves:** R07 compliance -- payload delivered within 5-10m zone.

**GO/NO-GO:** Landing distance 5-10m from dummy. Payload released.

**If it fails:**
- Landing too close (<5m): increase offset in config.py.
- Landing too far (>10m): improve GPS estimate accuracy (Steps 9-10).
- Payload stuck: check servo wiring, PWM values, mechanical clearance.

**Status:** TODO

---

### Step 14: PLB Focused Search Redirect

**What:** Mid-search, simulate PLB signal. Drone redirects to Focus Area.

| Sub-step | Script | Pass Criteria |
|----------|--------|---------------|
| 14a. Start search | main.py running lawnmower | Search in progress |
| 14b. Trigger PLB | `--beacon-delay N` or browser button | PLB signal received |
| 14c. Redirect | Drone abandons lawnmower | Drone flies to Focus Area |
| 14d. New search | Lawnmower over Focus Area | New pattern generated and followed |
| 14e. Detection in Focus Area | CV detects dummy | Same Y/X flow as Step 12 |

**Proves:** R06 compliance -- drone redirects to PLB Focus Area on signal.

**GO/NO-GO:** Drone redirects mid-search, generates new pattern, searches Focus Area.

**Status:** TODO

---

### Step 15: SSSI Geofence

**What:** Verify drone never enters SSSI no-fly zone during search.

| Sub-step | Script | Pass Criteria |
|----------|--------|---------------|
| 15a. Standalone fence test | Upload SSSI as exclusion fence in MP | Fence active |
| 15b. Fly toward SSSI | LOITER/GUIDED toward boundary | Drone stops at edge |
| 15c. Record closest point | GPS at closest approach | Distance from SSSI: ____ m |
| 15d. Integrate in search | main.py with SSSI avoidance | Lawnmower skips SSSI waypoints |
| 15e. Full search with SSSI | main.py --dry-run shows no SSSI overlap | Zero GPS points inside SSSI |

**Also use:** `tests/flight/0e_geofence_test.py` (software geofence unit tests)

**Proves:** R02 compliance -- drone never enters SSSI.

**GO/NO-GO:** Zero SSSI incursions in flight log.

**Status:** TODO

---

### Step 16: Items of Interest (Y/I/X)

**What:** Scatter objects on field. Pilot classifies: Y=dummy, I=item of interest, X=false positive.

| Sub-step | Action | Pass Criteria |
|----------|--------|---------------|
| 16a. Place objects | Scatter 3-5 objects + dummy on field | Objects at known GPS positions |
| 16b. Full search | main.py + pi_flight.py | Drone detects multiple objects |
| 16c. Classify each | Y / I / X in browser | Correct classifications |
| 16d. IOI logged | Items of interest saved with GPS + images | R10 compliance |
| 16e. Only Y triggers landing | Press Y only on real dummy | Drone lands near dummy only |

**Proves:** Full classification workflow. Items of interest logged with GPS and images (R10).

**Status:** TODO

---

### Step 17: Full L2 Mission

**What:** Everything combined end-to-end. The complete semi-autonomous mission.

| Sub-step | Script | Pass Criteria |
|----------|--------|---------------|
| 17a. Dry-run | `python main.py --dry-run` | Pattern correct, no SSSI overlap |
| 17b. Full mission | `python main.py --headless --stream` | All systems running |
| 17c. Takeoff + search | Automatic | Lawnmower search, SSSI avoided |
| 17d. PLB redirect | Mid-search trigger | Drone redirects to Focus Area |
| 17e. Detection + confirm | CV detects, pilot Y/I/X | Correct classification |
| 17f. Offset landing | 7.5m from target | Distance 5-10m measured |
| 17g. Payload delivery | Servo release | Payload delivered |
| 17h. RTL | Automatic | Safe return to launch |

**Proves:** Level 2 complete. All requirements (R01-R12) addressed in a single flight.

**GO/NO-GO:** All requirements met in one flight. This is the flight test (D5).

**Status:** TODO

---

## Script-to-Step Mapping

| Script | Steps | Purpose |
|--------|-------|---------|
| `preflight.py` | 1 | Component health check |
| `tests/diagnostics/diagnostics.py` | 1 | Multi-view diagnostics dashboard |
| `tests/laptop/test_cube.py` | 1 | Cube heartbeat verification |
| `tests/hardware/benchmark.py` | 1 | AI inference benchmark |
| `tests/hardware/gps_test.py` | 3 | GPS lock tracking |
| `tests/hardware/gps_health.py` | 3 | Step-by-step GPS verification |
| `tests/day_1_experiments/gps_drift.py` | 3 | GPS noise floor (stationary) |
| `tests/flight/0a_cube_commands.py` | 2 | RC override test with script |
| `tests/flight/0b_bench_mission.py` | 2 | Full bench command sequence |
| `tests/flight/0c_feedback_test.py` | 2 | Vision-GPS pipeline bench test |
| `tests/flight/0f_servo_test.py` | 2, 13 | Payload servo test |
| `tests/flight/0d_planning_test.py` | 11 | Lawnmower pattern unit tests |
| `tests/flight/0e_geofence_test.py` | 15 | SSSI geofence unit tests |
| `tests/calibration/fov_calibrate.py` | 2 | FOV calibration (bench) |
| `tests/calibration/gps_ground_truth.py` | 9 | GPS estimate vs actual |
| `tests/flight/draw_waypoints.py` | 6 | Draw waypoints on map (laptop) |
| `tests/flight/2_waypoints.py` | 6 | Fly GPS waypoints |
| `tests/flight/draw_search_area.py` | 11 | Draw search area on map (laptop) |
| `passive_watch.py` | 7, 8, 9 | Passive detection + geotagging |
| `tests/flight/1_passive_flight.py` | 7, 8 | Passive detection (simplified) |
| `tests/day_1_experiments/altitude_sweep.py` | 7 | Detection rate vs altitude |
| `tests/day_1_experiments/speed_sweep.py` | 7, 8 | Detection rate vs speed |
| `tests/day_1_experiments/gps_accuracy.py` | 9 | GPS estimate error vs ground truth |
| `tests/flight/4_detect_and_center.py` | 10 | Visual servo centering test |
| `tests/flight/3_auto_detect.py` | 12 | AUTO + AI -> GUIDED hover |
| `main.py` | 11, 12, 14, 15, 17 | Full state machine |
| `pi_flight.py` | 10, 12, 13, 14, 16, 17 | Browser ground station |
| `tests/flight/live_map.py` | 11 | Real-time coverage overlay |

---

## Gap Analysis: Steps Not in the Original Ladder

The following steps were **added** to improve safety and confidence:

| New Step | Why It Was Added | Risk It Mitigates |
|----------|-----------------|-------------------|
| **Step 5: Compass + Altitude Hold** | Compass miscalibration causes wrong heading on waypoints. Altitude drift causes search at wrong height. | Drone flies to wrong location. Search altitude inconsistent. |
| **Step 8: Speed Test at Search Params** | Original ladder tested altitude and speed separately, but the combination matters. | Detection fails at actual search parameters even though individual tests passed. |

---

## Parallel Tasks (can happen during any step)

These improve accuracy and data quality but do not block the critical path. Run them
whenever you have spare battery or bench time.

| Task | Script | Status | Best Time |
|------|--------|--------|-----------|
| Real-altitude FOV verification | `tests/calibration/alt_test.py` | TODO | After Step 7 |
| GPS noise floor (stationary) | `tests/day_1_experiments/gps_drift.py` | TODO | During Step 3 (free time) |
| GPS drift in hover | `tests/day_1_experiments/gps_drift.py` | TODO | During Step 7 |
| Compare all TFLite models | `tests/day_1_experiments/model_compare.py` | TODO | Bench or Step 7 |
| Tune confidence threshold | Review detection CSV | TODO | After Step 7 |
| Video stream latency | `pi_flight.py` + stopwatch | TODO | During Step 1 |
| Wi-Fi range test | Walk away with laptop | TODO | During Step 3 |
| Battery endurance | Time full flight | TODO | During Step 11 |
| NCNN backend test | `tests/hardware/benchmark.py` with NCNN | TODO | Bench anytime |

---

## Emergency Procedures (keep in pocket)

```
KILL SWITCH:     RC -> STABILIZE (always works, always available)
SCRIPT CRASH:    GCS failsafe -> RTL (automatic)
RC LOST:         RC failsafe -> RTL (automatic)
EMERGENCY:       Anyone calls "KILL KILL" -> pilot flips to STABILIZE

Communication protocol:
  "TAKING OFF" -- pilot announces before arming
  "AIRBORNE"   -- pilot confirms stable hover
  "SWITCHING"  -- pilot announces before GUIDED mode
  "KILL KILL"  -- anyone can call, pilot flips immediately
  "LANDING"    -- pilot announces before landing
```

---

*Last updated: 2026-04-03. Consolidates docs/FLIGHT_DAY_CHECKLIST.md, docs/PREFLIGHT_SAFETY.md, and dashboard/src/pages/mission-data.ts L2_CRITICAL_PATH.*
