# Nice to Have — Future Improvements

A list of improvements that would make the system better but aren't blockers.
Each entry includes impact, effort, and notes.

---

## God view: draw the TRUE tilted ground footprint (trapezoid) instead of a nadir rectangle

**Status**: nice to have
**Impact**: low (cosmetic / diagnostic) — 3/10
**Effort**: low — 2/10
**Added**: 2026-04-13

### The issue
When the drone flies with forward pitch (e.g. `--sim-tilt`), the camera's real
ground footprint is a **trapezoid**: near ground compressed, far ground stretched.
The camera view correctly renders this trapezoid via `cv2.warpPerspective`.

However, the **god view** still draws a simple 4:3 rotated rectangle as the
drone's FOV indicator, using `view_w_px × view_h_px` computed for a nadir view.
At steep tilt, this rectangle is a poor representation of what the camera
actually sees.

### Fix
In `simulator/simulation.py::get_god_view`, instead of drawing a rotated
rectangle, ray-trace the 4 image corners using the same R matrix as
`_get_perspective_view` (`R = Rz @ Ry(-pitch) @ Rx(-roll) @ R_cam_to_body`) and
draw the 4 resulting ground points as a polygon on the god view. Same math,
just expose the `ground_pts` calculation to the god view too.

### Why this is not urgent
The centering math uses the real ray-traced ground position, not the god-view
rectangle. So navigation is already accurate — only the visualisation in the
god view is idealised. For the presentation and demo flight, the current
rectangle is fine.

---

## Port `DummyEstimator` inverse-variance averaging to main.py

**Status**: nice to have
**Impact**: medium — 5/10 (drops Phase 1 CEP from ~3.6m to ~2m during search)
**Effort**: medium — 4/10
**Added**: 2026-04-13

### The issue
`main.py` currently **overwrites** `target_lat/target_lon` on every detection.
There's no running average or Kalman filter. The three-phase refinement
(rough → hover re-detect → hover GPS average) relies on the final hover step
to converge, not on per-frame averaging.

### Fix
Port the `DummyEstimator` class from `field_tools/passive_watch.py` (or
`pi_flight.py`) into `main.py`. Replace the `self.target_lat = ...` assignments
in `calculate_target_gps()` with `estimator.add_observation(...)` + `get_estimate()`.

The estimator uses inverse-altitude-squared weighting (lower altitude = higher
weight) and a centre-bonus (detections near frame centre weigh more).

### Why this is not urgent
The existing three-phase mechanism already achieves sub-metre CEP at hover. The
inverse-variance estimator would improve Phase 1 (rough flying estimate) from
~3.6m to ~2m, but the hover re-detect step already compensates for Phase 1
errors. Demo day doesn't need it.

---

## Sim tilt variant selector cleanup

**Status**: nice to have
**Impact**: low — 2/10 (code hygiene)
**Effort**: trivial — 1/10
**Added**: 2026-04-13

### The issue
During sim-tilt debugging we added 8 matrix variants gated by the
`SIM_TILT_VARIANT` env var. Variant 1 is confirmed working. The other 7 are
dead code kept "just in case".

### Fix
Once variant 1 is confirmed stable across real-world flight tests too, remove
the variant switch and hardcode variant 1 in both `simulator/simulation.py` and
`main.py`. Remove the `SIM_TILT_VARIANT` env var handling.

### Why this is not urgent
Keeping the variants lets us A/B test if something weird shows up during field
testing. No harm in leaving them for now.
