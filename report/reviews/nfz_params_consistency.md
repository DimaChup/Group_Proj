# NFZ Parameters Consistency Check

Verified: 2026-03-29

## Config Values (config.py, lines 113-123)

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `NFZ_SLOW_ZONE_M` | **20.0** | Speed scalar field active within this distance |
| `NFZ_SCALAR_ZERO_M` | **2.0** | Speed drops to 0 at this distance |
| `NFZ_MIN_SPEED_MPS` | **0.0** | Speed at SCALAR_ZERO_M and below |
| `NFZ_ZONE_MAX_SPEED_MPS` | **3.0** | Speed at outer edge of slow zone |
| `NFZ_WAYPOINT_BUFFER_M` | **30.0** | Skip waypoints within this of NFZ |

### speed_for_altitude (config.py, lines 68-75)
Linear interpolation: 6 m/s at 20m, 10 m/s at 50m. Correct formula confirmed.

---

## File-by-File Comparison

### 1. pattern_visualizer.py (lines 605-617)

**Reads parameters from:** `config.NFZ_SCALAR_ZERO_M`, `config.NFZ_MIN_SPEED_MPS`, `config.NFZ_SLOW_ZONE_M`, `config.NFZ_ZONE_MAX_SPEED_MPS` -- all direct config references.

**Speed ramp formula:**
```python
if is_inside or dist_m <= config.NFZ_SCALAR_ZERO_M:
    target = config.NFZ_MIN_SPEED_MPS          # = 0.0
elif dist_m < config.NFZ_SLOW_ZONE_M:
    ratio = (dist_m - config.NFZ_SCALAR_ZERO_M) / (config.NFZ_SLOW_ZONE_M - config.NFZ_SCALAR_ZERO_M)
    target = min(ratio * config.NFZ_ZONE_MAX_SPEED_MPS, cruise_speed)
```

**Cruise speed:** `config.speed_for_altitude(alt)` -- CORRECT.

**VERDICT: MATCHES main.py non-directional mode.** No hardcoded values.

---

### 2. pattern_compare.py (lines 74-77, 166-190)

**Reads parameters from:** Local aliases copied at module level:
```python
NFZ_SLOW_ZONE_M = config.NFZ_SLOW_ZONE_M         # 20.0
NFZ_SCALAR_ZERO_M = config.NFZ_SCALAR_ZERO_M      # 2.0
NFZ_MIN_SPEED_MPS = config.NFZ_MIN_SPEED_MPS      # 0.0
NFZ_ZONE_MAX_SPEED = config.NFZ_ZONE_MAX_SPEED_MPS # 3.0
```

**Speed ramp formula (nfz_speed_scalar, line 166):**
```python
if point_in_polygon(px, py, nfz_poly):
    return max(NFZ_MIN_SPEED_MPS, 0.1)             # <-- MISMATCH: floors to 0.1
if dist < NFZ_SCALAR_ZERO_M:
    return max(NFZ_MIN_SPEED_MPS, 0.1)             # <-- MISMATCH: floors to 0.1
if dist < NFZ_SLOW_ZONE_M:
    ratio = (dist - NFZ_SCALAR_ZERO_M) / (NFZ_SLOW_ZONE_M - NFZ_SCALAR_ZERO_M)
    speed = NFZ_MIN_SPEED_MPS + ratio * (NFZ_ZONE_MAX_SPEED - NFZ_MIN_SPEED_MPS)
    return min(speed, cruise_speed)                 # <-- MISMATCH: different ramp formula
```

**Cruise speed:** `config.speed_for_altitude(alt)` (line 684) -- CORRECT.

**MISMATCHES FOUND:**

| Issue | pattern_compare.py | main.py (actual drone) | pattern_visualizer.py |
|-------|-------------------|----------------------|----------------------|
| Inside NFZ speed | `max(0.0, 0.1)` = **0.1** | Force MANUAL mode (no speed) | **0.0** |
| At SCALAR_ZERO_M | `max(0.0, 0.1)` = **0.1** | **0.0** (directional) or **0.0** (total) | **0.0** |
| Ramp formula | `MIN + ratio * (MAX - MIN)` = `0 + ratio * 3` = `ratio * 3` | `ratio * MAX` = `ratio * 3` | `ratio * MAX` = `ratio * 3` |
| Speed cap | `min(speed, cruise)` | `max(0.3, allowed)` (directional) or raw `max_spd` (total) | `min(target, cruise)` |

---

### 3. main.py _enforce_geofence (lines 666-801)

**Two modes:**

**Directional mode** (default, `NFZ_DIRECTIONAL = True`):
```python
if nfz_dist <= config.NFZ_SCALAR_ZERO_M:
    max_approach = 0.0
else:
    ratio = (nfz_dist - config.NFZ_SCALAR_ZERO_M) / (config.NFZ_SLOW_ZONE_M - config.NFZ_SCALAR_ZERO_M)
    max_approach = ratio * config.NFZ_ZONE_MAX_SPEED_MPS
# Only limits approach component, not total speed
```

**Total speed mode** (`--nfz-total-speed` flag):
```python
if nfz_dist <= config.NFZ_SCALAR_ZERO_M:
    max_spd = 0.0
else:
    ratio = (nfz_dist - config.NFZ_SCALAR_ZERO_M) / (config.NFZ_SLOW_ZONE_M - config.NFZ_SCALAR_ZERO_M)
    max_spd = ratio * config.NFZ_ZONE_MAX_SPEED_MPS
self.nav.set_speed(max_spd)
```

**Manual speed calculation** (lines 671-676):
```python
if nfz_dist <= config.NFZ_SCALAR_ZERO_M:
    self._nfz_manual_max_speed = 0.3    # <-- hardcoded 0.3, not NFZ_MIN_SPEED_MPS (0.0)
else:
    ratio = ... same formula ...
    self._nfz_manual_max_speed = ratio * config.NFZ_ZONE_MAX_SPEED_MPS
```

---

## Summary of Mismatches

### MISMATCH 1: pattern_compare.py floors speed to 0.1 m/s inside NFZ
- **pattern_compare.py:** `max(NFZ_MIN_SPEED_MPS, 0.1)` = 0.1 m/s
- **main.py:** 0.0 m/s (or force MANUAL if inside)
- **pattern_visualizer.py:** 0.0 m/s (correct)
- **Impact:** Compare tool slightly overestimates speed inside/at NFZ boundary. Affects time estimates near NFZ.
- **Fix:** Remove the `max(..., 0.1)` floor or match main.py behavior.

### MISMATCH 2: pattern_compare.py ramp starts from NFZ_MIN_SPEED (additive formula)
- **pattern_compare.py:** `NFZ_MIN_SPEED_MPS + ratio * (NFZ_ZONE_MAX_SPEED - NFZ_MIN_SPEED_MPS)` = `0 + ratio * (3 - 0)` = `ratio * 3`
- **main.py / visualizer:** `ratio * NFZ_ZONE_MAX_SPEED_MPS` = `ratio * 3`
- **Impact:** With current config (MIN=0.0), the formulas are **numerically identical**. But if NFZ_MIN_SPEED_MPS were changed to a non-zero value, they would diverge. The compare tool's formula is arguably more correct (ramps from MIN to MAX), while main.py and the visualizer always ramp from 0 to MAX regardless of MIN.
- **Status:** No current impact, but a latent inconsistency.

### MISMATCH 3: main.py manual speed floors to 0.3 at SCALAR_ZERO_M
- **main.py line 673:** `self._nfz_manual_max_speed = 0.3` (hardcoded)
- **config.py:** `NFZ_MIN_SPEED_MPS = 0.0`
- **Impact:** In MANUAL mode, drone can still creep at 0.3 m/s near NFZ boundary. Neither tool models this. Not a visualization concern but worth noting.

### MISMATCH 4: Directional vs total speed mode not modeled in tools
- **main.py default:** Only limits the approach *component* of velocity (directional). Drone can fly fast parallel to NFZ.
- **Both tools:** Cap *total speed* (non-directional model).
- **Impact:** Tools underestimate actual drone speed near NFZ when flying parallel to boundary. Time estimates are conservative (longer than reality).
- **Severity:** Medium. For report figures this is acceptable (conservative estimate). For operational planning it overstates NFZ time penalty.

### NO MISMATCH: speed_for_altitude
All three files use `config.speed_for_altitude()` which reads from the same config constants. The function is defined once in config.py (lines 68-75) and returns:
- 6.0 m/s at 20m
- 7.33 m/s at 30m (by interpolation: 6 + (30-20)/(50-20) * 4 = 7.33)
- 8.0 m/s at 35m (by interpolation: 6 + (35-20)/(50-20) * 4 = 8.0)
- 10.0 m/s at 50m

### NO MISMATCH: NFZ_SLOW_ZONE_M value
Config says **20.0m** (not 40.0 as stated in the user prompt). All three files read this same value from config. No hardcoded overrides found.

---

## User's Stated Values vs Actual Config

| Parameter | User stated | Actual config.py | Match? |
|-----------|------------|-------------------|--------|
| NFZ_SLOW_ZONE_M | 40.0 | **20.0** | NO -- user's value is wrong |
| NFZ_SCALAR_ZERO_M | 2.0 | 2.0 | YES |
| NFZ_MIN_SPEED_MPS | 0.0 | 0.0 | YES |
| NFZ_ZONE_MAX_SPEED_MPS | 3.0 | 3.0 | YES |

---

## Recommended Fixes

1. **pattern_compare.py line 178, 183:** Remove `max(..., 0.1)` floor -- use `NFZ_MIN_SPEED_MPS` directly (currently 0.0). The `max(current_speed, 0.05)` on line 489 already prevents division-by-zero in the physics loop.

2. **Optional:** Add a note/comment to both tools that they model total-speed capping, not directional (which is main.py's default). This is acceptable for report figures but should be documented.

3. **No action needed** on speed_for_altitude -- all files use the same config function correctly.
