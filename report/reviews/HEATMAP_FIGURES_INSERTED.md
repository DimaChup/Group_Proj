# Heatmap Figures Inserted — 2026-04-04

## Summary

Three new estimation figures inserted into `report/sections/estimation_evaluation.tex` and cross-referenced from the body evaluation section.

## Figures Inserted

### 1. `estimation_heatmap_all.pdf` — Centrality-heatmapped bullseye
- **Location**: Bullseye Visualization subsection (after `bullseye_comparison` figure)
- **Label**: `fig:estimation-heatmap-all`
- **Placement**: `[H]`, width 0.6\textwidth
- **Caption**: Describes centrality weighting colour-mapping of all 53 GPS estimates, warm=high-weight near-centre, cool=low-weight edge detections
- **Narrative**: Connecting paragraph links it to the centrality weighting function in Figure `centrality-weighting`

### 2. `estimation_averaging.pdf` — Running average convergence + SMART lock
- **Location**: "When Is Enough Data Enough?" subsection, before the existing `gps_convergence` figure
- **Label**: `fig:estimation-averaging`
- **Placement**: `[H]`, width 0.65\textwidth
- **Caption**: Two-panel figure — upper shows lat/lon convergence toward ground truth with SMART lock event marked, lower shows instantaneous CEP vs detection count

### 3. `estimation_error_vs_detections.pdf` — Error vs N for 4 methods
- **Location**: Clustering Threshold Comparison sub-subsection, immediately before the paragraph analysis of threshold configurations (before "Single frame" paragraph)
- **Label**: `fig:estimation-error-vs-detections`
- **Placement**: `[H]`, width 0.65\textwidth
- **Caption**: CEP50 vs accumulated detections for single-frame, rolling average, Kalman, and IVW methods; GPS noise floor shown as dashed line
- **Narrative**: Introductory sentence connects to Table `clustering-tradeoffs`

## Body Evaluation Cross-Reference

- `report/sections/evaluation.tex` line 125: Added reference to `fig:estimation-heatmap-all` in the GPS estimation accuracy paragraph (D3), extending the existing parenthetical that already cited `gps_bullseye` and `gps_error_direction`

## Compilation

- Two-pass pdflatex: **244 pages, 0 errors** related to the new figures
- All three `\ref{}` and `\label{}` pairs resolve correctly
- Pre-existing undefined citations (unrelated) unchanged
