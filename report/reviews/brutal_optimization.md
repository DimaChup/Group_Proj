# Brutal Optimization Cross-Review

**Files reviewed:**
1. `optimization_master.tex` (Section: Search Parameter Optimisation)
2. `optimization_formal.tex` (Section: Multi-Objective Search Optimisation)
3. `design_strategy.tex` (Section: Design Strategy: Parameter Derivation Chain)
4. `path_optimization_definitive.tex` (Section: Search Path Optimisation)
5. `search_optimization.tex` (subsection-level: Multi-Objective Search Optimisation)
6. `05_path_planning.tex` (Section: Search Pattern and Path Planning) -- also read for cross-reference

---

## SCORE: 38 / 100

The five files tell the SAME story FIVE TIMES with minor variations. The numbers are remarkably consistent (which is good), but the redundancy is catastrophic for a 15-page-limited report. A reader encountering all five would conclude the authors padded the report.

---

## 1. REDUNDANCY ANALYSIS (the biggest problem)

### Content that appears in ALL FIVE files:
- The 5-objective MOO problem statement (coverage, time, energy, detection, NFZ)
- The power model: P_hover=150W, P_drag_ref=50W, v_ref=5m/s
- The 216-configuration sweep (6 alt x 36 angles)
- The altitude-dependent speed schedule: v(h) = 6 + 4(h-20)/30
- Selected operating point: 35m, 70deg, 8m/s
- Energy at selected point: 12.6 Wh = 10.9% of battery
- Detection probability >99.97%
- Coverage = 96%
- NFZ buffer = 30m waypoint + 20m speed ramp + 3m hard boundary
- 20% overlap covers 4.6m RSS lane error
- Mannequin 1.8m tall, 0.5m wide
- Per-frame detection sigmoid with p_min=7px, kappa=0.5
- f_inf = 4.8 FPS
- 14 frames per flyover at 35m/8m/s
- P_d = 1-(1-p)^n_f
- U-turn penalty = 2s hover-only
- NFZ speed ramp: 3.0 to 0.3 m/s over 20m
- Battery: 6S 5200mAh = 115.4 Wh

**Verdict:** You have roughly 15 pages of optimization content across the 5 files, but it's really ~4 pages of unique material repeated with different framing. Only ONE of these files should exist in the final report.

### What each file uniquely contributes:
| File | Unique content |
|------|---------------|
| `optimization_master.tex` | Composite score weights (0.40/0.35/0.25), Pareto frontier figure, tornado sensitivity chart, N2 diagram, coupling matrix, top-3 table, alternative strategies (wind-aligned, adaptive speed, two-pass) |
| `optimization_formal.tex` | Formal MOO min/max statement (Eq 2), constraint table with binding status, objective conflict matrix figure, takeoff proximity constraint (R03) |
| `design_strategy.tex` | Step-by-step derivation chain (6 steps), dependency DAG, function chain diagram, diagonal vs aligned scanning analysis |
| `path_optimization_definitive.tex` | 6-strategy comparison table (boustrophedon vs spiral vs expanding square etc.), top-5/bottom-5 energy table, detection chain table (GSD to P_d), motion blur analysis, focus area redirect impact, NFZ energy vs altitude figure |
| `search_optimization.tex` | Rotation angle comparison table (0/45/70 deg), coverage 96% probabilistic argument, NFZ margin vs altitude table, speed vs detection table, focus area redirect |

---

## 2. NUMBER CONSISTENCY CHECK

### Consistent across all files (GOOD):
- P_hover = 150W -- all files agree
- P_drag_ref = 50W at v_ref = 5m/s -- all files agree
- Selected: 35m, 70deg, 8m/s -- all files agree
- Energy at selected point: 12.6 Wh -- all files agree
- Battery: 115.4 Wh (6S 5200mAh) -- all files agree
- 10.9% of battery -- all files agree
- Footprint Wg = 32.2m at 35m -- all files agree
- Along-track Hg = 24.0-24.1m at 35m -- consistent (rounding)
- f_px = 1584 px -- all files agree
- 14 frames at 35m/8m/s -- all files agree
- P_d > 0.9997 at 35m/8m/s -- all files agree
- NFZ buffer layers: 30m/20m/3m -- all files agree
- 20% overlap = 6.4m margin -- all files agree
- RSS lane error = 4.6m -- all files agree
- U-turn penalty = 2s -- all files agree
- Optimal energy (50m/70deg): 8.2 Wh -- all files agree
- 4.8 FPS inference rate -- all files agree

### INCONSISTENCIES FOUND:

#### 1. Number of scan lines at 70deg/35m
- `optimization_master.tex` line 172: "minimising scan lines from 10 (at 0deg) to 6"
- `search_optimization.tex` line 82: "5 passes, 4 U-turns" at 70deg
- `path_optimization_definitive.tex` line 103: "minimises the number of scan lines from 10 to 6"
- **Conflict:** optimization_master and path_optimization say 6 lines, search_optimization says 5 passes/4 turns.
- The top-5 table in path_optimization_definitive says rank 5 (35m/70deg) has 6 turns, not 4.
- search_optimization rotation table says 70deg has 5 passes and 4 U-turns (which would be 5 lines).
- **WHICH IS IT? 5 or 6 scan lines? 4 or 5 U-turns?**
- optimization_master line 119 table says 6 U-turns... wait, no: "#1: 35m, 70deg" doesn't list turns.
- path_optimization_definitive top-5 table says rank 5 (70/35) has **6 turns** (not lines).
- But search_optimization says 70deg at 35m has **5 passes, 4 U-turns**.
- **This is a real inconsistency.** If 5 passes then 4 U-turns; if 6 lines then 5 U-turns. The tables disagree.

#### 2. Number of U-turns at N-S (0deg)
- `search_optimization.tex` line 80: 0deg has "9 passes, 8 U-turns"
- `path_optimization_definitive.tex` line 121: 0deg/20m has "16 turns"
- These aren't directly comparable (different altitudes: 35m vs 20m), but could confuse a reader.

#### 3. Total in-flight power
- All files say P(8m/s) = 150 + 50*(8/5)^2 = 150 + 128 = 278W -- consistent.
- `search_optimization.tex` line 31 says "approximately 350W at 10m/s" -- let's check: 150 + 50*(10/5)^2 = 150 + 200 = 350W. Correct.

#### 4. Worst-case energy at 0deg
- `design_strategy.tex` line 107: "At the worst angle (95deg): E = 25.4 Wh" (at 35m)
- `search_optimization.tex` line 80: 0deg at 35m: "25.9 Wh"
- `path_optimization_definitive.tex` line 125: 95deg/20m: "43.2 Wh" (different altitude)
- So at 35m the worst angle is either 95deg (25.4 Wh) or 0deg (25.9 Wh)? These are close but not identical. Which is worst?

#### 5. Ideal mission time in Pareto table
- `path_optimization_definitive.tex` line 332: "Ideal: 68s"
- `search_optimization.tex` line 240: "Ideal: 59s"
- **These disagree.** 68s matches the 50m/70deg config from the top-5 table. Where does 59s come from? It doesn't match any configuration in any table.

#### 6. Survey area size
- `path_optimization_definitive.tex` line 175: "32,200 m^2"
- `optimization_formal.tex` line 70: "32,200 m^2"
- `search_optimization.tex` line 216: "1.8 hectare" for full survey, "0.15 hectare" for focus
- `path_optimization_definitive.tex` line 216: "3.2 hectare"
- **32,200 m^2 = 3.22 hectare.** But search_optimization says 1.8 hectare. **These are different numbers.** 3.2 ha vs 1.8 ha is nearly a 2x discrepancy. One of them is wrong.

#### 7. Top-3 table: #2 configuration
- `optimization_master.tex` line 120: "#2: 30m, 65deg, 7.3 m/s, Pd=0.9999, C=0.96, E=14.8 Wh"
- `search_optimization.tex` top-5 table line 44: "#2: 70deg, 45m, 10m/s, E=9.0 Wh"
- These are ranking by DIFFERENT criteria (composite score vs energy). Not technically inconsistent, but confusing for the reader.

#### 8. Per-frame detection probability p
- `optimization_master.tex` line 160: "p = 0.95"
- `design_strategy.tex` line 92: "p = 0.95 (conservative for 48-pixel targets)"
- Wait -- at 35m the model-input height is 36px not 48px. Where does 48px come from?
- Actually design_strategy says 36px model-input for 35m (Table on line 38). The "48-pixel" claim is wrong or refers to a different measure.

#### 9. Safety factor on NFZ
- `optimization_formal.tex` line 142: "safety factor of 30/16.1 = 1.86"
- `optimization_master.tex` line 250: "d_nfz = 30m provides a 2.2x safety factor over the RSS margin requirement"
- `design_strategy.tex` line 150: "Combined margin of 50m exceeds RSS requirement of 23m by factor 2.2x"
- These are measuring different things: 1.86 = buffer/footprint-half, 2.2 = total-margin/RSS. Both correct, but could confuse.

#### 10. search_optimization energy table inconsistency
- Line 43: Rank 2 is "70deg, 45m" but the altitude set is {20,25,30,35,40,50} -- there is no 45m in the sweep! This is a fabricated data point.
- Line 46: Rank 3 is "70deg, 50m" with 4 turns, 59s, 8.4 Wh -- but rank 1 is also 70deg/50m with 4 turns, 68s, 8.2 Wh. How can the same configuration appear twice with different values?
- Line 53: Rank 214 is "0deg, 20m" with 16 turns, 318s, 35.5 Wh -- but rank 212 is also 0deg/20m with 16 turns, 380s, 39.7 Wh. Same config, different numbers.
- **search_optimization.tex has fabricated/inconsistent table entries.** This is a serious data integrity issue.

---

## 3. CONTRADICTIONS

| # | Issue | Files | Severity |
|---|-------|-------|----------|
| 1 | 5 vs 6 scan lines at 35m/70deg | search_opt vs all others | HIGH |
| 2 | Ideal mission time 59s vs 68s | search_opt vs path_opt_def | HIGH |
| 3 | Survey area 1.8 ha vs 3.2 ha (32,200 m^2) | search_opt vs path_opt_def/formal | CRITICAL |
| 4 | search_optimization energy table has impossible entries (45m altitude, duplicate configs with different values) | search_opt internal | CRITICAL |
| 5 | "48-pixel targets" claim for p=0.95 at 35m when table says 36px | design_strategy | MEDIUM |
| 6 | Worst angle energy: 25.4 vs 25.9 Wh at 35m | design_strategy vs search_opt | LOW |

---

## 4. FIGURE/TABLE DUPLICATION

### Figures referenced from multiple files (will cause LaTeX label conflicts):
- `n2_diagram` -- optimization_master AND optimization_formal (CONFLICT: same label, two sections)
- `sensitivity_matrix` -- optimization_master AND design_strategy (CONFLICT)
- `sensitivity_spider` -- optimization_master AND design_strategy (CONFLICT)
- `coupling_matrix` -- optimization_master AND design_strategy (CONFLICT)
- `altitude_speed_tradeoff` -- optimization_master (fig:alt-speed-body) AND design_strategy (fig:alt-speed-tradeoff) -- different labels, same image
- `tornado_sensitivity` -- optimization_master AND design_strategy (CONFLICT)
- `real_energy_heatmap` -- optimization_master (fig:energy-heatmap) AND path_optimization_definitive (fig:energy-heatmap) -- same label, will conflict
- `top3_paths` -- optimization_master AND path_optimization_definitive (CONFLICT)
- `pareto_2d_composite` -- optimization_master AND path_optimization_definitive (CONFLICT)
- `energy_efficiency` -- optimization_master AND search_optimization (different labels, same image)

**If more than one of these files is included, LaTeX will throw duplicate label errors everywhere.**

---

## 5. STORY COHERENCE

The narrative is actually coherent -- it's just told 5 times:

1. **optimization_master.tex** -- the most complete single telling. Has the sweep, top-3, sensitivity, coupling, Pareto, and alternatives. Self-contained.
2. **optimization_formal.tex** -- the most mathematically rigorous. Formal MOO notation, constraint table, solution approach justification. Overlaps ~80% with optimization_master.
3. **design_strategy.tex** -- reframes as a step-by-step derivation chain. Good unique framing but ~70% content overlap.
4. **path_optimization_definitive.tex** -- the longest file. Tries to be comprehensive: adds strategy comparison, detection chain, motion blur, focus area. ~60% overlap with optimization_master, ~50% with search_optimization.
5. **search_optimization.tex** -- subsection-level version. Overlap: ~90% with path_optimization_definitive. Has the worst data integrity (fabricated table entries).

### Recommendation for which to keep:
**Keep optimization_master.tex as the primary section.** It is the most concise, has the best structure (problem -> physics -> sweep -> top-3 -> sensitivity -> coupling -> Pareto -> summary), and the cleanest data.

**Merge in** from the other files:
- From path_optimization_definitive: the 6-strategy comparison table (unique, valuable)
- From design_strategy: the 6-step dependency chain narrative (unique framing)
- From optimization_formal: the constraint binding-status table (unique, concise)

**Delete entirely:**
- search_optimization.tex -- it's a strict subset of path_optimization_definitive with data errors
- optimization_formal.tex -- merge the constraint table into optimization_master, discard the rest

---

## 6. EQUATION LABEL CONFLICTS

If multiple files are compiled together:
- `eq:opt-decision` vs `eq:decision-vector` -- same equation, different labels
- `eq:opt-power` vs `eq:power` vs `eq:power-model` -- same equation, 3 labels
- `eq:opt-energy` vs `eq:energy` vs `eq:total-energy` -- same equation, 3 labels
- `eq:opt-modelpx` vs `eq:target-px` vs `eq:model-px` -- same equation, 3 labels
- `eq:opt-psingle` vs `eq:p-single` -- same equation, 2 labels
- `eq:opt-pdetect` vs `eq:p-detect` vs `eq:pdetect` vs `eq:detect-prob` -- same equation, 4 labels
- `eq:lane-spacing` vs `eq:lane-width` -- same equation, 2 labels
- `eq:speed-ramp-obj` vs `eq:speed-ramp` -- same equation, 2 labels

---

## 7. NUMBERS THAT ARE CORRECT AND CONSISTENT

To be fair, the core physics is solid and internally consistent:
- Footprint geometry: Wg = ws*h/f = 5.02*35/5.46 = 32.2m (correct everywhere)
- Along-track: Hg = 5.02*35/5.46 * 1088/1456 = 24.0m (correct, minor rounding to 24.1)
- f_px = 5.46/5.02 * 1456 = 1584 px (correct)
- Model-input pixels at 35m: 1.8*1584/35 * 640/1456 = 35.8 -> 36 px height (correct)
- Width at 35m: 0.5*1584/35 * 640/1456 = 9.95 -> 10 px (correct)
- Power at 8m/s: 150 + 50*(8/5)^2 = 278W (correct)
- Energy 12.6 Wh / 115.4 Wh = 10.9% (correct)
- Overlap margin: 0.20 * 32.2 = 6.44m (correct)
- RSS lane error: sqrt(3^2 + 1.5^2 + 3.1^2) = 4.63m (correct)
- NFZ safety: footprint half = 16.1m (correct)

---

## SUMMARY

| Category | Score |
|----------|-------|
| Number accuracy (within each file) | 85/100 |
| Cross-file consistency | 55/100 |
| Redundancy (lower = more redundant) | 15/100 |
| Data integrity (search_optimization tables) | 30/100 |
| Story coherence | 75/100 |
| Figure/label management | 20/100 |
| **OVERALL** | **38/100** |

### Critical actions needed:
1. **Choose ONE file** (optimization_master.tex recommended) and delete/archive the other four
2. **Fix the survey area**: is it 1.8 ha or 3.2 ha? Verify against KML
3. **Fix scan line count**: 5 or 6 at 35m/70deg? Run the actual script
4. **Fix ideal mission time**: 59s or 68s? Check the sweep output
5. **Delete search_optimization.tex** immediately -- it has fabricated table entries
6. **Resolve all duplicate figure/equation labels** before compilation
