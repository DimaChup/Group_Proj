# Planning.py Review -- Search Pattern Generation Logic

> Source: `v3/planning.py` (336 lines), `v3/main.py` (pattern generation at L284-289, dry-run at L830-903)

---

## 1. What class/function generates the lawnmower pattern?

**Class:** `PathPlanner` (line 7)

**Primary method:** `generate_search_pattern(map_w, map_h, drone_gps=None, alt_override=None)` (line 34)

**Secondary method:** `generate_spiral_pattern(map_w, map_h, drone_gps=None, alt_override=None)` (line 231) -- rectangular inward spiral, same mask technique.

**Post-processing:** `smooth_waypoints(waypoints, num_arc_points=3)` (line 193, static method) -- Bezier U-turn smoothing. **Not called anywhere in main.py.**

---

## 2. What inputs does it need?

### Constructor (`__init__`, line 28):
- `geo_transformer` -- a `GeoTransformer` instance (GPS <-> pixel conversion)
- `search_poly` -- list of `(x, y)` pixel vertices defining the search area

### `generate_search_pattern` arguments:
| Arg | Type | Source in main.py |
|-----|------|-------------------|
| `map_w` | int (pixels) | `sim.map_w` (SIMULATION) or `REAL_CANVAS_SIZE=4800` (REAL) |
| `map_h` | int (pixels) | `sim.map_h` (SIMULATION) or `REAL_CANVAS_SIZE=4800` (REAL) |
| `drone_gps` | `(lat, lon)` or None | Last transit waypoint, or `(REF_LAT, REF_LON)` in dry-run |
| `alt_override` | float or None | Defaults to `config.TARGET_ALT` (35m) |

### Config values consumed inside the method:
| Config | Value | Purpose |
|--------|-------|---------|
| `config.TARGET_ALT` | 35.0 m | Default search altitude |
| `config.SENSOR_WIDTH_MM` | 5.02 mm | Camera sensor width |
| `config.FOCAL_LENGTH_MM` | 5.46 mm | Calibrated focal length |
| `config.IMAGE_W` | 1456 px | Used only when `_no_turn=True` (aspect ratio calc) |
| `config.IMAGE_H` | 1088 px | Used only when `_no_turn=True` (aspect ratio calc) |

### External state:
- `self.pix_per_m` -- from GeoTransformer (pixels per metre scale)
- `self._no_turn` -- flag set externally (see section 7)

---

## 3. What does it return?

**Returns:** `list[(lat, lon)]` -- GPS waypoints defining the zigzag path.

- Each strip produces 2 waypoints (start and end of the strip).
- Strips alternate direction (zigzag / boustrophedon).
- Consecutive duplicates are removed (from narrow polygon regions).
- Returns empty list if polygon has < 3 vertices or mask is empty.
- Special case: if polygon fits in a single camera footprint, returns a single centroid waypoint.

---

## 4. How does it compute scan angle? (longest edge alignment)

**Lines 66-69:**
```python
rect = cv2.minAreaRect(poly_pts[0])
(center, size, angle) = rect
scan_angle = angle + 90 if size[0] < size[1] else angle
```

1. Computes the **minimum-area bounding rectangle** of the polygon using `cv2.minAreaRect`.
2. OpenCV returns `angle` as the rotation of the rectangle. `size = (width, height)`.
3. If width < height, adds 90 degrees to align scan lines along the **longer** dimension.
4. The mask is then rotated by `scan_angle` so the longest edge becomes horizontal.
5. Scan lines run horizontally across the rotated mask.
6. Result is stored in `self.last_scan_angle`.

The inverse rotation matrix is precomputed to un-rotate waypoints back to map coordinates.

---

## 5. How does it compute lane spacing? (altitude + camera FOV)

**Lines 76-84:**
```python
ground_footprint_m = (config.SENSOR_WIDTH_MM * search_alt) / config.FOCAL_LENGTH_MM
```

This is the thin-lens formula: `footprint = (sensor_width * altitude) / focal_length`.

At 35m altitude: `(5.02 * 35) / 5.46 = 32.2m` ground footprint width.

**Overlap handling:**
- If `_no_turn` is True: overlap = 0.0, footprint is scaled by `IMAGE_H/IMAGE_W` aspect ratio (0.747), giving ~24.0m effective swath
- If `_no_turn` is False: overlap = 0.2 (20%), swath = footprint * 0.8 = ~25.7m

**Strip spacing:** `strip_spacing_px = max(1, int(swath_m * self.pix_per_m))`

**Inset:** Scan lines are inset by `strip_spacing_px // 3` from the polygon edges (line 107), preventing strips from running along the very edge of the search area.

---

## 6. How does it handle the NFZ? (SSSI geofence)

### Planning.py itself: **No NFZ handling whatsoever.**

The `PathPlanner` class has zero awareness of the NFZ/SSSI. It generates waypoints purely from the search polygon geometry.

### NFZ filtering is in geofence.py:

`NFZGeofence.filter_waypoints(waypoints_gps)` (geofence.py line 124) removes waypoints inside or within `NFZ_WAYPOINT_BUFFER_M` (30m) of the SSSI polygon.

### CRITICAL FINDING: `filter_waypoints()` is **never called in main.py**.

- It is defined in `geofence.py` (line 124)
- It is called only in `tests/flight/geofence_demo.py` (line 385)
- **main.py generates waypoints (line 289) but never filters them through the geofence**
- The geofence only provides runtime protection (speed limiting, repulsive push, MANUAL mode switch) -- but the planned path itself is NOT filtered

This means the lawnmower pattern may include waypoints inside or near the SSSI. The drone relies entirely on runtime geofence enforcement to avoid the NFZ, rather than planning a safe path from the start.

---

## 7. What is the `_no_turn` flag?

**Set in main.py line 211:**
```python
self.planner._no_turn = True
```

**Effect in planning.py lines 77-82:**
When `_no_turn = True`:
- Uses `IMAGE_H / IMAGE_W` aspect ratio to scale footprint (assumes camera oriented so shorter dimension is along flight direction)
- Sets overlap to 0.0 (no overlap between strips)

When `_no_turn = False` (default):
- Uses full sensor width footprint
- 20% overlap between strips

The flag is always set to `True` in main.py. The name suggests it was intended for a mode where the drone flies straight without U-turns, but in practice it just changes the spacing calculation. The zigzag pattern is still generated regardless.

---

## 8. Does it do Bezier smoothing?

**Yes, the method exists:** `smooth_waypoints(waypoints, num_arc_points=3)` (line 193, static method).

It inserts quadratic Bezier arc points at each U-turn (odd-indexed waypoints = strip endpoints). For each turn, it generates `num_arc_points` interpolated points on a Bezier curve between the previous waypoint, the turn point, and the next waypoint.

**However: `smooth_waypoints()` is never called in main.py.** The raw zigzag waypoints are used directly. The drone navigates point-to-point without path smoothing.

---

## 9. Dry-run visualization in main.py

**Function:** `_dry_run(mission)` (line 830)

**What it does:**
1. Prints search polygon corners as GPS coordinates
2. Calls `mission.planner.generate_search_pattern(REAL_CANVAS_SIZE, REAL_CANVAS_SIZE, drone_gps)` with `drone_gps = (config.REF_LAT, config.REF_LON)`
3. Calculates total path distance and estimated time
4. Prints all waypoints with GPS coordinates
5. Loads `map.jpg` and draws:
   - Green polygon outline (search area)
   - Yellow circles + lines for waypoints/path
   - Red circle for first waypoint, blue for last
   - Yellow diamond for drone start position
   - Text overlay with stats
6. Saves to `dry_run_pattern.jpg`
7. Shows in window (if not headless)

**Key difference from normal mission:** Dry-run generates waypoints but does NOT:
- Call `filter_waypoints()` (but neither does the normal mission -- see section 6)
- Apply Bezier smoothing
- Draw the NFZ/SSSI polygon
- Show transit waypoints

---

## 10. Pattern generation pipeline summary

```
config.py                     planning.py                         main.py
─────────                     ───────────                         ───────
SEARCH_AREA_GPS ──(GPS→px)──> PathPlanner.__init__(geo, poly)
                                │
TARGET_ALT ──────────────────> generate_search_pattern()
SENSOR_WIDTH_MM ─────────────>   │
FOCAL_LENGTH_MM ─────────────>   ├─ rasterise polygon → binary mask
                                 ├─ minAreaRect → scan_angle
                                 ├─ rotate mask to axis-align
                                 ├─ compute strip_spacing_px
                                 ├─ scan horizontal strips (zigzag)
                                 ├─ un-rotate strip endpoints
                                 ├─ convert px → GPS waypoints
                                 └─ deduplicate
                                     │
                              list[(lat,lon)] ──────────────────> self.waypoints
                                                                  (NO NFZ filter)
                                                                  (NO Bezier smoothing)
```

---

## Visualizer implications

Any visualizer that wants to reproduce the exact same pattern must:

1. **Use the same GeoTransformer** (same REF_LAT, REF_LON, pix_per_m) to convert GPS polygon to pixel coordinates
2. **Use the same canvas size** -- `REAL_CANVAS_SIZE = 4800` for REAL mode, or `map_w x map_h` for SIMULATION
3. **Set `_no_turn = True`** (as main.py does) -- this changes overlap from 20% to 0% and scales footprint by aspect ratio
4. **Supply the correct `drone_gps`** -- this affects which corner the pattern starts from (closest to drone)
5. **Use the same config values**: `TARGET_ALT`, `SENSOR_WIDTH_MM`, `FOCAL_LENGTH_MM`, `IMAGE_W`, `IMAGE_H`
6. Optionally call `NFZGeofence.filter_waypoints()` to show the filtered pattern (main.py doesn't do this, but it should)
7. Optionally call `smooth_waypoints()` to show Bezier arcs (main.py doesn't do this either)

The simplest approach: instantiate `PathPlanner` with the same inputs and call `generate_search_pattern()` directly.
