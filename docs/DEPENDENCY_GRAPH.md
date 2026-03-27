# Dependency Graph — SAR Drone v3

Complete import, data flow, and configuration dependency map for the codebase.

---

## Quick Reference: File Roles

| File | Lines | Role | Key Exports |
|------|-------|------|------------|
| **config.py** | 240 | Central config; auto-detects hardware + connection | MODE, CONNECTION_STR, altitudes, camera specs, geofence bounds |
| **states.py** | 22 | Enum only | State class (INIT, CONNECTING, ARMING, ..., DONE) |
| **vision.py** | 428 | AI detection; dual backend (YOLO / TFLite) | VisionSystem class; `detect_in_image()` returns `(found, x, y, conf)` |
| **planning.py** | 284 | Lawnmower search pattern; geo math | PathPlanner class; `generate_search_pattern()` → waypoints list |
| **utils.py** | 58 | Geo transformation (GPS ↔ pixels) | GeoTransformer class; reads config.MAP_WIDTH_METERS, REF_LAT, REF_LON |
| **gps_utils.py** | 122 | Pure math: GPS distance + pixel-to-GPS conversion | `gps_distance()`, `calculate_target_from_pixels()`, `landing_offset_7_5m()` |
| **geofence.py** | 180 | SSSI no-fly zone enforcement | NFZGeofence class; waypoint filtering + runtime repulsion |
| **navigation.py** | 253 | MAVLink command wrapper | NavigationController class; arm/takeoff/goto/land/mode commands |
| **stream_server.py** | 225 | HTTP streaming + browser UI | `start_stream_server()`, `set_stream_frame()`, cmd_queue; port 8090 |
| **state_machine.py** | 1062 | State handlers (18 _handle_* methods) | StateHandlersMixin; all 32 state transitions + helper methods |
| **main.py** | 909 | Mission orchestrator (state machine + run loop) | VisualFlightMission class; instantiates all modules; entry point |
| **pi_flight.py** | 1130 | Alternative ground station (web + zero commands) | Standalone; port 8090; passive detection logging |

---

## Import Graph (ASCII Diagram)

```
EXTERNAL DEPENDENCIES (bottom layer)
├─ pymavlink.mavutil        (Cube autopilot comms)
├─ opencv-python (cv2)      (image capture + vision)
├─ numpy                     (matrices, math)
├─ tensorflow / tflite       (AI model inference)
│  └─ tflite-runtime OR ai-edge-litert (Pi only, Python 3.13)
├─ http.server              (streaming server)
└─ threading, queue, sys... (stdlib)

────────────────────────────────────────────────────────

CORE CONFIGURATION (config is read-only; no outgoing imports)
   config.py (240 lines)
   ↓ read by 8+ files

────────────────────────────────────────────────────────

INDEPENDENT MODULES (no circular dependencies)

1) states.py (22 lines)
   └─ imported by: main.py, state_machine.py

2) utils.py (58 lines)
   ├─ imports: config
   ├─ exported by: GeoTransformer
   └─ imported by: main.py, planning.py

3) gps_utils.py (122 lines)
   ├─ NO imports from project (pure math)
   └─ imported by: main.py

4) vision.py (428 lines)
   ├─ imports: config (reads IMAGE_W/H, CONFIDENCE_THRESHOLD)
   ├─ exports: VisionSystem class
   └─ imported by: main.py

5) planning.py (284 lines)
   ├─ imports: config, utils.GeoTransformer
   ├─ exports: PathPlanner class
   └─ imported by: main.py

6) geofence.py (180 lines)
   ├─ imports: config, utils.GeoTransformer (indirectly via NFZGeofence init)
   ├─ exports: NFZGeofence class
   └─ imported by: state_machine.py (via self.geofence in main.py)

7) navigation.py (253 lines)
   ├─ imports: pymavlink only
   ├─ exports: NavigationController class
   └─ imported by: main.py, state_machine.py

────────────────────────────────────────────────────────

MISSION STATE MACHINE (complex orchestration)

8) state_machine.py (1062 lines)
   ├─ imports:
   │  ├─ states.State
   │  ├─ navigation.NavigationController
   │  └─ config
   ├─ lazy-imports main (to avoid circular):
   │  └─ _get_main_globals() returns REAL_CANVAS_SIZE, SIM_SPEED, BEACON_DELAY
   ├─ exports: StateHandlersMixin class
   │  └─ 18 _handle_<STATE>() methods
   │  └─ helper methods (_set_state, get_dist_to_target, _gps_dist, etc.)
   └─ USED BY: main.py (VisualFlightMission inherits from this mixin)

9) stream_server.py (225 lines)
   ├─ NO imports from project modules
   ├─ exports: start_stream_server(), set_stream_frame(), cmd_queue
   └─ imported by: main.py

────────────────────────────────────────────────────────

ENTRY POINTS (instantiate everything else)

10) main.py (909 lines) — THE ORCHESTRATOR
    ├─ imports (in order):
    │  ├─ pymavlink, cv2, numpy, os, sys, threading, csv, time, datetime
    │  ├─ config
    │  ├─ states.State
    │  ├─ utils.GeoTransformer
    │  ├─ planning.PathPlanner
    │  ├─ vision.VisionSystem
    │  ├─ state_machine.StateHandlersMixin  ← MIXIN INHERITANCE
    │  ├─ navigation.NavigationController
    │  ├─ stream_server.*
    │  └─ gps_utils.{calculate_target_from_pixels, landing_offset_7_5m}
    │
    ├─ defines: VisualFlightMission class
    │  ├─ inherits from StateHandlersMixin (all 18 state handlers)
    │  ├─ instantiates:
    │  │  ├─ self.eyes = VisionSystem(...)         → AI detection
    │  │  ├─ self.planner = PathPlanner(...)       → lawnmower path
    │  │  ├─ self.nav = NavigationController(...)  → MAVLink commands
    │  │  ├─ self.geofence = NFZGeofence(...)      → SSSI boundary
    │  │  └─ simulation.SimulationEnvironment(...) → (if SIMULATION mode)
    │  │
    │  └─ main run loop (lines ~850-909)
    │     ├─ reads telemetry from self.master (pymavlink)
    │     ├─ calls self.eyes.detect_in_image()     → (found, x, y, conf)
    │     ├─ updates state via self._set_state()   ← from StateHandlersMixin
    │     ├─ dispatches state handlers
    │     ├─ calls self.nav.send_*() methods       → MAVLink to Cube
    │     └─ streams frame via set_stream_frame()  → browser UI
    │
    └─ entry point: if __name__ == "__main__": mission.run()

11) pi_flight.py (1130 lines) — ALTERNATIVE GROUND STATION
    ├─ standalone (separate from main.py)
    ├─ imports: config, gps_utils, vision, stream_server (+ stdlib)
    ├─ NO state_machine imports (passive observer only)
    ├─ exports: class VisualFlightObserver
    │  └─ stream page (same port 8090 as main.py stream_server)
    │  └─ detects targets but sends ZERO commands (passive logging)
    └─ entry point: if __name__ == "__main__": observer.run()

────────────────────────────────────────────────────────
```

---

## Data Flow: Camera → Detection → Navigation → Cube

```
CAPTURE LAYER
═════════════════════════════════════════════════════════
┌──────────────────────────────────────────────────────┐
│ vision.py :: VisionSystem                            │
│                                                      │
│ • Opens camera (cv2.VideoCapture or picamera2)      │
│ • Frames: 640x480 (laptop) or 1456x1088 (Pi native) │
│ • Applies lens undistortion (from calibration_data) │
│ • Resizes to [640, 640] for model input             │
│                                                      │
│ detect_in_image(frame) → (found, x, y, conf)        │
│  └─ x, y: pixel coords in [640, 640] model space    │
│  └─ conf: detection confidence (0-1)                │
└─────────────────┬──────────────────────────────────┘
                  │ output: (found, x, y, conf)
                  ▼
VISION PROCESSING LAYER
═════════════════════════════════════════════════════════
main.py :: VisualFlightMission.run() loop

  if found:
    [1] Convert model pixels to full image pixels:
        x_full = (x / 640) * raw_image_width
        y_full = (y / 640) * raw_image_height

    [2] Drone telemetry snapshot:
        drone_alt   = state_machine.altitude (from MAVLink GLOBAL_POSITION_INT)
        drone_yaw   = state_machine.yaw      (from MAVLink ATTITUDE)
        drone_lat   = state_machine.latitude
        drone_lon   = state_machine.longitude

    [3] Call gps_utils.calculate_target_from_pixels():
        est_lat, est_lon = calculate_target_from_pixels(
            x_full, y_full,
            drone_alt, drone_yaw,
            drone_lat, drone_lon,
            image_w, image_h,
            SENSOR_WIDTH_MM, FOCAL_LENGTH_MM
        )
        └─ output: estimated target GPS position

    [4] Store detected position:
        self.target_lat = est_lat
        self.target_lon = est_lon
        self.detected_confidence = conf
        self.detection_count += 1

    [5] Update state machine:
        if state == SEARCH:
            transition to CENTERING
        elif state == CENTERING:
            track target, issue GUIDED commands

                                  │
                                  ▼
STATE MACHINE LAYER
═════════════════════════════════════════════════════════
state_machine.py :: StateHandlersMixin (18 state handlers)

  _handle_SEARCH():
    • self.planner.generate_search_pattern() → waypoint list
    • Use self.nav.send_global_target(lat, lon, alt) to fly waypoints
    • Check if target detected → transition to CENTERING

  _handle_CENTERING():
    • self.nav.send_velocity(vx, vy, vz) for visual servo
    • Issue small GUIDED corrections toward detected target
    • When centered (pixel error < threshold) → transition to DESCENDING

  _handle_DESCENDING():
    • self.nav.send_global_target(target_lat, target_lon, lower_alt)
    • When alt < VERIFY_ALT → transition to VERIFY

  _handle_VERIFY():
    • Wait for operator confirmation (Y/N/I/X keys)
    • Update self.target_classification
    • Transition to LANDING or SEARCH

  _handle_LANDING():
    • Calculate landing offset 7.5m away
    • landing_lat, landing_lon = landing_offset_7_5m(...)
    • self.nav.send_global_target(landing_lat, landing_lon, 0)
    • When landed → transition to DONE

                                  │
                                  ▼
NAVIGATION COMMAND LAYER
═════════════════════════════════════════════════════════
navigation.py :: NavigationController

  Every state handler calls:
    • self.nav.arm()
    • self.nav.takeoff(altitude_m)
    • self.nav.send_global_target(lat, lon, alt)  ← most common
    • self.nav.send_velocity(vx, vy, vz)
    • self.nav.set_mode(mode_name)
    • self.nav.land()
    • self.nav.rtl()

  These methods construct MAVLink messages:
    ├─ SET_POSITION_TARGET_GLOBAL_INT (for lat/lon/alt commands)
    ├─ SET_POSITION_TARGET_LOCAL_NED (for velocity commands)
    ├─ SET_MODE (mode changes: AUTO, GUIDED, LAND, RTL)
    ├─ ARM_DISARM (arm/disarm)
    ├─ NAV_TAKEOFF (takeoff)
    └─ NAV_LAND (land)

                                  │
                                  ▼
CUBE AUTOPILOT (MAVLink)
═════════════════════════════════════════════════════════
  self.master.mav.send_msg(msg)

  Cube receives commands:
    • Arm/disarm motors
    • Takeoff to altitude
    • Fly to lat/lon/alt (GUIDED mode)
    • Hover/fly velocity vectors (GUIDED mode)
    • Change flight mode
    • Land at current location

  Cube sends back telemetry (reads in run loop):
    • GLOBAL_POSITION_INT: lat, lon, alt, vx, vy, vz
    • ATTITUDE: roll, pitch, yaw, yaw_rate
    • HEARTBEAT: arm_disarm status, mode
    • GPS_RAW_INT: fix_type, num_satellites
    • BATTERY_STATUS: voltage, current
    • (read via message_hooks in pymavlink)

                                  │
                                  ▼
GROUND STATION (Browser UI)
═════════════════════════════════════════════════════════
stream_server.py

  HTTP server (port 8090):
    • GET /               → dashboard HTML
    • GET /mjpeg          → MJPEG video stream
    • GET /status         → JSON telemetry (lat, lon, alt, yaw, etc.)
    • POST /cmd?key=Y     → operator buttons (Y/N/I/X/L/M)

  Every iteration, main.py:
    • set_stream_frame(frame) → uploads current camera frame
    • checks stream_cmd_queue for operator inputs (Y/N/I/X)
    • Operator confirms/rejects detections via browser buttons
```

---

## Configuration Dependency Map

All configuration is **read-only** in config.py. The following files read these config values:

### Mode & Connection (Automatic Setup)

```
config.MODE
├─ auto-detects: "SIMULATION" or "REAL"
│  └─ read by: main.py (line 39), controls SimulationEnvironment instantiation
│
config.CONNECTION_STR
├─ auto-detects: Pi serial, WSL gateway, or Windows localhost
│  └─ read by: main.py (line 72), passed to mavutil.mavlink_connection()
│
config.BAUD_RATE (921600)
└─ read by: main.py (line 73)
```

### Flight Altitudes & Speeds

```
config.TARGET_ALT (35.0 m)
├─ used by: planning.py line 17 (search pattern generation)
├─ used by: state_machine.py _handle_SEARCH() (waypoint altitude)
└─ tuneable: lower if AI can't see dummy from 35m

config.VERIFY_ALT (15.0 m)
├─ used by: state_machine.py _handle_DESCENDING() (descent target)
└─ tuneable: altitude at which operator confirms

config.SEARCH_SPEED_MPS (5.0 m/s)
├─ used by: state_machine.py _handle_SEARCH()
└─ tuneable: lower if AI struggles with motion blur
```

### Camera & Vision

```
config.IMAGE_W (1456), config.IMAGE_H (1088)
├─ Pi camera native resolution
├─ read by: vision.py (line 48) — captures at this resolution
├─ resized internally to [640, 640] for model input
└─ 2026-03-16: upgraded from 640x480 for full detail

config.SENSOR_WIDTH_MM (5.02 mm)
├─ physical width of IMX296 sensor
├─ used by: gps_utils.calculate_target_from_pixels()
├─ used by: planning.py line 42 (ground coverage width calc)
└─ calibrate with: tools/fov_calibrate_video.py

config.FOCAL_LENGTH_MM (5.46 mm)
├─ camera focal length (not f-number)
├─ calibrated 2026-03-11: 92cm visible at 1m height
├─ used by: gps_utils.calculate_target_from_pixels()
├─ used by: planning.py line 42 (ground coverage width calc)
└─ tune with: tools/fov_calibrate_video.py

config.CONFIDENCE_THRESHOLD (0.2)
├─ minimum detection confidence to accept a detection
├─ read by: vision.py line ~200 (filters detections)
├─ low (0.2) to catch edge cases, operator filters FPs
└─ tuneable: raise to 0.4 for fewer FPs, lower to 0.1 for more detections

config.CAMERA_AWB_MODE ("auto" or "daylight")
├─ white balance mode for Pi camera
├─ read by: vision.py (picamera2 config)
└─ use "daylight" for outdoor flights to fix blue tint

config.CAMERA_FLIP_180 (True)
├─ camera mounted inverted on drone
├─ read by: vision.py (line ~90, applies cv2.rotate())
```

### Map & Simulation (SIMULATION mode only)

```
config.MAP_FILE ("assets/map.jpg")
config.DUMMY_FILE ("assets/dummy.png")
config.CONE_FILE ("assets/cone.png")
├─ read by: main.py (SIMULATION mode setup)
├─ used by: simulation.SimulationEnvironment
└─ used by: generate_dataset_v2.py (training data generation)

config.MAP_WIDTH_METERS (480.0)
├─ real-world size of satellite map image
├─ read by: utils.GeoTransformer (line 8) — sets pix_per_m
├─ propagates through: planning.py, geofence.py
└─ used to convert pixels ↔ meters

config.REF_LAT (51.425106), config.REF_LON (-2.672257)
├─ top-left corner of satellite map (geographic reference)
├─ read by: utils.GeoTransformer (line 13, 20)
├─ used by: planning.py (polygon conversion)
├─ used by: geofence.py (no-fly zone checking)
└─ from AENGM0074.kml (take-off location)
```

### Search & Flight Areas (GPS polygons)

```
config.SEARCH_AREA_GPS
├─ 5-corner search polygon (list of lat/lon tuples)
├─ read by: main.py (line ~160, _setup_real_search_area())
├─ used by: planning.py.generate_search_pattern()
└─ from AENGM0074.kml or interactive drawing

config.FLIGHT_AREA_GPS
├─ 4-corner max flight boundary
├─ read by: geofence.py (waypoint filtering)
├─ prevents flying outside allowed zone
└─ from AENGM0074.kml

config.SSSI_GPS
├─ SSSI protected area (no-fly zone)
├─ read by: geofence.py (line 20, NFZGeofence init)
├─ used by: geofence.py.distance_to_boundary()
├─ cached as pixel contour for fast point-in-polygon testing
└─ from AENGM0074.kml

config.NFZ_HARD_BOUNDARY_M (50.0)
├─ auto-RTL if this close to SSSI boundary
├─ read by: geofence.py (line 24)
└─ safety margin for hard fence

config.NFZ_SOFT_BOUNDARY_M (100.0)
├─ repulsive force applied beyond soft boundary
├─ read by: geofence.py (line 25)
└─ warning zone; course adjusted but flight continues

config.NFZ_WAYPOINT_BUFFER_M (30.0)
├─ skip waypoints within this distance of SSSI
├─ read by: geofence.py.filter_waypoints()
└─ prevents planning near boundary
```

### Vehicle Specs (for physics)

```
config.DUMMY_HEIGHT_M (1.8)
├─ real casualty/dummy height
├─ used by: generate_dataset_v2.py (synthetic data scaling)
└─ used by: video_test.py (scale bar reference)

config.TARGET_REAL_RADIUS_M (0.15)
├─ casualty torso radius (~15cm)
├─ used by: planning.py (detection envelope calculations)
```

---

## External Dependencies Graph

```
PACKAGE → WHO USES IT → WHY
═════════════════════════════════════════════════════════

pymavlink
├─ imported by: navigation.py, main.py
├─ used for: autopilot commands (arm, takeoff, goto, land)
│            telemetry reading (GPS, attitude, battery)
│            message construction and serial/network protocol
└─ installation: pip install pymavlink

opencv-python (cv2)
├─ imported by: vision.py, planning.py, utils.py, geofence.py, main.py, stream_server.py
├─ used for: camera capture (cv2.VideoCapture)
│            image processing (resize, rotate, flip, undistortion)
│            drawing (polylines, circles for visualization)
│            contour operations (pointPolygonTest for geofence)
│            MJPEG encoding for stream
└─ installation: pip install opencv-python (or opencv-python-headless on Pi)

numpy
├─ imported by: vision.py, planning.py, geofence.py, gps_utils.py
├─ used for: matrix operations, coordinate transformations
│            polygon array handling
│            image array manipulation
└─ installation: pip install numpy (< 2.0 on Pi)

tensorflow / tflite
├─ imported by: vision.py (optional, conditional)
├─ used for: YOLOv8n model inference (AI detection)
│            tries: ultralytics.YOLO (laptop) → tflite_runtime (Pi) → ai-edge-litert (Pi 3.13) → tf.lite
├─ model file: best.tflite (3.2 MB YOLOv8n, input [1,640,640,3], output [1,5,8400])
├─ installation laptop: pip install ultralytics (full YOLO framework)
├─ installation Pi: pip install ai-edge-litert (tflite-runtime broken on Python 3.13)
└─ note: model is loaded only once at startup; inference adds 200ms per frame (Pi)

ultralytics
├─ imported by: vision.py (optional, conditional)
├─ used for: high-accuracy YOLO inference (laptop development)
│            model training / retraining (Colab)
├─ installation laptop: pip install ultralytics
└─ installation Pi: NOT used (too heavy; use TFLite instead)

picamera2 (Pi only)
├─ imported by: vision.py (conditional, if on Pi)
├─ used for: capturing from IMX296 camera module
│            camera controls (white balance, shutter, gain)
│            stream metadata
├─ installation Pi: pre-installed in Raspberry Pi OS 12+
└─ requires: --system-site-packages in venv

http.server, socketserver (stdlib)
├─ imported by: stream_server.py
├─ used for: HTTP server (port 8090) for streaming & dashboard
│            browser buttons → command queue
└─ no installation needed (stdlib)

threading, queue, time, math, json, csv, os, sys (stdlib)
└─ used throughout (run loop, timing, telemetry logging, etc.)

═════════════════════════════════════════════════════════

INSTALLATION QUICK REFERENCE:
  Laptop:  pip install -r requirements_dev.txt
  Pi:      pip install -r requirements_pi.txt
  Docker:  dockerfile.pi-test (validates Pi environment)
```

---

## Circular Dependency Avoidance

### The Problem
main.py needs imports from all modules. state_machine.py is a mixin that main.py inherits from, but some state handlers need `REAL_CANVAS_SIZE` from main.py.

### The Solution
**Lazy import via `_get_main_globals()` in state_machine.py (line 19-26):**

```python
def _get_main_globals():
    """Lazy import of main module globals to avoid circular imports."""
    import main
    return {
        'REAL_CANVAS_SIZE': getattr(main, 'REAL_CANVAS_SIZE', 4800),
        'SIM_SPEED': getattr(main, 'SIM_SPEED', 1),
        'BEACON_DELAY': getattr(main, 'BEACON_DELAY', 0),
    }
```

This is called **at runtime** (not import time) when needed, ensuring main.py has already finished loading state_machine.py.

### Result
- state_machine.py can be imported by main.py without triggering a circular import
- state_machine.py methods can still access main.py globals when called (during run loop)
- No coupling; clean separation of concerns

---

## Summary: Data Path (Camera → Cube)

```
Camera Frame
    ↓ [vision.py] detect_in_image(frame)
Pixel Detection (x, y, confidence)
    ↓ [gps_utils.py] calculate_target_from_pixels()
GPS Target (lat, lon)
    ↓ [state_machine.py] _handle_CENTERING() / _handle_DESCENDING()
MAVLink Command (SET_POSITION_TARGET_GLOBAL_INT)
    ↓ [navigation.py] send_global_target()
Cube Autopilot (ARM, TAKEOFF, GUIDED, LAND)
    ↓ [pymavlink] mav.send_msg()
Drone Flight (motors, servo, autopilot loop)
    ↓ [pymavlink] read_telemetry()
Telemetry (lat, lon, alt, yaw, battery, etc.)
    ↓ [main.py] run loop state update
Operator Dashboard
    ↓ [stream_server.py] HTTP + MJPEG
Browser (http://drone_ip:8090)
```

---

## File Modification Impact

**If you modify:**

- **config.py** → All modules affected (it's read everywhere). Retest all flows.
- **vision.py** → Only detection confidence affected. Retest CV benchmark.
- **planning.py** → Search pattern affected. Verify lawnmower is legal.
- **navigation.py** → MAVLink command format. Retest mission bench (no props).
- **state_machine.py** → State transitions. Retest full mission flow.
- **main.py** → Everything. Retest end-to-end.
- **gps_utils.py** → Landing offset / centering. Retest with dummy.
- **geofence.py** → No-fly zone enforcement. Verify boundary is respected.
- **utils.py** → Geo transformation. Retest map projection accuracy.
- **stream_server.py** → Browser UI only. Retest dashboard.

---

**Last updated:** 2026-03-27
**Version:** v3 (state_machine.py refactor, legacy pi_flight.py preserved as alternative ground station)
