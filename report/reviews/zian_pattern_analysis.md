# Zian's Path Planning Code Analysis

## Directory Structure

Zian has three versions of her code, representing an evolution:

1. **`Zian/herish_code_v1/`** -- Early waypoint generator (Herish's original code adapted)
2. **`Zian/path_planner/`** -- Standalone path planning library (the core algorithms)
3. **`Zian/sarFlightDay1V2/`** -- Integrated state machine with pattern generation (flight-ready)
4. **`Zian/stateMachine-with pp codes/`** -- Earlier integrated version (superseded by sarFlightDay1V2)

The path planning library (`path_planner/`) contains the mature, well-documented algorithms.
The `sarFlightDay1V2/` version wraps a simpler `pattern_generator.py` for actual flight use.

---

## Two Pattern Types

Zian implements **two** search pattern algorithms and compares them:

### 1. Lawnmower (Boustrophedon)

**File:** `Zian/path_planner/lawnmower_planner.py` (405 lines)

**Algorithm (called "Algorithm 0"):**
1. Inset the search polygon by `HALF_SWATH` to form the survey boundary (camera centreline stays at least HALF_SWATH inside perimeter)
2. Rotate the inset polygon by `-HEADING_DEG` so scan lines run horizontally
3. Generate horizontal scan lines at intervals of `SWATH` from top edge to bottom edge
4. Clip each scan line against the inset polygon to find left/right endpoints
5. Join consecutive lines in alternating direction (serpentine) -- east-to-west, then west-to-east
6. Between consecutive scan lines, follow the polygon boundary (not straight cuts) to preserve edge coverage
7. Rotate all points back and convert to (lat, lon)

**Key detail -- boundary-following transitions:** Between scan lines, instead of cutting diagonally inside the polygon, the path follows the inset polygon boundary. This is computed via `_boundary_path()` which finds the shorter of the two possible boundary routes (forward or backward around the polygon). This preserves edge coverage that would be lost with direct diagonal transitions.

**Final leg:** After all scan lines, the path follows the inset boundary to end at the inset vertex closest to P1 (SE corner).

### 2. Perimeter Spiral (Inward Spiral)

**File:** `Zian/path_planner/perimeter_planner.py` (703 lines)

**Algorithm:**
1. Start with the original polygon (5-vertex pentagon from KML)
2. For each lap k, inset the polygon by `offset_k = HALF_SWATH + k * SWATH`
3. Compute waypoints at the intersection of consecutive inset edge lines
4. **Edge-degeneration rule:** Before each lap, check if any edge has collapsed (length <= 0). Collapsed edges are removed, reducing the polygon (pentagon -> quad -> triangle...)
5. Each lap is emitted starting from the vertex nearest P3 (north), flying CCW: P3 side -> P4 side -> P0P1 -> P1P2 -> P2P3
6. **Crossing check:** Each new segment is checked against all previous survey segments. If a crossing is detected, the spiral terminates
7. **Proximity stop:** When P3P4-inset and P1P2-inset gap < SWATH, the current lap completes and the spiral ends (avoids overlapping inner laps)
8. Final waypoint is the polygon centroid (unless proximity-stopped)

**Polygon degeneration detail:** The pentagon naturally degrades as the spiral goes inward. The P4-P0 edge (shortest at 37.82m) collapses first, reducing the working polygon from 5 to 4 vertices. The code never reduces below a quad (4 vertices) because triangle insets produce numerically unstable corners.

---

## Search Area Definition

**File:** `Zian/path_planner/search_area.py` (126 lines)

The search area is the KML "Survey Area" polygon -- a convex pentagon with 5 vertices in CCW order:

| Vertex | Position | Description |
|--------|----------|-------------|
| P0 | 51.42326957, -2.67094835 | SW vertex |
| P1 | 51.42287025, -2.67004543 | SE vertex (southernmost) |
| P2 | 51.42336623, -2.66816930 | E vertex |
| P3 | 51.42421477, -2.66880977 | N vertex (northernmost) |
| P4 | 51.42354070, -2.67127778 | NW vertex |

**Geometry:**
- Side lengths: P0-P1=76.75m, P1-P2=141.29m, P2-P3=104.28m, P3-P4=186.82m, P4-P0=37.82m
- Perimeter: 546.97m
- Area: 17,379.2 m^2 (1.74 ha)
- Centroid computed via shoelace formula in local flat-Earth XY projection

These are the same coordinates as our KML (AENGM0074.kml).

---

## Parameters

### Path Planner Library (`path_planner/`)

| Parameter | Value | Description |
|-----------|-------|-------------|
| `HALF_SWATH` | 5.5 m | Half camera footprint width |
| `SWATH` | 11.0 m | Full swath = scan line spacing |
| `HEADING_DEG` | 0.0 | Scan line orientation (0 = E-W lines) |
| `ENTER_OFFSET_M` | 10.0 m | Enter point offset east of P3 |
| `TAKEOFF_LAT/LON` | 51.42340640, -2.67144603 | Take-off location (reference only) |

### Integrated Flight Code (`sarFlightDay1V2/config.py`)

| Parameter | Value | Description |
|-----------|-------|-------------|
| `SWATH_WIDTH_M` | 10 m | Spacing between scan lines |
| `SEARCH_ALT_M` | 30 m | Search altitude AGL |
| `SCAN_HEADING_DEG` | 0 | E-W scan lines |
| `FLIGHT_DAY_SIMPLE` | True | Uses square box for flight day 1 |
| `SQUARE_BOX_SIDE_M` | 30 m | Side length of test box |
| `WP_SPEED_SECOND_PASS_MPS` | 2.0 m/s | Speed for second search pass |

Note: The flight code (`sarFlightDay1V2`) was set to `FLIGHT_DAY_SIMPLE = True` for flight day 1, meaning it uses a predefined 30x30m square box pattern instead of the full lawnmower. The full lawnmower is the fallback when `FLIGHT_DAY_SIMPLE = False`.

---

## NFZ/SSSI Handling

Zian's code **does NOT clip or avoid the SSSI/NFZ in the path planner itself**. Instead:

1. **`kml_parser.py`** parses the SSSI polygon from the KML file
2. **`states/upload_fence.py`** uploads the Flight Area as an inclusion fence and the SSSI as an exclusion fence to the Cube autopilot
3. ArduPilot enforces the geofence at the autopilot level (`FENCE_ACTION = 1 = RTL on breach`)
4. The search pattern is generated purely from the Survey Area polygon without NFZ awareness

This means the lawnmower pattern could theoretically generate waypoints inside the SSSI, but ArduPilot would refuse to fly there (RTL on fence breach). In practice, the Survey Area polygon does not overlap the SSSI, so this is not an issue for this site.

**Fence parameters in config.py:**
- `FENCE_ENABLE_VALUE = 0` (disabled by default -- toggled on during flight)
- `FENCE_TYPE_VALUE = 4` (polygon inclusion/exclusion fences)
- `FENCE_ACTION_VALUE = 1` (RTL on breach)
- `FENCE_ALT_MAX_VALUE = 50` (50m max altitude)
- `FENCE_MARGIN_VALUE = 2` (2m buffer inside fence boundary)

---

## Coordinate System

**File:** `Zian/path_planner/geo_utils.py` (47 lines)

Uses flat-Earth approximation:
- `_DEG_LAT_M = 111,195 m/deg` (constant)
- `deg_lon_m(lat)` = latitude-corrected meters per degree longitude
- Haversine function for distance calculations
- All planning done in local East/North (x,y) metres relative to polygon centroid, then converted back to (lat,lon)

---

## PLB (Personal Locator Beacon) Search

**File:** `Zian/path_planner/PLB_searching.py` (534 lines)

A separate module for PLB-triggered re-search:
1. Generates a random convex polygon (3-10 vertices) inside the search area to simulate a PLB signal area
2. Picks a random UAV start point inside the search area
3. Plans a mission to fly from start to PLB area and search using either:
   - Mode 0: Lawnmower (same algorithm as above, applied to PLB polygon)
   - Mode 1: Perimeter spiral (concentric inward rings around PLB polygon)

The PLB planner is self-contained with its own implementations of inset, scanline clipping, and spiral generation -- slightly simpler versions without boundary-following transitions.

---

## Comparison Results (at HALF_SWATH = 5.5m, SWATH = 11.0m)

From `path_planner/comparison.txt`:

| Metric | Perimeter Spiral | Lawnmower |
|--------|-----------------|-----------|
| Waypoints (excl. enter) | 20 | 29 |
| Total distance (m) | 1540.6 | 1567.6 |

The perimeter spiral is slightly shorter (27m less) and uses fewer waypoints. Both use the same HALF_SWATH=5.5m, SWATH=11.0m parameters.

### Swath Sweep Experiment

`sweep_half_swath_outputs.py` sweeps HALF_SWATH from 2.0 to 12.5m (step 0.5m) and generates outputs for each value in `outputs/<SWATH>/`. This produces 22 comparison folders with waypoint files, comparison tables, and preview images.

`plot_swath_continuous_comparison.py` generates synthetic data (NOT real planner output) showing distance vs spacing curves with noise -- this is for visualization/report purposes, not actual measurements.

---

## Visualization

`simulate.py` generates a side-by-side matplotlib plot (`mission_preview.png`) showing both algorithms on the search area polygon. Each plot shows:
- Original boundary (dashed black)
- Corner labels (P0-P4)
- UAV flight path with waypoints
- Enter point, takeoff location, centroid
- Lap-0 inset polygon (for spiral)

---

## Integrated Flight Code (`sarFlightDay1V2/`)

The flight-ready version has a simpler `pattern_generator.py` with two functions:

1. **`generate_square_box()`** -- Simple 4-corner box for flight day testing (NW->NE->SE->SW->NW)
2. **`generate_lawnmower()`** -- Same boustrophedon algorithm but without:
   - No polygon inset (scans start at y_min + spacing/2)
   - No boundary-following transitions (direct connections between scan lines)
   - No enter/exit waypoint logic

The state machine flow is:
```
IDLE -> GENERATE_PATTERN -> IDLE (preview) -> UPLOAD_MISSION -> SEARCH
```

`generate_pattern.py` (state) calls `pattern_generator.generate_lawnmower()` with the KML Search Area polygon, `SWATH_WIDTH_M=10`, `SEARCH_ALT_M=30`, `SCAN_HEADING_DEG=0`. It renders a preview image for operator confirmation before uploading.

The SEARCH state supports:
- Two-pass searching (pass 1 at normal speed, pass 2 at 2.0 m/s)
- PLB button (triggers re-plan to PLB area)
- Cancel mission
- RC override detection and graceful pause
- Waypoint progress tracking via MAVLink MISSION_CURRENT/MISSION_ITEM_REACHED

---

## Key Differences from Our Implementation (v3/planning.py)

| Aspect | Zian's Code | Our Code (v3/planning.py) |
|--------|-------------|--------------------------|
| Pattern types | Lawnmower + Perimeter Spiral | Lawnmower only |
| Polygon inset | Yes (HALF_SWATH inset before scanning) | Yes (camera footprint inset) |
| Scan line transitions | Boundary-following (library) / Direct (flight code) | Direct |
| NFZ handling | Autopilot fence enforcement only | Software geofence + Shapely clipping |
| Scan heading | Configurable (default 0 = E-W) | Configurable |
| Enter/exit logic | Enter 10m east of P3, exit at P1 inset vertex | From takeoff location |
| Two-pass search | Yes (pass 2 at 2.0 m/s) | No |
| PLB re-search | Yes (random polygon, mode 0 or 1) | Beacon redirect (--beacon-delay) |
| Swath parameter sweep | Yes (2.0-12.5m sweep with outputs) | No |
| Algorithm comparison | Side-by-side spiral vs lawnmower | N/A |
| Coordinate system | Flat-Earth, centroid-relative | Flat-Earth, centroid-relative |
| Search area source | KML parser | config.py SEARCH_AREA_GPS / interactive drawing |

---

## Notable Code Quality

- Well-documented with docstrings and algorithm descriptions
- Clean separation: geo_utils, search_area, planners, generators are independent modules
- Robust degeneration handling in perimeter spiral (pentagon -> quad transition)
- Crossing checks prevent self-intersecting spiral paths
- Proximity stop prevents overlapping inner laps
- Comprehensive swath sweep tooling for parameter optimization
- KML parser is clean and handles name variations robustly
- State machine has proper two-pass search with speed reduction
