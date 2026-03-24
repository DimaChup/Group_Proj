# SAR Drone — Autonomous Search and Rescue

University of Bristol MSc project (AENGM0074). Autonomous drone that flies a search pattern, detects a casualty using onboard AI (YOLOv8), and delivers a payload to the target location.

## Quick Start

### Prerequisites

1. **SITL running** — Start Mission Planner → SIMULATION tab → click "Start"
2. **Python venv** — `test_env` or `venv` with dependencies installed
3. **Windows**: use `set DRONE_MODE=SIMULATION` (cmd) or `export DRONE_MODE=SIMULATION` (bash/WSL)

### Recommended Launch (Setting 1)

This is the tested, working combination:

```bash
DRONE_MODE=SIMULATION python main.py \
  --search-area \
  --no-descend \
  --speed 5 \
  --no-turn \
  --transit flight_plans/transit.json
```

**What this does:**
- `--search-area` — Pre-loads the survey polygon from KML (no interactive drawing)
- `--no-descend` — Stays at search altitude for verification (doesn't descend to 15m)
- `--speed 5` — 5x SITL time acceleration (faster simulation)
- `--no-turn` — Drone strafes between waypoints (no yaw rotation)
- `--transit flight_plans/transit.json` — Flies a pre-drawn path to/from the search area

### Workflow

1. **God-view window** opens with satellite map
2. **Left-click** to place targets (first = real dummy, rest = decoys). Press **C** to toggle dummy/cone.
3. **Right-click** when done placing targets
4. **Press any key** to launch the mission
5. Drone arms, takes off, flies transit path, then lawnmower search pattern
6. On detection → **VERIFY** prompt:
   - **Y** = Confirm target → choose landing side (N/E/S/W) → payload delivery → RTL
   - **I** = Item of Interest (blue marker, continues search)
   - **N** = False positive (red marker, continues search)
7. Drone retraces transit path and lands at home

---

## All CLI Flags

### Mission Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--search-area` | off | Pre-load search polygon from KML (skip interactive drawing) |
| `--no-descend` | off | Stay at search altitude during verification |
| `--no-turn` | off | Strafe between waypoints (no yaw rotation) |
| `--nfz-repel` | off | Enable SSSI no-fly zone repulsive force field |
| `--speed N` | 1 | SITL time multiplier (e.g. `--speed 5` for 5x faster) |
| `--alt N` | 50 | Override search altitude in metres |
| `--dry-run` | off | No GPS/arm — just show the search pattern and exit |
| `--headless` | auto | No cv2 windows (auto-detected on Pi/SSH) |

### Path Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--transit FILE` | none | Pre-drawn transit path JSON (flown to/from search area) |
| `--waypoints FILE` | none | Pre-drawn waypoints to fly before search pattern |
| `--pattern TYPE` | lawnmower | Search pattern algorithm (`lawnmower` or `spiral`) |
| `--smooth-bezier` | off | Bezier curves at turns (smooth arcs) |
| `--smooth-extra` | off | Extra waypoints at turns (wider arc) |

### Model Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--model PATH` | `best.tflite` | Path to TFLite model file |

### Stream Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--stream-port N` | 8090 | HTTP stream server port |
| `--stream-res WxH` | 320x240 | Stream resolution |
| `--stream-fps N` | 5 | Stream frame rate |
| `--stream-quality N` | 50 | JPEG quality (1-100) |
| `--no-stream` | off | Disable web stream entirely |

---

## Preset Configurations

### Setting 1 — Full Simulation (recommended)

```bash
DRONE_MODE=SIMULATION python main.py --search-area --no-descend --speed 5 --no-turn --transit flight_plans/transit.json
```

### Setting 2 — With NFZ Geofence (repulsive force)

```bash
DRONE_MODE=SIMULATION python main.py --search-area --no-descend --speed 5 --no-turn --transit flight_plans/transit.json --nfz-repel
```

Adds SSSI no-fly zone protection:
- **Orange buffer ring** (10m) drawn around SSSI on god-view
- **Repulsive force** pushes drone away when within 10m of boundary (up to 5 m/s)
- **Auto-manual** if drone enters NFZ — operator flies out, press M to resume
- No speed reduction, no RTL (repulsion only)

### Setting 3 — Dry Run (no SITL needed)

```bash
python main.py --dry-run
```

Shows the lawnmower pattern, tests the pipeline, saves `dry_run_pattern.jpg`. No connection needed.

### Setting 4 — Alternate Model

```bash
DRONE_MODE=SIMULATION python main.py --search-area --no-descend --speed 5 --model cv_models/sar_v2_1088/best.tflite
```

### Setting 5 — Real Flight on Pi

```bash
python main.py --search-area --transit flight_plans/transit.json
```

No `--speed` (real time), no `DRONE_MODE` (auto-detects Cube on serial port). Requires mavproxy running.

---

## Controls

### Keyboard (God-View Window)

| Key | Action | When |
|-----|--------|------|
| **Y** | Confirm target | VERIFY state |
| **N** | Reject (false positive) | VERIFY state |
| **I** | Item of Interest (blue marker) | VERIFY state |
| **N/E/S/W** | Choose landing side | After Y confirm |
| **M** | Toggle Manual Override | Any state |
| **W/A/S/D** | Fly North/West/South/East | Manual mode |
| **R/F** | Climb / Descend | Manual mode |
| **Q/E** | Yaw left / right | Manual mode |
| **ESC** | Quit mission | Any time |

### Browser (http://localhost:8090/)

The web dashboard provides the same controls as buttons, plus a live MJPEG video stream. Works over SSH/headless on the Pi.

| Button | Key | Action |
|--------|-----|--------|
| Y Confirm | `y` | Confirm target |
| N Reject | `n` | Reject target |
| M Manual | `m` | Toggle manual override |
| North/East/South/West | `n/e/s/w` | Landing direction |

**HTTP API:** `GET /cmd?key=y` sends a command programmatically.

---

## Mission States

```
INIT → CONNECTING → ARMING → TAKEOFF
  → PRE_WAYPOINTS (if --waypoints)
  → TRANSIT_TO_SEARCH (if --transit)
  → SEARCH (lawnmower pattern)
    → on detection: CENTERING → DESCENDING → VERIFY
      → Y: APPROACH → HOVER_TARGET → LANDING
      → N: RETURN_TO_SEARCH → SEARCH (continue)
      → I: mark blue, RETURN_TO_SEARCH → SEARCH (continue)
  → RETURN_TRANSIT (if --transit)
  → RETURN_HOME → LANDING → DONE
```

At any time: **M** enters MANUAL mode (WASD flight). Press **M** again to resume.

---

## Project Structure

```
v3/
├── main.py                    Mission orchestrator (state machine)
├── config.py                  All settings (auto-detects SITL vs real hardware)
├── states.py                  State enum
├── vision.py                  Camera + AI detection (dual backend: Ultralytics/TFLite)
├── planning.py                Lawnmower search pattern generator
├── navigation.py              MAVLink commands (goto, velocity, land)
├── geofence.py                NFZ boundary checking + repulsive offset
├── utils.py                   GPS <-> pixel math (GeoTransformer)
├── state_machine.py           Full state machine (with descent)
├── state_machine_no_descend.py  No-descend variant
├── stream_server.py           HTTP MJPEG stream + browser dashboard
│
├── best.tflite                Active AI model (swap to change detection)
├── cv_models/                 All trained model variants
│   ├── sar_v2_1088/           Best model (mAP50=0.995) ← RECOMMENDED
│   ├── sar_640/               Earlier 640x640 training
│   └── sar_1280/              Earlier 1280x1280 training
├── models/                    Alternative models
│   ├── human.tflite           COCO person detector (80 classes, backup)
│   └── custom_yolov8n.tflite  Original custom dummy detector
│
├── flight_plans/              Pre-drawn paths (JSON)
│   ├── transit.json           Transit path to/from search area
│   ├── search_area.json       Search polygon vertices
│   ├── waypoints.json         Pre-planned waypoints
│   ├── AENGM0074.kml         Official KML zones (takeoff, survey, flight area, SSSI)
│   ├── draw_transit.py        Interactive tool: draw transit path on map
│   ├── draw_search_area.py    Interactive tool: draw search polygon on map
│   └── draw_waypoints.py      Interactive tool: draw waypoints on map
│
├── simple_simulator.py        Interactive MVP (keyboard flight + CV + GPS estimation)
├── pi_flight.py               Web ground station for real flights
├── passive_watch.py           Passive camera observer (zero commands)
├── capture_training.py        Training data capture (video + photos)
├── preflight.py               Pre-flight connectivity checker
│
├── tests/                     All test scripts
│   ├── hardware/              Component checks (benchmark, GPS, buzzer)
│   ├── flight/                Progressive flight tests (0a → 4)
│   ├── diagnostics/           Monitoring dashboards, camera streams
│   ├── calibration/           FOV, lens distortion, GPS ground truth
│   ├── day_1_experiments/     Structured data collection (CSV output)
│   └── laptop/                Development tools (video analysis, model testing)
│
├── docs/                      Documentation
├── dashboard/                 React web app (project tracker)
└── assets/                    Map images, dummy image
```

---

## Other Scripts

| Script | Purpose | Commands Sent | Port |
|--------|---------|---------------|------|
| `simple_simulator.py` | Interactive keyboard flight + CV + GPS estimation | Simulated only | — |
| `pi_flight.py` | Web-based ground station (browser dashboard) | Yes (full mission) | 8090 |
| `passive_watch.py` | Stream + AI detection during manual RC flight | **ZERO** | 8090 |
| `capture_training.py` | Record video + photos for model retraining | **ZERO** | 8091 |
| `preflight.py` | Check camera, Cube, AI model connectivity | **ZERO** | — |

### simple_simulator.py

```bash
python simple_simulator.py --fps 4 --tflite --gps-drift 3 --shake 5
```

Keys: `SPACE`=arm, `WASD`=fly, `C`=GPS center, `V`=visual servo, `G`=GPS lock, `L`=land, `B`=record

### passive_watch.py (safe for manual flights)

```bash
python passive_watch.py --port 8090 --conf 0.4 --fps 5
```

Pilot flies on RC, Pi runs camera + AI, logs detections. Sends **zero** commands.

---

## Model Swapping

All scripts read `best.tflite` from the project root. To swap models:

**Option 1 — CLI flag (no file changes):**
```bash
python main.py --model cv_models/sar_v2_1088/best.tflite
```

**Option 2 — Copy (persists across runs):**
```bash
cp cv_models/sar_v2_1088/best.tflite best.tflite
```

**Available models:**

| Model | Size | Notes |
|-------|------|-------|
| `cv_models/sar_v2_1088/best.tflite` | 11.7 MB | **Best** — retrained on real + synthetic data, mAP50=0.995 |
| `cv_models/sar_640/best.tflite` | ~3 MB | Earlier training at 640x640 |
| `cv_models/sar_1280/best.tflite` | ~3 MB | Earlier training at 1280x1280 |
| `models/human.tflite` | 13 MB | COCO YOLOv8n person detector (80 classes, backup) |

All models share the same input `[1,640,640,3]` and output `[1,5,8400]` — drop-in replacements.

---

## Environment Setup

### Windows (Development)

```bash
git clone https://github.com/DimaChup/Group_Proj.git
cd Group_Proj
python -m venv test_env
test_env\Scripts\activate
python -m pip install -r requirements_dev.txt
```

### Raspberry Pi (Production)

```bash
git clone https://github.com/DimaChup/Group_Proj.git ~/sar-drone
cd ~/sar-drone
python3 -m venv --system-site-packages pienv
source pienv/bin/activate
pip install -r requirements_pi.txt
```

### Requirements Files

| File | Platform | Contents |
|------|----------|----------|
| `requirements_dev.txt` | Windows laptop | Full pip freeze (~90 packages) |
| `requirements_linux.txt` | WSL / Linux | Full pip freeze (no Windows packages) |
| `requirements_pi.txt` | Raspberry Pi | 4 lightweight packages only |

---

## Flight Testing Progression

**Never skip a step.** Each builds trust before adding risk.

1. **Mission Planner AUTO waypoints** — Upload square pattern in MP, fly in AUTO mode. Your code not involved.
2. **Waypoint test script** (`tests/flight/2_waypoint_test.py`) — Your code arms + flies GPS waypoints. No camera.
3. **Manual flight + passive CV** (`passive_watch.py`) — Pilot flies RC, Pi detects + logs. Zero commands.
4. **Autonomous search, log only** — main.py with detection logging but no action on detections.
5. **Full autonomous mission** — Everything enabled. Operator confirms Y/N at VERIFY.

---

## Key Configuration (config.py)

| Setting | Value | Notes |
|---------|-------|-------|
| `TARGET_ALT` | 50m | Search altitude (tune after real testing) |
| `VERIFY_ALT` | 15m | Verification altitude (with descent) |
| `SEARCH_SPEED_MPS` | 5 m/s | Drone speed during search |
| `IMAGE_W` | 1456 | Pi camera native width |
| `IMAGE_H` | 1088 | Pi camera native height |
| `FOCAL_LENGTH_MM` | 5.46 | Calibrated 2026-03-11 |
| Confidence threshold | 0.4 | In vision.py |

Config auto-detects the platform: serial port found → real Cube, otherwise → SITL on localhost.

---

## Branches

| Branch | Purpose |
|--------|---------|
| `Working` | Known-good version (tested, full mission works) |
| `Working2` | Active development branch |
| `dima1` | Stable backup |
| `MainOne2` | Main integration branch |
| `refactor-modular` | Modular refactor (NCNN, pytest, extracted modules) |
