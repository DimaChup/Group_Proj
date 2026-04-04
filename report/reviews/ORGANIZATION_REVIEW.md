# Organization Review — Goldmine Report (main.tex)

Reviewed: 2026-04-03 | Scope: overall structure, narrative flow, appendix grouping, redundancy, TOC readability, appendix guide accuracy.

---

## 1. Body Narrative Flow

The 15-page counted body follows a clean **why-what-prove-assess** arc:

| Section | Role | Pages (approx) |
|---------|------|-----------------|
| 1. Design Rationale | WHY we chose things | ~4 pp |
| 2. System Description | WHAT we built | ~5 pp |
| 3. Requirements Verification | Does it MEET the brief? | ~3 pp |
| 4. Evaluation | Honest ASSESSMENT | ~3 pp |

**Verdict: GOOD.** The logical flow is sound and matches the D6 marking rubric expectations. A first-time reader moves from justification through architecture to evidence to reflection. Two minor notes:

- Section 1.12 ("Camera Selection: Global vs Rolling Shutter") and 1.13 ("Field Day Adaptation") feel like they belong in Section 2 (System Description) or could be folded into the trade studies earlier in Section 1. They break the "why" narrative with "what happened" content. Not a deal-breaker, but slightly jarring.
- Section 1.2 ("Search Parameter Optimisation") is dense and highly technical for its position as the second subsection. A reader who just finished the STEEPLE table may find the jump to parametric sweeps abrupt. A one-sentence bridging paragraph at the end of 1.1 already exists and helps, but consider whether the detail level is right for the body vs. pointing to the appendix sooner.

**Pre-body sections** (Exec Summary, Introduction) are well-structured and excluded from the page count. The Introduction sets context, describes the company, and lists team members/roles -- all expected for D6.

---

## 2. Appendix Grouping Analysis

The appendix guide table groups appendices into four themes:

1. **Core system detail** (A-D): state table, config, training, safety
2. **Verification and validation** (E-G): testing, field results, future work
3. **Subsystem deep dives** (H-U): 14 appendices covering inference, CV, GPS, streaming, testing, field day, contingency, calibration, simulation, mission flow, comms, centering, pipeline FPS
4. **Search and flight optimisation** (V-AF): 11 appendices covering path optimization, payload, model comparison, search optimization, focus area, formal optimization, design strategy, vision performance, decision flow
5. **Extended body sections** (AG-AI): requirements detail, evaluation detail, development methodology

### Problems with current grouping:

**A. The "Subsystem deep dives" bucket (H-U) is a catch-all.** It contains 14 appendices spanning wildly different topics: CV inference (H), GPS estimation (K), testing philosophy (L), field day narrative (M), contingency planning (N), test script reference (O), sensor calibration (P), simulation validation (Q), mission flow (R), centering analysis (S), comms architecture (T), and pipeline FPS (U). A reader looking for "all CV stuff" has to jump between H, I, U, and also X and AE. A reader looking for "all testing stuff" has to visit E, L, M, O, and parts of F and Q.

**B. CV-related appendices are scattered across three groups:**
- H: Edge Inference Architecture (deep dives)
- I: CV Extended Analysis (deep dives)
- U: Pipeline FPS (deep dives)
- X: Model Comparison (search and flight)
- AE: Vision Performance Analysis (search and flight)
- C: Model Training (core system)

These six appendices all concern the vision/detection subsystem but are separated by 20+ other appendices. A reader interested in the CV story has to jump back and forth extensively.

**C. Testing-related appendices are similarly scattered:**
- E: Testing Methodology (verification)
- F: Field Testing Results (verification)
- L: Progressive Testing Deep Dive (deep dives)
- M: Field Day Narrative (deep dives)
- O: Test Script Reference (deep dives)

**D. Optimization appendices are over-fragmented (6 appendices on the same topic):**
- V: Flight Path Optimisation (trade-offs overview)
- Y: Multi-Objective Search Optimisation (SUPERSEDED, retained)
- AA: Search Path Optimisation (definitive 216-config sweep)
- AB: Search Parameter Optimisation (physics sim, Pareto, sensitivity)
- AC: Formal Multi-Objective Optimisation (mathematical formulation)
- AD: Design Strategy (parameter derivation chain)
- AF: Decision Flow (executive narrative)

That is SEVEN appendices covering search parameter optimization from different angles. While each has a distinct lens, the sheer number is likely to confuse rather than impress an examiner.

---

## 3. Redundancy Analysis

### HIGH redundancy (same topic, different depth/angle):

| Cluster | Appendices | Overlap |
|---------|-----------|---------|
| **Search optimization** | Y (superseded), AA, AB, AC, AD, AF, V | Y is explicitly superseded by AA. AB shares energy model and 216-config data with AA. AC formalizes what AB already presents numerically. AF is a narrative wrapper around AD. V overlaps with AA on strategy comparison. |
| **CV pipeline** | H, I, U, AE | H covers inference backend selection. I covers pipeline timing + benchmarks. U covers effective vs raw FPS (a subset of I's pipeline timing). AE covers altitude/speed/pixel analysis (could be a subsection of I). |
| **Testing** | E, L | E describes the five-tier framework. L provides a "deep dive" on the same five-tier framework. Much of L's philosophy and tier definitions re-state E. |
| **Field results** | F, M | F presents calibration data and benchmarks from the field day. M narrates the same field day. They cover the same event from data vs. narrative perspectives. |

### MODERATE redundancy:

| Pair | Overlap |
|------|---------|
| D (Safety) and N (Contingency) | Both cover failure scenarios and mitigations. D has the FMEA table; N has the eight failure scenarios with fallback scripts. Some failure modes appear in both. |
| R (Mission Flow) and A (State Table) | R narrates the mission; A tabulates the same transitions. Some state descriptions are duplicated. |
| AG (Requirements Detail) and Section 3 body | By design -- AG expands what Section 3 summarizes. This is fine. |
| AH (Evaluation Detail) and Section 4 body | Same pattern as above. Fine. |

### Recommendation (do NOT delete anything):

Reorder appendices into thematic clusters and add cross-reference notes so a reader knows which appendix is the "primary" and which are "supplementary perspectives." The superseded Appendix Y should either be clearly labeled in the guide table as "(superseded, retained for supplementary detail)" or moved to the very end.

---

## 4. TOC Readability for a First-Time Reader

### Strengths:
- The four body sections have clear, descriptive titles
- Appendix letters are easy to reference
- The Appendix Guide table on its own page is excellent -- it gives the reader a map before diving in

### Weaknesses:

**A. 35 entries in the appendix TOC is overwhelming.** A first-time reader sees the TOC go from a tidy 4-section body to a wall of 35 appendices (A through AI). The sheer count may signal "disorganized dump" rather than "well-structured supplementary material." The guide table partially mitigates this, but the TOC itself still looks intimidating.

**B. Appendix titles in the TOC do not always signal their relationship to each other.** For example:
- "Search Path Optimisation" (AA) vs "Search Parameter Optimisation" (AB) vs "Multi-Objective Search Optimisation" (Y/AC) -- a reader cannot tell these apart from titles alone.
- "Testing Methodology" (E) vs "Progressive Testing Methodology" (L) -- why are there two?
- "Field Testing and Results" (F) vs "Field Day: Adaptation Under Uncertainty" (M) -- same event?

**C. The appendix guide table groups are not reflected in the TOC.** The TOC just lists A, B, C, ... AI with no visual separation. The four thematic groups from the guide table should ideally appear as TOC dividers (e.g., a bold unumbered line "--- Core System Detail ---" before A). This can be done with `\addcontentsline{toc}{subsection}{\textit{Core System Detail}}` or similar.

**D. Paragraph-level entries in the TOC add noise.** The TOC includes paragraph-level entries like "Mission objective.", "System overview.", "Focal length: 7.0mm -> 5.46mm." These clutter the TOC without helping navigation. Consider using `\paragraph*` (starred, no TOC entry) or adjusting `\setcounter{tocdepth}{3}` to exclude paragraph level.

---

## 5. Appendix Guide Table Accuracy

Reviewing each entry against the actual file content:

| App | Guide Description | Actual Content | Accurate? |
|-----|-------------------|----------------|-----------|
| A | State transition table -- 20 states, 32 transitions | Matches | Yes |
| B | Configuration parameters | Matches | Yes |
| C | Model training and dataset | Matches | Yes |
| D | Safety and risk management | Matches | Yes |
| E | Testing methodology -- five-tier framework, 20 failure scenarios | File says "20 failure scenarios" but also mentions 74 test scripts, 127 unit tests. Guide says "20 failure scenarios, pass criteria" -- slightly understates scope. | Minor |
| F | Field testing and results -- calibration data, benchmarks, detection rates | Matches | Yes |
| G | Future work | Matches | Yes |
| H | Edge inference -- NCNN vs TFLite, Pi 5 | Matches | Yes |
| I | CV extended analysis -- pipeline, altitude, dual backend | Matches | Yes |
| J | Video streaming and ground station | Matches | Yes |
| K | GPS target estimation -- Kalman, clustering, error budget | Matches | Yes |
| L | Progressive testing methodology -- philosophy, integration strategy | Matches (but overlaps heavily with E) | Yes |
| M | Field day -- bench calibration pivot, concrete outputs | Matches | Yes |
| N | Contingency -- three-tier fallback, eight scenarios | Matches | Yes |
| O | Test script reference -- all 58 scripts | File content says 58 scripts. Exec summary says 58. Appendix E says 74 scripts + 127 unit tests. **Inconsistency: is it 58 or 74?** | CHECK |
| P | Sensor calibration -- FOV, lens, GPS, error budget | Matches | Yes |
| Q | Simulation validation -- sim-to-real gap, transfer confidence | Matches | Yes |
| R | Mission flow -- power-on to RTL | Matches | Yes |
| S | Centering vs direct offset landing | Matches | Yes |
| T | MAVLink communication architecture | Matches | Yes |
| U | Raw inference vs effective pipeline throughput | Matches | Yes |
| V | Flight path optimisation -- strategy comparison | Matches | Yes |
| W | Payload release mechanism | Matches | Yes |
| X | Model comparison and future vision | Matches | Yes |
| Y | Multi-objective search optimisation | **File header says "SUPERSEDED by path_optimization_definitive.tex"** -- guide table does not mention this. Reader may not know Y is largely replaced by AA. | ISSUE |
| Z | Focus area redirect and repulsive field | Matches | Yes |
| AA | Search path optimisation -- six strategies, energy, sweep | Matches (this is the definitive version that supersedes Y) | Yes |
| AB | Search parameter optimisation -- 216-config sim, Pareto, sensitivity | Matches | Yes |
| AC | Formal multi-objective optimisation -- math problem statement | Matches | Yes |
| AD | Design strategy -- parameter derivation chain | Matches | Yes |
| AE | Vision performance analysis -- altitude vs pixel, motion blur, detection envelope | Matches | Yes |
| AF | Decision flow -- executive narrative of parameter selection | Matches | Yes |
| AG | Requirements verification detail -- R01-R12 evidence | Matches | Yes |
| AH | Evaluation detail -- defect register, lessons, second iteration | Matches | Yes |
| AI | Development methodology -- sim-first, 10-phase timeline, lessons | Matches | Yes |

**Guide table verdict: Mostly accurate.** Two issues to fix:
1. Appendix Y should be noted as "(superseded by AA; retained for supplementary detail)"
2. Test script count inconsistency (58 in guide vs 74 in Appendix E) needs reconciliation

---

## 6. Suggested Reorganization

Below is a suggested reordering that groups appendices by theme. This is a **recommendation only** -- no files need to be renamed, only the `\input` order in `main.tex` and the guide table need updating.

### Proposed thematic order:

**Group 1: Core System Architecture (how it works)**
- A: State Transition Table
- B: Configuration Parameters
- R: Mission Flow (end-to-end narrative)
- T: MAVLink Communication Architecture

**Group 2: Computer Vision (detection subsystem)**
- C: Model Training and Dataset
- H: Edge Inference Architecture (NCNN vs TFLite)
- I: CV Extended Analysis (pipeline, timing, benchmarks)
- U: Pipeline FPS vs Raw Inference
- X: Model Comparison and Future Vision
- AE: Vision Performance Analysis (altitude, blur, detection envelope)

**Group 3: Search and Flight Optimization**
- V: Flight Path Optimisation (strategy overview)
- AA: Search Path Optimisation (definitive 216-config sweep) -- PRIMARY
- AB: Search Parameter Optimisation (physics sim, Pareto) -- SUPPORTING
- AC: Formal Multi-Objective Optimisation (math formulation) -- REFERENCE
- AD: Design Strategy (derivation chain)
- AF: Decision Flow (executive narrative)
- Y: Multi-Objective Search Optimisation (SUPERSEDED, supplementary only)

**Group 4: GPS, Calibration, and Localisation**
- K: GPS Target Estimation Deep Dive
- P: Sensor Calibration (FOV, lens, GPS ground truth)
- S: Centering vs Direct Offset Landing

**Group 5: Safety and Operations**
- D: Safety and Risk Management
- N: Contingency Planning and Deliverable Tiers
- W: Payload Release Mechanism
- Z: Focus Area Redirect and Repulsive Field

**Group 6: Testing and Verification**
- E: Testing Methodology (five-tier framework)
- L: Progressive Testing Deep Dive
- O: Test Script Reference
- F: Field Testing Results
- M: Field Day Narrative
- Q: Simulation Validation

**Group 7: Ground Station and Streaming**
- J: Video Streaming and Ground Station

**Group 8: Extended Body Sections**
- AG: Requirements Verification Detail
- AH: Evaluation Detail

**Group 9: Development Process**
- AI: Development Methodology
- G: Future Work

This reorganization:
- Puts all CV appendices together (C, H, I, U, X, AE)
- Puts all testing appendices together (E, L, O, F, M, Q)
- Puts all optimization appendices together (V, AA, AB, AC, AD, AF, Y) with clear primary/supporting labels
- Separates GPS/calibration as its own cluster
- Moves Future Work to the end (natural closing position)

---

## 7. Quick Wins (minimal effort, high impact)

1. **Add group dividers to the TOC.** Insert `\addtocontents{toc}{\bigskip\noindent\textbf{\textit{Core System Architecture}}\par}` before each group's first appendix. This breaks up the wall of 35 entries.

2. **Mark Appendix Y as superseded in the guide table.** Change "Multi-objective search optimisation" to "Multi-objective search optimisation (superseded by AA; retained for supplementary context)."

3. **Reduce TOC depth for pre-body sections.** Use `\paragraph*` instead of `\paragraph` in the Executive Summary to avoid "Mission objective.", "System overview." etc. appearing in the TOC.

4. **Reconcile test script counts.** The guide table says 58 scripts (Appendix O), but Appendix E says 74 scripts + 127 unit tests. Decide on one authoritative count and use it everywhere.

5. **Consider merging U into I.** Appendix U (Pipeline FPS) is essentially one subsection's worth of content that extends Appendix I (CV Extended Analysis). Merging would reduce the appendix count by one and keep all pipeline analysis in one place.

6. **Consider merging M into F.** The field day narrative (M) and field testing results (F) cover the same event. M provides context; F provides data. Together they tell a complete story. Merging would reduce count by one.

---

## 8. Summary Verdict

| Criterion | Rating | Notes |
|-----------|--------|-------|
| Body narrative flow | **Strong** | Clean why-what-prove-assess arc. Minor sequencing issues in 1.12-1.13. |
| Appendix thematic grouping | **Needs work** | Current groups are too broad ("Subsystem deep dives" = 14 items). CV and testing content scattered. |
| Redundancy | **Moderate concern** | 7 optimization appendices, 2 testing philosophy appendices, 1 explicitly superseded appendix still in sequence. No deletions needed, but labeling and ordering would help. |
| TOC readability | **Adequate** | Guide table helps, but raw TOC is a wall of 35 entries with no visual breaks. Paragraph-level entries add noise. |
| Guide table accuracy | **Good** | 33/35 entries accurate. Two issues: Y not marked as superseded, test script count inconsistency. |
| Overall | **Solid content, needs organizational polish** | The material is comprehensive and well-written. The main improvement is grouping related appendices together and adding visual structure to the TOC. |
