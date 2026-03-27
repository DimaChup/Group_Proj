# Speed, Blur, and Detection Breakdown Analysis

**SAR Drone Project (AENGM0074) -- Detection Envelope Characterisation**

This analysis determines the operational envelope of the onboard detection system:
at what combination of altitude and speed does target detection become unreliable,
and what is the true limiting factor?

---

## 1. System Parameters

All values from `config.py` and measured benchmarks (Pi 5, 2026-03-11).

| Parameter | Value | Source |
|-----------|-------|--------|
| Sensor width | 5.02 mm | `SENSOR_WIDTH_MM` |
| Focal length | 5.46 mm | `FOCAL_LENGTH_MM` (calibrated at 1 m) |
| Image resolution | 1456 x 1088 px | `IMAGE_W`, `IMAGE_H` (IMX296 native) |
| Model input | 640 x 640 px | YOLOv8n TFLite |
| Inference time | ~206 ms | Pi 5 TFLite benchmark |
| Frame rate | 4.8 FPS | 1000 / 206 ms |
| Confidence threshold | 0.2 | `CONFIDENCE_THRESHOLD` |
| Camera | IMX296 global shutter | No rolling-shutter artefacts |
| Target (dummy) | ~1.8 m tall, ~0.5 m wide | Lying on ground |

---

## 2. Ground Footprint and GSD by Altitude

The ground footprint width is:

```
footprint_W = SENSOR_WIDTH_MM * altitude / FOCAL_LENGTH_MM
footprint_H = footprint_W * (IMAGE_H / IMAGE_W)
```

Ground Sample Distance (GSD) is the physical size of one pixel at ground level:

```
GSD = footprint_W / IMAGE_W
```

| Altitude (m) | Footprint W (m) | Footprint H (m) | GSD (m/px) | Footprint Area (m^2) |
|:---:|:---:|:---:|:---:|:---:|
| 20 | 18.4 | 13.7 | 0.0126 | 252 |
| 25 | 23.0 | 17.2 | 0.0158 | 396 |
| 30 | 27.6 | 20.6 | 0.0189 | 569 |
| 35 | 32.2 | 24.0 | 0.0221 | 773 |
| 40 | 36.8 | 27.5 | 0.0253 | 1012 |
| 50 | 46.0 | 34.3 | 0.0316 | 1578 |

**Calculation example (35 m):**
- W = 5.02 * 35 / 5.46 = 32.2 m
- H = 32.2 * (1088 / 1456) = 24.0 m
- GSD = 32.2 / 1456 = 0.0221 m/px

---

## 3. Dummy Size in Pixels

The dummy (1.8 m x 0.5 m) projects to:

```
dummy_px_tall = DUMMY_HEIGHT_M / GSD
dummy_px_wide = 0.5 / GSD
```

Because the model input is 640x640 and the full frame is 1456x1088, the frame is
resized (squashed) by a factor of 640/1456 = 0.4396 horizontally and 640/1088 = 0.5882
vertically. The dummy size in the model's 640x640 input is:

```
dummy_model_tall = dummy_px_tall * (640 / IMAGE_H)
dummy_model_wide = dummy_px_wide * (640 / IMAGE_W)
```

| Altitude (m) | Full Frame (px) tall x wide | Model Input (px) tall x wide | Detectable? |
|:---:|:---:|:---:|:---:|
| 20 | 143 x 40 | 84 x 18 | Yes -- large target |
| 25 | 114 x 32 | 67 x 14 | Yes -- comfortable |
| 30 | 95 x 26 | 56 x 12 | Yes -- solid |
| 35 | 81 x 23 | 48 x 10 | Yes -- adequate |
| 40 | 71 x 20 | 42 x 9 | Yes -- marginal width |
| 50 | 57 x 16 | 34 x 7 | Marginal -- height OK, width thin |

**Detection threshold:** YOLOv8n requires roughly 15-20 px in the smallest dimension
of its 640x640 input to reliably detect an object. The dummy's height stays above
this threshold even at 50 m (34 px). The width drops to 7 px at 50 m, but because
the model was trained on the dummy shape (elongated figure lying down), height is
the dominant dimension for detection.

**Critical altitude:** The dummy drops below 20 px height in the model input at
approximately 85 m. Below 15 px (~100 m), detection would be unreliable. Our
operating range of 20-50 m keeps the dummy at 34-84 px in the model input --
comfortably above the detection floor.

---

## 4. Speed vs. FPS: Frame Coverage Analysis

At 4.8 FPS, the distance the drone travels between consecutive frames is:

```
frame_gap = speed / FPS
```

The number of frames the dummy appears in depends on how long it stays in the
camera's field of view:

```
time_in_view = footprint_H / speed       (along-track dimension)
frames_in_view = time_in_view * FPS
```

The altitude-dependent speed profile from `config.py` is:

```python
# Linear from (20m, 6 m/s) to (50m, 10 m/s)
SPEED_AT_LOW  = 6.0   # m/s at 20 m altitude
SPEED_AT_HIGH = 10.0  # m/s at 50 m altitude
```

| Altitude (m) | Speed (m/s) | Frame Gap (m) | Footprint H (m) | Time in View (s) | Frames in View |
|:---:|:---:|:---:|:---:|:---:|:---:|
| 20 | 6.0 | 1.25 | 13.7 | 2.28 | 11.0 |
| 25 | 6.7 | 1.39 | 17.2 | 2.57 | 12.3 |
| 30 | 7.3 | 1.53 | 20.6 | 2.82 | 13.5 |
| 35 | 8.0 | 1.67 | 24.0 | 3.00 | 14.4 |
| 40 | 8.7 | 1.80 | 27.5 | 3.16 | 15.2 |
| 50 | 10.0 | 2.08 | 34.3 | 3.43 | 16.5 |

**Key finding:** The dummy appears in 11-17 frames at every altitude. Even at the
fastest speed (10 m/s at 50 m), the target is visible for 3.4 seconds and captured
in ~16 frames. A single detection with confidence > 0.2 is sufficient to trigger
investigation, so there is substantial margin.

**At what speed would detection become marginal?** For the dummy to appear in only
1 frame, the drone would need to cross the entire footprint height in one frame
interval (1/4.8 = 0.208 s):

```
critical_speed = footprint_H * FPS
```

| Altitude (m) | 1-Frame Speed (m/s) | Notes |
|:---:|:---:|:---|
| 20 | 66 | Well beyond drone capability |
| 35 | 115 | Physically impossible |
| 50 | 165 | Physically impossible |

Frame coverage is never the limiting factor at any realistic drone speed.

---

## 5. Motion Blur Analysis

The IMX296 is a global shutter sensor, which eliminates rolling-shutter artefacts
(skew, wobble). However, motion blur from the drone's translational movement still
occurs and depends on exposure time.

**Blur on the sensor:**

```
blur_on_ground = speed * exposure_time          (metres of smear at ground level)
blur_in_pixels = blur_on_ground / GSD
```

| Speed (m/s) | Exposure | Blur on Ground (mm) | Blur at 20 m (px) | Blur at 35 m (px) | Blur at 50 m (px) |
|:---:|:---:|:---:|:---:|:---:|:---:|
| 6 | 1/500 s | 12 | 1.0 | 0.5 | 0.4 |
| 6 | 1/1000 s | 6 | 0.5 | 0.3 | 0.2 |
| 10 | 1/500 s | 20 | 1.6 | 0.9 | 0.6 |
| 10 | 1/1000 s | 10 | 0.8 | 0.5 | 0.3 |
| 15 | 1/500 s | 30 | 2.4 | 1.4 | 0.9 |
| 15 | 1/1000 s | 15 | 1.2 | 0.7 | 0.5 |

**Conclusion:** Motion blur is sub-pixel at all operating altitudes and speeds, even
with a conservative 1/500 s exposure. At the operational speed profile (6-10 m/s)
with 1/1000 s shutter, blur is 0.2-0.8 px -- completely negligible.

**Motion blur is NOT the limiting factor.** The global shutter combined with short
exposure times means the image is effectively frozen at any speed the drone can
achieve.

---

## 6. The Real Limiting Factor: Inference Speed

The detection pipeline bottleneck is inference time, not image quality:

| Constraint | Value | Impact |
|-----------|-------|--------|
| Inference time | 206 ms/frame | Caps throughput at 4.8 FPS |
| Frame gap at 10 m/s | 2.08 m | Spatial sampling resolution |
| Dummy width | 0.5 m | Smaller than one frame gap |
| Detection per pass | 11-17 frames | Sufficient (need only 1) |

However, 4.8 FPS is adequate because:

1. **The footprint is large.** At 35 m, each frame covers 32 x 24 m. A 2 m gap
   between frame centres means 94% overlap between consecutive frames.
2. **Lawnmower overlap provides redundancy.** Even with 0% commanded overlap, the
   diagonal realign yaw gives an effective ~67% bonus coverage of the inter-scan
   gaps.
3. **Confidence threshold is low.** At 0.2, even a partial or edge-of-frame
   detection triggers investigation. The operator confirms or rejects.
4. **Rescan passes are built in.** Up to 3 altitude-drop rescans
   (`MAX_RESCAN_PASSES = 3`, `RESCAN_ALT_FACTOR = 0.8`) ensure any near-miss
   at high altitude is caught at a lower pass.

**Where inference speed would matter:** If the drone flew at >30 m/s at 20 m altitude,
frame overlap would drop below 50% and the target might appear in only 2-3 frames.
This is well beyond the operational speed envelope (6-10 m/s).

---

## 7. Justification for Starting at 50 m Altitude

The search strategy begins at 50 m and descends if needed. This is justified by the
analysis above:

### 7.1 Detection Is Viable at 50 m

| Metric | Value at 50 m |
|--------|---------------|
| Dummy in model input | 34 x 7 px (height above 20 px threshold) |
| Dummy in full frame | 57 x 16 px |
| Frames per pass | ~16 (3.4 s in view at 10 m/s) |
| GSD | 0.032 m/px |
| Motion blur at 10 m/s, 1/1000 s | 0.3 px (negligible) |

The retrained model (`sar_v2_1088`, mAP50 = 0.995) was trained on synthetic images
that include altitude-correct scaling at various heights, including high-altitude
views where the dummy is small. With the confidence threshold at 0.2, even a
low-confidence partial detection is sufficient to trigger a closer look.

### 7.2 Coverage Efficiency

| Altitude (m) | Swath Width (m) | Scan Lines (est.) | Speed (m/s) | Relative Time |
|:---:|:---:|:---:|:---:|:---:|
| 35 | 24.0 | ~9 | 8.0 | 1.00x (baseline) |
| 40 | 27.5 | ~8 | 8.7 | 0.82x |
| 50 | 34.3 | ~6 | 10.0 | 0.59x |

Starting at 50 m instead of 35 m requires approximately 33% fewer scan lines and
permits 25% faster flight speed. Combined, the initial scan pass completes in
roughly 60% of the time. If detection succeeds on this first pass (as the pixel
analysis predicts it will for most target orientations), the entire mission is
significantly shorter.

### 7.3 Multi-Pass Safety Net

If the target is missed at 50 m (e.g., partial occlusion, unusual orientation,
or the dummy width falling to 7 px in the model input), the system automatically
descends:

```
Pass 1: 50 m  (dummy 34 px tall in model -- viable)
Pass 2: 40 m  (dummy 42 px tall -- comfortable)
Pass 3: 32 m  (dummy 52 px tall -- easy)
```

Each subsequent pass covers less area but with higher resolution. The altitude
floor is 15 m (`RESCAN_ALT_FLOOR_M`), where the dummy would be 100+ px tall.

---

## 8. NFZ Boundary Approach: Why the Carrot Method

Three approaches to No-Fly Zone avoidance were tested during development. The
analysis of each:

### 8.1 NFZ_REPEL (Velocity Commands Pushing Away)

**Approach:** When the drone approaches the NFZ boundary, send velocity commands
(SET_POSITION_TARGET_LOCAL_NED) pushing it away from the boundary, scaled by
proximity.

**Problem:** This fought ArduCopter's position controller. The autopilot is
simultaneously trying to hold the current GUIDED waypoint position while our
velocity command pushes the drone away. These two controllers operate at different
rates and with different dynamics -- the result was oscillation and jitter near
boundaries. The drone would overshoot the repulsion, the position controller would
pull it back, triggering more repulsion.

### 8.2 NFZ_SLOW (Velocity Toward Waypoint)

**Approach:** Compute the direction vector from the drone's current position to
the next waypoint. Scale the velocity magnitude based on NFZ proximity. Send this
as a velocity command.

**Problem:** Functional but redundant. We computed the direction and speed ourselves,
duplicating what ArduCopter's trajectory planner already does (and does better,
with acceleration limits, smoothing, and GPS noise filtering). Our 20 Hz velocity
commands produced jittery movement because they lack the trajectory planner's
lookahead and smoothing. Additionally, if the velocity command stream was interrupted
(e.g., a processing spike), the drone would halt until the next command.

### 8.3 NFZ_CARROT (DO_CHANGE_SPEED) -- Selected

**Approach:** Let ArduCopter handle all direction and trajectory planning via
normal GUIDED waypoints. Near the NFZ boundary, send `DO_CHANGE_SPEED` to reduce
the speed limit. The autopilot continues navigating toward the waypoint but at a
capped speed. An inner polygon offset (`NFZ_INNER_OFFSET_M = 20 m`) provides a
secondary additive velocity push that only activates very close to the boundary.

**Why this works:**

| Property | REPEL | SLOW | CARROT |
|----------|-------|------|--------|
| Uses ArduCopter trajectory planner | No | No | Yes |
| Smooth movement | No (oscillation) | No (jitter) | Yes |
| Code complexity | Medium | High | Low |
| Controller conflict | Yes | Partial | None |
| Failsafe on command gap | Drift | Stop | Continues to waypoint |

The carrot method is the minimal-intervention approach: it modifies a single
parameter (speed) and leaves all spatial reasoning to the flight controller. This
is consistent with the project's design philosophy of delegating as much as possible
to ArduCopter's battle-tested autopilot rather than reimplementing flight dynamics
in Python.

Relevant config values:
- `NFZ_SLOW_ZONE_M = 20.0` -- speed scaling active within 20 m of NFZ
- `NFZ_MIN_SPEED_MPS = 0.3` -- minimum speed at the boundary
- `NFZ_ZONE_MAX_SPEED_MPS = 3.0` -- speed at the outer edge of the slow zone
- `NFZ_HARD_BOUNDARY_M = 3.0` -- auto-switch to MANUAL mode inside this

---

## 9. Summary of Constraints

| Factor | Limiting? | Reason |
|--------|:---------:|--------|
| Motion blur | No | Global shutter + short exposure = sub-pixel blur at all speeds |
| Pixel size (altitude) | Marginal at 50 m | Dummy height 34 px in model input, above 20 px floor |
| Pixel size (altitude) | No below 40 m | Dummy height > 42 px in model input |
| Inference FPS | No | 4.8 FPS gives 11-17 frames per target flyover |
| Frame gap | No | 2 m gap at 10 m/s, but 94% frame overlap at 35 m altitude |
| Speed | No | Max 10 m/s is far below the ~66 m/s single-frame threshold |

**The real operational limit is altitude, not speed or blur.** At 50 m the system
is at the edge of comfortable detection (dummy width = 7 px in model input). Above
~85 m, the dummy height would drop below 20 px in the model input and detection
would become unreliable. The multi-pass descent strategy (50 m -> 40 m -> 32 m)
provides a robust safety net.

The speed profile (`SPEED_AT_LOW = 6 m/s` at 20 m, `SPEED_AT_HIGH = 10 m/s` at 50 m)
is conservative relative to the detection envelope. Speed could be increased to
15+ m/s without impacting detection, though this would reduce GPS estimation accuracy
due to the 100-200 ms GPS timing lag (see `memory/gps-timing-lag.md`).
