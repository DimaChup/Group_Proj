# Compile Check v4 -- Goldmine Report (main.tex)

**Date**: 2026-04-03
**Compiler**: pdflatex (MiKTeX) + biber 2.21
**Passes**: pdflatex -> biber -> pdflatex -> pdflatex -> pdflatex (5 total)
**Branch**: Working8.Robbin3

---

## Summary

| Metric | Before Fixes | After Fixes |
|--------|-------------|-------------|
| **Pages** | 201 (unstable) | **203** (stable) |
| **Errors** | 4 | **0** |
| **Multiply-defined labels** | 1 | **0** |
| **Undefined references** | 6+ | **0** |
| **Undefined citations** | 62 | **0** |
| **Dest warnings** | 65 | **0** |
| **Float too large** | 1 | 1 (unchanged) |
| **Overfull hbox** | 45-50 | 45 |
| **Underfull hbox** | 152 | 152 |
| **Overfull vbox** | 6 | 6 |

---

## Errors Fixed (4 total)

### 1. pgfkeys Error: Unknown key '/tikz/cross out' (gps_estimation_deep.tex:496)

**Cause**: `\node[cross out, ...]` used without loading the `shapes.misc` TikZ library.

**Fix**: Added `shapes.misc` to the existing `\usetikzlibrary` call:
```latex
% Before:
\usetikzlibrary{shapes.geometric, arrows.meta, positioning, calc, fit}
% After:
\usetikzlibrary{shapes.geometric, shapes.misc, arrows.meta, positioning, calc, fit}
```

### 2-4. "Not allowed in LR mode" x3 (gps_estimation_deep.tex:1373-1375)

**Cause**: TikZ nodes used `\\` for line breaks in text without `align=center` in the style.
```latex
\node[state] (sSearch) at (\colA, 0) {Phase 1\\SEARCH};   % ERROR
```

**Fix**: Added `align=center` to the `state` TikZ style definition:
```latex
state/.style={..., font=\small\bfseries, align=center},
```

### 5. Multiply-defined label `sec:vp:frames`

**Cause**: Same label used in both `gps_estimation_deep.tex:2096` and `vision_performance.tex:144`.

**Fix**: Renamed the duplicate in `gps_estimation_deep.tex` to `sec:gps:strip-visibility`. Updated the one internal cross-reference on line 315 of the same file.

### 6. Undefined reference `sec:req-detail` (decision_flow.tex, design_rationale.tex)

**Cause**: Reference used `sec:req-detail` but the actual label in `requirements_detail.tex` is `app:req-detail`.

**Fix**: `sed -i 's/sec:req-detail/app:req-detail/g'` in both `decision_flow.tex` and `design_rationale.tex`.

### 7. Undefined reference `eq:footprint` (path_tradeoffs.tex:19)

**Cause**: `eq:footprint` is defined in `05_path_planning.tex` which is NOT included in `main.tex`. The reference in `path_tradeoffs.tex` pointed to a non-existent equation.

**Fix**: Changed `\eqref{eq:footprint}` to `\eqref{eq:footprint_w}`, which is the equivalent equation defined in `cv_extended.tex` (included in main.tex).

### 8. 62 undefined citations

**Cause**: biber had not been run. Running `biber main` followed by two pdflatex passes resolved all 62 citation warnings.

---

## Remaining Warnings (not fixed -- content/layout decisions needed)

### Float too large for page (398pt overflow)

**Location**: `sections/evaluation.tex`, around line 60.
**Issue**: A table/figure is approximately 14cm taller than the page can accommodate. The table contains the evaluation matrix with risk items and capability assessments.
**Recommendation**: Split the table across two pages using `longtable`, or reduce font size with `\small`/`\footnotesize`, or split into separate tables.

### Overfull hbox (45 warnings)

Worst offenders (>40pt overflow):
- Line 149 (83pt) -- likely a wide table or code listing
- Lines 14-82 (66pt) -- long unbreakable content
- Line 25 (61pt) -- similar
- Lines 64-65 (60pt)
- Lines 43-44 (54pt)

Most are in table cells or code listings where LaTeX cannot break lines. These cause text to extend into the right margin. Minor layout issues, not critical.

### Underfull hbox (152 warnings)

Mostly from table cells and narrow columns where LaTeX struggles to justify text. Common in multi-column tables with narrow `p{}` columns.

### Overfull vbox (6 warnings)

Pages where content slightly exceeds the available vertical space. Minor.

---

## Page Count Stability

The report oscillated between 195-262 pages during compilation due to cross-reference resolution changing float placement. After 3+ passes it stabilized at **203 pages**. This is normal for documents with many floats and cross-references.

---

## Files Modified

1. `sections/gps_estimation_deep.tex` -- TikZ library, align=center, duplicate label fix
2. `sections/decision_flow.tex` -- sec:req-detail -> app:req-detail
3. `sections/design_rationale.tex` -- sec:req-detail -> app:req-detail
4. `sections/path_tradeoffs.tex` -- eq:footprint -> eq:footprint_w
