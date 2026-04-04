# Cross-Reference Audit (D6 Goldmine Report)

**Date:** 2026-04-04
**Scope:** All `.tex` files compiled via `main.tex` (42 files total)
**Non-compiled files excluded:** `01_introduction.tex`, `02_system_architecture.tex`, `03_hardware_platform.tex`, `04_computer_vision.tex`, `05_path_planning.tex`, `06_state_machine.tex`, `07_target_localisation.tex`, `08_ground_station.tex`, `09_simulation.tex`, `15_conclusion.tex`, `introduction.tex`, `steeple.tex`, `vision_standalone.tex`

---

## Summary

| Check | Result |
|-------|--------|
| Total labels in compiled files | 627 |
| Total unique refs in compiled files | ~290 |
| Broken refs (ref with no matching label) | **1 (FIXED)** |
| Duplicate labels (within compiled files) | **0** |
| `main.log` undefined-reference warnings | **0** |
| `main.log` multiply-defined warnings | **0** |
| Orphaned figure labels (never referenced) | 29 |
| Orphaned table labels (never referenced) | 15 |
| Orphaned section labels (never referenced) | ~170 |
| Orphaned equation labels (never referenced) | ~75 |
| Orphaned appendix labels (never referenced) | 9 |

---

## 1. Broken References (FIXED)

### `\ref{sec:intro}` in `design_rationale.tex` line 6

**Problem:** `sec:intro` is defined in `01_introduction.tex` and `introduction.tex`, neither of which is compiled via `main.tex`. The compiled introduction uses `\label{sec:intro-d6}` (in `intro_d6.tex`).

**Fix applied:** Changed `Section~\ref{sec:intro}` to `Section~\ref{sec:intro-d6}` in `design_rationale.tex` line 6.

---

## 2. Duplicate Labels

No duplicate labels exist within compiled files. There are 21 label names that appear in both compiled and non-compiled files (e.g., `sec:cv` in both `system_description.tex` and the non-compiled `04_computer_vision.tex`), but since the non-compiled files are never loaded, these cause no conflict.

---

## 3. Orphaned Figures (labelled but never `\ref`'d)

These figures exist in the document but are never cross-referenced from body text or other appendices. They are still visible to the reader but lose discoverability.

| Label | Likely location |
|-------|----------------|
| `fig:accuracy-progression` | evaluation or testing |
| `fig:altitude-detection-table` | vision performance |
| `fig:altitude-tradeoff-dual` | path optimisation |
| `fig:benchmark-comparison` | inference architecture |
| `fig:confusion-matrix` | model training |
| `fig:cooperative-loop` | comms architecture |
| `fig:coupling-body` | optimisation |
| `fig:coupling-pair` | optimisation |
| `fig:coverage` | search optimisation |
| `fig:det_vs_speed_ext` | cv extended |
| `fig:detection_heatmap` | cv extended |
| `fig:energy-efficiency-old` | path optimisation |
| `fig:function-chain` | design strategy |
| `fig:gps_accuracy` | GPS estimation |
| `fig:n2-diagram` | optimisation |
| `fig:nfz-margin-altitude-old` | focus/repulsive |
| `fig:objective-conflict` | optimisation |
| `fig:optimal-pattern` | path optimisation |
| `fig:pareto-2d` | optimisation |
| `fig:path-patterns` | path tradeoffs |
| `fig:pi_system` | field results or hw |
| `fig:rotation-comparison-old` | path optimisation |
| `fig:sensitivity-pair` | optimisation |
| `fig:speed-detection-energy-old` | path optimisation |
| `fig:speed-frames` | vision performance |
| `fig:three-level-comparison` | centering analysis |
| `fig:tier-flow` | testing deep |
| `fig:training-curves` | model training |
| `fig:two-step-decision-flow` | decision flow |

**Recommendation:** The most impactful figures to cross-reference from the body are:
- `fig:confusion-matrix` -- reference from the evaluation section's P4 (model performance)
- `fig:training-curves` -- reference from model training discussion
- `fig:pi_system` -- reference from hardware section

---

## 4. Orphaned Tables (labelled but never `\ref`'d)

| Label | Notes |
|-------|-------|
| `tab:ambition-levels` | development methodology |
| `tab:cal-tests` | calibration deep |
| `tab:constraints` | optimisation formal |
| `tab:df-final` | decision flow |
| `tab:df-top3` | decision flow |
| `tab:df-variables` | decision flow |
| `tab:experiment-scripts` | testing deep |
| `tab:hw-tests` | field results |
| `tab:model_variants` | cv extended |
| `tab:rotation-compare-old` | path optimisation |
| `tab:steeple` | design rationale |
| `tab:strategy-compare` | path tradeoffs |
| `tab:stream-protocols` | streaming architecture |
| `tab:test-ladder` | testing deep |
| `tab:vmodel-map` | simulation validation |

**Note:** `tab:steeple` is the STEEPLE table in `design_rationale.tex`. It appears directly under its section heading so a `\ref` is not strictly needed, but adding one from the executive summary or evaluation would strengthen cross-referencing.

---

## 5. Orphaned Appendix Labels

These `app:*` labels exist but are never referenced with `\ref{app:...}`:

| Label | Appendix |
|-------|----------|
| `app:cv:altitude` | CV extended (altitude analysis) |
| `app:cv:backends` | CV extended (backend comparison) |
| `app:cv:pipeline` | CV extended (pipeline detail) |
| `app:cv:runtime` | CV extended (runtime analysis) |
| `app:cv:swapping` | CV extended (model swapping) |
| `app:dev-methodology` | Development methodology |
| `app:eval-detail` | Evaluation detail |
| `app:guide` | Appendix Guide page |
| `app:what-would-change` | Evaluation detail (what would change) |

**Recommendation:** The body evaluation section already references `app:bug-cost`, `app:states`, `app:decision-flow`, `app:req-detail`, `app:cv:benchmarks`, `app:cv:training`, `app:cv:latency`, `app:cv:speed`, `app:cv-extended`, `app:config`, and `app:lessons-learned`. Adding refs to `app:eval-detail` and `app:dev-methodology` from the conclusion/evaluation would connect the remaining appendices.

---

## 6. Forward References

All forward references (body referencing a later appendix) are intentional and correct -- the body sections reference appendices using `Appendix~\ref{app:...}` patterns. This is standard academic practice and works correctly with LaTeX's two-pass compilation.

---

## 7. Non-Compiled Files with Duplicate Labels

These 13 `.tex` files in `sections/` are NOT compiled (not `\input`'d from `main.tex`). They contain labels that duplicate compiled ones but cause no conflict since they are never loaded:

- `01_introduction.tex` -- superseded by `intro_d6.tex`
- `02_system_architecture.tex` -- superseded by `system_description.tex`
- `03_hardware_platform.tex` -- content merged into `system_description.tex`
- `04_computer_vision.tex` -- content merged into `system_description.tex`
- `05_path_planning.tex` -- content merged into `system_description.tex`
- `06_state_machine.tex` -- content merged into `system_description.tex`
- `07_target_localisation.tex` -- content merged into `system_description.tex`
- `08_ground_station.tex` -- content merged into `system_description.tex`
- `09_simulation.tex` -- content merged into `system_description.tex`
- `15_conclusion.tex` -- conclusion merged into body
- `introduction.tex` -- superseded by `intro_d6.tex`
- `steeple.tex` -- superseded by section in `design_rationale.tex`
- `vision_standalone.tex` -- standalone CV report, not part of D6

**Recommendation:** Consider moving these to an `_archive/` or `_old/` subdirectory, or prefixing with `_` to avoid confusion. They are dead code.

---

## 8. Equation Labels (Orphaned)

~75 equation labels are defined but never `\ref`'d. Most are in appendix deep-dive sections where equations are presented inline without needing cross-references. This is acceptable practice -- labels are kept in case future text needs to reference them. No action needed.

---

## Actions Taken

1. **FIXED** `\ref{sec:intro}` -> `\ref{sec:intro-d6}` in `sections/design_rationale.tex` line 6

## Recommended Actions (not taken)

1. Add `\ref{fig:confusion-matrix}` and `\ref{fig:training-curves}` from body text (model training discussion or evaluation P4)
2. Add `\ref{app:eval-detail}` and `\ref{app:dev-methodology}` from evaluation/conclusion
3. Move 13 non-compiled `.tex` files to `sections/_old/` to reduce confusion
4. Consider referencing `tab:steeple` from the executive summary
