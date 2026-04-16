# D7 AHEP4 M16 & M17 Evidence Guide

**Purpose:** actionable breakdown of what AHEP4 M16 (Teamwork) and M17 (Communication) require at Master's (Level 7), what evidence hits each sub-clause, how Bristol's Level 7 marking criteria layer on top, and how a D7 reflective report commonly fails to meet them. Feeds the final D7 scoring rubric.

**Sources (verbatim, fetched 2026-04-11):**
- AHEP4, *The Accreditation of Higher Education Programmes*, 4th ed., Engineering Council, pp. 32-37 (CEng Master's column).
- University of Bristol, *University marking criteria: level 7*.

---

## 1. Verbatim Learning Outcomes (AHEP4 p. 36-37)

### M16 Teamwork
> "**M16.** Function effectively as an individual, and as a member or leader of a team. Evaluate effectiveness of own and team performance."

Bachelors equivalent (C16): "Function effectively as an individual, and as a member or leader of a team." — **The *Evaluate effectiveness of own and team performance* clause is the Master's-only increment.** This is the clause that separates a 60+ mark from a 50+ mark for an AHEP-accredited MSc D7.

### M17 Communication
> "**M17.** Communicate effectively on complex engineering matters with technical and non-technical audiences, evaluating the effectiveness of the methods used."

Bachelors equivalent (C17): "Communicate effectively on complex engineering matters with technical and non-technical audiences." — **The *evaluating the effectiveness of the methods used* clause is the Master's-only increment.** Again, this is the differentiator.

**Headline takeaway:** In both outcomes the *evaluation* clause is the Master's step-up. A D7 that merely *describes* what happened is Bachelor-level. A D7 that *evaluates effectiveness of the methods/performance* — with evidence, judgement, and identified improvements — is Master-level.

---

## 2. M16 — Sub-clause Breakdown

M16 decomposes into **four** sub-clauses. Each must be evidenced separately.

### M16.a — "Function effectively as an individual"
**What it requires:** evidence that the student personally delivered discrete, owned work to a professional standard, managed their own time/task load, and produced tangible outputs attributable to them (not "the team").

**Evidence that hits it (2-3 examples):**
1. "I owned the vision subsystem (`vision.py`, 312 lines) end-to-end from model selection through Pi deployment. Between Feb 16 and Mar 31 I delivered [X commits], [Y bug fixes], and closed [Z] issues from the backlog." — personal ownership, quantified.
2. "On 11 Mar I independently diagnosed a TFLite bbox coordinate bug (pixel-vs-normalised) that had been causing off-screen detection boxes for two weeks; the fix (`PIXEL_COORD_THRESHOLD` check) took 40 min after 3 h of investigation." — specific individual contribution with timing.
3. "I maintained my own Gantt (dashboard/wbs-data.ts), updated after every session, and hit 8/10 personal milestones on or before the internal deadline." — self-management evidence.

**Tick-box vs deep:** Tick-box. One paragraph with quantified ownership + one specific incident suffices. Examiners are looking for *existence* of individual contribution, not depth.

**Common failure:** Generic "I contributed to the team" with no tangible deliverable, no file names, no dates. Reads as passive participation.

### M16.b — "As a member ... of a team"
**What it requires:** evidence that the student interacted productively inside a team structure — attended meetings, responded to others' work, integrated across interfaces, handled dependencies.

**Evidence that hits it:**
1. "I consumed the mechanical team's CAD release v3.2 on 4 Mar and adapted the camera mount offset in `config.py` within 48 h; I flagged a clearance issue on the gimbal in the Slack #hardware channel that was fixed in v3.3." — cross-boundary collaboration.
2. "Weekly stand-ups (every Tuesday, 12 meetings) — I prepared a 1-slide status each time and took minutes for 4 of them when the PM was unavailable." — regular team participation.
3. "I paired with [teammate] on the GPS estimation module for 3 h on 20 Mar — we found two integration bugs that neither of us had seen alone." — collaboration specifics.

**Tick-box vs deep:** Tick-box. Pick one or two concrete collaborations; avoid generic "team meetings went well".

**Common failure:** "We had regular meetings and communicated well" — zero evidence. Examiner cannot verify.

### M16.c — "... or leader of a team"
**What it requires:** AHEP4 uses "or" — strictly, a student does **not** need to have been a formal team leader to satisfy M16. But if the D7 claims leadership, the threshold is higher. See Section 5 below for the leadership threshold.

**Evidence that hits it (if claimed):**
1. Owning a workstream (e.g. "CV lead") with **decision authority** — chose model architecture, set the threshold, made the model-swap call on flight day. Others deferred to your call.
2. Running a sub-meeting or review (e.g. led the CV code review on 3 Apr, wrote the review agenda, assigned action items).
3. Resolving a conflict — two teammates disagreed on [X], you proposed a compromise, it was adopted.
4. Recruiting/onboarding — wrote `docs/COLLEAGUE_CHECKLIST.md` so a new team member (Robbin) could contribute independently within 2 days.

**Tick-box vs deep:** **Deep** if claimed. If you say "I led" you must show delegation, decision, and outcome. Otherwise drop the word and just say "owned" or "was responsible for".

**Common failure:** Calling oneself a leader because one owned a module. Leadership requires influencing *others'* behaviour.

### M16.d — "Evaluate effectiveness of own and team performance" (MASTER'S INCREMENT)
**What it requires:** This is the most important clause in M16 for Level 7 marks. It demands:
- (i) A **criterion** or **measure** for what "effective" means (velocity, bug rate, commitment hits, satisfaction, external feedback, milestone delivery).
- (ii) A **judgement** against that criterion — how did you/the team actually score?
- (iii) A **causal explanation** for why it scored that way.
- (iv) A **lesson or change** arising from the evaluation.

**Evidence that hits it:**
1. **Own performance:** "I targeted 4.8 FPS Pi inference by 15 Mar (config baseline). Actual: 4.8 FPS on 11 Mar (ahead of schedule) but only after I abandoned the NCNN backend attempt on 8 Mar which cost 2 days. The evaluation: technically-on-target but 30% of my time went to a detour I should have scoped with a 2 h spike first. Lesson applied on 30 Mar: I now timebox all backend experiments to 4 h before committing." — criterion (FPS + time), judgement (partial), cause (premature commitment), lesson.
2. **Team performance:** "The team's velocity (WBS tasks closed per week) was 7, 5, 4, 9, 11 — a mid-project dip in weeks 3-4. Root cause: hardware dependency between CV and mechanical unblocked only after the mount release. We evaluate this as a coordination failure, not an effort failure. Fix: in future projects we would front-load interface contracts before parallel work begins." — quantified, causal, forward-looking.
3. **Both at once:** "Against the D6 requirements matrix (12 Rs), the team delivered 12/12 in simulation but only 4/12 in real hardware. Individually I delivered 9/12 of the vision-related Rs. The gap is primarily the flight cancellation on 11 Mar — an external factor — but 3 of the gaps (R02, R06, R11) were work we could have done on the bench and did not prioritise. Evaluation: the team underweighted bench work relative to code." — uses the project's own scoring framework as the criterion.

**Tick-box vs deep:** **Deep — this is where the marks live.** Aim for one paragraph on *own* evaluation and one on *team* evaluation, each containing all four elements (criterion, judgement, cause, lesson).

**Common failure:** "The team worked well together. We learnt a lot." — no criterion, no judgement, no cause, no lesson. This is the single biggest reason D7 reflections score in the 50s rather than 70s.

---

## 3. M17 — Sub-clause Breakdown

M17 decomposes into **four** sub-clauses.

### M17.a — "Communicate effectively on complex engineering matters"
**What it requires:** evidence that the student conveyed technically non-trivial content accurately. "Complex" is AHEP's key term — if the thing you communicated could have been communicated at A-level, it doesn't count.

**Evidence that hits it:**
1. "I wrote `docs/VISION_PIPELINE_FOR_COLLEAGUE.md` (2,400 words) explaining the full TFLite → undistortion → GPS projection chain including the BGR/RGB pitfall and the focal-length calibration procedure. Robbin used it to deploy the model independently on 4 Apr." — artefact, audience, outcome.
2. "Group Technical Report (D6) CV section — I authored §4.3 (model retraining workflow) covering dataset v2 augmentation, Colab training loop, and mAP50 validation methodology." — specific ownership inside a team artefact.

**Tick-box vs deep:** Tick-box *if* the artefact exists and is technically substantive.

### M17.b — "...with technical ... audiences"
**What it requires:** audience = other engineers / subject experts. Evidence they understood and acted.

**Evidence that hits it:**
1. Supervisor review comments on your section ("clear", "well-scoped", etc.) — direct acknowledgement from a technical expert.
2. A teammate who was able to pick up your module from the documentation alone.
3. A code review where reviewers asked clarifying questions that your reply closed out.

**Tick-box vs deep:** Tick-box. You are an engineering MSc student — most of your output is already for technical audiences.

### M17.c — "...and non-technical audiences" (OFTEN THE WEAK POINT)
**What it requires:** audience with no engineering background. This is **not** "another engineer in a different sub-discipline". It is a hiring manager, a member of the public, an end-user (e.g. SAR operator), a client, a journalist, a grant reviewer. See Section 6 for the threshold.

**Evidence that hits it:**
1. "The project dashboard (`dashboard/`) was designed for external stakeholders: no jargon on the landing page, status expressed as %complete and RAG, with technical depth behind expandable panels. Tested with [named non-technical person] on [date] who understood the mission status in under 2 min." — explicit audience adaptation.
2. Demo video / elevator pitch / poster for a general audience with evidence of audience reaction.
3. Re-writing a technical section for a lay summary — and being able to point to both versions.

**Tick-box vs deep:** **Deep.** This is the clause that is most often missed. The D7 must explicitly name a non-technical audience, the artefact used, the adaptation made (what jargon was stripped, what analogies added), and ideally a reaction.

**Common failure:** Claiming the report abstract is "for a non-technical audience" — it isn't; it's for examiners who are technical. No evidence of audience adaptation.

### M17.d — "Evaluating the effectiveness of the methods used" (MASTER'S INCREMENT)
**What it requires:** This is the Level-7 step-up for M17. It demands:
- (i) Identification of the **methods** you chose (report, demo, slide deck, README, dashboard, live meeting, video, code comments, diagram).
- (ii) A **criterion** for effectiveness per method (comprehension, action taken, feedback rating, time-to-understanding, revision count).
- (iii) A **judgement** for each (what worked, what didn't).
- (iv) A **comparison or alternative** — if you did it again, which method would you use and why.

**Evidence that hits it:**
1. "I used three methods for the CV section: (a) narrative prose in the D6 report; (b) annotated pipeline diagram (Fig. 4.3); (c) live demo on Pi at the 20 Mar review. Evaluated against teammate comprehension (informal Q&A): prose produced 3 follow-up questions, diagram 0, demo 2 (both about edge cases). The diagram was most effective per minute of author effort (~45 min to produce). Prose was least effective relative to its cost (~3 h). If I repeated, I would front-load the diagram and let prose support it." — enumerated methods, criterion, judgement, lesson.
2. "For the non-technical audience (prospective operator), I tested two versions of the one-page capability summary: v1 (technical pass-through, rejected by [tester]) and v2 (scenario-led with a photo, understood in 90 s). Evaluation: scenario framing beat feature list for this audience." — A/B style evaluation.
3. "The brain-dump.md capture method was highly effective for idea retention (zero ideas lost across 45 sessions) but ineffective for prioritisation — I compensated by adding `NICE_TO_HAVE.md` with explicit impact/effort scores on 11 Mar. Lesson: capture and prioritisation are separate methods and need separate tools." — reflective evaluation of own method choice.

**Tick-box vs deep:** **Deep — this is where the M17 marks live.** Without it you cap at B-level on this outcome.

**Common failure:** "I used a report, slides and a demo to communicate the work." — no evaluation, no criterion, no comparison. Descriptive, not evaluative.

---

## 4. "Evaluate effectiveness" vs "Reflect on effectiveness" — the Difference that Matters

These are NOT synonyms. Many students write reflections and assume they count as evaluations. They don't.

| Dimension | Reflect | Evaluate (AHEP4 M16/M17) |
|---|---|---|
| Mode | Introspective, subjective | Judgemental against a criterion |
| Evidence | Feelings, impressions, anecdote | Measures, counts, ratings, outcomes |
| Output | "I felt that ..." / "I noticed that ..." | "Against [criterion], X scored Y because Z" |
| Direction | Looking back | Looking back **and** forward-actionable |
| AHEP4 level | Bachelor (descriptive) | Master (judgemental) |
| Bristol L7 equivalent | "Some evidence of capacity to plan self-development" (50-59) | "Effective programme of self-development" (70-79) |

**Rule of thumb:** If you delete your sentence and it contains no verifiable claim — just a feeling — it is reflection, not evaluation. Upgrade by adding: (a) a measure, (b) a comparison, (c) a consequence.

**Example upgrade:**
- Reflect (Bachelor): "I think my communication improved during the project."
- Evaluate (Master): "My first D5 draft received 7 reviewer comments on clarity; my third draft received 1. The improvement came from adopting the 'claim-evidence-warrant' paragraph structure I learned from the 16 Mar review. I have since applied the same structure to D6 §4.3 and D7 §2."

---

## 5. "Leadership" — the Threshold Test for M16

AHEP4 says "member **or** leader" — either suffices. But if you claim leadership, here is the evidence floor a Level-7 examiner expects:

**Leadership requires at least TWO of:**
1. **Decision authority** — you made a call that bound the team (choice of architecture, tool, deadline, scope cut).
2. **Delegation** — you assigned work to named others and it got done.
3. **Influence under disagreement** — someone disagreed, you persuaded (not overruled).
4. **Accountability for group outcome** — your name attached to deliverables that were not solely yours.
5. **Meta-work** — you improved how the team worked (process change, new tool, onboarding doc), not just what they produced.

**Not leadership (do NOT claim as leadership):**
- Being the most active contributor.
- Knowing the most about a sub-topic.
- Volunteering for tasks.
- Being the "CV person" with no authority over others' CV work.

**Safer language if threshold not met:** "I owned", "I was responsible for", "I drove", "I championed" — these claim ownership without claiming leadership and cannot be marked down for lack of evidence.

**Evidence pattern when claimed:** Name the decision, name the people affected, name the outcome, name the alternative path. E.g. "On 16 Mar I decided the team should move from the 640x640 dataset to 1088x1088 despite the +6 h training cost; this required [teammate] to redo the data pipeline. Outcome: mAP50 0.87 → 0.995, justifying the call."

---

## 6. "Communicate effectively with non-technical audiences" — the Threshold Test for M17

This is the single clause most D7 reports fail outright. The examiner is looking for evidence that you **adapted your communication to a genuinely non-technical audience**.

**Non-technical audience MUST be:**
- Someone with no engineering degree AND
- Someone with a real stake/reason to understand (not just "my grandmother") AND
- Someone external to your own team (your team is technical)

**Acceptable non-technical audiences for a SAR drone project:**
- A SAR end-user (mountain rescue volunteer, coastguard operator).
- A funder / grant reviewer from a non-engineering background.
- A member of the public at an open day.
- A journalist covering robotics.
- A university communications officer writing a press release.
- A regulator (non-engineer) assessing safety case.
- A potential teammate from a non-engineering discipline (e.g. a psychology student).

**Adaptation evidence required — at least TWO of:**
1. **Jargon removal** — show before/after (e.g. "mAP50" → "accuracy score on the test images"). Best demonstrated with a side-by-side in the report.
2. **Analogy / framing** — what you used in place of a technical mechanism ("the drone sees the dummy the way a human glance does — quickly but not always reliably").
3. **Visual substitution** — replacing a graph with a photo, a pipeline with a scene.
4. **Audience-first structure** — leading with "why it matters" not "how it works".
5. **Feedback loop** — you showed a draft, got a reaction, revised. Cite the reaction.

**Evidence pattern when claimed:** Name the audience, name the artefact, show one concrete adaptation, report the reception.

**Common failure:** "The introduction is written for a general audience." — examiner cannot verify. There is no evidence of adaptation from a technical baseline.

---

## 7. Bristol Level 7 Generic Marking Criteria — What They Add to AHEP4

AHEP4 defines *what* must be evidenced. Bristol Level 7 defines *how well*, mapped to mark bands. Relevant categories for a D7 reflection are **Teamwork**, **Insight**, **Communication**, and **Decision-making** (all from the "Professional and life skills" section) plus **Logical argument** (Intellectual skills). Verbatim descriptors:

### Teamwork (BSP 5a, 5b, 5c, 6a)
| Band | Descriptor |
|---|---|
| 40-49 | Shows limited ability to work within a team setting. |
| 50-59 | Shows ability to work with others and contribute productively as a member of a team. |
| 60-69 | Works effectively within a team, recognising the value and contributions of others. Able to manage conflict. |
| 70-79 | Consistently demonstrates effective teamworking **and leadership skills** and able to ensure teams work effectively to meet their obligations and goals. Able to manage conflict. |
| 80-100 | Shows outstanding ability to **work and lead** a team with creativity and flexibility that is responsive to group members' interests and the obligations and goals of the team. Able to manage conflict. |

**Key addition beyond AHEP4:** Bristol makes **conflict management** a named evidence requirement from 60 upward, and **leadership** from 70 upward. AHEP4 leaves leadership optional; Bristol makes it a first-class criterion for 70+.

**Implication for D7:** To hit the 70+ band on Bristol's Teamwork line, the D7 must explicitly evidence at least one episode of (a) conflict management AND (b) leadership/driving team effectiveness.

### Insight (BSP 7b, 8a, 8b) — this is where self-evaluation lives
| Band | Descriptor |
|---|---|
| 40-49 | Displays limited awareness of own strengths or weaknesses. |
| 50-59 | Shows some ability to identify own strengths and weaknesses. Some evidence of capacity to plan self-development. |
| 60-69 | Confident in self-reflection and expressing own strengths and weaknesses and able to take a proactive approach to self-development. |
| 70-79 | Demonstrates ability to work autonomously and assess own strengths and weaknesses. Demonstrates ability to identify and **implement an effective programme of self-development**. |
| 80-100 | Shows confidence in working autonomously and setting own goals. Can assess own strengths and weaknesses. Able to identify and implement an effective programme of self-development. **Can provide effective feedback to others to aid their self-development.** |

**Key addition beyond AHEP4:** Bristol promotes self-evaluation from *existence* (60s: "confident in reflection") to *implementation* (70s: "implement an effective programme of self-development") to *peer development* (80s: "effective feedback to others"). The 70 → 80 jump requires evidence of **helping others improve**.

**Implication for D7:** For 70+, do not just say "I learnt X" — say "I learnt X, then I did Y in response, and the measurable improvement was Z". For 80+, also show you gave feedback that helped a teammate improve.

### Communication (BSP 5b, 9a)
| Band | Descriptor |
|---|---|
| 40-49 | Shows limited awareness of the ways communication needs to be adapted for different audiences. |
| 50-59 | Shows some awareness of ways that communication needs to be adapted for different audiences. |
| 60-69 | Can communicate effectively to a range of audiences, using a wide range of media as appropriate. |
| 70-79 | Can communicate effectively to a range of audiences, using a wide range of media as appropriate. |
| 80-100 | Can communicate effectively to a range of audiences in an **engaging and professional manner**, using a wide range of media as appropriate. |

**Key addition beyond AHEP4:** Bristol introduces **"a wide range of media"** as a 60+ requirement. A D7 that only evidences the written report cannot exceed 59 on this line. Evidence of 2+ distinct media (report, diagram, code/README, demo, slide, video, dashboard, face-to-face) is a floor for 60+.

**Note:** 60-69 and 70-79 share the same descriptor text in the Bristol document — the differentiation comes from the AHEP4 *evaluation* clause (M17.d). A Level-7 D7 in the 70s is one that is effective across multiple media **and** evaluates the effectiveness of each.

### Decision-making (BSP 8a, 9c)
| Band | Descriptor |
|---|---|
| 60-69 | Confident in adapting to changing and unfamiliar or challenging circumstances and making evidence-based decisions. |
| 70-79 | Confident in adapting to changing and unfamiliar/challenging circumstances and making **effective, evidence-based decisions**. |
| 80-100 | Shows confidence and creativity in adapting to changing and unfamiliar/challenging circumstances. |

**Implication for D7:** The flight-day cancellation on 11 Mar is a textbook "unfamiliar/challenging circumstance". The D7 should narrate at least one evidence-based decision made in response (e.g. pivot to bench testing, revised scope, model retraining on existing video footage instead of new flight data).

### Logical argument (Intellectual skills — most relevant Intellectual line for a reflection)
| Band | Descriptor |
|---|---|
| 50-59 | Ability to develop a logical argument, with some critical consideration of appropriate evidence. |
| 60-69 | Ability to create coherent substantiated arguments. Ability to consider, critically evaluate and use alternative perspectives. |
| 70-79 | Ability to comprehensively consider, critically evaluate and synthesise complex and unfamiliar information and ideas. |

**Implication for D7:** Every major claim in the reflection must be supported by evidence and should consider an alternative interpretation ("one reading is X; an alternative is Y; I conclude X because ..."). A single-perspective narrative caps at 59.

---

## 8. Mapping: Common D7 Content Types → M16/M17 Coverage

| D7 content type | M16.a indiv | M16.b member | M16.c leader | M16.d evaluate | M17.a complex | M17.b technical | M17.c non-tech | M17.d evaluate |
|---|---|---|---|---|---|---|---|---|
| "What I did" module ownership narrative | YES | partial | no | no | partial | no | no | no |
| Gantt / milestone hit-rate table | YES | no | no | YES | no | no | no | no |
| Cross-team interface episode | partial | YES | no | partial | YES | YES | no | no |
| Conflict / disagreement resolution | no | YES | YES (if led) | YES | partial | YES | no | no |
| Decision-authority episode | partial | no | YES | YES | partial | YES | no | no |
| Code review given/received | YES | YES | partial | YES | YES | YES | no | YES |
| Documentation artefact for teammate (VISION_PIPELINE etc.) | YES | YES | partial | no | YES | YES | no | partial |
| Dashboard / public-facing summary | no | no | no | no | partial | partial | YES | partial |
| Before/after jargon-removal demo | no | no | no | no | partial | no | YES | YES |
| A/B comparison of two comms methods | no | no | no | YES | YES | YES | partial | YES |
| Quantified velocity / bug rate / mAP metric over time | YES | YES | no | YES | no | no | no | no |
| Lesson-learnt with applied change and outcome | YES | partial | no | YES | no | no | no | partial |
| Non-technical demo + witnessed reaction | no | no | no | no | no | no | YES | YES |

**Reading the table:** if a D7 contains only the first five rows, it will cover M16.a-c well, leave M16.d thin, and largely miss M17.c and M17.d. Adding rows 8-13 is usually what lifts a D7 from the 50s/60s to the 70s.

---

## 9. Rubric Hooks — Scoring Checklist for the Writer Agent

Score each line 0-3. Sum drives the M16/M17 band judgement.

### M16 (AHEP4 Teamwork)
- [ ] **M16.a** One specific individual-contribution incident with file/date/metric — `0 / 1 / 2 / 3`
- [ ] **M16.b** One specific cross-team collaboration with named interface and outcome — `0 / 1 / 2 / 3`
- [ ] **M16.c** EITHER leadership episode meeting 2+ threshold tests OR ownership language used honestly — `0 / 1 / 2 / 3`
- [ ] **M16.d-own** Self-evaluation with criterion + judgement + cause + lesson — `0 / 1 / 2 / 3`
- [ ] **M16.d-team** Team-evaluation with criterion + judgement + cause + lesson — `0 / 1 / 2 / 3`
- [ ] **Bristol Teamwork 70+** Conflict management episode named — `0 / 1 / 2 / 3`
- [ ] **Bristol Insight 70+** Implemented self-development programme with measurable improvement — `0 / 1 / 2 / 3`

### M17 (AHEP4 Communication)
- [ ] **M17.a** Complex engineering content communicated (artefact + technical substance) — `0 / 1 / 2 / 3`
- [ ] **M17.b** Technical audience named with confirmed reception — `0 / 1 / 2 / 3`
- [ ] **M17.c** Non-technical audience named, adaptation shown (2+ of: jargon removal / analogy / visual sub / structure / feedback loop) — `0 / 1 / 2 / 3`
- [ ] **M17.d** Evaluation of methods: enumerated methods + criterion + judgement + comparison/alternative — `0 / 1 / 2 / 3`
- [ ] **Bristol Comms 60+** ≥2 distinct media evidenced — `0 / 1 / 2 / 3`
- [ ] **Bristol Comms 80** Engaging/professional manner with reception evidence — `0 / 1 / 2 / 3`

### Level-7 quality multipliers (apply across both)
- [ ] Every claim has evidence (no unbacked assertions) — `0 / 1 / 2 / 3`
- [ ] At least one alternative-perspective consideration ("one reading is ... another is ...") — `0 / 1 / 2 / 3`
- [ ] Forward-looking lesson tied to a named future context (next project, career, CPD) — `0 / 1 / 2 / 3`

**Banding guide (heuristic):**
- Sum 0-14 → 40s (limited)
- Sum 15-24 → 50s (sufficient, Bachelor-level evaluation missing)
- Sum 25-34 → 60s (Master evaluation present but uneven)
- Sum 35-42 → 70s (both M16.d and M17.d landed, Bristol criteria 70-band hit on teamwork AND insight AND communication)
- Sum 43+ → 80s (adds peer-development evidence, engaging delivery, outstanding leadership)

---

## 10. Top 10 Failure Modes (watch for these in the draft)

1. **Descriptive narrative with no criterion.** "The team worked well." → missing M16.d.
2. **Leadership claimed without evidence.** "I led the CV workstream" with no decision/delegation/influence episode → downgrade to "owned".
3. **Non-technical audience = another engineer.** → M17.c not actually hit.
4. **Report abstract treated as non-technical comms.** → No adaptation from baseline; does not hit M17.c.
5. **Methods listed but not evaluated.** "I used report, slides, demo." → misses M17.d.
6. **Feelings substituted for evaluation.** "I felt I communicated well." → Bachelor level.
7. **Single-medium communication.** Only the written report cited → caps Bristol Comms at 59.
8. **Lessons with no applied consequence.** "Next time I would ..." with no evidence it was applied within the project timeline.
9. **No conflict / no challenge narrative.** No episode of friction, no demonstration of resilience or decision-making under pressure → caps Bristol Decision-making at 59.
10. **No peer-development evidence.** Never gave feedback to a teammate that improved their work → cannot exceed 79 on Bristol Insight.

---

## 11. Quick-Reference: Evidence the D7 Should Contain (minimum set for a 70+ mark)

A 70+ D7 should contain at least the following twelve named evidence items:

1. One quantified individual-delivery metric (files, commits, tests, milestones hit).
2. One specific cross-team collaboration with named interface.
3. One decision made under disagreement or uncertainty (flight cancellation, model swap, threshold tuning).
4. One conflict or friction episode and its resolution.
5. One self-evaluation paragraph with criterion + judgement + cause + lesson.
6. One team-evaluation paragraph with the same structure.
7. Two distinct communication media used, each with an audience named.
8. One non-technical audience named, with a concrete adaptation evidenced.
9. One A/B or before/after comparison of communication methods.
10. One peer-development action (feedback given, doc written for onboarding, code review).
11. One applied lesson with measurable outcome inside the project timeline.
12. One forward-looking CPD or career plan tied to an identified weakness.

If the draft lacks any of items 5, 6, 8, or 9 it will not reach 70. These four are the load-bearing items.

---

## 12. Key Verbatim Quotes — Ready to Cite in the Rubric

For the writer agent to reference directly:

> AHEP4 M16: "Function effectively as an individual, and as a member or leader of a team. Evaluate effectiveness of own and team performance." (AHEP4 p. 36)

> AHEP4 M17: "Communicate effectively on complex engineering matters with technical and non-technical audiences, evaluating the effectiveness of the methods used." (AHEP4 p. 37)

> Bristol L7 Teamwork 70-79: "Consistently demonstrates effective teamworking and leadership skills and able to ensure teams work effectively to meet their obligations and goals. Able to manage conflict."

> Bristol L7 Insight 70-79: "Demonstrates ability to work autonomously and assess own strengths and weaknesses. Demonstrates ability to identify and implement an effective programme of self-development to improve practical and professional skills."

> Bristol L7 Communication 60-69 / 70-79: "Can communicate effectively to a range of audiences, using a wide range of media as appropriate."

> Bristol L7 Decision-making 70-79: "Confident in adapting to changing and unfamiliar/challenging circumstances and making effective, evidence-based decisions."

---

*End of guide. Hand to writer agent and scoring rubric builder.*
