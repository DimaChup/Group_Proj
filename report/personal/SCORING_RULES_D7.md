# Scoring Rules -- D7 Individual Reflective Report

---

## What We Want From This Report

**Purpose:** Individual reflective report demonstrating personal growth, teamwork, self-management, and insight. This is NOT a technical report -- it is about YOUR experience, decisions, learning, and development. The marker already knows what SAR drones are. Focus on the human story.

**Audience:** MSc markers assessing personal/professional development. They are looking for genuine reflection, not project description. They will check for AHEP4 learning outcomes (M5, M7, M16, M17) and the three rubric criteria (Teamwork, Self-management, Insight).

**Page limit:** 5 pages body (excluding cover and appendices). This is tight -- every sentence must earn its place.

**AHEP4 Standards (must explicitly address all four):**
- **M5:** Design solutions with originality. Consider health/safety, diversity, inclusion, cultural, societal, environmental, commercial, codes of practice, industry standards.
- **M7:** Evaluate environmental and societal impact across entire lifecycle. Minimise adverse impacts.
- **M16:** Function as individual and team member/leader. Evaluate own and team performance.
- **M17:** Communicate effectively with technical and non-technical audiences. Evaluate communication methods.

**Key content that MUST be present:**
1. Specific leadership and teamwork examples with outcomes (not "we worked well together")
2. Honest weaknesses (not humble brags)
3. At least one design failure and what you learned from it
4. Environmental/societal impact with lifecycle thinking (manufacture -> deploy -> maintain -> dispose)
5. Data privacy and ethical considerations (photographing people from altitude)
6. Self-development programme with measurable success metrics
7. Feedback you gave to others to aid their development
8. Reflective frameworks applied properly (not just cited)
9. Communication methods evaluated for effectiveness (not just listed)

**What makes it score 90+:**
- Deep, genuine reflection (not surface-level "I learned a lot")
- Specific conflict examples with resolution process and outcome
- Properly walked-through reflective cycle (Kolb/Gibbs/Schon -- all 4 stages, not just mention)
- Feedback to others (the 83+ Insight differentiator)
- Quantified claims (25-30 hrs/week, 15,000 lines, 71 test scripts)
- Personal voice that feels authentic (Ukrainian context, career goals, real struggles)

---

## Scoring Rubric (from AENGM0074 Appendix B)

**Note:** Unlike D6, the D7 rubric does NOT show explicit percentage weights. Assume roughly equal (33/33/33).

### Teamwork

| Band | Marks | What It Means in Practice |
|------|-------|---------------------------|
| 2:1 (62-68) | "works effectively, recognises others, manages conflict" | You worked in a team and dealt with disagreements. |
| First (72-78) | + "leadership skills, ensures teams meet goals" | You DROVE the team forward. You did not just participate -- you set direction, created structure, ensured deadlines were met. |
| High First (83-100) | + "outstanding, creativity and flexibility, responsive to members' interests" | You adapted your leadership style to different team members. You balanced individual interests with team goals. You resolved conflict creatively, not just by authority. |

**The 83+ differentiator:** "Responsive to group members' interests" means you considered what each person needed (skill development, contribution credit, role preference) not just what the project needed. Give specific examples.

### Self-Management

| Band | Marks | What It Means in Practice |
|------|-------|---------------------------|
| 2:1 (62-68) | "good self-organisational skills, professional attitude" | You managed your time, met deadlines. |
| First (72-78) | + "very good, works autonomously" | You identified and solved problems without being told. You set your own direction. |
| High First (83-100) | + "outstanding, completing ALL tasks" | You managed multiple concurrent workstreams (CV, state machine, GCS, docs, testing, hardware). You maintained quality across everything. Nothing was left half-done. |

**The 83+ differentiator:** "ALL tasks" (not just "tasks"). Show that nothing fell through the cracks. The documentation habit, the blueprint system, the CLAUDE.md ground truth -- these are evidence of outstanding self-organisation.

### Insight

| Band | Marks | What It Means in Practice |
|------|-------|---------------------------|
| 2:1 (62-68) | "confident self-reflection, proactive self-development" | You can name your strengths and weaknesses. |
| First (72-78) | + "implement effective self-development programme" | You created a concrete plan with success metrics, not just "I want to improve." |
| High First (83-100) | + "setting own goals, feedback to others to aid THEIR development" | You helped other people grow. You set direction for yourself, not just followed course requirements. |

**The 83+ differentiator is helping OTHER people develop.** This is the single most important thing for top marks on Insight. Examples: creating documentation so teammates could run tests independently, structured GitHub workflow for the team, mentoring Edward on CV sub-team, creating FIELD_QUICK_REF.md so non-coders could participate.

---

## Priority Checklist (ordered by impact on score)

### Critical (biggest mark gains):
- [ ] **Give M17 (Communication) its own subsection.** Currently folded into Teamwork. The marking scheme explicitly lists M17 -- give it a heading. Material exists: simulator as communication tool, web GCS for non-technical users, demos beat slides, documentation strategy. Impact: +3-4 marks.
- [ ] **Add a design failure story.** Camera BGR/RGB issue is perfect: assumed sensor matched API label, it didn't, cost days, learned to verify hardware assumptions with direct testing. Shows genuine reflection-in-action (Schon). Impact: +2-3 marks.
- [ ] **Walk through one full Kolb cycle properly.** All 4 stages in 3-4 sentences: concrete experience -> reflective observation -> abstract conceptualisation -> active experimentation. The "I built everything alone" story is the best candidate. Impact: +2 marks.
- [ ] **Deepen M7 (Environmental/Societal).** Add data privacy paragraph (GDPR for aerial photography), lifecycle thinking (battery production -> disposal), quantify environmental claims. Currently reads like a compliance checklist. Impact: +2-3 marks.

### High priority:
- [ ] **Add a second conflict/compromise example.** ROS vs MAVLink is good. Need another: state machine complexity, flight test methodology disagreement, workload distribution tension. Impact: +1-2 marks.
- [ ] **Replace time management subsection with real scheduling failure.** Weather-cancelled flight day + pivot to bench testing is genuine reflection material. "Weekly milestones" is filler. Impact: +1-2 marks.
- [ ] **Pick one skill and tell its deep story** instead of listing four. Field debugging on Pi over PuTTY with no internet, discovering camera colour issue by testing all 6 permutations. Impact: +1 mark.
- [ ] **Add success metric to development action 3** ("one sentence, one diagram, one demo" -- actions 1 and 2 have metrics, action 3 does not). Impact: +0.5 marks.

### Polish:
- [ ] **Verify "15,000 lines" claim** or qualify ("including test scripts and tooling").
- [ ] **Verify "50 physical flights" claim** or say "an estimated."
- [ ] **Reframe PM contribution** -- "essential logistics work" rather than "things I would have neglected."
- [ ] **Consider adding one small table** -- AHEP4 LO signpost table mapping M5/M7/M16/M17 to sections, or a timeline of key decision points.

---

## Current Score and Gaps

**Current score: ~81-82/100** (borderline First / High First)
- Teamwork: ~82
- Self-management: ~83
- Insight: ~81

**Scoring trajectory:**
| Version | Teamwork | Self-mgmt | Insight | Total |
|---------|----------|-----------|---------|-------|
| v1 | ~68 | ~70 | ~65 | ~68 |
| v2 | ~78 | ~80 | ~78 | ~79 |
| v3 (baseline) | ~76 | ~78 | ~76 | ~77 |
| v4 | ~82 | ~83 | ~81 | ~82 |

**What improved from v3 to v4:**
- State machine compromise story added
- 3 feedback examples added
- Effort quantified (25-30 hrs/week)
- M5 STEEPLE integrated into narrative
- Diversity/inclusion added
- M7 quantified environmental impact (125kg CO2)
- Personal dual-use stance (Ukrainian context)

**Gaps preventing 85+:**
1. M17 needs its own subsection (currently hidden in Teamwork)
2. No design failure story (everything reads as "I designed it, it worked")
3. Reflective frameworks cited but not properly walked through
4. M7 is thin -- compliance checklist rather than genuine ethical reasoning
5. No data privacy discussion (GDPR implications of aerial photography)
6. Time management section is filler (process description, not reflection)
7. Skills list without depth (list of 4 instead of deep story of 1)

**Gaps preventing 90+:**
- All of the 85+ gaps above PLUS:
- Need more "feedback to others" examples for Insight criterion
- Need deeper self-interrogation (what REALLY went wrong, not just "I could improve")
- Need evidence of communication method effectiveness (GCS usage stats, documentation feedback)

---

## Figures That Would Be Impressive

This is a reflective report, so figures are optional but can help:

### Helpful (if space permits in 5 pages):
- [ ] **AHEP4 signpost table** -- small table mapping M5/M7/M16/M17 to section numbers. Helps marker navigate. Takes 3 lines.
- [ ] **Timeline of key decision points** -- visual showing when major pivots happened (BGR discovery, weather cancellation, Python 3.13 fix). Shows temporal self-management.
- [ ] **Contribution breakdown** -- small pie chart or bar chart showing your vs team contribution by area (software, hardware, docs, testing). Honest visual that supports the "I built it alone" narrative without being arrogant.

### Not recommended:
- Technical diagrams (this is not a technical report)
- Code snippets (save for D6)
- System architecture (already in D6)

### Key principle:
In 5 pages, every figure costs ~0.3 pages. Only include a figure if it replaces more text than it consumes. The AHEP4 signpost table is the highest ROI because it takes 3 lines and helps the marker give you credit for coverage.
