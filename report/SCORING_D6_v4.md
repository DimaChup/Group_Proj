# D6 Company Report Scoring -- v4 Multi-Dimensional Assessment

Scored: 2026-03-27
Sections assessed: exec_summary, design_rationale, system_description, requirements_verification, evaluation
Main structure: main.tex (cover + exec + intro + 4 counted sections + refs + 19 appendices)

---

## 1. RUBRIC CRITERIA SCORES

### Specialist Skills & Problem-Solving (40%) -- Score: 82/100

**Strengths (pushing toward 83-100 band):**
- Complete end-to-end pipeline documented: camera -> lens undistortion -> YOLOv8n TFLite -> GPS estimation -> state machine -> landing
- Initiative demonstrated: model retrained 3 times (640, 1280, 1088), FOV calibrated from tape-measure and video, BGR colour bug discovered and fixed
- Autonomy: independent debugging of pyserial Python 3.13 regression, SRT sync issue, geofence sign errors
- Quantified throughout: mAP50=0.995, CEP50=2.3m, 206.5ms inference, 4.8 FPS, 50/50 detection, 0.966 confidence
- 58 test scripts across 6 categories -- exceptional for MSc level
- Dual-backend architecture (Ultralytics/TFLite) shows genuine software engineering maturity
- 4400 lines of code, 11 modules, clean separation of concerns

**Weaknesses (holding back from 90+):**
- No outdoor flight completed -- all verification is simulation/bench/video proxy
- Train/validation overlap acknowledged but not resolved (mAP inflated)
- No precision-recall curve for threshold selection
- Payload release not software-integrated (D8 in evaluation)

### Decision Making (40%) -- Score: 80/100

**Strengths:**
- 4 MCDA trade-off tables with weighted criteria: companion computer, communication architecture, detection model, search pattern
- STEEPLE analysis covers all 7 dimensions with specific, contextualised content (not generic)
- "Decisions That Changed" section (4 items) explicitly shows evidence-based corrections -- exactly what rubric asks for
- Autonomy level justified using Sheridan framework with asymmetric cost analysis of FP vs FN
- Weather adaptation framed as information-maximisation, not failure
- Every design choice backed by data (benchmarks, measurements, cost comparisons)
- "Why Not ROS" section pre-empts reviewer questions with 3 concrete reasons

**Weaknesses:**
- Some MCDA scores feel self-serving (Pi 5 scores 5 on nearly everything vs competitors)
- No sensitivity analysis on MCDA weights -- would changing weights change the winner?
- Missing decision documentation on some choices: why 20% overlap? why 30m NFZ buffer? why 120s verify timeout?
- No stakeholder analysis or user requirements gathering beyond the brief

### Communication (20%) -- Score: 78/100

**Strengths:**
- Professional LaTeX formatting with consistent colour scheme (headblue headers)
- 15 figures in body (programmatically generated from real data -- not hand-drawn)
- 8 tables in body sections (BOM, 4x MCDA, MAVLink commands, requirements verification, plus/delta)
- 1 equation (Rayleigh probability for landing accuracy)
- Cross-references throughout (\secref, \figref, \tabref)
- Subfigures used effectively (GPS accuracy pair, estimation pair, evaluation sensitivity pair)
- Executive summary is genuinely self-contained and information-dense
- 19 appendices provide depth without consuming page budget

**Weaknesses:**
- Some figures may be placeholder/generated rather than from real data (detection_heatmap, mission_timeline)
- No photographs of actual hardware (assembled drone, Pi setup, field day)
- No screenshot of the ground station web UI
- References count is high (118 bib entries) but many may be appendix-only citations
- Intro has [NAME] placeholders for 4 of 5 team members -- not yet complete

---

## 2. OVERALL ESTIMATED SCORE

| Criterion | Weight | Score | Weighted |
|-----------|--------|-------|----------|
| Specialist Skills | 40% | 82 | 32.8 |
| Decision Making | 40% | 80 | 32.0 |
| Communication | 20% | 78 | 15.6 |
| **TOTAL** | | | **80.4** |

**Band: 72-78 (First) -- pushing into 83-100 territory**

The report is solidly in First territory. To break into the 83+ band requires closing the gaps listed in Section 5 below.

---

## 3. CONTENT COMPLETENESS CHECKLIST

### Required Elements

| Item | Present? | Quality | Notes |
|------|----------|---------|-------|
| STEEPLE analysis | YES | STRONG | All 7 dimensions with specific references (WCA 1981, CAA, SORA). Not generic. |
| MCDA trade-off tables | YES (4) | STRONG | Companion computer, comms architecture, detection model, search pattern. All weighted. |
| R01-R12 all verified | YES | STRONG | Full traceability table + subsection per requirement. Evidence column populated. |
| Plus/delta evaluation | YES | EXCELLENT | 9 plus items + 9 delta items, each with evidence and "next step". Honest about limitations. |
| Real figures | 15 body | GOOD | Programmatically generated (gen_*.py scripts). Some may lack real flight data backing. |
| Tables | 8 body | GOOD | BOM, 4x MCDA, MAVLink commands, req verification, plus/delta |
| Equations | 1 body | ADEQUATE | Rayleigh distribution for landing probability. Could use more. |
| Citations | ~25 unique in body | GOOD | 118 total bib entries. Body sections cite ~25 unique keys. |
| Benchmark data with methodology | YES | STRONG | 50-run Pi benchmark, DJI video analysis, model comparison |
| Error analysis / uncertainty | PARTIAL | GOOD | CEP50=2.3m, GPS timing lag analysed, but no formal uncertainty propagation |

### Counts Summary

| Element | Body Sections | Appendices | Total |
|---------|--------------|------------|-------|
| Figures (\includegraphics) | 15 | many more | 15+ |
| Tables (\begin{table}) | 8 | many more | 8+ |
| Equations | 1 | likely more | 1+ |
| Unique citations (body) | ~25 | ~118 total bib | 118 bib entries |
| Appendices | -- | 19 | 19 |

---

## 4. SECTION-BY-SECTION ASSESSMENT

### Executive Summary (excluded from page count)
- **Quality: 9/10** -- Genuinely self-contained. Covers objective, system overview, key decisions, quantitative results, and weather adaptation. Specific numbers throughout. The "14 figures" and "20 states" callouts are good. Could mention team size and R01-R12 compliance more explicitly.

### Design Rationale (~4 pages counted)
- **Quality: 9/10** -- Strongest section. STEEPLE is specific and referenced. 4 MCDA tables. "Decisions That Changed" is excellent evidence of adaptation. Autonomy justification with Sheridan levels + asymmetric cost analysis is sophisticated. "Why Not ROS" pre-empts questions. Camera selection rationale is thorough.
- **Missing:** Sensitivity analysis on MCDA weights.

### System Description (~5 pages counted)
- **Quality: 8/10** -- Comprehensive architecture description. Good use of figures (architecture, pi_system, cv_pipeline, state_machine, GPS plots, mission timeline). BOM table and MAVLink command table are useful. Target localisation with Kalman filter + inverse-variance weighting is well explained.
- **Missing:** Hardware photograph, ground station screenshot, wiring diagram in body (likely in appendix).

### Requirements Verification (~3 pages counted)
- **Quality: 8.5/10** -- Clean traceability table. Every requirement gets a subsection with specific evidence. The per-flyover detection probability calculation (P_miss = 5e-15) is an excellent quantitative touch. R07 landing probability analysis using Rayleigh distribution is strong.
- **Missing:** Photo evidence of bench testing. R06 PLB not field-tested. R08 payload not wired in.

### Evaluation (~3 pages counted)
- **Quality: 9/10** -- Exceptionally honest. 9 plus + 9 delta items, each with specific evidence and actionable next steps. Acknowledges train/val overlap inflating mAP. Acknowledges missing outdoor flight. 4 lessons learned are genuine engineering insights. Weather cancellation framed as positive adaptation. Sensitivity figures (conf vs alt, det vs speed, latency breakdown, detection heatmap) add quantitative depth.
- **Missing:** Comparison to other teams' approaches or commercial SAR systems.

---

## 5. WHAT'S STILL MISSING -- RANKED BY IMPACT

### HIGH IMPACT (could move score from 80 to 85+)

| # | Item | Type | Why It Matters |
|---|------|------|----------------|
| 1 | **Hardware photographs** (assembled drone, Pi mounted, camera, field setup) | Figure | Rubric says "images recommended" in system description. No real photos anywhere in body. |
| 2 | **Ground station screenshot** (browser dashboard with MJPEG + GPS grid + buttons) | Figure | Proves the system exists beyond text description. |
| 3 | **MCDA sensitivity analysis** (vary weights +/-10%, check if winner changes) | Table/paragraph | Strengthens "evidence-based decisions" claim. Takes 2 sentences. |
| 4 | **Team member names** (4 placeholders say [NAME]) | Text | Report is incomplete without this. Looks unfinished. |
| 5 | **Detection examples figure** (side-by-side: detection at 15m, 30m, 50m altitude) | Figure | Shows the model working at different altitudes with bounding boxes. Powerful visual proof. |
| 6 | **Confusion matrix** from model training (already exists in cv_models/) | Figure | Standard ML reporting. 1/4 page, high density. |

### MEDIUM IMPACT (polish, could add 2-3 marks)

| # | Item | Type | Why It Matters |
|---|------|------|----------------|
| 7 | **Precision-recall curve** at different confidence thresholds | Figure | Directly addresses D4 delta. Shows rigour in threshold selection. |
| 8 | **Code architecture table** (module, lines, purpose, dependencies) | Table | Quantifies 4400 LOC across 11 modules. Shows scale. |
| 9 | **More equations** -- GSD formula, FOV geometry, Kalman filter state update | Equation | Currently only 1 equation in body. 3-4 would show mathematical depth. |
| 10 | **Geofence diagram** in body (currently only referenced as fig:geofence-diagram) | Figure | R02 is the highest-risk requirement. Visualising 4 protection layers is powerful. |
| 11 | **Comparison to commercial/academic SAR drones** (DJI Matrice, academic papers) | Table | Shows awareness of the broader field. References exist in SAR_COMPARISON.md. |
| 12 | **Power budget / endurance analysis** | Table | How long can the drone fly? Battery capacity vs consumption rate. Mission time estimate. |
| 13 | **Weight budget table** (airframe + Pi + camera + battery + payload = AUW) | Table | Standard systems engineering deliverable. |

### LOW IMPACT (nice-to-have, diminishing returns)

| # | Item | Type | Why It Matters |
|---|------|------|----------------|
| 14 | **Gantt chart or project timeline** | Figure | Shows project management maturity. Brief mentions it in D1 suggestions. |
| 15 | **Risk register table** (risk, likelihood, impact, mitigation) | Table | Referenced implicitly in evaluation but never shown. |
| 16 | **Communication latency measurement** (MAVLink round-trip timing) | Data | Mentioned in verification outline but no actual measurement reported. |
| 17 | **Search pattern figure** (lawnmower overlaid on search polygon) | Figure | Referenced as fig:search-pattern in R05 but may not exist in figs/. |
| 18 | **FOV calibration methodology figure** (tape measure setup, checkerboard photo) | Figure | Shows the actual calibration process, not just results. |
| 19 | **Training data examples** (synthetic vs real vs negative samples side by side) | Figure | Shows domain randomisation visually. Already have the images. |
| 20 | **Boustrophedon algorithm pseudocode** | Algorithm box | Shows the rotate-rasterise-rotate-back method formally. |
| 21 | **Network/comms diagram** (Pi <-> MAVProxy <-> Cube <-> RC, Pi <-> WiFi <-> GCS) | Figure | Clarifies the multi-consumer MAVProxy architecture. |

---

## 6. FIGURE AUDIT

### Figures referenced in body sections (15 total):

| Figure | File | Status | Real Data? |
|--------|------|--------|------------|
| mission_overview | mission_overview.pdf | EXISTS | Generated (gen_mission_overview.py) |
| architecture | architecture.pdf | EXISTS | Diagram (gen_architecture.py) |
| pi_system | pi_system.pdf | EXISTS | Diagram (gen_pi_system.py) |
| cv_pipeline | cv_pipeline.pdf | EXISTS | Diagram (gen_cv_pipeline.py) |
| state_machine | state_machine.pdf | EXISTS | Diagram (gen_state_machine.py) |
| gps_bullseye | gps_bullseye.pdf | EXISTS | Generated from DJI video data |
| gps_error_direction | gps_error_direction.pdf | EXISTS | Generated from DJI video data |
| gps_convergence | gps_convergence.pdf | EXISTS | Generated from DJI video data |
| estimator_comparison | estimator_comparison.pdf | EXISTS | Generated from DJI video data |
| mission_timeline | mission_timeline.pdf | EXISTS | Generated (gen_mission_timeline.py) |
| conf_vs_alt | conf_vs_alt.pdf | EXISTS | From DJI video analysis |
| det_vs_speed | det_vs_speed.pdf | EXISTS | From DJI video analysis |
| latency_breakdown | latency_breakdown.pdf | EXISTS | From Pi benchmark data |
| detection_heatmap | detection_heatmap.pdf | EXISTS | Generated (gen_detection_heatmap.py) |
| geofence_diagram | geofence_diagram.pdf | EXISTS | Diagram (gen_geofence_diagram.py) |

All 15 figures exist as PDFs. All are programmatically generated (gen_*.py scripts in figs/). 4-5 are based on real measurement data (GPS bullseye, convergence, conf vs alt, det vs speed, latency breakdown). The rest are architectural/schematic diagrams. None are photographs of real hardware.

### Missing figure files (referenced but potentially absent):
- `fig:search-pattern` -- referenced in R05 verification. Check if search_pattern.pdf exists.

---

## 7. REFERENCES AUDIT

- **118 bib entries** in references.bib
- **~25 unique citations** in body sections
- **Key citations present:** YOLOv8, ArduPilot/MAVProxy, Sheridan (autonomy levels), Choset/Galceran (coverage planning), Murphy (SAR drones), UK CAA, WCA 1981, SORA, Goodrich (HRI), ROS, TFLite, domain randomisation, edge AI, lens calibration
- **Missing citations that would strengthen the report:**
  - ArduPilot Copter firmware documentation
  - Raspberry Pi 5 technical reference
  - Kalman filter original (Kalman 1960) or textbook reference
  - OpenCV documentation
  - IAMSAR Manual (referenced in text but not in citations list -- check)
  - picamera2 documentation

---

## 8. COMPARISON TO RUBRIC TOP BAND (83-100)

### Specialist Skills: "Confident and comprehensive identification; highly effective implementation showing initiative, autonomy, and creativity"
- **Confident:** YES -- quantified claims throughout
- **Comprehensive:** YES -- covers full pipeline end-to-end
- **Initiative:** YES -- model retraining, FOV calibration, video proxy analysis
- **Autonomy:** YES -- independent debugging of 12 defects
- **Creativity:** PARTIAL -- GPS estimation with inverse-variance weighting and Kalman filter is creative; the video proxy workaround for cancelled flight is creative; but no truly novel algorithmic contribution

### Decision Making: "Shows confidence and creativity in adapting to changing/unfamiliar/challenging circumstances and making effective, evidence-based decisions"
- **Adapting:** YES -- weather cancellation pivot, 4 design corrections
- **Evidence-based:** YES -- every decision backed by benchmarks or measurements
- **Creativity in adaptation:** YES -- DJI video analysis pipeline as proxy
- **Gap:** No comparison to what other teams did or how alternatives performed in practice

### Communication: "Effective, engaging, and professional, making use of innovative techniques and resources"
- **Effective:** YES
- **Engaging:** PARTIAL -- text-heavy in places, no hardware photos, no UI screenshots
- **Professional:** YES -- consistent formatting, proper LaTeX
- **Innovative techniques:** PARTIAL -- programmatic figure generation is good, but dashboard as "innovative resource" is not mentioned in the report itself

---

## 9. QUICK WINS (< 30 minutes each, highest ROI)

1. **Fill in team member names** -- 5 minutes, removes "incomplete" impression
2. **Add 2-3 hardware photos** from field day (phone photos exist?) -- 15 minutes
3. **Add ground station browser screenshot** -- 10 minutes (run pi_flight.py, screenshot)
4. **Add confusion matrix from cv_models/sar_v2_1088/** -- 10 minutes (already exists as .png)
5. **Add one sentence on MCDA sensitivity** to each trade study -- 15 minutes
6. **Add GSD equation explicitly** in system description -- 5 minutes (formula is in text but not displayed)
7. **Mention the dashboard as innovative project management tool** in intro or evaluation -- 2 minutes
8. **Add detection example images at different altitudes** from video_test.py output -- 15 minutes
