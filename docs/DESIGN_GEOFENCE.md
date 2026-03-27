# NFZ Geofence Design

## 1. Defence in Depth: Three-Layer Protection

The search area for this SAR mission lies adjacent to a Site of Special Scientific Interest (SSSI), designated as a no-fly zone (NFZ). A single point of failure in boundary enforcement could result in an airspace violation, so the geofence system employs three independent protection layers, each catching what the previous one misses:

| Layer | Type | Runs on | Failure mode it covers |
|-------|------|---------|----------------------|
| **Scalar field** (speed cap) | Software | Companion computer (Pi) | Prevents high-speed overshoot into NFZ during autonomous waypoint following |
| **Vector field** (repulsive push) | Software | Companion computer (Pi) | Deflects the drone if the speed cap alone is insufficient (e.g. wind gust, GPS jump) |
| **Cube firmware geofence** | Hardware | Flight controller (Cube Orange) | Triggers LOITER or RTL if software layers fail entirely (crash, hang, lost link) |

The software layers degrade gracefully: if the companion computer loses power or the Python process crashes, the Cube's firmware geofence remains active as a hard backstop. Conversely, if the firmware geofence parameters are misconfigured, the software layers still enforce the boundary. No single failure can cause an NFZ breach.

---

## 2. Layer 1: Scalar Field (Speed Cap)

### Mechanism

When the drone is within `NFZ_SLOW_ZONE_M` (20 m) of the SSSI boundary, the software sends a `MAV_CMD_DO_CHANGE_SPEED` command to the autopilot, linearly reducing the maximum ground speed from the zone entry speed down to near-zero at the boundary itself.

### Speed profile

The speed at distance `d` metres from the NFZ boundary (where `0 <= d <= 20`):

```
speed(d) = NFZ_MIN_SPEED_MPS + (d / NFZ_SLOW_ZONE_M) * (NFZ_ZONE_MAX_SPEED_MPS - NFZ_MIN_SPEED_MPS)
```

Substituting the config.py constants:

```
speed(d) = 0.3 + (d / 20.0) * (3.0 - 0.3)
         = 0.3 + 0.135 * d       [m/s]
```

| Distance from NFZ | Speed limit |
|-------------------|-------------|
| 20 m (entering zone) | 3.0 m/s |
| 15 m | 2.325 m/s |
| 10 m | 1.65 m/s |
| 5 m | 0.975 m/s |
| 0 m (at boundary) | 0.3 m/s |
| > 20 m (outside zone) | Normal altitude-dependent speed (6--10 m/s) |

### Why linear

A linear ramp is simple, predictable, and easy to tune. The two free parameters (`NFZ_MIN_SPEED_MPS` and `NFZ_ZONE_MAX_SPEED_MPS`) directly control the endpoints. There is no risk of discontinuities or unexpected inflection points. The profile is monotonic: closer to the boundary always means slower.

### Why `DO_CHANGE_SPEED`

ArduCopter's `MAV_CMD_DO_CHANGE_SPEED` modifies the speed limit used by the autopilot's own position controller during GUIDED-mode waypoint following. This is critical: the autopilot continues to track the commanded waypoint and handle path smoothing, deceleration curves, and wind compensation internally. The companion computer only adjusts the ceiling on how fast the autopilot is allowed to fly.

The alternative considered was sending raw velocity commands (`SET_POSITION_TARGET_LOCAL_NED` with velocity fields) toward the next waypoint at the capped speed. This was implemented as the `--nfz-slow` mode and rejected because velocity commands fight the position controller: the autopilot receives conflicting instructions (a position target from the waypoint and a velocity target from the geofence), producing oscillation and jitter.

### Implementation (main.py, lines 699--706)

```python
elif not nfz_inside and nfz_dist < config.NFZ_SLOW_ZONE_M:
    ratio = nfz_dist / config.NFZ_SLOW_ZONE_M
    max_speed = config.NFZ_MIN_SPEED_MPS + ratio * (config.NFZ_ZONE_MAX_SPEED_MPS - config.NFZ_MIN_SPEED_MPS)
    self.nav.last_speed_req = 0        # bypass 3 s throttle
    self.nav.set_speed(max_speed)       # MAV_CMD_DO_CHANGE_SPEED
```

The `set_speed()` call (navigation.py, line 136) is normally throttled to once per 3 seconds to avoid flooding the autopilot. The geofence overrides this throttle by resetting `last_speed_req`, ensuring the speed cap responds immediately to distance changes.

---

## 3. Layer 2: Vector Field (Inner Polygon Repulsion)

### Mechanism

A virtual inner polygon is constructed by offsetting the SSSI boundary inward by `NFZ_INNER_OFFSET_M` (20 m). When the drone is within `NFZ_INNER_RANGE_M` (23 m) of this inner polygon, a constant-magnitude velocity command pushes the drone away from the nearest boundary edge at `NFZ_PUSH_SPEED_MPS` (3.0 m/s).

### Geometry

The effective activation zone is defined relative to the NFZ boundary:

```
signed_dist = distance_to_nfz    (positive = outside NFZ)
dist_to_inner = signed_dist + NFZ_INNER_OFFSET_M
```

Repulsion activates when `0 < dist_to_inner < NFZ_INNER_RANGE_M`, i.e.:

```
0 < signed_dist + 20 < 23
-20 < signed_dist < 3
```

This means:
- **Outside NFZ, within 3 m of boundary**: repulsion active (drone is pushed away before crossing)
- **Inside NFZ, up to 20 m deep**: repulsion active (drone is pushed back out)
- **More than 3 m outside NFZ**: repulsion inactive (normal flight)

The 3 m overlap beyond the boundary is intentional: the drone begins to feel the repulsive push *before* it reaches the NFZ edge, providing a safety margin against GPS error and control lag.

### Why constant magnitude (not gradient)

The repulsive velocity is a fixed 3.0 m/s regardless of how close the drone is to the boundary. A gradient-based force (stronger when closer) was considered but rejected because:

1. **Escape velocity must be guaranteed.** A gradient force that diminishes with distance can fail to overcome the waypoint controller's pull if the drone is at the edge of the activation zone. A constant push always exceeds the near-zero speed cap at the boundary (0.3 m/s), ensuring the drone can escape.
2. **Simplicity.** One tunable parameter (`NFZ_PUSH_SPEED_MPS`) rather than a force curve.

### Push direction computation

The push direction is determined by finding the closest point on the SSSI polygon boundary to the drone's current position, then computing the unit vector from that closest point to the drone. This is done in pixel space (via the `GeoTransformer` coordinate system) and converted back to GPS offsets.

For each edge of the polygon, the closest point is found by projecting the drone position onto the line segment:

```
t = clamp( dot(drone - p1, p2 - p1) / |p2 - p1|^2 , 0, 1 )
closest = p1 + t * (p2 - p1)
```

The push vector is then:

```
push_direction = normalize(drone_position - closest_point)
velocity = push_direction * NFZ_PUSH_SPEED_MPS
```

### Implementation (main.py, lines 708--727)

```python
signed_dist = nfz_dist if not nfz_inside else -nfz_dist
dist_to_inner = signed_dist + config.NFZ_INNER_OFFSET_M
if 0 < dist_to_inner < config.NFZ_INNER_RANGE_M:
    off_lat, off_lon = self.geofence.repulsive_offset(self.lat, self.lon)
    ...
    push_n = -off_lat * lat_m
    push_e = -off_lon * lon_m
    if nfz_inside:
        push_n = -push_n
        push_e = -push_e
    mag = math.sqrt(push_n**2 + push_e**2)
    strength = config.NFZ_PUSH_SPEED_MPS
    self.nav.send_velocity(push_n / mag * strength, push_e / mag * strength, 0, ...)
```

The velocity command is sent via `SET_POSITION_TARGET_LOCAL_NED` in the NED frame, overriding any waypoint-following velocity for that control cycle. Because the speed cap (Layer 1) has already reduced the waypoint-following speed to near-zero at the boundary, the repulsive push dominates.

---

## 4. Design Evolution: Three Approaches Tested

Three NFZ avoidance strategies were implemented and tested in SITL simulation before arriving at the final design.

### Approach 1: `--nfz-repel` (velocity commands only)

The original approach used an inverse-distance potential field: the closer to the NFZ, the stronger the repulsive velocity command. No speed cap was applied.

**Problem:** The repulsive velocity commands fought the autopilot's position controller. ArduCopter simultaneously tried to fly toward the commanded waypoint (position target) and away from the NFZ (velocity target). The result was oscillation at the buffer boundary, with the drone jittering back and forth rather than smoothly slowing down.

**Buffer zone:** 8 m (smaller, because the force was stronger at close range).

### Approach 2: `--nfz-slow` (velocity toward waypoint, speed capped)

The second approach computed the direction vector from the drone to its current waypoint, then sent velocity commands at a capped speed (the same linear ramp as the final design). No position targets were used in the buffer zone.

**Problem:** This required the companion computer to compute the navigation direction itself, duplicating what the autopilot already does internally. The velocity commands were jittery because they were recomputed every control cycle with slightly different GPS readings. The drone's path was less smooth than ArduCopter's internal path following.

**Buffer zone:** 20 m.

### Approach 3: `--nfz-carrot` (DO_CHANGE_SPEED + inner polygon push) -- **Selected**

The final approach separates concerns: the scalar field (Layer 1) handles speed reduction via `DO_CHANGE_SPEED`, letting the autopilot handle direction. The vector field (Layer 2) handles emergency deflection via velocity commands, but only activates within 3 m of the actual boundary where the speed cap alone might be insufficient.

**Why this won:**

1. **No oscillation.** The speed cap does not conflict with position targets; it modifies the same speed parameter the autopilot uses internally.
2. **Same flight path.** The drone follows the exact same waypoint sequence as without a geofence, just slower near the NFZ. No path re-planning required.
3. **Pilot override preserved.** `DO_CHANGE_SPEED` only affects GUIDED and AUTO modes. A pilot switching to STABILIZE or LOITER on the RC transmitter gets full stick authority with no software interference.
4. **Minimal code.** Three lines for the speed cap, plus the existing `repulsive_offset()` for the emergency push. No direction computation, no waypoint awareness.

---

## 5. Sign Conventions

The sign chain through the geofence computation involves three inversions that were the source of a significant debugging effort. They are documented here to prevent regressions.

### `cv2.pointPolygonTest` returns positive for INSIDE

```python
signed_dist_px = cv2.pointPolygonTest(contour, point, True)
is_inside = signed_dist_px > 0    # positive = inside polygon
```

This is counter-intuitive (one might expect "distance to boundary" to be positive outside). The original implementation had the sign inverted, which caused the hard-boundary trigger to fire in the buffer zone (outside the NFZ) instead of inside it.

### `repulsive_offset()` returns negated values

The `geofence.py` function `repulsive_offset()` converts the push direction from pixel space to GPS offsets using `pixels_to_gps()`, then subtracts `REF_LAT` and `REF_LON` to obtain a delta. Due to the coordinate system conventions of `GeoTransformer` (pixel Y increases downward, latitude increases upward), the resulting offset has inverted signs. The function compensates by returning `-offset_lat, -offset_lon` (geofence.py, line 180).

Without this negation, the "repulsive" force would *attract* the drone toward the NFZ.

### Inside-NFZ direction flip

When the drone is inside the NFZ, the push direction from `repulsive_offset()` points inward (toward the nearest boundary point, which is now "outward" in the reversed sense). The main loop compensates with an additional sign flip (main.py, lines 721--723):

```python
if nfz_inside:
    push_n = -push_n
    push_e = -push_e
```

### Complete sign chain

```
Drone outside NFZ, near boundary:
  cv2.pointPolygonTest  -> negative (outside)
  repulsive_offset      -> negated (pushes away from boundary)  [correct]
  main.py               -> no flip                              [correct: push away]

Drone inside NFZ:
  cv2.pointPolygonTest  -> positive (inside)
  repulsive_offset      -> negated (pushes toward boundary)     [wrong direction]
  main.py               -> flip applied                         [corrected: push out]
```

---

## 6. Manual Mode and NFZ Interaction

In the simulator (`simple_simulator.py`) and headless operation (`main.py --headless`), pressing the M key enters a software MANUAL mode. Despite the name, the drone remains in ArduCopter's GUIDED flight mode; WASD commands are translated to `SET_POSITION_TARGET_LOCAL_NED` velocity commands.

| Geofence layer | Effect in software MANUAL |
|----------------|--------------------------|
| Speed cap (`DO_CHANGE_SPEED`) | **No effect.** The speed cap modifies the autopilot's speed limit for position-target navigation. Velocity commands from WASD bypass this limit entirely. |
| Inner polygon repulsion | **Active.** The repulsive velocity push runs every control cycle regardless of state (except INIT, CONNECTING, ARMING, TAKEOFF, LANDING, DONE). In MANUAL mode, the repulsive push adds to the operator's WASD commands. |
| Cube firmware geofence | **Active.** The firmware geofence operates independently of all software modes. |

On real hardware with an RC transmitter, switching to STABILIZE or LOITER on the mode switch disconnects the companion computer from the control loop entirely. The pilot has full manual control with no software intervention. The Cube firmware geofence is the only remaining protection layer.

---

## 7. Configuration Constants

All geofence parameters are defined in `config.py` (lines 209--215) and can be tuned without code changes:

| Constant | Value | Unit | Purpose |
|----------|-------|------|---------|
| `NFZ_SLOW_ZONE_M` | 20.0 | m | Outer radius of the speed-cap scalar field |
| `NFZ_MIN_SPEED_MPS` | 0.3 | m/s | Speed limit at the NFZ boundary (near-stop) |
| `NFZ_ZONE_MAX_SPEED_MPS` | 3.0 | m/s | Speed limit at the outer edge of the slow zone |
| `NFZ_INNER_OFFSET_M` | 20.0 | m | Inward offset of the inner (repulsion) polygon from the NFZ boundary |
| `NFZ_INNER_RANGE_M` | 23.0 | m | Activation range for repulsive push (measured from inner polygon) |
| `NFZ_PUSH_SPEED_MPS` | 3.0 | m/s | Magnitude of the repulsive velocity command |

Additionally, `NFZGeofence` (geofence.py) defines instance-level thresholds:

| Attribute | Value | Purpose |
|-----------|-------|---------|
| `HARD_BOUNDARY` | 3.0 m | Inside NFZ or closer than this triggers auto-MANUAL |
| `SOFT_BOUNDARY` | 8.0 m | Legacy repulsive activation range (used by `repulsive_offset()`) |
| `WAYPOINT_BUFFER` | 30.0 m | Plan-time waypoint filter distance |

---

## 8. Auto-MANUAL on NFZ Entry

If the drone's GPS position falls inside the SSSI polygon (or within `HARD_BOUNDARY` = 3 m of it), the software immediately:

1. Saves the current state and position as departure reference
2. Switches to software MANUAL mode
3. Sends a zero-velocity command (`send_velocity(0, 0, 0)`) to halt the drone
4. Prints a warning: `[GEOFENCE] INSIDE NFZ! Switching to MANUAL -- fly out!`

The operator must then use WASD (in simulation) or the RC transmitter (in flight) to fly the drone back outside the NFZ boundary. The inner polygon repulsion assists by pushing the drone outward.

This is a last-resort software measure. On real hardware, the Cube's firmware geofence is configured to trigger LOITER (hold position) or RTL (return to launch) when the drone crosses the hardware geofence boundary. Because the firmware geofence operates at the flight controller level with direct access to the IMU and GPS, it reacts faster than the companion computer's Python loop (~10 Hz). The firmware geofence would typically intervene before the software auto-MANUAL logic executes.

The defence-in-depth rationale: the software auto-MANUAL catches cases where the firmware geofence is misconfigured, has a different boundary definition, or is disabled for testing. The firmware geofence catches cases where the companion computer has crashed, lost USB connection, or is running too slowly.
