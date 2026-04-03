# L2 Critical Path Analysis

**Generated from `dashboard/src/pages/mission-data.ts`**
**Last updated: 2026-04-03**

---

## Overview

The L2 Semi-Autonomous mission has **13 critical path steps** arranged in **12 rows**, with **3 milestones** and **20 parallel tasks**. Steps on the same row can be done simultaneously.

**Progress: 1/13 critical path steps complete. 5/20 parallel tasks complete.**

---

## Critical Path Steps (Do In Order)

### Row 1: Foundation

| Step | Name | Status | Script |
|------|------|--------|--------|
| cp-1 | All components healthy | **DONE** | `preflight.py`, `0a_cube_commands.py`, `0b_bench_mission.py`, `0c_feedback_test.py` |

**Proves:** Every subsystem talks to every other subsystem.
**Output:** PASS/FAIL per subsystem.

---

### Row 2: GPS Baseline

| Step | Name | Status | Script | Depends On |
|------|------|--------|--------|------------|
| cp-2 | Outdoor GPS 3D fix | **TODO** | `tests/hardware/gps_test.py`, `gps_health.py`, `gps_drift.py` | cp-1 |

**Proves:** GPS works outdoors. We have real coordinates to work with.
**Output:** Fix type, sat count, HDOP, lat/lon vs known position. Stationary drift CEP50/CEP95.
**Equipment:** Pi + Cube + GPS antenna, outdoor location with clear sky view.
**Estimated time:** 15-30 min (mostly waiting for satellite lock).

**How to run:**
```bash
# On Pi (SSH terminal)
source pienv/bin/activate && cd ~/sar-drone
python tests/hardware/gps_test.py          # continuous tracking
python tests/hardware/gps_health.py        # step-by-step verification
python tests/day_1_experiments/gps_drift.py # stationary noise floor
```

---

### --- MILESTONE 1 ---
> **All components are working and talking to each other**
> Camera, Cube, AI model, GPS with outdoor 3D fix -- every subsystem verified. Hardware integration complete. Ready to fly.

---

### Row 3: Safest First Flight (No Custom Code)

| Step | Name | Status | Script | Depends On |
|------|------|--------|--------|------------|
| cp-2a | Mission Planner AUTO waypoints | **TODO** | Mission Planner GUI (no Python script) | cp-2 |

**Proves:** The aircraft flies, GPS navigation works, Cube is configured correctly, RTL works. RC kill switch is reliable.
**Output:** Drone completed 4-waypoint pattern and returned. RC override tested mid-flight.
**Equipment:** Full drone assembled, battery, RC controller, Mission Planner on laptop, clear field.
**Estimated time:** 30-60 min (setup + multiple attempts).

**Decision points:**
- If drone drifts badly --> Tune PID/WPNAV params in Mission Planner before proceeding.
- If RC kill switch doesn't respond instantly --> **STOP. Fix before any autonomous code.**

---

### Row 4: Two Independent First Flights with Code (PARALLEL)

These two steps can be done simultaneously (same row).

| Step | Name | Status | Script | Depends On |
|------|------|--------|--------|------------|
| cp-3 | Manual flight + CV check | **TODO** | `passive_watch.py` or `tests/flight/1_passive_flight.py` | cp-2a |
| cp-4 | Fly GPS waypoints + RC override | **TODO** | `tests/flight/2_waypoints.py` | cp-2a |

**cp-3 (Manual flight + CV check):**
- Pilot flies manually over dummy at 15-30m. Pi runs camera + AI passively (ZERO commands).
- **Proves:** CV works from the air, not just on bench. Detection altitude range known.
- **Equipment:** Drone + Pi + camera, dummy on ground, RC controller.
- **Estimated time:** 20-30 min per flight.
- **How to run:**
```bash
python passive_watch.py --headless --stream
# Browser: http://PI_IP:8090
# Also run alongside: altitude_sweep.py, speed_sweep.py
```
- **Decision points:**
  - Detection only works below 15m --> Lower TARGET_ALT in config.py.
  - Too many false positives --> Raise confidence threshold or swap to `human.tflite`.

**cp-4 (Fly GPS waypoints + RC override):**
- Drone arms, takes off to 10m, flies 3-4 GPS waypoints in GUIDED mode, lands. No camera/AI.
- **Proves:** MAVLink commands make the drone fly to GPS coordinates. RC override works.
- **Equipment:** Same as above. Waypoints from `waypoints.json`.
- **Estimated time:** 15-20 min.
- **How to run:**
```bash
# Pre-test on bench (no props):
python tests/flight/0a_cube_commands.py
python tests/flight/0b_bench_mission.py
# Then fly:
python tests/flight/2_waypoints.py
# Preview pattern on laptop:
python main.py --dry-run
```

---

### Row 5: Position Accuracy + Geofence (3 PARALLEL steps)

| Step | Name | Status | Script | Depends On |
|------|------|--------|--------|------------|
| cp-5 | Geotagging from flyover | **TODO** | `tests/calibration/gps_ground_truth.py`, `gps_accuracy.py` | cp-3 |
| cp-6 | CV centering accuracy | **TODO** | `tests/flight/4_detect_and_center.py` | cp-3, cp-4 |
| cp-6b | Test geofence standalone | **TODO** | Mission Planner fence setup | cp-4 |

**cp-5 (Geotagging from flyover):**
- Fly over dummy without stopping. CV estimates GPS position. Compare with actual.
- **Proves:** Pixel-to-GPS conversion accuracy from a moving flyover.
- **Estimated time:** 20-30 min.
- **Decision points:**
  - <3m error --> May not need centering step at all. Faster mission.
  - 5-10m error --> Need centering (cp-6) to refine.
  - >10m error --> Camera calibration is off. Run FOV calibration first.

**cp-6 (CV centering accuracy):**
- Hover above dummy, use visual servo to centre. Compare centred GPS vs flyover GPS.
- **Proves:** CV centering works in real flight.
- **Estimated time:** 20-30 min.

**cp-6b (Test geofence standalone):**
- Upload SSSI polygon as exclusion fence in ArduCopter via Mission Planner. Fly toward boundary deliberately.
- **Proves:** ArduCopter geofence exclusion prevents drone from entering SSSI.
- **Estimated time:** 30 min.
- **Key params:** `FENCE_ENABLE=1`, `FENCE_TYPE=7`, `FENCE_ACTION` (RTL or BRAKE).

---

### --- MILESTONE 2 ---
> **We can reliably geotag a dummy from the air**
> Geotagging, centering, and geofence boundary all validated. Position accuracy known. Ready to build the full search loop.

---

### Row 6: Search Pattern Alone

| Step | Name | Status | Script | Depends On |
|------|------|--------|--------|------------|
| cp-7 | Fly search pattern (no CV action) | **TODO** | `main.py --headless --stream` | cp-3, cp-4 |

**Proves:** Autonomous lawnmower pattern works in the real world.
**Equipment:** Full drone, search area defined in `search_area.json`.
**Estimated time:** 15-20 min flight.
**How to run:**
```bash
# Preview on laptop first:
python main.py --dry-run
# Then fly on Pi:
python main.py --headless --stream
# Live coverage on laptop:
python tests/flight/live_map.py
```

---

### Row 7: Search + Detect + Confirm

| Step | Name | Status | Script | Depends On |
|------|------|--------|--------|------------|
| cp-8 | Search + detect dummy + confirm (Y/X) | **TODO** | `pi_flight.py` + `main.py` | cp-5, cp-6, cp-7 |

**Proves:** Core detect-investigate-confirm loop works. Pilot can see detections and decide.
**Equipment:** Full drone, dummy on ground, browser dashboard.
**Estimated time:** 30-45 min (multiple attempts expected).
**How to run:**
```bash
# On Pi:
python main.py --headless --stream
# Browser: http://PI_IP:8090 — Y/X buttons
# Rehearse on laptop first:
python simple_simulator.py
```

---

### Row 8: Landing + Payload

| Step | Name | Status | Script | Depends On |
|------|------|--------|--------|------------|
| cp-9 | Offset landing + payload delivery | **TODO** | `pi_flight.py` (L button) | cp-8 |

**Proves:** R07 compliance -- payload delivered within 5-10m zone.
**Equipment:** Tarot servo wired to Cube AUX port, first aid kit payload.
**Estimated time:** 30-45 min.

---

### --- MILESTONE 3 ---
> **We can find, confirm, and deliver to a target**
> Search + detect + confirm + land + payload. Core mission works. Remaining steps add PLB, items of interest, and SSSI.

---

### Row 9: PLB Redirect

| Step | Name | Status | Script | Depends On |
|------|------|--------|--------|------------|
| cp-10 | PLB focused search redirect | **TODO** | `pi_flight.py` (button) | cp-8 |

**Proves:** R06 compliance -- drone redirects to PLB Focus Area on signal.
**Estimated time:** 20-30 min.

---

### Row 10: Items of Interest

| Step | Name | Status | Script | Depends On |
|------|------|--------|--------|------------|
| cp-11 | Add items of interest (Y/I/X) | **TODO** | `pi_flight.py` + `main.py` | cp-10 |

**Proves:** Full classification workflow. Items of interest logged with GPS and images.
**Equipment:** Scatter objects in field alongside dummy.
**Estimated time:** 30 min.

---

### Row 11: SSSI Geofence in Search

| Step | Name | Status | Script | Depends On |
|------|------|--------|--------|------------|
| cp-12 | SSSI geofence in search | **TODO** | `main.py --dry-run` to preview, then fly | cp-6b, cp-11 |

**Proves:** R02 compliance in a real search mission. Search + detect + classify + avoid SSSI all work together.
**Estimated time:** 30-45 min.

---

### Row 12: Full Integrated Mission

| Step | Name | Status | Script | Depends On |
|------|------|--------|--------|------------|
| cp-13 | Full L2 mission | **TODO** | `main.py` + `pi_flight.py` | cp-9, cp-10, cp-11, cp-12 |

**Proves:** Level 2 complete. All requirements (R01-R12) addressed in a single flight.
**Equipment:** Everything. Follow `docs/FLIGHT_DAY_CHECKLIST.md`.
**Estimated time:** 45-60 min (including setup and review).
**How to run:**
```bash
# Preview:
python main.py --dry-run
# Fly:
python main.py --headless --stream
# Browser dashboard:
# http://PI_IP:8090
# Checklist:
# docs/FLIGHT_DAY_CHECKLIST.md
```

---

## Dependency Graph

```
cp-1 (DONE)
  |
cp-2 (GPS fix)
  |
cp-2a (MP AUTO waypoints)
  |
  +------+------+
  |              |
cp-3 (CV)    cp-4 (Waypoints)
  |              |
  +---+    +-----+-----+
  |   |    |     |     |
cp-5  cp-6    cp-6b
  |   |          |
  +---+----------+
  |
cp-7 (Search pattern)
  |
cp-8 (Search + detect + confirm)
  |
  +--------+---------+
  |         |         |
cp-9     cp-10     (cp-6b)
  |         |         |
  |      cp-11--------+
  |         |         |
  |      cp-12--------+
  |         |
  +---------+
  |
cp-13 (FULL L2 MISSION)
```

---

## Parallel Tasks (Do Alongside Critical Path)

### Calibration (3 tasks, 2 DONE)

| ID | Task | Status | Script |
|----|------|--------|--------|
| pt-fov | Calibrate FOV (focal length + sensor width) | **DONE** | `tests/calibration/fov_calibrate.py` |
| pt-lens | Lens distortion calibration | **DONE** | `tests/calibration/lens_calibrate.py` |
| pt-alt-fov | Real-altitude FOV verification | TODO | `tests/calibration/alt_test.py` (after pt-fov) |

### Accuracy Measurements (5 tasks, 0 DONE)

| ID | Task | Status | Script |
|----|------|--------|--------|
| pt-gps-drift | GPS noise floor (stationary drift) | TODO | `tests/day_1_experiments/gps_drift.py` |
| pt-gps-hover | GPS drift in hover | TODO | `tests/day_1_experiments/gps_drift.py` (after pt-gps-drift) |
| pt-gps-accuracy | GPS estimation error vs ground truth | TODO | `tests/day_1_experiments/gps_accuracy.py` |
| pt-rangefinder-accuracy | Rangefinder accuracy test | TODO | (manual) |
| pt-battery-endurance | Battery endurance profiling | TODO | (manual timing) |

### Parameter Tuning (6 tasks, 1 DONE)

| ID | Task | Status | Script |
|----|------|--------|--------|
| pt-pi-fps | Pi inference FPS benchmark | **DONE** | `tests/hardware/benchmark.py` |
| pt-altitude-sweep | Detection rate vs altitude | TODO | `tests/day_1_experiments/altitude_sweep.py` |
| pt-speed-sweep | Detection rate vs speed + blur | TODO | `tests/day_1_experiments/speed_sweep.py` |
| pt-model-compare | Compare all TFLite models | TODO | `tests/day_1_experiments/model_compare.py` |
| pt-conf-threshold | Tune confidence threshold | TODO | (after pt-altitude-sweep) |
| pt-ncnn-backend | Try NCNN inference backend | TODO | (after pt-pi-fps) |
| pt-resolution-tradeoff | Resolution vs FPS vs detection | TODO | `tests/hardware/benchmark.py` |

### Data Collection (4 tasks, 2 DONE)

| ID | Task | Status | Script |
|----|------|--------|--------|
| pt-training-data | Capture real training images | **DONE** | `capture_training.py` |
| pt-retrain-model | Retrain model on real aerial photos | **DONE** | `generate_dataset_v2.py` |
| pt-stream-latency | Test video stream latency | TODO | `pi_flight.py` |
| pt-comms-range | Wi-Fi + video stream range test | TODO | `pi_flight.py` |

---

## WBS Task Mapping

The following WBS tasks from `wbs-data.ts` map to L2 critical path steps:

| Critical Path Step | WBS Tasks |
|-------------------|-----------|
| cp-1 (Components healthy) | 2.2 Camera System (done), 4.2 Companion Computer (done), 2.3 CV Pipeline (done) |
| cp-2 (GPS fix) | 2.1.1 GPS module mount + lock test (done -- indoor only) |
| cp-2a (MP AUTO) | 5.1.3 RTL test (active), 5.1.4 Auto waypoint mode (done in sim) |
| cp-3 (CV check) | 2.3.4 Detection pipeline integration (done), 7.1.4 Camera-compute pipeline test (done) |
| cp-4 (Waypoints) | 5.1.5 Guided mode API control (done in sim), 5.2.1 Search pattern generation (done) |
| cp-6b (Geofence) | 5.4.1 Geofence setup (done in software), 5.2.2 NFZ boundary definition (done) |
| cp-7 (Search pattern) | 7.2.3 Waypoint following test (upcoming) |
| cp-8 (Detect + confirm) | 6.1.4 Target marking interface (done), 6.1.2 Custom telemetry dashboard (done) |
| cp-9 (Landing + payload) | 1.4.2 Release mechanism prototype (upcoming), 5.2.4 Delivery approach path (done) |
| cp-10 (PLB redirect) | -- no direct WBS task (R06 requirement) |
| cp-13 (Full mission) | 7.2.4 Full autonomous mission test (upcoming), 7.3.2 Simulated SAR semi-auto (upcoming) |

**Key WBS items still blocking:**
- 7.2.1 First hover test (upcoming) -- needed before any flight
- 7.2.2 Stabilized flight test (upcoming) -- needed for cp-2a
- 4.1.4 PID tuning flight (upcoming) -- needed for stable flight
- 1.4.1-1.4.3 Payload system (upcoming) -- needed for cp-9

---

## Estimated Time Budget

| Phase | Steps | Est. Time | Equipment Needed |
|-------|-------|-----------|-----------------|
| GPS Baseline | cp-2 | 30 min | Pi + Cube + GPS, outdoors |
| First Flight | cp-2a | 60 min | Full drone, RC, Mission Planner, battery |
| CV + Waypoints | cp-3, cp-4 | 60 min | Full drone + dummy on ground |
| Accuracy + Geofence | cp-5, cp-6, cp-6b | 90 min | Full drone + dummy + Mission Planner fence |
| Search Pattern | cp-7 | 30 min | Full drone, search_area.json |
| Detect + Confirm | cp-8 | 45 min | Full drone + dummy + browser |
| Landing + Payload | cp-9 | 45 min | Tarot servo wired, first aid kit |
| PLB Redirect | cp-10 | 30 min | Focus area defined |
| Items of Interest | cp-11 | 30 min | Objects scattered in field |
| SSSI Geofence | cp-12 | 45 min | SSSI fence uploaded |
| Full Mission | cp-13 | 60 min | Everything |
| **Total** | | **~8.5 hrs** | Multiple flight days |

**Note:** This assumes batteries, weather, and debugging time. Realistically, expect 2-3 full flight days to complete the critical path. Parallel tasks can be interleaved during battery changes and setup time.

---

## What's Next (Immediate Actions)

1. **cp-2: Outdoor GPS 3D fix** -- Take Pi + Cube outside, get satellite lock. This unblocks everything.
2. **cp-2a: MP AUTO waypoints** -- Safest possible first flight. No Python code involved.
3. **cp-3 + cp-4 (parallel)** -- First flights with our code. CV passive check + waypoint following.

**Before going to the field:**
- Verify bench tests pass: `preflight.py`, `0a_cube_commands.py`, `0b_bench_mission.py`
- Prepare `waypoints.json` on laptop: `python tests/flight/draw_waypoints.py`
- Prepare `search_area.json` on laptop: `python tests/flight/draw_search_area.py`
- Review `main.py --dry-run` output
- Print `docs/FLIGHT_DAY_CHECKLIST.md`
- Charge batteries
