# D7 V3 — Independent Score (Scorer B)

**Artifact scored:** `main_v3.pdf` (6 pages total: 1 cover + 5 body) rendered as `v3_page-1.png` … `v3_page-6.png`
**Source slots:** `slots/v3/01_my_role.tex` … `04_my_support.tex`
**Rubric used:** `D7_SCORING_FINAL.md` (single source of truth)
**Scorer:** B (independent of Scorer A — A's output not read)

---

## HARD GATES (Section 1)

| Gate | Result | Evidence |
|------|--------|----------|
| Page limit (final ≤ 5 body) | PASS | Cover = p1; body = p2–p6 → 5 pages |
| 4 required headings | PASS | "My role" / "My team" / "My impact" / "My support" verbatim |
| 10 required questions | PASS (10/10) | All sub-parts 1a, 1b, 1c, 2a, 2b, 2c, 3a, 3b, 4a, 4b bolded in text |
| First-person voice | PASS | "I…" dominant; no hiding behind "we" in reflective paragraphs |
| ≥5 named people | PASS | Robin, Edward, Demetro, Sid, the pilot, PM, course organiser (7) |
| ≥3 dated incidents | PASS | 2026-03-11 field day, 2026-03-30 field day, 2026-03-31 02:14 commit, wk12 kickoff, wk17 FSM conflict, wk19 CENTERING feedback, wk20 Robin handoff |
| ≥1 named conflict | PASS | wk17 FSM disagreement with Robin+Demetro (named, managed, outcome stated); also wk20 PM complaint-letter conflict |
| Honesty (genuine weakness + action) | PASS | "infrastructure alone was a way of feeling productive" / "avoidance dressed as conscientiousness" / "I was right about the FSM and wrong about the context" |
| Feedback-to-others episode | PASS (3 distinct) | Demetro FDR scripts; Robin CENTERING timeout; Pilot ground-station lexical rewrite |
| AI policy (personal voice) | PASS | Highly distinctive voice — Ukrainian framing, specific commit hashes, thesis sentences that could only be this author |
| Media diversity ≥2 | PASS (≥6) | D6 report, pipeline diagram/doc, browser dashboard (ground station), live demo at FDR, complaint letter, Teams pivot message, FDR speaker scripts, blueprint docs |
| Readability floor | PASS | ~10pt, reasonable margins, no cramming visible in PNGs |
| Presentation / page fill | PASS | p2–p6 each ~90–95% filled, no orphans, rubric map table at top is a marker-friendly move |
| Alternative perspective | PASS | "I was right about the FSM and wrong about the context"; "sim-to-real parity… an argument I can only win about the things I modelled"; "What looked like a technical problem was actually a maintainability disagreement" |
| Evidence density | PASS | Nearly every claim anchored to commit hash, file, date, or named person |

**No hard-gate violations.** No caps triggered. Ceiling open to High Distinction range.

---

## CRITERIA SCORES

### Teamwork — 76/100

**Band earned:** 72–78 "Consistently demonstrates effective teamworking and leadership skills… Able to manage conflict."

- **Conflict management:** Cleanly hits it twice. The wk17 FSM compromise is a textbook managed conflict — named parties (Robin, Demetro), named mechanism (24-hour pause, reread Robin's script, proposed the `--robin` interface concession as a compromise), named outcome (wk20 integration in an afternoon, both teammates accepted). The wk20 PM complaint-letter story is a rarer and more sophisticated conflict-management episode — "externalising an internal conflict" via collaborative writing, plus genuine meta-insight ("I can only handle confrontation when it is mediated by writing… a pattern across my personal life, not just this project").
- **Leadership threshold (2/5):** Clears comfortably. Decision authority (1088 dataset, FSM architecture, simulation-first pivot), influence under disagreement (FSM compromise — *persuaded*, not overruled), meta-work (blueprint system, CLAUDE.md, test ladder, decision log proposal), and accountability for group outcome (complaint letter signed by all five). That's 4/5.
- **Working as member:** M16.b well served — Edward unblock on Python 3.13 pyserial → mavproxy UDP bridge; Sid's DJI video anchoring FOV calibration and retrained mAP50=0.995; explicit integration seam with Robin via `passive_watch_2.py --robin`.

**Why not higher:** The 80+ band needs "outstanding ability to work and lead a team with creativity and flexibility that is **responsive to group members' interests**." The report is searingly honest that the author did NOT fully meet this — 3b explicitly says "the number of times a teammate other than me edited `simple_simulator.py` or `main.py` was zero." That self-indictment is worth insight marks but by the rubric's own words it prevents an 80+ Teamwork mark. The author is asking for credit for *noticing* the responsiveness gap, not for closing it.

### Self-management — 78/100

**Band earned:** 72–78 "Works autonomously demonstrating very good self-organisational skills and behaviours. Has a professional attitude to completing tasks." — top of band, pushing into 80s.

- **Autonomy:** Overwhelming evidence. 611th commit at 02:14 the morning after a cancelled field day. 820+ commits. Self-directed 1411→754 line refactor with 146 pytest tests. Writing FIELD_QUICK_REF.md on the cancelled flight day "before dark." Six-week simulation-first campaign. 127 unit tests.
- **Professional attitude:** Rigorous — calibration measurement (5.46 mm focal length against tape measure), bug tracking with commit hashes, evidence-anchored claims, modular architecture choices with justifications.
- **Milestone delivery under adversity:** Three cancelled field days + still delivered a working state machine, simulator, web GCS, 146-test harness, and a retrained model at mAP50=0.995.

**Why not higher (80+):** The 80+ band wants "outstanding self-organisational skills" — the author *does* demonstrate something close to outstanding, and I was tempted to give 80. Held at 78 because (a) the author openly frames the work ethic as partly avoidance of a harder team-engineering skill, which is honest but self-limiting, and (b) a Self-management 80 typically also shows outstanding *allocation* judgement (knowing when to stop), whereas this report explicitly admits to going deeper than allocated. The rubric rewards autonomy, not volume-above-scope. Still, 78 is justified.

### Insight — 78/100

**Band earned:** 72–78, reaching into 80s on some criteria. "Demonstrates ability to work autonomously and assess own strengths and weaknesses. Demonstrates ability to identify own weaknesses and implement an effective programme of self-development… Can provide effective feedback to others to aid their self-development."

- **Peer feedback (load-bearing gate for 70+):** Three fully developed feedback episodes, each with named teammate, specific content, their reaction, behaviour change, AND a self-critique of the author's delivery. The Demetro register insight — "good feedback to a peer presenter means writing in their voice, not polishing yours" — is a Level-4 move. The Robin CENTERING timeout propagating into his "shape-of-bug" model is exactly the criterion + judgement + cause + lesson pattern the rubric rewards. The pilot lexical rewrite (jargon removal: "geofence repulsor active within 10m buffer" → "the drone pushes itself away from the red fence if it gets within 10m") is a textbook M17.c non-technical adaptation plus feedback loop.
- **Self-development implementation (load-bearing for 70+):** Demonstrated in past tense inside the project timeline — the wk17 FSM compromise came from a belief-revision move the author then applied ("I had been conflating 'is this the right design' with 'is this the right design *for this team*'"). That's an implemented programme, not a promise.
- **Hatton & Smith Level 4 density:** Multiple Level-4 moves per page. "The uncomfortable realisation was…" (p2); "I initially framed this drift as conscientiousness — in hindsight I now see it was partly avoidance" (p2); "I was right about the FSM and wrong about the context" (p4); "I had not previously noticed in myself that I can only handle confrontation when it is mediated by writing" (p4); "sim-to-real parity is an argument I can only win about the things I modelled" (p5); identity-shift closing on p6 ("the engineer who delivers alone is one recruitment away from being the single point of failure in whatever system she builds"). I count ≥2 Level-4 moves on every body page.
- **Alternative-perspective moves:** Multiple, including the sober closing of 3a that lists what simulation could *not* tell them (motion blur, descent stall, GPS timing lag).
- **Falsifiable forward commitments:** Plural — 48-hour handoff signal, internship 6-week "teammate edits my module unasked" test, two-hour-per-week teaching session, 500-line pair-refactor rule, each with an observable signal.

**Why not higher (80+):** The 80+ band wants "confidence in working autonomously AND setting own goals. Can assess own strengths and weaknesses. Able to identify AND implement… Can provide effective feedback." The report clears the 80 threshold on feedback-giving density and quality and on identity-shift depth. It's held at 78 because the implemented programme is mostly *forward-looking falsifiable signals* rather than *measured past-tense outcomes within this project*. The internship commitments are excellent but by definition cannot be evidenced. The one fully-closed self-development loop (FSM → `--robin` interface) is strong but singular. A confident 80 would show 2–3 closed loops with numbers attached.

---

## AHEP4 M16/M17 SUB-CLAUSE COVERAGE (/48)

| Sub-clause | Score | Evidence |
|---|---|---|
| M16.a Individual function | 3 | Commit 611, 820+ commits, refactor 1411→754 lines, 146 pytests, mAP50=0.995, double-scaling fix `7eb7cc8`, bbox fix `3d62e6a` |
| M16.b Team member | 3 | Edward pyserial unblock, Sid DJI video → FOV calibration, Robin HTTP interface concession, named cross-team integration points |
| M16.c Leader | 3 | Leadership 2/5 met (decision authority + influence under disagreement + meta-work + accountability), but honestly named as "owned/drove" not inflated |
| M16.d-own Self-eval | 3 | Criterion (teammate edits = 0), judgement (technical ≠ team leadership), cause (built infrastructure alone as avoidance), lesson (500-line pair-refactor rule) |
| M16.d-team Team-eval | 3 | Criterion (handoff ratio 5:1 author-to-teammate time; 12/12 sim vs 4/12 real-hardware implied by thesis), judgement, cause (task-division over cadence), lesson (weekly decision log) |
| M17.a Complex content | 3 | VISION_PIPELINE_FOR_COLLEAGUE.md 2400 words, `--robin` JSON/HTTP contract, FSM design with geofence repulsor |
| M17.b Technical audience | 3 | Robin integrated unaided for 2 days from doc; Edward accepted Cube interface; named reception |
| M17.c Non-technical audience | 3 | The PILOT lexical rewrite is a textbook example. Named audience (RC pilot), concrete before/after ("MAV_CMD_NAV_TAKEOFF ACK race" → "the drone sometimes doesn't lift off because it is waiting for a confirmation message that never comes"), feedback loop (read aloud in one pass), behaviour change (triggered abort three times without looking at screen) — hits 3 of 5 adaptation criteria (jargon removal, analogy, feedback loop) |
| M17.d Evaluate methods | 3 | Explicit italic header in 3a: "Methods evaluated against observable behaviour change per author-hour." Enumerates 6 methods, names criterion (behaviour change ≤48h), judgement (pivot msg + `--robin` flag won; 3000-word doc lost), comparison, lesson ("timing, pairing, and interface shape dominated prose quality") — this is the cleanest M17.d I've seen in any D7 |
| Bristol conflict management | 3 | wk17 FSM + wk20 complaint letter |
| Bristol peer feedback | 3 | Three named episodes with named teammate + content + reaction + self-critique |
| Bristol implemented self-dev | 2 | Strong but mostly forward-looking falsifiable signals; one closed loop in project (FSM compromise) |
| Quality: every claim evidenced | 3 | Commit hashes, file paths, line counts, dates everywhere |
| Quality: alternative perspective | 3 | Multiple, explicit |
| Quality: forward lesson to context | 3 | Named internship + observable 6-week signal |
| Bristol Comms 80 engaging | 2 | Engaging voice, strong scene-setting; reception evidenced for some media but not uniformly |

**Sub-clause sum:** ~44/48 → predicts 80s band per §12 banding guide.

`sub_clause_adjustment = (44/48) × 10 − 5 = +4.17`

---

## BRISTOL L7 HIDDEN REQUIREMENTS (§5)

| Requirement | Result |
|---|---|
| Conflict management (60+ floor) | ✓ (two episodes, both with mechanism) |
| Leadership 2/5 (70+ gate) | ✓ (4/5 — decision authority, influence, meta-work, accountability) |
| Media diversity ≥2 (60+ Comms) | ✓ (≥6 distinct media) |
| Peer feedback (70+ Insight gate) | ✓ (three episodes) |
| Evaluate 4 elements (65+ floor) | ✓ (multiple paragraphs with criterion/judgement/cause/lesson) |
| Decision-making 70+ (unfamiliar circumstance) | ✓ (simulation-first pivot after cancellation is textbook) |
| Logical argument 60+ (alternative perspectives) | ✓ (multiple) |

**No caps triggered.**

---

## HATTON & SMITH DEPTH TEST

Target: ≥2 Level-4 moves per body page. Counted:
- **p2 (Rubric map + intro 1a/1b):** 4 Level-4 moves (uncomfortable realisation, reframing, counterfactual, pattern recognition)
- **p3 (1b cont + 1c + 2a/2b intro):** 3 Level-4 moves (avoidance reframe, capability vs enablement reframe, unexplicit-structure lesson)
- **p4 (2b/2c):** 4 Level-4 moves (FSM framing reveal, technical-vs-context distinction, internal-confrontation insight, document-as-substitute lesson)
- **p5 (3a + 3b):** 3 Level-4 moves (Kolb walk, sim limits confession, technical-vs-team leadership reframe)
- **p6 (4a/4b + closing):** 4 Level-4 moves (register scarcity, bug-shape propagation, UI frame shift, identity-shift closing)

Average ~3.6/page — well above the 2/page target for 72+.

---

## 10-QUESTION COVERAGE (§7)

| Q | ✓/✗ | Strength |
|---|---|---|
| 1a | ✓ | Strong — explicit role at wk12 (CV only) + implicit drift (simulator, FSM, blueprints, letters) + honest shift narrative |
| 1b | ✓ | Strong — not the obvious answer (mAP50), but the refusal to let a missing drone become a missing report; counterfactual used |
| 1c | ✓ | Strong — capability/enablement distinction + falsifiable signal (48h handoff test) |
| 2a | ✓ | Strong — structure named, declined tech-lead role, two drifts narrated (silent wk16, loud wk17) |
| 2b | ✓ | Strong — handoff ratio 5:1 metric + wk17 FSM conflict fully developed |
| 2c | ✓ | Strong — three concrete changes with falsifiable signals (decision log, interface contracts, 500-word doc rule) |
| 3a | ✓ | Strong — full Kolb walk (all 4 stages named in italics), plus sim-limits confession, plus methods-evaluated sub-section |
| 3b | ✓ | Strong — technical vs team leadership reframe + three falsifiable signals |
| 4a | ✓ | Strong — four named people with specific mechanism for each |
| 4b | ✓ | Strong — three full feedback episodes with named teammate + content + reaction + self-critique |

**10/10. No question penalty.**

---

## EVIDENCE BANK (§11) — 12 LOAD-BEARING ITEMS

1. Quantified individual delivery — ✓ (611 commits, 2508 simulator lines, 146 pytests, mAP50=0.995)
2. Cross-team collaboration with interface — ✓ (`--robin` HTTP flag, DESIGN_DECISIONS.md:107–109)
3. Decision under uncertainty — ✓ (simulation-first pivot after cancellation)
4. Conflict + resolution — ✓ (wk17 FSM compromise; wk20 complaint letter)
5. **Self-evaluation (criterion+judgement+cause+lesson)** — ✓ (teammate-edits=0 criterion)
6. **Team-evaluation (4 elements)** — ✓ (handoff ratio 5:1; 12/12 sim vs real gap)
7. Two distinct media with audience — ✓ (≥6)
8. **Non-technical audience + 2/5 adaptation** — ✓ (pilot, jargon removal + feedback loop + analogy, 3/5)
9. **A/B comparison of comms methods** — ✓ ("Methods evaluated against observable behaviour change per author-hour" sub-section)
10. Peer development action — ✓ (3 feedback episodes)
11. Applied lesson in timeline — ✓ (wk17 FSM lesson → `--robin` interface → wk20 unaided integration)
12. Forward CPD with falsifiability — ✓ (internship 6-week test)

**12/12 — all load-bearing items present.**

---

## COMPUTED SCORE

```
base_score          = mean(76, 78, 78) = 77.3
sub_clause_adj      = (44/48 × 10) − 5 = +4.17
question_penalty    = 0
hidden_cap          = none
final_raw           = 77.3 + 4.17 − 0   = 81.5
```

Rounding to rubric tick: **81/100** (lands in the 80–82 zone of the 83+ High Distinction band's lower border).

### Head check against descriptor language

- Teamwork 76: within 72–78 band cleanly — consistent teamwork + leadership + conflict management all evidenced.
- Self-management 78: top of 72–78 band — autonomous delivery, professional attitude, milestone resilience, held from 80s only by honest self-indictment.
- Insight 78: top of 72–78 band — 3 peer-feedback episodes + identity shift + implemented programme (one closed loop + multiple falsifiable signals).
- Raw average 77.3 with AHEP4 coverage at 44/48 puts this at the top of Distinction shading into High Distinction.

## FINAL SCORE: **81/100**

---

## KEY STRENGTHS (what is earning the marks)

1. **The M17.d paragraph in §3a is the cleanest evaluation-of-methods I've seen in a D7** — explicit italic sub-header, enumeration of 6 methods with audiences, criterion named, judgement with specific outcomes, comparative lesson that contradicts the author's prior belief.
2. **Three feedback episodes with self-critique of delivery.** Most D7s stop at "I gave feedback, they accepted it." This report adds "and my first three drafts were in my register not his" — that's the Insight 80 move.
3. **Identity-shift closing** ("the engineer who delivers alone is one recruitment away from being the single point of failure") is a clean Move #10 from §9.
4. **Honest weakness framed as a mechanism, not a humblebrag.** "Infrastructure alone was a way of feeling productive" reads as genuine, not as "my weakness is caring too much."
5. **Commit-hash density.** Every claim anchored to a file, a date, or a commit. Marker can spot-check.
6. **Rubric map table at top of p2** — implicit marker-friendliness worth ~1–2 marks of goodwill.
7. **Thesis-driven 3a.** "The simulation framework we built ourselves is the only reason this project produced any verifiable engineering output at all." Defended with mechanism, not asserted, then sober-closed with what simulation could *not* tell them.

## WEAKNESSES (what is holding it below 85)

1. **Self-indictment on responsiveness.** The honest admission that zero teammates edited the author's major files is a Level-4 move but by the rubric's own words it blocks an 80+ Teamwork mark — the rubric asks for *responsiveness to group members' interests*, and the report openly says this did not fully happen.
2. **Implemented self-development programme is mostly forward-looking.** The FSM→`--robin` closed loop is excellent but singular. A second or third closed loop with measured in-project outcome would push Insight into the 80s cleanly.
3. **Volume-above-scope framing.** 611 commits and a 2508-line simulator demonstrate autonomy, but in places the report reads as "I did more than was allocated" which can read to a conservative marker as scope drift rather than as self-management virtue. The report partially defuses this with the avoidance reframe but the defusing is itself a self-limit.
4. **Some language is still defensive around ambition.** The counterfactual framing ("had I acted a week earlier we'd have saved five days") is good reflection but subtly deflects the larger question of whether the simulation focus should have been the plan from wk1.
5. **No explicit Gibbs/Kolb citation year on first use in 3a for Kolb** — I see "Kolb (1984)" inline, so this is fine. Schön (1983) also cited. Hatton & Smith (1995) also cited. All three frameworks are *applied* not *decorated* — good, but there is no explicit Bristol L7 "programme of self-development" language that a marker scanning for rubric verbatim would tick.

## WHAT WOULD PUSH THIS TO 85+

- One more closed self-development loop with a measured in-project before/after (e.g., "my first D5 draft received 7 reviewer comments on clarity; my third draft received 1, after I adopted the claim-evidence-warrant structure").
- One sentence using the verbatim rubric phrase "effective programme of self-development" or "effective feedback to others" to give the marker a tick-box hook.
- A more forceful closing of the responsiveness-gap story — not collapsing into "I failed at it," but reframing as "here is the mechanism I used to start closing it within the project timeline" (the `--robin` flag does this implicitly; saying it explicitly would convert the self-indictment into an implemented lesson).

---

## CONFIDENCE

**Point estimate:** 81/100
**Plausible range:** 78 – 84
**Confidence:** Medium-high on the band (80s Distinction territory is robust); medium on the exact point within that band.

### Sources of uncertainty
- **±2 on Teamwork:** A generous marker may read the honest responsiveness-gap admission as insight (→ 78) rather than as a ceiling-blocker (→ 76). A strict marker may hold at 74 citing the zero-teammate-edits metric as disqualifying for 70+.
- **±2 on Insight:** Marker preference on "implemented programme" strictness. A marker who accepts the FSM→`--robin` loop + 3 feedback episodes + identity shift as "programme implemented" gives 80. A stricter reader wanting 2–3 closed loops with numbers stays at 76.
- **±1 on Self-management:** Close to the 80 boundary; reasonable markers split 77–80.
- **Sub-clause adjustment:** My 44/48 AHEP4 count could plausibly be 42 or 46 depending on how strictly "closed loop" is enforced. That is ±0.4 on the final number.
- **Hidden-cap risk:** None identified. All gates clear.

### Most likely outcomes
- **Most likely (55%):** 80–82 (solid Distinction, approaching High Distinction)
- **Upper plausible (25%):** 83–84 (crosses into High Distinction band on a generous read of peer-feedback quality and M17.d clarity)
- **Lower plausible (15%):** 77–79 (strict marker holds Teamwork at 74 on the responsiveness admission)
- **Tail (5%):** 76 or 85+ — both possible but would require an unusual marker stance

### Ranking against scoring doc examples
This draft clears all 12 evidence-bank items, clears all 5 Bristol hidden gates, clears the 10/10 question coverage, clears Hatton & Smith Level-4 density at 3.6/page, and lands M16.d + M17.d cleanly. Per §12 banding guide (sub-clause sum 43+ → 80s), the 80s band is the defensible band. I pick 81 within it because the criteria-average holds at 77.3 and the AHEP4 uplift is +4.17 — arithmetic says 81.5, rubric shading says "top of Distinction, just into HD."

**Final: 81/100, plausible range 78–84.**
