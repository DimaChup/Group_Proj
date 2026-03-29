# SAR Search Pattern Research

> Compiled from IAMSAR Manual Vol. III, USCG Auxiliary references, academic UAV
> coverage path planning literature, and ArduPilot/Mission Planner documentation.

---

## 1. IAMSAR Standard Search Patterns

The International Aeronautical and Maritime Search and Rescue (IAMSAR) Manual,
Volume III (Mobile Facilities), defines **six standard search patterns**. These are
the internationally agreed patterns used by coast guards, navies, and civil aviation
worldwide.

| Pattern | Code | Best When | Datum Required? |
|---------|------|-----------|-----------------|
| Expanding Square | SS | Position known accurately, small area | Yes (precise) |
| Sector Search | VS | Position very accurately known, small object | Yes (very precise) |
| Track Line Search | TS | Object lost along known route | Route known |
| Parallel Track | PS | Large area, position uncertain | No |
| Creeping Line Ahead | CS | Large area with drift/current, narrow channels | No |
| Contour Search | — | Mountainous/valley terrain | No |

### 1.1 Expanding Square Search (SS)

**When to use:** The datum (most probable position of the target) is known within
close limits. The target has minimal drift. Single search unit.

**Procedure:**
1. Start at the datum position.
2. First leg oriented into the wind (reduces navigation error from drift).
3. All turns are **90 degrees to the right** (starboard).
4. Leg length increases by one track spacing (S) every **two legs**.

**Leg sequence (where S = track spacing):**
```
Leg 1: 1S  (North)
Leg 2: 1S  (East)    — turn 90 right
Leg 3: 2S  (South)   — turn 90 right
Leg 4: 2S  (West)    — turn 90 right
Leg 5: 3S  (North)   — turn 90 right
Leg 6: 3S  (East)    — turn 90 right
Leg 7: 4S  (South)   — turn 90 right
Leg 8: 4S  (West)    — turn 90 right
...
Leg n: ceil(n/2)*S
```

**Key formula:** The first leg length equals the track spacing S. Track spacing S
is set equal to the effective sweep width W for coverage factor C=1.

**Waypoint generation algorithm:**
```
Given: datum (lat, lon), track_spacing S, num_legs N, initial_heading H
directions = [H, H+90, H+180, H+270]  (cycle through)

current_pos = datum
for i in range(N):
    direction = directions[i % 4]
    leg_length = ((i // 2) + 1) * S
    next_pos = offset(current_pos, direction, leg_length)
    waypoints.append(next_pos)
    current_pos = next_pos
```

**Advantages:** Concentrates effort near datum where target is most likely.
**Disadvantages:** Requires precise navigation. Not suitable for multiple units
at the same altitude simultaneously.

**References:**
- [IAMSAR Search Patterns — MarineGyaan](https://marinegyaan.com/what-are-different-search-patterns/)
- [Water Surface Searches — Wikipedia](https://en.wikipedia.org/wiki/Water_surface_searches)
- [Expanding Square — USCG Auxiliary](https://www.uscgaux-ocnj.org/Navagation/Exanding%20Square%20Search.pdf)


### 1.2 Sector Search (VS — Victor Sierra)

**When to use:** Target position is very accurately known. Search area is small.
Useful when the target is a small object (person in water, life raft).

**Procedure:**
1. Deploy a datum marker (smoke float, beacon) at the estimated position.
2. First leg from datum in the direction of drift, length = search radius R.
3. Turn **120 degrees to starboard** at the end of each radial leg.
4. Return to datum, pass through, continue on next radial leg.
5. After three complete passes (covering 360 degrees), offset by **30 degrees**
   and repeat for a second sector if needed.

**Geometry:**
- The pattern forms a **spoked wheel** centered on the datum.
- First set of legs: 0, 120, 240 degrees (relative to drift direction).
- Second set: 30, 150, 270 degrees (offset 30 degrees).
- This is the **only circular search pattern** in IAMSAR.

**Search radius:**
- Aircraft: 5-20 NM (9-37 km).
- Vessels: 2-5 NM (3.7-9.3 km).
- Drones: typically 200m-2km depending on sensor.

**Drift compensation:** By steering toward the drifting datum marker every third
leg, the search vessel drifts the same amount as the datum.

**References:**
- [Sector Search — BrightHub Engineering](https://www.brighthubengineering.com/seafaring/41039-types-of-search-patterns-sector-search/)
- [MarineGyaan](https://marinegyaan.com/what-are-different-search-patterns/)


### 1.3 Track Line Search (TS)

**When to use:** An aircraft or vessel has disappeared along a known route with
no distress signal. The search follows the intended track.

**Two variants:**
- **TSR (Track Line Return):** Fly along the track, turn, return along a parallel
  offset track. Search both sides of the route.
- **TSN (Track Line Non-Return):** Single pass along the track and to both sides,
  then proceed to the next segment.

**Flight altitude:** 300-600m (1000-2000 ft) daytime, 600-900m (2000-3000 ft)
at night. Aircraft are commonly used due to the long distances involved.


### 1.4 Parallel Track Search (PS — Papa Sierra)

**When to use:** Large search area. Survivor location is uncertain. Works with
single or multiple search units. Most effective over water or flat terrain.

**Procedure:**
1. Define a rectangular (or polygonal) search area.
2. Fly/sail parallel tracks (search legs) across the area.
3. Track spacing S = effective sweep width W for coverage C=1.
4. **Search legs are parallel to the long axis** of the search area (major axis).
5. Cross-legs (turns connecting parallel legs) are short.
6. Direction of creep (progression across the area) is along the **short axis**.

**This is our current "lawnmower" / boustrophedon pattern.** It is the standard
pattern for area search when target location is unknown.

**Key distinction from Creeping Line:** In Parallel Track, the search legs run
parallel to the **long** (major) axis. In Creeping Line, the search legs run
parallel to the **short** (minor) axis, meaning the direction of "creep" is
along the long axis.

**Track spacing calculation:**
```
S = W  (for coverage factor C = 1)
S = W / C_desired  (to achieve higher coverage)

Where:
  W = effective sweep width (sensor-dependent)
  S = track spacing (distance between parallel legs)
```

**References:**
- [Water Surface Searches — Wikipedia](https://en.wikipedia.org/wiki/Water_surface_searches)
- [MarineGyaan](https://marinegyaan.com/what-are-different-search-patterns/)


### 1.5 Creeping Line Ahead (CS — Charlie Sierra)

**When to use:** Large area with known drift/current direction. Narrow bays or
channels constrained by shorelines. The legs run **across the current** and
progress is **against the flow** (into the drift).

**How it differs from Parallel Track:**
- Parallel Track: legs along major axis, creep along minor axis.
- Creeping Line: legs along **minor** axis (shorter legs, more turns), creep
  along the **major** axis (direction of drift).
- The key operational difference is that Creeping Line **aligns creep direction
  with drift**, so the search progresses into the area where the target is most
  likely drifting.

**Practical effect:** More back-and-forth turns but the pattern advances in the
direction that compensates for target drift, improving probability of detection
when current/wind is a factor.

**For our drone SAR mission:** Since we operate over land with no drift, Parallel
Track (our existing lawnmower) is the appropriate choice. Creeping Line would be
equivalent to rotating the lawnmower 90 degrees.

**References:**
- [NZ Coastguard Training Manual — Search Techniques](https://www.coastguard.net.nz/sartr/modules/Search%20Techniques.pdf)
- [Water Surface Searches — Wikipedia](https://en.wikipedia.org/wiki/Water_surface_searches)


### 1.6 Contour Search

**When to use:** Mountainous terrain or valleys where sharp elevation changes
make other patterns impractical.

**Procedure:**
1. Start from the highest peak.
2. Search from top to bottom — a new search altitude for each circuit.
3. Altitude intervals: 150-300m (500-1000 ft) between circuits.
4. For mountains: descending orbits around the mountain.
5. For valleys: circles, moving the center one track spacing after each circuit.
6. If the mountain cannot be circled, fly successive sweeps along its side at
   altitude intervals.

**Relevance to our project:** Not directly applicable to our flat-terrain SAR
mission, but the concept of "following the boundary inward" relates to spiral
search patterns.

---

## 2. Search Theory: Coverage and Detection

### 2.1 Fundamental Formulas

**Coverage Factor (C):**
```
C = (W * L) / A

Where:
  W = effective sweep width (metres)
  L = total track length (metres)
  A = area searched (square metres)
```

**Probability of Detection (POD) from coverage:**

For parallel tracks with uniform spacing:
```
POD = 1 - e^(-C)    (exponential detection function)
```

| Coverage C | POD |
|-----------|-----|
| 0.5 | 39% |
| 1.0 | 63% |
| 1.5 | 78% |
| 2.0 | 86% |
| 3.0 | 95% |

**Track Spacing (S) for desired coverage:**
```
S = W / C_desired

For C=1 (63% POD): S = W
For C=2 (86% POD): S = W/2  (double the tracks, half the spacing)
```

### 2.2 Effective Sweep Width for Drones

For a drone with a camera:
```
W_camera = 2 * altitude * tan(HFOV / 2)   (ground footprint width)
```

With overlap (e.g. 20%):
```
S = W_camera * (1 - overlap)
```

For our system:
```
Altitude = 35m, HFOV = 54.4 deg (Pi camera)
W_camera = 2 * 35 * tan(27.2 deg) = 2 * 35 * 0.514 = 36.0m
With 20% overlap: S = 36 * 0.8 = 28.8m
```

### 2.3 Conversion from Detection Range to Sweep Width

From field experiments (Koester et al., 2014):
- High visibility: W = 1.8 x detection_range
- Medium visibility: W = 1.6 x detection_range
- Low visibility: W = 1.1 x detection_range

**References:**
- [Theory of Search — USCG](https://navcen.uscg.gov/sites/default/files/pdf/Theory_of_Search.pdf)
- [SARBayes — Brief Intro to Search Theory](https://sarbayes.org/search-theory/a-brief-intro-to-search-theory-2-of-4/)
- [Koester et al. — Sweep Width Estimation](https://journals.sagepub.com/doi/full/10.1016/j.wem.2013.09.016)

---

## 3. Spiral / Contour-Following Pattern (Polygon Inward Offset)

### 3.1 Concept

A spiral search pattern follows the boundary of the search polygon inward,
creating concentric shrinking copies of the polygon at intervals equal to the
track spacing. The drone flies along each successive ring, moving toward the
center until the polygon collapses.

This is distinct from the IAMSAR "Expanding Square" (which is axis-aligned and
expands outward from a datum). A polygon spiral:
- Follows the actual shape of the search area (not just a square).
- Starts from the outside edge and works inward (or vice versa).
- Handles irregular, non-rectangular polygons naturally.

### 3.2 Inward vs Outward

**Inward spiral (outside to center):**
- Start at the polygon boundary, work inward.
- Advantages: covers the boundary first (useful if target is near edges),
  natural "shrinking" behavior, the drone ends near the center.
- Used by: Mission Planner's spiral survey tool, autonomous mower applications.

**Outward spiral (center to outside):**
- Start at a datum point, expand outward.
- Advantages: concentrates initial effort near the datum (like expanding square),
  natural for "expanding search from last known position."
- Used by: IAMSAR expanding square (axis-aligned variant).

**For SAR with no datum:** Inward spiral is preferred because there is no known
target position. The drone systematically covers the entire area boundary-first.

**For SAR with a datum:** Outward spiral (or expanding square) concentrates
effort where the target is most likely.

### 3.3 Algorithm: Polygon Inward Offset

The standard algorithm uses **polygon offset** (also called polygon erosion or
negative buffer):

```python
from shapely.geometry import Polygon

def generate_spiral_waypoints(polygon_coords, track_spacing):
    """Generate inward spiral waypoints for a polygon.

    Args:
        polygon_coords: list of (x, y) or (lon, lat) vertices
        track_spacing: distance between rings (metres or degrees)

    Returns:
        List of waypoints forming the spiral path
    """
    poly = Polygon(polygon_coords)
    rings = []
    offset = 0

    while True:
        # Negative buffer = inward offset
        shrunk = poly.buffer(-offset, join_style='mitre')

        if shrunk.is_empty:
            break

        # Handle MultiPolygon (can happen with complex shapes)
        if shrunk.geom_type == 'MultiPolygon':
            # Take the largest fragment
            shrunk = max(shrunk.geoms, key=lambda g: g.area)

        # Extract ring coordinates
        coords = list(shrunk.exterior.coords)
        rings.append(coords)

        offset += track_spacing

    # Connect rings into a continuous path
    waypoints = []
    for i, ring in enumerate(rings):
        if i % 2 == 0:
            waypoints.extend(ring)       # forward
        else:
            waypoints.extend(ring[::-1])  # reverse for continuity

    return waypoints
```

### 3.4 Key Implementation Details

**Corner handling (join_style):**
- `join_style='round'`: Rounds corners — produces smooth paths but adds extra
  waypoints. Better for fixed-wing aircraft that cannot turn sharply.
- `join_style='mitre'`: Preserves sharp corners — keeps polygon shape. Better
  for multirotors that can hover-turn.
- `join_style='bevel'`: Cuts corners at 45 degrees — compromise.

**When does the polygon collapse?**
The polygon becomes empty when the offset exceeds the **inradius** (radius of
the largest inscribed circle). For a polygon with area A and perimeter P:
```
max_offset ~ 2*A / P   (approximate inradius)
```

**Handling irregular polygons:**
- Convex polygons: always produce clean shrinking rings.
- Concave polygons: offset may split the polygon into **multiple fragments**
  (MultiPolygon). Handle by taking the largest fragment, or by processing all
  fragments separately.
- Very narrow polygons: may collapse to empty after just one or two rings.
  Fall back to a single-pass lawnmower for the remaining area.

**Waypoint placement:**
- **At corners only:** Minimum waypoints, but the drone must fly straight
  between them. Good for GPS-guided multirotors.
- **Sampled along edges:** Intermediate points every N metres along each edge.
  Better for smoother flight paths, especially on long edges.
- **Recommended:** Corners only for multirotors (ArduPilot handles straight
  segments between waypoints well). Add intermediate points only if edges
  exceed ~100m.

### 3.5 Connecting Rings

The naive approach (fly ring 0, then ring 1, then ring 2...) creates a
"jump" between rings where the drone must fly from the end of one ring to the
start of the next. Better approaches:

1. **Closest-point connection:** After completing ring N, find the closest
   point on ring N+1 and fly to it. Minimises dead travel.

2. **Continuous spiral:** Instead of discrete rings, interpolate between
   successive rings to create a true continuous spiral path. More complex
   but eliminates all dead segments.

3. **Corner-to-corner connection:** At one corner of each ring, step inward
   to the corresponding corner of the next ring. Simple and creates a
   natural spiral feel.

### 3.6 Ensuring Full Coverage

**Gap analysis:** The offset distance between successive rings should equal
the track spacing S (which equals the camera footprint width minus overlap).
If the polygon has acute angles, the inward offset near those angles shrinks
faster than S, potentially creating small uncovered triangles.

**Mitigation:**
- Use `join_style='mitre'` to preserve sharp corners.
- Set mitre_limit high enough to avoid premature corner truncation.
- Add a small overlap (e.g. 10%) to the track spacing.
- For acute corners, add extra waypoints at the corner apex.

### 3.7 Comparison: Spiral vs Lawnmower

| Aspect | Lawnmower (Parallel Track) | Spiral (Contour-Following) |
|--------|---------------------------|---------------------------|
| Coverage | Guaranteed complete | Complete if properly spaced |
| Path efficiency | Many 180-degree turns | Gradual turns, smoother path |
| Turn sharpness | Sharp U-turns at edges | Follows polygon angles |
| Edge coverage | Orthogonal to one edge | Parallel to all edges |
| Datum-centric | No (uniform coverage) | Can start from outside or center |
| Wind alignment | Can align with wind | Follows polygon shape |
| Implementation | Simpler | More complex (polygon offset) |
| ArduPilot support | Built-in (Survey Grid) | Available (Spiral Survey) |

**References:**
- [ArduPilot Discourse — Spiral Polygon Coverage](https://discuss.ardupilot.org/t/auto-way-point-generation-for-polygon-coverage-from-outside-to-center-for-autonomous-mower/29607)
- [Shapely buffer documentation](https://shapely.readthedocs.io/en/stable/reference/shapely.buffer.html)
- [Energy-Aware Spiral CPP — IEEE Xplore](https://ieeexplore.ieee.org/document/8411478/)
- [UAV Survey CPP of Complex Regions — arXiv](https://arxiv.org/abs/2411.07053)
- [Survey on CPP with UAVs — MDPI Drones](https://www.mdpi.com/2504-446X/3/1/4)
- [Efficient CPP for UAV in Concave Regions — Nature](https://www.nature.com/articles/s41598-025-20978-8)

---

## 4. Expanding Square: Detailed Waypoint Generation

### 4.1 Step-by-Step Algorithm

```python
import math

def generate_expanding_square(datum_lat, datum_lon, track_spacing_m,
                                num_legs, initial_heading_deg=0):
    """Generate expanding square waypoints from a datum point.

    Args:
        datum_lat, datum_lon: center point (GPS)
        track_spacing_m: distance between tracks (= first leg length)
        num_legs: total number of legs
        initial_heading_deg: first leg heading (0=North, into wind preferred)

    Returns:
        List of (lat, lon) waypoints
    """
    waypoints = [(datum_lat, datum_lon)]
    current_lat = datum_lat
    current_lon = datum_lon

    for i in range(num_legs):
        # Heading rotates 90 deg clockwise each leg
        heading = (initial_heading_deg + 90 * i) % 360

        # Leg length: increases by S every 2 legs
        leg_length = ((i // 2) + 1) * track_spacing_m

        # Convert to GPS offset
        d_lat = leg_length * math.cos(math.radians(heading)) / 111320.0
        d_lon = (leg_length * math.sin(math.radians(heading)) /
                 (111320.0 * math.cos(math.radians(current_lat))))

        current_lat += d_lat
        current_lon += d_lon
        waypoints.append((current_lat, current_lon))

    return waypoints
```

### 4.2 Coverage Area

After N legs, the expanding square covers approximately:
```
A_covered = ((N/2)^2) * S^2   (for large N)
Total track length = sum of all leg lengths
```

For N=20 legs at S=30m: covers roughly 90,000 m^2 (300m x 300m square).

---

## 5. Sector Search: Detailed Waypoint Generation

### 5.1 Step-by-Step Algorithm

```python
def generate_sector_search(datum_lat, datum_lon, radius_m,
                           drift_heading_deg=0, num_sectors=2):
    """Generate sector search waypoints.

    Args:
        datum_lat, datum_lon: center point
        radius_m: search radius from datum
        drift_heading_deg: direction of drift (first leg heading)
        num_sectors: 1 = three legs (0/120/240), 2 = add 30/150/270

    Returns:
        List of (lat, lon) waypoints
    """
    waypoints = []
    angles = []

    # First sector: legs at 0, 120, 240 degrees relative to drift
    for i in range(3):
        angles.append(drift_heading_deg + i * 120)

    # Second sector: offset 30 degrees
    if num_sectors >= 2:
        for i in range(3):
            angles.append(drift_heading_deg + 30 + i * 120)

    for angle in angles:
        heading = angle % 360
        # Go out to radius
        d_lat = radius_m * math.cos(math.radians(heading)) / 111320.0
        d_lon = (radius_m * math.sin(math.radians(heading)) /
                 (111320.0 * math.cos(math.radians(datum_lat))))

        waypoints.append((datum_lat, datum_lon))  # return to datum
        waypoints.append((datum_lat + d_lat, datum_lon + d_lon))  # radial end

    waypoints.append((datum_lat, datum_lon))  # final return to datum
    return waypoints
```

---

## 6. Pattern Selection Guide (for our SAR drone)

### When to use each pattern:

| Scenario | Best Pattern | Why |
|----------|-------------|-----|
| **No idea where target is** (our default) | Parallel Track (Lawnmower) | Uniform coverage of entire area |
| **PLB/beacon signal received** (approximate location known) | Expanding Square | Concentrates effort near datum |
| **Target spotted once, lost** (precise location known) | Sector Search | Thorough coverage of small area around last sighting |
| **Want "cinematic" coverage** (visual appeal, smooth flight) | Inward Spiral | Follows polygon boundary, fewer sharp turns |
| **Narrow/elongated area** | Creeping Line | Short legs across narrow dimension |
| **Mountainous terrain** | Contour Search | N/A for our flat-terrain mission |

### Recommended implementation priority:

1. **Parallel Track (Lawnmower)** — DONE (planning.py, works well)
2. **Expanding Square** — HIGH priority. Simple to implement. Useful when beacon
   signal gives approximate datum. Just 20 lines of code.
3. **Inward Spiral** — MEDIUM priority. More visually interesting, smoother path.
   Uses Shapely polygon.buffer(-offset). Maybe 50 lines of code.
4. **Sector Search** — LOW priority. Only useful after visual sighting. Simple
   geometry (radial legs at 120 degree intervals).

---

## 7. Implementation Notes for Our System

### 7.1 Coordinate System Considerations

All patterns generate waypoints in GPS (lat, lon). The conversion between
metres and degrees depends on latitude:
```
1 degree latitude  ~ 111,320 m  (constant)
1 degree longitude ~ 111,320 * cos(latitude) m  (varies with latitude)

At Bristol (51.4N): 1 deg lon ~ 69,660 m
```

### 7.2 Integration with planning.py

The existing `PathPlanner` class generates lawnmower patterns using a
pixel-based approach (rasterize polygon, rotate, scan). For new patterns:

- **Expanding Square and Sector Search** work directly in GPS coordinates
  (no need for pixel conversion). They are datum-centric, not polygon-based.
- **Spiral** can use either:
  - Shapely on GPS coordinates (simpler, more accurate, but needs Shapely).
  - Pixel-based polygon offset (consistent with existing code, but less precise
    due to rasterization).

**Recommendation:** Use Shapely for the spiral pattern. We already use it for
NFZ clipping, so it is a known dependency.

### 7.3 Strip Width / Track Spacing for Our System

```python
# Camera ground footprint at search altitude
alt = 35  # metres
hfov = 54.4  # degrees (Pi camera, calibrated)
footprint_w = 2 * alt * math.tan(math.radians(hfov / 2))  # = 36.0m

# Track spacing with 20% overlap
overlap = 0.20
track_spacing = footprint_w * (1 - overlap)  # = 28.8m

# For expanding square / spiral
# Use track_spacing as S
```

---

## 8. Academic References (UAV Coverage Path Planning)

1. Torres et al., "Survey on Coverage Path Planning with Unmanned Aerial
   Vehicles," *Drones*, 3(1), 4, 2019.
   [MDPI](https://www.mdpi.com/2504-446X/3/1/4)

2. Di Franco & Buttazzo, "Energy-Aware Spiral Coverage Path Planning for UAV
   Photogrammetric Applications," *IEEE Robotics and Automation Letters*, 2018.
   [IEEE Xplore](https://ieeexplore.ieee.org/document/8411478/)

3. Li et al., "UAV Survey Coverage Path Planning of Complex Regions Containing
   Exclusion Zones," *arXiv*, 2411.07053, 2024.
   [arXiv](https://arxiv.org/abs/2411.07053)

4. Chen et al., "An Efficient Coverage Path Planning Method for UAV in Complex
   Concave Regions," *Scientific Reports*, 2025.
   [Nature](https://www.nature.com/articles/s41598-025-20978-8)

5. Cabreira et al., "Optimal Polygon Decomposition for UAV Survey Coverage Path
   Planning in Wind," *Sensors*, 18(7), 2132, 2018.
   [MDPI](https://www.mdpi.com/1424-8220/18/7/2132)

6. Koester et al., "Use of the Visual Range of Detection to Estimate Effective
   Sweep Width for Land SAR," *Wilderness & Environmental Medicine*, 25(1), 2014.
   [SAGE](https://journals.sagepub.com/doi/full/10.1016/j.wem.2013.09.016)

7. IAMSAR Manual, Volume III — Mobile Facilities, 2016 Edition.
   [PDF](https://maritimesafetyinnovationlab.org/wp-content/uploads/2021/02/Doc.9731-EN-IAMSAR-Manual.pdf)

8. USCG Auxiliary — Coxswain SAR Reference Guide.
   [PDF](https://rdept.cgaux.org/documents/CoxswainSAR-ReferenceGuide.pdf)

9. SARBayes — Brief Introduction to Search Theory.
   [Web](https://sarbayes.org/search-theory/a-brief-intro-to-search-theory-2-of-4/)

10. CGAL — 2D Straight Skeleton and Polygon Offsetting.
    [Docs](https://doc.cgal.org/latest/Straight_skeleton_2/index.html)

---

## 9. Summary of Key Findings

1. **Our existing lawnmower (Parallel Track) is the correct IAMSAR pattern**
   for area search with no datum. It is the standard pattern used worldwide.

2. **Expanding Square is simple to add** (~20 lines) and valuable when a PLB
   beacon narrows the search area. Just spiral outward from the datum with
   90-degree turns and increasing leg lengths.

3. **Inward spiral uses polygon.buffer(-offset)** from Shapely. Generate
   successively smaller copies of the search polygon, extract their boundary
   coordinates, and connect them into a continuous path. Handles arbitrary
   polygon shapes. Use `join_style='mitre'` for multirotors.

4. **Track spacing = camera footprint * (1 - overlap).** For our system at
   35m altitude: S = 28.8m. This gives coverage factor C=1 (63% POD per pass).

5. **Coverage factor C = (W * L) / A.** POD = 1 - e^(-C). Double the tracks
   (C=2) gives 86% POD. Diminishing returns after that.

6. **Creeping Line vs Parallel Track** is just a rotation of the pattern to
   align with drift direction. Over land with no drift, they are equivalent.

7. **Sector Search** is a specialised pattern for re-searching a small area
   around a known sighting. Six radial legs at 120-degree intervals, passing
   through the datum each time.

8. **For the spiral specifically:**
   - Start from outside, go IN (no datum assumption).
   - Waypoints at polygon corners only (multirotors handle straight segments).
   - Strip spacing = track spacing = camera footprint width minus overlap.
   - Connect rings at closest points to minimise dead travel.
   - Concave polygons may fragment — take the largest piece at each offset.
   - Polygon collapses when offset exceeds ~2*Area/Perimeter.
