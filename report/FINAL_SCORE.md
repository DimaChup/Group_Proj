# D6 Company Report -- Final Quality Score

**Date:** 2026-03-27
**Assessed against:** AENGM0074 D6 rubric (Level 7), Release 2.1

---

## Overall Score: 74 / 100

**Band: First Class (72-78 range)**

The report is a solid first-class submission. It demonstrates strong technical depth, clear evidence-based decision making, and professional communication. However, three specific weaknesses prevent it from reaching the top band (83-100).

---

## Criterion Breakdown

| Criterion | Weight | Score | Notes |
|-----------|--------|-------|-------|
| **Specialist Skills & Problem-Solving** | 40% | 76 | Comprehensive system built with initiative and autonomy. Dual-backend CV, progressive testing, modular architecture all show creativity. Weakened by lack of outdoor flight data -- the core deliverable (a flying SAR drone) was never demonstrated in the air. |
| **Decision Making** | 40% | 75 | Excellent use of MCDA trade studies (4 tables), STEEPLE analysis is thorough and specific (not generic). Evidence-based throughout. Slightly weakened by some decisions that feel post-hoc justified rather than genuinely evaluated (e.g., Pi 5 was provided hardware, not truly "selected"). |
| **Communication** | 20% | 70 | Well-structured, professional, good use of tables and equations. However: all figures are placeholder boxes (no actual images, diagrams, or screenshots), which significantly undermines visual communication for a robotics project. |

**Weighted total: 0.40(76) + 0.40(75) + 0.20(70) = 30.4 + 30.0 + 14.0 = 74.4 -> 74**

---

## Strengths

1. **STEEPLE analysis is specific and grounded.** Each dimension references the actual system (SSSI geofence for Environmental, PLB for Social, cost comparison to DJI Matrice for Economic). Not generic boilerplate.

2. **Requirements verification is thorough.** All 12 requirements mapped with method, evidence, and status. Subsections expand on each with concrete technical detail (GPS coordinates, config parameters, MAVLink commands).

3. **Honest evaluation.** The plus/delta table is genuinely self-critical (D1: no outdoor flight, D6: payload not software-integrated). This shows maturity and is what the rubric rewards under "adapting to challenging circumstances."

4. **Trade studies are well-structured.** Four MCDA tables with explicit weights and scoring -- companion computer, communication architecture, detection model, search pattern. This is strong evidence-based decision making.

5. **Technical depth is high.** Equations for coverage (footprint, lane width, Bezier smoothing), pinhole camera model for GPS estimation, Kalman filter for target localisation, energy analysis with 216-configuration sweep.

---

## Three Fixes to Push the Score Higher

### Fix 1: Replace ALL placeholder figures with real images (Impact: +5 to +8 marks)

**Problem:** Every figure in the report is a `\fbox{\parbox{...}}` placeholder with descriptive text instead of an actual image. The state machine diagram (Figure 2), the architecture diagram (Figure 1), and the lawnmower pattern (Figure 3 in the path planning section, which is not even included in the compiled report) are all missing. For a robotics project, this is a major communication failure.

**What to include:**
- State machine diagram (draw in draw.io or TikZ -- you have the 20 states and 32 transitions fully defined)
- Module dependency graph (4-layer architecture diagram)
- Photo of the assembled drone with Pi, camera, and Cube visible
- Screenshot of the ground station dashboard (browser at port 8090)
- Lawnmower pattern over the actual survey polygon (you have `dry_run_pattern.jpg`)
- At least one detection screenshot from bench testing or video analysis

**Why it matters:** The rubric's Communication criterion (20%) explicitly calls for "innovative techniques and resources." Placeholder boxes are the opposite of that. Real figures would also boost Specialist Skills by showing the system actually exists.

### Fix 2: Add the path planning section to the compiled report (Impact: +2 to +4 marks)

**Problem:** The file `05_path_planning.tex` (188 lines, ~4 pages of strong content including the rotated-mask algorithm, energy analysis, Bezier smoothing, and 216-configuration parametric sweep) is NOT included in `main.tex`. The system_description.tex covers path planning in a brief subsection (~15 lines), losing all the depth. This is some of the report's best technical content and it is invisible in the compiled PDF.

**Fix:** Either:
- (a) Add `\input{sections/05_path_planning}` to main.tex between system_description and requirements_verification (check page count -- you have ~15 pages budget), or
- (b) Merge the key content (algorithm steps, equations, energy analysis table, comparison table) into the system_description path planning subsection.

**Why it matters:** The 216-configuration sweep, Bezier smoothing equations, and energy model are strong "initiative and creativity" evidence for Specialist Skills (40%). Without them, the report undersells the path planning work.

### Fix 3: Reframe the "no flight" limitation as adaptation, not just a delta (Impact: +2 to +3 marks)

**Problem:** The evaluation honestly states "no outdoor flight completed" as delta D1, but does not sufficiently frame the response to this setback as evidence of decision-making under adverse circumstances -- which is exactly what the rubric's top band rewards ("confidence and creativity in adapting to changing and unfamiliar/challenging circumstances").

**Fix:** Add a short paragraph (4-5 sentences) in the Evaluation discussion that explicitly frames the team's response:
- Weather cancelled the flight -> team pivoted to DJI video analysis as a proxy for real flight data
- Progressive testing framework was designed precisely for this scenario (each tier builds confidence independently)
- Bench integration verified all subsystems simultaneously on the real airframe
- The system requires only parameter tuning (config.py), not architectural changes, to transition to outdoor flight
- This adaptability is itself a design outcome, not an accident

**Why it matters:** The Decision Making criterion (40%) at the 83-100 band specifically asks for "confidence and creativity in adapting to changing/challenging circumstances." The weather cancellation IS a challenging circumstance. The current text treats it as a weakness; it should also be framed as evidence of resilience.

---

## Minor Issues (not scored but worth fixing)

- **Cover page** lists "et al." -- the brief requires member names/bios in the introduction, but the cover should ideally list all five names.
- **Team Member 2/3/4/5** are placeholder names in the introduction. Replace with real names before submission.
- **References:** Verify all `\cite{}` keys resolve in `references.bib` (some like `sheridan2002humans`, `gabriely2001spanning` may be missing).
- **Page count check:** With Design Rationale (~4pp) + System Description (~5pp) + Requirements Verification (~3pp) + Evaluation (~3pp) = ~15 pages. Adding path planning content may push over the limit -- consider trimming the MCDA tables or moving one to an appendix.
