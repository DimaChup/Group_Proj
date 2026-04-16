# D7 V1 SCORE (Scorer A): 64/100

Baseline scoring of `report/personal_v2/main.pdf` (5 pages, compiled). Scored ruthlessly against the harsh rubric, AHEP4 M16/M17 guide, and Hatton & Smith depth test.

---

## HARD GATES

- [x] **Page limit <=7 (working) / <=5 (final)**: PASS — 5 pages body exactly (hits final target)
- [x] **4 required headings (My role / My team / My impact / My support)**: PASS — all four present (Sections 1-4)
- [x] **10 questions answered**: **10/10** — sub-headings 1a-4b all explicitly labelled and answered. (Question-coverage gate: passed.)
- [x] **Specifics (named people/dates/incidents)**: PASS — Robin, Demetro, Edward, Pilot, Project manager all named; wk16/wk18/wk20/wk22 dated; commit hashes (`2ba32f5`, `3d62e6a`, `cb39098`, `ea13d56`, `f2f2c85`, `7928c5a`, `792be5a` etc.) cited inline. Robust.
- [x] **Readability (10pt+, clear layout)**: PASS — appears 10pt body with compact tables, readable, 90%+ page density. No cramp.
- [~] **Media diversity**: BORDERLINE FAIL — only prose + text tables. **No screenshots, no diagrams, no photos, no figures**. Purely report-only. This caps Bristol Communication line at 59 per AHEP4 guide §7 "wide range of media" requirement.
- [x] **First-person voice**: PASS — "I" dominates every paragraph. Almost no passive voice hiding.
- [x] **AI policy (Cat 2 Minimal — personal voice)**: PASS — voice has personality, specific incidents, commit-hash citations, not AI-smooth.

---

## CRITERIA

| Criterion | Score | Reason |
|---|---|---|
| **Teamwork** | **62/100** | Names teammates and cross-team interactions (Robin FSM pushback, Demetro rewriting paperwork, Edward Cube handoff). BUT: no named conflict managed to resolution — the Robin 11-state FSM "pushback" is the closest but it's framed as Robin pushing me, not a conflict I mediated. No leadership-without-title episode that meets the 2-of-5 threshold (decision under disagreement, delegation, influence, accountability, meta-work). "I owned CV and autonomy" = ownership language, not leadership. Conflict management gate (60+) barely scraped via Robin FSM, not clearly enough for confident 65. |
| **Self-management** | **72/100** | Strongest criterion. Names concrete tools: `brain-dump.md`, `MEMORY.md`, `NICE_TO_HAVE.md`, blueprint maintenance, session-workflow. Quantified: 820+ commits, 127 unit tests, modularity audit 3.8/5.0, capability audit 2.1/10, FSM rewrites 4-5x. Past-tense outcomes. Autonomous initiative clearly visible (tests written unprompted, sim-framework built before field day). Hits "autonomous + very good organisation" descriptor cleanly. Does NOT quite hit "outstanding" 83+ because the programme is described but not formally *evaluated against a criterion* (M16.d-own is thin — no explicit "criterion -> judgement -> cause -> lesson" framing). |
| **Insight** | **60/100** | Most honesty items present: capability audit (2.1/10 self-scored), modularity audit, trade-offs acknowledged. BUT: **feedback given to others is thin**. Table 4b mentions writing docs for Robin (VISION_PIPELINE, COLLEAGUE_CHECKLIST) and narrative rewrite for Demetro — these are *artefacts*, not *feedback to a named teammate that changed their behaviour*. No "I told Robin X, their reaction was Y, my delivery was Z, I would do W differently" pattern. No belief-revision move ("I was wrong about..."). No "I now see this is because..." root-cause move. Stays at Hatton Level 3 (descriptive reflection + some dialogic), never reaches Level 4 critical reflection. Caps insight at ~68 per rubric ("no feedback given to others -> CAP 68"). Pulled further down to 60 by lack of changed-thinking moment. |
| **Average** | **64.7/100** | |

---

## BRISTOL L7 HIDDEN CAPS (from AHEP4 guide §7)

- [~] **Conflict managed (60+ gate)**: BORDERLINE PASS — Robin FSM pushback is the only candidate. Framed honestly but not as "I mediated a disagreement to resolution". Weak evidence for the gate; a harsh marker would say FAIL and cap Teamwork at 58.
- [ ] **Leadership evident (70+ gate)**: FAIL — no named episode of decision-authority-under-disagreement, delegation, or influence mechanism. Owned modules = ownership, not leadership. Caps Teamwork at 68.
- [ ] **Peer feedback given (72+ gate for Insight)**: FAIL — no named teammate + specific feedback + reaction + behaviour change. Docs written do not substitute for the feedback-giving pattern from §7 of the Exemplars. Caps Insight at 68 (actually pulled lower by Hatton-level ceiling).
- [ ] **Media diversity (Communication 60+ floor)**: FAIL — only prose + text tables. No figures, screenshots, diagrams, or photos evidenced. Caps Bristol Communication line at 59.

---

## AHEP4 COVERAGE

| Clause | Score | Notes |
|---|---|---|
| M16.1 (individual effectiveness) | **4/5** | Strong: named deliverables, commits, quantified ownership |
| M16.2 (member/leader of team) | **3/5** | Member: yes (handoffs named). Leader: claimed implicitly via "owned CV and autonomy" but no leadership threshold tests met |
| M16.3 (evaluate own performance) | **3/5** | Audits named (modularity 3.8, capability 2.1) but not fully structured as criterion/judgement/cause/lesson — descriptive audit, not evaluation |
| M16.4 (evaluate team performance) | **2/5** | Team evaluation almost absent. One line about team delivering 12/12 sim vs partial real is missing. No team velocity/quality metric |
| M17.1 (communicate complex engineering) | **4/5** | VISION_PIPELINE doc, FDR scripts, D6 section ownership — artefacts named |
| M17.2 (technical audiences) | **3/5** | Robin onboarding doc, Demetro paperwork — technical audiences named, but no confirmed reception evidence beyond "Robin used it" |
| M17.3 (non-technical audiences) | **1/5** | **Near miss** — no named non-technical audience (operator, member of public, funder, journalist). Complaint-letter-to-supervisor could count but is framed as team mechanic not audience adaptation. Pilot as end-user not evidenced. |
| M17.4 (evaluate effectiveness of methods) | **2/5** | Methods listed (docs, scripts, dashboard, reports) but no A/B evaluation, no criterion, no "if I did again..." comparison of methods. Thin. |
| **Total** | **22/40** | ~55%. Borderline Merit/Distinction on AHEP4 alone |

---

## HATTON LEVEL 4 DEPTH

**Paragraphs with "I now see this is because..." move (belief revision, assumption challenge, frame shift): 2/~20**

- §2a "Structure, whether we discussed..." — mild dialogic reflection on team structure emerging organically, but does not name an assumption revised
- §3b "Add/refocus" — "I focused on capability when I should have taught" comes closest to a belief-revision move, but it's in a table cell, not developed

**Missing Level 4 moves:**
- No "The uncomfortable realisation was that..."
- No "I initially framed X as technical — in fact it was communication, because..."
- No "I was wrong about X. [Teammate] was right."
- No "What looked like [X] was actually [Y] because..."
- No identity-shift closing ("I leave this project believing engineering leadership is less about X and more about Y")

**Hatton Level estimate: 2.5 — Descriptive reflection with some dialogic moments. Does NOT reach Level 3 consistently, nowhere near Level 4.**

This is the single biggest mark-impact weakness. Level 3 hits ~68. The draft sits at ~2.5, which aligns with the low 60s.

---

## FAILURE MODES DETECTED (from D7_EXEMPLARS §13)

Scanning the 20 failure modes; items present in V1:

1. **(#2) Generalised teamwork platitudes** — "Regular stand-ups, transparent commits, shared goals" in §2b is a platitude line
2. **(#5) Conflict-free narrative** — closest to a conflict (Robin FSM) is not framed as managed conflict
3. **(#6) Feedback-giving described without named-reaction pattern** — Table 4b lists what I *did for* teammates, not feedback I *gave* with their reaction
4. **(#7) Defensive retracts** — §1a "The explicit/implicit split was stark" then hedges — mild version present
5. **(#9) Tools-and-technologies listing** — Commit hashes and script names risk being read as CV padding (mostly earned by specificity, but borderline)
6. **(#11) Vague future commitments** — §2c "next time I would front-load interface contracts" — no falsifiability test
7. **(#13) Metrics as substitute for reflection** — 820 commits / 127 tests / 4-5 rewrites given but not paired with a reflective move
8. **(#14) Perfect-past syndrome** — §1b narrates what happened as if the plan was always clear
9. **(#15) Feedback-free feedback paragraphs** — §4b claims helping teammates but does not name what was said or how received
10. **(#16) Learning = reflection conflation** — "I learnt X" appears in several cells without showing what changed

**Absent (good):** chronological trap (#1, structure is thematic), hidden self-praise (#3), triumphalism (#8), Gibbs decoration (#10, no Gibbs at all), hiding behind "we" (#12, I-voice strong), closing bullet list (#19), "This report will..." opener (#20).

**Count: ~10 of 20 failure modes present or borderline.** Target for Distinction is <=2.

---

## FINAL SCORE: 64/100

Mark breakdown:
- Teamwork avg: 62
- Self-management avg: 72 (highest)
- Insight avg: 60 (lowest — drags the report)
- Raw average: 64.7
- Minor deduction for media-diversity gate failure applied to communication floor: -1
- **Final: 64**

**Band: upper Merit.** Not Distinction. Close to 65 but nothing to push it over — Insight is genuinely weak and Hatton Level never reaches 4.

---

## TOP 10 FIXES (ranked by mark impact)

1. **[+4 marks] Add one named feedback-giving incident** with the full pattern: "In wkN I told [Robin/Demetro/Edward] that [specific thing]. Their reaction was [honest]. My delivery was [self-critical]. Next time I would [mechanism]." Unlocks Insight 72+ gate. Single highest-leverage fix.
2. **[+3 marks] Add one named conflict managed to resolution** — not a handoff, an actual disagreement where I and another teammate disagreed, I took a specific action, and it resolved. Unlocks Teamwork 65+. The Robin 11-state FSM could be rewritten this way if there was a real disagreement.
3. **[+3 marks] Upgrade 3-4 paragraphs to Hatton Level 4** by adding explicit "I now see this is because..." / "I was wrong about..." / "What looked like a technical problem was actually..." moves. Push the draft from descriptive to critical reflection.
4. **[+2 marks] Add a non-technical audience episode for M17.3** — name the audience (pilot as end-user? open-day visitor? the letter-to-supervisor reframed as audience adaptation?), show the jargon-removal/analogy/visual substitution move, and report reception.
5. **[+2 marks] Add one figure or screenshot** to break the media-diversity cap on Communication. Even a single dashboard screenshot or pipeline diagram would unlock the 60+ floor per Bristol criteria.
6. **[+2 marks] Formalise M16.d evaluation** — pick one criterion (velocity, bug rate, mAP, milestone hit-rate), state target, state actual, state cause, state lesson. Currently audits are named but not structured as evaluations.
7. **[+1 mark] Add a belief-revision/identity-shift closing** — replace the current closing with "I entered this project thinking X; I leave it thinking Y; the moment this became clear was [incident]." High-leverage per Exemplars §9.
8. **[+1 mark] A/B comparison of one communication method** — "For Robin I tried prose docs vs the COLLEAGUE_CHECKLIST vs live walkthrough; X worked best per unit effort because Y." Unlocks M17.4.
9. **[+1 mark] Falsifiability tests on future commitments** — every "next time I would X" should add "and the way I will know it is working is Y".
10. **[+1 mark] Cut one platitude line per page** — especially §2b "regular stand-ups, transparent commits, shared goals" which scans as generic teamwork filler. Replace with a specific incident that shows the same mechanism.

**Cumulative ceiling if all 10 applied:** ~78. Realistic aim: hit 72-74 via items 1-5.

---

## Scorer note

V1 is structurally compliant (4 headings, 10 questions, specifics, readable, I-voice, honest) but reflectively shallow. It is a very good *Merit* draft masquerading as a Distinction draft through good presentation. The distance to 70+ is not more content — it is upgrading existing paragraphs to Level 4 reflection and adding the feedback/conflict/non-technical-audience items the rubric treats as hidden gates.
