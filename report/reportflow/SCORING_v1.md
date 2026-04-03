# Reportflow Scoring -- v1 Baseline

**Scored:** 2026-04-03
**Document:** `report/reportflow/main.tex` (688 lines, ~17 pages)
**Scored by:** Claude against the D6 rubric (same criteria as goldmine body)

---

## What This Document Is

The reportflow is titled "SAR Drone Search Parameter Optimisation -- Decision Flow." It is a standalone document covering the **search parameter selection process**: how altitude, speed, pattern type, heading mode, scan angle, NFZ margins, and overlap were chosen through a sequential 9-step decision chain backed by a 216-configuration energy sweep.

**Critical observation:** This is NOT a D6 group report. It covers only one slice of the project -- the search parameter optimisation. It does not contain an executive summary, system description, requirements verification, STEEPLE analysis, MCDA trade studies, state machine description, CV pipeline description, GPS estimation, ground station, testing strategy, or evaluation (plus/delta). It is a deep-dive technical paper on one topic, not a condensed version of the D6 body.

---

## 1. Specialist Skills & Problem-Solving (40%)

### Score: 78/100

**Strengths:**
- Exceptional mathematical rigour: 15+ numbered equations covering safety scoring, detection probability, energy modelling (momentum theory + parasitic drag), coverage computation, and composite scoring
- 216-configuration parametric sweep demonstrates genuine systems engineering -- not ad-hoc selection
- Physics-based energy model (hover power from momentum theory, forward-flight with quadratic drag, turn energy) is above MSc coursework standard
- Sensitivity analysis (tornado chart) quantifies parameter importance -- altitude has 2x the score impact of speed
- Pareto frontier analysis with parallel coordinates shows multi-objective optimisation awareness
- Detection envelope characterised across 3 lighting conditions with 15% safety margins -- systematic, not guesswork
- Real metrics used throughout: mAP50=0.995, 4.8 FPS TFLite, 9 FPS NCNN, CEP50=2.3m, 206.5ms inference
- NFZ margin derived from RSS of 4 error sources (footprint diagonal, GPS, reaction, wind) -- rigorous

**Weaknesses:**
- **Narrow scope**: Only covers search parameter selection. No state machine, no CV pipeline description, no GPS estimation architecture, no testing strategy, no ground station, no hardware description
- **No field results**: Everything is simulation/modelling. No bench test photos, no field day results, no real detection images
- **No code architecture**: The 4400-line codebase with 11 modules is never mentioned
- **No progressive testing methodology**: The 58 test scripts across 6 categories -- the strongest evidence of engineering maturity -- are absent
- **Some numbers feel circular**: The detection envelope (Table 2) appears to be derived from brightness-adjusted video replay, but methodology is not explained in enough detail to verify
- **No comparison to prior work**: No literature on SAR drone search optimisation, coverage planning algorithms (Choset, Galceran), or operational SAR procedures

### Evidence quality: HIGH for what's covered, but coverage is too narrow for a D6 report

---

## 2. Decision Making (40%)

### Score: 82/100

**Strengths:**
- **This is the document's strongest dimension.** The entire paper is a decision-making chain
- 9-step sequential decision chain with explicit "why this comes now" justification at each step -- exactly what the rubric asks for
- Clear priority stack (safety > detection > time > energy > coverage) stated upfront and maintained throughout
- Constraint-vs-objective split is well-argued: safety and time are pass/fail gates, detection/coverage/energy are continuously optimised -- this shows genuine engineering judgement
- Every decision traces to a physical measurement or calculation, not gut feel
- Alternatives genuinely evaluated: 4 search patterns, yaw vs fixed heading, spiral vs lawnmower
- "Because" chain summary (Section 10) is an excellent communication device -- every parameter justified in one sentence
- Non-quantifiable choices (Section 13) honestly acknowledges what the model cannot capture
- Composite score weights (40/35/25) are justified rather than assumed
- The constraint that detection=0 in any sub-component should collapse the whole score (multiplicative vs additive) shows deep understanding of the problem

**Weaknesses:**
- **No STEEPLE analysis**: The rubric explicitly requires coverage of Social, Technological, Economic, Environmental, Political, Legal, Ethical dimensions. Not present.
- **No MCDA trade-off tables**: The goldmine has 4 MCDA tables (companion computer, comms, detection model, search pattern). The reportflow has none. The 216-config sweep is a form of trade study, but it is not structured as a weighted MCDA.
- **No "Decisions That Changed" narrative**: The goldmine's strongest decision-making evidence is the 4 design corrections made after real testing. The reportflow has no equivalent.
- **No stakeholder analysis**: Who needs this system? What are their requirements? No discussion.
- **Sensitivity analysis on composite weights is missing**: If the weights were 50/30/20 instead of 40/35/25, would the winner change? Not addressed.
- **No autonomy level justification**: The goldmine uses the Sheridan framework with asymmetric cost analysis -- absent here.

---

## 3. Communication (20%)

### Score: 85/100

**Strengths:**
- **Professional formatting**: Clean LaTeX with coloured section headings, compact tables, consistent style
- **10 real figures** (not placeholders): spider charts, heatmap, tornado chart, Pareto parallel coordinates, top-3 path overlay, lighting conditions, decision flow infographic, sensitivity matrix, scoring overview, safety/detection sub-score decomposition
- **9 tables**: decision variables, detection envelope, speed envelope, top-3 configurations, final configuration, plus inline calculation tables
- **15+ numbered equations**: More mathematical content than the entire goldmine body
- **Logical flow**: The document reads as a narrative -- objective, constraints, dimensions, scoring, variables, coupling, chain, sweep, result, sensitivity, Pareto. Each section sets up the next.
- **tcolorbox for decision chain summary** is a nice visual element
- **Self-contained**: No forward references to content that does not appear in the document

**Weaknesses:**
- **No photographs**: No hardware, no field day, no detection examples, no ground station screenshot
- **No bibliography/references**: Zero citations. No \cite commands. An academic report without references is a significant omission.
- **No executive summary**: The document dives straight into the objective
- **Title is "Decision Flow" rather than a D6 group report**: Does not position itself as a coursework submission
- **No appendices**: Supporting data (raw sweep results, model training details) not included
- **Some figures may not compile**: The document references `../figs/` but it is unclear whether all 10 figure files exist in the correct location for this standalone build

---

## 4. Overall Weighted Score

| Criterion | Weight | Score | Weighted |
|-----------|--------|-------|----------|
| Specialist Skills & Problem-Solving | 40% | 78 | 31.2 |
| Decision Making | 40% | 82 | 32.8 |
| Communication | 20% | 85 | 17.0 |
| **TOTAL** | | | **81.0** |

**Band: First (72-82 range) -- not yet in the 83+ top band**

---

## 5. Comparison to Goldmine Body (what's missing?)

The goldmine body (scored 80.4 in v4 review) covers the full D6 structure. The reportflow covers only search optimisation. Here is what the reportflow is missing relative to the goldmine:

| Goldmine Content | Present in Reportflow? | Impact |
|-----------------|----------------------|--------|
| Executive summary | NO | HIGH -- markers read this first |
| STEEPLE analysis (7 dimensions) | NO | HIGH -- rubric explicitly requires it |
| 4 MCDA trade-off tables | NO | HIGH -- core Decision Making evidence |
| System architecture description | NO | HIGH -- what does the system actually look like? |
| CV pipeline (camera -> model -> detection) | Mentioned briefly | MEDIUM -- only referenced, not described |
| State machine (20 states, 32 transitions) | NO | HIGH -- the mission logic is absent |
| GPS estimation (Kalman, inverse-variance) | NO | MEDIUM -- key technical contribution |
| Ground station / operator interface | NO | MEDIUM -- proves the system is usable |
| Hardware platform (Pi 5, IMX296, Cube) | Mentioned briefly | MEDIUM -- no BOM, no photos |
| Requirements verification (R01-R12) | NO | HIGH -- rubric requires traceability |
| Plus/delta evaluation | NO | HIGH -- rubric requires honest assessment |
| "Decisions That Changed" (4 corrections) | NO | HIGH -- strongest adaptation evidence |
| Testing strategy (58 scripts, 6 categories) | NO | MEDIUM -- proves engineering rigour |
| Field day results | NO | MEDIUM -- demonstrates real-world attempt |
| Bibliography / citations | NO (zero references) | HIGH -- academic credibility |
| Autonomy level (Sheridan framework) | NO | MEDIUM -- sophisticated decision-making |

**Summary:** The reportflow is a deep, rigorous treatment of ONE topic (search parameter optimisation) but is missing approximately 70% of the content required for a D6 group report. It would score very high as a technical appendix or standalone optimisation paper, but it cannot stand alone as a D6 submission.

---

## 6. Top 5 Improvements (to push toward 83+)

### 1. Add the missing D6 structure sections (CRITICAL)
The reportflow needs at minimum: executive summary, system description (architecture + CV + state machine + GPS), requirements verification table, and plus/delta evaluation. Without these, it is not a D6 report regardless of how good the optimisation content is.
**Impact: +10-15 marks (structural completeness)**

### 2. Add STEEPLE analysis and MCDA tables (HIGH)
These are explicitly mentioned in the rubric under Decision Making. The 216-config sweep is impressive but does not replace the need for broader design rationale covering component selection, ethical considerations, and regulatory compliance.
**Impact: +5-8 marks on Decision Making**

### 3. Add a bibliography with citations (HIGH)
Zero references in 17 pages is a red flag in any academic report. At minimum cite: YOLOv8 (Ultralytics), ArduPilot, Choset/Galceran (coverage planning), momentum theory textbook, UK CAA regulations, SORA framework. The goldmine has 118 bib entries with ~25 unique body citations.
**Impact: +3-5 marks on Communication**

### 4. Add hardware photos and detection example images (MEDIUM)
The rubric says "images recommended" under system description and "innovative techniques and resources" under communication. Currently the reportflow has excellent generated charts but zero photographs of the actual system.
**Impact: +2-4 marks on Communication and Specialist Skills**

### 5. Add "Decisions That Changed" and field day narrative (MEDIUM)
The rubric rewards "adapting to changing/unfamiliar/challenging circumstances." The goldmine's weather cancellation pivot and 4 design corrections are its strongest adaptation evidence. The reportflow has none of this narrative.
**Impact: +3-5 marks on Decision Making**

---

## 7. What the Reportflow Does BETTER Than the Goldmine

Despite the structural gaps, the reportflow excels in areas where the goldmine is weaker:

| Area | Reportflow | Goldmine |
|------|-----------|----------|
| Mathematical depth | 15+ equations, physics-based models | 1 equation (Rayleigh) |
| Parametric optimisation | 216-config sweep with composite scoring | No parametric sweep |
| Sensitivity analysis | Tornado chart + spider chart + Pareto | No sensitivity analysis |
| Energy modelling | Momentum theory + parasitic drag | No energy model |
| Multi-objective visualisation | Parallel coordinates, heatmap, spider | Basic bar/scatter plots |
| Decision chain explicitness | 9-step "because" chain | Implicit decision logic |
| NFZ margin derivation | RSS of 4 error sources | NFZ mentioned but not derived |

**Recommendation:** The optimal D6 submission would integrate the reportflow's optimisation depth INTO the goldmine's D6 structure -- not replace it. The reportflow content belongs in the Design Rationale and/or a dedicated appendix, with the rest of the D6 sections providing the context it currently lacks.

---

## 8. Scoring History

| Version | Date | Specialist (40%) | Decision (40%) | Communication (20%) | Total |
|---------|------|-------------------|----------------|----------------------|-------|
| v1 | 2026-04-03 | 78 | 82 | 85 | **81.0** |
