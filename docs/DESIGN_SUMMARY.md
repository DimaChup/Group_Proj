# Design Decisions -- SAR Drone Software

## Overview

This document covers every significant design decision in the SAR drone autonomous
search-and-rescue system, built as a team of five for the University of Bristol MSc
module AENGM0074. The drone takes off, flies a lawnmower search pattern over a
designated survey area, uses onboard AI (YOLOv8n on a Raspberry Pi 5) to detect a
casualty dummy, presents detections to a ground-station operator for confirmation,
delivers a payload near the confirmed target, and returns home. The survey area sits
adjacent to a Site of Special Scientific Interest (SSSI) designated as a no-fly zone,
which shapes many of the design choices below.

---

## 1. Architecture

### 1.1 File Map

| File | Responsibility |
|------|---------------|
| `config.py` | Every tunable parameter: altitudes, speeds, camera, NFZ, connection strings |
| `states.py` | State enum (`SEARCH`, `VERIFY`, `LANDING`, etc.) |
| `vision.py` | Camera + AI detection. Dual backend (Ultralytics on laptop, TFLite on Pi). Single interface: `detect_in_image(frame) -> (found, x, y, conf)` |
| `planning.py` | Lawnmower search pattern generator. Independent module, returns `[(lat, lon), ...]` |
| `utils.py` | Geo math: GPS-to-pixel and pixel-to-GPS conversion (`GeoTransformer`) |
| `navigation.py` | MAVLink command abstraction: goto, set_speed, send_velocity, land, arm |
| `geofence.py` | NFZ boundary distance, repulsive offset computation, inner polygon geometry |
| `state_machine.py` | All state handler methods (mixin class inherited by main mission) |
| `main.py` | Mission orchestrator: connects modules, runs main loop, dispatches states |
| `simple_simulator.py` | Interactive keyboard-flight simulator with CV + GPS estimation (laptop only) |
| `pi_flight.py` | Web-based ground station: MJPEG stream + browser dashboard (headless on Pi) |
| `passive_watch.py` | Passive camera observer -- detects and logs, sends zero commands |

**Key principle:** `vision.py` is the only file that touches CV/AI. Everything else
calls `detect_in_image()`. The model, preprocessing, or backend can change without
touching any other file.

### 1.2 State Machine Overview

The mission is governed by a finite state machine. At any instant the drone is in
exactly one state. A dispatch dictionary maps each `State` enum to a handler method
called once per loop iteration.

```
                        +-- MANUAL OVERRIDE (M key, any state) --+
                        |  MANUAL -> RETURN_FROM_MANUAL -> resume |
                        +----------------------------------------+

 INIT -> CONNECTING -> ARMING -> TAKEOFF
                                    |
                    (transit file?)--+-- (no transit)
                    |                |
               PRE_WAYPOINTS    TRANSIT_TO_SEARCH
                    |                |
                    +-> TRANSIT_TO_SEARCH
                              |
                           SEARCH  <-- rescan (drop alt) <--+
                           /    \                            |
                  detection    all WPs done, no confirm -----+
                  queued         (pass < MAX_RESCAN_PASSES)
                     |
                  CENTERING (60s timeout -> SEARCH)
                     |  dist < 1m
                  VERIFY  (120s timeout -> reject)
                  / | \
           Y    N/I  timeout
           |     |
      APPROACH  queue pop -> CENTERING
           |    or RETURN_TO_SEARCH -> SEARCH
      HOVER_TARGET (servo release, 15s)
           |
      RETURN_TRANSIT -> RETURN_HOME -> LANDING -> DONE
```

### 1.3 Why a State Machine

| Property | Benefit |
|----------|---------|
| **Deterministic** | Exactly one state at all times. Transition is a pure function of (state, inputs, operator commands). Auditable and testable. |
| **Timeout safety** | Every blocking state has a wall-clock timeout. No state can hang indefinitely -- it falls back to a safe successor. |
| **Separation of concerns** | Detection in `vision.py`, path planning in `planning.py`, navigation in `navigation.py`, geo-transforms in `utils.py`. The state machine orchestrates without duplicating. |
| **Operator override** | M key (software) or RC transmitter switch (hardware) can interrupt any state. The machine records where it was and returns after override ends. |

---

## 2. Search Strategy

### 2.1 Lawnmower Pattern

The system uses a boustrophedon (lawnmower) scan pattern. Alternatives considered:

| Pattern | Coverage guarantee | Why rejected |
|---------|-------------------|-------------|
| **Lawnmower (chosen)** | Complete -- every cell visited | Standard in SAR literature (JSAR) |
| Expanding spiral | Biased toward centre; edges under-covered | No prior info on casualty location |
| Sector search | Requires known last-seen point | Not applicable |

The planner handles arbitrary polygons (including concave boundaries) by rasterising
with `cv2.fillPoly` onto a binary mask, then reading non-zero pixel runs from each row.
No explicit polygon clipping needed.

### 2.2 Scan Angle Optimisation

The optimal scan angle minimises the number of perpendicular scan lines. The planner
uses `cv2.minAreaRect` to find the minimum-area bounding rectangle and aligns scan lines
with the longest edge. A comprehensive analysis across 216 configurations (6 altitudes
x 36 angles) confirmed the optimal angle for the AENGM0074 polygon is 65-75 degrees,
consistent with its elongated NE-SW geometry.

### 2.3 Diagonal Realignment (the 53-Degree Trick)

The camera produces a 1456 x 1088 frame. The diagonal is longer than either side:

```
diagonal = sqrt(1456^2 + 1088^2) = 1818 pixels
```

By yawing the drone so the camera diagonal is perpendicular to the flight direction, the
effective swath increases from 1088 px (height) to 1818 px (diagonal) -- a factor of
**1.67x**, giving 67% more ground coverage per scan line at zero extra flight cost.

```
yaw_offset = atan(IMAGE_W / IMAGE_H) = atan(1456 / 1088) = 53.2 degrees
```

Configurable via `DIAGONAL_YAW_OFFSET_DEG` in `config.py`. Currently set to `0`
(disabled) but flight-ready. Set to `None` for auto-compute.

### 2.4 Swath Width and Overlap

Ground footprint width at altitude `h`:

```
ground_width = (SENSOR_WIDTH_MM * h) / FOCAL_LENGTH_MM
             = (5.02 * h) / 5.46  [metres]
```

At `TARGET_ALT = 35 m`: ground width ~ 32.2 m. The scan line spacing uses the image
height dimension (perpendicular to flight) with **0% explicit overlap**, because the
diagonal realignment already provides the 67% coverage bonus. A 1/3 swath margin is
maintained from polygon edges.

### 2.5 Altitude Strategy: Start High, Drop on Rescan

If the first pass finds nothing, the system drops altitude and rescans:

| Parameter | Value | `config.py` name |
|-----------|-------|-------------------|
| Max rescan passes | 3 | `MAX_RESCAN_PASSES` |
| Altitude factor per pass | 0.8 (20% drop) | `RESCAN_ALT_FACTOR` |
| Altitude floor | 15.0 m | `RESCAN_ALT_FLOOR_M` |

Altitude progression from 35 m default:

| Pass | Altitude | Speed | Ground width | Effect |
|------|----------|-------|-------------|--------|
| 1 (initial) | 35.0 m | 8.0 m/s | ~32.2 m | Fewest scan lines, fastest |
| 2 (rescan 1) | 28.0 m | 7.1 m/s | ~25.7 m | More lines, better GSD |
| 3 (rescan 2) | 22.4 m | 6.3 m/s | ~20.6 m | Most lines, best detection |

Each lower pass narrows the footprint (more scan lines) but increases target pixel size
by ~60%, catching targets missed due to lighting, blur, or occlusion.

### 2.6 Speed vs Altitude

Search speed varies linearly with altitude (`speed_for_altitude()` in `config.py`):

| Parameter | Value |
|-----------|-------|
| `SPEED_ALT_LOW` | 20 m |
| `SPEED_ALT_HIGH` | 50 m |
| `SPEED_AT_LOW` | 6.0 m/s |
| `SPEED_AT_HIGH` | 10.0 m/s |

**Why linear:** At lower altitudes, the target subtends more pixels but motion blur is
proportionally worse (higher angular rate). Slower speeds preserve frame quality. At
higher altitudes, blur is less severe, so faster speeds are acceptable. At 35 m default:
8.0 m/s.

### 2.7 Focus Area (PLB Beacon Redirect)

When a Personal Locator Beacon signal is received (B key or `--beacon-delay N`), the
search redirects to a smaller polygon:

1. Load focus area from `flight_plans/focus_area.json` (re-read each time, allows
   mid-flight coordinate updates from ground station)
2. Regenerate lawnmower pattern for the smaller polygon
3. Reset waypoint index and rescan counter
4. Drop speed to `FOCUS_SEARCH_SPEED_MPS = 5.0 m/s`
5. Preserve all rejected targets from the broad search

Fallback chain: JSON file -> drawn polygon (`config.FOCUS_AREA_GPS`) -> KML Focus Area.

---

## 3. NFZ Protection

The survey area is adjacent to a SSSI no-fly zone. A single point of failure in
boundary enforcement could cause an airspace violation, so the system uses three
independent protection layers.

### 3.1 Defence in Depth

| Layer | Type | Runs on | What it catches |
|-------|------|---------|----------------|
| **Speed cap** (scalar field) | Software | Pi | Prevents high-speed overshoot during waypoint following |
| **Repulsive push** (vector field) | Software | Pi | Deflects drone if speed cap alone is insufficient (wind gust, GPS jump) |
| **Cube firmware geofence** | Hardware | Flight controller | Triggers LOITER/RTL if software layers fail entirely (crash, hang, lost link) |

If the Pi crashes, the Cube geofence still works. If the firmware geofence is
misconfigured, the software layers still enforce the boundary.

### 3.2 The "Carrot" Concept

The name "carrot" comes from "carrot on a stick." ArduCopter's GUIDED mode autopilot
chases a target waypoint -- that waypoint is the carrot dangled in front of the drone.
We do not modify the waypoint position or direction (that would be a "stick" approach,
physically redirecting the drone). Instead, we cap how fast the autopilot is allowed to
chase the carrot using `MAV_CMD_DO_CHANGE_SPEED`. The autopilot still handles all
trajectory planning, path smoothing, deceleration curves, and wind compensation
internally. We only adjust the speed ceiling.

### 3.3 Layer 1: Speed Cap (Scalar Field)

Within `NFZ_SLOW_ZONE_M = 20 m` of the SSSI boundary, a `MAV_CMD_DO_CHANGE_SPEED`
command linearly reduces the maximum ground speed:

```
speed(d) = NFZ_MIN_SPEED_MPS + (d / NFZ_SLOW_ZONE_M) * (NFZ_ZONE_MAX_SPEED_MPS - NFZ_MIN_SPEED_MPS)
         = 0.3 + 0.135 * d   [m/s]
```

| Distance from NFZ | Speed limit |
|-------------------|-------------|
| 20 m (entering zone) | 3.0 m/s |
| 10 m | 1.65 m/s |
| 0 m (at boundary) | 0.3 m/s |
| > 20 m | Normal (6-10 m/s) |

**Why 20 m zone width:** The drone's maximum search speed is 10 m/s (at 50 m altitude).
At 10 m/s, stopping distance is approximately 5-8 m depending on wind conditions. A 20 m
zone provides roughly 2x safety margin over the worst-case stopping distance. It also
gives the drone sufficient distance to decelerate smoothly -- a gentle linear ramp over
20 m rather than a hard wall that would cause abrupt braking or overshoot.

**Why 3 m/s at the outer edge:** 3 m/s is the minimum useful search speed. Slower than
this and the drone produces too many scan lines for the same area, wasting battery and
flight time. Below 3 m/s, the drone is essentially loitering rather than searching.

**Why 0.3 m/s at the boundary:** 0.3 m/s is effectively hovering -- barely perceptible
movement. If the drone somehow reaches the actual NFZ boundary at 0.3 m/s, it has almost
no momentum to cross it. The autopilot can stop from 0.3 m/s in well under a metre, even
in moderate wind.

**Why `DO_CHANGE_SPEED` and not velocity commands:** `DO_CHANGE_SPEED` modifies the
autopilot's own speed limit. The autopilot continues handling path smoothing,
deceleration, and wind compensation internally. The companion computer only adjusts the
ceiling. Velocity commands (`SET_POSITION_TARGET_LOCAL_NED`) fight the position
controller, causing oscillation -- this was tested and rejected (see 3.5).

**Why linear:** Simple, predictable, monotonic. Two tunable parameters control the
endpoints. No discontinuities or inflection points.

### 3.4 Layer 2: Repulsive Push (Vector Field)

A virtual inner polygon is offset inward by `NFZ_INNER_OFFSET_M = 20 m` from the SSSI
boundary. When the drone is within `NFZ_INNER_RANGE_M = 23 m` of this inner polygon, a
constant-magnitude velocity command pushes it away at `NFZ_PUSH_SPEED_MPS = 3.0 m/s`.

Effective activation zone relative to the actual NFZ boundary:

- **Outside NFZ, within 3 m:** push active (pre-emptive, before crossing)
- **Inside NFZ, up to 20 m deep:** push active (escape)
- **More than 3 m outside:** inactive (normal flight)

The 3 m overlap beyond the boundary provides a safety margin against GPS error and
control lag.

**Why 20 m inner polygon offset:** The offset places the repulsion source deep inside
the NFZ so the resulting push field extends 3 m outside the actual boundary. This means
the drone feels the push *before* it reaches the boundary. If the offset were smaller
(e.g., 3 m), the push would only activate when the drone is already very close to or
inside the boundary -- too late if it is approaching at any meaningful speed.

**Why constant magnitude (not gradient):** A gradient force that weakens near the
boundary would let a fast-moving drone slip through. If the drone is within the danger
zone (23 m from the inner polygon, i.e., 3 m outside the actual NFZ boundary), the push
must be strong enough to overcome any residual velocity. A constant 3.0 m/s push always
exceeds the near-zero speed cap at the boundary (0.3 m/s), guaranteeing escape. One
tunable parameter instead of a force curve.

**Why the push is kept even though the carrot already slows the drone:** Defence in
depth. The speed cap prevents fast approach; the push prevents crossing even at low
speed. Belt and suspenders. The push is constant (not speed-dependent) so it works even
if `DO_CHANGE_SPEED` fails to take effect, or if the drone is blown toward the boundary
by wind. The speed cap is the primary defence; the push is the last resort.

Push direction: unit vector from the closest point on the SSSI polygon to the drone,
computed via line-segment projection in pixel space, converted back to GPS offsets.

### 3.5 Design Evolution: Three Approaches Tested

Three approaches were implemented and tested in SITL simulation before arriving at the
current design:

**Approach 1: `--nfz-repel` (velocity commands pushing away from boundary)**

Sent velocity commands (vx, vy) pushing the drone away from the NFZ boundary using an
inverse-distance potential field. Problem: ArduCopter's GUIDED mode position controller
is simultaneously trying to fly TO the next waypoint. Our velocity command says "go left"
while the autopilot says "go right" -- they fight each other, causing oscillation and
unpredictable jitter at the buffer boundary.

**Approach 2: `--nfz-slow` (velocity toward waypoint at capped speed)**

We computed the direction to the next waypoint ourselves and sent velocity commands at
reduced speed. Problem: we were duplicating what ArduCopter already does (trajectory
planning), but worse. Our 20 Hz velocity commands could not match ArduCopter's smooth
internal trajectory planner, resulting in jittery movement and overshoots at turns. The
velocity was recomputed each cycle with noisy GPS, compounding the jitter.

**Approach 3: `--nfz-carrot` (chosen) -- `DO_CHANGE_SPEED` + inner polygon push**

We tell ArduCopter "your max speed is now X m/s" via `DO_CHANGE_SPEED`. ArduCopter
handles ALL direction and trajectory planning. We never fight the autopilot. The result
is smooth, predictable flight with the same path the autopilot would fly without any
NFZ system -- just slower near the boundary. The inner polygon push only activates as a
last resort (within 3 m of the boundary) and is additive -- it pushes in addition to
normal navigation, not instead of it.

| Approach | Method | Result |
|----------|--------|--------|
| `--nfz-repel` | Velocity commands away from boundary | Oscillation (fought position controller) |
| `--nfz-slow` | Velocity toward waypoint at capped speed | Jittery (duplicated autopilot logic, noisy GPS) |
| **`--nfz-carrot`** | `DO_CHANGE_SPEED` + inner push | Smooth, predictable, no oscillation |

`NFZ_CARROT` separates concerns: the scalar field handles gradual slowdown (letting the
autopilot handle direction), and the vector field handles emergency deflection (only
within 3 m of the boundary where the speed cap alone might be insufficient).

### 3.6 Manual Mode and NFZ

| Geofence layer | Effect in software MANUAL (M key) |
|----------------|----------------------------------|
| Speed cap | No effect (WASD velocity commands bypass the autopilot speed limit) |
| Repulsive push | Active (adds to WASD commands) |
| Cube firmware geofence | Active (independent of all software) |

On real hardware, switching to STABILIZE/LOITER on the RC transmitter disconnects the
companion computer entirely. The pilot has full stick authority; only the firmware
geofence remains.

### 3.7 Auto-MANUAL on NFZ Entry

If the drone's GPS falls inside the SSSI (or within 3 m), the software immediately:
halts the drone (`send_velocity(0,0,0)`), saves the departure state, switches to MANUAL,
and prints a warning. The operator flies out manually, assisted by the repulsive push.
On real hardware, the Cube firmware geofence (LOITER/RTL) would typically intervene
first.

---

## 4. Detection and Target Management

### 4.1 AI Model

YOLOv8n (nano) was chosen for the Pi 5's CPU constraints:

| Variant | TFLite size | Pi 5 inference | Why |
|---------|------------|----------------|-----|
| **YOLOv8n (chosen)** | 3.2 MB | 206.5 ms (4.8 FPS) | Fast enough for search at 6-10 m/s |
| YOLOv8s | ~22 MB | ~400 ms (2.5 FPS) | Higher accuracy but halves frame rate |
| YOLOv8m | ~50 MB | ~800 ms (1.2 FPS) | Too slow for real-time |

At 4.8 FPS and 6 m/s, the drone moves 1.25 m between frames. The ground footprint at
35 m is ~47 m x 35 m, so a target appears in many consecutive frames.

### 4.2 Detection Queue (FIFO)

Detections are appended to a FIFO queue and investigated in order. The drone does not
immediately divert to a new detection -- it finishes the current investigation first.

**Why not immediate divert:** Two targets visible in alternating frames cause the drone
to bounce between them indefinitely.

**Why not priority (highest confidence first):** Confidence is not a reliable indicator
of validity. The same object scores differently depending on viewing angle, lighting, and
distance. A target detected at 0.3 from the edge may score 0.9 once the drone is
overhead. Prioritising by confidence would deprioritise valid oblique detections.

**Queue management:** `_pop_valid_target()` re-validates each entry against three filters
before dispatching: NFZ boundary, search area boundary, and proximity to known targets.
Invalid entries are silently skipped. This makes the queue self-cleaning when the search
area changes (e.g., PLB beacon redirect).

### 4.3 Target Lock During CENTERING (5 m Radius)

When investigating a target, only detections within `DETECT_LOCK_RADIUS_M = 5 m` of the
locked position refine the estimate. Detections outside 5 m are treated as separate
targets and queued.

**Why 5 m:** GPS has a CEP of 2-3 m. The same stationary object's estimated position
varies by up to 3 m between readings. 5 m comfortably encompasses this noise while
distinguishing objects that are physically separate.

**Why not no-lock:** A second target (B) visible from above target (A) would capture
attention if it has higher confidence, causing drift.

**Why not hard-lock (ignore all others):** Risks missing a nearby target the drone will
not see again.

### 4.4 Rejection Radius (5 m)

After the operator presses N or I, all future detections within `REJECTED_TARGET_RADIUS_M
= 5 m` of the rejected position are silently ignored.

**Why not 3 m:** Tested in simulation. The same object seen from adjacent scan lines
shifts by 3-4 m due to viewing geometry changes. 3 m caused re-investigation of
already-rejected targets.

**Why not 10 m:** Would suppress detections of distinct objects as close as 7 m apart.

### 4.5 NFZ and Search Area Filtering

- Detections inside the SSSI are silently discarded (the drone must never fly into the
  NFZ to investigate).
- Detections outside the active search polygon are ignored.
- Both checks are applied at detection time AND at dispatch time (`_pop_valid_target()`),
  so stale entries from before a PLB redirect are cleaned automatically.

### 4.6 Manual Mode Queuing

During M-key manual flight, detection continues running. Targets are queued with all
standard filters but no autonomous action is taken. On resume, queued targets are
investigated before returning to the scan line.

**Why not disable detection:** The camera is still pointing at the ground. Disabling
wastes frames that could contain the target.

### 4.7 Single Detection Per Frame

`detect_in_image()` returns only the highest-confidence detection per frame.

**Why:** The mission expects a single casualty. Multiple bounding boxes from the same
object (different scales) would flood the queue. Over multiple frames, different physical
objects naturally emerge as separate queue entries because the drone's movement changes
which object scores highest.

### 4.8 `--smart-detect` (Optional Multi-Frame Confirmation)

When active, requires `DETECT_CONFIRM_FRAMES = 3` consecutive detections before queuing.
Reduces false positives but risks missing edge-of-swath targets that appear in only 1-2
frames. **Off by default** because investigating a false positive costs ~10 seconds
(press N), while missing a real target costs a full rescan pass.

### 4.9 Confidence Threshold: 0.2

`CONFIDENCE_THRESHOLD = 0.2` in `config.py`.

**Why low:** The cost asymmetry is decisive. A missed detection (failed mission) far
outweighs a false positive (~10 seconds of operator time). Real dummy detections
consistently score above 0.8; false positives from terrain/shadows fall in 0.1-0.4. The
deduplication system (rejection radius, NFZ filter, boundary filter) prevents false
positives from flooding the queue.

---

## 5. GPS Position Estimation

### 5.1 Three-Stage Pipeline

Target localisation refines through three stages of increasing accuracy:

| Stage | When | Method | CEP |
|-------|------|--------|-----|
| 1. Trigonometric estimate | Flyover during SEARCH | Pixel offset -> GSD -> heading rotation -> GPS delta | ~5 m |
| 2. Centering refinement | CENTERING state (hover above target) | Re-detection with near-zero pixel offset | ~2 m |
| 3. GPS averaging (optional) | `--center-verify` flag during VERIFY | 10 s of readings (~100 samples at 10 Hz) | ~1 m |

### 5.2 GSD Formula

Ground Sample Distance at altitude `h`:

```
GSD = (SENSOR_WIDTH_MM * h) / (FOCAL_LENGTH_MM * IMAGE_W)
    = (5.02 * h) / (5.46 * 1456)
```

At `TARGET_ALT = 35 m`: GSD = **0.0221 m/pixel** (22.1 mm per pixel). A 1-pixel error
in detection centre = 22 mm on the ground -- negligible.

### 5.3 Pixel-to-GPS Conversion

```
offset_x_m = (px - IMAGE_W/2) * GSD
offset_y_m = (py - IMAGE_H/2) * GSD
offset_north = offset_x_m * cos(yaw) - offset_y_m * sin(yaw)
offset_east  = offset_x_m * sin(yaw) + offset_y_m * cos(yaw)
target_lat = drone_lat + offset_north / 111132.954
target_lon = drone_lon + offset_east / (111132.954 * cos(drone_lat))
```

### 5.4 Dominant Error Sources

| Source | Magnitude | Notes |
|--------|-----------|-------|
| GPS receiver latency | ~1 m at 6 m/s | 100-200 ms lag, along-track error |
| GPS position noise | 2-3 m CEP50 | Civilian GPS |
| Attitude uncertainty | Variable | Pitch/roll tilt the projection axis |
| Focal length calibration | +/- 0.1 mm | Measured at 5.46 mm |

Measured from DJI video analysis: CEP50 = 2.3 m, max outlier 16.5 m (GPS timing lag at
high speed).

### 5.5 Why Centering Above is Most Accurate

When the drone is directly above the target, the pixel displacement is near zero. The
GPS position is effectively the drone's own reading projected downward. No heading
rotation, no GSD scaling, no off-axis projection error. The estimate converges to the
drone's GPS accuracy itself (~2 m CEP).

### 5.6 `--center-verify` (Optional 10 s Averaging)

Adds 10 seconds of hover per detection to average ~100 GPS readings. Suppresses random
noise, reducing CEP to ~1 m. Opt-in because it costs time. For missions where the trig
estimate is adequate, omit the flag.

---

## 6. Vision System

### 6.1 Dual Backend

`vision.py` selects the inference backend at import time based on installed packages:

| Priority | Backend | Platform | Notes |
|----------|---------|----------|-------|
| 1 | Ultralytics YOLO | Laptop | GPU acceleration, rich debugging, auto output parsing |
| 2 | TFLite | Pi | CPU-optimized via `ai-edge-litert` (Python 3.13 compatible) |
| 3 | NCNN | Pi (experimental) | ARM NEON optimized, `--backend ncnn` flag |

All backends expose the same interface:

```python
detect_in_image(frame) -> (found: bool, x: int, y: int, conf: float)
```

No environment variables or flags needed for backend selection -- auto-detected.

### 6.2 IMX296 BGR Quirk

The IMX296 global shutter sensor outputs BGR pixel data despite picamera2's `RGB888`
format label. Discovered by testing all six channel permutations against known colour
targets. **No `cv2.cvtColor` conversion is applied** -- the data arrives in OpenCV's
native BGR format. Adding a conversion would swap red and blue, degrading detection.

### 6.3 Lens Undistortion

Calibrated using a checkerboard (calib.io, 14x9, 13x8 inner corners, 28 mm squares).
RMS reprojection error: 0.399 pixels. Remap maps precomputed at startup with
`cv2.initUndistortRectifyMap()`, applied per-frame via `cv2.remap()`. Cost: ~1.5 ms per
frame (negligible vs 206 ms inference). Applied inside `vision.py`, so all scripts
benefit automatically.

### 6.4 Model Retraining (v2)

The v2 model was retrained on a mixed dataset at native aspect ratio:

| Category | Count | Source |
|----------|-------|--------|
| Synthetic | 300 | `generate_dataset_v2.py` (dummy composited on DJI backgrounds, altitude-correct scaling) |
| Real | 16 | `tools/label_tool.py --full` (manually labelled DJI frames) |
| Negatives | 50 | DJI frames with no dummy (empty labels, reduces FP rate) |

Training: Google Colab T4 GPU, `imgsz=1088`, 150 epochs, batch 8. Result: mAP50 = 0.995.

**Drop-in replacement:** Same input `[1,640,640,3]`, same output `[1,5,8400]`, same
inference speed. Deploy with `cp cv_models/sar_v2_1088/best.tflite best.tflite`.

### 6.5 TFLite Coordinate Convention

YOLOv8 TFLite exports may output coordinates as normalized (0-1) or absolute pixels
(0-640). A runtime guard checks if values exceed 1.5 and scales accordingly:

```python
if raw_cx > 1.5:  # pixel coords
    cx = int(raw_cx * w / 640)
else:              # normalized coords
    cx = int(raw_cx * w)
```

Without this, pixel-coordinate models would cluster all detections in the top-left
corner.

---

## 7. Payload Delivery

### 7.1 Two-Stage Servo Release

After the operator confirms a target (Y), the drone flies to a 7.5 m lateral offset
from the target and descends to 3 m altitude. The servo then executes a two-stage
release:

| Time | Action | Servo PWM |
|------|--------|-----------|
| 0 s | Arrive at 3 m hover | 1500 (closed) |
| 3 s | Stage 1: partial release | 1300 |
| 6 s | Stage 2: full release | 1100 |
| 15 s | Close servo, depart | 1500 (closed) |

**Why two-stage:** A controlled release rather than a single sudden drop. Stage 1
loosens the payload, Stage 2 fully releases. 15-second hold ensures the payload clears
the mechanism and reaches the ground.

Servo commands sent via `MAV_CMD_DO_SET_SERVO` on channel 9. After the hold, the servo
closes, the drone climbs to search altitude, and transitions to `RETURN_TRANSIT` or
`RETURN_HOME`.

---

## 8. Configuration

### 8.1 Key Settings Table

| Parameter | Value | `config.py` name | Purpose |
|-----------|-------|-------------------|---------|
| Search altitude | 35.0 m | `TARGET_ALT` | Default scan height |
| Verify altitude | 15.0 m | `VERIFY_ALT` | Close-look altitude (legacy, no-descend design skips this) |
| Sensor width | 5.02 mm | `SENSOR_WIDTH_MM` | IMX296 physical sensor |
| Focal length | 5.46 mm | `FOCAL_LENGTH_MM` | Calibrated 2026-03-11 |
| Image resolution | 1456 x 1088 | `IMAGE_W`, `IMAGE_H` | Pi camera native |
| Confidence threshold | 0.2 | `CONFIDENCE_THRESHOLD` | Low to maximise recall |
| Speed at 20 m | 6.0 m/s | `SPEED_AT_LOW` | Less motion blur |
| Speed at 50 m | 10.0 m/s | `SPEED_AT_HIGH` | Faster coverage |
| Transit speed | 15.0 m/s | `TRANSIT_SPEED_MPS` | No detection during transit |
| Focus area speed | 5.0 m/s | `FOCUS_SEARCH_SPEED_MPS` | More detection time in PLB zone |
| Rejection radius | 5.0 m | `REJECTED_TARGET_RADIUS_M` | GPS noise margin for dedup |
| Lock radius | 5.0 m | `DETECT_LOCK_RADIUS_M` | Centering target lock |
| Max rescan passes | 3 | `MAX_RESCAN_PASSES` | Altitude-drop rescans |
| Rescan alt factor | 0.8 | `RESCAN_ALT_FACTOR` | 20% drop per pass |
| Rescan alt floor | 15.0 m | `RESCAN_ALT_FLOOR_M` | Obstacle clearance |
| NFZ slow zone | 20.0 m | `NFZ_SLOW_ZONE_M` | Speed cap activation range |
| NFZ min speed | 0.3 m/s | `NFZ_MIN_SPEED_MPS` | Near-stop at boundary |
| NFZ push speed | 3.0 m/s | `NFZ_PUSH_SPEED_MPS` | Repulsive velocity magnitude |
| Diagonal yaw offset | 0 (configurable) | `DIAGONAL_YAW_OFFSET_DEG` | Set to None for 53 deg auto |
| Confirm frames | 3 | `DETECT_CONFIRM_FRAMES` | `--smart-detect` only |

### 8.2 What to Tune Before Flight Day

| Setting | Why | How to determine |
|---------|-----|-----------------|
| `TARGET_ALT` | Lower if AI cannot detect from 35 m | Run passive_watch during manual flight, check detection altitude |
| `SPEED_AT_LOW` | Lower if frames are too blurry | Review detection rate from altitude_sweep experiment |
| `CONFIDENCE_THRESHOLD` | Raise if too many false positives outdoors | Analyse detection log from passive flight |
| `FOCAL_LENGTH_MM` | Re-calibrate if camera module changed | Hold camera 1 m above tape measure, read visible width |
| `NFZ_SLOW_ZONE_M` | Increase if GPS drift is severe on site | Check GPS noise from gps_drift experiment |

---

## 9. Key Tradeoffs

### 9.1 Single Frame vs Multi-Frame Detection

| | Single frame (default) | Multi-frame (`--smart-detect`) |
|---|---|---|
| **Behaviour** | Any detection above threshold is queued immediately | 3 consecutive detections required |
| **Pros** | Catches edge-of-swath targets (1-2 frames), aggressive recall | Fewer false positives |
| **Cons** | More FP investigations (~10 s each) | Misses targets at swath edges entirely |
| **Decision** | Default. Cost of a miss (full rescan, minutes) >> cost of a FP (10 seconds). |

### 9.2 0% Overlap vs 20% Overlap

| | 0% overlap (chosen) | 20% overlap |
|---|---|---|
| **Behaviour** | Scan lines spaced at full height dimension | Scan lines overlap by 20% |
| **Pros** | Fewer scan lines, faster coverage | Guaranteed coverage at seams |
| **Cons** | Relies on diagonal realignment for overlap | More scan lines, more time |
| **Decision** | Diagonal realignment gives 67% coverage bonus for free. 0% explicit overlap is sufficient. |

### 9.3 Speed Cap vs Velocity Commands for NFZ

| | `DO_CHANGE_SPEED` (chosen) | Velocity commands |
|---|---|---|
| **Behaviour** | Modify autopilot speed limit, let it handle direction | Send velocity toward waypoint at capped speed |
| **Pros** | No oscillation, same path, autopilot handles smoothing | Direct control |
| **Cons** | Speed cap does not affect WASD manual commands | Fights position controller, jittery |
| **Decision** | Tested both. Velocity commands caused oscillation. Speed cap integrates cleanly. |

### 9.4 Verify at Search Altitude vs Descend

| | Stay at altitude (chosen) | Descend to 15 m |
|---|---|---|
| **Behaviour** | Operator confirms from search altitude stream | Drone drops to get closer view |
| **Pros** | Saves 40 s per detection, avoids obstacle envelope, immediate resume | Better image for operator |
| **Cons** | Smaller target in stream | Costs time, battery, collision risk near 10-15 m trees |
| **Decision** | Camera FOV at 35 m is sufficient (~25 px on dummy). Time savings dominate over multiple FPs. |

### 9.5 Queue Order: FIFO vs Priority

| | FIFO (chosen) | Priority (highest confidence) |
|---|---|---|
| **Behaviour** | Investigate in detection order | Investigate strongest signal first |
| **Pros** | Simple, fair, no re-ordering overhead | Might find target sooner |
| **Cons** | Low-confidence-but-real target investigated before high-confidence FP | Same object scores differently from different angles; misleading |
| **Decision** | Confidence is not a reliable proxy for validity. FIFO is simple and fair. |

### 9.6 Rejection Radius: 5 m (GPS Noise Compromise)

| Radius | Behaviour | Problem |
|--------|-----------|---------|
| 3 m | Tight, matches GPS CEP | Same object re-investigated from adjacent scan lines (3-4 m shift) |
| **5 m (chosen)** | Encompasses viewing angle variation | Sweet spot |
| 10 m | Aggressive suppression | Masks distinct objects 7+ m apart |

---

## References

All numeric values in this document are drawn from `config.py` as deployed. Source files
are listed in Section 1.1. Design decision documents with full implementation details:

- `docs/DESIGN_DETECTION.md` -- detection pipeline (DD-1 through DD-10)
- `docs/DESIGN_GEOFENCE.md` -- NFZ three-layer protection
- `docs/DESIGN_PATH_PLANNING.md` -- lawnmower pattern and scan angle optimisation
- `docs/DESIGN_STATE_MACHINE.md` -- state definitions, transitions, timeouts
- `docs/DESIGN_VISION.md` -- CV subsystem, model training, GPS estimation
