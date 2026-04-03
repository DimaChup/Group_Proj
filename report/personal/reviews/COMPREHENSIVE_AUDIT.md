# D7 Individual Reflective Report -- COMPREHENSIVE AUDIT

> Audited: 2026-04-03. Current estimated score: 83-84/100 (v5).
> THIS IS THE ONLY GRADED REPORT. 50% of unit mark. Every sentence must earn its place.

---

## CRITICAL ISSUE: PAGE COUNT VIOLATION

**The report compiles to 8 pages. The limit is 5 pages (excluding cover + appendices).**

Page breakdown (from compilation output):
- Page 1: Title block + Introduction + Section 2 (Design) starts
- Page 2: Section 2 continues + Section 3 (Societal/Environmental) starts
- Page 3: Section 3 ends + Section 4 (Teamwork) starts
- Page 4: Section 4 continues
- Page 5: Section 4 ends + Section 5 (Self-Development) starts
- Page 6: Section 5 continues
- Page 7: Section 5 ends
- Page 8: References (bibliography)

**The body content alone is ~7 pages. We need to cut ~2 full pages (roughly 40% of the content).** References on page 8 are likely excluded from the 5-page count, but the body content on pages 1-7 is 3 pages over budget. This is a FAIL condition -- markers may stop reading at page 5 or penalise heavily.

---

## 1. Word Count Per Section

| Section | File | Words (raw .tex) | Est. Rendered Pages | Budget (from TARGET_BRIEF) | Verdict |
|---------|------|-------------------|--------------------|----|---------|
| 01 Introduction | 01_introduction.tex | 66 | ~0.3 | 0.5 | OK -- concise |
| 02 Design & Problem-Solving (M5) | 02_design_problem_solving.tex | 590 | ~1.8 | 1.0 | **80% OVER BUDGET** |
| 03 Societal & Environmental (M7) | 03_societal_environmental.tex | 609 | ~1.8 | 0.5 | **260% OVER BUDGET** |
| 04 Teamwork & Leadership (M16/M17) | 04_teamwork_leadership.tex | 881 | ~2.5 | 1.5 (M16+M17 combined) | **67% OVER BUDGET** |
| 05 Self-Development | 05_self_development.tex | 1,146 | ~3.2 | 1.5 | **113% OVER BUDGET** |
| **Total** | | **3,292** | **~7 pages** | **5 pages** | **2 PAGES OVER** |

**Target word count for 5 pages**: ~2,000-2,200 words (at 11pt, 20mm margins, 1.15 spacing).
**Current word count**: ~3,292 words. Need to cut ~1,000-1,200 words.

### Optimal Reallocation

| Section | Current Words | Target Words | Action |
|---------|--------------|-------------|--------|
| 01 Introduction | 66 | 60-80 | Keep as-is |
| 02 Design (M5) | 590 | 400-450 | Cut ~150 words. Diversity subsection is bloated. |
| 03 Impact (M7) | 609 | 350-400 | Cut ~250 words. Quantified env impact is too detailed. Dual-use is strong but long. |
| 04 Teamwork (M16/M17) | 881 | 550-600 | Cut ~300 words. Team effectiveness paragraph is verbose. Communication section can be tighter. |
| 05 Self-Development | 1,146 | 650-700 | Cut ~450 words. Biggest section, most bloat. Career goals + development programme too wordy. |

---

## 2. Rubric Coverage Matrix

### M5 -- Design Solutions with Originality (+ STEEPLE)

| Requirement | Where Addressed | Coverage (1-5) | Notes |
|-------------|----------------|----------------|-------|
| Original solutions | S02, para 1-3 (dual-backend, sim-first, localisation) | **5** | Three distinct examples, all project-specific |
| Complex engineering problems | S02, para 1 (Pi constraints, <5 FPS) | **4** | Good but could be more explicit about "complexity" |
| STEEPLE integration | S02, paras 1-3 + S02 subsection 2 | **4** | Safety, economic, legal, environmental woven into design. Political/technological light. |
| Diversity & inclusion | S02, subsection 3 | **3** | Present but feels bolted-on. 5 nationalities is stated, not deeply explored. Browser-based GS as inclusive design is good but stretched. |
| Evidence of design iteration | S02, para 3 (GPS lag discovery) | **3** | Only one iteration shown. Could reference the state machine simplification from S04 as design iteration driven by team feedback. |

**M5 total: 19/25 (76%). Strong on originality, weak on iteration evidence and diversity depth.**

### M7 -- Environmental and Societal Impact

| Requirement | Where Addressed | Coverage (1-5) | Notes |
|-------------|----------------|----------------|-------|
| Positive societal impact | S03, subsection 1 | **4** | SAR benefit + cost accessibility. Good. |
| Environmental impact quantified | S03, subsection 2 | **5** | 125kg CO2, 15W vs 300W, 0.5kWh Colab. Excellent specificity. |
| Lifecycle analysis | S03, subsection 2, last sentence | **2** | Acknowledged as gap, but no actual lifecycle content. Manufacturing, disposal, battery recycling all just named. |
| Adverse/dual-use impact | S03, subsection 3 | **5** | Outstanding. Personal Ukrainian perspective, honest about limitations of safeguards. Best paragraph in the report. |
| Mitigation strategies | S03, subsection 3, last para | **4** | Hardware geofencing suggestion is good. MIT licence tension identified but no stance taken. |
| Full lifecycle (manufacturing to disposal) | S03 | **2** | This is the biggest M7 gap. Admitting the gap is better than ignoring it, but at Level 7 you need to at least sketch the lifecycle. |

**M7 total: 22/30 (73%). Dual-use is exceptional, lifecycle analysis is the weak link.**

### M16 -- Team Effectiveness Evaluation

| Requirement | Where Addressed | Coverage (1-5) | Notes |
|-------------|----------------|----------------|-------|
| Leadership with creativity | S04, para 1 (role description) | **3** | Described roles, but leadership is stated not demonstrated. |
| Flexibility responsive to team | S04, para 3 (state machine compromise) | **4** | One excellent example, but "once in twenty weeks" undermines it. |
| Conflict management | S04, para 3 (ROS2 + state machine) | **3** | ROS2 is persuasion-by-demonstration, not conflict management. State machine is genuine but self-admitted as isolated. |
| Evaluate OWN effectiveness | S04, para 2 (solo coding admission) | **5** | Brutally honest about solo coding tendency and its impact. |
| Evaluate TEAM effectiveness | S04, last para (team effectiveness) | **3** | Present but reads as descriptive list. "Three of five roles had low sustained workload" -- good observation but no analysis of WHY or what the team could have done. |
| Evidence of bidirectional influence | S04, paras 3-4 (compromise + feedback) | **3** | Pilot button feedback and PM documentation feedback are the only bidirectional examples. State machine is the only case where team changed YOUR direction. |

**M16 total: 21/30 (70%). Solo coding honesty is excellent, but bidirectional influence and conflict management remain thin.**

### M17 -- Communication Methods + Evaluation

| Requirement | Where Addressed | Coverage (1-5) | Notes |
|-------------|----------------|----------------|-------|
| Communication methods listed | S04, "Communication across skill gaps" para | **4** | Simulator, ground station, demos, docs. Good range. |
| Evaluate effectiveness of each | S04, "Communication" para + "Receiving feedback" | **3** | Ground station has evidence (pilot independence). Other methods evaluated only by assertion. |
| Audience adaptation | S04, para on pilot walkthrough | **3** | One example (pilot). No discussion of adapting for PM, assessors, or other stakeholders. |
| PDR/FDR presentation evaluation | Not present | **1** | Mentioned once ("Live demonstrations at PDR and FDR") but zero reflection on presentation effectiveness. |
| Written vs verbal vs visual | S04, scattered | **2** | Simulator as visual aid is good. But no structured comparison of methods or reflection on which is stronger/weaker for the author. |

**M17 total: 13/25 (52%). This is the weakest area. Communication is described but not systematically evaluated.**

---

## 3. Evidence Audit -- Every Claim and Its Backing

### Section 02: Design & Problem-Solving

| Claim | Evidence | Strength |
|-------|----------|----------|
| "~15,000 lines of Python" | Codebase exists, verifiable | STRONG |
| "Single interface detect_in_image(frame)" | Code architecture, verifiable | STRONG |
| "Edward benchmarked detection thresholds and calibrated FOV" | Named teammate + specific task | STRONG |
| "Pounds 60 Pi platform" | Hardware cost, verifiable | STRONG |
| Simulation replaced ~50 physical flights | Rough estimate, reasonable | MODERATE -- hard to verify but plausible |
| "GPS timing lag 100-200ms" | DJI video analysis, documented in project | STRONG |
| "inverse-variance weighting w = 1/h^2" | Algorithm in code | STRONG |
| "Five-step progressive testing sequence" | Test ladder in docs/FLIGHT_LADDER.md | STRONG |

### Section 03: Societal & Environmental

| Claim | Evidence | Strength |
|-------|----------|----------|
| "Pounds 60 Raspberry Pi" | Hardware price | STRONG |
| "3.2 MB TFLite model" | File size verifiable | STRONG |
| "~2.5 kg CO2 from battery manufacturing amortisation" per flight | **WEAK** -- this number is dubious. Battery manufacturing CO2 amortised over one flight? Source needed. |
| "125 kg CO2 equivalent avoided" | Derived from dubious per-flight number | **WEAK** |
| "15W vs 300W+" | Pi power draw is ~15W under load, GPU server is reasonable | MODERATE |
| "0.5 kWh for 150 epochs on Colab" | Plausible estimate | MODERATE |
| "Human-in-the-loop is a software constraint, not hardware" | Accurate architectural claim | STRONG |
| "Removing verification prompt is a single-line code change" | Accurate | STRONG |

### Section 04: Teamwork

| Claim | Evidence | Strength |
|-------|----------|----------|
| "Specialist and Completer-Finisher" (Belbin) | Self-assessed, reasonable fit | MODERATE |
| "Hardware lead assembled drone independently" | Team structure claim | MODERATE -- no external confirmation |
| "25-30 hours per week from me alone" | Self-reported | MODERATE |
| "Teammates expressed frustration at feeling sidelined" | **Key claim with no specific moment/quote** | **WEAK** -- stated but not shown |
| "Pilot navigated ground station independently" | Specific observable event | STRONG |
| State machine compromise (11 states -> simplified) | Specific design change | STRONG |
| "Once in twenty weeks" | Honest quantification | STRONG (as self-assessment) |
| "ROS 2 vs raw MAVLink -- 20-line demo" | Specific technical artefact | STRONG |
| Pilot identified abort/confirm button proximity | Specific feedback event | STRONG |
| PM said documentation "too dense" | Specific feedback, but no direct quote | MODERATE |
| Edward's "pace of iteration" feedback | Paraphrased, no quote | MODERATE |

### Section 05: Self-Development

| Claim | Evidence | Strength |
|-------|----------|----------|
| "Learned MAVLink from scratch" | Codebase evidence | STRONG |
| "206.5ms, 4.8 FPS on Pi 5" -- wait, this isn't in section 05 | N/A | N/A |
| "Python 3.13 broke tflite-runtime" | Documented, verifiable | STRONG |
| "IMX296 outputs BGR despite RGB888 label" | Documented, tested | STRONG |
| "Docker-based Pi environment test" | Dockerfile.pi-test exists | STRONG |
| "25-30 hours per week" (repeated from S04) | Self-reported, redundant | MODERATE |
| "Ukraine's engineering culture prizes individual competence" | Personal observation, not sourced | MODERATE -- compelling but unsupported |
| Edward: "built things faster than anyone could review them" | Paraphrased quote | MODERATE -- would be stronger as direct quote |
| PM: "out of the loop" | Paraphrased quote | MODERATE |
| "Walked pilot through ground station field-by-field" | Specific activity | STRONG |
| "Explained state machine to PM using simulator" | Specific activity | STRONG |
| "Paired with Edward on FOV calibration" | Specific activity | STRONG |

---

## 4. Missing Elements

### CRITICAL (will cost marks if absent)

1. **PDR/FDR presentation reflection.** These are explicitly mentioned in the rubric guidance for M17 and TARGET_BRIEF. Currently one throwaway mention ("Live demonstrations at PDR and FDR generated more engagement than slides"). Need: What did you present? How did you adapt for the audience? What feedback did you receive? Was the presentation effective?

2. **Systematic evaluation of communication methods.** M17 explicitly asks you to EVALUATE methods, not just list them. Need a paragraph that compares: documentation vs demos vs ground station vs verbal briefings -- which worked for which audience, and why?

3. **Development programme success metrics.** All three development actions lack a measurable criterion for success. "How will you know this worked?" is unanswered. E.g., "In my next project, I will measure this by..." or "Success looks like..."

4. **MSc coursework balance.** Not mentioned once. If 25-30 hours/week went to this project, what happened to other modules? This is real self-management evidence left on the table.

### IMPORTANT (would strengthen the report)

5. **A mid-execution crisis (real-time adaptation).** All failure stories are retrospective (Pi deployment, camera colour). A moment where the plan broke DURING execution and you adapted on the spot would demonstrate dynamic self-management.

6. **Teammate frustration shown, not told.** "Teammates expressed frustration at feeling sidelined" is a critical claim with no specific moment, conversation, or quote. Show the moment this surfaced -- a meeting, a message, a conversation.

7. **Why the team structure produced the imbalance.** "Three roles had low sustained workload" is observed but not analysed. Was it the curriculum? Self-selection? Early role assignment? Poor scoping? This analysis would push M16 higher.

8. **MIT licence stance.** The dual-use section identifies the tension (anyone can fork and strip safeguards) but takes no position on whether MIT was the right choice. A one-sentence stance would demonstrate evaluative depth.

### NICE TO HAVE (diminishing returns)

9. **Argyris double-loop learning** applied to the speed-over-inclusion pattern (single-loop: "I'll involve team next time" vs double-loop: "I need to redefine what 'productive' means").

10. **Bus factor / industrial implications.** The "single point of failure" observation is made but not connected to professional practice in industry.

---

## 5. Weak Paragraphs (Descriptive Rather Than Reflective)

### S02: Diversity and Inclusion Subsection (WEAKEST)
> "Our team of five spanned five nationalities... I chose to build the ground station as a browser-based web application... All 16 documentation files were written in English..."

**Problem:** This reads as a project description with a reflective sentence tacked on at the end. The "lesson" ("inclusive design is a natural consequence of working in a diverse team") is a platitude. It does not show genuine learning or change in the author's thinking. The connection between 5 nationalities and browser-based GS is a stretch -- the GS was browser-based for technical reasons (headless Pi), not diversity reasons.

**Fix:** Either make this genuinely reflective (a moment where a cultural difference surfaced and changed your design approach) or cut it to 2 sentences and fold into another section. Currently wastes ~120 words.

### S03: Environmental Impact -- Quantification Block
> "Simulation-first development replaced approximately 50 physical test flights; assuming each flight consumes a 6S LiPo cycle (~2.5 kg CO2 from battery manufacturing amortisation, motor wear, and travel to the test site), this avoided an estimated 125 kg of CO2 equivalent."

**Problem:** The 2.5 kg CO2 per flight number is dubious and unsourced. Battery manufacturing amortisation spread over a single flight is not how lifecycle analysis works. The 125 kg figure sounds impressive but is built on shaky foundations. A marker with engineering background may challenge this.

**Fix:** Either source the number, reduce it to a more defensible estimate, or shift to qualitative: "Simulation-first development avoided approximately 50 physical test flights, reducing battery wear, motor degradation, and travel emissions -- though quantifying the exact savings would require a formal lifecycle assessment."

### S04: Team Effectiveness Evaluation (Last Paragraph)
> "Collectively, the team delivered a working system, but the five-person structure was suboptimal for a software-heavy project. Three of the five roles had low sustained workload..."

**Problem:** Reads as a summary/observation, not reflection. States what went wrong but does not analyse WHY the structure emerged or how the author's actions contributed to the imbalance. No reflective framework applied.

**Fix:** Apply Kolb or Gibbs to this observation. Why did the author not push for restructuring earlier? Was it because redistributing work felt slower than doing it alone? Connect to the "speed over inclusion" pattern from S05.

### S05: Career Goals (Last Paragraph)
> "I came to Bristol from Ukraine to develop robotics skills I can bring back to help my country... The skills developed---MAVLink integration, edge AI, safety-critical design---transfer to autonomous systems Ukraine needs..."

**Problem:** While emotionally compelling, this is a statement of intent, not reflection. No evidence of HOW the project changed the author's understanding of their career goals, or what they learned about themselves through the connection.

**Fix:** Add one sentence of genuine reflection: how did working on SAR drones change how you think about the technology's application in Ukraine? Did the dual-use tension in S03 make you reconsider anything?

---

## 6. Strongest Paragraphs (DO NOT BREAK THESE)

1. **S03: Dual-Use (Adverse Impact) -- paragraphs 1-2 of subsection 3.** This is the best writing in the entire report. Personal, honest, specific, and brave. The line "human-in-the-loop verification is not a feature I added for the rubric, but a constraint I insisted on because I understand what happens when it is removed" is exceptional. DO NOT TOUCH.

2. **S04: State Machine Compromise -- paragraph 3 of teamwork.** The only genuine compromise in the report, and the meta-commentary ("once in twenty weeks") elevates it from anecdote to self-analysis. The shift from "what I can debug" to "what the team can debug" is a genuine insight.

3. **S05: Strengths-as-Weaknesses Duality -- subsection 3.** The connection between rapid prototyping and speed-over-inclusion, validated by Edward's and PM's observations, is sophisticated. The Ukrainian cultural framing adds depth.

4. **S04: Pilot Button Safety Feedback.** Concrete, specific, with a clear action taken. Good evidence of receiving and acting on feedback.

5. **S02: Simulation-First Development.** Well-argued, with Schon reference and practical evidence. The environmental/safety connection is natural, not forced.

---

## 7. Page Count Analysis

| Item | Current | Required | Status |
|------|---------|----------|--------|
| Body content (sections 1-5) | ~7 pages | 5 pages max | **FAIL: 2 PAGES OVER** |
| References | 1 page | Excluded from limit | OK |
| Cover page | Not present | Excluded from limit | OK (title block on page 1 counts as part of body) |

**To reach 5 pages, you must cut ~1,000-1,200 words from the current ~3,292.**

Priority cuts (by lowest value-per-word):
1. S05 Self-Development: cut ~450 words (currently 1,146, target ~700). The "helping teammates develop" subsection repeats S04 content. Career goals paragraph can be 2 sentences.
2. S03 Environmental Impact: cut ~250 words. The quantified CO2 block can be halved (keep the approach, drop the dubious numbers). Lifecycle acknowledgement can be one sentence.
3. S04 Teamwork: cut ~300 words. Team effectiveness evaluation paragraph is verbose. Communication section can merge with the feedback section.
4. S02 Design: cut ~150 words. Diversity subsection can be halved.

---

## 8. Compilation Check

### Does main.tex include all sections?
- [x] `\input{sections/01_introduction}` -- YES
- [x] `\input{sections/02_design_problem_solving}` -- YES
- [x] `\input{sections/03_societal_environmental}` -- YES
- [x] `\input{sections/04_teamwork_leadership}` -- YES
- [x] `\input{sections/05_self_development}` -- YES
- [x] `\printbibliography` -- YES
- [x] biber compiles without errors -- YES

### Package issues?
- [x] All packages installed and working
- **Warning**: Overfull hbox in S02 para 1 (line 8-9). The `\texttt{detect\_in\_image(frame)}` is too wide. Fix: use `\small\texttt{...}` or break the line.
- **Warning**: Two undefined references on first compile (resolved on second pass). Normal with biblatex.

### Unused bibliography entries
These entries are in references.bib but never cited:
- `redmon2016yolo` (YOLO original paper)
- `aiedgelitert` (ai-edge-litert)
- `mavproxy` (MAVProxy)
- `abbeel2007helicopter` (RL helicopter)
- `hartley2003` (multi-view geometry)
- `opencv` (OpenCV)
- `picamera2` (picamera2)
- `mcconnell2004` (Code Complete)
- `humble2010` (Continuous Delivery)

**11 of 20 bib entries are unused.** Clean up to avoid biber warnings and reduce bibliography size (saves ~0.3 pages on the references page).

---

## 9. TOP 10 SPECIFIC IMPROVEMENTS (Ranked by Expected Mark Impact)

### 1. CUT TO 5 PAGES (+0 marks, but prevents PENALTY of -5 to -15)
**Impact: CRITICAL -- failure condition if not fixed.**
The report is 7 pages of body content. A 5-page limit violation may result in: (a) marker stops reading at page 5, losing all of S05; (b) explicit penalty; (c) impression of inability to follow instructions. Cut ~1,200 words as outlined in Section 7 above.

### 2. ADD PDR/FDR REFLECTION (+2-3 marks on M17)
**Impact: HIGH. Currently M17's biggest gap.**
Add 2-3 sentences about presenting at PDR and/or FDR. What did you present? How did you adapt for the audience (assessors vs teammates)? What feedback did you receive? Did you change anything based on it? This directly addresses the rubric's "evaluate communication methods" requirement. Can replace some of the verbose communication content.

### 3. SYSTEMATIC COMMUNICATION EVALUATION (+1-2 marks on M17)
**Impact: HIGH. M17 is the weakest AHEP4 standard (52% coverage).**
Add a compact paragraph that evaluates 3-4 communication methods used, not just lists them:
- Documentation: effective for async reference, but PM said "too dense" -> restructured
- Simulator demos: most effective for non-technical understanding
- Ground station: proven effective (pilot independent on field day)
- Verbal briefings: author's weakest mode, needs preparation
This turns M17 from description to evaluation.

### 4. TRIM DIVERSITY SUBSECTION (+0 marks, saves ~80 words for higher-value content)
**Impact: MEDIUM. Currently wastes space on weak reflective content.**
The diversity subsection in S02 is 120 words of descriptive content with a platitude conclusion. Cut to 2-3 sentences: "Team of five nationalities. Designed browser-based GS partly because different platforms, partly for volunteer accessibility. Taught me inclusive design emerges from diverse constraints."

### 5. ADD DEVELOPMENT PROGRAMME SUCCESS METRICS (+1 mark on Insight)
**Impact: MEDIUM. Explicitly identified in v5 scoring as gap.**
For each of the 3 development actions, add a one-sentence measurable criterion:
1. "Collaborative architecture: success = at least 2 people can modify any module independently"
2. "Day-one deployment: success = target hardware tested within first 5 days"
3. "Communication cadence: success = no teammate reports feeling 'out of the loop' at project end"

### 6. SHOW TEAMMATE FRUSTRATION MOMENT (+1 mark on M16)
**Impact: MEDIUM. Key claim currently unsupported.**
Replace "Teammates expressed frustration at feeling sidelined" with a specific moment: a team meeting, a message, a conversation. Even one sentence: "In week 16, the project manager said in our team meeting that she had not contributed to any code commit in three weeks and felt the software workstream was a black box." This transforms assertion into evidence.

### 7. FIX DUBIOUS CO2 NUMBERS (+0.5 marks on M7, prevents mark LOSS)
**Impact: MEDIUM. A sceptical marker could deduct for unsourced quantification.**
Either source the 2.5 kg CO2 per flight figure, reduce to a defensible range, or switch to qualitative framing. The current number looks like it was made up, which undermines the otherwise strong environmental section.

### 8. CUT S05 REPETITION (-0 marks, saves ~200 words)
**Impact: MEDIUM (space recovery). S05 "Helping Teammates Develop" repeats S04 content.**
The pilot walkthrough, PM simulator explanation, and Edward FOV calibration are already in S04. In S05, reference them with "As described in Section 4" and use the saved space for new content (PDR/FDR reflection, success metrics).

### 9. CONNECT CAREER GOALS TO DUAL-USE TENSION (+0.5 marks on Insight)
**Impact: LOW-MEDIUM.**
The career goals paragraph in S05 and the dual-use section in S03 are thematically linked but disconnected. One sentence in S05: "The dual-use tension I explored in Section 3 is not hypothetical for my career -- I will face these exact trade-offs when deploying autonomous systems in Ukraine." This closes the loop.

### 10. TAKE MIT LICENCE STANCE (+0.5 marks on M7)
**Impact: LOW. Identified in v5 scoring but small marginal gain.**
One sentence in S03: "In hindsight, a more restrictive licence -- such as a non-commercial clause prohibiting military adaptation -- would have been appropriate for this class of system, though it conflicts with the open-source ethos that enables volunteer SAR teams to adopt the technology." This demonstrates evaluative depth beyond description.

---

## Summary: Action Plan

**Phase 1 (MUST DO -- prevents penalty):**
- Cut report to 5 pages. Target: ~2,100 words total.
- Biggest cuts: S05 (-450w), S04 (-300w), S03 (-250w), S02 (-150w).

**Phase 2 (HIGH VALUE -- target +3-5 marks):**
- Add PDR/FDR reflection (3 sentences, ~50 words)
- Add systematic communication evaluation paragraph (~80 words)
- Add development programme success metrics (3 sentences, ~45 words)
- Show teammate frustration as specific moment (~30 words)

**Phase 3 (POLISH -- target +1-2 marks):**
- Fix CO2 numbers
- Trim diversity subsection
- Connect career goals to dual-use
- Clean up unused bib entries

**Expected score after all improvements: 86-88** (from current 83-84).
The page count fix alone prevents a potential 5-15 mark penalty.
The M17 improvements (PDR/FDR + systematic evaluation) address the weakest criterion.
