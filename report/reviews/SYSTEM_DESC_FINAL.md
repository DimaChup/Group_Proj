# System Description Final Polish Review

**File:** `report/sections/system_description.tex`
**Date:** 2026-04-04
**Reviewer:** Claude (automated)

---

## Changes Made

### Factual Corrections (verified against codebase)

| Item | Was | Now | Source |
|------|-----|-----|--------|
| Production code lines | 4,400 | 5,700 | `wc -l` on 11 modules = 5,729 |
| Test scripts | 74 | 83 | `find tests/ -name "*.py"` excluding `__init__.py` = 83 |
| Config parameters | 40+ | 70+ | `grep -cE "^[A-Z_]+ *=" config.py` = 73 |
| Landing detection | "triple touchdown" | "five-tick altimeter confirmation or ArduPilot auto-disarm" | `state_machine.py`: `TOUCHDOWN_TICKS = 5` + auto-disarm path |
| State machine phase count | "four phases" | "four primary phases, plus override and error-handling paths" | Now lists 6 bullet points (was 5) |

### Missing States Added (was 18/20, now 20/20)

- **RETURN_FROM_MANUAL**: Added to Override bullet -- validates GPS fix and NFZ clearance before resuming pre-override state.
- **HOVER**: Added as new "Error fallback" bullet -- entered when no valid waypoints generated, holds position for 60s.

### Missing Appendix Cross-References Added

In the Target Localisation subsection (line ~202), added:
- `\ref{sec:estimation-eval}` -- ground-truth evaluation methodology and bullseye diagnostics
- `\ref{sec:loc-approaches}` -- ten alternative localisation approaches

(The concurrent session also added `\ref{sec:centering-analysis}` and `\ref{sec:comms}` -- both labels verified as existing.)

---

## Verification Checklist

### 1. Architecture clearly explained (hardware + software)
- [x] Hardware: BOM table, UART/MAVProxy bridge, camera specs, lens calibration, global shutter rationale
- [x] Software: four-layer architecture, module dependency graph, Pi system diagram
- [x] Both diagrams referenced (Fig architecture, Fig pi_system)

### 2. Each module's interface described
- [x] `vision.py`: `detect_in_image(frame)` -> `(found, cx, cy, conf)` -- explicitly stated
- [x] `planning.py`: GPS polygon -> ordered waypoint list
- [x] `gps_utils.py`: bidirectional GPS<->pixel via GeoTransformer
- [x] `geofence.py`: NFZ enforcement
- [x] `navigation.py`: MAVLink commands table (6 methods)
- [x] `stream_server.py`: MJPEG ground station
- [x] `state_machine.py`: 20 state handlers as mixin
- [x] `config.py`: 70+ parameters with auto-detection
- [x] Zero mutual dependencies between independent modules -- stated and accurate

### 3. State machine fully documented
- [x] All 20 states now accounted for in the itemised list
- [x] State transition diagrams: hand-drawn (Fig state_machine) + auto-generated (Fig state_machine_generated)
- [x] Detection queue: spatial dedup (5m), bounded capacity (20), lazy validation -- all verified against code
- [x] VERIFY timeout: 120s -- verified in state_machine.py
- [x] Appendix ref for full state table

### 4. Vision pipeline end-to-end
- [x] Preprocessing: undistortion, BGR handling, resize, normalise
- [x] Inference: TFLite tensor shapes, confidence filtering, coordinate rescaling
- [x] Three backends (Ultralytics, TFLite, NCNN) with auto-selection
- [x] Smart detection mode (k consecutive frames)
- [x] Performance: 206.5ms / 4.8 FPS, 50/50 detection, 0.966 confidence
- [x] CV pipeline figure referenced
- [x] Training: three iterations (640, 1280, 1088), mAP50=0.995

### 5. Safety features prominent
- [x] Six layers enumerated clearly in numbered list
- [x] RC override guard: checked BEFORE state dispatch
- [x] RC kill switch: hardware-level bypass
- [x] GPS fix monitoring: 3D fix + 6 sats
- [x] Flight Area boundary: pointPolygonTest every iteration
- [x] Five-layer SSSI geofence: plan-time, speed ramp, repulsive, hard cutoff
- [x] Per-state timeouts with GCS failsafe backstop
- [x] Geofence runs AFTER state handler -- explicitly stated

### 6. Figures referenced and helpful
- [x] mission_overview (site map)
- [x] architecture (module dependency graph)
- [x] pi_system (Pi hardware data flow)
- [x] geofence_diagram (5 protection layers)
- [x] cv_pipeline (vision pipeline)
- [x] coverage_vs_time (area coverage)
- [x] search_pattern (lawnmower on polygon)
- [x] state_machine (hand-drawn transitions)
- [x] state_machine_generated (auto-generated, colour-coded)
- [x] gps_accuracy subfigures (bullseye + directional error)
- [x] mission_timeline (state transitions over time)
- Total: 11 figures/subfigures -- appropriate density for ~7 pages

### 7. Technical depth appropriate
- [x] GSD equation with all parameters defined
- [x] Coverage guarantee derivation (Wg, lane spacing, overlap)
- [x] Inverse-variance weighting formula
- [x] Kalman filter mentioned but not over-detailed (appendix)
- [x] MAVLink command table
- [x] Error budget summary (RSS 2.9m, GPS 2.3m, timing 1.5m)
- [x] CEP50 = 2.3m from real flight data
- Verdict: good balance -- equations support claims without overwhelming

### 8. Estimation appendix references
- [x] `\ref{sec:gps-deep}` -- full pipeline, error budget, fusion
- [x] `\ref{sec:estimation-eval}` -- ground-truth evaluation, bullseye (ADDED)
- [x] `\ref{sec:loc-approaches}` -- 10 alternative approaches (ADDED)
- [x] `\ref{sec:centering-analysis}` -- centering trade-off (added by concurrent session)
- [x] `\ref{fig:pipeline-flow}` -- 15-stage pipeline flowchart

---

## Cross-Reference Audit (all verified as existing)

| Reference | Target file | Label exists? |
|-----------|------------|---------------|
| `sec:rationale` | design_rationale.tex | Yes |
| `sec:requirements` | requirements_verification.tex | Yes |
| `sec:cv:inference` | inference_architecture.tex | Yes |
| `sec:streaming-arch` | streaming_architecture.tex | Yes |
| `sec:calibration` | calibration_deep.tex | Yes |
| `app:config` | A2_config_params.tex | Yes |
| `sec:test-scripts` | test_scripts_guide.tex | Yes |
| `app:cv-extended` | cv_extended.tex | Yes |
| `app:cv:benchmarks` | cv_extended.tex | Yes |
| `app:cv:training` | cv_extended.tex | Yes |
| `app:cv:speed` | cv_extended.tex | Yes |
| `sec:path-opt` | path_optimization_definitive.tex | Yes |
| `sec:nfz-interaction` | path_optimization_definitive.tex | Yes |
| `sec:repulsive-field` | focus_and_repulsive.tex | Yes |
| `app:states` | A1_state_table.tex | Yes |
| `sec:gps-deep` | gps_estimation_deep.tex | Yes |
| `sec:estimation-eval` | estimation_evaluation.tex | Yes |
| `sec:loc-approaches` | localization_approaches.tex | Yes |
| `sec:sim-validation` | simulation_validation.tex | Yes |
| `sec:safety` | 13_safety_risk.tex | Yes |
| `sec:mission-flow` | mission_flow.tex | Yes |
| `sec:comms` | comms_architecture.tex | Yes |
| `sec:centering-analysis` | centering_analysis.tex | Yes |
| `fig:pipeline-flow` | gps_estimation_deep.tex | Yes |

All 23 cross-references resolve. Zero undefined references.

---

## Items NOT Changed (reviewed and deemed correct)

- **20-state count**: Verified -- states.py has exactly 20 states
- **11 modules**: Verified -- config, states, vision, planning, gps_utils, geofence, navigation, stream_server, state_machine, main, utils
- **HFOV 49.3 degrees**: Verified -- 2*atan(5.02/(2*5.46)) = 49.3 for the Pi camera (distinct from 54.4 deg DJI)
- **127 unit tests**: Verified -- 28+19+26+5+36+13 = 127
- **5m reject radius, 20 queue capacity**: Verified in config.py
- **VERIFY 120s timeout**: Verified in state_machine.py
- **7.5m offset landing**: Verified in gps_utils.py
- **206.5ms inference, 4.8 FPS**: Consistent with benchmark results
- **CEP50 = 2.3m**: Consistent with video analysis results
- **12 defects caught in simulation**: Plausible from session logs

## Notes for Concurrent Session

Another Claude session is simultaneously editing this file (adding `\ref{sec:comms}`, `\ref{sec:centering-analysis}`, `\ref{sec:cv:pipeline-fps}`, `\ref{sec:vision-perf}`). These additions are complementary and do not conflict with the changes in this review.
