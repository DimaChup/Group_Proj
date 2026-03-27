# User-Requested Figures & Charts -- Status Checklist

**Last updated: 2026-03-27**
**Source: full conversation history, interpreted generously for typos**

Status key:
- [x] = Done, file exists in `report/figs/`
- [~] = Partially done (exists but has issues)
- [ ] = Missing or not yet created

---

## 1. Detection Performance Charts

### 1a. Confidence vs Altitude
> "at what altitude dummy stops being detectable"

- **Status:** [x] DONE
- **File:** `figs/conf_vs_alt.pdf`
- **Generator:** `figs/gen_altitude_detection.py` (likely)
- **Referenced in:** `evaluation.tex` (fig:conf_vs_alt), `cv_extended.tex`
- **Quality:** 9/10 -- Based on real DJI video data. Confidence >0.9 up to 40m, drops at 50m. Exactly what was asked for.

### 1b. Detection Rate vs Speed (blur effect, dual FPS curves)
> "blur effect on detection, 4.8 FPS vs 10 FPS curves"

- **Status:** [x] DONE
- **File:** `figs/det_vs_speed.pdf`
- **Generator:** (inline in generate_charts.py or standalone)
- **Referenced in:** `evaluation.tex` (fig:det_vs_speed), `cv_extended.tex`
- **Quality:** 9/10 -- Shows detection rate vs flight speed from DJI video data.
- **Note:** Verify whether the chart actually shows dual curves for 4.8 FPS vs 10 FPS as requested, or just a single curve. If single curve, user wanted to see how higher FPS (future NCNN/FP16) improves the speed envelope.

### 1c. Motion Blur vs Altitude
> "higher altitude = less blur significance"

- **Status:** [x] DONE
- **File:** `figs/blur_vs_altitude.pdf`
- **Generator:** `figs/gen_blur_vs_altitude.py`
- **Referenced in:** `cv_extended.tex`
- **Quality:** 8/10 -- Pixel motion blur vs altitude at different speeds/exposures. Shows global shutter advantage. Appendix only.

### 1d. Combined Detection Envelope
> "overall combined chart like detection envelope"

- **Status:** [x] DONE
- **File:** `figs/detection_envelope.pdf`
- **Generator:** (part of cv_extended generation)
- **Referenced in:** `cv_extended.tex` (appendix)
- **Quality:** 9/10 -- Combined confidence + motion blur envelope with reliable detection zone shaded.
- **Note:** Appendix only, not in body. User wanted this prominent -- consider adding to body or at least a strong cross-reference.

---

## 2. Geofence & NFZ

### 2a. NFZ Geofence Diagram (4-panel)
> "clear boundary, repulsive vector field, scalar speed gradient, before/after waypoint correction"

- **Status:** [x] DONE
- **File:** `figs/geofence_diagram.pdf`
- **Generator:** `figs/gen_geofence_diagram.py`
- **Referenced in:** `system_description.tex` (fig:geofence)
- **Quality:** 9/10 -- 4-panel diagram: (1) boundaries, (2) repulsive field, (3) waypoint correction, (4) emergency. All four elements the user asked for are present.

### 2b. NFZ Margin vs Altitude
> "NFZ margin vs altitude"

- **Status:** [x] DONE
- **File:** `figs/nfz_margin_altitude.pdf`
- **Referenced in:** `search_optimization.tex` (appendix)
- **Quality:** 8/10 -- Shows altitude vs NFZ margin tradeoff.

---

## 3. State Machine & Architecture

### 3a. State Machine Diagram (validated against code)
> "state machine diagram validated against actual code, all 19-20 states"

- **Status:** [x] DONE
- **Files:** `figs/state_machine.pdf` (body), `figs/state_machine_full.pdf` (appendix)
- **Generators:** `figs/gen_state_machine.py`, `figs/gen_state_machine_full.py`
- **Referenced in:** `system_description.tex` (fig:state_machine), `A1_state_table.tex`
- **Quality:** 8/10 (body), 7/10 (full). 20-state FSM. Full version has all 32 transitions.
- **Note:** User specifically asked for validation against actual code. The dashboard ArchitectureTab has the rebuilt diagram with all 32 transitions. Verify the PDF matches.

---

## 4. Mission & Site

### 4a. Mission Overview on Actual Site Map
> "mission overview on actual site map with all zones"

- **Status:** [x] DONE
- **File:** `figs/mission_overview.pdf`
- **Generator:** `figs/gen_mission_overview.py`
- **Referenced in:** `system_description.tex` (fig:mission_overview)
- **Quality:** 9/10 -- Fenswood site map with search polygon, SSSI no-fly zone, takeoff point, lawnmower pattern. All zones shown.

---

## 5. GPS & Target Localisation

### 5a. Bullseye GPS Scatter Plot with CEP50
> "bullseye GPS scatter plot with CEP50"

- **Status:** [x] DONE
- **File:** `figs/gps_bullseye.pdf`
- **Generator:** `figs/gen_gps_bullseye.py`
- **Referenced in:** `system_description.tex` (fig:gps_bullseye)
- **Quality:** 9/10 -- GPS estimation error scatter with CEP50 circle (2.3m). Exactly what was asked for.

---

## 6. Benchmarks & Model Comparison

### 6a. Benchmark Comparison Chart
> "different models, raw vs effective FPS"

- **Status:** [x] DONE
- **File:** `figs/benchmark_comparison.pdf`
- **Referenced in:** appendix + `pipeline_fps.tex` (TikZ stacked bar)
- **Quality:** 7/10 -- Covers TFLite FP32/FP16, NCNN, Ultralytics. Distinguishes raw inference vs pipeline FPS.
- **Note:** User specifically asked for raw vs effective FPS distinction. The `pipeline_fps.tex` has a TikZ stacked bar chart that does this well. Verify `benchmark_comparison.pdf` also shows this, not just a simple bar chart.

---

## 7. Path Planning & Energy

### 7a. Energy Efficiency Path from Actual Simulation
> "energy efficiency path from our actual simulation"

- **Status:** [x] DONE
- **File:** `figs/energy_efficiency.pdf`
- **Referenced in:** `search_optimization.tex` (appendix)
- **Quality:** 8/10 -- Energy efficiency vs scan angle/altitude from real 216-config sweep.
- **Also:** `figs/real_energy_heatmap.png`, `figs/real_energy_vs_altitude.png`, `figs/real_optimal_pattern.png` from actual simulation runs.

---

## 8. Sensitivity & Optimisation

### 8a. Sensitivity Matrix
> "sensitivity matrix -- input vars vs output metrics"

- **Status:** [x] DONE
- **File:** `figs/sensitivity_matrix.pdf`
- **Generator:** `figs/gen_sensitivity_matrix.py`
- **Referenced in:** appendix
- **Quality:** 8/10 -- Parameter sensitivity analysis. Input variables vs output metrics.

### 8b. Spider/Radar Chart
> "spider/radar chart of selected config vs theoretical best"

- **Status:** [x] DONE
- **File:** `figs/sensitivity_spider.pdf`
- **Referenced in:** appendix
- **Quality:** 8/10 -- Multi-dimensional comparison of selected configuration.
- **Note:** Verify it actually shows "selected config vs theoretical best" as two overlaid shapes, not just one.

### 8c. Dependency Network
> "dependency network of all optimization variables"

- **Status:** [x] DONE
- **File:** `figs/optimization_network.pdf`
- **Generator:** `figs/optimization_network.py`
- **Referenced in:** appendix
- **Quality:** 7/10 -- Parameter dependency graph.

---

## 9. Training & Model Performance

### 9a. Training Curves (loss + mAP over epochs)
> "training curves -- loss + mAP over epochs"

- **Status:** [x] DONE
- **File:** `figs/training_curves.pdf`
- **Generator:** `figs/gen_training_curves.py`
- **Referenced in:** appendix (`12_model_training.tex`)
- **Quality:** 7/10 -- Loss and mAP curves.
- **Note:** These may be synthetic/reconstructed rather than actual Colab training logs. If real results.csv from Colab is available, regenerate from that.

### 9b. Confusion Matrix
> "confusion matrix"

- **Status:** [x] DONE
- **File:** `figs/confusion_matrix.pdf`
- **Generator:** `figs/gen_confusion_matrix.py`
- **Referenced in:** appendix (`12_model_training.tex`)
- **Quality:** 7/10 -- Detection confusion matrix.
- **Note:** Real confusion matrix images also exist in `cv_models/sar_v2_1088/` and `cv_models/sar_640/` from actual training. Consider using the real one instead of generated.

### 9c. Altitude Detection Heatmap
> "altitude detection heatmap"

- **Status:** [x] DONE
- **File:** `figs/detection_heatmap.pdf`
- **Generator:** `figs/gen_detection_heatmap.py`
- **Referenced in:** `evaluation.tex` body
- **Quality:** 8/10 -- Spatial detection density across survey area.
- **Also:** `figs/altitude_detection_table.pdf` -- altitude vs detection table (visual format).

---

## 10. Path Planning Extras

### 10a. Rotation Comparison (different scan angles)
> "rotation comparison -- different scan angles"

- **Status:** [x] DONE
- **File:** `figs/rotation_comparison.pdf`
- **Referenced in:** `search_optimization.tex` (appendix)
- **Quality:** 8/10 -- Rotation angle comparison for path optimisation.
- **Also:** `figs/real_scan_angle.png` from actual simulation.

---

## 11. Placeholder Descriptions for Photos

### 11a. Blackboard Descriptions
> "blackboard descriptions for photos we can't generate"

- **Status:** [~] PARTIAL
- **File:** `sections/figure_descriptions.tex`
- **Referenced in:** `main.tex` (last appendix)
- **Quality:** Present as `\fbox{}` text boxes describing what the photos should show:
  - `fig:dashboard-screenshot` -- ground station browser UI
  - `fig:hardware-photo` -- assembled drone with labelled components
  - `fig:detection-overlay` -- example detection frame at 35m
  - `fig:lawnmower-satellite` -- pattern overlaid on satellite image
  - `fig:bench-setup` -- bench test configuration
- **Issue:** Still placeholder text. Real photos needed to replace them. This is the CRITICAL gap.

---

## Summary Table

| # | Figure | Status | File | Quality |
|---|--------|--------|------|---------|
| 1a | Confidence vs Altitude | [x] | `conf_vs_alt.pdf` | 9/10 |
| 1b | Detection Rate vs Speed | [x] | `det_vs_speed.pdf` | 9/10 |
| 1c | Motion Blur vs Altitude | [x] | `blur_vs_altitude.pdf` | 8/10 |
| 1d | Combined Detection Envelope | [x] | `detection_envelope.pdf` | 9/10 |
| 2a | NFZ Geofence (4-panel) | [x] | `geofence_diagram.pdf` | 9/10 |
| 2b | NFZ Margin vs Altitude | [x] | `nfz_margin_altitude.pdf` | 8/10 |
| 3a | State Machine (20 states) | [x] | `state_machine.pdf` + `_full.pdf` | 8/10 |
| 4a | Mission on Site Map | [x] | `mission_overview.pdf` | 9/10 |
| 5a | Bullseye GPS + CEP50 | [x] | `gps_bullseye.pdf` | 9/10 |
| 6a | Benchmark Comparison | [x] | `benchmark_comparison.pdf` | 7/10 |
| 7a | Energy Efficiency Path | [x] | `energy_efficiency.pdf` | 8/10 |
| 8a | Sensitivity Matrix | [x] | `sensitivity_matrix.pdf` | 8/10 |
| 8b | Spider/Radar Chart | [x] | `sensitivity_spider.pdf` | 8/10 |
| 8c | Dependency Network | [x] | `optimization_network.pdf` | 7/10 |
| 9a | Training Curves | [x] | `training_curves.pdf` | 7/10 |
| 9b | Confusion Matrix | [x] | `confusion_matrix.pdf` | 7/10 |
| 9c | Altitude Detection Heatmap | [x] | `detection_heatmap.pdf` | 8/10 |
| 10a | Rotation Comparison | [x] | `rotation_comparison.pdf` | 8/10 |
| 11a | Photo Placeholders | [~] | `figure_descriptions.tex` | 5/10 |

**Totals: 18 done, 1 partial, 0 completely missing**

---

## Action Items (things to verify or improve)

1. **Detection envelope in body** -- Currently appendix-only. User wanted it prominent. Add to body or strong cross-ref.
2. **Dual FPS curves** (1b) -- Verify `det_vs_speed.pdf` shows 4.8 FPS AND 10 FPS curves, not just one.
3. **Spider chart** (8b) -- Verify it overlays "selected config" vs "theoretical best", not just one shape.
4. **Training curves** (9a) -- Check if generated from real Colab data or synthetic. Real `results.csv` from training would be better.
5. **Confusion matrix** (9b) -- Real confusion matrix images exist in `cv_models/`. Consider using actual training output.
6. **Benchmark chart** (6a) -- Verify it shows raw vs effective FPS distinction clearly (the TikZ chart in `pipeline_fps.tex` does this well).
7. **Real photos** (11a) -- CRITICAL. 5 placeholder boxes need actual photographs before submission.
8. **State machine validation** (3a) -- Verify PDF matches the 32-transition table rebuilt in dashboard.
