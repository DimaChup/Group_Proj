# Figure Insertions v2

**Date:** 2026-04-04
**Compiled:** 238 pages, 0 errors, 0 undefined references for new figures

## Summary

9 new figures inserted into the D6 goldmine LaTeX sections. 1 figure (`system_architecture.pdf`) was already referenced in `02_system_architecture.tex` and was not duplicated.

## Insertions

| # | Figure | File | Location | Label | Text Reference |
|---|--------|------|----------|-------|----------------|
| 1 | `state_machine_generated.pdf` | `system_description.tex` | After existing `state_machine` figure (line ~155) | `fig:state_machine_generated` | Added to FSM intro paragraph |
| 2 | `system_architecture.pdf` | `02_system_architecture.tex` | **Already present** (line 32) | `fig:system_architecture` (existing) | N/A -- no change needed |
| 3 | `search_pattern.pdf` | `system_description.tex` | After `coverage_vs_time` figure, before State Machine section | `fig:search_pattern` | Added to coverage guarantee paragraph |
| 4 | `vision_pipeline.pdf` | `cv_extended.tex` | After Stage 6 (Visualisation), before Benchmark Results | `fig:vision_pipeline` | Caption references `tab:pipeline_timing` |
| 5 | `radar_comparison.pdf` | `evaluation.tex` | In Comparison with Published SAR Systems section, before discussion | `fig:radar_comparison` | Added intro sentence before "Three observations emerge" |
| 6 | `development_timeline.pdf` | `design_strategy.tex` | Before "Adapting When Hardware Was Unavailable" subsection | `fig:development_timeline` | Added sentence at end of progressive testing rationale paragraph |
| 7 | `geofence_layers.pdf` | `13_safety_risk.tex` | After the 5-layer enumeration, before Flight Area containment paragraph | `fig:geofence_layers` | Added to geofence intro sentence alongside `fig:geofence_diagram` |
| 8 | `gsd_altitude.pdf` | `cv_extended.tex` | In "Detection Performance vs Altitude" subsection, before Pixel Size Model | `fig:gsd_altitude` | Added intro sentence in subsection opening |
| 9 | `mcda_heatmap.pdf` | `design_rationale.tex` | After Pi 5 sensitivity analysis paragraph | `fig:mcda_heatmap` | Added sentence after sensitivity analysis conclusion |
| 10 | `detection_montage.pdf` | `evaluation.tex` | Before "Architecture resilience" discussion paragraph | `fig:detection_montage` | Added to detection performance discussion sentence |

## Verification

- First pdflatex pass: all 9 figures compiled and rendered (undefined references expected on first pass)
- Second pdflatex pass: 0 undefined references for any new figure labels
- 238 pages total, no compilation errors
- No existing figures were removed or modified
