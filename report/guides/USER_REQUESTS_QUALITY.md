# Quality & Process Requirements -- User Requests Checklist

**Generated: 2026-03-27**
**Purpose: Track every quality/process requirement the user explicitly asked for.**

Status key:
- [x] = Done, with evidence
- [~] = Partially done (exists but incomplete)
- [ ] = Missing or not yet implemented

---

## 1. No AI Mentions Anywhere in Reports (Category 2 Minimal)

**Status: [x] DONE**

**Evidence:**
- Full regex grep for `Claude`, `ChatGPT`, `LLM`, `language model`, `AI assist`, `AI generat`, `Copilot`, `GPT-4`, `AI tool`, `AI writing` across all `.tex` files in `report/` returns **zero matches**.
- All uses of "AI" in the report refer to the project's own AI-based detection system (legitimate usage).
- Verified in `CHECKLIST.md` under "No mention of AI writing tools" -- marked PASS for both D6 and D7.
- `report/guides/CHECKLIST.md` line 34: "Grep confirms no mentions of ChatGPT, Claude, Copilot, GPT, LLM, or writing assistant in any .tex file."

**Where verified:** `report/guides/CHECKLIST.md` (lines 34, 66), grep search results.

---

## 2. Proper Scoring Against Rubric -- Karpathy Iterations (Score, Fix, Re-score)

**Status: [x] DONE**

**Evidence:**
- **4 scoring iterations** exist in `report/reviews/`:
  - `SCORING_D6.md` -- initial scoring
  - `SCORING_D6_v2.md` -- second pass after fixes
  - `SCORING_D6_v3.md` -- third pass, all content included (score: 78-82)
  - `SCORING_D6_v4.md` -- fourth pass
  - `FINAL_SCORE.md` -- consolidated final score
- Each version identifies weaknesses and the next version shows fixes applied.
- D7 also has iterative scoring: `report/personal/reviews/SCORING_D7.md`, `SCORING_D7_v2.md`.
- Additional targeted reviews: `cv_review.md`, `design_rationale_review.md`, `figures_review.md`, `requirements_evaluation_review.md`, `system_description_review.md`, `state_machine_review.md`.
- `GOLDMINE_CHECKLIST.md` tracks current estimated score (~81, target 83+).

**Where:** `report/reviews/SCORING_D6*.md`, `FINAL_SCORE.md`, `report/personal/reviews/SCORING_D7*.md`

---

## 3. Brief Extracted Thoroughly with Images/Screenshots of Each Page

**Status: [x] DONE**

**Evidence:**
- `report/guides/TARGET_BRIEF.md` -- full brief extraction with rubric criteria, scoring bands, format requirements.
- `report/guides/CHECKLIST.md` -- 131-line checklist mapping every brief requirement to report sections.
- **Page screenshots exist** in three directories:
  - `report/report_pages/` -- 86 page screenshots (page_01.png through page_86.png)
  - `report/report_d6_pages/` -- 33 page screenshots (D6 compiled PDF)
  - `report/report_d7_pages/` -- 8 page screenshots (D7 compiled PDF)

**Where:** `report/guides/TARGET_BRIEF.md`, `report/guides/CHECKLIST.md`, `report/report_*_pages/`

---

## 4. Design Summary v2 for Sending to Teammate

**Status: [~] PARTIALLY DONE**

**Evidence:**
- No standalone "Design Summary v2" document exists as a separate file specifically for a teammate.
- The closest equivalents are:
  - `report/sections/system_description.tex` (240 lines, comprehensive system overview)
  - `report/sections/design_rationale.tex` (235 lines, all design decisions)
  - `report/team/main.tex` exists as a team report, but this is the D6 group report itself, not a standalone summary for a teammate.
- The user's request for a concise summary document to hand to a teammate has not been fulfilled as a distinct deliverable.

**Where:** No dedicated file. Partial coverage in `report/sections/system_description.tex` and `report/team/main.tex`.

---

## 5. Reports Organized in Single Directory (Not Scattered)

**Status: [x] DONE**

**Evidence:**
- All report files are under `report/` with clear subdirectories:
  - `report/main.tex` -- D6 master file
  - `report/personal/main.tex` -- D7 master file
  - `report/team/main.tex` -- team report
  - `report/sections/` -- all D6 section `.tex` files (50+ files)
  - `report/personal/sections/` -- D7 section files (5 files)
  - `report/figs/` -- all figures
  - `report/guides/` -- tracking/checklist documents
  - `report/reviews/` -- scoring and review documents (29 files)
  - `report/references.bib` -- bibliography

**Where:** `report/` directory tree.

---

## 6. All Figures Validated Visually (Screenshot Pages, Check Rendering)

**Status: [~] PARTIALLY DONE**

**Evidence:**
- Two visual review documents exist:
  - `report/reviews/VISUAL_REVIEW.md` (318 lines) -- page-by-page review of compiled PDF
  - `report/reviews/VISUAL_REVIEW_v2.md` (217 lines) -- second pass
  - `report/reviews/FIGURE_TABLE_AUDIT.md` -- figure and table audit
  - `report/reviews/figures_review.md` -- dedicated figures review
  - `report/reviews/final_figures_visual.md` -- final figures visual check
  - `report/reviews/final_charts_visual.md` -- charts visual check
- Page screenshots exist for all pages (86 + 33 + 8 images across three directories).
- VISUAL_REVIEW.md line 12 confirms: "No placeholder figures were found. All tables render correctly."
- **Gap:** Not every individual figure has been confirmed pixel-by-pixel for correctness (e.g., axis labels, legend entries, data accuracy). The reviews are page-level, not figure-level deep checks.

**Where:** `report/reviews/VISUAL_REVIEW*.md`, `report/reviews/FIGURE_TABLE_AUDIT.md`, `report/report_*_pages/`

---

## 7. Numbers Consistent Across All Sections

**Status: [ ] NOT DONE -- Known Inconsistencies Remain**

**Evidence:**
- `report/guides/USER_REQUESTS.md` (lines 303-311) documents **6 known inconsistencies**:
  1. Search speed: 5, 8, 10 m/s used in different sections
  2. Two FOV values (49.3 deg Pi vs 54.4 deg DJI) not always distinguished
  3. Footprint width R05: "27.6m" should be "32.2m" at 35m
  4. Sheridan level: R08 "Level 2" vs Design Rationale "Level 5/3"
  5. Waypoint count: exec summary "18" vs R01 "35 waypoints across 5 passes"
  6. Module names in system_description don't match actual code filenames
- These are documented but **unfixed** as of last update.
- `report/reviews/REVIEW_GAPS.md` also tracks inconsistencies.

**Where:** `report/guides/USER_REQUESTS.md` lines 303-311, `report/reviews/REVIEW_GAPS.md`

---

## 8. Real Simulation Data Used Where Available (Not Made-Up)

**Status: [x] DONE**

**Evidence:**
- 14 `real_*.png` figures generated from actual simulation code runs:
  - `real_energy_heatmap.png`, `real_energy_vs_altitude.png`, `real_optimal_pattern.png`
  - `real_path_patterns.png`, `real_scan_angle.png`, `real_coverage.png`
  - `real_detection_envelope.png`, `real_speed_vs_blur.png`, `real_speed_vs_frames.png`
  - `real_time_vs_altitude.png`, `real_altitude_vs_px.png`, `real_dry_run_pattern.jpg`
  - `real_scan_lines.png`, `real_search_comparison.png`
- DJI video analysis data used for detection charts (conf_vs_alt, det_vs_speed).
- `generate_charts.py` script exists to regenerate figures from real data.
- Benchmark numbers from actual Pi 5 hardware testing (206.5ms, 4.8 FPS, 0.966 confidence).
- 216-configuration parametric sweep run with actual simulation code.

**Where:** `report/figs/real_*.png` (14 files), `report/generate_charts.py`

---

## 9. Multiple Agents Reviewing Different Parts in Parallel

**Status: [x] DONE**

**Evidence:**
- `report/reviews/` contains 29 review files, many with `final_` prefix indicating parallel agent waves:
  - Wave of targeted reviews: `final_cv_comprehensive.md`, `final_design_rationale.md`, `final_design_strategy.md`, `final_evaluation.md`, `final_exec_intro.md`, `final_figures_visual.md`, `final_gps_safety.md`, `final_operations.md`, `final_path_optimization.md`, `final_real_plots.md`, `final_remaining_appendices.md`, `final_requirements.md`, `final_system_description.md`, `final_charts_visual.md`
  - Earlier parallel reviews: `cv_review.md`, `design_rationale_review.md`, `figures_review.md`, `requirements_evaluation_review.md`, `system_description_review.md`, `state_machine_review.md`
- Reviews cover different sections simultaneously (CV, design rationale, system description, evaluation, figures, requirements, etc.).
- CLAUDE.md session log (2026-03-11) confirms: "Thorough code review (6 parallel agents)."

**Where:** `report/reviews/final_*.md` (14 files), `report/reviews/*_review.md` (6 files)

---

## 10. Track Everything in a Master Checklist

**Status: [x] DONE**

**Evidence:**
- `report/guides/GOLDMINE_CHECKLIST.md` -- master tracking with completion dashboard, every section status, quality ratings, must-fix items.
- `report/guides/GOLDMINE_MASTER.md` -- definitive section tracking with page estimates and quality grades.
- `report/guides/USER_REQUESTS.md` -- exhaustive extraction of all user requests (361 lines).
- `report/guides/CHECKLIST.md` -- brief compliance checklist (131 lines).
- `report/guides/TARGET_BRIEF.md` -- brief requirements extraction.

**Where:** `report/guides/GOLDMINE_CHECKLIST.md`, `GOLDMINE_MASTER.md`, `USER_REQUESTS.md`, `CHECKLIST.md`

---

## 11. Review Against the Actual Brief Requirements

**Status: [x] DONE**

**Evidence:**
- `report/guides/TARGET_BRIEF.md` -- full brief extraction with rubric criteria (Specialist Skills 40%, Decision Making 40%, Communication 20%).
- `report/guides/CHECKLIST.md` -- 131-line checklist mapping every brief requirement (D6 format, D6 content, D7 format, D7 AHEP4 standards) to report sections with PASS/FAIL status.
- Scoring files score against the actual rubric language (quoted in `TARGET_BRIEF.md`).

**Where:** `report/guides/TARGET_BRIEF.md`, `report/guides/CHECKLIST.md`

---

## 12. Don't Cut Pages -- This Is a Goldmine Resource, Not the Final Submission

**Status: [x] DONE**

**Evidence:**
- The report retains massive appendix content (19 appendices in main.tex, 13 orphaned sections preserved as files).
- `GOLDMINE_MASTER.md` and `GOLDMINE_CHECKLIST.md` explicitly track this as a "goldmine" approach.
- Orphaned sections (05_path_planning.tex, steeple.tex, old numbered sections 00-09, 15) are all preserved on disk, not deleted.
- Body is ~15.5 pages (close to limit), but appendices run to 50+ additional pages of rich content.
- The compiled PDF with appendices is 86 pages (per screenshot count in `report_pages/`).

**Where:** `report/guides/GOLDMINE_MASTER.md`, `report/guides/GOLDMINE_CHECKLIST.md`, full report at 86 pages.

---

## 13. Include Alternative Text Versions to Choose From

**Status: [x] DONE**

**Evidence:**
- `report/sections/alternatives.tex` -- 78 lines with 5 sets of A/B/C paragraph alternatives:
  1. STEEPLE opening paragraph (3 versions)
  2. Weather adaptation paragraph (2+ versions)
  3. Autonomy level paragraph
  4. Evaluation opening paragraph
  5. Conclusion/summary paragraph
- Each version is a drop-in replacement paragraph, ready to swap.

**Where:** `report/sections/alternatives.tex`

---

## 14. Color-Coded Headings for Different Versions

**Status: [x] DONE**

**Evidence:**
- `report/sections/alternatives.tex` uses `\color{blue}` for Version A (current), `\color{red}` for Version B, `\color{olive}` for Version C.
- Confirmed in file content: `{\color{blue} Version A`, `{\color{red} Version B`, `{\color{olive} Version C`.
- Requires `\usepackage{xcolor}` in preamble (noted in file header).

**Where:** `report/sections/alternatives.tex` (lines 13, 16, 19 and throughout)

---

## 15. Score Deeply and Honestly, Be Brutal

**Status: [x] DONE**

**Evidence:**
- 4 scoring iterations (v1 through v4) plus FINAL_SCORE.md, each with detailed per-criterion breakdowns.
- Scores are honest: current estimate 78-82, not inflated. Target stated as 83+.
- Specific weaknesses called out bluntly:
  - "R06 thin (no quantitative evidence, no figure)"
  - "R07 no visual"
  - "streaming_architecture: Over-engineered -- 2+ pages justifying MJPEG is overkill"
  - "exec_summary doesn't mention field day pivot"
  - Number inconsistencies documented but unfixed
- `REVIEW_GAPS.md` and `CRITICAL_REVIEW_v3.md` provide critical assessments.
- Quality grades use honest scale (A, A-, B+, B, B-) with specific rationale.
- `GOLDMINE_CHECKLIST.md` line 23: "Must-fix issues: 3 done / 11 total (27%)" -- not sugar-coated.

**Where:** `report/reviews/SCORING_D6_v3.md` (score 78-82), `report/reviews/CRITICAL_REVIEW_v3.md`, `report/guides/GOLDMINE_CHECKLIST.md`

---

## 16. Proper Sequencing of Agent Waves

**Status: [x] DONE**

**Evidence:**
- Review files show clear wave structure:
  - **Wave 1**: Individual section reviews (`cv_review.md`, `design_rationale_review.md`, `system_description_review.md`, etc.)
  - **Wave 2**: Targeted final reviews (`final_cv_comprehensive.md`, `final_design_rationale.md`, etc.) -- 14 parallel review files
  - **Wave 3**: Cross-cutting reviews (`VISUAL_REVIEW.md`, `FIGURE_TABLE_AUDIT.md`, `REVIEW_GAPS.md`)
  - **Wave 4**: Scoring iterations (`SCORING_D6.md` through `SCORING_D6_v4.md`, `FINAL_SCORE.md`)
- Each wave builds on the previous one's findings.

**Where:** `report/reviews/` directory (29 files showing wave progression)

---

## 17. Personal Reflections -- Edward Focusing on CV

**Status: [ ] NOT DONE -- Edward Not Mentioned**

**Evidence:**
- `report/personal/sections/` contains 5 D7 sections (01-05).
- Grep for "Edward" or "edward" across all personal report `.tex` files returns **zero matches**.
- The user specifically asked for personal reflections to mention that Edward focused on CV together with the user.
- This detail is absent from the D7 reflective report.
- `report/guides/USER_REQUESTS.md` (line 259-261) notes this as `[~]` with "Quality: UNKNOWN -- not checked in detail."

**Where:** Missing from `report/personal/sections/*.tex`. Needs to be added to Section 04 (teamwork/leadership) or Section 02 (design/problem-solving).

---

## Summary Table

| # | Requirement | Status | Priority to Fix |
|---|-------------|--------|-----------------|
| 1 | No AI mentions anywhere | [x] DONE | -- |
| 2 | Karpathy scoring iterations | [x] DONE | -- |
| 3 | Brief extracted with page screenshots | [x] DONE | -- |
| 4 | Design Summary v2 for teammate | [~] PARTIAL | LOW (not a graded deliverable) |
| 5 | Reports in single directory | [x] DONE | -- |
| 6 | All figures validated visually | [~] PARTIAL | MEDIUM (page-level done, figure-level incomplete) |
| 7 | Numbers consistent across sections | [ ] MISSING | **CRITICAL -- 6 known inconsistencies unfixed** |
| 8 | Real simulation data used | [x] DONE | -- |
| 9 | Multiple parallel agent reviews | [x] DONE | -- |
| 10 | Master checklist tracking | [x] DONE | -- |
| 11 | Review against actual brief | [x] DONE | -- |
| 12 | Don't cut pages (goldmine) | [x] DONE | -- |
| 13 | Alternative text versions | [x] DONE | -- |
| 14 | Color-coded version headings | [x] DONE | -- |
| 15 | Score deeply and honestly | [x] DONE | -- |
| 16 | Proper agent wave sequencing | [x] DONE | -- |
| 17 | Edward + CV in personal reflections | [ ] MISSING | **HIGH -- graded D7 content gap** |

**Totals: 13 done, 2 partial, 2 missing out of 17 requirements.**

### Top Priority Fixes

1. **[CRITICAL] Number consistency** (#7) -- 6 documented inconsistencies across sections (speed, FOV, footprint, Sheridan level, waypoint count, module names). Fix in source `.tex` files.
2. **[HIGH] Edward + CV mention** (#17) -- Add to D7 personal report sections (teamwork or design/problem-solving). The user explicitly asked for this.
3. **[MEDIUM] Figure-level visual validation** (#6) -- Page-level review done, but individual figure data accuracy not fully confirmed.
4. **[LOW] Design Summary v2** (#4) -- Not a graded deliverable; existing system_description.tex serves the purpose within the report.
