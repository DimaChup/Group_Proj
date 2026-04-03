# main.py Feature Verification Checklist

> Code-inspected feature list for `main.py` + `state_machine.py`.
> Status: **VERIFIED** = confirmed in code, **UNTESTED** = code exists but never flight-tested,
> **BROKEN** = known issue. Last updated: 2026-04-03.

---

## Mission States

All states defined in `states.py`, handlers in `state_machine.py`, dispatch table in `main.py:726-745`.

| # | State | Handler | Status | Notes |
|---|-------|---------|--------|-------|
| 1 | INIT | `_handle_init` | VERIFIED | Connects to Cube via `config.CONNECTION_STR`. Retries every 1s. |
| 2 | CONNECTING | `_handle_connecting` | VERIFIED | Waits for heartbeat, requests data streams, sets SITL speedup. 15s warning if no heartbeat. |
| 3 | ARMING | `_handle_arming` | VERIFIED | Waits for GPS fix (type>=3, sats>=6), sets GUIDED mode, sends arm command. 120s timeout warning. |
| 4 | TAKEOFF | `_handle_takeoff` | VERIFIED | `MAV_CMD_NAV_TAKEOFF` to `TARGET_ALT`. Transitions at 90% altitude. 60s timeout warning. Re-arms in SIM if disarmed. |
| 5 | PRE_WAYPOINTS | `_handle_pre_waypoints` | VERIFIED | Flies transit waypoints from `flight_plans/transit.json` before entering search area. |
| 6 | TRANSIT_TO_SEARCH | `_handle_transit_to_search` | VERIFIED | Flies to first search waypoint at `TRANSIT_SPEED_MPS`. |
| 7 | SEARCH | `_handle_search` | VERIFIED | Lawnmower (or spiral with `--spiral`) pattern. Yaw alignment, speed adaptation, detection processing, beacon redirect. Rescan at lower altitude if pattern exhausted. |
| 8 | CENTERING | `_handle_centering` | VERIFIED | Flies to target GPS. 60s timeout (auto-resumes search). Locks target within `DETECT_LOCK_RADIUS_M`, queues new detections outside radius. |
| 9 | DESCENDING | `_handle_descending` | VERIFIED | Descends to `VERIFY_ALT` (or halfway between search alt and 3m). Velocity-controlled descent. |
| 10 | VERIFY | `_handle_verify` | VERIFIED | 120s operator timeout (auto-reject). Y/N/I/X input. GPS averaging (10s) when `--center-verify`. Periodic countdown warnings at 60s, 90s, 100s+. |
| 11 | HOVER | `_handle_hover` | VERIFIED | Fallback state when no waypoints generated. 60s timeout to DONE. |
| 12 | APPROACH | `_handle_approach` | VERIFIED | Flies to 7.5m offset landing spot, descends to 3m deploy altitude. Yaw toward landing point. |
| 13 | HOVER_TARGET | `_handle_hover_target` | VERIFIED | 15s hover with 2-stage servo payload release (3s partial, 6s full). Servo PWM from config. Animation overlay on HUD. |
| 14 | RETURN_TO_SEARCH | `_handle_return_to_search` | VERIFIED | Returns to departure point after reject/IOI, resumes search pattern. |
| 15 | RETURN_FROM_MANUAL | `_handle_return_from_manual` | VERIFIED | Safety checks (GPS fix, NFZ position) before resuming. Flies back to manual departure point at departure altitude. |
| 16 | RETURN_TRANSIT | `_handle_return_transit` | VERIFIED | Retraces transit waypoints in reverse after payload deploy. Climbs to search altitude. Yaw toward each waypoint. |
| 17 | RETURN_HOME | `_handle_return_home` | VERIFIED | Flies to home (takeoff) position. Guards against unknown home if GPS never fixed. Yaw toward home. |
| 18 | LANDING | `_handle_landing` | VERIFIED | `MAV_CMD_NAV_LAND` with retry (5 retries). Touchdown detection via altimeter (0.5m threshold, 5 consecutive ticks). ArduPilot auto-disarm detection. |
| 19 | MANUAL | via `_handle_manual_toggle` | VERIFIED | WASD/RF/QE velocity commands. NFZ viscous field clamps approach velocity. Detections queued during manual flight. |
| 20 | DONE | (no handler) | VERIFIED | Final distance displayed. 3s pause then exit. CSV log closed. |

### State Flow
```
INIT -> CONNECTING -> ARMING -> TAKEOFF -> PRE_WAYPOINTS -> TRANSIT_TO_SEARCH -> SEARCH
                                                                                   |
                                                         detection               v
                                                                             CENTERING
                                                                                   |
                                                                                   v
                                                                         DESCENDING (optional)
                                                                                   |
                                                                                   v
                                                                               VERIFY
                                                                              /   |   \
                                                                           Y     I      N/X
                                                                          /      |        \
                                                              select side    IOI log    RETURN_TO_SEARCH
                                                              (N/E/W/S)                (or next queued)
                                                                   |
                                                                   v
                                                    APPROACH -> HOVER_TARGET -> RETURN_TRANSIT -> RETURN_HOME -> LANDING -> DONE

Any state: M -> MANUAL -> M -> RETURN_FROM_MANUAL -> resume previous state
```

---

## Safety Features

| # | Feature | Location | Status | Notes |
|---|---------|----------|--------|-------|
| 1 | RC override guard | `main.py:760-767` | VERIFIED | If Cube mode != GUIDED(4) or LAND(9), ALL commands/keys/geofence skipped. Pilot has full control. Runs BEFORE key handling. |
| 2 | SSSI geofence (hard boundary) | `main.py:883-901` `_enforce_geofence()` | VERIFIED | Inside NFZ -> auto-switch to MANUAL + zero velocity. Skips MANUAL switch during APPROACH/RETURN (position target pulls drone out). |
| 3 | SSSI geofence (soft boundary / speed ramp) | `main.py:907-960` | VERIFIED | Directional speed clamping (default) or total speed clamping (`--nfz-total-speed`). Linear ramp from 0 m/s at `NFZ_SCALAR_ZERO_M` (2m) to `NFZ_ZONE_MAX_SPEED_MPS` at `NFZ_SLOW_ZONE_M` (20m). |
| 4 | NFZ repulsive push (MANUAL mode) | `main.py:962-978` | VERIFIED | Inverse-distance potential field pushes drone away from inner NFZ boundary. Only active in MANUAL state. |
| 5 | GPS degradation RTL | `main.py:484-521` `_check_gps_degradation()` | VERIFIED | Monitors fix_type and satellites. 5s sustained degradation (fix<3 or sats<6) triggers `_emergency_rtl()` + LANDING state. Throttled warnings every 3s. Recovery clears timer. |
| 6 | Force disarm after 90s landing timeout | `state_machine.py:767-774` | VERIFIED | `MAV_CMD_COMPONENT_ARM_DISARM` with force param 21196. Also force-disarms after 5 failed LAND retries. |
| 7 | Landing spot NFZ buffer check | `main.py:534-556` `calculate_landing_spot()` | VERIFIED | If landing spot is within 15m of NFZ, tries all 4 directions (N/S/E/W) and picks the one furthest from NFZ. |
| 8 | Emergency RTL on link loss | `main.py:980-998` `_emergency_rtl()` | VERIFIED | Sets RTL mode (mode 6) via MAVLink. Called on ConnectionResetError, BrokenPipeError, OSError. Falls back to ArduCopter GCS failsafe. |
| 9 | KeyboardInterrupt RTL | `main.py:1096-1097` | VERIFIED | Ctrl+C triggers `_emergency_rtl()` before exit. |
| 10 | Takeoff disarm detection | `state_machine.py:225-232` | VERIFIED | If disarmed during takeoff: retries in SIM, safety-stops in REAL. |
| 11 | Resume safety checks | `state_machine.py:280-293` | VERIFIED | Before resuming from MANUAL: validates GPS fix (type>=3, sats>=4) and NFZ position. Blocks resume if inside NFZ. |
| 12 | Arming timeout warning | `state_machine.py:168-172` | VERIFIED | 120s warning with actionable troubleshooting steps. |
| 13 | Takeoff timeout warning | `state_machine.py:234-238` | VERIFIED | 60s warning with actionable troubleshooting steps. |
| 14 | Centering timeout | `state_machine.py:491-495` | VERIFIED | 60s timeout auto-resumes search. |
| 15 | Verify timeout | `state_machine.py:559-577` | VERIFIED | 120s timeout auto-rejects target, checks queue for next. |
| 16 | Camera loss handling | `main.py:569-588` | VERIFIED | Counts consecutive None frames, warns every 5s, displays "CAMERA LOST" overlay. Recovery logged. |
| 17 | Home position guard | `state_machine.py:707-709` | VERIFIED | If GPS never fixed, lands in place instead of flying to potentially wrong home position. |
| 18 | Detection dedup | `state_machine.py:71-83` `_is_near_known()` | VERIFIED | Skips detections near rejected targets, IOIs, or queued targets within `REJECTED_TARGET_RADIUS_M`. |
| 19 | NFZ/search-area detection filter | `state_machine.py:85-101` | VERIFIED | Ignores detections inside NFZ or outside search polygon. |

---

## CLI Flags

All parsed in `main.py:30-56`.

| # | Flag | Variable | Status | Notes |
|---|------|----------|--------|-------|
| 1 | `--dry-run` | `DRY_RUN` | VERIFIED | Visualizes search pattern, prints waypoints + timing, saves `dry_run_pattern.jpg`. No Cube/GPS needed. |
| 2 | `--headless` | `HEADLESS` | VERIFIED | No `cv2.imshow` windows. Auto-detects on Pi (no `$DISPLAY`). Terminal + browser input only. |
| 3 | `--alt <m>` | `config.TARGET_ALT` | VERIFIED | Overrides search altitude. |
| 4 | `--speed <factor>` | `SIM_SPEED` | VERIFIED | SITL speedup factor (only affects SIMULATION mode via `SIM_SPEEDUP` param). |
| 5 | `--model <path>` | `MODEL_PATH` | VERIFIED | TFLite model path (default `best.tflite`). Passed to `VisionSystem`. |
| 6 | `--smart-detect` | `SMART_DETECT` | VERIFIED | Requires `DETECT_CONFIRM_FRAMES` consecutive confirmed frames before investigating. |
| 7 | `--center-verify` | `CENTER_VERIFY` | VERIFIED | GPS-averages target position for 10s after centering, before VERIFY. |
| 8 | `--no-nfz` | `NO_NFZ` | VERIFIED | Disables SSSI geofence entirely (no `NFZGeofence` created). |
| 9 | `--no-stream` | `STREAM_ENABLED` (inverted) | VERIFIED | Disables MJPEG stream server on port 8090. |
| 10 | `--transit <file>` | `TRANSIT_FILE` | VERIFIED | Transit waypoints JSON path (default `flight_plans/transit.json`). Exits with error if explicitly requested but missing. |
| 11 | `--beacon-delay <s>` | `BEACON_DELAY` | VERIFIED | Auto-triggers PLB focus area redirect after N seconds of search (0 = off). |
| 12 | `--conf <threshold>` | `config.CONFIDENCE_THRESHOLD` | VERIFIED | Overrides AI detection confidence threshold. |
| 13 | `--spiral` | `USE_SPIRAL` | VERIFIED | Uses Zian's perimeter spiral planner instead of lawnmower. Falls back to lawnmower if spiral fails. |
| 14 | `--lock-yaw` | `LOCK_YAW` | VERIFIED | Maintains search yaw heading throughout sweep. Continuous correction every 2s if error > 5 deg. |
| 15 | `--nfz-total-speed` | `NFZ_DIRECTIONAL` (inverted) | VERIFIED | Uses total speed clamping near NFZ instead of directional (default is directional). |

---

## Modes

| # | Mode | Status | Notes |
|---|------|--------|-------|
| 1 | SIMULATION | VERIFIED | `config.MODE == "SIMULATION"`. Uses `SimulationEnvironment` with `map.jpg`, simulated drone camera view, god-view composite display. SITL speedup. |
| 2 | REAL | UNTESTED (field-tested bench only) | `config.MODE == "REAL"`. Pi camera + Cube. Loads search area from `search_area.json` or `config.SEARCH_AREA_GPS`. Never fully flight-tested autonomous. |
| 3 | DRY_RUN | VERIFIED | `--dry-run` flag. No Cube, no GPS, no flying. Pattern visualization + statistics only. Works in both SIM and REAL config. |

---

## Input Handling

Keys processed in `state_machine.py:1049-1077` `_handle_keys()`.

| Key | Action | Active States | Status |
|-----|--------|---------------|--------|
| M | Toggle MANUAL override | Any (except DONE) | VERIFIED |
| Y | Confirm target | VERIFY | VERIFIED |
| N | Reject target | VERIFY + landing side select | VERIFIED |
| I | Mark as Item of Interest | VERIFY | VERIFIED |
| X | False positive rejection | VERIFY | VERIFIED |
| N/E/S/W | Select landing side | VERIFY (selecting_landing_side) | VERIFIED |
| K | Reset rejected targets + IOIs | Any | VERIFIED |
| B | Trigger PLB beacon redirect | SEARCH | VERIFIED |
| W/A/S/D | Move (body frame) | MANUAL | VERIFIED |
| R/F | Climb/descend | MANUAL | VERIFIED |
| Q/E | Yaw left/right | MANUAL | VERIFIED |
| ESC (27) | Quit mission | Any | VERIFIED |

Input sources:
- `cv2.waitKey()` (non-headless)
- Terminal thread (`_terminal_input_thread`, PuTTY/SSH via msvcrt or termios)
- Stream server queue (`stream_cmd_queue` via browser buttons / `/cmd?key=` HTTP endpoint)

---

## Detection Pipeline

| Feature | Location | Status | Notes |
|---------|----------|--------|-------|
| Dual backend (Ultralytics / TFLite) | `vision.py` | VERIFIED | Auto-selects based on platform. NCNN backend also available. |
| SMART detect (consecutive frames) | `state_machine.py:377-407` | VERIFIED | Requires N consecutive frames (`DETECT_CONFIRM_FRAMES`) before queuing. |
| Detection queue | `state_machine.py:103-123` | VERIFIED | FIFO queue with `MAX_DETECT_QUEUE` cap (drops oldest). Validates before popping (NFZ, search area, known targets). |
| Detection during MANUAL | `state_machine.py:1063-1072` | VERIFIED | Detections silently queued during manual flight. Investigated on resume. |
| Detection lock radius | `state_machine.py:500-512` | VERIFIED | During CENTERING, new detections outside `DETECT_LOCK_RADIUS_M` are queued (not replacing current target). |

---

## Telemetry and Logging

| Feature | Location | Status | Notes |
|---------|----------|--------|-------|
| MAVLink telemetry parsing | `main.py:446-482` | VERIFIED | GLOBAL_POSITION_INT, ATTITUDE, HEARTBEAT, GPS_RAW_INT. |
| CSV flight log (~1 Hz) | `main.py:753-758` | VERIFIED | Timestamp, State, Lat, Lon, Alt, Conf to `config.LOG_FILE`. |
| MJPEG stream server | `stream_server.py` via `main.py:710-713` | VERIFIED | Port 8090 with telemetry overlay. Disabled with `--no-stream`. |
| HUD overlay | `main.py:560-698` | VERIFIED | Mode, state, alt, position, speed, target, model name, verify countdown, IOI list, servo animation. |

---

## Additional Features

| Feature | Location | Status | Notes |
|---------|----------|--------|-------|
| KML zone loading | `config.load_kml_zones()` at `main.py:241` | VERIFIED | Loads search area, flight area, SSSI, takeoff from AENGM0074.kml. |
| Lawnmower pattern generation | `planning.py` via `self.planner` | VERIFIED | Altitude-adaptive strip spacing, edge margin, diagonal yaw alignment. |
| Spiral pattern generation | `main.py:67-131` `_generate_spiral_waypoints()` | VERIFIED | Uses Zian's perimeter planner with fallback to standalone reimplementation. |
| Rescan at lower altitude | `state_machine.py:425-447` | VERIFIED | After exhausting waypoints, rescans at `RESCAN_ALT_FACTOR * current_alt`, down to `RESCAN_ALT_FLOOR_M`. Up to `MAX_RESCAN_PASSES`. |
| PLB beacon redirect | `state_machine.py:810-862` | VERIFIED | Loads focus area from `flight_plans/focus_area.json`, replaces search polygon, regenerates waypoints. |
| Payload servo release (2-stage) | `state_machine.py:638-679` | VERIFIED | Stage 1 partial (3s), Stage 2 full (6s), close (15s). Configurable channel + PWM values. |
| Zoom (mouse wheel, SIM only) | `main.py:1000-1003` | VERIFIED | God-view zoom in simulation composite display. |
| Composite SIM view (god + camera) | `main.py:662-677` | VERIFIED | Side-by-side god view (waypoints, polygon, NFZ, IOIs) and camera view. |
| Continuous yaw enforcement | `main.py:807-837` `_enforce_search_yaw()` | VERIFIED | With `--lock-yaw`, corrects yaw every 2s if error > 5 deg. |
| Speed adaptation for altitude | `state_machine.py:457-462` | VERIFIED | `config.speed_for_altitude()` reduces speed at lower altitudes. Focus area uses `FOCUS_SEARCH_SPEED_MPS`. |

---

## Known Gaps / UNTESTED Items

1. **REAL mode full autonomous flight** -- never completed (weather cancelled field day). Bench-tested only.
2. **Payload servo** -- code verified, never tested with actual servo hardware.
3. **Spiral pattern** -- code verified, untested in flight (Zian's planner integration).
4. **Rescan passes** -- code verified, untested in real conditions (relies on config tuning).
5. **PLB beacon redirect** -- code verified in simulation, untested in field.
6. **NCNN backend** -- available in vision.py but not tested via main.py `--model` flag.
7. **`--lock-yaw`** -- code verified, untested in flight (yaw drift correction every 2s).
8. **`--nfz-total-speed`** -- code verified, directional mode is default and better tested.
