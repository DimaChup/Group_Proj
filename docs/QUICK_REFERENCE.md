# SAR Drone — Quick Reference (One-Page Cheat Sheet)

## How to Run

```bash
# Full autonomous mission (real or SITL)
python main.py

# Dry-run: visualize search pattern (no GPS/Cube needed)
python main.py --dry-run

# Swap AI model
python main.py --model cv_models/sar_v2_1088/best.tflite

# Headless mode (auto-detects on Pi)
python main.py --headless

# Interactive simulator (laptop only)
python simple_simulator.py --tflite --gps-drift 3 --shake 5

# Web ground station (browser dashboard)
python pi_flight.py

# Passive detection (pilot flies RC, Pi logs detections only)
python passive_watch.py
```

## Key Config Values (`config.py`)

| Parameter | Value | Purpose |
|-----------|-------|---------|
| TARGET_ALT | 30m | Search altitude |
| VERIFY_ALT | 15m | Confirmation hover altitude |
| SEARCH_SPEED_MPS | 5 m/s | Pattern flying speed |
| DESCEND_SPEED_MPS | 1 m/s | Safe descent rate |
| CONFIDENCE_THRESHOLD | 0.4 | AI detection threshold (0.0-1.0) |
| IMAGE_W, IMAGE_H | 1456x1088 | Pi camera resolution (native) |
| FOCAL_LENGTH_MM | 5.46 | Calibrated 2026-03-11 |

## State Machine (11 states → DONE)

1. **INIT** → Startup, load config, check files
2. **CONNECTING** → Wait for Cube heartbeat
3. **ARMING** → Disarm safety, request ARM
4. **TAKEOFF** → Climb to TARGET_ALT
5. **SEARCH** → Fly lawnmower pattern, scan for target
6. **CENTERING** → Hover and center on detection (visual servo)
7. **DESCENDING** → Drop to VERIFY_ALT while centered
8. **VERIFY** → Operator confirms Y/N (keyboard or browser)
9. **APPROACH** → Fly to hover over target GPS location
10. **LANDING** → Auto-land at target (or RTL if rejected)
11. **DONE** → Mission complete, disarm

## Keyboard Controls (main.py + pi_flight.py)

| Key | Action | Notes |
|-----|--------|-------|
| Y | Confirm target | Proceed to landing |
| N | Reject target | Resume search |
| I | Mark as interest | Log but continue searching |
| X | False positive | Mark and continue |
| M | Manual override | Switch to MANUAL mode |
| L | Land now | Force landing at current GPS |
| SPACE | Arm/disarm | Bench testing |
| Q | Quit | Exit gracefully |

**Browser buttons** (pi_flight.py): same Y/N/I/X/L buttons on dashboard at http://PI_IP:8090

## File Map (One-Line Reference)

| File | Purpose |
|------|---------|
| **config.py** | All settings (altitudes, speeds, thresholds) |
| **main.py** | Mission orchestrator (state machine, core logic) |
| **vision.py** | Camera + AI detection (dual backend: Ultralytics/TFLite) |
| **planning.py** | Lawnmower search pattern generator |
| **utils.py** | Geo math (GPS ↔ pixel conversion, Kalman filter) |
| **states.py** | State enum (SEARCH, VERIFY, LANDING, etc.) |
| **pi_flight.py** | Web ground station (browser dashboard + MJPEG) |
| **simple_simulator.py** | Interactive MVP (keyboard flight + CV + landing) |
| **passive_watch.py** | Passive observer (stream + detection, zero commands) |
| **best.tflite** | Active AI model (~3.3MB, all scripts read this) |
| **cv_models/** | Alternative models (sar_v2_1088, sar_640, sar_1280) |
| **tests/** | All test scripts (hardware, flight, calibration, diagnostics) |

## Detection Pipeline (One Paragraph)

Camera capture (Pi: 1456x1088 @ 30fps, Laptop: 640x480 @ 30fps) → lens undistortion (2ms) → AI inference via TFLite (206ms on Pi, 4.8 FPS) or Ultralytics (30fps on laptop) → bounding box extraction → confidence threshold (0.4) filter → (x, y, confidence) return. Found target triggers CENTERING state, which uses visual servo (offset from center) + GPS estimation (inverse variance weighting) to hover over dummy.

## NFZ Protection (One Paragraph)

Geofence defined in `config.py`: SEARCH_AREA_GPS (5-corner search zone), FLIGHT_AREA_GPS (4-corner max boundary), SSSI_GPS (no-fly zone). Each state checks if drone is inside SEARCH_AREA and within FLIGHT_AREA. If outside SEARCH_AREA during SEARCH, auto-switches to RTL. If inside SSSI (forbidden zone), forces MANUAL mode + buzzer alert. Repulsive force applies within 10m of boundary (pushes drone inward). Operator can override with M key.

## Model Swapping (Pi Deployment)

All scripts read `best.tflite` from project root. To switch model:
```bash
cp cv_models/sar_v2_1088/best.tflite best.tflite  # Best model (mAP50=0.995)
# OR
cp models/human.tflite best.tflite                 # Backup COCO detector
```
**No code changes needed** — all backends auto-detect. Restart script to reload.

## Quick Debug Checklist

- [ ] Cube heartbeat? → Run `tests/flight/0a_cube_commands.py`
- [ ] Camera + AI? → Run `tests/laptop/test_cv.py --camera`
- [ ] GPS lock? → Run `tests/hardware/gps_test.py`
- [ ] Inference speed? → Run `tests/hardware/benchmark_full.py`
- [ ] Detection on video? → Run `tests/laptop/video_test.py` (needs DJI video)
- [ ] Geofence correct? → Run `python main.py --dry-run` (check map)

## Key Facts

- **Pi IP**: 192.168.1.3 (on flight day network)
- **Cube baud**: 921600 (mavproxy bridge required on Pi)
- **Camera output**: BGR (IMX296 label says RGB888 but outputs BGR — no cvtColor)
- **TFLite model**: Input [1,640,640,3] float32, output [1,5,8400] (5 anchors per cell)
- **Confidence threshold**: 0.4 in vision.py (tune after real flights)
- **Best model**: cv_models/sar_v2_1088/ (retrained 2026-03-16, mAP50=0.995)
- **FOV (DJI video)**: 54.4° HFOV @ 1456x1088 crop
- **Drone speed**: 5 m/s (tunable, trade-off: faster = more blur, slower = longer search time)

---

*Print this. Tape it to your monitor. Update after each session.*
