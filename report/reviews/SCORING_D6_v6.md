# D6 Company Report Scoring -- v6 Final Assessment

Scored: 2026-04-03
Previous: v5 scored 2026-04-03 (84.0/100), v4 scored 2026-03-27 (80.4/100)
Sections assessed: exec_summary, design_rationale, decision_flow, system_description, requirements_verification, evaluation

---

## 0. DELTA FROM v5

### What Changed Since v5

1. **MCDA sensitivity analysis ADDED (design_rationale.tex):** A full paragraph after the companion computer MCDA table describes 12 perturbation scenarios (+/-0.05 on each weight). Pi 5 retains rank in all cases (min 4.72 vs Jetson max 3.68). Ranking inverts only under an extreme scenario explicitly stated as contradicting a hard project constraint. Same analysis applied to all 4 MCDA tables. This directly closes the #1 weakness flagged in v4 and v5.

2. **decision_flow.tex now referenced as an Appendix** from design_rationale.tex (final paragraph: "presented as a self-contained executive narrative in Appendix"). This is a structural choice -- the decision flow content is substantial (~5 pages) and placing it as an appendix keeps the body page count manageable while preserving all the analytical depth.

3. **Detection envelope tables and speed envelope tables** in decision_flow.tex remain with "preliminary measurements" / "preliminary testing" language. This was flagged in v5 and has NOT been clarified.

4. **Requirements verification: correlation-aware N_eff detection probability** is now mature. The calculation is transparent: N_eff = N * (1 - overlap) = 19 * 0.05 = 1.0, giving 95% single-pass and 99.75% two-pass probability. This is honest and conservative (v4 had the naive P_miss = 5e-15 which was implausibly optimistic). The correction itself is a strength.

5. **Exec summary updated** to reference "20 states and 32 transitions", "four MCDA trade studies", "58 test scripts", and all key quantitative results. Self-contained and information-dense.

### What Did NOT Change From v5

- Still no outdoor flight data (fundamental constraint)
- Still no hardware photographs in body sections
- Still no ground station screenshot in body
- Still no detection example images at different altitudes
- Still no precision-recall curve (D4)
- Still no confusion matrix in body
- "Preliminary measurements" in decision_flow envelope tables still vague

---

## 1. RUBRIC CRITERIA SCORES

### Specialist Skills & Problem-Solving (40%) -- Score: 86/100 (was 85)

**Strengths (solidly in 83-100 band):**
- Complete end-to-end pipeline documented with quantified performance at every stage: camera capture (1456x1088) -> lens undistortion (+1.5ms, RMS=0.399) -> resize to 640x640 -> YOLOv8n TFLite inference (206.5ms) -> confidence filtering (threshold 0.2) -> pixel-to-GPS projection (GSD formula) -> inverse-variance weighted Kalman fusion (CEP50=2.3m) -> 20-state FSM -> offset landing (7.5m) -> payload servo
- Model retrained 3 times at increasing fidelity (640, 1280, 1088). Final dataset: 300 synthetic + 16 real + 50 negatives. mAP50=0.995 (acknowledged as upper bound due to train/val overlap -- honesty is a strength)
- 12 defects caught at bench tier with git-timestamped fix durations and counterfactual cost analysis. Two of these (geofence sign inversion, repulsive force reversal) would have caused regulatory violation if discovered in flight. This is a standout feature.
- Correlation-aware detection probability: N_eff = 1.0 instead of naive N=19, yielding conservative 95% single-pass detection. This correction demonstrates statistical maturity beyond typical MSc level.
- Error budget decomposition into 6 independent sources with RSS propagation at two altitudes (Table in system_description)
- Landing probability via Rician distribution with multi-observation fusion: sigma_fused = 0.80m, P(5-10m) > 99%
- 71 test scripts across 6 categories with progressive gating
- Dual-backend architecture with single-interface abstraction (detect_in_image)
- 4400 LOC across 11 modules with documented dependency graph
- FOV calibration from tape measure AND video analysis (two independent methods)

**Weaknesses (preventing 90+):**
- No outdoor flight. Every hardware validation is bench/video proxy. This is the fundamental ceiling.
- Train/validation overlap: 16 real images out of 366 is 4.4%. The mAP50=0.995 is acknowledged as an upper bound, but no action taken to collect more real data.
- No precision-recall curve. Threshold of 0.2 chosen by visual inspection.
- Payload release not wired into state machine (D8). HOVER_TARGET state exists but servo integration is bench-tested only.
- NCNN inconsistency persists: decision_flow claims "9 FPS in full pipeline" while other sections say "not yet benchmarked on Pi." These cannot both be true.

**Why +1 from v5:** The MCDA sensitivity analysis, while primarily a Decision Making improvement, also demonstrates methodological rigour that contributes to the Specialist Skills assessment. The overall analytical toolkit is now more complete. However, the fundamental constraints (no flight, no PR curve, no independent test set) remain unchanged, capping the improvement.

### Decision Making (40%) -- Score: 87/100 (was 85)

**Strengths (strong within 83-100 band):**
- **MCDA sensitivity analysis now present and thorough.** 12 perturbation scenarios per table, applied to all 4 MCDA tables. The critical insight -- "ranking inverts only under extreme scenario contradicting a hard project constraint" -- is exactly what an examiner wants to see. This closes the single largest gap from v4/v5.
- **5 MCDA trade-off tables** with weighted criteria, established before scoring (stated explicitly in each table caption area). Tables cover: companion computer, communication architecture, detection model, search pattern, plus the top-3 configuration ranking.
- **STEEPLE analysis** is specific, localised, and referenced. Environmental cites the specific SSSI and WCA 1981. Legal distinguishes local vs cloud data storage. Ethical addresses the asymmetric cost of false positives vs negatives. Not generic.
- **216-configuration parametric sweep** with physics-based energy model on the real survey polygon. This is genuine engineering optimisation, not toy analysis.
- **Sequential measurement chain** (decision_flow Steps 1-4): lock altitude before speed, lock speed before scan angle, lock geometry before energy optimisation. This mirrors real flight-test methodology and prevents downstream invalidation.
- **8-step parameter derivation chain** in design_rationale with full traceability: target size -> altitude ceiling -> safety margin -> operating altitude -> max speed -> lane spacing -> scan angle -> NFZ margins -> coverage -> energy validation. No parameter assumed without justification.
- **"Decisions That Changed"** (4 items): focal length 7.0->5.46mm, resolution 640x480->1456x1088, tflite-runtime->ai-edge-litert, pyserial->MAVProxy. Each follows measurement->correction pattern. This is the strongest evidence of adaptive, evidence-based decision-making.
- **Autonomy justification** with Sheridan levels, asymmetric cost analysis, 20x automation advantage, and quantified timeout derivation (120s = 5.2% battery per event, permits 2 events while retaining 89% for search).
- **Pareto analysis** confirming the selected point sits at the frontier knee.
- **Non-quantifiable design choices** section honestly separates engineering judgement from numerical optimisation.
- **NFZ buffer derivation** fully traced: half-footprint 16.1m + GPS 3.0m + stopping distance 10.7m = 29.8m, rounded to 30m.
- **20% overlap** justified via RSS of 3 error sources (GPS 3.0m + crosswind 2.5m + attitude 2.2m = 4.5m RSS against 6.4m overlap margin, giving 1.4x factor).
- **Verify timeout** now derived from energy budget (120s * 180W = 6.0 Wh = 5.2% battery). This was missing in v4 and flagged as a gap.

**Weaknesses (preventing 90+):**
- The detection envelope tables (decision_flow Table 6, 7) still cite "preliminary measurements" and "preliminary testing" without specifying the source. Are these from DJI video replay? Bench testing with artificial lighting? Simulation? The evidence chain is vague at the most critical point of the sequential measurement chain.
- No stakeholder analysis beyond the brief. Mountain rescue teams are mentioned in STEEPLE Social but no user research was conducted.
- No comparison to commercial/academic SAR systems' decision processes. The DJI Matrice 30T appears in the Economic STEEPLE but is never benchmarked against on capability.
- Some MCDA scores still feel generous for Pi 5 (5/5 on four criteria). The sensitivity analysis mitigates this concern -- even with perturbation the Pi wins -- but the initial scoring table still looks like it was set up to win.

**Why +2 from v5:** The MCDA sensitivity analysis is the primary driver. It transforms every MCDA table from "we scored these and picked the winner" to "we scored these, picked the winner, and verified the pick is robust to weight uncertainty." This is exactly the gap v4 and v5 identified, and it is now closed convincingly. The 12-scenario perturbation with explicit identification of the inversion condition is thorough.

### Communication (20%) -- Score: 80/100 (was 80)

**Strengths:**
- Professional LaTeX throughout: SI units, consistent formatting, clean table styling, proper cross-references
- ~24 figures in body sections (architecture diagrams, data-driven plots, sensitivity analyses, GPS accuracy, system diagrams)
- ~16 tables in body (BOM, 5x MCDA, MAVLink, error budget, req verification, plus/delta, bug-cost, 5-tier, detection envelope x2, decision variables, top-3, final config)
- 3-4 displayed equations (footprint/lane, detection probability with N_eff, landing probability)
- Subfigures used effectively (GPS pair, estimation pair, detection sensitivity pair)
- Executive summary is genuinely self-contained and could stand alone as a briefing document
- decision_flow section reads as an accessible narrative -- the best-written section for a non-technical reader
- 29 appendices (A-AB) provide substantial depth without consuming page budget
- All body figures programmatically generated from real data or calibrated models (gen_*.py scripts)

**Weaknesses (preventing 85+):**
- **No hardware photographs.** This is the single most impactful communication gap. The report describes a physical system that has been assembled, calibrated, and bench-tested, but not a single photograph appears in the body. One annotated photo of the drone on the bench with Pi, camera, and Cube labelled would be worth more than three generated diagrams. This has been flagged since v4.
- **No ground station screenshot.** The text describes a browser dashboard with MJPEG stream, GPS grid, and 9 command buttons in impressive detail. Showing it would convert 200 words into instant visual proof.
- **No detection example images.** The model's performance is quantified (mAP, confidence, altitude curves) but never shown visually. Three side-by-side subfigures with bounding boxes at 15m, 30m, 50m altitude from video_test.py output would powerfully support the detection envelope analysis.
- **No confusion matrix in body** (exists as PNG in cv_models/). Standard ML reporting, 10 minutes to add.
- **8-step parameter chain is a wall of paragraphs.** Converting to a numbered table or flowchart would provide visual relief in an already text-dense section.
- **decision_flow is now an appendix**, meaning its substantial analytical content (5 pages of Pareto analysis, top-3 comparison, sequential measurement chain, decomposition) is outside the body. This preserves page budget but means an examiner reading only the body misses the strongest decision-making evidence. The trade-off is reasonable but should be considered.

**Why unchanged from v5:** No new visual content was added. The MCDA sensitivity text is a Decision Making improvement that happens to appear in the body text, but it does not address the visual communication gaps. The same three missing items (photos, screenshots, detection examples) persist. Communication score remains at 80.

---

## 2. OVERALL SCORE

| Criterion | Weight | v4 | v5 | v6 | Weighted (v6) |
|-----------|--------|----|----|-----|---------------|
| Specialist Skills | 40% | 82 | 85 | 86 | 34.4 |
| Decision Making | 40% | 80 | 85 | 87 | 34.8 |
| Communication | 20% | 78 | 80 | 80 | 16.0 |
| **TOTAL** | | **80.4** | **84.0** | | **85.2** |

**Band: 83-89 (High First) -- solidly in top band**

The report has moved from the threshold of the 83-89 band (v5: 84.0) to a more secure position within it (v6: 85.2). The MCDA sensitivity analysis was the primary driver -- it closed the single largest methodological gap that both v4 and v5 identified.

---

## 3. SECTION-BY-SECTION ASSESSMENT

### Executive Summary (excluded from page count)
- **Quality: 9.0/10** (unchanged)
- Self-contained, information-dense, covers objective/system/decisions/results/limitations
- Specific numbers throughout (20 states, 32 transitions, 4 MCDA, 58 tests, mAP50=0.995, CEP50=2.3m)
- Honest about limitations: "No autonomous outdoor flight was achieved; all integration results are from simulation, bench tests, and DJI video proxy analysis"
- Could be stronger: mention the MCDA sensitivity analysis explicitly as a methodological highlight

### Design Rationale (~6 pages estimated)
- **Quality: 9.5/10** (was 9.0 -- MCDA sensitivity is a meaningful improvement)
- STEEPLE: specific, referenced, non-generic. Strong.
- 5 MCDA tables with sensitivity analysis: this is now a standout feature. The 12-perturbation-scenario analysis with explicit inversion conditions is above typical MSc rigour.
- 8-step parameter derivation chain: thorough, fully traced, every parameter justified.
- Autonomy justification: Sheridan levels + asymmetric cost + 20x automation advantage + timeout derived from energy budget.
- "Decisions That Changed": 4 items, measurement->correction pattern. Best evidence of adaptive engineering.
- Camera selection: quantified rolling shutter skew (7.5 px at 5 m/s).
- "Why Not ROS": 3 concrete reasons with quantified alternatives.
- **Remaining weakness:** 8-step chain is text-heavy. A diagram would help.

### Decision Flow (Appendix, ~5 pages)
- **Quality: 8.5/10** (unchanged)
- Narrative structure is accessible and engaging.
- Sequential measurement chain is methodologically sound.
- Top-3 configuration table with "Why not?" column is excellent.
- 216-configuration sweep is genuine optimisation.
- Pareto analysis and non-quantifiable choices show maturity.
- **Remaining weakness:** "Preliminary measurements" and "preliminary testing" in envelope tables are still vague. This is the weakest link in an otherwise rigorous chain.

### System Description (~5 pages estimated)
- **Quality: 8.5/10** (unchanged)
- Architecture, CV pipeline, geofence, state machine, localisation, ground station all well documented.
- Error budget table (6 sources, RSS propagation at 2 altitudes) is a strong quantitative feature.
- BOM, MAVLink commands, and performance metrics provide useful reference material.
- **Remaining weakness:** No hardware photo, no ground station screenshot, no detection examples.

### Requirements Verification (~3.5 pages estimated)
- **Quality: 9.0/10** (unchanged)
- Clean traceability table with R01-R12.
- Correlation-aware N_eff detection probability is a highlight.
- R07 Rician distribution analysis with multi-observation fusion is strong.
- R06 PLB fully described (manual + timed trigger).
- R02 four-layer SSSI protection with parameter values.
- **Remaining weakness:** N_eff = 1.0 means the single-pass probability is essentially just p_d = 0.95, which makes the elaborate calculation somewhat circular. The two-pass probability of 99.75% is the meaningful result. Also, the bench p_d = 0.95 conflates static bench testing with dynamic aerial detection.

### Evaluation (~4 pages estimated)
- **Quality: 9.0/10** (unchanged)
- Plus/delta (9+9) is honest and evidence-based.
- Bug-cost table (12 defects) with counterfactual analysis is a standout.
- 5-tier progressive testing framework clearly presented.
- 4 lessons learned are engineering-grade insights.
- Weather cancellation framed as positive adaptation.
- "What Would Change" (4 items) demonstrates genuine reflection.
- **Remaining weakness:** No comparison to other teams or commercial systems. detection_heatmap should be labelled as simulated if it is.

---

## 4. FIGURE AND TABLE COUNTS

| Element | v4 | v5 | v6 | Notes |
|---------|----|----|-----|-------|
| Body figures | 15 | ~24 | ~24 | Unchanged; decision_flow figs now in appendix |
| Body tables | 8 | ~16 | ~17 | +MCDA sensitivity analysis is inline text, not a separate table |
| Equations | 1 | 3-4 | 3-4 | Unchanged |
| Body citations | ~25 | ~30+ | ~30+ | Unchanged |
| Appendices | 19 | 29 | 29 | Unchanged |

---

## 5. TOP 5 IMPROVEMENTS TO PUSH TOWARD 88-89

### 1. Hardware Photograph(s) -- Impact: +2-3 on Communication (-> 82-83)

One annotated photograph of the assembled drone (Pi, camera, Cube, GPS antenna visible) with callouts. Even a phone photo. This is the single highest-ROI action and has been the #1 recommendation since v4. If no photos exist, state this with a footnote and include a labelled physical layout diagram.

### 2. Ground Station Screenshot -- Impact: +1 on Communication

Screenshot of the browser dashboard showing MJPEG stream, GPS grid with detection clusters, and command buttons. Run pi_flight.py in simulation mode and capture. 10 minutes of work.

### 3. Detection Example Images at Multiple Altitudes -- Impact: +1 on Communication, +0.5 on Specialist Skills

Three subfigures showing YOLOv8n bounding boxes from DJI video at 15m, 30m, and 50m. These already exist as video_test.py output. Visually demonstrates the detection envelope that is otherwise only described numerically.

### 4. Clarify "Preliminary Measurements" in Decision Flow -- Impact: +1 on Decision Making

Specify the source of detection envelope (Table 6) and speed envelope (Table 7) data. One sentence each: "measured from DJI video replay at known altitudes" or "extrapolated from bench confidence measurements and the pixel-extent model." Vague evidence claims undermine the strongest analytical section.

### 5. Confusion Matrix in Body -- Impact: +0.5 on Communication, +0.5 on Specialist Skills

Already exists as PNG in cv_models/sar_v2_1088/. Standard ML reporting, 10 minutes to add. Shows model performance in a format every reviewer recognises.

---

## 6. WHAT WOULD PUSH THIS TO 90+

The hard ceiling is the absence of outdoor flight data. Without it, the maximum realistic score is approximately 87-88. To reach 90+ would require:

1. **Outdoor flight data** -- even one pass with detection logs. Cannot be manufactured.
2. **Independent test set** -- 50+ labelled frames from a separate flight to report credible mAP on truly held-out data.
3. **Precision-recall curve** with formal threshold selection at the operating point.
4. **Comparison to 2+ commercial/academic SAR systems** with structured comparison table.
5. **Payload release integrated into state machine** (D8 resolved).

Items 1-2 are blocked by weather/scheduling. Items 3-5 are achievable but represent significant work. The combination of items 1 and 2 would likely push Specialist Skills to 90+ on its own; their absence is the fundamental constraint.

---

## 7. HONEST ASSESSMENT

This report is genuine High First quality. The technical depth -- 216-configuration parametric sweep, correlation-aware detection statistics, Rician landing probability, Kalman-filtered GPS fusion, 6-source error budget with RSS propagation -- goes well beyond what is typical at MSc level. The MCDA sensitivity analysis is now thorough and convincing. The "Decisions That Changed" section is the best evidence of engineering adaptability I have seen in a student report.

The weaknesses are real but fall into two categories:

**Cannot fix (structural):** No outdoor flight data. This caps the score at ~87-88 regardless of writing quality. Every claim about real-world performance is hedged by "SITL only" or "DJI video proxy." The report handles this limitation well -- it is honest, frames bench testing as information-maximising, and clearly lists what remains unverified -- but no amount of good writing can replace actual flight data.

**Can fix (quick wins):** Hardware photos, ground station screenshot, detection examples, confusion matrix, "preliminary measurements" clarification. These are all under 30 minutes of effort and would add 2-4 marks primarily through Communication. The fact that they have been flagged since v4 and remain unaddressed is the most frustrating aspect of this scoring.

The decision_flow section being relegated to an appendix is a double-edged sword: it preserves page budget but means the examiner might not read the strongest decision-making content. If page budget allows, promoting the key tables (top-3 configs, final config) into the body and leaving the narrative detail in the appendix would be optimal.

**Bottom line:** 85.2, solidly in the 83-89 band. Adding the quick-win visual content would push to 86-87. Adding outdoor flight data would push to 88-90. The analytical foundation is there; the gap is evidence and presentation.

---

## 8. SCORING TRAJECTORY

| Version | Date | Specialist | Decision | Communication | Total | Key Driver |
|---------|------|-----------|----------|---------------|-------|------------|
| v4 | 2026-03-27 | 82 | 80 | 78 | 80.4 | Baseline comprehensive assessment |
| v5 | 2026-04-03 | 85 (+3) | 85 (+5) | 80 (+2) | 84.0 (+3.6) | decision_flow, 216-config sweep, Pareto, N_eff |
| v6 | 2026-04-03 | 86 (+1) | 87 (+2) | 80 (0) | 85.2 (+1.2) | MCDA sensitivity analysis |

Diminishing returns are setting in for text-based improvements. The next meaningful jump requires either (a) visual content (photos/screenshots) or (b) new data (flight, PR curve, independent test set).
