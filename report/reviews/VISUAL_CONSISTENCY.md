# Visual Consistency Audit

Audit date: 2026-04-03
Scope: All 53 .tex files in `report/sections/`, plus `main.tex`

---

## 1. Tables

### 1.1 Booktabs vs \hline

The project loads `booktabs` and **51 of 53 files** use `\toprule / \midrule / \bottomrule` correctly.

**One file uses old-style `\hline` exclusively:**

| File | \hline count | Tables affected |
|------|-------------|-----------------|
| `vision_standalone.tex` | **36 occurrences** | All 12 tables in the file |

This file is the only outlier. Every other table across the entire report uses booktabs. The 12 tables in `vision_standalone.tex` (lines 105-827) all use `\begin{tabular}` with `\hline` instead of `\toprule / \midrule / \bottomrule`.

**Recommendation:** Replace all `\hline` in `vision_standalone.tex` with booktabs rules for visual consistency with the rest of the report.

### 1.2 Captions and Labels

All tables have both `\caption{}` and `\label{}`. No exceptions found. Tables in `vision_standalone.tex` follow this convention correctly despite the \hline issue.

### 1.3 Table Environment Consistency

Tables use a mix of:
- `tabular` (most common, ~60 tables)
- `tabularx` (~30 tables, for full-width tables)
- `longtable` (1 instance, `A1_state_table.tex` line 22 -- appropriate for multi-page table)

This mix is appropriate -- `tabularx` for full-width, `tabular` for compact. No issues.

### 1.4 Float Placement Specifiers

Tables use inconsistent float specifiers:
- `[ht]` -- majority of files
- `[H]` -- `02_system_architecture.tex`, `10_testing.tex`, `11_field_results.tex`, `decision_flow.tex`, `design_rationale.tex`, `simulation_validation.tex`, `testing_deep.tex`, `test_scripts_guide.tex`, `optimization_formal.tex`
- `[htbp]` -- `06_state_machine.tex`, `13_safety_risk.tex`, `A2_config_params.tex`, `contingency.tex` (2 of 4 tables), `steeple.tex`, `requirements_verification.tex`, `vision_standalone.tex`
- `[ht!]` -- `evaluation.tex` (1 table)
- `[h]` -- `intro_d6.tex`

This is a minor inconsistency. The mix of `[ht]`, `[H]`, and `[htbp]` is common in practice but `[H]` (from `float` package) forces exact placement and can cause large whitespace gaps. Consider standardising on `[htbp]` or `[ht]` where `[H]` is not strictly needed.

### 1.5 Column Alignments

Column alignments are generally consistent within each table. No alignment issues found. The `\compactTable` command defined in `main.tex` is available but its usage was not audited per-table (it reduces tabcolsep and arraystretch).

---

## 2. Figures

### 2.1 Captions and Labels

All `\begin{figure}` environments have both `\caption{}` and `\label{}`. No exceptions found across all 53 files.

### 2.2 Figure Widths

Figure widths are **inconsistent** across the report:

| Width | Count | Files using it |
|-------|-------|---------------|
| `\linewidth` (1.0) | ~12 | system_description (5), A1_state_table, optimization_master (2), evaluation |
| `0.85\linewidth` | ~15 | Most common -- cv_extended, optimization_master, search_optimization, vision_performance, design_strategy, path_optimization_definitive |
| `0.88\linewidth` | ~6 | optimization_formal, path_optimization_definitive, design_strategy, vision_performance |
| `0.95\linewidth` | ~3 | optimization_master, path_optimization_definitive, system_description |
| `0.85\textwidth` | ~3 | cv_extended (mixed with \linewidth in same file) |
| `0.78\linewidth` | 2 | design_rationale |
| `0.75\textwidth` | 2 | cv_extended, system_description |
| `0.75\linewidth` | 2 | optimization_master |
| `0.9\textwidth` | 1 | system_description |
| `0.8\linewidth` | 1 | system_description |
| `0.65\textwidth` | 1 | cv_extended |
| `0.92\linewidth` | 2 | placeholders (03_hardware, 08_ground_station) |

**Key issues:**
1. **Mixed \linewidth vs \textwidth**: `cv_extended.tex` uses both `0.85\linewidth` and `0.85\textwidth` for different figures. In single-column layout these are identical, but it is inconsistent style.
2. **No dominant standard**: widths range from 0.65 to 1.0. While some variation is natural (wider for multi-panel, narrower for simple plots), the spread is wide.

**Recommendation:** Standardise on `\linewidth` (not `\textwidth`) throughout. Use 0.85\linewidth as the default for single-panel figures, \linewidth for full-width/diagrams.

### 2.3 Subfigures

Subfigures are used in 3 files, all using `subcaption` package correctly:
- `evaluation.tex` -- 2 pairs of subfigures, `0.48\textwidth`
- `optimization_master.tex` -- 2 pairs of subfigures, `0.48\linewidth`
- `system_description.tex` -- 2 pairs of subfigures, `0.48\textwidth`

**Inconsistency:** `evaluation.tex` and `system_description.tex` use `0.48\textwidth` while `optimization_master.tex` uses `0.48\linewidth`. Should standardise on one (both are equivalent in single-column layout but `\linewidth` is the better convention).

### 2.4 Placeholder Figures

Several figures are **text-only placeholders** (using `\fbox{\parbox{...}{...}}`):
- `02_system_architecture.tex` lines 25, 32 (2 figures)
- `03_hardware_platform.tex` line 9
- `04_computer_vision.tex` line 27
- `06_state_machine.tex` line 86
- `08_ground_station.tex` line 37
- `09_simulation.tex` line 77
- `07_target_localisation.tex` line 128 (text placeholder, no fbox)

Additionally, `figure_descriptions.tex` contains 5 large "blackboard diagram" placeholder figures with detailed textual descriptions.

**Total: ~13 placeholder figures** still in the report. These should be replaced with actual images before submission or clearly noted as intentional.

---

## 3. Environments

### 3.1 `infobox` Environment

**Defined in main.tex (line 71-80) but NOT used in any section file.**

The only uses found are in:
- `report/design_decisions.tex` (line 222) -- a file NOT included via `\input` in main.tex
- `report/reviews/VISUALIZATION_RECOMMENDATIONS.md` -- a review document, not compiled

**The `infobox` environment is dead code in the compiled report.**

### 3.2 `abstractbox` Environment

**Defined in main.tex (line 61-69) but NOT used in any section file.**

The only uses found are in:
- `report/design_decisions.tex` (line 121) -- not included in main.tex
- `report/team/main.tex` (line 130) -- separate document

**The `abstractbox` environment is also dead code in the compiled report.**

### 3.3 Equations

**Total numbered equations:** ~105 across all files.

**Equations WITHOUT labels (numbered but unreferenced):** 22 instances

| File | Line | Note |
|------|------|------|
| `09_simulation.tex` | 92 | |
| `11_field_results.tex` | 25 | |
| `calibration_deep.tex` | 28, 85 | |
| `cv_extended.tex` | 147, 181, 196 | 3 unlabelled equations |
| `design_strategy.tex` | 81, 87, 138, 179 | 4 unlabelled equations |
| `field_day_narrative.tex` | 38 | |
| `gps_estimation_deep.tex` | 197 | |
| `optimization_master.tex` | 90 | |
| `path_optimization_definitive.tex` | 264, 368 | |
| `vision_standalone.tex` | 391, 403, 415, 517, 523, 619 | 6 unlabelled equations |

**Recommendation:** If these equations are not cross-referenced, use `equation*` (unnumbered) instead of `equation` to avoid orphan equation numbers. If they are referenced by number in running text, add `\label{}`.

---

## 4. Spacing

### 4.1 \vspace Usage

Found 9 instances of `\vspace` in section files. **All are inside placeholder `\fbox{\parbox{}}` constructs** for figure placeholders (creating visual height for the placeholder box). None are used as paragraph spacing hacks in body text.

**Verdict:** No spacing hacks found. Clean.

### 4.2 \noindent Usage

Found 143 `\noindent` instances across 24 files. The highest concentrations:
- `optimization_formal.tex` -- 21
- `requirements_verification.tex` -- 15
- `requirements_detail.tex` -- 15
- `gps_estimation_deep.tex` -- 14
- `path_optimization_definitive.tex` -- 10
- `optimization_master.tex` -- 9

Since `main.tex` sets `\setlength{\parindent}{0pt}` (line 120), **all `\noindent` commands are redundant** and can be removed. They have no visual effect but add clutter.

### 4.3 Manual Spacing Commands

- `\medskip` -- 1 instance (`design_rationale.tex` line 288). Minor, but could be removed.
- `\bigskip` / `\smallskip` -- none found.
- `\\[Npt]` spacing in equations -- 5 instances, all inside math environments (appropriate).
- `\newpage` -- none found in section files (only in `main.tex`).

**Verdict:** Very clean. Essentially no manual spacing hacks.

### 4.4 Raw \\\\ Newlines Outside Tables/Equations

No instances of bare `\\` used as paragraph breaks in body text. All 903 `\\` occurrences are inside `tabular`, `equation`, `align`, or similar environments where they are appropriate.

**Verdict:** Clean. No abuse of `\\` for paragraph breaks.

---

## 5. Summary of Issues

### CRITICAL (visual inconsistency visible to reader)

| # | Issue | Location | Impact |
|---|-------|----------|--------|
| 1 | **\hline instead of booktabs** | `vision_standalone.tex` (all 12 tables, 36 occurrences) | Visually different table style from rest of report |

### MODERATE (style inconsistency, not immediately visible)

| # | Issue | Location | Impact |
|---|-------|----------|--------|
| 2 | Mixed `\textwidth` vs `\linewidth` in figure widths | `cv_extended.tex`, `evaluation.tex`, `system_description.tex` | Identical output but inconsistent source |
| 3 | 22 numbered equations without `\label` | 10 files (see Section 3.3) | Orphan equation numbers; should use `equation*` |
| 4 | Inconsistent float specifiers (`[H]` vs `[ht]` vs `[htbp]`) | ~15 files | Minor float placement differences |
| 5 | Subfigure width units mixed (`\textwidth` vs `\linewidth`) | `evaluation.tex` vs `optimization_master.tex` | No visual effect, style inconsistency |

### LOW (dead code, cleanup)

| # | Issue | Location | Impact |
|---|-------|----------|--------|
| 6 | `infobox` environment defined but never used | `main.tex` line 71-80 | Dead code in preamble |
| 7 | `abstractbox` environment defined but never used | `main.tex` line 61-69 | Dead code in preamble |
| 8 | 143 redundant `\noindent` commands | 24 files | No visual effect (parindent is already 0pt) |
| 9 | ~13 placeholder figures (fbox/parbox text) | 7 section files + figure_descriptions.tex | Need real images before submission |
| 10 | 1 `\medskip` in body text | `design_rationale.tex` line 288 | Minor manual spacing |

### CLEAN AREAS (no issues found)

- All tables have `\caption` and `\label`
- All figures have `\caption` and `\label`
- No `\\` used as paragraph breaks in body text
- No `\vspace` hacks in body text
- Subcaption package used consistently for all subfigures
- No `\bigskip` / `\smallskip` / `\newpage` in section files
- `\compactTable`, `\figref`, `\tabref`, `\secref` commands defined and available
