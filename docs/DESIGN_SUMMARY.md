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

The system uses a boustrophedon (lawnmower) scan pattern (Choset, 2001). Alternatives considered:

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

### 2.7 Energy-Aware Path Planning

An energy simulation (`analysis/path_optimization/`) evaluated the lawnmower pattern
across 216 configurations (6 altitudes x 36 angles), accounting for momentum at U-turns,
NFZ slowdown zones, and altitude-dependent speed.

**Energy model:**

```
P_total = P_hover + P_drag = 150 W + 50 W * (v / 5)^2
```

Each U-turn incurs a 2-second deceleration/reacceleration penalty (momentum cost). The
SSSI no-fly zone is adjacent to the search area, so scan lines that pass near the NFZ
boundary trigger the speed cap (Section 3.3), adding approximately 45% time penalty on
affected segments.

**Scan angle:** The optimal scan angle is 65-75 degrees, aligning with the polygon's
longest dimension (NE-SW axis). This minimises the number of U-turns and total path
length.

**Altitude vs energy:**

| Altitude | Scan lines | Time | Energy |
|----------|-----------|------|--------|
| 50 m | 6 | 1.8 min | 8.3 Wh |
| 35 m | 9 | 3.3 min | 12.6 Wh |

Higher altitude means fewer scan lines, fewer U-turns, and faster speed (10 m/s at 50 m
vs 8 m/s at 35 m). The energy cost at 35 m is 52% higher than at 50 m for the same area.

**Analysis recommendation:** Start at 50 m for the fastest initial sweep. If the target is
missed, rescan at lower altitudes (40 m, 32 m) where pixel size improves. This "start high,
drop on miss" strategy optimises for the common case (target found on first pass) while
retaining fallback thoroughness.

**Deployed default:** `TARGET_ALT = 35 m` is the conservative operational choice for initial
flights, prioritising detection confidence over scan efficiency. `TARGET_ALT` can be changed
to 50 m after first-flight validation confirms reliable detection at that altitude.

**Future work:** Full momentum simulation with wind model, path smoothing at U-turns to
reduce deceleration penalty.

### 2.8 Altitude Justification (Why 50 m Is Recommended)

The energy analysis recommends 50 m as the optimal initial search altitude, driven by five
factors. The deployed default is `TARGET_ALT = 35 m` as a conservative choice for initial
flights; `TARGET_ALT` can be raised to 50 m after first-flight validation.

1. **Detection threshold:** At 50 m, the dummy is 34 pixels tall in the model's 640x640
   input -- well above the empirical 20-pixel detection threshold. The critical altitude
   (where the dummy drops below 20 px) is 62.7 m.

2. **Motion blur:** At 10 m/s and 50 m altitude, motion blur is 0.3 pixels per frame
   exposure -- negligible, thanks to the IMX296 global shutter sensor.

3. **Scan efficiency:** 50 m requires 33% fewer scan lines than 35 m (6 vs 9 lines),
   covering the same area in roughly half the time and energy.

4. **Speed advantage:** The altitude-speed curve (Section 2.6) allows 10 m/s at 50 m vs
   8 m/s at 35 m -- a 25% speed increase.

5. **Rescan safety net:** With the deployed default of 35 m, rescans proceed at 28 m then
   22.4 m (RESCAN_ALT_FACTOR = 0.8). If TARGET_ALT is changed to 50 m, rescans would be
   50 m -> 40 m -> 32 m. Either way, each pass catches targets with progressively better
   pixel resolution. The cost of starting high is one fast pass; the cost of starting low
   is spending the entire flight at slower speed with more scan lines.

### 2.9 Focus Area (PLB Beacon Redirect)

When a Personal Locator Beacon signal is received (B key or `--beacon-delay N`), the
search redirects to a smaller polygon:

1. Load focus area from `flight_plans/focus_area.json` (re-read each time, allows
   mid-flight coordinate updates from ground station)
2. Regenerate lawnmower pattern for the smaller polygon
3. Reset waypoint index and rescan counter
4. Drop speed to `FOCUS_SEARCH_SPEED_MPS = 5.0 m/s`
5. Preserve all rejected targets from the broad search

Fallback chain: JSON file -> drawn polygon (`config.FOCUS_AREA_GPS`) -> KML Focus Area.

The PLB beacon is simulated via the B key or `--beacon-delay` flag. Real PLB hardware
integration is planned for future work.

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
Based on ArduCopter's default WPNAV_ACCEL = 2.5 m/s^2, stopping from 10 m/s takes ~4 s /
~20 m. The 20 m buffer provides safety margin. It also gives the drone sufficient distance
to decelerate smoothly -- a gentle linear ramp over 20 m rather than a hard wall that would
cause abrupt braking or overshoot.

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

YOLOv8n (Jocher et al., 2023) (nano) was chosen for the Pi 5's CPU constraints:

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

### 4.8 Cost Asymmetry Analysis

The detection strategy is shaped by a fundamental cost asymmetry between false positives
and missed targets:

| Outcome | Cost | Time |
|---------|------|------|
| **False positive investigated** | Fly to location (10-15 s), operator presses N (2 s), resume search | ~20 s |
| **Missed real target** | Entire rescan pass at lower altitude | 2-5 minutes |

The cost ratio is approximately **10:1** in favour of erring on the detection side. This
asymmetry justifies two design choices:

1. **Low confidence threshold (0.2):** Catches weak detections that may be real targets
   viewed at oblique angles or partially occluded. The deduplication system (rejection
   radius, NFZ filter, boundary filter) prevents false positives from compounding.

2. **Single-frame trigger (no `--smart-detect` by default):** A target at the edge of the
   camera swath may appear in only 1-2 frames. Requiring 3 consecutive detections would
   miss these entirely, costing a full rescan pass. One false investigation (20 s) is
   cheaper than one missed target (2-5 min).

### 4.9 `--smart-detect` (Optional Multi-Frame Confirmation)

When active, requires `DETECT_CONFIRM_FRAMES = 3` consecutive detections before queuing.
Reduces false positives but risks missing edge-of-swath targets that appear in only 1-2
frames. **Off by default** because investigating a false positive costs ~10 seconds
(press N), while missing a real target costs a full rescan pass.

### 4.10 Confidence Threshold: 0.2

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

This section is the most technically detailed in the document. The vision system is the
core differentiator of the SAR drone -- it is the subsystem that turns a flying platform
into an autonomous search tool. Every design choice here is backed by measured data from
Pi 5 hardware benchmarks, DJI flight video analysis, and calibrated optics.

---

### 6.1 Camera and Optics

#### 6.1.1 Sensor: IMX296 Global Shutter

The Raspberry Pi Global Shutter Camera uses the Sony IMX296 sensor. The defining feature
is its **global shutter** -- all pixels are exposed simultaneously, unlike rolling-shutter
CMOS sensors where rows are read sequentially top-to-bottom. Rolling shutter causes three
artefacts during motion:

| Artefact | Cause | Impact on detection |
|----------|-------|---------------------|
| Skew (leaning buildings) | Horizontal motion during row-sequential readout | Distorts bounding boxes |
| Wobble (jello effect) | Vibration during readout | Oscillating object shapes, confuses NMS |
| Partial exposure | Flash or sudden lighting change during readout | Inconsistent brightness across frame |

The global shutter eliminates all three. The only remaining blur source is translational
motion during the exposure window, which is analysed in Section 6.7.

#### 6.1.2 Optical Parameters

| Parameter | Value | Source |
|-----------|-------|--------|
| Sensor width | 5.02 mm | IMX296 datasheet |
| Focal length | 5.46 mm | Calibrated with ruler at 1 m (92 cm visible width) |
| Native resolution | 1456 x 1088 px | Pi camera hardware mode |
| Horizontal FOV | 49.4 deg | Computed: `2 * atan(SENSOR_WIDTH_MM / (2 * FOCAL_LENGTH_MM))` |
| DJI video HFOV | 54.4 deg | Calibrated from flight video using `tools/fov_calibrate_video.py` |

The focal length was measured by holding the camera exactly 1 m above a tape measure and
reading the visible width (92 cm), then computing:

```
FOCAL_LENGTH_MM = SENSOR_WIDTH_MM * distance / visible_width
                = 5.02 * 1000 / 920 = 5.46 mm
```

The HFOV from sensor geometry (49.4 deg) and the DJI video calibration (54.4 deg) differ
because the DJI video was cropped from 3840x2160 to 1456x1088 with a different lens. The
49.4 deg value applies to the Pi camera; the 54.4 deg value applies to DJI video analysis
only.

#### 6.1.3 BGR Output Quirk

The IMX296 sensor outputs BGR pixel data despite picamera2's `RGB888` format label. This
was discovered by capturing a frame of known colour targets (red/green/blue cards) and
testing all six channel permutations (RGB, RBG, GRB, GBR, BGR, BRG) against ground truth.
Only the raw (unswapped) output matched, confirming BGR ordering.

**No `cv2.cvtColor` conversion is applied** -- the data arrives in OpenCV's native BGR
format. Adding a conversion would swap red and blue channels, degrading detection accuracy
(the model was trained on BGR-ordered data).

---

### 6.2 Ground Footprint and Target Size

#### 6.2.1 Footprint Formula

The ground footprint at altitude `h` is derived from the thin-lens model:

```
footprint_W = (SENSOR_WIDTH_MM * h) / FOCAL_LENGTH_MM
footprint_H = footprint_W * (IMAGE_H / IMAGE_W)
GSD = footprint_W / IMAGE_W
```

Where GSD (Ground Sample Distance) is the real-world distance represented by one pixel:

```
GSD = (5.02 * h) / (5.46 * 1456) = h * 6.315e-4   [m/px]
```

#### 6.2.2 Footprint Table

| Altitude (m) | Footprint W x H (m) | GSD (m/px) | Coverage Area (m^2) |
|:------------:|:--------------------:|:----------:|:-------------------:|
| 20 | 18.4 x 13.7 | 0.0126 | 252 |
| 25 | 23.0 x 17.2 | 0.0158 | 396 |
| 30 | 27.6 x 20.6 | 0.0189 | 569 |
| 35 | 32.2 x 24.0 | 0.0221 | 773 |
| 40 | 36.8 x 27.5 | 0.0253 | 1,012 |
| 50 | 46.0 x 34.3 | 0.0316 | 1,578 |

#### 6.2.3 Target Size in Image

The dummy target is 1.8 m tall and 0.5 m wide (lying on the ground). Because the model
input is 640 x 640 and the native frame is 1456 x 1088, the frame is resized by a factor
of 640/1456 = 0.4396 horizontally and 640/1088 = 0.5882 vertically:

```
dummy_full_tall  = DUMMY_HEIGHT_M / GSD
dummy_model_tall = dummy_full_tall * (640 / IMAGE_H)
dummy_model_wide = (0.5 / GSD) * (640 / IMAGE_W)
```

| Altitude (m) | Full Frame (px) tall x wide | Model Input (px) tall x wide | Detectable? |
|:------------:|:---------------------------:|:----------------------------:|:-----------:|
| 20 | 143 x 40 | 84 x 18 | Yes -- large target |
| 25 | 114 x 32 | 67 x 14 | Yes -- comfortable |
| 30 | 95 x 26 | 56 x 12 | Yes -- solid |
| 35 | 81 x 23 | 48 x 10 | Yes -- adequate |
| 40 | 71 x 20 | 42 x 9 | Yes -- marginal width |
| 50 | 57 x 16 | 34 x 7 | Marginal -- height OK, width thin |

**Detection threshold:** YOLOv8n requires approximately 15-20 pixels in the smallest
dimension of its 640 x 640 input to reliably detect an object. The dummy's height remains
above this threshold even at 50 m (34 px). The width drops to 7 px at 50 m, but because
the model was trained on elongated figure shapes (lying-down dummy), height is the dominant
dimension for detection.

**Critical altitude:** The dummy height drops below 20 px in the model input at
approximately 85 m. Below 15 px (~100 m), detection would be unreliable. The operational
range of 20-50 m keeps the dummy at 34-84 px -- comfortably above the detection floor.

---

### 6.3 Model Architecture

#### 6.3.1 Why YOLOv8n

YOLOv8n (nano) was selected as the optimal trade-off between accuracy and inference speed
on the Raspberry Pi 5's Cortex-A76 CPU:

| Variant | Parameters | FLOPs (B) | COCO mAP50 | TFLite Size | Expected Pi 5 FPS |
|---------|:----------:|:---------:|:----------:|:-----------:|:-----------------:|
| **YOLOv8n (chosen)** | 3.2 M | 8.7 | 37.3 | 3.2-11.7 MB | **4.8** (measured) |
| YOLOv8s | 11.2 M | 28.6 | 44.9 | ~23 MB | ~1.5 (estimated) |
| YOLOv8m | 25.9 M | 78.9 | 50.2 | ~52 MB | ~0.6 (estimated) |

YOLOv8s would reduce throughput to approximately 1.5 FPS, cutting the number of frames
per target flyover from 11-17 down to 3-5. YOLOv8m would yield sub-1 FPS, making
real-time search impractical. YOLOv8n at 4.8 FPS provides 11-17 detection opportunities
per target pass (Section 6.8), which is more than sufficient given that a single detection
triggers investigation.

#### 6.3.2 Model Input/Output

- **Input shape:** `[1, 640, 640, 3]` -- single image, 640x640 pixels, 3 channels (RGB), float32
- **Output shape:** `[1, 5, 8400]` -- transposed to `[8400, 5]` where each row is
  `[cx, cy, w, h, class_conf]` in normalised coordinates
- **8400 candidates:** YOLOv8 generates predictions at three scales (P3/8, P4/16, P5/32),
  producing 80x80 + 40x40 + 20x20 = 8400 anchor-free detection candidates
- **Single class:** "dummy" (class 0). Only one confidence value per candidate.
- **NMS:** Non-maximum suppression filters overlapping boxes. The highest-confidence
  surviving detection is returned.

#### 6.3.3 Training Resolution vs Inference Resolution

The v2 model was **trained at `imgsz=1088`** (native camera resolution) but **infers at
640x640** (TFLite runtime always resizes to 640x640). This means the model learned features
from higher-resolution crops during training, but at inference time the input is
letterboxed/resized to 640x640 with aspect ratio preserved. The training at higher
resolution teaches the model to recognise finer features that survive the downscale.

#### 6.3.4 TFLite Export

| Property | Value |
|----------|-------|
| Format | TensorFlow Lite (float32) |
| Size (v2, sar_v2_1088) | 11.7 MB |
| Size (v1, original) | 3.2 MB |
| Quantisation | None (float32) |
| Delegate | XNNPACK (CPU, ARM NEON) |

The v2 model is larger because it was trained at higher resolution, which produces more
feature map weights. Both models have identical input/output shapes and are drop-in
replacements for each other.

---

### 6.4 Training Data

#### 6.4.1 Dataset Evolution

| Version | Dataset | Resolution | Images | Real Frames | Negatives | mAP50 |
|---------|---------|:----------:|:------:|:-----------:|:---------:|:-----:|
| v1 (original) | Synthetic only (map.jpg backgrounds) | 640 x 640 | 200 | 0 | 0 | ~0.95 |
| **v2 (current)** | **Synthetic + real + negatives** | **1456 x 1088** | **366** | **16** | **50** | **0.995** |

#### 6.4.2 v2 Dataset Composition

The v2 dataset (`dataset_v2/`, 366 images at 1456 x 1088) comprises three categories:

**300 synthetic images** (`generate_dataset_v2.py`):
- `dummy.png` composited on real DJI flight video frame backgrounds
- Altitude-correct scaling ensures the dummy pixel size matches what the camera would see
  at each simulated altitude (15-50 m)
- Augmentation: brightness +/-30%, contrast +/-20%, Gaussian blur (sigma 0-3 px),
  rotation +/-15 deg, scale 0.8-1.2x

**16 real labelled frames** (`tools/label_tool.py --full`):
- Extracted from DJI flight video at various altitudes
- Labelled at native 1456x1088 resolution (no squishing to 640x640)
- These anchor the model to actual camera characteristics: colour response, noise,
  compression artefacts, real lighting conditions

**50 negative images** (no dummy present):
- Real flight video frames containing no target
- Empty label files teach the model to suppress false positives on grass, paths, shadows,
  and terrain features
- Without negatives, the model learns that every image contains a target, inflating FP rate

#### 6.4.3 Why Synthetic Data Works

Synthetic compositing is effective for this application because:

1. **Real backgrounds:** The backgrounds are real satellite/aerial imagery, not
   procedurally generated textures. The model sees realistic grass, paths, and shadows.
2. **Altitude-correct scaling:** The composite scales the dummy to the correct pixel size
   for each simulated altitude, producing geometrically accurate training samples.
3. **Low visual complexity:** The single-class detection task (one target type on uniform
   grass) has far lower visual complexity than general object detection (COCO: 80 classes,
   cluttered scenes).
4. **Real frame anchoring:** The 16 real frames bridge the domain gap between synthetic
   composites and actual camera output.

The mAP50 of 0.995 on the v2 dataset and consistent high-confidence detections (0.966 avg)
on real Pi hardware confirm that the synthetic-dominant approach generalises adequately for
this constrained domain. (Note: train and validation sets overlap -- a known limitation of
the small dataset. Real-world performance is validated by the Pi benchmark and DJI video
analysis.)

#### 6.4.4 Training Configuration

```
Base weights:     yolov8n.pt (COCO pretrained)
Platform:         Google Colab, T4 GPU
Training:         imgsz=1088, epochs=150, batch=8, early stopping patience=30
Augmentation:     rotation +/-20 deg, scale 0.7, mosaic 1.0, copy-paste 0.2, hflip 0.5
Export:           TFLite float32 (imgsz=640)
Result:           mAP50 = 0.995
```

---

### 6.5 Dual Backend Architecture

`vision.py` implements a single public interface -- `detect_in_image(frame)` returning
`(found, x, y, confidence)` -- backed by three runtime engines selected automatically at
startup:

| Priority | Backend | Runtime | Model Format | Typical Platform |
|:--------:|---------|---------|--------------|------------------|
| 0 | NCNN | ncnn (C++ via Python bindings) | `.param` + `.bin` | Pi 5 (ARM-optimised) |
| 1 | Ultralytics YOLO | PyTorch + Ultralytics | `.tflite` or `.pt` | Laptop (dev/GPU) |
| 2 | TFLite Direct | ai-edge-litert / tflite-runtime | `.tflite` | Pi 5 (production) |

Backend selection is automatic: `vision.py` attempts imports in priority order and uses
the first available. On the Raspberry Pi, Ultralytics is not installed (it pulls in
PyTorch at 2+ GB, unacceptable for a 4 GB embedded board), so inference falls through to
TFLite Direct. On the development laptop, Ultralytics provides GPU acceleration and richer
debugging output.

**Why this matters:** All mission scripts (`main.py`, `pi_flight.py`, `passive_watch.py`)
call `detect_in_image()` without knowing which backend is active. The model file
(`best.tflite`) is identical on both platforms. Swapping models requires only copying a
file -- no code changes. Deploy the v2 model with:
`cp cv_models/sar_v2_1088/best.tflite best.tflite`.

---

### 6.6 Inference Pipeline

Every frame passes through the same pipeline regardless of backend:

```
Frame capture (picamera2 / cv2.VideoCapture)
    |
    v
1. Lens undistortion          ~1.5 ms    (cv2.remap, precomputed maps)
    |
    v
2. Colour conversion          ~0.3 ms    (BGR -> RGB via cv2.cvtColor)
    |
    v
3. Resize to 640x640          ~0.5 ms    (bilinear interpolation)
    |
    v
4. Normalise to [0, 1]        ~0.2 ms    (float32 division by 255)
    |
    v
5. TFLite invoke               ~206 ms   (XNNPACK CPU delegate)
    |
    v
6. Output parsing              ~0.1 ms   (transpose, threshold, NMS)
    |
    v
7. Coordinate scaling          ~0.0 ms   (normalised -> frame pixels)
    |
    v
Result: (found, x, y, conf)
```

**Total: ~208 ms = 4.8 FPS on Pi 5 CPU (XNNPACK).**

Step 5 (TFLite invoke) dominates at 99% of total time. All other steps combined add less
than 3 ms.

#### 6.6.1 TFLite Coordinate Convention

YOLOv8 TFLite exports may output coordinates as normalised (0-1) or absolute pixels
(0-640) depending on the export configuration. A runtime guard handles both:

```python
if raw_cx > 1.5:  # pixel coords (0-640)
    cx = int(raw_cx * w / 640)
else:              # normalized coords (0-1)
    cx = int(raw_cx * w)
```

Without this guard, pixel-coordinate models would cluster all detections in the top-left
corner of the frame.

---

### 6.7 Motion Blur Analysis

#### 6.7.1 Global Shutter Advantage

The IMX296 global shutter eliminates rolling-shutter artefacts (skew, wobble, partial
exposure) during motion. All rows are exposed simultaneously, so the only blur source is
translational motion during the exposure window.

#### 6.7.2 Blur Model

Motion blur on the ground plane:

```
blur_ground = speed * exposure_time                  [metres]
blur_pixels = blur_ground / GSD                       [pixels]
```

With `SENSOR_WIDTH_MM = 5.02`, `FOCAL_LENGTH_MM = 5.46`, `IMAGE_W = 1456`:

```
GSD = (5.02 * h) / (5.46 * 1456) = h * 6.315e-4    [m/px]
```

#### 6.7.3 Blur at Operational Conditions

| Speed (m/s) | Exposure | Blur on Ground (mm) | Blur at 20 m (px) | Blur at 35 m (px) | Blur at 50 m (px) |
|:-----------:|:--------:|:-------------------:|:-----------------:|:-----------------:|:-----------------:|
| 6 | 1/500 s | 12 | 1.0 | 0.5 | 0.4 |
| 6 | 1/1000 s | 6 | 0.5 | 0.3 | 0.2 |
| 10 | 1/500 s | 20 | 1.6 | 0.9 | 0.6 |
| 10 | 1/1000 s | 10 | 0.8 | 0.5 | 0.3 |
| 15 | 1/500 s | 30 | 2.4 | 1.4 | 0.9 |
| 15 | 1/1000 s | 15 | 1.2 | 0.7 | 0.5 |

#### 6.7.4 Blur Impact on Detection

At the operational speed profile (6-10 m/s, altitude-dependent) with 1/1000 s shutter
speed, motion blur is **0.2-0.8 pixels** -- effectively sub-pixel and invisible to the
detector. Even at a conservative 1/500 s exposure, blur remains below 1.6 pixels at
maximum speed.

The critical speed where blur exceeds 1 pixel (at 35 m altitude, 1/1000 s exposure):

```
1 pixel = critical_speed * 0.001 / (35 * 6.315e-4)
critical_speed = 35 * 6.315e-4 / 0.001 = 22.1 m/s
```

At 50 m altitude, the critical speed rises to **31.6 m/s** -- well above the maximum drone
speed of 15 m/s.

**Conclusion: Motion blur is not a limiting factor for detection performance.** The global
shutter combined with short exposure times freezes the image at any achievable drone speed.

---

### 6.8 Speed vs Frame Coverage

#### 6.8.1 Frame Coverage Model

At 4.8 FPS, the distance the drone travels between consecutive frames is:

```
frame_gap = speed / FPS
```

The number of frames containing the target depends on how long it remains in the camera's
field of view:

```
time_in_view = footprint_H / speed
frames_in_view = time_in_view * FPS
```

#### 6.8.2 Frames per Target Flyover

The altitude-dependent speed profile from `config.py` linearly interpolates between
6.0 m/s at 20 m and 10.0 m/s at 50 m:

| Altitude (m) | Speed (m/s) | Frame Gap (m) | Footprint H (m) | Time in View (s) | Frames in View |
|:------------:|:-----------:|:-------------:|:---------------:|:----------------:|:--------------:|
| 20 | 6.0 | 1.25 | 13.7 | 2.28 | 11.0 |
| 25 | 6.7 | 1.39 | 17.2 | 2.57 | 12.3 |
| 30 | 7.3 | 1.53 | 20.6 | 2.82 | 13.5 |
| 35 | 8.0 | 1.67 | 24.0 | 3.00 | 14.4 |
| 40 | 8.7 | 1.80 | 27.5 | 3.16 | 15.2 |
| 50 | 10.0 | 2.08 | 34.3 | 3.43 | 16.5 |

The target appears in **11-17 frames** at every operational altitude. Even at the fastest
configuration (10 m/s at 50 m), the target is visible for 3.4 seconds and captured in
approximately 16 frames. A single detection with confidence above 0.2 is sufficient to
trigger investigation.

#### 6.8.3 Single-Frame Detection Speed

For the target to appear in only 1 frame, the drone would need to traverse the entire
footprint height in one frame interval (1/4.8 = 0.208 s):

| Altitude (m) | Single-Frame Speed (m/s) | Notes |
|:------------:|:------------------------:|:------|
| 20 | 66 | Well beyond drone capability |
| 35 | 115 | Physically impossible |
| 50 | 165 | Physically impossible |

Frame coverage is never the limiting factor at any realistic drone speed.

#### 6.8.4 Consecutive Frame Overlap

At 35 m altitude and 8 m/s, the frame gap is 1.67 m against a 24.0 m footprint height:

```
overlap = 1 - (frame_gap / footprint_H) = 1 - (1.67 / 24.0) = 93%
```

Consecutive frames overlap by **93%**, providing substantial redundancy for detection.

---

### 6.9 GPS Estimation from Detection

#### 6.9.1 Method

When a detection occurs, the target's GPS position is estimated by projecting the pixel
offset from frame centre through the camera model:

```
offset_x_m = (pixel_x - IMAGE_W/2) * GSD
offset_y_m = (pixel_y - IMAGE_H/2) * GSD
offset_north = offset_x_m * cos(yaw) - offset_y_m * sin(yaw)
offset_east  = offset_x_m * sin(yaw) + offset_y_m * cos(yaw)
target_lat = drone_lat + offset_north / 111320
target_lon = drone_lon + offset_east / (111320 * cos(drone_lat))
```

This requires the drone's current GPS position, altitude (for GSD), and heading (yaw) to
rotate the pixel offset into the geographic frame.

#### 6.9.2 Measured Accuracy

Analysis of 143 GPS estimates from DJI flight video replay (`video_test.py`):

| Metric | Value |
|--------|-------|
| CEP50 (50% circular error probable) | 2.3 m |
| Maximum error | 16.5 m |
| Error distribution | Diagonal spread along flight direction |

#### 6.9.3 Error Sources

| Source | Magnitude | Mechanism |
|--------|-----------|-----------|
| **GPS receiver latency (dominant)** | ~1 m at 6 m/s | 100-200 ms lag; drone has moved since GPS fix was taken |
| GPS position noise | 2-3 m CEP50 | Civilian GPS accuracy limit |
| Yaw uncertainty | ~1.2 m at edge | Magnetometer +/-2-5 deg; `lateral_error = footprint_W/2 * sin(3 deg)` |
| Altitude error | 14% GSD error | GPS altitude +/-5 m; changes pixel-to-metre scaling |
| Lens distortion (corrected) | Sub-pixel | Barrel distortion at frame edges, corrected by calibration |

The GPS receiver latency creates a characteristic diagonal spread in the scatter plot --
estimates are biased along the direction of travel because the drone has moved 0.6-2.0 m
since the GPS fix was recorded.

#### 6.9.4 Bullseye Scatter Plot Visualisation

Two tools provide real-time bullseye scatter plots of GPS estimation accuracy:

- **`tests/laptop/video_test.py`** — replays DJI flight video with detection overlay. Shows two scatter plots: one coloured by distance from image centre (centre-snap detections are most accurate), one coloured by altitude (lower = more accurate). Prints CEP50, max spread, and mean error. This was used to measure the 2.3 m CEP50 from real flight data.

- **`simulator/simple_simulator.py`** — interactive simulation with live bullseye plot. As the drone flies over dummies, each detection adds a dot to the scatter. Shows inverse-variance weighted average, Kalman filter estimate, and running total. Supports zoom/pan, landing zone donut overlay, and Tab to cycle between multiple targets. Used to validate the GPS estimation pipeline end-to-end before real flights.

Both tools demonstrate how estimates converge as more observations are collected, and how centering directly above the target produces the tightest cluster.

#### 6.9.5 Accuracy Improvement Strategies

| Strategy | How it works | Expected CEP |
|----------|-------------|:------------:|
| **Vision centering** | Fly directly above target; pixel offset approaches zero | ~1 m |
| **GPS averaging (10 s)** | Mean of ~100 samples; random noise averages out | <0.5 m |
| **GPS lag compensation** | Offset position by `speed * lag` in heading direction | ~1.5 m (removes bias) |
| **Multi-pass averaging** | Estimates from opposite-direction scan lines cancel directional bias | ~1.5 m |

The CENTERING state in the state machine achieves vision centering by flying directly above
the detection. At that point the pixel displacement is near zero -- the GPS estimate
converges to the drone's own GPS accuracy (no heading rotation, no GSD scaling, no off-axis
projection error).

---

### 6.10 Confidence Threshold

#### 6.10.1 Current Setting

```python
CONFIDENCE_THRESHOLD = 0.2   # config.py
```

#### 6.10.2 Threshold Trade-off

| Threshold | False Positive Rate | Missed Target Risk | Best For |
|:---------:|:-------------------:|:------------------:|----------|
| 0.5+ | Very low | High (misses edge-of-frame, altitude limit) | Verification phase |
| 0.35-0.4 | Low | Medium | Bench testing, controlled conditions |
| 0.25-0.3 | Medium | Low | Video analysis default |
| **0.2** | **Higher** | **Very low** | **Search phase (current)** |

#### 6.10.3 Cost Asymmetry Justification

The threshold is deliberately set low (0.2) because of the asymmetric cost structure:

- **False positive cost:** The drone diverts to investigate, the operator reviews the
  detection image and rejects it (presses N). Total cost: ~10-15 seconds.
- **Missed target cost:** The target is not detected on this scan line. The system must
  complete the remaining scan, potentially run a rescan at lower altitude, adding 2-5
  minutes. In a real SAR scenario, a missed casualty could be life-threatening.

The cost ratio is approximately **10:1** in favour of erring on the detection side. Real
dummy detections consistently score 0.8-0.95; false positives from terrain/shadows
typically fall in 0.2-0.4. The deduplication system (rejection radius, NFZ filter,
boundary filter) prevents false positives from flooding the queue.

#### 6.10.4 Smart-Detect (Optional Multi-Frame Confirmation)

The `--smart-detect` flag enables multi-frame confirmation:

```python
DETECT_CONFIRM_FRAMES = 3   # config.py
```

When enabled, 3 consecutive frames with detections are required before triggering
investigation. This suppresses transient false positives while the low base threshold
ensures weak but real detections accumulate across frames. **Off by default** because
a target at the edge of the camera swath may appear in only 1-2 frames -- requiring 3
would miss it entirely, costing a full rescan pass.

---

### 6.11 Lens Calibration

#### 6.11.1 Calibration Method

Lens distortion was measured using a printed calibration target and OpenCV's camera
calibration pipeline (`cv2.findChessboardCornersSB` with robust fallback):

| Parameter | Value |
|-----------|-------|
| Camera | Raspberry Pi Global Shutter (IMX296) |
| Resolution | 1456 x 1088 |
| Calibration board | calib.io 14x9 (13x8 inner corners, 28 mm squares) |
| RMS reprojection error | 0.399 |
| Calibration file | `calibration_data.npz` (on Pi only, not in git) |

#### 6.11.2 Implementation

`vision.py` precomputes the undistortion remap tables at initialisation:

```python
new_mtx, _ = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 0, (w, h))
map1, map2 = cv2.initUndistortRectifyMap(mtx, dist, None, new_mtx, (w, h), cv2.CV_16SC2)
```

Every frame is corrected via `cv2.remap(frame, map1, map2, cv2.INTER_LINEAR)` before
detection. The `alpha=0` parameter crops the result to valid pixels only (no black borders).

#### 6.11.3 Performance Impact

| Metric | Without Undistortion | With Undistortion | Delta |
|--------|:--------------------:|:-----------------:|:-----:|
| Inference time | 206.5 ms | 208.0 ms | +1.5 ms (+0.7%) |
| Detection confidence | 0.966 | 0.958 | -0.008 (test image artefact) |
| GPS estimation at edges | Biased outward | Corrected | Improved accuracy |

The 1.5 ms cost is negligible (0.7% of total frame time). The primary benefit is improved
GPS estimation accuracy for detections near frame edges, where barrel distortion would
otherwise shift the apparent position by several pixels. The slight confidence drop (0.966
to 0.958) is an artefact of running undistortion on a synthetic test image that was
generated without lens distortion. On real distorted images, undistortion improves
edge-region accuracy.

---

### 6.12 Benchmark Results

All benchmarks measured on Raspberry Pi 5 (4 GB), Python 3.13, ai-edge-litert with
XNNPACK CPU delegate. Input: 640 x 640 float32.

| Model | Size | Undistort | Avg Inference (ms) | FPS | Detection Rate | Avg Confidence |
|-------|:----:|:---------:|:------------------:|:---:|:--------------:|:--------------:|
| best.tflite | 3.2 MB | No | 206.5 | 4.8 | 30/30 (100%) | 0.966 |
| best.tflite | 3.2 MB | Yes | 208.0 | 4.8 | 30/30 (100%) | 0.958 |
| sar_v2_1088 | 11.7 MB | No | ~206 | 4.8 | 30/30 (100%) | 0.966 |

#### Backend Comparison (Measured and Projected)

| Backend | Avg Inference (ms) | FPS | Status | Notes |
|---------|:------------------:|:---:|:------:|-------|
| TFLite (XNNPACK, FP32) | 206.5 | 4.8 | **Measured** | Current production backend |
| TFLite (XNNPACK, FP16) | ~100 | ~10 | Projected | Pi 5 ARMv8.2-A has native FP16 |
| NCNN (FP32) | ~68 | ~15 | Projected | ARM-optimised, export available |
| TFLite (INT8) | ~145 | ~7 | Projected | ~30% improvement over FP32 |

---

### 6.13 Multi-Pass Descent Strategy

The search begins at 50 m and descends if no detection occurs within the scan area. Each
rescan pass uses `RESCAN_ALT_FACTOR = 0.8` to reduce altitude:

```
Pass 1: 50 m   (dummy 34 px tall in model -- viable)
Pass 2: 40 m   (dummy 42 px tall -- comfortable)
Pass 3: 32 m   (dummy 52 px tall -- easy)
Floor:  15 m   (RESCAN_ALT_FLOOR_M -- dummy 100+ px tall)
```

Starting at 50 m rather than 35 m requires approximately 33% fewer scan lines and permits
25% faster flight speed. Combined, the initial scan pass completes in roughly 60% of the
time. The multi-pass strategy ensures that even if the first pass misses a partially
occluded or unusually oriented target, subsequent passes at lower altitude provide
increasingly favourable detection conditions.

---

### 6.14 Summary of Limiting Factors

| Factor | Limiting? | Reason |
|--------|:---------:|--------|
| Motion blur | **No** | Global shutter + short exposure = sub-pixel blur at all speeds |
| Target pixel size (altitude) | **Marginal at 50 m** | Dummy height 34 px in model input, above 20 px floor |
| Target pixel size (below 40 m) | **No** | Dummy height > 42 px in model input |
| Inference FPS | **No** | 4.8 FPS gives 11-17 frames per target flyover |
| Frame gap between frames | **No** | 93% frame overlap at 35 m altitude, 8 m/s |
| Drone speed | **No** | Max 10 m/s is far below ~66 m/s single-frame threshold |
| GPS estimation | **Yes** | CEP50 = 2.3 m, max 16.5 m, dominated by GPS receiver lag |

**The real operational limit is altitude, not speed or blur.** Above approximately 85 m,
the dummy height drops below 20 px in the model input and detection becomes unreliable.
The speed profile (`SPEED_AT_LOW = 6 m/s` at 20 m, `SPEED_AT_HIGH = 10 m/s` at 50 m)
is conservative relative to the detection envelope. Speed could be increased to 15+ m/s
without impacting detection, though this would degrade GPS estimation accuracy due to the
100-200 ms GPS timing lag.

---

### 6.15 Future Vision Improvements

#### 6.15.1 Inference Speed

| Improvement | Expected Gain | Effort | Status |
|-------------|:------------:|:------:|:------:|
| FP16 XNNPACK | ~2x (10 FPS) | Low (1-2 hrs) | Pi 5 has native FP16 (ARMv8.2-A) |
| Threaded capture + inference | +20-30% | Low (1 hr) | Producer-consumer, GIL not an issue |
| NCNN backend | ~3x (15 FPS) | Medium (2-3 hrs) | Export available in `cv_models/sar_v2_1088/ncnn/` |
| Overclock to 2.8 GHz | +15-20% | Low (15 min) | 3 lines in `/boot/firmware/config.txt` |
| Lower input resolution (416x416) | ~2x (8 FPS) | Low (30 min) | Accuracy impact on small targets |
| INT8 quantisation | ~30% | Medium (needs calibration) | Needs 300+ representative frames |
| YOLO26n + NCNN | ~3x (15 FPS) + better accuracy | High (retraining) | +7% mAP over YOLOv8n |
| Hailo-8L accelerator | 80+ FPS | Hardware ($70) | Dedicated AI HAT for Pi 5 |

**Recommended priority:** FP16 XNNPACK first (highest impact, lowest effort), then
threaded pipeline, then NCNN. Combined, these three could reach 10-15 FPS -- a 2-3x
improvement over the current 4.8 FPS baseline.

#### 6.15.2 Detection Quality

| Improvement | Impact | Effort |
|-------------|--------|--------|
| More real labelled frames (target: 50-100) | Reduces overfitting to synthetic data | Medium |
| Multiple dummy poses/clothing | Improves generalisation | Medium |
| Partially occluded training samples | Handles tall grass, shadows | Medium |
| Proper train/val split (80/20) | Gives meaningful validation metrics | Low |
| Multi-class detection (dummy + person + cone) | Broader target coverage | High |
| Tiled inference (640 px tiles with overlap) | Better small-target detection at high altitude | Medium |

#### 6.15.3 GPS Accuracy

| Improvement | Impact | Effort |
|-------------|--------|--------|
| GPS lag compensation (speed * lag in heading direction) | Removes directional bias | Low |
| Kalman filter on target position estimates | Smooths noisy estimates | Medium |
| RTK GPS module | Sub-centimetre positioning | High (hardware + cost) |
| Visual odometry (optical flow between frames) | Supplements GPS during fast manoeuvres | High |

---

### 6.16 Configuration Reference

All vision-related parameters from `config.py`:

```python
# Camera hardware
SENSOR_WIDTH_MM      = 5.02       # IMX296 sensor physical width
FOCAL_LENGTH_MM      = 5.46       # Calibrated: 92 cm visible at 1 m height
IMAGE_W              = 1456       # IMX296 native resolution (horizontal)
IMAGE_H              = 1088       # IMX296 native resolution (vertical)
CAMERA_FLIP_180      = True       # Camera mounted inverted on drone

# Detection
CONFIDENCE_THRESHOLD = 0.2       # Low threshold, operator filters FPs

# Speed profile (altitude-dependent)
SPEED_ALT_LOW        = 20.0      # Below this altitude: use SPEED_AT_LOW
SPEED_ALT_HIGH       = 50.0      # Above this altitude: use SPEED_AT_HIGH
SPEED_AT_LOW         = 6.0       # m/s at low altitude
SPEED_AT_HIGH        = 10.0      # m/s at high altitude
SEARCH_SPEED_MPS     = 10.0      # Default search speed
TRANSIT_SPEED_MPS    = 15.0      # Transit between waypoints

# Search strategy
TARGET_ALT           = 35.0      # Initial search altitude (m)
VERIFY_ALT           = 15.0      # Descent altitude for verification (m)
MAX_RESCAN_PASSES    = 3         # Number of altitude-drop rescans
RESCAN_ALT_FACTOR    = 0.8       # Altitude multiplier per rescan pass
RESCAN_ALT_FLOOR_M   = 15.0      # Minimum rescan altitude

# Target specifications
DUMMY_HEIGHT_M       = 1.8       # Target height for pixel-size calculations
TARGET_REAL_RADIUS_M = 0.15      # 15 cm detection radius
```

---

### 6.17 Key Formulas

For reference in the report, the core optical and detection formulas:

**Ground sample distance:**
```
GSD = (SENSOR_WIDTH_MM * altitude) / (FOCAL_LENGTH_MM * IMAGE_W)
```

**Ground footprint:**
```
footprint_W = SENSOR_WIDTH_MM * altitude / FOCAL_LENGTH_MM
footprint_H = footprint_W * (IMAGE_H / IMAGE_W)
```

**Target size in model input:**
```
target_model_px = (target_real_m / GSD) * (640 / IMAGE_dim)
```

**Motion blur:**
```
blur_pixels = (speed * exposure_time) / GSD
```

**Frames per flyover:**
```
frames_in_view = (footprint_H / speed) * FPS
```

**Consecutive frame overlap:**
```
overlap = 1 - (speed / (FPS * footprint_H))
```

**GPS estimation from pixel offset:**
```
offset_m = (pixel - IMAGE/2) * GSD
target_lat = drone_lat + offset_y_m / 111320
target_lon = drone_lon + offset_x_m / (111320 * cos(lat))
```

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

### 9.7 50 m vs 35 m Start Altitude

| | 50 m (analysis recommendation) | 35 m (deployed default) |
|---|---|---|
| **Scan lines** | 6 | 9 (50% more) |
| **Time** | 1.8 min | 3.3 min |
| **Energy** | 8.3 Wh | 12.6 Wh (52% more) |
| **Target pixel size** | 34 px | 49 px |
| **Speed** | 10 m/s | 8 m/s |
| **Decision** | Energy analysis favours 50 m for fastest initial sweep (34 px is above the 20 px detection threshold). 35 m is the conservative operational default for initial flights, prioritising detection confidence. TARGET_ALT can be raised to 50 m after first-flight validation. |

### 9.8 Energy vs Thoroughness

Fewer scan lines save energy and time but reduce overlap between passes. At 50 m with 0%
explicit overlap, the diagonal realignment provides the coverage bonus (Section 2.3). The
tradeoff is acceptable because the rescan mechanism (Section 2.5) catches misses at lower
altitude. Spending extra energy on a thorough first pass is wasteful if the target is found
on pass 1 (the common case).

### 9.9 NFZ Scalar Field Zone Width (20 m)

| Width | Behaviour | Problem |
|-------|-----------|---------|
| 10 m | Speed ramp from 3 m/s to 0.3 m/s over 10 m | Marginal stopping distance at 10 m/s approach |
| **20 m (chosen)** | 2x worst-case stopping distance | Smooth deceleration, ample margin |
| 30 m | Very conservative | Wastes 30% of scan lines in slow zone, excessive time penalty |

See Section 3.3 for full stopping distance derivation.

### 9.10 Why U-Turns Are Not Smoothed by Default

Smoothing U-turns (e.g., Dubins paths or arc transitions) would reduce the 2-second
deceleration/reacceleration penalty per turn. However:

- At 6-9 scan lines, there are only 5-8 U-turns total -- saving 2 s each = 10-16 s
- Implementing smooth turns adds complexity to `planning.py` and the waypoint format
- ArduCopter's WP_NAVALT_TURN parameter already provides some corner smoothing
- The energy saving is minimal compared to the altitude choice (Section 9.7)

Not worth the complexity for a single-digit second improvement.

---

## 10. What We Are Still Working On

These are active or planned improvements that have not yet been implemented:

1. **Full momentum-aware path optimisation:** The current energy model (Section 2.7) uses
   a fixed 2-second U-turn penalty. A full simulation would model acceleration/deceleration
   profiles, wind resistance, and bank angle constraints to find truly optimal scan
   parameters.

2. **NCNN backend testing on Pi:** NCNN export is available in
   `cv_models/sar_v2_1088/ncnn/` and is expected to reach ~15 FPS on the Pi 5 (3x current
   TFLite speed). Needs on-device benchmarking and validation that detection quality is
   preserved.

3. **INT8 quantisation:** Quantising the TFLite model from float32 to INT8 would halve
   model size and may improve inference speed on the Pi's CPU. Requires a representative
   calibration dataset to avoid accuracy loss.

4. **Multi-class detection:** The current model detects a single class (dummy). Extending
   to dummy + person + cone would allow the system to distinguish between casualty types
   and reduce false positives from non-target objects.

5. **Adaptive search:** After the first pass, use detection heatmaps and terrain features
   to focus subsequent passes on high-probability regions rather than repeating the full
   lawnmower pattern.

6. **Wind compensation in GPS estimation:** The GPS timing lag (Section 5.4) causes
   along-track error proportional to speed. Compensating by offsetting the GPS position
   by `speed * lag` in the heading direction would reduce CEP by an estimated 30-50%.

---

## References

All numeric values in this document are drawn from `config.py` as deployed. Source files
are listed in Section 1.1. Design decision documents with full implementation details:

- `docs/DESIGN_DETECTION.md` -- detection pipeline (DD-1 through DD-10)
- `docs/DESIGN_GEOFENCE.md` -- NFZ three-layer protection
- `docs/DESIGN_PATH_PLANNING.md` -- lawnmower pattern and scan angle optimisation
- `docs/DESIGN_STATE_MACHINE.md` -- state definitions, transitions, timeouts
- `docs/DESIGN_VISION.md` -- CV subsystem, model training, GPS estimation
