# Contingency Table -- Flight Day Safety Bible

> For every state in the state machine: what happens if something goes wrong?
>
> **Legend**: "Handled" = code deals with it. "NOT HANDLED" = risk exists, operator must intervene.
>
> **Universal safety nets** (apply to ALL states):
> - **RC kill switch**: Pilot can switch to STABILIZE/LOITER on RC transmitter at any time. This overrides everything.
> - **ArduCopter GCS failsafe** (`FS_GCS_ENABLE`): If heartbeat link drops for >5s, ArduCopter auto-RTLs.
> - **ArduCopter RC failsafe** (`FS_THR_ENABLE`): If RC signal lost, ArduCopter auto-RTLs.
> - **ESC key / Ctrl+C**: Triggers `_emergency_rtl()` then exits script.

---

## State Contingency Matrix

| State | Timeout | M key (manual override) | GPS loss | Camera fail | Connection drop | Notes |
|-------|---------|-------------------------|----------|-------------|-----------------|-------|
| **INIT** | Handled: retries connection every 1s, prints error on failure. No timeout limit -- will retry forever. | NOT HANDLED: M key does nothing (no mavlink connection yet). No risk -- drone is on ground. | N/A: drone is on ground, GPS not yet required. | N/A: camera initialized but not critical here. | Handled: try/except on `mavlink_connection()`, prints error and retries. | Safe state. Drone is on the ground. Operator can Ctrl+C. |
| **CONNECTING** | Handled: prints "No heartbeat" warning every 15s. No hard timeout -- waits indefinitely. | NOT HANDLED: M key ignored (no nav controller yet). No risk -- drone is on ground. | N/A: drone is on ground. | N/A: camera active but not used for decisions. | Handled: if heartbeat never arrives, stays in this state. ArduCopter is not armed. | Safe state. Drone is on the ground. Kill mavproxy and restart if stuck. |
| **ARMING** | Handled: 120s timeout prints detailed warning (GPS, safety switch, RC failsafe causes). Does NOT auto-abort -- keeps retrying. | NOT HANDLED: M key code runs but `self.nav` may be None (just created). Low risk -- drone is on ground, not armed yet. | Handled: waits for GPS fix (fix>=3, sats>=6) before attempting arm. Prints status every 5s. Will not arm without GPS. | N/A: camera active but not used for decisions. | Handled: if connection lost, arm commands fail silently. Drone stays disarmed on ground. | Safe state. Drone is on the ground. Worst case: operator waits, then Ctrl+C. |
| **TAKEOFF** | Handled: 60s timeout prints warning (propellers, GPS, obstructions). Does NOT auto-abort -- keeps waiting. | Handled: M key saves departure point, switches to MANUAL. **Risk**: drone is mid-climb, MANUAL mode requires WASD input to maintain altitude. Operator must actively fly. | Handled: `_check_gps_degradation()` runs. 5s of degraded GPS triggers emergency RTL. | NOT HANDLED: camera returns None, logged as "flying blind" but takeoff continues. Acceptable -- takeoff does not use camera. | Handled: `update_telemetry()` catches connection errors, triggers `_emergency_rtl()`, sets state to DONE. | REAL mode: if drone disarms during takeoff, goes to DONE (safety stop). SIM mode: retries arming. |
| **PRE_WAYPOINTS** | NOT HANDLED: no timeout. If drone cannot reach a transit waypoint (wind, GPS drift), it will fly toward it indefinitely. | Handled: M key saves departure point and previous state. Resume via RETURN_FROM_MANUAL returns to this state. | Handled: GPS degradation monitor active. 5s degraded = emergency RTL. | NOT HANDLED: camera returns None, logged as warning. Transit does not need camera, but detection queue still runs. Low risk. | Handled: `_emergency_rtl()` on connection loss. | Operator should monitor transit progress. If stuck, press M then manually navigate, or Ctrl+C for RTL. |
| **TRANSIT_TO_SEARCH** | NOT HANDLED: no timeout. Same risk as PRE_WAYPOINTS -- will fly toward first search waypoint indefinitely. | Handled: M key works. Resume returns to this state. | Handled: GPS degradation monitor active. 5s = emergency RTL. | NOT HANDLED: same as PRE_WAYPOINTS. Low risk -- transit does not use camera for decisions. | Handled: `_emergency_rtl()` on connection loss. | If stuck, press M or Ctrl+C. |
| **SEARCH** | Handled: when all waypoints exhausted, starts rescan at lower altitude. After `MAX_RESCAN_PASSES` or reaching `RESCAN_ALT_FLOOR_M`, transitions to DONE. Will NOT fly forever. | Handled: M key saves departure point, queues any current detection. Resume pops queued targets or returns to search via RETURN_FROM_MANUAL. | Handled: GPS degradation monitor active. 5s = emergency RTL. | NOT HANDLED: camera returns None, detection stops working. Drone completes search pattern with zero detections. Wastes time but safe. | Handled: `_emergency_rtl()` on connection loss. | Core search state. Geofence active -- NFZ proximity slows drone, entering NFZ forces MANUAL. |
| **CENTERING** | Handled: 60s timeout prints warning and auto-returns to SEARCH. Target may have moved or GPS estimate was inaccurate. | Handled: M key saves departure point. Resume returns to CENTERING (or RETURN_FROM_MANUAL if far). | Handled: GPS degradation monitor active. 5s = emergency RTL. Also: centering uses GPS to navigate, so degraded GPS makes centering inaccurate but not dangerous. | NOT HANDLED: camera returns None, but centering uses GPS target (not live vision) to navigate. Detection updates stop, but drone still flies to last known target GPS. Acceptable. | Handled: `_emergency_rtl()` on connection loss. | If centering is inaccurate, 60s timeout catches it and resumes search. |
| **DESCENDING** | Handled: immediately transitions to VERIFY (no-descend mode). Cannot get stuck. | N/A: state transitions instantly. | N/A: state transitions instantly. | N/A: state transitions instantly. | N/A: state transitions instantly. | Currently a pass-through state. If descent logic is re-enabled, needs its own timeout. |
| **VERIFY** | Handled: 120s timeout. If operator does not press Y/N/I within 120s, target is auto-rejected and drone resumes search. | Handled: M key saves departure point. Resume returns to VERIFY. Operator can still confirm/reject after resuming. | Handled: GPS degradation monitor active. 5s = emergency RTL. Drone hovers at target GPS during verify. | NOT HANDLED: camera returns None. Operator sees "CAMERA LOST" on HUD/stream but cannot visually verify target. **Risk**: operator may confirm blind. Mitigation: operator should press N if camera is dead. | Handled: `_emergency_rtl()` on connection loss. | **Critical decision point.** Operator MUST respond Y/N/I. Timeout defaults to reject (safe). GPS averaging runs for 10s after Y press. |
| **HOVER** | Handled: 60s timeout. Prints "stuck in HOVER with no waypoints" and transitions to DONE. | Handled: M key works. But HOVER means no waypoints exist -- resuming HOVER will just timeout again. | Handled: GPS degradation monitor active. 5s = emergency RTL. | NOT HANDLED: low risk -- HOVER is a fallback state, camera not critical. | Handled: `_emergency_rtl()` on connection loss. | HOVER is an error recovery state (no waypoints generated). Should not occur in normal operation. |
| **APPROACH** | NOT HANDLED: no explicit timeout. Drone flies to landing spot at 3m altitude. If it cannot reach (wind, GPS), it flies indefinitely. | Handled: M key saves departure point. Resume returns to APPROACH. | Handled: GPS degradation monitor active. 5s = emergency RTL. **Risk**: at 3m altitude, RTL climb may be aggressive. | NOT HANDLED: camera returns None. Approach uses GPS only (not vision), so camera failure does not affect navigation. Low risk. | Handled: `_emergency_rtl()` on connection loss. | Low altitude (3m). Operator should be especially vigilant. Press M if anything looks wrong. |
| **HOVER_TARGET** | Handled: 15s timed sequence (hover, servo stage 1, servo stage 2, depart). Auto-transitions to RETURN_TRANSIT or RETURN_HOME after 15s. Cannot get stuck. | Handled: M key works. **Risk**: if pressed mid-servo-release, payload drop may be incomplete. Servo returns to closed position only on normal completion (elapsed > 15s). | Handled: GPS degradation monitor active. 5s = emergency RTL. Drone hovers at landing GPS. | NOT HANDLED: camera returns None. Not critical -- hover uses GPS position hold. | Handled: `_emergency_rtl()` on connection loss. **Risk**: payload may be mid-release when RTL triggers. | Servo sequence: 3s hover, 3-6s stage 1 (partial), 6-15s stage 2 (full). If interrupted, servo state may be inconsistent. |
| **RETURN_TO_SEARCH** | NOT HANDLED: no explicit timeout. Flies to departure point. If unreachable, flies indefinitely. | Handled: M key works. Resume returns to RETURN_TO_SEARCH. | Handled: GPS degradation monitor active. 5s = emergency RTL. | NOT HANDLED: camera returns None. Low risk -- uses GPS navigation only. | Handled: `_emergency_rtl()` on connection loss. | Requires both horizontal proximity (<3m) AND altitude (>85% search alt) to transition. |
| **RETURN_FROM_MANUAL** | NOT HANDLED: no explicit timeout. Flies back to manual departure point. If unreachable, flies indefinitely. | Handled: M key re-enters MANUAL (does not save new departure -- uses existing one). Pressing M again resumes return. | Handled: GPS degradation monitor active. 5s = emergency RTL. | NOT HANDLED: camera returns None. Low risk -- GPS navigation only. | Handled: `_emergency_rtl()` on connection loss. | Triggers when operator exits MANUAL mode >5m from departure point. Drone flies back before resuming previous state. |
| **RETURN_TRANSIT** | NOT HANDLED: no explicit timeout. Retraces pre-waypoints in reverse. If a waypoint is unreachable, stuck. | Handled: M key works. Resume returns to RETURN_TRANSIT. | Handled: GPS degradation monitor active. 5s = emergency RTL. | NOT HANDLED: camera returns None. Low risk -- GPS navigation only. | Handled: `_emergency_rtl()` on connection loss. | First climbs to search altitude before traversing transit waypoints. |
| **RETURN_HOME** | NOT HANDLED: no explicit timeout. Flies to home_lat/home_lon at TARGET_ALT. If unreachable, flies indefinitely. | Handled: M key works. Resume returns to RETURN_HOME. | Handled: GPS degradation monitor active. 5s = emergency RTL. **Also**: if `gps_fix_ok` was never set, skips return and lands in place immediately. | NOT HANDLED: camera returns None. Low risk -- GPS navigation only. | Handled: `_emergency_rtl()` on connection loss. | If GPS never fixed (gps_fix_ok=False), lands in place instead of flying to potentially wrong home position. Good safety check. |
| **LANDING** | Handled: 90s absolute timeout. Force-disarms after 90s (covers baro-drift deadlock). Also retries LAND command 5 times if not descending, then force-disarms. | NOT HANDLED: M key runs `_handle_manual_toggle()` but **should not be used during landing**. Risk: entering MANUAL at low altitude during powered descent is dangerous. | Handled: GPS degradation monitor is NOT active in LANDING state (excluded). ArduCopter LAND mode uses barometer, not GPS, for final descent. Acceptable. | NOT HANDLED: camera returns None. Not critical -- landing uses barometer/accelerometer. | Handled: `_emergency_rtl()` on connection loss. ArduCopter's own landing logic continues even if script crashes. | Multiple touchdown detection methods: (1) ArduPilot auto-disarm (accelerometer), (2) altitude threshold (0.5m for 5 ticks), (3) 90s force-disarm, (4) 5-retry force-disarm. Very robust. |
| **MANUAL** | NOT HANDLED: no timeout. Drone hovers until operator presses M to resume or Ctrl+C for RTL. If operator walks away, drone hovers until battery failsafe. | Handled: M key exits MANUAL. If >5m from departure, goes to RETURN_FROM_MANUAL. If <5m, resumes previous state directly. Also checks for target detection on exit. | Handled: GPS degradation monitor is NOT active in MANUAL state (excluded). ArduCopter maintains GUIDED mode position hold using GPS. If GPS fails, ArduCopter's own GPS failsafe triggers. | NOT HANDLED: camera returns None but detections are still queued during MANUAL. If camera fails, no detections queued. Low risk -- operator is manually flying. | Handled: `_emergency_rtl()` on connection loss. | Operator has full WASD control. Detection queue continues in background. Geofence NOT enforced in MANUAL (excluded from `_enforce_geofence`). |
| **DONE** | N/A: terminal state. Waits 3s then exits. | N/A: terminal state, no dispatch handler. | N/A: drone is on ground (or should be). | N/A: terminal state. | N/A: terminal state. | Displays final landing error distance. Log file closed in `finally` block. |

---

## Summary of Unhandled Risks

### HIGH priority (fix before flight)

| Risk | States affected | Mitigation |
|------|----------------|------------|
| **No timeout on transit/return states** | PRE_WAYPOINTS, TRANSIT_TO_SEARCH, RETURN_TO_SEARCH, RETURN_FROM_MANUAL, RETURN_TRANSIT, RETURN_HOME, APPROACH | Drone flies toward unreachable waypoint indefinitely. Battery failsafe is the only backstop. **Operator must watch and press M or Ctrl+C if drone appears stuck.** Consider adding a 5-minute global transit timeout. |
| **M key during LANDING is dangerous** | LANDING | Entering MANUAL at low altitude during powered descent risks crash. Consider ignoring M key in LANDING state. |
| **No timeout in MANUAL** | MANUAL | If operator forgets, drone hovers until battery dies. Battery failsafe (FS_BATT) is the backstop. Consider adding a 5-minute warning beep. |

### MEDIUM priority (acceptable for first flights)

| Risk | States affected | Mitigation |
|------|----------------|------------|
| **Camera fail during VERIFY** | VERIFY | Operator sees "CAMERA LOST" on HUD but may confirm blind. **Operator rule: always press N if camera feed is dead.** |
| **Servo state on interrupt** | HOVER_TARGET | If M key or connection drop interrupts servo sequence, servo may be left in partial-release position. On next power cycle, servo returns to default. Consider sending SERVO_CLOSED on any state exit from HOVER_TARGET. |
| **Geofence not active in MANUAL** | MANUAL | Operator can fly into NFZ while in MANUAL mode. **Operator rule: do not fly into SSSI zone.** |
| **ARMING/CONNECTING never timeout** | INIT, CONNECTING, ARMING | Operator waits forever. Not dangerous (drone on ground) but annoying. Ctrl+C to exit. |

### LOW priority (safe by design)

| Risk | States affected | Mitigation |
|------|----------------|------------|
| Camera fail during transit states | PRE_WAYPOINTS, TRANSIT_TO_SEARCH, RETURN_TO_SEARCH, RETURN_TRANSIT, RETURN_HOME | These states use GPS navigation only. Camera failure is logged but has no effect on flight safety. |
| Camera fail during SEARCH | SEARCH | Drone completes pattern with zero detections. Wastes battery but is safe. |
| Camera fail during TAKEOFF | TAKEOFF | Takeoff is altitude-based, not vision-based. Camera failure has no effect. |

---

## Operator Quick Reference

**If the drone looks stuck**: Press M (manual), fly it to safety, press M again to resume.

**If camera feed dies**: Press N to reject any pending verification. Continue mission (search still flies pattern).

**If GPS warning appears**: You have 5 seconds before emergency RTL triggers automatically. Watch the drone.

**If connection drops**: Script sends RTL command. ArduCopter GCS failsafe is the backup. RC kill switch is the final backup.

**If you need to abort immediately**:
1. RC switch to STABILIZE (takes over instantly)
2. Or Ctrl+C in terminal (sends RTL then exits)
3. Or ESC key (sends RTL then exits)

**During LANDING -- DO NOT press M.** Let the landing sequence complete. It has a 90s timeout with force-disarm as ultimate safety net.

**During HOVER_TARGET -- be careful with M.** Servo release sequence may be interrupted. If you must interrupt, the servo will reset on next power cycle.
