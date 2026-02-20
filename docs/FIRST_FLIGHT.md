# First Flight Plan — Manual Flight + CV Detection

**Goal**: Fly the drone manually on RC, let the Pi detect the dummy with CV, measure how
well everything works. No autonomous commands on the first flight.

---

## What We Have

```
Pilot flies RC manually
        ↓
Pi runs camera + AI model
        ↓
CV detects dummy → estimates GPS position (pixel-to-GPS projection)
        ↓
Estimate builds up over multiple observations (weighted average)
        ↓
Pilot presses N → drone guided to estimated position, descends to 15m
        ↓
Pilot visually confirms what it is:
    Y = real dummy → press L to land 7.5m away
    I = item of interest → logged, estimate reset, resume
    X = false positive → discarded, estimate reset, resume
```

This is the simple_simulator.py flow. It works end-to-end in simulation.
For first real flight, we use a subset of this — passive detection only.

---

## Progressive Flight Steps

### Step 1: Mission Planner AUTO Waypoints (no custom code)

**Purpose**: Prove the drone flies, GPS works, RTL works. Your code not involved.

```
1. Upload 4-waypoint square in Mission Planner (10-15m altitude)
2. Switch to AUTO on RC
3. Drone flies pattern, RTLs home
4. Kill switch: RC mode → STABILIZE at any time
```

**Pass criteria**: Drone completes waypoints and lands safely.

### Step 2: Pi Passive Flight (manual RC, CV logging only)

**Purpose**: See if CV detects the dummy from altitude. Measure detection rate,
confidence, max altitude, motion blur effects. Pi sends ZERO commands.

```bash
# Terminal 1 (mavproxy bridge)
sudo /opt/mavlink/mavlink-venv/bin/mavproxy.py \
  --master=/dev/ttyAMA0 --baudrate=921600 --streamrate=10 \
  --out=udpout:127.0.0.1:14550 --out=tcpin:0.0.0.0:5762

# Terminal 2 (passive detection)
cd ~/dima/Group_Proj && source pienv/bin/activate
python tests2/pi_passive_flight.py --headless --stream
# Or with Pi monitor: python tests2/pi_passive_flight.py
```

**Procedure**:
1. Place dummy on ground in open area
2. Pilot takes off, hovers at 10m above dummy → hold 30s
3. Climb to 15m → hold 30s
4. Climb to 20m, 25m, 30m → same
5. Fly over dummy at 3 m/s at 15m → observe
6. Fly over at 5 m/s, 7 m/s → observe

**Record**:
```
| Altitude | Detection rate | Avg confidence | Notes |
|----------|---------------|----------------|-------|
| 10m      |     ____%     |    ____        |       |
| 15m      |     ____%     |    ____        |       |
| 20m      |     ____%     |    ____        |       |
| 25m      |     ____%     |    ____        |       |
| 30m      |     ____%     |    ____        |       |

| Speed @15m | Detection rate | Blur? | Notes |
|------------|---------------|-------|-------|
| 3 m/s      |     ____%     |  Y/N  |       |
| 5 m/s      |     ____%     |  Y/N  |       |
| 7 m/s      |     ____%     |  Y/N  |       |
```

**Pass criteria**: CV detects dummy reliably at some altitude. We learn max detection
altitude and max speed.

**After flight**: Review `passive_flight_log.csv` — all detections with GPS, altitude,
confidence logged.

### Step 3: Manual Flight with GPS Estimation (future)

**Purpose**: Test the full simple_simulator flow on real hardware.

This needs a Pi-compatible version of simple_simulator.py (or main.py adapted for
manual flight). Not yet implemented — Step 2 data tells us if CV works first.

**The flow would be**:
1. Pilot flies manually on RC over search area
2. Pi runs CV, builds GPS estimates of detected items
3. Pilot presses N → Pi sends GUIDED waypoint to Cube → drone flies to estimate
4. Pilot classifies: Y (dummy), I (interest), X (false positive)
5. If Y → press L → Pi sends landing waypoint 7.5m north → drone lands
6. Kill switch: RC to STABILIZE at any time overrides everything

### Step 4: Full Autonomous Mission (main.py)

Autonomous sweep of area + detection + verification + landing.
Only after Steps 1-3 prove everything works.

---

## What We're Measuring on First Flight

| Measurement | Why it matters | How to get it |
|-------------|---------------|---------------|
| Max detection altitude | Sets TARGET_ALT in config.py | Hover at different heights |
| Max speed for detection | Sets SEARCH_SPEED_MPS | Fly over at different speeds |
| Detection confidence vs altitude | Know reliability | passive_flight_log.csv |
| Motion blur impact | Know if we need slower flight | Review saved frames |
| False positive rate | Know if threshold needs tuning | Count false detections |
| GPS accuracy | Know real-world drift | Compare GPS vs known position |

---

## Pre-Flight Checklist

```
[ ] Drone:
    [ ] Battery charged
    [ ] Props secure
    [ ] GPS lock (green LED on Here 3+)
    [ ] RC bound and tested (all sticks responsive)
    [ ] Kill switch configured (mode switch → STABILIZE)
    [ ] Failsafe set (RTL on RC loss)

[ ] Pi:
    [ ] Pi powered (USB battery or drone power)
    [ ] Camera connected, lens focused
    [ ] mavproxy running (Terminal 1)
    [ ] Mission Planner connected via TCP (optional, for monitoring)
    [ ] Script running, no errors (Terminal 2)
    [ ] Model loaded (check terminal output: "TFLite loaded" or similar)

[ ] Ground:
    [ ] Dummy placed in open area, visible from altitude
    [ ] Wind acceptable (< 15 km/h for first flight)
    [ ] No people/obstacles near dummy or flight path
    [ ] Spotter assigned (eyes on drone at all times)
```

---

## Pi Setup Reminder

If pienv needs recreating on Pi:

```bash
cd ~/dima/Group_Proj
git pull origin MainOne5   # or whatever branch

python3 -m venv --system-site-packages pienv
source pienv/bin/activate

pip install -r requirements_pi.txt
# If tflite-runtime fails on Python 3.13:
pip install ai-edge-litert
# For Pi monitor display (not headless):
pip install opencv-python   # replaces opencv-python-headless

# Verify
python -c "import cv2; print('OpenCV:', cv2.__version__)"
python -c "import numpy; print('NumPy:', numpy.__version__)"
python -c "from ai_edge_litert.interpreter import Interpreter; print('TFLite: OK')"
python -c "from pymavlink import mavutil; print('pymavlink: OK')"
```

---

## CV Model Readiness

For first flight, the current `best.tflite` (custom-trained YOLOv8n) should work for
bench-level detection. However:

```
[ ] BEFORE FLIGHT: Test detection with corrected colors on Pi
    - Push latest code (BGR fix), pull on Pi
    - Run pi_2_detect.py --headless with dummy
    - Confirm detection works with correct colors

[ ] OPTIONAL: Prepare backup models on laptop
    - Export COCO person detector: yolo export model=yolov8n.pt format=tflite
    - Copy to models/ folder, ready to swap on Pi if custom model fails
    - On flight day: cp models/backup.tflite best.tflite
```

---

## After First Flight

1. Review `passive_flight_log.csv`
2. Update config.py with measured values:
   ```python
   TARGET_ALT = ___     # max reliable detection altitude
   SEARCH_SPEED_MPS = ___  # max reliable detection speed
   ```
3. Adjust confidence threshold if needed (vision.py)
4. Calibrate FOV if GPS estimates are consistently off (config.py)
5. Collect saved frames → retrain model on real data → better detection
6. Plan Step 3: manual flight with N/Y/I/X/L controls
