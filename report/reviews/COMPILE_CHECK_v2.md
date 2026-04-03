# D6 Report Compilation Check (v2)

**Date**: 2026-04-03
**Compiler**: pdflatex (MiKTeX, Windows)
**Command**: `pdflatex -interaction=nonstopmode main.tex`
**Result**: **PASS** -- PDF generated successfully

---

## Summary

| Metric                  | Count | Status |
|-------------------------|-------|--------|
| LaTeX errors (`!`)      | 0     | PASS   |
| Overfull hbox warnings  | 31    | WARN   |
| Underfull hbox/vbox     | 137   | WARN   |
| Undefined references    | 10    | FAIL   |
| Multiply defined labels | 15    | WARN   |
| Missing files           | 0     | PASS   |
| Float too large         | 1     | WARN   |
| Total pages             | 153   | INFO   |

---

## Page Structure

### Front Matter (pages 1-5)
- Page 1-2: Title page / TOC
- Page 3: Executive Summary
- Pages 4-5: Introduction

### Body Sections (pages 6-34) -- 29 pages

| Section | Title | Start Page | End Page | Pages |
|---------|-------|------------|----------|-------|
| 1       | Design Rationale | 6 | 12 | 7 |
| 2       | Decision Flow: How We Chose Our Search Parameters | 13 | 16 | 4 |
| 3       | System Description | 17 | 24 | 8 |
| 4       | Requirements Verification | 25 | 28 | 4 |
| 5       | Evaluation | 29 | 34 | 6 |

**Body total: ~29 pages (sections 1-5, pages 6-34)**

### Appendices (pages 35-153) -- 119 pages

| Appendix | Title | Start Page |
|----------|-------|------------|
| A | State Transition Table | 35 |
| B | Configuration Parameters | 37 |
| C | Model Training and Dataset | 38 |
| D | Safety and Risk Management | 42 |
| E | Testing Methodology | 44 |
| F | Field Testing and Results | 48 |
| G | Future Work | 50 |
| H | Computer Vision: Extended Analysis | 55 |
| I | Video Streaming and Ground Station Architecture | 62 |
| J | GPS Target Estimation: A Deep Dive | 65 |
| K | Progressive Testing Methodology | 69 |
| L | Field Day: Adaptation Under Uncertainty | 73 |
| M | Contingency Planning and Deliverable Tiers | 76 |
| N | Test Script Reference | 78 |
| O | Sensor Calibration | 83 |
| P | Mission Flow | 87 |
| Q | MAVLink Communication Architecture | 91 |
| R | Model Comparison and Future Vision Improvements | 97 |
| S | Focus Area Redirect and Repulsive Field | 104 |
| T | Search Path Optimisation | 106 |
| U | Search Parameter Optimisation | 112 |
| V | Multi-Objective Search Optimisation | 116 |
| W | Design Strategy: Parameter Derivation Chain | 124 |
| X | Vision Performance Analysis | 127 |

---

## 15-Page Body Limit Assessment

**FAIL** -- The 5 numbered body sections span pages 6-34 = **29 pages**.

This is **nearly double** the 15-page limit. If the requirement is that the 4 numbered
body sections (excluding executive summary and introduction) must fit in 15 pages,
the report exceeds this by ~14 pages.

**Breakdown of the excess:**
- Section 1 (Design Rationale): 7 pages -- could move STEEPLE, MCDA tables to appendix
- Section 2 (Decision Flow): 4 pages -- borderline, mostly derivation
- Section 3 (System Description): 8 pages -- largest section, could trim subsections
- Section 4 (Requirements Verification): 4 pages -- mostly tables
- Section 5 (Evaluation): 6 pages

**Recommendations to reach 15 pages:**
1. Move STEEPLE analysis (Sec 1.1) to appendix (-1 page)
2. Move detailed MCDA tables and trade studies to appendix (-2 pages)
3. Condense parameter derivation chain (Sec 1.3) -- full version already in Appendix W (-1 page)
4. Move Decision Flow (Sec 2) entirely to appendix or merge into Sec 1 (-3 pages)
5. Condense System Description subsections -- move code listings, detailed state tables to appendix (-3 pages)
6. Compress Requirements Verification tables (-1 page)
7. Tighten Evaluation prose (-1 page)

---

## Undefined References (10 unique)

These labels are referenced but never defined anywhere:

| Reference | Referenced on Page | Likely Fix |
|-----------|--------------------|------------|
| `app:field-day` | 13 | Add `\label{app:field-day}` to Appendix L (Field Day) |
| `subsec:operator` | 43 | Add label to operator interface subsection |
| `sec:cv:benchmarks` | 53 | Add label to CV benchmarks subsection |
| `sec:focus-area` | 77, 96, 104, 109 | Add label to focus area section (likely in Appendix S) |
| `tab:flight-params` | 87, 94 | Add label to flight parameters table |
| `subsec:states` | 89 | Add label to states subsection |
| `sec:algorithm` | 94, 96, 104 | Add label to algorithm section |
| `sec:bezier` | 95 | Add label to Bezier curve section |
| `sec:scan-angle` | 94 | Add label to scan angle section |
| `sec:accuracy` | 129 | Add label to accuracy section |

---

## Multiply Defined Labels (15)

These labels are defined in multiple places (likely duplicated between body and appendix):

- `eq:coverage`, `eq:footprint`, `eq:target-px` -- equations duplicated
- `fig:alt-speed-body`, `fig:coupling-matrix`, `fig:energy-heatmap`, `fig:pareto-2d` -- figures duplicated
- `fig:n2-diagram`, `fig:sensitivity-matrix`, `fig:sensitivity-spider`, `fig:tornado-sensitivity` -- figures duplicated
- `sec:experiment-scripts`, `sec:opt-summary`, `sec:plb-redirect` -- sections duplicated

**Fix**: Rename duplicates with unique suffixes (e.g., `fig:pareto-2d-body` vs `fig:pareto-2d-app`).

---

## Other Warnings

- **31 overfull hboxes**: Most are minor (2-15pt). Common in tables and URLs.
- **137 underfull hbox/vbox**: Cosmetic, usually from page breaks and paragraph spacing.
- **1 float too large for page** (172pt overflow): A figure or table exceeds page height.
- **3 pdfTeX dest warnings**: Referenced table captions (18, 41) that don't exist -- likely from multiply-defined labels.
- **hyperref token warnings**: Math symbols in section titles (use `\texorpdfstring`).
- **`\textdegree` invalid in math mode**: Use `{}^\circ` instead.

---

## Overall Assessment

| Check | Result |
|-------|--------|
| Compiles without errors | PASS |
| No missing files | PASS |
| Body within 15 pages | **FAIL (29 pages, ~2x over)** |
| All references resolved | **FAIL (10 undefined)** |
| No duplicate labels | **FAIL (15 duplicates)** |
| Acceptable warnings | WARN (31 overfull, manageable) |

**Priority fixes:**
1. **Critical**: Reduce body to 15 pages by moving content to appendices
2. **High**: Fix 10 undefined references (readers see `??` in PDF)
3. **Medium**: Rename 15 duplicate labels (causes wrong cross-references)
4. **Low**: Fix overfull hboxes, math-mode warnings
