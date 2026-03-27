# Figures Review -- report/figs/

Reviewed: 20 figures (15 PNG + 5 PDF-only).
Date: 2026-03-27

---

## Summary

| Rating | Count | Figures |
|--------|-------|---------|
| PASS | 11 | architecture, cv_pipeline, state_machine, state_machine_simple, mission_timeline, mission_overview, gps_bullseye, gps_convergence, estimator_comparison, detection_heatmap, geofence_diagram |
| MINOR FIX | 5 | pi_system, conf_vs_alt, blur_vs_altitude, detection_envelope, coverage_vs_time |
| NEEDS REGEN | 4 | state_machine_full, det_vs_speed, latency_breakdown, gps_error_direction |

**Critical errors found: 3** (data accuracy issues in latency_breakdown, det_vs_speed, conf_vs_alt threshold)

---

## Per-Figure Review

### 1. architecture.png -- PASS

- **Data/math**: Correct. Shows Ground Segment (RC, Ground Station) and Airborne Platform (Cube, Pi, camera, GPS, motors, buzzer).
- **Labels**: All readable. Communication protocols labelled (433 MHz, UART/MAVProxy, CSI-2, WiFi/MJPEG, PWM).
- **Colors**: Consistent 3-color scheme (blue=hardware, green=software, white=ground). Legend present.
- **Overlapping text**: None.
- **Professional**: Yes. Clean block diagram, appropriate for MSc report.
- **Caption match**: Caption says "Module dependency graph" with arrows indicating data dependencies. The figure shows a hardware block diagram, not a software module dependency graph. However, the caption in `system_description.tex` line 51 is generic enough ("Independent modules have no cross-dependencies; the orchestrator composes them at runtime") that it still works, since the figure shows both software modules and hardware connections.

### 2. pi_system.png -- MINOR FIX

- **Data/math**: Correct. Shows detailed Pi 5 internals with all software modules and external connections.
- **Labels**: Mostly readable but **small text is hard to read** -- the connection labels (e.g., "CSI-2 ribbon cable", "1456x1088 native", "found, x, y, conf") are quite small and may not survive LaTeX scaling.
- **Colors**: Consistent with architecture.png (blue=software, green=hardware, orange=communication links). Legend present.
- **Overlapping text**: Minor overlap between some arrow labels near the center where main.py connects to multiple modules. The "GPS estimate" and "Annotated frames" labels are close together.
- **Professional**: Good overall but slightly busy. The connection lines cross in places.
- **Caption match**: Caption says "Raspberry Pi 5 companion computer system: hardware interfaces and data flow between the CSI camera, TFLite inference engine, MAVProxy bridge, and ground station." -- accurate match.
- **Fix needed**: Increase font size on connection labels or simplify some paths. Consider width=0.85\textwidth instead of 0.75 for more space.

### 3. cv_pipeline.png -- PASS

- **Data/math**: Correct. Pipeline: Camera Frame (1456x1088) -> Lens Undistort (1.5ms) -> Resize 640x640 (0.3ms) -> YOLOv8n TFLite (196ms) -> NMS Filter (conf > 0.2) -> Detection (x,y,conf). Total ~198ms (5.1 FPS).
- **Note**: The total says "~198ms (5.1 FPS)" but benchmarks show 206.5ms (4.8 FPS). The 198ms excludes capture time which is fair for "pipeline only" but the caption in system_description.tex says "208 ms" -- slight inconsistency. The figure shows the processing pipeline stages only (no capture), so 198ms is defensible.
- **Labels**: Clear and readable. Each stage has timing underneath.
- **Colors**: Blue gradient boxes on white, orange accent for total time. Professional.
- **Overlapping text**: None.
- **Professional**: Excellent. Clean, clear, publication quality.
- **Caption match**: Caption says "208 ms on the Pi 5" but figure says "~198 ms". Minor discrepancy -- the 208ms includes capture overhead. Either update caption to say "~198 ms processing" or add capture stage to figure.

### 4. state_machine.png -- PASS

- **Data/math**: Correct simplified view. INIT -> TAKEOFF -> SEARCH -> CENTERING -> VERIFY -> APPROACH -> LANDING -> DONE. Manual override (dashed red) from SEARCH. RTL from VERIFY on link loss / RC kill. Rejected [N] loops back from VERIFY to SEARCH.
- **Labels**: All readable. Clear state names, transition labels.
- **Colors**: 4-color legend (green=start/end, blue=autonomous, orange=operator decision, red=safety override). Consistent and meaningful.
- **Overlapping text**: None.
- **Professional**: Excellent. Clean flowchart, appropriate abstraction level.
- **Caption match**: Caption says "Primary mission path flows left to right; engagement branches downward from SEARCH. Manual override (dashed) is accessible from any active state." The figure shows top-to-bottom flow (not left-to-right), but "flows" is generic enough. Manual override shown only from SEARCH, not "any active state" -- caption is slightly misleading. Consider updating caption to say "from SEARCH" or adding dashed arrows from other states.

### 5. state_machine_full.png -- NEEDS REGEN

- **Data/math**: Shows all states including CONNECTING, ARMING, PRE_WAYPOINTS, TRANSIT_TO_SEARCH, HOVER, HOVER_TARGET, DESCENDING, RETURN_TO_SEARCH, RETURN_FROM_MANUAL, RETURN_TRANSIT, RETURN_HOME. Comprehensive.
- **Labels**: **Too small to read at printed scale.** Many state names and transition labels are tiny. The grouped regions (Startup, Transit, Search, Engagement, Recovery, Safety) use pale background colors that don't provide enough contrast.
- **Colors**: 6-color scheme (grey=startup, green=transit, yellow-green=search, orange/yellow=engagement, yellow=recovery, pink=safety). Too many similar warm colors -- engagement and recovery are hard to distinguish.
- **Overlapping text**: **Yes.** Several transition labels overlap or are cut off, especially around the CENTERING/DESCENDING/VERIFY cluster and the RETURN_FROM_MANUAL area. The "M key" label near MANUAL overlaps with "Resume / Take Maker".
- **Professional**: **No.** Too dense and cluttered for print. Would be acceptable as a supplementary digital figure but not in the main report body.
- **Caption match**: Not directly referenced in main text -- only state_machine.png is used.
- **Fix needed**: Either (a) move to appendix and increase figure size to full page, or (b) split into two figures (mission flow + recovery/safety paths), or (c) don't include it at all since state_machine.png covers the simplified version well.

### 6. state_machine_simple.png -- PASS

- Identical to state_machine.png (same image). This is a duplicate. Both are clean and professional. No issues.

### 7. mission_timeline.png -- PASS

- **Data/math**: Shows two panels. Top: Gantt-style timeline (Takeoff 30s, Transit 30s, Search 120s, Centering 15s, Verify 30s, Approach 20s, Landing). Total ~4 min. Bottom: Altitude profile (0 -> 35m search -> descent to 15m verify -> landing). Timings are reasonable for a 17,400 m^2 search area at 10 m/s.
- **Labels**: All readable. Time axis clear (0:00 to 4:00). Altitude axis clear (0-40m).
- **Colors**: Consistent color scheme matching state_machine.png state categories. Nice visual coherence.
- **Overlapping text**: None.
- **Professional**: Excellent. Two-panel layout is effective. Altitude profile adds value.
- **Caption match**: Caption says "Mission timeline showing state transitions during a simulated end-to-end SAR mission. The horizontal axis represents elapsed time; coloured blocks indicate active states." -- accurate.

### 8. mission_overview.png -- PASS

- **Data/math**: Shows Fenswood Farm site with flight area boundary (blue dashed), search area (green polygon), SSSI no-fly zone (red hatched), lawnmower search pattern, take-off location (star), target position (red square), GPS estimates (green dots), landing point with 7.5m offset (green diamond), RTL path (grey dashed). Scale bar (50m) present. North arrow present.
- **Labels**: All readable. Legend comprehensive.
- **Colors**: Good differentiation between zones. Red hatching for SSSI is distinctive.
- **Overlapping text**: Minor -- "Landing (7.5 m offset)" label overlaps slightly with GPS estimate cluster, but still readable.
- **Professional**: Excellent. Publication quality geographic figure.
- **Caption match**: Caption mentions "lawnmower search pattern covers the designated survey polygon at 35 m altitude, with the take-off point, return-to-launch path, and SSSI no-fly zone boundary shown" -- accurate.

### 9. conf_vs_alt.pdf -- MINOR FIX

- **Data/math**: Shows detection confidence vs altitude (5-55m). Confidence stays near 1.0 from 5-35m, drops to ~0.9 at 55m. Sweet spot highlighted as 15-40m. Threshold shown at 0.2.
- **Issue**: The confidence threshold is shown as 0.2 but the report and config.py use 0.4 as the confidence threshold. The cv_pipeline.png also shows "conf > 0.2". Need to verify which is correct and make consistent. CLAUDE.md says "Confidence threshold: 0.4 (in vision.py)".
- **Labels**: All readable. Clean axes, legend clear.
- **Colors**: Blue line + scatter, red dashed threshold, light blue operational envelope. Professional.
- **Overlapping text**: None.
- **Professional**: Yes. Clean matplotlib output.
- **Caption match**: cv_extended.tex says "dashed line marks the 0.2 confidence threshold" -- matches figure but may conflict with actual code (0.4). evaluation.tex says "Confidence remains above 0.9 up to 40 m" -- matches figure data.
- **Fix needed**: Clarify whether the operational threshold is 0.2 or 0.4 and make all figures + text consistent.

### 10. det_vs_speed.pdf -- NEEDS REGEN

- **Data/math**: **PROBLEM.** Shows detection rate vs ground speed. Both TFLite CPU (4.8 FPS) and FP16 projected (9.5 FPS) curves are flat at 100% across all speeds from 0-15 m/s. This is unrealistic and uninformative -- it shows no speed dependency at all, making the figure pointless.
- **Root cause**: The figure appears to model "detection rate per flyover" (probability of at least one detection during a pass) rather than per-frame detection rate. With multiple frames per pass, even at 15 m/s the cumulative probability is ~100%. But this makes the figure provide zero useful information.
- **Caption mismatch**: evaluation.tex caption says "Detection rate vs. flight speed. At the nominal search speed of 8 m/s, detection rate exceeds 95%." The figure shows 100% at all speeds, and the search speed annotation says 10 m/s (not 8 m/s). cv_extended.tex caption talks about "single-frame detection rates of 0.70, 0.85, and 0.95" with multiple curves -- the figure only shows two flat lines, not three curves.
- **Fix needed**: Regenerate with per-frame detection probability or show the multi-curve version from cv_extended.tex caption (p_d = 0.70, 0.85, 0.95). The figure should show meaningful variation, not flat 100% lines. Also reconcile 8 m/s vs 10 m/s search speed.

### 11. gps_bullseye.png -- PASS

- **Data/math**: Shows scatter plot of GPS estimates around true position. CEP50 = 2.2m, CEP95 = 4.8m (dashed circles). Centroid at (+0.1, -0.2) -- near-zero bias. Individual estimates scattered within ~15m radius. Concentric circles at 5m, 10m, 15m for reference.
- **Note**: CEP50 = 2.2m in figure vs 2.3m mentioned in CLAUDE.md and gps_convergence.pdf. Minor discrepancy (possibly different simulation runs).
- **Labels**: Mostly readable but small at the rendered size. The "CEP50 = 2.2 m" and "CEP95 = 4.8 m" legend items are adequate.
- **Colors**: Blue/green estimates, red star for true position, orange dashed for CEP circles. Good contrast.
- **Overlapping text**: Minor -- the centroid label text overlaps with data points near the center, but still legible.
- **Professional**: Yes. Standard target/bullseye plot.
- **Caption match**: Caption says "CEP50 = 2.3 m shown as dashed circle" but figure shows CEP50 = 2.2 m. Minor discrepancy -- update caption or regenerate with consistent value.

### 12. gps_convergence.pdf -- PASS

- **Data/math**: Shows CEP decreasing with number of observations. Curve follows sigma_0/sqrt(n) + epsilon_sys. At n=30, CEP ~3.2m (measured data point). Measured CEP dashed at 2.3m. The theoretical curve doesn't quite reach the measured CEP -- this is expected since the model is approximate.
- **Labels**: All readable. Mathematical formula in legend is clear.
- **Colors**: Blue curve + scatter, orange dashed measured CEP. Clean two-color scheme.
- **Overlapping text**: None.
- **Professional**: Excellent. Good theoretical + empirical comparison.
- **Caption match**: Caption says "Kalman filter stabilises within 5-10 detections" -- the figure shows general CEP convergence, not specifically the Kalman filter. The curve label says CEP ~ sigma_0/sqrt(n) + epsilon_sys. Caption is slightly misleading but acceptable since the convergence behavior applies generally.

### 13. estimator_comparison.png -- PASS

- **Data/math**: Bar chart comparing 4 methods: Rolling Average (4.5m), Cumulative Average (3.2m), Kalman Filter (2.8m), Inverse Variance Weighted (2.3m, selected). Error bars shown. Inverse Variance Weighted is highlighted in orange with "Selected" badge.
- **Labels**: All readable. Clear axis labels, value annotations on each bar.
- **Colors**: Grey bars for non-selected, orange for selected. Clean and professional.
- **Overlapping text**: None.
- **Professional**: Excellent. Clear comparison chart.
- **Caption match**: Caption says "Comparison of estimation methods: raw average, inverse-variance weighted, and Kalman filter." Lists 3 methods but figure shows 4 (also includes rolling average). Minor caption omission.

### 14. gps_error_direction.png -- NEEDS REGEN

- **Data/math**: Two panels. Left: polar scatter plot showing error distribution at heading 155 degrees, 10 m/s. Elongation along flight direction visible. Right: bar chart of along-track vs cross-track error at 3 speeds (5, 7.5, 10 m/s). Along-track error increases with speed (1.9, 2.0, 2.1m), cross-track stays ~1.0m.
- **Labels**: **Too small.** The entire figure is rendered at very low resolution/small size. The polar plot labels, bar chart numbers, and annotation text ("GPS timing lag: 150 ms, At 10 m/s: 1.5m forward bias") are barely readable.
- **Colors**: Orange (along-track) and blue (cross-track) are consistent and distinguishable.
- **Overlapping text**: The annotation box in the right panel overlaps with the bar chart area.
- **Professional**: **Marginal.** The figure needs to be larger. At the size shown, it's not print-ready.
- **Caption match**: Caption says "Directional error distribution showing heading-aligned elongation from GPS timing lag." -- accurate.
- **Fix needed**: Regenerate at larger size. The figure is informative but needs to be at least 2x larger for print. Consider splitting into two separate figures or increasing figsize.

### 15. detection_heatmap.png -- PASS

- **Data/math**: Shows detection density across the search area. Target position (red star) and estimated position (green star) visible. CEP50 circle shown. Search area polygon outlined. Take-off point marked. Color scale represents detection confidence (0-1).
- **Labels**: Readable but small. The "CEP50" and "within FOV" labels are a bit cramped.
- **Colors**: Viridis-like colormap for detection confidence. Good for print (colorblind-safe).
- **Overlapping text**: Minor -- "CEP50" text overlaps with the confidence heatmap slightly.
- **Professional**: Yes. Good spatial context figure.
- **Caption match**: Caption says "Spatial detection heatmap showing detection density across the survey area during simulated search." -- accurate.

### 16. blur_vs_altitude.png -- MINOR FIX

- **Data/math**: Two panels. Left: 1/100s exposure showing pixel displacement vs altitude at 5, 10, 15 m/s. Right: 1/500s exposure. Blur threshold at 3 px shown as dashed line. Operational envelope (yellow band) shown.
- **Issue**: The figure title says "Exposure 1/100 s" and "Exposure 1/500 s". But the caption in cv_extended.tex says "2 ms exposure" (= 1/500 s). The report text should clarify which exposure the system actually uses. The IMX296 global shutter camera likely uses short exposure.
- **Labels**: Readable. Clear axes, legends, threshold line.
- **Colors**: Three-color lines (green=5m/s, blue=10m/s, red=15m/s). Consistent across both panels.
- **Overlapping text**: The "Blur threshold (3 px)" annotation on the right panel is small but readable. The "Operational envelope" label on both panels is in very light text.
- **Professional**: Good. Two-panel comparison is effective.
- **Caption match**: Caption says "At the nominal search configuration (10 m/s, 2 ms exposure), blur remains below 1 px for all altitudes above 15 m." This matches the right panel (1/500s) data. The left panel (1/100s) shows higher blur, providing context. Caption is accurate.
- **Fix needed**: Make "Operational envelope" labels darker/bolder. The light yellow text is hard to read.

### 17. detection_envelope.png -- MINOR FIX

- **Data/math**: Shows confidence vs altitude with 4 curves: No blur (ideal), 10 m/s at 1/100s, 15 m/s at 1/100s, and 10 m/s global shutter (1/500s). Right y-axis shows target pixel size. Operational envelope (15-40m) highlighted. Confidence threshold at 0.4.
- **Issue**: This figure shows threshold at 0.4 but conf_vs_alt.pdf shows it at 0.2. Inconsistency.
- **Labels**: Mostly readable. The "Blur significant below 15 m only" annotation and "~10 px min" annotation are in small italic text. The dual y-axis labels are clear.
- **Colors**: Four distinct line styles (solid blue, dashed orange, dash-dot red, dotted green). Good differentiation.
- **Overlapping text**: Minor -- "Confidence threshold (0.4)" text is close to the curves. The "Blur significant below 15 m only" annotation overlaps slightly with the red curve.
- **Professional**: Good. Informative combined plot. Dual y-axis is well handled.
- **Caption match**: Caption says "shaded region indicates the reliable detection zone" -- matches. "Nominal search altitude of 35 m sits comfortably within this envelope" -- confirmed by the figure.
- **Fix needed**: Reconcile the confidence threshold between this figure (0.4) and conf_vs_alt (0.2). One of them must change to match the actual system configuration.

### 18. latency_breakdown.pdf -- NEEDS REGEN

- **Data/math**: Stacked bar chart. Left bar: "TFLite INT8 (current)" = 206.5ms (4.8 FPS) with 196ms inference. Right bar: "FP16 XNNPACK (projected)" = 106.5ms (9.4 FPS) with 96ms inference.
- **CRITICAL ERROR**: The left bar is labelled **"TFLite INT8"** but the actual model is **float32** (FP32). From CLAUDE.md: "best.tflite (3.2MB YOLOv8n): 206.5ms / 4.8 FPS" and the model is explicitly "float32". The INT8 label is wrong and misleading. An INT8 model would typically be faster, not 206ms.
- **Labels**: Clear and readable. Pipeline stage legend (Capture, Undistort, Resize, Inference, Postprocess) is professional. Timing annotations on bars are clear.
- **Colors**: Monochromatic blue gradient for pipeline stages. Professional but the stages below inference are so thin they're barely visible -- this is accurate (they are <10ms combined) but visually the chart is essentially a single-color bar.
- **Overlapping text**: None.
- **Professional**: Good layout, but the incorrect INT8 label undermines credibility.
- **Caption match**: Caption says "Model inference (XNNPACK, 4-thread) accounts for 94% of total latency" -- this is mathematically correct (196/206.5 = 95%). Slight rounding difference but acceptable.
- **Fix needed**: Change "TFLite INT8 (current)" to "TFLite FP32 (current)" or "TFLite float32 (current)". This is a factual error that must be corrected.

### 19. coverage_vs_time.pdf -- MINOR FIX

- **Data/math**: Linear coverage increase from 0% to 100%. 50% at 0.5 min, 75% at 0.8 min, 100% at 1.1 min. Area: 17,418 m^2, Lane: 32.2 m, Speed: 10 m/s.
- **Math check**: At 10 m/s with ~32m lane spacing and ~17,418 m^2 area, the total path length is approximately area/lane_spacing = 17418/32.2 = 541m. At 10 m/s, that's 54s (~0.9 min). The figure says 1.1 min (66s) which includes turn time -- reasonable.
- **Note**: Lane width of 32.2m seems wide for a search pattern at 35m altitude. The camera FOV at 35m with 54.4 deg HFOV gives ~36m ground footprint width, so 32.2m lane spacing provides ~10% overlap. This is reasonable for systematic coverage but tight.
- **Labels**: All readable. Milestone annotations (50%, 75%, 100%) are clear and well-placed.
- **Colors**: Blue line with grey/orange/green milestone dots. Clean.
- **Overlapping text**: None.
- **Professional**: Clean and effective.
- **Caption match**: Caption says "near-linear increase confirms systematic, gap-free coverage of the survey polygon" -- matches the nearly straight line in the figure.
- **Minor issue**: The line continues flat at 100% past 1.1 min to ~1.2 min. This flat tail is fine but the x-axis could stop at 1.2 min instead of extending further.

### 20. geofence_diagram.png -- PASS

- **Data/math**: Four-panel layout. (a) Without Geofence: shows 7 path segments crossing SSSI boundary. (b) With Three-Layer Protection: shows deflected trajectory avoiding SSSI. (c) Speed Reduction Profile: linear speed ramp from 10 m/s to 0 between 20m and 3m from NFZ. (d) Protection Layer Summary table: 4 layers (Speed Ramp, Repulsive Force, Auto-MANUAL, Waypoint Filter) with distances and mechanisms.
- **Labels**: All readable. Panel labels (a-d) clear. Table in panel (d) is well formatted.
- **Colors**: Consistent with mission_overview.png (green=flight area, red=SSSI, blue=drone path). The repulsive force arrows and speed ramp are visually clear.
- **Overlapping text**: Minor -- some path labels in panel (a) are dense but still readable.
- **Professional**: Excellent. The four-panel layout effectively communicates the geofence system.
- **Caption match**: Caption in system_description.tex mentions "Four-panel geofence protection visualisation" with (a) boundaries, (b) repulsive force field, (c) waypoint correction, (d) emergency mode switch. The actual panels are: (a) without geofence, (b) with protection, (c) speed ramp, (d) summary table. The caption describes different panel contents than what's shown. Caption needs updating.

---

## Cross-Figure Consistency Issues

### 1. Confidence Threshold: 0.2 vs 0.4
- `cv_pipeline.png`: shows "conf > 0.2"
- `conf_vs_alt.pdf`: threshold line at 0.2
- `detection_envelope.png`: threshold line at 0.4
- `vision.py` / CLAUDE.md: threshold is 0.4
- **Action**: Decide on the correct value. If 0.4 is the operational threshold, update cv_pipeline.png, conf_vs_alt.pdf, and their captions.

### 2. Search Speed: 8 m/s vs 10 m/s
- `det_vs_speed.pdf`: annotation says "Search speed (10 m/s)"
- `evaluation.tex` caption: says "8 m/s"
- `coverage_vs_time.pdf`: Speed: 10 m/s
- `config.py`: SEARCH_SPEED_MPS = 5 (but this may have been updated)
- **Action**: Verify config.py value and make all references consistent.

### 3. CEP50: 2.2m vs 2.3m
- `gps_bullseye.png`: CEP50 = 2.2 m
- `gps_convergence.pdf`: Measured CEP = 2.3 m
- Caption in system_description.tex: "CEP50 = 2.3 m"
- **Action**: Minor, but should be consistent. Regenerate bullseye with 2.3m or update convergence to 2.2m.

### 4. Total Pipeline Latency: 198ms vs 206.5ms vs 208ms
- `cv_pipeline.png`: "~198 ms (5.1 FPS)"
- `latency_breakdown.pdf`: 206.5 ms (4.8 FPS)
- Caption in system_description.tex: "208 ms"
- **Action**: Clarify distinction. 198ms = processing only (no capture). 206.5ms = end-to-end including capture. 208ms = rounded. Add "processing" qualifier to cv_pipeline.png or include capture stage.

### 5. Model Type: INT8 vs FP32
- `latency_breakdown.pdf`: Says "TFLite INT8"
- Reality: Model is float32 (FP32)
- **Action**: MUST fix. This is factually wrong.

---

## Color Scheme Consistency

The figures use two broad color families:

**Architecture/system diagrams** (architecture, pi_system, cv_pipeline): Blue/green/orange hardware-software scheme. Consistent.

**State machine / mission figures** (state_machine, mission_timeline, mission_overview): Green/blue/orange/red for state categories. Consistent.

**Data plots** (conf_vs_alt, gps_bullseye, gps_convergence, estimator_comparison, etc.): Standard matplotlib blue with orange/red accents. Consistent.

**Overall**: Good cross-figure color consistency. The two families (system diagrams vs data plots) are visually distinct but don't clash.

---

## Priority Fixes (ordered by severity)

1. **CRITICAL -- latency_breakdown.pdf**: Change "TFLite INT8" to "TFLite FP32". Factual error.
2. **CRITICAL -- det_vs_speed.pdf**: Regenerate with meaningful curves (show detection probability at p_d=0.70, 0.85, 0.95 as separate lines, or show per-frame rate). Current flat-100% figure is uninformative.
3. **HIGH -- Confidence threshold inconsistency**: Pick 0.2 or 0.4, update all figures + text.
4. **HIGH -- gps_error_direction.png**: Regenerate at larger size (double figsize).
5. **HIGH -- state_machine_full.png**: Move to appendix or don't use. Too dense for main text.
6. **MEDIUM -- Search speed inconsistency**: Reconcile 8 vs 10 m/s across figures and text.
7. **MEDIUM -- CEP50 inconsistency**: Reconcile 2.2 vs 2.3m.
8. **MEDIUM -- geofence_diagram caption**: Update caption in system_description.tex to match actual panel contents.
9. **LOW -- pi_system.png**: Increase connection label font sizes.
10. **LOW -- blur_vs_altitude.png**: Make "Operational envelope" label text darker.
11. **LOW -- coverage_vs_time.pdf**: Trim x-axis to 1.2 min.
12. **LOW -- estimator_comparison caption**: Add "rolling average" to the caption text.
