# Project Map — What's Where

Quick reference for navigating the SAR Drone codebase.

---

## Root Directory — Core Scripts

| File | What it does |
|---|---|
| `main.py` | Full autonomous mission (state machine, search, detect, land) |
| `pi_flight.py` | Web ground station (browser dashboard + commands) port 8090 |
| `passive_watch.py` | Passive observer (stream + AI detection + GPS estimation, ZERO commands) port 8090 |
| `capture_training.py` | Record photos + video for model retraining (ZERO commands) port 8091 |
| `simple_simulator.py` | Interactive simulator (keyboard flight + CV + GPS estimation, laptop only) |
| `simulation.py` | Laptop simulation (map.jpg + simulated drone camera view) |
| `preflight.py` | Standalone connectivity checker (camera, Cube, AI model) |
| `config.py` | ALL settings (altitudes, speeds, camera, connection, auto-detects hardware) |
| `states.py` | State enum (20 states: INIT through DONE) |
| `vision.py` | Camera + AI detection (dual backend: Ultralytics on laptop, TFLite on Pi) |
| `planning.py` | Lawnmower/spiral search pattern generator |
| `utils.py` | Geo math (GPS <-> pixel conversion, GeoTransformer) |
| `CLAUDE.md` | Project ground truth for LLM sessions (must stay in root) |
| `best.tflite` | Active AI model (all scripts read this file) |

---

## `assets/` — Static Resources

| File | What |
|---|---|
| `map.jpg` | Satellite image for simulation (~12MB) |
| `dummy.png` | Dummy/casualty image for dataset generation + bench testing |

---

## `flight_plans/` — Mission Geometry

| File | What |
|---|---|
| `AENGM0074.kml` | KML from university — survey area, flight boundary, SSSI no-fly zone, takeoff point |
| `search_area.json` | Search polygon (drawn on laptop with `draw_search_area.py`) |
| `waypoints.json` | Pre-planned waypoints (drawn on laptop with `draw_waypoints.py`) |
| `transit.json` | Transit path to search area (drawn on laptop with `draw_transit.py`) |
| `draw_search_area.py` | Draw search polygon on map -> JSON |
| `draw_waypoints.py` | Draw waypoints on map -> JSON |
| `draw_transit.py` | Draw transit path on map -> JSON |

**Workflow:** Run draw scripts on laptop, push JSON to GitHub, pull on Pi.

---

## `cv_models/` — All AI Models

### Top-level models (standalone .tflite files)

| File | Size | What |
|---|---|---|
| `custom_yolov8n.tflite` | 3.2MB | Original custom dummy detector (baseline) |
| `human.tflite` | 12.2MB | COCO YOLOv8n person detector (80 classes, backup) |
| `best2.tflite` | 3.2MB | Placeholder copy |
| `original_best.tflite` | 3.2MB | Copy of the original best.tflite for reference |

### Trained model variants (subdirectories)

| Directory | What |
|---|---|
| `sar_v2_1088/best.tflite` | **BEST** — 11.7MB, retrained on real+synthetic 1088 data (mAP50=0.995) |
| `sar_v2_1088/best.pt` | Full YOLO weights for future fine-tuning |
| `sar_v2_1088/ncnn/` | NCNN export (untested on Pi) |
| `sar_640/best.tflite` | Earlier training at 640x640 (+ .onnx, .pt, results.png, confusion_matrix.png) |
| `sar_640/ncnn/` | NCNN export for 640 model |
| `sar_1280/best.tflite` | Earlier training at 1280x1280 (+ .onnx, .pt, results.png, confusion_matrix.png) |
| `sar_1280/ncnn/` | NCNN export for 1280 model |

**To swap model on Pi:** `cp cv_models/sar_v2_1088/best.tflite best.tflite`
**Or use flag:** `python main.py --model cv_models/sar_v2_1088/best.tflite`

---

## `training/` — Dataset Generation & Labelling

| File | What |
|---|---|
| `generate_dataset_v2.py` | Create synthetic + negative training images at 1456x1088 |
| `label_tool.py` | Label real video frames for training (`--full` for native resolution) |
| `dataset_v2/` | 366 images: 300 synthetic + 16 real + 50 negatives at 1456x1088 |
| `dataset_v2/dataset.yaml` | YOLO data config (1 class: dummy) |
| `dataset_v2/images/` | syn_*.jpg, real_*.jpg, neg_*.jpg |
| `dataset_v2/labels/` | Matching .txt YOLO labels (neg labels are empty) |
| `dataset_v2/preview_50m/` | Preview frames from DJI video at ~50m altitude |
| `dataset_v2.zip` | Zipped dataset ready for Colab upload |

See `docs/TRAINING_GUIDE.md` for the full Colab workflow.

---

## `tests/` — All Test Scripts

### `tests/hardware/` — Does This Part Work?

| Script | What |
|---|---|
| `benchmark.py` | Inference speed (50 runs, timing report) |
| `benchmark_full.py` | Comprehensive: system info, all models, threading |
| `cv_benchmark.py` | Detection rate, speed, blur simulation |
| `buzzer_test.py` | Buzzer melody test via MAVLink |
| `gps_test.py` | GPS diagnostics with fix tracking |
| `gps_health.py` | Step-by-step GPS verification |
| `detection_snapshot_test.py` | Single-frame detection on static image |

### `tests/flight/` — Can It Fly? (numbered by progression)

| Script | What | Risk |
|---|---|---|
| `0a_cube_commands.py` | Bench: test individual commands (mode, arm) | None |
| `0b_bench_mission.py` | Bench: full command sequence (no props) | None |
| `0c_feedback_test.py` | Bench: vision->GPS pipeline (no commands) | None |
| `1_passive_flight.py` | Manual RC, CV watches (ZERO commands) | None |
| `2_waypoints.py` | Fly GPS waypoints (no CV) | **FLIES** |
| `3_auto_detect.py` | AUTO + AI -> GUIDED hover | **FLIES** |
| `4_detect_and_center.py` | Autonomous pattern + center | **FLIES** |
| `5_two_waypoints.py` | Simple 2-waypoint test | **FLIES** |
| `live_map.py` | Real-time drone position on map | None |

### `tests/diagnostics/` — Is It Working?

| Script | What |
|---|---|
| `diagnostics.py` | Multi-view dashboard (camera, telemetry, GPS, battery). Press A=AI, M=swap model |
| `cube_monitor.py` | Live Cube telemetry dashboard |
| `camera_stream.py` | MJPEG stream to ground station |
| `camera_stream_fast.py` | Threaded MJPEG stream |
| `camera_stream_h264.py` | H.264/HLS stream (needs FFmpeg) |

### `tests/calibration/` — Are The Numbers Right?

| Script | What |
|---|---|
| `fov_calibrate.py` | Bench FOV calibration with ruler |
| `fov_test_simple.py` | Simple single-measurement FOV |
| `alt_test.py` | FOV at real altitude |
| `lens_calibrate.py` | Lens distortion calibration (checkerboard) |
| `gps_ground_truth.py` | GPS ground truth (CV estimate vs actual) |

### `tests/day_1_experiments/` — Structured Data Collection (CSV output)

| Script | What |
|---|---|
| `altitude_sweep.py` | Detection rate vs altitude (10-30m buckets) |
| `speed_sweep.py` | Detection rate vs speed + blur metric |
| `gps_accuracy.py` | GPS estimate error vs known dummy position |
| `gps_drift.py` | GPS noise floor (CEP50, CEP95) |
| `model_compare.py` | Benchmark ALL .tflite models side by side |
| `detection_log.py` | General catch-all flight logger |

### `tests/laptop/` — Development Only

| Script | What |
|---|---|
| `test_camera.py` | Camera preview + snapshot |
| `test_cv.py` | AI model loading + detection test |
| `test_cube.py` | Cube heartbeat, GPS, attitude, battery |
| `test_all.py` | Full system connectivity check |
| `test_tflite.py` | TFLite inference on laptop |
| `debug_tflite.py` | Raw TFLite model output inspection |
| `cv_test_synthetic.py` | Synthetic image CV benchmark |
| `video_test.py` | DJI video replay + detection + GPS + scale bar |
| `video_test_compare.py` | A/B model comparison on video (M key switches) |
| `visualize_paths.py` | Flight path visualization |
| `zoom_detect.py` | Zoom-based detection test |
| `video_tools/` | Helper modules (detect_fullres, detect_tiling, video_tiling, baselines) |

---

## `tools/` — Standalone Utilities

| Script | What |
|---|---|
| `fov_calibrate_video.py` | FOV calibration from video (click dummy at altitudes) |
| `lawnmower_visual.py` | Visualize lawnmower pattern |

---

## `requirements/` — Dependencies

| File | Platform |
|---|---|
| `requirements_dev.txt` | Windows laptop (full pip freeze) |
| `requirements_linux.txt` | WSL/Linux laptop |
| `requirements_pi.txt` | Raspberry Pi (4 packages only) |
| `requirements_test_env.txt` | Test environment (Ultralytics + TFLite) |
| `requirements_venv.txt` | Venv freeze |

---

## `docker/` — Containerized Testing

| File | What |
|---|---|
| `Dockerfile.pi-test` | Docker-based Pi environment test (TFLite model loads on slim Linux) |

---

## `docs/` — Documentation

### Project Documentation

| Doc | What |
|---|---|
| `PROJECT_MAP.md` | **THIS FILE** — what's where |
| `ARCHITECTURE.md` | System overview, hardware checklist |
| `DESIGN_DECISIONS.md` | Why each technical choice was made (DD-01 to DD-09) |
| `LAUNCH_GUIDE.md` | How to run main.py (all flags, all modes) |
| `TEST_LAUNCH_GUIDE.md` | Copy-paste commands for all test scripts |
| `TEST_GUIDE.md` | All 41+ test scripts: what, when, why |
| `DEPENDENCIES.md` | Script dependency graph, platform matrix |
| `SAR_COMPARISON.md` | Industry/academic comparison for report |

### Flight Day

| Doc | What |
|---|---|
| `FLIGHT_DAY_CHECKLIST.md` | Printable checklist (follow top to bottom) |
| `FLIGHT_DAY_LOG.md` | Flight day notes and results |
| `FIELD_QUICK_REF.md` | Copy-paste commands for field (no internet) |

### Setup & Guides

| Doc | What |
|---|---|
| `PI_SETUP.md` | Step-by-step Pi setup |
| `CV_GUIDE.md` | Vision system, model swapping |
| `TRAINING_GUIDE.md` | Model retraining workflow (Colab) |
| `VIDEO_ANALYSIS.md` | DJI video analysis tools, FOV calibration |
| `CONNECTIVITY.md` | Connection debugging |
| `SIMULATOR_GUIDE.md` | Simulator user guide |

### Planning & Status

| Doc | What |
|---|---|
| `NICE_TO_HAVE.md` | Improvement backlog (impact/effort scored) |
| `IMPROVEMENTS.md` | Ranked improvements with stepping stones |
| `GROUP_STATUS.md` | Group project status |
| `TEAM_PLAN.md` | Team workstreams |

### Reference

| Doc | What |
|---|---|
| `AENGM0074-project-brief.pdf` | University project brief |
| `MASTER_BLUEPRINT.md` | All files combined overview |
| `SESSION_ARCHIVE.md` | Archived session logs |

### Blueprints (read BEFORE source files >500 lines)

| Doc | For |
|---|---|
| `main_blueprint.md` | main.py line-range map |
| `simple_simulator_blueprint.md` | simple_simulator.py line-range map |
| `pi_flight_blueprint.md` | pi_flight.py line-range map |
| `passive_watch_blueprint.md` | passive_watch.py line-range map |

---

## `RealVideo/` — DJI Flight Recordings

**Use 30fps video only** (`DJI_0001_1456x1088_cropped_30fps.mp4`) — 6fps versions are OUT OF SYNC with SRT telemetry.

Contains original 4K videos, cropped/resized variants, SRT telemetry files, and detection CSV outputs.

---

## `detections/` — Saved Detection Photos

Auto-saved by `passive_watch.py` during flights. Filenames encode timestamp, GPS coordinates, and confidence: `YYYYMMDD_HHMMSS_lat_lon_conf.jpg`.

---

## `logs/` — Runtime Logs

| File | What |
|---|---|
| `flight_log.csv` | Runtime log (regenerated each run, gitignored) |

---

## `dashboard/` — React Web App

Project tracker + SE visualization. Standalone from drone code.
`cd dashboard && npm install && npm run dev` -> http://localhost:5050
See `dashboard/CLAUDE.md` for details.

---

## `.claude/` — Claude Workflow

| File | What |
|---|---|
| `brain-dump.md` | Append-only user ideas capture |
| `commands/status.md` | Slash command: project status |
| `commands/wrap-up.md` | Slash command: session wrap-up checklist |
| `commands/doc-health.md` | Slash command: documentation health check |
| `rules/blueprint-maintenance.md` | Auto-loaded rule: when/how to update blueprints |
| `rules/session-workflow.md` | Auto-loaded rule: start/during/end session checklist |

---

## `_archive/` — Old/Junk Files

Gitignored. Safe to delete. Contains old scripts, unused model exports, test artifacts.

---

## Quick Reference

```bash
# Simulation
DRONE_MODE=SIMULATION python main.py --search-area --speed 5

# Real flight on Pi
python main.py --search-area --model cv_models/sar_v2_1088/best.tflite

# Passive watch (manual RC flight, AI observes)
python passive_watch.py --model cv_models/sar_v2_1088/best.tflite

# Diagnostics dashboard
python tests/diagnostics/diagnostics.py

# Benchmark all models
python tests/day_1_experiments/model_compare.py --frames 50

# Draw flight plans (laptop only)
python flight_plans/draw_search_area.py
python flight_plans/draw_waypoints.py
python flight_plans/draw_transit.py
```
