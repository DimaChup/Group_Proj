# Final Flight Day Checklist

**Print this. Follow top to bottom. Copy-paste the commands.**

---

## Before Arriving

```
[ ] Push latest code:  git add -A && git commit -m "flight day" && git push
[ ] Charge drone LiPo (4.2V/cell), charge Pi power bank
[ ] Copy best model to root:  cp cv_models/sar_v2_1088/best.tflite best.tflite
[ ] Pack: laptop, RC, phone (hotspot), measuring tape, printed dummy
[ ] Verify dry-run:  python main.py --dry-run
```

---

## Hardware Setup

```
[ ] Assemble drone, mount Pi + camera facing DOWN
[ ] Connect Pi to Cube serial (TX->RX, RX->TX, shared GND)
[ ] Power Pi (USB-C power bank or drone BEC)
[ ] Power Cube (LiPo connected)
[ ] RC transmitter ON, bound to Cube
```

---

## Network

Both Pi and laptop on same WiFi (phone hotspot is easiest).

```bash
# On Pi — find IP:
hostname -I
```

Write Pi IP here: `_________________`

```bash
# On Pi — pull latest code:
cd ~/dima/Group_Proj && git pull
```

---

## Terminal Setup (3 PuTTY windows to Pi)

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
- If Robin/Zian are running their OWN mavproxy: **two mavproxy on the same serial port will NOT work**
- Solution: run ONE shared mavproxy with extra `--out` for each script that needs it
- Add `--out=udpout:127.0.0.1:14552` etc for additional consumers
- passive_watch uses 14550, main.py uses 14550 -- if running both, give one a different port via DRONE_CONN env var

### Terminal 2: passive_watch (Robin's CV observer)

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

**Key facts about passive_watch:**
- Sends ZERO commands to drone -- completely safe
- Reads GPS from mavproxy (udpin:14550) for geotagging -- needs mavproxy running
- `--no-mavlink` skips GPS entirely (no GPS overlay, no geotagging -- mostly useless)
- Uses `--port 8091` to avoid conflict with main.py on 8090
- `--class-filter person` to only save person detections (use with human.tflite model)

### Terminal 3: main.py (autonomous mission)

```bash
cd ~/dima/Group_Proj && source pienv/bin/activate
python main.py --headless --alt 25
```

**Browser:** `http://PI_IP:8090/`

---

## CRITICAL CONFLICT: Camera Sharing

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

---

## CRITICAL CONFLICT: Stream Port

| Script | Default Port | Fix |
|--------|-------------|-----|
| passive_watch.py | 8090 | Use `--port 8091` |
| main.py | 8090 | Keep default |
| capture_training.py | 8091 | Already different |

**Solution already applied above:** passive_watch runs on 8091, main.py on 8090.

---

## Laptop Connections

### Mission Planner
```
Connection → TCP → PI_IP → port 5762
```

### Browser dashboards
```
passive_watch:  http://PI_IP:8091/
main.py:        http://PI_IP:8090/
```

---

## Pre-Flight Safety Checks

```
[ ] GPS fix:  python tests/hardware/gps_test.py
    Need: fix_type=3, sats >= 8, Here3+ LED = flashing GREEN
[ ] RC kill switch test: flip to STABILIZE in Mission Planner, confirm mode changes
[ ] Flip back to GUIDED, confirm mode changes back
[ ] RC failsafe: Mission Planner > Config > Failsafe > Radio = RTL
[ ] Benchmark:  python tests/hardware/benchmark.py
    Record: ___ms avg, ___FPS, ___/50 detections
```

---

## Progressive Flight Steps

### Step 1: Mission Planner AUTO (no custom code)

```
[ ] Upload 4-waypoint square in MP at 15m altitude
[ ] Arm via RC, switch to AUTO
[ ] Drone flies pattern, RTLs
[ ] PASSED? Yes/No
```

### Step 2: Waypoint test (your code, no CV)

```bash
python tests/flight/2_waypoints.py --dry-run     # verify plan
python tests/flight/2_waypoints.py --alt 10       # real flight
```

```
[ ] Arms, takes off, flies waypoints, lands
[ ] PASSED? Yes/No
```

### Step 3: Passive CV (pilot flies RC, Pi watches)

**Stop main.py first. Start passive_watch.**

```bash
python field_tools/passive_watch.py --port 8091 --conf 0.3 --smart-estimate
```

Browser: `http://PI_IP:8091/`

```
[ ] Pilot hovers over dummy at 10m, 15m, 20m, 25m, 30m (30s each)
[ ] Record: max detection altitude = ___m, confidence = ___
[ ] Fly over dummy at 3/5/7 m/s at 15m
[ ] Record: max speed with detection = ___ m/s
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

## Kill Switch

**RC mode switch to STABILIZE -- overrides EVERYTHING, always.**

RC pilot's hand on kill switch at ALL times.

Ctrl+C on any script triggers RTL.

---

## Model Swap (if CV not detecting)

```bash
# Best model (retrained on real data):
cp cv_models/sar_v2_1088/best.tflite best.tflite

# COCO person detector (backup, 80 classes):
cp models/human.tflite best.tflite

# Or use --model flag (no copy needed):
python main.py --headless --model cv_models/sar_v2_1088/best.tflite
```

Lower confidence (if missing detections): edit `vision.py` line ~174, change `0.4` to `0.3` or `0.25`

---

## Post-Flight

```bash
# Copy logs to laptop:
scp pi@PI_IP:~/dima/Group_Proj/flight_log.csv .
scp -r pi@PI_IP:~/dima/Group_Proj/detections/ .
scp -r pi@PI_IP:~/dima/Group_Proj/robin_detections/ .
scp -r pi@PI_IP:~/dima/Group_Proj/mission_detections/ .

# Commit on Pi:
cd ~/dima/Group_Proj
git add -A && git commit -m "flight day data" && git push
```

Record results:
```
Max detection altitude:   ___m
Max detection speed:      ___ m/s
Avg confidence:           ___
Inference FPS on Pi:      ___
Landing distance error:   ___m
False positives seen:     ___
Config updates needed:    TARGET_ALT=___, SEARCH_SPEED_MPS=___
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
