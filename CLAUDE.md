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
├── simulation.py              ← Laptop-only sim: map.jpg + simulated drone camera view
├── preflight.py               ← Standalone connectivity checker (camera, Cube, AI model)
│
├── best.tflite                ← AI model file (~6MB, YOLOv8n exported to TFLite)
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

**Next: Push to git, pull on Pi, outdoor GPS test, then Step 1 (Mission Planner AUTO waypoints)**

---

**INSTRUCTIONS FOR LLM**: When starting a new session, read this file first. Then read
whichever doc is relevant to the user's current task. Always update the "Current State"
section and "Session Log" when work is completed. Keep this document as the single source
of truth.
