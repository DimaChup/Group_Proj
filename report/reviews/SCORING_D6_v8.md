# D6 Goldmine Report Scoring --- v8 (233 pages, 0 LaTeX errors)

**Date:** 2026-04-04
**Assessed sections:** Executive Summary, Design Rationale (~4pp), System Description (~5pp), Requirements Verification (~3pp), Evaluation (~3pp)
**Appendices:** 34 appendices (A--AH), referenced but not directly scored

---

## Overall Score: 86.3 / 100

| Axis | Score | Previous (v7) |
|------|-------|---------------|
| Specialist Knowledge | 89 | 86 |
| Decision Making | 88 | 87 |
| Communication | 82 | 80 |
| **Weighted Average** | **86.3** | **84.3** |

---

## Axis 1: Specialist Knowledge --- 89/100

### Evidence of Strength

1. **CV pipeline depth.** The report demonstrates genuine understanding of YOLOv8n internals: anchor-free detection across three FPN scales (8x/16x/32x), the [1,5,8400] output tensor semantics, XNNPACK delegate selection, and the pixel-vs-normalised coordinate ambiguity (Section 3.3). The pixel-coordinate heuristic (threshold > 1.5) is a real engineering insight, not textbook knowledge.

2. **GPS estimation pipeline.** The pinhole camera model is correctly applied with GSD derivation (Eq. 1), body-frame-to-NED rotation via heading, WGS84 conversion. The error budget decomposition (6 sources, RSS = 2.9m at 35m) shows quantitative understanding of sensor fusion. CEP50 = 2.3m from DJI video replay is a concrete, reproducible metric.

3. **Search parameter optimisation.** The 216-configuration parametric sweep with physics-based energy model is well beyond typical student work. The parameter derivation chain (Table 4) traces every operating value to a physical measurement through 8 steps --- detection ceiling -> altitude -> speed -> lane spacing -> scan angle -> NFZ buffer -> coverage -> energy.

4. **Geofence architecture.** Five independent protection layers (waypoint filtering, speed ramp, repulsive field, hard cutoff, firmware fence) with clear descriptions of signed-distance computation via cv2.pointPolygonTest. The explanation of why repulsive offset runs AFTER the state handler shows genuine system-level thinking.

5. **Edge inference knowledge.** TFLite vs NCNN vs ONNX Runtime comparison with actual benchmark numbers (206.5ms vs 72ms). XNNPACK delegate, FP16 dispatch potential, INT8 quantisation trade-offs discussed with specificity.

6. **Camera physics.** Global vs rolling shutter analysis with quantified parallelogram distortion (7.5px at 5m/s, 30m altitude). Lens distortion calibration (RMS 0.399, +1.5ms overhead). BGR/RGB888 mislabelling discovery and resolution.

7. **MAVLink protocol.** Table 3 lists specific MAVLink commands with correct message types. MAVProxy UDP bridge architecture explained with baud rate, port topology, and the Python 3.13 pyserial regression as root cause.

### What's Still Weak

- **Kalman filter details are thin in the body.** The KF on [phi, lambda] state vector is mentioned but the process noise model, measurement noise scaling, and convergence behaviour are deferred entirely to Appendix K. A 2-sentence summary of the noise model would strengthen the body.
- **No formal coverage proof.** The coverage guarantee claim ("guaranteeing every ground point falls within at least one swath") lacks a mathematical proof in the body. The 20% overlap and 2-3m GPS drift are stated but the geometric argument is not shown.
- **Thin on ArduPilot internals.** The report uses ArduPilot but doesn't discuss EKF2/EKF3 state estimation, barometric altitude correction, or how the autopilot's own position estimate interacts with the companion computer's GPS projection.
- **No discussion of wind effects on search pattern accuracy.** The lawnmower pattern assumes perfect waypoint tracking; real GPS guidance has cross-track error that could reduce effective overlap.

### What Would Push It Higher (89 -> 93+)

- Add 3-4 sentences on the Kalman filter noise model in the localisation subsection
- Include a brief geometric proof or diagram of the overlap guarantee under worst-case GPS drift
- Discuss ArduPilot EKF interaction with the companion computer's GPS estimate
- Quantify cross-track error under wind and its effect on coverage overlap

---

## Axis 2: Decision Making --- 88/100

### Evidence of Strength

1. **Four MCDA trade studies.** Companion computer (Table 2), communication architecture (Table 5), detection model (Table 6), and search pattern (Table 7) --- all with pre-set weights, 1-5 scoring, and weighted totals. Sensitivity analysis (+/-0.05 weight perturbation, 12 scenarios) confirms Pi 5 retains rank in every case. This is textbook MCDA done properly.

2. **Seven evidence-based corrections.** Section 2.11 documents decisions that changed when empirical data contradicted assumptions: focal length (7.0 -> 5.46mm), BGR colour space, camera resolution (640x480 -> 1456x1088), TFLite bbox interpretation, geofence sign inversion, TFLite runtime package, serial communication. Each follows: original decision -> evidence -> revision -> outcome. This is the strongest section in the report for demonstrating engineering judgement.

3. **Alternatives genuinely considered.** Section 4.4 (Evaluation of Design Choices) critically examines Pi 5 vs Jetson, Python+MAVLink vs ROS 2, lawnmower vs adaptive search, single-class vs multi-class detector, and simulation-first timing. The self-criticism of simulation-first ("10 weeks before hardware was powered on... excessive for a fixed-deadline project") is refreshingly honest.

4. **Autonomy level justified with cost asymmetry analysis.** The Sheridan Level 7-8/3-4 hybrid is justified by analysing false-positive vs false-negative costs, with specific energy penalties (90s descent cycle = 8% battery, 6.0 Wh per hover = 5.2%). The 120s timeout is derived from the energy budget, not arbitrary.

5. **Behaviour tree and reactive architecture rejection.** Quantitative argument: zero concurrent branches in the mission graph -> O(n log n) BT tick reduces to O(1) FSM dispatch with no functional benefit. The persistent state memory argument for multi-phase missions is technically sound.

6. **Why not ROS.** Three concrete reasons with numbers: 2GB disk vs 50MB, 0.5-2ms per message hop, 40-60hr learning curve = 25% of dev time. Not dismissive but proportionate.

7. **Train/validation overlap acknowledged.** The evaluation honestly flags mAP50 = 0.995 as an upper bound (D5), estimates realistic mAP at 0.85-0.90 from video detection rate, and includes footnotes on Table 8 marking the caveats. This is mature self-assessment.

### What's Still Weak

- **MCDA weights not justified from requirements.** The weights (e.g., 0.30 for inference speed, 0.25 for accuracy) are stated but the rationale for these specific numbers is missing. Why is speed weighted 0.30 and not 0.25? A brief sentence linking each weight to a requirement would close this gap.
- **No rejected alternatives for the geofence architecture.** The five-layer geofence is described but no alternative approaches (e.g., virtual fence in firmware only, simple boundary check) are compared.
- **Missing decision on landing strategy.** The 7.5m offset landing is mentioned but the rationale for this specific distance (vs 5m or 10m) is not in the body. It presumably relates to R07's 5-10m requirement but this should be explicit.

### What Would Push It Higher (88 -> 92+)

- Add 1 sentence per MCDA table linking weights to requirements
- Brief comparison of geofence approaches (firmware-only vs software-only vs hybrid)
- Explicit derivation of the 7.5m offset from R07 + GPS accuracy + safety margin
- Consider adding a decision matrix for the landing strategy (direct vs offset vs centering-then-offset)

---

## Axis 3: Communication --- 82/100

### Evidence of Strength

1. **Logical flow.** The report follows a clear problem -> design -> implementation -> verification -> evaluation arc. Design Rationale justifies choices, System Description shows how they're realised, Requirements Verification maps to R01-R12, Evaluation critically assesses results. Each section explicitly references the previous one (e.g., "With the design rationale established (Section 2), this section describes how those choices are realised").

2. **Rich figure set.** The body sections contain 15+ figures: mission overview map, architecture diagram, Pi system diagram, geofence visualisation, CV pipeline, coupling matrix, altitude-speed trade-off, coverage vs time, state machine diagram, GPS bullseye, GPS error direction, confidence vs altitude, detection rate vs speed, latency breakdown, detection heatmap, and mission timeline. All have descriptive captions.

3. **Tables are well-structured.** STEEPLE assessment (Table 1), BOM (Table 2), MAVLink commands (Table 3), parameter derivation chain (Table 4), MCDA tables (Tables 2, 5, 6, 7), requirements verification (Table 8), plus/delta (Table 9), SAR comparison (Table 10), mission metrics (Table 11), five-tier testing (Table 12). Good density without clutter.

4. **Appendix referencing is systematic.** Nearly every body paragraph references a specific appendix for deeper detail (e.g., "Appendix K documents the full 15-stage pipeline", "Appendix E details the full five-tier methodology"). The 1-page Appendix Guide at the start of appendices is a helpful navigation aid.

5. **Professional formatting.** Consistent use of SI units (\SI{}{}), proper mathematical notation, numbered equations, colour-coded section headers, compact tables.

6. **Honest language.** "The system remains incompletely validated", "mAP50 likely overestimates", "the 10-week delay to hardware was excessive" --- the evaluation avoids self-congratulation.

### What's Still Weak

1. **No hardware photographs.** The entire report describes physical hardware (Pi 5, camera, hexacopter, Cube Orange+, field day setup) but contains zero photographs. Every figure is a diagram, chart, or generated visualisation. One photo of the assembled drone, one of the Pi+camera mount, and one of the field day bench setup would significantly increase credibility and visual variety. This is the single biggest communication weakness.

2. **System Description is dense.** At ~5 pages with 7 subsections, 5 figures, and 3 tables, this section packs enormous information density. Paragraphs like the geofence enforcement description (Section 3.2, lines 89-91) are 10+ lines of unbroken text. Breaking these into shorter paragraphs or using a numbered list would improve readability.

3. **Requirements Verification is too brief relative to its importance.** At ~1 page of body text plus Table 8, this section does its job but feels rushed. The "late-stage code improvements" paragraph reads like a changelog rather than a verification narrative. R05 (the most important requirement --- search and detect) gets 2 lines in the table.

4. **Executive Summary could be tighter.** At 27 lines, it's comprehensive but slightly long. The "Architecture" paragraph recites internal details (20-state FSM, 32 transitions, four MCDA trade studies) that belong in the body, not a summary.

5. **Evaluation comparison table (Table 10) caveats are buried.** The footnotes explaining that mAP50 = 0.995 is an upper bound and CEP50 is from video replay are easy to miss. These are critical caveats that should be in the main text, not footnotes.

6. **Inconsistent figure referencing style.** Some figures are referenced as "Figure X" and others as "(Figure X)" or "see Figure X". Minor but noticeable.

7. **No detection example images.** The body describes detection at 0.966 confidence, 50/50 bench frames, DJI video analysis --- but never shows what a detection looks like. A 2x2 montage (true positive at different altitudes, false positive, missed detection) would be high-value evidence.

8. **The plus/delta table (Table 9) is very long.** 10 plus items and 9 delta items with full evidence descriptions makes this table span most of a page. Consider condensing to top 5 of each and moving details to the discussion paragraphs that follow.

### What Would Push It Higher (82 -> 88+)

- **Add 2-3 hardware photographs** (assembled drone, Pi+camera mount, field day setup). This alone is worth +3 marks.
- **Add a detection montage figure** showing example detections at different altitudes/conditions.
- **Break up the densest paragraphs** in System Description (geofence enforcement, localisation).
- **Expand Requirements Verification** by 0.5 pages: give R05 and R07 (the highest-risk requirements) 2-3 sentences each explaining the evidence chain, not just the table entry.
- **Move SAR comparison caveats** from table footnotes to body text.
- **Tighten the Executive Summary** by 5-7 lines (remove internal architecture details).

---

## Requirements Verification Check (R01-R12)

| Req | Addressed? | Evidence Quality | Gap |
|-----|-----------|-----------------|-----|
| R01 | Yes | Strong --- KML polygon, runtime pointPolygonTest, emergency RTL, SITL telemetry | None |
| R02 | Yes | Strong --- five-layer NFZ, SITL multi-angle approach | None |
| R03 | Yes | Adequate --- KML point, distance check at arming | Minor: no outdoor GPS verification |
| R04 | Yes | Strong --- config validation, navigation cap, 28 unit tests, firmware fence | None |
| R05 | Yes | Adequate --- simulation + DJI video proxy | Major: no real flight detection data |
| R06 | Yes | Adequate --- SITL only, beacon-delay flag | Moderate: not field-tested |
| R07 | Yes | Moderate --- probability analysis + SITL smoke test | Major: no outdoor landing accuracy data |
| R08 | Yes | Strong --- Sheridan framework, cost asymmetry analysis | None |
| R09 | Yes | Strong --- 3 independent override paths, RC override on hardware | None |
| R10 | Yes | Adequate --- detection images + JSON saved per event | Minor: only bench-verified |
| R11 | Yes | Adequate --- checklist + field-day bench test | Procedural only |
| R12 | Yes | Strong --- public repo, MIT LICENSE file | None |

**Summary:** All 12 requirements addressed. 7 have strong evidence, 4 adequate, 1 moderate. The biggest gaps are R05 and R07 (no outdoor flight data), which the report honestly acknowledges. The absence of flight data is the single largest weakness across all three axes.

---

## Is the Evaluation Genuinely Critical?

**Yes, substantially.** Key evidence of genuine self-criticism:

1. Flags mAP50 = 0.995 as inflated (D5), provides a realistic estimate of 0.85-0.90
2. Acknowledges no outdoor flight (D1) as "the single largest gap"
3. Criticises own simulation-first strategy timing ("10-week delay to hardware was excessive")
4. Notes GPS timing lag is characterised but uncompensated (D3)
5. Acknowledges confidence threshold was chosen "by visual inspection rather than a precision-recall curve"
6. Admits payload release is "not wired into the state machine" (D8)
7. The SAR comparison table includes footnotes marking caveats on own results
8. States "bench results suggest outdoor operation will require parameter tuning" --- hedged, not overclaiming

**Minor concern:** The 10 "plus" items outnumber the 9 "delta" items, and the plus items get slightly more text. The balance could be improved by condensing the plus items and expanding delta discussion.

---

## Does the Report Flow Logically?

**Yes.** The progression is:

1. **Exec Summary** --- mission, architecture, key results, field integration status
2. **Design Rationale** --- STEEPLE -> search parameters -> hardware selection -> software architecture -> model selection -> search pattern -> FSM -> autonomy level -> decisions that changed
3. **System Description** --- hardware platform -> software architecture -> CV pipeline -> search pattern -> state machine -> target localisation -> ground station -> simulation
4. **Requirements Verification** --- R01-R12 table + analysis of gaps
5. **Evaluation** --- plus/delta -> discussion -> SAR comparison -> design choice critique -> mission metrics -> future work -> testing summary -> closing assessment

Each section builds on the previous and forward-references the next. The only structural issue is that Design Rationale covers some implementation detail (parameter derivation chain with specific numbers) that arguably belongs in System Description --- but this is a minor overlap, not a flow problem.

---

## Claims Without Evidence

1. **"74 test scripts"** --- claimed repeatedly but no appendix shows the full list with descriptions (Appendix O is referenced but not verified here). If Appendix O exists and is complete, this is fine.
2. **"Over 100 hours of simulation"** --- stated in Evaluation but no log or time-tracking evidence supports this specific number.
3. **"87% single-pass detection rate"** --- from DJI video replay, but the methodology for computing this (what counts as a "pass", what ground truth was used) is not described in the body.
4. **"Two-pass detection probability ~98%"** --- assumes independence between passes, which is acknowledged but the actual correlation is not estimated.
5. **"300ms video latency"** --- stated for the ground station but no measurement methodology described.

None of these are fabricated --- they all have plausible sources --- but the evidence chains could be tighter.

---

## Summary of Recommendations (Prioritised by Mark Impact)

| Priority | Action | Estimated Impact |
|----------|--------|-----------------|
| 1 | Add 2-3 hardware photographs (drone, Pi mount, field day) | +3 Communication |
| 2 | Add detection montage figure (TP at different altitudes, FP, miss) | +2 Communication, +1 Specialist |
| 3 | Expand R05 and R07 verification narratives (2-3 sentences each) | +1 Decision Making |
| 4 | Justify MCDA weights from requirements (1 sentence per table) | +1 Decision Making |
| 5 | Add Kalman filter noise model summary (2-3 sentences) | +1 Specialist |
| 6 | Break up densest paragraphs in System Description | +1 Communication |
| 7 | Tighten Executive Summary by removing internal details | +0.5 Communication |
| 8 | Move SAR comparison table caveats to body text | +0.5 Communication |

**Total potential improvement with items 1-4: approximately +5-7 marks across axes.**

---

## Final Assessment

This is a strong MSc-level technical report that demonstrates genuine engineering competence. The design rationale section is particularly impressive --- the 216-configuration parametric sweep, four MCDA trade studies with sensitivity analysis, and seven evidence-based corrections show systematic engineering judgement rarely seen at this level. The evaluation is genuinely critical, honestly flagging the mAP inflation, missing flight data, and excessive simulation phase duration.

The two systemic weaknesses are: (1) zero hardware photographs in a hardware project, and (2) the compression of requirements verification into a single table without narrative depth for the highest-risk requirements. Both are fixable in under 2 hours and would push the score to ~89-90.

The absence of outdoor flight data is the elephant in the room, but the report handles it well: the field-day bench results, DJI video proxy analysis, and progressive testing framework provide more quantitative subsystem evidence than most student projects achieve even with successful flights. The honest framing ("validation gaps, not architectural deficiencies") is the right approach.
