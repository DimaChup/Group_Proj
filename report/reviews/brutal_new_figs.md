# Brutal Visual Review: New Optimization & Pareto Figures

Reviewed: 2026-03-27 | 10 figures scored 1-10

---

## Individual Scores

### 1. pareto_curve.png -- 9/10
**What it shows:** 2D Pareto frontier of Detection Probability vs Mission Time, color-coded by altitude, with selected config (35m, 8m/s) starred, utopia point marked.
**Strengths:** Excellent information density. The Pareto frontier line is clear and bold. Color bar for altitude adds a third dimension without clutter. The "Selected" annotation and utopia point "X" give immediate context. Subtitle explains the trade-off in plain English. The scatter cloud behind the frontier shows all 216 configs without obscuring the frontier.
**Weaknesses:** The text "Utopia point (unreachable)" overlaps slightly with the X marker -- could shift it a few pixels. Some low-altitude red points near (0.85, 100-150) overlap heavily. Minor: subtitle font could be slightly larger.
**Verdict:** Publication-quality. One of the best figures in the entire report.

### 2. pareto_3d.png -- 6/10
**What it shows:** 3D scatter of Detection Prob vs Mission Time vs Energy, with coverage as color (4th dimension).
**Strengths:** Ambitious -- shows 4 objectives simultaneously. The selected point is clearly starred and labelled. Color scale (coverage) is readable. Grid lines help with depth perception.
**Weaknesses:** 3D plots are inherently hard to read in a static PDF. Many points are occluded behind each other. The depth axis (Energy) is difficult to read precisely. The projection shadows on the walls are faint and don't help much. Labels on axes are small. Rotating this in a paper is impossible, so the viewing angle is critical and this one hides the clustering structure. The "Selected" label partially overlaps other points.
**Verdict:** Conceptually strong but the 3D format hurts readability. Consider whether the parallel coordinates plot (which IS readable) makes this redundant. If kept, it's supplementary material, not a main figure.

### 3. pareto_parallel.png -- 8/10
**What it shows:** Parallel coordinates across 5 objectives (Coverage, Detection Prob, Speed, Efficiency, Safety) for 216 configs. Pareto-optimal (orange), dominated (grey), selected (blue bold).
**Strengths:** Excellent for showing trade-offs across many objectives simultaneously. The selected config's blue line is immediately visible. Raw values annotated at key points (0.89, 1.00, 101s, 31Wh, 0.84). The 7 Pareto-optimal configs clearly separate from the 209 dominated ones. Legend is clean. Title includes the config count.
**Weaknesses:** The "Speed (1/time)" and "Efficiency (1/energy)" inversions are correct but slightly unintuitive -- a reader might need a moment. The grey mass of 209 dominated configs is quite dense at the bottom and obscures some structure. Axis label "Normalised Score (higher = better)" is good but could be more prominent.
**Verdict:** Very effective. Communicates the multi-objective trade-off far better than the 3D plot.

### 4. pareto_tradeoff_simple.png -- 8/10
**What it shows:** 2D summary: Mission Effectiveness (detection x coverage) vs Mission Cost (normalised time + energy). Five key configs plotted with distinct markers, labels, and a grey arrow from "Cheap but risky" to "Expensive but reliable."
**Strengths:** Brilliant simplification. Reduces the entire optimization to one intuitive scatter. The arrow narrative (cheap-risky to expensive-reliable) is immediately understandable. Each config is labelled with altitude + speed. The blue shaded region around the selected config draws the eye. Marker shapes are distinct (diamond, triangle, star, square, circle).
**Weaknesses:** The "25 m, 8 m/s" label partially overlaps the "35 m, 8 m/s (SELECTED)" label -- needs a few pixels of separation. The y-axis label wraps to two lines which looks slightly cramped. The shaded blue region's purpose isn't explained in the figure itself (is it a confidence interval? acceptable region?).
**Verdict:** Strong executive summary figure. Would work well early in the optimization section.

### 5. top3_paths.png -- 5/10
**What it shows:** Three side-by-side map views of the top 3 lawnmower path configurations, with search area, NFZ, flight boundary, and path overlay.
**Strengths:** Good idea -- shows how different configs produce different physical paths. The NFZ hatching (red) is clear. Turn markers and take-off point are visible. Stats below each panel (altitude, angle, speed, lanes, time, energy) are useful.
**Weaknesses:** The figure is too small to read comfortably. The text below each panel is tiny -- would be illegible at typical report column width. The three panels are cramped. The path colors (blue, orange, green) against the grey background don't pop. The legend bar at the bottom is minuscule. The NFZ buffer region is hard to distinguish from the NFZ itself. At this size, the individual waypoints blur together.
**Verdict:** Needs to be larger. Either make it full-width or drop to 2 panels. The stats text must be at least 8pt when printed. Currently too dense for its allocated space.

### 6. tornado_sensitivity.png -- 9/10
**What it shows:** Tornado/sensitivity diagram showing how each parameter (+/-20% variation) affects the composite mission score. Altitude has the largest swing, speed the smallest.
**Strengths:** Textbook-perfect tornado diagram. Immediately readable -- altitude dominates, speed barely matters. The delta values on the right (0.09, 0.04, 0.03, 0.02, 0.01) quantify the sensitivity precisely. Color coding (blue = improves, red = worsens) is intuitive. Baseline dashed line at 0.89 is clear. Subtitle explains the methodology. Parameters are ordered by sensitivity (correct convention).
**Weaknesses:** Very minor: the baseline value "0.89" overlaps slightly with the "0.85" label on the Speed bar. Could add the baseline parameter values in the y-axis labels (already partially there for some).
**Verdict:** One of the best figures. Clean, informative, immediately actionable. Keep as-is.

### 7. altitude_tradeoff_dual.png -- 7/10
**What it shows:** Dual-panel plot. Left: benefits of increasing altitude (ground footprint, coverage rate, lane reduction, energy saving). Right: costs (target pixel size, detection confidence, NFZ intrusion risk, GPS estimation error).
**Strengths:** Excellent concept -- the benefits-vs-costs framing is pedagogically strong. The "selected 35m" vertical dashed line appears in both panels, anchoring the discussion. Multiple curves on each panel show the multi-faceted nature of the trade-off. The "better" arrow on the left panel helps interpretation.
**Weaknesses:** Too small as rendered -- the axis labels and curve labels are hard to read. The right panel has 4 curves with different y-axis scales (pixels, %, meters, meters) all mapped to one axis labelled "Pixel size / Confidence" and a secondary axis "Distance (m)" -- this is confusing. The NFZ intrusion risk line (purple dashed) is hard to see against the grid. The "higher" arrow on the right panel points at what exactly? Left panel: "mixed units" y-axis is inherently problematic. The legend entries are small.
**Verdict:** Strong concept, weak execution. The dual-axis problem on the right panel needs fixing -- either separate the 4 curves into sub-panels or normalize them. As-is, a reader cannot extract actual values from the right panel.

### 8. function_chain.png -- 7/10
**What it shows:** Functional dependency tree showing how detection probability (P_detect) depends on intermediate quantities (n_frames, p_single) down to controllable parameters (altitude, focal length, sensor, speed) and fixed parameters (FPS, dummy height, etc.).
**Strengths:** Clean hierarchical layout. Color coding (dark blue = controllable, grey = fixed, salmon = intermediate, red = objective) is clear. Mathematical formulas inside each box connect the variables. Dashed lines show which controllable parameters affect which intermediates. Legend at bottom explains the color scheme.
**Weaknesses:** The dashed blue connection lines are hard to follow -- they cross and overlap. The text inside boxes is small and some formulas are partially cut off or blurry. The "affects 2 quantities" / "affects 3 quantities" annotations at the bottom are useful but small. Some boxes have subscript text that's nearly illegible at print size. The layout could be tighter vertically -- there's wasted space.
**Verdict:** Good systems engineering figure. Would benefit from slightly larger text and cleaner connection lines (perhaps using right-angle routing instead of curves).

### 9. n2_diagram.png -- 4/10
**What it shows:** N-squared (N2) dependency diagram for mission design variables. Variables along the diagonal, dependencies as dots in off-diagonal cells. Color coding for variable types (blue = decision, green = fixed, grey = derived, red/green = objectives).
**Strengths:** Classic SE tool, appropriate for the report. The variable key at the bottom lists all 19 variables. Color coding distinguishes variable types. Feedforward (black dots) vs feedback (red dots) dependencies are differentiated.
**Weaknesses:** Far too small to read. The diagonal labels are tiny -- I can barely make out "Target size", "Focal length", "Speed" etc. The off-diagonal dots are so small they could be rendering artifacts. The variable key at the bottom is legible but the diagram itself isn't. There are 19 variables making this a 19x19 grid, which is ambitious for a figure that will be maybe 8cm wide in a report. The white space around the diagram is excessive. Row/column numbers (1-19) are present but the corresponding variable names on the diagonal are illegible.
**Verdict:** Needs significant rework. Either reduce to the 8-10 most important variables, or make this a full-page figure. At current size, it communicates nothing -- a reader would skip it. The concept is right but the execution fails at print scale.

### 10. objective_conflict.png -- 8/10
**What it shows:** Six radar/spider charts comparing different configurations across 5 objectives (Coverage, Detection, 1/Time, 1/Energy, Safety). Each labelled with its strategy (max detection, SELECTED, max speed, energy efficient, worst of both, energy optimal) plus a "balance" score.
**Strengths:** Immediately shows WHY the selected config (B) is best -- it's the most balanced polygon. The "worst of both" config (E) is obviously poor. Each config is color-coded distinctly. The balance scores below each chart quantify the visual impression. Labels explain each config's strategy in plain English.
**Weaknesses:** The 1/Time and 1/Energy inversions (necessary for "higher = better" consistency) may confuse readers unfamiliar with the convention. Config B (Selected) at 0.536 balance isn't dramatically higher than D (0.475) -- the visual difference is subtle. Some axis labels overlap at the 0.5 gridline. The figure is quite wide -- 6 panels may be tight at column width.
**Verdict:** Very effective comparison tool. The six-panel layout works because each panel is simple. Good for justifying the selected configuration.

---

## TOP 5 BEST FIGURES (ranked)

| Rank | Figure | Score | Why |
|------|--------|-------|-----|
| 1 | tornado_sensitivity.png | 9 | Textbook-perfect. Instantly readable, quantified, correctly ordered. Zero confusion. |
| 2 | pareto_curve.png | 9 | Publication-quality Pareto frontier. Rich but not cluttered. Three dimensions encoded cleanly. |
| 3 | pareto_parallel.png | 8 | Best multi-objective visualization. 5 dimensions readable at a glance. |
| 4 | pareto_tradeoff_simple.png | 8 | Brilliant executive summary. Reduces complex optimization to one intuitive plot. |
| 5 | objective_conflict.png | 8 | Strong justification tool. Six configs compared visually and quantitatively. |

---

## FIGURES NEEDING IMPROVEMENT (ranked by urgency)

| Priority | Figure | Score | Fix needed |
|----------|--------|-------|------------|
| 1 | n2_diagram.png | 4 | CRITICAL: illegible at any reasonable print size. Reduce to 8-10 variables OR make full-page. Enlarge all text to minimum 8pt. |
| 2 | top3_paths.png | 5 | Too small, text illegible. Make full-width, increase font size, or drop to 2 panels. Stats text must be readable. |
| 3 | pareto_3d.png | 6 | 3D is inherently poor for static media. Consider moving to appendix since parallel coords covers the same info better. If kept, try a better viewing angle. |
| 4 | altitude_tradeoff_dual.png | 7 | Right panel has mixed-unit y-axis problem. Split into sub-panels or normalize. Increase text size. |
| 5 | function_chain.png | 7 | Connection lines are tangled. Enlarge text in boxes. Use right-angle routing for dependency lines. |

---

## SUMMARY

- **Average score: 7.1/10** across all 10 figures
- **3 figures are report-ready** (pareto_curve, tornado_sensitivity, and the 3 scoring 8)
- **2 figures need urgent rework** (n2_diagram is borderline unusable, top3_paths too cramped)
- **Key theme:** many figures are too small for print. Design for 8cm column width at 300 DPI. If text is below 7pt when printed, readers will skip the figure entirely.
