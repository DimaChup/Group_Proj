# Next Steps - Clear Roadmap

Each phase adds one layer of complexity. Don't skip ahead — each phase proves the previous one works.

```
PHASE 0: Laptop         → Code works, simulation runs, model detects          ✅ DONE
PHASE 1: Pi + Vision    → Camera works, AI detects on real hardware           ✅ DONE
PHASE 2: Pi + Vision + Cube  → CV and flight controller talk to each other    ✅ DONE
PHASE 3: First Flight   → Calibrate with real drone (manual only)             ← YOU ARE HERE
PHASE 4: Ground Station  → Remote monitoring and control                      (can overlap with 3)
PHASE 5: Autonomous     → Full mission with gradual confidence building
```

---

## PHASE 0: Laptop (before you touch the Pi)

**Goal**: Prove the code works and you understand the system.

| Step | What to do | How you know it works |
|------|-----------|----------------------|
| 0a | Run `python simulation.py` | See search pattern, click to place dummy, watch drone find it |
| 0b | Run `python tests/hardware/benchmark.py` | Model loads, detects on test image, prints speed + position |
| 0c | Read `docs/PI_SETUP.md` | Know exactly what to do when Pi arrives |
| 0d | Push code to git (including `best.tflite`) | Ready to clone onto Pi |

**Sign-off**: Simulation works. Model detects. Code is in git.

---

## PHASE 1: Pi — Vision Only (no Cube needed) — DONE

**Goal**: Camera + AI detection working on Pi hardware.

**Status**: COMPLETE. Camera works (picamera2, 640x480). TFLite detection working (256ms avg,
3.9 FPS, 50/50 detection at 0.966 confidence). Camera color fix applied (IMX296 BGR issue).

### Setup (one time)
```bash
sudo raspi-config    # enable camera, reboot
mkdir -p ~/sar-drone && cd ~/sar-drone
git clone <your-repo-url> .
python3 -m venv --system-site-packages pienv
source pienv/bin/activate
pip install -r requirements_pi.txt
# If tflite-runtime fails on Python 3.13: pip install ai-edge-litert
```

### Tests

| Step | Script | What it proves | Pass criteria | Status |
|------|--------|---------------|--------------|--------|
| 1 | `python tests/laptop/test_camera.py` | Camera gives frames | Prints frame size | PASS |
| 2 | `python tests/laptop/test_cv.py` | AI detects dummy | Bounding box on dummy printout | PASS |
| 3 | `python tests/hardware/benchmark.py` | Speed OK | Avg < 200ms | 256ms (acceptable) |
| 3b | `python tests/hardware/cv_benchmark.py --headless` | FPS + blur | Reports pipeline FPS, blur impact | -- |
| 3c | Resolution test (planned) | Best resolution | Recommends optimal resolution | -- |
| 4 | `python tests/calibration/fov_calibrate.py --headless` | Bench FOV | Predicted vs actual match | -- |

### Camera Color Note
The IMX296 Global Shutter Camera outputs BGR data despite picamera2 labeling it RGB888.
Do NOT add `cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)` — this double-swaps channels.
Use frames directly from `picam.capture_array()`. See CV_GUIDE.md for details.

### After Phase 1: Update config.py

Based on step 3c, if a lower resolution works:
```python
IMAGE_W = 320   # or whatever pi_9 recommends
IMAGE_H = 240
```

**Sign-off**: Camera captures frames. AI detects dummy. Speed is acceptable. Best resolution chosen.

---

## PHASE 2: Pi — Vision + Cube (bench, no flying) — DONE

**Goal**: CV and Cube work together on the desk.

**Status**: COMPLETE. Cube connected via mavproxy bridge (921600 baud). Heartbeat, GPS, attitude,
battery all confirmed. Buzzer beeps on detection. Guidance commands working. Mission Planner
connected via TCP bridge (tcpin:0.0.0.0:5762).

### Connection Setup

**Important**: Python 3.13 + pyserial has broken serial reads. Use mavproxy as a UDP bridge:

```bash
# Terminal 1: Start mavproxy bridge
sudo /opt/mavlink/mavlink-venv/bin/mavproxy.py \
  --master=/dev/ttyAMA0 --baudrate=921600 --streamrate=10 \
  --out=udpout:127.0.0.1:14550 --out=tcpin:0.0.0.0:5762
```

### Tests

| Step | Script | What it proves | Pass criteria | Status |
|------|--------|---------------|--------------|--------|
| 5 | `python tests/laptop/test_cube.py` | Cube talks to Pi | Heartbeat + yaw/pitch/roll printed | PASS |
| 6 | `python tests/hardware/buzzer_test.py --headless` | **CV + Cube together** | Buzzer beeps, guidance commands | PASS |
| 7 | `python preflight.py` | All connections OK | All checks pass | -- |

### Bench test results (buzzer_test.py)
- 144 detections from 513 frames, 210ms avg inference
- Guidance commands working (LEFT, RIGHT, FORWARD, BACK, CENTRED)
- Yaw data flowing from Cube
- Buzzer works on Pi monitor; may not sound over SSH headless

**Sign-off**: Buzzer beeps on detection. Guidance makes sense. CSV has entries.

---

## PHASE 3: First Test Flight Day (manual only) — NEXT

**Goal**: Calibrate with real data. No autonomous code — pilot flies with RC the whole time.

**Pre-requisites before going to field**:
1. Push BGR fix code to GitHub, pull on Pi, verify detection works with correct colors
2. Test GPS fix outdoors (tests/hardware/gps_test.py)
3. Have tests/flight/1_passive_flight.py ready — this is your main flight day script

### What to bring

- [ ] Drone with Pi + Camera + Cube (all wired, bench-tested)
- [ ] Laptop with SSH access to Pi
- [ ] RC controller
- [ ] Large dummy printout — lay flat on ground
- [ ] Tape measure or ground markers
- [ ] Notebook + pen
- [ ] Fully charged batteries

### Roles

| Person | Job |
|--------|-----|
| Pilot | Flies with RC. Holds altitude when told. Safety override. |
| Operator | SSH into Pi. Runs scripts. Records data. |
| Spotter | Calls out altitude from Mission Planner or RC telemetry |
| Safety | Watches for people/obstacles, calls "LAND NOW" if needed |

### Step 8: Max Detection Altitude

Can the drone see the dummy from above?

1. Place dummy flat on ground
2. SSH: `python tests/laptop/test_cv.py --headless`
3. Pilot hovers directly above dummy
4. Hold at each altitude ~10 seconds:

| Altitude | Detected? | Confidence | Notes |
|----------|-----------|------------|-------|
| 5m       |           |            |       |
| 10m      |           |            |       |
| 15m      |           |            |       |
| 20m      |           |            |       |
| 25m      |           |            |       |
| 30m      |           |            |       |

5. Record max altitude where confidence > 0.5 consistently
6. Ctrl+C to stop

**Result** → update `config.py`:
- `TARGET_ALT` = max reliable detection height
- `VERIFY_ALT` = ~half of TARGET_ALT

### Step 9: FOV Calibration

How much ground does the camera see at altitude?

1. Lay markers on ground at known distances
2. SSH: `python tests/calibration/alt_test.py`
3. Pilot hovers at ~10m, operator presses SPACE, enters ground width visible
4. Pilot climbs to ~20m, repeat
5. Script outputs actual FOV and correction values

**Result** → update `config.py`:
- `SENSOR_WIDTH_MM` or `FOCAL_LENGTH_MM` (script tells you which)

### Step 10: (bonus) CV + Cube from the Air

If time allows:
1. SSH: `python tests/flight/4_detect_and_center.py`
2. Pilot hovers at ~15m above dummy, flies side to side
3. Watch: does guidance say LEFT/RIGHT/CENTRED correctly?
4. Does buzzer beep?

**Sign-off**: Know max detection altitude. Know real FOV. config.py updated with real numbers.

---

## PHASE 4: Ground Station + Pre-Autonomous Prep

**Goal**: Can monitor and control the mission remotely.

```
[Camera] ---> [Pi] <--serial--> [Cube] <--telemetry radio--> [GS / Mission Planner]
                |                                                |
                +-------------- WiFi (SSH) ---------------------+
```

| Step | What | Pass criteria |
|------|------|--------------|
| 11 | Plug in telemetry radios | Mission Planner shows drone on map |
| 12 | SSH from laptop to Pi | Can run scripts remotely |
| 13 | Ground test: `python main.py` (no props!) | State machine runs, MP shows commands, kill switch works |

Step 13 is critical — run the full mission code connected to the real Cube but **with no propellers**. Watch Mission Planner to see if it tries to arm, sends waypoints, etc.

**Sign-off**: Telemetry works. SSH works. main.py talks to real Cube without errors.

---

## PHASE 5: Autonomous Flight (gradual)

**Goal**: Full mission. Build confidence step by step.

### Step 14: Short hover test

- Props on, pilot ready with RC kill switch
- `python main.py` — let it arm and take off
- **Immediately switch to manual if anything unexpected happens**
- Just prove: arm → takeoff → hover at TARGET_ALT → RTL
- Don't even need the dummy yet

### Step 15: Full search with dummy

- Place dummy somewhere in search area
- `python main.py` over SSH
- Drone takes off → flies search pattern → detects dummy → Y/N prompt
- Press Y → drone lands near target
- Press N → drone continues search
- **Pilot takes over at ANY sign of unexpected behaviour**

### Step 16: Iterate and refine

- Search speed too fast? → lower `SEARCH_SPEED_MPS` in config.py
- Pattern has gaps? → adjust search pattern spacing based on real FOV
- False positives? → raise confidence threshold in vision.py
- Missed dummy? → try bigger model, retrain with aerial data (see CV_GUIDE.md)
- Test N rejection → resume search correctly?
- Test edge cases: dummy at edge, wind, partial occlusion

---

## Summary

| Phase | What | Needs | Status |
|-------|------|-------|--------|
| 0. Laptop | Simulation + model test | Laptop only | **DONE** |
| 1. Pi Vision | Camera + AI on Pi | Pi + Camera | **DONE** |
| 2. Pi Vision+Cube | CV + Cube on bench | Pi + Camera + Cube | **DONE** |
| 3. First flight | Calibrate (manual RC) | All hardware + field | **NEXT** |
| 4. Ground station | Telemetry + SSH | Radios + WiFi | Partially done (MP connected via TCP) |
| 5. Autonomous | Full mission | Everything | After calibration |

---

## Evolution of Functionality

```
Phase 0:  [Laptop]  simulation works, model detects test image
             │
Phase 1:  [Pi]  camera works → AI detects dummy on desk
             │
Phase 2:  [Pi + Cube]  CV + Cube talk → buzzer beeps → guidance works on bench
             │
Phase 3:  [Real drone]  detection from air → calibrate FOV + altitude → real config values
             │
Phase 4:  [+ Ground Station]  remote monitoring → ground test main.py (no props)
             │
Phase 5:  [Autonomous]  hover test → full search → detect → land → iterate
             │
         [FINAL GOAL]  Reliable autonomous SAR: search → detect → verify → land
```

Each phase adds ONE new thing. If something breaks, you know exactly which layer caused it.

---

## Quick Reference

```bash
# PHASE 0 — Laptop
python simulation.py
python tests/hardware/benchmark.py

# PHASE 1 — Pi Vision
python tests/laptop/test_camera.py                # camera
python tests/laptop/test_cv.py                    # detection
python tests/hardware/benchmark.py                # speed
python tests/hardware/cv_benchmark.py --headless  # FPS + blur
# resolution test (planned)
python tests/calibration/fov_calibrate.py --headless  # bench FOV

# PHASE 2 — Pi Vision + Cube
python tests/laptop/test_cube.py              # Cube heartbeat
python tests/flight/4_detect_and_center.py    # CV + Cube together
python preflight.py                           # all checks

# PHASE 3 — First Flight (manual)
python tests/laptop/test_cv.py --headless     # detection at altitude
python tests/calibration/alt_test.py          # FOV calibration

# PHASE 4 — Ground Station
python main.py                           # ground test (no props!)

# PHASE 5 — Autonomous
python main.py                           # full mission
```
