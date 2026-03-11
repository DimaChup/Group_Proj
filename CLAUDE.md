# Project Context — SAR Drone (Ground Truth Document)

**Read this first. This is the single source of truth for the project.**
**Update this document as the project progresses.**

---

## What This Is

University of Bristol MSc project (AENGM0074). Team of 5.
Autonomous SAR (Search and Rescue) drone that:
1. Takes off
2. Flies a lawnmower search pattern
3. Uses onboard AI (YOLOv8 / TFLite) to detect a casualty/dummy
4. Centres on target, descends, operator confirms Y/N
5. Lands near target (or resumes search)

## Current State

**SIMULATION: WORKING** — Full mission runs on laptop with SITL + simulated camera.
The state machine, search pattern, detection, centering, descent, verification, and
landing all work end-to-end in simulation.

**PI HARDWARE: TESTED AND WORKING** — Camera, AI detection, and Cube connection all
verified on Raspberry Pi 5 (Python 3.13). Requires mavproxy UDP bridge for Cube
communication (Python 3.13 + pyserial serial reads are broken).

### What Works
- Full state machine: INIT → CONNECTING → ARMING → TAKEOFF → SEARCH → CENTERING → DESCENDING → VERIFY → APPROACH → LANDING → DONE
- Lawnmower search pattern generation from any polygon
- AI detection with dual backend (Ultralytics on laptop, TFLite on Pi)
- Interactive polygon drawing in both SIMULATION and REAL mode
- Config auto-detection (SITL on laptop, mavproxy UDP bridge on Pi)
- Manual override (M key) and RC kill switch support
- Preflight connectivity checker (preflight.py)
- Pi camera (picamera2) working at 640x480 with correct colors
- **Camera color fix applied**: IMX296 outputs BGR despite RGB888 label — no cvtColor conversion needed
- TFLite inference on Pi: ~256ms avg, 3.9 FPS, 50/50 detection at 0.966 confidence
- Cube connection on Pi via mavproxy bridge (921600 baud, udpout/udpin)
- ai-edge-litert replaces tflite-runtime on Python 3.13
- Mission Planner connects to Cube via mavproxy TCP bridge (tcpin:0.0.0.0:5762)
- Passive flight script ready (pi_passive_flight.py — pilot flies RC, Pi detects + buzzer)
- **simple_simulator.py**: interactive MVP — keyboard flight + CV + GPS estimation + offset landing
  - GPS centering (C), visual servo (V), GPS lock (G), 7.5m offset landing (L), data recording (B)
  - Multi-target support, spatial clustering, inverse variance weighting, Kalman filter
  - Pilot classification: Y=dummy, I=interest, X=false positive
  - Simulates GPS drift, camera shake, CV throttle, TFLite backend
  - End-to-end mission tested: flyover → centre → lock → land 7.5m away
- **pi_flight.py**: web-based ground station for real flights (browser dashboard)
  - MJPEG video stream, 2D GPS grid, detection clusters, command buttons (N/Y/I/X/L)
  - Works headless (no cv2.imshow) — all UI through browser at http://PI_IP:8090
  - Same GPS estimation math as simple_simulator.py
  - Tested in SIMULATION on laptop, ready for REAL mode on Pi

### What's Not Done Yet
- [x] Pi setup (OS, venv, dependencies)
- [x] Camera tested on Pi
- [x] TFLite inference tested on Pi
- [x] Cube wired to Pi and tested
- [x] Camera color fix (BGR/RGB issue resolved)
- [x] Mission Planner connected to Cube via Pi
- [ ] Test detection with corrected colors on Pi (push code, pull, test with dummy)
- [ ] Outdoor GPS fix test
- [ ] Manual flight with passive detection (tests/flight/1_passive_flight.py)
- [ ] Full autonomous bench test (main.py, no props)
- [ ] **BEFORE FLIGHT DAY: Prepare alternative CV models on laptop**
  - [ ] Export COCO person detector: `yolo export model=yolov8n.pt format=tflite`
  - [ ] Export INT8 quantized: `yolo export model=best.pt format=tflite int8=True`
  - [ ] Optionally retrain on better data (real photos of dummy)
  - [ ] Copy all .tflite files to `models/` folder, ready to swap on Pi
  - [ ] On flight day: swap models with `--model` flag or `cp models/X.tflite best.tflite`
  - [x] `models/best2.tflite` placeholder created (replace with retrained model)
  - [x] `--model` and `--dry-run` flags added to main.py

### Flight Testing Steps (follow in order)
Each step builds trust before adding risk. **Never skip a step.**

1. **[ ] Mission Planner AUTO waypoints (no custom code)**
   - Upload a simple square pattern (4 waypoints) in Mission Planner at 10-15m altitude
   - Switch to AUTO on RC, drone flies the pattern, RTLs
   - Proves: Cube, GPS, motors, RTL all work. Your code not involved.
   - Kill switch: RC mode switch to STABILIZE/LOITER at any time

2. **[ ] Waypoint test script (no CV)** — `tests/flight/2_waypoint_test.py`
   - Your code arms, takes off to 10m, flies 3-4 GPS waypoints in GUIDED mode, lands
   - No camera, no detection, no decision-making
   - Proves: your mavlink commands (arm, takeoff, goto, land) work on real hardware
   - Kill switch: RC override always active

3. **[ ] Manual flight + passive CV** — `tests/flight/1_passive_flight.py`
   - Pilot flies manually on RC
   - Pi runs camera + AI, logs detections, buzzer beeps — sends ZERO commands
   - Review log after: did it detect the dummy? At what altitude/distance?
   - Proves: CV works in real outdoor conditions, calibrates detection altitude

4. **[ ] Autonomous search + CV logging only (no action)**
   - Run main.py but with detection in "log only" mode — CV detects and logs but never triggers descent/landing
   - Drone flies the search pattern autonomously, comes home after
   - Review log: would it have found the target? Where? False positives?
   - Proves: full search pattern works, CV detects from altitude, no dangerous surprises

5. **[ ] Full autonomous mission**
   - Everything enabled: search, detect, centre, descend, verify, land
   - Operator confirms Y/N at verify stage
   - This is the real thing

### CV Optimization (Future Work)
- [ ] **Lower confidence threshold** — try 0.3 or 0.25 (currently 0.4 in vision.py) to catch more detections at cost of false positives
- [ ] **Retrain with real camera images** — current model trained on synthetic composites (map.jpg + dummy.png). Capture real photos of dummy in grass at various altitudes and retrain
- [x] **Camera color fix** — IMX296 outputs BGR despite RGB888 label. Removed incorrect cvtColor conversion. Colors now correct.
- [ ] **Larger model** — try YOLOv8s instead of YOLOv8n (more accurate, slower). Benchmark on Pi with pi_3_benchmark.py
- [ ] **Resolution tuning** — run pi_9_resolution_test.py to find best resolution vs speed vs detection tradeoff
- [ ] **Motion blur handling** — test detection quality at different drone speeds. Consider shorter exposure / higher shutter speed in picamera2 config
- [ ] **Altitude calibration** — run pi_cv_test.py on Pi to find max reliable detection altitude, adjust TARGET_ALT in config.py
- [ ] **Data augmentation** — add brightness, contrast, blur, rotation variations to training pipeline (generate_dataset.py)

## Project File Structure

```
v3/
├── CLAUDE.md                  ← THIS FILE — project ground truth for LLM sessions
├── .gitignore
├── .dockerignore
├── Dockerfile.pi-test         ← Docker-based Pi environment testing
│
├── config.py                  ← ALL settings: altitudes, speeds, camera, connection, mode
├── states.py                  ← State enum (SEARCH, VERIFY, LANDING, etc.)
├── utils.py                   ← Geo math: GPS ↔ pixel conversion (GeoTransformer)
├── vision.py                  ← Camera + AI detection [INDEPENDENT MODULE]
│                                 Dual backend: Ultralytics (laptop) / TFLite (Pi)
│                                 Interface: detect_in_image(frame) → (found, x, y, conf)
├── planning.py                ← Lawnmower search pattern generator [INDEPENDENT MODULE]
├── main.py                    ← Mission orchestrator — the state machine, ties everything
├── simple_simulator.py         ← Interactive MVP: keyboard flight + CV + GPS estimation + landing
│                                 Keys: SPACE=arm WASD=fly C=gps V=vision G=lock B=rec L=land
│                                 Flags: --fps 4 --tflite --gps-drift 3 --shake 5
├── pi_flight.py               ← Web ground station: browser dashboard + MJPEG stream + commands
│                                 Works headless (Pi) or laptop. http://localhost:8090
│                                 Keys in browser: N=investigate Y=confirm I=interest X=FP L=land
├── passive_watch.py           ← Passive camera observer: stream + AI detection + GPS estimation
│                                 ZERO commands. Saves detection photos + JSON metadata
│                                 http://PI_IP:8090 — use during manual RC flight
├── capture_training.py        ← Record video + photos for model retraining
│                                 ZERO commands. SPACE=photo V=video Q=quit
│                                 http://PI_IP:8091 — training data collection
├── simulation.py              ← Laptop-only sim: map.jpg + simulated drone camera view
├── preflight.py               ← Standalone connectivity checker (camera, Cube, AI model)
│
├── best.tflite                ← AI model file (~3.3MB, YOLOv8n exported to TFLite)
│                                 All scripts read this file. Swap model by overwriting:
│                                 cp models/human.tflite best.tflite
├── models/                    ← Alternative TFLite models for flight day testing
│   ├── custom_yolov8n.tflite  ← Copy of original best.tflite (our custom dummy detector)
│   ├── human.tflite           ← COCO YOLOv8n person detector (~13MB, 80 classes, backup)
│   └── best2.tflite           ← Placeholder (replace with retrained model)
├── map.jpg                    ← Satellite image for simulation (~12MB)
├── dummy.png                  ← Dummy/casualty image for dataset generation + bench test
├── generate_dataset.py        ← Creates synthetic training data from map.jpg + dummy.png
├── requirements_dev.txt       ← Windows laptop: full pip freeze (~90 packages, exact versions)
├── requirements_linux.txt     ← WSL/Linux laptop: full pip freeze (no Windows-specific packages)
├── requirements_pi.txt        ← Pi: pymavlink, opencv-headless, numpy<2, tflite-runtime
│
├── dashboard/                 ← Standalone React web app — project tracker + SE visualization
│   ├── CLAUDE.md              ← Dashboard-specific docs (how to run, file map, data editing)
│   ├── package.json           ← npm install && npm run dev → http://localhost:5050
│   └── src/pages/             ← GP v2 snapshot + Mission WBS (copied from Orgnaiser)
│                                 Edit wbs-data.ts to update task progress
│                                 Edit group-project-v2-data.ts for team/SE/approaches
│
├── docs/
│   ├── ARCHITECTURE.md        ← System overview, evolving diagrams, hardware checklist
│   ├── PI_SETUP.md            ← Step-by-step Pi setup and testing guide
│   ├── CV_GUIDE.md            ← Vision system, optimization stages, model swapping
│   ├── NEXT_STEPS.md          ← Phase-by-phase development plan
│   ├── CONNECTIVITY.md        ← Connection debugging guide
│   ├── PREFLIGHT_CHECKLIST.md ← Pre-flight safety checks
│   ├── TEAM_PLAN.md           ← Team workstreams and responsibilities
│   ├── FLIGHT_DAY_CHECKLIST.md ← Printable flight day checklist (single document, follow top to bottom)
│   ├── FLIGHT_DAY_TESTS.md    ← Master test reference: all scripts, protocols, troubleshooting
│   ├── FIRST_FLIGHT.md        ← First flight plan with progressive steps
│   ├── TRAINING_GUIDE.md      ← Model training/dataset guide
│   ├── DESIGN_DECISIONS.md    ← Design rationale documentation
│   ├── SIMULATOR.md           ← Simulator documentation
│   ├── SIMULATOR_GUIDE.md     ← Simulator user guide
│   ├── GROUP_STATUS.md        ← Group project status
│   └── ROADMAP.md             ← Full 10-phase development history
│
├── _archive/                  ← Old/junk files (gitignored, not deleted)
│
└── tests/                     ← All test scripts, categorized
    ├── hardware/              ← DOES THIS PART WORK? (individual component checks)
    │   ├── benchmark.py       ← Inference speed (50 runs, timing report)
    │   ├── cv_benchmark.py    ← Detection rate, speed, blur simulation
    │   ├── buzzer_test.py     ← Buzzer melody test via MAVLink
    │   ├── gps_test.py        ← GPS diagnostics with fix tracking
    │   ├── gps_health.py      ← Step-by-step GPS verification
    │   └── detection_snapshot_test.py ← Single-frame detection on static image
    ├── flight/                ← CAN IT FLY? (numbered by progression: bench → autonomous)
    │   ├── 0a_cube_commands.py   ← Bench: test individual commands (mode, arm)
    │   ├── 0b_bench_mission.py   ← Bench: full command sequence (no props)
    │   ├── 0c_feedback_test.py   ← Bench: vision→GPS pipeline (no commands)
    │   ├── 1_passive_flight.py   ← Manual RC, CV watches (ZERO commands)
    │   ├── 2_waypoint_test.py    ← Fly GPS waypoints (no CV)
    │   ├── 3_auto_detect.py      ← AUTO + AI → GUIDED hover
    │   └── 4_detect_and_center.py ← Autonomous pattern + center
    ├── diagnostics/           ← IS IT WORKING? (monitoring & debug)
    │   ├── diagnostics.py     ← Multi-view connectivity + camera + telemetry dashboard
    │   ├── cube_monitor.py    ← Live Cube telemetry dashboard
    │   ├── camera_stream.py   ← MJPEG stream to ground station
    │   ├── camera_stream_fast.py ← Threaded MJPEG stream
    │   └── camera_stream_h264.py ← H.264/HLS stream (FFmpeg)
    ├── calibration/           ← ARE THE NUMBERS RIGHT? (FOV, lens, camera)
    │   ├── fov_calibrate.py   ← Bench FOV calibration with ruler (comprehensive)
    │   ├── fov_test_simple.py ← Simple FOV test (single measurement)
    │   ├── alt_test.py        ← FOV calibration at real altitude
    │   ├── lens_calibrate.py  ← Lens distortion calibration (checkerboard → undistort)
    │   └── gps_ground_truth.py ← GPS ground truth calibration (CV estimate vs actual)
    ├── day_1_experiments/     ← WHAT'S THE DATA? (structured experiments, CSV output)
    │   ├── altitude_sweep.py  ← Detection rate vs altitude (10-30m buckets)
    │   ├── speed_sweep.py     ← Detection rate vs speed + blur metric
    │   ├── gps_accuracy.py    ← GPS estimate error vs known dummy position
    │   ├── gps_drift.py       ← GPS noise floor (CEP50, CEP95)
    │   ├── model_compare.py   ← Benchmark all .tflite models
    │   └── detection_log.py   ← General catch-all flight logger
    └── laptop/                ← DEVELOPMENT ONLY (laptop-only tests)
        ├── test_camera.py     ← Camera preview + snapshot
        ├── test_cv.py         ← AI model loading + detection test
        ├── test_cube.py       ← Cube heartbeat, GPS, attitude, battery
        ├── test_all.py        ← Full system connectivity check
        ├── test_tflite.py     ← TFLite inference on laptop
        ├── debug_tflite.py    ← Raw TFLite model output inspection
        └── cv_test_synthetic.py ← Synthetic image CV benchmark
```

## Architecture

```
config.py ............. All settings (altitudes, speeds, camera, connection)
states.py ............. State enum (SEARCH, VERIFY, etc.)
utils.py .............. Geo math (GPS <-> pixels)
vision.py ............. Camera + AI detection [INDEPENDENT — dual backend]
planning.py ........... Lawnmower search pattern [INDEPENDENT]
main.py ............... Mission orchestrator (state machine, ties everything together)
simple_simulator.py ... Interactive MVP (keyboard flight + CV + GPS est + landing)
pi_flight.py .......... Web ground station (browser dashboard + commands)
passive_watch.py ...... Passive observer (stream + detection + GPS estimation, ZERO commands)
capture_training.py ... Training data capture (video + photos, ZERO commands)
simulation.py ......... Laptop-only simulation (map + simulated drone view)
preflight.py .......... Connectivity checker (standalone tool)
generate_dataset.py ... Synthetic training data generator
tests/ ................ All test scripts (hardware/, flight/, diagnostics/, calibration/, laptop/)
```

### Key Design Decisions
- **vision.py is the ONLY file that touches CV/AI.** Everything else calls `detect_in_image(frame)` → `(found, x, y, conf)`. You can change the model, preprocessing, backend without touching any other file.
- **config.py auto-detects hardware.** Serial port → real Cube. No serial → SITL. Env var overrides everything. No code changes between laptop and Pi.
- **Same main.py for simulation and real.** The MODE flag only changes camera source and connection string. State machine logic is identical.
- **Interactive polygon drawing in REAL mode.** If map.jpg available, shows map for drawing. If headless (Pi), falls back to SEARCH_AREA_GPS in config.py.

### Development Workflow
- **Always develop and edit code on the laptop** (better tools, faster iteration, simulation)
- **Test in simulation on laptop first**, then push to GitHub, then pull on Pi and test on hardware
- **Never edit code directly on Pi** — the laptop is the single source of truth for code changes
- **If adding a new import/dependency**, also add it to `requirements_pi.txt` (or confirm it already exists on Pi)
- The architecture (config.py auto-detect, vision.py dual backend) means the same code runs on both platforms without changes

## File Locations

| File | Purpose | Notes |
|------|---------|-------|
| best.tflite | AI model (YOLOv8n exported to TFLite) | ~6MB, tracked in git |
| best.pt | YOLO weights (full, laptop only) | In .gitignore (large) |
| map.jpg | Satellite image for simulation | ~12MB, tracked in git |
| dummy.png | Test dummy image | For generate_dataset.py and bench testing |
| flight_log.csv | Runtime log | In .gitignore (changes every run) |
| requirements_dev.txt | Windows laptop dependencies | Full pip freeze (~90 packages, exact versions) |
| requirements_linux.txt | WSL/Linux laptop dependencies | Full pip freeze (Linux-compatible) |
| requirements_pi.txt | Pi dependencies | 4 packages: pymavlink, opencv-headless, numpy<2, tflite-runtime |

## How to Run

### Dry-run (no GPS, no Cube, no flying)
```bash
python main.py --dry-run                           # verify lawnmower pattern
python main.py --dry-run --model models/best2.tflite  # verify with alt model
```

### Simulation (laptop)
```bash
# Need: SITL running (Mission Planner or mavproxy), venv activated
set DRONE_MODE=SIMULATION      # Windows (cmd)
# export DRONE_MODE=SIMULATION  # Linux/WSL
python main.py
python main.py --model models/best2.tflite    # with alternate model
```

### Real mode on laptop (webcam + SITL)
```bash
set DRONE_MODE=REAL
python main.py
# Point webcam at printed dummy
```

### On Pi (future)
```bash
source pienv/bin/activate
cd ~/sar-drone
python main.py                 # config.py auto-detects Cube on /dev/ttyAMA0
```

## Recreating the Environment

Three platforms, three approaches. All pull from the same GitHub repo.

### Windows (Laptop — Development)

```bash
# 1. Clone the repo
git clone https://github.com/DimaChup/Group_Proj.git
cd Group_Proj
git checkout MainOne4

# 2. Create venv
python -m venv venv

# 3. Activate
venv\Scripts\activate

# 4. Install dependencies (full freeze — exact versions that work)
python -m pip install -r requirements_dev.txt

# 5. Verify
python -c "import cv2; print('OpenCV:', cv2.__version__)"
python -c "import ultralytics; print('Ultralytics:', ultralytics.__version__)"
python -c "import numpy; print('NumPy:', numpy.__version__)"

# 6. Test simulation
set DRONE_MODE=SIMULATION
python main.py
```

**Known issue**: On Windows, use `python -m pip` instead of `pip` if pip.exe gives
"Fatal error in launcher". Also use `cmd /c "python -m pip freeze > file.txt"` when
freezing — PowerShell's `>` creates UTF-16 which pip can't read.

### WSL / Linux (Simulation only — no webcam access)

```bash
# 1. Clone (or access Windows files via /mnt/c/)
git clone https://github.com/DimaChup/Group_Proj.git
cd Group_Proj
git checkout MainOne4

# 2. Create venv
python3 -m venv venv
source venv/bin/activate

# 3. Install (use Linux freeze, or install top-level packages)
pip install -r requirements_linux.txt
# OR if no freeze file: pip install pymavlink opencv-python-headless matplotlib numpy ultralytics

# 4. Verify
python -c "import cv2; print('OpenCV:', cv2.__version__)"
python -c "import ultralytics; print('Ultralytics:', ultralytics.__version__)"

# 5. Test simulation only (WSL can't access laptop webcam for real mode)
DRONE_MODE=SIMULATION python main.py
```

### Docker (Pi environment simulation)

```bash
# From project directory (WSL or Windows with Docker Desktop)
docker build -f Dockerfile.pi-test -t pi-test .
docker run pi-test
# Pass: prints "Model loaded: True"
# Tests: TFLite loads model on slim Linux with Pi-level dependencies
```

### Raspberry Pi (Production)

```bash
# 1. Clone
git clone https://github.com/DimaChup/Group_Proj.git ~/sar-drone
cd ~/sar-drone
git checkout MainOne4

# 2. Create venv (--system-site-packages needed for picamera2)
python3 -m venv --system-site-packages pienv
source pienv/bin/activate

# 3. Install Pi-specific lightweight deps (NOT requirements_dev.txt)
pip install -r requirements_pi.txt

# 4. Verify
python -c "import cv2; print('OpenCV:', cv2.__version__)"
python -c "import numpy; print('NumPy:', numpy.__version__)"
python -c "from tflite_runtime.interpreter import Interpreter; print('TFLite: OK')"
python -c "from pymavlink import mavutil; print('pymavlink: OK')"

# 5. Test progressively (see PI_SETUP.md for details)
python tests/laptop/test_camera.py
python tests/laptop/test_cv.py --camera
python tests/hardware/benchmark.py
```

**If tflite-runtime fails**: `pip install --extra-index-url https://google-coral.github.io/py-repo/ tflite-runtime`

See `docs/PI_SETUP.md` for full Pi setup including hardware (camera, serial, wiring).

### Requirements Files

| File | For | Contents |
|------|-----|----------|
| `requirements_dev.txt` | Windows laptop | Full pip freeze (~90 packages, exact Windows versions) |
| `requirements_linux.txt` | WSL / Linux laptop | Full pip freeze from Linux (no pywin32 etc.) |
| `requirements_pi.txt` | Raspberry Pi | 4 lightweight packages (pymavlink, opencv-headless, numpy<2, tflite-runtime) |

**How it works**: The code is identical on every platform — you always pull the same branch from
GitHub. The ONLY thing that changes is which requirements file you install:

| You're on... | Install with... | Why different? |
|--------------|----------------|----------------|
| Windows laptop | `requirements_dev.txt` | Full freeze includes Windows-specific packages (pywin32 etc.) |
| WSL / Linux | `requirements_linux.txt` | Full freeze without Windows packages |
| Raspberry Pi | `requirements_pi.txt` | Lightweight: only 4 packages (no ultralytics/torch — uses TFLite instead) |

**Why not one file?** A `pip freeze` captures every installed package including platform-specific
ones. Windows freeze has `pywin32` which fails on Linux. Linux freeze has packages that fail on
Windows. Pi needs completely different packages (tflite-runtime instead of ultralytics+torch).
`requirements_pi.txt` is hand-written (only 4 top-level packages) and works on any Linux.

### What Can Be Tested Where

| Platform | Simulation | Real (webcam) | Real (Pi camera) | Docker Pi test |
|----------|-----------|---------------|-------------------|---------------|
| Windows | Yes | Yes | No | Yes (via Docker Desktop) |
| WSL/Linux | Yes | No | No | Yes |
| Raspberry Pi | No | No | Yes | N/A |

All files MUST be UTF-8 encoded. If regenerating on Windows, use:
```bash
cmd /c "python -m pip freeze > requirements_dev.txt"
```
On Linux/WSL, normal `pip freeze > requirements_linux.txt` works fine.

## The Approach: Simulation → Real

We don't jump to flying. Progression:

1. **Simulation on laptop** (DONE) — prove logic works
2. **Real camera + SITL on laptop** (DONE) — prove real camera + AI works
2b. **WSL simulation** (DONE) — prove code runs on Linux
2c. **Docker Pi test** (DONE) — prove TFLite model loads on Pi-like environment
3. **Pi + camera (no Cube)** (DONE) — prove vision on real hardware
4. **Pi + camera + Cube (bench, no props)** (DONE — connection verified) — prove commands are correct
5. **Manual flight (pilot on RC, Pi logging)** — calibrate detection altitude
6. **Full autonomous flight** — the mission

Same code at every step. Only the hardware changes.

## Risk Unknowns (Things Simulation Can't Tell Us)

1. **Detection altitude** — does AI see dummy from 30m with real camera?
2. **Inference speed on Pi** — TFLite on CPU, target < 200ms
3. **GPS accuracy** — real GPS drifts ~2-3m vs perfect SITL
4. **Wind/motion blur** — moving camera may reduce detection confidence

None require code rewrites — just tuning config.py values after real testing.

## Key Config Values to Tune After Real Testing

```python
# config.py — update these based on Pi/flight test results:
TARGET_ALT = 30        # lower if AI can't detect from 30m
VERIFY_ALT = 15        # lower altitude for close confirmation
SEARCH_SPEED_MPS = 5   # lower if AI can't keep up
IMAGE_W = 640          # change based on pi_9 resolution test
IMAGE_H = 480          # change based on pi_9 resolution test
SENSOR_WIDTH_MM = 5.02 # calibrate with tests/calibration/fov_calibrate.py
FOCAL_LENGTH_MM = 6.0  # calibrate with tests/calibration/fov_calibrate.py
```

## Test Scripts (categorized in tests/)

```
tests/laptop/
  test_camera.py ............. Camera gives frames?
  test_cv.py ................. AI detects dummy? (--camera for live)
  test_cube.py ............... Cube heartbeat + GPS?
  test_all.py ................ Full system connectivity check
  test_tflite.py ............. TFLite inference on laptop
  debug_tflite.py ............ Raw model output inspection

tests/hardware/
  benchmark.py ............... Inference speed (50 runs)?
  buzzer_test.py ............. Buzzer melodies? (needs mavproxy)
  gps_test.py ................ GPS lock + satellite tracking
  gps_health.py .............. Step-by-step GPS verification

tests/calibration/
  fov_calibrate.py ........... Bench FOV calibration (comprehensive)
  fov_test_simple.py ......... Simple single-measurement FOV
  alt_test.py ................ FOV at real altitude (flight day)

tests/diagnostics/
  diagnostics.py ............. Multi-view connectivity dashboard
  cube_monitor.py ............ Live Cube telemetry
  camera_stream.py ........... MJPEG stream to ground station

tests/flight/
  passive_flight.py .......... Passive detection during manual flight (ZERO commands)
  waypoint_test.py ........... Fly GPS waypoints (Step 2 flight test)
  bench_mission.py ........... Bench mission sequence (no flying)
  cube_commands.py ........... Test Pi→Cube command path
  detect_and_center.py ....... Detect & center mission
  auto_detect.py ............. AUTO waypoints + detect & hover
```

### Camera Note (IMX296 Global Shutter)
The IMX296 sensor outputs BGR data despite picamera2 labeling it RGB888.
**Do NOT add `cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)`** — the data is already BGR.
This was discovered by testing all 6 channel permutations. See session log 2026-02-17 part 2.

## Documentation

| Doc | What it covers |
|-----|---------------|
| CLAUDE.md (this) | Project context for LLM sessions — ground truth |
| docs/ARCHITECTURE.md | System overview, evolving diagrams, hardware checklist |
| docs/PI_SETUP.md | Step-by-step Pi setup and testing |
| docs/CV_GUIDE.md | Vision system, optimization stages, model swapping |
| docs/NEXT_STEPS.md | Phase-by-phase development plan |
| docs/CONNECTIVITY.md | Connection debugging |
| docs/PREFLIGHT_CHECKLIST.md | Pre-flight checks |
| docs/FLIGHT_DAY_CHECKLIST.md | Printable flight day checklist (follow top to bottom) |
| docs/FLIGHT_DAY_TESTS.md | Master test reference — all scripts, protocols, troubleshooting |
| docs/TEAM_PLAN.md | Team workstreams |
| docs/ROADMAP.md | Full development history |
| docs/DESIGN_DECISIONS.md | Design rationale (DD-01 format, WHY each choice) |
| docs/SIMULATOR.md | Simulator documentation |
| docs/SIMULATOR_GUIDE.md | Simulator user guide (keyboard controls, modes) |
| docs/GROUP_STATUS.md | Group project status, meetings, roles |
| docs/TRAINING_GUIDE.md | Model retraining workflow (Colab, datasets) |
| docs/FIRST_FLIGHT.md | First flight plan with progressive steps |
| **Blueprints** (read BEFORE source) | |
| docs/main_blueprint.md | Line-range map for main.py (908 lines) |
| docs/simple_simulator_blueprint.md | Line-range map for simple_simulator.py (2508 lines) |
| docs/pi_flight_blueprint.md | Line-range map for pi_flight.py (1097 lines) |
| docs/passive_watch_blueprint.md | Line-range map for passive_watch.py (752 lines) |
| **Reference** | |
| docs/DEPENDENCIES.md | Script dependency graph, platform compatibility matrix |
| docs/SAR_COMPARISON.md | Industry/academic comparison, references to cite in report |
| docs/TEST_GUIDE.md | All 41 test scripts: what, when, why, dependencies, flight day order |

## Git Strategy

- **main branch**: stable, proven code
- **Feature branches**: for new work (e.g., pi-setup, tuning)
- Commit after each successful test milestone
- Never break main — merge only when something works
- Remote: https://github.com/DimaChup/Group_Proj.git
- Current working branch: MainOne7
- **Backup**: Push to GitHub after every session. Pull on Pi before flights.
- **Rollback**: `git log --oneline -20` to find good commit, `git checkout <hash>` to test it
- **Branch cleanup needed**: ~42 local branches, many dead (Backup*, W*, v*). Delete after flight day.

## Session Log

Track what was done each session so context is never lost.

> **Archived sessions (2026-02-16 through 2026-02-20):** See `docs/SESSION_ARCHIVE.md`

### Session: 2026-03-09 — Test reorganization, experiment scripts, dry-run mode

**Test directory reorganization:**
- Moved all test scripts into organized subdirectories:
  ```
  tests/
  ├── calibration/          FOV, lens distortion
  ├── diagnostics/          System health dashboards, stream tests
  ├── hardware/             Individual component checks (GPS, camera, buzzer, benchmark)
  ├── flight/               Progressive flight tests (numbered 0a-4)
  ├── day_1_experiments/    Structured data collection (CSV output)
  └── laptop/               Development-only tools
  ```
- Numbered flight tests by progression:
  - `0a_cube_commands.py` → bench: individual commands
  - `0b_bench_mission.py` → bench: full sequence
  - `0c_feedback_test.py` → bench: vision→GPS pipeline
  - `1_passive_flight.py` → manual RC, CV watches (zero commands)
  - `2_waypoint_test.py` → fly GPS waypoints (no CV)
  - `3_auto_detect.py` → AUTO + AI → GUIDED hover
  - `4_detect_and_center.py` → autonomous pattern + center

**Experiment scripts created (all passive, zero commands, CSV output):**
- `tests/day_1_experiments/altitude_sweep.py` — detection rate vs altitude (10-30m buckets)
- `tests/day_1_experiments/speed_sweep.py` — detection rate vs speed + blur metric
- `tests/day_1_experiments/gps_accuracy.py` — GPS estimate error vs known dummy position
- `tests/day_1_experiments/gps_drift.py` — GPS noise floor (CEP50, CEP95)
- `tests/day_1_experiments/model_compare.py` — benchmark all .tflite models
- `tests/day_1_experiments/detection_log.py` — catch-all flight logger

**Calibration scripts:**
- `tests/calibration/lens_calibrate.py` — checkerboard lens distortion calibration

**main.py new features:**
- `--dry-run` flag: prints lawnmower waypoints, state machine walkthrough, map visualization
  - No GPS, no arming, no Cube needed
  - Uses SEARCH_AREA_GPS from config.py
  - Saves visualization to `dry_run_pattern.jpg`
- `--model PATH` flag: switch AI model without copying files (default: best.tflite)
- Both flags documented in FLIGHT_DAY_CHECKLIST.md and FLIGHT_DAY_TESTS.md

**New files:**
- `models/best2.tflite` — placeholder copy of best.tflite (swap with retrained model)
- `docs/FLIGHT_DAY_TESTS.md` — master test reference with all scripts, protocols, troubleshooting
- `memory/testing-pattern.md` — reusable progressive robotics testing pattern (auto-memory)

**Documentation updates:**
- FLIGHT_DAY_CHECKLIST.md: added Phase 7 (dry-run verification), Step 3.5 (RC override test with script), model swap with `--model` flag, dry-run section
- FLIGHT_DAY_TESTS.md: added --dry-run and --model to Step 5, pre-flight bench items 7-8
- Updated all script paths to numbered names across docs

### Session: 2026-03-11 — BOOTSTRAP.md workflows, headless main.py, thorough review

**Applied BOOTSTRAP.md workflows to project:**
- Created `brain-dump.md` — append-only user ideas capture
- Created `NICE_TO_HAVE.md` — improvement backlog with impact/effort scoring (16 items)
- Created `.claude/commands/` — slash commands: status, wrap-up, doc-health
- Created blueprints for all files >500 lines:
  - `docs/main_blueprint.md` — main.py (908 lines) line map
  - `docs/simple_simulator_blueprint.md` — simple_simulator.py (2508 lines) line map
  - `docs/pi_flight_blueprint.md` — pi_flight.py (1096 lines) line map
- Updated `MEMORY.md` with test structure, blueprints, workflow files, headless info

**Headless main.py (PuTTY/SSH support):**
- Added `--headless` flag (auto-detects on Pi when no DISPLAY)
- Added terminal keyboard input thread (reads keypresses over SSH)
- Added browser buttons to stream page at http://localhost:8090 (Y/N/M/E/W/S)
- Added `/cmd?key=` HTTP endpoint for programmatic commands
- ThreadingMixIn HTTP server for concurrent stream + command handling
- VERIFY state prints clear prompt to terminal with instructions
- cv2.imshow/namedWindow/waitKey skipped in headless mode

**Code changes:**
- main.py: headless support, terminal input thread, browser buttons, /cmd endpoint
- pi_flight.py: fixed `self.investigating` bug (used but never initialized), video stream quality 70→85%, video box flex:1→flex:2 (larger)
- tests/flight/draw_search_area.py: new file (draw polygon on map → search_area.json)
- tests/flight/live_map.py: new file (real-time drone map viewer with coverage overlay)
- main.py: _setup_real_search_area() loads from search_area.json instead of interactive drawing
- pi_flight.py: loads search_area.json in REAL mode

**Drawing/flight script separation:**
- draw_waypoints.py → waypoints.json → 2_waypoints.py (load, don't draw)
- draw_search_area.py → search_area.json → main.py/pi_flight.py (load, don't draw)
- All drawing happens on laptop; Pi loads JSON headlessly

**Thorough code review (6 parallel agents):**
- main.py: 3 bugs (float logging, hardcoded lat scale, blocking ACK race), 4 security issues (HTML/JSON injection), run() is 264 lines (needs splitting)
- simple_simulator.py: 2508 lines (needs splitting into UI + estimation + flight modules), duplicate Kalman code
- pi_flight.py: self.investigating bug (FIXED), handle_command() 120 lines (needs splitting)
- passive_watch.py (752 lines): clean, no issues
- config.py, vision.py, planning.py, utils.py, states.py, simulation.py: all clean
- All 41 test scripts audited — well organized, no issues
- 16 doc files audited — stale script references fixed across 7+ docs

**Documentation fixes:**
- Fixed stale pi_1-pi_9 script references across ARCHITECTURE.md, CV_GUIDE.md, FLIGHT_DAY_CHECKLIST.md, FLIGHT_DAY_TESTS.md, NEXT_STEPS.md, PREFLIGHT_CHECKLIST.md, CONNECTIVITY.md
- Updated references from tests2/ to tests/ subdirectories
- Fixed 2_waypoint_test.py → 2_waypoints.py naming

---

**INSTRUCTIONS FOR LLM**: When starting a new session, read this file first. Then read
whichever doc is relevant to the user's current task. Always update the "Current State"
section and "Session Log" when work is completed. Keep this document as the single source
of truth.

### Session: 2026-03-11 (part 2) — FLIGHT DAY (weather cancelled flight, bench testing)

**Field day at site. Pi + Cube + camera assembled. Weather cancelled actual flight.**

**Terminal setup & connectivity (PuTTY + Pi screen):**
- Established 3-terminal workflow: PuTTY T1 (mavproxy), Pi screen (diagnostics), PuTTY T2 (scripts)
- Mavproxy with dual UDP outputs: 14550 (scripts) + 14551 (diagnostics) + TCP 5762 (Mission Planner)
- Resolved camera "in use" conflicts, port binding conflicts, PuTTY/Qt display crashes
- Pi IP changed to 192.168.1.3

**FOV calibration:**
- Measured 92cm visible at 1m height → FOCAL_LENGTH_MM = 5.46 (was 7.0)
- Used capture_training.py stream + tape measure

**passive_watch.py improvements:**
- GPS estimate now shows at ground level (clamp alt to 0.3m instead of skip <1.0m)
- Pink dot on detection center in stream overlay

**Lens calibration (checkerboard):**
- calib.io 14x9 board (13x8 inner corners, 28mm squares)
- lens_calibrate.py: added robust flags, findChessboardCornersSB fallback
- calibration_data.npz saved on Pi (RMS = 0.399)
- **Lens undistortion added to vision.py**: precomputed remap maps at startup, cv2.remap() in detect_in_image()
- Cost: ~1.5ms per frame (negligible on 208ms inference)
- All scripts benefit automatically (passive_watch, pi_flight, main.py)

**Benchmark results (Pi 5, TFLite, XNNPACK CPU):**
- best.tflite (3.2MB YOLOv8n): 206.5ms / 4.8 FPS, 50/50 detection, 0.966 confidence
- Undistortion cost: +1.5ms (negligible)
- All 3 models identical (best, best2, custom are copies)
- Created comprehensive benchmark_full.py: system info, preprocessing, all models, ONNX, threading

**CV speed improvement research:**
- Deep research on all Pi 5 inference speedup options (NCNN, FP16, threading, resolution, Hailo, etc.)
- Top picks: FP16 XNNPACK (~10 FPS), threaded pipeline (+20-30%), NCNN (~15 FPS)
- NOT viable: Coral TPU, Pi GPU, INT8 NCNN
- Full findings saved to memory/cv-speed-research.md

**New files:**
- FIELD_QUICK_REF.md — copy-paste ready commands for flight day without internet
- tests/hardware/benchmark_full.py — comprehensive CV benchmark (6 sections)
- memory/cv-speed-research.md — ranked CV speed improvement options
- memory/benchmarks.md — benchmark results tracking

**Commits (10 this part):**
- 72ea231: Flight readiness fixes (lat scale, camera warmup, RTL button, link lost banner)
- 12f1c4d: FIELD_QUICK_REF.md
- 9f773c2: passive_watch GPS estimate clamp
- 417c9d7: passive_watch pink dot
- 4404a99: Fix pink dot tuple bug
- fbc9a99: FOCAL_LENGTH_MM = 5.46
- 9e3d16e: waypoints.json update
- 319c69f: lens_calibrate robust detection
- b13d868: vision.py lens undistortion
- f22d1c8: Fix cam_w default
- 4754135: Fix benchmark.py path
- b7ff98a: benchmark_full.py (basic)
- da42e96: benchmark_full.py (comprehensive)

**NEW WORKFLOW (from BOOTSTRAP.md):**
- Read blueprints (`docs/*_blueprint.md`) BEFORE source files — they tell you exactly where to look
- Append every user message to `brain-dump.md` (cleaned up, all ideas preserved)
- Route improvement ideas to `NICE_TO_HAVE.md` with impact/effort scores
- After code changes: update relevant blueprint (line ranges shift)
- At session end: run `.claude/commands/wrap-up.md` checklist
