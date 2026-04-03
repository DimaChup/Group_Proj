# Passive Detection Checklist -- For Colleague's Drone Flight

**Print this. Follow it step by step. No internet needed.**

Your drone, your RC, your flight. Our Raspberry Pi sits on the ground (or on your
drone) running a camera + AI. It watches passively, detects the dummy, estimates its
GPS coordinate, and saves a result image. It sends **ZERO commands** to your drone.

---

## Overview

```
YOU fly your drone manually via RC
  |
PI runs passive_watch.py (camera + AI model)
  |
Detections accumulate --> SMART lock triggers when enough agree
  |
Result image saved with GPS coordinate --> you use it for your mission
```

---

## PHASE 1: Pi Setup (Before Flying)

### 1.1 Power and Network

```
[ ] 1.1  Power on the Pi (USB battery pack or drone BEC)
[ ] 1.2  Connect Pi and your laptop to the SAME WiFi
         (phone hotspot is easiest -- both devices join your phone)
[ ] 1.3  Note the Pi IP address. SSH in and run:
             hostname -I
         Write it here: _______________
```

### 1.2 Pull Latest Code

```bash
# SSH into Pi:
ssh pi@<PI_IP>
cd ~/dima/Group_Proj
git pull
source pienv/bin/activate
```

### 1.3 Start Mavproxy (Terminal 1 -- only if Pi is connected to a Cube)

If the Pi camera is mounted on your drone with a Cube flight controller:

```bash
sudo /opt/mavlink/mavlink-venv/bin/mavproxy.py \
  --master=/dev/ttyAMA0 --baudrate=921600 --streamrate=10 \
  --out=udpout:127.0.0.1:14550 --out=tcpin:0.0.0.0:5762
```

If the Pi is standalone (no Cube connection), skip this step and add `--no-mavlink`
to the launch command. GPS overlay will not be available, but detection still works.

### 1.4 Quick Camera Check (Terminal 2)

```bash
cd ~/dima/Group_Proj && source pienv/bin/activate
python -c "from vision import VisionSystem; v=VisionSystem(); f=v.get_frame(); print('Camera OK' if f is not None else 'CAMERA FAIL')"
```

```
[ ] 1.4  Camera returns a frame (prints "Camera OK")
```

If it fails:
- Check the ribbon cable is seated properly
- Run `libcamera-hello --timeout 1000` to verify the camera works at OS level
- If another script is using the camera, kill it first (`pkill -f passive_watch`)

### 1.5 Choose Your Model

| Model | Path | What it detects | Size |
|-------|------|-----------------|------|
| Custom dummy (BEST) | `cv_models/sar_v2_1088/best.tflite` | Our SAR dummy | 11.7 MB |
| Custom dummy (original) | `best.tflite` | Our SAR dummy | 3.2 MB |
| COCO person detector | `models/human.tflite` | Any person (80 classes) | 13 MB |

**Recommendation:** Use `cv_models/sar_v2_1088/best.tflite` for the SAR dummy.
Use `models/human.tflite` if searching for a real person instead of our dummy.

---

## PHASE 2: Launch passive_watch.py

### 2.1 The Full Command

Open Terminal 2 on the Pi (or a second SSH session):

```bash
cd ~/dima/Group_Proj && source pienv/bin/activate

DISPLAY= python field_tools/passive_watch.py \
  --model cv_models/sar_v2_1088/best.tflite \
  --conf 0.3 \
  --smart-estimate \
  --smart-min 5 \
  --smart-radius 1.0 \
  --save-dir detections \
  --port 8090
```

### 2.2 Flag Reference

| Flag | Default | What it does |
|------|---------|--------------|
| `--model PATH` | `best.tflite` | Which AI model to load. Use full path. |
| `--conf 0.3` | `0.4` | Minimum confidence to count a detection. Lower = more sensitive but more false positives. Start at 0.3, raise to 0.4 if too many false alarms. |
| `--smart-estimate` | OFF | Enable SMART mode: accumulates detections and locks when enough agree on a GPS coordinate. **You want this on.** |
| `--smart-min 5` | `5` | How many agreeing detections needed before SMART locks. 5 is good for a single flyover. Raise to 10 for multiple passes. |
| `--smart-radius 1.0` | `1.0` | Max spread (metres) between the agreeing detections. 1.0m means all 5 detections must fall within a 1m circle. Raise to 2.0 if GPS is noisy. |
| `--smart-dir PATH` | `<save-dir>/smart_detections/` | Where SMART result images are saved. Default is `detections/smart_detections/`. |
| `--save-dir DIR` | `detections` | Base directory for all saved snapshots, JSON, and CSV. |
| `--class-filter NAME` | None (all) | Only count detections of this class. Use `person` with human.tflite, or leave blank for custom dummy model. |
| `--port 8090` | `8090` | HTTP port for the browser dashboard. Change if 8090 is in use. |
| `--no-mavlink` | OFF | Skip Cube/mavproxy connection. Use this if Pi has no flight controller. GPS overlay will be blank. |
| `--no-save` | OFF | Don't save any files. Stream only. |
| `--fps N` | `5` | Legacy throttle (inference now runs as fast as the model allows). |

### 2.3 Confirm It Started

You should see output like:

```
==================================================
  passive_watch.py — Passive Camera Observer
==================================================
  Confidence: 0.3
  Max FPS:    5
  Saving to:  detections/
  Keys:       C = Clear All (reset SMART + detections)

  Dashboard:  http://192.168.x.x:8090/
  Stream:     http://192.168.x.x:8090/stream
  Snapshot:   http://192.168.x.x:8090/snapshot
```

```
[ ] 2.3  passive_watch.py started without errors
[ ] 2.4  Open http://<PI_IP>:8090/ in your laptop browser
[ ] 2.5  Live video stream is visible in the dashboard
```

---

## PHASE 3: During Flight

### 3.1 What You See in the Browser (http://PI_IP:8090/)

The dashboard has these panels:

| Panel | What it shows |
|-------|---------------|
| **Live Stream** (top left) | Camera feed with detection overlay, crosshair, GPS bar, compass |
| **Latest Detection** (top right) | Frozen frame from the most recent detection |
| **Bullseye** (bottom left) | GPS scatter plot of all detection estimates with bullseye rings |
| **SMART Grid** (bottom centre) | Thumbnails of the detections in the locked cluster |
| **Map** (bottom right) | Satellite map overlay with detection markers |

**Control bar** at the top lets you:
- Switch AI model (dropdown)
- Adjust confidence threshold (slider)
- Set class filter
- **Clear All** button -- resets everything (same as pressing C in terminal)
- **Reset Best** button -- clears the "best detection" panel

### 3.2 What the Terminal Shows

Every 50 frames you get a status line:

```
  #150 CAM:14.2 VIS:4.8 STR:12.1 Det:3 (2%) Saved:3 GPS:51.4234000,-2.6715000
```

- **CAM** = camera FPS (should be 10-15 on Pi)
- **VIS** = inference FPS (how fast AI runs -- 4-5 on Pi with TFLite)
- **Det** = total detections so far
- **Saved** = snapshots saved to disk

When SMART is accumulating detections, you see:

```
  [SMART] 3 detections, tightest 5 spread: 2.14m (need <1.0m)
  [SMART] 7 detections, tightest 5 spread: 0.83m (need <1.0m)
  [SMART] *** LOCKED! Spread: 0.83m ***
  [SMART] Median: 51.4233847, -2.6714532 (5 samples)
```

### 3.3 What a Detection Looks Like

- **Green box** appears around the dummy in the stream
- Box fades over 2 seconds between inference frames
- **Pink line** from detection centre to frame crosshair
- **Bottom bar** shows: `DUMMY EST: 51.4233847, -2.6714532 (N obs)`

### 3.4 Flight Tips for Best Detection

- Fly OVER the dummy, not beside it (camera points straight down)
- 10-25m altitude gives best detection confidence
- Slow passes (3-5 m/s) give more frames per flyover
- Multiple passes from different directions improve GPS accuracy
- The SMART estimator needs the dummy to be detected from multiple frames --
  a single flash detection is not enough

---

## PHASE 4: SMART Lock

### 4.1 What SMART Lock Means

SMART mode collects individual GPS estimates from each detection frame. When it finds
a cluster of `--smart-min` estimates (default 5) that all fall within `--smart-radius`
metres of each other (default 1.0m), it **locks**.

Lock means: "I am confident the dummy is at THIS coordinate."

### 4.2 What Happens at Lock

1. Terminal prints:
   ```
   ============================================================
     [SMART IMAGE SAVED] detections/smart_detections/0001_51.4233847_-2.6714532.png
     Coordinate: 51.4233847, -2.6714532  Spread: 0.83m
   ============================================================
   ```

2. A green **"TARGET FOUND"** banner flashes on the stream for 5 seconds

3. A result image is saved (see Phase 5 for details)

4. The SMART grid panel in the browser fills with the 5 detection thumbnails

### 4.3 What "Spread" Means

Spread is the maximum distance (in metres) between the detection estimates in
the locked cluster. Lower spread = higher confidence in the coordinate.

| Spread | Interpretation |
|--------|---------------|
| < 0.5m | Excellent -- very tight cluster |
| 0.5 - 1.0m | Good -- typical for a single pass at 15-20m altitude |
| 1.0 - 2.0m | Acceptable -- increase --smart-radius if you need this |
| > 2.0m | Poor -- fly lower or slower, or do more passes |

### 4.4 If SMART Doesn't Lock

- Not enough detections yet: fly over the dummy again, slower
- Spread too high: detections are scattered. Causes:
  - Flying too fast (fewer frames, more motion blur)
  - Flying too high (larger projection error)
  - GPS noise (100-200ms GPS lag causes ~1m error at 5 m/s)
- **Try:** lower altitude (15m), slower speed (3 m/s), multiple passes
- **Try:** increase `--smart-radius` to 2.0 if conditions are poor
- **Try:** decrease `--smart-min` to 3 for faster lock (less confidence)

---

## PHASE 5: Reading the Result

### 5.1 Where to Find the Result Image

```
detections/
  smart_detections/
    0001_51.4233847_-2.6714532.png    <-- THIS IS YOUR RESULT
```

The filename contains the GPS coordinate: `NNNN_LAT_LON.png`

If `--smart-dir` was specified, images go there instead.

### 5.2 What the Result Image Contains

The saved PNG is the best detection frame (most centred on the dummy) with:

- **"SMART COORDINATE"** banner at the top
- **GPS coordinate** in large text: `51.4233847, -2.6714532`
- **Stats**: spread, number of samples, method
- **Detection box** (green) around the dummy
- **Crosshair** at frame centre
- **GPS bar** at bottom with drone position

### 5.3 Using the Coordinate

The coordinate is the estimated GPS position of the dummy on the ground.

**To enter into Mission Planner:**
1. Right-click the map at the coordinate
2. Or: enter manually in the Flight Plan tab

**Expected accuracy:** 1-3 metres (depends on altitude, speed, GPS quality).

---

## PHASE 6: Re-triggering (Detecting Again)

After a SMART lock, the estimator stops collecting. To detect a new target
or re-detect the same one:

### Option A: Press C in the Pi terminal

```
Press C in the terminal running passive_watch.py
```

This clears ALL data:
- SMART estimator resets (unlocked, ready for new detections)
- All GPS estimates cleared
- Best detection cleared
- Bullseye plot cleared
- Detection counter resets

Terminal confirms: `[CLEAR ALL] Reset SMART + detections. Ready for next detection.`

### Option B: Click "Clear All" in the browser dashboard

Same effect as pressing C. The red **Clear All** button is in the top control bar.

After clearing, fly over the target again. SMART will start accumulating fresh.

---

## PHASE 7: After Landing

### 7.1 Collect Output Files

All outputs are in the `--save-dir` directory (default: `detections/`):

```
detections/
  smart_detections/
    0001_51.4233847_-2.6714532.png   -- SMART result image (your main output)
    0002_51.4234100_-2.6713200.png   -- second lock (if you cleared and re-ran)
  det_0001_0.87_51.423_-2.671.jpg    -- individual detection snapshot
  det_0001_0.87_51.423_-2.671.json   -- metadata sidecar (GPS, FOV, confidence)
  det_0002_...                       -- more snapshots
  detection_log.csv                  -- all detections in one CSV
```

**Note:** In `--smart-estimate` mode, individual detection snapshots (det_NNNN) are
NOT saved to disk -- only the SMART result image is saved. This is intentional:
SMART mode accumulates in memory and saves one clean result.

If you want individual snapshots too, run WITHOUT `--smart-estimate`.

### 7.2 Copy Files Off the Pi

```bash
# From your laptop:
scp -r pi@<PI_IP>:~/dima/Group_Proj/detections/ ./detections_from_pi/

# Or copy just the SMART results:
scp pi@<PI_IP>:~/dima/Group_Proj/detections/smart_detections/*.png ./
```

### 7.3 JSON Sidecar Format (for post-analysis)

Each `det_NNNN.json` contains:

```json
{
  "timestamp": "2026-04-03T14:23:01",
  "detection": {"cx": 0.52, "cy": 0.48, "conf": 0.87, "class": "dummy"},
  "drone": {"lat": 51.4234000, "lon": -2.6715000, "alt": 20.3, "yaw": 155.0},
  "fov": {"hfov_deg": 54.4, "ground_w_m": 18.2, "ground_h_m": 13.6},
  "estimate": {"lat": 51.4233847, "lon": -2.6714532}
}
```

---

## Troubleshooting

### No detections at all

```
Symptom: VIS FPS is running but Det stays at 0
```

1. **Is the dummy in frame?** Check the live stream -- can YOU see the dummy?
2. **Lower confidence:** Restart with `--conf 0.2` or `--conf 0.15`
3. **Wrong model?** Custom dummy model won't detect a real person. Use `--model models/human.tflite --class-filter person` for real people.
4. **Too high:** Fly lower (10-15m). Detection drops off above 25m.
5. **Camera pointing wrong way:** The camera must point straight down. Check `CAMERA_FLIP_180 = True` in config.py if the image is upside down.

### Detections but SMART won't lock

```
Symptom: [SMART] spread stays above --smart-radius
```

1. **Increase radius:** Restart with `--smart-radius 2.0` or `--smart-radius 3.0`
2. **Decrease min samples:** Restart with `--smart-min 3`
3. **Fly slower:** 3 m/s gives more frames, tighter cluster
4. **Fly lower:** 15m altitude reduces projection error
5. **Multiple passes:** Fly over from different directions

### Port conflict (Address already in use)

```
Symptom: OSError: [Errno 98] Address already in use
```

Another script is using port 8090. Either:
- Kill it: `pkill -f passive_watch` or `pkill -f pi_flight`
- Use a different port: `--port 8091`

### Camera not working

```
Symptom: Camera returns None / "CAMERA FAIL"
```

1. Check ribbon cable is fully seated (both ends)
2. Run `libcamera-hello --timeout 1000` -- if this fails, it's a hardware issue
3. Kill any other process using the camera: `pkill -f passive_watch`
4. Reboot the Pi if nothing else works

### Stream is very slow / laggy

- This is normal on Pi -- inference runs at ~5 FPS, stream updates at ~12-15 FPS
- The stream is MJPEG over WiFi; latency depends on network quality
- Move laptop closer to the WiFi source (phone hotspot)
- Do NOT open multiple browser tabs to the stream (each is a separate connection)

### No GPS overlay (GPS: --- in stream)

- If no Cube is connected, add `--no-mavlink` to suppress connection attempts
- If Cube is connected, check mavproxy is running in Terminal 1
- GPS needs a 3D fix (fix_type=3) before coordinates appear -- wait 1-5 min outdoors

---

## Quick Reference Card

**Start command (copy-paste):**
```bash
cd ~/dima/Group_Proj && source pienv/bin/activate
DISPLAY= python field_tools/passive_watch.py \
  --model cv_models/sar_v2_1088/best.tflite \
  --conf 0.3 \
  --smart-estimate \
  --smart-min 5 \
  --smart-radius 1.0
```

**Browser:** `http://<PI_IP>:8090/`

**Terminal keys:** `C` = Clear All and re-detect

**Result location:** `detections/smart_detections/NNNN_LAT_LON.png`

**Kill:** `Ctrl+C` in the terminal running passive_watch.py

**Safety:** This script sends ZERO commands. It cannot arm, disarm, or move any drone.
