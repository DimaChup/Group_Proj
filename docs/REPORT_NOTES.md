# Report Notes -- SAR Drone Sections 6-8

Structured notes mapping directly to the LaTeX report. Written in technical report style
with actual numbers. Adapt into LaTeX paragraphs as needed.

---

## Section 6: Path and Mission Planning

### 6.1 Algorithm Selection

Three candidate path planning algorithms were evaluated for the SAR search pattern:

| Criterion | Lawnmower (Boustrophedon) | Expanding Spiral | Sector Search |
|-----------|--------------------------|-----------------|---------------|
| Coverage guarantee | Complete -- every cell visited | Biased toward centre; edges under-covered | Requires known last-seen point |
| Computation | Trivial (offline) | Simple (offline) | Depends on prior info |
| Heritage | Standard in SAR literature (JSAR manual) | Limited SAR precedent | Not applicable without prior info |
| Replanning | Easy -- shift legs between passes | Must restart from centre | Must have updated last-seen position |

**Selected: boustrophedon (lawnmower) raster.** The survey area has no prior information on
casualty location, ruling out sector search. Expanding spiral under-covers edges where the
dummy is equally likely to be. The lawnmower pattern is the standard coverage algorithm for
systematic SAR (JSAR) and guarantees every cell within the polygon is overflown.

The planner handles arbitrary polygons (including concave boundaries) by rasterising with
`cv2.fillPoly` onto a binary mask, then reading non-zero pixel runs from each row. No
explicit polygon clipping is required.

### 6.2 Scan Angle Optimisation

The optimal scan angle minimises the number of perpendicular scan lines for a given polygon.
The planner uses `cv2.minAreaRect` to find the minimum-area bounding rectangle and aligns
scan lines with the longest edge.

A comprehensive analysis across 216 configurations (6 altitudes x 36 angles) confirmed the
optimal angle for the AENGM0074 polygon is **65-75 degrees**, consistent with its elongated
NE-SW geometry. This minimises the number of U-turns and total path length.

See: `analysis/path_optimization/plot3_scan_angle_vs_altitude.png` for the heatmap of scan
angle vs altitude.

### 6.3 Diagonal Realignment (the 53-Degree Trick)

The camera produces a 1456 x 1088 frame. The diagonal is longer than either side:

```
diagonal = sqrt(1456^2 + 1088^2) = 1818 pixels
```

By yawing the drone so the camera diagonal is perpendicular to the flight direction, the
effective swath increases from 1088 px (height) to 1818 px (diagonal) -- a factor of 1.67x,
giving **67% more ground coverage per scan line at zero extra flight cost**.

```
yaw_offset = atan(IMAGE_W / IMAGE_H) = atan(1456 / 1088) = 53.2 degrees
```

Configurable via `DIAGONAL_YAW_OFFSET_DEG` in `config.py`. Set to 0 (disabled) for initial
flights; set to `None` for auto-compute. The swath width at 35 m becomes approximately 47 m
(diagonal) vs 32 m (height-aligned), reducing total scan lines from 9 to approximately 6.

### 6.4 Three-Phase Flight Architecture

The mission proceeds in three phases, each with distinct navigation logic and airspeed:

1. **Transit** (15 m/s). Waypoint-to-waypoint flight from the launch point to the survey
   area entry. Pre-loaded as a MAVLink waypoint sequence. No detection runs during transit.

2. **Search** (6-10 m/s, altitude-dependent). Boustrophedon raster legs over the survey
   polygon. Onboard AI processes every frame; detections are queued for investigation. Speed
   is linearly interpolated between 6.0 m/s at 20 m altitude and 10.0 m/s at 50 m.

3. **Return** (15 m/s). After target confirmation and payload delivery (or exhaustion of all
   scan passes), the drone returns to the launch point via direct transit.

### 6.5 Rescan Strategy: Start High, Drop on Miss

If the first scan pass finds no confirmed target, the system drops altitude and rescans.
Three passes maximum, each reducing altitude by 20%:

| Pass | Altitude | Speed | Ground Width | Scan Lines | Target px (model) |
|------|----------|-------|-------------|------------|-------------------|
| 1 (initial) | 35 m | 8.0 m/s | 32.2 m | 9 | 48 px |
| 2 (rescan 1) | 28 m | 7.1 m/s | 25.7 m | ~11 | 60 px |
| 3 (rescan 2) | 22.4 m | 6.3 m/s | 20.6 m | ~14 | 75 px |

Each lower pass narrows the footprint (more scan lines, slower speed) but increases target
pixel size by approximately 60%, catching targets missed due to lighting, blur, or partial
occlusion.

**Config parameters:** `MAX_RESCAN_PASSES = 3`, `RESCAN_ALT_FACTOR = 0.8`,
`RESCAN_ALT_FLOOR_M = 15.0`.

**Note on initial altitude:** The energy analysis (Section 6.7) recommends 50 m as the
optimal initial scan altitude (33% fewer scan lines, 25% faster speed, ~60% of the time vs
35 m). The deployed default is 35 m as a conservative choice for initial flights;
`TARGET_ALT` can be raised to 50 m after first-flight validation. With 50 m start, rescans
proceed at 40 m then 32 m.

### 6.6 PLB Beacon Redirect to Focus Area

When a Personal Locator Beacon signal is received (B key or `--beacon-delay N` flag in
simulation), the search redirects to a smaller focus polygon:

1. Load focus area from `flight_plans/focus_area.json` (re-read each activation, allowing
   mid-flight coordinate updates from ground station).
2. Regenerate lawnmower pattern for the smaller polygon.
3. Reset waypoint index and rescan counter.
4. Drop speed to `FOCUS_SEARCH_SPEED_MPS = 5.0 m/s` for increased detection dwell time.
5. Preserve all rejected targets from the broad search (no re-investigation).

Fallback chain: JSON file -> drawn polygon (`config.FOCUS_AREA_GPS`) -> KML Focus Area.

### 6.7 Energy Analysis

An energy simulation (`analysis/path_optimization/`) evaluated the lawnmower pattern across
216 configurations (6 altitudes x 36 angles), accounting for momentum at U-turns, NFZ
slowdown zones, and altitude-dependent speed.

**Energy model:**
```
P_total = P_hover + P_drag = 150 W + 50 W * (v / 5)^2
```

Each U-turn incurs a 2-second deceleration/reacceleration penalty (momentum cost). Scan
lines near the SSSI no-fly zone trigger the speed cap (Section 7.3), adding approximately
45% time penalty on affected segments.

| Altitude | Scan Lines | Time | Energy |
|----------|-----------|------|--------|
| 50 m | 6 | 1.8 min | 8.3 Wh |
| 35 m | 9 | 3.3 min | 12.6 Wh |

Higher altitude means fewer scan lines, fewer U-turns, and faster speed (10 m/s at 50 m
vs 8 m/s at 35 m). The energy cost at 35 m is 52% higher than at 50 m for the same area.

**Plots (include in report):**
- `analysis/path_optimization/plot1_energy_vs_altitude.png` -- energy vs altitude
- `analysis/path_optimization/plot2_time_vs_altitude.png` -- time vs altitude
- `analysis/path_optimization/plot3_scan_angle_vs_altitude.png` -- scan angle vs altitude
- `analysis/path_optimization/plot4_scan_lines_vs_altitude.png` -- scan lines vs altitude
- `analysis/path_optimization/plot5_energy_heatmap.png` -- energy heatmap (angle x altitude)
- `analysis/path_optimization/plot6_survey_and_pattern.png` -- survey polygon with pattern overlay

---

## Section 7: Python-Based Demonstration

### 7.1 Simulation Architecture

#### State Machine Design

The mission is governed by a finite state machine with 18 states. At any instant the drone
is in exactly one state. A dispatch dictionary maps each `State` enum to a handler method
called once per main-loop iteration (~20 Hz).

**State transition diagram (simplified):**
```
INIT -> CONNECTING -> ARMING -> TAKEOFF
                                   |
                   (transit?) -----+-- (no transit)
                   |               |
              PRE_WAYPOINTS   TRANSIT_TO_SEARCH
                   |               |
                   +-> TRANSIT_TO_SEARCH
                             |
                          SEARCH  <-- rescan (drop alt) <--+
                          /    \                            |
                 detection    all WPs done, no confirm -----+
                 queued         (pass < MAX_RESCAN_PASSES)
                    |
                 CENTERING (60 s timeout -> SEARCH)
                    |  dist < 1 m
                 VERIFY  (120 s timeout -> reject)
                 / | \
          Y    N/I  timeout
          |     |
     APPROACH  queue pop -> CENTERING
          |    or RETURN_TO_SEARCH -> SEARCH
     HOVER_TARGET (servo release, 15 s)
          |
     RETURN_TRANSIT -> RETURN_HOME -> LANDING -> DONE
```

Manual override (M key or RC switch) can interrupt any state. The machine records where it
was and returns after override ends.

**Why a state machine:**

| Property | Benefit |
|----------|---------|
| Deterministic | Exactly one state at all times. Transition is a pure function of (state, inputs, operator commands). Auditable and testable. |
| Timeout safety | Every blocking state has a wall-clock timeout. No state can hang indefinitely. |
| Separation of concerns | Detection in `vision.py`, path planning in `planning.py`, navigation in `navigation.py`. The state machine orchestrates without duplicating. |
| Operator override | M key (software) or RC transmitter switch (hardware) can interrupt any state. |

#### Modular Design

| Module | Responsibility |
|--------|---------------|
| `config.py` | All tunable parameters: altitudes, speeds, camera, NFZ, connection strings |
| `states.py` | State enum (SEARCH, VERIFY, LANDING, etc.) |
| `vision.py` | Camera + AI detection. Dual backend: Ultralytics (laptop) / TFLite (Pi). Single interface: `detect_in_image(frame) -> (found, x, y, conf)` |
| `planning.py` | Lawnmower search pattern generator. Returns `[(lat, lon), ...]` |
| `navigation.py` | MAVLink command abstraction: goto, set_speed, send_velocity, land, arm |
| `geofence.py` | NFZ boundary distance, repulsive offset computation, inner polygon geometry |
| `state_machine.py` | All state handler methods (mixin class inherited by main mission) |
| `main.py` | Mission orchestrator: connects modules, runs main loop, dispatches states |
| `utils.py` | Geo math: GPS-to-pixel and pixel-to-GPS conversion (GeoTransformer) |

**Key principle:** `vision.py` is the only file that touches CV/AI. Everything else calls
`detect_in_image()`. The model, preprocessing, or backend can change without touching any
other file.

#### Same Code for SIM and REAL

`config.py` auto-detects hardware. If a serial port is found, it connects to the real Cube
flight controller. If no serial port, it connects to SITL. An environment variable
(`DRONE_MODE`) can override. No code changes between laptop simulation and Pi real flight.

#### God-View Simulation

`simple_simulator.py` provides an interactive laptop-only simulation with:
- Top-down god-view over real satellite imagery (`map.jpg`)
- Simulated camera view showing what the drone would see at current position/altitude
- Keyboard flight (WASD + altitude), GPS centering (C), visual servo (V), GPS lock (G)
- Simulated GPS drift, camera shake, CV inference throttle, TFLite backend

### 7.2 Detection Pipeline

#### YOLOv8n TFLite Inference

YOLOv8n (nano) was selected for the Raspberry Pi 5's Cortex-A76 CPU constraints:

| Variant | Parameters | TFLite Size | Pi 5 FPS (measured) | Pi 5 FPS (projected) |
|---------|:----------:|:-----------:|:-------------------:|:-------------------:|
| **YOLOv8n (chosen)** | 3.2 M | 3.2-11.7 MB | **4.8** | -- |
| YOLOv8s | 11.2 M | ~23 MB | -- | ~1.5 |
| YOLOv8m | 25.9 M | ~52 MB | -- | ~0.6 |

**Inference pipeline (per frame):**

| Step | Time | Notes |
|------|------|-------|
| Lens undistortion | 1.5 ms | cv2.remap with precomputed maps |
| Colour conversion (BGR->RGB) | 0.3 ms | |
| Resize to 640x640 | 0.5 ms | Bilinear interpolation |
| Normalise to [0,1] float32 | 0.2 ms | Division by 255 |
| TFLite invoke (XNNPACK) | 206 ms | 99% of total time |
| Output parsing + NMS | 0.1 ms | Transpose, threshold, NMS |
| **Total** | **~208 ms = 4.8 FPS** | |

Model input: `[1, 640, 640, 3]` float32. Output: `[1, 5, 8400]` transposed to `[8400, 5]`
where each row is `[cx, cy, w, h, class_conf]`. The 8400 candidates come from three-scale
prediction (80x80 + 40x40 + 20x20 = 8400 anchor-free detections). Single class: "dummy".

#### Detection Queue (FIFO)

Detections are appended to a FIFO queue and investigated in order. The drone does not
immediately divert to a new detection -- it finishes the current investigation first.

**Why FIFO, not priority (highest confidence first):** Confidence is not a reliable indicator
of validity. The same object scores differently depending on viewing angle, lighting, and
distance. A target detected at 0.3 from the edge may score 0.9 once overhead. Prioritising
by confidence would deprioritise valid oblique detections.

**Queue management:** `_pop_valid_target()` re-validates each entry against three filters
before dispatching: NFZ boundary, search area boundary, and proximity to rejected targets.
Invalid entries are silently skipped, making the queue self-cleaning.

#### GPS Estimation: Three-Stage Pipeline

| Stage | When | Method | CEP |
|-------|------|--------|-----|
| 1. Trigonometric estimate | Flyover during SEARCH | Pixel offset -> GSD -> heading rotation -> GPS delta | ~5 m |
| 2. Vision centering | CENTERING state (hover above) | Re-detection with near-zero pixel offset | ~2 m |
| 3. GPS averaging (optional) | `--center-verify` flag | 10 s of readings (~100 samples at 10 Hz) | <0.5 m |

**GSD formula:**
```
GSD = (SENSOR_WIDTH_MM * altitude) / (FOCAL_LENGTH_MM * IMAGE_W)
    = (5.02 * h) / (5.46 * 1456) = h * 6.315e-4  [m/px]
```

**Pixel-to-GPS conversion:**
```
offset_x_m = (px - IMAGE_W/2) * GSD
offset_y_m = (py - IMAGE_H/2) * GSD
offset_north = offset_x_m * cos(yaw) - offset_y_m * sin(yaw)
offset_east  = offset_x_m * sin(yaw) + offset_y_m * cos(yaw)
target_lat = drone_lat + offset_north / 111320
target_lon = drone_lon + offset_east / (111320 * cos(lat))
```

**Measured accuracy (from DJI video analysis, 143 estimates):** CEP50 = 2.3 m, max error =
16.5 m. The dominant error source is GPS receiver latency (100-200 ms), which creates a
characteristic diagonal spread along the direction of travel.

#### Confidence Threshold: 0.2

`CONFIDENCE_THRESHOLD = 0.2` is deliberately set low because of asymmetric cost structure:

| Outcome | Cost | Time |
|---------|------|------|
| **False positive investigated** | Fly to location, operator presses N, resume search | ~20 s |
| **Missed real target** | Entire rescan pass at lower altitude | 2-5 min |

The cost ratio is approximately **10:1** in favour of erring on the detection side. Real
dummy detections consistently score 0.8-0.95; false positives from terrain/shadows fall in
0.2-0.4. The deduplication system (5 m rejection radius, NFZ filter, boundary filter)
prevents false positives from flooding the queue.

**Single-frame trigger:** A target at the edge of the camera swath may appear in only 1-2
frames. Requiring 3 consecutive detections (`--smart-detect`) would miss these, costing a
full rescan pass. One false investigation (20 s) is cheaper than one missed target (2-5 min).

#### Training Data

The v2 model (sar_v2_1088) was trained on a dataset of 366 images at 1456 x 1088:
- **300 synthetic images:** dummy.png composited on real DJI flight video backgrounds with
  altitude-correct scaling, brightness/contrast/blur/rotation augmentation
- **16 real labelled frames:** extracted from DJI flight video, labelled at native resolution
- **50 negative images:** real flight frames containing no target (empty labels suppress FPs)

Training: Google Colab T4 GPU, `imgsz=1088`, 150 epochs, batch=8, early stopping patience=30.
Base weights: yolov8n.pt (COCO pretrained). Result: **mAP50 = 0.995**.

The model infers at 640x640 (TFLite runtime resizes), but training at 1088 teaches the model
to recognise finer features that survive the downscale.

### 7.3 NFZ Geofence

The survey area is adjacent to a SSSI no-fly zone. Three independent protection layers
provide defence in depth:

| Layer | Type | Runs on | What it catches |
|-------|------|---------|----------------|
| Speed cap (scalar field) | Software | Pi | Prevents high-speed overshoot during waypoint following |
| Repulsive push (vector field) | Software | Pi | Deflects drone if speed cap alone insufficient (wind, GPS jump) |
| Cube firmware geofence | Hardware | Flight controller | Triggers LOITER/RTL if all software fails |

If the Pi crashes, the Cube geofence still works. If the firmware geofence is misconfigured,
the software layers still enforce the boundary.

#### Layer 1: Speed Cap (DO_CHANGE_SPEED)

Within `NFZ_SLOW_ZONE_M = 20 m` of the SSSI boundary, a `MAV_CMD_DO_CHANGE_SPEED` command
linearly reduces maximum ground speed:

```
speed(d) = 0.3 + (d / 20) * (3.0 - 0.3)  [m/s]
```

| Distance from NFZ | Speed limit |
|-------------------|-------------|
| 20 m (entering zone) | 3.0 m/s |
| 10 m | 1.65 m/s |
| 0 m (at boundary) | 0.3 m/s |
| > 20 m | Normal (6-10 m/s) |

**Why 20 m zone width:** At WPNAV_ACCEL = 2.5 m/s^2, stopping from 10 m/s takes ~4 s /
~20 m. The buffer provides margin for smooth deceleration.

**Why DO_CHANGE_SPEED rather than velocity commands:** This modifies the autopilot's own
speed limit. The autopilot continues handling path smoothing, deceleration, and wind
compensation internally. The companion computer only adjusts the ceiling. Velocity commands
(`SET_POSITION_TARGET_LOCAL_NED`) fight the position controller, causing oscillation.

#### Layer 2: Repulsive Push (Vector Field)

A virtual inner polygon is offset inward by 20 m from the SSSI boundary. When the drone is
within 23 m of this inner polygon (effectively 3 m outside the actual NFZ boundary), a
constant-magnitude velocity command pushes it away at 3.0 m/s.

**Why constant magnitude (not gradient):** A gradient force weakening near the boundary
would let a fast-moving drone slip through. The constant 3.0 m/s push always exceeds the
near-zero speed cap at the boundary (0.3 m/s), guaranteeing escape.

#### Why NFZ_CARROT Won

Three approaches were implemented and tested in SITL simulation:

| Approach | Method | Result |
|----------|--------|--------|
| NFZ_REPEL | Velocity commands away from boundary | Oscillation -- fought position controller |
| NFZ_SLOW | Velocity toward waypoint at capped speed | Jittery -- duplicated autopilot logic with noisy GPS |
| **NFZ_CARROT** | **DO_CHANGE_SPEED + inner push** | **Smooth, predictable, no oscillation** |

NFZ_CARROT separates concerns: the scalar field handles gradual slowdown (letting the
autopilot handle direction), and the vector field handles emergency deflection (only within
3 m of the boundary).

### 7.4 Results

**Full mission demonstrated in SITL simulation:** The state machine transitions correctly
through all 18 states: INIT -> CONNECTING -> ARMING -> TAKEOFF -> TRANSIT -> SEARCH ->
CENTERING -> VERIFY -> APPROACH -> HOVER_TARGET -> RETURN_TRANSIT -> RETURN_HOME -> LANDING
-> DONE. All timeout fallbacks verified (CENTERING 60 s, VERIFY 120 s).

**Detection queue handles multiple targets correctly:** FIFO ordering prevents bounce between
targets. Three-filter validation (NFZ, search area, rejection radius) keeps the queue clean.
PLB beacon redirect clears stale entries automatically.

**NFZ geofence prevents boundary violations:** The speed cap produces smooth deceleration
approaching the SSSI boundary. Tested at multiple approach angles and speeds in SITL. The
repulsive push activates correctly within 3 m of boundary as a backup.

**Payload delivery demonstrated:** Two-stage servo release at 7.5 m lateral offset, 3 m
altitude. Servo PWM sequence: 1500 (closed) -> 1300 (partial, +3 s) -> 1100 (full, +6 s) ->
1500 (close, +15 s).

**Vision performance plots (include in report):**
- `analysis/plot1_altitude_vs_px.png` -- target pixel size vs altitude
- `analysis/plot2_speed_vs_blur.png` -- motion blur vs speed at various altitudes
- `analysis/plot3_speed_vs_frames.png` -- frames per flyover vs speed
- `analysis/plot4_coverage.png` -- ground coverage area vs altitude
- `analysis/plot5_detection_envelope.png` -- detection envelope (altitude/speed/blur)

### 7.5 Key Findings

1. **Motion blur is NOT the limiting factor.** The IMX296 global shutter combined with
   1/1000 s exposure produces 0.2-0.8 pixel blur at operational speeds (6-10 m/s). The
   critical speed for 1-pixel blur at 35 m altitude is 22.1 m/s -- well beyond the maximum
   drone speed. At 50 m, it rises to 31.6 m/s.

2. **Altitude is the real constraint.** At 50 m the dummy is 34 px tall in the 640x640
   model input -- above the empirical 20 px threshold but marginal on width (7 px). The
   critical altitude where height drops below 20 px is approximately 85 m. The operational
   range of 20-50 m keeps the dummy at 34-84 px.

3. **GPS accuracy: CEP50 = 2.3 m, improved to <0.5 m with centering + averaging.** The
   dominant error source is GPS receiver latency (100-200 ms), creating ~1 m along-track
   bias at 6 m/s. Vision centering (flying directly above, pixel offset near zero) improves
   to ~1 m. Adding 10 s GPS averaging (100 samples at 10 Hz) further reduces to <0.5 m.

4. **NFZ speed cap is smoother than velocity commands.** `DO_CHANGE_SPEED` lets the autopilot
   handle all trajectory planning internally. Velocity commands fight the position controller,
   causing oscillation. This was empirically verified across three implementations (Section
   7.3).

5. **Single-frame detection trigger is optimal.** Given the 10:1 cost asymmetry between
   missed targets (2-5 min rescan) and false positives (20 s investigation), requiring
   multiple frames would miss edge-of-swath targets for negligible gain.

6. **4.8 FPS is sufficient.** At every operational altitude and speed, the target appears in
   11-17 consecutive frames (93% frame overlap at 35 m). A single detection above 0.2
   confidence is enough to trigger investigation. The single-frame speed (only 1 frame
   containing the target) would require 66+ m/s -- physically impossible.

7. **Consecutive frame overlap is 93%.** At 35 m altitude and 8 m/s, the frame gap is 1.67 m
   against a 24.0 m footprint height: `overlap = 1 - (1.67 / 24.0) = 93%`.

---

## Section 8: Future Developments

### 8.1 Inference Speed Improvements

| Improvement | Expected Gain | Effort | Status |
|-------------|:------------:|:------:|:------:|
| FP16 XNNPACK | ~2x (10 FPS) | Low | Pi 5 has native FP16 (ARMv8.2-A) |
| Threaded capture + inference | +20-30% | Low | Producer-consumer pipeline |
| NCNN backend | ~3x (15 FPS) | Medium | Export available in `cv_models/sar_v2_1088/ncnn/` |
| Overclock to 2.8 GHz | +15-20% | Low | 3 lines in `/boot/firmware/config.txt` |
| INT8 quantisation | ~30% | Medium | Needs 300+ representative calibration frames |
| YOLO26n + NCNN | ~3x + better accuracy | High | +7% mAP over YOLOv8n, requires retraining |
| Hailo-8L accelerator | 80+ FPS | Hardware ($70) | Dedicated AI HAT for Pi 5 |

**Recommended priority:** FP16 XNNPACK first (highest impact, lowest effort), then threaded
pipeline, then NCNN. Combined, these three could reach 10-15 FPS -- a 2-3x improvement over
the current 4.8 FPS baseline.

### 8.2 Multi-Class Detection

Current system detects a single class ("dummy"). Extending to multi-class (dummy + person +
cone + vehicle) would broaden operational capability for real SAR scenarios. Requires
expanded training dataset with multiple target types. The single-class architecture (1
confidence value per 8400 candidates) would need to change to multi-class output (N
confidence values per candidate).

### 8.3 Adaptive Search (Heatmap-Focused Rescans)

Current rescans repeat the full lawnmower pattern at lower altitude. An adaptive approach
would concentrate rescan effort in areas with prior weak detections (confidence 0.15-0.2,
below threshold but suspicious). A heatmap of sub-threshold detections from the first pass
could guide a focused rescan, reducing flight time by 50-70%.

### 8.4 Wind Compensation in GPS Estimation

The GPS timing lag (100-200 ms) creates directional bias in target position estimates. A
correction term `offset = speed_vector * lag_time` applied in the heading direction would
remove this bias. Additionally, wind drift during descent (CENTERING state) shifts the
drone's position -- compensating for measured wind speed and direction would improve
centering accuracy.

### 8.5 Momentum-Aware Path Optimisation

Each U-turn incurs a 2-second deceleration/reacceleration penalty. Path smoothing at turn
points (Dubins paths or clothoid arcs) would reduce this penalty. Combined with a wind model
(flying with wind on one direction, against on return), the path planner could optimise
leg direction for minimum total energy.

### 8.6 Full Pi Integration

The full mission has been demonstrated end-to-end in SITL simulation on laptop. Remaining
integration steps for real flight:

1. Verify detection at operational altitude with real camera and lighting conditions
2. Validate GPS estimation accuracy against known ground truth positions
3. Test NFZ geofence response with real wind conditions
4. Full autonomous mission with operator in the loop for VERIFY confirmation
5. Progressive flight testing (passive detection -> waypoint flight -> autonomous search)

### 8.7 Detection Quality Improvements

| Improvement | Impact | Effort |
|-------------|--------|--------|
| More real labelled frames (target: 50-100) | Reduces overfitting to synthetic data | Medium |
| Multiple dummy poses/clothing | Improves generalisation | Medium |
| Partially occluded training samples | Handles tall grass, shadows | Medium |
| Proper train/val split (80/20) | Gives meaningful validation metrics | Low |
| Tiled inference (640 px tiles with overlap) | Better small-target detection at high altitude | Medium |

### 8.8 GPS Accuracy Improvements

| Improvement | Impact | Effort |
|-------------|--------|--------|
| GPS lag compensation | Removes directional bias (~1 m improvement) | Low |
| Kalman filter on target estimates | Smooths noisy multi-frame estimates | Medium |
| RTK GPS module | Sub-centimetre positioning | High (hardware + cost) |
| Visual odometry (optical flow) | Supplements GPS during fast manoeuvres | High |

---

## Figure Reference

### Path Optimisation Plots (`analysis/path_optimization/`)
- `plot1_energy_vs_altitude.png` -- total energy consumption vs search altitude
- `plot2_time_vs_altitude.png` -- total mission time vs search altitude
- `plot3_scan_angle_vs_altitude.png` -- optimal scan angle across altitudes
- `plot4_scan_lines_vs_altitude.png` -- number of scan lines vs altitude
- `plot5_energy_heatmap.png` -- energy heatmap (scan angle x altitude, 216 configurations)
- `plot6_survey_and_pattern.png` -- survey polygon with overlaid lawnmower pattern

### Vision Performance Plots (`analysis/`)
- `plot1_altitude_vs_px.png` -- target pixel size (height and width) vs altitude in model input
- `plot2_speed_vs_blur.png` -- motion blur in pixels vs drone speed at 20/35/50 m altitude
- `plot3_speed_vs_frames.png` -- frames per target flyover vs speed at various altitudes
- `plot4_coverage.png` -- ground coverage area vs altitude
- `plot5_detection_envelope.png` -- detection envelope showing altitude/speed operating region

---

## Key Numbers for Quick Reference

| Metric | Value | Source |
|--------|-------|--------|
| Inference speed (Pi 5) | 206.5 ms / 4.8 FPS | Measured benchmark |
| Model | YOLOv8n, 3.2M params, TFLite float32 | -- |
| Training data | 366 images (300 syn + 16 real + 50 neg) at 1456x1088 | -- |
| mAP50 | 0.995 | Colab training |
| Confidence threshold | 0.2 | config.py |
| GPS CEP50 (flyover) | 2.3 m | DJI video analysis, 143 estimates |
| GPS CEP (centered + averaged) | <0.5 m | Projected |
| Max GPS error | 16.5 m | Outlier from GPS timing lag |
| Motion blur (8 m/s, 35 m, 1/1000s) | 0.5 px | Calculated |
| Critical blur speed (35 m) | 22.1 m/s | 1 px blur threshold |
| Critical detection altitude | ~85 m | 20 px minimum in model input |
| Target px at 35 m (model) | 48 tall x 10 wide | Calculated |
| Target px at 50 m (model) | 34 tall x 7 wide | Calculated |
| Frames per flyover (35 m) | 14.4 | At 8 m/s, 4.8 FPS |
| Frame overlap (35 m, 8 m/s) | 93% | Calculated |
| Ground footprint (35 m) | 32.2 x 24.0 m | Calculated |
| GSD at 35 m | 22.1 mm/px | Calculated |
| Scan lines (35 m) | 9 | For AENGM0074 polygon |
| Scan lines (50 m) | 6 | 33% fewer than 35 m |
| Energy (35 m scan) | 12.6 Wh | Simulated |
| Energy (50 m scan) | 8.3 Wh | Simulated, 52% less |
| NFZ slow zone width | 20 m | config.py |
| NFZ min speed at boundary | 0.3 m/s | config.py |
| Focal length (IMX296) | 5.46 mm | Calibrated |
| Sensor width | 5.02 mm | Datasheet |
| Camera HFOV | 49.4 deg | Computed |
| Lens RMS reprojection error | 0.399 | Calibration |
| Undistortion cost | 1.5 ms/frame | Measured |
| Servo release altitude | 3 m | config.py |
| Lateral offset for payload | 7.5 m | config.py |
| Cost asymmetry (FP vs miss) | ~10:1 | Estimated |
| Rescan altitude factor | 0.8 (20% drop) | config.py |
| Max rescan passes | 3 | config.py |
