# Appendix Quality Sweep

**Date:** 2026-04-04  
**Scope:** All 36 appendices (A through AJ) in the D6 goldmine  
**Criteria:** Purpose statement, figures/tables, subsection structure, body cross-refs, overall quality

---

## Scoring Key

| Grade | Meaning |
|-------|---------|
| A | Excellent: clear purpose, figures/tables, well-structured, cross-referenced from body |
| B | Good: solid content, minor gaps (e.g. could use one more figure, or slightly repetitive) |
| C | Adequate: functional but has notable weaknesses (wall-of-text, limited visuals, overlap with other appendices) |
| D | Weak: needs significant improvement (missing purpose, no visuals, poor structure, or heavily redundant) |

---

## Full Ranking (Weakest to Strongest)

### Tier D (Weakest -- needs significant work)

| # | App | Title | Grade | Purpose | Figs/Tables | Structure | Body Xref | Notes |
|---|-----|-------|-------|---------|-------------|-----------|-----------|-------|
| 1 | AJ | Development Methodology | D | Yes | 1 table | 2 subsections visible | From body eval section | **Heavily redundant** with App L (Testing Deep), App Q (Simulation Validation), App AC (Design Strategy), and App AE (Decision Flow). Repeats the same 3 principles (simulation-first, same code everywhere, progressive trust) found in at least 3 other appendices. The 10-phase timeline table is the only unique content. Very short for an appendix. |
| 2 | AB | Formal Multi-Objective Optimisation | D | Yes | Equations only | 2 subsections visible | From body design rationale | **Heavily overlaps** with App Z (Search Path Optimisation) and App AA (Search Parameter Optimisation). Same decision vector, same objective functions, same constraints restated in formal notation. A reader going through Z, AA, AB encounters the same energy model equation 3 times. Limited standalone value beyond the mathematical formalism. No figures. |
| 3 | O | Test Script Reference | D+ | Yes | 3+ tables | Good (8 subsections) | From App E, App L | Well-structured catalogue but is essentially a **formatted directory listing**. 74 scripts listed with one-line descriptions. No analysis, no insights, no visualisation. Reads like auto-generated documentation. Could be condensed to a single table or moved to a README. |

### Tier C (Adequate -- has notable weaknesses)

| # | App | Title | Grade | Purpose | Figs/Tables | Structure | Body Xref | Notes |
|---|-----|-------|-------|---------|-------------|-----------|-----------|-------|
| 4 | B | Configuration Parameters | C | Yes | 1 large table | Minimal (no subsections) | From body system desc | Single table with no prose analysis. No discussion of how parameters interact, how they were derived, or sensitivity. Useful as reference but lacks analytical depth. |
| 5 | AA | Search Parameter Optimisation | C+ | Yes | Tables, equations | Good subsections | From body design rationale | Strong physics simulation content but **heavily overlaps** with App Z. Same energy model, same power equation, same decision variables. The 216-config sweep and Pareto analysis are unique and valuable, but the first 40% duplicates Z. |
| 6 | U | Pipeline FPS vs Raw Inference | C+ | Yes | 1 table, 1 pgfplots figure | 4 subsections | From App H | Narrow scope (a single insight: raw FPS != effective FPS). The stacked bar chart is good. Content could be a subsection of App H rather than a standalone appendix. Short. |
| 7 | L | Progressive Testing Methodology | C+ | Yes | 5+ tables, 1 figure | 8 subsections | From App E | **Significant overlap** with App E (Testing Methodology). Both cover the 5-tier framework, both list defect discovery tables, both discuss V-model mapping. L goes deeper on defect costs and experiment scripts, but a reader who has read E will find 40-50% of L repetitive. |
| 8 | G | Future Work | C+ | Yes | 0 figures/tables | 6 subsections | From body evaluation | Well-written prose but **no visual elements at all** -- pure text. No roadmap diagram, no priority matrix, no comparison table. Each subsection is a paragraph of text. Could benefit from a priority/feasibility matrix table. |
| 9 | AC | Design Strategy | C+ | Yes | 1 table | 3+ subsections visible | From body design rationale | Opens strong with simulation-first philosophy comparison table. But **repeats the same three principles** found in AJ, and overlaps the progressive testing ladder content in E and L. The parameter derivation chain is the unique value. |

### Tier B (Good -- solid with minor gaps)

| # | App | Title | Grade | Purpose | Figs/Tables | Structure | Body Xref | Notes |
|---|-----|-------|-------|---------|-------------|-----------|-----------|-------|
| 10 | A | State Transition Table | B | Yes | 1 figure, 1 large longtable | 1 section + global overrides list | From body system desc | Good reference material. The state machine diagram figure and comprehensive table are valuable. Could benefit from a summary/analysis paragraph about state machine complexity. |
| 11 | W | Payload Release | B | Yes | 0 figures | 6 subsections | From body system desc | Good engineering analysis of release-from-altitude vs landing decision. Clearly justified. Would benefit from a diagram of the servo mechanism or a photo of the hardware. No figures is a gap. |
| 12 | T | MAVLink Communication | B | Yes | 1 ASCII diagram, 1 table | 5 subsections | From body system desc | Solid technical content. The ASCII topology diagram is functional but could be a proper figure. Good coverage of the Python 3.13 serial problem and auto-detection cascade. |
| 13 | V | Flight Path Optimisation | B | Yes | 1 table | 7 subsections | From body design rationale | Good analysis of diagonal vs axis-aligned, lane width, speed schedule, turn strategy, overlap margin. One table. Could use a figure showing the actual pattern over the polygon. |
| 14 | J | Video Streaming Architecture | B | Yes | 2 tables, code snippets | 7 subsections | From App H | Thorough protocol comparison. Good bandwidth analysis. Threading model well-explained. A diagram of the streaming architecture would help. |
| 15 | X | Model Comparison and Future CV | B | Yes | 1 table | 5 subsections | From body CV section | Good model generations table. Tiling analysis is valuable. Future improvements list is practical. Could use detection example images comparing models. |
| 16 | Y | Focus Area + Repulsive Field | B | Yes | 1 algorithm, 1 table, equations | 3 subsections | From body system desc | Good technical depth on PLB redirect logic and NFZ repulsive field math. Algorithm pseudocode is a nice touch. Sign convention explanation is important. |
| 17 | Z | Search Path Optimisation | B | Yes | Equations, tables | 6+ subsections | From body design rationale | Good formalisation of the multi-objective problem. Energy model is well-derived. Six candidate strategies compared. Overlaps with AA and AB, but is the most self-contained of the three. |
| 18 | N | Contingency Planning | B | Yes | 4 tables | 6+ subsections | From body evaluation | Excellent structure with MVD/Target/Stretch tiers. Contingency table is comprehensive. Graceful degradation hierarchy is well-presented. The tier evolution narrative adds good context. |
| 19 | AH | Requirements Verification Detail | B | Yes | 0 figures | 12 subsections (R01-R12) | From body requirements | Thorough evidence narratives for each requirement. R05 detection probability analysis is particularly strong. No figures -- would benefit from at least one verification evidence image. |
| 20 | H | Edge Inference Architecture | B+ | Yes | 2 tables, 1 figure | 8 subsections | From body system desc | Strong technical content. Backend comparison table, quantisation trade-offs, pipeline architecture, benchmark methodology all well-covered. The benchmark comparison figure adds visual appeal. |
| 21 | AE | Decision Flow | B+ | Yes | 1 figure, 1 table | 9-step narrative | From body design rationale | Engaging narrative style ("A hiker is missing"). The priority stack (safety > detection > speed > energy) is clearly stated. Decision flow figure is referenced. Good standalone readability. |
| 22 | AI | Evaluation Detail | B+ | Yes | 1 table | 3 subsections | From body evaluation | Defect register table is valuable. "What would change" section shows strong self-reflection. Lessons learned are genuinely insightful. Compact and focused. |

### Tier A (Excellent -- well-rounded)

| # | App | Title | Grade | Purpose | Figs/Tables | Structure | Body Xref | Notes |
|---|-----|-------|-------|---------|-------------|-----------|-----------|-------|
| 23 | P | Sensor Calibration | A- | Yes | 3 tables, equations, code | 8 subsections | From body, App F, App K | Comprehensive: FOV, lens distortion, colour-space, DJI FOV, error budget cross-reference, pre-flight checklist, GPS error procedure, altitude error procedure. Error budget cross-reference table (cal vs budget) is excellent. |
| 24 | F | Field Testing Results | A- | Yes | 3 tables, 1 equation | 7 subsections | From body evaluation | Quantitative results well-presented. Benchmark table, CEP statistics, DJI analysis, dry-run validation. Good discussion section linking results to remaining unknowns. |
| 25 | Q | Simulation Validation | A- | Yes | 2 tables | 6 subsections | From body testing | Strong sim-to-real gap analysis. Validation matrix table is excellent. Confidence assessment (high/moderate/low) provides clear summary. Lessons are generalisable. |
| 26 | M | Field Day Narrative | A- | Yes | 5 tables | 9 subsections | From body evaluation | Engaging narrative with quantitative rigour. FOV calibration story is compelling. "What did not work" section shows honesty. Cumulative impact table ties everything together. Team coordination section adds SE perspective. |
| 27 | S | Centering vs Direct Offset | A- | Yes | 2 tables, equations | 5 subsections + safety analysis | From body system desc | Strong probabilistic analysis with Rayleigh distribution. Simulation comparison (20 runs each). Hover safety quantitative analysis (downwash, crash probability, noise) is unusually thorough. Industry practice comparison adds credibility. |
| 28 | AD | Vision Performance Analysis | A- | Yes | 1 table, 5 plots referenced | Well-structured | From body CV section | First-principles derivation of altitude vs pixel size, motion blur, frames-on-target. Good reference table of parameters. Plots are generated from code. |
| 29 | I | CV Extended Analysis | A | Yes | 1 table, code | 6+ subsections | From body CV section | Deep technical detail on every pipeline stage. Timing breakdown table is authoritative. Multi-backend abstraction well-explained. Good justification for design choices (direct resize vs letterbox). |
| 30 | AF | Target Geolocation Approaches | A | Yes | Equations | 10 approach subsections | From body GPS section | Excellent literature survey. 10 distinct approaches with mathematical basis, pros, cons, accuracy, computational cost, and suitability assessment. Well-justified selection. |
| 31 | AG | GPS Estimation Evaluation | A | Yes | Figures referenced, metrics | 5+ subsections | From body evaluation | Bullseye visualisation, SMART estimator, convergence analysis, heading bias analysis. Rigorous evaluation methodology with 5 metrics. |
| 32 | C | Model Training and Dataset | A | Yes | 3 tables, 2 figures | 9 subsections | From body CV section | Comprehensive: strategy, domain randomisation, augmentation pipeline, synthetic generation, real labelling, negative mining, composition analysis, training pipeline, results, export, deployment, limitations. Honest limitations section is excellent. |
| 33 | D | Safety and Risk Management | A | Yes | 5 tables, 1 figure | 7 subsections | From body requirements | Risk matrix, risk register with traceability, geofence layers, failure mode table, operator-in-the-loop, emergency procedures, pre-flight checks, lessons learned, regulatory compliance. Complete safety case. |
| 34 | K | GPS Estimation Deep Dive | A | Yes | Tables, equations, code | 7 parts, 20+ subsections | From body system desc | The most comprehensive appendix. Full derivation, error budget, attitude compensation, three estimation levels, fusion strategies, multi-pass observation, DJI validation. The appendix roadmap at the start is a nice touch. |
| 35 | E | Testing Methodology | A | Yes | 5+ tables, 1 figure | 12 subsections | From body requirements/eval | Comprehensive: V-model, 5-tier framework, unit test results, dry-run, DJI video analysis, stress testing (20 scenarios), parameter tuning table, confidence buildup, industry comparison. |
| 36 | R | Mission Flow | A | Yes | Tables referenced, figures referenced | 12 subsections | From body system desc | Outstanding end-to-end narrative from power-on to landing. Every state covered with transition triggers, failure handling, and typical duration. Safety layers section ties everything together. Incremental buildup section adds development perspective. |

---

## The 5 Weakest Appendices -- Specific Improvement Suggestions

### 1. Appendix AJ (Development Methodology) -- Grade D

**Problems:**
- Repeats the same 3 principles (simulation-first, same code, progressive trust) found in App AC, App L, App Q, and the body
- The 10-phase timeline is the only unique content
- Very short compared to other appendices
- No figures or diagrams

**Improvements:**
1. **Merge into App AC (Design Strategy)** as a subsection. The 10-phase timeline table belongs there as an evidence trail for the design strategy.
2. If kept standalone, **add a Gantt chart or timeline figure** showing the 10 phases visually with milestones.
3. **Add a team workload distribution table** showing who did what in each phase -- this would be unique content not found elsewhere.
4. **Remove the repeated 3 principles** and replace with a single sentence: "The development philosophy is described in Appendix AC; this appendix focuses on the timeline and outcomes."
5. **Add a "what we would do differently" paragraph** with concrete schedule changes (currently this content is in App AI only).

### 2. Appendix AB (Formal Multi-Objective Optimisation) -- Grade D

**Problems:**
- The decision vector, objective functions, and constraints are restated from App Z and App AA
- Same energy model equation appears for the third time
- No figures at all -- pure equations and text
- Adds mathematical formalism but no new engineering insight

**Improvements:**
1. **Merge into App Z or App AA** as a "Formal Problem Statement" subsection. The formal notation adds rigour but does not justify a standalone appendix.
2. If kept standalone, **add a coupling structure visualisation** (e.g., a matrix heatmap showing which variables affect which objectives).
3. **Add a Pareto frontier figure** showing the 216 configurations plotted on 2-3 objective axes.
4. **Remove duplicated content** (energy model, decision variable definitions) and instead reference App Z/AA: "The energy model is defined in Eq. X of Appendix Z."
5. **Add a constraints feasibility analysis** -- how many of the 216 configurations violate each constraint? This would be unique analytical content.

### 3. Appendix O (Test Script Reference) -- Grade D+

**Problems:**
- Essentially a formatted directory listing of 74 scripts
- No analysis, no insights, no test coverage visualisation
- Tables list scripts with one-line descriptions -- could be auto-generated
- Very long (likely 3-4 pages) for low analytical density

**Improvements:**
1. **Add a test coverage heatmap** showing which requirements (R01-R12) are covered by which test categories.
2. **Add a "test execution order" flowchart** showing the dependency graph between flight test scripts (0a must pass before 0b, etc.).
3. **Condense the tables** -- merge hardware, calibration, and experiment tables into one. Currently 5+ tables for what is essentially a catalogue.
4. **Add statistics**: "X% of scripts are zero-command (safe to run anytime)", "Y% require hardware", "Z% produce CSV output for analysis".
5. **Add a lessons-from-testing paragraph** for each category -- what did these scripts actually catch?

### 4. Appendix B (Configuration Parameters) -- Grade C

**Problems:**
- Single table with no analytical prose
- No discussion of parameter sensitivity or interactions
- No explanation of how values were chosen (just lists them)
- No figures

**Improvements:**
1. **Add a "Parameter Derivation" column** to the table showing where each value comes from (datasheet, calibration, simulation, assumption).
2. **Add a sensitivity analysis paragraph** -- which parameters, if wrong by 10%, cause the biggest mission impact?
3. **Add a parameter interaction diagram** showing the altitude-speed-footprint-detection coupling chain.
4. **Group parameters with prose introductions** -- currently the table has group headers but no explanatory text.
5. **Add a "parameters changed during testing" mini-table** -- FOCAL_LENGTH_MM, IMAGE_W/H, DISARM_DELAY all changed. This connects to App F (Field Results) and adds narrative value.

### 5. Appendix G (Future Work) -- Grade C+

**Problems:**
- Pure text with zero visual elements (no figures, no tables, no diagrams)
- No prioritisation framework -- items listed in subsections but no ranking
- No connection to project deficiencies identified in evaluation
- Reads as a wish list rather than an engineering roadmap

**Improvements:**
1. **Add a feasibility/impact matrix table** (e.g., 2x2 grid: quick wins, strategic investments, low-priority, long-term research).
2. **Add a technology readiness level (TRL)** assessment for each item -- some items are TRL 4 (lab-validated) while others are TRL 1 (concept only).
3. **Add estimated effort** in person-hours or calendar weeks for each item.
4. **Cross-reference deficiencies** -- "D2 (single-class detector) motivates item 3 (multi-class detection)" to show the future work addresses identified weaknesses.
5. **Add a dependency diagram** showing which improvements enable which others (e.g., NCNN enables higher search speeds, which enables thermal fusion).

---

## Redundancy Clusters (Appendices with Significant Overlap)

These clusters of appendices contain substantial duplicated content and should be reviewed for consolidation:

### Cluster 1: Testing (3 appendices)
- **E** (Testing Methodology) -- comprehensive, well-structured
- **L** (Progressive Testing) -- deeper on defect costs, overlaps 40-50% with E
- **O** (Test Script Reference) -- catalogue format

**Recommendation:** Keep E as the primary. Merge L's unique content (defect cost table, experiment script details) into E. Condense O into a single summary table within E.

### Cluster 2: Search Optimisation (3 appendices)
- **Z** (Search Path Optimisation) -- 6 strategies, energy model, parametric sweep
- **AA** (Search Parameter Optimisation) -- 216-config simulation, Pareto, sensitivity
- **AB** (Formal Multi-Objective Optimisation) -- mathematical formalism

**Recommendation:** Merge AB into Z as a "Formal Problem Statement" subsection. Keep Z and AA as companion appendices but eliminate the duplicated energy model and decision variable definitions from AA (reference Z instead).

### Cluster 3: Design Philosophy (3 appendices)
- **AC** (Design Strategy) -- philosophy + parameter derivation chain
- **AE** (Decision Flow) -- narrative of search parameter selection
- **AJ** (Development Methodology) -- 10-phase timeline

**Recommendation:** Merge AJ's timeline table into AC. Keep AC and AE as separate appendices (they have different audiences: AC is engineering-focused, AE is narrative/executive-focused).

---

## Summary Statistics

| Grade | Count | Appendices |
|-------|-------|------------|
| A     | 8     | C, D, E, I, K, R, AF, AG |
| A-    | 6     | F, M, P, Q, S, AD |
| B+    | 3     | H, AE, AI |
| B     | 10    | A, J, N, T, V, W, X, Y, Z, AH |
| C+    | 5     | AA, AC, G, L, U |
| C     | 1     | B |
| D+    | 1     | O |
| D     | 2     | AB, AJ |

**Overall assessment:** The appendix suite is strong -- 27 of 36 appendices are grade B or above. The primary weakness is redundancy between testing appendices (E/L/O) and optimisation appendices (Z/AA/AB), plus a few appendices that lack visual elements (B, G, W). Addressing the 5 weakest appendices and the 3 redundancy clusters would noticeably improve the overall quality without requiring new technical content.
