# Passive Watch Usage Guide

```
THIS FILE IS FOR ROBIN
Passive watch runs AI detection and saves GPS coordinates to a directory.
Sends ZERO drone commands. Completely safe to run during any flight.
```

---

## Robin's Exact Command

```bash
cd ~/dima/Group_Proj && source pienv/bin/activate
python field_tools/passive_watch.py --compensate-tilt --conf 0.3 \
  --smart-estimate --smart-min 5 --smart-radius 2.0 \
  --smart-dir robin_detections --model best.tflite
```

**Browser dashboard:** `http://PI_IP:8090/` (replace PI_IP with the Pi's IP, find it with `hostname -I`)

Use `--port 8091` if another script already uses port 8090.

---

## What Robin Gets

When the SMART estimator locks (enough detections agree on a GPS position), it saves:

1. **A PNG image** in `robin_detections/` with the GPS coordinate embedded in the filename
2. **A terminal printout** with the coordinate and spread

### Filename format

```
robin_detections/0001_51.4233990_-2.6715320.png
robin_detections/0002_51.4234050_-2.6715410.png
```

The format is: `<counter>_<latitude>_<longitude>.png`

### How to parse the filename

```python
import os, re

for fname in sorted(os.listdir("robin_detections")):
    if not fname.endswith(".png"):
        continue
    parts = fname.replace(".png", "").split("_")
    # parts = ["0001", "51.4233990", "-2.6715320"]
    lat = float(parts[1])
    lon = float(parts[2])
    print(f"Target at {lat}, {lon}")
```

### Per-detection JSON sidecars (in detections/ directory)

In addition to SMART results, every individual detection also saves a JSON sidecar in `detections/` (the default save directory). Example JSON:

```json
{
  "timestamp": "2026-03-31T14:22:05.123456",
  "frame": 1523,
  "detection": {
    "confidence": 0.87,
    "pixel_x": 728,
    "pixel_y": 544,
    "bbox_centre": [728, 544]
  },
  "drone": {
    "lat": 51.4234060,
    "lon": -2.6715320,
    "alt_m": 35.0,
    "yaw_deg": 155.2,
    "pitch_deg": -2.1,
    "roll_deg": 0.3,
    "sats": 14,
    "mode": "GUIDED"
  },
  "fov": {
    "focal_mm": 5.46,
    "sensor_w_mm": 5.02,
    "hfov_deg": 49.3,
    "ground_w_m": 32.18,
    "ground_h_m": 24.03
  },
  "estimate": {
    "lat": 51.4233990,
    "lon": -2.6715320,
    "n_observations": 7
  },
  "image": "det_0001_0.87_51.4234060_-2.6715320.jpg"
}
```

Key fields for Robin:
- `estimate.lat` / `estimate.lon` -- the estimated GPS of the target (not the drone)
- `drone.lat` / `drone.lon` -- where the drone was when it saw the target
- `detection.confidence` -- how confident the AI is (0.0 to 1.0)

### HTTP API (alternative to reading files)

Robin's code can also poll the HTTP API instead of reading files:

```
GET http://PI_IP:8090/api/estimates-full
```

Returns JSON with cluster data:
```json
{
  "estimates": [[51.4234, -2.6715, 0.3, 35.0, 0.87], ...],
  "smart": {
    "locked": true,
    "cluster": [[51.4233990, -2.6715320, 0.15], ...],
    "spread": 0.83,
    "median": [51.4233990, -2.6715320]
  },
  "mean": [51.4234010, -2.6715300],
  "n": 12
}
```

When `smart.locked` is `true`, `smart.median` is the consensus target position.

Other useful endpoints:
- `GET /api/status` -- detection counts, FPS, whether SMART has locked
- `GET /api/drone` -- current drone GPS, altitude, heading
- `GET /api/estimates` -- simple list of all GPS estimates as `[[lat, lon], ...]`

---

## Prerequisites

### 1. mavproxy must be running (Terminal 1 on Pi)

```bash
sudo /opt/mavlink/mavlink-venv/bin/mavproxy.py \
  --master=/dev/ttyAMA0 --baudrate=921600 --streamrate=10 \
  --out=udpout:127.0.0.1:14550 \
  --out=tcpin:0.0.0.0:5762
```

Wait for: `Detected vehicle 1:0` and `online system 1`.

Without mavproxy, passive_watch has no GPS data and cannot geotag detections. You can still run with `--no-mavlink` for stream-only mode (no GPS, no coordinate output -- mostly useless for Robin).

### 2. Camera must be available

The Pi camera (IMX296) must not be in use by another script. Only ONE process can use the camera at a time.

### 3. pienv venv activated

```bash
source pienv/bin/activate
```

### 4. Model file exists

Default: `best.tflite` in the project root. Copy the best model:
```bash
cp cv_models/sar_v2_1088/best.tflite best.tflite
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| **"Cannot open camera"** | Another script has the camera. Kill it: `sudo pkill -f python; sleep 2` |
| **"Address already in use" (port conflict)** | Another script is on port 8090. Use `--port 8091` or kill: `sudo pkill -f passive_watch; sleep 2` |
| **No GPS overlay / no coordinates** | mavproxy not running. Start it first (see Prerequisites above) |
| **No detections at all** | Lower confidence: `--conf 0.2`. Check model file exists: `ls -la best.tflite` |
| **SMART never locks** | Increase `--smart-radius` to 3.0 or decrease `--smart-min` to 3. Fly over the target multiple times. |
| **Browser shows black frame** | Camera warming up (1-2 seconds), or camera not connected |
| **Very slow on Pi** | Use `--fps 3` to limit CPU. Or switch to NCNN model from browser dropdown |
| **Camera stuck after crash** | `sudo pkill -f libcamera; sudo pkill -f python; sleep 2` |
| **Pi IP unknown** | Run `hostname -I` on the Pi |

---

## Browser Dashboard

Open `http://PI_IP:8090/` (or whatever `--port` you set) in any browser on the same network.

### What you see

- **Camera Feed** -- live MJPEG stream with green detection overlay, GPS bar, crosshair
- **Latest Detection** -- most recent detection snapshot (zoomable)
- **Best Detection** -- detection closest to frame centre (zoomable)
- **SMART Frames** -- grid of frames contributing to the SMART cluster
- **Satellite Map** -- interactive map with drone position and detection markers
- **GPS Analysis** -- scatter plots of GPS estimates, error distribution

### Control Bar (top of page)

All controls adjust live without restarting:

| Control | What it does |
|---------|-------------|
| **Model** dropdown | Switch between Original, SAR v2 TFLite, SAR v2 NCNN, COCO Person |
| **Conf** slider | Adjust confidence threshold (0.05 - 0.95) |
| **Class** checkboxes | Filter: person, bird, dummy, other |
| **Clear All** button | Reset all detection state (SMART cluster, best detection, estimates) |
| **Reset Best** button | Reset the "best detection" panel only |
| **Smart spread/count** inputs | Adjust SMART parameters live |

### Terminal Keys

| Key | Action |
|-----|--------|
| `C` | **Clear All** -- reset SMART cluster, detection counts, best detection |
| `Ctrl+C` | Exit cleanly |

---

## All CLI Flags

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--port` | int | `8090` | HTTP server port for web dashboard and MJPEG stream |
| `--conf` | float | `0.4` | AI confidence threshold (0.0-1.0). Lower = more detections, more false positives |
| `--fps` | float | `5` | Maximum inference FPS. Limits CPU usage on Pi |
| `--save-dir` | str | `detections` | Directory for saved detection images and metadata |
| `--no-save` | flag | off | Disable saving snapshots to disk (stream only) |
| `--no-mavlink` | flag | off | Skip mavproxy connection. No GPS overlay or geotagging |
| `--no-stream` | flag | off | Disable HTTP stream server entirely |
| `--model` | str | `best.tflite` | Path to TFLite model file |
| `--simple-names` | flag | off | Clean filenames without `det_` prefix. No JSON sidecar files |
| `--class-filter` | str | none | Only save detections matching this class (e.g., `person`, `dummy`) |
| `--compensate-tilt` | flag | off | Apply tilt-corrected GPS estimation using pitch/roll from ATTITUDE message |
| `--smart-estimate` | flag | off | Enable SMART consensus lock (accumulate detections, lock when cluster is tight) |
| `--smart-min` | int | `5` | Minimum number of agreeing GPS estimates required for SMART lock |
| `--smart-radius` | float | `1.0` | Maximum cluster spread in metres for SMART lock |
| `--smart-dir` | str | `<save-dir>/smart_detections/` | Output directory for SMART result images |
| `--fake` | flag | off | Replay DJI video + SRT telemetry instead of live camera |
| `--fake-video` | str | `RealVideo/DJI_0001_1456x1088_cropped_30fps.mp4` | Video file for fake mode |
| `--fake-srt` | str | `RealVideo/DJI_20260311172332_0001_V.SRT` | SRT telemetry file for fake mode |

### Flag Examples

```bash
# Lower confidence to catch more detections
python field_tools/passive_watch.py --conf 0.25

# Use the retrained v2 model
python field_tools/passive_watch.py --model cv_models/sar_v2_1088/best.tflite

# Use the COCO person detector (80 classes, larger)
python field_tools/passive_watch.py --model cv_models/human.tflite --class-filter person

# SMART lock with tight clustering
python field_tools/passive_watch.py --smart-estimate --smart-min 8 --smart-radius 0.5

# Save clean images for training data collection
python field_tools/passive_watch.py --simple-names --save-dir training_captures

# Custom port (avoid conflicts with other scripts)
python field_tools/passive_watch.py --port 8091

# Laptop replay (no hardware needed)
python field_tools/passive_watch.py --fake --no-mavlink --conf 0.3
```

---

## How SMART Estimation Works

SMART (Smart Multi-pass Accumulation for Robust Targeting) accumulates GPS estimates from multiple flyover detections and locks when enough estimates agree.

### Algorithm: Greedy Tightest Cluster

1. Each detection produces a noisy GPS estimate via camera geometry
2. Once there are >= `--smart-min` estimates, search for the tightest cluster:
   - Compute all pairwise GPS distances (metres) between estimates
   - Seed the cluster with the closest pair of points
   - Greedily add the point that minimises the cluster's maximum spread
   - Repeat until the cluster has `smart-min` points
3. If the cluster's max spread < `--smart-radius` metres: **LOCK**
   - Median lat/lon of the cluster = target position
   - Result image saved to `--smart-dir`
   - Terminal prints the coordinate
   - No further estimates accepted after lock (press Clear All or 'C' to reset and re-lock)

### Recommended Parameters

| Scenario | `--smart-min` | `--smart-radius` |
|----------|---------------|-------------------|
| Quick test | 3 | 3.0 |
| Normal flight | 5 | 2.0 |
| High confidence | 10 | 0.5 |

Parameters can be changed live from the browser control bar without restarting.

---

## How Tilt Compensation Works (`--compensate-tilt`)

Without tilt compensation, GPS estimation assumes the camera points straight down. In reality, drones tilt during flight (pitch forward when flying, roll in turns). This causes GPS estimation errors of 5-10+ metres.

With `--compensate-tilt`:
1. Reads pitch, roll, yaw from the MAVLink ATTITUDE message
2. Builds a full rotation matrix to correct for drone orientation
3. Ray-traces from drone position through the detection pixel down to the ground plane
4. Reduces error from ~6.2m average to ~0.3m average

Always use this flag during real flights.

---

## Available AI Models

Models can be switched live from the browser dropdown:

| ID | Name | File | Notes |
|----|------|------|-------|
| 0 | Original | `best.tflite` | Default custom dummy detector (3.2MB) |
| 1 | SAR v2 TFLite | `cv_models/sar_v2_1088/best.tflite` | Retrained on real+synthetic data (11.7MB, mAP50=0.995) |
| 2 | SAR v2 NCNN | `cv_models/sar_v2_1088/best.tflite` | Same model, NCNN backend (~4.5x faster) |
| 3 | COCO Person | `cv_models/human.tflite` | 80-class COCO detector, detects people (~13MB, slower) |

---

## Camera Sharing Warning

**passive_watch and main.py CANNOT run at the same time.** Both open the Pi camera -- only one process can use it.

Workflow:
1. Run passive_watch during manual RC flights
2. `Ctrl+C` passive_watch when done
3. Wait 2 seconds for camera release
4. Then start main.py if needed

If camera is stuck: `sudo pkill -f libcamera; sudo pkill -f python; sleep 2`
