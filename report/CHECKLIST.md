# D6 & D7 Report Checklist Against Brief Requirements

> Generated: 2026-03-27
> Brief: AENGM0074 Release 2.1 (4 Feb 2026)

---

## D6 Company Report (50%)

### Format & Structure

- [x] **Single PDF format** -- LaTeX compiles to single PDF
- [x] **Max 15 pages body** (excl. cover, exec summary, intro, refs, appendices) -- Counted sections: Design Rationale, System Description, Requirements Verification, Evaluation. These are the only 4 `\input` blocks between the "15-PAGE COUNTED CONTENT STARTS HERE" and "ENDS HERE" markers. Estimated at ~13-14 pages (tight margins, 10pt, 15mm margins). **ACTION: Compile and verify actual page count. The path_planning.tex section (188 lines, very dense) is NOT included in main.tex counted sections -- it exists as a standalone file but is not \input'd. Confirm this is intentional or if it should be folded into system_description.**
- [x] **Cover page present** -- Lines 126-133 of main.tex
- [x] **Executive summary present (1 page, self-contained)** -- `exec_summary.tex`, excluded from page count. Covers objective, system overview, key decisions, results, and what was demonstrated. Self-contained.
- [x] **Introduction present** -- `intro_d6.tex`, excluded from page count. Contains context/background, company description, member bios/roles, contribution summary table.
- [x] **Design Rationale present** -- `design_rationale.tex`, includes STEEPLE + hardware + software + detection + planning + state machine + HITL rationale
- [x] **System Description present** -- `system_description.tex`, includes hardware, software architecture, CV pipeline, search pattern, state machine, target localisation, ground station, simulation
- [x] **Requirements Verification present** -- `requirements_verification.tex`, covers R01-R12 individually with method, evidence, and status
- [x] **Evaluation present** -- `evaluation.tex`, plus/delta format as required, technical performance focus
- [x] **References present** -- biblatex with references.bib, excluded from page count
- [x] **Appendices present** -- 7 appendices (A-G): state table, config params, model training, safety/risk, testing, field results, future work. Excluded from page count, correctly marked as not assessed.

### Content Requirements

- [x] **STEEPLE analysis in Design Rationale** -- All 7 dimensions covered: Social, Technological, Economic, Environmental, Political, Legal, Ethical (Section 1.1)
- [x] **Member bios/roles in Introduction** -- 5 team members with names, backgrounds, and roles described
- [x] **Member contributions in Introduction** -- Table~1 maps each member to specific contributions
- [x] **Flow charts/schematics/images in System Description** -- Figure placeholders present for architecture diagram and state machine. **WARNING: Both are placeholder \fbox{} boxes, not actual figures. These MUST be replaced with real diagrams before submission.**
- [x] **Requirements verification for R01-R12** -- All 12 requirements addressed individually with verification method, evidence, and status. Summary table + detailed subsections.
- [x] **Plus/delta evaluation of TECHNICAL performance** -- Table with 8 Plus items (P1-P8) and 7 Delta items (D1-D7). Discussion section follows. Correctly excludes team-working (deferred to D7).
- [x] **GitHub link present** -- `\url{https://github.com/DimaChup/Group_Proj}` in R12 section and in the requirements table
- [x] **MIT licence mentioned** -- Confirmed in R12 section: "licensed under the MIT licence"
- [x] **No mention of AI writing tools** -- Grep confirms no mentions of ChatGPT, Claude, Copilot, GPT, LLM, or writing assistant in any .tex file. All "AI" references are about the project's detection system. **PASS (Category 2 Minimal)**

### Quality & Rubric Alignment

- [x] **Specialist Skills & Problem-Solving (40%)** -- Trade studies with MCDA tables (companion computer, comms architecture, detection model, search pattern). Quantitative evidence throughout. Progressive testing methodology.
- [x] **Decision Making (40%)** -- Evidence-based decisions documented with weighted scoring. Adaptation to constraints (Python 3.13 bug -> MAVProxy bridge, weather cancellation -> bench testing).
- [x] **Communication (20%)** -- Professional LaTeX formatting, consistent style, tables and figures, colour-coded section headers. **But: placeholder figures need replacing.**

### Issues Found

1. **CRITICAL: Placeholder figures** -- `system_description.tex` lines 42-46 and 100-105 have `\fbox{\parbox{...}}` placeholder boxes instead of real figures. The architecture diagram and state machine diagram MUST be real images before submission.
2. **CRITICAL: Placeholder figure in path planning** -- `05_path_planning.tex` lines 53-64 has a placeholder lawnmower pattern figure.
3. **WARNING: path_planning.tex not included** -- The 188-line `05_path_planning.tex` exists but is NOT `\input`'d in `main.tex`. The system_description.tex has a brief 1-paragraph coverage of search pattern (subsection 2.4). If path planning detail is intended for the main body, it needs to be included. If not, the current brief treatment may be sufficient but loses significant technical depth.
4. **MINOR: "et al." on cover page** -- Line 130: `Dmytro Chuprynyuk, \textit{et al.}` -- should list all 5 team members by name (or at minimum, the brief says "member bios" so real names are expected somewhere).
5. **NOTE: Several .tex files exist but are not included in main.tex** -- `00_abstract.tex`, `01_introduction.tex` (distinct from `intro_d6.tex`), `02_system_architecture.tex` through `09_simulation.tex`, `15_conclusion.tex`, `introduction.tex`, `steeple.tex`. These appear to be earlier drafts or standalone sections. Confirm they are intentionally excluded.

---

## D7 Individual Reflective Report (50%)

### Format & Structure

- [x] **Single PDF format** -- LaTeX compiles to single PDF
- [ ] **Max 5 pages body** (excl. cover, appendices) -- **ACTION: Compile and verify actual page count.** Report has 5 sections (Introduction, Design/Problem-Solving, Societal/Environmental, Teamwork/Leadership/Communication, Self-Assessment/Development). With 11pt font, 20mm margins, 1.15 line spacing, this is likely 5-6 pages. May be tight. No appendices are included (the brief allows appendices excluded from count, but none are present).
- [x] **Cover page / title block present** -- Lines 102-107 of main.tex

### AHEP4 Standards

- [x] **M5 addressed (Design solutions, STEEPLE)** -- Section 2: "Design and Problem-Solving (M5)". Covers dual-backend architecture, simulation-first development, target localisation, model retraining pipeline, safety-critical design, and STEEPLE considerations. Strong technical depth with specific examples.
- [x] **M7 addressed (Environmental/societal impact)** -- Section 3: "Societal and Environmental Impact (M7)". Covers societal impact (SAR lives saved, surveillance concerns, dual-use dimension with Ukraine context), environmental considerations at three levels (mission/SSSI geofencing, hardware life-cycle/5W Pi, development/simulation reduces physical testing). Life-cycle consideration present as required.
- [x] **M16 addressed (Teamwork, evaluate effectiveness)** -- Section 4: "Teamwork, Leadership, and Communication (M16, M17)". Covers team structure, what worked well, the solo coding reality (honest assessment), managing disagreements (ROS vs MAVLink decision), workload distribution tension, giving/receiving feedback.
- [x] **M17 addressed (Communication evaluation)** -- Section 4 subsection "Communication Methods and Effectiveness". Evaluates 4 methods: simulator demos, written documentation, ground station interface, weekly meetings/presentations. Rates effectiveness of each. Identifies improvement (video walkthroughs).
- [x] **No mention of AI writing tools** -- Grep confirms no mentions of ChatGPT, Claude, Copilot, GPT, LLM, or writing assistant in any .tex file. "Claude" appears only in SCORING_D7.md and TARGET_BRIEF.md (supporting files, not submitted). **PASS (Category 2 Minimal)**

### Rubric Alignment

- [x] **Teamwork** -- Addresses team leadership, conflict management (ROS debate, workload tension), responsiveness to teammates' constraints, feedback exchange. Honest about solo coding reality.
- [x] **Self-management** -- Section 5: time management with weekly milestones, contingency planning (indoor bench tests when weather cancelled), documentation discipline.
- [x] **Insight** -- Section 5: strengths (rapid prototyping, documentation, visual communication), weaknesses (designing for collaboration, speed over inclusion, delayed hardware testing). Concrete 3-item self-development programme with measurable goals. Career connection to Ukraine.

### Content Quality

- [x] **References present** -- references.bib exists. **WARNING: Only 1 citation found in entire D7 report** (`\cite{koopman2019safe}` in Section 2). This is very thin for a 5-page reflective report. Consider adding references for: AHEP4 standards, Sheridan automation levels, SAR operational research, Tuckman team stages, Belbin roles, or other reflective frameworks.
- [x] **Evaluates own AND team effectiveness** -- Honest about uneven workload, identifies what worked and what didn't, evaluates communication methods.
- [x] **Self-development programme** -- 3 concrete actions with specific plans: collaborative architecture design, earlier hardware-in-the-loop testing, verbal communication improvement.

### Issues Found

1. **WARNING: Very few references** -- Only 1 citation in the entire D7 report. Academic reflective reports typically reference frameworks (Belbin, Tuckman, Kolb, Gibbs, AHEP4 itself). Adding 3-5 references would strengthen academic credibility significantly.
2. **WARNING: No appendices** -- The brief allows appendices (excluded from page count). If the 5-page body is tight, evidence could be moved to appendices (e.g., screenshots of ground station, example detection images, timeline Gantt chart).
3. **MINOR: Section mapping to AHEP4** -- M16 and M17 are combined in one section (Section 4). While the content covers both, explicitly separating them or adding clearer sub-headings tied to each standard would make the mapping more obvious to assessors.
4. **MINOR: No cover page** -- The title block is on the first page of content. The brief says "5 pages EXCLUDING cover page" -- adding a separate cover page (university logo, module code, student ID) would be more professional and give slightly more body space.

---

## Summary of Actions Required

### CRITICAL (Must fix before submission)

| # | Report | Issue | Action |
|---|--------|-------|--------|
| 1 | D6 | Placeholder figures | Replace all 3 `\fbox{\parbox{}}` placeholders with real diagrams (architecture, state machine, lawnmower pattern) |
| 2 | D6 | Page count unverified | Compile PDF and count pages in the 15-page body section |
| 3 | D7 | Page count unverified | Compile PDF and count pages (must be <= 5) |

### HIGH (Strongly recommended)

| # | Report | Issue | Action |
|---|--------|-------|--------|
| 4 | D7 | Only 1 citation | Add 3-5 references (AHEP4 document, reflective frameworks, SAR literature) |
| 5 | D6 | Cover page names | Replace "et al." with all 5 team member names |
| 6 | D6 | Path planning depth | Decide: fold `05_path_planning.tex` into system_description, or keep the brief treatment |

### MEDIUM (Recommended)

| # | Report | Issue | Action |
|---|--------|-------|--------|
| 7 | D7 | No separate cover page | Add a cover page with university branding, module code, student ID |
| 8 | D7 | No appendices | Consider adding appendix with evidence (screenshots, detection examples) if body space is tight |
| 9 | D7 | M16/M17 combined | Add clearer sub-headings or separate sections for each AHEP4 standard |

### VERIFIED PASS

| Check | D6 | D7 |
|-------|----|----|
| No AI writing tool mentions | PASS | PASS |
| GitHub link + MIT licence | PASS | N/A |
| STEEPLE analysis | PASS | PASS (in M5) |
| Requirements R01-R12 | PASS | N/A |
| Plus/delta technical eval | PASS | N/A |
| AHEP4 M5 | N/A | PASS |
| AHEP4 M7 | N/A | PASS |
| AHEP4 M16 | N/A | PASS |
| AHEP4 M17 | N/A | PASS |
| Executive summary | PASS | N/A |
| Member bios/roles | PASS | N/A |
| References section | PASS | PASS (but thin) |
