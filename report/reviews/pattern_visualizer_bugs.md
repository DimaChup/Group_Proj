# Pattern Visualizer Bug Report

> File: `tools/pattern_visualizer.py` (547 lines)
> Cross-referenced with: `planning.py`, `config.py`, `report/reviews/planning_review.md`

---

## Bug 1: Overlap slider has no effect

**Severity:** HIGH -- slider is misleading; user thinks they are tuning overlap but nothing changes.

**Root cause:** The visualizer sets `planner._no_turn = True` (line 180), which is correct (main.py does the same). But inside the patched `patched_generate()`, lines 218-219 replicate the real planning.py logic:

```python
if planner._no_turn:
    ...
    custom_overlap = 0.0      # <-- overlap forced to 0 regardless of slider
else:
    custom_overlap = overlap   # <-- never reached because _no_turn is always True
```

The slider value is captured into `overlap = self.overlap_pct / 100.0` (line 186) but then discarded because `_no_turn=True` always forces `custom_overlap = 0.0`.

This faithfully reproduces main.py behaviour (which also uses `_no_turn=True` and therefore 0% overlap). The slider exists but has zero effect on the generated pattern.

**Fix options:**
1. **Remove the slider** -- it does not represent a tunable parameter since main.py hardcodes `_no_turn=True`.
2. **Make it functional** -- if you want to explore "what if we had overlap", replace the forced zero with the slider value when `_no_turn=True`:
   ```python
   if planner._no_turn:
       aspect = config.IMAGE_H / config.IMAGE_W
       ground_footprint_m = ground_footprint_m * aspect
       custom_overlap = overlap  # use slider value instead of 0.0
   ```
3. **Add a `_no_turn` toggle** -- let the user switch between `_no_turn=True` (current flight mode, 0% overlap, aspect-scaled footprint) and `_no_turn=False` (20% overlap, full sensor footprint). This would make the overlap slider meaningful in one mode.

---

## Bug 2: Scan angle slider works correctly (no bug)

**Status:** WORKS AS INTENDED

The patched generator (lines 206-209) handles the scan angle correctly:

```python
if self.scan_angle > 180:
    s_angle = angle + 90 if size[0] < size[1] else angle  # auto = longest edge
else:
    s_angle = float(self.scan_angle)  # manual override
```

Slider range is 0-181. Value 181 means "auto" (longest edge alignment). Values 0-180 override the scan angle. The stats panel displays "auto" or the degree value. This matches the logic in planning.py and correctly allows manual override.

---

## Bug 3: NFZ buffer slider is purely visual -- does not affect waypoints

**Severity:** MEDIUM -- misleading because it implies the buffer clips scan lines, but it only draws a shaded zone.

**Root cause:** The NFZ buffer slider controls `self.nfz_buffer`, which is used ONLY in `_draw()` at lines 330-337 to draw a shaded polygon around the SSSI. It is NOT used in `_generate_pattern()` at all -- the pattern generation has zero NFZ awareness.

This actually matches the real system: `planning_review.md` section 6 confirms that `PathPlanner` has "zero awareness of the NFZ/SSSI" and that `filter_waypoints()` is never called in main.py either. So the visualizer is faithful to the (broken) real behaviour.

But the slider name "NFZ Buffer (m)" implies it affects the pattern, when it only affects the visual overlay.

**Also note:** The `_on_nfz_buffer` callback (line 482) does NOT invalidate the cache (`self._cached_key = None` is missing), unlike all other slider callbacks. This means changing the NFZ buffer doesn't even trigger a visual redraw of the stats panel (though the overlay itself updates because `_draw()` reads `self.nfz_buffer` directly each frame).

**Fix:**
1. **Label honestly** -- rename to "NFZ Display Buffer" or add "(visual only)" to the label.
2. **Make it functional** -- after generating waypoints, filter them through `NFZGeofence.filter_waypoints()` using the slider value. This would require importing geofence.py and temporarily setting `config.NFZ_WAYPOINT_BUFFER_M` to the slider value.
3. **Add cache invalidation** to `_on_nfz_buffer`:
   ```python
   def _on_nfz_buffer(self, val):
       self.nfz_buffer = val
       self._cached_key = None  # force pattern regeneration if NFZ filtering is added
   ```

---

## Bug 4: Monkey-patching works but bypasses the real PathPlanner entirely

**Severity:** LOW -- the visualizer generates correct-looking patterns, but it is NOT calling `planner.generate_search_pattern()`. It defines a completely independent `patched_generate()` function and calls it directly (line 271).

**What happens:**
- Line 189: saves `orig_generate = planner.generate_search_pattern` (never used again)
- Lines 191-269: defines `patched_generate()` as a local function
- Line 271: calls `patched_generate(self.disp_w, self.disp_h)` directly
- The original `planner.generate_search_pattern` is never monkey-patched, never called

This means the visualizer is a **parallel reimplementation** of the planning algorithm, not a visualization of the real one. If planning.py changes (bug fixes, new features), the visualizer will show stale behaviour.

**Specific drift risks:**
- planning.py has a single-footprint shortcut (returns centroid if polygon fits in one footprint) -- the visualizer does not
- planning.py has a `drone_gps` parameter that selects the starting corner closest to the drone -- the visualizer does not pass this, so pattern start corner may differ from the real mission
- planning.py stores `self.last_scan_angle` -- the visualizer does not

**Fix:** Replace the parallel implementation with an actual call to `planner.generate_search_pattern()`. Override config values temporarily if needed:
```python
import config
old_alt = config.TARGET_ALT
config.TARGET_ALT = float(self.altitude)
waypoints = planner.generate_search_pattern(self.disp_w, self.disp_h, drone_gps=config.TAKEOFF_GPS)
config.TARGET_ALT = old_alt
```
This would guarantee the visualizer always matches the real planner. The scan angle override is harder (planning.py auto-computes it), but for the visualizer's purpose, using the real planner is more valuable than having a manual angle slider that diverges from reality.

---

## Bug 5: Coverage percentage calculation is wrong

**Severity:** MEDIUM -- coverage numbers are inaccurate.

**Root cause (lines 292-295):**
```python
covered_area = sum(
    gps_distance_m(waypoints[i * 2], waypoints[i * 2 + 1]) * ground_fp_h
    for i in range(n_strips) if i * 2 + 1 < len(waypoints))
```

This multiplies each strip LENGTH by `ground_fp_h` (the footprint height along the flight direction). But the camera footprint dimension perpendicular to the flight direction is `ground_fp_w` (the footprint width), not `ground_fp_h`.

When `_no_turn=True`, the footprint is scaled by the aspect ratio:
- `ground_fp_w` = full sensor footprint (32.2m at 35m alt)
- `ground_fp_h` = `ground_fp_w * IMAGE_H/IMAGE_W` = 24.0m

The swath width (perpendicular to flight) should be `ground_fp_h` (24.0m, the aspect-scaled value used for strip spacing). The strip coverage dimension along-track should use the strip length itself. So the formula `strip_length * ground_fp_h` is accidentally correct for the `_no_turn=True` case because `ground_fp_h` happens to equal the swath width.

However, there is a second issue: **strips overlap at their ends near polygon edges**, and this formula counts overlapping coverage regions multiple times, inflating the percentage. The `min(100.0, ...)` clamp hides this.

**Fix:** For accuracy, compute coverage as the union area of all strip rectangles (using Shapely or a simpler bounding approach), or just note that the percentage is approximate.

---

## Bug 6: Energy estimate is a placeholder constant

**Severity:** LOW -- the number is displayed but not useful.

**Line 298:**
```python
energy_wh = total_dist * 15 / 3600
```

This assumes 15 W per metre of flight regardless of speed, altitude, wind, or payload. For a 3kg drone at 10 m/s, actual power draw is typically 200-400W, giving 20-40 W per metre -- so the estimate is roughly 2x too low.

**Fix:** Either label it explicitly as "rough estimate" in the stats panel, or use a more realistic model: `energy_wh = total_dist / speed * power_watts / 3600` where `power_watts` is configurable.

---

## Bug 7: Canvas size mismatch with real mission

**Severity:** MEDIUM -- the visualizer generates patterns at display resolution, not mission resolution.

**Root cause:** The visualizer creates `GeoTransformer(map_w_px=self.disp_w)` where `self.disp_w` is the display-scaled map width (capped at 1000px by `MAX_DISPLAY`). The pattern is generated at this resolution (line 271: `patched_generate(self.disp_w, self.disp_h)`).

But the real mission uses:
- SIMULATION mode: `sim.map_w` (full map resolution, typically 4000+ px)
- REAL mode: `REAL_CANVAS_SIZE = 4800` px

Since `pix_per_m` scales with canvas size, and strip spacing is computed in pixels (`strip_spacing_px = max(1, int(swath_m * self.pix_per_m))`), using a smaller canvas means:
- Fewer pixels per metre
- Coarser strip spacing (rounding to nearest integer pixel matters more)
- Potentially different number of strips than the real mission
- The pattern START corner may differ (no `drone_gps` is passed)

At 1000px display width, the error is small but nonzero. The strip count could differ by 1-2 strips from the real 4800px canvas.

**Fix:** Generate the pattern at `REAL_CANVAS_SIZE` resolution (or full map resolution), then project the GPS waypoints onto the display for rendering. This decouples pattern accuracy from display resolution.

---

## Bug 8: `nfz_buffer` not in cache key

**Severity:** LOW (currently, because NFZ buffer doesn't affect pattern generation anyway).

The cache key (line 168) is:
```python
cache_key = (tuple(self.search_poly_px), self.altitude, self.overlap_pct, self.scan_angle)
```

`self.nfz_buffer` is not included. If Bug 3 is fixed (NFZ buffer actually filters waypoints), the cache would serve stale results when the buffer changes.

**Fix:** Add `self.nfz_buffer` to the cache key tuple.

---

## Summary

| # | Issue | Severity | Slider works? | Fix difficulty |
|---|-------|----------|---------------|----------------|
| 1 | Overlap slider has no effect (`_no_turn=True` forces 0%) | HIGH | No | Easy (remove slider or use value) |
| 2 | Scan angle slider | -- | Yes | N/A |
| 3 | NFZ buffer is visual-only, no waypoint filtering | MEDIUM | Visual only | Medium (import geofence.py) |
| 4 | Parallel reimplementation instead of calling real planner | LOW | N/A | Medium (call real planner) |
| 5 | Coverage % uses wrong footprint dimension (partially correct by accident) | MEDIUM | N/A | Easy |
| 6 | Energy estimate is a rough placeholder | LOW | N/A | Easy (label or improve) |
| 7 | Canvas size mismatch (display res vs mission res) | MEDIUM | N/A | Easy (generate at full res) |
| 8 | NFZ buffer missing from cache key | LOW | N/A | Trivial |

**Top 3 to fix before using the visualizer for report figures:**
1. Bug 1 -- remove or fix the overlap slider (misleading)
2. Bug 7 -- generate at mission resolution for accurate strip count
3. Bug 4 -- call the real planner instead of reimplementing it
