# SITL vs Real Drone — What Still Needs Confirming

Everything works in SITL simulation. This document lists what HASN'T been confirmed on the real drone yet and what tests to run.

---

## CONFIRMED WORKING (tested on real hardware)

| Item | When tested | Result |
|---|---|---|
| Pi camera captures frames | Flight day 1+2 | 1456x1088, IMX296, working |
| TFLite model loads on Pi | Flight day 1+2 | 5.2 FPS original, 3.1 FPS v2-1088 |
| NCNN model loads on Pi | Lab session | 13.8 FPS inference, 9 FPS pipeline |
| Cube heartbeat via mavproxy | Flight day 1+2 | Connected, telemetry flowing |
| GPS 1 lock | Flight day 2 | 13 sats, 3D fix, 0.8 HDOP |
| Battery reading | Flight day 2 | 16.1V, 95% |
| Passive watch stream | Flight day 2 | MJPEG at 4.5 FPS |
| Diagnostics dashboard | Flight day 2 | All views working |
| Model swap (M key) | Flight day 2 | Switches between models |
| Lens calibration | Flight day 1 | RMS 0.399, undistortion working |

---

## NOT YET CONFIRMED — Must Test Before Real Flight

### Priority 1: CRITICAL (flight won't work without these)

| # | Item | Risk | How to test | Notes |
|---|---|---|---|---|
| 1 | **Arming in GUIDED mode** | HIGH | `tests/flight/0a_cube_commands.py` | Blocked by GPS 2 issue — needs `param set GPS_TYPE2 0` |
| 2 | **Takeoff command** | HIGH | `tests/flight/0b_bench_mission.py` (no props) | Does MAV_CMD_NAV_TAKEOFF work? Does it climb? |
| 3 | **GUIDED waypoint navigation** | HIGH | `tests/flight/2_waypoints.py` | Does SET_POSITION_TARGET_GLOBAL_INT move the drone? |
| 4 | **Landing command** | HIGH | Watch for MAV_CMD_NAV_LAND response | SITL accepts it — does real Cube? |
| 5 | **GPS 2 parameter** | HIGH | In mavproxy: `param set GPS_TYPE2 0` then `reboot` | If GPS 2 not connected, this blocks all arming |
| 6 | **RC override / kill switch** | CRITICAL | Toggle RC switch to STABILIZE during GUIDED | Safety critical — must work instantly |

### Priority 2: HIGH (mission won't complete without these)

| # | Item | Risk | How to test | Notes |
|---|---|---|---|---|
| 7 | **Servo release — correct channel** | HIGH | `tests/flight/0a_cube_commands.py` + listen for servo click | Currently hardcoded channel 9, PWM 1100 |
| 8 | **Servo two-level release** | HIGH | Test both PWM values | We only send one value (1100). What's level 1 vs level 2? |
| 9 | **Servo PWM values** | HIGH | Check Mission Planner servo tab | What PWM = closed? What PWM = level 1? What PWM = level 2? |
| 10 | **Speed command works** | MEDIUM | Observe drone speed during waypoint test | MAV_CMD_DO_CHANGE_SPEED — does it actually change speed? |
| 11 | **Mode change from GUIDED to RTL** | MEDIUM | Trigger RTL in test | Does `set_mode('RTL')` work? |
| 12 | **Mode change from GUIDED to LAND** | MEDIUM | Trigger LAND in test | Does `set_mode('LAND')` work? |

### Priority 3: MEDIUM (affects quality but not safety)

| # | Item | Risk | How to test | Notes |
|---|---|---|---|---|
| 13 | **Camera image quality at altitude** | MEDIUM | Passive watch during manual flight | Do we actually detect dummy from 30-50m in real conditions? |
| 14 | **GPS estimation accuracy** | MEDIUM | Compare estimated GPS vs known dummy position | Is GSD calculation correct for real camera at real altitude? |
| 15 | **FOV calibration in flight** | MEDIUM | Use `fov_calibrate_video.py` on real flight video | Was the 54.4° HFOV correct? Or was that DJI-specific? |
| 16 | **Pi camera FOV vs DJI FOV** | MEDIUM | Compare detection at same altitude | IMX296 has different FOV than DJI — GSD calculations may differ |
| 17 | **Detection at different sun angles** | LOW | Test morning, midday, afternoon | Shadows and glare could affect detection |
| 18 | **Wind effect on hovering** | LOW | Observe centering stability | Can it hold position over target in wind? |
| 19 | **Vibration effect on camera** | LOW | Check frame quality during flight | Motor vibration might blur frames despite global shutter |

---

## SERVO RELEASE — Detailed Questions

Current code (state_machine.py line 456-460):
```python
# MAV_CMD_DO_SET_SERVO: servo channel 9, PWM 1100 (open)
self.master.mav.command_long_send(
    self.master.target_system, self.master.target_component,
    mavutil.mavlink.MAV_CMD_DO_SET_SERVO, 0,
    9, 1100, 0, 0, 0, 0, 0)
```

### Questions to answer:
1. **What channel is the servo on?** Check in Mission Planner → Servo/Relay tab
2. **What is the closed (locked) PWM?** Typically 1500 (neutral) or 1900
3. **What is level 1 release PWM?**
4. **What is level 2 release PWM?**
5. **Do we need to send level 1 first, wait, then level 2?**
6. **Can we test servo on bench?** `tests/flight/0a_cube_commands.py` sends a servo command

### How to find servo mapping:
In Mission Planner connected to Cube:
1. Go to **CONFIG → Servo/Relay** tab
2. Check which output (SERVO1_FUNCTION through SERVO16_FUNCTION) is set to a release function
3. Note the channel number and min/max PWM values
4. Or in mavproxy: `param show SERVO9_FUNCTION` (check our assumed channel 9)

---

## THINGS THAT MIGHT BEHAVE DIFFERENTLY IN REAL FLIGHT

### 1. GPS Drift During Centering
- SITL: GPS is perfect, centering converges quickly
- Real: GPS drifts 2-3m, centering might oscillate
- **Mitigation:** GPS estimation uses inverse-variance weighting, should average out
- **Test:** observe centering behaviour in passive watch during manual flight

### 2. Altitude Hold Accuracy
- SITL: holds exact altitude
- Real: barometer + GPS altitude can drift ±1-2m
- **Impact:** detection confidence varies with altitude (±2m = ±5% confidence at 50m)
- **Test:** check altimeter reading during hover, compare to expected

### 3. Yaw Accuracy
- SITL: perfect yaw reading
- Real: magnetometer can be off by 5-10° near metal structures
- **Impact:** GPS estimation of target position shifts by ~5m at 50m altitude
- **Mitigation:** multiple observations average out yaw error

### 4. Communication Latency
- SITL: localhost, ~0ms latency
- Real: mavproxy UDP bridge, ~5-10ms latency
- **Impact:** should be negligible for 3 FPS detection loop
- **But:** if mavproxy drops packets, telemetry gaps could cause state machine issues

### 5. Camera Exposure in Sunlight
- SITL/Lab: fixed simulated/indoor lighting
- Real: auto-exposure adjusts to sun — could be very short (1-2ms) or have glare
- **Impact:** very short exposure = sharper images (good!), but sun glare could blank the frame
- **Test:** passive watch in various sun conditions

### 6. Takeoff and Approach Behaviour
- SITL: instant mode changes, smooth transitions
- Real: mode changes take 0.5-1s, motors spool up gradually
- **Impact:** our timeout logic might be too aggressive
- **Test:** bench mission test (0b) with no props, verify state transitions

---

## PRE-FLIGHT TEST SEQUENCE (do these in order)

Each step builds confidence. **Never skip a step.**

```
Step 0: Fix GPS_TYPE2 (mavproxy: param set GPS_TYPE2 0, reboot)
Step 1: 0a_cube_commands.py — verify Pi→Cube commands work
Step 2: Check servo channel/PWM in Mission Planner
Step 3: 0b_bench_mission.py — full command sequence, no props
Step 4: Manual RC flight (pilot), passive_watch.py running
Step 5: 2_waypoints.py — autonomous waypoint flight (no CV)
Step 6: main.py with --no-descend — full mission, verify at altitude
Step 7: main.py full mission — search, detect, descend, verify, land
```

---

## KNOWN BLOCKERS FROM FLIGHT DAY 2

| Blocker | Status | Fix |
|---|---|---|
| GPS 2 still configuring | NOT FIXED | `param set GPS_TYPE2 0` in mavproxy |
| Drone didn't take off | UNKNOWN CAUSE | Could be GPS2, could be motor/ESC issue |
| Servo mapping unknown | NOT CONFIRMED | Check Mission Planner servo tab |
| Battery was at 40% by end | OK for now | Full charge before next flight |
