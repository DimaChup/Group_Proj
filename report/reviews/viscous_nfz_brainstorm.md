# Viscous NFZ Buffer Zone -- Brainstorm Analysis

## The Problem

Two control modes both use GUIDED, but behave differently:

| Mode | Command type | Function | State machine states |
|------|-------------|----------|---------------------|
| Navigation | `send_global_target(lat, lon, alt)` | Position control -- ArduCopter flies to waypoint | SEARCH, TRANSIT, CENTERING, DESCENDING |
| Manual | `send_velocity(vx, vy, vz)` | Velocity control -- WASD stick commands | MANUAL |

The current geofence in `_enforce_geofence()` (main.py ~L666-771) already implements **directional speed limiting** for navigation mode via `set_speed()` and a **scalar speed cap** for manual mode via `_nfz_manual_max_speed`. It also has a repulsive push via `send_velocity()` for the inner polygon zone.

**Core tension:** `send_velocity()` from repulsion overrides `send_global_target()` from navigation. ArduCopter processes the last GUIDED command it receives -- a velocity command cancels the position target, causing the drone to abandon its waypoint.

**The viscous fluid goal:** Movement toward the NFZ encounters increasing resistance. Movement away or parallel is unrestricted. Deeper in the buffer = more resistance. At the hard boundary, approach velocity = 0.

---

## Solution Analysis

### Solution 1: Intercept all commands in NavigationController (RECOMMENDED)

**Concept:** Add a `set_nfz_context(geofence, lat, lon, vn, ve)` method to `NavigationController`. Before any `send_velocity` or `send_global_target` is transmitted, decompose the commanded motion into toward-NFZ and away-from-NFZ components, clamp the toward component.

**For `send_velocity` (manual mode):**
1. Compute unit vector toward nearest NFZ boundary point
2. Project commanded velocity onto toward-NFZ axis: `v_toward = dot(v, toward_hat)`
3. If `v_toward > 0` (flying toward NFZ), clamp it: `v_toward = min(v_toward, max_approach)`
4. Reconstruct velocity: `v_clamped = v - (v_toward - clamped) * toward_hat`
5. Send clamped velocity

**For `send_global_target` (navigation mode):**
1. Compute direction from current position to target waypoint
2. Compute angle between waypoint-direction and toward-NFZ
3. If waypoint is deeper into the buffer zone, use `set_speed(max_approach)`
4. If waypoint is parallel or away, leave speed uncapped
5. Never replace position target with velocity command

**Pros:**
- Works transparently for both modes -- one interception point
- Never fights ArduCopter's position controller (no velocity override during navigation)
- Truly directional: parallel and away motion is free
- Clean separation: navigation.py handles clamping, main.py doesn't need geofence logic

**Cons:**
- NavigationController needs geofence awareness (breaks its current "thin wrapper" design)
- `set_speed()` is throttled to 3s intervals -- may be too slow for rapid maneuvering near NFZ
- `set_speed()` is scalar, not directional -- it limits total speed, not just approach speed

**Verdict:** The velocity interception for manual mode is clean and correct. The position-target interception is harder because `set_speed()` is inherently omnidirectional. This is the approach already partially implemented in `_enforce_geofence()`.

---

### Solution 2: Modify velocity command only, use set_speed for navigation (CURRENT APPROACH, MOSTLY WORKING)

**Concept:** This is what the code already does. Keep them separate:
- Manual mode: cap `spd` in `_handle_manual_flight()` via `_nfz_manual_max_speed`
- Navigation mode: call `set_speed(allowed)` where `allowed = max_approach / cos_angle`

**What's already implemented (main.py L691-754):**

```
Directional (default, --nfz-total-speed disables):
  1. Find nearest NFZ boundary point
  2. Compute unit vector toward NFZ
  3. Get current velocity from telemetry (vx, vy)
  4. Compute cos(angle) between velocity and toward-NFZ
  5. If cos > 0.05 (approaching): allowed = max_approach / cos_angle
  6. If allowed < current speed: set_speed(allowed)
  7. If flying away/parallel: no speed limit

Total speed (legacy):
  cap set_speed() based on distance only (omnidirectional)
```

**What's wrong with it:**
1. `set_speed()` is a persistent ArduCopter parameter -- once set low, it stays low even when the drone turns away from the NFZ. The 3s throttle makes it worse.
2. The repulsive push (L756-771) uses `send_velocity()` which **cancels** position targets in GUIDED navigation mode.
3. For manual mode, `_nfz_manual_max_speed` caps total speed, not just approach component.

**What needs fixing:**
- After limiting speed, need to **restore** speed when drone is no longer approaching NFZ
- The repulsive push should NOT fire during navigation states
- Manual mode speed cap should be directional (decompose WASD into toward/away)

---

### Solution 3: Feedback controller (post-process telemetry)

**Concept:** Don't modify commands. Instead, after each tick, read telemetry velocity. If approach speed exceeds limit, send a corrective velocity for one tick.

**How it works:**
1. State machine sends its normal command (position or velocity)
2. Next tick: read `vx`, `vy` from telemetry
3. Compute approach component toward NFZ
4. If approach > max_approach, send `send_velocity()` with clamped approach for one tick
5. Next tick: state machine sends its command again, overriding the correction

**Pros:**
- Works for both modes (reacts to actual velocity, not commanded)
- Doesn't need to know what type of command was sent
- Simple to implement

**Cons:**
- **Fights ArduCopter's control loop** -- the state machine says "go to waypoint" and the geofence says "slow down", creating oscillation
- One-tick velocity commands are unreliable (ArduCopter may not respond fast enough)
- Latency: telemetry is 100-200ms old, correction arrives 100ms later
- This is essentially what the current repulsive push does, and it causes the waypoint-cancellation problem

**Verdict:** Bad. The fundamental issue (velocity overriding position) remains.

---

### Solution 4: ArduCopter native fence (MAV_CMD_DO_SET_FENCE)

**Concept:** Use ArduCopter's built-in geofence. Upload fence polygon, let the flight controller handle enforcement.

**Pros:**
- Zero computation on Pi
- No command conflicts (ArduCopter handles internally)
- Battle-tested in production autopilots

**Cons:**
- ArduCopter fence is binary: inside = trigger action (RTL/LAND/brake), outside = free
- No directional speed limiting, no viscous ramp
- No soft warning zone
- Fence action is all-or-nothing (can't do graduated slowdown)
- Less control over behavior

**Verdict:** Good as a safety backup (hard fence at the real boundary), but doesn't provide the viscous fluid behavior. Could be used as a last-resort layer beneath our software geofence.

---

### Solution 5: Modify waypoint targets (push waypoints away from NFZ)

**Concept:** Instead of limiting speed at runtime, pre-process all waypoints. If a waypoint is within the buffer zone, push it away from the NFZ boundary. The drone navigates to modified waypoints and never enters the buffer zone at all.

**For navigation mode:**
1. At plan time: offset any waypoint within 40m of NFZ boundary outward
2. Drone navigates to safe waypoints -- never enters buffer zone
3. No runtime enforcement needed for navigation

**For manual mode:**
Still need runtime velocity clamping (can't pre-process manual stick inputs).

**Pros:**
- Eliminates the problem for navigation mode entirely (no runtime geofence during SEARCH/TRANSIT)
- Already partially done: `filter_waypoints()` removes waypoints inside NFZ+buffer
- No command conflicts, no fighting ArduCopter

**Cons:**
- Only works for pre-planned waypoints, not manual mode or dynamic targets (CENTERING, DESCENDING)
- `filter_waypoints()` already removes waypoints within `NFZ_WAYPOINT_BUFFER_M = 30m` -- waypoints near NFZ are already excluded
- Doesn't handle the case where ArduCopter's path between safe waypoints clips the buffer zone

**Verdict:** Already done for search pattern. Not sufficient alone -- dynamic states and manual mode still need runtime enforcement.

---

## Recommended Approach: Hybrid (Solution 2 improved + Solution 5 hardened)

The current code is 80% there. The fixes needed are surgical, not architectural:

### Fix 1: Directional clamping for manual mode (in `_handle_manual_flight`)

Currently `_nfz_manual_max_speed` caps total speed. Instead, decompose the WASD velocity:

```python
def _handle_manual_flight(self, key):
    spd = config.MANUAL_FLY_SPEED_MPS
    # ... build vx, vy from WASD key ...

    # Directional NFZ clamping
    if self._nfz_toward_hat is not None:  # set by _enforce_geofence
        max_approach = self._nfz_max_approach  # distance-based ramp
        # Project velocity onto toward-NFZ axis
        v_toward = vx * self._nfz_toward_hat[0] + vy * self._nfz_toward_hat[1]
        if v_toward > max_approach:
            # Subtract excess approach component
            excess = v_toward - max_approach
            vx -= excess * self._nfz_toward_hat[0]
            vy -= excess * self._nfz_toward_hat[1]

    self.nav.send_velocity(vx, vy, vz, ...)
```

This is the true viscous fluid: movement along the toward-NFZ axis is clamped, perpendicular movement is untouched.

### Fix 2: Speed restoration for navigation mode

After `set_speed(allowed)` limits approach speed, restore it when the drone is no longer approaching:

```python
# In _enforce_geofence, after the directional check:
if cos_angle <= 0.05:
    # Flying away or parallel -- restore normal speed
    if getattr(self, '_nfz_speed_limited', False):
        self.nav.last_speed_req = 0  # reset throttle
        self.nav.set_speed(config.SEARCH_SPEED_MPS)
        self._nfz_speed_limited = False
elif allowed < speed:
    self.nav.last_speed_req = 0
    self.nav.set_speed(max(0.3, allowed))
    self._nfz_speed_limited = True
```

### Fix 3: Remove repulsive push during navigation states

The `send_velocity()` repulsive push (L756-771) should ONLY fire during MANUAL mode. During navigation states, the position target handles everything -- the speed limit alone prevents approach.

```python
# Only apply repulsive velocity push in MANUAL mode
if self.state == State.MANUAL and 0 < dist_to_inner < config.NFZ_INNER_RANGE_M:
    off_lat, off_lon = self.geofence.repulsive_offset(self.lat, self.lon)
    # ... send_velocity push ...
```

### Fix 4: ArduCopter fence as backup (Solution 4 as safety net)

Upload the SSSI polygon as a MAVLink fence with BRAKE action. This is a hard stop that fires if our software geofence fails. Zero runtime cost, maximum safety.

---

## Computation Cost on Pi

All approaches are negligible:
- Nearest-point-on-polygon: ~10 edges, a few dot products = microseconds
- Velocity decomposition: 2 dot products + subtraction = nanoseconds
- `cv2.pointPolygonTest`: already called once per tick, ~microseconds
- No new dependencies, no new threads, no new data structures

The bottleneck remains CV inference at 206ms. Geofence math is invisible.

---

## Summary Table

| Solution | Manual mode | Navigation mode | Fights ArduCopter? | Complexity | Viscous? |
|----------|------------|-----------------|--------------------|-----------:|----------|
| 1. Intercept in NavigationController | Yes (clean) | Partial (set_speed is scalar) | No | Medium | Yes for manual, partial for nav |
| 2. Current approach (improved) | Yes (with Fix 1) | Yes (with Fix 2+3) | No (with Fix 3) | Low | Yes |
| 3. Feedback controller | Yes | Unstable | Yes | Medium | Approximate |
| 4. ArduCopter fence | N/A (binary) | N/A (binary) | No | Low | No |
| 5. Modify waypoints | N/A | Yes (plan-time only) | No | Low | No (binary) |
| **Hybrid (2+5+4)** | **Yes** | **Yes** | **No** | **Low** | **Yes** |

**Recommendation:** Apply Fixes 1-3 to the current code. This gives true viscous-fluid behavior for both modes with minimal changes. Add ArduCopter fence as a hard backup. The waypoint filtering (Solution 5) is already in place.

The key insight: **don't use `send_velocity()` to enforce geofence during navigation states**. Use `set_speed()` (directional) for navigation. Use velocity clamping (directional) for manual. Keep them separate because they use fundamentally different command types.
