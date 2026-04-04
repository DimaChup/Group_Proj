# Figure Audit -- D6 Goldmine Report

**Date:** 2026-04-04
**Scope:** All `.tex` files in `report/sections/` that are `\input` in `report/main.tex`

---

## Summary

| Metric | Count |
|--------|-------|
| Total `\begin{figure}` environments | 93 |
| Figures with real images (`\includegraphics`) | ~75 |
| Figures with TikZ diagrams | ~12 |
| Figures with ASCII/verbatim diagrams | 1 |
| **Placeholder figures (fbox, no real image)** | **1 remaining** |
| Figures without `\caption` | 0 |
| Figures without `\label{fig:...}` | 0 |
| Broken `\ref{fig:...}` (ref without matching label) | 0 |
| Orphan labels (defined but never referenced) | 0 |
| All referenced image files exist in `figs/` | Yes (53/53) |

---

## Fixes Applied (this audit)

### Placeholders replaced with real images (4 fixed)

1. **`02_system_architecture.tex:23`** -- "System Architecture Block Diagram" placeholder replaced with `architecture.pdf` (generated diagram exists in figs/)
2. **`02_system_architecture.tex:30`** -- "Module Dependency Graph" placeholder replaced with `system_architecture.pdf`
3. **`04_computer_vision.tex:24`** -- "CV pipeline placeholder" replaced with `cv_pipeline.pdf` (path was `figures/cv_pipeline.pdf`, corrected to `cv_pipeline`)
4. **`06_state_machine.tex:83`** -- "State machine diagram placeholder" replaced with `state_machine.pdf` (path was `figures/state_machine_diagram.pdf`, corrected to `state_machine`)

### Remaining placeholders (2, no matching image files)

5. **`03_hardware_platform.tex:6`** -- Hardware block diagram. **Fixed:** replaced with `pi_system.pdf` which shows the complete hardware/software block diagram with all subsystem connections.
6. **`08_ground_station.tex:34`** -- Dashboard screenshot. **Still a placeholder.** No screenshot image exists in `figs/`. Needs a real browser screenshot of the ground station UI (pi_flight.py at port 8090). This is the only remaining placeholder in the compiled report.

---

## Caption Quality Assessment

All 93 figures have captions. Quality is generally **good to excellent**:

- Most captions are 1-3 sentences explaining what the figure shows and why it matters
- Best examples: `gps_estimation_deep.tex` figures have detailed captions with quantitative context (e.g., "CEP50 vs. GPS averaging time... the 1/sqrt(T) convergence means...")
- `optimization_master.tex` captions include specific numbers and design rationale
- `system_description.tex` captions connect figures to the narrative

**No weak captions found.** All captions exceed the "System diagram" level -- they describe content, context, and significance.

---

## Cross-Reference Integrity

- **104 unique `\ref{fig:...}` references** across all tex files
- **104 unique `\label{fig:...}` definitions** across all tex files
- **Zero broken references** -- every `\ref{fig:X}` has a matching `\label{fig:X}`
- **Zero orphan labels** -- every defined label is referenced somewhere

This is excellent. No "Figure ??" will appear in the compiled PDF.

---

## Image File Verification

All 53 unique image names referenced by active `\includegraphics` commands have matching files in `report/figs/`. Most exist as both `.pdf` and `.png`. No missing files.

Notable: 37 Python generator scripts (`gen_*.py`) in `figs/` can regenerate the figures if needed.

---

## Sections Without Figures (included in compiled report, >60 lines)

These text-heavy sections have no visual content. Sections most likely to benefit from a figure are marked with priority.

| Section | Lines | Would benefit from figure? |
|---------|-------|---------------------------|
| `development_methodology.tex` | 390 | **HIGH** -- V-model or Agile workflow diagram, testing pyramid |
| `streaming_architecture.tex` | 256 | **HIGH** -- data flow diagram showing MJPEG pipeline |
| `calibration_deep.tex` | 237 | **MEDIUM** -- calibration setup photo, distortion before/after |
| `test_scripts_guide.tex` | 232 | LOW -- reference table, not narrative |
| `decision_flow.tex` | 216 | **HIGH** -- has `decision_flow.pdf` in figs/ but no figure environment! |
| `centering_analysis.tex` | 175 | **MEDIUM** -- centering convergence plot |
| `simulation_validation.tex` | 158 | **MEDIUM** -- SITL vs real comparison |
| `contingency.tex` | 152 | LOW -- contingency table format is fine |
| `mission_flow.tex` | 147 | **HIGH** -- mission timeline or flowchart |
| `requirements_detail.tex` | 145 | LOW -- tabular format works |
| `field_day_narrative.tex` | 131 | **HIGH** -- field day photos would add authenticity |
| `focus_and_repulsive.tex` | 130 | **MEDIUM** -- NFZ repulsive force diagram |
| `13_safety_risk.tex` | 114 | **MEDIUM** -- risk matrix or safety architecture diagram |
| `11_field_results.tex` | 107 | **HIGH** -- bench test photos, detection screenshots |
| `path_tradeoffs.tex` | 83 | LOW -- covered by other optimization sections |
| `intro_d6.tex` | 79 | LOW -- introduction, text is appropriate |
| `model_comparison.tex` | 79 | **MEDIUM** -- model comparison bar chart |
| `evaluation_detail.tex` | 79 | LOW -- supplements main evaluation |

### Critical finding: `decision_flow.tex` -- FIXED

`decision_flow.pdf` existed in `figs/` but the section did not include it. **Fixed:** added `\includegraphics{decision_flow}` with caption and label, referenced in the intro paragraph.

### Top 5 sections that need figures most urgently:

1. ~~**`decision_flow.tex`** (216 lines)~~ -- **FIXED** (decision_flow.pdf added)
2. **`field_day_narrative.tex`** (131 lines) + **`11_field_results.tex`** (107 lines) -- real photos from field day would significantly boost the Communication mark
3. **`development_methodology.tex`** (390 lines) -- a development process diagram (V-model, testing pyramid) would break up dense text
4. **`streaming_architecture.tex`** (256 lines) -- a data flow diagram for the MJPEG pipeline
5. **`mission_flow.tex`** (147 lines) -- `mission_timeline.pdf` exists in figs/ and could be referenced here

---

## `figure_descriptions.tex` Status

This file contains 5 detailed text-description placeholders for figures that need real photos/screenshots:
1. Ground station dashboard screenshot
2. Hardware assembly photo
3. Detection overlay example
4. Lawnmower pattern on satellite image
5. Bench test setup photo

**This file is commented out** in `main.tex` (line 383: `% \input{sections/figure_descriptions}`). These descriptions are well-written and could serve as extended captions if real images are added, but they are not currently compiled into the PDF.

---

## Figure Distribution by Section

| Section file | Fig count | Type |
|-------------|-----------|------|
| `gps_estimation_deep.tex` | 15 | 10 TikZ + 3 includegraphics + 2 pgfplots |
| `optimization_master.tex` | 12 | All includegraphics |
| `system_description.tex` | 9 | All includegraphics |
| `design_strategy.tex` | 7 | All includegraphics |
| `path_optimization_definitive.tex` | 7 | All includegraphics |
| `cv_extended.tex` | 6 | All includegraphics |
| `vision_performance.tex` | 5 | All includegraphics |
| `search_optimization.tex` | 4 | All includegraphics (section commented out) |
| `evaluation.tex` | 2 | Subfigures with includegraphics |
| `design_rationale.tex` | 2 | includegraphics |
| `optimization_formal.tex` | 2 | includegraphics |
| `12_model_training.tex` | 2 | includegraphics |
| `02_system_architecture.tex` | 2 | includegraphics (fixed from placeholder) |
| Remaining 14 sections | 1 each | Mixed |

The appendix sections (gps_estimation_deep, optimization_master, design_strategy) are heavily illustrated. The main body sections (system_description, evaluation, design_rationale) are adequately illustrated. The gap is in the operational/narrative appendices.

---

## Recommendations

1. **Add `decision_flow.pdf` to `decision_flow.tex`** -- the image is already generated
2. **Capture a real screenshot** of the ground station dashboard to replace the placeholder in `08_ground_station.tex`
3. **Add field day photos** to `field_day_narrative.tex` and `11_field_results.tex` -- these are the biggest Communication score boosters
4. **Consider adding `mission_timeline.pdf`** reference to `mission_flow.tex`
5. **Add a development process diagram** to `development_methodology.tex`
6. The `figure_descriptions.tex` text descriptions are excellent -- if real photos are added, use these descriptions as extended captions
