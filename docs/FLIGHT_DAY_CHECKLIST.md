# Flight Day Checklist

**Print this. Follow it step by step. Don't skip steps.**

**Estimated time:** ~2-2.5 hours total
- Setup (Phase 0-3): ~30 min
- Calibration (Phase 4-5): ~15 min
- Step 1 (MP AUTO): ~10 min
- Step 1.5 (Waypoint test): ~10 min
- Step 2 (Passive CV): ~20 min (needs 1 battery)
- Step 3 (Dashboard): ~30 min (needs 1 battery)

**Batteries needed:** Minimum 2, ideally 3 (each gives ~15-20 min flight)

---

## PHASE 0: Before Leaving (Laptop, at Home)

```
[ ] 0.1  Push latest code:  git add -A && git commit -m "flight day" && git push
[ ] 0.2  Charge drone battery (LiPo full = 4.2V per cell)
[ ] 0.3  Charge Pi power source (USB battery pack or drone BEC)
[ ] 0.4  Pack: laptop, RC controller, USB cable, phone (hotspot), measuring tape
[ ] 0.5  Pack: printed dummy (for placing on ground)
```

---

## PHASE 1: Pi Setup (at Field, Before Flying)

### 1.1 Network

Both Pi and laptop must be on the same WiFi. Options:
- Phone hotspot (easiest — both connect to your phone)
- Pi hotspot (Pi creates network, laptop joins)

```
[ ] 1.1  Connect Pi and laptop to same WiFi
[ ] 1.2  Note Pi IP:  hostname -I    (e.g. 192.168.x.x)
```

### 1.2 Pull Code on Pi

```bash
cd ~/dima/Group_Proj
git pull
```

### 1.3 Recreate pienv (only if broken)

```bash
python3 -m venv --system-site-packages pienv
source pienv/bin/activate
pip install -r requirements_pi.txt
pip install ai-edge-litert   # replaces tflite-runtime on Python 3.13
```

### 1.4 Start Mavproxy (Terminal 1 on Pi — always first)

```bash
sudo /opt/mavlink/mavlink-venv/bin/mavproxy.py \
  --master=/dev/ttyAMA0 --baudrate=921600 --streamrate=10 \
  --out=udpout:127.0.0.1:14550 --out=tcpin:0.0.0.0:5762
```

### 1.5 Quick System Check (Terminal 2 on Pi)

```bash
cd ~/dima/Group_Proj && source pienv/bin/activate
python tests/diagnostics/diagnostics.py
```

Check all green:
```
[ ] Camera:    OK (640x480 frames)
[ ] AI Model:  OK (best.tflite loaded)
[ ] Cube:      OK (heartbeat, system 1)
[ ] GPS:       OK (satellites > 0, wait for fix_type=3)
[ ] Battery:  ___V (must be >14.4V / 3.6V per cell for safe flight)
```

### 1.6 Connect Mission Planner (Laptop)

```
Mission Planner → Connection → TCP → <PI_IP> → port 5762
```

```
[ ] MP connected, map shows drone position
[ ] GPS satellites visible in MP (bottom bar)
```

---

## PHASE 2: GPS Lock

**Do not fly until GPS lock is confirmed.**

```bash
# On Pi:
python tests/hardware/gps_test.py
```

```
[ ] fix_type = 3 (3D fix)
[ ] Satellites >= 8
[ ] Here 3+ LED = flashing GREEN (not blue)
```

This can take 1-5 minutes outdoors. Be patient.

**If GPS doesn't lock after 15 minutes:**
- Move to more open area (away from buildings/trees)
- Cold start after power cycle can take 10-15 min
- Check Here 3+ LED: blue=no lock, green=locked, yellow=pre-arm fail
- Urban canyons and overcast sky slow GPS lock

---

## PHASE 3: RC Setup & Safety

```
[ ] 3.1  RC bound to Cube (sticks responsive in MP)
[ ] 3.2  Kill switch configured: one RC switch = STABILIZE mode
         (test it: flip switch in MP, mode should change to STABILIZE)
[ ] 3.3  Failsafe set: RC signal loss = RTL
         (Mission Planner → Config → Failsafe → Radio = RTL)
[ ] 3.4  Test: flip kill switch back and forth, confirm mode changes in MP
[ ] 3.5  Test RC override WITH a script running:
         Start: python tests/flight/0a_cube_commands.py (or pi_flight.py)
         Flip RC to STABILIZE → confirm MP shows STABILIZE (script ignored)
         Flip back → script can send commands again
         This proves RC ALWAYS overrides Python, no matter what.
[ ] 3.6  Agree on who is RC pilot, who is spotter, who runs dashboard
```

**Rule: RC pilot's hand is always on the kill switch.**

---

## PHASE 4: FOV Calibration (Bench — Before First Flight)

This is the most important calibration. Wrong FOV = wrong GPS estimates.

```bash
# On Pi (with camera pointing down at a ruler):
python tests/calibration/fov_calibrate.py --headless
```

Steps:
1. Hold camera pointing straight down at known height (e.g. 50cm)
2. Place ruler/tape measure flat on ground below camera
3. Note how many cm are visible edge-to-edge in the camera frame
4. Enter values when prompted
5. Script calculates corrected FOCAL_LENGTH_MM

```
[ ] 4.1  Ran fov_calibrate.py
[ ] 4.2  Measured visible width: ____cm at ____cm height
[ ] 4.3  Script says FOCAL_LENGTH_MM should be: ____
[ ] 4.4  Updated config.py:  FOCAL_LENGTH_MM = ____
[ ] 4.5  Pushed update:  git add config.py && git commit -m "FOV calibration" && git push
```

Current values (update after calibration):
```
SENSOR_WIDTH_MM = 5.02   (IMX296 datasheet — don't change unless wrong sensor)
FOCAL_LENGTH_MM = 6.0    (UPDATE THIS with measured value)
IMAGE_W = 640
IMAGE_H = 480
```

---

## PHASE 5: Inference Benchmark (Quick — 2 minutes)

```bash
python tests/hardware/benchmark.py
```

```
[ ] Avg inference time: ____ms
[ ] FPS: ____
[ ] Detection rate: ____/50
[ ] Confidence: ____
```

Write these down — they tell you:
- **FPS** → set `--fps` flag in pi_flight.py to match (don't exceed Pi's capability)
- **Confidence** → if low, model might struggle from altitude

---

## PHASE 6: Dummy Placement

```
[ ] 6.1  Place dummy on flat open ground (grass)
[ ] 6.2  No trees/obstacles within 20m
[ ] 6.3  Note dummy GPS from Mission Planner: ____, ____
         (walk to dummy with phone/MP connected, read coordinates)
[ ] 6.4  Mark dummy position on paper (for comparing estimates later)
```

---

## PHASE 7: Dry-Run Verification (No GPS Needed)

```bash
# On Pi (or laptop):
python main.py --dry-run
```

```
[ ] 7.1  Verify SEARCH_AREA_GPS coordinates in config.py match the field
[ ] 7.2  Run --dry-run, confirm waypoints cover intended area
[ ] 7.3  Note: estimated flight time = ____min, waypoints = ____
[ ] 7.4  If wrong area: update SEARCH_AREA_GPS in config.py, re-run --dry-run
```

---

## STEP 1: Mission Planner AUTO Flight (No Custom Code)

**Purpose:** Prove drone flies, GPS works, RTL works. Your code is NOT running.

```
[ ] 1. In MP: Plan → add 4 waypoints in a square (10-15m altitude)
[ ] 2. Upload to Cube (Write WPs button)
[ ] 3. Arm via RC
[ ] 4. Switch to AUTO on RC
[ ] 5. Drone flies square pattern
[ ] 6. Watch for stability, GPS track on MP
[ ] 7. Switch to RTL or let it complete → drone lands
```

**Pass:** Drone completes pattern and lands safely.
**Fail:** Do NOT continue to Step 2. Fix issues first.

```
[ ] STEP 1 PASSED
```

---

## STEP 1.5: Waypoint Test (Your Code, No CV)

**Purpose:** Prove your MAVLink commands work on real hardware. No camera, no AI — just arm, takeoff, fly 4 waypoints, land.

```bash
# Terminal 2 on Pi:
python tests/flight/2_waypoints.py --dry-run   # verify commands without arming
python tests/flight/2_waypoints.py --alt 10     # real flight at 10m
```

```
[ ] 1.5.1  Dry-run passed (commands print but don't execute)
[ ] 1.5.2  Drone arms and takes off to 10m
[ ] 1.5.3  Flies 4 waypoints (20m square)
[ ] 1.5.4  Lands at launch point
```

**Pass:** Drone completes waypoints and lands safely.
**Fail:** Do NOT continue to Step 2. Fix MAVLink commands first.

```
[ ] STEP 1.5 PASSED
```

---

## STEP 2: Passive CV (passive_flight.py)

**Purpose:** Measure how well CV detects dummy from altitude. Pi sends ZERO commands.

```bash
# Terminal 2 on Pi:
python tests/flight/1_passive_flight.py --headless --stream
```

```
# On laptop browser (to see live camera):
http://<PI_IP>:8090
```

Procedure:
```
[ ] 2.0  Start passive_flight.py, open http://PI_IP:8090 in browser
[ ] 2.0b Confirm video stream shows in browser (even if pointing at ground)
[ ] 2.1  Pilot takes off, hovers at 10m directly above dummy → hold 30s
[ ] 2.2  Climb to 15m → hold 30s
[ ] 2.3  Climb to 20m → hold 30s
[ ] 2.4  Climb to 25m → hold 30s
[ ] 2.5  Climb to 30m → hold 30s
[ ] 2.6  Fly over dummy at 3 m/s at 15m altitude
[ ] 2.7  Fly over at 5 m/s
[ ] 2.8  Fly over at 7 m/s
```

Record results:

| Altitude | Detections? | Confidence | Notes |
|----------|------------|------------|-------|
| 10m      |            |            |       |
| 15m      |            |            |       |
| 20m      |            |            |       |
| 25m      |            |            |       |
| 30m      |            |            |       |

| Speed @15m | Detections? | Blur? | Notes |
|------------|------------|-------|-------|
| 3 m/s     |            |       |       |
| 5 m/s     |            |       |       |
| 7 m/s     |            |       |       |

After landing, review CSV:
```bash
cat passive_flight_log.csv
```

**Pass:** CV detects dummy reliably at some altitude.
**Result:** Max detection altitude = ____ → update `TARGET_ALT` in config.py

```
[ ] STEP 2 PASSED
[ ] Updated config.py:  TARGET_ALT = ____
[ ] Updated config.py:  SEARCH_SPEED_MPS = ____
```

**If CV doesn't detect at all:**
- Swap model: `cp cv_models/sar_v2_1088/best.tflite best.tflite` and retry
- Lower confidence threshold in vision.py (0.4 → 0.3 → 0.25)
- Try flying lower (5-10m)
- Try with larger dummy / brighter colors

---

## STEP 3: Full Dashboard (pi_flight.py)

**Purpose:** Test the complete N → investigate → classify → L → land flow.

```bash
# Terminal 2 on Pi:
python pi_flight.py --fps 4
```

```
# On laptop browser:
http://<PI_IP>:8090
```

Pre-flight bench check:
```
[ ] 3.0  Start pi_flight.py on bench (no flying)
[ ] 3.0b Open http://PI_IP:8090 in browser, confirm dashboard loads
[ ] 3.0c Click FAKE DET, verify cluster appears on grid
[ ] 3.0d Close pi_flight.py (Ctrl+C)
```

Flow:
```
[ ] 3.1  Pilot flies RC over dummy area
[ ] 3.2  Watch browser — detection alert appears, cluster on grid
[ ] 3.3  Press N in browser → drone flies to estimate (GUIDED mode)
[ ] 3.4  Drone descends to 15m, hovers
[ ] 3.5  Camera shows live view — can you see the dummy?
[ ] 3.6  Classify: Y (real dummy) / I (item of interest) / X (false positive)
[ ] 3.7  If Y: press L → drone flies to 7.5m north → lands
[ ] 3.8  Measure actual landing distance from dummy: ____m
```

**If CV isn't detecting:** Use FAKE DET button
```
[ ] 3.9  Click FAKE DET in browser
[ ] 3.10 Enter dummy GPS (from Phase 6) or leave blank for drone position
[ ] 3.11 Cluster appears on grid → press N → investigate → L → land
         (tests full command sequence without needing CV)
```

**At ANY point:** RC to STABILIZE overrides everything.

```
[ ] STEP 3 PASSED
```

---

## After Flying: Record Results

```
FOV calibration:
  FOCAL_LENGTH_MM = ____

CV performance:
  Max detection altitude = ____m
  Max detection speed = ____ m/s
  Avg confidence at best altitude = ____
  Inference rate on Pi = ____ FPS
  False positives seen = ____

Landing accuracy:
  GPS estimate error = ____m (compare estimate vs known dummy GPS)
  Landing distance from dummy = ____m (measure with tape)

Config updates needed:
  [ ] TARGET_ALT = ____
  [ ] SEARCH_SPEED_MPS = ____
  [ ] FOCAL_LENGTH_MM = ____
  [ ] Confidence threshold = ____ (in vision.py, line 174 and 197)
```

---

## Quick Reference: Commands

**Mavproxy (Pi Terminal 1 — always running):**
```bash
sudo /opt/mavlink/mavlink-venv/bin/mavproxy.py \
  --master=/dev/ttyAMA0 --baudrate=921600 --streamrate=10 \
  --out=udpout:127.0.0.1:14550 --out=tcpin:0.0.0.0:5762
```

**Passive flight (Pi Terminal 2):**
```bash
cd ~/dima/Group_Proj && source pienv/bin/activate
python tests/flight/1_passive_flight.py --headless --stream
```

**Full dashboard (Pi Terminal 2):**
```bash
cd ~/dima/Group_Proj && source pienv/bin/activate
python pi_flight.py --fps 4
```

**Laptop browser:**
```
http://<PI_IP>:8090
```

**Mission Planner:**
```
TCP → <PI_IP> → port 5762
```

**Dashboard buttons:**
```
N = investigate nearest cluster (fly to it)
Y = confirm as real dummy
I = log as item of interest
X = discard as false positive
L = land 7.5m north of estimate
M = resume manual control
FAKE DET = create fake detection for testing
```

**Kill switch:** RC mode switch → STABILIZE (overrides everything, always)

---

## Model Swap (if CV not working)

Models are in `cv_models/` folder:
```bash
# List available:
ls cv_models/
python tests/day_1_experiments/model_compare.py --list

# Option A: swap the default model file:
cp cv_models/sar_v2_1088/best.tflite best.tflite

# Option B: use --model flag (no copy needed):
python pi_flight.py --fps 4 --model cv_models/sar_v2_1088/best.tflite
python main.py --model cv_models/sar_v2_1088/best.tflite

# Compare all models on bench:
python tests/day_1_experiments/model_compare.py --frames 50
```

Currently available:
```
best.tflite                          — active model (copy whichever variant you want)
cv_models/sar_v2_1088/best.tflite    — retrained v2 (real+synthetic 1088, mAP50=0.995) ← BEST
cv_models/sar_640/best.tflite        — earlier training at 640x640
cv_models/sar_1280/best.tflite       — earlier training at 1280x1280
models/human.tflite                  — COCO YOLOv8n person detector (80 classes, backup)
```

If all models fail:
- Lower confidence threshold in vision.py (0.4 → 0.3 → 0.25)
- Try flying lower (5-10m)
- Use FAKE DET button to test command flow without CV

---

## Dry-Run (Test Pattern Without Flying)

```bash
# On Pi or laptop — no GPS, no arming, no Cube needed:
python main.py --dry-run

# With specific model:
python main.py --dry-run --model cv_models/sar_v2_1088/best.tflite
```

Shows:
- Search area from SEARCH_AREA_GPS in config.py
- Generated lawnmower waypoints (GPS coordinates)
- Transit distance, search path length, estimated flight time
- State machine walkthrough (every state transition printed)
- Map visualization (if map.jpg exists) saved to dry_run_pattern.jpg

**Before first real flight:** Run `--dry-run` to verify SEARCH_AREA_GPS coordinates
cover the intended field. Update config.py if wrong.
