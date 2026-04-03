# D6 Company Report Scoring -- v5 Comprehensive Assessment

Scored: 2026-04-03
Previous: v4 scored 2026-03-27 (80.4/100)
Sections assessed: design_rationale, system_description, requirements_verification, evaluation, decision_flow (NEW)

---

## 0. DELTA FROM v4

### What Changed Since v4

1. **decision_flow.tex added (~5 pages)** -- Entirely new section explaining the search parameter optimisation as a narrative "decision flow". Contains sequential measurement chain, detection/speed envelope tables, Pareto analysis, decomposition into sub-problems, and non-quantifiable design choices. This is a MAJOR addition that directly addresses the v4 weakness "Missing decision documentation on some choices."

2. **design_rationale.tex significantly expanded:**
   - Search parameter optimisation subsection added (coupling matrix figure, 216-config sweep, altitude-speed tradeoff figure)
   - 8-step parameter derivation chain (detection ceiling -> safety margin -> max speed -> lane spacing -> scan angle -> NFZ margins -> coverage -> energy validation)
   - Autonomy level justification expanded with asymmetric cost analysis (false positive vs false negative), automation advantage quantified at 20x
   - "Decisions That Changed" expanded to 4 items with measurement->correction pattern
   - Camera selection rationale with rolling vs global shutter motion analysis (250 px/s, 7.5 px skew)
   - Field day adaptation section framing weather cancellation as information-maximising pivot
   - NFZ buffer derivation (RSS of GPS error + reaction distance + footprint = 23m, 30m provides 2.2x factor)
   - 20% overlap justified via RSS analysis (GPS drift 3m + crosswind + attitude = 4.6m against 6.4m overlap margin)

3. **system_description.tex refined:**
   - Geofence enforcement paragraph added with 4-panel figure reference
   - Smart detection mode documented (--smart-detect, k=3 consecutive frames)
   - Performance paragraph with quantified overlap analysis (95% frame overlap, 11-17 detection opportunities)
   - Error budget table added (6 independent sources, RSS total 2.9m at 35m)
   - Ground station section now describes MJPEG rationale and 300ms measured latency

4. **requirements_verification.tex substantially improved:**
   - Per-flyover detection probability calculation with correlation-aware N_eff analysis (not naive independence assumption)
   - R07 landing probability now uses Rician distribution with CEP50-derived sigma, multi-detection fusion to >99%
   - R06 PLB Focus Area implementation fully described (manual + timed trigger, polygon re-read, resume behaviour)
   - R09 expanded to three independent layers with specific verification evidence

5. **evaluation.tex significantly strengthened:**
   - 9 plus items + 9 delta items (expanded from v4)
   - Bug discovery table (12 defects at Tiers 1-3 with fix times and "cost if missed")
   - 5-tier progressive testing framework table
   - 4 figures: conf_vs_alt, det_vs_speed, latency_breakdown, detection_heatmap
   - Discussion sections: architecture resilience, detection performance, GPS estimation, testing effectiveness
   - "What Would Change in a Second Iteration" (4 items)
   - 4 lessons learned with engineering depth
   - Honest acknowledgment of train/val overlap, missing outdoor flight, single-class limitation

### What Did NOT Change From v4

- Still no outdoor flight data (fundamental constraint, cannot change)
- Still no hardware photographs visible in body sections
- Still no ground station screenshot referenced in body
- Cannot verify if [NAME] placeholders in intro were filled (intro.tex not read)
- No precision-recall curve added (still listed as D4 delta)

---

## 1. RUBRIC CRITERIA SCORES

### Specialist Skills & Problem-Solving (40%) -- Score: 85/100 (was 82)

**Strengths (firmly in 83-100 band):**
- Complete end-to-end pipeline: camera -> lens undistortion -> YOLOv8n TFLite -> GPS estimation -> Kalman filter -> state machine -> offset landing -> payload release design
- Initiative demonstrated repeatedly: model retrained 3 times, FOV calibrated by tape-measure AND video, BGR colour bug found by exhaustive 6-permutation testing, DJI video proxy pipeline built in one session after weather cancellation
- Correlation-aware detection probability (N_eff = N * (1-overlap) rather than naive independence) -- this is a genuinely sophisticated statistical treatment rare at MSc level
- 12 defects caught and fixed at bench tier with documented fix times (5min to 2hr) and counterfactual cost analysis
- 71 test scripts across 6 categories with progressive gating (Tier N must pass before Tier N+1)
- Quantified throughout with real measurements: mAP50=0.995, CEP50=2.3m, 206.5ms/frame, 4.8 FPS, 0.966 confidence, RMS=0.399 lens calibration, f=5.46mm focal length
- Dual-backend architecture (Ultralytics/TFLite/NCNN) with single-interface abstraction
- 4400 LOC across 11 modules with clean dependency graph (independent modules have zero cross-deps)
- Error budget decomposition into 6 independent sources with RSS propagation at two altitudes
- Landing probability derived from Rician distribution with multi-observation fusion (sigma_fused = 0.80m, P>99%)

**Weaknesses (preventing 90+):**
- No outdoor flight completed -- all hardware validation is bench/video proxy. This is the single biggest gap.
- Train/validation overlap acknowledged (D5) but not resolved -- mAP50=0.995 is likely an upper bound
- No precision-recall curve (D4) -- threshold of 0.2 chosen by visual inspection, not formal sweep
- Payload release designed but not wired into state machine (D8) -- a functional gap, not just a tuning gap
- The NCNN 9 FPS claim in decision_flow.tex Step 3 appears in a body section but the NCNN backend is described elsewhere as "not yet benchmarked on the Pi" -- minor inconsistency
- 16 real training images is acknowledged as small but no plan to increase is actioned

**Why +3 from v4:** The correlation-aware detection probability, error budget table, bug-cost table with counterfactual analysis, and 4 genuine lessons learned all demonstrate analytical depth beyond what v4 had. The decision_flow section's sequential measurement chain and decomposition into sub-problems show mature engineering thinking.

### Decision Making (40%) -- Score: 85/100 (was 80)

**Strengths (firmly in 83-100 band):**
- **5 MCDA trade-off tables** (up from 4): companion computer, communication architecture, detection model, search pattern, plus the top-3 configuration ranking table with "Why not?" column
- **STEEPLE analysis** covers all 7 dimensions with specific, localised content. The Environmental dimension cites the specific SSSI, specific legislation (WCA 1981), and specific technical mitigation (3-layer geofence + waypoint filtering). The Legal dimension distinguishes local data storage from cloud. Not generic.
- **"Decisions That Changed"** section (4 items) is the strongest evidence of evidence-based decision-making. Each follows measurement->correction pattern with quantified impact (e.g., focal length shift causes 3m GPS error at 30m altitude).
- **216-configuration parametric sweep** with physics-based energy model -- this is genuine optimisation, not guessing
- **Sequential measurement chain** (decision_flow.tex) locks each variable before optimising the next -- mirrors real flight-test programme methodology
- **Decomposition into 5 independent sub-problems** with clear input-output interfaces -- shows systems thinking
- **Pareto analysis** with parallel-coordinates plot and explicit explanation of why moving from the selected point worsens at least one objective
- **Non-quantifiable design choices** section honestly separates engineering judgement from numerical optimisation
- **Autonomy level** justified using Sheridan framework with asymmetric cost analysis and 20x automation advantage quantification
- **NFZ buffer derivation** now fully traced: RSS(GPS 3m + reaction + footprint) = 23m, buffer = 30m, factor = 2.2x
- **20% overlap** justified via RSS of GPS drift + crosswind + attitude = 4.6m against 6.4m margin
- **Detection envelope tables** (altitude x lighting conditions, speed x lighting conditions) with 15% margins
- **Tornado sensitivity** and **spider plot** referenced for robustness characterisation
- **Weather cancellation** framed as information-maximising adaptation, not failure, with specific data yields listed

**Weaknesses (preventing 90+):**
- Still no explicit sensitivity analysis on MCDA weights (would changing weights by +/-10% change the winner?). The 216-config sweep partially compensates but the individual MCDA tables for companion computer, comms, model, and pattern lack this.
- Some MCDA scores still feel generous -- Pi 5 scores 5 on 4 of 6 criteria in Table 2. The Jetson Nano's GPU advantage is acknowledged in text but scored only 3-4 everywhere.
- No stakeholder analysis beyond the brief. Who are the mountain rescue teams? What do they actually need? No user requirements gathering.
- The detection envelope tables (Table 6, 7 in decision_flow) cite "preliminary measurements" and "preliminary testing" but it is unclear what these measurements actually are -- DJI video replay? Simulation? Bench? The evidence chain is vague here.
- No comparison to how other academic/commercial SAR systems made similar decisions

**Why +5 from v4:** The decision_flow section is a massive improvement. The sequential measurement chain, 216-config sweep, Pareto analysis, and decomposition into sub-problems transform what was previously "good decisions documented" into "systematic optimisation methodology documented." The missing decision rationale (overlap, NFZ buffer, verify timeout) that v4 flagged is now largely addressed in design_rationale.tex.

### Communication (20%) -- Score: 80/100 (was 78)

**Strengths:**
- Professional LaTeX with consistent formatting, proper use of SI units (\SI{}), clean table styling
- Body figures now include: coupling_matrix, altitude_speed_tradeoff, mission_overview, architecture, pi_system, cv_pipeline, geofence_diagram, state_machine, gps_bullseye, gps_error_direction, gps_convergence, estimator_comparison, coverage_vs_time, mission_timeline, conf_vs_alt, det_vs_speed, latency_breakdown, detection_heatmap -- approximately 18+ figures in body
- Tables: BOM, 5x MCDA, MAVLink commands, error budget, requirements verification, plus/delta, bug-cost, 5-tier testing, detection envelope (2), decision variables, top-3 configs, final config -- approximately 14+ tables in body
- Equations: footprint/lane spacing (Eq 1), per-pass detection probability with N_eff, Rician/Gaussian landing probability, GSD formula in text -- 3-4 displayed equations
- Subfigures used effectively (GPS accuracy pair, estimation pair, detection sensitivity pair)
- Cross-references throughout (secref, figref, tabref)
- 52 PDF figures in figs/ directory -- substantial investment in visual communication
- 29 appendices (A-AB) provide depth without consuming page budget
- decision_flow.tex reads like an accessible narrative -- good for non-specialist readers

**Weaknesses (preventing 85+):**
- Still no photographs of actual hardware (assembled drone, Pi mounted on frame, field day setup). This is the most impactful communication gap. A single annotated photograph of the assembled system would be worth more than three generated diagrams.
- No ground station screenshot. The text describes a browser dashboard with MJPEG stream, GPS grid, and 9 command buttons -- showing it would be powerful proof of existence.
- No detection example images (bounding boxes at different altitudes from video_test.py output). The model's performance is quantified in numbers but never shown visually in the body.
- No confusion matrix in body (exists in cv_models/ as PNG). Standard ML reporting.
- decision_flow.tex references fig:sensitivity-matrix, fig:energy-heatmap, fig:pareto-parallel, fig:top3-paths, fig:tornado-sensitivity, fig:sensitivity-spider -- 6 additional figures. Need to verify these all compile.
- Some text-heavy passages in design_rationale (the 8-step parameter chain is a wall of paragraphs). Could be a numbered table or flowchart for visual relief.
- The detection probability derivation in requirements_verification is dense and would benefit from a figure showing the geometric setup (camera footprint moving over target).

**Why +2 from v4:** More figures, more tables, more equations, and the decision_flow narrative is genuinely well-written. But the fundamental gap of no real-world photographs persists, and the new decision_flow section adds 6 more figure references that need verification.

---

## 2. OVERALL SCORE

| Criterion | Weight | v4 Score | v5 Score | Weighted (v5) |
|-----------|--------|----------|----------|----------------|
| Specialist Skills | 40% | 82 | 85 | 34.0 |
| Decision Making | 40% | 80 | 85 | 34.0 |
| Communication | 20% | 78 | 80 | 16.0 |
| **TOTAL** | | **80.4** | | **84.0** |

**Band: 83-89 (High First) -- just entered the top band**

The report has crossed the 83 threshold. The decision_flow section and the expanded design_rationale were the primary drivers. To solidify 85+ and push toward 88-90 requires addressing the communication gaps (photographs, screenshots, detection examples) and adding MCDA sensitivity analysis.

---

## 3. SECTION-BY-SECTION ASSESSMENT

### Design Rationale (~6 pages estimated)
- **Quality: 9.0/10** (was 9.0 in v4 -- maintained but now denser)
- STEEPLE: specific, referenced, non-generic. Strong.
- 5 MCDA tables: comprehensive. Scores defensible but could use sensitivity note.
- Search parameter optimisation: coupling matrix + 216-config sweep + altitude-speed tradeoff figure = excellent. This is the centrepiece.
- 8-step parameter derivation chain: thorough but text-heavy. Consider converting to a diagram or numbered table for visual relief.
- Autonomy justification: Sheridan levels + asymmetric cost + 20x automation advantage = sophisticated.
- "Decisions That Changed": 4 items, each with measurement->correction pattern. Still the strongest evidence of adaptive decision-making.
- Camera selection: quantified rolling shutter skew (7.5 px at 5 m/s). Good.
- Field day adaptation: well framed.
- **Missing:** MCDA weight sensitivity. One sentence per table would suffice.

### Decision Flow (~5 pages estimated, NEW)
- **Quality: 8.5/10**
- Narrative structure ("The Problem" -> "The Variables" -> "Our Strategy" -> "What We Evaluated" -> "The Result") is accessible and engaging. Best-written section for a non-specialist reader.
- Sequential measurement chain (Steps 1-4) is methodologically sound and mirrors flight-test practice.
- Detection and speed envelope tables with lighting conditions add real-world grounding.
- Top-3 configuration table with "Why not?" column is excellent decision documentation.
- Decomposition into 5 sub-problems shows systems thinking.
- Pareto analysis and non-quantifiable choices demonstrate maturity.
- **Weaknesses:** "Preliminary measurements" and "preliminary testing" for envelope tables are vague -- what were these measurements? The NCNN 9 FPS claim sits oddly next to "not yet benchmarked on Pi" in other sections. The section references 6+ figures (sensitivity-matrix, energy-heatmap, pareto-parallel, top3-paths, tornado-sensitivity, sensitivity-spider) that need compilation verification.

### System Description (~5 pages estimated)
- **Quality: 8.5/10** (was 8.0 -- improved)
- Architecture figure + Pi system figure + CV pipeline figure + state machine figure = good visual density.
- BOM table, MAVLink commands table, error budget table = useful reference material.
- Geofence enforcement with 4-panel figure is a strong addition.
- Target localisation with Kalman filter, inverse-variance weighting, and error budget = quantitatively thorough.
- Ground station section with MJPEG rationale and 300ms latency measurement.
- Smart detection mode (k=3 consecutive frames) documented.
- **Missing:** Hardware photograph, ground station screenshot, wiring diagram (even a simple block diagram showing Pi<->MAVProxy<->Cube<->RC physical connections).

### Requirements Verification (~3.5 pages estimated)
- **Quality: 9.0/10** (was 8.5 -- improved)
- Clean traceability table with every R01-R12 mapped.
- Per-flyover detection probability with correlation-aware N_eff is genuinely sophisticated. The distinction between 19 raw frames and N_eff=1.0 effective independent observations, leading to 95% single-pass and 99.75% two-pass probability, is excellent statistical reasoning.
- R07 landing probability analysis using Rician distribution with multi-observation fusion (P>99%) is strong quantitative work.
- R06 PLB Focus Area fully described with both activation methods and resume behaviour.
- R09 three independent layers with specific SITL verification.
- R02 four protection layers with specific parameter values.
- **Weakness:** The N_eff formula is an approximation that assumes uniform overlap. In reality, overlap varies at scan line ends. This isn't mentioned. Also, the detection probability formula uses p_d >= 0.95 "measured on bench and DJI video proxy" but the bench test uses a static image -- not the same as detecting from a moving platform. This conflation of bench and real-world p_d is a subtle weakness.

### Evaluation (~4 pages estimated)
- **Quality: 9.0/10** (was 9.0 -- maintained at high level)
- Plus/delta table is exceptionally honest: 9 plus + 9 delta with evidence and next steps.
- Bug-cost table (12 defects) with counterfactual analysis is a standout feature. "Geofence sign convention inverted -- Cost if missed: SSSI incursion; regulatory violation" is powerful.
- 5-tier progressive testing framework clearly presented.
- 4 sensitivity figures (conf_vs_alt, det_vs_speed, latency_breakdown, detection_heatmap).
- Discussion of weather cancellation as positive adaptation evidence is well-argued.
- "What Would Change" section (4 items) shows genuine reflection.
- 4 lessons learned are engineering-grade insights, not platitudes.
- **Weakness:** No comparison to other teams' approaches. No comparison to commercial SAR systems (DJI Matrice 30T mentioned in STEEPLE but never benchmarked against). The detection_heatmap figure may be from simulation, not real data -- should be clearly labelled.

---

## 4. FIGURE AND TABLE COUNTS

### Body Sections (estimated from tex files read)

| Element | v4 Count | v5 Count | Notes |
|---------|----------|----------|-------|
| Figures | 15 | ~24 | +coupling_matrix, altitude_speed_tradeoff, geofence_diagram, coverage_vs_time, + ~6 in decision_flow |
| Tables | 8 | ~16 | +error budget, bug-cost, 5-tier, detection envelope (2), decision variables, top-3, final config |
| Equations | 1 | 3-4 | +footprint/lane, detection probability, (landing probability was already in v4) |
| Citations (body) | ~25 | ~30+ | Several new refs in decision_flow and design_rationale |
| Appendices | 19 | 29 (A-AB) | Significant expansion |

### Assessment of Figure Quality

- **Based on real data (strong):** gps_bullseye, gps_error_direction, gps_convergence, estimator_comparison, conf_vs_alt, det_vs_speed, latency_breakdown, confusion_matrix -- all derived from DJI video analysis or Pi benchmarks
- **Architectural diagrams (adequate):** architecture, pi_system, cv_pipeline, state_machine, geofence_diagram, mission_overview -- programmatically generated, clean, professional
- **Model-based (good):** altitude_speed_tradeoff, coupling_matrix, coverage_vs_time, energy_heatmap, pareto_parallel, tornado_sensitivity -- derived from physics models applied to real polygon geometry
- **Missing entirely:** Hardware photographs, ground station screenshots, detection example images at multiple altitudes

---

## 5. TOP 5 IMPROVEMENTS TO REACH 85+ SOLIDLY (AND PUSH TOWARD 88)

### 1. Hardware Photograph(s) -- Impact: +2-3 on Communication

Add 1-2 annotated photographs of the assembled system (drone on bench with Pi visible, camera mounted). Even a phone photo with callout annotations (Pi, Camera, Cube, GPS, Battery) would transform the System Description. This is the single highest-ROI action. If no photos exist from field day, state this explicitly with a footnote and include a labelled CAD/diagram of the physical layout instead.

**Where:** system_description.tex, after the BOM table.

### 2. Ground Station Screenshot -- Impact: +1-2 on Communication

Screenshot of the browser dashboard at http://localhost:8090 showing the MJPEG stream, GPS grid with detection clusters, and command buttons. Run pi_flight.py in simulation mode and capture. This converts 200 words of description into visual proof.

**Where:** system_description.tex, ground station subsection.

### 3. MCDA Sensitivity Analysis -- Impact: +2-3 on Decision Making

For each of the 5 MCDA tables, add one sentence: "Varying all weights by +/-10% does not change the ranking; the winning candidate maintains its lead across all tested perturbations" (or "the ranking inverts between X and Y when weight W exceeds 0.35, indicating the decision is sensitive to the relative importance of W"). This is 5 sentences total, 10 minutes of work, and directly addresses the v4 weakness.

**Where:** design_rationale.tex, after each MCDA table or as a summary paragraph at the end of the section.

### 4. Detection Example Images -- Impact: +1-2 on Communication and Specialist Skills

Three side-by-side subfigures showing YOLOv8n bounding boxes on the DJI video at 15m, 30m, and 50m altitude. These already exist as output from video_test.py. This visually demonstrates the detection envelope and directly supports the confidence-vs-altitude analysis.

**Where:** evaluation.tex, near the detection performance discussion, or system_description.tex in the CV pipeline subsection.

### 5. Clarify "Preliminary Measurements" in Decision Flow -- Impact: +1 on Decision Making

The detection envelope (Table 6) and speed envelope (Table 7) in decision_flow.tex cite "preliminary measurements" and "preliminary testing." Specify the source: "measured from DJI video replay at known altitudes under varying artificial brightness" or "extrapolated from bench confidence measurements and the pixel-extent vs altitude model." Vague evidence claims undermine an otherwise rigorous section.

**Where:** decision_flow.tex, paragraphs around Tables 6 and 7.

---

## 6. ADDITIONAL IMPROVEMENTS (MEDIUM PRIORITY)

| # | Item | Impact | Effort |
|---|------|--------|--------|
| 6 | Confusion matrix in body from cv_models/sar_v2_1088/ | +1 Comm | 10 min |
| 7 | Detection probability geometry figure (camera footprint sliding over target) | +1 Comm | 20 min |
| 8 | Verify all decision_flow figure references compile (6 figs) | blocks -2 if broken | 5 min |
| 9 | Fix NCNN inconsistency (9 FPS claim vs "not benchmarked on Pi") | +0.5 Specialist | 5 min |
| 10 | Add comparison to DJI Matrice 30T or academic SAR (price, weight, detection range) | +1 Decision | 15 min |
| 11 | Convert 8-step parameter chain to a figure/flowchart | +1 Comm | 20 min |
| 12 | Label detection_heatmap as "simulated" if from simulation | +0.5 honesty | 2 min |

---

## 7. WHAT WOULD PUSH THIS TO 90+

To reach 90+, the report would need:

1. **Outdoor flight data** -- even one pass with detection logs. This cannot be manufactured but is the single factor that caps the score. Without it, the maximum realistic score is approximately 87-88.

2. **Independent test set** -- 50+ labelled frames from a separate flight (not the synthetic pipeline) to report a credible mAP on truly held-out data.

3. **Precision-recall curve** with formal threshold selection at the operating point.

4. **Comparison to at least 2 commercial/academic SAR systems** with a structured comparison table (not just price).

5. **Payload release integrated into state machine** (D8 resolved, not just designed).

Items 1-2 are blocked by weather/scheduling. Items 3-5 are achievable but represent significant work.

---

## 8. SCORING SUMMARY

| Criterion | Weight | v4 | v5 | Delta | Key Driver |
|-----------|--------|----|----|-------|------------|
| Specialist Skills & Problem-Solving | 40% | 82 | 85 | +3 | Correlation-aware detection prob, error budget, bug-cost table, lessons learned |
| Decision Making | 40% | 80 | 85 | +5 | decision_flow section, 216-config sweep, sequential chain, Pareto analysis, NFZ/overlap derivations |
| Communication | 20% | 78 | 80 | +2 | More figures/tables/equations, better narrative in decision_flow |
| **WEIGHTED TOTAL** | | **80.4** | **84.0** | **+3.6** | |

**Verdict:** The report has entered the 83-89 band. The decision_flow section was the biggest single improvement, transforming decision-making from "good documentation" to "systematic optimisation methodology." The remaining gap to 88+ is primarily communication (photographs, screenshots, detection examples) and the fundamental constraint of no outdoor flight data. The five improvements listed in Section 5 are achievable within a few hours and would solidify the score at 85-86.
