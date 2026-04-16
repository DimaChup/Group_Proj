# D7 HARSH SCORE — personal_v2/main.pdf (initial)

**Date:** 2026-04-11
**Rubric:** `report/personal_v2/D7_SCORING_HARSH.md`
**Target file:** `report/personal_v2/main.pdf` (rendered pages `report/report_d7_pages/page_01..08.png`)

---

## D7 HARSH SCORE: **42/100**

---

## HARD GATES

| Gate | Result |
|------|--------|
| Page limit <=5 body | **FAIL** — 7 pages of body + 1 references page = 8 total. Body alone is 7pp (Introduction on p.1, Section 2 on p.1–2, Section 3 on p.3, Section 4 spans p.3–5, Section 5 spans p.6–7). Cap applied: **48**. |
| 4 required headings (My role / My team / My impact / My support) | **FAIL** — none present. Current headings are Introduction / Design and Problem-Solving / Societal and Environmental Impact / Teamwork, Leadership, and Communication / Self-Assessment and Development. This is the OLD D6-style AHEP-mapped structure, not the Release 2.2 D7 brief. Cap applied: **58**. |
| 10 required questions answered | **2/10** (see question coverage below). |
| First-person authenticity | **FAIL** — large tracts read as project summary ("The team functioned effectively..."), not personal reflection. Cap risk: **52**. |
| Specific named incidents / named people | **FAIL** — zero teammates named, zero dated incidents, no conflicts managed. Cap applied: **58**. |
| Honesty (weaknesses + critique) | PARTIAL — §5.4 names two weaknesses ("designing for collaboration", "speed over inclusion") but both are abstract and neither has a remediation outcome. |
| AI policy (personal voice) | PARTIAL-FAIL — tone is smooth, neutral, hedged, and generic ("I recognise this as a leadership gap"). Reads like polished AI prose with a thin first-person veneer. Cap risk: **48**. |
| Evidence (5+ concrete specifics) | FAIL — technical facts exist (CEP50=2.3 m, 41 scripts, 15k LOC, mAP50=0.995) but no human/process specifics. Cap applied: **62**. |

**Binding caps:** page overrun (48), heading mismatch (58), no specifics (58), AI-tone risk (48). **Lowest binding cap = 48.**

---

## CRITERIA

### Teamwork: **44/100**
The report talks about "the team" abstractly. No teammate is named. No conflict is described or managed. §4.4 "Managing Disagreements" discusses an architectural disagreement (single Cube workload vs Pi offload) but frames it as "the team" resolving it through "honest technical accounting" — no role for the author as mediator, no named counterpart, no outcome attributable to the author's intervention. §4.3 ("Solo Coding Reality") actually argues the author worked alone on software ("I ended up as the de facto single point of failure"), which undermines teamwork evidence rather than demonstrating it.
Band: **42–48** ("limited ability"). No evidence of conflict management, leadership, or recognising others' value by name. Cannot exceed 58 per rubric harsh checkpoint ("no named teammate contribution recognised").

### Self-management: **52/100**
There are traces: "I structured my work around weekly milestones aligned with the project timeline. Weeks 12–15 focused on simulation, Weeks 16–18 shifted to Pi deployment..." and a "What's Not Done Yet" list. But no named tracking tool (brain-dump.md, NICE_TO_HAVE.md, blueprints — all of which exist in the repo and are unmentioned!), no self-imposed deadline vs team deadline, no autonomous-recovery story with measurable outcome. The "Skills Developed" section is a list of technical topics (MAVLink, Pi deployment, AI deployment), not self-management evidence.
Band: **52–58** ("some evidence, completes most tasks on time"). Autonomous-initiative stories absent → cannot reach 68+.

### Insight: **48/100**
§5.3 Strengths and §5.4 Weaknesses exist, but weaknesses are abstract ("designing for collaboration", "choose speed over inclusion"). §5.5 is a 3-item self-development programme — but every item is future tense ("will define", "will establish", "will practise"). A development programme the student **has not yet executed** doesn't count as evidence for an insight band above 58 (rubric: "weaknesses listed but no plan to address → CAP 58" — this is one notch better because a plan exists, but with zero outcomes). No feedback given to others that changed their behaviour. No "changed thinking" story. §4.6 claims "I provided technical feedback" but gives no specific feedback, no recipient, no behaviour change.
Band: **52–58** (some self-development, identifies strengths/weaknesses). Cannot reach 68+ (feedback-to-others absent).

**Unweighted average: (44 + 52 + 48) / 3 = 48**

---

## QUESTION COVERAGE: 2/10

| Q | Topic | Verdict | Reason |
|---|-------|---------|--------|
| 1a | Roles explicit vs implicit, did they change? | **PARTIAL (0.5)** | §4.1 says "software and computer vision lead", "hardware lead" existed, but doesn't contrast explicit vs implicit allocation or discuss how the author's role changed over the project. |
| 1b | Most proud of? | **WEAK (0.5)** | §5.3 mentions "rapid prototyping and system integration" as strengths, but "most proud of" is not explicitly addressed. |
| 1c | Focus differently in future? | **MISSING** | Generic "choose speed over inclusion" line but no concrete future-focus shift. |
| 2a | Team structure, discussed explicitly? Changed? | **MISSING** | No description of how the team agreed its structure, no discussion of whether this was revisited. |
| 2b | Most impactful team-working elements? | **PARTIAL (0.5)** | §4.5 lists communication channels (simulator, docs, ground station, meetings) — but these are author's artefacts, not team-working practices. |
| 2c | What would you change next time? | **PARTIAL (0.5)** | §4.2 "What Worked Well" flips into a one-line "teammates lead exam-constrained" observation; §5.5 item 1 ("collaborative architecture design") is adjacent but forward-looking. |
| 3a | How did your contributions drive the team? | **MISSING** | Contributions listed (simulator, pi_flight, passive_watch) but not framed as "how they drove the team". §4.3 actually says they fostered dependency, not drive. |
| 3b | Add/refocus in future? | **PARTIAL (0.5)** | §5.5 development programme items 1–3. Forward-looking; no past evidence. |
| 4a | What did others do that helped you? | **MISSING** | Not addressed. Project manager briefly mentioned in §4.4 parenthetical ("project manager's logistical contributions") but no story. |
| 4b | What did you do that helped others? | **WEAK (0.5)** | §4.6 "I provided technical feedback" — vague, no recipient, no outcome. |

**Question score: ~2/10.** Penalty at 3 marks per missing: 8 missing or weak × 3 = 24, capped at **-15**.

---

## PENALTIES

| Penalty | Amount |
|---------|--------|
| Page overrun (>5 body pages) | binding cap 48 |
| Heading mismatch (none of 4 required) | binding cap 58 |
| No named specifics (people/dates/conflicts) | binding cap 58 |
| AI-tone / generic prose | risk cap 48 |
| No feedback given to others | -5 (within criterion) |
| No conflict managed | -5 (within criterion) |
| Missing 8 of 10 questions | -15 (capped) |
| Evidence floor (fewer than 5 human-specific anchors) | cap 62 |

**The lowest binding cap is 48 (page overrun + AI tone).** Raw criterion average (48) meets the cap but question-coverage penalty pulls further.

Pre-penalty: 48 (criterion average)
Post question penalty: 48 − 15 = 33... but criterion scores already reflect missing content. To avoid double-counting, apply the page cap of 48 as ceiling and subtract only the half of the question penalty that is NOT already baked into criterion bands: **-6**.

**FINAL SCORE: 48 − 6 = 42/100.**

This is firmly in the **Limited (42–48)** band for Level 7: the reader can see effort and competence, but the document does not meet the D7 brief's structural or evidentiary bar.

---

## WHERE IT FALLS IN EACH BAND (plain-English)

- **Teamwork:** Bottom of "Limited ability". No conflict, no named teammate, no leadership anecdote. The "Solo Coding Reality" section actively argues against a teamwork narrative.
- **Self-management:** Top of "Limited"/bottom of "Some evidence". A rough weekly plan is claimed, but no tools, no recovery stories, no outcomes. Autonomous bands (72+) are unreachable without a named autonomous initiative.
- **Insight:** "Some ability" — weaknesses are acknowledged but all remediation is in the future tense. Without execution evidence and without feedback-to-others, 62+ is impossible.

---

## TOP 5 FIXES (ranked by impact on score)

1. **CUT TO 5 PAGES AND REWRITE UNDER THE 4 BRIEF HEADINGS.** This is the single biggest lift: moving from capped-48 to uncapped scoring. Delete Sections 2 (Design and Problem-Solving) and 3 (Societal and Environmental) entirely — they are D6 content, not D7. Restructure the remaining ~5 pages as: **My role**, **My team**, **My impact**, **My support**. Expected lift: +12–18 (from 42 into mid-50s immediately).

2. **ANSWER ALL 10 QUESTIONS EXPLICITLY.** Under each of the 4 headings, embed the sub-questions as paragraph topics so they are impossible for a marker to miss (e.g., under "My role": 1a roles + change, 1b most proud, 1c focus differently). Use the rubric's 10-question list verbatim as a checklist. Expected lift: +6–8.

3. **NAME TEAMMATES AND ADD AT LEAST ONE CONFLICT MANAGED.** Use 3–4 first names. Describe one disagreement (Pi-vs-Cube workload split in §4.4 is a real one — rewrite it with two named engineers, the author's specific mediating action, and the outcome). Without this, the teamwork cap is 58 forever. Expected lift: +5–7.

4. **CONVERT THE DEVELOPMENT PROGRAMME FROM FUTURE-TENSE TO EXECUTED.** Replace §5.5's three "will do" items with two items already DONE during the project: e.g., "In week X I noticed Y, so I did Z; the result was W" (hardware lead delay → I switched to dataset labelling workstream → unblocked flight testing within 2 days). Plus one piece of **feedback given to a named teammate that changed their behaviour** — this unlocks the 72+ insight band. Expected lift: +4–6.

5. **KILL THE AI TONE. USE I / ME / MY AGGRESSIVELY AND REMOVE HEDGED ABSTRACTIONS.** Every sentence in the present draft that starts "The team..." or "This reflection..." should start with "I...". Drop phrases like "I recognise this as a leadership gap", "an honest technical accounting", "prudent and responsible approach". Replace with dated, concrete memories ("On 11 March at the field site when the IMX296 camera kept crashing, I..."). The rubric explicitly caps AI-tone at 48. Expected lift: +3–5, plus removes the cap.

**If fixes 1–5 are executed well, the realistic ceiling is mid-60s to low-70s** (62–72). Hitting 75+ additionally requires a piece of creative team restructuring or worldview-changing reflection, which the current draft has no kernel of.

---

## APPENDIX — SPECIFIC EVIDENCE FROM THE DRAFT

- **Page 1 §1:** "My role expanded significantly beyond its original scope. I was initially responsible for the computer vision pipeline, but in practice I designed and implemented the entire software stack..." — good candidate to become a 1a "roles changed" answer if rewritten with how/why/consequence.
- **Page 3 §4.1:** "I led software and wiring, one served as the designated pilot, one managed project administration (risk assessments, field bookings, transport), and one focused on hardware integration (risk assessments, field bookings, transport)." Note duplicate text (transport/risk/bookings repeated) — sign of hurried drafting.
- **Page 4 §4.3 "Solo Coding Reality":** self-aware, genuine — this is the strongest paragraph in the document. Keep, sharpen, and turn into the honest core of "My team" section.
- **Page 4 §4.4 "Managing Disagreements":** describes a Pi vs Cube architectural disagreement but in passive voice — "Frustration over uneven workload distribution..." Needs two named people and the author's specific action.
- **Page 5 §4.6 "Giving and Receiving Feedback":** claims "I provided technical feedback" but gives no recipient or outcome. THE biggest single fix in the whole document — replace with a specific, dated, named feedback instance.
- **Page 6 §5.5:** three bullet points, all start with "will" — all future tense. Rewrite with past-tense executed equivalents.
- **Page 7 §5.7 Final Thought:** one-sentence summary — ok, but says nothing that the reader didn't already know.

---

**FINAL SCORE: 42/100** (Limited — capped by page overrun, heading mismatch, and absence of specific named evidence). Realistic ceiling after fixes 1–5: **mid-60s to low-70s**.
