# D6 Group Report Session -- Ready-to-Paste Prompt

Copy everything below the line into a new Claude Code session.

---

## Project Context

You are helping write the **D6 Group Company Report** for a University of Bristol MSc Group Design Project (AENGM0074). Team of 5 students building an autonomous SAR (Search and Rescue) drone. The drone takes off, flies a lawnmower search pattern, uses onboard YOLOv8/TFLite AI to detect a casualty, centres on target, operator confirms, then lands nearby.

The codebase lives at `c:/Users/Bristol/Desktop/AI for Robotics/v3/`. All report files live under `v3/report/`.

## CRITICAL CONSTRAINT

**DO NOT modify any Python code.** You may ONLY create/edit files inside the `report/` directory. Do not touch anything outside `report/`. If you need data, metrics, or code snippets from the Python codebase, tell me what you need and I will get it.

## Scope: D6 Only

This session is ONLY for the D6 group report. Do NOT work on the D7 individual report or the team process report. Those have separate sessions.

- Main file: `report/main.tex`
- Sections: `report/sections/*.tex`
- Figures: `report/figs/` (generator scripts `gen_*.py` produce PDF/PNG)
- Bibliography: `report/references.bib` and `report/extra_refs.bib`

## Page Budget (15 pages total, excluding exec summary/intro/references/appendices)

| Section | Pages | File |
|---------|-------|------|
| Design Rationale | 4 | `report/sections/design_rationale.tex` |
| System Description | 4 | `report/sections/system_description.tex` |
| Requirements Verification | 4 | `report/sections/requirements_verification.tex` |
| Evaluation | 3 | `report/sections/evaluation.tex` |

Additional standalone section files exist in `report/sections/` (e.g., `04_computer_vision.tex`, `05_path_planning.tex`, `06_state_machine.tex`, etc.) -- these contain deep technical content that may be `\input{}` into the four main sections or used as appendices. Check `main.tex` to see what is currently included.

## Rubric (how this is graded)

| Criterion | Weight | What Markers Want |
|-----------|--------|-------------------|
| **Specialist Skills & Problem-Solving** | 40% | Comprehensive system with initiative and autonomy. Show creativity in design, evidence the system works (benchmarks, test results, photos). Biggest weakness: no outdoor flight data -- mitigate by showing extensive simulation + bench testing + field day results. |
| **Decision Making** | 40% | Evidence-based decisions throughout. MCDA trade studies with explicit weights. STEEPLE analysis that is specific to YOUR system (not generic). Decisions should feel genuinely evaluated, not post-hoc justified. |
| **Communication** | 20% | Professional structure, real figures (NOT placeholder boxes), clear equations, good use of tables. "Innovative techniques and resources" means actual diagrams, photos, screenshots -- not `\fbox{\parbox{}}` placeholders. |

## Current Score and Priorities

Current estimate: **74/100** (solid first-class, but not top band).

Three fixes to push higher (from `report/reviews/FINAL_SCORE.md`):

1. **Replace ALL placeholder figures** with real diagrams (state machine, architecture, CV pipeline, lawnmower pattern, drone photos, ground station screenshots). Impact: +5 to +8 marks on Communication.
2. **Ensure path planning content is included** in the compiled report. `05_path_planning.tex` has strong content (rotated-mask algorithm, energy analysis, Bezier smoothing, 216-config parametric sweep) that may not be `\input{}`-ed in `main.tex`.
3. **Tighten evaluation section** with more quantitative plus/delta analysis and honest assessment of what was not achieved (no outdoor flight).

## Files to Read First

Read these at the start of the session:

1. **Report structure:** `v3/report/README.md` -- directory layout and compilation
2. **Current report:** `v3/report/main.tex` -- see what sections are included
3. **Scoring:** `v3/report/reviews/FINAL_SCORE.md` -- current 74/100 with specific fixes
4. **Target brief:** `v3/report/guides/TARGET_BRIEF.md` -- what markers want, section by section
5. **Checklists:**
   - `v3/report/guides/CHECKLIST.md` -- completion against brief requirements
   - `v3/report/guides/GOLDMINE_CHECKLIST.md` -- comprehensive improvement checklist
6. **Rubric data (structured):** `v3/dashboard/src/pages/group-report-data.ts`
7. **Design decisions:** `v3/docs/DESIGN_DECISIONS.md` -- DD-01 format, WHY each choice
8. **Lessons learned:** `v3/docs/LESSONS_LEARNED.md` -- development and field testing insights
9. **Project ground truth:** `v3/CLAUDE.md` -- architecture, what works, session history, key metrics

## Key Metrics (verified numbers -- use as evidence)

| Metric | Value | Source |
|--------|-------|--------|
| Model accuracy (mAP50) | 0.995 | Retrained YOLOv8n on 366-image dataset |
| Inference speed (Pi 5) | 206.5ms avg, 4.8 FPS | TFLite + XNNPACK CPU, 50-run benchmark |
| Detection confidence | 0.966 | 50/50 detection rate on test images |
| GPS estimation accuracy | CEP50 = 2.3m, max 16.5m | DJI video analysis with calibrated pipeline |
| FOV calibration | 54.4 deg HFOV | 9 samples across 15-50m altitude |
| Lens calibration RMS | 0.399 | Checkerboard calibration, 1.5ms undistortion cost |
| State machine | 20 states, 32 transitions | Full mission with manual override |
| Geofence | 4 layers | Flight area, SSSI NFZ, repulsive buffer, alt cap |
| Search pattern | Lawnmower + Bezier smoothing | Complete area coverage |
| Test scripts | 41 scripts, 6 categories | Progressive: hardware -> flight -> autonomous |
| Training dataset | 366 images at 1456x1088 | 300 synthetic + 16 real + 50 negatives |
| Model size | 3.2MB TFLite (YOLOv8n) | Input [1,640,640,3], output [1,5,8400] |

## Compilation

```bash
cd "c:/Users/Bristol/Desktop/AI for Robotics/v3/report"
pdflatex -interaction=nonstopmode main.tex && biber main && pdflatex -interaction=nonstopmode main.tex && pdflatex -interaction=nonstopmode main.tex
```

Run this after every significant edit to verify the PDF compiles cleanly. Check for overfull hboxes, missing references, and page count.

## What You Can Do

- Edit any `.tex` file in `report/` and `report/sections/`
- Edit `.bib` bibliography files
- Edit markdown files in `report/reviews/` and `report/guides/`
- Create new `.tex` section files if needed
- Run `pdflatex` / `biber` to compile
- Read any file in `v3/` for reference (but do NOT modify files outside `report/`)

## What You Must NOT Do

- Do NOT modify any Python code (`.py` files) anywhere
- Do NOT modify files outside `report/`
- Do NOT work on D7 (individual reflective) or team process report
- Do NOT exceed 15 pages for the four main body sections
- Do NOT leave placeholder figures -- every `\fbox{\parbox{}}` must be replaced with a real figure or removed

## Coordination

If you need something from outside `report/`:
- Code snippets, metrics, or test results from the Python codebase -- describe what you need and I will get it
- Figure generation scripts (`report/figs/gen_*.py`) need modification -- describe the changes and I will handle them
- Do not attempt to run Python scripts outside `report/`

Start by reading the files listed above, then tell me what you see and ask what to work on first.
