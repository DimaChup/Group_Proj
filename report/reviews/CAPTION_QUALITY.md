# Caption Quality Audit

**Date:** 2026-04-04
**Scope:** All 278 `\caption{}` entries across 50 `.tex` files in `report/sections/`

## Methodology

Every caption was evaluated against five criteria:
1. **Descriptive** -- not just a label (e.g., "GPS scatter plot" is bad)
2. **Tells the reader what to look for** -- directs attention to the key insight
3. **Includes key numbers** where the figure/table contains quantitative data
4. **Consistent style** -- sentence case, period at end, no fragment captions
5. **Sources data** if applicable (e.g., "from DJI video replay")

## Summary

| Category | Count | Notes |
|----------|-------|-------|
| Total captions | 278 | Across 50 .tex files |
| Already strong | ~240 | Descriptive, include numbers, guide the reader |
| Fixed (weak) | 38 | Were labels or lacked insight; now improved |
| Borderline (left) | ~0 | All weak captions addressed |

## Captions Fixed (38 edits across 14 files)

### 10_testing.tex (2 fixes)
- **"Testing effort summary."** -- Added headline numbers (74 scripts, 98.7% pass rate, 80% defects caught before flight)
- **"Stress test results: 20 failure scenarios tested in SITL."** -- Added outcome split (11 first-pass, 9 required fixes)

### vision_standalone.tex (11 fixes)
- **"Model training history."** -- Added v2 mAP50 and what made it better (real frames, negatives, native resolution)
- **"YOLOv8n model specifications."** -- Added context on shared input shape, NCNN size difference
- **"IMX296 sensor and camera configuration."** -- Added global shutter benefit and resolution pipeline
- **"Inference benchmarks on Raspberry Pi 5."** -- Added TFLite config details and undistortion overhead
- **"Available model variants for deployment."** -- Added drop-in compatibility and best model mAP50
- **"Preprocessing techniques and their deployment status."** -- Added default-off rationale and latency ceiling
- **"CV inference speed improvement options for Pi 5."** -- Added baseline FPS and best option (NCNN)
- **"GPS position error from 10% focal length miscalibration."** -- Added 30m altitude context and CEP comparison
- **"Dummy size in model input space and expected detection performance."** -- Added detection floor and altitude ceiling
- **"Data augmentation techniques ranked by impact for aerial SAR."** -- Added what top two address
- **"Recommended dataset composition for single-class aerial detection."** -- Added why negatives matter

### test_scripts_guide.tex (1 fix)
- **"Calibration test scripts."** -- Added connection to GPS estimation error budget

### 03_hardware_platform.tex (1 fix)
- **"Key hardware specifications."** -- Added global shutter and baud rate significance

### 05_path_planning.tex (2 fixes)
- **"Comparison of coverage path planning algorithms."** -- Added why boustrophedon was selected
- **"Search flight parameters."** -- Added decision flow derivation reference

### testing_deep.tex (2 fixes)
- **"Test script categories and their tier coverage."** -- Added tier distribution insight
- **"Cost and risk gradient across testing tiers."** -- Added concrete cost comparison (minutes vs. days)

### intro_d6.tex (1 fix)
- **"Team member contributions by project area."** -- Added overlap/integration note

### simulation_validation.tex (1 fix)
- **"Quantitative simulation validation results."** -- Added sim-to-real gap numbers (100% to 87%, sub-metre to 2.3m)

### development_methodology.tex (4 fixes)
- **"Ten-phase development history with outcomes."** -- Added when defects were discovered
- **"Three product levels with autonomy and demonstration scope."** -- Added achievement status
- **"Progressive flight testing ladder with scripts and risk isolation."** -- Added one-risk-per-step principle
- **"Simulation vs. real hardware readiness (0--10 scale)."** -- Added average scores (7.7 vs 2.1)

### contingency.tex (4 fixes)
- **"Minimum viable deliverable: components and requirement coverage."** -- Added achievement status
- **"Target deliverable: full autonomous mission."** -- Added weather cancellation context
- **"Tier structure and verification gates."** -- Added graceful fallback principle
- **"Contingency-to-test-script mapping."** -- Added on-site verification note

### design_rationale.tex (4 fixes)
- **"MCDA: companion computer selection"** -- Added Pi 5 selection rationale
- **"MCDA: communication architecture"** -- Added MAVProxy selection rationale
- **"MCDA: detection model selection"** -- Added YOLOv8n speed/accuracy trade-off
- **"MCDA: search pattern selection"** -- Added boustrophedon dominance reason

### evaluation.tex (3 fixes)
- **"Per-frame latency breakdown"** -- Added 94% inference dominance number
- **"Spatial detection heatmap"** -- Added what clustering pattern means
- **"System performance: inference latency budget and spatial detection distribution."** -- Added subfigure (a)/(b) guidance

### Other files (1 fix each)
- **gps_estimation_deep.tex**: GSD table -- added camera params and 35m pixel size
- **field_day_narrative.tex**: Benchmark table -- added detection rate and confidence
- **steeple.tex**: STEEPLE table -- added what-to-look-for guidance
- **A2_config_params.tex**: Config table -- added calibration vs datasheet provenance
- **system_description.tex**: MAVLink commands -- added altitude cap and geofence context

## Captions That Were Already Strong (examples)

These required no changes -- they follow the ideal pattern:

- *"CEP50 comparison of four fusion algorithms on DJI replay data. IVW achieves the lowest error at 2.3 m, highlighted as the selected method. Error bars show 95% confidence intervals from 1000-iteration bootstrap resampling."* (estimation_evaluation.tex)
- *"Geofence protection layers shown to scale on the Fenswood Farm site..."* (13_safety_risk.tex)
- *"Altitude--speed trade-off space. Colour encodes composite mission score (40% detection + 35% coverage + 25% energy)..."* (design_rationale.tex)
- *"Training and validation loss curves over 150 epochs. Rapid convergence occurs in epochs 1--30..."* (12_model_training.tex)
- *"Along-track estimation bias as a function of flight heading..."* (estimation_evaluation.tex)

## Style Observations

1. **Most captions already end with a period** -- consistent.
2. **Sentence case is used throughout** -- consistent.
3. **Subfigure captions are generally shorter than parent captions** -- appropriate.
4. **Data sources are cited** when figures come from video replay or bench testing.
5. **The estimation_evaluation.tex and cv_extended.tex files have the best captions** in the entire report -- rich with numbers, directional, and insightful. These set the standard.

## Recommendation

The report's caption quality is now uniformly strong. No further fixes needed. The key pattern for future captions: *label + what-to-look-for + key number + so-what*.
