# Reportflow Compilation Report

**Date:** 2026-04-04
**File:** `report/reportflow/main.tex`
**Build tool:** pdflatex + bibtex (MiKTeX 25.12)

## Result: COMPILES CLEANLY

- **Pages:** 32
- **Errors:** 0
- **Undefined references:** 0
- **Undefined citations:** 0
- **Overfull hboxes:** 0
- **Underfull hboxes:** 16 (cosmetic, all in tables/paragraphs)
- **Missing figures:** 0 (all 22 figures resolved)

## Build Sequence

Full clean build requires 4 passes:
```
rm -f main.aux main.out main.log main.toc main.bbl main.blg
pdflatex -interaction=nonstopmode main.tex
bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
```

## Bibliography

- **Engine:** natbib with `plainnat` style (`[numbers,sort&compress]`)
- **Bib file:** `../references.bib` (shared with goldmine report)
- **Citations resolved:** 16 entries from .bib
- All `\cite{}` keys have matching entries in references.bib

## Figures (22 total, all found)

All figures live in `../figs/` (i.e. `report/figs/`). All 22 exist as PDF or PNG:

| Figure key | Format |
|---|---|
| sensitivity_spider | PDF |
| safety_subscore | PDF |
| detection_subscore | PDF |
| scoring_overview | PDF |
| sensitivity_matrix | PDF |
| decision_flow | PDF |
| lighting_combined | PDF |
| search_pattern | PDF |
| real_energy_heatmap | PNG |
| altitude_speed_tradeoff | PDF |
| top3_paths | PDF |
| objective_conflict | PDF |
| tornado_sensitivity | PDF |
| pareto_parallel | PDF |
| architecture | PDF |
| state_machine_generated | PDF |
| detection_montage | PDF |
| four_phase_accuracy | PDF |
| bullseye_comparison | PDF |
| convergence_plot | PDF |
| geofence_layers | PDF |
| radar_comparison | PDF |

## Fixes Applied (2 issues)

### 1. Table row terminators (CRITICAL)
**Lines 1071-1082:** SAR comparison table used single `\` instead of `\\` for row endings.
This caused `! Misplaced \noalign`, `! Extra alignment tab`, and 105pt overfull hbox errors.
**Fix:** Changed all 8 row-ending `\` to `\\`.

### 2. Overfull hbox in TFLite bug paragraph
**Line 1011:** Long paragraph with multiple `\texttt{}` monospace words (e.g. `PIXEL_COORD_THRESHOLD`) could not be broken by LaTeX.
21.7pt overfull.
**Fix:** Wrapped paragraph in `{\sloppy ... \par}` to allow looser line breaking.

## Document Structure

- 1124 lines of LaTeX
- 82 labels defined
- 18 sections, 14 subsections, 7 subsubsections
- Executive Summary + 16 numbered sections + bibliography
- Key sections: Objective, Constraints, Five Competing Dimensions, STEEPLE, MCDA, Scoring, Decision Chain (Steps 1-9), 216-Configuration Sweep, Result, Sensitivity, Pareto, System Description, Requirements Verification, Plus/Delta, Evidence-Based Adaptation, Energy Model, Testing Methodology, Sim-to-Real, Industry Context, Conclusion

## Notes

- The file uses UTF-8 box-drawing characters (`---`, `===`) in LaTeX comments. These are harmless (comments are not processed) but may cause warnings on some older TeX engines. Modern pdflatex handles them fine.
- The `\sloppy` fix on line 1011 trades slightly looser word spacing for eliminating the overfull. Visually negligible.
- One grammatical issue: line 95, "SSSI). following" should be "SSSI). Following" (lowercase 'f' after period).
