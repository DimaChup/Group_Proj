# Scoring Rules -- CV Standalone Report

---

## What We Want From This Report

**Purpose:** A standalone ~15-20 page report dedicated entirely to the computer vision pipeline. This is NOT a graded deliverable in itself -- it serves as either (a) a detailed appendix/companion document to D6, (b) a portfolio piece demonstrating CV expertise, or (c) a reference document for the team or future developers.

**Audience:** Technical readers with ML/CV background (markers, colleagues, future maintainers). They will expect standard ML reporting conventions: training methodology, dataset description, benchmark results, ablation studies, precision-recall curves, confusion matrices.

**Page limit:** Self-imposed ~15-20 pages. No external constraint since this is not a graded deliverable, but conciseness is valued.

**Key content that MUST be present:**
1. Problem framing: why CV for aerial SAR is hard (small targets, altitude variation, motion blur, edge hardware, real-time constraint)
2. Model selection rationale with alternatives considered
3. Dataset description: composition, augmentation, train/val split, limitations
4. Training methodology: hyperparameters, convergence, results
5. Deployment architecture: TFLite/NCNN/Ultralytics backends, pipeline stages, latency breakdown
6. Performance evaluation: detection rate, confidence vs altitude, speed vs blur, frames on target
7. Localisation: pixel-to-GPS projection, error budget, Kalman fusion, CEP50
8. Honest limitations: no outdoor flight data, train/val overlap, small real dataset
9. Future work: quantisation, tiling, multi-class, NCNN deployment

**What makes it excellent (since no formal rubric):**
- Standard ML paper structure (Introduction, Related Work, Method, Experiments, Results, Discussion)
- Every claim backed by measured data, not projections
- Clear separation of measured vs projected/estimated results in tables
- Reproducibility: enough detail that someone could replicate the pipeline
- Honest about what was NOT tested (outdoor, diverse conditions, adversarial)

---

## Scoring Rubric (self-assessed, ML paper standards)

Since this is not a formally graded deliverable, we use ML paper conventions:

### Technical Depth (40%)
- **Adequate:** Describes what was built. Shows it works.
- **Good:** Quantified performance. Ablation on key parameters (threshold, resolution, model variant). Error analysis.
- **Excellent:** First-principles derivations (GSD, detection envelope, motion blur model). Statistical treatment (CEP50, N_eff, Rician landing probability). Comparison to baselines. Sensitivity analysis.

### Experimental Rigour (30%)
- **Adequate:** Reports mAP and inference speed.
- **Good:** Reports per-altitude detection rate, speed/blur trade-off, frames on target. Acknowledges limitations.
- **Excellent:** Independent test set (or honest admission of lacking one). Precision-recall curve. Confusion matrix. False positive rate on negative frames. Cross-validation or held-out evaluation.

### Presentation (20%)
- **Adequate:** Readable, correct LaTeX.
- **Good:** Proper figures with captions, consistent notation, clean tables.
- **Excellent:** Pipeline diagrams, latency breakdown charts, detection examples at multiple altitudes, GPS scatter plots, training curves, confusion matrix -- all from real data, not placeholders.

### Reproducibility (10%)
- **Adequate:** Lists tools used.
- **Good:** Specifies hyperparameters, model architecture, input/output shapes.
- **Excellent:** Complete training recipe (Colab cells), dataset download instructions, model file checksums, runtime environment specification.

---

## Priority Checklist (ordered by impact)

### Critical (report credibility):
- [ ] **Fix number inconsistencies** -- confidence threshold (0.2 vs 0.4), HFOV (49.3 vs 49.4), detection rate (30/30 vs 50/50), v1 mAP (0.94 vs 0.95), training time (45 vs 47 min), search speed (8 vs 10 m/s). Pick one value for each, use consistently throughout.
- [ ] **Eliminate duplication between appendix sections.** Backend selection written 3 times (04_cv, cv_extended, inference_architecture). Altitude vs pixel table in 2 places. Motion blur in 2 places. Each topic should live in ONE place.
- [ ] **Separate measured vs projected results** in all tables. NCNN "~68ms" and FP16 "~100ms" are projections, not measurements. Use grey italic or separate table sections.
- [ ] **Replace pipeline figure placeholder** (\fbox in 04_computer_vision.tex). Either TikZ diagram or draw.io export.

### High priority:
- [ ] **Generate real data from video_test.py** -- run on 30fps DJI video and extract: (a) confidence vs altitude scatter, (b) false positive count on frames without mannequin, (c) detection rate per altitude bin. This is real held-out data from a different camera.
- [ ] **Add confusion matrix** -- already exists as PNG in cv_models/sar_v2_1088/. Standard ML reporting.
- [ ] **Add training curves** -- loss/mAP vs epoch. Exists in cv_models/ results.
- [ ] **Clarify which model the benchmarks use** -- main body table says 3.2 MB (old model) but text discusses 11.7 MB retrained model. Specify clearly.
- [ ] **Remove self-congratulatory language** -- "near-perfect detection performance", "entirely negligible", "never the limiting factor", "comfortably above this floor". Replace with neutral reporting.

### Nice to have:
- [ ] **Latency histogram** from benchmark.py (50 runs). Shows inference time distribution/stability.
- [ ] **Detection probability vs number of passes** plot. Simple formula: P = 1 - (1-p)^n.
- [ ] **Model generation comparison bar chart** -- v1/v2/v3 mAP side by side.
- [ ] **Battery budget for CV computation** -- 3W x 900s = 0.75 Wh = negligible vs 99.9 Wh drone battery.
- [ ] **Citations in vision_performance.tex** -- currently zero. Cite photogrammetry references for GSD/FOV equations.
- [ ] **"20px detection threshold" citation** -- needs source or explicit caveat that it is empirically estimated.

---

## Current Score and Gaps

**Current estimated quality: ~75/100** (Good but not excellent by ML paper standards)

**Strengths:**
- Impressive technical depth: first-principles GSD derivation, correlation-aware N_eff, Rician landing probability, 6-source error budget with RSS
- Honest limitations section in training chapter
- Three model generations with clear progression story
- Dual-backend architecture is a genuine engineering contribution
- Comprehensive operational envelope analysis (altitude, speed, blur, coverage)

**Weaknesses preventing "Excellent":**
1. **Heavy duplication** -- ~150 lines of repeated content across 5 appendix files. Backend selection, altitude table, motion blur analysis each appear 2-3 times.
2. **Number inconsistencies** -- 6 different values that conflict between files (see checklist above). Undermines credibility.
3. **No real flight detection data** -- all claims from bench tests (static image at 1m) or DJI video (different camera). Honest about this, but no substitute.
4. **No precision-recall curve** -- threshold of 0.2 chosen by visual inspection, not formal analysis.
5. **No independent test set** -- train/val overlap acknowledged but not mitigated.
6. **Projected results mixed with measured** -- NCNN/FP16 projections appear alongside TFLite measurements in tables.
7. **Pipeline figure is a placeholder** (\fbox not a real diagram).
8. **Self-congratulatory tone** in several appendix sections.
9. **Missing citations** in vision_performance.tex (zero references in an analytical section).

**What would push to 85+:**
- Fix all number inconsistencies
- Eliminate duplication (each topic in ONE file)
- Generate real data from DJI video analysis
- Add confusion matrix and training curves
- Replace pipeline placeholder
- Separate measured vs projected in tables
- Add 5-10 citations to analytical sections

**What would push to 90+:**
- All of the above PLUS:
- Precision-recall curve with operating point
- Independent test set evaluation
- Real outdoor detection data
- Comparison to published aerial detection benchmarks (VisDrone, DOTA)

---

## Figures That Would Be Impressive

### Already exist (just need including properly):
- [ ] Confusion matrix (PNG in cv_models/sar_v2_1088/)
- [ ] Training curves / results (PNG in cv_models/)
- [ ] GPS scatter plot (from video_test.py)
- [ ] Model comparison results (confusion matrices for each generation)

### Need creating:
- [ ] **CV pipeline block diagram** -- frame -> undistort -> resize -> inference -> NMS -> confidence filter -> pixel-to-GPS. Replace the \fbox placeholder.
- [ ] **Latency breakdown bar chart** -- preprocessing, inference, postprocessing, GPS projection. Data exists in tables.
- [ ] **Confidence vs altitude scatter** -- from DJI video replay. Real empirical data.
- [ ] **Detection examples triptych** -- bounding boxes at 15m, 30m, 50m. Visual proof of detection envelope.
- [ ] **False positive rate timeline** -- frames with/without target, showing FP distribution over video.
- [ ] **Detection rate per altitude bin** -- bar chart from DJI video (15-20m, 20-25m, ..., 45-50m).
- [ ] **Model generation comparison** -- 3 bars showing mAP50 for v1/v2/v3.
- [ ] **Detection probability vs passes** -- curve showing P = 1-(1-p)^n for 1-5 passes.

### Would be impressive but high effort:
- [ ] **Precision-recall curve** at the operating threshold
- [ ] **ROC curve** comparing models
- [ ] **Tiling vs full-frame comparison** -- same image, different approaches, detection difference
- [ ] **GSD vs altitude diagram** -- showing how pixel size scales with height, with detection threshold overlay
- [ ] **Kalman filter convergence** -- GPS estimate refining over consecutive detections

### Recommended final structure for figures:
```
Fig 1:  CV pipeline block diagram (replace placeholder)
Fig 2:  Dataset examples (synthetic, real, negative samples)
Fig 3:  Training curves (loss + mAP vs epoch)
Fig 4:  Confusion matrix
Fig 5:  Detection examples at 3 altitudes (15m, 30m, 50m)
Fig 6:  Confidence vs altitude scatter (from DJI video)
Fig 7:  Latency breakdown bar chart
Fig 8:  Detection rate per altitude bin
Fig 9:  GPS estimation scatter (CEP50 = 2.3m)
Fig 10: Model generation comparison (v1/v2/v3 mAP)
```
