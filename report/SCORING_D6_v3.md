# D6 Deep Scoring v3 -- All Content Included

**Date:** 2026-03-27
**Scored against:** AENGM0074 D6 Rubric (Level 7), Release 2.1
**Report structure:** 4 body sections (Design Rationale, System Description, Requirements Verification, Evaluation) + 16 appendices

---

## Current Grade Estimate: 78-82 (upper first-class band, approaching top band)

---

## 1. Specialist Skills & Problem-Solving (40%) -- Score: 78-82

### What scores well (72-78 territory and above)

**Comprehensive identification of task and challenges:**
- Every R01-R12 requirement identified, decomposed, and addressed with explicit verification
- Six error sources in GPS estimation quantified with analytical budgets (Table in gps_estimation_deep.tex)
- Python 3.13 compatibility chain (pyserial broken -> mavproxy bridge, tflite-runtime -> ai-edge-litert) identified and resolved creatively
- BGR/RGB colour channel discovery on IMX296 -- a hardware subtlety invisible to simulation
- FOV miscalibration caught at bench (22% error, would have caused 6m offset at 30m altitude)

**Technologies selected and implemented highly effectively:**
- Dual-backend inference (Ultralytics/TFLite) with auto-detection -- genuine engineering elegance
- 20-state FSM with 32 transitions, dictionary dispatch, per-state timeouts
- Four GPS fusion strategies implemented, benchmarked, and compared (rolling avg, cumulative, Kalman, inverse-variance)
- 216-configuration parametric sweep for scan angle optimisation
- Lens calibration integrated at 1.5ms cost (0.7% of inference time)
- 58 test scripts across 8 categories -- industrially serious test infrastructure

**Initiative, autonomy, creativity:**
- Simulation-first methodology with 5-tier gated framework is genuinely novel for a student project
- Building a custom browser-based ground station rather than using QGC/MAVProxy
- DJI video replay as Tier 3 proxy when weather cancelled flights -- creative adaptation
- Synthetic dataset generation (300 syn + 16 real + 50 neg) at native resolution
- Energy model with U-turn penalties and NFZ slowdown zones

### What holds it back from 83+

1. **No outdoor flight data.** This is the single biggest penalty. The rubric rewards "implemented highly effectively" -- the system is _designed_ highly effectively but not _proven_ in the target environment. Every verification is simulation, bench, or video-replay. The evaluator will note this.

2. **Individual contribution imbalance.** The contribution table makes clear that one person (Dmytro) did essentially all technical work. While honest, this weakens the "company" narrative the brief expects. The rubric is assessing the company, not individuals.

3. **STEEPLE depth is uneven.** Social, Economic, Environmental, and Ethical are strong with specific evidence. Political (CAA A3) and Legal (WCA 1981, GDPR-adjacent) are adequate but shallow -- one paragraph each with a single citation. Technological is well-evidenced but reads more like a feature list than a STEEPLE consideration.

4. **R06 (PLB Focus Area) verification is thin.** "Implemented and verified in SITL" with no quantitative evidence. No figure showing the redirect behaviour.

5. **R07 (Land 5-10m) evidence chain incomplete.** The 7.5m offset with CEP50=2.3m argument is solid mathematically, but there is no plot or table showing the probability distribution of actual landing positions.

---

## 2. Decision Making (40%) -- Score: 76-80

### What scores well

**Evidence-based decisions:**
- Five MCDA tables (companion computer, comms architecture, detection model, search pattern, streaming protocol) with weighted criteria and numerical scores -- this is textbook evidence-based decision making
- Quantitative justification for every parameter: 35m altitude (24px target size), 20% overlap (compensates 2-3m GPS drift), 0.2 confidence threshold
- Defect discovery table (Table bug-cost) with tier, fix time, and escalation cost -- directly demonstrates risk-based decision making
- Cost-risk gradient table quantifying iteration throughput at each tier (50:1 ratio Tier 1 vs Tier 5)
- V-model mapping connecting the 5-tier framework to formal SE verification levels

**Adaptation to changing/unfamiliar/challenging circumstances:**
- Weather cancellation pivot is the strongest adaptation evidence in the report -- reframed as calibration day, produced 6 quantitative outputs
- Python 3.13 breakage chain resolved with mavproxy bridge (not downgrading Python)
- BGR colour discovery required systematic 6-permutation test -- methodical problem-solving under field pressure
- Model retrained 3 times with progressively better data (640 -> 1280 -> 1088 native resolution)
- Contingency planning with 3 deliverable tiers (MVD, target, stretch) mapped to requirements

**Confidence and creativity:**
- Inverse-variance weighting over Kalman filter, with explicit justification (physics-aligned, no convergence plateau, simplicity) -- this is a mature engineering judgment call
- Bezier-smoothed U-turns as energy optimisation
- Centre-snap optimisation bypassing GSD projection when target near image centre
- Three-layer geofence (speed field + repulsive potential + hard cutoff) -- defence-in-depth

### What holds it back from 83+

1. **MCDA tables risk looking formulaic.** Five trade-study tables with the same format could appear mechanical rather than genuinely deliberative. The evaluator may question whether these were constructed post-hoc to justify decisions already made. Adding a sentence like "We initially selected X, but the trade study revealed Y was superior because..." would add authenticity.

2. **No explicit "decision that went wrong" narrative.** The rubric rewards "adapting to challenging circumstances" -- the field day pivot is good, but there's no example of a design decision that was reversed based on evidence. The FOV calibration story _implies_ the default was wrong, but it's framed as "discovery" rather than "we chose 7.0mm based on datasheet, discovered it was wrong, and the impact would have been X".

3. **Streaming architecture appendix is overkill.** The bandwidth estimation and port allocation sections, while thorough, spend 2+ pages justifying a choice (MJPEG) that any reviewer would consider obvious for a student project. This depth would be better spent on flight-test analysis.

4. **No discussion of what would change given more time/budget.** The evaluation's "delta" section lists what wasn't done, but doesn't prioritise or estimate the effort. A "if we had 2 more weeks, we would..." discussion would show strategic thinking.

---

## 3. Communication (20%) -- Score: 80-84

### What scores well

**Effective, engaging, professional:**
- 14 figures (PDFs): architecture diagram, Pi system diagram, CV pipeline, state machine, mission timeline, GPS bullseye, GPS error direction, GPS convergence, estimator comparison, coverage vs time, plus detection heatmap, latency breakdown, confidence vs altitude, detection vs speed
- Consistent use of `compactTable` formatting, `siunitx` for units, `booktabs` for professional tables
- Blue-themed section headings, clean float placement, proper subfigure usage
- Mathematical derivations (GSD, body-frame projection, heading rotation, WGS84 conversion, Kalman filter, Bezier curves) are typeset correctly and numbered
- Tables are information-dense: BOM, MCDA tables, error budget, defect discovery, V-model mapping, test categories

**Innovative techniques and resources:**
- Plus/delta table with colour-coded P1-P8/D1-D7 entries -- visually distinctive and easy to scan
- Subfigure pairs (GPS bullseye + directional error, convergence + estimator comparison) -- good use of space
- Code snippet in streaming architecture showing the frame-lock pattern -- appropriate level of detail for an engineering report
- 16 appendices providing depth without consuming page budget

### What holds it back from 85+

1. **No photographs of the actual hardware.** The report describes assembly, wiring, and field testing but includes zero photos. A photo of the assembled drone, the Pi mounted on the airframe, the 3-terminal PuTTY setup, or the dummy on the field would dramatically increase engagement and credibility.

2. **No ground station screenshot.** The browser dashboard is described in detail but never shown. A single screenshot of the MJPEG stream with detection overlay and command buttons would be worth 500 words.

3. **Missing detection example figure.** No image shows what a detection actually looks like -- bounding box on a real or synthetic frame. The CV pipeline figure shows the _process_ but not the _result_.

4. **Page count efficiency.** The 4 body sections are dense but the allocation may not be optimal. Design Rationale (~4 pages with 5 MCDA tables) could potentially be tighter (3 pages), freeing space for a richer Evaluation discussion or a brief results subsection with detection example images.

5. **References could be stronger.** The citations include good foundational references (Choset, Galceran, Kalman, Sheridan) but are missing some obvious SAR drone papers that would show broader literature awareness. No citation for ArduPilot itself (only mavproxy).

---

## Composite Score: ~79 (range 77-82)

| Criterion | Weight | Score | Weighted |
|-----------|--------|-------|----------|
| Specialist Skills | 40% | 80 | 32.0 |
| Decision Making | 40% | 78 | 31.2 |
| Communication | 20% | 82 | 16.4 |
| **Total** | | | **79.6** |

---

## What Would Push This to 83+

### HIGH IMPACT (do these first)

1. **Add 3-4 photographs** (30 minutes of effort, +2-3 marks in Communication)
   - Assembled drone on bench/field
   - Pi camera + Cube wiring closeup
   - Ground station browser screenshot with detection overlay
   - Field day setup (laptop + PuTTY + Pi screen)
   - These go in System Description and Field Day appendix
   - _This is the single easiest improvement._

2. **Add a detection result figure** (15 minutes)
   - A single frame from DJI video replay showing the bounding box on the dummy
   - Side-by-side: raw frame vs detected frame at 35m altitude
   - Goes in System Description -> Computer Vision Pipeline or Evaluation

3. **Reframe the field day as a "decision reversed" narrative** (30 minutes, +1-2 in Decision Making)
   - In Evaluation or Design Rationale, explicitly state: "Our initial focal length of 7.0mm was derived from the lens datasheet. Field calibration revealed the true value was 5.46mm -- a 22% error that would have displaced GPS estimates by up to 6m at search altitude. This discovery validates the progressive testing methodology: the parameter was corrected before it could affect any flight-critical estimate."
   - This turns a bug into evidence of mature engineering judgment.
   - Currently it's in the Field Day appendix (not assessed) -- it MUST appear in the body.

4. **Add a detection image montage to Requirements Verification R05/R10** (20 minutes)
   - Show 4-6 detection snapshots at different altitudes (from DJI video replay)
   - With bounding boxes, confidence scores, altitude labels
   - This directly evidences R05 and R10 with imagery, which the brief explicitly requests

5. **Strengthen Evaluation discussion** (45 minutes, +1-2 in Specialist Skills and Decision Making)
   - Add a "What Would Change" subsection: prioritised list of improvements with estimated effort
   - Add explicit "lessons learned" that go beyond the plus/delta list
   - Mention the sim-to-real gap explicitly: "These results give X% confidence that outdoor performance will be within Y% of bench results because Z"
   - Currently the Evaluation is honest but defensive -- make it _reflective_

### MEDIUM IMPACT

6. **Bring key appendix content into the body** (30 minutes)
   - The brief says "Appendices will NOT be assessed"
   - The defect discovery table (testing_deep.tex) is GOLD for Decision Making -- put a condensed version (top 5 defects) in Evaluation
   - The contingency tiers (MVD/Target/Stretch) show strategic thinking -- summarise in 1 paragraph in Design Rationale
   - The error budget table (gps_estimation_deep.tex) is strong evidence -- put it in System Description -> Target Localisation

7. **Add one more citation per STEEPLE dimension** (20 minutes)
   - Political: cite the actual CAA CAP 722 (not just "caa2024uas")
   - Legal: cite UK GDPR for data protection claim
   - Social: cite a specific mountain rescue team report on drone adoption barriers

8. **Tighten MCDA authenticity** (15 minutes)
   - For at least one trade study, add a sentence: "The initial prototype used [Alternative X], but [specific problem encountered] led to the trade study that selected [Winner]."
   - Companion computer is a good candidate: "The Pi 5 was the platform provided by the module, but we validated this choice against alternatives to understand the constraints it imposes."

### LOWER IMPACT (polish)

9. **Add ArduPilot citation** -- it's the core flight stack and uncited

10. **Number the appendices consistently** -- currently A1, A2, then named sections. Use A through P consistently with descriptive titles.

11. **Cross-reference body to appendices more aggressively** -- the body should say "see Appendix K for the full defect table" etc. Currently some appendices feel disconnected.

12. **Executive Summary could mention the field day pivot** -- currently it doesn't mention weather cancellation or adaptation, which is one of the strongest Decision Making stories.

---

## Figure Inventory (14 PDFs + generators)

| Figure | Used In | Status |
|--------|---------|--------|
| architecture.pdf | System Description (Fig 1) | In body |
| pi_system.pdf | System Description (Fig 2) | In body |
| cv_pipeline.pdf | System Description (Fig 3) | In body |
| state_machine.pdf | System Description (Fig 4) | In body |
| mission_timeline.pdf | System Description (Fig 5) | In body |
| gps_bullseye.pdf | System Description (Fig 6a) | In body |
| gps_error_direction.pdf | System Description (Fig 6b) | In body |
| gps_convergence.pdf | System Description (Fig 7a) | In body |
| estimator_comparison.pdf | System Description (Fig 7b) | In body |
| coverage_vs_time.pdf | Path Planning (appendix only!) | NOT in body |
| conf_vs_alt.pdf | ? | Check if referenced |
| det_vs_speed.pdf | ? | Check if referenced |
| detection_heatmap.pdf | ? | Check if referenced |
| latency_breakdown.pdf | ? | Check if referenced |

**WARNING:** `coverage_vs_time.pdf`, `conf_vs_alt.pdf`, `det_vs_speed.pdf`, `detection_heatmap.pdf`, and `latency_breakdown.pdf` appear to exist but may only be used in appendices or not at all. If they show detection performance data, they MUST appear in the body (Evaluation or System Description) to score Communication marks.

---

## Missing Content Checklist

| Item | Priority | Impact | Where to Add |
|------|----------|--------|--------------|
| Hardware photographs | CRITICAL | +2-3 Communication | System Description, Field Day |
| Ground station screenshot | CRITICAL | +1-2 Communication | System Description / Ground Station |
| Detection result image | HIGH | +1-2 Specialist Skills | CV Pipeline or Evaluation |
| Detection montage at multiple altitudes | HIGH | +1 Specialist Skills | Requirements Verification R05/R10 |
| Defect table excerpt in body | HIGH | +1-2 Decision Making | Evaluation |
| Error budget table in body | HIGH | +1 Specialist Skills | System Description |
| Contingency tiers summary in body | MEDIUM | +1 Decision Making | Design Rationale |
| "Decision reversed" narrative | MEDIUM | +1 Decision Making | Evaluation |
| "What would change" subsection | MEDIUM | +1 Decision Making | Evaluation |
| Sim-to-real confidence statement | MEDIUM | +1 Specialist Skills | Evaluation |
| conf_vs_alt / det_vs_speed figures in body | MEDIUM | +1 Communication | Evaluation |

---

## Path Planning Section NOT in Body

**IMPORTANT:** `05_path_planning.tex` is a well-written 4-page section with equations, a parametric sweep, energy analysis, Bezier smoothing, and a coverage comparison table -- but it is NOT included in the main body via `\input{}`. It exists only as a standalone file. The body's System Description has a 1-paragraph summary of the search pattern in `system_description.tex`.

**Decision:** The body is already dense. Adding the full path planning section would push well beyond 15 pages. However, consider:
- Moving the coverage_vs_time figure into the body (System Description or Evaluation)
- Adding path planning as a numbered appendix (it's currently orphaned)
- Referencing the appendix from the body: "The path planning algorithm is detailed in Appendix X"

---

## Bottom Line

The report is technically outstanding for a student project. The depth of the GPS estimation mathematics, the 5-tier testing framework, the MCDA trade studies, and the dual-backend architecture would be credible in a professional engineering report. The weakness is _tangibility_: no flight, no photos, no screenshots. The assessor reads about an impressive system but never _sees_ it. Adding 4-5 images and pulling 2-3 key tables/figures from appendices into the body would push this from "strong first" (78-80) into "top band" (83+) territory.
