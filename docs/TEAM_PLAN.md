# Team Plan - Parallel Workstreams

5 team members, working in parallel, coming together at integration points.

---

## Workstreams

```
STREAM A: Computer Vision        ──────┐
STREAM B: Hardware & Connectivity ─────┤
STREAM C: Search Logic & Algorithms ───┼──> INTEGRATION ──> FLIGHT TEST
STREAM D: Ground Station & Operator ───┤
STREAM E: Safety & Testing ────────────┘
```

---

## Stream A: Computer Vision (Pi + Camera)

**Goal**: AI detection running reliably on Pi with real camera.

### A1. Camera works on Pi
- [ ] Connect camera ribbon to Pi CSI port
- [ ] Run `python tests/pi_1_camera.py`
- [ ] Confirm frames captured (check resolution, FPS)
- [ ] If OpenCV fails, confirm picamera2 fallback works
- **Test**: Script prints "Camera opened successfully" + frame size

### A2. AI detection works on Pi
- [ ] Copy `best.tflite` to Pi
- [ ] Run `python tests/pi_2_detect.py` (with screen connected)
- [ ] Hold dummy printout in front of camera
- [ ] Confirm bounding boxes appear around dummy on screen
- [ ] Press 's' to save a detection snapshot for the team
- **Test**: Detection boxes visible, confidence > 0.4

### A3. Detection speed is acceptable
- [ ] Run `python tests/pi_3_benchmark.py`
- [ ] Record: avg inference time, FPS
- [ ] Target: < 200ms per frame (5+ FPS)
- [ ] If too slow: try `--headless` mode, lower resolution, or quantised model
- **Test**: Benchmark report shows avg < 200ms

### A4. Headless mode works (for flight)
- [ ] Run `python tests/pi_2_detect.py --headless`
- [ ] Confirm detections print to terminal without display
- [ ] Compare speed: headless vs display mode
- [ ] Document speed difference
- **Test**: Terminal shows detection messages, speed same or faster

### A5. Detection works at different distances/angles
- [ ] Test with dummy printout at various distances (simulate altitudes)
- [ ] Test at different angles (not just head-on)
- [ ] Test in different lighting (indoor, outdoor, shadow)
- [ ] Record confidence at each distance → find max reliable detection height
- **Deliverable**: Table of distance vs confidence for the team

---

## Stream B: Hardware & Connectivity

**Goal**: All physical connections verified and working.

### B1. Pi ↔ Cube serial link
- [ ] Wire: Pi TX (GPIO 14) → Cube RX, Pi RX (GPIO 15) → Cube TX, GND → GND
- [ ] Run `python tests/test_cube.py`
- [ ] Confirm heartbeat received
- [ ] Record baud rate that works (57600 or 921600)
- **Test**: Heartbeat + attitude data displayed

### B2. Cube GPS fix
- [ ] Take Cube outdoors (or near window)
- [ ] Run `python tests/test_cube.py`
- [ ] Confirm GPS shows valid lat/lon (not 0,0)
- [ ] Record time to first fix
- **Test**: GPS coordinates shown in test_cube output

### B3. Telemetry radio (Cube ↔ GS)
- [ ] Plug radio into Cube TELEM1
- [ ] Plug matching radio into laptop USB
- [ ] Open Mission Planner, connect via COM port
- [ ] Confirm HUD shows attitude, map shows drone icon
- **Test**: Mission Planner connected and showing live data

### B4. RC controller bound
- [ ] Bind RC transmitter to receiver on Cube
- [ ] Verify channels in Mission Planner (Radio Calibration)
- [ ] Set up kill switch / flight mode switch
- [ ] Test manual override: switch to STABILIZE from GUIDED
- **Test**: Mission Planner shows RC input, mode switch works

### B5. Full connectivity map
- [ ] Run `python tests/test_all.py`
- [ ] All links show OK
- [ ] Run `python preflight.py`
- [ ] All checks pass (serial, heartbeat, camera, AI model)
- **Test**: preflight.py shows 0 failures

---

## Stream C: Search Logic & Algorithms

**Goal**: Optimised search pattern and detection logic. Can be developed on laptop with simulation.

### C1. Review current search pattern
- [ ] Run `python simulation.py` on laptop
- [ ] Observe lawnmower pattern: coverage, overlap, efficiency
- [ ] Document: how many waypoints, total distance, estimated time at search speed
- **Deliverable**: Map screenshot with coverage analysis

### C2. Optimise search pattern
- [ ] Adjust waypoint spacing based on real FOV at search altitude
- [ ] Consider: start position, wind direction, area shape
- [ ] Test different patterns: lawnmower, spiral, expanding square
- [ ] Pick best pattern for the search area
- **Deliverable**: Updated waypoints, before/after comparison

### C3. Detection logic improvements
- [ ] Current: detect → centre → descend → verify → land
- [ ] Consider: multi-pass confirmation (detect on 3 consecutive frames?)
- [ ] Consider: confidence threshold tuning (from Stream A5 distance tests)
- [ ] Consider: what happens if target moves between detect and descend?
- **Deliverable**: Updated state machine logic if needed

### C4. PLB / focused search (if applicable)
- [ ] Design PLB trigger logic (when does focused search start?)
- [ ] Design focused search pattern (smaller lawnmower in focus area)
- [ ] Implement and test in simulation
- **Deliverable**: Working PLB focused search in simulator

### C5. Landing spot selection
- [ ] Current: lands N/S/E/W of target based on wind
- [ ] Review: is offset distance correct for safety?
- [ ] Consider: obstacle detection before landing?
- **Deliverable**: Validated landing logic

---

## Stream D: Ground Station & Operator

**Goal**: Operator can monitor and control the mission from the ground.

### D1. Mission Planner setup
- [ ] Connect via telemetry radio (from B3)
- [ ] Configure map view, HUD, quick actions
- [ ] Set up geofence for search area
- [ ] Set up failsafe: RTL on low battery, signal loss
- **Test**: Mission Planner shows drone on map with geofence

### D2. SSH control from GS to Pi
- [ ] Pi and laptop on same WiFi network
- [ ] SSH into Pi: `ssh pi@<pi-ip>`
- [ ] Run `python main.py` over SSH
- [ ] Confirm Y/N prompt works over SSH
- **Test**: Can start mission and confirm target remotely

### D3. Detection image to GS (Phase 9)
- [ ] When Pi detects target, save frame as JPEG
- [ ] Send JPEG to GS over WiFi (SCP, or simple HTTP)
- [ ] Operator sees what the drone saw before pressing Y/N
- [ ] Keep it simple: no constant video stream
- **Test**: Detection image appears on GS within 2 seconds

### D4. Mission logging
- [ ] Log all state transitions to file
- [ ] Log all detections with GPS to CSV (pi_4_detect_and_log.py already does this)
- [ ] After mission: review logs on GS
- **Deliverable**: Post-flight log analysis

---

## Stream E: Safety & Testing

**Goal**: Safe to fly, tested at every level.

### E1. Pre-flight checklist validated
- [ ] Walk through docs/PREFLIGHT_CHECKLIST.md with real hardware
- [ ] Update checklist based on what was missing or wrong
- [ ] Confirm all preflight.py checks pass
- **Deliverable**: Updated PREFLIGHT_CHECKLIST.md

### E2. Failsafe testing
- [ ] Test RTL on signal loss (turn off RC)
- [ ] Test RTL on low battery (simulate in Mission Planner)
- [ ] Test kill switch
- [ ] Test geofence breach behaviour
- **Test**: Drone returns home or disarms safely in all cases

### E3. Ground test (no props)
- [ ] Run full mission with real Cube, no props
- [ ] Verify: arm, takeoff command, waypoint navigation, mode changes
- [ ] Mission Planner shows all commands being received
- **Test**: Full state machine runs without errors

### E4. Tethered test (with props)
- [ ] Props on, drone tethered or held
- [ ] Short hover test in GUIDED mode
- [ ] Verify motors respond correctly
- [ ] Test manual override (switch to STABILIZE)
- **Test**: Drone hovers stable, responds to commands

### E5. First autonomous flight
- [ ] Full mission: takeoff → search → detect → descend → verify → land
- [ ] Operator monitors on Mission Planner
- [ ] RC ready for manual override at all times
- **Test**: Complete mission successfully

---

## Integration Points

These are when the team comes together. Don't move to the next integration until all prerequisites pass.

### Integration 1: Pi Works
**When**: A1-A4 + B1 done
**Test**: Run `python tests/pi_4_detect_and_log.py`
- Camera detects dummy → buzzer beeps → GPS/yaw logged
- Proves CV and Cube both work on Pi

### Integration 2: Full System on Bench
**When**: A1-A5 + B1-B5 + D1-D2 done
**Test**: Run `python preflight.py` → all pass, then `python main.py` with SITL
- Pi runs real camera + simulated flight over WiFi
- Mission Planner shows drone flying
- Hold dummy in front of camera → detection → Y/N over SSH

### Integration 3: Ground Test
**When**: Integration 2 + C1-C3 + E1-E3 done
**Test**: Run `python main.py` connected to real Cube (no props)
- Full state machine runs with real hardware
- Mission Planner shows real commands
- All failsafes tested

### Integration 4: Flight
**When**: Integration 3 + E4 done
**Test**: Full autonomous mission with props
- Everything works end-to-end
- Operator can intervene at any time

---

## Flight Test Plan

Limited flight time - make every flight count. Each flight has a specific goal and data to collect.

### Pre-Flight: Prepare Data Collection
- [ ] Ensure `detection_log.csv` logging is on (pi_4_detect_and_log.py or main.py)
- [ ] Mission Planner set to record telemetry log (.tlog)
- [ ] Place dummy target at known GPS coordinates (measure with phone GPS app)
- [ ] Measure dummy from above: note its size in metres
- [ ] Note weather: wind speed/direction, lighting conditions, time of day
- [ ] Assign roles: pilot (RC), operator (GS + SSH), data recorder (notes), safety observer

### Flight 1: Hover + CV Calibration
**Goal**: Find out at what altitude CV reliably detects the dummy.

**Procedure**:
1. Place dummy on ground at known GPS position
2. Take off manually, hover directly above dummy
3. Hold at each altitude for 10 seconds while logging:

| Altitude | Detected? | Confidence | Pixel size | Notes |
|----------|-----------|------------|------------|-------|
| 5m | | | | |
| 10m | | | | |
| 15m | | | | |
| 20m | | | | |
| 25m | | | | |
| 30m | | | | |
| 35m | | | | |

4. Note the max altitude where detection is reliable (conf > 0.5 consistently)

**Data to collect**:
- [ ] `detection_log.csv` - confidence vs altitude
- [ ] Mission Planner tlog - actual GPS positions
- [ ] Screenshots of detection at each altitude
- [ ] Note: does dummy appear in camera at 30m? How many pixels?

**What this tells us**:
- Is `TARGET_ALT = 30m` too high? Should we search lower?
- Is `VERIFY_ALT = 15m` the right descent target?
- Do we need to retrain the model for aerial views?

### Flight 2: FOV + GPS Accuracy
**Goal**: Verify the camera FOV calculation and GPS position estimation.

**Procedure**:
1. Place 4 markers at known GPS positions (corners of a rectangle)
2. Hover at search altitude (30m or whatever Flight 1 determined)
3. Fly over each marker, let CV detect it
4. Compare: detected GPS vs actual GPS

| Marker | Actual GPS | Detected GPS | Error (m) |
|--------|-----------|--------------|-----------|
| 1 | | | |
| 2 | | | |
| 3 | | | |
| 4 | | | |

**Data to collect**:
- [ ] `detection_log.csv` - detected positions
- [ ] Actual marker GPS positions (measured beforehand)
- [ ] Camera frame screenshots showing markers

**What this tells us**:
- Is `SENSOR_WIDTH_MM = 5.02` correct?
- Is `FOCAL_LENGTH_MM = 6.0` correct?
- How far off is our GPS estimation? (acceptable: < 5m)
- Do we need to calibrate camera parameters?

### Flight 3: Search Pattern
**Goal**: Test the full lawnmower search pattern.

**Procedure**:
1. Place dummy somewhere in the search area
2. Run full autonomous mission (`python main.py`)
3. Let drone search, detect, and attempt to verify

**Data to collect**:
- [ ] Total search time from takeoff to detection
- [ ] Which waypoint was dummy detected at?
- [ ] Did drone centre on target correctly?
- [ ] Did descent work properly?
- [ ] Y/N prompt timing - was there enough time to decide?
- [ ] Mission Planner tlog - full flight path
- [ ] `detection_log.csv` - all detection events
- [ ] `flight_log.csv` - state transitions

**What this tells us**:
- Is search speed (10 m/s) too fast for detection?
- Does the lawnmower pattern have gaps?
- Is the state machine timing right for real flight?

### Flight 4: Edge Cases
**Goal**: Test difficult scenarios.

**Procedure** (pick relevant ones):
- [ ] Dummy at edge of search area (not centre)
- [ ] Dummy partially hidden (under bush/shadow)
- [ ] Press N on verify - does it resume search correctly?
- [ ] Multiple passes over same area - consistent detection?
- [ ] What happens in wind? Does drone drift during descent?

**Data to collect**:
- [ ] False positive count (detected something that isn't dummy)
- [ ] False negative count (flew over dummy but missed it)
- [ ] Landing accuracy: distance from target to landing spot

### After Each Flight: Data Review Checklist
- [ ] Download `detection_log.csv` from Pi
- [ ] Download `flight_log.csv` from Pi
- [ ] Save Mission Planner tlog
- [ ] Note any bugs, unexpected behaviour, or tuning needed
- [ ] Update config.py if parameters need changing:
  - `TARGET_ALT` - search altitude
  - `VERIFY_ALT` - descent altitude
  - `SEARCH_SPEED_MPS` - too fast/slow?
  - `SENSOR_WIDTH_MM` / `FOCAL_LENGTH_MM` - if GPS estimation is off
  - Detection confidence threshold (0.4) - too sensitive/not enough?

### Parameters We're Calibrating

| Parameter | Current value | What affects it | Calibrated by |
|-----------|--------------|-----------------|---------------|
| `TARGET_ALT` | 30m | Max detection height | Flight 1 |
| `VERIFY_ALT` | 15m | Descent for confirmation | Flight 1 |
| `SEARCH_SPEED_MPS` | 10 m/s | Time per frame at speed | Flight 3 |
| `SENSOR_WIDTH_MM` | 5.02mm | GPS estimation from pixels | Flight 2 |
| `FOCAL_LENGTH_MM` | 6.0mm | GPS estimation from pixels | Flight 2 |
| Confidence threshold | 0.4 | False positives vs misses | Flight 1 + 4 |

---

## Who Does What

| Stream | Focus | Can start now? | Needs hardware? |
|--------|-------|---------------|-----------------|
| A: CV | Camera + AI on Pi | When Pi arrives | Pi + Camera |
| B: Hardware | Wiring + connections | When hardware arrives | Pi + Cube + Radios + RC |
| C: Search Logic | Algorithms + patterns | YES (laptop simulation) | No |
| D: Ground Station | Mission Planner + operator | Partly (MP setup) | Telemetry radio for full test |
| E: Safety | Testing + checklists | Partly (review docs) | All hardware for full test |

**Right now** (before hardware): Streams C and D can start. Review and improve search logic in simulation, set up Mission Planner configuration, review safety checklists.

---

## Test Scripts Quick Reference

| Script | What it tests | Stream |
|--------|--------------|--------|
| `tests/pi_1_camera.py` | Camera gives frames | A |
| `tests/pi_2_detect.py` | AI detection with display | A |
| `tests/pi_2_detect.py --headless` | AI detection without display | A |
| `tests/pi_3_benchmark.py` | Inference speed | A |
| `tests/test_cube.py` | Cube heartbeat + GPS | B |
| `tests/test_all.py` | Full connectivity map | B |
| `tests/pi_4_detect_and_log.py` | CV + Cube: detect, beep, log | A+B |
| `tests/pi_6_fov_test.py` | Bench FOV calibration (camera over ruler) | A |
| `tests/pi_7_alt_test.py` | Flight FOV calibration (hover at 2 altitudes) | A+B |
| `tests/pi_8_camera_test.py` | Camera FPS, pipeline FPS, motion blur vs detection | A |
| `tests/pi_9_resolution_test.py` | Resolution vs speed vs detection trade-off | A |
| `preflight.py` | Final go/no-go | E |
| `simulation.py` | Search pattern simulation | C |
| `main.py` | Full mission | All |
