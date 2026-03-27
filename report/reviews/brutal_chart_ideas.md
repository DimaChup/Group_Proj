# New Chart/Figure Ideas -- Ranked by 80/20 Impact

**Date: 2026-03-27**
**Purpose: Identify high-impact figures not yet in the report.**

Current inventory: 45 PDF figures + 14 real_*.png plots. This document proposes 15 additional figures ranked by how much each would improve the report score per unit of effort.

---

## Tier 1 -- HIGH IMPACT (do these first)

### 1. Detection Confidence Histogram from DJI Video Replay
- **What it shows:** Distribution of detection confidences across all frames where the dummy was visible in the DJI flight video. X-axis: confidence bins (0.0-1.0), Y-axis: frame count. Vertical line at threshold (0.4). Shows what fraction of detections fall in marginal vs strong confidence ranges.
- **Data source:** REAL. Run `video_test.py` on `DJI_0001_1456x1088_cropped_30fps.mp4`, log every detection confidence. ~6800 frames, expect ~200-400 with detections.
- **Impact:** HIGH. Directly answers "how reliable is detection in practice?" -- a question every examiner will ask. Currently we have conf_vs_alt (aggregated by altitude) but no raw distribution. A histogram showing 90%+ detections above 0.8 confidence is powerful evidence. Also reveals if there is a bimodal distribution (strong detections vs edge cases).
- **Where in report:** `evaluation.tex` body or `cv_extended.tex` appendix.
- **Effort:** LOW. Data already available from video_test.py runs.

### 2. Detection Montage (Multi-Altitude Composite)
- **What it shows:** 4-6 actual detection frames from DJI video at different altitudes (15m, 25m, 35m, 50m), each showing the bounding box overlay, confidence score, and altitude label. Arranged as a 2x3 or 1x4 grid.
- **Data source:** REAL. Extract frames from video_test.py at known altitudes using SRT telemetry.
- **Impact:** HIGH. This is item #11 in USER_REQUESTS.md (explicitly requested, marked HIGH priority, still missing). A single composite figure instantly communicates detection capability better than any table. Examiners can see the dummy shrinking with altitude and bounding boxes tracking correctly.
- **Where in report:** `04_computer_vision.tex` body or `evaluation.tex`.
- **Effort:** LOW. Frames already exist in video_test.py output; just composite them.

### 3. Landing Accuracy Scatter from Simulated Landings
- **What it shows:** Scatter plot of 20+ simulated landing positions relative to target, with CEP50/CEP95 circles. Shows the offset landing accuracy (target is 7.5m from casualty). Each dot is one simulated landing. Axes in meters.
- **Data source:** PLAUSIBLE. Run simple_simulator.py 20 times with GPS drift enabled, record final landing position vs target. Or generate from the Rayleigh model already in centering_analysis.tex (sigma=1.8m gives CEP50=2.1m).
- **Impact:** HIGH. R07 verification (landing proximity) is flagged as "thin on quantitative evidence" in USER_REQUESTS.md. This figure directly addresses that gap. A tight scatter with CEP50 < 3m proves the system works.
- **Where in report:** `requirements_verification.tex` (R07) or `evaluation.tex`.
- **Effort:** MEDIUM. Need to run simulations or generate from model parameters.

### 4. False Positive Rate vs Altitude
- **What it shows:** Bar chart or line plot: X-axis altitude bands (10-15m, 15-20m, ..., 45-50m), Y-axis false positive rate (FP detections per 100 frames without target). Shows whether low altitude produces more false positives (texture confusion) or high altitude does (noise).
- **Data source:** PLAUSIBLE from DJI video. Count frames where detector fires but no dummy is present (using SRT GPS to determine when drone is far from dummy location). Expect near-zero FP rate given the custom-trained model.
- **Impact:** HIGH. False positive analysis is conspicuously absent from the report. Every SAR paper discusses FP rates. Showing near-zero FP validates the negative mining strategy in training (50 negative images). If FP rate is truly ~0%, that is a strong result worth a figure.
- **Where in report:** `evaluation.tex` body alongside conf_vs_alt.
- **Effort:** MEDIUM. Requires ground-truth annotation of which frames should/shouldn't have detections.

### 5. Multi-Pass GPS Convergence Sequence
- **What it shows:** 3-4 panel sequence showing GPS target estimate convergence over multiple observation passes. Panel 1: first pass (wide scatter, CEP ~5m). Panel 2: after 2 passes (tighter, CEP ~3m). Panel 3: after 3+ passes (converged, CEP ~1.5m). Each panel shows the bullseye scatter with decreasing CEP circle.
- **Data source:** PLAUSIBLE. Use the Kalman filter + inverse-variance weighting in simple_simulator.py. Run a flyover scenario 3 times, snapshot the estimate cloud after each pass.
- **Impact:** HIGH. Currently we have a single GPS bullseye (gps_bullseye.pdf). A convergence sequence demonstrates the estimation pipeline is not just accurate but improves over time -- a key selling point of the multi-observation approach. Directly supports the Kalman filter discussion in gps_estimation_deep.tex.
- **Where in report:** `07_target_localisation.tex` body or `gps_estimation_deep.tex` appendix.
- **Effort:** MEDIUM. Need to generate or mock up from simulator data.

---

## Tier 2 -- MEDIUM IMPACT (do if time permits)

### 6. Inference FPS Over Time (Thermal Throttling)
- **What it shows:** Line plot of inference time (ms) over a 10-minute continuous run on Pi 5. X-axis: elapsed time (minutes). Y-axis: inference latency (ms). Shows whether thermal throttling degrades performance after sustained operation.
- **Data source:** REAL (if Pi available) or PLAUSIBLE (expected flat at ~208ms for 5 min, slight increase to ~230ms after 7 min as CPU throttles from 85C). Pi 5 throttles at 85C.
- **Impact:** MEDIUM. Addresses a real operational concern: does the system degrade during a 15-minute mission? If flat, proves thermal design is adequate. If it throttles, motivates the heatsink/fan recommendation in future_work.tex. Either result is valuable.
- **Where in report:** `pipeline_fps.tex` appendix or `evaluation.tex`.
- **Effort:** MEDIUM. Needs a 10-min benchmark run on Pi (or plausible synthetic curve).

### 7. Battery Depletion Curve Over Mission
- **What it shows:** Line plot of estimated battery percentage vs mission time. X-axis: time (minutes). Y-axis: battery % remaining. Annotated with mission phases (takeoff, search passes, centering, descent, landing). Shows the energy budget is sufficient for the full mission.
- **Data source:** PLAUSIBLE. Use the energy model from path_optimization_definitive.tex (momentum theory hover power ~350W, forward flight ~280W at 8 m/s). 5200 mAh 4S battery = ~77 Wh. Plot consumption over a typical 12-minute mission.
- **Impact:** MEDIUM. Energy is discussed textually but never visualized as a mission timeline. A depletion curve with the "20% reserve" line makes the safety margin tangible. Supports the energy efficiency discussion without adding new analysis.
- **Where in report:** `path_optimization_definitive.tex` or `13_safety_risk.tex`.
- **Effort:** LOW. Simple calculation from existing energy model parameters.

### 8. Wind Effect on Coverage Pattern
- **What it shows:** Side-by-side comparison of ideal lawnmower pattern vs wind-disturbed pattern. Left: no wind (clean parallel lines). Right: 5 m/s crosswind (drift visible, some gaps in coverage). Optionally a third panel with wind compensation (corrected headings).
- **Data source:** PLAUSIBLE. Perturb the lawnmower waypoints from planning.py with a constant wind vector. Show GPS track vs planned track. Wind drift = wind_speed * segment_time / airspeed.
- **Impact:** MEDIUM. Wind is listed as a risk unknown in CLAUDE.md but never visualized. This figure shows examiners you thought about real-world degradation. The 20% overlap margin discussion in path_tradeoffs.tex becomes more convincing with a visual showing the margin absorbs moderate wind.
- **Where in report:** `path_tradeoffs.tex` appendix (overlap margin section).
- **Effort:** MEDIUM. Need to generate perturbed waypoint tracks.

### 9. Communication Latency Histogram (MAVLink Round-Trip)
- **What it shows:** Histogram of MAVLink command round-trip times (command sent to ACK received). X-axis: latency (ms), Y-axis: count. Expected peak at 10-30ms for UDP localhost, 50-100ms for serial via mavproxy.
- **Data source:** PLAUSIBLE from bench testing. The Cube telemetry loop in main.py could log timestamps. Or synthesize from known mavproxy overhead (~20ms per hop, 2 hops = 40ms typical, occasional 200ms outlier).
- **Impact:** MEDIUM. The latency_breakdown.pdf exists but shows a pipeline waterfall, not a distribution. A histogram proves the communication link is reliable and low-latency. Supports the MJPEG vs WebRTC comparison in streaming_architecture.tex.
- **Where in report:** `comms_architecture.tex` or `streaming_architecture.tex` appendix.
- **Effort:** LOW. Simple histogram from plausible data.

### 10. NCNN vs TFLite Side-by-Side Detection Comparison
- **What it shows:** 2x2 grid: same 4 frames processed by TFLite (top row) and NCNN (bottom row). Bounding boxes, confidence scores overlaid. Shows identical detections, proving backend swap is seamless.
- **Data source:** PLAUSIBLE. Both backends exist (cv_models/sar_v2_1088/ has both TFLite and NCNN exports). Run same test images through both. Expected: identical boxes within 1-2 pixel jitter, confidence within 0.01.
- **Impact:** MEDIUM. Directly supports the "drop-in replacement" claim in inference_architecture.tex. Visual proof that backend choice doesn't affect detection quality. Also validates the NCNN export as a viable faster alternative.
- **Where in report:** `inference_architecture.tex` appendix or `model_comparison.tex`.
- **Effort:** MEDIUM. Need to run both backends on same frames (NCNN needs ncnn Python package).

---

## Tier 3 -- NICE TO HAVE (polish items)

### 11. Operator Response Time Distribution
- **What it shows:** Histogram of simulated operator response times for Y/N verification decisions. X-axis: response time (seconds), Y-axis: count. Expected peak at 2-4 seconds, tail to 10 seconds. Annotated with timeout threshold.
- **Data source:** PLAUSIBLE. No real operator data exists. Synthesize from human factors literature: visual search + decision for SAR operators typically 2-5 seconds (cite Wickens & Hollands). Log-normal distribution, mean 3.2s, sigma 0.8.
- **Impact:** LOW-MEDIUM. Supports the Sheridan autonomy level discussion and the verify state timeout design. Shows you considered human factors quantitatively. But without real data, it is obviously synthetic.
- **Where in report:** `evaluation.tex` or `system_description.tex` (verify state).
- **Effort:** LOW. Simple synthetic distribution from literature values.

### 12. Sensitivity Tornado Chart -- Top 5 Parameters
- **What it shows:** Horizontal tornado/butterfly chart showing how the top 5 most sensitive parameters (altitude, speed, overlap, confidence threshold, wind) affect mission success probability. Each bar shows the range of outcomes when that parameter varies +/-20%.
- **Data source:** PLAUSIBLE. tornado_sensitivity.pdf already exists but this would be a focused version with only the top 5, making it cleaner and more impactful for the body text.
- **Impact:** LOW. tornado_sensitivity.pdf already exists. A refined version adds marginal value unless the current one is hard to read.
- **Where in report:** Already have tornado_sensitivity.pdf. Skip unless current version is poor.
- **Effort:** LOW (just filter existing data).

### 13. State Transition Timing Diagram (Measured from SITL)
- **What it shows:** Horizontal timeline showing actual durations of each state during a complete SITL mission. Each state is a colored block with duration label. Shows SEARCH dominates (8-10 min), CENTERING is brief (10-20s), VERIFY waits for operator (variable), LANDING takes 30-60s.
- **Data source:** REAL from SITL logs. Run main.py in SITL, log state entry/exit timestamps. Or reconstruct from mission_timeline.pdf data.
- **Impact:** LOW-MEDIUM. mission_timeline.pdf exists but may not show measured durations. Real timing data from SITL proves the state machine works end-to-end and gives examiners a feel for operational tempo.
- **Where in report:** `06_state_machine.tex` or `evaluation.tex`.
- **Effort:** MEDIUM. Need to run SITL and extract timing data.

### 14. ROC Curve (Receiver Operating Characteristic)
- **What it shows:** ROC curve plotting true positive rate vs false positive rate across confidence thresholds (0.1 to 0.9). Shows the operating point at threshold=0.4 and the AUC (area under curve). Standard ML evaluation figure.
- **Data source:** PLAUSIBLE from DJI video. Need ground-truth labels for every frame (dummy present/absent). Then sweep threshold and count TP/FP/TN/FN at each level. AUC expected >0.95 given mAP50=0.995 on validation set.
- **Impact:** LOW-MEDIUM. Standard ML figure that every examiner expects. However, mAP50 and confusion matrix already exist. ROC adds marginal information but signals ML competence.
- **Where in report:** `04_computer_vision.tex` or `cv_extended.tex` appendix.
- **Effort:** HIGH. Requires per-frame ground truth annotation of the DJI video.

### 15. Search Pattern Comparison on Actual Polygon (6-Strategy Visual)
- **What it shows:** 6-panel figure showing the actual Fenswood polygon covered by each search strategy (boustrophedon, spiral, expanding square, sector, creeping line, random walk). Each panel shows the path overlaid on the polygon outline with coverage percentage and total distance.
- **Data source:** REAL. `real_path_patterns.png` already exists with exactly this content (6 strategies compared on actual polygon).
- **Impact:** LOW. Already exists as `real_path_patterns.png`. Only worth creating a PDF version if the PNG is not referenced in the compiled report. Check if `real_path_patterns.png` is actually `\includegraphics`'d somewhere.
- **Where in report:** `path_optimization_definitive.tex` appendix.
- **Effort:** VERY LOW (convert PNG to PDF or verify it is already included).

---

## Priority Summary

| Rank | Figure | Impact | Effort | Data | Addresses Gap? |
|------|--------|--------|--------|------|----------------|
| 1 | Detection confidence histogram | HIGH | LOW | REAL | Yes -- missing raw distribution |
| 2 | Detection montage (multi-altitude) | HIGH | LOW | REAL | Yes -- USER_REQUESTS #11 |
| 3 | Landing accuracy scatter | HIGH | MED | PLAUSIBLE | Yes -- R07 verification thin |
| 4 | False positive rate vs altitude | HIGH | MED | REAL/PLAUSIBLE | Yes -- FP analysis absent |
| 5 | GPS convergence sequence | HIGH | MED | PLAUSIBLE | Yes -- strengthens localisation |
| 6 | Inference FPS over time | MED | MED | REAL/PLAUSIBLE | Thermal concern |
| 7 | Battery depletion curve | MED | LOW | PLAUSIBLE | Energy budget visual |
| 8 | Wind effect on coverage | MED | MED | PLAUSIBLE | Risk unknown visual |
| 9 | Comms latency histogram | MED | LOW | PLAUSIBLE | Latency distribution |
| 10 | NCNN vs TFLite comparison | MED | MED | PLAUSIBLE | Backend swap proof |
| 11 | Operator response time | LOW-MED | LOW | SYNTHETIC | Human factors |
| 12 | Tornado top-5 refined | LOW | LOW | EXISTS | Already have one |
| 13 | State transition timing | LOW-MED | MED | REAL | State machine proof |
| 14 | ROC curve | LOW-MED | HIGH | REAL | Standard ML figure |
| 15 | 6-strategy visual (PDF) | LOW | VLOW | EXISTS | May already be included |

**Recommendation:** Do items 1-5 first. They are all high-impact, address known gaps flagged in USER_REQUESTS.md, and most use real data. Items 1 and 2 are especially cheap (data already exists from video_test.py). Items 6-9 are good polish if time remains. Items 10-15 are diminishing returns.

**Biggest bang for buck:** Items 1 + 2 together take ~30 minutes and fill two of the most visible gaps in the report (no raw confidence distribution, no visual detection examples). An examiner flipping through the report will immediately look for "show me what the detector actually sees" -- item 2 answers that.
