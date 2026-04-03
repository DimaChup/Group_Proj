# Appendix Reorganisation Review

**Date**: 2026-04-03
**Scope**: 33 appendix includes in `main.tex` lines 209-307 (labelled A through AB, with errors)

---

## 1. Current Appendix Order (as listed in main.tex)

| # | Comment Label | File | Topic | `\section` or `\subsection`? |
|---|--------------|------|-------|------------------------------|
| 1 | Appendix A | A1_state_table.tex | State transition table | `\section` |
| 2 | Appendix B | A2_config_params.tex | Configuration parameters | `\section` |
| 3 | Appendix C | 12_model_training.tex | Model training & dataset | `\section` |
| 4 | Appendix D | 13_safety_risk.tex | Safety & risk management | `\section` |
| 5 | Appendix E | 10_testing.tex | Testing methodology | `\section` |
| 6 | Appendix F | 11_field_results.tex | Field testing results | `\section` |
| 7 | Appendix G | 14_future_work.tex | Future work | `\section` |
| 8 | Appendix H | inference_architecture.tex | Edge inference architecture | `\subsection` (!) |
| 9 | Appendix H2 | cv_extended.tex | CV extended analysis | `\section` |
| 10 | Appendix I | streaming_architecture.tex | Streaming & ground station | `\section` |
| 11 | Appendix J | gps_estimation_deep.tex | GPS estimation deep dive | `\section` |
| 12 | Appendix K | testing_deep.tex | Progressive testing deep dive | `\section` |
| 13 | Appendix L | field_day_narrative.tex | Field day narrative | `\section` |
| 14 | Appendix M | contingency.tex | Contingency planning | `\section` |
| 15 | Appendix N | test_scripts_guide.tex | Test scripts reference | `\section` |
| 16 | Appendix O | calibration_deep.tex | Sensor calibration deep dive | `\section` |
| 17 | Appendix P | simulation_validation.tex | Simulation validation | `\subsection` (!) |
| 18 | Appendix Q | mission_flow.tex | Mission flow narrative | `\section` |
| 19 | Appendix R | centering_analysis.tex | Centering vs offset landing | `\subsection` (!) |
| 20 | Appendix S | comms_architecture.tex | MAVLink communication | `\section` |
| 21 | Appendix T | pipeline_fps.tex | Pipeline FPS vs raw inference | `\subsection` (!) |
| 22 | Appendix U | path_tradeoffs.tex | Path planning tradeoffs | `\subsection` (!) |
| 23 | Appendix V | payload_release.tex | Payload release mechanism | `\subsection` (!) |
| 24 | Appendix W | model_comparison.tex | Model comparison & future CV | `\section` |
| 25 | Appendix X | search_optimization.tex | Multi-objective search opt. | `\subsection` (!) |
| 26 | Appendix Y | focus_and_repulsive.tex | Focus area + repulsive field | `\section` |
| 27 | Appendix Z | path_optimization_definitive.tex | Definitive path optimisation | `\section` |
| 28 | Appendix AA | optimization_master.tex | Master optimisation (physics sim, Pareto) | `\section` |
| 29 | Appendix AB | optimization_formal.tex | Formal multi-objective optimisation | `\section` |
| 30 | **Appendix AB** (DUPLICATE!) | design_strategy.tex | Design strategy param derivation | `\section` |
| 31 | **Appendix AB** (DUPLICATE!) | vision_performance.tex | Vision performance analysis | `\section` |
| 32 | **Appendix AA** (DUPLICATE!) | alternatives.tex | Alternative paragraph options | `\section*` (unnumbered) |
| 33 | **Appendix R** (DUPLICATE!) | figure_descriptions.tex | Figure description placeholders | No section at all |

---

## 2. Critical Issues Found

### 2.1 Duplicate Appendix Labels (BROKEN)
The following comments in main.tex assign the SAME letter to multiple appendices:

- **"Appendix AB"** is used THREE times (lines 293, 296, 299) for: optimization_formal, design_strategy, vision_performance
- **"Appendix AA"** is used twice (lines 290, 302) for: optimization_master, alternatives
- **"Appendix R"** is used twice (lines 263, 305) for: centering_analysis, figure_descriptions

Note: The comment labels are cosmetic only -- LaTeX auto-assigns letters based on `\section{}` commands. But the comments are misleading and will cause confusion when cross-referencing. The actual compiled letter depends on how many `\section{}` commands precede each file. Files using `\subsection{}` will NOT get their own letter -- they become subsections of the previous `\section`, which changes the counting.

### 2.2 Subsection-Level Appendices (No Letter Assignment)
Seven files use `\subsection{}` instead of `\section{}`. In appendix mode, only `\section{}` gets a letter (A, B, C...). These subsections will be nested under the preceding `\section` appendix, which means:

| File | Uses | Will appear under |
|------|------|-------------------|
| inference_architecture.tex | `\subsection` | Appendix G (Future Work) -- WRONG |
| simulation_validation.tex | `\subsection` | Appendix O (Calibration) -- WRONG |
| centering_analysis.tex | `\subsection` | Appendix Q (Mission Flow) -- WRONG |
| pipeline_fps.tex | `\subsection` | Appendix S (Comms Architecture) -- WRONG |
| path_tradeoffs.tex | `\subsection` | Appendix T (Pipeline FPS... which is itself a subsection!) |
| payload_release.tex | `\subsection` | Under whatever section precedes it |
| search_optimization.tex | `\subsection` | Appendix W (Model Comparison) -- WRONG |

**These are all logically independent topics that should be their own appendix letters.** They need to be promoted to `\section{}`.

### 2.3 Non-Appendix Content Included as Appendices
- **alternatives.tex**: Uses `\section*{}` (unnumbered). Contains draft paragraph alternatives -- this is working material, NOT a real appendix. Should be removed from the compiled report.
- **figure_descriptions.tex**: Contains `\fbox{\parbox{}}` placeholder figures. If real figures have replaced these, this file should be removed. If placeholders remain, they should be integrated into the relevant appendix rather than dumped at the end.

### 2.4 Content That Should Probably Be in the Body, Not Appendices
- **optimization_master.tex**: Comment says "COUNTED in 15-page limit" -- if it is counted in the body page limit, it should be in the body section of main.tex, not the appendix section.
- **optimization_formal.tex**: Comment also says "COUNTED in 15-page limit" -- same issue.

---

## 3. Overlap and Duplication Analysis

### 3.1 Optimisation Cluster (5 appendices with heavy overlap)
These five files all cover search path optimisation with significant content duplication:

| File | Focus | Overlap with |
|------|-------|-------------|
| path_tradeoffs.tex | Diagonal vs aligned, lane width, speed, overlap | search_optimization, path_optimization_definitive |
| search_optimization.tex | Multi-objective opt: energy, rotation, NFZ, coverage | path_optimization_definitive, optimization_master |
| path_optimization_definitive.tex | "Supersedes search_optimization" (says so in comments!) | search_optimization (explicitly) |
| optimization_master.tex | Physics sim, 216 configs, top 3, Pareto, sensitivity | path_optimization_definitive (same 216 configs) |
| optimization_formal.tex | Formal problem statement, decision vector, constraints | optimization_master (same problem, more formal) |

**Key finding**: `path_optimization_definitive.tex` explicitly says it "supersedes search_optimization.tex" in its comment header. Both are included. The optimization_master and optimization_formal files also restate the same 5-objective problem.

**Recommendation**: Consolidate into at most 2 appendices:
1. One "Path Optimisation" appendix covering tradeoffs + the definitive 216-config analysis
2. One "Formal Optimisation" appendix for the mathematical formulation + Pareto analysis

### 3.2 Testing Cluster (3 appendices with overlap)
| File | Focus | Overlap with |
|------|-------|-------------|
| 10_testing.tex | V-model, five-tier framework | testing_deep (same five tiers, more detail) |
| testing_deep.tex | Progressive testing methodology | 10_testing (extends it) |
| test_scripts_guide.tex | 71 test scripts reference | 10_testing (scripts listed there too) |

**Recommendation**: Merge 10_testing + testing_deep into one appendix. Keep test_scripts_guide separate as a reference.

### 3.3 CV/Inference Cluster (5 appendices with overlap)
| File | Focus | Overlap with |
|------|-------|-------------|
| 12_model_training.tex | Training data, domain randomisation | model_comparison (model generations table) |
| inference_architecture.tex | NCNN vs TFLite, backend selection | cv_extended (dual backend architecture), pipeline_fps |
| cv_extended.tex | Pipeline timing, benchmarks, altitude, backends | inference_architecture, pipeline_fps, model_comparison |
| pipeline_fps.tex | Raw vs effective FPS | cv_extended (pipeline timing subsection) |
| model_comparison.tex | Model generations, COCO fallback, tiling | 12_model_training, cv_extended |

**Recommendation**: Consolidate into 2-3 appendices:
1. "Model Training & Dataset" (keep 12_model_training as-is)
2. "CV Architecture & Performance" (merge inference_architecture + cv_extended + pipeline_fps)
3. "Model Comparison" (keep model_comparison, remove overlap with training)

### 3.4 Field/Operations Cluster (minor overlap)
| File | Focus |
|------|-------|
| 11_field_results.tex | Bench testing, FOV calibration, benchmarks |
| field_day_narrative.tex | Narrative of the field day |
| mission_flow.tex | End-to-end mission sequence |

These are distinct enough to keep separate, but should be grouped together.

---

## 4. Cross-Reference Audit

### 4.1 Body sections referencing appendices correctly
- `system_description.tex` references `\ref{app:config}` (Appendix B) and `\ref{app:states}` (Appendix A) -- CORRECT
- `evaluation.tex` references `\ref{sec:five-tier}` (in testing appendix) -- CORRECT
- `design_rationale.tex` references `\ref{sec:path-opt}` (path_optimization_definitive) -- CORRECT

### 4.2 Potential broken references
- `design_rationale.tex` references `\ref{sec:path-opt}` which is in path_optimization_definitive.tex. If this file is merged or removed, the reference breaks.
- inference_architecture.tex, pipeline_fps.tex, centering_analysis.tex, simulation_validation.tex, path_tradeoffs.tex, payload_release.tex, and search_optimization.tex all use `\subsection` -- their labels will resolve but the rendered section numbers may be confusing (e.g., "G.1" for inference architecture under Future Work).

### 4.3 Missing `app:` prefix convention
Only 3 files use the `app:` label prefix (A1_state_table, A2_config_params, cv_extended). All others use `sec:` prefix, making it impossible to distinguish body sections from appendix sections by label alone.

---

## 5. Recommended Reorganisation

### Guiding Principles
1. Group by theme (CV, GPS, Testing, Safety, Operations, Optimisation, Reference)
2. Each appendix gets its own `\section{}` (own letter)
3. Eliminate duplicated content (keep the better/more complete version)
4. Remove working materials (alternatives.tex, figure_descriptions.tex if obsolete)
5. Move "counted in body" sections back to the body

### Proposed Order (23 appendices, down from 33)

```
% ══════════════════════════════════════════════════════════════
% GROUP 1: SYSTEM REFERENCE (A-B)
% ══════════════════════════════════════════════════════════════

% Appendix A: State transition table
\input{sections/A1_state_table}

% Appendix B: Configuration parameters
\input{sections/A2_config_params}

% ══════════════════════════════════════════════════════════════
% GROUP 2: COMPUTER VISION (C-F)
% ══════════════════════════════════════════════════════════════

% Appendix C: Model training and dataset
\input{sections/12_model_training}

% Appendix D: CV extended analysis (merge pipeline_fps + inference_architecture INTO this)
\input{sections/cv_extended}

% Appendix E: Model comparison and future CV
\input{sections/model_comparison}

% Appendix F: Vision performance analysis (altitude, blur, coverage envelope)
\input{sections/vision_performance}

% ══════════════════════════════════════════════════════════════
% GROUP 3: GPS & LOCALISATION (G-H)
% ══════════════════════════════════════════════════════════════

% Appendix G: GPS estimation deep dive
\input{sections/gps_estimation_deep}

% Appendix H: Sensor calibration (FOV, lens, colour)
\input{sections/calibration_deep}

% ══════════════════════════════════════════════════════════════
% GROUP 4: PATH PLANNING & OPTIMISATION (I-L)
% ══════════════════════════════════════════════════════════════

% Appendix I: Path planning tradeoffs (promote to \section)
\input{sections/path_tradeoffs}

% Appendix J: Definitive path optimisation (216-config sweep) -- KEEP, REMOVE search_optimization
\input{sections/path_optimization_definitive}

% Appendix K: Formal multi-objective optimisation (decision vector, Pareto)
\input{sections/optimization_formal}

% Appendix L: Focus area redirect + repulsive field
\input{sections/focus_and_repulsive}

% ══════════════════════════════════════════════════════════════
% GROUP 5: TESTING & FIELD RESULTS (M-Q)
% ══════════════════════════════════════════════════════════════

% Appendix M: Testing methodology (merge testing_deep INTO 10_testing, or vice versa)
\input{sections/10_testing}

% Appendix N: Test scripts reference
\input{sections/test_scripts_guide}

% Appendix O: Field testing results and calibration data
\input{sections/11_field_results}

% Appendix P: Field day narrative
\input{sections/field_day_narrative}

% Appendix Q: Simulation validation (promote to \section)
\input{sections/simulation_validation}

% ══════════════════════════════════════════════════════════════
% GROUP 6: SAFETY & OPERATIONS (R-V)
% ══════════════════════════════════════════════════════════════

% Appendix R: Safety and risk management
\input{sections/13_safety_risk}

% Appendix S: Contingency planning
\input{sections/contingency}

% Appendix T: Mission flow (real flight narrative)
\input{sections/mission_flow}

% Appendix U: Communication architecture (MAVLink)
\input{sections/comms_architecture}

% Appendix V: Streaming architecture (ground station)
\input{sections/streaming_architecture}

% ══════════════════════════════════════════════════════════════
% GROUP 7: DESIGN & MISC (W-X)
% ══════════════════════════════════════════════════════════════

% Appendix W: Design strategy (parameter derivation chain)
\input{sections/design_strategy}

% Appendix X: Future work
\input{sections/14_future_work}
```

### Files REMOVED from appendices:
| File | Reason |
|------|--------|
| inference_architecture.tex | Merge into cv_extended.tex (it is a subsection of the same topic) |
| pipeline_fps.tex | Merge into cv_extended.tex (it is a subsection of the same topic) |
| search_optimization.tex | Superseded by path_optimization_definitive.tex (says so in its own header) |
| optimization_master.tex | Move to body (comment says "COUNTED in 15-page limit") or merge into optimization_formal |
| testing_deep.tex | Merge into 10_testing.tex (extends the same five-tier framework) |
| centering_analysis.tex | Merge into mission_flow.tex as a subsection (directly related) |
| payload_release.tex | Merge into mission_flow.tex as a subsection (directly related) |
| alternatives.tex | Remove entirely -- working draft material, not a real appendix |
| figure_descriptions.tex | Remove if all placeholders replaced; otherwise integrate into relevant appendices |

### Files needing `\subsection` -> `\section` promotion:
- path_tradeoffs.tex
- simulation_validation.tex
- search_optimization.tex (if kept)
- Any others remaining as `\subsection` after merges

---

## 6. Additional Recommendations

### 6.1 Add an Appendix Index Page
As suggested in D6_GOLDMINE_WORKFLOW.md, add a one-page appendix guide at the start of the appendices section:
```latex
\section*{Appendix Guide}
\begin{description}
  \item[Appendices A--B] System reference tables (states, configuration)
  \item[Appendices C--F] Computer vision: training, architecture, performance
  \item[Appendices G--H] GPS estimation and sensor calibration
  ...
\end{description}
```

### 6.2 Consistent Label Prefix
Adopt `app:` prefix for all appendix labels to distinguish from body `sec:` labels. Currently only 3 of 33 files use `app:`.

### 6.3 One-Line Summary at Top of Each Appendix
Each appendix `\section{}` should be followed by a 1-2 sentence italicised summary explaining why the appendix exists and what the reader will find. Example:
```latex
\section{GPS Target Estimation: A Deep Dive}\label{app:gps-deep}
\textit{This appendix derives the full mathematical model for converting pixel
detections to GPS coordinates, quantifies six error sources, and reports
empirical accuracy from flight-video replay.}
```

### 6.4 Body Cross-Reference Pass
After reorganisation, search the body for all `\ref{sec:...}` that point to appendix labels and verify they still resolve. Key ones to check:
- `\ref{sec:path-opt}` in design_rationale.tex
- `\ref{sec:five-tier}` in evaluation.tex
- `\ref{app:config}` and `\ref{app:states}` in system_description.tex

---

## 7. Summary of Issues

| Category | Count | Severity |
|----------|-------|----------|
| Duplicate appendix labels in comments | 3 pairs (6 entries) | HIGH -- misleading |
| `\subsection` files that should be `\section` | 7 files | HIGH -- wrong letter assignment |
| Duplicated/superseded content | 5+ files | MEDIUM -- bloat, reader confusion |
| Working material in appendices | 2 files | LOW -- unprofessional if noticed |
| Body sections in appendix zone | 2 files | MEDIUM -- page count error |
| Missing appendix index | 1 | LOW -- navigation aid |

**Net effect of reorganisation**: 33 includes reduced to 23 appendices (A through W), with clearer grouping, no duplicates, and correct letter assignment.
