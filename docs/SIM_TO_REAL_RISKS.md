# Simulation-to-Real Transition Risks

> Comprehensive risk register for transitioning from SITL simulation to real flight.
> Generated 2026-04-03. Review and update before every flight day.
>
> **Scoring:** Likelihood 1-5 (1=rare, 5=almost certain), Impact 1-5 (1=minor, 5=catastrophic).
> Risk score = Likelihood x Impact. Items scored 15+ are blockers.
>
> **Context:** The project has a 5.6-point gap between simulation (7.7/10) and real
> hardware (2.1/10) readiness. Zero minutes of real autonomous flight time have been
> logged. Every risk below represents something that works perfectly in SITL but may
> fail in the real world. See `docs/NEEDS_VS_CAPABILITIES.md` for the full scoring matrix.

---

## 1. Physics Risks (Simulation Does Not Model)

These are forces, dynamics, and physical effects that SITL ignores entirely. The
simulated drone responds instantly, flies in calm air, and never degrades.

| ID | Risk | L | I | Score | Mitigation |
|----|------|:-:|:-:|:-----:|------------|
| PH-01 | **Wind effects on flight path** -- SITL has zero wind. Real wind at the Bristol site can be 10-20 km/h with gusts. Wind pushes the drone off its search pattern, degrades GPS waypoint tracking, and makes centering on a target much harder. Crosswind on a lawnmower leg turns a straight pass into a curved one, reducing coverage overlap. | 4 | 3 | 12 | Check weather forecast: no-fly if sustained wind > 20 km/h or gusts > 30 km/h. Fly at lower altitude (15-20m) where ground turbulence is lower than at 35m over open fields. ArduCopter's WPNAV_SPEED and WPNAV_ACCEL handle wind compensation in GUIDED mode -- but only if PID tuning is correct. First flight should be a simple LOITER hold to observe drift. |
| PH-02 | **Motor/ESC response time** -- SITL motor response is instantaneous. Real motors have spin-up lag (~50-100ms), ESC communication delay, and variable thrust curves. This affects altitude hold precision and velocity control smoothness. ArduCopter's default PID gains are tuned for a "generic quad" which may not match our airframe's thrust-to-weight ratio. | 3 | 3 | 9 | Perform an initial hover at 3m and observe altitude oscillation. If the drone bobs or oscillates, PID tuning is needed (AUTOTUNE mode or manual P/I/D adjustment in Mission Planner). Do not fly autonomous missions until hover is stable. |
| PH-03 | **Battery voltage sag under load** -- SITL battery voltage is constant. Real LiPo batteries sag under load (especially during climb and aggressive maneuvers). A battery that reads 16.0V on the ground may drop to 14.5V during a hard climb. If `FS_BATT_VOLTAGE` is set too close to nominal, the failsafe triggers during normal flight. Conversely, if set too low, the battery is damaged by over-discharge. | 4 | 4 | 16 | Set `FS_BATT_VOLTAGE` conservatively (3.5V/cell = 14.0V for 4S). Set `FS_BATT_CRT_ACT` for critical voltage (3.3V/cell = 13.2V). Monitor battery voltage in Mission Planner during first hover. Calculate expected flight time from battery capacity and measured current draw. Never plan missions that use more than 70% of battery capacity. |
| PH-04 | **Vibration affecting camera and IMU** -- SITL has zero vibration. Real propellers at 5000+ RPM create vibration that: (a) causes motion blur in camera images, reducing AI detection accuracy, (b) introduces noise in IMU accelerometer readings, degrading altitude hold and position estimation, (c) can loosen connectors over time. | 4 | 3 | 12 | Mount camera on vibration dampening (rubber grommets or gel pads). Check IMU vibration levels in Mission Planner (VIBE message -- should be < 30 m/s/s on all axes). If vibration is high, balance propellers and check motor mounts. Test detection accuracy with `passive_watch.py` during a manual hover at 10-15m to assess real motion blur impact. |
| PH-05 | **Temperature effects on electronics** -- SITL runs at room temperature. Outdoor flights in cold weather (< 5C) reduce LiPo capacity by 10-20%, increase ESC failure risk, and can cause the Pi to throttle if it overheats in direct sun. The IMX296 sensor noise increases at high temperatures. | 2 | 2 | 4 | Keep batteries warm before flight (store in insulated bag). Monitor Pi CPU temperature via `vcgencmd measure_temp` (throttle at 80C, shutdown at 85C). Fly in mild conditions (5-25C). Shade the Pi enclosure from direct sunlight. |
| PH-06 | **Prop wash and ground effect** -- SITL does not model prop wash (disturbed air from propellers) or ground effect (increased lift within 1 rotor diameter of ground). Prop wash causes turbulence during descent, making the last 2-3m of landing unstable. Ground effect makes the drone "float" near the ground, complicating the final landing. | 3 | 2 | 6 | Use `MAV_CMD_NAV_LAND` for landing (ArduCopter handles ground effect compensation). Do not attempt manual altitude control below 3m with code. The 7.5m offset landing mitigates some risk by landing away from disturbed air. Accept that landing precision will be worse than simulation. |

---

## 2. Sensor Risks (Simulation Provides Perfect Data)

SITL sensors have zero noise, zero drift, and zero latency. Real sensors lie.

| ID | Risk | L | I | Score | Mitigation |
|----|------|:-:|:-:|:-----:|------------|
| SN-01 | **GPS drift (sim: 0, real: 2-5m)** -- SITL GPS is pixel-perfect. Real GPS has 2-5m CEP95 horizontal accuracy, worse near buildings or trees. GPS position jumps randomly within this error circle. Our lawnmower strip spacing, target GPS estimation, and offset landing all assume sub-meter GPS, which is not achievable with consumer GPS. | 5 | 3 | 15 | Accept 2-5m position uncertainty as baseline. Strip spacing in `planning.py` already accounts for overlap (FOV wider than strip width). GPS target estimation uses spatial clustering + inverse variance weighting to average multiple observations (reduces error by sqrt(N)). The 7.5m offset landing zone (5-10m range) provides margin. Run `tests/day_1_experiments/gps_drift.py` on the ground to measure local CEP50/CEP95 before flying. |
| SN-02 | **GPS timing lag (100-200ms)** -- SITL GPS updates are synchronous with the simulation clock. Real GPS receivers have 100-200ms internal processing latency. At 5 m/s flight speed, 200ms lag = 1m position error in the flight direction. This creates a systematic bias in target GPS estimates: all estimates are shifted along the direction of travel. DJI video analysis showed CEP50=2.3m with max 16.5m scatter. | 5 | 3 | 15 | Fly search passes at 6 m/s or slower to limit lag error to ~1m. The lawnmower pattern crosses the target from opposite directions -- averaging cancels the systematic bias. GPS lag compensation (offset by speed x lag in heading direction) is designed but not yet implemented. Centre-snap bonus gives 10x weight to detections at optical axis where projection error is minimal. See `memory/gps-timing-lag.md`. |
| SN-03 | **Barometer drift (0.5-2m over time)** -- SITL barometer is perfect. Real barometers drift with temperature changes, wind gusts over the sensor port, and atmospheric pressure changes during flight. Over a 10-minute mission, altitude can drift 1-2m. This means `TARGET_ALT = 35m` might actually be 33-37m. | 3 | 2 | 6 | ArduCopter fuses barometer with GPS altitude and accelerometer for altitude estimation (EKF). The fused estimate is much better than barometer alone. However, wind over the baro port causes fast transients. Ensure the barometer is shielded from direct airflow (foam cover on Cube). Altitude drift of 1-2m is acceptable for our mission -- detection works across a range of altitudes. |
| SN-04 | **Camera exposure changes (sun angle, clouds)** -- SITL uses a static map image with constant lighting. Real outdoor lighting changes constantly: sun angle, clouds passing overhead, shadows from the drone itself, and auto-exposure adjustments. Bright sun causes overexposure of light-colored targets. Shadows create high-contrast edges that trigger false detections. Sudden cloud cover changes exposure, causing frames where the AI model's performance degrades. | 4 | 3 | 12 | The retrained model (`sar_v2_1088`) includes brightness and contrast augmentation in training data, but real lighting variation exceeds training augmentation range. Use `--smart-detect` (requires 3 consecutive frames) to filter transient false positives from lighting changes. Test detection with `passive_watch.py` at the flight site before autonomous flight. Consider fixed exposure on Pi camera (`picamera2` manual exposure mode) to prevent auto-exposure hunting. |
| SN-05 | **Compass interference from motors** -- SITL has a perfect compass. Real motors draw 10-30A per motor and generate strong magnetic fields that corrupt the compass reading. Bad compass = bad yaw estimate = wrong heading = search pattern flies in the wrong direction. ArduCopter fuses compass with gyroscope, but if the compass is badly wrong, the EKF cannot compensate. | 3 | 4 | 12 | Mount the compass (GPS module with built-in compass) as far from motors and power wires as possible (top of GPS mast, at least 15cm above the frame). Run compass calibration (Mission Planner > Setup > Compass) at the flight site. Check `MAG_FIELD` in flight logs -- if it changes significantly with throttle, the compass is too close to motors. Consider disabling the internal compass (`COMPASS_USE2 = 0`) and using only the external GPS-mounted compass. |
| SN-06 | **IMU noise and vibration** -- SITL accelerometer and gyroscope have zero noise. Real IMU data on a flying drone has vibration harmonics from props, structural resonance, and wind buffeting. High vibration noise degrades EKF state estimation, causing position drift, altitude oscillation, and in extreme cases, EKF failsafe (EKFCHECK). | 3 | 4 | 12 | Check vibration after first hover: Mission Planner > Status tab > vibrations, or review `.bin` flight log `VIBE.VibeX/Y/Z`. Target: < 30 m/s/s on all axes. If above 30: check prop balance, motor mount tightness, and frame rigidity. If above 60: do not fly autonomously -- the EKF will produce unreliable position estimates. Add vibration dampening to the flight controller mounting (double-sided foam tape is standard). |
| SN-07 | **Rangefinder absence** -- SITL provides perfect AGL (above ground level) altitude. Real flights rely on GPS altitude + barometer fusion, which measures MSL (above mean sea level), not AGL. Over uneven terrain, a drone at "35m MSL" could be 30-40m AGL depending on ground elevation. Our offset landing at "0m altitude" means "0m above home" not "0m above the actual ground at the landing point". | 3 | 3 | 9 | The flight site is a relatively flat field, so MSL/AGL difference is small (< 2m across the site). For landing, ArduCopter uses the barometer for the final descent (more responsive than GPS altitude). Without a downward-facing rangefinder, landing precision is limited to ~0.5m altitude accuracy. A $20 TFMini lidar would solve this but has not been integrated. Accept this limitation for now. |

---

## 3. Software Risks (Code Path Differences)

Code that runs perfectly on the laptop may behave differently on the Pi, in
headless mode, over a real MAVLink connection, or with a different camera.

| ID | Risk | L | I | Score | Mitigation |
|----|------|:-:|:-:|:-----:|------------|
| SW-01 | **Inference speed difference (laptop GPU vs Pi CPU)** -- Laptop with Ultralytics runs detection at ~15ms (GPU-accelerated). Pi with TFLite runs at ~207ms (CPU). Pi with NCNN runs at ~72ms. Code that assumes fast inference (e.g., detection every frame) will miss targets at Pi frame rates. At 10 m/s and 4.8 FPS (TFLite), the drone moves 2.1m between frames -- a small target could be in only 1-2 frames of the FOV. | 5 | 3 | 15 | Use NCNN backend on Pi (`requirements_pi.txt` includes `ncnn`). At 9 FPS / 72ms, the drone moves 1.1m between frames at 10 m/s -- still 3+ frames per FOV crossing at 35m altitude. Reduce search speed to 6 m/s with `SPEED_AT_LOW = 6.0`. Use `--smart-detect` with `DETECT_CONFIRM_FRAMES = 3` to ensure the target is seen in multiple frames. Test actual FPS during flight with `passive_watch.py` before relying on autonomous detection. |
| SW-02 | **Frame rate difference (30fps sim vs 5-14fps real)** -- SITL with OpenCV webcam runs at 30fps. Pi with IMX296 + TFLite detection runs at 4.8fps (TFLite) or ~13-14fps (NCNN with threaded detection). Code timing, loop rates, and detection intervals all differ. State machine transitions that assume "N consecutive frames" take 3x longer on Pi. | 4 | 2 | 8 | `DETECT_CONFIRM_FRAMES = 3` at 5fps = 0.6s confirmation delay (acceptable). State machine transitions use time-based timeouts, not frame counts, for critical decisions. The `_handle_centering()` loop in `state_machine.py` uses `time.time()` for timeout, not frame count. Verify all timing-sensitive code uses wall clock, not frame count. |
| SW-03 | **Connection latency (localhost vs serial/UDP)** -- SITL connects via `tcp:127.0.0.1:5762` (loopback, < 1ms latency). Real connection goes through mavproxy UDP bridge: serial at 921600 baud → mavproxy → UDP → pymavlink. Each hop adds latency. Total: 5-20ms per message. Command acknowledgments take longer. Heart beat monitoring timers may need adjustment. | 3 | 2 | 6 | MAVLink is designed for lossy, high-latency links. pymavlink handles retransmission internally. `main.py` already uses `blocking=True, timeout=5` for critical ACKs. The 50ms main loop sleep is much larger than the added latency. Test the full pipeline on bench with `tests/flight/0a_cube_commands.py` before flying to verify command roundtrip works. |
| SW-04 | **Headless mode edge cases** -- SITL development uses `cv2.imshow()` for visual debugging. Pi runs headless (`--headless` flag, auto-detected when `$DISPLAY` is empty). Any code path that calls `cv2.imshow()`, `cv2.waitKey()`, or `cv2.namedWindow()` without a headless guard will crash or hang on Pi. The browser-based dashboard (`http://PI_IP:8090`) is the only visual interface. | 3 | 3 | 9 | All `cv2.imshow`/`waitKey` calls are guarded by `if not self.headless:` checks in `main.py`. Tested on Pi via SSH. Terminal keyboard input thread has try/except for no-TTY environments (nohup, systemd). Browser dashboard tested in simulation. Risk: untested code paths in error handling or new features may still call cv2 functions. Run `main.py --headless --dry-run` on Pi before any flight to catch these. |
| SW-05 | **picamera2 vs OpenCV webcam differences** -- SITL uses `cv2.VideoCapture(0)` (laptop webcam or virtual camera). Pi uses `picamera2` library (directly controls ISP). Frame format, resolution, colour space, and capture timing all differ. The IMX296 outputs BGR despite being labeled RGB888 (see LL-02 in LESSONS_LEARNED.md). Any new code that assumes OpenCV webcam behavior may break on Pi. | 3 | 3 | 9 | `vision.py` abstracts camera access: `detect_in_image(frame)` takes a raw numpy array regardless of source. Camera initialization is platform-specific but encapsulated. The BGR color issue is documented and fixed (no cvtColor). Test camera output on Pi with `tests/laptop/test_camera.py` before each flight day. If colors look wrong, check all 6 channel permutations before adding conversions. |
| SW-06 | **Python 3.13 compatibility** -- Laptop uses Python 3.11. Pi uses Python 3.13 (Bookworm default). Two critical breakages: (a) `tflite-runtime` does not support 3.13 -- must use `ai-edge-litert` instead, (b) `pyserial` has a regression causing serial byte drops -- must use mavproxy UDP bridge instead of direct serial. Any new dependency added on laptop must be verified on Pi. | 3 | 4 | 12 | Use `ai-edge-litert` (drop-in replacement, same API). Use mavproxy UDP bridge (already standard workflow). Before adding any new pip package, check PyPI for Python 3.13 wheels. Test on Pi after every code change that adds imports. See LL-07 in LESSONS_LEARNED.md. |
| SW-07 | **State machine untested transitions in real hardware** -- SITL tests the happy path thoroughly but some state transitions only occur under real-world conditions: GPS fix loss mid-flight, RC override during descent, battery failsafe during centering, compass error during search. These transitions have code paths that are difficult to trigger in SITL. | 4 | 4 | 16 | Unit tests cover 127 test functions including state transitions (`tests/unit/`). However, interaction with real ArduCopter failsafes is untested. The RC override guard (LL-01) is the primary safety net -- any unexpected situation can be recovered by the pilot flipping to STABILIZE. On first autonomous flight, keep altitude low (10-15m) and stay within quick-recovery distance. Log everything (`LOG_FILE` captures state transitions for post-flight analysis). |

---

## 4. Operational Risks (Human and Environmental Factors)

These risks exist regardless of software quality. They are about the people,
the environment, and the procedures around the flight.

| ID | Risk | L | I | Score | Mitigation |
|----|------|:-:|:-:|:-----:|------------|
| OP-01 | **Pilot unfamiliar with kill switch procedure** -- If the autonomous code does something unexpected, the pilot must immediately flip the RC mode switch to STABILIZE or POSHOLD. Hesitation of even 2-3 seconds at 10 m/s = 20-30m of uncontrolled flight. If the pilot has never practiced the switch under stress, reaction time will be slow. | 3 | 5 | 15 | Rehearse the kill switch procedure on the bench before every flight: pilot flips mode switch while looking at Mission Planner to confirm mode change. Practice until the muscle memory is automatic. The pilot should know: (1) which switch position is STABILIZE, (2) that the drone will hold attitude but not position, (3) that they need to actively fly after switching. Brief the pilot on every new flight phase before takeoff. |
| OP-02 | **No line of sight at distance** -- The search area extends up to 200m from the takeoff point. At 200m, a small drone is difficult to see against the sky. The pilot cannot judge altitude, attitude, or heading visually. UK CAA regulations require visual line of sight (VLOS) at all times. | 3 | 4 | 12 | Fly at altitudes where the drone is visible (15-35m). Use Mission Planner on a laptop with telemetry for real-time position display. Keep the drone within 150m horizontal distance. If VLOS is lost, immediately trigger RTL. Consider a bright LED or strobe on the drone for visibility. Have a spotter dedicated to watching the drone (not looking at screens). |
| OP-03 | **Other aircraft in area** -- The flight site may have other drones, model aircraft, or low-flying helicopters/light aircraft. A mid-air collision would destroy both vehicles and endanger people on the ground. | 2 | 5 | 10 | Check NOTAM (Notice to Airmen) for the area before flying. Use a spotter scanning for other aircraft. Stay below 120m (400ft) per UK drone regulations. Fly in designated areas away from aerodromes. If another aircraft is spotted, immediately descend and land. |
| OP-04 | **Spectators entering flight area** -- Curious people may walk into the flight area during operations, especially on a university campus or public field. A drone descending for landing or flying a low search pass could strike a bystander. | 3 | 5 | 15 | Mark the flight area with cones and caution tape. Have a team member act as a safety marshal to keep people out. Brief the team: if anyone enters the area, the pilot immediately switches to LOITER/hover and does not descend until the area is clear. Never fly over people. The 7.5m offset landing position should be away from the target (where an observer might stand). |
| OP-05 | **Communication breakdown between pilot and operator** -- The pilot (holding RC), the operator (at the laptop running main.py / browser dashboard), and the safety marshal must coordinate. If the operator sees a problem on screen but the pilot doesn't hear the call to abort, the drone continues its bad behavior. | 3 | 4 | 12 | Establish clear voice commands before flight: "ABORT" = pilot flips to STABILIZE immediately, "RTL" = pilot flips to RTL, "HOLD" = pilot switches to LOITER. Practice the callouts on the bench. Stand close enough to communicate without shouting (< 5m between pilot and operator). Never use ambiguous commands. |
| OP-06 | **WiFi link to Pi drops during flight** -- The browser dashboard and SSH session both rely on WiFi between the laptop and Pi. If WiFi drops, the operator loses video feed, telemetry overlay, and the ability to send Y/N verification commands. The autonomous code continues running without operator input. | 4 | 3 | 12 | ArduCopter's GCS failsafe (`FS_GCS_ENABLE = 1`) triggers RTL if heartbeats from `main.py` stop. However, `main.py` runs on the Pi (not the laptop), so a WiFi drop does NOT stop heartbeats -- the code keeps running autonomously. Mitigation: the VERIFY state has a timeout (configurable) -- if no Y/N response, it defaults to N (reject) and resumes search. RC override is always available regardless of WiFi. Consider a secondary RC channel mapped to a command (e.g., land) as a WiFi-independent control. |
| OP-07 | **First flight overconfidence** -- 7.7/10 simulation score creates a false sense of readiness. The team may attempt an aggressive first flight (full autonomous mission) instead of the progressive test ladder. Skipping steps 1-4 in the flight testing progression is the single most likely cause of an incident. | 4 | 5 | 20 | Follow the flight testing steps in CLAUDE.md strictly and in order. Step 1: Mission Planner AUTO waypoints (no custom code). Step 2: Waypoint test script (no CV). Step 3: Manual flight + passive CV. Step 4: Autonomous search with CV logging only (no action). Step 5: Full autonomous mission. Never skip a step. Each step must produce a clean log before advancing. See `docs/MISTAKES_TO_AVOID.md` FM-02. |
| OP-08 | **Incorrect Cube parameters on real hardware** -- SITL uses default ArduCopter parameters. The real Cube may have different defaults, or parameters set during a previous project. Critical parameters: `DISARM_DELAY`, `FS_GCS_ENABLE`, `FS_BATT_ENABLE`, `RTL_ALT`, `WPNAV_SPEED`, `FENCE_ENABLE`. Wrong parameters can cause unexpected disarms, no failsafes, wrong RTL altitude, or excessive speed. | 4 | 4 | 16 | Print and verify every parameter in `docs/MISTAKES_TO_AVOID.md` (CFG-01 through CFG-03) before first flight. Use Mission Planner's "Compare" feature to diff Cube parameters against a known-good SITL parameter file. Key settings: `DISARM_DELAY = 0`, `FS_GCS_ENABLE = 1`, `FS_BATT_VOLTAGE = 14.0`, `RTL_ALT = 3000`. Save a verified parameter file as backup. |

---

## 5. Risk Summary Matrix

### Top 10 Risks by Score

| Rank | ID | Risk | Score | Category |
|:----:|------|------|:-----:|----------|
| 1 | OP-07 | First flight overconfidence (skipping test steps) | 20 | Operational |
| 2 | PH-03 | Battery voltage sag under load | 16 | Physics |
| 3 | SW-07 | Untested state machine transitions on real hardware | 16 | Software |
| 4 | OP-08 | Incorrect Cube parameters | 16 | Operational |
| 5 | SN-01 | GPS drift (2-5m real vs 0 in sim) | 15 | Sensor |
| 6 | SN-02 | GPS timing lag (100-200ms) | 15 | Sensor |
| 7 | SW-01 | Inference speed difference (laptop vs Pi) | 15 | Software |
| 8 | OP-01 | Pilot unfamiliar with kill switch | 15 | Operational |
| 9 | OP-04 | Spectators entering flight area | 15 | Operational |
| 10 | PH-01 | Wind effects on flight path | 12 | Physics |

### Risks by Category

| Category | Count | Avg Score | Max Score |
|----------|:-----:|:---------:|:---------:|
| Physics | 6 | 8.2 | 16 |
| Sensor | 7 | 10.7 | 15 |
| Software | 7 | 10.7 | 16 |
| Operational | 8 | 12.8 | 20 |
| **Total** | **28** | **10.7** | **20** |

### Score Distribution

| Score Range | Interpretation | Count | Action |
|:-----------:|----------------|:-----:|--------|
| 15-25 | **Critical** -- must mitigate before flight | 9 | Verify mitigation is in place, test on bench |
| 9-12 | **High** -- mitigate where possible | 13 | Implement mitigations, accept residual risk |
| 4-8 | **Medium** -- monitor during flight | 6 | Awareness only, no specific action needed |
| 1-3 | **Low** -- acceptable | 0 | -- |

---

## 6. Config Values That Differ Between Sim and Real

These `config.py` settings work in simulation but may need tuning after real
flight testing. Values marked with an asterisk (*) are best guesses that have
never been validated on real hardware.

| Setting | Sim Value | Real Concern | Tuning Method |
|---------|-----------|-------------|---------------|
| `TARGET_ALT = 35.0` | Works in SITL | *May be too high for detection. Dummy may be invisible at 35m with real camera + outdoor lighting.* | Fly `passive_watch.py` at 15m, 20m, 25m, 30m, 35m. Check detection rate at each altitude. |
| `SEARCH_SPEED_MPS = 10.0` | Works in SITL | *Too fast for 4.8fps TFLite (2.1m between frames). Motion blur degrades detection.* | Start at 6 m/s. Increase only after confirming detection rate at speed. |
| `FOCAL_LENGTH_MM = 5.46` | Calibrated on bench at 1m | *FOV may differ at 15-35m altitude. Thermal expansion of lens at outdoor temperatures.* | Run `tests/calibration/gps_estimate_calibrate.py` with a known dummy position. |
| `IMAGE_W/H = 1456x1088` | Set for IMX296 native | Works on Pi (verified). No change needed. | N/A |
| `CONFIDENCE_THRESHOLD = 0.2` | Low for passive observation | *Will produce many false positives outdoors (shadows, rocks, people). Autonomous flight needs higher threshold.* | Use `--conf 0.4` for autonomous flight. Test with `passive_watch.py` first to measure FP rate. |
| `DETECT_CONFIRM_FRAMES = 3` | 3 frames at 30fps = 0.1s | 3 frames at 5fps = 0.6s. Acceptable but slower response. | No change needed. May increase to 5 if FP rate is high outdoors. |
| `NFZ_WAYPOINT_BUFFER_M = 30` | Works in SITL | *30m buffer reduces searchable area. May be excessive for real GPS accuracy of 3-5m.* | Start with 30m (conservative). Reduce to 15m after confirming GPS accuracy at site. |
| `CONNECTION_STR` | `tcp:127.0.0.1:5762` | Auto-detects to `udpin:0.0.0.0:14550` on Pi. | Verify with `tests/flight/0a_cube_commands.py` on bench. |
| `CAMERA_FLIP_180 = True` | N/A in sim (uses webcam) | Camera mounted inverted on drone frame. If mounting changes, this must change. | Visual check: is the stream image right-side-up in the browser? |

---

## 7. Pre-Flight Risk Verification Checklist

Before any real flight, verify these mitigations are in place. Check each box.

### Physics
- [ ] Weather checked: wind < 20 km/h sustained, < 30 km/h gusts
- [ ] Battery charged to 4.2V/cell, stored warm
- [ ] Camera mounted on vibration dampening
- [ ] All connectors secured (zip ties, hot glue on critical connections)

### Sensors
- [ ] GPS fix verified: fix_type >= 3, satellites >= 8 (more is better)
- [ ] Compass calibrated at flight site (Mission Planner > Compass Calibration)
- [ ] Barometer port shielded from direct airflow
- [ ] Camera exposure tested in current lighting conditions

### Software
- [ ] `main.py --headless --dry-run` runs without errors on Pi
- [ ] `tests/flight/0a_cube_commands.py` passes on Pi (arm, mode switch, RC override)
- [ ] Correct model deployed: `ls -la best.tflite` (should be 11.7MB for sar_v2_1088)
- [ ] NCNN backend available: `python -c "import ncnn; print('OK')"`
- [ ] mavproxy running with correct outputs

### Operational
- [ ] Pilot briefed on kill switch procedure (which switch, which position)
- [ ] Voice commands agreed: ABORT, RTL, HOLD
- [ ] Flight area marked with cones
- [ ] Safety marshal assigned to watch for spectators
- [ ] Cube parameters verified against checklist (DISARM_DELAY, FS_GCS, FS_BATT, RTL_ALT)
- [ ] Progressive test step identified (never skip steps)
- [ ] Flight log recording enabled

---

*Update this document after each flight day with new risks discovered, revised
likelihood/impact scores based on real experience, and new mitigations implemented.
Cross-reference with `docs/LESSONS_LEARNED.md` for detailed incident analysis.*
