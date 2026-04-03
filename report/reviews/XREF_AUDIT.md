# Cross-Reference Integrity Audit

**Date**: 2026-04-03
**Scope**: All `.tex` files in `report/sections/`, `report/main.tex`, plus `report/design_decisions.tex`
**Bib files**: `report/references.bib`, `report/extra_refs.bib`

---

## Summary Statistics

| Metric | Count |
|--------|-------|
| `\label{}` definitions | 633 |
| Unique `\ref{}` / `\figref{}` / `\tabref{}` / `\secref{}` targets | 221 |
| Total reference uses | 343 |
| Unique `\cite{}` keys used | 96 |
| Bib entries across both `.bib` files | 131 |
| **Undefined references** (ref with no label) | **5** |
| **Orphan labels** (label never referenced) | **416** |
| **Undefined citations** (cite key not in .bib) | **1** |
| **Orphan bib entries** (in .bib but never cited) | **36** |

---

## Undefined References (5) -- MUST FIX

These `\ref{}` / `\figref{}` / `\tabref{}` / `\secref{}` targets have no matching `\label{}` anywhere in the compiled document. They will appear as **??** in the PDF.

| Missing Label | Used In | Line |
|---------------|---------|------|
| `app:field-day` | `sections/design_rationale.tex` | 280 |
| `fig:bottleneck_shift` | `sections/pipeline_fps.tex` | 62 |
| `fig:energy-efficiency` | `sections/optimization_master.tex` | 317 |
| `sec:field-fov` | `sections/field_day_narrative.tex` | 27 |
| `tab:df-speed-envelope` | `sections/decision_flow.tex` | 152 |

### Recommended Fixes

1. **`app:field-day`** -- Either add `\label{app:field-day}` to the field day narrative appendix (`sections/field_day_narrative.tex`, which already has `\label{sec:field-day}` at line 1), or change the reference to `\ref{sec:field-day}`.
2. **`fig:bottleneck_shift`** -- Create the missing figure in `sections/pipeline_fps.tex`, or remove the reference.
3. **`fig:energy-efficiency`** -- A label `fig:energy_efficiency` exists in `sections/search_optimization.tex:63` (underscore, not hyphen). Change the ref to `\ref{fig:energy_efficiency}`.
4. **`sec:field-fov`** -- No matching label exists. The field day narrative has `sec:field-tests`, `sec:field-colour`, etc. Add `\label{sec:field-fov}` to the relevant FOV subsection, or update the ref.
5. **`tab:df-speed-envelope`** -- No matching table label exists in `sections/decision_flow.tex`. Either create the table with that label or remove the reference.

---

## Undefined Citations (1) -- MUST FIX

| Cite Key | Used In | Likely Correct Key |
|----------|---------|-------------------|
| `ultralytics2023yolov8` | `sections/vision_standalone.tex:157` | `jocher2023yolov8` (exists in `extra_refs.bib:78`) |

The bib entry for YOLOv8/Ultralytics is keyed as `jocher2023yolov8` but the citation uses `ultralytics2023yolov8`. Change `\cite{ultralytics2023yolov8}` to `\cite{jocher2023yolov8}`.

---

## Orphan Labels (416) -- LOW PRIORITY

416 out of 633 labels (65.7%) are defined but never referenced from any `\ref{}`, `\figref{}`, `\tabref{}`, or `\secref{}`. This is common in large reports with many appendices -- labels exist for potential cross-referencing but are not yet used.

### Breakdown by Prefix

| Prefix | Orphan Count | Notes |
|--------|-------------|-------|
| `sec:` | 233 | Most are appendix section headers -- normal |
| `eq:` | 93 | Equations labelled for reference but only used locally |
| `fig:` | 44 | Figures that exist but are not cross-referenced from other sections |
| `tab:` | 20 | Tables not cross-referenced |
| `app:` | 10 | Appendix anchors |
| `alg:` | 1 | Algorithm |
| `subsec:` | 3 | Subsections |
| Other | 12 | Design decisions (in `design_decisions.tex`, NOT included from `main.tex`) |

### Notable Orphans Worth Reviewing

These labels are in the main body sections (not appendices) and might benefit from cross-references:

- `fig:pi_system` (system_description.tex) -- Pi hardware photo, could be referenced from design rationale
- `fig:estimation` / `fig:estimator_comparison` / `fig:gps_accuracy` / `fig:gps_convergence` (system_description.tex) -- GPS estimation figures
- `fig:coverage` (vision_performance.tex) -- coverage analysis figure
- `fig:confusion-matrix` / `fig:training-curves` (12_model_training.tex) -- model training results

### Dead Labels (in files NOT included from main.tex)

`design_decisions.tex` is in the report root but is NOT `\input`'d from `main.tex`. Its 12 labels are completely dead:

- `sec:dd01` through `sec:dd10`
- `tab:dd01-options`, `tab:dd07-steps`, `tab:dd10-modes`, `tab:summary`

Similarly, these section files exist in `sections/` but are NOT included from `main.tex`:
- `00_abstract.tex`, `01_introduction.tex`, `02_system_architecture.tex`, `03_hardware_platform.tex`
- `04_computer_vision.tex`, `05_path_planning.tex`, `06_state_machine.tex`, `07_target_localisation.tex`
- `08_ground_station.tex`, `09_simulation.tex`, `15_conclusion.tex`, `introduction.tex`
- `steeple.tex`, `vision_standalone.tex`

Labels in these files are dormant -- they compile only if someone adds `\input{}` for them.

---

## Orphan Bib Entries (36) -- INFORMATIONAL

These entries exist in `references.bib` or `extra_refs.bib` but are never cited. This is not a problem (unused references are simply not printed), but cleaning them up would reduce bib file size.

<details>
<summary>Full list of 36 orphan bib keys</summary>

- `agrawal2020hotl_uav`
- `albanese2022low_power_uav`
- `araujo2023tvv_ras`
- `cabreira2019cpp_survey`
- `chang2023gps_denied_review`
- `coombes2017boustrophedon`
- `coombes2018polygon_decomposition`
- `david2021tflite`
- `du2023multi_uav_astar`
- `fevgas2022cpp_energy`
- `gps_accuracy`
- `gugan2023path_planning`
- `hayat2020multi_objective_sar`
- `hitl`
- `jacob2018quantization`
- `jocher2023yolov8`
- `khan2022uav_disaster`
- `kim2022geofencing`
- `koopman2018av_validation`
- `lin2022gps_denied_vision`
- `mavlink`
- `mishra2020drone_sar`
- `missionplanner`
- `mjpeg`
- `numpy`
- `redmon2016yolo`
- `scaramuzza2011visual`
- `seraj2023hitl_drl_uav`
- `shakhatreh2019uav_civil`
- `sora`
- `terven2023yolo_review`
- `tobin2017domain`
- `toma2022edge_ml_uav`
- `visdrone2021`
- `wang2023uav_yolov8`
- `zhao2024yolov8n_uav`

</details>

**Note**: `jocher2023yolov8` appears orphan because it is not directly cited -- but it SHOULD be cited (see undefined citation `ultralytics2023yolov8` above). Once that cite key is fixed, this entry will no longer be orphan.

---

## Recommendations

### Priority 1 -- Fix before final submission
1. Fix the **1 undefined citation**: change `\cite{ultralytics2023yolov8}` to `\cite{jocher2023yolov8}` in `vision_standalone.tex:157`
2. Fix the **5 undefined references** (all show as **??** in PDF):
   - `fig:energy-efficiency` is likely a typo for `fig:energy_efficiency` (hyphen vs underscore)
   - `app:field-day` likely should be `sec:field-day`
   - `fig:bottleneck_shift`, `sec:field-fov`, `tab:df-speed-envelope` need labels created or refs removed

### Priority 2 -- Cleanup
3. Consider adding cross-references to key orphan figures/tables in the main body to improve document navigation
4. Remove or archive `design_decisions.tex` from the report root (its content appears to have been superseded by `sections/design_rationale.tex`)

### Priority 3 -- Optional
5. Clean up 36 unused bib entries to keep bibliography files lean
6. Review whether any of the 14 non-included section files (`00_abstract.tex`, `01_introduction.tex`, etc.) should be removed or archived -- they appear to be earlier drafts superseded by the current structure
