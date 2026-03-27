# SAR Drone -- Comprehensive Design Summary (v2)

**Project:** AENGM0074 Group Project in Aerial Robotics, University of Bristol MSc
**Team:** 5 members
**Platform:** Hexsoon EDU-450 + Cube Orange + Raspberry Pi 5 + IMX296 global shutter camera

The drone takes off, flies a lawnmower search pattern over a designated survey area,
uses onboard AI (YOLOv8n / TFLite) to detect a casualty dummy, presents detections to
a ground-station operator for confirmation, delivers a first aid kit near the confirmed
target, and returns home. The survey area sits adjacent to an SSSI no-fly zone, which
shapes many of the design choices below.

---

## Quick Facts

| # | Fact | Value |
|---|------|-------|
| 1 | AI model | YOLOv8n (nano), single class ("dummy"), TFLite float32 |
| 2 | Inference speed (Pi 5) | **206 ms / 4.8 FPS** (XNNPACK CPU) |
| 3 | Model accuracy | **mAP50 = 0.995** (v2 model, 366 training images) |
| 4 | Search altitude | **35 m** default, rescans at 28 m then 22 m |
| 5 | Search speed | **8 m/s** at 35 m (linear: 6 m/s at 20 m, 10 m/s at 50 m) |
| 6 | Camera | IMX296 global shutter, **1456 x 1088**, f = **5.46 mm** |
| 7 | GPS estimation accuracy | **CEP50 = 2.3 m** (from DJI flight video, 143 estimates) |
| 8 | Confidence threshold | **0.2** (low on purpose -- operator filters false positives) |
| 9 | NFZ protection | 3 layers: speed cap + repulsive push + Cube firmware geofence |
| 10 | Compute platform | Raspberry Pi 5 (4 GB), Python 3.13, ai-edge-litert |

---

## 1. Mission and Requirements

### 1.1 Scenario

A lost hiker in Fenswood Wilderness. Mid-search (5-15 min in) they activate a Personal
Locator Beacon (PLB) giving a Focus Area. The search region contains an SSSI (Site of
Special Scientific Interest) no-fly zone with rare nesting birds.

### 1.2 Requirements Table

| R | Requirement | How We Meet It |
|---|-------------|----------------|
| R01 | Fly only within Flight Area | Software geofence (3-layer) + Cube firmware geofence |
| R02 | Do not fly over SSSI | Speed cap + repulsive push + hard cutoff to MANUAL |
| R03 | Take off within 5 m of Take-Off Location | KML-loaded coordinates, GPS-verified before arm |
| R04 | Max altitude 50 m AGL | `TARGET_ALT = 35 m` default, ceiling enforced in config |
| R05 | Search area, identify items of interest | Lawnmower scan + YOLOv8n detection + operator classification (Y/N/I/X) |
| R06 | On PLB, receive Focus Area, refocus search | B key or `--beacon-delay N`; loads focus polygon, regenerates pattern |
| R07 | Land within 10 m but not within 5 m of casualty, deploy first aid kit, RTH | 7.5 m offset landing + two-stage servo release + return transit |
| R08 | Justify level of autonomy and interface | Operator-in-the-loop verification; web dashboard; documented rationale |
| R09 | RTH and motor cutoff + failsafes | RTH button (software + RC), RC kill switch, link-lost RTL |
| R10 | Report lat/lon and images of detections | Detection log with GPS, confidence, timestamps; snapshot images saved |
| R11 | Designated Company Pilot + Safety Pilot | Safety pilot has RC override authority at all times |
| R12 | Public GitHub, MIT licence | https://github.com/DimaChup/Group_Proj.git, MIT licence |

### 1.3 STEEPLE Summary

| Factor | Key Consideration | Design Influence |
|--------|-------------------|------------------|
| Social | Volunteer SAR teams face coverage gaps | Low-cost, easy-to-deploy, open-source platform |
| Technological | Edge AI on embedded hardware; open autopilot | Pi 5 + YOLOv8n/TFLite; ArduPilot GUIDED mode |
| Economic | University budget; no cloud costs | Sub-GBP 500 compute stack; free Colab training |
| Environmental | SSSI wildlife sensitivity; battery lifecycle | 3-layer software geofence; electric propulsion |
| Political | UK push for civilian drone adoption | Aligns with CAA innovation sandbox; transparent release |
| Legal | CAA Open Category A3; VLOS; GDPR | Operator-in-the-loop; on-device inference; MIT licence |
| Ethical | Autonomous decisions affecting human life | Human confirmation before descent; no persistent image storage |

---

## 2. System Architecture

### 2.1 Module Map

```
                    config.py
                 (all parameters)
                       |
          +------------+------------+
          |            |            |
      vision.py   planning.py   geofence.py
      (camera+AI)  (lawnmower)   (NFZ boundary)
          |            |            |
          +-----+------+------+-----+
                |             |
            utils.py     navigation.py
           (geo math)   (MAVLink cmds)
                |             |
                +------+------+
                       |
                 state_machine.py
                (state handlers)
                       |
                    main.py
              (mission orchestrator)
                       |
              +--------+--------+
              |                 |
         MJPEG stream      terminal/browser
        (port 8090)         (Y/N/M keys)
```

**Key principle:** `vision.py` is the ONLY file that touches CV/AI. Everything else
calls `detect_in_image(frame)` which returns `(found, x, y, conf)`. The model,
preprocessing, or backend can change without touching any other file.

**Other scripts:**
- `pi_flight.py` -- web-based ground station with browser dashboard (headless on Pi)
- `passive_watch.py` -- passive camera observer, sends zero commands (safe always)
- `simple_simulator.py` -- interactive keyboard-flight simulator (laptop only)

### 2.2 File Responsibilities

| File | Responsibility |
|------|---------------|
| `config.py` | Every tunable parameter: altitudes, speeds, camera, NFZ, connection strings. KML loader for zone coordinates. |
| `states.py` | State enum (`SEARCH`, `VERIFY`, `LANDING`, etc.) |
| `vision.py` | Camera + AI detection. Dual backend: Ultralytics on laptop, TFLite on Pi. Lens undistortion. |
| `planning.py` | Lawnmower search pattern generator from arbitrary polygons. Returns `[(lat, lon), ...]`. |
| `utils.py` | Geo math: GPS-to-pixel and pixel-to-GPS conversion (`GeoTransformer`) |
| `navigation.py` | MAVLink command abstraction: goto, set_speed, send_velocity, land, arm |
| `geofence.py` | NFZ boundary distance, repulsive offset, inner polygon geometry |
| `state_machine.py` | All state handler methods (mixin class inherited by main mission) |
| `main.py` | Mission orchestrator: connects modules, runs main loop, dispatches states |

### 2.3 Platform Auto-Detection

`config.py` auto-detects the hardware environment:
- Serial port present (`/dev/ttyAMA0`) --> Pi with Cube --> connect via mavproxy UDP bridge
- WSL detected --> connect via gateway IP to Windows SITL
- Default --> localhost SITL on Windows

Same code runs on laptop (simulation), Pi (real flight), and WSL (Linux testing). The
only difference is which `requirements_*.txt` is installed.

---

## 3. Key Design Decisions

### 3.1 Finite State Machine Architecture

**Chosen:** Explicit FSM with dispatch dictionary mapping `State` enum to handler methods.
**Rejected:** Behaviour trees (more complex, harder to audit), sequential script (no timeout safety).

| Property | Benefit |
|----------|---------|
| Deterministic | Exactly one state at all times. Transition is a pure function of (state, inputs, commands). |
| Timeout safety | Every blocking state has a wall-clock timeout. No state can hang indefinitely. |
| Operator override | M key or RC switch interrupts any state. Machine records where it was and resumes. |

### 3.2 Lawnmower Search Pattern

**Chosen:** Boustrophedon (lawnmower) scan (Choset, 2001).
**Rejected:** Expanding spiral (biased toward centre, edges under-covered), sector search (requires known last-seen point).

The planner handles arbitrary polygons by rasterising with `cv2.fillPoly` onto a binary
mask, then reading non-zero pixel runs from each row. `cv2.minAreaRect` finds the optimal
scan angle (65-75 degrees for the AENGM0074 polygon, aligned with NE-SW axis) to minimise
scan lines.

### 3.3 YOLOv8n on TFLite

**Chosen:** YOLOv8n (nano) exported to TFLite float32, running on XNNPACK CPU delegate.
**Rejected:** YOLOv8s (~2.5 FPS, halves frame rate), YOLOv8m (~1.2 FPS, impractical).

At 4.8 FPS and 6-10 m/s, the target appears in 11-17 consecutive frames per flyover.
A single detection above threshold triggers investigation.

### 3.4 Dual-Backend Vision System (DD-03)

**Chosen:** Single `vision.py` with auto-detection -- tries NCNN first, then Ultralytics, then TFLite.
**Why:** Same code runs on both platforms. No `if platform == ...` scattered everywhere.

On Pi: Ultralytics is not installed (it pulls in PyTorch at 2+ GB). Inference falls through to TFLite.
On laptop: Ultralytics provides GPU acceleration and richer debugging.

### 3.5 MJPEG Streaming (DD-01)

**Chosen:** MJPEG over HTTP (pure OpenCV `imencode()`).
**Rejected:** H.264/GStreamer (extra dependencies, doesn't work in plain browser), WebRTC (overkill at 3 FPS).

Works in any browser, zero extra dependencies, stateless. Our inference is only 3-5 FPS --
low-latency streaming is irrelevant when AI processes 3 frames per second.

### 3.6 mavproxy UDP Bridge (DD-04)

**Chosen:** mavproxy reads serial, forwards via UDP.
**Rejected:** Direct pyserial (broken on Python 3.13, bytes dropped).

Also gives free Mission Planner connectivity via TCP. Scripts connect to `udpin:0.0.0.0:14550`.

### 3.7 Headless Operation (DD-02)

**Chosen:** SSH + headless flags. All visual output via MJPEG web stream, never `cv2.imshow`.
**Rejected:** Attaching monitor to Pi on field, VNC (adds latency/complexity).

### 3.8 Low Confidence Threshold (0.2) with Cost Asymmetry

**Chosen:** `CONFIDENCE_THRESHOLD = 0.2` -- deliberately low.
**Why:** Cost asymmetry is 10:1. A false positive costs ~10 seconds (operator presses N).
A missed target costs 2-5 minutes (full rescan). Real detections score 0.8-0.95; false
positives from terrain/shadows fall in 0.2-0.4. Deduplication (rejection radius, NFZ filter,
boundary filter) prevents FP flooding.

### 3.9 FIFO Detection Queue

**Chosen:** FIFO order.
**Rejected:** Priority by confidence (same object scores differently from different angles -- misleading).

`_pop_valid_target()` re-validates each entry against NFZ boundary, search area, and
proximity to known targets. Invalid entries silently skipped.

### 3.10 7.5 m Offset Landing (DD-09)

**Chosen:** After GPS lock, fly 7.5 m north and land there.
**Why:** Drone must not land on casualty (propwash, crash risk). 7.5 m gives safe separation.
"North" is arbitrary but consistent.

### 3.11 NFZ Speed Cap over Velocity Commands (DD-10)

**Chosen:** `DO_CHANGE_SPEED` to cap autopilot speed + inner polygon repulsive push.
**Rejected:** Velocity commands toward waypoint (fought position controller, caused oscillation);
velocity commands away from boundary (jittery, duplicated autopilot logic).

See Section 5 for full NFZ design.

---

## 4. How It Works

### 4.1 State Machine Flow

```
                    +-- MANUAL OVERRIDE (M key, any state) --+
                    |  MANUAL -> RETURN_FROM_MANUAL -> resume |
                    +----------------------------------------+

 INIT -> CONNECTING -> ARMING -> TAKEOFF
                                    |
                              [alt reached]
                                    |
                        (transit waypoints?)---yes---> PRE_WAYPOINTS
                                    |                       |
                                    no                      |
                                    |                       v
                           TRANSIT_TO_SEARCH <--------------+
                                    |
                              [at search area]
                                    |
                                 SEARCH  <-- rescan (drop alt) <--+
                                 /    \                            |
                    [detection] /      \ [all WPs done,           |
                               /        \ no confirm] ------------+
                            CENTERING     (pass < MAX_RESCAN_PASSES)
                               |
                          [dist < 2.5m]
                               |
                            VERIFY (120s timeout -> reject)
                            / | \
                       [Y]  [N/I]  [timeout]
                        |     |
                   APPROACH  queue pop -> CENTERING
                        |    or RETURN_TO_SEARCH -> SEARCH
                   HOVER_TARGET (servo release, 15s)
                        |
               RETURN_TRANSIT -> RETURN_HOME -> LANDING -> DONE
```

**All 19 states** (from `states.py`): INIT, CONNECTING, ARMING, TAKEOFF, PRE_WAYPOINTS,
TRANSIT_TO_SEARCH, SEARCH, CENTERING, DESCENDING, VERIFY, HOVER, APPROACH,
RETURN_TO_SEARCH, RETURN_FROM_MANUAL, HOVER_TARGET, RETURN_TRANSIT, RETURN_HOME, LANDING,
MANUAL, DONE.

### 4.2 Typical Mission Timeline

| Phase | Duration | Notes |
|-------|----------|-------|
| TAKEOFF | ~30 s | Climb to 35 m |
| TRANSIT | ~2 min | 294 m at 8 m/s |
| SEARCH (pass 1) | ~3.3 min | 18 waypoints at 35 m |
| CENTERING + VERIFY | ~30 s | Per detection |
| APPROACH + DELIVER | ~45 s | Descend to 3 m, two-stage servo release |
| RETURN | ~2 min | Retrace transit |
| LANDING | ~30 s | Auto-land at home |
| **Total** | **~10-12 min** | Single pass, one target |

### 4.3 CV Pipeline

Every frame passes through this pipeline regardless of backend:

```
Frame capture (picamera2 / cv2.VideoCapture)
    |
1. Lens undistortion          ~1.5 ms    (cv2.remap, precomputed maps)
    |
2. Colour conversion          ~0.3 ms    (BGR -> RGB)
    |
3. Resize to 640x640          ~0.5 ms    (bilinear interpolation)
    |
4. Normalise to [0, 1]        ~0.2 ms    (float32 / 255)
    |
5. TFLite invoke               ~206 ms   (XNNPACK CPU delegate)
    |
6. Output parsing              ~0.1 ms   (transpose, threshold, NMS)
    |
7. Coordinate scaling          ~0.0 ms   (normalised -> frame pixels)
    |
Result: (found, x, y, conf)   Total: ~208 ms = 4.8 FPS
```

Step 5 dominates at 99% of total time.

**Model I/O:**
- Input: `[1, 640, 640, 3]` float32
- Output: `[1, 5, 8400]` transposed to `[8400, 5]` where each row = `[cx, cy, w, h, class_conf]`
- 8400 candidates from three scales (80x80 + 40x40 + 20x20)
- Single class: "dummy"
- **Coordinate guard:** YOLOv8 TFLite exports may output normalised (0-1) or pixel (0-640)
  coordinates depending on export config. A runtime check (`if raw_cx > 1.5`) handles both.

### 4.4 GPS Position Estimation

Three-stage pipeline of increasing accuracy:

| Stage | When | Method | CEP |
|-------|------|--------|-----|
| 1. Trigonometric estimate | Flyover during SEARCH | Pixel offset x GSD x heading rotation -> GPS delta | ~5 m |
| 2. Centering refinement | CENTERING state (hover above) | Re-detection with near-zero pixel offset | ~2 m |
| 3. GPS averaging (optional) | `--center-verify` during VERIFY | 10 s of readings (~100 samples) | ~1 m |

**Core formulas:**

```
GSD = (SENSOR_WIDTH_MM * altitude) / (FOCAL_LENGTH_MM * IMAGE_W)
    = (5.02 * h) / (5.46 * 1456) = h * 6.315e-4   [m/px]

offset_x_m = (px - IMAGE_W/2) * GSD
offset_y_m = (py - IMAGE_H/2) * GSD
offset_north = offset_x_m * cos(yaw) - offset_y_m * sin(yaw)
offset_east  = offset_x_m * sin(yaw) + offset_y_m * cos(yaw)
target_lat = drone_lat + offset_north / 111132.954
target_lon = drone_lon + offset_east / (111132.954 * cos(drone_lat))
```

**Dominant error sources:** GPS receiver latency (~1 m at 6 m/s), GPS position noise
(2-3 m CEP50), attitude uncertainty (variable).

### 4.5 Search Strategy Details

**Diagonal realignment (53-degree trick):** Camera diagonal (1818 px) is 1.67x the height
(1088 px). By yawing 53 degrees, the effective swath increases by 67% at zero extra cost.
Configurable via `DIAGONAL_YAW_OFFSET_DEG` (currently 0, set to `None` for auto-compute).

**Altitude strategy:** Start at 35 m, drop 20% per rescan pass:
- Pass 1: 35 m (48 px target in model)
- Pass 2: 28 m (60 px)
- Pass 3: 22 m (76 px)
- Floor: 15 m (100+ px)

**Speed vs altitude:** Linear interpolation -- 6 m/s at 20 m, 10 m/s at 50 m. Slower at
lower altitudes to preserve frame quality (less angular rate = less blur).

**Focus Area (PLB redirect):** On beacon signal, load focus polygon from JSON, regenerate
lawnmower pattern, drop speed to 5 m/s. Preserves all rejected targets from broad search.

### 4.6 Detection Queue and Target Management

- Detections appended to FIFO queue, investigated in order
- 5 m lock radius during CENTERING (GPS noise margin)
- 5 m rejection radius after operator presses N/I (prevents re-investigation)
- NFZ and search area boundary filtering at detection time AND dispatch time
- Single detection per frame (highest confidence) -- prevents queue flooding from overlapping boxes
- Detection continues during manual mode; targets queued for later

### 4.7 Payload Delivery

After operator confirms (Y), the drone flies to 7.5 m north of target, descends to 3 m:

| Time | Action | Servo PWM |
|------|--------|-----------|
| 0 s | Arrive at 3 m hover | 1500 (closed) |
| 3 s | Stage 1: partial release | 1300 |
| 6 s | Stage 2: full release | 1100 |
| 15 s | Close servo, depart | 1500 (closed) |

---

## 5. Safety Systems

### 5.1 NFZ Geofence -- Defence in Depth (3 Layers)

The SSSI is adjacent to the search area. Three independent layers prevent incursion:

| Layer | Type | Runs On | What It Catches |
|-------|------|---------|----------------|
| **Speed cap** (scalar field) | Software | Pi | Prevents high-speed overshoot during waypoint following |
| **Repulsive push** (vector field) | Software | Pi | Deflects drone if speed cap alone is insufficient |
| **Cube firmware geofence** | Hardware | Flight controller | Triggers LOITER/RTL if software layers fail entirely |

If the Pi crashes, the Cube geofence still works. If the firmware geofence is
misconfigured, the software layers still enforce the boundary.

**Speed cap profile (20 m buffer zone):**

| Distance from NFZ | Speed limit |
|-------------------|-------------|
| 20 m (entering zone) | 3.0 m/s |
| 10 m | 1.65 m/s |
| 0 m (at boundary) | 0.3 m/s (near-stop) |
| > 20 m | Normal (6-10 m/s) |

**Why 20 m:** Stopping from 10 m/s at WPNAV_ACCEL = 2.5 m/s^2 takes ~20 m. The buffer
matches worst-case stopping distance.

**Repulsive push:** Constant 3 m/s push away from NFZ when within 3 m of boundary. Active
as last resort even if speed cap fails or drone blown by wind.

**Auto-MANUAL on NFZ entry:** If GPS falls inside SSSI (or within 3 m), software halts
the drone, saves state, switches to MANUAL, prints warning. Operator flies out manually.

### 5.2 Kill Switch and RC Override

- RC transmitter mode switch to STABILIZE/LOITER disconnects companion computer entirely
- Pilot has full stick authority; only firmware geofence remains active
- M key in software provides manual override with state save/restore
- Link-lost failsafe triggers RTL automatically

### 5.3 Operator-in-the-Loop Verification

The drone never autonomously confirms a target. On detection:
1. Drone centres above detection
2. Presents live video + detection overlay to operator
3. Operator must press Y (confirm), N (reject), or I (item of interest)
4. Only Y triggers approach and payload delivery

This was a deliberate ethical choice: rejecting fully autonomous target confirmation
despite the time cost, because false-positive actions (landing near uninvolved person)
or false negatives (abandoning real casualty) have disproportionate consequences.

### 5.4 Progressive Test Strategy (DD-07)

Never skip a step. Each step isolates one new variable:

1. Mission Planner AUTO waypoints (no custom code)
2. Waypoint test script (no CV)
3. Manual flight + passive CV (zero commands)
4. Autonomous search + CV logging only (no action)
5. Full autonomous mission

---

## 6. Results and Benchmarks

### 6.1 Pi 5 Inference Benchmarks

All measured on Raspberry Pi 5, Python 3.13, ai-edge-litert with XNNPACK CPU delegate.

| Model | Size | Undistort | Avg Inference | FPS | Detection Rate | Avg Confidence |
|-------|:----:|:---------:|:------------:|:---:|:--------------:|:--------------:|
| best.tflite (v1) | 3.2 MB | No | 206.5 ms | 4.8 | 30/30 (100%) | 0.966 |
| best.tflite (v1) | 3.2 MB | Yes | 208.0 ms | 4.8 | 30/30 (100%) | 0.958 |
| sar_v2_1088 | 11.7 MB | No | ~206 ms | 4.8 | 30/30 (100%) | 0.966 |

Lens undistortion adds only 1.5 ms (0.7% overhead). Both model versions are drop-in
replacements with identical input/output shapes.

**Projected speedups (not yet tested):**

| Backend | Expected FPS | Effort | Notes |
|---------|:-----------:|:------:|-------|
| TFLite XNNPACK FP16 | ~10 | Low | Pi 5 has native FP16 (ARMv8.2-A) |
| NCNN FP32 | ~15 | Medium | Export available in `cv_models/sar_v2_1088/ncnn/` |
| Threaded capture + inference | +20-30% | Low | Producer-consumer pipeline |

### 6.2 Training Data and Model Performance

| Version | Resolution | Images | Real Frames | Negatives | mAP50 |
|---------|:----------:|:------:|:-----------:|:---------:|:-----:|
| v1 | 640 x 640 | 200 | 0 | 0 | ~0.95 |
| **v2 (current)** | **1456 x 1088** | **366** | **16** | **50** | **0.995** |

v2 dataset: 300 synthetic (dummy composited on real DJI video backgrounds with altitude-correct
scaling + augmentation), 16 real labelled frames from DJI flight video, 50 negatives (empty
scenes to suppress false positives). Trained on Google Colab T4 GPU, 150 epochs.

### 6.3 Camera and Optics

| Parameter | Value | Source |
|-----------|-------|--------|
| Sensor | Sony IMX296 (global shutter) | Eliminates rolling-shutter artefacts |
| Sensor width | 5.02 mm | Datasheet |
| Focal length | 5.46 mm | Calibrated: 92 cm visible at 1 m |
| Resolution | 1456 x 1088 | Pi camera native mode |
| HFOV (Pi camera) | 49.4 deg | Computed from sensor geometry |
| Lens calibration RMS | 0.399 | Checkerboard calibration |
| Colour output | BGR (despite RGB888 label) | Empirical testing of all 6 permutations |

### 6.4 Ground Footprint and Target Size

| Altitude | Footprint W x H | GSD (m/px) | Dummy in Model Input (px) | Detectable? |
|:--------:|:----------------:|:----------:|:-------------------------:|:-----------:|
| 20 m | 18.4 x 13.7 m | 0.013 | 84 px tall | Yes -- large |
| 35 m | 32.2 x 24.0 m | 0.022 | 48 px tall | Yes -- adequate |
| 50 m | 46.0 x 34.3 m | 0.032 | 34 px tall | Marginal (above 20 px floor) |

**Detection threshold:** YOLOv8n needs ~15-20 px in the smallest dimension. The dummy drops
below 20 px at ~85 m altitude. The operational range (20-50 m) keeps target size at 34-84 px.

### 6.5 Motion Blur Analysis

Global shutter eliminates rolling-shutter artefacts. At operational speeds (6-10 m/s)
with 1/1000 s exposure, motion blur is 0.2-0.8 pixels -- sub-pixel and invisible to the
detector. Critical speed where blur exceeds 1 pixel at 35 m: 22.1 m/s (well above max
drone speed). **Motion blur is not a limiting factor.**

### 6.6 Frame Coverage

At 4.8 FPS, the target appears in multiple consecutive frames at every altitude:

| Altitude | Speed | Footprint H | Frames in View | Frame Overlap |
|:--------:|:-----:|:-----------:|:--------------:|:-------------:|
| 20 m | 6.0 m/s | 13.7 m | 11 | 91% |
| 35 m | 8.0 m/s | 24.0 m | 14 | 93% |
| 50 m | 10.0 m/s | 34.3 m | 17 | 94% |

A target at 35 m / 8 m/s would need to be moving at 115 m/s to appear in only 1 frame --
physically impossible. Frame coverage is never the limiting factor.

### 6.7 GPS Estimation from Video Analysis

From DJI flight video analysis (143 detection estimates):
- **CEP50 = 2.3 m** (half of estimates within 2.3 m of actual)
- Max outlier: 16.5 m (caused by GPS timing lag at high speed)
- GPS receiver has 100-200 ms latency --> 1 m error at 5 m/s along-track

### 6.8 Summary of Limiting Factors

| Factor | Limiting? | Reason |
|--------|:---------:|--------|
| Motion blur | **No** | Global shutter + 1/1000 s exposure = sub-pixel at all speeds |
| Target pixel size (<40 m) | **No** | Dummy > 42 px in model input |
| Target pixel size (50 m) | **Marginal** | 34 px, above 20 px floor |
| Inference FPS | **No** | 4.8 FPS gives 11-17 frames per flyover |
| Frame overlap | **No** | 91-94% at all operational altitudes |
| GPS estimation | **Yes** | CEP50 = 2.3 m, dominated by GPS receiver lag |

**The real operational limit is altitude, not speed or blur.** Above ~85 m, detection
becomes unreliable. Speed could theoretically increase to 15+ m/s without impacting
detection, but GPS estimation accuracy would degrade due to GPS timing lag.

### 6.9 Energy Analysis

| Altitude | Scan Lines | Time | Energy | Speed |
|----------|:---------:|:----:|:------:|:-----:|
| 50 m | 6 | 1.8 min | 8.3 Wh | 10 m/s |
| 35 m | 9 | 3.3 min | 12.6 Wh | 8 m/s |

Energy model: `P_total = P_hover + P_drag = 150 W + 50 W * (v/5)^2`. Each U-turn
incurs a 2-second momentum penalty. NFZ slow zone adds ~45% time on affected segments.

---

## 7. What Is Not Done Yet

Honest assessment of remaining work:

1. **No full outdoor autonomous flight test.** Simulation works end-to-end. Pi hardware
   (camera, AI, Cube connection) all verified individually. Weather cancelled the planned
   flight day. Progressive test steps 1-3 partially completed (bench only).

2. **NCNN backend not tested on Pi.** Export available in `cv_models/sar_v2_1088/ncnn/`,
   expected ~15 FPS (3x current). Needs on-device benchmarking.

3. **FP16 / INT8 quantisation not tested.** Pi 5 has native FP16 support -- expected ~2x
   speedup for free. Not yet benchmarked.

4. **GPS lag compensation not implemented.** Known fix: offset GPS by `speed * lag` in
   heading direction. Would reduce CEP by an estimated 30-50%.

5. **Multi-class detection not implemented.** Current model detects only "dummy" class.
   Extending to dummy + person + cone would reduce false positives.

6. **Limited real training data.** Only 16 real labelled frames in v2 dataset. More real
   frames (target: 50-100) would reduce overfitting to synthetic data.

7. **Train/val split overlap.** The small dataset (366 images) has overlapping train/val
   sets. mAP50 of 0.995 may be optimistic. Real-world performance validated by Pi
   benchmark and DJI video analysis instead.

---

## 8. Key Config Parameters

All in `config.py`. These are the values that matter most:

### 8.1 Flight

| Parameter | Value | Name |
|-----------|-------|------|
| Search altitude | 35.0 m | `TARGET_ALT` |
| Verify altitude | 15.0 m | `VERIFY_ALT` |
| Speed at 20 m | 6.0 m/s | `SPEED_AT_LOW` |
| Speed at 50 m | 10.0 m/s | `SPEED_AT_HIGH` |
| Transit speed | 15.0 m/s | `TRANSIT_SPEED_MPS` |
| Focus area speed | 5.0 m/s | `FOCUS_SEARCH_SPEED_MPS` |

### 8.2 Camera

| Parameter | Value | Name |
|-----------|-------|------|
| Sensor width | 5.02 mm | `SENSOR_WIDTH_MM` |
| Focal length | 5.46 mm | `FOCAL_LENGTH_MM` |
| Resolution | 1456 x 1088 | `IMAGE_W`, `IMAGE_H` |
| Camera inverted | Yes | `CAMERA_FLIP_180` |

### 8.3 Detection

| Parameter | Value | Name |
|-----------|-------|------|
| Confidence threshold | 0.2 | `CONFIDENCE_THRESHOLD` |
| Lock radius | 5.0 m | `DETECT_LOCK_RADIUS_M` |
| Rejection radius | 5.0 m | `REJECTED_TARGET_RADIUS_M` |
| Confirm frames | 3 (off by default) | `DETECT_CONFIRM_FRAMES` |

### 8.4 NFZ Geofence

| Parameter | Value | Name |
|-----------|-------|------|
| Slow zone width | 20.0 m | `NFZ_SLOW_ZONE_M` |
| Min speed at boundary | 0.3 m/s | `NFZ_MIN_SPEED_MPS` |
| Zone max speed | 3.0 m/s | `NFZ_ZONE_MAX_SPEED_MPS` |
| Push speed | 3.0 m/s | `NFZ_PUSH_SPEED_MPS` |
| Hard boundary | 3.0 m | `NFZ_HARD_BOUNDARY_M` |

### 8.5 Search Strategy

| Parameter | Value | Name |
|-----------|-------|------|
| Max rescan passes | 3 | `MAX_RESCAN_PASSES` |
| Altitude drop per pass | 0.8x | `RESCAN_ALT_FACTOR` |
| Altitude floor | 15.0 m | `RESCAN_ALT_FLOOR_M` |
| Diagonal yaw offset | 0 (disabled) | `DIAGONAL_YAW_OFFSET_DEG` |

### 8.6 Payload

| Parameter | Value | Name |
|-----------|-------|------|
| Servo channel | 9 | `SERVO_CHANNEL` |
| Close PWM | 1500 | `SERVO_CLOSE_PWM` |
| Partial release PWM | 1300 | `SERVO_PARTIAL_PWM` |
| Full release PWM | 1100 | `SERVO_FULL_PWM` |

---

## 9. How to Run

### 9.1 Quick Start

```bash
# Dry-run (no GPS, no Cube, no flying -- verifies pattern + state machine)
python main.py --dry-run

# Simulation (laptop -- needs SITL running in Mission Planner or mavproxy)
set DRONE_MODE=SIMULATION      # Windows
python main.py

# Real mode on Pi
source pienv/bin/activate
cd ~/sar-drone
python main.py                 # config.py auto-detects Cube
```

### 9.2 Useful Flags

| Flag | Effect |
|------|--------|
| `--dry-run` | Print waypoints + state walkthrough, no hardware needed |
| `--model PATH` | Use alternative TFLite model |
| `--headless` | No cv2.imshow, all output via web stream (auto on Pi) |
| `--smart-detect` | Require 3 consecutive detections before triggering |
| `--nfz-carrot` | Enable NFZ speed cap + repulsive push (recommended) |
| `--beacon-delay N` | Simulate PLB activation after N seconds |
| `--center-verify` | 10 s GPS averaging during VERIFY |

### 9.3 Ground Station

During flight, open browser to `http://<PI_IP>:8090` for:
- MJPEG video stream with detection overlay
- 2D GPS grid with detection clusters
- Command buttons: Y (confirm), N (reject), I (interest), X (false positive), L (land)

### 9.4 Model Swapping

All scripts read `best.tflite` from project root. To swap:
```bash
cp cv_models/sar_v2_1088/best.tflite best.tflite
```
No code changes needed. All TFLite models have identical input/output shapes.

---

## 10. Key Tradeoff Summary

| Decision | Chosen | Rejected | Why |
|----------|--------|----------|-----|
| Search pattern | Lawnmower | Spiral, sector | Complete coverage, standard in SAR |
| Model size | YOLOv8n (4.8 FPS) | YOLOv8s (1.5 FPS) | 11-17 frames per target is sufficient |
| Detection trigger | Single frame | Multi-frame (3) | Miss cost (minutes) >> FP cost (10 s) |
| Confidence threshold | 0.2 (low) | 0.4+ | 10:1 cost asymmetry favours recall |
| Queue order | FIFO | Priority by confidence | Confidence varies by angle -- unreliable |
| NFZ method | Speed cap (carrot) | Velocity commands | Tested both; velocity caused oscillation |
| Scan overlap | 0% explicit | 20% | Diagonal realignment gives 67% bonus for free |
| Start altitude | 35 m (conservative) | 50 m (optimal) | Prioritise detection confidence for initial flights |
| Verification | Stay at altitude | Descend to 15 m | Saves 40 s per detection; camera FOV sufficient |
| Streaming | MJPEG | H.264/WebRTC | Zero dependencies; 3 FPS makes low-latency irrelevant |
| Landing offset | 7.5 m north | On target | Safety: propwash, crash risk |

---

## References

- ArduPilot (2024). "ArduCopter GUIDED Mode Commands." https://ardupilot.org/copter/docs/common-mavlink-mission-command-messages-mav_cmd.html
- Choset, H. (2001). "Coverage of Known Spaces: The Boustrophedon Cellular Decomposition." *Autonomous Robots*, 9(3), 247-253.
- Jocher, G. et al. (2023). "Ultralytics YOLOv8." https://github.com/ultralytics/ultralytics

---

## Internal Source Documents

Detailed design documents for each subsystem:

- `docs/DESIGN_DECISIONS.md` -- DD-01 through DD-10 with full rationale
- `docs/DESIGN_DETECTION.md` -- detection pipeline
- `docs/DESIGN_GEOFENCE.md` -- NFZ three-layer protection
- `docs/DESIGN_PATH_PLANNING.md` -- lawnmower pattern and scan angle optimisation
- `docs/DESIGN_STATE_MACHINE.md` -- state definitions, transitions, timeouts
- `docs/DESIGN_VISION.md` -- CV subsystem, model training, GPS estimation
- `docs/DESIGN_SUMMARY.md` -- v1 of this document (1600 lines, full derivations for vision optics, NFZ math, key formulas, and future improvement tables)
