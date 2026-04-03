# Mistakes to Avoid -- SAR Drone Project Checklist

A catalog of mistakes that cause crashes, failed flights, or wasted hours.
Each entry explains what goes wrong, how we prevent it, and where in our
codebase the protection lives.

Use this as a pre-flight review checklist and a reference when debugging.

---

## Code Mistakes

### CM-01: DON'T send mode commands while pilot is on RC

- [ ] **Verified: RC override guard is active**

**What goes wrong:** If your script sends `SET_MODE(GUIDED)` every loop iteration
while the pilot's RC transmitter is set to LOITER or STABILIZE, ArduCopter
receives conflicting mode commands dozens of times per second. Neither mode runs
long enough to maintain stable control. The drone oscillates between two control
strategies and falls out of the sky. This happened to a colleague's drone.

**How we prevent it:** The RC Override Guard in `main.py` (line ~757) checks
`self._cube_mode` (read from every HEARTBEAT message) before processing any
commands. If the mode is anything other than 4 (GUIDED) or 9 (LAND), the entire
main loop body is skipped -- no mode changes, no velocity commands, no position
targets, no geofence enforcement.

```python
# main.py line ~757
_pilot_override = self._cube_mode not in (4, 9) and self.state not in (
    State.INIT, State.CONNECTING, State.ARMING, State.DONE)
if _pilot_override:
    time.sleep(0.05)
    continue  # Skip keys + state handler + geofence
```

**Where the protection is:**
- `main.py` line ~757: RC override guard (runs BEFORE `_handle_keys`)
- `main.py` line ~468: `self._cube_mode` updated from HEARTBEAT `custom_mode`
- `state_machine.py` line ~264: resume safety checks (GPS fix + NFZ position)
- See `docs/LESSONS_LEARNED.md` LL-01 for full incident analysis

---

### CM-02: DON'T send SET_POSITION_TARGET during takeoff

- [ ] **Verified: no position commands in TAKEOFF state**

**What goes wrong:** `SET_POSITION_TARGET_GLOBAL_INT` cancels an in-progress
`NAV_TAKEOFF` command. The flight controller abandons the climb, the drone sits
on the ground with motors spinning, and the `DISARM_DELAY` timer kicks in --
auto-disarming the vehicle. Your script thinks it is taking off but the drone
never leaves the ground.

**How we prevent it:** The `_handle_takeoff()` method in `state_machine.py`
(line ~210) only checks altitude. It never sends position or velocity targets.
The transition to SEARCH (where position commands begin) only happens after
`self.alt >= config.TARGET_ALT * 0.90`.

**Where the protection is:**
- `state_machine.py` line ~210: `_handle_takeoff()` -- no position commands
- `state_machine.py` line ~225: altitude gate (`0.90 * TARGET_ALT`) before search
- Known good takeoff sequence: commit `adcec9d` on `refactor-modular`
- See `memory/sitl-disarm-delay.md` for full details

---

### CM-03: DON'T use cv2.CAP_DSHOW on Linux/Pi

- [ ] **Verified: platform guard is in place**

**What goes wrong:** `cv2.VideoCapture(0, cv2.CAP_DSHOW)` crashes immediately on
Linux and Raspberry Pi because DirectShow is a Windows-only video capture API.
The error message is cryptic (segfault or "backend not available") and wastes
debugging time.

**How we prevent it:** `vision.py` only passes `cv2.CAP_DSHOW` on Windows:

```python
if platform.system() == "Windows":
    cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
else:
    cap = cv2.VideoCapture(idx)
```

**Where the protection is:**
- `vision.py`: platform-guarded `CAP_DSHOW` in webcam initialization
- Fixed in session 2026-03-30 (Pi compatibility fixes)

---

### CM-04: DON'T apply cvtColor to IMX296 frames

- [ ] **Verified: no RGB/BGR conversion in vision pipeline**

**What goes wrong:** The IMX296 global shutter sensor outputs BGR data despite
picamera2 labeling the format as `RGB888`. If you add
`cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)`, you double-swap the red and blue
channels. All images get a blue tint. AI detection accuracy drops because the
model was trained on correct colours.

**How we prevent it:** No `cvtColor` call in `vision.py`. The raw frame from
picamera2 is already in OpenCV's native BGR order. This was verified empirically
by testing all 6 permutations of R, G, B channels.

**Where the protection is:**
- `vision.py`: no cvtColor in `detect_in_image()`
- `docs/LESSONS_LEARNED.md` LL-02: full incident analysis
- Comment in `CLAUDE.md` Camera Note section

**Rule:** If colours look wrong on a new sensor, test all 6 channel permutations
before adding any conversion code. Don't trust format labels.

---

### CM-05: DON'T trust TFLite bbox coords are normalised

- [ ] **Verified: PIXEL_COORD_THRESHOLD check is in vision.py**

**What goes wrong:** YOLOv8 TFLite exports are inconsistent. Some models output
normalised coordinates (0.0-1.0), others output pixel coordinates (0-640 relative
to the model input). If you assume normalised and multiply by frame dimensions,
a pixel coordinate like `(320, 240)` becomes `(466560, 261120)` -- bounding boxes
drawn far off-screen, GPS estimates wildly wrong.

**How we prevent it:** `vision.py` checks `PIXEL_COORD_THRESHOLD = 1.5` before
scaling. If the raw coordinate exceeds 1.5, it is treated as pixel coords and
rescaled from model-input space (640x640) to frame space. If below 1.5, it is
treated as normalised. This handles both formats automatically.

**Where the protection is:**
- `vision.py` line ~26: `PIXEL_COORD_THRESHOLD = 1.5`
- Both TFLite and NCNN detection paths use the same check
- `docs/LESSONS_LEARNED.md` LL-03: full incident analysis
- Fixed in commit `3d62e6a` (session 2026-03-30)

---

### CM-06: DON'T use corrupted calibration_data.npz

- [ ] **Verified: UNDISTORT_ENABLED = False by default in config.py**

**What goes wrong:** An empty or corrupt `calibration_data.npz` (0 bytes, from an
interrupted calibration run or failed file transfer) causes `cv2.remap()` to use
garbage remap matrices. Every camera frame is mangled beyond recognition. AI
detection stops working entirely -- the model receives distorted noise instead
of images.

NumPy's `np.load()` does not crash on an empty `.npz` -- it silently returns
empty arrays, which `cv2.initUndistortRectifyMap()` accepts without error.

**How we prevent it:** `config.py` sets `UNDISTORT_ENABLED = False` by default.
The IMX296 global shutter has minimal barrel distortion, so undistortion is
optional. If enabled, the calibration file must be verified (>1KB, RMS < 1.0).

**Where the protection is:**
- `config.py` line ~92: `UNDISTORT_ENABLED = False`
- `vision.py`: only loads calibration_data.npz when `UNDISTORT_ENABLED = True`
- `docs/LESSONS_LEARNED.md` LL-04: full incident analysis

**Recovery:** If detection suddenly stops working on Pi, check
`calibration_data.npz` file size. Delete it if < 1KB. Restart the script.

---

### CM-07: DON'T set DISARM_DELAY > 0

- [ ] **Verified: DISARM_DELAY = 0 in Cube parameters**

**What goes wrong:** ArduCopter's `DISARM_DELAY` parameter defaults to 10 seconds.
If the drone is armed but hasn't left the ground after this time, it automatically
disarms. Our state machine spends several seconds after arming validating GPS,
preparing waypoints, and setting up the camera. By the time it sends the takeoff
command, the Cube has already disarmed.

**How we prevent it:** Set `DISARM_DELAY = 0` in Mission Planner's Full Parameter
List before every flight session (SITL and real). The state machine handles
disarming explicitly when the mission is complete or aborted.

**Where the protection is:**
- Must be set manually in Mission Planner parameters (not in code)
- `state_machine.py` line ~210-218: detects unexpected disarm during takeoff
  - SIMULATION: retries arm sequence
  - REAL: safety stop, transitions to DONE
- `docs/LESSONS_LEARNED.md` LL-06: full incident analysis
- `memory/sitl-disarm-delay.md`: detailed notes

---

## Flight Mistakes

### FM-01: DON'T fly without testing RC kill switch first

- [ ] **Verified: kill switch tested on bench before every flight**

**What goes wrong:** If the RC kill switch (mode channel mapped to STABILIZE or
POSHOLD) doesn't work and your autonomous code does something unexpected, the
pilot has no way to regain control. The drone flies wherever the buggy code
sends it.

**How we prevent it:**
1. Bench test `0a_cube_commands.py`: verify the RC mode switch changes
   `custom_mode` in HEARTBEAT messages
2. Verify the RC override guard in `main.py` responds: flip to STABILIZE,
   confirm the script prints `_pilot_override` and stops sending commands
3. On first flight: flip the kill switch at 3m altitude, verify the drone
   holds position in STABILIZE/POSHOLD

**Where the protection is:**
- `main.py` line ~757: RC override guard skips all commands when mode is not GUIDED/LAND
- `tests/flight/0a_cube_commands.py`: bench test for RC mode switching
- `docs/FLIGHT_DAY_CHECKLIST.md`: kill switch test is a mandatory pre-flight item

---

### FM-02: DON'T skip bench test (props off) before flight

- [ ] **Verified: bench test completed before any flight**

**What goes wrong:** A wiring error, wrong channel mapping, inverted servo, or
command sequence bug discovered in the air is far more dangerous (and expensive)
than discovering it on the bench with props removed.

**How we prevent it:** Progressive test ladder in `tests/flight/`:
1. `0a_cube_commands.py` -- individual MAVLink commands on bench
2. `0b_bench_mission.py` -- full command sequence (no props)
3. `0c_feedback_test.py` -- vision-to-GPS pipeline (no commands)
4. `0d_planning_test.py` -- lawnmower pattern generation (no hardware)
5. `0e_geofence_test.py` -- NFZ boundary checks (no hardware)

Only after all bench tests pass do you proceed to `1_passive_flight.py` (manual
RC flight with passive CV observation).

**Where the protection is:**
- `tests/flight/` directory: numbered scripts enforce ordering
- `docs/DESIGN_DECISIONS.md` DD-07: progressive test strategy rationale
- `docs/FLIGHT_DAY_CHECKLIST.md`: bench test phase before any flight

---

### FM-03: DON'T fly without GPS 3D fix (>6 satellites)

- [ ] **Verified: GPS gate in ARMING state**

**What goes wrong:** Without a solid GPS fix (fix_type >= 3, satellites >= 6),
the drone's position estimate is unreliable. GUIDED mode waypoints will be
wrong, geofence checks will use garbage coordinates, and RTL may send the drone
to a nonsensical "home" position. ArduCopter may also refuse to arm, or worse,
arm with a poor fix and drift immediately after takeoff.

**How we prevent it:** The `_handle_arming()` method in `state_machine.py`
(line ~154) blocks all arming attempts until `self.gps_fix_ok` is True. This
requires `fix_type >= 3` and `sats >= 6` from `GPS_RAW_INT` messages.

```python
# state_machine.py line ~163
if fix_type >= 3 and sats >= 6:
    self.gps_fix_ok = True
```

**Where the protection is:**
- `state_machine.py` line ~163: GPS fix gate in ARMING state
- `state_machine.py` line ~268: GPS re-check before resuming after manual override
- `tests/hardware/gps_test.py`: standalone GPS diagnostics
- `tests/hardware/gps_health.py`: step-by-step GPS verification

---

### FM-04: DON'T fly faster than 6 m/s on first flight

- [ ] **Verified: SPEED_AT_LOW = 6.0 m/s in config.py**

**What goes wrong:** Higher speed means more motion blur (reducing detection
accuracy), shorter reaction time for the pilot to take over, more aggressive
turns that stress the airframe, and larger GPS lag errors (1m error per 5 m/s).
On an untested drone, you don't know the vibration profile, PID tuning quality,
or structural limits.

**How we prevent it:** `config.py` uses altitude-dependent speed:
- `SPEED_AT_LOW = 6.0` m/s at altitudes below 20m
- `SPEED_AT_HIGH = 10.0` m/s at altitudes above 50m
- Linear interpolation between those

For first flights, keep `TARGET_ALT` at 10-15m which automatically limits speed
to 6 m/s.

**Where the protection is:**
- `config.py` line ~65-75: `speed_for_altitude()` function
- `config.py` line ~60: `FOCUS_SEARCH_SPEED_MPS = 5.0` for centering phase
- NFZ speed cap: ramps speed down to 0.3 m/s near SSSI boundary

---

### FM-05: DON'T use confidence threshold below 0.4 on first flight

- [ ] **Verified: operator has confirmed threshold setting**

**What goes wrong:** A low confidence threshold (e.g., 0.1 or 0.2) produces
many false positive detections -- shadows, rocks, patches of grass all trigger
the AI. On first flights, false positives cause the drone to stop searching and
attempt to centre on nothing, wasting battery and flight time. Worse, if the
autonomous pipeline trusts a false positive, the drone may descend toward an
empty field.

**How we prevent it:** `config.py` sets `CONFIDENCE_THRESHOLD = 0.2` as the
global default (intentionally low for passive observation scripts). For
autonomous flight with `main.py`, the `--smart-detect` flag requires
`DETECT_CONFIRM_FRAMES = 3` consecutive detections before acting, which filters
out sporadic false positives even at lower thresholds.

For first flights, use `--conf 0.4` or higher to be conservative, then lower it
once you understand the false positive rate in your environment.

**Where the protection is:**
- `config.py` line ~98: `CONFIDENCE_THRESHOLD = 0.2` (default)
- `config.py` line ~99: `DETECT_CONFIRM_FRAMES = 3` (consecutive frame filter)
- `main.py`: `--conf` CLI flag to override at runtime
- `passive_watch.py`: browser slider for live confidence adjustment

---

### FM-06: DON'T fly in GUIDED without testing STABILIZE fallback

- [ ] **Verified: STABILIZE/POSHOLD fallback tested on bench**

**What goes wrong:** If your GUIDED mode code crashes, sends bad coordinates, or
loses the MAVLink connection, the pilot must immediately switch to a manual mode.
If STABILIZE or POSHOLD has never been tested on the actual airframe, the pilot
doesn't know how the drone will behave -- stick sensitivity, leveling response,
or whether the mode even works with the current PID tuning.

**How we prevent it:**
1. Test STABILIZE on the bench: flip the RC switch, verify the Cube accepts it
2. On first hover: flip to STABILIZE at 3m, fly manually for 30s, verify control
3. Test POSHOLD if available: verify GPS hold works with sticks centered
4. Always have the RC transmitter in hand with the mode switch accessible

**Where the protection is:**
- `main.py` line ~757: RC override guard -- any non-GUIDED mode stops all script commands
- `tests/flight/0a_cube_commands.py`: verify mode switching on bench
- `docs/FLIGHT_DAY_CHECKLIST.md`: RC mode test is a mandatory item

---

## Configuration Mistakes

### CFG-01: DON'T forget to set GCS failsafe

- [ ] **Verified: FS_GCS_ENABLE is set in Cube parameters**

**What goes wrong:** If your Python script crashes, the laptop loses WiFi, or the
ground station disconnects, the Cube keeps doing whatever it was last told to do.
Without a GCS failsafe, a drone in GUIDED mode with a velocity command will fly
in that direction until the battery dies or it hits something. With the failsafe
set, the Cube switches to RTL after losing heartbeat for a configurable timeout.

**How to set it:**
- Mission Planner > Config > Full Parameter List
- `FS_GCS_ENABLE = 1` (RTL on GCS loss) -- recommended
- `FS_GCS_TIMEOUT = 5` (seconds without heartbeat before triggering)
- Alternative: `FS_GCS_ENABLE = 2` (LAND on GCS loss -- safer if RTL altitude is risky)

**Where the protection is:**
- Must be set manually in Mission Planner parameters (not in our code)
- `main.py` sends heartbeats implicitly through pymavlink connection
- If `main.py` crashes, heartbeats stop, and ArduCopter triggers RTL/LAND
- `docs/PREFLIGHT_CHECKLIST.md`: GCS failsafe verification item

---

### CFG-02: DON'T forget to set battery failsafe

- [ ] **Verified: FS_BATT_ENABLE is set in Cube parameters**

**What goes wrong:** Without a battery failsafe, the drone flies until the battery
voltage drops below the ESC cutoff and all motors stop simultaneously. The drone
falls from whatever altitude it's at. With the failsafe set, ArduCopter triggers
RTL or LAND when the battery reaches a configurable voltage or remaining capacity.

**How to set it:**
- Mission Planner > Config > Full Parameter List
- `FS_BATT_ENABLE = 1` (LAND on low battery) or `= 2` (RTL on low battery)
- `FS_BATT_VOLTAGE = 14.0` (4S example: 3.5V/cell, adjust for your battery)
- `FS_BATT_MAH = 500` (remaining mAh before failsafe, requires current sensor)
- Also set `FS_BATT_CRT_ACT` for critical battery (lower voltage, more aggressive action)

**Where the protection is:**
- Must be set manually in Mission Planner parameters (not in our code)
- `state_machine.py` line ~707: landing handler has a 90s timeout with force-disarm
  as an absolute safety net, but this is a last resort -- battery failsafe should
  trigger well before this
- `docs/PREFLIGHT_CHECKLIST.md`: battery failsafe verification item

---

### CFG-03: DON'T fly without RTL_ALT configured

- [ ] **Verified: RTL_ALT is set appropriately in Cube parameters**

**What goes wrong:** `RTL_ALT` defaults to 1500 (15m in centimetres). If you're
flying in an area with trees, buildings, or terrain higher than 15m, the drone
may collide during RTL. If set too high, the drone wastes battery climbing before
returning. If set to 0, the drone returns at its current altitude, which could be
2m above ground (risky with obstacles between it and home).

**How to set it:**
- Mission Planner > Config > Full Parameter List
- `RTL_ALT` = desired return altitude in centimetres (e.g., 3000 = 30m)
- Set higher than any obstacle between the search area and the takeoff point
- `RTL_ALT_FINAL` = altitude to hold at before landing (0 = land immediately)

For our site (open field, no obstacles): `RTL_ALT = 3000` (30m) is safe.

**Where the protection is:**
- Must be set manually in Mission Planner parameters (not in our code)
- `state_machine.py` line ~690: our RETURN_HOME handler climbs to `config.TARGET_ALT`
  before flying home, which provides a code-level safety net -- but RTL_ALT is the
  ArduCopter-level protection that works even if our code crashes
- `docs/PREFLIGHT_CHECKLIST.md`: RTL altitude verification item

---

## Quick Reference: Where Each Protection Lives

| Mistake | Protection Location | Type |
|---------|---------------------|------|
| CM-01 Mode fighting | `main.py` line ~757 | Code guard |
| CM-02 Takeoff cancel | `state_machine.py` `_handle_takeoff()` | State design |
| CM-03 CAP_DSHOW crash | `vision.py` platform check | Code guard |
| CM-04 IMX296 cvtColor | `vision.py` -- no conversion | Design choice |
| CM-05 TFLite bbox | `vision.py` `PIXEL_COORD_THRESHOLD` | Code guard |
| CM-06 Corrupt npz | `config.py` `UNDISTORT_ENABLED = False` | Default config |
| CM-07 DISARM_DELAY | Mission Planner params | Manual setting |
| FM-01 Kill switch | `main.py` RC override guard | Code guard |
| FM-02 Bench test | `tests/flight/` numbered scripts | Process |
| FM-03 GPS fix | `state_machine.py` `_handle_arming()` | Code gate |
| FM-04 Speed limit | `config.py` `speed_for_altitude()` | Config function |
| FM-05 Confidence | `config.py` + `--smart-detect` flag | Config + CLI |
| FM-06 STABILIZE test | `tests/flight/0a_cube_commands.py` | Process |
| CFG-01 GCS failsafe | Mission Planner `FS_GCS_ENABLE` | Manual setting |
| CFG-02 Battery failsafe | Mission Planner `FS_BATT_ENABLE` | Manual setting |
| CFG-03 RTL altitude | Mission Planner `RTL_ALT` | Manual setting |

---

*Add new mistakes as they are discovered. Each entry should include: what goes
wrong, how we prevent it, and where in the code or configuration the protection
lives. Reference the relevant source files and line numbers.*
