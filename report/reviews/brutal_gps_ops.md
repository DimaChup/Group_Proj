# Brutal Review: GPS Estimation, Safety, Mission Flow, Testing, Field Day

Reviewer: Claude Opus 4.6 | Date: 2026-03-27

---

## 1. GPS Estimation Deep Dive (`gps_estimation_deep.tex`)

**Score: 78/100**

### Strengths
- Full mathematical derivation from pixel to WGS84 is rigorous and well-structured.
- Error budget table (Table 2) is excellent -- quantifies each source independently with RSS totals.
- Four fusion strategies are compared side-by-side with convergence data at N=5/15/50.
- The "Why Inverse-Variance Won" subsection is a standout: genuinely analytical rather than hand-wavy.
- Centre-snap optimisation is a clever practical detail that shows engineering judgment.

### Weaknesses
1. **Simulation numbers presented as empirical.** Table 3 (method comparison) mixes "repeated simulation trials" with "DJI video replay" but does not separate the results. The reader cannot tell which numbers come from simulation (where you control the ground truth) and which from real video (where you don't). This undermines credibility. Fix: split into two sub-tables or add a "Source" column.
2. **CEP50=2.3m claim is under-supported.** The DJI video replay is a proxy, not a controlled experiment. The "surveyed position" of the dummy is mentioned but never described -- how was ground truth established? Handheld GPS? RTK? Tape measure from a known point? The accuracy of the ground truth directly bounds the validity of the CEP claim. A 2m ground-truth error would make the 2.3m CEP meaningless.
3. **No confidence intervals on the error budget.** The sigma values in Table 2 are point estimates. Are these 1-sigma? 2-sigma? The RSS formula assumes independence -- is that validated? GPS noise and timing lag are correlated (both depend on dynamics).
4. **Missing: how many observations in the DJI replay?** "CEP50=2.3m" from how many data points? 20? 200? 2000? Statistical significance is unaddressed.
5. **Offset landing section is thin.** The 99% probability claim ("within 10m") is asserted without derivation. What distribution is assumed? If GPS errors are not Gaussian (they have heavy tails, as the 16.5m outlier shows), the 99% figure is optimistic.
6. **No discussion of multipath or urban canyon effects.** The test site is an open field, but real SAR environments include buildings, trees, water. The error budget is site-specific but presented as general.
7. **Haversine equation uses arctan instead of arcsin.** Equation 6 writes arctan(sqrt(a), sqrt(1-a)) which is the atan2 form -- technically correct but inconsistent with how Haversine is typically presented. A minor confusion risk.

### Plausible Experimental Results That Would Strengthen
- **Ground-truth survey with RTK GPS or total station** (sub-10cm accuracy). Place dummy at known coordinates. Fly 5 passes at 3 altitudes. Report CEP50/95 per altitude with N>50 per bin. This one experiment would make the entire section publishable.
- **GPS drift characterisation (static hover)**: 10 minutes of raw GPS at the test site. Report CEP50/95, maximum excursion, autocorrelation time constant. This validates the 2.3m CEP95 claim for the receiver and separates receiver noise from dynamics-induced error.
- **Heading error measurement**: compare magnetometer heading to GPS-derived track heading during straight-line flight. Report mean offset and standard deviation. This validates the +/-5 degree assumption in the error budget.
- **Altitude-stratified estimation accuracy**: report CEP50 separately for detections at 35m, 25m, 15m, 10m. Show that the 1/h^2 weighting is justified by actual improvement at lower altitude.
- **Before/after velocity correction**: same dataset, with and without the GPS lag correction. Show the directional bias disappears.
- **Convergence curve**: plot fused estimate error vs number of observations (1 to 50) for all 4 methods on real data. The current table gives only 3 snapshots.

---

## 2. Safety and Risk Management (`13_safety_risk.tex`)

**Score: 72/100**

### Strengths
- Three-layer geofence is well-described with specific parameter values.
- Failure mode table covers 8 distinct scenarios with detection methods and responses.
- SORA and CAA references are appropriate and correctly cited.
- Operator-in-the-loop verification with timeout is a sensible design.
- Risk register follows standard likelihood-severity format.

### Weaknesses
1. **Geofence is untested in flight.** The section describes the geofence software in detail but never states whether it was tested during an actual flight near the SSSI boundary. SITL testing of geofence logic is mentioned in the testing section but not here. A reader expects "tested in SITL; not yet validated in flight" -- the omission reads as evasion.
2. **No quantitative stopping distance analysis.** The speed ramp reduces to 0.3 m/s at the boundary, but what is the stopping distance at 3.0 m/s in a 10 m/s crosswind? The claim "well under one metre" is unsubstantiated. Wind loads on a 2kg hexacopter at 3 m/s groundspeed are not negligible.
3. **Failure mode table has gaps.**
   - What if GPS jumps (position spike)? The drone could teleport into the NFZ in software even if physically outside it. No mention of position-spike filtering.
   - What if the magnetometer is corrupted (nearby metal, motor interference)? The heading error propagates directly into GPS estimation and geofence waypoint following.
   - What if the operator gives a wrong classification at Verify (confirms a false positive)? The system lands on nothing.
4. **Risk register is qualitative only.** Likelihood as L/M/H without numerical probabilities. Severity as 1/2/3 without consequence descriptions. SORA requires quantitative ground risk assessment for anything beyond Open Category. The register is adequate for the project scope but should acknowledge this limitation.
5. **No discussion of cyber/software security.** The ground station runs an unauthenticated HTTP server on port 8090. Anyone on the same WiFi network can send /cmd?key=y and confirm a false target, or /cmd?key=m and take manual control. This is a real vulnerability in a field setting with shared networks.
6. **Regulatory section claims A3 but does not confirm weight class.** CAA Open Category A3 has a maximum takeoff mass (MTOM) limit. The aircraft weight is never stated in this section.
7. **"Three independent abort mechanisms" -- are they truly independent?** RC kill switch is independent (hardware). Ctrl+C and M key both go through the Pi software stack. If the Pi crashes, both are lost. The claim of independence is overstated.

### Plausible Experimental Results That Would Strengthen
- **SITL geofence boundary test**: fly the drone on a trajectory that approaches the SSSI boundary from 3 directions at 3 speeds. Log minimum distance to boundary achieved before repulsion/stop. Report as a table: approach speed vs closest approach distance. This validates the stopping distance claim.
- **GPS position spike injection test**: in SITL, inject a sudden 50m GPS jump and verify the system does not falsely trigger NFZ incursion or fly to a wrong waypoint. Report: does the system filter spikes? What is the threshold?
- **Wind tolerance test (SITL)**: simulate 10 m/s sustained wind at the NFZ boundary. Does the speed ramp + repulsion keep the drone clear? Report margin.
- **Operator response time measurement**: during simulated Verify states, measure the time from prompt to operator Y/N/I response across 10 trials. Report: mean, max, and whether the 120s timeout is well-calibrated.
- **RTL reliability test**: trigger RTL from 5 different states (SEARCH, CENTERING, VERIFY, APPROACH, MANUAL). Confirm the drone returns home in all cases. Report: success rate, landing accuracy relative to home point.

---

## 3. Mission Flow (`mission_flow.tex`)

**Score: 82/100**

### Strengths
- Comprehensive end-to-end narrative from power-on to RTL.
- Explicit requirement traceability (R01-R12 references throughout).
- Detection queuing strategy (continue pattern, don't stop on first detection) shows mature engineering thinking.
- PLB redirect is a nice operational feature that demonstrates flexibility.
- Three independent touchdown detection mechanisms show thorough failure-mode thinking.
- Payload delivery sequence with timed servo stages is specific and testable.

### Weaknesses
1. **Unvalidated claims.** The payload delivery sequence (PWM 1300 -> 1100 -> 1500) reads as a design, not a tested procedure. Was this actually tested on hardware? With an actual payload? The servo timing and PWM values need verification on real hardware.
2. **Speed schedule is mentioned but not justified.** "6 m/s at 20m, linearly interpolating to 10 m/s at 50m" -- why these values? Is it based on detection performance (GSD vs inference rate), wind tolerance, or battery optimisation? The rationale is missing.
3. **"Confidence below 0.2 are discarded" contradicts config.** The CLAUDE.md says the threshold is 0.4 in vision.py; here it says 0.2. Which is current? This inconsistency undermines trust.
4. **Transit waypoints via waypoints.json are mentioned without explaining what they are.** Are these operator-defined avoid-zones? A direct path to the search area? Scenic route around the SSSI? The reader needs context.
5. **No mention of what happens if the search pattern completes with zero detections.** Does the drone RTL? Rescan? Hover? This is a common operational scenario that should be addressed.
6. **Offset landing rationale is repeated from gps_estimation_deep.tex.** The "three reasons" paragraph appears in both sections. This is either deliberate cross-referencing or accidental duplication. If deliberate, a forward reference would be cleaner.
7. **Missing: battery management during mission.** What is the expected mission duration? What is the battery capacity? Is there a point-of-no-return calculation? The RTL section mentions returning home but not whether there is a battery-aware decision to abort the search early.

### Plausible Experimental Results That Would Strengthen
- **SITL full-mission timing**: run the complete mission in SITL (takeoff -> search -> detect -> verify -> land -> RTL) and report total elapsed time, distance flown, battery consumed (simulated). Compare against available battery capacity to confirm mission feasibility.
- **Detection queuing effectiveness**: run the search pattern over 2 targets with 3 false-positive-prone features. Report: how many items entered the queue? Were they correctly ordered by priority? Did the 5m reject radius prevent re-investigation?
- **PLB redirect test**: mid-mission, inject a PLB coordinate. Report: time from keypress to pattern regeneration, new pattern covers the focus area, old rejected targets preserved.
- **Payload servo test (bench)**: mount the Tarot servo on the airframe, attach a payload of the target weight, run the PWM sequence. Confirm: stage 1 loosens, stage 2 releases, retract works. Report: release reliability over 10 trials.
- **Zero-detection scenario**: complete the full search pattern with no dummy present. Confirm: drone RTLs cleanly, no stuck states, correct log output.

---

## 4. Progressive Testing Methodology (`testing_deep.tex`)

**Score: 85/100**

### Strengths
- The five-tier framework is genuinely well-designed and clearly presented.
- Defect discovery table (Table 6) is the strongest evidence in the entire report -- concrete bugs with tiers, fix times, and counterfactual costs.
- V-model mapping gives academic legitimacy to what could otherwise look like ad-hoc testing.
- Cost-risk gradient table makes the economic argument convincingly.
- "Never skip a tier" philosophy is stated with conviction and backed by evidence.
- 80% of defects caught at Tiers 1-2 is a compelling statistic.

### Weaknesses
1. **58 test scripts claimed but only ~41 exist in the codebase.** The CLAUDE.md file map counts approximately 41 scripts across all test directories. The table claims 58 including 6 unit tests and 4 automated tests in directories (`tests/unit/`, `tests/automated/`) not mentioned anywhere in the project file structure. Are these real? If they were created after the CLAUDE.md was last updated, fine -- but the discrepancy needs reconciliation.
2. **No Tier 4 or Tier 5 results.** The section describes what Tiers 4 and 5 would test but provides no results because they were never executed. This is honest but should be explicitly stated: "Tiers 4 and 5 remain unexecuted due to weather cancellation and schedule constraints."
3. **"12 of 15 defects caught at Tiers 1-3" but only 12 are listed in the table.** Where are the other 3? If the table is exhaustive, the claim should say "12 defects" not "15." If there are 3 more, list them.
4. **GPS timing lag listed as Tier 3 with asterisk "via DJI video."** This is an honest acknowledgment but it blurs the tier boundary. DJI video analysis is not a Tier 3 passive flight -- it is an offline analysis of pre-existing data. Consider calling it "Tier 1.5" or "offline analysis proxy" to maintain tier discipline.
5. **No test coverage metrics.** How many of the state machine transitions are exercised by the 22 SITL tests? What percentage of code paths are covered? Without coverage data, the "exhaustive" claim is aspirational.
6. **Experiment scripts (Section 4.5) describe what they will collect but report no data.** This is understandable (weather cancelled the flight) but the section reads like a test plan, not a test report. Frame it explicitly as "prepared for execution" rather than "conducted."

### Plausible Experimental Results That Would Strengthen
- **Tier 3 passive flight data**: altitude sweep results (detection rate vs altitude), speed sweep results (detection rate vs ground speed), GPS accuracy scatter plot vs ground truth. Even partial data from a single 10-minute flight would transform this from methodology to evidence.
- **State machine transition coverage**: enumerate all 32 transitions from the state diagram. Mark each as tested/untested. Report: X/32 tested in SITL, Y/32 tested on bench, Z/32 tested in flight.
- **Regression test results**: run all 22 SITL tests before and after a code change. Report: all pass (green), or which failed and why. This demonstrates the test suite actually catches regressions.
- **Defect injection experiment**: deliberately reintroduce 3 previously-fixed bugs (e.g., geofence sign convention, BGR inversion, infinite landing loop). Run the test suite. Report: which tier catches each re-injected bug, confirming the test suite's sensitivity.
- **Timing data for Tier 1 iteration**: measure the wall-clock time for a full SITL test run (all 22 scenarios). If it is truly "minutes," report the exact number. This substantiates the "50:1 iteration throughput" claim.

---

## 5. Field Day Narrative (`field_day_narrative.tex`)

**Score: 80/100**

### Strengths
- Honest, well-structured narrative that turns a weather cancellation into a positive story.
- Three-terminal workflow is practical and well-described -- a reader could replicate it.
- FOV calibration discovery (22% error) is a genuine highlight, well-presented with equation and consequence analysis.
- Camera colour discovery is a good "only-on-real-hardware" story.
- The "pivot" framing is effective: six concrete outputs from zero flight time.
- DJI video analysis as a Tier 3 proxy is clever and well-justified.
- "Lessons for the Next Field Day" is actionable and specific.

### Weaknesses
1. **No photos.** A field day narrative with zero photographs is a missed opportunity. Photos of: the three-terminal setup, the checkerboard calibration, the tape-measure FOV test, the team at the site, the weather conditions -- any of these would add credibility and visual interest.
2. **Camera resolution inconsistency.** Section 5.2 item 1 says "640x480 frames" but the camera is configured for 1456x1088 (per config.py and every other section). Which resolution was actually used on field day? If the camera was initially at 640x480 and later changed, say so.
3. **"Six quantitative outputs" is generous.** The FOV correction and lens calibration are quantitative. The colour-channel fix is binary (correct/incorrect). The connectivity verification and field reference sheet are procedural. The benchmark confirms pre-existing Docker estimates. Calling all six "quantitative" inflates the claim. "Six concrete outputs, three of which provided new quantitative data" would be more precise.
4. **DJI video section repeats content from gps_estimation_deep.tex.** The CEP50=2.3m figure, the 16.5m outlier, the GPS timing lag, the SRT sync trap -- all appear in both files. This will create duplication in the final report unless one section explicitly defers to the other.
5. **No timeline.** What time did the team arrive? When was connectivity established? When was the go/no-go decision made? A rough timeline would add structure and demonstrate time management.
6. **Lens calibration details are sparse.** How many checkerboard images were captured? At what distances? What were the distortion coefficients (k1, k2, p1, p2, k3)? The RMS is reported but the coefficients are not. For a "deep dive" appendix, this is too shallow.
7. **"Intermittent rain made outdoor electronics operation inadvisable" -- but the Pi and Cube were already outdoors for bench testing.** Were they under shelter? What changed between bench testing and the flight decision? The narrative implies the weather was fine for bench testing but not for flight, which is plausible but unstated.

### Plausible Experimental Results That Would Strengthen
- **FOV cross-validation at multiple distances**: repeat the tape-measure test at 0.5m, 1.0m, 1.5m, 2.0m. Report visible width at each distance. Fit a line through (distance, visible_width) and extract focal length with uncertainty. A single measurement at 1.0m has no error bar.
- **Checkerboard calibration details**: report the full camera matrix and distortion coefficients. Show a before/after undistortion comparison image. Report the number of images used (N>15 is good practice).
- **Colour channel verification**: show the test image in all 6 permutations (or at least RGB vs BGR) alongside the known-colour reference. This is a one-figure addition that makes the claim visually undeniable.
- **GPS satellite tracking over the session**: plot satellite count vs time during the field day. This shows whether GPS was stable enough for flight (if weather had permitted) and characterises the site.
- **Setup time measurement**: report actual elapsed time from arrival to "all systems green" on the diagnostics dashboard. This baseline is valuable for planning future field days.

---

## Cross-Cutting Issues

### Consistency Problems
1. **Confidence threshold**: 0.4 (CLAUDE.md, config.py) vs 0.2 (mission_flow.tex). Resolve.
2. **Camera resolution**: 640x480 (field day narrative item 1) vs 1456x1088 (everywhere else). Resolve.
3. **Search speed**: 8 m/s (gps_estimation, field day benchmark), 5 m/s (PLB redirect), altitude-dependent schedule (mission flow). These are all different contexts but the reader encounters 3 different speed numbers without a unifying table.
4. **CEP50=2.3m** appears in 3 files. If the number changes, all 3 must be updated. Use a LaTeX macro (\newcommand{\CEPfifty}{2.3}) to ensure consistency.
5. **Content duplication**: GPS timing lag, DJI replay results, offset landing rationale all appear in multiple files. Decide which section owns each topic and cross-reference from others.

### Missing Content
1. **No battery/endurance analysis anywhere.** How long can the drone fly? How does mission duration compare to battery capacity? This is a fundamental operational constraint that is never quantified.
2. **No wind tolerance data.** The go/no-go checklist has wind thresholds, but the thresholds are never stated in the report. What is the maximum wind speed for safe autonomous flight?
3. **No discussion of what happens after landing.** The mission ends at DONE. But in a real SAR scenario: is the payload accessible? Does someone walk to the landing site? How is the drone recovered?
4. **No comparison with other SAR drone systems.** How does 2.3m CEP50 compare to commercial systems? How does 4.8 FPS compare to industry practice? Without benchmarks, the reader cannot judge whether the results are good or bad.

### Overall Assessment

| Section | Score | Verdict |
|---------|-------|---------|
| GPS Estimation | 78 | Strong math, weak validation. Needs real ground-truth experiment. |
| Safety & Risk | 72 | Comprehensive design, untested claims. Needs geofence flight test. |
| Mission Flow | 82 | Best narrative flow. Minor inconsistencies. Needs timing data. |
| Testing | 85 | Strongest section. Framework is genuinely good. Needs Tier 3+ results. |
| Field Day | 80 | Honest and well-structured. Needs photos and detail. |

**Aggregate: 79/100**

The strongest aspect across all five sections is the engineering methodology: the progressive testing tiers, the error budget decomposition, the four-method comparison. The weakest aspect is the gap between designed experiments and executed experiments. The report describes an impressive test infrastructure but has limited empirical results from real flight conditions. The DJI video replay is the only real-world data source, and it is a proxy, not a controlled experiment.

**The single most impactful addition** would be results from a single Tier 3 passive flight (even 10 minutes): altitude sweep detection rates, GPS estimation scatter vs surveyed ground truth, and inference latency under real motion. This would lift the GPS estimation section from 78 to 88, the testing section from 85 to 92, and the field day narrative from 80 to 88.
