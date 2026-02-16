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

**REAL MODE: CODE READY, UNTESTED ON HARDWARE** — Same main.py runs in REAL mode
with real camera + SITL on laptop. Interactive polygon drawing works. Webcam detection
tested. Not yet tested on Pi or with real Cube.

### What Works
- Full state machine: INIT → CONNECTING → ARMING → TAKEOFF → SEARCH → CENTERING → DESCENDING → VERIFY → APPROACH → LANDING → DONE
- Lawnmower search pattern generation from any polygon
- AI detection with dual backend (Ultralytics on laptop, TFLite on Pi)
- Interactive polygon drawing in both SIMULATION and REAL mode
- Config auto-detection (SITL on laptop, serial Cube on Pi)
- Manual override (M key) and RC kill switch support
- Preflight connectivity checker (preflight.py)

### What's Not Done Yet
- [ ] Pi setup (OS, venv, dependencies)
- [ ] Camera tested on Pi
- [ ] TFLite inference tested on Pi
- [ ] Cube wired to Pi and tested
- [ ] Bench test (no props) with real Cube
- [ ] Manual flight with passive detection (calibrate altitude)
- [ ] Full autonomous flight

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
├── simulation.py              ← Laptop-only sim: map.jpg + simulated drone camera view
├── preflight.py               ← Standalone connectivity checker (camera, Cube, AI model)
│
├── best.tflite                ← AI model file (~6MB, YOLOv8n exported to TFLite)
├── map.jpg                    ← Satellite image for simulation (~12MB)
├── dummy.png                  ← Dummy/casualty image for dataset generation + bench test
├── generate_dataset.py        ← Creates synthetic training data from map.jpg + dummy.png
├── test_flight10.py           ← Legacy flight test script
│
├── requirements_dev.txt       ← Laptop: pymavlink, opencv, numpy, ultralytics, matplotlib
├── requirements_pi.txt        ← Pi: pymavlink, opencv-headless, numpy, tflite-runtime
│
├── docs/
│   ├── ARCHITECTURE.md        ← System overview, evolving diagrams, hardware checklist
│   ├── PI_SETUP.md            ← Step-by-step Pi setup and testing guide
│   ├── CV_GUIDE.md            ← Vision system, optimization stages, model swapping
│   ├── NEXT_STEPS.md          ← Phase-by-phase development plan
│   ├── CONNECTIVITY.md        ← Connection debugging guide
│   ├── PREFLIGHT_CHECKLIST.md ← Pre-flight safety checks
│   ├── TEAM_PLAN.md           ← Team workstreams and responsibilities
│   └── ROADMAP.md             ← Full 10-phase development history
│
└── tests/
    ├── pi_1_camera.py         ← Test: camera gives frames (OpenCV or picamera2)
    ├── pi_2_detect.py         ← Test: live AI detection (--headless for SSH)
    ├── pi_3_benchmark.py      ← Test: inference speed (50 runs, timing report)
    ├── pi_4_detect_and_log.py ← Test: camera + Cube + buzzer + CSV logging
    ├── pi_5_guidance.py       ← Test: detection + directional commands (--headless)
    ├── pi_6_fov_test.py       ← Test: FOV calibration on bench (--headless)
    ├── pi_7_alt_test.py       ← Test: FOV calibration at altitude (--headless)
    ├── pi_8_camera_test.py    ← Test: FPS + motion blur impact (--headless)
    ├── pi_9_resolution_test.py← Test: resolution vs speed vs detection quality
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
simulation.py ......... Laptop-only simulation (map + simulated drone view)
preflight.py .......... Connectivity checker (standalone tool)
tests/ ................ All test scripts (pi_1 through pi_9, test_cube, etc.)
```

### Key Design Decisions
- **vision.py is the ONLY file that touches CV/AI.** Everything else calls `detect_in_image(frame)` → `(found, x, y, conf)`. You can change the model, preprocessing, backend without touching any other file.
- **config.py auto-detects hardware.** Serial port → real Cube. No serial → SITL. Env var overrides everything. No code changes between laptop and Pi.
- **Same main.py for simulation and real.** The MODE flag only changes camera source and connection string. State machine logic is identical.
- **Interactive polygon drawing in REAL mode.** If map.jpg available, shows map for drawing. If headless (Pi), falls back to SEARCH_AREA_GPS in config.py.

## File Locations

| File | Purpose | Notes |
|------|---------|-------|
| best.tflite | AI model (YOLOv8n exported to TFLite) | ~6MB, tracked in git |
| best.pt | YOLO weights (full, laptop only) | In .gitignore (large) |
| map.jpg | Satellite image for simulation | ~12MB, tracked in git |
| dummy.png | Test dummy image | For generate_dataset.py and bench testing |
| flight_log.csv | Runtime log | In .gitignore (changes every run) |
| requirements_dev.txt | Laptop dependencies | pymavlink, opencv, numpy, ultralytics, matplotlib |
| requirements_pi.txt | Pi dependencies | pymavlink, opencv-headless, numpy, tflite-runtime |

## How to Run

### Simulation (laptop)
```bash
# Need: SITL running (Mission Planner or mavproxy), venv activated
set DRONE_MODE=SIMULATION      # Windows
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
git checkout MainOne2

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
python simple_simulator.py
```

**Known issue**: On Windows, use `python -m pip` instead of `pip` if pip.exe gives
"Fatal error in launcher". Also use `cmd /c "python -m pip freeze > file.txt"` when
freezing — PowerShell's `>` creates UTF-16 which pip can't read.

### WSL / Linux (Docker-style testing)

```bash
# 1. Clone
git clone https://github.com/DimaChup/Group_Proj.git
cd Group_Proj
git checkout MainOne2

# 2. Create venv
python3 -m venv venv
source venv/bin/activate

# 3. Install
pip install -r requirements_dev.txt

# 4. Verify
python -c "import cv2; print('OpenCV:', cv2.__version__)"
python -c "import ultralytics; print('Ultralytics:', ultralytics.__version__)"
```

### Raspberry Pi (Production)

```bash
# 1. Clone
git clone https://github.com/DimaChup/Group_Proj.git ~/sar-drone
cd ~/sar-drone
git checkout MainOne2

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
| `requirements_dev.txt` | Windows/Linux laptop | Full pip freeze (~90 packages, exact versions) |
| `requirements_pi.txt` | Raspberry Pi | 4 lightweight packages (pymavlink, opencv-headless, numpy<2, tflite-runtime) |

Both files MUST be UTF-8 encoded. If regenerating on Windows, use:
```bash
cmd /c "python -m pip freeze > requirements_dev.txt"
```

## The Approach: Simulation → Real

We don't jump to flying. Progression:

1. **Simulation on laptop** (DONE) — prove logic works
2. **Real camera + SITL on laptop** (DONE) — prove real camera + AI works
3. **Pi + camera (no Cube)** — prove vision on real hardware
4. **Pi + camera + Cube (bench, no props)** — prove commands are correct
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
pi_8_camera_test.py ..... FPS + blur impact?  (--headless)
pi_9_resolution_test.py . Best resolution?
pi_6_fov_test.py ........ FOV calibration?  (--headless)
pi_5_guidance.py ........ Centering commands?  (--headless)
test_cube.py ............ Cube heartbeat + GPS?
pi_4_detect_and_log.py .. Camera + Cube + buzzer together?
pi_7_alt_test.py ........ FOV at real altitude? (flight day)
preflight.py ............ All systems go?
```

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
- Current working branch: MainOne2

## Session Log

Track what was done each session so context is never lost.

### Session: 2026-02-16
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

---

**INSTRUCTIONS FOR LLM**: When starting a new session, read this file first. Then read
whichever doc is relevant to the user's current task. Always update the "Current State"
section and "Session Log" when work is completed. Keep this document as the single source
of truth.
