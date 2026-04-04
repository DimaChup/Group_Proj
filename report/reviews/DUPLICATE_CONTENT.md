# Duplicate Content Audit — D6 Goldmine Report

Scanned all 58 `.tex` files in `report/sections/`. This document identifies content
overlaps, classifies each as intentional (different perspective/depth) or accidental
(near-verbatim), and recommends consolidation or cross-referencing.

---

## Cluster 1: GPS Estimation / Target Localisation

### Files involved
| File | Role | Section label | ~Lines |
|------|------|---------------|--------|
| `07_target_localisation.tex` | **Main body** — concise pixel-to-GPS math + IVW fusion | `sec:localisation` | ~120 |
| `gps_estimation_deep.tex` | **Appendix K** — full 7-part deep dive (pipeline, math, error, tilt, strategies, flow, validation) | `sec:gps-deep` | ~1600+ |
| `localization_approaches.tex` | **Appendix** — survey of 10 geolocation approaches | `sec:loc-approaches` | ~400 |
| `estimation_evaluation.tex` | **Appendix** — ground-truth evaluation, bullseye plots, clustering thresholds, CEP stats | `sec:estimation-eval` | ~300 |

### What overlaps

1. **Pixel-to-GPS math (GSD, heading rotation, WGS 84 projection):**
   - `07_target_localisation.tex` Eqs 1-4: GSD, body offset, NE rotation, GPS offset
   - `gps_estimation_deep.tex` Part II (sec:gps-math): identical derivation with more detail
   - `localization_approaches.tex` Approach 1 (sec:approach-direct): restates GSD and WGS 84 equations
   - **Verdict: ACCIDENTAL overlap.** The same GSD equation appears three times with slightly different notation. The main body version is the necessary self-contained summary; the deep appendix expands it; but `localization_approaches.tex` duplicates the math unnecessarily since it could simply reference `sec:gps-math`.

2. **IVW weighting formula (altitude + centrality):**
   - `07_target_localisation.tex` sec:fusion: defines w_alt, w_cen, weighted mean
   - `gps_estimation_deep.tex` Part VII: same formulas with additional context
   - `estimation_evaluation.tex` sec:centrality-weighting: describes the weighting heatmap figure
   - **Verdict: Mostly intentional.** Main body gives the formula; deep appendix derives it; evaluation appendix validates it. But the formula itself is written out in full three times.

3. **CEP50 = 2.3m from DJI replay:**
   - Stated in `07_target_localisation.tex`, `gps_estimation_deep.tex`, `estimation_evaluation.tex`, `localization_approaches.tex`, `10_testing.tex`, and `evaluation.tex`
   - **Verdict: Intentional cross-reference.** This is a key result cited wherever relevant. Not a problem.

4. **Error budget table (6 error sources):**
   - `estimation_evaluation.tex` Table `tab:error-budget-relative`: full 6-row error budget
   - `gps_estimation_deep.tex` Part III: same error sources described narratively
   - **Verdict: Intentional.** The table is the definitive presentation; the narrative expands each row.

### Recommendations

| Action | File | Detail |
|--------|------|--------|
| **Cross-reference, don't restate** | `localization_approaches.tex` Approach 1 | Replace the GSD/WGS84 equation block with: "The mathematical basis is derived in Section~\ref{sec:gps-math}; the key equation is Eq.~\ref{eq:gsd}." Saves ~15 lines. |
| **Keep as-is** | `07_target_localisation.tex` | This is the main body; must be self-contained. It correctly provides the essential formulas. |
| **Keep as-is** | `gps_estimation_deep.tex` | This is the deep appendix; the full derivation belongs here. Primary source for GPS math. |
| **Keep as-is** | `estimation_evaluation.tex` | Distinct purpose (validation/evaluation, not derivation). References gps_estimation_deep correctly. |

**Primary file:** `gps_estimation_deep.tex` (full derivation)
**Main body summary:** `07_target_localisation.tex` (self-contained extract)
**Should cross-ref instead of repeating:** `localization_approaches.tex` Approach 1

---

## Cluster 2: Testing Methodology

### Files involved
| File | Role | Section label | ~Lines |
|------|------|---------------|--------|
| `10_testing.tex` | **Appendix** — V-model, five tiers, unit test results, stress testing, DJI analysis, confidence buildup | `sec:testing` | ~284 |
| `testing_deep.tex` | **Appendix L** — deep dive on progressive methodology, tier detail, experiment scripts, defect table, V-model mapping, cost-risk | `sec:testing-deep` | ~228 |
| `test_scripts_guide.tex` | **Appendix** — per-script reference, flight progression table, hardware tests, calibration, experiments, diagnostics, gaps | `sec:test-scripts` | ~235 |

### What overlaps

1. **Five-tier framework description:**
   - `10_testing.tex` sec:five-tier: Table `tab:five-tier` (5 rows: environment, what it verifies, risk level) + 5 paragraphs (Tier 1-5)
   - `testing_deep.tex` sec:tiers-detail: Figure `fig:tier-flow` + 5 detailed subsubsections (Tier 1-5) with "Defects caught" paragraphs
   - **Verdict: ACCIDENTAL near-duplicate.** Both describe the same 5 tiers at similar depth. `10_testing.tex` Tier descriptions are 1-2 paragraphs each; `testing_deep.tex` Tier descriptions are 1-2 paragraphs each with slightly more detail (defect lists). The reader encounters the same information twice.

2. **Test script organisation (8 categories, 74 scripts):**
   - `10_testing.tex` sec:test-org: bullet list of 8 directories with script counts
   - `testing_deep.tex` sec:test-org-detail: Table `tab:test-categories` mapping directories to tiers
   - `test_scripts_guide.tex` sec:script-categories: Description list of 8 directories (most detailed)
   - **Verdict: ACCIDENTAL triple-presentation.** The same "74 scripts in 8 categories" is stated three times at increasing detail. The first two could reference the third.

3. **Flight test progression (0a through 4):**
   - `10_testing.tex` does NOT have a flight progression table (refers to sec:five-tier)
   - `testing_deep.tex` sec:test-org-detail: mentions numbered scripts briefly
   - `test_scripts_guide.tex` sec:flight-progression: Table `tab:flight-scripts` (7 rows, full detail)
   - **Verdict: Properly split.** Only `test_scripts_guide.tex` has the detailed flight progression.

4. **Experiment scripts (6 CSV-output scripts):**
   - `10_testing.tex`: does not list them individually
   - `testing_deep.tex` sec:experiment-scripts: numbered list of 6 scripts with descriptions
   - `test_scripts_guide.tex` sec:experiment-scripts-app: Table `tab:experiment-scripts` (6 rows)
   - **Verdict: ACCIDENTAL duplicate.** Both `testing_deep.tex` and `test_scripts_guide.tex` describe the same 6 experiment scripts at similar detail. One should reference the other.

5. **Defect discovery table:**
   - `10_testing.tex` Table `tab:stress-results`: 20 stress test scenarios
   - `10_testing.tex` Table `tab:param-tuning`: 6 parameters corrected through testing
   - `testing_deep.tex` Table `tab:bug-cost-appendix`: 12 defects with tier, fix time, cost estimate
   - **Verdict: Intentional.** Different perspectives: `10_testing.tex` focuses on stress scenarios and parameter corrections; `testing_deep.tex` focuses on per-defect cost analysis. Minimal textual overlap.

6. **Unit test results (150 tests, 98.7% pass):**
   - `10_testing.tex` sec:unit-test-results: Table `tab:unit-results` (6 modules)
   - `testing_deep.tex`: references the unit tests but does not replicate the table
   - **Verdict: Clean.** No duplicate.

### Recommendations

| Action | File | Detail |
|--------|------|--------|
| **Consolidate tier descriptions** | `10_testing.tex` + `testing_deep.tex` | `10_testing.tex` should have the concise tier table + brief paragraphs (current). `testing_deep.tex` should open with "This appendix expands the tier descriptions from Section~\ref{sec:five-tier}" and provide ONLY the additional detail (defects caught, specific scripts). Remove the tier-summary paragraphs from `testing_deep.tex` that merely restate what `10_testing.tex` says. Saves ~40 lines. |
| **Single source for script organisation** | `test_scripts_guide.tex` | Make `test_scripts_guide.tex` the definitive script reference. In `10_testing.tex` sec:test-org, replace the 8-item bullet list with a 2-sentence summary + "see Section~\ref{sec:test-scripts} for the complete reference." In `testing_deep.tex` sec:test-org-detail, replace Table `tab:test-categories` with a cross-reference. Saves ~30 lines across two files. |
| **Single source for experiment scripts** | `test_scripts_guide.tex` | Remove the 6-script enumerated list from `testing_deep.tex` sec:experiment-scripts. Replace with: "The six experiment scripts are detailed in Section~\ref{sec:experiment-scripts-app}." Saves ~25 lines. |
| **Keep as-is** | Defect tables | Different analytical perspectives; no text duplication. |

**Primary file for tier methodology:** `10_testing.tex` (appendix-level overview)
**Primary file for tier detail + cost analysis:** `testing_deep.tex` (deep dive)
**Primary file for per-script reference:** `test_scripts_guide.tex` (exhaustive catalogue)

---

## Cluster 3: Safety and Contingency

### Files involved
| File | Role | Section label | ~Lines |
|------|------|---------------|--------|
| `13_safety_risk.tex` | **Appendix** — risk matrix, risk register, geofence, failure modes, operator-in-loop, emergency procedures, preflight, lessons, regulatory | `sec:safety` | ~219 |
| `contingency.tex` | **Appendix** — deliverable tiers (MVD/target/stretch), tier evolution, contingency plans for 11 scenarios, hardware/software/environmental contingencies, graceful degradation, test-script mapping | `sec:contingency` | ~237 |

### What overlaps

1. **Failure mode / contingency response tables:**
   - `13_safety_risk.tex` Table `tab:failure-modes`: 11 failure modes with detection, response, verification status
   - `contingency.tex` Table `tab:contingency`: 11 failure scenarios with detection criteria and response
   - **Verdict: ACCIDENTAL near-duplicate.** Both tables list essentially the same failure scenarios (camera failure, GPS degradation, MAVLink loss, RC loss, battery, Pi crash, operator timeout, NFZ incursion, flight area breach, landing stall, mode fighting) with overlapping response descriptions. `contingency.tex` adds a few scenarios not in `13_safety_risk.tex` (no GPS lock, CV fails, detection altitude too low, wind, model wrong format, geofence misconfigured) but the core ~8 scenarios appear in both.

2. **Geofence description:**
   - `13_safety_risk.tex` sec:geofencing: 5-layer geofence with numbered list, Figure `fig:geofence_layers`
   - `contingency.tex` sec:sw-contingencies "RC override guard" paragraph: restates the whitelist `(4, 6, 9)` and guard logic
   - **Verdict: Mostly intentional** (safety section is the primary geofence description; contingency mentions it briefly in context). But the RC override guard paragraph in `contingency.tex` is nearly verbatim from `13_safety_risk.tex`.

3. **Emergency procedures (RC kill, keyboard abort, M key):**
   - `13_safety_risk.tex` sec:emergency: 3 numbered abort mechanisms
   - `contingency.tex` sec:hw-contingencies: restates Cube failure and Pi failure responses in similar language
   - **Verdict: Partial duplicate.** The emergency procedures in `13_safety_risk.tex` are the definitive description. `contingency.tex` restates some of the same material (especially firmware failsafes: FS_GCS_ENABLE, FS_THR_ENABLE, FS_BATT_ENABLE) nearly verbatim.

4. **Preflight checklist:**
   - `13_safety_risk.tex` sec:procedures Table `tab:preflight`: 10-row preflight checklist
   - `contingency.tex` sec:test-mapping Table `tab:test-scripts`: 7-row contingency-to-test-script mapping
   - **Verdict: Clean.** Different content (checklist items vs test scripts).

5. **Graceful degradation:**
   - `contingency.tex` Table `tab:degradation`: 8-row component-loss table
   - `13_safety_risk.tex`: no equivalent table
   - **Verdict: Clean.** Unique to `contingency.tex`.

### Recommendations

| Action | File | Detail |
|--------|------|--------|
| **Merge failure mode tables** | `13_safety_risk.tex` is primary | The `tab:failure-modes` table in `13_safety_risk.tex` should be the SINGLE failure mode reference. In `contingency.tex`, replace `tab:contingency` with a cross-reference: "Table~\ref{tab:failure-modes} in Section~\ref{sec:failure-modes} lists the automated responses to hardware and software failures. This section focuses on the *flight-day contingency plans*---what the team does when a failure occurs." Then keep only the ~4 scenarios unique to contingency (no GPS lock at startup, CV fails in field, detection altitude too low, model wrong format). Saves ~30 lines and removes the duplicated rows. |
| **Remove duplicate RC override text** | `contingency.tex` | The RC override guard paragraph (sec:sw-contingencies) duplicates sec:emergency in `13_safety_risk.tex`. Replace with: "The RC override guard (Section~\ref{sec:emergency}) suppresses all MAVLink commands when the pilot switches away from GUIDED/LAND/RTL." One sentence instead of a paragraph. |
| **Remove duplicate firmware failsafe text** | `contingency.tex` | The FS_GCS_ENABLE / FS_THR_ENABLE / FS_BATT_ENABLE paragraph at end of sec:hw-contingencies restates identical info from `13_safety_risk.tex` sec:emergency. Replace with a cross-reference. |
| **Keep as-is** | Graceful degradation table, deliverable tiers, tier evolution | These are unique to `contingency.tex` and provide genuine new content. |

**Primary file for safety/risk:** `13_safety_risk.tex`
**Primary file for flight-day contingency plans + deliverable tiers:** `contingency.tex`

---

## Cluster 4: Search Optimisation / Path Planning

### Files involved
| File | Role | Section label | ~Lines |
|------|------|---------------|--------|
| `05_path_planning.tex` | **Appendix** — rotated-mask algorithm, coverage path planning, search area definition | `sec:planning` | ~200 |
| `design_rationale.tex` | **Main body (counted)** — STEEPLE + search parameter trade-offs (summary) | `sec:rationale` | ~150 |
| `design_strategy.tex` | **Appendix** — simulation-first philosophy, strategy alternatives, parameter derivation chain | `sec:design-strategy` | ~200 |
| `search_optimization.tex` | **COMMENTED OUT** (superseded) — original 216-config sweep + energy model | `sec:search-opt` | ~60 lines visible, file explicitly marked "SUPERSEDED by path_optimization_definitive.tex" |
| `path_optimization_definitive.tex` | **Appendix** — definitive path optimisation: MOO problem, energy model, 216 sweep, strategy comparison, NFZ interaction, detection integration, selected config | `sec:path-opt` | ~384 |
| `optimization_master.tex` | **Appendix AB** — physics sim, Pareto analysis, sensitivity, coupling, composite scoring | `sec:optimisation` | ~376 |
| `optimization_formal.tex` | **Appendix AC** — formal mathematical MOO problem statement | `sec:formal-opt` | ~60+ |
| `decision_flow.tex` | **Appendix** — executive narrative of parameter selection (9-step chain) | `app:decision-flow` | ~266 |

### What overlaps

1. **The 216-configuration parametric sweep:**
   - `search_optimization.tex` (SUPERSEDED, commented out in main.tex): describes the sweep + Table `tab:energy-top5-old`
   - `path_optimization_definitive.tex` sec:sweep: describes the same sweep + Table `tab:energy-top-bottom` (identical data, different labels)
   - `optimization_master.tex` sec:opt-physics: describes the sweep again + Table `tab:opt-top3`
   - `decision_flow.tex` sec:df-evaluation: summarises the sweep + Table `tab:df-top3` (top 3, same numbers)
   - `design_rationale.tex` sec:search-param-opt: mentions the sweep results (1-2 sentences + figure reference)
   - **Verdict: The sweep is described FOUR TIMES in active files.** `search_optimization.tex` is already commented out (good). But `path_optimization_definitive.tex`, `optimization_master.tex`, and `decision_flow.tex` all present the 216-sweep methodology and top-3 results with near-identical tables. `design_rationale.tex` is a brief summary which is fine.

2. **Energy model (P_hover + P_drag):**
   - `path_optimization_definitive.tex` sec:energy-model: Eq `eq:power-model` and `eq:total-energy`
   - `optimization_master.tex` sec:opt-physics: Eq `eq:opt-power` and `eq:opt-energy`
   - `decision_flow.tex`: not restated (references figures)
   - **Verdict: ACCIDENTAL duplicate.** The same power model (P_hover=150W, P_drag_ref=50W, v_ref=5m/s, quadratic scaling, 2s U-turn penalty) is derived twice in near-identical language.

3. **Selected operating point (35m, 70deg, 8m/s):**
   - Stated with a summary table in `path_optimization_definitive.tex` (Table `tab:pareto-final`), `optimization_master.tex` (Table `tab:opt-final`), `decision_flow.tex` (Table `tab:df-final`), and `design_rationale.tex` (in-text)
   - **Verdict: The final parameters table appears THREE TIMES.** Each table has slightly different columns/emphasis but presents the same 6 parameters with the same values.

4. **Top-3 configurations table:**
   - `optimization_master.tex` Table `tab:opt-top3`: 3 rows (alt, angle, speed, Pd, C, energy, S, trade-off)
   - `decision_flow.tex` Table `tab:df-top3`: 3 rows (alt, angle, speed, Pd, energy, score, "why not?")
   - `path_optimization_definitive.tex` Table `tab:energy-top-bottom`: 10 rows (top 5 + bottom 5)
   - **Verdict: Near-identical tables.** The top-3 data (35m/70deg, 30m/65deg, 40m/75deg) is tabulated three times.

5. **Pareto frontier figures:**
   - `optimization_master.tex`: 5 Pareto figures (2D composite, curve, 3D, parallel coordinates, simplified)
   - `path_optimization_definitive.tex`: 2 Pareto figures (2D composite, altitude tradeoff dual)
   - `decision_flow.tex`: references the same figures but doesn't add new ones
   - **Verdict: Partially intentional.** `optimization_master.tex` has the full Pareto gallery; `path_optimization_definitive.tex` reuses `pareto_2d_composite` (same figure file). The same figure appearing in two sections is fine as long as the label doesn't conflict (they use different labels).

6. **Search strategy comparison (boustrophedon vs 5 alternatives):**
   - `05_path_planning.tex` sec:cpp: brief 3-strategy comparison (boustrophedon, spiral, random)
   - `path_optimization_definitive.tex` sec:strategy-compare: detailed 6-strategy comparison with Table `tab:strategy-compare` + 5 justification points
   - `optimization_master.tex` sec:opt-alternatives: 3 alternative strategies (wind-aligned, adaptive speed, two-pass altitude)
   - `decision_flow.tex` sec:df-pattern-type: rotation vs no-rotation variant
   - **Verdict: Intentional different scope.** `05_path_planning.tex` is the algorithm description. `path_optimization_definitive.tex` is the strategy justification. `optimization_master.tex` covers alternatives not in `path_optimization_definitive.tex`. `decision_flow.tex` covers a detail (rotation) not elsewhere. Complementary, not duplicate.

7. **Detection probability chain (altitude -> GSD -> pixel extent -> Pd):**
   - `path_optimization_definitive.tex` sec:detect-prob: full derivation + Table `tab:detect-chain`
   - `optimization_master.tex` sec:opt-physics "Detection Model": same derivation with Eqs `eq:opt-modelpx`, `eq:opt-psingle`, `eq:opt-pdetect`
   - `decision_flow.tex` paragraphs 1-3: narrative version of same chain
   - **Verdict: ACCIDENTAL triple-derivation.** The sigmoid detection model and cumulative detection formula appear three times.

8. **NFZ speed ramp description:**
   - `path_optimization_definitive.tex` sec:nfz-interaction: Eq `eq:speed-ramp` + 3-layer description
   - `optimization_master.tex`: mentions speed ramp in energy model subsection
   - `13_safety_risk.tex` sec:geofencing: 5-layer geofence including speed ramp
   - `decision_flow.tex` paragraph 5: mentions 30m buffer + speed ramp
   - **Verdict: Partially duplicate.** The NFZ speed ramp is described in full in `13_safety_risk.tex` (its natural home) and again in `path_optimization_definitive.tex` (energy impact context). The energy-impact perspective is unique to `path_optimization_definitive.tex`, but the mechanism description is duplicated.

### Recommendations

| Action | File | Detail |
|--------|------|--------|
| **Designate one primary for sweep + energy model** | `path_optimization_definitive.tex` | This should be the SINGLE definitive appendix for: energy model, 216-sweep methodology, top configurations, selected operating point. It already has the "DEFINITIVE" status comment. |
| **Refocus `optimization_master.tex`** | `optimization_master.tex` | Remove the energy model derivation (cross-ref to `path_optimization_definitive.tex`). Remove the top-3 table (cross-ref). Keep ONLY what is unique: composite scoring formula, Pareto frontier gallery (5 figures), sensitivity analysis, tornado chart, coupling N2 diagram, spider plot. Rename section to "Pareto Analysis and Sensitivity" to clarify scope. Saves ~80 lines. |
| **Refocus `decision_flow.tex`** | `decision_flow.tex` | Remove Table `tab:df-top3` (cross-ref `tab:opt-top3`). Remove Table `tab:df-final` (cross-ref `tab:opt-final`). Keep the 9-step narrative, sequential measurement chain, decomposition, robustness table, and qualitative choices---these are genuinely unique and valuable as an executive narrative. Saves ~30 lines. |
| **Refocus `optimization_formal.tex`** | `optimization_formal.tex` | Keep as the formal MOO problem statement. It already self-identifies as the "rigorous formulation" and doesn't heavily duplicate the sweep results. Fine as-is. |
| **Keep `design_strategy.tex` as-is** | `design_strategy.tex` | Philosophy + strategy alternatives are unique. It references results from other files without restating them. |
| **Keep `search_optimization.tex` commented out** | `search_optimization.tex` | Already correctly superseded. Do not re-enable. |
| **Cross-ref NFZ speed ramp** | `path_optimization_definitive.tex` | In sec:nfz-interaction, replace the mechanism description with a cross-ref to sec:geofencing and focus only on the energy-impact analysis (which is unique). |
| **Single detection model derivation** | `optimization_master.tex` or `path_optimization_definitive.tex` | Pick one as the primary location for the sigmoid + cumulative Pd equations. The other should cross-reference. Recommendation: keep it in `path_optimization_definitive.tex` (where the full detection-chain table lives) and cross-ref from `optimization_master.tex`. |

**Primary for energy model + sweep + selected config:** `path_optimization_definitive.tex`
**Primary for Pareto analysis + sensitivity:** `optimization_master.tex`
**Primary for executive narrative:** `decision_flow.tex`
**Primary for formal math:** `optimization_formal.tex`

---

## Cluster 5: Additional Minor Overlaps

### 5a. Simulation validation
- `09_simulation.tex` (appendix) and `simulation_validation.tex` (appendix): not checked in detail but likely overlap on sim-to-real gap discussion. `10_testing.tex` sec:sim-fidelity-summary also touches this.
- **Recommendation:** Spot-check these three for duplicate sim-to-real gap content.

### 5b. Field results
- `11_field_results.tex` and `field_day_narrative.tex`: likely overlap on bench day events.
- **Recommendation:** Spot-check; `field_day_narrative.tex` is probably the expanded version.

### 5c. Requirements
- `requirements_verification.tex` (main body) and `requirements_detail.tex` (appendix): by design, the main body has a summary table and the appendix expands each requirement.
- **Verdict: Intentional.** No action needed.

### 5d. Evaluation
- `evaluation.tex` (main body) and `evaluation_detail.tex` (appendix): same pattern.
- **Verdict: Intentional.** No action needed.

### 5e. CV content
- `04_computer_vision.tex` and `cv_extended.tex`: main body + deep appendix pattern.
- **Verdict: Intentional.** No action needed.

---

## Summary: Estimated Savings

| Cluster | Files affected | Duplicate lines (est.) | Action |
|---------|---------------|----------------------|--------|
| GPS Estimation | localization_approaches.tex | ~15 | Cross-ref GSD/WGS84 equations |
| Testing | 10_testing.tex, testing_deep.tex | ~70 | Cross-ref tiers + scripts to test_scripts_guide |
| Testing | testing_deep.tex | ~25 | Cross-ref experiment scripts to test_scripts_guide |
| Safety/Contingency | contingency.tex | ~40 | Merge failure tables, cross-ref RC guard + failsafes |
| Optimisation | optimization_master.tex | ~80 | Remove energy model + top-3 table, keep Pareto/sensitivity |
| Optimisation | decision_flow.tex | ~30 | Remove top-3 and final-params tables, keep narrative |
| Optimisation | path_optimization_definitive.tex | ~15 | Cross-ref NFZ mechanism to safety section |
| Optimisation | optimization_master.tex | ~20 | Cross-ref detection model to path_optimization_definitive |
| **Total** | | **~295 lines** | |

Consolidation would remove approximately 295 lines of duplicate content (roughly 3-4 pages)
while improving readability by giving the reader a single authoritative location for each
topic. No content would be lost---only redirected to its primary home via cross-references.

---

## Priority Order for Fixes

1. **HIGH: Optimisation cluster** (4 files with heavy overlap) --- most confusing for the reader
2. **MEDIUM: Testing cluster** (3 files with moderate overlap) --- reader encounters 5-tier framework three times
3. **MEDIUM: Safety/Contingency** (2 files with overlapping failure tables) --- reader sees same failure modes twice
4. **LOW: GPS Estimation** (minor equation repetition) --- small and the cross-ref is easy
