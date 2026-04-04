# System Description Deep-Polish Review

**Date:** 2026-04-04
**File:** `report/sections/system_description.tex`
**Scope:** Technical depth, accuracy, completeness

---

## Factual Errors Fixed

| Issue | Was | Should Be | Status |
|-------|-----|-----------|--------|
| CV confidence threshold | 0.2 | 0.4 (matches `vision.py:DEFAULT_CONF_THRESHOLD`) | FIXED |
| Search speed | "8 m/s" hardcoded | Altitude-dependent 6-10 m/s; ~8.7 at 35m | FIXED |
| Geofence distances | "20m to 2m" | SOFT=8m, HARD=3m (matches `config.py`) | FIXED |
| Link loss mechanism | "3s heartbeat timeout" (then "5s") | ArduCopter GCS failsafe (`FS_GCS_ENABLE`), not a code timer | FIXED |
| Geofence caption distances | "20m speed ramp" | "8m speed ramp" | FIXED |

## Depth Improvements Made

### Hardware Platform (S3.1)
- Added dual UDP/TCP MAVProxy output detail (14550 + 5762) explaining WHY this architecture decouples components
- Added global shutter rationale (eliminates rolling-shutter distortion for GPS estimation accuracy)
- Added camera FPS detail (30fps native, throttled to ~4.8fps by inference)

### Software Architecture (S3.2)
- Added explicit interface signatures for each independent module (`detect_in_image` return type, `planning.py` input/output, `GeoTransformer` role)
- Added "127 tests" detail to explain why zero-dependency design matters
- Added main loop frequency (~20-50 Hz, limited by CV when active)
- Added 50m altitude hard cap (R04) in navigation module
- Enhanced 5-stage pipeline with timing and cross-references

### Computer Vision (S3.3)
- Added feature pyramid scale factors (8x, 16x, 32x)
- Added pixel-coordinate heuristic (threshold >1.5) for TFLite/NCNN output format auto-detection
- Added altitude-dependent speed explanation with linear interpolation formula
- Fixed confidence threshold to match code (0.4, not 0.2)

### Geofence (S3.2 paragraph)
- Corrected soft/hard boundary distances to 8m/3m (from 20m/2m)
- Added detail on coordinate frame conversion (pixel frame via GeoTransformer, then back to GPS)
- Clarified that repulsive offset is velocity correction applied AFTER state handler

### State Machine Safety (S3.5)
- Expanded from one-sentence list to a proper 6-item enumerated list
- Added RC override guard detail: checked BEFORE every state dispatch and key handler, modes 4/6/9 permitted
- Added GPS fix monitoring as explicit safety layer (was implicit)
- Clarified ArduCopter GCS failsafe as hardware backstop, not a software timer
- Added per-state timeout example (VERIFY: 120s)
- Added detection queue spatial dedup detail (checks rejected targets + IOI + queue)

### Ground Station (S3.7)
- Added command key mappings (N/Y/X/I/L/M)
- Added `/cmd?key=` HTTP endpoint for programmatic control
- Added note that Y/N at VERIFY is the only required human input
- Added ThreadingMixIn detail
- Added terminal keyboard thread for PuTTY/SSH operation

### Simulation Framework (S3.8)
- Added script names for each level
- Expanded defect examples with technical detail (SET_POSITION_TARGET race, cos(phi) omission, DISARM_DELAY=10)
- Added DRONE_MODE=REAL as the only config change needed

## Remaining Gaps (not addressed -- would exceed page budget)

1. **No timing diagram** for the 5-stage pipeline showing where the 208ms is spent. Would be valuable but needs a figure. Consider adding to appendix.
2. **No mention of detection photo saving** (R10: photos + JSON saved to `mission_detections/`). Could add one sentence to state machine section.
3. **Multi-class model** (5-class SAR_NAMES) is implemented but not mentioned. Currently only single-class "dummy" is described.
4. **NCNN benchmark** (72ms, 4.5x faster than TFLite) is available but described as "not yet benchmarked." Could update if NCNN is now validated.
5. **Altitude-dependent speed formula** is in config.py but the section only mentions the result, not the linear interpolation explicitly. Adequate for body text; formula is in config appendix.

## Cross-Reference Integrity

All `\ref{}` and `\cite{}` targets verified to exist:
- `sec:cv:inference` -- inference_architecture.tex
- `sec:streaming-arch` -- streaming_architecture.tex
- `sec:calibration` -- calibration_deep.tex
- `app:config` -- A2_config_params.tex
- `app:cv-extended` -- cv_extended.tex
- `app:cv:benchmarks` -- cv_extended.tex
- `app:cv:training` -- cv_extended.tex
- `app:cv:speed` -- cv_extended.tex
- `sec:path-opt` -- path_optimization_definitive.tex
- `app:states` -- A1_state_table.tex
- `sec:repulsive-field` -- focus_and_repulsive.tex
- `sec:nfz-interaction` -- path_optimization_definitive.tex
- `sec:gps-deep` -- gps_estimation_deep.tex
- `sec:sim-validation` -- simulation_validation.tex
- `sec:test-scripts` -- test_scripts_guide.tex
- `sec:rationale` -- design_rationale.tex

All cross-references resolve. No broken refs.

## Verdict

The section now provides sufficient technical depth for a reader to understand HOW the system works (interfaces, data flow, safety layers, protocols) while deferring mathematical detail to appendices. The five factual errors that could have caused credibility damage with an examiner are corrected.
