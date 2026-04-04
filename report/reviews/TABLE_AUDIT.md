# Table Audit -- D6 Goldmine Report

**Date:** 2026-04-04
**Scope:** All `\begin{table}` environments in `.tex` files included by `report/main.tex`

---

## Summary

| Metric | Count |
|--------|-------|
| Total tables in D6 goldmine (included files) | ~113 |
| Tables with caption | 113/113 (100%) |
| Tables with label | 113/113 (100%) |
| Tables cross-referenced in text (before fixes) | 97/113 (86%) |
| Tables cross-referenced in text (after fixes) | 113/113 (100%) |
| Duplicate/near-duplicate table pairs (cross-file) | 8 pairs |
| Internal duplicate tables (same file) | 3 in gps_estimation_deep.tex |
| File with most tables | gps_estimation_deep.tex (19 tables) |

---

## 1. Caption and Label Compliance

**Result: PASS -- all tables have both caption and label.**

Every `\begin{table}` environment in the included sections contains both a `\caption{...}` and a `\label{tab:...}`. No tables are missing either element.

All captions are descriptive and explain what the table shows, not just a title. Column headers are clear throughout.

---

## 2. Cross-References (FIXED)

**16 tables had labels but were never referenced with `\ref{tab:...}` in the text.** All 16 have been fixed by adding inline references in the surrounding prose.

### Fixed tables:

| Label | File | Fix |
|-------|------|-----|
| `tab:ambition-levels` | development_methodology.tex | Added "Table~\ref" in intro sentence |
| `tab:test-ladder` | development_methodology.tex | Added "Table~\ref" in intro sentence |
| `tab:cal-tests` | test_scripts_guide.tex | Added "(Table~\ref)" in intro sentence |
| `tab:hw-tests` | test_scripts_guide.tex | Added intro sentence with Table~\ref |
| `tab:experiment-scripts` | test_scripts_guide.tex | Added "(Table~\ref)" in intro sentence |
| `tab:constraints` | optimization_formal.tex | Added "(Table~\ref)" in intro sentence |
| `tab:df-variables` | decision_flow.tex | Added "(Table~\ref)" in intro sentence |
| `tab:df-top3` | decision_flow.tex | Added "Table~\ref shows the top three results" |
| `tab:df-final` | decision_flow.tex | Added intro sentence with Table~\ref |
| `tab:model_variants` | cv_extended.tex | Added "(Table~\ref)" in intro sentence |
| `tab:rotation-compare-old` | search_optimization.tex | Added "(Table~\ref)" in intro sentence |
| `tab:strategy-compare` | path_optimization_definitive.tex | Added intro sentence with Table~\ref |
| `tab:stream-protocols` | streaming_architecture.tex | Added "(Table~\ref)" in intro sentence |
| `tab:vmodel-map` | testing_deep.tex | Added "as shown in Table~\ref" |
| `tab:bench-results` | field_day_narrative.tex | Added "(Table~\ref)" in intro sentence |
| `tab:ncnn-bench` | field_day_narrative.tex | Added "(Table~\ref)" in intro sentence |

### Remaining unreferenced (NOT in D6 goldmine -- in vision_standalone.tex, not compiled):
- `tab:dataset-composition`, `tab:ground-coverage`, `tab:hw-specs`, `tab:model-specs`, `tab:model-variants`, `tab:speed-options`

---

## 3. Duplicate Labels (compile warning risk)

Four labels are defined in two different files:

| Label | File 1 | File 2 | Risk |
|-------|--------|--------|------|
| `tab:steeple` | design_rationale.tex | steeple.tex | None -- steeple.tex not included |
| `tab:hw-bom` | system_description.tex | 03_hardware_platform.tex | None -- 03_hardware not included |
| `tab:mavlink-commands` | system_description.tex | 02_system_architecture.tex | None -- 02_system not included |
| `tab:cv_benchmarks` | cv_extended.tex | 04_computer_vision.tex | None -- 04_cv not included |

**No compile-time errors** because only one copy of each label is in the included files. However, if these sections are ever combined, the duplicates will cause LaTeX warnings.

---

## 4. Cross-File Content Duplication (8 pairs flagged)

These table pairs contain substantially the same data in different appendices:

### HIGH overlap (essentially the same table):

| Pair | Table A | Table B | Verdict |
|------|---------|---------|---------|
| 1 | `tab:bug-cost` (evaluation_detail.tex) | `tab:bug-cost-appendix` (testing_deep.tex) | **Same 13 defects**, same columns, slightly reworded. The evaluation_detail version adds TFLite bbox bug and total row; the testing_deep version omits those. |
| 2 | `tab:energy-top5-old` (search_optimization.tex) | `tab:energy-top-bottom` (path_optimization_definitive.tex) | **Same top-5/bottom-5 energy data** with minor value differences in bottom rows. |
| 3 | `tab:pareto-summary-old` (search_optimization.tex) | `tab:pareto-final` (path_optimization_definitive.tex) | **Same Pareto trade-off summary** table, near-identical captions. |
| 4 | `tab:df-top3` (decision_flow.tex) | `tab:opt-top3` (optimization_master.tex) | **Same top-3 configurations** (35m/70deg, 30m/65deg, 40m/75deg), same scores. |

### MODERATE overlap (same topic, different depth/angle):

| Pair | Table A | Table B | Verdict |
|------|---------|---------|---------|
| 5 | `tab:backend_comparison` (inference_architecture.tex) | `tab:pipeline_fps` (pipeline_fps.tex) | Both benchmark Pi inference. Different focus: A = backend comparison, B = raw vs effective throughput. Complementary. |
| 6 | `tab:inference_roadmap` (inference_architecture.tex) | `tab:pipeline_fps` (pipeline_fps.tex) | Both about Pi inference performance. Different focus: A = roadmap/projections, B = measured pipeline throughput. Complementary. |
| 7 | `tab:rotation-compare-old` (search_optimization.tex) | `tab:strategy-compare` (path_optimization_definitive.tex) | Both compare search strategies. Different scope: A = 3 angles only, B = 6 full strategies. Complementary. |
| 8 | `tab:model-variants` (vision_standalone.tex) | `tab:model_variants` (cv_extended.tex) | Same model variant list. vision_standalone not compiled, so no issue. |

### Internal duplication in gps_estimation_deep.tex (19 tables):

Three tables present the **four-phase accuracy progression** with the same CEP values:

| Label | Line | Focus |
|-------|------|-------|
| `tab:accuracy-progression` | L55 | Summary: 4 phases with CEP, N_obs, dominant error |
| `tab:accuracy-journey` | L1015 | Same 4 phases + DJI validation row, "Why it improves" column |
| `tab:state-accuracy` | L1348 | Same 4 phases with more detailed conditions, N_obs ranges |

**Recommendation:** These three could be consolidated into one definitive table, with the others replaced by forward/back references. However, each appears in a different subsection context (strategy roadmap, mission flow summary, detailed progression), so they serve as self-contained reference points for readers who jump to specific sections. Acceptable in a long appendix but worth noting.

---

## 5. Table Density Analysis

Files with the most tables relative to content:

| File | Tables | Assessment |
|------|--------|------------|
| gps_estimation_deep.tex | 19 | **Heavy but justified** -- this is a 2200-line deep-dive appendix covering 7 topics. Each table supports a specific analysis. The 3 internal duplicates (above) are the only concern. |
| cv_extended.tex | 7 | Appropriate for a CV deep-dive appendix. |
| test_scripts_guide.tex | 6 | Appropriate -- each table catalogues a script category. |
| design_rationale.tex | 6 | Appropriate -- STEEPLE + parameter chain + 4 MCDA tables. |
| search_optimization.tex | 5 | Appropriate but note: 3 tables overlap with path_optimization_definitive. |
| decision_flow.tex | 5 | Appropriate -- the narrative references each table inline. |
| contingency.tex | 5 | Appropriate -- MVD, target, tiers, contingency plans, script mapping. |
| vision_performance.tex | 5 | Appropriate -- pixel extent, blur, frames, limits, params. |

No section has excessive tables relative to its text content.

---

## 6. Data Quality Check

All tables contain meaningful, non-padded data. No tables appear to exist solely to fill space. Every table either:
- Presents quantitative measurements (benchmark results, CEP values, energy calculations)
- Compares alternatives (MCDA scoring, strategy comparison, model variants)
- Catalogues test assets (scripts, calibration procedures, defects)
- Summarises design decisions (operating parameters, constraint status)

---

## 7. Recommendations (not actioned)

1. **Consider consolidating** the 3 accuracy-progression tables in gps_estimation_deep.tex into one canonical table, with cross-references from the other locations.
2. **Consider merging** search_optimization.tex and path_optimization_definitive.tex, since 3 of their tables present the same data at the same detail level. Alternatively, keep one as the "executive summary" version and the other as the "full analysis" version, with explicit cross-references noting the relationship.
3. **Add a note** to the duplicate bug-cost tables (evaluation_detail vs testing_deep) explaining that one is the condensed main-body version and the other is the detailed appendix version, or merge them.

---

## Files Modified

- `sections/development_methodology.tex` -- added 2 Table~\ref
- `sections/test_scripts_guide.tex` -- added 3 Table~\ref
- `sections/optimization_formal.tex` -- added 1 Table~\ref
- `sections/decision_flow.tex` -- added 3 Table~\ref
- `sections/cv_extended.tex` -- added 1 Table~\ref
- `sections/search_optimization.tex` -- added 1 Table~\ref
- `sections/path_optimization_definitive.tex` -- added 1 Table~\ref
- `sections/streaming_architecture.tex` -- added 1 Table~\ref
- `sections/testing_deep.tex` -- added 1 Table~\ref
- `sections/field_day_narrative.tex` -- added 2 Table~\ref
