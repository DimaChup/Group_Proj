# Evaluation: Reportflow vs USER_VISION.md

**Date**: 2026-03-28
**Document**: `report/reportflow/main.tex` (12 pages, compiled to main.pdf)

---

## Checklist: Every Vision Requirement

### 1. THE GOAL: Find the casualty as fast as possible
- **STATUS: PASS** -- Section 1 ("The Problem") opens with: "The mission is to locate a lost casualty as quickly as possible."

### 2. THE CONSTRAINTS: Hardware, regulatory, operational
- **STATUS: PASS** -- Section 1 explicitly lists: Hexsoon EDU-450, Pi 5, 4.8 FPS, R01-R04 flight area/SSSI/50m limit, single battery, one search pass.

### 3. 5 COMPETING DIMENSIONS (Coverage, Detection, Time, Energy, Safety)
- **STATUS: PASS** -- Section 1 bullet-lists all five and states "five competing dimensions that must be balanced." Priority stack stated: safety > detection > speed > energy.

### 4. ALL VARIABLES + INTERCONNECTION (coupling/sensitivity matrix)
- **STATUS: PASS** -- Section 2 (Table 1) lists all 6 variables with ranges and what each affects. Figure 2 shows the sensitivity matrix with darker cells = stronger influence. Text notes altitude-speed pair dominates.

### 5a. Max altitude for detection + 15% safety margin
- **STATUS: PASS** -- Step 2 (Section 3.2) finds detection ceiling per lighting condition (Table 2). Step 3 (Section 3.3) applies **15% safety margin** (not 30%). Calculation shown: 38m * 0.85 = 32m (dusk), 52m * 0.85 = 44m (overcast), selected 35m.

### 5b. Max speed at that altitude + 15% margin
- **STATUS: PASS** -- Step 4 (Section 3.4) derives speed from along-track footprint / (required frames / FPS) = 11.5 m/s. Table 3 shows speed envelope per lighting with "Chosen (15% margin)" column. Selected 8 m/s.

### 5c. Speed varies with lighting (table)
- **STATUS: PASS** -- Table 3 (Step 4) shows bright/overcast/dusk rows with max speed, limiting factor, and chosen speed. Section 9 (Non-Quantifiable) explicitly discusses adaptive speed policy: 10 m/s in bright, 8 m/s overcast (baseline), 6 m/s dusk.

### 5d. Once altitude/speed settled, decide search pattern
- **STATUS: PASS** -- Step 5 (Section 3.5) explicitly states "Why this comes after altitude and speed" and evaluates 4 pattern types (lawnmower, spiral, expanding square, random walk). Selects lawnmower with rationale.

### 5e. Energy efficiency simulation (momentum theory, drag, 216-config sweep)
- **STATUS: PASS** -- Step 7 (Section 3.7) details physics model: hover power from momentum theory, forward flight with quadratic parasitic drag. 216-configuration sweep (6 altitudes x 36 angles). Energy heatmap figure (Figure 3) included.

### 5f. NFZ margins (camera footprint + GPS error + reaction time)
- **STATUS: PASS** -- Step 8 (Section 3.8) shows RSS calculation: camera footprint half-diagonal 18m + GPS 3m + reaction 4m + wind 2m = 19m RSS. Selected 30m buffer (1.5x safety factor).

### 6. THE RESULT: Selected configuration with rationale
- **STATUS: PASS** -- Section 6 (Table 5) shows final config: 35m, 8 m/s, 70 deg, fixed heading, 20% overlap, 30m NFZ buffer. Performance: >99.97% detection, 96% coverage, 112s search, 12.6 Wh (10.9% battery).

---

## Critical Fix: 15% vs 30%

| Location | Before | After | Status |
|----------|--------|-------|--------|
| decision_flow.py line 89 | "Apply 30% safety margin" | "Apply 15% safety margin" | FIXED |
| decision_flow.pdf (Figure 1) | Shows "30%" | Shows "15%" | REGENERATED |
| main.tex body text | Already said 15% everywhere | No change needed | OK |

---

## Structural Fix: Measure-then-Optimise Transition

**Before**: Section 3 introduced the chain but did not explicitly distinguish measured vs optimised steps.

**After**: Added Phase A / Phase B framing:
- "Phase A (Steps 1-4): Measure" -- start with variables we can directly measure (detection ceiling, speed limits) and lock them with 15% margins
- "Phase B (Steps 5-9): Optimise" -- once altitude and speed are fixed, optimise remaining path parameters using energy simulation and 216-config sweep
- Chain box now shows [Measure] and [Optimise] labels with colour coding

---

## Flow Logic: Does Each Step Follow from the Previous?

| Step | Depends on | Why it must come here | Verdict |
|------|------------|----------------------|---------|
| 1. Train model | Nothing | Foundation -- all detection numbers depend on model quality | PASS |
| 2. Detection ceiling | Step 1 | Can only measure ceiling with a trained model | PASS |
| 3. Operating altitude | Step 2 | 15% margin below ceiling | PASS |
| 4. Max speed | Step 3 | Speed depends on footprint size, which depends on altitude | PASS |
| 5. Pattern type | Steps 3-4 | Pattern evaluation needs swath width + energy per metre | PASS |
| 6. Heading mode | Step 5 | Yaw vs fixed depends on pattern geometry | PASS |
| 7. Scan angle | Steps 5-6 | Energy sweep needs pattern type + heading mode as inputs | PASS |
| 8. NFZ margins | Steps 6-7 | Margin depends on footprint geometry (heading + angle) | PASS |
| 9. Overlap | Steps 3, 8 | Lane spacing depends on footprint + error budget | PASS |

**Verdict**: The chain is logically ordered. Each "Why this comes after..." paragraph makes the dependency explicit. The flow feels inevitable.

---

## Additional Figures and Sections Present

- Sensitivity matrix (Figure 2) -- variable coupling
- Energy heatmap (Figure 3) -- 216-config sweep results
- Altitude-speed tradeoff (Figure 4) -- composite score with detection contours
- Top 3 paths overlaid on polygon (Figure 5)
- Objective conflict radar charts (Figure 6) -- 6 configs on 5 dimensions
- Tornado sensitivity (Figure 7) -- parameter importance ranking
- Sensitivity spider (Figure 8) -- selected config performance profile
- Pareto parallel coordinates (Figure 9) -- Pareto frontier visualization
- Drone turning vs not turning (Step 6) -- explicit tradeoff with 3 cost categories
- Pattern alternatives (Step 5) -- 4 types evaluated

---

## Summary

All USER_VISION.md requirements are met. Two fixes applied:
1. **decision_flow.py**: "30%" changed to "15%", figure regenerated
2. **main.tex Section 3**: Added explicit Phase A (Measure) / Phase B (Optimise) framing to make the "start with measurable, then optimise" transition clear
