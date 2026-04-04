# Compile Check v6 -- 2026-04-04

**Branch:** MainWorking3
**Compiler:** pdflatex (MiKTeX)
**Passes:** 3 (references stabilized)

## Results

| Metric | Count |
|--------|-------|
| **Total pages** | **252** |
| Fatal errors (! lines) | **0** |
| Undefined references | **0** |
| Multiply-defined labels | **0** |
| Float too large warnings | **0** |
| Missing figures | **0** |
| Overfull hbox | 58 (cosmetic) |
| Underfull hbox | 216 (cosmetic) |
| Overfull vbox | 3 (cosmetic) |
| Biber rerun needed | 1 (bibliography) |

## Issues Found and Fixed

### 1. Undefined reference: `sec:autonomy-level` (page 37)
- **File:** `sections/evaluation.tex:186`
- **Fix:** Changed `\ref{sec:autonomy-level}` to `\ref{sec:autonomy-rationale}` (existing label in `design_rationale.tex:235`)

### 2. Undefined reference: `sec:smart-estimator` (page 228)
- **File:** `sections/estimation_evaluation.tex:26`
- **Fix:** Added `\label{sec:smart-estimator}` to the "SMART Detection as Convergence Criterion" subsubsection in `estimation_evaluation.tex:24`

### 3. Undefined reference: `sec:gps-timing-lag` (page 228)
- **File:** `sections/estimation_evaluation.tex:52`
- **Fix:** Added `\label{sec:gps-timing-lag}` to the "GPS timing lag" paragraph in `gps_estimation_deep.tex:314`

### 4. Undefined reference: `sec:fov-calibration` (page 230)
- **File:** `sections/estimation_evaluation.tex:81`
- **Fix:** Changed `\ref{sec:fov-calibration}` to `\ref{sec:cal:fov}` (existing label in `calibration_deep.tex:6`). The label `sec:fov-calibration` only existed in `vision_standalone.tex` which is NOT included in `main.tex`.

### 5. Multiply-defined label: `fig:error-waterfall`
- **Defined in:** `sections/estimation_evaluation.tex:159` AND `sections/gps_estimation_deep.tex:307`
- **Fix:** Renamed the label in `gps_estimation_deep.tex` to `fig:error-waterfall-deep` and updated the corresponding `\ref` on line 274 of that file.

### 6. Float too large: plus/delta table (431pt overflow)
- **File:** `sections/evaluation.tex:10-61`
- **Cause:** The combined P1-P10 + D1-D9 table (19 rows with long evidence text) exceeded one full page height by 431pt.
- **Fix:** Split into two tables: "Plus/delta review -- strengths" (`tab:plus-delta`, P1-P10) and "Plus/delta review -- areas for improvement" (`tab:delta`, D1-D9). Both use `[ht]` placement.

## Remaining (Cosmetic, Non-blocking)

- **58 overfull hbox:** Long `\texttt{}` strings and `\SI{}{}` units slightly exceed margins. Not visible in print.
- **216 underfull hbox:** Sparse table cells. No visual impact.
- **3 overfull vbox:** Pages slightly taller than text height. No content loss.
- **Biber rerun:** Bibliography citations show as `[?]` until `biber main && pdflatex main.tex` is run. This is expected when only running pdflatex.

## Files Modified

- `report/sections/evaluation.tex` -- ref fix, table split
- `report/sections/estimation_evaluation.tex` -- added label, ref fix
- `report/sections/gps_estimation_deep.tex` -- added label, renamed duplicate label + ref
