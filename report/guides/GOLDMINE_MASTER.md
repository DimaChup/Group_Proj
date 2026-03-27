# GOLDMINE MASTER -- Definitive Report Tracking Document

**Last updated: 2026-03-27**
**Report type: D6 Company Report (50% of grade)**
**Page budget: 15 pages (excl. cover, exec summary, intro, refs, appendices)**

---

## BODY SECTIONS (assessed, count toward 15-page limit)

| Status | File | Topic | Est. Pages | Quality |
|--------|------|-------|-----------|---------|
| [x] | `design_rationale.tex` | STEEPLE (7 dims), 4 MCDA tables, autonomy justification, contingency mention | ~3.5 | A -- dense, substantive, well-cited |
| [x] | `system_description.tex` | Architecture, HW BOM, geofence (4-layer), CV pipeline, path planning (incl. 216-config sweep, coverage_vs_time fig), state machine, GPS estimation (4 figs), ground station, simulation, mission timeline | ~6 | A -- 16 figures, equations, comprehensive |
| [x] | `requirements_verification.tex` | R01-R12 matrix table + per-req subsections with evidence | ~3 | B -- R06/R07/R11 thin on quantitative evidence |
| [x] | `evaluation.tex` | Plus/delta (9+/9-), 4 discussion paragraphs, bug-cost table (12 defects), lessons learned (4 items), weather adaptation narrative, 4 body figures | ~3 | A- -- strong, honest, cross-referenced |

**Estimated total: ~15.5 pages (may need minor trimming)**

---

## EXCLUDED SECTIONS (not counted toward page limit, included in main.tex)

| Status | File | Topic | Quality |
|--------|------|-------|---------|
| [x] | `exec_summary.tex` | 1-page summary | B -- doesn't mention field day pivot or weather adaptation |
| [x] | `intro_d6.tex` | Context, team bios, contribution table | B+ -- functional |

---

## APPENDIX SECTIONS (not assessed, included in main.tex)

| Status | File | Appendix | Topic | Quality |
|--------|------|----------|-------|---------|
| [x] | `A1_state_table.tex` | A | Full 20-state, 32-transition table + state_machine_full figure | A |
| [x] | `A2_config_params.tex` | B | All config.py parameters with rationale | B+ |
| [x] | `12_model_training.tex` | C | Dataset composition, augmentation pipeline, training config, v1 vs v2 results | A |
| [x] | `13_safety_risk.tex` | D | Failure modes table, risk register with mitigations | B+ |
| [x] | `10_testing.tex` | E | Five-tier framework table, 20 SITL stress tests | A |
| [x] | `11_field_results.tex` | F | Pi 5 benchmarks, FOV calibration equation | B+ |
| [x] | `14_future_work.tex` | G | Prioritised improvements | B |
| [x] | `inference_architecture.tex` | H | Backend comparison (TFLite/ONNX/NCNN), roadmap | B+ |
| [x] | `cv_extended.tex` | H2 | Detection envelope, altitude performance, blur analysis, footprint table, frames per flyover, pipeline timing | A -- 394 lines, excellent depth |
| [x] | `streaming_architecture.tex` | I | MJPEG vs HLS vs WebRTC comparison | B- (over-engineered for MJPEG) |
| [x] | `gps_estimation_deep.tex` | J | Full derivation chain: GSD, pixel-to-body, body-to-GPS, 4 estimators, error budget (6 sources) | A |
| [x] | `testing_deep.tex` | K | Bug-cost table, cost-gradient (50:1), V-model mapping, test categories | A |
| [x] | `field_day_narrative.tex` | L | FOV discovery story, bench day timeline, calibration narrative | A- |
| [x] | `contingency.tex` | M | MVD/Target/Stretch tiers, contingency plans, test-script mapping | B+ |
| [x] | `test_scripts_guide.tex` | N | All test scripts, script-to-requirement traceability | B+ |
| [x] | `calibration_deep.tex` | O | Lens calibration, FOV measurement, DJI video calibration | A- |
| [x] | `simulation_validation.tex` | P | 20-scenario validation matrix, quantitative results | B+ |
| [x] | `mission_flow.tex` | Q | Full mission sequence: pre-flight to RTL | B+ |
| [x] | `centering_analysis.tex` | R | Centering vs direct offset (20 simulated missions), Rayleigh model | A- |
| [x] | `comms_architecture.tex` | S | MAVLink message types, Pi-Cube link, mavproxy bridge | B+ |
| [x] | `pipeline_fps.tex` | -- | Raw vs effective FPS, 4 backends, TikZ stacked bar | A |
| [x] | `path_tradeoffs.tex` | -- | 7 subsections: diagonal alignment, lane width, speed schedule, turns, overlap RSS, start corner, PLB redirect | A |
| [x] | `payload_release.tex` | -- | Tarot mechanism, hover-release rationale (5 reasons), servo sequence | A- |
| [x] | `model_comparison.tex` | -- | 3-generation model progression table, COCO fallback, tiling tradeoff | A- |
| [x] | `search_optimization.tex` | -- | Multi-objective Pareto, energy simulation (216 configs), rotation comparison, NFZ margin, speed-detection-energy | A |
| [x] | `focus_and_repulsive.tex` | -- | PLB redirect logic (R06), repulsive field equations (4 equations) | A |
| [x] | `path_optimization_definitive.tex` | -- | 354-line definitive path optimisation: MOO problem, energy model, 6 strategies, Pareto, 4 figures | A+ |
| [x] | `design_strategy.tex` | -- | 7-step parameter derivation chain: target px -> model px -> altitude -> speed -> overlap -> lane -> energy | A+ |
| [x] | `vision_performance.tex` | -- | Altitude vs pixel size, motion blur, frames on target, coverage, combined envelope | A |
| [x] | `alternatives.tex` | -- | 5 sets of A/B/C paragraph versions (reference, not for inclusion) | Reference |
| [x] | `figure_descriptions.tex` | -- | Placeholder text boxes for photos not yet taken | Placeholder |

---

## FIGURES -- Diagrams (programmatic/drawn)

| Status | Filename | What It Shows | Location | Quality 1-10 |
|--------|----------|---------------|----------|--------------|
| [x] | `architecture.pdf` | Software module dependency graph (6 modules, 4 layers) | Body: system_description | 8 |
| [x] | `pi_system.pdf` | Pi 5 hardware interfaces and data flow | Body: system_description | 8 |
| [x] | `geofence_diagram.pdf` | 4-panel: boundaries, repulsive field, waypoint correction, emergency | Body: system_description | 9 |
| [x] | `cv_pipeline.pdf` | CV pipeline: capture->undistort->resize->inference->filter->rescale | Body: system_description | 8 |
| [x] | `state_machine.pdf` | 20-state FSM transition diagram | Body: system_description | 8 |
| [x] | `state_machine_full.pdf` | Full state machine (alternative layout) | Appendix: A1_state_table | 7 |
| [x] | `state_machine_simple.pdf` | Simplified state machine | Not referenced | 6 |
| [x] | `mission_overview.pdf` | Fenswood site map with search polygon, SSSI, takeoff, lawnmower | Body: system_description | 9 |
| [x] | `mission_timeline.pdf` | Mission timeline with state transitions (coloured blocks) | Body: system_description | 7 |
| [x] | `system_overview_simple.pdf` | Simple system overview | Not referenced | 6 |
| [x] | `optimization_network.pdf` | Parameter dependency network | Appendix | 7 |
| [x] | `sensitivity_matrix.pdf` | Parameter sensitivity matrix | Appendix | 8 |
| [x] | `sensitivity_spider.pdf` | Spider/radar chart | Appendix | 8 |

## FIGURES -- Data Charts (from measured/computed data)

| Status | Filename | What It Shows | Location | Quality 1-10 |
|--------|----------|---------------|----------|--------------|
| [x] | `conf_vs_alt.pdf` | Detection confidence vs altitude (DJI video data) | Body: evaluation + Appendix: cv_extended | 9 |
| [x] | `det_vs_speed.pdf` | Detection rate vs flight speed | Body: evaluation + Appendix: cv_extended | 9 |
| [x] | `latency_breakdown.pdf` | Per-frame latency breakdown (5-stage, Pi 5 hardware) | Body: evaluation + Appendix: cv_extended | 9 |
| [x] | `detection_heatmap.pdf` | Spatial detection density across survey area | Body: evaluation | 8 |
| [x] | `gps_bullseye.pdf` | GPS estimation error scatter with CEP50 circle | Body: system_description | 9 |
| [x] | `gps_error_direction.pdf` | Directional GPS error distribution (heading elongation) | Body: system_description | 9 |
| [x] | `gps_convergence.pdf` | GPS estimate convergence over successive observations | Body: system_description | 8 |
| [x] | `estimator_comparison.pdf` | 3-method comparison: raw avg, inverse-variance, Kalman | Body: system_description | 9 |
| [x] | `detection_envelope.pdf` | Combined confidence + motion blur detection envelope | Appendix: cv_extended | 9 |
| [x] | `blur_vs_altitude.pdf` | Pixel motion blur vs altitude at different speeds | Appendix: cv_extended | 8 |
| [x] | `coverage_vs_time.pdf` | Coverage % vs time for boustrophedon pattern | Body: system_description | 8 |
| [x] | `benchmark_comparison.pdf` | Inference benchmark comparison across models | Appendix | 7 |
| [x] | `training_curves.pdf` | Model training loss/mAP curves | Appendix | 7 |
| [x] | `confusion_matrix.pdf` | Detection confusion matrix | Appendix | 7 |
| [x] | `altitude_detection_table.pdf` | Altitude vs detection table (visual) | Appendix | 7 |
| [x] | `energy_efficiency.pdf` | Energy efficiency vs scan angle/altitude | Appendix: search_optimization | 8 |
| [x] | `rotation_comparison.pdf` | Rotation angle comparison for path optimisation | Appendix: search_optimization | 8 |
| [x] | `nfz_margin_altitude.pdf` | NFZ margin vs altitude analysis | Appendix: search_optimization | 8 |
| [x] | `speed_detection_energy.pdf` | Speed vs detection vs energy triple tradeoff | Appendix: search_optimization | 9 |

## FIGURES -- Real Simulation Outputs (from actual code runs)

| Status | Filename | What It Shows | Location | Quality 1-10 |
|--------|----------|---------------|----------|--------------|
| [x] | `real_dry_run_pattern.jpg` | Actual dry-run pattern output on satellite image | Appendix | 7 |
| [x] | `real_coverage.png` | Real coverage computation output | Appendix | 7 |
| [x] | `real_detection_envelope.png` | Real detection envelope plot | Appendix | 8 |
| [x] | `real_energy_heatmap.png` | Energy heatmap from parametric sweep | Appendix: path_optimization_definitive | 8 |
| [x] | `real_energy_vs_altitude.png` | Energy vs altitude from real sweep | Appendix: path_optimization_definitive | 8 |
| [x] | `real_optimal_pattern.png` | Optimal pattern from solver | Appendix: path_optimization_definitive | 8 |
| [x] | `real_path_patterns.png` | 6 strategy comparison patterns | Appendix: path_optimization_definitive | 9 |
| [x] | `real_scan_angle.png` | Scan angle analysis output | Appendix | 7 |
| [x] | `real_scan_lines.png` | Scan line visualisation | Appendix | 7 |
| [x] | `real_search_comparison.png` | Search strategy comparison | Appendix | 8 |
| [x] | `real_speed_vs_blur.png` | Speed vs blur from real parameters | Appendix | 7 |
| [x] | `real_speed_vs_frames.png` | Speed vs frames on target | Appendix | 7 |
| [x] | `real_time_vs_altitude.png` | Mission time vs altitude | Appendix | 7 |
| [x] | `real_altitude_vs_px.png` | Target pixel size vs altitude | Appendix | 7 |

## FIGURES -- Still Missing (need real photos/screenshots)

| Status | What We Need | Where It Goes | Impact |
|--------|-------------|---------------|--------|
| [ ] | **Ground station browser UI screenshot** (MJPEG + GPS grid + buttons) | Body or Req Verification | CRITICAL -- directly evidences R10, +2 Communication |
| [ ] | **Assembled drone photo** with labelled components (Pi, Cube, camera, GPS, battery) | Body: System Description or Introduction | CRITICAL -- proves it's real, +2-3 Communication |
| [ ] | **Detection overlay frame** at ~35m with bounding box, confidence, scale bar | Body: Req Verification (R05, R10) | HIGH -- directly evidences detection capability |
| [ ] | **Detection montage** (4-6 frames at 15m, 25m, 35m, 45m altitudes) | Req Verification (R05) | HIGH -- shows detection across altitude range |
| [ ] | **Bench test setup photo** (Pi + camera + Cube + laptop + PuTTY terminals) | Evaluation or System Description | MEDIUM -- shows real engineering setup |
| [ ] | **Field day photo(s)** (team at Fenswood, outdoor equipment) | Introduction or field_day_narrative appendix | MEDIUM -- engagement and credibility |
| [ ] | **Rescue dummy on field** (currently only have workshop photo) | Introduction | LOW -- dummy.png partially covers this |
| [ ] | **Payload release mechanism** closeup photo | System Description or payload_release appendix | MEDIUM -- evidences R07 hardware |

---

## TABLES IN BODY

| Label | Section | What It Contains |
|-------|---------|-----------------|
| `tab:mcda-companion` | Design Rationale | MCDA: Pi 5 vs Jetson Nano vs Jetson Orin (weighted scores) |
| `tab:mcda-comms` | Design Rationale | MCDA: MAVLink vs ROS vs custom (weighted scores) |
| `tab:mcda-model` | Design Rationale | MCDA: YOLOv8n vs 8s vs SSD vs Faster-RCNN |
| `tab:mcda-search` | Design Rationale | MCDA: Boustrophedon vs spiral vs grid vs sector |
| `tab:hw-bom` | System Description | Hardware bill of materials (components, specs, costs) |
| `tab:mavlink-commands` | System Description | MAVLink commands used (command, purpose, when, response) |
| `tab:req-verification` | Requirements Verification | R01-R12 matrix: method, evidence, status |
| `tab:plus-delta` | Evaluation | Plus/delta (9 strengths, 9 weaknesses with evidence) |
| `tab:bug-cost` | Evaluation | 12 defects: tier found, fix time, projected cost if missed |
| `tab:contributions` | Introduction (excluded) | Team member contributions by area |

**Total body tables: 10** (9 assessed + 1 in excluded intro)

---

## EQUATIONS IN BODY

| Label/Location | Section | What It Expresses |
|---------------|---------|-------------------|
| `eq:footprint` | System Description | Camera footprint width: $W_g = w_s \cdot h / f$ |
| Lane width | System Description | $L = W_g(1 - \alpha)$ |
| GPS lag compensation | Evaluation (D3) | $\Delta\mathbf{p} = \mathbf{v} \cdot \Delta t_{\text{lag}}$ |

**Note:** Most equations are in appendices (gps_estimation_deep has ~12 equations, cv_extended has ~5, calibration_deep has ~6, design_strategy has ~10, focus_and_repulsive has 4, path_optimization_definitive has several). The body is deliberately equation-light, with derivations in appendices and key results in body text.

---

## KEY TOPICS COVERAGE

### Multi-Objective Optimisation & Path Planning

| Topic | Status | Where | Notes |
|-------|--------|-------|-------|
| Multi-objective optimization (Pareto) | DONE | `path_optimization_definitive.tex` (appendix), mentioned in `system_description.tex` | 5 objectives formalised, Pareto frontier discussed |
| 216-config energy sweep | DONE | `search_optimization.tex` + `path_optimization_definitive.tex` (appendices), mentioned in body | 19 angles x 7 altitudes x 11 speeds |
| Strategy comparison (6 strategies) | DONE | `path_optimization_definitive.tex` (appendix) with `real_path_patterns.png` | 6 strategies compared on real polygon |
| NFZ margin analysis | DONE | `search_optimization.tex` (appendix) with `nfz_margin_altitude.pdf` | Altitude vs NFZ margin tradeoff |
| Speed vs detection tradeoff | DONE | `evaluation.tex` body (fig:det_vs_speed) + `search_optimization.tex` appendix | Real DJI video data + energy model |
| Altitude vs detection | DONE | `evaluation.tex` body (fig:conf_vs_alt) + `cv_extended.tex` appendix | Confidence remains >0.9 to 40m |
| Blur analysis (global shutter advantage) | DONE | `cv_extended.tex` appendix with `blur_vs_altitude.pdf` + `detection_envelope.pdf` | Motion blur vs altitude at multiple speeds |
| Coverage vs time | DONE | `system_description.tex` body (fig:coverage_vs_time) | Near-linear coverage progression shown |

### GPS & Target Localisation

| Topic | Status | Where | Notes |
|-------|--------|-------|-------|
| GPS estimation (4 methods) | DONE | Body: system_description (4 figures) + Appendix: gps_estimation_deep (full derivation) | Raw avg, EWMA, inverse-variance, Kalman |
| Bullseye validation | DONE | Body: system_description (fig:gps_bullseye) | CEP50 = 2.3m from DJI video |
| GPS error budget (6 sources) | PARTIAL | Appendix only (tab:error-budget in gps_estimation_deep) | Exists but NOT pulled into body |
| GPS timing lag | DONE | Body: evaluation D3 + appendix | 100-200ms latency quantified |

### Design & Architecture

| Topic | Status | Where | Notes |
|-------|--------|-------|-------|
| Design reasoning chain (7 steps) | DONE | `design_strategy.tex` (appendix, 236 lines) | Target px -> model px -> altitude -> speed -> overlap -> lane -> energy |
| Sensitivity matrix | DONE | `sensitivity_matrix.pdf` figure (appendix) | Parameter sensitivity analysis |
| Spider/radar chart | DONE | `sensitivity_spider.pdf` figure (appendix) | Multi-dimensional comparison |
| Dependency network | DONE | `optimization_network.pdf` figure (appendix) | Parameter dependency graph |
| Mission flow (pre-flight to RTL) | DONE | `mission_flow.tex` appendix + `mission_timeline.pdf` in body | Full mission sequence |
| Payload release mechanism | DONE | `payload_release.tex` (appendix, 58 lines) | Hover-release rationale (5 reasons), servo sequence |
| Centering vs direct offset | DONE | `centering_analysis.tex` appendix (70 lines) | 20 simulated missions, Rayleigh model |
| Streaming architecture | DONE | `streaming_architecture.tex` appendix | MJPEG vs HLS vs WebRTC (over-engineered) |
| Communication architecture | DONE | `comms_architecture.tex` appendix | MAVLink messages, Pi-Cube link, mavproxy |
| Why not ROS | DONE | `design_rationale.tex` body (tab:mcda-comms) | MCDA table: MAVLink vs ROS vs custom |
| Autonomy level justification (Sheridan) | DONE | Body: design_rationale + requirements_verification R08 | L5 search / L3 landing |

### Computer Vision & Inference

| Topic | Status | Where | Notes |
|-------|--------|-------|-------|
| NCNN vs TFLite benchmarks | DONE | `inference_architecture.tex` appendix (tab:backend_comparison) | TFLite/ONNX/NCNN compared |
| Pipeline FPS vs raw inference | DONE | `pipeline_fps.tex` appendix (tab:pipeline_fps + TikZ chart) | 4 backends, 8-stage pipeline |
| Model training (domain randomization, augmentation) | DONE | `12_model_training.tex` appendix | 7 augmentation types, pipeline described |
| Model comparison (3 generations) | DONE | `model_comparison.tex` appendix (tab:model_generations) | v1(640) -> v2(1280) -> v3(1088) with metrics |
| Detection envelope | DONE | `cv_extended.tex` appendix (fig:detection_envelope) | Combined confidence + blur envelope |

### Testing & Evaluation

| Topic | Status | Where | Notes |
|-------|--------|-------|-------|
| Progressive testing (5 tiers) | DONE | Appendix: 10_testing.tex (tab:five-tier) + body cross-references | Five-tier framework described |
| Field day narrative | DONE | Body: evaluation (weather adaptation) + Appendix: field_day_narrative | FOV discovery, bench day pivot |
| Contingency plans | DONE | `contingency.tex` appendix | MVD/Target/Stretch tiers |
| Bug discovery table in body | DONE | Body: evaluation (tab:bug-cost) | 12 defects with tier, fix time, projected cost |
| Plus/delta evaluation | DONE | Body: evaluation (tab:plus-delta) | 9+/9- with evidence |
| Lessons learned | DONE | Body: evaluation (subsection, 4 items) | Data collection, sensor characterisation, sim fidelity, scheduling |

### Systems Engineering & Decision Making

| Topic | Status | Where | Notes |
|-------|--------|-------|-------|
| STEEPLE analysis | DONE | Body: design_rationale (inline, 7 dimensions) | All substantive with design responses |
| MCDA trade studies (4 tables) | DONE | Body: design_rationale | Companion, comms, model, search |
| Decisions that changed (4 corrections) | DONE | Body: evaluation P3 + appendix | BGR, FOV, pyserial, tflite-runtime |
| Requirements verification (R01-R12) | DONE | Body: requirements_verification | All 12 requirements addressed |

### Report Quality & Communication

| Topic | Status | Where | Notes |
|-------|--------|-------|-------|
| Alternative text versions (5 paragraphs x 3 versions) | DONE | `alternatives.tex` (reference file) | Available for final polish |
| Focus area redirect (R06) detail | DONE | `focus_and_repulsive.tex` appendix | PLB logic + repulsive field equations |

---

## ITEMS STILL MISSING OR NEEDS IMPROVEMENT

### CRITICAL (do before submission)

| # | Item | Status | Impact | Action |
|---|------|--------|--------|--------|
| 1 | **Real photos** (drone, bench, dashboard, field) | MISSING | +2-3 Communication score | Take photos, replace placeholder fbox in figure_descriptions.tex |
| 2 | **Ground station screenshot** | MISSING | +2 Communication, evidences R10 | Run pi_flight.py in SIMULATION, screenshot browser |
| 3 | **Inconsistent search speed** (5/8/10 m/s across sections) | NEEDS FIX | Credibility | Standardise to "altitude-dependent, ~8 m/s nominal at 35m" everywhere |
| 4 | **Two FOV values** (49.3 Pi vs 54.4 DJI) not distinguished | NEEDS FIX | Credibility | Label every instance: "DJI video" vs "IMX296 Pi camera" |
| 5 | **Broken citation** `rtca_do178c` | NEEDS FIX | Compilation | Add to references.bib |
| 6 | **Broken cross-refs** (sec:detection, sec:target-localisation) | NEEDS FIX | Compilation | Fix label names to match defined labels |

### HIGH PRIORITY (significant score impact)

| # | Item | Status | Impact | Action |
|---|------|--------|--------|--------|
| 7 | **Detection montage figure** (4-6 altitude frames) | MISSING | +1 Specialist Skills (R05/R10 evidence) | Generate from DJI video |
| 8 | **Exec summary** doesn't mention weather pivot or adaptation | NEEDS IMPROVEMENT | +0.5 Communication | Add 1 sentence about field day pivot |
| 9 | **R06 verification thin** -- no quantitative evidence | NEEDS IMPROVEMENT | +0.5 Specialist Skills | Add redirect timing or pattern-shift figure |
| 10 | **R07 verification** -- no visual | NEEDS IMPROVEMENT | +0.5 Specialist Skills | Add landing offset diagram or simulation scatter |
| 11 | **GPS error budget** only in appendix | PARTIAL | +1 Specialist Skills | Pull 1-paragraph summary into body |
| 12 | **Five-tier table** only in appendix | PARTIAL | +1 Specialist Skills | Add condensed version or explicit cross-ref in body |
| 13 | **Footprint width** R05: "27.6m" should be "32.2m" at 35m | NEEDS FIX | Accuracy | Fix number |
| 14 | **Sheridan level inconsistency** (R08 "Level 2" vs Design Rationale "Level 5/3") | NEEDS FIX | Credibility | Standardise to "Level 5 search / Level 3 landing" |
| 15 | **extra_refs.bib** not loaded or merged | NEEDS FIX | Broken citations | Add \addbibresource or merge into references.bib |

### MEDIUM PRIORITY (polish, +0.5 each)

| # | Item | Status | Impact | Action |
|---|------|--------|--------|--------|
| 16 | "What would change" subsection in Evaluation | MISSING | +1 Decision Making | Prioritised table: NCNN, FP16, GPS lag compensation, multi-class, real test set |
| 17 | Sim-to-real confidence statement | MISSING | +0.5 Specialist Skills | 2-3 sentences quantifying what sim validates vs what it can't |
| 18 | Docker Pi test as Tier 2.5 evidence | NOT MENTIONED | +0.5 Specialist Skills | 1 sentence in Evaluation or System Description |
| 19 | Dashboard mention (React project tracker) | NOT MENTIONED | +0.5 Communication ("innovative technique") | 1 sentence in Introduction or Evaluation |
| 20 | MCDA authenticity sentence | MISSING | +0.5 Decision Making | "Initially selected X, trade study revealed Y" |
| 21 | Waypoint count inconsistency (exec summary "18" vs "35 across 5 passes") | NEEDS FIX | Accuracy | Verify and make consistent |
| 22 | Module names in system_description (gps_utils.py, geofence.py) don't match real code | NEEDS FIX | Accuracy | Update to real filenames (utils.py, main.py geofence section) |
| 23 | Duplicate appendix letter "R" (centering_analysis + figure_descriptions) | NEEDS FIX | Professionalism | Rename figure_descriptions to "T" or later letter |
| 24 | Verify "58 test scripts" claim | UNVERIFIED | Accuracy | Count files in tests/ |
| 25 | ArduPilot citation (used throughout, never cited) | MISSING | +0.5 Communication | Add to references.bib |
| 26 | Iterative model training narrative (3 rounds with specific metrics) | PARTIAL | +0.5 Decision Making | P1 says "swapped three times" but no per-round detail in body |

---

## SUMMARY STATISTICS

| Metric | Count |
|--------|-------|
| Body sections in main.tex | 4 (+ 2 excluded) |
| Appendix sections in main.tex | 32 |
| Orphaned sections (not compiled) | 13 |
| Total .tex files | 50 |
| PDF figures in figs/ | 30 |
| PNG figures in figs/ | 30 (includes duplicates + real_ outputs) |
| JPG figures in figs/ | 1 (real_dry_run_pattern) |
| Figures in body | 16 (in 8 figure environments, some subfigures) |
| Figures still missing (need photos) | 8 (2 CRITICAL, 2 HIGH, 4 MEDIUM) |
| Tables in body | 10 |
| Tables in appendices | ~45 |
| Equations in body | 3 (most are in appendices by design) |
| Equations in appendices | ~50+ |
| Critical fixes remaining | 6 |
| High-priority items remaining | 9 |
| Medium-priority items remaining | 11 |

---

## SCORE ESTIMATE

**Current: ~80 (range 78-83)**

| Criterion | Weight | Current | With fixes | Notes |
|-----------|--------|---------|------------|-------|
| Specialist Skills & Problem-Solving | 40% | ~80 | 85 | Strong: MCDA, progressive testing, quantitative figures. Gap: no real photos, some inconsistencies |
| Decision Making | 40% | ~78 | 84 | Strong: 4 MCDA tables, honest delta, weather adaptation. Gap: no "what would change", some inconsistencies |
| Communication | 20% | ~78 | 85 | Strong: 16 body figures, dense tables. Gap: NO real photos (critical), no dashboard screenshot |

**After all critical+high fixes: ~84 (range 82-87)**
**After all fixes including medium: ~86 (range 84-88)**

The single biggest score lever is **real photos** (drone, dashboard, bench). Second is **fixing all inconsistencies** (speed, FOV, Sheridan level, cross-refs). Third is **pulling key appendix content into body** (error budget, five-tier table).
