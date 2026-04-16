# D7 V3b — Independent Score (Scorer B)

**Draft:** `report/personal_v2/` V3b (7 PDF pages)
**Slots:** `01_my_role.tex`, `02_my_team_alt.tex`, `03_my_impact_alt.tex`, `04_my_support.tex`
**Rubric:** `D7_SCORING_FINAL.md`
**Scored independently of Scorer A.**

---

## D7 FINAL SCORE: 77/100

Working-draft band (7pp). Final 5-page cut would need compression but the content is already at high-Distinction quality and would likely hold 75–78 after trimming.

---

## HARD GATES (§1)

| Gate | Verdict | Notes |
|------|---------|-------|
| Page limit (working ≤7) | PASS | 7 pages body — at the working-draft ceiling |
| Page limit (FINAL ≤5) | NOT YET | Would cap at 48 if submitted at 7pp — current version is a working draft |
| 4 required headings | PASS | My role / My team / My impact / My support (all present, verbatim variants) |
| 10 required questions | PASS — 10/10 | 1a, 1b, 1c, 2a, 2b, 2c, 3a, 3b, 4a, 4b all answered substantively |
| First-person voice | PASS | "I" dominant throughout every section; "we" only for genuine team action |
| Specifics ≥5 people / ≥3 dates / ≥1 conflict | PASS | Robin, Demetro, Edward, Sid, Pilot, PM (6); wk12/wk14/wk17/wk19/wk20/wk22, 2026-03-30, 2026-04-03 (multiple); 11-state FSM conflict + PM workload conflict (2) |
| Honesty — genuine weakness | PASS | "I trust my own hands more than I trust a conversation I have not had" (§1a); solo-work reflex; "I can only handle confrontation when it is mediated by writing" (§2b) |
| Feedback-to-others ≥1 specific episode | PASS | THREE specific episodes (Demetro FDR, Robin timeout, Pilot UI) each with teammate + action + observable behaviour change |
| AI policy | PASS | Strong personal voice, unforgeably specific |
| Media diversity ≥2 | PASS | Narrative prose (D7 itself), complaint letter, FDR speaking scripts, web ground station, blueprints, COLLEAGUE handoff docs, FIELD_QUICK_REF — ≥4 distinct media |
| Readability | PASS (visually) | Normal body size, consistent margins across 7 pages |
| Presentation | PASS | Consistent bold sub-headings (1a/1b/...), rubric map table on p1, good page fill |
| Evidence density | PASS | Nearly every claim anchored — commit hashes, line counts, dates |
| Alternative perspective | PASS | "I initially framed this as X — in fact it was Y" move appears 3+ times (§1a, §3a, §4a) |

**Hard gate caps triggered:** NONE (if treated as working draft). If assessed at 7pp as the final submission, CAP 48 applies.

---

## CRITERIA

### Teamwork: 76/100 — lower 70s band

**Band language earned:** "Consistently demonstrates effective teamworking and leadership skills … Able to manage conflict."

Evidence:
- **Conflict management (mandatory for 60+):** TWO named conflicts handled. (1) 11-state FSM disagreement with Robin → refactor + interface-widening resolution (not overruling). (2) PM workload tension → complaint letter, 6 iterations, PM pushback on 1 paragraph, rewritten together, all 5 names signed. Both have named parties, named mechanism, named outcome. This clears the 60+ gate decisively.
- **Leadership 2/5 threshold (mandatory for 70+):**
  1. Decision authority: wk14 call to build simulator despite no one asking; wk19 main.py refactor call
  2. Meta-work: progressive test ladder (0a-4), blueprint system, FIELD_QUICK_REF, interface workshop proposal
  3. Influence under disagreement: Robin FSM disagreement widened the interface rather than overruling
  4. Accountability for group outcome: signed complaint letter with all five names
  - Meets 4/5 — clears the gate cleanly.
- **Honest ownership language** where leadership not claimed ("owned", "drove", "championed")
- **Cross-team integration:** `passive_watch_2.py --robin` HTTP endpoint, Demetro script handoff

Not reaching 80+ because:
- Not framed as "outstanding creativity/flexibility responsive to group members' interests" — the self-critique is that the author worked *around* collaboration rather than *inside* it. This is honest and high-insight, but it deliberately refuses the 80+ descriptor.

### Self-management: 78/100 — mid 70s band

**Band language earned:** "Works autonomously demonstrating very good self-organisational skills and behaviours. Has a professional attitude to completing tasks."

Evidence:
- Autonomy: wrote simulator, state machine, test ladder, geofence, web GS, FDR scripts, complaint letter — all unassigned
- Professional attitude: 820 commits, 146 pytests, modularity audit of own code (3.0/5.0 self-score on main.py — ruthlessly honest)
- Dated delivery under hostile conditions: wk14–wk22 progression, responded to 3 cancelled flight days with pivot to bench + simulator
- Meta-organisation: blueprints, brain-dump.md, MEMORY.md, NICE_TO_HAVE.md, session logs

Not 80+ because the author explicitly names solo-work as a *failure mode* ("a castle while the town starved"), which is correct Insight but pulls Self-management back from "outstanding" — the draft earns 78 on consistency and professional attitude, not the 83+ "outstanding" band.

### Insight: 78/100 — mid 70s band (pushing on 80)

**Band language earned:** "Demonstrates ability to work autonomously and assess own strengths and weaknesses. Demonstrates ability to identify own weaknesses and implement an effective programme of self-development. Can provide effective feedback to others."

Evidence:
- **Peer feedback (mandatory for 70+):** 3 named episodes with teammate + week + specific thing + reaction + delivery self-critique + generalisable lesson. All three hit Section 9 Move #3 verbatim. The Demetro episode explicitly includes author self-critique ("my first three drafts were in my register, not his"). This is an 80+ quality feedback set.
- **Implementation of self-development programme:** the modularity audit (2026-04-03) IS a past-tense implemented programme — run the audit → scored own file 3.0/5.0 → refactored → measured Robin's behaviour change (opened state_machine.py, added 7 lines, pushed). Load-bearing.
- **Kolb deep-dive (§3a):** all four stages italicised and walked through the main.py refactor. Textbook Layer 3.
- **Schön one-liner:** ("reflection-in-action, Schön") appears parenthetically in the evidence bank via BGR story — not visible in current V3b draft page shots, so possibly dropped. (See "Weaknesses" below.)
- **Hatton & Smith Level 4 moves:** very high density — "uncomfortable realisation" appears 4+ times; "I initially framed this as X — in fact it was Y" appears 3+ times; identity-shift closing on §1c ("engineering leadership is less about X and more about Y"); counterfactual in §3b ("Had I acted on the shape of the file a month earlier…"). Average well above 2/page.
- **Evaluate vs reflect:** ≥3 paragraphs with criterion + judgement + cause + lesson (e.g. §3a Kolb cycle, §1c falsifiability test, §4b Robin bug-shape propagation).

Reason not 80+: the 83+ Insight band wants "confidence in working autonomously and setting own goals." The draft is confident but also self-flagellating — and one area (Schön name-drop, CV speed evaluation) could be sharper. The top-band "outstanding/creative/responsive" ceiling is narrowly missed.

### Communication (folded into Insight via M17)

Would score ~75.
- ≥4 media (report, diagram via Kolb table, web GCS demo, FIELD_QUICK_REF, complaint letter, speaking scripts)
- Non-technical audiences: PM (written letter adapted for tone/register — 6 iterations), pilot (minimalist button layout, RC thumb reach), Demetro (register shift to his voice). Three non-technical adaptations with reception evidence. Clears the 2/5 threshold.
- M17.d evaluation of methods: present implicitly in the Demetro story ("register not prose quality was the scarce resource") and the pilot story ("best UI is the one the pilot does not have to notice"). Could be more explicitly A/B — e.g. "narrative prose produced X follow-up questions, diagram 0, demo 2." Current version is qualitative, not A/B quantitative.

### Average: (76 + 78 + 78) / 3 = **77.3**

---

## AHEP4 COVERAGE (sub-clauses /48)

| Clause | Score | Evidence |
|--------|-------|----------|
| M16.a individual function | 3 | vision.py ownership, 820 commits, 146 pytests, specific file/date/metric |
| M16.b team member | 3 | passive_watch_2.py --robin interface, Demetro scripts handoff, PM letter |
| M16.c leader/owner | 3 | Leadership threshold met 4/5; plus honest language where not claimed |
| M16.d-own evaluate | 3 | §1c: criterion (teammate handoff ≤48h without ping) + judgement + cause + lesson |
| M16.d-team evaluate | 2 | §3a/§3b: refactor 8 weeks late, modularity audit → 3.0/5.0, Robin's 7-line fix as test. All 4 elements present but the team-level evaluation is slightly blended with the individual one — not fully split |
| M17.a complex content | 3 | Kolb table, 6-module architecture, GPS projection chain |
| M17.b technical audience | 3 | Robin's independent integration of vision stack in one session, no follow-up |
| M17.c non-technical audience | 3 | PM register shift, pilot RC-thumb layout, Demetro voice — 3 adaptations with reception |
| M17.d evaluate methods | 2 | Present in register/prose insight + UI minimalism, but no explicit A/B comparison of method effectiveness with counts (the rubric's ideal is "prose 3 follow-up questions, diagram 0, demo 2") |
| Bristol Comms ≥2 media | 3 | ≥4 distinct media |
| Bristol Comms 80 engaging | 2 | Pilot reception + Robin's downstream habit propagation |
| Quality: every claim has evidence | 3 | Commit hashes, line counts, dates — ruthless anchoring |
| Quality: alternative perspective | 3 | "I initially framed this as X — in fact it was Y" used 3+ times |
| Quality: forward-looking lesson | 3 | Falsifiability test (teammate completes handoff <48h), collaboration diagnostic (fortnightly check) |

**Sub-clause total: 39/48** → 70s band per §12 banding guide.

Sub-clause adjustment: (39/48) × 10 − 5 = **+3.1**

---

## BRISTOL L7 HIDDEN REQS (§5)

| Req | Verdict |
|-----|---------|
| Conflict management named | ✓ (2 named) |
| Leadership 2/5 threshold | ✓ (4/5) |
| Media diversity ≥2 | ✓ (≥4) |
| Peer feedback episode | ✓ (3 episodes, all with reaction + self-critique) |
| Evaluate (4 elements) | ✓ (present in multiple paragraphs, criterion+judgement+cause+lesson) |
| Decision-making 70+ (evidence-based decision under unfamiliar circumstances) | ✓ (flight cancellations → simulator pivot, wk14) |
| Logical argument 60+ (alternative perspectives) | ✓ ("one reading is X, another is Y" pattern) |

**All seven Bristol hidden caps cleared. No hidden cap triggered.**

---

## QUESTION COVERAGE: 10/10

| Q | Status | Reason |
|---|--------|--------|
| 1a roles allocated vs taken | ✓ strong | CV lead → infrastructure drift, named and explained |
| 1b most proud of | ✓ strong | Simulator + wk14 judgement call, not the artefact but the decision |
| 1c focus differently in future | ✓ strong | Falsifiable <48h teammate-handoff test + identity-shift close |
| 2a structure, discussed explicitly | ✓ strong | Whiteboard vs interface contract, "assumptions degrade silently" |
| 2b most impactful team elements | ✓ strong | Two conflicts told honestly — FSM + PM letter |
| 2c what would you change | ✓ strong | 90-min interface workshop wk1, fortnightly reflection round |
| 3a contributions that drove team forward | ✓ strong | 4-action table + Kolb deep-dive on refactor |
| 3b add/refocus in future | ✓ strong | Collaboration diagnostic with falsifiable trigger |
| 4a what others did for you | ✓ strong | 4 named people + specific mechanism each (Edward/Robin/Demetro/Pilot/Sid) |
| 4b what you did for others | ✓ outstanding | 3 feedback episodes, each a Section 9 Move #3 template |

**Question penalty: 0**

---

## HATTON & SMITH LEVEL 4 DENSITY

Scanning the 7-page draft for Level-4 moves (belief revision / reframing / assumption examination / counterfactual / alternative perspective):

- p1 (My role 1a): "uncomfortable realisation," "I now see I preferred the first framing because it protected me from…"
- p1 (1b): "uncomfortable realisation," "I had previously thought of engineering judgement as picking the right technique. This project forced me to reframe that"
- p2 (1c): identity-shift closing ("engineering leadership is less about X and more about Y"); modularity audit 3.0/5.0 self-score
- p2–3 (My team 2a/2b): "uncomfortable realisation was that our 'structure' had never been agreed — it had been *assumed*"; "what looked like a technical disagreement was actually an ownership-boundary disagreement"
- p3 (2b second conflict): "I had not previously noticed in myself that I can only handle confrontation when it is mediated by writing"
- p3 (2c): "a castle while the town starved"
- p4 (My impact 3a): "the file was not a capability: it was a bottleneck with my name on it"
- p4–5 (Kolb): all four stages named and walked through with belief revision at the end ("stopped treating modularity as engineering hygiene and started treating it as a form of team communication")
- p5 (3b): counterfactual ("Had I acted on the shape of the file a month earlier"); "the uncomfortable truth is that I will always drift toward solo ownership under stress"
- p6 (4a): "my instinct to 'finish debugging before asking for help' is a cost I pay, not a professionalism I exhibit"
- p6 (4b Demetro): self-critique of own delivery ("my first three drafts were in my register, not his")
- p6 (4b Robin): "habit propagated" observation
- p7 (4b Pilot): "the best UI is the one the pilot does not have to notice"
- p7 close: "building tools for others was my version of teamwork *because* I struggled with real-time collaboration — async handoff docs were emotional scaffolding for me as much as they were help for the recipient"

**~15+ Level-4 moves across 7 pages → well above 2/page target.** Cap not triggered; this is the single strongest driver of the 70s score.

---

## STRENGTHS (what is carrying the mark)

1. **Three feedback-to-others episodes** each hitting the Section 9 Move #3 template. This alone clears the Insight 70+ gate that most D7s miss. The Demetro self-critique ("first three drafts in my register, not his") is 80+ quality.
2. **Brutal honesty about solo-work reflex** framed as cultural and psychological, not just operational. This is the identity-shift closing the rubric explicitly rewards.
3. **Two conflicts told** — FSM and PM letter — both with mechanism, outcome, and documentation. Covers both the 60+ Teamwork gate and the higher-band "able to widen the interface so the argument becomes moot" move.
4. **Kolb deep-dive as a genuine learning cycle**, not a decorative citation. Italicised stages, belief revision as outcome, Robin's 7-line fix as the experiment's result. Textbook Layer 3.
5. **Evidence density** — commit hashes, line counts, file paths, dates, percentages, tests counts. The marker can verify any claim against the repo.
6. **Falsifiable forward commitments** — the <48h teammate-handoff test, the fortnightly collaboration diagnostic, the 60/40 solo/pair time cap. Not wishes, mechanisms.
7. **Hatton & Smith Level 4 density** is exceptionally high (~15+ moves over 7 pages).

---

## WEAKNESSES (what is holding the mark back from 80+)

1. **Working-draft page count (7pp).** If this is the final submission it caps at 48. Must compress to 5 pages for submission. Likely candidates for cuts: the Sid paragraph in 4a (not structurally load-bearing), the second half of the 4b infrastructure list, some of the framing in 1a.
2. **M17.d method evaluation is qualitative, not A/B.** The rubric's ideal is "narrative prose produced X follow-up questions; diagram 0; demo 2." Current draft has the insight but not the count. Adding two A/B sentences (Kolb diagram vs prose vs demo) would push Communication from 75 → 80.
3. **Team-level M16.d evaluation is blended with the individual one.** The rubric wants one own-evaluation paragraph AND one team-evaluation paragraph, each with all four elements. The team evaluation (R01–R12 matrix, 12/12 sim vs 4/12 real) is present but not framed as a dedicated paragraph.
4. **Schön name-drop possibly missing** from V3b (not visible in the page shots I reviewed; may have been dropped in this revision). Costs ~1 mark of theoretical literacy.
5. **Self-flagellation tone** — honest and insight-rich, but the 83+ band wants "confidence in setting own goals." The tone is uniformly "I failed at collaboration" rather than "I developed under pressure." One or two sentences of observable growth (e.g. "by wk20 I was pairing 30% of hours, up from 5% in wk14") would unlock the 80+ band without breaking the honesty.
6. **No quantified before/after on communication improvement** — the rubric exemplar is "D5 draft 1 had 7 reviewer comments, draft 3 had 1." Would add 1–2 marks of M17.d evaluation.

---

## FIXES TO REACH 80+ (final 5-page cut)

1. Compress to 5pp by cutting the Sid paragraph and trimming the 4b infrastructure list.
2. Add two A/B sentences to the Kolb paragraph: "Against Robin's comprehension (informal Q&A), the first all-in-one main.py produced zero successful contributions in two weeks; the six-module version produced his 7-line fix in twenty minutes."
3. Split M16.d into one explicit team-evaluation sentence: "Against the R01–R12 matrix, the team delivered 12/12 in simulation but 4/12 on real hardware — 3 of 8 gaps were bench work we did not prioritise, a coordination failure not an effort failure."
4. Add one observable-growth sentence in §1c: "By wk22 I had moved roughly 30% of my hours into pairing and handoff documentation, up from an estimated 5% in wk14 — not enough, but the direction was measurable."
5. Restore the Schön one-liner on the BGR permutation story if dropped.

Estimated after all fixes: **80–81**.

---

## SCORE CARD

```
D7 FINAL SCORE: 77/100 (working draft, 7pp)

HARD GATES (§1):
  [x] Page limit (working ≤7) → PASS
  [ ] Page limit (FINAL ≤5)   → NOT YET (would cap at 48 if final)
  [x] 4 headings → PASS
  [x] 10 questions → 10/10
  [x] Named specifics ≥5 people / ≥3 dates / ≥1 conflict → PASS (6/many/2)
  [x] Media diversity ≥2 → PASS (≥4)
  [x] First-person authenticity → PASS

CRITERIA:
  Teamwork:         76/100 — 2 conflicts managed, leadership 4/5, honest non-claim where not met
  Self-management:  78/100 — autonomous, professional, but self-named solo-work failure mode
  Insight:          78/100 — 3 feedback episodes, Kolb cycle, Level-4 density ~15+ moves
  Average:          77.3

AHEP4 COVERAGE:
  M16.a 3  M16.b 3  M16.c 3  M16.d-own 3  M16.d-team 2
  M17.a 3  M17.b 3  M17.c 3  M17.d 2
  Bristol add-ons 5  Quality multipliers 9
  Total: 39/48 → 70s band

BRISTOL HIDDEN REQS (§5):
  Conflict management:   ✓ (2 named)
  Leadership 2/5:        ✓ (4/5)
  Media diversity ≥2:    ✓ (≥4)
  Peer feedback:         ✓ (3 episodes)
  Evaluate (4 elements): ✓
  Decision-making 70+:   ✓ (simulator pivot)
  Alt perspectives:      ✓ (3+ reframings)

QUESTION COVERAGE: 10/10 (no penalty)

FINAL CALCULATION:
  base_score = 77.3
  sub_clause_adj = (39/48)*10 - 5 = +3.1
  question_penalty = 0
  hidden_cap = none
  raw = 80.4
  PRESENTATION ADJUSTMENT for working-draft 7pp: -3 (density not yet compressed, some load-bearing paragraphs could be tighter in a 5pp cut)
  FINAL: 77/100
```

If the 7pp draft were the final submission, the hard gate caps at 48. The 77 score assumes this is a working draft and will be compressed to ≤5pp without losing the load-bearing moves listed in Strengths.

---

## CONFIDENCE

**Confidence: HIGH (8/10)** on the 77 score.

- HIGH confidence (9/10) that the content clears the 70+ threshold on all three criteria — all five Bristol hidden caps cleared, AHEP4 sub-clause total 39/48, Level-4 density exceptional, 3 feedback episodes hitting Move #3. This report cannot score below 72 on content.
- HIGH confidence (8/10) on the 77 specific number — could justify 76, 77, or 78 equally well. The M17.d quantitative gap and the team-level M16.d split are the two things keeping it off 80.
- MEDIUM confidence (6/10) on how a real Bristol marker would handle the 7pp working-draft status. Strict reading = cap 48. Generous reading = score the content. I assume the caller wants content scored; if the caller wants hard-gate enforcement, the score is 48.
- HIGH confidence (9/10) that after the 5 fixes listed above, this reaches 80–81.

Known uncertainties:
- Could not confirm whether Schön one-liner is present in V3b (not visible in page shots I inspected); if dropped, costs ~1 mark.
- The page shots rendered some content in small font — possible I missed a paragraph that would affect a ±1 adjustment.
- The "team evaluation" M16.d score of 2 (not 3) is a judgement call — another marker could reasonably give 3 based on the Kolb experiment + R01–R12 pattern.

**Independent score (not compared to Scorer A): 77/100.**
