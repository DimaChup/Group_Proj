# State Machine Design

This document describes the finite state machine (FSM) that governs the autonomous
SAR drone mission. It is intended as a reference section for the MSc project report
(AENGM0074) and covers rationale, state definitions, transitions, and key design
choices.

---

## 1. Why a State Machine

The SAR mission consists of discrete, sequential phases: connect to the autopilot,
arm, take off, fly a search pattern, investigate detections, deliver a payload, and
return home. Each phase has a single responsibility, well-defined entry conditions,
and a clear successor. A finite state machine is the standard approach for mission
sequencing in autonomous robotics because it provides:

- **Deterministic behaviour.** At any instant the drone is in exactly one state. The
  transition function is a pure mapping from (current state, sensor inputs, operator
  commands) to next state. This makes the system auditable and testable.

- **Timeout safety.** Every state that waits for an external condition (heartbeat,
  GPS fix, operator confirmation) carries a wall-clock timeout. If the condition is
  not met within the allowed window the machine transitions to a safe fallback
  (abort, resume search, or land). This prevents the drone from hanging indefinitely
  at any point in the mission.

- **Separation of concerns.** Detection logic lives in `vision.py`, path planning in
  `planning.py`, navigation commands in `navigation.py`, and geo-transforms in
  `utils.py`. The state machine in `state_machine_no_descend.py` orchestrates these
  modules without duplicating their logic.

- **Operator override at every state.** The M key and the RC transmitter switch can
  interrupt any state. The machine records where it was and returns there after the
  override ends.

The implementation uses a dispatch dictionary in `main.py` (line 637) that maps each
`State` constant to a handler method. The main loop calls the active handler once per
iteration, passing the latest detection result and keypress. All handler methods are
defined in the `StateHandlersMixin` class (`state_machine_no_descend.py`), which the
`VisualFlightMission` class inherits via mixin.

---

## 2. States and Transitions

### 2.1 State List

| State | Responsibility |
|-------|---------------|
| `INIT` | Establish MAVLink connection to autopilot |
| `CONNECTING` | Wait for first heartbeat from Cube |
| `ARMING` | Wait for GPS fix (fix_type >= 3, sats >= 6), set GUIDED mode, arm motors |
| `TAKEOFF` | Climb to `TARGET_ALT` (35 m). Generate search pattern on arrival |
| `PRE_WAYPOINTS` | Fly pre-planned transit waypoints (e.g. obstacle-avoidance corridor) |
| `TRANSIT_TO_SEARCH` | Fly to first waypoint of the lawnmower pattern |
| `SEARCH` | Follow lawnmower waypoints. Run detection every frame. Queue targets |
| `CENTERING` | Fly to the estimated GPS position of a queued detection |
| `VERIFY` | Hold position. Operator classifies: Y (confirm), N (reject), I (interest) |
| `APPROACH` | Descend to 3 m above the 7.5 m offset landing spot |
| `HOVER_TARGET` | Hold at 3 m. Two-stage servo payload release. 15 s total hold |
| `RETURN_TRANSIT` | Retrace transit waypoints in reverse at search altitude |
| `RETURN_HOME` | Fly to home (takeoff) position |
| `LANDING` | Send `MAV_CMD_NAV_LAND`. Wait for touchdown (3 frames below 0.3 m) |
| `DONE` | Mission complete. Disarm. Log final distance from home |
| `MANUAL` | Operator flies via WASD velocity commands. Detections are queued |
| `RETURN_FROM_MANUAL` | Fly back to the point where MANUAL was engaged |
| `RETURN_TO_SEARCH` | Climb to search altitude and fly back to scan-line departure point |
| `HOVER` | Fallback idle state if no waypoints were generated (60 s timeout) |
| `DESCENDING` | Legacy state, immediately forwards to `VERIFY` (no-descend design) |

### 2.2 ASCII State Diagram

```
                           ┌─────────────────────────────────────────────┐
                           │            MANUAL OVERRIDE (M key)          │
                           │  Any state ──► MANUAL ──► RETURN_FROM_MANUAL│
                           │                  │             │            │
                           │                  │  (close)    ▼            │
                           │                  └────► previous_state      │
                           └─────────────────────────────────────────────┘

 ┌──────┐    heartbeat    ┌────────────┐   GPS fix + armed   ┌─────────┐
 │ INIT ├────────────────►│ CONNECTING ├────────────────────►│ ARMING  │
 └──────┘                 └────────────┘                     └────┬────┘
                                                                  │ armed
                                                                  ▼
                                                            ┌──────────┐
                                                            │ TAKEOFF  │
                                                            └────┬─────┘
                                                                 │ alt >= 90% TARGET_ALT
                                          ┌──────────────────────┤
                                          │ (transit file loaded) │ (no transit)
                                          ▼                       ▼
                                   ┌──────────────┐    ┌──────────────────┐
                                   │PRE_WAYPOINTS │    │TRANSIT_TO_SEARCH │
                                   └──────┬───────┘    └────────┬─────────┘
                                          │ all pre-WPs         │ arrived
                                          ▼                     │
                                   ┌──────────────────┐         │
                                   │TRANSIT_TO_SEARCH │◄────────┘
                                   └────────┬─────────┘
                                            │ arrived at WP[0]
                                            ▼
                           ┌────────────────────────────────┐
                           │            SEARCH              │
                           │  Follow lawnmower waypoints.   │
                           │  Queue detections via CV.      │
                           │  B key ──► beacon redirect.    │
                           └───────┬──────────┬─────────────┘
                                   │          │
                      detection    │          │ all WPs done,
                      queued &     │          │ no confirm
                      popped       │          ▼
                                   │   ┌─────────────┐  pass < MAX_RESCAN
                                   │   │  (rescan)   ├──────► SEARCH
                                   │   │  drop alt   │       (lower alt)
                                   │   └──────┬──────┘
                                   │          │ pass >= MAX_RESCAN
                                   │          ▼
                                   │       ┌──────┐
                                   │       │ DONE │
                                   │       └──────┘
                                   ▼
                           ┌───────────┐  timeout 60s   ┌────────┐
                           │ CENTERING ├───────────────►│ SEARCH │
                           └─────┬─────┘                └────────┘
                                 │ dist < 1.0 m
                                 ▼
                           ┌──────────┐
                           │  VERIFY  │
                           └──┬──┬──┬─┘
                    Y confirm │  │  │ N reject / I interest
                              │  │  │
                              │  │  └──► queue pop ──► CENTERING
                              │  │       or RETURN_TO_SEARCH ──► SEARCH
                              │  │
                              │  │ timeout 120s ──► reject ──► SEARCH
                              ▼
                    (select landing side N/E/S/W)
                              │
                              ▼
                       ┌──────────┐
                       │ APPROACH │  fly to 7.5 m offset, descend to 3 m
                       └────┬─────┘
                            │ dist < 2 m, alt < 4 m
                            ▼
                     ┌─────────────┐
                     │ HOVER_TARGET│  servo release (3s partial, 6s full)
                     └──────┬──────┘
                            │ 15 s elapsed
                            ▼
                 ┌─────────────────┐  (transit path exists)
                 │ RETURN_TRANSIT  ├──► retrace pre-waypoints in reverse
                 └────────┬────────┘
                          │ all retraced
                          ▼
                    ┌─────────────┐
                    │ RETURN_HOME │  fly to home_lat, home_lon
                    └──────┬──────┘
                           │ dist < 2 m
                           ▼
                      ┌─────────┐
                      │ LANDING │  MAV_CMD_NAV_LAND, retry up to 5x
                      └────┬────┘
                           │ 3 frames below 0.3 m
                           ▼
                       ┌──────┐
                       │ DONE │
                       └──────┘
```

---

## 3. No-Descend Design

Earlier iterations of the state machine included a `DESCENDING` state that lowered
the drone from search altitude (35 m) to a verification altitude (15 m) before
presenting the operator with the confirm/reject prompt. The current design
(`state_machine_no_descend.py`) eliminates that descent for three reasons:

1. **Camera FOV is sufficient at 35 m.** The onboard camera (IMX296, 1456 x 1088 px,
   HFOV 54.4 deg) covers approximately 37 m x 28 m of ground at 35 m altitude. A
   casualty dummy (0.5 m x 1.8 m) spans roughly 20-25 pixels at this altitude, which
   is above the YOLOv8n detection threshold validated in DJI video analysis
   (`tests/laptop/video_test.py`). The operator can visually confirm the target in
   the MJPEG stream without needing a closer view.

2. **Time and battery savings.** A 20 m descent and re-climb at 2 m/s costs 20
   seconds each way (40 seconds total), plus stabilisation time. Over a mission with
   multiple false positives this penalty compounds. Staying at search altitude allows
   the drone to immediately resume the pattern after a rejection.

3. **Reduced collision risk.** The search area (Failand, Bristol) contains hedgerows
   and trees up to 10-15 m. Descending to 15 m puts the drone within the obstacle
   envelope. Remaining at 35 m maintains a comfortable margin above all terrain
   features.

The `DESCENDING` state is retained in `states.py` for backward compatibility. Its
handler (`_handle_descending`, line 559) immediately transitions to `VERIFY` if the
state is entered.

When the `--center-verify` flag is set, the `CENTERING` state initiates GPS sample
collection as the drone arrives above the target. During `VERIFY`, the system
accumulates GPS readings for 10 seconds, then computes a centroid. This averaged
position replaces the initial trigonometric estimate:

```
Trig estimate (flyover)  ──►  Centering refinement  ──►  10 s GPS average
       CEP ~5 m                     CEP ~2 m                  CEP ~1 m
```

The GPS averaging is opt-in because it adds 10 seconds of hover time per detection.
For missions where time is critical and the trig estimate is adequate, the flag is
omitted.

---

## 4. Manual Override Architecture

The system provides two independent override mechanisms with different trust levels:

### 4.1 Software Override (M Key)

Pressing M transitions from any state to `MANUAL`. The drone remains in GUIDED mode
and ArduCopter continues to accept MAVLink velocity commands from the Pi. The
operator flies using WASD (horizontal), R/F (vertical), and Q/E (yaw). The state
machine records:

- `previous_state` -- the state to resume after override ends
- `manual_departure_lat`, `manual_departure_lon`, `manual_departure_alt` -- the
  position to return to

Pressing M again exits `MANUAL`. The system first checks for any targets in the
detection queue and investigates those. If the drone has moved more than 5 m from the
departure point, it enters `RETURN_FROM_MANUAL` to fly back before resuming. If
within 5 m, it resumes the previous state directly.

During `MANUAL` mode, detections are still queued (line 900-911 of
`state_machine_no_descend.py`). This means the operator can manually fly over an area
of interest and accumulate detections, which are then investigated automatically when
manual mode ends.

### 4.2 Hardware Override (RC Transmitter)

The RC transmitter's mode switch can change the flight mode to STABILIZE or LOITER at
any time. This bypasses the MAVLink command layer entirely -- ArduCopter ignores all
GUIDED-mode position targets and the pilot has direct stick control. This is a
hardware-level safety mechanism that cannot be overridden by software.

### 4.3 Why Two Levels

The M key is a convenience for simulation testing and for the ground station operator
to briefly reposition the drone without breaking the mission flow. The RC switch is a
safety-critical mechanism for the flight pilot: if the software misbehaves, the pilot
can instantly take control without relying on the software processing a keypress.

---

## 5. Detection Queue Integration

The detection queue decouples target discovery from target investigation. During
`SEARCH`, every valid detection is appended to `self._detect_queue` as a
`(lat, lon, confidence)` tuple. The queue is processed one target at a time:

1. **Queueing (SEARCH, line 420-445).** Each frame, if a detection is found:
   - The trigonometric GPS position is computed from pixel coordinates.
   - The position is checked against three filters: NFZ boundary, search area
     boundary, and proximity to known targets (`_is_near_known` checks rejected
     targets, items of interest, and already-queued positions within
     `REJECTED_TARGET_RADIUS_M` = 5 m).
   - If `--smart-detect` is active, `DETECT_CONFIRM_FRAMES` (3) consecutive frames
     must detect before the target is queued.
   - Otherwise, a single detection queues the target immediately.

2. **Popping (SEARCH, line 450).** After the detection check, if the queue is
   non-empty, `_pop_valid_target()` is called. This method pops the front of the
   queue and re-validates the target (NFZ, search area, proximity). Invalid targets
   are silently discarded. The first valid target becomes the investigation target.

3. **Departure point preservation.** When the first detection causes a departure from
   the scan line, `self.departure_lat` and `self.departure_lon` are recorded (line
   456-457). This departure point is preserved across multiple queue pops. After an
   N or I response in `VERIFY`, the system pops the next queue item (line 1008-1016)
   and transitions to `CENTERING` without overwriting the departure point. Only when
   the queue is exhausted does the drone return to `departure_lat/departure_lon` via
   `RETURN_TO_SEARCH`.

4. **Queue during CENTERING and MANUAL.** New detections spotted while centering on a
   different target are queued if they fall outside the `DETECT_LOCK_RADIUS_M` (5 m)
   from the locked target (line 521-528). Detections during `MANUAL` mode are also
   queued (line 900-909) and investigated when the operator exits manual mode.

---

## 6. Timeout Handling

Every state that blocks on an external condition has a timeout to prevent the drone
from hovering indefinitely:

| State | Timeout | Action on Expiry |
|-------|---------|-----------------|
| `CONNECTING` | 30 s (logged warning every 15 s) | Continues retrying, prints diagnostic |
| `ARMING` | 120 s | Prints `ARMING TIMEOUT` warning. Does not abort (operator may fix pre-arm checks) |
| `TAKEOFF` | 60 s | Prints `TAKEOFF TIMEOUT` warning |
| `CENTERING` | 60 s | Transitions to `SEARCH` (target lost or cannot converge) |
| `VERIFY` | 120 s | Rejects target, appends to `rejected_targets`, transitions to `SEARCH` |
| `HOVER_TARGET` | 15 s | Closes servo, climbs, transitions to `RETURN_TRANSIT` or `RETURN_HOME` |
| `HOVER` | 60 s | Transitions to `DONE` (no waypoints to fly) |
| `LANDING` | 5 s per retry, 5 retries max | Force disarm after 5 failed `MAV_CMD_NAV_LAND` attempts |

All timeouts are measured against `self.state_start_time`, which is reset by
`_set_state()` on every transition (line 55-64). This ensures that re-entering a
state (e.g. `SEARCH` after a rescan) resets the timer.

The rationale is straightforward: an autonomous drone operating beyond visual line of
sight cannot rely on the operator noticing a stuck state. The timeout values are
conservative -- long enough to accommodate GPS drift, slow convergence, and operator
reaction time, but short enough to prevent battery exhaustion or drift into restricted
airspace.

---

## 7. Rescan Logic

If the drone completes all lawnmower waypoints without the operator confirming a
target (Y), it does not immediately end the mission. Instead, it drops altitude and
regenerates the search pattern:

1. The current search altitude is multiplied by `RESCAN_ALT_FACTOR` (0.8). At the
   default `TARGET_ALT` of 35 m, the second pass flies at 28 m, and the third at
   22.4 m.

2. The altitude floor `RESCAN_ALT_FLOOR_M` (15 m) prevents the drone from descending
   into the obstacle envelope. If the computed altitude falls to or below this floor,
   the mission ends.

3. Up to `MAX_RESCAN_PASSES` (3) additional passes are flown. The pass counter
   `self.rescan_pass` tracks which pass is active.

4. Each rescan regenerates the lawnmower pattern via
   `self.planner.generate_search_pattern()` with `alt_override` set to the new
   altitude (line 488-489). Because the swath width is a function of altitude and
   camera FOV, the regenerated pattern has tighter line spacing, increasing the
   overlap and probability of detection.

5. The yaw orientation is reset (`_search_yaw_done = False`, line 492) so the drone
   re-aligns its diagonal footprint for the new pass direction. This diagonal
   realignment maximises the camera's ground coverage along the perpendicular axis.

6. Rejected targets are preserved across passes. A target marked N (false positive)
   on pass 1 will not trigger investigation on pass 2.

The rescan approach addresses a key uncertainty in aerial SAR: the detection model may
miss a target on a single pass due to lighting angle, motion blur, or partial
occlusion. Lower altitude improves the ground sampling distance (more pixels on
target), and the re-oriented scan direction presents the target from a different
viewing angle.

---

## 8. PLB Beacon Redirect

A Personal Locator Beacon (PLB) transmission provides an approximate GPS position for
the casualty. When received, the drone should abandon the broad area search and focus
on a smaller polygon around the beacon signal. The state machine supports this via the
`_trigger_beacon_redirect()` method (line 762).

### Trigger Mechanisms

- **B key** during `SEARCH` state (line 896-897): simulates a PLB signal.
- **`--beacon-delay N` flag**: automatically triggers the redirect N seconds after
  `SEARCH` begins (line 402-409). Used for simulation testing.

### Redirect Sequence

1. The focus area polygon is loaded from `flight_plans/focus_area.json` (re-read on
   each trigger, allowing mid-flight coordinate updates). If the JSON file does not
   exist, it falls back to `config.FOCUS_AREA_GPS` (drawn interactively or loaded
   from KML).

2. The planner's search polygon is replaced with the focus area polygon (line
   808-810).

3. A new lawnmower pattern is generated for the smaller polygon from the drone's
   current position (line 820-822). The `_focus_area = True` flag on the planner
   enables tighter swath margins for complete coverage of the smaller area.

4. The waypoint index and rescan counter are reset (line 822-823). The search speed
   drops to `FOCUS_SEARCH_SPEED_MPS` (5 m/s, vs 10 m/s default) to allow more
   detection time per frame (line 396-397).

5. Rejected targets from the broad search are preserved -- false positives marked
   before the redirect remain marked.

---

## 9. Servo Payload Delivery

The `HOVER_TARGET` state manages payload release at 3 m above the computed landing
spot (7.5 m lateral offset from the confirmed target position). The servo operates on
a two-stage release timeline:

| Time (s) | Action | Servo PWM |
|-----------|--------|-----------|
| 0 | Arrive at 3 m hover | 1500 (closed) |
| 3 | Stage 1: partial release | 1300 |
| 6 | Stage 2: full release | 1100 |
| 15 | Close servo, depart | 1500 (closed) |

The two-stage approach provides a controlled release rather than a single sudden drop.
Stage 1 loosens the payload at 3 seconds, Stage 2 fully releases at 6 seconds. The
drone holds position for a total of 15 seconds to allow the payload to clear the
release mechanism and reach the ground.

Servo commands are sent via `MAV_CMD_DO_SET_SERVO` on channel 9 (line 627-650). The
channel and PWM values are defined as constants in the handler method; for production
flights these should be moved to `config.py` and verified on the bench before flight.

After the 15-second hold, the servo is closed, the drone climbs to search altitude,
and transitions to `RETURN_TRANSIT` (if transit waypoints exist) or `RETURN_HOME`
(direct return).

---

## 10. GPS Position Estimation Flow

Locating the target involves three stages of increasing accuracy. Each stage refines
the position estimate from the previous one:

### Stage 1: Trigonometric Estimate (Flyover)

During `SEARCH`, when the detection model finds a target in frame, the pixel
coordinates `(px_u, px_v)` are passed to `calculate_target_gps()`. This method uses
the drone's current GPS position, altitude, yaw, and the camera's calibrated FOV to
project the pixel location onto the ground plane:

```
target_lat = drone_lat + (offset_north / 111320)
target_lon = drone_lon + (offset_east / (111320 * cos(lat)))
```

where `offset_north` and `offset_east` are computed from the pixel displacement, the
altitude-dependent ground sampling distance, and the drone's heading. This estimate
has a circular error probable (CEP) of approximately 5 m, dominated by GPS latency
(100-200 ms) and single-frame noise.

### Stage 2: Centering Refinement

In `CENTERING`, the drone flies to the Stage 1 estimate and hovers above the target.
As it approaches, the detection model re-acquires the target. Each frame refines the
locked target position via `_locked_target` updates (line 519), but only if the new
detection falls within `DETECT_LOCK_RADIUS_M` (5 m) of the locked position. This
prevents a nearby second target from corrupting the estimate.

When the drone is directly above the target (distance < 1.0 m), the pixel
displacement is near zero, and the GPS position is effectively the drone's own GPS
reading projected downward. CEP improves to approximately 2 m.

### Stage 3: GPS Averaging (Optional, `--center-verify`)

If the `--center-verify` flag is set, the `CENTERING` state starts collecting GPS
samples (`self._gps_avg_samples`) when the drone arrives above the target. Collection
continues through the `VERIFY` state for 10 seconds. The final position is the
arithmetic mean of all samples:

```python
avg_lat = sum(s[0] for s in samples) / len(samples)
avg_lon = sum(s[1] for s in samples) / len(samples)
```

At the telemetry rate of 10 Hz, this averages approximately 100 GPS readings,
suppressing random noise. The averaged position replaces the trig estimate as the
final target location used for the approach and landing offset calculation. CEP
improves to approximately 1 m.

The three-stage pipeline ensures that even without the optional averaging, the
position is refined from a rough flyover estimate to a centered overhead reading
before any approach or payload delivery is attempted.
