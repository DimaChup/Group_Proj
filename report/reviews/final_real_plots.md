# Final Review: Real Analysis Plots

Reviewed: 2026-03-27. All 9 plots from actual simulation/analysis data.

---

## 1. real_energy_heatmap.png
**Score: 8/10**

A 2D heatmap of energy (Wh) across altitude (y-axis, 20-50m) and scan angle (x-axis, 0-170 degrees). Uses viridis colormap with a colorbar on the right. The optimal point (50m, 70 deg, 8.3 Wh) is annotated with a star and leader line.

**Strengths:**
- Clear color gradient showing the energy landscape.
- Optimal point annotated with exact values -- immediately communicable.
- Axes and colorbar are labeled with units.
- Subtitle explains the color convention (darker = less energy = better).

**Weaknesses:**
- The annotation text box is slightly small and could be hard to read in print at reduced size.
- The dark purple bands at certain scan angles (around 130-150 deg) are visually striking but unexplained in the figure itself -- caption will need to address this.
- Could benefit from contour lines overlaid to make iso-energy boundaries clearer.

**Verdict:** Strong publication-quality figure. Much more informative than a generic bar chart would be.

---

## 2. real_optimal_pattern.png
**Score: 6/10**

Side-by-side panels: left shows survey area overview (blue polygon, red NFZ, pink buffer, green take-off marker), right shows the optimal lawnmower pattern (6 lines, cyan path over the same zones).

**Strengths:**
- Two-panel layout effectively compares area context vs. flight plan.
- Legend identifies all zones (Survey, SSSI/NFZ, buffer, take-off).
- Title includes key parameters (Alt=50m, Angle=70d, 6 lines, 8.3 Wh).

**Weaknesses:**
- The figure is quite small/compressed -- labels and legend text are borderline readable.
- The flight path lines on the right panel are thin and could be thicker for visibility.
- Axis labels ("East (m)", "North (m)") are small. At report column width this will be hard to read.
- The red NFZ polygon overlaps significantly with the survey polygon, making the geometry hard to parse without zooming in.
- No grid lines or scale reference beyond axes.

**Verdict:** Functional but needs to be rendered at higher resolution or larger size for print. Currently the weakest of the set for readability.

---

## 3. real_search_comparison.png
**Score: 7/10**

Five-panel bar chart comparing search strategies (Lawnmower optimal, Lawnmower 90-deg, Spiral inward, Lawnmower cell-start) across: Distance, Turns, Time, Energy, Coverage. Two altitude conditions (30m blue, 50m orange) shown side by side.

**Strengths:**
- Comprehensive -- five metrics in one figure, easy to compare strategies.
- Numeric values printed above each bar for precision.
- Summary box in bottom-right with key findings (polygon area, fastest strategy, energy model).
- Color coding for altitude is consistent across all panels.

**Weaknesses:**
- Very information-dense -- at report column width the bar labels and numbers will be tiny.
- The x-axis strategy labels are long and may overlap or require rotation.
- The "Coverage" panel shows all strategies at ~100%, making it less informative (could note this).
- Some bar value labels overlap with the top of the bar at the current size.

**Verdict:** Good analytical content. Would benefit from being a full-width figure in the report rather than squeezed into a single column.

---

## 4. real_dry_run_pattern.jpg
**Score: 4/10**

Satellite image of the actual field site (aerial/orthophoto). Shows a grassy field with hedgerows, a building in the top-left corner. No overlays, no flight path, no annotations.

**Strengths:**
- Provides real-world context for the survey area.
- High resolution satellite imagery.

**Weaknesses:**
- No overlay whatsoever -- no flight path, no polygon boundary, no waypoints, no scale bar.
- As a standalone figure it conveys almost nothing about the mission planning.
- JPEG artifacts visible. Not cropped to a clean boundary.
- No axis labels, no north arrow, no coordinate reference.
- Compared to the generated plots, this looks like a raw screenshot rather than an analytical figure.

**Verdict:** This needs significant work. Either overlay the lawnmower pattern on this satellite image (which would be excellent), or replace it. As-is, it is not publication quality and adds little value.

---

## 5. real_altitude_vs_px.png
**Score: 9/10**

Line plot showing target (dummy) height in pixels vs. altitude (20-80m). Blue curve shows pixel height decreasing with altitude. Red dashed line marks the 20px detection threshold. Grey dashed line marks the critical altitude (63m). Pink shaded region highlights the "undetectable" zone above 63m.

**Strengths:**
- Very clean, professional look. Axes labeled with units. Title includes model info (YOLOv8n 640x640).
- The threshold line and critical altitude are clearly annotated.
- Shaded danger zone immediately draws the eye to the key finding.
- Legend is clean and uncluttered.
- Directly answers a key design question (max detection altitude).

**Weaknesses:**
- Minor: could include a few data points/markers along the curve to show it is computed from a model (currently looks purely analytical).
- The x-axis could extend slightly beyond 80m to give visual breathing room.

**Verdict:** Best figure in the set. Clean, informative, directly supports a design decision. Publication ready.

---

## 6. real_speed_vs_blur.png
**Score: 8/10**

Line plot showing motion blur (sensor pixels) vs. drone speed (0-20 m/s) at three altitudes (20m, 35m, 50m). Horizontal dashed line marks the 1px visible-blur threshold.

**Strengths:**
- Clean three-line design with distinct colors for each altitude.
- Threshold line clearly shows that blur stays below 1px for all speeds up to ~13 m/s at 50m altitude.
- Title includes key parameter (1/1000s exposure, global shutter).
- Axes labeled with units.

**Weaknesses:**
- The lines are somewhat thin -- could be slightly bolder for print.
- Legend could include line markers (circles, squares) in addition to color for B&W printing.
- The finding (blur is negligible with this shutter/sensor combo) could be more dramatically highlighted.

**Verdict:** Strong figure. Demonstrates a key hardware advantage (global shutter eliminates blur concern). Ready for publication.

---

## 7. real_speed_vs_frames.png
**Score: 8/10**

Line plot showing target visibility duration (frames) vs. drone speed (1-15 m/s) at three altitudes (20m, 35m, 50m). Two horizontal threshold lines: 3 frames (smart-detect) and 1 frame (minimum). Shows hyperbolic decay.

**Strengths:**
- Clear hyperbolic relationship -- immediately shows the speed/altitude trade-off.
- Threshold lines are well-chosen and labeled.
- Title includes FPS (4.8) grounding the analysis in real hardware performance.
- Color-coded altitude lines are consistent with the blur plot.

**Weaknesses:**
- The y-axis goes up to ~225 frames at low speed, compressing the interesting region (5-15 m/s) where values approach thresholds. A log scale or zoomed inset would help.
- The green threshold markers along the bottom are very dense and hard to distinguish.
- At 50m altitude and 5 m/s the target is visible for ~20 frames -- this key operating point could be annotated.

**Verdict:** Good analytical figure. The key message (even at operational speed and altitude, target is visible for many frames) comes through clearly.

---

## 8. real_coverage.png
**Score: 7/10**

Dual-axis line plot showing coverage rate (m^2/s, left axis, blue) and swath width (m, right axis, pink dashed) vs. altitude (15-60m). Both increase with altitude.

**Strengths:**
- Dual-axis design efficiently combines two related metrics.
- Clean lines with distinct styles (solid vs. dashed).
- Both axes labeled with units and color-coded.
- Shows the near-quadratic growth of coverage rate with altitude.

**Weaknesses:**
- The two curves are nearly identical in shape, which makes the dual-axis feel slightly redundant -- the swath width IS the primary driver of coverage rate, so one could be derived.
- No annotation of the chosen operating point (50m).
- Title is generic ("Search Efficiency vs Altitude") -- could be more specific.
- No grid lines, making it harder to read exact values.

**Verdict:** Solid supporting figure. Would be stronger with an annotated operating point and grid lines.

---

## 9. real_energy_vs_altitude.png
**Score: 8/10**

Line plot showing total search energy (Wh) vs. altitude (20-50m) for two conditions: without NFZ slowdown (blue) and with NFZ slowdown (red). Pink shaded area between curves shows the NFZ energy penalty. Optimal point (50m, 8.5 Wh) annotated.

**Strengths:**
- Excellent use of shaded area to visualize the NFZ penalty.
- Optimal point clearly annotated with a callout box.
- Both curves clearly show energy decreasing with altitude (fewer turns at higher alt).
- Professional appearance with labeled axes and units.

**Weaknesses:**
- The callout box text is small and positioned at the edge -- could be slightly larger.
- X-axis only goes to 50m -- extending to 60m would show if the trend continues or plateaus.
- Data points are shown as dots on the curves which is good, but the dot size is small.

**Verdict:** Strong figure that effectively communicates the altitude-energy trade-off and NFZ impact. Publication ready.

---

## Summary Table

| # | Figure | Score | Publication Ready? |
|---|--------|-------|--------------------|
| 1 | real_energy_heatmap.png | 8/10 | Yes |
| 2 | real_optimal_pattern.png | 6/10 | Needs larger render |
| 3 | real_search_comparison.png | 7/10 | Yes (full-width) |
| 4 | real_dry_run_pattern.jpg | 4/10 | NO -- needs overlays |
| 5 | real_altitude_vs_px.png | 9/10 | Yes -- best figure |
| 6 | real_speed_vs_blur.png | 8/10 | Yes |
| 7 | real_speed_vs_frames.png | 8/10 | Yes |
| 8 | real_coverage.png | 7/10 | Yes (minor tweaks) |
| 9 | real_energy_vs_altitude.png | 8/10 | Yes |

**Overall average: 7.2/10**

## Key Recommendations

1. **Fix real_dry_run_pattern.jpg (4/10):** This is the weakest figure by far. Either overlay the lawnmower pattern and survey polygon on the satellite image, or replace it with the annotated version from real_optimal_pattern.png. A satellite image with flight path overlay would be the single most impressive figure in the report.

2. **Enlarge real_optimal_pattern.png (6/10):** Render at higher resolution or use as a full-width figure. The current size makes text unreadable. Consider increasing line thickness for the flight path.

3. **Use real_search_comparison.png as full-width:** This five-panel figure needs column width to be readable. Force it to span both columns in the LaTeX layout.

4. **Annotate operating points:** Figures 7 (speed_vs_frames) and 8 (coverage) would benefit from marking the chosen operating point (50m altitude, 5 m/s speed) with an arrow or highlighted dot.

5. **Consistency:** Figures 5-7 use the same altitude color scheme (blue=20m, orange=35m, pink=50m) which is good. Ensure all multi-altitude figures use this same palette.

## Comparison: Real Plots vs Generated Charts

The real analysis plots are significantly more credible than generic generated illustrations because they:
- Use actual field geometry (real polygon, real NFZ)
- Show computed results from the real system parameters (4.8 FPS, IMX296, YOLOv8n)
- Include hardware-specific details in titles (exposure time, model input size)
- Demonstrate quantitative design justification rather than qualitative hand-waving

The weakest link is the dry-run satellite image which currently looks like a raw screenshot. Fixing that one figure would bring the whole set to a consistently strong level.
