# D6 Goldmine Report Consistency Audit

Audited all `.tex` files in `report/sections/` for numerical, terminological, and factual consistency.

---

## Issues Found and Fixed

### 1. Detection rate: 30/30 vs 50/50 (FIXED)
- **File:** `04_computer_vision.tex` line 100
- **Was:** `Detection rate & 30/30 & 30/30` (Table `cv_benchmarks`)
- **Should be:** `50/50` -- every other file (`11_field_results.tex`, `cv_extended.tex`, `evaluation.tex`, `field_day_narrative.tex`, `system_description.tex`, `development_methodology.tex`) consistently says 50/50 (50-run benchmark).
- **The same table's own caption says "50-run average"**, contradicting the 30/30 in the body.
- **Fix applied:** Changed to `50/50`.

### 2. Inference time: "approximately 200 ms" vs 206.5 ms (FIXED)
- **File:** `02_system_architecture.tex` line 78
- **Was:** "approximately 200\,ms"
- **Should be:** ~206 ms -- all benchmark tables say 206.5 ms precisely.
- **Fix applied:** Changed to "approximately 206\,ms".

### 3. Geofence layers: "four-layer" vs "five-layer" (FIXED in 3 files)
- The correct count is **five layers**: (1) plan-time waypoint filter, (2) speed ramp, (3) repulsive field, (4) hard boundary cutoff, (5) firmware backup.
- **Consistently "five-layer" in:** `exec_summary.tex`, `13_safety_risk.tex`, `design_strategy.tex`, `design_rationale.tex`, `mission_flow.tex`, `steeple.tex`, `development_methodology.tex`.
- **Was "four-layer" (FIXED):**
  - `contingency.tex` line 42 -- changed to "Five-layer geofence"
  - `requirements_verification.tex` line 15 -- changed to "Five-layer NFZ"
  - `system_description.tex` line 156 -- changed to "five-layer SSSI geofence"
- **Intentionally "four-layer" (NOT changed):**
  - `focus_and_repulsive.tex` -- explicitly scoped to "four software layers" (firmware layer is described separately). Context makes this correct.

### 4. State count: 19 vs 20 states (FIXED in 3 files)
- The correct count is **20 states** per `A1_state_table.tex`, `06_state_machine.tex`, `exec_summary.tex`, `system_description.tex`, `design_rationale.tex`.
- **Was "19 states" (FIXED):**
  - `02_system_architecture.tex` line 42 -- changed to "20 named states"
  - `09_simulation.tex` line 115 -- changed to "20-state"
  - `simulation_validation.tex` lines 19, 81 -- changed both to "20 states"

### 5. Airframe cost: "under 400" vs ~565 (FIXED)
- **File:** `15_conclusion.tex` line 3
- **Was:** "complete airframe cost under \pounds400"
- **Should be:** ~565 (matches both BOM tables in `03_hardware_platform.tex` and `system_description.tex`)
- **Fix applied:** Changed to "approximately \pounds565".

### 6. System cost: "under 500" vs ~565 (FIXED)
- **File:** `03_hardware_platform.tex` line 3
- **Was:** "the complete system costs under \pounds500"
- **Should be:** ~565 (matches its own BOM table showing Total = ~565)
- **Fix applied:** Changed to "approximately \pounds565".

### 7. Heartbeat timeout: 3s vs 5s (FIXED)
- **File:** `system_description.tex` line 156
- **Was:** "3 second heartbeat timeout"
- **Should be:** 5 seconds -- consistent with `02_system_architecture.tex` ("5 s"), `06_state_machine.tex`, `mission_flow.tex` ("five seconds"), `08_ground_station.tex` ("five seconds").
- **Fix applied:** Changed to "5 second".

---

## Issues Found -- Consistent (No Fix Needed)

### 8. Inference time: 206.5 ms / 4.8 FPS / 206 ms
- Used consistently across all files. Some places round to "206 ms" or "~200 ms" in prose (acceptable rounding). The precise figure 206.5 ms appears in all tables and benchmark discussions.

### 9. Altitude: 35 m consistently
- The nominal search altitude is consistently **35 m** everywhere. Some places mention 30 m as a reference altitude for the inverse-variance weighting formula ($h_{ref} = 30$ m) or as an alternate configuration in the sweep. The default `TARGET_ALT` is always 35 m. No inconsistency.

### 10. mAP50: 0.995 consistently
- All files consistently quote mAP50 = 0.995 for the v2 model. No "99.5%" vs "0.995" inconsistency found.

### 11. CEP50 = 2.3 m consistently
- All files consistently quote CEP50 = 2.3 m from DJI video analysis. Maximum error 16.5 m is also consistent.

### 12. Tilt correction: 6.2 m -> 0.3 m consistently
- The `gps_estimation_deep.tex` appendix consistently quotes 6.2 m error at 10-degree pitch reduced to ~0.3 m with compensation. The `evaluation.tex` P10 entry matches. No inconsistency.

### 13. Model name: YOLOv8n consistently
- Always referred to as "YOLOv8n" (nano variant). No inconsistency.

### 14. Requirements: "12 requirements" / "R01--R12"
- Consistently "twelve" or "12" requirements everywhere. No inconsistency.

### 15. Test scripts: "74 test scripts" and "127 unit tests"
- Consistently quoted across `exec_summary.tex`, `system_description.tex`, `evaluation.tex`, `10_testing.tex`. No inconsistency.

### 16. Confidence threshold: 0.2 consistently
- All files that mention the confidence threshold say 0.2 (not 0.4). The CLAUDE.md mentions 0.4 as an old value in vision.py, but all report files use 0.2 consistently.

### 17. Terminology: "casualty" vs "dummy" vs "mannequin" vs "target"
- **Usage pattern is consistent by context:**
  - "mannequin" or "dummy" -- when referring to the physical test object
  - "casualty" -- when referring to the SAR scenario or operational context
  - "target" -- when referring to the detection pipeline's output
  - "rescue mannequin" -- defined once in `intro_d6.tex` as the canonical term
- This is appropriate contextual usage, not an inconsistency.

### 18. Airframe: "S500 quadcopter" vs "EDU-450 hexacopter" (NOT FIXED -- needs human decision)
- `03_hardware_platform.tex` describes an "S500" frame, "quadcopter", and "four motors" with a BOM totaling ~565.
- The D6 body sections (`exec_summary.tex`, `intro_d6.tex`, `design_rationale.tex`, `system_description.tex`, `mission_flow.tex`, `evaluation.tex`) all describe a "Hexsoon EDU-450 hexacopter".
- These appear to be two different airframes described in two different report layers. The appendix (Section 3) appears to describe the original/early hardware spec, while the body reflects the actual university-provided EDU-450.
- **Action needed:** The user should decide whether `03_hardware_platform.tex` should be updated to match the EDU-450 description used everywhere else, or whether this section is intentionally describing a different build.

### 19. "Onboard computing cost under 100"
- Pi (60) + camera (45) = 105. Some places say "under 100" which is slightly optimistic. The abstract and conclusion both say "under 100" for the onboard compute. This is a borderline case -- if "onboard compute" means just the Pi (60), it's accurate. If it includes the camera, it's 105.

---

## Summary

| Category | Found | Fixed | Noted |
|----------|-------|-------|-------|
| Detection rate (30 vs 50) | 1 | 1 | -- |
| Inference time rounding | 1 | 1 | -- |
| Geofence layer count | 3 | 3 | 1 intentional |
| State count (19 vs 20) | 3 | 3 | -- |
| Cost figures | 2 | 2 | 1 borderline |
| Heartbeat timeout | 1 | 1 | -- |
| Airframe identity | 1 | 0 | needs human decision |
| **Total** | **12** | **11** | **2** |

All other checked metrics (mAP, CEP50, tilt correction, altitude, model name, requirement count, test count, confidence threshold, terminology) are consistent across all files.
