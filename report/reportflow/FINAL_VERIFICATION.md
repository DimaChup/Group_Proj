# FINAL VERIFICATION — reportflow/main.pdf (v11, 13 pages)

Compiled: 2026-03-28 | 13 pages, 1,012,900 bytes | No LaTeX errors

---

## Page-by-Page Description

**Page 1** — Title ("SAR Drone Search Parameter Optimisation Decision Flow"), Sec 1 Objective (one sentence: find casualty as fast as possible), Sec 2 Constraints (6 bullet points: SSSI NFZ, flight area, 50m altitude, single battery, one pass, hardware ceiling at 9 FPS NCNN / 4.8 FPS TFLite), Sec 3 Five Competing Dimensions (numbered: Safety, Detection, Time, Energy, Coverage), priority stack stated, spider chart introduced as "target shape".

**Page 2** — Spider chart (Figure 1: "Target performance profile"), Sec 4 Variables (7 variables in Table 1 with ranges and affected objectives), Sec 5 How They Interconnect (intro to sensitivity matrix).

**Page 3** — Sensitivity matrix heatmap (Figure 2), Sec 6 Decision Chain intro (Phase A Measure / Phase B Optimise, 15% margins stated).

**Page 4** — Decision flow infographic (Figure 3: 9-step sequential chain, colour-coded Phase A green / Phase B blue), chain summary box with [Measure] and [Optimise] labels.

**Page 5** — Step 1 (Train model, mAP50=0.995), Step 2 (Max altitude / detection ceiling), Table 2 (detection envelope: bright/overcast/dusk with max altitude, target width, confidence at 35m), Figure 4 (lighting performance: altitude vs lighting left panel, max detectable speed right panel with 15% margins).

**Page 6** — Step 3 (15% safety margin -> 35m operating altitude, IMX296 sensor mentioned with focal length 5.46mm, 1456x1088 resolution), Step 4 (max speed at 35m, physics equation v_max = 24m / (10/4.8) = 11.5 m/s), Table 3 (speed envelope: bright 12/10 m/s, overcast 10/8.5, dusk 7/6 with 15% margins), IMX296 global shutter paragraph explaining bright=faster, NCNN 9 FPS paragraph showing detection no longer bottleneck, 5 frames empirically justified.

**Page 7** — Step 5 (pattern type: 4 alternatives evaluated — lawnmower, spiral, expanding square, random walk; lawnmower chosen for deterministic coverage with NFZ), Step 6 (fixed heading vs yaw-to-face: 3 costs listed, no-yaw chosen for 15s + 3-5% energy saving, NFZ margin consequence explained), Step 7 intro (energy-optimal scan angle, momentum theory + quadratic drag physics model).

**Page 8** — Step 7 continued (216-config sweep: 6 altitudes x 36 angles), Figure 5 (energy heatmap with 65-75 deg valley, red star at minimum), Step 8 (NFZ safety margins: 4 error sources RSS'd to 19m, rounded to 30m buffer with 1.5x safety factor).

**Page 9** — Step 9 (swath overlap: 20%, covers 4.6m lane error with 2.2m spare), Sec 7 Decision Chain in Summary (altitude-speed trade-off Figure 6 with composite score colour map, detection contours, coverage contours, selected point marked).

**Page 10** — 7-point "because" chain summary, Sec 8 (216-Configuration Sweep details: composite score weights 40/35/25, Table 4 with top 3 configs, rationale for each), Figure 7 (top 3 lawnmower paths overlaid on survey polygon with NFZ).

**Page 11** — Figure 8 (6-config objective conflict: 6 spider charts comparing configurations, selected = most balanced polygon, balance score 0.536), Sec 9 The Result (Table 5: final configuration — all 11 parameters with values and rationale).

**Page 12** — Sec 10 Sensitivity and Robustness (Figure 9: tornado chart, altitude dominates), spider plot cross-reference, adaptivity statement, Sec 11 Pareto Optimality (text describing knee of Pareto frontier).

**Page 13** — Figure 10 (parallel coordinates: 216 configs, 7 Pareto-optimal orange, selected thick blue), Sec 12 Non-Quantifiable Design Choices (3 bullets: speed adaptation to lighting, operator-in-the-loop, single-class detector).

---

## Scoring Against All 20 Requirements

| # | Requirement | Status | Evidence |
|---|-------------|--------|----------|
| 1 | Objective: find casualty fastest — stated clearly? | PASS | Page 1, Sec 1: "find the casualty as fast as possible" — bold, one sentence, unmissable. |
| 2 | Constraints listed — NFZ, battery, altitude, etc.? | PASS | Page 1, Sec 2: 6 bullet points covering SSSI NFZ, flight area, 50m altitude, single battery, one pass, hardware ceiling. All hard constraints. |
| 3 | 5 dimensions clearly stated with priority stack? | PASS | Page 1, Sec 3: numbered list (Safety, Detection, Time, Energy, Coverage). Priority stack in bold: safety > detection > time > energy > coverage. Each dimension explained. |
| 4 | Spider chart introduced as "target shape"? | PASS | Page 1 bottom / Page 2 top: "This spider chart is the target shape — the optimisation that follows aims to produce a configuration whose profile fills this envelope." Figure 1 caption reinforces. |
| 5 | All 7 variables listed with coupling (sensitivity matrix)? | PASS | Page 2, Table 1: 7 variables (altitude, speed, pattern type, scan angle, overlap, NFZ buffer, heading mode) with ranges and affected objectives. Page 3, Figure 2: sensitivity matrix heatmap showing coupling. Text: "altitude-speed pair dominates, jointly determining four of the five objectives." |
| 6 | Phase A (Measure) / Phase B (Optimise) clear? | PASS | Page 3, Sec 6: "Phase A (Steps 1-4): Measure... empirical constraints, not design choices. Phase B (Steps 5-9): Optimise." Decision flow infographic (Figure 3, page 4) colour-codes the two phases. Chain summary box uses [Measure] and [Optimise] labels. |
| 7 | 15% safety margin EVERYWHERE (not 30%)? | PASS | Page 6: "15% safety margin below the worst-case ceiling" (Step 3). Table 3: "Chosen (15% margin)" column header. Figure 4 right panel shows 15% margins. The only "30%" in the document is the 30m NFZ buffer (a distance in metres, not a percentage margin) and "10-30%" swath overlap range. No 30% safety margin exists anywhere. |
| 8 | NCNN is DEFAULT at 9 FPS (not upgrade, not fragile)? | PASS | Page 1, Sec 2: "onboard inference runs at approximately 9 FPS with the deployed NCNN backend (YOLOv8n on Raspberry Pi 5), with TFLite at 4.8 FPS available as a fallback." NCNN is presented as the deployed default; TFLite is the fallback. Page 6: "The deployed NCNN backend achieves approximately 9 FPS in the full pipeline." |
| 9 | 5 frames empirically justified? | PASS | Page 6, Step 4: "requiring just 5 frames on target — empirically sufficient for reliable detection across lighting conditions" and "testing across bright, overcast, and dusk conditions showed that 5 independent observations at >=85% per-frame confidence consistently yielded >99% cumulative detection." |
| 10 | Detection NOT speed bottleneck at 9 FPS? | PASS | Page 6: "With the deployed backend, detection is no longer the speed-limiting factor; speed is instead constrained by energy budget, NFZ reaction time, GPS update rate, and wind tolerance." v_max = 24/(5/9) = 43 m/s shown — far above practical speed. |
| 11 | Speed varies with lighting — table + chart? | PASS | Table 3 (page 6): bright 12->10, overcast 10->8.5, dusk 7->6 m/s. Figure 4 right panel (page 5): chart showing max detectable speed vs lighting with 15% margins. Page 13, Sec 12 bullet 1: speed adaptation as deliberate design choice. |
| 12 | IMX296 global shutter mentioned for bright=faster? | PASS | Page 6, Step 4: "The IMX296 global shutter is critical here: unlike a rolling shutter that reads the sensor row-by-row (introducing motion smear proportional to flight speed), the global shutter captures the entire frame simultaneously, eliminating in-frame distortion regardless of speed. This is why bright conditions — where shorter exposure times further reduce motion blur — permit significantly higher flight speeds." |
| 13 | Drone turning vs not turning tradeoff? | PASS | Page 7, Step 6: full subsection "Fixed Heading vs. Yaw-to-Face" with 3 costs (time, energy, NFZ margin), quantified savings (15s, 3-5% energy), detection rate preserved (>92%), NFZ margin consequence explained. Alternative approach considered and rejected. |
| 14 | Energy simulation with physics (momentum theory)? | PASS | Page 7, Step 7: "Hover power from momentum theory: P_hover = sqrt((mg)^3 / (2*rho*A))" and "Forward flight power with quadratic parasitic drag: P_forward = P_hover + 1/2 * rho * C_D * A_front * v^3". U-turns modelled as decelerate-turn-reaccelerate with energy proportional to v^2. |
| 15 | 216-config sweep with results? | PASS | Page 8: "216 configurations (6 altitudes x 36 scan angles)" swept. Figure 5: energy heatmap. Page 10: Table 4 with top 3 configs and composite scores. Figure 7: top 3 paths overlaid. Page 11: Figure 8 with 6-config objective conflict spider charts. |
| 16 | Pattern alternatives (lawnmower, spiral, etc.)? | PASS | Page 7, Step 5: 4 alternatives evaluated (lawnmower, spiral inward, expanding square, random walk) with pros/cons for each. Decision justified: lawnmower for deterministic coverage guarantee with irregular polygon + NFZ. Spiral acknowledged as better for convex areas. |
| 17 | Every figure explained in surrounding text? | PASS | All 10 figures have surrounding text explaining what they show and why they matter: Fig 1 (spider target shape), Fig 2 (sensitivity coupling), Fig 3 (decision flow), Fig 4 (lighting performance), Fig 5 (energy heatmap), Fig 6 (alt-speed tradeoff), Fig 7 (top 3 paths), Fig 8 (objective conflict), Fig 9 (tornado), Fig 10 (parallel coordinates). No orphan figures. |
| 18 | Every table referenced? | PASS | All 5 tables are referenced in text: Table 1 (L129), Table 2 (L205), Table 3 (L256), Table 4 (L403), Table 5 (L441). Each has surrounding explanation. |
| 19 | Lighting condition charts included? | PASS | Figure 4 (page 5): two-panel chart showing (a) confidence vs altitude under 3 lighting conditions, (b) max detectable speed vs lighting with 15% margins. Table 2: detection envelope with max altitude per condition. Table 3: speed envelope per condition. |
| 20 | Flow: objective -> constraints -> dimensions -> variables -> chain -> result? | PASS | Exact section order: Sec 1 Objective -> Sec 2 Constraints -> Sec 3 Five Competing Dimensions -> Sec 4 Variables -> Sec 5 Coupling -> Sec 6 Decision Chain (9 steps) -> Sec 7 Summary -> Sec 8 Evaluation -> Sec 9 Result -> Sec 10 Sensitivity -> Sec 11 Pareto -> Sec 12 Qualitative. Flow is inevitable and sequential. |

---

## Additional Quality Observations

**Strengths:**
- The "because" chain in Sec 7 (page 10) is excellent — 7 linked statements where each follows from the previous
- The decision flow infographic (Figure 3) is a strong visual anchor for the entire document
- The 6-configuration spider comparison (Figure 8) makes Pareto optimality visually intuitive
- The parallel coordinates plot (Figure 10) is a sophisticated multi-objective visualisation
- Every numerical claim traces to a measurement, equation, or simulation
- Phase A/B split clearly separates empirical measurement from design optimisation
- The tornado chart (Figure 9) quantifies which parameters matter most — useful for robustness argument
- The footnote on detection probability (page 11) honestly acknowledges frame independence assumption

**Minor observations (non-blocking):**
- The document says "Three choices" in Sec 12 intro but lists 3 bullets — this is correct (earlier versions had a mismatch, now fixed)
- The 30m NFZ buffer (Step 8) uses a 1.5x safety factor, which is a distance multiplier not a percentage — correctly distinct from the 15% margin used for altitude and speed
- Speed equation on page 6 uses 4.8 FPS for the conservative case, then separately shows NCNN at 9 FPS — both are correct and well-distinguished

---

## FINAL SCORE: 95 / 100

**Breakdown:**
- Requirements compliance: 20/20 items PASS = 100%
- Document flow and logic: Excellent — inevitable sequential chain, no jumps
- Figures and tables: All 10 figures + 5 tables referenced, explained, and purposeful
- Technical depth: Strong — physics equations, empirical data, simulation results
- Visual quality: Strong — infographic, heatmaps, spider charts, tornado, parallel coordinates
- Writing clarity: Clear, concise, engineering voice throughout

**-5 points for:**
- The document is dense at 13 pages with narrow margins — some figures are slightly small (sensitivity matrix, spider charts in objective conflict) which may be hard to read when printed
- Step 4 (speed) is the longest subsection and could benefit from tighter editing — the TFLite and NCNN calculations are both shown in full, which creates some redundancy
- No references/citations section (acceptable if this is a self-contained appendix to a larger report)

**Verdict: READY FOR SUBMISSION.** All 20 user requirements are met. The document tells a complete, self-contained story from objective through constraints to optimised configuration with full traceability.
