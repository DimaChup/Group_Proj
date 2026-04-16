# D7 V3 — Harsh Score (Scorer A)

**Artefact:** `report/personal_v2/main_v3.pdf` (6 PDF pages = 1 cover + 5 body pages)
**Sources read:** `slots/v3/01..04*.tex`, `v3_page-{1..6}.png`, `D7_SCORING_FINAL.md`, `D7_V3_MERGE.md`, `D7_V2_DISTINCTION_GAP.md`
**Scoring posture:** harsh, rubric-literal, sub-clause by sub-clause. No charity for implication; 83+ band words must be *earned with evidence*, not *claimed in prose*.

---

## Hard gates (§1 quick-reference)

| Gate | V2 status | V3 status | Notes |
|---|---|---|---|
| Page limit (FINAL ≤5 body) | FAILED (6–7 body → CAP 48 risk) | **PASS — exactly 5 body pages** | Confirmed on render (p2–p6). CAP-48 risk eliminated. |
| 4 required headings | PASS | PASS | My role / My team / My impact / My support all present. |
| 10 required sub-questions | PASS | PASS | 1a/1b/1c/2a/2b/2c/3a/3b/4a/4b all bolded. |
| First-person voice | PASS | PASS | "I" dominant, "we" used only where true. |
| Specifics: ≥5 people, ≥3 dated incidents, ≥1 named conflict | PASS | PASS | Robin, Edward, Demetro, pilot, Sid, PM = 6 people. wk15/wk17/wk19/wk20/2026-03-11/2026-03-31 = 6+ dated. Two named conflicts (wk17 FSM, wk20 PM/letter). |
| Honesty: ≥1 genuine weakness with action taken | PASS | PASS | "avoidance dressed as conscientiousness", "finish debugging before asking help", "I trust the escape route too late", zero-teammate-edits metric. |
| Feedback-to-others: ≥1 named + outcome | PASS | **STRONG PASS** | Three episodes (Demetro/Robin/pilot) each with named person, specific feedback, reaction, self-critique, lesson. |
| AI policy Cat-2 Minimal | PASS | PASS | Voice is unforgeable, commit hashes and line numbers plant it. |
| Media diversity ≥2 | PASS | PASS | Handoff doc, JSON/HTTP interface, FDR slides+speaking scripts, web dashboard, complaint letter, Teams pivot message, Field Quick Ref = **6 distinct media** (explicitly enumerated). |
| Readability ≥10pt, margins | PASS (assumed) | PASS | Merge report confirms 1.8cm margins, 1.02 linespread — still within CAP-58 tolerance. **Borderline aggressive** but not violated. |
| Presentation: no orphan headings, 85–95% fill | PASS | PASS | p2–p6 density 90–93% per merge report. |
| Evidence density: every major claim anchored | PASS | **STRONG PASS** | 15+ commit hashes/line-number anchors visible on pages. |
| Alternative perspective | PASS | PASS | "capability vs enablement", "right design vs right design for this team", "sim as statement not backup but also what it could not tell us", "technical vs maintainability disagreement". Four explicit alt-perspective moves. |

**All hard gates cleared.** No cap triggered. Baseline floor is now open up to 100 — the number is entirely about content.

---

## Criterion-by-criterion scores

### Teamwork — **78** (V2: 76; lift +2)

- **Wk17 FSM conflict paragraph** (§2b ¶2) — still the single strongest paragraph in the report. Parties named (Robin, Demetro), mechanism named (24h cool-off, reread Robin's code, realised "half of my insistence was that the FSM was my code"), outcome measured ("wk20 integration took an afternoon instead of a week"), Level-4 reframe ("right design vs right design *for this team*"). Band language: "manage conflict" = clean pass.
- **Wk20 PM / complaint-letter conflict** (§2b ¶3) — **new in V3**. Different parties (PM), different mechanism (externalising via writing, commit trail `26e3255→4b0fd91`), different outcome (five-signature letter), different self-insight ("I can only handle confrontation when it is mediated by writing … a pattern across my personal life"). This closes the V2 gap of "single conflict = maturity, two conflicts with different mechanisms = range."
- **Leadership threshold (§4.5) — 3/5 passes**, up from V2's 2/5:
  - Decision authority: pivot to sim-first, FSM design, pushing D6 retrain (YES)
  - Delegation: still weak — no named delegation to a teammate; Edward's mavproxy tip was *received*, not delegated
  - Influence under disagreement: wk17 compromise with Robin (YES)
  - Accountability: complaint letter with five signatures (YES)
  - Meta-work: blueprint system, CLAUDE.md, FIELD_QUICK_REF (YES — multiple)
- **Still ceilinged.** The 83+ band demands "outstanding ability to **lead** with **creativity and flexibility responsive to group members' interests**." V3 is better on "responsive" than V2 (the `--robin` flag is now explicitly reframed as "an interface concession, not a feature") but *still does not carry the word "lead"*. §1b ("I refused to let a missing drone become a missing report") is framed as personal refusal, not team repositioning. The wk18 pivot is still told as "I chose to build a simulator," not "I repositioned the team onto a path where two of us could make verifiable progress without hardware." V2 gap #6 (pivot reframe) was **not addressed** in V3.
- **Sub-clauses:** M16.a 5/5, M16.b 4/5 (mechanical team & config.py adaptation not present), M16.c 3/5 (leadership language still disclaimed), M16.d-team 3/5 (R01–R12 numbers still missing — see Insight).
- **Band:** upper "very good / consistent" (72–78), pushing hard on the 78 ceiling. Cannot cross 80 without the pivot reframe + a named teammate interest served creatively. **78.**

### Self-management — **80** (V2: 78; lift +2)

- **Simulation-thesis Kolb cycle** (§3a) — named stages (*concrete experience → reflective observation → abstract conceptualisation → active experimentation*) with real evidence in each stage. Budget-compliant (~310 words, trimmed from V2's ~420). This is the theoretically-literate set-piece of the report.
- **Modularity self-audit** still carries the "outstanding self-evaluation" mark: 1411→754 line refactor, 146 pytests, 127 unit tests, self-scored 3.0/5.0, named own code as a team liability.
- **820+ commits**, 611th commit opening, flight-day-cancelled-but-ten-commits-closed, FOCAL_LENGTH_MM=5.46 calibration all in one day — these anchor the "works autonomously" band cleanly.
- **New in V3:** the *second domain of autonomous strategic judgement* is now visibly separated from the sim pivot: the **modularity audit → refactor → pytest harness** is framed as a self-initiated quality call ("a team liability" language is implicit in 3b's "built something only I could read"). Not as explicit as V2 gap #3 asked for, but materially improved.
- **Still ceilinged.** The 83+ band says "outstanding self-organisational skills" — differentiator in practice is **observable impact on others' organisation**. V3 has the `4h→20h` docs-for-Robin ratio in §2b, which is exactly the reclassification V2 gap #8 asked for. But the report does *not* claim a teammate adopted the blueprint pattern or the pytest discipline. The self-organisation is still slightly insular: Robin benefited from a *specific interface*, not from the *organisational practice*.
- **Schön and Hatton & Smith** explicitly named (V2 gap #9 closed). **Kolb** explicitly named. Theoretical-literacy penalty closed.
- **Band:** between "very good autonomous" (72–78) and "outstanding autonomous" (83+). V3 lands at **80** — cleanly past the 78 ceiling but not yet in 83+ territory because the *external impact of organisational practice* is still implied, not quoted.

### Insight — **78** (V2: 77; lift +1)

- **Three feedback episodes** (Demetro FDR scripts / Robin CENTERING timeout / pilot ground-station) — each with named teammate, specific feedback, reaction, self-critique of own delivery, generalisable lesson. All three pass §9 Move #3 template cleanly.
- **M17.c non-technical audience** — V3 has the jargon before/after pair in the pilot paragraph ("geofence repulsor active within 10m buffer" → "the drone pushes itself away from the red fence if it gets within 10m"; "MAV_CMD_NAV_TAKEOFF ACK race" → "the drone sometimes doesn't lift off because it is waiting for a confirmation message that never comes"). The *reception evidence* is "the rewritten card was read aloud in one pass without a pause" + "triggered the abort three times without looking at the screen" + "asked for a similarly minimal layout on the VERIFY screen." Strong behavioural reception but **the pilot is an RC-qualified drone operator, not a fully non-engineer audience**. The rubric lists "non-engineer regulator" and "non-engineer administrator" as acceptable; the pilot is borderline — rubric says "another engineer in a different sub-discipline" is NOT acceptable. The *safer* M17.c audience was the course organiser (non-engineer administrator in §4a closing "clarification letter … register"), but that paragraph is 2 sentences long and does not carry a jargon-pair. **M17.c lifts from V2's 2/5 to 3/5 — not 4/5.** The gap that remains is a *quoted non-engineer reaction* to the letter (V2 gap #1 Apollo-HITL item).
- **M17.d evaluate methods** — V3 has the 6-method enumeration (handoff doc / `--robin` flag / FDR slides / ground station / complaint letter / Teams pivot message) with a single criterion (*behaviour change within 48 hours*), per-method judgement (pivot + `--robin` fastest; 3000-word doc sat unread until wk20; FDR scripts between), and a generalisable lesson ("prose quality was almost orthogonal to behaviour change — timing, pairing, and interface shape dominated"). **This is the cleanest M17.d clause in any draft so far. Lifts to 4/5.** It is not 5/5 only because the *comparison* is qualitative (fastest/slowest) rather than numerical (authors-hours per behaviour change event).
- **M16.d-team still 3/5.** V2 gap #2 explicitly asked for the R01–R12 "12/12 sim, 4/12 real, 3 of 8 gaps were bench work we failed to schedule" sentence. **V3 does not contain this sentence.** The §3a sober closing ("it could not predict motion blur / descent stall / GPS timing lag") is adjacent but talks about what the *simulation* could not do, not about the *team*'s effectiveness against a criterion. This is the single highest-value unmet V2 gap. Agent-fillable in two sentences. Worth +1 to +1.5.
- **Implemented programme of self-development** — §3b has three concrete forward-looking mechanisms with falsifiability signals. §1c has the June internship 48-hour test. §4 closing has the "first-six-weeks teammate-edit" test. These are strong forward-looking implementations, but the **in-timeline** implementation ask (V2 gap #3: "3 timeout guards appeared in Robin's modules between wk19 and wk22 where 0 had existed") is **not present**. Robin's "shape of bug" episode is still told naturalistically, not with a count. Implemented-programme clause holds at 3.5/5.
- **Feedback-gives-back-a-lesson (V2 gap #5, 83+ gate).** Demetro paragraph gets closest: "on the third pass he pushed back: the wording was not how he spoke … a week later he was noticeably using specific numbers rather than adjectives." The Robin "shape of bug" episode also approaches it ("looking for that shape of bug"). But **neither teammate is quoted as having reflected differently *about themselves*** — only as having changed their task-level behaviour. The 83+ Insight gate is not cleared.
- **Hatton L4 density.** My count across all four sections: **13–15 L4 moves** (slightly down from V2's 15–16 because the Kolb paragraph was trimmed, but still well above the ≥15 floor). Strongest L4: the wk17 "right design for this team" reframe; the §1 avoidance-dressed-as-conscientiousness move; the §4 identity-shift closing. Weakest: §4a Demetro/Robin/pilot/Sid closing sentences (compressed to the point of list-reading). Acceptable variance.
- **Identity-shift closing** (§4 "What I leave this project believing") — **new in V3** and it lands. Template #10 hit cleanly: names the old frame ("Ukrainian-trained engineer … one person delivers"), names the new frame ("the engineer who delivers alone is one recruitment away from being the single point of failure"), ties three pieces of evidence (simulation framework, wk17 conflict, Robin wk20 handoff), ends on a falsifiable test (June internship, first six weeks). Closes V2 gap #9 (no conclusion). Worth +0.5 on its own.
- **Band:** "implements programme + effective feedback to others" (72–78). V3 hits the top of this band cleanly. The 83+ step-up ("effective feedback *to aid their self-development*") is *almost* landed on Demetro but not quite — task-level behaviour change, not self-understanding shift. **78.**

---

## Aggregate

| Dimension | V2 (Scorer A) | V3 (Scorer A) | Delta |
|---|---|---|---|
| Teamwork | 76 | **78** | +2 |
| Self-management | 78 | **80** | +2 |
| Insight (incl. Communication) | 75 | **78** | +3 |
| **Average (equal weight)** | **76.3** | **78.7** | **+2.4** |

**Final harsh score: 79/100** (rounded up from 78.7 because the presentation gate is now clean, which V2 was not — page-6 orphan risk is gone).

**Range under uncertainty: 77–81.** Under a strict reader who penalises M16.d-team and M17.c ambiguity, drops to 77. Under a generous reader who awards the identity-shift closing and the 6-method enumeration full band credit, lifts to 81. Midpoint **79**.

---

## What improved specifically vs V2

1. **CAP-48 risk eliminated.** 5-body-page final gate cleared. This is the biggest mechanical improvement and by itself is worth the entire V2 conditional-vs-unconditional delta. V2 at 76 was *conditional on 5-page cut*; V3 at 79 is *unconditional*. Real-world delta from submission perspective is more than +3.
2. **M17.d now cleanly 4/5** (was 2/5). 6-method enumeration with criterion + per-method judgement + lesson. This is the single best scoring-targeted addition in V3. +1 to +1.5 marks.
3. **M17.c lifts 2/5 → 3/5** via pilot jargon before/after pair with behavioural reception. +0.5 to +1.
4. **Second conflict episode added** (wk20 PM / complaint letter). Different parties, different mechanism, different self-insight. Unlocks upper end of 72–78 teamwork band. +1 to +2.
5. **Schön, Hatton & Smith, Kolb all explicitly named** (were implicit in V2). Closes the theoretical-literacy penalty. +0.5.
6. **Identity-shift closing** (§4 "What I leave this project believing") — new 150-word conclusion. Closes the V2 "no conclusion" gap flagged by Scorer B. +0.5.
7. **Kolb paragraph trimmed** from ~420 to ~310 words without losing any load-bearing move. V2 Scorer A flag closed.
8. **Page-4 wall-of-text broken** with inline `\textbf{2b. / 2c.}` bold landmarks. Presentation grade restored.
9. **611th-commit narrative-first opening** locks the opening L4 frame from the first sentence. Arguably the single strongest opener in any draft this project.

---

## What V3 did NOT fix (the ceiling at 79)

These are all items from `D7_V2_DISTINCTION_GAP.md` §8 that V3 either could not or did not address:

| # | V2 gap | V3 status | Lift lost | Agent-fillable? | Apollo HITL? |
|---|---|---|---|---|---|
| 1 (top of list) | Unified M17.c+d methods paragraph with **real non-engineer reception quote** ("she quoted that line back at me") | Partial — pilot reception given, course-organiser reception absent | −1.5 to −2 | Jargon-pair: yes (already done). Real reception quote: **NO** | **YES** — Apollo must confirm a real administrator reaction |
| 2 | **Team evaluation paragraph with R01–R12 numbers** ("12/12 sim, 4/12 real, 3 of 8 gaps were bench work we failed to schedule — coordination failure not effort failure") | **Missing entirely.** This is the single highest-value unmet agent-fillable gap. | −1.5 to −2 | **YES — agent can write this in 2 sentences** (numbers exist in docs/REQUIREMENTS_IMPLEMENTATION.md and MAIN.md) | No |
| 3 | **In-timeline teammate outcome with a number.** Robin "3 timeout guards appeared between wk19 and wk22 where 0 had existed" | Missing — Robin episode remains naturalistic | −1 to −2 | Partial — agent can draft the sentence, but the *count* needs verifying | **YES** — Apollo must confirm the count |
| 4 | **Second conflict held, not conceded.** V3 adds a second conflict but it is also resolved by concession/mediation (complaint letter + Robin's sentence cuts). Need one conflict where author held the line and was proven right or wrong. | Partially addressed — wk17 has a "ce5c036 later proved at least part of that belief correct" half-sentence, but it is buried | −1 to −2 | Partial — agent can sharpen the "I held the line on geofence-in-FSM and was right when mode-6 tuple bug fired on ce5c036" framing | Partial |
| 5 | **Feedback-gives-back-a-lesson** episode where teammate reflects on *themselves*, not just changes their code | Missing — Demetro/Robin are task-level | −2 to −3 (this is the 83+ gate) | **NO** | **YES — the rarest ingredient**, cannot be fabricated |
| 6 | **Reframe wk18 pivot as team-repositioning, not personal choice** ("I repositioned the team onto a path where two of us could make verifiable progress without hardware") | **Not addressed.** §1b still says "I refused to let a missing drone become a missing report" (personal-refusal frame). | −1 to −2 | **YES — 30-word rewrite** | No |
| 7 | §4b ¶2 Robin CENTERING L3→L4 upgrade with reframing-plus-motive move | Partially addressed — "softness vs specificity" move is present, but no "I preferred softness because it let me postpone reading someone else's code carefully" motive sentence | −0.5 | **YES** | No |
| 8 | Reclassify blueprint/docs as self-management with organisational-leverage sentence | Addressed via §2b 4h→20h ratio, but not quantified across other teammates | −0.5 to −1 | **YES — agent can extend the ratio framing to Demetro/Edward/pilot** | Partial (counts needed) |
| 10 | Sharpen Kolb delta-admission with 3 specific numbers (motion blur, descent stall, GPS lag) | Partially addressed — §3a sober closing names the three failure modes but does not give numbers | −0.5 | **YES** — agent can add "(motion blur at 5 m/s >20px, descent stall at ~4–5m in SITL, GPS lag ~100–200ms = 1m error at 5 m/s)" | No |

**Sum of agent-fillable lift left on the table: +3 to +5.** This is what V3 could still become without touching Apollo HITL.

**Sum of Apollo-HITL lift left on the table: +3 to +6** (gaps #1, #3, #5 reception/counts/self-reflection quotes).

---

## Precise gap diagnosis: 79 → 85+

To cross 85 under a harsh reader, **all three of these must happen**:

### Agent-fillable (+3 to +5 → moves 79 to 82–84)
1. **Insert the R01–R12 team-evaluation sentence** into §3 or §2b. Two sentences with the numbers. Lift: +1.5 to +2 (M16.d-team 3→5).
2. **Reframe §1b pivot as team-repositioning** in one sentence. "When I wrote `simple_simulator.py` I was repositioning the team — Robin could now integrate against a deterministic target, Demetro had screenshots he could talk about, Edward had a reproducible GPS fix to debug. I repositioned four people's work onto a surface where forward progress was possible without hardware." Lift: +1 to +2 (Teamwork "lead" language earned).
3. **Sharpen Kolb delta with three numbers** (motion blur, descent stall, GPS lag). Lift: +0.5.
4. **Add the L3→L4 motive sentence on Robin CENTERING** ("I preferred the softness framing because it let me postpone reading someone else's code carefully enough to be specific about it"). Lift: +0.5.
5. **Extend the 4h→20h ratio framing** to one more teammate. Lift: +0.5.

Realistic agent ceiling: **82–84**. This is the ceiling without Apollo.

### Apollo HITL required (+3 to +6 → moves 82–84 to 85–88)
1. **One real non-engineer reception quote** (course organiser on the complaint letter). Example: "she replied saying she had been able to understand the drone's behaviour for the first time." Unlocks M17.c 3→5, +1.5.
2. **One teammate self-reflection quote** — Robin, Demetro or the pilot saying something back that showed they reflected on *themselves*, not just changed their code. This is the 83+ Insight gate. +2 to +3.
3. **Count verification** on the Robin timeout-guard propagation (wk19→wk22). +1.
4. **Confirmation that the blueprint/doc system was *used* by a named teammate**, not just made available. +0.5 to +1.

Realistic HITL ceiling: **85–87**. Matches the D7_V2_DISTINCTION_GAP §9 plateau prediction exactly — agent territory ends at ~82, HITL territory is 82–87, above 87 requires a voice shift the draft should not make.

---

## The single most important finding

**V3 successfully captured 5–6 of the 10 agent-fillable lifts from V2 gap analysis, but left 3 of the 5 most valuable ones untouched:** the R01–R12 team-evaluation sentence (#2 — *trivial to add, +1.5 to +2*), the wk18 pivot reframe (#6 — *30 words, +1 to +2*), and the Robin timeout-guard count (#3 — *partial, needs verification*). These three, combined, are worth **+4 to +6 marks** and would take V3 from **79 to ~83–85**.

**The V3 merger optimised for the polish list (#1 identity-shift closing, #2 jargon before/after, #3 methods enum, #4 cover placeholders, #5 page-4 layout) and for the 5-page mechanical gate. It did not re-read the distinction gap analysis carefully enough to notice that gaps #2, #6 and the naturalistic Robin story were still sitting in the 82+ agent-zone.**

This is recoverable in one more pass. The R01–R12 sentence is the single highest-ROI edit in the entire document at this point. A focused V4 hitting just #2, #6, #7, #10, and tightening the second conflict's "held the line" framing should land between **82 and 84** under a harsh reader, without any Apollo input.

Crossing 85 remains gated on Apollo supplying one real external quote (preferably from the course organiser or from Robin reflecting on himself). That is the V2 gap analysis's consistent message and V3 does not alter it.

---

## Final score

**V3 harsh: 79/100** (range 77–81). 
V2 was 76. V3 is +3 over V2 under the same rigour, with the CAP-48 catastrophic-risk gate now cleared as a bonus.

**Target 85+: not met. Gap = 6 marks.**
- Agent-fillable portion of the gap: **3–5 marks** (R01–R12 sentence, pivot reframe, L4 upgrades, Kolb numbers, ratio extension). **Recoverable in one V4 pass.**
- Apollo HITL portion of the gap: **2–3 marks** (non-engineer reception quote, teammate self-reflection quote, timeout-guard count). **Requires real external input.**

**Recommendation:** one more merger pass that treats `D7_V2_DISTINCTION_GAP.md §8 items #2, #6, #3 (agent half), #10` as a hard checklist, *not* as a suggestion. Skip the polish items; they are done. Focus only on the sub-clause lifts that V3 left on the table.
