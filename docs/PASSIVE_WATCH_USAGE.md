# Passive Watch Usage Guide

**File:** `field_tools/passive_watch.py` (3421 lines)

---

## What It Does

Passive camera observer that runs AI detection, estimates target GPS coordinates, and streams results to a web dashboard. It sends **ZERO commands** to the drone -- completely safe to run at any time, during manual RC flight or on the bench.

Features:
- Live MJPEG video stream with detection overlay at `http://PI_IP:8090/`
- YOLOv8 AI detection (TFLite or NCNN backend)
- GPS estimation of detected targets using camera geometry
- SMART consensus lock: accumulates detections until a tight GPS cluster emerges
- Saves detection images + JSON metadata to disk
- Model switching, confidence tuning, and class filtering from the browser UI
- Tilt-compensated GPS projection (corrects for drone pitch/roll)
- Fake mode: replay DJI video with SRT telemetry on laptop (no hardware needed)

---

## Quick Start

### Simulation / Laptop (replay DJI video)

```bash
cd v3
python field_tools/passive_watch.py --fake --no-mavlink --conf 0.3
# Open http://localhost:8090/ in browser
```

### Real Flight on Pi (with GPS from mavproxy)

```bash
source pienv/bin/activate
cd ~/dima/Group_Proj
python field_tools/passive_watch.py --compensate-tilt --conf 0.3 \
  --smart-estimate --smart-dir robin_detections
# Open http://PI_IP:8090/ in browser
```

### Robin's Recommended Command

```bash
python field_tools/passive_watch.py --compensate-tilt --conf 0.3 \
  --smart-estimate --smart-min 5 --smart-radius 2.0 \
  --smart-dir robin_detections --model best.tflite
```

### Minimal (stream only, no saving)

```bash
python field_tools/passive_watch.py --no-save --no-mavlink
```

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
```

---

## Web Dashboard

Open `http://PI_IP:8090/` in any browser. The dashboard shows:

### Row 1: Video + Detections
- **Camera Feed** -- live MJPEG stream with detection overlay (green bounding box, GPS bar, crosshair)
- **Latest Detection** -- most recent detection snapshot (zoomable)
- **Best Detection** -- detection closest to frame centre (zoomable)
- **SMART Frames** -- grid of frames contributing to the SMART cluster

### Row 2: Map + GPS Analysis
- **Satellite Map** -- interactive map with drone position and detection markers
- **GPS Analysis** -- scatter plots of GPS estimates, error distribution

### Row 3: Pipeline Visualizations
- **CV Detection Pipeline** -- step-by-step detection pipeline visualization
- **GPS Estimation Pipeline** -- GPS projection math visualization

### Control Bar (top of page)
All controls are adjustable live from the browser without restarting:

| Control | What it does |
|---------|-------------|
| **Model** dropdown | Switch between Original, SAR v2 TFLite, SAR v2 NCNN, COCO Person |
| **Conf** slider | Adjust confidence threshold (0.05 - 0.95) |
| **Class** checkboxes | Filter: person, bird, dummy, other |
| **Clear All** button | Reset all detection state (SMART cluster, best detection, estimates) |
| **Reset Best** button | Reset the "best detection" panel only |
| **Smart spread/count** inputs | Adjust SMART parameters live |

### HTTP Endpoints

| Endpoint | Returns |
|----------|---------|
| `/` | Dashboard HTML page |
| `/stream` | Raw MJPEG stream (for embedding in other tools) |
| `/snapshot` | Latest detection JPEG |
| `/latest` | Latest detection thumbnail |
| `/best` | Best detection thumbnail |
| `/smart-grid` | SMART frames grid image |
| `/api/status` | JSON: frame count, FPS, detections, saved count |
| `/api/drone` | JSON: drone GPS, altitude, heading, attitude |
| `/api/estimates` | JSON: all GPS estimates (lat, lon) |
| `/api/estimates-full` | JSON: full estimate data with cluster info |
| `/api/switch-model?id=N` | Switch AI model (0-3) |
| `/api/set-conf?val=X` | Set confidence threshold |
| `/api/set-class?name=X` | Set class filter |
| `/api/clear-all` | Reset all detection state |
| `/api/reset-best` | Reset best detection |
| `/api/set-smart?spread=X&count=Y` | Update SMART parameters |
| `/api/set-ground-truth?lat=X&lon=Y` | Set known target position (for error calculation) |
| `/api/clear-ground-truth` | Remove ground truth marker |
| `/api/toggle-bullseye-bg` | Toggle satellite map behind bullseye scatter plots |

---

## Terminal Keys

While running in a terminal (PuTTY/SSH or local):

| Key | Action |
|-----|--------|
| `C` | **Clear All** -- reset SMART cluster, detection counts, best detection |
| `Ctrl+C` | Exit cleanly |

---

## Output Format

### Standard Mode (default)

Detection images saved to `<save-dir>/` (default: `detections/`):

**Image filename:**
```
det_0001_0.87_51.4234060_-2.6715320.jpg    # with GPS
det_0002_0.65_nogps.jpg                     # without GPS
```

**JSON sidecar** (same name, `.json` extension):
```json
{
  "timestamp": "2026-03-31T14:22:05.123456",
  "frame": 1523,
  "detection": {
    "confidence": 0.87,
    "pixel_x": 728, "pixel_y": 544,
    "bbox_centre": [728, 544]
  },
  "drone": {
    "lat": 51.4234060, "lon": -2.6715320,
    "alt_m": 35.0,
    "yaw_deg": 155.2,
    "pitch_deg": -2.1
  }
}
```

**CSV log** (`detection_log.csv` in save-dir): one row per detection with frame, timestamp, confidence, drone GPS, estimated target GPS.

### Simple Names Mode (`--simple-names`)

Clean filenames, no JSON sidecars, no CSV log:
```
0001_51.4233990_-2.6715320.jpg    # estimated target GPS in filename
0002_51.4234010_-2.6715280.jpg
0003_nogps.jpg                     # no GPS available
```

### SMART Result Images

When the SMART estimator locks (enough detections agree), a result image is saved to `<smart-dir>/`:

```
smart_detections/0001_51.4233990_-2.6715320.png
```

The result image includes:
- The best detection frame (target most centred)
- SMART coordinate overlay (median lat/lon of the locked cluster)
- Spread and CEP50 statistics
- Map panel showing SSSI polygon (red), search area (yellow), and target position (magenta star)

---

## How Tilt Compensation Works (`--compensate-tilt`)

Without tilt compensation, GPS estimation assumes the camera points straight down. In reality, drones tilt during flight (pitch forward when flying, roll in turns). This causes GPS estimation errors of 5-10+ metres.

### The Math

1. Reads pitch, roll, yaw from the MAVLink ATTITUDE message
2. Builds a full rotation matrix: `R = Rz(yaw) @ Ry(-pitch) @ Rx(-roll)`
3. Converts the detection pixel to a camera-frame ray using focal length
4. Rotates the ray into the world frame (NED: North, East, Down)
5. Ray-traces from drone position at altitude down to the ground plane
6. Intersection point = estimated target GPS

### When It Activates

- Only when tilt exceeds 0.5 degrees in pitch or roll
- Below 0.5 degrees, falls back to flat-earth projection (equivalent, less computation)
- If the ray is nearly horizontal (rw2 < 0.01), falls back to flat-earth to avoid extreme projections

### Improvement

- Tested reduction from ~6.2m average error to ~0.3m error
- Uses the same verified rotation matrix approach as main.py (proven with 1440 unit tests)

---

## How SMART Estimation Works (`--smart-estimate`)

SMART (Smart Multi-pass Accumulation for Robust Targeting) accumulates GPS estimates from multiple flyover detections and locks when enough estimates agree.

### Algorithm: Greedy Tightest Cluster

1. Each detection produces a noisy GPS estimate via `DummyEstimator`
2. Once there are >= `--smart-min` estimates, search for the tightest cluster:
   - Compute all pairwise GPS distances (metres) between estimates
   - Seed the cluster with the closest pair of points
   - Greedily add the point that minimises the cluster's maximum spread
   - Repeat until the cluster has `smart-min` points
3. If the cluster's max spread < `--smart-radius` metres: **LOCK**
   - Median lat/lon of the cluster = target position
   - Best frame (detection closest to image centre) saved as reference
   - No further estimates accepted after lock

### Parameters

| Parameter | Flag | Default | Effect |
|-----------|------|---------|--------|
| Min samples | `--smart-min` | 5 | More = higher confidence, takes longer to lock |
| Max spread | `--smart-radius` | 1.0m | Smaller = stricter agreement, may not lock in high-noise conditions |

### Typical Values

| Scenario | `--smart-min` | `--smart-radius` |
|----------|---------------|-------------------|
| Quick test | 3 | 2.0 |
| Normal flight | 5 | 1.0 |
| High confidence | 10 | 0.5 |

### Adjusting Live

SMART parameters can be changed from the browser control bar without restarting. The cluster resets when parameters change.

---

## Integration with Robin's State Machine

Robin's autonomous code can poll the SMART output directory for locked target coordinates:

1. passive_watch runs continuously during flight, saving SMART results to `--smart-dir`
2. Each SMART lock produces a PNG image and the GPS coordinate is embedded in the filename:
   ```
   robin_detections/0001_51.4233990_-2.6715320.png
   ```
3. Robin's code can parse the filename to extract lat/lon, or query the HTTP API:
   ```
   GET /api/estimates-full
   ```
   Returns JSON with cluster data, spread, and median coordinate.

4. The `/api/status` endpoint reports detection counts and whether a SMART lock has occurred.

---

## Available AI Models

Models can be switched live from the browser dropdown:

| ID | Name | File | Notes |
|----|------|------|-------|
| 0 | Original | `best.tflite` | Default custom dummy detector (3.2MB) |
| 1 | SAR v2 TFLite | `cv_models/sar_v2_1088/best.tflite` | Retrained on real+synthetic data (11.7MB, mAP50=0.995) |
| 2 | SAR v2 NCNN | `cv_models/sar_v2_1088/best.tflite` | Same model, NCNN backend (~4.5x faster) |
| 3 | COCO Person | `cv_models/human.tflite` | 80-class COCO detector, detects people (~13MB, slower) |

To use a different model from the command line:
```bash
python field_tools/passive_watch.py --model cv_models/sar_v2_1088/best.tflite
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "Cannot open camera" | Another script has the camera. Kill it: `pkill -f passive_watch` |
| No GPS overlay | Mavproxy not running, or use `--no-mavlink` for stream-only |
| Port already in use | Use `--port 8091` or kill the other process |
| Very slow on Pi | Lower FPS: `--fps 3`. Or use NCNN model (switch from browser) |
| No detections | Lower confidence: `--conf 0.2`. Check model path. |
| SMART never locks | Increase `--smart-radius` (e.g., 2.0) or decrease `--smart-min` (e.g., 3) |
| Browser shows black | Camera warming up (1-2 seconds), or camera not connected |
| Fake mode won't start | Ensure `RealVideo/DJI_0001_1456x1088_cropped_30fps.mp4` exists |

---

## Prerequisites

### On Raspberry Pi
- mavproxy running (for GPS):
  ```bash
  sudo /opt/mavlink/mavlink-venv/bin/mavproxy.py \
    --master=/dev/ttyAMA0 --baudrate=921600 --streamrate=10 \
    --out=udpout:127.0.0.1:14550 --out=tcpin:0.0.0.0:5762
  ```
- Camera connected (picamera2 + IMX296)
- `pienv` venv activated with requirements_pi.txt installed

### On Laptop (fake mode)
- `test_env` venv activated
- DJI video file in `RealVideo/`
- OpenCV + NumPy installed
