# SIMULATION vs REAL Mode: Comprehensive Code Path Mapping

Last updated: 2026-04-03

This document maps every divergence between SIMULATION and REAL mode across the codebase.
The mode is set by `config.MODE = os.environ.get("DRONE_MODE", "SIMULATION")` (default: SIMULATION).

---

## Files with zero MODE checks (mode-agnostic)

These modules have **no** `config.MODE` branches. Code path is identical in both modes:

| File | Notes |
|------|-------|
| `vision.py` | Backend auto-detects (Ultralytics/TFLite/NCNN). Camera opens OpenCV then falls back to picamera2. No MODE check. |
| `planning.py` | Pure geometry — generates waypoints from pixel polygons. |
| `utils.py` | GPS<->pixel math (GeoTransformer). |
| `gps_utils.py` | `calculate_target_from_pixels`, `landing_offset_7_5m`. |
| `navigation.py` | MAVLink velocity/position commands. |
| `geofence.py` | NFZ boundary math. |
| `stream_server.py` | MJPEG + telemetry JSON server. |
| `states.py` | State enum only. |

---

## Master Divergence Table

Every `if config.MODE == "SIMULATION"` / `"REAL"` branch, traced to the exact file and line.

### 1. Import / Module Loading

| Component | SIMULATION | REAL | Risk |
|-----------|-----------|------|------|
| **Simulation env** | `from simulator.simulation import SimulationEnvironment` (main.py:28, pi_flight.py:66, simple_simulator.py:45) | Not imported | **None** -- guarded by MODE check |

### 2. Initialization (main.py `__init__`, lines 242-274)

| Component | SIMULATION | REAL | Risk |
|-----------|-----------|------|------|
| **SimulationEnvironment** | Created. `self.sim` holds map, targets, god-view. `self.geo` derived from map pixel width. | `self.sim = None`. `self.geo` uses `config.REAL_CANVAS_SIZE` (4800 px). | **LOW** -- `REAL_CANVAS_SIZE` is arbitrary; only affects pixel->GPS scaling in GeoTransformer. Search polygon is immediately converted to GPS anyway. |
| **Search area source** | `preload_gps = config.SEARCH_AREA_GPS` passed to `sim.setup_on_map()` which opens interactive map drawing window. Returns pixel polygon. | `_setup_real_search_area()` loads from `flight_plans/search_area.json`, falls back to `config.SEARCH_AREA_GPS` / KML. No interactive drawing. | **MEDIUM** -- In REAL mode, if `search_area.json` is missing AND KML load failed, the drone has no search polygon. Would get empty waypoints and enter HOVER. Not dangerous but mission fails silently. |
| **VisionSystem camera_index** | `camera_index=None` (no camera opened; sim renders frames). AI enabled only if target type is "dummy". | `camera_index=config.REAL_CAMERA_INDEX` (0). AI enabled if model loads. | **LOW** -- Different but correct for each mode. |
| **Canvas size for pattern gen** | `self.sim.map_w, self.sim.map_h` (from map.jpg dimensions, ~4900x3600). | `config.REAL_CANVAS_SIZE, config.REAL_CANVAS_SIZE` (4800x4800). | **LOW** -- Only affects GeoTransformer pixel scale. GPS waypoints are the same regardless because the polygon is defined in GPS coords. |

### 3. Connection (state_machine.py `_handle_connecting`, line 147)

| Component | SIMULATION | REAL | Risk |
|-----------|-----------|------|------|
| **Connection string** | `tcp:127.0.0.1:5762` (auto-detected: no serial port found, not WSL, default). | `udpin:0.0.0.0:14550` (auto-detected: `/dev/ttyAMA0` exists on Pi). | **None** -- auto-detection in `config._detect_connection()` handles this correctly. Can be overridden with `DRONE_CONN` env var. |
| **SIM_SPEEDUP param** | Sends `SIM_SPEEDUP` parameter to SITL (`config.SIM_SPEED`, default 1). | Skipped. | **None** -- SITL-only parameter, harmless if sent to real Cube (param doesn't exist, ignored). |
| **Data stream request** | Same `MAV_DATA_STREAM_ALL` at 10Hz. | Same. | **None** -- identical code path. |

### 4. Takeoff Recovery (state_machine.py `_handle_takeoff`, lines 212-217)

| Component | SIMULATION | REAL | Risk |
|-----------|-----------|------|------|
| **Disarm during takeoff** | Re-enters ARMING state (SITL auto-disarm if `DISARM_DELAY` > 0). | Transitions to DONE (safety stop). Requires manual re-arm via RC. | **CRITICAL BEHAVIORAL DIFFERENCE** -- In SIMULATION, auto-disarm is a nuisance that triggers auto-retry. In REAL, disarm during takeoff means something is wrong (failsafe, GPS loss) and the correct response is to stop. The code handles this correctly. |

### 5. Altitude-Reached Pattern Generation (state_machine.py `_handle_takeoff`, lines 227-230)

| Component | SIMULATION | REAL | Risk |
|-----------|-----------|------|------|
| **Canvas size** | `self.sim.map_w, self.sim.map_h` | `config.REAL_CANVAS_SIZE, config.REAL_CANVAS_SIZE` | **LOW** -- Same pattern as init. GPS output is identical. |

### 6. Rescan Pattern Regeneration (state_machine.py `_advance_waypoint`, line 418)

| Component | SIMULATION | REAL | Risk |
|-----------|-----------|------|------|
| **Canvas size** | `self.sim.map_w, self.sim.map_h` | `config.REAL_CANVAS_SIZE, config.REAL_CANVAS_SIZE` | **LOW** -- Same as above. |

### 7. Beacon Redirect (state_machine.py `_trigger_beacon_redirect`, line 832)

| Component | SIMULATION | REAL | Risk |
|-----------|-----------|------|------|
| **Canvas size** | `self.sim.map_w, self.sim.map_h` | `config.REAL_CANVAS_SIZE, config.REAL_CANVAS_SIZE` | **LOW** -- Same pattern. |

### 8. Frame Acquisition (main.py `update_dashboard`, lines 561-585)

| Component | SIMULATION | REAL | Risk |
|-----------|-----------|------|------|
| **Frame source** | `self.sim.get_drone_view(px, py, alt, yaw)` -- renders a cropped/rotated view of map.jpg at the drone's simulated position. Returns frame + FOV dimensions. | `self.eyes.get_frame()` -- reads from OpenCV VideoCapture or picamera2. Returns raw BGR frame. | **HIGH RISK OF MISMATCH** -- see detailed analysis below. |
| **Camera failure handling** | Never None (simulation always renders). | Can return None (camera disconnect, hardware fault). Replaced with black frame + "CAMERA LOST" text. Warns every 5s. | **REAL-ONLY SAFETY** -- well handled. |
| **Frame resolution** | Determined by simulated FOV at altitude. Variable size. | `config.IMAGE_W x config.IMAGE_H` (1456x1088). Fixed. | **MEDIUM** -- detection pixel coords are relative to frame size. In SIM, frame size varies with altitude. In REAL, it's always 1456x1088. GPS estimation uses `config.IMAGE_W/H` in both modes, so SIM GPS estimates may be slightly off if sim frame dimensions differ from config. |

### 9. God-View Display (main.py `update_dashboard`, lines 659-674)

| Component | SIMULATION | REAL | Risk |
|-----------|-----------|------|------|
| **God view** | Renders top-down map with drone position, polygon overlays, waypoints, NFZ. Shown side-by-side with camera view. | Not rendered. Only camera frame shown. | **None** -- display only. No effect on flight logic. |

### 10. Window Setup (main.py `run`, lines 718-719)

| Component | SIMULATION | REAL | Risk |
|-----------|-----------|------|------|
| **Mouse callback** | `cv2.setMouseCallback` registered for interactive map zoom/pan. | Not registered. | **None** -- display only. |

### 11. pi_flight.py Divergences

| Component | SIMULATION | REAL | Risk |
|-----------|-----------|------|------|
| **SimulationEnvironment** (line 442-463) | Created with interactive map setup. Targets placed on map. `self.eyes` has `camera_index=None`. | Not created. `self.eyes = VisionSystem(camera_index=config.REAL_CAMERA_INDEX)`. | **None** -- correct separation. |
| **Search area** (line 465-484) | From `sim.setup_on_map()` interactive drawing. | From `search_area.json` or `config.SEARCH_AREA_GPS`. | **Same as main.py** |
| **Frame source** (line 553-558) | `self.sim.get_drone_view(px, py, alt, yaw)` | `self.eyes.get_frame()` | **Same as main.py** |

### 12. simple_simulator.py Divergences

| Component | SIMULATION | REAL | Risk |
|-----------|-----------|------|------|
| **SimulationEnvironment** (line 108) | Full sim setup with map, targets, interactive polygon drawing. | Not created (simple_simulator is laptop-only anyway). | **None** -- simple_simulator is not intended for REAL mode. |
| **Frame source** (line 741) | `self.sim.get_drone_view()` | `self.eyes.get_frame()` | **N/A** -- laptop-only tool. |
| **Error display** (lines 830, 861) | Shows actual vs estimated GPS error on screen. | Not shown (no ground truth). | **None** -- debug display only. |

### 13. field_tools/system_readiness.py (line 145)

| Component | SIMULATION | REAL | Risk |
|-----------|-----------|------|------|
| **Camera check** | Tests webcam via `cv2.VideoCapture(0)`. Reports WARN if no webcam. | Tests picamera2 via `Picamera2()`. Reports FAIL if no Pi camera. | **None** -- preflight diagnostic only. |

---

## Implicit Differences (No MODE check, but behavior differs by platform)

These are differences that arise from the hardware/software environment, NOT from explicit `if config.MODE` branches:

| Component | Laptop (SIMULATION) | Pi (REAL) | Risk |
|-----------|-----------|------|------|
| **AI backend** | Ultralytics YOLO (.pt files) or TFLite. ~330ms on CPU. | TFLite or NCNN only (no PyTorch/Ultralytics). TFLite ~206ms, NCNN ~72ms. | **MEDIUM** -- Ultralytics is skipped for `.tflite` files (line 392 in vision.py), so if using `best.tflite`, both platforms use the TFLite backend. If using `.pt` files, REAL mode would fail (no Ultralytics on Pi). The `--model` flag defaults to `best.tflite`, so this is safe in practice. |
| **Camera API** | `cv2.VideoCapture` with `CAP_DSHOW` (Windows). | `cv2.VideoCapture` first, falls back to `picamera2`. IMX296 outputs BGR despite RGB888 label. | **LOW** -- vision.py handles both paths transparently. The IMX296 BGR quirk is documented and accounted for (no cvtColor applied). |
| **Camera resolution** | Webcam native (varies, typically 640x480 or 1280x720). Config requests 1456x1088 but webcam may not support it -- falls back gracefully. | Pi camera IMX296: 1456x1088 native. | **MEDIUM** -- If laptop webcam gives 640x480 but `config.IMAGE_W/H` says 1456x1088, the GPS estimation math uses config values. The actual frame may be smaller, causing detection pixel coords to be in a different coordinate space than expected. In practice, VisionSystem logs the actual resolution but `config.IMAGE_W/H` is used elsewhere. |
| **Camera flip** | `config.CAMERA_FLIP_180 = True` applies `cv2.flip(frame, -1)`. On laptop webcam this flips the image upside down. | Same flip applied. Correct because Pi camera is mounted inverted on the drone. | **LOW** -- Flip is wrong for laptop webcam (image upside down in REAL mode on laptop). Only matters for REAL+laptop testing, not for actual flights. |
| **Lens undistortion** | `config.UNDISTORT_ENABLED = False`. Even if True, needs `calibration_data.npz` which is Pi-specific. | Same config, but `calibration_data.npz` was found to be corrupt and deleted. Undistortion off. | **None** -- disabled in config. |
| **Connection auto-detect** | Returns `tcp:127.0.0.1:5762` (no serial port on laptop). | Returns `udpin:0.0.0.0:14550` (detects `/dev/ttyAMA0`). | **None** -- auto-detection works correctly. |
| **GPS source** | SITL: perfect GPS, 0 drift, instant fix, high sat count. | Real GNSS: 2-5m CEP, 100-200ms latency, variable sat count, fix can degrade. | **HIGH** -- See detailed analysis below. |
| **Barometer** | SITL: perfect baro, 0 drift. | Real: baro drift, temperature sensitivity. | **MEDIUM** -- Landing detection uses `alt < 0.5m` threshold with 5-tick hysteresis. Baro drift could cause false triggers or stall. Mitigated by 90s timeout + force disarm. |
| **Wind** | None. | Real wind gusts affect position hold, ground speed, centering accuracy. | **HIGH** -- No wind compensation code exists. ArduPilot's position controller handles it, but GPS estimation assumes stationary drone during detection. Wind-blown drift between detection and GPS read introduces error. |
| **Frame rate** | ~30 FPS (webcam) or unlimited (simulation renders). | ~5-14 FPS depending on AI backend (TFLite ~5, NCNN ~14). | **MEDIUM** -- Lower FPS means fewer detection opportunities per pass. At 10 m/s search speed, each frame covers different ground. Miss rate increases with lower FPS. The SMART detect feature (`--smart-detect`) requires consecutive frames, which is harder at lower FPS. |
| **Inference speed** | Ultralytics (.pt): ~50ms GPU, ~330ms CPU. TFLite: ~100ms. | TFLite: ~206ms. NCNN: ~72ms. | **LOW** -- speed affects FPS (above) but detection quality is identical (same model weights). |
| **cv2.imshow** | Available. Shows "Mission Dashboard" window. | Not available headless. `--headless` flag disables all cv2 windows. Browser stream at port 8090 instead. | **None** -- handled by HEADLESS flag, independent of MODE. |
| **Terminal input** | `msvcrt` on Windows (main.py line 144). | `tty/termios` on Linux/Pi (main.py line 150). | **None** -- platform detection, not MODE-dependent. |
| **Motor direction** | SITL physics model -- motors "just work". | Real ESC + motor wiring must be correct. Wrong rotation = flip on takeoff. | **OUTSIDE CODE** -- not a code path difference. Verified in Mission Planner motor test. |
| **Servo control** | `MAV_CMD_DO_SET_SERVO` sent to SITL. SITL logs it but has no physical servo. | Same MAVLink command. Physical servo moves. | **LOW** -- identical code. SITL just ignores the physical effect. |

---

## Detailed Risk Analysis

### HIGH RISK: GPS Accuracy Mismatch

**Problem**: SITL GPS is perfect. Real GPS has:
- 2-5m CEP (circular error probable)
- 100-200ms latency (1m error at 5m/s)
- Multipath in cluttered environments
- Satellite geometry variations (HDOP)

**Affected code paths**:
- `calculate_target_gps()` -- converts pixel detection to GPS using drone GPS + altitude + camera FOV. In SIM, drone GPS is exact, so the only error is pixel quantization. In REAL, drone GPS error directly adds to target estimate error.
- `get_dist_to_target()` / `get_dist_to_point()` -- uses `self.lat/lon` which has GPS noise. Waypoint acceptance radius of 2.0m may cause premature or delayed transitions.
- `_gps_avg_samples` in VERIFY -- averages GPS over 10s. Helps with noise but not systematic bias.
- `_is_near_known()` -- uses 5m radius to skip known targets. With 3m GPS error, could falsely skip a new target near a rejected one, or fail to skip a duplicate.

**Mitigation**: The `--center-verify` flag enables GPS averaging over 10 seconds at hover, which reduces random error. Systematic GPS lag is unaddressed.

### HIGH RISK: Camera Frame Source

**Problem**: Simulation renders a perfectly aligned, undistorted, correctly-scaled view of map.jpg. Real camera has:
- Lens distortion (IMX296 is low but non-zero)
- Motion blur at speed
- Exposure/white balance variations (sun angle, shadows, clouds)
- Vibration from motors
- Different aspect ratio / resolution than simulated view

**Affected code paths**:
- `detect_in_image()` -- model trained on synthetic data (map.jpg composites). Real outdoor scenes look very different. Detection confidence and recall may differ significantly.
- `update_dashboard()` -- pixel coordinates from detection are used for `calculate_target_gps()`. In SIM, the frame is geometrically correct (rendered from known position). In REAL, camera mounting angle, gimbal tilt, or roll/pitch offsets cause the pixel->GPS mapping to be wrong.

**Mitigation**: Model retrained on real + synthetic data (v2, mAP50=0.995). Lens undistortion available but disabled. Camera mounting assumed nadir (straight down).

### MEDIUM RISK: Canvas Size / GeoTransformer Scaling

**Problem**: The `GeoTransformer` converts between GPS and pixel coordinates. In SIMULATION, it's calibrated to map.jpg dimensions with known `REF_LAT/LON` and `MAP_WIDTH_METERS`. In REAL, it uses `REAL_CANVAS_SIZE = 4800` with the same REF_LAT/LON.

**Why it works**: The search polygon is defined in GPS coordinates. `gps_to_pixels()` converts to pixels for internal math (planning, polygon tests). `pixels_to_gps()` converts back. As long as the same GeoTransformer is used consistently, the roundtrip is accurate. The absolute pixel values don't matter -- only the GPS values fed to MAVLink commands matter.

**Where it could break**: If GeoTransformer precision degrades at high pixel counts, or if the linear approximation (meters per degree) diverges over the search area. At 51.4N latitude, 1 degree longitude = ~70km. The search area is ~300m across, so the linear approximation error is < 0.01%.

---

## Summary: What Could Break Going SIM -> REAL

| # | Issue | Severity | Likelihood | Notes |
|---|-------|----------|------------|-------|
| 1 | GPS noise causes target GPS estimate to be 3-5m off | HIGH | CERTAIN | Inherent to real GPS. Mitigated by `--center-verify` averaging. |
| 2 | Model misses detections in real outdoor conditions | HIGH | LIKELY | Trained on synthetic + 16 real images. Need more real data. |
| 3 | Motion blur reduces detection at speed | MEDIUM | LIKELY | No exposure control. IMX296 global shutter helps. |
| 4 | Wind pushes drone off waypoints, affects centering | MEDIUM | LIKELY | ArduPilot compensates, but GPS estimation assumes stationary. |
| 5 | Baro drift causes landing detection issues | MEDIUM | POSSIBLE | 0.5m threshold + 5-tick + 90s timeout + force disarm. |
| 6 | Camera fails mid-flight (connector, overheating) | LOW | UNLIKELY | Black frame fallback + warning. Mission continues blind. |
| 7 | Lower FPS causes missed detections on fast passes | MEDIUM | LIKELY | 5 FPS at 10 m/s = one frame every 2m of travel. |
| 8 | SMART detect needs N consecutive frames -- harder at low FPS | LOW | POSSIBLE | Use N=2 or 3 (default 3). At 5 FPS and 10m/s, target in view for ~4 frames at 35m alt. |
| 9 | `config.IMAGE_W/H` mismatch with actual camera resolution | LOW | UNLIKELY | VisionSystem logs actual res. Config set to 1456x1088 which matches IMX296. |
| 10 | Webcam flip (CAMERA_FLIP_180) wrong for laptop REAL mode testing | LOW | ONLY FOR TESTING | Correct for Pi drone mount. Wrong for laptop webcam. |

---

## Checklist Before First Real Flight

Based on this analysis, verify these before switching from SIMULATION to REAL:

- [ ] `search_area.json` or KML file exists and is correct (no interactive drawing in REAL headless mode)
- [ ] `best.tflite` on Pi is the correct model (cp from `cv_models/sar_v2_1088/best.tflite`)
- [ ] `config.IMAGE_W/H` matches actual Pi camera resolution (1456x1088 for IMX296)
- [ ] `config.CAMERA_FLIP_180 = True` (camera mounted inverted on drone)
- [ ] `config.UNDISTORT_ENABLED = False` (no valid calibration file)
- [ ] `config.CONFIDENCE_THRESHOLD` set appropriately (currently 0.2 -- very permissive)
- [ ] GPS fix verified before mission (ARMING state waits for fix_type >= 3, sats >= 6)
- [ ] Waypoint acceptance radius (2.0m) reasonable given real GPS noise
- [ ] `--center-verify` flag recommended for GPS averaging at target
- [ ] `--smart-detect` with `DETECT_CONFIRM_FRAMES = 2` or 3 (not too high for low FPS)
- [ ] mavproxy running with correct baud rate and UDP outputs
- [ ] RC kill switch tested (mode switch away from GUIDED stops all commands)
