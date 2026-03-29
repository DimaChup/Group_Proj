# SAR Drone Manim Animation Ideas

Ranked by impact for the report/presentation. Each animation described with visual flow, duration, and manim implementation notes.

Run any script with:
```bash
"CW Ai for Robotics/venv/Scripts/python.exe" -m manim -pqh script.py ClassName
```

Style reference: `CW Ai for Robotics/visualize_pipeline.py` and `visualize_rf_hog.py` (scene-based, step labels, coloured boxes, arrows between stages, LaggedStart for groups).

---

## 1. Decision Flow Animation (HIGHEST IMPACT)

**What**: The 9-step optimization chain from `decision_flow.py` — each box materializes with its step number, label, and result value, connected by arrows. Phase A ("Measure") and Phase B ("Optimise") brackets slide in at the right moments. Final "Selected Configuration" box pulses gold at the end.

**Why it matters**: This IS the optimization story. A static figure needs the reader to trace the logic; animated, the causal chain is unmissable. Each step appears because the previous one locked in a value.

**Visual flow** (~12s):
1. Title "Search Parameter Decision Flow" writes on (0.5s)
2. Priority boxes appear: SAFETY (green, left), DETECTION (blue, right), then TIME and ENERGY (grey, below) fade in (1.5s)
3. Steps 1-4 appear one at a time, each with: numbered circle (FadeIn), label (Write), arrow value (Write in colour), then connecting arrow grows down (0.6s each = 2.4s)
4. Phase A bracket draws on the left with "Phase A: Measure" label (0.5s)
5. Dashed separator line draws (0.3s)
6. Steps 5-9 appear same way (0.6s each = 3.0s)
7. Phase B bracket draws with "Phase B: Optimise" label (0.5s)
8. Final arrow down, then result box fades in with gold border, config values Write on (1.5s)
9. "15% safety margin" text pulses green (0.5s)

**Manim objects**: `RoundedRectangle` for boxes, `Arrow` for connections, `Circle` with `Text` for step numbers, `Line` + `Text` for phase brackets, `SurroundingRectangle` for result highlight. Use colour constants matching the report: GREEN=#2E7D32, BLUE=#1565C0, GREY=#616161.

**Estimated duration**: 12 seconds

---

## 2. Spider Web / Radar Chart Animation

**What**: A 5-axis radar chart (Safety, Detection, Coverage, Energy, Time) that builds in three layers: (a) the axes draw, (b) a dashed "desired envelope" polygon appears showing the TARGET shape the mission should fit, (c) the actual scored configuration fills in as a solid polygon, showing how well it matches.

**Why it matters**: The spider chart is the visual thesis of the optimization section. Animating it shows the INTENT (desired shape) before the RESULT (actual shape), making the gap analysis visceral. The non-circular envelope shape communicates that some dimensions are pass/fail constraints while others are continuously optimised.

**Visual flow** (~10s):
1. Title "Mission Scoring: Target vs Achieved" writes on (0.5s)
2. Five axis lines grow outward from centre, each with a label at the tip (LaggedStart, 1.5s)
3. Concentric grid rings fade in (0.5s)
4. "Desired Envelope" label appears, then a dashed blue polygon draws around the target shape — Safety and Time pushed to 0.9+, Detection/Coverage/Energy at 0.7-0.85 (1.5s)
5. Brief hold (0.5s)
6. "Actual Configuration" label appears, then a solid green polygon grows from centre to its final shape (Safety=0.96, Detection=0.93, Coverage=0.96, Energy=0.89, Time=0.92) (2s, use UpdateFromAlphaFunc to interpolate vertices from 0 to final)
7. Overlap region between desired and actual highlights briefly (0.5s)
8. Score labels appear at each vertex: "0.96", "0.93", etc. (LaggedStart, 1s)
9. Composite score "S = 0.93" fades in at bottom (0.5s)
10. Dimension that falls short (if any) briefly flashes red (0.5s)

**Manim objects**: `Line` for axes, `Polygon` for envelopes (dashed via `DashedVMobject`), `Text` for labels, custom `ValueTracker` + `always_redraw` for the growing polygon. Manual polar-to-cartesian conversion for vertex positions.

**Estimated duration**: 10 seconds

---

## 3. Lawnmower Pattern Animation

**What**: A drone icon (small triangle or dot) flies a lawnmower search pattern over a satellite map outline. As it passes each lane, a semi-transparent coverage strip fills in behind it. The SSSI no-fly zone glows red and the drone respects the 30m buffer. At the end, coverage percentage appears.

**Why it matters**: The lawnmower pattern is the core mission behaviour. Showing it animated — with the NFZ being avoided and coverage filling in — instantly communicates the spatial strategy better than any static figure. This is the "hero shot" of the project.

**Visual flow** (~15s):
1. Map outline appears: Flight Area (grey dashed), Search Area (blue polygon), SSSI (red polygon with hatching) (1.5s)
2. Takeoff point marker appears with "T/O" label (0.3s)
3. Drone icon (small white triangle) spawns at takeoff (0.3s)
4. Drone transits to search area start (traced path line, 1s)
5. Drone flies lane 1 — a semi-transparent blue strip fills behind it as it moves (1.5s per lane... but we have ~8 lanes, so speed up)
6. Lanes 1-8 fly with increasing speed (total 6s), each U-turn showing the heading change. Coverage strips accumulate.
7. Near-NFZ lanes show the 30m buffer as a faded red zone — the drone lane clips short (0.5s emphasis)
8. Drone returns to takeoff (1s)
9. "96% coverage | 112s | 12.6 Wh" fades in as summary (1s)
10. Optional: a detection flash (yellow circle) at some point during the search (0.5s)

**Manim objects**: `Polygon` for areas, `Dot`/custom triangle for drone, `TracedPath` for flight path, `Rectangle` with low opacity for coverage strips, `MoveAlongPath` for drone motion. Use actual GPS coordinates from config.py converted to screen space.

**Estimated duration**: 13-15 seconds

---

## 4. Pareto Frontier Animation

**What**: 216 configuration dots appear on a 2D plot (Detection Effectiveness vs Energy Cost), coloured by altitude. The Pareto frontier line then draws through the non-dominated points. Finally, the selected configuration highlights with a star marker and callout showing its values.

**Why it matters**: The 216-config sweep is the quantitative backbone of the optimization. Animating the dot cloud building up and the frontier emerging shows the engineering trade-off space. The selected point being on/near the frontier proves the choice is rational.

**Visual flow** (~10s):
1. Axes draw: x="Energy Cost (Wh)", y="Detection Effectiveness" (0.5s)
2. Dots appear in batches by altitude (6 batches of 36 dots each), coloured from purple (20m) to yellow (50m). LaggedStart within each batch. (3s total)
3. Colourbar legend appears on right (0.3s)
4. Brief hold to appreciate the cloud shape (0.5s)
5. Pareto frontier line draws through non-dominated points (red dashed, 1.5s, Create)
6. All non-Pareto dots dim to 30% opacity (0.5s)
7. Selected config (35m, 8m/s, 20% overlap) highlights with a gold star, grows slightly (0.5s)
8. Callout arrow + text box appears: "35m | 8 m/s | 20% overlap" with "Eff=0.92, Energy=12.6 Wh" (1s)
9. "216 configurations evaluated" subtitle fades in (0.5s)

**Manim objects**: `Axes` for the plot, `Dot` for each config point (216 total), `VGroup` + `LaggedStart` for batch appearance, `VMobject` for Pareto line, `Star` or scaled `Dot` for selected point, `Arrow` + `RoundedRectangle` for callout.

**Estimated duration**: 10 seconds

---

## 5. Detection Pipeline Animation

**What**: A camera frame flows through the CV pipeline: raw capture, lens undistortion, resize to 640x640, YOLOv8n inference (shown as a network block), NMS post-processing, final detection box drawn on frame. Each stage has a timing label.

**Why it matters**: Shows exactly what happens every 208ms on the Pi. The audience sees the full data transformation. Perfect for the "System Design" section of the report.

**Visual flow** (~10s):
1. Title "On-Board Detection Pipeline (Pi 5)" writes on (0.5s)
2. Camera icon on left, "4.8 FPS" label (0.5s)
3. Raw frame rectangle appears (labelled "1456x1088 BGR") (0.5s)
4. Arrow right, "Undistort" box with "+1.5ms" label, frame warps slightly (0.8s)
5. Arrow right, "Resize" box, frame shrinks to square (labelled "640x640") (0.8s)
6. Arrow right, large "YOLOv8n TFLite" box (coloured, largest element), "206ms" label, neural network icon inside (pulses briefly) (1.5s)
7. Arrow right, "NMS" box with "conf > 0.4" label (0.5s)
8. Arrow right, output frame with green detection bounding box drawn on it, confidence "0.97" label (1s)
9. Total pipeline timing bar appears at bottom: "|---1.5ms---|---2ms---|---206ms---|---0.5ms---|" showing where time goes (1s)
10. "4.8 FPS on Raspberry Pi 5 CPU" subtitle (0.5s)

**Manim objects**: `Rectangle` for frames, `Arrow` for flow, `RoundedRectangle` for processing blocks, `Text` for labels, `Rectangle` with proportional widths for timing bar, `SurroundingRectangle` for detection box on final frame.

**Estimated duration**: 10 seconds

---

## 6. NFZ Scalar + Vector Field Animation

**What**: Bird's-eye view of the SSSI boundary. A colour gradient shows the speed ramp (100% far away, ramping down to 0% at boundary). Repulsive force vectors (arrows) emanate from the boundary, getting stronger closer in. A drone approaches, its velocity arrow bends away, and it curves along the buffer zone.

**Why it matters**: The three-layer geofence protection (speed ramp + repulsive force + hard boundary) is a key safety feature. This animation makes the invisible force field visible. Examiners can see the drone being deflected rather than just reading about it.

**Visual flow** (~12s):
1. SSSI polygon draws (red, hatched interior) with "SSSI No-Fly Zone" label (1s)
2. 30m buffer ring draws around it (orange dashed) (0.5s)
3. Colour gradient fills: green (>30m) fading to yellow (15m) to red (0m). Label: "Speed Limit Field" (2s, use many thin rectangles or a background image)
4. Repulsive force arrows appear: short far away, long and red near the boundary, all pointing outward from SSSI (LaggedStart, 1.5s)
5. Drone icon enters from top-left at full speed (white arrow showing velocity) (1s)
6. As drone enters the buffer zone: speed arrow shrinks (speed ramp), then bends (repulsive force), drone path curves parallel to boundary (3s, smooth animation using ValueTracker)
7. Drone exits the buffer zone, speed arrow returns to full length (1s)
8. Three-layer legend appears: "Layer 1: Speed ramp | Layer 2: Repulsive force | Layer 3: Hard boundary" (1s)

**Manim objects**: `Polygon` for SSSI, `DashedVMobject(Polygon)` for buffer, `Arrow` for vectors (many small ones in a grid), `Dot` + `Arrow` for drone + velocity, `ValueTracker` + `updater` for drone motion with physics. Background gradient via overlapping semi-transparent rectangles.

**Estimated duration**: 12 seconds

---

## 7. State Machine Animation

**What**: The 19 states from `states.py` appear as nodes, grouped by mission phase (Setup, Search, Investigate, Recovery). Transitions animate as arrows drawing between states, with trigger labels (e.g., "target detected", "operator confirms").

**Why it matters**: The state machine is the entire mission logic. A 19-state diagram is complex on paper; animated, you can group related states, show the nominal path first, then layer in the contingency transitions.

**Visual flow** (~15s):
1. Title "Mission State Machine" (0.5s)
2. Phase 1 states appear (INIT, CONNECTING, ARMING, TAKEOFF) in a vertical column on the left, green boxes (1.5s)
3. Arrows chain them together top-to-bottom (0.5s)
4. Phase 2 states (TRANSIT_TO_SEARCH, SEARCH) appear in centre, blue (1s)
5. Phase 3 states (CENTERING, DESCENDING, VERIFY, HOVER_TARGET, APPROACH) appear right of centre, orange (2s)
6. VERIFY branches: "Y" arrow to APPROACH, "N" arrow to RETURN_TO_SEARCH (1s)
7. Recovery states (MANUAL, RETURN_FROM_MANUAL, RETURN_HOME) appear at bottom, red (1s)
8. LANDING and DONE appear at bottom-right, gold (0.5s)
9. Nominal path highlights (thick green trace from INIT to DONE through the happy path) (2s)
10. Contingency paths flash briefly: MANUAL override, RETURN_TO_SEARCH on reject, RETURN_HOME on timeout (2s)
11. "19 states | 32 transitions" subtitle (0.5s)

**Manim objects**: `RoundedRectangle` + `Text` for state nodes, `Arrow` with `Text` labels for transitions, `VGroup` for phase grouping, colour-coded by phase. `Succession` or `AnimationGroup` for highlighting paths.

**Estimated duration**: 13-15 seconds

---

## 8. GPS Estimation Convergence

**What**: A bird's-eye grid shows the drone flying multiple passes over a target. Each pass drops a scatter point (the GPS estimate from that pass). An ellipse (CEP) shrinks as estimates accumulate. The centroid converges toward the true target position.

**Why it matters**: GPS estimation from multiple flyovers is a novel part of the system. Showing the scatter converging visually is more convincing than quoting CEP50 numbers.

**Visual flow** (~10s):
1. Grid appears with scale bar (1m grid, 20m view) (0.5s)
2. True target position marked with red X (0.3s)
3. Pass 1: drone flies across (small triangle), drops a blue dot at estimated position (offset 3-5m from truth) (1.5s)
4. CEP circle draws around the single point (large, ~5m radius) (0.3s)
5. Passes 2-5: drone flies different directions, each dropping a dot. CEP ellipse redraws smaller each time. Centroid marker (green +) shifts toward the red X (3s total)
6. Passes 6-10: faster, dots cluster tighter, CEP shrinks to ~1.5m (2s)
7. Final centroid highlighted: "CEP50 = 1.8m after 10 passes" (0.5s)
8. Compare labels: "Single pass: 4.2m error" vs "10 passes: 1.8m error" (1s)

**Manim objects**: `NumberPlane` or grid of `Line`s, `Dot` for estimates, `Ellipse` for CEP (redrawn with `Transform`), `Cross` for true position, `Dot` for centroid, drone as small `Triangle`. Use `MoveAlongPath` for flyovers.

**Estimated duration**: 10 seconds

---

## 9. Altitude Trade-off Dual Axis

**What**: Split-screen or dual-y-axis animation showing what happens as altitude increases: detection pixel size shrinks (bad), but footprint width grows (good), frames on target change, energy per lane changes. Sliders or growing bars communicate the multi-dimensional trade-off.

**Why it matters**: Altitude is the most coupled variable — it affects ALL 5 dimensions. Animating the trade-off makes the coupling tangible. The sweet spot at 35m should feel inevitable.

**Visual flow** (~10s):
1. Title "Altitude: The Master Variable" (0.5s)
2. Altitude slider on the left, starting at 20m (0.5s)
3. Right panel: 4 gauges/bars — Target Size (px), Footprint Width (m), Frames on Target, Detection Probability (1s to set up)
4. Slider moves from 20m to 50m over 4 seconds. As it moves:
   - Target Size bar shrinks (red when < 20px)
   - Footprint Width bar grows (green)
   - Frames on Target bar decreases (orange)
   - Detection Probability follows a curve (high at 20m, dips at 50m) (4s)
5. At 63m: red line flashes "Detection Ceiling" (0.5s)
6. Slider snaps back to 35m: "Operating altitude" with green highlight, all bars at comfortable values (1s)
7. "15% margin below 63m ceiling" annotation (0.5s)
8. All 5 dimension icons flash briefly showing altitude affects them all (1s)

**Manim objects**: `ValueTracker` for altitude, `always_redraw` bars, `NumberLine` for slider, `Rectangle` bars with height bound to computed values, `DashedLine` for ceiling. Functions compute target_px, footprint_w, n_frames, p_detect from altitude using the physics formulas in `gen_pareto_2d.py`.

**Estimated duration**: 10 seconds

---

## 10. Energy Heatmap Build

**What**: A 6x6 grid (altitude x speed, one heatmap per overlap value) builds cell by cell. Colours go from green (efficient) to red (wasteful). The optimal valley emerges as cells fill in. Then the selected cell highlights.

**Why it matters**: The 216-config energy sweep is a key quantitative contribution. Watching the heatmap build cell by cell gives the audience time to understand the axes before seeing the pattern. The "valley" of efficiency is more dramatic when it emerges gradually.

**Visual flow** (~10s):
1. Title "Energy Efficiency Across 216 Configurations" (0.5s)
2. Empty 6x6 grid appears with axis labels: rows = altitude (20-50m), cols = speed (4-14 m/s) (1s)
3. "Overlap = 20%" label appears (current slice) (0.3s)
4. Cells fill in row by row with colour (green to red), each cell showing energy value in small text. LaggedStart across rows. (3s)
5. Optimal cell (lowest energy) pulses with gold border (0.5s)
6. Quick morph: grid colours shift as overlap changes from 5% to 30% (showing how the valley shifts) (2s, 6 morphs at 0.3s each)
7. Return to 20% overlap, selected config (35m, 8m/s) highlighted with star (0.5s)
8. "Minimum: 12.6 Wh at 35m, 8 m/s" callout (0.5s)
9. Comparison: "Battery capacity: 88 Wh | Mission uses 14%" (0.5s)

**Manim objects**: `Rectangle` grid (36 cells), `ColorGradient` or manual RGB interpolation for cell colours, `Text` for values, `SurroundingRectangle` for highlight, `Transform` for overlap morphing. Pre-compute all 216 energy values using the physics from `gen_pareto_2d.py`.

**Estimated duration**: 10 seconds

---

## Implementation Priority

| # | Animation | Impact | Effort | Priority |
|---|-----------|--------|--------|----------|
| 1 | Decision Flow | 10/10 | Medium | DO FIRST |
| 2 | Spider Web | 9/10 | Medium | DO SECOND |
| 3 | Lawnmower Pattern | 9/10 | High | DO THIRD |
| 4 | Pareto Frontier | 8/10 | Medium | High |
| 5 | Detection Pipeline | 7/10 | Low | High |
| 6 | NFZ Vector Field | 8/10 | High | Medium |
| 7 | State Machine | 6/10 | High | Medium |
| 8 | GPS Convergence | 7/10 | Medium | Medium |
| 9 | Altitude Trade-off | 7/10 | Medium | Medium |
| 10 | Energy Heatmap | 5/10 | Medium | Low |

**Top 3 recommendation**: Decision Flow, Spider Web, Lawnmower Pattern. These three together tell the complete optimization story: the logic chain (1), the scoring result (2), and the spatial outcome (3).

---

## Shared Style Notes (from existing scripts)

- **Colour palette**: Match report figures. GREEN=#2E7D32, BLUE=#1565C0, GREY=#616161, GOLD=#F9A825, RED=#C62828, PURPLE=#6A1B9A.
- **Font sizes**: Title 30-34, step labels 18-22, body text 12-16, annotations 9-11.
- **Scene structure**: Use `# ══════` comment blocks per scene (matching `visualize_pipeline.py` style).
- **Timing**: Each atomic animation 0.3-0.8s. Use `self.wait(0.5-1.5)` for breathing room. Total scene 10-15s.
- **LaggedStart**: Use for groups of similar elements (dots, cells, arrows) with `lag_ratio=0.05-0.15`.
- **Write vs FadeIn**: `Write` for text, `Create` for shapes, `GrowArrow` for arrows, `FadeIn` for images/groups.
- **Clean transitions**: `FadeOut` previous step label before `Write` next one.
- **Background**: Default black (manim default) works well for presentations. Use WHITE for report embedding only.
- **Resolution**: `-pqh` flag = 1920x1080 at 60fps. Good for both presentations and report GIF embeds.
