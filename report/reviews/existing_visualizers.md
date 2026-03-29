# Existing Visualization Code Review

What can `pattern_visualizer.py` reuse from the codebase?

---

## 1. main.py `_dry_run()` (lines 830-903)

**What it does**: Generates a lawnmower pattern and renders it on map.jpg with OpenCV. Static image, no interactivity (just `cv2.waitKey(0)` to pause).

**Visualization elements drawn**:
- Green polygon outline: `cv2.polylines(vis, [np.array(mission.search_poly)], True, (0,255,0), 2)`
- Cyan waypoints: `cv2.circle(vis, pt, 4, color, -1)` — red for first, blue for last, cyan for middle
- Yellow path lines connecting waypoints: `cv2.line(vis, prev, pt, (255,255,0), 1)`
- Yellow diamond for drone start: `cv2.drawMarker(vis, dp, (0,255,255), MARKER_DIAMOND, 15, 2)`
- Green text overlay with stats: WP count, total distance, estimated time

**Reusable pieces**:
- Color scheme (green polygon, cyan WPs, yellow path, diamond drone marker)
- Text overlay format: `"DRY-RUN: {N} WPs, {dist}m, ~{time}min"`
- Distance calculation: `111320 * sqrt((dlat)^2 + (dlon*cos(lat))^2)`
- Transit distance + search distance + total time formula
- Scale-to-fit: `scale = min(1.0, 900 / vis.shape[0])`

**What's missing** (pattern_visualizer needs to add):
- Interactive controls (zoom, pan, altitude slider, angle rotation)
- NFZ overlay
- Camera swath visualization
- Multiple strategy comparison
- Transit path from takeoff

---

## 2. `analysis/path_simulation.py` (420 lines)

**What it does**: Compares 4 search strategies (lawnmower, rotated 90-deg, spiral, alt-start) at 2 altitudes (35m, 50m). Outputs matplotlib bar charts + pattern overlays. Non-interactive (saves PNGs).

**Visualization elements**:
- Polygon plotted in local metres (GPS-to-local conversion): `gps_to_local(p)` using lat/lon scale factors
- Path plotted as colored line on polygon: `ax.plot(wxs, wys, "-", color=..., linewidth=0.8)`
- Green circle for start, red square for end
- Gray polygon fill with black outline
- Bar chart comparison of metrics (distance, turns, time, energy, coverage)
- Coverage estimation via cv2 mask intersection (swath drawn as thick line)

**Reusable pieces**:
- `gps_distance()` — Haversine distance (lines 36-43)
- `path_length()` — total path distance (lines 47-51)
- `count_turns()` — direction changes > 30 deg (lines 54-72)
- `polygon_area_m2()` — Shoelace formula (lines 75-89)
- `estimate_coverage()` — swath mask intersection with polygon mask (lines 92-118)
- `energy_joules()` — hover + drag energy model (lines 132-140)
- Strategy generators: `strategy_lawnmower`, `strategy_lawnmower_rotated`, `strategy_spiral`, `strategy_random_start` (lines 157-205)
- GPS-to-local-metres plotting convention (East-North axes in metres)

**What's missing**:
- Interactivity (all static matplotlib with `Agg` backend)
- NFZ overlay and slow-zone visualization
- Camera footprint rectangles
- Real-time parameter adjustment

---

## 3. `analysis/path_optimization/optimize_path.py` (~800 lines)

**What it does**: Sweeps altitude x scan-angle grid, computes energy/time/coverage metrics with NFZ slowdown modelling. Generates 6 publication-quality matplotlib plots. Non-interactive.

**Visualization elements**:
- Plot 1: Energy vs Altitude (line chart, with/without NFZ shading)
- Plot 2: Time vs Altitude (same format)
- Plot 3: Optimal scan angle vs altitude (bar chart)
- Plot 4: Scan lines vs altitude (dual-axis with swath width)
- Plot 5: Energy heatmap (altitude x angle, viridis colormap, red star at optimum)
- Plot 6: Survey area overview + optimal lawnmower pattern with:
  - Blue polygon fill, black outline
  - Red SSSI/NFZ fill with dashed buffer zone
  - Green triangle for takeoff
  - Cool-colormap scan lines (color shows progression)
  - Dashed U-turn connections

**Reusable pieces**:
- `gps_to_local()` / `polygon_gps_to_local()` — coordinate conversion (lines 89-99)
- `polygon_area()` — Shoelace (lines 106-114)
- `rotate_points()` — rotate polygon for scan angle (lines 117-126)
- `point_to_polygon_dist()` — min distance to polygon edges (lines 129-151)
- `point_in_polygon()` — ray-casting test (lines 154-165)
- `segment_nfz_time()` — time with NFZ speed ramp (lines 168-211)
- `camera_footprint()` — ground width/height/swath from altitude (lines 218-227)
- `generate_lawnmower()` — pure-geometry lawnmower (no cv2), scan-line intersection with rotated polygon (lines 234-308)
- `compute_path_metrics()` — full metrics including NFZ time penalty (lines 311-420)
- NFZ buffer zone drawing technique (offset vertices outward from centroid)
- Color-mapped scan lines: `plt.cm.cool(np.linspace(0, 1, len(segments)))`

**This is the richest source of reusable code.** The pure-geometry `generate_lawnmower()` and `compute_path_metrics()` are exactly what pattern_visualizer needs for angle sweeping and metric calculation.

---

## 4. `tests/flight/draw_search_area.py`

**Does not exist.** Referenced in MEMORY.md but the file is missing. Cannot reuse.

---

## 5. `planning.py` — PathPlanner class

**What it does**: The actual flight planner used by main.py. Generates lawnmower and spiral patterns using cv2 mask rasterization + rotation.

**Key methods**:
- `generate_search_pattern()` — lawnmower via rotated binary mask scanning
- `generate_spiral_pattern()` — rectangular inward spiral
- Both return GPS waypoints `[(lat, lon), ...]`

**Reusable**: Use PathPlanner directly for generating patterns at different altitudes/angles, just like path_simulation.py and dry-run do. The `alt_override` parameter already exists.

---

## Summary: What to Reuse

| Component | Source | How to reuse |
|-----------|--------|-------------|
| Pattern generation | `planning.py` PathPlanner | Import directly, call with `alt_override` |
| GPS-to-local-metres | `optimize_path.py` lines 89-99 | Copy or import |
| Pure-geometry lawnmower | `optimize_path.py` lines 234-308 | Import for angle-sweep without cv2 masks |
| Metrics (distance, turns, time, energy, coverage) | `optimize_path.py` + `path_simulation.py` | Import functions |
| NFZ distance/time modelling | `optimize_path.py` lines 129-211 | Import |
| Camera footprint calc | `optimize_path.py` lines 218-227 | Import |
| Color scheme | `main.py` dry-run | Match colors: green polygon, cyan WPs, yellow path |
| Map background | `main.py` dry-run | Load map.jpg, use GeoTransformer for GPS-to-pixel |
| Polygon data | `config.py` SEARCH_AREA_GPS, SSSI_GPS, TAKEOFF_GPS | Import config |
| Focus area polygon | `flight_plans/focus_area.json` | Load JSON |

**Recommended approach**: The pattern_visualizer should combine:
1. **optimize_path.py's pure-geometry engine** (angle sweep, metrics, NFZ modelling) for the computation layer
2. **main.py dry-run's OpenCV rendering** (map background, color scheme, overlays) for the display layer
3. **matplotlib interactive mode** (instead of Agg) or **cv2 trackbars** for the interactive controls (altitude slider, angle slider, strategy selector)

The key gap in all existing code: none of it is interactive. Everything either shows a static image or saves PNGs. The pattern_visualizer's main value-add is making these parameters adjustable in real time.
