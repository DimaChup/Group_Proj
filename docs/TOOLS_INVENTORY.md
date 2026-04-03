# Tools Inventory

Definitive reference for every script, tool, and utility in the SAR drone project.
Last updated: 2026-04-03.

---

## 1. Mission Scripts

Scripts that fly the drone or run a full autonomous mission.

| File | Purpose | Platform | Safety | Key Flags | Dependencies |
|------|---------|----------|--------|-----------|--------------|
| `main.py` | Full autonomous SAR mission: state machine, search pattern, detection, centering, descent, landing | Both | **SENDS COMMANDS** — arms, takes off, navigates, lands | `--dry-run` `--headless` `--alt N` `--speed N` `--model PATH` `--transit FILE` `--beacon-delay N` `--smart-detect` `--center-verify` `--no-nfz` `--no-stream` | pymavlink, opencv, vision.py, planning.py, config.py, state_machine.py, navigation.py, stream_server.py |
| `pi_flight.py` | Web-based ground station with browser dashboard, MJPEG stream, operator command buttons | Both | **SENDS COMMANDS** (unless `--passive`) | `--port N` `--fps N` `--cluster-dist N` `--takeoff-alt N` `--passive` | pymavlink, opencv, vision.py, config.py |
| `simple_state.py` | Simple state machine test: fly transit waypoints, descend to 3m, hover, reverse, land | Both | **SENDS COMMANDS** — arms, flies waypoints, lands | `--alt N` | pymavlink, flight_plans/transit.json |

---

## 2. Monitoring and Detection

Passive observers that stream video, run AI detection, and log results. Send zero commands.

| File | Purpose | Platform | Safety | Key Flags | Dependencies |
|------|---------|----------|--------|-----------|--------------|
| `field_tools/passive_watch.py` | Passive camera observer with web stream, auto-snapshot on detection, GPS estimation | Both | **ZERO commands** | `--port N` `--conf N` `--fps N` `--save-dir DIR` `--no-save` `--no-mavlink` `--model PATH` `--simple-names` `--class-filter CLASS` `--smart-estimate` `--smart-min N` `--smart-radius N` `--smart-dir DIR` `--fake` `--fake-video` `--fake-srt` `--no-stream` | opencv, vision.py, config.py, pymavlink (optional) |
| `field_tools/passive_watch_clean.py` | Same as passive_watch but saves RAW detection images (no overlay) as PNG with GPS in filename | Both | **ZERO commands** | `--port N` `--conf N` `--fps N` `--save-dir DIR` `--no-save` `--no-mavlink` `--model PATH` | opencv, vision.py, config.py |
| `field_tools/passive_watch_recovered.py` | Recovery copy of passive_watch.py (backup) | Both | **ZERO commands** | Same as passive_watch.py | Same as passive_watch.py |
| `tests/diagnostics/diagnostics.py` | Multi-view connectivity + camera + telemetry dashboard with threaded AI and model switching | Both | **ZERO commands** (read-only telemetry) | M key cycles models | pymavlink, opencv, vision.py |
| `tests/diagnostics/cube_monitor.py` | Live Cube telemetry dashboard in terminal (GPS, attitude, battery, RC, modes) | Both | **ZERO commands** (read-only MAVLink) | None | pymavlink |
| `tests/diagnostics/camera_stream.py` | Simple MJPEG stream to browser with optional AI overlay | Both | **ZERO commands** | None | opencv, vision.py |
| `tests/diagnostics/camera_stream_fast.py` | Threaded MJPEG stream (faster frame delivery) | Both | **ZERO commands** | None | opencv, vision.py |
| `tests/diagnostics/camera_stream_h264.py` | H.264/HLS camera stream via FFmpeg | Pi | **ZERO commands** | None | opencv, ffmpeg |
| `tests/flight/live_map.py` | Real-time drone position on satellite map with coverage overlay | Windows | **ZERO commands** (read-only telemetry) | `--host IP` `--port N` | pymavlink, opencv, map.jpg |

---

## 3. Calibration

Scripts for calibrating camera FOV, lens distortion, and GPS estimation accuracy.

| File | Purpose | Platform | Safety | Key Flags | Dependencies |
|------|---------|----------|--------|-----------|--------------|
| `tests/calibration/fov_calibrate.py` | Comprehensive bench FOV calibration with multi-height measurements | Both | **ZERO commands** (camera read-only) | `--headless` | opencv |
| `tests/calibration/fov_test_simple.py` | Simple single-measurement FOV test | Both | **ZERO commands** | `--headless` | opencv |
| `tests/calibration/alt_test.py` | FOV calibration at real altitude using Cube telemetry | Both | **ZERO commands** (read-only altitude) | None | pymavlink, opencv |
| `tests/calibration/lens_calibrate.py` | Checkerboard lens distortion calibration, saves calibration_data.npz | Both | **ZERO commands** | `--headless` `--board 13x8` `--load` | opencv, numpy |
| `tests/calibration/gps_estimate_calibrate.py` | Terminal-based focal length calibration for GPS estimation accuracy | Both | **ZERO commands** (read-only telemetry) | `--no-mavlink` | pymavlink (optional), opencv |
| `tests/calibration/gps_calibrate_gui.py` | OpenCV GUI focal length calibration with live camera, step-by-step workflow | Both | **ZERO commands** | None | pymavlink, opencv |
| `tests/calibration/gps_ground_truth.py` | Compare CV GPS estimate vs actual GPS (walk to dummy with phone) | Both | **ZERO commands** (read-only GPS) | None | pymavlink |
| `tools/fov_calibrate_video.py` | FOV calibration from DJI video: click dummy at different altitudes, compute focal length | Windows | **Read-only** (video file) | None | opencv, argparse |
| `tools/map_calibrate.py` | Click landmarks on map.jpg, enter real GPS, compute optimal map calibration constants | Windows | **Read-only** | None | opencv |

---

## 4. Data Collection

Scripts for recording training data, video, and photos. Send zero commands.

| File | Purpose | Platform | Safety | Key Flags | Dependencies |
|------|---------|----------|--------|-----------|--------------|
| `field_tools/capture_training.py` | Record video + photos for model retraining with per-frame GPS telemetry CSV | Both | **ZERO commands** | `--video` `--interval N` `--port N` `--fps N` `--res WxH` `--no-mavlink` `--undistort` | opencv, pymavlink (optional) |
| `generate_dataset_v2.py` | Generate synthetic training images + negatives at 1456x1088 from map.jpg + dummy.png | Windows | **Read-only** (generates files) | None | opencv, numpy, map.jpg, dummy.png |
| `tools/label_tool.py` | Label real video frames with bounding boxes for YOLO training | Windows | **Read-only** | `--full` (native resolution) | opencv |

---

## 5. Flight Tests

Progressive test ladder from bench to autonomous. Numbered 0a through 5.

| File | Purpose | Platform | Safety | Key Flags | Dependencies |
|------|---------|----------|--------|-----------|--------------|
| `tests/flight/0a_cube_commands.py` | Bench: test individual MAVLink commands (mode switch, arm, param read) | Both | **SENDS COMMANDS** (mode changes, arm attempt) | None | pymavlink |
| `tests/flight/0b_bench_mission.py` | Bench: full mission command sequence WITHOUT flying (no props) | Both | **SENDS COMMANDS** (full sequence on bench) | None | pymavlink |
| `tests/flight/0c_feedback_test.py` | Bench: vision-to-GPS-to-command pipeline end-to-end, reads telemetry only | Both | **ZERO commands** (read-only telemetry) | None | pymavlink, opencv, vision.py |
| `tests/flight/0d_planning_test.py` | Verify lawnmower pattern generation, bounds, NFZ avoidance (6 tests) | Both | **ZERO** (pure computation, no connection) | None | planning.py, config.py |
| `tests/flight/0e_geofence_test.py` | NFZ boundary math, waypoint filtering, repulsion vectors (7 tests) | Both | **ZERO** (pure computation, no connection) | None | geofence.py, config.py |
| `tests/flight/0f_servo_test.py` | Bench: test payload servo PWM commands on Cube AUX rail | Both | **SENDS COMMANDS** (servo PWM only, no arming) | None | pymavlink |
| `tests/flight/1_passive_flight.py` | Manual RC flight with passive AI detection, buzzer beeps on detection | Both | **ZERO commands** (read-only telemetry + buzzer) | `--headless` | pymavlink, opencv, vision.py |
| `tests/flight/2_waypoints.py` | Fly GPS waypoints from waypoints.json in GUIDED mode | Both | **SENDS COMMANDS** (arms, flies, lands) | `--dry-run` `--alt N` | pymavlink, waypoints.json |
| `tests/flight/3_auto_detect.py` | AUTO waypoints + AI detection triggers GUIDED hover on target | Both | **SENDS COMMANDS** (mode switch, position hold) | `--dry-run` `--headless` `--stream` | pymavlink, opencv, vision.py |
| `tests/flight/4_detect_and_center.py` | Autonomous search pattern + velocity-based visual centering on target | Both | **SENDS COMMANDS** (velocity commands during centering) | `--dry-run` `--headless` `--stream` | pymavlink, opencv, vision.py |
| `tests/flight/5_two_waypoints.py` | Fly to 2 hardcoded GPS coordinates, hover, land (minimal setup) | Both | **SENDS COMMANDS** (arms, flies, lands) | `--dry-run` `--alt N` `--hover N` | pymavlink |
| `tests/flight/geofence_demo.py` | Upload hardware polygon fence to ArduCopter, test breach response | Both | **SENDS COMMANDS** (fence upload, optional breach test) | `--dry-run` `--test-breach` | pymavlink, opencv |
| `tests/flight/geofence_repulsion_test.py` | Visualize repulsion field vectors on satellite map (click to test) | Windows | **Read-only** (visualization) | None | opencv, geofence.py, map.jpg |
| `tests/mapping/0d_mapping_test.py` | Interactive SITL-to-real mapping verification: direction, yaw, speed, servo, altitude | Both | **SENDS COMMANDS** (velocity, yaw, servo, mode) | None | pymavlink, config.py |

---

## 6. Benchmarks

Inference speed, detection rate, and system performance measurement.

| File | Purpose | Platform | Safety | Key Flags | Dependencies |
|------|---------|----------|--------|-----------|--------------|
| `tests/hardware/benchmark.py` | Quick inference speed benchmark (50 runs, timing report) | Both | **ZERO commands** (pure computation) | Image path (optional) | vision.py, opencv |
| `tests/hardware/benchmark_full.py` | Comprehensive 6-section benchmark: system info, preprocessing, all models, threading | Both | **ZERO commands** | None | vision.py, opencv, numpy |
| `tests/hardware/ncnn_benchmark.py` | Compare NCNN vs TFLite inference speed side-by-side | Both | **ZERO commands** | None | vision.py, ncnn (optional) |
| `tests/hardware/cv_benchmark.py` | Live camera detection rate, speed, and motion blur simulation | Both | **ZERO commands** (camera read-only) | `--headless` `--blur` | opencv, vision.py |
| `tests/hardware/detection_snapshot_test.py` | Single-frame detection test on a static image | Both | **ZERO commands** | None | vision.py |
| `tests/day_1_experiments/altitude_sweep.py` | Detection rate vs altitude in 10-30m buckets, CSV output | Both | **ZERO commands** (observational) | None | pymavlink, opencv, vision.py |
| `tests/day_1_experiments/speed_sweep.py` | Detection rate vs drone speed + blur metric, CSV output | Both | **ZERO commands** | None | pymavlink, opencv, vision.py |
| `tests/day_1_experiments/gps_accuracy.py` | GPS estimate error vs known dummy position, CSV output | Both | **ZERO commands** | None | pymavlink, opencv, vision.py |
| `tests/day_1_experiments/gps_drift.py` | GPS noise floor (CEP50, CEP95) from stationary Cube, CSV output | Both | **ZERO commands** | None | pymavlink |
| `tests/day_1_experiments/model_compare.py` | Benchmark and compare all .tflite models (speed + detection rate) | Both | **ZERO commands** (no Cube needed) | None | vision.py |
| `tests/day_1_experiments/detection_log.py` | General catch-all flight logger: every detection + telemetry to CSV | Both | **ZERO commands** | None | pymavlink, opencv, vision.py |

---

## 7. Visualization and Simulation

Interactive tools for pattern design, path analysis, and demo animations.

| File | Purpose | Platform | Safety | Key Flags | Dependencies |
|------|---------|----------|--------|-----------|--------------|
| `dashboard/` | Standalone React+Vite+Tailwind web app: project tracker, WBS, SE visualization | Windows | **Read-only** (static web app) | `npm run dev` on port 5050 | Node.js, npm |
| `tools/pattern_visualizer_v7.py` | Interactive search pattern visualizer with sliders (altitude, overlap, angle, NFZ buffer) | Windows | **Read-only** | `--draw` (custom polygon) | opencv, planning.py, config.py |
| `tools/pattern_visualizer.py` | Pattern visualizer (earlier version) | Windows | **Read-only** | `--draw` | opencv, planning.py |
| `tools/pattern_visualizer_v1.py` | Pattern visualizer v1 | Windows | **Read-only** | None | opencv |
| `tools/pattern_visualizer_v2.py` | Pattern visualizer v2 | Windows | **Read-only** | None | opencv |
| `tools/pattern_visualizer_v5.py` | Pattern visualizer v5 | Windows | **Read-only** | None | opencv |
| `tools/pattern_visualizer_v6.py` | Pattern visualizer v6 | Windows | **Read-only** | None | opencv |
| `tools/lawnmower_visual.py` | Draw polygon on map, see lawnmower pattern at different altitudes, compare mode | Windows | **Read-only** | `--altitude N` `--compare` | opencv, planning.py |
| `tools/pattern_compare.py` | Compare search patterns (lawnmower angles, spiral, altitudes) with drone physics simulation | Windows | **Read-only** (generates analysis) | None | numpy, config.py, planning.py |
| `tools/pattern_compare_35m.py` | Pattern comparison at 35m altitude | Windows | **Read-only** | None | numpy, config.py |
| `tools/pattern_compare_v2.py` | Pattern comparison v2 with updated physics | Windows | **Read-only** | None | numpy, config.py |
| `tools/pattern_compare_visual.py` | Visual pattern comparison with side-by-side plots | Windows | **Read-only** | None | opencv, numpy |
| `tools/descent_sim.py` | Simulate drone descent near NFZ buffer zone (ArduCopter physics model) | Windows | **Read-only** (pure simulation) | None | config.py |
| `tools/descent_test_sitl.py` | Systematic SITL descent test: fly to locations, command descent, measure result | Windows | **SENDS COMMANDS** (SITL only) | None | pymavlink, config.py |
| `tools/path_physics.py` | Reusable path physics simulation engine (momentum, NFZ speed limits, energy) | Both | **Library module** (no standalone execution) | N/A (import only) | numpy, config.py |
| `tests/laptop/servo_release_demo.py` | Visual animation of two-stage servo release mechanism (OpenCV drawing) | Windows | **Read-only** (animation) | None | opencv |
| `tests/laptop/visualize_paths.py` | Generate image showing lawnmower patterns for 5 polygon shapes + algorithm explanation | Windows | **Read-only** (generates image) | None | opencv, planning.py |
| `tests/flight/geofence_repulsion_test.py` | Visualize potential field repulsion vectors on satellite map | Windows | **Read-only** | None | opencv, geofence.py |

---

## 8. Video Analysis

DJI flight video replay with detection overlay, model comparison, and GPS estimation.

| File | Purpose | Platform | Safety | Key Flags | Dependencies |
|------|---------|----------|--------|-----------|--------------|
| `tests/laptop/video_test.py` | DJI video replay with detection overlay, SRT telemetry, GPS scatter, scale bar, measure tool | Windows | **Read-only** | SPACE=pause T=tiling A/D=skip +/-=speed | opencv, ultralytics or tflite, RealVideo/ |
| `tests/laptop/video_test_compare.py` | A/B model comparison on DJI video (M key switches models live) | Windows | **Read-only** | M=switch model | opencv, ultralytics or tflite, RealVideo/ |
| `tests/laptop/video_compare_all.py` | Cycle through 3 backends (TFLite original, v2-1088 TFLite, v2-1088 NCNN) on DJI video | Windows | **Read-only** | M=next model T=tiling | opencv, RealVideo/ |
| `tests/laptop/ncnn_video_player.py` | Play video with NCNN detection (simple, no threading) | Both | **Read-only** | SPACE A/D | opencv, ncnn |
| `tests/laptop/tflite_video_player.py` | Play video with TFLite detection (compare FPS vs NCNN) | Both | **Read-only** | SPACE A/D | opencv, tflite |
| `tests/laptop/gps_cluster_compare.py` | Run detection over full DJI video with different settings, compare GPS estimate clusters | Windows | **Read-only** | None | opencv, vision.py, RealVideo/ |
| `tests/laptop/video_tools/detect_fullres.py` | Full-resolution single-pass detection helper | Windows | **Library module** | N/A | opencv |
| `tests/laptop/video_tools/detect_tiling.py` | Tiled detection (640px tiles with overlap) helper | Windows | **Library module** | N/A | opencv |
| `tests/laptop/video_tools/video_tiling.py` | Video frame tiling utilities | Windows | **Library module** | N/A | opencv |
| `tests/laptop/video_tools/video_test_baseline.py` | Baseline detection logic for video analysis | Windows | **Library module** | N/A | opencv |
| `tests/laptop/video_tools/zoom_detect_baseline.py` | Zoom-based detection baseline | Windows | **Library module** | N/A | opencv |
| `tests/laptop/zoom_detect.py` | Zoom-based detection test on video | Windows | **Read-only** | None | opencv |

---

## 9. Hardware Tests

Individual component checks for camera, GPS, buzzer, and detection.

| File | Purpose | Platform | Safety | Key Flags | Dependencies |
|------|---------|----------|--------|-----------|--------------|
| `tests/laptop/test_camera.py` | Camera preview + snapshot (test camera works) | Both | **ZERO commands** | Camera index arg | opencv |
| `tests/laptop/test_cv.py` | AI model loading + detection test on dummy.png or live webcam | Both | **ZERO commands** | `--camera` (live mode), image path arg | vision.py, opencv |
| `tests/laptop/test_cube.py` | Cube heartbeat, GPS, attitude, battery check | Both | **ZERO commands** (read-only MAVLink) | Connection string arg | pymavlink |
| `tests/laptop/test_all.py` | Full system connectivity check: Cube link + camera + AI model + platform detection | Both | **ZERO commands** | None | pymavlink, opencv, vision.py |
| `tests/laptop/test_tflite.py` | TFLite inference test on laptop (live webcam or synthetic altitude sweep) | Both | **ZERO commands** | `--synthetic` | opencv, tflite |
| `tests/laptop/debug_tflite.py` | Raw TFLite model output inspection (tensor shapes, values, ranges) | Both | **ZERO commands** | None | tflite |
| `tests/laptop/cv_test_synthetic.py` | Synthetic image CV benchmark (generate test frames, run detection) | Windows | **ZERO commands** | `--headless` `--save` | opencv, vision.py |
| `tests/laptop/blur_altitude_test.py` | Simulate detection at different altitudes and motion blur levels | Windows | **ZERO commands** | `--model PATH` `--backend ncnn` | opencv, vision.py |
| `tests/hardware/buzzer_test.py` | Play 15 buzzer melodies via MAVLink PLAY_TUNE command | Both | **SENDS COMMANDS** (harmless buzzer tunes only) | None | pymavlink |
| `tests/hardware/gps_test.py` | GPS diagnostics with satellite tracking and fix quality | Both | **ZERO commands** (read-only MAVLink) | None | pymavlink |
| `tests/hardware/gps_health.py` | Step-by-step GPS verification (HDOP, satellite count, fix type) | Both | **ZERO commands** (read-only MAVLink) | None | pymavlink |

---

## 10. Automated and Unit Tests

Non-interactive tests that run to completion and report pass/fail.

| File | Purpose | Platform | Safety | Key Flags | Dependencies |
|------|---------|----------|--------|-----------|--------------|
| `tests/automated/sitl_smoke_test.py` | SITL smoke test: arm, takeoff, waypoints, yaw, velocity, land with 30s timeouts | Windows | **SENDS COMMANDS** (SITL only) | `--conn STRING` | pymavlink |
| `tests/automated/coverage_simulation.py` | Coverage simulation: compute coverage % at different altitudes with turning modes | Both | **ZERO** (pure computation) | None | planning.py, config.py, opencv |
| `tests/automated/geofence_optimization.py` | Sweep repulsion parameters (speed, buffer, damping) to find optimal geofence settings | Both | **ZERO** (pure computation) | None | config.py |
| `tests/automated/geofence_unit_test.py` | Geofence math unit tests without SITL (pure geometry) | Both | **ZERO** (pure computation) | None | geofence.py |
| `tests/unit/test_config.py` | Unit tests for config.py (altitude ranges, image dimensions) | Both | **ZERO** | None | pytest, config.py |
| `tests/unit/test_gps_utils.py` | Unit tests for gps_utils.py (Haversine distance, bearing) | Both | **ZERO** | None | pytest, gps_utils.py |
| `tests/unit/test_planning.py` | Unit tests for planning.py (lawnmower pattern generation on various polygons) | Both | **ZERO** | None | pytest, planning.py |
| `tests/unit/test_states.py` | Unit tests for states.py (state enum validation) | Both | **ZERO** | None | pytest, states.py |
| `tests/unit/test_utils.py` | Unit tests for utils.py (GeoTransformer, overlay_image_alpha) | Both | **ZERO** | None | pytest, utils.py |
| `tests/unit/test_vision.py` | Unit tests for vision.py (VisionSystem constructor, camera skip, model fallback) | Both | **ZERO** | None | pytest, vision.py |
| `tests/integration/test_imports.py` | Verify all .py files compile and core modules import without errors | Both | **ZERO** | None | pytest |
| `tests/laptop/test_passive_watch.py` | Automated integration test: launch passive_watch in --fake mode, exercise HTTP API | Windows | **ZERO commands** | None | requests, RealVideo/ |
| `tests/laptop/test_approach_descent.py` | Investigate ArduCopter low-altitude descent behavior in SITL | Windows | **SENDS COMMANDS** (SITL only) | None | pymavlink |
| `tests/laptop/test_nfz_manual.py` | Test NFZ velocity clamping math without SITL (pure computation) | Both | **ZERO** (pure computation) | None | config.py, geofence.py |

---

## 11. Preflight and System Checks

Run before flight to verify everything is connected and ready.

| File | Purpose | Platform | Safety | Key Flags | Dependencies |
|------|---------|----------|--------|-----------|--------------|
| `field_tools/preflight.py` | Standalone connectivity checker (camera, Cube, AI model, network) | Both | **ZERO commands** (read-only checks) | None | opencv, pymavlink |
| `field_tools/system_readiness.py` | Comprehensive system readiness check (12+ subsystems, color-coded report) | Both | **ZERO commands** | `--quick` `--no-cube` | opencv, pymavlink, config.py |

---

## 12. Core Library Modules

Not standalone scripts. Imported by other scripts.

| File | Purpose | Imported By |
|------|---------|-------------|
| `config.py` | All settings: altitudes, speeds, camera, connection, mode auto-detection | Nearly everything |
| `states.py` | State enum (INIT, SEARCH, VERIFY, LANDING, etc.) | main.py, state_machine.py |
| `utils.py` | Geo math: GPS-to-pixel conversion (GeoTransformer), overlay helpers | main.py, pi_flight.py, tests |
| `vision.py` | Camera + AI detection with dual backend (Ultralytics on laptop, TFLite on Pi) | All detection scripts |
| `planning.py` | Lawnmower search pattern generator from any GPS polygon | main.py, visualizers, tests |
| `geofence.py` | NFZ enforcement: polygon test, repulsion vectors, speed clamping | main.py, state_machine.py, tests |
| `gps_utils.py` | Shared GPS math: Haversine distance, bearing, landing offset | main.py, field_tools |
| `navigation.py` | MAVLink navigation commands wrapper (arm, takeoff, goto, land, velocity, yaw) | main.py, state_machine.py |
| `state_machine.py` | State handler mixin: all state transition logic for the mission | main.py |
| `stream_server.py` | Lightweight HTTP server for MJPEG streaming and operator commands | main.py |
| `spiral_planner.py` | Perimeter spiral planner for any GPS polygon | planning.py, visualizers |
| `field_tools/cv_pipeline_visual.py` | Self-contained HTML/CSS/JS for CV pipeline visualization diagram | passive_watch.py |
| `field_tools/gps_pipeline_visual.py` | Self-contained HTML/CSS/JS for GPS estimation pipeline visualization | passive_watch.py |
| `field_tools/interactive_map.py` | Interactive canvas map component with zoom, pan, FOV footprint, detection dots | passive_watch.py |
| `field_tools/gps_charts.py` | HTML/JS for interactive GPS scatter charts in browser dashboard | passive_watch.py, pi_flight.py |
| `tools/path_physics.py` | Path physics simulation engine (momentum, NFZ speed limits, energy model) | pattern_compare tools |

---

## Quick Reference: Safety Summary

| Safety Level | Count | Scripts |
|--------------|-------|---------|
| **SENDS COMMANDS** (can arm/fly) | 13 | main.py, pi_flight.py, simple_state.py, 0a, 0b, 0f, 2_waypoints, 3_auto_detect, 4_detect_and_center, 5_two_waypoints, geofence_demo, descent_test_sitl, sitl_smoke_test |
| **SENDS COMMANDS** (bench only) | 2 | buzzer_test (harmless tunes), mapping_test (bench/SITL) |
| **ZERO commands** | ~50+ | All passive_watch variants, diagnostics, calibration, benchmarks, experiments, unit tests |
| **Read-only / Library** | ~20 | config, vision, planning, geofence, visualizers, video analysis |

---

## Quick Reference: Platform Summary

| Platform | What Runs | What Does Not |
|----------|-----------|---------------|
| **Windows laptop** | Everything except picamera2-dependent scripts | camera_stream_h264 (needs Pi FFmpeg + picamera2) |
| **Raspberry Pi** | All field_tools, tests/hardware, tests/flight, main.py, pi_flight.py | tests/laptop/video_* (need DJI video files + Ultralytics), dashboard (needs Node.js) |
| **Both** | Core modules, unit tests, most flight tests (auto-detect SITL vs real) | |

---

## Total Script Count

| Category | Count |
|----------|-------|
| Mission scripts | 3 |
| Monitoring and detection | 10 |
| Calibration | 9 |
| Data collection | 3 |
| Flight tests | 14 |
| Benchmarks | 11 |
| Visualization and simulation | 19 |
| Video analysis | 12 |
| Hardware tests | 11 |
| Automated and unit tests | 14 |
| Preflight | 2 |
| Core library modules | 16 |
| **Total** | **~124** |
