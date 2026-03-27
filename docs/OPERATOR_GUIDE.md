# SAR Drone Operator Guide

> Practical step-by-step guide for operating an autonomous SAR mission.
> This is NOT a technical reference -- it tells you what to look at, what to press, and when to worry.

---

## Quick Reference Card

| Key | When | What it does |
|-----|------|-------------|
| **Y** | VERIFY prompt | Confirm target -- proceed to landing sequence |
| **N** | VERIFY prompt | Reject target -- resume search |
| **I** | VERIFY prompt | Mark as Item of Interest -- log position, resume search |
| **N/E/S/W** | After Y confirm | Select which side to land (relative to target) |
| **M** | Any time | Toggle manual override / resume automation |
| **K** | Any time | Clear all rejected targets and IOIs (re-enable all areas) |
| **B** | During SEARCH | Simulate PLB beacon signal (redirect to Focus Area) |
| **Esc** | Any time | Abort mission (triggers emergency RTL) |

---

## Phase 1: Pre-Flight on Laptop (Before Leaving)

### 1.1 Verify Search Pattern (5 min)

Run from the project directory with test_env activated:

```
python main.py --dry-run
```

This generates and displays the lawnmower search pattern without connecting to
anything. Check:

- [ ] Correct number of waypoints printed
- [ ] Pattern covers the entire search polygon (opens map visualization)
- [ ] Estimated flight time is reasonable (printed in terminal)
- [ ] `dry_run_pattern.jpg` saved for reference

If the pattern looks wrong, check `flight_plans/AENGM0074.kml` and `config.py`
SEARCH_AREA_GPS values.

### 1.2 Verify Model

```
python main.py --dry-run --model cv_models/sar_v2_1088/best.tflite
```

Confirms the model file exists and loads without error.

### 1.3 Pack Checklist

- [ ] Laptop with test_env venv (for field monitoring via Mission Planner)
- [ ] Pi fully charged, SD card inserted
- [ ] Cube Orange connected to Pi via serial (check cable)
- [ ] Correct `best.tflite` on Pi (should be `cv_models/sar_v2_1088/best.tflite`)
- [ ] RC transmitter charged, kill switch channel configured
- [ ] Printed copy of this guide (or phone with this page open)
- [ ] Safety officer briefed on kill switch procedure

---

## Phase 2: Field Setup (At the Site)

### 2.1 Hardware Assembly

1. Mount Pi on drone frame, connect serial cable to Cube (Telem2, 921600 baud)
2. Connect Pi camera ribbon cable -- check lens is clean
3. Power on Cube, wait for boot tone
4. Power on Pi (USB-C power)

### 2.2 Pi Terminal Setup (3 terminals needed)

**Terminal 1 -- mavproxy bridge (start first, leave running):**
```
sudo /opt/mavlink/mavlink-venv/bin/mavproxy.py \
  --master=/dev/ttyAMA0 --baudrate=921600 --streamrate=10 \
  --out=udpout:127.0.0.1:14550 \
  --out=udpout:127.0.0.1:14551 \
  --out=tcpin:0.0.0.0:5762
```

Wait for `APM: ArduCopter V4.x.x` and `Flight battery X percent` messages.

**Terminal 2 -- diagnostics (optional, for monitoring):**
```
cd ~/sar-drone && source pienv/bin/activate
python tests/diagnostics/cube_monitor.py
```

Verify: heartbeat present, GPS fix >= 3D, satellites >= 6.

**Terminal 3 -- mission script (start when ready):**
```
cd ~/sar-drone && source pienv/bin/activate
python main.py --headless
```

### 2.3 Mission Planner on Laptop

1. Connect to Pi via TCP: `PI_IP:5762` (e.g., `192.168.1.3:5762`)
2. Verify on the HUD: GPS fix, satellite count, battery voltage
3. Check the Messages tab for any pre-arm warnings
4. Keep Mission Planner open throughout the flight for backup monitoring

### 2.4 Open Browser Dashboard

On your phone or laptop browser, navigate to:
```
http://PI_IP:8090/
```

You should see:
- Live video stream from the Pi camera
- Operator buttons: Y Confirm, N Reject, M Manual, N/E/S/W directions
- Status bar showing last command sent

### 2.5 Pre-Arm Checks

Before the script arms the drone, it will:
1. Connect to mavproxy (prints `Connecting to udpin:0.0.0.0:14550...`)
2. Wait for heartbeat (prints `Heartbeat. Requesting Data Stream...`)
3. Wait for GPS fix >= 3D with >= 6 satellites
4. Set GUIDED mode
5. Send arm command

**If arming fails:** Check Mission Planner Messages tab. Common issues:
- "PreArm: Need 3D Fix" -- wait longer, move to open sky
- "PreArm: Check Battery" -- voltage too low
- "PreArm: Compass not calibrated" -- run compass calibration in MP
- "PreArm: RC not calibrated" -- calibrate RC in MP

The script prints a 120-second arming timeout warning if it cannot arm.

---

## Phase 3: During Autonomous Flight

### 3.1 What You See on the Dashboard

The browser dashboard (`http://PI_IP:8090/`) shows:

**Video stream with HUD overlay:**
- Top-left: MODE (SIMULATION/REAL), STATE (current state machine state)
- Below that: ALT (altitude in meters), GPS position, speed
- Center: yellow crosshair (frame center)
- Green circle + line: active detection (target to crosshair)
- Detection confidence shown next to green circle (e.g., `TGT 0.85`)
- MODEL name shown at bottom-left

**What to watch for:**
- STATE should progress: INIT -> CONNECTING -> ARMING -> TAKEOFF -> SEARCH
- ALT should climb to 35m (TARGET_ALT) during takeoff
- During SEARCH, the drone flies the lawnmower pattern automatically
- Detections appear as green circles on the video feed

### 3.2 Normal Search Flow

The drone flies the search pattern at 35m altitude. The AI runs at ~5 FPS,
scanning every frame for the target. You do not need to do anything during
this phase unless:

- You see the drone heading toward the SSSI (NFZ) -- the geofence will slow
  it down and push it away automatically
- You want to pause for any reason -- press **M** for manual override

### 3.3 What the Terminal Shows

The Pi terminal (T3) prints:
- Waypoint progress: `Pre-waypoint 3/5 reached.`
- Speed changes near NFZ
- Any GPS warnings
- `TARGET DETECTED!` when the AI finds something

---

## Phase 4: Detection Workflow

This is the critical part where the operator makes decisions.

### 4.1 Detection -> CENTERING

When the AI detects a target during SEARCH:
1. Terminal prints: `TARGET DETECTED!` and `Investigating target at (lat, lon)`
2. State changes to **CENTERING** -- drone flies to the estimated GPS position
3. The drone homes in on the detection, refining the GPS estimate
4. Detection queue shows remaining targets if multiple were found

### 4.2 CENTERING -> VERIFY

Once the drone is within 1m of the target GPS:
1. State changes to **VERIFY**
2. Terminal prints: `VERIFY (at Xm) -- Y=Confirm  N=Reject  I=Interest`
3. The video HUD shows: `Y=Confirm  N=Reject  I=Interest` with a countdown timer
4. You have **120 seconds** to respond

**The drone hovers directly above the target. Look at the video feed carefully.**

### 4.3 Making Your Decision

Look at the video stream and decide:

| You see... | Press | What happens |
|------------|-------|-------------|
| The dummy/casualty clearly visible | **Y** | Confirmed -- GPS averaging starts, then landing sequence |
| Something interesting but not sure | **I** | Logged as Item of Interest with GPS, search resumes |
| False positive (rock, shadow, etc.) | **N** | Rejected -- position blacklisted, search resumes |
| Nothing at all (AI hallucinated) | **N** | Same as above -- reject and move on |

**If you do nothing:** After 120 seconds, the system auto-rejects and resumes search.
Terminal warnings at 60s, 90s, and every 10s after 100s.

### 4.4 After Pressing Y (Confirm)

1. If GPS averaging is active (--center-verify mode): system collects 10 seconds
   of GPS samples for higher accuracy. Terminal shows: `Y confirmed -- averaging GPS for Xs more...`
2. Terminal prints: `USER CONFIRMED TARGET. SELECT LANDING SIDE: N/E/S/W`
3. HUD shows: `SELECT LANDING SIDE: N/S/W/E`
4. Press **N**, **E**, **S**, or **W** to choose which side of the target to land on
   - Think about wind direction, obstacles, terrain
   - The drone will land 7.5m offset in the chosen direction
5. State changes to APPROACH -> HOVER_TARGET (15s hover + payload drop) -> RETURN

### 4.5 After Pressing N (Reject) or I (Interest)

The system checks the detection queue:
- If more targets are queued: immediately goes to CENTERING on the next one
- If no more targets: returns to the search departure point, resumes pattern

Terminal prints: `Next queued target at (lat, lon) -- X remaining` or
`Returning to search departure point`

### 4.6 Detection Queue

The system queues up to 20 detections (configurable via MAX_DETECT_QUEUE in
config.py). When multiple targets are found during a single search pass:

- They are investigated one at a time, oldest first
- After each Y/N/I decision, the next queued target is popped
- Invalid targets (inside NFZ, outside search area, near rejected positions)
  are automatically skipped
- If the queue overflows, the oldest detection is dropped

---

## Phase 5: Emergencies and Contingencies

### "If the drone stops moving"

1. Check the terminal -- what state is it in?
2. If HOVER: no waypoints were generated. Check search polygon config.
3. If CENTERING for >60s: centering timeout will trigger automatically,
   resuming search. The target GPS was probably inaccurate.
4. If any other state seems stuck: press **M** for manual override,
   then **M** again to resume automation.

### "If no detections after full scan"

The system handles this automatically:
- After completing all search waypoints, it starts a **rescan pass**
- Each rescan drops altitude by 20% (RESCAN_ALT_FACTOR = 0.8)
- Up to 3 rescan passes (MAX_RESCAN_PASSES = 3)
- Minimum altitude floor: 15m (RESCAN_ALT_FLOOR_M)
- Example: 35m -> 28m -> 22.4m -> 17.9m
- If all rescans exhausted with no confirmed target, mission ends (DONE state)

Terminal prints: `SEARCH COMPLETE -- nothing confirmed. Dropping Xm -> Ym (pass N)`

### "If false positive spam"

If the AI is producing many false positives:
1. Press **N** to reject each one quickly (do not let them time out)
2. Press **K** to clear all rejected targets and IOIs if you want to reset
3. Rejected positions are blacklisted (5m radius) so the same spot is not
   investigated again
4. Consider: the confidence threshold is set to 0.2 (very low). For future
   flights, increase CONFIDENCE_THRESHOLD in config.py (try 0.4 or 0.5)

### "If drone heads toward NFZ (SSSI)"

The geofence has three layers of protection:

1. **Waypoint filtering**: Search waypoints within 30m of NFZ are skipped at
   plan time (NFZ_WAYPOINT_BUFFER_M).
2. **Speed reduction**: Within 20m of NFZ boundary, speed ramps down from
   3 m/s to 0.3 m/s (proportional to distance).
3. **Repulsive push**: Within 23m of the inner NFZ boundary, a constant
   3 m/s push velocity is applied away from the boundary.
4. **Hard boundary**: If the drone crosses into the NFZ (within 3m), the system
   forces MANUAL mode and stops all velocity commands. Terminal prints:
   `[GEOFENCE] INSIDE NFZ! Switching to MANUAL`

**What to do:** The geofence is automatic. If the drone enters MANUAL due to
NFZ violation, press **M** to resume -- it will fly back to its departure point
first (RETURN_FROM_MANUAL), then resume the previous state.

### "If connection lost"

**Software link (Pi to Cube via mavproxy):**
- If recv_match fails, the script prints `[LINK LOST]` and attempts emergency
  RTL (sets Cube to RTL mode via MAVLink)
- If that also fails, ArduCopter's GCS failsafe (FS_GCS_ENABLE) triggers
  automatic RTL after the configured timeout

**RC link lost:**
- ArduCopter handles this independently via RC failsafe (FS_THR_ENABLE)
- Default behavior: RTL
- This works regardless of the Pi script state

### "If GPS degrades during flight"

The system monitors GPS fix quality continuously:
- If fix drops below 3D or satellites < 6, terminal prints warnings every 3s
- After 5 seconds of sustained degradation: emergency RTL is triggered
- Terminal prints: `[GPS] FIX LOST for Xs -- EMERGENCY RTL`
- If GPS recovers within 5s, the warning clears and flight continues

### RC Kill Switch (ALWAYS available)

The RC transmitter kill switch overrides everything:
- Flip the designated RC channel to switch from GUIDED to STABILIZE or LOITER
- This immediately gives the pilot full manual control
- ArduCopter obeys RC mode switches regardless of what the Pi script is doing
- The Pi script will print a warning: `WARNING: Cube in STABILIZE (not GUIDED)`

**Use the kill switch if:**
- The drone is behaving unexpectedly
- It is heading toward people or obstacles
- Any doubt about safety -- switch first, debug later

### Ctrl+C (Keyboard Interrupt)

Pressing Ctrl+C in the Pi terminal:
- Prints `[USER] Aborted -- attempting RTL before exit`
- Sends RTL mode command to the Cube
- Exits the script
- The Cube will complete the RTL independently

---

## Phase 6: Post-Flight

### 6.1 Available Data

After the mission, the following data is available:

**Flight log (CSV):**
```
logs/flight_log.csv
```
Columns: Timestamp, State, Lat, Lon, Alt, Target_Conf
Logged at ~1 Hz throughout the mission.

**Terminal output:**
- All state transitions, detection events, operator decisions
- GPS averaging results (if --center-verify was used)
- Final landing distance from home: `MISSION COMPLETE -- Landed X.XXm from home.`

**Items of Interest:**
- If you pressed **I** during VERIFY, the positions are stored in
  `self.items_of_interest` and printed to terminal
- Currently logged to terminal only -- copy/paste or screenshot

**Dry-run pattern:**
- `dry_run_pattern.jpg` -- the planned search pattern overlaid on the satellite map

### 6.2 Post-Flight Debrief Checklist

- [ ] Download `logs/flight_log.csv` from Pi
- [ ] Note any false positive patterns (altitude, lighting, terrain features)
- [ ] Record actual detection altitude vs. configured TARGET_ALT
- [ ] Record GPS accuracy (final landing distance from home)
- [ ] Record any geofence activations
- [ ] Note battery remaining at landing
- [ ] If detection performance was poor: consider adjusting CONFIDENCE_THRESHOLD,
      retraining model, or changing TARGET_ALT

### 6.3 Config Values to Tune After Flight

Based on flight results, update `config.py`:

| Value | Default | Tune if... |
|-------|---------|-----------|
| TARGET_ALT | 35m | AI cannot detect from this altitude -- lower it |
| CONFIDENCE_THRESHOLD | 0.2 | Too many false positives -- raise it |
| SEARCH_SPEED_MPS | 10 m/s | Motion blur causing missed detections -- lower it |
| DETECT_CONFIRM_FRAMES | 3 | Use with --smart-detect to filter transient FPs |

---

## State Machine Reference

```
INIT ──> CONNECTING ──> ARMING ──> TAKEOFF ──> PRE_WAYPOINTS ──> TRANSIT_TO_SEARCH
                                                                         |
                                                                    SEARCH (lawnmower)
                                                                    /    |
                                                          detection      | no detection
                                                               |        |
                                                          CENTERING     rescan at lower alt
                                                               |        (up to 3 passes)
                                                            VERIFY       |
                                                           /  |  \      DONE
                                                          Y   N   I
                                                          |   |   |
                                                   (select |   +-- resume search
                                                    side)  |
                                                      |    +-- RETURN_TO_SEARCH
                                                   APPROACH
                                                      |
                                                 HOVER_TARGET (15s, payload drop)
                                                      |
                                                 RETURN_TRANSIT (retrace path)
                                                      |
                                                 RETURN_HOME
                                                      |
                                                   LANDING
                                                      |
                                                    DONE

Any state: M ──> MANUAL ──> M ──> RETURN_FROM_MANUAL ──> resume previous state
```

---

## Current Dashboard Limitations

The browser dashboard at `/` is minimal by design (works over poor network).
It shows:

**What IS shown:**
- Live MJPEG video with HUD overlay (state, altitude, GPS, detection boxes)
- Operator buttons (Y/N/M/N/E/S/W)
- Last command confirmation with timestamp

**What is NOT shown (monitor via terminal or Mission Planner instead):**
- No map view in browser (use Mission Planner for map)
- No detection queue size display (printed to terminal)
- No battery level in browser (shown in Mission Planner)
- No audio alerts on detection (watch for green circle in video)
- No flight path history or coverage map
- No telemetry graphs (speed, altitude over time)

**Workarounds:**
- Keep Mission Planner open on the laptop for map, battery, and telemetry
- Keep the Pi terminal visible for queue size, state transitions, and warnings
- The video HUD shows altitude, state, and target coordinates

---

## CLI Flags Reference

```
python main.py [options]

--dry-run          Visualize pattern, no Cube needed
--headless         No cv2 windows (auto-detected on Pi)
--model PATH       Use alternate TFLite model
--transit PATH     Load transit waypoints from JSON
--speed N          SITL speedup factor (simulation only)
--alt N            Override TARGET_ALT
--beacon-delay N   Auto-trigger PLB beacon after N seconds of search
--center-verify    GPS averaging during VERIFY (10s hover for accuracy)
--smart-detect     Require N consecutive frames before triggering (DETECT_CONFIRM_FRAMES)
--no-nfz           Disable geofence enforcement
--no-stream        Disable HTTP stream server
```

---

## Troubleshooting Quick Reference

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| "No heartbeat in Xs" | mavproxy not running or wrong port | Start mavproxy (Terminal 1) |
| "Waiting for GPS fix..." | Outdoor, need open sky | Wait, move away from buildings |
| "ARM REJECTED" | Pre-arm check failed | Check Mission Planner Messages tab |
| "CAMERA LOST" on video | Camera disconnected or in use | Check ribbon cable, kill other scripts |
| "WARNING: Cube in STABILIZE" | RC pilot took over | Expected if kill switch used |
| "[GEOFENCE] INSIDE NFZ!" | Drone entered SSSI zone | Press M to resume, geofence pushes back |
| "[GPS] FIX LOST" | GPS signal degraded | Auto-RTL triggers, check antenna |
| "[LINK LOST]" | Serial/UDP connection dropped | Emergency RTL attempted, check cables |
| No detections at all | Altitude too high, wrong model | Lower TARGET_ALT or swap model |
| Many false positives | Threshold too low | Raise CONFIDENCE_THRESHOLD in config.py |
