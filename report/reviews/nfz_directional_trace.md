# NFZ Directional Code Trace -- Concrete Scenario

## Bugs Found (3 total, 1 critical)

| # | Severity | Summary |
|---|----------|---------|
| 1 | **CRITICAL** | `send_velocity` fights `send_global_target` -- velocity override is immediately undone by GUIDED position controller, creating oscillation that looks like "pulling" |
| 2 | **HIGH** | The velocity subtraction changes the drone's heading, deflecting it along the NFZ tangent instead of just slowing it down |
| 3 | **MEDIUM** | No waypoint-arrival relaxation -- the drone can never reach waypoints that are outside the 30m buffer but inside the 20m slow zone |

---

## The Code Under Test

**`main.py` lines 681-723** (`_enforce_geofence`, directional branch):

```python
if NFZ_DIRECTIONAL and not nfz_inside and nfz_dist < config.NFZ_SLOW_ZONE_M:
    # max_approach ramps 0 -> 3.0 m/s over 2m -> 20m
    if nfz_dist <= config.NFZ_SCALAR_ZERO_M:
        max_approach = 0.0
    else:
        ratio = (nfz_dist - config.NFZ_SCALAR_ZERO_M) / (config.NFZ_SLOW_ZONE_M - config.NFZ_SCALAR_ZERO_M)
        max_approach = ratio * config.NFZ_ZONE_MAX_SPEED_MPS

    # Find nearest NFZ boundary point (project onto each edge)
    # ... edge projection loop ...
    # Result: (nfz_lat, nfz_lon) = closest point on SSSI boundary

    # Direction toward nearest NFZ boundary
    dx = (nfz_lon - self.lon) * 111320 * cos(lat)   # East component
    dy = (nfz_lat - self.lat) * 111320               # North component
    nx, ny = dx/dist, dy/dist                         # unit vector toward NFZ

    vn = self.vx   # North velocity (from GLOBAL_POSITION_INT)
    ve = self.vy   # East velocity

    v_toward = vn * ny + ve * nx   # dot product: speed toward NFZ
    if v_toward > max_approach:
        excess = v_toward - max_approach
        self.nav.send_velocity(vn - ny*excess, ve - nx*excess, 0, current_yaw=0)
```

**`navigation.py` lines 64-78** (`send_velocity`):

```python
def send_velocity(self, vx, vy, vz, yaw_rate=0, current_yaw=None):
    """Send body-frame velocity command, rotated to NED before transmission."""
    if current_yaw is None:
        current_yaw = self._get_yaw()
    cos_yaw = math.cos(current_yaw)
    sin_yaw = math.sin(current_yaw)
    vx_ned = vx * cos_yaw - vy * sin_yaw
    vy_ned = vx * sin_yaw + vy * cos_yaw
    # sends to MAV_FRAME_LOCAL_NED
```

**Config values:**

```python
NFZ_SLOW_ZONE_M = 20.0         # Speed ramp active within 20m of NFZ
NFZ_SCALAR_ZERO_M = 2.0        # Full stop at 2m
NFZ_ZONE_MAX_SPEED_MPS = 3.0   # Max approach speed at 20m
NFZ_WAYPOINT_BUFFER_M = 30.0   # Waypoints within 30m are skipped at plan time
```

---

## Test Scenario

### Coordinates

**Drone position**: lat=51.42340, lon=-2.67095
(Near search polygon vertex 0, northwest edge near SSSI)

**Drone heading (yaw)**: 155 deg (2.705 rad, facing south-southeast toward search area)

**Drone velocity**: 8 m/s toward the next waypoint (south-southwest)
- vn (North) = -6.0 m/s
- ve (East)  = -2.0 m/s
- speed = sqrt(36 + 4) = 6.32 m/s

**SSSI polygon** (from config.py):
```
Vertex 0: (51.42353587, -2.67145175)  -- NW
Vertex 5: (51.42326667, -2.67096542)  -- closest to drone
Vertex 6: (51.42356862, -2.67132430)  -- NW
```

---

## Step-by-Step Trace

### Step 1: `distance_to_boundary` returns nfz_dist

Assume: **nfz_dist = 10.0 m**, nfz_inside = False.

Since 10 < 20 (NFZ_SLOW_ZONE_M), we enter the directional block.

### Step 2: Compute max_approach

```
ratio = (10.0 - 2.0) / (20.0 - 2.0) = 8/18 = 0.444
max_approach = 0.444 * 3.0 = 1.333 m/s
```

### Step 3: Find nearest NFZ boundary point

Edge from vertex 5 to vertex 6 is closest. Projecting drone onto this edge:

```
cos(51.4234) = 0.6245

Edge vector (metres):
  e_n = (51.42356862 - 51.42326667) * 111320 = 33.61 m
  e_e = (-2.67132430 + 2.67096542) * 111320 * 0.6245 = -24.96 m

Drone-to-p1 vector:
  d_n = (51.42340 - 51.42326667) * 111320 = 14.84 m
  d_e = (-2.67095 + 2.67096542) * 111320 * 0.6245 = 1.07 m

t = (14.84 * 33.61 + 1.07 * (-24.96)) / (33.61^2 + 24.96^2)
  = (498.9 - 26.7) / 1752.6 = 0.269

Closest point on edge:
  c_lat = 51.42326667 + 0.269 * 0.00030195 = 51.42334797
  c_lon = -2.67096542 + 0.269 * (-0.00035888) = -2.67106205

Distance to closest point:
  dn = (51.42340 - 51.42334797) * 111320 = 5.79 m  (drone is north of NFZ point)
  de = (-2.67095 + 2.67106205) * 69540 = 7.79 m    (drone is east of NFZ point)
  dist = sqrt(5.79^2 + 7.79^2) = 9.71 m
```

**Nearest boundary point**: (51.42334797, -2.67106205), 9.71m away.

### Step 4: Compute direction toward NFZ

```python
dx = (nfz_lon - self.lon) * 111320 * cos(lat)
   = (-2.67106205 + 2.67095) * 69540
   = -7.79 m                            # NFZ is to the WEST

dy = (nfz_lat - self.lat) * 111320
   = (51.42334797 - 51.42340) * 111320
   = -5.79 m                            # NFZ is to the SOUTH

dist = 9.71 m

Unit vector toward NFZ:
  nx = -7.79 / 9.71 = -0.802   (East component, negative = west)
  ny = -5.79 / 9.71 = -0.596   (North component, negative = south)
```

**NFZ is to the south-west.** Toward-NFZ unit vector: (nx=-0.802, ny=-0.596).

### Step 5: Compute v_toward (dot product)

```python
vn = -6.0    # flying south
ve = -2.0    # flying west (toward NFZ)

v_toward = vn * ny + ve * nx
         = (-6.0) * (-0.596) + (-2.0) * (-0.802)
         = 3.576 + 1.604
         = 5.18 m/s    # positive = approaching NFZ
```

**v_toward = 5.18 m/s**, exceeds max_approach (1.333 m/s). Reduction triggered.

### Step 6: Compute reduction

```python
excess = v_toward - max_approach = 5.18 - 1.333 = 3.847
```

### Step 7: Compute new velocity

```python
new_vn = vn - ny * excess = -6.0 - (-0.596) * 3.847 = -6.0 + 2.293 = -3.707
new_ve = ve - nx * excess = -2.0 - (-0.802) * 3.847 = -2.0 + 3.085 = +1.085
```

**Verification:**
- New speed = sqrt(3.707^2 + 1.085^2) = sqrt(13.74 + 1.18) = 3.86 m/s
- New v_toward = (-3.707)(-0.596) + (1.085)(-0.802) = 2.21 - 0.87 = 1.34 m/s (matches max_approach)
- Original heading: atan2(-2.0, -6.0) = 198 deg (south-southwest)
- New heading: atan2(+1.085, -3.707) = 164 deg (south-southeast)

**The velocity vector rotated 34 degrees.** The drone was heading south-southwest (toward waypoint + NFZ), and is now heading south-southeast (along the NFZ boundary).

### Step 8: What `send_velocity` does with these values

```python
self.nav.send_velocity(-3.707, +1.085, 0, current_yaw=0)
```

Inside `send_velocity`, `current_yaw=0` means:
```python
cos(0) = 1, sin(0) = 0
vx_ned = -3.707 * 1 - 1.085 * 0 = -3.707  (North)
vy_ned = -3.707 * 0 + 1.085 * 1 = +1.085  (East)
```

The rotation is identity. The NED values pass through unchanged to `MAV_FRAME_LOCAL_NED`.

**The MAVLink velocity command is correct NED.** The `current_yaw=0` hack works because it bypasses the body-to-NED rotation for what are already NED values.

---

## Bug Analysis

### BUG #1 (CRITICAL): Velocity override fights GUIDED position controller

The SEARCH state (in `state_machine.py` line 394) sends position commands:

```python
self.nav.send_global_target(target[0], target[1], self._current_search_alt())
```

This tells the autopilot: "fly to this GPS coordinate." The autopilot's position controller continuously generates velocity commands to reach that waypoint.

Then `_enforce_geofence()` runs (line 647) and sends a velocity override:

```python
self.nav.send_velocity(-3.707, +1.085, 0, current_yaw=0)
```

**What happens next loop iteration (~50ms later):**

1. `_handle_search()` runs first, sends `send_global_target` again -- autopilot position controller takes over, starts accelerating toward waypoint
2. `_enforce_geofence()` runs, reads the new velocity (partially restored toward waypoint), sends velocity override again
3. Repeat

**Result**: The drone oscillates. The position controller wants to go toward the waypoint (near NFZ), the geofence keeps overriding with a deflected velocity. Each `send_global_target` resets the autopilot's velocity plan. Each `send_velocity` interrupts it.

The user sees: the drone wobbling, making no progress toward the waypoint, appearing to be "pulled away." The velocity overrides deflect it sideways (along the NFZ tangent), while the position controller keeps trying to correct back toward the waypoint.

**The fix**: When the geofence is actively limiting speed, it should override the waypoint navigation entirely. Either:
- (a) Switch from `send_global_target` to `send_velocity`-only navigation when near NFZ, or
- (b) Move the waypoint further from NFZ dynamically, or
- (c) Skip the waypoint if it's inside the slow zone, or
- (d) Use `DO_CHANGE_SPEED` instead of velocity override (just slow down, don't change direction)

### BUG #2 (HIGH): Velocity subtraction changes heading

The directional reduction correctly caps the approach speed toward NFZ. But the subtracted vector is along the toward-NFZ axis, which means the remaining velocity is the tangential component.

In the example:
- Original heading: 198 deg (toward waypoint and NFZ)
- After reduction: 164 deg (deflected 34 deg along NFZ boundary)

This is mathematically correct for "remove approach component." But combined with Bug #1, the drone is being actively steered along the NFZ boundary, fighting the position controller that wants to go toward the waypoint. The result is the drone sliding sideways instead of slowing down.

**If the intent is "slow approach to NFZ"**, the code should scale the entire velocity vector down rather than removing only the NFZ-approach component. The non-directional branch (line 724-732) does this correctly with `set_speed(max_spd)`.

### BUG #3 (MEDIUM): Waypoint buffer vs. slow zone mismatch

```
NFZ_WAYPOINT_BUFFER_M = 30m   -- waypoints within 30m are removed at plan time
NFZ_SLOW_ZONE_M = 20m         -- speed ramp active within 20m
```

Waypoints at 21-30m from NFZ are removed (good). Waypoints at 30+ meters are kept.

But the transit PATH between two waypoints can cut closer to the NFZ than either endpoint. If waypoint A is 35m from NFZ and waypoint B is 35m from NFZ, but the straight line between them passes within 15m of NFZ, the drone will enter the slow zone during transit.

This is exactly the "2nd waypoint" scenario. The waypoint itself was outside the buffer, but the flight path crossed into the slow zone, triggering the directional velocity override.

---

## Frame Convention Audit

| Variable | Frame | Meaning |
|----------|-------|---------|
| `self.vx` | NED (from GLOBAL_POSITION_INT) | North velocity, m/s |
| `self.vy` | NED | East velocity, m/s |
| `nx` | NED | East component of unit vector toward NFZ |
| `ny` | NED | North component of unit vector toward NFZ |
| `v_toward` | Scalar | Dot product: speed toward NFZ (positive = approaching) |
| `new_vn` | NED | Corrected North velocity |
| `new_ve` | NED | Corrected East velocity |
| `send_velocity(vn, ve, 0, current_yaw=0)` | NED passed as body-frame | `current_yaw=0` makes the body-to-NED rotation an identity, so NED values pass through correctly |

**Frame conventions are internally consistent.** The `current_yaw=0` trick is a hack but produces correct MAVLink output. The `nx`/`ny` naming is unconventional (nx=East, ny=North) but the math is consistent.

---

## Recommended Fixes

### Fix 1: Don't fight the position controller

When the geofence needs to limit approach speed, don't send `send_velocity` while the state machine is using `send_global_target`. Instead, either:

**(a) Use `set_speed` only** (simplest, like the non-directional branch):
```python
# Instead of send_velocity, just limit the autopilot's speed
if v_toward > max_approach:
    scale = max_approach / v_toward
    self.nav.set_speed(current_speed * scale)
```

**(b) Suppress `send_global_target` when geofence is active**:
Set a flag like `self._geofence_velocity_override = True` and check it in `_advance_waypoint` to skip the `send_global_target` call.

### Fix 2: Path-aware waypoint filtering

Instead of only filtering individual waypoints, also check the straight-line path between consecutive waypoints. If the path crosses within `NFZ_SLOW_ZONE_M` of the NFZ boundary, insert an intermediate waypoint that routes around the NFZ.

### Fix 3: Arrival tolerance near NFZ

If a waypoint is within 20-30m of NFZ and the drone is within 5m of the waypoint, consider it "reached" even if it hasn't hit the 2m threshold. The speed reduction near NFZ means the drone approaches very slowly and may never reach the exact waypoint position.

---

## Summary

The directional NFZ velocity math (dot product, subtraction, frame handling) is **correct in isolation**. The velocity sent to MAVLink is the right NED vector to cap approach speed.

**The fundamental problem is architectural**: the velocity override fights the position controller. Every 50ms the state machine sends `send_global_target(waypoint)` and the geofence sends `send_velocity(deflected)`. The autopilot oscillates between the two commands, and the drone appears to be "pulled away" from its waypoint.

The non-directional branch (line 724-732) avoids this by using `set_speed()` which works WITH the position controller instead of against it. The directional branch should do the same or take over navigation entirely when active.
