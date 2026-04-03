# Pre-Flight Safety Checklist

**Print this document. Follow every checkbox in order. Do not skip steps.**

This is the definitive safety checklist for the SAR drone. It consolidates lessons
from bench testing, field testing, and a colleague's crash (LL-01). Every item here
exists because something went wrong, or because skipping it could cause a crash.

---

## BEFORE LEAVING (Laptop)

```
[ ] 1.  Code pushed to GitHub
        Branch: ________________  Commit: ________________
        git add -A && git commit -m "flight day" && git push

[ ] 2.  Dry-run passes (no GPS, no Cube needed):
        python main.py --dry-run
        Waypoints: ____  Est. flight time: ____ min

[ ] 3.  All unit tests pass:
        python tests/run_all_tests.py
        Result: ____ / ____ passed

[ ] 4.  Model file is the correct one:
        ls -la best.tflite
        Expected: 11.7 MB (sar_v2_1088) or 3.2 MB (original YOLOv8n)
        Actual size: ________

[ ] 5.  Config reviewed for first flight (write down current values):
        TARGET_ALT       = ____ m  (default 35)
        SEARCH_SPEED_MPS = ____ m/s (default 10)
        CONFIDENCE_THRESHOLD = ____ (default 0.2)
        CAMERA_FLIP_180  = ____ (True if camera mounted inverted)

[ ] 6.  SEARCH_AREA_GPS in config.py matches the intended field
        (compare with KML / Google Maps)

[ ] 7.  Batteries charged:
        [ ] Drone LiPo (full = 4.2V per cell, min safe = 3.6V per cell)
        [ ] Pi power source (USB battery pack or drone BEC)
        [ ] RC transmitter batteries
        [ ] Laptop charged

[ ] 8.  Packed:
        [ ] Laptop + charger
        [ ] RC transmitter (correct model selected)
        [ ] Drone with Pi + camera mounted
        [ ] USB cable (Pi debug)
        [ ] Phone (WiFi hotspot)
        [ ] Dummy / casualty prop
        [ ] Measuring tape (for FOV calibration + landing accuracy)
        [ ] This printed checklist + pen
```

---

## AT FIELD (Before Power)

```
[ ] 9.  Props REMOVED for bench testing
        (never apply power with props on until Phase 5)

[ ] 10. RC transmitter powered ON
        [ ] Correct model/profile selected
        [ ] Sticks centred
        [ ] Kill switch in STABILIZE position (safe default)

[ ] 11. Pi and laptop on same network
        Method: phone hotspot / Pi hotspot / field WiFi
        Pi IP: ________________

[ ] 12. SSH into Pi, pull latest code:
        cd ~/dima/Group_Proj && git pull
        source pienv/bin/activate  (or ncnn_env)

[ ] 13. Verify model on Pi matches laptop:
        ls -la best.tflite
        Size: ________  (must match step 4)
```

---

## BENCH TEST (No Props -- Mandatory)

### Start Services

```
[ ] 14. Start mavproxy on Pi (Terminal 1 -- always first):
        sudo /opt/mavlink/mavlink-venv/bin/mavproxy.py \
          --master=/dev/ttyAMA0 --baudrate=921600 --streamrate=10 \
          --out=udpout:127.0.0.1:14550 --out=tcpin:0.0.0.0:5762

[ ] 15. Connect Mission Planner on laptop:
        TCP -> PI_IP -> port 5762
        [ ] Map shows drone position
        [ ] Telemetry bar visible at bottom
```

### Verify Components

```
[ ] 16. Camera working:
        python passive_watch.py --headless
        Open http://PI_IP:8090 in browser
        [ ] Video stream visible
        Ctrl+C to stop

[ ] 17. Cube heartbeat received:
        python tests/laptop/test_cube.py
        [ ] "Heartbeat received" printed
        [ ] System ID shown

[ ] 18. GPS satellites:
        python tests/hardware/gps_test.py
        fix_type: ____  (need 3 = 3D fix)
        Satellites: ____  (need >= 6, prefer >= 8)
        [ ] Here 3+ LED flashing GREEN (not blue)

        If no GPS lock after 15 min:
        - Move to open area (away from buildings/trees)
        - Power cycle for cold start
        - Check Here 3+ LED: blue=searching, green=locked
```

### Verify Safety Systems

```
[ ] 19. DISARM_DELAY = 0 in Mission Planner:
        Config -> Full Parameter List -> DISARM_DELAY
        [ ] Set to 0 (prevents auto-disarm before takeoff)
        See LL-06: default of 10 causes auto-disarm during startup

[ ] 20. RC failsafe configured:
        Mission Planner -> Config -> Failsafe
        [ ] Radio failsafe = RTL (drone comes home if RC signal lost)
        [ ] GCS failsafe = RTL (drone comes home if Pi script crashes)
        [ ] Battery failsafe = RTL (set voltage threshold)

[ ] 21. RC override test WITH a script running:
        Start: python tests/flight/0a_cube_commands.py
        [ ] Flip RC to STABILIZE -> Mission Planner shows STABILIZE
        [ ] Script prints "RC OVERRIDE ACTIVE, commands paused"
        [ ] Flip back -> script can send commands again
        [ ] Ctrl+C to stop script

        This proves RC ALWAYS overrides Python. If this fails, DO NOT FLY.
```

---

## CRITICAL SAFETY LESSON: GUIDED vs LOITER Mode-Fighting

> **A colleague's drone crashed** because their software sent SET_MODE(GUIDED) every
> loop iteration while the pilot's RC was set to LOITER. ArduCopter oscillated between
> modes dozens of times per second. Neither mode ran long enough to maintain stable
> flight. The drone fell out of the sky.

**How our code prevents this (LL-01):**

Our main loop checks `self._cube_mode` from every HEARTBEAT before sending any command:

```python
# main.py line ~760
_pilot_override = self._cube_mode not in (4, 9)  # 4=GUIDED, 9=LAND
if _pilot_override:
    continue  # Send ZERO commands -- pilot is flying
```

When the pilot switches away from GUIDED, our code:
- Sends ZERO MAVLink commands (no mode changes, no velocity, no position targets)
- Skips keyboard/button handlers
- Skips geofence enforcement
- Prints a warning to terminal

**Verification on bench (step 21 above) proves this works before every flight.**

---

## BEFORE FLIGHT (Props On)

```
[ ] 22. All bench tests above PASSED (steps 14-21)

[ ] 23. Props installed and secured
        [ ] All prop nuts tight
        [ ] Correct rotation direction (CW/CCW matched to motors)

[ ] 24. Kill switch final test:
        [ ] RC in STABILIZE -- this is the kill switch position
        [ ] Flip to GUIDED (or AUTO) -- mode changes in Mission Planner
        [ ] Flip back to STABILIZE -- mode returns immediately
        The pilot's thumb stays near this switch for the entire flight.

[ ] 25. Area clear:
        [ ] No people within 30m of takeoff point
        [ ] No obstacles in flight path (trees, power lines, buildings)
        [ ] Dummy placed at known GPS: ____, ____

[ ] 26. Wind check:
        Estimated wind: ____ mph
        [ ] Below 15 mph (safe for flight)
        [ ] Below 10 mph (preferred for first test)

[ ] 27. Roles assigned:
        RC Pilot: ________________ (hands on RC at all times)
        Spotter: ________________  (eyes on drone, calls hazards)
        Dashboard: ______________  (runs Pi script, monitors stream)

[ ] 28. Flight mode plan:
        Start in STABILIZE (RC pilot has full control)
        Switch to GUIDED only when airborne and stable
        Kill switch = STABILIZE at any time
```

---

## DURING FLIGHT

```
[ ] 29. RC pilot has override at all times
        [ ] Thumb near kill switch (STABILIZE)
        [ ] Eyes on drone (not on screen)

[ ] 30. Spotter watching:
        [ ] Drone visible at all times
        [ ] Calls "KILL" if drone behaves unexpectedly
        [ ] Watches for other aircraft, people entering area

[ ] 31. Dashboard operator monitoring:
        [ ] Pi terminal visible (for error messages)
        [ ] Browser stream at http://PI_IP:8090
        [ ] Watching for "RC OVERRIDE" warnings

[ ] 32. Communication protocol:
        "TAKING OFF" -- pilot announces before arming
        "AIRBORNE"   -- pilot confirms stable hover
        "SWITCHING"  -- pilot announces before GUIDED mode
        "KILL KILL"  -- anyone can call, pilot flips to STABILIZE immediately
        "LANDING"    -- pilot announces before landing
```

---

## EMERGENCY PROCEDURES

### Kill Switch (Primary -- Always Available)

```
RC mode switch -> STABILIZE

This immediately:
- Gives full manual control to the RC pilot
- Our code detects mode != GUIDED and sends ZERO commands
- Pilot can fly manually, hover, or land
```

### Script Crash / Pi Failure

```
If the Python script crashes or the Pi loses power:
1. ArduCopter GCS failsafe triggers -> RTL (return to launch)
   (only if FS_GCS_ENABLE is set -- verify in step 20)
2. If RTL doesn't activate, pilot switches to STABILIZE and lands manually
3. The Cube flies independently of the Pi -- it never depends on Pi for stability
```

### RC Signal Lost

```
If RC transmitter loses connection:
1. ArduCopter RC failsafe triggers -> RTL (configured in step 20)
2. Drone climbs to RTL_ALT, flies home, lands at takeoff point
3. DO NOT chase the drone -- wait at the launch point
```

### Drone Not Responding to RC

```
1. Check RC transmitter is still bound (LED status)
2. Check battery voltage -- low voltage causes erratic behaviour
3. If drone is flying away: it is likely in RTL -- wait at launch point
4. If drone is descending uncontrolled: clear the area, do not attempt to catch
```

### Emergency RTL from Software

```
Our code triggers emergency RTL on:
- Link lost for > 30 seconds
- GPS fix lost during autonomous flight
- Geofence violation (inside SSSI NFZ)

The terminal prints:
  "EMERGENCY: Attempting RTL — <reason>"
  "If RTL fails, ArduCopter GCS failsafe should trigger RTL"
  "RC kill switch is always available"
```

---

## POST-FLIGHT

```
[ ] 33. Drone landed and disarmed
[ ] 34. Props removed before handling
[ ] 35. Battery disconnected
[ ] 36. Record results:

        Max detection altitude: ____ m
        Max detection speed:    ____ m/s
        Avg confidence:         ____
        Inference FPS on Pi:    ____
        False positives seen:   ____
        Landing distance from dummy: ____ m
        GPS estimate error:     ____ m

[ ] 37. Config updates needed:
        TARGET_ALT =          ____ (lower if no detection at current alt)
        SEARCH_SPEED_MPS =    ____ (lower if detections missed at speed)
        CONFIDENCE_THRESHOLD = ____ (lower if too few detections, raise if too many FPs)
        FOCAL_LENGTH_MM =     ____ (update if FOV calibration done)

[ ] 38. Commit results:
        git add -A && git commit -m "flight results" && git push
```

---

## QUICK REFERENCE CARD (tear off and keep in pocket)

```
KILL SWITCH:     RC -> STABILIZE (always works, always available)
SCRIPT CRASH:    GCS failsafe -> RTL (automatic)
RC LOST:         RC failsafe -> RTL (automatic)
PI IP:           ________________
STREAM:          http://PI_IP:8090
MISSION PLANNER: TCP -> PI_IP -> 5762

MAVPROXY:
  sudo /opt/mavlink/mavlink-venv/bin/mavproxy.py \
    --master=/dev/ttyAMA0 --baudrate=921600 --streamrate=10 \
    --out=udpout:127.0.0.1:14550 --out=tcpin:0.0.0.0:5762

DASHBOARD KEYS:
  N = investigate    Y = confirm    I = interest
  X = false positive L = land       M = manual

MODE NUMBERS:
  0 = STABILIZE    4 = GUIDED    9 = LAND    6 = RTL
```

---

*Last updated: 2026-04-03. Based on lessons LL-01 through LL-08 in docs/LESSONS_LEARNED.md.*
