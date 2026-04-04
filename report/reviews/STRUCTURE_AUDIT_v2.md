# Goldmine Report Structure Audit v2

**Date:** 2026-04-03
**File:** `report/main.tex`
**Total appendices:** 35 (A through AI)
**Total body sections:** 4 counted + Executive Summary + Introduction (excluded)

---

## 1. Document Structure Overview

### Pre-counted content (excluded from 15-page limit)
| Order | File | Title | Lines | Quality |
|-------|------|-------|-------|---------|
| Cover | (inline) | Cover page | -- | OK |
| ToC | (inline) | Table of Contents | -- | OK |
| Exec Summary | `exec_summary.tex` | Executive Summary | 18 | HIGH -- dense, quantitative, comprehensive |
| Introduction | `intro_d6.tex` | Introduction (D6) | 79 | HIGH -- context, company, roles, contributions table |

### Counted body (15-page limit)
| Order | File | Title | Lines | Quality |
|-------|------|-------|-------|---------|
| Sec 1 | `design_rationale.tex` | Design Rationale | 250 | HIGH -- 4 MCDA tables, STEEPLE, parameter chain, evidence-based corrections |
| Sec 2 | `system_description.tex` | System Description | 212 | HIGH -- 6 subsystems, BOM, architecture, CV, FSM, localisation, ground station, simulation |
| Sec 3 | `requirements_verification.tex` | Requirements Verification | 30 | MEDIUM -- single summary table, delegates detail to Appendix AG |
| Sec 4 | `evaluation.tex` | Evaluation | 155 | HIGH -- 10 plus items, 9 delta items, discussion, testing framework summary |

### Post-counted content (excluded)
- References (biber, two .bib files)
- Appendix Guide (1-page directory table)

---

## 2. Appendix Map (declared letter vs actual \input order)

The appendix guide table (lines 222-262 of main.tex) declares letters A-AI.
The `\input` statements follow in the same order. Because `\renewcommand{\thesection}{\AlphAlph{\value{section}}}` is used, LaTeX auto-numbers them A, B, C, ... AA, AB, etc.

| Declared | File | \section label | Title | Lines | Quality |
|----------|------|---------------|-------|-------|---------|
| A | `A1_state_table.tex` | `app:states` | State Transition Table | 244 | HIGH -- full 20-state, 32-transition table + diagram |
| B | `A2_config_params.tex` | `app:config` | Configuration Parameters | 82 | MEDIUM -- good but short, single table |
| C | `12_model_training.tex` | `sec:training` | Model Training and Dataset | 224 | HIGH -- 3-source strategy, augmentation, Colab workflow |
| D | `13_safety_risk.tex` | `sec:safety` | Safety and Risk Management | 114 | MEDIUM -- geofence detail good but could expand HAZOP |
| E | `10_testing.tex` | `sec:testing` | Testing Methodology | 190 | HIGH -- V-model, five-tier framework, stress tests |
| F | `11_field_results.tex` | `sec:results` | Field Testing and Results | 107 | MEDIUM -- bench results, FOV cal, good but brief |
| G | `14_future_work.tex` | `sec:future` | Future Work | 52 | LOW-MEDIUM -- only 52 lines, could be more substantive |
| H | `inference_architecture.tex` | `sec:cv:inference` | Edge Inference Architecture | 127 | HIGH -- Pi 5 constraints, backend comparison, quantisation |
| I | `cv_extended.tex` | `app:cv-extended` | CV Extended Analysis | 402 | HIGH -- detailed pipeline timing, benchmarks, altitude analysis |
| J | `streaming_architecture.tex` | `sec:streaming-arch` | Streaming Architecture | 256 | HIGH -- protocol comparison, threading model, bandwidth |
| K | `gps_estimation_deep.tex` | `sec:gps-deep` | GPS Target Estimation Deep Dive | 2212 | VERY HIGH -- massive 7-part deep dive, most detailed appendix |
| L | `testing_deep.tex` | `sec:testing-deep` | Progressive Testing Deep Dive | 227 | HIGH -- philosophy, tier detail, V-model mapping |
| M | `field_day_narrative.tex` | `sec:field-day` | Field Day Narrative | 131 | MEDIUM-HIGH -- good narrative, concrete outcomes |
| N | `contingency.tex` | `sec:contingency` | Contingency Planning | 152 | HIGH -- 3-tier deliverables, 8 failure scenarios |
| O | `test_scripts_guide.tex` | `sec:test-scripts` | Test Script Reference | 226 | HIGH -- all 58 scripts categorised |
| P | `calibration_deep.tex` | `sec:calibration` | Sensor Calibration | 237 | HIGH -- FOV, lens, colour, pre-flight checklist |
| Q | `simulation_validation.tex` | `sec:sim-validation` | Simulation Validation | 158 | MEDIUM-HIGH -- sim-to-real gap analysis |
| R | `mission_flow.tex` | `sec:mission-flow` | Mission Flow | 146 | MEDIUM-HIGH -- pre-flight to landing narrative |
| S | `centering_analysis.tex` | `sec:centering-analysis` | Centering vs Direct Offset | 175 | HIGH -- quantitative trade-off, 3 risk factors |
| T | `comms_architecture.tex` | `sec:comms` | MAVLink Communication | 101 | MEDIUM -- Python 3.13 issue, MAVProxy bridge, failsafes |
| U | `pipeline_fps.tex` | `sec:cv:pipeline-fps` | Pipeline FPS vs Raw Inference | 94 | MEDIUM -- overhead budget, good but compact |
| V | `path_tradeoffs.tex` | `sec:path-tradeoffs` | Flight Path Optimisation | 83 | MEDIUM -- diagonal vs axis-aligned, wind, PLB redirect |
| W | `payload_release.tex` | `sec:payload-release` | Payload Release Mechanism | 58 | LOW-MEDIUM -- shortest appendix, basic servo description |
| X | `model_comparison.tex` | `sec:model_comparison` | Model Comparison | 79 | MEDIUM -- 3 model generations table, tiling discussion |
| Y | `search_optimization.tex` | `sec:search-opt` | Multi-Objective Search Opt. | 251 | MEDIUM -- **overlaps significantly with AA/AB/AC/AD** |
| Z | `focus_and_repulsive.tex` | `sec:focus-repulsive` | Focus Area + Repulsive Field | 130 | MEDIUM-HIGH -- PLB logic, repulsive vector field |
| AA | `path_optimization_definitive.tex` | `sec:path-opt` | Search Path Optimisation | 381 | HIGH -- **definitive**, 216-config sweep, energy model |
| AB | `optimization_master.tex` | `sec:optimisation` | Search Parameter Optimisation | 372 | HIGH -- physics sim, Pareto, sensitivity, coupling |
| AC | `optimization_formal.tex` | `sec:formal-opt` | Formal Multi-Objective Opt. | 247 | HIGH -- mathematical problem statement, constraints |
| AD | `design_strategy.tex` | `sec:design-strategy` | Design Strategy Chain | 294 | HIGH -- step-by-step parameter derivation |
| AE | `vision_performance.tex` | `sec:vision-perf` | Vision Performance Analysis | 302 | HIGH -- altitude, blur, frames, coverage envelope |
| AF | `decision_flow.tex` | `app:decision-flow` | Decision Flow (Executive) | 216 | HIGH -- plain-English narrative, cherry-picked figures |
| AG | `requirements_detail.tex` | `app:req-detail` | Requirements Detail (R01-R12) | 145 | MEDIUM -- per-requirement evidence, could be expanded |
| AH | `evaluation_detail.tex` | `app:eval-detail` | Evaluation Detail | 77 | LOW-MEDIUM -- defect register table, lessons learned |
| AI | `development_methodology.tex` | `app:dev-methodology` | Development Methodology | 390 | HIGH -- philosophy, 10-phase timeline, lessons |

---

## 3. Structural Issues Found

### 3.1 BROKEN CROSS-REFERENCES (will show "??" in PDF)

1. **`\ref{sec:req-detail}`** -- used in `design_rationale.tex` (line 59) and `decision_flow.tex`, but the label is `app:req-detail` (in `requirements_detail.tex`). This produces an undefined reference warning in the LaTeX log.

2. **`\label{sec:vp:frames}` multiply defined** -- confirmed by LaTeX log. Appears in `vision_performance.tex` in two places.

### 3.2 HARDCODED APPENDIX LETTERS ARE WRONG

Evaluation.tex uses hardcoded appendix letters that do not match the actual ordering:

| In evaluation.tex | Says | Should be | Correct appendix |
|-------------------|------|-----------|-----------------|
| P3 | "Appendix~K for the full defect register" | Appendix~AH | `evaluation_detail.tex` has `\label{app:bug-cost}` |
| P7 | "Appendix~N for the full script inventory" | Appendix~O | `test_scripts_guide.tex` is the 15th appendix = O |
| P7 | "Appendix~K (`\secref{sec:test-org-detail}`)" | Appendix~L | `sec:test-org-detail` is in `testing_deep.tex` = L |

**Recommendation:** Replace all hardcoded appendix letters with `\ref{}` to auto-generated labels. Alternatively, verify every hardcoded letter against the actual \input order.

### 3.3 MASSIVE CONTENT OVERLAP IN OPTIMISATION APPENDICES (Y, AA, AB, AC, AD, AF)

Six appendices cover search parameter optimisation from different angles:

| App | Title | Lines | Focus |
|-----|-------|-------|-------|
| Y | Multi-Objective Search Opt. | 251 | 5 objectives, parametric sweep (overlaps AA) |
| AA | Search Path Optimisation | 381 | **Definitive**: 216-config sweep, energy model |
| AB | Search Parameter Optimisation | 372 | Physics sim, Pareto, sensitivity |
| AC | Formal Multi-Objective Opt. | 247 | Mathematical problem statement |
| AD | Design Strategy Chain | 294 | Parameter derivation reasoning |
| AF | Decision Flow (Executive) | 216 | Plain-English narrative |

Appendix Y explicitly says: *"Note: The definitive path optimisation analysis appears in Appendix AA; the formal problem statement in Appendix AC..."* -- it acknowledges it is superseded but is "retained for completeness." This is **1761 lines** (roughly 25+ pages) on the same topic from different angles. A reader/assessor may see this as padding.

**Recommendation:** Either consolidate Y into AA (merge unique content, remove Y as standalone) or add a clear note in the appendix guide that Y/AA/AB/AC/AD/AF form a progressive deep-dive on the same topic.

### 3.4 LEGACY FILES IN sections/ DIRECTORY

15 unused .tex files remain in `sections/`:
- `00_abstract.tex` through `09_simulation.tex` (10 files) -- old numbered structure, superseded
- `15_conclusion.tex` -- no conclusion in current structure
- `alternatives.tex`, `figure_descriptions.tex` -- commented out in main.tex
- `introduction.tex`, `steeple.tex` -- superseded by `intro_d6.tex` and `design_rationale.tex`
- `vision_standalone.tex` -- standalone CV report, not part of this document

These contain **duplicate labels** that would conflict if accidentally re-included (e.g., `sec:cv`, `sec:groundstation`, `fig:architecture`, `tab:steeple`). Currently harmless because they are not `\input`-ed, but a maintenance risk.

### 3.5 APPENDIX GUIDE TABLE vs CONTENT MISMATCH

Minor wording discrepancies between the appendix guide descriptions and actual section titles:

| App | Guide says | Actual \section title |
|-----|-----------|----------------------|
| P | "Sensor calibration --- FOV, lens distortion, GPS ground truth, pre-flight checklist, error budget cross-reference" | "Sensor Calibration" (simpler) |
| AI | Long description in guide | "Development Methodology" (simpler) |

These are cosmetic -- the guide descriptions are more detailed than the actual titles, which is fine.

### 3.6 INCONSISTENT LABEL NAMESPACE

Labels mix `sec:`, `app:`, and no prefix inconsistently:
- Appendix A uses `app:states` (good)
- Appendix B uses `app:config` (good)
- Appendix C uses `sec:training` (should be `app:`)
- Appendix D uses `sec:safety` (should be `app:`)
- Most other appendices use `sec:` prefix despite being appendices

This is not a compile error but makes cross-referencing confusing. `\ref{sec:training}` could be mistaken for a body section when it is actually Appendix C.

---

## 4. Logical Ordering Assessment

The current ordering is **largely logical**:

**Body sections:** Design Rationale -> System Description -> Requirements Verification -> Evaluation. This follows a natural engineering narrative (why -> what -> does it work -> how well). **Good.**

**Appendices A-G:** Core supplementary material -- state table, config, training, safety, testing, field results, future work. **Good progression.**

**Appendices H-K:** Deep technical dives -- inference, CV extended, streaming, GPS estimation. **Good grouping by subsystem.**

**Appendices L-P:** Testing and calibration deep dives -- testing methodology, field day, contingency, test scripts, calibration. **Good grouping.**

**Appendices Q-T:** Simulation, mission flow, centering analysis, comms. **Reasonable.**

**Appendices U-X:** Miscellaneous technical -- pipeline FPS, path tradeoffs, payload, model comparison. **Fine but feels like a grab-bag.**

**Appendices Y-AF:** Optimisation cluster -- the weakest structural point. Six appendices on overlapping optimisation topics. **Needs consolidation or clearer delineation.**

**Appendices AG-AI:** Requirements detail, evaluation detail, dev methodology. **Should arguably be earlier** -- AG and AH are directly referenced by the body's requirements and evaluation sections. Placing them at the end (positions 33-35) means a reader following body references has to jump very far.

---

## 5. Quality Summary

| Rating | Count | Appendices |
|--------|-------|------------|
| VERY HIGH | 1 | K (GPS deep dive, 2212 lines) |
| HIGH | 17 | A, C, E, H, I, J, L, N, O, P, S, AA, AB, AC, AD, AE, AF, AI |
| MEDIUM-HIGH | 4 | M, Q, R, Z |
| MEDIUM | 7 | B, D, F, T, U, V, X |
| LOW-MEDIUM | 3 | G (52 lines), W (58 lines), AH (77 lines) |

**Strongest sections:** GPS deep dive (K), CV extended (I), path optimisation (AA/AB), design strategy (AD), development methodology (AI), state transition table (A).

**Weakest sections:** Future work (G, only 52 lines), payload release (W, 58 lines), evaluation detail (AH, only 77 lines -- defect register is thin for an appendix).

---

## 6. Actionable Recommendations (priority order)

1. **FIX `\ref{sec:req-detail}` -> `\ref{app:req-detail}`** in design_rationale.tex and decision_flow.tex. This is a compile-visible error ("??").

2. **FIX duplicate `\label{sec:vp:frames}`** in vision_performance.tex. One instance needs renaming.

3. **FIX hardcoded appendix letters** in evaluation.tex (P3 says "Appendix~K", P7 says "Appendix~N" and "Appendix~K" -- all wrong). Replace with `Appendix~\ref{...}` or correct the letters.

4. **Consider merging Appendix Y into AA** or removing Y entirely since it self-declares as superseded. This removes 251 lines of acknowledged redundancy.

5. **Move AG and AH earlier** (e.g., after F or G) so body cross-references to requirements detail and defect register don't jump 30+ appendices.

6. **Expand AH (evaluation detail)** -- at 77 lines it is the thinnest appendix. The defect register table deserves more analysis (cost savings, lessons per defect, statistical summary).

7. **Delete or archive legacy files** (01_introduction.tex through 09_simulation.tex, etc.) to remove duplicate label risk.
