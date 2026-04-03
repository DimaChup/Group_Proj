# Flight Day Checklist

**Print this. Follow top to bottom. Tick boxes and fill blanks as you go.**

---

## 1. Day Before

```
[ ] Push latest code:  git add -A && git commit -m "flight day" && git push
[ ] Charge drone LiPo (4.2V/cell), charge Pi power bank
[ ] Copy best model to root:  cp cv_models/sar_v2_1088/best.tflite best.tflite
[ ] Pack: laptop, RC, phone (hotspot), measuring tape, printed dummy
[ ] Verify dry-run on laptop:  python main.py --dry-run
```

### Bench Calibration (do at home if possible)

Place camera pointing **straight down** at EXACTLY 1m above a ruler/tape.
Measure visible width in frame (expected ~92cm with FOCAL_LENGTH_MM = 5.46).

```bash
python tests/calibration/fov_calibrate.py          # interactive (with display)
python tests/calibration/fov_test_simple.py         # quick single measurement
```

If visible width differs from 92cm:
```
FOCAL_LENGTH_MM = (SENSOR_WIDTH_MM * height_mm) / visible_width_mm
                = (5.02 * 1000) / visible_width_mm

Example: see 85cm -> FOCAL_LENGTH_MM = 5020 / 850 = 5.91
```

- [ ] Measured visible width at 1m: ______ cm
- [ ] Computed FOCAL_LENGTH_MM: ______ (current: 5.46)
- [ ] Updated config.py if changed
- [ ] Repeat at 50cm and 150cm -- values should agree within 0.3mm

---

## 2. Hardware Setup

```
[ ] Assemble drone, mount Pi + camera facing DOWN
[ ] Connect Pi to Cube serial (TX->RX, RX->TX, shared GND)
[ ] Power Pi (USB-C power bank or drone BEC)
[ ] Power Cube (LiPo connected)
[ ] RC transmitter ON, bound to Cube
```

---

## 3. Network

Both Pi and laptop on same WiFi (phone hotspot is easiest).

```bash
# On Pi -- find IP:
hostname -I
```

**Pi IP: `_________________`**

```bash
# On Pi -- pull latest code:
cd ~/dima/Group_Proj && git pull
```

---

## 4. Calibration Checks (on Pi, at the field)

### Camera Color Check (1 min)

IMX296 outputs **BGR** despite picamera2 labeling it RGB888.

```bash
python tests/diagnostics/camera_stream.py
# Open http://PI_IP:8090 in browser
```

- [ ] Stream looks natural (skin tones correct, sky is blue not orange)
- [ ] Do **NOT** add `cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)` -- it is already BGR

### FOV Calibration (if not done day before, 10 min)

```bash
python tests/calibration/fov_calibrate.py --headless   # Pi over SSH
python tests/calibration/fov_test_simple.py             # quick check
```

Current values:
```
SENSOR_WIDTH_MM  = 5.02   (IMX296 datasheet, fixed)
FOCAL_LENGTH_MM  = 5.46   (calibrated 2026-03-11)
IMAGE_W          = 1456   (IMX296 native)
IMAGE_H          = 1088   (IMX296 native)
```

### Pixel-to-GPS Pipeline Verification (optional, 10 min)

```bash
python tests/calibration/gps_estimate_calibrate.py          # terminal (SSH)
python tests/calibration/gps_calibrate_gui.py               # GUI (needs display)
python tests/calibration/gps_estimate_calibrate.py --no-mavlink  # without Cube
```

1. Hold camera pointing down at known height (e.g., 1.5m)
2. Place dummy at known horizontal offset from directly below camera
3. Enter height and offset when prompted
4. Repeat 3-4 times at different offsets, Ctrl+C for summary

- [ ] Estimated distance vs actual: error < 10%

### Lens Undistortion (optional, skip unless edge accuracy matters)

- [ ] `calibration_data.npz` exists and is > 1KB? If corrupt/empty: `rm calibration_data.npz`
- [ ] Cost: ~1.5ms/frame (negligible)

---

## 5. Terminal Setup (3 PuTTY windows to Pi)

### Terminal 1: mavproxy (ALWAYS start first)

```bash
sudo pkill -f mavproxy; sleep 2
sudo /opt/mavlink/mavlink-venv/bin/mavproxy.py \
  --master=/dev/ttyAMA0 --baudrate=921600 --streamrate=10 \
  --out=udpout:127.0.0.1:14550 \
  --out=udpout:127.0.0.1:14551 \
  --out=tcpin:0.0.0.0:5762
```

Wait for: `Detected vehicle 1:0` + `online system 1` + `Mode STABILIZE`

**PORT CONFLICT WARNING:**
- If Robin/Zian run their OWN mavproxy: **two mavproxy on the same serial port will NOT work**
- Solution: run ONE shared mavproxy with extra `--out` for each consumer
- Add `--out=udpout:127.0.0.1:14552` etc for additional scripts
- passive_watch uses 14550, main.py uses 14550 -- if running both, set `DRONE_CONN` env var

### Terminal 2: Robin's passive_watch

```bash
cd ~/dima/Group_Proj && source pienv/bin/activate
python field_tools/passive_watch.py \
  --port 8091 \
  --conf 0.3 \
  --smart-estimate --smart-min 5 --smart-radius 2.0 \
  --smart-dir robin_detections \
  --model best.tflite
```

**Browser:** `http://PI_IP:8091/`

Key facts:
- Sends ZERO commands to drone -- completely safe
- Reads GPS from mavproxy (udpin:14550) for geotagging
- `--no-mavlink` skips GPS (no geotagging -- mostly useless)
- `--port 8091` avoids conflict with main.py on 8090
- `--class-filter person` for use with human.tflite model

### Terminal 3: main.py (autonomous mission)

```bash
cd ~/dima/Group_Proj && source pienv/bin/activate
python main.py --headless --alt 25
```

**Browser:** `http://PI_IP:8090/`

### CRITICAL: Camera Sharing

**passive_watch and main.py CANNOT run at the same time.**

Both open the Pi camera -- only ONE process can use `/dev/video0`.

**Workflow:**
1. Run passive_watch FIRST (Robin's CV logging during manual flights)
2. Ctrl+C passive_watch when done
3. Wait 2 seconds for camera release
4. THEN start main.py for autonomous mission

If camera stuck:
```bash
sudo pkill -f libcamera; sudo pkill -f python; sleep 2
```

### Stream Port Reference

| Script | Default Port | Fix |
|--------|-------------|-----|
| passive_watch.py | 8090 | Use `--port 8091` |
| main.py | 8090 | Keep default |
| capture_training.py | 8091 | Already different |

### Laptop Connections

```
Mission Planner:    TCP → PI_IP → port 5762
passive_watch:      http://PI_IP:8091/
main.py:            http://PI_IP:8090/
```

---

## 6. Preflight Safety Checks

### Hardware Health

```bash
python tests/laptop/test_camera.py          # camera gives frames?
python tests/laptop/test_cv.py --camera      # AI model loads + detects?
python tests/laptop/test_cube.py             # Cube heartbeat + GPS + battery?
python preflight.py                          # full system check
```

- [ ] Camera returns frames (no black/mangled images)
- [ ] AI model loads, detects dummy in frame
- [ ] Cube heartbeat received
- [ ] Battery voltage > 14.8V (4S) or > 22.2V (6S)

### GPS Fix

```bash
python tests/hardware/gps_health.py          # wait for convergence
python tests/hardware/gps_test.py            # live altitude + GPS display
```

- [ ] GPS fix type >= 3, satellites >= 8
- [ ] Here3+ LED = flashing GREEN (blue = no lock)
- [ ] HDOP < 1.5

### Kill Switch Test

- [ ] RC kill switch to STABILIZE in Mission Planner -- confirm mode changes
- [ ] Flip back to GUIDED -- confirm mode changes back
- [ ] RC failsafe: Mission Planner > Config > Failsafe > Radio = RTL

### Inference Speed

```bash
python tests/hardware/benchmark.py           # 50 runs, timing report
python tests/hardware/benchmark_full.py      # comprehensive (all models)
```

- [ ] Inference time: ______ ms (target: < 250ms TFLite, < 100ms NCNN)
- [ ] FPS: ______ (target: > 4 FPS)
- [ ] Detections: ______/50

### Dry Run

```bash
python main.py --dry-run
python main.py --dry-run --alt 20
```

- [ ] KML zones loaded (search area, flight area, SSSI)
- [ ] Lawnmower waypoints generated (check count and spacing)
- [ ] Geofence active (no waypoints inside SSSI)
- [ ] `dry_run_pattern.jpg` saved and looks correct
- [ ] No import errors or config warnings

---

## 7. GPS / Altitude Error Check (5 min each)

### Altitude (Barometer) Drift

ArduCopter reports altitude from barometer (relative to arm point). Drifts with temperature/pressure.

1. Arm the drone on flat ground (altitude reads 0m)
2. Wait 5 minutes, note altitude reading
3. If drift > 0.5m, recalibrate baro in Mission Planner (Initial Setup > Mandatory > Accel Calibration)

- [ ] Altitude drift after 5 min on ground: ______ m
- [ ] Drift < 0.5m?

### GPS Accuracy

1. Place drone at a **known** GPS position (e.g., Take-Off: 51.423406, -2.671446)
2. Record reported GPS for 60 seconds

```bash
python tests/day_1_experiments/gps_drift.py   # 60s, CSV output
```

- [ ] CEP50: ______ m (50% of readings within this radius)
- [ ] CEP95: ______ m
- [ ] Max deviation: ______ m
- [ ] Satellite count: ______
- [ ] CEP50 < 3m? (expected with Here 3+)

---

## 8. Progressive Flight Steps

### Step 1: Mission Planner AUTO (no custom code)

```
[ ] Upload 4-waypoint square in MP at 15m altitude
[ ] Arm via RC, switch to AUTO
[ ] Drone flies pattern, RTLs
[ ] PASSED? Yes / No
```

### Step 2: Waypoint test (your code, no CV)

```bash
python tests/flight/2_waypoints.py --dry-run     # verify plan
python tests/flight/2_waypoints.py --alt 10       # real flight
```

```
[ ] Arms, takes off, flies waypoints, lands
[ ] PASSED? Yes / No
```

### Step 3: Passive CV (pilot flies RC, Pi watches)

**Stop main.py first. Start passive_watch.**

```bash
python field_tools/passive_watch.py --port 8091 --conf 0.3 --smart-estimate
```

Browser: `http://PI_IP:8091/`

```
[ ] Pilot hovers over dummy at 10m, 15m, 20m, 25m, 30m (30s each)
[ ] Max detection altitude: ___m, confidence: ___
[ ] Fly over dummy at 3/5/7 m/s at 15m
[ ] Max speed with detection: ___ m/s
```

**If CV not detecting:**
```bash
# Swap model:
cp cv_models/sar_v2_1088/best.tflite best.tflite

# Or try COCO person detector:
python field_tools/passive_watch.py --port 8091 --model models/human.tflite --class-filter person
```

### Step 4: Full autonomous mission

**Stop passive_watch first. Wait 2s. Start main.py.**

```bash
python main.py --headless --alt 25
```

Browser: `http://PI_IP:8090/`

```
[ ] Drone searches lawnmower pattern
[ ] Detection triggers investigation
[ ] At VERIFY stage: press Y (confirm) or N (reject) in browser
[ ] If Y: drone approaches and lands
[ ] Measure landing distance from dummy: ___m
```

---

## 9. During Flight

### Kill Switch

**RC mode switch to STABILIZE -- overrides EVERYTHING, always.**

RC pilot's hand on kill switch at ALL times. Ctrl+C on any script triggers RTL.

### What to Watch

- Browser stream: detection boxes appearing?
- Terminal: state transitions (SEARCH -> CENTERING -> DESCENDING -> VERIFY)
- Mission Planner: altitude, GPS track, mode

### Y/N/I Decisions at VERIFY

| Key | Meaning | Effect |
|-----|---------|--------|
| Y | Confirm target | Drone approaches and lands |
| N | Reject / false positive | Resume search pattern |
| I | Mark as interest | Log position, resume search |
| X | Mark as false positive | Log and ignore |

### Model Swap (if CV not detecting mid-flight)

```bash
# Stop script first (Ctrl+C), then:
cp cv_models/sar_v2_1088/best.tflite best.tflite   # best retrained model
cp models/human.tflite best.tflite                  # COCO person detector (backup)

# Or use --model flag (no copy needed):
python main.py --headless --model cv_models/sar_v2_1088/best.tflite
```

Lower confidence if missing detections: edit `vision.py` line ~174, change `0.4` to `0.3` or `0.25`

---

## 10. Post-Flight

### Copy Data to Laptop

```bash
scp pi@PI_IP:~/dima/Group_Proj/flight_log.csv .
scp -r pi@PI_IP:~/dima/Group_Proj/detections/ .
scp -r pi@PI_IP:~/dima/Group_Proj/robin_detections/ .
scp -r pi@PI_IP:~/dima/Group_Proj/mission_detections/ .
```

### Commit on Pi

```bash
cd ~/dima/Group_Proj
git add -A && git commit -m "flight day data" && git push
```

### Record Results

```
Max detection altitude:   ___m
Max detection speed:      ___ m/s
Avg confidence:           ___
Inference FPS on Pi:      ___
Landing distance error:   ___m
False positives seen:     ___
Config updates needed:    TARGET_ALT=___, SEARCH_SPEED_MPS=___
```

### Config Values to Update After Flight

```python
# config.py -- fill in measured values
SENSOR_WIDTH_MM  = 5.02    # IMX296 datasheet (don't change)
FOCAL_LENGTH_MM  = ____    # From FOV calibration
IMAGE_W          = 1456    # IMX296 native (don't change)
IMAGE_H          = 1088    # IMX296 native (don't change)
TARGET_ALT       = ____    # Search altitude, lower if detection poor from 35m
CONFIDENCE_THRESHOLD = ____ # Start at 0.3, lower if missing targets
UNDISTORT_ENABLED = ____   # True if valid calibration_data.npz, False otherwise
```

---

## 11. Error Budget Reference

| Source | Typical Error | Controllable? | How to Reduce |
|--------|--------------|---------------|---------------|
| GPS position | 2-3m CEP | No | Wait for more sats, use RTK |
| Altitude (baro) | 0.5-1m | Partially | Recalibrate before flight |
| FOV / focal length | 0-5% if calibrated | Yes | Bench calibration at 1m |
| Lens distortion | < 0.5m at edges | Optional | Checkerboard calibration |
| Camera tilt | 0-2m if tilted | Yes | Mount camera straight down |
| GPS timing lag | ~1m at 5m/s | Known | Average multiple passes |
| **TOTAL (RSS)** | **~3-4m CEP** | | **~2.3m CEP measured** |

### Focal Length Error Impact

| Altitude | 10% focal length error = position error |
|----------|----------------------------------------|
| 10m      | 0.9m                                   |
| 20m      | 1.8m                                   |
| 35m      | 3.2m                                   |

### Altitude Error Impact

```
At 35m altitude:
  1m baro error = 2.9% GSD error = ~0.9m ground position error at frame edge
  2m baro error = 5.7% GSD error = ~1.8m ground position error at frame edge
```

### GSD Table (metres per pixel at each altitude)

| Altitude | GSD (m/px) | Frame width (m) | Frame height (m) |
|----------|-----------|-----------------|-------------------|
| 10m | 0.0063 | 9.2 | 6.9 |
| 15m | 0.0095 | 13.8 | 10.3 |
| 20m | 0.0126 | 18.4 | 13.7 |
| 25m | 0.0158 | 23.0 | 17.2 |
| 30m | 0.0189 | 27.6 | 20.6 |
| 35m | 0.0221 | 32.2 | 24.0 |
| 40m | 0.0252 | 36.7 | 27.4 |
| 50m | 0.0315 | 45.9 | 34.3 |

Formula: `GSD = (5.02 * alt) / (5.46 * 1456)`

### Pipeline Math at Current Config

```
GSD = (SENSOR_WIDTH_MM * altitude) / (FOCAL_LENGTH_MM * IMAGE_W)
    = (5.02 * 35) / (5.46 * 1456)
    = 0.0221 m/pixel

Full frame width on ground = 1456 * 0.0221 = 32.2m
Full frame height on ground = 1088 * 0.0221 = 24.0m
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Camera "in use" | `sudo pkill -f libcamera; sudo pkill -f python; sleep 2` |
| No heartbeat | Check serial cable TX<->RX, shared GND. Is Cube powered? |
| Qt crash in PuTTY | Add `--headless` flag. Or run on Pi screen. |
| GPS won't lock | Open area, wait 5-15 min. Here3+ LED blue=no lock, green=locked. |
| Port 8090 in use | Kill old script: `sudo pkill -f passive_watch; sleep 2` |
| mavproxy won't start | `sudo pkill -f mavproxy; sleep 2` then retry |
| Pi IP changed | `hostname -I` on Pi |
| Git pull fails | `cd ~/dima/Group_Proj && git stash && git pull` |
