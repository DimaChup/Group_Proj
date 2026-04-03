# Gap Analysis: Reportflow vs Goldmine Body Sections

**Date**: 2026-04-03
**Reportflow**: `reportflow/main.tex` (17 pages, ~687 lines)
**Goldmine sections compared**: `design_rationale.tex`, `system_description.tex`, `requirements_verification.tex`, `evaluation.tex`

---

## 1. Structural Comparison

| Goldmine Section | Reportflow Equivalent | Present? |
|---|---|---|
| **Design Rationale** (STEEPLE, search param optimisation, hardware rationale) | Sections 1-9 cover search param optimisation in much greater depth. STEEPLE and hardware rationale are **missing**. | Partial |
| **System Description** (hardware, software arch, CV pipeline, search pattern, state machine, localisation, ground station, simulation) | Only search pattern generation is covered. Everything else is **missing**. | Minimal |
| **Requirements Verification** (R01-R12 traceability table, per-requirement evidence) | **Entirely missing**. | No |
| **Evaluation** (plus/delta table, discussion, bug discovery table, testing framework, lessons learned, what would change) | **Entirely missing**. | No |

**Verdict**: Reportflow covers only one topic -- search parameter optimisation / design rationale for flight parameters. It is a deep-dive appendix-style document, not a replacement for the four goldmine body sections.

---

## 2. Key Content in Goldmine but MISSING from Reportflow

### 2.1 Design Rationale gaps
- **STEEPLE analysis** (Social, Technological, Economic, Environmental, Political, Legal, Ethical) -- the entire subsection with 7 dimension descriptions
- **Hardware platform selection rationale** (global shutter camera justification, no thermal imaging justification, MAVProxy bridge rationale)
- **Parameter derivation chain Steps 1-8** -- the goldmine has a compressed 8-step version; reportflow has a 9-step expanded version that is largely equivalent but structured differently

### 2.2 System Description (entirely absent from reportflow)
- **Hardware platform**: BOM table (Table hw-bom), UART/MAVProxy communication architecture, lens calibration details
- **Software architecture**: 11-module layered architecture, module dependency graph (Fig architecture), Pi system diagram (Fig pi_system)
- **MAVLink command table** (Table mavlink-commands)
- **Geofence enforcement**: three nested protection layers, geofence diagram (Fig geofence_diagram), cv2.pointPolygonTest implementation
- **CV pipeline details**: preprocessing (BGR issue, resize, normalise), TFLite output tensor shape [1,5,8400], three backends (Ultralytics/TFLite/NCNN), smart detection mode, CV pipeline figure
- **Mission state machine**: 20-state FSM, four mission phases (startup/search/engagement/recovery), state transition diagram, detection queue with spatial deduplication, five safety mechanisms
- **Target localisation**: pinhole camera model projection, spatial clustering (30m merge), inverse-variance weighting formula, Kalman filter, error budget table (6 sources), GPS bullseye/convergence/estimator comparison figures
- **Ground station**: browser dashboard description, MJPEG rationale, headless operation, passive monitoring mode
- **Simulation framework**: four simulation levels, mission timeline figure

### 2.3 Requirements Verification (entirely absent)
- **R01-R12 traceability table** with verification method, evidence, and status per requirement
- **Per-requirement evidence narratives** (R01 flight area, R02 SSSI overfly, R03 takeoff location, R04 altitude limit, R05 search+identify with per-flyover detection probability math, R06 PLB focus area, R07 landing 5-10m with probability analysis, R08 autonomy levels (Sheridan framework), R09 RTH/motor cutoff (3 independent mechanisms), R10 lat/lon reporting, R11 company pilot, R12 GitHub/MIT)
- **Probability analysis for R07** (Rician distribution, CEP50-based landing accuracy >99%)

### 2.4 Evaluation (entirely absent)
- **Plus/delta table** (9 pluses P1-P9, 9 deltas D1-D9) with specific evidence
- **Discussion of key findings**: architecture resilience, detection performance caveats, GPS estimation accuracy, testing effectiveness
- **Bug discovery table** (Table bug-cost): 12 defects with tier discovered, fix time, cost if missed
- **Detection sensitivity figures**: confidence vs altitude, detection rate vs speed, latency breakdown, detection heatmap
- **Five-tier progressive testing framework** (Table five-tier-summary)
- **What would change in a second iteration** (4 items)
- **Lessons learned** (4 technical lessons)
- **Honest limitations discussion**: no outdoor flight, train/val overlap concern, single-class detector, payload not integrated, GPS lag uncompensated

---

## 3. Missing Metrics and Data

| Metric/Data | In Goldmine | In Reportflow |
|---|---|---|
| mAP50 = 0.995 | Yes | Yes (Step 1) |
| 4.8 FPS / 206.5ms TFLite | Yes | Yes |
| 9 FPS NCNN | Yes (mentioned) | Yes (used in speed calcs) |
| CEP50 = 2.3m GPS accuracy | Yes (detailed) | No |
| Max GPS error 16.5m | Yes | No |
| Error budget table (6 sources) | Yes | No |
| 50/50 bench detection at 0.966 conf | Yes | No |
| Lens calibration RMS = 0.399 | Yes | No |
| Undistortion cost +1.5ms | Yes | No |
| 300ms MJPEG latency | Yes | No |
| System cost 565 GBP | Yes | No |
| 4400 lines of code / 11 modules | Yes | No |
| 71 test scripts | Yes | No |
| 12 defects caught at low-cost tiers | Yes | No |
| Landing accuracy P(5-10m) > 99% | Yes | No |
| Sheridan Level 7-8 / 3-4 autonomy | Yes | No |
| Detection confidence vs altitude curve | Yes (figure) | Partially (table of 3 conditions) |
| Detection rate vs speed curve | Yes (figure) | Partially (table of 3 conditions) |

---

## 4. Missing Figures and Tables

### Figures in goldmine but NOT in reportflow:
- `mission_overview` -- mission plan overlaid on site
- `architecture` -- module dependency graph
- `pi_system` -- Pi companion computer system diagram
- `geofence_diagram` -- four-panel geofence visualisation
- `cv_pipeline` -- CV pipeline stages
- `coverage_vs_time` -- area coverage progression
- `state_machine` -- 20-state FSM diagram
- `gps_bullseye` -- GPS estimation error scatter
- `gps_error_direction` -- directional error distribution
- `gps_convergence` -- Kalman filter convergence
- `estimator_comparison` -- raw/weighted/Kalman comparison
- `mission_timeline` -- state transitions over time
- `conf_vs_alt` -- detection confidence vs altitude
- `det_vs_speed` -- detection rate vs speed
- `latency_breakdown` -- per-frame latency budget
- `detection_heatmap` -- spatial detection density

### Figures in reportflow but NOT in goldmine:
- `sensitivity_spider` -- 5-axis performance envelope (new)
- `sensitivity_matrix` -- input-output coupling matrix (new)
- `decision_flow` -- 9-step decision chain infographic (new)
- `lighting_combined` -- detection envelope under 3 lighting conditions (new)
- `real_energy_heatmap` -- 216-config energy heatmap (new)
- `top3_paths` -- top 3 configurations on polygon (new)
- `objective_conflict` -- 6-config 5-objective comparison (new)
- `tornado_sensitivity` -- tornado chart of sensitivities (new)
- `pareto_parallel` -- parallel coordinates Pareto plot (new)
- `safety_subscore` -- safety score decomposition spider (new)
- `detection_subscore` -- detection score decomposition spider (new)
- `scoring_overview` -- scoring framework diagram (new)

### Tables in goldmine but NOT in reportflow:
- `hw-bom` -- bill of materials
- `mavlink-commands` -- MAVLink command table
- `error-budget-summary` -- 6-source error budget
- `req-verification` -- R01-R12 traceability matrix
- `plus-delta` -- 9 pluses / 9 deltas
- `bug-cost` -- 12 defects with tier/time/cost
- `five-tier-summary` -- progressive testing framework

### Tables in reportflow but NOT in goldmine:
- `df-variables` -- 7 decision variables (new)
- `df-detection-envelope` -- detection ceiling by lighting (new)
- `df-speed-envelope` -- speed limits by lighting (new)
- `df-top3` -- top 3 configurations ranked (new)
- `df-final` -- final operating configuration summary (new)

---

## 5. Does Reportflow Follow the Same 4-Section Structure?

**No.** Reportflow has its own structure:

1. Objective
2. Constraints
3. Five Competing Dimensions
4. Scoring the Five Dimensions (Safety, Detection, Time, Energy, Coverage)
5. The Variables We Can Choose
6. How They Interconnect
7. The Decision Chain (Steps 1-9)
8. The Decision Chain in Summary
9. What We Evaluated (216-config sweep)
10. The Result
11. Sensitivity and Robustness
12. Pareto Optimality
13. Non-Quantifiable Design Choices

This maps roughly to a deep expansion of goldmine `design_rationale.tex` Section 2.2 (Search Parameter Optimisation) and Section 2.4 (Parameter Derivation Chain). It does NOT cover any of the other three goldmine sections.

---

## 6. Is Reportflow Self-Contained (Submittable Alone)?

**No.** Reportflow is missing:

- **No introduction or abstract** -- jumps straight into "Objective"
- **No system description** -- assumes the reader already knows the hardware, software, state machine, CV pipeline, ground station, and localisation subsystem
- **No requirements verification** -- the brief requires R01-R12 traceability
- **No evaluation/reflection** -- no plus/delta, no lessons learned, no honest limitations
- **No references/bibliography** -- zero citations (the goldmine cites ~15 sources)
- **No appendices** -- references appendices that don't exist in this document

Reportflow is best used as:
- A **supplementary appendix** to the main report (e.g., Appendix: Search Parameter Optimisation)
- A **deep-dive companion** that the main report can reference for the full derivation chain
- Source material to **compress into** the goldmine's design_rationale Section 2.2-2.4 (currently ~60 lines in the goldmine, expandable to ~2 pages)

---

## 7. Recommendations

1. **Do NOT submit reportflow as the main report** -- it covers only 1 of 4 required sections and lacks requirements verification entirely.

2. **Use reportflow as an appendix** -- rename it "Appendix: Search Parameter Optimisation Decision Flow" and reference it from the goldmine's design_rationale section.

3. **Merge unique reportflow content into goldmine** where it adds value:
   - The scoring framework (Section 4) with safety/detection/time/energy/coverage decomposition
   - The lighting-dependent detection/speed envelopes (Tables df-detection-envelope, df-speed-envelope)
   - The pattern type comparison (Step 5: 4 patterns evaluated)
   - The heading mode analysis (Step 6: fixed vs yaw-to-face)
   - The Pareto/sensitivity analysis (tornado chart, parallel coordinates)
   - The top-3 configuration comparison table

4. **Fill goldmine gaps** that reportflow does NOT address:
   - STEEPLE analysis (already in goldmine, keep it)
   - Hardware rationale (already in goldmine, keep it)
   - System description (entire section -- this is the biggest gap)
   - Requirements verification (entire section)
   - Evaluation (entire section)

5. **Add bibliography to reportflow** if it will be submitted as an appendix -- currently has zero citations.
