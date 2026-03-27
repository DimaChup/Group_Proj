# Requirements Verification -- Brutal Goldmine Review

**File**: `report/sections/requirements_verification.tex`
**Reviewed**: 2026-03-27

---

## Overall Assessment

The section is well-structured with per-requirement subsections, concrete config parameter names, and honest verification status labelling. The probability math in R07 is correct. The probability math in R05 has a significant error in the overlap calculation that cascades into wrong N_eff and wrong P_detect. Several claims overstate what was actually tested on real hardware.

---

## CRITICAL Issues (must fix)

### C1. R05: Overlap calculation is WRONG (92% claimed, 80% at best)

The report states overlap = 91% and N_eff = 1.7. Verified computation:

- Advance per frame: 8.0 / 4.8 = 1.667 m
- Frame overlap = 1 - (1.667 / 32.2) = **94.7%**, not 91%
- N_eff = 19 * (1 - 0.947) = **1.0**, not 1.7
- P_detect = 1 - 0.05^1.0 = **0.95**, not 0.92

The formula `N_eff = N * (1 - alpha)` is ad-hoc and not from any established source. With correct overlap (94.7%), N_eff collapses to ~1.0, meaning the per-pass probability simply equals p_d = 0.95. The 0.92 figure is wrong.

**Worse**: the report uses the **width** footprint (32.2 m) for the along-track visibility calculation. The camera sees a rectangle on the ground; the along-track dimension is the **height** footprint = 32.2 * (1088/1456) = **24.0 m**. This gives only ~14 frames, not 19. With correct height footprint, overlap = 93.1%, N_eff still ~1.0, P_detect still = p_d.

**The degraded case is also wrong**: at 10 m/s with p_d=0.7, the same N_eff~1.0 logic gives P_detect = 0.70, not 0.79. The "79%" figure is fiction.

**Fix**: Either (a) drop the entire N_eff/overlap correction and simply state P_detect = p_d per pass with the two-pass formula P_two = 1-(1-p_d)^2 = 99.75%, or (b) use an established temporal correlation model (e.g., exponential decorrelation with a physically motivated correlation length). Option (a) is honest and still gives a strong 99.75% two-pass number.

### C2. R07: "After touchdown, the aircraft returns to the TOL via MAV_CMD_NAV_RETURN_TO_LAUNCH" -- FALSE

The actual code flow is:
1. APPROACH -> HOVER_TARGET (servo deploy at 3m)
2. HOVER_TARGET -> RETURN_TRANSIT (retrace pre-waypoints at search alt)
3. RETURN_TRANSIT -> RETURN_HOME (fly to home_lat, home_lon)
4. RETURN_HOME -> LANDING (MAV_CMD_NAV_LAND at home position)

The drone returns to home BEFORE landing, not after. It uses `MAV_CMD_NAV_LAND`, NOT `MAV_CMD_NAV_RETURN_TO_LAUNCH`. The RTL command is only used in emergency failsafes. The report has the sequence completely backwards -- the drone lands near the casualty, deploys payload, then returns home and lands again? No -- it hovers at 3m, deploys payload, then climbs, retraces transit, and lands at home.

**Fix**: Rewrite to: "After payload deployment at 3 m altitude, the aircraft climbs to search altitude, retraces its transit waypoints, and lands at the TOL via `MAV_CMD_NAV_LAND`."

### C3. R05: HFOV = 49.4 degrees is Pi camera HFOV, but the 54.4-degree figure from video analysis is for DJI

The report correctly uses 49.4 deg HFOV (matches config: 2*atan(5.02/(2*5.46)) = 49.4 deg). This is accurate. BUT: the mAP50=0.995 was validated on DJI video proxy at 54.4 deg HFOV. The actual Pi camera has a narrower FOV, meaning the dummy appears ~10% larger at the same altitude on the Pi, which should HELP detection. This is fine but should be noted -- the DJI proxy validation is slightly pessimistic for the Pi camera. Not technically wrong, just worth one sentence of honesty.

---

## HIGH Issues (strongly recommend fixing)

### H1. R07: Servo deployment described as "during APPROACH before landing" -- wrong state

Report says "A Tarot servo... deploys the first-aid kit via a two-stage PWM sequence during APPROACH before landing." The servo actually fires during **HOVER_TARGET** state (3-second partial, 6-second full release), not during APPROACH. APPROACH merely flies to the offset point; HOVER_TARGET is where the hover + deploy happens.

**Fix**: "deploys the first-aid kit via a two-stage PWM sequence during a 15-second hover at 3 m altitude (HOVER_TARGET state)."

### H2. Evidence column honesty -- "Verified (SITL)" vs "Verified (simulation + video)"

The table correctly labels most items as "Verified (SITL)". However:
- **R01**: "geofence unit test" -- this test (`tests/automated/geofence_unit_test.py`) exists and tests geometry, but not in flight. Honest.
- **R05**: "Verified (simulation + video)" -- the DJI video proxy is NOT the Pi camera. Should say "Verified (SITL + DJI video proxy + Pi bench)".
- **R06**: "Verified (SITL)" -- SITL diversion + resume. Honest.
- **R07**: "Verified (simulation)" -- the probability analysis is pure math, CEP50 is from DJI video analysis, not real Pi flights. Should say "Verified (analysis + DJI proxy)".

### H3. R05: "100% recall on the validation set" is misleading

mAP50=0.995 and 100% recall on a 366-image dataset (300 synthetic + 16 real + 50 negative) is not particularly impressive when 300/366 images are synthetic. The 16 real images are extremely few for a recall claim. The report should note the dataset composition more carefully -- "100% recall on the validation set (predominantly synthetic)" or simply drop the recall claim and let mAP50 speak for itself.

### H4. R09: "Three independent RTH mechanisms" -- independence is overstated

The report says "any one of which is sufficient." The RC kill switch is truly independent (hardware). But the software M-key and the GPS failsafe both run on the same companion computer -- if the Pi crashes or hangs, BOTH are lost. The firmware failsafes (GCS heartbeat loss, battery) provide the actual second independent layer. The section somewhat conflates software-layer failsafes with hardware-layer ones.

### H5. SEARCH_SPEED_MPS = 10.0 in config but report says "nominal 8 m/s"

The config default `SEARCH_SPEED_MPS = 10.0` but the altitude-dependent schedule at 35m gives 8.0 m/s. The report correctly says "nominal search speed of 8 m/s (altitude-dependent schedule at 35 m)" which is accurate. However, `SEARCH_SPEED_MPS` is documented as "Default search pass speed" at 10 m/s. If someone reads the config, they'd think 10 is the speed. The report should mention the altitude schedule more explicitly or reference `speed_for_altitude()`.

---

## MEDIUM Issues (nice to fix)

### M1. R01: "35 waypoints across 5 parallel passes" -- unverified specific number

The exact waypoint count depends on scan angle optimization. Is 35 actually the current output? If the path optimizer has been run since, this could be stale. Verify or use approximate language ("~30-40 waypoints").

### M2. R02: "Four independent protection layers" but actually lists five

Paragraph lists 4 numbered items, then a 5th (firmware fence) in the following text. Either say "five layers" or restructure. Currently the enumerate has 4 and the 5th is outside it with "a fifth layer" phrasing, which is technically fine but slightly confusing.

### M3. R03: "Here 3+ GPS receiver's 2.5 m CEP" -- no source cited

The 2.5m CEP for the Here 3+ is stated without citation. This is a datasheet spec -- cite the datasheet or CubePilot documentation.

### M4. R04: "RESCAN_ALT_FACTOR = 0.8, floor RESCAN_ALT_FLOOR_M = 15.0" is correct

Verified against config.py lines 162-163. These are accurate.

### M5. R10: "flight_log.csv" path should be "logs/flight_log.csv"

Report says "A CSV file (flight_log.csv)" but config.py has `LOG_FILE = "logs/flight_log.csv"`. Minor path inaccuracy.

### M6. R06: "flight_plans/focus_area.json" -- correct path, verified

The report correctly references this path and the B-key trigger. The `--beacon-delay` flag is confirmed at main.py line 52.

### M7. R08: "120 s timeout at the verify state" -- correct

Verified: `state_machine.py` line 513: `remaining = 120 - elapsed_v` and line 517 confirms auto-reject.

### M8. R12: "268+ commits" -- now 408+

The repo has 408 commits as of now. Update the number or use "400+" for accuracy.

---

## Config Parameter Name Audit

| Report claims | Config actual | Match? |
|---|---|---|
| `CONFIDENCE_THRESHOLD = 0.2` | `CONFIDENCE_THRESHOLD = 0.2` (line 97) | YES |
| `TARGET_ALT = 35.0` | `TARGET_ALT = 35.0` (line 55) | YES |
| `VERIFY_ALT = 15.0` | `VERIFY_ALT = 15.0` (line 56) | YES |
| `FENCE_ALT_MAX` (firmware) | Not in config.py (firmware param) | N/A |
| `NFZ_WAYPOINT_BUFFER_M = 30` | `NFZ_WAYPOINT_BUFFER_M = 30.0` (line 116) | YES |
| `NFZ_SLOW_ZONE_M = 20` | `NFZ_SLOW_ZONE_M = 20.0` (line 117) | YES |
| `NFZ_MIN_SPEED_MPS = 0.3` | `NFZ_MIN_SPEED_MPS = 0.3` (line 118) | YES |
| `NFZ_ZONE_MAX_SPEED_MPS = 3.0` | `NFZ_ZONE_MAX_SPEED_MPS = 3.0` (line 119) | YES |
| `NFZ_INNER_OFFSET_M = 20` | `NFZ_INNER_OFFSET_M = 20.0` (line 120) | YES |
| `NFZ_INNER_RANGE_M = 23` | `NFZ_INNER_RANGE_M = 23.0` (line 121) | YES |
| `NFZ_PUSH_SPEED_MPS = 3.0` | `NFZ_PUSH_SPEED_MPS = 3.0` (line 122) | YES |
| `NFZ_HARD_BOUNDARY_M = 3` | `NFZ_HARD_BOUNDARY_M = 3.0` (line 114) | YES |
| `RESCAN_ALT_FACTOR = 0.8` | `RESCAN_ALT_FACTOR = 0.8` (line 162) | YES |
| `RESCAN_ALT_FLOOR_M = 15.0` | `RESCAN_ALT_FLOOR_M = 15.0` (line 163) | YES |
| `FOCAL_LENGTH_MM = 5.46` | `FOCAL_LENGTH_MM = 5.46` (line 82) | YES |
| `SENSOR_WIDTH_MM = 5.02` | `SENSOR_WIDTH_MM = 5.02` (line 81) | YES |
| `SERVO_CHANNEL = 9` | `SERVO_CHANNEL = 9` (line 182) | YES |
| `SERVO_PARTIAL_PWM = 1300` | `SERVO_PARTIAL_PWM = 1300` (line 184) | YES |
| `SERVO_FULL_PWM = 1100` | `SERVO_FULL_PWM = 1100` (line 185) | YES |
| `FOCUS_SEARCH_SPEED_MPS = 5.0` | `FOCUS_SEARCH_SPEED_MPS = 5.0` (line 60) | YES |
| HFOV 49.4 deg | 2*atan(5.02/(2*5.46)) = 49.4 deg | YES |

All config parameter names are accurate. Well done.

---

## R07 Probability Math Verification

- CEP50 = 2.3 m -> sigma = 2.3 / 1.1774 = **1.953 m** (report rounds to 1.95: OK)
- z-scores: (10-7.5)/1.953 = 1.280, (5-7.5)/1.953 = -1.280 (report says 1.28: OK)
- Phi(1.28) - Phi(-1.28) = 0.8997 - 0.1003 = **0.7994 ~ 80%** (report says ~80%: CORRECT)
- Fused sigma: 1.953 / sqrt(6) = **0.797 m** (report says ~0.80: OK)
- Fused P(5<=r<=10): **99.83%** (report says >99%: CORRECT)

R07 math is verified and correct.

---

## SITL-only vs Real Hardware Evidence Matrix

| Req | SITL evidence | Real hardware evidence | Gap |
|---|---|---|---|
| R01 | Full mission telemetry, geofence unit test | None | Need outdoor GPS flight |
| R02 | Multi-angle approach SITL | None | Need outdoor near-SSSI test |
| R03 | SITL home position <1m error | None (GPS accuracy untested in field) | |
| R04 | Config audit (no altitude >35m) | None | Low risk -- config is clear |
| R05 | SITL end-to-end + DJI video proxy | Pi bench (50/50 at 0.966) | No outdoor aerial detection test |
| R06 | SITL B-key diversion + resume | None | |
| R07 | Probability analysis only | CEP50 from DJI video (not Pi) | No real landing offset test |
| R08 | Design rationale | None | Autonomy levels are design, not testable |
| R09 | SITL: RC, M-key, GPS failsafe | None (RC override not tested on real hardware) | |
| R10 | SITL ground station logs | Pi bench (camera stream works) | No outdoor GPS estimation test |
| R11 | Procedural | Team plan exists | |
| R12 | Repository inspection | Public repo confirmed | Fully verified |

**Key gap**: NO requirement has been verified with real outdoor flight. All "Verified (SITL)" claims are honest but the examiner will note that SITL cannot validate GPS accuracy, wind effects, detection range, or EMI interference. The report should add one sentence acknowledging this -- e.g., "All SITL-verified requirements await outdoor flight validation; the progressive test plan (Section X) is designed to close this gap."

---

## Summary of Required Fixes

| # | Severity | Fix |
|---|---|---|
| C1 | CRITICAL | Fix R05 overlap math or drop the N_eff framework entirely |
| C2 | CRITICAL | Fix R07 claim about MAV_CMD_NAV_RETURN_TO_LAUNCH -- it's MAV_CMD_NAV_LAND, and RTH happens BEFORE landing |
| C3 | CRITICAL | Clarify DJI proxy vs Pi camera FOV in R05 validation |
| H1 | HIGH | Fix servo deployment state name (HOVER_TARGET, not APPROACH) |
| H2 | HIGH | Sharpen evidence source labels in table |
| H3 | HIGH | Qualify "100% recall" with dataset composition caveat |
| H4 | HIGH | Acknowledge companion-computer single point of failure in R09 |
| H5 | HIGH | Clarify altitude-dependent speed schedule vs SEARCH_SPEED_MPS |
| M5 | MEDIUM | Fix flight_log.csv path to logs/flight_log.csv |
| M8 | MEDIUM | Update commit count from 268+ to 400+ |
