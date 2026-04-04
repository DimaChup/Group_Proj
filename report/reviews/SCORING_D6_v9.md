# D6 Company Report Scoring -- v9 Assessment

Scored: 2026-04-04
Previous: v7 scored 2026-04-03 (85.2/100)
Sections assessed: exec_summary, intro_d6, design_rationale, system_description, requirements_verification, evaluation
Appendices sampled: estimation_evaluation (AG), localization_approaches (AF), requirements_detail (AH), evaluation_detail (AI), development_methodology (AJ)
Total figures in figs/: 162 files (PNG+PDF+JPG)
Total \includegraphics across all sections: 98
Total \cite across all sections: 188
Bibliography: ~1209 lines across 2 .bib files
Appendices: 36 (A through AJ)

---

## 0. DELTA FROM v7

### What Changed Since v7 (85.2)

Major new content detected:

1. **Appendix AF: Localization Approaches** (NEW) -- 10 geolocation methods surveyed with mathematical basis, pros/cons, accuracy estimates, computational cost, and suitability assessment for each. Includes direct georeferencing, multi-frame triangulation, Kalman filtering, VSLAM, bundle adjustment, template matching, IVW clustering, particle filters (inferred from 10-method count), optical flow, and IMU integration. Each approach has equations and explicit comparison to the deployed system. This is a genuine literature survey with engineering judgment -- substantial specialist content.

2. **Appendix AG: Estimation Evaluation** (NEW) -- Systematic ground-truth comparison with 7 estimation strategies on DJI replay data (Table with CEP50 from 5.1m down to 1.5m). Bullseye visualization methodology explained. Frame budget analysis at 3 speeds. Clustering threshold comparison table (5 configs). Error waterfall chart. Centrality weighting heatmap. Convergence plots (2 figures). Error budget breakdown at 3 altitudes. This appendix alone is ~15 pages of quantitative analysis with ~10 figures.

3. **Appendix AH: Requirements Detail** (NEW/EXPANDED) -- Full evidence narratives for R01-R12. R01 alone runs ~40 lines with 5 verification mechanisms explained. R05 includes the correlation-aware N_eff detection probability calculation with concrete numbers. R07 has Rician probability analysis with multi-observation fusion. Each requirement ends with an italicized summary. This converts the sparse body table into deep evidence.

4. **Appendix AI: Evaluation Detail** (NEW) -- Defect register table (13 bugs with tier, fix time, counterfactual cost). "What Would Change" section (5 items). 4 lessons learned. This is reflective engineering judgment of high quality.

5. **Appendix AJ: Development Methodology** (NEW) -- 10-phase timeline table. Development philosophy (3 principles). Progressive trust methodology.

6. **New figures**: error_waterfall, error_budget_breakdown, centrality_weighting, bullseye_comparison, convergence_plot (evaluation appendix). These are data-driven analytical figures, not decorative.

7. **Body sections**: Substantively similar to v7 in the 5 counted sections. The new appendices support but do not change the body text.

### Bottom Line on Changes

**Significant new appendix content (AF, AG, AH, AI, AJ).** The estimation evaluation appendix alone represents a meaningful research contribution. The localization survey is a proper literature review. The requirements detail converts sparse verification claims into deep evidence narratives. The body text is unchanged, so Communication score is constrained by the same visual gaps flagged since v4.

---

## 1. RUBRIC CRITERIA SCORES

### Specialist Skills & Problem-Solving (40%) -- Score: 88/100 (+2 from v7)

**New strengths (v9):**
- 10-method localization survey with mathematical formulation for each, explicit suitability rankings, and honest assessment of why simpler methods outperform theoretically superior ones given Pi 5 constraints
- 7-strategy GPS estimation comparison table with CEP50 ranging from 5.1m (single frame) to 1.5m (multi-pass IVW), backed by actual DJI replay data
- Systematic clustering threshold comparison: 5 configs evaluated with lock probability, response time, and trade-off description -- this is parameter engineering with real data
- Frame budget analysis: detection opportunities vs speed, with binomial probability of achieving N detections per pass
- Error waterfall chart decomposing 6 sources by variance contribution (GPS noise 60-70%, attitude 15-25%, quantisation 5-10%, timing lag 5-10%, calibration 2-3%, distortion 1-2%)
- Centrality weighting visualization showing 5x weight ratio centre-to-corner
- Convergence curves showing IVW stabilises at ~5 detections (~1.3s)
- R01-R12 evidence narratives: R01 describes 5 independent enforcement mechanisms. R05 includes correlation-aware N_eff=1.0 calculation. R07 has Rician probability >99% with fusion.

**Persistent strengths (from v7):**
- Complete quantified pipeline end-to-end
- 12 defects caught with timestamped fixes and counterfactual costs
- 74 test scripts, 127 unit tests
- Dual-backend architecture
- 216-config parametric sweep
- 6-source error budget with RSS

**Weaknesses:**
- No outdoor flight data (cannot fix)
- Train/validation overlap: 16 real images out of 366 (4.4%). Still no independent test set.
- No precision-recall curve -- threshold chosen by inspection
- NCNN inconsistency persists across sections
- Localization survey cites limited external references for some approaches (self-contained analysis rather than deeply referenced)

**Why +2**: The estimation evaluation appendix and localization survey demonstrate research-level specialist depth. The 7-strategy comparison table and convergence analysis are the kind of systematic parameter studies that distinguish 88+ from 86. The requirements detail narratives convert soft claims into hard evidence. These are not body-section changes but they substantially strengthen the evidence base that the body sections reference.

### Decision Making (40%) -- Score: 88/100 (+1 from v7)

**New strengths (v9):**
- Clustering threshold is now a studied design parameter with 5 configurations evaluated against real data, not a magic number. The SMART default (5 samples, 2m spread) is justified as the optimal knee of the accuracy-vs-response-time curve.
- Frame budget analysis provides the detection opportunity count that justifies the clustering threshold choice (at 5m/s: 18.7 frames, 14.6 expected detections, P(>=5)>0.99)
- Error budget decomposition justifies the design priority: multi-frame averaging targets the dominant 60-70% GPS noise component, which is the single most effective improvement
- "What Would Change" section (5 items) shows mature engineering self-reflection: the #1 item is "start with Pi hardware from week 3, not week 16" -- directly honest about the simulation-first overshoot
- 4 generalizable lessons learned elevate from project report to engineering knowledge

**Persistent strengths (from v7):**
- MCDA sensitivity analysis: 12 perturbations per table, 4 tables
- 216-configuration sweep
- 8-step parameter derivation chain
- "Decisions That Changed": 7 items
- Autonomy justification: Sheridan L7-8/L3-4 with asymmetric cost analysis
- NFZ buffer traced: half-footprint + GPS CEP + stopping = 29.8m -> 30m

**Weaknesses:**
- Detection envelope tables still cite "preliminary measurements" without full source
- Some MCDA scores still feel generous for Pi 5
- No formal sensitivity analysis on the clustering threshold choice itself (only descriptive comparison)

**Why +1**: The clustering threshold study and error budget decomposition demonstrate that design parameters were systematically evaluated rather than chosen by intuition. The "What Would Change" section is particularly valuable -- it shows the team can identify their own strategic errors (simulation-first overshoot) and propose concrete corrections.

### Communication (20%) -- Score: 82/100 (+2 from v7)

**New strengths (v9):**
- 162 figure files (vs ~100 previously estimated). Many are analytical (error waterfall, centrality heatmap, convergence plots, bullseye comparison) rather than decorative.
- 36 appendices now form a coherent reference system: the Appendix Guide table provides a 1-page directory with thematic grouping
- Estimation evaluation appendix is well-structured: methodology -> visualization -> threshold comparison -> error budget -> ground truth -> convergence
- Requirements detail narratives follow a consistent format: mechanism description -> evidence -> italicized summary
- 188 citations across sections -- well-referenced

**Persistent strengths:**
- Professional LaTeX: SI units, consistent formatting, clean tables
- Exec summary genuinely self-contained and information-dense
- Subfigures used effectively
- All body figures programmatically generated

**Persistent weaknesses (flagged since v4):**
- **No hardware photographs.** Still zero photos of the assembled drone, Pi, camera, or field day setup. This has been the #1 recommendation for 5 consecutive scorings.
- **No ground station screenshot.** The browser dashboard is described but never shown.
- **No detection example images** at different altitudes with bounding boxes
- **No confusion matrix in body** (exists in cv_models/)
- **Teammate names redacted** ([TEAMMATE 3-5] and "[Surname]") -- acceptable for draft but loses marks if submitted this way
- Body sections unchanged: same figure density, same visual content

**Why +2**: The appendix structure improvements (guide table, thematic grouping, 36 total) and the analytical figures in the estimation evaluation appendix improve the overall document as a reference. The requirements detail narratives make the verification claims much more convincing. However, the body-section visual gaps remain. The +2 reflects the goldmine's improved depth as a team resource, not body-section improvements.

---

## 2. OVERALL SCORE

| Criterion | Weight | v5 | v6 | v7 | v9 | Weighted (v9) |
|-----------|--------|----|----|-----|-----|---------------|
| Specialist Skills | 40% | 85 | 86 | 86 | 88 | 35.2 |
| Decision Making | 40% | 85 | 87 | 87 | 88 | 35.2 |
| Communication | 20% | 80 | 80 | 80 | 82 | 16.4 |
| **TOTAL** | | **84.0** | **85.2** | **85.2** | | **86.8** |

**Band: 83-89 (High First) -- improved within band**

---

## 3. WHAT THE 5 BODY SECTIONS DO WELL

1. **Claims backed by data**: Yes, extensively. Every performance figure traces to a measurement source (bench benchmark, DJI replay, SITL telemetry, unit test). The mAP50=0.995 is honestly flagged as an upper bound with a realistic estimate of 0.85-0.90. CEP50=2.3m is cited with methodology. The 87% single-pass detection rate is from DJI video.

2. **Figures referenced and captioned**: Yes. All 24+ body figures have \ref cross-references and descriptive captions with quantitative content. Subfigure pairs (GPS accuracy, detection sensitivity, latency+heatmap) are well-composed.

3. **Genuinely critical evaluation**: Yes. The plus/delta table has 10 strengths and 9 deltas with specific evidence for each. The "Evaluation of Design Choices" subsection asks "was the right system built?" and gives honest answers (Pi vs Jetson trade-off, Python vs ROS, simulation-first overshoot). The SAR comparison table includes footnotes acknowledging inflated mAP and proxy-only data.

4. **Requirements addressed**: All 12 requirements are in the verification table with method, evidence, and status. Appendix AH provides deep evidence narratives. The honest acknowledgment that R05/R06/R07 lack outdoor flight data and that R06 is SITL-only is appropriate.

5. **What's missing for 90+**: See Section 5.

---

## 4. APPENDIX SUPPORT QUALITY

The appendices substantially strengthen the body sections:

| Body Claim | Supporting Appendix | Quality |
|------------|-------------------|---------|
| CEP50=2.3m | AG: 7-strategy comparison, convergence, error budget | Excellent -- research-grade |
| mAP50=0.995 (upper bound) | C: training pipeline, I: CV extended | Good -- honest about limitations |
| 12 defects caught | AI: full defect register with timestamps | Excellent -- concrete evidence |
| 5-layer geofence | AH (R01, R02): mechanism-by-mechanism narratives | Excellent |
| Detection at 35m | AD: vision performance, real altitude-pixel data | Good |
| Lawnmower pattern optimal | Z, AA: 216-config sweep, Pareto front | Excellent |
| IVW best fusion method | AF: 10-approach survey, AG: 7-strategy comparison | Excellent -- systematic |
| Simulation-first methodology | AJ: 10-phase timeline, lessons learned | Good |

The localization survey (AF) and estimation evaluation (AG) are the standout appendices -- they provide the kind of systematic analysis that elevates a project report toward a research contribution.

---

## 5. PRIORITIZED 80/20 IMPROVEMENT ROADMAP

### Tier 1: Quick wins (<1 hour total, +3-5 marks)

| # | Action | Time | Impact | Target Score Area |
|---|--------|------|--------|-------------------|
| 1 | **Add 1 annotated hardware photo** (drone assembled with callouts for Pi, camera, Cube, GPS) | 15 min | +1.5 Comm | Photo proves the physical system exists |
| 2 | **Add ground station screenshot** (browser dashboard with detection overlay, GPS grid, command buttons) | 10 min | +1.0 Comm | Proves the web UI works |
| 3 | **Add detection montage at 15/25/35/50m** from DJI video with bounding boxes and confidence scores | 15 min | +0.5 Comm, +0.5 Spec | Shows altitude-dependent detection visually |
| 4 | **Fill in teammate names** (replace [TEAMMATE 3-5] and [Surname]) | 5 min | +0.5 Comm | Required for submission |
| 5 | **Add confusion matrix figure in body** (from cv_models/) | 10 min | +0.5 Comm | Standard ML reporting |

**Subtotal Tier 1: ~55 min, +3-5 marks -> 89-91**

### Tier 2: Medium effort (1-3 hours total, +2-3 marks)

| # | Action | Time | Impact | Target Score Area |
|---|--------|------|--------|-------------------|
| 6 | **Run precision-recall threshold sweep** on DJI video (0.1-0.9 in 0.05 steps) and add PR curve figure to body evaluation | 2 hr | +1.0 Spec, +0.5 Decision | Closes D4, replaces "chosen by inspection" with formal operating point selection |
| 7 | **Add field-day bench photo** (Pi on airframe, checkerboard calibration, terminal screen) | 15 min | +0.5 Comm | Proves bench testing happened |
| 8 | **Cross-reference body to appendix more aggressively** -- in evaluation discussion, add "(see Appendix AG for full strategy comparison)" for each key claim | 30 min | +0.5 Comm | Guides reader to the deep evidence |
| 9 | **Clarify "preliminary measurements"** in detection envelope tables -- specify source (bench test date, DJI video timestamp) | 15 min | +0.5 Decision | Removes vagueness from otherwise strong analysis |
| 10 | **Add a "decision tree" figure** for the 8-step parameter derivation chain | 1 hr | +0.5 Comm, +0.5 Decision | Visual version of Table 3, much easier to follow |

**Subtotal Tier 2: ~4 hr, +2-3 marks -> 91-93**

### Tier 3: High effort (requires flight/data, +3-5 marks)

| # | Action | Time | Impact | Target Score Area |
|---|--------|------|--------|-------------------|
| 11 | **One outdoor flight** (even Tier 3 passive only) | 1 day | +3 Spec, +1 Decision | Closes D1, provides real detection data |
| 12 | **Collect 50+ labelled real frames** for held-out test set | 2 hr post-flight | +1 Spec | Closes D5, replaces inflated mAP |
| 13 | **Deploy NCNN and benchmark** on Pi | 2 hr | +0.5 Spec | Closes D2/D9, validates 4.5x speedup claim |

**Subtotal Tier 3: 1 day + 4 hr, +3-5 marks -> 93-95**

---

## 6. SCORE CEILING ANALYSIS

| Scenario | Specialist | Decision | Communication | Total |
|----------|-----------|----------|---------------|-------|
| Current (v9) | 88 | 88 | 82 | **86.8** |
| + Tier 1 quick wins | 89 | 88 | 86 | **87.8** |
| + Tier 2 medium effort | 90 | 89 | 88 | **89.2** |
| + One outdoor flight | 93 | 90 | 89 | **91.0** |
| + Held-out test set + PR curve | 94 | 91 | 89 | **91.8** |
| Theoretical ceiling (no flight) | 90 | 89 | 88 | **89.2** |
| Theoretical ceiling (with flight) | 95 | 92 | 90 | **92.4** |

**Key insight**: The theoretical ceiling without flight is ~89. The gap from 87 to 89 is entirely Communication (visual content). The gap from 89 to 92+ requires real flight data.

---

## 7. SCORING TRAJECTORY

| Version | Date | Specialist | Decision | Communication | Total | Key Driver |
|---------|------|-----------|----------|---------------|-------|------------|
| v4 | 2026-03-27 | 82 | 80 | 78 | 80.4 | Baseline |
| v5 | 2026-04-03 | 85 | 85 | 80 | 84.0 | decision_flow, 216-config sweep |
| v6 | 2026-04-03 | 86 | 87 | 80 | 85.2 | MCDA sensitivity analysis |
| v7 | 2026-04-03 | 86 | 87 | 80 | 85.2 | No changes |
| **v9** | **2026-04-04** | **88** | **88** | **82** | **86.8** | Estimation eval, localization survey, requirements detail |

The +1.6 from v7 comes from new appendix depth (estimation evaluation, localization survey, requirements detail). The body sections are unchanged but now have substantially stronger backing evidence. Diminishing returns on text-based improvements are setting in again -- the next meaningful jump requires visual content (Tier 1) or flight data (Tier 3).

---

## 8. HONEST BOTTOM LINE

This is a genuinely strong report at 86.8. The analytical depth -- 10-method localization survey, 7-strategy estimation comparison with real data, 216-config parametric sweep, correlation-aware detection statistics, Rician landing probability, 36 appendices with research-grade content -- is well above typical MSc level.

**The single fastest path to 90 is spending 55 minutes on Tier 1 visual content.** Hardware photos, ground station screenshots, and detection montages are the only remaining low-effort improvements. Everything else requires either new data (flight) or substantial new analysis (PR curve).

The report's greatest strength is its honesty: the mAP is flagged as inflated, the weather cancellation is framed as information-maximisation rather than hidden, the simulation-first overshoot is self-criticized, and every delta item has a concrete next step. This intellectual honesty is itself a specialist skill that distinguishes the work.

The greatest weakness remains the visual poverty of the body sections relative to the analytical depth. A reader encountering this report for the first time would see dense text, generated diagrams, and zero photographs of a physical system that demonstrably exists. One annotated photo would do more for the Communication score than any further text polish.
