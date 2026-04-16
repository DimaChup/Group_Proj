# PM2 -- Complete Extraction

> **Source**: "3 Project Management 2.pdf" (32 slides) + "3z Resource leveling task.xlsx"
> **Lecturer**: Mark Graham, 13 Oct 2025
> **Extracted**: 2026-04-16

---

## 1. Learning Objectives (Slide 5)

### Unit-level objective
> "2. work as a member of a team, **employing appropriate project management and planning tools to create, monitor and deliver a project plan**"

### Session-level objectives (7 total)
1. **Recall and discuss** the attributes of waterfall and agile project management approaches
2. **Create** a work breakdown structure
3. **Identify** task dependencies within a project
4. **Create** a network diagram from a list of task durations and task dependencies
5. **Create** a Gantt chart from a corresponding network diagram (or directly from a list of tasks and task dependencies)
6. **Identify** the critical path of a schedule and the float of any task within a network diagram or Gantt chart
7. **Critically analyse** a project schedule to **identify** risks and opportunities within the plan

---

## 2. Tuckman Model (Slides 2-4)

### The Five Stages

| Stage | Personal Relations | Task/Function | Emotions/Thoughts | Behaviours | Team Tasks |
|---|---|---|---|---|---|
| **Forming** | Dependency | Orienting | Expectation, anxiety, how to meet goals | Silence, lots of questioning, very polite | Discussing overall goals, setting rules and expectations |
| **Storming** | Tension | Organising | Anger, frustration, strong concerns about how to meet goals | Less polite discourse, critical language, less suppression of feelings & self | Exploring how work is done, breaking down large goals, smaller ones, finding problems in the team and systems |
| **Norming** | Cohesion | Sharing | More comfortable in expression of real feelings, see individuals' strengths and weaknesses and reality of the team | More frequent and open communication between members, constructive criticism welcomed. Team might develop its own culture, jokes, language | Productivity increases, a real plan starts to appear. Team begins to be able to assess and monitor its progress |
| **Performing** | Inter-dependence | Solving | Satisfaction, group awareness of strengths and weaknesses of group members | Team able to problem solve, difference between team members are utilised (and celebrated). Roles can become very fluid | High levels of team performance, progress is recognised. Making significant progress on team goals |
| **Transforming** | Disengagement | Transitioning | (project conclusion / disbanding) | | |

### Tuckman Scenarios (Slide 3)

Three timeline scenarios showing how stages can overlap:

- **Best-case**: F -> S -> N -> long P -> T (short storming, quick to performing)
- **Probable**: F -> S -> N -> P -> T (longer storming, moderate performing)
- **Worst-case**: F -> long S -> F -> S -> N -> P -> T (team regresses back to forming/storming before eventually reaching performing -- significantly delayed)

**Key insight**: Teams can regress. The worst-case shows a team cycling back through Forming and Storming before eventually reaching Performing, extending the overall timeline considerably.

---

## 3. Gantt Charts (Slides 6-16)

### Gantt Chart Principle (Slide 6)
- Horizontal axis = **time**
- Rows = **tasks**
- Arranged logically (tasks grouped according to dependency)
- Visual representation of the project schedule

### Equivalence: Table -> Network -> Gantt (Slides 7, 16, 18)

Worked example with 6 tasks:

| Activity | Predecessor | Duration (weeks) |
|---|---|---|
| A | (start) | 3 |
| B | (start) | 2 |
| C | A | 8 |
| D | B | 7 |
| E | B, C | 2 |
| F | D | 2 |

**Network diagram** (Activity-on-Arrow):
```
                    C (8)
        A(3)   1 ---------> 3    E(2)
       /                      \
  0 --                    dashed--> 5 (End, day 13)
       \                      /
        B(2)   2 ---------> 4    F(2)
                    D (7)
```

Node timings (forward pass):
- Node 0: time 0
- Node 1 (after A): time 3
- Node 2 (after B): time 2 -> but 4 (latest)
- Node 3 (after C): time 11
- Node 4 (after D): time 9 -> 11
- Node 5 (end): time 13

**Critical path**: A -> C -> E (total = 3 + 8 + 2 = 13 weeks)

The dashed line from node 3 to the B,C join represents a **dummy activity** showing the dependency of E on both B and C.

### Five Components of a Gantt Chart (Slides 8-15)

1. **Dependencies** (Slide 9) -- arrows connecting task bars showing predecessor relationships (Finish-to-Start links shown as green arrows)

2. **Critical path tasks** (Slide 10) -- highlighted/labelled with "CP"; tasks A, C, E are on the critical path. Any delay in these tasks directly delays the project end date.

3. **Float** (Slide 11) -- the amount of time a non-critical task can be delayed without affecting the project end date. Shown as the gap between the end of a task bar and the latest allowable finish. Tasks B, D, F have float; tasks A, C, E (critical path) have zero float.

4. **Project length** (Slide 12) -- the total duration from start to end milestone, determined by the critical path (13 weeks in the example = 21 Nov to 04 Dec).

5. **Milestones** (Slide 13) -- diamond markers at key dates (e.g., project end). Zero-duration events marking significant achievements.

**Summary slide** (Slide 14-15): All five components shown together with labels. Note: "Notice groupings of linked tasks" -- tasks naturally cluster into dependency chains.

### Optimising Your Plan Using Float (Slide 17)

In path B -> D -> F there is a **float of 2 days**. Options:
- Delay B by 2 days
- Delay B by 1 day and D by 1 day
- Use the float to level resources

**Key principle**: Float gives scheduling flexibility. Non-critical tasks can be moved within their float window to optimise resource usage, reduce peak demand, or manage risk.

---

## 4. Resource Levelling Task (Slides 19-26)

### Problem Statement (Slides 19-20)

**Context**: A torque link failed due to fatigue crack during a test programme. The company urgently needs to design, manufacture, measure, and assemble/test 3 new prototype parts:
- Steering sleeve
- Upper Torque Link
- Lower Torque Link

**Rules/Constraints**:
- 1 designer, 1 metrologist, 1 development engineer already available
- They have suggested they may need to get additional short-term contract staff to help ($$$$)
- **Only designers can design** (resource type: d)
- **Only metrologists can measure** (the newly made parts) (resource type: me)
- **Development engineers can assemble parts and complete the proof test** (resource type: dev)
- **All manufacturing is carried out sub-contract (outsourced)** and doesn't require any resource (resource type: ma)
- **Avoid breaking up a task** in sections as this is inefficient

### Normal Flow for a New Part (Slide 21)

Each part follows the same workflow:
```
Design new part -> Manufacture new parts -> Measure new parts -> Assemble -> Test
```

### 11 Tasks (Slide 20)

| Label | Task | Duration (days) | Resource |
|---|---|---|---|
| A | Design 'Steering sleeve' | 1 | d |
| B | Manufacture 'Steering sleeve' | 2 | ma (subcontracted) |
| C | Measure 'Steering sleeve' | 2 | me |
| D | Design 'Lower Torque Link' | 3 | d |
| E | Manufacture 'Lower Torque Link' | 4 | ma (subcontracted) |
| F | Measure 'Lower Torque Link' | 1 | me |
| G | Design 'Upper Torque Link' | 3 | d |
| H | Manufacture 'Upper Torque Link' | 9 | ma (subcontracted) |
| I | Measure 'Upper Torque Link' | 2 | me |
| J | Assemble all Parts | 1 | dev |
| K | Complete proof test of assembly | 3 | dev |

### Approach 1: Sequential / "Too Long" (Slide 23)

Tasks done one part at a time sequentially (sleeve first, then lower torque link, then upper torque link, then assemble, then test):
- A -> B -> C -> D -> E -> F -> G -> H -> I -> J -> K

**Result**: Duration = **22 days**. No extra staff needed (never more than 1 of any resource on any day).

Resource tracker shows max 1 designer, 1 metrologist, 1 dev engineer at any time.

**Conclusion**: Too slow. Inefficient use of time -- resources sit idle while manufacturing is subcontracted.

### Approach 2: "Do Everything As Early As Possible" (Slide 24)

All three parts start design in parallel. Tasks scheduled at earliest possible start:
- Day 1: Design Upper (G) + Design Lower (D) + Design Sleeve (A) -- **all in parallel**
- Manufacturing starts as soon as each design finishes
- Measurement starts as soon as each part is manufactured

**Result**: Duration = **18 days** (4 days saved). BUT:
- **Designer demand on Day 1**: 3 designers needed simultaneously (A, D, G all start Day 1)
- Day 2: 2 designers needed
- **Extra design staff needed** -- must hire 2 additional contract designers

Resource tracker: Designers peak at 3 (Day 1), 2 (Days 2-3). Metrologists peak at 2 on some days.

**Conclusion**: Faster but expensive -- need to hire extra staff.

### Approach 3: Resource Levelling Pass 1 (Slide 25)

**Use the float to permit resource levelling**. Shift non-critical design tasks to avoid parallel designer demand:

Strategy: Stagger the design tasks so only 1 designer is needed at a time:
- G (Design Upper Torque Link): Days 1-3
- D (Design Lower Torque Link): Days 1-3 (parallel with G -- still needs 2 designers on some days)
- A (Design Steering Sleeve): shifted later using float

**Result**: Duration = **18 days** (same as Approach 2). Only **1 extra metrologist needed** (improvement over Approach 2 which needed extra designers).

### Approach 4: Resource Levelling Pass 2 (Slide 26)

Further refinement -- shift tasks within their float windows to completely eliminate the need for extra staff:

**Result**: Duration = **18 days**. **No additional resource needed at all**.

**Key insight**: By carefully sequencing tasks within their float windows, the project achieves the same 18-day duration as the "everything ASAP" approach but with ZERO extra staff. This is the power of resource levelling.

### Resource Levelling Summary

| Approach | Duration | Extra Staff | Cost Implication |
|---|---|---|---|
| Sequential | 22 days | None | Slow, inefficient |
| All ASAP | 18 days | 2 extra designers | Fast but expensive |
| Levelled Pass 1 | 18 days | 1 extra metrologist | Better |
| **Levelled Pass 2** | **18 days** | **None** | **Optimal** |

---

## 5. Rolling Wave Planning (Slides 27-28)

### Deterrents to Planning (and Responses)

| Excuse | Response |
|---|---|
| "I don't have enough detail to plan" | **Start planning anyway** |
| "I have no idea about the durations of tasks" | **That's normal. Just guesstimate.** |
| "I only know any detail about the immediate tasks" | **Of course -- that's called rolling wave planning** |

### Rolling Wave Planning Explained (Slide 28)

A hierarchical decomposition of time, where near-term work is planned in detail and far-term work is left at a higher level:

```
2023 -------------------- 2052
  Get degree
    Yr 1 -> Yr 2 -> Yr 3       1st job       Buy house
      TB1 -> TB2
        Week 9 -> Week 10 -> Week 11 -> Week 12
          Monday -> Tuesday
            Travel to uni
              Meet team
                Study X                    Order the curtains
```

**Principle**: You plan in fine detail for the immediate future (what you're doing this week, today) and in progressively coarser detail for the distant future. As time passes, the "wave" of detailed planning rolls forward. This is natural -- nobody plans their entire life in hourly increments.

---

## 6. Anti-Patterns & Warnings (Slides 29-32)

### "Museum of Mediocrity" (Slide 29)
A warning against poor-quality work. Image of a pigeon at a mediocre display. Message: don't produce mediocre project plans.

### "A Group of Individuals != a Team" (Slides 30-31)

Two metaphors:
1. **"Lone Genius"** (Slide 30) -- castle image. Working in isolation, building your own fortress. Individuals working separately don't form a team.
2. **"Drifting along, drifting alone"** (Slide 31) -- people on a raft labelled "Structures", "Quality", "Aero", "PM" each paddling their own direction. **Time** is the shark circling. Message: without coordination, the team drifts and time runs out.

### "Delaying Planning and Design Work" (Slide 32)

Image of a skeleton at a bus stop with caption: **"I'll start when I have all the information"**

**Message**: Waiting for perfect information before starting to plan is a fatal mistake. You will never have all the information. Start planning now with what you know (rolling wave planning). Perfection is the enemy of progress.

---

## 7. Excel Resource Levelling Task -- Detailed Extraction

### Sheet 1: "Resource scheduling"

**Gantt-style grid** with:
- Rows: Tasks A through K
- Columns: Days 1-25
- Each cell contains a resource code from a dropdown: d (designer), ma (manufacturer), me (metrologist), dev (development engineer)
- Resource tracker at bottom counts how many of each resource type is needed per day

**Colour coding**:
- Yellow/Gold: designer (d)
- Green: manufacturer (ma) -- subcontracted, no internal resource
- Blue: metrologist (me)
- Light green/teal: development engineer (dev)

### Sheet 2: "Tasks and Durations"

The 11 tasks listed (not in dependency order -- students must determine the correct order):

| Task Description | Duration (days) |
|---|---|
| Manufacture new 'Upper Torque Link' | 9 |
| Measure new 'Lower Torque Link' | 1 |
| Complete proof test of final assembly | 3 |
| Measure new 'Steering sleeve' | 2 |
| Design new 'Steering sleeve' | 1 |
| Measure new 'Upper Torque Link' parts | 2 |
| Manufacture new 'Lower Torque Link' | 4 |
| Design new 'Lower Torque Link' | 3 |
| Design new 'Upper Torque Link' | 3 |
| Manufacture new 'Steering sleeve' | 2 |
| Assemble all new Parts | 1 |

**Key exercise requirements**:
1. Decide on the dependencies (which tasks come first?)
2. Create a Gantt chart using the Excel sheet
3. Determine the minimum time the project can be done
4. Determine any resources needed
5. Validate or reject the engineering team's request for more staff
6. Upload a screenshot of your plan onto the Padlet

---

## 8. Mapping to Apollo's SAR Drone Project

### 8.1 Resource Levelling in the SAR Project

**Direct parallel**: The SAR drone project had similar resource constraints:
- **Limited hardware**: 1 Raspberry Pi, 1 Cube flight controller, 1 camera -- analogous to having 1 designer, 1 metrologist
- **Subcontracted manufacturing**: Just as manufacturing was outsourced in the torque link task, **model training was "outsourced" to Google Colab** (external GPU compute), freeing the team to work on other tasks in parallel
- **Resource types map directly**:
  - Designer (d) = Software developer writing code on laptop
  - Metrologist (me) = Testing/calibration engineer running bench tests on Pi
  - Development engineer (dev) = Integration engineer assembling full system
  - Manufacturer (ma) = Colab GPU training (no local resource needed)

**Resource levelling applied**: The project used the "staggered start" approach (Pass 2). While model training ran on Colab (subcontracted, no local resource), the team could work on flight test scripts, documentation, and hardware setup in parallel. This is exactly the resource levelling principle -- using float in the manufacturing/training path to keep human resources continuously productive.

### 8.2 Critical Path in the SAR Project

The project's critical path was:
```
Vision pipeline development -> Pi hardware integration -> Field calibration -> Flight testing
```

Non-critical paths with float included:
- Documentation (could be delayed without affecting flight readiness)
- Dashboard development (independent, used float extensively)
- Unit test writing (done in parallel during manufacturing/training "wait" periods)

### 8.3 Rolling Wave Planning Applied

The SAR project naturally used rolling wave planning:
- **Near-term (Week 1-2)**: Detailed task breakdown -- specific Python scripts, exact test sequences, line-by-line code changes
- **Mid-term (Week 3-4)**: Module-level planning -- "complete vision pipeline", "integrate with Pi"
- **Far-term (Month 2+)**: High-level goals -- "achieve autonomous flight", "write report"

This mirrors the lecture's hierarchy: Year -> Term -> Week -> Day -> Hour.

### 8.4 Gantt Chart Usage

The project maintained a **WBS (Work Breakdown Structure)** in the dashboard (`dashboard/src/pages/wbs-data.ts`) that functioned as a living Gantt chart equivalent, tracking:
- Task dependencies
- Progress percentages
- Milestone dates (D5, D6, D7 deliverables)

### 8.5 Tuckman Model Applied

The 5-person team progressed through Tuckman's stages:
- **Forming**: Initial role assignment, politeness, "what are we doing?"
- **Storming**: Disagreements on architecture choices (monolithic vs modular), frustration with hardware delays
- **Norming**: Established Git workflow, agreed on testing progression (bench -> passive -> autonomous)
- **Performing**: Parallel workstreams running efficiently, team members cross-contributing
- **Transforming**: Report writing phase, knowledge transfer documentation

---

## 9. Weaponisable Quotes for D7

### From the Slides

> "Employing appropriate project management and planning tools to create, monitor and deliver a project plan" (Slide 5 -- unit learning objective)

> "Critically analyse a project schedule to identify risks and opportunities within the plan" (Slide 5, Objective 7)

> "Notice groupings of linked tasks" (Slide 15 -- on Gantt chart structure)

> "I'll start when I have all the information" (Slide 32 -- anti-pattern warning)

> "Start planning anyway" / "That's normal. Just guesstimate." / "Of course -- that's called rolling wave planning" (Slide 27 -- responses to planning deterrents)

> "A group of individuals is not a team" (Slides 30-31)

> "Drifting along, drifting alone" (Slide 31 -- anti-pattern of uncoordinated individual work)

### Constructed from Lecture Content

> "Resource levelling allows a project to achieve the same duration as the 'everything ASAP' approach but with zero additional staff, by exploiting float in non-critical paths." (From Slides 23-26 comparison)

> "The critical path determines the minimum project duration; float on non-critical tasks provides scheduling flexibility for resource optimisation." (From Slides 10-11, 17)

> "Rolling wave planning acknowledges that detailed planning is only possible for near-term work, while distant work remains at a higher level of abstraction." (From Slides 27-28)

---

## 10. Hatton L4 Moves

### L4 = Critical Evaluation / Synthesis

**Move 1: Evaluate resource levelling trade-offs in your own project**
"In our SAR drone project, we faced a resource levelling challenge analogous to the torque link exercise: with only one Raspberry Pi available, we could not run camera calibration and flight controller bench-testing simultaneously. By identifying that model training could be 'subcontracted' to Google Colab (requiring no local hardware), we freed the Pi for calibration work during training runs. This mirrors the lecture's Pass 2 solution -- achieving the optimal 18-day schedule without additional resources by exploiting the float in the training path."

**Move 2: Critically assess the limitations of Gantt charts for agile/iterative projects**
"While the Gantt chart proved effective for visualising our hardware integration critical path (Pi setup -> camera test -> Cube connection -> flight test), it was less suitable for the iterative software development workstream where tasks like 'refine detection algorithm' had no fixed duration and were revisited multiple times. This suggests that for hybrid projects combining hardware and software, a dual-track approach -- Gantt for hardware milestones, Kanban for software iterations -- provides better visibility than either tool alone."

**Move 3: Synthesise Tuckman with rolling wave planning**
"Our team's progression through Tuckman's stages directly influenced our planning granularity. During Forming and Storming (weeks 1-3), we could only plan at the module level because roles and responsibilities were still being negotiated. As we reached Norming and Performing, our planning resolution naturally increased -- we could schedule specific test scripts to specific days because team members had established reliable working patterns. This suggests that rolling wave planning is not merely a response to information uncertainty but also to team maturity: detailed planning requires the stable working relationships that only emerge in the Norming/Performing stages."

**Move 4: Evaluate the critical path under uncertainty**
"The lecture identifies the critical path as the sequence determining minimum project duration. However, in our project, the critical path shifted dynamically: initially it ran through software development, but after a weather cancellation delayed outdoor flight testing, the critical path pivoted to hardware validation. This aligns with the lecture's Objective 7 -- 'critically analyse a project schedule to identify risks' -- and demonstrates that critical path analysis must be a continuous monitoring activity, not a one-time calculation."

**Move 5: Challenge the "everything ASAP" assumption**
"The resource levelling exercise demonstrates that scheduling all tasks at their earliest start date (Approach 2) creates a peak resource demand of 3 designers on Day 1 -- a 200% overallocation. In our project, we observed an analogous pattern: attempting to parallelise all five team members' workstreams simultaneously in Week 1 created bottlenecks on shared resources (the single Pi, the shared Git repository). By deliberately staggering starts -- mirroring the lecture's Pass 2 levelling -- we achieved the same overall timeline with fewer integration conflicts."

---

## 11. Key Concepts Summary

| Concept | Definition | Lecture Source |
|---|---|---|
| **WBS** | Work Breakdown Structure -- hierarchical decomposition of project scope into tasks | Slide 5, Obj 2 |
| **Network Diagram** | Graph showing task dependencies and durations (Activity-on-Arrow or Activity-on-Node) | Slides 7, 16 |
| **Gantt Chart** | Bar chart with time on horizontal axis, tasks on vertical axis, showing schedule | Slides 6-16 |
| **Critical Path** | Longest path through the network; determines minimum project duration | Slides 10, 16 |
| **Float (Slack)** | Time a non-critical task can be delayed without affecting the end date | Slides 11, 17 |
| **Milestone** | Zero-duration marker for a key project event | Slide 13 |
| **Resource Levelling** | Adjusting the schedule within float to smooth resource demand | Slides 23-26 |
| **Rolling Wave Planning** | Progressive elaboration -- detail near-term, abstract far-term | Slides 27-28 |
| **Tuckman Model** | Forming -> Storming -> Norming -> Performing -> Transforming | Slides 2-4 |
| **Dependencies** | Predecessor relationships constraining task start times (typically Finish-to-Start) | Slides 7, 9 |

---

## 12. Network Diagram Calculation Method (from Slide 16)

### Forward Pass (Earliest Start/Finish)

```
Node 0 (Start):     ES = 0
Node 1 (after A):   ES = 0 + 3 = 3
Node 2 (after B):   ES = 0 + 2 = 2
Node 3 (after C):   ES = 3 + 8 = 11
Node 4 (after D):   ES = 2 + 7 = 9  --> but must wait for dummy from node 3? 
                     Actually: 11 (taking the max of all predecessors)
Node 5 (End):       ES = max(11 + 2, 11 + 2) = 13
```

### Critical Path Identification
- Path A-C-E: 3 + 8 + 2 = **13** (longest = critical)
- Path B-D-F: 2 + 7 + 2 = **11** (float = 13 - 11 = 2)

### Float Calculation
- Tasks on critical path (A, C, E): Float = 0
- Tasks on non-critical path (B, D, F): Float = 13 - 11 = **2 weeks**

---

## 13. Relationship Between the Three Representations

The lecture emphasises that **Table, Network Diagram, and Gantt Chart are three equivalent representations** of the same information (Slide 18):

```
Table (task list)  <===>  Network Diagram  <===>  Gantt Chart
```

- **Table**: Best for listing tasks, durations, dependencies -- good for data entry
- **Network**: Best for calculating critical path, float, earliest/latest times -- good for analysis
- **Gantt**: Best for visual communication of the schedule to stakeholders -- good for reporting

Each can be derived from the others. The skill is knowing when to use which representation.
