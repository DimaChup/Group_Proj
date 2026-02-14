# SAR Drone - Roadmap

## End Goal Architecture
```
[Camera] --CSI--> [Pi] --Serial UART--> [Cube] --Telemetry Radio--> [GS / Mission Planner]
                   |                                                    |
                   +------------- WiFi (video stream) -----------------+
                   |
                   +------------- WiFi (SSH for Y/N confirm) ----------+
```

### What Each Component Does
| Component | Role |
|-----------|------|
| Pi | Brain - runs CV, decides where to fly, sends commands to Cube |
| Camera | Eyes - CSI ribbon to Pi, captures frames |
| Cube | Pilot - handles flight, motors, GPS, IMU |
| GS (laptop) | Monitor - Mission Planner shows drone on map, operator confirms target |
| Telemetry Radio | Cube <-> GS wireless link (independent of Pi) |
| WiFi | Pi <-> GS for video stream + SSH control |

### Connections Summary
| Link | Protocol | Purpose |
|------|----------|---------|
| Camera -> Pi | CSI ribbon | Video frames for CV |
| Pi -> Cube | Serial UART (/dev/ttyAMA0) | MAVLink flight commands + telemetry |
| Cube -> GS | Telemetry radio | Live monitoring in Mission Planner |
| Pi -> GS | WiFi (video stream) | Operator sees what drone sees |
| GS -> Pi | WiFi (SSH) | Operator sends Y/N confirmation |

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

### Phase 4: Pi + Camera (NEXT - when hardware arrives)
- [ ] Set up Pi with venv (--system-site-packages for picamera2)
- [ ] pip install: pymavlink opencv-python-headless "numpy<2" tflite-runtime
- [ ] Clone git repo onto Pi
- [ ] Run pi_1_camera.py - verify camera works
- [ ] Run pi_2_detect.py - verify AI detects dummy printout
- [ ] Run pi_3_benchmark.py - check inference speed (<200ms target)
- [ ] If camera needs picamera2: verify BGR/RGB handling in pi_1_camera.py
- [ ] Compare pi_3_benchmark results with Windows/Docker runs

### Phase 5: Pi + Cube (after camera works)
- [ ] Wire Cube TELEM2 to Pi UART (/dev/ttyAMA0)
- [ ] Run test_cube.py - verify heartbeat, GPS, attitude
- [ ] Run test_all.py - full connectivity map
- [ ] Run preflight.py - all checks pass
- [ ] Test main.py in REAL mode with SITL over WiFi (Pi camera + simulated flight)

### Phase 6: Full Integration (flight ready)
- [ ] Telemetry radio: Cube TELEM1 to GS
- [ ] Verify Mission Planner shows drone position
- [ ] SSH into Pi from GS laptop
- [ ] Run main.py in REAL mode over SSH
- [ ] Test Y/N confirmation over SSH
- [ ] Ground test: run full mission without props, verify state transitions

### Phase 7: Nice-to-Have (after core works)
- [ ] Video stream: Pi sends camera frames to GS over WiFi
- [ ] Auto-confirm: skip Y/N if confidence > threshold
- [ ] PLB focused search: narrower lawnmower after signal received
- [ ] Web UI on Pi for Y/N instead of SSH terminal
- [ ] Log camera frames to disk for post-flight analysis

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
python tests/pi_1_camera.py      # Step 1: camera
python tests/pi_2_detect.py      # Step 2: camera + AI
python tests/pi_3_benchmark.py   # Step 3: speed check
python tests/test_cube.py        # Step 4: Cube connection
python tests/test_all.py         # Step 5: everything
python preflight.py              # Step 6: final check
python main.py                   # Step 7: fly
```

### Environment Variables
```bash
export DRONE_MODE=REAL                        # or SIMULATION
export DRONE_CONN=tcp:192.168.1.42:5762       # or /dev/ttyAMA0
export DRONE_BAUD=57600                       # serial baud rate
```
