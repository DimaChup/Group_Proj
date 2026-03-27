# CRITICAL REVIEW v3 -- Body Sections Only

**Date:** 2026-03-27
**Reviewer posture:** Hostile examiner looking for reasons to dock marks.
**Rubric focus:** Specialist Skills (40%), Decision Making (40%), Communication (20%)

---

## SECTION 1: Design Rationale -- Score: 72/100

### Weakest Paragraph

> "SAR operations directly serve community safety. The system is designed for volunteer mountain rescue teams who lack the budget for commercial platforms. An operator-in-the-loop verification stage ensures that autonomous decisions do not bypass human judgement in life-critical situations, maintaining public trust in drone-assisted SAR."

This is generic waffle. Any SAR project could paste this paragraph verbatim. It says nothing specific to YOUR design. The "Social" bullet should discuss YOUR specific operator interface, YOUR specific user group (university assessors, not mountain rescue teams -- you built a coursework drone, not a deployed product), and any stakeholder engagement or user testing you actually did (which is zero).

### Claims Lacking Evidence

1. **"approximately one-tenth the price of a DJI Matrice 30T (GBP 5,800)"** -- No citation for the Matrice 30T price. No like-for-like comparison (Matrice has thermal, RTK GPS, enterprise software). This is a misleading comparison.
2. **"The lightweight airframe (3 kg AUW) minimises noise disturbance to wildlife"** -- No noise measurement, no citation for wildlife noise thresholds, no evidence this was considered beyond a single sentence.
3. **MCDA scores are invented.** Every MCDA table has scores that appear to be assigned by the team, not derived from measurement or literature. The Jetson Nano gets "3" for Python 3.13 compatibility -- based on what? The SSD MobileNet mAP is listed as 0.88 -- from what benchmark, what dataset? None of these scores are cited or justified.
4. **"automation advantage in coverage rate is approximately 20x compared to an operator watching a live stream"** -- Citation is Goodrich 2008 but this specific 20x claim is not substantiated. What is the basis for this number?
5. **"BVLOS authorisation requires a Specific Category assessment under SORA"** -- Correct but irrelevant. You flew VLOS. This reads like padding.

### Missing Figures/Tables

- **Photo of actual assembled hardware.** You describe all these components but never show the reader what the drone looks like. This is bizarre for a hardware project.
- **System cost comparison table** (your system vs. commercial SAR drones with matched feature list).
- **STEEPLE matrix** as a proper table, not a description list. A table with columns for each dimension and rows for each design decision would be far more powerful.

### What a Skeptical Examiner Would Challenge

1. "Why are all your MCDA weights conveniently set to make your pre-chosen option win? Did you establish weights BEFORE scoring?" -- You claim "Criteria weights were established before candidate scoring" but this phrase is copy-pasted identically across ALL FOUR MCDA tables. This repetition actually undermines credibility. Show the weighting rationale or reference a team meeting where weights were agreed.
2. "You say 'no thermal imaging' is a deliberate choice, but you were given a fixed equipment list. You had no choice." The framing implies you chose NOT to use thermal when in reality thermal was never available.
3. The autonomy level section is the strongest part -- Sheridan framework, false positive/negative cost analysis, specific numbers. But it switches between Level 7-8 and Level 5 and Level 3-4 inconsistently. Pick one framework and be consistent.

### Content in Appendices That MUST Be in Body

- The **centering_analysis.tex** probability analysis is referenced from requirements verification (R07) but the derivation is in an appendix subsection. The core probability result (80% -> 99% with fusion) MUST appear in the body, either in Design Rationale or Requirements Verification.
- The **state transition table** (Appendix A) -- at least a summary or the key transitions should be in the body. 20 states and 32 transitions is a claim; the reader cannot verify it without seeing the table.

---

## SECTION 2: System Description -- Score: 68/100

### Weakest Paragraph

> "The ground station is a browser-based dashboard served by a threaded HTTP server on the Pi at port 8090, accessible from any device on the local Wi-Fi network using the Pi's built-in wireless adapter. This architecture constitutes an innovative communication technique: the operator needs only a standard web browser---no native application, no Mission Planner installation, and no platform dependency---yet receives live video, spatial awareness, and full command authority in a single view."

Calling a basic MJPEG stream served over HTTP an "innovative communication technique" is overclaiming. This is a standard approach used in every IoT project. The word "innovative" will irritate an examiner. Describe what it does, don't self-award innovation medals.

### Claims Lacking Evidence

1. **"eleven Python modules totalling approximately 4,400 lines of code"** -- No line count breakdown by module. Is this verified or estimated?
2. **"approximately 300 ms" end-to-end latency for MJPEG** -- How was this measured? With what tool? Under what network conditions?
3. **"bugs caught in simulation include a MAVLink race condition during takeoff, incorrect latitude scaling, auto-disarm timeout, and GPS timing lag"** -- These are listed but never elaborated. This is the most interesting content in the section and it's one sentence. EXPAND THIS.
4. **Strip spacing equation** and coverage guarantee -- the math is correct but there is no verification. Show the actual waypoint overlay on the search area polygon. Figure ref exists but you need to confirm the figure actually demonstrates complete coverage visually.
5. **"Kalman filter on the [phi, lambda] state vector"** -- No Kalman filter equations, no process noise model, no measurement noise model. This is a claim of sophistication without supporting evidence. Either show the filter design or call it what it probably is: a recursive weighted average.

### Missing Figures/Tables

- **Screenshot of the ground station dashboard.** You describe it in detail but never show it. This is the operator interface -- it should be a figure.
- **Screenshot of the detection overlay** (bounding box on a real or simulated frame). The reader has never seen what a detection looks like.
- **Wiring diagram / hardware integration photo.** Pi to Cube to camera to servo -- show how it connects.
- **Module line count table.** You claim 4,400 lines across 11 modules -- prove it with a breakdown.
- **Data flow diagram** showing the 5-stage pipeline with timing annotations. The text describes capture -> resize -> inference -> GPS -> geofence but a pipeline diagram with ms timings per stage would be far more compelling than prose.

### What a Skeptical Examiner Would Challenge

1. "You have 20 states but Figure state_machine only shows a simplified version. How do I know your state machine actually has 20 states and 32 transitions? Show me the full diagram or a table."
2. "Your simulation framework has 4 levels but you only tested levels 1-3. Level 4 (DJI video replay) is not a simulation level -- it's offline analysis of someone else's footage."
3. "You claim the geofence uses cv2.pointPolygonTest but this function is designed for image processing, not geodetic computation. Are you projecting GPS to pixel coordinates? What projection? What are the accuracy implications?"
4. The search pattern section claims Bezier-smoothed U-turns but never shows the smoothing or its effect on coverage. Is coverage maintained through turns?

### Content in Appendices That MUST Be in Body

- The **bug discovery table** (tab:bug-cost from testing_deep.tex) is referenced in the Evaluation section's plus/delta table but never appears in any body section. This table is your strongest evidence of engineering rigour -- it MUST be in the body. Either in System Description (showing what the simulation framework caught) or in Requirements Verification.
- The **full state machine diagram** (state_machine_full) exists as a figure file but only the simplified version is in the body. At least reference the full version or include it.
- The **five-tier testing framework table** (testing_deep.tex) -- this is claimed as a major engineering contribution but the actual table is in an appendix. A summary version must appear in the body.

---

## SECTION 3: Requirements Verification -- Score: 75/100

### Weakest Paragraph

> "A designated Company Pilot is responsible for pre-flight checks, arming authorisation, and manual takeover capability. The Safety Pilot (Flight Lab staff) retains ultimate authority via the RC transmitter at all times, as required by university flight operations policy. The Company Pilot's responsibilities include: verifying the pre-flight checklist (docs/FLIGHT_DAY_CHECKLIST.md), monitoring the ground station during autonomous flight, and being prepared to call for manual takeover. Roles are documented in Section intro_d6."

This is procedural boilerplate. R11 verification should state: WHO is the pilot (name), WHAT training they have, and WHERE is evidence they were briefed. Citing a markdown file in your repo is not verification evidence.

### Claims Lacking Evidence

1. **R05 detection probability calculation** -- "$P_{miss} = (1 - p_d)^n \leq 0.05^{19} \approx 5 \times 10^{-25}$". This assumes independent detections, which they are NOT. Consecutive frames are 91% overlapping -- they see essentially the same scene. A target missed in frame N due to camouflage or orientation is likely missed in frame N+1 too. This calculation is WRONG and an examiner will catch it.
2. **R07 probability of landing in 5-10m annulus** -- "P(5 <= r <= 10) > 99%" after fusion. This assumes Gaussian errors and a simplified uni-axial projection. The actual error distribution from your own data (CEP50=2.3m, max error=16.5m) has heavy tails that a Gaussian does not capture. The 16.5m maximum error means you have outliers that would violate R07.
3. **R01 "without approaching the flight area boundary"** -- In SITL only. On real hardware with GPS drift of 2-3m and wind, this is unverified.
4. **R06 "verified by comparing pre- and post-diversion waypoint indices"** -- This is a weak form of verification. Show the flight path plot with the diversion visible.
5. **R12 "268+ commits"** -- Commit count is not evidence of quality. This reads like padding.

### Missing Figures/Tables

- **Flight path plot for SITL** showing the drone's actual trajectory vs. the planned waypoints overlaid on the search area polygon. This is the single most important figure for R01/R02 verification and it is ABSENT.
- **Detection screenshot** from the bench test or DJI video showing bounding box, confidence, and GPS estimate overlay for R05/R10.
- **Geofence test trajectory** showing the drone approaching the SSSI boundary and being deflected -- you describe this test but show no evidence.
- **PLB diversion flight path** for R06 -- show before and after diversion on a map.
- **Ground station screenshot** with detection clusters and coordinates for R10.

### What a Skeptical Examiner Would Challenge

1. "Everything is 'Verified (SITL)' or 'Verified (simulation)'. Nothing is verified in flight. Your verification table is honest about this but an examiner will ask: if you never flew, how can you claim ANY requirement is 'verified'? SITL verification should be labelled as 'Partially verified (SITL only)' or similar."
2. "R07 landing accuracy depends on a probability model derived from DJI video data processed through YOUR pipeline -- but the DJI footage was from a different drone with a different camera. How transferable is this result?"
3. "The Sheridan levels in R08 are inconsistent with Design Rationale -- here you say Level 5/3, there you say Level 7-8/3-4."
4. "R02 four-layer geofence sounds impressive but has it been tested with actual GPS noise? In SITL, GPS is perfect. A 3m hard boundary with 2.5m CEP GPS means there's a non-trivial probability of entering the SSSI before the hard cutoff fires."

### Content in Appendices That MUST Be in Body

- The **centering vs. direct offset landing analysis** (centering_analysis.tex) is critical for R07 -- the probability derivation should be in this section, not buried in an appendix.
- The **calibration data** (FOV, lens distortion RMS) is foundational for R05 and R07 accuracy claims. At least a summary table of calibration results should appear here.
- The **config parameter table** (A2_config_params) -- key parameters like TARGET_ALT, CONFIDENCE_THRESHOLD, NFZ buffer distances are referenced but the reader has to trust your text. A compact table of safety-critical parameters would strengthen this section enormously.

---

## SECTION 4: Evaluation -- Score: 78/100

### Weakest Paragraph

> "The 58 test scripts across six categories represent an investment in verification infrastructure that exceeded what was strictly necessary for a single demonstration flight, but proved essential for diagnosing faults rapidly during the compressed bench-testing window."

Self-congratulatory. "Exceeded what was strictly necessary" -- the examiner decides what was necessary, not you. 58 scripts sounds impressive but many are trivial (camera_stream.py is ~20 lines). The evaluation should assess OUTCOMES, not count artifacts. How many of the 58 scripts actually caught a bug?

### Claims Lacking Evidence

1. **"14 publication-quality figures generated programmatically"** -- Calling your own figures "publication-quality" is poor form. Let the examiner judge.
2. **"DJI video pipeline... yielded more quantitative performance data than many projects that completed their demonstration flights"** -- This is an unsubstantiated comparison with unnamed projects. Delete it.
3. **D5 acknowledges train/val overlap** but still reports mAP=0.995 as a headline number throughout the report. If you know it's inflated, STOP leading with it. Report it with a caveat every time, or report the real-image-only performance separately.
4. **Figure refs to det_sensitivity and perf_analysis** -- These figures are generated from DJI video data but the DJI drone had a DIFFERENT camera (DJI sensor, not IMX296). The confidence-vs-altitude and detection-vs-speed curves may not transfer. This is never acknowledged.
5. **"parameter tuning rather than architectural changes"** -- This is the report's central claim but it's asserted, not demonstrated. How do you KNOW that only parameters need tuning? You've never flown.

### Missing Figures/Tables

- **Bug discovery table (tab:bug-cost).** Referenced TWICE in this section but the table itself is in testing_deep.tex (an appendix section). This is the evaluation section's most important piece of evidence and it is NOT HERE. This is a serious omission.
- **Before/after comparison** of a design correction (e.g., focal length 7.0 -> 5.46mm: show GPS estimation scatter with wrong vs. correct value).
- **Precision-recall curve** -- D4 acknowledges this is missing, but if you have DJI video data with ground truth, you CAN generate one. Do it.
- **Confusion matrix** for the retrained model -- exists in cv_models/ directory but not referenced in the body.
- **Comparison with other university SAR drone projects** or with commercial baselines. The evaluation has zero external benchmarks.
- **Timeline/Gantt chart** showing planned vs. actual milestones. The weather cancellation narrative would be far stronger with visual evidence of the schedule disruption and pivot.

### What a Skeptical Examiner Would Challenge

1. "9 plus items and 9 delta items -- very symmetrical. Did you manufacture balance? Most honest evaluations are asymmetric."
2. "P7 claims 58 test scripts as a strength. But your own D1 says you never flew. Having 58 test scripts and zero flight data is not a strength -- it suggests over-engineering of testing infrastructure at the expense of actual testing."
3. "Lesson 4 says 'schedule one flight day per week'. You had one flight day and it was cancelled. Did you attempt to rebook? If not, why not? If so, what happened?"
4. "The summary paragraph says delta items are 'operational gaps rather than architectural deficiencies'. But D8 (payload release not integrated) IS an architectural deficiency -- the servo is mounted but not wired into the state machine. That's incomplete integration, not a parameter to tune."
5. "You claim FOV calibration prevented a 3m systematic bias. But you only discovered this on the SAME day you were supposed to fly. What if you had flown before discovering it? This suggests your simulation-first methodology had a blind spot."

### Content in Appendices That MUST Be in Body

- **Bug discovery table** -- absolutely essential. Move it or duplicate it in the evaluation body.
- **Five-tier testing framework summary** -- the evaluation references progressive testing as P3/P7/P8 but never shows the framework itself. At least a compact version of the tier table must appear.
- **Field day narrative excerpt** -- the weather cancellation story is told abstractly in the evaluation. A concrete paragraph from field_day_narrative.tex (the three-terminal setup, the specific tests conducted) would add credibility.
- **Calibration results summary** -- FOV correction, lens distortion RMS, BGR discovery. These are claimed as successes but the actual numbers are scattered across appendix sections.

---

## COMPREHENSIVE FIGURE/TABLE INVENTORY

### Figures Currently in Body Sections

| Figure | Section | Status |
|--------|---------|--------|
| mission_overview | System Description | OK -- exists in figs/ |
| architecture | System Description | OK |
| pi_system | System Description | OK |
| geofence_diagram | System Description | OK |
| cv_pipeline | System Description | OK |
| coverage_vs_time | System Description | OK |
| state_machine | System Description | OK |
| gps_bullseye | System Description | OK |
| gps_error_direction | System Description | OK |
| gps_convergence | System Description | OK |
| estimator_comparison | System Description | OK |
| mission_timeline | System Description | OK |
| conf_vs_alt | Evaluation | OK |
| det_vs_speed | Evaluation | OK |
| latency_breakdown | Evaluation | OK |
| detection_heatmap | Evaluation | OK |

### Figures Generated But NOT Referenced in Body

| Figure | In figs/ | Should Be In |
|--------|----------|--------------|
| blur_vs_altitude | YES | Evaluation (D2 discussion) or System Description (CV) |
| detection_envelope | YES | Requirements Verification (R05) |
| energy_efficiency | YES | Evaluation or Design Rationale |
| nfz_margin_altitude | YES | Requirements Verification (R02) |
| rotation_comparison | YES | System Description (path planning) |
| speed_detection_energy | YES | Evaluation (speed/detection trade-off) |
| state_machine_full | YES | System Description or Appendix ref |

### Tables Currently in Body Sections

| Table | Section |
|-------|---------|
| tab:mcda-companion | Design Rationale |
| tab:mcda-comms | Design Rationale |
| tab:mcda-model | Design Rationale |
| tab:mcda-search | Design Rationale |
| tab:hw-bom | System Description |
| tab:mavlink-commands | System Description |
| tab:req-verification | Requirements Verification |
| tab:plus-delta | Evaluation |

### Tables That MUST Be Added to Body

| Table | What It Contains | Where It Should Go |
|-------|-----------------|-------------------|
| Bug discovery table (tab:bug-cost) | 12 defects, tier caught, fix time, severity | Evaluation (referenced but absent) |
| Five-tier framework summary | Tier, environment, what it verifies, risk | Req Verification or Evaluation |
| Calibration results summary | Parameter, initial, corrected, method, impact | Req Verification (R05, R07) |
| Safety-critical config parameters | Parameter, value, rationale, safety margin | Req Verification (R01-R04) |
| Confusion matrix summary | TP, FP, FN, TN from bench/video test | Evaluation (detection performance) |

### NEW Figures That Should Be Generated

| Figure | What It Shows | Why It Matters |
|--------|---------------|----------------|
| **SITL flight path overlay** | Drone trajectory on KML map with waypoints | R01/R02 verification -- most critical missing figure |
| **Ground station screenshot** | Browser dashboard with video, GPS grid, buttons | System Description -- you describe it in 200 words but never show it |
| **Detection example** | Frame with bounding box, confidence, GPS overlay | System Description / Req Verification -- prove the CV works |
| **Hardware photo** | Assembled drone with Pi, camera, labels | System Description -- readers need to see the platform |
| **Precision-recall curve** | PR curve at different confidence thresholds | Evaluation D4 -- you have the data to generate this |
| **Before/after FOV correction** | GPS scatter with f=7.0 vs f=5.46 | Evaluation -- quantify the correction's impact |
| **PLB diversion flight path** | Search pattern with mid-flight redirect shown | Req Verification R06 |
| **Geofence deflection trajectory** | Drone approaching SSSI and being repelled | Req Verification R02 |
| **Tier progression results** | Gantt-like chart showing which tiers were completed | Evaluation P3 |
| **Payload release mechanism photo** | Tarot servo mounted on airframe | System Description or Req Verification R07 |

### Data You Have But Do Not Present

| Data Source | What It Contains | Where to Use |
|------------|-----------------|--------------|
| cv_models/sar_v2_1088/confusion_matrix.png | Training confusion matrix | Evaluation or System Description (CV) |
| cv_models/sar_v2_1088/results.png | Training loss/mAP curves | Evaluation (model training) |
| Benchmark results (50-run timing) | Full timing distribution, not just mean | Evaluation P4 (show histogram) |
| DJI video detection log | Frame-by-frame detections with altitude/speed | Already used for figures but raw data tables would help |
| SITL telemetry logs | Position, altitude, state transitions over time | Req Verification R01-R04 |
| Lens calibration checkerboard | calibration_data.npz, RMS=0.399 | System Description (show calibration image pair) |
| 366 training images breakdown | Count by type, augmentation examples | System Description (CV pipeline) |

---

## OVERALL ASSESSMENT

### Combined Score: 73/100

### Top 5 Actions to Raise Score

1. **Add the bug discovery table to the body.** This is your single best piece of evidence for "initiative, autonomy, creativity" (the top rubric band). It proves your testing framework caught real bugs. Without it in the body, the examiner must take your word for it.

2. **Add a SITL flight path figure.** Without a trajectory plot overlaid on the KML zones, your R01/R02 verification is words only. This is trivially generated from SITL telemetry logs and would strengthen Requirements Verification enormously.

3. **Add a ground station screenshot and a detection example frame.** Two figures that take minutes to create but transform the System Description from abstract description to concrete evidence.

4. **Fix the R05 independence assumption.** The detection probability calculation assumes independent frames, which is physically wrong for overlapping frames. Either: (a) model correlated detections properly, (b) use the number of independent looks (non-overlapping footprints), or (c) add a caveat acknowledging the assumption and providing a lower bound with p_d from worst-case altitude/speed.

5. **Remove self-congratulatory language.** "Innovative communication technique", "publication-quality", "exceeded what was strictly necessary", "more quantitative data than many projects" -- all of these will irritate the examiner. Let the work speak.

### Structural Issue: Page Budget

You have 15 pages for 4 sections. Current estimated lengths:
- Design Rationale: ~4.5 pages (with 4 MCDA tables)
- System Description: ~5 pages (with 8+ figures)
- Requirements Verification: ~4 pages
- Evaluation: ~4 pages

**Total: ~17.5 pages. You are over budget.** You need to cut 2.5 pages. Candidates for cuts:
- Camera Selection subsection (0.5 page) -- the camera was provided, not selected. Move to appendix.
- Field Day Adaptation subsection in Design Rationale (0.5 page) -- move to Evaluation where it fits better.
- Ground station description (0.3 page) -- condense to one paragraph + screenshot.
- Simulation framework description (0.3 page) -- condense; the 4-level breakdown is appendix material.
- Autonomy level justification (0.4 page) -- excellent content but slightly verbose. Tighten.

### The Elephant in the Room

The report describes a system that has never flown. The rubric rewards "technologies selected and implemented highly effectively" -- but "implemented" implies working, not just coded. The evaluation handles this honestly, but the Design Rationale and System Description read as if the system is complete and proven. Either:
- Add explicit caveats throughout ("verified in simulation; outdoor flight pending"), or
- Lean hard into the simulation-first methodology as the deliberate engineering approach (you already do this in Evaluation -- propagate the framing to the other sections).

The Evaluation section is the strongest because it is honest. Make the other three sections equally honest and the overall score rises.
