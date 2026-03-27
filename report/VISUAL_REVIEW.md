# Visual Review of Compiled PDF Reports

Reviewed: 2026-03-27
Reports: D6 (33 pages), D7 (8 pages)

---

## D6 Company Report (report/main.pdf) -- 33 pages

### Overall Assessment

The report is professionally typeset in LaTeX with consistent formatting throughout. Section numbering, heading hierarchy, and page numbering are all correct. The document uses a clean serif font (Computer Modern), appropriate margins, and well-structured tables. No placeholder figures were found. All tables render correctly and are readable.

### Brief Compliance Checklist

| Requirement | Status | Notes |
|-------------|--------|-------|
| Executive Summary | PRESENT (p2) | Single page, self-contained, covers all key results |
| Introduction with bios | PRESENT (p3-4) | Context, background, company description, 5 member bios with roles |
| Contributions table | PRESENT (p4) | Table 1 with key contributions per member |
| Design Rationale | PRESENT (p5-7) | Section 1, includes STEEPLE analysis |
| STEEPLE analysis | PRESENT (p5) | All 7 dimensions covered: Social, Technological, Economic, Environmental, Political, Legal, Ethical |
| System Description | PRESENT (p8-10) | Section 2, hardware platform, software architecture, CV pipeline, state machine |
| Requirements Verification | PRESENT (p11-13) | Section 3, all 12 requirements (R01-R12) addressed individually |
| Evaluation | PRESENT (p13-15) | Section 4, plus/delta table, discussion of key findings |
| References | PRESENT (p16-17) | 29 numbered references, two-column format |
| Appendices | PRESENT (p18-33) | A through G: state transition table, config params, model training, safety/risk, testing methodology, field results, future work |
| Page limit (15 excl. cover/exec/intro/refs/appendices) | NEEDS CHECK | Counted pages: cover(1) + exec summary(1) + intro(2) = 4 excluded. Sections 1-4 span p5-p15 = 11 pages. References excluded. Well within 15-page limit. |
| GitHub link | PRESENT (p13) | Section 3.12, public repo with MIT licence |

### Page-by-Page Notes

**Page 1 -- Title Page**
- Clean, minimal title page with title, author, course, date
- ISSUE: Very sparse -- the entire bottom 80% of the page is blank white space. Consider adding the aerial map figure from the brief (Figure 1 with flight area, search area, SSSI overlays) to make the title page more informative and visually engaging. A title page with just 4 lines of text looks underwhelming.

**Page 2 -- Executive Summary**
- Well-written, self-contained single page
- Covers: mission objective, system overview, key design decisions, results achieved, what was demonstrated
- Good density of concrete numbers (4.8 FPS, 0.966 confidence, CEP50 of 2.3m, 1.1 minutes search time)
- Professional and complete

**Page 3 -- Introduction (Context, Background, Company, Bios)**
- Good context setting with scenario description
- Bullet list of drone capabilities is clear
- Company description covers team formation, methodology (agile, workstream-based), tools (GitHub, Slack)
- Team member bios are detailed with specific roles
- ISSUE: Team members are named "Team Member 2", "Team Member 3", etc. instead of real names. Only Dmytro Chuprynyuk has a real name. This needs to be fixed before submission -- all members need real names.

**Page 4 -- Introduction (continued) + Contributions Table**
- Table 1 (contributions) is well-formatted and readable
- ISSUE: Same anonymisation problem -- "Team Member 2" through "Team Member 5" instead of real names in both the text and the table

**Page 5 -- Design Rationale (STEEPLE + Hardware Selection)**
- STEEPLE analysis covers all 7 dimensions in a natural flowing paragraph style (not a forced table)
- Social, Technological, Economic, Environmental, Political, Legal, Ethical all addressed
- Hardware selection section with bullet points for key design choices (global shutter, no thermal, MAVProxy bridge)
- Good technical depth with cost figures and justifications
- References properly cited

**Page 6 -- Design Rationale (Trade Studies + Software Architecture)**
- Table 2: Companion computer MCDA (Pi 5 vs Jetson Nano vs Intel NCS2) -- well formatted, weighted criteria, clear winner
- Table 4: Communication architecture MCDA (Direct Serial vs MAVProxy Bridge vs ROS 2) -- same quality
- Section 1.3 Software Architecture Rationale with 4 numbered design principles
- GOOD: Trade study tables are clear, properly weighted, and justify decisions with evidence

**Page 7 -- Design Rationale (Detection Model + Path Planning + State Machine)**
- Table 6: Detection model selection MCDA (YOLOv8n vs others)
- Table 8: Search pattern selection MCDA (Lawnmower vs Spiral vs Expanding Sq vs Random)
- Section 1.6 State Machine Design rationale
- GOOD: The MCDA tables are consistent in format throughout the report (1-5 scale, weighted)
- All tables numbered sequentially and referenced in text

**Page 8 -- System Description (Hardware Platform + Software Architecture)**
- Section 2.1 Hardware Platform with Table 10 (bill of materials with costs, total 565 GBP)
- Section 2.2 Software Architecture with Figure 1 (module dependency graph)
- ISSUE: Figure 1 (Module dependency graph) is a plain text box with arrows shown as text characters ("Config -> Independent Modules -> Domain -> Orchestrator"). This should be a proper diagram (flowchart/block diagram) with boxes and arrows. A text-only figure looks unprofessional in a LaTeX report and does not meet the brief's recommendation for "flow charts, schematics, images."
- The BOM table is clean and informative

**Page 9 -- System Description (CV Pipeline + Search Pattern)**
- Table 12: MAVLink commands used -- clear and informative
- Section 2.3 Computer Vision Pipeline with preprocessing, inference, smart detection mode
- Section 2.4 Search Pattern Generation with algorithm description
- Good technical detail on the detection pipeline stages
- Equation for FOV/ground footprint referenced but not shown on this page

**Page 10 -- System Description (State Machine) + Requirements Verification (start)**
- Figure 2: State transition diagram -- TEXT ONLY, same issue as Figure 1. Shows state flow as plain text ("INIT -> CONNECTING -> ARMING -> TAKEOFF..."). This MUST be a proper state machine diagram with boxes, arrows, and labels. This is a critical visual for the report.
- ISSUE: Both figures in the entire report are text-only placeholders. The brief explicitly recommends "flow charts, schematics, images." Two text-box figures significantly weaken the Communication criterion (20% of grade).
- Section 2.5 Mission State Machine description is thorough
- Sections 2.6-2.8 (Target Localisation, Ground Station, Simulation) are concise

**Page 11 -- Requirements Verification**
- Table 13: Requirements verification summary -- excellent. All 12 requirements mapped with Method, Evidence, and Status columns. All show "Verified" status.
- Sections 3.1-3.3 (R01-R03) expand on specific requirements
- GOOD: The verification table is exactly what the brief asks for
- Section 3.1 (R01 - Fly Within Flight Area) references the geofence implementation with four software layers
- Section 3.3 (R03) explains KML parsing and SITL testing

**Page 12 -- Requirements Verification (continued)**
- Sections 3.4-3.10 covering R04 through R10
- Each requirement has a subsection with method and evidence description
- R07 (Land 5-10m from casualty) explains 7.5m offset landing approach
- R08 (Autonomy level) references Sheridan's levels of autonomy and the SAR operational requirement
- R09 (RTH and Motor Cutoff) describes three independent safety mechanisms (RC kill, keyboard abort, automated failsafes)
- R10 (Report lat/lon and images) describes detection logging with JSON metadata

**Page 13 -- Requirements Verification (R11-R12) + Evaluation start**
- R11 (Company Pilot) and R12 (Public GitHub with MIT licence) completed
- Section 4 Evaluation begins with plus/delta framing
- GOOD: Evaluation explicitly states it excludes team-working aspects per the brief footnote

**Page 14 -- Evaluation (Plus/Delta Table + Discussion)**
- Table 14: Plus/delta review -- comprehensive table with 7 strengths (P1-P8) and 7 areas for improvement (D1-D7)
- Each item has specific evidence/detail, not generic statements
- Section 4.2 Discussion of Key Findings covers architecture resilience, detection performance, GPS estimation accuracy, incomplete flight validation
- GOOD: Honest about limitations (no outdoor flight, GPS timing lag, float32 model)

**Page 15 -- Evaluation (continued)**
- Detection performance (P4) discussion with mAP, confidence numbers
- GPS estimation accuracy (D3) with CEP50 and worst-case error
- Incomplete flight validation (D1, D4, D5, D6) -- honest about weather cancellation
- GOOD: The discussion is technically rigorous with specific numbers, not hand-waving

**Pages 16-17 -- References**
- 29 references in IEEE-style numbered format, two-column layout
- Mix of academic papers, technical documentation, standards (CAA, JARS, AHEP4)
- Properly formatted with authors, titles, venues, years
- URLs included where appropriate with access dates
- GOOD: References appear legitimate and well-cited throughout the text

**Page 18 -- Appendix A: State Transition Table**
- Table 16: Complete 20-state transition table with Entry Condition, Actions, Exit Transitions, Timeout
- Very detailed -- every state documented
- ISSUE: Table is dense but readable. Some cells have long text that wraps extensively. Consider if this level of detail is needed given appendices are not assessed.

**Pages 19-20 -- Appendix A (continued) + Appendix B: Configuration Parameters**
- Page 19: Continuation of state transition table (VERIFY through DONE states) + global overrides
- Page 20: Table 17 with all configuration parameters grouped by function (altitudes, speeds, camera optics, detection, geofence, servo)
- GOOD: Configuration table is well-organized with Parameter, Default, Unit, Description columns

**Pages 21-22 -- Appendix C: Model Training and Dataset**
- C.1 Training Data Strategy (synthetic + real + negatives)
- C.2 Synthetic Data Generation (step-by-step)
- C.3 Real Data Labelling
- C.4 Negative Mining
- C.5 Training Pipeline with Table 18 (hyperparameters)
- C.6 Results with Table 19 (v1 vs v2 model comparison with mAP, precision, recall)
- C.7 Deployment instructions
- C.8 Limitations (5 bullet points, honest about dataset limitations)
- GOOD: Thorough training documentation with reproducible details

**Pages 23-24 -- Appendix D: Safety and Risk Management**
- D.1 Geofence Implementation (speed scalar, repulsive vector, hard boundary cutoff)
- D.2 Failure Mode Analysis with Table 20 (failure modes and automated responses)
- D.3 Operator-in-the-Loop (VERIFY state classification: Y/N/I)
- D.4 Emergency Procedures (RC kill, keyboard abort, automated failsafes)
- D.5 Risk Assessment with Table 21 (risk register with likelihood, severity, mitigation)
- D.6 Regulatory Considerations (CAA, VLOS, SSSI, Wildlife Act)
- GOOD: Safety section is comprehensive and addresses real failure modes

**Pages 25-28 -- Appendix E: Testing Methodology**
- E.1 V-Model Verification Approach
- E.2 Five-Tier Progressive Testing with Table 22
- E.3 Test Script Organisation (41 scripts in 6 categories)
- E.4 Dry-Run Validation
- E.5 DJI Video Analysis
- E.6 Stress Testing and Failure Scenarios with Table 23 (20 scenarios, PASS/FIXED results)
- E.7 Comparison with Industry Testing Standards (V-model, NASA, SORA)
- E.8 Preflight Checklist
- GOOD: Testing section is exceptionally thorough. The 20-scenario stress test table is impressive.

**Pages 29-30 -- Appendix F: Field Testing and Results**
- F.1 Bench Testing Results
- F.2 FOV Calibration with Equation (1) for focal length calculation
- F.3 Lens Distortion Calibration
- F.4 Inference Benchmarks with Table 24 (with/without undistortion timing)
- F.5 Post-Hoc Video Analysis
- F.5.1 Detection Performance
- F.5.2 GPS Estimation Accuracy (CEP50, maximum error)
- GOOD: Equation (1) renders correctly. Benchmark table is clear.

**Pages 31-33 -- Appendix F (continued) + Appendix G: Future Work**
- F.6 Dry-Run Validation
- F.7 Discussion (detection pipeline confidence, GPS accuracy, inference throughput, remaining unknowns)
- G.1-G.6: Future Work sections (Inference Acceleration, Detection Improvements, Multi-Target Support, Thermal Imaging, Communication, Swarm Operations)
- GOOD: Future work is realistic and well-structured, not fantasy

---

## D7 Individual Reflective Report (report_personal/main.pdf) -- 8 pages

### Overall Assessment

Clean LaTeX formatting consistent with D6. The report is well-structured with clear section headings mapped to AHEP4 standards. Writing is reflective and personal, not generic.

### Brief Compliance Checklist

| Requirement | Status | Notes |
|-------------|--------|-------|
| M5 (Design solutions, safety, diversity, standards) | PRESENT | Section 2 (Design and Problem-Solving) with 2.1 Original Solutions, 2.2 Safety-Critical Design, 2.3 STEEPLE Considerations |
| M7 (Environmental/societal impact, life-cycle) | PRESENT | Section 3 (Societal and Environmental Impact) with 3.1 Societal Impact, 3.2 Environmental Considerations |
| M16 (Team effectiveness, leadership) | PRESENT | Section 4 (Teamwork, Leadership, Communication) with 4.1-4.4 covering structure, what worked, solo coding reality, disagreements |
| M17 (Communication effectiveness) | PRESENT | Section 4.5 (Communication Methods and Effectiveness) + 4.6 (Giving and Receiving Feedback) |
| Page limit (5 pages excl. cover + appendices) | ISSUE | Content runs from p1 to p7 (7 pages of content), plus p8 (references). No separate cover page. No appendices. The 5-page limit applies to the BODY -- pages 1-7 contain body text. This is 7 pages, which EXCEEDS the 5-page limit by 2 pages. CRITICAL ISSUE. |
| Self-assessment | PRESENT | Section 5 with strengths (5.3), weaknesses (5.4), self-development programme (5.5) |
| References | PRESENT (p8) | Only 1 reference (Koopman 2019). Very thin -- should have more citations to support claims. |

### Page-by-Page Notes

**Page 1 -- Title + Introduction + Design and Problem-Solving (M5) start**
- Title "Individual Reflective Report: Autonomous SAR Drone Project"
- Section 1 Introduction: good personal framing, mentions scope expansion, 15,000 lines of Python
- Section 2.1 Original Solutions to Complex Problems: dual-backend vision, simulation-first development, target localisation under uncertainty, model retraining pipeline
- GOOD: Concrete technical examples, not vague claims
- Writing style is reflective ("I built", "I discovered", "I implemented")

**Page 2 -- M5 (continued) + STEEPLE + M7 start**
- Section 2.2 Safety-Critical Design: five-step progressive testing, geofencing, RC kill switch
- Section 2.3 STEEPLE Considerations: covers all 7 dimensions briefly
- Section 3 (Societal and Environmental Impact - M7) begins at bottom
- GOOD: Safety section references aerospace verification practices

**Page 3 -- M7 (Societal and Environmental Impact)**
- Section 3.1 Societal Impact: SAR application, dual-use concerns (surveillance), personal Ukraine connection
- Section 3.2 Environmental Considerations: mission-level (SSSI geofence), hardware life-cycle (Pi 5 power, LiPo batteries), development-level (simulation minimised physical testing)
- GOOD: Honest about dual-use technology concerns. Ukraine connection adds personal depth.
- Environmental section covers mission/hardware/development levels per the brief's "entire life-cycle" requirement

**Page 4 -- M16 (Teamwork)**
- Section 4.1 Team Structure and Roles
- Section 4.2 What Worked Well: handoff points, pilot independence, project manager logistics
- Section 4.3 The Solo Coding Reality: honest about being the sole software developer, delegation barriers
- Section 4.4 Managing Disagreements: ROS 2 vs raw MAVLink debate, workload tension
- GOOD: Very honest and reflective. The "solo coding reality" section shows genuine self-awareness about delegation difficulties. The disagreement resolution is specific and credible.

**Page 5 -- M17 (Communication) + Self-Assessment start**
- Section 4.5 Communication Methods and Effectiveness: simulator, documentation, ground station interface, meetings/presentations
- Section 4.6 Giving and Receiving Feedback: specific examples (GPS antenna placement, abort button location)
- Section 5 Self-Assessment and Development begins
- GOOD: Evaluates four different communication methods with honest effectiveness assessment. The "abort button too close to confirm button" feedback example is excellent -- specific and shows responsiveness.

**Page 6 -- Self-Assessment**
- Section 5.1 Skills Developed: MAVLink/ArduPilot, edge AI deployment, real-time systems, field debugging
- Section 5.2 Time Management and Goal-Setting: weekly milestones, living document tracking, contingency planning
- Section 5.3 Strengths Identified: rapid prototyping, documentation, demonstrations
- Section 5.4 Weaknesses Acknowledged: designing for collaboration, speed over inclusion, delayed hardware testing
- GOOD: Strengths and weaknesses are genuine, not "my weakness is that I work too hard"

**Page 7 -- Self-Development Programme + Career Goals + Final Thought**
- Section 5.5 Self-Development Programme: 3 concrete actions (collaborative architecture design, earlier hardware testing, verbal communication of technical decisions)
- Section 5.6 Connection to Career Goals: Ukraine, humanitarian technology, mine clearance
- Section 5.7 Final Thought: "the quality of an autonomous system is determined not by the cleverness of its algorithms, but by the rigour of its testing and the honesty of its failure analysis" (in italics)
- GOOD: The final sentence is memorable and demonstrates genuine insight. Career goals are specific and personal.

**Page 8 -- References**
- CRITICAL ISSUE: Only 1 reference (Koopman 2019). A 7-page reflective report at MSc level should cite more sources to support claims about aerospace verification practices, Sheridan's autonomy levels, AHEP4 standards, V-model testing, etc. The D6 report has 29 references; the D7 has 1.

---

## Critical Issues Summary (Must Fix Before Submission)

### D6 Report

1. **FIGURES ARE TEXT-ONLY (HIGH PRIORITY)**: Both Figure 1 (module dependency graph, p8) and Figure 2 (state machine diagram, p10) are rendered as plain text in grey boxes rather than proper diagrams with boxes and arrows. The brief explicitly recommends "flow charts, schematics, images" for the System Description. This directly impacts the Communication criterion (20% of grade). Replace with proper diagrams (TikZ, draw.io export, or included PNG/PDF images).

2. **Team member names anonymised (HIGH PRIORITY)**: Pages 3-4 use "Team Member 2" through "Team Member 5" instead of real names. This must be corrected before submission. The brief requires "member bios/roles."

3. **Title page is very sparse (MEDIUM)**: The title page is 90% white space. Consider adding the aerial map from the brief (flight area, search area, SSSI overlays) or a system photo to make it visually engaging.

4. **No photographs or screenshots anywhere in the main body (MEDIUM)**: The entire 15-page main body contains zero photographs, screenshots, or visual figures beyond the two text-box placeholders. No ground station screenshot, no detection overlay image, no hardware photo, no search pattern visualization. For a project that produced working software with visual outputs, this is a missed opportunity for the Communication criterion.

### D7 Report

1. **EXCEEDS 5-PAGE LIMIT (CRITICAL)**: The body content spans 7 pages (pages 1-7). The brief specifies "5 pages EXCLUDING cover page and appendices." Even if page 1 title area is excluded, the content is still ~6.5 pages. Must cut approximately 2 pages of content. Candidates for trimming: Section 2.3 STEEPLE (already in D6), parts of Section 4.3 Solo Coding Reality, Section 5.2 Time Management.

2. **Only 1 reference (HIGH PRIORITY)**: The references section contains a single entry. At MSc level, reflective writing should still cite sources: Sheridan's autonomy taxonomy (referenced in D6 but not D7), V-model verification standards, AHEP4 document itself, aerospace testing frameworks. Add at least 5-8 references.

3. **No cover page (MEDIUM)**: The brief says "5 pages EXCLUDING cover page." There is no separate cover page -- the title is at the top of page 1 with content immediately below. Adding a cover page would also help with the page count issue by moving the title off page 1.

---

## What Looks Good

### D6
- Executive summary is excellent -- dense with concrete metrics
- STEEPLE analysis is naturally integrated, not a forced checklist
- MCDA trade study tables (Tables 2, 4, 6, 8) are consistently formatted and well-justified
- Requirements verification table (Table 13) directly maps every requirement
- Plus/delta evaluation is honest about limitations
- Appendices are thorough (state transitions, config, training, safety, testing, field results, future work)
- References are substantive (29 entries, properly formatted)
- The stress test table (Table 23, 20 scenarios) is impressive evidence of rigour

### D7
- Reflective tone is genuine throughout -- first person, specific examples, honest self-criticism
- AHEP4 mapping is clear (M5, M7, M16, M17 all explicitly addressed)
- The "solo coding reality" and "managing disagreements" sections show real self-awareness
- Career goals tied to personal Ukraine connection adds authenticity
- Final thought is memorable and insightful
- Feedback examples are specific (GPS antenna placement, abort button layout)

---

## Formatting Quality

| Aspect | D6 | D7 |
|--------|----|----|
| Font consistency | Good (Computer Modern) | Good (Computer Modern) |
| Heading hierarchy | Good (numbered sections) | Good (numbered sections) |
| Table formatting | Excellent (consistent, readable) | N/A (no tables) |
| Equation rendering | Good (Eq. 1 on p29) | N/A |
| Page numbers | Present, correct | Present, correct |
| Citation style | IEEE numeric, consistent | IEEE numeric (but only 1 ref) |
| Margins | Standard LaTeX | Standard LaTeX |
| Column layout | Single column (body), two-column (refs) | Single column throughout |
| Orphan/widow lines | Minor instances but acceptable | Clean |
| Hyperlinks | Present in references (blue) | Present in references (blue) |
