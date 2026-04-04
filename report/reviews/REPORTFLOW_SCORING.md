# Reportflow Scoring Assessment

Scored: 2026-04-04
File: `report/reportflow/main.tex` (1102 lines, ~27 pages)
Compared against: `report/main.tex` (goldmine, ~238 pages, 29 appendices, 118 citations)

---

## 1. RUBRIC CRITERIA SCORES

### Specialist Skills & Problem-Solving (40%) -- Score: 79/100

**Strengths:**
- Rigorous 216-configuration parametric sweep with physics-based energy model (momentum theory + parasitic drag)
- Complete scoring framework: 5 dimensions, multiplicative detection composite, constraint-vs-objective split well justified
- 9-step sequential decision chain with explicit "why this comes now" reasoning at each step
- Energy model fully derived: hover power, forward flight, turn cost, NFZ speed ramp penalty
- Safety score decomposed into 6 weighted sub-elements with equations
- Detection score: 4 sub-factors (confidence, frames, cumulative probability, pixel size) as a product -- good reasoning for multiplicative vs additive
- Pareto analysis, tornado sensitivity, spider charts, parallel coordinates -- multi-view optimisation evidence
- System description section covers architecture, state machine, CV pipeline, GPS estimation
- Attitude compensation math (rotation matrix, 1440 automated tests, error reduction 6.2m -> 0.3m)
- Error budget table with 5 sources and magnitudes
- GSD calculation shown explicitly
- 58 test scripts + 127 unit tests referenced with specific validation examples
- 4 evidence-based corrections (BGR fix, focal length, TFLite coords, calibration corruption) -- strong adaptive engineering

**Weaknesses:**
- **No GPS estimation deep dive.** The goldmine has a 387-line appendix (localization_approaches.tex) surveying 10 approaches with math, pros/cons, accuracy estimates, and suitability ratings. The reportflow has a 1-paragraph "Detection-to-GPS Pipeline" subsection. This is the single biggest content gap.
- **No attitude compensation derivation.** The reportflow mentions it in 3 sentences (line 832) but the goldmine has a full section with the rotation matrix, verification methodology, and literature comparison. The reportflow just says "ray-tracing each detection through the full rotation matrix" without showing WHY this works or comparing to alternatives.
- **No field day results section.** The goldmine has a full appendix (11_field_results.tex) with bench results, FOV calibration procedure, lens distortion calibration, inference benchmarks with tables. The reportflow mentions these as facts but never presents the methodology or data.
- **No SAR comparison table.** The goldmine has a table comparing against AUSPEX, Sambolek, Drones+YOLO, SearchWing with FPS, mAP, GPS accuracy, plus radar chart. The reportflow has zero external comparison.
- **No detection montage or real detection images.** No visual evidence of the system actually detecting anything.
- **No mission-level performance estimates.** The goldmine has Table tab:mission-metrics with survey area, coverage rate, search time, detection probability, battery endurance. The reportflow has individual numbers but no consolidated mission-level view.
- **Limited hardware detail.** No BOM table, no Pi system diagram, no hardware photo reference.
- **No precision-recall discussion.** Threshold of 0.4 stated but no PR curve or justification for threshold choice.
- **No train/val overlap acknowledgment.** The goldmine honestly flags mAP50=0.995 as inflated (D5). The reportflow states 0.995 without caveat.

### Decision Making (40%) -- Score: 82/100

**Strengths:**
- STEEPLE analysis: specific, localised, with design impact column. Above-average quality.
- MCDA for inference backend: 4 options, 6 criteria, weighted, with explicit sensitivity analysis showing NCNN retains rank under perturbation. This is well done.
- Priority ordering (safety > detection > time > energy > coverage) clearly stated and consistently applied throughout
- Constraint-vs-objective split: safety and time as pass/fail gates, not continuous scores. This is a mature engineering decision with good justification (paragraph at line 362-364)
- Composite weight robustness tested (+/-10 percentage points)
- "Non-quantifiable design choices" section (line 745-755): speed adaptation, operator-in-the-loop, single-class detector. Shows awareness of decisions outside the model.
- 4 evidence-based corrections demonstrate reflective practice and willingness to change direction
- Plus/delta evaluation is honest about simulation-vs-real gap (7.7/10 vs 2.1/10)

**Weaknesses:**
- **Only 1 MCDA table.** The goldmine has 5 MCDA tables (companion computer, inference backend, search pattern, camera, overall platform). The reportflow has only the inference backend MCDA. This reduces the breadth of formal decision-making evidence.
- **No camera selection rationale.** The goldmine justifies global shutter vs rolling shutter with quantified pixel skew (7.5px), thermal imaging cost analysis, and onboard vs offboard inference comparison. The reportflow mentions "IMX296 global shutter" without justifying WHY.
- **No autonomy justification.** The goldmine has Sheridan framework (L7-8 search / L3-4 landing), asymmetric cost analysis, 20x coverage advantage. The reportflow just says "operator-in-the-loop verification" without a framework.
- **No hardware platform selection.** Why Pi 5? Why not Jetson? The goldmine addresses this in both design rationale and evaluation. The reportflow assumes the hardware.
- **Detection envelope tables cite brightness-adjusted video but don't explain the methodology.** How was "dusk" simulated? The goldmine is similarly vague here but has more supporting evidence elsewhere.
- **No stakeholder analysis beyond STEEPLE.** No named stakeholders (SAR teams, landowner, CAA).

### Communication (20%) -- Score: 75/100

**Strengths:**
- Professional LaTeX: consistent formatting, blue headings, tcolorbox for decision chain, clean tables
- Clear logical flow: objective -> constraints -> dimensions -> scoring -> variables -> coupling -> decision chain -> result -> sensitivity -> Pareto
- Figures well-chosen: spider chart, sensitivity matrix, energy heatmap, altitude-speed tradeoff, top 3 paths, objective conflict, Pareto parallel coordinates, tornado chart
- Tables are dense and informative (detection envelope, speed envelope, top 3 configs, final parameters, energy budget, requirements verification)
- Executive summary is self-contained with all key numbers
- "Because" chain summary (line 627-637) is excellent -- distills the entire decision logic into 7 bullet points

**Weaknesses:**
- **Only ~8 unique citations.** The goldmine uses 118 citations. The reportflow cites only: murphy2014, galceran2013survey, yolov8, ardupilot, tflite, ncnn, synthdata, jarus2019sora, wca1981, choset2001coverage. This is far below what's expected for a technical report at MSc level. Critical missing references: thermal SAR, edge AI, CAA regulations, SORA, DJI comparison, IMX296 datasheet, OpenCV, XNNPACK, Kalman filter theory, photogrammetry, GSD, momentum theory, YOLOv5/v3 comparison papers.
- **No table of contents.** The goldmine has one. For a 27-page document this helps navigation.
- **No hardware photos or screenshots.** Zero visual evidence of the physical system. The goldmine references a mission overview map, Pi system diagram, geofence visualisation, detection montage, ground station screenshot, coverage vs time plot. The reportflow has none of these.
- **No state machine diagram.** Referenced as "20-state finite state machine" but no figure shows it. The goldmine has both a hand-drawn and auto-generated version.
- **No CV pipeline figure.** The goldmine has fig:cv_pipeline showing the 5-stage pipeline visually.
- **No mission overview map.** The goldmine has fig:mission_overview showing the lawnmower pattern on the actual site.
- **No search pattern figure.** The goldmine has fig:search_pattern.
- **No bullseye scatter plot.** The goldmine has gps_bullseye, bullseye_comparison, estimation_heatmap_all. These are compelling visual evidence of GPS accuracy.
- **No detection performance figures.** No conf_vs_alt, det_vs_speed, latency_breakdown, detection_heatmap.
- **No geofence diagram.** The goldmine has a 4-panel figure showing all 5 protection layers.
- **Page budget allocation seems suboptimal.** ~14 pages on optimisation/decision chain, ~5 pages on system description + testing + sim-to-real + evaluation. The goldmine allocates more evenly.

---

## 2. OVERALL SCORES

| Criterion | Weight | Score | Weighted |
|-----------|--------|-------|----------|
| Specialist Skills | 40% | 79 | 31.6 |
| Decision Making | 40% | 82 | 32.8 |
| Communication | 20% | 75 | 15.0 |
| **Total** | | | **79.4** |

**Previous reportflow score: 87.2 (from v6 session).** That score was likely generous and assumed the bibliography and additional sections were stronger than they are. This assessment is calibrated against the goldmine's v7 score of 85.2.

---

## 3. COMPARISON: WHAT THE GOLDMINE HAS THAT THE REPORTFLOW IS MISSING

### Critical Gaps (each worth 2-5 marks)

| Priority | Content | Goldmine Location | Impact | Effort |
|----------|---------|-------------------|--------|--------|
| **1** | **Literature references** (118 vs 8 citations) | Throughout all sections | +5-8 marks across all 3 criteria. The single highest-impact fix. An MSc report with 8 citations looks like it was written in a vacuum. | 2-3 hours: add ~30-40 relevant citations to existing text |
| **2** | **SAR comparison table + radar chart** | evaluation.tex line 148-182 | +3-4 marks (Specialist + Decision). Shows awareness of field, positions contribution. | 1 hour: copy and adapt from goldmine |
| **3** | **GPS estimation deep dive** (10 approaches survey) | localization_approaches.tex (387 lines) | +3-4 marks (Specialist). Currently the weakest subsystem explanation. At minimum, add a table comparing 4-5 approaches with justification for chosen method. | 2 hours: condense the 10-approach survey into a 1-page comparison table with 2-3 sentences per approach |
| **4** | **Attitude compensation derivation** | gps_estimation_deep.tex Part IV | +2-3 marks (Specialist). Currently just a mention. Show the rotation matrix, explain WHY it works, cite the 1440-test verification. | 1 hour: expand the existing 3 sentences to a subsection with the R matrix and verification summary |
| **5** | **Hardware photos / system diagrams** | system_description.tex (mission_overview, pi_system, geofence_diagram, state_machine, cv_pipeline, search_pattern) | +3-5 marks (Communication). A report about a physical drone with zero photos of the drone is a major communication weakness. | 1-2 hours: add 4-6 key figures |
| **6** | **Field day results** (bench testing, calibration data, benchmarks) | 11_field_results.tex | +2-3 marks (Specialist). Currently mentioned as facts but never presented as evidence with tables/procedures. | 1 hour: add a condensed field results subsection |
| **7** | **Mission flow narrative** | mission_flow.tex | +1-2 marks (Specialist + Communication). The goldmine has a full end-to-end narrative from power-on to RTL. The reportflow has a state list but no operational narrative. | 1 hour: add a 0.5-page mission narrative |
| **8** | **Additional MCDA tables** (camera, companion computer, search pattern) | design_rationale.tex lines 83-98, system_description.tex | +2-3 marks (Decision). Multiple trade studies demonstrate systematic decision-making. | 1-2 hours: add 2-3 more MCDA tables |
| **9** | **Detection montage / visual evidence** | evaluation.tex fig:detection_montage | +1-2 marks (Communication). Visual proof the system works. | 30 min: add existing detection montage figure |
| **10** | **Bullseye scatter plots** | estimation_evaluation.tex | +1-2 marks (Specialist + Communication). Compelling visual evidence of GPS accuracy. | 30 min: add existing bullseye figure |

### Lower-Priority Gaps

| Priority | Content | Impact | Effort |
|----------|---------|--------|--------|
| 11 | Autonomy justification (Sheridan framework) | +1 mark (Decision) | 30 min |
| 12 | Table of contents | +0.5 mark (Communication) | 5 min |
| 13 | Train/val overlap caveat on mAP50 | +0.5 mark (Specialist honesty) | 5 min |
| 14 | Mission-level performance estimates table | +1 mark (Specialist) | 30 min |
| 15 | Coverage vs time plot | +0.5 mark (Communication) | 15 min |
| 16 | Ground station description + screenshot | +0.5 mark (Communication) | 30 min |
| 17 | BOM / cost table | +0.5 mark (Specialist) | 15 min |
| 18 | Pi 5 vs Jetson trade-off discussion | +1 mark (Decision) | 30 min |

---

## 4. PRIORITISED ACTION PLAN (for maximum marks per hour)

### Phase 1: Quick Wins (3-4 hours, +10-15 marks estimated)

1. **Add ~35-40 citations** throughout existing text. Every claim about SAR methodology, energy modelling, coverage planning, YOLO, TFLite, NCNN, GPS estimation, ArduPilot, edge AI, camera selection, etc. should cite something. Target: every section has at least 3-5 citations. Use the goldmine's references.bib which already has 109 entries.
2. **Add SAR comparison table** from goldmine's evaluation.tex. Adapt to reportflow context.
3. **Add 4-6 key figures**: state machine diagram, mission overview map, geofence diagram, CV pipeline, detection montage, bullseye scatter. These already exist in `report/figs/`.
4. **Add table of contents** (`\tableofcontents` after title block).
5. **Add mAP50 caveat**: "The 0.995 figure is an upper bound due to train/validation overlap (only 16 of 366 images are real); realistic performance is estimated at 0.85-0.90 based on video replay detection rate."

### Phase 2: Medium Effort (3-4 hours, +8-12 marks estimated)

6. **Add GPS estimation approaches table**: condense 10 approaches from localization_approaches.tex into a comparison table (approach, accuracy, compute cost, suitability). 1 page.
7. **Expand attitude compensation** to a proper subsection with the rotation matrix and verification.
8. **Add field day results subsection**: FOV calibration, lens calibration, inference benchmarks (copy Table tab:benchmark-results from goldmine).
9. **Add 2-3 more MCDA tables** (companion computer, camera, search pattern).
10. **Add mission flow narrative** (0.5 page, condensed from goldmine's mission_flow.tex).

### Phase 3: Polish (2-3 hours, +3-5 marks estimated)

11. Add Sheridan autonomy justification.
12. Add mission-level performance estimates table.
13. Add BOM table.
14. Add Pi 5 vs Jetson trade-off in evaluation.
15. Add coverage vs time plot.
16. Ground station description with screenshot.

### Estimated Final Score After All Phases

| Criterion | Current | After Phase 1 | After Phase 2 | After Phase 3 |
|-----------|---------|---------------|---------------|---------------|
| Specialist | 79 | 84 | 88 | 89 |
| Decision | 82 | 85 | 89 | 90 |
| Communication | 75 | 83 | 86 | 88 |
| **Weighted Total** | **79.4** | **84.2** | **87.8** | **89.2** |

---

## 5. KEY STRUCTURAL DIFFERENCES

### Reportflow Strengths Over Goldmine
- **Tighter narrative arc**: The decision chain flows logically from objective to result without digression. The goldmine is encyclopaedic; the reportflow is focused.
- **Better optimisation depth**: The 216-sweep, Pareto analysis, tornado chart, and composite scoring framework are presented with more mathematical rigour in the reportflow than in the goldmine body (goldmine puts much of this in appendices).
- **Energy model detail**: The reportflow has a stronger energy model section (power decomposition, energy budget table) than the goldmine body.
- **Explicit constraint-vs-objective justification**: The paragraph explaining why safety and time are constraints not scores (line 362-364) is better argued than anything equivalent in the goldmine.

### Goldmine Strengths Over Reportflow
- **Breadth**: 29 appendices cover every conceivable angle. Even if appendices aren't assessed, they demonstrate depth of understanding.
- **Literature grounding**: 118 citations vs 8. This is the most impactful difference.
- **Visual evidence**: Hardware photos, detection montages, geofence diagrams, state machine figures, bullseye plots. The reportflow is almost entirely text + optimisation charts.
- **Honest self-assessment**: The goldmine's evaluation is brutally honest (D1-D9, comparison with published systems, "was simulation-first the right strategy?"). The reportflow's evaluation is honest but less self-critical.
- **External context**: SAR comparison table, Sheridan framework, SORA reference, CAA regulations. The reportflow exists in isolation.

---

## 6. BOTTOM LINE

The reportflow is a strong optimisation-focused report with excellent mathematical rigour in the decision chain. However, it reads like an optimisation paper, not an engineering report. It lacks:
1. **Literature context** (the single biggest gap -- 8 citations for an MSc report is unacceptable)
2. **Visual evidence** (no photos, no detection images, no system diagrams)
3. **External positioning** (no comparison with published systems)
4. **Subsystem depth** (GPS estimation, attitude compensation, field results are superficial)

Fixing items 1-3 would lift the score from ~79 to ~87 in approximately 6-8 hours of work. The content already exists in the goldmine -- it's a matter of condensing and integrating, not creating from scratch.
