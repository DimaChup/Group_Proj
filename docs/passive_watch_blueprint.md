# passive_watch.py — Passive Camera Observer Blueprint

> MAP of passive_watch.py (752 lines). Not a code copy — a navigation aid.
> Updated: 2026-03-11

## Purpose

Passive camera observer with web MJPEG stream, AI detection overlay, auto-saved
detection snapshots (JPG + JSON sidecar), CSV log, and GPS position estimation.
Sends **ZERO commands** to the drone — safe to run anytime during manual RC flight.
Optionally reads telemetry from mavproxy (read-only) for GPS geotagging.

## How to Run

```bash
# On Pi via SSH:
cd ~/dima/Group_Proj && source pienv/bin/activate
DISPLAY= python passive_watch.py

# On laptop (simulation):
python passive_watch.py --no-mavlink

# With options:
python passive_watch.py --port 8090 --conf 0.3 --fps 10 --save-dir my_detections
python passive_watch.py --no-save --no-mavlink
```

## CLI Flags

| Flag | Default | Purpose |
|------|---------|---------|
| `--port` | 8090 | HTTP server port |
| `--conf` | 0.4 | Confidence threshold for detection |
| `--fps` | 5 | Max inference FPS (throttle) |
| `--save-dir` | `detections/` | Directory for snapshot JPGs + JSON + CSV |
| `--no-save` | off | Disable snapshot saving (stream only) |
| `--no-mavlink` | off | Skip mavproxy connection (no GPS overlay) |

## Section Map

| Section | Lines | Purpose |
|---------|-------|---------|
| Docstring + imports | 1-51 | Signal handler, headless DISPLAY check, cv2, numpy, config, VisionSystem |
| Globals for streaming | 52-55 | `latest_jpeg`, `latest_det_jpeg`, `frame_lock` (threading.Lock) |
| Argument parsing | 57-65 | argparse: --port, --conf, --fps, --save-dir, --no-save, --no-mavlink |
| HTML_PAGE | 68-102 | Inline HTML+CSS+JS for browser dashboard. Polls `/api/status` every 1s |
| Handler (HTTP) | 106-155 | BaseHTTPRequestHandler: routes `/`, `/stream`, `/snapshot`, `/api/status` |
| ThreadedServer | 158-159 | ThreadingMixIn + HTTPServer, daemon_threads=True |
| Stats dict | 162-169 | Global stats dict returned by `/api/status` (frames, detections, GPS, FOV, estimate) |
| RollingFPS class | 172-194 | Rolling window FPS tracker (3s window). Instances: cam, vis, stream |
| FOV / calibration | 196-231 | `get_fov_info()` and `ground_coverage(alt_m)` — reads config sensor/focal values |
| DummyEstimator class | 235-320 | Accumulates detection observations, inverse-variance weighted GPS estimate |
| GPS state + COPTER_MODES | 323-332 | `gps_data` dict (lat, lon, alt, sats, yaw, mode), mode int-to-name map |
| mavlink_reader() | 335-363 | Background thread: reads GLOBAL_POSITION_INT, GPS_RAW_INT, HEARTBEAT, ATTITUDE |
| draw_overlay() | 366-490 | Renders detection box, crosshair, GPS bar, FPS bar, compass rose, FOV bar, dummy estimate bar |
| main() | 494-752 | Entry point: IP detect, mavlink connect, camera+AI init, HTTP server start, camera loop |

## Key Classes

### RollingFPS (lines 172-194)
- `tick()` — record a timestamp
- `fps()` — return FPS over rolling 3s window
- Three global instances: `cam_fps_tracker`, `vis_fps_tracker`, `stream_fps_tracker`

### DummyEstimator (lines 235-320)
- `add_observation(drone_lat, drone_lon, alt_m, yaw_deg, det_x, det_y)` — pixel-to-GPS projection, inverse-variance weighted (1/alt^2), centre-bonus (4x for detections near frame centre)
- `get_estimate()` — returns `(lat, lon, n_observations)` or None
- `reset()` — clear all observations
- Global instance: `dummy_estimator` (line 320)

### Handler (lines 106-155)
- HTTP request handler, `log_message` suppressed (silent)
- Routes: see HTTP Endpoints table below

### ThreadedServer (lines 158-159)
- ThreadingMixIn wrapper for concurrent stream + API requests

## HTTP Endpoints

| Method | Path | Lines | Returns |
|--------|------|-------|---------|
| GET | `/` | 111-115 | HTML dashboard page (HTML_PAGE constant) |
| GET | `/stream` | 117-132 | MJPEG multipart stream (continuous push, 50ms sleep between frames) |
| GET | `/snapshot` | 134-144 | Latest detection frame JPEG (or latest stream frame if no detection) |
| GET | `/api/status` | 146-151 | JSON stats dict (FPS, detections, GPS, estimate, FOV) |

Browser polls `/api/status` every 1000ms. Stream is continuous MJPEG push.

## Key Data Structures

### stats (line 163)
```python
{
    "frames", "detections", "det_pct", "saved",
    "cam_fps", "vis_fps", "stream_fps",
    "gps_lat", "gps_lon", "alt", "sats", "flight_mode",
    "est_lat", "est_lon", "est_obs",
    "fov_deg", "cal_1m_w", "cal_1m_h"
}
```

### gps_data (line 324)
```python
{
    "lat", "lon", "alt", "sats", "fix",
    "yaw", "pitch", "roll", "mode"
}
```
Updated by `mavlink_reader()` background thread. Read-only from mavproxy.

### Detection snapshot output (per detection)
- **JPG**: `detections/det_NNNN_conf_lat_lon.jpg` — frame with overlay + GPS stamp
- **JSON sidecar**: same name `.json` — structured metadata (detection, drone, FOV, estimate)
- **CSV row**: appended to `detections/detection_log.csv`

## main() Flow (lines 494-752)

```
1. Auto-detect Pi IP (hostname -I)                    [498-505]
2. Print banner + config                               [507-523]
3. Connect to mavproxy (read-only, background thread)  [526-544]
4. Init VisionSystem (camera + AI model)               [547-550]
5. Start ThreadedServer on --port                      [553-556]
6. Open CSV log                                        [558-568]
7. Camera loop (infinite):                             [582-748]
   a. Get frame from VisionSystem
   b. Throttle inference to --fps
   c. If detection >= --conf:
      - Update DummyEstimator with GPS projection
      - Save snapshot JPG + JSON sidecar (unless --no-save)
      - Append CSV row
   d. Update detection age for fading overlay
   e. Draw overlay (detection box, GPS, compass, FOV, estimate)
   f. Encode JPEG for stream (quality 70)
   g. Update stats dict
   h. Print terminal summary every 50 frames
```

## draw_overlay() Layout (lines 366-490)

```
+--[ Top bar: CAM:fps VIS:fps STR:fps | Y:yaw P:pitch R:roll MODE ]--+
|                                                   [Compass rose]     |
|                                                   with heading       |
|                     FRONT label                    arrow             |
|                                                                      |
|              +------+                                                |
|              | DET  |  ← green box (fades over 2s)                  |
|              | conf |                                                |
|              +------+                                                |
|                   +                                                  |
|                crosshair                                  Xm height  |
|                                                                      |
|                          <-- X.Xm -->  (ground width at alt)         |
|                                                                      |
+--[ DUMMY EST: lat, lon (N obs) ]------------------------------------+
+--[ FOV: deg | Ground: WxH m @alt | Cal@1m: WxH cm ]----------------+
+--[ GPS: lat, lon | Alt: Xm | Sats: N ]-----------------------------+
```

## Important Notes / Gotchas

1. **ZERO commands** — mavlink connection is udpin (read-only). No arm, no mode change, no waypoints. Safe always.
2. **Headless mode** — if no `DISPLAY` env var, removes `QT_QPA_PLATFORM` to prevent cv2 crash on Pi via SSH.
3. **Camera BGR** — VisionSystem returns BGR frames directly. No cvtColor conversion (IMX296 outputs BGR despite RGB888 label).
4. **Detection box persistence** — last detection box stays visible for 2 seconds with fade-out (alpha decay), so pilot can see where detection was even between inference frames.
5. **Inference throttle** — detection only runs every `1/fps` seconds. Camera captures every frame for smooth stream, but AI runs at throttled rate.
6. **JPEG quality** — stream encoded at quality 70 (line 710). Snapshots saved at default quality (higher).
7. **JSON sidecar** — every saved detection frame gets a `.json` file with structured metadata (drone position, FOV, estimate). Useful for post-flight analysis and retraining.
8. **CSV log** — appends to `detections/detection_log.csv` (not overwritten between runs). Header written only if file is empty.
9. **GPS estimate weighting** — inverse altitude squared (10m observation = 9x weight of 30m) plus centre-bonus (detections near frame centre get up to 5x boost).
10. **Port conflict** — uses port 8090 by default, same as `pi_flight.py` and `capture_training.py` (8091). Don't run simultaneously without changing `--port`.
