# D6 Company Report Scoring -- v10 Assessment (v16 of report)

Scored: 2026-04-04
Previous: v9 scored 2026-04-04 (86.8/100)
Report version: v16 (~246 pages, 0 compile errors)
Sections assessed: exec_summary, intro_d6, design_rationale, system_description, requirements_verification, evaluation
Total \includegraphics across sections: 98
Total \cite across sections: 188
Bibliography: ~1209 lines across 2 .bib files
Appendices: 36 (A through AJ)
Figures in figs/: 160+ files (PNG+PDF+JPG)

---

## 0. DELTA FROM v9 (86.8)

### What Changed Since v9

Commits v13-v16 represent a sustained polish wave across all body sections. Specific changes:

1. **System Description expanded** (+79 insertions/-30 deletions): Geofence enforcement subsection now describes five independent layers with a dedicated figure (geofence_diagram). MAVLink command table added. Data pipeline five-stage description added. Ground station subsection expanded with latency measurements (300ms at 0.3MB/s). Simulation framework expanded to four levels with defect discovery count (12 defects).

2. **Evaluation expanded** (+82 insertions/-29 deletions): Detection montage figure now inserted in body (detection_montage.png). Radar comparison chart added (radar_comparison.png) comparing against 4 published SAR systems. Mission-level performance table added (Table: estimated mission metrics). Prioritised future work with 7 ranked items. Testing framework summary table added. Closing assessment paragraph significantly strengthened with honest self-criticism.

3. **Design Rationale polished** (+45 insertions/-27 deletions): Consistency fixes to parameter derivation chain. Camera selection subsection sharpened. Cross-references to appendices improved.

4. **Introduction expanded** (+31 insertions/-8 deletions): Report structure paragraph added guiding the reader through sections.

5. **Requirements Verification** (+10 insertions/-4 deletions): Late-stage improvements paragraph added explaining R01/R03/R04/R07/R10/R12 gap closures. Risk ranking of outstanding requirements.

6. **Exec Summary** (minor edit): One-line tweak.

7. **New body figures since v9**: detection_montage (DJI video bounding boxes at altitudes), radar_comparison (6-axis comparison chart), geofence_diagram (5-layer visualization), coverage_vs_time, mission_timeline, pi_system. These are significant -- they address multiple v9 visual gaps.

### What v9 Recommended vs. What Was Done

| v9 Recommendation | Status | Notes |
|---|---|---|
| 1. Annotated hardware photo | NOT DONE | Still zero photographs of the physical drone/Pi/camera |
| 2. Ground station screenshot | NOT DONE | Dashboard described but never shown visually |
| 3. Detection montage at altitudes | DONE | detection_montage.png inserted in evaluation with bounding boxes and confidence scores |
| 4. Fill teammate names | NOT DONE | [TEAMMATE 3-5] and "[Surname]" still redacted in red |
| 5. Confusion matrix in body | EXISTS in figs/ | confusion_matrix.png/pdf generated but not referenced in any body section |
| 6. PR threshold sweep | NOT DONE | Still "chosen empirically" |
| 7. Field-day bench photo | NOT DONE | No photographs at all |
| 8. More body-to-appendix cross-refs | DONE | Cross-refs significantly improved across all sections |
| 9. Decision tree figure | NOT DONE | Parameter chain still table-only |
| 10. One outdoor flight | NOT DONE | Cannot fix |

**Bottom line**: 2 of 10 v9 recommendations addressed (detection montage, cross-refs). The visual poverty problem is partially mitigated by the new generated figures (radar chart, geofence diagram, montage) but real photographs remain absent.

---

## 1. RUBRIC CRITERIA SCORES

### Specialist Skills & Problem-Solving (40%) -- Score: 89/100 (+1 from v9)

**Top 3 Strengths:**

1. **Quantified end-to-end pipeline with honest uncertainty bounds.** Every performance figure traces to a measurement source: 206.5ms inference (50-run bench), CEP50=2.3m (DJI replay with ground truth), 4.8 FPS (XNNPACK CPU), mAP50=0.995 flagged as upper bound with realistic estimate of 0.85-0.90 from 87% video detection rate. The six-source error budget (GPS noise 60-70%, attitude 15-25%, quantisation 5-10%, timing lag 5-10%, calibration 2-3%, distortion 1-2%) with RSS at three altitudes is research-grade.

2. **Systematic multi-objective parameter optimization.** The 216-configuration sweep, 8-step parameter derivation chain (target size -> altitude -> speed -> lane spacing -> scan angle -> NFZ buffer -> coverage -> energy), altitude-speed trade-off contour plot, and Pareto front analysis are well above typical MSc level. The coupling matrix figure shows which variable pairs interact and through which metric.

3. **Progressive testing as a quantified engineering discipline.** 12 defects caught at Tiers 1-3, each with tier, resolution time, and counterfactual flight-day impact. The five-tier framework is not just described but evidenced: 5 at Tier 1 (1.5hr), 6 at Tier 2 (4.7hr), 1 at Tier 3 (video proxy). Seven would have caused mission-critical failures. The defect register in Appendix K with timestamps converts a methodology claim into auditable evidence.

**Top 3 Weaknesses:**

1. **No outdoor flight data.** All performance figures are from simulation, bench, or DJI video proxy. The 87% single-pass detection rate, CEP50=2.3m, and 4.8 FPS are all from controlled conditions. Real outdoor performance under wind, varying lighting, motion blur at speed, and GPS dynamics remains entirely unknown. This caps the specialist score. **Fix**: One passive flight (Tier 4) with the existing codebase would provide real detection data.

2. **Train/validation overlap inflates mAP.** Only 16 of 366 training images (4.4%) are real; the rest are synthetic from the same generation pipeline. The 0.995 mAP is acknowledged as inflated but no held-out test set exists. **Fix**: Collect 50+ labelled frames from a separate flight or different video, evaluate on a zero-synthetic split.

3. **No precision-recall curve.** The confidence threshold (0.2 in evaluation, 0.4 in vision.py -- note the inconsistency) was set by visual inspection. No systematic sweep characterizes the precision-recall trade-off. **Fix**: Replay DJI video at thresholds 0.1-0.9, plot PR curve, identify optimal operating point.

**What would push to 95+:** Real outdoor flight data providing measured detection rate vs altitude, GPS estimation accuracy under dynamic manoeuvres, and a held-out test set with 100+ real labelled frames producing a credible mAP figure.

### Decision Making (40%) -- Score: 89/100 (+1 from v9)

**Top 3 Strengths:**

1. **Four MCDA trade studies with sensitivity analysis.** Companion computer, communication architecture, detection model, and search pattern each have weighted criteria tables with 3-5 candidates scored 1-5. Weights set before scoring (stated explicitly). Sensitivity analysis with +/-0.05 perturbation across 12 scenarios confirms rank stability for all four selected options. The composite MCDA heatmap (mcda_heatmap) is an excellent single-figure summary.

2. **"Decisions That Changed" section with 7 evidence-based corrections.** Each follows observe-diagnose-fix-verify pattern. Three corrections (BGR inversion, geofence sign error, TFLite bbox mismatch) would have caused mission-critical failures. The focal length correction (7.0mm -> 5.46mm) directly impacts the R07 landing accuracy requirement. This section demonstrates engineering maturity -- willingness to admit and document mistakes.

3. **Autonomy level justified through asymmetric cost analysis.** Sheridan L7-8 for search, L3-4 for landing, with quantified false-positive cost (90s, 8% battery, coverage pause, mechanical risk) vs false-negative recoverability (lawnmower revisits). The 120s verify timeout traced to energy budget (6.0 Wh per hover, 5.2% battery, two timeouts retain 89%). This is the kind of principled reasoning that distinguishes high marks.

**Top 3 Weaknesses:**

1. **Simulation-first strategy self-critique is honest but the lesson is not quantified.** The evaluation correctly identifies the 10-week simulation delay as excessive, but doesn't estimate the cost: how many additional flight hours could have been achieved with an earlier hardware start? What was the marginal value of simulation hours 50-100 vs hours 1-50? **Fix**: Add a rough timeline comparison showing the alternative where hardware starts week 3.

2. **Some MCDA scores may be generous.** Pi 5 gets 5/5 on "TFLite/edge-AI support" when it only achieves 4.8 FPS (vs Jetson's 12-30 FPS). The "5 = best" framing rewards being the cheapest viable option but doesn't penalize being 3-6x slower. The scoring is defensible but a more nuanced 10-point scale would reveal finer distinctions. **Fix**: Acknowledge in text that the 1-5 scale compresses meaningful differences.

3. **No formal decision on the confidence threshold.** The threshold appears as 0.4 in config, 0.2 in evaluation text -- this inconsistency itself is a decision-making gap. No analysis shows which threshold optimizes the mission-level objective. **Fix**: State the threshold clearly, justify it, or flag it as a studied open parameter.

**What would push to 95+:** A formal decision analysis on the confidence threshold using a PR curve, a timeline comparison quantifying the simulation-first cost, and outdoor test results that validate or invalidate the design decisions (especially altitude, speed, and NFZ buffer choices).

### Communication (20%) -- Score: 83/100 (+1 from v9)

**Top 3 Strengths:**

1. **Professional LaTeX throughout.** Consistent SI units (\SI, \ang), numbered equations, labeled tables/figures with descriptive captions, subfigure pairs, FloatBarrier usage, and clean bibliography. The exec summary is genuinely self-contained and information-dense -- a model of technical writing.

2. **Evaluation section is remarkably honest.** The plus/delta table (10 strengths, 9 deltas) with specific evidence for each is the gold standard. The comparison with published systems includes footnotes acknowledging inflated mAP and proxy-only data. The closing assessment paragraph ("the system remains incompletely validated") is the kind of intellectual honesty that builds reader trust.

3. **New generated figures significantly improve visual communication.** The detection montage (real DJI frames with bounding boxes), radar comparison chart, geofence 5-layer diagram, altitude-speed trade-off contour, coverage-vs-time plot, and mission timeline collectively address much of the "dense text" criticism from earlier reviews. The body now has ~24 figures across the counted sections.

**Top 3 Weaknesses:**

1. **Still zero photographs of the physical system.** This has been flagged in every review since v4. The drone was assembled, bench-tested, and photographed (calibration session with checkerboard, Pi mounted on airframe). Yet the 246-page report contains exclusively generated diagrams and charts. One annotated photograph of the assembled drone with callouts (Pi, camera, Cube, GPS, frame) would instantly prove the physical system exists. **Fix**: 15 minutes. Take a phone photo or use one from the field day, annotate in PowerPoint/Figma, export as PNG, add to System Description.

2. **No ground station screenshot.** The browser dashboard is described in detail (MJPEG stream, GPS grid, command buttons, 300ms latency) but never shown. A screenshot would prove the web UI works and help the reader understand the operator interface. **Fix**: 10 minutes. Screenshot from a simulation run, crop to the browser window, caption it.

3. **Teammate names still redacted.** [TEAMMATE 3-5] in red text with "[Surname]" is clearly a draft state. This will lose marks if submitted as-is. **Fix**: 5 minutes. Fill in actual names.

**What would push to 95+:** Hardware photographs (assembled drone, bench setup, field day), ground station screenshots, teammate names filled in, and a confusion matrix placed in the CV section body. These are all sub-1-hour fixes. Beyond that, photographs from an outdoor flight would be the single highest-impact visual addition.

---

## 2. OVERALL SCORE

| Criterion | Weight | v5 | v6 | v7 | v9 | v10 (v16) | Weighted (v10) |
|-----------|--------|----|----|-----|-----|-----------|----------------|
| Specialist Skills | 40% | 85 | 86 | 86 | 88 | 89 | 35.6 |
| Decision Making | 40% | 85 | 87 | 87 | 88 | 89 | 35.6 |
| Communication | 20% | 80 | 80 | 80 | 82 | 83 | 16.6 |
| **TOTAL** | | **84.0** | **85.2** | **85.2** | **86.8** | | **87.8** |

**Band: 83-89 (High First) -- improved within band, approaching ceiling without flight data**

---

## 3. CHANGES SINCE v9 -- IMPACT ANALYSIS

The +1.0 from 86.8 to 87.8 comes from:

- **Specialist +1**: The system description is now substantially richer (geofence diagram, 5-stage pipeline, MAVLink table, simulation four-level breakdown with 12 defects). The evaluation gained mission-level metrics and the radar comparison table provides literature context. The detection montage is real evidence from DJI video.

- **Decision +1**: The evaluation's "Evaluation of Design Choices" subsection (Pi vs Jetson, Python vs ROS, lawnmower vs adaptive, single vs multi-class, simulation-first critique) is a mature retrospective that was already present but is now better integrated with quantified comparisons.

- **Communication +1**: Detection montage, radar comparison, geofence diagram, coverage-vs-time, mission timeline, and pi_system figures are all new in body since v9. These address the "visual poverty" criticism. Cross-references to appendices are now systematic ("see Appendix X for..."). However, the photograph gap persists.

**Diminishing returns**: Text-based improvements are yielding <0.5 marks per iteration. The remaining gap to 90 is almost entirely visual content (photographs, screenshots) and data (flight, PR curve).

---

## 4. PRIORITIZED 80/20 IMPROVEMENT LIST

### Tier 1: Quick wins (<1 hour total, +2-4 marks)

| # | Action | Time | Impact | Why |
|---|--------|------|--------|-----|
| 1 | **Add 1 annotated hardware photo** | 15 min | +1.5 Comm | 6th consecutive review flagging this. Photo proves physical system exists. Use any field-day photo. |
| 2 | **Fill in teammate names** | 5 min | +0.5 Comm | Red [TEAMMATE] text will lose marks. Non-negotiable for submission. |
| 3 | **Add ground station screenshot** | 10 min | +0.5 Comm | Run simulation, screenshot browser dashboard, insert in ground station subsection. |
| 4 | **Add confusion matrix in CV section** | 10 min | +0.5 Comm/Spec | confusion_matrix.png already generated in figs/ -- just \includegraphics + caption. |
| 5 | **Fix confidence threshold inconsistency** | 10 min | +0.5 Decision | Body says 0.2, config says 0.4, vision.py says 0.4. Pick one, state it clearly everywhere. |

**Subtotal Tier 1: ~50 min, +3.5 marks -> ~91.3**

### Tier 2: Medium effort (2-4 hours, +1.5-2.5 marks)

| # | Action | Time | Impact | Why |
|---|--------|------|--------|-----|
| 6 | **Run PR threshold sweep** on DJI video | 2 hr | +1.0 Spec/Decision | Closes D4. Produces a figure that replaces "chosen empirically." |
| 7 | **Add field-day bench photo** (checkerboard, Pi on airframe) | 15 min | +0.5 Comm | Proves bench testing happened physically. |
| 8 | **Decision tree figure** for 8-step parameter chain | 1 hr | +0.5 Comm/Decision | Visual version of Table 3, easier to follow than text. |

**Subtotal Tier 2: ~3.5 hr, +2.0 marks -> ~93.3**

### Tier 3: Requires flight/data (+3-5 marks, 1+ day)

| # | Action | Time | Impact | Why |
|---|--------|------|--------|-----|
| 9 | **One outdoor passive flight** (Tier 4) | 1 day | +3 Spec/Decision | Closes D1. Real detection data replaces proxy estimates. |
| 10 | **Collect 50+ labelled real frames** | 2 hr post-flight | +1 Spec | Closes D5. Credible held-out mAP replaces inflated 0.995. |
| 11 | **Deploy NCNN + benchmark** on Pi | 2 hr | +0.5 Spec | Closes D2/D9. Validates 4.5x speedup claim with real data. |

**Subtotal Tier 3: 1 day + 4 hr, +4.5 marks -> ~95+**

---

## 5. SCORE CEILING ANALYSIS

| Scenario | Specialist | Decision | Communication | Total |
|----------|-----------|----------|---------------|-------|
| Current (v16) | 89 | 89 | 83 | **87.8** |
| + Tier 1 quick wins (50 min) | 89.5 | 89.5 | 87 | **89.0** |
| + Tier 2 medium effort (3.5 hr) | 90.5 | 90 | 88 | **89.8** |
| + One outdoor flight (Tier 3) | 93 | 91 | 89 | **91.4** |
| + Held-out test set + PR curve | 95 | 92 | 89 | **92.4** |
| **Ceiling without flight** | **91** | **90** | **88** | **89.8** |
| **Ceiling with flight** | **95** | **92** | **91** | **93.2** |

**Key insight**: The gap from 87.8 to ~89 is almost entirely Communication (visual content -- photographs, screenshots). This is fixable in under 1 hour. The gap from 89 to 93+ requires real flight data that no amount of text polish can substitute.

---

## 6. SCORING TRAJECTORY

| Version | Date | Specialist | Decision | Communication | Total | Key Driver |
|---------|------|-----------|----------|---------------|-------|------------|
| v4 | 2026-03-27 | 82 | 80 | 78 | 80.4 | Baseline |
| v5 | 2026-04-03 | 85 | 85 | 80 | 84.0 | decision_flow, 216-config sweep |
| v6 | 2026-04-03 | 86 | 87 | 80 | 85.2 | MCDA sensitivity analysis |
| v7 | 2026-04-03 | 86 | 87 | 80 | 85.2 | No changes |
| v9 | 2026-04-04 | 88 | 88 | 82 | 86.8 | Estimation eval, localization survey |
| **v10 (v16)** | **2026-04-04** | **89** | **89** | **83** | **87.8** | Body section polish, new figures, cross-refs |

The trajectory shows clear diminishing returns on text-only improvements. Each version since v5 has gained less than the previous. The curve is flattening at ~88-89 without visual/flight data inputs.

---

## 7. WHAT'S GENUINELY EXCELLENT

1. **The evaluation section is the best part of the report.** The plus/delta tables, SAR comparison with honest footnotes, design choice retrospective ("was the right system built?"), mission-level metrics, and the closing paragraph are all genuinely impressive. The simulation-first self-critique is particularly mature.

2. **The design rationale's parameter derivation chain.** Tracing from target size through altitude, speed, scan angle, NFZ buffer, coverage, and energy in an unbroken 8-step chain with every value derived from the previous step is a textbook example of systematic design.

3. **The "Decisions That Changed" section.** Seven evidence-based corrections, each with observe/diagnose/fix/verify, three of which would have been mission-critical failures. This is the most compelling evidence of engineering competence in the report.

4. **The detection montage.** Real DJI video frames with bounding boxes at multiple altitudes is exactly the kind of evidence this report needed. It grounds the abstract performance numbers in visible reality.

---

## 8. HONEST BOTTOM LINE

**87.8/100** -- a strong High First that has essentially reached its ceiling without visual content and flight data.

The analytical content is research-grade in places (estimation evaluation, 216-config optimization, 10-method localization survey). The writing is professional and honest. The quantification is thorough.

**The single fastest path to 89 is 50 minutes of visual content**: one hardware photo (15 min), teammate names (5 min), ground station screenshot (10 min), confusion matrix insertion (10 min), confidence threshold fix (10 min). This is the same recommendation as v9 and the four reviews before it.

**The path to 93+ requires one flight day.** Nothing in the text can substitute for this. The codebase is ready; the bottleneck is scheduling and weather.

The report's intellectual honesty remains its greatest asset. The mAP is flagged as inflated. The weather cancellation is analyzed rather than hidden. The simulation-first overshoot is self-criticized. Every delta has a concrete next step. This kind of engineering maturity is difficult to teach and valuable to demonstrate.
