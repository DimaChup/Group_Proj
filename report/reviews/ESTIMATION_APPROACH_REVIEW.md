# GPS Estimation & SMART Detection — Technical Review

## Overview

The SAR drone project uses three distinct GPS estimation and detection-filtering approaches across four codebases. This document details each approach, the math behind key parameters, and an assessment of strengths and weaknesses.

---

## 1. GPS Estimation from Pixel Coordinates

### 1.1 Core Algorithm (gps_utils.py — `calculate_target_from_pixels`)

The canonical pixel-to-GPS projection used by `main.py`:

1. **Ground Sample Distance (GSD)**:
   ```
   GSD = (sensor_width_mm * altitude) / (focal_length_mm * image_w)
   ```
   With calibrated values: sensor=5.02mm, focal=5.46mm, image=1456px.
   At 35m altitude: GSD = (5.02 * 35) / (5.46 * 1456) = 0.0221 m/px.

2. **Pixel offset from image centre**:
   ```
   delta_x = u - image_w/2
   delta_y = v - image_h/2
   ```

3. **Camera-frame to metres** (forward = up in image = -delta_y):
   ```
   fwd_m  = -delta_y * GSD
   right_m = delta_x * GSD
   ```

4. **Rotate by drone yaw to NED frame**:
   ```
   offset_n = fwd * cos(yaw) - right * sin(yaw)
   offset_e = fwd * sin(yaw) + right * cos(yaw)
   ```

5. **Spherical projection to GPS**:
   ```
   dLat = offset_n / R_EARTH * (180/pi)
   dLon = offset_e / (R_EARTH * cos(lat)) * (180/pi)
   ```

**Tilt compensation** (main.py, passive_watch.py): When pitch/roll > ~1 degree, a full rotation matrix R = Rz(yaw) * Ry(-pitch) * Rx(-roll) is applied instead of the flat-earth approximation. The detection pixel is ray-traced through the tilted camera to find the ground intersection point. Falls back to flat-earth if the ray is nearly horizontal (rw2 < 0.01).

### 1.2 Passive Watch Variant (field_tools/passive_watch.py — `DummyEstimator`)

Uses normalised detection coordinates (0-1) instead of pixel coordinates:
```
dx_px = (det_x - 0.5) * image_w
dy_px = (det_y - 0.5) * image_h
dx_m = dx_px * altitude / focal_px    # focal_px = focal_mm * image_w / sensor_mm
```

Mathematically equivalent to the gps_utils.py approach (same GSD relationship), just parameterised differently. Also supports tilt-compensated ray-tracing via `--compensate-tilt` flag.

### 1.3 Simulator Variant (simulator/simple_simulator.py — `DummyEstimator.calculate_target_gps`)

Same flat-earth projection as gps_utils.py, but adds simulated noise sources:
- `alt_noise`: Gaussian noise on barometric altitude reading
- `yaw_noise`: Gaussian noise on compass heading
- `fov_error_pct`: Systematic FOV miscalibration (fixed bias per session)
- `gps_drift_max`: Random walk on GPS position (mean-reverting, ~0.3m/s wander)

---

## 2. Detection Weighting Schemes

### 2.1 Passive Watch: Inverse Altitude Squared + Centre Bonus

```python
weight = 1.0 / (alt_m ** 2)
```

**Rationale**: GPS estimation error is proportional to altitude (GSD scales linearly), so variance is proportional to altitude squared. Inverse-variance weighting (1/alt^2) is the statistically optimal weighting for combining measurements with known variance.

**Centre bonus** (passive_watch.py `DummyEstimator`):
```python
dist_from_centre = sqrt(dx_norm^2 + dy_norm^2)    # 0 at centre, ~0.707 at corner
max_dist = sqrt(0.5^2 + 0.5^2)                     # ~0.707
centre_factor = 1.0 + 4.0 * max(0, 1.0 - dist_from_centre / (max_dist * 0.3))
weight *= centre_factor
```

This gives up to 5x bonus for detections near the frame centre (within 30% of max distance). The factor decays linearly from 5.0 at centre to 1.0 at 21% of the way to the corner, then stays at 1.0.

**Justification**: Detections near the image centre have less projection error because:
- The flat-earth approximation is most accurate directly below (nadir)
- Lens distortion is minimal at centre
- Small yaw errors produce smaller position errors for near-nadir detections

### 2.2 Simulator: Altitude + Centre, Two Regimes

**Centre-snap** (within 30px of centre):
```python
est_lat = drone_lat    # target is directly below
est_lon = drone_lon
alt_factor = (30.0 / max(alt, 1.0))^2    # 30m=1x, 15m=4x, 10m=9x
weight = 10.0 * alt_factor               # base weight 10x (centre snap is high confidence)
```

**Standard detection** (outside 30px):
```python
centre_weight = 1.0 + 4.0 * (1.0 - dist_from_centre / max_dist)    # 5 at centre, 1 at corner
alt_factor = (30.0 / max(alt, 1.0))^2
weight = centre_weight * alt_factor
```

The simulator weights range from ~1 (corner at 30m) to ~90 (centre-snap at 10m).

### 2.3 Main.py (state_machine.py): No Weighting

The autonomous mission (main.py) does **not** use weighted averaging at all. Each detection produces a single GPS estimate (`calculate_target_gps`), and the drone flies to that point. There is no accumulation of multiple estimates during the SEARCH state — one confirmed detection triggers CENTERING immediately (or after `DETECT_CONFIRM_FRAMES` consecutive detections if `--smart-detect` is enabled).

The `--center-verify` flag enables GPS averaging only during the CENTERING state: after the drone arrives within 1m of the target, it collects GPS samples for a few seconds and uses their average to refine the target position before entering VERIFY.

---

## 3. Detection Clustering

### 3.1 Simulator: Distance-Based Spatial Clustering

```python
CLUSTER_THRESHOLD_M = 30    # default (configurable via --cluster-dist)
```

**Algorithm**:
1. For each new GPS estimate, find the nearest existing cluster (by distance from cluster's `best_gps` — its rolling weighted average).
2. If distance < `CLUSTER_THRESHOLD_M`, add to that cluster.
3. Otherwise, create a new cluster.

Each cluster maintains:
- **Rolling average** (last 50 observations): inverse-variance weighted mean
- **Total average** (all observations ever): cumulative weighted mean
- **Kalman filter estimate**: 2D static-target Kalman filter with altitude-dependent measurement noise

### 3.2 Main.py: Detection Dedup (Not Clustering)

The autonomous mission uses a simpler dedup mechanism:
- `REJECTED_TARGET_RADIUS_M = 5.0m` — any detection within 5m of a previously rejected target, item of interest, or queued detection is silently discarded.
- No spatial clustering or accumulation.

### 3.3 Passive Watch: SmartEstimator (Greedy Tightest Cluster)

This is the most sophisticated approach, used during manual flights to lock a target position:

**Not** distance-based routing — instead, all estimates are collected in a flat list, and the tightest cluster of exactly `min_samples` points is found post-hoc.

---

## 4. SMART Detection (SmartEstimator)

### 4.1 Algorithm

The SmartEstimator in `passive_watch.py` (lines 1165-1430) implements a **greedy tightest-cluster consensus lock**:

1. Every detection produces a GPS estimate via `DummyEstimator.add_observation()`.
2. The estimate `(lat, lon, pixel_dist, frame)` is appended to `all_estimates`.
3. Once `len(all_estimates) >= min_samples`, the `_find_tightest()` algorithm runs:

   **Step 1 — Pairwise distances**: Compute ground distance between every pair using the equirectangular approximation:
   ```
   north_m = delta_lat * 111320
   east_m  = delta_lon * 111320 * cos(mean_latitude)
   dist = sqrt(north_m^2 + east_m^2)
   ```

   **Step 2 — Seed with closest pair**: Start the cluster with the two nearest points.

   **Step 3 — Greedy expansion**: Repeatedly add the candidate point that minimises the cluster's maximum pairwise distance (spread). This is a greedy heuristic, not globally optimal.

   **Step 4 — Check spread**: If the final cluster's max pairwise distance < `max_spread`, declare **LOCK**.

4. On lock:
   - `locked_cluster` stores the winning points
   - `get_median()` returns the component-wise median (lat and lon independently)
   - `locked_frame` = the frame with smallest `pixel_dist` (most centred detection)
   - `lock_id` increments (persists across resets)
   - No further estimates are accepted after lock

### 4.2 Default Parameters

| Parameter | Default | CLI Flag | Description |
|-----------|---------|----------|-------------|
| `min_samples` | 5 | `--smart-min` | Minimum cluster size for lock |
| `max_spread` | 1.0m | `--smart-radius` | Maximum cluster spread |

These can also be adjusted at runtime via the browser UI (`/api/set-smart?spread=X&count=Y`).

### 4.3 Output

- **`get_median()`**: Component-wise median of locked cluster — `(median_lat, median_lon, n_samples)`. Uses statistical median, not mean, for outlier robustness.
- **`get_cep50()`**: Circular Error Probable — median distance from each cluster point to the median centre. CEP50 means 50% of estimates fall within this radius.

### 4.4 How It Differs from main.py's `--smart-detect`

The `--smart-detect` flag in main.py uses a **completely different** mechanism: a simple consecutive-frame counter.

```python
# state_machine.py, _process_detection()
if smart_detect:
    self._consecutive_detect_count += 1
    if self._consecutive_detect_count >= config.DETECT_CONFIRM_FRAMES:  # default 3
        self._enqueue_detection(...)
        self._consecutive_detect_count = 0
else:
    self._enqueue_detection(...)  # immediate trigger
```

- **main.py `--smart-detect`**: Requires N=3 consecutive frames with detection before enqueuing. Any frame without a detection resets the counter to 0. No GPS clustering, no spread check, no median.
- **passive_watch.py SmartEstimator**: Accumulates GPS estimates across multiple flyovers (not necessarily consecutive), finds the tightest spatial cluster, locks when spread < threshold.

These are fundamentally different approaches solving different problems:
- main.py's consecutive filter prevents single-frame false positives during autonomous flight
- passive_watch's SmartEstimator provides a confident GPS position from multiple noisy flyover observations

---

## 5. Kalman Filter (Simulator Only)

The simulator maintains a 2D Kalman filter per detection cluster for a **static target with varying measurement noise**:

**State**: `x = [lat, lon]` (target position, constant)
**Process noise**: `Q = (0.1m / R_EARTH)^2` (tiny — target doesn't move)
**Measurement noise**: `R = (3.0 / weight)^2` — inversely proportional to observation weight. High-weight observations (low altitude, centred) get low measurement noise.

```python
# Predict (target static):
P = P + Q * I

# Update:
S = P + R * I           # innovation covariance
K = P * inv(S)          # Kalman gain
x = x + K * (z - x)    # updated state
P = (I - K) * P         # updated covariance
```

The Kalman filter is compared against rolling and total weighted averages in the simulator's scatter plot display, but is **not used** in main.py or passive_watch.py.

---

## 6. Frame Count Math: How Many Frames See the Target?

### Parameters
- **Altitude**: 35m (TARGET_ALT)
- **Speed**: 10 m/s (SEARCH_SPEED_MPS at 35m, though `speed_for_altitude` may reduce this)
- **Inference rate**: ~4.8 FPS on Pi (TFLite), ~3.9 FPS observed
- **FOV**: HFOV = 2 * atan(5.02 / (2 * 5.46)) = 49.3 degrees
- **Ground footprint width**: 35 * 5.02 / 5.46 = 32.2m
- **Ground footprint height**: 32.2 * 1088 / 1456 = 24.1m (along flight direction)

### Calculation

**Time target is in FOV** (flying straight over):
```
t_visible = footprint_height / speed = 24.1m / 10 m/s = 2.41 seconds
```

**Frames during visibility**:
```
n_frames = t_visible * FPS = 2.41 * 4.8 = 11.6 frames (TFLite)
                           = 2.41 * 3.9 = 9.4 frames (observed)
```

**At 5 m/s (focus area speed)**:
```
t_visible = 24.1 / 5.0 = 4.82 seconds
n_frames = 4.82 * 4.8 = 23.1 frames
```

### Implications for SMART Parameters

- With `--smart-min 5` and `max_spread 1.0m`, the SmartEstimator needs 5 estimates within 1m of each other. A single flyover at 35m/10m/s produces ~10 frames, each with ~2-3m GPS estimation error (CEP50 from DJI video analysis). Getting 5 within 1m from a single pass is unlikely — typically requires 2+ passes or lower altitude.
- The main.py `DETECT_CONFIRM_FRAMES = 3` consecutive-frame filter is easily met during a single flyover (10+ frames available).

---

## 7. Centre vs Edge Detection Handling

| System | Centre Detection | Edge Detection |
|--------|-----------------|----------------|
| **Simulator** | Centre-snap: if within 30px, use drone GPS directly. Weight = 10 * alt_factor (very high). | Standard GSD projection. Weight = (1-5) * alt_factor based on distance from centre. |
| **Passive Watch** | No snap threshold. Centre bonus factor = up to 5x for detections within 21% of centre distance. | Standard projection. Centre factor decays to 1.0. |
| **Main.py** | No special handling. Single estimate, no weighting. | Same as centre — single GSD-based estimate. |

The simulator's centre-snap is aggressive: within 30px of centre (~0.66m at 35m altitude), it bypasses the GSD projection entirely and assumes the target is directly below the drone. This is accurate when hovering but can be wrong during fast forward flight (the camera may lag behind the GPS position).

---

## 8. Existing Figures and Visualizations

The following estimation-related figures exist in `report/figs/`:

| File | Content |
|------|---------|
| `estimator_comparison.pdf/png` | Bar chart: CEP50 for 4 methods — Rolling Avg (4.5m), Cumulative (3.2m), Kalman (2.8m), IVW (2.3m). IVW highlighted as "Selected". |
| `gps_bullseye.pdf/png` | Bullseye scatter plot of GPS estimates around target |
| `gps_error_direction.pdf/png` | Directional GPS error distribution |
| `gps_convergence.pdf` | GPS estimate convergence over time |

The `gen_estimator_comparison.py` script generates the comparison chart with hardcoded CEP50 values from simulation testing and DJI video analysis. Error bars show 95% confidence intervals from bootstrap resampling.

---

## 9. Confidence Score Handling

| System | Confidence Use |
|--------|---------------|
| **All systems** | `CONFIDENCE_THRESHOLD = 0.2` — detections below this are discarded by `vision.py` before reaching any estimator. |
| **Main.py** | Confidence is logged and saved in detection JSON metadata, but does **not** affect the GPS estimate or weighting. |
| **Passive Watch DummyEstimator** | Confidence is **not used** in weighting — only altitude and centre distance determine weight. |
| **Passive Watch SmartEstimator** | Confidence is **not used** — only spatial agreement (spread) matters for lock. |
| **Simulator** | Confidence stored but not used in weighting. |

**Assessment**: Confidence could improve estimation quality — a conf=0.95 detection at 35m is likely more accurately centered on the target than a conf=0.25 detection. However, the current approach avoids this because YOLO confidence reflects classification certainty, not localization precision. The bounding box center of a high-confidence detection is not necessarily closer to the target's true center than a low-confidence one.

---

## 10. Strengths and Weaknesses

### Strengths

1. **Tilt compensation**: The ray-tracing approach using the full rotation matrix (Rz * Ry * Rx) is mathematically correct and handles real-world pitch/roll during flight. This was validated with 1440 test cases.

2. **Inverse-variance weighting**: Statistically sound — weights by 1/alt^2 which is the optimal weighting when measurement variance scales as altitude squared. The estimator comparison chart shows IVW achieves CEP50 = 2.3m vs 4.5m for simple rolling average.

3. **SmartEstimator robustness**: The greedy tightest-cluster approach naturally rejects outliers — a single bad estimate won't trigger a false lock because it won't cluster tightly with the good estimates. Using median (not mean) for the final position adds further outlier protection.

4. **Multiple estimation backends**: The simulator provides rolling average, total average, Kalman filter, and IVW for comparison, enabling empirical selection of the best method.

5. **Separation of concerns**: GPS estimation (`gps_utils.py`, `DummyEstimator`), detection filtering (`SmartEstimator`, `_process_detection`), and state transitions (`state_machine.py`) are cleanly separated.

### Weaknesses

1. **No confidence weighting**: Detection confidence is computed but completely ignored in all weighting schemes. While YOLO confidence is an imperfect proxy for localization quality, incorporating it (even partially) could help — especially for filtering marginal detections that happen to be near the image centre.

2. **GPS timing lag not compensated**: The GPS receiver has 100-200ms latency, causing ~1m error at 5m/s along the flight direction (documented in `memory/gps-timing-lag.md`). No code compensates for this — the drone's GPS position at detection time is assumed to be current, but it's actually 100-200ms stale. Fix: offset GPS by `speed * lag` in the heading direction.

3. **Centre bonus is discontinuous (passive_watch)**: The centre_factor formula `1.0 + 4.0 * max(0, 1.0 - dist / (max_dist * 0.3))` creates a cliff at 30% of max distance — inside that radius, weight jumps up to 5x; outside, it's exactly 1.0. A smooth decay (e.g., Gaussian or inverse-square) would be more principled.

4. **Simulator centre-snap during forward flight**: The 30px snap threshold assumes the target is directly below the drone, which is only true when hovering. At 5m/s with 200ms GPS lag, the drone is ~1m ahead of its reported position — the snap introduces a systematic ~1m bias in the flight direction.

5. **SmartEstimator is greedy, not optimal**: The tightest-cluster algorithm seeds with the closest pair and greedily expands. This is O(n^2) and not guaranteed to find the globally tightest cluster. For typical sample sizes (5-50 points), this is acceptable, but the greedy solution could miss a tighter cluster that doesn't include the globally closest pair.

6. **No multi-pass fusion in main.py**: The autonomous mission treats each detection independently — there is no accumulation of GPS estimates across multiple search passes. If the drone flies over the same target on parallel lawnmower strips, each detection triggers a separate CENTERING attempt rather than refining the estimate. The `--center-verify` flag partially addresses this but only during the CENTERING state.

7. **Three different estimation codebases**: `gps_utils.py`, `passive_watch.py DummyEstimator`, and `simple_simulator.py DummyEstimator` implement the same core math independently. Changes to one don't propagate to the others. The passive_watch version uses `111320` for lat-to-metres conversion while main.py uses `111132.0` — a 0.17% discrepancy.

8. **No motion blur consideration**: At 10m/s and ~200ms exposure, motion blur can smear the target by ~2m in the image. This shifts the detected bounding box centre, but the weighting scheme treats all detections equally regardless of blur.

---

## 11. Parameter Justification Summary

| Parameter | Value | Justification |
|-----------|-------|---------------|
| `DETECT_CONFIRM_FRAMES` | 3 | At ~5 FPS, a real target produces 10+ frames per pass. 3 consecutive frames filters single-frame false positives while keeping response time fast (~0.6s delay). |
| `smart_min` (SmartEstimator) | 5 | With CEP50 ~2.3m per estimate, 5 agreeing within 1m means multiple flyovers confirm the same location. 5 is a balance between confidence and speed. |
| `smart_radius` (max_spread) | 1.0m | 1m spread for 5 points means all 5 agree to within 1m — much tighter than the ~2.3m single-estimate CEP50. This filters noise effectively while being achievable with 2-3 flyovers at different altitudes. |
| `CLUSTER_THRESHOLD_M` | 30m (simulator) | At 35m altitude, the FOV footprint is ~32m wide. Detections from a single flyover of the same target will typically cluster within ~10-15m. 30m is conservative — prevents splitting one target into two clusters, while keeping distinct targets (>30m apart) separate. |
| `REJECTED_TARGET_RADIUS_M` | 5.0m | Prevents re-investigating the same target after rejection. 5m is ~2x the GPS estimation CEP50 (2.3m), so re-detections of the same physical target will almost always fall within this radius. |
| `CONFIDENCE_THRESHOLD` | 0.2 | Deliberately low — the operator (via Y/N buttons) is the final filter. Low threshold catches more true positives at the cost of more false positives that the operator can dismiss. |
| Inverse-variance weight | 1/alt^2 | GSD (m/px) scales linearly with altitude. Pixel localization error is approximately constant (few pixels). Therefore GPS error in metres scales as altitude. Variance scales as altitude^2. Optimal weight = 1/variance = 1/alt^2. |
| Centre bonus | up to 5x | Empirically motivated — detections near frame centre have less projection error due to smaller yaw sensitivity and less lens distortion. The 5x factor was tuned in simulation. |
