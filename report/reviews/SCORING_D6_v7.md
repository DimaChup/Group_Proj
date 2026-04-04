# D6 Company Report Scoring -- v7 Assessment

Scored: 2026-04-03
Previous: v6 scored 2026-04-03 (85.2/100)
Sections assessed: exec_summary, design_rationale, system_description, requirements_verification, evaluation
Branch: Working8.Robbin3 (user states "Working9.5 polish" but assessment is on current file content)

---

## 0. DELTA FROM v6

### What Changed Since v6

After careful comparison of the five body sections against v6's notes and weaknesses, the following observations apply:

1. **design_rationale.tex**: The content is substantively the same as v6. The STEEPLE table, 5 MCDA tables with sensitivity analysis, 8-step parameter derivation chain, "Decisions That Changed" section, autonomy justification, camera selection, and "Why Not ROS" are all present and unchanged. The coupling matrix figure and altitude-speed trade-off figure remain. The section summary paragraph at the end is the same. No new figures, tables, or analytical content detected.

2. **system_description.tex**: Content is substantively identical to v6. The mission overview figure, BOM table, software architecture (11 modules, 4400 LOC), geofence enforcement (5 layers), CV pipeline, search pattern, 20-state FSM, target localisation (CEP50=2.3m, 6-source error budget), ground station, and simulation framework are all present and unchanged. No new hardware photographs or ground station screenshots added. No detection example images.

3. **requirements_verification.tex**: Identical structure and content. R01-R12 verification table with status column. Same closing paragraphs about evidence gaps and highest-risk requirements. No new verification evidence.

4. **evaluation.tex**: Substantively the same. Plus/delta table (P1-P10, D1-D9) is identical. Discussion of key findings, testing framework summary, 5-tier table -- all unchanged. Same figures referenced (conf_vs_alt, det_vs_speed, latency_breakdown, detection_heatmap). No new data or analysis.

5. **exec_summary.tex**: Content appears identical to v6. Same quantitative highlights (20 states, 32 transitions, mAP50=0.995, CEP50=2.3m, 206ms, 4.8 FPS, 74 test scripts, 127 unit tests). Same honest framing of weather cancellation.

### Bottom Line on Changes

**No substantive changes detected between v6 and v7.** The five assessed sections appear to be the same content that was scored at 85.2 in v6. If polish occurred on "Working9.5," it either affected appendices, figures, or other files not in scope of this assessment, or involved formatting/LaTeX refinements not visible in the textual content.

---

## 1. RUBRIC CRITERIA SCORES

### Specialist Skills & Problem-Solving (40%) -- Score: 86/100 (unchanged from v6)

**Strengths (unchanged):**
- Complete quantified pipeline: 1456x1088 capture -> undistortion (+1.5ms) -> 640x640 resize -> YOLOv8n TFLite (206.5ms) -> confidence filter (0.2) -> pixel-to-GPS (GSD) -> inverse-variance Kalman fusion (CEP50=2.3m) -> 20-state FSM -> 7.5m offset landing
- Model retrained 3x (640, 1280, 1088). Final: 366 images, mAP50=0.995 (honestly acknowledged as upper bound)
- 12 defects caught at bench tier with timestamped fixes and counterfactual cost analysis
- Correlation-aware N_eff=1.0 detection probability: conservative, statistically mature
- 6-source error budget with RSS propagation at two altitudes
- Rician distribution landing probability analysis with multi-observation fusion
- 74 test scripts, 127 unit tests across 8 categories
- Dual-backend architecture with single-interface abstraction
- FOV calibration from two independent methods (tape measure + video)

**Weaknesses (unchanged):**
- No outdoor flight data. All hardware validation is bench/video proxy.
- Train/validation overlap: 16 real images out of 366 (4.4%). No independent test set.
- No precision-recall curve. Threshold of 0.2 chosen by visual inspection.
- Payload release not wired into state machine (D8).
- NCNN inconsistency: "9 FPS in full pipeline" vs "not yet benchmarked on Pi" in different sections.

### Decision Making (40%) -- Score: 87/100 (unchanged from v6)

**Strengths (unchanged):**
- MCDA sensitivity analysis: 12 perturbation scenarios per table, all 4 tables, with explicit inversion conditions. Thorough and convincing.
- 5 MCDA trade-off tables with weights established before scoring (stated explicitly).
- STEEPLE analysis: specific, localised, referenced. Not generic boilerplate.
- 216-configuration parametric sweep on real survey polygon geometry.
- 8-step parameter derivation chain with full traceability from target size to energy validation.
- "Decisions That Changed": 4 items following measurement-to-correction pattern. Strongest evidence of adaptive engineering.
- Autonomy justification: Sheridan L7-8/L3-4, asymmetric cost analysis, 20x coverage advantage, timeout derived from energy budget (120s = 5.2% battery).
- NFZ buffer fully traced: half-footprint + GPS CEP + stopping distance = 29.8m -> 30m.
- 20% overlap justified via RSS of 3 error sources (4.5m RSS vs 6.4m margin = 1.4x factor).

**Weaknesses (unchanged):**
- Detection envelope tables still cite "preliminary measurements" without specifying source.
- No stakeholder analysis beyond the brief.
- No structured comparison to commercial/academic SAR systems.
- Some MCDA scores feel generous for Pi 5 (5/5 on four criteria), though sensitivity analysis mitigates.

### Communication (20%) -- Score: 80/100 (unchanged from v6)

**Strengths (unchanged):**
- Professional LaTeX: SI units, consistent formatting, clean tables, proper cross-references.
- ~24 body figures, ~16-17 body tables, 3-4 displayed equations.
- Executive summary is genuinely self-contained and information-dense.
- 29 appendices provide depth without consuming page budget.
- All body figures programmatically generated from real data (gen_*.py scripts).
- Subfigures used effectively (GPS accuracy pair, detection sensitivity pair).

**Weaknesses (unchanged -- these have been flagged since v4):**
- **No hardware photographs.** The report describes a physical system that has been assembled, calibrated, and bench-tested, but zero photos appear. One annotated photo would be worth more than three generated diagrams.
- **No ground station screenshot.** The browser dashboard is described in impressive detail but never shown.
- **No detection example images** at different altitudes. The model's altitude-dependent performance is quantified but never visualised with actual bounding boxes.
- **No confusion matrix in body** (exists as PNG in cv_models/).
- **8-step parameter chain remains text-heavy.** A diagram or numbered table would provide visual relief.
- **decision_flow is an appendix**, so strongest decision-making evidence is outside the body.

---

## 2. OVERALL SCORE

| Criterion | Weight | v5 | v6 | v7 | Weighted (v7) |
|-----------|--------|----|----|-----|---------------|
| Specialist Skills | 40% | 85 | 86 | 86 | 34.4 |
| Decision Making | 40% | 85 | 87 | 87 | 34.8 |
| Communication | 20% | 80 | 80 | 80 | 16.0 |
| **TOTAL** | | **84.0** | **85.2** | | **85.2** |

**Band: 83-89 (High First) -- same position as v6**

---

## 3. HONEST ASSESSMENT

The score is unchanged at 85.2. The content of the five body sections is substantively identical to what was assessed in v6. No new figures, tables, data, or analytical content were detected in the sections under review.

The report remains genuine High First quality. The analytical depth -- 216-config sweep, correlation-aware detection statistics, Rician landing probability, Kalman-filtered GPS fusion, 6-source error budget, MCDA sensitivity analysis -- is well above typical MSc level.

### What Would Move the Score

The same recommendations from v6 remain, now flagged for the fourth consecutive scoring:

| Action | Time | Impact | Status |
|--------|------|--------|--------|
| Hardware photograph(s) | 15 min | +2-3 Comm | Not done (flagged v4-v7) |
| Ground station screenshot | 10 min | +1 Comm | Not done (flagged v4-v7) |
| Detection examples at 15/30/50m | 15 min | +1 Comm, +0.5 Spec | Not done (flagged v4-v7) |
| Clarify "preliminary measurements" | 5 min | +1 Decision | Not done (flagged v5-v7) |
| Confusion matrix in body | 10 min | +0.5 Comm, +0.5 Spec | Not done (flagged v4-v7) |
| **Total quick wins** | **~55 min** | **+4-6 marks** | **None addressed** |

With all quick wins: ~87-88. With outdoor flight data: ~89-90. Without either: 85.2 is the ceiling.

The fundamental constraints remain:
1. **Cannot fix:** No outdoor flight data (caps score at ~87-88 regardless of writing).
2. **Can fix in <1 hour:** Visual content (photos, screenshots, detection images, confusion matrix). These are the lowest-hanging fruit and have been the top recommendation for four consecutive scoring rounds.

---

## 4. SCORING TRAJECTORY

| Version | Date | Specialist | Decision | Communication | Total | Key Driver |
|---------|------|-----------|----------|---------------|-------|------------|
| v4 | 2026-03-27 | 82 | 80 | 78 | 80.4 | Baseline |
| v5 | 2026-04-03 | 85 (+3) | 85 (+5) | 80 (+2) | 84.0 (+3.6) | decision_flow, 216-config sweep, Pareto, N_eff |
| v6 | 2026-04-03 | 86 (+1) | 87 (+2) | 80 (0) | 85.2 (+1.2) | MCDA sensitivity analysis |
| v7 | 2026-04-03 | 86 (0) | 87 (0) | 80 (0) | 85.2 (0) | No substantive changes detected |

Diminishing returns have fully set in for text-based improvements. The next meaningful jump requires visual content (quick wins) or new data (flight, PR curve, independent test set). The analytical writing is at or near its ceiling without new evidence to discuss.
