# Cross-Reference Audit v2

**Date:** 2026-04-03
**Scope:** All `\ref{}` in `report/sections/*.tex` checked against all `\label{}` in `sections/*.tex` + `main.tex`

## Summary

| Metric | Count |
|--------|-------|
| Unique `\ref{}` keys in sections/ | 312 |
| Unique `\label{}` keys in sections/ + main.tex | 747 |
| **Broken refs (no matching label)** | **3 found, 2 fixed** |
| Duplicate labels across all section files | 21 (but 0 among files actually `\input`'d by main.tex) |
| Unused labels (defined but never referenced) | 435 |

## Broken References (FIXED)

All 3 broken references were in `gps_estimation_deep.tex`. Two were fixable; one was a false positive from the initial scan (already correct in the file).

### 1. `\ref{tab:gsd-values}` -- FIXED
- **File:** `sections/gps_estimation_deep.tex`, line 1469
- **Problem:** No `\label{tab:gsd-values}` exists anywhere
- **Correct label:** `tab:gsd-altitude` (same file, line 197)
- **Fix:** Changed `\ref{tab:gsd-values}` to `\ref{tab:gsd-altitude}`

### 2. `\ref{sec:flight-testing}` -- FIXED
- **File:** `sections/gps_estimation_deep.tex`, line 2212
- **Problem:** No `\label{sec:flight-testing}` exists
- **Correct label:** `sec:flight-progression` (in `test_scripts_guide.tex`, line 25)
- **Fix:** Changed `\ref{sec:flight-testing}` to `\ref{sec:flight-progression}`

### 3. `\ref{sec:req-detail}` -- FALSE POSITIVE
- **Initial scan artifact.** The actual files use `\ref{app:req-detail}` which correctly matches `\label{app:req-detail}` in `requirements_detail.tex`. No fix needed.

## Duplicate Labels (informational)

21 labels are defined in more than one `.tex` file under `sections/`, but **none conflict among the files actually included by `main.tex`**. The duplicates exist between:
- Numbered section files (`01_introduction.tex`, `02_system_architecture.tex`, etc.) -- NOT included
- Active section files (`introduction.tex`, `system_description.tex`, etc.) -- INCLUDED

Since only one version is `\input`'d, LaTeX will not emit "multiply-defined label" warnings. No action needed.

**Duplicate labels (for reference):**
`eq:focal-length`, `eq:focal-px`, `eq:gsd`, `eq:power`, `fig:architecture`, `fig:coverage_vs_time`, `fig:cv_pipeline`, `fig:state_machine`, `sec:cv`, `sec:groundstation`, `sec:intro`, `sec:lens-calibration`, `sec:localisation`, `sec:objectives`, `sec:report-structure`, `sec:simulation`, `sec:steeple`, `tab:cv_benchmarks`, `tab:hw-bom`, `tab:mavlink-commands`, `tab:steeple`

## Unused Labels (informational, not errors)

435 labels are defined but never referenced by any `\ref{}`. This is normal for a large report -- labels exist for potential future cross-referencing. The breakdown:

| Category | Count | Notes |
|----------|-------|-------|
| `fig:` | 35 | Figures that exist but are not cross-referenced from text |
| `tab:` | 25 | Tables not cross-referenced |
| `sec:` | ~240 | Section labels for potential linking |
| `eq:` | ~95 | Equation labels for potential linking |
| `app:` | 8 | Appendix labels |

These are not errors. Many are in appendix sections or deep-dive sections that are self-contained. No cleanup recommended -- removing labels would prevent future cross-referencing.

## Verification

After fixes, re-running the audit shows **0 broken references**.
