# Brutal Compile Check

**Date:** 2026-03-27
**Source:** `main.log` from latest LaTeX build
**Total LaTeX warnings:** 38

---

## Summary

| Category | Count | Severity |
|----------|-------|----------|
| Undefined references | 15 (10 unique labels) | HIGH -- prints **??** in PDF |
| Multiply-defined labels | 16 (13 unique labels) | MEDIUM -- wrong cross-ref target |
| `\textdegree` in math mode | 4 (2 locations) | LOW -- renders but looks wrong |
| Float too large for page | 1 | LOW -- cosmetic overflow |
| Overfull/underfull boxes | 165 | LOW -- cosmetic |
| Hard errors (`!`) | 0 | NONE |
| Missing figures | 0 | NONE |
| Undefined citations | 0 | NONE |

**Bottom line:** Zero hard errors, zero missing citations. The PDF compiles and all bibliography entries resolve. But 10 cross-references print literal **??** in the output, and 13 labels point to the wrong target because they are defined twice.

---

## 1. UNDEFINED REFERENCES (prints ?? in PDF)

Root cause: sections `05_path_planning.tex`, `06_state_machine.tex`, and `07_target_localisation.tex` define labels that other included files reference, but these three files are **not** `\input` in `main.tex`. The labels exist only in orphaned files.

| # | Broken `\ref{...}` | Page | Referenced FROM (included file) | Label defined IN (orphaned file) | Fix |
|---|---------------------|------|---------------------------------|----------------------------------|-----|
| 1 | `subsec:operator` | 38 | `13_safety_risk.tex` | `06_state_machine.tex:146` | Change to `\ref{sec:operator-loop}` (defined in `13_safety_risk.tex:46`, already included) |
| 2 | `sec:cv:benchmarks` | 48 | `inference_architecture.tex` | `04_computer_vision.tex:86` | Replace with prose ("the performance benchmarks in Appendix H2") or add `\label{sec:cv:benchmarks}` to `cv_extended.tex` near its benchmark subsection |
| 3 | `sec:focus-area` | 72, 91, 99, 105 | `contingency.tex`, `focus_and_repulsive.tex`, `path_optimization_definitive.tex`, `path_tradeoffs.tex` | `05_path_planning.tex:125` | Add `\label{sec:focus-area}` to `focus_and_repulsive.tex` at its PLB Focus Area subsection (line 7), since that appendix IS included |
| 4 | `tab:flight-params` | 82, 89 | `mission_flow.tex`, `path_tradeoffs.tex` | `05_path_planning.tex:164` | Move the flight-params table into `system_description.tex` or `design_rationale.tex` (main body), or add the table to an included appendix and label it `tab:flight-params` |
| 5 | `subsec:states` | 84 | `centering_analysis.tex` | `06_state_machine.tex:40` | Replace with `\ref{sec:state-machine}` or whichever label exists in `system_description.tex` for the state machine subsection |
| 6 | `sec:algorithm` | 89, 91, 99 | `path_tradeoffs.tex`, `focus_and_repulsive.tex` | `05_path_planning.tex:32` | Add `\label{sec:algorithm}` to `system_description.tex` where the rotated-mask algorithm is described, OR to `path_tradeoffs.tex` itself if it re-explains the algorithm |
| 7 | `sec:scan-angle` | 89 | `path_tradeoffs.tex` | `05_path_planning.tex:85` | Add `\label{sec:scan-angle}` to `optimization_master.tex` where the 216-config sweep is described |
| 8 | `sec:bezier` | 90 | `path_tradeoffs.tex` | `05_path_planning.tex:114` | Add `\label{sec:bezier}` to `path_tradeoffs.tex` itself if Bezier smoothing is discussed there, or to `system_description.tex` |
| 9 | `sec:accuracy` | 122 | `vision_performance.tex` | `07_target_localisation.tex:104` | Add `\label{sec:accuracy}` to `gps_estimation_deep.tex` where GPS accuracy is analysed, or replace with `\ref{sec:gps-estimation}` if that label exists |
| 10 | `sec:geofencing` | (multiple) | `06_state_machine.tex` (orphaned), `focus_and_repulsive.tex`, `mission_flow.tex`, `steeple.tex` | `13_safety_risk.tex:5` | **This one is OK** -- `13_safety_risk.tex` IS included. But `06_state_machine.tex` also references it and is orphaned, so only the refs from included files work. No fix needed. |

### Fastest fix strategy

Add a small label-only shim file that defines the missing labels and `\input` it early in `main.tex`:

```latex
% labels_shim.tex -- redirect orphaned labels to included content
\phantomsection\label{sec:focus-area}    % -> focus_and_repulsive.tex
\phantomsection\label{sec:algorithm}     % -> system_description path planning
\phantomsection\label{sec:scan-angle}    % -> optimization_master 216-sweep
\phantomsection\label{sec:bezier}        % -> path_tradeoffs Bezier section
\phantomsection\label{sec:cv:benchmarks} % -> cv_extended benchmarks
\phantomsection\label{sec:accuracy}      % -> gps_estimation_deep accuracy
```

But this is a hack. The proper fix is to add `\label{...}` at the correct location in each included file (see table above).

---

## 2. MULTIPLY-DEFINED LABELS (wrong cross-ref target)

When a label is defined twice, LaTeX uses the **last** definition. Any `\ref` will silently point to the wrong location.

| # | Label | Defined in file 1 | Defined in file 2 | Fix |
|---|-------|--------------------|--------------------|-----|
| 1 | `sec:experiment-scripts` | `testing_deep.tex:114` | `test_scripts_guide.tex:110` | Rename one to `sec:experiment-scripts-guide` |
| 2 | `eq:footprint` | `system_description.tex:131` | `calibration_deep.tex:9`, `vision_performance.tex:39` (3 total!) | Keep in `system_description.tex` (main body), rename appendix copies to `eq:footprint-cal` and `eq:footprint-vp` |
| 3 | `sec:plb-redirect` | `path_tradeoffs.tex:82` | `focus_and_repulsive.tex:7` | Rename one to `sec:plb-redirect-detail` |
| 4 | `fig:top3-paths` | `path_optimization_definitive.tex:201` | `optimization_master.tex:129` | Rename one to `fig:top3-paths-master` |
| 5 | `fig:alt-speed-body` | `design_rationale.tex:59` | `optimization_master.tex:169` | Rename one to `fig:alt-speed-appendix` |
| 6 | `fig:energy-heatmap` | `path_optimization_definitive.tex:92` | `optimization_master.tex:178` | Rename one to `fig:energy-heatmap-master` |
| 7 | `sec:opt-summary` | `search_optimization.tex:228` | `optimization_master.tex:293` | Rename one to `sec:opt-summary-master` |
| 8 | `fig:pareto-2d` | `path_optimization_definitive.tex:344` | `optimization_master.tex:277` | Rename one to `fig:pareto-2d-master` |
| 9 | `eq:target-px` | `optimization_formal.tex:76` | `design_strategy.tex:17` | Rename one to `eq:target-px-formal` |
| 10 | `eq:coverage` | `optimization_formal.tex:66` | `vision_performance.tex:196` | Rename one to `eq:coverage-vp` |
| 11 | `fig:n2-diagram` | `optimization_formal.tex:193` | `optimization_master.tex:230` | Rename one to `fig:n2-diagram-master` |
| 12 | `fig:sensitivity-matrix` | `design_strategy.tex:245` | `optimization_master.tex:259` | Rename one |
| 13 | `fig:sensitivity-spider` | `design_strategy.tex:252` | `optimization_master.tex:263` | Rename one |
| 14 | `fig:coupling-matrix` | `design_strategy.tex:259` | `optimization_master.tex:234` | Rename one |
| 15 | `fig:tornado-sensitivity` | `design_strategy.tex:280` | `optimization_master.tex:204` | Rename one |

### Pattern

Most duplicates come from **optimization content being spread across 4 appendices** (`optimization_master.tex`, `optimization_formal.tex`, `path_optimization_definitive.tex`, `design_strategy.tex`) that share figures and equations. These appendices were likely written independently and then all included.

**Recommended fix:** Pick one canonical appendix for each figure/equation. In the others, remove the duplicate and use `\ref{...}` to point to the canonical one. Or rename the duplicates with a suffix.

---

## 3. `\textdegree` IN MATH MODE (4 warnings, 2 locations)

| File | Line | Problematic code | Fix |
|------|------|-------------------|-----|
| `path_tradeoffs.tex` | 15 | `$\cos(45°)$` | `$\cos(45\degree)$` (uses `gensymb` already loaded) |
| `path_tradeoffs.tex` | 71 | `$\tan(5°)$` | `$\tan(5\degree)$` (uses `gensymb` already loaded) |
| `optimization_master.tex` | 91 | `\text{\textdegree}` inside equation | `{^\circ}` or `\degree` |

---

## 4. FLOAT TOO LARGE FOR PAGE (1 warning)

| File | Line | Issue | Fix |
|------|------|-------|-----|
| `evaluation.tex` | 58 | Plus/delta table (D1-D9) overflows page by 173pt (~6cm) | Add `\small` or `\footnotesize` inside the table, or split into two tables (Plus items / Delta items), or use `\begin{table}[p]` to put it on its own page |

---

## 5. OVERFULL/UNDERFULL BOXES (165 total)

Not individually listed. These are cosmetic line-breaking issues. The worst are typically in tables with long text in narrow columns. Run `grep "Overfull.*hbox.*badness 10000" main.log | wc -l` to find the worst offenders if you want to polish.

---

## Priority Action List

1. **Fix 10 undefined references** -- these print visible **??** in the PDF. Examiner will notice.
2. **Rename 13 duplicate labels** -- these cause silent wrong cross-references. Examiner may follow a ref and land on the wrong page.
3. **Fix 2 degree symbols in math mode** -- trivial one-line fixes.
4. **Shrink the evaluation table** -- one `\small` command.
5. Overfull boxes -- cosmetic, lowest priority.
