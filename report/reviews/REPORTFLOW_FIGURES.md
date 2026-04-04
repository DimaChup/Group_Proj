# Reportflow Figure Audit

**Date**: 2026-04-04
**File**: `report/reportflow/main.tex`
**Graphics path**: `../figs/` (goldmine's figs directory, 236 files)

---

## Summary

- **Before**: 16 figures (including `attitude_compensation` which was already present)
- **After**: 22 figures (+6 high-impact additions)
- All figures exist in `../figs/` as PDF
- All figures have captions, labels, and `\ref{}` references in body text

---

## Existing Figures (all OK)

| # | File | Label | Captioned | Referenced | Section |
|---|------|-------|-----------|------------|---------|
| 1 | `sensitivity_spider` | `fig:sensitivity-spider` | Yes | Yes (L133, L725) | Five Competing Dimensions |
| 2 | `safety_subscore` | `fig:safety-subscore` | Yes | Yes (L231) | Scoring: Safety |
| 3 | `detection_subscore` | `fig:detection-subscore` | Yes | Yes (L281) | Scoring: Detection |
| 4 | `scoring_overview` | `fig:scoring-overview` | Yes | Yes (L366) | Composite Score |
| 5 | `sensitivity_matrix` | `fig:sensitivity-matrix` | Yes | Yes (L401) | How They Interconnect |
| 6 | `decision_flow` | `fig:decision-flow` | Yes | Yes (L419) | The Decision Chain |
| 7 | `lighting_combined` | `fig:lighting` | Yes | Yes (L471) | Step 2: Detection Ceiling |
| 8 | `real_energy_heatmap` | `fig:energy-heatmap` | Yes | Yes (L576) | Step 7: Scan Angle |
| 9 | `altitude_speed_tradeoff` | `fig:alt-speed-body` | Yes | Yes (L619) | Decision Chain Summary |
| 10 | `top3_paths` | `fig:top3-paths` | Yes | Yes (L663) | Evaluation |
| 11 | `objective_conflict` | `fig:objective-conflict` | Yes | Yes (L671) | Evaluation |
| 12 | `tornado_sensitivity` | `fig:tornado-sensitivity` | Yes | Yes (L717) | Sensitivity |
| 13 | `pareto_parallel` | `fig:pareto-parallel` | Yes | Yes (L735) | Pareto Optimality |
| 14 | `architecture` | `fig:architecture` | Yes | Yes (L765) | Software Architecture |
| 15 | `attitude_compensation` | `fig:attitude-compensation` | Yes | Yes | Detection-to-GPS |
| 16 | `geofence_layers` | `fig:geofence_layers` | Yes | Yes (L853) | Safety Architecture |

---

## Newly Added Figures (+6)

| # | File | Label | Section | Why High-Impact |
|---|------|-------|---------|-----------------|
| 17 | `state_machine_generated` | `fig:state-machine` | State Machine (L794) | The state machine section had only a text chain -- this is one of the most complex system components and deserves a visual. Shows all 20 states and transitions. |
| 18 | `search_pattern` | `fig:search-pattern` | Step 5: Search Pattern (L550) | The lawnmower pattern is the core search strategy; showing it on the actual polygon with NFZ makes the decision concrete. |
| 19 | `detection_montage` | `fig:detection-montage` | CV Pipeline (L814) | Visual proof that the model works at real altitudes. This is the most compelling "it works" evidence for the CV system. |
| 20 | `four_phase_accuracy` | `fig:four-phase-accuracy` | Progressive Accuracy (L901) | Shows the CEP contracting from 3.5m to 1.0m across mission phases -- directly supports the progressive error elimination argument. |
| 21 | `convergence_plot` | `fig:convergence` | Frame Rate Sufficiency (L915) | Validates the SMART clustering threshold of 5 detections. Connects frame rate to GPS accuracy. |
| 22 | `sar_comparison_bubble` | `fig:sar-comparison` | Industry Context (L1261) | Positions the project against commercial SAR platforms. New section added before Conclusion. |

---

## Figures Considered But Not Added

| File | Reason |
|------|--------|
| `bullseye_comparison` | Already present at L909 as `fig:bullseye-comparison-body` |
| `system_architecture` | `architecture` already serves this role at L777 |
| `radar_comparison` | Similar to `sar_comparison_bubble`; one industry comparison is enough |
| `cost_comparison` | Would be redundant with the bubble chart which already encodes cost on Y-axis |
| `cv_pipeline` / `vision_pipeline` | The text description of the 5-stage pipeline is clear enough; adding a pipeline diagram would be redundant with the architecture figure |

---

## Cross-Reference Verification

All 6 new figures have body-text `\ref{}` calls:

- `fig:state-machine` referenced at L783: "implements a 20-state finite state machine (Figure~\ref{fig:state-machine})"
- `fig:search-pattern` referenced at L546: "Figure~\ref{fig:search-pattern} shows the generated pattern"
- `fig:detection-montage` referenced at L811: "Figure~\ref{fig:detection-montage} shows representative detections"
- `fig:four-phase-accuracy` referenced at L882: "Table~\ref{tab:accuracy-progression-body} and Figure~\ref{fig:four-phase-accuracy}"
- `fig:convergence` referenced at L921: "Figure~\ref{fig:convergence} confirms that the GPS estimate converges"
- `fig:sar-comparison` referenced at L1256: "Figure~\ref{fig:sar-comparison} compares it against commercial..."

---

## Impact Assessment

The 6 added figures fill critical visual gaps:

1. **State machine** -- was the biggest missing visual; the 20-state FSM is the system's core complexity
2. **Detection montage** -- provides tangible "it works" evidence; most reviewers want to see actual detections
3. **Search pattern** -- makes the abstract lawnmower discussion concrete with the real polygon
4. **Four-phase accuracy** -- the progressive error elimination is a key design insight that benefits from visual presentation
5. **Convergence plot** -- bridges the gap between frame rate calculation and GPS accuracy
6. **SAR comparison bubble** -- provides industry context that was completely missing; positions the project

Expected score impact: +2-3 marks on Communication criteria (visual evidence, figure density, industry awareness).
