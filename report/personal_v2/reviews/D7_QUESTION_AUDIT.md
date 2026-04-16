# D7 Question Audit — Release 2.2 (§10.1) vs. `report/personal_v2/`

**Audited**: 2026-04-11
**Sources**: `report/personal_v2/sections/01_introduction.tex` through `05_self_development.tex` (current LaTeX).
**Also reviewed**: `report/report_d7_pages/page_01.png`–`page_08.png` (compiled PDF).

## Source vs. PDF mismatch (read this first)

The compiled PDF in `report_d7_pages/` does NOT match the current `.tex` sources. The PDF is an **older draft** with different section structure:

| PDF (older) | LaTeX sources (current) |
|---|---|
| §4.2 What Worked Well | No such subsection |
| §4.3 The Solo Coding Reality | Paragraph in §4 (un-labelled) |
| §4.4 Managing Disagreements | §4 "Disagreements and compromise" paragraph |
| §4.5 Communication Methods and Effectiveness | §4 "Communication across skill gaps (M17)" |
| §4.6 Giving and Receiving Feedback | §4 "Receiving and acting on feedback" (no "giving" subsection in sources) |
| §5.1–5.4 + 5.5 Dev Programme + 5.6 Career + 5.7 Final Thought | §5.1 Skills Developed, §5.2 Time Mgmt Failures, §5.3 Strengths/Weaknesses, §5.4 Development Programme (+ career paragraph) |
| References: only [1] Koopman | References: full biblatex bibliography |

The PDF also names no teammates by role (no "Edward"); the LaTeX sources do. **This audit scores the LaTeX sources** because they are the live version, but notes where the PDF diverges.

---

## The 10 required questions

### 1. My role

#### 1a. Roles/responsibilities — explicit vs implicit, did they change?
- **Status**: PARTIAL
- **Where**: §1 Introduction (p.1) + §4 opening paragraph (p.3, "Our five-person team had distinct roles…")
- **Quality**: weak
- **Specific evidence**: Explicit role stated ("software and computer vision lead"; "state machine, vision, planning, localisation, ground station, testing, ~15,000 lines"). Other teammates described only by role ("hardware lead", "pilot", "project manager", "flight dynamics research"). Edward is the only teammate named.
- **What's missing**:
  - No distinction between *explicit* (assigned at kickoff) vs *implicit* (drifted into) responsibilities.
  - No account of whether the role **changed over time** — e.g. did the author become de facto systems integrator later? The phrase "de facto systems integrator" appears but is not traced through the project timeline.
  - No dates, no kickoff meeting reference, no mention of when roles were formally agreed.

#### 1b. Most proud of?
- **Status**: MISSING
- **Where**: Not explicitly answered anywhere.
- **Quality**: n/a
- **Specific evidence**: no
- **What's missing**: No sentence of the form "I am most proud of…". §5.3 names a strength ("rapid prototyping and system integration") and §5.1 names the most formative skill (BGR/RGB channel debug), but neither is framed as pride. The IMX296 debugging story and the pilot flying the ground station unaided are candidates but are not labelled as "proud of".

#### 1c. Focus differently in future?
- **Status**: PARTIAL
- **Where**: §5.4 Development Programme (Actions 1–3, p.7) and §4 closing paragraph ("A more effective allocation would have paired two people on software from day one").
- **Quality**: strong on *how I would work* (three actions), weak on *focus* in the personal-role sense.
- **Specific evidence**: yes — three concrete actions: (1) collaborative architecture from day one; (2) day-one hardware deployment; (3) structured communication cadence with "one sentence, one diagram, one demo" framework.
- **What's missing**: Framed as team/process improvements, not as "which parts of *my own role* I would refocus". No statement like "I would spend less time on X and more on Y."

---

### 2. My team

#### 2a. Team structure — discussed explicitly? changed?
- **Status**: PARTIAL
- **Where**: §4 opening paragraph (p.3).
- **Quality**: weak
- **Specific evidence**: Structure described ("five-person team", roles listed), Belbin framework applied ("Specialist and Completer-Finisher").
- **What's missing**:
  - No statement of whether the team ever **sat down and discussed structure** (kickoff, mid-project retro, etc.).
  - No account of whether structure **changed** during the project. Only a retrospective judgement ("the five-person structure was suboptimal") — no narrative of a change that happened or was attempted.
  - No meeting cadence (e.g. "we met weekly on Tuesdays") or decision-making process described.

#### 2b. Most impactful team-working elements?
- **Status**: PARTIAL
- **Where**: §4 paragraph 1 ("worked effectively where responsibilities had explicit handoff points") + §4 paragraph 2 (Edward pairing) + §4 "Communication across skill gaps" (simulator as communication device).
- **Quality**: moderate
- **Specific evidence**: Three specific elements named — (i) explicit handoff points between independent roles, (ii) Edward–author pairing on CV "complementary expertise", (iii) the simulator as a communication device. The pilot's independent operation of the ground station on the cancelled flight day is cited as "strongest evidence".
- **What's missing**: No explicit ranking or "most impactful" statement. No mention of team rituals (stand-ups, retrospectives, Slack/Discord, shared docs, PDR/FDR presentations — though the PDF draft mentions PDR/FDR, the current LaTeX does not).

#### 2c. What would you change?
- **Status**: ANSWERED
- **Where**: §4 final paragraph "Team effectiveness evaluation" (p.4); §4 "Helping teammates develop" paragraph.
- **Quality**: strong
- **Specific evidence**: yes — "pair two people on software from day one with explicit interface contracts and code review cycles, treating skill transfer as a project deliverable". Also the self-criticism "contribution points must be designed in from the start, not retrofitted."
- **What's missing**: None for this question; answer is direct and specific.

---

### 3. My impact

#### 3a. How did YOUR contributions drive team forward?
- **Status**: PARTIAL
- **Where**: §2 Design and Problem-Solving (dual-backend architecture, simulator, target localisation) + §4 paragraph 2 (Edward pairing unlocked CV calibration).
- **Quality**: moderate
- **Specific evidence**: Modular vision.py let Edward's FOV calibration "slot in without any integration pain"; simulator "replaced approximately 50 physical test flights"; ground station let the pilot operate autonomously on flight day. These are impact claims tied to specific teammates/events.
- **What's missing**:
  - No explicit "because I built X, the team was able to Y" framing for the overall project.
  - No quantified team-level outcomes (e.g. "this saved the team N days", "unblocked task Z").
  - Unclear how the author's work enabled the **project administration**, **flight dynamics research**, or **hardware assembly** teammates — only Edward's progress is clearly linked.

#### 3b. Add/refocus in future?
- **Status**: PARTIAL
- **Where**: §5.4 Development Programme, Action 1 and Action 3; §4 "Helping teammates develop" ("Creating a checklist is accessibility; sitting with someone while they write their first MAVLink command is development").
- **Quality**: moderate to strong on *process*, weak on *technical focus*.
- **Specific evidence**: yes — would refocus from "making a system usable" to "making a team capable"; would design contribution points from week 1; would schedule regular check-ins.
- **What's missing**: No statement about which *technical* contributions to add or drop. e.g. "I would do less X (CV work) and more Y (documentation)" — the refocus is entirely on collaboration style, not on the portfolio of technical tasks.

---

### 4. My support

#### 4a. What did OTHERS do that helped YOU?
- **Status**: PARTIAL
- **Where**: §4 "Receiving and acting on feedback" paragraph (p.4); §4 paragraph 2 (Edward's optics knowledge).
- **Quality**: moderate
- **Specific evidence**: Three concrete feedback incidents —
  1. Pilot identified abort/confirm buttons were dangerously close → author separated them and added confirmation.
  2. Project manager said documentation was too dense → author restructured guides + one-page checklist.
  3. Edward noted iteration pace made module versions hard to track → author added version tags and ground-truth document.
  - Also: Edward's FOV calibration and lens-distortion work; team's push-back on 11-state machine ("sitting with their feedback overnight") which changed the author's mind.
  - Project manager "booked field slots and submitted risk assessments I would have neglected".
- **What's missing**:
  - Only Edward is named. The pilot and project manager are un-named.
  - No emotional/morale support mentioned — all "help" is technical-feedback or logistical.
  - No supervisor/advisor input mentioned at all.
  - No incidents where a teammate unblocked the author on a technical problem (vs. on a design decision).

#### 4b. What did YOU do that helped OTHERS?
- **Status**: PARTIAL (and explicitly self-critical)
- **Where**: §4 "Communication across skill gaps" and "Helping teammates develop" paragraphs; §4 paragraph 2 (Edward pairing).
- **Quality**: moderate — the section is dominated by an **admission of failure** to support teammates.
- **Specific evidence**:
  - Built numbered test scripts, 16 guide files, a browser-based ground station, simulator — framed as accessibility tools.
  - Taught the pilot via "hands-on bench walkthroughs until he could make independent decisions during flight".
  - Paired with Edward on complementary CV tasks → "Edward grew because we paired".
  - Explicit admission: "did not invest in developing teammates' technical skills… I handed them finished systems instead of learning opportunities."
- **What's missing**:
  - Very little positive "helping others" — the dominant note is what the author failed to do.
  - No mention of helping teammates with report writing, debugging their own code, or non-technical support (morale, time management, stress).
  - No feedback the author *gave* to teammates (only feedback *received*).

---

## Catalogue

### Named teammates
- **Edward** — named 3 times (§2 "Edward benchmarked detection thresholds and calibrated the camera's field of view", §4 "productive sub-team pairing was with Edward on computer vision", §5 "Edward observed that I 'built things faster than anyone could review them'").
- **Others un-named**: "hardware lead", "pilot", "project manager" (referred to as "she" once), "flight dynamics research" teammate. Five nationalities mentioned, none specified.
- **No supervisor / academic staff / industry advisor named.**

### Named incidents (with specificity)
1. IMX296 camera BGR-vs-RGB debug, "six channel permutations on a PuTTY terminal" (§5.1). No date.
2. Python 3.13 broke `tflite-runtime` in week 18; cost "two full days" (§5.2). Weeks specified.
3. Pilot flagged dangerous button placement → author separated controls + confirmation dialog (§4 feedback para). No date.
4. Project manager criticised dense documentation → author created one-page colleague checklist (§4). No date.
5. Edward noted version-tracking problem → author added version tags + ground-truth document (§4). No date.
6. 11-state machine pushback → author refactored after "sitting with their feedback overnight", "cost a week of refactoring" (§4). No date.
7. ROS 2 vs raw MAVLink disagreement resolved by "20-line working heartbeat demo" (§4). Described as "persuasion by fait accompli".
8. Project manager said she felt unable to contribute beyond logistics → author "offered reassurance" (self-criticised as "conflict avoidance disguised as appreciation") (§4). No date.
9. Weather cancelled flight day → pre-planned bench tests salvaged it (§5.2). No date.
10. Cancelled flight day: pilot operated ground station unaided (§4). No date.
11. Simulation-first claim: "replaced approximately 50 physical test flights" (§2, §3).

### Conflict mentioned: YES
- ROS 2 vs. MAVLink (technical).
- 11-state machine complexity (technical, genuine change of mind).
- Project manager's workload/contribution concern (interpersonal — self-critically acknowledged as unresolved).
- General "teammates expressed frustration at feeling sidelined" (§4).

### Feedback given to others: MINIMAL
- Author received three specific pieces of feedback (catalogued above).
- No specific incident of **feedback the author gave** to a named teammate. The Edward pairing implies mutual exchange but no concrete example.
- "Teaching the pilot to read mode indicators independently" (§5.4) is skills transfer, not feedback.

### Self-development actions: LISTED and PARTIALLY IMPLEMENTED
- Three numbered actions in §5.4:
  1. Collaborative architecture from day one — *partially implemented* (vision.py interface, numbered test scripts cited).
  2. Day-one hardware deployment — *implemented* (Docker Pi test + preflight checker).
  3. Structured communication cadence — *claimed but no evidence of implementation in this project*.
- Measurement criterion given for Action 3 ("whether a teammate can independently modify a module I wrote within one sprint") but no pass/fail stated.

### Autonomous initiative (started without being asked)
- Built simulator from scratch (§2).
- Designed 5-step progressive testing ladder (§2).
- Created Docker Pi test after Python 3.13 incident (§5.2).
- Insisted on human-in-the-loop verification stage (§3).
- Created `CLAUDE.md` 800+ line ground-truth document (§5.2).
- Wrote 16 guide files and one-page colleague checklist (§4).
- Refactored 11-state machine after team feedback (§4) — not strictly autonomous (team-prompted) but self-directed.

### Changed thinking / worldview shifts
1. **11-state machine → simpler FSM** (§4): "first time I genuinely changed a technical direction because of team input rather than technical evidence"; "shifting my view of 'good architecture' from 'what I can debug' to 'what the team can debug.'" Most explicit worldview-shift in the document.
2. **Accessibility vs. capability-building** (§4): "Creating a checklist is accessibility; sitting with someone while they write their first MAVLink command is development."
3. **Simulation as insufficient validation** (§5.3): "delayed hardware testing… I treated simulation as sufficient validation for too long."
4. **Ukraine engineering culture reflection** (§5.3): "Ukraine's engineering culture, where individual competence is prized above collaborative process. Learning to value slower, inclusive approaches as equally 'productive' is an ongoing adjustment."
5. **Dual-use reflection** (§3.3): personal/Ukrainian perspective shapes view of autonomy — but this is a held conviction, not a shift during the project.

---

## Summary scoreboard

| # | Question | Status |
|---|---|---|
| 1a | Roles — explicit/implicit, changed? | PARTIAL |
| 1b | Most proud of? | **MISSING** |
| 1c | Focus differently in future? | PARTIAL |
| 2a | Team structure discussed explicitly? Changed? | PARTIAL |
| 2b | Most impactful team-working elements? | PARTIAL |
| 2c | What would you change? | ANSWERED |
| 3a | How YOUR contributions drove team forward | PARTIAL |
| 3b | Add/refocus in future? | PARTIAL |
| 4a | What OTHERS did that helped YOU | PARTIAL |
| 4b | What YOU did that helped OTHERS | PARTIAL (heavily self-critical) |

**Gaps most likely to cost marks in a rewrite:**
- Question **1b** is entirely absent — no "most proud of" sentence exists.
- Only **one teammate is named** (Edward). The pilot and project manager are anonymous, which weakens every "my team" and "my support" answer.
- No **dates or meeting references** anywhere — incidents float in time.
- No **feedback the author gave** to any named teammate.
- No **kickoff / structure-discussion** event described for Question 2a.
- No mention of supervisor, advisor, or any external stakeholder support.
- PDF compiled output (`report_d7_pages/`) is **out of date** relative to `.tex` sources — needs recompilation before submission.
