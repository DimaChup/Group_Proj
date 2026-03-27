# TEST CHECKLIST: Working5.8

**Branch**: Working5.8
**Date Created**: 2026-03-27
**Purpose**: Verify all features and bug fixes work correctly before production deployment
**Audience**: Test lead, before each flight day

This checklist covers:
- Simulation mode (SITL) tests
- New CLI flags (--speed, --smart-detect, --center-verify, --beacon-delay, --no-nfz)
- Manual override (M key) workflow
- Multi-target queue system
- Geofence (NFZ) behavior and speed capping
- Detection filtering (search area, spatial clustering)
- Code refactoring (state machine, navigation, stream server)

---

## Pre-Test Setup

### 1. Verify Environment
- [ ] Windows laptop with SITL running (Mission Planner or mavproxy)
- [ ] `test_env` venv activated (has pymavlink, Ultralytics, TFLite)
- [ ] `export DRONE_MODE=SIMULATION` (or `set DRONE_MODE=SIMULATION` on cmd)
- [ ] Best model linked: `best.tflite` exists in project root
- [ ] No dangling processes on ports 8090/8091 (previous test runs)

### 2. Prepare Simulation Environment
```bash
cd v3
python -c "import config; print(f'MODE={config.MODE}, SEARCH_AREA={config.SEARCH_AREA_GPS}')"
```
Expected: Shows SIMULATION mode, valid 5-point polygon.

### 3. Dummy Placement
- [ ] In simple_simulator.py, know how to place dummies: click at desired pixel, press Y for dummy
- [ ] Have a test pattern: 1 dummy, 2 dummies, 4+ dummies for different tests

---

## TEST 1: Full Autonomous Mission (Baseline)

**Purpose**: Verify standard mission flow works end-to-end (lawnmower → detect → center → verify → land)

**Command**:
```bash
python main.py --speed 5 --dry-run  # First, verify dry-run
python main.py --speed 5            # Full mission
```

**Test Steps**:
1. Mission starts, shows INFO panel with state, GPS, battery
2. Drone takes off to TARGET_ALT (30m)
3. Begins SEARCH pattern (lawnmower) at SEARCH_SPEED_MPS (5 m/s)
4. Place 1 dummy in the center of search area
5. When AI detects dummy (detection box visible in stream):
   - State transitions to CENTERING
   - Drone slows to 1 m/s, centers visually on target
6. After ~10s centering, transitions to VERIFY
   - "CONFIRM DUMMY? (Y)es / (N)o / (I)nterest / (X) false positive" prompt appears
7. Press Y (confirm dummy)
8. State transitions to APPROACH (7.5m offset landing)
9. Drone lands and mission ends
10. Log file generated (flight_log.csv)

**Pass Criteria**:
- [ ] All states traversed in correct order
- [ ] Visual centering visible (cross lines move to track dummy)
- [ ] Terminal prompt works (Y/N/I/X input)
- [ ] APPROACH state executes (flies to 7.5m offset point)
- [ ] Landing completes without errors
- [ ] Flight log has >100 rows with valid telemetry

**Fail / Investigate**:
- [ ] Detections flickering (multiframe confirmation missing — enable --smart-detect)
- [ ] Dummy not detected (check confidence threshold, model swap)
- [ ] Heading wrong on offset landing (compass calibration issue)
- [ ] Crash/exit without clean state (check log for exception)

---

## TEST 2: Smart Detection (Multi-Frame Confirmation)

**Purpose**: Verify --smart-detect flag requires N consecutive detections before triggering (reduces false positives)

**Command**:
```bash
python main.py --speed 5 --smart-detect
```

**Test Steps**:
1. Start mission, place 1 dummy in search area
2. As drone flies over dummy, watch stream for detection box
3. Detection should appear, disappear, re-appear as drone passes
4. Verify: drone does NOT transition to CENTERING until N (e.g., 3) **consecutive frames** see the dummy
5. Watch terminal for debug: `[SMART_DETECT] Frame N/3 confirmed` (or similar)
6. Once confirmed, transition to CENTERING should happen
7. Press Y to confirm

**Pass Criteria**:
- [ ] Jittery detections (single frame) don't trigger state change
- [ ] Consistent multi-frame trigger works
- [ ] Smooth transition to CENTERING (not bouncy)
- [ ] Debug output shows frame counter

**Fail / Investigate**:
- [ ] Still triggers on single frame (--smart-detect not parsed correctly)
- [ ] Counter never reaches N (detection threshold too high, dummy too small)
- [ ] Performance degradation (multi-frame check shouldn't cost much)

---

## TEST 3: Center Verify (Vision Centering + GPS Averaging)

**Purpose**: Verify --center-verify flag enables dual centering: vision targeting + 10s GPS location averaging (improves landing accuracy)

**Command**:
```bash
python main.py --speed 5 --center-verify
```

**Test Steps**:
1. Start mission, place dummy in center of search area
2. Drone detects, enters CENTERING state
3. Watch stream: should see visual servo centering (not just GPS goto)
   - Dummy box should move toward center of frame
4. After ~10s, verify state should show: "GPS Averaging" in terminal (or similar debug)
5. Watch GPS fixes accumulate (should be 10-20 fixes at ~1Hz)
6. Transition to APPROACH (offset landing)
7. Landing should be more accurate than baseline

**Pass Criteria**:
- [ ] CENTERING shows visual servo (not instant goto)
- [ ] Terminal shows GPS averaging counter
- [ ] Final landing position closer to dummy (measure: within 2m)
- [ ] No crashes during visual servo phase

**Fail / Investigate**:
- [ ] Visual servo not visible (vision.py might not be exposing target pixel)
- [ ] No GPS averaging printout (debug output missing)
- [ ] Landing still offset (10s averaging didn't help — check GPS noise)

---

## TEST 4: Geofence (No-Fly Zone) Enforcement

**Purpose**: Verify NFZ (No-Fly Zone / geofence) logic: speed capping near boundary, repulsion if inside, auto-manual mode if breached

**Command**:
```bash
python main.py --speed 5
```

**Test Steps**:
1. Check config.py: SSSI_GPS should be loaded from KML file (4-point polygon)
2. Start mission, manually place dummy OUTSIDE the search area but near SSSI boundary
3. As drone flies toward detection:
   - Watch telemetry: speed should cap at SPEED_CAP_NFZ (2-3 m/s) within 10m of boundary
   - Terminal should show: `[NFZ] Boundary check: distance=Xm, speed capping`
4. If dummy is inside SSSI, drone should:
   - Auto-switch to MANUAL mode (RC takes over)
   - Emit repulsive force pushing back out
   - Terminal shows: `[NFZ] INSIDE SSSI! Switching to MANUAL mode`
5. Manual mode: drone stops accepting AI commands, pilot must fly out

**Pass Criteria**:
- [ ] Speed visibly reduces near boundary (< 3 m/s in telemetry)
- [ ] Debug output shows boundary distances
- [ ] Detections outside search area are ignored (not queued)
- [ ] Inside SSSI switches to MANUAL mode (RC override active)
- [ ] Repulsion vector points outward

**Fail / Investigate**:
- [ ] Speed cap not applied (NFZ logic disabled — check NO_NFZ flag)
- [ ] KML not loaded (geofence empty) — check CLAUDE.md SSSI_GPS polygon
- [ ] Detection queue has points outside search area (validation missing)
- [ ] Repulsion direction wrong (sign error in offset calculation)

---

## TEST 5: Disable Geofence (Testing Mode)

**Purpose**: Verify --no-nfz flag disables all geofence logic (for testing in constrained areas)

**Command**:
```bash
python main.py --speed 5 --no-nfz
```

**Test Steps**:
1. Place dummy INSIDE SSSI (or right on boundary)
2. Start mission
3. Verify: drone ignores NFZ boundary, no speed capping, no auto-manual mode
4. Flies directly to dummy, centers, lands (normal flow)
5. Terminal should show: `[NFZ] DISABLED (--no-nfz flag)`

**Pass Criteria**:
- [ ] No boundary warnings in terminal
- [ ] Speed never capped
- [ ] Drone centers and lands on in-SSSI dummy
- [ ] Safe for indoor test flights

**Fail / Investigate**:
- [ ] Still speed-capping despite flag (flag not parsed)
- [ ] Still switching to manual (NFZ logic not disabled)

---

## TEST 6: Manual Override (M Key) Workflow

**Purpose**: Verify operator can pause autonomous flight, fly manually, detect/queue dummies, then resume autonomy

**Command**:
```bash
python main.py --speed 5
```

**Test Steps**:
1. Start autonomous mission (drone in SEARCH state)
2. Press M key → state transitions to MANUAL
   - Terminal shows: "MANUAL MODE: Press M to resume, Y/N to mark detections"
   - Stream shows detection queue overlay
3. While in MANUAL, pilot flies around with arrow keys (or gamepad if hooked up)
4. Place dummy #1 in frame, press Y → adds to queue, shows "Queued: 1"
5. Fly to dummy #2, press Y again → "Queued: 2"
6. Fly to dummy #3, press Y again → "Queued: 3"
7. Press M again → state transitions back to SEARCH (resumes pattern)
8. Drone visits queued dummies in order (APPROACH each, VERIFY, land on each)

**Pass Criteria**:
- [ ] Manual mode triggered by M key
- [ ] Detection queue visible in stream (list of (lat, lon) coordinates)
- [ ] Y/N/I/X/L keys queue dummies correctly while in MANUAL
- [ ] Resume (M key again) restarts autonomous search
- [ ] Queue persists through resume (not cleared)
- [ ] Drone approaches queue in order
- [ ] Each dummy gets VERIFY step (operator confirms Y/N)

**Fail / Investigate**:
- [ ] M key not recognized (input handler broken)
- [ ] Queue not shown in stream (stream_server UI missing)
- [ ] Queue lost after resume (persists in wrong variable scope)
- [ ] Drone skips some queued dummies (pop logic missing validation)

---

## TEST 7: Multiple Dummies (Queue Ordering)

**Purpose**: Verify detection queue processes dummies in correct order (spatial clustering, inverse variance weighting)

**Command**:
```bash
python main.py --speed 5
```

**Test Steps**:
1. Start mission
2. Place 4 dummies in different corners of search area (spread out, >10m apart)
3. Watch detection box appear as drone flies over each
4. Verify: dummies are queued in order
5. Watch drone approach each in queue:
   - Should visit nearest first, or in detection order (check design doc)
   - Each gets CENTERING + VERIFY + APPROACH + LANDING
6. Count total landings == 4

**Pass Criteria**:
- [ ] All 4 dummies detected (no false negatives)
- [ ] Queue shows all 4 in stream overlay
- [ ] Drone approaches and lands on all 4
- [ ] Clear ordering logic (alphabetical, distance, detection time)
- [ ] Log shows 4 target entries

**Fail / Investigate**:
- [ ] Only 1 dummy visited (queue bug, only first processed)
- [ ] Landings not in expected order (ordering logic wrong)
- [ ] Duplicate entries in queue (dedup logic missing)
- [ ] Landing position inconsistent (GPS noise or heading calibration)

---

## TEST 8: NFZ Speed Capping at Boundary

**Purpose**: Deep test of geofence boundary behavior: verify speed ramps down gradually as drone approaches, recovers when moving away

**Command**:
```bash
python main.py --speed 8
```

**Test Steps**:
1. Configure search area polygon to TOUCH the SSSI boundary (intentionally close)
2. Start mission
3. Watch telemetry as drone flies toward boundary:
   - At 50m away: SEARCH_SPEED_MPS = 8 m/s
   - At 15m away: speed should drop to ~5 m/s
   - At 10m away: speed should drop to ~2 m/s (SPEED_CAP_NFZ)
   - At <5m away: should be ~1 m/s (emergency slow)
4. Watch distance metric in terminal: "Distance to boundary: Xm, speed capped at Ym/s"
5. If drone turns away from boundary, speed should recover to 8 m/s

**Pass Criteria**:
- [ ] Speed decrease is smooth, not jerky
- [ ] Capping starts at correct distance (10m buffer in config)
- [ ] Emergency slow works (prevent accidental boundary breach)
- [ ] Speed recovery when turning away is immediate
- [ ] Telemetry shows speed in real-time

**Fail / Investigate**:
- [ ] Speed never caps (repulsive_offset() not called or broken)
- [ ] Speed drops to 0 (too aggressive capping)
- [ ] Recovers too slowly (hysteresis in logic)

---

## TEST 9: Detection Outside Search Area (Ignored)

**Purpose**: Verify detections outside polygon are filtered out (only process dummies within search area)

**Command**:
```bash
python main.py --speed 5
```

**Test Steps**:
1. Place dummy #1 INSIDE search polygon
2. Place dummy #2 OUTSIDE search polygon (different area)
3. Start mission
4. As drone flies, watch stream and queue:
   - Dummy #1 (inside): should be detected and queued
   - Dummy #2 (outside): should appear in detection box but NOT be queued
5. Terminal should show: `[SEARCH] Detection outside polygon, ignoring`
6. Only dummy #1 should be approached and landed on

**Pass Criteria**:
- [ ] Inside detection queued immediately
- [ ] Outside detection visible but not queued (stream shows X on it)
- [ ] Terminal warning printed
- [ ] Only 1 landing happens (on inside dummy)

**Fail / Investigate**:
- [ ] Outside dummy queued (polygon check broken)
- [ ] Inside dummy ignored (polygon orientation or sign error)

---

## TEST 10: Beacon Delay (PLB Simulation)

**Purpose**: Verify --beacon-delay N simulates a Personal Locator Beacon (PLB) signal arriving N seconds after search begins (tests beacon-based redirect)

**Command**:
```bash
python main.py --speed 5 --beacon-delay 30
```

**Test Steps**:
1. Start mission (drone in SEARCH, lawnmower pattern)
2. Place dummy #1 in initial search area
3. Let mission run for ~30 seconds (timer hidden)
4. At T=30s, a secondary dummy appears (simulated PLB location)
5. Watch behavior:
   - Drone should detect original dummy, begin approach
   - Simultaneously, PLB signal triggers state change (new target)
   - Terminal shows: `[BEACON] PLB signal received! Redirecting to (lat, lon)`
6. Drone should redirect to PLB target instead, approach and land

**Pass Criteria**:
- [ ] Timing accurate (30s delay before beacon)
- [ ] State change triggered by beacon
- [ ] Redirect visible in terminal + stream
- [ ] Final landing is on PLB target (not original dummy)
- [ ] No crashes during redirect

**Fail / Investigate**:
- [ ] Beacon never triggers (timer logic broken)
- [ ] Beacon triggers too early/late (timing wrong)
- [ ] Redirect not executed (state change missing)

---

## TEST 11: Transit Planning (Path Optimization)

**Purpose**: Verify drone uses optimized transit path (if --transit JSON provided), not just lawnmower

**Command**:
```bash
python main.py --speed 5 --transit flight_plans/transit.json --dry-run
python main.py --speed 5 --transit flight_plans/transit.json
```

**Test Steps**:
1. Check if transit.json exists in project (see db481f2 commit "path simulation script")
2. Run dry-run first to visualize pattern (should show custom path, not lawnmower)
3. Run full mission
4. Verify: drone follows custom waypoint sequence (not standard lawnmower)
5. Watch terminal for path debug: "Path: [WP1, WP2, ...]"

**Pass Criteria**:
- [ ] --transit flag recognized (no error)
- [ ] Dry-run shows custom path image
- [ ] Drone follows custom waypoints (not lawnmower)
- [ ] Smooth transitions between waypoints

**Fail / Investigate**:
- [ ] transit.json not found (file missing or path wrong)
- [ ] Falls back to lawnmower (transit loading broken)
- [ ] Erratic path (waypoint coordinates invalid)

---

## TEST 12: Altitude Override

**Purpose**: Verify --alt N flag overrides TARGET_ALT and VERIFY_ALT settings

**Command**:
```bash
python main.py --speed 5 --alt 20  # Search at 20m instead of 30m
```

**Test Steps**:
1. Normal config has TARGET_ALT=30, verify by checking config.py
2. Run mission with --alt 20
3. Watch telemetry: drone should take off to 20m (not 30m)
4. Search pattern should execute at 20m altitude
5. Terminal should confirm: "TARGET_ALT overridden: 20m" (or similar)

**Pass Criteria**:
- [ ] Drone takes off to 20m (visible in telemetry graph)
- [ ] Search pattern executed at 20m
- [ ] Verify altitude is also adjusted (lower for closer view)
- [ ] Landing still works correctly

**Fail / Investigate**:
- [ ] Ignores flag, takes off to 30m (flag not parsed)
- [ ] Takes off to 20m but reverts during search (override not persistent)

---

## TEST 13: Dry-Run Mode (No Flying)

**Purpose**: Verify --dry-run prints mission plan without arming or connecting to Cube

**Command**:
```bash
python main.py --dry-run
python main.py --dry-run --speed 5
python main.py --dry-run --alt 25
```

**Test Steps**:
1. Run dry-run (no SITL needed, no arming)
2. Should print:
   - Mission summary (target alt, search speed, landing offset)
   - Lawnmower waypoint list (lat/lon coordinates)
   - State machine walkthrough (INIT → SEARCH → VERIFY → LANDING)
   - Estimated time and energy
3. Should save visualization image: `dry_run_pattern.jpg` (map + waypoints)
4. Should NOT:
   - Connect to Cube (no mavproxy needed)
   - Arm drone
   - Start state machine
5. Exit cleanly (no errors)

**Pass Criteria**:
- [ ] Runs without SITL or CUBE connection
- [ ] Prints readable mission plan
- [ ] Generates visualization image
- [ ] No errors or exceptions
- [ ] Fast execution (<1s)

**Fail / Investigate**:
- [ ] Tries to connect to Cube (dry-run not respected)
- [ ] Image file not created (visualization broken)
- [ ] Gibberish output (plan calculation error)

---

## TEST 14: Headless Mode (Pi Simulation)

**Purpose**: Verify --headless flag disables cv2.imshow and uses terminal/HTTP for UI (simulates Pi headless environment)

**Command**:
```bash
set DRONE_MODE=REAL  # (or SIMULATION)
python main.py --dry-run --headless
python main.py --speed 5 --headless
```

**Test Steps**:
1. Run with --headless
2. Verify:
   - No windows open (no cv2.imshow, cv2.namedWindow, etc.)
   - All output to terminal
   - Web stream starts on http://localhost:8090
3. Open browser to http://localhost:8090
   - Should show MJPEG stream + control buttons (Y/N/M/E/W/S)
4. Use browser buttons instead of keyboard
5. Mission should run headless (no X11 or GUI dependency)

**Pass Criteria**:
- [ ] No windows open (headless confirmed)
- [ ] Web stream accessible
- [ ] Browser buttons work (Y/N/etc.)
- [ ] Mission completes via browser control
- [ ] Terminal shows status (no visual output needed)

**Fail / Investigate**:
- [ ] Windows still open (headless not implemented)
- [ ] Stream not starting (HTTP server broken)
- [ ] Browser buttons not responding (command queue broken)

---

## TEST 15: Code Refactoring Validation

**Purpose**: Verify recent refactoring (extract state_machine, navigation, gps_utils, stream_server) didn't break integration

**Command**:
```bash
python main.py --dry-run        # Verify imports
python main.py --speed 5        # Verify runtime
```

**Test Steps**:
1. Check imports in main.py: should see `from state_machine import StateHandlersMixin`, `from navigation import NavigationController`, `from gps_utils import ...`, `from stream_server import ...`
2. Run dry-run: should not error on imports
3. Run full mission:
   - State machine should work (all states processed)
   - Navigation should work (waypoint following)
   - GPS utils should work (coordinate conversions)
   - Stream server should work (web UI responsive)
4. Check file sizes:
   - main.py: ~909 lines (was 1800+)
   - state_machine.py: ~1062 lines
   - navigation.py: ~253 lines
   - gps_utils.py: ~122 lines
   - stream_server.py: ~225 lines

**Pass Criteria**:
- [ ] All imports successful
- [ ] No AttributeError or NameError at runtime
- [ ] File sizes reasonable (main.py <1000 lines is goal)
- [ ] Mission completes end-to-end
- [ ] No performance degradation (similar speed as before refactoring)

**Fail / Investigate**:
- [ ] ImportError (module file missing or misnamed)
- [ ] AttributeError (function not exported from module)
- [ ] Runtime slower (overhead from module imports)

---

## TEST 16: Stream Server (HTTP UI)

**Purpose**: Verify web-based ground station works correctly during flight

**Command**:
```bash
python main.py --speed 5
```

**Test Steps**:
1. Mission starts
2. Open browser to http://localhost:8090
3. Should see:
   - Live MJPEG stream (video feed)
   - State info (current state, battery, GPS)
   - Detection queue (list of queued targets)
   - Control buttons: Y (confirm), N (reject), M (manual), E/W/S/N (compass)
4. Click buttons:
   - Y: should queue a dummy detection
   - N: should skip a detection
   - M: should toggle MANUAL mode
5. Buttons should respond in <100ms (no lag)
6. Stream should update at ~10 FPS (smooth video)

**Pass Criteria**:
- [ ] Web UI loads (no 404 errors)
- [ ] Stream shows live video
- [ ] State info updates in real-time
- [ ] Buttons responsive and immediate
- [ ] No console errors (browser dev tools)
- [ ] CPU usage reasonable (<50% for stream thread)

**Fail / Investigate**:
- [ ] Port 8090 not accessible (HTTP server not starting)
- [ ] Stream shows garbage or corrupted frames (video encoding issue)
- [ ] Buttons don't work (command queue not processing HTTP)
- [ ] Stream lags (threading bottleneck or frame rate issue)

---

## TEST 17: Confidence Threshold (0.2)

**Purpose**: Verify AI model confidence threshold (0.2) catches real dummies without excessive false positives

**Command**:
```bash
python main.py --speed 5
```

**Test Steps**:
1. Place 1 dummy in search area (high confidence: ~0.95)
2. Place random object (low confidence: ~0.15-0.25)
3. Start mission
4. Watch detections:
   - Real dummy: always detected, high confidence box
   - Random object: some detections at threshold edge
5. Verify: random object detections are occasional (not persistent)
6. Terminal shows confidence values: "Detection: conf=0.95, x=100, y=50"

**Pass Criteria**:
- [ ] Real dummy reliably detected (>95% of passes)
- [ ] False positives rare (< 5 per 100 detections)
- [ ] Confidence values printed for each detection
- [ ] Threshold value (0.2) reasonable for test environment

**Fail / Investigate**:
- [ ] Missing real dummy (threshold too high)
- [ ] Flooded with false positives (threshold too low)
- [ ] Confidence values not printed (debug output missing)

---

## TEST 18: Reject Radius (5m)

**Purpose**: Verify drone doesn't re-investigate same dummy within 5m radius (prevents loops)

**Command**:
```bash
python main.py --speed 5
```

**Test Steps**:
1. Place dummy #1 at location A
2. Approach, confirm (Y), land offset 7.5m away
3. Operator resets drone back to point A (within 5m of original)
4. Confirm new detection (Y)
5. Verify: drone does NOT re-investigate dummy #1 (detects rejection)
6. Instead, checks for NEW dummies in area (or skips if same)

**Pass Criteria**:
- [ ] Duplicate dummies skipped (within reject radius)
- [ ] Terminal shows: "Detection within 5m of known target, rejecting"
- [ ] No wasted fuel/time on same dummy

**Fail / Investigate**:
- [ ] Re-investigates same dummy (radius check broken)
- [ ] Radius too small (lands within 5m, still re-triggers)
- [ ] Radius too large (skips valid new dummies)

---

## TEST 19: Manual Mode Detection Queue

**Purpose**: Verify detections queued while in MANUAL mode are processed after resume

**Command**:
```bash
python main.py --speed 5
```

**Test Steps**:
1. Start mission, press M → MANUAL mode
2. Fly manually to dummy #1, press Y (queue it)
3. Fly to dummy #2, press Y (queue it)
4. Terminal shows: "Queue: [(lat1, lon1), (lat2, lon2)]"
5. Press M again → resumes SEARCH
6. Drone should approach dummy #1 first (from queue)
7. After landing on #1, approach dummy #2

**Pass Criteria**:
- [ ] Queue persists across MANUAL → SEARCH transition
- [ ] Queue visible in terminal or stream
- [ ] Dummies approached in queue order
- [ ] No duplicates if same dummy added twice

**Fail / Investigate**:
- [ ] Queue cleared on resume (bug in state transition)
- [ ] Queue not visible (debug output missing)
- [ ] Wrong order (queue logic scrambled)

---

## TEST 20: Rapid Key Presses (Input Robustness)

**Purpose**: Verify input handler doesn't crash under rapid/conflicting key presses

**Command**:
```bash
python main.py --speed 5
```

**Test Steps**:
1. Start mission
2. Rapidly press: M, Y, N, I, X, L in sequence (< 1 second apart)
3. Observe: terminal should NOT crash or hang
4. Each keypress should queue (not dropped)
5. After sequence, verify state is consistent (not corrupted)

**Pass Criteria**:
- [ ] No crashes or hangs
- [ ] No exception traces in terminal
- [ ] Keys processed in order (FIFO queue)
- [ ] State remains valid (not in unknown state)

**Fail / Investigate**:
- [ ] Crash on rapid input (race condition in input handler)
- [ ] Keys dropped (queue overflow)
- [ ] Corrupted state (invalid transition)

---

## TEST 21: Empty Detection Queue

**Purpose**: Verify mission handles case where queue empties (all dummies visited)

**Command**:
```bash
python main.py --speed 5
```

**Test Steps**:
1. Place 1 dummy in search area
2. Start mission
3. Detect, approach, confirm, land
4. After landing, drone should:
   - Check queue (empty)
   - Resume SEARCH pattern (continue lawnmower)
   - Or RTL if search complete
5. Terminal shows: "Queue empty, resuming search" or "Search complete, RTL"

**Pass Criteria**:
- [ ] No crash when queue empty
- [ ] Sensible next action (resume search or RTL)
- [ ] Terminal message clarifies behavior
- [ ] Mission continues (not stuck in LANDING)

**Fail / Investigate**:
- [ ] Crash on queue.pop() from empty (validation missing)
- [ ] Stuck in LANDING state indefinitely
- [ ] Attempts to approach None target

---

## TEST 22: Log File Generation

**Purpose**: Verify flight log (CSV) is created and contains valid telemetry

**Command**:
```bash
python main.py --speed 5
python -c "import csv; r = csv.DictReader(open('flight_log.csv')); print(next(r))"
```

**Test Steps**:
1. Run mission
2. Check for flight_log.csv in project root
3. Open and inspect:
   - Header row: time, state, lat, lon, alt, vx, vy, vz, battery, confidence, detection_x, detection_y
   - Data rows: should have >100 entries
   - No NaN or empty values (except detection fields if no detection)
4. Verify timestamps increase monotonically
5. Verify lat/lon are valid coordinates (e.g., 51.42, -2.67)

**Pass Criteria**:
- [ ] Log file created after mission
- [ ] All required columns present
- [ ] Timestamps monotonic
- [ ] Coordinates in valid range
- [ ] No corruption or garbage data

**Fail / Investigate**:
- [ ] No log file generated (CSV writer not called)
- [ ] Missing columns (schema wrong)
- [ ] Invalid coordinates (coordinate conversion error)

---

## SUMMARY

**Total Tests**: 22
**Estimated Runtime**: 45-60 minutes (in simulation)
**Prerequisites**: SITL running, test_env activated, no GUI blocking ports

### Quick Run (Critical Tests Only)
If short on time, prioritize:
1. TEST 1: Full mission baseline
2. TEST 6: Manual override (operators need this)
3. TEST 8: NFZ speed capping (safety critical)
4. TEST 15: Code refactoring (verify no regressions)
5. TEST 22: Log file (mission validation)

### Full Run (Complete Validation)
Run all 22 tests before deployment to ensure:
- All CLI flags work
- Refactoring didn't break integration
- Safety systems (NFZ, geofence) functional
- Queue and multi-target system solid
- Web UI responsive
- Logging complete

### Pass Definition
- [ ] 0 crashes
- [ ] 0 exceptions (all caught and logged)
- [ ] 0 failed state transitions (all states reachable)
- [ ] All 22 tests pass (or documented as known limitation)
- [ ] Performance acceptable (< 5s state transitions, smooth video stream)

---

**Next Steps After Passing**:
1. Merge Working5.8 to MainOne2 (staging branch)
2. Deploy to Pi and test in REAL mode (outdoor GPS, real camera)
3. Update CLAUDE.md session log with test results
4. Archive this checklist (append pass/fail times and notes)

---

**Questions / Issues During Testing**:
- Log all failures with timestamp and terminal output
- Screenshot any GUI anomalies (stream server, detection boxes)
- Note any performance issues (dropped frames, slow state changes)
- Report to team lead before proceeding to next phase
