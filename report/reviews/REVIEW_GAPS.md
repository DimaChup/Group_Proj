# Report Review: Gaps, Inconsistencies, and Recommendations

Date: 2026-03-27 (comprehensive re-review)
Scope: All body sections (exec_summary, intro_d6, design_rationale, system_description, requirements_verification, evaluation) plus path planning (05_path_planning.tex), main.tex structure, figures directory, and dashboard report data.

---

## 1. NUMBER INCONSISTENCIES

### 1.1 HFOV: 49.3 vs 49.4 vs 54.4 degrees
- `system_description.tex` line 34: "horizontal FOV of approximately 49.3 degrees" (Pi camera)
- `requirements_verification.tex` R05: "calibrated HFOV (49.4 degrees)" -- minor rounding mismatch, pick one
- `05_path_planning.tex` uses the same sensor model and gets consistent 49.3 from Eq (1)
- `07_target_localisation.tex` (appendix) caption: "54.4 degree HFOV" -- this is the DJI video FOV, not the Pi camera. This is technically correct (different cameras) but the report never explains the distinction clearly in the body. A reader will see 49.3 and 54.4 and be confused.
- **FIX**: Standardise to 49.3 for Pi camera. Add a parenthetical in the DJI video analysis sections clarifying that 54.4 is the DJI cropped-video FOV, not the Pi camera FOV.

### 1.2 Search speed: 5, 8, or 10 m/s?
- `exec_summary.tex`: "5 m/s search speed"
- `design_rationale.tex` sec:autonomy-rationale: "scanning terrain at 5 m/s"
- `evaluation.tex` D2: "10 m/s search speed" with "2.1 m between frames"
- `evaluation.tex` D3: "1 m position error at 5 m/s"
- `evaluation.tex` fig caption: "nominal search speed of 8 m/s"
- `05_path_planning.tex`: altitude-dependent speed schedule "6 m/s at 20m to 10 m/s at 50m"
- `requirements_verification.tex` R05: "search speed of 10 m/s" with "2.1 m between frames"
- **FIX**: These are all different numbers for the same thing. The path planning section defines 6-10 m/s altitude-dependent. At 35m altitude, interpolation gives ~8 m/s. The exec summary says 5 m/s (this is the FOCUS AREA speed, not the general search speed). Pick one nominal value (8 m/s at 35m) and use it consistently. Fix exec summary from "5 m/s" to "8 m/s" or clarify it is altitude-dependent (6-10 m/s).

### 1.3 Ground footprint width: 27.6m vs 32.2m
- `system_description.tex` sec:search-pattern: "ground footprint is ~32.2m wide, yielding 25.7m lane spacing"
- `requirements_verification.tex` R05: "ground footprint of approximately 27.6m per pass"
- `05_path_planning.tex`: "W_g = 32.2m" (at 35m altitude), which is correct from the equation
- The 27.6m appears in `04_computer_vision.tex` (appendix) computed at h=30m, not 35m
- **FIX**: At 35m: W_g = 5.02 * 35 / 5.46 = 32.2m. At 30m: W_g = 5.02 * 30 / 5.46 = 27.6m. The R05 section says "27.6m" but the search altitude is 35m. Change R05 to use 32.2m (or 32m) at 35m.

### 1.4 Waypoint count: 18 vs 35
- `exec_summary.tex`: "18 waypoints"
- `requirements_verification.tex` R01: "35 waypoints across 5 parallel passes"
- `11_field_results.tex` (appendix): "18 waypoints"
- **FIX**: Clarify. These may be from different polygon sizes or configurations. Use one consistent number in the body text, and if 35 is from a different test, clarify.

### 1.5 Figure count: "14 figures" in exec summary
- Exec summary claims "14 figures"
- Actual figure labels in the body sections: architecture, pi_system, cv_pipeline, state_machine, gps_bullseye, gps_error_direction, gps_convergence, estimator_comparison, mission_timeline, coverage_vs_time (only if 05_ is included), conf_vs_alt, det_vs_speed, latency_breakdown, detection_heatmap
- But geofence_diagram and search-pattern are referenced in the body but not defined there
- coverage_vs_time is only in 05_path_planning.tex which is NOT currently in the body
- **FIX**: Count figures after all structural fixes are applied, then update the claim

### 1.6 Detection per-pass frames: needs recalculation
- Used as "11-17 frames" consistently in system_description.tex and requirements_verification.tex
- But R05 uses "10 m/s" to compute "2.1m between frames" while other sections use different speeds
- At 8 m/s (the interpolated 35m speed), frame advance = 8/4.8 = 1.67m, giving ~19 frames in a 32.2m footprint
- **FIX**: Recalculate with the agreed nominal speed and footprint

### 1.7 Confidence threshold: 0.2 vs 0.4
- `system_description.tex` cv section: "confidence filtering (threshold 0.2)"
- `CLAUDE.md` and `MEMORY.md`: "Confidence threshold: 0.4"
- `evaluation.tex` D4: "detection threshold of 0.2"
- **FIX**: Verify which threshold is actually in the code. The report should match the deployed value.

---

## 2. BROKEN/MISSING CROSS-REFERENCES

### 2.1 fig:geofence-diagram -- UNDEFINED in body
- Referenced in `requirements_verification.tex` R02: "illustrated in Figure~\ref{fig:geofence-diagram}"
- The figure file `geofence_diagram.pdf` EXISTS in figs/ but no `\label{fig:geofence-diagram}` exists in any body section
- The figure is not included via `\includegraphics` in any body section
- **FIX**: Add the geofence diagram figure to requirements_verification.tex R02 section

### 2.2 fig:search-pattern -- UNDEFINED
- Referenced in `requirements_verification.tex` R05: "overlaying the waypoint pattern on the KML satellite image (Figure~\ref{fig:search-pattern})"
- No label `fig:search-pattern` exists anywhere in the report
- No corresponding figure file found in figs/
- **FIX**: Either create the figure (lawnmower pattern overlay on satellite image) or remove the reference

### 2.3 tab:bug-cost -- defined in appendix only
- Referenced in `evaluation.tex` P3 (body section)
- Defined in `testing_deep.tex` (Appendix E)
- This will compile (LaTeX cross-references work across the document) but the reader must flip to the appendix
- **FIX**: Pull a condensed version of the bug table into evaluation, or at minimum add "(Appendix E)" after the reference

### 2.4 sec:bug-discovery -- defined in appendix only
- Referenced in `evaluation.tex` P3 via `\secref{sec:bug-discovery}`
- Defined in `testing_deep.tex` (Appendix E)
- Same issue -- sends reader to appendix

### 2.5 sec:detection -- UNDEFINED
- Referenced in `05_path_planning.tex` line 160: "see Section~\ref{sec:detection}"
- No `\label{sec:detection}` exists anywhere in the report
- **FIX**: Point to `sec:cv` instead

### 2.6 Duplicate figure labels (WILL CAUSE LATEX ERRORS)
- `fig:conf_vs_alt` defined in BOTH `cv_extended.tex` (appendix) AND `evaluation.tex` (body)
- `fig:det_vs_speed` defined in BOTH `cv_extended.tex` (appendix) AND `evaluation.tex` (body)
- `fig:latency_breakdown` defined in BOTH `cv_extended.tex` (appendix) AND `evaluation.tex` (body)
- `fig:architecture` defined in BOTH `02_system_architecture.tex` AND `system_description.tex`
- `fig:cv_pipeline` defined in BOTH `04_computer_vision.tex` AND `system_description.tex`
- **These WILL cause LaTeX "multiply defined label" warnings and unpredictable cross-references**
- **FIX**: Remove duplicate labels from the appendix versions, or rename them (e.g., `fig:conf_vs_alt_extended`)

---

## 3. FIGURES: REFERENCED BUT MISSING FROM BODY

### 3.1 Geofence diagram -- HIGH PRIORITY
- `geofence_diagram.pdf` exists in figs/
- Referenced in R02 but never included with `\includegraphics`
- This is a key safety figure that should be visible in the body

### 3.2 Search pattern / lawnmower satellite overlay -- MEDIUM
- Referenced in R05 but no figure exists
- `coverage_vs_time.pdf` exists (in 05_path_planning.tex, which is NOT in the body)
- Consider creating a satellite image overlay showing the lawnmower pattern

### 3.3 Detection overlay example -- HIGH PRIORITY
- No detection example figure in the body (bounding box on a frame)
- `fig:detection-overlay` exists in `figure_descriptions.tex` (appendix) but not in body
- The reader never sees what a detection looks like

### 3.4 Ground station dashboard screenshot -- MEDIUM
- `fig:dashboard-screenshot` exists in `figure_descriptions.tex` (appendix) but not in body
- The ground station is described in text but never shown

### 3.5 Hardware photo -- MEDIUM
- `fig:hardware-photo` and `fig:bench-setup` exist in appendix but not in body
- A photo of the actual assembled drone would strengthen the hardware section

---

## 4. PATH PLANNING SECTION (05_path_planning.tex) -- NOT IN BODY

The file `05_path_planning.tex` contains ~180 lines of excellent content:
- Rotated-mask algorithm detail (6-step algorithm)
- Lane width equations with derivation
- Scan angle optimisation (216-configuration sweep)
- Energy analysis model
- Bezier smoothing with equation
- Focus area support
- Spiral alternative
- Coverage algorithm comparison table
- Flight parameters table
- coverage_vs_time figure

**This section is NOT included in main.tex body.** It is not in the body AND not in the appendices -- it is completely orphaned.

The body's `system_description.tex` has a brief 5-line summary of path planning (sec:search-pattern) that is far thinner than the standalone section.

**RECOMMENDATION**: Either:
1. Replace the brief `system_description.tex` path planning subsection with `\input{sections/05_path_planning}` (if page budget allows), OR
2. Pull the most impactful content (equations, energy analysis, flight params table, coverage figure) into the body and add 05_ as an appendix

The 05_path_planning.tex content is some of the strongest technical material in the report and directly demonstrates "Specialist Skills" and "Decision Making" per the rubric.

---

## 5. CLAIMS WITHOUT EVIDENCE (in body sections)

### 5.1 "58 test scripts" -- unverified, no body table
- Claimed in exec_summary and evaluation (P7)
- Listed in appendix `test_scripts_guide.tex` but never summarised in body
- The dashboard WBS lists "90 tasks" which is a different count
- **FIX**: Count the actual scripts, add a compact category summary table to body

### 5.2 "12 defects caught" -- no body table
- Claimed in evaluation P3, references tab:bug-cost in appendix
- The defect list is compelling evidence -- a condensed 5-row version belongs in the body

### 5.3 "mAP50 = 0.995" -- train/val overlap acknowledged but headline number unqualified
- Correctly flagged in evaluation D5, but the exec summary and other body sections use 0.995 as a headline without qualification
- **FIX**: When citing 0.995 in exec summary and system description, add "(on validation set sharing the synthetic generation pipeline)"

### 5.4 R08 autonomy level: "Level 2" vs "Level 5" vs "Level 3"
- `requirements_verification.tex` R08: "Level 2 semi-autonomy"
- `design_rationale.tex` sec:autonomy-rationale: "Sheridan Level 5" for search, "Level 3" for landing
- Using "Level 2" and "Level 5" for the same system without explanation is confusing
- **FIX**: Use the Sheridan framework consistently. If Level 5 for search and Level 3 for landing, say that in R08 too.

### 5.5 "4,400 lines of code" -- uncited
- Stated in system_description.tex
- Should be verifiable; consider removing if not easily confirmed

---

## 6. SECTIONS TOO THIN

### 6.1 Ground Station (system_description.tex sec:groundstation) -- 4 lines
- No figure, no architecture detail, no screenshot
- The ground station is a significant subsystem (pi_flight.py is 1097 lines)
- **FIX**: Add dashboard screenshot, MJPEG latency measurement, command flow

### 6.2 Simulation Framework (system_description.tex sec:simulation) -- 6 lines + 1 figure
- Four simulation levels listed but no detail
- **FIX**: Add interactive simulator description, SITL architecture, DJI video replay methodology

### 6.3 Hardware Platform (system_description.tex sec:hw) -- BOM table + 3 lines
- No hardware photo, no wiring diagram
- **FIX**: Add hardware photo and connection diagram

### 6.4 Search Pattern in Body -- 5 lines
- The full 05_path_planning.tex has excellent content completely wasted
- See Section 4 above

---

## 7. TABLES/GRAPHS/FIGURES THAT COULD STILL BE ADDED

### 7.1 STRONGLY RECOMMENDED (high impact, data exists)
1. **Geofence diagram** -- PDF exists, just needs \includegraphics in R02
2. **Detection example frame** -- bounding box overlay on a real/DJI frame
3. **Bug discovery table (condensed)** -- 5-6 key defects with tier, resolution time, in body
4. **Test script category summary** -- 1 small table: category, count, example
5. **Search pattern satellite overlay** -- lawnmower on KML map

### 7.2 RECOMMENDED (moderate impact)
6. **Ground station screenshot** -- web dashboard with detection overlay
7. **Hardware assembly photo** -- assembled drone with components labelled
8. **Confusion matrix** -- from model training (exists in cv_models/)
9. **Energy breakdown** -- from the 216-config sweep data (transit vs search vs turns)
10. **Bezier smoothing comparison** -- before/after path illustration
11. **Dashboard React app mention** -- "innovative communication technique" for marks

### 7.3 NICE TO HAVE
12. **Altitude-speed schedule graph** -- linear interpolation visualised
13. **Gantt chart** -- project timeline
14. **Detection confidence histogram** -- distribution from video analysis
15. **Frame-by-frame detection strip** -- 5-6 frames showing target entering/leaving FOV

---

## 8. CONTENT FROM APPENDICES TO PULL INTO BODY

### 8.1 Path Planning (05_path_planning.tex) -- HIGHEST PRIORITY
- Algorithm overview, lane width equation, coverage_vs_time figure, flight params table
- Currently completely orphaned (not in body OR appendix)

### 8.2 Bug Discovery Table (testing_deep.tex tab:bug-cost)
- Referenced in body but only in appendix
- Pull condensed 5-row version into evaluation

### 8.3 Model Training (12_model_training.tex)
- Dataset composition (300 syn + 16 real + 50 neg), domain randomisation, before/after
- Key differentiator for "initiative" marks

### 8.4 Safety Layers (13_safety_risk.tex)
- Five defence-in-depth mechanisms -- compelling for "Decision Making"
- Pull geofence diagram + safety layer summary table

### 8.5 Calibration Results (calibration_deep.tex)
- Lens calibration RMS, FOV correction, BGR discovery
- Strong "evidence-based adaptation" material -- pull summary table

---

## 9. STRUCTURAL ISSUES

### 9.1 05_path_planning.tex not included anywhere in main.tex
- Not in body, not in appendices -- completely orphaned
- **CRITICAL FIX**

### 9.2 Duplicate appendix letter in comments
- main.tex line 246: "% Appendix R: Centering analysis"
- main.tex line 252: "% Appendix R: Figure descriptions"
- LaTeX auto-numbers so just confusing comments, but clean up

### 9.3 Team member names still placeholder
- intro_d6.tex: Four team members are `\textcolor{red}{[NAME]}`
- **Must be filled before submission**

### 9.4 Report Structure paragraph references wrong sections
- "Sections sec:sysdesc--sec:groundstation" -- sec:groundstation is a subsection, not a top-level section
- "Section sec:testing" -- testing is only in appendix, not in body
- **FIX**: Update to match actual body organisation

### 9.5 Exec summary claims don't match body
- "five-tier progressive testing framework" -- never explained in body (only appendix)
- "58 test scripts" -- needs verification
- "14 figures" -- needs recount after structural fixes

---

## 10. DASHBOARD DATA (group-report-data.ts) -- UNUSED EVIDENCE

### 10.1 "Show CREATIVITY" tip not fully exploited
- The GPS estimation pipeline (custom pinhole-to-GPS projection with Kalman filter, spatial clustering, inverse-variance weighting) is a novel development, not a library call
- Body mentions it but could emphasise originality more

### 10.2 "Include failed experiments" tip
- Evaluation does this well (D1-D9) but could add the SRT sync failure explicitly

### 10.3 Dashboard as "innovative communication technique"
- The React dashboard is NEVER mentioned in the body sections
- **FIX**: Add a sentence mentioning it -- directly targets Communication (20%) rubric criterion

### 10.4 Page budget alignment
- Dashboard allocates: Design 4 + System 4 + Verification 4 + Evaluation 3 = 15 pages
- System description currently thin; pulling in path planning content would fill the allocation

---

## 11. SUMMARY OF CRITICAL FIXES (Priority Order)

| # | Fix | Severity | Effort |
|---|-----|----------|--------|
| 1 | Include 05_path_planning.tex in body or appendix (orphaned) | CRITICAL | Low |
| 2 | Fix search speed inconsistency (5 vs 8 vs 10 m/s) | HIGH | Low |
| 3 | Fix ground footprint (27.6m vs 32.2m -- wrong altitude in R05) | HIGH | Low |
| 4 | Add geofence diagram figure to R02 body (PDF exists) | HIGH | Low |
| 5 | Fix duplicate figure labels (conf_vs_alt etc in body+appendix) | HIGH | Low |
| 6 | Create or remove fig:search-pattern reference in R05 | HIGH | Medium |
| 7 | Fix sec:detection undefined reference in 05_path_planning | MEDIUM | Low |
| 8 | Fix autonomy level numbers (Level 2 vs 5 vs 3) | MEDIUM | Low |
| 9 | Fill team member names (4x [NAME] in intro_d6.tex) | CRITICAL | Low |
| 10 | Verify "58 test scripts" claim and add summary table | MEDIUM | Medium |
| 11 | Add detection example figure to body | MEDIUM | Medium |
| 12 | Thicken ground station subsection (4 lines -> proper coverage) | MEDIUM | Medium |
| 13 | Fix HFOV rounding (49.3 vs 49.4) | LOW | Low |
| 14 | Add dashboard mention for communication marks | LOW | Low |
| 15 | Fix waypoint count inconsistency (18 vs 35) | MEDIUM | Low |
| 16 | Qualify mAP50=0.995 in exec summary/system desc | LOW | Low |
| 17 | Fix Report Structure paragraph cross-refs | LOW | Low |
