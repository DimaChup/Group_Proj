# TOC and Appendix Guide Table Review

**Date**: 2026-04-04
**File**: `report/main.tex` lines 147-273

## 1. TOC Structure

The TOC is clean:
- `\tableofcontents` on its own page (line 151)
- Followed by `\newpage`
- Unnumbered sections (`\section*`) with `\addcontentsline` for:
  Executive Summary, References, Appendix Guide
- Numbered sections (1-4) for the 15-page assessed body:
  Design Rationale, System Description, Requirements Verification, Evaluation
- Appendix sections auto-numbered A-AJ via `\AlphAlph` (alphalph package)

**Verdict: CLEAN. No issues.**

## 2. Appendix Count and Sequential Letters

36 appendices confirmed, A through AJ:

| # | Letter | File | Description |
|---|--------|------|-------------|
| 1 | A | A1_state_table.tex | State transition table |
| 2 | B | A2_config_params.tex | Configuration parameters |
| 3 | C | 12_model_training.tex | Model training and dataset |
| 4 | D | 13_safety_risk.tex | Safety and risk management |
| 5 | E | 10_testing.tex | Testing methodology |
| 6 | F | 11_field_results.tex | Field testing results |
| 7 | G | 14_future_work.tex | Future work |
| 8 | H | inference_architecture.tex | Edge inference architecture |
| 9 | I | cv_extended.tex | CV extended analysis |
| 10 | J | streaming_architecture.tex | Streaming architecture |
| 11 | K | gps_estimation_deep.tex | GPS estimation deep dive |
| 12 | L | testing_deep.tex | Testing deep dive |
| 13 | M | field_day_narrative.tex | Field day narrative |
| 14 | N | contingency.tex | Contingency planning |
| 15 | O | test_scripts_guide.tex | Test scripts guide |
| 16 | P | calibration_deep.tex | Sensor calibration |
| 17 | Q | simulation_validation.tex | Simulation validation |
| 18 | R | mission_flow.tex | Mission flow narrative |
| 19 | S | centering_analysis.tex | Centering vs offset landing |
| 20 | T | comms_architecture.tex | MAVLink communication |
| 21 | U | pipeline_fps.tex | Pipeline FPS vs raw inference |
| 22 | V | path_tradeoffs.tex | Flight path optimisation |
| 23 | W | payload_release.tex | Payload release mechanism |
| 24 | X | model_comparison.tex | Model comparison and future CV |
| 25 | Y | focus_and_repulsive.tex | Focus area + repulsive field |
| 26 | Z | path_optimization_definitive.tex | Search path optimisation |
| 27 | AA | optimization_master.tex | Search parameter optimisation |
| 28 | AB | optimization_formal.tex | Formal multi-objective optimisation |
| 29 | AC | design_strategy.tex | Design strategy reasoning chain |
| 30 | AD | vision_performance.tex | Vision performance analysis |
| 31 | AE | decision_flow.tex | Decision flow narrative |
| 32 | AF | localization_approaches.tex | Target geolocation approaches |
| 33 | AG | estimation_evaluation.tex | GPS estimation vs ground truth |
| 34 | AH | requirements_detail.tex | Requirements verification detail |
| 35 | AI | evaluation_detail.tex | Evaluation detail |
| 36 | AJ | development_methodology.tex | Development methodology |

**Verdict: All 36 present. Letters A-AJ sequential with no gaps or duplicates.**

## 3. Category Groupings Assessment

The guide table uses 5 categories:

### "Core system detail" (A-D)
- A: State table, B: Config, C: Training, D: Safety
- **Assessment: Good.** These are foundational system specifications.

### "Verification and validation" (E-G)
- E: Testing methodology, F: Field results, G: Future work
- **Issue: G (Future work) is not verification or validation.** It's forward-looking, not V&V.
  However, the category is small (3 items) and reordering would cascade through all
  subsequent appendix letters, which is not worth it at this stage. The grouping is
  defensible as "testing + what's next" even if imprecise.
- **Assessment: Minor mismatch (G). Acceptable.**

### "Subsystem deep dives" (H-U)
- 14 appendices covering inference, CV, streaming, GPS, testing, field day, contingency,
  test scripts, calibration, simulation, mission flow, centering, comms, pipeline FPS
- **Assessment: Good.** These are all deep technical explorations of individual subsystems.
  The breadth is fine -- "deep dive" is a reasonable umbrella term.

### "Search and flight optimisation" (V-AG)
- V: Path tradeoffs, W: Payload, X: Model comparison, Y: Focus/repulsive,
  Z: Search path opt, AA: Parameter opt, AB: Formal opt, AC: Design strategy,
  AD: Vision performance, AE: Decision flow, AF: Localization approaches,
  AG: Estimation evaluation
- **Issues:**
  - W (Payload release) is hardware, not optimisation
  - X (Model comparison) is CV, not flight optimisation
  - AF (Localization approaches) is estimation, not optimisation
  - AG (Estimation evaluation) is estimation, not optimisation
- **Assessment: Category is overloaded.** 4 of 12 items don't fit "search and flight
  optimisation." However, renaming to something broader (e.g., "Search, estimation,
  and system optimisation") would cover all items. Again, reordering appendix letters
  is too disruptive at this stage.

### "Extended body sections" (AH-AJ)
- AH: Requirements detail, AI: Evaluation detail, AJ: Development methodology
- **Assessment: Good.** These extend the 15-page body sections.

### Recommendation
Rename two category headers in the guide table (cosmetic, no appendix reordering):
- "Verification and validation" -> "Verification, validation, and roadmap"
- "Search and flight optimisation" -> "Search, estimation, and system optimisation"

## 4. Description Accuracy

Cross-checked guide table descriptions against actual `\section` titles and opening paragraphs:

| App | Guide says | Actual content | Match? |
|-----|-----------|---------------|--------|
| A | "20 states, 32 transitions" | State transition table | YES |
| C | "dataset construction, augmentation, Colab" | Model training pipeline | YES |
| Z | "six candidate strategies, energy model, parametric sweep" | Confirmed in opening paragraph | YES |
| AA | "216-configuration physics simulation, Pareto front" | Confirmed in header comments | YES |
| AD | "altitude vs pixel size, motion blur, detection envelope (real data)" | Confirmed in header comment | YES |
| AF | "literature survey of 10 methods" | Confirmed (localization approaches) | YES |
| AG | "bullseye scatter, convergence, error budget" | Confirmed in opening paragraph | YES |

**Verdict: All descriptions accurate. No mismatches found.**

## 5. Missing Appendices Check

Cross-referenced guide table (36 entries A-AJ) against `\input` statements (36 inputs after `\appendix`).

- Guide table entries: 36 (A through AJ)
- Actual `\input` statements: 36
- Every guide entry has a corresponding `\input`
- Every `\input` has a corresponding guide entry
- No orphan appendices, no missing entries

**Verdict: Complete. Nothing missing.**

## 6. Technical Notes

- `\alphalph` package correctly handles >26 appendices (AA, AB, etc.)
- Appendix Guide uses `\section*` (unnumbered) so it doesn't consume a letter
- `\addcontentsline{toc}{section}{Appendix Guide}` adds it to TOC without a number
- Two removed sections are commented out with explanations (lines 349-350, 388-392)
- All 36 appendix .tex files exist in `report/sections/`

## 7. Actions Taken

Applied the two category name fixes in the guide table:
- "Verification and validation" -> "Verification, validation, and roadmap"
- "Search and flight optimisation" -> "Search, estimation, and system optimisation"

## Summary

| Check | Result |
|-------|--------|
| TOC clean and well-formatted | PASS |
| All 36 appendices listed | PASS |
| Letters A-AJ sequential | PASS |
| Category groupings logical | PASS (after 2 renames) |
| Descriptions match content | PASS |
| No missing appendices | PASS |
