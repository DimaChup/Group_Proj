# Search Pattern Comparison: Lawnmower vs Zian's Perimeter Spiral

**Site:** Fenswood Farm Survey Area (AENGM0074 KML)
**Camera:** IMX296 (1456x1088, sensor 5.02mm, focal 5.46mm)
**NFZ:** SSSI no-fly zone adjacent to western boundary
**Physics:** Momentum model (3 m/s² accel/decel), directional NFZ scalar field
**Date:** 2026-03-29

---

## 1. Methodology

### Patterns Compared
- **Lawnmower** (boustrophedon): parallel scan lines aligned to longest polygon edge (~23.6°), from `planning.py` PathPlanner
- **Zian Spiral** (perimeter inset): concentric polygon shells spiraling inward with edge degeneration, from `Zian/path_planner/perimeter_planner.py`

### Shared Parameters
- Footprint height used for strip spacing (not width): `footprint_h = footprint_w × 1088/1456`
- Edge margin: 1/3 of strip spacing (same as lawnmower's `inset_px = strip_spacing_px // 3`)
- Speed from altitude: linear interpolation 6 m/s (20m) to 10 m/s (50m)
- Energy model: P = 150W hover + 50W × (speed/5)² drag
- NFZ: directional mode — only limits velocity component toward SSSI boundary

### Parameter Sweep
- **Full sweep:** 6 altitudes (20-50m) × 4 overlaps (0-30%) × 2 patterns = 48 configs
- **35m sweep:** fixed altitude, 9 overlaps (0-40%) × 2 patterns = 18 configs

### Scoring
Composite score (higher = better):
- 30% coverage + 25% (1 - time_norm) + 25% (1 - energy_norm) + 20% (1 - nfz_norm)

---

## 2. Results: Full Altitude Sweep

### Best Overall Config Per Pattern

| Metric | Best Lawnmower | Best Spiral | Winner |
|--------|---------------|-------------|--------|
| **Config** | 35m, 0% overlap | 50m, 0% overlap | - |
| Strip spacing | 24.1m | 34.4m | - |
| Waypoints | 10 | 7 | Spiral (-30%) |
| Path length | 846m | 469m | **Spiral (-45%)** |
| Mission time | 580s (9.7 min) | 195s (3.2 min) | **Spiral (-66%)** |
| Energy | 26.3 Wh | 9.5 Wh | **Spiral (-64%)** |
| Coverage | 94.5% | 85.7% | **Lawnmower (+8.8pp)** |
| Detection prob | 1.0000 | 1.0000 | Tie |
| NFZ exposure | 12.7% | 3.4% | **Spiral (-73%)** |
| **Composite score** | 0.701 | 0.872 | **Spiral** |

Spiral wins 5/7 metrics. Lawnmower's only advantage is coverage (+8.8 percentage points).

### Top 3 Configs Per Pattern (full sweep)

**Lawnmower:**
1. 35m, 0% overlap — Coverage=94.5%, Time=580s, Energy=26.3Wh, NFZ=12.7% (score=0.701)
2. 35m, 10% overlap — identical (planning.py `_no_turn` ignores overlap)
3. 35m, 20% overlap — identical

**Zian Spiral:**
1. 50m, 0% overlap — Coverage=85.7%, Time=195s, Energy=9.5Wh, NFZ=3.4% (score=0.872)
2. 50m, 30% overlap — Coverage=93.9%, Time=355s, Energy=17.0Wh, NFZ=5.4% (score=0.871)
3. 50m, 10% overlap — Coverage=85.4%, Time=223s, Energy=10.8Wh, NFZ=3.7% (score=0.855)

---

## 3. Results: Fixed 35m Altitude (Fair Comparison)

### Best Config at 35m Per Pattern

| Metric | Lawnmower (5% ov) | Spiral (35% ov) | Delta | Winner |
|--------|-------------------|-----------------|-------|--------|
| Strip spacing | 22.9m | 15.7m | - | - |
| Footprint | 32.2 × 24.1m | 32.2 × 24.1m | same | - |
| Waypoints | 10 | 21 | +110% | Lawnmower |
| Path length | 846m | 1,485m | +76% | Lawnmower |
| Mission time | 602s (10.0 min) | 639s (10.7 min) | +6% | Lawnmower |
| Energy | 27.2 Wh | 29.7 Wh | +9% | Lawnmower |
| Coverage | 94.9% | **97.2%** | +2.3pp | **Spiral** |
| Detection prob | 1.0000 | 1.0000 | - | Tie |
| NFZ exposure | 12.6% | **4.9%** | **-61%** | **Spiral** |
| **Composite score** | 0.691 | **0.915** | +32% | **Spiral** |

### Interpretation

At the same altitude (35m), the spiral achieves:
- **Higher coverage** (97.2% vs 94.9%) by using 35% overlap to fill corner gaps
- **61% less NFZ exposure** (4.9% vs 12.6%) — the spiral's inner rings naturally avoid the SSSI boundary
- Only **6-9% more time and energy** — a small price for better coverage and safety

The lawnmower's path is shorter (846m vs 1,485m) and has fewer waypoints (10 vs 21), but these don't translate to significant time/energy savings because the spiral's wider turns waste less time on deceleration/acceleration compared to the lawnmower's tight 180° U-turns.

---

## 4. Key Findings

### Why Spiral Wins on NFZ Safety
The SSSI polygon shares edges with the western side of the search area. The lawnmower's parallel strips cross this zone on every pass (12.6% of time near NFZ). The spiral's outer ring traces the boundary once, then all inner rings retreat away from it (only 4.9% near NFZ).

With directional NFZ enforcement, the drone only slows when flying *toward* the SSSI. The spiral's inner rings fly mostly parallel to the boundary, so they maintain full cruise speed. The lawnmower's perpendicular crossings trigger the scalar field on every pass.

### Why Lawnmower Wins on Path Efficiency
Parallel strips aligned to the longest edge (186.8m, P3-P4) minimize turns. The spiral must traverse all 5 edges on every ring, including the short P4-P0 edge (37.8m), creating more waypoints and a longer total path.

### Coverage Trade-off
The lawnmower achieves 94.5-96.8% coverage at 0% overlap because its parallel strips naturally tile the polygon. The spiral has coverage gaps at polygon corners where edges degenerate (pentagon → quad → triangle). Adding 30-35% overlap fills these gaps, bringing spiral coverage to 93.9-97.2%.

### Detection Probability
Both patterns achieve P(detect) = 1.0000 at all tested altitudes (20-50m). The target (0.15m radius dummy) produces sufficient pixel size even at 50m for the IMX296 camera at 4.8 FPS. Detection probability is not a differentiator between patterns for this site.

---

## 5. Recommendation

**For maximum coverage with minimal risk: Zian Spiral at 35m, 30-35% overlap.**

This configuration provides:
- 97% coverage (vs 95% lawnmower)
- 61% less time near the SSSI boundary
- Only 6-9% longer mission time
- Same detection probability

**For fastest mission with acceptable coverage: Zian Spiral at 50m, 0% overlap.**

This gives 86% coverage in just 3.2 minutes — useful for a quick initial sweep before a slower detailed search.

**Lawnmower remains preferable when:**
- Minimum waypoint count matters (simpler autopilot load)
- Path length must be minimised (e.g., battery-critical missions)
- No NFZ is present (spiral's safety advantage disappears)

---

## 6. Files

| File | Description |
|------|-------------|
| `tools/pattern_compare_v2.py` | Full altitude sweep (48 configs) |
| `tools/pattern_compare_35m.py` | Fixed 35m comparison (18 configs) |
| `tools/pattern_compare_visual.py` | Publication-quality visual (optimal vs optimal) |
| `tools/pattern_analysis/compare_v2.json` | Full sweep results (JSON) |
| `tools/pattern_analysis/compare_35m.png` | 35m comparison figure |
| `tools/pattern_analysis/optimal_comparison.png` | Best-vs-best figure |
| `tools/pattern_analysis/pareto_overlay.png` | Pareto frontier (time vs energy) |
| `tools/pattern_analysis/radar_chart.png` | 5-axis radar chart |
| `tools/pattern_analysis/coverage_vs_time.png` | Coverage vs mission time scatter |

---

## 7. Physics Model Summary

```
Cruise speed:     6.0 m/s (20m) → 10.0 m/s (50m), linear interpolation
Acceleration:     3.0 m/s²
Deceleration:     3.0 m/s²
Hover power:      150 W
Drag power:       50 × (speed/5)² W
NFZ slow zone:    20m outer → 2m inner, linear speed ramp 0-3 m/s
NFZ mode:         Directional (only approach component limited)
Camera FPS:       4.8 (Pi 5 TFLite benchmark)
Footprint @35m:   32.2m (width) × 24.1m (height)
```
