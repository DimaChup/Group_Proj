# PM Specialist Session 1 -- Complete Extraction

**Source**: "4 PM Specialist Session 1.pdf" (22 slides)
**Lecturer**: Mark Graham (avdasi2@bristol.ac.uk)
**Date**: 12 November 2025
**Module**: AVDASI2 Project Management (Specialist Class 1)

---

## SLIDE-BY-SLIDE EXTRACTION

### Slide 1 -- Title
- **PROJECT MANAGEMENT (SPECIALIST CLASS 1)**
- 12th November 2025, Mark Graham
- University of Bristol

### Slide 2 -- Project Management Summative Assessment
- Submit and discuss your team's project plans for the AVDASI2 project
- Plans must include detailed/thorough planning for the **Detailed Design and Final Manufacture phase**
- Expected deliverables: **WBS, Network Diagram, and Gantt chart**
- Must show how your detailed plan fits into the larger team and then company plan
- Formative feedback is available at a defined point
- Concurrent documentation required for this phase
- Diagram shows the 2025-26 AVDASI2 Project Plan timeline with the "Detailed Design + FDR" phase highlighted in red

### Slide 3 -- Planning Challenges
Seven key challenges identified:
1. **Real-life complexity** -- plans must handle messy reality, not textbook simplicity
2. **Limitations (and availability) of software** -- PM tools have constraints
3. **Non-continuous working** (Man-days != days taken) -- people don't work 24/7; weekends, holidays, shared resources mean elapsed time exceeds effort
4. **Types of precedence relationship** -- not all tasks are simple finish-to-start
5. **Resource scheduling (and availability)** -- who is available when, shared across teams
6. **Intra-team dependencies** -- outputs from one sub-team become inputs for another
7. **Representing the macro & micro scale** -- need both high-level overview and detailed task breakdowns

### Slide 4 -- Increasing Planning Competence (and Difficulty)
**Three integrated tools**: WBS + Network + Gantt

Ten levels of increasing competence:
1. The team's final design and manufacturing work is fully defined
2. Tasks are same between the three tools
3. Dependencies are shown on the network
4. Dependencies are shown on the Gantt
5. Intra-team dependencies (i.e. inputs/outputs) are shown on the network and Gantt
6. Network shows precedence relationship type and CP (Critical Path)
7. Network shows timings
8. Network accounts for non-continuous working
9. Network and Gantt timings correlate
10. Network and Gantt consider resource scheduling

**Key insight**: Items >= 7 are **exponentially more challenging**

### Slide 5 -- AoA vs AoN (Precedence Diagramming Method PDM)
Two network diagramming approaches compared:

**Activity-on-Arrow (AoA)**:
- Arrow shows activity
- Easy to learn
- Difficult to plot for a complex network
- Often requires dummy tasks
- Example shows nodes 0-4 with activities A(3), B(2), C(4), D(8), E(2)

**Activity-on-Node (PDM -- Precedence Diagramming Method)**:
- Node shows activity
- **Most popular method**
- Shows more timing data
- Easier to plot
- Can encode the maths
- Each node contains: ES, AD, EF (top row), Activity name (middle), LS, TF, LF (bottom row)
- Worked example: Start -> Warm Iron / Collect Parts -> Solder Parts / Fit Parts to PCB -> Test -> Finish

### Slide 6 -- Building an Activity-on-Node (PDM)
**Node anatomy** (6 fields per box):
- **ES** = Earliest Start (top-left)
- **AD** = Activity Duration (top-centre)
- **EF** = Earliest Finish (top-right)
- **Unique identifier** (e.g. 1.1) -- centre
- **Activity name or description** -- centre
- **LS** = Latest Start (bottom-left)
- **TF** = Total Float (bottom-centre)
- **LF** = Latest Finish (bottom-right)

Example node: ES=0, AD=3, EF=3, Activity "A", "Warm Iron", LS=3, TF=3, LF=6

### Slide 7 -- Soldering Example: Step 1 -- Add Durations
**Activity table**:
| Activity | Description | Predecessor | Duration (mins) |
|----------|-------------|-------------|-----------------|
| A | Warm-up iron | -- | 3 |
| B | Collect all parts | -- | 2 |
| C | Fit parts to PCB | B | 4 |
| D | Solder parts | A, C | 8 |
| E | Test | D | 2 |

Network drawn with durations filled in, ES/EF/LS/TF/LF blank.

### Slide 8 -- Soldering Example: Step 2 -- Forward Pass
**Forward pass rules** (left to right):
- a) **Earliest Start = Earliest Finish of predecessor activity** (choose latest EF if multiple predecessors)
- b) **Earliest Finish = Earliest Start + Activity Duration**

Computed values:
- Start: ES=0, EF=0
- A (Warm Iron): ES=0, AD=3, EF=3
- B (Collect Parts): ES=0, AD=2, EF=2
- C (Fit Parts): ES=2, AD=4, EF=6
- D (Solder Parts): ES=6, AD=8, EF=14 (takes max of A's EF=3 and C's EF=6, so ES=6)
- E (Test): ES=14, AD=2, EF=16
- Finish: ES=16, EF=16

**Project duration = 16 minutes**

### Slide 9 -- Soldering Example: Step 3 -- Backwards Pass
**Backward pass rules** (right to left):
- a) **Latest Finish = Latest Start of successor activity** (choose earliest LS if multiple successors)
- b) **Latest Start = Latest Finish - Activity Duration**

Computed values:
- Finish: LS=16, LF=16
- E (Test): LS=14, LF=16
- D (Solder Parts): LS=6, LF=14
- C (Fit Parts): LS=2, LF=6
- B (Collect Parts): LS=0, LF=2
- A (Warm Iron): LS=3, LF=6

### Slide 10 -- Soldering Example: Step 4 -- Calculate Float
**Total Float = Latest Start - Earliest Start**
- If TF = 0, this is a **Critical Path task**

Computed float values:
- Start: TF=0 (critical)
- A (Warm Iron): TF = 3-0 = **3** (NOT critical, 3 mins slack)
- B (Collect Parts): TF = 0-0 = **0** (critical)
- C (Fit Parts): TF = 2-2 = **0** (critical)
- D (Solder Parts): TF = 6-6 = **0** (critical)
- E (Test): TF = 14-14 = **0** (critical)
- Finish: TF=0 (critical)

### Slide 11 -- Soldering Example: Step 4 -- Identify Critical Path
- Critical Path highlighted in **red/bold**: Start -> B -> C -> D -> E -> Finish
- Activity A (Warm Iron) has TF=3, so it is NOT on the critical path
- A can be delayed by up to 3 minutes without affecting the project end date
- The CP determines the minimum project duration (16 mins)

### Slide 12 -- Building an Activity-on-Node (PDM) Diagram -- Summary
Complete 8-step procedure:
1. Identify the activity dependencies
2. Draw the activity boxes and record a unique identifier and activity description
3. Draw the dependency lines between the boxes
4. Record the Activity Durations
5. **Forward Pass**: Working through the complete network from start to finish (left to right)
   - a) Earliest Start = Earliest Finish of predecessor activity (choose latest EF if multiple predecessors)
   - b) Earliest Finish = Earliest Start + Activity Duration
6. **Backwards Pass**: Working back through the complete network from finish to start (right to left)
   - a) Latest Finish = Latest Start of successor activity (choose earliest LS if multiple successors)
   - b) Latest Start = Latest Finish - Activity Duration
7. **Total Float = Latest Start - Earliest Start** (if 0, then this is a Critical Path task)
8. **Label critical path** (bold/colour/symbol)

### Slide 13 -- Example 2
More complex network with 7 activities (A-G):
- Two parallel paths from Start
- Critical path shown in red/bold: Start -> B -> E -> G -> Finish (duration = 9)
- Also shows AoA equivalent diagram in bottom-right corner with dummy tasks marked
- Activities A(2), B(3), C(4), D(5), E(5), F(2), G(1)
- Path through A has float (TF=1 for A)

### Slide 14 -- Example 3
Seven activities (A-G) with more complex dependencies:
- Activity table: A(3,Start), B(2,Start), C(4,A), D(5,B), E(4,B), F(3,C+D), G(2,E)
- **Two critical paths** identified:
  - Start -> B -> D -> F -> Finish (duration = 10)
  - Start -> A -> C -> F -> Finish (duration = 10)
- All activities on these paths have TF=0
- Activities E(TF=2) and G(TF=2) have float
- Also shows AoA equivalent with dummy tasks

### Slide 15 -- Dealing with Non-Continuous Working (Problem)
- Same Example 3 network but poses the question:
- **"What happens if task D takes 5 days, but bridges a weekend?"**
- This is critical for real-world planning where elapsed time != working time

### Slide 16 -- Dealing with Non-Continuous Working (Solution)
- Task D (5 working days) is **split into D(1) and D(2)** with a **Delay (Weekend)** node inserted
- D(1): ES=2, AD=3, EF=5 (3 working days before weekend)
- Delay (Weekend): ES=5, AD=2, EF=7 (2 non-working days)
- D(2): ES=7, AD=2, EF=9 (remaining 2 working days)
- This pushes the project from 10 to **12 days elapsed**
- Float on E and G increases (E: TF=4, G: TF=4)
- **"The whole network might need recalculating multiple times"** when accounting for non-continuous working
- Key insight: the network must model REAL calendar time, not just effort

### Slide 17 -- Types of Precedence Relationship: Finish-to-Start (FS)
**Finish-to-Start (FS)** -- the most common relationship:
- **FS = 0** (no lag): B starts immediately when A finishes
- **FS = 2** (with lag): B can start 2 days AFTER A finishes
- Example: "Concrete can be drilled 2 days after it has been laid"
- Shows both network notation and Gantt representation

### Slide 18 -- Types of Precedence Relationship: Start-to-Start (SS)
**Start-to-Start (SS)**:
- **SS = 5**: Task B can start 5 days after Task A has started
- Example: "Design of actuator mounting bracket can start 5 days after mechanism design has started"
- Allows overlapping/concurrent work with a controlled delay
- Shows both network and Gantt views

### Slide 19 -- Types of Precedence Relationship: Finish-to-Finish (FF)
**Finish-to-Finish (FF)**:
- **FF = 5**: Task B must finish 5 days (at the latest) after Task A has finished
- Example: "Must finish painting the parking lines no more than 5 days after finishing asphalting the road"
- Constrains the END of successor relative to END of predecessor
- Shows both network and Gantt views

### Slide 20 -- Types of Precedence Relationship: Start-to-Finish (SF)
**Start-to-Finish (SF)** -- the rarest relationship:
- **SF = 5**: Task B cannot finish until 5 days after Task A has started
- Example: "Phase out old system cannot finish until 5 days after testing of new system has started"
- Used for system transitions/cutover scenarios
- Shows both network and Gantt views

### Slide 21 -- Gantt Relationship Examples
Practical Gantt chart showing a "Build > Wing" work package with tasks 1.1-1.5 plus 1.3:
- **SS with lag** between Task a (1.1) and Task b (1.2) -- overlapping start
- **FS no lag** between Task b (1.2) and Task c (1.3) -- sequential
- **FS with lag** between Task c (1.3) and Task d (1.4) -- gap between
- **FF with lag** between Task e (1.5) and Task f (1.3) -- finish alignment
- Demonstrates how all four relationship types appear on a real Gantt chart
- Timeline spans weeks 13-17, with dates from 22/01 to 23/02

### Slide 22 -- End Slide
University of Bristol branding, bristol.ac.uk

---

## KEY CONCEPTS SUMMARY

### 1. The Three Integrated PM Tools
| Tool | Purpose | Shows |
|------|---------|-------|
| **WBS** | Decompose work into manageable tasks | Hierarchy, scope, ownership |
| **Network Diagram** | Show dependencies, calculate CP, timings | Logic, float, critical path |
| **Gantt Chart** | Show timeline, resource allocation | Calendar, milestones, progress |

All three must use the **same task list** and be **internally consistent**.

### 2. Critical Path Method (CPM) -- The Core Algorithm
1. Forward pass: compute ES, EF for every activity
2. Backward pass: compute LS, LF for every activity
3. Float = LS - ES (or LF - EF)
4. Critical path = all activities with float = 0
5. Project duration = EF of final activity

### 3. Four Precedence Relationships
| Type | Notation | Meaning | Example |
|------|----------|---------|---------|
| **Finish-to-Start** | FS | B starts after A finishes | Most common; sequential tasks |
| **Start-to-Start** | SS | B starts after A starts (+ lag) | Overlapping design work |
| **Finish-to-Finish** | FF | B finishes after A finishes (+ lag) | Coordinated completion |
| **Start-to-Finish** | SF | B finishes after A starts (+ lag) | System cutover/transition |

### 4. Non-Continuous Working
- Man-days != elapsed days
- Weekends, holidays, part-time availability must be modelled
- Solution: insert **delay nodes** into the network for non-working periods
- May require **multiple recalculations** of the entire network
- Critical for student projects where team members have lectures, exams, other commitments

### 5. Competence Levels (Assessment Ladder)
- Levels 1-6: defining tasks, showing dependencies, identifying CP -- achievable
- Levels 7-10: encoding timings, non-continuous working, resource scheduling, Gantt correlation -- **exponentially harder**
- The assessment rewards those who reach levels 7+

---

## MAPPING TO APOLLO'S SAR DRONE PROJECT

### Critical Path Analysis Applied to SAR Drone

**The SAR drone project has a clear critical path through software development:**

| Activity | Description | Predecessor | Duration (days) | On CP? |
|----------|-------------|-------------|-----------------|--------|
| A | Config + state machine design | -- | 3 | Yes |
| B | Vision system (vision.py) | -- | 5 | No |
| C | Planning module (planning.py) | -- | 2 | No |
| D | Main orchestrator (main.py) | A, B, C | 10 | Yes |
| E | SITL simulation testing | D | 3 | Yes |
| F | Pi hardware setup | -- | 4 | No |
| G | Pi integration testing | E, F | 3 | Yes |
| H | Flight testing (progressive) | G | 5 | Yes |

**Critical Path**: A -> D -> E -> G -> H (24 days)
**Float on B (Vision)**: Can be delayed ~2 days without affecting project
**Float on F (Pi Setup)**: Can be delayed ~11 days without affecting project

### Precedence Relationships in the SAR Project

**FS (Finish-to-Start)**:
- Vision system must be FINISHED before main.py integration can START
- Simulation testing must FINISH before Pi integration testing can START

**SS (Start-to-Start)**:
- Pi hardware setup (F) can START at the same time as software development (A)
- Documentation can START shortly after development STARTS (SS with lag)
- "Design of actuator mounting bracket can start 5 days after mechanism design has started" -- analogous to our GPS estimation module starting once the core detection pipeline was partially built

**FF (Finish-to-Finish)**:
- Unit tests must FINISH close to when the module they test FINISHES
- Report writing must FINISH near when development FINISHES

**FS with Lag**:
- After soldering Pi connections, need to wait for inspection before powering on (FS+1 day)
- After pushing code to Pi, need SSH connection established before testing (FS+0.5 day)

### Non-Continuous Working -- Direct Relevance

The SAR project experienced exactly the challenge described in Slide 15-16:
- **Team members had lectures on different days** -- man-days != calendar days
- **Weather cancelled flight day** (2026-03-11) -- delay node inserted, entire schedule shifted
- **Pi hardware was shared** -- only one Pi, so hardware testing was serialised
- **Weekend gaps** -- development sprints bridged weekends, adding elapsed time
- The network had to be **recalculated multiple times** when weather delays and hardware availability changed

### Planning Challenges (Slide 3) -- Evidence from Project

1. **Real-life complexity**: 11-state state machine, 41 test scripts, 3 platforms (Windows/WSL/Pi)
2. **Software limitations**: No professional PM tool used; tracked via WBS dashboard + CLAUDE.md
3. **Non-continuous working**: 5 team members with different schedules; part-time MSc effort
4. **Precedence types**: Used all 4 types -- sequential testing ladder (FS), parallel development (SS), coordinated testing (FF)
5. **Resource scheduling**: Single Pi 5 = bottleneck resource; laptop development parallelised
6. **Intra-team dependencies**: Vision system output format determined main.py interface; config.py auto-detect required by all modules
7. **Macro & micro scale**: High-level phases (Design -> Sim -> Hardware -> Flight) with micro-level task breakdowns (41 test scripts in 6 categories)

---

## WEAPONIZABLE QUOTES

### From the Lecture
1. **"Items >= 7 are exponentially more challenging"** -- on reaching competence levels 7-10 in network planning. Use to justify why professional-grade scheduling is rare in student projects.

2. **"Man-days != days taken"** -- the fundamental non-continuous working insight. Direct quote usable in any discussion of schedule estimation.

3. **"The whole network might need recalculating multiple times"** -- on non-continuous working. Use to argue that real project schedules are living documents, not static plans.

4. **"Choose latest EF if multiple predecessors"** -- the merge-point rule. The reason parallel paths create bottlenecks; the slowest predecessor determines the earliest start.

### Constructable from Lecture Content
5. **"Total Float = Latest Start - Earliest Start; if zero, the task is critical"** -- the definition of critical path membership. Use to show you understand the mathematical basis.

6. **"The critical path determines the minimum project duration"** -- any delay to a CP task delays the entire project by the same amount.

7. **"A task with float can be delayed without affecting the project end date, but a task on the critical path cannot"** -- the practical meaning of float.

---

## HATTON L4 MOVES

### Move 1: Critical Evaluation of CPM Limitations in Agile-Adjacent Projects
The CPM (Critical Path Method) taught in this session assumes **deterministic task durations** and **known dependencies at planning time**. In the SAR drone project, neither assumption held: inference speed on the Pi was unknown until benchmarking (206ms actual vs. "target <200ms" estimated), and the weather-cancelled flight day introduced a dependency that did not exist in the original plan. This aligns with Wysocki's (2019) observation that traditional PM methods struggle with **exploratory projects** where scope emerges through iteration. The SAR project's progressive testing ladder (bench -> passive -> waypoint -> autonomous) is effectively a **risk-ordered critical path** where each stage validates assumptions before committing to the next, blending CPM's sequential logic with agile's iterative discovery.

### Move 2: Float as a Strategic Resource, Not Just Slack
Graham's lecture defines float as "how much a task can be delayed without affecting the project end date." In practice, float is a **strategic buffer** that can be deliberately consumed. In the SAR project, vision.py had significant float (it was an independent module that could be developed in parallel), which was intentionally used: the vision system was iteratively refined across 3 model versions (sar_640, sar_1280, sar_v2_1088) without ever blocking the critical path through main.py integration. This demonstrates **planned float consumption** -- using non-critical path time for quality improvement rather than treating float as purely defensive slack. Goldratt's (1997) Critical Chain methodology formalises this as "feeding buffers."

### Move 3: Non-Continuous Working as the Dominant Planning Challenge
Of the seven planning challenges listed (Slide 3), **non-continuous working** proved the most impactful for the SAR project. With 5 team members across different MSc programmes, the effective work rate was approximately 0.3 FTE per person (lectures, other coursework, exams). A task estimated at "5 man-days" typically consumed 2-3 calendar weeks. The lecture's solution of inserting delay nodes (Slide 16) works for predictable breaks (weekends), but fails for the **stochastic interruptions** common in student projects (illness, competing deadlines, equipment availability). This gap between the taught method and lived experience suggests that **probabilistic scheduling** (PERT analysis with optimistic/pessimistic/most-likely estimates) would be more appropriate for university project planning than deterministic CPM.

### Move 4: Intra-Team Dependencies as Interface Contracts
Slide 4 item 5 identifies "intra-team dependencies (i.e. inputs/outputs)" as a key planning element. In the SAR project, this was managed through **interface contracts**: vision.py's output `detect_in_image(frame) -> (found, x, y, conf)` was defined before implementation, allowing main.py development to proceed against the interface while the vision implementation evolved. This is the software engineering concept of **programming to interfaces** applied as a PM technique -- it decouples the dependency from the implementation timeline. The 4-tuple interface was stable across all 3 model versions, 2 backends (Ultralytics/TFLite), and the addition of lens undistortion, validating that **well-defined interfaces reduce critical path coupling**.

### Move 5: Assessment Competence Ladder as a Maturity Model
The 10-level competence ladder (Slide 4) can be read as a **PM maturity model**. The SAR project reached approximately Level 7-8: tasks were defined (L1), consistent across WBS/network/Gantt (L2), dependencies shown (L3-4), intra-team dependencies mapped (L5), CP identified (L6), timings computed (L7), and non-continuous working partially accounted for (L8). Levels 9-10 (Gantt-network correlation, resource scheduling) were not formally achieved due to the project using an informal tracking system rather than professional PM software. This honest self-assessment against the taught framework demonstrates **reflective practice** -- recognising both competence achieved and gaps remaining.

---

## REFERENCES

- **Graham, M.** (2025) "Project Management (Specialist Class 1)", AVDASI2, University of Bristol, 12 November 2025.
- **Goldratt, E.M.** (1997) *Critical Chain*. Great Barrington, MA: North River Press.
- **Wysocki, R.K.** (2019) *Effective Project Management: Traditional, Agile, Extreme, Hybrid*. 8th edn. Indianapolis: Wiley.
- **PMI** (2021) *A Guide to the Project Management Body of Knowledge (PMBOK Guide)*. 7th edn. Project Management Institute.
- **Lock, D.** (2020) *Project Management*. 11th edn. Abingdon: Routledge.

---

## QUICK-REFERENCE: KEY FORMULAE

```
ES = max(EF of all predecessors)        -- Forward Pass
EF = ES + AD                            -- Forward Pass
LF = min(LS of all successors)          -- Backward Pass
LS = LF - AD                            -- Backward Pass
TF = LS - ES  (or equivalently LF - EF) -- Float
CP = all activities where TF = 0        -- Critical Path
Project Duration = EF(Finish node)      -- Minimum duration
```

## ASSESSMENT APPLICABILITY

This session's content maps directly to the D7 summative assessment requirements:
- **WBS**: decompose the SAR project into work packages with unique identifiers
- **Network diagram**: PDM/AoN with forward pass, backward pass, float, CP identification
- **Gantt chart**: timeline with precedence relationships (FS, SS, FF, SF with lags)
- **Non-continuous working**: model weekends, lecture clashes, weather delays
- **Intra-team dependencies**: show how vision.py output feeds main.py, how Pi setup feeds integration testing
- **Resource scheduling**: single Pi as a constrained resource, laptop development parallelised
