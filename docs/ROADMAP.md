# SAR Drone - Roadmap

## The Final Goal

An autonomous SAR drone that searches an area, detects a casualty with computer vision, and lands nearby - with an operator on the ground monitoring everything and confirming the target.

### What Happens in a Mission
1. Operator sets up search area on GS (Mission Planner)
2. Drone takes off and flies a lawnmower search pattern autonomously
3. Pi runs CV on every camera frame, looking for the dummy/casualty
4. When detected: drone centres on target, descends, operator gets a prompt
5. Operator sees the detection image and confirms Y/N
6. On Y: drone lands near the casualty. On N: drone resumes search.
7. Throughout: GS shows drone position on map, operator can intervene via RC

### System Architecture
```
                         [RC Controller]
                              |
                         (manual override)
                              |
[Camera] --CSI--> [Pi] --Serial UART--> [Cube] --Telemetry Radio--> [GS / Mission Planner]
                   |                                                    |
                   +------------ WiFi (detection image) ---------------+
                   |                                                    |
                   +------------ WiFi (SSH operator Y/N) --------------+
```

### What Each Component Does
| Component | Role |
|-----------|------|
| Pi | Brain - runs CV, decides where to fly, sends MAVLink commands to Cube |
| Camera | Eyes - CSI ribbon to Pi, captures frames for CV |
| Cube | Pilot - handles flight, motors, GPS, IMU, safety |
| GS (laptop) | Monitor - Mission Planner shows drone on map, operator watches |
| RC Controller | Safety override - operator can take manual control at any time |
| Telemetry Radio | Cube <-> GS wireless link (independent of Pi) |
| WiFi | Pi <-> GS for detection images + SSH operator control |

### Connections
| # | Link | Protocol | What flows |
|---|------|----------|------------|
| 1 | Camera -> Pi | CSI ribbon | Video frames for CV processing |
| 2 | Pi -> Cube | Serial UART (/dev/ttyAMA0) | MAVLink: arm, takeoff, goto, mode changes |
| 3 | Cube -> GS | Telemetry radio (433/915MHz) | Live position, attitude, battery on Mission Planner |
| 4 | RC -> Cube | RC receiver | Manual override, kill switch |
| 5 | Pi -> GS | WiFi | Detection image when target spotted (not constant stream to save bandwidth) |
| 6 | GS -> Pi | WiFi (SSH) | Operator Y/N confirmation |

### Design Decisions
- **CV runs on Pi**, not GS — no video stream delay in the detection loop
- **Image sent to GS only on detection** — saves bandwidth, reduces lag vs constant streaming
- **RC always has override** — safety, required for any real flight
- **Pi talks to Cube, not GS** — GS is monitoring only, Pi makes the decisions

---

## Steps to Get There

### Phase 1: Simulation on Laptop (DONE)
- [x] State machine: SEARCH -> CENTERING -> DESCENDING -> VERIFY -> LANDING
- [x] Search pattern (lawnmower with optimised start)
- [x] Simulated drone view from map.jpg
- [x] AI detection with Ultralytics YOLO
- [x] GPS calculation from pixel coordinates
- [x] Mission Planner + SITL integration
- [x] Operator Y/N confirmation at verify altitude
- [x] Landing spot selection (N/S/E/W)
- [x] Final accuracy measurement

### Phase 2: Multi-Platform CV (DONE)
- [x] Multi-backend vision.py (Ultralytics for dev, TFLite for Pi)
- [x] Docker Pi environment test (packages load)
- [x] TFLite position bug fixed (0-1 normalised coords)
- [x] Backend comparison: Ultralytics (319,369) vs TFLite (321,371) - match
- [x] Auto-detect connection in config.py (serial/WSL/localhost)
- [x] Environment variable overrides (DRONE_MODE, DRONE_CONN, DRONE_BAUD)

### Phase 3: Test Infrastructure (DONE)
- [x] preflight.py - quick connectivity check with IP prompt
- [x] tests/test_camera.py - camera test with live preview
- [x] tests/test_cube.py - serial + heartbeat + GPS + attitude + battery
- [x] tests/test_cv.py - model load + detection on static/live
- [x] tests/test_all.py - full connectivity map
- [x] tests/pi_1_camera.py - Pi camera (OpenCV + picamera2 fallback)
- [x] tests/pi_2_detect.py - Pi camera + AI detection live
- [x] tests/pi_3_benchmark.py - speed + accuracy comparison across backends
- [x] tests/debug_tflite.py - raw TFLite output inspector
- [x] tests/pi_6_fov_test.py - bench FOV calibration (camera over ruler)
- [x] tests/pi_7_alt_test.py - flight FOV calibration (hover at 2 altitudes)
- [x] tests/pi_8_camera_test.py - camera FPS, pipeline FPS, blur vs detection
- [x] tests/pi_9_resolution_test.py - resolution vs speed vs detection trade-off

### Phase 4: Pi + Camera
- [ ] Set up Pi with venv (--system-site-packages for picamera2)
- [ ] pip install: pymavlink opencv-python-headless "numpy<2" tflite-runtime
- [ ] Clone git repo onto Pi
- [ ] Run pi_1_camera.py - verify camera works
- [ ] Run pi_2_detect.py - verify AI detects dummy printout
- [ ] Run pi_3_benchmark.py - check inference speed (<200ms target)
- [ ] If camera needs picamera2: verify BGR/RGB handling in pi_1_camera.py
- [ ] Compare pi_3_benchmark results with Windows/Docker runs

### Phase 5: Pi + Cube Wired (after camera works)
- [ ] Wire Cube TELEM2 to Pi UART (/dev/ttyAMA0)
- [ ] Run test_cube.py - verify heartbeat, GPS, attitude
- [ ] Run pi_4_detect_and_log.py - detect dummy, buzzer beeps, log altitude + yaw
- [ ] Run test_all.py - full connectivity map
- [ ] Run preflight.py - all checks pass

### Phase 6: SITL over WiFi (real camera, simulated flight)
- [ ] Run SITL on laptop, Pi connects over WiFi (`export DRONE_CONN=tcp:<laptop-ip>:5762`)
- [ ] Run main.py on Pi with real camera
- [ ] Drone "flies" search pattern in Mission Planner
- [ ] Hold dummy printout in front of camera to trigger detection
- [ ] Verify full state machine: SEARCH -> DETECT -> CENTRE -> DESCEND -> VERIFY (Y/N) -> LAND
- [ ] Test Y/N confirmation over SSH

### Phase 7: Real Cube, No Props (ground test)
- [ ] Telemetry radio: Cube TELEM1 to GS
- [ ] Verify Mission Planner shows drone position via telemetry radio
- [ ] Run main.py on Pi connected to real Cube (no props!)
- [ ] Verify: arm command sent, waypoints sent, mode changes happen
- [ ] Mission Planner shows commands being received
- [ ] Test kill switch / disarm

### Phase 8: First Flight
- [ ] Props on, full system
- [ ] Ground test: motors spin, throttle responds, kill switch works
- [ ] Short hover test in GUIDED mode
- [ ] Full autonomous mission

### Phase 9: GS Integration (operator experience)
- [ ] Pi sends detection image to GS on detection (not constant stream)
- [ ] Operator sees detection image + confidence on GS before Y/N
- [ ] Log camera frames to disk for post-flight review
- [ ] Consider: simple web UI on Pi instead of SSH terminal for Y/N

### Phase 10: Nice-to-Have (polish)
- [ ] Auto-confirm: skip Y/N if confidence > threshold
- [ ] PLB focused search: narrower lawnmower after signal received
- [ ] Constant video stream option (if bandwidth allows)
- [ ] Multiple target support (detect, mark, continue searching)

---

## Quick Reference

### Pi Setup Commands
```bash
python3 -m venv --system-site-packages pienv
source pienv/bin/activate
pip install pymavlink opencv-python-headless "numpy<2" tflite-runtime
git clone <repo-url>
```

### Test Order on Pi
```bash
# Camera only (no Cube needed)
python tests/pi_1_camera.py           # Step 1: camera gives frames?
python tests/pi_2_detect.py           # Step 2: AI detects dummy?
python tests/pi_3_benchmark.py        # Step 3: inference speed ok?
python tests/pi_8_camera_test.py      # Step 3b: camera FPS, blur vs detection
python tests/pi_9_resolution_test.py  # Step 3c: resolution sweet spot
python tests/pi_6_fov_test.py         # Step 4: bench FOV check (camera over ruler)

# Cube wired up
python tests/test_cube.py             # Step 5: heartbeat + GPS + attitude?
python tests/pi_4_detect_and_log.py   # Step 6: detect + buzzer + log GPS/yaw

# Full system
python preflight.py                   # Step 7: final go/no-go

# First flight (manual hover)
python tests/pi_7_alt_test.py         # Step 8: FOV calibration at 2 altitudes
python tests/pi_2_detect.py --headless  # Step 9: max detection altitude

# Autonomous
python main.py                        # Step 13: full mission
```

### Environment Variables
```bash
export DRONE_MODE=REAL                        # or SIMULATION
export DRONE_CONN=tcp:192.168.1.42:5762       # or /dev/ttyAMA0
export DRONE_BAUD=57600                       # serial baud rate
```
