# Figure & Table Audit

Generated 2026-03-27. Covers every `\begin{figure}` and `\begin{table}` across the report.

**Report structure reminder:**
- Cover page, Exec Summary, Introduction: EXCLUDED from 15-page limit, NOT formally assessed as body
- Sections 1-4 (design_rationale, system_description, requirements_verification, evaluation): BODY -- ASSESSED
- Everything after `\appendix`: NOT assessed

---

## 1. Figures IN Body (Assessed)

All figures in `system_description.tex`, `evaluation.tex`. The `design_rationale.tex` and `requirements_verification.tex` have NO figures.

| # | Label | File Used | Caption Summary | Section | Quality |
|---|-------|-----------|-----------------|---------|---------|
| 1 | `fig:mission_overview` | `mission_overview.pdf` | Mission plan on Fenswood Farm site with search pattern, zones | System Description 2.0 | GOOD - essential overview |
| 2 | `fig:architecture` | `architecture.pdf` | Module dependency graph | System Description 2.2 | GOOD - shows modularity |
| 3 | `fig:pi_system` | `pi_system.pdf` | Pi 5 hardware interfaces and data flow | System Description 2.2 | GOOD - hardware context |
| 4 | `fig:geofence_diagram` | `geofence_diagram.pdf` | Four-panel geofence protection visualisation | System Description 2.2 | GOOD - critical safety feature |
| 5 | `fig:cv_pipeline` | `cv_pipeline.pdf` | CV pipeline: capture to inference to output | System Description 2.3 | GOOD - core subsystem |
| 6 | `fig:coverage_vs_time` | `coverage_vs_time.pdf` | Area coverage progression over time | System Description 2.4 | GOOD - quantitative |
| 7 | `fig:state_machine` | `state_machine.pdf` | State transition diagram (simplified) | System Description 2.5 | GOOD - essential |
| 8 | `fig:gps_bullseye` | `gps_bullseye.pdf` | GPS estimation error scatter, CEP50=2.3m | System Description 2.6 (subfig a) | GOOD - quantitative |
| 9 | `fig:gps_error_direction` | `gps_error_direction.pdf` | Directional error distribution | System Description 2.6 (subfig b) | GOOD - quantitative |
| 10 | `fig:gps_convergence` | `gps_convergence.pdf` | GPS estimate convergence over observations | System Description 2.6 (subfig c) | GOOD - shows Kalman filter |
| 11 | `fig:estimator_comparison` | `estimator_comparison.pdf` | Comparison of estimation methods | System Description 2.6 (subfig d) | GOOD - method comparison |
| 12 | `fig:mission_timeline` | `mission_timeline.pdf` | Mission timeline with state transitions | System Description 2.7 | GOOD - simulation evidence |
| 13 | `fig:conf_vs_alt` | `conf_vs_alt.pdf` | Detection confidence vs altitude | Evaluation 4.2 (subfig a) | GOOD - key result |
| 14 | `fig:det_vs_speed` | `det_vs_speed.pdf` | Detection rate vs flight speed | Evaluation 4.2 (subfig b) | GOOD - key result |
| 15 | `fig:latency_breakdown` | `latency_breakdown.pdf` | Per-frame latency breakdown | Evaluation 4.2 (subfig c) | GOOD - performance |
| 16 | `fig:detection_heatmap` | `detection_heatmap.pdf` | Spatial detection heatmap | Evaluation 4.2 (subfig d) | GOOD - spatial evidence |

**Body figure count: 16** (including subfigures counted individually: 12 figure environments, 4 subfigure pairs)

---

## 2. Tables IN Body (Assessed)

| # | Label | Caption Summary | Section | Quality |
|---|-------|-----------------|---------|---------|
| 1 | `tab:mcda-companion` | MCDA companion computer selection | Design Rationale 1.2.1 | GOOD - weighted trade study |
| 2 | `tab:mcda-comms` | MCDA communication architecture | Design Rationale 1.2.2 | GOOD - weighted trade study |
| 3 | `tab:mcda-model` | MCDA detection model selection | Design Rationale 1.4 | GOOD - weighted trade study |
| 4 | `tab:mcda-search` | MCDA search pattern selection | Design Rationale 1.5 | GOOD - weighted trade study |
| 5 | `tab:hw-bom` | Bill of materials with costs | System Description 2.1 | GOOD - hardware summary |
| 6 | `tab:mavlink-commands` | MAVLink commands used | System Description 2.2 | OK - useful reference |
| 7 | `tab:req-verification` | Requirements verification summary R01-R12 | Requirements 3.0 | ESSENTIAL - core deliverable |
| 8 | `tab:plus-delta` | Plus/delta review (P1-P9, D1-D9) | Evaluation 4.1 | ESSENTIAL - core deliverable |

**Body table count: 8**

---

## 3. Tables/Figures in Introduction (Excluded from page count, not formally body)

| # | Label | Caption Summary | Section | Notes |
|---|-------|-----------------|---------|-------|
| 1 | `tab:contributions` | Team member contributions | Introduction | Required by brief |

---

## 4. Tables/Figures in Appendices (NOT Assessed)

### Appendix A: State Table
- `tab:state-transitions` -- Full 20-state transition table

### Appendix B: Config Params
- `tab:config-params` -- Configuration parameters

### Appendix C: Model Training (12_model_training.tex)
- `tab:augmentation` -- Data augmentation techniques
- `tab:data_composition` -- Dataset composition
- `tab:training_config` -- Training hyperparameters
- `tab:training_results` -- Training results

### Appendix D: Safety/Risk (13_safety_risk.tex)
- `tab:failure-modes` -- Failure mode analysis
- `tab:risk-register` -- Risk register

### Appendix E: Testing (10_testing.tex)
- `tab:five-tier` -- Five-tier testing framework
- `tab:stress-results` -- Stress test results

### Appendix F: Field Results (11_field_results.tex)
- `tab:benchmark-results` -- Pi 5 benchmark results

### Appendix H: Inference Architecture
- `tab:backend_comparison` -- Inference backend comparison
- `tab:inference_roadmap` -- Inference performance roadmap

### Appendix H2: CV Extended (cv_extended.tex)
- `tab:pipeline_timing` -- Per-stage timing breakdown
- `tab:cv_benchmarks` -- Full inference benchmarks
- `tab:footprint` -- Camera ground footprint at altitudes
- `tab:frames_flyover` -- Frames per flyover detection probability
- `tab:altitude_performance` -- Detection performance vs altitude
- `tab:training_results_extended` -- Training eval metrics
- `tab:model_variants` -- Available model variants
- `fig:conf_vs_alt` (duplicate label!) -- Confidence vs altitude
- `fig:detection_envelope` -- Detection envelope
- `fig:blur_vs_altitude` -- Motion blur vs altitude
- `fig:det_vs_speed` (duplicate label!) -- Detection rate vs speed
- `fig:latency_breakdown` (duplicate label!) -- Latency breakdown

### Appendix I: Streaming Architecture
- `tab:stream-protocols` -- Streaming protocol comparison

### Appendix J: GPS Estimation Deep
- `tab:gsd-altitude` -- GSD at altitude
- `tab:error-budget` -- Error budget
- `tab:method-compare` -- Method comparison

### Appendix K: Testing Deep
- `fig:tier-flow` -- Tier progression diagram
- `tab:test-categories` -- Test script categories
- `tab:bug-cost` -- Bug discovery cost table (referenced from body!)
- `tab:vmodel-map` -- V-model mapping
- `tab:cost-gradient` -- Cost gradient

### Appendix L-Z: Various
- `fig:comms-topology`, `tab:mavlink-messages` (Comms Architecture)
- `tab:mvd`, `tab:target`, `tab:contingency`, `tab:test-scripts` (Contingency)
- `tab:centering-comparison` (Centering Analysis)
- `tab:nfz-layers` (Focus & Repulsive)
- `tab:alt-tradeoff` (Path Tradeoffs)
- `tab:pipeline_fps`, `fig:bottleneck_shift` (Pipeline FPS)
- `tab:model_generations` (Model Comparison)
- `tab:energy-top5`, `tab:rotation-compare`, `tab:nfz-margin`, `tab:speed-detect`, `tab:pareto-summary` (Search Optimization)
- `tab:sim-val-matrix`, `tab:sim-val-results` (Simulation Validation)
- `tab:calibration` (Calibration Deep)
- 6 tables in Test Scripts Guide
- `fig:dashboard-screenshot`, `fig:hardware-photo`, `fig:detection-overlay`, `fig:lawnmower-satellite`, `fig:bench-setup` (Figure Descriptions -- TEXT PLACEHOLDERS, not real images)

---

## 5. HIGH-VALUE Appendix Items That SHOULD Move to Body

These are currently buried in appendices (not assessed) but would significantly strengthen the assessed sections:

| Priority | Current Location | Label | Why It Should Be in Body |
|----------|-----------------|-------|--------------------------|
| **CRITICAL** | Appendix K (testing_deep) | `tab:bug-cost` | Already referenced from body Evaluation P3 and discussion! The body says "Table~\ref{tab:bug-cost}" but the table is in a non-assessed appendix. **The reader sees a cross-ref to content they might not read.** Move it to Evaluation or add a summary version in body. |
| **HIGH** | Appendix E (10_testing) | `tab:five-tier` | The five-tier framework is a key differentiator mentioned in exec summary and evaluation. A compact version belongs in body (System Description or Evaluation). |
| **HIGH** | Appendix H2 (cv_extended) | `tab:footprint` | Ground footprint at altitudes directly supports R05 detection argument. Move to System Description CV section. |
| **HIGH** | Appendix H2 (cv_extended) | `tab:frames_flyover` | Detection probability per flyover is a core result. Move to Requirements Verification R05. |
| **HIGH** | Appendix D (13_safety_risk) | `tab:risk-register` | A top-5 risk summary table in Design Rationale would show engineering maturity. |
| **MEDIUM** | Appendix F (11_field_results) | `tab:benchmark-results` | Pi 5 inference benchmarks are key evidence for P4. A one-line summary exists in body but the table is stronger. |
| **MEDIUM** | Appendix X (search_optimization) | `tab:rotation-compare` | Scan angle optimisation directly supports the path planning rationale. |

---

## 6. DUPLICATE LABELS (Will Cause LaTeX Warnings/Errors)

The following labels appear in BOTH body and appendix files, which will cause LaTeX `multiply defined` warnings and broken cross-references:

| Label | Body File | Appendix File |
|-------|-----------|---------------|
| `fig:conf_vs_alt` | evaluation.tex (line 69) | cv_extended.tex (line 239) |
| `fig:det_vs_speed` | evaluation.tex (line 76) | cv_extended.tex (line 373) |
| `fig:latency_breakdown` | evaluation.tex (line 88) | cv_extended.tex (line 388) |

**Fix:** Rename the appendix versions (e.g., `fig:conf_vs_alt_ext`, `fig:det_vs_speed_ext`, `fig:latency_breakdown_ext`).

---

## 7. Generated Figure PDFs NOT Referenced Anywhere

These PDFs exist in `figs/` but are not included in ANY `.tex` file:

| File | What It Likely Shows | Should It Be Added? |
|------|---------------------|---------------------|
| `energy_efficiency.pdf` | Energy efficiency analysis | MAYBE -- could support path planning evaluation |
| `nfz_margin_altitude.pdf` | NFZ margin vs altitude | YES -- supports R02 (SSSI geofence). Add to body or search_optimization appendix |
| `rotation_comparison.pdf` | Scan angle rotation comparison | YES -- directly supports path planning rationale in body |
| `speed_detection_energy.pdf` | Speed vs detection vs energy trade-off | MAYBE -- Pareto plot, could go in evaluation |
| `state_machine_full.pdf` | Full state machine (20 states) | YES -- use in Appendix A alongside the transition table |
| `state_machine_simple.pdf` | Simplified state machine | MAYBE -- alternative to current `state_machine.pdf` in body |

---

## 8. Figures/Tables That SHOULD Exist But DON'T

For a top-mark MSc report on an autonomous SAR drone, these are conspicuously absent:

### CRITICAL (would significantly improve the body)

| What | Where It Should Go | Why |
|------|-------------------|-----|
| **Hardware photo of assembled drone** | System Description 2.1 | Currently NO photo of the actual platform. The `figure_descriptions.tex` appendix has a TEXT PLACEHOLDER (`fig:hardware-photo`) with a prose description instead of a real image. A single photo of the assembled EDU-450 with Pi, camera, and Cube visible would be worth 100 words of description. |
| **Ground station screenshot** | System Description 2.6 (Ground Station) | Same issue -- `fig:dashboard-screenshot` in appendix is a TEXT PLACEHOLDER, not a real screenshot. The ground station is described in 200+ words but never shown. Take a screenshot of the browser dashboard during simulation. |
| **Detection overlay example** | System Description 2.3 (CV) or Evaluation | `fig:detection-overlay` in appendix is also a TEXT PLACEHOLDER. A single frame showing the bounding box on the dummy from real camera or DJI video would be powerful evidence. |
| **Search pattern on satellite map** | System Description 2.4 or Requirements R05 | `fig:search-pattern` is REFERENCED in requirements_verification.tex R05 (`Figure~\ref{fig:search-pattern}`) but NEVER DEFINED -- this is a broken reference! The `mission_overview.pdf` exists and might cover this, but there is no `fig:search-pattern` label anywhere. |

### HIGH (would add meaningful value)

| What | Where It Should Go | Why |
|------|-------------------|-----|
| **Confusion matrix from training** | Evaluation or System Description CV | The cv_models directory has `confusion_matrix.png` from training. This is standard ML evidence. |
| **Training loss curves** | Evaluation D5 discussion | Shows convergence, helps reader assess overfitting. `results.png` exists in cv_models/. |
| **Lawnmower pattern diagram** | System Description 2.4 | `fig:lawnmower-satellite` in appendix is a TEXT PLACEHOLDER. The `mission_overview.pdf` partially covers this but a clean diagram of the boustrophedon pattern itself (not on the map) would explain the algorithm. |
| **Bench test setup photo** | Evaluation or Field Day section | `fig:bench-setup` in appendix is a TEXT PLACEHOLDER. A photo of the Pi+camera+Cube on the bench would show hardware integration evidence. |
| **Communication topology diagram** | System Description 2.2 | `fig:comms-topology` exists in appendix (comms_architecture.tex) but is NOT in body. A Pi-MAVProxy-Cube-GCS diagram would clarify the architecture. |

### MEDIUM (nice to have)

| What | Where It Should Go | Why |
|------|-------------------|-----|
| **Precision-recall curve** | Evaluation D4 | Acknowledged as missing in D4 delta. Would show threshold trade-off. |
| **FOV calibration photo** | Design Rationale (decisions changed) | Tape measure at 1m showing 92cm visible -- powerful evidence of calibration methodology. |
| **Lens distortion before/after** | System Description CV | Side-by-side showing the checkerboard undistortion. Quantifies the 0.399 RMS. |
| **Battery endurance estimate** | Evaluation or System Description | No power/endurance analysis figure exists. Flight time is critical for SAR. |
| **Wind envelope diagram** | Evaluation D1 | Shows the go/no-go boundary that cancelled the flight. |

---

## 9. Summary Statistics

| Category | Count |
|----------|-------|
| Figures in assessed body | 12 figure environments (16 individual images incl. subfigures) |
| Tables in assessed body | 8 |
| Figures in appendices | ~15 (5 are text placeholders, not real images) |
| Tables in appendices | ~45 |
| Generated PDFs not referenced | 6 |
| Broken cross-references | 1 (`fig:search-pattern` -- referenced but never defined) |
| Duplicate labels | 3 (will cause LaTeX warnings) |
| Text placeholder "figures" | 5 (in figure_descriptions.tex -- describe images but contain no actual images) |

---

## 10. Priority Action Items

1. **FIX BROKEN REF**: `fig:search-pattern` is referenced in requirements_verification.tex R05 but never defined. Either create the figure or remove the reference.
2. **FIX DUPLICATE LABELS**: Rename `fig:conf_vs_alt`, `fig:det_vs_speed`, `fig:latency_breakdown` in cv_extended.tex to avoid multiply-defined warnings.
3. **MOVE `tab:bug-cost` summary to body**: It is already cross-referenced from body text. At minimum, add a compact 3-4 row summary version in Evaluation.
4. **ADD REAL IMAGES**: Replace the 5 text placeholders in figure_descriptions.tex with actual screenshots/photos. The hardware photo and ground station screenshot are the highest priority.
5. **ADD `rotation_comparison.pdf`**: Already generated, directly supports path planning rationale. Include in body Section 2.4.
6. **ADD `state_machine_full.pdf`**: Include in Appendix A alongside the transition table.
7. **ADD `nfz_margin_altitude.pdf`**: Supports R02 SSSI compliance. Include in body or search_optimization appendix.
8. **MOVE compact versions of `tab:five-tier` and `tab:footprint` to body**: These are key evidence tables currently hidden in appendices.
