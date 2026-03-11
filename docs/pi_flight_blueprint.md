# pi_flight.py — Web Ground Station Blueprint

> MAP of pi_flight.py (1097 lines). Not a code copy — a navigation aid.
> Updated: 2026-03-11

## Section Map

| Section | Lines | Purpose |
|---------|-------|---------|
| Imports + headless setup | 1-68 | Threading, cv2, http.server, pymavlink. If no DISPLAY: overrides cv2.imshow/waitKey to no-ops |
| Constants | 69-77 | `COPTER_MODES` dict (ArduCopter custom_mode int -> name), `CLUSTER_COLORS` (8 hex) |
| HTML Dashboard | 82-279 | Inline HTML+CSS+JS served at `/`. Single-page app, no build step |
| Web Server | 285-366 | ThreadedHTTPServer + WebHandler: routes, MJPEG stream, state API, command handler |
| PiFlight.__init__ | 372-488 | Telemetry vars, camera/sim setup, MAVLink connect, HTTP server start |
| MAVLink connection | 491-535 | `_connect_mavlink()`, `drain_mavlink()` — heartbeat filter, target_system extraction |
| Camera + CV | 538-548 | `get_frame()` (sim or real), `get_stream_jpeg()` (thread-safe JPEG access) |
| GPS Estimation | 551-649 | Clustering: `_new_cluster`, `_route_to_cluster`, `_add_observation`, `calculate_target_gps` |
| MAVLink Commands | 652-715 | `_passive_block`, `send_arm`, `send_takeoff`, `send_to_gps`, `send_velocity`, `send_land` |
| Command Handler | 718-855 | `handle_command()`: arm, takeoff, investigate, confirm, interest, false_positive, land, fake_detect, resume |
| Mode Execution | 857-898 | `execute_mode()`: INVESTIGATING (approach->descend->observe) + LANDING (fly_to->descend->landed) |
| State Export | 901-934 | `get_state()`: JSON dict for browser polling (telemetry, clusters, targets, flags) |
| Main Loop | 937-1008 | 50Hz: drain MAVLink, CV detection (throttled), execute_mode, stream encode |
| Keyboard Control | 1010-1065 | `_keyboard_loop()`: WASD terminal input (Windows msvcrt / Linux termios) |
| Cleanup + Entry | 1067-1097 | argparse: `--port`, `--fps`, `--cluster-dist`, `--takeoff-alt`, `--passive` |

## Browser Dashboard Layout

```
+--[ HEADER: flight_mode [drone_mode] | GPS | ALT | DET | BAT ]--+
|                          |                                      |
|  2D GPS Grid (canvas)    |   MJPEG Video Stream                |
|  flex:1                  |   flex:2 (larger)                    |
|  - drone arrow (orange)  |   - detection boxes (green)          |
|  - clusters (numbered)   |   - HUD overlay (alt, mode, det)    |
|  - search polygon        |   - DETECTION alert (orange flash)  |
|  - logged items (IOI/FP) |                                      |
|  [cluster-info panel]    |                                      |
|                          |                                      |
+--[ ARM | TAKEOFF | N:INVESTIGATE | Y:CONFIRM | I:INTEREST |    |
|    X:FALSE POS | L:LAND | M:RESUME | FAKE DET               ]--+
```

## HTTP Endpoints

| Method | Path | Handler | Returns |
|--------|------|---------|---------|
| GET | `/` | `_serve_html()` | HTML_DASHBOARD string |
| GET | `/stream` | `_serve_stream()` | MJPEG multipart stream (~20fps max) |
| GET | `/state` | `_serve_state()` | JSON: telemetry + clusters + targets |
| GET | `/snapshot` | `_serve_snapshot()` | JPEG captured during investigate observe phase |
| POST | `/command` | `_handle_command()` | JSON: `{ok, message}` |

Browser polls `/state` every 400ms. Stream is continuous MJPEG push.

## Command Flow

```
Browser button/key -> POST /command {action, cluster}
                   -> WebHandler._handle_command()
                   -> PiFlight.handle_command(body)
                   -> sets self.flight_mode, self.investigate_phase, etc.
                   -> execute_mode() in main loop acts on state
                   -> MAVLink commands sent to Cube
```

## Flight Modes + Phases

```
MANUAL ----[N:investigate]----> INVESTIGATING
  ^                                |
  |  [Y:confirm / I:interest      |---> approaching (fly to cluster GPS)
  |   / X:false_pos / M:resume]   |---> descending  (drop to 15m)
  +--------------------------------+---> observing   (hover, capture snapshot, wait for Y/I/X)

MANUAL ----[L:land]-----------> LANDING
  ^                                |
  |  [M:resume]                    |---> flying_to   (fly to 7.5m north of estimate)
  +--------------------------------+---> descending  (send LAND, wait for alt < 0.5m)
                                   +---> landed      (done, back to MANUAL)
```

## Key Data Structures

**Cluster** (in `self.detection_clusters` list):
```python
{
    "id": int,                    # permanent, monotonically increasing
    "observations": [(lat, lon, weight), ...],  # last 50 (rolling window)
    "best_gps": (lat, lon),       # weighted average of rolling 50
    "total_gps": (lat, lon),      # weighted average of ALL observations ever
    "total_wlat": float,          # running weighted sum (lat)
    "total_wlon": float,          # running weighted sum (lon)
    "total_w": float,             # running total weight
    "detection_count": int,       # total observations routed here
}
```

**GPS weight calculation** (in `calculate_target_gps`):
- `alt_factor = (30 / alt)^2` — lower altitude = exponentially more weight
- Centre-snap (within 30px of frame centre): weight = 10.0 * alt_factor
- Off-centre: weight = centre_weight * alt_factor, where centre_weight = 1..5 based on distance from centre

**Logged items** (`self.logged_items`): `[{type: "interest"|"false_positive", lat, lon, cluster_id, count?}]`

## Init Flow (PiFlight.__init__, lines 372-488)

1. Auto-detect Pi IP via `hostname -I`
2. Init telemetry vars (lat/lon from config.REF_LAT/LON, alt=0, yaw=0)
3. Init flight state (MANUAL, no investigate/landing targets)
4. Init detection state (empty clusters, cv_interval from --fps)
5. **SIMULATION**: create SimulationEnvironment, interactive map setup (place dummies, draw polygon), load VisionSystem model-only
6. **REAL**: load search_area.json or config.SEARCH_AREA_GPS, open camera via VisionSystem
7. Connect MAVLink (`_connect_mavlink`)
8. Start ThreadedHTTPServer on `0.0.0.0:port`, daemon thread

## Main Loop (lines 937-1008)

```
while running (50Hz):
    1. Retry MAVLink if disconnected (5s cooldown)
    2. drain_mavlink() -> update telemetry vars from messages
    3. If CV interval elapsed AND alt > 1.0:
       a. get_frame() from sim or camera
       b. detect_in_image(frame) -> (found, u, v, conf)
       c. If found: draw green box, calculate_target_gps(u,v)
       d. Add HUD text overlay (alt, mode, detections, GPS estimate)
       e. Encode JPEG (quality 85), store in _stream_jpeg
    4. If on ground (alt <= 1.0): stream "ON GROUND" overlay
    5. execute_mode() -> send MAVLink commands for current flight mode
    6. sleep(0.02)
```

## MAVLink Details

- `_connect_mavlink()` (line 491): connects, waits heartbeat, requests all data streams at 10Hz
- `drain_mavlink()` (line 508): non-blocking loop, updates lat/lon/alt from GLOBAL_POSITION_INT, yaw from ATTITUDE, speed from VFR_HUD, battery from SYS_STATUS, mode from HEARTBEAT
- Heartbeat filter: skips MAV_TYPE_GCS (mavproxy heartbeats)
- target_system extracted from first autopilot heartbeat (fixes system 0 bug)
- `send_arm()`: sets GUIDED mode first (MAV_CMD_DO_SET_MODE, custom_mode=4), then arms
- `send_to_gps()`: SET_POSITION_TARGET_GLOBAL_INT with lat/lon/alt mask
- `send_velocity()`: body-frame to NED conversion using yaw, SET_POSITION_TARGET_LOCAL_NED

## Known Issues

- `self.investigating` used in `_cancel_investigate()` (line 849) and `execute_mode()` (line 872) but **never initialized in __init__** — works by accident (AttributeError would only occur if observe phase reached before any cancel)
- `handle_command()` is 120 lines, monolithic — should split per action
- JavaScript uses minified variable names (`S` for state, `selCluster`)
- Grid canvas redrawn on every poll (400ms) — no dirty checking
- Cluster removal via `pop(ci)` in false_positive can shift indices of other clusters (permanent IDs mitigate this for the browser, but `active_cluster_idx` / `investigate_cluster_idx` may go stale)

## CLI Flags

| Flag | Default | Purpose |
|------|---------|---------|
| `--port` | 8090 | Web dashboard port |
| `--fps` | 4 | CV inference rate limit (0=unlimited) |
| `--cluster-dist` | 30 | Cluster grouping distance in metres |
| `--takeoff-alt` | 20 | Takeoff altitude in metres |
| `--passive` | false | ZERO commands sent to Cube (blocks all send_* methods) |

## Dependencies

- **config.py**: MODE, CONNECTION_STR, BAUD_RATE, REF_LAT/LON, IMAGE_W/H, SENSOR_WIDTH_MM, FOCAL_LENGTH_MM, REAL_CAMERA_INDEX, SEARCH_AREA_GPS
- **vision.py**: VisionSystem (camera + model), detect_in_image()
- **utils.py**: GeoTransformer (GPS <-> pixel conversion)
- **simulation.py**: SimulationEnvironment (SIMULATION mode only, conditional import)
