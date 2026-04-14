# Sim-Tilt Fix — Perspective Rendering & GPS Estimation Consistency

**Date**: 2026-04-13
**Branch**: `presentation-final`
**Files changed**: `simulator/simulation.py`, `main.py`

---

## The Bug

When running `python main.py --sim-tilt`, two things happened:

1. **Before the fix**: The rendered perspective view did NOT rotate correctly with drone yaw. If the drone yawed to face east, the camera view stayed oriented to world-north. The drone was effectively "stuck looking north".
2. **After a naive fix**: Rotating the camera view fixed the visual, but the dummy GPS estimate now landed in the wrong place — the drone detected the dummy but navigated to a nearby-but-wrong position.

## Root cause

The simulator and the GPS estimator (in main.py) **both** do pixel-to-ground ray tracing using a rotation matrix `R`. The matrix was defined in TWO places, but it had a subtle convention error AND a 90° rotation missing:

```python
# OLD (broken):
R = Rz(yaw) @ Ry(-pitch) @ Rx(-roll)
```

The issue: `R` treated the camera ray `(u, v, 1)` as if it were already in the drone body frame (camera X = drone forward). But standard image coordinates have:
- Image right (+u direction) → drone RIGHT (body Y)
- Image down (+v direction) → drone BACKWARD (-body X)
- Optical axis (+z) → drone DOWN (body Z)

Without a camera→body rotation, the entire perspective view was rotated 90° from where it should be, and the yaw rotation embedded in `R` rotated the view around the wrong axis.

The symptom was self-consistent when BOTH the sim and the detection used the same broken R — the drone still got close to the dummy via iterative centering — but the view was visually 90° off.

## Why the intermediate "fix" failed

First attempt: added `R_cam_to_body` only to the simulator's forward projection.

```python
R_c2b = [[0, -1, 0], [1, 0, 0], [0, 0, 1]]
R = Rz(yaw) @ Ry(-pitch) @ Rx(-roll) @ R_c2b  # sim only
```

This made the sim render a correct view, but now the sim and the main.py GPS estimator used DIFFERENT R matrices. The sim projected the dummy onto (say) image row 201; the estimator back-projected row 201 using the old (rotated) R, giving a GPS 90° off. **Forward and inverse were out of sync.**

## The actual fix

Apply the same `R_cam_to_body` correction to **both** the simulator AND the GPS estimator, so forward and inverse projections use an identical R matrix:

```python
# simulator/simulation.py::_get_perspective_view
R_cam_to_body = np.array([
    [0.0, -1.0, 0.0],   # body_X (forward) = -cam_Y  (image top)
    [1.0,  0.0, 0.0],   # body_Y (right)   = +cam_X  (image right)
    [0.0,  0.0, 1.0],   # body_Z (down)    = +cam_Z  (optical axis)
], dtype=np.float64)
R = Rz(yaw) @ Ry(-pitch) @ Rx(-roll) @ R_cam_to_body
```

```python
# main.py::calculate_target_gps — SAME matrix, SAME order
R_cam_to_body = np.array([...same values...])
R = Rz(yaw) @ Ry(-pitch) @ Rx(-roll) @ R_cam_to_body
```

## Why no inverse?

A natural assumption is "we render forward, so detection must use the inverse". But both operations are actually **pixel → ground**:

| Step | Sim (rendering) | Detection (GPS estimation) |
|------|-----------------|----------------------------|
| 1. Pick pixel(s) | 4 image corners | 1 detection pixel |
| 2. Build ray | `ray_cam = ((u-cx)/fx, (v-cy)/fy, 1)` | Same formula |
| 3. Rotate to world | `ray_world = R @ ray_cam` | Same |
| 4. Ground intersect | `t = alt / ray_world[2]`, then `north_m = ray_world[0]*t`, `east_m = ray_world[1]*t` | Same |
| 5. Use result | src_pts for `cv2.warpPerspective` | Convert to GPS and navigate |

Both go from a camera-frame ray through `R` to a ground position. **They use the same R in the same direction — no inversion needed.**

The "camera is tilted by drone attitude" is encoded *inside* `R` itself. When the drone tilts, `R` changes, and that automatically:
- Makes the sim render a tilted view (corner rays hit different ground points)
- Makes the detection correctly account for the tilt (the same R compensates)

## Variant system (diagnostic)

During debugging we added a variant selector gated by `SIM_TILT_VARIANT` env var, keeping 8 sign/rotation combinations available so the user could test empirically:

| Variant | Description |
|---------|-------------|
| 0 | Original unfixed code (baseline) |
| **1** ⭐ | `R_cam_to_body` CCW, signs `-pitch, -roll` — the working fix |
| 2 | CCW, flipped pitch sign |
| 3 | CCW, flipped roll sign |
| 4 | CCW, both pitch and roll flipped |
| 5 | Original signs but flipped yaw |
| 6 | CCW + flipped yaw |
| 7 | CW rotation instead of CCW |

Default in both files is **variant 1** (working). Override with env var if needed.

## How to verify

```bash
python main.py --sim-tilt --speed 5
```

Expected behaviour:
1. Camera view rotates with drone yaw (look at the video feed as the drone turns)
2. When the drone pitches forward during flight, the camera view tilts forward (far ground at top of image, near ground at bottom)
3. Detection GPS estimate lands **on** the dummy, not next to it
4. Drone navigates accurately to the dummy during CENTERING

## Known limitation

This fix only touches the `--sim-tilt` code path (perspective view with non-zero pitch/roll). The nadir view (zero tilt) was already correct via a different code path (`_get_nadir_view` + `cv2.warpAffine`) and is unchanged.
