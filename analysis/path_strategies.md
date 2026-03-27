# Search Path Strategies -- Comparative Analysis

SAR drone path planning for the AENGM0074 survey area (University of Bristol MSc).
Compares six candidate strategies against the implemented lawnmower pattern.

---

## Survey Area Parameters

| Parameter | Value |
|-----------|-------|
| Polygon | 5-corner irregular (from AENGM0074.kml) |
| Lat span | ~150 m |
| Lon span | ~216 m |
| Approx area | ~32,200 m^2 (3.2 ha) |
| Altitude (default) | 35 m (TARGET_ALT), 50 m recommended for initial sweep |
| Camera swath at 35 m | 25.7 m (with 20% overlap) |
| Camera swath at 50 m | 36.8 m (with 20% overlap) |
| Speed at 35 m | 8.0 m/s (altitude-dependent linear) |
| Speed at 50 m | 10.0 m/s |
| Adjacent constraint | SSSI no-fly zone on the northeast edge (7-corner polygon) |
| Drone | Quadcopter, ~150 W hover, ~206 ms CV inference (4.8 FPS) |

---

## 1. Lawnmower / Boustrophedon (Current Implementation)

### How It Works

Parallel scan lines aligned to the polygon's longest edge (auto-computed via
`cv2.minAreaRect`). The drone flies back and forth, reversing direction at each
edge. 20% overlap between adjacent swaths guarantees no coverage gaps.

```
  Start
    |
    v
    +----------------------------------->  line 1
                                          |
    <-----------------------------------+  line 2
    |
    +----------------------------------->  line 3
                                          |
    <-----------------------------------+  line 4
    |
    +----------------------------------->  line 5
                                          |
    <-----------------------------------+  line 6
                                        End
```

### Implementation Details

`planning.py` rasterises the polygon onto a binary mask, rotates the mask so scan
lines align with the longest axis, then reads non-zero pixel runs from each row.
The planner auto-selects the start corner closest to the drone and optimises scan
direction (left-to-right vs right-to-left) to minimise transit distance.

Bezier curve smoothing (`smooth_waypoints()`) inserts 3 arc points at each U-turn
to reduce deceleration penalty.

### Estimates for Our Polygon

| Altitude | Scan lines | Path length | Time | Energy |
|----------|-----------|-------------|------|--------|
| 35 m | ~6 | ~1,250 m | ~2.6 min | ~12.6 Wh |
| 50 m | ~4-6 | ~876 m | ~1.5 min | ~8.3 Wh |

### Pros

- **Guaranteed complete coverage** -- every point in the polygon is visited.
  Mathematically provable given swath width and overlap.
- **Simple and predictable** -- easy to verify, debug, and explain to operators.
  Standard in SAR literature (JSAR Manual, IMO IAMSAR Vol III).
- **Scan angle optimisation** -- auto-aligns to the polygon's longest axis,
  minimising the number of turns. Our analysis tested 216 configurations (6
  altitudes x 36 angles) to confirm the optimal angle.
- **NFZ-aware** -- the speed scalar field and repulsive push integrate naturally
  with parallel scan lines (the drone simply slows near the SSSI boundary).
- **Handles arbitrary polygons** -- the rasterisation approach (cv2.fillPoly +
  row scanning) works on convex and concave shapes, irregular boundaries, and
  polygons with narrow protrusions.

### Cons

- **U-turn penalty** -- each reversal requires deceleration to ~0, turn, and
  reacceleration. With Bezier smoothing this costs ~2 seconds per turn. For 6
  scan lines that is 5 turns = ~10 seconds overhead.
- **Edge inefficiency** -- at polygon edges the scan line may be very short
  (narrow strips). The drone spends time turning for minimal additional coverage.
- **No prioritisation** -- every part of the polygon is searched with equal
  probability. No ability to search "more likely" areas first.
- **Long transit at start** -- if the takeoff point is far from the first scan
  line, transit time is wasted. (Mitigated by closest-corner start selection.)

### When It Is the Best Choice

- No prior information about target location.
- Regulatory or procedural requirement for complete area coverage.
- Irregular polygon shape (concave, multi-sided).
- Adjacent NFZ requiring predictable, controllable flight paths.

---

## 2. Spiral Inward

### How It Works

Start from the polygon perimeter and trace progressively smaller concentric
rectangles (or polygon offsets) toward the centre. Each ring inward is spaced by
one swath width.

```
    +-----------------------------------+
    |  +-----------------------------+  |
    |  |  +-----------------------+  |  |
    |  |  |  +-----------------+  |  |  |
    |  |  |  |                 |  |  |  |
    |  |  |  +-----------<----+  |  |  |
    |  |  +-------->---------+   |  |  |
    |  +---<-----------------+   |  |  |
    +------->--------------------+  |  |
    +---<---------------------------+  |
    +--->-------------------------------+
  Start
```

### Implementation

`planning.py` already contains `generate_spiral_pattern()`. It uses the same
rotated-mask approach as the lawnmower, but walks the bounding rectangle edges
inward (top->right->bottom->left, shrinking each ring by one swath step).

### Estimates for Our Polygon

| Altitude | Rings | Path length | Time | Energy |
|----------|-------|-------------|------|--------|
| 35 m | ~3 | ~1,350 m | ~2.8 min | ~13.5 Wh |
| 50 m | ~2 | ~980 m | ~1.6 min | ~9.0 Wh |

Path length is ~8-10% longer than lawnmower because the ring perimeters include
four direction changes per ring (90-degree corners) instead of simple U-turns.

### Pros

- **Fewer sharp U-turns** -- direction changes are 90-degree corners rather than
  180-degree reversals. Smoother flight dynamics.
- **Perimeter coverage first** -- the outer ring covers the polygon boundary
  early, useful if the target is more likely near edges.
- **Natural for circular/square areas** -- minimal wasted path segments.

### Cons

- **Coverage gaps at centre** -- the innermost ring often leaves an uncovered
  patch at the polygon centre where the spiral collapses. Requires a final
  centre-fill waypoint.
- **Longer total path** -- the four 90-degree turns per ring add up. Our
  irregular 5-corner polygon has poor spiral nesting, increasing path length.
- **Poor fit for elongated polygons** -- our survey area is roughly 216 m x
  150 m (aspect ratio ~1.44). The spiral wastes path segments on the short axis.
- **Hard to guarantee coverage** -- unlike the lawnmower, proving complete
  coverage on an irregular polygon requires careful polygon offsetting (Minkowski
  sum), which is error-prone with concave shapes.
- **NFZ interaction** -- the northeast side borders the SSSI. The spiral's outer
  ring runs parallel to this boundary, requiring the full length of the NFZ edge
  to be traversed at reduced speed. The lawnmower only clips this edge at the
  end of specific scan lines.

### When It Is the Best Choice

- Circular or near-square search areas with no adjacent hazards.
- Target more likely near the perimeter (e.g., maritime overboard search from
  a known drift ring).

---

## 3. Expanding Square

### How It Works

Start from a known point of interest (e.g., last known position or PLB beacon
signal) and fly outward in expanding square legs. Each leg is one swath longer
than the previous.

```
              Start (PLB signal)
                |
                v
            +---+---+
            |       |
        +---+       +---+
        |               |
    +---+               +---+
    |                       |
    +-----------+-----------+
                |
              (expanding outward)
```

Leg sequence: N(1), E(1), S(2), W(2), N(3), E(3), S(4), W(4), ...
Each pair of legs increases length by one swath width.

### Estimates for Our Polygon

To cover the full 32,200 m^2 from the centre:

| Altitude | Legs to full coverage | Path length | Time | Energy |
|----------|----------------------|-------------|------|--------|
| 35 m | ~24 legs | ~1,500 m | ~3.1 min | ~15.0 Wh |
| 50 m | ~16 legs | ~1,100 m | ~1.8 min | ~10.2 Wh |

Energy is ~18-23% higher than lawnmower because the expanding square does not
align with the polygon shape, wasting path outside the search area.

### Pros

- **Searches highest-probability area first** -- if you have a beacon signal or
  last known position, the most likely target location is searched immediately.
- **Progressive coverage** -- can abort early if target is found near the centre.
  Expected search time is much lower than worst-case if the target is near the
  start point.
- **Simple to compute** -- no polygon rasterisation needed. Just increment leg
  length after each pair of turns.

### Cons

- **Not area-optimal** -- the square pattern does not conform to the polygon
  boundary. Many legs extend outside the search area (wasted energy) or fail to
  reach polygon corners (missed coverage).
- **Requires a start point** -- useless without prior information about the
  target location. Our default mission has no PLB signal.
- **Many 90-degree turns** -- every leg ends with a right-angle turn. For 24
  legs, that is 24 turns (~48 seconds of turning overhead).
- **Poor with NFZ** -- the expanding square has no awareness of the SSSI
  boundary. Legs toward the northeast would need real-time truncation, breaking
  the pattern's regularity.

### When It Is the Best Choice

- PLB/ELT beacon signal received with approximate position.
- Lost-person search from last known point (e.g., campsite, trail junction).
- Time-limited search where checking the most likely area first maximises
  probability of detection within available battery.

**Note:** Our system implements this as the Focus Area mode (config.FOCUS_AREA_GPS).
When a PLB signal is received (`B` key or `--beacon-delay N`), the search
redirects to a smaller polygon around the beacon location, using a lawnmower
within that focused area. This combines the "search likely area first" benefit
with the coverage guarantee of the lawnmower.

---

## 4. Sector Search

### How It Works

Divide the search area into sectors (e.g., quadrants or grid cells). Assign a
prior probability to each sector based on available intelligence (terrain, wind,
last sighting, population density). Search high-probability sectors first.

```
    +--------+--------+--------+
    |        |  P=0.3 |        |
    |  P=0.1 | search |  P=0.1 |
    |        |  2nd   |        |
    +--------+--------+--------+
    |  P=0.05|  P=0.4 |  P=0.05|
    |        | search |        |
    |        |  1st   |        |
    +--------+--------+--------+

    Within each sector: lawnmower sub-pattern
```

### Estimates for Our Polygon

Assuming 4 sectors with lawnmower within each:

| Altitude | Sub-patterns | Path length | Time | Energy |
|----------|-------------|-------------|------|--------|
| 35 m | 4 | ~1,400 m | ~2.9 min | ~14.0 Wh |
| 50 m | 4 | ~1,000 m | ~1.7 min | ~9.5 Wh |

Overhead comes from transit between sectors (~100 m extra) and sub-optimal scan
alignment within smaller polygons.

### Pros

- **Probability-weighted** -- allocates flight time where the target is most
  likely. Maximises probability of detection per unit energy.
- **Flexible** -- each sector can use a different scan pattern, altitude, or
  speed based on terrain difficulty.
- **Interruptible** -- can stop after searching the top 2 sectors if battery is
  low. The most likely areas are already covered.

### Cons

- **Requires a probability model** -- needs prior intelligence about target
  location. Without it, degrades to uniform sector search (same as lawnmower
  but with inter-sector transit overhead).
- **Sector boundaries cause gaps** -- unless sub-patterns overlap at sector
  edges, thin strips between sectors can be missed.
- **Transit overhead** -- flying between non-adjacent sectors wastes energy.
  For our 32,200 m^2 polygon, transit between 4 sectors adds ~100-200 m.
- **Complexity** -- requires probability estimation, sector partitioning, and
  inter-sector routing. Our five-person team chose to invest engineering time
  in reliable single-pattern execution rather than probabilistic planning.

### When It Is the Best Choice

- Large search areas (>1 km^2) where full coverage is not feasible in one
  battery cycle.
- Multi-source intelligence available (witnesses, terrain analysis, wind
  modelling, cell phone pings).
- Multi-drone operations where sectors can be assigned to different aircraft.

---

## 5. Creeping Line Ahead

### How It Works

Similar to lawnmower, but all scan lines progress in the same direction (e.g.,
always left to right). At the end of each line, the drone transits back to the
start side at the next line's offset, then scans forward again.

```
    +----------------------------------->  line 1
    |
    + - - - - - - - - - - - - - - - - <   (transit back, no scanning)
    |
    +----------------------------------->  line 2
    |
    + - - - - - - - - - - - - - - - - <   (transit back)
    |
    +----------------------------------->  line 3
    |
    + - - - - - - - - - - - - - - - - <   (transit back)
    |
    +----------------------------------->  line 4
```

### Estimates for Our Polygon

| Altitude | Scan lines | Path length | Time | Energy |
|----------|-----------|-------------|------|--------|
| 35 m | ~6 | ~2,200 m | ~4.6 min | ~22.0 Wh |
| 50 m | ~4-6 | ~1,550 m | ~2.6 min | ~14.5 Wh |

Path length is approximately **double** the lawnmower because every scan line
requires a full-length return transit. Energy cost is 75% higher.

### Pros

- **Simple** -- no alternating direction logic. Every scan line is identical.
- **Good for rectangular areas** -- when scan lines are very long, the return
  transit is a small fraction of total distance. (Not the case for our polygon.)
- **Consistent viewing angle** -- the drone always approaches from the same
  direction. Useful for side-looking sensors (sonar, SAR radar) that have an
  asymmetric beam pattern. Not relevant for our nadir-pointing camera.
- **Deterministic wind handling** -- if there is a strong crosswind, always
  scanning upwind avoids drift accumulation.

### Cons

- **Nearly double the path length** -- the return transits add ~100% to total
  distance for our polygon. This is the most energy-inefficient strategy.
- **Wasted time** -- return transits produce no useful imagery. The camera is
  still running but pointing at already-scanned ground.
- **No coverage benefit** -- for a nadir-pointing camera with no directional
  preference, there is zero advantage over the lawnmower.
- **More turns** -- each line has two turns (end-of-scan + start-of-next) vs
  one U-turn in the lawnmower.

### When It Is the Best Choice

- Side-looking sensors (marine sonar, SAR radar) that require consistent
  scan direction.
- Strong crosswind where always scanning into the wind improves ground track
  stability.
- Very long scan lines (>1 km) where return transit is a small fraction.

---

## 6. Adaptive / Heatmap Search

### How It Works

Start with a coarse initial sweep (e.g., every other scan line). Build a
probability heatmap from detections and terrain features. Adaptively re-plan
the next scan lines to focus on high-probability regions.

```
    Pass 1 (coarse):
    +----------------------------------->  line 1 (scan)
                                          |
                                     (skip line 2)
                                          |
    <-----------------------------------+  line 3 (scan)
                                          |
                                     (skip line 4)
                                          |
    +----------------------------------->  line 5 (scan)

    Detection on line 3!

    Pass 2 (focused):
    <---+                         +----   line 2 (fill gap around detection)
        |                         |
    +---+--- detection zone ------+----   line 3 (rescan, lower altitude)
        |                         |
    <---+                         +----   line 4 (fill gap around detection)
```

### Estimates for Our Polygon

Best case (target found on first coarse pass):

| Altitude | Scan lines | Path length | Time | Energy |
|----------|-----------|-------------|------|--------|
| 50 m (coarse) | ~3 | ~450 m | ~0.8 min | ~4.2 Wh |
| 35 m (focused) | ~2 | ~200 m | ~0.4 min | ~2.0 Wh |
| **Total** | **5** | **~650 m** | **~1.2 min** | **~6.2 Wh** |

Worst case (target not found, full coverage needed):

| Altitude | Scan lines | Path length | Time | Energy |
|----------|-----------|-------------|------|--------|
| Full coverage | ~8+ | ~1,500 m+ | ~3.5 min+ | ~16.0 Wh+ |

### Pros

- **Energy-efficient in the best case** -- if the target is found early, the
  search terminates with minimal energy expenditure.
- **Adaptive** -- responds to real-time information. Can redirect to areas with
  partial detections, shadows, or terrain features suggesting a casualty.
- **Multi-resolution** -- coarse pass at high altitude, detailed pass at low
  altitude only where needed.

### Cons

- **Complex** -- requires real-time path replanning, probability estimation,
  and heatmap management. Significantly more engineering effort than the
  lawnmower.
- **No coverage guarantee** -- the coarse pass may miss the target entirely if
  it falls between scan lines. The probability of this depends on swath width
  vs skip distance.
- **Worst case is worse** -- if the coarse pass misses the target, the total
  search (coarse + fill) takes longer than a single lawnmower pass.
- **Detection dependency** -- the adaptive logic only helps if the AI detector
  works reliably. With 4.8 FPS and ~0.2 confidence threshold, edge-of-frame
  detections are unreliable. The heatmap could be misled by false positives.
- **Testing difficulty** -- much harder to validate in simulation. The number
  of execution paths is combinatorial (depends on where/when detections occur).

### When It Is the Best Choice

- Large search areas where full coverage in one battery is impossible.
- High-confidence detector with low false-positive rate.
- Multi-sortie operations where each flight builds on the previous one's data.
- Future work for our system (after detector reliability is proven).

**Note:** Our system already implements a simplified version of this concept
through the rescan chain (Section 2.7 of DESIGN_SUMMARY.md). After the initial
lawnmower pass, if the target is not confirmed, the drone rescans at progressively
lower altitudes (35 m -> 28 m -> 22 m) with narrower swaths. This gives multi-
resolution coverage without the complexity of real-time heatmap replanning.

---

## Summary Comparison

| Strategy | Path length (50 m) | Time | Energy | Coverage guarantee | Needs prior info | Complexity |
|----------|-------------------|------|--------|-------------------|-----------------|------------|
| **Lawnmower** | ~876 m | 1.5 min | 8.3 Wh | Yes | No | Low |
| Spiral inward | ~980 m | 1.6 min | 9.0 Wh | Partial | No | Low |
| Expanding square | ~1,100 m | 1.8 min | 10.2 Wh | No | Yes (start point) | Low |
| Sector search | ~1,000 m | 1.7 min | 9.5 Wh | Per-sector | Yes (probability) | Medium |
| Creeping line | ~1,550 m | 2.6 min | 14.5 Wh | Yes | No | Low |
| Adaptive/heatmap | 650-1,500 m | 1.2-3.5 min | 6.2-16.0 Wh | No (probabilistic) | No | High |

All estimates at 50 m altitude, 10 m/s search speed, 150 W hover + drag model.

---

## Why Lawnmower Was the Right Choice

Five factors made the lawnmower pattern the clear winner for our specific mission:

**1. No prior information.** The mission brief specifies a casualty somewhere in
the survey polygon. There is no PLB signal, no last known position, no probability
map. Without prior information, all area-prioritisation strategies (expanding
square, sector search) degrade to uniform coverage with added transit overhead.
The lawnmower provides uniform coverage natively.

**2. Complete coverage is mandatory.** The assessment requires demonstrating that
the drone can find the target in the designated area. A missed detection is a
failed mission. Only the lawnmower and creeping-line-ahead provide mathematically
provable complete coverage. The creeping line is 75% more expensive in energy for
the same guarantee.

**3. Irregular polygon with adjacent NFZ.** Our 5-corner survey polygon is not
square or circular. The spiral pattern fits poorly (coverage gaps, inefficient
nesting). The lawnmower's rasterisation-based approach handles arbitrary polygons
naturally. Furthermore, the SSSI no-fly zone on the northeast edge integrates
cleanly with parallel scan lines -- the speed scalar field simply slows the drone
at the ends of affected lines. A spiral or expanding square would require
per-segment NFZ checks with complex path truncation logic.

**4. Small area, single battery.** At 32,200 m^2, the entire polygon can be
covered in 1.5 minutes at 50 m altitude. The energy cost (8.3 Wh) is well within
a single battery cycle (~200 Wh typical for a survey quadcopter). There is no need
to optimise for partial coverage or multi-sortie efficiency. The lawnmower's
simplicity and reliability outweigh the marginal efficiency gains of more complex
strategies.

**5. Team engineering budget.** Five team members, limited development time.
The lawnmower was implemented, tested, and validated in simulation in one session.
The adaptive/heatmap approach alone would require probability estimation, real-time
replanning, and combinatorial testing -- engineering effort better spent on NFZ
safety, operator UI, and flight testing. The rescan chain (altitude drops on miss)
provides the multi-resolution benefit without the planning complexity.

**Bottom line:** For a small, irregular, single-battery survey area with no prior
target information and an adjacent no-fly zone, the lawnmower pattern delivers
guaranteed coverage at the lowest energy cost with the least implementation risk.
The system's Focus Area mode and rescan chain provide the adaptive benefits of
more complex strategies (search likely area first, multi-resolution) without
abandoning the coverage guarantee.
