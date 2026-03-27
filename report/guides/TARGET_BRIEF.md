# D6 Company Report -- Scoring Guide

> Source: AENGM0074 Project Brief Release 2.1. This file tells you exactly what the markers want.

---

## What Gets 75+ (First Class)

### Specialist Skills & Problem-Solving (40%)

**Rubric language:** "Confident and comprehensive identification of task and challenge aspects. Appropriate technologies and approaches selected and implemented highly effectively, showing initiative, autonomy, and creativity."

**HOW TO HIT THIS:**

1. **Deep challenge identification** -- Do not just say "we built a SAR drone." Name every hard sub-problem: detection at altitude, GPS timing lag, inference speed on edge hardware, geofencing without visible markers, camera colour-space mismatch, Python 3.13 breaking TFLite. Show you understood what made each one hard.

2. **Justified technology choices** -- Every choice needs a WHY with alternatives considered:
   - YOLOv8n over YOLOv8s: 206ms inference on Pi 5 vs projected 400ms+. Real-time needed at 5 m/s.
   - TFLite over ONNX/NCNN: widest Pi support, XNNPACK CPU acceleration, proven pipeline.
   - Lawnmower over spiral: complete area coverage guarantee for SAR (no gaps), simple path verification.
   - MAVLink GUIDED over AUTO: dynamic re-planning on PLB Focus Area, state machine needs waypoint-level control.
   - Dual-backend (Ultralytics laptop / TFLite Pi): same model, same detections, develop fast on laptop, deploy lean on Pi.
   - Pi 5 over Jetson: provided hardware, but also sufficient (4.8 FPS proven).

3. **Initiative beyond requirements** -- Things we built that were not asked for:
   - Interactive simulator (simple_simulator.py) with keyboard flight, GPS estimation, Kalman filter.
   - Video analysis pipeline (DJI replay + detection + FOV calibration + GPS scatter).
   - Web ground station (pi_flight.py) with MJPEG stream, browser dashboard, headless SSH support.
   - Passive watch mode for safe manual-flight data collection.
   - Synthetic dataset generator (300 images + 50 negatives + 16 real labelled frames).
   - Comprehensive progressive test suite (41 scripts, 6 categories, numbered flight progression).
   - Lens distortion calibration and automatic undistortion in the vision pipeline.

4. **Creativity** -- Highlight non-obvious solutions:
   - Config auto-detect (serial port presence selects real vs SITL, zero code changes).
   - Headless browser control (same main.py works over PuTTY SSH with terminal keys or browser buttons).
   - BGR discovery (tested all 6 channel permutations to find IMX296 colour output).
   - Inverse-variance weighted GPS estimation with spatial clustering for multi-pass target localisation.

---

### Decision Making (40%)

**Rubric language:** "Shows confidence and creativity in adapting to changing and unfamiliar/challenging circumstances. Effective evidence-based decisions."

**HOW TO HIT THIS:**

1. **Adaptation stories** -- Each must follow: Problem --> Response --> Evidence --> Outcome.
   - Weather cancelled flight day --> pivoted to bench testing + DJI video analysis pipeline. Extracted FOV calibration, detection-altitude data, GPS scatter statistics from recorded video.
   - Python 3.13 broke tflite-runtime --> found ai-edge-litert drop-in replacement, verified identical inference (206ms, 0.966 confidence).
   - Camera output BGR despite RGB888 label --> tested all 6 permutations, fixed without cvtColor, documented for future teams.
   - GPS receiver 100-200ms latency --> quantified via video analysis (CEP50=2.3m), planned speed*lag compensation.
   - Pi serial reads broken on Python 3.13 --> mavproxy UDP bridge architecture, bonus: enables Mission Planner parallel connection.

2. **Evidence-based** -- Every claim backed by numbers:
   - Benchmark tables: 206.5ms avg, 4.8 FPS, 50/50 detection at 0.966 confidence.
   - FOV calibration: 9 samples across 15-50m altitude, focal length 1416px +/- 41, HFOV 54.4 deg.
   - Lens calibration: RMS 0.399, undistortion cost 1.5ms (negligible).
   - Model retraining: mAP50 0.995 on 366-image dataset (300 syn + 16 real + 50 neg).
   - GPS accuracy: CEP50=2.3m, max error 16.5m from DJI video analysis.

3. **Progressive testing philosophy** -- Show the 5-step flight progression as a deliberate risk-management strategy, not just caution. Each step builds trust before adding risk. Never skip a step.

---

### Communication (20%)

**Rubric language:** "Effective, engaging, and professional, making use of innovative techniques and resources."

**HOW TO HIT THIS:**

1. **Diagrams that earn marks:**
   - State machine diagram (11 states, 32 transitions) -- show the full mission flow.
   - System architecture block diagram (Pi, Cube, camera, RC, ground station, MAVLink paths).
   - Lawnmower search pattern visualization with polygon overlay.
   - Hardware wiring schematic (Pi GPIO --> Cube TELEM2, camera CSI, power).
   - CV pipeline flow: frame --> resize --> inference --> NMS --> bbox --> GPS estimation.
   - Software module dependency graph (vision.py independent, config.py central).

2. **Tables and data:**
   - Requirements verification matrix (R01-R12, method, evidence, status).
   - Benchmark comparison table (model variants, inference time, detection rate, confidence).
   - STEEPLE analysis table (factor, consideration, design impact).
   - Trade-off / MCDA tables for key decisions (detection model, search pattern, autonomy level).

3. **Formatting:**
   - Professional LaTeX with consistent heading hierarchy.
   - Figures captioned and cross-referenced.
   - Code snippets only where they illuminate (config values, interface signatures), not dumps.
   - GPS scatter plots, confusion matrices, training curves from cv_models/.

---

## Required Sections Checklist

- [ ] **Executive Summary** (1 page, self-contained, EXCLUDED from page count)
- [ ] **Introduction** (context, team bios, roles, contributions, EXCLUDED from page count)
- [ ] **Design Rationale** (STEEPLE analysis, MCDA-style justifications for every major decision)
- [ ] **System Description** (architecture, flow charts, schematics, images)
- [ ] **Requirements Verification** (R01-R12 mapped to evidence: descriptions, images, data)
- [ ] **Evaluation** (plus/delta of TECHNICAL performance only, not teamwork)
- [ ] **References** (cite research/design/code sources, EXCLUDED from page count)
- [ ] **Appendices** (NOT assessed, for completeness, EXCLUDED from page count)

---

## Page Budget (15 pages max for body)

| Section | Pages | Key Content |
|---------|-------|-------------|
| Design Rationale | 4 | STEEPLE table, decision trade-offs (model, pattern, autonomy, hardware), alternative approaches considered |
| System Description | 5 | Architecture diagram, CV pipeline, state machine, search planning, ground station, geofence, comms |
| Requirements Verification | 3 | R01-R12 matrix with method + evidence + status. Include test photos, benchmark data, screenshots |
| Evaluation | 3 | Plus/delta table, benchmark results, detection performance, GPS accuracy, what worked/what would change |

**Free pages (excluded):** Cover, Executive Summary (1p), Introduction (~2p), References (~1p), Appendices (unlimited).

---

## Requirements Quick Reference

| R | Core Ask | Evidence Needed |
|---|----------|----------------|
| R01 | Fly only within Flight Area | Geofence code + flight log showing no excursion |
| R02 | No SSSI fly-over | SSSI polygon in geofence + cv2.pointPolygonTest |
| R03 | Take off within 5m of TOL | GPS log of takeoff position vs TOL coords |
| R04 | Max 50m altitude | Config TARGET_ALT + flight log altitude trace |
| R05 | Search area, identify items | Lawnmower pattern + detection log with images |
| R06 | Receive PLB Focus Area, refocus | Dynamic re-planning code + demo/test evidence |
| R07 | Land 5-10m from casualty, deploy kit, RTH | GPS estimation accuracy + landing logic + payload release |
| R08 | Justify autonomy level | Autonomy trade-off analysis (full auto vs supervised) |
| R09 | RTH + motor cutoff + failsafes | RC kill switch, RTL button, link-lost handler, GCS commands |
| R10 | Report lat/lon + images | Detection log format, verification appendix with imagery |
| R11 | Designated pilot + safety pilot | Named in introduction, roles described |
| R12 | Public GitHub, MIT licence | Repo URL, licence file, flight logs committed |

---

## STEEPLE Factors to Cover

| Factor | Example Content |
|--------|----------------|
| **S**ocial | SAR saves lives, public trust in autonomous drones, operator-in-the-loop for ethical oversight |
| **T**echnological | Edge AI inference limits (206ms), GPS accuracy (CEP50 2.3m), camera global shutter for motion |
| **E**conomic | Pi 5 vs Jetson cost, open-source stack (zero software cost), reusable for other SAR teams |
| **E**nvironmental | SSSI no-fly zone protection, battery life vs search coverage, noise impact on wildlife |
| **P**olitical | UK CAA drone regulations, university flight permissions, autonomous weapon concerns |
| **L**egal | MIT licence (R12), data protection (casualty imagery), operator liability |
| **E**thical | False negative risk (missing a casualty), false positive cost (wasted time), AI decision transparency |

---

## Common Pitfalls (Avoid These)

1. **Describing what you built without saying why.** Every paragraph needs a decision rationale.
2. **Listing features without evidence.** "We tested it" is worthless. "4.8 FPS at 0.966 confidence over 50 runs" is evidence.
3. **Putting teamwork evaluation in D6.** D6 is technical performance only. Teamwork goes in D7.
4. **Exceeding 15 pages.** Markers may stop reading. Use appendices for overflow.
5. **Weak executive summary.** It must stand alone. A reader who reads ONLY the exec summary should know: what you built, how well it works, and what the key results are.
6. **No STEEPLE.** The brief explicitly requires it in Design Rationale. Missing it loses easy marks.
7. **Vague requirements verification.** Each R needs: what it requires, how you verified, what the result was. Use a table.
8. **AI usage not declared.** Category 2 (Minimal) for reporting. Acknowledge any AI assistance used.
