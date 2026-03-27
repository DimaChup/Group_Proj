# Optimization Figures Review

Reviewed: 2026-03-27 | 8 figures total

---

## 1. N2 Dependency Diagram (`n2_diagram.png`)

**What it claims:** N2 diagram showing design variable dependencies for the search mission.

**Assessment:**
- Shows 18 variables along the diagonal (decision variables in blue, fixed/calculated in grey, derived in green, objectives in red). This is a proper N2 layout.
- Feedforward (black dots above diagonal) and feedback (red dots below diagonal) coupling shown correctly. The feedback loops (e.g., detection probability feeding back to coverage) are plausible.
- Variable key at bottom lists all 18 variables but the text is quite small -- borderline readable at print size.
- **Does it show sensitivity?** No. An N2 diagram shows *structural* dependencies (which variables affect which), not sensitivity magnitude. The user asked whether the N2 shows sensitivity -- it does not and should not. That is the job of the sensitivity matrix. The N2 correctly shows coupling structure only.
- The colored boxes on the diagonal clearly distinguish variable types. Good use of the legend.
- Minor issue: some of the variable labels inside boxes are hard to read due to small font on the colored backgrounds.

**Plausibility:** Correct. The dependency links make physical sense (altitude affects footprint, footprint affects coverage rate, speed affects frames-on-target, etc.).

**Score: 7/10** -- Structurally correct N2, good color coding, but text readability is marginal at smaller print sizes. Would benefit from slightly larger font in the diagonal boxes.

---

## 2. Sensitivity Matrix (`sensitivity_matrix.png`)

**What it claims:** Input variables vs performance metrics, showing influence strength and direction.

**Assessment:**
- 5 input variables (rows: altitude h, ground speed v, scan angle theta, overlap fraction alpha, NFZ margin d_nfz) vs 5 performance metrics (columns: coverage %, detection P, mission time, energy Wh, NFZ risk).
- Each cell shows a signed value (e.g., +0.6, -0.3) with a brief explanation, color-coded green (improvement) to red (worsening).
- The footnote clarifies: "increasing input improves metric (+green) or worsens it (-red)". This is correct and clearly labeled.
- **Key checks:**
  - Altitude +0.6 coverage (wider lanes) -- correct, higher = wider footprint = fewer lanes.
  - Altitude -0.3 detection (smaller target) -- correct, higher = smaller pixel target.
  - Altitude -0.5 mission time (fewer lines) -- correct, fewer lanes = less flight time.
  - Speed -0.4 detection (fewer frames) -- correct, faster = fewer frames on target.
  - Speed -0.7 mission time (faster cover) -- correct and strongest effect, makes sense.
  - NFZ margin -0.9 NFZ risk (much safer) -- correct, larger buffer = much safer.
  - NFZ margin -0.4 coverage (less area) -- correct, larger buffer eats into searchable area.
- All signs and magnitudes are physically plausible. No contradictions found.
- Color scale bar on right clearly shows the -1 to +1 range.
- The brief text annotations inside each cell (e.g., "wider lanes", "fewer frames") are excellent -- they explain the mechanism, not just the number.

**Score: 9/10** -- Excellent figure. Clear, correct, well-labeled, with mechanism explanations. The only minor improvement would be making the cell text slightly larger for print.

---

## 3. Coupling Matrix (`coupling_matrix.png`)

**What it claims:** Pairwise interaction effects between the 5 design variables.

**Assessment:**
- Symmetric 5x5 matrix with diagonal showing self-effects. Off-diagonal cells show coupling strength (Strong/Medium/Weak/Independent) with color coding (red/yellow/green/light green).
- Each cell includes a brief mechanism explanation.
- **Key checks:**
  - Altitude-Speed: Strong coupling (coverage rate + detection probability) -- correct, these two jointly determine how many frames see the target and how much ground is covered per pass.
  - Altitude-Scan angle: Weak -- plausible, scan angle mainly affects turn count, altitude mainly affects lane width; they are relatively independent.
  - Altitude-Overlap: Medium (lane spacing) -- correct, overlap fraction modifies effective lane spacing which depends on footprint width (altitude-dependent).
  - Speed-NFZ margin: Medium (reaction distance) -- correct, faster speed = less time to react near NFZ boundary.
  - Scan angle-NFZ margin: Medium (NFZ proximity) -- reasonable, scan angle affects how close the pattern gets to boundaries.
  - Overlap-NFZ margin: Weak/Independent -- plausible, overlap doesn't directly affect safety distance.
- The matrix is symmetric as expected for pairwise coupling.
- Color scheme is intuitive and consistent.

**Score: 8/10** -- Well constructed, correct coupling classifications, good mechanism annotations. The "Self (primary metric)" diagonal labels are a nice touch. Slightly less impactful than the sensitivity matrix because coupling strengths are qualitative (Strong/Medium/Weak) rather than quantitative.

---

## 4. Pareto Frontier (`pareto_2d_composite.png`)

**What it claims:** Pareto frontier from 216 configuration sweep, projecting 5 objectives into 2 composite dimensions.

**Assessment:**
- X-axis: "Mission Effectiveness (coverage x detection probability)" -- a composite of 2 objectives.
- Y-axis: "Mission Cost (normalised time + energy)" -- a composite of 2 more objectives.
- Color: Altitude (m), shown via colorbar on right.
- The subtitle explicitly states: "This 2D view collapses 5 objectives into 2 composite dimensions." This directly answers the question -- yes, the 5D-to-2D projection is clearly stated.
- 216 points = plausible grid (e.g., 6 altitudes x 6 speeds x 6 overlaps = 216).
- Pareto frontier line connects the non-dominated points along the top-right edge -- correct placement (high effectiveness, low cost is top-right which would be bottom-right... let me check).
  - Actually: high effectiveness (right) + low cost (bottom) is the ideal corner. The Pareto frontier curves from bottom-right toward upper-right. This is correct -- it shows the trade-off envelope.
- Four labeled configurations:
  - "Best detection (20 m, 6 m/s)" -- low altitude, slow speed, high effectiveness but high cost. Makes sense.
  - "Selected (35 m, 8 m/s)" -- balanced point, clearly marked. Good.
  - "Energy-optimal (50 m, 6 m/s)" -- high altitude, on the frontier.
  - "Fastest (50 m, 14 m/s)" -- high altitude, fast, lowest cost but lower effectiveness.
- The color gradient showing altitude is informative -- you can see low altitude (purple/blue) clusters at high effectiveness but high cost.
- **Issue:** The 5th objective (NFZ safety) is not visually represented. It is presumably folded into one of the composites or used as a constraint. This could be clearer.

**Score: 8/10** -- Strong figure. The 5D-to-2D statement is present and clear. The labeled operating points tell a compelling story. Loses a point because the 5th objective (safety/NFZ) role is not explicitly shown, and the Pareto frontier line could be slightly more prominent.

---

## 5. Altitude Tradeoff Dual (`altitude_tradeoff_dual.png`)

**What it claims:** "The Altitude Dilemma: Competing Effects" -- benefits vs costs of increasing altitude.

**Assessment:**
- Left panel (Benefits): ground footprint (linear increase), coverage rate (x10 m^2/s, increases), lane reduction (decreasing curve -- fewer passes), energy saving (mWh^-1, increases). All increase with altitude = all benefits.
- Right panel (Costs): target size (px, decreases hyperbolically), detection confidence (%, decreases), NFZ intrusion risk (m, increases with altitude as footprint widens), GPS estimation error (m, increases slightly).
- The "selected 35 m" vertical dashed line appears on both panels -- excellent for showing the chosen operating point.
- **Plausibility checks:**
  - Target size decreasing as 1/h^2 (area) or 1/h (linear dimension) -- the curve looks roughly hyperbolic, consistent with 1/h scaling for pixel size. Correct.
  - Detection confidence dropping from ~95% at 15m to ~60% at 55m -- plausible for a small target model.
  - Ground footprint linear in h -- correct (FOV * altitude).
  - NFZ intrusion risk increasing -- makes sense, wider footprint at higher altitude means edges get closer to NFZ.
- Right panel has dual y-axes (pixel size/confidence on left, distance in meters on right). This is clear.
- "better" and "higher" arrows indicate the favorable direction on each panel -- good.

**Score: 9/10** -- Excellent dual-panel figure. Clearly demonstrates the fundamental altitude trade-off. The "selected 35 m" marker ties it to the design decision. Physically plausible curves. Only minor issue: the left panel y-axis label says "mixed units" which is honest but slightly awkward -- an examiner might prefer separate y-axes or normalized values.

---

## 6. Function Chain (`function_chain.png`)

**What it claims:** Detection probability functional dependency chain.

**Assessment:**
- Top level: P_detect (red, mission objective) with formula 1-(1-p)^n.
- Second level: n_frames (number of frames on target) and p_single (single-frame detection probability).
- Third level: W_foot (footprint width), delta_px (pixel spacing), p_blur (blur probability).
- Bottom level: controllable parameters (blue: altitude h, speed v, overlap eta), fixed parameters (grey: focal f, sensor w_s, FPS f_ps, t_exp, H_s dummy height).
- Lines show which parameters feed into which intermediate quantities.
- **Formula check:** P_detect = 1-(1-p)^n is the standard independent-trials detection formula. Correct.
- The decomposition from mission objective down through intermediate quantities to controllable parameters is textbook systems engineering (functional decomposition).
- Color coding is clear: red=objective, orange=intermediate, blue=controllable, grey=fixed.

**Plausibility:** All the dependency links are physically correct (altitude affects footprint width, speed affects pixel spacing and blur, etc.).

**Score: 8/10** -- Clean functional decomposition diagram. Formulas are visible in the boxes. Good color hierarchy. Would score higher if the formulas were slightly more readable (some are small) and if there were units annotated on the intermediate quantities.

---

## 7. Objective Conflict Radar (`objective_conflict.png`)

**What it claims:** Six configurations compared on 5 objectives via radar/spider charts, showing how objectives conflict.

**Assessment:**
- Six radar charts (A through F) each showing 5 axes: Coverage, Detection, 1/Time, 1/Energy, Safety.
- Using 1/Time and 1/Energy (inverses) so that "bigger is better" on all axes -- correct normalization for radar charts.
- Each configuration labeled with altitude and speed.
- "balance" score shown below each (standard deviation-based? lower = more balanced shape).
- **Key observations:**
  - A (20m, 6 m/s, max detection): high detection, low coverage, low 1/Time -- makes sense, low/slow = good detection but slow coverage.
  - B (35m, 8 m/s, SELECTED): most balanced shape (balance=0.576, highest). The pentagon is the most regular. This correctly shows why this was selected -- best balance.
  - C (50m, 10 m/s, max speed): high coverage and 1/Time but low detection -- correct, fast/high covers ground but misses targets.
  - D (35m, 6 m/s, energy efficient): similar to B but slower, good energy -- plausible.
  - E (20m, 10 m/s, worst of both): low on multiple axes -- labeled honestly as "worst of both", irregular shape.
  - F (50m, 6 m/s, energy optimal): high 1/Energy and coverage but low detection -- makes sense.
- The visual clearly shows objective conflicts: no single configuration fills all axes.
- Balance scores are consistent with visual shape regularity.

**Score: 8/10** -- Effective visualization of multi-objective trade-offs. The "SELECTED" label on B draws attention to the design choice. Balance metric adds quantitative backing. Minor issue: the radar chart axes could use tick mark labels (0.2, 0.4, etc. are shown as concentric circles but values are small).

---

## 8. Altitude-Speed Tradeoff Heatmap (`altitude_speed_tradeoff.png`)

**What it claims:** Composite mission score across altitude-speed design space.

**Assessment:**
- X-axis: Altitude h (m), 20-50. Y-axis: Ground speed v (m/s), 6-15.
- Color: composite score (detection + coverage + energy) -- green = better, red = worse.
- Overlaid contours: detection probability iso-lines (blue dashed, P_d=90%, 99%) and coverage time iso-lines (brown dash-dot, t_cov=120s, 180s).
- Operating point marked with star at (35m, 8 m/s) labeled "Selected".
- **Plausibility:**
  - Green region (high score) is at moderate-high altitude and moderate speed -- this makes sense as the sweet spot between coverage efficiency and detection probability.
  - Red regions at low altitude + high speed (top-left) -- correct, fast at low altitude = blur + excessive energy.
  - Red at low altitude + low speed (bottom-left) -- this should actually be decent for detection... The red here likely reflects very slow coverage (high time cost) which hurts the composite. Plausible if time is weighted.
  - Detection probability contours decrease with altitude and speed -- correct (smaller target + fewer frames).
  - Coverage time contours decrease as speed increases -- correct.
- The selected point at 35m/8m/s sits in the green zone, above the P_d=90% line and near the t_cov=120s line. Good design justification.
- Color bar label: "Composite score (detection + coverage + energy)" -- clear.

**Score: 9/10** -- Excellent figure. The overlay of detection probability and coverage time contours on the composite score heatmap is a powerful way to show the multi-objective trade-off in 2D. The selected operating point is well-justified visually. Professional quality. Only suggestion: add a small note about what weights were used in the composite.

---

## Summary Table

| # | Figure | Correct? | Clear? | Shows claim? | Examiner impact | Score |
|---|--------|----------|--------|-------------|-----------------|-------|
| 1 | N2 Diagram | Yes | Marginal text size | Shows structure, not sensitivity (correct for N2) | Good | 7/10 |
| 2 | Sensitivity Matrix | Yes | Excellent | Yes, influence strength + direction | Impressive | 9/10 |
| 3 | Coupling Matrix | Yes | Good | Yes, pairwise interactions | Good | 8/10 |
| 4 | Pareto Frontier | Yes | Good | Yes, explicitly states 5D to 2D | Impressive | 8/10 |
| 5 | Altitude Tradeoff Dual | Yes | Excellent | Yes, competing effects | Very impressive | 9/10 |
| 6 | Function Chain | Yes | Good | Yes, functional decomposition | Good | 8/10 |
| 7 | Objective Conflict Radar | Yes | Good | Yes, multi-objective conflict | Good | 8/10 |
| 8 | Altitude-Speed Heatmap | Yes | Excellent | Yes, composite trade-off | Very impressive | 9/10 |

**Overall average: 8.25/10**

## Answers to Specific Questions

1. **Does the N2 show sensitivity?** No, and it should not. The N2 correctly shows *structural coupling* (which variables affect which). Sensitivity magnitudes are shown in the separate sensitivity matrix. This is the correct division of information.

2. **Is the sensitivity matrix labeled correctly?** Yes. The title says "Input Variables vs Performance Metrics", the colorbar says "Influence strength", the footnote explains the sign convention. Each cell has both a numerical value and a mechanism explanation. Correctly labeled.

3. **Does the Pareto clearly state 5D to 2D projection?** Yes. The subtitle at the bottom explicitly reads: "This 2D view collapses 5 objectives into 2 composite dimensions." The axis labels also clarify what each composite dimension contains.

## Recommendations

1. **N2 diagram:** Increase font size in diagonal boxes and variable key. Consider A3 or landscape orientation if space allows.
2. **Pareto:** Add a brief note about how safety (5th objective) is handled -- is it a constraint or folded into one axis?
3. **Altitude-speed heatmap:** State the composite weights (e.g., "equal weights" or specific values).
4. **Function chain:** Add units to intermediate quantities (e.g., W_foot in meters, delta_px in pixels).
5. **General:** All figures are publication-quality. No mathematical errors detected. The set collectively tells a coherent optimization story: problem structure (N2) -> sensitivity analysis -> coupling -> functional decomposition -> trade-off visualization -> Pareto selection -> design justification.
