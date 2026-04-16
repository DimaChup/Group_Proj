# D7 V2 — Distinction Gap Analysis (76–78 → 85+)

**Scope.** This is a ruthless diagnosis of what stands between the current V2 consensus score (Scorer A: 76, Scorer B: 78, space eval: B+) and a High-Distinction 85+. Page-cap fix and placeholder fill are assumed done — this document concerns only the *content ceiling*, not the mechanical gates. References to rubric clauses are from `D7_SCORING_FINAL.md`; exemplar citations are from `D7_EXEMPLARS.md`.

---

## 1. Current position and distance to target

| Dimension | Current | Target | Gap |
|---|---|---|---|
| Criterion avg | 74.3–78.0 | 85+ | 7–11 marks |
| AHEP4 sub-clause total | 38–39 / 48 | 43+ / 48 | 4–5 sub-marks |
| Hatton L4 moves | 15–16 / 6 pages | ≥15 held, but depth uneven | density fine, variance too high |
| Bristol band earned | 72–78 "very good / consistent" | 83–100 "outstanding / creative / responsive" | one band step |

The numerical lift required is **7–9 marks**. The rubric lift required is one band step, and the rubric's 80→83 threshold is *qualitatively* different from 75→80: the former is a refinement, the latter is a *change of kind* (see §7 below).

---

## 2. Teamwork analysis

**Current score: 74–77.** Carrying the score: wk17 FSM conflict paragraph (§2b ¶2) — full parties/mechanism/outcome template, the single strongest paragraph in the report. Plus leadership 4/5 on §4.5 checklist (decision authority wk14, delegation to Edward, meta-work, accountability via complaint letter). Plus the "right design vs right design *for this team*" reframe, which is Level 4 and load-bearing.

**80–85 gap.** The 80-band descriptor says "creativity and flexibility **responsive to group members' interests**." Currently the team-facing behaviour is rendered through the author's own diagnostic lens: Robin is an interface partner, Demetro is a feedback recipient, Edward is a delegation target. What's missing is *a paragraph where the author adapts to a teammate's interest or constraint in a way the teammate recognised and named back*. The wk17 compromise comes closest, but it's described as a structural concession ("I gave up the FSM") rather than a creative response to Robin's interest. To hit 80, insert one paragraph where a teammate's *goal or style* is named first, and the author's behaviour change is described as a creative response to it — not a concession under pressure.

**85–90 gap.** 83+ demands "**outstanding ability to LEAD a team** with **creativity and flexibility**." V2 explicitly disclaims leadership ("leadership-without-title moment, such as it was") — which is honest and rewarded at 75, but ceilinged at 80. To score 85+ the report needs *one* paragraph where the author acted in a recognisably leadership-shaped way *and owns it*: a moment the author changed the team's trajectory by influence (not by delegating a fix), and a teammate can be named as having followed that influence. The wk18 pivot to simulation-first is this moment in latent form — but the current prose frames it as "I chose for myself" rather than "I repositioned the team." Rewrite it as the latter and the mark moves.

**Single hardest thing to add.** A **second, differently-textured conflict episode.** One conflict resolved by structural concession (wk17) shows maturity; two conflicts — one resolved by concession, one resolved by the author *holding the line and being proven right or wrong* — shows the range the 83+ band language ("creativity AND flexibility") demands. This cannot be agent-authored; it requires Apollo to surface a second incident from memory or commit history.

---

## 3. Self-management analysis

**Current score: 75–80.** Carrying the score: 2508-line simulator, 1411→754 refactor with 146 pytests, progressive test ladder, blueprint system, NCNN timebox decision, modularity audit self-scored 3.0/5.0 on own code. The self-audit at 3.0 is the strongest single clause in the report and already sitting in 80-band territory. Scorer B puts Self-management at 80 for this reason.

**80–85 gap.** The 83+ descriptor says "**outstanding** self-organisational skills" with a "professional attitude." "Very good" (72–78) says the same words without "outstanding." The difference in practice is *observable impact on others' organisation*. Currently the self-management story is insular: the author organised *himself* heroically. To hit 83 the report needs one paragraph where the author's self-organisation *raised the organisational floor for the team* — e.g. the blueprint system being used by Robin or Demetro to navigate the codebase faster, with a measured time saving. The `--robin` flag and the 4h-docs-→-20h-Robin-unblocked story is the seed of this, but it's currently classified as comms, not self-management. Reclassify it and add one sentence making the organisational-leverage move explicit.

**85–90 gap.** 83+ needs a *second* domain of outstanding autonomy (Scorer B flags this explicitly). Currently the sim-first pivot is the only domain. A second candidate exists in the report (the modularity audit → refactor → pytest pipeline) but it is framed as a self-correction rather than as autonomous engineering judgement. Reframe it as "I decided without prompting that untested code at 1411 lines was a team liability, and I set myself a 2-day budget to halve it" — that is outstanding-autonomy register.

**Single hardest thing to add.** Evidence that the self-organisation **changed the organisational behaviour of a teammate in a way that survived past the project timeline**. "Robin adopted my blueprint pattern in his own modules from wk20 onwards" is the shape; Apollo has to confirm it is true.

---

## 4. Insight analysis

**Current score: 74–77.** Carrying the score: three peer-feedback episodes (Demetro / Robin / pilot), each passing the §9 Move #3 template; 60/40 solo/pair cap with 48h falsifiability signal; modularity self-audit. Hatton L4 density (15–16 moves) is already at Distinction-plus level.

**80–85 gap.** The rubric's 80-band ask is "implement an effective programme of self-development" (emphasis on *implement*, past tense, inside the timeline). Currently *most* of the implemented programme is forward-looking (60/40 cap, 500-line pairing rule — things that will be tested on future projects). The exception is the wk17→wk20 "afternoon instead of a week" outcome. To hit 80 the report needs *one more* in-timeline implementation — an instance where the author identified a weakness in week N, applied a mechanism, and by week N+2 a teammate or artefact measurably improved as a result. The Robin "shape of bug" propagation comes closest but is described naturalistically rather than as a measured outcome. Rewrite it with a number (e.g. "3 timeout guards appeared in Robin's modules between wk19 and wk22 where 0 had existed").

**85–90 gap.** The 83+ descriptor says "provide effective feedback to others **to aid their self-development**." The emphasis is on the teammate's *self-development*, not on task-level fixes. Currently all three feedback episodes describe task-level behaviour change (Demetro uses numbers not adjectives; Robin guards timeouts; pilot asks for the same UI on VERIFY). None describe a teammate *reflecting differently about themselves* as a result of the author's feedback. This is the rarest and highest-value move in the rubric. It is almost impossible to fake — it requires the teammate to have said something back like "I now see I was doing X." Apollo must supply this sentence or the ceiling holds.

**Single hardest thing to add.** A **feedback-gives-back-a-lesson** episode where the teammate's self-understanding shifted, not just their code. This is the 83+ gate and it cannot be agent-authored.

---

## 5. AHEP4 sub-clause coverage (1–5 each)

| Clause | Current | Target | Comment |
|---|---|---|---|
| **M16.c** function effectively as individual | **5** | 5 | Loaded: vision.py, 2508-line sim, 1411→754 refactor. No gap. |
| **M16.d-own** evaluate own effectiveness | **5** | 5 | Modularity audit 3.0/5.0 is the single strongest sub-clause in the report. No gap. |
| **M16.d-team** evaluate team effectiveness | **3** | 5 | R01–R12 matrix is *implied* ("thin delta on Pi") but never stated as a tight criterion+judgement+cause+lesson paragraph. Needs one sentence with the actual numbers: "12/12 in sim, 4/12 on hardware, 3 of the 8 gaps were bench work we failed to schedule." |
| **M17.a** communicate complex engineering | **5** | 5 | VISION_PIPELINE_FOR_COLLEAGUE.md, TFLite→undistortion→GPS chain, JSON schema. Locked. |
| **M17.b** technical audience | **4** | 5 | "Robin integrated without asking a clarifying question for two days" is strong but the paragraph has one reception anchor. Adding Edward's reception-side behaviour (did Edward use the SITL home fix advice immediately? did it hold across tests?) lifts to 5. |
| **M17.c** non-technical audience | **2** | 4 | **Weakest clause.** Pilot scrapes 2/5 threshold; complaint letter is named but adaptation is *not shown*. Needs an explicit before/after jargon-pair sentence (Scorer B's fix #2) and a named non-engineer reaction. |
| **M17.d** evaluate effectiveness of methods | **2** | 4 | **Second-weakest.** A/B comparison is present but informal — criterion, judgement, and per-method comparison are not enumerated. Needs one sentence listing methods as a set with per-method outcome per author-hour (Scorer B's fix #3). |
| Bristol add-on: implemented programme | **3** | 5 | Most implementation is forward-looking. Needs one in-timeline measured outcome on the team side. |

**Weakest two clauses: M17.c (2) and M17.d (2).** Lifting both to 4 is worth ~3 marks on the sub-clause adjustment (from 38/48 to ~43/48 → +1.0 raw, +2 banded).

### Unified paragraph to lift M17.c and M17.d simultaneously

Insert inside §2b or §4a:

> "Across the project I used six comms methods with named audiences: the VISION_PIPELINE handoff doc (Robin, 3000 words, unread until wk20), the `--robin` HTTP flag (Robin, 40 lines of JSON schema, integrated same afternoon), the FDR speaking scripts (Demetro → academic panel, four iterations), the web dashboard (pilot, four buttons mapped to RC thumb-reach), the complaint letter (course organiser — non-engineer administrator), and the Teams pivot message (team, 400 words). Against the criterion of behaviour change per author-hour the ranking was clear: the `--robin` flag and the Teams pivot moved behaviour fastest; the 3000-word doc moved nothing until Robin had already been blocked for a week; the FDR scripts sat between the two. The non-engineer case forced the cleanest edit: my first draft of the complaint letter used the phrase 'geofence repulsion vector,' which the organiser later told me she had skipped over; the signed version said 'an invisible fence that nudges the drone back inside a safe zone,' and she quoted that line back at me when she replied. The lesson I take from the ranking is that prose quality is the least scarce of the comms resources; the scarce resources are timing, pairing, and audience-register, in that order."

This single paragraph: (a) enumerates methods with named audiences (M17.c threshold clear 4/5); (b) gives per-method criterion × judgement (M17.d clean 4/5); (c) names a non-engineer reaction quoting the author's own line back (reception evidence for Bristol Comms 80+); (d) ranks communication resources (alt-perspective credit). Estimated lift: **+3 to +4 marks**. Cost: 170 words + one real sentence Apollo must supply ("she quoted that line back at me when she replied" — only real if it's real).

---

## 6. Hatton & Smith level count and upgrade candidates

**Current: 15–16 L4 moves across 6 body pages (2.5–2.7/page).** Target (≥15) already met. This is the strongest dimension of V2 and is not the bottleneck.

**Upgrade candidates — paragraphs stuck at L3:**

1. **§4b ¶2 (Robin CENTERING timeout).** Scorer A flags this as "Level 3–4 transitional." The L4 move is only in the final generalisation sentence. Insert one earlier reframe: *"I had previously treated peer feedback as a softness-calibration problem — I now see it is a specificity problem, and I preferred the softness framing because it let me postpone the harder work of reading someone else's code carefully enough to be specific about it."* This converts the paragraph from L3 → L4 and adds the Section 14 Move #2 template (reframing-plus-motive).

2. **§3a Kolb paragraph.** Currently L4 on the "sim as statement not backup" move, but the L3→L4 edge is the delta admission ("could not tell us what it could not tell us"). This is defensive-adjacent — one harsh reader could call it "defensive retract" (Merit failure mode #7). Sharpen by naming what specifically the sim *failed* to model (motion blur, descent stall, GPS lag) and giving one number on each. That converts a hedged L4 into an assertive L4.

3. **§1b ¶1 ("What I am actually proud of").** L4 on the "judgement is choosing when to stop trusting stated constraints" move, but the paragraph doesn't examine why the author needed permission from himself to do this. Add one sentence: *"That permission was not a professional judgement — it was an act of trust in my own discomfort with the official plan, and I had to overrule a version of myself that wanted institutional cover."* This is Move #8 (value-tension move), rare and highly rewarded.

**No paragraph is stuck at L2 (descriptive).** The ceiling is uneven L4 quality, not absence of L4.

---

## 7. Bristol "outstanding" 83+ band analysis

The rubric's 83+ band uses five weaponised words: **outstanding, lead, creativity, flexibility, responsive.** Count of appearances in V2: zero of them are earned with evidence at team level.

- **"Lead."** V2 explicitly disclaims it. This is honest and rewarded at 75. It is *capped* at 80.
- **"Creativity."** The `--robin` flag is creative, but framed as a concession. The simulation framework is creative, but framed as self-protection. Neither carries the word.
- **"Flexibility."** wk17 is the flexibility moment, but it's framed as "I backed down" rather than "I adapted to the team's register."
- **"Responsive to group members' interests."** This is the single most damning gap. The report is *diagnostic* about group members, not *responsive* to them. Robin is analysed; Demetro is analysed; the pilot is analysed. None of them are described as having an *interest* the author then served creatively.
- **"Outstanding."** The modularity self-audit is outstanding self-evaluation. Nothing else carries the word.

**What "very good" (72–78) vs "outstanding" (83+) actually means in Self-management.** Very good = consistent high-quality autonomous delivery. Outstanding = that delivery *visibly raised the operating standard for others*. The delta is not more effort; it is *demonstrable impact on others' organisation*, and the report does not currently carry evidence of this.

**The feedback-to-others 83+ clause is measurable.** Rubric wording: "provide effective feedback to others **to aid their self-development**." The author must show a teammate *reflecting differently about themselves*, not just doing their task differently. The Robin "shape of bug" episode almost qualifies — if Robin can be quoted as having said "I now see I default to optimistic timeouts" or similar, it lands. If not, it remains a task-level fix and holds at 77.

---

## 8. Top 10 mark-lifting changes ranked by delta

| # | Change | Lift | Difficulty | Needs Apollo HITL? |
|---|---|---|---|---|
| 1 | **Unified M17.c+M17.d methods-comparison paragraph** (see §5 above). Enumerates six methods with audiences, per-method criterion+judgement, non-engineer reception with quoted line. | **+3 to +4** | Medium | **YES** — the organiser-quotes-your-line detail must be true. Jargon-pair can be agent-drafted. |
| 2 | **Team evaluation paragraph with R01–R12 numbers.** "12/12 in sim, 4/12 on hardware, 3 of 8 gaps were bench work we failed to schedule — coordination failure not effort failure." Lifts M16.d-team 3→5. | **+1.5 to +2** | Easy | NO — numbers already known. |
| 3 | **In-timeline teammate outcome with number.** Rewrite Robin "shape of bug" as "between wk19 and wk22, 3 timeout guards appeared in Robin's modules where 0 had existed." Lifts Insight implemented-programme 3→5. | **+1 to +2** | Medium | **YES** — must verify the count. |
| 4 | **Second conflict episode.** Different party, different mechanism (conflict held rather than conceded). Unlocks Teamwork 77→82. | **+2 to +3** | Hard | **YES** — Apollo must surface a real incident. Cannot be fabricated. |
| 5 | **Feedback episode with teammate self-reflection outcome.** One of Demetro / Robin / pilot quoted as having reflected differently about themselves. Unlocks Insight 77→83+. | **+2 to +3** | Hard | **YES** — requires a real quote or paraphrase. The rarest ingredient. |
| 6 | **Reframe wk18 pivot as team-repositioning, not personal choice.** Current: "I chose to build a simulator." Target: "I repositioned the team onto a path where two of us could make verifiable progress without waiting for hardware access." Same event, different frame — unlocks "lead" language. | **+1 to +2** | Easy | NO — agent-authored rewrite. |
| 7 | **Upgrade §4b ¶2 (Robin CENTERING) from L3→L4.** Insert reframing-plus-motive move (see §6 upgrade candidate 1). | **+0.5 to +1** | Easy | NO. |
| 8 | **Reclassify blueprint/docs story as self-management not comms, and add organisational-leverage sentence.** "Robin and Demetro navigated vision.py via the blueprint file for N hours that would otherwise have been mine to absorb" — unlocks Self-management 80→83. | **+1 to +1.5** | Easy | **YES** — Apollo should confirm blueprint actually got used. |
| 9 | **Schön parenthetical + Hatton & Smith citation.** Two name-drops, earned by how the text already behaves. | **+0.5 to +1** | Trivial | NO. |
| 10 | **Sharpen Kolb paragraph delta admission with three specific numbers** (motion blur, descent stall, GPS lag). Converts hedged L4 to assertive L4. | **+0.5** | Easy | NO. |

**Aggregate lift if all 10 land cleanly: +13 to +20 marks on paper.** Realistically attenuated to ~+9 to +11 by the band-step penalty (harder to move 77→85 than 70→77 because the rubric steps get coarser). Practical ceiling: **85–86 if items 1, 4, and 5 all succeed with real Apollo input**; **82–83 if only items 1, 2, 6, 8 succeed (agent-authored only)**.

---

## 9. Plateau prediction

**Agent-only ceiling: ~82.** With only agent-authored rewrites — items 1 (partial, minus the organiser quote), 2, 6, 7, 8 (partial), 9, 10 — the score lifts to ~82. This captures: unified methods paragraph (minus the real reception quote), team-evaluation numbers, pivot reframe, L3→L4 upgrades, theoretical citations, sharpened Kolb. The ceiling is set by M17.c (still 3/5 without the real jargon-pair reaction) and by the absence of a second conflict episode.

**Apollo HITL ceiling: 85–87.** Required inputs from Apollo, ranked by value:

1. **One real non-engineer reception quote.** (Unlocks M17.c to 5/5, worth ~1.5.)
2. **One teammate quote that shows self-reflection as a result of author's feedback.** (Unlocks Insight 83+, worth ~2–3.)
3. **One second conflict episode with different mechanism.** (Unlocks Teamwork 83+, worth ~2–3.)
4. **Confirmation that the blueprint/doc system was used by named teammates with an estimated time saving.** (Unlocks Self-management 83+, worth ~1–1.5.)
5. **Timeout-guard count in Robin's modules before/after wk19.** (Unlocks in-timeline programme, worth ~1.)

**Hard ceiling even with full HITL: ~88.** Above 88 requires either a second "outstanding" domain of autonomy (a second independent strategic call on the scale of the sim-first pivot) or an explicit leadership-under-authority moment, both of which Apollo's own self-framing in V2 consistently disclaims. The honest "leadership-without-title" voice is a 77–83 voice by construction — pushing above 83 requires either a voice shift (risky, loses authenticity) or a new piece of evidence that contradicts the self-framing. The report is self-consistent at ~83; the gap between 83 and 88 is paid in evidence, not in rewrites.

**Where Apollo HITL input becomes essential:** above ~82. Between 76 and 82 is agent territory. Between 82 and 87 is HITL territory. Above 87 is either impossible without a new incident or requires abandoning the honest-self-diagnostic voice, which would be worse than leaving the score at 85.

---

## 10. Single-sentence summary

The V2 draft is a self-consistent 77 that can be mechanically lifted to 82 by an agent (methods paragraph, team-eval numbers, pivot reframe, L3→L4 upgrades) and to 85–87 by Apollo supplying five specific pieces of external evidence (non-engineer quote, teammate self-reflection quote, second conflict, blueprint adoption data, timeout-guard count) — above 87 requires a voice shift the draft should not make.
