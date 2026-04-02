# passive_watch.py — Passive Camera Observer Blueprint

> MAP of passive_watch.py (1691 lines). Not a code copy — a navigation aid.
> Updated: 2026-04-02

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
| Globals for streaming | 52-65 | `latest_jpeg`, `latest_det_jpeg`, frame_lock, gps_lock, map/bullseye/smart JPEGs |
| Argument parsing | 67-85 | argparse: --port, --conf, --fps, --save-dir, --no-save, --no-mavlink, --fake, --simple-names, --class-filter, --smart-estimate |
| MODEL_TABLE + runtime_state | 87-103 | 4 model definitions (id/name/path/backend), runtime state dict + lock for browser control |
| parse_srt() | 106-135 | Parse DJI SRT telemetry file → dict frame_num → {lat, lon, alt, yaw} |
| HTML_PAGE | 139-310 | Inline HTML+CSS+JS. Model selector bar + 2-col grid + 3-col bottom. Polls `/api/status` every 2s, syncs controls |
| Handler (HTTP) | 313-485 | Routes: `/`, `/stream`, `/snapshot`, `/bullseye`, `/latest`, `/smart-grid`, `/map`, `/api/status`, `/api/switch-model`, `/api/set-conf`, `/api/set-class` |
| ThreadedServer | 488-489 | ThreadingMixIn + HTTPServer, daemon_threads=True |
| Stats dict | 491-505 | Global stats dict for `/api/status` (frames, detections, GPS, FOV, estimate, active_model, conf, class) |
| RollingFPS class | 333-342 | Rolling window FPS tracker (3s window). Instances: cam, vis, stream |
| FOV / calibration | 343-378 | `get_fov_info()` and `ground_coverage(alt_m)` — reads config sensor/focal values |
| DummyEstimator class | 381-465 | Accumulates observations, inverse-variance weighted GPS, centrality bonus |
| SmartEstimator class | 468-587 | Greedy tightest cluster: 10 central estimates within max_spread |
| render_latest_detection() | 590-624 | Thumbnail with pink line center→detection, crosshair, pixel+real distance, info bar |
| _snapshot_overlay() | ~1031-1097 | Capture resized detection snapshot as JPEG. Supports per-panel width (728 Latest, 1024 Best), GPS info bar (drone+dummy+offset), label badge |
| render_smart_grid() | 627-646 | 5x2 grid of locked smart frame thumbnails |
| render_map() | 649-703 | GPS estimates on satellite map.jpg with drone position + smart median |
| render_bullseye() | 706-830 | GPS scatter plot with bullseye rings, weighted mean, median, smart cluster |
| GPS state + COPTER_MODES | 833-845 | `gps_data` dict, mode int-to-name map |
| mavlink_reader() | 848-885 | Background thread: GLOBAL_POSITION_INT, GPS_RAW_INT, HEARTBEAT, ATTITUDE |
| draw_overlay() | ~1070-1230 | Detection box, **pink line center→detection + px/m distance**, crosshair, GPS bar, FPS bar, compass, FOV bar, **scale bar (1m)**, pink dot, dummy estimate |
| main() | ~1240-1691 | Entry point: fake mode SRT loading, IP detect, mavlink, camera+AI, HTTP server, model switch handler in loop |

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

| Method | Path | Returns |
|--------|------|---------|
| GET | `/` | HTML dashboard page (HTML_PAGE constant) |
| GET | `/stream` | MJPEG multipart stream (continuous push, 50ms sleep between frames) |
| GET | `/snapshot` | Latest detection frame JPEG (or latest stream frame if no detection) |
| GET | `/bullseye` | GPS bullseye scatter plot JPEG |
| GET | `/latest` | Latest detection thumbnail JPEG |
| GET | `/smart-grid` | 5x2 smart frames grid JPEG |
| GET | `/map` | Satellite map overlay JPEG |
| GET | `/api/status` | JSON stats dict (FPS, detections, GPS, estimate, FOV, active model, conf, class) |
| GET | `/api/switch-model?id=N` | Switch AI model (0-3). Blocks up to 3s for load. Returns `{ok, model, id}` |
| GET | `/api/set-conf?val=X` | Set confidence threshold (0.01-0.99). Returns `{ok, conf}` |
| GET | `/api/set-class?name=X` | Set class filter ("all", "dummy", "person"). Returns `{ok, class_filter}` |

Browser polls `/api/status` every 2000ms. Stream is continuous MJPEG push.
Control bar syncs model/conf/class from server state on each poll.

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
