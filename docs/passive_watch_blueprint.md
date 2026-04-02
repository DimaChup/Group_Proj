# passive_watch.py — Passive Camera Observer Blueprint

> MAP of passive_watch.py (2857 lines). Not a code copy — a navigation aid.
> Updated: 2026-04-02 (threaded inference refactor)

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
| Docstring + imports | 1-54 | Signal handler, headless DISPLAY check, cv2, numpy, config, VisionSystem |
| Globals for streaming | 55-77 | `latest_jpeg`, `latest_det_jpeg`, frame_lock, gps_lock, map/bullseye/smart JPEGs |
| Threaded inference globals | 78-88 | `_inference_frame`, `_inference_lock`, `_inference_eyes`, snapshot request flags, det/saved counters |
| Result mode globals | 90-95 | `_smart_result_saved`, `_survey_result_saved`, `SURVEY_TARGET`, `_result_banner` |
| Argument parsing | 97-115 | argparse: --port, --conf, --fps, --save-dir, --no-save, --no-mavlink, --fake, --simple-names, --class-filter, --smart-estimate |
| MODEL_TABLE + runtime_state | 117-133 | 4 model definitions (id/name/path/backend), runtime state dict + lock for browser control |
| parse_srt() | 136-170 | Parse DJI SRT telemetry file → dict frame_num → {lat, lon, alt, yaw} |
| HTML_PAGE | 172-444 | Inline HTML+CSS+JS. Model selector bar + 2-col grid + 3-col bottom. Polls `/api/status` every 2s, syncs controls |
| Handler (HTTP) | 447-850 | Routes: `/`, `/stream`, `/snapshot`, `/bullseye`, `/latest`, `/smart-grid`, `/map`, `/api/status`, `/api/switch-model`, `/api/set-conf`, `/api/set-class`, `/api/clear-all`, `/api/set-smart` |
| ThreadedServer | 852-853 | ThreadingMixIn + HTTPServer, daemon_threads=True |
| Stats dict | 856-863 | Global stats dict for `/api/status` |
| RollingFPS class | 866-888 | Rolling window FPS tracker (3s window). Instances: cam, vis, stream |
| FOV / calibration | 890-925 | `get_fov_info()` and `ground_coverage(alt_m)` |
| DummyEstimator class | 928-1012 | Accumulates observations, inverse-variance weighted GPS, centrality bonus |
| SmartEstimator class | 1015-1158 | Greedy tightest cluster: 10 central estimates within max_spread |
| _snapshot_overlay() | 1161-1235 | Capture resized detection snapshot as JPEG. GPS info bar, label badge |
| generate_result_image() | 1238-1300 | Final result image with banner, GPS, stats |
| compute_survey_analysis() | 1303-1417 | Analyze all GPS estimates, pick best coordinate + method |
| render_smart_grid() | 1419-1484 | 5x2 grid of locked smart frame thumbnails |
| render_map() | 1487-1542 | GPS estimates on satellite map.jpg with drone position + smart median |
| render_bullseye() | 1545-1945 | GPS scatter plot with bullseye rings, weighted mean, median, smart cluster (5 panels) |
| GPS state + COPTER_MODES | 1948-1957 | `gps_data` dict, mode int-to-name map |
| mavlink_reader() | 1960-1992 | Background thread: GLOBAL_POSITION_INT, GPS_RAW_INT, HEARTBEAT, ATTITUDE |
| draw_overlay() | 1995-2226 | Detection box, pink line, crosshair, GPS bar, FPS bar, compass, FOV bar, scale bar, pink dot, dummy estimate, result banner |
| **inference_worker()** | **2229-2514** | **NEW: Background thread — grabs latest frame, runs AI detection, updates GPS estimation, snapshots, smart estimator. All detection logic lives here.** |
| main() | 2516-2857 | Entry point: fake mode, mavlink, camera+AI, HTTP server, **starts inference thread**, display loop at ~30fps, model switch, overlay, JPEG encode, stats |

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

## Threading Architecture (refactored 2026-04-02)

```
Thread 1 (Display/Main — the while True loop in main()):
  - Read video frame (fake or camera) at ~30fps
  - Hand frame copy to inference thread via _inference_frame
  - Handle model switch requests
  - Read last_det from inference thread (tuple = atomic)
  - Update detection age (fade boxes over 2 seconds)
  - draw_overlay(frame, last_det) — uses latest detection
  - Capture snapshots when flagged by inference thread
  - JPEG encode → update latest_jpeg for stream
  - Periodic renders (bullseye, map, smart grid) every ~60 frames
  - Update stats, pace to ~30fps with sleep

Thread 2 (Inference — inference_worker(), daemon thread):
  - while True: grab frame from _inference_frame
  - Run detect_in_image(frame)
  - If detection passes conf + class filter:
    - Update _mod._last_det (tuple assignment = atomic)
    - Update draw_overlay attrs (_last_bw, _last_bh, _last_class)
    - GPS estimation (DummyEstimator + SmartEstimator)
    - Set _snap_request_latest / _snap_request_best flags
    - Save snapshots (JPG + JSON + CSV) — file I/O in inference thread
  - No sleep — runs as fast as inference allows

Thread 3 (Mavlink — mavlink_reader(), daemon thread):
  - Reads GLOBAL_POSITION_INT, GPS_RAW_INT, HEARTBEAT, ATTITUDE
  - Updates gps_data dict under gps_lock

Thread 4+ (HTTP — ThreadedServer, daemon threads):
  - Serves /stream, /snapshot, /api/status, etc.
```

## Shared State (thread safety)

| Variable | Writer | Reader | Safety |
|----------|--------|--------|--------|
| `_inference_frame` | Display | Inference | Protected by `_inference_lock` |
| `_mod._last_det` | Inference | Display | Tuple (immutable) = atomic ref assignment |
| `draw_overlay._last_bw/bh/class` | Inference | Display | Simple attribute = atomic |
| `_all_gps_estimates` | Inference | Display+HTTP | list.append() is GIL-safe |
| `_snap_request_latest/best` | Inference (set) | Display (clear) | Bool flag, one writer |
| `gps_data` | Mavlink | Inference+Display | Protected by `gps_lock` |
| `latest_jpeg` | Display | HTTP stream | Protected by `frame_lock` |
| `_inference_eyes` | Display (swap) | Inference (read) | Protected by `_inference_eyes_lock` |
| `smart_estimator` | Inference (write) | Display (read) | Only inference calls add(), display reads locked state |

## main() Flow (lines 2516-2857)

```
1. Auto-detect Pi IP                                   [2526-2534]
2. Print banner + config                               [2536-2548]
3. Fake mode: load video + SRT                         [2554-2573]
4. Connect to mavproxy (read-only, background thread)  [2576-2594]
5. Init VisionSystem (camera + AI model)               [2597-2624]
6. Start ThreadedServer on --port                      [2627-2633]
7. Open CSV log                                        [2638-2649]
8. Init shared state + start inference thread          [2651-2672]
9. Display loop (30fps, infinite):                     [2676-2847]
   a. Read frame (fake video or camera)
   b. Hand frame copy to inference thread
   c. Handle model switch requests
   d. Read last_det from inference thread
   e. Update detection age for fading overlay
   f. Periodic plot renders (~every 2s)
   g. draw_overlay(frame, last_det) — every frame
   h. Capture snapshots if flagged by inference
   i. Update smart grid if new data
   j. JPEG encode for stream (quality 70)
   k. Update stats dict
   l. Terminal output every 50 frames
   m. Sleep to pace at ~30fps
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
5. **Threaded inference** — display loop runs at ~30fps (smooth stream), inference runs in a background daemon thread at its own speed (~1.4fps laptop, ~4.8fps Pi). The `--fps` throttle is no longer used; inference runs as fast as the model allows.
6. **JPEG quality** — stream encoded at quality 70. Snapshots saved at higher quality (85-92).
7. **JSON sidecar** — every saved detection frame gets a `.json` file with structured metadata (drone position, FOV, estimate). Useful for post-flight analysis and retraining.
8. **CSV log** — appends to `detections/detection_log.csv` (not overwritten between runs). Header written only if file is empty.
9. **GPS estimate weighting** — inverse altitude squared (10m observation = 9x weight of 30m) plus centre-bonus (detections near frame centre get up to 5x boost).
10. **Port conflict** — uses port 8090 by default, same as `pi_flight.py` and `capture_training.py` (8091). Don't run simultaneously without changing `--port`.
11. **Thread safety** — last_det is a tuple (immutable, atomic ref assignment). Frame handoff uses `_inference_lock`. GPS data uses `gps_lock`. Model swap uses `_inference_eyes_lock`. Snapshot requests use bool flags (one writer, one reader).
