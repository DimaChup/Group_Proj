# Missing Figures Check (2026-04-04)

## Summary

**All 72 referenced figures exist in `figs/`.** No missing figure files.

Two `\fbox{}` placeholder figures remain in INCLUDED sections. Several older sections
(not included in `main.tex`) also have placeholders but are harmless.

---

## 1. Missing Figure Files: NONE

Every `\includegraphics` in every included `.tex` file resolves to an existing file
in `figs/` (as `.pdf` or `.png`). LaTeX will compile without "file not found" errors.

## 2. `figs/` Prefix Issue (estimation_evaluation.tex)

`estimation_evaluation.tex` (included at line 378 of `main.tex`) uses explicit
`{figs/...}` paths in 10 `\includegraphics` calls:

| Line | Reference |
|------|-----------|
| 60 | `{figs/gps_bullseye}` |
| 69 | `{figs/bullseye_comparison}` |
| 157 | `{figs/error_waterfall}` |
| 166 | `{figs/error_budget_breakdown}` |
| 181 | `{figs/centrality_weighting}` |
| 224 | `{figs/estimator_comparison}` |
| 235 | `{figs/gps_convergence}` |
| 244 | `{figs/convergence_plot}` |
| 262 | `{figs/gps_error_direction}` |
| 271 | `{figs/heading_bias}` |

Since `main.tex` sets `\graphicspath{{figs/}}`, LaTeX first tries `figs/figs/gps_bullseye`
(fails), then falls back to the literal path `figs/gps_bullseye` (succeeds). This works
but is **inconsistent** with every other section file which uses bare names like
`{gps_bullseye}`. Recommend removing the `figs/` prefix for consistency.

## 3. `\fbox{}` Placeholders in INCLUDED Sections

### 3a. Simulator screenshot (`sections/09_simulation.tex`, line 77) -- NOT INCLUDED

This section is **not** `\input` in `main.tex`, so it is harmless. The simulator
screenshot placeholder describes a 2x2 layout (god view, camera, bullseye, dashboard).

**Status**: NOT IN COMPILED DOCUMENT. No action needed.

### 3b. Dashboard screenshot (`sections/08_ground_station.tex`, line 37) -- NOT INCLUDED

Also **not** `\input` in `main.tex`. Has a commented-out `\includegraphics{dashboard_screenshot}`
and an `\fbox` placeholder.

**Status**: NOT IN COMPILED DOCUMENT. No action needed.

### 3c. Testing tiers diagram (`sections/testing_deep.tex`, lines 22-30) -- INCLUDED

These `\fbox` calls are **decorative** (tier labels in a tabular layout), not missing
figure placeholders. They render as labeled boxes showing "Tier 1 SITL Simulation",
"Tier 2 Bench Test", etc. This is intentional design.

**Status**: OK, no action needed.

### 3d. Figure descriptions (`sections/figure_descriptions.tex`) -- COMMENTED OUT

Line 393 of `main.tex`: `% \input{sections/figure_descriptions}`. Not compiled.

**Status**: NOT IN COMPILED DOCUMENT. No action needed.

## 4. PNG-Only Figures (no PDF version)

These 13 figures exist only as `.png` (no `.pdf`). LaTeX handles `.png` fine but
`.pdf` is preferred for vector graphics quality. All 9 that are referenced in included
sections will compile correctly.

Referenced in included sections:
- `real_altitude_vs_px.png` (vision_performance.tex)
- `real_coverage.png` (vision_performance.tex)
- `real_detection_envelope.png` (vision_performance.tex)
- `real_energy_heatmap.png` (path_optimization_definitive.tex, optimization_master.tex)
- `real_energy_vs_altitude.png` (path_optimization_definitive.tex)
- `real_optimal_pattern.png` (path_optimization_definitive.tex)
- `real_path_patterns.png` (path_optimization_definitive.tex)
- `real_speed_vs_blur.png` (vision_performance.tex)
- `real_speed_vs_frames.png` (vision_performance.tex)

Not referenced (unused):
- `real_dry_run_pattern.jpg`
- `real_scan_angle.png`
- `real_scan_lines.png`
- `real_search_comparison.png`
- `real_time_vs_altitude.png`

**Status**: These are likely raster screenshots/plots. No action needed unless vector
quality is desired.

## 5. Commented-Out References (harmless)

| File | Line | Reference | Status |
|------|------|-----------|--------|
| 07_target_localisation.tex | 127 | `figures/gps_scatter.pdf` | Commented out, section not included |
| 08_ground_station.tex | 36 | `dashboard_screenshot` | Commented out, section not included |

## 6. Sections NOT Included in main.tex (with figure references)

These old numbered sections have been replaced by consolidated sections and are not
compiled. Their figure references are irrelevant:

- `sections/02_system_architecture.tex` (replaced by `system_description.tex`)
- `sections/03_hardware_platform.tex`
- `sections/04_computer_vision.tex`
- `sections/05_path_planning.tex`
- `sections/06_state_machine.tex`
- `sections/07_target_localisation.tex`
- `sections/08_ground_station.tex`
- `sections/09_simulation.tex`
- `sections/search_optimization.tex` (commented out at line 351)
- `sections/figure_descriptions.tex` (commented out at line 393)

## 7. Recommended Actions

| Priority | Action | Effort |
|----------|--------|--------|
| LOW | Remove `figs/` prefix from 10 references in `estimation_evaluation.tex` | 2 min |
| NONE | All figures exist, no missing files | -- |
| NONE | fbox placeholders are in non-included sections or decorative | -- |

## Verdict

**The report will compile without any missing figure errors.** The only cleanup is
cosmetic: removing redundant `figs/` prefixes in `estimation_evaluation.tex`.
