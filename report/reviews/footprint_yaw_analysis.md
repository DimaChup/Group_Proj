# Camera Ground Footprint vs Drone Yaw: Analysis

## 1. Camera and Sensor Parameters

From `config.py`:

| Parameter | Value |
|-----------|-------|
| `SENSOR_WIDTH_MM` | 5.02 mm |
| `FOCAL_LENGTH_MM` | 5.46 mm |
| `IMAGE_W` | 1456 px |
| `IMAGE_H` | 1088 px |
| `TARGET_ALT` | 35 m |
| `DIAGONAL_YAW_OFFSET_DEG` | 0 (disabled) |

The sensor width (5.02 mm) corresponds to the 1456-pixel dimension. The sensor height is derived from the aspect ratio:

```
sensor_height = SENSOR_WIDTH_MM * (IMAGE_H / IMAGE_W)
              = 5.02 * (1088 / 1456)
              = 3.75 mm
```

---

## 2. Ground Footprint at 35 m Altitude

The ground footprint is a rectangle projected from the camera sensor through the lens:

```
ground_width  = SENSOR_WIDTH_MM * altitude / FOCAL_LENGTH_MM
              = 5.02 * 35 / 5.46
              = 32.16 m    (along IMAGE_W = 1456 px)

ground_height = ground_width * (IMAGE_H / IMAGE_W)
              = 32.16 * (1088 / 1456)
              = 24.04 m    (along IMAGE_H = 1088 px)
```

The footprint rectangle is **32.16 m x 24.04 m** at 35 m altitude.

The diagonal of the footprint:

```
diagonal = sqrt(32.16^2 + 24.04^2)
         = sqrt(1034.3 + 577.9)
         = sqrt(1612.2)
         = 40.15 m
```

---

## 3. How Yaw Affects Cross-Track Coverage

The drone flies along scan lines. The camera is body-fixed, pointing straight down. What matters for coverage is the **cross-track width** -- how much ground the footprint covers perpendicular to the flight direction.

### Case A: Drone faces along scan line (yaw offset = 0)

The footprint rectangle is aligned with the flight direction. If the drone flies north:
- Along-track (north-south): ground_width = 32.16 m (IMAGE_W dimension)
- **Cross-track (east-west): ground_height = 24.04 m** (IMAGE_H dimension)

This is what `_no_turn = True` assumes. The planner uses `ground_footprint_m * aspect` = 24.04 m as the strip spacing.

### Case B: Drone faces perpendicular to scan line (yaw offset = 90 deg)

- Along-track: ground_height = 24.04 m
- **Cross-track: ground_width = 32.16 m**

This would give 34% more cross-track coverage. But the along-track footprint shrinks, meaning less time-on-target per pass.

### Case C: Drone faces at diagonal angle (yaw offset = 53.2 deg)

When the drone yaws so the footprint diagonal is perpendicular to the flight direction, the cross-track width equals the footprint diagonal:

```
cross_track = diagonal = 40.15 m
```

This is **1.67x the height-aligned cross-track** (40.15 / 24.04 = 1.67).

The required angle:

```
optimal_yaw_offset = atan2(IMAGE_W, IMAGE_H)
                   = atan2(1456, 1088)
                   = atan(1.338)
                   = 53.2 degrees
```

At this angle, the footprint rectangle's corner-to-corner diagonal is exactly perpendicular to the flight direction.

---

## 4. Geometric Proof

Consider the footprint rectangle with width W and height H, rotated by angle theta relative to the flight direction. The cross-track projection (perpendicular to flight) is:

```
cross_track(theta) = W * sin(theta) + H * cos(theta)
```

To find the maximum, take the derivative and set to zero:

```
d/d(theta) [W sin(theta) + H cos(theta)] = W cos(theta) - H sin(theta) = 0
W cos(theta) = H sin(theta)
tan(theta) = W / H
theta_opt = atan(W / H) = atan(32.16 / 24.04) = atan(1.338) = 53.2 deg
```

At this angle:

```
cross_track_max = W * sin(53.2) + H * cos(53.2)
               = 32.16 * 0.800 + 24.04 * 0.600
               = 25.73 + 14.42
               = 40.15 m    (= diagonal, as expected)
```

The along-track projection at the same angle:

```
along_track(theta) = W * cos(theta) + H * sin(theta)
                   = 32.16 * 0.600 + 24.04 * 0.800
                   = 19.30 + 19.23
                   = 38.53 m
```

Note: the along-track projection is NOT the diagonal (it is actually W*cos + H*sin, which differs from the cross-track formula). Both projections sum to the same value by symmetry: both equal `sqrt(W^2 + H^2)` at the optimal angle.

---

## 5. Summary of Cross-Track Width vs Yaw Offset

| Yaw offset | Cross-track (m) | vs baseline | Strip spacing needed |
|------------|-----------------|-------------|---------------------|
| 0 deg (face forward) | 24.04 | baseline | 24.04 m (current `_no_turn`) |
| 53.2 deg (diagonal) | 40.15 | **+67%** | 40.15 m (or ~32 m with 20% overlap) |
| 90 deg (perpendicular) | 32.16 | +34% | 32.16 m |

---

## 6. What `_no_turn` Does in `planning.py`

**Location:** `planning.py` lines 77-83, activated in `main.py` line 211 (`self.planner._no_turn = True`).

When `_no_turn = True`:
- Scales the ground footprint by `IMAGE_H / IMAGE_W` (= 0.747), giving 24.04 m
- Sets overlap to 0.0
- Strip spacing = 24.04 m

When `_no_turn = False` (default):
- Uses the full sensor width footprint: 32.16 m
- Applies 20% overlap
- Strip spacing = 32.16 * 0.8 = 25.73 m

**The implicit assumption of `_no_turn = True`:** The drone faces along the scan line (yaw offset = 0), so the cross-track coverage equals `ground_height` (the IMAGE_H dimension), not `ground_width` (IMAGE_W). The name "no turn" refers to the drone not yawing at U-turns -- it keeps the same heading throughout, which means the narrower IMAGE_H dimension always faces cross-track.

---

## 7. What `DIAGONAL_YAW_OFFSET_DEG` Does

**Location:** `config.py` line 166, applied in `state_machine.py` lines 330-334.

At the start of SEARCH state, the drone yaws to:

```python
yaw_deg = (flight_direction + diag_offset) % 360
```

Where `diag_offset` is either:
- `DIAGONAL_YAW_OFFSET_DEG` if set to a number (currently 0)
- `atan2(IMAGE_W, IMAGE_H)` = 53.2 deg if set to `None` (auto-compute)

**Purpose:** Rotate the drone so the footprint diagonal is cross-track, giving 67% more coverage width per scan line. The drone still follows the same flight path -- only the heading changes.

**Current status:** Disabled (set to 0). Can be enabled by setting to `None` or `53`.

---

## 8. Inconsistency: `_no_turn` Spacing vs Diagonal Yaw

There is a **mismatch** between the strip spacing and the yaw offset:

| Setting | Strip spacing assumes | Actual cross-track |
|---------|----------------------|-------------------|
| `_no_turn=True`, yaw=0 | 24.04 m (correct) | 24.04 m |
| `_no_turn=True`, yaw=53 | 24.04 m (**too tight**) | 40.15 m |
| `_no_turn=False`, yaw=0 | 25.73 m (**wrong**) | 24.04 m (gaps!) |
| `_no_turn=False`, yaw=53 | 25.73 m (close but not exact) | 40.15 m |

**If diagonal yaw is enabled (`DIAGONAL_YAW_OFFSET_DEG = None`):**
- The cross-track width becomes 40.15 m
- But `_no_turn=True` still uses 24.04 m strip spacing
- Result: massive overlap (40%), wasting flight time but no gaps
- To get zero overlap with diagonal yaw: strip spacing should be ~40 m

**If yaw=0 (current config) with `_no_turn=False`:**
- Strip spacing is 25.73 m (80% of 32.16 m sensor width)
- But actual cross-track is only 24.04 m (height dimension)
- Result: **1.7 m gaps between strips** -- coverage holes!
- This is why `_no_turn=True` was introduced: it fixes the strip spacing to match the actual cross-track width when the drone faces forward.

---

## 9. Impact on Mission Coverage

At 35 m altitude over the search area (approx 240 m x 200 m):

| Configuration | Strip spacing | Num scan lines | Total path length (approx) |
|---------------|--------------|----------------|---------------------------|
| `_no_turn=True`, yaw=0 (current) | 24.04 m | ~9 | ~2100 m |
| `_no_turn=True`, yaw=53 (diagonal) | 24.04 m | ~9 (over-covered) | ~2100 m |
| Optimal diagonal (matched spacing) | 40.15 m | ~5-6 | ~1300 m |

Enabling diagonal yaw with matched strip spacing could reduce scan lines from 9 to 6 -- a **33% reduction in flight time** for the same coverage.

---

## 10. Recommendations

1. **Current config (`_no_turn=True`, yaw=0) is correct and safe.** Strip spacing matches actual cross-track width. No gaps.

2. **To enable diagonal yaw optimisation:**
   - Set `DIAGONAL_YAW_OFFSET_DEG = None` (auto-compute 53.2 deg)
   - Update `planning.py` to use the diagonal footprint for strip spacing when diagonal yaw is active:
     ```python
     if config.DIAGONAL_YAW_OFFSET_DEG is None or config.DIAGONAL_YAW_OFFSET_DEG != 0:
         # Diagonal: cross-track = sqrt(ground_w^2 + ground_h^2)
         ground_w = (config.SENSOR_WIDTH_MM * search_alt) / config.FOCAL_LENGTH_MM
         ground_h = ground_w * (config.IMAGE_H / config.IMAGE_W)
         cross_track = math.sqrt(ground_w**2 + ground_h**2)
         swath_m = cross_track * (1.0 - overlap)
     ```
   - Apply modest overlap (10-15%) for safety margin

3. **Do NOT enable diagonal yaw without updating strip spacing.** The current `_no_turn` spacing (24.04 m) with diagonal yaw wastes 40% of flight time on redundant coverage.

4. **The `_no_turn=False` default (without diagonal yaw) has coverage gaps.** It uses SENSOR_WIDTH for spacing but the actual cross-track is IMAGE_H-based. This is only safe if the drone actively yaws to face perpendicular to the scan direction at each strip -- which it does not do in the current codebase.

---

## Appendix: Quick Reference Formulas

```
Ground footprint width  = SENSOR_WIDTH_MM * alt / FOCAL_LENGTH_MM
Ground footprint height = ground_width * (IMAGE_H / IMAGE_W)
Footprint diagonal      = sqrt(width^2 + height^2)

Optimal yaw offset      = atan(IMAGE_W / IMAGE_H) = 53.2 deg
Max cross-track         = footprint diagonal = 1.67 * footprint height

At 35m:  width=32.2m, height=24.0m, diagonal=40.2m
At 25m:  width=23.0m, height=17.2m, diagonal=28.7m
At 50m:  width=46.0m, height=34.3m, diagonal=57.4m
```
