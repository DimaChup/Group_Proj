# Flight Day Tests — What to Run, When, Why

**This is the testing companion to FLIGHT_DAY_CHECKLIST.md.**
Checklist = what to do. This file = what data to collect and how.

---

## Test Directory Map

```
tests/
├── calibration/          TUNE NUMBERS (before first flight, re-check on day)
│   ├── fov_calibrate.py      Measure FOV → FOCAL_LENGTH_MM (bench, ruler)
│   ├── fov_test_simple.py    Quick FOV sanity check (bench)
│   ├── alt_test.py           FOV from real altitude (flight day, needs Cube)
│   └── lens_calibrate.py     Lens distortion (checkerboard → undistort coeffs)
│
├── diagnostics/          IS IT WORKING? (run when something seems broken)
│   ├── diagnostics.py        3-view dashboard: connectivity / camera+AI / telemetry
│   ├── cube_monitor.py       Raw MAVLink inspector (message types, rates)
│   ├── camera_stream.py      MJPEG stream test (verify laptop can see Pi camera)
│   ├── camera_stream_fast.py Optimised stream
│   └── camera_stream_h264.py H.264 stream (needs ffmpeg, not recommended)
│
├── hardware/             DOES THIS PART WORK? (individual component checks)
│   ├── gps_test.py           GPS lock, satellites, fix type
│   ├── gps_health.py         Deep GPS diagnostics (CAN bus, params)
│   ├── benchmark.py          AI speed on synthetic image (no camera needed)
│   ├── cv_benchmark.py       AI speed on live camera + blur test
│   └── buzzer_test.py        Buzzer melody test
│
├── flight/               CAN IT FLY? (numbered by progression, simple → complex)
│   ├── 0a_cube_commands.py   Bench: test individual commands (mode, arm)
│   ├── 0b_bench_mission.py   Bench: full command sequence (no props needed)
│   ├── 0c_feedback_test.py   Bench: vision→GPS pipeline (no commands)
│   ├── 1_passive_flight.py   Manual RC flight, CV watches (ZERO commands)
│   ├── 2_waypoint_test.py    Fly 4 GPS waypoints (SENDS COMMANDS, no CV)
│   ├── 3_auto_detect.py      MP AUTO + AI → GUIDED hover (SENDS COMMANDS)
│   └── 4_detect_and_center.py Autonomous pattern + center (SENDS COMMANDS)
│
├── day_1_experiments/    WHAT'S THE DATA? (structured experiments, CSV output)
│   ├── altitude_sweep.py     Detection rate vs altitude (10-30m)
│   ├── speed_sweep.py        Detection rate vs flyover speed + blur metric
│   ├── gps_accuracy.py       GPS estimate error vs known dummy position
│   ├── gps_drift.py          GPS noise floor while hovering
│   ├── model_compare.py      Compare multiple TFLite models (bench or flight)
│   └── detection_log.py      General catch-all flight logger
│
└── laptop/               DEVELOPMENT ONLY (not for Pi or flight day)
    ├── test_all.py           Connectivity check (laptop)
    ├── test_camera.py        Camera preview
    ├── test_cube.py          Cube heartbeat (SITL)
    ├── test_cv.py            AI model test
    ├── test_tflite.py        TFLite backend test
    ├── debug_tflite.py       Raw TFLite output inspector
    └── cv_test_synthetic.py  AI on synthetic images
```

---

## Pre-Flight Day (at home, bench)

Do these BEFORE going to the field. They don't need GPS or flying.

```
[ ] 1. FOV calibration (bench)
      python tests/calibration/fov_calibrate.py --headless
      → Update config.py: FOCAL_LENGTH_MM = ____

[ ] 2. Lens distortion calibration (if you have a checkerboard)
      python tests/calibration/lens_calibrate.py
      → Saves calibration_data.npz

[ ] 3. Model comparison (bench)
      python tests/day_1_experiments/model_compare.py --list
      python tests/day_1_experiments/model_compare.py --frames 50
      → Pick best model, copy to best.tflite

[ ] 4. AI benchmark
      python tests/hardware/cv_benchmark.py --headless
      → Note FPS, set --fps flag to match on flight day

[ ] 5. Bench integration test (carry drone over printed dummy)
      python tests/flight/0c_feedback_test.py --headless
      → Verify: camera sees → AI detects → GPS estimate updates
      → This proves the full pipeline WITHOUT flying

[ ] 6. Bench mission test (motors won't spin without RC+GPS)
      python tests/flight/0b_bench_mission.py
      → Verify: commands reach Cube, ACKs received

[ ] 7. Dry-run pattern verification (no GPS needed)
      python main.py --dry-run
      → Verify: SEARCH_AREA_GPS covers intended field
      → Note: waypoint count, estimated flight time
      → If wrong: update config.py SEARCH_AREA_GPS, re-run

[ ] 8. Dry-run with alternate model (if available)
      python main.py --dry-run --model models/best2.tflite
      → Verify: model loads correctly
```

---

## Flight Day — Setup Phase (at field, before flying)

```
[ ] 1. System diagnostics
      python tests/diagnostics/diagnostics.py --headless
      → All 5 subsystems green: Camera, AI, Cube, GPS, GS

[ ] 2. GPS lock
      python tests/hardware/gps_test.py
      → fix_type=3, satellites >= 8, LED = green

[ ] 3. Camera stream test
      python tests/diagnostics/camera_stream.py
      → Open http://PI_IP:8090 on laptop, verify video shows

[ ] 4. Quick AI benchmark (confirm Pi speed)
      python tests/hardware/benchmark.py
      → Note: avg ms = ____, FPS = ____
```

---

## Flight Day — Experiments (during flight)

Run these during manual RC flights. ALL are passive (zero commands).
Pilot flies, Pi watches and logs. Each produces a CSV.

### Experiment 1: Altitude Sweep (1 battery)
```
python tests/day_1_experiments/altitude_sweep.py --headless --stream
```
- Pilot hovers above dummy at 10m (30s), 15m, 20m, 25m, 30m
- Script auto-bins by altitude
- Output: `exp_altitude_TIMESTAMP.csv`
- Result: max reliable detection altitude → set config.py TARGET_ALT

### Experiment 2: Speed Sweep (same or next battery)
```
python tests/day_1_experiments/speed_sweep.py --headless --stream --alt 15
```
- Pilot flies over dummy at 3, 5, 7 m/s at 15m altitude
- Script measures detection rate + blur metric per speed
- Output: `exp_speed_TIMESTAMP.csv`
- Result: max reliable speed → set config.py SEARCH_SPEED_MPS

### Experiment 3: GPS Accuracy (same flight as altitude sweep)
```
python tests/day_1_experiments/gps_accuracy.py --headless --stream --dummy-gps LAT,LON
```
- Needs known dummy GPS position (from Mission Planner or phone)
- Estimates GPS from pixel position, compares to truth
- Output: `exp_gps_TIMESTAMP.csv`
- Result: estimation error in metres → predicts landing accuracy

### Experiment 4: GPS Drift (while hovering for altitude sweep)
```
python tests/day_1_experiments/gps_drift.py --headless --duration 60
```
- Pilot hovers still for 60s
- Measures GPS jitter (CEP50, CEP95)
- Output: `exp_drift_TIMESTAMP.csv`
- Result: GPS noise floor → minimum possible estimation error

### Experiment 5: General Detection Log (any flight)
```
python tests/day_1_experiments/detection_log.py --headless --stream --save-detections
```
- Catch-all logger. Fly anywhere, logs everything
- Saves detection images with bounding boxes
- Output: `exp_detlog_TIMESTAMP.csv` + `detection_images/` folder
- Review after: false positive rate, missed detections, blur

---

## Flight Day — Progressive Flight Tests

These are the actual flight tests from FLIGHT_DAY_CHECKLIST.md.
Run in order. Each builds trust before adding risk.

### Step 1: Mission Planner AUTO (no code)
- Upload 4 waypoints in MP → fly → RTL
- Proves: Cube, GPS, motors, RTL work
- No Pi scripts involved

### Step 1.5: Waypoint Test (your code, no CV)
```
python tests/flight/2_waypoint_test.py --dry-run    # verify first
python tests/flight/2_waypoint_test.py --alt 10     # real flight
```
- Arms, takes off, flies 4 GPS waypoints, lands
- Proves: your MAVLink commands work on real hardware

### Step 2: Passive Flight (CV, zero commands)
```
python tests/flight/1_passive_flight.py --headless --stream
```
- Pilot flies manually, Pi watches + logs + buzzer
- Proves: CV works outdoors, calibrates detection altitude
- Can run altitude/speed sweep experiments simultaneously

### Step 3: Dashboard (pi_flight.py — full system)
```
python pi_flight.py --fps 4
```
- Browser dashboard + video stream
- N = investigate, Y = confirm, L = land
- First test with FAKE DET button (no CV needed)
- Then with real CV detections

### Step 4: Detect and Center (intermediate)
```
python tests/flight/4_detect_and_center.py --alt 15 --dry-run
python tests/flight/4_detect_and_center.py --alt 15
```
- Flies waypoints + AI → centers on target → hovers
- Intermediate between passive and full main.py
- Operator: 'l' = land, 'r' = resume, 'q' = RTL

### Step 5: Full Autonomous (main.py)
```
python main.py --dry-run                          # verify pattern first (no GPS needed)
python main.py --dry-run --model models/best2.tflite  # verify with different model
python main.py                                     # real flight (default model)
python main.py --model models/best2.tflite         # real flight with alternate model
```
- `--dry-run`: prints lawnmower waypoints, state machine walkthrough, saves map visualization — no arming, no GPS
- `--model PATH`: switch AI model without copying files (default: best.tflite)
- Full state machine: search → detect → center → descend → verify → land
- The real mission

---

## After Flight — Data Processing

All experiment CSVs are in project root. To analyze:

```python
import pandas as pd
import matplotlib.pyplot as plt

# Altitude sweep
df = pd.read_csv("exp_altitude_TIMESTAMP.csv")
grouped = df[df.alt_bucket != ""].groupby("alt_bucket")
rates = grouped.apply(lambda g: g.detection.eq("YES").mean())
print(rates)

# GPS accuracy
df = pd.read_csv("exp_gps_TIMESTAMP.csv")
errors = df[df.error_m != ""].error_m.astype(float)
print(f"Mean error: {errors.mean():.1f}m, Median: {errors.median():.1f}m")
```

---

## Quick Troubleshooting

| Problem | Run this |
|---------|----------|
| Camera not working | `tests/diagnostics/diagnostics.py --headless` (View 2) |
| AI not detecting | `tests/hardware/cv_benchmark.py --headless` |
| Cube not responding | `tests/diagnostics/cube_monitor.py` |
| GPS won't lock | `tests/hardware/gps_test.py` then `gps_health.py` |
| Buzzer not working | `tests/hardware/buzzer_test.py` |
| Stream not showing | `tests/diagnostics/camera_stream.py` |
| Commands not reaching Cube | `tests/flight/0a_cube_commands.py` |
| Pipeline not working together | `tests/flight/0c_feedback_test.py --headless` |
| Which model to use | `tests/day_1_experiments/model_compare.py` |
| Everything seems broken | `tests/diagnostics/diagnostics.py --headless` (View 1) |
