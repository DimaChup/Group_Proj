# D7 V1 SCORE — Scorer B (Independent)

**Inputs reviewed:** `personal_v2/main.pdf` (5 rendered pages), `D7_SCORING_HARSH.md`, `D7_EXEMPLARS.md`.
**Not read:** Scorer A's output.

---

## D7 HARSH SCORE: 74/100

## HARD GATES

| Gate | Result |
|---|---|
| Page limit (working ≤7 / final ≤5) | PASS — body reads as 5 pages, final-compliant |
| 4 required headings (My role / My team / My impact / My support) | PASS — all four present as `\section`s |
| 10 sub-questions answered | PASS — rubric mapping table on p1 explicitly tags §s and commits for each of 1a–4b |
| First-person authenticity | PASS — "I", "my", named incidents, idiosyncratic voice ("I built a castle") |
| Specific evidence (named people / dates / incidents) | PASS — Edward, Robin, Demetro, pilot, PM, wk14, wk16, wk18, wk20, wk22, multiple commit hashes |
| Honesty (self-critical) | PASS — "I built a castle while the town starved", "offloading" admission, "non-technical help mattered as much as the technical" |
| AI boilerplate tone | PASS — voice is distinctive, occasionally punchy; not generic |
| Readability (font / cramping) | PASS — pages render cleanly, tables legible, mapping table readable at 150dpi |
| Presentation quality | PASS-ish — layout is consistent, though the `4a` table on p4 consumes ~70% of a page and the top of p4 has an awkward small paragraph tail before the table |

**No gates tripped.** Evidence floor (≥5 named specifics) easily cleared — I count 5 teammates named and >10 dated incidents/commits.

---

## CRITERIA SCORES

### Teamwork: 72/100
**Reasoning.** The report clears the 62–68 band (effective, recognises others, manages conflict) and reaches into 72–78 territory in several places. Evidence:
- **Conflict managed (explicit):** wk20 disagreement with Demetro about the 11-state FSM — writer explains pushback *and* the resolution ("I rewrote it to an 8-state FSM they could navigate"). This is the single strongest Teamwork beat and is what lifts the score above 68.
- **Leadership without title:** proposing to take CV/autonomy at kickoff (wk12), then rebuilding Demetro's FDR scripts "4–5 times", writing handoff docs for Robin (wk21). Named, dated, with outcomes.
- **Responsiveness to members' interests:** Robin's CV integration handoff, Edward's FOV calibration work cited specifically, Demetro's narrative needs.
- **Recognises others' value:** 4a table is exactly the kind of "what they did for me" evidence the 72+ band asks for, with named teammates and changed-my-work outcomes.

**Why not higher (80+).** The "outstanding creativity and flexibility responsive to group members' interests" bar needs more than one conflict and more than one adaptation. Only the 11-state FSM story is dissected in depth; Edward/Robin/pilot moments are acknowledged but not examined at Level 4 (Hatton & Smith). The "complaint letter for group benefit" angle hinted at in the brief's exemplar is absent. Team restructuring creativity is not shown.

### Self-management: 76/100
**Reasoning.** This is the report's strongest criterion. Clearly clears 72–78 (autonomous, very good organisation, professional).
- **Autonomous infrastructure:** named tools and artefacts the writer built for themselves — `brain-dump.md`, `MEMORY.md`, `NICE_TO_HAVE.md`, `CLAUDE.md`, blueprints, session-workflow rules. These are exactly the 83–100 evidence types the rubric appendix lists.
- **Delivery under setback:** 3 failed flight days, 820+ commits, modularity audit 3.8/5.0, capability audit 2.1/10, 127 unit tests written unprompted. Concrete, measurable, professional-attitude signals.
- **Goal-setting without assignment:** rewriting FSM, retraining the CV model (sar_v2_1088, mAP50=0.995), D6 iteration 74→85.2 across 6 cycles.

**Why not 80+.** The top band wants "outstanding" not just "autonomous" — and there's a self-critical admission on p1/p2 that the writer over-invested in the simulator ("castle while the town starved") which the assessor will read as a partial self-indictment of the organisation itself. That's honest and good for Insight, but it caps Self-management below "outstanding". Also no explicit personal planning cadence (weekly review, self-imposed deadlines that beat team deadlines) is narrated.

### Insight: 74/100
**Reasoning.** Clears 72–78 (autonomous + identifies weaknesses + programme of self-development + feedback to others) — just.
- **Self-critical named gap:** "I built a castle while the town starved" — the writer names the pattern (building solo infrastructure instead of pairing/teaching), which is the structural-not-dispositional self-criticism the exemplars reward.
- **Programme of self-development (past tense, with outcome):** modularity audit → refactor → 127 tests chain; capability audit → honest commit; goldmine iteration 74→85.2. These are exactly the evidence chains the rubric asks for.
- **Feedback to others:** Demetro's FDR scripts ("rewrote 4–5 times") and Robin's handoff docs are present. This clears the 72+ "provide effective feedback to others" bar — though barely.
- **Changed worldview:** The "non-technical help mattered as much as the technical" line on p4 is a genuine reframing moment (Level 4 reflection per Hatton & Smith).

**Why not 80+.** The feedback-to-others examples are stated, not dissected. The rubric asks what *changed in the teammate's behaviour* after your feedback — the report says Demetro's narrative improved, but doesn't show Demetro *doing something differently next time*. That's the Level 4 move. Also the "what I'd do differently" answers on p2/p3 are crisp but short; the `1c`, `2c`, `3b` forward-looking bullets don't all have the "because I now see X was driven by Y" depth that pushes into 80+.

### Average: (72 + 76 + 74) / 3 = **74.0**

---

## QUESTION COVERAGE: 10/10

Cross-check against the rubric mapping table on p1:

| Q | Present | Quality |
|---|---|---|
| 1a roles explicit/implicit | Yes — p1 "1a. What I was given vs what I ended up doing" | Strong, names implicit scope creep |
| 1b most proud of | Yes — p1 "1b. What I am most proud of" | Specific (sim framework, CV retrain) |
| 1c future focus | Yes — p1/p2 "1c. What I would focus on differently" | Honest ("build less, teach more") |
| 2a team structure | Yes — p2 "2a. Structure, whether we discussed it, and how it changed" | Covers wk12 kickoff + change |
| 2b impactful team-working | Yes — p2 "2b. Most impactful team-working elements" | 3 named elements with commits |
| 2c change next time | Yes — p2 "2c. What I would change next time" | 2 specific counterfactuals |
| 3a drove team forward | Yes — p3 "3a. How my contributions drove the team forward" | Table with specific outcomes |
| 3b add/refocus | Yes — p3 "3b. What I would add or refocus on" | Present but the shortest answer |
| 4a others helping me | Yes — p4 big table, 5 teammates | Strong, by far the best-evidenced question |
| 4b me helping others | Yes — p4/p5 table extension + prose | Good, with "observed behaviour change" column |

**All 10 questions answered and explicitly tagged.** Question coverage is a strength.

---

## PENALTIES

| Penalty | Value | Reason |
|---|---|---|
| Page overrun | 0 | 5 pages |
| Missing questions | 0 | 10/10 |
| No feedback to others | 0 | Present (Demetro, Robin) |
| Vague/generic | −0 | Generally specific; a few soft moments in 3b |
| Layout orphans | 0 | None visible |
| **Total penalties** | **0** | |

---

## FINAL SCORE: 74/100

**Band:** high Merit / low Distinction. Consistent with a report that clears every hard gate, answers every question, and demonstrates the 72+ band on all three criteria but doesn't yet reach the 80+ "outstanding / creativity / responsive to individual interests" tier.

---

## TOP 5 FIXES (ranked by marks/effort)

1. **Deepen the feedback-to-others evidence (Insight → 78).** For Demetro and Robin, add one sentence each showing *what they did differently next time* after your feedback. That's the Hatton & Smith Level 4 move the rubric explicitly asks for ("feedback to others to aid their self-development"). Worth ~3 marks on Insight.

2. **Add a second managed-conflict beat (Teamwork → 76+).** The 11-state FSM story is strong but currently stands alone. One more named disagreement with resolution — e.g. the PM workload concern, the pilot walkthrough at wk21, or a supervisor complaint-letter moment — pushes Teamwork clearly into the 72–78 band and closer to 80. Worth ~4 marks on Teamwork.

3. **Tighten 3b — "what I would add or refocus on".** Currently the shortest answer and reads like it was cut for space. Add 2–3 lines of concrete forward-looking commitment grounded in a named gap (not just "build less, teach more"). Worth ~2 marks on Insight and ~1 on Teamwork.

4. **Show one instance of creative team restructuring initiated by you.** Top-band Teamwork (80+) requires "creativity and flexibility responsive to group members' interests". The Robin handoff is the candidate — dissect the decision to move CV integration to Robin at wk21 as a deliberate team-shape choice, not a logistics fact. Worth ~2 marks on Teamwork if done well.

5. **Page 4 layout polish.** The `4a` table consumes ~70% of p4 with a small paragraph tail at the top. Either lift one of the rows into a prose paragraph to rebalance, or let the table start immediately under the heading. Presentation caps aren't tripped, but this is the one page where a marker might notice imbalance. Worth ~1 mark under Presentation/Communication.

---

## CONFIDENCE

| Criterion | Confidence | What would change my mind |
|---|---|---|
| Teamwork 72 | **Medium-high** | If I missed a second dissected conflict on re-read, score lifts to 75–76. If the 11-state FSM beat is actually about Demetro rather than the writer's proposal, score drops to 68. |
| Self-management 76 | **High** | Named tools + 820 commits + audit metrics + unit tests is a very stable 72–78 signature. Only a page-limit violation on final cut would drop this. |
| Insight 74 | **Medium** | Hinges on whether the feedback-to-others examples actually show *behaviour change in the teammate*. If I re-read and see explicit "after this, Demetro started doing X", it's 77. If not (which is my current read), 74 stands. |
| Overall 74 | **Medium-high** | The three criterion averages are internally consistent and triangulate with question coverage (10/10) and hard-gate status (all clear). A third opinion is most likely to land in 72–76. |

**Biggest uncertainty:** I cannot read the prose at full fidelity from 150dpi screenshots — some nuance in the 2b/2c/3b answers may be stronger than I'm giving credit for, or weaker. If the text contains a second conflict I missed, overall nudges to 75–76. If the feedback-to-others claims turn out to be assertions without teammate-side outcomes, overall drops to 72.

**What would make me confident the score is wrong by 5+ marks:**
- **Up:** a second fully-dissected conflict + a Level 4 "I was wrong about X, here's what changed" moment I missed → 78–80.
- **Down:** discovering the named incidents are asserted but not examined (pure chronology in reflective clothing) → 68–70.
