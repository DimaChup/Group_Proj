# Report Writing Session -- Ready-to-Paste Prompt

Copy everything below the line into a new Claude Code session.

---

## Project Context

You are helping write reports for a University of Bristol MSc Group Design Project (AENGM0074). Team of 5 students building an autonomous SAR (Search and Rescue) drone. The drone takes off, flies a lawnmower search pattern, uses onboard YOLOv8/TFLite AI to detect a casualty, centres on target, operator confirms, then lands nearby.

The codebase lives at `c:/Users/Bristol/Desktop/AI for Robotics/v3/`. All report files live under `v3/report/`.

## CRITICAL CONSTRAINT

**DO NOT modify any Python code.** You may ONLY create/edit files inside the `report/` directory. If you need data, metrics, or code snippets from the Python codebase, document what you need and I will get it from my other Claude Code session that handles code/testing work.

## Deliverables

There are TWO graded deliverables, each worth 50% of the module grade:

### D6 -- Group Company Report (50% of grade)
- **Max 15 pages** body (Design Rationale, System Description, Requirements Verification, Evaluation)
- Executive Summary, Introduction, References, Appendices are EXCLUDED from the 15-page count
- Rubric: 40% Specialist Skills & Problem-Solving, 40% Decision Making, 20% Communication
- Current score estimate: **74/100** (see `report/reviews/FINAL_SCORE.md`)
- Main file: `report/main.tex`
- Sections: `report/sections/*.tex`
- Figures: `report/figs/` (generator scripts `gen_*.py` produce PDF/PNG)
- Bibliography: `report/references.bib` and `report/extra_refs.bib`

### D7 -- Individual Reflective Report (50% of grade)
- **Max 5 pages** body
- Sections: Design & Problem-Solving, Societal & Environmental, Teamwork & Leadership, Self-Development
- Main file: `report/personal/main.tex`
- Sections: `report/personal/sections/*.tex`
- Scoring guide: `report/personal/reviews/SCORING_D7.md`

### Team Process Report (part of D7 submission)
- Main file: `report/team/main.tex`
- Sections: `report/team/sections/*.tex`

## Files to Read First

Read these files at the start of the session to understand the project, rubrics, and current state:

1. **Rubric data (structured):**
   - `v3/dashboard/src/pages/group-report-data.ts` -- D6 rubric criteria, weights, what markers want
   - `v3/dashboard/src/pages/individual-report-data.ts` -- D7 rubric criteria

2. **Scoring guides and reviews:**
   - `v3/report/guides/TARGET_BRIEF.md` -- Exactly what markers want, section by section, with page budget
   - `v3/report/reviews/FINAL_SCORE.md` -- Current 74/100 assessment with specific fixes to improve
   - `v3/report/reviews/SCORING_D6_v3.md` -- Detailed D6 scoring analysis
   - `v3/report/guides/CHECKLIST.md` -- Completion checklist against brief requirements
   - `v3/report/guides/GOLDMINE_CHECKLIST.md` -- Comprehensive improvement checklist
   - `v3/report/personal/reviews/SCORING_D7_v2.md` -- D7 scoring analysis

3. **Technical content sources:**
   - `v3/docs/DESIGN_DECISIONS.md` -- Design rationale documentation (DD-01 format, WHY each choice)
   - `v3/docs/LESSONS_LEARNED.md` -- Lessons learned from development and field testing
   - `v3/docs/PROJECT_STATUS.md` -- Current project status and what was achieved
   - `v3/CLAUDE.md` -- Comprehensive project ground truth (architecture, what works, session history)

4. **Report structure:**
   - `v3/report/README.md` -- Directory layout and compilation instructions

## Key Metrics to Include in Reports

These are verified numbers from testing. Use them as evidence throughout:

| Metric | Value | Source |
|--------|-------|--------|
| Model accuracy (mAP50) | 0.995 | Retrained YOLOv8n on 366-image dataset (300 synthetic + 16 real + 50 negatives) |
| Inference speed (Pi 5) | 206.5ms avg, 4.8 FPS | TFLite + XNNPACK CPU, 50-run benchmark |
| Detection confidence | 0.966 | 50/50 detection rate on test images |
| GPS estimation accuracy | CEP50 = 2.3m, max 16.5m | DJI video analysis with FOV-calibrated pipeline |
| FOV calibration | 54.4 deg HFOV | 9 samples across 15-50m altitude, focal length 1416px +/- 41 |
| Lens calibration RMS | 0.399 | Checkerboard calibration, undistortion cost 1.5ms |
| State machine | 20 states, 32 transitions | Full mission: INIT through DONE with manual override |
| Geofence | 4 layers | Flight area boundary, SSSI no-fly zone, repulsive buffer, altitude cap |
| Search pattern | Lawnmower with Bezier smoothing | Complete area coverage, configurable altitude/strip width |
| Test scripts | 41 scripts, 6 categories | Progressive: hardware, flight (numbered 0a-4), diagnostics, calibration, experiments, laptop |
| Training dataset | 366 images at 1456x1088 | 300 synthetic + 16 real labelled + 50 negatives |
| Model size | 3.2MB (TFLite, YOLOv8n) | Input [1,640,640,3], output [1,5,8400] |
| Cube baud rate | 921,600 | Via mavproxy UDP bridge (Python 3.13 serial workaround) |

## Compilation

Each report compiles independently:

```bash
# Group report
cd "c:/Users/Bristol/Desktop/AI for Robotics/v3/report"
pdflatex -interaction=nonstopmode main.tex && biber main && pdflatex main.tex && pdflatex main.tex

# Personal report
cd "c:/Users/Bristol/Desktop/AI for Robotics/v3/report/personal"
pdflatex -interaction=nonstopmode main.tex && biber main && pdflatex main.tex && pdflatex main.tex

# Team report
cd "c:/Users/Bristol/Desktop/AI for Robotics/v3/report/team"
pdflatex -interaction=nonstopmode main.tex && biber main && pdflatex main.tex && pdflatex main.tex
```

## Overleaf Connection

There is also an Overleaf project at `c:/Users/Bristol/Desktop/AI for Robotics/CW Aerial Robitics/overleaf/` which contains earlier versions of the group report. The canonical version is now in `v3/report/`. Do NOT edit the overleaf directory.

## Coordination Protocol

This session handles ONLY report writing. A separate Claude Code session handles code and testing.

- If you need to extract data, metrics, or code snippets from the Python codebase, write a clear request describing exactly what you need (file path, function name, variable, etc.) and I will relay it to the code session.
- If you discover that a figure generator script (`report/figs/gen_*.py`) needs modification, describe what changes are needed and I will handle it in the code session.
- Do not attempt to run Python scripts outside of `report/` -- they may have dependencies not available in this environment.

## Current Priorities (from FINAL_SCORE.md)

The report is at 74/100. Three fixes to push higher:

1. **Replace ALL placeholder figures** with real diagrams (state machine, architecture, CV pipeline, lawnmower pattern). Currently `\fbox{\parbox{}}` placeholders. Impact: +5 to +8 marks.
2. **Add real photos/screenshots** from field testing, Pi hardware, detection overlays, ground station UI.
3. **Tighten evaluation section** with more quantitative plus/delta analysis.

## What You Can Do

- Edit any `.tex` file in `report/`, `report/personal/`, or `report/team/`
- Edit `.bib` bibliography files
- Edit markdown files in `report/reviews/` and `report/guides/`
- Create new `.tex` section files if needed
- Compile reports using pdflatex/biber
- Read any file in the project for reference (but do not modify files outside `report/`)

Start by reading the files listed above, then ask me what to work on first.
