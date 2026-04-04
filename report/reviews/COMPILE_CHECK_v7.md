# Compile Check v7 — 2026-04-04

Build chain: `pdflatex -> biber -> pdflatex -> pdflatex -> pdflatex` (5 passes, clean aux)

## Summary

| Metric | Before fixes | After fixes |
|--------|-------------|-------------|
| Pages | 253 (pre-biber: 252) | **252** |
| Errors (`!`) | 0 | **0** |
| Undefined citations | 7 (3 keys: sun2016sar, sambolek2025person, gautam2018error) | **0** |
| Undefined references | 0 | **0** |
| Missing figures | 0 | **0** |
| Float overflow | 0 | **0** |
| Overfull hbox (total) | 61 | **44** |
| Overfull hbox (>10pt) | 20 | **8** |
| Overfull vbox | 3 | **3** |
| Underfull | 216 | **216** |
| Rerun needed | No | **No** |

## Root Cause: Undefined Citations

The initial compile (`pdflatex` only, no biber) showed 7 undefined citation warnings for 3 keys.
All 3 keys exist in `references.bib` (lines 1137, 1183, 1193). The citations were used in
`sections/estimation_evaluation.tex` and `sections/localization_approaches.tex`.

**Fix:** Running the full `pdflatex -> biber -> pdflatex -> pdflatex` chain resolves all
undefined citations. The previous compile check likely ran only `pdflatex` without `biber`.

## Fixes Applied

### 1. Undefined citations (7 -> 0)
- Ran biber to resolve all bibliography entries.

### 2. Overfull hbox reductions (20 -> 8 severe)

| File | Issue | Fix |
|------|-------|-----|
| `contingency.tex` L221 | Test-script mapping table: `\texttt{}` paths too long for 3.8cm column | Shortened script names, reduced column widths to `p{2.2cm}p{3.2cm}X` |
| `contingency.tex` L64 | Long `\texttt{cv_models/...}` path in stretch goals | Added `\allowbreak{}` in path |
| `A2_config_params.tex` L14 | Config table: `llll` columns don't wrap | Changed to `p{5.2cm}lll` + `\scriptsize` |
| `requirements_verification.tex` L10 | Verification table overflows | Changed to `\scriptsize`, adjusted column widths |
| `cv_extended.tex` L222 | Altitude performance table: Assessment column too wide | Changed last column from `l` to `p{4.5cm}` |
| `simulation_validation.tex` L15 | Validation matrix headers too wide | Changed to `\footnotesize`, first column to `p{4.2cm}` |
| `inference_architecture.tex` L53 | Long `\texttt{TFLITE_XNNPACK_...}` constant | Added `\allowbreak{}` |
| `calibration_deep.tex` L43 | Dense paragraph with multiple `\texttt{}` calls | Added discretionary hyphens (`\-`) in function names |
| `focus_and_repulsive.tex` L127 | Long paragraph with `\texttt{}` flag | Reformulated sentence for better line breaking |
| `gps_estimation_deep.tex` L56 | Accuracy progression table slightly wide | Added `\small` before tabular |

### 3. Float overflow / vbox fixes

| File | Issue | Fix |
|------|-------|-----|
| `evaluation.tex` L111, L170 | `[H]` placement forced figures, causing 525pt vbox overflow | Changed to `[htbp]`, added `\FloatBarrier` between subsections |
| `evaluation.tex` all tables | `[ht]` placement too restrictive | Changed all to `[htbp]` |
| `contingency.tex` L10/34/89 | `[ht]` tables accumulating | Changed all to `[htbp]`, added `\FloatBarrier` before Contingency Plans subsection |

## Remaining Warnings (acceptable)

### Overfull hbox >10pt (8 remaining)
These are all in dense appendix tables with long `\texttt{}` parameter names. None exceed 46pt.
Further reduction would require switching to `\tiny` or restructuring the tables.

| pt | File |
|----|------|
| 45.2 | A2_config_params.tex (NFZ param names) |
| 25.2 | requirements_verification.tex |
| 19.6 | focus_and_repulsive.tex |
| 19.3 | estimation_evaluation.tex |
| 17.8 | evaluation_detail.tex |
| 14.6 | requirements_verification.tex |
| 12.8 | gps_estimation_deep.tex |
| 10.5 | requirements_detail.tex |

### Overfull vbox (3 remaining)
| pt | File | Cause |
|----|------|-------|
| 260.5 | evaluation.tex | Consecutive figures/tables; LaTeX places them on float pages |
| 176.3 | contingency.tex | Multiple consecutive tables |
| 28.6 | system_description.tex | Minor float placement |

These are cosmetic float-page overflows, not content errors.

### Underfull (216)
All are badness warnings in paragraph/table line-breaking. Standard for a 252-page
document with many tables and `\texttt{}` identifiers. No action needed.

### Font warning (1)
`OMS/lmtt/m/n` undefined — standard Latin Modern monospace has no math symbols
font shape. Benign; LaTeX substitutes automatically.

### Biber warning (1)
Invalid ISBN format in `sheridan2002humans` entry. Cosmetic only.

## Verdict

**CLEAN BUILD.** Zero errors, zero undefined references, zero missing figures.
The 8 remaining severe hbox overflows are all in dense parameter tables in appendices
and do not affect readability. The 3 vbox overflows are standard float-page behavior.
