# Multi-Objective Optimization in UAV Academic Papers — Literature Review

> Research on how to properly present parameter coupling, trade-offs, and optimization
> in drone/UAV academic papers. Collected 2026-03-27.

---

## 1. Core Terminology and Frameworks

Academic UAV optimization papers use these established frameworks. Pick the one that
matches what you are actually doing — do not overstate.

### Multi-Objective Optimization (MOO)
The general framework. You have N objectives that conflict (e.g., coverage vs speed vs
detection rate). Two main solution approaches:

| Approach | What it does | When to use | Limitation |
|----------|-------------|-------------|------------|
| **Weighted Sum** | Collapse N objectives into one scalar: `J = w1*f1 + w2*f2 + ...` | You know the priorities upfront; want a single "best" answer | Cannot explore non-convex Pareto regions; 70% of route planning papers use this but it hides trade-offs |
| **Pareto Front** | Find the full set of non-dominated solutions; present as a curve/surface | You want to show the decision-maker the trade-off space | Computationally expensive; hard to visualize beyond 3 objectives |

**Key finding**: 70% of UAV path planning papers use weighted sum (Drones 2024, 8(12), 769).
But Pareto-based papers (NSGA-II, NSGA-III) are considered more rigorous because they
expose the trade-off rather than hiding it behind arbitrary weights.

**Source**: "Dealing with Multiple Optimization Objectives for UAV Path Planning in
Hostile Environments: A Literature Review" — Drones 2024, 8(12), 769.
https://www.mdpi.com/2504-446X/8/12/769

### Multi-Criteria Decision Analysis (MCDM / MCDA)
A step beyond MOO. Once you have candidate solutions (from Pareto front or otherwise),
MCDM provides structured methods to select among them:

- **AHP** (Analytic Hierarchy Process) — pairwise comparison of criteria importance
- **TOPSIS** — rank alternatives by distance to ideal/anti-ideal solution
- **PROMETHEE** — preference ranking based on outranking relations
- **Goal Programming** — minimize deviation from target values for each objective

**UAV-specific application**: Integrated MCDM model for UAV base selection + mission
planning in disaster management. Uses AHP for goal weights, then goal programming to
jointly minimize: number of bases, flight distance, unairworthy days, and cost.

**Source**: "An integrated multi-criteria decision-making model for long-term planning
of UAVs in disaster management" — PLOS ONE, 2024.
https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0340303

**Source**: "A revision on multi-criteria decision making methods for multi-UAV mission
planning support" — Expert Systems with Applications, 2021.
https://arxiv.org/html/2402.18743v1

### Multidisciplinary Design Optimization (MDO)
The aerospace-native framework for systems where multiple engineering disciplines
(aerodynamics, structures, propulsion, control) are coupled. Each discipline has its own
analysis code; MDO coordinates them.

**Key concept**: Coupling variables — outputs of one discipline that are inputs to another.
The strength of coupling determines whether you can optimize disciplines independently
(weak coupling) or must solve them simultaneously (strong coupling).

**UAV applications**: Wing design (aero-structure coupling), solar UAV endurance
(power-aero-weight coupling), VTOL transition (aero-control coupling).

**Source**: "Multidisciplinary Design Optimization of Aerial Vehicles: A Review of
Recent Advancements" — Int J Aerospace Engineering, 2018.
https://onlinelibrary.wiley.com/doi/10.1155/2018/4258020

**Source**: "A unified and experimentally validated design framework for long-endurance
solar UAVs using model-based multi-objective MDO" — Struct Multidisc Optim, 2025.
https://link.springer.com/article/10.1007/s00158-025-04194-6

### Design of Experiments (DOE) + Response Surface Methodology (RSM)
When you cannot run a full optimizer (too expensive, too many parameters), DOE gives you
a structured way to sample the design space, and RSM fits a surrogate model (polynomial
surface) to the samples.

**Standard DOE designs**: Full factorial, fractional factorial, Central Composite Design
(CCD), Latin Hypercube Sampling (LHS).

**UAV application**: RSM for tailsitter UAV structural parameters. Varied 4 parameters
(chord, span, sweep), built response surface for endurance + drag, then ran MOGA on the
surface. Result: +19.5% endurance, -34.78% drag vs baseline.

**Source**: "Development of Response Surface Model of Endurance Time and Structural
Parameter Optimization for a Tailsitter UAV" — PMC, 2020.
https://pmc.ncbi.nlm.nih.gov/articles/PMC7147476/

---

## 2. Standard Figures and Visualizations

### 2.1 Pareto Frontier Plot
**The** canonical figure for multi-objective optimization.

- 2D: Objective 1 on x-axis, Objective 2 on y-axis. Non-dominated solutions form a curve.
  Points below/left of the curve are infeasible or dominated.
- 3D: Three objectives on axes. Pareto front becomes a surface.
- >3D: Use parallel coordinates, radar/spider charts, or self-organizing maps (iSOM).

**How papers present it**:
- Plot all evaluated solutions as grey dots, Pareto-optimal as colored dots/line
- Mark the "knee point" (best compromise) or the selected operating point
- Sometimes overlay utopia point (best of each objective independently) to show gap

**For your report**: A 2D Pareto curve of (coverage completeness vs detection
reliability) or (search time vs detection probability) with your chosen operating
point marked.

**Source on >3D visualization**: "A taxonomy of methods for visualizing Pareto front
approximations" — GECCO 2018. https://dl.acm.org/doi/10.1145/3205455.3205607

**Source**: "Visualization and analysis of Pareto-optimal fronts using interpretable
self-organizing map (iSOM)" — Swarm and Evolutionary Computation, 2023.
https://www.sciencedirect.com/science/article/abs/pii/S2210650222001687

### 2.2 Tornado Diagram (Sensitivity Ranking)
Horizontal bar chart showing which parameter has the most influence on the output.
Each parameter is varied from low to high while others held at baseline. Widest bar
= most influential parameter. Bars ordered top-to-bottom by influence magnitude.

**Standard in**: risk analysis, engineering design, project management.
**For your report**: Vary each mission parameter (altitude, speed, lane spacing, confidence
threshold, overlap) independently. Show which one moves detection probability or coverage
time the most.

### 2.3 Sensitivity / Interaction Matrix (Heatmap)
NxN matrix where rows = input parameters, columns = output metrics. Cell color = strength
of influence (from Jacobian ∂output/∂input or correlation coefficient). Shows at a glance
which parameters matter for which outputs, and which are coupled.

**Formal version**: Jacobian matrix J_ij = ∂y_i/∂x_j. In engineering design, the
Jacobian captures how each output responds to each input. SVD of the Jacobian reveals
principal sensitivity directions.

**Source**: "Uncertainty quantification and reduction using Jacobian and Hessian
information" — Design Science, Cambridge.
https://www.cambridge.org/core/journals/design-science/article/uncertainty-quantification-and-reduction-using-jacobian-and-hessian-information/957A5E1284BB22E1DC734187E9625396

### 2.4 Design Structure Matrix (DSM) / N2 Diagram
Square matrix showing dependencies between system components or parameters.
Diagonal = components. Off-diagonal = interfaces/data flows.
- Above diagonal: feedforward (outputs that feed downstream)
- Below diagonal: feedback (outputs that feed back upstream — these create coupling loops)

**N2 variant (NASA)**: Functions on diagonal, inputs in columns, outputs in rows.
Popularized at NASA for spacecraft systems engineering. Shows data flow between subsystems.

**Extended DSM (XDSM)**: Adds process flow arrows + iteration markers on top of standard
DSM. The standard diagram for MDO architecture visualization. Published by Lambe & Martins
(2012).

**For your report**: A DSM showing how your mission parameters (altitude, speed, lane
spacing, FOV, detection threshold) are coupled through physics. E.g., altitude affects
FOV ground footprint AND detection confidence AND GPS accuracy.

**Source**: MIT OCW Lecture 04: Design Structure Matrix.
https://ocw.mit.edu/courses/esd-36-system-project-management-fall-2012/6c7bc91f35c7d387147908cd2c80c9ca_MITESD_36F12_Lec04.pdf

**Source**: "Extensions to the design structure matrix for MDO processes" — Struct
Multidisc Optim, 2012. https://link.springer.com/article/10.1007/s00158-012-0763-y

### 2.5 Response Surface / Contour Plot
3D surface or 2D contour map showing how an output (e.g., detection probability) varies
as two input parameters change simultaneously. Reveals:
- Optimal region (peak/valley)
- Sensitivity direction (steep vs flat)
- Interaction effects (curved contours = parameters interact)

**For your report**: Contour plot of detection probability vs (altitude, speed) with
your operating point marked. Or coverage time vs (lane spacing, altitude).

### 2.6 Spider / Radar Chart
Used in MCDM to compare candidate configurations across multiple criteria simultaneously.
Each axis = one criterion (normalized 0-1). Configurations overlaid as polygons.

**For your report**: Compare 3-4 mission configurations (conservative, balanced,
aggressive) across 5-6 criteria (coverage time, detection rate, false positive rate,
power consumption, safety margin, GPS accuracy).

### 2.7 Parallel Coordinates Plot
Each vertical axis = one objective/parameter. Each solution = a polyline crossing all axes.
Pareto-optimal solutions highlighted. Good for >4 dimensions where scatter plots fail.

---

## 3. Key Papers with Specific Approaches

### Paper 1: UAV Path Planning Benchmark (Pareto Baselines)
**"A multi-objective benchmark for UAV path planning with baseline results"**
Swarm and Evolutionary Computation, 2025.
https://www.sciencedirect.com/science/article/abs/pii/S2210650225001269

- Establishes standardized benchmark for comparing MOO algorithms on UAV path planning
- Presents Pareto fronts from multiple algorithms (NSGA-II, MOEA/D, etc.) on same problem
- Figures: overlaid Pareto fronts, hypervolume convergence curves, spacing metrics
- **Useful for**: justifying your choice of operating point on the trade-off curve

### Paper 2: Multi-Objective Jellyfish Search for UAV Paths
**"A UAV path planning method based on the framework of multi-objective jellyfish
search algorithm"** — Nature Scientific Reports, 2024.
https://www.nature.com/articles/s41598-024-79323-0

- Multi-objective cost function: path length + threat avoidance + altitude constraints +
  smoothness + wind effects (5 objectives)
- Uses reference-point-based Pareto decomposition
- Figures: 3D path visualization, Pareto front plots, convergence curves
- **Useful for**: showing how 5+ objectives are handled via decomposition

### Paper 3: Drone Swarm Coverage + Connectivity Trade-off
**"Multi-objective path planning for multi-UAV connectivity and area coverage"**
Ad Hoc Networks, 2024.
https://www.sciencedirect.com/science/article/abs/pii/S1570870524001318

- Trade-off between area coverage and communication connectivity
- Hybrid optimization balances coverage vs inter-UAV distance vs energy
- **Useful for**: the coverage-vs-something-else Pareto framing

### Paper 4: DRL for Time-Critical Wilderness SAR
**"Deep reinforcement learning for time-critical wilderness search and rescue using
drones"** — PMC, 2025.
https://pmc.ncbi.nlm.nih.gov/articles/PMC11831046/

- SAR-specific: optimizes time-to-find with endurance constraints
- Compares DRL paths against lawnmower baseline
- **Useful for**: SAR-specific terminology, comparison against lawnmower pattern

### Paper 5: UAV Swarm Load Sensitivity Analysis
**"UAV Swarm Mission Planning and Load Sensitivity Analysis Based on Clustering and
Optimization Algorithms"** — Applied Sciences, 2023.
https://www.mdpi.com/2076-3417/13/22/12438

- Sensitivity analysis of platform parameters (ascent angle, visible distance, viewing
  angle) on search efficiency
- Figures: sensitivity bar charts, parameter variation plots
- **Useful for**: how to present which parameters matter most

### Paper 6: MDO Survey with XDSM Notation
**"Multidisciplinary Design Optimization: A Survey of Architectures"**
Martins & Lambe, MIT/University of Michigan.
https://fab.cba.mit.edu/classes/865.18/design/mdo/MDOSurvey.pdf

- Defines XDSM notation (the standard for MDO process diagrams)
- Categorizes all MDO architectures (MDF, IDF, AAO, BLISS, CO, etc.)
- Figures: XDSM diagrams for every architecture
- **Useful for**: if you want to present your parameter dependencies formally

### Paper 7: RSM for Tailsitter UAV
**"Development of Response Surface Model of Endurance Time and Structural Parameter
Optimization for a Tailsitter UAV"** — Sensors/PMC, 2020.
https://pmc.ncbi.nlm.nih.gov/articles/PMC7147476/

- DOE (Central Composite Design) + RSM + MOGA workflow
- Figures: response surface plots, contour plots, Pareto front from MOGA
- **Useful for**: the DOE→RSM→optimization pipeline presentation

### Paper 8: MCDM for Multi-UAV Mission Planning
**"A revision on multi-criteria decision making methods for multi-UAV mission planning
support"** — Expert Systems with Applications, 2021.
https://arxiv.org/html/2402.18743v1

- Compares AHP, TOPSIS, ELECTRE, PROMETHEE, fuzzy MCDM on UAV scenarios
- Figures: decision matrices, criteria weight charts, ranking comparisons
- **Useful for**: if presenting a structured decision between configurations

---

## 4. How Papers Present "Everything Affects Everything"

This is the core challenge: altitude affects footprint, detection confidence, GPS accuracy,
flight time, and safety. Speed affects coverage rate, motion blur, detection window, and
power. Lane spacing affects coverage completeness, overlap, and mission time. Every
parameter touches multiple outputs.

### Approach A: Sensitivity Matrix (most common, easiest)
Build an NxN heatmap: rows = parameters (altitude, speed, lane spacing, threshold, etc.),
columns = outputs (coverage time, detection probability, GPS error, false positive rate).
Color = strength of influence. This is essentially a discretized Jacobian.

**How to compute**: vary each parameter +/-20% from baseline, measure output change.
Normalize to percentage change. Fill matrix.

**Advantages**: Shows everything at once. Immediately reveals which parameters are
"high-leverage" (hot row = affects many outputs) and which outputs are "fragile"
(hot column = sensitive to many parameters).

### Approach B: Design Structure Matrix / N2 (systems engineering native)
Put parameters on the diagonal. Off-diagonal cells show HOW they couple:
- altitude → footprint (physics: FOV geometry)
- altitude → detection confidence (empirical: altitude sweep data)
- speed → motion blur (physics: exposure time)
- lane spacing → coverage gaps (geometry: footprint overlap)

**Advantages**: Shows the coupling mechanism, not just the strength. Shows feedback
loops (e.g., lower altitude → smaller footprint → need tighter lane spacing → longer
mission → more battery → need to fly faster → more blur → lower confidence → need
lower altitude... circular).

### Approach C: Tornado Diagram per Output (simplest)
For each key output (e.g., detection probability), show a tornado diagram ranking
which input parameter moves it the most. Do one tornado per output.

**Advantages**: Very readable. Non-specialist audiences (like markers) get it instantly.

### Approach D: Pareto Front of Key Trade-off (most impactful)
Pick the TWO most important conflicting objectives (e.g., coverage time vs detection
reliability). Plot the Pareto front. Mark your chosen operating point.

**Advantages**: Directly shows that you cannot optimize both simultaneously and that
your design is a conscious compromise.

### Approach E: Response Surface (if you have data)
Pick the TWO most influential parameters (from tornado diagram). Plot a contour map
of the key output as a function of those two parameters. Mark your operating point.

**Advantages**: Shows interaction effects. If contours curve, the parameters interact
(cannot be optimized independently).

---

## 5. Recommended Approach for Your SAR Drone Report

Given your project (single drone, lawnmower search, YOLOv8 detection, fixed hardware),
the most appropriate and honest presentation is:

### What you are NOT doing (do not claim these)
- You are not running a formal MOO optimizer (NSGA-II, MOEA/D)
- You are not doing DOE with factorial designs
- You are not doing MDO across coupled disciplines with XDSM

### What you ARE doing (claim these confidently)
- **Parameter sensitivity analysis**: varying mission parameters and measuring effect on
  performance metrics. This is legitimate and publishable.
- **Trade-off characterization**: identifying and quantifying the key trade-offs
  (altitude vs detection, speed vs coverage, etc.)
- **Design point selection**: choosing operating parameters based on understanding of
  the trade-off space (even if done by engineering judgment rather than optimizer)

### Recommended figures (pick 2-3)

1. **Sensitivity matrix (heatmap)** — Parameters vs Outputs. Shows the "everything
   affects everything" problem at a glance. Use your DJI video data + simulation
   results to populate it.

2. **Pareto sketch or trade-off curve** — Coverage time vs Detection probability.
   Even 3-5 data points (from different altitude/speed configs) forms a meaningful
   curve. Mark your chosen config.

3. **Tornado diagram** — For detection probability specifically: which parameter
   moves it the most? (Probably altitude, then speed, then threshold, then lane
   spacing.)

### Recommended terminology
- "Parameter sensitivity analysis" (not "optimization" unless you actually optimized)
- "Trade-off characterization" or "trade-off analysis"
- "Design space exploration" (if you sampled multiple configs)
- "Operating point selection" (your chosen configuration)
- "Coupled parameters" or "parameter interdependence" (for the everything-affects-
  everything problem)
- "Pareto-optimal" only if you actually generated the full front
- "Multi-criteria" is fine even without formal MCDM

---

## 6. Quick Reference: Which Figure for Which Purpose

| What you want to show | Figure type | Complexity |
|----------------------|-------------|------------|
| Which parameters matter most | Tornado diagram | Low |
| How all parameters relate to all outputs | Sensitivity heatmap | Medium |
| The key trade-off | Pareto curve (2D) | Medium |
| Parameter interactions | Contour / response surface | Medium |
| System coupling / feedback loops | DSM / N2 diagram | Medium |
| Compare configurations holistically | Radar / spider chart | Low |
| High-dimensional trade-offs | Parallel coordinates | High |
| Full MDO process | XDSM diagram | High |

---

## Sources

- [Dealing with Multiple Optimization Objectives for UAV Path Planning — Drones 2024](https://www.mdpi.com/2504-446X/8/12/769)
- [A multi-objective benchmark for UAV path planning — Swarm & Evol Comp 2025](https://www.sciencedirect.com/science/article/abs/pii/S2210650225001269)
- [Multi-objective jellyfish search for UAV paths — Nature Sci Rep 2024](https://www.nature.com/articles/s41598-024-79323-0)
- [Multi-UAV connectivity and coverage — Ad Hoc Networks 2024](https://www.sciencedirect.com/science/article/abs/pii/S1570870524001318)
- [DRL for wilderness SAR drones — PMC 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC11831046/)
- [UAV swarm load sensitivity analysis — Applied Sciences 2023](https://www.mdpi.com/2076-3417/13/22/12438)
- [MDO survey with XDSM — Martins & Lambe](https://fab.cba.mit.edu/classes/865.18/design/mdo/MDOSurvey.pdf)
- [RSM for tailsitter UAV — PMC 2020](https://pmc.ncbi.nlm.nih.gov/articles/PMC7147476/)
- [MCDM for multi-UAV mission planning — Expert Sys w/ Apps 2021](https://arxiv.org/html/2402.18743v1)
- [MCDM for UAV disaster management — PLOS ONE 2024](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0340303)
- [MDO of aerial vehicles review — Int J Aerosp Eng 2018](https://onlinelibrary.wiley.com/doi/10.1155/2018/4258020)
- [Solar UAV MDO framework — Struct Multidisc Optim 2025](https://link.springer.com/article/10.1007/s00158-025-04194-6)
- [Pareto front visualization taxonomy — GECCO 2018](https://dl.acm.org/doi/10.1145/3205455.3205607)
- [Pareto visualization with iSOM — Swarm & Evol Comp 2023](https://www.sciencedirect.com/science/article/abs/pii/S2210650222001687)
- [Jacobian for uncertainty quantification — Design Science](https://www.cambridge.org/core/journals/design-science/article/uncertainty-quantification-and-reduction-using-jacobian-and-hessian-information/957A5E1284BB22E1DC734187E9625396)
- [DSM Wikipedia](https://en.wikipedia.org/wiki/Design_structure_matrix)
- [MIT OCW DSM Lecture](https://ocw.mit.edu/courses/esd-36-system-project-management-fall-2012/6c7bc91f35c7d387147908cd2c80c9ca_MITESD_36F12_Lec04.pdf)
- [XDSM extensions for MDO — Struct Multidisc Optim 2012](https://link.springer.com/article/10.1007/s00158-012-0763-y)
- [DSM coupling in aerospace MDO — Struct Multidisc Optim 2025](https://link.springer.com/article/10.1007/s00158-025-04003-0)
- [N2 diagram guide — Engineer's Vault](https://www.engineersvault.com/n2-diagram-and-functional-analysis/)
- [Tornado diagram — Wikipedia](https://en.wikipedia.org/wiki/Tornado_diagram)
- [Drone swarm detection & tracking — Communications Engineering 2023](https://www.nature.com/articles/s44172-023-00104-0)
- [Exploration strategies with MCDM for rescue — Autonomous Robots 2011](https://link.springer.com/article/10.1007/s10514-011-9249-9)
