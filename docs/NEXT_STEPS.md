# Next Steps - Clear Roadmap

Each phase adds one layer of complexity. Don't skip ahead — each phase proves the previous one works.

```
PHASE 0: Laptop         → Code works, simulation runs, model detects
PHASE 1: Pi + Vision    → Camera works, AI detects on real hardware
PHASE 2: Pi + Vision + Cube  → CV and flight controller talk to each other
PHASE 3: First Flight   → Calibrate with real drone (manual only)
PHASE 4: Ground Station  → Remote monitoring and control
PHASE 5: Autonomous     → Full mission with gradual confidence building
```

---

## PHASE 0: Laptop (before you touch the Pi)

**Goal**: Prove the code works and you understand the system.

| Step | What to do | How you know it works |
|------|-----------|----------------------|
| 0a | Run `python simulation.py` | See search pattern, click to place dummy, watch drone find it |
| 0b | Run `python tests/pi_3_benchmark.py` | Model loads, detects on test image, prints speed + position |
| 0c | Read `docs/PI_SETUP.md` | Know exactly what to do when Pi arrives |
| 0d | Push code to git (including `best.tflite`) | Ready to clone onto Pi |

**Sign-off**: Simulation works. Model detects. Code is in git.

---

## PHASE 1: Pi — Vision Only (no Cube needed)

**Goal**: Camera + AI detection working on Pi hardware.

### Setup (one time)
```bash
sudo raspi-config    # enable camera, reboot
mkdir -p ~/sar-drone && cd ~/sar-drone
git clone <your-repo-url> .
python3 -m venv --system-site-packages pienv
source pienv/bin/activate
pip install -r requirements_pi.txt
```

### Tests

| Step | Script | What it proves | Pass criteria |
|------|--------|---------------|--------------|
| 1 | `python tests/pi_1_camera.py` | Camera gives frames | Prints frame size |
| 2 | `python tests/pi_2_detect.py` | AI detects dummy | Bounding box on dummy printout |
| 3 | `python tests/pi_3_benchmark.py` | Speed OK | Avg < 200ms |
| 3b | `python tests/pi_8_camera_test.py --headless` | FPS + blur | Reports pipeline FPS, blur impact |
| 3c | `python tests/pi_9_resolution_test.py --headless` | Best resolution | Recommends optimal resolution |
| 4 | `python tests/pi_6_fov_test.py --headless` | Bench FOV | Predicted vs actual match |

### After Phase 1: Update config.py

Based on step 3c, if a lower resolution works:
```python
IMAGE_W = 320   # or whatever pi_9 recommends
IMAGE_H = 240
```

**Sign-off**: Camera captures frames. AI detects dummy. Speed is acceptable. Best resolution chosen.

---

## PHASE 2: Pi — Vision + Cube (bench, no flying)

**Goal**: CV and Cube work together on the desk.

### Wiring

| Pi GPIO | Cube TELEM2 |
|---------|-------------|
| TX (GPIO 14, pin 8) | RX |
| RX (GPIO 15, pin 10) | TX |
| GND (pin 6) | GND |

### Tests

| Step | Script | What it proves | Pass criteria |
|------|--------|---------------|--------------|
| 5 | `python tests/test_cube.py` | Cube talks to Pi | Heartbeat + yaw/pitch/roll printed |
| 6 | `python tests/pi_4_detect_and_log.py` | **CV + Cube together** | Buzzer beeps, guidance commands, CSV log |
| 7 | `python preflight.py` | All connections OK | All checks pass |

### Step 6 is the big bench test

Carry the drone by hand over a dummy printout:

```
[READY] Carry drone over dummy. Follow guidance commands.

  [14:23:01] DETECTED #1  conf=0.87  >> LEFT + FORWARD  GPS=(no fix)  yaw=45
  [14:23:03] DETECTED #2  conf=0.91  >> RIGHT  GPS=(no fix)  yaw=47
  [14:23:05] DETECTED #3  conf=0.93  >> CENTRED - DESCEND  GPS=(no fix)  yaw=48
```

This proves: camera detects → Cube reads telemetry → buzzer beeps → guidance logic works → CSV logs.

**Sign-off**: Buzzer beeps on detection. Guidance makes sense. CSV has entries. Preflight passes.

---

## PHASE 3: First Test Flight Day (manual only)

**Goal**: Calibrate with real data. No autonomous code — pilot flies with RC the whole time.

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
2. SSH: `python tests/pi_2_detect.py --headless`
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
2. SSH: `python tests/pi_7_alt_test.py`
3. Pilot hovers at ~10m, operator presses SPACE, enters ground width visible
4. Pilot climbs to ~20m, repeat
5. Script outputs actual FOV and correction values

**Result** → update `config.py`:
- `SENSOR_WIDTH_MM` or `FOCAL_LENGTH_MM` (script tells you which)

### Step 10: (bonus) CV + Cube from the Air

If time allows:
1. SSH: `python tests/pi_4_detect_and_log.py`
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

| Phase | What | Needs | Can do now? |
|-------|------|-------|-------------|
| 0. Laptop | Simulation + model test | Laptop only | **YES** |
| 1. Pi Vision | Camera + AI on Pi | Pi + Camera | **When Pi arrives** |
| 2. Pi Vision+Cube | CV + Cube on bench | Pi + Camera + Cube | After Phase 1 |
| 3. First flight | Calibrate (manual RC) | All hardware + field | After Phase 2 |
| 4. Ground station | Telemetry + SSH | Radios + WiFi | Can overlap with 2-3 |
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
python tests/pi_3_benchmark.py

# PHASE 1 — Pi Vision
python tests/pi_1_camera.py              # camera
python tests/pi_2_detect.py              # detection
python tests/pi_3_benchmark.py           # speed
python tests/pi_8_camera_test.py --headless   # FPS + blur
python tests/pi_9_resolution_test.py --headless  # resolution
python tests/pi_6_fov_test.py --headless      # bench FOV

# PHASE 2 — Pi Vision + Cube
python tests/test_cube.py                # Cube heartbeat
python tests/pi_4_detect_and_log.py      # CV + Cube together
python preflight.py                      # all checks

# PHASE 3 — First Flight (manual)
python tests/pi_2_detect.py --headless   # detection at altitude
python tests/pi_7_alt_test.py            # FOV calibration

# PHASE 4 — Ground Station
python main.py                           # ground test (no props!)

# PHASE 5 — Autonomous
python main.py                           # full mission
```
