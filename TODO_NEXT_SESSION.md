# Next Session TODO -- Tilt Compensation Priority

## 1. CRITICAL: Verify Tilt Compensation Math (run tests!)

The tilt compensation ray-tracing is implemented but needs thorough testing.
Two bugs were already found and fixed (sign flip, rotation axes) -- there may be more.

### Run the unit test:
```bash
cd "c:/Users/Bristol/Desktop/AI for Robotics/v3"
python -c "
import math, sys
sys.path.insert(0, '.')
from gps_utils import calculate_target_from_pixels
import config

# Test: drone heading NORTH, pitch -10° (nose down), detection at center
# Should give target ~6m NORTH of drone
fw, fh = 1456, 1088
alt, yaw, pitch, roll = 35.0, 0.0, -0.17, 0.0
focal_px = config.FOCAL_LENGTH_MM / config.SENSOR_WIDTH_MM * fw

# Compensation math from main.py
u, v = fw/2, fh/2  # center pixel
ray_x = (u - fw/2) / focal_px
ray_y = (v - fh/2) / focal_px
ray_z = 1.0
cp, sp = math.cos(pitch), math.sin(pitch)
cr, sr = math.cos(roll), math.sin(roll)
ry = ray_x * cr + ray_z * sr
rz = -ray_x * sr + ray_z * cr
rx = ray_y
ry2 = ry
rz2 = rx * sp + rz * cp
rx2 = rx * cp - rz * sp
t = alt / rz2
ground_x = ry2 * t
ground_y = rx2 * t
gsd = (config.SENSOR_WIDTH_MM * alt) / (config.FOCAL_LENGTH_MM * fw)
u_new = fw/2 + ground_x / gsd
v_new = fh/2 - ground_y / gsd

lat, lon = calculate_target_from_pixels(u_new, v_new, alt, yaw, 51.4234, -2.6714, fw, fh, config.SENSOR_WIDTH_MM, config.FOCAL_LENGTH_MM)
offset_n = (lat - 51.4234) * 111320
print(f'North offset: {offset_n:+.1f}m (expected +6.0m)')
print('PASS' if 5 < offset_n < 8 else 'FAIL')
"
```

### Visual test in simulation:
```bash
python main.py --speed 5 --lock-yaw --clean --sim-tilt --verbose-gps
```
Watch the verbose output -- when detecting while flying, the compensation should place
the target AHEAD of the drone (in flight direction), not behind.

## 2. Add --compensate-tilt to passive_watch.py

Robin needs tilt-compensated detections from passive_watch.
Currently passive_watch doesn't have attitude compensation.

### What to add:
- Read ATTITUDE message from mavproxy (pitch, roll available)
- Apply same ray-trace math when computing GPS estimate
- Add `--compensate-tilt` flag to passive_watch.py
- Test with `--fake` mode first

## 3. Fix Tilt Simulation Visual (lower priority)

The perspective warp in simulation.py works but the visual isn't quite right:
- Map features don't rotate correctly with tilt
- Arrow/text on map flips direction
- This is cosmetic -- the MATH is what matters for detection

### The perspective warp approach is correct in principle:
1. Ray-trace 4 image corners through tilted camera → trapezoid on ground
2. Extract trapezoid ROI from map
3. cv2.getPerspectiveTransform → warp to rectangle
4. Targets composited BEFORE warp (get same distortion)

### What might be wrong:
- Rotation matrix convention (Rz @ Ry @ Rx vs Rz @ Rx @ Ry)
- Sign convention for ArduPilot pitch (positive = nose UP)
- The NED → pixel coordinate mapping
- Run with --verbose-gps to verify numbers match expected physics

## 4. Set Up Proper Test Environment

Create a test script that:
1. Simulates known pitch/roll values
2. Places a dummy at a known position
3. Checks if the compensation correctly identifies the position
4. Runs multiple scenarios (all headings, pitch up/down, roll left/right)
5. Reports PASS/FAIL with expected vs actual GPS

```bash
python tests/unit/test_tilt_compensation.py
```

## 5. Document Everything in Goldmine

Already partially done. Verify:
- [ ] Ray-trace equations correct in LaTeX
- [ ] Error reduction table matches actual test results
- [ ] Simulation vs compensation consistency documented
- [ ] Two modes (--sim-tilt / --compensate-tilt) explained

## Key Math Reference

```
Camera at altitude h, pitch θ, roll φ:

1. Detection pixel (u,v) → camera ray:
   ray = ((u - cx)/f, (v - cy)/f, 1)

2. Rotate by attitude:
   R = Ry(-pitch) @ Rx(-roll)  [NED, ArduPilot signs negated]
   ray_world = R @ ray

3. Intersect ground (z = h below camera):
   t = h / ray_world_z
   ground = ray_world_xy × t

4. Convert to GPS offset:
   Rotate by yaw, scale by 1/111320
```

ArduPilot sign convention:
- pitch > 0 = nose UP (so forward flight = negative pitch)
- roll > 0 = right wing DOWN
- yaw > 0 = clockwise from north
