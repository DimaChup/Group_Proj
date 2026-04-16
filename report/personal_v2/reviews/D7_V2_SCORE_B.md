# D7 V2 — Independent Score (Scorer B)

**Artefact:** `report/personal_v2/main_v2.pdf` (7 PNG pages)
**Rubric:** `D7_SCORING_FINAL.md`
**Scored blind** — did not read Scorer A's output or V1 scores.

---

## D7 FINAL SCORE: **78 / 100** (Distinction)

Banded as a strong mid-Distinction. Would be a high-Distinction (82+) if the body were cut to the 5-page hard limit and one named non-technical-audience adaptation were made explicit (see CRITICAL FIX #1 below).

---

## HARD GATES (§1)

| Gate | Status | Note |
|---|---|---|
| Page limit — working draft ≤7 | PASS | Cover + rubric-map + body spans pp.1–7 PDF. Body content runs pp.2–7 = **6 body pages**. Working-draft gate (≤7) passes. |
| Page limit — FINAL ≤5 body | **FAIL (if submitted as final)** | Body overruns by ~1 page. **CAP 48** applies if submitted as-is. Treating this as v2/working draft → no cap applied, but flagged as #1 fix. |
| 4 required headings | PASS | My role / My team / My impact / My support — exact match. |
| 10 required questions | PASS (10/10) | 1a, 1b, 1c, 2a, 2b, 2c, 3a, 3b, 4a, 4b all answered with named anchors. |
| First-person voice | PASS | "I…" dominates every paragraph. No hiding behind "we". |
| Specifics (≥5 people / ≥3 dates / ≥1 conflict) | PASS | Robin, Demetro, Edward, pilot, Sid, PM named. Dates: wk12, wk14, wk15, wk16, wk17, wk18, wk19, wk20, wk22, 2026-03-11, 2026-03-20, 2026-03-30, 2026-04-03. Conflict: wk17 FSM disagreement with Robin+Demetro. |
| Honesty (≥1 genuine weakness + action) | PASS | "Convert anxiety into code", solo-work instinct, technical framing as emotional protection, register mismatch in Demetro feedback. Multiple genuine weaknesses with mechanisms. |
| Feedback-to-others (≥1 named episode + outcome) | PASS | Three episodes: Demetro cadence, Robin CENTERING timeout → bug-shape propagation, pilot minimalist button layout → VERIFY request. |
| AI policy (personal voice) | PASS | Distinctly personal voice — Ukrainian engineering culture line, "trust my hands over a conversation" — unforgeable. |
| Media diversity ≥2 | **WEAK PASS** | Report, docs (VISION_PIPELINE, FIELD_QUICK_REF, complaint letter), web dashboard UI, FDR speaking scripts, Teams messages. ≥2 media evidenced but audiences overlap heavily inside the team. |
| Readability (≥10pt, 1.05, 1.8–2cm) | PASS | 11pt, linespread 1.05, 1.8/2cm margins per main_v2.tex. |
| Presentation (headings, fill) | PASS | Compact titlesec, consistent hierarchy, ~90% fill. Rubric map at top is a nice assessor-friendly move. |
| Evidence density | PASS | Nearly every claim anchored to file/commit/date/line — `ce5c036`, `3d62e6a`, `DESIGN_DECISIONS.md:107–109`, `passive_watch_2.py`, `a5b1ab7`, etc. |
| Alternative perspective (≥1) | PASS | Multiple: "I initially framed this as X — in fact it was Y"; "I was right about the FSM and wrong about the context"; technical vs maintainability disagreement reframing. |

---

## CRITERIA (0–100)

### Teamwork: **77** — upper-Distinction band

**Band reason:** Bristol 70–79 descriptor earned ("consistently demonstrates effective teamworking and leadership skills … manage conflict"). Cleared:
- **Conflict management episode** — wk17 FSM disagreement: named parties (Robin, Demetro), named disagreement (two-out-of-five maintainability floor), named mechanism (24h cool-down, reread Robin's script, compromise via `--robin` HTTP interface), named outcome (wk20 integration in an afternoon instead of a week). Textbook.
- **Leadership threshold (2/5 §4.5):** hits at least 3 —
  - *Decision authority*: wk18 pivot to simulation-first, delegated SITL home-location fix to Edward, moved Demetro's FDR slot forward
  - *Meta-work*: blueprint system, brain-dump, FIELD_QUICK_REF, handoff docs
  - *Influence under disagreement*: wk17 compromise on FSM; six-iteration tonal polish on complaint letter
- **Honest ownership language** balances leadership claim — "leadership-without-title moment, such as it was" is the exact right register.
- **Cross-team collaboration with interface**: `passive_watch_2.py --robin` HTTP cv_mode polling as a named interface with named beneficiary.

Why not 80+: the section acknowledges the author's solo pattern but the *team's* collective functioning is described mostly via the author's orbit around it. "Outstanding creativity/flexibility responsive to group members' interests" (80+ descriptor) is suggested but not quite evidenced at the team level — the team-as-system stays thinly drawn.

### Self-management: **80** — top of Distinction band

**Band reason:** "Works autonomously, very good self-organisational skills, professional attitude" (70–79) cleanly earned and pushed toward 80+ ("outstanding"):
- Autonomy under ambiguity is the whole Kolb anchor story — built a 6-week simulation-first path when no one asked for it, held the line, delivered.
- Evidence-based decision under challenging/unfamiliar circumstance (Bristol Decision-making 70+): 2026-03-11 weather cancellation → decided institutional constraint required a second path. Textbook.
- Applied lessons inside the project timeline: timeboxing rule (NCNN detour), modularity audit → refactor 1411→754 lines, 127 unit tests added.
- Discipline: refactor + 146 pytests + modularity audit is a professional-attitude signal the rubric explicitly rewards.

Why not 85+: the "creative, responsive, outstanding" 80+ territory needs a second domain of outstanding autonomy — the section has one, not two. And the solo-work pattern is named as a weakness (which is honest) but it slightly undercuts the pure autonomy claim.

### Insight: **77** — mid-Distinction

**Band reason:** All four Bristol 70–79 gates cleared:
- *Assess own strengths and weaknesses*: multiple named patterns ("convert anxiety into code", register mismatch, technical framing as emotional protection, solo-work as avoidance of collaboration).
- *Implemented programme of self-development*: 60/40 solo/pair cap with falsifiable test, timebox rule applied mid-project, modularity audit → refactor → pytest coverage chain.
- *Effective feedback to others*: three distinct episodes (Demetro/Robin/pilot), each with named reaction AND self-critique of delivery AND generalisable lesson. Robin episode is the strongest — observable downstream behaviour change ("looking for that shape of bug", contract-style handoffs propagating).
- *Forward-looking commitments are falsifiable*: "teammate completes handoff within 48h without asking a second question", "no file >500 lines refactored solo", "any doc >500 words paired with 15-min walkthrough". Mechanism-based, not wishes.

**M17.d evaluation of methods** is the weakest clause for Insight. The 2000-word vs 3000-word vs 400-word comparison in §2c is exactly the A/B evidence the rubric wants — but it's one paragraph, not a dedicated evaluation move, and it mixes "long handoff doc sat unread" with "short pivot message worked" without explicit criterion × judgement × comparison formatting. It earns the credit but not cleanly.

**Non-technical audience (M17.c)** — this is the single biggest hole. The complaint letter to the course organiser is flagged as "non-technical-audience artefact" in §4b but the **adaptation is not shown** (no before/after, no jargon-removal pair, no analogy). Per §4.6, 2-of-5 adaptation evidence is required. The pilot counts as a mild non-technical audience (RC thumb-reach → 4-button layout is analogy + audience-first structure = 2/5 threshold JUST cleared), but the stronger artefact (complaint letter to a non-engineer administrator) is named without evidence of adaptation. This costs ~3–5 Insight marks.

Hatton & Smith Level 4: strongly present. "I initially framed this as X — I now see I preferred the X framing because it protected me from Z" is the canonical Level 4 move and it appears at least 4× (§1a, §2b, §4a Robin paragraph, §4b closing). Level-4 moves per page: ~2.5–3 average. Cleanly above the ≥2/page floor.

### **Average: (77 + 80 + 77) / 3 = 78.0**

---

## AHEP4 COVERAGE (sub-clauses out of 48)

Scoring each 0–3 based on coverage depth and evaluation quality:

| Sub-clause | Score | Evidence |
|---|---|---|
| M16.a — individual contribution w/ file/date/metric | **3** | vision.py end-to-end, 2508-line simulator, 1411→754 refactor, 146 pytests, bbox bug commit `3d62e6a` |
| M16.b — cross-team collab w/ named interface | **3** | `passive_watch_2.py --robin` HTTP cv_mode polling, `DESIGN_DECISIONS.md:107–109` agreement |
| M16.c — leadership OR honest ownership | **3** | Hits threshold: wk18 pivot decision + delegation, meta-work (blueprints/docs), influence at wk17. Honest caveat "such as it was" |
| M16.d-own — self-eval criterion+judgement+cause+lesson | **3** | NCNN detour timebox; 60/40 cap with falsifiable signal; modularity audit self-score 3.0/5.0 on own code is the strongest concrete self-evaluation I've seen in a D7 |
| M16.d-team — team-eval c+j+c+l | **2** | R01–R12 matrix "12/12 sim, 4/12 real" implied by "limits of that statement"; silent drift at wk16 named as coordination failure. Present but not formalised as one tight c+j+c+l paragraph |
| M17.a — complex content communicated | **3** | VISION_PIPELINE_FOR_COLLEAGUE.md, FDR scripts with speaking cadence, complaint letter |
| M17.b — technical audience reception | **3** | "Robin integrated in a single session without asking follow-up questions for two days" — confirmed reception with metric |
| M17.c — non-tech audience + 2/5 adaptation | **2** | Pilot UX scrapes 2/5 (analogy: RC thumb-reach, audience-first: minimal buttons). Complaint letter named as non-tech artefact but **adaptation not shown** (no before/after, no jargon pair). Weakest clause. |
| M17.d — methods enumerated + criterion + comparison | **2** | 2c contrasts pivot msg (short/timely + live call → behaviour change) vs 3000-word handoff doc (sat unread until needed). Present but informal — no explicit "method → criterion → judgement" table or parallel structure |
| Bristol Comms 60+ (≥2 media) | **3** | Report, docs, dashboard UI, FDR slides+speaking, Teams threads, complaint letter |
| Bristol Comms 80 (engaging + reception) | **2** | Robin's "looking for that shape of bug" is exactly the reception evidence the 80-band asks for. But only one such anchor |
| Every claim has evidence | **3** | Exemplary — nearly every sentence has a commit/file/date anchor |
| Alternative-perspective consideration | **3** | Multiple "one reading is X, another is Y" moves; "right about the FSM, wrong about the context" |
| Forward-looking lesson tied to future context | **3** | Three falsifiable mechanisms in §3b with observable signals |

**Total: 38 / 48**

Banding guide: 35–42 → 70s. Fits the 77/78 average cleanly.

**Sub-clause adjustment:** (38/48) × 10 − 5 = +2.9

---

## BRISTOL HIDDEN REQUIREMENTS (§5)

| Req | Status | Note |
|---|---|---|
| Conflict management | ✓ | wk17 FSM — textbook |
| Leadership 2/5 threshold | ✓ | 3/5 cleared (decision authority, meta-work, influence under disagreement) |
| Media diversity ≥2 | ✓ | Multiple |
| Peer feedback | ✓ | Three episodes, all with self-critical delivery analysis |
| Evaluate 4 elements (criterion+judgement+cause+lesson) | ✓ | Cleanly on self-evaluation; less cleanly on team-evaluation and M17.d |

No hidden cap triggered.

---

## QUESTION COVERAGE: 10 / 10

- **1a** ✓ Roles allocated vs taken — CV lead at wk12 drifted to infrastructure/state machine/simulator/geofence by wk22, with honest mechanism ("anxiety → code")
- **1b** ✓ Most proud — simulation framework, decision to build it at wk14, with mechanism and outcome (D6 verifiable output)
- **1c** ✓ Focus differently — 60/40 cap + falsifiable signal (teammate handoff task in 48h)
- **2a** ✓ Structure — kickoff negotiation, two named drifts (silent wk16 + loud wk17), renegotiation with file/line anchor
- **2b** ✓ Most impactful — handoff doc 5:1 time ratio + wk17 conflict + wk18 pivot delegation
- **2c** ✓ Change next time — three concrete changes with falsifiable signals (decision log, interface contracts, doc+walkthrough rule)
- **3a** ✓ Drove team forward — Kolb-anchored simulation-first thesis + three side contributions (Robin integration, Demetro FDR, complaint letter)
- **3b** ✓ Add/refocus — three falsifiable teach-first mechanisms
- **4a** ✓ What others did for me — Edward/Robin/Demetro/pilot/Sid each with named mechanism and lesson
- **4b** ✓ What I did for others — three feedback episodes with named reactions, self-critique, generalisable lessons

All 10 strongly answered. No penalties.

---

## LEVEL-4 MOVES (Hatton & Smith)

Per page (body pages 2–7, = 6 pages):
- p.2 (My role start): ~2 (anxiety→code reframe; "trust my hands more than a conversation")
- p.3 (My role end + My team): ~3 (judgement ≠ picking techniques; Ukrainian culture reframe; unexplicit structure as luxury)
- p.4 (My team end + My impact start): ~3 (right about FSM wrong about context; handoff docs as emotional scaffolding; technical vs team leadership as orthogonal)
- p.5 (My impact continued): ~2 (sim-first as claim about discipline not preference; sober limits of the statement)
- p.6 (My support 4a): ~2 (SITL parity as hypothesis not evidence; technical vs maintainability framing protected me)
- p.7 (My support 4b + close): ~3 (register > prose quality; bug-shape propagation; async docs as emotional scaffolding)

**Total: ~15 Level-4 moves across body.** Comfortably above the ≥10 floor (≥2/page). One of the strongest Level-4 densities I'd expect at Distinction level.

---

## PENALTIES

| Penalty | Amount | Note |
|---|---|---|
| Page overrun (working draft) | 0 | Within ≤7 working gate |
| Page overrun (final submission) | −30 (CAP 48) | **Applies if this is submitted as final.** Excluded from main score as this is v2/working. |
| Missing questions | 0 | 10/10 |
| No feedback-to-others | 0 | Three episodes |
| No conflict | 0 | wk17 |
| Media diversity | 0 | Cleared |
| M17.c non-tech audience weakness | −1 | Pilot just scrapes 2/5; complaint letter adaptation not shown |
| M17.d evaluation informality | −0.5 | A/B comparison present but not in tight c+j+c+l form |
| Vague/generic | 0 | None detected |

Net penalty: −1.5

---

## FINAL SCORE CALCULATION

```
base_score        = 78.0 (avg of 77/80/77)
sub_clause_adj    = +2.9 (38/48 coverage)
question_penalty  =  0
other_penalties   = −1.5
------
raw              = 79.4
```

Rounding to nearest Bristol band step (72 / 75 / 78 / 83): **78 / 100**.

---

## TOP 5 FIXES (ranked by impact)

1. **CUT TO 5 PAGES (hard cap for final submission).** Body is currently 6 pages. Suggested cuts: tighten §2b conflict paragraph (trim the "I had proposed an 11-state FSM" setup), compress §3a Kolb (180 words is the budget — current is ~350), remove the "three other contributions" paragraph in §3a (already evidenced elsewhere), consolidate §4a pilot+Sid into one paragraph. **Target: cut ~350–400 words.** If submitted at 6 pages: CAP 48 → catastrophic.

2. **Show the non-technical-audience adaptation explicitly.** Pick one artefact (complaint letter is strongest) and add a 2-sentence before/after: "My first draft said [technical phrase X]; the version the team signed said [lay equivalent Y] — I dropped the reference to [jargon Z] because the audience was an administrator, not an engineer." This unlocks M17.c from 2/3 to 3/3 and would add ~2 marks.

3. **Formalise the M17.d A/B comparison.** Turn the implicit comparison in §2c into an explicit sentence: "Against the criterion of observable behaviour change per author-hour: the 400-word pivot message produced a team pivot within 24h; the 3000-word handoff doc produced no action until week N; the FDR script rewrites produced measurable cadence improvement. The scarce resource was not prose quality but timing and pairing." Named comparison, named criterion.

4. **Tighten the team-evaluation clause (M16.d-team).** The R01–R12 "12/12 sim, 4/12 real" is implied but never stated. Add one sentence: "Against the R01–R12 requirements matrix the team delivered 12/12 in simulation and 4/12 in real hardware. 3 of the 8 gaps were bench work we did not schedule — a coordination failure, not an effort failure." This upgrades M16.d-team from 2/3 to 3/3.

5. **Add one engaging reception anchor for Comms 80+.** The Robin "looking for that shape of bug" line is the only named reception outcome with measurable downstream effect. Adding one more (e.g., Demetro using "specific numbers rather than adjectives" a week later — which is already in the draft but not tagged as reception evidence) would push Comms toward the 80 band.

---

## CONFIDENCE

| Criterion | Confidence | What would change my mind |
|---|---|---|
| **Teamwork (77)** | **HIGH** | Would move to 74 if wk17 conflict were re-read as author-centric rather than mutually managed (I don't think it is — Robin's pushback is credited); would move to 80 if a second conflict episode with different party and different mechanism were added. |
| **Self-management (80)** | **HIGH** | Would move to 83 if a second outstanding-autonomy domain were evidenced (currently one domain — simulation-first pivot — dominates). Would move to 77 only if I decided the solo pattern admission materially weakens the autonomy claim (I don't — it sharpens it). |
| **Insight (77)** | **MEDIUM** | Would move to 80 if M17.c non-tech adaptation were explicitly shown (2 marks locked behind this). Would move to 73 if the pilot episode doesn't actually clear 2/5 on second reading — I counted "analogy" (RC thumb-reach) and "audience-first structure", but a stricter reader might count only one. |
| **M16.d-own self-evaluation** | **HIGH** | Strongest clause in the report. Modularity self-audit at 3.0/5.0 on own code is unusually honest. |
| **M17.c non-tech audience** | **LOW** | This is the weakest clause and I'm least certain whether it clears 2/3 or stays at 1/3. A harsh marker could rule the complaint letter isn't shown with adaptation evidence and the pilot is borderline same-discipline. If ruled 1/3, Insight drops to ~74, final score ~76. |
| **M17.d methods evaluation** | **MEDIUM** | The comparison is informal. A strict rubric reader might want the three methods (prose/diagram/demo or pivot/handoff/FDR) formalised as a table or parallel sentence block. Score could sit 2/3 or 1/3 depending on strictness. |
| **Page limit (working vs final)** | **HIGH** that the working draft gate passes; **HIGH** that the final-submission gate fails at 6 body pages and would trigger CAP 48 if submitted. This is the single biggest risk in the document. |
| **Final aggregate (78)** | **MEDIUM–HIGH** | Plausible range 74–80 depending on how strictly M17.c is judged. I am confident it is a Distinction; I am less confident whether it sits at 75, 78, or 80. The 5-page cut is what separates "Distinction working draft" from "submittable Distinction final". |

**Overall:** This is a strong Distinction-level D7 working draft. The writing is honest, the reflection is consistently at Hatton & Smith Level 4, the evidence density is exceptional, and the falsifiable forward commitments are the best feature of the document. The gap between 78 and the 83+ band is mainly (a) one explicit non-technical adaptation, (b) formalising the M17.d comparison, and (c) cutting to the 5-page hard limit. All three are mechanical fixes.
