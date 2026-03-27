# MAVLink Commands Reference

**For: Colleagues Understanding the Autopilot Protocol**

This document lists every MAVLink command and message the drone sends to the Cube autopilot. Each entry explains what the drone receives, how it's sent, and what the autopilot does with it.

**ArduCopter Target**: 4.x (Copter 4.0+). All commands are fully compatible.

---

## High-Level Summary

The drone uses **6 message types**:

1. **SET_POSITION_TARGET_GLOBAL_INT** — "Fly to GPS waypoint X with heading Y"
2. **SET_POSITION_TARGET_LOCAL_NED** — "Move at velocity (m/s) in body-frame coords"
3. **command_long** — General autopilot commands (arm, disarm, takeoff, land, mode change, etc.)
4. **request_data_stream** — Request telemetry updates from Cube (GPS, attitude, battery)
5. **param_set** — Set autopilot parameters (SITL speedup only)

---

## Commands by Category

### 1. Mode Control — `MAV_CMD_DO_SET_MODE`

**Used in**: navigation.py, state_machine.py, pi_flight.py, and all flight tests.

| **Parameter 1** | **Parameter 2** | **Meaning** |
|---|---|---|
| `MAV_MODE_FLAG_CUSTOM_MODE_ENABLED` (1) | Mode ID (see below) | Enable custom mode |

**ArduCopter Mode IDs** (from Copter 4.x):

| Mode Name | ID | When Used |
|---|---|---|
| STABILIZE | 0 | Manual stable flight (not used in autonomous) |
| ALT_HOLD | 2 | Hold altitude (not used) |
| GUIDED | 4 | Autonomous guided flight (main mission mode) |
| LOITER | 5 | Hold position (used in manual override) |
| RTL | 6 | Return to launch (operator RC command) |
| LAND | 9 | Controlled landing (not used — we use MAV_CMD_NAV_LAND instead) |

**Example** (from navigation.py line 231-235):
```python
self.master.mav.command_long_send(
    self.master.target_system, self.master.target_component,
    mavutil.mavlink.MAV_CMD_DO_SET_MODE, 0,
    mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
    4,  # GUIDED mode ID
    0, 0, 0, 0, 0)
```

**What the Cube does**: Switches to the requested mode. Must be in GUIDED for autonomous commands.

**Compatibility**: Copter 4.0+ fully compatible. GUIDED mode is the standard for autonomous waypoint missions.

---

### 2. Arm/Disarm — `MAV_CMD_COMPONENT_ARM_DISARM`

**Used in**: navigation.py, state_machine.py, pi_flight.py, flight tests.

| **Parameter 1** | **Meaning** | **Returns** |
|---|---|---|
| `1` | Arm the drone | COMMAND_ACK (result 0 = success, 4 = pre-arm check failed) |
| `0` (with param 2 = 0) | Disarm normally | COMMAND_ACK |
| `0` (with param 2 = 21196) | Force disarm (emergency) | COMMAND_ACK |

**Example** (navigation.py line 158-161):
```python
self.master.mav.command_long_send(
    self.master.target_system, self.master.target_component,
    mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0,
    1,  # arm
    0, 0, 0, 0, 0, 0)
```

**Normal disarm** (state_machine.py line 738-740):
```python
self.master.mav.command_long_send(
    self.master.target_system, self.master.target_component,
    mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0,
    0,  # disarm
    0, 0, 0, 0, 0, 0)
```

**Force disarm** (state_machine.py line 768-771, emergency only):
```python
self.master.mav.command_long_send(
    self.master.target_system, self.master.target_component,
    mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0,
    0, 21196,  # force disarm magic number
    0, 0, 0, 0, 0)
```

**What the Cube does**:
- **Arm (1)**: Motor control enabled. Runs pre-arm checks. Returns ACK with result code.
- **Disarm (0, 0)**: Motor control disabled. Clean shutdown.
- **Force disarm (0, 21196)**: Disarm without checks (emergency failsafe only).

**Compatibility**: Copter 4.0+ fully compatible. Force disarm is supported as emergency failsafe.

---

### 3. Takeoff — `MAV_CMD_NAV_TAKEOFF`

**Used in**: navigation.py, state_machine.py, pi_flight.py, flight tests.

| **Parameter 7** | **Meaning** |
|---|---|
| `altitude_m` | Target takeoff altitude in meters (above home, relative) |

**Example** (navigation.py line 178-181):
```python
self.master.mav.command_long_send(
    self.master.target_system, self.master.target_component,
    mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0,
    0, 0, 0, 0,  # params 1-4 unused
    0, 0,        # params 5-6 unused (lat/lon)
    alt)         # param 7: altitude in meters
```

**Critical Note**: DO NOT send SET_POSITION_TARGET during takeoff — it cancels NAV_TAKEOFF's climb sequence. Wait for drone to reach TARGET_ALT before issuing position targets.

**What the Cube does**:
1. Assumes drone is armed in GUIDED mode
2. Initializes PID climb controller
3. Climbs to target altitude at fixed climb rate (default ~2.5 m/s)
4. Hovers at target altitude

**Compatibility**: Copter 4.0+ fully compatible. Standard takeoff method.

---

### 4. Land — `MAV_CMD_NAV_LAND`

**Used in**: navigation.py, state_machine.py, pi_flight.py, flight tests.

| **Parameter 5** | **Parameter 6** | **Parameter 7** | **Meaning** |
|---|---|---|---|
| `lat` (float degrees) | `lon` (float degrees) | `0` (altitude param, unused) | Landing location |

**Example** (navigation.py line 194-198):
```python
self.master.mav.command_long_send(
    self.master.target_system, self.master.target_component,
    mavutil.mavlink.MAV_CMD_NAV_LAND, 0,
    0, 0, 0, 0,
    lat, lon,  # Landing GPS coordinates
    0)         # Altitude unused (descent controlled by autopilot)
```

**Our implementation** (state_machine.py line 752-756): Land at home position.
```python
self.master.mav.command_long_send(
    self.master.target_system, self.master.target_component,
    mavutil.mavlink.MAV_CMD_NAV_LAND, 0,
    0, 0, 0, 0,
    self.home_lat, self.home_lon,
    0)
```

**What the Cube does**:
1. Disengages GPS position control
2. Descends at constant rate (default ~0.5 m/s, configurable)
3. Detects ground contact via barometer + accelerometer
4. **Auto-disarms** when detected (no second disarm needed)

**Compatibility**: Copter 4.0+ fully compatible. **Recommended method** for controlled descent. Much safer than manual descent + disarm.

**Retry logic** (state_machine.py line 762-780): If drone doesn't descend after 5s, resend command up to 5 times before force-disarm.

---

### 5. Change Speed — `MAV_CMD_DO_CHANGE_SPEED`

**Used in**: navigation.py, state_machine.py, flight tests.

| **Parameter 1** | **Parameter 2** | **Meaning** |
|---|---|---|
| `1` | `speed_mps` | Ground speed in m/s |
| `speed_mps` | `-1` | -1 = no throttle scaling (leave as is) |

**Example** (navigation.py line 145-148):
```python
self.master.mav.command_long_send(
    self.master.target_system, self.master.target_component,
    mavutil.mavlink.MAV_CMD_DO_CHANGE_SPEED, 0,
    1, speed_mps,  # type 1 = ground speed
    -1,  # -1 = no throttle change
    0, 0, 0, 0)
```

**What the Cube does**: Sets target ground speed for autonomous waypoint navigation. Drone maintains this speed between SET_POSITION_TARGET commands.

**Throttle** (navigation.py): `-1` means "don't change existing throttle" — Cube auto-adjusts thrust to maintain ground speed and altitude.

**Compatibility**: Copter 4.0+ fully compatible.

**Throttle** (navigation.py): Throttled to once per 3 seconds (expensive computation on autopilot).

---

### 6. Yaw Control — `MAV_CMD_CONDITION_YAW`

**Used in**: state_machine.py (search pattern orientation + manual yaw control).

| **Parameter 1** | **Parameter 2** | **Parameter 3** | **Parameter 4** | **Meaning** |
|---|---|---|---|---|
| `target_deg` | `yaw_rate_dps` | `direction` | `relative` | Target heading and spin rate |

**Direction/Relative Flags**:
- **Parameter 3**: `-1` = absolute (global), `1` = relative (body frame)
- **Parameter 4**: `0` = direction CCW, `1` = direction CW, or unused

**Example 1: Search pattern orientation** (state_machine.py line 375-378):
```python
self.master.mav.command_long_send(
    self.master.target_system, self.master.target_component,
    mavutil.mavlink.MAV_CMD_CONDITION_YAW, 0,
    yaw_deg,   # param 1: target heading in degrees (0-360)
    45,        # param 2: yaw rate in deg/s
    1,         # param 3: direction (1=CW)
    0,         # param 4: relative (0=absolute, so this means absolute heading)
    0, 0, 0)
```

**Example 2: Manual yaw left (Q key)** (state_machine.py line 925-928):
```python
self.master.mav.command_long_send(
    self.master.target_system, self.master.target_component,
    mavutil.mavlink.MAV_CMD_CONDITION_YAW, 0,
    config.MANUAL_YAW_STEP_DEG,  # param 1: relative angle step
    yaw_rate,                      # param 2: rate deg/s
    -1,                            # param 3: absolute heading (global frame)
    1,                             # param 4: relative flag (1 = relative)
    0, 0, 0)
```

**What the Cube does**: Rotates drone to target heading at given yaw rate.

**Compatibility**: Copter 4.0+ fully compatible.

---

### 7. Servo Control — `MAV_CMD_DO_SET_SERVO`

**Used in**: state_machine.py (payload release during hover).

| **Parameter 1** | **Parameter 2** | **Meaning** |
|---|---|---|
| `servo_channel` (1-16) | `pwm_value` (1000-2000) | Output PWM on servo channel |

**Example** (state_machine.py lines 659-662, 669-672, 677-680):
```python
# Stage 1: Partial release at 3s
self.master.mav.command_long_send(
    self.master.target_system, self.master.target_component,
    mavutil.mavlink.MAV_CMD_DO_SET_SERVO, 0,
    9,      # param 1: servo channel 9
    1300,   # param 2: PWM 1300 (partial)
    0, 0, 0, 0, 0)

# Stage 2: Full release at 6s
self.master.mav.command_long_send(
    self.master.target_system, self.master.target_component,
    mavutil.mavlink.MAV_CMD_DO_SET_SERVO, 0,
    9,      # servo channel 9
    1100,   # PWM 1100 (full)
    0, 0, 0, 0, 0)

# Close at 15s
self.master.mav.command_long_send(
    self.master.target_system, self.master.target_component,
    mavutil.mavlink.MAV_CMD_DO_SET_SERVO, 0,
    9,      # servo channel 9
    1500,   # PWM 1500 (closed)
    0, 0, 0, 0, 0)
```

**What the Cube does**: Outputs PWM signal to AUX servo channel. Used for payload release (simulated casualty rescue — drops a marker).

**PWM Range**: 1000 (minimum) to 2000 (maximum). Typical servo:
- 1000 = fully left
- 1500 = center
- 2000 = fully right

**Compatibility**: Copter 4.0+ fully compatible. Standard servo control.

**Flight Day Note**: Verify servo channel and PWM values with hardware before flight.

---

### 8. Get Home Position — `MAV_CMD_GET_HOME_POSITION`

**Used in**: tests/flight/0a_cube_commands.py (connectivity test only).

**What it does**: Requests the drone's home position from the autopilot. Used only for diagnostics, not in main mission.

**Example** (0a_cube_commands.py line 230-232):
```python
master.mav.command_long_send(
    master.target_system, master.target_component,
    mavutil.mavlink.MAV_CMD_GET_HOME_POSITION, 0,
    0, 0, 0, 0, 0, 0, 0)
```

**Compatibility**: Copter 4.0+ fully compatible.

---

### 9. Geofence Commands — `MAV_CMD_NAV_FENCE_POLYGON_VERTEX_*`

**Used in**: tests/flight/geofence_demo.py (experimental geofence testing).

| **Command** | **Purpose** |
|---|---|
| `MAV_CMD_NAV_FENCE_POLYGON_VERTEX_INCLUSION` | Add point to inclusion zone (allowable area) |
| `MAV_CMD_NAV_FENCE_POLYGON_VERTEX_EXCLUSION` | Add point to exclusion zone (no-fly zone) |

**Example** (geofence_demo.py line 145, 155):
```python
'cmd': mavutil.mavlink.MAV_CMD_NAV_FENCE_POLYGON_VERTEX_INCLUSION
'cmd': mavutil.mavlink.MAV_CMD_NAV_FENCE_POLYGON_VERTEX_EXCLUSION
```

**Status**: Experimental feature. Not enabled in main mission yet. Requires Mission Planner setup.

**Compatibility**: Copter 4.0+ fully compatible.

---

## Position Control Messages (No Command ACK)

These are **position messages**, not commands. They don't trigger COMMAND_ACK responses.

### SET_POSITION_TARGET_GLOBAL_INT — "Fly to GPS waypoint"

**Used in**: navigation.py, state_machine.py, pi_flight.py, all flight tests.

**Purpose**: Direct drone to fly to GPS coordinates (lat, lon) at target altitude, with optional heading hold.

**Parameters** (pymavlink method signature):
```python
set_position_target_global_int_send(
    time_boot_ms,          # 0 (unused)
    target_system,         # Cube system ID (usually 1)
    target_component,      # Cube component ID (usually 1)
    coordinate_frame,      # MAV_FRAME_GLOBAL_RELATIVE_ALT_INT
    type_mask,             # Bitmask: which fields to use
    lat_int,               # Latitude in degrees * 1e7 (int)
    lon_int,               # Longitude in degrees * 1e7 (int)
    alt,                   # Altitude in meters (relative to home)
    vx, vy, vz,            # Velocity (m/s) — usually 0 (not used)
    afx, afy, afz,         # Acceleration (m/s²) — usually 0 (not used)
    yaw,                   # Heading in radians (0 = north, π/2 = east)
    yaw_rate)              # Yaw rate in rad/s (usually 0)
```

**Coordinate frame**: `MAV_FRAME_GLOBAL_RELATIVE_ALT_INT`
- Altitude is **relative to home** (not sea level)
- Latitude/Longitude in degrees * 1e7 (integer format for precision)

**Type mask** (bitmask of fields to ignore):

The bitmask tells the Cube which fields to use. Our code uses two variants:

**With yaw hold** (strafe mode, no turn):
```python
type_mask = 0b100111111000
# Bit 10 = 0 (yaw field USED)
# Bit 11 = 0 (yaw_rate IGNORED)
# All other position/velocity fields USED
```

**Without yaw hold** (normal, rotate to face waypoint):
```python
type_mask = 0b110111111000
# Bit 10 = 1 (yaw field IGNORED)
# Bit 11 = 0 (yaw_rate IGNORED)
# Drone rotates to face next waypoint naturally
```

**Example** (navigation.py line 89-93, with yaw hold):
```python
self.master.mav.set_position_target_global_int_send(
    0, self.master.target_system, self.master.target_component,
    mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
    0b100111111000,  # yaw field used, yaw_rate ignored
    int(lat * 1e7),  # lat as int
    int(lon * 1e7),  # lon as int
    alt,             # meters AGL
    0, 0, 0,         # velocities unused
    0, 0, 0,         # accelerations unused
    yaw,             # heading in radians (hold this yaw)
    0)               # yaw_rate unused
```

**What the Cube does**:
1. Engages GPS position control
2. Flies to target GPS coordinate
3. Maintains target altitude (climbs/descends as needed)
4. If yaw is provided, holds that heading and strafes sideways (useful for camera)
5. If yaw is not provided, rotates drone to face next waypoint during flight

**Compatibility**: Copter 4.0+ fully compatible. Standard autonomous waypoint navigation.

**Update rate**: Sent every 0.2-2.0 seconds (see `self.last_req` throttle in code).

---

### SET_POSITION_TARGET_LOCAL_NED — "Move at velocity"

**Used in**: navigation.py, state_machine.py, pi_flight.py, simple_simulator.py, manual flight tests.

**Purpose**: Command drone to move at specified velocity (body-frame: forward/right/down).

**Parameters**:
```python
set_position_target_local_ned_send(
    time_boot_ms,          # 0 (unused)
    target_system,         # Cube system ID (usually 1)
    target_component,      # Cube component ID (usually 1)
    coordinate_frame,      # MAV_FRAME_LOCAL_NED
    type_mask,             # Bitmask: use velocity fields only
    x, y, z,               # Position (meters) — IGNORED
    vx, vy, vz,            # Velocity NED (m/s) — USED
    afx, afy, afz,         # Acceleration — IGNORED
    yaw,                   # Heading in radians — IGNORED
    yaw_rate)              # Yaw rate in rad/s — USED (optional)
```

**Coordinate frame**: `MAV_FRAME_LOCAL_NED`
- **NED** = North-East-Down (autopilot convention)
- X = North (forward in nose direction)
- Y = East (right wing)
- Z = Down (positive = descend)

**Type mask** (velocity-only):
```python
type_mask = 0b010111000111
# Bits for position (1-3) = 1 (IGNORED)
# Bits for velocity (4-6) = 0 (USED)
# Bits for acceleration (7-9) = 1 (IGNORED)
# Bits for yaw/yaw_rate = variable
```

**Body-frame rotation** (navigation.py line 123-126):
The code sends velocity in NED frame, but the input is body-frame (forward/right):
```python
# Input: vx (forward), vy (right), current_yaw (heading radians)
# Rotate to NED:
cos_yaw = math.cos(current_yaw)
sin_yaw = math.sin(current_yaw)
vx_ned = vx * cos_yaw - vy * sin_yaw
vy_ned = vx * sin_yaw + vy * cos_yaw
# vz (down) stays unchanged
```

**Example** (navigation.py line 127-131):
```python
self.master.mav.set_position_target_local_ned_send(
    0, self.master.target_system, self.master.target_component,
    mavutil.mavlink.MAV_FRAME_LOCAL_NED,
    0b010111000111,  # velocity fields only
    0, 0, 0,         # position unused
    vx_ned, vy_ned, vz,  # NED velocities (m/s)
    0, 0, 0,         # accelerations unused
    0,               # yaw unused
    math.radians(yaw_rate))  # yaw rate in rad/s (optional)
```

**What the Cube does**:
1. Engages velocity control (not position control)
2. Accelerates drone to match requested velocity
3. Maintains altitude if vz=0, climbs/descends if vz≠0
4. Applies yaw rate if provided

**Compatibility**: Copter 4.0+ fully compatible. Standard velocity control for manual flight.

**Update rate**: Sent every 50-100ms during manual flight (high frequency).

---

## Request Messages (Request Data Stream)

### REQUEST_DATA_STREAM — "Send me telemetry"

**Used in**: state_machine.py line 164-166 (initial connection).

**Parameters**:
```python
request_data_stream_send(
    target_system,      # Cube system ID (1)
    target_component,   # Cube component ID (1)
    req_stream_id,      # MAV_DATA_STREAM_ALL
    req_message_rate,   # Rate in Hz (10 = 10 updates/sec)
    start_stop)         # 1 = start, 0 = stop
```

**Example**:
```python
self.master.mav.request_data_stream_send(
    self.master.target_system, self.master.target_component,
    mavutil.mavlink.MAV_DATA_STREAM_ALL,
    10,   # 10 Hz
    1)    # start
```

**What the Cube does**: Enables all telemetry streams at 10 Hz (heartbeat, GPS, attitude, battery, etc.).

**Compatibility**: Copter 4.0+ fully compatible.

---

## Parameter Messages (SITL Only)

### PARAM_SET — "Set an autopilot parameter"

**Used in**: state_machine.py line 169-171 (SIMULATION mode only).

**Purpose**: Adjust Cube autopilot parameters at runtime (e.g., SITL speed).

**Parameters**:
```python
param_set_send(
    target_system,      # Cube system ID (1)
    target_component,   # Cube component ID (1)
    param_id,           # Parameter name as bytes (e.g., b'SIM_SPEEDUP')
    param_value,        # Value as float
    param_type)         # MAV_PARAM_TYPE_REAL32
```

**Example** (state_machine.py line 169-171):
```python
self.master.mav.param_set_send(
    self.master.target_system, self.master.target_component,
    b'SIM_SPEEDUP',                              # Parameter name
    SIM_SPEED,                                   # Value (2.0 = 2x speedup)
    mavutil.mavlink.MAV_PARAM_TYPE_REAL32)      # Type
```

**What the Cube does** (SITL only): Runs simulation clock at `SIM_SPEEDUP × realtime` (default 1.0). Ignored on real Cube hardware.

**Real hardware**: This command has no effect. Only useful for speeding up SITL testing.

**Compatibility**: Copter 4.0+ supports SIM_SPEEDUP in SITL mode.

---

## Inbound Messages (Telemetry from Cube)

We don't send these, but we listen for them:

| **Message** | **Source** | **Purpose** |
|---|---|---|
| `HEARTBEAT` | Cube (1 Hz) | Proves connection alive |
| `COMMAND_ACK` | Cube (reply to command) | Acknowledge arm/disarm/mode commands, result codes |
| `GPS_RAW_INT` | Cube (10 Hz) | GPS fix type, lat/lon, satellites, altitude |
| `ATTITUDE` | Cube (10 Hz) | Roll/pitch/yaw in radians |
| `BATTERY_STATUS` | Cube (1 Hz) | Voltage, current, remaining capacity |
| `VFR_HUD` | Cube (10 Hz) | Airspeed, groundspeed, altitude, climb rate |

**COMMAND_ACK result codes**:
- `0` = ACCEPTED
- `1` = REJECTED (command not supported)
- `2` = FAILED (accepted but failed to execute)
- `3` = DENIED (denied by safety checks)
- `4` = FAILED (pre-arm check failed for arm command)

---

## Coordinate Frames & Altitude Conventions

### Coordinate Frames Used

| **Frame** | **Constants** | **Altitude** | **Usage** |
|---|---|---|---|
| `MAV_FRAME_GLOBAL_RELATIVE_ALT_INT` | SET_POSITION_TARGET_GLOBAL_INT | Meters AGL (above home) | GPS waypoints |
| `MAV_FRAME_LOCAL_NED` | SET_POSITION_TARGET_LOCAL_NED | N/A (velocity only) | Manual flight, velocity commands |

### Altitude References

- **AGL** (Above Ground Level) = meters above home position (takeoff point)
- **Home position** = GPS coordinate where drone armed, set at startup by Cube
- **Altitude 0m** = at home level
- **Altitude 30m** = 30 meters above home

---

## Timing & Update Rates

| **Message** | **Rate** | **Purpose** | **Notes** |
|---|---|---|---|
| SET_POSITION_TARGET_GLOBAL_INT | 0.5-2.0 Hz | Waypoint command | Throttled (every 0.2-2.0 sec) to avoid Cube overload |
| SET_POSITION_TARGET_LOCAL_NED | 10-20 Hz | Velocity command (manual) | High frequency for smooth manual control |
| MAV_CMD_DO_CHANGE_SPEED | 0.33 Hz | Set cruise speed | Throttled (once per 3 sec) |
| MAV_CMD_CONDITION_YAW | On-demand | Orientation | Sent when yaw change needed |
| REQUEST_DATA_STREAM (response) | 10 Hz | Telemetry | Cube replies 10 times per second |

---

## Safety & Failsafes

### RC Failsafe (Operator-Controlled)

The operator can override autonomous commands at any time:
1. **RC mode switch to STABILIZE/LOITER/MANUAL**: Drone switches mode immediately, ignoring all autonomous commands
2. **RC kill switch**: Disarms drone immediately (emergency)

Our code does NOT disable these failsafes. They're always active.

### Geofence (Future Work)

Geofence commands exist in the codebase (tests/flight/geofence_demo.py) but are **not enabled** in main.py.

If enabled: Cube will refuse to fly outside geofence boundaries, auto-triggering RTL or land.

### Pre-arm Checks

Before arming, the Cube verifies:
- Compass calibration OK
- Accelerometer calibration OK
- GPS lock (3D fix with 6+ satellites)
- Battery voltage sufficient
- No other hardware errors

If any check fails, ARM command returns result code 4 (FAILED).

---

## Command Acknowledgements (COMMAND_ACK)

When we send a command (arm, disarm, mode change), we wait for a COMMAND_ACK response:

```python
ack = self.master.recv_match(type='COMMAND_ACK', blocking=True, timeout=1)
if ack:
    if ack.result == 0:
        print("ACCEPTED")
    elif ack.result == 4:
        print("PRE-ARM CHECKS FAILED")
    else:
        print(f"ERROR: result code {ack.result}")
```

**Timeout**: If no ACK within 1 second, we assume the command was rejected (mavproxy/connection issue).

---

## Testing Connections

To verify the Cube is receiving commands:

```bash
# 1. Check heartbeat (proves Cube is alive)
python tests/flight/0a_cube_commands.py
# Should see: "Heartbeat received: ..."

# 2. Test mode change (proves command path works)
# Should see: "SET_MODE (GUIDED) accepted"

# 3. Test arm/disarm (proves pre-arm checks pass)
# Should see: "ARM command accepted"
```

---

## References & Further Reading

- **ArduCopter Parameters**: https://ardupilot.org/copter/docs/parameters.html
- **MAVLink Protocol**: https://mavlink.io/en/messages/common.html
- **ArduCopter Modes**: https://ardupilot.org/copter/docs/flight-modes.html
- **Set Position Target**: https://mavlink.io/en/messages/common.html#SET_POSITION_TARGET_GLOBAL_INT
- **Command Long**: https://mavlink.io/en/messages/common.html#COMMAND_LONG

---

## Summary Table: All Commands by File

| **Command** | **Files** | **State** | **Frequency** |
|---|---|---|---|
| `MAV_CMD_DO_SET_MODE` | navigation.py, state_machine.py, pi_flight.py | ARMING → GUIDED | 1× during arming |
| `MAV_CMD_COMPONENT_ARM_DISARM` | Same | ARMING, LANDING | 1-5× (retries) |
| `MAV_CMD_NAV_TAKEOFF` | Same | TAKEOFF | 1× after arming |
| `MAV_CMD_NAV_LAND` | Same | LANDING | 1-5× (retries) |
| `MAV_CMD_DO_CHANGE_SPEED` | Same | SEARCH, TRANSIT | 0.33 Hz (throttled) |
| `MAV_CMD_CONDITION_YAW` | state_machine.py | SEARCH, MANUAL | On-demand |
| `MAV_CMD_DO_SET_SERVO` | state_machine.py | HOVER_TARGET | 3× (stages) |
| `SET_POSITION_TARGET_GLOBAL_INT` | navigation.py, state_machine.py, pi_flight.py | CENTERING, SEARCH, APPROACH | 0.5-2.0 Hz |
| `SET_POSITION_TARGET_LOCAL_NED` | Same | MANUAL | 10-20 Hz |
| `REQUEST_DATA_STREAM` | state_machine.py | CONNECTING | 1× on startup |
| `PARAM_SET` | state_machine.py | CONNECTING (SITL only) | 1× on startup |

---

**Last Updated**: 2026-03-27
**For Colleagues**: Forward this to autopilot engineers or operators who need to understand what commands the drone is sending.
