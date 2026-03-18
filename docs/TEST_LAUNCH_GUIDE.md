# Test Script Launch Guide

> Copy-paste commands for every test script. Follow the order on flight day.
> See also: LAUNCH_GUIDE.md (main.py flags), FLIGHT_DAY_CHECKLIST.md (full procedure)

---

## Setup (every session)

```bash
# Pi Terminal 1: Start mavproxy (ALWAYS first)
sudo /opt/mavlink/mavlink-venv/bin/mavproxy.py \
  --master=/dev/ttyAMA0 --baudrate=921600 --streamrate=10 \
  --out=udpout:127.0.0.1:14550 --out=tcpin:0.0.0.0:5762

# Pi Terminal 2: Activate venv
cd ~/dima/Group_Proj && source pienv/bin/activate

# Laptop (simulation): Activate venv
cd "c:\Users\Bristol\Desktop\AI for Robotics\v3"
venv\Scripts\activate
set DRONE_MODE=SIMULATION
```

---

## Phase 1: Bench Tests (indoors, no props, no GPS needed)

### 1.1 AI Benchmark — is inference fast enough?

```bash
# Pi:
python tests/hardware/benchmark.py

# Laptop:
python tests/hardware/benchmark.py

# With custom image:
python tests/hardware/benchmark.py my_image.jpg
```
**Pass:** <250ms avg on Pi, detections > 0
**Output:** timing stats + detection confidence to terminal

### 1.2 Full Benchmark — all models compared

```bash
python tests/hardware/benchmark_full.py
```
**Pass:** all models load, timing report printed

### 1.3 Cube Commands — can Pi talk to Cube?

```bash
python tests/flight/0a_cube_commands.py
```
**Pass:** heartbeat received, mode changes ACKed, params readable
**Risk:** LOW — reads/writes modes and params, no arming

### 1.4 Bench Mission — full command sequence (no props!)

```bash
# Safe mode (skip arm):
python tests/flight/0b_bench_mission.py

# With arm attempt (remove props first!):
python tests/flight/0b_bench_mission.py --with-arm
```
**Pass:** all commands ACKed in sequence
**Risk:** LOW — arms motors briefly (no props = no danger)

### 1.5 Vision Pipeline — camera + AI + GPS estimation

```bash
# With display:
python tests/flight/0c_feedback_test.py

# Headless (SSH):
python tests/flight/0c_feedback_test.py --headless
```
**Pass:** detections appear when pointing camera at dummy, GPS estimate printed
**Risk:** ZERO — no Cube commands

### 1.6 FOV Calibration — get accurate measurements

```bash
# Full calibration (ruler at known distance):
python tests/calibration/fov_calibrate.py

# Headless:
python tests/calibration/fov_calibrate.py --headless

# Quick single measurement:
python tests/calibration/fov_test_simple.py
```
**Output:** FOCAL_LENGTH_MM value → update config.py if different from 5.46

### 1.7 Lens Calibration — correct barrel distortion

```bash
python tests/calibration/lens_calibrate.py
```
**Needs:** printed checkerboard (14x9, 28mm squares)
**Output:** calibration_data.npz (auto-loaded by vision.py)

---

## Phase 2: Outdoor Pre-Flight (GPS lock required)

### 2.1 System Diagnostics — all green?

```bash
# With display:
python tests/diagnostics/diagnostics.py

# Headless (SSH):
python tests/diagnostics/diagnostics.py --headless
```
**Check:** Camera OK, AI OK, Cube OK, GPS OK (fix_type>=3, sats>=6), Battery >14.4V

### 2.2 GPS Health — deep GPS check

```bash
python tests/hardware/gps_test.py
```
**Pass:** fix_type >= 3, satellites >= 6, HDOP < 2.0
**Takes:** 1-5 minutes for first fix outdoors

### 2.3 GPS Drift — how noisy is our position?

```bash
# Leave drone stationary, run for 2-5 min:
python tests/day_1_experiments/gps_drift.py --headless
```
**Output:** gps_drift.csv, CEP50/CEP95 stats
**Pass:** CEP50 < 3m

### 2.4 Buzzer Test — verify buzzer works for passive detection

```bash
python tests/hardware/buzzer_test.py
```
**Pass:** buzzer plays melody

---

## Phase 3: First Flight (manual RC, progressive trust)

### 3.1 Passive Flight — pilot flies RC, Pi watches (ZERO commands)

```bash
# Headless + stream (recommended — view on laptop browser):
python tests/flight/1_passive_flight.py --headless --stream

# With frame saving (keeps every detection image):
python tests/flight/1_passive_flight.py --headless --stream --save-detections

# With all frames saved (every Nth frame):
python tests/flight/1_passive_flight.py --headless --stream --save-frames --save-every 4

# Custom stream settings:
python tests/flight/1_passive_flight.py --headless --stream --stream-res 640x480 --stream-quality 70
```
**View:** http://PI_IP:8090 on laptop browser
**Pass:** detects dummy from search altitude, GPS estimate within ~5m
**Risk:** ZERO — sends no commands to Cube

### 3.2 Altitude Sweep — at what height can we detect?

```bash
# During manual flight (pilot varies altitude 10-30m):
python tests/day_1_experiments/altitude_sweep.py --headless --stream
```
**Output:** altitude_sweep.csv (detection rate per altitude bucket)

### 3.3 Speed Sweep — at what speed do we lose detections?

```bash
python tests/day_1_experiments/speed_sweep.py --headless --stream
```
**Output:** speed_sweep.csv (detection rate vs groundspeed + blur metric)

---

## Phase 4: Autonomous Flight (sends commands — be ready on RC kill switch!)

### 4.1 Waypoint Flight — GPS navigation, no CV

```bash
# Dry-run first (verify waypoints, no arming):
python tests/flight/2_waypoints.py --dry-run

# Real flight (default: waypoints.json):
python tests/flight/2_waypoints.py

# Custom altitude:
python tests/flight/2_waypoints.py --alt 20

# Inline waypoints (no JSON file):
python tests/flight/2_waypoints.py --wp 51.4234,-2.6710 --wp 51.4238,-2.6695

# Simple 2-waypoint test (alternative):
python tests/flight/5_two_waypoints.py
```
**Kill switch:** RC mode switch to STABILIZE at any time
**Pass:** drone flies all waypoints and RTLs

### 4.2 AUTO + Detect — Mission Planner waypoints + AI hover

```bash
python tests/flight/3_auto_detect.py --headless --stream
```
**How:** Upload AUTO mission in Mission Planner. Script watches camera. On detection → switches to GUIDED hover.
**Kill switch:** RC to STABILIZE

### 4.3 Detect and Centre — full autonomous pattern + centering

```bash
python tests/flight/4_detect_and_center.py --headless --stream
```
**How:** Flies search pattern, detects target, centres on it, descends
**Kill switch:** RC to STABILIZE
**This is the step before running full main.py**

---

## Phase 5: Data Collection (during any flight)

### GPS Accuracy — how good is our GPS estimation?

```bash
# Place dummy at known GPS location, fly over it:
python tests/day_1_experiments/gps_accuracy.py --headless --stream \
  --truth-lat 51.42350 --truth-lon -2.66900
```
**Output:** gps_accuracy.csv (estimated vs actual position, error in meters)

### Detection Log — general flight logger

```bash
python tests/day_1_experiments/detection_log.py --headless --stream
```
**Output:** detection_log.csv (timestamp, position, detection, confidence)

### Model Comparison — which model is best on real data?

```bash
# List available models:
python tests/day_1_experiments/model_compare.py --list

# Benchmark all:
python tests/day_1_experiments/model_compare.py --frames 50
```

---

## Phase 6: Post-Flight Calibration

### GPS Ground Truth — validate CV accuracy

```bash
# After landing, measure dummy position with phone GPS:
python tests/calibration/gps_ground_truth.py \
  --truth-lat 51.42350 --truth-lon -2.66900
```
**Output:** comparison of CV-estimated vs actual GPS

### FOV at Altitude — refine from real flight data

```bash
# During hover at known altitude:
python tests/calibration/alt_test.py --headless
```

---

## Monitoring Tools (run alongside other scripts)

### Live Telemetry Dashboard

```bash
python tests/diagnostics/cube_monitor.py
```

### Camera Stream (standalone, no AI)

```bash
# Basic:
python tests/diagnostics/camera_stream.py

# Threaded (smoother):
python tests/diagnostics/camera_stream_fast.py
```
**View:** http://PI_IP:8090

### Live Map (laptop, shows drone position on satellite map)

```bash
python tests/flight/live_map.py
```

---

## Drawing Tools (laptop only, before flight day)

```bash
# Draw search polygon → search_area.json
python tests/flight/draw_search_area.py

# Draw transit route → transit.json
python tests/flight/draw_transit.py

# Draw waypoints → waypoints.json
python tests/flight/draw_waypoints.py
```
All output JSON files to project root. Push via git for Pi.

---

## Common Flags (most scripts support these)

| Flag | What |
|------|------|
| `--headless` | No cv2 window (required for SSH/PuTTY) |
| `--stream` | MJPEG video stream on port 8090 |
| `--stream-port N` | Custom stream port |
| `--stream-res WxH` | Stream resolution (e.g. 640x480) |
| `--stream-quality N` | JPEG quality 1-100 |
| `--dry-run` | Simulate without arming |
| `--save-detections` | Save detection images to disk |
| `--save-frames` | Save all frames |
| `--save-every N` | Save every Nth frame |

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `No module 'pymavlink'` | Activate venv first |
| `Camera in use` | Kill other scripts using camera (`pkill -f python`) |
| `Connection refused` | Start mavproxy first (Terminal 1) |
| No GPS lock | Wait 1-5 min outdoors, check antenna connection |
| Detection not working | Run benchmark.py to verify model loads |
| Stream not loading | Check Pi IP, firewall, port 8090 |
| Cube not responding | Check serial cable, baud 921600, mavproxy running |
| `COMMAND_ACK timeout` | Cube may be in wrong mode — check RC switch position |

---

## Quick Decision Tree

```
Something broken?
  ├── Camera? → tests/diagnostics/camera_stream.py
  ├── AI model? → tests/hardware/benchmark.py
  ├── Cube comms? → tests/flight/0a_cube_commands.py
  ├── GPS? → tests/hardware/gps_test.py
  └── Everything? → tests/diagnostics/diagnostics.py

Ready to fly?
  ├── First time? → 1_passive_flight (manual RC, CV watches)
  ├── GPS nav works? → 2_waypoints (auto waypoints, no CV)
  ├── CV works in air? → 4_detect_and_center (full auto)
  └── All good? → main.py (full mission)
```
