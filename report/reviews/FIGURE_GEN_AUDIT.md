# Figure Generation Audit

**Date:** 2026-04-03
**Scope:** `report/figs/` -- all gen scripts, standalone scripts, output files, and .tex references

---

## 1. Generator Scripts (34 total)

### gen_*.py scripts (32 files)

| Script | Output file(s) | Description |
|--------|---------------|-------------|
| `gen_altitude_detection.py` | `altitude_detection_table.pdf/.png` | Altitude vs detection performance -- 3-panel horizontal bar chart (target px, confidence, detection rate by altitude) |
| `gen_altitude_tradeoff_dual.py` | `altitude_tradeoff_dual.pdf/.png` | Two-panel altitude dilemma figure using real physics params from config.py |
| `gen_architecture.py` | `architecture.pdf/.png` | System architecture block diagram (Camera/Pi/Cube/GCS boxes and arrows) |
| `gen_blur_vs_altitude.py` | `blur_vs_altitude.pdf/.png`, `detection_envelope.pdf/.png` | Motion blur vs altitude + detection confidence envelope (TWO outputs) |
| `gen_confusion_matrix.py` | `confusion_matrix.pdf/.png` | YOLOv8n SAR detector confusion matrix on validation set |
| `gen_coupling_matrix.py` | `coupling_matrix.pdf/.png`, `altitude_speed_tradeoff.pdf/.png` | Design coupling matrix + altitude-speed tradeoff (TWO outputs) |
| `gen_cv_pipeline.py` | `cv_pipeline.pdf/.png` | CV detection pipeline flow diagram |
| `gen_detection_heatmap.py` | `detection_heatmap.pdf/.png` | Detection heatmap over search area with lawnmower pattern |
| `gen_detection_subscore.py` | `detection_subscore.pdf/.png` | Spider chart of detection sub-component scores |
| `gen_estimator_comparison.py` | `estimator_comparison.pdf/.png` | CEP50 comparison for 4 GPS estimation methods |
| `gen_function_chain.py` | `function_chain.pdf/.png` | Detection probability as function DAG (variable dependency) |
| `gen_geofence_diagram.py` | `geofence_diagram.pdf/.png` | NFZ geofence protection diagram with actual GPS coordinates, repulsive forces |
| `gen_gps_bullseye.py` | `gps_bullseye.pdf/.png` | GPS bullseye plot -- target estimation accuracy scatter |
| `gen_gps_error_direction.py` | `gps_error_direction.pdf/.png` | GPS error vs flight direction -- timing lag directional bias |
| `gen_lighting_detection.py` | `lighting_detection.pdf/.png`, `lighting_speed.pdf/.png`, `lighting_combined.pdf/.png` | Lighting condition effects on detection (THREE outputs) |
| `gen_mission_overview.py` | `mission_overview.pdf/.png` | Mission overview on Fenswood Wilderness map (requires shapely) |
| `gen_mission_timeline.py` | `mission_timeline.pdf/.png` | Mission timeline/sequence with altitude profile |
| `gen_n2_diagram.py` | `n2_diagram.pdf/.png` | N2 Design Structure Matrix for search mission variables |
| `gen_objective_conflict.py` | `objective_conflict.pdf/.png` | 6 radar charts showing objective conflicts across altitude/speed configs |
| `gen_pareto_2d.py` | `pareto_2d_composite.pdf/.png` | 2D Pareto frontier of 216 altitude/speed/overlap configurations |
| `gen_pareto_alternatives.py` | `pareto_curve.pdf/.png`, `pareto_3d.pdf/.png`, `pareto_parallel.pdf/.png`, `pareto_tradeoff_simple.pdf/.png` | 4 alternative Pareto visualizations (FOUR outputs) |
| `gen_path_planning.py` | `energy_efficiency.pdf/.png`, `nfz_margin_altitude.pdf/.png`, `rotation_comparison.pdf/.png`, `speed_detection_energy.pdf/.png` | Search path planning optimization (FOUR outputs) |
| `gen_pi_system.py` | `pi_system.pdf/.png` | Pi-side system architecture diagram |
| `gen_safety_subscore.py` | `safety_subscore.pdf/.png` | Spider chart of safety sub-component scores |
| `gen_scoring_overview.py` | `scoring_overview.pdf/.png` | Infographic -- constraint vs optimized dimensions |
| `gen_sensitivity_matrix.py` | `sensitivity_matrix.pdf/.png`, `sensitivity_spider.pdf/.png` | Sensitivity heatmap + spider chart (TWO outputs) |
| `gen_state_machine.py` | `state_machine.pdf/.png` | Simplified 10-state state machine diagram |
| `gen_state_machine_full.py` | `state_machine_simple.pdf/.png`, `state_machine_full.pdf/.png` | Simple + full 19-state state machine diagrams (TWO outputs) |
| `gen_system_overview_simple.py` | `system_overview_simple.pdf/.png` | Simplified 1-line system block diagram |
| `gen_top3_paths.py` | `top3_paths.pdf/.png` | Top-3 path configurations from 216-config sweep on search area (requires shapely) |
| `gen_tornado_sensitivity.py` | `tornado_sensitivity.pdf/.png` | Tornado diagram -- parameter sensitivity of composite mission score |
| `gen_training_curves.py` | `training_curves.pdf/.png` | Training convergence curves for YOLOv8n on SAR Dataset v2 |

### Standalone scripts (not gen_* prefixed, 2 files)

| Script | Output file(s) | Description |
|--------|---------------|-------------|
| `decision_flow.py` | `decision_flow.pdf/.png` | 9-step decision flow for optimization strategy (Phase A/B) |
| `optimization_network.py` | `optimization_network.pdf/.png` | Variable dependency/influence network diagram |

### Bulk generator (1 file, in report/ root)

| Script | Output file(s) | Description |
|--------|---------------|-------------|
| `generate_charts.py` | `conf_vs_alt.pdf`, `det_vs_speed.pdf/.png`, `gps_convergence.pdf`, `latency_breakdown.pdf`, `coverage_vs_time.pdf` | 5 charts from system physics parameters. PDF-only for 3 of them (no PNG). |

---

## 2. All Figure Files in figs/ (110 files)

### PDF files (52)
altitude_detection_table, altitude_speed_tradeoff, altitude_tradeoff_dual, architecture, benchmark_comparison, blur_vs_altitude, conf_vs_alt, confusion_matrix, coupling_matrix, coverage_vs_time, cv_pipeline, decision_flow, det_vs_speed, detection_envelope, detection_heatmap, detection_subscore, energy_efficiency, estimator_comparison, function_chain, geofence_diagram, gps_bullseye, gps_convergence, gps_error_direction, latency_breakdown, lighting_combined, lighting_detection, lighting_speed, mission_overview, mission_timeline, n2_diagram, nfz_margin_altitude, objective_conflict, optimization_network, pareto_2d_composite, pareto_3d, pareto_curve, pareto_parallel, pareto_tradeoff_simple, pi_system, rotation_comparison, safety_subscore, scoring_overview, sensitivity_matrix, sensitivity_spider, speed_detection_energy, state_machine, state_machine_full, state_machine_simple, system_overview_simple, top3_paths, tornado_sensitivity, training_curves

### PNG files (61) -- includes 14 "real_*" data-derived plots + 1 JPG
altitude_detection_table, altitude_speed_tradeoff, altitude_tradeoff_dual, architecture, benchmark_comparison, blur_vs_altitude, confusion_matrix, coupling_matrix, cv_pipeline, decision_flow, det_vs_speed, detection_envelope, detection_heatmap, detection_subscore, energy_efficiency, estimator_comparison, function_chain, geofence_diagram, gps_bullseye, gps_error_direction, lighting_combined, lighting_detection, lighting_speed, mission_overview, mission_timeline, n2_diagram, nfz_margin_altitude, objective_conflict, optimization_network, pareto_2d_composite, pareto_3d, pareto_curve, pareto_parallel, pareto_tradeoff_simple, pi_system, rotation_comparison, safety_subscore, scoring_overview, sensitivity_matrix, sensitivity_spider, speed_detection_energy, state_machine, state_machine_full, state_machine_simple, system_overview_simple, top3_paths, tornado_sensitivity, training_curves, **real_altitude_vs_px**, **real_coverage**, **real_detection_envelope**, **real_dry_run_pattern** (JPG), **real_energy_heatmap**, **real_energy_vs_altitude**, **real_optimal_pattern**, **real_path_patterns**, **real_scan_angle**, **real_scan_lines**, **real_search_comparison**, **real_speed_vs_blur**, **real_speed_vs_frames**, **real_time_vs_altitude**

### PDFs with no matching PNG (4)
- `conf_vs_alt.pdf` -- from generate_charts.py (saves PDF only)
- `coverage_vs_time.pdf` -- from generate_charts.py (saves PDF only)
- `gps_convergence.pdf` -- from generate_charts.py (saves PDF only)
- `latency_breakdown.pdf` -- from generate_charts.py (saves PDF only)

### PNGs/JPGs with no matching PDF (14)
All are `real_*` files -- these appear to be generated by `gen_path_planning.py` or the path optimization scripts, not by individual gen_ scripts. No standalone generator found for these; they may come from `gen_path_planning.py` or an external tool.

---

## 3. Figures Referenced in Compiled .tex Sections

### Active references in main.tex-compiled sections (52 unique figure names)
altitude_detection_table, altitude_speed_tradeoff, altitude_tradeoff_dual, architecture, benchmark_comparison, blur_vs_altitude, conf_vs_alt, confusion_matrix, coupling_matrix, coverage_vs_time, cv_pipeline, det_vs_speed, detection_envelope, detection_heatmap, energy_efficiency, estimator_comparison, function_chain, geofence_diagram, gps_bullseye, gps_convergence, gps_error_direction, latency_breakdown, mission_overview, mission_timeline, n2_diagram, nfz_margin_altitude, objective_conflict, optimization_network, pareto_2d_composite, pareto_3d, pareto_curve, pareto_parallel, pareto_tradeoff_simple, pi_system, real_altitude_vs_px, real_coverage, real_detection_envelope, real_energy_heatmap, real_energy_vs_altitude, real_optimal_pattern, real_path_patterns, real_speed_vs_blur, real_speed_vs_frames, rotation_comparison, sensitivity_matrix, sensitivity_spider, speed_detection_energy, state_machine, state_machine_full, top3_paths, tornado_sensitivity, training_curves

### Additional references in reportflow/main.tex (separate document, 14 figures)
altitude_speed_tradeoff, architecture, decision_flow, detection_subscore, lighting_combined, objective_conflict, pareto_parallel, real_energy_heatmap, safety_subscore, scoring_overview, sensitivity_matrix, sensitivity_spider, top3_paths, tornado_sensitivity

Note: `filename` also appears in `figure_descriptions.tex` but this is a placeholder/comment, not a real figure reference.

---

## 4. Missing Figures (referenced in .tex but NOT in figs/)

**NONE.** All figures referenced via active `\includegraphics` in compiled sections exist as files in `figs/`. This is clean.

Previously-identified missing figures (`hardware_block_diagram`, `dashboard_screenshot`, `gps_scatter`) are all in COMMENTED-OUT `\includegraphics` lines in sections that use `\fbox` placeholders, so they do not cause compilation errors.

---

## 5. Orphaned Figures (in figs/ but NOT referenced in any compiled .tex)

| Figure | Has gen script? | Notes |
|--------|----------------|-------|
| `lighting_detection.pdf/.png` | Yes (`gen_lighting_detection.py`) | Only `lighting_combined` is referenced; single-panel versions unused |
| `lighting_speed.pdf/.png` | Yes (same script) | Same -- combined version used instead |
| `system_overview_simple.pdf/.png` | Yes (`gen_system_overview_simple.py`) | Not referenced in any compiled section |
| `state_machine_simple.pdf/.png` | Yes (`gen_state_machine_full.py`) | `state_machine` is used (from `gen_state_machine.py`), not this simplified variant |
| `benchmark_comparison.pdf/.png` | Yes (unknown generator -- no gen_ script found) | Referenced in `inference_architecture.tex` which IS compiled -- actually NOT orphaned |
| `real_dry_run_pattern.jpg` | No gen script | Likely a manual screenshot/export |
| `real_scan_angle.png` | No gen script | Not referenced in compiled .tex |
| `real_scan_lines.png` | No gen script | Not referenced in compiled .tex |
| `real_search_comparison.png` | No gen script | Not referenced in compiled .tex |
| `real_time_vs_altitude.png` | No gen script | Not referenced in compiled .tex |
| `altitude_detection_table.pdf/.png` | Yes (`gen_altitude_detection.py`) | Referenced in `cv_extended.tex` -- NOT orphaned |

**Truly orphaned (7 files, never referenced in any compiled section):**
- `lighting_detection.pdf/.png`
- `lighting_speed.pdf/.png`
- `system_overview_simple.pdf/.png`
- `state_machine_simple.pdf/.png`
- `real_dry_run_pattern.jpg`
- `real_scan_angle.png`
- `real_scan_lines.png`
- `real_search_comparison.png`
- `real_time_vs_altitude.png`

---

## 6. Figures Without a Generator Script

These figures exist in figs/ but have no corresponding gen_*.py or standalone .py script:

| Figure | Source |
|--------|--------|
| `benchmark_comparison.pdf/.png` | Unknown -- no gen script found. May have been manually created or from an earlier session. |
| `conf_vs_alt.pdf` | `generate_charts.py` (report root) |
| `det_vs_speed.pdf/.png` | `generate_charts.py` (report root) |
| `gps_convergence.pdf` | `generate_charts.py` (report root) |
| `latency_breakdown.pdf` | `generate_charts.py` (report root) |
| `coverage_vs_time.pdf` | `generate_charts.py` (report root) |
| All `real_*` files (14) | Likely from `gen_path_planning.py` or an external optimization script. No individual generators. |

---

## 7. Recommendations

### High Priority

1. **`generate_charts.py` outputs lack PNGs.** Three figures (`conf_vs_alt`, `gps_convergence`, `latency_breakdown`) are saved as PDF only with no PNG fallback. The other gen scripts all produce both formats. Consider re-running `generate_charts.py` after adding `.png` saves alongside `.pdf` saves for consistency and preview convenience.

2. **`benchmark_comparison` has no generator.** This figure is actively referenced in `inference_architecture.tex` but has no reproducible gen script. If data changes, it cannot be regenerated. Create a `gen_benchmark_comparison.py` script or document how it was originally produced.

3. **`real_*` figures have no individual generators.** 14 data-derived plots (real_altitude_vs_px, real_coverage, etc.) exist as PNG only with no PDF versions and no clear generator script. 9 of them ARE referenced in compiled sections (vision_performance.tex, path_optimization_definitive.tex). If data changes, these cannot be regenerated. Document or create their generator.

### Medium Priority

4. **Naming inconsistency: 2 standalone scripts not prefixed `gen_`.** `decision_flow.py` and `optimization_network.py` should be renamed to `gen_decision_flow.py` and `gen_optimization_network.py` for consistency with the 32 other generators.

5. **`generate_charts.py` in report/ root vs gen_*.py in figs/.** The 5 charts from `generate_charts.py` could be migrated into individual `gen_*.py` files in figs/ for consistency. Currently there are two different generation patterns.

6. **Orphaned figures cleanup.** 9 figures are never referenced in compiled .tex. They consume space and cause confusion. Either reference them in a section or move to an archive directory.

### Low Priority

7. **Multi-output scripts.** Several gen scripts produce 2-4 outputs (gen_blur_vs_altitude, gen_coupling_matrix, gen_lighting_detection, gen_pareto_alternatives, gen_path_planning, gen_sensitivity_matrix, gen_state_machine_full). This makes the script-to-figure mapping non-obvious. Consider adding a comment block at the top of each listing all outputs, or creating a manifest file.

8. **Regeneration opportunity.** All gen scripts use hardcoded physics parameters (FOCAL_MM=5.46, SENSOR_W_MM=5.02, FPS=4.8, etc.) that match config.py. If config values change, all scripts need manual updating. A shared `params.py` import would prevent drift.

9. **`real_*` figures are PNG-only.** For a LaTeX report, PDF is preferred (vector, smaller, crisper at any zoom). If these are from matplotlib, re-running with `.pdf` saves would improve print quality.

---

## 8. Summary Statistics

| Metric | Count |
|--------|-------|
| Generator scripts (gen_*.py) | 32 |
| Standalone generator scripts | 2 (decision_flow.py, optimization_network.py) |
| Bulk generator (generate_charts.py) | 1 (produces 5 figures) |
| Total unique figure basenames | 66 |
| PDF files | 52 |
| PNG files | 60 |
| JPG files | 1 |
| Figures referenced in compiled .tex | 52 |
| Figures referenced in reportflow/main.tex | 14 |
| Missing figures (referenced but not present) | 0 |
| Orphaned figures (present but not referenced) | 9 |
| Figures with no generator script | 15 (1 benchmark + 14 real_*) |
