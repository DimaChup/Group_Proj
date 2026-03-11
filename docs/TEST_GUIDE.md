# Test Scripts Guide

> Which tests to run, when, and why. 41 scripts across 6 categories.

## Quick Reference: Flight Day Critical Path

Run these **in order** before any autonomous flight:

```
BENCH (indoors, no props):
  1. tests/hardware/benchmark.py          — inference speed OK?
  2. tests/hardware/gps_health.py         — GPS configured? (wait for lock outdoors)
  3. tests/flight/0a_cube_commands.py     — commands reach Cube?
  4. tests/flight/0b_bench_mission.py     — full sequence ACKs?
  5. tests/calibration/fov_calibrate.py   — FOV with ruler → update FOCAL_LENGTH_MM

OUTDOOR (GPS lock required):
  6. tests/diagnostics/diagnostics.py     — all systems green?
  7. tests/flight/1_passive_flight.py     — manual RC, CV watches (ZERO commands)
  8. tests/flight/2_waypoints.py          — autonomous GPS waypoints (no CV)

  >>> GO / NO-GO DECISION <<<

  9. tests/flight/4_detect_and_center.py  — full autonomous with CV
```

## Categories

### Hardware (`tests/hardware/`) — Component Checks
| Script | What | Needs | Commands | Essential? |
|--------|------|-------|----------|-----------|
| benchmark.py | Inference speed (50 runs) | AI model | ZERO | YES |
| cv_benchmark.py | Live detection rate + speed | Camera + AI | ZERO | Nice |
| detection_snapshot_test.py | Auto-save detection images | Camera + AI | ZERO | Nice |
| buzzer_test.py | Cube buzzer melodies | Cube | Tune only | Nice |
| gps_test.py | GPS diagnostics table | Cube GPS | READ-ONLY | YES |
| gps_health.py | Step-by-step GPS check | Cube GPS | READ-ONLY | YES |

### Flight (`tests/flight/`) — Progressive Trust-Building
Numbered by risk level. **Never skip a number.**

| Script | Risk | What | Commands | Essential? |
|--------|------|------|----------|-----------|
| 0a_cube_commands.py | LOW | Test command path (mode, arm, params) | Mode changes | YES |
| 0b_bench_mission.py | LOW | Full mission sequence on bench | ARM attempt, waypoints | YES |
| 0c_feedback_test.py | LOW | Vision→GPS pipeline (hand-carry) | ZERO | Nice |
| 1_passive_flight.py | MED | Manual RC + passive CV logging | ZERO | **CRITICAL** |
| 2_waypoints.py | HIGH | Fly GPS waypoints autonomously | ARM, goto, land | **CRITICAL** |
| 3_auto_detect.py | HIGH | AUTO + detect → GUIDED hover | Mode switch | Nice |
| 4_detect_and_center.py | **CRIT** | Full autonomous: pattern + CV + centre | Velocity commands | **CRITICAL** |
| 5_two_waypoints.py | HIGH | Simple 2-waypoint test | ARM, goto, land | Redundant (use 2) |

**Utilities** (laptop only, zero risk):
- draw_search_area.py → search_area.json (draw polygon on map)
- draw_waypoints.py → waypoints.json (place waypoints on map)
- live_map.py — real-time drone position viewer

### Diagnostics (`tests/diagnostics/`) — Monitoring
| Script | What | Essential? |
|--------|------|-----------|
| diagnostics.py | Multi-view connectivity dashboard | YES (preflight) |
| cube_monitor.py | Live telemetry (attitude, GPS, battery) | Debug tool |
| camera_stream.py | MJPEG stream to browser | Nice |
| camera_stream_fast.py | Threaded MJPEG (smoother) | Nice |
| camera_stream_h264.py | H.264/HLS via FFmpeg | Not needed |

### Calibration (`tests/calibration/`) — Accuracy Setup
| Script | When | What |
|--------|------|------|
| fov_calibrate.py | **Pre-flight bench** | Ruler method → FOCAL_LENGTH_MM |
| fov_test_simple.py | Quick check | Single FOV measurement |
| alt_test.py | Hovering at altitude | FOV from real altitude |
| lens_calibrate.py | If edge distortion visible | Checkerboard calibration |
| gps_ground_truth.py | **After landing** | CV estimate vs actual GPS |

### Day 1 Experiments (`tests/day_1_experiments/`) — Data Collection
All passive (ZERO commands), all output CSV. Run during manual flights.

| Script | Measures | Output |
|--------|----------|--------|
| altitude_sweep.py | Detection rate vs altitude (10-30m) | altitude_sweep.csv |
| speed_sweep.py | Detection rate vs speed + blur | speed_sweep.csv |
| gps_accuracy.py | GPS estimate error vs ground truth | gps_accuracy.csv |
| gps_drift.py | GPS noise floor (CEP50/95) | gps_drift.csv |
| model_compare.py | Benchmark all .tflite models | Terminal comparison |
| detection_log.py | General flight logger | detection_log.csv |

### Laptop (`tests/laptop/`) — Development Only
Skip on flight day. For simulation/development.

| Script | What |
|--------|------|
| test_camera.py | Camera preview + snapshot |
| test_cv.py | Model loading + detection |
| test_cube.py | Cube heartbeat + GPS |
| test_all.py | Full connectivity check |
| test_tflite.py | TFLite inference test |
| debug_tflite.py | Raw model output inspection |
| cv_test_synthetic.py | Synthetic detection benchmark |
| visualize_paths.py | Path planning visualization |

## Dependency Chain

```
Camera works? ──→ AI model loads? ──→ Detection works?
                                          │
Cube responds? ──→ GPS lock? ──→ Commands work?
                                          │
                              FOV calibrated? ──→ GPS estimation accurate?
                                          │
                              ┌────────────┴────────────┐
                              │                         │
                    1_passive_flight           2_waypoints
                    (manual + CV)             (auto GPS)
                              │                         │
                              └─────────┬───────────────┘
                                        │
                              4_detect_and_center
                              (full autonomous)
```

## Platform Compatibility

| Script Category | Laptop (SIM) | Pi (REAL) | Headless? |
|-----------------|:---:|:---:|:---:|
| hardware/ | Partial | YES | Most have --headless |
| flight/0a-0c | YES | YES | YES |
| flight/1-4 | SIM only | YES | YES (--headless) |
| diagnostics/ | YES | YES | Most have --headless |
| calibration/ | YES | YES | Most have --headless |
| day_1_experiments/ | SIM only | YES | YES (--headless) |
| laptop/ | YES | No | No (need display) |

## Common Flags

Most flight/experiment scripts support:
- `--headless` — no cv2.imshow (SSH/PuTTY safe)
- `--stream` — MJPEG stream on port 8090
- `--dry-run` — simulate without arming
- `--save-detections` — save detection images
- `--save-frames` — save all frames

## Redundant Scripts (can skip)

- `5_two_waypoints.py` — simpler version of `2_waypoints.py`
- `fov_test_simple.py` — less comprehensive than `fov_calibrate.py`
- `camera_stream_h264.py` — MJPEG is preferred (lower latency)
- `detection_snapshot_test.py` — overlaps with `1_passive_flight.py --save-detections`
