# PP_EXPANDED_ALL -- Merged Concept Library

> **Generated:** 2026-04-16
> **Sources:** Five Dysfunctions (FD), Team Development (TD), Risk Management (RM), Innovation/PM (IT, PM, L4)
> **Raw total:** 168 concepts across 4 files
> **Duplicates removed:** 9 (see Deduplication Log below)
> **Final count:** 159 unique concepts
> **JS array entries:** 62 (grouped for planner usability)

---

## Summary

| Priority | Count | Description |
|----------|-------|-------------|
| **MUST** | 43 | Core frameworks + direct project evidence. Use in D7 body. |
| **SHOULD** | 52 | Antidotes, tools, supporting concepts. Use in "what to change" and "refocus." |
| **COULD** | 38 | Supporting symptoms, metaphors, polish. Use if space allows. |
| **SKIP** | 6 + 11 RM-LOW | Peripheral. Only if desperate for variety. |
| **Removed (duplicate)** | 9 | Merged into richer entry. |

### Count by Source

| Source | Must | Should | Could | Skip | Total |
|--------|------|--------|-------|------|-------|
| Five Dysfunctions (FD) | 13 | 17 | 12 | 2 | 44 |
| Team Development (TD) | 12 | 12 | 14 | 2 | 40 |
| Risk Management (RM) | 18 | 13 | 0 | 7 | 38 |
| Innovation Tools (IT) | 5 | 5 | 0 | 0 | 10 |
| Project Management (PM) | 7 | 10 | 5 | 2 | 24 |
| Cross-cutting L4 (L4) | 3 | 2 | 0 | 0 | 5 |

---

## Deduplication Log

| Removed | Kept (richer) | Reason |
|---------|---------------|--------|
| PM-01 (Three Pillars) | RM-17 (Three Pillars: Moral, Economic, Legal) | Same concept, RM version has worked example |
| PM-02 (F x C) | RM-05 (Risk Number = L x C) | Same formula, RM version more detailed |
| PM-03 (Residual Risk) | RM-13 (Pre/Post Mitigation Scoring) | Same concept, RM has before/after example |
| PM-16 (Tuckman Five Stages) | TD-01 through TD-06 | PM-16 is summary; TD entries have per-stage detail |
| TD-21 (skip management irony) | TD-24 (investment paradox) | TD-24 subsumes TD-21's insight with richer application |
| FD-29 (chain metaphor) | FD-01 (pyramid model) | Chain metaphor is minor variant of pyramid; merge into FD-01 |
| TD-09 (true norming = resolved conflict) | TD-08 (violently agreeing) | TD-09 is the flip side of TD-08; merge |
| PM-04 (existing vs additional mitigations) | RM-13 (pre/post mitigation) | RM-13 already covers the split |
| TD-35 (L3 dialogic) | TD-36 (L4 critical) | TD-35 is prerequisite of TD-36; merge guidance into TD-36 |

---

## MUST (43 concepts)

### Five Dysfunctions (Lencioni)

**FD-01** | The Pyramid Model (sequential, bottom-up)
- src: Lencioni 2002, Graham lecture
- sections: 3a, 2a
- how: Use as overarching analytical framework. Trust must be fixed before conflict, conflict before commitment, etc. Map team's journey bottom-up. The chain metaphor (slide 9) reinforces this: break one link and the whole chain fails.
- quote: "Each level builds on the one below it. Fix from the bottom up."
- ref: Lencioni (2002); Graham (2025)

**FD-02** | Absence of Trust -- Invulnerability
- src: Lencioni Level 1
- sections: 1a, 2a, 3a
- how: Solo-coding pattern (1411-line main.py, 820 solo commits) is textbook invulnerability. Ring-fenced work because he didn't trust others to navigate it.
- quote: "Hiding our weaknesses, our mistakes and our humanity prevents the growth of trust."
- ref: Graham (2025); Lencioni (2002)

**FD-03** | Ring-fencing work (trust symptom)
- src: Slide transcript
- sections: 1a, 2b
- how: Name Apollo's behaviour explicitly as 'ring-fencing.' The 1411-line monolith was an architectural ring-fence.
- quote: "Acting defensively / ring-fencing work"
- ref: Lencioni (2002)

**FD-04** | Fear of Conflict -- Artificial Harmony
- src: Lencioni Level 2
- sections: 2b, 3a
- how: Team avoided difficult conversations about unequal workload. Wk20 PM workload complaint surfaced late. Robin's FSM pushback (Wk17) was one of few moments of real conflict.
- quote: "This apparent harmony is really an artificial harmony."
- ref: Lencioni (2002)

**FD-05** | Back channels and gossip (conflict symptom)
- src: Slide 10 symptoms
- sections: 2b
- how: Important comms via side-channels rather than open team meetings. Direct Lencioni symptom of fear of conflict.
- quote: "Important communication happens via back channels and gossip."
- ref: Lencioni (2002)

**FD-06** | Lack of Commitment -- Ambiguity
- src: Lencioni Level 3
- sections: 2a, 2c, 3a
- how: Different perceptions of what the drone should do. No written objectives until late. FSM architecture revisited rather than committed to.
- quote: "Commitment needs clarity and buy-in."
- ref: Lencioni (2002)

**FD-07** | The Weasel Metaphor (commitment avoidance)
- src: Graham transcript, Slide 6
- sections: 2b, 2c
- how: Some teammates avoided written commitments. But Apollo also avoided committing to collaboration -- 820 solo commits were his own form of hiding behind ambiguity.
- quote: "Usually more slippery than a weasel and are typically the ones who hate action logs."
- ref: Graham (2025)

**FD-08** | Avoidance of Accountability -- Low Standards
- src: Lencioni Level 4
- sections: 2b, 4b, 3a
- how: Accountability fell entirely on Apollo as de facto tech lead. No peer challenge on code quality, deadlines, or contributions.
- quote: "If I was never committed to the team's goals, how can you call me out?"
- ref: Lencioni (2002)

**FD-09** | Peer pressure beats bureaucracy
- src: Graham transcript
- sections: 2b, 2c, 4b
- how: Apollo's team had neither trust foundation nor peer pressure. Accountability collapsed onto the leader.
- quote: "Peer pressure in the team is way more effective than a bureaucratic measurement system."
- ref: Graham (2025)

**FD-10** | The Leader Burden (accountability consequence)
- src: Graham transcript
- sections: 2b, 4b
- how: Apollo became the sole source of discipline and compliance. This is exactly what Lencioni predicts when Level 4 fails.
- quote: "The burden falls back on the team leader to be the source of all discipline."
- ref: Graham (2025)

**FD-11** | Inattention to Results -- Status and Ego
- src: Lencioni Level 5
- sections: 2b, 3b, 3a
- how: Some members focused on own marks rather than collective drone success. Apollo's 820 solo commits = optimising his output rather than team capability.
- quote: "Individual success and ego become more relevant than the success of the group."
- ref: Lencioni (2002)

**FD-12** | Why teams exist (not individuals)
- src: Graham transcript
- sections: 3a, 4a
- how: Frame the identity shift: the instinct to solo-code was wrong even though faster. Complex problems require teams.
- quote: "If the problem was simple, it could have been fixed by an individual."
- ref: Graham (2025)

**FD-13** | Consensus NOT required for commitment
- src: Graham transcript
- sections: 2c, 3b
- how: Apollo didn't need everyone to agree, just needed to ensure voices were heard.
- quote: "What they object to is when they don't feel like their voice has been heard."
- ref: Lencioni (2002)

### Team Development (Tuckman)

**TD-01** | Forming -- dependency, politeness, anxiety
- src: Tuckman Section 5
- sections: 2a, 2b
- how: Map Wk12 kickoff to Forming: polite role allocation, lots of questions, Apollo looked to for technical direction. Argue Forming was too brief.
- quote: "Trust will be limited and there will be a mix of excitement and anxiety."
- ref: Tuckman (1965)

**TD-02** | Storming -- rivals compete, politeness drops
- src: Tuckman Section 6
- sections: 2a, 2b, 2c, 4a
- how: Map Wk17 FSM conflict + Wk20 workload tensions. Cite architecture disagreement (monolithic vs modular).
- quote: "Levels of politeness drop as individuals start to realise the clock is ticking."
- ref: Tuckman (1965)

**TD-06** | Team regression -- undevelopment, moving right-to-left
- src: Tuckman Section 11
- sections: 2a, 2c
- how: Map flight cancellations to regression: team was Norming, weather cancelled flights, trust in timeline eroded. THE L4 move -- model is non-linear from lived experience.
- quote: "You can go from right to left. Your team could undevelop."
- ref: Tuckman (1965)

**TD-08** | Violently agreeing = artificial harmony = skipped Storming
- src: Tuckman Section 12
- sections: 2b, 2c, 4a
- how: Did the team violently agree? If yes, flag as weakness. If no, use as evidence of healthy Storming. True Norming = resolved conflict, not absent conflict.
- quote: "Be careful of that -- violently agreeing all the time."
- ref: Tuckman (1965)

**TD-11** | Worst-case timeline -- too little Forming, jump to Storming
- src: Tuckman Section 10
- sections: 2a, 2c
- how: "Our Wk12 kickoff may have been too brief, matching Tuckman's worst-case where too little Forming means no trust foundation."
- quote: "Too little time spent forming, no building of trust, just jumping straight into storming."
- ref: Tuckman (1965)

**TD-15** | Dominant personalities exerting unequal impact -- possibly you
- src: Tuckman Section 1 (Drawbacks)
- sections: 1a, 1b, 2b, 4a
- how: HIGH-VALUE L4 self-aware critique of own dominance. "As the primary software developer, I may have been the dominant personality Graham warns about."
- quote: "Possibly that dominant character might even be you."
- ref: Graham (2025)

**TD-24** | Investment paradox -- manage well now = manage less later
- src: Tuckman Section 2 (ideal team)
- sections: 2c, 3b, 4a
- how: THE takeaway for "what I'd do differently." Teams that invest in managing themselves spend less time managing. Front-load process discussions. Subsumes the irony that teams skipping management spend MORE time managing.
- quote: "Teams that invest in managing themselves well will have to spend less time managing."
- ref: Graham (2025)

**TD-25** | Limitation: original study was therapy groups
- src: Tuckman Section 17 (#1)
- sections: 2a, 2c
- how: L4 CRITICAL: "Tuckman's model was derived from therapy group literature, which he himself admitted cannot be considered truly representative."
- quote: "Tuckman admitted the literature cannot be considered truly representative."
- ref: Tuckman (1965, p.384)

**TD-26** | Limitation: linearity assumption -- real teams oscillate
- src: Tuckman Section 17 (#2)
- sections: 2a
- how: L4 CRITICAL: "Our experience was cyclical -- we regressed after flight cancellations. Supports Bonebright's (2010) critique."
- quote: "Real teams oscillate between stages rather than progressing linearly."
- ref: Tuckman (1965); Bonebright (2010)

**TD-32** | Storming is universal -- every team, no exceptions
- src: Tuckman Section 6
- sections: 2a, 2b
- how: Normalise conflict: "Graham states without exception, every team experiences Storming."
- quote: "Without exception, every new team I've worked within has experienced this stage."
- ref: Graham (2025)

**TD-36** | L4 Critical: evaluate model limitations + compare theory to experience
- src: Tuckman Section 15 (Hatton table)
- sections: 2a, 2c
- how: At least ONE L4 move per page. Always L3 minimum (Tuckman predicts X, we experienced Y) then push to L4 (evaluate model limitations). Combine dialogic comparison with critical evaluation.
- quote: "Tuckman's original study was conducted on therapy groups, not engineering teams."
- ref: Tuckman (1965, p.384); Hatton & Smith (1995); Bonebright (2010)

### Risk Management

**RM-01** | ISO 31000 Definition of Risk
- src: ISO 31000:2018; Graham Video 2
- sections: B.2
- how: Open risk section with formal definition. Frame every risk as "uncertainty affecting our objective."
- quote: "Risk is 'the effect of uncertainty on objectives.'"
- ref: ISO 31000:2018

**RM-02** | Risk as Choice (Risacare Etymology)
- src: Graham Video 2; Bernstein 1996
- sections: B.2
- how: Reframe risk as deliberate engineering choice. "We chose to fly at 35m (accepting lower detection confidence) rather than 20m."
- quote: "The word 'risk' derives from the early Italian risicare, meaning 'to dare.'"
- ref: Bernstein (1996)

**RM-03** | Six Risk Types
- src: Graham Video 2 slides s03-s04
- sections: B.3
- how: Categorise risk register entries. Show at least 3 types: Safety (crash/SSSI), Schedule (cancelled flights), Performance (AI detection rate).
- ref: Graham (2025)

**RM-04** | Hazard vs Risk Distinction
- src: Graham Video 2 slide s05; ISO 31000
- sections: B.4
- how: Be precise: "The hazard is the spinning propeller. The risk is the likelihood x consequence."
- quote: "Hazard: Something that has the potential to do harm."
- ref: ISO 31000:2018

**RM-05** | Risk Number = Likelihood x Consequence
- src: Graham Video 2 slides s08-s10
- sections: B.8, B.11
- how: Score every risk with f and c values. Weather-cancellation risk (f=4, c=3, fxc=12 INTOLERABLE) is the strongest example because it actually materialised.
- quote: "The resulting number guides you as to what to do."
- ref: Graham (2025)

**RM-06** | Mitigations: Reduce Likelihood, Reduce Consequence, or Both
- src: Graham Video 2 slides s05-s06
- sections: B.5
- how: Map each mitigation: Geofence = BOTH. RC kill switch = CONSEQUENCE only. Progressive test ladder = LIKELIHOOD. This analytical move gets L4.
- quote: "Different mitigations can improve the likelihood, consequence, or both."
- ref: Graham (2025)

**RM-07** | Risk Compensation (Helmet Makes You Careless)
- src: Graham Video 2 slide s06
- sections: B.6
- how: Highest-value concept for D7. Apply twice: (1) NCNN 4.5x faster could tempt higher flight speed. (2) Successful simulation created overconfidence. Both = L4 self-critique.
- quote: "The climber might think they are safer because they have a helmet and be less careful."
- ref: Graham (2025)

**RM-09** | HSE 5-Step Risk Assessment Cycle
- src: Graham Video 2 slide s07
- sections: B.7
- how: Map each step to concrete project action. CYCLIC nature is key -- show you went around the loop more than once.
- quote: "The process is cyclic."
- ref: HSE guidance

**RM-10** | Risk Assessment Pro Forma (9 Columns)
- src: Graham Video 2 slides s08-s10
- sections: B.8
- how: Use exactly the 9-column format. Shows direct application of taught framework.
- ref: Graham (2025)

**RM-14** | 5x5 Criticality Matrix
- src: Graham Video 2 slide s12
- sections: B.12
- how: Plot project risks. Weather risk at fxc=12 = Intolerable -- flights were halted. Framework working in practice.
- quote: "11-25: Intolerable. Activity must halt."
- ref: Graham (2025)

**RM-15** | ALARP (As Low As Reasonably Practicable)
- src: Graham Video 1; HSAWA Section 2
- sections: A.8
- how: Apply with NUMBERS. "Reducing from 35m to 20m would increase detection by ~15% but require 3.1x more passes." ALARP with quantitative reasoning = L4.
- quote: "Often reliant on the experience of company safety experts."
- ref: HSAWA (1974)

**RM-17** | Three Pillars: Moral, Economic, Legal
- src: Graham Video 1 slides s12-s13
- sections: A.6
- how: Connect ALL THREE to one decision (RC override guard). Moral = protect bystanders. Economic = ~2000 GBP equipment. Legal = ANO 2016 liability.
- quote: "You have a moral obligation to work safely. This obligation is above all others."
- ref: Graham (2025)

**RM-18** | 'Reasonably Practicable' Concept
- src: Graham Video 1; HSAWA 1974
- sections: A.4, A.8
- how: This is a LEGAL STANDARD requiring cost-benefit analysis. "Adding a secondary GPS receiver at ~500 GBP not reasonably practicable for uni prototype."
- ref: HSAWA (1974)

**RM-20** | Flixborough Disaster (1974)
- src: Graham Video 1 slides s07-s08
- sections: A.3
- how: Historical anchor for HSAWA. Then pivot: "Our progressive test ladder embodies the same principle: never skip safety steps."
- quote: "Flixborough accelerated the implementation of the Health and Safety at Work Act."
- ref: Graham (2025)

**RM-22** | Working Alone on Risk Assessment Is Suboptimal
- src: Graham Video 2 slide s10
- sections: B.8
- how: Justify team-based risk assessment AND acknowledge weakness. Risk register primarily authored by one member.
- quote: "A diversity of views are needed to capture more of the eventualities."
- ref: Graham (2025)

**RM-31** | Mitigations May Cause Unwanted Additional Risks
- src: Graham Video 2 slide s10
- sections: B.8
- how: Emergency RTL geofence introduces secondary risk: sudden mode change near ground. Chain of mitigation-upon-mitigation.
- quote: "Mitigations may cause unwanted additional risks."
- ref: Graham (2025)

**RM-36** | Iterative Risk Re-Assessment
- src: Graham Video 2 slide s07 (Step 5)
- sections: B.7, D.15
- how: Strongest L4 move. Show you went around the HSE cycle MORE THAN ONCE. After corrupt calibration_data.npz, re-scored AI detection from f=2 to f=4.
- ref: Graham (2025)

**RM-42** | Cascading/Compounding Risk (Beyond Simple f x c)
- src: D.17 Hatton L4 Moves
- sections: B.11, D.17
- how: CRITIQUE the framework. GPS-loss cascades into geofence AND navigation failure. Fault-tree analysis better captures dependencies. Meta: limits of the tool.
- ref: Graham (2025)

### Innovation Tools

**IT-01** | Divergent vs Convergent Thinking
- src: Innovation Tools Section 1
- sections: methodology, design approach
- how: Divergent phase (brainstorming patterns/backends) then convergent (down-selecting via benchmarks). Looped back when TFLite failed benchmarks.
- quote: "You may need to repeat the loop and generate new ideas."
- ref: Graham (2025)

**IT-04** | Controlled Convergence / Pugh Matrix
- src: Innovation Tools Section 6
- sections: design decisions, solution comparison
- how: Model selection as Pugh matrix. Datum = YOLOv8n baseline. sar_v2_1088 wins (+accuracy, =speed, -size).
- quote: "Just because it's the only idea left doesn't mean it's the one you have to use."
- ref: Graham (2025)

**IT-05** | MCDA (Multi-Criteria Decision Analysis)
- src: Innovation Tools Section 7
- sections: design decisions, final selection
- how: Weighted scoring. NCNN wins (4.15 vs TFLite 3.55). "Most popular tool with engineers."
- quote: "Very logical, very effective, but not over complicated."
- ref: Graham (2025)

**IT-06** | Requirements Analysis Before Solution Selection
- src: Innovation Tools Section 2
- sections: methodology, requirements
- how: R01-R12 defined BEFORE selecting solutions. "If you skip requirements, solution selection takes longer."
- ref: Graham (2025)

**IT-07** | Tools Support Thinking, Not Replace It
- src: Innovation Tools Section 6+9
- sections: critical reflection, Hatton L4
- how: KEY Hatton L4 move. Gap between tool output and final choice acceptable IF justified.
- quote: "These are only simple tools, there to support your thinking, not to replace it."
- ref: Graham (2025)

### Project Management

**PM-07** | WBS (100% Rule, Max 5 Levels)
- src: PM1 Slides 12-17
- sections: project management, planning
- how: Apollo's dashboard WBS, file structure in CLAUDE.md, flight testing steps.
- quote: "No more than 5 levels. Captures everything (the 100% rule)."
- ref: Graham (2025)

**PM-09** | Critical Path Method (CPM)
- src: PM1 Slides 25-29
- sections: scheduling, risk
- how: Forward/backward pass, float. Critical path: Pi setup -> camera -> Cube -> flight test. Weather extended it.
- quote: "Any delay to a CP task delays the entire project."
- ref: Graham (2025)

**PM-13** | Waterfall vs Agile vs Hybrid
- src: PM1 Slides 9-10
- sections: methodology
- how: HYBRID: waterfall for sequential flight testing, agile for sprint sessions + backlogs.
- quote: "Not one size fits all."
- ref: Graham (2025)

**PM-18** | "Group != Team"
- src: PM2 Slides 30-31
- sections: teamwork, reflection
- how: "Lone Genius" vs "Drifting alone" (TIME is the shark). Was team truly integrated or five individuals in parallel?
- quote: "A group of individuals is not a team."
- ref: Graham (2025)

### Cross-Cutting L4 Moves

**L4-01** | What We Should Have Done (Reflective Gap)
- sections: critical reflection
- how: "CV backend selection driven by benchmarks not structured MCDA. Formal comparison would have forced explicit trade-offs."

**L4-02** | Float as Strategic Resource
- sections: project management
- how: "Vision.py had significant float (independent module). Iteratively refined across 3 model versions without blocking main.py critical path."

**L4-03** | Hybrid Methodology Justification
- sections: methodology
- how: "Hardware = waterfall. Software = agile. Risk-driven hybrid necessary because 'not one size fits all.'"

---

## SHOULD (52 concepts)

### Five Dysfunctions

**FD-14** | Personal Histories Exercise (trust antidote)
- sections: 2c, 3b | how: Run at project start to build trust. | ref: Lencioni (2005)

**FD-15** | Team Effectiveness Exercise
- sections: 2c, 3b | how: Identify most/least effective contributions. Tough but builds trust + accountability. | ref: Lencioni (2005)

**FD-16** | Conflict Mining (conflict antidote)
- sections: 2c, 3b | how: Designate someone to arbitrate disputes. | ref: Lencioni (2005)

**FD-17** | Real-Time Permission (conflict antidote)
- sections: 2c, 3b | how: Give explicit permission to disagree. | ref: Lencioni (2005)

**FD-18** | Cascading Messaging (commitment antidote)
- sections: 2c, 3b | how: After decisions, cascade clearly to all. Prevents ambiguity. | ref: Lencioni (2005)

**FD-19** | Project Pre-Mortems
- sections: 2c, 3b | how: Imagine project has failed -- what went wrong? | ref: Lencioni (2005)

**FD-20** | Team Scoreboard / Dashboard (results antidote)
- sections: 2c, 3b | how: Public tracking of collective results. Apollo built dashboard but tracked individual tasks. | ref: Lencioni (2005)

**FD-21** | Public Declaration of Results
- sections: 2c, 3b | how: Publicly declare team goals. Harder to drift to individual agendas. | ref: Lencioni (2005)

**FD-22** | Results-Based Rewards (not individual)
- sections: 2c, 3b | how: Celebrate collective milestones, not commit counts. | ref: Lencioni (2005)

**FD-23** | The 38-Question Diagnostic Tool
- sections: 3a, 2b | how: Structured tool Apollo could have used mid-project. Brief self-assessment in D7. | ref: Lencioni (2002)

**FD-24** | Behavioural Profiling Tools (DISC, MBTI)
- sections: 2c, 3b | how: Understand team dynamics, build trust faster. | ref: Lencioni (2005)

**FD-25** | Shared Experiences as Trust Builder
- sections: 2c, 3b | how: Limited in-person time contributed to trust deficit. | ref: Lencioni (2005)

**FD-26** | Publication of Goals and Standards (accountability antidote)
- sections: 2c, 3b | how: Written commitments harder to renege on. Links to weasel metaphor. | ref: Lencioni (2005)

**FD-27** | Regular Progress Reviews
- sections: 2c, 3b | how: Genuine accountability reviews, not just status updates. | ref: Lencioni (2005)

**FD-28** | Worst Case Analysis (commitment antidote)
- sections: 2c, 3b | how: Reduces fear of commitment by bounding the downside. | ref: Lencioni (2005)

**FD-30** | Hatton Level 4 Critical Reflection Moves (pre-written)
- sections: 1a, 2a, 2b, 3a, 4a | how: Four pre-written L4 paragraphs ready for adaptation. | ref: Lencioni (2002); Hatton & Smith (1995)

### Team Development

**TD-03** | Norming -- sense of belonging, own culture
- sections: 2a, 2b | how: Evidence via handoff docs, Robin integration, Git workflow. | ref: Tuckman (1965)

**TD-04** | Performing -- fluidity, differences become useful
- sections: 2a, 3a | how: Be honest: did we reach Performing? Field day role fluidity? | ref: Tuckman (1965)

**TD-07** | Regression triggers -- 6 specific causes
- sections: 2a, 2c | how: (1) new member (Robin), (3) scope changes (flight cancellations), (5) external pressure. | ref: Tuckman (1965)

**TD-10** | Best-case timeline -- short F+S, long Performing (very rare)
- sections: 2a, 2c | how: Project plans implicitly built on best-case Tuckman. Acknowledge naive. | ref: Tuckman (1965)

**TD-13** | Extroverts speak-to-think vs introverts think-to-speak
- sections: 2b, 2c, 4a, 4b | how: Circulate agendas beforehand, allow async written input. | ref: Graham (2025)

**TD-14** | Groupthink / Echo Chamber
- sections: 2b, 2c | how: Did team have genuine intellectual diversity? | ref: Graham (2025)

**TD-16** | Diffusion of responsibility -- nobody reading the map
- sections: 2b, 3a, 4a | how: Integration testing assumed to be someone else's job. | ref: Graham (2025)

**TD-18** | Democratic weakness -- popular != good
- sections: 2b, 2c | how: Solutions converged by average approval not necessarily best. | ref: Graham (2025)

**TD-20** | Team time allocation -- 4 scenarios
- sections: 2b, 2c, 3b | how: Poor teams >50% on management. Ideal teams invest early. | ref: Graham (2025)

**TD-27** | Limitation: cultural bias -- 1960s American context
- sections: 2c | how: Multicultural team may exhibit different Storming patterns. | ref: Tuckman (1965)

**TD-37** | L4 Critical: synthesise Tuckman with Belbin
- sections: 2a, 2b | how: Cross-model synthesis. Role clashes explain Storming. | ref: Tuckman (1965); Belbin (2010)

**TD-40** | Best-case requires active management
- sections: 2c, 3b | how: "Unless naturally gifted or lucky, you must actively manage the team." | ref: Graham (2025)

### Risk Management

**RM-08** | Electricians Overconfident in Circuit Breakers
- sections: B.6 | how: Parallel analogy for risk compensation. | ref: Graham (2025)

**RM-11** | Frequency Scoring (1-5 Logarithmic Scale)
- sections: B.9 | how: Define project-specific scale. Logarithmic jumps. | ref: Graham (2025)

**RM-12** | Consequence Scoring (Network Rail Examples)
- sections: B.10 | how: Adapt Network Rail 5-level to SAR drone context. | ref: Network Rail

**RM-13** | Pre/Post Mitigation Scoring (Residual Risk)
- sections: B.8, B.13 | how: Show BEFORE/AFTER for 2+ risks. Includes existing vs additional mitigations split. | ref: Graham (2025)

**RM-19** | Duty of Care (Priestley v Fowler 1835)
- sections: A.2.2 | how: Historical mention shows legal knowledge depth. | ref: Graham (2025)

**RM-21** | Corporate Manslaughter Act 2007
- sections: A.7 | how: Systemic failures, not just individual errors. | ref: CMA (2007)

**RM-23** | No One Has to Be Harmed for an Offence
- sections: A.4 | how: Creating risk of harm is itself an offence. Justifies geofence. | ref: HSAWA (1974)

**RM-24** | Risk Assessment Is Continuous and Unconscious
- sections: B.2 | how: Bridge from theory to practice. Formalising makes implicit process auditable. | ref: Graham (2025)

**RM-27** | HSAWA Six Employer Duties
- sections: A.4 | how: Map 3+ duties to project. | ref: HSAWA (1974)

**RM-28** | Mental Health as Employer Duty
- sections: A.4 | how: Cancelled flights + fixed deadline = stress. Simulation fallback reduced anxiety. | ref: Graham (2025)

**RM-32** | Non-Experts Add Value to Risk Assessment
- sections: B.8 | how: Non-expert question prompted GPS-fix pre-condition. | ref: Graham (2025)

**RM-34** | 'Don't Walk By' -- Report Hazards
- sections: A.10 | how: Any team member could halt at any time on flight day. | ref: Graham (2025)

**RM-35** | Professional Approach Starts Now
- sections: A.10 | how: Full RM on student project where none required = professional standard. | ref: Graham (2025)

**RM-38** | Risk Management as Art, Not Just Science
- sections: B.2 | how: Scores involve judgment. Limited flight experience is itself a risk factor. | ref: Graham (2025)

**RM-40** | Strong Safety Culture Drives Continuous Improvement
- sections: A.9 | how: Progressive test ladder: even after successful simulation, didn't skip to autonomous. | ref: Graham (2025)

**RM-45** | Auditors Check Risk Assessments
- sections: B.7 | how: Documentation rigour justified. | ref: Graham (2025)

### Innovation / PM

**IT-02** | Simple Pairwise Comparison
- sections: design decisions | how: Rank flight test priorities. Implicit in test ladder. | ref: Graham (2025)

**IT-03** | Numerical Pairwise Comparison (9/3/1)
- sections: criteria weighting | how: Produces % weightings for MCDA. | ref: Graham (2025)

**IT-08** | Survivor Bias Warning
- sections: critical reflection | how: Was lawnmower truly optimal, or just the survivor? | ref: Graham (2025)

**IT-09** | Benefits of Structured Tools
- sections: teamwork | how: Faster agreement, neutralises loud voices, stakeholder explanation. | ref: Graham (2025)

**IT-10** | Risks of Structured Tools (GIGO, Hiding Behind Tool)
- sections: Hatton L4 | how: GIGO + hiding behind tool + too systematic kills creativity. | ref: Graham (2025)

**PM-08** | Network Diagrams (AOA, AON/PDM)
- sections: scheduling | how: Flight test dependency chain IS a network diagram. | ref: Graham (2025)

**PM-10** | Gantt Chart -- Five Components
- sections: scheduling | how: Dependencies, CP, float, project length, milestones. | ref: Graham (2025)

**PM-11** | Resource Levelling
- sections: resource management | how: Single Pi = bottleneck. Training subcontracted to Colab GPU. | ref: Graham (2025)

**PM-12** | Rolling Wave Planning
- sections: planning approach | how: Near-term detailed, far-term abstract. "I only know immediate tasks? That's rolling wave." | ref: Graham (2025)

**PM-17** | "Museum of Mediocrity" Anti-Pattern
- sections: quality | how: Living documentation vs static plan obsolete by Week 3. | ref: Graham (2025)

**PM-21** | 7 Planning Challenges
- sections: challenges | how: 11-state machine, 41 scripts, 3 platforms, non-continuous working. | ref: Graham (2025)

**PM-23** | Precedence Relationships (FS, SS, FF, SF)
- sections: scheduling | how: FS (simulation before Pi), SS (hardware + software parallel). | ref: Graham (2025)

**PM-25** | Non-Continuous Working
- sections: realism | how: Man-days != elapsed days. Weather delay node. | ref: Graham (2025)

**PM-26** | Intra-Team Dependencies as Interface Contracts
- sections: architecture | how: vision.py 4-tuple API stable across 3 model versions. | ref: Graham (2025)

**L4-04** | Dynamic Critical Path
- sections: PM + risk | how: CP shifted from software to hardware after weather cancellation. | ref: Graham (2025)

**L4-05** | Tuckman + Rolling Wave Synthesis
- sections: teamwork + planning | how: Team maturity enables planning detail. Rolling wave responds to Tuckman stage. | ref: Tuckman (1965); Graham (2025)

---

## COULD (38 concepts)

### Five Dysfunctions

**FD-31** | Hiding mistakes (trust symptom) | sections: 2b | ref: Lencioni (2002)
**FD-32** | Slow to apologise (trust symptom) | sections: 2b | ref: Lencioni (2002)
**FD-33** | Boring meetings / safe topics (conflict symptom) | sections: 2b | ref: Lencioni (2002)
**FD-34** | Revisiting same discussions (commitment symptom) | sections: 2b, 2c | ref: Lencioni (2002)
**FD-35** | Opinions not solicited (conflict symptom) | sections: 2b | ref: Lencioni (2002)
**FD-36** | Never sharing personal life (trust symptom) | sections: 2b | ref: Graham (2025)
**FD-37** | Academic departments as Level 5 example | sections: 3a | ref: Graham (2025)
**FD-38** | Dysfunctions not virtues (model design choice) | sections: 3a | ref: Graham (2025)
**FD-39** | Exercises may feel awkward (meta-observation) | sections: 3b | ref: Graham (2025)
**FD-40** | Ice Climber visual (trust metaphor) | sections: 3a | ref: Graham (2025)
**FD-41** | Resentment in both directions (accountability symptom) | sections: 2b | ref: Lencioni (2002)
**FD-42** | Human behaviours not resources (closing insight) | sections: 4a, 3b | ref: Graham (2025)

### Team Development

**TD-05** | Transforming / Adjourning -- knowledge capture | sections: 1c, 3b | ref: Tuckman & Jensen (1977)
**TD-12** | Probable timeline -- compressed Performing | sections: 2a | ref: Tuckman (1965)
**TD-17** | Collective courage -- teams attempt what individuals would not | sections: 1b, 3a | ref: Graham (2025)
**TD-19** | Underground conflict from democratic peacekeeping | sections: 2b, 2c | ref: Tuckman (1965)
**TD-22** | Worker 85% technical / manager 50-50 split | sections: 1a, 1c | ref: Graham (2025)
**TD-23** | Engineering-to-management transition pain | sections: 1c | ref: Graham (2025)
**TD-28** | Limitation: no timeframes given | sections: 2a | ref: Tuckman (1965)
**TD-29** | Limitation: pre-assigned vs self-selected teams | sections: 2a, 2c | ref: Tuckman (1965)
**TD-31** | Fractal nature -- Tuckman repeats at division level | sections: 2a, 3b | ref: Graham (2025)
**TD-33** | Good teams > sum of parts | sections: 3a | ref: Graham (2025)
**TD-34** | Team interaction creates accidental discoveries | sections: 2b, 3a | ref: Graham (2025)
**TD-38** | Forming is deceptively pleasant | sections: 2a | ref: Graham (2025)
**TD-39** | Tuckman's two parallel dimensions (interpersonal + task) | sections: 2a | ref: Tuckman (1965)
**TD-41** | 5 indicators of reaching Norming | sections: 2a | ref: Graham (2025)
**TD-42** | Forming: unclear roles (chaotic) vs Performing: flexible roles (intentional) | sections: 2a | ref: Tuckman (1965)
**TD-43** | Senior manager mindset: team's work is your work | sections: 1a, 1c | ref: Graham (2025)

### Innovation / PM

**PM-05** | Combining Pairwise + MCDA Pipeline | sections: methodology | ref: Graham (2025)
**PM-06** | Democratic Scoring -- should each voice carry equal weight? | sections: reflection | ref: Graham (2025)
**PM-14** | Project Lifecycle Models (4/5/6/7/8 Phase) | sections: lifecycle | ref: Graham (2025)
**PM-19** | Delaying Planning = Skeleton at Bus Stop | sections: planning | ref: Graham (2025)
**PM-20** | Three Equivalent Representations (Table/Network/Gantt) | sections: PM | ref: Graham (2025)
**PM-22** | 10-Level Competence Ladder | sections: self-assessment | ref: Graham (2025)

---

## SKIP (6 + 11 RM-LOW)

**FD-43** | TEDx Talk: Are You an Ideal Team Player? | ref: Lencioni (2016)
**FD-44** | Decision Tech fable context | ref: Lencioni (2002)
**TD-30** | Limitation: remote/hybrid work not covered | ref: Tuckman (1965)
**TD-44** | Will of the people -- provocative democratic critique | ref: Graham (2025)
**PM-15** | Project / Programme / Portfolio Hierarchy | ref: Graham (2025)
**PM-24** | AON/PDM Node Anatomy -- 6-Field Box | ref: Graham (2025)

### Risk Management LOW

**RM-16** | VPF (Value of Prevented Fatality) | ref: DfT (2016)
**RM-25** | Secondary Legislation / Regulations | ref: Graham (2025)
**RM-26** | HSE Inspectors Greater Powers Than Police | ref: Graham (2025)
**RM-29** | F1 Pit-Stop Worked Example | ref: Graham (2025)
**RM-30** | FMEA Variants | ref: Graham (2025)
**RM-33** | Improvement Since 1974 (651 to 150) | ref: Graham (2025)
**RM-37** | Peter Bernstein / Against the Gods | ref: Bernstein (1996)
**RM-39** | Risk Management Unlocks Opportunity | ref: Graham (2025)
**RM-41** | White Phosphorus / Phossy Jaw | ref: Graham (2025)
**RM-43** | Supplier Safety Records | ref: Graham (2025)
**RM-44** | Factory Act 1802 | ref: Graham (2025)

---

## JavaScript Array for planner.html

The following array consolidates 159 concepts into **62 actionable planner entries**. Sub-concepts grouped under parent entries. Replace `const PP = [...]` in planner.html with this.

```javascript
const PP = [
  // ===================================================================
  // MUST -- Core frameworks, direct project evidence, D7 body text
  // ===================================================================

  // --- Five Dysfunctions (Lencioni) ---
  {id:'pp01', pri:'must', name:'Lencioni Five Dysfunctions (pyramid model)', src:'Lencioni 2002; Graham 2025', sections:'3a,2a', how:'Sequential bottom-up framework. Trust>Conflict>Commitment>Accountability>Results. Map team journey through all 5 levels. Chain metaphor: break one link = whole chain fails.', quote:'Each level builds on the one below it. Fix from the bottom up.', ref:'Lencioni (2002); Graham (2025)'},
  {id:'pp02', pri:'must', name:'Absence of Trust -- Invulnerability + Ring-fencing', src:'Lencioni L1', sections:'1a,2a,3a,2b', how:'1411-line monolith = architectural ring-fence. 820 solo commits = invulnerability. Name behaviour explicitly as Lencioni "ring-fencing." Refusing to delegate = refusing to be vulnerable.', quote:'Hiding our weaknesses prevents the growth of trust.', ref:'Lencioni (2002); Graham (2025)'},
  {id:'pp03', pri:'must', name:'Fear of Conflict -- Artificial Harmony + Back Channels', src:'Lencioni L2', sections:'2b,3a', how:'Team avoided hard conversations (Wk20 workload). Important comms via side-channels. Robin FSM pushback (Wk17) = rare real conflict. Meetings touched safe topics only.', quote:'This apparent harmony is really an artificial harmony.', ref:'Lencioni (2002)'},
  {id:'pp04', pri:'must', name:'Lack of Commitment -- Ambiguity + Weasel Metaphor', src:'Lencioni L3', sections:'2a,2b,2c,3a', how:'No written objectives until late. FSM revisited not committed. Some avoided action logs (weasel). Apollo also avoided committing to collaboration -- solo commits = hiding behind ambiguity.', quote:'Usually more slippery than a weasel... once written down, harder to renege.', ref:'Lencioni (2002); Graham (2025)'},
  {id:'pp05', pri:'must', name:'Avoidance of Accountability -- Leader Burden + Peer Pressure', src:'Lencioni L4', sections:'2b,4b,2c,3a', how:'Accountability collapsed onto Apollo. No peer challenge. Peer pressure (with trust) beats bureaucracy. Leader became sole source of discipline -- exactly Lencioni L4 failure.', quote:'With little accountability, the burden falls back on the team leader.', ref:'Lencioni (2002); Graham (2025)'},
  {id:'pp06', pri:'must', name:'Inattention to Results -- Status & Ego over Collective', src:'Lencioni L5', sections:'2b,3b,3a', how:'Some focused on own marks/report. Apollo optimised his output not team capability. Why teams exist: complex problems need teams not individuals.', quote:'Individual success and ego become more relevant than group success.', ref:'Lencioni (2002); Graham (2025)'},
  {id:'pp07', pri:'must', name:'Consensus NOT required for commitment', src:'Graham 2025', sections:'2c,3b', how:'Key "what to change" insight. Didn\'t need everyone to agree, just ensure voices heard. Robin FSM pushback could have been handled by hearing then committing.', quote:'What they object to is when their voice has not been heard.', ref:'Lencioni (2002)'},

  // --- Team Development (Tuckman) ---
  {id:'pp08', pri:'must', name:'Tuckman Forming + Storming (mapped to project)', src:'Tuckman 1965', sections:'2a,2b,2c,4a', how:'Forming: Wk12 polite kickoff, dependency on Apollo, too brief. Storming: Wk17 FSM conflict, Wk20 workload. Storming is universal (Graham: every team, no exceptions). Normalise conflict as necessary stage.', quote:'Levels of politeness drop as the clock is ticking.', ref:'Tuckman (1965); Graham (2025)'},
  {id:'pp09', pri:'must', name:'Tuckman Regression -- Teams Can "Undevelop"', src:'Tuckman 1965', sections:'2a,2c', how:'Flight cancellations caused regression from Norming. Triggers: new member (Robin), scope change (weather), external pressure. THE L4 move: model is non-linear from lived experience.', quote:'You can go from right to left. Your team could undevelop.', ref:'Tuckman (1965)'},
  {id:'pp10', pri:'must', name:'Worst-Case Timeline -- Too Little Forming', src:'Tuckman 1965', sections:'2a,2c', how:'Brief Wk12 kickoff = no trust foundation leading to extended Storming. Best-case (short Storming) is "very very rare." Budget explicitly for Storming in Gantt.', quote:'Too little time forming, no trust, jumping straight into storming.', ref:'Tuckman (1965)'},
  {id:'pp11', pri:'must', name:'Violently Agreeing = Artificial Harmony', src:'Tuckman 1965', sections:'2b,2c,4a', how:'Did team violently agree? If yes = weakness (absent diversity). True Norming = resolved conflict, not absent conflict.', quote:'Be careful of violently agreeing all the time.', ref:'Tuckman (1965)'},
  {id:'pp12', pri:'must', name:'Dominant Personalities -- Possibly You', src:'Graham 2025', sections:'1a,1b,2b,4a', how:'HIGHEST L4 self-aware critique. "As primary software developer, I may have been the dominant personality Graham warns about -- exerting unequal impact."', quote:'Possibly that dominant character might even be you.', ref:'Graham (2025)'},
  {id:'pp13', pri:'must', name:'Investment Paradox -- Manage Well Now = Manage Less Later', src:'Graham 2025', sections:'2c,3b,4a', how:'THE takeaway for "what I\'d do differently." Front-load team processes. Teams that skip management spend MORE time managing. Irony: resisting processes created more confusion.', quote:'Teams that invest in managing themselves will spend less time managing.', ref:'Graham (2025)'},
  {id:'pp14', pri:'must', name:'Tuckman Limitations (L4 Critical Moves)', src:'Tuckman 1965', sections:'2a,2c', how:'(1) Therapy groups not engineering teams (p.384). (2) Linearity assumption -- real teams oscillate (Bonebright 2010). (3) 1960s American cultural bias. Always compare theory to experience then evaluate limits.', quote:'Tuckman admitted the literature cannot be considered truly representative.', ref:'Tuckman (1965, p.384); Bonebright (2010); Hatton & Smith (1995)'},

  // --- Risk Management ---
  {id:'pp15', pri:'must', name:'ISO 31000 Risk Definition + Risk as Choice', src:'ISO 31000; Bernstein 1996', sections:'B.2', how:'Open with formal definition. Risk = effect of uncertainty on objectives. Risicare = "to dare." Reframe as deliberate engineering choice, not passive fate.', quote:'Risk derives from risicare, meaning "to dare."', ref:'ISO 31000:2018; Bernstein (1996)'},
  {id:'pp16', pri:'must', name:'Risk Number = F x C + 5x5 Criticality Matrix', src:'Graham Video 2', sections:'B.8,B.11,B.12', how:'Score every risk. Weather: f=4,c=3,fxc=12=INTOLERABLE -- actually materialised (flights halted). 1-5=Negligible, 6-10=Tolerable, 11-25=Intolerable. Map on matrix.', quote:'The resulting number guides you as to what to do.', ref:'Graham (2025)'},
  {id:'pp17', pri:'must', name:'Risk Compensation (Helmet Effect)', src:'Graham Video 2', sections:'B.6', how:'HIGHEST-VALUE self-reflection. (1) NCNN 4.5x faster could tempt higher speed. (2) Successful simulation created overconfidence reducing urgency of hardware testing. Electrician analogy.', quote:'The climber might be less careful because they have a helmet.', ref:'Graham (2025)'},
  {id:'pp18', pri:'must', name:'ALARP with Quantitative Reasoning', src:'HSAWA 1974', sections:'A.8', how:'Apply with NUMBERS. "35m to 20m: +15% detection but 3.1x more passes." Using TFLite (proven, 206ms) vs NCNN (untested). Legal standard, not common sense.', quote:'Often reliant on experience of company safety experts.', ref:'HSAWA (1974)'},
  {id:'pp19', pri:'must', name:'Three Pillars: Moral, Economic, Legal', src:'Graham Video 1', sections:'A.6', how:'All three on one decision (RC override guard). Moral=bystanders. Economic=GBP2000 equipment. Legal=ANO 2016. L4 synthesis.', quote:'Moral obligation is above all others.', ref:'Graham (2025)'},
  {id:'pp20', pri:'must', name:'HSE 5-Step Cycle (Iterative Re-Assessment)', src:'Graham Video 2', sections:'B.7', how:'Map each step to project. CYCLIC: went around loop >1 time. After corrupt calibration_data.npz, re-scored AI detection risk f=2 to f=4. Hallmark of mature RM.', quote:'The process is cyclic.', ref:'HSE guidance; Graham (2025)'},
  {id:'pp21', pri:'must', name:'Hazard vs Risk + Six Risk Types + Pro Forma', src:'Graham Video 2; ISO 31000', sections:'B.3,B.4,B.8', how:'Hazard=spinning propeller, risk=LxC of laceration. 3+ types: Safety, Schedule, Performance. 9-column pro forma format.', quote:'Hazard: something with potential to do harm.', ref:'ISO 31000:2018; Graham (2025)'},
  {id:'pp22', pri:'must', name:'Mitigations: L, C, or Both + Secondary Risks', src:'Graham Video 2', sections:'B.5,B.8', how:'Geofence=BOTH. Kill switch=C only. Test ladder=L only. Warning: mitigations cause secondary risks (emergency RTL near ground). Chain of mitigation-upon-mitigation.', quote:'Mitigations may cause unwanted additional risks.', ref:'Graham (2025)'},
  {id:'pp23', pri:'must', name:'Solo Risk Assessment Weakness + Non-Expert Value', src:'Graham Video 2', sections:'B.8', how:'Register authored by one person = blind spots. Non-expert question prompted GPS-fix pre-condition. Diversity of views needed.', quote:'Working alone on RA is suboptimal.', ref:'Graham (2025)'},
  {id:'pp24', pri:'must', name:'Cascading Risk (Beyond f x c) -- L4 Framework Critique', src:'Hatton L4', sections:'B.11', how:'GPS-loss cascades into geofence AND navigation failure. Fault-tree analysis better captures dependencies. Meta: limits of the tool you are using.', quote:'', ref:'Graham (2025)'},
  {id:'pp25', pri:'must', name:'Flixborough + "Reasonably Practicable" + HSAWA', src:'Graham Video 1; HSAWA', sections:'A.3,A.4,A.8', how:'28 deaths accelerated HSAWA. Legal standard: cost of mitigation vs degree of risk. "Secondary GPS at GBP500 not reasonably practicable for uni prototype."', quote:'Flixborough accelerated HSAWA implementation.', ref:'HSAWA (1974); Graham (2025)'},

  // --- Innovation & PM ---
  {id:'pp27', pri:'must', name:'Divergent then Convergent Thinking (Loop Back)', src:'Graham Innovation 2025', sections:'methodology', how:'Divergent: brainstormed patterns + backends. Convergent: down-selected via benchmarks. Looped back when TFLite failed. Show two-phase process.', quote:'You may need to repeat the loop and generate new ideas.', ref:'Graham (2025)'},
  {id:'pp28', pri:'must', name:'Pugh Matrix + MCDA (Down-Selection)', src:'Graham Innovation 2025', sections:'design decisions', how:'Pugh: datum=YOLOv8n, sar_v2_1088 wins (+acc,=speed,-size). MCDA: weighted scoring, NCNN 4.15 vs TFLite 3.55. Most popular tool with engineers.', quote:'Very logical, very effective, not over complicated.', ref:'Graham (2025)'},
  {id:'pp29', pri:'must', name:'Requirements Before Solutions', src:'Graham Innovation 2025', sections:'methodology', how:'R01-R12 defined BEFORE selecting solutions. "Skip requirements = solution selection takes longer."', quote:'Team finds it harder to agree on what good looks like.', ref:'Graham (2025)'},
  {id:'pp30', pri:'must', name:'Tools Support Thinking, Not Replace It (L4)', src:'Graham Innovation 2025', sections:'critical reflection', how:'KEY Hatton L4. Gap between tool output and final choice is OK if justified. "CV selection driven by benchmarks not formal MCDA -- outcome sound but would have forced explicit trade-offs."', quote:'These tools support your thinking, not replace it.', ref:'Graham (2025)'},
  {id:'pp31', pri:'must', name:'WBS (100% Rule) + Critical Path Method', src:'Graham PM1 2025', sections:'PM,scheduling', how:'WBS: 5 levels max, captures everything. CPM: forward/backward pass, float. Critical path: Pi to camera to Cube to flight. Weather extended it.', quote:'No more than 5 levels. Captures everything.', ref:'Graham (2025)'},
  {id:'pp32', pri:'must', name:'Waterfall vs Agile vs Hybrid', src:'Graham PM1 2025', sections:'methodology', how:'HYBRID: waterfall for sequential flight testing (safety), agile for sprints + backlogs. brain-dump.md=product backlog. "Not one size fits all."', quote:'Not one size fits all.', ref:'Graham (2025)'},
  {id:'pp33', pri:'must', name:'"Group is not a Team"', src:'Graham PM2 2025', sections:'teamwork', how:'"Lone Genius" (castle) vs "Drifting alone" (raft, paddling different directions, TIME is the shark). Was team truly integrated or 5 individuals in parallel?', quote:'A group of individuals is not a team.', ref:'Graham (2025)'},
  {id:'pp34', pri:'must', name:'L4: Reflective Gap + Float as Strategic Resource', src:'Synthesis', sections:'critical reflection,PM', how:'CV selection driven by benchmarks not structured MCDA. Float used strategically: vision.py independent, iteratively refined across 3 model versions without blocking CP.', quote:'', ref:'Graham (2025)'},
  {id:'pp35', pri:'must', name:'L4: Risk-Driven Hybrid Methodology', src:'Synthesis', sections:'methodology', how:'Hardware = waterfall (can\'t skip serial verification). Software = agile sprints. Risk-driven hybrid for single project with dual methodology.', quote:'', ref:'Graham (2025)'},

  // ===================================================================
  // SHOULD -- Antidotes, tools, supporting concepts
  // ===================================================================

  {id:'pp36', pri:'should', name:'Lencioni Antidotes: Trust (Histories, Profiling, Shared Experience)', src:'Lencioni 2005', sections:'2c,3b', how:'Personal histories at start. Team effectiveness exercise. DISC/MBTI profiling. Shared experiences. Limited in-person time = trust deficit.', quote:'Simple sharing helps recognise the human in others.', ref:'Lencioni (2005)'},
  {id:'pp37', pri:'should', name:'Lencioni Antidotes: Conflict (Mining, Real-Time Permission)', src:'Lencioni 2005', sections:'2c,3b', how:'Conflict miner to arbitrate. Real-time permission to disagree. "I want your honest opinion even if it disagrees."', quote:'Someone to arbitrate and help share points of view.', ref:'Lencioni (2005)'},
  {id:'pp38', pri:'should', name:'Lencioni Antidotes: Commitment (Messaging, Pre-Mortems, Worst Case)', src:'Lencioni 2005', sections:'2c,3b', how:'Cascade decisions consistently. Pre-mortems: imagine failure. Worst case analysis bounds downside.', quote:'Cascading messaging prevents ambiguity.', ref:'Lencioni (2005)'},
  {id:'pp39', pri:'should', name:'Lencioni Antidotes: Accountability + Results (Scoreboard, Goals, Reviews)', src:'Lencioni 2005', sections:'2c,3b', how:'Published goals (anti-weasel). Regular progress reviews. Team scoreboard. Results-based rewards (not individual).', quote:'Written commitments are harder to renege on.', ref:'Lencioni (2005)'},
  {id:'pp40', pri:'should', name:'38-Question Diagnostic + Hatton L4 Pre-Written Moves', src:'Lencioni 2002; Hatton 1995', sections:'3a,2b,1a,2a,4a', how:'Diagnostic as mid-project tool. 4 pre-written L4 paragraphs. "My 1411-line main.py was absence of trust made architectural."', quote:'Rate each statement 1-5. Takes under 15 minutes.', ref:'Lencioni (2002); Hatton & Smith (1995)'},
  {id:'pp41', pri:'should', name:'Tuckman Norming + Performing (Evidence Checklist)', src:'Tuckman 1965', sections:'2a,3a', how:'Norming: handoff docs, Git workflow, constructive criticism. Performing: field day fluidity. 5 Norming indicators. Be honest if Performing was reached.', quote:'Differences between team members become useful.', ref:'Tuckman (1965)'},
  {id:'pp42', pri:'should', name:'Regression Triggers + Best-Case Timeline', src:'Tuckman 1965', sections:'2a,2c', how:'6 triggers: new member, scope change, external pressure. Best-case (short Storming) is naive assumption. Budget Storming time.', quote:'New members disrupt established norms.', ref:'Tuckman (1965)'},
  {id:'pp43', pri:'should', name:'Extroverts vs Introverts + Groupthink Risk', src:'Graham 2025', sections:'2b,2c,4a', how:'Speak-to-think vs think-to-speak. Circulate agendas. Echo chamber from clones. Evaluate intellectual diversity.', quote:'These differences require different management.', ref:'Graham (2025)'},
  {id:'pp44', pri:'should', name:'Diffusion of Responsibility (Hiking Analogy)', src:'Graham 2025', sections:'2b,3a,4a', how:'Nobody reading the map. Integration testing assumed to be someone else\'s job.', quote:'No one realised no one was reading the map either.', ref:'Graham (2025)'},
  {id:'pp45', pri:'should', name:'Democratic Weakness + Active Management Required', src:'Graham 2025', sections:'2b,2c,3b', how:'Popular != good. "Unless gifted or lucky, actively manage the team." Schedule Forming activities.', quote:'Just because it\'s popular doesn\'t make it good.', ref:'Graham (2025)'},
  {id:'pp46', pri:'should', name:'Tuckman + Belbin Synthesis (L4 Cross-Model)', src:'Tuckman; Belbin 2010', sections:'2a,2b', how:'Role clashes explain Storming. Two Shapers = intense Storming. Performing requires role complementarity.', quote:'Belbin explains why Storming occurs.', ref:'Tuckman (1965); Belbin (2010)'},
  {id:'pp47', pri:'should', name:'Team Time Allocation (4 Scenarios)', src:'Graham 2025', sections:'2b,2c,3b', how:'Poor teams >50% on management. During Storming = us. Ideal: invested management reduces overhead.', quote:'Teams that don\'t bother thinking about how they work spend even more time managing.', ref:'Graham (2025)'},
  {id:'pp48', pri:'should', name:'Pre/Post Mitigation Scoring + Residual Risk', src:'Graham Video 2', sections:'B.8,B.13', how:'Show BEFORE/AFTER for 2+ risks. SSSI: pre f=3,c=4=12 to post f=1,c=4=4. Split existing vs additional mitigations.', quote:'Residual risk remains even after mitigations.', ref:'Graham (2025)'},
  {id:'pp49', pri:'should', name:'Legal Depth (Duty of Care, CMA, HSAWA Duties, Mental Health)', src:'Graham Video 1', sections:'A.2-A.7', how:'Priestley v Fowler 1835. CMA 2007 (systemic failures). HSAWA 6 duties mapped to project. "No one harmed = still an offence." Mental health duty.', quote:'Creating risk of harm is itself an offence.', ref:'HSAWA (1974); CMA (2007)'},
  {id:'pp50', pri:'should', name:'Safety Culture + Professional Approach Starts Now', src:'Graham Video 1', sections:'A.9,A.10', how:'Progressive test ladder = continuous improvement. "Don\'t walk by." Full RM on student project = professional standard. Auditors check RAs first.', quote:'Your professional approach to working safely starts now.', ref:'Graham (2025)'},
  {id:'pp51', pri:'should', name:'Risk as Art + Frequency/Consequence Scales', src:'Graham Video 2', sections:'B.2,B.9,B.10', how:'Scores involve judgment. Logarithmic frequency scale. Network Rail consequence 5-level. Non-experts ask great questions. Continuous unconscious daily activity made explicit.', quote:'Non-experts often ask great questions.', ref:'Graham (2025); Network Rail'},
  {id:'pp52', pri:'should', name:'Pairwise Comparison (Simple + Numerical) + Survivor Bias', src:'Graham Innovation 2025', sections:'design decisions', how:'Rank criteria. Simple = ordinal. Numerical 9/3/1 = % weightings for MCDA. Was lawnmower truly optimal or just the survivor?', quote:'Half for A as it was more important twice and equal once.', ref:'Graham (2025)'},
  {id:'pp53', pri:'should', name:'Benefits + Risks of Structured Tools', src:'Graham Innovation 2025', sections:'teamwork,L4', how:'Benefits: faster agreement, neutralises loud voices. Risks: GIGO, hiding behind tool, too systematic kills creativity.', quote:'Using an analytical tool takes focus away from personalities.', ref:'Graham (2025)'},
  {id:'pp54', pri:'should', name:'Network Diagrams + Gantt (5 Components)', src:'Graham PM1-2 2025', sections:'scheduling', how:'AOA/AON. Flight test chain IS a network. Gantt: deps, CP, float, length, milestones. Three equivalent representations.', quote:'Activities as arrows, events as circles.', ref:'Graham (2025)'},
  {id:'pp55', pri:'should', name:'Resource Levelling + Rolling Wave Planning', src:'Graham PM2 2025', sections:'resource mgmt,planning', how:'Pi=bottleneck. Training on Colab (using float). Near=detailed, far=abstract. "Only know immediate tasks? That\'s rolling wave."', quote:'Resource levelling achieves same duration with zero additional staff.', ref:'Graham (2025)'},
  {id:'pp56', pri:'should', name:'PM Challenges + Precedence + Non-Continuous + Interface Contracts', src:'Graham Specialist 2025', sections:'scheduling,realism,architecture', how:'7 challenges. FS/SS/FF/SF. Man-days != elapsed. Weather delay node. vision.py 4-tuple API stable across 3 versions.', quote:'Man-days != days taken.', ref:'Graham (2025)'},
  {id:'pp57', pri:'should', name:'L4: Dynamic CP + Tuckman x Rolling Wave Synthesis', src:'Synthesis', sections:'PM,teamwork', how:'CP shifted software to hardware after weather. Team maturity enables planning detail. Rolling wave responds to Tuckman stage, not just info uncertainty.', quote:'', ref:'Graham (2025); Tuckman (1965)'},
  {id:'pp58', pri:'should', name:'"Museum of Mediocrity" Anti-Pattern', src:'Graham PM2 2025', sections:'quality', how:'Living docs (CLAUDE.md, session logs) vs static plan obsolete by Week 3.', quote:'', ref:'Graham (2025)'},

  // ===================================================================
  // COULD -- Polish, metaphors, depth
  // ===================================================================

  {id:'pp59', pri:'could', name:'Lencioni Symptoms Checklist', src:'Lencioni 2002', sections:'2b', how:'Hiding mistakes, slow to apologise, boring meetings, revisiting discussions, opinions not solicited, never sharing personal life, resentment both directions.', quote:'Various symptom quotes from Slide 10.', ref:'Lencioni (2002)'},
  {id:'pp60', pri:'could', name:'Lencioni Depth (academic depts, negative framing, exercises awkward, ice climber, human behaviours)', src:'Lencioni 2002; Graham 2025', sections:'3a,3b,4a', how:'Academics = L5 example. Dysfunctions not virtues by design. Exercises feel awkward. Ice climber trust metaphor. "Not lack of resources but basic human behaviours."', quote:'It\'s not lack of resources but basic human behaviours.', ref:'Lencioni (2002); Graham (2025)'},
  {id:'pp61', pri:'could', name:'Tuckman Depth (transforming, timeline, courage, two dimensions, fractal, roles, team>sum)', src:'Tuckman 1965; Graham 2025', sections:'2a,3a,1c,3b', how:'Adjourning = knowledge capture. Probable = compressed Performing. Collective courage. Two parallel dimensions. Fractal teams. Unclear (Forming) vs flexible (Performing) roles. Senior mindset: team\'s work IS your work.', quote:'Good teams > sum of their parts.', ref:'Tuckman (1965); Graham (2025)'},
  {id:'pp62', pri:'could', name:'PM Depth (lifecycle models, expert weighting, competence ladder, don\'t delay, tool pipeline)', src:'Graham PM 2025', sections:'PM,methodology,self-assessment', how:'4/5/6/8 phase lifecycle. Should each voice carry equal weight? 10-level ladder (honest self-assess). Start planning now. Pairwise+MCDA pipeline.', quote:'I\'ll start when I have all the info = fatal mistake.', ref:'Graham (2025)'},
];
```

---

_End of PP_EXPANDED_ALL.md_
