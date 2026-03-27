# D6 Report Content Brainstorm -- Complete Inventory

> Exhaustive list of everything this report COULD contain. Use to identify gaps and pick the highest-impact items within the 15-page budget.

---

## Tables We Could Include

| # | Title | What Data | Which Section | Priority | Exists? |
|---|-------|-----------|---------------|----------|---------|
| 1 | Hardware Bill of Materials | All components, specs, costs, weights | System Description | HIGH | YES (tab:hw-bom) |
| 2 | MCDA: Companion Computer | Pi 5 vs Jetson Nano vs Jetson Orin, weighted scores | Design Rationale | HIGH | YES (tab:mcda-companion) |
| 3 | MCDA: Communication Architecture | MAVLink vs ROS vs custom, weighted scores | Design Rationale | HIGH | YES (tab:mcda-comms) |
| 4 | MCDA: Detection Model | YOLOv8n vs 8s vs SSD vs Faster-RCNN, weighted scores | Design Rationale | HIGH | YES (tab:mcda-model) |
| 5 | MCDA: Search Pattern | Boustrophedon vs spiral vs grid vs sector, weighted scores | Design Rationale | HIGH | YES (tab:mcda-search) |
| 6 | Requirements Verification Matrix | R01-R12, method, evidence, status, fidelity level | Requirements Verification | HIGH | YES (tab:req-verification) |
| 7 | Plus/Delta Review | 9 strengths, 9 weaknesses, evidence for each | Evaluation | HIGH | YES (tab:plus-delta) |
| 8 | MAVLink Commands Used | Command, purpose, when used, response expected | System Description | MEDIUM | YES (tab:mavlink-commands) |
| 9 | Team Contributions | Member, role, areas owned, % contribution | Introduction | HIGH | YES (tab:contributions) |
| 10 | Altitude-Lane Width Detection Trade-off | 4 altitudes, footprint, GSD, lane width, detection prob | System Description or Appendix | HIGH | YES (tab:alt-tradeoff) in path_tradeoffs.tex (NOT included) |
| 11 | Pipeline FPS Breakdown | 4 backends (TFLite FP32, FP16, NCNN, Ultralytics), raw vs effective FPS | Evaluation or Appendix | MEDIUM | YES (tab:pipeline_fps) in pipeline_fps.tex (NOT included) |
| 12 | CPP Algorithm Comparison | 5 algorithms: boustrophedon, spiral, spanning tree, sector, grid A* | Design Rationale or Appendix | MEDIUM | YES (tab:cpp-comparison) in 05_path_planning.tex (NOT included) |
| 13 | Search Flight Parameters | 8 params (altitude, speed, overlap, lane width, etc.) with rationale | System Description | MEDIUM | YES (tab:flight-params) in 05_path_planning.tex (NOT included) |
| 14 | Five-Tier Progressive Testing Framework | Tier, environment, what's tested, scripts, defects found | Evaluation or Req Verification | HIGH | YES (tab:five-tier) in testing appendix |
| 15 | Bug-Cost Discovery Table | Defect, tier found, fix time, projected cost if found later | Evaluation | HIGH | YES (tab:bug-cost) in testing_deep.tex, cross-referenced |
| 16 | Cost-Risk Gradient Across Tiers | Tier, cost, risk, cumulative defects, 50:1 ratio evidence | Evaluation | HIGH | YES (tab:cost-gradient) in testing_deep.tex |
| 17 | GPS Error Budget (6 sources) | Source, magnitude, mitigation, residual error | System Description | HIGH | YES (tab:error-budget) in gps_estimation_deep.tex |
| 18 | Sensor Calibration Summary | Sensor, parameter, method, before/after, error if uncalibrated | System Description or Appendix | MEDIUM | YES (tab:calibration) in calibration_deep.tex |
| 19 | State Transition Table (full) | 20 states, 32 transitions, triggers, guards, actions | Appendix | LOW | YES (tab:state-transitions) in A1_state_table.tex |
| 20 | Configuration Parameters | All config.py params, values, units, rationale | Appendix | LOW | YES (tab:config-params) in A2_config_params.tex |
| 21 | Data Augmentation Pipeline | 7 augmentation types, parameters, purpose | Appendix | LOW | YES (tab:augmentation) in 12_model_training.tex |
| 22 | Dataset Composition | 300 syn + 16 real + 50 neg, image source, resolution | System Description or Appendix | MEDIUM | YES (tab:data_composition) in 12_model_training.tex |
| 23 | Training Hyperparameters | imgsz, epochs, batch, optimizer, lr schedule | Appendix | LOW | YES (tab:training_config) in 12_model_training.tex |
| 24 | Model Training Results (v1 vs v2) | mAP50, mAP50-95, precision, recall per generation | Evaluation | MEDIUM | YES (tab:training_results) in 12_model_training.tex |
| 25 | Failure Modes and Automated Responses | Failure, detection method, response, recovery | Design Rationale or Appendix | MEDIUM | YES (tab:failure-modes) in 13_safety_risk.tex |
| 26 | Risk Register with Mitigations | Risk, likelihood, impact, mitigation, residual risk | Design Rationale or Appendix | MEDIUM | YES (tab:risk-register) in 13_safety_risk.tex |
| 27 | Stress Test Scenarios (SITL) | 20 scenarios, expected vs actual behavior | Evaluation or Appendix | LOW | YES (tab:stress-results) in 10_testing.tex |
| 28 | Pi 5 Inference Benchmark Results | Model, undistort, avg ms, FPS, detections, confidence | Evaluation | HIGH | YES (tab:benchmark-results) in 11_field_results.tex |
| 29 | Backend Comparison (TFLite vs ONNX vs NCNN) | Backend, FPS, model size, quantization, accuracy | Appendix | LOW | YES (tab:backend_comparison) in inference_architecture.tex |
| 30 | Camera Footprint at Different Altitudes | Altitude, footprint W/H, GSD, pixel-per-metre | System Description or Appendix | MEDIUM | YES (tab:footprint) in cv_extended.tex |
| 31 | Detection Performance vs Altitude | Altitude, confidence, detection rate, false positive rate | Evaluation | HIGH | YES (tab:altitude_performance) in cv_extended.tex |
| 32 | Streaming Protocol Comparison | MJPEG vs HLS vs WebRTC, latency, complexity, Pi feasibility | Design Rationale or Appendix | LOW | YES (tab:stream-protocols) in streaming_architecture.tex |
| 33 | V-Model to Five-Tier Mapping | V-model phase mapped to our tier, showing SE rigour | Appendix | MEDIUM | YES (tab:vmodel-map) in testing_deep.tex |
| 34 | Contingency Plans (MVD/Target/Stretch) | Tier, components included, mission capability | Design Rationale | MEDIUM | YES (tab:mvd, tab:target) in contingency.tex |
| 35 | Test Script-to-Requirement Mapping | Script, R01-R12 coverage, traceability | Appendix | MEDIUM | YES (tab:script-req-map) in test_scripts_guide.tex |
| 36 | GSD and Footprint at Key Altitudes | Altitude, GSD (cm/px), footprint (m), frames per flyover | Appendix | LOW | YES (tab:gsd-altitude) in gps_estimation_deep.tex |
| 37 | Simulation Validation Coverage Matrix | Feature, sim tested, bench tested, field tested | Appendix | LOW | YES (tab:sim-val-matrix) |
| 38 | Centering vs Direct Offset (20 simulated missions) | Method, mean error, max error, success rate | Appendix | LOW | YES (tab:centering-comparison) |
| 39 | Comparison with Published SAR Drones | Our system vs 5-6 published systems on key metrics | Introduction or Design Rationale | MEDIUM | NO -- data in SAR_COMPARISON.md |
| 40 | Model Retraining Progression | v1(640)->v2(1280)->v3(1088), mAP, dataset size, what changed | Evaluation | MEDIUM | NO -- data scattered |
| 41 | "What Would Change" Prioritised List | Improvement, effort (days), expected impact, priority | Evaluation | MEDIUM | NO |
| 42 | Energy/Power Budget | Component, current draw, duration, total Wh, flight time impact | Design Rationale or System Description | LOW | NO |
| 43 | Weight Budget | Component, mass (g), total, payload margin | System Description | LOW | NO -- partial in BOM |
| 44 | Communication Latency Budget | Link, latency, jitter, impact on mission | System Description | LOW | NO |
| 45 | STEEPLE Summary (7 dimensions) | Dimension, consideration, design response | Design Rationale | HIGH | YES (inline in design_rationale.tex) |
| 46 | Overlap Margin Error Budget | 3 error sources (GPS, crosswind, attitude), RSS total | System Description | MEDIUM | NO -- math in path_tradeoffs.tex |
| 47 | Detection Window Analysis | Speed, FPS, frames per footprint, cumulative detection probability | Evaluation | MEDIUM | YES (tab:frames_flyover) in cv_extended.tex |
| 48 | Per-Stage Timing Breakdown (50 runs) | Capture, undistort, resize, inference, post-process, total | Evaluation | LOW | YES (tab:pipeline_timing) in cv_extended.tex |

---

## Figures We Could Include

| # | Description | Exists? | Filename | Section | Priority |
|---|-------------|---------|----------|---------|----------|
| 1 | Fenswood site map with search polygon, SSSI, takeoff, lawnmower pattern | YES | mission_overview.pdf | System Description | HIGH |
| 2 | Software module dependency graph (config, vision, planning, main, utils) | YES | architecture.pdf | System Description | HIGH |
| 3 | Pi 5 hardware interfaces and data flow diagram | YES | pi_system.pdf | System Description | HIGH |
| 4 | 4-panel geofence: boundaries, repulsive field, waypoint correction, emergency | YES | geofence_diagram.pdf | System Description | HIGH |
| 5 | CV pipeline: capture->undistort->resize->inference->filter->rescale | YES | cv_pipeline.pdf | System Description | HIGH |
| 6 | 20-state FSM transition diagram | YES | state_machine.pdf | System Description | HIGH |
| 7 | GPS estimation error scatter with CEP50 circle | YES | gps_bullseye.pdf | System Description | HIGH |
| 8 | Directional GPS error distribution (heading-aligned elongation) | YES | gps_error_direction.pdf | System Description | HIGH |
| 9 | GPS estimate convergence over successive observations | YES | gps_convergence.pdf | System Description | HIGH |
| 10 | Estimator comparison: raw avg, inverse-variance, Kalman filter | YES | estimator_comparison.pdf | System Description | HIGH |
| 11 | Mission timeline with state transitions (coloured blocks) | YES | mission_timeline.pdf | System Description | MEDIUM |
| 12 | Detection confidence vs altitude plot | YES | conf_vs_alt.pdf | Evaluation | HIGH |
| 13 | Detection rate vs flight speed | YES | det_vs_speed.pdf | Evaluation | HIGH |
| 14 | Per-frame latency breakdown (capture, undistort, resize, inference, post) | YES | latency_breakdown.pdf | Evaluation | HIGH |
| 15 | Spatial detection density heatmap across survey area | YES | detection_heatmap.pdf | Evaluation | HIGH |
| 16 | Combined confidence + motion blur detection envelope | YES | detection_envelope.pdf | Appendix (cv_extended) | HIGH -- should be in body |
| 17 | Pixel motion blur vs altitude at different speeds/exposures | YES | blur_vs_altitude.pdf | Appendix (cv_extended) | MEDIUM |
| 18 | Coverage % vs time for different scan angles | YES | coverage_vs_time.pdf | Appendix (05_path_planning) -- ORPHANED | HIGH -- path planning has zero body coverage |
| 19 | Stacked bar: inference vs pipeline overhead per backend (TikZ) | YES (inline) | fig:bottleneck_shift in pipeline_fps.tex | NOT included | MEDIUM |
| 20 | Full state machine (alternative version) | YES | state_machine_full.pdf | Not referenced | LOW |
| 21 | Simplified state machine (alternative version) | YES | state_machine_simple.pdf | Not referenced | LOW |
| 22 | Ground station browser UI screenshot (MJPEG + GPS grid + buttons) | NO -- need to take | N/A | System Description or Req Verification | CRITICAL |
| 23 | Assembled drone photo with labelled components | NO -- need to take | N/A | System Description or Introduction | CRITICAL |
| 24 | Detection overlay frame at 35m with bounding box, confidence, scale bar | NO -- need to generate from video | N/A | Requirements Verification | HIGH |
| 25 | Lawnmower pattern overlaid on real satellite image | PARTIAL | mission_overview.pdf covers this | System Description | LOW |
| 26 | Bench test setup photo (Pi + camera + Cube + laptop + PuTTY) | NO -- need to take | N/A | Evaluation or System Description | MEDIUM |
| 27 | Detection montage: 4-6 frames at different altitudes (15m, 25m, 35m, 45m) | NO -- generate from DJI video | N/A | Requirements Verification | HIGH |
| 28 | R06 PLB redirect: before/after pattern shift | NO -- generate from simulation | N/A | Requirements Verification | MEDIUM |
| 29 | Landing position probability distribution | NO -- generate from simulation data | N/A | Requirements Verification | MEDIUM |
| 30 | Confusion matrix from training | EXISTS in cv_models/ as PNG | confusion_matrix.png | Appendix | LOW |
| 31 | Training loss curves | EXISTS in cv_models/ as PNG | results.png | Appendix | LOW |
| 32 | Mission Planner SITL connection screenshot | NO -- take | N/A | System Description | LOW |
| 33 | Rescue dummy photo on field | PARTIAL -- dummy.png exists (workshop photo) | dummy.png | Introduction | MEDIUM |
| 34 | Pi camera frame vs DJI camera frame at same altitude | NO -- generate | N/A | Appendix | LOW |
| 35 | Wiring schematic (Pi GPIO to Cube TELEM2) | NO -- draw | N/A | System Description or Appendix | LOW |
| 36 | Field day photos: team at Fenswood, outdoor equipment | NO -- need from team | N/A | Introduction | MEDIUM |
| 37 | Model training progression (640->1280->1088 with metrics) | NO -- create | N/A | Evaluation | MEDIUM |
| 38 | Energy sweep results (power vs speed vs altitude) | NO -- derive from equations | N/A | Appendix | LOW |
| 39 | NFZ margin analysis diagram (SSSI buffer zone, repulsive field gradient) | PARTIAL -- geofence_diagram.pdf has 4 panels | geofence_diagram.pdf | System Description | MEDIUM |
| 40 | Sheridan autonomy level diagram (our system on the scale) | NO -- create | N/A | Design Rationale | LOW |
| 41 | V-model diagram mapped to our 5-tier framework | NO -- create | N/A | Evaluation or Appendix | MEDIUM |
| 42 | Payload release mechanism photo/diagram | NO -- need from team | N/A | System Description | MEDIUM |
| 43 | GitHub commit history / contributions graph | NO -- screenshot | N/A | Introduction | LOW |
| 44 | Software layer diagram (4 layers: config, independent modules, orchestration, scripts) | PARTIAL -- architecture.pdf has module graph | architecture.pdf | System Description | LOW |
| 45 | Kalman filter convergence animation/sequence | PARTIAL -- gps_convergence.pdf shows this | gps_convergence.pdf | System Description | LOW |
| 46 | IMX296 global vs rolling shutter comparison | NO -- create | N/A | Design Rationale or CV section | LOW |
| 47 | RC kill switch activation sequence diagram | NO -- create | N/A | Design Rationale or Safety | LOW |
| 48 | Simple simulator screenshot (keyboard flight + detection overlay) | NO -- take | N/A | System Description (simulation) | MEDIUM |

---

## Equations We Could Show

| # | Equation | Description | Where | Impact | Exists? |
|---|----------|-------------|-------|--------|---------|
| 1 | Camera footprint width/height | $W = 2h \tan(\theta/2)$ | System Description (path planning) | HIGH | YES (eq:footprint in 05_path_planning.tex) |
| 2 | Lane width from footprint and overlap | $w = W(1 - o)$ where $o$ is overlap fraction | System Description (path planning) | HIGH | YES (eq:lane-width in 05_path_planning.tex) |
| 3 | Ground Sample Distance (GSD) | $\text{GSD} = h \cdot s_w / (f \cdot I_w)$ | System Description (CV or GPS) | HIGH | YES (eq:gsd-deep in gps_estimation_deep.tex) |
| 4 | Pixel-to-body-frame transform | $\Delta x_b, \Delta y_b$ from pixel offset, altitude, focal length | System Description (target localisation) | MEDIUM | YES (eq:body-deep) |
| 5 | Body-to-GPS rotation (heading) | Rotation matrix from body frame to north-east | System Description (target localisation) | MEDIUM | YES (eq:rotation-deep) |
| 6 | GPS coordinate conversion (metres to lat/lon) | $\Delta\text{lat} = \Delta y / R$, $\Delta\text{lon} = \Delta x / (R \cos\phi)$ | System Description (target localisation) | MEDIUM | YES (eq:wgs84-deep) |
| 7 | Rolling average estimator | $\hat{p}_n = \alpha p_n + (1-\alpha)\hat{p}_{n-1}$ | System Description (GPS estimation) | LOW | YES (eq:rolling) |
| 8 | Cumulative weighted average | $\hat{p} = \sum w_i p_i / \sum w_i$ | System Description (GPS estimation) | MEDIUM | YES (eq:cumulative) |
| 9 | Kalman filter measurement noise from altitude | $R = R_0 (h/h_{\text{ref}})^2$ | System Description (GPS estimation) | MEDIUM | YES (eq:kalman-R-deep) |
| 10 | Kalman predict/update equations | Standard KF predict + update with altitude-dependent R | System Description (GPS estimation) | HIGH | YES (align block in gps_estimation_deep.tex) |
| 11 | Inverse variance weighting | $w_i = 1/\sigma_i^2$ | System Description (GPS estimation) | MEDIUM | YES (eq:weight-deep) |
| 12 | Altitude-dependent weight | $w \propto 1/h^2$ | System Description (GPS estimation) | MEDIUM | YES (eq:alt-weight) |
| 13 | Haversine distance formula | Great-circle distance between GPS coordinates | System Description or Appendix | LOW | YES (eq:haversine) |
| 14 | Bezier curve for U-turn smoothing | $B(t) = (1-t)^3 P_0 + 3(1-t)^2 t P_1 + \ldots$ | System Description (path planning) | LOW | YES (eq:bezier in 05_path_planning.tex) |
| 15 | Power model for speed-energy trade-off | $P(v) = P_0 + k_1 v^2 + k_2/v$ | Appendix (path planning) | LOW | YES (eq:power in 05_path_planning.tex) |
| 16 | Altitude-dependent speed schedule | $v(h) = v_{\min} + (v_{\max} - v_{\min})(h - h_{\min})/(h_{\max} - h_{\min})$ | System Description or path_tradeoffs | MEDIUM | YES (in path_tradeoffs.tex) |
| 17 | Overlap margin RSS error | $\epsilon = \sqrt{\epsilon_{\text{GPS}}^2 + \epsilon_{\text{wind}}^2 + \epsilon_{\text{att}}^2}$ | System Description (path planning) | MEDIUM | YES (in path_tradeoffs.tex) |
| 18 | GPS timing lag compensation | $\Delta\mathbf{p} = \mathbf{v} \cdot \Delta t_{\text{lag}}$ | Evaluation (D3) | MEDIUM | YES (inline in evaluation.tex) |
| 19 | Cumulative detection probability | $P_{\text{detect}} = 1 - (1-p)^n$ where $n$ = frames per flyover | System Description or Evaluation | HIGH | NO -- could derive |
| 20 | Repulsive force field (geofence) | $F_{\text{rep}} = k / d^2$ for distance $d$ to boundary | System Description (geofence) | MEDIUM | NO -- in code, not in LaTeX |
| 21 | Confidence decay with altitude | Empirical fit: $c(h) = c_0 e^{-\lambda h}$ or similar | Evaluation | MEDIUM | NO -- could fit from data |
| 22 | CEP (Circular Error Probable) | $\text{CEP}_{50} = 0.5887(\sigma_x + \sigma_y)$ | System Description (GPS) | MEDIUM | NO -- used in figures but not shown |
| 23 | SPRT (Sequential Probability Ratio Test) for detection | Could frame multi-frame detection as hypothesis test | System Description (detection logic) | LOW | NO |
| 24 | Field of View from focal length | $\text{FOV} = 2\arctan(s/(2f))$ | System Description (CV calibration) | MEDIUM | NO -- but trivial |
| 25 | SNR vs altitude for detection | Signal-to-noise model for target visibility | Appendix | LOW | NO |

---

## Analysis We Could Present

| # | Analysis | Data Source | How Convincing | Section | Priority |
|---|----------|-------------|----------------|---------|----------|
| 1 | Detection confidence vs altitude (empirical curve) | DJI flight video at 15-50m altitudes | Very convincing -- real data | Evaluation | HIGH -- EXISTS (fig:conf_vs_alt) |
| 2 | Detection rate vs flight speed | DJI video at different playback/flight speeds | Convincing -- real video | Evaluation | HIGH -- EXISTS (fig:det_vs_speed) |
| 3 | Per-frame latency breakdown (5-stage pipeline) | Pi 5 benchmark (50 runs, measured timings) | Very convincing -- hardware data | Evaluation | HIGH -- EXISTS (fig:latency_breakdown) |
| 4 | GPS estimation accuracy (CEP50, max error) | DJI video with SRT telemetry ground truth | Convincing -- real data | System Description | HIGH -- EXISTS (fig:gps_bullseye) |
| 5 | GPS estimate convergence over observations | Simulated/video multi-pass analysis | Convincing | System Description | HIGH -- EXISTS (fig:gps_convergence) |
| 6 | Estimator comparison (3 methods) | Same dataset, 3 estimation approaches | Very convincing -- controlled comparison | System Description | HIGH -- EXISTS (fig:estimator_comparison) |
| 7 | 216-configuration parametric sweep for scan angle | Algorithmic sweep varying angle, overlap, altitude | Very convincing -- systematic optimisation | System Description or Appendix | HIGH -- in orphaned 05_path_planning.tex |
| 8 | Coverage completeness vs time for different scan angles | Simulation of coverage progress | Convincing | System Description or Appendix | HIGH -- coverage_vs_time.pdf exists |
| 9 | Bug discovery cost analysis (50:1 ratio) | 12 defects tracked with tier found, fix time | Convincing -- quantitative | Evaluation | HIGH -- in testing_deep.tex |
| 10 | V-model mapping to 5-tier progressive testing | Framework design, SE literature | Moderately convincing -- design argument | Evaluation or Appendix | MEDIUM |
| 11 | Detection envelope (confidence + blur combined) | Model from video data + blur simulation | Convincing -- multi-variable | Appendix/Evaluation | HIGH -- detection_envelope.pdf exists |
| 12 | Spatial detection density across survey area | Heatmap from video analysis | Convincing -- visual evidence | Evaluation | HIGH -- detection_heatmap.pdf exists |
| 13 | Lens distortion calibration impact (before/after) | Checkerboard calibration data | Convincing -- measured | System Description | MEDIUM -- in calibration_deep.tex |
| 14 | GPS timing lag analysis (100-200ms latency) | Here 3+ receiver measurement | Convincing -- hardware data | Evaluation | HIGH -- in D3 and gps_estimation_deep.tex |
| 15 | FOV calibration from video (9 samples, cross-validated) | DJI video with known dummy size at multiple altitudes | Very convincing -- rigorous method | Appendix | MEDIUM |
| 16 | Model retraining progression (3 generations) | mAP metrics from each training round | Convincing -- iterative improvement | Evaluation | MEDIUM |
| 17 | Simulation validation (SITL vs expected behavior) | 20 stress scenarios | Moderately convincing -- no real comparison | Appendix | LOW |
| 18 | Overlap margin analysis (RSS of 3 error sources) | Analytical model from GPS/wind/attitude errors | Convincing -- mathematical | System Description | MEDIUM |
| 19 | Energy vs speed vs altitude trade-off | Analytical power model | Moderately convincing -- model only | Appendix | LOW |
| 20 | Inference speed comparison across backends | Pi 5 benchmarks for TFLite, NCNN, Ultralytics | Convincing -- measured | Appendix or Evaluation | MEDIUM |
| 21 | Cumulative detection probability over multiple frames | Probability model: $P = 1-(1-p)^n$ | Convincing -- mathematical | Evaluation | MEDIUM |
| 22 | Sensitivity analysis: what if altitude was 25m instead of 35m | Trade-off analysis using existing models | Convincing -- parametric | Evaluation | MEDIUM |
| 23 | Geofence margin analysis (how close did we get to SSSI) | Simulation data, repulsive field behavior | Moderately convincing -- sim only | System Description or Evaluation | LOW |
| 24 | Comparison of our GPS accuracy with commercial GNSS specs | Our CEP vs Here 3+ datasheet specs | Moderately convincing | Evaluation | LOW |
| 25 | Weather impact on mission capability | Field day cancellation narrative, what was gained instead | Convincing as adaptation evidence | Evaluation | HIGH -- already in body |
| 26 | Cross-platform validation (Windows/WSL/Pi) | Same test on 3 platforms, same results | Moderately convincing | Evaluation | LOW |
| 27 | Docker containerisation for reproducibility | Dockerfile.pi-test proves TFLite loads on Pi-like env | Moderately convincing -- novel approach | Evaluation | LOW |
| 28 | DJI SRT sync analysis (30fps vs 6fps mismatch) | Frame count analysis, telemetry alignment | Convincing as data integrity example | Appendix or Evaluation | LOW |

---

## Experiments We Could Describe

| # | Experiment | Real or Plausible? | What It Shows | Section | Priority |
|---|------------|-------------------|---------------|---------|----------|
| 1 | Pi 5 inference benchmark (50 runs, 206.5ms avg, 4.8 FPS) | REAL -- measured on Pi hardware | On-device inference is feasible at ~5 FPS | Evaluation | HIGH |
| 2 | FOV calibration (9 samples at 15-50m, IMX296 + DJI) | REAL -- measured in field + from video | Rigorous optical calibration methodology | Appendix or System Description | HIGH |
| 3 | Lens distortion calibration (checkerboard, RMS 0.399) | REAL -- measured on Pi | Professional calibration practice | Appendix | MEDIUM |
| 4 | DJI video detection analysis (flight at 15-50m) | REAL -- processed real flight footage through pipeline | Detection performance at realistic altitudes | Evaluation | HIGH |
| 5 | GPS estimation from video (CEP50 = 2.3m, max = 16.5m) | REAL -- computed from DJI video + SRT telemetry | Target localisation accuracy quantified | System Description | HIGH |
| 6 | 216-config scan angle parametric sweep | REAL -- algorithmic simulation | Systematic optimisation of search pattern | System Description or Appendix | HIGH |
| 7 | 20 SITL stress test scenarios | REAL -- run in SITL | Robustness testing of state machine | Appendix | MEDIUM |
| 8 | Bench day: Pi + camera + Cube integration | REAL -- field day hardware testing | Hardware integration validated | Evaluation | HIGH |
| 9 | BGR colour discovery (6 permutations tested) | REAL -- systematic debugging | IMX296 quirk found and resolved | Evaluation | MEDIUM |
| 10 | Python 3.13 compatibility investigation | REAL -- pyserial/tflite broken, alternatives found | Platform compatibility problem-solving | Design Rationale | MEDIUM |
| 11 | Model retraining v1 (640px, synthetic only) | REAL -- trained on Colab | Baseline model performance | Appendix | LOW |
| 12 | Model retraining v2 (1088px, synthetic + real + negative) | REAL -- trained on Colab, mAP50=0.995 | Improved model with real data | Evaluation | HIGH |
| 13 | Altitude sweep: detection rate vs altitude | PLAUSIBLE -- data extractable from DJI video | Detection altitude limits characterised | Evaluation | HIGH |
| 14 | Speed sweep: detection rate vs drone speed | PLAUSIBLE -- data extractable from DJI video | Speed limit for reliable detection | Evaluation | HIGH |
| 15 | GPS drift measurement (CEP50, CEP95) | PLAUSIBLE -- scripts ready, needs flight | GPS noise floor characterised | Future work | MEDIUM |
| 16 | Confidence threshold sweep (PR curve) | PLAUSIBLE -- scripts exist, needs ground truth | Optimal detection threshold found | Future work / Evaluation | MEDIUM |
| 17 | NCNN inference benchmark on Pi | PLAUSIBLE -- export exists, not benchmarked | Alternative backend speed comparison | Future work | LOW |
| 18 | Full autonomous mission (search->detect->centre->land) | PLAUSIBLE -- code ready, weather cancelled | End-to-end mission validation | Requirements Verification | HIGH -- acknowledged gap |
| 19 | Passive flight detection (manual RC, AI watches) | PLAUSIBLE -- script ready, not run | Real-world detection calibration | Future work | MEDIUM |
| 20 | Multi-pass target convergence test | PLAUSIBLE -- simulation supports this | GPS estimate improves with passes | System Description | MEDIUM |
| 21 | Payload release mechanism test | UNKNOWN -- depends on team | First aid kit deployment | Requirements Verification (R07) | HIGH |
| 22 | RTH failsafe test (RC loss, battery, link loss) | PLAUSIBLE -- ArduPilot handles this | Safety system validation | Requirements Verification (R09) | HIGH |

---

## Comparisons With Literature

| # | Our System | Published Work | Comparison Point | Reference | Impact |
|---|-----------|---------------|-----------------|-----------|--------|
| 1 | Boustrophedon with angle-aligned rotation | Choset 2001 coverage path planning | We implement their algorithm with polygon-specific optimisation | choset2001coverage | HIGH -- foundational |
| 2 | YOLOv8n TFLite on Pi 5 (4.8 FPS) | MDPI J. Imaging 2025 -- YOLOv8 on embedded | Compare FPS, mAP, model size on similar hardware | YOLOv8 embedded benchmark | HIGH |
| 3 | Single-pass lawnmower | MDPI Drones 2019 -- CPP survey | We chose simplest proven algorithm, justify vs alternatives | Survey on CPP | HIGH |
| 4 | GPS estimation with inverse variance weighting | Standard Kalman filter literature | More sophisticated than single-point, less than full SLAM | Kalman filter textbooks | MEDIUM |
| 5 | Operator-in-the-loop (Sheridan Level 3/5) | Sheridan 1992 autonomy levels | Justified by regulatory constraints (CAA BVLOS) | sheridan1992 | HIGH |
| 6 | Progressive testing (5 tiers) | Aerospace V&V standards (DO-178C, RTCA) | Rare in academic drone projects, standard in industry | DO-178C (or equivalent) | HIGH |
| 7 | 7.5m offset landing | SAR literature -- downwash risk | Addresses real SAR concern rarely discussed in academic work | SAR operations manuals | MEDIUM |
| 8 | Edge AI (Pi 5 CPU, no GPU accelerator) | AUSPEX SAR framework (Frontiers 2025) | Compare computational approach, they may use Jetson | AUSPEX framework | MEDIUM |
| 9 | Browser-based ground station (MJPEG) | ROS-based ground stations (RViz, QGC) | Simpler, works over SSH, no ROS dependency | Common practice | LOW |
| 10 | MAVLink + pymavlink (no ROS) | ROS-based academic drones | Lighter weight, direct control, less abstraction | ROS vs MAVLink literature | MEDIUM |
| 11 | Synthetic + real training data mix | Domain adaptation / sim-to-real literature | Our 300:16 ratio, domain gap acknowledgement | Transfer learning papers | MEDIUM |
| 12 | Global shutter camera (IMX296) | Most drones use rolling shutter | Eliminates motion blur artefacts, rare at this price | Camera datasheets | MEDIUM |
| 13 | TFLite vs NCNN vs Ultralytics backends | Edge AI deployment literature | Multi-backend approach for flexibility | Edge AI benchmarks | LOW |
| 14 | No thermal camera | Real SAR: FLIR + RGB dual | Acknowledged limitation, cost/weight constraint | Thermal SAR papers | MEDIUM |
| 15 | ArduPilot + Cube Orange | PX4 vs ArduPilot comparison | Industry standard, well-documented, large community | ArduPilot docs | LOW |
| 16 | Hexsoon EDU-450 platform | Commercial SAR drones (DJI M300, Matrice) | Educational platform vs professional, cost difference 100x | Equipment specs | LOW |
| 17 | Single-class detector | Multi-class person detection (COCO 80-class) | Trade-off: specialisation vs generality | Person detection surveys | MEDIUM |
| 18 | SITL-first development | Simulation-first aerospace methodology | Standard in industry, rare in academic drone projects | Aerospace development literature | MEDIUM |

---

## Things a Reviewer Might Ask

| # | Question | Where Our Answer Is | Strength of Answer |
|---|----------|--------------------|--------------------|
| 1 | Why didn't you fly the drone? | Evaluation D1: weather cancelled, rebooked | Strong -- honest, shows adaptation |
| 2 | How do you know detection works at altitude? | DJI video analysis (conf_vs_alt, det_vs_speed), bench benchmark | Strong -- real video data |
| 3 | Why YOLOv8n instead of a larger model? | MCDA table (tab:mcda-model), Pi 5 constraint, 206ms inference | Strong -- quantitative trade-off |
| 4 | Why not use ROS? | MCDA table (tab:mcda-comms), simplicity, no learning curve, direct MAVLink | Strong -- justified |
| 5 | How do you handle the SSSI no-fly zone? | 3-layer geofence (geofence_diagram.pdf), repulsive field, emergency RTH | Strong -- systematic |
| 6 | What happens if detection fails? | State machine timeouts, operator override, RTH failsafe | Strong -- multiple fallbacks |
| 7 | How accurate is your GPS estimation? | CEP50 = 2.3m from DJI video, error budget table, 3 estimation methods compared | Very strong -- quantitative |
| 8 | Why 35m search altitude? | Trade-off: footprint vs GSD vs detection confidence (tab:alt-tradeoff) | Strong -- if included |
| 9 | How did you test without flying? | 5-tier framework, SITL, bench, video analysis, Docker Pi sim | Very strong -- systematic |
| 10 | Is 4.8 FPS enough? | Frames-per-flyover analysis, cumulative detection probability, speed schedule | Medium -- needs more detail |
| 11 | Why not thermal camera? | Cost, weight, scope constraint, acknowledged limitation | Adequate -- honest |
| 12 | How do you verify R06 (PLB focus area)? | Code handles polygon redirect, simulation tested | Medium -- thin evidence |
| 13 | How do you land within 10m but not 5m (R07)? | GPS estimation + 7.5m offset calculation, statistical argument | Medium -- no flight data |
| 14 | What's the false positive rate? | Single-class detector limitation, operator verification at VERIFY state | Weak -- no empirical PR curve |
| 15 | How did you validate simulation matches reality? | 12 bugs found in testing that wouldn't show in sim, FOV recalibration | Medium -- partial |
| 16 | Why Python and not C++? | Development speed, team familiarity, 206ms inference is adequate | Strong -- practical |
| 17 | How do you handle communication loss? | ArduPilot failsafe (RTH on RC loss, link loss), timeout in state machine | Strong -- standard approach |
| 18 | What's novel about your approach? | Progressive testing, GPS estimation methods, offset landing, headless GCS | Medium -- incremental novelty |
| 19 | How much of the code did AI write? | Category 3 (selective use for software), human-designed architecture | Adequate -- policy compliant |
| 20 | How do you ensure the drone stays in the flight area (R01)? | 3-layer geofence: soft boundary, repulsive field, hard boundary with emergency RTH | Strong |
| 21 | Why 20% lateral overlap? | RSS error analysis of GPS drift + crosswind + attitude errors | Strong -- if path_tradeoffs included |
| 22 | How do you handle wind? | Altitude-dependent speed schedule, overlap margin, ArduPilot wind compensation | Medium |
| 23 | What is the minimum detectable object size? | GSD analysis at altitude, minimum pixel footprint for YOLOv8 detection | Medium -- in cv_extended.tex |
| 24 | Could this work at night? | No -- no thermal camera, acknowledged limitation | Honest |
| 25 | How do you handle multiple targets? | Spatial clustering in GPS estimation, sequential investigation in state machine | Strong -- designed for this |
| 26 | What is the total mission time? | Mission timeline figure, depends on area size, speed, detections | Medium |
| 27 | How did you manage the team? | Dashboard with 93 WBS tasks, GitHub, weekly meetings (in D7/Intro) | Medium -- mostly D7 |
| 28 | Why did you choose boustrophedon over other CPP algorithms? | CPP comparison table (tab:cpp-comparison), simplicity, verifiability, optimality | Strong -- if included |
| 29 | What happens if the dummy is in the SSSI? | System cannot detect in NFZ, acknowledged limitation | Honest -- design constraint |
| 30 | How robust is the system to different dummy appearances? | Brief notes "will be attired differently", single-class detector limitation | Weak -- acknowledged |
| 31 | Why not use a gimbal? | Fixed camera simplicity, weight, global shutter compensates | Medium -- in MCDA or design rationale |
| 32 | How do you deploy the first aid kit (R07)? | Tarot payload release mechanism, GPS-based proximity trigger | Medium -- depends on team's work |
| 33 | What is the battery life? | Not measured -- ArduPilot failsafe monitors, acknowledged gap | Weak |
| 34 | How do you handle GPS-denied environments? | Not addressed -- GPS assumed available, acknowledged limitation | Honest |
| 35 | What safety mitigations are in place? | Kill switch, operator override, geofence, RTH failsafes, progressive testing | Strong -- multiple layers |
| 36 | How does the system scale to larger search areas? | Lane count increases linearly, time proportional to area, battery is limiting factor | Medium |
| 37 | What is the TRL of this system? | TRL 4-5 (lab/bench validated), TRL 6 requires flight | Honest |
| 38 | How did STEEPLE influence your design? | 7 dimensions covered in Design Rationale with specific design responses | Strong |
| 39 | Why not use deep reinforcement learning for search? | MCDA: boustrophedon is optimal for complete coverage, RL is for adaptive search | Strong -- if CPP comparison included |
| 40 | What are the ethical implications of autonomous surveillance? | STEEPLE: ethical dimension covers privacy, data handling, operator verification | Medium |

---

## Additional Content Opportunities

### Narratives That Show "Initiative, Autonomy, and Creativity" (rubric top band)

1. **BGR colour discovery** -- systematic debugging (tested 6 channel permutations), not guessing
2. **FOV recalibration story** -- field day weather cancellation led to discovering FOV was wrong ($7.0 \to 5.46$mm), improved all downstream calculations
3. **Python 3.13 compatibility chain** -- tflite-runtime broken, discovered ai-edge-litert, pyserial broken, discovered mavproxy UDP bridge
4. **SRT sync discovery** -- 6fps video out of sync with telemetry, methodical investigation, 30fps required
5. **Simulation-first methodology** -- aerospace-standard approach applied to MSc project
6. **Docker containerisation for Pi testing** -- tested deployment environment without hardware
7. **3-generation model improvement** -- 640 baseline -> 1280 experiment -> 1088 native resolution (mAP50: baseline -> 0.995)
8. **Headless ground station** -- browser-based UI works over SSH, designed for real field conditions
9. **Weather cancellation pivot** -- turned cancelled flight into calibration + benchmarking day

### Cross-Cutting Themes for the Report

1. **Evidence-based decision making** -- every design choice backed by MCDA, benchmark, or analysis
2. **Progressive de-risking** -- simulation -> bench -> passive -> active -> autonomous
3. **Quantitative rigour** -- 14+ programmatic figures, 6-source error budget, measured not estimated
4. **Honest evaluation** -- explicitly state what wasn't tested, quantify the gap
5. **Modularity as resilience** -- swap models, platforms, backends without code changes
6. **Field adaptation** -- weather cancellation, BGR discovery, FOV recalibration show real engineering

### Things That Distinguish an 83+ Report

1. **Real photos** of hardware, setup, field -- proves it's real, not just simulation
2. **Quantitative figures from measured data** -- not sketches or diagrams
3. **Honest gaps acknowledged** with concrete next steps
4. **Cross-referenced appendices** that support body claims with depth
5. **STEEPLE that actually influenced design** (not just listed for marks)
6. **MCDA tables that show genuine trade-offs** (not post-hoc justification)
7. **Professional presentation** -- consistent formatting, proper captions, SI units
8. **Equations that are used** (not decorative) -- directly feed into design parameters
9. **Comparison with literature** -- positions work in context
10. **Testing methodology as a contribution** -- 5-tier framework is genuinely novel for MSc level
