# Professional Practice to D7 Mapping

> Single reference document. Maps every PP framework, quote, and concept to D7 sections.
> Generated 2026-04-16 from 8 extraction files + D7 brief.

---

## Table 1: Framework to D7 Section Mapping

| # | Framework | Source Lecture | D7 Section(s) | How to Use | Priority |
|---|-----------|--------------|----------------|------------|----------|
| 1 | **Lencioni Five Dysfunctions** (pyramid: Trust > Conflict > Commitment > Accountability > Results) | Five Dysfunctions (Graham, video) | s2a (structure), s2b (team working), s2c (what to change), s4b (what you did for team) | Map your team to the pyramid bottom-up. Solo-coding = absence of trust. FSM pushback = fear of conflict. Accountability collapsed onto you. | **MUST** |
| 2 | **Tuckman Stages** (Forming > Storming > Norming > Performing > Transforming) | Team Development (Graham, video) + PM2 slides 2-4 | s2a (structure), s2b (team working), s2c (what to change) | Map team timeline to F/S/N/P/T. Show regression after flight cancellations. Warn about artificial harmony. | **MUST** |
| 3 | **Risk Assessment** (5-step HSE process, f x c matrix, ALARP, residual risk) | Risk Management (Graham, two videos) + PM1 Downselection slides 8-20 | s1a (role/responsibilities), s1c (future focus), s3a (contributions), s3b (refocus) | You owned the risk register. Progressive test ladder = risk mitigation. Flight day cancellation = schedule risk that materialised. | **MUST** |
| 4 | **MCDA / Pairwise Comparison / Controlled Convergence** (4 down-selection tools) | Innovation Tools (Graham, video) + PM1 Downselection slides 1-7 | s1b (proud of), s2b (impactful elements), s3a (drove team forward) | Frame CV backend selection (TFLite vs NCNN) and model selection as structured decisions. Even if not formally used, reflect on what MCDA would have changed. | **SHOULD** |
| 5 | **Bennett DMIS** (6-stage intercultural sensitivity continuum: Denial > Defence > Minimisation > Acceptance > Adaptation > Integration) | Cultural Competence (Graham, video) | s2b (team working), s4a (what others did), s4b (what you did) | Place yourself on the continuum. Ukrainian "one person delivers" = cultural lens. Moving from Minimisation to Acceptance = growth. | **SHOULD** |
| 6 | **Shore Inclusion Framework** (2x2: Belongingness x Value in Uniqueness) | Cultural Competence (Graham, video) | s2b (team working), s4b (what you did for team) | Did team operate in Assimilation (treating everyone the same) or Inclusion? Adapting communication per teammate = moving toward Inclusion. | **SHOULD** |
| 7 | **Hofstede Cultural Dimensions** (6 dimensions: PDI, IDV, MAS, UAI, LTO, IVR) | Cultural Competence (Graham, video) | s2b (team working) | UA cultural context: high PDI, high UAI. Contrast with UK flat team structure. Brief mention only -- don't over-apply. | **COULD** |
| 8 | **Trompenaars 7 Dimensions** | Cultural Competence (Graham, video) | s2b (team working) | Universalism vs Particularism could explain code ownership debates. Probably too much for 5 pages. | **COULD** |
| 9 | **Meyer Culture Map** (8 scales) | Cultural Competence (Graham, video) | s2b | Low vs high context communication. Quick mention if space allows. | **COULD** |
| 10 | **WBS / Work Breakdown Structure** (100% rule, 5 levels max) | PM1 (Graham, slides 11-20) | s1a (role), s3a (contributions) | You created a WBS in the dashboard. Show decomposition discipline. | **SHOULD** |
| 11 | **Critical Path / Float** (network diagrams, forward/backward pass) | PM1 slides 22-33, PM2 slides 6-18 | s1a (role), s2b (impactful elements), s3b (refocus) | Hardware integration was the critical path. Software had float. Use to explain why flight cancellations hurt so much. | **SHOULD** |
| 12 | **Resource Levelling** (sequential vs ASAP vs levelled) | PM2 slides 19-26 | s2b (team working), s3a (contributions) | Colab training = subcontracted manufacturing. Staggering tasks on one Pi = resource levelling. | **COULD** |
| 13 | **Rolling Wave Planning** | PM2 slides 27-28 | s1a (role), s1c (future focus) | Near-term detail, far-term abstract. Natural for agile-ish project. Quick mention. | **COULD** |
| 14 | **Waterfall vs Agile** (and hybrid approaches) | PM1 slide 9-10, PM2 slide 5 | s1a (role), s2b (impactful elements) | Project was hybrid: waterfall for safety-critical hardware path, agile for CV pipeline. | **SHOULD** |
| 15 | **Gantt Chart** (5 components: dependencies, CP, float, length, milestones) | PM2 slides 6-16 | s3a (contributions) | Evidence of PM tools used. Brief mention. | **COULD** |
| 16 | **Three Pillars of Obligation** (Moral, Economic, Legal) | Risk Management video 1 | s1c (future focus), s3a (contributions) | Frame safety decisions through all three pillars (geofence = moral + legal, kill switch = moral). | **SHOULD** |
| 17 | **HSAWA 1974** (employer duties, "reasonably practicable") | Risk Management video 1 | s1c (future focus) | Connect ALARP to "reasonably practicable." Professional responsibility framing. | **COULD** |
| 18 | **Risk Compensation** | Risk Management video 2 | s1c (future focus), s3b (refocus) | Simulation confidence (7.7/10) created overconfidence about real-world (2.1/10). NCNN speed gains could tempt faster flight. | **SHOULD** |
| 19 | **Tuckman Timeline Scenarios** (best/probable/worst case) | Team Development (Graham) + PM2 slides 2-4 | s2a (structure), s2c (what to change) | Our team was probably-to-worst-case. Brief Forming, extended Storming, compressed Performing. | **MUST** (part of Tuckman) |
| 20 | **Team Time Allocation Model** (technical vs management split) | Team Development (Graham) | s1a (role), s2c (what to change) | Poor teams spend >50% on management. Our team arguably under-invested in management early, then over-corrected. | **SHOULD** |

---

## Table 2: Quote Bank by D7 Section

### s1 My Role

| Quote | Source | Usage |
|-------|--------|-------|
| "If the problem was simple, it could have been fixed by an individual and we wouldn't need a team." | Graham/Lencioni (Five Dysfunctions) | Justify why solo coding was the wrong instinct despite being faster |
| "The forced detachment from the technical work which might have been the reason why you entered engineering, can be too much to bear." | Graham (Tuckman) | Reflect on tension between wanting to code and needing to manage |
| "The team's work IS your work." | Graham (Tuckman) | Reframe leadership -- managing the team was not a distraction from the real work |
| "The art of risk management, for it is an art, is the most important activity of any senior manager in a technical field." | Graham (Risk Management) | Frame your risk ownership as professional leadership |
| "Your professional approach to working safely starts now." | Graham (Risk Management) | Connect university project to professional practice |
| "Showing that you are skilled in risk management can also help unlock greater investment or personal opportunity." | Graham (Risk Management) | Closing statement linking risk competence to career |
| "Not one size fits all." | Graham (PM1) | Justify hybrid waterfall/agile approach |

### s2 My Team

| Quote | Source | Usage |
|-------|--------|-------|
| "Hiding our weaknesses, our mistakes and our humanity prevents the growth of trust." | Graham/Lencioni (Five Dysfunctions) | Solo-coding pattern = invulnerability |
| "Without exception, every new team I've worked within or have managed has experienced this stage [Storming]." | Graham (Tuckman) | Normalise your team's conflicts |
| "Violently agreeing with each other all the time -- be careful of that." | Graham (Tuckman) | Flag artificial harmony risk in your team |
| "Peer pressure in the team, providing there's a foundation of trust, is way more effective than a bureaucratic measurement system." | Graham/Lencioni (Five Dysfunctions) | Why accountability structures failed |
| "Most team members don't expect the team should agree with their personal views... what they object to is when they don't feel like their voice has been heard." | Graham/Lencioni (Five Dysfunctions) | FSM conflict resolution, bypassed input |
| "We see what we believe." | Graham (Cultural Competence) | Recognising own cultural lens in team dynamics |
| "In many circumstances, treating everyone the same is clearly unfair." | Graham (Cultural Competence) | Adapting approach per teammate |
| "Teams that invest in managing themselves well will have to spend less time managing themselves in the end." | Graham (Tuckman) | Justify time spent on team processes |
| "Diversity of thought is critical in finding the best solutions." | Graham (Tuckman) | Value of disagreement within team |
| "A group of individuals is not a team." | Graham (PM2) | If the team operated as individuals rather than a unit |
| "You can go from right to left. Certainly your team could undevelop." | Graham (Tuckman) | Explain regression after disruptions |

### s3 My Impact

| Quote | Source | Usage |
|-------|--------|-------|
| "The tools are there to support, not replace, your thinking." | Graham (Innovation Tools) | Decision-making approach |
| "No one has to be harmed for an offence to be committed -- there only has to be a risk of harm." | Graham (Risk Management) | Why geofence matters even though no incursion occurred |
| "The best businesses will be those that have a strong health and safety culture at their core." | Graham (Risk Management) | Progressive test ladder philosophy |
| "Different mitigations can improve the likelihood, consequence, or both." | Graham (Risk Management) | Analysing geofence (likelihood) vs kill switch (consequence) |
| "Risks have to be balanced against opportunities." | Graham (Risk Management) | ALARP decisions (altitude vs detection rate trade-off) |
| "Using an analytical tool is a great way of taking the focus away from personalities and placing the debate back within the realms of logic and reason." | Graham (Innovation Tools) | How structured tools could have helped team decisions |
| "These tools are useful, I would say essential for explaining to your stakeholders why you chose a particular idea." | Graham (Innovation Tools) | Communicating design decisions to team and markers |

### s4 My Support

| Quote | Source | Usage |
|-------|--------|-------|
| "With little accountability within the team, the burden falls back on the team leader to be the source of all discipline and compliance." | Graham/Lencioni (Five Dysfunctions) | How you became sole disciplinarian |
| "It's generally not a lack of resources or technical skill that prevents most teams from succeeding, but is often more related to a set of basic human behaviours." | Graham/Lencioni (Five Dysfunctions) | Closing identity-shift -- soft skills mattered more than code |
| "The individual's identity is more relevant than the culture of any group that they might belong to." | Graham (Cultural Competence) | Avoiding stereotyping while adapting to teammates |
| "The skill of the engineer is in knowing the strengths and limitations of the models." | Graham (Cultural Competence) | Meta-reflection on applying frameworks themselves |
| "If you see something you don't like, please don't walk by, report it." | Graham (Risk Management) | Team safety culture and mutual accountability |

---

## Table 3: MUST / SHOULD / COULD Classification

### MUST-INCLUDE (brief says "refer to Professional Practice"; rubric demands evidence)

| Framework | Why MUST | D7 sections |
|-----------|---------|-------------|
| **Lencioni Five Dysfunctions** | Taught in PP. Directly maps to Teamwork rubric criterion (conflict management, team effectiveness). The pyramid IS the analytical framework for s2. | s2a, s2b, s2c, s4b |
| **Tuckman Stages** | Taught in PP. The brief asks about team structure changes over time (s2a). Tuckman IS the standard model for team development over time. | s2a, s2b, s2c |
| **Risk Assessment** (f x c, ALARP, mitigations) | Taught in PP. Shows M16 (evaluate effectiveness) and M17 (communicate on complex matters). Progressive test ladder = risk management applied. | s1a, s3a, s3b |

### SHOULD-INCLUDE (strengthen rubric score, demonstrate breadth)

| Framework | Why SHOULD | D7 sections |
|-----------|-----------|-------------|
| **MCDA / Down-Selection Tools** | Shows structured decision-making. Even if not formally used, reflecting on what MCDA would have improved = Hatton L4. | s1b, s2b, s3a |
| **Bennett DMIS** | Shows self-awareness re cultural lens. Ukrainian background = genuine material. Moves Self-management and Insight scores up. | s2b, s4a, s4b |
| **Shore Inclusion Framework** | Quick 2x2 that adds analytical depth to cultural discussion without taking much space. Pairs with Bennett. | s2b, s4b |
| **Critical Path / Float** | Explains why hardware delays were catastrophic (zero float on critical path). Shows PM competence. | s1a, s2b, s3b |
| **Waterfall vs Agile hybrid** | Shows awareness of PM methodology. Justifies your approach. | s1a, s2b |
| **Three Pillars of Obligation** (Moral/Economic/Legal) | Quick frame for safety decisions. One sentence suffices. | s1c, s3a |
| **Risk Compensation** | Self-critical insight about simulation overconfidence. Strongly L4. | s1c, s3b |
| **Team Time Allocation** | Quick mention -- teams that skip management pay for it later. | s2c |

### COULD-INCLUDE (only if space allows; diminishing returns)

| Framework | Why COULD | Risk of Including |
|-----------|----------|-------------------|
| Hofstede dimensions | Gives specificity to cultural analysis (PDI, UAI numbers for UA vs UK) | Easily becomes superficial. Graham warns "a little knowledge can be a dangerous thing." |
| Trompenaars dimensions | Universalism vs Particularism is interesting for code ownership | Too many cultural models = padding |
| Meyer Culture Map | High/low context communication | Third cultural model = overkill |
| Resource Levelling | Colab as subcontracted manufacturing is a nice parallel | Too technical for D7 reflection |
| Rolling Wave Planning | Natural fit but low reflective depth | One sentence max |
| Gantt Chart mechanics | Evidence you used PM tools | Better as D6 content |
| WBS rules (100% rule) | Shows decomposition discipline | One sentence in s1a |
| HSAWA legal details | Flixborough, VPF, legislation timeline | Way too technical for D7 |

---

## Table 4: Anecdote x Framework Mapping

| Incident | Approx Date | Framework(s) | D7 Section | Hatton L4 Move |
|----------|-------------|-------------|------------|----------------|
| **Solo-coding main.py to 1411 lines** | Wk12-17 | Lencioni L1 (Absence of Trust) | s2a, s1b | "My 1411-line main.py was invulnerability made architectural -- I was ring-fencing work because I didn't trust the team to navigate it." |
| **Wk17 FSM pushback from Robin** | Wk17 | Lencioni L2 (Fear of Conflict) + Tuckman (Storming) | s2b | "I now see the FSM conflict was healthy Storming (Tuckman, 1965), not dysfunction. Graham's pyramid suggests the discomfort I felt was because trust was insufficient to sustain productive conflict." |
| **Refactoring main.py from 1411 to 754 lines** | Wk20 | Lencioni L1 antidote (opening trust) + Tuckman (Norming) | s1b, s3a | "The refactor was as much about opening trust as about code quality. Creating 6 extracted modules with clear interfaces was an architectural invitation for others to contribute." |
| **Wk20 PM workload complaint surfacing late** | Wk20 | Lencioni L2 (back-channel communication) + Tuckman (delayed Storming) | s2b, s2c | "This issue surfaced via back-channels rather than open discussion -- exactly the symptom Lencioni describes when trust is insufficient for direct conflict." |
| **Three flight day cancellations** | Multiple | Risk Assessment (schedule risk f=4, c=3, RN=12 Intolerable) + Tuckman (regression) | s2b, s3b | "Weather cancellations were a textbook schedule risk that we scored as Intolerable (RN=12). Tuckman predicts such disruptions cause regression -- and we did re-enter Storming as confidence in the timeline eroded." |
| **820 solo commits** | Throughout | Lencioni L5 (Inattention to Results -- individual over collective) | s1c, s2c | "My 820 solo commits were their own form of ego-driven behaviour. I optimised for my output rather than building team capability -- exactly Lencioni's Level 5 dysfunction." |
| **Creating handoff docs (COLLEAGUE_CHECKLIST, VISION_PIPELINE)** | Wk20-21 | Lencioni L1 antidote (shared experiences) + Tuckman (Norming) | s4b, s3a | "Creating onboarding documentation was a trust-building act -- it signalled 'I want you to understand this code' rather than 'stay away from my domain.'" |
| **CV backend decision (TFLite to NCNN)** | Wk17-20 | MCDA (not formally used, should have been) | s1b, s3a | "Our CV backend migration was driven by benchmark numbers alone. A formal MCDA incorporating deployment complexity and maintainability would have produced a more defensible decision." |
| **Simulation scoring 7.7/10 vs real hardware 2.1/10** | Wk21+ | Risk Compensation | s3b, s1c | "Successful simulation created risk compensation: confidence in virtual results reduced perceived urgency of hardware testing." |
| **Adapting communication per teammate** | Throughout | Bennett DMIS (Minimisation to Acceptance) + Shore (Assimilation to Inclusion) | s4b, s2b | "My default 'treat everyone the same' approach was, as Graham argues, 'clearly unfair.' Moving toward Bennett's Acceptance required me to adapt my communication style per teammate's strengths." |
| **Progressive test ladder (5 steps)** | Wk15+ | Risk Assessment (mitigations reduce likelihood AND consequence) + Critical Path | s1b, s3a | "The 5-step test ladder was controlled convergence applied to validation: each step simultaneously reduced the likelihood of a dangerous failure and the consequence of one." |
| **Bench testing during cancelled flight day** | 2026-03-11 | Float/Critical Path + Risk mitigation | s1a, s3a | "Because I had identified that documentation was off the critical path, I redirected effort to bench calibration -- tasks that were ON the critical path but could be partially advanced without flying." |
| **Field day: FOV calibration, lens calibration** | 2026-03-11 | Rolling wave planning (adapting near-term plan) | s1a | "When flight was cancelled, we replanned immediately -- classic rolling wave: the far-term plan (flight) was deferred while near-term tasks were re-prioritised." |

---

## Section 5: BibTeX Entries (Consolidated)

```bibtex
% === LENCIONI (Five Dysfunctions) ===
@book{lencioni2002,
  author    = {Lencioni, Patrick M.},
  title     = {The Five Dysfunctions of a Team: A Leadership Fable},
  year      = {2002},
  publisher = {Jossey-Bass},
  address   = {San Francisco},
}

@book{lencioni2005,
  author    = {Lencioni, Patrick M.},
  title     = {Overcoming the Five Dysfunctions of a Team: A Field Guide for Leaders, Managers, and Facilitators},
  year      = {2005},
  publisher = {Jossey-Bass},
  address   = {San Francisco},
  series    = {Leadership Fables},
}

@misc{graham2025dysfunctions,
  author       = {Graham, Mark},
  title        = {The Five Dysfunctions of a Team [Lecture video]},
  year         = {2025},
  howpublished = {AENGM0074 Professional Practice, University of Bristol},
  note         = {Blackboard video and slides},
}

% === TUCKMAN (Team Development) ===
@article{tuckman1965,
  author  = {Tuckman, Bruce W.},
  title   = {Developmental Sequence in Small Groups},
  journal = {Psychological Bulletin},
  year    = {1965},
  volume  = {63},
  number  = {6},
  pages   = {384--399},
  doi     = {10.1037/h0022100},
}

@article{tuckman1977,
  author  = {Tuckman, Bruce W. and Jensen, Mary Ann C.},
  title   = {Stages of Small-Group Development Revisited},
  journal = {Group \& Organization Studies},
  year    = {1977},
  volume  = {2},
  number  = {4},
  pages   = {419--427},
  doi     = {10.1177/105960117700200404},
}

% === CULTURAL COMPETENCE ===
@misc{graham2026cultural,
  author       = {Graham, Mark},
  title        = {Building Cultural Competence},
  year         = {2026},
  howpublished = {AENGM0074 Professional Practice lecture, University of Bristol},
  note         = {Video lecture on cultural competence, inclusion, and intercultural sensitivity models},
}

@article{shore2011inclusion,
  author  = {Shore, Lynn M. and Randel, Amy E. and Chung, Beth G. and Dean, Michelle A. and Ehrhart, Karen Holcombe and Singh, Gangaram},
  title   = {Inclusion and Diversity in Work Groups: A Review and Model for Future Research},
  journal = {Journal of Management},
  volume  = {37},
  number  = {4},
  pages   = {1262--1289},
  year    = {2011},
  doi     = {10.1177/0149206310385943},
}

@book{hofstede2001culture,
  author    = {Hofstede, Geert},
  title     = {Culture's Consequences: Comparing Values, Behaviors, Institutions and Organizations Across Nations},
  edition   = {2nd},
  publisher = {Sage Publications},
  year      = {2001},
  address   = {Thousand Oaks, CA},
}

@book{trompenaars1997riding,
  author    = {Trompenaars, Fons and Hampden-Turner, Charles},
  title     = {Riding the Waves of Culture: Understanding Diversity in Global Business},
  edition   = {2nd},
  publisher = {Nicholas Brealey Publishing},
  year      = {1997},
  address   = {London},
}

@book{meyer2014culture,
  author    = {Meyer, Erin},
  title     = {The Culture Map: Breaking Through the Invisible Boundaries of Global Business},
  publisher = {PublicAffairs},
  year      = {2014},
  address   = {New York},
}

@article{bennett1986developmental,
  author  = {Bennett, Milton J.},
  title   = {A Developmental Approach to Training for Intercultural Sensitivity},
  journal = {International Journal of Intercultural Relations},
  volume  = {10},
  number  = {2},
  pages   = {179--196},
  year    = {1986},
  doi     = {10.1016/0147-1767(86)90005-2},
}

% === RISK MANAGEMENT ===
@misc{graham2023safety,
  author       = {Graham, Mark},
  title        = {Health and Safety at Work},
  year         = {2023},
  howpublished = {AENGM0074 Professional Practice video lecture},
  institution  = {University of Bristol},
}

@misc{graham2023risk,
  author       = {Graham, Mark},
  title        = {Assessing and Managing Risk},
  year         = {2023},
  howpublished = {AENGM0074 Professional Practice video lecture},
  institution  = {University of Bristol},
}

@standard{iso31000:2018,
  author       = {{International Organization for Standardization}},
  title        = {ISO 31000:2018 Risk Management -- Guidelines},
  year         = {2018},
  organization = {ISO},
}

@book{bernstein1996gods,
  author    = {Bernstein, Peter L.},
  title     = {Against the Gods: The Remarkable Story of Risk},
  year      = {1996},
  publisher = {John Wiley \& Sons},
  address   = {New York},
}

% === INNOVATION / DOWN-SELECTION ===
@misc{graham_innovation_tools,
  author       = {Graham, Mark},
  title        = {Innovation Methods: Down-Selection Tools},
  year         = {2025},
  howpublished = {AENGM0074 Professional Practice video lecture, University of Bristol},
  note         = {Covers pairwise comparison (ranking and numerical), controlled convergence (Pugh matrix), and MCDA},
}

% === PROJECT MANAGEMENT ===
@misc{graham2025pm1,
  author       = {Graham, Mark},
  title        = {Project Management 1},
  year         = {2025},
  howpublished = {AENGM0074 Professional Practice lecture, University of Bristol},
  note         = {WBS, network diagrams, critical path, dependencies},
}

@misc{graham2025pm2,
  author       = {Graham, Mark},
  title        = {Project Management 2},
  year         = {2025},
  howpublished = {AENGM0074 Professional Practice lecture, University of Bristol},
  note         = {Gantt charts, resource levelling, rolling wave planning, Tuckman model},
}
```

---

## Section 6: Frameworks to NOT Cite (and Why)

| Framework / Content | Source | Why NOT for D7 |
|---------------------|--------|---------------|
| **CPM forward/backward pass calculations** | PM1 slides 22-31 | That is D6 technical content (show you used network diagrams), not D7 reflection. Citing the concept of critical path is fine; doing the maths is not. |
| **ALARP / VPF arithmetic** (1.83M per fatality) | Risk Management video 1 | Too technical. Mention ALARP as a principle ("reasonably practicable"), don't do the calculation. |
| **Gantt chart mechanics** (5 components, milestone symbols) | PM2 slides 6-16 | D6 content. In D7, you can say "I created a Gantt chart" but don't explain how Gantt charts work. |
| **Network diagram dummy activities** | PM1 slide 30 | Pure PM technique, no reflective value for D7. |
| **Resource levelling spreadsheet mechanics** | PM2 slides 19-26, Excel task | The concept is useful (one sentence about staggering tasks), but the worked example is D6. |
| **Flixborough disaster details** | Risk Management video 1 | Historical context, not relevant to your project reflection. |
| **HSAWA Section 2 legal text** | Risk Management video 1 | Too much legal detail. One sentence about "duty of care" or "reasonably practicable" suffices. |
| **Hofstede dimension scores for specific countries** | Cultural Competence | Graham explicitly warns against oversimplifying. Don't cite "Ukraine scores X on PDI" -- instead say "my cultural background instilled..." |
| **Trompenaars / Meyer detailed dimension descriptions** | Cultural Competence | Three cultural models is overkill. Pick ONE (Bennett DMIS) and cite Shore as a complement. Don't try to use all three quantitative cultural models. |
| **F1 pit-stop risk assessment quiz** | Risk Management Excel | Worked example for the lecture, not relevant to your project. |
| **RIAT 2024 risk assessment** | PM1 slide 20 | Professional example, but citing it in D7 adds nothing to personal reflection. |
| **Pairwise comparison arithmetic** (9/3/1/0.333/0.111 scale) | Innovation Tools | The concept of structured decision-making matters; the specific numerical scale does not belong in D7. |
| **WBS "100% rule" / "5 levels max" rules** | PM1 slides 12-17 | One-sentence mention is fine; don't explain WBS rules in D7. |
| **Boeing programme/portfolio hierarchy** | PM1 slide 4 | Lecture example, irrelevant to your reflection. |
| **Priestley v Fowler (1835)** | Risk Management video 1 | Historical legal case, no reflective value. |

---

## Quick-Reference: Optimal Framework Allocation per Section

Given 5 pages, here is the recommended framework density:

| D7 Section | ~Words | Primary Frameworks | Secondary/Brief |
|------------|--------|-------------------|-----------------|
| **s1 My Role** (~1 page) | ~400 | Risk ownership, critical path awareness | Hybrid waterfall/agile, rolling wave |
| **s2 My Team** (~1.5 pages) | ~600 | Lencioni (primary analytical lens), Tuckman (timeline structure) | Bennett DMIS + Shore inclusion (1 paragraph), team time allocation (1 sentence) |
| **s3 My Impact** (~1 page) | ~400 | Risk mitigations mapped to f x c, progressive test ladder as controlled convergence | MCDA reflection (what MCDA would have improved), risk compensation |
| **s4 My Support** (~0.5 page) | ~250 | Lencioni L4 (accountability burden), handoff docs as trust-building | Cultural adaptation per teammate |

Total unique frameworks deployed: 7-8 (Lencioni, Tuckman, Risk Assessment, Bennett DMIS, Shore, MCDA reflection, Critical Path, Risk Compensation). This is the right density for 5 pages -- enough to show breadth without becoming a framework catalogue.
