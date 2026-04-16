# Lecture 1: Down-Selection & Risk Management — Complete Extraction

**Source**: AVDASI2 Project Workshop, Week 3, Monday 6th October 2025
**Lecturer**: Mark Graham (avdasi2@bristol.ac.uk)
**University of Bristol**

---

## PART A: DOWN-SELECTION / CONVERGENT TOOLS (Slides 1-7)

---

### Slide 1 — Title Slide

- **Title**: AVDASI2 PROJECT WORKSHOP — Down-Selection & Risk Management
- Week 3, Monday 6th October 2025, Mark Graham
- Decorative image of a lion cub (no technical content)

---

### Slide 2 — Convergent Tools: Learning Objectives

**Unit level learning objective (ULO 2)**:
> "Carry out the design, build and test of a functioning major UAV assembly as part of a team, **using applicable interdisciplinary concepts and methods**"

(The phrase "using applicable interdisciplinary concepts and methods" is highlighted in cyan — this is what down-selection and risk assessment directly serve.)

**Session level learning objectives** (all covered in both video and live session):
1. **Recall** the benefits of using a structured down-selection methodology
2. **Utilise** a *numerical* and *non-numerical pairwise comparison tool* to **rank** or **weight** solution criteria
3. **Utilise** a *controlled convergence* tool to **select** an optimum solution
4. **Utilise** a *multi-criteria decision analysis (MCDA) method* to **select** an optimum solution

---

### Slide 3 — Convergent Tools: Recap (4-Tool Overview)

A diagram showing four convergent tools in a pipeline with green arrows:

| Tool | Name | Purpose |
|------|------|---------|
| **Tool 1** | Pairwise Comparison (Simple) | **Use for ranking criteria** — non-numerical, compare each criterion against every other |
| **Tool 2** | Pairwise Comparison (Numerical) | **Use for assigning a weighting factor** to your design criteria — numerical scale |
| **Tool 3** | Controlled Convergence | **Comparing designs against chosen criteria** (+, better or worse) — evaluate designs |
| **Tool 4** | Multicriteria Decision Analysis (MCDA) | **Comparing designs, using weighted criteria and a scoring system** — MCDA matrix |

**Pipeline flow** (green arrows):
- Evaluate criteria (Tools 1 & 2) --> Evaluate designs (Tools 3 & 4)

**Visual**: Four small matrix/table screenshots showing each tool's typical spreadsheet layout.

---

### Slide 4 — Combining Tools

Shows how Tool 2 (Pairwise Comparison Numerical) feeds into Tool 4 (MCDA matrix):

**Pairwise Comparison Matrix** (top):
- Scale: =Much More Important (9), =More Important (3), The =Same (1), =Less Important (0.333333), =Much Less Important (0.111111)
- Criteria listed: Initial Cost, Durability, Weight, Handling, Disposal
- Each criterion compared pairwise; row totals give percentage weightings
- Red circle highlights the weighting percentages flowing out

**Arrow**: "Weightings from this Pairwise comparison ... can be used as the weightings in the MCDA"

**MCDA Matrix** (bottom):
- Criteria column with weightings (must add to 100%)
- Design columns (a, b, c, d) each with raw score and weighted score
- **"Highest score suggests optimum design"**

---

### Slide 5 — Combining Tools (Detailed Worked Example)

**Warning callout (yellow box, red border)**: "Warning -- scales can cause excessive sensitivity."

**Pairwise Comparison Matrix** (fully worked):

| Criteria | Initial Cost | Durability | Weight | Handling | Disposal | Total | % |
|----------|-------------|------------|--------|----------|----------|-------|---|
| Initial Cost | X | 1 | 1 | 3 | 3 | 8.00 | 24 |
| Durability | 1 | X | 1 | 1 | 3 | 6.00 | 18 |
| Weight | 1 | 1 | X | 9 | 3 | 14.00 | 41 |
| Handling | 0.333 | 0.1111 | X | 0.333 | | 1.78 | 5 |
| Disposal | 0.333 | 0.333 | 0.333 | 3 | X | 4.00 | 12 |

Scale used: 9, 3, 1, 0.333, 0.111 (symmetric — if A vs B = 3, then B vs A = 1/3 = 0.333)

**MCDA Matrix** (fully worked):

| Criteria | Weightings | Design # | design a |  | design b |  | design c |  | design d |  |
|----------|-----------|----------|---------|---------|---------|---------|---------|---------|---------|---------|
|  | (must add to 100%) |  | score | weighted | score | weighted | score | weighted | score | weighted |
| Initial Cost | 0.240 | 1 | 4 | 1.0 | 3 | 0.7 | 1 | 0.2 | 1 | 0.2 |
| Durability | 0.180 | 2 | 1 | 0.2 | 2 | 0.4 | 3 | 0.5 | 2 | 0.4 |
| Weight | 0.410 | 3 | 3 | 1.2 | 1 | 0.4 | 5 | 2.1 | 5 | 2.1 |
| Handling | 0.050 | 4 | 2 | 0.1 | 5 | 0.3 | 0 | 0 | 5 | |
| Disposal | 0.120 | 5 | | 0.0 | | 0.0 | | 0.0 | | 0.0 |
| **Total** | | | | **2.5** | | **1.7** | | **2.8** | | **2.9** |

Design d scores highest (2.9), suggesting it is the optimum choice.

---

### Slide 6 — Developing Tools Further

Same MCDA matrix as slide 5, with red arrows pointing at the individual "score" values.

**Key questions raised**:
- "Could this be an average based on team votes?"
- "Is more democratic necessarily better?"
- "Should each voice carry equal weight?"

**Implication**: Scores can be averaged from multiple team members' votes, but this raises questions about whether democratic averaging is always the right approach, and whether some team members' opinions should carry more weight (e.g., domain experts).

---

### Slide 7 — Exercise: Convergence

**Instructions for in-class exercise**:
1. Read the worksheet instructions
2. Pick which question (A or B) to carry out the down-selection on
3. Decide/complete your list of criteria
4. Decide/complete your list of potential solutions
5. Select which tools are appropriate for getting you an answer & then use the tools
6. Discuss the result of the tool output vs your initial gut feel
7. **Consider any limitations of the methods used** (highlighted in yellow)
8. **Consider any opportunities to improve the method** (highlighted in yellow)

A worksheet is shown on the right side of the slide.

---

## PART B: RISK ASSESSMENT (Slides 8-20)

---

### Slide 8 — Risk Management Learning Objectives

**Unit level learning objective (ULO 4)**:
> "discuss key health and safety responsibilities for engineers; and using recognised risk management tools create risk assessments to analyse a variety of project risks"

**Session level learning objectives**:
1. **Discuss** the Health and Safety responsibilities of engineers operating in the UK, **referring** to the key legal requirements & implications (greyed out — covered elsewhere)
2. **Create** a risk assessment using a recognised process whilst **identifying** frequency scores, consequence scores; and appropriate risk mitigations for operational, technical and project risks (checked)
3. **Generate** a scoring system for the classification of frequency and consequence (checked)
4. **Classify** risks using a criticality matrix (greyed out)

---

### Slide 9 — Risk Assessment (Section Divider)

Photo of a team of ~8 people sitting around a glass conference table, looking at a document titled "Risk" — visual metaphor for collaborative risk assessment process.

---

### Slide 10 — Risk Assessment: Three Pillars

**Diagram showing three categories of risk with sub-types**:

#### 1. Moral/Ethical (left column, green boxes)
- **Health and Safety** (red star = high importance)
- Inclusion, Ethics, Sustainability
- Note: "these also have legal requirements here" (arrow pointing to Legal column)

#### 2. Economic (centre column, pink boxes)
- **Schedule (Delays)** (red star)
- **Financial ($)** (red star)
- Reputational
- **Damage to property / equipment** (red star)

#### 3. Legal (Law) (right column, blue boxes)
- Commercial / Corporate
- Criminal
- Civil
- Intellectual property
- Employment

**Red stars mark the most relevant risk types for this course**: Health and Safety, Schedule, Financial, Damage to property/equipment.

**Key insight**: Risk assessment is NOT just about safety — it encompasses schedule delays, financial loss, property damage, legal liability, and reputational harm.

---

### Slide 11 — Completing a Risk Assessment (Template)

**Full risk assessment table structure with annotated columns**:

| Column | Content | Annotation |
|--------|---------|------------|
| **Date and Initials of reviewer** | Who reviewed, when | Traceability |
| **Type of Risk** | Health and Safety, Financial, Schedule, Legal... | Categorisation |
| **Description of Hazard** | Simple description of the Hazard | What could go wrong |
| **Description of Consequence** | Consequence if the hazard occurs | What happens if it does |
| **Frequency** | Frequency (Scoring) — how likely | Numerical score |
| **Consequence** | Consequence (Scoring) — how severe | Numerical score |
| **Risk number (f x c)** | Risk Number = frequency x consequence | Calculated priority |
| **Mitigation** | What mitigations will I apply | Actions to reduce risk |
| **Residual risk** | What risk remains even after the mitigation | Acknowledgement of remaining risk |

---

### Slide 12 — Risk Assessment Examples: Hazard

**Definition**: **Hazard = something that has potential to cause harm**

**Two examples shown** (with photo of a Portaledge — a hanging tent used in climbing):
- Hazard: **Total** failure of mounting system during overnight stay on 'Portaledge'
- Hazard: **Partial** failure of mounting system during overnight stay on 'Portaledge'

**Key point**: The same system can have multiple hazards with different severity levels (total vs partial failure).

---

### Slide 13 — Risk Assessment Examples: Frequency

**Definition**: **Frequency = how often/likely is this likely to happen**

**"Select a scale of 1-5 or 1-10"**

**Example 1** — Server outage due to power interruption:
| Score | Meaning |
|-------|---------|
| 1 | < 1 in 10,000 hrs |
| 2 | 1 in 10,000 hrs |
| 3 | 1 in 1,000 hrs |
| 4 | 1 in 100 hrs |
| 5 | 1 in 10 hrs |
Frequency = ? (exercise for students)

**Example 2** — Landing gear stuck due to total failure of hydraulic hose (with photo of 747 at LGW, 2014):
| Score | Meaning |
|-------|---------|
| 1 | 1 in 10,000,000 |
| 2 | ... |
| 3 | 1 in 100,000 |
| 4 | ... |
| 5 | 1 in ... |
Frequency = ? (exercise for students)

**Key point**: The frequency scale must be defined BEFORE scoring. Teams choose their own scale (1-5 or 1-10) appropriate to the domain.

---

### Slide 14 — Risk Assessment Examples: Consequence

**Definition**: **Consequence = if this does happen, what might be the consequences**

**"Select a scale of 1-5 or 1-10"**

**Example 1** — Test rig failure, delay to product release (Financial impact):
| Score | Meaning |
|-------|---------|
| 1 | Negligible (<$10k) |
| 2 | Minor (>$10k <$100k) |
| 3 | Major (>$100k <$1m) |
| 4 | Severe (>$1m <$10m) |
| 5 | Extreme (>$10m) |
Consequence = ? (exercise)

**Example 2** — Train fails to stop due to wheel slide causing collision (with photo of 31st October 2021, Salisbury, image from RAIB):
| Score | Meaning |
|-------|---------|
| 1 | (Negligible) Non-reportable injury |
| 2 | (Minor) Minor injury |
| 3 | (Major) Major injury or multiple minor injuries |
| 4 | (Critical) Single fatality or multiple major injuries |
| 5 | (Catastrophic) Multiple fatalities |
Consequence = ? (exercise)

**Key point**: Consequence scales are domain-specific — financial scales use dollar amounts, safety scales use injury severity. The same framework applies to both.

---

### Slide 15 — Risk Assessment Examples: Risk Number

**Definition**: **Risk Number = frequency x consequence**

**Example 1** — Ingestion of volcanic ash into both engines (photo of Eyjafjallajokull, Iceland, 2010):
- Frequency: 1 (extremely rare)
- Consequence: 5 (catastrophic — both engines out)
- **Risk number = 1 x 5 = 5**

**Example 2** — Bird strike to 1 engine (photo of a bird + damaged engine):
- Frequency: 3 (moderately common)
- Consequence: 4 (critical — engine damage/failure)
- **Risk number = 3 x 4 = 12**

**Key insight**: A common moderate event (bird strike, RN=12) can have a higher risk number than a rare catastrophic event (volcanic ash, RN=5). This is the power of the multiplicative model — it prioritises by combined probability and impact.

---

### Slide 16 — Risk Assessment: Going Further (Residual Risk)

Same risk assessment table template as slide 11, with a red callout box at the "Residual risk" column:

> **"Consider rescoring the Frequency, Consequence and RN here is a great idea."**

**Key point**: After defining mitigations, the best practice is to RESCORE frequency and consequence to produce a new (lower) residual risk number. This demonstrates that mitigations actually reduce risk quantitatively, not just qualitatively.

---

### Slide 17 — Advanced Template: Post-Mitigation Scoring

**Enhanced risk assessment table** with explicit pre-mitigation and post-mitigation columns:

| Risk ID (number) | Type of Risk | Description of Hazard | Description of Consequence or Effect | **Pre-mitigation** F | **Pre-mitigation** C | **Pre-mitigation** Risk number | Mitigations (identify existing and additional) | **Post-mitigation** F | **Post-mitigation** C | **Post-mitigation** Risk number | Actions (with owners and date) |
|---|---|---|---|---|---|---|---|---|---|---|---|

**Red circle** highlights the Post-mitigation columns (F, C, Risk number).

**Key additions vs basic template**:
- Risk ID numbering system
- Explicit pre/post mitigation scoring columns
- "Actions (with owners and date)" — assigns accountability
- Mitigations column specifies "identify existing AND additional"

---

### Slide 18 — Exercise: Develop a Risk Assessment (~20 minutes)

**Two example scenarios**:
- **Example A**: Use of dry ice to cool brakes on Formula 1 car during race preparation (photo of F1 pit stop)
- **Example B**: Drone inspection of wind turbine (photo of large wind turbine)

**Instructions (centre)**:
- Complete the risk assessment for 3-4 risks
- Include a range of risk types — not just safety
- Complete all a row before adding new risks
- Use the blank paper copies

**Important callout (yellow box)**: "Take 5 min to develop a scoring system before starting. It does not need to be perfect!"

---

### Slide 19 — Tip: Recording Existing and New Mitigations

**Key principle**: Best to split mitigations into:
1. **Already existing/deployed mitigations**
2. **Additional mitigations** (as a result of the Risk Assessment)

**"The score is based on existing mitigations."** (The pre-mitigation score already accounts for existing controls.)

**Example for climbing rope**:
- *Existing mitigation*: Use min 8kN rope to EN 892
- *Additional mitigation*: Deploy double rope system on traversing climbs

**Mitigation column layout suggestion**:
```
Existing:
[list existing controls]

Additional:
[list new controls identified by RA]
```

---

### Slide 20 — Example Risk Assessment

**Reference to a real-world professional risk assessment**:
- **Royal Air Force Charitable Trust Enterprises**
- **ROYAL INTERNATIONAL AIR TATTOO 2024**
- **EVENT RISK ASSESSMENT (B)**
- Photo of two military jets in formation (Black Eagles aerobatic team)

**Purpose**: Shows students that professional organisations (military aviation events) use the same risk assessment framework taught in this lecture. The RIAT is one of the world's largest military airshows — their risk assessment is a real worked example students can reference.

---

## KEY DEFINITIONS SUMMARY

| Term | Definition |
|------|-----------|
| **Hazard** | Something that has potential to cause harm |
| **Frequency** | How often/likely is this likely to happen (scored 1-5 or 1-10) |
| **Consequence** | If this does happen, what might be the consequences (scored 1-5 or 1-10) |
| **Risk Number** | Frequency x Consequence (multiplicative model) |
| **Mitigation** | Actions taken to reduce frequency and/or consequence |
| **Residual Risk** | Risk remaining after mitigations are applied |
| **Pairwise Comparison** | Comparing criteria in pairs to rank or weight them |
| **Controlled Convergence** | Comparing designs against criteria (+, better/worse) |
| **MCDA** | Multi-Criteria Decision Analysis — weighted scoring of designs against criteria |

---

## KEY FRAMEWORKS

### 1. Pairwise Comparison Scale (Numerical)
| Value | Meaning |
|-------|---------|
| 9 | Much More Important |
| 3 | More Important |
| 1 | The Same |
| 0.333 | Less Important |
| 0.111 | Much Less Important |

Symmetric: if A vs B = 3, then B vs A = 1/3

### 2. Risk Assessment Formula
```
Risk Number (RN) = Frequency (F) x Consequence (C)
```

### 3. Risk Assessment Process
1. Define scoring system (1-5 or 1-10 for both F and C)
2. Identify hazards (by type: H&S, Financial, Schedule, Legal, Property)
3. Describe consequences
4. Score frequency
5. Score consequence
6. Calculate risk number (F x C)
7. Identify mitigations (existing + additional)
8. Rescore F, C, and RN post-mitigation = Residual Risk
9. Assign actions with owners and dates

### 4. Risk Types (Three Pillars)
- **Moral/Ethical**: Health & Safety, Inclusion, Ethics, Sustainability
- **Economic**: Schedule delays, Financial loss, Reputational damage, Property/equipment damage
- **Legal**: Commercial/Corporate, Criminal, Civil, Intellectual Property, Employment

---

## D7 RELEVANCE: MAPPING TO APOLLO'S SAR DRONE PROJECT

### Down-Selection Evidence in the Project

| Decision Point | Method Used | Evidence |
|---|---|---|
| **AI model selection** (YOLOv8n vs YOLOv8s vs COCO) | MCDA-style comparison: inference speed, accuracy, model size, Pi compatibility | 3 model variants tested in `cv_models/`, benchmarked in `tests/hardware/benchmark.py` |
| **Inference backend** (TFLite vs NCNN vs Ultralytics) | Pairwise comparison on speed, compatibility, accuracy | NCNN 4.5x faster than TFLite (72ms vs 327ms), documented in `memory/cv-speed-research.md` |
| **Camera resolution** (640x480 vs 1456x1088) | Controlled convergence — tested both, 1088 gives better detection at altitude | Config changed from 640x480 to 1456x1088 after field testing |
| **Communication architecture** (direct serial vs mavproxy bridge) | Risk-driven: serial failed on Python 3.13, mavproxy adds reliability | Documented in `docs/CONNECTIVITY.md` |
| **Detection confidence threshold** (0.25 vs 0.4 vs 0.5) | Trade-off analysis: lower = more detections but more false positives | 0.4 chosen as compromise, with `--conf` flag for field adjustment |
| **Flight test progression** (5 steps) | Controlled convergence — each step builds trust before adding risk | Steps 1-5 in `docs/FIRST_FLIGHT.md`, never skip a step |

### Risk Assessment Evidence in the Project

| Risk ID | Type | Hazard | F | C | RN | Mitigation | Residual |
|---------|------|--------|---|---|-----|-----------|----------|
| R01 | H&S / Legal | Drone flies outside Flight Area boundary | 2 | 5 | 10 | Runtime geofence (`cv2.pointPolygonTest` -> emergency RTL) | 1x5=5 |
| R02 | H&S | Drone enters SSSI (No-Fly Zone) | 2 | 4 | 8 | NFZ polygon check, repulsive offset, waypoint filtering | 1x4=4 |
| R03 | H&S | Drone takes off far from designated TOL | 2 | 3 | 6 | Distance check at arming (warns if >5m from TOL) | 1x3=3 |
| R04 | H&S | Drone exceeds safe altitude | 1 | 4 | 4 | 50m altitude hard cap in `navigation.py` | 1x4=4 |
| R05 | Property | Drone crashes during autonomous flight | 3 | 4 | 12 | RC override guard: pilot can always take control; kill switch to STABILIZE | 1x4=4 |
| R06 | Schedule | AI model fails to detect casualty in real conditions | 4 | 3 | 12 | 3 model variants, `--model` flag, retrained on real data (mAP50=0.995) | 2x3=6 |
| R07 | Property | Drone lands on casualty | 2 | 5 | 10 | 7.5m offset landing, operator Y/N confirmation at VERIFY | 1x5=5 |
| R08 | Schedule | GPS estimate too inaccurate for target localisation | 3 | 3 | 9 | Kalman filter, multi-pass averaging, inverse variance weighting | 2x3=6 |
| R09 | H&S | Loss of communication (GCS failsafe) | 2 | 4 | 8 | GCS failsafe enabled, RTL on link loss, link-lost banner in UI | 1x4=4 |
| R10 | Legal | Operating without evidence of detection | 2 | 2 | 4 | Detection photos + JSON saved to `mission_detections/` on Y/N/I/X | 1x2=2 |
| R11 | Schedule | Code fails on Pi hardware (platform incompatibility) | 3 | 3 | 9 | Docker Pi test, platform auto-detect in config.py, progressive testing | 1x3=3 |
| R12 | Legal / IP | No software license | 1 | 2 | 2 | MIT LICENSE file added | 1x1=1 |

### Weaponizable Quotes for D7 Reflection

**On structured decision-making**:
> "Using applicable interdisciplinary concepts and methods" (ULO 2) — directly justifies using MCDA for model selection, pairwise comparison for backend choice

> "Warning -- scales can cause excessive sensitivity" (Slide 5) — shows awareness of tool limitations; Apollo can discuss how confidence threshold selection required domain knowledge beyond the numerical tool

> "Is more democratic necessarily better? Should each voice carry equal weight?" (Slide 6) — Apollo can reflect on how the team weighted domain expertise (e.g., the CV specialist's vote on model choice carried more weight than general team consensus)

**On risk assessment**:
> "The score is based on existing mitigations" (Slide 19) — Apollo can show how his pre-mitigation scores already accounted for built-in safety (RC override, kill switch) and then ADDITIONAL mitigations (geofence, NFZ repulsion) further reduced residual risk

> "Include a range of risk types -- not just safety" (Slide 18) — Apollo can demonstrate breadth by showing schedule risks (R06, R08, R11), legal risks (R10, R12), property risks (R05, R07), not just H&S

> "Consider rescoring the Frequency, Consequence and RN [after mitigation] is a great idea" (Slide 16) — Apollo implemented this exact pattern: pre-mitigation RN calculated, mitigations applied in code, residual risk documented

**On process**:
> "Take 5 min to develop a scoring system before starting. It does not need to be perfect!" (Slide 18) — pragmatic approach; Apollo can argue that the scoring system evolved as understanding of real-world risks deepened through simulation and field testing

### Hatton L4 Moves This Content Enables

| L4 Move | How This Lecture Enables It | Apollo's Evidence |
|---------|---------------------------|-------------------|
| **Critical evaluation of methods** | Slides 5-6 warn about sensitivity of scales and democratic vs expert weighting | Apollo can critically evaluate MCDA limitations in model selection — e.g., how benchmark numbers alone don't capture real-world performance |
| **Justification of approach** | The 4-tool pipeline (rank criteria -> weight criteria -> evaluate designs -> score designs) provides a structured framework to JUSTIFY, not just DESCRIBE | Apollo's progressive test ladder (5 steps, never skip) is a controlled convergence applied to flight testing |
| **Risk beyond safety** | Slide 10's three pillars (Moral/Economic/Legal) demand breadth | R01-R12 cover all three pillars: H&S (R01-R04, R09), Economic/Schedule (R06, R08, R11), Property (R05, R07), Legal (R10, R12) |
| **Pre/post mitigation quantification** | Slide 17's advanced template with explicit pre/post columns | Every risk in the table above has pre-mitigation RN and post-mitigation residual risk, showing measurable risk reduction |
| **Existing vs additional mitigations** | Slide 19's split between existing and new controls | Existing: RC override, kill switch, GCS failsafe (hardware). Additional (from RA): geofence, NFZ repulsion, altitude cap, detection logging (software) |
| **Connecting tools** | Slides 3-4 show how pairwise comparison feeds MCDA | Apollo can show how risk assessment INFORMED the down-selection (e.g., model choice prioritised reliability/speed because risk assessment identified R06 as high-priority) |

### Key Pedagogical Takeaways

1. **Down-selection is not gut feel** — structured tools exist to make it traceable and defensible
2. **Risk assessment covers 3 pillars** — Moral/Ethical, Economic, Legal (not just safety)
3. **Risk Number = F x C** — simple multiplicative model, but must define scales FIRST
4. **Mitigations reduce residual risk** — rescore after mitigation to prove quantitative improvement
5. **Split existing vs additional mitigations** — shows what was already in place vs what the RA process added
6. **Tools have limitations** — scale sensitivity, democratic averaging, domain expertise weighting
7. **Combine tools** — pairwise comparison weightings feed directly into MCDA scoring
8. **Professional practice uses the same framework** — RIAT 2024 risk assessment uses identical structure

---

## REFERENCES / FURTHER READING

- RIAT 2024 Event Risk Assessment (B) — Royal Air Force Charitable Trust Enterprises (slide 20)
- RAIB (Rail Accident Investigation Branch) — Salisbury, 31 October 2021 (slide 14)
- EN 892 — European standard for climbing ropes (slide 19)
- LGW 747 incident, 2014 — landing gear failure example (slide 13)
- Eyjafjallajokull volcanic ash incident, Iceland 2010 (slide 15)
