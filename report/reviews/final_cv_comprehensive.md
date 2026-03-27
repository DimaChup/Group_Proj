# Final CV Comprehensive Review

**Files reviewed:**
1. `cv_extended.tex` -- Extended CV analysis (appendix)
2. `inference_architecture.tex` -- NCNN vs TFLite, pipeline, streaming
3. `vision_performance.tex` -- Altitude/speed/blur/coverage analysis
4. `model_comparison.tex` -- Model generations, tiling, future work
5. `12_model_training.tex` -- Training dataset, pipeline, results, limitations

---

## 1. Numerical Consistency Audit

### Inference Latency / FPS

| File | TFLite Latency | FPS | Consistent? |
|------|---------------|-----|-------------|
| cv_extended.tex (Table 2) | 206.5 ms (no undist), 208 ms (undist) | 4.8 | YES |
| inference_architecture.tex (Table 1) | 206.5 ms | 4.8 | YES |
| inference_architecture.tex (Table 2) | 206.5 ms | 4.8 | YES |
| vision_performance.tex (Table 1) | 206 ms | 4.8 | YES |
| model_comparison.tex (para) | ~207 ms, 4.8 FPS | 4.8 | YES |
| 12_model_training.tex | N/A (training file) | N/A | N/A |

**Verdict: CONSISTENT.** Minor rounding (206 vs 206.5 vs ~207) is acceptable.

### mAP Values

| File | mAP50 (v3) | mAP50-95 (v3) | v1 mAP50 | Consistent? |
|------|-----------|---------------|----------|-------------|
| cv_extended.tex (Table 9) | 0.995 | 0.828 | 0.94 | YES |
| model_comparison.tex (Table 1) | 0.995 | 0.828 | ~0.95 | MINOR DIFF |
| 12_model_training.tex (Table 5) | 0.995 | 0.828 | ~0.95 | MINOR DIFF |

**Issue: v1 mAP50 is "0.94" in cv_extended.tex but "~0.95" in the other two files.** The tilde makes it approximate, so this is borderline acceptable, but should be standardised. Recommend using "~0.95" everywhere or "0.94" everywhere.

### Model File Sizes

| File | v3 (sar_v2_1088) | v1 (sar_640) | COCO | Consistent? |
|------|-----------------|-------------|------|-------------|
| cv_extended.tex | 11.7 MB | 3.2 MB | 13.0 MB | YES |
| inference_architecture.tex | 3.2 MB (generic), 3.1 MB (NCNN) | -- | -- | YES |
| model_comparison.tex | 11.7 MB | 3.2 MB | 13 MB | YES |
| 12_model_training.tex | 11.7 MB (TFLite FP32) | -- | -- | YES |

**Verdict: CONSISTENT.**

### Precision / Recall

| File | Precision | Recall | Consistent? |
|------|-----------|--------|-------------|
| cv_extended.tex | 0.994 | 0.989 | YES |
| 12_model_training.tex (Table 5) | 0.994 | 0.989 | YES |

**Verdict: CONSISTENT.**

### Training Details

| File | Epochs | Batch | GPU | Time | Image Size | Consistent? |
|------|--------|-------|-----|------|-----------|-------------|
| cv_extended.tex | 150, best epoch 127 | -- | T4 | 47 min | 1088x1088 | YES |
| 12_model_training.tex | 150 (patience 30) | 8 | T4 | ~45 min | 1088x1088 | MINOR DIFF |

**Issue: Training time is "47 min" in cv_extended.tex but "~45 min" in 12_model_training.tex.** Pick one. 47 min is more specific so likely the real number.

### Dataset Composition

| File | Total | Synthetic | Real | Negative | Consistent? |
|------|-------|-----------|------|----------|-------------|
| cv_extended.tex | 366 (implied) | 300 | 16 | 50 | YES |
| model_comparison.tex | 300+16+50 | 300 | 16 | 50 | YES |
| 12_model_training.tex | 366 | 300 | 16 | 50 | YES |

**Verdict: CONSISTENT.**

### NCNN Projected Performance

| File | NCNN Latency | NCNN FPS | Consistent? |
|------|-------------|----------|-------------|
| cv_extended.tex | ~68 ms (mentioned) | ~15 | YES |
| inference_architecture.tex | ~68 ms | ~15 | YES |
| 12_model_training.tex | ~3x speedup | -- | YES (3x of 207 = ~69 ms) |

**Verdict: CONSISTENT.**

### Confidence Threshold

| File | Threshold | Consistent? |
|------|-----------|-------------|
| cv_extended.tex | 0.2 | YES |
| vision_performance.tex | 0.2 | YES |

**Note:** CLAUDE.md says 0.4 is the threshold in vision.py, but the report consistently says 0.2. Either the code was updated or the report is aspirational. Should verify which is actually deployed.

### Camera/Sensor Parameters

| Parameter | cv_extended | vision_performance | inference_arch | Consistent? |
|-----------|------------|-------------------|---------------|-------------|
| Sensor width | 5.02 mm | 5.02 mm | -- | YES |
| Focal length | 5.46 mm | 5.46 mm | -- | YES |
| Resolution | 1456x1088 | 1456x1088 | -- | YES |
| Model input | 640x640 | 640x640 | 640x640 | YES |
| Shutter | global | global, 1/1000s | -- | YES |

**Verdict: CONSISTENT.**

### Altitude vs Pixel Size

| Alt (m) | cv_extended px | vision_performance px | Consistent? |
|---------|---------------|----------------------|-------------|
| 20 | 142 (full), 72 (note: different basis) | 84 (model input) | SEE NOTE |
| 30 | 95 | 56 | SEE NOTE |
| 35 | 81 | 48 | SEE NOTE |
| 50 | 57 | 34 | SEE NOTE |

**Issue: cv_extended.tex and vision_performance.tex use DIFFERENT pixel size columns.** cv_extended reports "Dummy px" as pixels in the 640x640 model input but computes it differently from vision_performance.tex. At 20m: cv_extended says 142 px, vision_performance says 84 px (model input) and 143 px (full frame). The 142 vs 143 discrepancy is rounding. But cv_extended's "Dummy px" column header is ambiguous -- it appears to be full-frame pixels (matching the 143 in vision_performance), not model-input pixels. Meanwhile the detailed altitude table in cv_extended (Table 7, altitude performance) lists 72 px at 20m, matching vision_performance's 84... no, those differ too.

**Deeper analysis:** cv_extended Table 4 (footprint) says 142 px at 20m and the text says this is "subtended by a 1.8m target along the vertical axis of the 640x640 model input (computed as 1.8/GSD x 640/1088)". But 1.8/0.0127 x 640/1088 = 141.7/1088 x 640 = wait, that's 1.8/0.0127 = 141.7 in sensor pixels, then 141.7 x 640/1088 = 83.3 in model pixels. So the text describes model-input pixels but the NUMBER 142 is sensor pixels. This is a **contradiction in cv_extended.tex itself**.

Meanwhile cv_extended Table 7 (altitude performance) says 72 px at 20m, which doesn't match either 142 or 84.

And vision_performance.tex Table 2 says 84 px (model input) and 143 px (full frame) at 20m.

**CONTRADICTION FOUND:** cv_extended.tex Table 4 says "Dummy px" = 142 at 20m and claims it's model-input pixels, but the actual model-input value should be ~84 (as correctly shown in vision_performance.tex). The 142 is the full-frame sensor pixel value. The column description in the text is wrong, or the numbers are wrong.

Additionally, cv_extended.tex Table 7 gives yet a third value (72 px at 20m) which doesn't match either calculation.

**ALSO:** vision_performance.tex Eq.3 computes model pixels as `(d / H_gnd) * N_v * 640/max(N_h,N_v)`. With N_v=1088, N_h=1456, max=1456: `(1.8/13.8) * 1088 * 640/1456 = 0.1304 * 1088 * 0.4396 = 62.4`. But the table says 84. Let me recheck: H_gnd at 20m = W_gnd * N_v/N_h = (5.02*20/5.46) * 1088/1456 = 18.39 * 0.747 = 13.74m. Then (1.8/13.74)*1088*(640/1456) = 0.131*1088*0.4396 = 62.7. The table says 84. There's a formula mismatch -- the equation and the table numbers don't agree in vision_performance.tex either. This suggests the equation may have an error or the table was computed with a different formula.

**This is a significant cross-file inconsistency in pixel-size calculations.** Three different numbers appear for the same quantity (dummy pixels in model input at 20m): 142, 84, and 72.

---

## 2. Claims Without Evidence

| Claim | File | Evidence? |
|-------|------|-----------|
| "50/50 detection at 0.966 confidence" | cv_extended | YES -- benchmark script results |
| "mAP50 = 0.995" | multiple | YES -- but train=val overlap caveat is honestly stated |
| "NCNN ~68ms / ~15 FPS" | inference_arch | PARTIAL -- cites Ultralytics benchmark, not own measurement. Clearly labelled "projected" |
| "NCNN FP16 ~45ms / ~22 FPS" | inference_arch | NO -- pure projection, no citation. Labelled "projected" but combines two unverified multipliers |
| "FP16 ~100ms / ~10 FPS" | inference_arch | NO -- projected based on theoretical 2x throughput of FP16. Not measured. Honestly labelled |
| "Hailo-8L >60 FPS" | inference_arch | NO -- no citation or measurement. Hardware not integrated |
| "INT8 ~30% speedup" | inference_arch | WEAK -- cites TFLite docs generally, no specific YOLOv8n benchmark |
| "2-thread 38% slower" | inference_arch | YES -- implies measured ("confirmed") |
| "p_d = 0.90 at 35m" | cv_extended | PARTIAL -- extrapolated from video replay, not rigorous field test |
| "p_d = 0.70 at 50m" | cv_extended | PARTIAL -- same caveat |
| "Sub-200ms MJPEG latency" | inference_arch | NOT MEASURED -- claimed but no measurement methodology described |
| "v1 frequent false positives" | model_comparison | QUALITATIVE -- no quantified FP rate for v1 |
| "Near-zero false positives" for v3 | model_comparison | YES -- 0/50 on negative set, but small sample |
| "Mosaic augmentation" effectiveness | 12_model_training | CITED (Bochkovskiy 2020) |
| "Domain randomisation" principle | 12_model_training | CITED |
| "Negative mining" rationale | 12_model_training | CITED (Shrivastava 2016) |

**Verdict:** Most claims are either evidenced or honestly labelled as projected. The altitude-dependent detection probabilities (p_d values in Table 6) are the weakest -- presented as authoritative numbers but sourced from limited video replay, not systematic field testing.

---

## 3. Is the Training Story Compelling?

**YES -- this is one of the strongest parts of the CV coverage.**

Strengths:
- Clear three-generation narrative (v1 -> v2 -> v3) showing learning from each iteration
- Honest about train/val overlap and its implications
- Excellent limitations section in 12_model_training.tex -- 7 specific, well-articulated limitations
- Domain randomisation is well-explained with proper citations
- The synthetic-real-negative three-source strategy is well-motivated
- Augmentation table is comprehensive and each choice is justified
- The "few-shot anchoring" framing is effective

Weaknesses:
- The 16 real images are presented well but the reader may question if this is enough for reliable generalisation. The text acknowledges this.
- No learning curves or loss plots are shown (referenced but not included as figures)
- No cross-validation or proper train/test split -- acknowledged honestly
- The claim that "real frames proved disproportionately valuable" has no quantitative backing (e.g., ablation study without real frames)

---

## 4. Is the NCNN vs TFLite Comparison Fair?

**MOSTLY FAIR, with caveats.**

The comparison is honest about the key facts:
- TFLite 206.5ms is MEASURED; NCNN 68ms is PROJECTED (from Ultralytics benchmarks)
- The reason for not deploying NCNN (fragile build dependency on Python 3.13/aarch64) is legitimate
- The argument that 4.8 FPS is sufficient for the mission profile is well-supported by the frames-per-flyover analysis

**Fairness issues:**
1. The NCNN "~68ms" number comes from Ultralytics' own benchmarks, not independent testing. Ultralytics has an incentive to show fast NCNN numbers. This should be noted.
2. The projected NCNN FP16 at "~45ms / ~22 FPS" combines two unverified multipliers (NCNN speedup * FP16 speedup) with no basis for multiplication being valid.
3. The Hailo-8L entry (">60 FPS, <15ms") is speculative marketing-level performance with no citation.
4. Table in inference_architecture.tex mixes "Measured", "Projected", and "Hardware" status labels, which is good practice, but the "Projected" numbers carry very different confidence levels (NCNN FP32 from a vendor benchmark vs NCNN FP16 from pure speculation).

**Recommendation:** Add a footnote to the NCNN FP16 and Hailo-8L rows noting these are extrapolated rather than benchmarked.

---

## 5. Contradictions Found

| # | Issue | Files | Severity |
|---|-------|-------|----------|
| 1 | v1 mAP50: "0.94" vs "~0.95" | cv_extended vs model_comparison, 12_model_training | LOW |
| 2 | Training time: "47 min" vs "~45 min" | cv_extended vs 12_model_training | LOW |
| 3 | Dummy pixel size at 20m: 142 vs 84 vs 72 across tables | cv_extended (Tables 4, 7) vs vision_performance (Table 2) | HIGH |
| 4 | Confidence threshold: 0.2 (report) vs 0.4 (CLAUDE.md/code) | report vs codebase | MEDIUM |
| 5 | Search speed: "8 m/s" nominal in some places, "10 m/s" (SEARCH_SPEED) in others | cv_extended vs vision_performance | LOW -- altitude-adaptive |
| 6 | FOV: cv_extended uses 49.3 deg HFOV (from 5.02mm/5.46mm), vision_performance uses same. But CLAUDE.md mentions "54.4 deg HFOV for cropped DJI video" -- this is a different camera so OK | N/A | N/A (different cameras) |
| 7 | cv_extended Table 4 text says "pixels in 640x640 model input" but numbers are full-frame sensor pixels | cv_extended internal | HIGH |
| 8 | Tiling detection at 30-35m: model_comparison says "24 pixels" for mannequin height; vision_performance says 48-56 px at those altitudes | model_comparison vs vision_performance | MEDIUM |

**Issue #3 and #7 are the most serious.** The pixel-size calculations are inconsistent across files and even within cv_extended.tex. This undermines the quantitative credibility of the altitude analysis.

**Issue #8:** model_comparison.tex Section 4.4 says "the mannequin subtends approximately 24 pixels in height when the 1456x1088 camera frame is resized to the 640x640 inference input" at 30-35m. But vision_performance Table 2 says 48 px (at 35m) and 56 px (at 30m) in the model input. This is a 2x discrepancy. The model_comparison number appears to be wrong.

---

## 6. Redundancy Analysis

There is significant overlap between the five files:
- **Benchmark results** appear in cv_extended (Table 3), inference_architecture (Table 1), and vision_performance (Table 1)
- **Altitude vs pixel size** appears in cv_extended (Tables 4, 7) and vision_performance (Table 2)
- **Model comparison** appears in cv_extended (Table 9) and model_comparison (Table 1) and 12_model_training (Table 5)
- **Training details** appear in cv_extended (Section 5) and 12_model_training (full section)
- **Pipeline timing** in cv_extended (Table 1) and inference_architecture (Section 4)
- **NCNN comparison** in cv_extended (Section 7) and inference_architecture (Section 2)

This repetition is not necessarily bad for an appendix structure (each section can stand alone), but it multiplies the risk of inconsistencies. Every duplicated number is a potential contradiction.

---

## 7. Missing Content

- No confusion matrix figure (referenced but not shown)
- No training loss curves (mentioned "three distinct phases" but no figure)
- No actual NCNN measurement on Pi (understandable but limits the comparison)
- No field-test detection rates (all numbers are bench test or video replay)
- No comparison with other aerial SAR detection systems (how does 4.8 FPS / 0.995 mAP compare to published work?)
- No power consumption data for inference
- No discussion of inference consistency over long missions (thermal drift, memory leaks)

---

## 8. Writing Quality

**Very strong overall.** The technical writing is clear, well-structured, and appropriately detailed. Specific positives:
- Excellent use of tables for quantitative claims
- Good practice of labelling "Measured" vs "Projected"
- Limitations section in 12_model_training is unusually honest for student work
- The frames-per-flyover probability analysis is rigorous and well-presented
- Each design decision (TFLite over NCNN, FP32 over INT8, full-frame over tiling) is justified with specific technical reasoning

Minor writing issues:
- Some redundancy could be reduced with better cross-referencing ("as shown in Table X" rather than repeating numbers)
- The detection envelope scoring function (vision_performance Eq. 6-9) normalisation choices (60 px, 5 frames, 5 px blur) feel arbitrary -- no justification given

---

## 9. Overall CV Coverage Score

| Category | Score | Notes |
|----------|-------|-------|
| Numerical consistency | 65/100 | Pixel-size contradictions across files are serious |
| Evidence quality | 78/100 | Bench measurements solid; altitude performance is interpolated |
| Training narrative | 88/100 | Compelling, honest, well-structured |
| NCNN/TFLite fairness | 75/100 | Honest labelling but some speculative projections |
| Technical depth | 90/100 | Excellent pipeline analysis, probability modelling |
| Writing quality | 88/100 | Clear, well-structured, good tables |
| Honesty/limitations | 92/100 | Unusually candid for student work |
| Completeness | 80/100 | Missing loss curves, confusion matrix figures |
| Cross-file coherence | 60/100 | Too much duplication, inconsistent pixel calculations |

**OVERALL: 78/100**

The CV coverage is technically impressive and well-written, dragged down primarily by the pixel-size calculation inconsistencies across files (which a reviewer would catch) and the duplication that makes consistency hard to maintain. Fixing the pixel numbers and deduplicating the repeated tables would push this to 85+.

---

## 10. Priority Fixes

1. **HIGH: Reconcile pixel-size calculations.** Pick ONE formula, apply it consistently in all tables across all 5 files. The vision_performance.tex approach (separate "full frame px" and "model input px" columns) is clearest. Fix cv_extended Table 4 text (says model-input but shows full-frame numbers).
2. **HIGH: Fix model_comparison tiling section.** "24 pixels" at 30-35m is wrong by ~2x. Should be ~48-56 px.
3. **MEDIUM: Standardise v1 mAP.** Use "~0.95" everywhere (with tilde, since it was never precisely measured).
4. **MEDIUM: Standardise training time.** Use "approximately 45 minutes" or "47 minutes" everywhere, not both.
5. **MEDIUM: Verify confidence threshold.** Report says 0.2, CLAUDE.md says 0.4. Check actual deployed value and make consistent.
6. **LOW: Add cross-references** between files to reduce duplication and improve navigability.
7. **LOW: Add loss curve figure** to 12_model_training.tex (even a simple screenshot from Colab).
