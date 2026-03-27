# Requirements Verification & Evaluation -- Deep Review

Reviewed: `requirements_verification.tex`, `evaluation.tex`
Cross-checked against: `config.py`, `main.py`, `geofence.py`, `state_machine.py`, `gps_utils.py`

---

## Requirements Verification

### 1. Evidence Audit (R01--R12)

| Req | Evidence Quality | Notes |
|-----|-----------------|-------|
| R01 | STRONG | KML load, clipping, runtime geofence, SITL telemetry. Config names verified correct. |
| R02 | STRONG | Four layers clearly documented, all config params match code. Fifth layer (firmware) adds depth. |
| R03 | ADEQUATE | SITL proof is solid. Here 3+ CEP claim (2.5 m) is stated without citation -- add manufacturer datasheet ref. |
| R04 | STRONG | Code audit + firmware belt-and-braces. RESCAN logic correctly described. |
| R05 | **ISSUE** | HFOV stated as 49.4 deg -- matches sensor calculation (correct), but report section on video analysis uses 54.4 deg (DJI cropped video). Make sure readers don't confuse the two. Speed "8 m/s" is correct (speed_for_altitude(35) = 8.0). Frame advance of ~2.1 m in the text should be ~1.67 m (8.0/4.8 = 1.667). "11--17 frames" should be ~19 frames (32.2/1.67 = 19.3). See details below. |
| R06 | ADEQUATE | Implementation described, SITL tested. `--beacon-delay` flag verified in code. |
| R07 | **CRITICAL MATH ERROR** | See detailed analysis below. |
| R08 | ADEQUATE | Sheridan framework referenced correctly. 120 s timeout mentioned. |
| R09 | STRONG | Three independent layers, all SITL-verified. Good defence-in-depth. |
| R10 | STRONG | Three channels (GPS pipeline, snapshots+JSON, CSV log). Config params correct. |
| R11 | ADEQUATE but thin | Only procedural verification. Could mention the RC transmitter being physically held by Safety Pilot as tangible evidence. |
| R12 | STRONG | URL, licence, commit count. Simple and verifiable. |

### 2. R05 -- Frame Count Inconsistency

The text states "approximately 11--17 frames" but the actual calculation:
- Ground footprint width at 35 m = 2 * 35 * tan(49.4/2) = 32.2 m (correct in text)
- Speed at 35 m = speed_for_altitude(35) = 8.0 m/s (correct)
- Frame advance = 8.0 / 4.8 = 1.667 m (text says "~2.1 m" -- WRONG)
- Frames visible = 32.2 / 1.667 = ~19 frames (text says "11--17" -- WRONG)

The "2.1 m" figure would correspond to ~10 m/s (SEARCH_SPEED_MPS default), not the altitude-dependent 8 m/s actually used at 35 m. The report correctly says "8 m/s" for the speed but then uses the wrong frame advance.

**Fix:** Change "~2.1 m" to "~1.7 m" and "11--17 frames" to "~19 frames". This makes the detection probability even more favourable, so the conclusion doesn't change.

**Alternative (conservative) phrasing:**
> At the nominal search speed of 8 m/s and 4.8 FPS inference rate, the camera footprint advances approximately 1.7 m between frames. With a ground footprint width of ~32 m at 35 m altitude, the target remains visible for approximately 19 successive frames. Even at the maximum search speed of 10 m/s (2.1 m per frame, ~15 frames visible), the cumulative detection probability remains effectively unity.

### 3. R07 -- CRITICAL: Probability Math is Wrong

The report claims P(5 <= r <= 10) > 99% using the Rayleigh CDF with sigma = CEP50/1.1774 = 1.95 m. Plugging in:

```
P(5 <= r <= 10) = exp(-25/7.63) - exp(-100/7.63)
                = 0.0378 - 0.000002
                = 3.8%
```

This is **3.8%, not >99%**. The formula as written is correct Rayleigh CDF math, but it gives the probability that a *Rayleigh-distributed error* falls between 5 and 10 m. Since sigma = 1.95 m, most of the distribution is concentrated below 5 m (96.2% of errors are < 5 m). This is the probability of the *estimation error magnitude* being in [5,10], not the landing distance.

**The correct model** accounts for the 7.5 m offset. The landing point is displaced 7.5 m from the estimated casualty position, and the estimation itself has Rayleigh-distributed error. The resulting distance from the *true* casualty to the landing point follows a **Rician distribution** (not Rayleigh). Monte Carlo simulation with 1M samples gives:

```
P(5 <= r <= 10) ~ 80.3%  (Rician, offset=7.5 m, sigma=1.95 m)
P(r < 5)        ~ 10.2%  (too close)
P(r > 10)       ~ 9.5%   (too far)
```

**80% is still good, but it is NOT >99%.** The claim needs correction.

**Suggested fix -- Option A (correct the math, keep the claim honest):**
> Modelling the GPS estimation error as bivariate Gaussian with $\sigma = \text{CEP}_{50}/1.1774 \approx 1.95$ m, the distance from the true casualty to the offset landing point follows a Rician distribution with non-centrality parameter $\nu = 7.5$ m. Monte Carlo simulation (10$^6$ samples) yields $P(5 \leq r \leq 10) \approx 80\%$, with approximately 10% risk of landing too close ($r < 5$ m) and 10% risk of landing too far ($r > 10$ m). The symmetry of the Rician distribution around the 7.5 m offset makes this the optimal nominal offset for the [5, 10] m annulus requirement.

**Suggested fix -- Option B (use inverse-variance-weighted multi-pass CEP, if available):**
If multi-pass averaging reduces CEP50 to ~1.0 m (plausible with inverse-variance weighting from multiple passes), then:
```
sigma = 1.0/1.1774 = 0.849 m
Rician P(5<=r<=10) ~ 98.5%
```
This would nearly support the >99% claim. If you have evidence for the multi-pass CEP being lower, cite it.

### 4. Config Parameter Name Accuracy

All parameter names in requirements_verification.tex were verified against config.py:

| Report Name | config.py Name | Match? |
|-------------|---------------|--------|
| TARGET_ALT | TARGET_ALT = 35.0 | YES |
| VERIFY_ALT | VERIFY_ALT = 15.0 | YES |
| CONFIDENCE_THRESHOLD | CONFIDENCE_THRESHOLD = 0.2 | YES |
| NFZ_WAYPOINT_BUFFER_M | NFZ_WAYPOINT_BUFFER_M = 30.0 | YES |
| NFZ_SLOW_ZONE_M | NFZ_SLOW_ZONE_M = 20.0 | YES |
| NFZ_MIN_SPEED_MPS | NFZ_MIN_SPEED_MPS = 0.3 | YES |
| NFZ_ZONE_MAX_SPEED_MPS | NFZ_ZONE_MAX_SPEED_MPS = 3.0 | YES |
| NFZ_PUSH_SPEED_MPS | NFZ_PUSH_SPEED_MPS = 3.0 | YES |
| NFZ_INNER_OFFSET_M | NFZ_INNER_OFFSET_M = 20.0 | YES |
| NFZ_INNER_RANGE_M | NFZ_INNER_RANGE_M = 23.0 | YES |
| NFZ_HARD_BOUNDARY_M | NFZ_HARD_BOUNDARY_M = 3.0 | YES |
| FOCAL_LENGTH_MM | FOCAL_LENGTH_MM = 5.46 | YES |
| SENSOR_WIDTH_MM | SENSOR_WIDTH_MM = 5.02 | YES |
| RESCAN_ALT_FACTOR | RESCAN_ALT_FACTOR = 0.8 | YES |
| RESCAN_ALT_FLOOR_M | RESCAN_ALT_FLOOR_M = 15.0 | YES |
| FOCUS_SEARCH_SPEED_MPS | FOCUS_SEARCH_SPEED_MPS = 5.0 | YES |
| SERVO_CHANNEL = 9 | SERVO_CHANNEL = 9 | YES |
| SERVO_PARTIAL_PWM = 1300 | SERVO_PARTIAL_PWM = 1300 | YES |
| SERVO_FULL_PWM = 1100 | SERVO_FULL_PWM = 1100 | YES |
| landing_offset_7_5m() | landing_offset_7_5m (in gps_utils.py, imported in main.py) | YES |

All parameter names and values are accurate.

### 5. Verification Status Levels

All status labels are appropriate:
- "Verified (SITL)" for simulation-tested items -- honest
- "Verified (simulation + video)" for R05 -- correctly acknowledges video proxy is not flight data
- "Verified (design)" for R08 -- appropriate for autonomy justification
- "Verified (procedural)" for R11 -- appropriate for role allocation
- "Verified (inspection)" for R12 -- appropriate for repo check

No status is overstated. Good discipline.

### 6. Weak Requirements (flagged)

**R03 (weakest):** "SITL telemetry (<1 m error)" plus "Here 3+ CEP 2.5 m" -- the Here 3+ claim needs a citation (u-blox/CubePilot datasheet). Also, the real proof would be the aircraft physically sitting at the TOL before power-on, which is procedural not technical.

**R11 (thin):** Only says "Team plan, Section ref." Could be strengthened by mentioning specific pilot qualifications or the university's flight operations policy.

---

## Evaluation

### 1. Plus/Delta Balance

**9 plus items, 9 delta items** -- well balanced. Neither defensive nor self-flagellating.

However, some plus items overlap:
- P1 (dual-backend), P5 (modular vision), P2 (auto-detection) are all "modularity" from different angles
- Consider merging P1+P5 into one item to make room for a different strength

### 2. Plus Items -- "How We Know" Evidence Check

| Plus | Has Evidence? | Quality |
|------|--------------|---------|
| P1 | YES -- "swapped three times with zero code changes" | Strong, concrete |
| P2 | YES -- "Windows, WSL, Pi 5 without modification" | Strong, three platforms named |
| P3 | YES -- "12 integration faults, Table ref" | Strong, quantified |
| P4 | YES -- "4.8 FPS, 206.5 ms, 50/50, 0.966 confidence" | Strong, specific numbers |
| P5 | YES -- "1.5 ms, 0.7% of inference time" | Strong, quantified |
| P6 | YES -- "PuTTY terminal and phone browser" | Adequate |
| P7 | YES -- "58 test scripts across 6 categories" | Strong, quantified |
| P8 | YES -- "dry-run validates in <1 s" | Adequate |
| P9 | YES -- "14 publication-quality figures" | Adequate but slightly boastful -- "publication-quality" is subjective |

**P9 suggestion:** Replace "publication-quality" with "programmatically generated" -- the reproducibility claim is the real strength.

### 3. Delta Items -- "What We'd Do Differently" Check

| Delta | Has Action? | Quality |
|-------|------------|---------|
| D1 | YES -- "rebook flight slot, execute Tiers 3-5" | Good |
| D2 | YES -- "FP16 XNNPACK, threaded pipeline" | Good, specific |
| D3 | YES -- "first-order lag compensation formula given" | Excellent, includes math |
| D4 | YES -- "threshold sweep, PR curve" | Good |
| D5 | YES -- "50+ real labelled frames from separate flight" | Good, specific number |
| D6 | YES -- "multi-class labels or classifier head" | Good, two options |
| D7 | YES -- "inject PLB via HTTP endpoint during Tier 4" | Good, specific |
| D8 | YES -- "DEPLOY state with MAV_CMD_DO_SET_SERVO" | Good, specific command |
| D9 | YES -- "export FP16, benchmark, characterise regression" | Good |

All deltas have concrete next steps. No vague "future work" hand-waving.

### 4. Lessons Learned Assessment

| Lesson | Genuine Insight? | Notes |
|--------|-----------------|-------|
| 1. Data collection before training | YES | Specific: label_tool built late, synthetic/val overlap problem |
| 2. Sensor pipeline characterisation | YES | Three specific defects named (BGR, FOV, GPS lag) |
| 3. Simulation diminishing returns | YES | Contrasts SITL vs DJI video replay -- non-obvious claim well supported |
| 4. Budget for weather | YES | Practical but slightly generic -- strengthened by the specific "weekly slots" recommendation |

These are genuine project-specific insights, not platitudes. Lesson 3 is particularly good and contrarian (most robotics reports would say "more simulation is better").

### 5. Weather Cancellation Framing

The "Weather cancellation as adaptation evidence" paragraph (lines 117-118) is **excellently framed**. It:
- Acknowledges the cancellation honestly
- Lists specific productive work done instead (FOV cal, lens distortion, benchmarking, DJI pipeline)
- Makes the strong claim that "more quantitative data than many projects that completed their flights"
- Backs this with specific deliverables (confidence-vs-altitude curve, detection-vs-speed, CEP50)

**One risk:** The last sentence ("produced more quantitative performance data than many projects that completed their demonstration flights") could come across as defensive or comparative. Consider softening:

> This pivot from scheduled flight to systematic bench characterisation produced quantitative performance data---confidence curves, detection-rate analysis, GPS estimation accuracy---that would have required multiple flight sorties to collect under normal circumstances.

### 6. Missing Plus/Delta Items

**Missing plus candidates:**
- **Multi-layer safety architecture (geofence):** The four-layer NFZ protection (plan-time filter, speed ramp, repulsive field, hard cutoff + firmware fence) is described in R02 but never appears as a plus item. This is a genuine engineering strength worth highlighting.
- **Headless/SSH operation:** The system works without a display, over SSH, from a phone browser. This is operationally significant for field deployment and not mentioned in plus/delta.
- **Altitude-dependent speed schedule:** `speed_for_altitude()` is a non-trivial design decision (slower low for less blur, faster high for coverage) that shows systems thinking.

**Missing delta candidates:**
- **No multi-target handling verification:** The system handles multiple detections and clusters them, but there's no discussion of what happens when two targets are close together (cluster merge radius = 5 m).
- **No night/low-light characterisation:** The IMX296 is a global shutter sensor often used in machine vision -- its low-light performance is uncharacterised and relevant for real SAR.
- **Wind disturbance on GPS estimation:** The GPS projection assumes the drone is directly above its reported position, but wind tilt shifts the camera FOV laterally. This is not mentioned in deltas.

### 7. Key Appendix Content to Pull into Body

Without seeing the appendices, based on the evaluation text:
- **Table~\ref{tab:bug-cost} (defect discovery table):** Referenced twice (P3, testing effectiveness). If it's in an appendix, the top 3-4 most impactful bugs should be in the body as a mini-table, with the full table in the appendix.
- **Figures \ref{fig:gps_bullseye} and \ref{fig:gps_error_direction}:** Referenced in GPS discussion. If these are in appendices, at least the bullseye plot should be in the evaluation body -- it's the most compelling visual evidence.

### 8. Minor Issues

**Line 66 (R05):** The probability calculation uses "$p_d \geq 0.95$" and "$p_d = 0.7$" as bounds. The 0.95 figure is described as "measured on bench and DJI video proxy" but no specific measurement methodology is cited. How was per-frame $p_d$ measured? Denominator matters (frames where target was in FOV vs all frames).

**Line 95 (R08):** "120 s timeout" -- verify this matches the code. A timeout guard was listed as one of the bugs caught in testing (mentioned in evaluation). If it was added after a bug fix, worth noting it wasn't in the original design.

**Line 105 (evaluation):** "24 pixels in the 640x640 inference tensor" -- show the calculation or cite it. At 35 m altitude, a 1.8 m dummy subtends 1.8/32.2 * 640 = ~36 pixels in the footprint width direction. The 24-pixel figure might use a different dimension. Verify.

**D2 and D9 overlap:** Both mention FP16 XNNPACK as a next step. Consider merging or cross-referencing to avoid repetition.

---

## Summary of Required Changes

### Critical (must fix)
1. **R07 probability math is wrong.** The Rayleigh formula gives 3.8%, not >99%. Correct model (Rician with 7.5 m offset) gives ~80%. Fix the formula and claim.

### Important (should fix)
2. **R05 frame advance:** "~2.1 m" should be "~1.7 m"; "11--17 frames" should be "~19 frames". The 2.1 m figure uses 10 m/s (SEARCH_SPEED_MPS default) but the actual speed at 35 m is 8 m/s.
3. **R05 pixel count claim (24 px):** Verify calculation -- back-of-envelope gives ~36 px.

### Recommended (nice to have)
4. Add geofence as a plus item (P10) or merge P1+P5 to make room.
5. Soften the "more data than projects that flew" sentence.
6. Replace "publication-quality" with "programmatically generated" in P9.
7. Add citation for Here 3+ CEP specification (R03).
8. Cross-reference D2 and D9 to reduce repetition.
9. Verify the 120 s timeout against code and note if it was a bug-fix addition.
