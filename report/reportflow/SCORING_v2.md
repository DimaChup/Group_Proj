# Reportflow Scoring -- v2 (Post-Expansion)

**Scored:** 2026-04-03
**Document:** `report/reportflow/main.tex` (875 lines, ~22 pages)
**Scored by:** Claude against the D6 rubric
**Delta from:** v1 (81.0)

---

## What Changed Between v1 and v2

Six new sections were added to address the structural gaps identified in v1:

1. **Executive Summary** (Section 0) -- one-paragraph overview covering system, optimisation, results, testing, and evaluation
2. **STEEPLE Analysis** (Section 4) -- 7-dimension table mapping Social/Technological/Economic/Environmental/Political/Legal/Ethical to concrete design impacts
3. **MCDA: Inference Backend Trade-off** (Section 5) -- 4-option weighted MCDA table (TFLite/NCNN/Ultralytics/Hailo-8) with sensitivity check
4. **System Description** (Section 15) -- software architecture (11 modules, 4400 lines), 20-state FSM, CV pipeline (5 stages), GPS estimation, and 58-script testing infrastructure with 127 unit tests
5. **Requirements Verification** (Section 16) -- R01-R12 traceability matrix with quantitative evidence and test script references (10 met, 2 partially met)
6. **Plus/Delta Evaluation** (Section 17) -- 6 pluses (modular architecture, physics optimisation, progressive testing, model quality, layered safety, dual backend), 6 deltas (real-world validation, GPS lag, INT8, multi-pass, wind, field calibration), honest 7.7/10 sim vs 2.1/10 real assessment

---

## 1. Specialist Skills & Problem-Solving (40%)

### Score: 86/100 (was 78, +8)

**What improved:**
- **System description fills the biggest v1 gap.** The software architecture section (11 modules, strict dependency ordering, single-function CV interface) demonstrates genuine systems engineering. The architecture diagram and module descriptions show a student who understands separation of concerns, not just someone who wrote code that works.
- **Testing infrastructure is now visible.** 58 test scripts across 6 categories plus 127 unit tests is exceptional for an MSc project. The progressive flight test ladder (bench -> passive -> waypoints -> auto -> full mission) demonstrates a safety-conscious engineering methodology that many professional projects lack.
- **CV pipeline described end-to-end.** The 5-stage pipeline (capture -> undistort -> resize -> inference -> post-process) with specific timing (1.5ms undistort, 72ms NCNN, 206.5ms TFLite) gives the marker concrete evidence of technical depth.
- **GPS estimation architecture.** Inverse-variance weighting, spatial clustering, calibrated intrinsics (5.46mm focal length, 5.02mm sensor), and CEP50=2.3m field measurement -- this is a genuine technical contribution, not textbook reproduction.
- **Requirements verification with quantitative evidence.** Each requirement traces to specific test scripts, benchmark numbers, and section references. The two "partially met" entries (R07, R12) demonstrate intellectual honesty.

**Remaining weaknesses:**
- **Still no photographs.** No hardware photos, no detection example images, no field day shots. The system description mentions the Pi 5, IMX296, and Cube Orange but shows none of them. For a hardware project, this is a notable gap.
- **No code snippets or pseudocode.** The architecture is described in prose, but showing the actual `detect_in_image()` interface or a state machine transition table would strengthen the specialist skills evidence.
- **Detection envelope methodology still thin.** "Brightness-adjusted video replay" is mentioned but the methodology (how brightness was adjusted, what video was used, how many samples per condition) is not detailed enough for reproducibility.
- **No field results.** The honest assessment acknowledges 2.1/10 real-world readiness. While honesty is valued, the rubric rewards "innovative techniques and resources used effectively" -- and all resources shown are simulation/bench, not field.
- **No bibliography.** Still zero \cite commands. This is a persistent gap that limits academic credibility.

---

## 2. Decision Making (40%)

### Score: 88/100 (was 82, +6)

**What improved:**
- **STEEPLE analysis directly addresses a rubric requirement.** The 7-dimension table connects each external factor to a specific design decision (e.g., Legal -> single-class detector, Ethical -> detection weighted 40%). This is exactly what the rubric asks for under "broader context."
- **MCDA table with sensitivity analysis.** The inference backend MCDA (6 criteria, 4 options, weighted scoring) is well-structured. The sensitivity paragraph ("NCNN retains first place even if inference speed weight is halved") is above-average for MSc work -- most students present MCDA without checking robustness.
- **Requirements verification proves traceability.** The R01-R12 matrix shows that decisions were traced through to implementation and verified, not just discussed in the abstract. This closes the loop that v1 left open.
- **Plus/delta evaluation shows reflective judgement.** The 6 deltas are specific and actionable (GPS lag compensation, INT8 quantisation, wind modelling), not generic filler. The honest 7.7/10 vs 2.1/10 assessment demonstrates the kind of engineering maturity the rubric rewards under "adapting to changing circumstances."

**Remaining weaknesses:**
- **Only one MCDA table.** The goldmine body has 4 MCDA tables (companion computer, comms, detection model, search pattern). The reportflow has 1 (inference backend). Adding at least one more (e.g., companion computer selection: Pi 5 vs Jetson vs laptop) would strengthen this dimension.
- **No "Decisions That Changed" narrative.** The plus/delta acknowledges what should change in future, but does not describe decisions that were actually revised during development. The goldmine's strongest evidence is 4 design corrections made after real testing (e.g., BGR colour fix, focal length recalibration). The reportflow's session logs mention these but the report body does not.
- **STEEPLE depth is uneven.** Social, Ethical, and Environmental are well-argued. Political ("University flight permissions require demonstrated safety case") and Legal ("BVLOS operations restricted") are thin -- they state facts but don't explain what design trade-offs resulted beyond the obvious (fly within VLOS, get permission).
- **Stakeholder analysis absent.** Who needs this system? Emergency services, university assessors, CAA regulators? No discussion of stakeholder requirements or how competing stakeholder needs were balanced.
- **Autonomy level not justified.** The goldmine uses the Sheridan framework with asymmetric cost analysis. The reportflow mentions operator-in-the-loop as a "safety philosophy" in Section 14 but does not systematically justify the chosen autonomy level.

---

## 3. Communication (20%)

### Score: 88/100 (was 85, +3)

**What improved:**
- **Executive summary provides the missing entry point.** The marker now gets a one-paragraph orientation covering system, optimisation, results, testing, and evaluation. This is professional document practice.
- **Document now reads as a D6 report, not just a technical paper.** The addition of system description, requirements, and evaluation sections transforms the document from "deep-dive on one topic" to "structured coursework submission." The flow is: executive summary -> objective -> constraints -> context (STEEPLE) -> trade-off (MCDA) -> optimisation -> system -> requirements -> evaluation -> conclusion.
- **More content with maintained quality.** The document grew from ~688 to ~875 lines without losing the tight prose style, clean LaTeX formatting, or logical flow. The new sections integrate naturally.
- **Requirements table is a strong visual element.** The checkmark/tilde/cross notation with test script references is immediately parseable.

**Remaining weaknesses:**
- **Still zero bibliography/references.** This remains the single biggest communication gap. An 875-line academic report with no citations is a red flag. At minimum: YOLOv8 (Ultralytics), ArduPilot, momentum theory (Leishman or Johnson), coverage planning (Galceran & Carreras 2013), SORA framework, UK CAA regulations, FSRS or spaced repetition if used. The goldmine has ~25 unique citations.
- **Still no photographs.** Hardware, field day, detection examples -- all absent. For a physical drone project, this significantly weakens the "communication of technical work" dimension.
- **Architecture diagram not verified.** The document references `\includegraphics{architecture}` but it's unclear if this file exists in `../figs/`. If any figures fail to compile, the communication score drops sharply.
- **No appendices.** Raw sweep data, model training curves, benchmark tables -- these belong in appendices and would add weight without bloating the main text.
- **Section numbering may confuse.** The executive summary is unnumbered (`\section*`), which is correct, but the STEEPLE and MCDA sections appear before the original optimisation content, changing the numbering of all subsequent sections from v1. This is fine structurally but may require careful cross-referencing if the document is merged with the goldmine.

---

## 4. Overall Weighted Score

| Criterion | Weight | v1 Score | v2 Score | Weighted (v2) |
|-----------|--------|----------|----------|----------------|
| Specialist Skills & Problem-Solving | 40% | 78 | 86 | 34.4 |
| Decision Making | 40% | 82 | 88 | 35.2 |
| Communication | 20% | 85 | 88 | 17.6 |
| **TOTAL** | | **81.0** | | **87.2** |

**Delta from v1: +6.2 marks**

**Band: Strong First (85-90 range) -- now in the top band**

---

## 5. What Improved Most (ranked by impact)

| Improvement | Criterion | Estimated Impact |
|-------------|-----------|-----------------|
| System description (architecture, FSM, CV, GPS, testing) | Specialist Skills | +5 |
| Requirements verification matrix (R01-R12) | Both SS and DM | +4 |
| Plus/delta evaluation with honest assessment | Decision Making | +3 |
| STEEPLE analysis | Decision Making | +3 |
| MCDA inference backend table | Decision Making | +2 |
| Executive summary | Communication | +2 |

---

## 6. Remaining Gaps (what would push toward 90+)

### 1. Add a bibliography with citations (CRITICAL -- easiest high-impact fix)
Zero references in 875 lines. This is the single largest remaining gap. Adding 15-20 citations would take 30 minutes and add 2-4 marks on Communication plus indirect credibility gains on Specialist Skills.
**Impact: +2-4 marks**

### 2. Add hardware photographs and detection example images (HIGH)
One photo of the Pi+camera+Cube assembly, one detection overlay screenshot from passive_watch, one field day photo. Three images, massive credibility gain.
**Impact: +2-3 marks on Communication and Specialist Skills**

### 3. Add a second MCDA table (MEDIUM)
Companion computer selection (Pi 5 vs Jetson Nano vs laptop tethered) or search pattern MCDA (lawnmower vs spiral vs expanding square with weighted criteria). Section 8 already evaluates 4 patterns in prose -- restructuring as an MCDA table would cost 10 minutes.
**Impact: +1-2 marks on Decision Making**

### 4. Add "Decisions That Changed" narrative (MEDIUM)
The project has 4 clear corrections: BGR colour fix, focal length recalibration (7.0 -> 5.46mm), TFLite bbox coord bug, calibration_data.npz corruption. Each was discovered through testing and changed a design parameter. This is the rubric's "adapting to changing/unfamiliar/challenging circumstances."
**Impact: +1-2 marks on Decision Making**

### 5. Deepen STEEPLE analysis (LOW-MEDIUM)
Political and Legal entries are thin. Adding: UK drone code (Drone and Model Aircraft Code), EASA Open Category limits, university risk assessment process, insurance requirements. Two sentences per dimension would suffice.
**Impact: +1 mark on Decision Making**

### 6. Add appendices (LOW)
Raw sweep data CSV, model training loss curves, benchmark comparison table. These add academic weight without bloating the main text.
**Impact: +0.5-1 mark on Communication**

---

## 7. Comparison to v1 Gap Table (closure status)

| Gap identified in v1 | Addressed in v2? | Quality |
|----------------------|-------------------|---------|
| Executive summary | YES | Good -- concise, covers all key points |
| STEEPLE analysis | YES | Good -- 7 dimensions with design impacts, some entries thin |
| MCDA trade-off tables | PARTIAL -- 1 of 4 recommended | Good quality but only one table |
| System architecture description | YES | Strong -- modules, FSM, CV pipeline, GPS, testing |
| Requirements verification (R01-R12) | YES | Strong -- quantitative evidence, test script references |
| Plus/delta evaluation | YES | Strong -- specific, honest, actionable |
| "Decisions That Changed" narrative | NO | Still missing |
| Bibliography / citations | NO | Still zero references -- critical gap |
| Hardware photographs | NO | Still no photos |
| Autonomy level (Sheridan framework) | NO | Operator-in-the-loop mentioned but not systematically justified |

**Closure rate: 6/10 gaps addressed, 4 remain**

---

## 8. Scoring History

| Version | Date | Specialist (40%) | Decision (40%) | Communication (20%) | Total |
|---------|------|-------------------|----------------|----------------------|-------|
| v1 | 2026-04-03 | 78 | 82 | 85 | **81.0** |
| v2 | 2026-04-03 | 86 | 88 | 88 | **87.2** |
