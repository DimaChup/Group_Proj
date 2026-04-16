# D7 V2 — Independent Score Card (Reviewer A)

**Artefact:** `report/personal_v2/main_v2.pdf` (7 PDF pages: 1 cover + 6 body)
**Sources cross-read:** `slots/01_my_role.tex`, `02_my_team.tex`, `03_my_impact.tex`, `04_my_support.tex`
**Rubric:** `D7_SCORING_FINAL.md` (authoritative)
**Reviewer posture:** Harsh, independent. Did not read V1 scores.

---

## 1. HARD GATES (§1)

| Gate | Rule | Result | Cap triggered |
|------|------|--------|---------------|
| Page limit — working draft | ≤ 7 body pages | **6 body pages** → PASS working | none |
| Page limit — FINAL submission | ≤ 5 body pages | **6 body → FAIL** | **CAP 48** (if submitted as-is) |
| 4 required headings | My role / team / impact / support | **PASS** (all four, verbatim) | none |
| 10 required questions | 1a–4b all answered | **10/10 answered strongly** | none |
| First-person voice | "I" dominant | **PASS** — "I" is the subject in every reflective paragraph. "We" used only factually. | none |
| Specifics — ≥5 named people | Robin, Demetro, Edward, pilot, Sid, PM | **6/6** → PASS | none |
| Specifics — ≥3 dated incidents | wk12, wk14, wk17, wk19, wk20, 2026-03-11, 2026-03-30, 2026-04-03 | PASS | none |
| Specifics — ≥1 named conflict | wk17 FSM conflict, parties, mechanism, outcome | PASS | none |
| Honesty — ≥1 weakness + action | Solo-work instinct; Ukrainian-engineering framing; handoff vs pairing | PASS | none |
| Feedback-to-others | 3 episodes: Demetro, Robin, pilot | PASS | none |
| AI policy (Cat 2 Minimal) | Personal voice unforgeable | **PASS** — voice is idiosyncratic, honest, not boilerplate | none |
| Media diversity ≥ 2 | Docs, code/flag, HTTP interface, slides, scripts, letter, web dashboard, test ladder | **PASS** (6+ distinct media) | none |
| Readability — 10pt, 1.05 spacing, 1.8–2 cm margins | Body at ~10pt, compact, legible | PASS | none |
| Presentation — consistent, 85–95% fill | Pages 2–6 dense; p1 cover; p7 (partial) | p7 not fully filled — ~40% fill | soft −1 |
| Evidence density | Every major claim anchored to commit/date/artefact | PASS | none |
| Alternative perspective | "one reading is X, another is Y" | Present (Kolb 3a limits paragraph, wk17 "right design vs right design for this team") | PASS |

**THE LOAD-BEARING GATE:** Final submission is 5 pages. Current is 6 body pages. **If V2 is submitted unchanged, CAP 48.** This is the single most important finding — everything below is conditional on the page being cut to 5 before submission. I score below as if the 6→5 cut happens cleanly (no content loss); if it does not, replace the final score with 48.

---

## 2. BRISTOL L7 HIDDEN GATES (§5)

| Hidden gate | Requirement | Met? | Evidence |
|-------------|-------------|------|----------|
| **Conflict managed** (60+ Teamwork) | Named parties + mechanism + outcome | **YES** | wk17 FSM conflict: Robin + Demetro pushed back on 11-state FSM; 24 h reflection; compromise via `--robin` HTTP flag in `passive_watch_2.py`; wk20 integration "an afternoon instead of a week". Parties named, mechanism explicit (interface concession, not persuasion-by-rhetoric), outcome measured. |
| **Leadership 2/5** (70+ Teamwork) | 2 of: decision authority, delegation, influence, accountability, meta-work | **YES (4/5)** | (1) Decision authority: wk14 simulator-build call; (2) delegation: Edward (SITL home fix) + Demetro (FDR slot forward); (3) meta-work: blueprint system, CLAUDE.md, FIELD_QUICK_REF.md, modularity audit; (4) accountability: drafted group complaint letter that team signed. Influence under disagreement partial (wk17 resolved by structural concession, not persuasion). |
| **Media diversity ≥ 2** (60+ Comms) | ≥2 distinct media with audience | **YES** | (a) Docs: `VISION_PIPELINE_FOR_COLLEAGUE.md` for Robin; (b) Code-as-comms: `--robin` flag + JSON schema; (c) Slide deck + speaking scripts for Demetro's FDR; (d) Web dashboard for pilot; (e) Complaint letter for course organiser; (f) Teams pivot message for team. 6 distinct media, each with named audience. |
| **Peer feedback given** (72+ Insight) | Named teammate + specific + reaction + self-critique + mechanism | **YES (3 episodes)** | (i) Demetro FDR scripts — iterated 4–5×, pushback on register, self-critique "my first three drafts were in my register, not his", behaviour change (numbers-not-adjectives carrying into his next deck). (ii) Robin CENTERING timeout — named variable `consecutive_lost`, fix landed same afternoon, downstream propagation ("looking for that shape of bug"). (iii) Pilot button layout — density critique accepted, 4-button set, RC-thumb pattern, pilot re-applied demand to VERIFY screen. All three pass the §9 Move #3 template. |
| **Evaluate (4 elements)** (65+) | Criterion + judgement + cause + lesson | **YES, multiple times** | (1) Own evaluation — `main.py` modularity audit scored 3.0/5.0 "weakest module was the one I spent most hours on alone"; (2) Team evaluation — sim-to-real pivot: 12/12 R-reqs in sim, thin delta on Pi, but modelled ≠ unmodelled (motion blur, descent stall, GPS lag); (3) Comms evaluation — 5:1 handoff-hours ratio (4h docs → 20h Robin unblocked), versus 3000-word colleague doc "sat unread until Robin finally needed it" (A/B comparison built in). |

**All five hidden gates are met.** No hidden caps triggered.

---

## 3. CRITERIA SCORES (§3)

| Criterion | Score | Band descriptor earned | One-line reason |
|-----------|-------|------------------------|-----------------|
| **Teamwork** | **74/100** | 72–78 "Consistently demonstrates effective teamworking and leadership skills … manage conflict." | Named conflict managed via structural concession + delegation + accountability + meta-work. Does NOT hit 80 band because leadership was mostly meta-work and decision authority, not "creativity and flexibility responsive to group members' interests" — the candidate explicitly diagnoses that solo-building was a *failure mode* of leadership, not an example of it. |
| **Self-management** | **75/100** | 72–78 "Works autonomously … very good self-organisational skills … professional attitude." | Autonomous to the point of self-criticism. 2508-line simulator, 1411→754 refactor, 146 pytest, blueprint system, progressive test ladder — all self-directed. Honest diagnosis that autonomy tipped into solo-heroism caps it below 80 band (outstanding would require evidence that the programme of self-development was *implemented* with observable team-facing outcomes, not just personal ones). |
| **Insight** | **74/100** | 72–78 "Identify own weaknesses and implement an effective programme of self-development … provide effective feedback to others." | Three peer-feedback episodes with behaviour change. Implemented programme: wk14 decision to build simulator changed by wk18 to explicit pivot-and-delegate; wk17 FSM conflict changed his stance on "right design *for this team*"; 2026-04-03 modularity audit produced the 60/40 solo/pair commitment with falsifiability test. Below 80 because the implemented programme is framed forward-looking (next project), not completed inside project timeline with teammate-side measurable improvement that the candidate did not author himself. |

**Average: (74 + 75 + 74) / 3 = 74.3**

---

## 4. AHEP4 COVERAGE (sub-clauses /48, §12 Step 3)

| Clause | Score /3 | Evidence |
|--------|----------|----------|
| **M16.a** — individual contribution (file/date/metric) | 3 | `vision.py` owned; 2508-line simulator; 1411→754 refactor; 146 pytest tests; commits dated. |
| **M16.b** — cross-team with named interface | 3 | Edward's pymavlink UDP bridge fix (wk15); Robin's HTTP handoff `--robin` flag (a5b1ab7); Demetro FDR slides (32fb0c5). |
| **M16.c** — leadership (2/5) OR ownership language | 3 | 4/5 threshold met; honest "leadership-without-title" framing avoids overclaim. |
| **M16.d-own** — self-eval (4 elements) | 3 | Modularity audit: criterion (0–5 scale), judgement (3.0), cause ("the one I spent most hours on alone"), lesson (60/40 solo/pair cap with falsifiable 48h signal). |
| **M16.d-team** — team eval (4 elements) | 3 | Sim-to-real pivot: criterion (R01–R12 matrix), judgement (12/12 sim, thin Pi delta), cause (asymmetry between laptop-accessible and hardware-bound work), lesson (sim-first is "a claim about what the discipline owes"). Second team eval (wk17): FSM design "right, but wrong for this team" — explicit causal attribution. |
| **M17.a** — complex content communicated | 3 | `VISION_PIPELINE_FOR_COLLEAGUE.md`; TFLite→undistortion→GPS chain; JSON schema. |
| **M17.b** — technical audience reception confirmed | 3 | "Robin wired passive_watch into his mission script without asking me a single clarifying question for two days"; Edward acting on Cube advice; both are confirmed reception. |
| **M17.c** — non-technical audience + adaptation (2/5) | **2** | Pilot is the strongest non-technical case: audience named, adaptation shown (density→4 buttons mapped to RC thumb-reach), feedback loop (pilot asked for same on VERIFY). Complaint letter to course organiser is borderline (organiser is still an academic audience) — counted as supporting. Missing: no explicit jargon-removal before/after, no explicit visual-substitution paragraph. 2/5 threshold met but only just; cannot score 3. |
| **M17.d** — evaluation of methods | **2** | Has the A/B comparison (4h docs → 20h Robin unblocked at 5:1; contrast with 3000-word doc that "sat unread"). Has criterion and judgement. Does NOT enumerate methods as a list with per-method criterion-and-score — the comparison is implicit in prose. One clean paragraph short of a 3. |
| **Bristol add-on 1** — Conflict management | 3 | wk17 FSM conflict, full template. |
| **Bristol add-on 2** — Implemented self-dev programme | 2 | Programme stated with mechanisms; falsifiability tests present; but most of the "implementation" is explicitly next-project. Modularity audit lesson is the one piece that landed inside project timeline. |
| **Quality mult 1** — every claim has evidence | 3 | Commit hashes, line counts, dates, named teammates throughout. |
| **Quality mult 2** — alternative perspective | 3 | "Right design vs right design for this team"; sim could/couldn't tell us; technical vs maintainability framing. |
| **Quality mult 3** — forward-looking lesson tied to future | 3 | 60/40 cap, 500-line pairing rule, 2 h/week teaching sessions, all with 48 h falsifiability signals. |

**Total: 39/48**

§12 banding: **sum 35–42 → 70s (M16.d and M17.d landed; Bristol 70-band hit on all three)** — this matches the criterion scores above.

Sub-clause adjustment: (39/48 × 10) − 5 = **+3.1**

---

## 5. HATTON & SMITH LEVEL 4 DEPTH COUNT

Target: ≥2 Level-4 moves per body page × 6 pages = **≥12**.

Level-4 move = explicit examination of assumption / reframing / belief revision / "I now see this is because…".

| Page | Level-4 moves identified | Count |
|------|--------------------------|-------|
| p2 (My role 1a/start 1b) | (1) "I initially framed this as 'the team needs infrastructure' — in fact it was closer to 'I trust my own hands more than a conversation I have not had' … I preferred the first framing because it protected me from noticing the second." (2) "my instinct under uncertainty is to convert anxiety into code." | 2 |
| p3 (My role 1b/1c + My team 2a start) | (3) "I had previously thought of engineering judgement as picking the right technique… judgement is also choosing when to stop trusting the stated constraints." (4) "I grew up inside a Ukrainian engineering culture… that instinct served me but also let me quietly take work off teammates." (5) "I did not understand before this project that unexplicit structure is a luxury which only survives in slack-rich teams." | 3 |
| p4 (My team 2b/2c — conflict + ebi) | (6) "I had been conflating 'is this the right design' with 'is this the right design *for this team*,' and these two kinds of rightness can come apart. I was right about the FSM and wrong about the context." (7) "handoff docs as a cost I paid for politeness" → reframed as 5:1 economics. (8) "any document longer than 500 words must be paired with a 15-minute walkthrough… or I treat it as unsent." | 3 |
| p5 (My impact 3a Kolb) | (9) "the simulation framework was not a backup plan but a *statement*: verifiable engineering is possible without hardware access." (10) "the limits of that statement are also true: sim-to-real parity is an argument I can only win about the things I modelled." (11) "I mistook technical leadership for team leadership. I now see they are orthogonal — you can build great tools that do not enable anyone." | 3 |
| p6 (My support 4a/start 4b) | (12) "my instinct to 'finish debugging before asking for help' is a cost I pay, not a professionalism I exhibit." (13) "I had framed as a technical disagreement was actually a maintainability disagreement, and I preferred the technical framing because it protected me from noticing I had built something only I could read." | 2 |
| p7 (4b feedback + close) | (14) "the scarce resource was register, not prose quality." (15) "specificity is the scarce resource, not softness." (16) "building tools for others was my version of teamwork *because* I struggled with real-time collaboration — async handoff docs were emotional scaffolding for me as much as they were help for the recipient." | 3 |

**Total Level-4 moves: 16 across 6 body pages (2.67/page average)**

Target met and exceeded. No ceiling penalty. This is the single strongest dimension of V2 — it is a genuine Hatton-Level-4 document. If anything, a harsh marker might say it borders on over-exposure (the report is so relentlessly self-critical that the reader occasionally craves one paragraph of plain accomplishment for contrast).

---

## 6. FAILURE MODES (§10) — 20 MODES SCAN

| # | Mode | Present? | Note |
|---|------|----------|------|
| 1 | Chronological trap | ✗ clean | Structure is by question, not by week. Weeks cited but as evidence, not scaffold. |
| 2 | Generalised teamwork platitudes | ✗ clean | Zero platitudes. |
| 3 | Hidden self-praise / humblebrag | ✗ clean | "I worked too hard" is stated but explicitly diagnosed as a *failure mode*, not a brag. |
| 4 | Unsupported leadership claims | ✗ clean | Claims limited to "leadership-without-title"; hedged appropriately. |
| 5 | Conflict-free narrative | ✗ clean | wk17 conflict explicit. |
| 6 | Feedback in passive voice | ✗ clean | All three feedback episodes first-person active. |
| 7 | Defensive retract | ✗ clean | No "constraints made it unavoidable". |
| 8 | Triumphalism | ✗ clean | Closing is sober: "the limits of that statement are also true". |
| 9 | Tools-and-tech padding | ✗ clean | Tools named only as evidence of specific claims. |
| 10 | Decorative framework citation | ✗ clean | Kolb used structurally (stages named), Schön in Hatton-style reflection moves (implicit). **BUT:** Schön is NOT explicitly named as a parenthetical label on the BGR debug story — §6 Layer 4 says to drop "reflection-in-action (Schön)" once. **Missed +1 mark.** Hatton & Smith not explicitly cited either. |
| 11 | Vague future commitments | ✗ clean | 48 h signal, 60/40 cap, 500-line pairing rule. |
| 12 | Hiding behind "we" | ✗ clean | "I" is the subject. |
| 13 | Metrics as substitute for reflection | ✗ clean | Metrics are evidence, not substitute. |
| 14 | Perfect-past syndrome | ✗ clean | "I could not articulate at the time" — explicitly honest about what he didn't see in the moment. |
| 15 | Feedback-free feedback paragraphs | ✗ clean | All three have named reaction + behaviour change. |
| 16 | "Learning" confused with "reflecting" | ✗ clean | Input/output distinction respected. |
| 17 | Gibbs as rigid 6-heading template | ✗ clean | Not used. |
| 18 | Bulleted lists where prose is needed | ✗ clean | Prose throughout. Rubric-map table is a legitimate assessor-friendly device. |
| 19 | Closing with lessons-learned bullet list | ✗ clean | Prose closing. |
| 20 | "This report will…" opener | ✗ clean | Opens with 1a straight into specific evidence ("At the wk12 kickoff I was explicitly allocated…"). Not a literary opener but also not the banned one. |

**Failure modes detected: 0 hard / 1 soft (Schön not explicitly named, −1 theoretical-literacy credit).**

---

## 7. EVIDENCE BANK (§11) — 12 LOAD-BEARING ITEMS

| # | Item | Present? | Where |
|---|------|----------|-------|
| 1 | One quantified individual-delivery metric | ✓ | 2508 lines, 1411→754 refactor, 146 pytest, mAP50 0.995 |
| 2 | Cross-team collab with named interface | ✓ | Edward's pymavlink UDP bridge; `--robin` HTTP flag |
| 3 | Decision under disagreement/uncertainty | ✓ | wk14 simulator build; wk18 pivot-and-delegate; wk17 FSM compromise |
| 4 | Conflict + resolution | ✓ | wk17 FSM, parties + mechanism + outcome |
| 5 | **Self-evaluation (4 elements) [LOAD-BEARING]** | ✓ | Modularity audit, 3.0/5.0, causal, lesson |
| 6 | **Team-evaluation (4 elements) [LOAD-BEARING]** | ✓ | R01–R12 12/12 sim, delta analysis |
| 7 | Two distinct media + audiences | ✓ | Doc (Robin), flag (Robin), slides+scripts (Demetro → FDR audience), dashboard (pilot), letter (organiser), Teams pivot (team) |
| 8 | **Non-tech audience + adaptation [LOAD-BEARING]** | ◐ partial | Pilot is clean (density→4 buttons, RC thumb-reach). Before/after jargon removal not made explicit. Still passes the 2/5 threshold. |
| 9 | **A/B or before/after comms comparison [LOAD-BEARING]** | ✓ | 4h docs → 20h Robin (5:1) vs 3000-word doc "sat unread". |
| 10 | Peer-development action (feedback applied) | ✓ | Robin CENTERING timeout → fix + downstream "looking for that shape of bug". |
| 11 | Applied lesson with measurable outcome *inside* project | ◐ partial | wk17 compromise → wk20 afternoon integration is in-timeline. 60/40 cap, 500-line rule are forward-only. 1 in-timeline applied lesson present; rubric says "one" → met. |
| 12 | Forward-looking CPD plan with falsifiability | ✓ | 60/40 cap + 48 h handoff signal; 500-line pairing rule; 2 h/week teaching sessions with test. |

**12/12 items present; #8 and #11 are partial but pass.** The four load-bearing items (5, 6, 8, 9) all land. No cap triggered.

---

## 8. PER-PARAGRAPH 7-POINT HEURISTIC (§13) — SAMPLE 5 PARAGRAPHS

### Sample 1 — 1a ¶2 ("It was not ambition…")
1. Specific named incident? ✓ wk14, wk17, wk20 | 2. "I"? ✓ | 3. Revises a belief? ✓ reframes "duty" as "teammate quietly absorbing four roles" | 4. Self-crit specific/actionable? ✓ structural pattern | 5. Avoids failure modes? ✓ | 6. Falsifiable forward? N/A (belongs to 1c) | 7. Cynical marker: "did anything change?" → handled by 1c commitments.
**Verdict: Level 4. Distinction-band.**

### Sample 2 — 1b ¶2 ("What I am actually proud of…")
1. Incident? ✓ wk14 | 2. "I"? ✓ | 3. Belief revision? ✓ "I had previously thought of engineering judgement as picking the right technique" → reframed | 4. Self-crit specific? ✓ "technical insurance policy *and* psychological one" | 5. Failure modes? Borderline #3 (pride claim) — but disarmed by diagnostic framing | 6. Falsifiable? N/A | 7. Cynical marker? Covered.
**Verdict: Level 4.**

### Sample 3 — 2b ¶2 (wk17 FSM conflict)
1. Incident? ✓ wk17, commits ce5c036 | 2. "I"? ✓ | 3. Reframe? ✓ "right design" vs "right design for this team" | 4. Specific, proportionate? ✓ "half of my insistence was that the FSM was my code" | 5. Failure modes? ✓ clean | 6. Falsifiable forward? ✓ interface contract rule | 7. Cynical marker? ✓ wk20 integration "afternoon instead of a week".
**Verdict: Level 4. The single strongest paragraph in the report.**

### Sample 4 — 3a Kolb ¶ ("The anchor is a full Kolb cycle…")
1. Incident? ✓ three cancelled flight days | 2. "I"? ✓ | 3. Reframe? ✓ simulation as *statement* not *backup* | 4. Self-crit? Present in the sober closing "could not tell us what it could not tell us" | 5. Failure modes? ✓ Kolb used structurally, not decoratively | 6. Falsifiable? ✓ R01–R12 matrix | 7. Cynical marker? Addressed via delta acknowledgement.
**Verdict: Level 4. Earns the Kolb theoretical-literacy mark.** One nit: the paragraph is ~420 words — longest in the report — and flirts with §8 density target. Could tighten.

### Sample 5 — 4b ¶2 (Robin CENTERING timeout feedback)
1. Incident? ✓ wk19, `consecutive_lost`, `4_detect_and_center.py` | 2. "I"? ✓ | 3. Reframe? Partial — this paragraph is mostly S-T-A-R with a reflection tail, the reframe is lighter than 2b | 4. Self-crit? ✓ "specificity is the scarce resource, not softness" | 5. Failure modes? ✓ | 6. Falsifiable? Indirect — the downstream "shape of bug" is a naturalistic outcome, not a designed test | 7. Cynical marker? ✓ observable propagation into Robin's own modules.
**Verdict: Level 3–4 transitional. Passes the Insight-72+ template cleanly; the Level-4 move is in the final generalisation, not the narrative. Would not be out of place in a 72 scoring but slightly below the density of 2b.**

**5/5 sampled paragraphs pass; 4 are unambiguously Level 4; 1 (sample 5) is transitional.**

---

## 9. QUESTION COVERAGE (§7) — 10/10

| Q | Landed? | Strength |
|---|---------|----------|
| 1a Roles explicit vs implicit, changed? | ✓ | Strong. "CV lead → everything infrastructure" shift, named drivers. |
| 1b Most proud of | ✓ | Strong. Simulation framework *and* the judgement call to build it. |
| 1c Focus differently | ✓ | Strong. 60/40 cap, 48 h falsifiable signal, identity-shift closing. |
| 2a Structure, discussed, changed | ✓ | Strong. Two drifts named (silent wk16, loud wk17), renegotiation recorded in DESIGN_DECISIONS.md:107–109. |
| 2b Most impactful | ✓ | Strong. Handoff-doc 5:1 ratio + Demetro FDR iteration. Doubles as conflict paragraph. |
| 2c Change next time | ✓ | Strong. Three specific mechanisms each with falsifiability signal. |
| 3a Contributions drove team | ✓ | Strong. Kolb structured, sober limits acknowledged. |
| 3b Add/refocus future | ✓ | Strong. Three mechanisms with tests. |
| 4a Others helped me | ✓ | Strong. 5 named people, specific mechanisms each. |
| 4b **I helped others** ← Insight-72+ gate | ✓ | Strong. 3 episodes (Demetro / Robin / pilot), each with reaction + behaviour change + self-critique. |

**No question penalty. 0 deduction.**

---

## 10. SCORING ALGORITHM (§12 Step 7)

```
base_score            = mean(74, 75, 74)             = 74.33
sub_clause_adjustment = (39/48 × 10) − 5             = +3.13
question_penalty      = 0
hidden_cap (pre-page) = none
final (pre-page-gate) = 74.33 + 3.13 − 0             = 77.46
```

Apply Schön-not-named soft penalty (§6 Layer 4 missed credit): −0.5 → **76.96**
Apply p7 fill penalty (~40%, breaks §8 density target): −0.5 → **76.46**

### Final numbers

**If page limit is cut to 5 before final submission (V2 content preserved):**
## FINAL SCORE: **76 / 100** (high Distinction band, 72–78)

**If V2 is submitted at 6 body pages (current state):**
## FINAL SCORE (capped): **48 / 100**

The page gate is the single binary that decides between these two outcomes.

---

## 11. SCORE CARD SUMMARY (§12 format)

```
D7 V2 FINAL SCORE: 76/100 (conditional on 5-page cut)
                   48/100 (current 6-body state, CAPPED)

HARD GATES (§1):
  [x] Page limit working (≤7)     PASS (6 body)
  [ ] Page limit FINAL (≤5)       FAIL — CAP 48 if submitted
  [x] 4 headings                  PASS
  [x] 10 questions                10/10
  [x] Named specifics             6 people, 8+ dated incidents, 1 conflict
  [x] Media diversity ≥2          6 media, all audience-named
  [x] First-person authenticity   PASS
  [x] Readability                 PASS
  [~] Presentation                p7 ~40% filled (density miss), −0.5

CRITERIA:
  Teamwork:         74/100 — conflict managed + leadership 4/5 + honest framing; below 80 because leadership was meta-work
  Self-management: 75/100 — autonomous to the point of self-diagnosis; 80+ needs outward-facing programme outcomes
  Insight:         74/100 — three feedback episodes with behaviour change; implemented programme mostly forward-looking
  Average:         74.3/100

AHEP4 COVERAGE (sub-clauses /48):
  M16.a 3   M16.b 3   M16.c 3   M16.d-own 3   M16.d-team 3
  M17.a 3   M17.b 3   M17.c 2   M17.d 2
  Bristol conflict 3   Bristol implemented 2
  Quality mult: evidence 3 / alt-perspective 3 / forward-future 3
  Total: 39/48

BRISTOL HIDDEN REQS (§5):
  Conflict management:     PASS
  Leadership 4/5:          PASS
  Media diversity ≥2:      PASS (6 media)
  Peer feedback:           PASS (3 episodes)
  Evaluate (4 elements):   PASS (multiple)

QUESTION COVERAGE: 10/10

LEVEL-4 MOVES: 16 across 6 body pages (target ≥12)  PASS

PENALTIES:
  Page overrun (final):    CAP 48 if uncut (or 0 if cut)
  Missing Q:               0
  No feedback-to-others:   0
  No conflict:             0
  Media diversity:         0
  Vague/generic:           0
  Schön not named:         −0.5 (missed theoretical-literacy +1)
  p7 density:              −0.5
```

---

## 12. TOP 10 FIXES RANKED BY MARK LIFT

| # | Fix | Lift | Cost | Risk |
|---|-----|------|------|------|
| **1** | **Cut 6 body pages → 5.** Merge 1a ¶1 and 1b ¶1 opening (they restate the CV-lead framing twice); compress the "three other contributions" paragraph in 3a to two sentences; trim 4a paragraphs on Demetro/pilot/Sid to one sentence each (leave Edward and Robin full-length); shrink the Kolb paragraph by ~80 words without losing a stage. Target: 5 full pages, density 90%. | **+28 (from 48 cap to 76)** | 1 afternoon | Mechanical — content survives |
| **2** | **Land M17.c cleanly.** Add a single before/after jargon removal sentence in the pilot paragraph or the complaint letter paragraph. Example: "When I showed the pilot the word 'geofence repulsor' he asked what it meant; I replaced it with 'fence that pushes you back'. Same paragraph of instructions cut 90 seconds from his read time." | +1 to +2 | 10 min | Low |
| **3** | **Land M17.d enumeration.** Add one sentence listing the methods as a set and giving per-method outcome: "Across the project I used six comms methods with audiences (doc→Robin, flag→Robin, slides+script→Demetro/FDR panel, dashboard→pilot, letter→organiser, Teams pivot→team); the two that moved behaviour fastest per author hour were the 400-word pivot message and the `--robin` flag, not the 3000-word doc." | +1 to +2 | 10 min | Low |
| **4** | **Add one Schön parenthetical.** Drop "(reflection-in-action, Schön)" on the BGR 6-permutation debug story or the wk17 24 h-reflection story. §6 Layer 4 says this is worth ~+1. | +0.5 to +1 | 2 min | None |
| **5** | **Add one implemented-in-project outcome on the team-side.** Currently most "programme" claims are forward-looking. Add one past-tense sentence where Robin or Demetro's behaviour changed *as a direct result of a specific feedback action inside the project timeline, with a measurable before/after.* The Robin CENTERING story already approaches this but the "shape of bug" outcome is naturalistic — make it numerical ("before wk19: 0 timeout guards in his modules; after wk20: 3"). | +1 to +2 | 15 min | Low — needs real data or principled estimate |
| **6** | **Explicit Hatton & Smith citation once.** "The Hatton-level move I now see" already appears in 2b — make it "(Hatton & Smith, 1995)" once and add to references. | +0.5 | 5 min | None |
| **7** | **Rubric-map table: add AHEP4 column.** Marker-friendly: let them tick M16.d / M17.d against paragraphs. Right now it maps only Q → section → rubric axis. Adding AHEP coverage column in the same table is free marks from assessor-friendliness. | +0.5 to +1 | 10 min | None |
| **8** | **Tighten one Level-3 feedback paragraph (Robin CENTERING) to Level 4.** The final generalisation sentence ("specificity is the scarce resource") is the only Level-4 move in that paragraph. Insert one earlier reframe: "I had previously thought peer feedback was a softness-calibration problem — I now see it is a specificity problem, and the reason I had it backwards is that I am socialised to read bluntness as rudeness." | +0.5 | 5 min | None |
| **9** | **Contrast paragraph for self-honesty.** One sober sentence acknowledging something the report does *not* know — e.g. "I cannot yet tell whether the 60/40 cap will survive contact with a project where the team genuinely needs a solo heroics phase; my test for this commitment is not yet falsified because it is not yet tested." Adds intellectual honesty (§9 Closer #2). | +0.5 | 5 min | None |
| **10** | **p7 density fix.** The final page is ~40% filled. Either pull content up (merge final 4b paragraph with closing) or add one paragraph on AHEP4 identity-shift closing. Currently the closing is strong but visually thin. | +0.5 (presentation) | 15 min | None |

**Aggregate lift if all 10 applied cleanly: 76 → ~80** (bumping into 80–100 band territory via M17.c/d completion, theoretical-literacy tags, and page discipline). Budget estimate: 2 hours. The page cut (#1) is the only non-negotiable.

---

## 13. REVIEWER'S CLOSING NOTE

V2 is a genuine Distinction draft. It has the three things V1 reviewers typically flag as missing from D7 attempts at this level: (a) named conflict with a structural (not rhetorical) resolution; (b) three peer-feedback episodes that pass the §9 Move #3 template; (c) criterion + judgement + cause + lesson evaluation on both self and team. The voice is honest to the point of self-indictment — the "async handoff docs were emotional scaffolding for me" sentence is the kind of disclosure that cannot be faked and that markers reward. Hatton Level 4 moves are abundant and load-bearing.

The single thing standing between V2 and a 76 is the page gate. If the candidate cuts 6→5 without losing the wk17 conflict, the Kolb cycle, or the three feedback episodes, the mark is 76. If he panics and cuts those, the mark could drop as low as 68 — the load-bearing content must survive the cut. The fix list above is ordered accordingly: the page cut is #1 because it is the only fix that changes the mark by more than 2.

A harsher reviewer than me would deduct another ~2 marks on the grounds that the report occasionally slips into self-diagnosis as a form of performance (the "preferred the first framing because it protected me from noticing the second" template appears 3 times, and by the third instance it reads as a rhetorical tic). I have not applied that deduction because the underlying diagnoses are distinct and the repetition is outweighed by the evidence density. A kinder reviewer would give +1 on Teamwork because the wk17 resolution mechanism — an HTTP-interface concession rather than a persuasion victory — is a more mature form of conflict management than the rubric explicitly requires and shows unusual reflective-practitioner sophistication. I have not applied that credit either.

**Final position: 76 / 100 conditional on the 5-page cut, 48 / 100 otherwise.**
