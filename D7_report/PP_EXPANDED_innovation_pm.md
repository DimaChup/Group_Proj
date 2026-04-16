# PP Expanded: Innovation Tools + Project Management

> Extracted from 5 source files. Every actionable concept with D7 priority, section, application, quote, and reference.

---

## INNOVATION TOOLS (Source: INNOVATION_TOOLS_COMPLETE.md)

### IT-01: Divergent vs Convergent Thinking
```
id:       IT-01
pri:      must
name:     Divergent vs Convergent Thinking
src:      INNOVATION_TOOLS_COMPLETE.md, Section 1
sections: D7 methodology / design approach
how:      Apollo's project had a clear divergent phase (brainstorming search patterns: lawnmower,
          spiral, expanding square; CV backends: TFLite, NCNN, Ultralytics, ONNX) followed by
          convergent phase (down-selecting to lawnmower + NCNN using benchmarks). Show you
          understand the two-phase process and that you looped back when initial choices failed
          (e.g. TFLite -> NCNN after benchmarking showed 4.5x speed gain).
quote:    "Normally you will try to progress through the divergent and convergent processes in
          one sweep, but when working with challenging problems you should keep it in mind that
          you may need to repeat the loop and generate new ideas if the one that you converged
          on does not satisfy your requirements."
ref:      Graham (2025), Innovation Methods: Down-Selection Tools, AENGM0074, UoB
```

### IT-02: Simple Pairwise Comparison (Non-Numerical Ranking)
```
id:       IT-02
pri:      should
name:     Simple Pairwise Comparison (Non-Numerical Ranking)
src:      INNOVATION_TOOLS_COMPLETE.md, Section 4
sections: D7 design decisions / criteria prioritisation
how:      Apollo could have used simple pairwise to rank flight test priorities (bench safety >
          detection accuracy > GPS precision > speed > landing precision). Each criterion
          compared pairwise, letter of winner recorded, count gives rank. Output: ordinal rank
          order, no magnitude. In practice the team's flight test ladder (bench -> passive ->
          waypoint -> auto) implicitly used this logic. Reflect on whether formalising it would
          have surfaced disagreements earlier.
quote:    "I have put the count for A as 2.5 because A was shown to be more important twice and
          equal once."
ref:      Graham (2025), slide 7, pairwise comparison matrix example
```

### IT-03: Numerical Pairwise Comparison (Weighted, 9/3/1 Scale)
```
id:       IT-03
pri:      should
name:     Numerical Pairwise Comparison (Weighted, 9/3/1 Scale)
src:      INNOVATION_TOOLS_COMPLETE.md, Section 5
sections: D7 design decisions / criteria weighting
how:      Produces percentage weightings (must sum to 100%). Apollo's CV backend selection
          criteria (inference speed, accuracy, Pi compatibility, model size, ease of deployment)
          could have been weighted this way: speed "much more important" (9) vs model size (1),
          giving speed ~41% weight. Weightings feed directly into MCDA (IT-05). The 9/3/1 scale
          with inverses (1/3, 1/9) for the reverse comparison. Symmetric matrix.
quote:    "The other numbers shown here are just the inverse of these numbers."
ref:      Graham (2025), slide 9, numerical pairwise Excel worksheet
```

### IT-04: Controlled Convergence / Pugh Matrix (Datum, +/=/-)
```
id:       IT-04
pri:      must
name:     Controlled Convergence / Pugh Matrix
src:      INNOVATION_TOOLS_COMPLETE.md, Section 6
sections: D7 design decisions / solution comparison
how:      Apollo's model selection is a natural Pugh matrix: Datum = YOLOv8n baseline (best.tflite).
          Alternatives: YOLOv8s (larger), COCO human.tflite (80-class), retrained sar_v2_1088.
          Criteria: inference speed, detection rate, model size, false positive rate. Each
          alternative scored +/=/- against datum. sar_v2_1088 wins (+accuracy, =speed, -size).
          The flight test progression (5 steps) is also a controlled convergence: each step is
          compared against the previous as datum.
quote:    "Just because it's the only idea left doesn't mean it's the one that you have to use."
ref:      Graham (2025), slide 12, balloon/helicopter/seagulls example
```

### IT-05: MCDA (Multi-Criteria Decision Analysis)
```
id:       IT-05
pri:      must
name:     MCDA (Multi-Criteria Decision Analysis)
src:      INNOVATION_TOOLS_COMPLETE.md, Section 7
sections: D7 design decisions / final selection
how:      Combines weightings (from IT-03) with solution scoring. Apollo's inference backend
          decision: criteria = speed (0.35), accuracy (0.25), Pi compatibility (0.20),
          deployment ease (0.10), community support (0.10). Score each backend 1-5. Weighted
          sum product = winner. NCNN wins (speed 5*0.35=1.75, accuracy 4*0.25=1.0,
          compatibility 4*0.20=0.8, deployment 3*0.10=0.3, support 3*0.10=0.3 = 4.15 vs
          TFLite 3.55). "Most popular tool with engineers as the process is very logical,
          very effective, but not over complicated."
quote:    "This seems to be the most popular tool with engineers as the process is very logical,
          very effective, but not over complicated."
ref:      Graham (2025), slide 15, energy storage MCDA example
```

### IT-06: Requirements Analysis Before Solution Selection
```
id:       IT-06
pri:      must
name:     Requirements Analysis Before Solution Selection
src:      INNOVATION_TOOLS_COMPLETE.md, Section 2
sections: D7 methodology / requirements
how:      Apollo's R01-R12 requirements (from project brief) were defined BEFORE selecting
          solutions. The DESIGN_DECISIONS.md file (DD-01 format) documents rationale for each
          choice. Group detailed requirements into 5-7 categories. "If you skip the requirements
          analysis, you'll most likely find that the solution selection takes much longer anyway."
          Evidence: config.py contains all parameters derived from requirements analysis.
quote:    "If you skip the requirements analysis, you'll most likely find that the solution
          selection takes much longer anyway as the team will find it harder to agree on what
          good is supposed to look like."
ref:      Graham (2025), slide 4
```

### IT-07: "Tools Support Thinking, Not Replace It"
```
id:       IT-07
pri:      must
name:     Tools Support Thinking, Not Replace It
src:      INNOVATION_TOOLS_COMPLETE.md, Section 6 (caveat) + Section 9
sections: D7 critical reflection / Hatton L4
how:      This is a KEY Hatton L4 move. Apollo can argue: "Our CV backend selection was driven by
          benchmark results rather than a formal MCDA. While the outcome was sound, the tool
          would have forced the team to articulate trade-offs explicitly." Show awareness that
          the team's decision is final and a gap between tool output and final choice is
          acceptable IF justified. "It's absolutely fine to have a gap between what the tool
          indicates and what you finally select, providing there's a justifiable and explainable
          reason for that gap."
quote:    "These are only simple tools, and they are there to support your thinking, not to
          replace it. In all cases, the team's decision is final."
ref:      Graham (2025), transcript
```

### IT-08: "Just Because It's the Only Idea Left..."
```
id:       IT-08
pri:      should
name:     Survivor Bias Warning
src:      INNOVATION_TOOLS_COMPLETE.md, Section 1 + Section 6
sections: D7 critical reflection
how:      Apply to search pattern selection: lawnmower was the "last idea standing" after
          rejecting spiral (poor coverage) and expanding square (complex nav). But Apollo should
          reflect: was lawnmower truly optimal, or just the survivor? The loop-back principle
          says generate new ideas if the survivor doesn't satisfy requirements. Evidence: the
          team DID iterate (added transit waypoints, edge margins, strip spacing optimisation).
quote:    "Just because it's the only idea left doesn't mean it's the one that you have to use."
ref:      Graham (2025), slide 3
```

### IT-09: Benefits — Faster Agreement, Neutralises Loud Voices, Stakeholder Explanation
```
id:       IT-09
pri:      should
name:     Benefits of Structured Tools
src:      INNOVATION_TOOLS_COMPLETE.md, Section 8
sections: D7 teamwork / professional practice
how:      Three benefits Apollo can reference:
          (1) Faster agreement: MCDA/Pugh would have shortened architecture debates.
          (2) Neutralises strong personalities: "Using an analytical tool is a great way of
          taking the focus away from personalities and placing the debate back within the
          realms of logic and reason." Relevant if team had dominant voices.
          (3) Stakeholder communication: "Essential for explaining to your stakeholders why you
          chose a particular idea" — directly applicable to D6/D7 report and viva.
quote:    "Using an analytical tool is a great way of taking the focus away from personalities
          and placing the debate back within the realms of logic and reason."
ref:      Graham (2025), slide 16
```

### IT-10: Risks — Rubbish In = Rubbish Out, Hiding Behind the Tool
```
id:       IT-10
pri:      should
name:     Risks of Structured Tools
src:      INNOVATION_TOOLS_COMPLETE.md, Section 9
sections: D7 critical reflection / Hatton L4
how:      Two risks Apollo should acknowledge:
          (1) GIGO: "If you put rubbish in, you will get rubbish out. You can't blame the Excel
          sheet if you clearly select the wrong idea." If benchmark conditions don't match
          real-world (e.g. benchmarking indoors vs outdoor with wind), the MCDA scores are
          misleading.
          (2) Hiding behind the tool: "The final trap is to start to hide behind the tool and
          let it take over as the master decision maker." Apollo's team used engineering
          judgement (DD-01 format) alongside data — this is the correct balance.
          (3) Too systematic kills creativity: "Have your wide-ranging unstructured debates
          first, and then use these tools to help tidy up afterwards."
quote:    "If you put rubbish in, you will get rubbish out. You can't blame the Excel sheet if
          you clearly select the wrong idea."
ref:      Graham (2025), slide 16
```

---

## PROJECT MANAGEMENT 1: DOWNSELECTION & RISK (Source: 1_DOWNSELECTION_RISK_COMPLETE.md)

### PM-01: Risk Assessment — Three Pillars (Moral/Economic/Legal)
```
id:       PM-01
pri:      must
name:     Risk Assessment Three Pillars
src:      1_DOWNSELECTION_RISK_COMPLETE.md, Slide 10
sections: D7 risk management / safety
how:      Apollo's R01-R12 risks cover ALL three pillars:
          - Moral/Ethical (H&S): R01 geofence, R02 SSSI, R03 TOL distance, R04 altitude cap, R09 link loss
          - Economic: R05 crash (property), R06 detection failure (schedule), R08 GPS accuracy (schedule), R11 platform incompatibility (schedule)
          - Legal: R10 detection evidence, R12 software license
          Show breadth: "Include a range of risk types — not just safety" (Graham, Slide 18).
quote:    "Include a range of risk types -- not just safety."
ref:      Graham (2025), PM1 Downselection & Risk, slide 10
```

### PM-02: Risk Number = Frequency x Consequence
```
id:       PM-02
pri:      must
name:     Risk Number Formula (F x C)
src:      1_DOWNSELECTION_RISK_COMPLETE.md, Slides 13-15
sections: D7 risk management
how:      Apollo's 12 risks each have pre-mitigation F, C, and RN scores. Define scales FIRST
          (1-5 for both). Then score. A common moderate event (bird strike RN=12) can outrank
          a rare catastrophe (volcanic ash RN=5). Apollo's highest pre-mitigation: R05 (crash,
          3x4=12) and R06 (detection failure, 4x3=12). After mitigation: R05 drops to 1x4=4.
quote:    "A common moderate event can have a higher risk number than a rare catastrophic event.
          This is the power of the multiplicative model."
ref:      Graham (2025), slides 13-15
```

### PM-03: Pre/Post Mitigation Scoring (Residual Risk)
```
id:       PM-03
pri:      must
name:     Residual Risk (Rescore After Mitigation)
src:      1_DOWNSELECTION_RISK_COMPLETE.md, Slides 16-17
sections: D7 risk management
how:      Apollo's risk table has explicit pre-mitigation RN and post-mitigation residual RN for
          all 12 risks. Shows quantitative risk reduction. E.g. R05: pre=12, added geofence +
          RC override + kill switch, post=4. Split mitigations into "existing" (RC override,
          kill switch = hardware) and "additional" (geofence, NFZ repulsion = software from RA).
quote:    "Consider rescoring the Frequency, Consequence and RN here is a great idea."
ref:      Graham (2025), slides 16-17, advanced template
```

### PM-04: Existing vs Additional Mitigations
```
id:       PM-04
pri:      should
name:     Split Existing and Additional Mitigations
src:      1_DOWNSELECTION_RISK_COMPLETE.md, Slide 19
sections: D7 risk management
how:      For each risk, distinguish what was ALREADY in place vs what the RA process ADDED.
          R05 example:
          - Existing: RC override (always active), kill switch (STABILIZE mode on RC)
          - Additional (from RA): runtime geofence (cv2.pointPolygonTest), NFZ repulsion,
            altitude hard cap (50m in navigation.py)
          "The score is based on existing mitigations" — pre-mitigation score already accounts
          for existing controls.
quote:    "The score is based on existing mitigations."
ref:      Graham (2025), slide 19
```

### PM-05: Combining Pairwise + MCDA Pipeline
```
id:       PM-05
pri:      could
name:     Tool Pipeline (Pairwise Weightings -> MCDA)
src:      1_DOWNSELECTION_RISK_COMPLETE.md, Slides 4-5
sections: D7 methodology
how:      Numerical pairwise comparison produces % weightings that feed directly into MCDA as
          criteria weights. Recommended pipeline: Tool 2 -> Tool 4. Apollo can show how risk
          assessment INFORMED the down-selection: model choice prioritised reliability/speed
          because RA identified R06 (detection failure) as high-priority (RN=12).
          "Warning — scales can cause excessive sensitivity" (Slide 5).
quote:    "Weightings from this Pairwise comparison can be used as the weightings in the MCDA."
ref:      Graham (2025), slides 4-5
```

### PM-06: Democratic Scoring — Should Each Voice Carry Equal Weight?
```
id:       PM-06
pri:      could
name:     Expert Weighting vs Democratic Averaging
src:      1_DOWNSELECTION_RISK_COMPLETE.md, Slide 6
sections: D7 teamwork / reflection
how:      MCDA scores can be averaged from team votes, but "Is more democratic necessarily
          better? Should each voice carry equal weight?" Apollo can reflect: the CV specialist's
          vote on model choice should carry more weight than a team member unfamiliar with
          inference pipelines. Passion/experience should carry weight.
quote:    "Is more democratic necessarily better? Should each voice carry equal weight?"
ref:      Graham (2025), slide 6
```

---

## PROJECT MANAGEMENT 1: PM TOOLS (Source: 2_PM1_COMPLETE.md)

### PM-07: WBS (100% Rule, Max 5 Levels)
```
id:       PM-07
pri:      must
name:     Work Breakdown Structure (WBS)
src:      2_PM1_COMPLETE.md, Slides 12-17
sections: D7 project management / planning
how:      Apollo created an explicit WBS in dashboard/src/pages/wbs-data.ts with hierarchical
          task breakdown. Rules: (1) No more than 5 levels, (2) Captures everything (100% rule),
          (3) Tasks contribute to parent. WBS tells you WHAT needs doing, not timing or
          dependencies. The file structure in CLAUDE.md IS a WBS. Flight testing steps (5-step
          ladder) = a testing WBS. 41 test scripts in 6 categories = test WBS.
          WBS -> List -> Kanban Board pipeline (Slides 19-21).
quote:    "No more than 5 levels. Captures everything (the 100% rule). Tasks contribute to
          parent task."
ref:      Graham (2025), PM1, slides 12-17
```

### PM-08: Network Diagrams (AOA, AON/PDM)
```
id:       PM-08
pri:      should
name:     Network Diagrams (AOA and AON/PDM)
src:      2_PM1_COMPLETE.md, Slides 22-32 + 4_SPECIALIST_COMPLETE.md, Slides 5-6
sections: D7 project management / scheduling
how:      Two formats: AOA (arrows = activities, nodes = events) and AON/PDM (nodes = activities,
          arrows = dependencies). AON is "most popular method" and "shows more timing data" and
          "easier to plot." Apollo's flight test dependency chain IS a network diagram:
          bench(0a) -> passive(1) -> waypoint(2) -> auto_detect(3) -> detect_and_center(4).
          Each node contains: ES, AD, EF (top), LS, TF, LF (bottom). Dummy activities (dashed,
          zero duration) represent dependencies without work.
quote:    "Activities drawn as arrows, Events (nodes) as circles, Time increases left to right."
ref:      Graham (2025), PM1 slides 22-30 + Specialist slides 5-6
```

### PM-09: Critical Path Method (Forward/Backward Pass, Float)
```
id:       PM-09
pri:      must
name:     Critical Path Method (CPM)
src:      2_PM1_COMPLETE.md, Slides 25-29 + 4_SPECIALIST_COMPLETE.md, Slides 8-11
sections: D7 project management / scheduling / risk
how:      Forward pass: EET(node) = MAX(EET(pred) + duration). Backward pass: LET(node) =
          MIN(LET(succ) - duration). Float = LET - EET (or LS - ES). If float = 0, task is
          critical. Apollo's critical path: Pi setup -> camera test -> Cube connection ->
          flight test. Float existed on: documentation, dashboard, model retraining, simulation.
          Zero float on hardware integration chain. Weather cancellation (2026-03-11) extended
          the critical path. "Any delay to a CP task delays the entire project."
quote:    "When earliest finish and latest start are equal, the event is part of the critical
          path."
ref:      Graham (2025), PM1 slides 25-29, AOA Cheat Sheet
```

### PM-10: Gantt Chart (5 Components)
```
id:       PM-10
pri:      should
name:     Gantt Chart — Five Components
src:      3_PM2_COMPLETE.md, Slides 8-15
sections: D7 project management / scheduling
how:      Five components: (1) Dependencies — arrows showing predecessor relationships,
          (2) Critical path tasks — highlighted/labelled CP, (3) Float — gap between task end
          and latest allowable finish, (4) Project length — total duration from start to end
          milestone, (5) Milestones — diamond markers at key dates. Apollo's dashboard WBS
          functioned as a living Gantt equivalent, tracking task dependencies, progress %,
          and milestone dates (D5, D6, D7). "Notice groupings of linked tasks."
quote:    "Notice groupings of linked tasks."
ref:      Graham (2025), PM2, slides 8-15
```

### PM-11: Resource Levelling (Sequential vs ASAP vs Levelled)
```
id:       PM-11
pri:      should
name:     Resource Levelling
src:      3_PM2_COMPLETE.md, Slides 19-26
sections: D7 project management / resource management
how:      Four approaches compared: Sequential (22 days, no extra staff, too slow), All ASAP
          (18 days, 2 extra designers, expensive), Levelled Pass 1 (18 days, 1 extra), Levelled
          Pass 2 (18 days, ZERO extra — optimal). Apollo's project: single Pi = bottleneck
          resource. Model training "subcontracted" to Colab GPU (like subcontracted manufacturing
          = no local resource). While training ran on Colab, team worked on flight test scripts
          and docs in parallel. This IS resource levelling — using float in training path to
          keep human resources continuously productive.
quote:    "Resource levelling allows a project to achieve the same duration as the 'everything
          ASAP' approach but with zero additional staff, by exploiting float in non-critical
          paths."
ref:      Graham (2025), PM2, slides 23-26
```

### PM-12: Rolling Wave Planning
```
id:       PM-12
pri:      should
name:     Rolling Wave Planning
src:      3_PM2_COMPLETE.md, Slides 27-28
sections: D7 project management / planning approach
how:      Near-term = detailed, far-term = abstract. Apollo's project naturally used this:
          Week 1-2: specific Python scripts, exact test sequences, line-by-line code changes.
          Month 2+: "achieve autonomous flight", "write report". As time passed, the wave of
          detailed planning rolled forward. Responds to three deterrents: "I don't have enough
          detail" -> start anyway. "I have no idea about durations" -> guesstimate. "I only
          know immediate tasks" -> that's rolling wave planning.
quote:    "I don't have enough detail to plan? Start planning anyway. I have no idea about
          durations? That's normal. Just guesstimate. I only know immediate tasks? Of course
          — that's called rolling wave planning."
ref:      Graham (2025), PM2, slides 27-28
```

### PM-13: Waterfall vs Agile vs Hybrid
```
id:       PM-13
pri:      must
name:     Waterfall vs Agile vs Hybrid Methodology
src:      2_PM1_COMPLETE.md, Slides 9-10
sections: D7 methodology / project management approach
how:      Apollo's project used a HYBRID approach. Waterfall elements: sequential flight testing
          ladder (cannot skip steps), regulated (drone safety, SSSI, RC kill switch), clear
          requirements (R01-R12), hardware dependencies inherently sequential. Agile elements:
          sprint-like development sessions, brain-dump.md = product backlog, NICE_TO_HAVE.md =
          prioritised backlog, Kanban task tracking, iterative model retraining (v1->v2->v3).
          "Not one size fits all" — depends on technology, company methods, innovation level.
          The waterfall/agile binary is an oversimplification; many methodologies exist.
quote:    "Not one size fits all."
ref:      Graham (2025), PM1, slides 9-10
```

### PM-14: Project Lifecycle Models
```
id:       PM-14
pri:      could
name:     Project Lifecycle Models (4/5/6/7/8 Phase)
src:      2_PM1_COMPLETE.md, Slides 5-7
sections: D7 project management / lifecycle
how:      Multiple models exist: 4-phase (Concept->Definition->Development->Handover), 5-phase
          APM PMBOK (Initiation->Planning->Execution->M&C->Closure), 6-phase, RIBA 8-phase.
          Apollo's project maps to 4-phase: Concept (Oct-Nov), Definition (Nov-Dec), Development
          (Jan-Mar), Handover/Closure (Mar-Apr). Or to APM PMBOK: Initiation (brief), Planning
          (WBS, dependencies, Gantt), Execution (code, build, train), Monitoring (session logs,
          brain-dump, NICE_TO_HAVE scoring), Closure (D7 report, lessons learned).
quote:    "Not one size fits all... depends on type of technology, company methods, new
          innovation or new application, customer and supplier systems."
ref:      Graham (2025), PM1, slides 5-7 + Airbus lifecycle (Panunzio, 2016)
```

### PM-15: Project vs Programme vs Portfolio
```
id:       PM-15
pri:      skip
name:     Project / Programme / Portfolio Hierarchy
src:      2_PM1_COMPLETE.md, Slides 3-4
sections: —
skip:     Too high-level for D7 individual reflection. Applicable to enterprise context, not
          a student MSc project. Mention only if discussing how the SAR project fits within the
          AENGM0074 unit as a "programme" containing multiple "projects" (D5, D6, D7).
ref:      Graham (2025), PM1, slides 3-4
```

---

## PROJECT MANAGEMENT 2: GANTT, RESOURCES, TUCKMAN (Source: 3_PM2_COMPLETE.md)

### PM-16: Tuckman Timeline Scenarios (Best/Probable/Worst)
```
id:       PM-16
pri:      must
name:     Tuckman Model — Five Stages + Three Timeline Scenarios
src:      3_PM2_COMPLETE.md, Slides 2-4
sections: D7 teamwork / team development
how:      Five stages: Forming (dependency, anxiety, politeness), Storming (tension, anger, less
          polite), Norming (cohesion, open communication, productivity increases), Performing
          (interdependence, high performance, roles fluid), Transforming (disengagement).
          Three scenarios: Best (short storming, quick to performing), Probable (moderate),
          Worst (team regresses back to Forming/Storming — significantly delayed). Apollo's
          team: Forming (role assignment), Storming (architecture disagreements), Norming
          (established Git workflow, testing progression), Performing (parallel workstreams),
          Transforming (report writing, knowledge transfer). Teams CAN REGRESS.
quote:    (No direct quote — concept from Tuckman model as presented in slides 2-4)
ref:      Graham (2025), PM2, slides 2-4; Tuckman (1965)
```

### PM-17: "Museum of Mediocrity" Anti-Pattern
```
id:       PM-17
pri:      should
name:     Museum of Mediocrity Anti-Pattern
src:      3_PM2_COMPLETE.md, Slide 29
sections: D7 critical reflection / quality
how:      Warning against producing mediocre project plans and deliverables. Apollo can use this
          as a reflective hook: "Graham's 'museum of mediocrity' warning motivated our team to
          go beyond minimum viable plans — maintaining living documentation (CLAUDE.md, session
          logs, blueprints) rather than producing a static plan that became obsolete by Week 3."
          Connect to the difference between a plan that looks good on paper and one that
          actually drives the project.
quote:    (Concept from slide 29 — pigeon at mediocre display)
ref:      Graham (2025), PM2, slide 29
```

### PM-18: "Group != Team"
```
id:       PM-18
pri:      must
name:     Group of Individuals != Team
src:      3_PM2_COMPLETE.md, Slides 30-31
sections: D7 teamwork / reflection
how:      Two metaphors: "Lone Genius" (castle, working in isolation) and "Drifting along,
          drifting alone" (raft with people paddling different directions, TIME is the shark).
          Apollo can reflect on whether the team was truly integrated or five individuals
          working in parallel. Evidence of team behaviour: shared Git repo, defined interfaces
          (vision.py 4-tuple API), progressive test ladder requiring sequential handoffs,
          cross-contribution in later sprints. Evidence of group behaviour: different schedules,
          some parallel-but-uncoordinated work.
quote:    "A group of individuals is not a team."
ref:      Graham (2025), PM2, slides 30-31
```

### PM-19: "Delaying Planning = Skeleton at Bus Stop"
```
id:       PM-19
pri:      could
name:     Don't Wait for Perfect Information
src:      3_PM2_COMPLETE.md, Slide 32
sections: D7 planning approach
how:      "I'll start when I have all the information" = fatal mistake. You will never have all
          the information. Start planning now with what you know. Connects to rolling wave
          planning (PM-12). Apollo started development before knowing Pi camera specs, Cube
          baud rate, or outdoor GPS accuracy — then adjusted config.py as real data emerged.
          This is the pragmatic approach.
quote:    "I'll start when I have all the information" (anti-pattern)
ref:      Graham (2025), PM2, slide 32
```

### PM-20: Three Equivalent Representations (Table <-> Network <-> Gantt)
```
id:       PM-20
pri:      could
name:     Table / Network / Gantt Equivalence
src:      3_PM2_COMPLETE.md, Slide 18
sections: D7 project management
how:      Table (best for data entry), Network (best for analysis — CP, float), Gantt (best
          for stakeholder communication). Each can be derived from the others. Apollo used
          table format (CLAUDE.md task lists), network logic (dependency chain in flight tests),
          and Gantt equivalent (dashboard WBS with timeline). The skill is knowing when to use
          which representation.
quote:    (Concept from slide 18 — three equivalent representations)
ref:      Graham (2025), PM2, slide 18
```

---

## PM SPECIALIST SESSION 1 (Source: 4_SPECIALIST_COMPLETE.md)

### PM-21: 7 Planning Challenges
```
id:       PM-21
pri:      should
name:     Seven Planning Challenges
src:      4_SPECIALIST_COMPLETE.md, Slide 3
sections: D7 project management / challenges
how:      (1) Real-life complexity — 11-state state machine, 41 test scripts, 3 platforms.
          (2) Software limitations — no professional PM tool; tracked via WBS dashboard + CLAUDE.md.
          (3) Non-continuous working — 5 team members with different schedules, MSc part-time effort.
          (4) Precedence types — used FS (sequential testing), SS (parallel development), FF
          (coordinated testing).
          (5) Resource scheduling — single Pi = bottleneck; laptop development parallelised.
          (6) Intra-team dependencies — vision.py output format determined main.py interface.
          (7) Macro & micro scale — high-level phases + micro-level 41 test scripts in 6 categories.
quote:    "Man-days != days taken."
ref:      Graham (2025), Specialist Session 1, slide 3
```

### PM-22: 10-Level Competence Ladder
```
id:       PM-22
pri:      could
name:     10-Level Planning Competence Ladder
src:      4_SPECIALIST_COMPLETE.md, Slide 4
sections: D7 self-assessment / reflection
how:      Levels 1-6 achievable, 7-10 "exponentially more challenging." Apollo's project reached
          approximately Level 7-8: tasks defined (L1), consistent across tools (L2), dependencies
          shown (L3-4), intra-team dependencies mapped (L5), CP identified (L6), timings computed
          (L7), non-continuous working partially modelled (L8). Levels 9-10 (Gantt-network
          correlation, resource scheduling) not formally achieved — used informal tracking. This
          honest self-assessment is a Hatton L4 move.
quote:    "Items >= 7 are exponentially more challenging."
ref:      Graham (2025), Specialist Session 1, slide 4
```

### PM-23: Precedence Relationships (FS, SS, FF, SF)
```
id:       PM-23
pri:      should
name:     Four Precedence Relationship Types
src:      4_SPECIALIST_COMPLETE.md, Slides 17-21
sections: D7 project management / scheduling
how:      FS (Finish-to-Start, most common): simulation must FINISH before Pi integration STARTS.
          SS (Start-to-Start + lag): Pi hardware setup can START same time as software development.
          Documentation can START shortly after development STARTS.
          FF (Finish-to-Finish + lag): unit tests must FINISH close to when the module they test
          FINISHES.
          SF (Start-to-Finish, rarest): old system phaseout can't finish until new system starts.
          Not directly applicable to SAR project.
          Example FS with lag: after soldering Pi connections, wait for inspection before power-on.
quote:    "Concrete can be drilled 2 days after it has been laid." (FS with lag example)
ref:      Graham (2025), Specialist Session 1, slides 17-20
```

### PM-24: AON/PDM Node Anatomy (ES, AD, EF, LS, TF, LF)
```
id:       PM-24
pri:      skip
name:     PDM Node Anatomy — 6-Field Box
src:      4_SPECIALIST_COMPLETE.md, Slide 6
sections: —
skip:     Too mechanical/procedural for D7 reflection. This is the "how to draw" rather than
          "how to apply." Reference the concept (PM-09 CPM) but don't detail the node box format
          unless building an actual network diagram for the appendix.
ref:      Graham (2025), Specialist Session 1, slide 6
```

### PM-25: Non-Continuous Working (Weekends, Delay Nodes)
```
id:       PM-25
pri:      should
name:     Non-Continuous Working
src:      4_SPECIALIST_COMPLETE.md, Slides 15-16
sections: D7 project management / realism
how:      Man-days != elapsed days. Task D (5 working days) bridging a weekend becomes D(1)+
          Delay(2)+D(2) = 9 elapsed days. "The whole network might need recalculating multiple
          times." Apollo's project: 5 team members with different lecture schedules, weather
          cancellation inserted a delay node (2026-03-11), Pi hardware shared (serialised access).
          Weekend gaps bridged development sprints. Critical for honest schedule reporting.
quote:    "The whole network might need recalculating multiple times."
ref:      Graham (2025), Specialist Session 1, slides 15-16
```

### PM-26: Intra-Team Dependencies as Interface Contracts
```
id:       PM-26
pri:      should
name:     Intra-Team Dependencies
src:      4_SPECIALIST_COMPLETE.md, Slide 3 (item 5) + D7 mapping
sections: D7 teamwork / architecture
how:      Outputs from one sub-team become inputs for another. Apollo managed this through
          interface contracts: vision.py's output detect_in_image(frame) -> (found, x, y, conf)
          was defined BEFORE implementation, allowing main.py to develop against the interface
          while vision evolved. The 4-tuple interface was stable across 3 model versions, 2
          backends, and lens undistortion addition. "Well-defined interfaces reduce critical
          path coupling." This is "programming to interfaces" applied as a PM technique.
quote:    "Intra-team dependencies (i.e. inputs/outputs) are shown on the network and Gantt."
ref:      Graham (2025), Specialist Session 1, slide 3
```

---

## CROSS-CUTTING HATTON L4 MOVES (synthesised from all sources)

### L4-01: Formal Tools We Didn't Use (Reflective Gap)
```
id:       L4-01
pri:      must
name:     Hatton L4 — What We Should Have Done
sections: D7 critical reflection
how:      "Looking back, our CV backend selection (TFLite to NCNN migration) was driven by
          benchmark results rather than a structured MCDA. While the outcome was sound, a
          formal weighted comparison incorporating criteria such as deployment complexity,
          community support, and long-term maintainability alongside raw inference speed would
          have produced a more defensible decision and forced the team to articulate trade-offs
          explicitly." (IT-05 + IT-07)
```

### L4-02: Float as Strategic Resource
```
id:       L4-02
pri:      must
name:     Hatton L4 — Float Consumption Strategy
sections: D7 project management
how:      "Vision.py had significant float (independent module, not on critical path), which was
          intentionally used: the vision system was iteratively refined across 3 model versions
          without ever blocking the critical path through main.py integration. This demonstrates
          planned float consumption — using non-critical path time for quality improvement rather
          than treating float as purely defensive slack." (PM-09 + PM-11)
```

### L4-03: Hybrid Methodology Justification
```
id:       L4-03
pri:      must
name:     Hatton L4 — Risk-Driven Hybrid
sections: D7 methodology
how:      "Rather than adopting pure waterfall or agile, I employed a risk-driven approach. The
          hardware integration path followed strictly sequential waterfall discipline — you
          cannot test flight software before verifying the serial connection — while the software
          development path used agile sprints with continuous integration. This hybrid was
          necessary because 'not one size fits all' (Graham, 2025)." (PM-13)
```

### L4-04: Critical Path Shifted Under Uncertainty
```
id:       L4-04
pri:      should
name:     Hatton L4 — Dynamic Critical Path
sections: D7 project management / risk
how:      "The critical path shifted dynamically: initially through software development, but
          after weather cancelled outdoor testing, it pivoted to hardware validation. This
          demonstrates that critical path analysis must be a continuous monitoring activity,
          not a one-time calculation." (PM-09 + PM-25)
```

### L4-05: Tuckman + Rolling Wave Synthesis
```
id:       L4-05
pri:      should
name:     Hatton L4 — Team Maturity Enables Planning Detail
sections: D7 teamwork + planning
how:      "During Forming and Storming, we could only plan at module level because roles were
          still being negotiated. As we reached Norming and Performing, planning resolution
          naturally increased — we could schedule specific test scripts to specific days. This
          suggests rolling wave planning is not merely a response to information uncertainty
          but also to team maturity: detailed planning requires the stable working relationships
          that only emerge in Norming/Performing." (PM-16 + PM-12)
```

---

## PRIORITY SUMMARY

| Priority | Count | IDs |
|----------|-------|-----|
| **must** | 14 | IT-01, IT-04, IT-05, IT-06, IT-07, PM-01, PM-02, PM-03, PM-07, PM-09, PM-13, PM-16, PM-18, L4-01/02/03 |
| **should** | 14 | IT-02, IT-03, IT-08, IT-09, IT-10, PM-04, PM-06, PM-08, PM-10, PM-11, PM-12, PM-21, PM-23, PM-25, PM-26, L4-04/05 |
| **could** | 5 | PM-05, PM-14, PM-19, PM-20, PM-22 |
| **skip** | 2 | PM-15 (project/programme/portfolio — too enterprise), PM-24 (PDM node anatomy — too mechanical) |

---

## BIBTEX ENTRIES

```bibtex
@misc{graham_innovation_tools,
  author       = {Graham, Mark},
  title        = {Innovation Methods: Down-Selection Tools},
  year         = {2025},
  howpublished = {AENGM0074 Professional Practice video lecture, University of Bristol},
  note         = {Pairwise comparison, Pugh matrix, MCDA}
}

@misc{graham_pm1_risk,
  author       = {Graham, Mark},
  title        = {Down-Selection and Risk Management},
  year         = {2025},
  howpublished = {AVDASI2 Project Workshop Week 3, University of Bristol},
  note         = {Risk assessment three pillars, F x C model, residual risk}
}

@misc{graham_pm1,
  author       = {Graham, Mark},
  title        = {Project Management 1},
  year         = {2025},
  howpublished = {AVDASI2 Lecture, 13 October 2025, University of Bristol},
  note         = {WBS, network diagrams, critical path, waterfall vs agile}
}

@misc{graham_pm2,
  author       = {Graham, Mark},
  title        = {Project Management 2},
  year         = {2025},
  howpublished = {AVDASI2 Lecture, 13 October 2025, University of Bristol},
  note         = {Gantt charts, resource levelling, Tuckman model, rolling wave planning}
}

@misc{graham_pm_specialist,
  author       = {Graham, Mark},
  title        = {Project Management Specialist Session 1},
  year         = {2025},
  howpublished = {AVDASI2 Specialist Class, 12 November 2025, University of Bristol},
  note         = {PDM/AON, precedence relationships (FS/SS/FF/SF), non-continuous working, competence ladder}
}
```
