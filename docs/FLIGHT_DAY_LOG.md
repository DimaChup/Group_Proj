# Flight Day Log — 2026-03-11

## Setup
- **Location:** ___
- **Weather:** ___
- **Wind:** ___
- **Team:** ___
- **Pi IP:** 192.168.1.3
- **Cube:** ArduCopter V4.6.3, CubeOrangePlus, QUAD/X
- **Battery:** 90% at start

## Phase 1: Setup
- [x] Mavproxy running (Terminal 1)
- [x] Diagnostics — AI OK, Cube OK, GPS lock at 85m
- [ ] FOV calibration — SKIPPED
- [ ] Benchmark — FPS: ___, avg inference: ___ms

## Phase 2: Training Data Capture
- [ ] capture_training.py running on port 8091
- [ ] Photos taken: ___
- [ ] Video recorded: ___

## Step 1: Mission Planner AUTO (no custom code)
- [ ] 4 waypoints uploaded
- [ ] Drone flew pattern
- [ ] RTL landed safely
- **Result:** PASS / FAIL
- **Notes:**

## Step 1.5: Waypoint Test (2_waypoints.py)
- [ ] Dry-run passed
- [ ] Real flight at 10m
- [ ] Flew 4 waypoints
- [ ] Landed safely
- **Result:** PASS / FAIL
- **Notes:**

## Step 2: Passive CV (1_passive_flight.py)
- [ ] Stream visible at http://PI_IP:8090

| Altitude | Detections? | Confidence | Notes |
|----------|------------|------------|-------|
| 10m      |            |            |       |
| 15m      |            |            |       |
| 20m      |            |            |       |
| 25m      |            |            |       |
| 30m      |            |            |       |

| Speed @15m | Detections? | Blur? | Notes |
|------------|------------|-------|-------|
| 3 m/s     |            |       |       |
| 5 m/s     |            |       |       |

- **Max detection altitude:** ___m
- **Result:** PASS / FAIL
- **Notes:**

## Step 3: Dashboard (pi_flight.py)
- [ ] Dashboard loaded in browser
- [ ] Detection appeared
- [ ] N → investigated cluster
- [ ] Classified (Y/I/X)
- [ ] L → landed 7.5m north
- **Landing distance from dummy:** ___m
- **Result:** PASS / FAIL
- **Notes:**

## Step 5: Full Autonomous (main.py) — if time allows
- [ ] Search pattern flew correctly
- [ ] Detection triggered
- [ ] Centred on target
- [ ] Operator verified
- [ ] Landed near target
- **Result:** PASS / FAIL
- **Notes:**

## Config Updates After Flight
```
TARGET_ALT = ___
SEARCH_SPEED_MPS = ___
FOCAL_LENGTH_MM = ___
Confidence threshold = ___
```

## Issues Encountered


## Lessons Learned

