# D6 Goldmine Body: Section Transitions Review

**Date:** 2026-04-04
**Sections reviewed (in order):**
1. `report/sections/introduction.tex`
2. `report/sections/design_rationale.tex`
3. `report/sections/system_description.tex`
4. `report/sections/requirements_verification.tex`
5. `report/sections/evaluation.tex`

---

## 1. Narrative Arc Assessment

The five sections follow a clear **problem -> approach -> implementation -> proof -> reflection** arc:

| Section | Role in arc | Status |
|---------|-------------|--------|
| Introduction | **Problem**: SAR time pressure, coverage gap, cost gap | Strong |
| Design Rationale | **Approach**: why these choices (STEEPLE, trade studies, parameter optimisation) | Strong |
| System Description | **Implementation**: how the choices became a working system | Strong |
| Requirements Verification | **Proof**: does the system meet the 12 requirements? | Strong |
| Evaluation | **Reflection**: plus/delta, what worked, what remains | Strong |

The arc is solid. A reader moving through these sections in order will understand the progression from problem to solution to evidence.

---

## 2. Transition-by-Transition Analysis

### Transition 1: Introduction -> Design Rationale

| Check | Before fix | After fix |
|-------|-----------|-----------|
| Intro ends with forward pointer? | YES -- "Report Structure" subsection (S1.5) explicitly maps all sections | No change needed |
| Design Rationale opens with backward link? | NO -- opened cold with "Every major design decision was evaluated..." | FIXED -- now opens with "The mission scenario and requirements outlined in Section 1 demand..." linking back to the problem |

**Note:** The "Report Structure" subsection acts as a mechanical roadmap. It tells the reader WHERE things are, but not WHY they should care. The new opening sentence in Design Rationale provides the narrative "why."

### Transition 2: Design Rationale -> System Description

| Check | Before fix | After fix |
|-------|-----------|-----------|
| Design Rationale ends with forward pointer? | PARTIAL -- had a summary paragraph but no forward link | FIXED -- added "Section 3 now describes how these design choices were realised in the final integrated system." |
| System Description opens with backward link? | NO -- opened with "The final system integrates seven subsystems..." | FIXED -- now opens with "Having established the rationale behind each design choice (Section 2), this section describes how those choices were realised..." |

This was the weakest transition. The reader jumped from "why we chose X" to "here is the full system" with no bridge. Now both ends connect.

### Transition 3: System Description -> Requirements Verification

| Check | Before fix | After fix |
|-------|-----------|-----------|
| System Description ends with forward pointer? | NO -- ended with Figure 10 (mission timeline) and nothing after it | FIXED -- added closing sentence: "With the system architecture... now described, Section 4 verifies that this integrated system satisfies each of the twelve project requirements." |
| Requirements Verification opens with backward link? | NO -- opened cold with "Table X maps each requirement..." | FIXED -- now opens with "The system described in Section 3 was designed to satisfy twelve requirements..." |

This was the second-weakest transition. The system description just stopped after a figure, and requirements verification launched into a table with no preamble.

### Transition 4: Requirements Verification -> Evaluation

| Check | Before fix | After fix |
|-------|-----------|-----------|
| Requirements Verification ends with forward pointer? | PARTIAL -- mentioned gaps (R05, R07 unvalidated) but no explicit forward link | FIXED -- added "Section 5 evaluates the system's overall technical performance, examining both the strengths that these verification results demonstrate and the gaps that remain." |
| Evaluation opens with backward link? | WEAK -- mentioned "12 requirements (R01-R12)" but didn't reference the previous section | FIXED -- now opens with "Section 4 established that 8 of 12 requirements are verified at bench or higher fidelity, with 3 verified in simulation only and 1 partially verified." |

This transition was the strongest before fixes (the content naturally flowed from verification gaps to evaluation), but the explicit section references make the handoff cleaner.

---

## 3. Repeated Content Check

| Issue | Sections | Severity |
|-------|----------|----------|
| FOV calibration (5.46mm) | Design Rationale (S2.10 para 1), System Description (S3.1), Evaluation (P3/weather) | LOW -- each use serves a different purpose (decision change, spec, evidence). Acceptable repetition. |
| mAP50 = 0.995 | Design Rationale (S2.6), System Description (S3.3), Evaluation (P4, D5) | LOW -- same pattern: rationale context, implementation detail, evaluation critique. Each adds something new. |
| BGR colour fix | Design Rationale (S2.10 para 2), System Description (S3.3), Evaluation (P3) | LOW -- mentioned in each section but from a different angle (decision change, preprocessing note, bug-catching evidence). |
| CEP50 = 2.3m | System Description (S3.6), Evaluation (D3) | LOW -- one states the result, the other critiques the uncompensated lag. Fine. |
| Weather cancellation | Design Rationale (S2.11), Evaluation (D1) | LOW -- rationale explains the bench-day pivot, evaluation discusses the validation gap. Different angles. |

**Verdict:** No jarring repetitions. The same numbers appear across sections but each occurrence serves a distinct rhetorical purpose (justification vs specification vs critique). This is expected in a well-integrated report.

---

## 4. Jarring Jumps

| Location | Issue | Severity | Fix applied? |
|----------|-------|----------|-------------|
| End of System Description -> Requirements Verification | Section ended with a figure and no wrap-up text | HIGH | YES -- added closing transition |
| Start of Design Rationale | Jumped straight into STEEPLE without acknowledging the problem from Section 1 | MEDIUM | YES -- added opening sentence linking back |
| Start of System Description | No acknowledgement that the rationale was just presented | MEDIUM | YES -- added "Having established the rationale..." |

No other jarring jumps found. Within each section, the subsection flow is logical.

---

## 5. Reader Orientation ("Where am I? Why am I reading this?")

After fixes, every section now:
- Opens by connecting to the previous section (what was established)
- States what THIS section will do
- Closes by pointing to what comes next

The reader always knows:
- **Introduction**: "Here is the problem and mission."
- **Design Rationale**: "Here is WHY we chose this approach, grounded in the problem just described."
- **System Description**: "Here is HOW those choices became a working system."
- **Requirements Verification**: "Here is PROOF that the system meets the requirements."
- **Evaluation**: "Here is an honest assessment of strengths and gaps."

---

## 6. Summary of Changes Made

| File | Change |
|------|--------|
| `design_rationale.tex` line 4 | Replaced cold opening with backward-linking sentence referencing Section 1 |
| `design_rationale.tex` last paragraph | Added forward pointer: "Section 3 now describes..." |
| `system_description.tex` line 8 | Added "Having established the rationale behind each design choice (Section 2)..." |
| `system_description.tex` after final figure | Added closing transition pointing to Section 4 |
| `requirements_verification.tex` line 3 | Added "The system described in Section 3..." |
| `requirements_verification.tex` final paragraph | Added forward pointer to Section 5 |
| `evaluation.tex` line 3 | Added "Section 4 established that 8 of 12 requirements are verified..." |

**Total: 7 transition sentences added. Zero content deleted.**
