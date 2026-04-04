# Figure Brainstorm -- High-Impact Additions to Goldmine Report

Generated: 2026-04-03
Goal: Identify figures that would make markers say "wow" -- demonstrating rigour, real data, and engineering maturity.

---

## Current Figure Inventory (52 PDFs in figs/)

### Already Included in Body (~24 figures):
- `mission_overview` -- annotated site map with search polygon
- `architecture` -- system block diagram
- `pi_system` -- Pi hardware connections
- `cv_pipeline` -- detection pipeline flowchart
- `geofence_diagram` -- 4-panel NFZ enforcement
- `state_machine` -- full state machine diagram
- `gps_bullseye` + `gps_error_direction` -- GPS accuracy scatter
- `coverage_vs_time` -- search coverage progression
- `mission_timeline` -- mission phase timeline
- `coupling_matrix` -- parameter coupling heat map
- `altitude_speed_tradeoff` -- dual-axis trade-off
- `conf_vs_alt` -- confidence vs altitude
- `det_vs_speed` -- detection rate vs speed
- `latency_breakdown` -- inference pipeline timing
- `detection_heatmap` -- detection spatial density
- `confusion_matrix` + `training_curves` -- ML training
- `n2_diagram` -- N2 interface diagram
- `tornado_sensitivity` -- sensitivity tornado
- `pareto_2d_composite` + `pareto_curve` + `pareto_3d` + `pareto_parallel` -- Pareto fronts
- `energy_efficiency` -- energy vs config
- `top3_paths` -- top 3 configuration comparison
- `sensitivity_matrix` + `sensitivity_spider` -- sensitivity analysis
- Various `real_*` plots in appendices (14 data-driven figures)

### Commented Out / Missing (gaps identified in SCORING_D6_v5):
- `hardware_block_diagram` -- commented out in 03_hardware_platform.tex
- `dashboard_screenshot` -- commented out in 08_ground_station.tex
- `gps_scatter` -- commented out in 07_target_localisation.tex (gps_bullseye used instead)
- `state_machine_diagram` -- commented out in 06 (state_machine_full used instead)

---

## TIER 1: HIGHEST IMPACT -- "Must Add" (directly address scoring weaknesses)

### 1. Hardware Photograph with Callout Annotations
**Impact on marks: 5/5** | Feasibility: Requires real photo | Section: system_description.tex

The #1 recommendation from EVERY scoring review. An annotated photo of the assembled drone showing Pi 5, IMX296 camera, Cube Orange, GPS module, battery, and telemetry radio. Even a bench photo with labelled arrows transforms the System Description from "text about hardware" to "proof of hardware."

If no clean photo exists from field day, alternatives:
- Take one now (bench setup, no props needed)
- Create a professional 3D-style annotated block diagram showing physical layout (not just logical connections)
- Annotate a top-down photo of the Pi with camera ribbon cable

**Why it matters:** Reviewers want to SEE the thing you built. Every commercial SAR paper leads with a photograph. Its absence is conspicuous.

---

### 2. Ground Station Browser Screenshot
**Impact on marks: 4/5** | Feasibility: Easy -- run pi_flight.py in SIMULATION, screenshot browser | Section: system_description.tex

Screenshot of http://localhost:8090 showing:
- MJPEG video stream with detection overlay
- GPS grid with target clusters
- Command buttons (Y/N/M/L etc.)
- Telemetry readout (altitude, mode, GPS)

Run `python pi_flight.py` in simulation mode on laptop, open browser, screenshot. 5 minutes.

**Why it matters:** The text describes a sophisticated ground station UI. Showing it is worth more than 200 words describing it.

---

### 3. Detection Montage at Multiple Altitudes
**Impact on marks: 5/5** | Feasibility: Easy -- extract from video_test.py output | Section: evaluation.tex or cv_extended.tex

A 2x2 or 1x4 grid of detection screenshots from DJI video at:
- 15m altitude (large target, high confidence)
- 25m altitude (medium target)
- 35m altitude (design altitude, still detected)
- 50m altitude (detection ceiling, marginal)

Each panel annotated with: altitude, confidence score, bounding box size in pixels, GSD.

**gen_ script:** Extract frames from `video_test.py` at known altitudes using SRT telemetry, overlay bounding box + text, compose into subfigure grid.

**Why it matters:** This is THE visual proof that the CV system works. Currently the report has numbers (mAP50=0.995, conf=0.966) but never shows a single detection image. Markers need to see the green bounding box on the orange dummy.

---

### 4. FOV Geometry / Detection Probability Diagram
**Impact on marks: 4/5** | Feasibility: Easy TikZ or matplotlib | Section: requirements_verification.tex

Side-view diagram showing:
- Drone at altitude h with camera cone
- Ground footprint width W = 2h*tan(HFOV/2)
- Lane spacing = W * (1 - overlap)
- Target on ground with "detection zone" shaded
- Multiple passes shown with overlap region highlighted
- Annotated: "N_eff = 1.0 independent observations per pass" with visual explanation of WHY overlap reduces effective N

This directly supports the correlation-aware N_eff derivation that reviewers called "genuinely sophisticated." Making it visual cements understanding.

**Why it matters:** The detection probability calculation is one of the strongest technical contributions. A diagram makes it accessible and memorable.

---

## TIER 2: HIGH IMPACT -- "Should Add" (demonstrate additional rigour)

### 5. Error Budget Waterfall Chart
**Impact on marks: 4/5** | Feasibility: Easy gen_ script | Section: system_description.tex (near error budget table)

Horizontal waterfall/cascade chart showing each error source stacking:
```
GPS receiver:   3.0m  ||||||||
Attitude tilt:  0.8m  ||
FOV cal:        0.5m  |
Pixel quant:    0.3m  |
GPS timing lag: 1.0m  |||
Wind gust:      1.5m  ||||
                ──────────────
RSS Total:      3.6m  (not arithmetic sum)
```

Two bars at bottom: "Arithmetic sum: 7.1m" vs "RSS (independent): 3.6m" -- visually demonstrates WHY RSS is appropriate and conservative.

**gen_ script:** Simple matplotlib horizontal bar chart with cumulative + RSS comparison. Data already in error budget table.

**Why it matters:** Tables of numbers are forgettable. A waterfall chart is immediately understood and shows the engineering judgement of using RSS propagation.

---

### 6. Progressive Testing Coverage Ladder
**Impact on marks: 4/5** | Feasibility: Easy gen_ script | Section: evaluation.tex

Stacked/stepped diagram showing the 5-tier testing framework:
```
Tier 5: Full Autonomous Mission      [0% -- not reached]
Tier 4: Auto Search + CV Logging      [0%]
Tier 3: Manual Flight + Passive CV    [0%]
Tier 2: Waypoint Flight (no CV)       [0%]
Tier 1: Bench (no props)              [100% -- 12 bugs caught here]
Tier 0: Simulation                    [100% -- full mission end-to-end]
```

Each tier shows: requirements verified (R01-R12 mapping), bugs caught at that tier, and a "gate" arrow showing "must pass before advancing."

Annotated callout: "71 test scripts across 6 categories" and "12 defects caught at Tier 1 alone, including geofence sign inversion."

**Why it matters:** Transforms the testing narrative from "we tested things" to a visible progression methodology. The fact that 12 bugs were caught at bench tier (before any flying) is a strong safety argument.

---

### 7. Mission Timeline with State Colours (Enhanced)
**Impact on marks: 3/5** | Feasibility: Already exists, needs enhancement | Section: system_description.tex

The current `mission_timeline` exists but could be enhanced to show:
- Coloured blocks for each state (SEARCH=blue, CENTERING=yellow, VERIFY=orange, LANDING=green)
- Time axis with actual durations from simulation
- Key events annotated (first detection, GPS lock, operator confirm, touchdown)
- RC override window highlighted (manual takeover at any time)

**Why it matters:** Shows the temporal flow of a mission in a way the state machine diagram cannot. Reviewers see both the topology (state machine) and the chronology (timeline).

---

### 8. Centering Convergence Plot (CEP vs Time)
**Impact on marks: 4/5** | Feasibility: Medium -- needs data from simulation log or synthetic | Section: evaluation.tex or system_description.tex

Line plot showing:
- X-axis: time since first detection (seconds)
- Y-axis: CEP (Circular Error Probable) in metres
- Line drops from initial ~16m scatter down to <1m as Kalman filter fuses observations
- Vertical dashed lines at key events: "Switch to CENTERING", "GPS lock achieved", "VERIFY"
- Shaded region showing 95% confidence interval

Could include two lines: "Single observation" (noisy) vs "Kalman filtered" (smooth convergence).

**gen_ script:** Use DJI video test GPS estimation data (already logged in memory/gps-timing-lag.md: CEP50=2.3m, max=16.5m).

**Why it matters:** Visually demonstrates the Kalman filter and inverse-variance weighting doing useful work. Shows the system gets MORE accurate over time -- a fundamental property that separates this from a naive "detect and dive" approach.

---

### 9. System Architecture Data Flow Diagram (with rates)
**Impact on marks: 3/5** | Feasibility: Easy -- enhance existing architecture.pdf | Section: system_description.tex

Enhanced version of the architecture block diagram with data flow rates on each edge:
```
Camera (13 FPS) --> Vision (4.8 FPS) --> State Machine (1 Hz) --> MAVLink (10 Hz) --> Cube
                                              |
                                    GPS Estimator (4.8 Hz)
                                              |
                                    Kalman Filter --> Target DB
                                              |
                                    Ground Station (MJPEG 10 FPS, 300ms latency)
```

**Why it matters:** Shows that you understand the pipeline throughput, bottlenecks (inference is the limiting factor), and how different subsystems operate at different rates.

---

### 10. Before/After Lens Undistortion Comparison
**Impact on marks: 3/5** | Feasibility: Easy -- use calibration_data.npz output | Section: cv_extended.tex (appendix)

Side-by-side image showing raw vs undistorted frame from IMX296 camera. Overlay a grid to make distortion visible. Include RMS=0.399 annotation.

Even if distortion is minimal (IMX296 is a global shutter with low distortion), showing you measured and corrected it demonstrates thoroughness.

**Why it matters:** Shows calibration rigour. Even the null result ("distortion is 0.4px RMS, negligible") proves you checked.

---

## TIER 3: MEDIUM IMPACT -- "Nice to Have" (polish and depth)

### 11. Precision-Recall Curve
**Impact on marks: 3/5** | Feasibility: Medium -- needs model inference on test set | Section: evaluation.tex

Standard ML figure. Sweep confidence threshold 0.1-0.9, plot precision vs recall. Mark the operating point (0.4 threshold) with annotation explaining the choice.

Include mAP50 and mAP50-95 on the plot.

**gen_ script:** Run inference on dataset_v2 validation set, compute PR at each threshold.

**Why it matters:** Standard ML reporting that reviewers expect. Its absence is noted in SCORING_D6_v5. Directly justifies the 0.4 confidence threshold choice.

---

### 12. MCDA Sensitivity Spider/Tornado per Table
**Impact on marks: 3/5** | Feasibility: Easy gen_ script | Section: design_rationale.tex

For each of the 5 MCDA tables, a small sensitivity analysis:
- Vary each weight by +/-20%
- Show whether the winner changes
- Could be a simple bar chart or a single summary table

Even a single figure showing "Winner robust across all 5 MCDA tables under +/-20% weight perturbation" would be powerful.

**Why it matters:** Directly addresses the #3 improvement recommendation from SCORING_D6_v5. Transforms MCDA from "we picked scores" to "our selection is robust."

---

### 13. Wiring / Physical Layout Diagram
**Impact on marks: 3/5** | Feasibility: Easy TikZ | Section: system_description.tex

Block diagram showing physical connections (not just logical):
- Pi 5 <--USB-C power--> PDB
- Pi 5 <--UART /dev/ttyAMA0 921600--> MAVProxy <--UDP 14550--> main.py
- Pi 5 <--ribbon cable--> IMX296
- Cube <--telemetry 5762--> Mission Planner (laptop)
- RC receiver <--PPM/SBUS--> Cube
- GPS module <--I2C--> Cube

**Why it matters:** Fills the "wiring diagram" gap noted in system_description review. Shows the physical architecture that the software architecture runs on.

---

### 14. Search Pattern with NFZ Avoidance Overlay
**Impact on marks: 3/5** | Feasibility: Easy -- enhance dry_run_pattern | Section: path_optimization or design_rationale

Satellite map overlay showing:
- Search polygon (yellow)
- SSSI no-fly zone (red, hatched)
- 30m buffer zone (orange dashed)
- Lawnmower pattern with filtered waypoints (blue lines)
- Rejected waypoints inside NFZ (red X marks)
- Start/end points annotated

**gen_ script:** Already have `real_dry_run_pattern.jpg` and `real_optimal_pattern.png`. Enhance with NFZ overlay.

**Why it matters:** Visually proves the geofence actually works, waypoints are filtered, and the buffer is maintained. One image replaces paragraphs of text.

---

### 15. Dual-Backend Inference Comparison Bar Chart
**Impact on marks: 2/5** | Feasibility: Easy -- data exists in benchmarks.md | Section: inference_architecture.tex

Grouped bar chart:
```
            TFLite    NCNN     Ultralytics
Latency:    207ms     72ms     --
FPS:        4.8       9.0      15.0 (GPU)
Model Size: 3.2MB     3.2MB    22MB
Platform:   Pi CPU    Pi CPU   Laptop GPU
```

**Why it matters:** Quantifies the architecture's flexibility. Shows that the dual-backend design isn't just theoretical.

---

### 16. GSD (Ground Sample Distance) vs Altitude Chart
**Impact on marks: 2/5** | Feasibility: Easy calculation | Section: cv_extended.tex

Line plot:
- X: altitude (5-60m)
- Y1: GSD in mm/pixel
- Y2: dummy size in pixels (secondary axis)
- Horizontal line at "minimum detectable size" (~20px for YOLOv8n)
- Shaded region: "operational envelope" where detection is feasible

Derived from: GSD = (altitude * sensor_width) / (focal_length * image_width)

**Why it matters:** Provides the theoretical foundation for the detection envelope. Connects camera physics to detection capability.

---

### 17. Kalman Filter State Estimation Diagram
**Impact on marks: 2/5** | Feasibility: Easy TikZ | Section: gps_estimation_deep.tex (appendix)

Block diagram showing:
```
Detection (pixel coords) --> Geo-projection --> Raw GPS estimate
                                                      |
                                                      v
Drone GPS + Altitude + Heading -----------------> Kalman Filter --> Fused estimate
                                                      ^
                                              Prior state + covariance
```

With equations: prediction step, update step, Kalman gain.

**Why it matters:** The Kalman filter is mentioned in text but never visualised as a control diagram.

---

### 18. Flight Day Adaptation Evidence Diagram
**Impact on marks: 3/5** | Feasibility: Easy -- list/flowchart | Section: evaluation.tex

Visual showing the weather cancellation pivot:
```
PLANNED                    ACTUAL
--------                   --------
Passive flight test   -->  FOV calibration (tape measure)
Waypoint test         -->  Lens calibration (checkerboard)
Auto detect test      -->  Benchmark (3 models, all metrics)
                      -->  DJI video proxy pipeline built
                      -->  Bug: TFLite bbox coords fixed
                      -->  Bug: GPS normalisation fixed
                      -->  12 defects caught at bench tier
```

**Why it matters:** The "field day adaptation" is called out as a strength in every review. Visualising it shows "we didn't waste the day -- we maximised information yield."

---

## TIER 4: AMBITIOUS -- "Wow Factor" (if time permits)

### 19. 3D Mission Visualisation
**Impact on marks: 4/5** | Feasibility: Hard -- needs 3D matplotlib | Section: cover page or system_description

3D plot showing:
- Satellite imagery as ground texture
- Lawnmower flight path in 3D (altitude on Z)
- Detection events as red spheres along path
- Descent trajectory from search altitude to target
- NFZ boundary as a semi-transparent red wall

**Why it matters:** Instant "wow." Shows the entire mission in one figure.

---

### 20. Real-Time Pipeline Sequence Diagram (UML)
**Impact on marks: 2/5** | Feasibility: Medium -- TikZ or PlantUML | Section: appendix

UML sequence diagram showing one detection cycle:
```
Camera -> Vision: frame (13 FPS)
Vision -> Vision: resize to 640x640
Vision -> TFLite: inference (207ms)
TFLite -> Vision: [1,5,8400] tensor
Vision -> StateMachine: (found, x, y, conf)
StateMachine -> GeoTransformer: pixel_to_gps(x, y)
GeoTransformer -> KalmanFilter: raw GPS estimate
KalmanFilter -> TargetDB: fused estimate
StateMachine -> MAVLink: goto(target_lat, target_lon)
```

**Why it matters:** Shows the software is engineered, not hacked together. UML is expected in MSc engineering reports.

---

## PRIORITY RANKING (by marks-per-hour)

| Priority | Figure | Impact | Time | Marks/Hour |
|----------|--------|--------|------|------------|
| 1 | Hardware photo + annotations | 5 | 15min | Extreme |
| 2 | Detection montage (4 altitudes) | 5 | 30min | Very High |
| 3 | Ground station screenshot | 4 | 10min | Very High |
| 4 | FOV geometry diagram | 4 | 45min | High |
| 5 | Error budget waterfall | 4 | 30min | High |
| 6 | Testing ladder diagram | 4 | 30min | High |
| 7 | Centering convergence plot | 4 | 60min | High |
| 8 | PR curve | 3 | 45min | Medium |
| 9 | NFZ avoidance overlay | 3 | 30min | Medium |
| 10 | MCDA sensitivity summary | 3 | 30min | Medium |
| 11 | Wiring diagram | 3 | 30min | Medium |
| 12 | Data flow with rates | 3 | 30min | Medium |
| 13 | Flight day adaptation | 3 | 20min | Medium |
| 14 | Lens undistortion before/after | 3 | 20min | Medium |
| 15 | GSD vs altitude | 2 | 20min | Medium |
| 16 | Backend comparison bars | 2 | 15min | Medium |
| 17 | 3D mission visualisation | 4 | 120min | Low |
| 18 | UML sequence diagram | 2 | 60min | Low |

---

## RECOMMENDED BATCH (4-6 figures, ~3 hours, maximum mark impact)

If you have 3 hours, do these in order:

1. **Hardware photo** (15min) -- take a bench photo, annotate in PowerPoint/Inkscape
2. **Ground station screenshot** (10min) -- run pi_flight.py, screenshot browser
3. **Detection montage** (30min) -- extract 4 frames from video_test.py at known altitudes
4. **Error budget waterfall** (30min) -- gen_error_waterfall.py
5. **FOV geometry diagram** (45min) -- gen_fov_geometry.py or TikZ
6. **Testing ladder** (30min) -- gen_testing_ladder.py

Expected improvement: Communication +4-6 points (80 -> 84-86), pushing overall from 84.0 to **86-88**.

The key insight: the report is data-rich but visually sparse on "proof of existence" images. The first three items are photographs/screenshots, not generated charts. That's where the biggest gap is.

---

## FIGURES THAT WOULD NOT HELP (avoid these)

- More Pareto plots (already have 5 variants)
- More sensitivity plots (already have tornado + spider + matrix)
- Abstract conceptual diagrams without data
- Gantt charts (not relevant to D6 technical content)
- Additional state machine variants (already have 3: simple, full, state_machine)
- More energy model plots (already have energy_efficiency + energy_heatmap + energy_vs_altitude)
