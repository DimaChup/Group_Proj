# main.py Launch Guide

> Complete reference for launching main.py. Covers every flag, path setup, model selection, and mode combination.

---

## Quick Reference

```bash
# Activate venv first (always required)
# Windows:  venv\Scripts\activate
# Pi:       source pienv/bin/activate

# Dry-run (no Cube, no GPS, no flying — just verify pattern)
python main.py --dry-run

# Simulation (needs SITL running in Mission Planner)
set DRONE_MODE=SIMULATION          # Windows cmd
export DRONE_MODE=SIMULATION       # Linux/Pi/WSL
python main.py

# Full real flight with preloaded paths
python main.py --search-area --waypoints flight_plans/waypoints.json --transit flight_plans/transit.json

# Full real with alternate model + headless (Pi over SSH)
python main.py --search-area --transit flight_plans/transit.json --model cv_models/sar_v2_1088/best.tflite --headless
```

---

## All CLI Flags

| Flag | Argument | Default | Description |
|------|----------|---------|-------------|
| `--dry-run` | — | off | Skip GPS/arm/fly. Shows pattern, prints state walkthrough, saves `dry_run_pattern.jpg` |
| `--model` | path | `best.tflite` | TFLite model file for AI detection |
| `--search-area` | — | off | Skip interactive polygon drawing, use KML survey area from `AENGM0074.kml` |
| `--waypoints` | file.json | none | Pre-planned waypoints flown BEFORE the search pattern |
| `--transit` | file.json | none | Transit path from takeoff to search area entry point |
| `--speed` | number | `1` | SITL simulation speedup multiplier (e.g., 1, 5, 10) |
| `--no-turn` | — | off | Quadcopter strafes between waypoints (no yaw rotation at turns) |
| `--pattern` | name | `lawnmower` | Search pattern type (`lawnmower` or `spiral`) |
| `--headless` | — | auto | No cv2 windows. Auto-enabled on Pi when no DISPLAY. Enables terminal + browser input |
| `--no-stream` | — | off | Disable MJPEG video stream server |
| `--stream-port` | number | `8090` | HTTP stream server port |
| `--stream-res` | WxH | `320x240` | Stream resolution (e.g., `640x480`) |
| `--stream-fps` | number | `5` | Stream frame rate |
| `--stream-quality` | 1-100 | `50` | JPEG quality for stream |

---

## Environment Variable

The **only** env var that matters:

```bash
DRONE_MODE=SIMULATION    # Use SITL + simulated camera (laptop)
DRONE_MODE=REAL          # Use real Cube + real camera (Pi or laptop webcam)
```

If not set, `config.py` auto-detects:
- Serial port found (`/dev/ttyAMA0`) → REAL
- No serial port → defaults based on platform

---

## Modes Explained

### 1. Dry-Run (`--dry-run`)

**Purpose:** Verify search pattern, waypoints, and state machine WITHOUT any connection.

```bash
python main.py --dry-run
python main.py --dry-run --search-area
python main.py --dry-run --search-area --transit flight_plans/transit.json --waypoints flight_plans/waypoints.json
```

**What happens:**
1. Loads search polygon (from `flight_plans/search_area.json`, KML, or config.py)
2. Generates lawnmower/spiral waypoints
3. Prints every waypoint GPS coordinate
4. Prints state machine walkthrough (INIT → CONNECTING → ... → LANDING)
5. Shows map visualization with pattern overlay (if `map.jpg` exists)
6. Saves visualization to `dry_run_pattern.jpg`
7. Exits — no arming, no flying, no Cube needed

**No requirements:** No venv packages needed beyond opencv + numpy.

### 2. Simulation (`DRONE_MODE=SIMULATION`)

**Purpose:** Full end-to-end mission on laptop with SITL.

```bash
set DRONE_MODE=SIMULATION
python main.py
```

**Prerequisites:**
- SITL running in Mission Planner (or standalone mavproxy)
- SITL home location: `--home=51.423406,-2.671446,50,155`
- Connection: `tcp:127.0.0.1:5762` (auto-configured by config.py)

**What happens:**
1. Opens `map.jpg` for interactive polygon drawing (or use `--search-area` to skip)
2. Connects to SITL via TCP
3. Arms, takes off, flies search pattern
4. Simulated camera view (cropped from map.jpg based on drone position)
5. AI detection runs on simulated view
6. Full state machine: SEARCH → CENTERING → DESCENDING → VERIFY → LANDING

**Interactive setup (without `--search-area`):**
- Map window opens
- Left-click to place polygon corners
- Right-click to undo
- SPACE/ENTER to confirm
- Can also draw transit path on map

### 3. Real Mode (`DRONE_MODE=REAL`)

**Purpose:** Actual flight with real camera and Cube.

```bash
# On Pi:
python main.py --search-area --transit flight_plans/transit.json --headless

# On laptop with webcam + SITL:
set DRONE_MODE=REAL
python main.py --search-area
```

**Prerequisites:**
- Cube connected (serial on Pi, or SITL for laptop testing)
- Camera available (Pi camera or webcam)
- mavproxy bridge running on Pi (for serial → UDP)
- GPS fix (fix_type >= 3, satellites >= 6)

---

## Search Area Setup (3 methods, in priority order)

main.py loads the search polygon using this priority:

### Priority 1: `flight_plans/search_area.json` (recommended)

Created by the drawing tool on laptop, pushed via git, loaded on Pi automatically.

```bash
# On laptop — draw polygon on satellite map:
python flight_plans/draw_search_area.py
# → Creates flight_plans/search_area.json
# → Push to git, pull on Pi
```

**Format:**
```json
[
  {"lat": 51.423567, "lon": -2.668786, "label": "P1"},
  {"lat": 51.423100, "lon": -2.668200, "label": "P2"},
  {"lat": 51.422800, "lon": -2.669500, "label": "P3"}
]
```

main.py detects `flight_plans/search_area.json` and loads it automatically. No flags needed.

### Priority 2: `--search-area` flag (KML)

Loads the survey polygon from `AENGM0074.kml` (the official field zone).

```bash
python main.py --search-area
```

This calls `config.load_kml_zones()` and uses `config.SEARCH_AREA_GPS`.

### Priority 3: Interactive drawing (simulation only)

If neither JSON nor `--search-area` flag, opens `map.jpg` for interactive drawing. Only works in SIMULATION mode with a display.

### Priority in REAL mode:
1. `flight_plans/search_area.json` exists → use it (no flag needed)
2. `SEARCH_AREA_GPS` in config.py → use it
3. Neither → error, no search pattern

---

## Transit & Waypoint Setup

### Transit Path (`--transit flight_plans/transit.json`)

The route from takeoff to the search area entry point. Avoids no-fly zones.

```bash
# Draw on laptop:
python flight_plans/draw_transit.py
# → Creates flight_plans/transit.json

# Use in flight:
python main.py --transit flight_plans/transit.json
```

**What it does:**
- Drone flies these waypoints BEFORE starting the search pattern
- Search pattern starts from the last transit waypoint (instead of current position)
- In SIMULATION mode, transit path is also drawn on the setup map

### Pre-Waypoints (`--waypoints flight_plans/waypoints.json`)

Additional waypoints flown BEFORE the search pattern. Can combine with transit.

```bash
# Draw on laptop:
python flight_plans/draw_waypoints.py
# → Creates flight_plans/waypoints.json

# Use in flight:
python main.py --waypoints flight_plans/waypoints.json
```

### Combined: Transit + Waypoints

Both are merged into `pre_waypoints` and flown in order:
1. `--waypoints` waypoints first
2. `--transit` waypoints second
3. Then search pattern begins

```bash
python main.py --waypoints flight_plans/waypoints.json --transit flight_plans/transit.json --search-area
```

### JSON Format (same for all three files)

```json
[
  {"lat": 51.423442, "lon": -2.670364, "label": "WP1"},
  {"lat": 51.423198, "lon": -2.670117, "label": "WP2"}
]
```

Also accepts simple arrays:
```json
[[51.423442, -2.670364], [51.423198, -2.670117]]
```

---

## Model Selection

### Available Models

| Model | Path | Size | Notes |
|-------|------|------|-------|
| **Default** | `best.tflite` | 3.2MB | Copy of whichever model is active |
| **Best (v2 retrained)** | `cv_models/sar_v2_1088/best.tflite` | 11.7MB | mAP50=0.995, retrained on real data |
| Earlier 640 | `cv_models/sar_640/best.tflite` | — | Trained at 640x640 |
| Earlier 1280 | `cv_models/sar_1280/best.tflite` | — | Trained at 1280x1280 |
| Original custom | `cv_models/custom_yolov8n.tflite` | 3.2MB | First custom dummy detector |
| COCO person | `cv_models/human.tflite` | 13MB | YOLOv8n 80-class, detects real humans |
| Placeholder | `cv_models/best2.tflite` | 3.2MB | Copy, replace with new model |

### How to Select

**Option A: `--model` flag (temporary, per-run)**
```bash
python main.py --model cv_models/sar_v2_1088/best.tflite
python main.py --model cv_models/human.tflite
```

**Option B: Overwrite `best.tflite` (permanent until changed)**
```bash
cp cv_models/sar_v2_1088/best.tflite best.tflite
python main.py   # uses new model automatically
```

All models are drop-in compatible: same input `[1,640,640,3]`, same output `[1,5,8400]`.

### When to Use Which

| Scenario | Model | Why |
|----------|-------|-----|
| Custom dummy on field | `cv_models/sar_v2_1088/best.tflite` | Best accuracy on our dummy |
| Real human detection | `cv_models/human.tflite` | COCO-trained, detects people |
| Quick bench test | `best.tflite` (default) | Whatever's currently active |
| Comparing models | Use `--model` flag | Switch per-run without copying |

---

## Headless Mode (Pi / SSH)

```bash
python main.py --headless
# Auto-detected on Pi when no DISPLAY env var
```

**What changes:**
- No `cv2.imshow` windows (would crash over SSH)
- Terminal keyboard input thread reads keypresses from PuTTY/SSH
- Browser UI at `http://PI_IP:8090` with buttons: Y Confirm, N Reject, M Manual, etc.
- HTTP endpoint: `http://PI_IP:8090/cmd?key=y` for programmatic commands

**Browser controls:**
| Button | Key | Action |
|--------|-----|--------|
| Y Confirm | `y` | Confirm target at VERIFY stage |
| N Reject | `n` | Reject and resume search |
| M Manual | `m` | Toggle manual override |
| North/East/South/West | `w/d/s/a` | Nudge drone direction |
| E Stop | `e` | Emergency — switches to LOITER |

---

## Stream Server

Enabled by default. Serves MJPEG video + control buttons.

```bash
# Default: stream on port 8090
python main.py

# Custom port and resolution
python main.py --stream-port 9000 --stream-res 640x480 --stream-fps 10 --stream-quality 80

# Disable entirely
python main.py --no-stream
```

**Access:** Open `http://localhost:8090` (or `http://PI_IP:8090` from another device).

---

## Common Launch Combinations

### Laptop Development

```bash
# Quick pattern check (no SITL needed)
python main.py --dry-run --search-area

# Full simulation
set DRONE_MODE=SIMULATION
python main.py

# Simulation with preloaded everything
set DRONE_MODE=SIMULATION
python main.py --search-area --transit flight_plans/transit.json --waypoints flight_plans/waypoints.json

# Test alternate model in simulation
set DRONE_MODE=SIMULATION
python main.py --model cv_models/human.tflite
```

### Pi Flight Day

```bash
# Terminal 1: Start mavproxy
sudo /opt/mavlink/mavlink-venv/bin/mavproxy.py \
  --master=/dev/ttyAMA0 --baudrate=921600 --streamrate=10 \
  --out=udpout:127.0.0.1:14550 --out=tcpin:0.0.0.0:5762

# Terminal 2: Launch mission
source pienv/bin/activate
cd ~/sar-drone

# Option A: Full autonomous with v2 model
python main.py --search-area --transit flight_plans/transit.json --model cv_models/sar_v2_1088/best.tflite

# Option B: With custom waypoints
python main.py --search-area --waypoints flight_plans/waypoints.json --transit flight_plans/transit.json

# Option C: Minimal (flight_plans/search_area.json loaded automatically)
python main.py
```

### Drawing Paths (laptop only, before flight day)

```bash
# 1. Draw search polygon → flight_plans/search_area.json
python flight_plans/draw_search_area.py

# 2. Draw transit route → flight_plans/transit.json
python flight_plans/draw_transit.py

# 3. Draw test waypoints → flight_plans/waypoints.json
python flight_plans/draw_waypoints.py

# 4. Verify with dry-run
python main.py --dry-run --search-area --transit flight_plans/transit.json

# 5. Push to git for Pi
git add flight_plans/search_area.json flight_plans/transit.json flight_plans/waypoints.json
git commit -m "Update flight paths"
git push
```

---

## State Machine Flow

```
INIT → CONNECTING → ARMING → TAKEOFF
  → PRE_WAYPOINTS (if --waypoints or --transit provided)
  → TRANSIT_TO_SEARCH
  → SEARCH (lawnmower/spiral pattern)
  → CENTERING (target detected → center in frame)
  → DESCENDING (descend to VERIFY_ALT)
  → VERIFY (operator confirms Y/N)
    → Y: APPROACH → LANDING → DONE
    → N: RETURN_TO_SEARCH → SEARCH (continue pattern)
  → MANUAL (M key override at any time, RC always has priority)
```

**Kill switch:** RC mode switch to STABILIZE/LOITER overrides everything at any time.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `No module 'pymavlink'` | Activate venv: `venv\Scripts\activate` or `source pienv/bin/activate` |
| Exits immediately, no output | SITL not running — start Mission Planner SITL first |
| `No search area defined` | Create `flight_plans/search_area.json` (draw tool) or add `--search-area` flag |
| Black camera in REAL mode | Check camera connected, not in use by another script |
| `Connection timeout` | Check mavproxy is running, correct port (14550 UDP) |
| Dry-run shows no map | `map.jpg` not found in project root (pattern still prints to console) |
| Stream not accessible | Check firewall, correct IP, port 8090 open |
| Detection not working | Verify `best.tflite` exists and is correct model (benchmark first) |

---

## Config Values That Affect Flight

These are in `config.py` — tune after real testing:

```python
TARGET_ALT = 50.0        # Search altitude (meters)
VERIFY_ALT = 15.0        # Descent altitude for confirmation
SEARCH_SPEED_MPS = 5.0   # Speed during search pattern
TRANSIT_SPEED_MPS = 8.0  # Speed flying to/from search area
IMAGE_W = 1456           # Camera resolution width
IMAGE_H = 1088           # Camera resolution height
FOCAL_LENGTH_MM = 5.46   # Calibrated 2026-03-11
WP_RADIUS = 3.0          # "Close enough" distance to waypoint (meters)
```
