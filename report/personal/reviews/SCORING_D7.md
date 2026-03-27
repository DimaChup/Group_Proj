# D7 Individual Reflective Report -- Scoring Against Rubric

**Date:** 2026-03-27
**Sections reviewed:** 01_introduction, 02_technical_contributions, 02_design_problem_solving (M5), 03_design_philosophy, 03_societal_environmental (M7), 04_challenges, 05_skills_developed, 06_team_dynamics, 07_reflection

---

## CRITICAL STRUCTURAL ISSUE

**`main.tex` does not include two written sections:**
- `02_design_problem_solving.tex` (M5) -- exists but NOT in `\input{}` list
- `03_societal_environmental.tex` (M7) -- exists but NOT in `\input{}` list

The compiled PDF will be missing the explicit M5 and M7 sections. This must be fixed immediately. The current `main.tex` includes `02_technical_contributions` and `03_design_philosophy` instead. You likely want to either replace those or add the AHEP4 sections alongside them.

**Recommendation:** Replace or merge. The current structure has 7 sections across ~4,500 words (estimated). The 5-page limit (excl. cover/appendices) at 11pt with 20mm margins and 1.15 spacing gives roughly 3,500-4,000 words. You are likely over the page limit. You need to consolidate.

---

## D7 Rubric Criterion 1: TEAMWORK (maps to M16)

**Current Score: 68/100** (just below top band)

### What's Strong
- Section 06 (Team Dynamics) is remarkably honest and self-aware. The "Solo Coding Reality" subsection directly confronts the imbalanced workload without making excuses.
- Clear description of what delegation looked like in practice and why it failed ("barrier to entry was too high for a short-term contribution").
- Identifies specific things that worked well: clear task boundaries, documented handoff points, checklists enabling collaboration across skill gaps.
- The simulator-as-communication-tool insight is genuinely creative.
- Acknowledges the speed-vs-inclusion trade-off explicitly and evaluates own choice ("right call for project outcome, wrong call for team learning").

### What's Missing
- **No evidence of conflict management.** The rubric explicitly asks for "able to manage conflict." There is tension described (workload imbalance, pace vs inclusion) but no specific conflict episode and how it was resolved. Even if no major conflicts occurred, the report should describe how disagreements were handled or prevented.
- **No evidence of responsiveness to group members' interests and obligations.** The rubric asks for this specifically. The report describes what the team did but not how the author adapted to teammates' schedules, interests, or personal circumstances.
- **Creativity and flexibility in teamwork is weak.** The report admits choosing speed over inclusion repeatedly. The rubric wants "outstanding ability to work and lead a team with creativity and flexibility" -- the author needs to show creative approaches to enabling team contribution, not just explain why delegation was hard.
- **No peer feedback mechanisms described.** Did you run retrospectives? Code reviews? How did you give/receive feedback within the team?
- **M16 requires "evaluate effectiveness of own and team performance."** The evaluation is present but could be more structured -- e.g., what metrics or criteria define "effective"?

### Specific Improvements to Reach 75+
1. Add a concrete conflict or disagreement example and how it was resolved (even a minor one: "We disagreed about whether to use ROS vs raw MAVLink. I advocated for raw MAVLink because... The team accepted this after I demonstrated...")
2. Add a paragraph on how you adapted to teammates' constraints (e.g., "Team member X had exam commitments in week 18, so I front-loaded the software integration to avoid blocking hardware assembly").
3. Show at least one creative attempt to enable collaboration: pair programming session, a simplified API designed specifically for a teammate to implement against, a code walkthrough you ran.
4. Add a sentence about feedback mechanisms: "We ran weekly check-ins where I presented progress and the team flagged concerns."
5. Quantify team effectiveness: "We met X of Y milestones on time. The hardware track completed assembly by week N, enabling software integration testing."

---

## D7 Rubric Criterion 2: SELF-MANAGEMENT

**Current Score: 78/100** (solidly in top band)

### What's Strong
- The report demonstrates outstanding autonomous working throughout. The author built 15,000 lines across 50+ files, 41 test scripts, a full simulator, and multiple ground station variants -- all largely independently.
- Professional attitude is evident in the progressive testing methodology, documentation discipline (CLAUDE.md as living document), and simulation-first development approach.
- The "What I Would Do Differently" subsection in 07_reflection shows genuine self-organisational awareness: starting with the Pi earlier, investing in automated tests earlier, recording flight video earlier.
- Field day productivity despite weather cancellation demonstrates excellent adaptability -- the author had pre-planned bench tests that could run without flying.
- The FIELD_QUICK_REF.md preparation for no-internet scenarios shows professional-level planning.

### What's Missing
- **No explicit mention of time management or scheduling.** How was work planned across the semester? Were there milestones? A Gantt chart? Weekly goals? The rubric wants "outstanding self-organisational skills" -- show the system, not just the output.
- **No mention of handling setbacks emotionally/professionally.** The challenges section is purely technical. How did you handle the frustration of weather cancellation? The pressure of being the sole software developer?
- **No evidence of balancing this project with other coursework/life.** The rubric's "professional attitude to completing all tasks" implies managing competing priorities.

### Specific Improvements to Reach 80+
1. Add 2-3 sentences about how you structured your time: "I set weekly milestones aligned with the project timeline. Weeks 12-15 focused on simulation validation, weeks 16-18 on Pi deployment, weeks 19-20 on field testing."
2. Mention how you balanced this project with other MSc commitments.
3. The CLAUDE.md/documentation discipline is a strong self-management example -- explicitly frame it as a self-management tool ("Maintaining a living project document meant I never lost context between work sessions, even after breaks of several days").

---

## D7 Rubric Criterion 3: INSIGHT

**Current Score: 72/100** (bottom of top band)

### What's Strong
- Honest self-assessment of strengths: "I am most productive as a technical lead who builds the core system, not as a manager who coordinates others' contributions."
- Clear identification of weaknesses: impatience with delegation, systems reflecting a single mental model, designing for solo development rather than collaboration.
- The "What I Would Do Differently" section is excellent -- four specific, actionable improvements with clear reasoning.
- The "Key Takeaways" are genuinely insightful, particularly "the quality of an autonomous system is determined not by the cleverness of its algorithms, but by the rigour of its testing."
- Connection to career goals is authentic and specific.

### What's Missing
- **No explicit self-development programme.** The rubric asks for "implement effective self-development programme." What are you going to do about the weaknesses you identified? "I would approach differently in future team settings" is vague. What specific actions, courses, or practices will you adopt?
- **No evidence of providing feedback to others.** The rubric explicitly asks for "provide effective feedback to others." Did you give feedback to teammates on their work? Did you review their risk assessments, flight parameter research, or hardware assembly? How did you communicate what was good and what needed improvement?
- **No evidence of goal-setting.** The rubric mentions "confidence in working autonomously, setting own goals." The report shows autonomous work but does not discuss how goals were set and whether they were achieved.
- **Strengths assessment is narrow.** The report identifies technical strengths well but does not assess interpersonal, communication, or leadership strengths/weaknesses beyond the delegation point.

### Specific Improvements to Reach 78+
1. Add a "Self-Development Plan" paragraph: "To address my delegation weakness, I plan to [specific action]. To improve cross-skill-gap communication, I will [specific action]. In my next team project, I will [specific commitment]."
2. Add a concrete example of giving feedback to a teammate: "I reviewed the hardware assembly against the wiring diagram and flagged that the GPS antenna cable routing could cause interference. I suggested rerouting along the arm, which the hardware lead implemented."
3. Frame the weekly documentation updates as deliberate goal-setting: "Each week I set specific targets in the project tracker and evaluated progress against them."
4. Assess communication strengths/weaknesses explicitly: "I communicate technical concepts well through demonstrations and documentation, but I struggle with spontaneous verbal explanation of complex architecture decisions."

---

## AHEP4 Alignment

### M5: Complex problem design with originality, STEEPLE considerations

**Score: 70/100** (borderline top band -- BUT only if 02_design_problem_solving.tex is included in main.tex)

- **If the section is NOT included in the compiled PDF (current state): 55/100.** The M5 content exists in the file but will not appear in the submitted document. The other sections contain some M5-relevant material (design philosophy, challenges) but do not explicitly reference M5 or STEEPLE.
- **Originality** is well demonstrated: dual-backend architecture, inverse-variance weighting, simulation-first approach, progressive testing methodology.
- **STEEPLE** coverage in 02_design_problem_solving.tex is present but thin -- it reads as a checklist paragraph rather than integrated analysis. Safety and Environmental get decent treatment; Social, Technological, Economic, Political, Legal, and Ethical get one sentence each or less.
- **Health and safety** is well covered through the progressive testing methodology and geofence system.
- **Codes of practice / industry standards** are mentioned (CAA regulations, aerospace verification practices) but could cite specific standards (e.g., DO-178C, AS9100).

**To improve:**
1. FIX main.tex to include this section.
2. Expand STEEPLE beyond a single paragraph -- give Economic (cost of Pi vs GPU, accessibility for resource-limited SAR teams) and Political (drone regulation landscape, UK CAA vs international) at least 2-3 sentences each.
3. Cite a specific industry standard beyond just "aerospace verification practices."

### M7: Environmental and societal impact evaluation

**Score: 72/100** (BUT only if 03_societal_environmental.tex is included in main.tex)

- **If NOT included in compiled PDF (current state): 45/100.** There are scattered environmental references in other sections but no coherent M7 treatment.
- **Life-cycle analysis** is present and reasonably thorough: mission-level, hardware-level, development-level impacts.
- **Societal impact** discussion is good: acknowledges both positive potential (lives saved) and negative risks (surveillance concerns), with mitigation (human in the loop).
- **Environmental** specifics are solid: SSSI geofencing, Pi power consumption (5W), simulation reducing physical flights, battery disposal flagged.
- **Minimising adverse impacts** section covers noise, bystander risk, e-waste, and software reuse (MIT licence).

**To improve:**
1. FIX main.tex to include this section.
2. Add quantitative estimates where possible: "Simulation replaced approximately X physical flight tests, saving an estimated Y battery cycles and Z kg CO2 from avoided travel."
3. Mention dual-use concerns more directly -- this technology has military applications, which is especially relevant given the author's stated connection to Ukraine.

### M16: Team effectiveness evaluation

**Score: 65/100**

- Section 06 evaluates team dynamics well but focuses more on describing the situation than evaluating effectiveness against criteria.
- Missing: structured evaluation framework (what does "effective" look like?), peer feedback evidence, metrics.
- See Teamwork criterion above for improvements.

### M17: Communication effectiveness evaluation

**Score: 55/100** -- This is the weakest AHEP4 area.

- The report mentions communication challenges (explaining across skill gaps) and one creative solution (simulator as communication tool).
- **Missing entirely:** evaluation of communication methods used. The rubric wants you to "communicate effectively on complex engineering matters with technical and non-technical audiences" AND "evaluate effectiveness of methods used."
- No mention of: presentations given (PDR, FDR), how documentation was received by teammates, whether the ground station UI was effective for operators, how field day communication worked.

**To improve:**
1. Add a paragraph evaluating communication methods: "I used four primary communication channels: GitHub documentation (effective for persistent reference, poor for urgency), weekly meetings (good for alignment, limited by differing technical depths), the simulator (most effective for conveying system behaviour), and the flight day checklist (effective for coordinating non-software tasks). If I were to improve one, I would add short video walkthroughs of the codebase -- documentation alone was insufficient for teammates without strong programming backgrounds."
2. Reference the PDR/FDR presentations and how they went.
3. Evaluate whether the ground station UI achieved its communication goal (operator situational awareness during flight).

---

## Summary Scores

| Criterion | Current Score | Top Band Threshold | Gap |
|-----------|--------------|-------------------|-----|
| Teamwork (M16) | 68 | 72 | -4 |
| Self-management | 78 | 72 | +6 |
| Insight | 72 | 72 | 0 |
| M5 (design/STEEPLE) | 70* | 72 | -2 |
| M7 (env/societal) | 72* | 72 | 0 |
| M16 (team evaluation) | 65 | 72 | -7 |
| M17 (communication) | 55 | 72 | -17 |

*Scores assume the missing sections are added to main.tex. Without them, M5 drops to ~55 and M7 drops to ~45.

**Overall estimated D7 grade: 68-70** (if sections are included) or **60-63** (if sections remain excluded from main.tex).

---

## Priority Actions (ordered by impact)

1. **FIX main.tex** -- include `02_design_problem_solving.tex` and `03_societal_environmental.tex`. Without this, you lose ~15 marks.
2. **Add M17 communication evaluation** -- this is the biggest gap. Add a paragraph evaluating communication methods and their effectiveness.
3. **Add conflict management example** to Section 06 -- even a small one raises Teamwork from 68 to 72+.
4. **Add self-development programme** to Section 07 -- concrete actions to address identified weaknesses.
5. **Add feedback-to-others example** to Section 07 -- the rubric explicitly asks for this.
6. **Check page count** -- you likely have 6-7 pages of content for a 5-page limit. Consolidate: merge 02_technical_contributions into 02_design_problem_solving, merge 03_design_philosophy into the rest. The AHEP4-structured sections (M5, M7) are more strategically valuable than the free-form technical narrative.

---

## Structural Recommendation

The current 7-section structure (intro, tech contributions, design philosophy, challenges, skills, team, reflection) is narrative-driven but does not map to the rubric. A rubric-aligned structure would be:

1. Introduction (0.5 pages)
2. Design and Problem-Solving -- M5 (1 page) -- merge current 02_tech + 02_design + 03_philosophy
3. Societal and Environmental Impact -- M7 (0.75 pages)
4. Teamwork and Leadership -- M16 (1 page) -- current 06_team + conflict + feedback + communication evaluation
5. Communication -- M17 (0.5 pages) -- NEW, or merged into M16
6. Self-Assessment and Development -- M16/Insight (1 page) -- merge current 05_skills + 07_reflection
7. Conclusion (0.25 pages)

This structure explicitly addresses every rubric criterion and AHEP4 standard, making it easy for the marker to find evidence and award marks.
