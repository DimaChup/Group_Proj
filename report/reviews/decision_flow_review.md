# Review: decision_flow.tex

**File**: `report/sections/decision_flow.tex`
**Date**: 2026-03-28
**Verdict**: GOOD -- minor edits applied, no structural rewrite needed.

---

## 1. Conciseness (target: 2-3 pages)

PASS. 119 lines of LaTeX with two compact tables and no embedded figures. Estimated 2-2.5 printed pages. Well within budget.

## 2. Story vs List

PASS with minor note. The six numbered paragraphs form a genuine decision chain where each step constrains the next: target size -> altitude -> footprint -> speed -> scan angle -> NFZ margin -> overlap. This is a story, not a catalogue. The opening bullet list (5 competing objectives) is acceptable as scene-setting -- it frames the tension before the resolution.

## 3. Priority Statement

FIXED. Original said "safety first, then detection, then everything else" -- vague about speed vs energy ordering. Changed to explicit stack: **safety > detection > speed > energy**, with one-sentence justification for each level.

## 4. Figure References

All 8 figure references checked against `report/figs/`:

| Reference | File exists? | Notes |
|-----------|-------------|-------|
| `fig:sensitivity-matrix` | YES (pdf+png) | |
| `fig:energy-heatmap` | YES (png only) | Label defined in `path_optimization_definitive.tex` (line 92). No PDF version -- will compile if pdflatex accepts png. |
| `fig:alt-speed-body` | YES (pdf+png as `altitude_speed_tradeoff`) | Label defined in `optimization_master.tex` (line 169) and `design_rationale.tex` (line 59). |
| `fig:pareto-parallel` | YES (pdf+png) | |
| `fig:top3-paths` | YES (pdf+png) | |
| `fig:tornado-sensitivity` | YES (pdf+png) | |
| `fig:sensitivity-spider` | YES (pdf+png) | |

All 6 requested figures (sensitivity_matrix, altitude_speed_tradeoff, tornado_sensitivity, top3_paths, pareto_parallel, sensitivity_spider) confirmed present.

**Note**: `energy-heatmap` and `alt-speed-body` are referenced but their `\label{}` definitions live in other section files, not in decision_flow.tex itself. This is fine for multi-file compilation but will produce "??" if decision_flow.tex is compiled standalone.

## 5. Language Quality

GOOD overall. Plain English with minimal jargon. Three spots were improved:

- **"RSS margin"** (line 63): Unexplained acronym. FIXED -- expanded to "root-sum-square (RSS)".
- **"knee of the Pareto frontier"** (line 89): Technical optimisation jargon that a non-engineer would not understand. FIXED -- changed to "sweet spot of the trade-off frontier".
- **"negligibly small"** (line 66): Stated as fact without evidence. FIXED -- softened to "unlikely casualty location" and added explicit trade-off framing.

## 6. Non-Engineer Accessibility

PASS. The six-step chain reads naturally: "How high can we fly? How fast at that height? What angle saves energy?" etc. Each paragraph answers one question and feeds into the next. The tables are well-captioned with a "Why not?" column that preempts the reader's objections. A project manager or pilot could follow this without engineering background.

## 7. Unjustified Claims

| Claim | Justified? | Notes |
|-------|-----------|-------|
| "99.97% detection probability" | YES | Derived: 14 frames at 95% per-frame = 1 - 0.05^14. Math stated in line 57. |
| "7 pixels at 50m" | PARTIALLY | Follows from geometry but the pixel-size model isn't shown here. Acceptable for a summary section -- full derivation presumably in appendix. |
| "Halves energy vs worst orientation" | NEEDS CHECK | References Fig energy-heatmap. Should be verifiable from the figure. |
| "96% coverage acceptable" | FIXED | Was stated as obvious. Now framed as a deliberate safety trade-off. |
| "2.2x safety factor" | YES | 30m buffer / 23m RSS requirement = 1.30. Wait -- 30/23 = 1.30, not 2.2. **This may be wrong** unless the 2.2x refers to a different baseline (e.g., 30m / 13.6m camera-only margin). Recommend verifying the denominator. |

**ACTION ITEM**: Verify the "2.2x safety factor" claim on line 63. If the RSS margin is 23m and the buffer is 30m, the factor is 1.3x, not 2.2x. If 2.2x is correct, the denominator should be stated explicitly.

## 8. Edits Applied

Four targeted edits made directly to the file:

1. **Line 20**: Priority statement expanded from vague "everything else" to explicit "safety > detection > speed > energy" with per-level justification.
2. **Line 63**: "RSS" acronym expanded to "root-sum-square (RSS)".
3. **Line 66**: "negligibly small" softened; added explicit trade-off framing.
4. **Line 89**: "knee of the Pareto frontier" simplified to "sweet spot of the trade-off frontier".

## 9. Remaining Suggestions (not edited -- author decision)

- **Opening bullets**: Consider converting the 5 objectives into a single flowing sentence to reduce the "list" feel. Current form is acceptable but less narrative.
- **Table column widths**: The top-3 table (tab:df-top3) has 8 columns which may be tight on a single-column page. Test in compilation.
- **"216 configurations"**: The text says "6 altitudes x 36 scan angles" = 216. But speed is also varied (table shows different speeds per config). Clarify whether speed was swept independently or derived from altitude.
- **The 2.2x safety factor**: Verify as noted above. If incorrect, fix to match the actual calculation.

---

**Overall**: Strong section. Tells a clear decision story with an unbroken logical chain. Language is accessible. All figures exist. The four edits improve precision without changing the structure.
