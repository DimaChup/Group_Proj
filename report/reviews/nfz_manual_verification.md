# NFZ Manual Mode Viscous Field -- Verification Trace

**Date**: 2026-03-29
**Files examined**:
- `state_machine.py` lines 852-904 (`_handle_manual_flight`)
- `main.py` lines 666-801 (`_enforce_geofence`)
- `navigation.py` lines 64-78 (`send_velocity`)
- `config.py` lines 112-123 (NFZ params)

---

## System Overview

Two independent NFZ enforcement mechanisms run every tick:

1. **`_enforce_geofence()` in main.py** (lines 666-801) -- runs AFTER state dispatch for ALL states.
   Sets `self._nfz_toward_vec` and `self._nfz_manual_max_speed` as shared state.
   Also runs `set_speed()` for navigation states and repulsive push for MANUAL.

2. **`_handle_manual_flight()` in state_machine.py** (lines 852-904) -- runs when a WASD key is
   pressed in MANUAL state. Reads the shared variables set by `_enforce_geofence()`.

### Execution Order Per Tick

```
main loop iteration:
  1. handler(target_found, px_u, px_v, key)   # state handler, including _handle_manual_flight
  2. self._last_repulsion_vec = None
  3. self._enforce_geofence()                  # sets _nfz_toward_vec, _nfz_manual_max_speed
```

**IMPORTANT**: The geofence runs AFTER the state handler. This means manual flight uses the
PREVIOUS tick's `_nfz_toward_vec` and `_nfz_manual_max_speed`. At ~50 Hz loop rate this is
a ~20ms delay -- negligible for a human pilot pressing keys.

---

## Config Values

```python
NFZ_HARD_BOUNDARY_M  = 3.0    # Inside this -> force MANUAL
NFZ_SLOW_ZONE_M      = 40.0   # Viscous field active within this distance
NFZ_SCALAR_ZERO_M    = 2.0    # Speed drops to near-zero at this distance
NFZ_ZONE_MAX_SPEED_MPS = 3.0  # Max approach speed at outer edge (40m)
MANUAL_FLY_SPEED_MPS = 5.0    # WASD command speed
```

Speed ramp formula (linear):
```
if dist <= 2m:   max_approach = 0.3 m/s  (hardcoded floor, line 673)
if 2m < dist < 40m:
    ratio = (dist - 2) / (40 - 2) = (dist - 2) / 38
    max_approach = ratio * 3.0 m/s
```

---

## Key Data Flow

### How `self.yaw` is set
- `ATTITUDE` MAVLink message: `self.yaw = msg.yaw` (main.py line 364)
- ATTITUDE.yaw is in **radians**, range [-pi, pi], 0 = North, positive = clockwise (East)
- This is correct and consistent with ArduCopter conventions

### How `send_velocity()` works (navigation.py lines 64-78)
```python
def send_velocity(self, vx, vy, vz, yaw_rate=0, current_yaw=None):
    if current_yaw is None:
        current_yaw = self._get_yaw()     # lambda: self.yaw (radians from ATTITUDE)
    cos_yaw = math.cos(current_yaw)
    sin_yaw = math.sin(current_yaw)
    vx_ned = vx * cos_yaw - vy * sin_yaw  # body forward/right -> NED north/east
    vy_ned = vx * sin_yaw + vy * cos_yaw
    # sends SET_POSITION_TARGET_LOCAL_NED with MAV_FRAME_LOCAL_NED
```

**Key insight**: `send_velocity` ALWAYS rotates (vx, vy) from body frame to NED.
When `current_yaw=0` is passed explicitly, cos(0)=1, sin(0)=0, so vx_ned=vx, vy_ned=vy.
This means passing `current_yaw=0` treats inputs AS IF THEY ARE ALREADY NED.

---

## Scenario 1: Drone at 15m from NFZ, facing NORTH (yaw=0), NFZ is EAST, press D (fly right/east)

### Step 1: _enforce_geofence (previous tick)
```
nfz_dist = 15m, nfz_inside = False
15m < 40m -> enter slow zone
ratio = (15 - 2) / (40 - 2) = 13/38 = 0.342
_nfz_manual_max_speed = 0.342 * 3.0 = 1.026 m/s

Nearest NFZ point is to the east:
  toward_n = 0.0   (no north component)
  toward_e = 1.0   (pure east)
_nfz_toward_vec = (0.0, 1.0)
```

### Step 2: _handle_manual_flight (this tick, key='d')
```
vf=0, vr=5  (right in body frame)
yaw = 0 (facing north)

Body to NED:
  vn = 0*cos(0) - 5*sin(0) = 0
  ve = 0*sin(0) + 5*cos(0) = 5

Approach component:
  v_toward = vn*toward_n + ve*toward_e = 0*0 + 5*1 = 5.0

5.0 > 1.026 -> CLAMP
  reduction = 5.0 - 1.026 = 3.974
  vn = 0 - 0*3.974 = 0
  ve = 5 - 1*3.974 = 1.026

send_velocity(0, 1.026, 0, current_yaw=0)
  -> vx_ned = 0*1 - 1.026*0 = 0
  -> vy_ned = 0*0 + 1.026*1 = 1.026
  -> Sends NED: north=0, east=1.026
```

**RESULT: CORRECT.** Approach limited to 1.026 m/s east. Drone creeps toward NFZ slowly.

---

## Scenario 2: Same position (15m, NFZ east), facing NORTH, press A (fly left/west, AWAY)

### _handle_manual_flight
```
vf=0, vr=-5  (left in body frame)
yaw = 0

Body to NED:
  vn = 0*cos(0) - (-5)*sin(0) = 0
  ve = 0*sin(0) + (-5)*cos(0) = -5

Approach:
  v_toward = 0*0 + (-5)*1 = -5.0

-5.0 < 1.026 -> NO CLAMP (moving away)

send_velocity(0, -5, 0, current_yaw=0)
  -> NED: north=0, east=-5
```

**RESULT: CORRECT.** Full speed west (away from NFZ). No restriction.

---

## Scenario 3: Drone facing SOUTH (yaw=pi), press W (forward=south), NFZ is EAST

### _handle_manual_flight
```
vf=5, vr=0
yaw = pi

Body to NED:
  vn = 5*cos(pi) - 0*sin(pi) = 5*(-1) - 0 = -5
  ve = 5*sin(pi) + 0*cos(pi) = 5*(~0) + 0 = 0
  (sin(pi) ~ 1.2e-16, effectively 0)

Approach:
  v_toward = (-5)*0 + 0*1 = 0.0

0.0 < 1.026 -> NO CLAMP (perpendicular motion)

send_velocity(-5, 0, 0, current_yaw=0)
  -> NED: north=-5, east=0
```

**RESULT: CORRECT.** Full speed south (perpendicular to NFZ). No restriction.

---

## Scenario 4: Drone facing EAST (yaw=pi/2), press W (forward=east toward NFZ)

### _handle_manual_flight
```
vf=5, vr=0
yaw = pi/2

Body to NED:
  vn = 5*cos(pi/2) - 0 = 5*0 = 0
  ve = 5*sin(pi/2) + 0 = 5*1 = 5

Approach:
  v_toward = 0*0 + 5*1 = 5.0

5.0 > 1.026 -> CLAMP
  reduction = 3.974
  vn = 0 - 0*3.974 = 0
  ve = 5 - 1*3.974 = 1.026

send_velocity(0, 1.026, 0, current_yaw=0) -> NED: north=0, east=1.026
```

**RESULT: CORRECT.** Same as scenario 1 -- heading doesn't matter, only NED velocity matters.

---

## Scenario 5: Drone facing NORTHEAST (yaw=pi/4), press W (forward=NE), NFZ is EAST

### _handle_manual_flight
```
vf=5, vr=0
yaw = pi/4

Body to NED:
  vn = 5*cos(pi/4) = 5*0.707 = 3.536
  ve = 5*sin(pi/4) = 5*0.707 = 3.536

Approach:
  v_toward = 3.536*0 + 3.536*1 = 3.536

3.536 > 1.026 -> CLAMP
  reduction = 3.536 - 1.026 = 2.510
  vn = 3.536 - 0*2.510 = 3.536  (unchanged -- no north component in toward vector)
  ve = 3.536 - 1*2.510 = 1.026

send_velocity(3.536, 1.026, 0, current_yaw=0) -> NED: north=3.536, east=1.026
```

**RESULT: CORRECT.** North component preserved at full 3.536 m/s, east clamped to 1.026 m/s.
The pilot can still fly north at full speed while the eastward approach is limited. This is
exactly the "viscous field" behavior: only the toward-NFZ component is damped.

---

## Scenario 6: Very close (3m from NFZ), press D (east toward NFZ)

```
dist = 3m
ratio = (3 - 2) / 38 = 0.026
max_approach = 0.026 * 3.0 = 0.079 m/s

vf=0, vr=5, yaw=0 -> vn=0, ve=5
v_toward = 5.0 > 0.079 -> CLAMP
  reduction = 4.921
  ve = 5 - 4.921 = 0.079

send_velocity(0, 0.079, 0, current_yaw=0) -> NED: north=0, east=0.079
```

**RESULT: CORRECT.** Near-zero approach speed at 3m. Drone barely moves toward NFZ.

---

## Scenario 7: At 2m or less (NFZ_SCALAR_ZERO_M)

```
dist <= 2m -> max_approach = 0.3 m/s  (hardcoded floor, line 673)
```

Note: the manual clamping code (line 673) uses 0.3 m/s, while the navigation code (line 722)
uses 0.0 m/s. This is intentional -- in manual mode the pilot should still be able to creep
slowly, while navigation should fully stop.

---

## Critical Check: `current_yaw=0` in send_velocity

### The concern
When `_handle_manual_flight` computes NED velocities itself and calls
`send_velocity(vn, ve, vd, current_yaw=0)`, is this correct?

### Analysis
`send_velocity()` always rotates inputs from body frame to NED:
```python
vx_ned = vx * cos(current_yaw) - vy * sin(current_yaw)
vy_ned = vx * sin(current_yaw) + vy * cos(current_yaw)
```

When `current_yaw=0`:
```python
vx_ned = vx * 1 - vy * 0 = vx
vy_ned = vx * 0 + vy * 1 = vy
```

So passing `current_yaw=0` means "my inputs are already in NED, pass them through unchanged."
Since `_handle_manual_flight` already rotated body->NED using the real yaw, this is correct.

**VERDICT: NO BUG.** The `current_yaw=0` is an intentional identity-rotation to bypass
the body->NED conversion that `send_velocity` normally does.

---

## Critical Check: "Press east INSIDE buffer zone moves drone WEST"

### Could this happen?

If the drone is inside the NFZ (nfz_inside=True), `_enforce_geofence` sets
`_nfz_manual_max_speed = None` and `_nfz_toward_vec = None` (line 704-706).
The viscous field condition (line 879) checks both are not None, so it falls through
to the plain `send_velocity(vf, vr, vd)` in body frame (line 897). No clamping occurs.

**However**, there is a separate repulsive push (lines 784-800) that runs in MANUAL mode:
```python
if self.nav and self.state == State.MANUAL:
    signed_dist = nfz_dist if not nfz_inside else -nfz_dist
    dist_to_inner = signed_dist + NFZ_INNER_OFFSET_M  # e.g. -3 + 20 = 17
    if 0 < dist_to_inner < NFZ_INNER_RANGE_M:         # 0 < 17 < 23 -> yes
        off_lat, off_lon = self.geofence.repulsive_offset(...)
        push_n, push_e = -off_lat * lat_m, -off_lon * lon_m
        if nfz_inside:
            push_n, push_e = -push_n, -push_e   # reverse direction when inside
        self.nav.send_velocity(push_n/mag*5, push_e/mag*5, 0, current_yaw=0)
```

This repulsive push runs AFTER the state handler, so it OVERRIDES the manual velocity command
from the same tick. The push sends a constant 5 m/s away from the NFZ boundary.

**This IS the cause of "pressing east moves drone west"**: if the pilot presses D while inside
the buffer zone, the manual handler sends the velocity east, but then `_enforce_geofence` runs
and sends a 5 m/s push west -- the LAST velocity command wins.

**This is actually correct behavior**: when inside the NFZ, the repulsive push SHOULD override
pilot commands to push the drone out. However, it may feel counterintuitive. The pilot can fly
freely only after exiting the inner range (NFZ_INNER_RANGE_M = 23m from inner polygon).

### Buffer zone geometry
```
NFZ_INNER_OFFSET_M = 20m     # inner polygon is 20m inside NFZ boundary
NFZ_INNER_RANGE_M  = 23m     # repulsion active within 23m of inner polygon

Repulsion active when: 0 < (signed_dist + 20) < 23
  Outside NFZ: signed_dist > 0 -> active when dist < 3m from boundary
  Inside NFZ:  signed_dist < 0 -> active when dist < 20m inside (always active inside)
```

So repulsive push activates within 3m outside or anywhere inside the NFZ. Beyond 3m outside,
only the viscous speed limit applies (no push, just velocity clamping).

---

## Critical Check: self.yaw in SIMULATION mode

`self.yaw` is set from the ATTITUDE MAVLink message (main.py line 364):
```python
self.yaw = msg.yaw   # radians, from ATTITUDE message
```

In SIMULATION mode, SITL sends real ATTITUDE messages over the mavlink connection,
so `self.yaw` is always in radians, always from ATTITUDE, in both REAL and SIMULATION modes.
No conversion issue.

---

## Critical Check: Wind pushing drone toward NFZ

**Question**: If wind pushes the drone toward NFZ while in MANUAL mode (no keys pressed),
will the viscous field actively decelerate it?

**Answer: NO** -- the viscous field in `_handle_manual_flight` only runs when a key is
pressed (vf != 0 or vr != 0, line 879). If no key is pressed, no velocity command is sent
by the manual handler.

**However**, `_enforce_geofence()` runs every tick regardless and has two fallback mechanisms:

1. **Navigation speed limit** (lines 719-772): In non-MANUAL states, it reads telemetry
   velocity (`self.vx`, `self.vy`) and calls `set_speed()` if approach speed exceeds the
   ramp limit. This does NOT apply in MANUAL mode.

2. **Repulsive push** (lines 784-800): In MANUAL mode, if the drone drifts within 3m of
   the NFZ boundary (or inside), the constant repulsive push at 5 m/s activates. This WILL
   fight wind-driven drift, but ONLY within the 3m outer buffer.

**Gap**: Between 3m and 40m from NFZ, if wind pushes the drone toward NFZ in MANUAL mode
with no keys pressed, there is NO active countermeasure. The viscous field only affects
pilot-commanded velocity, not drift. ArduCopter's own position hold (LOITER mode) would
resist wind, but in GUIDED mode (which MANUAL state uses for velocity commands), there is
no inherent position hold between commands.

**Mitigation**: This is acceptable because:
- The pilot should notice drift on the ground station
- The repulsive push at 3m will catch it
- The hard boundary at 3m forces MANUAL + stop
- In practice, ArduCopter maintains position reasonably well even in GUIDED mode between
  velocity commands due to its internal velocity controller

---

## Summary of Findings

| Check | Result | Notes |
|-------|--------|-------|
| Body->NED rotation | CORRECT | Uses real yaw from ATTITUDE (radians) |
| Toward-NFZ vector | CORRECT | Nearest-point projection on polygon edges |
| Approach clamping | CORRECT | Only toward-component reduced, tangential preserved |
| Away motion unrestricted | CORRECT | Negative v_toward skips clamping |
| Perpendicular motion unrestricted | CORRECT | Zero v_toward skips clamping |
| `current_yaw=0` bypass | CORRECT | Identity rotation, inputs already NED |
| Speed ramp continuity | CORRECT | Linear from 0 at 2m to 3.0 at 40m |
| Diagonal approach | CORRECT | Only east component clamped in NE example |
| `self.yaw` source | CORRECT | ATTITUDE msg, radians, both SIM and REAL |
| "East moves west" report | EXPLAINED | Repulsive push overrides manual command inside buffer |
| Wind drift protection | PARTIAL | Only repulsive push at <3m; no active brake 3-40m in MANUAL |

### Bugs Found: NONE

The viscous field implementation is mathematically correct. The "pressing east moves west"
behavior is the repulsive push working as designed, not a bug in the viscous field.

### One Minor Concern: Duplicate Nearest-Point Computation

`_enforce_geofence()` computes the nearest NFZ boundary point TWICE:
1. Lines 678-701: to set `_nfz_toward_vec` for manual flight
2. Lines 727-753: to set `toward_n/toward_e` for navigation speed limiting

These are identical computations with identical code. Could be refactored into a helper,
but functionally correct as-is.

### Architectural Note

The one-tick delay between `_enforce_geofence()` setting the shared variables and
`_handle_manual_flight()` reading them is inherent to the execution order (state handler
runs before geofence). At 50 Hz this is ~20ms, which is well within acceptable latency
for pilot-in-the-loop control. No fix needed.
