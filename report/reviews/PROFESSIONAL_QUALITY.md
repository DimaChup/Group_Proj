# Professional Quality Audit — Goldmine Report (D6)

Audited: 2026-04-03. Covers all four body sections (Design Rationale, System Description, Requirements Verification, Evaluation), executive summary, introduction, bibliography, and key appendices.

---

## 1. Claims Backed by Evidence

**VERDICT: STRONG (9/10)**

Almost every claim in the body is backed by a specific number, measurement, or reference. Examples of excellence:

- "mAP50 = 0.995" with dataset size (366 images), composition (300 syn + 16 real + 50 neg), and training resolution stated
- "206.5 ms per frame (4.8 FPS)" with run count (50 runs) and hardware specified (Pi 5 CPU, XNNPACK)
- "CEP50 = 2.3 m" with worst case (16.5 m) and source (DJI video replay)
- "FOV calibration correction 7.0 mm -> 5.46 mm" with method (tape measure at 1 m)
- "12 defects caught at Tiers 1-3, total debugging time ~6 hr 10 min"
- Cost comparison: GBP 565 total vs DJI Matrice 30T

One weakness: the SSD MobileNet mAP (0.88) is measured on COCO while YOLO figures use the custom dataset -- the text notes this ("indicative rather than direct") which is honest but the table itself doesn't flag it visually.

**Honest about limitations**: D5 in evaluation explicitly calls the 0.995 mAP an "upper bound" due to train/val overlap. D1 openly states zero outdoor flights completed. This is exactly the right approach for a top-band report.

---

## 2. Figures Generated from Real Data

**VERDICT: EXCELLENT (10/10)**

- 32 generator scripts (`figs/gen_*.py`) produce figures programmatically
- 150 figure files in the figs directory (PDF + PNG pairs)
- Body explicitly states: "15 body figures generated programmatically from calibration data, inference benchmarks, and flight video analysis -- not manually drawn -- ensuring reproducibility"
- Key data-driven figures confirmed present:
  - `coupling_matrix.pdf` -- variable coupling matrix
  - `altitude_speed_tradeoff.pdf` -- altitude-speed trade-off with composite score
  - `gps_bullseye.pdf` -- GPS estimation scatter from DJI video
  - `gps_error_direction.pdf` -- directional error distribution
  - `conf_vs_alt.pdf` -- detection confidence vs altitude
  - `det_vs_speed.pdf` -- detection rate vs speed
  - `latency_breakdown.pdf` -- per-frame latency budget
  - `detection_heatmap.pdf` -- spatial detection density
  - `coverage_vs_time.pdf` -- coverage progression
  - `state_machine.pdf` -- state transition diagram
  - `geofence_diagram.pdf` -- five-layer geofence visualisation
  - `cv_pipeline.pdf` -- CV pipeline diagram
  - `architecture.pdf` -- module dependency graph
  - `mission_overview.pdf` -- mission plan on site map
  - `mission_timeline.pdf` -- state transitions over time

No placeholder `\fbox` figures appear in any file included by `main.tex`. (Old section files like `04_computer_vision.tex` and `06_state_machine.tex` contain placeholders but are NOT included in the build.)

---

## 3. Table Formatting (booktabs)

**VERDICT: STRONG (9/10)**

All body section tables use `\toprule`, `\midrule`, `\bottomrule` consistently:
- STEEPLE table (Tab 1)
- Parameter derivation chain (Tab 2)
- Four MCDA tables (companion, comms, model, search pattern)
- Bill of materials (Tab 6)
- MAVLink commands (Tab 7)
- Requirements verification (Tab 8)
- Plus/delta (Tab 9)
- Five-tier testing (Tab 10)

The `\compactTable` command is used consistently for dense tables.

**Issue**: `vision_standalone.tex` uses `\hline` throughout (20+ instances) -- but this file is NOT included in the main build, so it does not affect the submitted report. All included appendices use booktabs consistently.

---

## 4. Equations Numbered and Referenced

**VERDICT: GOOD (7/10)**

- 110+ equations across the report, all numbered via `\begin{equation}` environments
- Body sections reference equations properly: Eq. (1) for GSD in system_description.tex
- Appendices use `\eqref{}` and `Equation~\ref{}` consistently (30+ cross-references found)
- Good practice: equations have descriptive labels (`eq:gsd-sysdesc`, `eq:body-deep`, `eq:kalman-R-deep`)

**Issues**:
- **Duplicate label `eq:gsd`** appears in THREE files: `03_hardware_platform.tex`, `07_target_localisation.tex`, and `path_optimization_definitive.tex`. Only the last file is in the build, but this creates the potential for confusion if old files are ever re-included. The body uses `eq:gsd-sysdesc` (unique) -- correct.
- Some equations in appendices are unlabelled (no `\label{}`), e.g., several in `centering_analysis.tex` and `design_strategy.tex`. These are unreferenced so it is acceptable, but numbered-without-reference equations can look orphaned.

---

## 5. Cross-References That Resolve

**VERDICT: NEEDS ATTENTION (5/10)**

The LaTeX log reveals:
- **240 multiply-defined label warnings** -- mostly from old section files whose labels clash with the rewritten versions (e.g., `sec:training`, `sec:safety`, `sec:testing`, `sec:five-tier`). These are generated because both old and new appendix files define the same labels, and the new ones overwrite.
- **47 undefined reference/citation warnings**, including:
  - `sec:req-detail` (referenced on pages 20, 195, 196 -- appears in body requirements section)
  - `tab:gsd-values`, `sec:flight-testing`, `tab:preflight-cal`, `tab:cal-vs-budget`, `tab:hover-safety`, `tab:mavlink-messages`, `fig:bottleneck_shift`, `eq:footprint`, `tab:model_generations`, `alg:beacon-redirect` -- all in appendices
  - `fig:energy-heatmap`, `fig:pareto-parallel`, `fig:sensitivity-matrix`, `fig:tornado-sensitivity-app`, `fig:top3-paths-app`, `fig:energy-heatmap-app`, `tab:pareto-final`, `tab:px-vs-alt` -- optimisation appendices
  - Citations: `beard2012small`, `barber2006vision`, `johnson2013helicopter`, `murphy2016disaster` -- 4 missing bib entries (all in appendices)

**Critical**: `sec:req-detail` is referenced from the body (requirements_verification.tex line 59: "Appendix~\ref{app:req-detail}") but the label in `requirements_detail.tex` appears to use `app:req-detail` -- needs verification. The body text would show "??" in the PDF.

**Recommendation**: Fix the 4 missing citations and the undefined body reference before submission. The multiply-defined labels in appendices are cosmetic (last definition wins) but should be cleaned up.

---

## 6. Consistent Notation

**VERDICT: GOOD (8/10)**

Strengths:
- SI units used consistently via `\SI{}{}` throughout (metres, seconds, watts, etc.)
- Custom commands for cross-refs: `\figref`, `\tabref`, `\secref` -- used in some places
- `\SI` for all physical quantities: `\SI{35}{\metre}`, `\SI{8}{\metre\per\second}`, `\SI{206.5}{\milli\second}`
- Consistent variable naming: $h$ for altitude, $f$ for focal length, $v$ for speed, $w_s$ for sensor width

Minor inconsistencies:
- Some places use "8 m/s" in text while others use `\SI{8}{\metre\per\second}` -- mixed but mostly consistent
- GSD is defined with the same equation in both system_description.tex (Eq. 1, label `eq:gsd-sysdesc`) and appendix `gps_estimation_deep.tex` (label `eq:gsd-deep`). Both use the same symbols, which is good for readability.
- CEP50 notation varies between "CEP$_{50}$" and "CEP$_{50}$" -- actually consistent
- "mAP$_{50}$" used consistently throughout

---

## 7. Professional LaTeX Formatting

**VERDICT: EXCELLENT (9/10)**

Strengths:
- Clean preamble with well-organised package loading and comments
- Custom `\compactTable` command for dense tables
- Professional colour scheme (headblue for section headers)
- `mdframed` environments for info boxes and abstracts
- `microtype` for microtypographic improvements
- `siunitx` for consistent unit formatting
- `booktabs` throughout
- `biblatex` with proper numeric style, no DOI/ISBN clutter
- `multicol` for reference list
- Proper `\AlphAlph` handling for >26 appendices (AA, AB, etc.)
- Float control parameters tuned to prevent orphan floats

No raw formatting hacks found in body sections. No manual `\vspace` abuse, no `\\[20pt]` line breaks in body text, no `\newpage` mid-section.

---

## 8. Bibliography

**VERDICT: GOOD (8/10)**

- 117 bibliography entries across `references.bib` (1236 lines)
- Mix of peer-reviewed papers, conference proceedings, official standards, and software references
- Proper BibTeX types used: `@inproceedings`, `@article`, `@misc`, `@techreport`
- `biblatex` with `numeric` style, `sorting=none`, `maxbibnames=3`, `giveninits=true`
- DOI, ISBN, URL suppressed for clean output
- Displayed in two-column format

**Issues**:
- 4 undefined citations: `beard2012small`, `barber2006vision`, `johnson2013helicopter`, `murphy2016disaster` -- all referenced in appendices but missing from both .bib files
- `extra_refs.bib` is 6 lines and appears to contain no actual entries (0 `@` symbols) -- possibly empty or malformed
- Some `@misc` entries use `howpublished = {\url{...}}` which is correct for biblatex

---

## 9. Section Summaries

**VERDICT: STRONG (9/10)**

- **Design Rationale**: Has explicit "Section summary" paragraph at end (line 256) -- excellent, ties everything together with the evidence-driven engineering message
- **System Description**: No explicit summary paragraph, but the opening paragraph serves as both introduction and implicit summary by listing all seven subsystems with their key metrics
- **Requirements Verification**: Final paragraph summarises the verification status (8 fully verified, 3 simulation only, 1 partial gap) and identifies the biggest gap
- **Evaluation**: Final "Summary" paragraph (line 153-154) explicitly summarises all key numbers, outstanding gaps, and what would be needed to close them -- thorough and honest

---

## 10. Honest Assessment of Limitations

**VERDICT: EXCELLENT (10/10)**

This is the strongest aspect of the report. The evaluation section contains:
- 10 plus items and **9 delta items**, each with specific evidence
- D1: "No outdoor flight completed" -- states this plainly as the single largest gap
- D5: "Train/validation overlap" -- calls mAP50=0.995 an "upper bound" and prescribes the fix (50+ real labelled frames from a separate flight)
- D4: "No precision-recall curve" -- admits confidence threshold was chosen empirically
- D6: "Single-class detector cannot distinguish target types"
- D8: "Payload release not software-integrated"
- D9: "Float32 model on constrained hardware" -- acknowledges FP16/INT8 optimisation not deployed

Each delta has an explicit "Next step" action item. The weather cancellation is framed honestly as "information-maximisation, not failure" with four concrete outputs that resulted.

The executive summary states "High winds on the field day prevented powered flight; all integration results are therefore from simulation, bench tests, and video proxy analysis" -- no attempt to hide this.

---

## Overall Professional Quality Score: 84/100

### Breakdown:
| Criterion | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| Claims backed by evidence | 9/10 | 15% | 13.5 |
| Figures from real data | 10/10 | 15% | 15.0 |
| Table formatting | 9/10 | 5% | 4.5 |
| Equations numbered/referenced | 7/10 | 10% | 7.0 |
| Cross-references resolve | 5/10 | 15% | 7.5 |
| Consistent notation | 8/10 | 5% | 4.0 |
| Professional LaTeX | 9/10 | 10% | 9.0 |
| Bibliography | 8/10 | 10% | 8.0 |
| Section summaries | 9/10 | 5% | 4.5 |
| Honest limitations | 10/10 | 10% | 10.0 |
| **Total** | | **100%** | **83.0** |

### Top-Band Markers Present:
- [x] Every design decision traced to quantified rationale (physical measurement, parametric sweep, or energy budget)
- [x] Four decisions explicitly revised when evidence contradicted assumptions
- [x] All figures programmatically generated with reproducible scripts
- [x] Honest about the largest gap (no outdoor flight) without being defeatist
- [x] MCDA tables with sensitivity analysis confirming robustness
- [x] Parameter derivation chain showing unbroken traceability
- [x] Progressive testing framework with defect register and fix times
- [x] Autonomy level justified with asymmetric cost analysis
- [x] 117 references including peer-reviewed, standards, and software

### Fixes Required Before Submission:

**HIGH PRIORITY (affect body text):**
1. Fix `sec:req-detail` / `app:req-detail` label mismatch -- produces "??" in the requirements section body text
2. Add missing bib entries: `beard2012small`, `barber2006vision`, `johnson2013helicopter`, `murphy2016disaster`

**MEDIUM PRIORITY (affect appendices):**
3. Fix 20+ undefined figure/table references in optimisation appendices (energy-heatmap, pareto-parallel, sensitivity-matrix, etc.)
4. Clean up 240 multiply-defined labels by renaming labels in old/duplicate section files

**LOW PRIORITY (polish):**
5. Replace teammate placeholders (`\textcolor{red}{[TEAMMATE~3]}` etc.) in intro_d6.tex with real names
6. Verify `extra_refs.bib` is not empty/malformed (0 entries found)

### What Would Push This to 90+:
- Resolve all cross-reference warnings (the 47 undefined refs drag the score significantly)
- Add real hardware photos (assembled drone, bench setup, ground station screenshot)
- Include a precision-recall curve even from video replay data
- Add the defect register table (referenced as Appendix K / `app:bug-cost`) to the body evaluation as a condensed version
