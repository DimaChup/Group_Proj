# Simple Simulator — Documentation

`simple_simulator.py` is an interactive MVP for testing drone CV, GPS estimation, and
centering logic before committing to the full state machine in `main.py`. It connects
to SITL (or a real Cube), gives you keyboard RC controls, runs YOLOv8 detection on the
simulated camera, and estimates the target's GPS from pixel detections.

## Why This Exists

`main.py` is a full autonomous state machine (SEARCH, CENTERING, DESCENDING, VERIFY,
LANDING). That's great for a real mission, but terrible for iterating on individual
pieces. The simple simulator lets you:

- Fly manually and watch CV detections happen in real time
- Test GPS estimation accuracy under realistic conditions
- Compare GPS centering vs visual servo centering
- Simulate Pi hardware constraints (slow FPS, TFLite, GPS drift, camera shake)
- Tune parameters (gains, thresholds) interactively

Same MAVLink, same CV pipeline, same GPS math as `main.py` — just with you in the loop
instead of the state machine.

---

## How to Run

### Basic (no realism flags — full speed, Ultralytics, perfect GPS)
```bash
python simple_simulator.py
```

### Realistic (match Pi hardware conditions)
```bash
python simple_simulator.py --tflite --fps 4 --gps-drift 5 --shake 5
```

### Requires
- SITL running (Mission Planner or mavproxy)
- `config.py` with `MODE = "SIMULATION"`
- `map.jpg` and `best.tflite` in the project root

---

## Keyboard Controls

| Key | Action |
|-----|--------|
| SPACE | Arm / disarm (sets GUIDED mode first) |
| W / S | Fly forward / back |
| A / D | Fly left / right |
| Q / E | Yaw left / right |
| R | Throttle up (takeoff if on ground, climb if airborne) |
| F | Throttle down (descend) |
| C | Toggle GPS centering (fly to estimated target GPS) |
| V | Toggle visual servo (pixel-based centering) |
| L | Emergency land |
| ESC | Quit |
| Scroll | Zoom god view (simulation only) |

WASD/QE/RF override and cancel C or V modes.

---

## Features

### 1. MAVLink Connection
Connects to SITL or real Cube via `config.CONNECTION_STR`. Filters mavproxy GCS
heartbeats (type=6) and extracts `target_system` from the first autopilot heartbeat.
Same fixes applied to `main.py` for Pi compatibility.

### 2. CV Detection
Uses `VisionSystem` from `vision.py` — same dual-backend system as the real mission.
Ultralytics (laptop) or TFLite (Pi). Detections return `(found, u, v, confidence)`.

### 3. GPS Estimation from Pixels
When the target is detected at pixel `(u, v)`:
1. Compute GSD (ground sample distance) from altitude and camera intrinsics
2. Convert pixel offset from image centre to metres (forward/right)
3. Rotate by drone yaw to get North/East offsets
4. Add to drone GPS position to get target GPS estimate

**Centre-snap**: When the target is within 30px of image centre, the drone's GPS
is used directly as the target GPS (most accurate — target is directly below).

**Weighted averaging**: Each observation gets a weight based on distance from image
centre (centre = weight 5, edge = weight 1, snap = weight 10). The best estimate is
the weighted average of the last 50 observations. This smooths out noise and converges
toward the true position over time.

### 4. GPS Centering (C key)
Flies the drone to the weighted-average GPS estimate using
`SET_POSITION_TARGET_GLOBAL_INT`. Works even when the target isn't visible (uses last
known position). Accuracy limited by GPS error (~2.5m for Here 3+ without RTK).

### 5. Visual Servo (V key)
Pixel-based centering that bypasses GPS entirely:
1. Compute pixel error: `err_x = target_u - centre_u`
2. Apply EMA smoothing to filter out camera shake noise
3. Proportional controller: `velocity = Kp * smoothed_error`
4. Clamp to max speed (2 m/s)
5. Send body-frame velocity via `SET_POSITION_TARGET_LOCAL_NED`

**Why both C and V?** GPS centering gets you within ~3-5m (GPS accuracy). Visual servo
takes over from there for sub-metre precision. C works blind (no target needed), V needs
the target visible. The intended workflow: **C to get close, V to get precise.**

**EMA filter**: `smooth = alpha * raw + (1-alpha) * smooth` with alpha=0.3. This means
each new detection contributes 30% and the history contributes 70%. Dampens shake-induced
pixel jitter without adding significant lag. Filter resets when V is toggled off/on.

### 6. HUD Overlay
The camera view shows:
- Crosshair at image centre
- Detection marker (green circle + line to centre)
- ARM/DISARM status
- Altitude, speed, position, yaw
- Detection count
- GPS CENTRE / VISUAL SERVO mode indicator
- SNAP indicator when target is dead centre
- GPS estimates: BEST (weighted avg, cyan), LATEST (single, green), ACTUAL (ground truth, orange)
- Error in metres for each estimate (green < 3m, orange < 10m, red > 10m)
- Active simulation flags (GPS DRIFT, SHAKE)

---

## Simulation Flags

All flags are **optional**. Default behaviour is unchanged (full speed, Ultralytics,
perfect GPS, no shake). Flags simulate real-world Pi hardware conditions.

### `--fps N` — CV Throttle

**What**: Only runs AI inference every `1/N` seconds. Between inferences, returns the
last detection result.

**Why**: On the Raspberry Pi 5, TFLite inference takes ~256ms per frame (~4 FPS). On the
laptop with Ultralytics + GPU, it runs at 30+ FPS. This flag throttles the laptop to
match Pi speed, so you can see how the system behaves with delayed/stale detections.

**How it works**: Tracks `last_cv_time`. If less than `1/N` seconds have passed, skips
`process_frame_manually()` and returns cached `_last_detection`. The camera frame is
still captured fresh (just not processed by AI).

**Realistic value**: `--fps 4`

### `--tflite` — Force TFLite Backend

**What**: Forces the TFLite inference backend instead of Ultralytics.

**Why**: The Pi runs TFLite (no PyTorch/Ultralytics). TFLite has slightly different
detection characteristics (confidence values, bounding box precision). Testing with
TFLite on the laptop ensures you see what the Pi will see.

**How it works**: Temporarily hides `YOLO` from `vision.py` module globals and forces
import of TFLite interpreter (`tflite_runtime` > `ai_edge_litert` > `tensorflow.lite`).
Falls back to Ultralytics if no TFLite backend is available.

**Note**: Requires at least one TFLite backend installed. `pip install tensorflow` works
on the laptop (includes `tf.lite.Interpreter`).

### `--gps-drift N` — Simulated GPS Error

**What**: Adds up to N metres of GPS wander to the reported drone position.

**Why**: Real GPS (Here 3+ without RTK) has ~2.5m CEP accuracy — meaning 50% of readings
are within 2.5m of truth, and the rest can be further. This directly affects GPS
estimation (target GPS = drone GPS + pixel offset) and GPS centering (C key flies to a
potentially wrong coordinate).

**How it works**: A slow random walk (Ornstein-Uhlenbeck process) with:
- Wander speed: ~0.3 m/s
- Mean-reverting: drifts back toward zero over time
- Hard clamp: never exceeds N metres from true position
- Applied to `self.lat`/`self.lon` only (what the drone "reports")
- `self.true_lat`/`self.true_lon` remain physical position (used for camera rendering)

This separation is critical: the camera sees the real world (true position), but all
GPS math uses the drifted reading (what the drone thinks).

**Realistic values**:
- `--gps-drift 2.5` — matches Here 3+ CEP (median case)
- `--gps-drift 5` — worst case for Here 3+ in standard mode (recommended for testing)

**GPS reference**: CubePilot Here 3+ uses u-blox M8P-2 chip. Standard 3D fix: 2.5m CEP.
RTK mode: 2.5cm (not used in this project — no base station).

### `--shake N` — Camera Vibration

**What**: Adds random pixel jitter to the camera position each frame, simulating motor
vibration.

**Why**: Drone motors create high-frequency vibration that shifts the camera slightly
between frames. This affects visual servo accuracy (target pixel position jitters) and
GPS estimation (pixel-to-GPS math has noise).

**How it works**: Each frame, adds `gauss(0, N*0.5)` pixels to the camera crop position
on the map. This is a Gaussian distribution centred at zero with standard deviation of
half the specified value, so most frames shake less than N pixels.

**What it affects**:
- Visual servo (V key) — target bounces around, controller must handle noisy input
- GPS estimation — each pixel detection has a small random error
- The EMA filter on the visual servo smooths this out

**What it does NOT affect**:
- GPS centering (C key) — flies to a GPS coordinate, camera not involved
- Detection itself — YOLO is robust to small positional shifts

**Realistic values**:
- `--shake 5` — mild vibration (well-dampened drone)
- `--shake 10` — moderate vibration
- `--shake 15+` — severe (poorly balanced props, no vibration dampening)

**Note on motion blur**: Camera shake does NOT add blur in our simulation. In reality,
vibration during exposure time causes slight blur. However, the IMX296 global shutter
camera with fast exposure in daylight (~1/500s) produces negligible blur from vibration
(sub-pixel). Shake as frame-to-frame jitter is the dominant real effect.

---

## Architecture

```
simple_simulator.py
    |
    |--- config.py          (MODE, CONNECTION_STR, camera intrinsics)
    |--- utils.py            (GeoTransformer: GPS <-> pixel conversion)
    |--- vision.py           (VisionSystem: camera + AI detection)
    |--- simulation.py       (SimulationEnvironment: map + drone view)
    |
    |--- MAVLink (SITL)      (telemetry in, velocity/position commands out)
    |--- OpenCV              (display, keyboard input)
```

### State Machine
Minimal: `INIT` -> `CONNECTING` -> `FLYING`. That's it. You fly manually. The simulator
just reads telemetry, runs CV, and estimates GPS. Centering (C/V) is the only automation.

### Key Methods
| Method | Purpose |
|--------|---------|
| `update_telemetry()` | Drain MAVLink, update position/attitude, apply GPS drift |
| `get_frame_and_detect()` | Get camera frame, apply shake, run CV (with throttle) |
| `calculate_target_gps(u,v)` | Pixel detection -> GPS estimate (with weighted averaging) |
| `send_velocity(vx,vy,vz)` | Body-frame velocity -> NED conversion -> MAVLink |
| `send_to_gps(lat,lon)` | Fly to GPS position (for C key centering) |
| `draw_hud()` | All HUD overlay rendering |

---

## Tunable Parameters

| Parameter | Default | Location | What it controls |
|-----------|---------|----------|-----------------|
| `servo_kp` | 0.005 | `__init__` | Visual servo responsiveness (pixel error -> m/s) |
| `servo_max_speed` | 2.0 | `__init__` | Max velocity from visual servo (m/s) |
| `servo_alpha` | 0.3 | `__init__` | EMA smoothing factor (0=sluggish, 1=raw/noisy) |
| `CENTRE_THRESHOLD_PX` | 30 | `__init__` | Pixels from centre for centre-snap |
| `fly_speed` | 3.0 | `__init__` | WASD manual flight speed (m/s) |
| `climb_rate` | 2.0 | `__init__` | R/F climb/descend speed (m/s) |
| `yaw_rate` | 30.0 | `__init__` | Q/E yaw rate (deg/s) |

---

## Example Test Scenarios

### Test 1: Baseline accuracy (no noise)
```bash
python simple_simulator.py
```
Fly over dummy, observe GPS estimation error converging. Best estimate should be < 1m.

### Test 2: Pi-realistic conditions
```bash
python simple_simulator.py --tflite --fps 4 --gps-drift 5 --shake 5
```
Full Pi simulation. GPS estimates will be noisier. Test C then V centering.

### Test 3: GPS centering vs visual servo comparison
```bash
python simple_simulator.py --gps-drift 5
```
1. Fly over dummy, collect detections
2. Press C — drone flies to GPS estimate (stops ~3-5m from target due to drift)
3. Press V — drone centres precisely using camera (sub-metre)

### Test 4: Visual servo under heavy shake
```bash
python simple_simulator.py --shake 15
```
Test the EMA filter's ability to smooth noisy detections. Increase `servo_alpha` if
too sluggish, decrease if too jittery.
