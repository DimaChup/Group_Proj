# SAR Drone Project -- Master Reference

> **The single entry point for anyone (human or AI) to understand the entire project.**
> Last updated: 2026-04-03. For detailed context: read `CLAUDE.md`. For session history: see `CLAUDE.md` Session Log.

---

## 1. What This Is

University of Bristol MSc project (AENGM0074). Team of 5. An autonomous Search and Rescue drone that takes off, flies a lawnmower search pattern over a defined area, uses onboard AI (YOLOv8n / TFLite) to detect a casualty dummy, centres on the target, descends for operator verification, and lands 7.5m away to deliver a first aid payload. The pilot retains RC override authority at all times. The system runs on a Raspberry Pi 5 with an IMX296 global shutter camera, connected to a Cube autopilot via mavproxy UDP bridge.

---

## IMPORTANT: Simulation Rendering Change (2026-04-03)

**Major design change to god view rendering in `simulator/simulation.py`.**
The god view was previously copying the full 63MB map image (4319x4885) every frame, then drawing overlays, then resizing for display. This caused the dashboard to become unresponsive, especially when the Flight Area geofence triggered RTL (the cv2 window froze due to skipped `cv2.waitKey` calls combined with heavy rendering).

**What changed**: The god view now works on a **pre-scaled map** (~4MB, scaled to `IMAGE_H` height at init). All coordinates are multiplied by `_god_scale`. Coverage overlay also at reduced resolution. This is a **94% memory reduction per frame**.

**Impact**: The simulation feels noticeably more responsive. Previous versions (before commit `374a462` on `Working8.Session4`) used the full-resolution map. If you need to revert, `git checkout ce5c036` has the old rendering with the geofence crash fix but without the god view optimization.

**Also fixed in this change**: Flight Area geofence RTL no longer crashes the dashboard. The RC override guard now allows RTL mode (6), calls `cv2.waitKey(1)` during override, and transitions state to LANDING.

---

## 2. Project Status (as of 2026-04-03)

| Metric | Value |
|--------|-------|
| Simulation readiness | **7.7 / 10** -- full mission runs end-to-end in SITL |
| Real hardware readiness | **2.1 / 10** -- bench tested, zero flights |
| L2 Critical Path | **1 / 13** steps done (component health). GPS fix is next blocker. |
| Unit tests | **116 passing** across 6 test files (2 known geofence edge cases) |
| WBS completion | 67/121 nodes (55%). Weakest: Integration & Testing (17%) |
| Deliverables | D1+D2+D3 done (27.5% of marks). D4 active. D5+D6+D7 upcoming (72.5%). |
| Total scripts | ~124 (13 send commands, 50+ send zero commands, 20+ library modules) |

### Three Product Levels

| Level | Name | What It Delivers | Gap to Achievement |
|-------|------|------------------|--------------------|
| **L1** | Manual MVP | Pilot flies RC, Pi detects passively, buzzer alerts, geotagged images saved | 1 flight day |
| **L2** | Semi-Autonomous | Drone searches autonomously, pilot confirms Y/I/X, offset landing + payload | 2-3 flight days |
| **L3** | Full Autonomous | Auto-confidence accumulation, no pilot confirmation needed | Not feasible yet |

---

## 3. Quick Start

```bash
# Clone and setup (Windows laptop)
git clone https://github.com/DimaChup/Group_Proj.git && cd Group_Proj
git checkout MainOne2
python -m venv test_env && test_env\Scripts\activate
python -m pip install -r requirements_dev.txt

# Verify lawnmower pattern (no GPS, no Cube needed)
python main.py --dry-run

# Passive watch with fake video replay
python field_tools/passive_watch.py --fake --smart-estimate
# Open http://localhost:8090

# Full simulation (needs SITL running in Mission Planner)
set DRONE_MODE=SIMULATION
python main.py --speed 5

# Run unit tests
python tests/run_all_tests.py
```

See `docs/QUICK_START.md` for Pi setup, model swapping, and more commands.

---

## 4. Architecture

```
config.py ............ All settings (auto-detects platform: Win/WSL/Pi)
vision.py ............ AI detection [INDEPENDENT] -- 3 backends: NCNN > Ultralytics > TFLite
planning.py .......... Lawnmower + spiral search pattern generator [INDEPENDENT]
utils.py ............. GPS <-> pixel math (GeoTransformer)
gps_utils.py ......... Pure GPS functions (Haversine, bearing, landing offset)
states.py ............ State enum (INIT -> SEARCH -> VERIFY -> LANDING -> DONE)
navigation.py ........ MAVLink command wrapper (arm, takeoff, goto, land, velocity)
geofence.py .......... SSSI no-fly zone enforcement (3 avoidance modes)
stream_server.py ..... MJPEG stream + telemetry JSON server
state_machine.py ..... State handler mixin (all transition logic)
main.py .............. Mission orchestrator (ties everything together)
```

### Module Independence Scores (from modularity audit)

| Module | Score | Notes |
|--------|:-----:|-------|
| vision.py | 5.0 | Exemplary. 3 backends, optional config, 34 try/except blocks |
| states.py | 5.0 | Zero dependencies. Pure data. |
| gps_utils.py | 4.8 | Pure functions, no config dependency |
| stream_server.py | 4.8 | No project imports. Thread-safe. Reusable. |
| config.py | 4.8 | KML loader, env var overrides, platform auto-detect |
| navigation.py | 4.3 | Clean wrapper. Input validation on all commands. |
| geofence.py | 3.8 | Coupled to config.py + utils.py |
| passive_watch.py | 3.3 | 3000+ lines, needs splitting |
| planning.py | 2.8 | No error handling, coupled to config.py |
| main.py | 2.5 | Orchestrator by design |
| state_machine.py | 2.0 | Mixin, tightly coupled to main.py |

**Overall project score: 3.8 / 5.0** -- see `docs/MODULARITY_AUDIT.md`

---

## 5. Key Files Map

### Core Mission Files

| File | Purpose |
|------|---------|
| `main.py` | Full autonomous mission -- state machine, search, detect, centre, land |
| `field_tools/passive_watch.py` | Passive observer: stream + AI detection + GPS estimation. ZERO commands. |
| `pi_flight.py` | Web ground station: browser dashboard + MJPEG + operator commands |
| `simple_simulator.py` | Interactive laptop MVP: keyboard flight + CV + GPS estimation + landing |
| `config.py` | All settings: altitudes, speeds, camera, connection, mode auto-detection |
| `vision.py` | Camera + AI detection (TFLite / NCNN / Ultralytics). `detect_in_image()` interface |
| `planning.py` | Lawnmower/spiral search pattern from any GPS polygon |
| `utils.py` | GeoTransformer: GPS-to-pixel and pixel-to-GPS conversion |
| `gps_utils.py` | Haversine distance, bearing, 7.5m landing offset |
| `states.py` | State enum |
| `navigation.py` | MAVLink command wrapper |
| `geofence.py` | NFZ polygon test, repulsion, speed capping |
| `stream_server.py` | MJPEG + JSON HTTP server |
| `state_machine.py` | State handler mixin for main.py |
| `spiral_planner.py` | Perimeter spiral search pattern |

### Field Tools

| File | Purpose | Safety |
|------|---------|--------|
| `field_tools/passive_watch.py` | Passive detection + SMART GPS lock + web dashboard | ZERO commands |
| `field_tools/passive_watch_clean.py` | Save RAW detection images (no overlay) with GPS | ZERO commands |
| `field_tools/capture_training.py` | Record video + photos + per-frame GPS telemetry CSV | ZERO commands |
| `field_tools/preflight.py` | Connectivity checker (camera, Cube, AI model) | ZERO commands |
| `field_tools/system_readiness.py` | Comprehensive 12-subsystem readiness check | ZERO commands |

### Tests (by category)

| Directory | Count | Purpose |
|-----------|:-----:|---------|
| `tests/flight/` | 14 | Progressive flight tests: bench (0a-0f) to autonomous (1-5) |
| `tests/hardware/` | 6 | Component checks: benchmark, GPS, buzzer, detection |
| `tests/calibration/` | 7 | FOV, lens distortion, GPS estimate, compass |
| `tests/diagnostics/` | 5 | Telemetry dashboards, camera streams |
| `tests/day_1_experiments/` | 6 | Structured data collection: altitude sweep, speed sweep, GPS accuracy |
| `tests/laptop/` | 15 | Development tools: video analysis, model comparison, synthetic CV |
| `tests/unit/` | 6 | pytest unit tests: config, states, utils, planning, vision, gps_utils |
| `tests/automated/` | 6 | Integration tests: SITL smoke, geofence, coverage simulation |
| `tests/mapping/` | 1 | SITL-to-real mapping verification |

### Training

| File | Purpose |
|------|---------|
| `training/generate_dataset_v3.py` | 700-image synthetic dataset with 10 augmentations |
| `training/colab_cells.py` | Ready-to-paste Colab training cells |
| `generate_dataset_v2.py` | v2 dataset generator (300 syn + 16 real + 50 neg at 1456x1088) |
| `tools/label_tool.py` | Label real video frames for YOLO training (`--full` for native res) |
| `tools/fov_calibrate_video.py` | FOV calibration from DJI video |

### Models

| Path | Description | Size |
|------|-------------|------|
| `best.tflite` | Active model (all scripts read this) | ~11.7 MB |
| `cv_models/sar_v2_1088/` | Best retrained model (mAP50=0.995) | TFLite + NCNN + .pt |
| `cv_models/sar_640/` | Earlier training at 640x640 | TFLite + .pt |
| `cv_models/sar_1280/` | Earlier training at 1280x1280 | TFLite + .pt |
| `models/human.tflite` | COCO YOLOv8n 80-class person detector (backup) | ~13 MB |

### Dashboard

| Path | Purpose |
|------|---------|
| `dashboard/` | React+Vite+Tailwind web app: project tracker, WBS, SE visualization |
| `dashboard/CLAUDE.md` | Dashboard-specific docs |
| Run: `cd dashboard && npm install && npm run dev` | http://localhost:5050 |

---

## 6. Search Patterns

- **Lawnmower** (default): parallel strips covering the polygon. Strip spacing = camera footprint width * (1 - overlap).
- **Spiral** (`--spiral` flag): perimeter-inward spiral pattern.
- Parameters: altitude -> FOV -> strip spacing -> overlap percentage
- Preview: `python main.py --dry-run --alt 30`
- Interactive visualizer: `python tools/pattern_visualizer_v7.py`

Key formula: `footprint_width = (altitude * SENSOR_WIDTH_MM) / FOCAL_LENGTH_MM`

At 35m altitude: footprint = 35 * 5.02 / 5.46 = 32.2m wide, with 30% overlap = 22.5m strip spacing.

---

## 7. Vision Pipeline

```
Camera frame (1456x1088 BGR)
  -> [optional: lens undistortion via cv2.remap]
  -> [resize to 640x640]
  -> AI inference (NCNN ~72ms / TFLite ~206ms / Ultralytics ~50ms GPU)
  -> Bounding box + confidence
  -> Pixel-to-GPS conversion (GeoTransformer + drone GPS + altitude + heading)
  -> Spatial clustering (inverse-variance weighting, 1/alt^2)
  -> SMART lock (greedy tightest-cluster, N samples within max_spread)
  -> Result image (hero frame + grid + map composite + stats)
```

### Three Backends

| Backend | Platform | Speed (Pi 5) | When Used |
|---------|----------|:------------:|-----------|
| NCNN | Pi (ARM optimized) | ~72ms / 14 FPS | `--backend ncnn` flag |
| TFLite | Pi (default) | ~206ms / 4.8 FPS | Auto-selected on Pi |
| Ultralytics | Laptop (PyTorch) | ~50ms GPU | Auto-selected with .pt files |

### Model Swapping

```bash
cp cv_models/sar_v2_1088/best.tflite best.tflite    # deploy best model
# or at runtime:
python main.py --model cv_models/sar_v2_1088/best.tflite
```

All models share input `[1,640,640,3]` and output `[1,5,8400]` -- true drop-in replacement.

### Training

- Current dataset (v2): 366 images (300 synthetic + 16 real + 50 negatives) at 1456x1088
- Next dataset (v3): 700 images with 10 augmentations -- see `training/generate_dataset_v3.py`
- Training on Google Colab: `imgsz=640, epochs=250, batch=16`
- Colab cells ready at `training/colab_cells.py`
- Full workflow: `docs/TRAINING_WORKFLOW_V3.md` and `docs/CV_BEST_PRACTICES.md`

---

## 8. Flight Testing Ladder

18 steps from bench to full mission. **Never skip a step.**

| Phase | Steps | What It Covers | Status |
|-------|:-----:|----------------|--------|
| **A: Bench** | 0-2 | Component health, safety systems, RC override | DONE (partial) |
| **B: First Flight** | 3-6 | GPS lock, MP AUTO waypoints, compass, waypoint script | TODO |
| **C: CV in the Air** | 7-10 | Passive CV, speed test, geotagging, centering accuracy | TODO |
| **D: Autonomous Search** | 11-12 | Fly search pattern, detect + confirm loop | TODO |
| **E: Full Mission** | 13-17 | Offset landing, payload, PLB, SSSI, full L2 | TODO |

**Currently at:** Step 1 (component health -- DONE on bench).
**Next blocker:** Step 3 (outdoor GPS 3D fix).
**Estimated total time:** 8.5 hours across 2-3 flight days.

See `docs/FLIGHT_LADDER.md` for the complete 618-line ladder with checklists.

---

## 9. Calibrations Required

**Order matters. Each depends on the previous.**

```
1. Lens distortion --> calibration_data.npz (optional, IMX296 has minimal distortion)
2. FOV / focal length --> FOCAL_LENGTH_MM in config.py (MOST IMPORTANT)
3. GPS estimate calibration --> corrected focal length
4. Ground truth validation --> CEP50, CEP95 error stats
```

| Parameter | Current Value | Source |
|-----------|:------------:|--------|
| FOCAL_LENGTH_MM | 5.46 | Calibrated 2026-03-11 (92cm visible at 1m) |
| SENSOR_WIDTH_MM | 5.02 | IMX296 datasheet |
| IMAGE_W x IMAGE_H | 1456 x 1088 | Pi camera native resolution |
| DJI video HFOV | 54.4 deg | Calibrated from 9 samples across 15-50m altitude |

See `docs/CALIBRATION_SEQUENCE.md` for step-by-step procedures.

---

## 10. Safety and Lessons Learned

### Top 8 Lessons

| ID | Lesson | Reference |
|----|--------|-----------|
| LL-01 | **Mode-fighting crash**: never send SET_MODE while pilot's RC is in another mode. RC override guard at main.py ~line 757. | `docs/LESSONS_LEARNED.md` |
| LL-02 | **IMX296 BGR**: camera outputs BGR despite RGB888 label. Do NOT add cvtColor. | `docs/LESSONS_LEARNED.md` |
| LL-03 | **TFLite bbox coords**: can be pixel (0-640) or normalised (0-1). PIXEL_COORD_THRESHOLD check in vision.py. | `docs/LESSONS_LEARNED.md` |
| LL-04 | **calibration_data.npz corruption**: empty file mangles all frames. Delete if < 1KB. | `docs/LESSONS_LEARNED.md` |
| LL-05 | **GPS timing lag**: 100-200ms latency = 1m error at 5m/s. Average from multiple passes. | `docs/LESSONS_LEARNED.md` |
| LL-06 | **DISARM_DELAY must be 0**: ArduCopter auto-disarms after 10s if still on ground. | `docs/LESSONS_LEARNED.md` |
| LL-07 | **Python 3.13 on Pi**: tflite-runtime broken (use ai-edge-litert), pyserial broken (use mavproxy UDP). | `docs/LESSONS_LEARNED.md` |
| LL-08 | **Geofence sign conventions**: cv2.pointPolygonTest positive = INSIDE. Negate repulsive offsets. | `docs/LESSONS_LEARNED.md` |

### Safety Hierarchy

```
RC pilot  >  kill switch (STABILIZE)  >  RC override guard  >  Python script  >  geofence
```

### Pre-Flight Non-Negotiables

- [ ] DISARM_DELAY = 0 in Mission Planner params
- [ ] RC kill switch tested with script running
- [ ] GCS failsafe = RTL (FS_GCS_ENABLE = 1)
- [ ] Battery failsafe configured (FS_BATT_ENABLE)
- [ ] GPS 3D fix (fix_type >= 3, sats >= 6)
- [ ] Confidence threshold >= 0.4 for first flight
- [ ] Speed <= 6 m/s for first flight

See `docs/MISTAKES_TO_AVOID.md` for 16 catalogued mistakes with protections.

---

## 11. Sim vs Real Differences

**7 files have MODE branches**, 8 core modules are mode-agnostic.

| Risk | Issue | Severity |
|:----:|-------|----------|
| 1 | GPS noise: 2-5m CEP vs perfect SITL GPS | HIGH, CERTAIN |
| 2 | Model may miss detections in real outdoor conditions | HIGH, LIKELY |
| 3 | Motion blur at speed | MEDIUM, LIKELY |
| 4 | Wind affects centering and GPS estimation | MEDIUM, LIKELY |
| 5 | Lower FPS (5 vs 30) means fewer detection opportunities | MEDIUM, LIKELY |
| 6 | Baro drift affects landing detection | MEDIUM, POSSIBLE |

**Key mitigation**: `--center-verify` for GPS averaging, `--smart-detect` for consecutive frame filtering.

See `docs/SIM_VS_REAL_MAPPING.md` for the complete 222-line analysis.

---

## 12. Design Decisions Log

| ID | Decision | Rationale |
|----|----------|-----------|
| DD-01 | MJPEG over H.264 streaming | Most reliable for field ops, works in any browser, matches 3-5 FPS inference rate |
| DD-02 | Headless operation via SSH | PuTTY + browser dashboard, no monitor needed on Pi |
| DD-03 | Dual/triple-backend vision | Same `detect_in_image()` interface: NCNN > Ultralytics > TFLite |
| DD-04 | mavproxy UDP bridge | Bypasses Python 3.13 pyserial bug, adds Mission Planner TCP |
| DD-05 | Camera shares one owner | One process owns picamera2, others get stream via MJPEG |
| DD-06 | IMX296 BGR fix | No cvtColor -- empirically tested all 6 channel permutations |
| DD-07 | Progressive test strategy | Numbered scripts 0a-5 in tests/flight/, never skip a step |
| DD-08 | Inverse-variance GPS weighting | 1/alt^2 weighting, 10x centrality bonus for frame-centre detections |
| DD-09 | 7.5m offset landing | Centre of 5-10m safe zone, consistent "north" direction |
| DD-10 | NFZ geofence: 3 avoidance modes | Speed-cap (`--nfz-carrot`) recommended: smooth, same path, just slower |
| DD-11 | Threaded inference | Stream at 30fps, detect in background thread, ~200ms overlay lag |
| DD-12 | SmartEstimator greedy cluster | Tightest N points for GPS lock, deterministic, no hyperparameters |
| DD-13 | NCNN backend (3rd option) | 4.5x faster than TFLite on Pi 5 (72ms vs 327ms) |
| DD-14 | Zero-command passive mode | passive_watch.py sends exactly zero MAVLink commands |
| DD-15 | SMART result image composite | Hero frame + grid + map + stats in one image |
| DD-16 | Altitude-dependent observation quality | Full weighting model with centrality bonus |
| DD-17 | CLI flags reflected in browser UI | Template injection + /stats JSON endpoint, live-adjustable |

Full rationale: `docs/DESIGN_DECISIONS.md`

---

## 13. CLI Flags Reference

### main.py

```
--dry-run              No arming/flying/GPS. Print waypoints, save pattern image.
--headless             No cv2 windows. Auto-enabled on Pi when $DISPLAY is empty.
--alt <m>              Override search altitude (default 35m).
--speed <factor>       SITL speedup (default 1).
--model <path>         TFLite model path (default best.tflite).
--transit <file>       Transit waypoints JSON (default flight_plans/transit.json).
--beacon-delay <s>     Auto-trigger PLB redirect after N seconds (default 0 = off).
--smart-detect         Require consecutive confirmed frames before investigating.
--center-verify        GPS-average target position after centering, before VERIFY.
--no-nfz               Disable SSSI geofence.
--no-stream            Disable MJPEG stream server (port 8090).
--conf <float>         Override confidence threshold.
--spiral               Use spiral search pattern instead of lawnmower.
--nfz-carrot           Speed-cap geofence mode (recommended).
--nfz-repel            Repulsive force geofence mode.
--nfz-slow             Velocity-clamped geofence mode.
```

### passive_watch.py

```
--fake                 Replay DJI video instead of live camera.
--fake-video <path>    Path to video file for fake mode.
--fake-srt <path>      Path to SRT telemetry for fake mode.
--smart-estimate       Enable SMART GPS estimation with greedy clustering.
--smart-min <N>        Minimum cluster size for lock (default 5).
--smart-radius <M>     Maximum spread in metres for lock (default 1.0).
--smart-dir <dir>      Output directory for SMART results.
--conf <float>         Confidence threshold (default 0.2).
--class-filter <cls>   Only save detections matching class name.
--model <path>         Override model path.
--simple-names         Clean filenames with estimated GPS (for training data).
--no-mavlink           Run without Cube connection.
--no-save              Don't save detection images.
--no-stream            Disable web stream.
--port <N>             Stream port (default 8090).
```

---

## 14. Colleague Integration (Passive Detection)

`passive_watch.py` sends ZERO MAVLink commands. Safe to run during any flight.

```bash
# On Pi (Terminal 1): start mavproxy
sudo /opt/mavlink/mavlink-venv/bin/mavproxy.py \
  --master=/dev/ttyAMA0 --baudrate=921600 --streamrate=10 \
  --out=udpout:127.0.0.1:14550 --out=tcpin:0.0.0.0:5762

# On Pi (Terminal 2): start passive watch
source pienv/bin/activate && cd ~/sar-drone
python field_tools/passive_watch.py --headless --smart-estimate --simple-names

# On laptop browser:
# http://PI_IP:8090
```

**Output**: SMART result images with map panel (SSSI red + search area yellow + magenta star at target GPS), detection thumbnails, confidence stats.

**Terminal keys**: N=investigate, Y=confirm, I=interest, X=false positive, L=land, C=clear all.

See `docs/COLLEAGUE_CHECKLIST.md` and `docs/VISION_PIPELINE_FOR_COLLEAGUE.md`.

---

## 15. Report Writing

| Deliverable | Weight | Format | Location |
|-------------|:------:|--------|----------|
| D4: Flight Readiness Review | 10% | Presentation | ACTIVE |
| D5: Flight Test | 20% | Demo + data | UPCOMING |
| D6: Final Report (group) | 30% | 15-page report | `report/main.tex` |
| D7: Peer Assessment (individual) | 12.5% | 5-page reflective | `report/personal/` |

Chat prompts ready:
- `docs/REPORT_CHAT_PROMPT.md` -- general report writing
- `docs/REPORT_CHAT_PROMPT_D6.md` -- D6 specific
- `docs/REPORT_CHAT_PROMPT_D7.md` -- D7 specific

Evidence sources: simulation logs, flight data CSVs, detection images, config.py values, benchmark results, dashboard screenshots. See `docs/PROCESS_MAP.md` Section 5 for full evidence mapping.

---

## 16. Known Issues and Gaps

### Code Issues

| Issue | Severity | Notes |
|-------|----------|-------|
| GPS: no multipath filter, no lag compensation | HIGH | ~13m worst case, CEP50=2.3m from DJI analysis |
| Landing offset (7.5m) hardcoded in 3 files | MEDIUM | Should be `config.LANDING_OFFSET_M` |
| state_machine.py circular import | LOW | Lazy `import main` for 3 values |
| planning.py: no error handling | MEDIUM | Division by zero possible from bad config |
| passive_watch.py: 3000+ lines | LOW | Should extract GPS estimator + overlay renderer |
| 2 geofence unit test edge cases | LOW | Known, non-critical |

### Data Gaps

| Gap | Impact | Fix |
|-----|--------|-----|
| 14% real images in dataset (target 25-50%) | Detection may fail outdoors | Label 50+ frames via `tools/label_tool.py --full` |
| Zero outdoor flight data | Cannot validate detection altitude | Step 7 in flight ladder |
| No GPS noise floor measurement | Cannot set waypoint acceptance radius | `tests/day_1_experiments/gps_drift.py` |

### Hardware Gaps

| Gap | Impact |
|-----|--------|
| Payload servo not integrated | Cannot demonstrate R07 (delivery) |
| No rangefinder for AGL altitude | Baro-only, may drift |
| WiFi range at operational distance untested | Stream may drop at 100m+ |

---

## 17. Documentation Index

### Core Documents

| File | Purpose |
|------|---------|
| `MAIN.md` | THIS FILE -- master entry point |
| `CLAUDE.md` | Project ground truth, session log, full context for LLM sessions |
| `docs/ARCHITECTURE.md` | System overview, hardware, evolving diagrams |
| `docs/DESIGN_DECISIONS.md` | DD-01 through DD-17 with full rationale |
| `docs/PROJECT_STATUS.md` | L1/L2/L3 levels, WBS completion, stepping stones |
| `docs/L2_CRITICAL_PATH.md` | 13-step critical path with dependency graph |

### Flight and Safety

| File | Purpose |
|------|---------|
| `docs/FLIGHT_LADDER.md` | 18-step progressive test ladder with checklists |
| `docs/FLIGHT_DAY_CHECKLIST.md` | Printable flight day checklist |
| `docs/CALIBRATION_SEQUENCE.md` | Calibration order: lens -> FOV -> GPS -> ground truth |
| `docs/CALIBRATION_GUIDE.md` | Camera and FOV calibration procedures |
| `docs/PREFLIGHT_SAFETY.md` | Pre-flight safety verification |
| `docs/MISTAKES_TO_AVOID.md` | 16 catalogued mistakes with protections |
| `docs/LESSONS_LEARNED.md` | 8 hard-won lessons (LL-01 through LL-08) |
| `docs/FIELD_QUICK_REF.md` | Copy-paste commands for flight day without internet |

### Technical References

| File | Purpose |
|------|---------|
| `docs/QUICK_START.md` | 5-minute setup cheatsheet |
| `docs/PI_SETUP.md` | Step-by-step Raspberry Pi setup |
| `docs/CONNECTIVITY.md` | Connection debugging guide |
| `docs/TOOLS_INVENTORY.md` | All 124 scripts with purpose and safety level |
| `docs/TEST_GUIDE.md` | All test scripts: what, when, why, dependencies |
| `docs/DEPENDENCIES.md` | Script dependency graph, platform compatibility |
| `docs/SIM_VS_REAL_MAPPING.md` | Every SIMULATION vs REAL code path divergence |
| `docs/MODULARITY_AUDIT.md` | Code quality scores per module |
| `docs/NEEDS_VS_CAPABILITIES.md` | Sim 7.7/10 vs Real 2.1/10 scoring matrix |
| `docs/PROCESS_MAP.md` | 7 workflow pipelines (dev, training, calibration, flight, report) |
| `docs/MAVLINK_COMMANDS.md` | MAVLink command reference |
| `docs/MAVLINK_MAPPING.md` | Command-to-code mapping |

### Vision and Training

| File | Purpose |
|------|---------|
| `docs/CV_GUIDE.md` | Vision system overview, optimization stages |
| `docs/CV_BEST_PRACTICES.md` | Dataset composition, augmentation ranking, export |
| `docs/TRAINING_GUIDE.md` | Complete retraining workflow (Colab, dataset_v2) |
| `docs/TRAINING_WORKFLOW_V3.md` | Dataset v3 training workflow |
| `docs/DATASET_V3_REPORT.md` | Dataset v3 design rationale |
| `docs/VIDEO_ANALYSIS.md` | DJI video analysis tools, FOV calibration, SRT sync |
| `docs/VISION_PIPELINE_FOR_COLLEAGUE.md` | Step-by-step vision pipeline for teammate |

### Colleague and Team

| File | Purpose |
|------|---------|
| `docs/COLLEAGUE_CHECKLIST.md` | Onboarding checklist for new team members |
| `docs/TEAM_PLAN.md` | Team workstreams and responsibilities |
| `docs/GROUP_STATUS.md` | Group project status, meetings |
| `docs/REPORT_CHAT_PROMPT.md` | General report writing prompt |
| `docs/REPORT_CHAT_PROMPT_D6.md` | D6 (final report) prompt |
| `docs/REPORT_CHAT_PROMPT_D7.md` | D7 (peer assessment) prompt |

### Design Deep-Dives

| File | Purpose |
|------|---------|
| `docs/DESIGN_DETECTION.md` | Detection pipeline design |
| `docs/DESIGN_GEOFENCE.md` | Geofence implementation design |
| `docs/DESIGN_PATH_PLANNING.md` | Search pattern algorithm design |
| `docs/DESIGN_STATE_MACHINE.md` | State machine design |
| `docs/DESIGN_VISION.md` | Vision system design |
| `docs/DESIGN_SUMMARY.md` | Design summary for report |
| `docs/SAR_COMPARISON.md` | Industry/academic SAR comparison for report |

### Blueprints (line-range maps for files > 500 lines)

| File | Maps |
|------|------|
| `docs/main_blueprint.md` | main.py (908 lines) |
| `docs/simple_simulator_blueprint.md` | simple_simulator.py (2508 lines) |
| `docs/pi_flight_blueprint.md` | pi_flight.py (1097 lines) |
| `docs/passive_watch_blueprint.md` | passive_watch.py (752+ lines) |
| `docs/MASTER_BLUEPRINT.md` | All modules overview |

### Other

| File | Purpose |
|------|---------|
| `docs/IMPROVEMENTS.md` | Improvement roadmap |
| `docs/FUTURE_WORK.md` | Future work items |
| `docs/NICE_TO_HAVE.md` | Backlog with impact/effort scoring |
| `docs/SESSION_ARCHIVE.md` | Archived session logs (2026-02-16 to 2026-02-20) |
| `docs/TODO.md` | Active TODO items |
| `docs/OPERATOR_GUIDE.md` | Operator instructions |
| `docs/LAUNCH_GUIDE.md` | Launch procedures |

### Memory Files (persistent across sessions)

| File | Purpose |
|------|---------|
| `.claude/projects/.../memory/MEMORY.md` | Key facts, Pi IP, model swapping, workflows |
| `.claude/projects/.../memory/benchmarks.md` | Pi benchmark results |
| `.claude/projects/.../memory/cv-speed-research.md` | CV speed improvement options |
| `.claude/projects/.../memory/gps-timing-lag.md` | GPS lag analysis |
| `.claude/projects/.../memory/geofence-signs.md` | Geofence sign conventions |

---

## 18. Git Strategy

| Item | Value |
|------|-------|
| Current branch | `Working8.Robbin3` |
| Backup branch | `Working8.Robbin2` (committed at 41e713c) |
| Main branch | `MainOne2` |
| Remote | `https://github.com/DimaChup/Group_Proj.git` |
| Strategy | Feature branches, merge when proven. Never break main. |
| Workflow | Edit on laptop -> simulate -> push -> pull on Pi -> test hardware |
| Rollback | `git log --oneline -20` then `git checkout <hash>` |
| Branch cleanup | ~42 local branches, many dead. Clean after flight day. |

---

*This document is the entry point. For deep dives, follow the links to specific docs. For LLM sessions, read `CLAUDE.md` for full project context and session history.*
