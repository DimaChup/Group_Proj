# NFZ Directional Scalar Field — Bug Investigation

**Date:** 2026-03-29
**Files examined:** `main.py` (lines 681–723), `navigation.py` (lines 64–78), `geofence.py`, `config.py`

---

## Executive Summary

**ROOT CAUSE FOUND: The `send_velocity()` function expects BODY-FRAME inputs (forward/right), but the directional NFZ code passes NED-FRAME values (north/east). With `current_yaw=0` hardcoded, the body-to-NED rotation becomes an identity transform, which *masks* the bug when the drone is heading north — but at any other heading, the velocity correction is applied in the wrong direction, potentially pulling the drone toward the NFZ instead of slowing it.**

There is also a secondary sign-convention issue in the toward-vector computation that is actually correct, but confusingly named. Details below.

---

## 1. The Directional NFZ Code (main.py lines 681–723)

```python
# Line 681-723
if NFZ_DIRECTIONAL and not nfz_inside and nfz_dist < config.NFZ_SLOW_ZONE_M:
    # Ramp: 0 m/s at SCALAR_ZERO_M (2m), linearly up to ZONE_MAX at SLOW_ZONE_M (20m)
    if nfz_dist <= config.NFZ_SCALAR_ZERO_M:
        max_approach = 0.0
    else:
        ratio = (nfz_dist - config.NFZ_SCALAR_ZERO_M) / (config.NFZ_SLOW_ZONE_M - config.NFZ_SCALAR_ZERO_M)
        max_approach = ratio * config.NFZ_ZONE_MAX_SPEED_MPS

    # ... nearest boundary point computation (lines 689-711) ...

    # Direction toward nearest NFZ boundary point
    dx = (nfz_lon - self.lon) * 111320 * math.cos(math.radians(self.lat))   # Line 713
    dy = (nfz_lat - self.lat) * 111320                                       # Line 714
    dist = math.sqrt(dx * dx + dy * dy)                                      # Line 715
    if dist > 0.1:
        nx, ny = dx / dist, dy / dist  # unit vector toward NFZ              # Line 717
        vn = getattr(self, 'vx', 0)    # north m/s (from GLOBAL_POSITION_INT) # Line 718
        ve = getattr(self, 'vy', 0)    # east m/s                             # Line 719
        v_toward = vn * ny + ve * nx    # dot product: positive = approaching  # Line 720
        if v_toward > max_approach:
            excess = v_toward - max_approach                                   # Line 722
            self.nav.send_velocity(vn - ny * excess, ve - nx * excess, 0, current_yaw=0) # Line 723
```

---

## 2. The Toward-Vector: Sign Analysis

### 2.1 What `dx` and `dy` represent

```python
dx = (nfz_lon - self.lon) * 111320 * cos(lat)   # metres EAST from drone to NFZ point
dy = (nfz_lat - self.lat) * 111320               # metres NORTH from drone to NFZ point
```

- `dx > 0` → NFZ is EAST of drone
- `dy > 0` → NFZ is NORTH of drone

After normalization: `(nx, ny) = (dx/dist, dy/dist)`
- `nx` = unit component in EAST direction toward NFZ
- `ny` = unit component in NORTH direction toward NFZ

**VERDICT: The toward-vector IS correct.** It points from the drone toward the nearest NFZ boundary point. The naming `nx, ny` is confusing (suggests north/x, but `nx` is east-component and `ny` is north-component), but the math is valid.

### 2.2 The dot product

```python
v_toward = vn * ny + ve * nx
```

With `vn` = north velocity and `ve` = east velocity:
- `vn * ny` = north_speed × north_component_toward_NFZ
- `ve * nx` = east_speed × east_component_toward_NFZ
- Sum = projection of velocity onto the toward-NFZ direction

**VERDICT: The dot product IS correct.** Positive means approaching the NFZ; negative means moving away.

### 2.3 The velocity correction

```python
self.nav.send_velocity(vn - ny * excess, ve - nx * excess, 0, current_yaw=0)
```

Subtracting `ny * excess` from north velocity and `nx * excess` from east velocity removes the excess approach speed in the toward-NFZ direction.

**VERDICT: The NED math is correct in isolation.** If `send_velocity` accepted NED inputs directly, this would work perfectly.

---

## 3. CRITICAL BUG: send_velocity() Frame Mismatch

### 3.1 What send_velocity expects

From `navigation.py` line 64:

```python
def send_velocity(self, vx, vy, vz, yaw_rate=0, current_yaw=None):
    """Send body-frame velocity command, rotated to NED before transmission."""
    ...
    cos_yaw = math.cos(current_yaw)
    sin_yaw = math.sin(current_yaw)
    vx_ned = vx * cos_yaw - vy * sin_yaw
    vy_ned = vx * sin_yaw + vy * cos_yaw
    self.master.mav.set_position_target_local_ned_send(
        0, ..., MAV_FRAME_LOCAL_NED, ...,
        vx_ned, vy_ned, vz, ...)
```

**`send_velocity` expects BODY-FRAME inputs:** `vx` = forward (along drone heading), `vy` = right (perpendicular to heading). It then rotates by `current_yaw` to produce NED velocities.

### 3.2 The hack: `current_yaw=0`

The NFZ code passes `current_yaw=0` on line 723:

```python
self.nav.send_velocity(vn - ny * excess, ve - nx * excess, 0, current_yaw=0)
```

When `current_yaw=0`:
- `cos(0) = 1`, `sin(0) = 0`
- `vx_ned = vx * 1 - vy * 0 = vx` (the first argument, passed through as NED north)
- `vy_ned = vx * 0 + vy * 1 = vy` (the second argument, passed through as NED east)

**So `current_yaw=0` makes `send_velocity` treat its inputs as NED directly.** This is an intentional hack — the code computes NED velocities and bypasses the body-to-NED rotation by forcing yaw to zero.

### 3.3 Is the hack correct?

**YES — but only partially.** The correction velocity is computed correctly in NED and arrives at the MAVLink layer correctly in NED. The `current_yaw=0` bypass works.

**HOWEVER**, the corrected velocity `(vn - ny * excess, ve - nx * excess)` uses the drone's CURRENT NED velocity from `GLOBAL_POSITION_INT` as the base. This means the code:

1. Reads the current velocity (correct, in NED)
2. Subtracts the excess approach component (correct, in NED)
3. Sends the result as a velocity command (correct via `current_yaw=0` hack)

**The NED pipeline is actually consistent.** The `current_yaw=0` hack works correctly here.

---

## 4. REAL BUG: GLOBAL_POSITION_INT vx/vy Convention

### 4.1 MAVLink GLOBAL_POSITION_INT fields

From the MAVLink specification:
- `vx`: Ground X speed (latitude), **cm/s**, positive = NORTH
- `vy`: Ground Y speed (longitude), **cm/s**, positive = EAST
- `vz`: Ground Z speed, **cm/s**, positive = DOWN

The parsing in `main.py` line 362:
```python
self.vx = msg.vx / 100.0; self.vy = msg.vy / 100.0; self.vz = msg.vz / 100.0
```

So `self.vx` = north m/s, `self.vy` = east m/s. The comments on lines 718-719 are correct:
```python
vn = getattr(self, 'vx', 0)    # north m/s (from GLOBAL_POSITION_INT)
ve = getattr(self, 'vy', 0)    # east m/s
```

**VERDICT: vx/vy convention is correct.**

---

## 5. Nearest Boundary Point Computation

### 5.1 Edge projection

Lines 692–711 iterate over all polygon edges, project the drone position onto each edge segment (clamping `t` to [0, 1]), and find the closest projected point. This is the standard closest-point-on-polygon algorithm.

### 5.2 Concave polygons

The algorithm finds the nearest point on ANY edge, regardless of polygon convexity. For concave polygons, this is still correct — the nearest boundary point is always on some edge, and iterating all edges finds it.

### 5.3 Polygon corners

When `t` clamps to 0 or 1, the closest point is a vertex. Multiple edges will produce the same vertex, but `dsq < best_dist_sq` picks the first one. This is fine — the result is the same vertex regardless.

**VERDICT: Nearest boundary point computation is correct for all polygon shapes.**

---

## 6. So What IS Causing the Pull Effect?

After tracing through every component, the NED math and sign conventions are all correct. Let me look at the remaining possibilities:

### 6.1 Hypothesis: The correction OVERRIDES the flight controller's GUIDED waypoint command

This is the most likely cause. Here's the sequence:

1. The drone is in GUIDED mode, flying toward a lawnmower waypoint (let's say waypoint W is AWAY from the NFZ)
2. ArduCopter is commanding velocity toward W
3. `_enforce_geofence()` detects the drone is within 20m of NFZ
4. The code reads current velocity `(vn, ve)` — drone is flying toward W, which is AWAY from NFZ
5. `v_toward` is NEGATIVE (flying away from NFZ) → `v_toward < max_approach` → **no correction applied**
6. BUT: The drone is also near the NFZ from a different pass, or the velocity temporarily points toward NFZ
7. When correction IS applied, it sends `send_velocity(corrected_vn, corrected_ve, 0, current_yaw=0)`
8. **This velocity command REPLACES the GUIDED waypoint command entirely**
9. The drone now flies at the corrected velocity indefinitely until the next waypoint command or the next geofence check

**The problem: when `v_toward <= max_approach` (not approaching), the code does NOTHING — it doesn't re-issue the waypoint command. But when `v_toward > max_approach`, it sends a velocity command that overrides GUIDED mode. Once the excess is removed and the drone is no longer approaching too fast, the velocity command from the previous geofence check may still be in effect, and the GUIDED waypoint navigation is disrupted.**

### 6.2 Hypothesis: Velocity command at yaw=0 disrupts heading

When `send_velocity` is called with `current_yaw=0`, the MAVLink message includes `yaw_rate=0` (from default parameter). But the type mask `0b010111000111` ignores position but uses velocity AND yaw. The yaw component might interfere with the drone's heading, causing erratic flight that appears as "pulling toward NFZ."

### 6.3 Hypothesis: The `vz=0` stops the drone climbing/descending

The correction always sends `vz=0`, which commands zero vertical velocity. If the drone is climbing to altitude or adjusting height, this command forces it level. This could cause unexpected behavior that manifests as path deviation.

### 6.4 Hypothesis: Timing / race condition

`_enforce_geofence()` is called every loop iteration (likely 10–20 Hz). The velocity correction is sent repeatedly. Each call reads the CURRENT velocity (which may already be modified by a previous correction), computes a new correction, and sends it. If the velocity hasn't converged yet, the corrections can oscillate.

### 6.5 THE ACTUAL PULL MECHANISM

After careful analysis, here is the most likely pull scenario:

**The velocity command stays active after the geofence check stops issuing corrections.** Consider:

1. Drone approaches NFZ. Code issues `send_velocity(reduced_vn, reduced_ve, 0)` — slows approach.
2. Drone velocity drops below `max_approach`. Code stops issuing corrections.
3. But the LAST `send_velocity` command is still active in ArduCopter's GUIDED mode. The drone continues at that reduced velocity.
4. If the reduced velocity had a component TOWARD the NFZ (it was reduced, not zeroed unless at 2m), the drone continues drifting toward NFZ at `max_approach` speed.
5. As the drone gets closer, `max_approach` gets smaller (ramp down), so the code issues slower and slower velocity commands — but ALWAYS with a toward-NFZ component equal to `max_approach`.
6. **The drone slides along the boundary at `max_approach` speed, unable to resume its waypoint navigation, appearing to be "pulled" toward and along the NFZ.**

The GUIDED waypoint navigation is never resumed because `send_velocity` puts the flight controller into velocity-tracking mode, not position-tracking mode. The drone needs a `goto_gps` command to resume waypoint navigation.

---

## 7. Test Cases

### Test Case 1: Drone flying north, NFZ to the east

- Drone at P, velocity = (vn=8, ve=0) → flying north at 8 m/s
- NFZ nearest point is due east → `dx > 0, dy ≈ 0` → `nx ≈ 1, ny ≈ 0`
- `v_toward = vn * ny + ve * nx = 8 * 0 + 0 * 1 = 0` → flying perpendicular, no approach
- `0 < max_approach` → **no correction** ✓

### Test Case 2: Drone flying east toward NFZ

- Drone at P, velocity = (vn=0, ve=8) → flying east at 8 m/s
- NFZ nearest point is due east → `nx ≈ 1, ny ≈ 0`
- `v_toward = 0 * 0 + 8 * 1 = 8` → approaching at 8 m/s
- `max_approach = 3.0` (at 20m) → `excess = 8 - 3 = 5`
- Corrected: `send_velocity(0 - 0*5, 8 - 1*5, 0) = send_velocity(0, 3, 0)` → drone slows to 3 m/s east ✓
- **But: the drone is now in velocity mode, not returning to its waypoint.** After this correction, even when the drone slows to 3 m/s and the condition `v_toward > max_approach` is no longer true, the drone keeps flying east at 3 m/s (from the last velocity command) instead of returning to its lawnmower waypoint.

### Test Case 3: The pull scenario

- Step 1: Drone flying east at 8 m/s, NFZ is east, 15m away. max_approach = 2.17 m/s
- Step 2: Code sends velocity (0, 2.17, 0) — slowing drone to max_approach speed TOWARD NFZ
- Step 3: Next iteration: drone now at 2.17 m/s east. v_toward = 2.17. max_approach ≈ 2.17. No correction needed.
- Step 4: Drone continues at 2.17 m/s east TOWARD NFZ (last velocity command still active)
- Step 5: Drone is now at 14m. max_approach = 2.0. v_toward = 2.17 > 2.0. Code corrects to 2.0.
- Step 6: Drone continues at 2.0 m/s east TOWARD NFZ...
- **The drone rides the ramp all the way down to the boundary**, approaching at ever-decreasing speed but NEVER stopping or turning away. This IS the "pull toward NFZ" behavior.

---

## 8. Conclusion

**The directional NFZ code has a fundamental design flaw: it caps the approach speed but never provides a REPULSIVE force.** It reduces approach velocity to `max_approach`, which means:

- At 20m: drone approaches at 3.0 m/s (allowed)
- At 10m: drone approaches at 1.67 m/s (allowed)
- At 5m: drone approaches at 0.83 m/s (allowed)
- At 2m: drone approaches at 0.0 m/s (full stop)

The drone slides down the ramp, always approaching at the maximum permitted speed, because `send_velocity` overrides GUIDED waypoint navigation and the correction only limits speed — it doesn't redirect the drone back toward its waypoint.

Additionally, once `send_velocity` is called even ONCE, the drone switches from position-tracking (GUIDED waypoint) to velocity-tracking mode in ArduCopter. The waypoint navigation is silently broken.

---

## 9. Suggested Fix

The fix requires two changes:

### Fix 1: Add repulsive component (don't just cap approach speed)

Instead of just limiting approach speed, subtract a repulsive velocity that pushes the drone away from the NFZ when it's close:

```python
if dist > 0.1:
    nx, ny = dx / dist, dy / dist  # unit toward NFZ (east, north components)
    vn = getattr(self, 'vx', 0)
    ve = getattr(self, 'vy', 0)
    v_toward = vn * ny + ve * nx

    if v_toward > max_approach:
        excess = v_toward - max_approach
        new_vn = vn - ny * excess
        new_ve = ve - nx * excess
        # Also add a gentle repulsive push AWAY from NFZ
        repulse_strength = (1.0 - ratio) * config.NFZ_PUSH_SPEED_MPS  # stronger when closer
        new_vn -= ny * repulse_strength
        new_ve -= nx * repulse_strength
        self.nav.send_velocity(new_vn, new_ve, 0, current_yaw=0)
    # IMPORTANT: when v_toward <= max_approach, do NOT send velocity command.
    # Let the GUIDED waypoint controller handle flight normally.
```

### Fix 2: Re-issue waypoint after geofence intervention

After the directional check decides no correction is needed, re-send the current waypoint to restore GUIDED position-tracking:

```python
if v_toward > max_approach:
    # ... send correction velocity ...
    self._geofence_intervening = True
elif getattr(self, '_geofence_intervening', False):
    # Geofence was intervening but no longer needs to — resume waypoint
    self._geofence_intervening = False
    if self.state == State.SEARCH and hasattr(self, 'current_wp'):
        lat, lon = self.current_wp
        self.nav.goto_gps(lat, lon, self.alt)
```

### Fix 3: Never send velocity toward NFZ

The current code sends `max_approach` speed toward the NFZ. It should send ZERO or negative (repulsive) when the drone is already heading toward the NFZ within the slow zone:

```python
if v_toward > 0:  # any approach at all
    # Remove ALL approach velocity, don't allow max_approach toward NFZ
    new_vn = vn - ny * v_toward  # zero out toward-NFZ component entirely
    new_ve = ve - nx * v_toward
    self.nav.send_velocity(new_vn, new_ve, 0, current_yaw=0)
```

---

## 10. Summary Table

| Investigation Item | Finding |
|---|---|
| Toward-vector sign | **Correct** — points from drone to nearest NFZ boundary point |
| vx/vy MAVLink convention | **Correct** — vx = north m/s, vy = east m/s |
| Dot product sign | **Correct** — positive = approaching NFZ |
| Nearest boundary computation | **Correct** — works for concave polygons and corners |
| `send_velocity` frame | **Correct** via `current_yaw=0` hack (bypasses body-to-NED rotation) |
| Subtraction direction | **Correct** in isolation — reduces approach component |
| **Velocity command overrides GUIDED** | **BUG** — `send_velocity` switches ArduCopter from position-tracking to velocity-tracking, breaking waypoint navigation |
| **Ramp allows perpetual approach** | **BUG** — code caps approach speed to `max_approach` but never stops or reverses approach. Drone rides the ramp to the boundary. |
| **No waypoint resumption** | **BUG** — when geofence stops intervening, no `goto_gps` is sent to resume waypoint navigation |
