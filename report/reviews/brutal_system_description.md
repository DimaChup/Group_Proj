# Brutal Review: System Description (Section 3)

**Score: 72/100**

---

## What Works Well

1. **Comprehensive scope.** Covers hardware, software architecture, CV pipeline, search pattern, state machine, localisation, ground station, and simulation -- all the subsystems a marker would expect. Nothing obviously missing from the table of contents.

2. **Quantitative throughout.** Error budget table (Tab 2), benchmark numbers (206.5 ms, 4.8 FPS), CEP50 = 2.3 m, strip spacing derivation, 91% overlap calculation, RMS calibration, MJPEG latency. The section earns credibility by backing claims with numbers.

3. **Figures are well-chosen.** 12 figures/subfigures total. The geofence 4-panel (Fig 6), GPS bullseye + directional error (Fig 9), and estimator comparison (Fig 11) are exactly what a marker wants to see. The state machine diagram (Fig 7) is essential and present.

4. **Error budget table.** This is the strongest part of the section. Six sources, two altitudes, RSS total, notes column. This is MSc-level systems engineering, not just code description.

5. **Equation for coverage guarantee.** Eq (1) ties sensor width, focal length, altitude, and overlap to strip spacing. Shows the design is analytically grounded, not trial-and-error.

---

## Weak Spots and Issues

### CRITICAL

**C1. Architecture diagram is not described in enough detail.**
The text says "four layers" and lists them with bullet points, but the description is extremely compressed. A reader seeing Figure 2 for the first time would struggle to understand data flow. Which module calls which? What data flows between them? The bullet list names modules but does not explain *interfaces* or *data contracts*. The `detect_in_image()` interface is mentioned in the CV subsection but not here where it belongs.

**C2. State machine description is too compressed for 20 states.**
Four bullet points cover 20 states. States like HOVER, RETURN_TO_SEARCH, RETURN_FROM_MANUAL are not mentioned at all. The engagement sequence (CENTERING -> DESCENDING -> VERIFY -> APPROACH -> HOVER_TARGET) deserves a paragraph explaining the operator interaction model and timeouts, not a single compressed line. The "detection queue with spatial deduplication" is mentioned in one sentence but never explained -- how does the 5 m reject radius work? How is lazy validation implemented?

**C3. No figure for the ground station UI.**
The ground station subsection (3.7) describes a "three primary panels" dashboard but provides ZERO screenshots or mockups. This is a browser-based interface that the operator must use during flight -- the reader has no idea what it looks like. A screenshot of the dashboard with labelled panels would be worth 200 words of text.

### HIGH

**H1. CV pipeline mixes architecture and results.**
The pipeline description (Sec 3.3) includes benchmark results (206.5 ms, 4.8 FPS, 100% detection rate, 0.966 confidence) that belong in the Testing/Results section. The system description should describe *what* the pipeline does and *how*, not *how well*. Performance numbers here pre-empt the evaluation section and create redundancy.

**H2. Three backends claimed, only one tested.**
The CV subsection mentions NCNN ("~15 FPS expected"), Ultralytics, and TFLite. But NCNN is described with "expected" -- it was never benchmarked on Pi. The section presents three backends as equivalent but only one was validated. This is misleading. Either remove the NCNN FPS claim or explicitly state it is untested.

**H3. Simulation framework undersells itself.**
Sec 3.8 is a single paragraph listing four levels. This is actually a strong contribution (multi-fidelity simulation with same codebase) but gets no dedicated figure, no comparison table, and no explanation of what each level catches. The bugs caught are listed in a sentence fragment. A table with columns [Level | What it tests | Bugs caught | Limitations] would elevate this.

**H4. Missing figure: communication topology.**
The Pi-to-Cube-to-GCS communication path (UART -> MAVProxy -> UDP/TCP -> Pi scripts / Mission Planner) is described in prose only. Fig 3 (pi_system) may cover this, but the text does not reference it in the communication paragraph. The MAVProxy bridge is a non-trivial architectural decision (necessary because pyserial is broken on Python 3.13) and deserves explicit visual treatment.

**H5. Search pattern algorithm needs pseudocode or clearer figure.**
The "rotate-rasterise-zigzag-rotate-back" description is dense. Five numbered steps crammed into a single paragraph. A pseudocode block or algorithm figure would make the approach reproducible. The Bezier-smoothed U-turns are mentioned but never explained or illustrated.

### MEDIUM

**M1. Hardware table missing weight.**
The BOM table lists cost but not weight. For a drone, total takeoff weight is a critical system parameter that affects flight time, manoeuvrability, and safety. Add a weight column or state AUW somewhere.

**M2. No timing diagram for the main loop.**
The "five stages per iteration" pipeline is described in prose but has no timing breakdown. How much of the 208 ms is inference vs. preprocessing vs. state dispatch? The latency_breakdown.pdf figure exists in figs/ but is not referenced anywhere in this section.

**M3. Geofence subsection could reference the code review finding.**
The sign convention for `cv2.pointPolygonTest` (positive = INSIDE, not outside) was a discovered bug. Mentioning this in the context of safety-critical geofencing would show engineering rigour and honest self-assessment.

**M4. Overlap calculation uses different speed than config.**
Line 119 says "nominal search speed of 8 m/s (altitude-dependent schedule at 35 m)" which is correct per config.py's interpolation. But the overlap calculation ("adjacent frames overlap by ~91%") is not shown. The reader cannot verify 91%. Show the math: at 8 m/s and 4.8 FPS, inter-frame distance = 1.67 m. Ground footprint width along flight direction at 35 m = 5.02*35/5.46 = 32.2 m. Overlap = 1 - 1.67/32.2 = 94.8%. The claimed 91% does not match -- check this.

**M5. "Eleven Python modules" claim.**
Line 46 says "eleven Python modules totalling approximately 4,400 lines." The actual codebase has more than 11 .py files in the root. Is this counting only the core modules? State which 11. If it includes test scripts, the architecture claim is wrong. If it excludes them, say so.

---

## Missing Figures/Charts

| Missing | Impact | Notes |
|---------|--------|-------|
| Ground station screenshot | HIGH | Sec 3.7 describes 3 panels, reader sees nothing |
| Communication topology diagram | HIGH | UART/UDP/TCP paths are complex |
| Latency breakdown bar chart | MEDIUM | `latency_breakdown.pdf` EXISTS in figs/ but is never referenced |
| Search pattern pseudocode/algorithm | MEDIUM | 5-step algorithm is dense prose |
| Simulation level comparison table | MEDIUM | 4 levels listed in prose, no structure |
| Hardware photo (drone assembled) | LOW | Shows integration quality |
| Detection examples (positive + negative) | LOW | What does a detection look like at 35 m? |

---

## Factual Accuracy Check

| Claim | Verdict | Notes |
|-------|---------|-------|
| 20-state FSM | CORRECT | states.py has exactly 20 states |
| Confidence threshold 0.2 | CORRECT | config.py CONFIDENCE_THRESHOLD = 0.2 |
| 49.3 deg HFOV | CORRECT | 2*atan(5.02/(2*5.46)) = 49.3 deg |
| 8 m/s at 35 m | CORRECT | Linear interpolation: 6 + (35-20)/(50-20)*4 = 8 |
| 206.5 ms inference | CORRECT | Matches benchmark results in MEMORY.md |
| CEP50 = 2.3 m | CORRECT | Matches video analysis results |
| 91% overlap | SUSPECT | Math gives ~95% at 8 m/s and 4.8 FPS. Check source. |
| 11 modules, 4400 LOC | UNVERIFIED | Count the actual modules and lines |
| RSS = 2.9 m | CORRECT | sqrt(2.3^2 + 1.5^2 + 0.6^2 + 0.5^2 + 0.5^2 + 0.01^2) = 2.89 |
| "Three backends" | MISLEADING | NCNN never tested on Pi, "~15 FPS expected" is speculative |
| Strip spacing 25.7 m | CORRECT | 32.2*(1-0.20) = 25.76 |

---

## Structural Issues

1. **Section is too long relative to weight.** At ~263 lines of LaTeX, this is probably 3-4 pages including figures. For a 15-page limit report, that is 20-27% of the budget on system description alone. Consider whether the ground station and simulation subsections could be trimmed.

2. **Redundancy with other sections.** The CV performance numbers (206.5 ms, 4.8 FPS, detection rate) will appear again in Testing/Evaluation. The model training details (mAP50=0.995) are likely in the CV/ML section. State this once, reference it elsewhere.

3. **Subsection ordering.** Hardware -> Software -> CV -> Search -> State Machine -> Localisation -> Ground Station -> Simulation. This is logical but the state machine (the core orchestrator) is buried at position 5/8. Consider promoting it or making the ordering follow the mission timeline.

---

## Actionable Fixes (Priority Order)

1. **Add ground station screenshot** (Fig reference in Sec 3.7). One figure replaces 100 words of panel descriptions.
2. **Reference latency_breakdown.pdf** somewhere -- it already exists.
3. **Expand state machine** by 3-4 sentences covering the engagement workflow and operator decision points.
4. **Remove or qualify NCNN FPS claim.** Say "untested" or remove the number entirely.
5. **Verify the 91% overlap claim** -- the math suggests ~95%.
6. **Add a simulation comparison table** (4 rows, 3-4 columns).
7. **Clarify "11 modules"** -- list them or at least state what counts.
8. **Move benchmark results** from CV subsection to Testing section; keep only architecture/design here.

---

## Final Verdict

Solid engineering content with good quantitative backing and a strong error budget analysis. Falls short on visual communication (missing ground station screenshot, unreferenced latency breakdown, no communication topology) and compresses the state machine and simulation framework into too-small spaces. The 91% overlap claim needs verification. The NCNN "expected" figure should be qualified or removed. With the fixes above, this could reach 82-85.
