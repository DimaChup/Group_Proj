# Figure Audit v2

Generated 2026-04-03. Comprehensive audit of every figure across all `.tex` files included in `main.tex`.

---

## 1. PLACEHOLDER FIGURES (fbox/parbox -- MUST be replaced)

These are text-only placeholder boxes with no actual image. Sorted by priority (body first, then appendices).

### Body Sections (ASSESSED -- highest priority)

| # | File | Line | Label | Description | Priority |
|---|------|------|-------|-------------|----------|
| 1 | `02_system_architecture.tex` | 25 | `fig:architecture` | "System Architecture Block Diagram" | **CRITICAL** -- duplicate label with `system_description.tex:52` which HAS a real figure. This placeholder is in an OLD/UNUSED section file that is NOT `\input`-ed by `main.tex`. See note below. |
| 2 | `02_system_architecture.tex` | 32 | `fig:arch-block` | "Module Dependency Graph" | **CRITICAL** -- same as above, old file. |
| 3 | `03_hardware_platform.tex` | 9 | `fig:hw-block` | Hardware block diagram (Camera->Pi->Cube->GCS) | **HIGH** -- `\includegraphics` commented out, `fbox` active. File `hardware_block_diagram` does NOT exist in figs/. |
| 4 | `04_computer_vision.tex` | 27 | `fig:cv_pipeline` | Detection pipeline diagram | **HIGH** -- `\includegraphics` commented out, `fbox` active. `cv_pipeline.pdf` EXISTS in figs/ but is not used. Duplicate label with `system_description.tex:114` which uses the real figure. |
| 5 | `06_state_machine.tex` | 86 | `fig:state_machine` | State machine diagram | **HIGH** -- `\includegraphics` commented out, `fbox` active. `state_machine.pdf` EXISTS in figs/. Duplicate label with `system_description.tex:156` which uses the real figure. |
| 6 | `07_target_localisation.tex` | 127 | `fig:gps-scatter` | GPS scatter plot | **HIGH** -- `\includegraphics` commented out, plain italic text placeholder. `gps_scatter.pdf` does NOT exist, but `gps_bullseye.pdf` does. |
| 7 | `08_ground_station.tex` | 37 | `fig:dashboard` | Browser dashboard screenshot | **HIGH** -- `\includegraphics` commented out, `fbox` active. `dashboard_screenshot` does NOT exist in figs/. No real screenshot exists anywhere. |
| 8 | `09_simulation.tex` | 77 | `fig:simulator` | Interactive simulator screenshot (2x2 layout) | **MEDIUM** -- `fbox` placeholder. No screenshot file exists. |

**IMPORTANT NOTE on 02_system_architecture.tex**: This file is NOT included in `main.tex`. The `\input` list shows `system_description.tex` instead, which contains the real figures for `fig:architecture` and `fig:cv_pipeline`. However, `04_computer_vision.tex`, `06_state_machine.tex`, `07_target_localisation.tex`, and `08_ground_station.tex` are also NOT in the `\input` list -- they appear to be OLD standalone section files superseded by the consolidated body files (`design_rationale.tex`, `system_description.tex`, `requirements_verification.tex`, `evaluation.tex`). **If these files are not `\input`-ed, their placeholders don't appear in the compiled PDF.**

Let me verify which placeholder files ARE actually compiled:

**Files with placeholders that ARE `\input`-ed in main.tex**: NONE of the above files (02-09) are in the `\input` list. The body uses `design_rationale.tex`, `decision_flow.tex`, `system_description.tex`, `requirements_verification.tex`, `evaluation.tex`.

**Appendix files with placeholders that ARE `\input`-ed**:

| # | File | Line | Label | Description | Priority |
|---|------|------|-------|-------------|----------|
| 9 | `figure_descriptions.tex` | 10 | `fig:dashboard-screenshot` | Ground station dashboard (text description) | **LOW** -- appendix, text placeholder is intentional "blackboard diagram" |
| 10 | `figure_descriptions.tex` | 51 | `fig:hardware-photo` | Hardware assembly photo (text description) | **LOW** -- appendix, intentional text placeholder |
| 11 | `figure_descriptions.tex` | 92 | `fig:detection-overlay` | Detection overlay example (text description) | **LOW** -- appendix, intentional text placeholder |
| 12 | `figure_descriptions.tex` | 130 | `fig:lawnmower-satellite` | Lawnmower pattern on satellite (text description) | **LOW** -- appendix, intentional text placeholder |
| 13 | `figure_descriptions.tex` | 175 | `fig:bench-setup` | Bench test setup photo (text description) | **LOW** -- appendix, intentional text placeholder |

### Non-placeholder fbox usage (NOT figures)

| File | Line | What | Issue? |
|------|------|------|--------|
| `testing_deep.tex` | 22-30 | Tier 1-5 boxes in a tabular layout | NO -- this is a styled diagram using fbox, not a placeholder. It is a TikZ-like tier progression display. |

---

## 2. REAL FIGURES (includegraphics) -- Quality Assessment

### Body: `system_description.tex` (12 figures -- ALL GOOD)

| # | Label | File | Exists? | Quality |
|---|-------|------|---------|---------|
| 1 | `fig:mission_overview` | `mission_overview.pdf` | YES | GOOD -- essential site overview |
| 2 | `fig:architecture` | `architecture.pdf` | YES | GOOD -- module dependency graph |
| 3 | `fig:pi_system` | `pi_system.pdf` | YES | GOOD -- hardware data flow |
| 4 | `fig:geofence_diagram` | `geofence_diagram.pdf` | YES | GOOD -- 4-panel NFZ protection |
| 5 | `fig:cv_pipeline` | `cv_pipeline.pdf` | YES | GOOD -- detection pipeline |
| 6 | `fig:coverage_vs_time` | `coverage_vs_time.pdf` | YES | GOOD -- quantitative coverage |
| 7 | `fig:state_machine` | `state_machine.pdf` | YES | GOOD -- simplified FSM |
| 8 | `fig:gps_bullseye` | `gps_bullseye.pdf` | YES | GOOD -- GPS accuracy |
| 9 | `fig:gps_error_direction` | `gps_error_direction.pdf` | YES | GOOD -- directional error |
| 10 | `fig:gps_convergence` | `gps_convergence.pdf` | YES | GOOD -- Kalman convergence |
| 11 | `fig:estimator_comparison` | `estimator_comparison.pdf` | YES | GOOD -- method comparison |
| 12 | `fig:mission_timeline` | `mission_timeline.pdf` | YES | GOOD -- simulation timeline |

### Body: `design_rationale.tex` (2 figures)

| # | Label | File | Exists? | Quality |
|---|-------|------|---------|---------|
| 13 | `fig:coupling-body` | `coupling_matrix.pdf` | YES | GOOD |
| 14 | `fig:alt-speed-body` | `altitude_speed_tradeoff.pdf` | YES | GOOD |

### Body: `evaluation.tex` (4 figures in 2 subfigure groups)

| # | Label | File | Exists? | Quality |
|---|-------|------|---------|---------|
| 15 | `fig:conf_vs_alt` | `conf_vs_alt.pdf` | YES | GOOD |
| 16 | `fig:det_vs_speed` | `det_vs_speed.pdf` | YES | GOOD |
| 17 | `fig:latency_breakdown` | `latency_breakdown.pdf` | YES | GOOD |
| 18 | `fig:detection_heatmap` | `detection_heatmap.pdf` | YES | GOOD |

### Body: `decision_flow.tex` (0 new figures -- references figures defined elsewhere)

References `fig:sensitivity-matrix`, `fig:energy-heatmap`, `fig:alt-speed-body`, `fig:pareto-parallel`, `fig:top3-paths`, `fig:sensitivity-spider` -- all defined in appendix files.

### Body: `requirements_verification.tex` (0 new figures -- references `fig:geofence_diagram`)

### Appendix figures (selected, all `\input`-ed):

| File | Label | Image File | Exists? | Quality |
|------|-------|-----------|---------|---------|
| `A1_state_table.tex` | `fig:state_machine_full` | `state_machine_full.pdf` | YES | GOOD |
| `12_model_training.tex` | `fig:training-curves` | `training_curves.pdf` | YES | GOOD |
| `12_model_training.tex` | `fig:confusion-matrix` | `confusion_matrix.pdf` | YES | GOOD |
| `inference_architecture.tex` | `fig:benchmark-comparison` | `benchmark_comparison.pdf` | YES | GOOD |
| `cv_extended.tex` | `fig:altitude-detection-table` | `altitude_detection_table.pdf` | YES | GOOD |
| `cv_extended.tex` | `fig:conf_vs_alt_ext` | `conf_vs_alt.pdf` | YES | OK -- same file as body |
| `cv_extended.tex` | `fig:detection_envelope` | `detection_envelope.pdf` | YES | GOOD |
| `cv_extended.tex` | `fig:blur_vs_altitude` | `blur_vs_altitude.pdf` | YES | GOOD |
| `cv_extended.tex` | `fig:det_vs_speed_ext` | `det_vs_speed.pdf` | YES | OK -- same file as body |
| `cv_extended.tex` | `fig:latency_breakdown_ext` | `latency_breakdown.pdf` | YES | OK -- same file as body |
| `pipeline_fps.tex` | `fig:bottleneck_shift` | TikZ (inline) | N/A | GOOD -- pgfplots bar chart |
| `comms_architecture.tex` | `fig:comms-topology` | verbatim text | N/A | OK -- ASCII diagram |
| `optimization_master.tex` | 15+ figures | various | ALL YES | GOOD -- comprehensive |
| `path_optimization_definitive.tex` | 7 figures | various | ALL YES | GOOD |
| `design_strategy.tex` | 7 figures | various | ALL YES | GOOD |
| `optimization_formal.tex` | 2 figures | `n2_diagram`, `objective_conflict` | YES | GOOD |
| `search_optimization.tex` | 4 figures | various | ALL YES | GOOD |
| `vision_performance.tex` | 5 figures | `real_*.png` | ALL YES | GOOD |
| `05_path_planning.tex` | `fig:coverage_vs_time` | `coverage_vs_time.pdf` | YES | DUPLICATE label with system_description.tex |

---

## 3. DUPLICATE LABELS (will cause LaTeX warnings)

| Label | File 1 (defines it) | File 2 (also defines it) | Both compiled? |
|-------|---------------------|--------------------------|----------------|
| `fig:architecture` | `system_description.tex:52` (real fig) | `02_system_architecture.tex:27` (placeholder) | NO -- 02_ is not `\input`-ed |
| `fig:cv_pipeline` | `system_description.tex:114` (real fig) | `04_computer_vision.tex:29` (placeholder) | NO -- 04_ is not `\input`-ed |
| `fig:state_machine` | `system_description.tex:156` (real fig) | `06_state_machine.tex:88` (placeholder) | NO -- 06_ is not `\input`-ed |
| `fig:coverage_vs_time` | `system_description.tex:144` (real fig) | `05_path_planning.tex:57` (real fig) | **05_ is NOT `\input`-ed** |
| `fig:top3-paths` | `optimization_master.tex:129` | `path_optimization_definitive.tex:201` | **BOTH compiled** |
| `fig:n2-diagram` | `optimization_master.tex:230` | `optimization_formal.tex:193` | **BOTH compiled** |
| `fig:coupling-matrix` | `optimization_master.tex:234` | `design_strategy.tex:259` | **BOTH compiled** |
| `fig:sensitivity-matrix` | `optimization_master.tex:259` | `design_strategy.tex:245` | **BOTH compiled** |
| `fig:sensitivity-spider` | `optimization_master.tex:263` | `design_strategy.tex:252` | **BOTH compiled** |
| `fig:alt-speed-body` | `optimization_master.tex:169` | `design_rationale.tex:59` | **BOTH compiled** |
| `fig:tornado-sensitivity` | `optimization_master.tex:204` | `design_strategy.tex:280` | **BOTH compiled** |
| `fig:energy-heatmap` | `optimization_master.tex:178` | `path_optimization_definitive.tex:92` | **BOTH compiled** |
| `fig:pareto-2d` | `optimization_master.tex:277` | `path_optimization_definitive.tex:344` | **BOTH compiled** |

**13 duplicate labels detected. 10 are in files that are BOTH compiled -- these will cause LaTeX "multiply defined" warnings and broken cross-references.**

---

## 4. MISSING FIGURE FILES (referenced by includegraphics but not in figs/)

| Referenced As | In File | Exists? | Notes |
|---------------|---------|---------|-------|
| `hardware_block_diagram` | `03_hardware_platform.tex` | NO | Commented out, not compiled |
| `dashboard_screenshot` | `08_ground_station.tex` | NO | Commented out, not compiled |
| `gps_scatter` | `07_target_localisation.tex` | NO | Commented out, not compiled |
| `state_machine_diagram` | `06_state_machine.tex` | NO | Commented out, not compiled |

**All 4 missing files are in commented-out `\includegraphics` lines AND in files not `\input`-ed. No missing files in compiled sections.**

---

## 5. UNREFERENCED FIGURE LABELS (defined but never `\ref`-ed)

These labels exist but are never cross-referenced in any text:

| Label | File | Image | Should it be referenced? |
|-------|------|-------|-------------------------|
| `fig:altitude-detection-table` | `cv_extended.tex` | real | MAYBE -- standalone appendix figure |
| `fig:altitude-tradeoff-dual` | `path_optimization_definitive.tex` | real | MAYBE |
| `fig:bench-setup` | `figure_descriptions.tex` | placeholder | NO -- appendix placeholder |
| `fig:benchmark-comparison` | `inference_architecture.tex` | real | MAYBE -- could reference from body |
| `fig:confusion-matrix` | `12_model_training.tex` | real | MAYBE |
| `fig:coupling-body` | `design_rationale.tex` | real | YES -- body figure, should be referenced |
| `fig:coupling-pair` | `optimization_master.tex` | real | MAYBE |
| `fig:dashboard-screenshot` | `figure_descriptions.tex` | placeholder | NO |
| `fig:detection-overlay` | `figure_descriptions.tex` | placeholder | NO |
| `fig:detection_heatmap` | `evaluation.tex` | real | Group label exists (`fig:perf_analysis`) |
| `fig:energy_efficiency` | `search_optimization.tex` | real | MAYBE |
| `fig:estimation` | `system_description.tex` | group label | Group parent, subfigs referenced |
| `fig:estimator_comparison` | `system_description.tex` | real | Group child, parent referenced |
| `fig:function-chain` | `design_strategy.tex` | real | MAYBE |
| `fig:gps_accuracy` | `system_description.tex` | group label | Group parent |
| `fig:gps_convergence` | `system_description.tex` | real | Group child |
| `fig:hardware-photo` | `figure_descriptions.tex` | placeholder | NO |
| `fig:lawnmower-satellite` | `figure_descriptions.tex` | placeholder | NO |
| `fig:nfz_margin_altitude` | `search_optimization.tex` | real | MAYBE |
| `fig:objective-conflict` | `optimization_formal.tex` | real | MAYBE |
| `fig:optimal-pattern` | `path_optimization_definitive.tex` | real | MAYBE |
| `fig:optimization-network` | `design_strategy.tex` | real | MAYBE |
| `fig:path-patterns` | `path_optimization_definitive.tex` | real | MAYBE |
| `fig:pi_system` | `system_description.tex` | real | YES -- body figure, never referenced in text |
| `fig:rotation_comparison` | `search_optimization.tex` | real | MAYBE |
| `fig:sensitivity-pair` | `optimization_master.tex` | group label | MAYBE |
| `fig:speed-frames` | `vision_performance.tex` | real | MAYBE |
| `fig:speed_detection_energy` | `search_optimization.tex` | real | MAYBE |
| `fig:tier-flow` | `testing_deep.tex` | styled boxes | MAYBE |
| `fig:training-curves` | `12_model_training.tex` | real | MAYBE |

---

## 6. GENERATED PDFs IN figs/ NOT USED ANYWHERE

| File | What It Shows | Recommendation |
|------|---------------|----------------|
| `decision_flow.pdf` | Decision flow diagram | Could be used in `decision_flow.tex` body section |
| `detection_subscore.pdf` | Detection subscore analysis | Could support evaluation |
| `lighting_combined.pdf` | Combined lighting analysis | Could support CV appendix |
| `lighting_detection.pdf` | Lighting vs detection | Could support CV appendix |
| `lighting_speed.pdf` | Lighting vs speed | Could support CV appendix |
| `safety_subscore.pdf` | Safety subscore | Could support risk appendix |
| `scoring_overview.pdf` | Scoring overview | Could support evaluation |
| `state_machine_simple.pdf` | Simplified state machine | Alternative to current `state_machine.pdf` |
| `system_overview_simple.pdf` | Simple system overview | Alternative architecture view |

---

## 7. FIGURES THAT SHOULD EXIST BUT DON'T

### CRITICAL (would significantly improve assessed body)

| What | Where | Why | Effort |
|------|-------|-----|--------|
| **Hardware photo** | System Description or figure_descriptions.tex | No photo of assembled drone anywhere. The text placeholder is detailed but a real photo is worth 100x more for communication marks. | Take photo or ask teammate |
| **Ground station screenshot** | System Description or figure_descriptions.tex | Dashboard is described in 200+ words but never shown. Take a screenshot during simulation. | 5 min -- run pi_flight.py in SIMULATION and screenshot browser |
| **Detection overlay frame** | System Description CV section | A single real detection frame (bounding box on dummy) would powerfully evidence the CV pipeline. | 5 min -- extract from DJI video replay |

### HIGH (meaningful improvement)

| What | Where | Why | Effort |
|------|-------|-----|--------|
| **Simulator screenshot** | `09_simulation.tex` (if moved to appendix input list) | The 2x2 simulator layout is described but never shown. | 5 min -- screenshot of simple_simulator.py |
| **Precision-recall curve** | Evaluation | Acknowledged as missing (D4 delta). Standard ML evidence. | 30 min -- generate from model validation |
| **Hardware block diagram** | `03_hardware_platform.tex` | Referenced file `hardware_block_diagram` doesn't exist. Could use `pi_system.pdf` instead. | Already exists as `pi_system.pdf` |

### MEDIUM (nice to have)

| What | Where | Why |
|------|-------|-----|
| FOV calibration photo | Design rationale | Tape measure at 1m showing 92cm visible |
| Lens distortion before/after | CV appendix | Demonstrates calibration quality |
| Wind envelope diagram | Evaluation D1 | Go/no-go boundary |

---

## 8. SUMMARY STATISTICS

| Category | Count |
|----------|-------|
| **Placeholder figures in compiled PDF** | **5** (all in `figure_descriptions.tex` appendix -- intentional "blackboard diagrams") |
| **Placeholder figures in non-compiled files** | **8** (in 02_, 03_, 04_, 06_, 07_, 08_, 09_ -- old section files not `\input`-ed) |
| **Real figures in assessed body** | **18** (16 images + 2 in design_rationale) |
| **Real figures in appendices** | **~50** |
| **Duplicate labels (both compiled)** | **10** (will cause LaTeX warnings) |
| **Duplicate labels (one not compiled)** | **3** (harmless) |
| **Missing image files** | **0** in compiled sections (4 in non-compiled, all commented out) |
| **Unreferenced figure labels** | **~30** (most are appendix figures or group labels) |
| **Generated PDFs not used** | **9** |
| **Broken cross-references** | **0** (the old `fig:search-pattern` issue is resolved) |
| **Figures that should exist but don't** | **3 critical, 3 high, 3 medium** |

---

## 9. PRIORITY ACTION ITEMS

### P0: Fix duplicate labels (10 instances, both files compiled)

These cause LaTeX "multiply defined" warnings and may break cross-references. The issue is that `optimization_master.tex`, `path_optimization_definitive.tex`, `design_strategy.tex`, and `design_rationale.tex` all define overlapping labels. Fix by renaming duplicates (e.g., append `_opt`, `_def`, `_ds` suffixes).

Most critical duplicates:
1. `fig:alt-speed-body` -- `design_rationale.tex` vs `optimization_master.tex`
2. `fig:top3-paths` -- `optimization_master.tex` vs `path_optimization_definitive.tex`
3. `fig:energy-heatmap` -- `optimization_master.tex` vs `path_optimization_definitive.tex`
4. `fig:pareto-2d` -- `optimization_master.tex` vs `path_optimization_definitive.tex`
5. `fig:n2-diagram` -- `optimization_master.tex` vs `optimization_formal.tex`
6. `fig:coupling-matrix` -- `optimization_master.tex` vs `design_strategy.tex`
7. `fig:sensitivity-matrix` -- `optimization_master.tex` vs `design_strategy.tex`
8. `fig:sensitivity-spider` -- `optimization_master.tex` vs `design_strategy.tex`
9. `fig:tornado-sensitivity` -- `optimization_master.tex` vs `design_strategy.tex`

### P1: Add 3 real images to replace critical missing visuals

1. **Ground station screenshot** -- run `pi_flight.py` in simulation, screenshot the browser, save as `figs/dashboard_screenshot.png`, uncomment `\includegraphics` in `08_ground_station.tex` (if it gets `\input`-ed) or add to `system_description.tex`.
2. **Detection overlay frame** -- extract a frame from DJI video replay with bounding box overlay, save to `figs/detection_overlay.png`.
3. **Hardware photo** -- photograph assembled drone or ask teammate for a photo.

### P2: Reference body figures that are defined but never `\ref`-ed

- `fig:coupling-body` in `design_rationale.tex` -- defined but text never says "Figure X"
- `fig:pi_system` in `system_description.tex` -- defined but text never says "Figure X" (the architecture paragraph mentions the module graph but not the Pi system diagram)

### P3: Clean up non-compiled old section files

Files `02_system_architecture.tex`, `03_hardware_platform.tex`, `04_computer_vision.tex`, `05_path_planning.tex`, `06_state_machine.tex`, `07_target_localisation.tex`, `08_ground_station.tex`, `09_simulation.tex` are NOT `\input`-ed in `main.tex`. They contain 8 placeholder figures and multiple duplicate labels. Either:
- Delete them (they're superseded by the consolidated body files)
- Move to `_archive/` directory
- Or keep them but ensure they don't cause confusion

### P4: Use the 9 generated but unreferenced PDFs

`decision_flow.pdf`, `detection_subscore.pdf`, `lighting_*.pdf`, `safety_subscore.pdf`, `scoring_overview.pdf`, `state_machine_simple.pdf`, and `system_overview_simple.pdf` all exist but aren't used. The `decision_flow.pdf` is particularly valuable for the body `decision_flow.tex` section.

### P5: Replace figure_descriptions.tex placeholders with real images

The 5 "blackboard diagram" placeholders in `figure_descriptions.tex` are well-written text descriptions but would be far more impactful as actual images. Priority order:
1. Dashboard screenshot (easiest -- just take a screenshot)
2. Detection overlay (extract from video analysis)
3. Lawnmower pattern on satellite (dry-run output `real_dry_run_pattern.jpg` exists in figs/)
4. Hardware photo (need physical photo)
5. Bench test setup (need physical photo)
