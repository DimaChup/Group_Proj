# Visualization Opportunities for D6 Goldmine Report

Audit of all `.tex` files in `report/sections/`. Each entry describes data currently
presented as text or tables that would communicate more effectively as a chart or figure.

---

## TOP 5 HIGHEST-IMPACT VISUALIZATIONS (Communication Score)

These five items would most improve the Communication rubric mark because they replace
dense numeric tables with instantly graspable visuals in the **main body** sections
that every reader encounters.

### 1. Cost Comparison Bar Chart (03_hardware_platform.tex)

**What data exists:** The BOM table (Tab. hw-bom) lists 11 components totalling ~565 GBP.
The text also compares against DJI Matrice 30T (~5,800 GBP) and Matrice 350 RTK
(~12,000+ GBP).

**Best chart type:** Horizontal stacked bar chart showing component cost breakdown for
"This Project" vs single bars for each commercial platform, with a 10x cost line
annotation.

**Why visual is better:** The 10x cost difference is the project's headline value
proposition. A bar chart communicates this in one glance; the current text buries it
in a paragraph. Readers will remember a visual "our drone costs 1/10th" far more than
a sentence.

**Matplotlib:** Yes, straightforward. Data is all in the .tex file.

---

### 2. Defect Discovery Tier Waterfall / Stacked Bar (10_testing.tex, evaluation.tex)

**What data exists:** 12 defects caught at Tiers 1-3 with resolution times. Tab.
stress-results lists 20 failure scenarios (11 first-pass, 9 fixed). Tab. param-tuning
lists 6 configuration corrections. The evaluation section (P3) summarizes: 5 at Tier 1
(1.5 hr), 6 at Tier 2 (4.7 hr), 1 at Tier 3 proxy.

**Best chart type:** Two-panel figure:
- Left: Stacked bar showing defect count by tier (Tier 1 = 5, Tier 2 = 6, Tier 3 = 1)
  colored by severity (mission-critical vs cosmetic).
- Right: Estimated cost comparison (minutes at each tier vs hypothetical hours/crashes
  if discovered in flight).

**Why visual is better:** "80% of bugs caught before flight" is the testing section's
key message. A visual showing the steep cost gradient from simulation to flight makes
the progressive methodology argument instantly compelling. Currently buried in paragraphs
across three sections.

**Matplotlib:** Yes. Data is all explicit in the text.

---

### 3. SAR System Comparison Table as Grouped Bar Chart (evaluation.tex)

**What data exists:** Tab. sar-comparison compares 5 systems across Platform, Detector,
FPS (4.8 to 30), mAP50 (0.78 to 0.995), GPS accuracy, and cost. The radar chart
(Fig. radar_comparison) already exists but is a separate concept -- the raw numeric
comparison in the table is what needs visualizing.

**Best chart type:** Grouped bar chart with 5 systems on x-axis, clustered bars for
FPS (left y-axis, log scale) and mAP50 (right y-axis). Annotate each cluster with
platform cost. OR: a scatter plot with FPS on x-axis, mAP on y-axis, bubble size = cost.

**Why visual is better:** The table forces the reader to mentally compare 5 rows and
6 columns. A scatter/bubble plot instantly shows the project sits in a unique
"low-cost, high-accuracy, moderate-speed" quadrant that no competitor occupies.

**Matplotlib:** Yes. Five data points, three dimensions.

---

### 4. GPS Estimation Accuracy Progression (07_target_localisation.tex, estimation_evaluation.tex)

**What data exists:** Tab. ground-truth-results compares 7 estimation strategies with
CEP50 from 5.1m (single frame) down to 1.5m (multi-pass IVW). Tab. localisation-accuracy
in the main body has CEP50=2.3m, CEP95=8.5m, max=16.5m.

**Best chart type:** Horizontal bar chart showing CEP50 for each strategy (single frame,
rolling avg, cumulative weighted, Kalman, IVW/SMART, hover-lock, multi-pass), with the
GPS noise floor drawn as a vertical dashed line. Color-code by "implemented" vs
"available but not deployed."

**Why visual is better:** The progressive improvement from 5.1m to 1.5m is the
localization section's narrative arc. Currently it's a table that requires row-by-row
reading. A descending bar chart with the GPS floor line tells the story at a glance.

**Matplotlib:** Yes. Seven data points from Tab. ground-truth-results.

---

### 5. Dataset Composition Pie/Donut Chart (12_model_training.tex)

**What data exists:** Tab. data_composition: 300 synthetic (81.9%), 16 real (4.4%),
50 negative (13.7%) = 366 total. Also v1 vs v2 comparison in Tab. training_results
(mAP50 ~0.95 vs 0.995) and Tab. model_generations (3 generations).

**Best chart type:** Two side-by-side donuts:
- Left: v1 dataset (200 synthetic, 0 real, 0 negative) -- simple circle.
- Right: v2 dataset (300 syn, 16 real, 50 neg) -- three segments.
Below each donut: mAP50 value in large text. Arrow connecting them saying "mixed
sources + negatives."

**Why visual is better:** The training narrative is "we went from pure synthetic to
mixed-source and the results improved dramatically." A before/after donut with a big
mAP number makes this memorable. The current tables require cross-referencing two
separate sections.

**Matplotlib:** Yes, trivial.

---

## ADDITIONAL VISUALIZATION OPPORTUNITIES (by section)

### 01_introduction.tex

**VIZ-6: Coverage Rate Comparison (ground team vs drone)**
- Data: Ground team 0.1-0.5 km2/hr, drone at 30m ~0.6 km2/hr, order of magnitude
  improvement per searcher.
- Chart: Simple bar or pictogram showing "10 ground searchers" vs "1 drone" covering
  equivalent area.
- Why: The motivation paragraph states the key advantage but a visual would anchor it.
- Matplotlib: Yes.

### 02_system_architecture.tex

**VIZ-7: Module Lines-of-Code Breakdown**
- Data: 11 modules totalling ~4,400 LOC. config.py=267, vision.py=651, planning.py=335,
  gps_utils.py=177, utils.py=170, geofence.py=327, navigation.py=149,
  stream_server.py=494, state_machine.py=943, main.py=823, states.py=22.
- Chart: Treemap or horizontal bar chart, color-coded by layer (config, independent,
  domain, orchestration).
- Why: Shows relative complexity of each module. Currently buried in prose.
- Matplotlib: Yes (squarify package for treemap, or simple barh).

### 04_computer_vision.tex

**VIZ-8: Three-Backend Decision Flow**
- Data: Three backends (NCNN, Ultralytics, TFLite) with priority chain and auto-selection.
- Chart: Flowchart/decision tree. Not a data chart but a process diagram.
- Why: The priority chain is described in an enumerated list but a flowchart with
  "installed? yes/no" decision nodes is faster to parse.
- Matplotlib: No -- better as a TikZ diagram or hand-drawn.

### 05_path_planning.tex

**VIZ-9: Altitude vs Energy Trade-off (216-config sweep)**
- Data: 6 altitudes x 36 angles = 216 configurations. Key finding: energy roughly
  doubles at 20m vs 50m. Transit vs search split is 80/20 at 35m. NFZ adds ~45% time
  penalty.
- Chart: Line plot showing total energy vs altitude (with speed overlay), OR heatmap
  of energy vs (altitude, scan angle).
- Why: The 216-configuration parametric sweep is a significant engineering contribution
  but is communicated only through bullet points. A heatmap would be visually striking.
- Matplotlib: Yes. Script exists at `analysis/path_optimization/optimize_path.py`.

**VIZ-10: Strip Spacing / Footprint vs Altitude**
- Data: At 20m footprint=18.4m, at 35m footprint=32.2m, at 50m footprint=46.0m. Lane
  width with 20% overlap correspondingly varies.
- Chart: Dual-axis line: footprint width (left axis) and number of scan lines (right
  axis) vs altitude.
- Why: The relationship between altitude, footprint, and scan count is central to the
  planning trade-off. Currently only shown in equations.
- Matplotlib: Yes.

### 06_state_machine.tex

**[ALREADY HAS: state_machine figure (Fig. state_machine)]**

No major visualization gaps. The state transition table (Tab. transitions) is
appropriate as a table. The dispatch code snippet is appropriate as code.

### 07_target_localisation.tex

**VIZ-11: Error Source Pie/Tornado**
- Data: Tab. error-budget-relative: GPS noise 60-70%, attitude 15-25%, GSD 5-10%,
  timing lag 5-10%, focal length 2-3%, lens distortion 1-2%.
- Chart: Already has waterfall (Fig. error_waterfall) and breakdown (Fig.
  error_budget_breakdown) in estimation_evaluation.tex. Main body could use a simplified
  pie chart.
- Matplotlib: Yes.

**[PLACEHOLDER FIGURE DETECTED: Fig. gps-scatter]**
- Line 128: `\textit{[Placeholder: GPS scatter plot showing individual estimates...]}`.
  This is a critical missing figure. The bullseye scatter from estimation_evaluation.tex
  (Fig. gps-bullseye) may be the same data -- check if it can be cross-referenced or
  duplicated here.

### 08_ground_station.tex

**[PHOTO NEEDED] Fig. dashboard (line 37-41)**
- Currently a `\fbox` placeholder with text description.
- Needed: Real screenshot of the browser dashboard showing GPS grid, MJPEG stream,
  detection overlay, and command buttons.
- This is the MOST IMPORTANT missing photo in the entire report. The ground station
  is a major contribution and the placeholder box is extremely obvious to markers.
- Cannot be generated with matplotlib.

### 09_simulation.tex

**[PHOTO NEEDED] Fig. simulator (line 75-80)**
- Currently a `\fbox` placeholder.
- Needed: Screenshot of the interactive simulator's 4-panel layout (god view, camera,
  bullseye scatter, dashboard).
- High impact -- shows the simulation-first approach in action.
- Cannot be generated with matplotlib -- this is a screenshot.

### 10_testing.tex

**VIZ-12: V-Model Diagram (testing tiers mapped to V-model)**
- Data: 5 tiers mapped to component/subsystem/system verification levels. Already
  mentioned as a concept but no figure.
- Chart: Classic V-model diagram with left side (decomposition: system -> subsystem ->
  component) and right side (verification: unit test -> bench -> flight), with tier
  numbers annotated.
- Why: Would visually anchor the testing methodology narrative.
- Matplotlib: No -- better as TikZ.

### 11_field_results.tex

**VIZ-13: Before/After FOV Calibration Impact**
- Data: Tab. fov-impact (in field_day_narrative.tex): at 30m, old footprint=21.5m,
  true=27.5m, systematic error=6.0m.
- Chart: Two overlapping rectangles (old FOV vs corrected FOV) on a schematic ground
  view at 30m altitude, with the error gap highlighted.
- Why: The 22% focal length error and its 6m GPS consequence is a compelling field-day
  story. A simple diagram makes it visceral.
- Matplotlib: Yes.

### 12_model_training.tex

**VIZ-14: Augmentation Gallery / Sample Grid**
- Data: 10 augmentation types (brightness, contrast, blur, rotation, scale, etc.)
  each with parameters.
- Chart: 2x5 or 3x4 image grid showing the same base image with each augmentation
  applied. Label each panel.
- Why: Tab. augmentation lists augmentation parameters but showing them is more
  effective than describing them. This is standard in ML papers.
- Matplotlib: Yes, using subplots with actual augmented images from the dataset.

**[ALREADY HAS: training_curves (Fig. training-curves), confusion_matrix (Fig.
confusion-matrix)]**

### 13_safety_risk.tex

**VIZ-15: Geofence Layers Diagram (concentric zones)**
- Data: 5 protection layers with distances: 30m waypoint buffer, 20m speed zone,
  3m repulsive field, SSSI hard cutoff, firmware fence.
- Chart: Already has Fig. geofence_layers. BUT the risk matrix (Tab. risk-matrix) could
  be visualized as a colored heatmap instead of the current manual table.
- Matplotlib: Yes for the risk matrix heatmap.

### vision_performance.tex

**[ALREADY HAS: 5 excellent figures -- alt_vs_px, speed_vs_blur, speed_vs_frames,
coverage, detection_envelope]**

This section is the gold standard for visualization in the report. No gaps.

### estimation_evaluation.tex

**[ALREADY HAS: bullseye, bullseye_comparison, error_waterfall, error_budget_breakdown,
centrality_weighting, estimator_comparison, gps_convergence, convergence_plot,
gps_error_direction, heading_bias]**

This section is extremely well-visualized. No additional charts needed.

### evaluation.tex

**[ALREADY HAS: conf_vs_alt, det_vs_speed, latency_breakdown, detection_heatmap,
detection_montage, radar_comparison]**

Well-visualized overall.

---

## [PHOTO NEEDED] LIST

These require real screenshots or photographs that cannot be generated programmatically.

| Priority | Location | Description | Impact |
|----------|----------|-------------|--------|
| **CRITICAL** | 08_ground_station.tex, Fig. dashboard | Browser dashboard screenshot with GPS grid, video stream, detection overlay, command buttons | Highest impact. This is a placeholder box that markers WILL notice. |
| **CRITICAL** | 09_simulation.tex, Fig. simulator | Interactive simulator 4-panel screenshot (god view, camera, bullseye, dashboard) | Second highest. Major contribution shown as placeholder text. |
| **HIGH** | 07_target_localisation.tex, Fig. gps-scatter | GPS scatter plot of target estimates (may already exist as bullseye in estimation_evaluation) | Check if Fig. gps-bullseye can be reused here. |
| **HIGH** | 03_hardware_platform.tex (new) | Photo of assembled drone on bench with components labeled | Shows the hardware is real, not just a paper design. |
| **HIGH** | field_day_narrative.tex (new) | Photo of field day setup (3-terminal workflow, Pi + Cube assembled) | Demonstrates hands-on engineering. |
| **MEDIUM** | 12_model_training.tex (new) | Grid of detection examples at different altitudes from DJI video | Already partially covered by detection_montage in evaluation.tex. |
| **MEDIUM** | 10_testing.tex (new) | Screenshot of diagnostics dashboard multi-panel view | Shows the go/no-go gate tool. |
| **LOW** | 05_path_planning.tex (new) | Satellite view with lawnmower pattern overlaid (from dry-run output) | The dry_run_pattern.jpg already exists in the project root. |

---

## SUMMARY: PRIORITIZED ACTION LIST

**Batch 1 -- Matplotlib charts (highest Communication impact, 2-4 hours total):**
1. Cost comparison bar chart (VIZ-1, hardware section)
2. Defect discovery tier chart (VIZ-2, testing/evaluation)
3. GPS estimation progression bars (VIZ-4, localisation)
4. Dataset composition donuts with mAP (VIZ-5, training)
5. SAR system comparison scatter/bubble (VIZ-3, evaluation)

**Batch 2 -- Screenshots (cannot generate, must capture manually):**
1. Ground station dashboard (CRITICAL placeholder)
2. Interactive simulator 4-panel (CRITICAL placeholder)
3. Assembled drone photo
4. Field day setup photo

**Batch 3 -- Additional matplotlib charts (lower priority):**
5. Coverage rate: ground team vs drone (VIZ-6)
6. Module LOC treemap (VIZ-7)
7. Altitude vs energy heatmap (VIZ-9)
8. FOV calibration before/after (VIZ-13)
9. Augmentation sample grid (VIZ-14)

**Batch 4 -- Diagrams (TikZ or drawing tool):**
10. Three-backend decision flow (VIZ-8)
11. V-model testing diagram (VIZ-12)

---

## EXISTING FIGURES THAT ARE ALREADY GOOD

For reference, these sections already have strong visualizations and do NOT need
additional charts:

- `vision_performance.tex` -- 5 plots covering the full operating envelope
- `estimation_evaluation.tex` -- 10 figures covering every aspect of GPS accuracy
- `evaluation.tex` -- 6 figures including montage, sensitivity, latency, radar
- `06_state_machine.tex` -- state transition diagram
- `02_system_architecture.tex` -- architecture and dependency diagrams
- `04_computer_vision.tex` -- pipeline diagram
- `13_safety_risk.tex` -- geofence layers diagram
- `12_model_training.tex` -- training curves and confusion matrix
