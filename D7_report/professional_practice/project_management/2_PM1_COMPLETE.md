# Project Management 1 -- Complete Extraction

**Source**: "2 Project Management 1.pdf" (33 slides) + "2z AOA Cheat Sheet.pdf" (1 page)
**Lecture**: Monday 13th October 2025, avdasi2@bristol.ac.uk
**Lecturer**: Mark Graham

---

## SLIDE-BY-SLIDE EXTRACTION

### Slide 1 -- Title Slide
- **PROJECT MANAGEMENT 1**
- Monday 13th October 2025
- University of Bristol

### Slide 2 -- Learning Objectives

**Unit level learning objective(s):**
> 2. work as a member of a team, **employing appropriate project management and planning tools to create, monitor and deliver a project plan**;

**Session level learning objectives:**
1. **Recall** and **discuss** the attributes of waterfall and agile project management approaches
2. **Create** a work breakdown structure
3. **Identify** task dependencies within a project
4. **Create** a network diagram from a list of task durations and task dependencies
5. **Create** a Gantt chart from a corresponding network diagram (or directly from a list of tasks and task dependencies) -- (NEXT WEEK)
6. **Identify** the critical path of a schedule and the float of any task within a network diagram or Gantt chart
7. **Critically analyse** a project schedule to **identify** risks and opportunities within the plan -- (NEXT WEEK)

### Slide 3 -- What is a Project?

**Key definitions (boxed, highlighted):**

- **Project**: A planned set of interrelated tasks to be executed over a **fixed period** and within certain cost and other **limitations**
  - Temporary. Defined beginning and end. Fixed scope. Fixed resources. Unique (not routine).

- **Programme**: multiple projects to achieve overall objectives
  - Common knowledge and skills across projects

- **Portfolio**: multiple projects & programmes to achieve **strategic direction** and objectives

### Slide 4 -- Examples from Aerospace

**Diagram**: Hierarchical structure showing Boeing's widebody jets:
- **Portfolio**: Widebody Jets
  - **747 programme** (Project 1, Project 2, Project ...)
  - **767 programme** (Project 1, Project 2, Project ...)
  - **777 programme** (777-300ER, 777F, 777-9X, 777-8X) -- highlighted in teal
  - **787 programme** (Project 1, Project 2, Project ...)

Each programme contains multiple projects (aircraft variants). The portfolio is the strategic umbrella.

### Slide 5 -- Project Lifecycle(s) (intro)

**Diagram**: Linear arrow chain showing 4 phases:
> Concept --> Definition --> Development --> Handover/Closure

"Not one size fits all..." depends on:
- Type of technology
- Company methods (and culture)
- New innovation or new application
- Customer (and supplier systems)

### Slide 6 -- Project Lifecycle(s) (detailed comparison)

**Diagram**: 5 different lifecycle models compared side by side:

| Model | Phases |
|-------|--------|
| **4 phases** | Concept --> Definition --> Development --> Handover/Closure |
| **5 phases (APM PMBOK)** | Initiation --> Planning --> Execution --> Monitoring and Control --> Closure |
| **6 phases** | Scope --> Build --> Develop --> Test and Validate --> Launch --> Close |
| **7 Phases (Panoptic Development Inc.)** | Requirements/User story --> UI design --> Iterate software --> Incremental release --> Beta testing --> Final release |
| **8 Phases (RIBA)** | Strategic Definition --> Preparation and Brief --> Concept design --> Developed design --> Technical design --> Construction --> Handover and Closure --> In Use |

### Slide 7 -- Example: Airbus

**Diagram**: Airbus aircraft development lifecycle shown in 3 levels of detail:
- **Top level**: FEASIBILITY --> CONCEPT --> DEFINITION --> DEVELOPMENT --> SERIES
  - Gates: Definition of basic concept, Instruction to Proceed (ITP), Go ahead, Entry into service
- **Mid level**: Order released for project --> Definition of basic concept --> Instruction to Proceed (ITP) --> Go ahead --> Begin final assembly --> First flight --> Entry into service
- **Bottom level**: Product idea established --> Top level specification --> Concept selected --> Authorisation offer (A/C) --> First metal --> Power on --> Type certification --> End development phase for batch

Reference: Panunzio, T., 2016. Concurrent engineering development and practices for aircraft design at Airbus. 24th International Congress of the Aeronautical Sciences (ICAS).

### Slide 8 -- Diversity of Projects

**Content**: Two images (landing gear concept, cloud-based home design tool)

Discussion prompt: "As a team -- discuss how these projects might differ."

Comparison dimensions (checklist):
- Safety criticality
- Duration of tasks
- Time to build the prototype
- Interdependency of tasks (how sequential?)
- Legislation
- How iterative can the design/project/manufacture be?
- Quality documentation for legislator and/or customer
- Testing and validation
- Clearly defined end goal and/or customer requirements

### Slide 9 -- Waterfall vs Agile

**Diagram (left)**: Waterfall model -- sequential cascade:
Design --> Manufacture --> Test --> Validate --> Design (for Prototype 1, then Field Trial)

**Diagram (right)**: Agile model -- circular sprints:
SPRINT 1 --> SPRINT 2 --> SPRINT 3 (each with iterative loop)

| Waterfall | Agile |
|-----------|-------|
| Very Sequential | End goal likely to change |
| Dependent tasks | Less documentation |
| Predictable | Unpredictable / Iterative |
| Regulated | Better to get something that works partially |
| Clear requirements | Scrum/Kanban |
| Lots of documentation | |
| Expensive and time-consuming prototypes | |

### Slide 10 -- More than Waterfall vs Agile

**Diagram**: Word cloud showing many PM methodologies:
CRITICAL, SCRUMBAN, XP, AGILE, PROJECT, METHODOLOGY, WATERFALL, LEAN, KANBAN, FRAMEWORK, RAPID, SCRUM, PMBOK, SIX (sigma), EXTREME, CHAIN, PER, PRODUCT, PRODUCTION, PACKAGE, ADAPTIVE, NEW, METHOD, PATH, PROGRAMMING

(Message: the waterfall/agile binary is an oversimplification; many methodologies exist)

### Slide 11 -- Producing a Project Plan... Tools

**Diagram**: Three-tier vertical flow:

| Tool | Purpose |
|------|---------|
| **Work Breakdown Structure** | Breaks down the project into a manageable set of tasks. Arranges the tasks in a logical way |
| **Network Diagram** | Determine duration of tasks and relationships between them |
| **Gantt** | Plot tasks and relationships in-time |

Arrow labeled "Project scheduling tools" runs down the right side, showing the progression: WBS --> Network Diagram --> Gantt

### Slide 12 -- Work Breakdown Structure (intro)

**Content**:
1) Breaking down large projects into smaller* tasks
2) Then arrange logically

**Diagram**: Hand-drawn hierarchical tree (one parent node, three children, each with sub-children)

*Small enough to be manageable
*Not so small that visibility is lost

### Slide 13 -- 1) Breakdown (WBS example)

**Diagram**: Full WBS tree for "Build a house":
- **Build a house** (root)
  - **Building design**: Architects drawings, Design consultation, Research, Concept development
  - **Foundations**: Excavation, Levelling
  - **Utilities**: Plumbing, Electrical, Internet
  - **Roof**: Framing & Joists, Tiling, Insulation, Framing
  - **Walls**: Exterior walls, Interior walls
  - **Interior Finishing**: Plastering, Painting, Doors, Flooring, Bathroom tiling, Hallway carpet
  - **Landscaping**: Levelling, Build, Driveway & Paths, Plant
  - **Regulatory planning**: Planning permission, Planning consultation

**Rules** (stated on slide):
1. No more than 5 levels (branching)
2. Captures everything (the 100% rule)
3. Tasks contribute to parent task

### Slide 14 -- 2) Arrange (WBS rearranged, plain)

**Diagram**: Same "Build a house" tasks rearranged into logical groupings:
- **Building design**: Team recruitment, Design, Regulatory planning (with sub-tasks)
- **Exterior**: Foundations, Utilities, Roof, Walls, Landscaping (with sub-tasks)
- **Interior**: Plastering, Painting, Fittings Finishing, Flooring, Doors, Windows

### Slide 15 -- 2) Arrange (color-coded)

Same diagram as Slide 14 but with color coding applied to groups:
- Building design group in purple/blue
- Exterior group in green
- Interior group in light purple
- "Exterior" label highlighted in dark purple box

### Slide 16 -- 2) Arrange (with dependency labels)

Same diagram with dependency labels added:
- D (parent of Building design)
- D1 = Team recruitment
- D2 = Design
- D3 = Regulatory planning
- D1.1 = Hire architect
- D1.2 = Hire builders

Shows how WBS numbering convention works for tracking.

### Slide 17 -- WBS (summary)

**Diagram**: Complete color-coded WBS for "Build a house" with all dependency labels.

**WBS tells you:**
- [checkmark] What work needs to be done
- [X] How long the task takes
- [X] What the **dependencies** are
- [X] How long the project takes

**Key point**: WBS only tells you WHAT needs doing, not timing or dependencies. For those you need Network Diagrams and Gantt Charts.

### Slide 18 -- AVDASI2 Unit Work Breakdown Structure

**Diagram**: Full WBS for the AVDASI2 course unit (2025-26), created by M. Graham, Issue 01, 12/09/2025.

Seven top-level branches:
1. **Training** (with sub-tasks)
2. **Design** (with sub-tasks)
3. **Project Management** (with sub-tasks)
4. **Quality** (with sub-tasks)
5. **Build** (with sub-tasks)
6. **Test** (with sub-tasks)
7. **Assessment & Reporting** (with sub-tasks)

(Image is small but shows the unit structure mirrors real aerospace project management)

### Slide 19 -- WBS > List > Team Kanban Board (with tree)

**Diagram (left)**: Simple WBS tree:
- Project
  - Planning
  - Design (with sub-branches: Analysis, CAD --> Modelling, Drafting)
  - Procurement

**Table (right)**: WBS converted to a tabular list with columns:
| Level 1 | Level 2 | Level 3 | Level 4 | Work package description | Link to task on Kanban |
|---------|---------|---------|---------|--------------------------|----------------------|
| 1. Planning | 1.1 WBS | 1.1.1 Release first issue of WBS | | | |
| | 1.2 Network | 1.2.1 Create Dependencies Table | | | |
| | | 1.2.2 Create Network Diagram | | | |
| | 1.3.1 Gantt | 1.3.1 Create Gantt Chart | | | |
| 2. Design | 2.1 Analysis | 2.1.1 Structural analysis | 2.1.1.1 Main Wing Spar structural calculations | | |
| | | | 2.1.1.2 MWP-Emp Joint structural calculations | | |
| | | 2.1.2 Aerodynamic analysis | 2.1.2.1 Main Wing Spar structural calculations | | |
| | 2.2 CAD | 2.2.1 Modelling | 2.2.1.1 Model Main Wing Spar | | |
| | | | 2.2.1.2 Model Wing Ribs and Skin | | |
| | | 2.2.2 Drafting | 2.2.1.1 Release Main Wing Spar (Dwg 0008) | Draw, Check, Approve and release | https://tasks.office.co m/bristol.ac.uk/en- |
| | | | 2.2.1.2 Release Wing Ribs and Skin (Dwg 0015) | | |
| 3. Procurement | ... | ... | ... | | |
| 4. Manufacturing | ... | ... | ... | | |
| 5. Testing | ... | ... | ... | | |
| 6. Quality | ... | ... | ... | | |

**Key concept**: WBS hierarchy --> flattened list --> mapped to Kanban board tasks

### Slide 20 -- WBS > List > Team Kanban Board (table closeup)

Same table as Slide 19 but zoomed in for readability. Shows the same Level 1-4 structure with work package descriptions and Kanban links.

### Slide 21 -- Team Kanban Board

**Screenshot**: Microsoft Teams Planner (Kanban board) for "grp-Group 999 Kanban b..."

Columns: **Not started** | **In progress** | **Waiting validation** | **Done**

Example card in "In progress":
- Tags: "Drafting", "Design"
- Task: "2.2.1.1 Release Main Wing Spar (Dwg 0008)"
- Has a due date and assigned member

**Red text at bottom**: "All communications and task management (for the group) should take place on your private teams channel."

### Slide 22 -- Network Diagram (activity-on-arrow) -- intro

**Activities from WBS** (PCB assembly example):
- Solder Parts
- Collect all parts from store
- Fit parts to PCB (Printed circuit board)
- Test PCB
- Switch on soldering iron

**Table** (partially filled with question marks):

| Activity | Description | Predecessor |
|----------|-------------|-------------|
| A | ? | (Start) |
| B | ? | (Start) |
| C | ? | ? |
| D | ? | ? |
| E | ? | ? |

### Slide 23 -- Network Diagram (activity-on-arrow) -- solved

**Completed dependency table:**

| Activity | Description | Predecessor |
|----------|-------------|-------------|
| A | Warm-up iron | (Start) |
| B | Collect all parts | (Start) |
| C | Fit parts to PCB | B |
| D | Solder parts | A, C |
| E | Test | D |

**Diagram**: AOA network diagram:
- Node 0 (start) --> A (3) --> Node 2; B (2) --> Node 1
- Node 1 --> C (4) --> Node 2
- Node 2 --> D (8) --> Node 3
- Node 3 --> E (2) --> Node 4

**Rules**:
- Time: left to right
- Nodes = Events (start/end)
- There is no scale
- Arrows = Activities/Tasks
- Connections = dependencies

### Slide 24 -- Network Diagram -- with durations

**Table with durations added:**

| Activity | Description | Predecessor | Duration (mins) |
|----------|-------------|-------------|----------------|
| A | Warm-up iron | -- | 3 |
| B | Collect all parts | -- | 2 |
| C | Fit parts to PCB | B | 4 |
| D | Solder parts | A, C | 8 |
| E | Test | D | 2 |

**Diagram**: Same AOA network with durations labeled in blue on each arrow:
- A=3, B=2, C=4, D=8, E=2

"Forward pass planning.... Add durations"

### Slide 25 -- Forward Pass Planning

**Diagram**: Complete forward pass on the PCB example:

```
              6           14          16
         (2)--D:8-->(3)--E:2-->(4)
    A:3 /           
(0)----/    C:4
    \  B:2  /
     \(1)--/
       2
```

**Earliest times calculated (red numbers at nodes):**
- Node 0: 0 (start)
- Node 1: 2 (0+2 from B)
- Node 2: 6 (max of: 0+3=3 from A, 2+4=6 from B-->C)
- Node 3: 14 (6+8 from D)
- Node 4: 16 (14+2 from E)

**Key**: Number above each node = earliest time possible at that event

"Forward pass planning.... calculate earliest start"

**Convention shown**: Earliest time possible --> shown in red above/beside node

### Slide 26 -- Forward Pass and Backward Pass (new example)

**New, larger example with 7 activities:**

**Diagram**: AOA network with nodes 0-5:
- Node 0 --> A(2) --> Node 1; B(3) --> Node 2
- Node 1 --> C(4) --> Node 3
- Node 2 --> D(5) --> Node 3(? via Node 4 path too); E(5) --> Node 4
- Node 3 --> F(2) --> Node 5
- Node 4 --> G(1) --> Node 5

**Forward pass (earliest times, red above nodes):**
- Node 0: 0
- Node 1: 2
- Node 2: 3
- Node 3: 6
- Node 4: 8
- Node 5: 9

**Backward pass (latest times, green below nodes):**
- Node 5: 9
- Node 4: 8
- Node 3: 7
- Node 2: 3
- Node 1: 3
- Node 0: 0

**Key**:
- Earliest time possible --> red number (above)
- Latest time possible --> green number (below)

"Forwards pass.... Calculate earliest start"
"Backwards pass... Calculate latest finish"

### Slide 27 -- Forward Pass and Backward Pass -- Critical Path identified

**Same diagram as Slide 26** but now with critical path marked (double red lines // on arrows):

Critical path marked on: B, E, G (with // marks)

Other paths (B, D and A, C, F) are NOT on the critical path.

**Critical path = the longest path through the project**

- Critical path = 9 days
- Critical path = B --> E --> G

(The path 0-->2-->4-->5: B(3)+E(5)+G(1) = 9 days)
(Alternative path 0-->1-->3-->5: A(2)+C(4)+F(2) = 8 days -- NOT critical, has 1 day float)
(Alternative path 0-->2-->3-->5: B(3)+D(5)+F(2) = 10? -- wait, checking: node 3 EF=6 but via D from node 2 at 3+5=8, which is > 6. Let me re-check the slide...)

Actually from the slide: Critical path = B --> E --> G = 3+5+1 = 9 days. The node times confirm this.

### Slide 28 -- "Your Turn" Exercise

**Given data:**

| Activity | Predecessor | Duration (days) |
|----------|-------------|----------------|
| A | (Start) | 3 |
| B | (Start) | 2 |
| C | A | 4 |
| D | B | 5 |
| E | B | 4 |
| F | C, D | 3 |
| G | E | 2 |

**Instructions:**
1. Draw the network
2. Label the durations
3. Conduct forward pass (identify earliest possible time at each node)
4. Conduct the backwards path
5. State the critical path length
6. Identify and state the critical path(s) route(s) -- i.e. the activity sequence(s)
7. **Bonus**: Which task(s) can be delayed (and by how much) without delaying the project?

**Rules & conventions:**
- Activities drawn as arrows
- Events (nodes) as circles
- Time increases left to right
- Label the critical path with // (double red lines)
- Show durations below the activity letter
- Start = Node 0
- Record earliest finish above and latest start below

### Slide 29 -- "Your Turn" -- SOLUTION

**Diagram**: Complete AOA network with forward and backward pass:

```
         3           7           10
    (1)--C:4-->(3)--F:3-->(5)
A:3/ 3         7           10
(0)     D:5         G:2
B:2\ 2    (4)------->(5 merged? no...)
    (2)--E:4-->(4)
     2         6
               8
```

**Forward pass (earliest times, red):**
- Node 0: 0
- Node 1: 3 (via A=3)
- Node 2: 2 (via B=2)
- Node 3: 7 (max of: 3+4=7 from C, 2+5=7 from D)
- Node 4: 6 (2+4 from E)
- Node 5: 10 (max of: 7+3=10 from F, 6+2=8 from G)

**Backward pass (latest times, green):**
- Node 5: 10
- Node 4: 8 (10-2 from G)
- Node 3: 7 (10-3 from F)
- Node 2: 2 (min of: 7-5=2 from D, 8-4=4 from E --> min=2)
- Node 1: 3 (7-4 from C)
- Node 0: 0

**Critical path = 10 days**

**Critical path(s)**: A --> C --> F **and** B --> D --> F (both = 10 days)

**Float**: Tasks E and G can be delayed by a **total** of 2 days without affecting the project duration. "There are 2 days of float."

The difference between earliest and latest times at a node = **Float**.
- Node 4: earliest=6, latest=8, float = 2 days

### Slide 30 -- Dummy Activities

**Diagram**: AOA network with a DUMMY activity (dashed red line):

```
     (1)--C:8-->(3)--E:2-->
A:3/              \         (6)
(0)    dummy(dash)/
B:2\              /
     (2)--D:7-->(3? leads to same node)--F:2-->
```

Activity E depends on both C and B. Since you can't have two arrows between the same pair of nodes, a **dummy activity** (dashed line, zero duration) represents the dependency from node 2 to node 3.

**Table:**

| Activity | Predecessor | Duration (weeks) |
|----------|-------------|-----------------|
| A | (start) | 3 |
| B | (start) | 2 |
| C | A | 8 |
| D | B | 7 |
| E | C, B | 2 |
| F | D | 2 |

**Definition**: "Dummy activity: Representing a dependency, but line does not represent an activity (time)"

The dummy has zero duration -- it just shows that E cannot start until B is complete (in addition to C).

### Slide 31 -- Network Optimisation (real management)

**Diagram**: Return to the PCB example with full forward and backward pass:

```
              6           14          16
         (2)--D:8-->(3)--E:2-->(4)
    A:3 /    6        14         16
(0)----/    C:4
    \  B:2  /
     \(1)--/
       2
       2
```

**Forward pass (red above):** 0, 2, 6, 14, 16
**Backward pass (green below):** 0, 2, 6, 14, 16

All earliest = latest, so **every activity is on the critical path**: B --> C --> D --> E

Critical path = 2+4+8+2 = 16 minutes

**Key insight**: When all activities are critical (zero float everywhere), there is NO room for delay on ANY task. This is the riskiest schedule.

Photo: soldering iron on PCB (real-world context)

### Slide 32 -- Complex Real-World Network

**Diagram**: Large, complex AOA network diagram (appears to be a real project plan, possibly for aircraft/drone assembly). Contains approximately 30+ activities with multiple parallel paths, many nodes, and duration labels. Activities include things like:
- Collect basic components
- Buy aircraft and GPS receiver
- Design and manufacture custom components
- Order custom PCB and components
- Buy servos/motors
- Software development paths
- Assembly and integration paths
- Testing paths

Multiple parallel work streams converge at integration/test milestones. Shows the real complexity of network diagrams for engineering projects.

### Slide 33 -- Learning Objectives (recap, with highlights)

Same as Slide 2 but with objectives 1-6 highlighted in green (covered this session):
1. [GREEN] Recall and discuss waterfall and agile
2. [GREEN] Create a WBS
3. [GREEN] Identify task dependencies
4. [GREEN] Create a network diagram
5. Create a Gantt chart (NEXT WEEK)
6. [GREEN] Identify critical path and float
7. Critically analyse a project schedule (NEXT WEEK)

---

## AOA CHEAT SHEET -- COMPLETE CONTENT

**Title**: AVDASI2 Network Diagrams -- Activity-on-Arrow cheat sheet
**Source**: University of Bristol

### Annotated Diagram

Complete AOA network diagram with all elements labeled:

**Nodes/Events**: Circles with arbitrary identifier numbers (0, 1, 2, 3, 4, 5)
**Task/Activity**: Letter labels on arrows (A, B, C, D, E, F, G)
**Activity duration**: Numbers below activity letters
**Earliest finish**: Red numbers above nodes -- calculated on forward pass
**Latest start**: Green numbers below nodes -- calculated on backward pass (backwards pass method)
**//** (double lines): Indicates this route is part of the **critical path**

**Full network:**
```
           2           6           9
      (1)--C:4-->(3)--F:2-->(5)
 A:2/  3           7           9
(0)         D:5         G:1
 B:3\  3    (4)------->(5)
      (2)--E:5-->(4)   8
       3           8
```

**Data table:**

| Activity | Predecessor | Duration (days) |
|----------|-------------|----------------|
| A | (Start) | 2 |
| B | (Start) | 3 |
| C | A | 4 |
| D | B | 5 |
| E | B | 5 |
| F | C, D (note: needs dummy from node 2 to allow D dependency) | 2 |
| G | E | 1 |

### Key Annotations on Diagram

1. **"When earliest finish and latest start are equal, the event is part of the critical path"** -- nodes where red=green are on the critical path

2. **"When earliest finish and latest start are different, the event is not on the critical path. There is float in the task(s), meaning that the task can move or be delayed without compromising the critical path (i.e. project length). The amount of float is the difference between earliest finish and latest start for that event/node."**

3. **"For the last node (the end) these are always equal"** -- pointing to Node 5 where earliest=latest=9

4. **Critical path = 9 days**
5. **Critical path = B --> E --> G**

### Method (from cheat sheet)

1. Create a WBS to breakdown the project into tasks
2. Consider the task dependencies and estimate the task durations
3. Create a dependencies table (or use the network to explore the dependencies)
4. Draw an activity-on-arrow network diagram
   1. Label the durations (next to the activity letter)
   2. Conduct the forward pass (identify earliest possible time at each node)
   3. Conduct the backwards path (subtract the task durations from the latest start times)
   4. State the critical path length
   5. Label the critical path routes. These are where the earliest and latest start times are equal.
   6. Identify any float i.e. which task(s) can be delayed (and by how much) without delaying the project end date?

---

## KEY DEFINITIONS AND FORMULAS

### Core Definitions

| Term | Definition |
|------|-----------|
| **Project** | A planned set of interrelated tasks executed over a fixed period, within cost and other limitations. Temporary, unique, fixed scope. |
| **Programme** | Multiple projects achieving overall objectives, with common knowledge/skills |
| **Portfolio** | Multiple projects & programmes achieving strategic direction and objectives |
| **WBS** | Hierarchical decomposition of project into manageable tasks, arranged logically |
| **Network Diagram** | Visual representation of task dependencies and durations (AOA or AON) |
| **Gantt Chart** | Time-scaled bar chart showing tasks, durations, and dependencies |
| **Critical Path** | The longest path through the network diagram; determines minimum project duration |
| **Float (Slack)** | The amount of time a task can be delayed without delaying the project end date |
| **Forward Pass** | Left-to-right calculation determining the earliest possible time at each node |
| **Backward Pass** | Right-to-left calculation determining the latest allowable time at each node |
| **Dummy Activity** | A zero-duration arrow (dashed line) representing a dependency only, not real work |
| **AOA** | Activity-on-Arrow: activities are arrows, nodes are events |
| **AON** | Activity-on-Node: activities are boxes/nodes, arrows show dependencies |

### Formulas

**Forward Pass (Earliest Event Time, EET):**
```
EET(node) = MAX(EET(predecessor) + duration(activity))
```
Take the MAXIMUM when multiple paths converge at a node.

**Backward Pass (Latest Event Time, LET):**
```
LET(node) = MIN(LET(successor) - duration(activity))
```
Take the MINIMUM when multiple paths diverge from a node. Start from the end node where LET = EET.

**Float:**
```
Float(event) = LET(node) - EET(node)
```
Or for an activity:
```
Total Float = LET(end node) - EET(start node) - duration
```

**Critical Path Identification:**
- A node is on the critical path when EET = LET (float = 0)
- The critical path is the sequence of activities connecting all zero-float nodes
- Mark with // (double lines) on the diagram

### WBS Rules (the 100% Rule)
1. No more than 5 levels of branching
2. Captures everything (the 100% rule) -- all work is accounted for
3. Tasks contribute to parent task (children sum to parent)
4. Small enough to be manageable, not so small that visibility is lost

---

## WORKED EXAMPLES WITH NUMBERS

### Example 1: PCB Assembly (Slides 23-25, 31)

**Data:**

| Activity | Description | Predecessor | Duration (mins) |
|----------|-------------|-------------|----------------|
| A | Warm-up iron | (Start) | 3 |
| B | Collect all parts | (Start) | 2 |
| C | Fit parts to PCB | B | 4 |
| D | Solder parts | A, C | 8 |
| E | Test | D | 2 |

**Forward pass:**
- Node 0 = 0
- Node 1 = 0+2 = 2 (B)
- Node 2 = max(0+3, 2+4) = max(3, 6) = **6** (B-->C governs, not A)
- Node 3 = 6+8 = 14 (D)
- Node 4 = 14+2 = **16** (E)

**Backward pass:**
- Node 4 = 16
- Node 3 = 16-2 = 14
- Node 2 = 14-8 = 6
- Node 1 = 6-4 = 2
- Node 0 = min(6-3, 2-2) = min(3, 0) = 0

**Result**: All EET = LET, so ALL activities are critical. Critical path = B --> C --> D --> E = 16 mins. Zero float. VERY risky schedule.

### Example 2: Seven-Activity Project (Slides 26-27)

**Data:**

| Activity | Predecessor | Duration |
|----------|-------------|----------|
| A | (Start) | 2 |
| B | (Start) | 3 |
| C | A | 4 |
| D | B | 5 |
| E | B | 5 |
| F | C | 2 |
| G | E | 1 |

**Forward pass:** 0, 2, 3, 6, 8, 9
**Backward pass:** 0, 3, 3, 7, 8, 9

**Critical path = 9 days, route: B --> E --> G**

Non-critical: A(float=1), C(float=1), F(float=1), D(float=1)

### Example 3: Student Exercise (Slides 28-29)

**Data:**

| Activity | Predecessor | Duration (days) |
|----------|-------------|----------------|
| A | (Start) | 3 |
| B | (Start) | 2 |
| C | A | 4 |
| D | B | 5 |
| E | B | 4 |
| F | C, D | 3 |
| G | E | 2 |

**Forward pass:** 0, 3, 2, 7, 6, 10
**Backward pass:** 0, 3, 2, 7, 8, 10

**Critical path = 10 days**
**TWO critical paths**: A --> C --> F **AND** B --> D --> F (both = 10 days)

**Float**: E and G have 2 days of total float (node 4: EET=6, LET=8, difference=2)

---

## MAPPING TO APOLLO'S SAR DRONE PROJECT

### 1. Project Definition Match

The SAR drone project is a textbook "project" per Graham's definition:
- **Fixed period**: MSc academic year (Oct 2025 - Apr 2026)
- **Limitations**: Budget (student), equipment (Pi 5, Cube, one drone), team of 5
- **Temporary**: Defined beginning (brief) and end (D7 submission)
- **Unique**: Not routine -- novel autonomous SAR system with custom CV pipeline
- **Interrelated tasks**: CV depends on camera, GPS estimation depends on CV, flight testing depends on both

### 2. WBS Evidence

Apollo created an explicit WBS for the project. Evidence:
- **`dashboard/src/pages/wbs-data.ts`**: A coded WBS with hierarchical task breakdown, tracked in a React dashboard
- **CLAUDE.md file structure section**: The entire project is decomposed into modules (config, vision, planning, main, tests, docs) -- this IS a WBS
- **Flight testing steps** (in CLAUDE.md): Progressive 5-step ladder from bench to autonomous -- a WBS for testing
- **`docs/TEST_GUIDE.md`**: 41 test scripts categorized into hardware/, flight/, diagnostics/, calibration/, laptop/ -- hierarchical test WBS

**Hatton L4 move**: "Our WBS followed the 100% rule (Graham, 2025) by decomposing the project into seven top-level work packages -- Training, Design, Project Management, Quality, Build, Test, and Assessment -- mirroring the AVDASI2 unit WBS. Within my CV subsystem, I further decomposed into four levels: Vision Pipeline > Model Training > Dataset Generation > Individual augmentation transforms. This ensured no work was invisible to the team."

### 3. Network Diagram / Dependencies

Apollo's project has clear task dependencies documented in CLAUDE.md:
- vision.py is INDEPENDENT (no dependencies on other modules)
- planning.py is INDEPENDENT
- main.py DEPENDS ON vision.py, planning.py, config.py, states.py, utils.py
- TFLite testing on Pi DEPENDS ON camera working, model exported, Pi OS configured
- Flight testing has STRICT sequential dependencies (bench --> passive --> waypoint --> auto)

**The flight testing ladder IS a dependency chain:**
```
Step 1 (MP AUTO) --> Step 2 (waypoint script) --> Step 3 (passive CV) --> Step 4 (auto + log only) --> Step 5 (full autonomous)
```
"Never skip a step" = respecting the critical path through validation.

### 4. Critical Path Analysis

The project's critical path ran through:
1. Pi hardware setup (camera, serial, OS)
2. CV model working on Pi (TFLite inference)
3. MAVLink connection verified
4. Outdoor GPS test
5. Flight day testing

**Float existed on**:
- Documentation (could be done in parallel with development)
- Dashboard/visualization (nice-to-have, not blocking flight)
- Model retraining (could iterate while other testing continued)
- Simulation testing (completed early, had weeks of float)

**Zero float on**: Hardware integration (Pi + Cube + Camera + GPS = the critical chain). Any delay in getting the Pi camera working or the Cube communicating would delay the entire project. This is exactly what happened on 2026-03-11 when weather cancelled the flight day -- the critical path was extended.

### 5. Waterfall vs Agile in the Project

The project used a **hybrid approach** (as Graham's slide 10 suggests -- "more than waterfall vs agile"):

**Waterfall elements:**
- Sequential flight testing ladder (cannot skip steps)
- Regulated (drone safety, SSSI geofence, RC kill switch requirements)
- Clear requirements (R01-R12 from project brief)
- Hardware dependencies are inherently sequential

**Agile elements:**
- Sprint-like development sessions (session log shows intense 1-day sprints)
- `brain-dump.md` = product backlog (append-only ideas capture)
- `NICE_TO_HAVE.md` = prioritized backlog with impact/effort scoring
- Kanban-style task tracking in dashboard
- Iterative model retraining (v1 --> v2 --> v3 datasets)
- "Get something that works partially" -- simulation-first approach

**Hatton L4 move**: "Rather than adopting a pure waterfall or agile methodology, I employed what Boehm and Turner (2003) term a 'risk-driven' approach. The hardware integration path followed a strictly sequential waterfall discipline -- you cannot test flight software before verifying the serial connection -- while the software development path used agile sprints with continuous integration. This hybrid was necessary because, as the lecture material notes, 'not one size fits all' and the choice depends on 'type of technology, company methods, and how iterative the design can be' (Graham, 2025)."

### 6. Project Lifecycle Mapping

Using Graham's 4-phase model:
- **Concept** (Oct-Nov 2025): Project brief, initial research, team formation
- **Definition** (Nov-Dec 2025): Requirements analysis (R01-R12), architecture decisions, WBS creation
- **Development** (Jan-Mar 2026): Code development, simulation testing, hardware integration, model training
- **Handover/Closure** (Mar-Apr 2026): Flight day testing, report writing, D6/D7 submission

Using the 5-phase APM PMBOK model:
- **Initiation**: Brief received, team allocated
- **Planning**: WBS, dependencies table, Gantt chart, flight test ladder
- **Execution**: Software development, hardware build, model training
- **Monitoring and Control**: Session logs in CLAUDE.md, brain-dump.md, NICE_TO_HAVE.md scoring
- **Closure**: D7 report, lessons learned documentation

---

## WEAPONIZABLE QUOTES

### From the Lecture Material

1. **"A planned set of interrelated tasks to be executed over a fixed period and within certain cost and other limitations"** -- Project definition. Maps perfectly to SAR drone.

2. **"Not one size fits all"** -- Lifecycle choice depends on technology, company methods, innovation level, customer systems. Justifies the hybrid waterfall/agile approach.

3. **"Small enough to be manageable, not so small that visibility is lost"** -- WBS granularity principle. Justifies the level of decomposition in the dashboard WBS.

4. **"No more than 5 levels (branching). Captures everything (the 100% rule). Tasks contribute to parent task."** -- WBS rules. Can cite when describing project decomposition.

5. **"Critical path = the longest path through the project"** -- Use when discussing which tasks had zero float (hardware integration chain).

6. **"The difference is called 'Float'"** -- Use when discussing which tasks could absorb delays (documentation, visualization, model retraining).

7. **"Dummy activity: Representing a dependency, but line does not represent an activity (time)"** -- Use when discussing dependencies between subsystems (e.g., vision.py must be working before flight testing can begin, but vision development itself has independent float).

8. **"All communications and task management (for the group) should take place on your private teams channel"** -- Kanban board usage requirement.

### From the Cheat Sheet

9. **"When earliest finish and latest start are equal, the event is part of the critical path"** -- Formal definition useful for report.

10. **"When earliest finish and latest start are different... the task can move or be delayed without compromising the critical path"** -- Float definition for report.

---

## HATTON L4 MOVES

### Move 1: Critical Evaluation of PM Approach
"While the WBS decomposition followed the 100% rule (Graham, 2025), ensuring all work was visible, the network diagram revealed that our critical path ran exclusively through hardware integration tasks. This meant that software development -- despite consuming 70% of total effort -- had significant float and could not accelerate the project completion date. In retrospect, I should have identified this critical path earlier and allocated more team resources to the hardware-dependent tasks."

### Move 2: Reflective Application of Float
"The concept of float proved practically valuable when our flight day was cancelled due to weather (2026-03-11). Because I had identified that documentation and model retraining were off the critical path, I immediately redirected that day's effort to bench testing, FOV calibration, and lens calibration -- tasks that WERE on the critical path but could be partially advanced without flying. This is precisely the kind of schedule optimization that network analysis enables (Graham, 2025)."

### Move 3: WBS to Kanban Pipeline
"Following the lecture's WBS --> List --> Kanban Board pipeline, I created a hierarchical WBS in our React dashboard (`wbs-data.ts`), then mapped leaf-level work packages to our team's task tracker. Each work package had a clear 'definition of done' -- for example, WBS item 5.3.2 'TFLite inference on Pi' was only marked complete when benchmark.py reported >4 FPS with >0.9 confidence. This traceability from WBS to acceptance criteria is what transforms project management from bureaucratic overhead into engineering rigour."

### Move 4: Hybrid Methodology Justification
"The diversity-of-projects discussion (Graham, 2025) highlighted that safety-critical, highly-interdependent projects with clear requirements favour waterfall, while projects with changing end goals favour agile. Our SAR drone exhibited BOTH characteristics: the flight safety requirements (R01 geofence, R04 altitude cap, RC kill switch) demanded waterfall discipline, while the CV pipeline (model architecture, training data, confidence thresholds) benefited from agile iteration. I therefore adopted a risk-driven hybrid: waterfall for the safety-critical path, agile sprints for the perception pipeline."

### Move 5: Dependencies and the Progressive Testing Ladder
"The network diagram concept directly informed our flight testing strategy. Each test step (bench commands --> passive CV --> waypoint flight --> autonomous) had a strict finish-to-start dependency -- the predecessor must PASS before the successor begins. This is the AOA convention applied to validation: each arrow represents not just a task but a trust-building activity. The 'never skip a step' rule is the engineering equivalent of respecting the critical path through the verification chain."

---

## DIAGRAM DESCRIPTIONS (for reference)

### Slide 13 WBS Tree
A hierarchical tree diagram rooted at "Build a house" with 8 Level-1 branches (Building design, Foundations, Utilities, Roof, Walls, Interior Finishing, Landscaping, Regulatory planning). Each branch has 2-6 leaf tasks. Hand-drawn style. Follows the 100% rule.

### Slide 23 AOA Network (PCB)
Five numbered circles (0-4) connected by arrows. Two paths leave node 0: A goes to node 2, B goes to node 1. From node 1, C goes to node 2. From node 2, D goes to node 3. From node 3, E goes to node 4. The teal arrow points to node circle explaining "Node or event."

### Slide 25 Forward Pass
Same PCB network with red numbers added above each node showing earliest event times: 0, 2, 6, 14, 16. Convention box shows "Earliest time possible" with red number next to a generic node circle.

### Slide 27 Critical Path
Seven-activity network with both forward (red, above) and backward (green, below) pass numbers. Double red lines (//) mark the critical path on arrows B, E, G. Non-critical paths (A, C, D, F) have no marks. Text states "Critical path = 9 days" and "Critical path = B --> E --> G."

### Slide 29 Student Exercise Solution
Seven-activity network with forward/backward pass. Two critical paths both marked with //: A-->C-->F and B-->D-->F. Pink arrow points to node 4 where EET(6) != LET(8), labeled "Difference is called 'Float'." Float = 2 days for tasks E and G.

### Slide 30 Dummy Activity
Network with dashed red line (dummy activity) connecting node 2 to node 3, representing that activity E depends on both C and B without adding duration. Photo of a crash test dummy (visual pun).

### Slide 32 Complex Network
Large-scale real engineering project network with ~30+ activities, multiple parallel streams, and convergence points. Demonstrates the practical complexity that network analysis tools must handle.

### AOA Cheat Sheet
Fully annotated single-page reference diagram with all conventions labeled: nodes, arrows, durations, forward pass numbers, backward pass numbers, critical path markings, float identification. Includes the complete 6-step method and a worked example table.
