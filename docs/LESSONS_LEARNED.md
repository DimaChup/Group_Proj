# Lessons Learned -- Critical Safety and Engineering Notes

This document records hard-won lessons from building and testing the SAR drone system.
Each entry follows the same structure: what happened, why, how we fixed it, and a
checklist so nobody repeats the mistake.

---

## LL-01: GUIDED / LOITER Mode-Fighting Crash

### WHAT HAPPENED

A colleague's drone crashed because the onboard software kept switching the flight mode
to GUIDED while the pilot's RC transmitter was set to LOITER (or vice versa). ArduCopter
received conflicting mode commands every loop iteration -- the flight controller
oscillated between two modes, lost stable control authority, and the drone fell.

The root cause is simple: if your code sends `SET_MODE(GUIDED)` on every loop while the
pilot's RC channel maps to LOITER, ArduCopter accepts both requests alternately. Neither
mode runs long enough to maintain stable flight. The drone does not "pick a winner" -- it
obeys whichever command arrived last, dozens of times per second.

### WHY THIS IS DANGEROUS

- ArduCopter mode changes are instant. There is no lock-out or debounce.
- GUIDED uses position/velocity targets from MAVLink. LOITER uses stick inputs. Mixing
  the two produces unpredictable thrust commands.
- The pilot may not even realise the software is fighting them -- the mode indicator
  flickers but the drone is already falling.

### OUR FIX (RC Override Guard)

In `main.py` (line ~760), every main-loop iteration checks `self._cube_mode` (updated
from every HEARTBEAT message at line ~471):

```python
# RC OVERRIDE GUARD: if pilot switched away from GUIDED,
# stop ALL commands. This prevents fighting the RC pilot.
# Modes 4=GUIDED, 9=LAND are ours. Anything else = pilot has control.
_pilot_override = self._cube_mode not in (4, 9) and self.state not in (
    State.INIT, State.CONNECTING, State.ARMING, State.DONE)
if _pilot_override:
    time.sleep(0.05)
    continue  # Skip keys + state handler + geofence -- pilot is flying
```

Key design choices:

- The guard runs **before** `_handle_keys()` and the state dispatch table. When the
  pilot has control, our code sends zero MAVLink commands -- no mode changes, no
  velocity commands, no position targets, no geofence enforcement.
- Only modes 4 (GUIDED) and 9 (LAND) are "ours". Any other mode means the pilot
  (or ArduCopter failsafe) took over.
- `self._cube_mode` comes from the actual HEARTBEAT `custom_mode` field, not from
  what we last requested. This means we track the real state of the autopilot.

### CHECKLIST

- [ ] Never send `SET_MODE` while the pilot's RC switch is in a manual mode
- [ ] Always read `custom_mode` from HEARTBEAT before deciding to send commands
- [ ] Test RC override on the bench (`tests/flight/0a_cube_commands.py`) before flying
- [ ] Verify the RC kill switch works: flip to STABILIZE mid-flight, confirm code stops
- [ ] If resuming after manual override, validate GPS fix and NFZ position first

---

## LL-02: IMX296 BGR Color Issue

### WHAT HAPPENED

Camera images from the Pi's IMX296 global shutter sensor had a persistent blue tint.
Attempts to fix it with AWB modes, manual colour gains, and ISP tuning all failed.
The real problem: the sensor outputs BGR data despite picamera2 labelling the format
as `RGB888`. Our code had `cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)` which double-swapped
the red and blue channels.

### WHY

The IMX296 is a monochrome-origin global shutter sensor with a Bayer filter. Its raw
pipeline in picamera2 produces BGR-ordered bytes regardless of the requested format
string. The label `RGB888` refers to the pixel packing (3 bytes, 8 bits each) not the
channel order. OpenCV expects BGR natively, so the data was already correct -- adding
`cvtColor` broke it.

### OUR FIX

Removed `cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)` entirely from `vision.py`. The raw
frame from picamera2 is already in OpenCV-native BGR order.

Discovery method: tested all 6 permutations of R, G, B channels and compared visually.
"No conversion" produced correct colours.

### CHECKLIST

- [ ] Do NOT add `cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)` to any Pi camera code
- [ ] If colours look wrong on a new sensor, test all 6 channel permutations before
      adding conversion code
- [ ] Don't trust format labels -- test empirically

---

## LL-03: TFLite Bounding Box Coordinate Bug

### WHAT HAPPENED

Green detection bounding boxes were drawn off-screen or in the wrong position. The
YOLO TFLite model outputs bounding box centre coordinates in the range 0-640 (pixel
coordinates relative to the 640x640 model input). Our code was treating these as
normalised values in the range 0-1, then multiplying by the frame dimensions. A
coordinate like `(320, 240)` was being multiplied by `(1456, 1088)`, producing a
position of `(466560, 261120)` -- far off-screen.

### WHY

YOLOv8 TFLite exports are inconsistent: some models output normalised coordinates
(0-1), others output pixel coordinates (0-640). The same model format can behave
differently depending on the export settings and runtime version. There was no
documentation stating which format our export used.

### OUR FIX

Added `PIXEL_COORD_THRESHOLD = 1.5` in `vision.py` (line 26). Before scaling, the
code checks whether the raw coordinate exceeds this threshold:

```python
if raw_cx > PIXEL_COORD_THRESHOLD:
    # Pixel coords relative to model input size -- scale to frame
    cx = int(raw_cx * w / input_w)
    cy = int(raw_cy * h / input_h)
else:
    # Normalised coords -- multiply by frame dimensions
    cx = int(raw_cx * w)
    cy = int(raw_cy * h)
```

This handles both formats automatically. The same logic is used in both the TFLite
and NCNN detection paths.

### CHECKLIST

- [ ] When adding a new model backend, check whether bbox output is pixel or normalised
- [ ] Test with a known detection: verify the green box visually matches the target
- [ ] If boxes appear off-screen or at (0,0), check the coordinate scaling path
- [ ] The threshold 1.5 works because normalised coords are always less than 1.0 and
      pixel coords are always at least several pixels

---

## LL-04: calibration_data.npz Corruption

### WHAT HAPPENED

On the Pi, `calibration_data.npz` (lens distortion calibration) was an empty file
(0 bytes). When `vision.py` loaded it at startup, `cv2.remap()` used garbage remap
matrices, mangling every frame. Detection stopped working entirely -- the AI model
received distorted noise instead of camera images.

### WHY

The file was likely created by an interrupted calibration run or a failed file transfer.
NumPy's `np.load()` does not crash on an empty `.npz` -- it returns empty arrays, which
`cv2.initUndistortRectifyMap()` accepts without error but produces meaningless output.

### OUR FIX

Deleted the corrupt `calibration_data.npz` on the Pi. Detection immediately started
working. The IMX296 global shutter has minimal barrel distortion, so lens undistortion
is optional. `config.py` has `UNDISTORT_ENABLED = False` by default.

If you do need undistortion:
1. Run `tests/calibration/lens_calibrate.py` with a proper checkerboard (calib.io,
   14x9 board, 13x8 inner corners, 28mm squares)
2. Verify RMS error is below 1.0 (ours was 0.399)
3. Visually confirm: straight lines in the real world should appear straight in the
   undistorted image
4. Set `UNDISTORT_ENABLED = True` in `config.py`

### CHECKLIST

- [ ] If detection suddenly stops working on Pi, check `calibration_data.npz` file size
- [ ] Delete `calibration_data.npz` if it exists and is < 1KB -- it is corrupt
- [ ] Undistortion adds ~1.5ms per frame -- negligible on a 206ms inference cycle
- [ ] The file is Pi-only and not tracked in git -- each Pi needs its own calibration
- [ ] When in doubt, delete it. `UNDISTORT_ENABLED = False` skips the remap entirely

---

## LL-05: GPS Timing Lag

### WHAT HAPPENED

GPS-estimated target positions had a consistent diagonal spread when the drone was
moving. Analysis of DJI flight video with SRT telemetry showed CEP50 of 2.3m and
maximum error of 16.5m. The error was always biased in the direction of flight.

### WHY

GPS receivers have 100-200ms internal processing latency. When the drone flies at
5 m/s, a 200ms delay means the reported position is 1m behind the actual position.
The target GPS estimate uses the drone's reported position plus the camera offset --
if the drone position is stale by 1m, the target estimate inherits that error.

At higher speeds or with gusty wind, the error compounds. The diagonal pattern in
scatter plots is a signature of motion-correlated GPS lag.

### MITIGATION STRATEGIES

1. **Average from multiple passes**: the lawnmower pattern crosses the target area
   in opposite directions. Errors cancel out when averaged with inverse-variance
   weighting (implemented in `gps_utils.py`).
2. **Slow down near target**: `FOCUS_SEARCH_SPEED_MPS = 5.0` reduces lag error to
   ~0.5m during the centering phase.
3. **GPS lag compensation** (not yet implemented): offset the reported position by
   `speed * lag` in the heading direction. Requires tuning the lag constant per
   GPS receiver.
4. **Centre-snap bonus**: detections where the target is at the optical axis
   (frame centre) get 10x weight in the position average, because projection
   error is minimal at the principal point.

### CHECKLIST

- [ ] Expect 1-3m GPS error in all position estimates during motion
- [ ] Use multiple observations from different passes, not a single frame
- [ ] Slow the drone to < 3 m/s before committing to a landing position
- [ ] The 7.5m offset landing provides margin for GPS estimation error
- [ ] See `memory/gps-timing-lag.md` for detailed analysis

---

## LL-06: DISARM_DELAY Must Be 0

### WHAT HAPPENED

During SITL testing, the drone auto-disarmed within 10 seconds of arming if it had
not yet taken off. The state machine armed the motors, then spent a few seconds
validating GPS and preparing waypoints. By the time it sent the takeoff command,
the Cube had already disarmed.

### WHY

ArduCopter's `DISARM_DELAY` parameter defaults to 10 seconds. If the drone is armed
but has not left the ground after this time, it automatically disarms as a safety
measure. This is sensible for manual flying (prevents a pilot from leaving motors
spinning on the ground) but breaks autonomous scripts that have a multi-second
startup sequence between arming and takeoff.

### OUR FIX

Set `DISARM_DELAY = 0` in Mission Planner's Full Parameter List before every flight.
This disables the auto-disarm timer entirely. The state machine handles disarming
explicitly when the mission is complete or aborted.

### CHECKLIST

- [ ] Before every SITL session: verify `DISARM_DELAY = 0` in Mission Planner params
- [ ] Before every real flight: verify `DISARM_DELAY = 0` on the Cube
- [ ] If the drone arms then immediately disarms, this parameter is the first thing
      to check
- [ ] Do NOT send `SET_POSITION_TARGET` during the takeoff phase -- it cancels
      `NAV_TAKEOFF` and can trigger the disarm timer
- [ ] Working commit for takeoff sequence: `adcec9d` on `refactor-modular`

---

## LL-07: Python 3.13 Compatibility on Raspberry Pi

### WHAT HAPPENED

Two critical packages are broken on Python 3.13:

1. **tflite-runtime**: cannot be installed. The official package does not support 3.13.
2. **pyserial**: serial reads are broken -- bytes are dropped, producing `BAD_DATA`
   MAVLink errors when reading directly from `/dev/ttyAMA0`.

### WHY

- `tflite-runtime` has C extensions compiled against Python's stable ABI. The 3.13
  release changed internal structures that broke binary compatibility. Google has not
  published updated wheels.
- `pyserial` has a known regression in 3.13 related to buffered reads on Linux serial
  devices. Bytes are occasionally lost, causing MAVLink framing errors.

### OUR FIX

**TFLite**: Use `ai-edge-litert` instead of `tflite-runtime`. It is Google's
replacement package with identical API:
```bash
pip install ai-edge-litert
```
Import is the same: `from tflite_runtime.interpreter import Interpreter` -- the
package installs compatibility shims.

**Serial**: Use mavproxy as a UDP bridge instead of direct serial access:
```bash
sudo mavproxy.py --master=/dev/ttyAMA0 --baudrate=921600 \
    --out=udpout:127.0.0.1:14550 --out=tcpin:0.0.0.0:5762
```
Scripts connect to `udpin:0.0.0.0:14550` (UDP, zero data loss). Mission Planner
connects via `tcp:<PI_IP>:5762` through the same bridge.

### CHECKLIST

- [ ] Never install `tflite-runtime` on Python 3.13 -- it will fail
- [ ] Install `ai-edge-litert` instead (in `requirements_pi.txt`)
- [ ] Never open serial ports directly in Python 3.13 scripts
- [ ] Always start mavproxy before running any flight script on Pi
- [ ] Verify mavproxy is running: `python -c "from pymavlink import mavutil; m = mavutil.mavlink_connection('udpin:0.0.0.0:14550'); print(m.recv_match(type='HEARTBEAT', blocking=True, timeout=5))"`
- [ ] If upgrading Python on Pi, re-test both packages before flying

---

## LL-08: Geofence Sign Conventions

### WHAT HAPPENED

Early geofence code pushed the drone *toward* the NFZ instead of away from it. The
repulsive force was inverted. Separately, the "inside NFZ" check was initially coded
with the wrong polarity, so the drone was flagged as inside when it was outside and
vice versa.

### WHY

`cv2.pointPolygonTest(contour, point, measureDist=True)` returns:

- **Positive** value = point is **INSIDE** the polygon
- **Negative** value = point is **OUTSIDE** the polygon
- **Zero** = point is on the boundary

This is counter-intuitive if you expect "distance to boundary" to be positive when
you are safely outside. The sign convention is documented in OpenCV but easy to get
wrong.

The repulsive offset function (`geofence.py`, `repulsive_offset()`) computes a GPS
delta using `GeoTransformer.pixels_to_gps()`. Due to the coordinate transform, the
raw offset points toward the NFZ. The returned values must be **negated** so that
adding them to a waypoint pushes the drone away.

From `geofence.py` (line ~210):
> "The returned offsets are therefore **negated** so that adding them to a target
> waypoint pushes the drone *away* from the NFZ. Without the negation the force
> would *attract* the drone into the NFZ."

### OUR FIX

- `distance_to_boundary()`: `is_inside = signed_dist_px >= 0` (treating boundary
  as inside for safety)
- `repulsive_offset()`: returns `(-offset_lat, -offset_lon)` (negated)
- Unit tests in `tests/flight/0e_geofence_test.py` verify both sign conventions
- Repulsive push only active during `State.MANUAL` to avoid fighting waypoint
  navigation in other states

### CHECKLIST

- [ ] `cv2.pointPolygonTest` positive = INSIDE, not outside
- [ ] Always negate repulsive offsets before adding to waypoints
- [ ] Run `tests/flight/0e_geofence_test.py` after any geofence code changes
- [ ] Visualise the NFZ on the map overlay to confirm the buffer zone is on the
      correct side (outside the polygon)
- [ ] If the drone drifts toward the NFZ instead of away, check offset signs first

---

*Add new lessons as they happen. Each lesson should include WHAT HAPPENED, WHY,
OUR FIX, and CHECKLIST. Date the entry. Reference the relevant source files and
line numbers so future developers can trace the fix.*
