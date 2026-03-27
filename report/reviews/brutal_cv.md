# Brutal CV/Vision Appendix Review

Reviewed files:
- `sections/04_computer_vision.tex` (main body CV section)
- `sections/cv_extended.tex` (appendix: extended CV analysis)
- `sections/12_model_training.tex` (appendix: training & dataset)
- `sections/inference_architecture.tex` (appendix: edge inference)
- `sections/vision_performance.tex` (appendix: operational envelope)
- `sections/model_comparison.tex` (appendix: model generations & future)

---

## 1. NUMBER INCONSISTENCIES

### 1.1 Confidence threshold: 0.2 vs 0.4
- `config.py`: `CONFIDENCE_THRESHOLD = 0.2`
- `vision.py`: `DEFAULT_CONF_THRESHOLD = 0.4` (hardcoded default)
- `04_computer_vision.tex` line 69: "default 0.2, set in config.py" -- correct per config.py
- `cv_extended.tex` line 65: "confidence threshold of 0.2" -- matches config.py
- `vision_performance.tex` line 29: "Confidence threshold 0.2" -- matches config.py
- **PROBLEM**: `vision.py` hardcodes 0.4 as the class-level default. If config.py override isn't passed, actual runtime threshold is 0.4, not 0.2. The report consistently says 0.2, but the code default is 0.4. Verify which value is actually used at runtime. If vision.py's 0.4 wins, all the "low threshold favours recall" reasoning is based on the wrong number.

### 1.2 HFOV: 49.3 deg vs 49.4 deg vs 54.4 deg
- `cv_extended.tex` line 121: "theta_H approx 49.3 deg"
- `04_computer_vision.tex` line 114: "theta_HFOV approx 49.4 deg"
- `CLAUDE.md` / `MEMORY.md`: "FOV calibrated to 54.4 deg HFOV for cropped DJI video"
- **Distinction**: 49.3-49.4 deg is from the thin-lens formula (sensor_width/focal_length), 54.4 deg is the empirically calibrated FOV from the DJI video tool. The report uses 49.3-49.4 everywhere. These are computed from IMX296 params and are self-consistent. The 54.4 value is for the DJI camera (different sensor), so no actual conflict. But the 49.3 vs 49.4 rounding inconsistency between cv_extended and 04_computer_vision should be harmonised. **Pick one: 49.3 deg.**

### 1.3 Detection rate denominator: 30/30 vs 50/50
- `04_computer_vision.tex` Table 3 (line 100): "Detection rate: 30/30"
- `cv_extended.tex` Table (line 87): "50/50 (100%)"
- **These are from different benchmark runs** (30-run in main body, 50-run in extended). Both correct, but a reader comparing them will be confused. Add a note to the main body table saying "30-run test" or harmonise to 50/50 everywhere since the extended analysis uses the more rigorous 50-run protocol.

### 1.4 v1 mAP50: ~0.94 vs ~0.95
- `cv_extended.tex` line 288: "v1 model achieved mAP50 = 0.94"
- `12_model_training.tex` Table (line 166): "v1: ~0.95"
- `model_comparison.tex` Table (line 17): "v1: ~0.95"
- **Pick one.** These are approximate, but the inconsistency is sloppy. Use ~0.95 everywhere (matches 2 of 3 sources).

### 1.5 Training time: 45 min vs 47 min
- `12_model_training.tex` line 143: "approximately 45 minutes"
- `cv_extended.tex` line 277: "47 min"
- **Pick one.** ~45 min is fine for both.

### 1.6 Search speed: 8 m/s vs 6-10 m/s vs 10 m/s
- Multiple sections use different "nominal" speeds:
  - `04_computer_vision.tex`: "8 m/s" as nominal at 35m
  - `inference_architecture.tex` line 127: "8 m/s" at 35m
  - `vision_performance.tex`: uses adaptive schedule 6-10 m/s
  - `cv_extended.tex` line 165: "10 m/s" as "Default SEARCH_SPEED"
- **PROBLEM**: cv_extended Table says 10 m/s is the "Default SEARCH_SPEED" but the main CV section says 8 m/s is "nominal at 35m". These might both be correct (10 m/s is the config default, 8 m/s is the altitude-interpolated value at 35m), but the labelling is confusing. Clarify in cv_extended that 10 m/s is the maximum and 8 m/s is the interpolated value at the nominal 35m search altitude.

### 1.7 Model file size: 3.2 MB confusion
- The v1/v2 (sar_640, sar_1280) are 3.2 MB, but the deployed v3 (sar_v2_1088) is 11.7 MB
- `04_computer_vision.tex` benchmark table shows "3.2 MB" as the model -- this is the OLD model
- The main body section talks about deploying the retrained v2 model (11.7 MB) but the benchmark table uses the 3.2 MB model
- **Clarify**: Is the benchmark for the old or new model? cv_extended.tex line 89 has a separate row for sar_v2_1088 at 11.7 MB showing 206.8 ms -- good. The main body table should note which model was used.

---

## 2. DUPLICATED CONTENT

### 2.1 Heavy duplication between files
The following topics are covered in 3+ places with near-identical text:

| Topic | 04_cv | cv_extended | 12_training | inference_arch | vision_perf | model_comp |
|-------|-------|-------------|-------------|----------------|-------------|------------|
| Pipeline stages | Full | Full (repeat) | - | Partial | - | - |
| Benchmark table | Yes | Yes (expanded) | - | Yes (different format) | - | - |
| Backend selection (3-tier) | Full | Full (repeat) | - | Full (repeat) | - | - |
| Model swapping | Mentioned | Full section | Mentioned | - | - | Mentioned |
| Training data composition | Mentioned | Mentioned | Full (2 tables) | - | - | Mentioned |
| Altitude vs pixel size | In benchmark | Full table | - | - | Full table (same data) | - |
| Motion blur analysis | - | Full section | - | - | Full section (same data) | - |
| Frames per flyover | In benchmark | Full table | - | Reference | Full table (same data) | - |
| NCNN projection | Mentioned | - | Mentioned | Full | - | - |
| Quantisation trade-offs | Mentioned | - | - | Full | - | - |
| Confidence threshold rationale | Full | Full (repeat) | - | - | - | - |
| COCO fallback | Paragraph | Paragraph | - | - | - | Full section |

**Worst offenders:**
1. **Backend selection** is written out fully THREE times (04_cv, cv_extended, inference_architecture). Nearly identical text.
2. **Altitude vs pixel size table** appears in BOTH cv_extended AND vision_performance with the same data.
3. **Motion blur** is analysed in BOTH cv_extended (Section "Detection Speed vs Drone Speed") AND vision_performance (Section "Speed vs Motion Blur"). Same equations, same conclusions.
4. **Frames on target** computed in BOTH cv_extended AND vision_performance. Same equation, same table structure.

### 2.2 Recommendation
The appendix sections should be restructured so each topic lives in ONE place:
- `12_model_training.tex`: training data, augmentation, results, limitations -- SOLE OWNER. Good as-is.
- `inference_architecture.tex`: backend selection, quantisation, pipeline threading, streaming, benchmarks -- SOLE OWNER. Remove backend discussion from cv_extended.
- `vision_performance.tex`: altitude, blur, frames, coverage, detection envelope -- SOLE OWNER. Remove altitude/blur/frames sections from cv_extended.
- `cv_extended.tex`: pipeline timing breakdown, mission detection probability, model swapping, field deployment. Remove duplicated sections.
- `model_comparison.tex`: model generations, COCO fallback, overfitting risk, tiling, future work -- SOLE OWNER. Good as-is.

---

## 3. MISSING CONTENT / FIGURES

### 3.1 Missing figures (referenced but may not exist)
Check that these figure files actually exist in the figures directory:
- `training_curves` (12_model_training.tex line 149)
- `confusion_matrix` (12_model_training.tex line 174)
- `benchmark_comparison` (inference_architecture.tex line 123)
- `real_altitude_vs_px` (vision_performance.tex line 88)
- `real_speed_vs_blur` (vision_performance.tex line 136)
- `real_speed_vs_frames` (vision_performance.tex line 186)
- `real_coverage` (vision_performance.tex line 219)
- `real_detection_envelope` (vision_performance.tex line 258)
- `altitude_detection_table` (cv_extended.tex line 231)
- `conf_vs_alt` (cv_extended.tex line 244)
- `detection_envelope` (cv_extended.tex line 255)
- `blur_vs_altitude` (cv_extended.tex line 372)
- `det_vs_speed` (cv_extended.tex line 378)
- `latency_breakdown` (cv_extended.tex line 393)
- **04_computer_vision.tex line 27**: Pipeline figure is a `\fbox` PLACEHOLDER, not a real figure

### 3.2 Missing analysis that would strengthen the report
1. **No real flight detection results.** All confidence/detection-rate numbers are from bench tests (static image) or DJI video replay (different camera). The report should explicitly state this limitation. The altitude performance table (cv_extended.tex) says "empirically observed or interpolated from video replay data" which is honest, but the numbers look too clean (0.98, 0.97, 0.96, 0.94...) -- they appear to be interpolated/estimated, not measured. If they're estimates, label them as such.

2. **No confusion between cv_extended detection_envelope and vision_performance detection_envelope.** Both files have a "detection envelope" figure but they show different things -- cv_extended shows confidence + blur overlay, vision_performance shows a speed-altitude heatmap score. This is fine but potentially confusing. Different figure names help.

3. **No cross-validation or held-out test set results.** The training section (12_model_training.tex) honestly admits train=val overlap, but then the cv_extended appendix presents confidence numbers by altitude as if they're validated. These numbers came from video replay (a form of held-out testing), not from the validation set, which is good -- but this distinction should be made more explicit.

---

## 4. PLAUSIBLE RESULTS TO ADD

These would strengthen the report without fabricating data -- they can be derived from existing data or generated with existing tools:

### 4.1 Generate with existing tools (run the scripts)
1. **Actual latency histogram** from benchmark.py (50 runs). Plot the distribution of inference times. Shows stability. Currently just reported as mean +/- std.

2. **Per-altitude confidence scatter from video_test.py.** The DJI video has SRT telemetry with altitude. Run video_test.py on the 30fps video, extract (altitude, confidence) pairs for every detection, plot as scatter. This gives REAL measured confidence-vs-altitude data instead of the interpolated table.

3. **False positive rate from video replay.** Run v3 model on the full DJI video. Count frames with detections where no mannequin is present. Report as "X false positives in Y frames without target" = FP rate. This is a real held-out metric.

4. **GPS estimation scatter plot.** Already mentioned in CLAUDE.md as existing (CEP50=2.3m from video analysis). Include the actual scatter plot showing estimated target positions vs true position.

5. **Detection rate vs altitude bins from video.** Bin detections by SRT altitude (15-20m, 20-25m, 25-30m, 30-35m, 35-40m, 40-45m, 45-50m), report detection rate per bin. Real data.

### 4.2 Compute analytically (no new experiments needed)
1. **Lawnmower coverage completeness.** Given the search polygon, swath width at 35m, and 20% overlap, compute: total scan lines, total flight distance, estimated flight time, area covered. Show the lawnmower pattern overlaid on the search polygon.

2. **Battery budget for CV.** TFLite inference at 206ms uses ~3W on Pi 5. Over a 15-minute mission: 3W x 900s = 2700J = 0.75 Wh. Negligible vs the 99.9Wh drone battery. Worth stating.

3. **Detection probability vs number of passes.** For a given single-pass detection probability p, plot cumulative detection probability after 1, 2, 3 passes. Shows the value of the multi-pass lawnmower pattern. Simple formula: P(detect in n passes) = 1 - (1-p)^n.

### 4.3 Create missing figures programmatically
1. **Pipeline block diagram** (replace the \fbox placeholder in 04_computer_vision.tex). Draw with TikZ or export from draw.io.

2. **Latency breakdown pie/bar chart.** Data is all in the pipeline timing table. Just needs plotting.

3. **Model generation comparison bar chart.** Three bars for v1/v2/v3 showing mAP50. Simple and visually effective.

---

## 5. QUALITY ISSUES

### 5.1 Overly verbose
- cv_extended.tex is ~400 lines and covers 7 subsections. Several overlap with other appendix files. The unique content (pipeline timing, mission detection probability, model swapping) is ~200 lines. The rest is duplication.
- The backend selection text in cv_extended.tex (lines 294-318) is almost word-for-word the same as 04_computer_vision.tex (lines 32-44) and inference_architecture.tex (lines 14-44).

### 5.2 Self-congratulatory tone
- "Near-perfect detection performance" (12_model_training, line 156)
- "comfortably above this floor" (vision_performance, line 81)
- "entirely negligible" (vision_performance, line 123)
- "never the limiting factor" (vision_performance, line 164)
- The report repeatedly emphasises how well everything works. The limitations section in 12_model_training.tex is excellent and honest -- the rest of the appendices should match that tone.

### 5.3 Projected numbers presented too confidently
- NCNN "~68ms" and "~15 FPS" are from Ultralytics benchmarks on different hardware/software configurations, not measured on this system. The text says "projected" but the tables present them alongside measured values.
- FP16 "~100ms" and "~10 FPS" are theoretical extrapolations. Same issue.
- Recommendation: visually separate measured vs projected in ALL tables (e.g., grey italic for projected, or separate table sections).

### 5.4 Citations needed
- vision_performance.tex has zero citations. It's all first-principles derivation, which is fine, but could cite standard photogrammetry references for the GSD/FOV equations.
- "20px detection threshold" for YOLOv8 (vision_performance.tex line 79) -- needs a citation or explicit caveat that this is empirically estimated, not from the YOLOv8 paper.
- model_comparison.tex line 72: "YOLO11 \cite{yolov8}" -- YOLO11 is cited with the YOLOv8 reference. Either find the YOLO11 paper/release or remove the citation.

### 5.5 Minor errors
- `model_comparison.tex` line 30: "All three models produce identical inference latency (~207ms)" but the actual benchmarks show 206.5-207.2ms. The 207 is fine as a round number but inconsistent with the precise 206.5 used elsewhere.
- `inference_architecture.tex` line 91: "BGR->RGB conversion" listed as part of preprocessing -- but earlier text says no cvtColor is applied on Pi path. Clarification: the BGR->RGB IS applied before TFLite (model expects RGB), just not the spurious RGB->BGR that was previously applied.
- `cv_extended.tex` line 196: f_px = 5.46/5.02 x 1456 = 1584 px. Let me check: 5.46/5.02 = 1.0876, x 1456 = 1583.5. OK, rounds to 1584. Fine.

---

## 6. STRUCTURAL RECOMMENDATIONS

### 6.1 Suggested final structure (eliminate duplication)
```
Main body: 04_computer_vision.tex
  - YOLOv8 architecture (keep)
  - Training summary (keep, points to Sec training)
  - Three-backend design (keep, SOLE location)
  - Preprocessing pipeline (keep)
  - Inference & postprocessing (keep)
  - Smart detection mode (keep)
  - Performance benchmarks (keep)
  - Future speed improvements (keep)

Appendix A: 12_model_training.tex (no changes needed)
  - Training data strategy, domain randomisation, augmentation
  - Synthetic pipeline, real labelling, negative mining
  - Training config, convergence, results
  - Export, deployment, limitations

Appendix B: inference_architecture.tex
  - Compute platform constraints (keep)
  - Backend comparison table (keep -- REMOVE from cv_extended)
  - Quantisation trade-offs (keep)
  - Pipeline architecture / threading (keep)
  - Video streaming (keep)
  - Benchmark methodology (keep)
  - Results & projected improvements (keep)

Appendix C: vision_performance.tex (no changes needed)
  - Altitude vs pixel size
  - Speed vs motion blur
  - Speed vs frames on target
  - Coverage efficiency
  - Combined detection envelope

Appendix D: cv_extended.tex (TRIMMED -- remove duplicated sections)
  - Pipeline timing breakdown (KEEP -- unique)
  - Mission runtime / detection probability analysis (KEEP -- unique)
  - Model swapping & field deployment (KEEP -- unique)
  - REMOVE: "Dual Backend Architecture" (duplicates 04_cv + inference_arch)
  - REMOVE: "Detection Speed vs Drone Speed" blur analysis (duplicates vision_perf)
  - REMOVE: "Detection Performance vs Altitude" (duplicates vision_perf)
  - REMOVE: "Model Training Results" (duplicates 12_model_training)

Appendix E: model_comparison.tex (no changes needed)
  - Model generations comparison
  - COCO fallback
  - Overfitting risk
  - Tiling vs full-frame
  - Future improvements
```

### 6.2 Quick wins (can be done in 30 minutes)
1. Fix 0.94 -> 0.95 for v1 mAP in cv_extended.tex
2. Fix 49.3 -> 49.4 (or vice versa) for HFOV consistency
3. Fix training time to one value (45 or 47 min)
4. Add "(30-run test)" note to main body benchmark table or change to 50/50
5. Replace pipeline figure placeholder with actual figure
6. Clarify "Default SEARCH_SPEED" label in cv_extended detection probability table

---

## 7. VERDICT

**Content quality: STRONG.** The technical depth is impressive -- first-principles derivations, honest limitations, multi-angle analysis. The training section (12_model_training.tex) is the best-written of the lot.

**Main problem: DUPLICATION.** Five appendix files covering overlapping ground means a reader encounters the same equations, tables, and conclusions 2-3 times. This dilutes impact and looks like padding.

**Second problem: NO REAL FLIGHT DATA.** All performance claims rest on bench tests (static image at 1m) and DJI video replay (different camera, different altitude). The report is honest about this, but adding even basic video replay analysis results (confidence scatter by altitude, false positive count) would significantly strengthen the empirical foundation.

**Third problem: PROJECTED vs MEASURED.** NCNN and FP16 numbers appear in tables alongside measured TFLite data. These projections are clearly labelled but could mislead a skimming reader. Visual separation would help.

**Priority fixes:**
1. Deduplicate (remove ~150 lines of repeated content from cv_extended.tex)
2. Harmonise the 5 number inconsistencies listed above
3. Generate real data from video_test.py (confidence scatter, FP rate, detection rate by altitude bin)
4. Replace pipeline figure placeholder
5. Add citations to vision_performance.tex
