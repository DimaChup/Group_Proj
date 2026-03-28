# BRUTAL SCORE: Reportflow main.tex vs USER_VISION.md

**Date**: 2026-03-28
**Document**: `main.tex` (13 pages, compiled to PDF)
**Scored against**: `USER_VISION.md` (all requirements including Additional Requirements)

---

## Page-by-Page Visual Review

### Page 1
Title "SAR Drone Search Parameter Optimisation Decision Flow". Clean layout with blue headings. Sections 1 (Objective), 2 (Constraints), 3 (Five Competing Dimensions) all on page 1. Priority stack stated clearly: safety > detection > time > energy > coverage. Spider chart introduced as "the target shape". Good density, no wasted space.

### Page 2
Spider chart figure (Figure 1) rendered correctly -- shows the selected configuration profile with five axes, blue filled polygon vs theoretical best dashed outline. Table 1: decision variables and their affects. Section 5 "How They Interconnect" begins. Clean, readable.

### Page 3
Sensitivity matrix heatmap (Figure 2) -- red/green cells showing coupling between input variables and output metrics. Altitude and speed clearly dominate (darkest cells). Section 6 "The Decision Chain" begins with Phase A (Measure) vs Phase B (Optimise) split. Well explained.

### Page 4
Decision flow infographic (Figure 3) -- the nine-step sequential chain from model training through to final configuration. Green boxes for Phase A (measure), blue boxes for Phase B (optimise). Selected configuration box at bottom. Visually clear, follows the logic chain.

### Page 5
Steps 1-4 in detail. Step 1: train vision model. Step 2: detection ceiling with Table 2 (detection envelope across bright/overcast/dusk). Step 3: 15% safety margin calculation. Step 4: maximum speed with dwell time math and the v_max = 24m / (10/4.8) = 11.5 m/s formula. Dense but readable.

### Page 6
Table 3: speed envelope at 35m across lighting conditions with 15% margin applied. Step 5: search pattern type (4 patterns evaluated: lawnmower, spiral, expanding square, random walk). Step 6: fixed heading vs yaw-to-face with 3 cost factors and NFZ margin consequence. All well explained.

### Page 7
Step 6 continued (alternative considered: aligning camera diagonal to waypoint bearing). Step 7: energy-optimal scan angle with momentum theory hover power formula and quadratic parasitic drag. 216-configuration sweep described. Energy heatmap (Figure 4) showing the 65-75 degree valley. 70 degrees selected.

### Page 8
Step 8: NFZ safety margins with RSS calculation (camera footprint + GPS error + reaction distance + wind = ~19m, rounded to 30m with 1.5x factor). Step 9: swath overlap at 20%. Section 7: Decision Chain in Summary begins.

### Page 9
Altitude-speed tradeoff figure (Figure 5) -- colour-coded composite score with detection probability contours, coverage time contours, and selected point marked. Seven "because" statements summarizing the chain. Section 8: 216-configuration sweep details begin.

### Page 10
Table 4: top 3 configurations ranked by composite score. Configuration #1 (35m, 70deg, 8m/s) wins with 0.87 score. Figure 6: top 3 lawnmower paths overlaid on survey polygon with SSSI zone and buffer shown. Clear visual comparison.

### Page 11
Figure 7: six configurations compared on five objectives as spider/radar charts. Selected configuration (B, blue) has the most balanced polygon (balance score 0.538). Section 9: The Result with Table 5 (final operating configuration and predicted performance). Every parameter with value and rationale.

### Page 12
Section 10: Sensitivity and Robustness with tornado chart (Figure 8). Altitude dominates. Section 11: Pareto Optimality begins.

### Page 13
Parallel coordinates plot (Figure 9) -- all five objectives simultaneously, Pareto-optimal configurations in orange, selected in thick blue. Section 12: Non-Quantifiable Design Choices (speed adaptation to lighting, operator-in-the-loop, single-class detector). Document ends cleanly.

---

## Requirement-by-Requirement Scoring

| # | Requirement | Score (0-10) | Evidence | Fix needed? |
|---|-------------|:---:|----------|:-----------:|
| 1 | **THE GOAL: Find casualty ASAP** | **10** | Section 1, first sentence: "find the casualty as fast as possible" -- verbatim from vision. | No |
| 2 | **THE CONSTRAINTS listed** | **10** | Section 2: NFZ, flight area, altitude limit, single battery, one pass, hardware ceiling (4.8 FPS). All six constraints present and clearly stated. | No |
| 3 | **5 competing dimensions stated** | **10** | Section 3: Safety, Detection, Time, Energy, Coverage. Exact quote: "five competing performance dimensions that must be balanced." | No |
| 4 | **Priority ordering stated** | **10** | "safety > detection > time > energy > coverage" with justification for each level. Bold, clear, impossible to miss. | No |
| 5 | **Spider chart as TARGET shape** | **9** | Figure 1 introduced as "the target shape -- the optimisation that follows aims to produce a configuration whose profile fills this envelope." Nearly perfect. Minor: the spider shows the *selected* config's performance, not a pure aspirational target separate from the result. Still, the intent is conveyed. | Minor |
| 6 | **All variables listed** | **10** | Table 1: altitude, speed, search pattern type, scan angle, swath overlap, NFZ buffer, heading mode. Seven variables, all with ranges tested and what they affect. | No |
| 7 | **Interconnection / coupling shown** | **10** | Section 5 + Figure 2 (sensitivity matrix heatmap). "altitude-speed pair dominates, jointly determining four of the five objectives." Dense coupling explicitly stated. | No |
| 8 | **Max altitude for detection (measurable first)** | **10** | Step 2: detection ceiling with empirical data across 3 lighting conditions (Table 2). 63m bright, 52m overcast, 38m dusk. Clear "we can measure this ourselves" approach. | No |
| 9 | **15% safety margin (NOT 30%)** | **10** | Step 3: "We applied a 15% safety margin" -- explicit, correct, applied to both altitude (Step 3) and speed (Step 4, Table 3). Consistent throughout. | No |
| 10 | **Max speed at that altitude** | **10** | Step 4: dwell time physics, v_max formula, 14 frames at 8 m/s, cumulative detection probability >99.97%. Speed derived from altitude, not assumed. | No |
| 11 | **Speed varies with lighting** | **10** | Table 3: speed envelope across bright/overcast/dusk with 15% margin applied (10/8.5/6 m/s). Section 12 repeats: "In bright conditions the operator can increase speed to 10 m/s, and in poor lighting it should be reduced to 6 m/s." | No |
| 12 | **Search pattern as design variable** | **10** | Step 5: four pattern types evaluated (lawnmower, spiral, expanding square, random walk). Lawnmower selected with rationale (irregular polygon + NFZ). Spiral acknowledged as better for convex areas. | No |
| 13 | **Energy efficiency simulation (momentum theory, quadratic drag)** | **10** | Step 7: P_hover = sqrt((mg)^3 / (2*rho*A)), P_forward with quadratic parasitic drag. U-turn energy modelled. 216-config sweep with energy heatmap (Figure 4). | No |
| 14 | **216-config sweep** | **10** | Section 8: "216 configurations (6 altitudes x 36 scan angles)" with composite scoring (40% detection + 35% coverage + 25% energy). Table 4: top 3 ranked. | No |
| 15 | **NFZ margins calculated** | **10** | Step 8: camera footprint diagonal + GPS error + reaction distance + wind = RSS ~19m, 1.5x factor to 30m buffer. Layered protection with speed-ramp zone and 3m hard cutoff. | No |
| 16 | **Drone turning vs not turning tradeoff** | **10** | Step 6: fixed heading vs yaw-to-face. Three costs quantified (time, energy, NFZ margin geometry). Decision: no yaw, saves 15s and 3-5% energy. Alternative considered (diagonal alignment). | No |
| 17 | **Pattern alternatives mentioned** | **10** | Step 5: lawnmower, spiral inward, expanding square, random walk. Each described with pros/cons. | No |
| 18 | **THE RESULT: selected config with rationale** | **10** | Section 9: Table 5 with all 6 parameters + 4 performance metrics, each with rationale column. "Every parameter traces back to a physical measurement or regulatory constraint." | No |
| 19 | **Logic chain feels INEVITABLE** | **9** | Each step opens with "Why this comes first/after X" and closes with "what value we selected." The chain is: model -> altitude ceiling -> safety margin -> operating alt -> speed -> pattern -> heading -> scan angle -> NFZ -> overlap. Very strong. Minor: Step 1 (train model) feels slightly bolted on -- the chain *really* starts at Step 2. | Minor |
| 20 | **Start with measurable, then optimize** | **10** | Phase A (Steps 1-4): "Measure" -- empirical constraints. Phase B (Steps 5-9): "Optimise" -- physics-based simulation. Explicit split with labels. | No |
| 21 | **Every figure explained in text** | **9** | All 9 figures have surrounding text explaining what they show and why they matter. Figure 1 (spider), Figure 2 (sensitivity matrix), Figure 3 (decision flow), Figure 4 (energy heatmap), Figure 5 (alt-speed tradeoff), Figure 6 (top 3 paths), Figure 7 (objective conflict), Figure 8 (tornado), Figure 9 (parallel coordinates). Minor: Figure 7 caption could be more descriptive about *what* the balance score means. | Minor |
| 22 | **Every table referenced and explained** | **10** | All 5 tables are referenced in text before they appear and explained after. Table 1 (variables), Table 2 (detection envelope), Table 3 (speed envelope), Table 4 (top 3 configs), Table 5 (final config). | No |
| 23 | **Light conditions with plausible empirical results** | **9** | Table 2: detection ceiling vs lighting (63/52/38m). Table 3: speed vs lighting (12/10/7 m/s). Described as "derived from brightness-adjusted video replay with the retrained model." Plausible and internally consistent. Minor: no separate detection-performance-vs-lighting chart/figure was generated -- the data is in tables only, not a visual chart. Vision said "Generate charts showing detection performance vs lighting if helpful." | Minor |
| 24 | **Camera specs (global shutter, IMX296) justify bright=faster** | **7** | IMX296 mentioned once in Step 3 ("IMX296 sensor with calibrated focal length 5.46mm"). Global shutter is NOT mentioned. The bright=faster logic is explained via exposure time ("short exposure OK" in Table 3) but the connection to the IMX296's global shutter advantage is never made explicit. This was a specific ask. | Yes -- add 1-2 sentences in Step 4 explaining that the IMX296 global shutter eliminates rolling-shutter smear, which is why bright conditions allow faster speeds (shorter exposure, sharp frames). |
| 25 | **Flow: Objective -> Constraints -> 5 dims -> Variables -> Decision chain -> Result** | **10** | Sections follow this exact order: 1 Objective -> 2 Constraints -> 3 Five Dimensions -> 4 Variables -> 5 Interconnect -> 6 Decision Chain -> 7 Summary -> 8 Evaluation -> 9 Result -> 10 Sensitivity -> 11 Pareto -> 12 Qualitative. Perfect match. | No |

---

## Visual Quality Assessment

| Aspect | Score (0-10) | Notes |
|--------|:---:|-------|
| Typography & layout | **9** | Clean 10pt, blue headings, good density, 15mm margins. Tcolorbox decision chain summary. Professional. |
| Figure quality | **8** | All figures render correctly. Spider, heatmap, decision flow, tornado, parallel coords all clear. Some figures (spider, objective conflict) could be slightly larger for readability. |
| Table quality | **9** | All tables use booktabs, siunitx, clean formatting. Top 3 config table is excellent. |
| Information density | **9** | 13 pages, no filler, no padding. Every paragraph earns its space. Could arguably be tighter (the qualitative section at the end is a bit thin for a full section) but nothing is wasted. |
| Flow / readability | **9** | The "Why this comes first/after X" pattern at each step creates a strong narrative thread. Reader never wonders "why are we talking about this now?" |

---

## Summary

| Category | Score |
|----------|:-----:|
| Structure match to USER_VISION | 98% |
| Content completeness | 96% |
| Logic chain inevitability | 93% |
| Figure/table integration | 93% |
| Visual quality | 90% |
| **OVERALL** | **94/100** |

---

## What's Missing / Needs Fixing (3 items)

1. **IMX296 global shutter not mentioned** (Score impact: -3)
   - The vision specifically asks to justify bright=faster using camera specs (global shutter, IMX296).
   - Currently: IMX296 named once for focal length. "Global shutter" never appears.
   - Fix: Add 1-2 sentences in Step 4 explaining that the IMX296 global shutter eliminates rolling-shutter motion artifacts, which is why the detector tolerates higher speeds in bright conditions (shorter exposure = sharper frames, and global shutter means no row-by-row skew even during fast motion).

2. **No detection-vs-lighting chart** (Score impact: -1)
   - Vision said "Generate charts showing detection performance vs lighting if helpful."
   - Data exists in Tables 2 and 3 but no visual chart was created.
   - Optional fix: generate a simple bar chart or line plot showing confidence vs lighting condition, or detection ceiling vs lighting. Would strengthen the "we measured this" narrative.

3. **Spider chart framing** (Score impact: -1)
   - Vision: "Spider chart must be introduced as 'this is the shape our mission outcome should fit' -- the TARGET profile."
   - Current: introduced correctly as "the target shape" but the figure itself shows the *selected* configuration's performance, not a pure aspirational target. This is a very minor semantic distinction -- the text framing is correct even if the data is post-hoc.
   - No fix needed -- this is fine as-is.

---

## Verdict

This is a **94/100** document. The logic chain is tight, the structure matches the vision almost exactly, every figure and table is explained, the 15% margin is consistent, the Phase A/Phase B split works, and the 216-config sweep with physics-based energy model is properly presented. The only real gap is the missing global shutter mention -- a 2-sentence fix. Everything else is polished and publication-ready.
