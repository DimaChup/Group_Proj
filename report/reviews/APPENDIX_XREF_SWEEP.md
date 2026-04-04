# Appendix Cross-Reference Sweep

**Date:** 2026-04-04
**Scope:** Check every appendix (A through AJ) is referenced from at least one body section.

## Method

1. Extracted the `\label{}` for every appendix section and subsection.
2. Searched the four body files (`design_rationale.tex`, `system_description.tex`, `requirements_verification.tex`, `evaluation.tex`) for `\ref{}` calls to each appendix label (including subsection labels).
3. Any appendix with zero references from the body was flagged as "invisible to the reader."

## Appendices Already Referenced (no action needed)

| App | Label | Referenced from |
|-----|-------|-----------------|
| A | `app:states` | design_rationale (x2), system_description (x2) |
| B | `app:config` | system_description |
| E | `sec:testing` / `sec:five-tier` | intro_d6, evaluation |
| H | `sec:cv:inference` | system_description |
| I | `app:cv-extended` / `app:cv:benchmarks` / `app:cv:training` / `app:cv:speed` | system_description, evaluation |
| J | `sec:streaming-arch` | system_description (x2) |
| K | `sec:gps-deep` / `sec:centering-mitigation` | system_description, evaluation, design_rationale |
| L | `sec:testing-deep` / `sec:test-org-detail` / `sec:bug-discovery` | evaluation |
| M | `sec:field-day` | design_rationale, evaluation |
| O | `sec:test-scripts` | system_description |
| P | `sec:calibration` | system_description |
| Q | `sec:sim-validation` | system_description |
| Y | `sec:focus-repulsive` / `sec:repulsive-field` | system_description |
| Z | `sec:path-opt` / `sec:nfz-interaction` | design_rationale (x3), system_description |
| AC | `sec:design-strategy` | design_rationale |
| AE | `app:decision-flow` | design_rationale (x2) |
| AF | `sec:loc-approaches` | design_rationale |
| AG | `sec:estimation-eval` | design_rationale (x2), requirements_verification (x3), evaluation (x2) |
| AH | `app:req-detail` | design_rationale, requirements_verification (x2), evaluation |
| AI | `app:eval-detail` / `app:bug-cost` / `app:lessons-learned` | evaluation (x4) |

## Appendices That Were Unreferenced (16 total -- all now fixed)

| App | Label | Added reference in | Context |
|-----|-------|--------------------|---------|
| C | `sec:training` | `design_rationale.tex` | Model selection paragraph, after COCO fallback sentence |
| D | `sec:safety` | `system_description.tex` | After state machine safety mechanisms, alongside `app:states` |
| F | `sec:results` | `evaluation.tex` | Weather cancellation paragraph, after field-day reference |
| G | `sec:future` | `evaluation.tex` | End of Prioritised Future Work subsection |
| N | `sec:contingency` | `evaluation.tex` | End of Prioritised Future Work subsection |
| R | `sec:mission-flow` | `system_description.tex` | After state machine safety mechanisms, alongside `app:states` |
| S | `sec:centering-analysis` | `system_description.tex` | Target localisation subsection, after GPS-deep reference |
| T | `sec:comms` | `system_description.tex` | Hardware platform subsection, after streaming-arch reference |
| U | `sec:cv:pipeline-fps` | `system_description.tex` | CV performance paragraph, after cv:speed reference |
| V | `sec:path-tradeoffs` | `design_rationale.tex` | Coverage path planning, after lawnmower selection |
| W | `sec:payload-release` | `evaluation.tex` | End of Prioritised Future Work subsection |
| X | `sec:model_comparison` | `design_rationale.tex` | Model selection paragraph, after COCO fallback sentence |
| AA | `sec:optimisation` | `design_rationale.tex` | Coverage path planning, after lawnmower selection |
| AB | `sec:formal-opt` | `design_rationale.tex` | Coverage path planning, after lawnmower selection |
| AD | `sec:vision-perf` | `system_description.tex` | CV performance paragraph, after cv:speed reference |
| AJ | `app:dev-methodology` | `evaluation.tex` | Simulation-first discussion paragraph |

## New Appendices Check

Both new appendices added in the latest session were already well-referenced:

- **AF (localization_approaches)**: Referenced from `design_rationale.tex` in the target localisation rationale paragraph and from `system_description.tex` in the localisation subsection.
- **AG (estimation_evaluation)**: Referenced 7 times across `design_rationale.tex` (x2), `requirements_verification.tex` (x3), and `evaluation.tex` (x2). Heavily integrated.

## Bonus: Broken Reference Found

- `evaluation.tex` line 186 references `Section~\ref{sec:autonomy-level}` but no such label exists. The correct label is `sec:autonomy-rationale` (in `design_rationale.tex`). The linter appears to have already fixed this to `sec:autonomy-rationale`.

## Files Modified

- `report/sections/design_rationale.tex` -- added refs to C, V, X, AA, AB
- `report/sections/system_description.tex` -- added refs to D, R, S, T, U, AD
- `report/sections/evaluation.tex` -- added refs to F, G, N, W, AJ
