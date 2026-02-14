# Next Steps - Clear Roadmap

---

## PHASE 1: Bench Work (no flying needed)

Everything here is done on a desk or carrying the drone by hand.
**Do ALL of this before your first test flight date.**

| Step | Script | What it proves | How you know it works |
|------|--------|---------------|----------------------|
| 1 | `python tests/pi_1_camera.py` | Camera gives frames | Prints frame size, shows image |
| 2 | `python tests/pi_2_detect.py` | AI detects dummy | Bounding box on screen, or beeps via PuTTY (`--headless`) |
| 3 | `python tests/pi_3_benchmark.py` | Inference speed OK | Average < 200ms per frame |
| 3b | `python tests/pi_8_camera_test.py` | **Camera + CV quality** | Reports: pipeline FPS, motion blur effect, is blur killing detection? |
| 3c | `python tests/pi_9_resolution_test.py` | **Resolution sweet spot** | Tests 640x480 → 320x240 → 160x120: which is fastest while still detecting? |
| 4 | `python tests/pi_6_fov_test.py` | Bench FOV check | Hold camera over ruler, compare predicted vs actual |
| 5 | `python tests/test_cube.py` | Cube talks to Pi | Heartbeat + yaw/pitch/roll printed |
| 6 | `python tests/pi_4_detect_and_log.py` | **CV + Cube together** | Carry drone over dummy → buzzer beeps, guidance commands, CSV log |
| 7 | `python preflight.py` | All connections OK | All checks pass |

### Step 6 is the big one

Carry the drone by hand over a dummy printout. The script does everything at once:

1. Detects dummy with CV
2. Reads yaw/altitude/GPS from Cube
3. Buzzer beeps on detection
4. Logs to `detection_log.csv`
5. Shows guidance: **"go LEFT"**, **"go RIGHT"**, **"CENTRED - DESCEND"**

```
[READY] Carry drone over dummy. Follow guidance commands.

  [14:23:01] DETECTED #1  conf=0.87  >> LEFT + FORWARD  GPS=(no fix)  yaw=45
  [14:23:03] DETECTED #2  conf=0.91  >> RIGHT  GPS=(no fix)  yaw=47
  [14:23:05] DETECTED #3  conf=0.93  >> CENTRED - DESCEND  GPS=(no fix)  yaw=48
```

**Done when**: Buzzer beeps, guidance makes sense, CSV has entries.

### After bench work: update config.py

Based on steps 3b and 3c, update `config.py` if needed:
- `IMAGE_W` / `IMAGE_H` — if a lower resolution is faster without losing detection
- Note the pipeline FPS and blur results for reference on flight day

### Bench work sign-off checklist

Before going to the field, confirm:
- [ ] Camera captures frames reliably
- [ ] AI detects dummy with confidence > 0.4
- [ ] Inference speed < 200ms (ideally < 100ms)
- [ ] Best resolution chosen and set in config.py
- [ ] Cube heartbeat works over serial
- [ ] CV + Cube work together (step 6 passed)
- [ ] Preflight passes (step 7)
- [ ] Spare battery, dummy printout, tape measure packed for flight day

---

## PHASE 2: First Test Flight Day

**All manual — pilot flies with RC, no autonomous code running.**
The goal is to collect calibration data and prove detection works from the air.

### What to bring

- [ ] Drone with Pi + Camera + Cube (all wired)
- [ ] Laptop with SSH access to Pi (WiFi hotspot or direct cable)
- [ ] RC controller (pilot flies manually the whole time)
- [ ] Telemetry radio pair (optional but useful for Mission Planner view)
- [ ] Large dummy printout — lay flat on the ground
- [ ] Tape measure or ground markers at known distances (for FOV measurement)
- [ ] Notebook for recording numbers
- [ ] Fully charged batteries (drone + Pi)

### Roles

| Person | Job |
|--------|-----|
| Pilot | Flies with RC. Holds altitude when told. Safety override. |
| Operator | SSH into Pi on laptop. Runs scripts. Records data. |
| Spotter | Watches drone, calls out altitude from Mission Planner or RC telemetry |
| Safety | Watches for people/obstacles, calls "LAND NOW" if needed |

### Flight Day Step-by-Step

#### Step 8: Hover + Detection Test (is CV working from the air?)

This is the most important test. Can the drone actually see the dummy from above?

1. Place dummy flat on the ground, clear area around it
2. SSH into Pi: `python tests/pi_2_detect.py --headless`
3. Pilot takes off manually, hovers directly above dummy
4. Hold steady at each altitude for ~10 seconds:

| Altitude | Detected? | Confidence | Notes |
|----------|-----------|------------|-------|
| 5m       |           |            |       |
| 10m      |           |            |       |
| 15m      |           |            |       |
| 20m      |           |            |       |
| 25m      |           |            |       |
| 30m      |           |            |       |

5. Operator watches SSH terminal — detection prints when found
6. Record the **max altitude where confidence > 0.5 consistently**
7. Ctrl+C to stop the script

**What this tells you:**
- `TARGET_ALT` — set to max reliable detection height (search at this altitude)
- `VERIFY_ALT` — set to ~half of TARGET_ALT (descend to this for closer look)
- If detection fails at all heights → problem with model, camera angle, or dummy size

#### Step 9: FOV Calibration (how much ground does the camera see?)

1. Lay tape measure or markers on the ground at known distances (e.g. 5m apart)
2. SSH into Pi: `python tests/pi_7_alt_test.py`
3. Pilot hovers at altitude 1 (e.g. 10m), holds steady
4. Operator presses SPACE → script reads altitude from Cube
5. Look at what camera sees — enter the ground width visible (metres)
6. Pilot climbs to altitude 2 (e.g. 20m), repeat
7. Press 'q' when done — script shows results

The script will output:
```
  Your actual FOV:  62.3 degrees
  Config FOV:       45.4 degrees
  Difference:       +16.9 degrees

  >> UPDATE config.py with ONE of these:
     SENSOR_WIDTH_MM = 7.21  (keep FOCAL_LENGTH_MM = 6.0)
     FOCAL_LENGTH_MM = 4.18  (keep SENSOR_WIDTH_MM = 5.02)
```

**Update config.py immediately** — this affects how the search pattern spacing is calculated.

#### Step 10: (If time allows) Carry test with CV + Cube

If there's flight time left, try `pi_4_detect_and_log.py` while hovering:
1. SSH into Pi: `python tests/pi_4_detect_and_log.py`
2. Pilot hovers at ~15m above dummy
3. Slowly fly side to side across the dummy
4. Watch: does it detect? Does guidance say LEFT/RIGHT/CENTRED correctly?
5. Check: does buzzer beep on the Cube?

This proves the full pipeline works from the air — not just detection, but guidance too.

### After Flight Day: Update config.py

| Parameter | What to change | Where it came from |
|-----------|---------------|-------------------|
| `TARGET_ALT` | Max reliable detection height | Step 8 altitude table |
| `VERIFY_ALT` | ~half of TARGET_ALT | Step 8 altitude table |
| `SENSOR_WIDTH_MM` or `FOCAL_LENGTH_MM` | Corrected FOV | Step 9 output |
| `IMAGE_W` / `IMAGE_H` | Best resolution (if not already set from bench) | Step 3c bench result |

### Flight day sign-off checklist

- [ ] Know the max detection altitude → `TARGET_ALT` updated
- [ ] Know the real FOV → `SENSOR_WIDTH_MM` or `FOCAL_LENGTH_MM` updated
- [ ] CV works from the air (detections seen in SSH terminal)
- [ ] If step 10 done: guidance commands make sense from the air
- [ ] All data noted down / detection_log.csv saved

---

## PHASE 3: Ground Station Setup (can overlap with above)

```
[Camera] ---> [Pi] <--serial--> [Cube] <--telemetry radio--> [GS / Mission Planner]
                |                                                |
                +-------------- WiFi (SSH) ---------------------+
```

| Step | What | How you know it works |
|------|------|----------------------|
| 11 | Plug in telemetry radios | Mission Planner shows drone on map |
| 12 | SSH from laptop to Pi | Can run commands on Pi remotely |
| 13 | `python main.py` over SSH | Full mission runs, MP shows flight, Y/N works |

---

## PHASE 4: Second Test Flight Day (semi-autonomous)

**Careful transition from manual to automatic. Pilot always has RC override.**

### Step 14: Ground test with real Cube (no props)

Before flying autonomous, test on the ground with no props:
1. `python main.py` on Pi
2. Watch Mission Planner — does it try to arm? Send waypoints?
3. Verify state machine runs through INIT → CONNECTING → ARMING
4. Kill switch / disarm works instantly
5. This proves the code talks to real Cube correctly

### Step 15: First autonomous flight

1. Place dummy somewhere in the search area
2. Pilot ready on RC with kill switch
3. `python main.py` over SSH
4. Drone takes off, follows search pattern
5. When it detects dummy → operator gets Y/N prompt over SSH
6. Press Y → drone lands. Press N → drone continues search.
7. **Pilot takes over manually at ANY sign of unexpected behaviour**

### Step 16: Iterate

- Adjust search speed if drone moves too fast for detection
- Adjust pattern spacing based on real FOV
- Test edge cases: dummy at edge of search area, wind, partial occlusion
- Test N rejection → does it resume search correctly?

---

## Summary

| Phase | Steps | Needs | Can do now? |
|-------|-------|-------|-------------|
| 1. Bench testing | 1-7 (incl 3b, 3c) | Pi + Camera + Cube on desk | **YES** |
| 2. First flight day | 8-10 | Manual hover with RC | After bench work passes |
| 3. Ground station | 11-13 | Telemetry radios + WiFi | Partly (MP setup) |
| 4. Second flight day | 14-16 | Everything above done | After calibration |

**You can validate 80% of the system on a bench before ever leaving the ground.**

---

## Why this order?

| Phase | What's new | What could go wrong |
|-------|-----------|-------------------|
| Bench (1-7) | Camera, CV, Cube, wiring | Library issues, baud rate, serial port |
| First flight (8-10) | Real altitude, real FOV, real detection | Config params wrong, detection range, camera angle |
| GS (11-13) | Telemetry, WiFi, SSH | Radio, firewall, network |
| Second flight (14-16) | Autonomous control | Search pattern, timing, wind, everything physical |

Each phase isolates one type of problem. If step 6 fails, you know it's the Cube wiring — not the camera, because steps 1-3 already proved that works.

---

## Quick Pre-Flight-Day Summary

```
BEFORE FLIGHT DAY (bench):
  Steps 1-7  →  camera works, AI detects, speed ok, Cube talks, CV+Cube together, preflight passes
  Result: You KNOW the system works on a desk. No surprises from software.

ON FLIGHT DAY 1 (manual only):
  Step 8   →  hover above dummy at 5m/10m/15m/20m/25m/30m → find max detection height
  Step 9   →  hover at 2 heights → measure ground footprint → calibrate FOV
  Step 10  →  (bonus) hover while running CV+Cube script → guidance works from air?
  Result: You KNOW config.py has real numbers. Detection works from real altitude.

AFTER FLIGHT DAY 1:
  Update config.py with real TARGET_ALT, VERIFY_ALT, FOV values

BEFORE FLIGHT DAY 2:
  Steps 11-13 →  ground station, SSH, test main.py with no props

ON FLIGHT DAY 2 (semi-autonomous):
  Step 14  →  ground test (no props) with main.py
  Step 15  →  first autonomous flight with dummy in search area
  Step 16  →  iterate, tune, edge cases
```
