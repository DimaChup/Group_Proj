# Figure Review: reportflow/main.tex

Review of all 8 figures for correctness, placement, caption quality, and narrative fit.

---

## Figure-by-Figure Assessment

### Fig 1: decision_flow.png -- Decision Flow Infographic
- **Placement**: CORRECT. Opens the document before Section 1. Sets up the entire logical chain the reader is about to walk through.
- **Content**: Clean flowchart: target size -> altitude -> speed -> scan angle -> NFZ -> final config. Matches the 5-step chain described in Section 3 exactly.
- **Caption**: Good. Describes the sequential chain clearly.
- **Verdict**: PERFECT placement. This is the "map" for the whole document -- seeing it first lets the reader follow the detailed reasoning without getting lost.

### Fig 2: sensitivity_matrix.png -- Sensitivity Matrix
- **Placement**: CORRECT. Appears in Section 2 ("The Variables We Control") right after Table 1 lists the variables. The text says "The coupling structure is shown in Figure X: darker cells indicate stronger influence" and this is exactly what the figure shows.
- **Content**: 5x5 heatmap of input variables vs performance metrics with numerical annotations. Color-coded green (improves) / red (worsens). Very informative.
- **Caption**: Good. Could add "Green cells indicate that increasing the input improves the metric; red indicates worsening" but the footnote on the figure itself already says this.
- **Verdict**: GOOD. Correctly placed. One observation: there is also a `coupling_matrix.png` in figs/ which shows pairwise *variable-to-variable* coupling (Strong/Medium/Weak). The sensitivity_matrix is the right choice here because it maps variables to *objectives*, which is what Section 2 is about. The coupling_matrix would be redundant.

### Fig 3: altitude_speed_tradeoff.png -- Altitude-Speed Trade-off
- **Placement**: CORRECT. Appears in Section 3 after paragraphs 1-3 explain the altitude ceiling (63m), safety margin (35m), and speed limit (8m/s). The figure visualises the 2D trade-off space with the selected point marked.
- **Content**: Filled contour plot of composite score vs altitude and speed. Blue contours for detection probability, orange for coverage time. Star at (35m, 8m/s). High quality.
- **Caption**: GOOD. Explains the colour encoding, contour meanings, and why the selected point is where it is. Detailed and helpful.
- **Verdict**: PERFECT. This is the key figure for the altitude/speed decision -- exactly where it should be.

### Fig 4: real_energy_heatmap.png -- Energy Heatmap (Altitude x Scan Angle)
- **Placement**: CORRECT. Appears after paragraph 4 ("What scan angle minimises energy?"). The text describes sweeping 36 angles and finding 70deg optimal.
- **Content**: Heatmap of energy (Wh) vs scan angle and altitude. Clear low-energy valley at ~70deg. Red star at global minimum (50m, 70deg).
- **Caption**: GOOD. Mentions the 65-75deg valley, the global minimum, and quantifies the energy trade-off for choosing 35m over 50m.
- **Issue**: The figure title says "darker = less energy = better" but the colormap is viridis (dark purple = low energy). The visual is clear but the caption text says "low-energy valley" which correctly describes the dark band. Minor: the red star annotation says "Best: 50m, 70d, 8.3 Wh" but the caption says the selected point trades 4.4 Wh -- this math checks out (12.6 - 8.2 ~ 4.4).
- **Verdict**: GOOD placement and content. No issues.

### Fig 5: top3_paths.png -- Top 3 Lawnmower Configurations
- **Placement**: CORRECT. Appears in Section 4 ("What We Evaluated") after Table 3 lists the top 3 configurations. The figure shows what those three patterns actually look like on the polygon.
- **Content**: Three side-by-side panels showing scan paths over the survey polygon with NFZ and buffer zones marked. Clear labels with altitude, angle, speed, energy, time stats.
- **Caption**: GOOD. Identifies each panel clearly.
- **Issue**: The figure is quite small/compressed. At 0.85\linewidth the three panels are narrow. Consider using `width=\linewidth` or even making it wider. But this is a formatting issue, not a placement issue.
- **Verdict**: GOOD. Correctly placed right after the table it illustrates.

### Fig 6: tornado_sensitivity.png -- Tornado Diagram
- **Placement**: CORRECT. Opens Section 6 ("Sensitivity and Robustness"). The text says altitude is most influential and scan angle has a flat optimum -- both visible in the chart.
- **Content**: Horizontal bar chart showing +/-20% perturbation effects on composite score. Altitude has the widest bar (delta=0.09), speed the narrowest (delta=0.01). Clear blue/red coding.
- **Caption**: GOOD. Explains what each bar represents and highlights the key finding.
- **Issue**: Minor caption discrepancy -- text says "a +/-5m change has nearly double the effect of a +/-2m/s speed change". The tornado shows +/-20% perturbation from baseline, not fixed units. At 35m, +/-20% = +/-7m; at 8m/s, +/-20% = +/-1.6m/s. The text's "5m" and "2m/s" don't match the figure's methodology. This should be corrected in the body text to say "+/-20% perturbation" or the specific values should match.
- **Verdict**: GOOD placement, minor text-figure mismatch on perturbation values.

### Fig 7: sensitivity_spider.png -- Spider/Radar Plot
- **Placement**: CORRECT. Immediately follows the tornado chart in the same section. The text uses it to argue the design is "robust to moderate perturbations" based on the compact polygon.
- **Content**: 5-axis radar (Detection, Coverage, NFZ Safety, Energy, Time) showing the selected configuration's normalised scores. NFZ Safety = 1.0, Coverage = 0.96, Detection = 0.93, Time = 0.38, Energy = 0.40.
- **Caption**: Adequate but could be better -- it talks about "polygon area" indicating sensitivity footprint, but what the figure actually shows is *performance* on each objective (not sensitivity). The title on the figure itself says "Selected Configuration Performance" which is accurate. The caption's framing as "sensitivity footprint" is misleading -- this is a performance profile, not a sensitivity diagram. The tornado chart already shows sensitivity. This figure shows where the selected config excels (safety, coverage, detection) and where it's weaker (time, energy).
- **Issue**: CAPTION MISMATCH. The caption says "Spider plot of normalised sensitivities" but the figure shows *performance scores*, not sensitivities. Recommend rewriting the caption to: "Radar plot of the selected configuration's normalised performance across all five objectives. High scores on safety, detection, and coverage confirm the priority stack; lower scores on time and energy reflect acceptable trade-offs."
- **Verdict**: CORRECT placement but CAPTION NEEDS FIXING. The figure content is right; the caption describes it incorrectly as a "sensitivity" plot.

### Fig 8: pareto_parallel.png -- Parallel Coordinates
- **Placement**: CORRECT. Appears in Section 7 ("Pareto Optimality") as the culminating visualisation. Shows all 216 configurations across 5 objectives, with 7 Pareto-optimal ones highlighted and the selected config in blue.
- **Content**: Parallel coordinates with 5 axes (Coverage, Detection Probability, Speed, Efficiency, Safety). 209 dominated configs in grey, 7 Pareto-optimal in orange, selected in blue. Clear and informative.
- **Caption**: GOOD. Explains the colour coding and what "balanced performance" means.
- **Issue**: The selected config (blue) scores middling on Speed (1/time) and Efficiency (1/energy) but high on Detection and decent on Coverage and Safety. This is consistent with the priority stack (safety > detection > speed > energy). The figure effectively shows the selected config is NOT the best on any single axis but avoids being worst on any.
- **Verdict**: PERFECT. Strong closing figure that wraps up the optimisation story.

---

## Narrative Flow Assessment

The 8 figures follow a logical progression:

1. **decision_flow** -- Here is the chain (overview)
2. **sensitivity_matrix** -- Here are the variables and what they affect
3. **altitude_speed_tradeoff** -- Here is how we picked altitude and speed
4. **real_energy_heatmap** -- Here is how we picked scan angle
5. **top3_paths** -- Here are the best candidates and what they look like
6. **tornado_sensitivity** -- Here is how sensitive the result is
7. **sensitivity_spider** -- Here is the selected config's performance profile
8. **pareto_parallel** -- Here is proof it sits at the Pareto knee

This sequence is CORRECT and tells a complete story: problem -> variables -> optimisation -> result -> validation.

---

## Missing Figures

### objective_conflict.png -- SHOULD BE INCLUDED
This is a 6-panel radar chart comparing six different configurations (20m/6m/s, 35m/8m/s SELECTED, 50m/10m/s, etc.) with balance scores. It would be extremely valuable in **Section 4 (What We Evaluated)** or as a companion to the top3_paths figure. It visually shows *why* the selected configuration wins: it has the most balanced/circular polygon (balance=0.536) while every other config is lopsided.

**Recommendation**: Insert after top3_paths (Fig 5), before Section 5. The table gives numbers; top3_paths shows geometry; objective_conflict shows *why the selected config is balanced*. This is the missing "aha" visualisation. Suggested caption:

> "Objective conflict radar charts for six representative configurations. The selected configuration (B, blue) achieves the most balanced polygon (balance score 0.536), while alternatives sacrifice one or more objectives: A maximises detection but wastes energy; C maximises speed but detection drops below acceptable levels."

### detection_envelope.png -- CONSIDER ADDING
Shows detection confidence vs altitude with motion blur curves. Would strengthen paragraph 1 of Section 3 (the altitude ceiling argument) by showing the 63m ceiling visually rather than stating it. Currently the altitude ceiling is asserted but not shown.

**Recommendation**: Optional. The text is clear enough without it, and the altitude_speed_tradeoff figure covers the altitude dimension. But if space permits, it would add rigour to the detection ceiling claim.

### pareto_curve.png -- NOT NEEDED
2D Pareto frontier (Detection Probability vs Mission Time) with altitude colour coding. The parallel coordinates plot (pareto_parallel) already covers this in a more comprehensive way (5 objectives vs 2). Including both would be redundant.

### coupling_matrix.png -- NOT NEEDED
Variable-to-variable coupling (Strong/Medium/Weak). The sensitivity_matrix already covers variable-to-objective coupling, which is more relevant to the narrative. Including both would be redundant and confusing.

---

## Issues Found

| # | Figure | Issue | Severity |
|---|--------|-------|----------|
| 1 | sensitivity_spider (Fig 7) | Caption says "normalised sensitivities" but figure shows performance scores | HIGH -- misleading |
| 2 | tornado_sensitivity (Fig 6) | Body text says "+/-5m" and "+/-2m/s" but figure uses +/-20% perturbation (= +/-7m and +/-1.6m/s) | MEDIUM -- factual mismatch |
| 3 | top3_paths (Fig 5) | Figure is compressed at 0.85\linewidth; three panels are very small | LOW -- readability |
| 4 | (missing) objective_conflict | Best available figure for showing WHY balanced config wins; not included | MEDIUM -- missed opportunity |

---

## Recommended Actions

1. **FIX Fig 7 caption** (sensitivity_spider): Change "Spider plot of normalised sensitivities. Polygon area indicates the overall sensitivity footprint. A compact polygon means the design is robust to perturbations." to something like: "Radar plot of the selected configuration's normalised performance across all five objectives. High scores on safety (1.00), coverage (0.96), and detection (0.93) confirm adherence to the priority stack. Lower scores on time (0.38) and energy (0.40) reflect deliberate trade-offs."

2. **FIX body text for Fig 6** (tornado): Change "a +/-5m change has nearly double the effect of a +/-2m/s speed change" to "a +/-20% altitude perturbation (+/-7m) has nearly double the score impact of a +/-20% speed perturbation (+/-1.6m/s)".

3. **ADD objective_conflict.png** after Fig 5 (top3_paths) in Section 4. This is the strongest visual argument for WHY the selected configuration wins -- no other figure shows this multi-config comparison.

4. **OPTIONAL**: Widen top3_paths to `\linewidth` for better readability of the three panels.
