# main.py CLI Flags & Configuration Reference

Complete reference for every command-line flag and environment variable
accepted by `main.py`. Last updated: 2026-04-03.

---

## Recommended Configurations

### Simulation Testing
```bash
python main.py --speed 5 --lock-yaw --clean --sim-tilt
```
Standard simulation run: 5x speedup, consistent heading, clean detection folder,
realistic camera tilt from flight dynamics.

### Real Flight (Pi)
```bash
python main.py --headless --clean --center-verify
```
Headless mode for SSH/PuTTY. Clean detection folder. GPS-average the target
position after centering for higher accuracy before VERIFY.

### Stress Test (CV robustness)
```bash
python main.py --speed 5 --lock-yaw --clean --sim-tilt --blur 1.0 --shake 3
```
Tests whether the detection pipeline holds up under realistic motion blur
and camera vibration at speed.

### Dry Run (no flying)
```bash
python main.py --dry-run
```
No arming, no GPS, no Cube needed. Prints lawnmower waypoints, state machine
walkthrough, timing estimate, and saves `dry_run_pattern.jpg`.

### Debug GPS Estimation
```bash
python main.py --speed 5 --lock-yaw --clean --verbose-gps
```
Prints detailed GPS estimation math (pixel-to-GPS conversion) for every
detection frame. Useful for calibrating focal length and diagnosing offset errors.

### Beacon Redirect Test
```bash
python main.py --speed 5 --beacon-delay 300 --clean
```
After 300 seconds of search, auto-triggers PLB beacon redirect to Focus Area.

### NFZ Stress Test
```bash
python main.py --speed 5 --lock-yaw --clean --nfz-total-speed
```
Uses total-speed NFZ clamping (simpler but more aggressive) instead of the
default directional approach.

### SMART Detection (fewer false positives)
```bash
python main.py --speed 5 --lock-yaw --clean --smart-detect --conf 0.3
```
Requires multiple consecutive confirmed frames before investigating a target.
Lower confidence threshold compensates for the stricter confirmation.

### Spiral Pattern (Zian's planner)
```bash
python main.py --speed 5 --spiral --clean
```
Uses Zian's perimeter spiral pattern instead of the default lawnmower.

---

## All Flags Reference

### 1. Mission Control

| Flag | Default | Platform | Description |
|------|---------|----------|-------------|
| `--dry-run` | off | Both | No arming, no flying, no GPS. Visualize pattern only. |
| `--clean` | off | Both | Wipe `mission_detections/` folder at mission start. |
| `--headless` | auto | Both | No cv2 windows. Auto-enabled on Pi when `$DISPLAY` is empty. |

#### `--dry-run`
- **What it does**: Generates the search pattern (lawnmower or spiral), prints all
  waypoints with GPS coordinates, calculates transit distance and estimated flight
  time, shows the state machine progression, and saves a visualization to
  `dry_run_pattern.jpg`. No Cube connection, no arming, no GPS fix required.
- **When to use**: Before every flight to verify the search pattern covers the area
  correctly. Also useful for checking `--alt` effects on strip spacing.
- **Example**: `python main.py --dry-run --alt 20`

#### `--clean`
- **What it does**: Deletes the entire `mission_detections/` directory at startup
  and recreates it empty. Without this flag, detection images from previous runs
  accumulate.
- **When to use**: At the start of every new mission to avoid confusion with old data.
- **Example**: `python main.py --clean`

#### `--headless`
- **What it does**: Skips all `cv2.imshow()`, `cv2.namedWindow()`, and
  `cv2.waitKey()` calls. All UI is served through the browser stream at
  `http://localhost:8090/`. Terminal keyboard input still works via PuTTY/SSH.
  Auto-detected on Linux when `$DISPLAY` is empty (typical Pi over SSH).
- **When to use**: Always on Pi. On laptop only if you prefer browser-only UI.
- **Example**: `python main.py --headless`

---

### 2. Speed & Altitude

| Flag | Default | Platform | Description |
|------|---------|----------|-------------|
| `--speed <factor>` | `1` | SIM only | SITL simulation speedup multiplier. |
| `--alt <meters>` | `35.0` | Both | Override search altitude (capped at 50m). |

#### `--speed <factor>`
- **What it does**: Sets `config.SIM_SPEED` which controls SITL time acceleration.
  Higher values make the simulation run faster. Only affects SIMULATION mode;
  ignored in REAL mode.
- **When to use**: Always in simulation to avoid waiting. `5` is a good default.
  Use `1` for real-time debugging.
- **Example**: `python main.py --speed 10`

#### `--alt <meters>`
- **What it does**: Overrides `config.TARGET_ALT` (search altitude). Affects strip
  spacing in the lawnmower pattern (higher altitude = wider footprint = fewer strips).
  Capped at 50m by config.py safety check.
- **When to use**: Lower for better detection (20-25m), higher for faster coverage
  (35-50m). First flights should use `--alt 20` for safety.
- **Example**: `python main.py --alt 25`

---

### 3. Detection

| Flag | Default | Platform | Description |
|------|---------|----------|-------------|
| `--model <path>` | `best.tflite` | Both | TFLite model file path. |
| `--conf <threshold>` | `0.2` | Both | Minimum YOLO confidence threshold. |
| `--smart-detect` | off | Both | Require consecutive confirmed frames before investigating. |

#### `--model <path>`
- **What it does**: Overrides the TFLite model file loaded by `VisionSystem`.
  Allows swapping models without copying files to `best.tflite`.
- **When to use**: A/B testing models on flight day, or benchmarking different
  training runs.
- **Example**: `python main.py --model cv_models/sar_v2_1088/best.tflite`
- **Example**: `python main.py --model models/human.tflite`

#### `--conf <threshold>`
- **What it does**: Overrides `config.CONFIDENCE_THRESHOLD`. Detections below this
  confidence are ignored. Lower values catch more targets but increase false
  positives. The operator filters false positives at VERIFY.
- **When to use**: Lower (0.1-0.2) for maximum sensitivity. Higher (0.4-0.6) to
  reduce false positive interruptions.
- **Example**: `python main.py --conf 0.3`

#### `--smart-detect`
- **What it does**: Enables consecutive-frame confirmation. Instead of immediately
  investigating every detection, requires `config.DETECT_CONFIRM_FRAMES` (default 3)
  consecutive frames with a valid detection before queuing. Reduces false positives
  from single-frame glitches.
- **When to use**: When false positive rate is high (e.g., textured terrain, shadows).
  Combine with lower `--conf` to compensate for the stricter filter.
- **Example**: `python main.py --smart-detect --conf 0.15`

---

### 4. Navigation

| Flag | Default | Platform | Description |
|------|---------|----------|-------------|
| `--lock-yaw` | off | SIM only | Maintain search heading throughout sweep. |
| `--center-verify` | off | Both | GPS-average target position after centering. |
| `--beacon-delay <s>` | `0` (off) | Both | Auto-trigger PLB redirect after N seconds. |
| `--spiral` | off | Both | Use Zian's perimeter spiral instead of lawnmower. |
| `--transit <file>` | `flight_plans/transit.json` | Both | Transit waypoints JSON file. |

#### `--lock-yaw`
- **What it does**: Sets `config.LOCK_YAW = True`. During SEARCH state, the drone
  maintains a fixed yaw heading (the heading at the start of the first search leg)
  instead of rotating to face each waypoint. Keeps the camera footprint consistent
  across all passes.
- **When to use**: In simulation to test consistent coverage. In real flight if the
  camera is fixed-forward and you want predictable footprint overlap.
- **Example**: `python main.py --lock-yaw`

#### `--center-verify`
- **What it does**: After reaching the target in CENTERING state (within 1.0m), starts
  a GPS averaging window. Collects multiple GPS position samples and averages them
  before transitioning to VERIFY/DESCEND. Improves target position accuracy by
  averaging out GPS noise.
- **When to use**: In real flights where GPS drift is significant. Adds a few seconds
  to the centering phase but gives a more accurate target fix.
- **Example**: `python main.py --center-verify`

#### `--beacon-delay <seconds>`
- **What it does**: Sets `config.BEACON_DELAY`. After this many seconds of active
  searching, auto-triggers a PLB (Personal Locator Beacon) redirect to the Focus
  Area polygon. `0` = disabled (default).
- **When to use**: To simulate a mid-mission PLB activation that redirects the search
  to a smaller Focus Area.
- **Example**: `python main.py --beacon-delay 300` (redirect after 5 minutes)

#### `--spiral`
- **What it does**: Replaces the default lawnmower search pattern with Zian's
  perimeter spiral planner. The spiral starts from the polygon perimeter and works
  inward with the same strip spacing as lawnmower.
- **When to use**: Testing alternative coverage patterns. Falls back to a standalone
  reimplementation if Zian's planner module is not available.
- **Example**: `python main.py --spiral --dry-run`

#### `--transit <file>`
- **What it does**: Specifies a JSON file containing transit waypoints for the
  PRE_WAYPOINTS state (waypoints flown before entering the search area). Default
  is `flight_plans/transit.json`.
- **When to use**: When you have a specific ingress/egress route to follow (e.g.,
  avoiding obstacles or restricted zones between takeoff and search area).
- **Example**: `python main.py --transit flight_plans/custom_transit.json`

---

### 5. Camera Simulation & Tilt Compensation

| Flag | Default | Platform | Description |
|------|---------|----------|-------------|
| `--sim-tilt` | off | SIM only | Camera tilts in flight direction (pitch + roll from SITL). |
| `--compensate-tilt` | off | Both | Ray-trace GPS estimates through attitude rotation matrix. |
| `--sim-pitch` | off | SIM only | Camera pitch offset during forward flight (legacy). |
| `--sim-roll <deg>` | `0.0` | SIM only | Random roll oscillation in degrees. |
| `--blur <factor>` | `0.0` | SIM only | Motion blur proportional to speed. |
| `--shake <pixels>` | `0` | SIM only | Random pixel offset per frame (vibration). |

#### `--sim-tilt`
- **What it does**: Uses actual roll and pitch angles from SITL telemetry to shift
  and rotate the simulated camera view. This is the combined replacement for the
  older `--sim-pitch` and `--sim-roll` flags. Produces realistic camera displacement
  that matches flight dynamics.
- **When to use**: Standard simulation testing. Exposes whether the detection
  pipeline handles tilted frames. In simulation, also implicitly enables
  `--compensate-tilt` so GPS estimates are corrected for the simulated tilt.
- **Example**: `python main.py --sim-tilt`

#### `--compensate-tilt`
- **What it does**: Applies attitude-compensated GPS estimation. For each detection,
  constructs a ray in the camera frame, rotates it into the world frame using the
  full rotation matrix R = Rz(yaw) * Ry(-pitch) * Rx(-roll) built from the
  ATTITUDE MAVLink message, and intersects it with the ground plane. This is the
  exact mathematical inverse of the camera model, reducing tilt-induced position
  error from 6.2m to ~0.3m at 35m altitude and 10 deg pitch. The residual error
  is limited only by IMU angular noise (~0.5 deg).
- **When to use**: In real flights and passive observation (`passive_watch.py`).
  In simulation, `--sim-tilt` enables this automatically. Use `--compensate-tilt`
  standalone when the camera is physically tilted by aircraft motion (real flight)
  rather than simulated tilt.
- **Activation threshold**: Only activates when pitch or roll exceeds 0.02 rad
  (~1.1 deg) and altitude > 1m. During hover, the correction is a no-op.
- **Verification**: Tested with 1440 automated cases (4 altitudes x 4 pitch x
  3 roll x 5 yaw x 6 target positions), all producing errors < 0.01m.
- **Example**: `python main.py --compensate-tilt`
- **Example**: `python main.py --sim-tilt` (enables both tilt simulation + compensation)

#### `--sim-pitch`
- **What it does**: Simulates camera pitch offset during forward flight. Legacy flag;
  `--sim-tilt` is preferred as it uses real SITL attitude data rather than a simple
  model.
- **When to use**: Only if you want pitch-only simulation without roll.
- **Example**: `python main.py --sim-pitch`

#### `--sim-roll <degrees>`
- **What it does**: Adds random roll oscillation to the simulated camera view. Each
  frame gets a random rotation between `-deg` and `+deg`. Simulates wind-induced
  roll during flight.
- **When to use**: Stress-testing detection robustness under roll disturbance.
- **Example**: `python main.py --sim-roll 5`

#### `--blur <factor>`
- **What it does**: Applies directional motion blur to the simulated camera frame,
  proportional to ground speed. Factor `1.0` is calibrated for a realistic 5ms
  exposure time. Higher values exaggerate the blur for stress testing. The blur
  kernel size is calculated from speed, GSD (ground sample distance), and the factor.
- **When to use**: Testing whether the model detects targets under motion blur.
  `1.0` = realistic, `2.0` = stress test, `0.5` = mild.
- **Example**: `python main.py --blur 1.5`

#### `--shake <pixels>`
- **What it does**: Adds a random pixel offset (jitter) to each frame in both X and
  Y directions, uniformly distributed between `-N` and `+N` pixels. Simulates
  high-frequency vibration from motors/props.
- **When to use**: Testing detection robustness under vibration. Values of 2-5 are
  realistic; 10+ is extreme.
- **Example**: `python main.py --shake 3`

---

### 6. Geofence (NFZ)

| Flag | Default | Platform | Description |
|------|---------|----------|-------------|
| `--no-nfz` | off | Both | Disable SSSI geofence entirely. |
| `--nfz-total-speed` | off | Both | Use total-speed NFZ clamping instead of directional. |

#### `--no-nfz`
- **What it does**: Disables the SSSI (Site of Special Scientific Interest) geofence
  completely. No speed clamping, no repulsive push, no waypoint filtering, no
  hard boundary enforcement. The NFZ polygon is still loaded but ignored.
- **When to use**: Testing in areas without an NFZ, or debugging non-NFZ issues
  without geofence interference.
- **Example**: `python main.py --no-nfz`

#### `--nfz-total-speed`
- **What it does**: Switches NFZ speed clamping from directional (default) to
  total-speed mode. **Directional (default)**: only the velocity component toward
  the NFZ boundary is clamped; tangential movement is unrestricted. The drone can
  fly fast parallel to the boundary. **Total-speed**: the entire ground speed is
  clamped regardless of direction. Simpler but more aggressive; the drone slows
  down even when flying parallel to the NFZ.
- **When to use**: If directional clamping causes unexpected behavior, or for
  maximum safety near the NFZ boundary.
- **Example**: `python main.py --nfz-total-speed`

---

### 7. Stream Server

| Flag | Default | Platform | Description |
|------|---------|----------|-------------|
| `--no-stream` | off | Both | Disable MJPEG stream server entirely. |
| `--stream-scale <factor>` | `640x480` | Both | Scale stream resolution relative to camera. |
| `--stream-quality <1-100>` | `50` | Both | JPEG compression quality for stream. |
| `--stream-fps <fps>` | `10` | Both | Target stream frame rate. |

#### `--no-stream`
- **What it does**: Disables the MJPEG stream server on port 8090 entirely. The
  mission runs without any web UI. Terminal keyboard input still works.
- **When to use**: If port 8090 is in use, or you don't need the browser dashboard.
- **Example**: `python main.py --no-stream`

#### `--stream-scale <factor>`
- **What it does**: Scales the stream resolution relative to the camera resolution
  (`config.IMAGE_W` x `config.IMAGE_H`). Factor `0.5` with a 1456x1088 camera
  produces a 728x544 stream. Factor `1.0` = full resolution (higher bandwidth).
  Default stream size is 640x480 (independent of camera resolution) unless this
  flag is set.
- **When to use**: Reduce for slow WiFi connections (Pi to laptop). Increase for
  sharper stream when bandwidth allows.
- **Example**: `python main.py --stream-scale 0.5`

#### `--stream-quality <1-100>`
- **What it does**: Sets JPEG compression quality for the MJPEG stream. Lower values
  reduce bandwidth but introduce compression artifacts. Default `50` is a good
  WiFi-friendly balance.
- **When to use**: Lower (30-40) on unreliable WiFi. Higher (70-90) on LAN or
  localhost.
- **Example**: `python main.py --stream-quality 70`

#### `--stream-fps <fps>`
- **What it does**: Sets the target frame rate for the MJPEG stream. Lower values
  reduce bandwidth. The actual FPS may be lower if inference is slower than the
  target.
- **When to use**: Lower (5) to save bandwidth over slow links. Higher (15-20) for
  smoother video on fast connections.
- **Example**: `python main.py --stream-fps 15`

---

### 8. Debug

| Flag | Default | Platform | Description |
|------|---------|----------|-------------|
| `--verbose-gps` | off | Both | Print detailed GPS estimation math for every detection. |

#### `--verbose-gps`
- **What it does**: Enables verbose logging of the pixel-to-GPS conversion for every
  detection frame. Prints the raw pixel coordinates, normalised values, altitude,
  heading, focal length, and resulting GPS estimate. Useful for diagnosing GPS
  estimation accuracy and calibrating focal length.
- **When to use**: When GPS estimates are consistently offset and you need to trace
  the math.
- **Example**: `python main.py --verbose-gps`

---

## Environment Variables

These are read by `config.py` at import time, before any CLI flags are parsed.

| Variable | Default | Description |
|----------|---------|-------------|
| `DRONE_MODE` | `SIMULATION` | `SIMULATION` or `REAL`. Controls camera source and connection auto-detection. |
| `DRONE_CONN` | auto-detected | Override connection string (e.g., `tcp:127.0.0.1:5762`, `udpin:0.0.0.0:14550`). |
| `DRONE_BAUD` | `921600` | Serial baud rate (only used for direct serial connections). |

### `DRONE_MODE`
- **`SIMULATION`** (default): Uses `map.jpg` + simulated camera view. Connects to
  SITL on localhost. Interactive polygon drawing on the map.
- **`REAL`**: Uses real camera (Pi camera or webcam). Connects to Cube via mavproxy
  UDP bridge. Loads search area from `flight_plans/search_area.json` or
  `config.SEARCH_AREA_GPS`.

```bash
# Windows (cmd)
set DRONE_MODE=REAL
python main.py

# Linux / Pi
export DRONE_MODE=REAL
python main.py
```

### `DRONE_CONN`
- **Auto-detection order**: (1) `DRONE_CONN` env var, (2) Pi serial port present
  (`/dev/ttyAMA0` etc.) -> `udpin:0.0.0.0:14550`, (3) WSL -> gateway IP via TCP,
  (4) fallback `tcp:127.0.0.1:5762`.
- Override when auto-detection picks the wrong target.

```bash
export DRONE_CONN=tcp:192.168.1.3:5762
python main.py
```

### `DRONE_BAUD`
- Only relevant for direct serial connections (not used with mavproxy UDP bridge).
- Default 921600 matches Cube Orange configuration.

---

## Config.py Constants (tunable, not CLI flags)

These are set in `config.py` and affect mission behavior. They can only be changed
by editing the file (except where CLI flags override them, noted above).

| Constant | Value | Overridden by |
|----------|-------|---------------|
| `TARGET_ALT` | `35.0` m | `--alt` |
| `VERIFY_ALT` | `15.0` m | -- |
| `CONFIDENCE_THRESHOLD` | `0.2` | `--conf` |
| `DETECT_CONFIRM_FRAMES` | `3` | -- (affects `--smart-detect`) |
| `DETECT_LOCK_RADIUS_M` | `5.0` m | -- |
| `SEARCH_SPEED_MPS` | `10.0` m/s | -- |
| `TRANSIT_SPEED_MPS` | `15.0` m/s | -- |
| `FOCUS_SEARCH_SPEED_MPS` | `5.0` m/s | -- |
| `NFZ_HARD_BOUNDARY_M` | `3.0` m | -- |
| `NFZ_SOFT_BOUNDARY_M` | `8.0` m | -- |
| `NFZ_WAYPOINT_BUFFER_M` | `30.0` m | -- |
| `NFZ_SLOW_ZONE_M` | `20.0` m | -- |
| `NFZ_SCALAR_ZERO_M` | `2.0` m | -- |
| `NFZ_PUSH_SPEED_MPS` | `5.0` m/s | -- |
| `IMAGE_W` | `1456` px | -- |
| `IMAGE_H` | `1088` px | -- |
| `SENSOR_WIDTH_MM` | `5.02` mm | -- |
| `FOCAL_LENGTH_MM` | `5.46` mm | -- |
| `SIM_SPEED` | `1` | `--speed` |
| `BEACON_DELAY` | `0` | `--beacon-delay` |
| `LOCK_YAW` | `False` | `--lock-yaw` |
| `REAL_CANVAS_SIZE` | `4800` px | -- |
| `REJECTED_TARGET_RADIUS_M` | `5.0` m | -- |
| `MAX_RESCAN_PASSES` | `3` | -- |
| `SERVO_CHANNEL` | `9` | -- |

---

## Quick Reference Card

```
MISSION:    --dry-run  --clean  --headless
SPEED/ALT:  --speed <N>  --alt <m>
DETECTION:  --model <path>  --conf <0-1>  --smart-detect
NAVIGATION: --lock-yaw  --center-verify  --beacon-delay <s>  --spiral  --transit <file>
CAMERA SIM: --sim-tilt  --compensate-tilt  --sim-pitch  --sim-roll <deg>  --blur <factor>  --shake <px>
GEOFENCE:   --no-nfz  --nfz-total-speed
STREAM:     --no-stream  --stream-scale <f>  --stream-quality <1-100>  --stream-fps <N>
DEBUG:      --verbose-gps
ENV VARS:   DRONE_MODE=SIMULATION|REAL  DRONE_CONN=tcp:IP:PORT  DRONE_BAUD=921600
```

**Total: 23 CLI flags + 3 environment variables.**
