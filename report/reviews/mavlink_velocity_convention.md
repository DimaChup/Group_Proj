# MAVLink Velocity Convention Investigation

## 1. Where vx/vy Come From

**Source message**: `GLOBAL_POSITION_INT` (MAVLink message #33)

**Parsing** in `main.py` line 362:
```python
self.vx = msg.vx / 100.0
self.vy = msg.vy / 100.0
self.vz = msg.vz / 100.0
```

## 2. Frame and Units

Per the MAVLink spec, `GLOBAL_POSITION_INT` fields:
- `vx`: ground speed in **North** direction, integer **cm/s**
- `vy`: ground speed in **East** direction, integer **cm/s**
- `vz`: ground speed in **Down** direction, integer **cm/s**

**Frame**: NED (North-East-Down), ground-fixed, NOT body-frame.

After dividing by 100.0, `self.vx` / `self.vy` / `self.vz` are in **m/s, NED**.

| Attribute | Meaning     | Raw units | Stored units |
|-----------|-------------|-----------|-------------|
| self.vx   | North speed | cm/s      | m/s         |
| self.vy   | East speed  | cm/s      | m/s         |
| self.vz   | Down speed  | cm/s      | m/s         |

## 3. Confirmation: vx = North, vy = East

Line 718-719 in main.py confirms the team's understanding is correct:
```python
vn = getattr(self, 'vx', 0)    # north m/s (from GLOBAL_POSITION_INT)
ve = getattr(self, 'vy', 0)    # east m/s
```

## 4. send_velocity() Convention

**File**: `navigation.py` line 64-78

```python
def send_velocity(self, vx, vy, vz, yaw_rate=0, current_yaw=None):
    """Send body-frame velocity command, rotated to NED before transmission."""
    cos_yaw = math.cos(current_yaw)
    sin_yaw = math.sin(current_yaw)
    vx_ned = vx * cos_yaw - vy * sin_yaw
    vy_ned = vx * sin_yaw + vy * cos_yaw
    # Sends via SET_POSITION_TARGET_LOCAL_NED in MAV_FRAME_LOCAL_NED
```

**What send_velocity() expects**: body-frame inputs (vx=forward, vy=right relative to drone heading), which it then rotates to NED using the drone's yaw before transmitting.

**What MAVLink receives**: NED velocities via `SET_POSITION_TARGET_LOCAL_NED` in `MAV_FRAME_LOCAL_NED`.

## 5. CRITICAL BUG: Frame Mismatch in NFZ Code

The NFZ geofence code (main.py lines 718-723 and 743-749) passes **NED velocities** into `send_velocity()`, but `send_velocity()` treats its inputs as **body-frame** and applies a yaw rotation:

```python
# Line 718-723: passes NED values...
vn = getattr(self, 'vx', 0)    # north m/s (NED!)
ve = getattr(self, 'vy', 0)    # east m/s  (NED!)
self.nav.send_velocity(vn - ny * excess, ve - nx * excess, 0, current_yaw=0)
#                      ^^^^ NED values fed into body-frame parameter ^^^^
```

**However**, all callers pass `current_yaw=0`, which makes `cos(0)=1, sin(0)=0`, so the rotation becomes an identity transform:
```
vx_ned = vx * 1 - vy * 0 = vx
vy_ned = vx * 0 + vy * 1 = vy
```

**Result**: The `current_yaw=0` hack effectively bypasses the body-to-NED rotation, so NED values pass through unchanged. This **works correctly by accident**, but the code is misleading:
- The docstring says "body-frame velocity command"
- The callers pass NED values
- `current_yaw=0` neutralises the rotation so it works anyway

## 6. Summary Table

| Item | Value |
|------|-------|
| Telemetry message | `GLOBAL_POSITION_INT` |
| Telemetry frame | NED (North-East-Down) |
| Raw telemetry units | cm/s (integer) |
| Stored as self.vx/vy/vz | m/s (float), NED |
| self.vx meaning | North velocity (positive = northward) |
| self.vy meaning | East velocity (positive = eastward) |
| self.vz meaning | Down velocity (positive = descending) |
| send_velocity() documented input | Body-frame (forward, right) |
| send_velocity() output | NED via SET_POSITION_TARGET_LOCAL_NED |
| send_velocity() frame conversion | Yaw rotation (body -> NED) |
| NFZ callers pass | NED values with current_yaw=0 (bypasses rotation) |
| Command message | `SET_POSITION_TARGET_LOCAL_NED` in `MAV_FRAME_LOCAL_NED` |
| Command units | m/s, NED |

## 7. Recommendation

The `send_velocity()` function has a dual-personality problem. Either:

1. **Rename to clarify**: Make two functions -- `send_velocity_body(fwd, right, down)` and `send_velocity_ned(north, east, down)`. The NFZ code would call the NED variant directly without any rotation.

2. **Or at minimum**: Document that passing `current_yaw=0` is the intended way to send raw NED values, so future developers don't "fix" it by passing the real yaw.
