# D6 Company Report -- Rubric Scoring

> Scored against the AENGM0074 D6 rubric (Release 2.1).
> Sections reviewed: 00_abstract, 01_introduction, 02_system_architecture, 04_computer_vision, 05_path_planning, 06_state_machine, 10_testing, 11_field_results, 13_safety_risk.
> Date: 2026-03-27

---

## 1. Specialist Skills & Problem-Solving (40%)

**Current Score: 72/100** (low first-class)

### What's Strong
- **Technology selection is thorough and well-justified.** YOLOv8n chosen over larger variants with benchmarks on target hardware. TFLite chosen over Jetson with cost/power rationale. Boustrophedon chosen over spiral/random with coverage guarantees and JSAR standard reference.
- **Initiative and autonomy are evident.** The team built a three-backend inference system (Ultralytics/TFLite/NCNN), a 216-configuration parametric path optimisation sweep, Bezier turn smoothing, lens calibration with precomputed remap matrices, FOV calibration from first principles, and a synthetic+real training pipeline.
- **Hardware-software co-design.** The IMX296 BGR discovery, Python 3.13 pyserial workaround via mavproxy, ai-edge-litert swap -- all show real engineering problem-solving on actual hardware constraints.
- **Comprehensive state machine.** 20 states, dispatch table pattern, detection queue with spatial dedup, operator-in-the-loop verification -- this is a substantial and well-structured piece of software engineering.
- **Quantitative benchmarks.** Inference timing (206.5ms, 4.8 FPS), lens calibration RMS (0.399px), FOV (49.4 deg HFOV), ground footprint overlap (96% along-track) -- numbers are precise and traceable.

### What's Missing or Weak
- **No STEEPLE analysis.** The rubric explicitly requires STEEPLE considerations in the Design Rationale section. None of the reviewed sections contain one. This is a structural gap that will cost marks.
- **No explicit "Design Rationale" section.** The rubric lists this as a required section. Design decisions are scattered across architecture, CV, planning, and state machine sections but never consolidated with STEEPLE framing.
- **Figure placeholders.** Multiple "[Figure placeholder]" boxes remain in the architecture and state machine sections. For a 50% deliverable, these must be real diagrams. The state machine diagram, module dependency graph, and CV pipeline diagram are all missing.
- **Limited creativity beyond standard approaches.** The lawnmower pattern, YOLOv8, TFLite deployment -- while competently executed -- are well-trodden paths. The rotated-mask algorithm and energy analysis show more originality, but the report doesn't emphasise what's novel vs. what's standard practice.
- **No comparison with team/peer approaches.** The brief implies a "Company" context; showing awareness of alternative approaches attempted by the team and why they were rejected would strengthen problem-solving evidence.

### To Reach 75+
1. **Add a dedicated Design Rationale section with STEEPLE analysis.** Cover: Social (SAR benefit, volunteer team accessibility), Technological (Pi vs Jetson, RGB vs thermal), Economic (sub-100 GBP compute), Environmental (SSSI protection, battery vs fuel), Political (CAA regulation), Legal (Wildlife and Countryside Act), Ethical (false positive consequences, autonomy vs human authority).
2. **Replace all figure placeholders with real diagrams.** The state machine diagram, architecture block diagram, and CV pipeline are load-bearing figures that reviewers will look for.
3. **Explicitly frame what is novel.** The rotated-mask algorithm, the three-backend auto-switching, the progressive five-tier testing methodology -- call these out as contributions more assertively.
4. **Add a brief trade-study table** for the key decisions (autopilot choice, camera choice, detection model family, communication protocol) showing alternatives considered and selection criteria.

---

## 2. Decision Making (40%)

**Current Score: 70/100** (upper second / borderline first)

### What's Strong
- **Evidence-based parameter selection.** FOV calibrated empirically (92cm at 1m -> f=5.46mm). Confidence threshold set at 0.2 with explicit rationale (false positives filtered by operator, missed detections irrecoverable). 20% overlap margin justified against GPS drift and crosswind. 35m altitude justified as detection/coverage compromise.
- **Adaptability to hardware constraints.** Python 3.13 pyserial failure -> mavproxy bridge. tflite-runtime unavailable -> ai-edge-litert. BGR/RGB mislabelling discovered empirically and resolved. Camera resolution changed from 640x480 to native 1456x1088 after calibration.
- **Adaptability to field conditions.** Weather cancelled flight -> pivoted to bench testing, FOV calibration, lens calibration, DJI video analysis. This produced more useful data than a single rushed flight attempt would have.
- **Risk-proportionate testing.** The five-tier progressive approach is well-argued as a decision framework -- each tier gates the next, reducing risk of expensive failures.
- **GPS timing lag discovery.** Identified 100-200ms lag from DJI analysis, quantified its effect (1-2m at 10m/s), and described the mitigation (spatial clustering). This shows genuine analytical engagement with unexpected data.
- **Smart detection mode.** The decision to make multi-frame confirmation optional (defaulting to single-frame for initial flights) shows thoughtful trade-off between sensitivity and precision.

### What's Missing or Weak
- **No explicit decision log or trade-off matrices.** Decisions are narrated but rarely presented as structured comparisons. A table showing "Option A vs B vs C, scored on criteria X, Y, Z" would be stronger evidence of systematic decision-making.
- **Limited evidence of decisions changing under pressure.** The field day pivot is mentioned but not framed as a decision under uncertainty. What was the go/no-go threshold? What alternatives were considered?
- **No discussion of decisions that went wrong.** Everything reads as successful. Acknowledging decisions that required revision (e.g., the initial focal length of 7.0mm that was 22% off, the initial 640x480 resolution that wasted camera capability) would show deeper reflection.
- **Confidence threshold choice (0.2) is stated but not empirically validated.** The report says it's deliberately low but doesn't show a precision-recall curve or any data on how many false positives it produces in practice.
- **Missing Requirements Verification section.** The rubric explicitly requires "Process and evidence of satisfaction of requirements." R01-R12 are never systematically verified against evidence.

### To Reach 75+
1. **Add a Requirements Verification section** with a table mapping R01-R12 to evidence (test results, code features, documentation). This is explicitly required by the rubric and currently missing entirely.
2. **Add at least one structured trade-off table.** The thermal vs RGB decision, the YOLOv8n vs YOLOv8s vs YOLOv8m comparison, or the Jetson vs Pi comparison would all work well.
3. **Frame the field day pivot as a deliberate decision.** "Weather conditions exceeded the go/no-go threshold of X. The team pivoted to bench testing, which was pre-planned as the fallback protocol. This yielded calibration data that would not have been collected during flight."
4. **Acknowledge and learn from incorrect assumptions.** The f=7.0mm -> f=5.46mm correction is a 22% error that would have corrupted every GPS estimate. This is a strong example of evidence-based correction -- present it that way.
5. **Show a precision-recall curve or ROC** for the confidence threshold, even if simulated from the DJI video analysis data.

---

## 3. Communication (20%)

**Current Score: 68/100** (upper second)

### What's Strong
- **Writing quality is high.** Sentences are clear, technical terms are defined on first use, and the prose flows logically within each section. The abstract is concise and informative.
- **Good use of equations.** FOV footprint (Eq. 1), focal length calibration (Eq. 2), lane width (Eq. 3), Bezier smoothing (Eq. 4), power model (Eq. 5) -- all well-formatted and referenced in text.
- **Tables are well-structured.** The MAVLink command table, benchmark table, state transition table, failure mode table, risk register, and flight parameters table are all clear and informative.
- **Literature review is substantial.** 25+ references spanning SAR operations, edge AI, coverage planning, object detection, and regulatory frameworks. The related work section positions the project within the field.
- **Consistent technical depth.** The report doesn't shy away from implementation detail (e.g., XNNPACK delegate, C2f backbone blocks, cv2.pointPolygonTest for signed distance) while remaining readable.

### What's Missing or Weak
- **All figures are placeholders.** This is the single biggest communication weakness. The state machine diagram, architecture block diagram, CV pipeline, and lawnmower pattern visualisation are all placeholder boxes. For a report worth 50% of the module grade, this is unacceptable.
- **No photographs of the hardware.** The rubric recommends "images" in the system description. There are no photos of the drone, the Pi setup, the camera mount, the bench test configuration, or the field day setup.
- **No screenshots of the ground station UI.** The web dashboard (MJPEG stream, buttons, GPS grid) is described in text but never shown.
- **Code snippets are used sparingly.** The dispatch table snippet in the state machine section is effective; more of this (e.g., the detect_in_image interface, the geofence distance computation) would make the architecture more concrete.
- **Report structure doesn't match the rubric.** The rubric requires: Exec Summary, Introduction, Design Rationale, System Description, Requirements Verification, Evaluation, References, Appendices. The current sections are: Abstract (not Exec Summary), Introduction, System Architecture, CV, Path Planning, State Machine, Testing, Field Results, Safety. Missing: Design Rationale, Requirements Verification, Evaluation (plus/delta).
- **No Evaluation section.** The rubric requires a "plus/delta review of system technical performance." The Discussion subsection in Field Results partially covers this but doesn't use the plus/delta format.
- **Section numbering may exceed page limit.** Eight substantive sections (architecture, CV, path planning, state machine, testing, field results, safety, plus missing design rationale and requirements verification) may exceed 15 pages. The report needs to be checked against the page budget.
- **No "innovative techniques"** in presentation. The rubric's top band mentions "innovative techniques and resources." Consider: a QR code linking to the GitHub repo and a demo video, annotated photographs with callouts, a fold-out state machine diagram, or a requirements traceability matrix with colour-coded pass/fail.

### To Reach 75+
1. **Replace every figure placeholder with a real diagram.** Priority order: (a) state machine diagram, (b) system architecture block diagram, (c) CV pipeline flowchart, (d) lawnmower pattern on satellite image, (e) ground station screenshot.
2. **Add photographs.** At minimum: the assembled drone, the Pi+camera+Cube bench setup, the field day workspace, a detection overlay screenshot from the video analysis tool.
3. **Restructure to match the rubric exactly.** Rename/merge sections to match: Exec Summary, Introduction, Design Rationale (with STEEPLE), System Description (architecture + CV + planning + state machine), Requirements Verification (R01-R12 table), Evaluation (plus/delta), Safety, References, Appendices.
4. **Add an Evaluation section in plus/delta format.** Plus: modular architecture enabled independent testing, progressive methodology caught integration issues early, operator-in-the-loop prevented false positive landings. Delta: no autonomous flight achieved, inference speed limits detection at higher speeds, GPS estimation accuracy depends on timing lag compensation.
5. **Add one "innovative" presentation element.** A QR code to the GitHub repo with a 30-second demo GIF would satisfy this criterion with minimal effort.

---

## Overall Weighted Score

| Criterion | Weight | Score | Weighted |
|-----------|--------|-------|----------|
| Specialist Skills & Problem-Solving | 40% | 72 | 28.8 |
| Decision Making | 40% | 70 | 28.0 |
| Communication | 20% | 68 | 13.6 |
| **Total** | **100%** | | **70.4** |

**Current grade: 70 (upper second-class, 2 points below first-class boundary)**

---

## Priority Actions to Reach 75+ (First-Class)

Ranked by impact per effort:

1. **[CRITICAL] Add Requirements Verification section.** Table mapping R01-R12 to evidence. Missing entirely; rubric explicitly requires it. ~2 hours.

2. **[CRITICAL] Replace figure placeholders with real diagrams.** State machine, architecture, CV pipeline, lawnmower pattern. Without these, the Communication score cannot reach 70+. ~3 hours.

3. **[CRITICAL] Add Design Rationale section with STEEPLE.** Consolidate scattered design justifications. Add STEEPLE analysis. ~2 hours.

4. **[HIGH] Add Evaluation section (plus/delta format).** Honest assessment of what worked and what didn't. ~1.5 hours.

5. **[HIGH] Add photographs and screenshots.** Hardware photos, ground station UI, detection overlays. ~1 hour.

6. **[HIGH] Restructure sections to match rubric headings.** Exec Summary (not Abstract), Design Rationale, System Description, Requirements Verification, Evaluation. ~1 hour of reorganisation.

7. **[MEDIUM] Add one trade-off table.** Pi vs Jetson, or YOLOv8n vs s vs m, or thermal vs RGB. ~30 minutes.

8. **[MEDIUM] Frame field-day pivot as a decision narrative.** ~30 minutes.

9. **[LOW] Add QR code to GitHub repo on the first page.** ~10 minutes.

Completing items 1-6 would likely move the score to 76-80 (solid first-class).
