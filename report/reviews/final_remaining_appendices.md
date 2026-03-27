# Review: Remaining Appendix Sections

**Files reviewed:**
- `streaming_architecture.tex`
- `comms_architecture.tex`
- `payload_release.tex`
- `pipeline_fps.tex`
- `centering_analysis.tex`
- `search_optimization.tex`

**Cross-referenced against:**
- `05_path_planning.tex`, `path_tradeoffs.tex`
- `04_computer_vision.tex`, `inference_architecture.tex`
- `07_target_localisation.tex`
- `08_ground_station.tex`
- `06_state_machine.tex`

---

## 1. streaming_architecture.tex

### Quality & Tone
Excellent. Reads like a mature systems-engineering justification. The protocol comparison table is clear and the four-criteria MJPEG rationale is persuasive. The bandwidth estimation subsection adds quantitative rigour often missing from appendices.

### Issues

**CONTRADICTION: Producer frame rate claim (line 124-125)**
The verbatim code comment says "Producer (main loop, ~50 Hz)" but the actual camera capture rate on the Pi is ~5 FPS (limited by inference). On the laptop in simulation it may approach 30 FPS, but 50 Hz is not achieved on either platform. This should say "~5-30 Hz depending on platform" or simply remove the frequency claim.

**CONTRADICTION: Stream FPS vs pipeline FPS**
Line 138-140 says the HTTP handler "caps the stream at approximately 20 fps" via a 50 ms sleep. This is consistent internally but creates a misleading impression. On the Pi the actual stream is ~5 FPS (inference-bound), so the 20 FPS cap is never the bottleneck. The text should clarify that 20 FPS is the *maximum* rate and the effective rate is inference-limited.

**Minor: Port 8090 vs 8091 conflict note**
Line 184 says capture_training.py "runs alongside the primary ground station." But they share the camera resource. This is stated as "avoids contention on the camera resource" -- actually both open the camera, which would conflict on the Pi (only one process can own the camera). In practice capture_training.py is used instead of passive_watch.py, not alongside it. Clarify that only one camera-using script runs at a time.

**Minor: DISPLAY check (line 152)**
The headless section shows `if not os.environ.get('DISPLAY')` -- this is Linux-only. On Pi this works, but on Windows (where DISPLAY is never set) this would always trigger headless mode. The actual code likely has a more nuanced check. Verify the verbatim matches the real implementation.

**Citation: RFC 2435**
Section 08_ground_station.tex cites `rfc2435` for MJPEG, and this file cites `munoz2016mjpeg`. Both are used for the same claim (browser decoding of multipart/x-mixed-replace). The RFC 2435 citation in 08_ground_station is actually for RTP JPEG, not MJPEG over HTTP. Consider using a consistent citation.

### Missing Content
- No mention of CORS or security considerations for the HTTP server (acceptable for a LAN-only deployment, but worth one sentence acknowledging it).

---

## 2. comms_architecture.tex

### Quality & Tone
Strong. The Python 3.13 serial problem is well-documented. The four-tier auto-detection cascade is one of the best-written subsections in the report -- clear, concise, and verifiable.

### Issues

**CONTRADICTION: Heartbeat rate**
Line 73 states heartbeat at 1 Hz (correct per MAVLink spec), but the link-loss section (line 94) describes `recv_match` raising `ConnectionResetError` as the trigger for RTL. This is a UDP connection -- UDP does not raise ConnectionResetError. ConnectionResetError would come from TCP (Mission Planner path). For the UDP path (main.py), the actual link-loss detection is a heartbeat timestamp timeout, not an exception. The exception handling is a secondary defence for TCP consumers. This distinction should be clarified.

**CONTRADICTION: GPS degradation satellite threshold**
Line 96 says "satellite count falls below 6 for more than 5 seconds." Check against config.py -- the code may use a different threshold (often 5 satellites or fix_type < 3 alone). If the values differ from the deployed config, update.

**Minor: Latency arithmetic**
Line 101 says "32-byte MAVLink v2 frame requires approximately 0.35 ms for serial transmission." At 921600 baud, 32 bytes = 256 bits. 256/921600 = 0.278 ms. The 0.35 ms figure assumes ~10 bits per byte (start/stop bits), which gives 320/921600 = 0.347 ms. The calculation is correct but the rounding to 0.35 is slightly generous -- fine for an order-of-magnitude argument.

**Minor: Figure format**
The ASCII-art topology diagram (lines 29-41) is effective but will render in monospace in the PDF. Consider whether a proper TikZ figure would be more professional, or at least wrap in a `\texttt` block for consistent formatting. Currently uses `\begin{verbatim}` which is fine.

### Missing Content
- No discussion of MAVLink signing or authentication. For a university project this is acceptable, but one sentence noting that authentication was not required for the isolated network would be thorough.

---

## 3. payload_release.tex

### Quality & Tone
Well-structured. The five-reason justification for hover release vs landing is convincing. The probability analysis cross-referencing centering_analysis.tex is tight.

### Issues

**CONTRADICTION: File references that do not exist in the codebase**
- Line 30 references `gps_utils.py` -- this file does not exist in the project structure. The offset function is in `utils.py` (per CLAUDE.md). Must be corrected.
- Line 35 references `state_machine.py` -- this file does exist per the state machine section (06_state_machine.tex line 16 confirms it). This is fine.

**CONTRADICTION: Hover_Target vs state machine**
Line 35 says payload deployment happens in "Hover_Target state, implemented in state_machine.py." This is consistent with 06_state_machine.tex line 65 which describes HOVER_TARGET with the same 15-second sequence. No conflict.

**INCONSISTENCY: Descent altitude**
Line 38 says the drone descends to "3 m AGL" during approach. But centering_analysis.tex line 8 says the centering pipeline descends from "35 m to 15 m in increments" -- and the payload release bypasses centering, proceeding "directly from a confirmed detection to a 7.5 m offset landing" (centering_analysis.tex line 3). The question is: at what altitude does the drone fly to the offset point? payload_release.tex says 3 m, but the state machine section (06_state_machine.tex line 64) says "3 m altitude" for APPROACH. This seems consistent but note that 3 m AGL is very low and aggressive for GPS-only navigation. One sentence acknowledging this risk or referencing the ArduPilot rangefinder integration would strengthen the argument.

**INCONSISTENCY: CEP50 value**
Line 20 cites CEP50 = 2.3 m "from Section sec:localisation." Line 30 then uses "sigma_fused ~ 0.80 m" with N_eff = 6. centering_analysis.tex equations 1-4 use the same values. These are all internally consistent.

**Minor: "Close and depart" timing**
Line 46 says close-and-depart at t=15s, but full release is at t=6s. That leaves 9 seconds of hovering after release with no payload. The text says this is to "prevent snagging during climb-out" but the servo closes immediately at t=15s. It would be more accurate to say the 9-second gap ensures the payload has fully separated and any swinging has dampened before closing the mechanism and climbing.

**Missing Content**
- No mention of payload mass or its effect on flight characteristics (CG shift after release, reduced weight improving endurance).
- No mention of what happens if the servo fails to actuate (timeout? retry? abort?).

---

## 4. pipeline_fps.tex

### Quality & Tone
Outstanding. This is one of the strongest appendix sections. The distinction between raw and effective FPS is genuinely insightful and well-supported by data. The bottleneck transition analysis with the stacked bar chart is excellent.

### Issues

**CONTRADICTION: NCNN raw latency -- two different values**
- pipeline_fps.tex Table 1 (line 38): NCNN raw latency = ~77 ms, ~13 FPS
- inference_architecture.tex Table (line 26): NCNN projected latency = ~68 ms, ~15 FPS
- pipeline_fps.tex paragraph (line 50): NCNN "benchmarked on the Pi 5 at approximately 77 ms"

The inference_architecture.tex value of 68 ms is attributed to Ultralytics' published figure, while pipeline_fps.tex uses 77 ms from actual benchmarking. This discrepancy should be harmonised. Either: (a) use 77 ms everywhere as the measured value and note Ultralytics claims 68 ms, or (b) explain the discrepancy (different model version, warm-up, etc.).

**CONTRADICTION: NCNN effective FPS**
pipeline_fps.tex line 50 says effective FPS was "8-9 FPS" during integrated testing, but the table says ~10.9 FPS. The text explains the discrepancy (cache contention, preprocessing overhead), but the table should show the measured 8-9 FPS rather than the calculated 10.9 FPS, or add a "measured" column alongside "projected."

**Minor: TFLite raw latency**
Table says 196 ms raw, but inference_architecture.tex says 206.5 ms. The difference is likely that 196 ms is raw inference only while 206.5 ms includes some overhead. The text explains this correctly (196 ms raw + 12 ms overhead = 208 ms total, yielding 4.8 FPS), but earlier benchmark reports (CLAUDE.md session logs) consistently say 206.5 ms. If 206.5 ms was the measured end-to-end and 196 ms is the isolated inference, make this clearer.

**Minor: Along-track footprint**
Line 93 says "ground distance between consecutive analysed frames is 1.67 m" at 4.8 FPS and 8 m/s. Check: 8/4.8 = 1.67 m. Correct. Then says "32.2 m horizontal field of view" -- but 32.2 m is the cross-track width. The along-track footprint at 35 m altitude is approximately 24 m (the height dimension of the sensor). A target at the centre would be observed in 24/1.67 = ~14 frames. This is correctly stated. Good.

### Missing Content
- No mention of thermal throttling. The Pi 5 can thermally throttle under sustained load, which would increase inference latency over time. One sentence noting that no throttling was observed during 2-minute missions (with passive cooling / heatsink) would be valuable.

---

## 5. centering_analysis.tex

### Quality & Tone
Very good. The probability analysis is mathematically rigorous and well-presented. The simulation comparison table effectively supports the design decision.

### Issues

**POTENTIAL ISSUE: Probability model assumptions**
Equation 2 (line 35) models the landing distance as r = d0 + epsilon, where epsilon is projected onto the offset axis. This is a 1D simplification. The text acknowledges this ("conservative uni-axial projection gives a lower bound of 80%") which is correct. However, Equation 3 (line 41) then uses the fused sigma and gets >99%, but this assumes the lateral error component only moves the landing point around the annular band. This is approximately true when sigma_fused << d0 (0.80 << 7.5), so the small-angle approximation holds. The analysis is sound but could benefit from one sentence stating this condition explicitly.

**INCONSISTENCY: "Mean Error" column interpretation**
Table line 59: "Mean Error" is described as "the absolute deviation of the actual landing distance from the intended 7.5 m offset." For the direct offset approach: mean error 3.1 m means the landing was on average at 7.5 +/- 3.1 m = between 4.4 and 10.6 m from the target. But the "In 5-10 m Band" column says 95% (19/20). An outlier at 11.2 m and a mean error of 3.1 m seems high -- this would imply large variance. Check: if mean absolute deviation is 3.1 m and the distribution is Gaussian with sigma ~1.95 m, the expected MAD would be sigma * sqrt(2/pi) ~ 1.55 m. A MAD of 3.1 m suggests either the simulation noise was higher than the analytical model, or the "mean error" is actually the mean distance from the true target (not from the 7.5 m nominal). Clarify which interpretation is intended.

**Minor: Visual servo oscillation**
Line 14 mentions "three of twenty centering runs exhibited oscillatory lateral corrections at 8 m altitude." This is mentioned again in line 65. The repetition is fine for emphasis but could be condensed slightly.

**Minor: Wind vector reference**
Line 21 says offset is "perpendicular to the wind vector when available, otherwise due south." This is the first mention of wind-aware offset direction. payload_release.tex line 30 says "operator-selected cardinal direction (N/E/S/W)." These are slightly different -- one is wind-based, the other is operator-selected. Clarify which takes priority in the actual implementation.

### Missing Content
- No confidence interval on the simulation results (20 runs is a small sample).
- No discussion of what happens when GPS multipath is sustained rather than a single spike.

---

## 6. search_optimization.tex

### Quality & Tone
Excellent. The most quantitatively rigorous appendix. The energy simulation, rotation analysis, and Pareto trade-off summary are publication-quality.

### Issues

**MAJOR CONTRADICTION: Energy model parameters differ from 05_path_planning.tex**
- search_optimization.tex (line 30): P_hover ~ 350 W, P_forward ~ 380 W at 10 m/s
- 05_path_planning.tex (line 99-100): P_hover = 150 W, P_total = 150 + 50(v/v_ref)^2

These are completely different power models. At v=10 m/s, the path_planning model gives P_total = 150 + 50*(10/5)^2 = 150 + 200 = 350 W, which actually does agree with the hover power in search_optimization. But the hover power is different: 150 W vs 350 W. The search_optimization model uses momentum theory (P = sqrt(T^3/(2*rho*A))), which for a 2.3 kg quad with 5-inch props gives a realistic ~350 W. The 150 W in 05_path_planning is unrealistically low for any quadcopter.

**Resolution needed:** Either (a) update 05_path_planning.tex to use the 350 W momentum-theory model from search_optimization.tex, or (b) explain that 05_path_planning uses a simplified relative model for parameter comparison while search_optimization uses a physics-based absolute model. Currently the reader will notice the 2.3x discrepancy in hover power and question the energy numbers.

**CONTRADICTION: Energy values in the sweep**
search_optimization.tex Table 1 (line 48): rank 5 (the selected point at 35m/8m/s) = 12.6 Wh. With a 115.4 Wh battery (line 12), this is 10.9% of capacity.

05_path_planning.tex does not give absolute Wh values for the selected point, so no direct conflict in the numbers. But the 150 W hover model would produce roughly half the energy of the 350 W model, which would make the energy numbers in the two sections irreconcilable if compared.

**INCONSISTENCY: Configuration sweep dimensions**
- 05_path_planning.tex line 89: "216 configurations: 6 altitudes x 36 scan angles"
- search_optimization.tex line 22: "216 configurations comprising 19 rotation angles x 7 altitudes x 11 speeds" -- but 19 * 7 * 11 = 1463, not 216.

This is clearly an error. Either the number of configurations is wrong (should be 1463) or the parameter ranges are wrong. If the intent was 216 = 6*36 (matching path_planning), then the "19 angles x 7 altitudes x 11 speeds" description is incorrect. Fix.

**INCONSISTENCY: Altitude range in sweep**
- 05_path_planning.tex line 89: "6 altitudes (20, 25, 30, 35, 40, and 50 m)"
- search_optimization.tex line 22: "7 altitudes (20-50 m in 5 m steps)" = 20,25,30,35,40,45,50 = 7 values

05_path_planning has 6 altitudes (skips 45 m), search_optimization has 7. One is wrong.

**INCONSISTENCY: Scan angle steps**
- 05_path_planning.tex: "36 scan angles (0-175 deg in 5 deg steps)"
- search_optimization.tex: "19 rotation angles (0-180 deg in 10 deg steps)"

Different granularity. The total 216 in path_planning = 6*36. In search_optimization, 19*7 = 133 (without speed) or 19*7*11 = 1463 (with speed). Neither matches 216.

**Minor: E_turn units**
Line 32: "E_turn ~ 15 Wh per U-turn." This seems extremely high. 15 Wh per turn would mean that 4 turns cost 60 Wh -- more than half the battery. This is almost certainly a units error. At 350 W hover for 3 seconds, the turn energy is 350*3/3600 = 0.29 Wh, plus kinetic energy 0.5*2.3*8^2 = 73.6 J = 0.020 Wh. Total ~ 0.31 Wh per turn. The value should be ~0.3 Wh, not 15 Wh. Fix.

**Minor: Effective coverage equation**
Line 108-109: The equation P_eff = 0.96 + 0.04 * 0.0 * 0.1 = 0.96 uses a detection probability of 0.0 for the uncovered zone (because it is not imaged), which makes the second term zero regardless of the access probability factor. The equation is technically correct but trivially so -- it reduces to 0.96 + 0 = 0.96. The prose argument is more persuasive than the equation. Consider whether the equation adds value or is misleadingly formal.

**Minor: NFZ margin table "Total margin" column**
Table (line 141-151): "Total margin" is listed as 50 m for all altitudes (30 m waypoint buffer + 20 m slow zone). But "Surplus" = Total margin - Footprint radius, not Total margin - Min drone dist. Actually Surplus = 50 - footprint_r, which checks out (e.g., 50 - 9.2 = 40.8). But "Min drone dist" = footprint_r, which is the distance from the drone to the boundary needed to keep the footprint out. The actual margin between the drone path and the boundary is the waypoint buffer (30 m), and the surplus should be 30 - footprint_r. The table uses "Total margin" = 50 m, which includes the slow zone, but the slow zone does not prevent the drone from being there -- it only slows it down. The surplus is overstated. At 50 m altitude, the footprint radius is 23 m, and the waypoint buffer is 30 m, giving only 7 m surplus (not 27 m). Recalculate or clarify.

### Missing Content
- No sensitivity analysis on the power model parameters (drag coefficient, rotor disc area). Given the two different models in the report, this would help the reader understand confidence bounds.

---

## Summary of Cross-Section Contradictions

| Issue | Sections | Severity |
|-------|----------|----------|
| Energy model: P_hover = 150 W vs 350 W | 05_path_planning vs search_optimization | **HIGH** |
| Configuration sweep: 216 vs 1463 | 05_path_planning vs search_optimization | **HIGH** |
| E_turn = 15 Wh (should be ~0.3 Wh) | search_optimization | **HIGH** |
| NCNN latency: 68 ms vs 77 ms | inference_architecture vs pipeline_fps | MEDIUM |
| TFLite latency: 196 ms vs 206.5 ms | pipeline_fps vs benchmarks | LOW |
| gps_utils.py does not exist | payload_release | MEDIUM |
| Altitude count: 6 vs 7 | 05_path_planning vs search_optimization | MEDIUM |
| Scan angle steps: 5 deg vs 10 deg | 05_path_planning vs search_optimization | MEDIUM |
| Offset direction: wind vs operator | centering_analysis vs payload_release | LOW |
| Producer rate: "~50 Hz" is misleading | streaming_architecture | LOW |
| NFZ surplus margin overstated | search_optimization | MEDIUM |
| UDP does not raise ConnectionResetError | comms_architecture | LOW |
| Camera resource sharing claim | streaming_architecture | LOW |

## Priority Fixes

1. **Harmonise energy models** between 05_path_planning.tex and search_optimization.tex. The momentum-theory model (350 W) is physically correct; the 150 W model is not.
2. **Fix E_turn = 15 Wh** in search_optimization.tex -- should be ~0.3 Wh.
3. **Fix configuration sweep count** in search_optimization.tex -- either 216 or 1463, with matching parameter ranges.
4. **Fix gps_utils.py reference** in payload_release.tex to `utils.py`.
5. **Harmonise NCNN latency figures** across inference_architecture.tex and pipeline_fps.tex.
6. **Recalculate NFZ surplus** using waypoint buffer alone (not waypoint buffer + slow zone).
