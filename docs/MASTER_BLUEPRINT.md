# MASTER BLUEPRINT — SAR Drone Codebase

> Single-document reference for the entire `v3/` codebase. Read this BEFORE any source file.
> Line ranges are approximate and shift when code changes -- verify with the file.
> Last updated: 2026-03-16. Total: ~7,512 lines across 12 source files.

---

## 1. FILE-BY-FILE REFERENCE

---

### config.py (192 lines)

**Purpose:** All configuration constants + auto-detection of connection/platform.

**Key functions:**
- `_detect_connection()` L10-L43 -- auto-detect MAVLink connection string (env var > serial > WSL gateway > localhost)
- `load_kml_zones(kml_path)` L121-L184 -- parse AENGM0074.kml into GPS polygon variables

**Key constants:**
- `MODE` L49 -- "SIMULATION" or "REAL" (env var `DRONE_MODE`)
- `CONNECTION_STR` L54 -- auto-detected MAVLink connection
- `TARGET_ALT = 50.0` L58, `VERIFY_ALT = 15.0` L59
- `FOCAL_LENGTH_MM = 5.46` L77, `SENSOR_WIDTH_MM = 5.02` L74
- `IMAGE_W = 1456`, `IMAGE_H = 1088` L78-L79 (Pi camera native resolution)
- `CONFIDENCE_THRESHOLD = 0.4` L96
- `TRANSIT_SPEED_MPS = 15.0` L99, `SEARCH_SPEED_MPS = 10.0` L100
- `CAMERA_FLIP_180 = True` L90
- `SEARCH_AREA_GPS` L106-L113 -- fallback polygon (overwritten by KML)
- `FLIGHT_AREA_GPS`, `SSSI_GPS`, `TAKEOFF_GPS`, `FOCUS_AREA_GPS` L116-L119

**External deps:** None (standalone, uses only stdlib).

---

### states.py (23 lines)

**Purpose:** Enum-like class defining all mission states.

**States (20 total):**
```
INIT, CONNECTING, ARMING, TAKEOFF, PRE_WAYPOINTS, TRANSIT_TO_SEARCH,
SEARCH, CENTERING, DESCENDING, VERIFY, HOVER, APPROACH,
RETURN_TO_SEARCH, RETURN_FROM_MANUAL, HOVER_TARGET, RETURN_TRANSIT,
RETURN_HOME, LANDING, MANUAL, DONE
```

---

### utils.py (59 lines)

**Purpose:** Geo math -- GPS-to-pixel and pixel-to-GPS conversion, plus alpha overlay utility.

**Key classes:**
- `GeoTransformer` L6-L24
  - `gps_to_pixels(lat, lon)` L10-L15
  - `pixels_to_gps(x, y)` L17-L24
- `overlay_image_alpha(background, overlay, x, y, target_w, target_h, rotation_deg)` L26-L59

**GPS math formula:**
```python
lat_m = 111132.954 - 559.822 * cos(2 * radians(lat))
lon_m = 111132.954 * cos(radians(lat))
```

**External deps:** `config` (MAP_WIDTH_METERS, REF_LAT, REF_LON)

---

### vision.py (292 lines)

**Purpose:** Camera + AI detection. The ONLY file that touches CV/AI inference. Dual backend: Ultralytics (laptop) / TFLite (Pi).

**Key class: `VisionSystem`** L32-L292
- `__init__(camera_index, model_path)` L33-L162
  - Camera: tries OpenCV L44-L56, falls back to picamera2 L58-L103
  - Lens undistortion: loads `calibration_data.npz`, precomputes remap maps L105-L120
  - Model: tries Ultralytics YOLO L134-L143, falls back to TFLite L146-L162
- `undistort(frame)` L164-L168 -- applies lens correction (~1.5ms)
- `detect_in_image(frame)` L170-L246 -- **THE core detection interface**
  - Returns: `(found: bool, x: int, y: int, confidence: float)`
  - TFLite path L184-L230: BGR->RGB, resize 640x640, normalize, invoke, parse output
  - Ultralytics path L233-L244: passes frame directly
  - Draws bounding box on frame (side effect)
- `get_frame()` L259-L282 -- capture frame, apply color correction + flip

**Backend priority:** Ultralytics > tflite_runtime > ai_edge_litert > tensorflow.lite

**External deps:** `config` (IMAGE_W/H, SENSOR_WIDTH_MM, etc.)

---

### planning.py (226 lines)

**Purpose:** Lawnmower and spiral search pattern generators.

**Key class: `PathPlanner`** L7-L226
- `generate_search_pattern(map_w, map_h, drone_gps, alt_override)` L15-L136 -- **Lawnmower**
  - Create mask, rotate to longest edge, calculate swath from FOV, generate scan lines, optimize start corner
- `generate_spiral_pattern(map_w, map_h, drone_gps, alt_override)` L139-L226 -- **Spiral**

**Swath formula:** `ground_width = (SENSOR_WIDTH_MM * alt) / FOCAL_LENGTH_MM * 0.8` (20% overlap)

**External deps:** `config` (TARGET_ALT, SENSOR_WIDTH_MM, FOCAL_LENGTH_MM)

---

### simulation.py (413 lines)

**Purpose:** Laptop-only simulation -- map rendering, dummy placement, camera view synthesis.

**Key class: `SimulationEnvironment`** L8-L413
- `setup_on_map(preload_polygon_gps, preload_transit_gps)` L39-L213 -- Interactive target/polygon/transit setup
- `get_drone_view(cx, cy, alt, yaw)` L215-L267 -- Synthesize camera frame from map
- `get_god_view(cx, cy, yaw, ...)` L269-L413 -- Top-down map with all overlays

**External deps:** `config`, `utils.overlay_image_alpha`

---

### preflight.py (247 lines)

**Purpose:** Standalone pre-flight connectivity checker.

**Checks:** TCP/serial connectivity, MAVLink heartbeat, camera, AI model.
**Missing:** GPS fix check, picamera2 support, battery voltage.

**Entry point:** `python preflight.py`

---

### main.py (1,348 lines)

**Purpose:** Full autonomous mission orchestrator -- state machine from ARM to LAND.

**Key class: `VisualFlightMission`** L235-L1208
- `__init__()` L236-L418 -- simulation/real setup, pattern generation
- `update_telemetry()` L449-L481 -- drain MAVLink, detect RC failsafe
- `calculate_target_gps(u, v)` L482-L497 -- pixel → GPS estimate
- `update_dashboard()` L499-L602 -- frame + detection + HUD + composite view
- **State handlers** L635-L996 (one method per state)
- `_handle_keys()` L999-L1081 -- M=manual, WASD, Y/N verify
- `run()` L1085-L1157 -- main loop
- `_dry_run()` L1210-L1341 -- pattern visualization without flight

**CLI flags:** `--dry-run`, `--model`, `--pattern`, `--headless`, `--waypoints`, `--transit`, `--search-area`

**Web server:** `/` (dashboard), `/stream` (MJPEG), `/cmd?key=X` (commands) on port 8090

**External deps:** config, states, utils, planning, vision, simulation

---

### simple_simulator.py (2,508 lines)

**Purpose:** Interactive MVP -- keyboard flight + CV + GPS estimation + offset landing.

**Key class: `SimpleMission`** L45-L2508
- GPS estimation with noise simulation, Kalman filter, spatial clustering
- Visual servo (pixel-based centering)
- Multi-target support with Y/I/X classification
- Full HUD + scatter plot + dashboard

**CLI flags:** `--fps`, `--tflite`, `--gps-drift`, `--shake`, `--alt-noise`, `--yaw-noise`, `--fov-error`, `--cluster-dist`

**Entry point:** `python simple_simulator.py`

---

### pi_flight.py (1,121 lines)

**Purpose:** Web ground station for real flights. Browser dashboard + MJPEG + commands.

**Key class: `PiFlight`** L378-L1101
- Full web dashboard with 2D GPS grid, detection clusters, command buttons
- Commands: arm, takeoff, investigate, confirm, interest, false_positive, land, rtl
- Same GPS estimation math as simple_simulator (minus Kalman filter)

**Web endpoints:** `/` (dashboard), `/stream` (MJPEG), `/state` (JSON), `/snapshot`, `/command` (POST)

**CLI flags:** `--port`, `--fps`, `--cluster-dist`, `--takeoff-alt`, `--passive`

---

### passive_watch.py (760 lines)

**Purpose:** Passive observer. Stream + detection + GPS estimation. ZERO commands.

**Web endpoints:** `/` (stats page), `/stream`, `/snapshot`, `/api/status`

---

### capture_training.py (334 lines)

**Purpose:** Record video + photos for retraining. ZERO commands. Port 8091.

---

## 2. CROSS-CUTTING CONCERNS

### 2.1 Complete State Machine Flow

See `docs/STATE_MACHINE.md` for the full detailed diagram.

### 2.2 MAVLink Commands Used

| Command | File(s) | Purpose |
|---------|---------|---------|
| `MAV_CMD_DO_SET_MODE` (GUIDED) | main.py, pi_flight.py | Set GUIDED before arming |
| `MAV_CMD_DO_SET_MODE` (RTL) | pi_flight.py | Return to launch |
| `MAV_CMD_COMPONENT_ARM_DISARM` | main.py, pi_flight.py | Arm/disarm motors |
| `MAV_CMD_NAV_TAKEOFF` | main.py, pi_flight.py | Takeoff to altitude |
| `MAV_CMD_NAV_LAND` | pi_flight.py | Land command |
| `MAV_CMD_DO_CHANGE_SPEED` | main.py | Set transit/search speed |
| `MAV_CMD_DO_SET_SERVO` | main.py | Payload servo (ch9, PWM 1100) |
| `set_position_target_global_int` | main.py, pi_flight.py | Fly to GPS position |
| `set_position_target_local_ned` | main.py, pi_flight.py, simple_sim | Velocity (WASD) |

### 2.3 GPS Estimation Pipeline

All files use the same core math:
```
1. GSD = (SENSOR_WIDTH_MM × alt) / (FOCAL_LENGTH_MM × IMAGE_W)
2. dx = (u - cx) × GSD,  dy = -(v - cy) × GSD
3. Rotate by yaw: N = dy×cos(yaw) - dx×sin(yaw), E = dy×sin(yaw) + dx×cos(yaw)
4. target_lat = lat + N / R × (180/π)
   target_lon = lon + E / (R × cos(lat)) × (180/π)
```

Weighting: `weight = centre_bonus × (30/alt)²` — lower altitude and centre-frame detections get more weight.

### 2.4 Camera Pipeline

```
get_frame() → flip 180° → gray_world() → undistort() → detect_in_image()
  → TFLite: BGR→RGB, resize 640×640, /255, invoke, parse [1,5,8400]
  → Ultralytics: pass frame directly
  → Returns (found, cx, cy, conf)
```

### 2.5 Web Server Endpoints

| Script | Port | Routes |
|--------|------|--------|
| main.py | 8090 | `/`, `/stream`, `/cmd?key=X` |
| pi_flight.py | 8090 | `/`, `/stream`, `/state`, `/snapshot`, `/command` |
| passive_watch.py | 8090 | `/`, `/stream`, `/snapshot`, `/api/status` |
| capture_training.py | 8091 | `/`, `/stream` |

### 2.6 Shared Patterns (duplicated across files)

1. **GPS estimation math** — main.py, pi_flight.py, passive_watch.py, simple_simulator.py
2. **Spatial clustering** — pi_flight.py, simple_simulator.py
3. **MAVLink telemetry drain** — all 4 main scripts
4. **MJPEG stream server** — all 4 main scripts
5. **COPTER_MODES dict** — defined identically in 4 files
6. **GPS distance function** — 3 different implementations (Haversine vs flat-earth)

### 2.7 Config Flow

```
config.py
  ├─ MODE → camera source, connection type
  ├─ CONNECTION_STR → MAVLink connection
  ├─ TARGET_ALT, VERIFY_ALT → search/verify altitudes
  ├─ SENSOR_WIDTH_MM, FOCAL_LENGTH_MM → GSD + swath calculation
  ├─ IMAGE_W, IMAGE_H → camera resolution
  ├─ CONFIDENCE_THRESHOLD → detection filtering
  ├─ SEARCH/TRANSIT_SPEED_MPS → flight speeds
  └─ SEARCH_AREA_GPS → search polygon (from KML or hardcoded)
```

## 3. DEPENDENCY GRAPH

```
config.py ← states.py ← utils.py ← vision.py
                │            │           │
          planning.py   simulation.py    │
                │            │           │
        ┌───────┴────────────┴───────────┘
        │           │           │              │
     main.py    pi_flight   simple_sim   passive_watch
                                              │
                                        capture_training (standalone)
```

## 4. QUICK LOOKUP TABLE

| Need to change... | Edit this file |
|---|---|
| Detection model/threshold | `vision.py` L170+, `config.py` L96 |
| Search altitude | `config.py` L58 |
| Camera resolution | `config.py` L78-L79 |
| Search area polygon | `config.py` L106+, or KML, or `search_area.json` |
| Lawnmower pattern | `planning.py` L15-L136 |
| State transitions | `main.py` L635-L996 |
| Landing offset | `main.py` L613, `pi_flight.py` L425, `simple_sim` L256 |
| Web dashboard UI | `pi_flight.py` L82-L286 |
| GPS estimation | `main.py` L482-L497, `pi_flight.py` L619-L657 |
| Servo/payload | `main.py` L936-L944 (ch9, PWM 1100) |
| Add new state | `states.py` + `main.py` (handler + dispatch) |
