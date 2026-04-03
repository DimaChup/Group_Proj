# Modularity Audit

> Audit of codebase modularity, flexibility, and robustness.
> Date: 2026-04-03

---

## 1. Module Independence

### vision.py -- Camera + AI Detection

**Can it run without main.py?** Yes. VisionSystem is fully self-contained. It imports
only `cv2`, `numpy`, `os`, `sys`, and optionally `config` (with try/except fallback to
defaults). Any script can instantiate `VisionSystem(camera_index=0, model_path="best.tflite")`
and call `detect_in_image(frame)` with zero coupling to the mission logic. This is the
strongest module boundary in the project.

**Dependencies:** cv2, numpy, and one of {ultralytics, tflite-runtime/ai-edge-litert, ncnn}.
Config import is optional (falls back to `DEFAULT_CAM_W=640`, `DEFAULT_CONF_THRESHOLD=0.4`).

**Verdict:** Fully independent. Used by main.py, passive_watch.py, pi_flight.py,
diagnostics.py, and 10+ test scripts without modification.

### planning.py -- Search Pattern Generator

**Can it run without main.py?** Partially. It requires a `GeoTransformer` instance (from
utils.py) and reads `config.TARGET_ALT`, `config.SENSOR_WIDTH_MM`, `config.FOCAL_LENGTH_MM`,
`config.IMAGE_W`, `config.IMAGE_H` at runtime. The `import config` at the top is a hard
dependency (no try/except fallback). It cannot function without config.py present.

**Verdict:** Independent from main.py, but tightly coupled to config.py and utils.py.
Config values are read directly as module-level constants rather than passed as parameters.

### utils.py -- GeoTransformer + overlay_image_alpha

**Can it run without main.py?** Partially. `import config` is at module level with no
fallback. GeoTransformer reads `config.MAP_WIDTH_METERS`, `config.REF_LAT`, `config.REF_LON`
directly. If config.py is absent, the import fails.

**Verdict:** Independent from main.py, but hard-coupled to config.py.

### states.py -- State Enum

**Can it run without main.py?** Yes. Zero imports. Pure data definition.

**Verdict:** Fully independent. No dependencies at all.

### gps_utils.py -- GPS Math

**Can it run without main.py?** Yes. Imports only `math`. All parameters are explicit
function arguments. No config dependency. This is the cleanest module in the project.

**Verdict:** Fully independent. Textbook pure-function design.

### navigation.py -- MAVLink Commands

**Can it run without main.py?** Yes. Requires only `pymavlink` and a `master` connection
object. No config imports. Input validation on all position commands (NaN, bounds, altitude
range). Mode names are validated against a local dict.

**Verdict:** Fully independent. Clean wrapper with good safety checks.

### geofence.py -- NFZ Enforcement

**Can it run without main.py?** Partially. Hard `import config` at module level for
polygon coordinates and buffer distances. Requires a GeoTransformer instance.

**Verdict:** Independent from main.py, coupled to config.py and utils.py.

### stream_server.py -- HTTP Stream Server

**Can it run without main.py?** Yes. No project imports. Pure stdlib + cv2. Thread-safe
by design. Clean module-level API (`set_stream_frame`, `set_telemetry`, `start_stream_server`,
`cmd_queue`).

**Verdict:** Fully independent. Excellent reusable component.

### state_machine.py -- State Handlers Mixin

**Can it run without main.py?** No. Uses `_get_main_globals()` which does `import main`
(lazy, to avoid circular import). The mixin expects `self.nav`, `self.master`, `self.state`,
`self.lat/lon/alt/yaw`, `self.waypoints`, etc. -- all provided by the consuming class in
main.py.

**Verdict:** Tightly coupled to main.py by design (it is a mixin for the mission class).

### passive_watch.py (field_tools/)

**Can it run without main.py?** Yes. Imports `config` and `VisionSystem` from vision.py.
Completely standalone script with its own HTTP server, GPS estimation, threading architecture.
Sends zero MAVLink commands.

**Verdict:** Independent from main.py. Coupled to config.py and vision.py.


## 2. Config Centralisation

### What is centralised (good)

config.py contains 60+ settings covering: mode, connection, flight parameters, camera/optics,
detection thresholds, target specs, NFZ geofence distances, search area GPS polygons,
simulation map paths, servo PWM values, manual flight speeds, and logging path. KML loader
populates GPS zones from file. Environment variable overrides for MODE, CONN, BAUD.

### Hardcoded values that should be in config.py

| File | Value | What it is |
|------|-------|-----------|
| `gps_utils.py:163` | `7.5` | Landing offset distance (metres) |
| `pi_flight.py:425` | `7.5` | Landing offset distance (metres) |
| `simple_simulator.py:266` | `7.5` | Landing offset distance (metres) |
| `stream_server.py:103-106` | `320x240, 5fps, quality 50` | Stream defaults (overridable via function args, but not from config.py) |
| `vision.py:19` | `0.4` | Default confidence threshold fallback |
| `vision.py:29` | `10` | Camera warmup frames |
| `state_machine.py:14` | `4800` | REAL_CANVAS_SIZE fallback |
| `navigation.py:100` | `3.0` | Speed command throttle interval (seconds) |
| `navigation.py:50-51` | `400` | Max altitude guard |
| `passive_watch.py` | `8090` | Default port (also used by pi_flight.py -- conflict risk) |

**Landing offset (7.5m)** is the most significant: it appears in 3 files with no single
source of truth. If someone changes it in one file, the others stay stale.

### What is well-centralised

- All altitude/speed values in config.py
- Camera sensor dimensions and focal length in config.py
- Detection confidence threshold in config.py (with fallback in vision.py)
- GPS zones loaded from KML with config.py fallback
- NFZ distances all in config.py


## 3. Model Swapping

**How easy?** Trivial. Copy the file:
```bash
cp cv_models/sar_v2_1088/best.tflite best.tflite
```
No code changes, no config changes, no restart parameters. All scripts read `best.tflite`
from the project root by default. The `--model` CLI flag on main.py allows runtime switching
without even copying.

**Multiple backends:** vision.py auto-selects Ultralytics (laptop .pt), TFLite (.tflite),
or NCNN (with `--backend ncnn`). All share the same `detect_in_image()` interface.

**Drop-in compatibility:** All exported models use the same input shape [1,640,640,3] and
output shape [1,5,8400], so swapping is truly zero-config.

**Score: 5/5** -- This is a best-practice design.


## 4. Platform Portability

**Same code on Windows and Pi?** Yes. Key mechanisms:

| Mechanism | How |
|-----------|-----|
| Connection auto-detect | `_detect_connection()` in config.py: serial port -> Pi UDP, WSL -> gateway TCP, else localhost |
| Camera auto-detect | vision.py: OpenCV VideoCapture -> picamera2 fallback |
| AI backend auto-detect | vision.py: Ultralytics -> TFLite -> NCNN priority chain |
| Display auto-detect | main.py: `--headless` flag or `DISPLAY` env var check |
| Platform guard | `sys.platform == 'win32'` for `cv2.CAP_DSHOW` (Windows-only) |

**What differs by platform:**
- `requirements_dev.txt` (Windows) vs `requirements_pi.txt` (Pi) -- different packages
- picamera2 + libcamera only on Pi
- calibration_data.npz only on Pi (not in git)
- TFLite runtime variant: `tflite-runtime` vs `ai-edge-litert` (Python 3.13)

**Score: 5/5** -- Excellent cross-platform design without conditional compilation.


## 5. Adding New Features

### Adding a new state
1. Add to `states.py` (1 line)
2. Add handler method to `state_machine.py`
3. Add dispatch entry in `main.py` `run()` method
4. Update transitions in existing handlers

**Effort:** Low. Clear pattern to follow. Well-documented in blueprint.

### Adding a new detection backend
1. Add availability check at top of `vision.py` (try/except import)
2. Add `_try_load_<backend>()` method
3. Add `_detect_<backend>()` method
4. Add to priority chain in `_init_model()`

**Effort:** Low. NCNN was added this way -- the pattern is proven.

### Adding a new calibration
1. Create script in `tests/calibration/`
2. Output calibration data to a file (e.g., `.npz`)
3. Load in vision.py or config.py at startup

**Effort:** Low. Existing `calibration_data.npz` flow is a template.

### Adding a new flight test script
1. Create in `tests/flight/` with appropriate number prefix
2. Import what you need (vision.py, navigation.py, config.py)
3. No framework or base class required

**Effort:** Very low. Flat script structure makes this trivial.


## 6. Error Handling

### Where it fails gracefully

| Module | Mechanism |
|--------|-----------|
| `vision.py` | 34 try/except blocks. Missing model file -> prints warning, detection disabled (mission flies but never detects). Missing camera -> prints warning, `get_frame()` returns None. Missing config -> falls back to defaults. Missing calibration -> skips undistortion. |
| `config.py` | KML file not found -> prints warning, uses fallback GPS coordinates. WSL detection failure -> falls back to localhost. |
| `navigation.py` | NaN/out-of-bounds GPS -> prints WARNING, skips command. Invalid mode name -> raises ValueError with helpful message listing valid modes. Zero/negative takeoff altitude -> prints warning, returns. |
| `stream_server.py` | Port in use -> tries next 5 consecutive ports. Broken pipe on stream -> silently disconnects client. No frame available -> returns 503. |
| `geofence.py` | No polygon configured -> returns `(inf, False)` (safe, no restriction). |
| `gps_utils.py` | No error handling needed -- pure math functions with well-defined inputs. |

### Where it can crash

| Module | Risk |
|--------|------|
| `planning.py` | Zero try/except blocks. If `config.FOCAL_LENGTH_MM` is zero -> division by zero. If polygon vertices are degenerate -> cv2 errors. |
| `utils.py` | Zero try/except blocks. If `config.MAP_WIDTH_METERS` is zero -> division by zero in `GeoTransformer.__init__()`. |
| `state_machine.py` | Depends on main.py attributes existing. If any `self.` attribute is missing -> AttributeError with no helpful message. `_get_main_globals()` does `import main` which could fail if main.py has a syntax error. |
| `passive_watch.py` | 3000+ lines with limited error handling around GPS estimation. Thread crashes are caught by daemon thread status but not always reported clearly. |
| `main.py` | Top-level try/except wraps `run()`, but individual state handlers in the mixin can throw unhandled exceptions that abort the mission. |


## 7. Testing

### Can modules be tested independently?

| Module | Independently testable? | How |
|--------|------------------------|-----|
| `vision.py` | Yes | `vs = VisionSystem(None, "best.tflite"); vs.detect_in_image(frame)` |
| `planning.py` | Yes (needs config.py + utils.py) | `PathPlanner(geo, polygon).generate_search_pattern(w, h)` |
| `gps_utils.py` | Yes | Pure functions, no setup needed |
| `navigation.py` | Yes (needs pymavlink mock) | `NavigationController(mock_master)` |
| `geofence.py` | Yes (needs config.py + utils.py) | `NFZGeofence(geo).check_position(lat, lon)` |
| `stream_server.py` | Yes | `start_stream_server(port=9999)` |
| `states.py` | Yes | Just constants |
| `state_machine.py` | No | Mixin requires full mission object |
| `config.py` | Yes | Import and read values |

### Existing test coverage

41 test scripts in `tests/` covering hardware, flight, diagnostics, calibration, experiments,
and laptop development. Tests are structured as standalone scripts rather than pytest/unittest,
which means:
- No automated test runner
- No assertions (visual/manual verification)
- No CI/CD integration
- But very practical for robotics (hardware-in-the-loop testing)


## 8. Dependency Graph

```
                    +-----------+
                    | states.py |  (zero deps)
                    +-----------+
                         |
                    +-----------+
                    | config.py |  (os, platform, subprocess)
                    +-----------+
                    /    |    \
                   /     |     \
          +--------+  +------+  +-----------+
          |utils.py|  |geofnc|  |planning.py|
          +--------+  +------+  +-----------+
              |           |          |
              +-----------+----------+
                          |
              +-----------+-----------+
              |                       |
         +----------+          +----------+
         |vision.py |          |gps_utils |  (zero deps)
         +----------+          +----------+
              |                       |
              +-----------+-----------+
                          |
              +-----------+-----------+
              |                       |
         +----------+        +-------------+
         |navigatn. |        |stream_server|  (zero project deps)
         +----------+        +-------------+
              |                       |
              +-----------+-----------+
                          |
                  +---------------+
                  |state_machine  |  (mixin for main)
                  +---------------+
                          |
                     +--------+
                     |main.py |  (orchestrator)
                     +--------+
```

### Circular imports

**One circular dependency exists:** `state_machine.py` imports `main` (lazy, via
`_get_main_globals()`). This is handled with a deferred import inside a function,
so it does not cause an import error, but it is a code smell. The values it reads
(`REAL_CANVAS_SIZE`, `SIM_SPEED`, `BEACON_DELAY`) should be passed as constructor
parameters or stored in config.py instead.

### Import direction violations

None beyond the state_machine.py case above. All other imports flow downward
(main -> modules -> config). vision.py's config import is optional with fallback.


## Summary Scorecard

| Module | Independence | Configurability | Error Handling | Testability | Overall |
|--------|:---:|:---:|:---:|:---:|:---:|
| **vision.py** | 5 | 5 | 5 | 5 | **5.0** |
| **gps_utils.py** | 5 | 5 | 4 | 5 | **4.8** |
| **states.py** | 5 | 5 | 5 | 5 | **5.0** |
| **stream_server.py** | 5 | 4 | 5 | 5 | **4.8** |
| **navigation.py** | 5 | 3 | 5 | 4 | **4.3** |
| **config.py** | 5 | 5 | 4 | 5 | **4.8** |
| **geofence.py** | 3 | 4 | 4 | 4 | **3.8** |
| **planning.py** | 3 | 3 | 2 | 3 | **2.8** |
| **utils.py** | 3 | 3 | 2 | 4 | **3.0** |
| **state_machine.py** | 1 | 3 | 3 | 1 | **2.0** |
| **main.py** | 1 | 4 | 3 | 2 | **2.5** |
| **passive_watch.py** | 3 | 4 | 3 | 3 | **3.3** |

### Overall Project Score: 3.8 / 5.0

### Strengths

1. **vision.py is exemplary.** Clean interface, optional config, three backend fallbacks,
   34 try/except blocks, zero coupling to mission logic. Every other module in the project
   should aspire to this design.

2. **gps_utils.py is textbook.** Pure functions, explicit parameters, no hidden state,
   no config dependency. Perfect for unit testing.

3. **Platform portability is excellent.** Auto-detection at every level (connection, camera,
   AI backend, display) means the same code runs on Windows, WSL, and Pi without changes.

4. **Model swapping is trivial.** Copy one file. No code changes. This is exactly right for
   field operations where you need to swap models quickly.

5. **stream_server.py is well-isolated.** Thread-safe, no project dependencies, clean public
   API. Could be extracted as a standalone library.

### Weaknesses

1. **Landing offset (7.5m) is hardcoded in 3 files.** Should be `config.LANDING_OFFSET_M`.

2. **planning.py and utils.py have no error handling.** Division by zero from bad config
   values would crash silently.

3. **state_machine.py circular import.** The lazy `import main` in `_get_main_globals()`
   should be replaced by passing values through the constructor or config.py.

4. **passive_watch.py is 3000+ lines.** The DummyEstimator, SmartEstimator, and rendering
   functions should be extracted into separate modules (e.g., `gps_estimator.py`,
   `overlay_renderer.py`).

5. **No automated test framework.** All 41 test scripts are manual. Adding pytest with
   unit tests for gps_utils.py, planning.py, and geofence.py would catch regressions.

### Recommended Actions (by priority)

1. **Move `7.5` to `config.LANDING_OFFSET_M`** and reference it from gps_utils.py,
   pi_flight.py, and simple_simulator.py.
2. **Add try/except in planning.py** around footprint calculation (div-by-zero guard).
3. **Remove circular import** in state_machine.py -- pass `REAL_CANVAS_SIZE`, `SIM_SPEED`,
   `BEACON_DELAY` as constructor args or put them in config.py.
4. **Extract GPS estimation classes** from passive_watch.py into a shared module
   (pi_flight.py could reuse them).
5. **Add pytest unit tests** for gps_utils.py (pure functions, easy to test) and
   planning.py (waypoint count, polygon coverage, edge cases).
