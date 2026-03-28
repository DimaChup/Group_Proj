# Reportflow PDF — Page-by-Page Review

9 pages total. Rendered at 150 DPI to `pages/page_1.png` through `pages/page_9.png`.

---

## Page 1 — Title Page

**What it shows:** Title "SAR Drone Search Parameter Optimisation Decision Flow", subtitle "AENGM0074 Group Design Project", "University of Bristol -- 2025-26". Horizontal rule below. Rest of page is blank.

**Verdict:** Clean and minimal. The title communicates the subject clearly — this is about parameter optimisation, not the full system. The massive blank space below the title feels wasteful but is standard LaTeX article class behaviour. No abstract, no author names, no date beyond the academic year. Acceptable for a supplementary/appendix document but would feel incomplete as a standalone report.

---

## Page 2 — Mission Objective + The Problem (Section 1)

**What it shows:**
- Header: "Mission Objective: Find the Casualty Fastest"
- A green-themed decision flow infographic (Figure 1) with 5 numbered steps:
  1. Max detection altitude (~63 m, 20 px minimum target)
  2. Apply 30% safety margin (~35 m operating altitude)
  3. Max speed for 10+ frames (~8 m/s, altitude-dependent)
  4. Energy-optimal scan angle (~70 deg, longest edge, 4 turns)
  5. NFZ margin (footprint + GPS) (~30 m buffer, 96% coverage)
- Bottom box: "Selected Configuration" — 35 m, 8 m/s, 70 deg, 20% overlap, 12.6 Wh, 112 s, 93% coverage probability
- Colour-coded legend: Safety (green), Detection (blue), Secondary (grey)
- Section 1 "The Problem" begins: hiker missing, one battery, one camera, 20 minutes, 3.2-hectare field bordered by SSSI no-fly zone. Five competing objectives listed.

**Does the mission come through?** YES — immediately and powerfully. The infographic is the strongest element in the entire document. The sequential chain (altitude drives speed drives angle drives NFZ drives overlap) is visually obvious. The green-to-blue colour coding separates safety constraints from detection objectives. The "Selected Configuration" box at the bottom gives the punchline before the reader even starts reading prose.

**Does constraints come through?** YES — the SSSI no-fly zone, single battery, 20-minute window, and detection minimum (20 px) are all stated clearly both in the infographic and the opening paragraph.

**Optimisation dimensions?** Partially. The infographic shows 5 parameters but Section 1 text mentions "five things compete" — coverage, detection, time, energy, safety. The mapping from objectives to parameters is not yet explicit on this page; it comes on page 3.

**Issues:**
- The infographic text is quite small at this rendering — "12.6 Wh | 112 s | 93% coverage probability" is borderline readable
- "20 px minimum target" in step 1 is a critical assumption but is not justified on this page (justified later in Section 8)
- The transition from infographic to prose is slightly abrupt — the figure caption is brief

---

## Page 3 — Variables, Sensitivity Matrix, Strategy (Sections 2-3)

**What it shows:**
- Section 2 "The Variables We Control" — five parameters in Table 1: altitude (20-50 m), speed (0-18 m/s), scan angle (0-175 deg), swath overlap (10-30%), NFZ buffer (10-50 m)
- Figure 2: Sensitivity matrix heatmap — input variables vs performance metrics. Darker cells = stronger influence. Altitude-speed pair dominates detection, coverage, time, and energy.
- Section 3 "Our Strategy: Safety-First, Detection-Optimised" — sequential chain: target size -> altitude -> speed -> scan angle -> NFZ margin -> overlap. References Section 4 for experimental data.
- Clear priority stack stated: safety > detection > speed > energy

**Verdict:** This page nails the optimisation dimensions. Table 1 is clean and compact. The sensitivity matrix (Figure 2) is genuinely useful — it shows at a glance that altitude and speed dominate everything, while scan angle and overlap are secondary. The priority stack (safety > detection > speed > energy) makes the decision logic transparent.

**Issues:**
- The sensitivity matrix colour scale lacks a quantitative legend — it says "darker = stronger" but there are no numerical sensitivity values. This is fine for intuition but a reviewer might want to know how these were computed.
- "Range tested" column in Table 1 is helpful but scan angle "0-175 deg" is a strange range — 0 deg scan angle has no physical meaning. Maybe "15-175 deg"?

---

## Page 4 — Altitude-Speed Trade-off + Energy Heatmap (Figures 3-4)

**What it shows:**
- Figure 3: Altitude-speed trade-off contour plot. X-axis = altitude (20-50 m), Y-axis = ground speed (6-14 m/s). Colour = composite mission score (40% detection + 35% coverage + 25% energy). Blue contours = detection probability. Orange contours = coverage time. Selected point marked at (35 m, 8 m/s) in the high-score region above the 95% detection contour.
- Figure 4: Energy heatmap across 216 altitude-angle configurations. X-axis = scan angle (0-360 deg), Y-axis = altitude (20-50 m). Colour = energy (darker = less = better). Clear low-energy valley at 45-75 deg at all altitudes. Red star at global minimum (30 m, 70 deg). Selected point (35 m, 70 deg) marked nearby.

**Verdict:** These are the two strongest figures in the document. The altitude-speed contour plot is publication-quality — the composite score surface, overlaid detection/coverage contours, and marked operating point tell a complete story in one image. The reader can see that the selected point (35 m, 8 m/s) sits in a "sweet spot" above 95% detection, in the high-composite region, without being at the extreme of any axis.

The energy heatmap shows the scan angle decision is not arbitrary — 70 deg aligns with a clear energy valley (longest-edge alignment minimises turns). The red star vs selected point offset shows altitude was chosen for detection, not energy.

**Issues:**
- Figure 3 colour bar label "Composite score (detection + coverage + energy)" is partially cut off at the right edge
- Figure 4 x-axis goes to 360 deg but the energy landscape repeats at 180 deg (symmetric for back-and-forth lawnmower). Worth noting or cropping to 0-180.
- Both figures are slightly small — the contour labels and axis text are hard to read at this DPI. In the actual PDF at 100% zoom they may be fine.

---

## Pages 5-9 — Quick Summary

**Page 5 (Section 4 "What We Evaluated"):** 216-configuration sweep results. Table 2 shows top 3 configs ranked by composite score. Three lawnmower pattern overlays on the survey polygon (Figure 5) visualise the differences. Config #1 (35 m, 70 deg, 8 m/s) wins as best compromise.

**Page 6 (Section 5 "The Result" + radar charts):** Six radar charts (Figure 6) comparing configurations across 5 objectives (coverage, detection, safety, energy, time). Selected config (B, blue) has the roundest/most balanced profile. Table 3 gives final parameter values with rationale for each.

**Page 7 (Sections 6-7 "Sensitivity and Robustness" + "Pareto Optimality"):** Tornado diagram (Figure 7) shows altitude dominates sensitivity. Spider/radar plot (Figure 8) shows selected config performance vs theoretical best. Pareto optimality argument begins.

**Page 8 (Pareto continued + Section 8 "Sequential Measurement Chain"):** Parallel coordinates plot (Figure 9) — 216 configs, 7 Pareto-optimal highlighted, selected config marked. Section 8 describes the sequential measurement chain: train model -> map detection envelope -> determine speed limits -> energy-efficient path search. Table 4: detection altitude under different lighting.

**Page 9 (Section 8 continued + Section 9 "Non-Quantifiable Design Choices"):** Speed limits at 35 m under different lighting (Table 5). Section 9 covers three qualitative decisions: lawnmower vs spiral, operator-in-the-loop verification, single-class detector. Document ends here — no references section, no appendix.

---

## Overall Assessment: Do Pages 1-4 Set Up the Story?

**Mission:** Crystal clear. The reader knows within 10 seconds of page 2 what the drone does, what it is optimising, and what the constraints are.

**Constraints:** Well communicated. Battery, time, SSSI no-fly zone, and detection physics (20 px minimum) are all stated early.

**Optimisation dimensions:** Come through strongly by page 3. The five variables, their ranges, and the sensitivity matrix make the design space tangible. The priority stack (safety > detection > speed > energy) gives the reader a mental framework for every decision that follows.

**What works well:**
- The Figure 1 decision flow infographic is excellent — it tells the entire story before the reader hits any prose
- The altitude-speed contour plot (Figure 3) is the standout figure — genuinely informative and well-designed
- The sequential chain logic is convincing: each parameter is locked before the next is explored
- Clean LaTeX formatting, good figure quality, appropriate use of colour

**What could be improved:**
- Page 1 is entirely wasted space — consider adding an abstract or executive summary, or start the content on page 1
- Some figure text is small (colour bar labels, contour values) — test readability when printed on A4
- The sensitivity matrix (Figure 2) lacks quantitative backing — how were the sensitivities computed?
- Scan angle range "0-175 deg" in Table 1 needs clarification (0 deg is undefined)
- No references section — the 20 px detection threshold, 30% safety margin, and detection probability model all need citations or justification
- The document ends abruptly after Section 9 with no conclusion or summary
