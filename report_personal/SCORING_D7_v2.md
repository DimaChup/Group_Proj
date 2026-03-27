# D7 Individual Reflective Report -- Scoring v2

> Karpathy iteration 2. Scored against Appendix B rubric (Level 7).
> Previous scores (v1): Teamwork 68, Self-management 78, Insight 72.

---

## Rubric Criteria Scores

### 1. Teamwork (M16) -- Score: 78/100 (+10 from 68)

**What improved:**
- Section 04 now has genuine substance. The "Solo Coding Reality" subsection is brutally honest about why delegation failed -- this is exactly the kind of critical reflection that pushes into the 72+ band.
- Concrete conflict example: ROS 2 vs raw MAVLink disagreement with a clear resolution narrative (20-line demo that convinced the team). This is specific, technical, and shows leadership through evidence rather than authority.
- The "Managing Disagreements" section acknowledges workload frustration as the persistent tension and describes how it was managed (focusing on shared goals, explicitly valuing the PM's logistics work). This is mature.
- The pilot's feedback about abort/confirm button placement is an excellent concrete example of responsive adaptation to team input.
- Communication section is strong: four distinct channels, each evaluated for effectiveness, with the simulator identified as the most impactful.

**What's still weak:**
- The report describes flexibility mainly as "I adapted my schedule to their constraints" -- this is accommodation, not the creative flexibility the rubric demands. Where did you change YOUR approach because of team input?
- Conflict management is still thin. The ROS 2 disagreement was resolved by demonstration (you won), and workload frustration was "managed" by reframing. Neither shows genuine compromise or negotiation where you gave ground.
- "No major interpersonal conflicts" reads as defensive. A 75+ report would dig into the discomfort of uneven workload more honestly -- did anyone feel sidelined? Did you ever receive pushback on your technical decisions?
- The feedback subsection is one-directional: you gave technical feedback (wiring, risk assessment), but examples of receiving and acting on feedback are limited to one UI button layout change.

**To reach 83+:** Show a moment where team input changed your technical direction (not just button placement). Show genuine negotiation where you compromised on something you believed in. Deepen the "receiving feedback" angle -- what did teammates tell you about your communication style, pace, or approach?

---

### 2. Self-management -- Score: 82/100 (+4 from 78)

**What improved:**
- Time management section is now concrete: weeks 12-15 simulation, 16-18 Pi deployment, 19-20 field testing. This shows structured planning.
- The "living ground-truth document" as both progress log and goal-setting tool is a strong example of professional self-organisation.
- Contingency planning for weather cancellation (pre-planned bench tests) demonstrates professional attitude -- engineering the schedule itself.
- Balancing MSc coursework with project priorities shows autonomy in resource allocation.
- The "day one deployment" lesson learned from delayed hardware testing is a genuine professional insight.

**What's still weak:**
- The section could quantify effort more: how many hours per week? How did this compare to teammates? The rubric says "professional attitude to completing ALL tasks" -- what tasks did you deprioritise and why?
- No mention of version control discipline, which is actually a strong professional behaviour (feature branches, progressive commits). This is evidence left on the table.
- The weekly milestone structure sounds smooth -- where did it break down? A 83+ report would show a moment where self-management failed and how you recovered.

**To reach 83+:** Add a concrete example of a self-management failure and recovery (e.g., underestimating integration time, missing a self-imposed deadline). Show the correction mechanism, not just the plan.

---

### 3. Insight -- Score: 79/100 (+7 from 72)

**What improved:**
- Strengths and weaknesses are now specific and honest. "Designing for collaboration" as the primary weakness is a mature, non-trivial self-assessment that directly connects to project evidence.
- "Choose speed over inclusion" is an excellent framing -- it names the behaviour pattern precisely and connects it to leadership.
- "Delayed hardware testing" as a third weakness shows genuine technical self-awareness with a concrete consequence (Python 3.13 issues, camera colour bugs).
- The self-development programme has three concrete, measurable actions with specific strategies ("contributor guides," "day one deployment," "one sentence, one diagram, one demo" framework).
- Career connection to Ukraine gives the self-development narrative genuine stakes and purpose.
- The final thought ("quality is determined not by cleverness but by rigour of testing") is a strong, earned insight.

**What's still weak:**
- The development programme actions are forward-looking but lack reflection on how you've ALREADY started implementing them. Item 2 mentions "I have already begun applying this" -- good. Items 1 and 3 don't have this.
- Feedback to others is addressed in Section 04 (wiring review, risk assessment additions) but not cross-referenced here. The rubric explicitly says "provide effective feedback to others to aid THEIR self-development" -- your examples are about correcting work, not developing people.
- The strengths section doesn't critically examine whether "rapid prototyping" could also be a weakness (it is -- it's the same pattern as "speed over inclusion").
- Missing: how do you know these are your weaknesses? What evidence beyond this project? Any feedback from teammates that confirmed them?

**To reach 83+:** Add evidence of helping teammates develop (not just correcting their work). Show that your self-assessment is validated by external input, not just introspection. Connect strengths and weaknesses as two sides of the same trait.

---

## AHEP4 Standards Scores

### M5 (Design solutions with originality) -- Score: 80/100

**Strengths:** Four distinct original solutions described with technical depth. The dual-backend architecture is genuinely clever. Simulation-first methodology is well-articulated. STEEPLE coverage is comprehensive (all 7 factors addressed).

**Weakness:** STEEPLE reads slightly like a checklist -- each factor gets one sentence. The safety and environmental factors are well-integrated into the design narrative, but political/ethical feel like afterthoughts. "Health/safety, diversity, inclusion, cultural" from M5 -- diversity and inclusion are not addressed at all (team composition? accessibility of ground station interface?).

### M7 (Environmental and societal impact) -- Score: 77/100

**Strengths:** Three-level environmental analysis (mission, hardware lifecycle, development) is well-structured. Dual-use discussion is personal and honest. Quantified claim (simulation replaced ~50 physical flights) adds credibility. Battery disposal mention shows lifecycle thinking.

**Weakness:** The lifecycle analysis is still mostly qualitative. What are the actual energy numbers? How much CO2 for Colab GPU training? The "positive potential" paragraph is generic SAR benefits rather than project-specific evaluation. The rubric says "evaluate" and "minimise adverse impacts" -- the evaluation of your own system's adverse impacts could be sharper.

### M16 (Team effectiveness evaluation) -- Score: 76/100

**Strengths:** Clear role descriptions, honest assessment of what worked and what didn't, acknowledgment of uneven workload, plus/delta structure implicit throughout. The solo coding analysis is a genuinely critical evaluation of team effectiveness.

**Weakness:** Evaluation of team effectiveness is mostly about YOUR effectiveness within the team. What about the team's collective performance? Was the role allocation optimal? If you could redesign the team structure, what would you change? The rubric says "evaluate effectiveness of own AND team performance."

### M17 (Communication effectiveness evaluation) -- Score: 78/100

**Strengths:** Four communication channels with honest evaluation of each. The insight that the simulator was more effective than documentation for onboarding is a genuine finding. The ground station as a "communication tool" is a creative framing. Improvement suggestion (video walkthroughs) is concrete.

**Weakness:** Evaluation of presentation effectiveness (PDR/FDR) is brief. How did you adapt your communication for technical vs non-technical audiences specifically? The rubric says "technical and non-technical audiences" -- show the difference in how you communicated with assessors vs teammates vs the pilot.

---

## Composite Scores

| Criterion | v1 Score | v2 Score | Change | Band |
|-----------|----------|----------|--------|------|
| Teamwork (M16) | 68 | **78** | +10 | First (72-78 sub-band) |
| Self-management | 78 | **82** | +4 | First (78-83 sub-band) |
| Insight | 72 | **79** | +7 | First (72-78 sub-band) |

| AHEP4 | Score | Band |
|-------|-------|------|
| M5 (Design/originality) | **80** | First |
| M7 (Environmental/societal) | **77** | First |
| M16 (Team effectiveness) | **76** | First |
| M17 (Communication) | **78** | First |

**Overall estimated D7 mark: 79-80** (up from ~72-73 in v1)

---

## Summary: What Changed

The restructured report is substantially stronger. The biggest gains:

1. **Honesty about solo coding** -- Section 04's "Solo Coding Reality" transformed teamwork from a weakness into a strength. Admitting the problem IS the evidence of insight.
2. **Concrete conflict examples** -- ROS 2 vs MAVLink, workload frustration, button placement feedback. These replace vague claims with verifiable narratives.
3. **Structured self-assessment** -- Three named weaknesses, three development actions, career connection. This is a complete self-development programme, not a list.
4. **Communication evaluation** -- Four channels, each assessed for effectiveness. This directly satisfies M17.

## What's Still Weak (Top 3 Actions for v3)

1. **Teamwork conflict depth.** The report needs ONE example where you genuinely compromised or changed your technical approach based on team input. Currently every disagreement ends with you being right. Even if you WERE right, show the process of listening and considering alternatives seriously.

2. **Feedback to aid others' development.** The rubric explicitly requires this. Current examples are corrective (wiring reroute, risk assessment additions). Add an example of helping a teammate grow: teaching the pilot to read telemetry, helping the PM understand system architecture for the report, mentoring on Git workflow. Frame it as developing their capability, not fixing their output.

3. **Team effectiveness evaluation (not just your own).** Add 2-3 sentences evaluating the team's collective performance: Was the 5-person structure right for this project? What would you change about role allocation? How did the team's diverse backgrounds (or lack thereof) affect outcomes? This directly addresses the M16 requirement to "evaluate effectiveness of team performance."

---

## Rough Page Estimate

| Section | Current est. | Target |
|---------|-------------|--------|
| 01 Introduction | ~0.4 pg | 0.4 |
| 02 Design/M5 | ~1.3 pg | 1.2 |
| 03 Impact/M7 | ~0.7 pg | 0.7 |
| 04 Teamwork/M16+M17 | ~1.8 pg | 1.8 |
| 05 Self-development | ~1.3 pg | 1.3 |
| **Total** | **~5.5 pg** | **5.0 max** |

The report is likely slightly over the 5-page limit. Trim the introduction (currently verbose) and compress the STEEPLE paragraph in Section 02 to recover ~0.5 pages.
