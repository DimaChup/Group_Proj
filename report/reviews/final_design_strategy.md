# Design Strategy Review: Parameter Derivation Chain

**File:** `report/sections/design_strategy.tex`
**Reviewed:** 2026-03-27

---

## Overall Verdict

The reasoning chain is strong. The dependency DAG is genuine -- each step does depend on prior outputs -- and the numerical calculations are correct. There are a few inconsistencies with config.py and some arguable logical steps that a reviewer could probe. Issues ranked by severity.

---

## NUMERICAL VERIFICATION

All core equations were recomputed from config.py values (`f=5.46mm`, `w_s=5.02mm`, `W=1456px`, `H=1088px`).

| Quantity | Paper value | Recomputed | Match? |
|----------|-------------|------------|--------|
| f_px | 1584 px | 1583.6 px | YES (rounded) |
| Sensor px at 20m | 143 | 142.5 | YES |
| Sensor px at 35m | 81 | 81.4 | YES |
| Sensor px at 50m | 57 | 57.0 | YES |
| Model px at 35m | 48 | 47.9 | YES |
| Model px at 85m | 20 | 20.0 | YES |
| H_g (along-track, 35m) | 24.1 m | 24.0 m | YES (rounding) |
| W_g (cross-track, 35m) | 32.2 m | 32.2 m | YES |
| v_max conservative | 11.5 m/s | 11.5 m/s | YES |
| n_f at 8 m/s | 14.5 -> 14 | 14.4 -> 14 | YES |
| RSS NFZ margin | 23.1 m | 23.0 m | YES (rounding) |
| Lane error RSS | 4.6 m | 4.6 m | YES |
| Overlap margin (20%) | 6.4 m | 6.4 m | YES |
| speed_for_altitude(35) | 8.0 m/s | 8.0 m/s | YES |

**All numbers check out.** Rounding differences are sub-1% and inconsequential.

---

## ISSUES FOUND

### 1. WIDTH COLUMN IN TABLE -- INCONSISTENT WITH RECOMPUTATION (MEDIUM)

**Line 37-41:** The "Width model (px)" column in Table 1 uses values 18, 10, 7, 6, 4 for altitudes 20, 35, 50, 60, 85m. Recomputing `0.5 * 1583.6 / h * 640/1088` gives 23, 13, 9, 8, 5.

These are significantly different. The paper values appear to use a different dummy width (perhaps 0.3m instead of 0.5m, which gives 14, 8, 6, 5, 3 -- still different). Or they may use a different formula.

**Impact:** The "10-pixel width comfort threshold" argument (line 48, 52) rests on these width values. If the true width at 35m is 13px (not 10px), the comfort threshold is passed at a higher altitude than claimed, which actually *helps* the argument (the margin is larger than stated). But the table numbers need to be correct.

**Fix:** Recompute the width column. At 35m, width = 13px model-input, not 10. At 50m, width = 9px, not 7. Update the comfort threshold discussion accordingly.

### 2. SEARCH_SPEED_MPS vs CLAIMED SPEED (LOW)

**Line 59 of config.py:** `SEARCH_SPEED_MPS = 10.0` (default search speed). The paper claims 8.0 m/s at 35m via the altitude-dependent schedule, and this is correct per `speed_for_altitude(35)`. However, a reviewer reading config.py would see `SEARCH_SPEED_MPS = 10` and wonder if the altitude-dependent schedule is actually used in the code, or if the flat 10 m/s default overrides it.

**Fix:** Add a brief note that the altitude-dependent speed schedule (lines 63-75 of config.py) is the operative speed source, not `SEARCH_SPEED_MPS`.

### 3. REACTION TIME IN NFZ RSS -- QUESTIONABLE INCLUSION (MEDIUM-HIGH)

**Line 132:** "Reaction time: at v = 8 m/s, a 2-second reaction window covers 16 m."

This term is problematic for two reasons:
- (a) The drone is autonomous -- there is no human reaction time. The "reaction" is software, which should be sub-second (one inference cycle = 208ms).
- (b) Adding 16m as an independent error source in an RSS calculation alongside 3m GPS error and 2m wind is questionable -- it dominates the RSS (16m vs 3m), making it essentially `sqrt(16.1^2 + 16^2) = 22.7m` with the other terms contributing almost nothing.

A reviewer would ask: "If the system is autonomous, why is there a 2-second reaction delay? And if there is, why RSS it instead of adding it linearly (it's not a random error, it's a deterministic delay)?"

**Fix options:**
- Justify the 2s delay (e.g., "detection-to-command latency including inference time, communication, and control loop settling") -- but even then, 2s is very conservative.
- Or reduce to a more defensible value (e.g., 0.5s = 4m, representing 2 inference cycles + control loop). This still gives RSS = 17.3m, and the 30m buffer still has 1.7x margin.
- Or separate deterministic delays (added linearly) from stochastic errors (RSS'd): margin = 16.1 (half-footprint) + 4m (braking distance) + RSS(3, 2) = 23.7m. This is more rigorous.

### 4. RSS vs LINEAR COMBINATION FOR NFZ MARGIN (LOW-MEDIUM)

**Line 138-139:** The RSS formula treats half-footprint (16.1m) as an "error source" alongside GPS error, reaction time, and wind. But half-footprint is not a random error -- it is a deterministic geometric offset. It should be added linearly, not RSS'd.

Proper formulation: `d_margin = 16.1 (half-footprint, deterministic) + RSS(3, wind, reaction)`.

If reaction = 4m (0.5s), wind = 2m, GPS = 3m: `d_margin = 16.1 + sqrt(9+4+16) = 16.1 + 5.4 = 21.5m`. The 30m buffer still provides 1.4x margin, so the conclusion holds. But the derivation as written is mathematically inconsistent.

### 5. "30% SAFETY MARGIN" CLAIM IN DEPENDENCY CHAIN (LOW)

**Line 212:** "a 30% safety margin yields h = 35m." This implies 35 = 50 * 0.70, which checks out arithmetically. But the body text (line 52) justifies 35m via the 1.4x width margin and 2.4x height margin -- there is no explicit "30% safety margin" calculation in the body. The dependency chain summary introduces a framing that wasn't established earlier.

**Fix:** Either add the 30% framing in the body text of Step 1, or rephrase the summary to match the actual justification (width/height margins).

### 6. ALONG-TRACK FOOTPRINT FORMULA (COSMETIC)

**Line 64:** The formula `H_g = (w_s * h / f) * (H_px / W_px)` is correct but non-obvious. The first term `w_s * h / f` gives the *cross-track* ground width (using sensor width). Multiplying by `H_px/W_px` converts to the along-track dimension using the pixel aspect ratio. This works because the sensor is rectangular with uniform pixel pitch.

A reviewer might find it clearer to see: `H_g = (sensor_height_mm * h) / f` where `sensor_height_mm = w_s * H_px/W_px = 5.02 * 1088/1456 = 3.75mm`. Both give 24.0m. Consider a one-line note explaining the ratio.

### 7. CUMULATIVE DETECTION PROBABILITY ASSUMES INDEPENDENCE (LOW)

**Line 92:** `P_d = 1 - (1-0.95)^14 > 0.9999` assumes independent per-frame detections. But the text itself (line 76-77) notes that consecutive frames are "highly correlated" -- the same target appears in similar positions with similar backgrounds. If the model fails to detect due to a systematic issue (e.g., the target blends with the background at that angle), it may fail on all 14 frames.

This is acknowledged implicitly by requiring 10 "raw" frames for 3-4 "substantially different views," but the probability calculation still uses all 14 as if independent.

**Fix:** Either compute over the 3-4 independent views (`P_d = 1 - (1-0.95)^4 = 0.99999375` -- still very high), or add a caveat noting the independence assumption.

### 8. STEP 6 IS NOT REALLY A STEP IN THE CHAIN (COSMETIC)

Step 6 ("Diagonal vs Aligned Scanning") is a rejected alternative, not a derived parameter. The dependency chain summary in Section 3.7 lists only 6 items and omits Step 6 entirely (the summary jumps from overlap to energy budget validation). The section title says "7-step reasoning chain" but there are really 5 derivation steps + 1 trade-off rejection + 1 validation. Consider relabeling Step 6 as a subsection of Step 3 (scan angle), since it's justifying the same decision.

---

## LOGICAL FLOW ASSESSMENT

The dependency chain is genuine and well-structured:

```
Target size (physical) --> Altitude (Step 1)
     |
     v
Altitude --> Footprint --> Speed (Step 2)
     |            |
     v            v
Altitude + Speed --> Scan Angle (Step 3)
     |
     v
Altitude --> Footprint --> NFZ Margin (Step 4)
     |
     v
Footprint + Errors --> Overlap (Step 5)
     |
     v
Energy budget validates all (Summary)
```

Each arrow represents a genuine dependency. No circular reasoning. The chain starts from physics (target size, sensor specs) and regulation (altitude ceiling), not from desired outcomes. This is exactly what a reviewer wants to see.

---

## WHAT A REVIEWER COULD POKE

1. **"Why not use a better camera/model to fly higher and save energy?"** The paper should briefly acknowledge this (it does in line 236 with "faster inference backend" but could mention sensor/model upgrades too).

2. **"Your p=0.95 per-frame detection rate -- where does this come from?"** Line 92 says "conservative for 48-pixel targets" but doesn't cite the model's actual measured detection rate at that pixel size. The mAP50=0.995 from training doesn't directly map to per-frame probability at 35m altitude in real conditions.

3. **"The RSS formulation mixes deterministic offsets with stochastic errors."** (Issue #4 above.) A controls/safety reviewer would flag this immediately.

4. **"You claim 96% coverage but don't quantify the detection probability in that 4% gap."** The justification that the gap is in a fenced wildlife reserve (line 154) is operational, not analytical.

---

## SUMMARY

| Category | Count |
|----------|-------|
| Calculation errors | 1 (width column in table) |
| Inconsistencies with config.py | 1 (minor -- search speed source) |
| Logical/methodological issues | 2 (RSS formulation, independence assumption) |
| Framing/cosmetic | 3 (30% margin sourcing, Step 6 labeling, formula clarity) |

**The chain is fundamentally sound.** The altitude, speed, scan angle, overlap, and NFZ margins all follow logically. The numbers are correct (except the width column). The main vulnerability is the NFZ RSS calculation mixing deterministic and stochastic terms -- this is the one thing a rigorous reviewer would challenge. Fix the width column and tighten the RSS formulation, and the section is very strong.
