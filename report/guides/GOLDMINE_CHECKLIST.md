# D6 Report Goldmine Checklist

**Master tracking document. Updated: 2026-03-27 (v2 -- exhaustive audit).**
**Current estimated score: ~81 (range 79-84). Target: 83+.**
**Overall completeness: ~85%.**

Page budget: 15 pages counted (Design Rationale + System Description + Requirements Verification + Evaluation).
Excluded from count: Cover, Exec Summary, Introduction, References, Appendices.

---

## Completion Dashboard

| Area | Done | Total | % |
|------|------|-------|---|
| Body sections included in main.tex | 4 | 4 | 100% |
| Figures in body (PDF) | 15 | 15 | 100% |
| Figures -- real photos (hardware, dashboard, field) | 0 | 4 needed | 0% |
| Tables in body | 9 | 9 | 100% |
| Appendices included in main.tex | 19 | 19 | 100% |
| Orphaned sections (exist, not in main.tex) | 13 | 13 | -- |
| New sections written but not yet included | 3 | 3 | 0% |
| Must-fix issues | 3 done | 11 total | 27% |
| High-priority content ideas implemented | 3 | 8 | 38% |
| Medium-priority content ideas implemented | 2 | 8 | 25% |

---

## Section Files -- Complete Inventory

### Body Sections (counted toward 15-page limit, included in main.tex)

| # | Status | File | Title | Lines | In main.tex? | Quality | Notes |
|---|--------|------|-------|-------|-------------|---------|-------|
| 1 | [x] | `design_rationale.tex` | Design Rationale | 235 | YES | Good | 5 MCDA tables, STEEPLE (7 dimensions, all substantive). No MCDA "authenticity" sentence yet. |
| 2 | [x] | `system_description.tex` | System Description | 240 | YES | Good | 11 figures, dense. Ground station EXPANDED to ~10 lines (was 3). Simulation section now 4 levels. |
| 3 | [x] | `requirements_verification.tex` | Requirements Verification | 123 | YES | Needs improvement | R06 thin (no quantitative evidence, no figure). R07 no visual. R11 very brief. |
| 4 | [x] | `evaluation.tex` | Evaluation | 142 | YES | IMPROVED | Plus/delta table (9+/9-). "Lessons Learned" subsection added (4 items). "Weather as adaptation" paragraph added. Bug-cost table cross-referenced (Table~\ref{tab:bug-cost}). Discussion paragraphs cover architecture, detection, GPS, testing, weather, incomplete validation. Summary paragraph present. |

### Excluded Sections (not counted toward page limit, included in main.tex)

| # | Status | File | Title | Lines | In main.tex? | Quality | Notes |
|---|--------|------|-------|-------|-------------|---------|-------|
| 5 | [x] | `exec_summary.tex` | Executive Summary | 18 | YES | Needs improvement | Doesn't mention field day pivot. Claims "14 figures" and "18 waypoints" -- verify. |
| 6 | [x] | `intro_d6.tex` | Introduction | 79 | YES | Good | Team bios, contribution table. |

### Appendices (excluded from page limit, included in main.tex, NOT assessed)

| # | Status | File | Appendix Letter | Lines | Quality | Key content to pull into body? |
|---|--------|------|----------------|-------|---------|-------------------------------|
| A | [x] | `A1_state_table.tex` | A | 235 | Good | No -- too large |
| B | [x] | `A2_config_params.tex` | B | 77 | Good | No |
| C | [x] | `12_model_training.tex` | C | 208 | Good | Training results table (v1 vs v2) -- shows iterative improvement |
| D | [x] | `13_safety_risk.tex` | D | 110 | Good | Top 3-5 risk items condensed in Design Rationale |
| E | [x] | `10_testing.tex` | E | 134 | Good | Five-tier table (tab:five-tier) -- GOLD for body |
| F | [x] | `11_field_results.tex` | F | 105 | Good | Benchmark numbers already in body |
| G | [x] | `14_future_work.tex` | G | 50 | Good | 1-paragraph summary in Evaluation |
| H | [x] | `inference_architecture.tex` | H | 120 | Good | No |
| H2 | [x] | `cv_extended.tex` | H2 | 394 | Excellent | detection_envelope figure, altitude_performance table |
| I | [x] | `streaming_architecture.tex` | I | 259 | Over-engineered | 2+ pages justifying MJPEG is overkill |
| J | [x] | `gps_estimation_deep.tex` | J | 303 | Excellent | Error budget table (6 sources) -- should be in body |
| K | [x] | `testing_deep.tex` | K | 227 | Excellent | bug-cost table, cost-gradient table -- cross-referenced from body |
| L | [x] | `field_day_narrative.tex` | L | 116 | Good | FOV discovery story -- already in Evaluation as "adaptation evidence" |
| M | [x] | `contingency.tex` | M | 115 | Good | MVD/Target/Stretch tiers -- 1 paragraph in Design Rationale |
| N | [x] | `test_scripts_guide.tex` | N | 226 | Good | script-req-map table shows traceability |
| O | [x] | `calibration_deep.tex` | O | 115 | Good | calibration summary table (error if uncalibrated) |
| P | [x] | `simulation_validation.tex` | P | 118 | Good | No |
| Q | [x] | `mission_flow.tex` | Q | 124 | Good | No |
| R1 | [x] | `centering_analysis.tex` | R (first) | 70 | Good | No |
| S | [x] | `comms_architecture.tex` | S | 101 | Good | No |
| R2 | [x] | `figure_descriptions.tex` | R (DUPLICATE letter) | 216 | Placeholder only | These should become real images |

### NEW Sections Written But NOT in main.tex

These are fully written, high-quality sections that exist as files but are not `\input{}` anywhere.

| # | Status | File | Title | Lines | Quality | Action Needed |
|---|--------|------|-------|-------|---------|---------------|
| N1 | [!] | `path_tradeoffs.tex` | Flight Path Optimisation | 82 | Excellent | 7 subsections: diagonal vs axis-aligned, lane width vs altitude, speed schedule, turn strategy, overlap margin, start corner, PLB redirect. Has `tab:alt-tradeoff` table. Should be subsection of System Description or standalone appendix. |
| N2 | [!] | `pipeline_fps.tex` | Raw Inference vs Effective Pipeline FPS | 95 | Excellent | Has `tab:pipeline_fps` table + TikZ `fig:bottleneck_shift` stacked bar chart (inline, not PDF). Covers TFLite FP32/FP16, NCNN, Ultralytics. Should be appendix or subsection of CV in body. |
| N3 | [!] | `alternatives.tex` | Alternative Paragraph Options | 78 | Reference only | 5 sets of alternative paragraphs (A/B/C versions) for: STEEPLE opening, weather adaptation, autonomy level, evaluation opening, conclusion/summary. Not for inclusion -- pick best version and swap into body sections. |

### Orphaned Sections (exist but NOT included in main.tex)

These were written as standalone sections before the report was restructured. Content may be reusable.

| # | File | Title | Lines | In main.tex? | Reusable content? |
|---|------|-------|-------|-------------|-------------------|
| 1 | `05_path_planning.tex` | Path Planning (full section) | 181 | NO | YES -- comprehensive: rotated-mask algorithm, lane width equations, scan angle sweep (216 configs), energy analysis, Bezier smoothing, spiral alternative, CPP comparison table (tab:cpp-comparison), coverage_vs_time figure, flight params table (tab:flight-params). MUCH richer than body coverage. Should be appendix + pull key content into body. |
| 2 | `steeple.tex` | STEEPLE Analysis | 44 | NO | Superseded -- design_rationale.tex has full inline STEEPLE (lines 8-33). |
| 3 | `00_abstract.tex` | Abstract | 5 | NO | Superseded by exec_summary. |
| 4 | `01_introduction.tex` | Introduction (old) | 92 | NO | Superseded by intro_d6. |
| 5 | `02_system_architecture.tex` | System Architecture (old) | 164 | NO | Superseded by system_description. |
| 6 | `03_hardware_platform.tex` | Hardware Platform (old) | 150 | NO | Content in system_description. |
| 7 | `04_computer_vision.tex` | Computer Vision (old) | 126 | NO | Content in system_description + cv_extended. |
| 8 | `06_state_machine.tex` | State Machine (old) | 203 | NO | Rich content: 20 states described, operator interface, timeout logic, geofence integration, Sheridan levels. Some content in system_description but this has MORE detail. |
| 9 | `07_target_localisation.tex` | Target Localisation (old) | 135 | NO | Content in system_description + gps_estimation_deep. |
| 10 | `08_ground_station.tex` | Ground Station (old) | 57 | NO | Superseded -- system_description now has expanded ground station subsection (~10 lines). |
| 11 | `09_simulation.tex` | Simulation (old) | 140 | NO | Partially superseded. Has more detail than system_description's 4-line simulation section. |
| 12 | `15_conclusion.tex` | Conclusion | 21 | NO | Brief says no conclusion section required. Could repurpose as stronger summary in Evaluation. |
| 13 | `introduction.tex` | Another introduction variant | 54 | NO | Superseded. |

---

## Figures (Charts, Diagrams, Photos)

### Currently in Body Sections (PDF files referenced)

| # | Status | File | Description | Section | Referenced? | Quality |
|---|--------|------|-------------|---------|------------|---------|
| 1 | [x] | `mission_overview.pdf` | Fenswood site map with search polygon, SSSI, takeoff, lawnmower | System Description | YES (fig:mission_overview) | Good |
| 2 | [x] | `architecture.pdf` | Module dependency graph (config, vision, planning, main, utils) | System Description | YES (fig:architecture) | Good |
| 3 | [x] | `pi_system.pdf` | Pi 5 hardware interfaces and data flow diagram | System Description | YES (fig:pi_system) | Good |
| 4 | [x] | `geofence_diagram.pdf` | 4-panel geofence: boundaries, repulsive field, waypoint correction, emergency | System Description | YES (fig:geofence) | Good |
| 5 | [x] | `cv_pipeline.pdf` | CV pipeline: capture -> undistort -> resize -> inference -> filter -> rescale | System Description | YES (fig:cv_pipeline) | Good |
| 6 | [x] | `state_machine.pdf` | 20-state FSM transition diagram | System Description | YES (fig:state_machine) | Good |
| 7 | [x] | `gps_bullseye.pdf` | GPS estimation error scatter with CEP50 circle | System Description | YES (fig:gps_bullseye) | Good |
| 8 | [x] | `gps_error_direction.pdf` | Directional error distribution showing heading-aligned elongation | System Description | YES (fig:gps_error_direction) | Good |
| 9 | [x] | `gps_convergence.pdf` | GPS estimate convergence over successive observations | System Description | YES (fig:gps_convergence) | Good |
| 10 | [x] | `estimator_comparison.pdf` | Comparison: raw avg, inverse-variance, Kalman filter | System Description | YES (fig:estimator_comparison) | Good |
| 11 | [x] | `mission_timeline.pdf` | Mission timeline with state transitions (coloured blocks) | System Description | YES (fig:mission_timeline) | Good |
| 12 | [x] | `conf_vs_alt.pdf` | Detection confidence vs altitude plot | Evaluation | YES (fig:conf_vs_alt) | Good |
| 13 | [x] | `det_vs_speed.pdf` | Detection rate vs flight speed | Evaluation | YES (fig:det_vs_speed) | Good |
| 14 | [x] | `latency_breakdown.pdf` | Per-frame latency breakdown (capture, undistort, resize, inference, post) | Evaluation | YES (fig:latency_breakdown) | Good |
| 15 | [x] | `detection_heatmap.pdf` | Spatial detection density across survey area | Evaluation | YES (fig:detection_heatmap) | Good |

### Additional PDF Figures That Exist (not referenced in body)

| # | Status | File | Description | Where used | Quality |
|---|--------|------|-------------|-----------|---------|
| 16 | [x] | `state_machine_full.pdf` | Full state machine (alternative version) | Not referenced | Good |
| 17 | [x] | `state_machine_simple.pdf` | Simplified state machine (alternative version) | Not referenced | Good |

### In Appendices Only (not in body)

| # | Status | File | Description | Appendix | Quality | Should move to body? |
|---|--------|------|-------------|----------|---------|---------------------|
| 18 | [x] | `detection_envelope.pdf` | Combined confidence + motion blur envelope with reliable detection zone | cv_extended | Good | YES -- strong evidence for Evaluation |
| 19 | [x] | `blur_vs_altitude.pdf` | Pixel motion blur vs altitude at different speeds/exposures | cv_extended | Good | Consider -- supports IMX296 global shutter argument |
| 20 | [x] | `coverage_vs_time.pdf` | Coverage % vs time for different scan angles | 05_path_planning (ORPHANED) | Good | YES -- path planning not in body at all |

### Inline TikZ Figures (generated by LaTeX, no PDF file)

| # | Status | Label | Description | File | Notes |
|---|--------|-------|-------------|------|-------|
| 21 | [!] | `fig:bottleneck_shift` | Stacked bar: inference vs pipeline overhead per backend | `pipeline_fps.tex` | NOT in main.tex yet. Requires pgfplots package. |

### Figures That Exist as Placeholder Text Only (no real image)

These are in `figure_descriptions.tex` as detailed text descriptions inside `\fbox{}` boxes. They need actual photos/screenshots.

| # | Status | Label | Description | Impact if added |
|---|--------|-------|-------------|-----------------|
| 22 | [ ] | `fig:dashboard-screenshot` | Ground station browser UI with MJPEG stream + GPS grid + command buttons | CRITICAL -- +2 Communication |
| 23 | [ ] | `fig:hardware-photo` | Assembled drone with labelled components (Pi, Cube, camera, GPS, battery) | CRITICAL -- +2-3 Communication |
| 24 | [ ] | `fig:detection-overlay` | Example detection frame at 35m with bounding box, confidence, scale bar | HIGH -- +1-2 Specialist Skills |
| 25 | [ ] | `fig:lawnmower-satellite` | Lawnmower pattern overlaid on real satellite image with SSSI + takeoff | MEDIUM -- mission_overview.pdf partially covers this |
| 26 | [ ] | `fig:bench-setup` | Bench test configuration: Pi + camera + Cube + laptop + PuTTY | MEDIUM -- shows real engineering setup |

### Figures We Could Create But Don't Have

| # | Status | Idea | Where it would go | Impact |
|---|--------|------|-------------------|--------|
| 27 | [ ] | Detection montage: 4-6 frames at different altitudes (15m, 25m, 35m, 45m) with bounding boxes | Requirements Verification R05/R10 | HIGH -- directly evidences detection capability |
| 28 | [ ] | R06 PLB redirect: before/after showing pattern shift when focus area received | Requirements Verification R06 | MEDIUM -- R06 verification is thin |
| 29 | [ ] | Landing position probability distribution (histogram or scatter) for R07 | Requirements Verification R07 | MEDIUM -- mathematical argument needs visual backup |
| 30 | [ ] | Confusion matrix from training (already exists in cv_models/) | Model Training appendix or Evaluation | LOW -- already described in text |
| 31 | [ ] | Training loss curves (already exists in cv_models/) | Model Training appendix | LOW |
| 32 | [ ] | Screenshot of Mission Planner showing SITL connection | System Description or Introduction | LOW |
| 33 | [ ] | Photo of the rescue dummy on the field | Introduction or System Description | MEDIUM -- context for what we're detecting |
| 34 | [ ] | Comparison: Pi camera frame vs DJI camera frame at same altitude | Evaluation or Calibration appendix | LOW |
| 35 | [ ] | Energy/battery consumption estimate diagram | Path Planning or Design Rationale | LOW |
| 36 | [ ] | Wiring schematic (Pi GPIO to Cube TELEM2 pinout) | System Description or Hardware appendix | LOW |
| 37 | [ ] | Field day photo(s): team at Fenswood, equipment setup outdoors | Introduction or Field Day appendix | MEDIUM -- engagement and credibility |
| 38 | [ ] | Model training progression visualization (640->1280->1088 with metrics) | Evaluation | MEDIUM -- shows iterative improvement |

---

## Tables

### Currently in Body Sections

| # | Status | Label | Description | Section | Quality |
|---|--------|-------|-------------|---------|---------|
| 1 | [x] | `tab:contributions` | Team member contributions by project area | Introduction | Good |
| 2 | [x] | `tab:mcda-companion` | MCDA: companion computer selection (Pi 5 vs Jetson vs etc.) | Design Rationale | Good |
| 3 | [x] | `tab:mcda-comms` | MCDA: communication architecture | Design Rationale | Good |
| 4 | [x] | `tab:mcda-model` | MCDA: detection model selection (YOLOv8n vs 8s vs etc.) | Design Rationale | Good |
| 5 | [x] | `tab:mcda-search` | MCDA: search pattern selection | Design Rationale | Good |
| 6 | [x] | `tab:hw-bom` | Hardware bill of materials with costs | System Description | Good |
| 7 | [x] | `tab:mavlink-commands` | MAVLink commands used by navigation module | System Description | Good |
| 8 | [x] | `tab:req-verification` | Requirements verification summary (R01-R12 status) | Requirements Verification | Good |
| 9 | [x] | `tab:plus-delta` | Plus/delta review of technical performance (9+/9-) | Evaluation | Good |

### Tables in NEW Sections (not yet in main.tex)

| # | Status | Label | Description | File | Quality | Action |
|---|--------|-------|-------------|------|---------|--------|
| 10 | [!] | `tab:alt-tradeoff` | Altitude-lane width-detection trade-off (4 altitudes) | path_tradeoffs.tex | Excellent | Include file to activate |
| 11 | [!] | `tab:pipeline_fps` | Raw vs effective FPS per backend (4 backends) | pipeline_fps.tex | Excellent | Include file to activate |

### Tables in ORPHANED Sections (not in main.tex)

| # | Status | Label | Description | File | Quality | Action |
|---|--------|-------|-------------|------|---------|--------|
| 12 | [!] | `tab:cpp-comparison` | Coverage path planning algorithm comparison (5 algorithms) | 05_path_planning.tex | Good | Add as appendix to activate |
| 13 | [!] | `tab:flight-params` | Search flight parameters (8 params with rationale) | 05_path_planning.tex | Good | Add as appendix to activate |

### Tables in Appendices (NOT assessed)

| # | Status | Label | Description | Appendix | Move to body? |
|---|--------|-------|-------------|----------|---------------|
| 14 | [x] | `tab:steeple` | STEEPLE analysis summary (7 dimensions) | steeple.tex (ORPHANED) | Superseded by inline STEEPLE in design_rationale |
| 15 | [x] | `tab:state-transitions` | Full 20-state, 32-transition table | A1_state_table | No -- too large |
| 16 | [x] | `tab:config-params` | All configuration parameters | A2_config_params | No -- reference material |
| 17 | [x] | `tab:augmentation` | Data augmentation pipeline (offline + online) | 12_model_training | No -- detail level |
| 18 | [x] | `tab:data_composition` | Dataset composition (300 syn + 16 real + 50 neg) | 12_model_training | Consider 1-line summary in body |
| 19 | [x] | `tab:training_config` | Training hyperparameters | 12_model_training | No |
| 20 | [x] | `tab:training_results` | Detection performance: v1 vs v2 model comparison | 12_model_training + cv_extended | YES -- shows iterative improvement |
| 21 | [x] | `tab:failure-modes` | Failure modes and automated responses | 13_safety_risk | Consider condensed version in Design Rationale |
| 22 | [x] | `tab:risk-register` | Risk register with mitigations | 13_safety_risk | Consider top 3-5 in body |
| 23 | [x] | `tab:five-tier` | Five-tier progressive testing framework | 10_testing | YES -- key evidence for methodology |
| 24 | [x] | `tab:stress-results` | 20 stress test scenarios in SITL | 10_testing | Consider top 5 in Evaluation |
| 25 | [x] | `tab:benchmark-results` | Pi 5 inference benchmark results | 11_field_results | Already summarised in body |
| 26 | [x] | `tab:backend_comparison` | Inference backend comparison (TFLite vs ONNX vs NCNN) | inference_architecture | No |
| 27 | [x] | `tab:inference_roadmap` | Inference improvement roadmap (baseline + projected) | inference_architecture | No |
| 28 | [x] | `tab:pipeline_timing` | Per-stage timing breakdown (50 runs) | cv_extended | No -- latency_breakdown figure covers this |
| 29 | [x] | `tab:cv_benchmarks` | Full inference benchmarks on Pi 5 | cv_extended | No |
| 30 | [x] | `tab:footprint` | Camera footprint at different altitudes | cv_extended | Consider -- useful for understanding coverage |
| 31 | [x] | `tab:frames_flyover` | Frames per flyover and detection probability | cv_extended | No -- detail level |
| 32 | [x] | `tab:altitude_performance` | Detection performance vs altitude table | cv_extended | YES -- directly supports R05 |
| 33 | [x] | `tab:model_variants` | Available model variants for field deployment | cv_extended | No |
| 34 | [x] | `tab:stream-protocols` | Video streaming protocol comparison (MJPEG vs HLS vs WebRTC) | streaming_architecture | No |
| 35 | [x] | `tab:gsd-altitude` | GSD and footprint at key altitudes | gps_estimation_deep | No |
| 36 | [x] | `tab:error-budget` | Single-observation GPS error budget (6 sources) | gps_estimation_deep | YES -- strong quantitative evidence |
| 37 | [x] | `tab:method-compare` | GPS estimation method comparison (4 methods) | gps_estimation_deep | Already shown via figure |
| 38 | [x] | `tab:bug-cost` | Defect discovery table (tier, fix time, escalation cost) | testing_deep | CROSS-REFERENCED from body (P3 in evaluation.tex) |
| 39 | [x] | `tab:test-categories` | Test script categories and tier coverage | testing_deep | No |
| 40 | [x] | `tab:vmodel-map` | V-model to 5-tier framework mapping | testing_deep | Consider -- shows SE rigour |
| 41 | [x] | `tab:cost-gradient` | Cost and risk gradient across tiers (50:1 ratio) | testing_deep | YES -- powerful evidence |
| 42 | [x] | `tab:mvd` | Minimum viable deliverable components | contingency | Consider 1-paragraph summary in Design Rationale |
| 43 | [x] | `tab:target` | Target deliverable components | contingency | Consider 1-paragraph summary |
| 44 | [x] | `tab:contingency` | Contingency plans for flight day failures | contingency | No |
| 45 | [x] | `tab:test-scripts` | Contingency-to-test-script mapping | contingency | No |
| 46 | [x] | `tab:flight-scripts` | Flight test progression scripts | test_scripts_guide | No |
| 47 | [x] | `tab:hw-tests` | Hardware test scripts | test_scripts_guide | No |
| 48 | [x] | `tab:cal-tests` | Calibration test scripts | test_scripts_guide | No |
| 49 | [x] | `tab:experiment-scripts` | Day 1 experiment scripts | test_scripts_guide | No |
| 50 | [x] | `tab:script-req-map` | Test scripts mapped to requirements | test_scripts_guide | Consider -- shows traceability |
| 51 | [x] | `tab:test-gaps` | Tests not yet completed on real hardware | test_scripts_guide | No |
| 52 | [x] | `tab:calibration` | Sensor calibration summary with "error if uncalibrated" | calibration_deep | YES -- shows initiative |
| 53 | [x] | `tab:sim-val-matrix` | Simulation validation coverage matrix | simulation_validation | No |
| 54 | [x] | `tab:sim-val-results` | Quantitative simulation validation results | simulation_validation | Consider |
| 55 | [x] | `tab:centering-comparison` | Centering vs direct offset: 20 simulated missions | centering_analysis | No |
| 56 | [x] | `tab:mavlink-messages` | MAVLink messages used | comms_architecture | Overlaps tab:mavlink-commands |

### Tables We Don't Have But Could Add

| # | Status | Idea | Where | Impact |
|---|--------|------|-------|--------|
| 57 | [ ] | Requirements compliance matrix with evidence type + fidelity level (sim/bench/field) | Requirements Verification | MEDIUM |
| 58 | [ ] | Model retraining progression: v1 (640) -> v2 (1280) -> v3 (1088) with metrics per round | Evaluation or System Description | MEDIUM -- shows iterative improvement |
| 59 | [ ] | Comparison with commercial/academic SAR drones (from docs/SAR_COMPARISON.md) | Design Rationale or Introduction | MEDIUM |
| 60 | [ ] | "What would change" prioritised list (improvement, effort, impact) | Evaluation | MEDIUM |

---

## What's Been Done Since Last Checklist Update

### Sections Improved
- [x] **evaluation.tex MAJOR REWRITE**: Now 142 lines with Lessons Learned subsection (4 items), weather adaptation paragraph, bug discovery cross-reference to appendix tab:bug-cost, discussion paragraphs for 5 themes, summary paragraph. Was previously thin.
- [x] **system_description.tex ground station EXPANDED**: Was 3 lines (L182-184). Now ~10 lines covering MJPEG, 3 panels, 9 buttons, operator workflow, headless auto-detect, passive mode. Substantially improved.
- [x] **system_description.tex simulation EXPANDED**: Now covers 4 simulation levels with specific bugs caught.
- [x] **05_path_planning.tex FULLY WRITTEN**: 181-line comprehensive section with: CPP background + citations, area definition (3 input methods), rotated-mask algorithm (6 steps), lane width equations, scan angle optimization (216 configs), energy analysis, Bezier smoothing, focus area, spiral alternative, CPP comparison table, flight parameters table, coverage_vs_time figure. NOT in main.tex.

### New Sections Written
- [x] **path_tradeoffs.tex** (82 lines): 7 subsections covering diagonal vs axis-aligned, lane width vs altitude trade-off (with table), altitude-dependent speed schedule (with equation), turn strategy + Bezier, overlap margin analysis (3 error sources, root-sum-square), start corner optimization, PLB focus area redirect. NOT in main.tex.
- [x] **pipeline_fps.tex** (95 lines): Raw inference vs effective pipeline FPS analysis. 8-stage pipeline breakdown with measured timings. Table comparing 4 backends. TikZ stacked bar chart. Bottleneck transition analysis. Operational implications for mission planning. NOT in main.tex.
- [x] **alternatives.tex** (78 lines): 5 sets of A/B/C paragraph alternatives for key sections. Reference document for choosing best narrative angle. Not for direct inclusion.

### Cross-References Added
- [x] evaluation.tex P3 now cross-references `tab:bug-cost` and `sec:bug-discovery` (in testing_deep appendix)
- [x] evaluation.tex P6 cross-references `sec:groundstation` (now defined in system_description)
- [x] evaluation.tex P7 cross-references `sec:test-org-detail` (in testing_deep appendix)
- [x] evaluation.tex P8 cross-references `sec:simulation` (now defined in system_description)

---

## Topics Covered vs Still Missing

### COVERED in body sections

| Topic | Where | Depth |
|-------|-------|-------|
| STEEPLE analysis (all 7 dimensions) | Design Rationale | Good -- all substantive |
| Hardware platform + BOM | System Description + Design Rationale | Good |
| Companion computer MCDA | Design Rationale | Good (table) |
| Communication architecture MCDA | Design Rationale | Good (table) |
| Detection model MCDA | Design Rationale | Good (table) |
| Search pattern MCDA | Design Rationale | Good (table) |
| Software architecture (11 modules, 4 layers) | System Description | Good |
| Computer vision pipeline | System Description | Good (figure + text) |
| State machine (20 states) | System Description | Good (figure + text) |
| GPS estimation (3 methods compared) | System Description | Good (4 figures) |
| Geofence (3-layer) | System Description | Good (figure) |
| Ground station | System Description | Good (expanded to ~10 lines) |
| Simulation framework (4 levels) | System Description | Adequate |
| Requirements R01-R12 verification | Requirements Verification | Adequate -- R06, R07, R11 thin |
| Plus/delta (9+/9-) | Evaluation | Good |
| Detection confidence vs altitude | Evaluation | Good (figure) |
| Detection rate vs speed | Evaluation | Good (figure) |
| Latency breakdown | Evaluation | Good (figure) |
| Detection heatmap | Evaluation | Good (figure) |
| Weather cancellation as adaptation | Evaluation | Good (paragraph) |
| Lessons learned (4 items) | Evaluation | Good (new subsection) |
| Incomplete flight validation | Evaluation | Good (honest) |
| Bug discovery (12 defects) | Evaluation cross-ref to appendix | Good |
| Modular architecture resilience | Evaluation | Good |

### NOT COVERED (missing from body, exists elsewhere or not written)

| Topic | Status | Where it could go | Impact | Priority |
|-------|--------|-------------------|--------|----------|
| **Path planning detail** | Written in orphaned 05_path_planning.tex + path_tradeoffs.tex, NOT in body or appendix | Appendix + 1 para in System Description | HIGH -- major subsystem completely absent from assessable pages | 1 |
| **Pipeline FPS analysis** | Written in pipeline_fps.tex, NOT in body | Appendix or CV subsection | MEDIUM -- good quantitative depth | 2 |
| **Real photos** (drone, bench, field, dashboard) | Not taken | body figures | CRITICAL -- +2-3 Communication | 1 |
| **Dashboard as project management tool** | Not mentioned anywhere in report | Introduction or Evaluation | MEDIUM -- "innovative technique" for Communication | 3 |
| **Docker testing as Tier 2.5** | Not mentioned | System Description or Evaluation | MEDIUM -- novel testing approach | 3 |
| **WSL cross-platform testing** | Not mentioned | Evaluation | LOW -- supports "same code everywhere" claim | 4 |
| **3-round model progression** (640->1280->1088) | Mentioned in P1 ("swapped three times") but no detail/table | Evaluation or appendix | MEDIUM -- shows iterative improvement | 3 |
| **"What would change" subsection** | Not written | Evaluation | MEDIUM -- +1 Decision Making | 2 |
| **Sim-to-real confidence statement** | Not written | Evaluation | MEDIUM -- +1 Specialist Skills | 3 |
| **GPS error budget in body** | Only in appendix (tab:error-budget) | System Description | MEDIUM -- +1 Specialist Skills | 3 |
| **Five-tier table in body** | Only in appendix (tab:five-tier) | Req Verification or Evaluation | MEDIUM -- +1 Specialist Skills | 3 |
| **Contingency tiers summary** | Only in appendix (tab:mvd, tab:target) | Design Rationale | LOW -- +0.5 Decision Making | 4 |
| **MCDA authenticity sentence** | Not written | Design Rationale | LOW -- +0.5 Decision Making | 4 |
| **Explicit SAR industry comparison** | docs/SAR_COMPARISON.md exists, not cited | Introduction or Design Rationale | LOW -- +0.5 Specialist Skills | 4 |
| **ArduPilot citation** | Used throughout, never cited | References | LOW -- +0.5 Communication | 4 |

---

## Fixes Required (from REVIEW_GAPS.md)

### Must Fix Before Submission

| # | Status | Issue | Severity | Fix | Done? |
|---|--------|-------|----------|-----|-------|
| 1 | [ ] | Inconsistent search speed (5, 8, 10 m/s across sections) | CRITICAL | Pick "altitude-dependent, ~8 m/s at 35m nominal" everywhere. path_tradeoffs.tex has the correct speed schedule equation. | NO |
| 2 | [ ] | Two FOV values (49.3 Pi vs 54.4 DJI) not distinguished | CRITICAL | Label every 54.4 as "DJI video" and every 49.3 as "IMX296 Pi camera" | NO |
| 3 | [ ] | Broken citation `rtca_do178c` | HIGH | Add to references.bib | NO |
| 4 | [ ] | Broken cross-refs: `sec:detection`, `sec:ground-station`, `sec:target-localisation` | HIGH | Fix label names -- note sec:groundstation now defined in system_description.tex | PARTIAL (groundstation fixed, others unknown) |
| 5 | [ ] | Footprint width in R05: 27.6m should be 32.2m at 35m | MEDIUM | Fix number (05_path_planning.tex and path_tradeoffs.tex both correctly use 32.2m) | NO |
| 6 | [ ] | Sheridan level: R08 says "Level 2" but Design Rationale says "Level 5/3" | MEDIUM | Make consistent. alternatives.tex Version A says "Level 5 search, Level 3 landing" -- use this. | NO |
| 7 | [ ] | Waypoint count: exec summary "18" vs R01 "35 waypoints across 5 passes" | MEDIUM | Clarify or make consistent | NO |
| 8 | [x] | Duplicate appendix letter "R" (centering_analysis + figure_descriptions) | LOW | Still present in main.tex lines 246+252. Rename figure_descriptions to "T". | NO |
| 9 | [ ] | `extra_refs.bib` not loaded in main.tex | HIGH | Add `\addbibresource{extra_refs.bib}` or merge all keys into references.bib | NO |
| 10 | [ ] | Verify "58 test scripts" claim | LOW | Count actual scripts in tests/ | NO |
| 11 | [ ] | Module names in system_description (gps_utils.py, geofence.py etc.) don't match actual code (utils.py, main.py) | MEDIUM | Update to match real filenames | NO |

### New Issues Found This Audit

| # | Status | Issue | Severity | Fix |
|---|--------|-------|----------|-----|
| 12 | [ ] | `sec:groundstation` defined TWICE: in system_description.tex AND orphaned 08_ground_station.tex | MEDIUM | Remove from orphaned file (not in main.tex so harmless, but confusing) |
| 13 | [ ] | `sec:simulation` defined TWICE: in system_description.tex AND orphaned 09_simulation.tex | MEDIUM | Same -- orphaned file not compiled but label exists |
| 14 | [ ] | path_tradeoffs.tex references `Section~\ref{sec:algorithm}` and `Section~\ref{sec:scan-angle}` which are in orphaned 05_path_planning.tex (not in main.tex) | HIGH if included | Must include 05_path_planning.tex or redefine labels |
| 15 | [ ] | pipeline_fps.tex uses pgfplots TikZ chart -- needs `\usepackage{pgfplots}` in preamble | HIGH if included | Add package to main.tex preamble |
| 16 | [ ] | pipeline_fps.tex references `Section~\ref{sec:future}` -- verify this label exists | MEDIUM | Check 14_future_work.tex |

---

## Content Ideas Status Tracker

### High Priority (directly impact score)

| # | Status | Idea | Target section | Impact | Done? |
|---|--------|------|---------------|--------|-------|
| 1 | [x] | **"Decision reversed" narrative**: FOV calibration story | Evaluation | +1-2 Decision Making | YES -- in "Weather cancellation as adaptation evidence" paragraph |
| 2 | [ ] | **"What would change" subsection**: prioritised improvements with effort estimates | Evaluation | +1 Decision Making | NO |
| 3 | [ ] | **Sim-to-real confidence statement** | Evaluation | +1 Specialist Skills | NO |
| 4 | [x] | **Condensed defect discovery**: Bug-cost table referenced from body | Evaluation | +1-2 Decision Making | YES -- P3 cross-references tab:bug-cost |
| 5 | [ ] | **Condensed error budget**: 6-source GPS error budget from gps_estimation_deep | System Description | +1 Specialist Skills | NO |
| 6 | [ ] | **Five-tier testing summary**: Condense into body | Req Verification or Evaluation | +1 Specialist Skills | NO |
| 7 | [ ] | **Contingency tiers summary**: MVD/Target/Stretch | Design Rationale | +1 Decision Making | NO |
| 8 | [x] | **Expand Ground Station subsection** | System Description | +0.5 Communication | YES -- expanded from 3 lines to ~10 lines |

### Medium Priority

| # | Status | Idea | Target section | Impact | Done? |
|---|--------|------|---------------|--------|-------|
| 9 | [ ] | **MCDA authenticity sentence** | Design Rationale | +0.5 Decision Making | NO |
| 10 | [ ] | **Deeper STEEPLE for Political and Legal**: cite CAA CAP 722, UK GDPR | Design Rationale | +0.5 Decision Making | NO -- but Political now cites caa2024uas and jarus2019sora |
| 11 | [ ] | **Docker Pi test as Tier 2.5** | System Description or Evaluation | +0.5 Specialist Skills | NO |
| 12 | [ ] | **WSL cross-platform testing** | Evaluation | +0.5 Specialist Skills | PARTIAL -- P2 mentions "WSL (SITL)" |
| 13 | [ ] | **Iterative model training narrative**: 3 rounds (640->1280->1088) | Evaluation or System Description | +0.5 Decision Making | PARTIAL -- P1 says "swapped three times" but no detail |
| 14 | [ ] | **Branch strategy as SE evidence** | Introduction or Evaluation | +0.5 Communication | NO |
| 15 | [ ] | **Dashboard mention**: React-based project tracker | Introduction or Evaluation | +0.5 Communication | NO |
| 16 | [ ] | **Explicit comparison with industry SAR systems** | Introduction or Design Rationale | +0.5 Specialist Skills | NO |

### Lower Priority (polish)

| # | Status | Idea | Target section | Impact | Done? |
|---|--------|------|---------------|--------|-------|
| 17 | [ ] | BGR colour discovery as debugging narrative | Evaluation | +0.5 | PARTIAL -- mentioned in P3 bug list |
| 18 | [ ] | SRT sync discovery (6fps vs 30fps mismatch) | Evaluation | +0.5 | NO |
| 19 | [ ] | Python 3.13 compatibility chain as adaptation evidence | Design Rationale | Already mentioned | YES -- in Hardware Platform Selection |
| 20 | [ ] | Exec summary mention of weather cancellation + adaptation | Exec Summary | +0.5 | NO |
| 21 | [ ] | Data augmentation details | System Description or appendix | LOW | In appendix (12_model_training) |
| 22 | [ ] | ArduPilot citation | References | +0.5 Communication | NO |
| 23 | [x] | Fix duplicate appendix letter "R" | main.tex | Fix | NOT FIXED -- still duplicate in main.tex |

---

## Evidence We Have But Haven't Used

### From Project Code & Infrastructure

| # | Evidence | Where it lives | Used in report? | Impact |
|---|----------|----------------|-----------------|--------|
| 1 | Docker Pi test (Dockerfile.pi-test) | CLAUDE.md, Dockerfile.pi-test | NO | Novel Tier 2.5 testing evidence |
| 2 | WSL simulation testing | CLAUDE.md | PARTIAL (P2 mentions WSL) | Platform independence |
| 3 | 3 model variants (sar_640, sar_1280, sar_v2_1088) | cv_models/ | PARTIAL (P1 says "three times") | Iterative improvement story |
| 4 | DJI SRT sync discovery (6fps vs 30fps) | CLAUDE.md | NO | Rigorous testing narrative |
| 5 | Camera colour fix (BGR despite RGB888) | CLAUDE.md, vision.py | YES -- in P3 bug list | Done |
| 6 | Data augmentation pipeline (7 types) | generate_dataset_v2.py | In appendix only | Detail level |
| 7 | 268+ commits, branch strategy | GitHub | NO | Professional SE |
| 8 | 58 test scripts across 8 categories | tests/ directory | Claimed in P7, not broken down | Need verification |
| 9 | Dashboard/project tracker | dashboard/ | NO | "Innovative technique" |
| 10 | FOV calibration from video (9 samples) | tools/fov_calibrate_video.py | In appendix only | Field calibration rigour |
| 11 | GPS timing lag discovery (100-200ms) | memory/gps-timing-lag.md | In body (D3) + appendix | Done |
| 12 | Cost-risk gradient (50:1 ratio) | testing_deep.tex | Appendix only | Powerful quantitative evidence |
| 13 | V-model mapping to 5-tier framework | testing_deep.tex | Appendix only | SE maturity |
| 14 | Lens calibration at 1.5ms cost | vision.py | In body (P5) | Done |
| 15 | Inverse-variance weighting justification | System Description | In body | Done |
| 16 | simple_simulator.py (2508 lines) | simple_simulator.py | Barely mentioned | Full interactive MVP |
| 17 | 93 WBS tasks tracked in dashboard | dashboard/wbs-data.ts | NO | Project management |
| 18 | Bezier-smoothed U-turns | 05_path_planning.tex (orphaned) | NOT in assessable pages | Novel optimization |
| 19 | 216-config parametric sweep | 05_path_planning.tex (orphaned) | NOT in assessable pages | Systematic optimization |
| 20 | Altitude-dependent speed schedule equation | path_tradeoffs.tex (not included) | NOT in assessable pages | Novel contribution |
| 21 | Overlap margin root-sum-square analysis | path_tradeoffs.tex (not included) | NOT in assessable pages | Quantitative rigour |
| 22 | Pipeline FPS bottleneck transition analysis | pipeline_fps.tex (not included) | NOT in assessable pages | Shows inference vs pipeline understanding |

---

## Priority Actions (ordered by score impact)

### Tier 1: Quick wins for 83+ (do these first)

1. **[ ] Take real photos** -- drone assembled, bench test setup, Pi + camera closeup, field day. Replace placeholder text boxes in figure_descriptions.tex. (+2-3 Communication)
2. **[ ] Take ground station screenshot** -- run pi_flight.py in SIMULATION, screenshot the browser dashboard with detection overlay. (+1-2 Communication)
3. **[ ] Include 05_path_planning.tex as appendix in main.tex** -- add `\input{sections/05_path_planning}` after existing appendices. This activates coverage_vs_time figure, cpp-comparison table, flight-params table. Add 1 paragraph referencing it from System Description body. (+1 Specialist Skills)
4. **[ ] Include pipeline_fps.tex as appendix** -- add `\input{sections/pipeline_fps}` and add `\usepackage{pgfplots}` to preamble. Cross-reference from Evaluation D2/D9. (+0.5 Specialist Skills)
5. **[ ] Fix all critical inconsistencies** -- speed (use altitude-dependent schedule), FOV (label Pi vs DJI), footprint (32.2m), Sheridan level, cross-refs, citations. (+1 across all criteria)

### Tier 2: Moderate effort, significant impact

6. **[ ] Add "what would change" subsection to Evaluation** -- prioritised table: NCNN backend, FP16 inference, GPS lag compensation, multi-class detector, real test set. (+1 Decision Making)
7. **[ ] Pull GPS error budget (tab:error-budget) into System Description** -- 1-paragraph summary + reference to appendix. (+1 Specialist Skills)
8. **[ ] Add detection montage figure** -- 4-6 frames from DJI video at different altitudes. (+1 Specialist Skills for R05/R10)
9. **[ ] Include path_tradeoffs.tex content** -- either as appendix or merge key content (speed schedule equation, overlap margin analysis) into System Description. (+0.5 Specialist Skills)
10. **[ ] Fix extra_refs.bib** -- either add `\addbibresource{extra_refs.bib}` or merge into references.bib. (+0.5 fixes broken citations)
11. **[ ] Add `\addbibresource{extra_refs.bib}` or merge** + add rtca_do178c + ArduPilot citation. (+0.5 Communication)

### Tier 3: Polish

12. **[ ] Mention dashboard as project management tool** in Introduction or Evaluation.
13. **[ ] Add Docker Pi test as Tier 2.5 evidence** in 1 sentence in Evaluation or System Description.
14. **[ ] Add model training progression** -- expand P1 with 1-2 sentences about 640->1280->1088 with specific metrics.
15. **[ ] Add contingency tiers summary** (1 paragraph) in Design Rationale.
16. **[ ] Add sim-to-real confidence statement** in Evaluation.
17. **[ ] Add 1 MCDA authenticity sentence** ("initially selected X, trade study revealed Y").
18. **[ ] Fix appendix letter duplication** (R appears twice).
19. **[ ] Mention field day pivot** in Exec Summary.
20. **[ ] Verify "58 test scripts" claim** by counting files in tests/.
21. **[ ] Fix module names** in system_description (gps_utils.py -> utils.py, etc.).

---

## Alternative Paragraphs Available (from alternatives.tex)

For final polish, pick the strongest version for each:

| Section | Versions | Recommendation |
|---------|----------|----------------|
| STEEPLE opening | A (current: systematic), B (safety stakes), C (economic accessibility) | B or C stronger than A -- lead with concrete stakes |
| Weather adaptation | A (current: factual), B (narrative), C (data quality) | C is strongest -- quantifies what was gained |
| Autonomy level | A (current: Sheridan), B (SAR practitioner), C (DO-178C) | B most engaging, C most rigorous |
| Evaluation opening | A (current: balanced), B (honest admission), C (strongest result first) | B or C -- B shows maturity, C hooks the reader |
| Conclusion/summary | A (current), B (lessons-first), C (future-impact-first) | B is strongest -- "knowing whether it works rivals building it" |

---

## Summary Statistics

| Metric | Count |
|--------|-------|
| Total .tex section files | 42 |
| Included in main.tex | 25 (4 body + 2 excluded + 19 appendices) |
| NOT included in main.tex | 17 (3 new + 13 orphaned + 1 reference-only) |
| PDF figures in figs/ | 20 (15 body + 2 unused + 3 appendix-only) |
| PNG duplicates in figs/ | 16 (same figures, different format) |
| Tables in body | 9 |
| Tables in appendices | 43 |
| Tables in new/orphaned (not compiled) | 4 |
| Total unique tables | 56 |
| Broken cross-references | 3-4 estimated |
| Broken citations | 1-2 confirmed |
| Critical fixes remaining | 8 of 11 |
| High-priority content ideas done | 3 of 8 |
| Estimated pages used | ~14.5 of 15 |
