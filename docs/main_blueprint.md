# main.py Blueprint (908 lines) — Mission Orchestrator

> This is a MAP, not a copy of code. Use it to navigate main.py without reading 900+ lines.
> Update this file whenever main.py changes structurally.

## Section Map

| Section | Lines | Purpose |
|---------|-------|---------|
| Imports + config check | 1-35 | Standard lib + project modules |
| CLI flags | 37-62 | `--model`, `--dry-run`, `--stream-*`, `--no-stream`, `--headless` |
| Stream/queue globals | 69-109 | `_stream_frame`, `_stream_lock`, `_cmd_queue`, HEADLESS detection, terminal input thread |
| HTTP handler | 111-193 | `_StreamHandler`: `/stream` (MJPEG), `/cmd?key=` (Y/N/M/E/W/S), `/` (dashboard HTML) |
| Stream server | 195-219 | ThreadingHTTP on port 8090 |
| `__init__` | 222-296 | SimulationEnvironment or real setup, VisionSystem, PathPlanner, telemetry vars, CSV logger |
| `_setup_real_search_area` | 298-326 | Load from `search_area.json` -> `config.SEARCH_AREA_GPS` -> empty fallback |
| `update_telemetry` | 328-359 | Parse GLOBAL_POSITION_INT, ATTITUDE, HEARTBEAT; RC failsafe detection |
| `calculate_target_gps` | 361-376 | Pixel (u,v) -> GPS via GSD + yaw rotation |
| `update_dashboard` | 378-455 | Frame capture, CV detection, HUD overlay, god view composite, stream update |
| `set_speed` | 457-462 | MAV_CMD_DO_CHANGE_SPEED (3s throttle) |
| `calculate_landing_spot` | 464-481 | 7.5m offset in N/S/E/W direction |
| `run()` | 483-746 | Main loop: telemetry -> dashboard -> key input -> state machine |
| State: INIT -> CONNECTING | 538-560 | Connect, wait heartbeat, request data stream |
| State: ARMING | 562-618 | GPS fix check (type>=3, sats>=6), set GUIDED, arm |
| State: TAKEOFF | 620-643 | Climb to TARGET_ALT, generate waypoints |
| State: TRANSIT -> SEARCH | 645-674 | Fly waypoints, detect -> CENTERING |
| State: CENTERING -> DESCENDING | 676-699 | Fly to target, descend to VERIFY_ALT |
| State: VERIFY | 700-709 | Wait Y/N input (terminal, browser, or cv2) |
| State: APPROACH -> LANDING -> DONE | 711-730 | Fly to landing spot, land, report error |
| Key input handling | 508-535, 732-746 | M=manual, Y/N=verify, N/E/W/S=landing side, ESC=quit |
| `_dry_run` | 774-900 | No-fly visualization: pattern, timing estimates, map display |

## State Machine Flow

```
INIT -> CONNECTING -> ARMING -> TAKEOFF -> TRANSIT_TO_SEARCH -> SEARCH
                                                                  |
                                          detect target           v
                                                            CENTERING
                                                                  |
                                                                  v
                                                            DESCENDING
                                                                  |
                                                                  v
                                                              VERIFY
                                                             /      \
                                                          Y           N
                                                         /             \
                                              select side          back to SEARCH
                                             (N/E/W/S)
                                                  |
                                                  v
                                              APPROACH -> LANDING -> DONE

Any state: M -> MANUAL -> M -> resume previous state
```

## Key Instance Variables

| Variable | Type | Purpose |
|----------|------|---------|
| `self.master` | `mavutil.mavlink_connection` | pymavlink connection to Cube |
| `self.eyes` | `VisionSystem` | Camera + AI detection (dual backend) |
| `self.planner` | `PathPlanner` | Lawnmower search pattern generator |
| `self.geo` | `GeoTransformer` | GPS <-> pixel coordinate conversion |
| `self.waypoints` | `list[(lat, lon)]` | Generated lawnmower waypoints |
| `self.target_lat/lon` | `float` | Detected target GPS position |
| `self.landing_lat/lon` | `float` | 7.5m offset landing spot |
| `self.state` | `State` enum | Current state machine state |
| `_cmd_queue` | `queue.Queue` | Thread-safe queue for browser/terminal keys |

## Input Methods (headless support)

Three parallel input paths, all feed into `_cmd_queue`:

1. **cv2.waitKey** — display mode (laptop with monitor)
2. **Terminal keypresses** — `_terminal_input_thread` for PuTTY/SSH
3. **Browser buttons** — `http://localhost:8090` via `/cmd?key=` endpoint

## Web Dashboard (port 8090)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | HTML dashboard page with buttons |
| `/stream` | GET | MJPEG video stream (multipart) |
| `/cmd?key=X` | GET | Send command key (Y, N, M, E, W, S) |

## Dependencies on Other Modules

```
main.py
  |-- config.py        All settings (altitudes, speeds, connection strings)
  |-- states.py        State enum definition
  |-- utils.py         GeoTransformer (GPS <-> pixel math)
  |-- vision.py        VisionSystem.detect_in_image(frame) -> (found, x, y, conf)
  |-- planning.py      PathPlanner.generate_waypoints(polygon) -> [(lat, lon)]
  |-- simulation.py    SimulationEnvironment (laptop-only, map.jpg based)
```

## CLI Flags

| Flag | Default | Purpose |
|------|---------|---------|
| `--model PATH` | `best.tflite` | Use alternate TFLite model |
| `--dry-run` | off | Visualize pattern without flying (no Cube needed) |
| `--stream-port N` | 8090 | HTTP stream port |
| `--stream-quality N` | 60 | MJPEG JPEG quality (0-100) |
| `--no-stream` | off | Disable HTTP stream server |
| `--headless` | auto | Force headless mode (no cv2.imshow) |

## Known Issues

- `run()` is 264 lines — should be split into per-state handler methods
- Hardcoded 0.62 latitude scale factor (Bristol-specific, should use `cos(lat)`)
- HTML injection possible in stream page (CLI args not escaped)
- `calculate_target_gps` uses simplified flat-earth projection (adequate for <1km range)

## Modification Guide

| To change... | Edit... |
|--------------|---------|
| Add a new state | `states.py` (enum) + `run()` state machine block |
| Change detection logic | `vision.py` only (main.py just calls `detect_in_image`) |
| Change search pattern | `planning.py` only (main.py just calls `generate_waypoints`) |
| Change altitudes/speeds | `config.py` only |
| Add new browser command | `_StreamHandler` (HTML button + `/cmd` handler) + key handling in `run()` |
| Change landing offset | `calculate_landing_spot` (~line 464) |
| Add new CLI flag | argparse block (~line 37) |
