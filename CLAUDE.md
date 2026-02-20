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
- [ ] Manual flight with passive detection (pi_passive_flight.py)
- [ ] Full autonomous bench test (main.py, no props)
- [ ] **BEFORE FLIGHT DAY: Prepare alternative CV models on laptop**
  - [ ] Export COCO person detector: `yolo export model=yolov8n.pt format=tflite`
  - [ ] Export INT8 quantized: `yolo export model=best.pt format=tflite int8=True`
  - [ ] Optionally retrain on better data (real photos of dummy)
  - [ ] Copy all .tflite files to `models/` folder, ready to swap on Pi
  - [ ] On flight day: swap models between tests (`cp models/X.tflite best.tflite`)

### Flight Testing Steps (follow in order)
Each step builds trust before adding risk. **Never skip a step.**

1. **[ ] Mission Planner AUTO waypoints (no custom code)**
   - Upload a simple square pattern (4 waypoints) in Mission Planner at 10-15m altitude
   - Switch to AUTO on RC, drone flies the pattern, RTLs
   - Proves: Cube, GPS, motors, RTL all work. Your code not involved.
   - Kill switch: RC mode switch to STABILIZE/LOITER at any time

2. **[ ] Waypoint test script (no CV)** — `tests/pi_waypoint_test.py` (to be written)
   - Your code arms, takes off to 10m, flies 3-4 GPS waypoints in GUIDED mode, lands
   - No camera, no detection, no decision-making
   - Proves: your mavlink commands (arm, takeoff, goto, land) work on real hardware
   - Kill switch: RC override always active

3. **[ ] Manual flight + passive CV** — `tests/pi_passive_flight.py`
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
├── simulation.py              ← Laptop-only sim: map.jpg + simulated drone camera view
├── preflight.py               ← Standalone connectivity checker (camera, Cube, AI model)
│
├── best.tflite                ← AI model file (~6MB, YOLOv8n exported to TFLite)
├── models/                    ← Alternative TFLite models for flight day testing
│   └── custom_yolov8n.tflite  ← Copy of best.tflite (baseline)
├── map.jpg                    ← Satellite image for simulation (~12MB)
├── dummy.png                  ← Dummy/casualty image for dataset generation + bench test
├── generate_dataset.py        ← Creates synthetic training data from map.jpg + dummy.png
├── test_flight10.py           ← Legacy flight test script
│
├── requirements_dev.txt       ← Windows laptop: full pip freeze (~90 packages, exact versions)
├── requirements_linux.txt     ← WSL/Linux laptop: full pip freeze (no Windows-specific packages)
├── requirements_pi.txt        ← Pi: pymavlink, opencv-headless, numpy<2, tflite-runtime
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
│   └── ROADMAP.md             ← Full 10-phase development history
│
└── tests/
    ├── pi_1_camera.py         ← Test: camera gives frames (OpenCV or picamera2)
    ├── pi_2_detect.py         ← Test: live AI detection (--headless for SSH)
    ├── pi_3_benchmark.py      ← Test: inference speed (50 runs, timing report)
    ├── pi_3b_buzzer.py        ← Test: standalone buzzer melody test via MAVLink
    ├── pi_4_detect_and_log.py ← Test: camera + Cube + buzzer + CSV logging
    ├── pi_4b_detect_buzzer.py ← Test: pi_2 style display + Cube buzzer + guidance + CSV
    ├── pi_5_guidance.py       ← Test: detection + directional commands (--headless)
    ├── pi_5b_telemetry.py     ← Test: pi_4b + live Cube telemetry overlay (alt, GPS, yaw)
    ├── pi_6_fov_test.py       ← Test: FOV calibration on bench (--headless)
    ├── pi_7_alt_test.py       ← Test: FOV calibration at altitude (--headless)
    ├── pi_8_camera_test.py    ← Test: FPS + motion blur impact (--headless)
    ├── pi_9_resolution_test.py← Test: resolution vs speed vs detection quality
    ├── pi_passive_flight.py   ← Test: passive detection during manual RC flight + buzzer
    ├── pi_cv_test.py          ← Test: CV detection quality with Pi camera
    ├── pi_camera_tune.py      ← Test: camera parameter tuning
    ├── pi_cube_debug.py       ← Diagnostic: MAVLink message types + rates from Cube
    ├── pi_diagnostics.py      ← Visual dashboard: all subsystem connectivity + live rates
    ├── pi_gps_test.py         ← GPS lock test: wait for satellite fix, show status
    ├── pi_color_picker.py     ← Tool: color channel ordering picker (6 options)
    ├── pi_color_fix.py        ← Tool: computed color correction with grid
    ├── pi_color_manual.py     ← Tool: manual slider-based color tuning
    ├── pi_color_calibrate.py  ← Tool: color calibration with reference chart
    ├── test_tflite_laptop.py  ← Test: TFLite inference on laptop (same path as Pi)
    ├── test_camera.py         ← Quick camera preview + snapshot
    ├── test_cube.py           ← Cube heartbeat, GPS, attitude, battery
    ├── test_cv.py             ← AI model loading + detection test
    ├── test_all.py            ← Full system connectivity check
    └── debug_tflite.py        ← Raw TFLite model output inspection
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
simulation.py ......... Laptop-only simulation (map + simulated drone view)
preflight.py .......... Connectivity checker (standalone tool)
tests/ ................ All test scripts (pi_1 through pi_9, test_cube, etc.)
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

### Simulation (laptop)
```bash
# Need: SITL running (Mission Planner or mavproxy), venv activated
set DRONE_MODE=SIMULATION      # Windows (cmd)
# export DRONE_MODE=SIMULATION  # Linux/WSL
python main.py
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
python tests/pi_1_camera.py
python tests/pi_2_detect.py --headless
python tests/pi_3_benchmark.py
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
SENSOR_WIDTH_MM = 5.02 # calibrate with pi_6 FOV test
FOCAL_LENGTH_MM = 6.0  # calibrate with pi_6 FOV test
```

## Test Scripts (run in this order on Pi)

```
pi_1_camera.py .......... Camera gives frames?
pi_2_detect.py .......... AI detects dummy?  (--headless for SSH)
pi_3_benchmark.py ....... Inference speed?
pi_3b_buzzer.py ......... Buzzer plays melodies? (needs mavproxy)
pi_4b_detect_buzzer.py .. Camera + AI + buzzer + guidance? (--headless for SSH)
pi_4_detect_and_log.py .. Camera + Cube + buzzer + CSV logging
pi_5_guidance.py ........ Centering commands?  (--headless)
pi_6_fov_test.py ........ FOV calibration?  (--headless)
pi_7_alt_test.py ........ FOV at real altitude? (flight day)
pi_8_camera_test.py ..... FPS + blur impact?  (--headless)
pi_9_resolution_test.py . Best resolution?
pi_passive_flight.py .... Passive detection during manual RC flight
test_cube.py ............ Cube heartbeat + GPS?
preflight.py ............ All systems go?
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
| docs/TEAM_PLAN.md | Team workstreams |
| docs/ROADMAP.md | Full development history |

## Git Strategy

- **main branch**: stable, proven code
- **Feature branches**: for new work (e.g., pi-setup, tuning)
- Commit after each successful test milestone
- Never break main — merge only when something works
- Remote: https://github.com/DimaChup/Group_Proj.git
- Current working branch: MainOne4

## Session Log

Track what was done each session so context is never lost.

### Session: 2026-02-16 (part 1)
- Audited all 7 docs for redundancy and inconsistencies
- Created docs/ARCHITECTURE.md with evolving Phase 0-5 diagrams
- Fixed the REAL mode gap: drone had no waypoints in real mode — added SEARCH_AREA_GPS to config.py, unified TAKEOFF state for both modes
- Added interactive polygon drawing to REAL mode (_setup_real_search_area in main.py)
- Fixed preflight.py mode default to read from config.py
- Fixed PREFLIGHT_CHECKLIST.md path (~/v3 → ~/sar-drone)
- Cleaned up requirements (deleted bloated freeze files, created requirements_dev.txt)
- Added simulation→real transition docs to ARCHITECTURE.md
- Added hardware checklist and risk unknowns to ARCHITECTURE.md
- Added "The Journey: Basic → Optimised" stages to CV_GUIDE.md
- Updated .gitignore (added .claude/, flight_log.csv)
- Pushed to Group_Proj remote

### Session: 2026-02-16 (part 2) — Cross-platform environment testing
- Tested simulation + real mode on Windows — both work
- Tested simulation on WSL/Linux (myenv) — works
- Tested Docker Pi environment (Dockerfile.pi-test) — TFLite model loads (prints "Model loaded: True")
- Froze Windows dependencies: `cmd /c "python -m pip freeze > requirements_dev.txt"` (UTF-8)
- Froze Linux dependencies: `pip freeze > requirements_linux.txt`
- Discovered: full pip freeze is platform-specific (Windows has pywin32, Linux doesn't) — need separate freeze files
- Discovered: PowerShell `>` creates UTF-16 files pip can't read — must use `cmd /c "..."` on Windows
- Discovered: `pip.exe` launcher can break if venv was created from a moved Python install — use `python -m pip` as workaround
- Added "Recreating the Environment" section to CLAUDE.md (Windows, WSL, Pi, Docker)
- Added requirements file strategy docs (platform-specific freezes + cross-platform requirements_pi.txt)
- Pushed to MainOne3 branch on Group_Proj remote
- **Next: Pi setup tomorrow — clone MainOne4, create pienv, run progressive tests (PI_SETUP.md)**

### Session: 2026-02-16 (part 3) — Housekeeping
- Switched to MainOne4 branch (identical code to MainOne3, same commit)
- Fixed CLAUDE.md: updated all branch references from MainOne3 → MainOne4
- Fixed CLAUDE.md: corrected "How to Run" commands from `simple_simulator.py` → `main.py` (simple_simulator.py doesn't exist, main.py is the entry point)
- Confirmed project structure matches documentation — all files accounted for
- MainOne4 NOT yet pushed to remote (need: `git push origin MainOne4`)
- **Next: Push MainOne4, then Pi setup — clone, create pienv, run progressive tests (PI_SETUP.md)**

### Session: 2026-02-17 — Pi setup and hardware testing
- Pushed MainOne4 to remote, cloned on Pi at ~/dima/Group_Proj
- Created pienv with `--system-site-packages` on Pi (Python 3.13.5)
- **tflite-runtime doesn't support Python 3.13** — installed `ai-edge-litert` instead
- Updated vision.py import chain: tflite_runtime → ai_edge_litert → tensorflow
- numpy<2 (1.26.4) built from source on Pi (~5 min compile, works)
- Installed opencv-python (GUI version) for live camera preview on Pi monitor
- **pi_1_camera.py**: PASS — picamera2 detected, 640x480, RGB format
- **pi_2_detect.py**: PASS — TFLite detection working, some detections on real camera
- **pi_3_benchmark.py**: PASS — 206ms avg inference, 4.8 FPS, 50/50 detection, 0.966 confidence
- **Cube serial issue**: Python 3.13 + pyserial = broken serial reads (bytes dropped, BAD_DATA)
  - Raw `cat /dev/ttyAMA0` gets data fine, pymavlink can't parse it
  - Solution: mavproxy as UDP bridge (already installed at /opt/mavlink/mavlink-venv/)
- **Cube baud rate is 921600** (not 57600 as previously assumed)
- Updated config.py: auto-detects serial port → returns `udpin:0.0.0.0:14550`
- Updated config.py: default baud rate 57600 → 921600
- **test_cube.py**: PASS via mavproxy bridge — Heartbeat, GPS, Attitude, Battery all OK
- ArduCopter V4.6.3, CubeOrangePlus, Frame: QUAD/X confirmed
- Updated test_cube.py: use recv_match loop instead of wait_heartbeat (Python 3.13 compat)
- **Pi startup procedure**:
  1. Terminal 1: `sudo /opt/mavlink/mavlink-venv/bin/mavproxy.py --master=/dev/ttyAMA0 --baudrate=921600 --out=udpout:127.0.0.1:14550`
  2. Terminal 2: `cd ~/dima/Group_Proj && source pienv/bin/activate && python3 main.py`
- **Known issues**:
  - Camera slightly out of focus (twist lens ring to adjust)
  - Detection quality lower with real camera vs simulation (expected — lighting, print quality)
  - No GPS fix indoors (normal)
  - Battery shows 0.0V when powered via USB only (normal)
- Created **pi_3b_buzzer.py**: standalone buzzer melody test (5 tunes via MAVLink PLAY_TUNE)
- Created **pi_4b_detect_buzzer.py**: like pi_2 but adds Cube buzzer + guidance commands + CSV logging
  - Supports --headless (SSH) and display mode (Pi monitor)
  - Beep cooldown: max once per second
  - Guidance: LEFT/RIGHT/FORWARD/BACK/CENTRED based on target pixel position
  - Logs: timestamp, GPS, attitude, confidence, pixel coords to detection_log.csv
- **pi_3b_buzzer.py**: PASS on Pi monitor — buzzer plays all 5 melodies
- **pi_4b_detect_buzzer.py --headless**: PASS — 144 detections from 513 frames, 210ms avg
  - Guidance commands working correctly (LEFT, RIGHT, FORWARD, BACK, CENTRED)
  - Yaw data flowing from Cube (e.g. yaw=-153)
  - Buzzer beeps on Pi monitor mode; silent in SSH headless (may need audio forwarding)
- **Known**: Buzzer beep via MAVLink works when script runs on Pi's own monitor/terminal,
  but not when run over SSH headless — likely a timing/resource issue, not a code bug
- Created **pi_5b_telemetry.py**: full bench test — camera + AI + buzzer + guidance + live Cube telemetry
  - Telemetry overlay on camera feed: GPS, altitude, yaw/pitch/roll, battery
  - Fixed recv_match bug: drain all messages first, then read from mav.messages cache
  - --streamrate=10 on mavproxy boosted ATTITUDE from 0.4 Hz to 7.4 Hz
- Created **pi_cube_debug.py**: diagnostic — shows all MAVLink message types + rates + latest values
- Created **pi_gps_test.py**: standalone GPS lock test — live table showing fix type, sats, coords
  - GPS hardware confirmed working (fix_type=1 = "searching"), just no fix indoors (0 sats)
- **vision.py updated**: picamera2 fallback added to VisionSystem
  - OpenCV tried first (laptop unchanged), falls back to picamera2 on Pi
  - get_frame() returns BGR from both backends
  - release() cleans up both backends
  - Tested on Pi: `Frame: (480, 640, 3)` — works
- **main.py runs on Pi!** — connects to Cube, opens camera, loads AI model
  - Stuck at ARMING indoors (no GPS, no RC) — expected
  - Cube pre-arm buzzer silenced via mavproxy: `param set NTF_BUZZ_ENABLE 0`
- **Mission Planner connected to real Cube via Pi**:
  - mavproxy: `--out=tcpin:0.0.0.0:5762` for MP + `--out=udpout:127.0.0.1:14550` for Pi scripts
  - MP connects TCP to Pi IP (192.168.1.121:5762)
  - Slight delay over WiFi but fully functional
- **Pi IP**: 192.168.1.121 (on local network)
- **Full mavproxy command** (Pi Terminal 1):
  ```
  sudo /opt/mavlink/mavlink-venv/bin/mavproxy.py --master=/dev/ttyAMA0 --baudrate=921600 --streamrate=10 --out=udpout:127.0.0.1:14550 --out=tcpin:0.0.0.0:5762
  ```
- **Next: Outdoor test (GPS fix), then manual flight with passive detection**

### Session: 2026-02-17 (part 2) — Camera color fix + documentation
- **CRITICAL FIX: IMX296 Global Shutter Camera BGR/RGB issue**
  - Camera outputs BGR data despite picamera2 labeling it RGB888
  - All code had `cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)` which was DOUBLE-swapping channels
  - This caused a blue tint on all camera images — spent hours trying AWB modes, manual gains,
    gray world correction, ISP tuning file edits, kernel update (rpi-update) before discovering root cause
  - **Fix**: Remove the `cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)` conversion entirely
  - The sensor data is already in BGR format (OpenCV's native format), so no conversion needed
  - Discovery method: tested all 6 permutations of R,G,B channels — RGB (no conversion) looked correct
- **Files modified for BGR fix**:
  - vision.py: removed COLOR_RGB2BGR in get_frame() picamera2 path
  - config.py: disabled CAMERA_COLOR_CORRECTION, removed CAMERA_SWAP_RB
  - tests/pi_1_camera.py: removed COLOR_RGB2BGR
  - tests/pi_2_detect.py: removed COLOR_RGB2BGR
  - tests/pi_4b_detect_buzzer.py: removed COLOR_RGB2BGR
  - tests/pi_5b_telemetry.py: removed COLOR_RGB2BGR
  - tests/pi_5_guidance.py: removed COLOR_RGB2BGR
  - tests/pi_6_fov_test.py: removed COLOR_RGB2BGR
  - tests/pi_8_camera_test.py: removed COLOR_RGB2BGR
  - tests/pi_9_resolution_test.py: removed COLOR_RGB2BGR
  - tests/pi_diagnostics.py: removed COLOR_RGB2BGR
- **New files created**:
  - tests/test_tflite_laptop.py: standalone TFLite inference test (same code path as Pi, no Ultralytics)
  - tests/pi_color_picker.py: color correction picker (6 channel ordering options)
  - tests/pi_color_fix.py: computed color correction with grid
  - tests/pi_color_manual.py: manual slider-based color tuning
  - tests/pi_color_calibrate.py: color calibration with reference chart
- **rpi-update performed**: kernel updated on Pi (no negative effects, but didn't fix colors — the fix was the BGR conversion removal)
- **Mission Planner connected to Cube via mavproxy TCP bridge** (tcpin:0.0.0.0:5762)
- **Benchmark results**: 256ms avg inference, 3.9 FPS, 50/50 detection, 0.966 confidence
- **Known issue**: pi_color_manual.py and pi_color_calibrate.py still have COLOR_RGB2BGR (they were diagnostic tools, not critical)
- **Next steps**:
  1. Push BGR fix to GitHub, pull on Pi
  2. Test detection with corrected colors (pi_2_detect.py --headless with dummy)
  3. Passive flight test (pi_passive_flight.py during manual RC flight)
  4. Outdoor GPS fix test
  5. Full autonomous flight prep

### Session: 2026-02-18 — GPS diagnostics, Cube wiring, diagnostics GS fix
- **GPS diagnostics on Pi**: ran tests2/gps_test.py — GPS hardware confirmed connected (GPS_RAW_INT arrives, fix_type=1) but 0 satellites indoors (expected, need outdoor test)
- **ArduCopter 4.6+ parameter naming**: GPS_TYPE renamed to GPS1_TYPE, GPS_GNSS_MODE to GPS1_GNSS_MODE — gps_test.py updated to try both old and new names
- **CAN port checks**: Added CAN_P2_DRIVER and CAN_D2_PROTOCOL checks (Here 3+ GPS connected to CAN2)
- **Wiring confirmed**:
  - Here 3+ GPS → CubeOrange+ CAN2 (4-pin CAN cable, gets power from Cube)
  - CubeOrange+ TELEM2 → Pi GPIO UART (TX→RX, RX→TX, GND) at 921600 baud
- **Diagnostics GS/Mission Planner detection fix** (tests2/pi_diagnostics.py):
  - **Problem**: GS check used socket connect_ex which couldn't distinguish "MP connected" from "port listening"
  - **Fix**: Replaced with `ss -tna` command to check actual TCP connection state on port 5762
    - `ESTAB` on :5762 → "MP CONNECTED" (green)
    - `LISTEN` on :5762 → "WAITING FOR MP" (yellow/wait, not green)
    - No :5762 → "NO TCP OUTPUT" or "NOT DETECTED" (red)
  - Also added periodic `detect_mavproxy()` re-detection (was only running once at startup)
  - Falls back to socket connect on non-Linux (Windows)
- **tests2/ directory**: Clean test directory with only essential scripts:
  - pi_diagnostics.py, cube_commands.py, gps_test.py, cube_monitor.py
  - passive_flight.py, pi_passive_flight.py, feedback_test.py
- **Next: Outdoor GPS fix test, then manual flight with passive detection**

### Session: 2026-02-18 (part 2) — Cube command testing, mavproxy fixes, flight prep

**Cube command testing (bench, no props):**
- Created `tests2/cube_commands.py`: tests Pi→Cube command path (mode changes, arm, params, buzzer)
- Created `tests2/bench_mission.py`: walks Cube through full mission sequence (GUIDED, waypoints, LAND)
- Both scripts initially showed `system 0` (mavproxy) instead of Cube (`system 1`)
- Mode names showed as `Mode(0x00000004)` instead of "GUIDED"

**Three mavproxy issues found and fixed across all scripts:**
1. **Heartbeat filtering**: mavproxy sends GCS heartbeats (type=6) alongside Cube heartbeats (type=2).
   Fix: filter `msg.type != MAV_TYPE_GCS` to skip mavproxy's heartbeats.
2. **target_system extraction**: `recv_match` doesn't set target_system (stays 0). `wait_heartbeat()`
   with `source_system=255` broke connection entirely.
   Fix: manually set `mav.target_system = hb.get_srcSystem()` from first autopilot heartbeat.
3. **Mode name mapping**: `mavutil.mode_string_v10()` unreliable via mavproxy (returns raw hex).
   Fix: custom `COPTER_MODES` dict mapping custom_mode numbers to ArduCopter mode names.
4. **ARMING mode change**: `mode_mapping()['GUIDED']` unreliable via mavproxy, can crash.
   Fix: use `command_long_send(MAV_CMD_DO_SET_MODE, ..., 4)` with hardcoded mode number.

**Files fixed:**
- `tests2/cube_commands.py`: all 3 fixes applied
- `tests2/bench_mission.py`: all 3 fixes applied + drain_messages() for stale heartbeat verification
- `main.py`: all 3 fixes applied (heartbeat filter, target_system extraction, mode change command)

**Bench test results (system 1, correct mode names):**
- GUIDED mode: works (autonomous, no RC needed)
- STABILIZE: fails without RC (expected — manual mode needs RC input)
- LOITER: fails without GPS (expected)
- LAND: works (autonomous mode)
- ARM: rejected "RC not found" (expected — command DID reach Cube)
- Waypoints: ACK'd with result=4 FAILED (no GPS — expected)
- Parameters: read correctly (ARMING_CHECK = 29182)
- Conclusion: all commands reach Cube and are processed. Failures are from missing RC/GPS, not code bugs.

**New test scripts created:**
- `tests2/gps_health.py`: step-by-step GPS verification (CAN bus, GPS type, hardware data, satellite tracking)
- `tests2/pi_waypoint_test.py`: Step 2 flight test — fly 4 GPS waypoints in GUIDED mode, no CV
  - `--dry-run` flag: verify commands without arming
  - `--alt N`: set altitude (default 10m)
  - Ctrl+C triggers RTL (Return To Launch)
  - 20m square pattern at 3 m/s
- `tests2/pi_camera_stream.py`: MJPEG stream to ground station
  - Serves on http://<PI_IP>:8090/stream
  - Downscales to 320x240 for bandwidth (~0.5 Mbps)
  - `--with-detection`: overlay AI detection boxes
  - `--res`, `--fps`, `--quality` flags for tuning

**Here 3+ GPS LED reference:**
- Flashing BLUE = disarmed, no GPS lock (normal indoors)
- Flashing GREEN = disarmed, GPS lock acquired (ready to arm!)
- Double YELLOW = pre-arm checks failing
- Flashing YELLOW = RC failsafe

**Progressive flight testing steps (all documented in CLAUDE.md):**
1. Mission Planner AUTO waypoints (no custom code) — not done
2. pi_waypoint_test.py (your code, no CV) — script ready, not tested
3. pi_passive_flight.py (manual flight, CV logging) — script exists
4. main.py with CV logging only (no descent) — needs log-only flag
5. Full autonomous mission — main.py ready after steps 1-4

### Session: 2026-02-18 (part 3) — Camera stream detection fix, H.264 alternative

**Camera stream detection fix:**
- `pi_camera_stream.py --with-detection` was not detecting targets (det 0%)
- Root cause: camera + model bundled in one VisionSystem call, no warmup inference
- Fix: separated camera opening from model loading (same approach as diagnostics)
  - Camera opened directly (OpenCV or picamera2) — not through VisionSystem
  - Model loaded with `VisionSystem(camera_index=None, ...)` — model only
  - Added warmup inference before main loop
  - Added real frame test at startup for immediate feedback
  - Added terminal debug output (model status, backend type, detection hits)
- Detection now works correctly in the stream

**Streaming approach decision (documented in ARCHITECTURE.md):**
- **Chosen: MJPEG** (`pi_camera_stream.py`, port 8090)
  - Pure Python, zero dependencies, any browser
  - Near-realtime latency (~100ms)
  - ~0.5 Mbps at 320x240, 5fps
- **Alternative tested: H.264/HLS** (`pi_camera_stream_h264.py`, port 8091)
  - Uses ffmpeg (needs `sudo apt install ffmpeg`)
  - 5-10x better compression (~0.05 Mbps)
  - 2-4 second latency (HLS segment buffering)
  - Browser needs hls.js (loaded from CDN)
- **Decision: MJPEG wins** — for drone ops, low latency > compression.
  0.5 Mbps is trivial over WiFi. Revisit only if bandwidth becomes an issue.

**Next: Push to git, pull on Pi, outdoor GPS test, then Step 1 (Mission Planner AUTO waypoints)**

### Session: 2026-02-19 — simple_simulator.py (interactive MVP)

**Created `simple_simulator.py`** — interactive flight simulator for testing GPS estimation
and landing approach before real flights. Connects to SITL, you fly with keyboard (like an
RC controller), CV runs live and estimates target GPS position.

**Features built across two sub-sessions:**
- **Keyboard RC**: SPACE=arm, WASD=fly, QE=yaw, RF=altitude
- **C mode (GPS centering)**: press C → drone auto-flies to best GPS estimate of dummy
- **V mode (visual servo)**: press V → drone centres on dummy using pixel offset (proportional control)
  - EMA smoothing on detection position (alpha=0.3) to reduce shake noise
  - Falls back to GPS estimate when target lost
  - Centre-snap: when target within 30px of centre, drone GPS = dummy GPS (weight 10)
- **B key (recording)**: manual toggle to record GPS estimates during C or V mode
  - Three data buckets: C GPS EST, V GPS EST (improved by centre-snaps), V drone GPS (raw proxy)
- **G key (GPS lock)**: starts 30s automatic averaging while V mode keeps drone centred
  - Only collects samples when centre-snap active (target confirmed at centre)
  - Shows Avg GPS error and GPS EST error at end
- **L key (7.5m offset landing)**: after G lock, calculates coordinate 7.5m north of estimated dummy
  - Flies to that coordinate, auto-lands when within 3m and slow
  - Shows full landing report: estimate error, landing GPS error, distance to dummy
- **End-of-flight charts (ESC)**: scatter plot of estimated positions + error histogram
- **Camera shake simulation (--shake N)**: altitude-dependent angular jitter
  - Shake is in camera pixels (fixed angular displacement), converted to map pixels using altitude
  - HUD shows ground distance equivalent: `SHAKE: 5px = 20cm on ground`
- **GPS drift simulation (--gps-drift N)**: Ornstein-Uhlenbeck random walk on GPS readings
- **CV throttle (--fps N)**: limit inference rate to match Pi speed
- **TFLite backend (--tflite)**: force TFLite instead of Ultralytics

**HUD layout:**
- DUMMY section: ACTUAL position (ground truth), GPS EST (weighted avg), LATEST (single detection), errors
- DRONE section: GPS POS, TRUE POS (with drift), GPS drift magnitude, DRONE→DUMMY distance
- LOCKING indicator (30s countdown, sample count)
- LOCKED result (Avg GPS + GPS EST with errors)
- Landing status (flying to / descending / landed with distance)

**Key findings from simulation testing:**
- GPS-only centering (C mode): ~1-3m estimate error depending on altitude and drift
- Vision centering (V mode): significantly improves estimate — centre-snap observations dominate weighted avg
- G lock (30s averaging while centred): ~0.5m estimate error in simulation
- 7.5m offset landing: SITL lands perfectly at target coordinate (zero navigation error)
  - Real Cube would add ~2.5m navigation error → expect 5-10m actual landing distance
- Estimate error direction matters: perpendicular to offset direction barely affects total distance
  (0.48m error on 7.5m offset ≈ 7.515m actual — geometry makes it nearly invisible)

**Safety constraint identified (not yet implemented):**
- Drone should NOT hover directly above casualty (propwash, crash risk)
- Current V mode centres directly above — need offset approach
- **Planned Z mode**: centre target on right half of camera view instead of dead centre
  - Drone stays offset to one side, never directly over dummy
  - Use pixel-to-GPS conversion from offset position for G lock (not drone GPS)
  - At 15m altitude with half-frame offset ≈ 3m horizontal separation (safe)
  - **Deferred to future session** — V mode at high altitude (15-20m) is safe enough for now
- **Alternative**: use V at high altitude only (15-20m) where propwash is negligible, then G lock
  from height. Less precise but safe and simpler.

**Mission sequence tested end-to-end in simulation:**
1. Manual flight → detect dummy during flyover → GPS observations accumulate
2. C → GPS centering brings drone roughly above dummy (~1-3m error)
3. Descend to 10m → V → vision servo centres precisely above dummy
4. G → 30s averaging while centred → locked GPS estimate (~0.5m error)
5. L → fly to 7.5m north of estimate → auto-land → landed ~7.5m from dummy

**Files created/modified:**
- `simple_simulator.py` — new file, ~1135 lines, full interactive MVP
- No changes to existing project files (config.py, vision.py, etc.)

**Command line:**
```bash
# Basic (no simulated errors):
set DRONE_MODE=SIMULATION && python simple_simulator.py

# With Pi-like conditions:
set DRONE_MODE=SIMULATION && python simple_simulator.py --fps 4 --tflite --gps-drift 3 --shake 5
```

**Next steps:**
- [ ] Implement Z mode (offset centering) for safety — keep target in right half of frame
- [ ] Add GPS navigation error to SITL send_to_gps() for more realistic landing simulation
- [ ] Test in REAL mode (webcam + SITL)
- [ ] Push to git, outdoor GPS test, manual flight with passive detection

### Session: 2026-02-20 — Multi-target, clustering, estimation improvements, first flight doc

**Continued from 2026-02-19 session (ran out of context, continued in new session).**

**Multi-target support (simulation.py + simple_simulator.py):**
- Multiple dummies placed on map during setup (left-click to place, right-click when done)
- All render identically as dummy images (CV can't distinguish)
- Pilot classification: Y=dummy, I=item of interest, X=false positive
- Items of interest logged with GPS position; false positives discarded

**Spatial clustering:**
- Observations grouped into clusters by GPS distance (`--cluster-dist N`, default 30m)
- Each cluster has permanent ID (never shifts when others are classified/removed)
- Each cluster maintains independent rolling 50, total average, and Kalman filter
- Cluster markers on god view: numbered, color-coded, active cluster highlighted

**Estimation improvements:**
- **Running total average** added — weighted average of ALL observations ever (most stable)
- **Kalman filter** added — 2D Bayesian filter with varying measurement noise (needs tuning)
- **Inverse variance weighting** — weight ∝ 1/altitude² (10m observations 9x more valuable than 30m)
- Centre-snap observations get 10x bonus weight (target at frame centre = minimal projection error)
- Three markers on god view: circle (rolling 50), square "T" (total avg), triangle "K" (Kalman)

**Altitude test (H key):**
- Automatically steps through 30/25/20/15/10m altitude, hovers 10s each
- Prints comparison table of all three estimators at each altitude
- Confirmed: lower altitude = better estimate (fewer metres per pixel)

**Investigate mode fixes:**
- During investigate, observations forced to investigated cluster (skip distance routing)
- N key uses total average position (not rolling 50) for consistency
- Simple "park and hold" — fly to initial estimate, hover, don't chase updates
- L key prefers total average from active cluster for landing estimate

**Key changes:**
- F key → X key for false positive (F was conflicting with throttle down)
- Tab key cycles scatter plot reference through all placed dummies
- Permanent cluster IDs (pop() no longer shifts numbering)
- `--cluster-dist` CLI flag (default 30m)

**Documentation added:**
- `docs/CV_GUIDE.md` — new section: "GPS Estimation: Error Sources, Compensation, and Best Practices"
  - Error source table (random vs systematic)
  - FOV calibration explained as only systematic error
  - Inverse variance weighting explanation
  - Altitude test results
  - Simulation vs reality comparison
  - Operational flow for first flight
  - SAR industry best practices (confirmed by research)
- `docs/FIRST_FLIGHT.md` — new file: first flight plan with progressive steps
  - Step 1: Mission Planner AUTO waypoints (no code)
  - Step 2: pi_passive_flight.py (passive CV, zero commands)
  - Step 3: Manual flight with N/Y/I/X/L controls (future)
  - Step 4: Full autonomous main.py (future)
  - Pre-flight checklist, measurement plan, Pi setup reminder

**Pi compatibility assessment:**
- simple_simulator.py is laptop-only (needs cv2.imshow, map.jpg, simulation.py)
- For first real flight: use pi_passive_flight.py (passive, proven on Pi)
- Pi venv may need recreating if code is re-uploaded (requirements_pi.txt + ai-edge-litert)

**Files modified:**
- `simple_simulator.py` — clustering, permanent IDs, total average, Kalman filter, altitude test,
  inverse variance weighting, Tab key, H key, X key, investigate fixes
- `simulation.py` — cluster rendering in god view (numbered markers, total avg squares, Kalman triangles)
- `docs/CV_GUIDE.md` — GPS estimation error sources section added
- `docs/FIRST_FLIGHT.md` — new file, first flight plan

**Next steps:**
- [ ] Push to git, pull on Pi
- [ ] Test detection with corrected colors on Pi (BGR fix from 2026-02-17)
- [ ] Outdoor GPS fix test
- [ ] Step 1: Mission Planner AUTO waypoints
- [ ] Step 2: pi_passive_flight.py during manual RC flight
- [ ] FOV calibration on bench (pi_6_fov_test.py)

### Session: 2026-02-20 (part 2) — pi_flight.py web ground station + flight day prep

**Continued from part 1 (ran out of context, continued in new session).**

**Created `pi_flight.py`** — web-based ground station for real flights (~1016 lines):
- Serves dashboard at `http://localhost:8090` (or Pi IP on same WiFi)
- Works in both SIMULATION (laptop + SITL) and REAL (Pi + Cube) modes
- **No `cv2.imshow`** — fully headless, all UI through browser
- Key components:
  - MJPEG video stream with detection overlay (green boxes + confidence)
  - 2D GPS grid showing drone position (arrow), detection clusters (color-coded), logged items
  - Command buttons: ARM, TAKEOFF, N (investigate), Y (confirm), I (interest), X (false pos), L (land), M (resume)
  - Status bar: flight mode, drone mode, GPS, altitude, detection count, battery
  - Detection alerts (orange flash when new detection)
  - Cluster info panel (click cluster to select for investigation)
  - Keyboard shortcuts in browser (N/Y/I/X/L/M keys)
- Terminal keyboard control (WASD flight) for simulation testing
- Same GPS estimation math as simple_simulator.py:
  - Pixel-to-GPS projection, centre-snap, inverse variance weighting
  - Spatial clustering with permanent IDs
  - Rolling 50 + running total average
- Investigate flow: approaching → descending to 15m → observing (captures snapshot)
- Landing flow: 7.5m north offset → fly to → descend → landed
- ThreadingMixIn HTTP server for concurrent stream + API requests
- `request_data_stream_send()` after MAVLink connect (required for SITL to send GPS/attitude)

**Tested in SIMULATION on laptop:**
- Dashboard loads in browser, grid renders, buttons visible
- Fixed layout: buttons were cut off (flex:1.5 → flex:1, better height calc)
- Fixed static video: SITL requires explicit data stream request — added to `_connect_mavlink()`
- Status bar shows: MANUAL [GUIDED], BAT: 12.6V, GPS coordinates

**Ground station architecture confirmed:**
```
Cube → Pi UART → mavproxy
                    ├── udpout:127.0.0.1:14550  → pi_flight.py (commands + telemetry)
                    └── tcpin:0.0.0.0:5762       → Mission Planner (monitoring, read-only)
```
- Browser dashboard: operator interface (camera, detections, commands)
- Mission Planner: safety monitor (map, instruments, failsafe)
- RC controller: always has override priority (STABILIZE kill switch)

**Flight day plan confirmed:**
1. **pi_passive_flight.py** first — fly over dummy, measure CV (zero commands, zero risk)
2. **pi_flight.py** second — full dashboard with N/Y/I/X/L commands

**Model preparation started (not completed):**
- Created `models/` directory
- Copied `best.tflite` → `models/custom_yolov8n.tflite` as baseline
- COCO yolov8n export attempted but missing ONNX dependencies
- Installed onnx, onnxslim, onnxruntime in venv
- Remaining exports deferred to next session (onnx2tf dependency issues)
- **TODO for next session**: Export COCO person detector, INT8 quantized, yolov8s models
- **TODO**: Consider using pretrained YOLO person detection (COCO class 0) as fallback
- **TODO**: Retrain custom model with more diverse dummy images (different positions, angles, lighting)

**Added FAKE DET button to pi_flight.py:**
- Browser button that creates a fake detection at drone's current GPS or custom coordinates
- Allows testing full investigate → classify → land sequence without CV working
- Useful on flight day if model doesn't detect from altitude

**Created `docs/FLIGHT_DAY_CHECKLIST.md`:**
- Single printable document for flight day — follow top to bottom
- Phase 0: push code, charge, pack
- Phase 1: Pi setup, mavproxy, diagnostics, MP connection
- Phase 2: GPS lock (wait for green LED)
- Phase 3: RC setup, kill switch test
- Phase 4: FOV calibration (camera + ruler → update FOCAL_LENGTH_MM)
- Phase 5: inference benchmark (measure FPS on Pi)
- Phase 6: dummy placement, note GPS
- Step 1: MP AUTO waypoints (no code)
- Step 2: passive CV (pi_passive_flight.py — zero commands)
- Step 3: full dashboard (pi_flight.py — N/Y/I/X/L commands)
- After-flight recording template (results, config updates needed)
- Quick reference: all commands, model swap instructions

**Audited flight readiness:**
- All core scripts compile and are ready
- Some pi_1 through pi_9 scripts only exist on Pi (not in git), but tests2/ has equivalent or better versions
- FOV calibration scripts exist in both tests/ and tests2/
- Confidence threshold is 0.4 in vision.py (lines 174 and 197)

**Files created:**
- `pi_flight.py` — web ground station (~1030 lines, with FAKE DET)
- `models/custom_yolov8n.tflite` — copy of current best.tflite
- `docs/FIRST_FLIGHT.md` — first flight plan (created in part 1)
- `docs/FLIGHT_DAY_CHECKLIST.md` — single printable flight day document
- `docs/CV_GUIDE.md` — GPS estimation section (added in part 1)

**Files modified:**
- `CLAUDE.md` — session log, file structure, current state updated

**Installed in venv (partial — for model export):**
- onnx, onnxslim, onnxruntime (installed OK)
- onnx2tf, sng4onnx, onnx_graphsurgeon (failed — dependency issues on Windows)

**Known issues / future work:**
- Model export pipeline needs ONNX → TF SavedModel → TFLite chain (onnx2tf install failed on Windows)
- May need to export models on Linux/WSL instead of Windows
- Custom dummy model trained on synthetic composites only — need real photos for better accuracy
- COCO "person" class may work as fallback (dummy is human-shaped)
- pi_flight.py not yet tested on Pi hardware (tested in SIMULATION only)
- Some pi_1-pi_9 test scripts missing from git (exist on Pi only) — tests2/ covers same functionality

**Next steps (before flight day):**
- [ ] Push all code to git, pull on Pi
- [ ] Recreate pienv on Pi if needed (requirements_pi.txt + ai-edge-litert)
- [ ] Export alternative TFLite models (COCO person, INT8, yolov8s) — try on WSL if Windows fails
- [ ] Retrain custom model with diverse dummy images (different positions, angles, lighting)
- [ ] Test pi_flight.py in SIMULATION (verify video stream fix works)
- [ ] Configure RC controller (kill switch = STABILIZE, failsafe = RTL)
- [ ] Follow FLIGHT_DAY_CHECKLIST.md on flight day

---

**INSTRUCTIONS FOR LLM**: When starting a new session, read this file first. Then read
whichever doc is relevant to the user's current task. Always update the "Current State"
section and "Session Log" when work is completed. Keep this document as the single source
of truth.
