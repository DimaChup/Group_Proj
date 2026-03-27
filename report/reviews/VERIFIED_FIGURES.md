# Verified Figures Checklist

**Audit date:** 2026-03-27
**Method:** For each item in USER_REQUESTS_FIGURES.md: (1) checked file exists in figs/, (2) checked \includegraphics reference in a .tex file that is \input'd from main.tex, (3) visually inspected the PNG/PDF.

Status key:
- PASS = file exists, referenced in compiled report, visually correct
- PARTIAL = file exists but not referenced (orphan) or referenced but has issues
- FAIL = file missing, or content does not match what was requested

---

## 1a. Confidence vs Altitude (`conf_vs_alt`)

| Check | Result |
|-------|--------|
| File exists? | YES -- `figs/conf_vs_alt.pdf` (PDF only, no PNG) |
| Referenced? | YES -- `evaluation.tex:67`, `cv_extended.tex:237` |
| In compiled report? | YES -- both sections are \input'd in main.tex |
| Visual check | N/A (PDF, not viewable as image; PNG not generated) |

**Verdict: PASS** (PDF exists and is referenced; cannot visually verify PDF content from CLI but generator script exists)

---

## 1b. Detection Rate vs Speed (`det_vs_speed`)

| Check | Result |
|-------|--------|
| File exists? | YES -- `figs/det_vs_speed.png` + `.pdf` |
| Referenced? | YES -- `evaluation.tex:74`, `cv_extended.tex:371` |
| In compiled report? | YES |
| Visual check | PASS -- Shows detection rate (%) vs ground speed (m/s). Has THREE curves: per-frame detection rate (red dashed), cumulative at 4.8 FPS (blue solid), cumulative at 9.5 FPS projected (orange). Search speed (10 m/s) marked. Dual FPS curves ARE present as user requested. |

**Verdict: PASS**

---

## 1c. Motion Blur vs Altitude (`blur_vs_altitude`)

| Check | Result |
|-------|--------|
| File exists? | YES -- `figs/blur_vs_altitude.png` + `.pdf` |
| Referenced? | YES -- `cv_extended.tex:364` |
| In compiled report? | YES |
| Visual check | PASS -- Two-panel chart (1/100s and 1/500s exposure). Pixel motion per frame vs altitude at 5/10/15 m/s. Shows higher altitude = less blur. Operational envelope shaded. Blur threshold line at ~5 px. Clear and informative. |

**Verdict: PASS**

---

## 1d. Combined Detection Envelope (`detection_envelope`)

| Check | Result |
|-------|--------|
| File exists? | YES -- `figs/detection_envelope.png` + `.pdf` |
| Referenced? | YES -- `cv_extended.tex:247` |
| In compiled report? | YES (appendix via cv_extended) |
| Visual check | PASS -- Confidence vs altitude with motion blur overlaid. Shows ideal (no blur), 10 m/s rolling shutter, 15 m/s rolling shutter, 10 m/s global shutter curves. Operational envelope (15-40m) shaded. Confidence threshold at 0.2 marked. Dual y-axis: confidence + target pixel size. Excellent combined figure. |
| Note | Appendix only. User wanted it prominent -- consider cross-ref from body. |

**Verdict: PASS**

---

## 2a. NFZ Geofence Diagram 4-panel (`geofence_diagram`)

| Check | Result |
|-------|--------|
| File exists? | YES -- `figs/geofence_diagram.png` + `.pdf` |
| Referenced? | YES -- `system_description.tex:94` |
| In compiled report? | YES |
| Visual check | PASS -- 4-panel layout: (a) Without Geofence (path crosses SSSI, 7 segments marked), (b) With Three-Layer Geofence Protection (deflected trajectory, repulsive vectors shown), (c) Speed Reduction Profile (speed ramp from 10 m/s to 0 near boundary), (d) Protection Layer Summary table (4 layers: speed ramp, repulsive force, auto-MANUAL, waypoint filter with distances and mechanisms). All four elements user requested are present: clear boundary, repulsive vector field, speed gradient, before/after correction. |

**Verdict: PASS**

---

## 2b. NFZ Margin vs Altitude (`nfz_margin_altitude`)

| Check | Result |
|-------|--------|
| File exists? | YES -- `figs/nfz_margin_altitude.png` + `.pdf` |
| Referenced? | YES -- `search_optimization.tex:155` |
| In compiled report? | YES |
| Visual check | PASS -- "NFZ Safety Margin vs Altitude" chart. Shows camera footprint radius, total buffer (30m waypoint + 20m speed ramp), safety margin (buffer - footprint), safe zone shading. Operating point marked at 35m, margin=33.9m. Clear and correct. |

**Verdict: PASS**

---

## 3a. State Machine Diagram -- body version (`state_machine`)

| Check | Result |
|-------|--------|
| File exists? | YES -- `figs/state_machine.png` + `.pdf` |
| Referenced? | YES -- `system_description.tex:154` |
| In compiled report? | YES |
| Visual check | PASS -- Simplified 9-state diagram: INIT -> TAKEOFF -> SEARCH -> CENTERING -> VERIFY -> APPROACH -> LANDING -> DONE, with MANUAL override. Color-coded: green (start/end), blue (autonomous), orange (operator decision), red (safety). Clean, readable for body text. |
| Note | This is the simplified body version (9 states). The full version is separate. |

**Verdict: PASS**

---

## 3a-full. State Machine Full (`state_machine_full`)

| Check | Result |
|-------|--------|
| File exists? | YES -- `figs/state_machine_full.png` + `.pdf` |
| Referenced? | YES -- `A1_state_table.tex:12` |
| In compiled report? | YES (appendix) |
| Visual check | PASS -- Full 20-state FSM with all transitions. States grouped into 5 categories (Startup, Transit, Search, Engagement, Safety/Recovery) with color coding. All 20 states visible: INIT, CONNECTING, ARMING, TAKEOFF, PRE_WAYPOINTS, TRANSIT_TO_SEARCH, SEARCH, HOVER, CENTERING, DESCENDING, VERIFY, HOVER_TARGET, APPROACH, LANDING, DONE, MANUAL, RETURN_FROM_MANUAL, RETURN_TO_SEARCH, RETURN_TRANSIT, RETURN_HOME. Transition labels present (M key, detection, N key, Y key, etc.). Complex but complete. |

**Verdict: PASS**

---

## 4a. Mission Overview on Site Map (`mission_overview`)

| Check | Result |
|-------|--------|
| File exists? | YES -- `figs/mission_overview.png` + `.pdf` |
| Referenced? | YES -- `system_description.tex:12` |
| In compiled report? | YES |
| Visual check | PASS -- "Mission Overview -- Fenswood Wilderness Site". Shows flight area boundary (blue dashed), search area (green solid), SSSI no-fly zone (red hatched), focus area/PLB (orange dashed), search pattern (grey arrows), take-off location (yellow star), target (red diamond), GPS estimates (green cluster), landing point (green diamond, 7.5m offset), RTL path (grey dashed). North arrow and 50m scale bar. All zones shown as requested. |

**Verdict: PASS**

---

## 5a. Bullseye GPS Scatter with CEP50 (`gps_bullseye`)

| Check | Result |
|-------|--------|
| File exists? | YES -- `figs/gps_bullseye.png` + `.pdf` |
| Referenced? | YES -- `system_description.tex:207` |
| In compiled report? | YES |
| Visual check | PASS -- "Target GPS Estimation Accuracy" bullseye plot. Concentric circles at 5m, 10m, 15m. GPS estimates as blue scatter points. CEP50 = 2.3m (orange box), CEP95 = 5.1m (red dashed). True position (red cross) at center. Centroid at (+0.6, -0.2)m. Diagonal spread visible (consistent with GPS timing lag). Exactly what was requested. |

**Verdict: PASS**

---

## 6a. Benchmark Comparison (`benchmark_comparison`)

| Check | Result |
|-------|--------|
| File exists? | YES -- `figs/benchmark_comparison.png` + `.pdf` |
| Referenced? | **NO** -- not referenced by any \includegraphics in any .tex file |
| In compiled report? | NO (orphan file). However, `pipeline_fps.tex` has a TikZ-drawn stacked bar chart that serves the same purpose inline. |
| Visual check | The PNG shows "Inference Benchmark Comparison -- Pi 5 ARM Cortex-A76". Bar chart with 6 backends: TFLite FP32 best.tflite (4.8 FPS), TFLite FP32 sar_v2_1088 (4.8 FPS), TFLite FP32 human.tflite (4.7 FPS), NCNN FP32 projected (10.9 FPS), TFLite FP16 projected (8.9 FPS), Ultralytics PyTorch laptop (0.8 FPS). Distinguishes measured (solid blue) vs projected (hatched orange). Shows raw inference time in ms. |
| Note | The TikZ chart in `pipeline_fps.tex` covers the same data as a stacked bar (capture + preprocess + inference + postprocess breakdown). The PNG is an **orphan** -- generated but never included. User wanted "raw vs effective FPS" which the TikZ chart does better. |

**Verdict: PARTIAL** -- File exists and looks correct, but is NOT included in the compiled report. The TikZ chart in `pipeline_fps.tex` partially covers the same ground. If both raw and effective FPS comparison is desired as a standalone figure, this PNG needs an \includegraphics reference.

---

## 7a. Energy Efficiency Path (`energy_efficiency`)

| Check | Result |
|-------|--------|
| File exists? | YES -- `figs/energy_efficiency.png` + `.pdf` |
| Referenced? | YES -- `search_optimization.tex:61` |
| In compiled report? | YES |
| Visual check | PASS -- "Search Configuration: Mission Time vs Energy Consumption". Pareto frontier scatter plot. X-axis: mission time (s), Y-axis: energy (Wh), color: coverage (%). Selected config (35m, 8 m/s) marked with star. Fastest and most efficient configs labelled. From actual 216-config simulation sweep. |

**Verdict: PASS**

---

## 7a-extra. Real Energy Heatmap (`real_energy_heatmap`)

| Check | Result |
|-------|--------|
| File exists? | YES -- `figs/real_energy_heatmap.png` |
| Referenced? | YES -- `path_optimization_definitive.tex:90` |
| In compiled report? | YES |
| Visual check | PASS -- "Energy Heatmap: Altitude x Scan Angle". Viridis colormap, altitude (20-50m) on y-axis, scan angle (0-170 deg) on x-axis. Best config marked: 50m, 70 deg, 8.3 Wh. Clear minimum visible. From actual simulation data. |

**Verdict: PASS**

---

## 8a. Sensitivity Matrix (`sensitivity_matrix`)

| Check | Result |
|-------|--------|
| File exists? | YES -- `figs/sensitivity_matrix.png` + `.pdf` |
| Referenced? | **NO** -- not referenced by any \includegraphics in any .tex file |
| In compiled report? | NO (orphan) |
| Visual check | PASS visually -- "Sensitivity Matrix: Input Variables vs Performance Metrics". 5x5 heatmap (altitude, ground speed, scan angle, overlap, NFZ margin) vs (coverage, detection P, mission time, energy, NFZ risk). Each cell has influence value (-1 to +1) and brief annotation. Green = positive, red = negative. Clean and informative. |

**Verdict: PARTIAL** -- Excellent figure but NOT included in any .tex file. Orphan.

---

## 8b. Spider/Radar Chart (`sensitivity_spider`)

| Check | Result |
|-------|--------|
| File exists? | YES -- `figs/sensitivity_spider.png` + `.pdf` |
| Referenced? | **NO** -- not referenced by any \includegraphics in any .tex file |
| In compiled report? | NO (orphan) |
| Visual check | Shows "Selected Configuration Performance (35m, 8 m/s, 70 deg, 20%, 30m margin)". Pentagon radar chart with 5 axes: Detection (0.93), Coverage (0.96), NFZ Safety (1.00), Energy (0.40), Time (0.38). Blue filled = selected config. Grey dashed = theoretical best (visible as outer boundary). Shows actual/best values per axis (e.g., "92%/99%", "112s/60s", "15 Wh/8.2 Wh"). Two overlaid shapes as user requested. |

**Verdict: PARTIAL** -- Excellent figure matching user request (two overlaid shapes), but NOT included in the compiled report. Orphan.

---

## 8c. Dependency Network (`optimization_network`)

| Check | Result |
|-------|--------|
| File exists? | YES -- `figs/optimization_network.png` + `.pdf` |
| Referenced? | YES -- `design_strategy.tex:236` |
| In compiled report? | YES |
| Visual check | PASS -- "Optimisation Variable Dependency Network". Three columns: Decision Variables (blue: altitude, scan angle, ground speed, overlap, NFZ margin), Derived Quantities (white: ground footprint, path length, lane spacing, scan lines, U-turns, target pixels, frames on target, GSD, motion blur, time near NFZ), Performance Metrics (red: coverage, detection probability, mission time, energy use, NFZ risk). Arrows show connections with strong/medium/weak line weights. |

**Verdict: PASS**

---

## 9a. Training Curves (`training_curves`)

| Check | Result |
|-------|--------|
| File exists? | YES -- `figs/training_curves.png` + `.pdf` |
| Referenced? | **NO** -- not referenced by any \includegraphics in any .tex file |
| In compiled report? | NO (orphan) |
| Visual check | Shows "Training Convergence -- YOLOv8n on SAR Dataset v2". Dual y-axis: training loss (orange, left) and mAP50 (blue, right) vs epoch (0-150). Loss drops rapidly in first 20 epochs then plateaus near 0.4. mAP50 rises to ~0.99 by epoch 40 and stays. Best epoch 127 marked. Annotated phases: "Rapid Adaptation", "Refinement", "Plateau". |

**Verdict: PARTIAL** -- Figure exists and looks good, but is NOT included in the compiled report. The `12_model_training.tex` appendix discusses training but has no figure reference.

---

## 9b. Confusion Matrix (`confusion_matrix`)

| Check | Result |
|-------|--------|
| File exists? | YES -- `figs/confusion_matrix.png` + `.pdf` |
| Referenced? | **NO** -- not referenced by any \includegraphics in any .tex file |
| In compiled report? | NO (orphan) |
| Visual check | Shows "YOLOv8n SAR Detector -- Confusion Matrix (Validation Set)". 2x2 matrix: TP=989, FP=6, FN=11, TN=50. Precision=0.994, Recall=0.989, F1=0.991. Green/pink color coding. Clear and correct. |

**Verdict: PARTIAL** -- Figure exists and looks correct, but is NOT included in the compiled report.

---

## 9c. Altitude Detection Heatmap (`detection_heatmap`)

| Check | Result |
|-------|--------|
| File exists? | YES -- `figs/detection_heatmap.png` + `.pdf` |
| Referenced? | YES -- `evaluation.tex:93` |
| In compiled report? | YES |
| Visual check | PASS -- "Detection Heatmap Over Search Area". Shows search area polygon (grey), detection estimates (red dots with confidence colormap), estimated position (green star), true target (red star), CEP50 circle. Take-off point marked. Spatial distribution of detections across the survey area. |

**Verdict: PASS**

Also: `altitude_detection_table.png` exists -- 3-panel horizontal bar chart: target pixel size, detection confidence, and detection rate vs altitude (10-50m). Color-coded by rate quality (green >90%, yellow 70-90%, orange/red <70%). Referenced? Not directly by \includegraphics but may be in a table environment -- checking confirms it is NOT referenced. Orphan.

---

## 10a. Rotation Comparison (`rotation_comparison`)

| Check | Result |
|-------|--------|
| File exists? | YES -- `figs/rotation_comparison.png` + `.pdf` |
| Referenced? | YES -- `search_optimization.tex:89` |
| In compiled report? | YES |
| Visual check | PASS -- "Scan Angle Comparison: Impact on Path Length and Turn Count". Three-panel: 0 deg (N-S, 5 turns, 903m), 20 deg (longest edge, selected, 3 turns, 755m), 90 deg (E-W, 7 turns, 903m). Each panel shows search area (pink), SSSI (orange), flight path (blue), start/end markers. Middle panel highlighted as selected. Clear demonstration of scan angle optimization. |

**Verdict: PASS**

---

## 11a. Photo Placeholders (`figure_descriptions.tex`)

| Check | Result |
|-------|--------|
| File exists? | YES -- `sections/figure_descriptions.tex` |
| Referenced? | YES -- `main.tex:286` (\input) |
| In compiled report? | YES (last appendix) |
| Content check | Contains 5 \fbox{} placeholder descriptions: (1) dashboard-screenshot, (2) hardware-photo, (3) detection-overlay, (4) lawnmower-satellite, (5) bench-setup. Each has a detailed textual description of what the photo should show, plus a proper \caption and \label. |
| Note | These are STILL text placeholders. No actual photographs have replaced them. This is the main gap before submission. |

**Verdict: PARTIAL** -- Placeholder descriptions exist and are well-written, but no actual photographs are included. These need real photos.

---

## Additional Figures (not in user checklist but referenced and present)

These figures exist, are referenced, and compile correctly:

| Figure | File | Referenced in | Status |
|--------|------|--------------|--------|
| `architecture` | .png + .pdf | `system_description.tex:50` | PASS |
| `pi_system` | .png + .pdf | `system_description.tex:57` | PASS |
| `cv_pipeline` | .png + .pdf | `system_description.tex:112` | PASS |
| `mission_timeline` | .png + .pdf | `system_description.tex:259` | PASS |
| `gps_error_direction` | .png + .pdf | `system_description.tex:214` | PASS |
| `estimator_comparison` | .png + .pdf | `system_description.tex:233` | PASS |
| `gps_convergence` | .pdf only | `system_description.tex:226` | PASS |
| `coverage_vs_time` | .pdf only | `system_description.tex:142`, `05_path_planning.tex:55` | PASS |
| `latency_breakdown` | .pdf only | `cv_extended.tex:386`, `evaluation.tex:86` | PASS |
| `speed_detection_energy` | .png + .pdf | `search_optimization.tex:197` | PASS |
| `real_energy_vs_altitude` | .png | `path_optimization_definitive.tex:136` | PASS |
| `real_path_patterns` | .png | `path_optimization_definitive.tex:192` | PASS |
| `real_optimal_pattern` | .png | `path_optimization_definitive.tex:312` | PASS |
| `real_altitude_vs_px` | .png | `vision_performance.tex:88` | PASS |
| `real_speed_vs_blur` | .png | `vision_performance.tex:135` | PASS |
| `real_speed_vs_frames` | .png | `vision_performance.tex:185` | PASS |
| `real_coverage` | .png | `vision_performance.tex:218` | PASS |
| `real_detection_envelope` | .png | `vision_performance.tex:257` | PASS |

---

## Summary

| # | Figure | File Exists? | In Report? | Visual OK? | Verdict |
|---|--------|-------------|-----------|-----------|---------|
| 1a | Confidence vs Altitude | YES (PDF) | YES | (PDF, no visual check) | PASS |
| 1b | Detection Rate vs Speed | YES | YES | YES -- dual FPS curves present | PASS |
| 1c | Motion Blur vs Altitude | YES | YES | YES | PASS |
| 1d | Combined Detection Envelope | YES | YES | YES | PASS |
| 2a | NFZ Geofence (4-panel) | YES | YES | YES -- all 4 panels correct | PASS |
| 2b | NFZ Margin vs Altitude | YES | YES | YES | PASS |
| 3a | State Machine (body, 9 states) | YES | YES | YES | PASS |
| 3a-full | State Machine (full, 20 states) | YES | YES | YES -- all 20 states visible | PASS |
| 4a | Mission Overview on Site Map | YES | YES | YES -- all zones shown | PASS |
| 5a | Bullseye GPS + CEP50 | YES | YES | YES -- CEP50=2.3m, scatter | PASS |
| 6a | Benchmark Comparison | YES | **NO (orphan)** | YES | **PARTIAL** |
| 7a | Energy Efficiency Path | YES | YES | YES | PASS |
| 7a+ | Real Energy Heatmap | YES | YES | YES | PASS |
| 8a | Sensitivity Matrix | YES | **NO (orphan)** | YES | **PARTIAL** |
| 8b | Spider/Radar Chart | YES | **NO (orphan)** | YES -- two shapes overlaid | **PARTIAL** |
| 8c | Dependency Network | YES | YES | YES | PASS |
| 9a | Training Curves | YES | **NO (orphan)** | YES | **PARTIAL** |
| 9b | Confusion Matrix | YES | **NO (orphan)** | YES | **PARTIAL** |
| 9c | Altitude Detection Heatmap | YES | YES | YES | PASS |
| 10a | Rotation Comparison | YES | YES | YES | PASS |
| 11a | Photo Placeholders | YES | YES | N/A -- still text placeholders | **PARTIAL** |

**Totals: 14 PASS, 7 PARTIAL, 0 FAIL**

---

## Action Items

### Critical (orphan figures -- generated but never \includegraphics'd)

1. **`sensitivity_matrix.png`** -- Add to `design_strategy.tex` or `search_optimization.tex`. This is a strong figure showing parameter-metric relationships.
2. **`sensitivity_spider.png`** -- Add to `design_strategy.tex` alongside the optimization network. Shows selected vs theoretical best clearly.
3. **`training_curves.png`** -- Add to `12_model_training.tex`. Section discusses training but has zero figures.
4. **`confusion_matrix.png`** -- Add to `12_model_training.tex`. Same issue.
5. **`benchmark_comparison.png`** -- Either add to `pipeline_fps.tex` or another inference section. The TikZ chart is good but this PNG adds model-level comparison. Consider whether both are needed or just one.
6. **`altitude_detection_table.png`** -- Strong 3-panel altitude vs performance figure. Consider adding to evaluation or cv_extended.

### Important (content gaps)

7. **Photo placeholders (11a)** -- 5 \fbox{} text descriptions need actual photographs before submission. This is the biggest remaining gap.

### Minor

8. **Detection envelope (1d)** -- Currently appendix-only. User wanted it prominent. Add a cross-reference from the body evaluation section.
9. **`conf_vs_alt` has no PNG** -- only PDF exists. Not a problem for LaTeX compilation but means it cannot be visually verified here. Consider generating PNG alongside PDF for consistency.
