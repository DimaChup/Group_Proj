# Goldmine Report -- Master Structure Document

> **File:** `report/main.tex`
> **Last updated:** 2026-04-03
> **Current score:** 85.2/100 (v6)
> **Target:** 87+ (top first-class band)

---

## What the User Wants from the Goldmine

### Philosophy
The goldmine is a **comprehensive reference document with no page limit on appendices**. The 15-page assessed body is surgically lean, but the appendices behind it form an exhaustive technical portfolio. Every appendix should be self-contained and independently readable, with a one-line "why this matters" summary at the top.

### Non-Negotiable Requirements
1. **Well-organized with clear TOC and appendix guide** -- a reader must find any topic in under 10 seconds
2. **Every claim backed by data** -- no vague statements, every metric cited with source (simulation, bench, DJI video, or field test)
3. **All requirements (R01--R12) proven met** -- evidence table in body, full narratives in Appendix AG
4. **Extensive technical depth** -- especially GPS estimation (Appendix K, 2200+ lines), CV pipeline (Appendix I), and search optimization (Appendices AA--AC)
5. **Multiple TikZ diagrams and charts** -- not just decoration; each diagram must convey information that prose cannot
6. **Literature references where applicable** -- DJI white papers, CAA regulations, JARUS guidelines, academic CV/GPS papers
7. **Professional appendix lettering** -- A through AI (35 appendices), consistently labeled with alphalph for AA+
8. **Cross-references working** -- every `\figref`, `\tabref`, `\secref` resolves (no `??` in compiled PDF)
9. **Clean compilation** -- zero errors, minimal warnings, biber bibliography resolves

### Data Presentation Preferences
- Comparison tables over prose for A/B decisions
- Before/after screenshots (simulation, ground station, detection)
- Radar/spider charts for multi-criteria comparisons (MCDA)
- Box plots for distribution data (GPS accuracy, inference times)
- Pareto fronts for optimization tradeoffs (search parameters)
- Annotated photographs of hardware with callouts
- Key findings boxes (`infobox` environment) for standout results
- Section summaries (1--2 sentences) at end of each body section

---

## Scoring History

| Version | Date | Specialist (40%) | Decision (40%) | Communication (20%) | Total |
|---------|------|-------------------|----------------|----------------------|-------|
| v1 | 2026-03-24 | -- | -- | -- | ~74 |
| v4 | 2026-03-27 | 82 | 80 | 78 | 80.4 |
| v5 | 2026-04-03 | 85 | 85 | 80 | 84.0 |
| v6 | 2026-04-03 | 86 | 87 | 80 | 85.2 |

---

## Current Structure (from main.tex)

### Front Matter (excluded from page count)
| Section | Source file | Description | ~Pages |
|---------|-----------|-------------|--------|
| Cover page | inline in main.tex | Title, author, unit, date | 1 |
| Table of Contents | `\tableofcontents` | Auto-generated | 1--2 |
| Executive Summary | `sections/exec_summary.tex` | Self-contained 1-page summary. Mentions field day pivot and weather adaptation | 1 |
| Introduction | `sections/intro_d6.tex` | Context, background, company description, member bios/roles, contributions | 1--2 |

### Body Sections (15-page assessed limit)

#### 1. Design Rationale (~4 pages)
**Source:** `sections/design_rationale.tex`

Justification of design decisions including STEEPLE considerations. Contains:
- MCDA tables (platform selection, detection approach, inference backend)
- STEEPLE analysis (societal, technological, economic, environmental, political, legal, ethical)
- Key design decisions with rationale (why YOLOv8n, why Pi 5, why lawnmower pattern, why TFLite)
- Trade-off studies summarized (full data in appendices)

**Scoring focus:** Decision Making (40%). Every decision must be evidence-based, not post-hoc.

#### 2. System Description (~5 pages)
**Source:** `sections/system_description.tex`

Architecture of the final system. Contains:
- High-level architecture diagram (state machine, module relationships)
- CV pipeline overview (4-phase detection flow: capture, preprocess, infer, postprocess)
- State machine description (20 states, key transitions)
- GPS target estimation summary (3-level architecture: passive, stop-and-look, visual centering)
- Communication architecture (Pi to Cube, ground station, RC override)
- Hardware integration (Pi 5, IMX296 camera, Cube Orange, payload servo)

**Scoring focus:** Specialist Skills (40%). Must show initiative, autonomy, and creativity.

#### 3. Requirements Verification (~3 pages)
**Source:** `sections/requirements_verification.tex`

Process and evidence of satisfaction of R01--R12. Contains:
- Summary evidence table (requirement, method, result, reference)
- Key evidence highlights (geofence logs, detection screenshots, landing accuracy)
- References to Appendix AG for full narratives per requirement
- 1440-test verification matrix reference

**Scoring focus:** Both Specialist (evidence quality) and Decision (verification approach).

#### 4. Evaluation (~3 pages)
**Source:** `sections/evaluation.tex`

Plus/delta review of system technical performance. Contains:
- Plus column: what worked well (CV pipeline, state machine robustness, simulation-first approach)
- Delta column: what to improve (no outdoor flight data, GPS estimation unvalidated outdoors)
- Honest assessment of simulation vs real gap
- Quantified performance metrics (inference speed, detection rate, GPS accuracy from sim)

**Scoring focus:** Decision Making (honesty and self-awareness score highly).

### Back Matter (excluded from page count)
| Section | Source | Description |
|---------|--------|-------------|
| References | `references.bib` + `extra_refs.bib` | Two-column bibliography via biber |

---

## Appendices (A--AI, not assessed, comprehensive)

All appendices are excluded from the 15-page limit and are not directly assessed, but they demonstrate depth and serve as evidence backing body claims.

| App | Source file | Title / Contents | ~Pages |
|-----|-----------|------------------|--------|
| Guide | inline in main.tex | 1-page directory of all appendices with descriptions | 1 |
| A | `sections/A1_state_table.tex` | Full state transition table -- 20 states, 32 transitions | 2 |
| B | `sections/A2_config_params.tex` | Configuration parameters -- all tuneable values and rationale | 2 |
| C | `sections/12_model_training.tex` | Model training pipeline -- dataset construction, augmentation, Colab workflow | 3 |
| D | `sections/13_safety_risk.tex` | Safety and risk management -- HAZOP, regulatory compliance, mitigations | 4 |
| E | `sections/10_testing.tex` | Testing methodology -- five-tier framework, stress tests, pass criteria | 4 |
| F | `sections/11_field_results.tex` | Field testing results -- calibration data, benchmark numbers, detection rates | 3 |
| G | `sections/14_future_work.tex` | Future work -- roadmap for post-submission development | 2 |
| H | `sections/inference_architecture.tex` | Edge inference architecture -- NCNN vs TFLite, quantisation, Pi 5 constraints | 3 |
| I | `sections/cv_extended.tex` | Computer vision extended analysis -- detection pipeline, altitude, dual backend | 4 |
| J | `sections/streaming_architecture.tex` | Video streaming and ground station architecture | 2 |
| K | `sections/gps_estimation_deep.tex` | GPS target estimation deep dive -- Kalman filter, clustering, error budget. **Flagship appendix: 2200+ lines, 12+ TikZ diagrams** | 15+ |
| L | `sections/testing_deep.tex` | Progressive testing deep dive -- test ladder, integration strategy | 3 |
| M | `sections/field_day_narrative.tex` | Field day narrative -- adaptation under weather cancellation | 2 |
| N | `sections/contingency.tex` | Contingency planning and deliverable tiers | 2 |
| O | `sections/test_scripts_guide.tex` | Test script reference -- all 41 scripts with usage and dependencies | 3 |
| P | `sections/calibration_deep.tex` | Sensor calibration -- FOV, lens distortion, GPS ground truth, error budget | 3 |
| Q | `sections/simulation_validation.tex` | Simulation validation and sim-to-real gap analysis | 3 |
| R | `sections/mission_flow.tex` | Mission flow -- real flight narrative, operator interaction | 2 |
| S | `sections/centering_analysis.tex` | Centering vs direct offset landing analysis | 2 |
| T | `sections/comms_architecture.tex` | MAVLink communication architecture | 2 |
| U | `sections/pipeline_fps.tex` | Raw inference vs effective pipeline throughput (FPS analysis) | 2 |
| V | `sections/path_tradeoffs.tex` | Flight path optimisation trade-offs | 2 |
| W | `sections/payload_release.tex` | Payload release mechanism -- servo hardware and actuation sequence | 1 |
| X | `sections/model_comparison.tex` | Model comparison and future vision improvements | 2 |
| Y | `sections/search_optimization.tex` | Multi-objective search optimisation -- energy, rotation, coverage | 3 |
| Z | `sections/focus_and_repulsive.tex` | Focus area redirect and repulsive field implementation | 2 |
| AA | `sections/path_optimization_definitive.tex` | Search path optimisation -- definitive 216-configuration data | 4 |
| AB | `sections/optimization_master.tex` | Search parameter optimisation -- physics sim, Pareto, sensitivity | 4 |
| AC | `sections/optimization_formal.tex` | Formal multi-objective optimisation | 3 |
| AD | `sections/design_strategy.tex` | Design strategy -- parameter derivation reasoning chain | 3 |
| AE | `sections/vision_performance.tex` | Vision performance analysis (real flight data) | 3 |
| AF | `sections/decision_flow.tex` | Decision flow: executive narrative of search parameter selection | 3 |
| AG | `sections/requirements_detail.tex` | Requirements verification detail -- R01--R12 evidence narratives | 5 |
| AH | `sections/evaluation_detail.tex` | Evaluation detail -- defect register, lessons learned, second iteration changes | 4 |
| AI | `sections/development_methodology.tex` | Development methodology -- simulation-first philosophy, 10-phase timeline, progressive testing ladder, ambition levels, sim-to-real gap analysis | 5 |

**Total appendices:** 35 (A through AI)
**Estimated appendix pages:** ~110--120

---

## Key Strengths (what scores well)

### Specialist Skills
1. **GPS estimation appendix (K)** -- 2200+ lines, 12+ TikZ diagrams, three-level estimation architecture (passive/stop-and-look/visual centering), error budget with 16 quantified sources, attitude compensation with literature comparison
2. **Four-phase detection flow** -- capture, preprocess, infer, postprocess; dual backend (Ultralytics on laptop, TFLite/NCNN on Pi); documented in body + Appendix I
3. **1440-test verification** -- comprehensive test matrix across requirements, referenced in body Section 3
4. **216-configuration search optimization** -- definitive parametric study with Pareto front (Appendix AA--AC)
5. **Progressive testing ladder** -- five-tier framework (bench to autonomous), shows initiative and safety awareness

### Decision Making
1. **MCDA tables with weighted criteria** -- platform, detection, inference backend decisions
2. **STEEPLE analysis** -- environmental (SSSI), legal (CAA), ethical (casualty privacy)
3. **Weather adaptation narrative** -- field day cancelled, pivoted to bench testing (Appendix M)
4. **Centering vs offset analysis** -- quantified safety argument with rotor wash, crash probability, noise (Appendix S)
5. **Honest evaluation** -- simulation-only limitation acknowledged explicitly

### Communication
1. **TikZ diagrams throughout** -- state machine, GPS geometry, detection pipeline, error budget, bias cancellation
2. **Appendix guide page** -- 1-page directory at start of appendices
3. **infobox environment** -- key findings highlighted in styled boxes
4. **Two-column references** -- professional bibliography layout
5. **Consistent heading hierarchy** -- blue headblue color scheme throughout

---

## What Still Needs Work

### Critical (blocks 87+ score)
1. **Hardware photos** -- no photos of assembled drone, Pi setup, or field day equipment. Even bench photos of Pi + Cube + camera assembly would add +2 Specialist, +3 Communication
2. **Ground station screenshots** -- no browser dashboard screenshot from pi_flight.py or passive_watch.py. Capture from http://PI_IP:8090 would add +2--3 Communication
3. **Detection example images** -- no montage of successful detections at various altitudes from video analysis. Grid of detections at 15m/25m/35m would add +2 Specialist

### Important (incremental improvements)
4. **MCDA sensitivity analysis** -- vary weights per table, show winner stability. Would add +2--3 Decision
5. **[NAME] placeholders** -- 4/5 team member names still missing in Introduction
6. **Broken cross-references** -- some `\ref{}` resolve to `??` in compiled PDF
7. **Bibliography cleanup** -- 6 duplicate bib entries, 15 duplicate labels across sections
8. **17 undefined acronyms** -- need `\newacronym` or inline definitions on first use
9. **Missing decision rationale** -- why 20% overlap? why 30m NFZ buffer? why 120s verify timeout?

### Nice to Have
10. **Precision-recall curve** for confidence threshold selection
11. **Train/val overlap** acknowledged but not resolved in dataset
12. **Body is ~29 pages** -- needs trimming to stay within 15-page limit (or verify current count)

---

## Scoring Rubric Summary

Assessment is via the D6 Company Report rubric (Appendix A of project brief):

| Criterion | Weight | Current | Target | What Gets 83+ |
|-----------|--------|---------|--------|----------------|
| Specialist Skills & Problem-Solving | 40% | 86 | 88+ | Confident, comprehensive identification. Appropriate technologies implemented highly effectively, showing initiative, autonomy, and creativity |
| Decision Making | 40% | 87 | 88+ | Confidence and creativity in adapting to changing/unfamiliar circumstances. Effective, evidence-based decisions |
| Communication | 20% | 80 | 85+ | Effective, engaging, professional. Innovative techniques and resources. **This is the bottleneck** -- needs real photos/screenshots |

### Communication is the Bottleneck
Communication at 80 drags the total down. Moving it to 85 (with hardware photos + ground station screenshot + detection montage) would push the total from 85.2 to ~87. This is the highest-leverage improvement remaining.

---

## File Map

```
report/
  main.tex                          -- master document (this structure)
  references.bib                    -- primary bibliography
  extra_refs.bib                    -- additional references
  sections/
    exec_summary.tex                -- executive summary
    intro_d6.tex                    -- introduction (bios, roles, contributions)
    design_rationale.tex            -- body section 1
    system_description.tex          -- body section 2
    requirements_verification.tex   -- body section 3
    evaluation.tex                  -- body section 4
    A1_state_table.tex              -- Appendix A
    A2_config_params.tex            -- Appendix B
    12_model_training.tex           -- Appendix C
    13_safety_risk.tex              -- Appendix D
    10_testing.tex                  -- Appendix E
    11_field_results.tex            -- Appendix F
    14_future_work.tex              -- Appendix G
    inference_architecture.tex      -- Appendix H
    cv_extended.tex                 -- Appendix I
    streaming_architecture.tex      -- Appendix J
    gps_estimation_deep.tex         -- Appendix K (flagship, 2200+ lines)
    testing_deep.tex                -- Appendix L
    field_day_narrative.tex         -- Appendix M
    contingency.tex                 -- Appendix N
    test_scripts_guide.tex          -- Appendix O
    calibration_deep.tex            -- Appendix P
    simulation_validation.tex       -- Appendix Q
    mission_flow.tex                -- Appendix R
    centering_analysis.tex          -- Appendix S
    comms_architecture.tex          -- Appendix T
    pipeline_fps.tex                -- Appendix U
    path_tradeoffs.tex              -- Appendix V
    payload_release.tex             -- Appendix W
    model_comparison.tex            -- Appendix X
    search_optimization.tex         -- Appendix Y
    focus_and_repulsive.tex         -- Appendix Z
    path_optimization_definitive.tex -- Appendix AA
    optimization_master.tex         -- Appendix AB
    optimization_formal.tex         -- Appendix AC
    design_strategy.tex             -- Appendix AD
    vision_performance.tex          -- Appendix AE
    decision_flow.tex               -- Appendix AF
    requirements_detail.tex         -- Appendix AG
    evaluation_detail.tex           -- Appendix AH
    development_methodology.tex     -- Appendix AI
  figs/                             -- all figures referenced by \graphicspath
```

---

## Related Documents

| File | Purpose |
|------|---------|
| `report/D6_GOLDMINE_WORKFLOW.md` | Iterative improvement workflow, checklist, cycle tracking |
| `report/GOLDMINE_CONTENT_CHECKLIST.md` | Running tracker of what GPS/CV content is written vs needed |
| `docs/PROJECT_BRIEF_COMPLETE.md` | Full extraction of project brief with rubric and requirements |
| `report/reviews/*.md` | Per-section audit files from review agents (~20 files) |
