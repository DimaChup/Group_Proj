# D7 Connection Graph — Pointer Network

This file is a lightweight graph connecting Professional Practice content → D7 sections → report versions.
Read this INSTEAD of re-reading all 8 PP extractions every time.

---

## LEGEND
- **→** = "feeds into"
- **⇒** = "must cite" (MUST priority)
- **⇢** = "should cite if space" (SHOULD)
- **⇝** = "could cite" (COULD)
- `[file:section]` = pointer to specific content

---

## §1 MY ROLE (Q1a, Q1b, Q1c)

```
PP Sources:
  Tuckman ⇒ "team's work IS your work" / manager time split
    [team_development/TUCKMAN_COMPLETE.md → §3 Time allocation]
  Risk Assessment ⇢ "your professional approach starts now" / three pillars
    [risk_management/RISK_MANAGEMENT_COMPLETE.md → Part A §6]
  WBS ⇢ decomposition discipline
    [project_management/2_PM1_COMPLETE.md → WBS section]
  Waterfall/Agile ⇢ hybrid approach justification
    [project_management/2_PM1_COMPLETE.md → Waterfall vs Agile]
  Rolling Wave ⇝ near-term detail / far-term abstract
    [project_management/3_PM2_COMPLETE.md → §Rolling Wave]

Anecdotes:
  → role drift wk12→wk22 (commit 7eb7cc8 at 02:14)
  → simulator pivot as "the team's work IS your work" reframe
  → Ukrainian "one person delivers" culture clash

Report versions:
  Goldmine: [goldmine/slots/01_my_role.tex] ~2200 words — full depth
  Strict A: [strict_A/slots/01_my_role.tex] — narrative-first, 02:14 anchor
  Strict B: [strict_B/slots/01_my_role.tex] — "thing I'm not comfortable admitting" opener
```

---

## §2 MY TEAM (Q2a, Q2b, Q2c)

```
PP Sources:
  Lencioni ⇒ Five Dysfunctions pyramid (THE primary framework for §2)
    [five_dysfunctions/FIVE_DYSFUNCTIONS_COMPLETE.md → §2 Model + §6 D7 Application]
    Key quotes: "ring-fencing work" = absence of trust
                "if the problem was simple, you wouldn't need a team"
                "artificial harmony" = fear of conflict
    38 diagnostic questions: [→ §5 Diagnostic Tool]
  Tuckman ⇒ F/S/N/P stages mapped to project timeline
    [team_development/TUCKMAN_COMPLETE.md → §4-9 Stages + §12 D7 Application]
    Timeline: Forming wk12 → Storming wk17-20 → fragile Norming wk21 → regression
    Warning: "violently agreeing = no diversity of thought"
  Bennett DMIS ⇢ cultural sensitivity continuum
    [working_across_cultures/CULTURAL_COMPETENCE_COMPLETE.md → §7 Bennett]
    Apollo: Minimisation → Acceptance trajectory
  Shore Inclusion ⇢ 2×2 (belongingness × uniqueness)
    [working_across_cultures/CULTURAL_COMPETENCE_COMPLETE.md → §4 Shore]
    Team operated in Assimilation? → reflecting on moving to Inclusion
  Risk Compensation ⇢ safety illusion from simulation confidence
    [risk_management/RISK_MANAGEMENT_COMPLETE.md → Part B §6]
  Hofstede ⇝ UA high PDI/UAI vs UK flat structure
    [working_across_cultures/CULTURAL_COMPETENCE_COMPLETE.md → §5.1]

Anecdotes:
  → wk12 kickoff (Forming — was structure discussed?)
  → wk17 FSM pushback (Storming — Robin + Demetro, Lencioni Level 2)
  → wk20 PM workload / complaint letter (second conflict, different mechanism)
  → Robin cv_mode integration (Norming — handoff docs worked)
  → Flight day cancellations → regression

Report versions:
  Goldmine: [goldmine/slots/02_my_team.tex] ~2400 words — Lencioni + Tuckman + 3 conflicts
  Strict A: [strict_A/slots/02_my_team.tex] — 2 conflicts in prose
  Strict B: [strict_B/slots/02_my_team.tex] — Tuckman mapping table + 2 conflicts
```

---

## §3 MY IMPACT (Q3a, Q3b)

```
PP Sources:
  Kolb ⇒ full 4-stage deep-dive (on simulator pivot OR main.py refactor)
    [team_development/TUCKMAN_COMPLETE.md → §13 Connections/Kolb]
    4 stages: Experience → Reflect → Conceptualise → Experiment (italicised)
  Risk Assessment ⇒ progressive test ladder as risk mitigation
    [risk_management/RISK_MANAGEMENT_COMPLETE.md → Part B §7-12]
    ALARP applied to project decisions (TFLite vs NCNN, altitude, model)
  MCDA ⇢ structured technology down-selection
    [innovation_tools/INNOVATION_TOOLS_COMPLETE.md → §8 Tool 4: MCDA]
    Could frame CV backend choice as MCDA (even if not formally used — reflect on what it would have changed)
  Critical Path ⇢ hardware = critical path, software had float
    [project_management/2_PM1_COMPLETE.md → Critical Path section]
    Flight cancellations hurt because hardware was on the critical path
  Schön ⇢ reflection-in-action label (one use, parenthetical)
    "IMX296 BGR debug at 02:14 was (Schön, 1983) reflection-in-action"

Anecdotes:
  → Simulation framework (Kolb deep-dive candidate #1)
  → main.py refactor 1411→754 + Robin pushing 7 lines (Kolb candidate #2)
  → Progressive test ladder (tests/flight/0a→4)
  → 127 unit tests (voluntarily)
  → R01-R12: 12/12 sim vs 4/12 real

Report versions:
  Goldmine: [goldmine/slots/03_my_impact.tex] ~2800 words — both Kolb stories + MCDA + risk
  Strict A: [strict_A/slots/03_my_impact.tex] — Kolb on simulator
  Strict B: [strict_B/slots/03_my_impact.tex] — Kolb on refactor, dev actions table
```

---

## §4 MY SUPPORT (Q4a, Q4b)

```
PP Sources:
  Lencioni ⇒ accountability + trust (what teammates did for you = trust-building)
    [five_dysfunctions/FIVE_DYSFUNCTIONS_COMPLETE.md → §2 Level 1 Trust + Level 4 Accountability]
  Tuckman ⇢ performing stage = fluid roles, differences become useful
    [team_development/TUCKMAN_COMPLETE.md → §8 Performing]
  Three Pillars ⇢ moral obligation framing for why you helped
    [risk_management/RISK_MANAGEMENT_COMPLETE.md → Part A §6]
  Innovation Tools ⇢ "tools support thinking, not replace it"
    [innovation_tools/INNOVATION_TOOLS_COMPLETE.md → §10 Risks]
    Quote: "The team's decision is final, the tools are there to support, not replace, your thinking"
  Bennett ⇢ adapting communication to teammate's cultural context
    [working_across_cultures/CULTURAL_COMPETENCE_COMPLETE.md → §8]
  Shore ⇢ treating teammates differently ≠ unfairly (Shore's insight)
    [working_across_cultures/CULTURAL_COMPETENCE_COMPLETE.md → §4]
    Quote: "treating everyone the same is clearly unfair"

Anecdotes:
  → Edward: mavproxy bridge, pyserial 3.13, "test passes doesn't mean hardware does"
  → Robin: CENTERING timeout feedback, cv_mode integration, handoff docs
  → Demetro: FDR speaking scripts (4-5 drafts, register shift)
  → Pilot: 4-button layout, jargon removal, unaided field day operation
  → PM: admin/scheduling help
  → Complaint letter: group-first action, 6 tone iterations

THE 85+ GATE (from QUESTIONNAIRE_FOR_APOLLO.md §E):
  → Did a teammate say they reflected differently about THEMSELVES?
  → This is the Insight 83+ gate — no agent can fabricate this
  → Apollo must answer questionnaire §E Q49

Report versions:
  Goldmine: [goldmine/slots/04_my_support.tex] ~3200 words — all feedback + closing
  Strict A: [strict_A/slots/04_my_support.tex] — 3 feedback episodes in prose
  Strict B: [strict_B/slots/04_my_support.tex] — feedback table + identity-shift closing
```

---

## FRAMEWORK USAGE BUDGET (for 5-page strict versions)

Can't cite everything in 5 pages. Budget:

| Priority | Framework | Pages consumed | Where |
|----------|-----------|---------------|-------|
| ⇒ MUST | Lencioni (1-2 dysfunctions) | ~0.3pp | §2 |
| ⇒ MUST | Tuckman (stage mapping) | ~0.3pp (or table) | §2 |
| ⇒ MUST | Risk/ALARP (1 decision) | ~0.2pp | §3 |
| ⇢ SHOULD | Kolb (1 deep-dive, italicised) | ~0.3pp | §3 |
| ⇢ SHOULD | Bennett DMIS (1 sentence) | ~0.1pp | §2 or §4 |
| ⇢ SHOULD | Shore (1 sentence) | ~0.1pp | §4 |
| ⇢ SHOULD | MCDA (1 sentence) | ~0.1pp | §3 |
| ⇝ COULD | Schön (parenthetical label) | ~0 (inline) | §3 |
| ⇝ COULD | Hatton & Smith (parenthetical) | ~0 (inline) | anywhere |
| **Total** | | **~1.4pp** | |

Leaves ~3.6pp for Apollo's actual reflection. That's the right ratio — frameworks are seasoning, not the meal.

---

## CROSS-VERSION POINTERS

When an agent works on Strict A or B, it should:
1. Read THIS graph (not all 8 PP files)
2. Read the relevant goldmine slot for full content
3. Compress to 5pp using the framework budget above
4. Check the 85+ gate items from §4

When an agent scores, it should:
1. Check MUST frameworks are cited (Lencioni + Tuckman + Risk)
2. Check at least 2 SHOULD frameworks appear
3. Check no COULD frameworks are cited without a MUST being present (priorities wrong)
4. Check framework budget is ≤1.5pp (rest is personal reflection)

---

## FILE POINTERS (for quick agent access)

| What | File |
|------|------|
| Rubric (all 19 sections) | `D7_SCORING.md` |
| Brief verbatim | `D7_BRIEF_ONLY.md` |
| This graph | `D7_CONNECTION_GRAPH.md` |
| PP → D7 full mapping | `PP_TO_D7_MAPPING.md` |
| Framework quotes (30+) | `PP_TO_D7_MAPPING.md` Table 2 |
| BibTeX entries (18) | `PP_TO_D7_MAPPING.md` §5 |
| Apollo's questionnaire | `QUESTIONNAIRE_FOR_APOLLO.md` |
| Workflow phases | `D7_WORKFLOW.md` |
| Goldmine (full content) | `goldmine/main.pdf` (18pp) |
| Strict A (prose) | `strict_A/main.pdf` (5pp) |
| Strict B (tables) | `strict_B/main.pdf` (5pp) |
| Raw material bank | `../report/personal_v2/reviews/D7_RAW_MATERIAL.md` |
| Gap analysis | `../report/personal_v2/reviews/D7_V2_DISTINCTION_GAP.md` |
