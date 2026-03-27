# GPS Estimation Accuracy Analysis

**Purpose**: Quantify the expected error in converting pixel detections to GPS coordinates for offset landing.

**Context**: Uses the pixel-to-GPS conversion math from `gps_utils.py` and `config.py` with actual hardware calibration values.

---

## System Overview

The pixel-to-GPS estimation pipeline works as follows:

```
AI detection → pixel (u, v) → camera geometry → world frame rotation → GPS offset → target estimate
```

Each step introduces error from multiple sources. This document calculates and combines those errors.

### Key Config Values

From `config.py` (as of 2026-03-16):

| Parameter | Value | Source |
|-----------|-------|--------|
| **Camera Calibration** | | |
| FOCAL_LENGTH_MM | 5.46 | Calibrated 2026-03-11: 92cm visible at 1m height |
| SENSOR_WIDTH_MM | 5.02 | IMX296 global shutter sensor spec |
| IMAGE_W | 1456 | Pi camera native resolution (upgraded from 640) |
| IMAGE_H | 1088 | Pi camera native resolution (upgraded from 480) |
| **Flight Altitudes** | | |
| TARGET_ALT | 35 m | Search altitude (nominal) |
| VERIFY_ALT | 15 m | Centering altitude (verification phase) |
| **Detection Threshold** | | |
| CONFIDENCE_THRESHOLD | 0.2 | Min confidence to report detection |
| **Speeds** | | |
| SEARCH_SPEED_MPS | 10 | m/s at search altitude |
| FOCUS_SEARCH_SPEED_MPS | 5 | m/s in focus area |
| **Positioning** | | |
| DETECT_LOCK_RADIUS_M | 5 | Ignore detections >5m from locked target |

---

## Error Budget Components

### 1. GPS Receiver Noise (σ_gps)

**Source**: GNSS receiver inherent noise floor while stationary.

**From MEMORY.md (2026-03-11 field test data)**:
- CEP50: ~1.5m (50% of fixes within this radius)
- CEP95: ~2.3m (95% of fixes within this radius)
- Max drift: ~16.5m (rare outliers)

**Conservative estimate**: ±2-3m CEP (circular error probable).

**At any single instant**: Assuming normal distribution with CEP95 = 2.3m,
- Horizontal accuracy ≈ ±1.2-1.5m (1σ)
- Becomes dominant error at low altitude or high detection confidence

**Formula**:
```
σ_gps ≈ CEP95 / 2 ≈ 2.3 / 2 = 1.15m (1σ-equivalent)
or worst-case: 2-3m single-point error
```

---

### 2. Altitude Barometer Error (σ_alt)

**Source**: Barometer drift and absolute altitude measurement error.

**Specification**: DJI/Auterion barometers typically ±0.5m.

**Impact on GPS estimate**:

The pixel-to-GPS conversion uses altitude to scale pixel offsets to ground distance:

```
GSD (m/pixel) = (SENSOR_WIDTH_MM * drone_alt) / (FOCAL_LENGTH_MM * IMAGE_W)
```

At TARGET_ALT = 35m:
```
GSD = (5.02 * 35) / (5.46 * 1456)
    = 175.7 / 7948.76
    = 0.0221 m/pixel = 22.1 mm/pixel
```

If actual altitude is 35.5m (barometer +0.5m error):
```
GSD_actual = (5.02 * 35.5) / 7948.76 = 0.0224 m/pixel
error_per_pixel = 0.0224 - 0.0221 = 0.0003 m/pixel
```

For a detection at pixel offset Δx = 100 px from image centre:
```
ground_error = 100 px * 0.0003 m/px = 0.03 m = 3 cm
```

**At VERIFY_ALT = 15m**:
```
GSD = (5.02 * 15) / 7948.76 = 0.00948 m/pixel = 9.48 mm/pixel
error_per_pixel = (5.02 * 15.5) / 7948.76 - 0.00948 = 0.0011 m/pixel
ground_error = 100 px * 0.0011 = 0.11 m = 11 cm
```

**Worst case: typical pixel offset at 35m altitude**:
- Image is 1456 pixels wide → max offset ≈ 728 pixels from centre
- With ±0.5m altitude error → error ≈ 0.3 m to 1.6m depending on distance

**Conservative contribution**: σ_alt ≈ 0.2-0.5m at 35m, negligible at 15m.

---

### 3. Yaw Error (σ_yaw)

**Source**: Compass/IMU error in drone heading. Cube reports yaw ±2-5 degrees (spec).

**Impact**: Rotation of the pixel offset vector by wrong angle.

The pixel-to-GPS conversion rotates camera-frame offsets by yaw:

```
offset_north = fwd * cos(yaw) - right * sin(yaw)
offset_east = fwd * sin(yaw) + right * cos(yaw)
```

At TARGET_ALT = 35m with GSD = 22.1 mm/px:
- Max ground distance from centre: 728 px * 22.1 mm = 16.1 m
- If object is at (fwd=0, right=16.1m), yaw error rotates this vector

**Yaw error ±2 degrees** (0.035 rad):
```
fwd' = 0 * cos(±0.035) - 16.1 * sin(±0.035) = ∓0.56 m
right' = 0 * sin(±0.035) + 16.1 * cos(±0.035) ≈ 16.1 m
error = sqrt(0.56² + 0) ≈ 0.56 m
```

**Yaw error ±5 degrees** (0.087 rad):
```
fwd' = -16.1 * sin(±0.087) = ∓1.4 m
error ≈ 1.4 m
```

**For a detection at smaller offset (100 px right)**:
- Ground distance: 100 * 22.1 mm = 2.21 m
- Yaw error ±2°: error = 0.076 m
- Yaw error ±5°: error = 0.19 m

**Typical case (mid-image detection)**:
- Detection ~200-300 px from centre → ~4.4-6.6 m ground distance
- Yaw error ±2°: 0.15-0.23 m
- Yaw error ±5°: 0.38-0.58 m

**Conservative contribution**: σ_yaw ≈ 0.3-0.6m (assuming ±2-3° yaw noise).

---

### 4. GSD Quantization Error (σ_quantization)

**Source**: Discrete pixel grid → continuous ground coordinates.

**Model**: Each pixel represents a ~22mm x ~22mm ground area at 35m.

For a random detection within a pixel:
```
quantization_error ≈ GSD / sqrt(12) ≈ 22.1mm / sqrt(12) ≈ 6.4 mm
```

At the image centre (Cx=728, Cy=544) vs offset (u=750, v=560):
```
Δ pixel = sqrt((750-728)² + (560-544)²) = sqrt(484 + 256) = 27.5 px
ground_distance = 27.5 * 22.1 mm = 608 mm = 0.6 m
quantization_error << 0.6 m (negligible)
```

**Conservative contribution**: σ_quantization ≈ 0.01m — negligible.

---

### 5. GPS Timing Lag (σ_lag)

**Source**: GPS receiver latency (~100-200ms) relative to image capture.

**During mission**: Drone is flying, not hovering.

At SEARCH_SPEED_MPS = 10 m/s:
```
lag = 150 ms (mid-range estimate)
distance_traveled = 10 m/s * 0.15 s = 1.5 m
```

The GPS position reported is 150ms old → actual drone was 1.5m further along flight direction.

**Impact**: Pixel detection is from current frame (0ms lag), but GPS position is 150ms stale.
- If flying North at 10 m/s, GPS reports position 1.5m South of actual
- This causes the estimated target to be offset ~1.5m in the flight direction

**In centering phase (FOCUS_SEARCH_SPEED_MPS = 5 m/s)**:
```
lag = 150 ms
distance_traveled = 5 m/s * 0.15 s = 0.75 m
```

**Correction**: Use velocity vector to age GPS position forward:
```
corrected_lat, corrected_lon = offset_gps_by_distance(
    drone_lat, drone_lon,
    north_m = velocity_north_mps * lag_s,
    east_m = velocity_east_mps * lag_s
)
```

**Without correction**: σ_lag = 1.5m (search), 0.75m (centering).
**With velocity correction**: σ_lag ≈ 0.1-0.2m (residual IMU/velocity error).

**Conservative contribution**: σ_lag ≈ 0.3-0.5m if no correction applied, ~0.1m if corrected.

---

### 6. Camera Mounting Offset (σ_offset)

**Source**: Camera not perfectly nadir (directly below drone) or slightly off-centre on frame.

**Specification**: IMX296 mounted on Pi with housing.
- Estimated misalignment: ±2-3 degrees from nadir
- Lateral offset from body centre: ±10-20mm

**Misalignment impact** at 35m altitude:
- 2° tilt → projects ground point upward by 35 * tan(2°) ≈ 1.2 m
- 3° tilt → 2.0 m error

**Lateral offset** of 15mm:
- At 35m altitude with focal length 5.46mm: projects to ~95m on ground (extreme divergence)
- More realistically: if camera tilted, offset is absorbed in yaw/pitch errors

**Mitigation**: Camera should be mounted as nadir as possible. If not calibrated, treat as additional yaw error.

**Conservative contribution**: σ_offset ≈ 0.5-1.0m if not calibrated.

---

## Total Error Budget: Root Sum Square (RSS)

### At TARGET_ALT = 35m (Search Phase)

Assuming independent error sources:

```
σ_total = sqrt(σ_gps² + σ_alt² + σ_yaw² + σ_quantization² + σ_lag² + σ_offset²)
```

**Conservative scenario** (worst reasonable assumptions):
```
σ_gps = 2.3 m (GPS CEP95)
σ_alt = 0.5 m (barometer ±0.5m, scaled by geometry)
σ_yaw = 0.6 m (Cube compass ±5°)
σ_quantization = 0.01 m (negligible)
σ_lag = 0.3 m (lag corrected with velocity)
σ_offset = 0.5 m (camera mount uncertainty)

σ_total = sqrt(2.3² + 0.5² + 0.6² + 0.01² + 0.3² + 0.5²)
        = sqrt(5.29 + 0.25 + 0.36 + 0.0001 + 0.09 + 0.25)
        = sqrt(6.22) ≈ 2.5 m (CEP, one measurement)
```

**Optimistic scenario** (with corrections in place):
```
σ_gps = 1.5 m (GPS noise floor, 1σ)
σ_alt = 0.1 m (barometer stable, geometry cancellation)
σ_yaw = 0.2 m (Cube compass ±2°)
σ_quantization = 0.01 m (negligible)
σ_lag = 0.1 m (velocity-corrected)
σ_offset = 0.2 m (camera well-mounted)

σ_total = sqrt(1.5² + 0.1² + 0.2² + 0.01² + 0.1² + 0.2²)
        = sqrt(2.25 + 0.01 + 0.04 + 0.0001 + 0.01 + 0.04)
        = sqrt(2.35) ≈ 1.5 m (CEP, one measurement)
```

### At VERIFY_ALT = 15m (Centering Phase)

GSD shrinks: GSD = (5.02 * 15) / 7948.76 = 9.48 mm/pixel

Pixel offsets now represent smaller ground distances → some errors shrink.

```
σ_gps = 2.3 m (GPS independent of altitude)
σ_alt = 0.1 m (smaller geometry impact)
σ_yaw = 0.3 m (smaller ground offsets at lower altitude)
σ_lag = 0.75 m (5 m/s * 150ms, or 0.1m if corrected)
σ_quantization = 0.005 m
σ_offset = 0.3 m (offset doesn't scale with altitude)

Conservative (uncorrected lag): σ_total ≈ sqrt(2.3² + 0.1² + 0.3² + 0.75² + 0.005² + 0.3²)
                                        ≈ sqrt(6.68) ≈ 2.6 m

Optimistic (corrected lag): σ_total ≈ sqrt(2.3² + 0.1² + 0.3² + 0.1² + 0.005² + 0.3²)
                                     ≈ sqrt(5.38) ≈ 2.3 m
```

---

## Multi-Observation Averaging

The GPS estimation scripts (pi_flight.py, main.py) use **inverse-variance weighting** to combine multiple observations:

```python
weight = 1.0 / (altitude²)  # Lower altitude → higher confidence
weighted_avg = sum(estimate * weight) / sum(weight)
```

**Effect**: With N independent observations, σ improves as 1/sqrt(N).

| N Observations | Improvement Factor | Single Error 2.5m → Avg |
|---|---|---|
| 1 | 1.0x | 2.5 m |
| 4 | 2.0x | 1.25 m |
| 9 | 3.0x | 0.83 m |
| 16 | 4.0x | 0.63 m |
| 25 | 5.0x | 0.5 m |

**In practice during approach**:
- Search phase: ~10-20 detections over 30-60s descent → ~3-5x improvement
- Centering phase: constant hovering with 10+ detections → 3-4x improvement

**Realistic combined accuracy**: 1.5-2.0m at 35m (search), 1.0-1.5m at 15m (centering).

---

## Offset Landing Distance (7.5m)

Given typical GPS estimation error of **1.5-2.5m**, the 7.5m offset landing distance is designed to:

1. **Avoid collision with target**: 7.5m > 2.5m (max reasonable error)
2. **Provide safe margin**: Assumes potential 5-10m landing scatter
3. **Enable visual confirmation**: Operator can see target and confirm safe landing area

**Landing position probability** (assuming 2.0m Gaussian error):

```
P(landing within X m of true target) = 1 - exp(-X²/2σ²)

At X = 7.5m, σ = 2.0m:
P = 1 - exp(-(7.5²)/(2*2²)) = 1 - exp(-7.03) ≈ 99%
```

**Improvement from GPS averaging** (if N=9 observations → 0.83m error):

```
At X = 7.5m, σ = 0.83m:
P = 1 - exp(-(56.25)/(2*0.69)) ≈ 100%
```

---

## Improvement Strategies

### Strategy 1: Multi-Pass Centering (GPS Averaging)

**Current**: Single descent pass, collect 4-8 detections.

**Improvement**: Three descending passes to collect 15-25 detections per altitude.

**Gain**: σ → σ/sqrt(N) = 2.5m / 5 ≈ **0.5m accuracy**.

**Trade-off**: +90-120s flight time, higher fuel cost.

**Recommendation**: ✓ Implement for improved landing accuracy.

---

### Strategy 2: Velocity-Corrected GPS Lag

**Current**: Assumes lag ≈ 0 (or ignored).

**Improvement**: Extract velocity from telemetry, offset GPS position forward by velocity * lag_time.

**Gain**: Eliminates ~0.5-1.5m systematic error from lag.

**Trade-off**: +3 lines of code in main.py / pi_flight.py.

**Recommendation**: ✓ Implement immediately (quick fix, high impact).

---

### Strategy 3: Yaw Calibration

**Current**: Trust Cube compass (±5° error possible).

**Improvement**: Ground truth yaw calibration using visual landmarks before flight.

**Gain**: Reduces σ_yaw from 0.6m → 0.2m.

**Trade-off**: 2-3 min calibration overhead on flight day.

**Recommendation**: ✓ Implement if compass-related failures observed.

---

### Strategy 4: Camera Lens Undistortion

**Current**: Lens calibration done (2026-03-11), undistortion applied in vision.py.

**Gain**: Already implemented — removes ~10-20% lens distortion error.

**Status**: ✓ Done. Precomputed remap in vision.py, negligible runtime cost.

---

### Strategy 5: Altitude-Adaptive GSD Calibration

**Current**: FOCAL_LENGTH_MM = 5.46 (calibrated once at 1m).

**Improvement**: Measure GSD at multiple altitudes, fit polynomial to account for atmospheric focus shift.

**Gain**: Reduces σ_alt from 0.5m → 0.1m, reduces σ_yaw indirectly.

**Trade-off**: 30min calibration + code change.

**Recommendation**: △ Post-flight optimization (nice-to-have).

---

### Strategy 6: Sensor Fusion (Barometer + Visual Height Estimation)

**Current**: Trust barometer alone.

**Improvement**: Estimate altitude from detection size (dummy apparent size shrinks with altitude), fuse with barometer.

**Gain**: Reduces σ_alt → 0.05m, improves GSD scaling.

**Trade-off**: Requires dummy height in detection pipeline, moderate complexity.

**Recommendation**: △ Post-flight research.

---

## Field Testing Recommendations

### Day 1: GPS Accuracy Experiment

**Run**: `tests/day_1_experiments/gps_accuracy.py --dummy-gps LAT,LON --headless --stream`

**Protocol**:
1. Measure dummy GPS position precisely (walk to it with phone).
2. Pilot manually hovers above dummy at 10m, 15m, 20m, 25m, 30m, 35m.
3. Script records 20-30 detections per altitude.
4. CSV output: error vs altitude vs confidence.

**Success criteria**:
- Mean error < 3m at all altitudes
- Error reduces with averaging (>5 observations per altitude)
- No altitude-dependent bias (suggests FOV/yaw calibration is good)

### Day 1: GPS Drift Experiment

**Run**: `tests/day_1_experiments/gps_drift.py --headless --duration 120`

**Protocol**:
1. Pilot hovers in place for 120 seconds at 15-20m altitude.
2. Script logs raw GPS at 4Hz, computes CEP50/CEP95.

**Success criteria**:
- CEP95 < 3m (tight GPS)
- No significant drift trend (receiver stable)
- Altitude varies < 1m (pilot steady)

### Centering Phase: Real-World Test

**When**: First full flight after confirming GPS accuracy.

**Metrics**:
1. Count detections during centering approach.
2. Log final landing position vs estimated target.
3. Post-flight: compare GPS estimate (from flight log) vs true target (ground measurement).

**Expected outcome**:
- Landing accuracy ±1-2m with 7.5m offset (conservative case).
- Accuracy ±0.5-1m if averaging applied over multiple detections.

---

## Summary Table

| Error Source | 35m Altitude | 15m Altitude | Notes |
|---|---|---|---|
| GPS receiver | 2.3m | 2.3m | Dominant error, independent of altitude |
| Barometer | 0.5m | 0.1m | Scales with GSD |
| Compass yaw | 0.6m | 0.3m | Smaller ground offset at lower alt |
| Pixel quantization | 0.01m | 0.005m | Negligible |
| GPS timing lag | 0.3m* | 0.1m* | *With velocity correction; 1.5m without |
| Camera mount | 0.5m | 0.5m | Altitude-independent if fixed offset |
| **Total (RSS)** | **2.5m** | **2.3m** | Conservative scenario |
| **With averaging (N=9)** | **0.8m** | **0.8m** | Multi-pass approach |

---

## Conclusion

The pixel-to-GPS estimation pipeline achieves:

- **1.5-2.5m accuracy** with a single observation at any altitude
- **0.5-1.0m accuracy** with 9+ averaged observations
- **Dominant errors**: GPS receiver noise (2-3m), followed by yaw (0.3-0.6m)
- **Smallest errors**: pixel quantization, altitude barometer (with correction)

The 7.5m offset landing distance provides 99%+ probability of safe landing within the margin of error, even with conservative assumptions.

**Recommended next steps**:
1. Run Day 1 GPS accuracy + drift experiments to validate real-world numbers.
2. Implement velocity-corrected GPS lag (code change 3 lines).
3. Enable multi-observation averaging in centering phase (already in code).
4. Monitor landing scatter on first flights; adjust offset distance if needed.

---

## References

- `gps_utils.py`: Conversion formulas
- `config.py`: Camera calibration values
- `main.py`, `pi_flight.py`: Real-world GPS estimation implementation
- `tests/day_1_experiments/gps_accuracy.py`: Field validation script
- `tests/day_1_experiments/gps_drift.py`: GPS noise floor measurement
- MEMORY.md (2026-03-11): Field test benchmark data
