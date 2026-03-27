# Real Flight Workflow

Step-by-step workflow for running the SAR mission on a Raspberry Pi with a real Cube.
Copy-paste ready for the Pi terminal.

---

## Pre-Flight (at Home)

### 1. Push latest code to GitHub

```bash
git add -A && git commit -m "pre-flight" && git push
```

### 2. Verify dry-run works

```bash
export DRONE_MODE=REAL
python main.py --dry-run --headless --alt 35
```

Check output: waypoints cover the intended search area, estimated flight time is
reasonable, no errors. If the search area is wrong, update `SEARCH_AREA_GPS` in
`config.py` (or check that `flight_plans/AENGM0074.kml` is present and correct).

### 3. Check model is deployed

```bash
cp cv_models/sar_v2_1088/best.tflite best.tflite
```

### 4. Pack gear

```
[ ] Laptop + charger
[ ] RC controller (charged)
[ ] LiPo batteries (charged, 4.2V/cell)
[ ] Pi power source (USB battery pack or drone BEC)
[ ] Phone (hotspot)
[ ] Printed dummy (for placing on ground)
[ ] Measuring tape
```

---

## At the Field

### Network

Connect Pi and laptop to the same WiFi (phone hotspot is easiest).
Note the Pi IP:

```bash
hostname -I
```

---

### Terminal 1: mavproxy (ALWAYS start first)

```bash
sudo /opt/mavlink/mavlink-venv/bin/mavproxy.py \
  --master=/dev/ttyAMA0 --baudrate=921600 --streamrate=10 \
  --out=udpout:127.0.0.1:14550 --out=tcpin:0.0.0.0:5762
```

Wait for: `Detected vehicle 1:0` + `online system 1` + `Mode STABILIZE`

If mavproxy is already running or stuck:

```bash
sudo pkill -f mavproxy; sleep 2
```

Then start it again.

---

### Terminal 2: pull code and activate venv

```bash
cd ~/dima/Group_Proj && source pienv/bin/activate
git pull
```

If pienv is broken or missing:

```bash
python3 -m venv --system-site-packages pienv
source pienv/bin/activate
pip install -r requirements_pi.txt
pip install ai-edge-litert
```

---

### System Check

```bash
python tests/diagnostics/diagnostics.py
```

All must be green:

```
[ ] Camera:   OK
[ ] AI Model: OK (best.tflite loaded)
[ ] Cube:     OK (heartbeat received)
[ ] GPS:      satellites > 0 (wait for fix_type=3)
[ ] Battery:  > 14.4V (3.6V/cell minimum)
```

---

### GPS Lock

```bash
python tests/hardware/gps_test.py
```

Wait for:

```
[ ] fix_type = 3 (3D fix)
[ ] Satellites >= 8
```

This can take 1-15 minutes outdoors. Do not fly until GPS is locked.

---

### Laptop: Mission Planner

```
Connection > TCP > PI_IP > port 5762
```

Confirm: map shows drone position, GPS satellites visible in bottom bar.

---

### Laptop: Browser

Open `http://PI_IP:8090` for video stream and command buttons.

---

## Running the Mission

### Option A: Passive CV (pilot flies RC, Pi watches, ZERO commands)

```bash
python tests/flight/1_passive_flight.py --headless --stream
```

Browser: `http://PI_IP:8090` -- watch for detections at various altitudes.

### Option B: Full Dashboard (semi-autonomous with operator commands)

```bash
export DRONE_MODE=REAL
python pi_flight.py --fps 4
```

Browser: `http://PI_IP:8090` -- use buttons to command the drone.

### Option C: Full Autonomous Mission

```bash
export DRONE_MODE=REAL
python main.py --headless --alt 35
```

Browser: `http://PI_IP:8090` -- Y/N verification at VERIFY stage.

Other useful flags:

```
--model cv_models/sar_v2_1088/best.tflite   # use specific model
--dry-run                                     # verify pattern without flying
--smart-detect                                # multi-frame confirmation
--no-nfz                                      # disable geofence (testing only)
--speed 2                                     # SITL speedup (simulation only)
--beacon-delay 30                             # simulate PLB signal after N seconds
```

---

## During Flight

### Dashboard Buttons (browser)

```
N = investigate nearest cluster (fly to it)
Y = confirm as real dummy
I = log as item of interest
X = discard as false positive
L = land 7.5m north of estimate
B = PLB beacon redirect
M = resume manual control
FAKE DET = create fake detection for testing
```

### Kill Switch

**RC mode switch to STABILIZE = emergency override.**
Our code stops sending commands immediately. RC pilot's hand on switch at all times.

### Ctrl+C

All flight scripts trigger RTL on Ctrl+C. The drone will return to launch and land.

---

## After Flight

### Check logs

```bash
cat logs/flight_log.csv
```

Review: detection positions, confidence values, GPS estimates, state transitions.

### Check coverage

If `--dry-run` was used before flight, compare `dry_run_pattern.jpg` with actual
flight path in Mission Planner.

### Record results

```
CV performance:
  Max detection altitude = ____m
  Avg confidence         = ____
  Inference rate on Pi   = ____ FPS
  False positives seen   = ____

Landing accuracy:
  GPS estimate error     = ____m
  Landing distance       = ____m

Config updates needed:
  [ ] TARGET_ALT = ____
  [ ] SEARCH_SPEED_MPS = ____
  [ ] CONFIDENCE_THRESHOLD = ____
```

---

## Troubleshooting

### No camera

```bash
# Check camera detected:
libcamera-hello --list-cameras

# Kill stuck camera process:
sudo pkill -f libcamera; sudo pkill -f python; sleep 2

# Quick test:
python -c "
from picamera2 import Picamera2
cam = Picamera2()
cam.configure(cam.create_still_configuration(main={'size': (640,480), 'format': 'RGB888'}))
cam.start()
import time; time.sleep(1)
frame = cam.capture_array()
print('Camera OK:', frame.shape)
cam.stop(); cam.close()
"
```

### No Cube heartbeat

```bash
# Is mavproxy running?
ps aux | grep mavproxy

# Restart mavproxy:
sudo pkill -f mavproxy; sleep 2
sudo /opt/mavlink/mavlink-venv/bin/mavproxy.py \
  --master=/dev/ttyAMA0 --baudrate=921600 --streamrate=10 \
  --out=udpout:127.0.0.1:14550 --out=tcpin:0.0.0.0:5762

# Test connection:
python tests/laptop/test_cube.py
```

If no heartbeat: check serial cable TX/RX not swapped, check shared ground wire,
check Cube is powered.

### No GPS lock

```bash
python tests/hardware/gps_test.py
```

- Move to open area (away from buildings/trees)
- Cold start after power cycle can take 10-15 minutes
- Here 3+ LED: blue = no lock, green = locked
- Wait. Do not fly without fix_type = 3.

### No detections

```bash
# Check model is loaded:
python -c "from vision import VisionSystem; v = VisionSystem(); print('Model loaded:', v.model is not None)"

# Swap to best model:
cp cv_models/sar_v2_1088/best.tflite best.tflite

# Lower confidence threshold (edit config.py):
# CONFIDENCE_THRESHOLD = 0.2  (already low, try 0.15 if needed)

# Or use --model flag:
python pi_flight.py --fps 4 --model cv_models/sar_v2_1088/best.tflite
```

### Qt/Display crash over PuTTY

Add `--headless` flag to any script, or use the browser dashboard instead.

### Port 8090 already in use

```bash
sudo pkill -f python; sleep 2
```

Then restart your script.

### Model swap on the fly

```bash
# Stop current script (Ctrl+C)
cp cv_models/sar_v2_1088/best.tflite best.tflite
# Restart script
```

Available models:

```
cv_models/sar_v2_1088/best.tflite  -- retrained v2, BEST (mAP50=0.995)
cv_models/sar_640/best.tflite      -- earlier training at 640x640
cv_models/sar_1280/best.tflite     -- earlier training at 1280x1280
models/human.tflite                -- COCO person detector (80 classes, backup)
```
