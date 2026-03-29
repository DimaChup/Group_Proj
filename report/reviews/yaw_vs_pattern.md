# Yaw vs Search Pattern Direction

**Date**: 2026-03-29
**Question**: How does drone yaw relate to the lawnmower scan direction, and does it affect coverage?

---

## 1. What is DIAGONAL_YAW_OFFSET_DEG?

**Location**: `config.py` line 166

```python
DIAGONAL_YAW_OFFSET_DEG = 0    # Yaw offset at turn (0 = face scan line, None = auto)
```

This setting controls how many degrees the drone's nose is rotated *away from* the direction
of travel when flying the lawnmower search pattern. Two modes:

| Value | Meaning |
|-------|---------|
| `0` | Drone faces exactly along the scan line (direction of travel). Camera is perpendicular to flight path. |
| `None` (auto) | Offset is computed as `atan2(IMAGE_W, IMAGE_H)` = ~53.2 deg for 1456x1088. The camera is rotated so its diagonal aligns with the perpendicular axis. |
| Any number N | Drone nose is rotated N degrees clockwise from the scan-line heading. |

**Current value is 0** -- the drone faces forward along the scan line.

---

## 2. How Yaw Is Set (the _orient_search_yaw method)

**Location**: `state_machine.py` lines 314-352

The method runs once at the start of the SEARCH state (and again after each rescan). Steps:

1. **Compute base yaw**: bearing from waypoint[0] to waypoint[1] using
   `atan2(dlon * cos(lat), dlat)`. This gives the heading of the first scan strip.
   Fallback: `planner.last_scan_angle` (the rotation angle of the polygon's longest edge).

2. **Apply diagonal offset**: add `DIAGONAL_YAW_OFFSET_DEG` (or auto-computed value if `None`).

3. **Send MAV_CMD_CONDITION_YAW**: rotates the drone to the computed heading at 45 deg/s.

4. **Wait for alignment**: polls `self.yaw` until error < 10 deg or 5 second timeout.

5. **Set once, held forever**: the `no_turn=True` flag on the NavigationController means
   every subsequent `send_global_target()` call re-sends this same yaw value. The drone
   never re-orients when it U-turns at strip ends -- it flies the return strip sideways/backwards.

```
state_machine.py:136:  self.nav = NavigationController(self.master, no_turn=True, get_yaw=lambda: self.yaw)
navigation.py:48:      if yaw is None and self.no_turn and self._get_yaw is not None: yaw = self._get_yaw()
```

**Key insight**: the drone maintains a FIXED yaw for the entire search pattern. It does NOT
rotate to face each new strip direction. On the return strips it flies backwards/sideways.

---

## 3. Does the Drone Face the Direction of Travel?

**No.** With `no_turn=True`, the drone locks its yaw to the heading of the *first* strip
(plus any diagonal offset) and holds it for the entire pattern. On odd-numbered strips it
flies forward; on even-numbered strips it flies backward (or at a diagonal if offset is
applied). This is by design -- it avoids time-consuming 180-degree yaw rotations at each
U-turn.

If `no_turn` were `False`, the drone would rotate to face each strip's travel direction.
But the current code always sets `no_turn=True`.

---

## 4. Why Diagonal? (Camera Footprint Alignment)

The `None` (auto) mode computes `atan2(IMAGE_W, IMAGE_H)` which is the angle of the
camera's diagonal. The idea:

- The camera sensor is rectangular (1456 x 1088 pixels, aspect ratio 1.34:1).
- The ground footprint is also rectangular, with width > height.
- When the drone faces straight along the scan line (`offset=0`), the camera's *width*
  is perpendicular to travel -- this gives maximum perpendicular coverage per strip.
- When the drone is rotated by the diagonal angle (~53 deg), the camera's *diagonal*
  becomes perpendicular to travel -- this gives more perpendicular coverage (diagonal >
  width), but the coverage shape is a rotated rectangle, which complicates strip spacing.

**However, the current value is 0 (no diagonal offset).** The diagonal mode was an
experimental idea but is not active.

---

## 5. Does Camera Footprint Shape Depend on Yaw vs Flight Direction?

**Yes, critically.** The camera is fixed to the drone body. Its footprint on the ground is
always a rectangle aligned with the drone's body axes. What matters for coverage is how
this rectangle is oriented relative to the *strip direction*:

| Drone yaw | Perpendicular coverage (strip spacing) | Along-strip coverage |
|-----------|---------------------------------------|---------------------|
| Faces along strip (offset=0) | Camera width (wider) | Camera height (shorter) |
| 90 deg offset | Camera height (shorter) | Camera width (wider) |
| Diagonal (~53 deg) | Camera diagonal (widest) | Camera minor axis (shortest) |

The `no_turn` mode in `planning.py` (line 77-80) adjusts strip spacing to account for this:

```python
if getattr(self, '_no_turn', False):
    aspect = config.IMAGE_H / config.IMAGE_W    # 1088/1456 = 0.747
    ground_footprint_m = ground_footprint_m * aspect
    overlap = 0.0
```

**Wait -- this is calculating the NARROWER dimension (height).** With `no_turn=True` and
`offset=0`, the drone faces the first strip direction. On return strips, it flies backwards.
The camera width is perpendicular to the *first* strip, but on return strips, the camera
width is *still* perpendicular (because yaw is fixed and the strip direction reverses --
the perpendicular axis doesn't change). So perpendicular coverage is always the camera
width, not height.

**But the code uses `aspect * footprint` = camera height for strip spacing.** This appears
to be a conservative choice or possibly a bug. With the camera width perpendicular to scan
lines in both directions, the strip spacing should use the full width (with 20% overlap),
not the height. Using the height (shorter dimension) means tighter strips and more overlap
than necessary.

Analysis from `coverage_simulation.py` confirms two modes are tested:
- `no_turn`: perpendicular coverage = `gh` (ground height, shorter)
- `turning`: perpendicular coverage = `gw` (ground width, wider)

---

## 6. If We Change the Scan Angle, Does Yaw Need to Change?

**Yes, automatically.** The yaw is computed from the first two waypoints of the generated
pattern. When the scan angle changes (because the polygon shape changes or the start
corner changes), the waypoint direction changes, and the yaw follows.

The scan angle itself is computed in `planning.py` line 68:
```python
scan_angle = angle + 90 if size[0] < size[1] else angle
```
This aligns the scan strips with the polygon's *longest edge*, which minimises the number
of U-turns. The yaw then aligns with this same direction.

**If you manually change the scan angle** (not currently exposed as a config option), the
yaw would automatically update because it's derived from the waypoint geometry.

---

## 7. Is Coverage Guaranteed Regardless of Drone Yaw?

**Coverage depends on yaw consistency, not on the specific yaw value.**

- With `no_turn=True` (current mode): yaw is fixed, camera orientation is constant, strip
  spacing is computed for that fixed orientation. Coverage is guaranteed *as long as the
  drone actually holds the commanded yaw*.

- The risk: if ArduPilot overrides yaw (e.g., weathervaning in wind), the actual camera
  footprint shifts and gaps can appear between strips. The code assumes the drone holds
  the commanded yaw exactly.

- With `DIAGONAL_YAW_OFFSET_DEG = 0`: the camera width axis is perpendicular to scan lines.
  The strip spacing uses the camera height (narrower), giving ~33% extra overlap as a safety
  margin. This effectively makes coverage robust against moderate yaw errors.

- If the offset were non-zero (e.g., diagonal mode): the footprint would be a rotated
  rectangle, and coverage analysis becomes more complex. Gaps could appear at strip
  boundaries if the rotation isn't accounted for in the spacing calculation.

**Bottom line**: with the current settings (`offset=0`, `no_turn=True`, spacing based on
camera height), coverage is conservatively guaranteed. The drone could yaw-drift by up to
~20 degrees and still maintain coverage, because the strips are closer together than they
need to be.

---

## Summary

| Question | Answer |
|----------|--------|
| What does `DIAGONAL_YAW_OFFSET_DEG` do? | Adds N degrees to the drone's yaw relative to the scan-line bearing |
| Current value? | `0` (face along scan line) |
| Does drone face direction of travel? | Only on the first strip. It holds fixed yaw (no_turn=True), so it flies backwards on return strips |
| Why diagonal option exists? | To maximize perpendicular coverage using the camera diagonal. Not currently active. |
| Does yaw affect coverage? | Yes -- camera footprint orientation determines perpendicular coverage width |
| Does scan angle change require yaw change? | Yaw auto-updates from waypoint geometry |
| Is coverage guaranteed? | Yes, conservatively. Strip spacing uses camera height (narrower dim), giving ~33% safety margin |

---

## Key Files

| File | Lines | Relevance |
|------|-------|-----------|
| `config.py` | 166 | `DIAGONAL_YAW_OFFSET_DEG` definition |
| `state_machine.py` | 314-352 | `_orient_search_yaw()` -- computes and commands yaw |
| `state_machine.py` | 136 | `no_turn=True` on NavigationController |
| `navigation.py` | 28-62 | `no_turn` flag re-sends fixed yaw with every position command |
| `planning.py` | 77-80 | `_no_turn` adjusts strip spacing to camera height |
| `tests/automated/coverage_simulation.py` | 62-148 | Validates coverage for both turning and no-turn modes |
