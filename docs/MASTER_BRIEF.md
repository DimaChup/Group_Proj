# Master Brief -- Everything in One Place

> **The ONE reference for scoring both D6 and D7.** Read this, not 5 separate documents.

---

## Source

Extracted from AENGM0074-project-brief.pdf (Release 2.1, 4 February 2026, S Bullock).
Full extraction at `docs/PROJECT_BRIEF_COMPLETE.md`.

---

## Requirements (R01--R12)

| R | Requirement | Note |
|---|-------------|------|
| R01 | The drone shall only fly within the Flight Area. | Geofence required |
| R02 | The drone shall not fly over the SSSI. | Geofence required |
| R03 | The drone shall take off from a region within 5m of the defined Take-Off Location (TOL). | Geofence required |
| R04 | The drone shall not exceed an altitude of 50m above TOL ground level. | Geofence required |
| R05 | The drone shall undertake a search of the Search Area and identify potential items of lost person clothing and equipment ("items of interest"). | Geofence required |
| R06 | Upon PLB activation (expected 5-15 min into search), teams receive coordinates of a Focus Area (3-10 lat/long points), upon which the drone should then focus its search. | |
| R07 | The drone shall land within 10m but not within 5m of the casualty, deploy the provided first aid kit, then return to TOL. | |
| R08 | The level of autonomy and interface format/functionality shall be determined and justified by the Company and approved by the Client. | |
| R09 | All interfaces (RC, Ground Station, others) shall include 'Return to Home' (RTH) and 'Motor Cutoff' commands and other appropriate failsafes. | |
| R10 | Lat/lon and images of detected items of interest and of the casualty shall be reported. Verification report appendix including relevant imagery, data, uncertainties. | |
| R11 | The operation must have a designated Company Pilot, supervised by a Flight Lab Safety Pilot with ultimate responsibility and absolute authority. | |
| R12 | All software and flight logs shall be delivered via a public GitHub repository linked from the Company Report, licensed under MIT licence. | |

**Footnote (R01-R05):** Areas will NOT be visibly marked in field trials. Teams must report excursions/incursions verbally during trials and in post-flight reports. Flight logs may be examined. **Use of automatic geofences is required.**

---

## Deliverables

| D | What | Due | Weight |
|---|------|-----|--------|
| D1 | PDR presentation | Wk16 | Formative |
| D2 | Platform validation flight | Wk20 | Formative |
| D3 | Trial flights | Wk21 | Formative |
| D4 | FDR presentation | Wk22 | Formative |
| D5 | Demonstration flights | Wk22 | Formative |
| **D6** | **Group Report** | **Thu wk23** | **50% (peer weighted)** |
| **D7** | **Individual Reflective Report** | **Thu wk23** | **50%** |

**AI Policy:** Software development = Category 3 (Selective). Reporting = Category 2 (Minimal).

---

## D6 Group Report -- Page Limits and Required Sections

**Max length:** 15 pages (excluding cover, exec summary, introduction, references, appendices).

| Section | In/Out of page count | Notes |
|---------|---------------------|-------|
| Cover page | Excluded | |
| Executive Summary | Excluded | Single page, self-contained |
| Introduction | Excluded | Context, team bios, roles, member contributions |
| Design Rationale | **COUNTED** | STEEPLE analysis required |
| System Description | **COUNTED** | Flow charts, schematics, images recommended |
| Requirements Verification | **COUNTED** | Process and evidence for each R |
| Evaluation | **COUNTED** | Plus/delta of TECHNICAL performance only (not teamwork) |
| References | Excluded | Cite research/design/code sources |
| Appendices | Excluded | **Will NOT be assessed** -- include excerpts in main sections |

### Suggested Page Budget (15 pages)

| Section | Pages | Focus |
|---------|-------|-------|
| Design Rationale | 4 | STEEPLE, MCDA tables, decision trade-offs, alternatives |
| System Description | 5 | Architecture, CV pipeline, state machine, ground station, geofence |
| Requirements Verification | 3 | R01-R12 matrix with method + evidence + status |
| Evaluation | 3 | Plus/delta, benchmarks, detection performance, what would change |

---

## D6 Assessment Rubric (Appendix A -- EXACT wording, ALL bands)

### Specialist Skills and Problem-Solving (40%)

| Band | Marks | Descriptor |
|------|-------|------------|
| Fail | 0, 7, 15, 22, 29, 35 | Does not show ability to identify key aspects of complex problems or to use appropriate skills and resources to address them. |
| Third | 42, 45, 48 | Little evidence of awareness of key aspects, weak deployment of appropriate tools and techniques. |
| 2:2 | 52, 55, 58 | Limited ability to identify key aspects and use appropriate resources to address them. Some understanding of technologies and approaches demonstrated. |
| 2:1 | 62, 65, 68 | Key aspects of task and challenges identified. Appropriate technologies and approaches selected and implemented effectively. |
| First | 72, 75, 78 | Key aspects of task and challenges identified. Appropriate technologies and approaches selected and implemented effectively, showing initiative and autonomy. |
| High First | 83, 94, 100 | Confident and comprehensive identification of task and challenge aspects. Appropriate technologies and approaches selected and implemented highly effectively, showing initiative, autonomy, and creativity. |

**Key progression:** 62-68 = "effectively". 72-78 = adds "initiative and autonomy". 83+ = adds "confident and comprehensive" + "highly effectively" + "creativity".

### Decision Making (40%)

| Band | Marks | Descriptor |
|------|-------|------------|
| Fail | 0, 7, 15, 22, 29, 35 | No evidence shown of ability to make decisions in complex and unpredictable circumstances. |
| Third | 42, 45, 48 | Little evidence shown of ability to make decisions in complex and unpredictable circumstances. |
| 2:2 | 52, 55, 58 | Shows limited ability to make decisions in complex and unpredictable circumstances. |
| 2:1 | 62, 65, 68 | Confident in adapting to changing and unfamiliar or challenging circumstances and making evidence-based decisions. |
| First | 72, 75, 78 | Confident in adapting to changing and unfamiliar/challenging circumstances and making effective, evidence-based decisions. |
| High First | 83, 94, 100 | Shows confidence and creativity in adapting to changing and unfamiliar/challenging circumstances and making effective, evidence-based decisions. |

**Key progression:** 62-68 = "confident" + "evidence-based". 72-78 = adds "effective". 83+ = adds "creativity".

### Communication (20%)

| Band | Marks | Descriptor |
|------|-------|------------|
| Fail | 0, 7, 15, 22, 29, 35 | Very limited awareness of effective communication in reporting and presentation. |
| Third | 42, 45, 48 | Limited awareness of effective communication in reporting and presentation. |
| 2:2 | 52, 55, 58 | Some awareness of effective communication in reporting and presentation. |
| 2:1 | 62, 65, 68 | Reporting and presentation are effective, making use of appropriate techniques and resources. |
| First | 72, 75, 78 | Reporting and presentation are effective, making use of appropriate techniques and resources. |
| High First | 83, 94, 100 | Reporting and presentation are effective, engaging, and professional, making use of innovative techniques and resources. |

**Key progression:** 62-68 and 72-78 are IDENTICAL wording. 83+ = adds "engaging", "professional", and "innovative". This means Communication is binary: either you're at 62-78 ("appropriate") or you jump to 83+ ("engaging, professional, innovative"). No middle ground.

---

## D6 -- What 90+ Looks Like in Practice

### Specialist Skills (40%) -- what "highly effectively with initiative, autonomy, creativity" means:

1. **Comprehensive challenge identification.** Name every hard sub-problem: detection at altitude, GPS timing lag, inference speed on edge hardware, geofencing without visible markers, camera BGR/RGB mismatch, Python 3.13 TFLite breakage, PLB dynamic replanning, 5-10m landing zone accuracy.

2. **Justified technology choices with alternatives.** Every decision needs a WHY and what was rejected:
   - YOLOv8n over YOLOv8s: 206ms vs projected 400ms+ on Pi 5. Real-time needed at 5 m/s.
   - TFLite over ONNX/NCNN: widest Pi support, XNNPACK acceleration.
   - Lawnmower over spiral: complete area coverage guarantee (no gaps).
   - GUIDED over AUTO mode: dynamic replanning on PLB, state machine needs waypoint control.
   - Dual-backend CV: same model, develop fast on laptop, deploy lean on Pi.

3. **Initiative beyond requirements** (things not asked for):
   - Interactive simulator with keyboard flight, GPS estimation, Kalman filter.
   - Video analysis pipeline (DJI replay + detection + FOV calibration).
   - Web ground station with MJPEG stream and browser dashboard.
   - Passive watch mode for safe data collection.
   - Synthetic dataset generator (300 syn + 50 neg + 16 real).
   - 41 test scripts in 6 categories with numbered flight progression.
   - Lens distortion calibration and automatic undistortion.

4. **Creativity** (non-obvious solutions):
   - Config auto-detect (serial port = real, no serial = SITL, zero code changes).
   - Headless browser control (terminal keys or browser buttons, same codebase).
   - BGR discovery (tested all 6 channel permutations).
   - Inverse-variance weighted GPS estimation with spatial clustering.

### Decision Making (40%) -- what "confidence and creativity in adapting" means:

Every adaptation story must follow: **Problem --> Response --> Evidence --> Outcome.**

- Weather cancelled flight --> pivoted to bench testing + DJI video analysis. Extracted FOV calibration, altitude-detection data, GPS scatter statistics from recorded video.
- Python 3.13 broke tflite-runtime --> found ai-edge-litert replacement, verified identical inference (206ms, 0.966 confidence).
- Camera BGR despite RGB888 label --> tested all 6 permutations, documented.
- GPS 100-200ms latency --> quantified via video analysis (CEP50=2.3m), planned speed*lag compensation.
- Pi serial broken on Python 3.13 --> mavproxy UDP bridge, bonus: enables Mission Planner parallel connection.

**Evidence-based = numbers, not claims:**
- 206.5ms avg inference, 4.8 FPS, 50/50 detection at 0.966 confidence.
- FOV: 9 samples, 15-50m altitude, focal length 1416px +/- 41, HFOV 54.4 deg.
- Lens calibration: RMS 0.399, undistortion cost 1.5ms.
- Model retraining: mAP50 0.995 on 366-image dataset.
- GPS accuracy: CEP50=2.3m, max error 16.5m.

### Communication (20%) -- what "engaging, professional, innovative" means:

**Diagrams that earn marks:**
- State machine diagram (11 states, 32 transitions).
- System architecture block diagram.
- Lawnmower pattern with polygon overlay.
- Hardware wiring schematic.
- CV pipeline flow: frame --> resize --> inference --> NMS --> bbox --> GPS estimation.
- Software module dependency graph.

**Tables:**
- Requirements verification matrix (R01-R12).
- Benchmark comparison table.
- STEEPLE analysis table.
- MCDA / trade-off tables.

**Formatting:**
- Professional LaTeX, consistent headings.
- Figures captioned and cross-referenced.
- GPS scatter plots, confusion matrices, training curves.
- Real photos of hardware, screenshots of ground station.

### Our current D6 score estimate: 85.2/100
- Specialist 86, Decision 87, Communication 80
- **Communication is the bottleneck** -- needs hardware photos + screenshots for +2-4 marks

---

## D7 Individual Reflective Report -- Page Limits

**Max length:** 5 pages (excluding cover page and appendices).
**Submission:** Individual PDF.
**Assessment:** Appendix B rubric + AHEP4 standards M5, M7, M16, M17.

> **"DETAIL TO FOLLOW"** -- appears with bright yellow highlight in the PDF. Steve said he would issue a "draft update first thing next week." As of 2026-04-03, this has NOT been issued.

### AHEP4 Standards (must explicitly address all four)

**M5.** Design solutions for complex problems that evidence some originality and meet a combination of societal, user, business and customer needs. Consideration of health/safety, diversity, inclusion, cultural, societal, environmental, commercial matters, codes of practice, industry standards.

**M7.** Evaluate environmental and societal impact of solutions to complex problems (entire life-cycle). Minimise adverse impacts.

**M16.** Function effectively as individual, and as member or leader of a team. Evaluate effectiveness of own and team performance.

**M17.** Communicate effectively on complex engineering matters with technical and non-technical audiences. Evaluate effectiveness of methods used.

### Suggested Page Budget (5 pages)

| Section | Pages | Content |
|---------|-------|---------|
| Intro + role description | 0.5 | Your role, team context, project summary |
| Design and originality (M5) | 1.0 | Key design decisions, originality, STEEPLE-style considerations |
| Impact and ethics (M7) | 0.5 | Environmental/societal impact, lifecycle, mitigation |
| Teamwork and leadership (M16) | 1.0 | Leadership examples, flexibility, conflict, team evaluation |
| Communication (M17) | 0.5 | Methods used, what worked, what didn't |
| Self-development and insight | 1.5 | Strengths/weaknesses, learning programme, autonomy, feedback to others |

---

## D7 Assessment Rubric (Appendix B -- EXACT wording, ALL bands)

**Note:** Unlike D6, the D7 rubric does NOT show explicit percentage weights for the three criteria.

### Teamwork

| Band | Marks | Descriptor |
|------|-------|------------|
| Fail | 0, 7, 15, 22, 29, 35 | Little or no demonstration of ability to work within a team setting. |
| Third | 42, 45, 48 | Shows limited ability to work within a team setting. |
| 2:2 | 52, 55, 58 | Shows ability to work with others and contribute productively as a member of a team. |
| 2:1 | 62, 65, 68 | Works effectively within a team, recognising the value and contributions of others. Able to manage conflict. |
| First | 72, 75, 78 | Consistently demonstrates effective teamworking and leadership skills and able to ensure teams work effectively to meet their obligations and goals. Able to manage conflict. |
| High First | 83, 94, 100 | Shows outstanding ability to work and lead a team with creativity and flexibility that is responsive to group members' interests and the obligations and goals of the team. Able to manage conflict. |

**Key progression:** 62-68 = "works effectively, recognises others, manages conflict". 72-78 = adds "leadership skills" + "ensures teams meet goals". 83+ = "outstanding" + "creativity and flexibility" + "responsive to group members' interests".

### Self-management

| Band | Marks | Descriptor |
|------|-------|------------|
| Fail | 0, 7, 15, 22, 29, 35 | Shows very limited evidence of self-organisational skills and behaviours and ability to meet deadlines. |
| Third | 42, 45, 48 | Shows limited evidence of self-organisational skills and behaviours and ability to meet deadlines. |
| 2:2 | 52, 55, 58 | Shows some evidence of self-organisational skills and behaviours. Able to complete most tasks by deadlines. |
| 2:1 | 62, 65, 68 | Demonstrates good self-organisational skills and behaviours. Has a professional attitude to completing tasks. |
| First | 72, 75, 78 | Works autonomously demonstrating very good self-organisational skills and behaviours. Has a professional attitude to completing tasks. |
| High First | 83, 94, 100 | Works autonomously demonstrating outstanding self-organisational skills and behaviours. Has a professional attitude to completing all tasks. |

**Key progression:** 62-68 = "good" + "professional attitude". 72-78 = "very good" + "works autonomously". 83+ = "outstanding" + "completing ALL tasks" (not just "tasks").

### Insight

| Band | Marks | Descriptor |
|------|-------|------------|
| Fail | 0, 7, 15, 22, 29, 35 | Shows very limited awareness of own strengths and weaknesses. |
| Third | 42, 45, 48 | Displays limited awareness of own strengths or weaknesses. |
| 2:2 | 52, 55, 58 | Shows some ability to identify own strengths and weaknesses. Some evidence of capacity to plan self-development to improve practical and professional skills. |
| 2:1 | 62, 65, 68 | Confident in self-reflection and expressing own strengths and weaknesses and able to take a proactive approach to self-development to improve practical and professional skills. |
| First | 72, 75, 78 | Demonstrates ability to work autonomously and assess own strengths and weaknesses. Demonstrates ability to identify and implement an effective programme of self-development to improve practical and professional skills. |
| High First | 83, 94, 100 | Shows confidence in working autonomously and setting own goals. Can assess own strengths and weaknesses. Able to identify and implement an effective programme of self-development to improve practical and professional skills. Can provide effective feedback to others to aid their self-development. |

**Key progression:** 72-78 = "implement effective self-development programme". 83+ = adds "setting own goals" + "feedback to others to aid THEIR self-development". The differentiator for top marks is helping OTHER people grow, not just yourself.

---

## D7 -- What 90+ Looks Like in Practice

### Teamwork -- specific evidence needed:
- Leadership: took initiative on entire software stack, set the development roadmap, created progressive testing methodology.
- Flexibility: adapted to different skill levels -- built web-based ground station so non-coders could participate, created FIELD_QUICK_REF.md for anyone to run scripts.
- Responsiveness: structured work so hardware and software teams could progress in parallel, created clean interfaces (vision.py API, config.py auto-detect).
- Conflict management: GIVE SPECIFIC EXAMPLES with outcomes (compromise, data-driven decisions, deferring to expertise).

### Self-management -- specific evidence needed:
- Multiple concurrent workstreams managed (CV training, state machine, ground station, hardware integration, documentation, testing).
- Professional discipline: CLAUDE.md as ground truth, 16+ docs, blueprints, version control discipline, never breaking main branch.
- Autonomous working: simulation-first development, Docker Pi test, identified and resolved blockers independently (BGR/RGB, Python 3.13 TFLite, mavproxy serial).
- Follow-through from design through implementation, testing, field deployment, and documentation.

### Insight -- specific evidence needed:
- **Strengths (honest):** rapid prototyping, simulation-first methodology, modular architecture, systematic testing, documentation habits.
- **Weaknesses (honest):** tendency to build solo rather than delegate, over-engineering (2500-line simulator), needed to learn "good enough" vs perfect, underestimated hardware integration.
- **Self-development:** learned MAVLink from scratch, edge AI deployment (TFLite, NCNN, quantisation), safety-critical software design, web ground control, lens calibration.
- **Feedback to others:** how you helped team members learn ArduPilot/Mission Planner, documentation that enabled others to run tests, structured GitHub workflow for the team.

### AHEP4 standards in practice:

**M5 (Design with originality):**
- Simulation-first, dual-backend CV, auto-detecting config, headless ground station, progressive testing.
- STEEPLE: safety (geofencing, kill switch, progressive testing), environmental (SSSI, battery lifecycle, noise), legal (CAA, licensing), ethical (false negatives in SAR = life-or-death).

**M7 (Environmental/societal impact, full lifecycle):**
- Positive: SAR drones reduce search time, cover inaccessible terrain, operate in poor visibility.
- Negative: battery production/disposal, e-waste, noise disturbance to wildlife, AI training energy.
- Mitigation: efficient YOLOv8n (3.2MB), edge inference (no cloud), geofencing for SSSI, mission abort.
- Lifecycle: manufacturing --> deployment --> maintenance --> disposal of drone + Pi + batteries.

**M16 (Own and team effectiveness):**
- Own: simulation-first saved weeks; modular design enabled rapid iteration. BUT: solo bottleneck, could have pair-programmed more.
- Team: honest assessment of dynamics, workload distribution, communication, adaptation to setbacks. Plus/delta format.

**M17 (Communication methods + evaluate):**
- Methods: GitHub, 16+ docs, web ground station, presentations (PDR, FDR), live demos.
- What worked: web GCS excellent for non-technical stakeholders, documentation prevented context loss.
- What didn't: too much documentation can overwhelm, verbal updates sometimes faster.

### Our current D7 score estimate: 83-84/100
- Teamwork 83, Self-management 84, Insight 83

---

## How Much Depends on a Successful Flight?

### D6 (Group Report):
The rubric says "technologies and approaches selected and implemented highly effectively" -- it focuses on implementation quality, not flight success. A simulation-validated implementation with extensive testing should qualify for top marks. BUT: the rubric is ambiguous about whether "implemented" requires physical demonstration.

**Our reading:** Simulation is implementation. We have end-to-end runs, benchmarks, field bench tests, DJI video analysis, model retraining, and Pi hardware verification. The PROCESS and EVIDENCE are there even without a polished outdoor flight. The 72-78 band requires "initiative and autonomy" (we have this). The 83+ band adds "creativity" (we have this too).

**Risk:** If the marker interprets "implemented" as "flew outdoors successfully," our Specialist score might cap around 72-78 despite the software quality justifying 83+.

### D7 (Individual Report):
D7 is about PERSONAL REFLECTION, not technical achievement. The rubric never mentions flight success. It evaluates teamwork, self-management, and insight. Hardware setbacks are actually GOOD material for reflection (how you adapted, what you learned, honest self-assessment). D7 score should be independent of flight outcome.

---

## Requirements Verification -- Evidence Needed Per Requirement

| R | Core Ask | Evidence We Have | Gap |
|---|----------|-----------------|-----|
| R01 | Fly within Flight Area | Geofence code + SITL flight logs showing no excursion | No outdoor flight log |
| R02 | No SSSI fly-over | SSSI polygon in geofence + cv2.pointPolygonTest + unit tests | No outdoor flight log |
| R03 | Take off within 5m of TOL | GPS log from SITL, TOL coords in config | No outdoor GPS log |
| R04 | Max 50m altitude | Config TARGET_ALT=35m + flight log altitude trace | SITL only |
| R05 | Search and identify items | Lawnmower pattern + detection log + DJI video analysis | No live outdoor detection log |
| R06 | PLB Focus Area redirect | Dynamic replanning code + SITL test | No outdoor test |
| R07 | Land 5-10m, deploy kit, RTH | GPS estimation (CEP50=2.3m) + landing logic + descent stall bug | Landing zone accuracy unverified outdoors |
| R08 | Justify autonomy level | Autonomy trade-off analysis in report | Complete |
| R09 | RTH + motor cutoff + failsafes | RC kill switch, RTL button, link-lost handler | Tested on bench, not in flight |
| R10 | Report lat/lon + images | Detection log format, verification imagery | From simulation/DJI video, not live flight |
| R11 | Designated pilot + safety pilot | Named in introduction | Complete |
| R12 | Public GitHub, MIT licence | Repo URL + licence file | Complete |

**Summary:** R08, R11, R12 are fully evidenced. R01-R07, R09-R10 have SITL/bench/analysis evidence but lack outdoor flight data.

---

## STEEPLE Quick Reference (for D6 Design Rationale)

| Factor | Key Content |
|--------|-------------|
| **S**ocial | SAR saves lives, public trust in autonomous drones, operator-in-the-loop for ethical oversight |
| **T**echnological | Edge AI limits (206ms inference), GPS accuracy (CEP50 2.3m), global shutter for motion |
| **E**conomic | Pi 5 vs Jetson cost, open-source stack (zero software cost), reusable for other SAR teams |
| **E**nvironmental | SSSI no-fly zone protection, battery life vs coverage, noise impact on wildlife |
| **P**olitical | UK CAA regulations, university flight permissions, autonomous weapon public concerns |
| **L**egal | MIT licence (R12), data protection (casualty imagery), operator liability |
| **E**thical | False negative risk (missing casualty), false positive cost (wasted time), AI decision transparency |

---

## What's UNCLEAR (Questions for Steve)

### D6 Questions:
1. Does "implemented highly effectively" require outdoor flight data, or does simulation-validated + bench-tested + video-analysed count?
2. How important are hardware photos/screenshots for Communication? Hard requirement or nice-to-have?
3. Are appendices read by markers? Brief says "will NOT be assessed" but also says to "include excerpts in main sections." Does this mean markers will reference appendices if pointed to from the main text?
4. Is there a specific balance expected between the 4 body sections (Design Rationale, System Description, Requirements Verification, Evaluation)?
5. How does peer weighting work exactly? (Brief says "details to follow" -- have these been issued?)

### D7 Questions:
1. Where is the "draft update" Steve promised? Has it been issued? The brief still says "DETAIL TO FOLLOW" with yellow highlight.
2. Are the 3 rubric criteria (Teamwork, Self-management, Insight) equally weighted (33/33/33)?
3. Is there a specific structure expected? Should we follow M5-M7-M16-M17 order, or organise around the 3 rubric criteria?
4. What distinguishes 83+ from 72-78 in practice? The rubric language differences are subtle.

### Assessment Fairness Questions:
1. Steve said he would "take into account" our hardware situation -- how specifically? Verbal assurance or written adjustment to marking?
2. Can we achieve 90+ despite limited outdoor flight data?
3. Will simulation-validated results be credited the same as outdoor-tested results?
4. The equipment provision timeline was significantly compressed -- is there an explicit marking adjustment for this?

---

## Our Concern

We believe our software quality justifies top marks (85%+). But we are worried that:

1. **Demo gap.** The demonstration will not be as polished as teams who had 8 weeks more hardware access. Our D5 demonstration may look weaker even though our underlying system is more sophisticated.

2. **Evidence gap.** Lack of outdoor flight data might cap our D6 Specialist Skills score. Requirements R01-R07 all have SITL/bench evidence but no outdoor flight logs. If the marker requires outdoor evidence, we are capped at 72-78 regardless of software quality.

3. **Perception gap.** The gap between what we COULD have demonstrated and what we will actually demonstrate is entirely due to hardware provision timing, not effort or capability. This is beyond our control.

4. **No written confirmation.** We need Steve's hardware accommodation in writing, not just verbal. Verbal assurances are forgotten at marking time.

**Action required:** Get written confirmation from Steve before submission that simulation-validated, bench-tested, and video-analysed evidence will be credited equivalently to outdoor flight data, given the hardware provision constraints.

---

## Common Mistakes to Avoid

### D6:
1. Describing what you built without saying WHY. Every paragraph needs decision rationale.
2. Listing features without evidence. "We tested it" is worthless. "4.8 FPS at 0.966 confidence over 50 runs" is evidence.
3. Putting teamwork evaluation in D6. D6 is technical performance only. Teamwork goes in D7.
4. Exceeding 15 pages. Markers may stop reading.
5. Weak executive summary. Must stand alone -- a reader who reads ONLY the exec summary should know what you built, how well it works, and key results.
6. No STEEPLE. The brief explicitly requires it. Missing it loses easy marks.
7. Vague requirements verification. Each R needs: what it requires, how you verified, result.
8. Not declaring AI usage. Category 2 (Minimal) for reporting.

### D7:
1. Describing the project instead of reflecting. The marker knows what SAR drones are. Focus on YOUR experience, decisions, growth.
2. Being uncritical. "Everything went great" scores low. Show genuine weaknesses and what you learned.
3. Ignoring AHEP4 codes. Explicitly reference M5, M7, M16, M17 -- the marker looks for these.
4. Treating teamwork superficially. "We worked well together" is not enough. Concrete examples with outcomes.
5. Forgetting lifecycle in M7. Not just "drones help people" -- discuss manufacturing, energy, disposal.
6. Not evaluating communication methods (M17). Don't just list them -- assess which were effective and why.

---

## Mark Band Summary (both deliverables)

| Band | D6 Marks | D7 Marks | What it means |
|------|----------|----------|---------------|
| Fail | 0-35 | 0-35 | No evidence of competence |
| Third | 42-48 | 42-48 | Limited evidence, weak deployment |
| 2:2 | 52-58 | 52-58 | Some understanding, limited ability |
| 2:1 | 62-68 | 62-68 | Effective, confident, evidence-based |
| First | 72-78 | 72-78 | Initiative, autonomy, leadership, effective self-development |
| High First | 83-100 | 83-100 | Creativity, outstanding, innovative, helps others develop |

**Note on mark boundaries:** Marks within each band are representative (e.g., 83, 94, 100), not boundaries. There are gaps at 79-82 and 95-99 -- these ranges are never assigned.
