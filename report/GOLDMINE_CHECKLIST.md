# D6 Report Goldmine Checklist

**Master tracking document. Updated: 2026-03-27.**
**Current estimated score: ~79 (range 77-82). Target: 83+.**

Page budget: 15 pages counted (Design Rationale + System Description + Requirements Verification + Evaluation).
Excluded from count: Cover, Exec Summary, Introduction, References, Appendices.

---

## Figures (Charts, Diagrams, Photos)

### Currently in Body Sections

| # | Status | File | Description | Section | Quality |
|---|--------|------|-------------|---------|---------|
| 1 | [x] | `mission_overview.pdf` | Fenswood site map with search polygon, SSSI, takeoff point, lawnmower pattern | System Description | Good |
| 2 | [x] | `architecture.pdf` | Module dependency graph (config, vision, planning, main, utils) | System Description | Good |
| 3 | [x] | `pi_system.pdf` | Pi 5 hardware interfaces and data flow diagram | System Description | Good |
| 4 | [x] | `geofence_diagram.pdf` | 4-panel geofence: boundaries, repulsive field, waypoint correction, emergency mode | System Description | Good |
| 5 | [x] | `cv_pipeline.pdf` | CV pipeline: capture -> undistort -> resize -> inference -> filter -> rescale | System Description | Good |
| 6 | [x] | `state_machine.pdf` | 20-state FSM transition diagram | System Description | Good |
| 7 | [x] | `gps_bullseye.pdf` | GPS estimation error scatter with CEP50 circle | System Description | Good |
| 8 | [x] | `gps_error_direction.pdf` | Directional error distribution showing heading-aligned elongation | System Description | Good |
| 9 | [x] | `gps_convergence.pdf` | GPS estimate convergence over successive observations | System Description | Good |
| 10 | [x] | `estimator_comparison.pdf` | Comparison: raw avg, inverse-variance, Kalman filter | System Description | Good |
| 11 | [x] | `mission_timeline.pdf` | Mission timeline with state transitions (coloured blocks) | System Description | Good |
| 12 | [x] | `conf_vs_alt.pdf` | Detection confidence vs altitude plot | Evaluation | Good |
| 13 | [x] | `det_vs_speed.pdf` | Detection rate vs flight speed | Evaluation | Good |
| 14 | [x] | `latency_breakdown.pdf` | Per-frame latency breakdown (capture, undistort, resize, inference, post) | Evaluation | Good |
| 15 | [x] | `detection_heatmap.pdf` | Spatial detection density across survey area | Evaluation | Good |

### In Appendices Only (not in body)

| # | Status | File | Description | Appendix | Quality | Should move to body? |
|---|--------|------|-------------|----------|---------|---------------------|
| 16 | [x] | `detection_envelope.pdf` | Combined confidence + motion blur envelope with reliable detection zone | cv_extended | Good | YES -- strong evidence for Evaluation |
| 17 | [x] | `blur_vs_altitude.pdf` | Pixel motion blur vs altitude at different speeds/exposures | cv_extended | Good | Consider -- supports IMX296 global shutter argument |
| 18 | [x] | `coverage_vs_time.pdf` | Coverage % vs time for different scan angles | 05_path_planning (ORPHANED) | Good | YES -- path planning not in body at all |

### Figures That Exist as Placeholder Text Only (no real image)

These are in `figure_descriptions.tex` as detailed text descriptions inside `\fbox{}` boxes. They need actual photos/screenshots.

| # | Status | Label | Description | Impact if added |
|---|--------|-------|-------------|-----------------|
| 19 | [ ] | `fig:dashboard-screenshot` | Ground station browser UI with MJPEG stream + GPS grid + command buttons | CRITICAL -- +2 Communication |
| 20 | [ ] | `fig:hardware-photo` | Assembled drone with labelled components (Pi, Cube, camera, GPS, battery) | CRITICAL -- +2-3 Communication |
| 21 | [ ] | `fig:detection-overlay` | Example detection frame at 35m with bounding box, confidence, scale bar | HIGH -- +1-2 Specialist Skills |
| 22 | [ ] | `fig:lawnmower-satellite` | Lawnmower pattern overlaid on real satellite image with SSSI + takeoff | MEDIUM -- mission_overview.pdf partially covers this |
| 23 | [ ] | `fig:bench-setup` | Bench test configuration: Pi + camera + Cube + laptop + PuTTY | MEDIUM -- shows real engineering setup |

### Figures We Could Create But Don't Have

| # | Status | Idea | Where it would go | Impact |
|---|--------|------|-------------------|--------|
| 24 | [ ] | Detection montage: 4-6 frames at different altitudes (15m, 25m, 35m, 45m) with bounding boxes | Requirements Verification R05/R10 | HIGH -- directly evidences detection capability |
| 25 | [ ] | R06 PLB redirect: before/after showing pattern shift when focus area received | Requirements Verification R06 | MEDIUM -- R06 verification is thin |
| 26 | [ ] | Landing position probability distribution (histogram or scatter) for R07 | Requirements Verification R07 | MEDIUM -- mathematical argument needs visual backup |
| 27 | [ ] | Confusion matrix from training (already exists in cv_models/) | Model Training appendix or Evaluation | LOW -- already described in text |
| 28 | [ ] | Training loss curves (already exists in cv_models/) | Model Training appendix | LOW |
| 29 | [ ] | Screenshot of Mission Planner showing SITL connection | System Description or Introduction | LOW |
| 30 | [ ] | Photo of the rescue dummy on the field | Introduction or System Description | MEDIUM -- context for what we're detecting |
| 31 | [ ] | Comparison: Pi camera frame vs DJI camera frame at same altitude | Evaluation or Calibration appendix | LOW -- explains two-FOV issue |
| 32 | [ ] | Energy/battery consumption estimate diagram | Path Planning or Design Rationale | LOW |
| 33 | [ ] | Wiring schematic (Pi GPIO to Cube TELEM2 pinout) | System Description or Hardware appendix | LOW |
| 34 | [ ] | Field day photo(s): team at Fenswood, equipment setup outdoors | Introduction or Field Day appendix | MEDIUM -- engagement and credibility |

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
| 9 | [x] | `tab:plus-delta` | Plus/delta review of technical performance | Evaluation | Good |

### Tables in Appendices (NOT assessed)

| # | Status | Label | Description | Appendix | Move to body? |
|---|--------|-------|-------------|----------|---------------|
| 10 | [x] | `tab:steeple` | STEEPLE analysis summary (7 dimensions) | steeple.tex (ORPHANED) | Check if included via design_rationale |
| 11 | [x] | `tab:state-transitions` | Full 20-state, 32-transition table | A1_state_table | No -- too large |
| 12 | [x] | `tab:config-params` | All configuration parameters | A2_config_params | No -- reference material |
| 13 | [x] | `tab:augmentation` | Data augmentation pipeline (offline + online) | 12_model_training | No -- detail level |
| 14 | [x] | `tab:data_composition` | Dataset composition (300 syn + 16 real + 50 neg) | 12_model_training | Consider 1-line summary in body |
| 15 | [x] | `tab:training_config` | Training hyperparameters | 12_model_training | No |
| 16 | [x] | `tab:training_results` | Detection performance: v1 vs v2 model comparison | 12_model_training + cv_extended | YES -- shows iterative improvement |
| 17 | [x] | `tab:failure-modes` | Failure modes and automated responses | 13_safety_risk | Consider condensed version in Design Rationale |
| 18 | [x] | `tab:risk-register` | Risk register with mitigations | 13_safety_risk | Consider top 3-5 in body |
| 19 | [x] | `tab:five-tier` | Five-tier progressive testing framework | 10_testing | YES -- key evidence for methodology |
| 20 | [x] | `tab:stress-results` | 20 stress test scenarios in SITL | 10_testing | Consider top 5 in Evaluation |
| 21 | [x] | `tab:benchmark-results` | Pi 5 inference benchmark results | 11_field_results | Already summarised in body |
| 22 | [x] | `tab:backend_comparison` | Inference backend comparison (TFLite vs ONNX vs NCNN) | inference_architecture | No |
| 23 | [x] | `tab:inference_roadmap` | Inference improvement roadmap (baseline + projected) | inference_architecture | No |
| 24 | [x] | `tab:pipeline_timing` | Per-stage timing breakdown (50 runs) | cv_extended | No -- latency_breakdown figure covers this |
| 25 | [x] | `tab:cv_benchmarks` | Full inference benchmarks on Pi 5 | cv_extended | No |
| 26 | [x] | `tab:footprint` | Camera footprint at different altitudes | cv_extended | Consider -- useful for understanding coverage |
| 27 | [x] | `tab:frames_flyover` | Frames per flyover and detection probability | cv_extended | No -- detail level |
| 28 | [x] | `tab:altitude_performance` | Detection performance vs altitude table | cv_extended | YES -- directly supports R05 |
| 29 | [x] | `tab:model_variants` | Available model variants for field deployment | cv_extended | No |
| 30 | [x] | `tab:stream-protocols` | Video streaming protocol comparison (MJPEG vs HLS vs WebRTC) | streaming_architecture | No |
| 31 | [x] | `tab:gsd-altitude` | GSD and footprint at key altitudes | gps_estimation_deep | No |
| 32 | [x] | `tab:error-budget` | Single-observation GPS error budget (6 sources) | gps_estimation_deep | YES -- strong quantitative evidence |
| 33 | [x] | `tab:method-compare` | GPS estimation method comparison (4 methods) | gps_estimation_deep | Already shown via figure |
| 34 | [x] | `tab:bug-cost` | Defect discovery table (tier, fix time, escalation cost) | testing_deep | YES -- GOLD for Decision Making |
| 35 | [x] | `tab:test-categories` | Test script categories and tier coverage | testing_deep | No |
| 36 | [x] | `tab:vmodel-map` | V-model to 5-tier framework mapping | testing_deep | Consider -- shows SE rigour |
| 37 | [x] | `tab:cost-gradient` | Cost and risk gradient across tiers (50:1 ratio) | testing_deep | YES -- powerful evidence |
| 38 | [x] | `tab:mvd` | Minimum viable deliverable components | contingency | Consider 1-paragraph summary in Design Rationale |
| 39 | [x] | `tab:target` | Target deliverable components | contingency | Consider 1-paragraph summary |
| 40 | [x] | `tab:contingency` | Contingency plans for flight day failures | contingency | No |
| 41 | [x] | `tab:test-scripts` | Contingency-to-test-script mapping | contingency | No |
| 42 | [x] | `tab:flight-scripts` | Flight test progression scripts | test_scripts_guide | No |
| 43 | [x] | `tab:hw-tests` | Hardware test scripts | test_scripts_guide | No |
| 44 | [x] | `tab:cal-tests` | Calibration test scripts | test_scripts_guide | No |
| 45 | [x] | `tab:experiment-scripts` | Day 1 experiment scripts | test_scripts_guide | No |
| 46 | [x] | `tab:script-req-map` | Test scripts mapped to requirements | test_scripts_guide | Consider -- shows traceability |
| 47 | [x] | `tab:test-gaps` | Tests not yet completed on real hardware | test_scripts_guide | No |
| 48 | [x] | `tab:calibration` | Sensor calibration summary with "error if uncalibrated" | calibration_deep | YES -- shows initiative |
| 49 | [x] | `tab:sim-val-matrix` | Simulation validation coverage matrix | simulation_validation | No |
| 50 | [x] | `tab:sim-val-results` | Quantitative simulation validation results | simulation_validation | Consider |
| 51 | [x] | `tab:centering-comparison` | Centering vs direct offset: 20 simulated missions | centering_analysis | No |
| 52 | [x] | `tab:mavlink-messages` | MAVLink messages used | comms_architecture | Overlaps tab:mavlink-commands |

### Tables We Don't Have But Could Add

| # | Status | Idea | Where | Impact |
|---|--------|------|-------|--------|
| 53 | [ ] | MCDA: streaming protocol (already exists as tab:stream-protocols in appendix -- condense) | Design Rationale | LOW -- 5th MCDA may be overkill |
| 54 | [ ] | Requirements compliance matrix with evidence type + fidelity level (sim/bench/field) | Requirements Verification | MEDIUM -- more structured than current prose |
| 55 | [ ] | Model retraining progression: v1 (640) -> v2 (1280) -> v3 (1088) with metrics | Evaluation or System Description | MEDIUM -- shows iterative improvement |
| 56 | [ ] | Comparison with commercial/academic SAR drones (from docs/SAR_COMPARISON.md) | Design Rationale or Introduction | MEDIUM -- shows literature awareness |
| 57 | [ ] | "What would change" prioritised list (improvement, effort, impact) | Evaluation | MEDIUM -- shows strategic thinking |
| 58 | [ ] | Platform comparison (Hexsoon EDU-450 vs DJI vs custom) | Design Rationale | LOW -- platform was provided, not chosen |

---

## Sections

### Body Sections (counted toward 15-page limit)

| # | Status | File | Title | ~Lines | Quality | Notes |
|---|--------|------|-------|--------|---------|-------|
| 1 | [x] | `design_rationale.tex` | Design Rationale | 235 | Good | 5 MCDA tables, STEEPLE. Could tighten to free 0.5 page. STEEPLE depth uneven (Political, Legal shallow). |
| 2 | [x] | `system_description.tex` | System Description | 213 | Good | 11 figures, dense. Ground station only 3 lines (L182-184). Simulation section thin. |
| 3 | [x] | `requirements_verification.tex` | Requirements Verification | 123 | Needs improvement | R06 thin (no quantitative evidence, no figure). R07 no visual. R11 very brief. Sheridan level inconsistent with Design Rationale. |
| 4 | [x] | `evaluation.tex` | Evaluation | 142 | Needs improvement | Plus/delta table is good. Missing: "what would change" subsection, "decision reversed" narrative, sim-to-real confidence statement, lessons learned. |

### Excluded Sections (not counted)

| # | Status | File | Title | ~Lines | Quality | Notes |
|---|--------|------|-------|--------|---------|-------|
| 5 | [x] | `exec_summary.tex` | Executive Summary | 18 | Needs improvement | Doesn't mention field day pivot or adaptation. Claims "14 figures" and "18 waypoints" -- verify. Could mention weather cancellation as maturity evidence. |
| 6 | [x] | `intro_d6.tex` | Introduction | 79 | Good | Team bios, contribution table. |

### Appendices (excluded, NOT assessed, but support body cross-references)

| # | Status | File | Appendix | Quality | Key content to pull into body? |
|---|--------|------|----------|---------|-------------------------------|
| A | [x] | `A1_state_table.tex` | A: State transition table | Good | No -- too large |
| B | [x] | `A2_config_params.tex` | B: Config parameters | Good | No |
| C | [x] | `12_model_training.tex` | C: Model training pipeline | Good | Training results table (v1 vs v2) |
| D | [x] | `13_safety_risk.tex` | D: Safety & risk | Good | Top 3-5 risk items condensed in Design Rationale |
| E | [x] | `10_testing.tex` | E: Testing methodology | Good | Five-tier table is GOLD -- must appear in body |
| F | [x] | `11_field_results.tex` | F: Field results | Good | Benchmark numbers already in body |
| G | [x] | `14_future_work.tex` | G: Future work | Good | 1-paragraph summary in Evaluation |
| H | [x] | `inference_architecture.tex` | H: Inference architecture | Good | No |
| H2 | [x] | `cv_extended.tex` | H2: CV extended analysis | Excellent | detection_envelope figure, altitude_performance table |
| I | [x] | `streaming_architecture.tex` | I: Streaming architecture | Over-engineered | Scorer says 2+ pages justifying MJPEG is overkill |
| J | [x] | `gps_estimation_deep.tex` | J: GPS estimation deep dive | Excellent | Error budget table (6 sources) -- should be in body |
| K | [x] | `testing_deep.tex` | K: Testing deep dive | Excellent | bug-cost table, cost-gradient table -- MUST be in body |
| L | [x] | `field_day_narrative.tex` | L: Field day narrative | Good | FOV discovery story -- must appear in body as "decision reversed" |
| M | [x] | `contingency.tex` | M: Contingency planning | Good | MVD/Target/Stretch tiers -- 1 paragraph in Design Rationale |
| N | [x] | `test_scripts_guide.tex` | N: Test scripts guide | Good | script-req-map table shows traceability |
| O | [x] | `calibration_deep.tex` | O: Sensor calibration | Good | calibration summary table (error if uncalibrated) |
| P | [x] | `simulation_validation.tex` | P: Simulation validation | Good | No |
| Q | [x] | `mission_flow.tex` | Q: Mission flow | Good | No |
| R | [x] | `centering_analysis.tex` | R: Centering vs offset analysis | Good | No |
| S | [x] | `comms_architecture.tex` | S: Communication architecture | Good | No |
| T* | [x] | `figure_descriptions.tex` | Appendix with placeholder figures | Placeholder only | These should become real images, not text descriptions |

### Orphaned Sections (exist but NOT included in main.tex)

These were written as standalone sections before the report was restructured. Content may be reusable.

| # | File | Title | Lines | Reusable content? |
|---|------|-------|-------|-------------------|
| 1 | `05_path_planning.tex` | Path Planning (full section) | 181 | YES -- 4-page section with equations, parametric sweep, energy analysis, Bezier smoothing, coverage comparison. Currently the body has only 1 paragraph. Consider making this an appendix + pulling coverage_vs_time figure into body. |
| 2 | `steeple.tex` | STEEPLE Analysis | 44 | Check if design_rationale.tex already includes this content inline or via \input |
| 3 | `00_abstract.tex` | Abstract | ? | Probably superseded by exec_summary |
| 4 | `01_introduction.tex` | Introduction (old) | ? | Superseded by intro_d6 |
| 5 | `02_system_architecture.tex` | System Architecture (old) | ? | Superseded by system_description |
| 6 | `03_hardware_platform.tex` | Hardware Platform (old) | ? | Content likely in system_description |
| 7 | `04_computer_vision.tex` | Computer Vision (old) | ? | Content likely in system_description + cv_extended |
| 8 | `06_state_machine.tex` | State Machine (old) | ? | Content likely in system_description |
| 9 | `07_target_localisation.tex` | Target Localisation (old) | ? | Content likely in system_description |
| 10 | `08_ground_station.tex` | Ground Station (old) | ? | Content may have more detail than the 3 lines currently in system_description |
| 11 | `09_simulation.tex` | Simulation (old) | ? | Content in system_description + simulation_validation |
| 12 | `15_conclusion.tex` | Conclusion | ? | Brief says no conclusion section required, but could be useful |
| 13 | `introduction.tex` | Another introduction variant | ? | Superseded |

---

## Content Ideas Not Yet Written

### High Priority (directly impact score)

| # | Status | Idea | Target section | Impact |
|---|--------|------|---------------|--------|
| 1 | [ ] | **"Decision reversed" narrative**: FOV discovery story (7.0mm datasheet -> 5.46mm field calibration, 22% error, would have caused 6m offset). Currently only in Field Day appendix (NOT assessed). | Evaluation or Design Rationale | +1-2 Decision Making |
| 2 | [ ] | **"What would change" subsection**: prioritised improvements with effort estimates. "If we had 2 more weeks..." | Evaluation | +1 Decision Making |
| 3 | [ ] | **Sim-to-real confidence statement**: "These results give X% confidence that outdoor performance will be within Y% because Z" | Evaluation | +1 Specialist Skills |
| 4 | [ ] | **Condensed defect discovery table**: Top 5 bugs from tab:bug-cost pulled into body (tier discovered, fix time, escalation cost if missed) | Evaluation | +1-2 Decision Making |
| 5 | [ ] | **Condensed error budget**: 6-source GPS error budget from gps_estimation_deep into System Description or Evaluation | System Description | +1 Specialist Skills |
| 6 | [ ] | **Five-tier testing summary**: Condense tab:five-tier into body (even 1 paragraph + simplified table) | Requirements Verification or Evaluation | +1 Specialist Skills |
| 7 | [ ] | **Contingency tiers summary**: 1 paragraph describing MVD/Target/Stretch deliverable tiers | Design Rationale | +1 Decision Making |
| 8 | [ ] | **Expand Ground Station subsection**: Currently 3 lines. Describe MJPEG streaming, GPS grid, 9 command buttons, headless operation, /cmd endpoint | System Description | +0.5 Communication |

### Medium Priority

| # | Status | Idea | Target section | Impact |
|---|--------|------|---------------|--------|
| 9 | [ ] | **MCDA authenticity sentence**: "Initially selected X, but trade study revealed Y..." for at least one MCDA table | Design Rationale | +0.5 Decision Making |
| 10 | [ ] | **Deeper STEEPLE for Political and Legal**: cite CAA CAP 722 specifically, UK GDPR for data protection | Design Rationale | +0.5 Decision Making |
| 11 | [ ] | **Docker Pi test as methodology evidence**: Tier 2.5 testing -- proves TFLite on Pi-like environment before hardware access | System Description or Evaluation | +0.5 Specialist Skills |
| 12 | [ ] | **WSL cross-platform testing**: Same code runs on Windows and Linux without changes | Evaluation | +0.5 Specialist Skills |
| 13 | [ ] | **Iterative model training narrative**: 3 rounds (640 -> 1280 -> 1088) with progressively better data. Currently only mentions final model. | Evaluation or System Description | +0.5 Decision Making |
| 14 | [ ] | **Branch strategy as SE evidence**: Feature branches, single protected main, 268+ commits | Introduction or Evaluation | +0.5 Communication |
| 15 | [ ] | **Dashboard mention**: React-based project tracker as "innovative technique" for Communication criterion | Introduction or Evaluation | +0.5 Communication |
| 16 | [ ] | **Explicit comparison with industry SAR systems**: cite 2-3 papers from docs/SAR_COMPARISON.md, position our system | Introduction or Design Rationale | +0.5 Specialist Skills |

### Lower Priority (polish)

| # | Status | Idea | Target section | Impact |
|---|--------|------|---------------|--------|
| 17 | [ ] | BGR colour discovery as debugging narrative (systematic 6-permutation test) | Evaluation | +0.5 |
| 18 | [ ] | SRT sync discovery (6fps vs 30fps mismatch) as rigorous testing evidence | Evaluation | +0.5 |
| 19 | [ ] | Python 3.13 compatibility chain (pyserial broken -> mavproxy bridge) as adaptation evidence | Design Rationale | Already mentioned, could be expanded |
| 20 | [ ] | Exec summary mention of weather cancellation + adaptation | Exec Summary | +0.5 |
| 21 | [ ] | Data augmentation details: brightness, contrast, blur, rotation, scale variations | System Description or Model Training appendix | LOW |
| 22 | [ ] | ArduPilot citation (core flight stack, currently uncited) | References | +0.5 Communication |
| 23 | [ ] | Rename second "Appendix R" to "Appendix T" (duplicate letter) | main.tex | Fix |

---

## Evidence We Have But Haven't Used

### From CLAUDE.md / Project Code

| # | Evidence | Where it lives | Why it matters | Used in report? |
|---|----------|----------------|----------------|-----------------|
| 1 | Docker Pi test (Dockerfile.pi-test) | CLAUDE.md, Dockerfile.pi-test | Proves TFLite works on Pi-like environment before having hardware. Novel simulation-first evidence. | NO |
| 2 | WSL simulation testing | CLAUDE.md session log | Same code runs on Linux without changes. Platform independence. | NO |
| 3 | 3 model variants (sar_640, sar_1280, sar_v2_1088) | cv_models/ | Iterative improvement story across 3 training rounds. | Partially -- only final model mentioned |
| 4 | DJI SRT sync discovery (6fps vs 30fps) | CLAUDE.md, memory/ | Rigorous testing revealing issues. Good "decisions that changed" story. | NO |
| 5 | Camera colour fix (BGR despite RGB888 label) | CLAUDE.md session log, vision.py | Hardware subtlety invisible to simulation. Debugging under field pressure. | Mentioned in Design Rationale, could be in Evaluation too |
| 6 | Data augmentation pipeline details | generate_dataset_v2.py | 7 augmentation types at native resolution. Shows training sophistication. | Partially in appendix |
| 7 | 268+ commits, branch strategy | GitHub | Professional software engineering. Feature branches, protected main. | R12 mentions commits, not branch strategy |
| 8 | 58 test scripts across 8 categories | tests/ directory | Industrially serious test infrastructure. | Claimed but not broken down in body |
| 9 | Dashboard/project tracker | dashboard/ | "Innovative technique" for Communication criterion. | NOT mentioned anywhere |
| 10 | FOV calibration from video (9 samples, 15-50m) | tools/fov_calibrate_video.py, docs/VIDEO_ANALYSIS.md | Shows field calibration rigour. Dummy measures 1.7-1.9m consistently. | In appendix only |
| 11 | GPS timing lag discovery (100-200ms, 1m error at 5m/s) | memory/gps-timing-lag.md | Novel finding about GPS latency. | In gps_estimation_deep appendix, not body |
| 12 | Cost-risk gradient (50:1 ratio Tier 1 vs Tier 5) | testing_deep.tex tab:cost-gradient | Powerful quantitative evidence for simulation-first approach. | Appendix only |
| 13 | V-model mapping to 5-tier framework | testing_deep.tex tab:vmodel-map | Shows SE maturity. | Appendix only |
| 14 | Lens calibration integrated at 1.5ms cost (0.7% of inference time) | CLAUDE.md, vision.py | Negligible performance cost for significant accuracy improvement. | In body, well covered |
| 15 | Inverse-variance weighting justification over Kalman | System Description | Mature engineering judgment (physics-aligned, no convergence plateau). | In body, well covered |
| 16 | simple_simulator.py interactive MVP (2508 lines) | simple_simulator.py | Full interactive simulation with keyboard flight, CV, GPS estimation, landing. | Barely mentioned |
| 17 | 93 WBS tasks tracked in dashboard | dashboard/wbs-data.ts | Project management evidence. | NO |
| 18 | Bezier-smoothed U-turns for energy optimisation | 05_path_planning.tex | Novel path smoothing approach. | In orphaned section, not in body |
| 19 | 216-configuration parametric sweep for scan angle | 05_path_planning.tex | Systematic optimisation evidence. | In orphaned section, not in body |
| 20 | Centre-snap optimisation bypassing GSD projection | system_description.tex / code | Novel optimisation: skip expensive projection when target is near centre. | In code, not sure if in report |

### From Dashboard Data (group-report-data.ts)

| # | Evidence | Status |
|---|----------|--------|
| 1 | Top mark tips for each criterion (8 specific strategies per criterion) | Used to guide writing, not cited |
| 2 | Page budget allocation (4+4+4+3 = 15) | Being followed |
| 3 | Outline for each section with specific evidence items | Partially used |
| 4 | SAR comparison references (docs/SAR_COMPARISON.md) | NOT cited in body |

---

## Alternatives to Consider

### Section Structure Alternatives

| # | Current | Alternative | Pros | Cons |
|---|---------|-------------|------|------|
| 1 | 4 body sections (DR + SD + RV + Eval) at ~4+5+3+3 pages | Tighter Design Rationale (3 pages) to free space for richer Evaluation (4 pages) | Evaluation is where the scorer will look for "adaptation" and "lessons learned" | MCDA tables may need to be compressed |
| 2 | Path planning is 1 paragraph in System Description | Add path planning as numbered appendix + pull coverage figure into body + add 1 paragraph of math in System Description | Path planning is a major subsystem with novel content (parametric sweep, Bezier smoothing) | Adds ~0.5 pages to body if expanded |
| 3 | Plus/delta as a single table | Plus/delta as 2-column table + expanded narrative discussion (2-3 paragraphs) after the table | More reflective, shows deeper thinking | Uses more page space |
| 4 | Ground station in 3 lines | Ground station as its own subsection (0.5 page) with screenshot | Shows a major deliverable properly | Page budget |

### Figure Alternatives

| # | Current | Alternative | Impact |
|---|---------|-------------|--------|
| 1 | mission_overview.pdf (generated diagram) | Same figure but with real satellite base map from Google Earth or KML | More professional, shows real terrain |
| 2 | 11 figures in System Description | Move 2-3 figures to Evaluation to balance visual density | Better reading flow |
| 3 | No real photos anywhere | Add 3-4 photos (drone, bench, field, dashboard) | CRITICAL for Communication 83+ |
| 4 | GPS accuracy shown as bullseye + directional plots | Add a table alongside: CEP50, CEP95, max error, mean error | Quantitative + visual combined |

### Narrative Alternatives

| # | Current | Alternative | Impact |
|---|---------|-------------|--------|
| 1 | MCDA tables presented as analysis results | Frame at least one as "we initially chose X, then the trade study showed Y" | Authenticity, avoids appearing formulaic |
| 2 | Weather cancellation not mentioned in body | Frame field day as "adaptive calibration day" yielding 6 quantitative outputs | Strongest "adaptation" evidence available |
| 3 | No explicit failure narrative | Add "a design decision we reversed" section in Evaluation (FOV calibration story) | Shows mature engineering judgment |
| 4 | Future work as simple list in appendix | "What would change with 2 more weeks" as prioritised table in Evaluation body | Shows strategic thinking |

---

## Fixes Required (from REVIEW_GAPS.md)

### Must Fix Before Submission

| # | Status | Issue | Severity | Fix |
|---|--------|-------|----------|-----|
| 1 | [ ] | Inconsistent search speed (5, 8, 10 m/s across sections) | CRITICAL | Pick "~8 m/s at 35m nominal" everywhere |
| 2 | [ ] | Two FOV values (49.3 Pi vs 54.4 DJI) not distinguished | CRITICAL | Label every 54.4 as "DJI video" and every 49.3 as "IMX296 Pi camera" |
| 3 | [ ] | Broken citation `rtca_do178c` | HIGH | Add to references.bib |
| 4 | [ ] | Broken cross-refs: `sec:detection`, `sec:ground-station`, `sec:target-localisation` | HIGH | Fix label names |
| 5 | [ ] | Footprint width in R05: 27.6m should be 32.2m at 35m | MEDIUM | Fix number |
| 6 | [ ] | Sheridan level: R08 says "Level 2" but Design Rationale says "Level 5/3" | MEDIUM | Make consistent |
| 7 | [ ] | Waypoint count: exec summary "18" vs R01 "35 waypoints across 5 passes" | MEDIUM | Clarify or make consistent |
| 8 | [ ] | Duplicate appendix letter "R" (centering_analysis + figure_descriptions) | LOW | Rename one |
| 9 | [ ] | `extra_refs.bib` not loaded in main.tex | HIGH | Add `\addbibresource{extra_refs.bib}` or verify all keys in main bib |
| 10 | [ ] | Verify "58 test scripts" claim | LOW | Count actual scripts |
| 11 | [ ] | Module names in system_description (gps_utils.py, geofence.py etc.) don't match actual code (utils.py, main.py) | MEDIUM | Update to match real filenames |

---

## Priority Actions (ordered by score impact)

### Tier 1: Quick wins for 83+ (do these first)

1. **[ ] Take real photos** -- drone assembled, bench test setup, Pi + camera closeup, field day. Replace placeholder text boxes in figure_descriptions.tex. (+2-3 Communication)
2. **[ ] Take ground station screenshot** -- run pi_flight.py in SIMULATION, screenshot the browser dashboard with detection overlay. (+1-2 Communication)
3. **[ ] Pull defect discovery table (top 5) into Evaluation body** -- from testing_deep.tex tab:bug-cost. (+1-2 Decision Making)
4. **[ ] Add "decision reversed" narrative** -- FOV calibration story in Evaluation body. (+1 Decision Making)
5. **[ ] Fix all inconsistencies** -- speed, FOV, footprint width, Sheridan level, cross-refs, citation. (+1 across all criteria)

### Tier 2: Moderate effort, significant impact

6. **[ ] Pull GPS error budget table into System Description** -- from gps_estimation_deep tab:error-budget. (+1 Specialist Skills)
7. **[ ] Add "what would change" subsection to Evaluation** -- prioritised table of improvements. (+1 Decision Making)
8. **[ ] Add detection montage figure** -- 4-6 frames at different altitudes from DJI video. (+1 Specialist Skills for R05/R10)
9. **[ ] Expand Ground Station subsection** -- from 3 lines to 1 paragraph + screenshot. (+0.5 Communication)
10. **[ ] Make 05_path_planning.tex an appendix** -- add to main.tex, reference from body, pull coverage_vs_time into body. (+0.5 Specialist Skills)

### Tier 3: Polish

11. **[ ] Mention dashboard as project management tool** in Introduction or Evaluation.
12. **[ ] Add contingency tiers summary** (1 paragraph) in Design Rationale.
13. **[ ] Add sim-to-real confidence statement** in Evaluation.
14. **[ ] Deepen STEEPLE** -- cite CAP 722, UK GDPR specifically.
15. **[ ] Mention field day pivot** in Exec Summary.
16. **[ ] Add ArduPilot citation.**
17. **[ ] Add 1 MCDA authenticity sentence.**
18. **[ ] Fix appendix letter duplication.**
