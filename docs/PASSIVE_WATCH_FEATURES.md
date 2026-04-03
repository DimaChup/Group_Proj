# passive_watch.py Feature Verification Checklist

> Regression checklist for `field_tools/passive_watch.py` (3031 lines).
> Before any change, verify affected features still work.
> Mark status: VERIFIED / UNTESTED / BROKEN (with date + notes).
>
> Source: `field_tools/passive_watch.py`
> Blueprint: `docs/passive_watch_blueprint.md`

---

## Detection & AI

| # | Feature | CLI / Browser | Status | Notes |
|---|---------|---------------|--------|-------|
| D1 | TFLite backend (default) | `--model best.tflite` | UNTESTED | Default backend on Pi (ai-edge-litert). MODEL_TABLE id=0,1,3 |
| D2 | NCNN backend | Browser model selector id=2 | UNTESTED | MODEL_TABLE id=2: SAR v2 NCNN. Requires `pip install ncnn` |
| D3 | Ultralytics backend (laptop auto) | Automatic on laptop | UNTESTED | VisionSystem auto-selects Ultralytics when available |
| D4 | Model switching via browser | Browser dropdown + `/api/switch-model?id=N` | UNTESTED | 4 models in MODEL_TABLE (Original, SAR v2 TFL, SAR v2 NCNN, COCO Person). Blocks up to 3s for load |
| D5 | Model selection via CLI | `--model <path>` | UNTESTED | Auto-matches path to MODEL_TABLE entry; defaults to id=0 if no match |
| D6 | Confidence threshold (CLI) | `--conf 0.4` (default) | UNTESTED | Passed to VisionSystem at init |
| D7 | Confidence threshold (browser) | Slider + `/api/set-conf?val=X` | UNTESTED | Range 0.01-0.99. Updates `runtime_state["conf_threshold"]` |
| D8 | Class filter (CLI) | `--class-filter person` | UNTESTED | Only saves detections matching class name |
| D9 | Class filter (browser) | Dropdown + `/api/set-class?name=X` | UNTESTED | Options: all, dummy, person. Resets best/latest detection on change |
| D10 | Detection box overlay (green, fading) | Automatic | UNTESTED | Green box persists for 2s with alpha fade-out between inference frames |
| D11 | Raw detection markers (gray, all classes) | Automatic | UNTESTED | Dim gray markers for detections rejected by class filter. Fades after 0.5s |
| D12 | Threaded inference (background) | Automatic | UNTESTED | Inference runs in daemon thread at model speed; display loop at ~30fps |

## GPS Estimation

| # | Feature | CLI / Browser | Status | Notes |
|---|---------|---------------|--------|-------|
| G1 | DummyEstimator (inverse-variance weighted) | Always active | UNTESTED | Inverse altitude^2 weighting + centre-bonus (4x for frame-centre detections) |
| G2 | SmartEstimator (tightest cluster lock) | `--smart-estimate` | UNTESTED | Greedy cluster: `--smart-min` central estimates within `--smart-radius` metres |
| G3 | Smart params via CLI | `--smart-min 5 --smart-radius 1.0` | UNTESTED | Min samples and max spread for SMART cluster lock |
| G4 | Smart params via browser | Input fields + `/api/set-smart?spread=X&count=Y` | UNTESTED | Live update of spread and count thresholds |
| G5 | GPS estimate overlay on stream | Automatic (with mavlink) | UNTESTED | Bottom bar: "DUMMY EST: lat, lon (N obs)" |
| G6 | Bullseye scatter plot | `/bullseye` endpoint in browser | UNTESTED | 5-panel GPS scatter with bullseye rings, weighted mean, median, smart cluster |
| G7 | Bullseye map background | Default ON (`bullseye_map_bg`) | UNTESTED | Satellite map.jpg crop behind bullseye scatter plots |
| G8 | Map overlay with estimates | `/map` endpoint in browser | UNTESTED | All GPS estimates plotted on satellite map.jpg with drone position + smart median |
| G9 | Ground truth marker | Hardcoded `_ground_truth` + `/api/set-ground-truth` | UNTESTED | Set via API: `?lat=X&lon=Y`. Clear via `/api/clear-ground-truth`. Shown on bullseye/map |
| G10 | Survey analysis (auto at N estimates) | SURVEY_TARGET = 100 | UNTESTED | After 100 estimates, runs `compute_survey_analysis()` and saves result image |

## Output & Saving

| # | Feature | CLI / Browser | Status | Notes |
|---|---------|---------------|--------|-------|
| O1 | Detection snapshot JPG | Automatic (unless `--no-save`) | UNTESTED | Saved to `<save-dir>/det_NNNN_conf_lat_lon.jpg` |
| O2 | JSON sidecar per detection | Automatic (unless `--no-save` or `--simple-names`) | UNTESTED | Same filename `.json` with structured metadata (drone pos, FOV, estimate) |
| O3 | CSV detection log | Automatic (unless `--no-save`) | UNTESTED | Appends to `<save-dir>/detection_log.csv`. Header written only if empty |
| O4 | Simple filenames mode | `--simple-names` | UNTESTED | Clean filenames (no det_ prefix), no JSON sidecars, estimated GPS in filename |
| O5 | SMART result image | `--smart-estimate` | UNTESTED | Saved on each SMART lock: frame + banner + GPS coordinate. Uses `lock_id` counter |
| O6 | SMART result directory | `--smart-dir <path>` | UNTESTED | Default: `<save-dir>/smart_detections/`. Separate from regular detections |
| O7 | Custom save directory | `--save-dir <path>` | UNTESTED | Default: `detections/`. Created automatically if missing |
| O8 | No-save mode (stream only) | `--no-save` | UNTESTED | Disables all snapshot saving; stream + overlay still work |
| O9 | Async file I/O queue | Automatic | UNTESTED | Dedicated `_save_worker` thread. Queue maxsize=50, drops oldest if full |
| O10 | Survey result image | Automatic at SURVEY_TARGET | UNTESTED | `generate_result_image()` with "SURVEY COMPLETE" banner after 100 estimates |
| O11 | Best (most central) detection tracking | Automatic | UNTESTED | Tracks `_best_center_dist`, saves best detection JPEG + GPS info |

## Stream & UI (Browser Dashboard)

| # | Feature | Endpoint / Control | Status | Notes |
|---|---------|-------------------|--------|-------|
| S1 | MJPEG stream | `GET /stream` | UNTESTED | Continuous multipart push, 50ms sleep between frames, quality 70 |
| S2 | Browser dashboard (HTML page) | `GET /` | UNTESTED | Inline HTML+CSS+JS. Model selector bar + 2-col grid + 3-col bottom |
| S3 | Status polling | `GET /api/status` (every 2s) | UNTESTED | JSON: FPS, detections, GPS, estimate, FOV, active model, conf, class, ground_truth |
| S4 | Model selector dropdown | Browser + `/api/switch-model` | UNTESTED | Syncs with server state on each poll |
| S5 | Confidence slider | Browser + `/api/set-conf` | UNTESTED | Syncs with server state on each poll |
| S6 | Class filter dropdown | Browser + `/api/set-class` | UNTESTED | Syncs with server state on each poll |
| S7 | Smart params inputs | Browser + `/api/set-smart` | UNTESTED | Spread + count input fields |
| S8 | Latest detection thumbnail | `GET /latest` | UNTESTED | Most recent detection frame JPEG |
| S9 | Best detection thumbnail | `GET /snapshot` | UNTESTED | Best (most central) detection frame JPEG |
| S10 | Smart grid (5x2 thumbnails) | `GET /smart-grid` | UNTESTED | 5x2 grid of locked smart frame thumbnails with overlays |
| S11 | CLI flags reflected in browser defaults | Automatic | UNTESTED | `--conf`, `--class-filter`, `--smart-min`, `--smart-radius` set initial browser values |
| S12 | No-stream mode | `--no-stream` | UNTESTED | Disables HTTP server entirely (terminal output only) |

## Overlay Elements (on stream)

| # | Feature | Trigger | Status | Notes |
|---|---------|---------|--------|-------|
| V1 | FPS bars (CAM / VIS / STR) | Always | UNTESTED | Top bar with rolling 3s window FPS for camera, vision, stream |
| V2 | Compass rose with heading arrow | With mavlink (yaw data) | UNTESTED | Top-right compass with heading arrow |
| V3 | Attitude display (yaw/pitch/roll) | With mavlink | UNTESTED | Top bar: Y:yaw P:pitch R:roll MODE |
| V4 | GPS bar (lat, lon, alt, sats) | With mavlink | UNTESTED | Bottom bar with drone GPS coordinates |
| V5 | FOV bar (degrees, ground coverage) | Always | UNTESTED | FOV deg, ground WxH at altitude, calibrated 1m values |
| V6 | Scale bar (ground width reference) | With altitude | UNTESTED | Shows ground width visible at current altitude |
| V7 | Crosshair (frame centre) | Always | UNTESTED | Centre crosshair marker |
| V8 | Pink dot on detection centre | On detection | UNTESTED | Pink dot at detection centre pixel |
| V9 | Dummy estimate coordinate | On GPS estimate | UNTESTED | "DUMMY EST: lat, lon (N obs)" bar |
| V10 | Result banner (SMART/SURVEY) | On lock/completion | UNTESTED | Temporary banner showing result event |
| V11 | FRONT label | Always | UNTESTED | Indicates camera forward direction |

## Modes

| # | Feature | How to activate | Status | Notes |
|---|---------|----------------|--------|-------|
| M1 | Real camera (Pi) | Default on Pi (no `--fake`) | UNTESTED | Uses VisionSystem with camera_index=0 (Pi) or None (fake) |
| M2 | Fake mode (DJI video replay) | `--fake` | UNTESTED | Replays `--fake-video` + `--fake-srt` for GPS. No camera/mavproxy needed |
| M3 | Fake video/SRT paths | `--fake-video <path> --fake-srt <path>` | UNTESTED | Defaults: `RealVideo/DJI_0001_1456x1088_cropped_30fps.mp4` + matching SRT |
| M4 | No-mavlink mode | `--no-mavlink` | UNTESTED | Skips mavproxy connection. No GPS overlay, no geotagging. Stream + AI still work |
| M5 | Headless (no cv2.imshow) | Automatic when no DISPLAY | UNTESTED | Removes QT_QPA_PLATFORM env var. No cv2 windows at all (pure stream + terminal) |
| M6 | No-stream mode | `--no-stream` | UNTESTED | Disables HTTP server. Terminal output only |

## Controls

| # | Feature | How | Status | Notes |
|---|---------|-----|--------|-------|
| C1 | Terminal 'C' key = Clear All | Press C in terminal | UNTESTED | Resets SMART estimator, DummyEstimator, best detection, all GPS estimates |
| C2 | Browser Clear All button | Click button | UNTESTED | Calls `/api/clear-all`. Same effect as terminal C key |
| C3 | Browser Reset Best button | Click button | UNTESTED | Calls `/api/reset-best`. Resets best detection only (keeps estimates) |
| C4 | Set ground truth (browser) | `/api/set-ground-truth?lat=X&lon=Y` | UNTESTED | Sets ground truth marker for bullseye/map accuracy reference |
| C5 | Clear ground truth (browser) | `/api/clear-ground-truth` | UNTESTED | Removes ground truth marker |

## Threading & Safety

| # | Feature | Status | Notes |
|---|---------|--------|-------|
| T1 | ZERO commands to drone | UNTESTED | mavlink connection is udpin (read-only). No arm, no mode, no waypoints |
| T2 | Thread-safe model switching | UNTESTED | `_inference_eyes_lock` protects VisionSystem swap. Inference thread pauses during switch |
| T3 | Thread-safe frame handoff | UNTESTED | `_inference_lock` protects `_inference_frame` between display and inference threads |
| T4 | Thread-safe GPS data | UNTESTED | `gps_lock` protects `gps_data` dict between mavlink and display/inference threads |
| T5 | Atomic last_det (tuple ref) | UNTESTED | Tuple is immutable; Python ref assignment is GIL-safe |
| T6 | Snapshot request flags (bool) | UNTESTED | One writer (inference), one reader (display). No lock needed |
| T7 | Async save queue (non-blocking) | UNTESTED | `_save_queue` maxsize=50, drops oldest if full. Dedicated `_save_worker` thread |

---

## Full CLI Reference

```
python field_tools/passive_watch.py [OPTIONS]

--port 8090             HTTP server port
--conf 0.4              Confidence threshold
--fps 5                 Max inference FPS (legacy, inference now runs at model speed)
--save-dir detections   Snapshot output directory
--no-save               Disable snapshot saving
--no-mavlink            Skip mavproxy connection
--model best.tflite     TFLite model path
--simple-names          Clean filenames, no JSON sidecars
--class-filter <name>   Only save detections of this class (e.g. "person")
--smart-estimate        Enable SMART cluster estimator
--smart-min 5           Min central detections before SMART lock
--smart-radius 1.0      Max spread for SMART cluster (metres)
--smart-dir <path>      Directory for SMART result images
--fake                  Replay DJI video instead of camera
--fake-video <path>     Video file for fake mode
--fake-srt <path>       SRT telemetry file for fake mode
--no-stream             Disable HTTP stream server
```

## HTTP Endpoints Reference

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/` | Browser dashboard (HTML page) |
| GET | `/stream` | MJPEG multipart stream |
| GET | `/snapshot` | Best detection frame JPEG |
| GET | `/latest` | Latest detection thumbnail JPEG |
| GET | `/bullseye` | GPS bullseye scatter plot JPEG |
| GET | `/smart-grid` | 5x2 smart frames grid JPEG |
| GET | `/map` | Satellite map overlay JPEG |
| GET | `/api/status` | JSON stats (polled every 2s by browser) |
| GET | `/api/switch-model?id=N` | Switch AI model (0-3) |
| GET | `/api/set-conf?val=X` | Set confidence threshold |
| GET | `/api/set-class?name=X` | Set class filter |
| GET | `/api/set-smart?spread=X&count=Y` | Update SMART cluster params |
| GET | `/api/clear-all` | Reset all estimators + detections |
| GET | `/api/reset-best` | Reset best detection only |
| GET | `/api/set-ground-truth?lat=X&lon=Y` | Set ground truth position |
| GET | `/api/clear-ground-truth` | Remove ground truth marker |

---

*Last updated: 2026-04-03. All features UNTESTED -- run through checklist before next code change.*
