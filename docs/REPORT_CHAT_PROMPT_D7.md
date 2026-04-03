# D7 Individual Reflective Report Session -- Ready-to-Paste Prompt

Copy everything below the line into a new Claude Code session.

---

## Project Context

You are helping write the **D7 Individual Reflective Report** for a University of Bristol MSc Group Design Project (AENGM0074). The student is a Ukrainian robotics student whose team of 5 built an autonomous SAR (Search and Rescue) drone. The drone takes off, flies a lawnmower search pattern, uses onboard YOLOv8/TFLite AI to detect a casualty, centres on target, operator confirms, then lands nearby.

The student was the primary software developer on the team -- responsible for the entire software stack: state machine, computer vision pipeline, ground station, testing framework, simulation environment, and documentation system. The other team members handled hardware assembly, wiring, project management, and pilot duties.

The codebase lives at `c:/Users/Bristol/Desktop/AI for Robotics/v3/`. The D7 report files live under `v3/report/personal/`.

## CRITICAL CONSTRAINT

**DO NOT modify any Python code.** You may ONLY create/edit files inside `report/personal/`. If you need project evidence, tell me what you need and I will get it.

## Scope: D7 Only

This session is ONLY for the D7 individual reflective report. Do NOT work on the D6 group report or the team process report.

- Main file: `report/personal/main.tex`
- Sections: `report/personal/sections/*.tex`
  - `01_introduction.tex`
  - `02_design_problem_solving.tex`
  - `03_societal_environmental.tex`
  - `04_teamwork_leadership.tex`
  - `05_self_development.tex`

## Page Budget: 5 pages max (excluding cover page and appendices)

Every sentence must earn its place. This is a reflective report, not a technical report -- it is about YOU, not the system. Use the system as evidence for personal growth claims.

## Rubric Criteria (three assessed areas)

### 1. Teamwork (M16) -- currently scoring 78/100

**What the rubric demands at top band:**
"Outstanding ability to work and lead a team with creativity and flexibility responsive to group members' interests and the obligations and goals of the team. Able to manage conflict."

**What is currently weak:**
- Flexibility reads as accommodation ("I adapted my schedule"), not creative adaptation where team input changed YOUR approach
- Conflict management is thin -- the ROS 2 disagreement was resolved by demonstration (you won). Need genuine compromise examples
- "Receiving feedback" examples are limited to one button layout change
- Need moments where team input changed your technical direction

**To push to 83+:** Show a moment where you gave ground on something you believed in. Show genuine negotiation. Deepen examples of receiving and acting on feedback about your communication style or pace.

### 2. Self-Management (M17) -- currently scoring 82/100

**What the rubric demands at top band:**
"Works autonomously demonstrating outstanding self-organisational skills and behaviours. Has a professional attitude to completing all tasks."

**What is currently weak:**
- No quantified effort (hours per week, comparison to teammates)
- Version control discipline (feature branches, progressive commits) is evidence left on the table
- Everything sounds smooth -- where did self-management FAIL and how did you recover?

**To push to 83+:** Add a concrete self-management failure and recovery (underestimating integration time, missing a deadline). Show the correction mechanism, not just the plan.

### 3. Insight (M5/M7) -- currently scoring 79/100

**What the rubric demands at top band:**
"Shows confidence in working autonomously and setting own goals. Can assess own strengths and weaknesses. Able to identify and implement an effective programme of self-development. Can provide effective feedback to others."

**What is currently weak:**
- Forward-looking development actions lack evidence of ALREADY implementing them
- Feedback to others is about correcting work, not developing people
- Self-assessment relies on introspection -- where is external validation?
- "Rapid prototyping" as a strength is also a weakness (speed over inclusion) -- connect them

**To push to 83+:** Show evidence of helping teammates develop (not just correcting work). Validate self-assessment with external input. Connect strengths and weaknesses as two sides of the same trait.

## AHEP4 Standards (must explicitly address all four)

| Standard | What to Cover |
|----------|---------------|
| **M5** -- Design with originality | Dual-backend CV, simulation-first methodology, auto-detecting config, progressive testing. STEEPLE must be specific to YOUR system (not generic). Address diversity/inclusion (currently missing). |
| **M7** -- Environmental & societal impact | Full lifecycle: manufacturing, deployment, disposal. Quantify where possible (simulation replaced ~50 physical flights, 3.2MB model vs cloud inference). Dual-use discussion should be personal and honest. |
| **M16** -- Team effectiveness | Own + team evaluation. Honest workload distribution. Plus/delta format. What would you do differently? |
| **M17** -- Communication methods | GitHub, documentation suite (16+ docs), web ground station, presentations, live demos. Evaluate which worked and which did not. |

## Files to Read First

1. **Current report sections:**
   - `v3/report/personal/main.tex`
   - `v3/report/personal/sections/01_introduction.tex`
   - `v3/report/personal/sections/02_design_problem_solving.tex`
   - `v3/report/personal/sections/03_societal_environmental.tex`
   - `v3/report/personal/sections/04_teamwork_leadership.tex`
   - `v3/report/personal/sections/05_self_development.tex`

2. **Scoring and rubric:**
   - `v3/report/personal/reviews/SCORING_D7_v2.md` -- detailed scoring with specific improvement advice per criterion
   - `v3/report/personal/reviews/TARGET_BRIEF.md` -- what markers want at 75+ level

3. **Evidence sources (read for specific examples to use):**
   - `v3/docs/LESSONS_LEARNED.md` -- development and field testing lessons, setbacks, recoveries
   - `v3/docs/DESIGN_DECISIONS.md` -- DD-01 format decisions showing rationale and trade-offs
   - `v3/CLAUDE.md` -- comprehensive project history, session log, what works, architecture
   - `v3/docs/ROADMAP.md` -- 10-phase development history showing progression

4. **Rubric data (structured):**
   - `v3/dashboard/src/pages/individual-report-data.ts`

## Writing Guidelines

- **This is a reflective report.** First person. Honest. Self-critical. Not a technical manual.
- **Every claim needs evidence.** "I showed leadership" is worthless. "I created a 10-phase progressive testing methodology because the team had never flown a custom drone before" is evidence.
- **Be specific about failures.** The rubric rewards honest self-assessment more than listing achievements. The BGR/RGB camera bug that took hours to find, the Python 3.13 incompatibility discovered on Pi, the weather cancelling flight day -- these are BETTER material than things that went smoothly.
- **Connect personal growth to the project.** The student's career goal is helping Ukraine through robotics/technology. The SAR drone project connects directly to this. Use it.
- **Strengths and weaknesses are two sides of the same coin.** "Rapid prototyping" = strength (fast iteration) AND weakness (speed over inclusion, building solo instead of delegating). Show this duality.
- **Do not pad.** 5 pages is tight. Every paragraph must serve a rubric criterion. Cut anything that reads like a project summary -- that belongs in D6.

## User Context

The student is Ukrainian, studying MSc at University of Bristol. Priority: finish university and build a career helping Ukraine. Activities outside uni: boxing, drumming, capoeira, salsa, reading. Writes with heavy typos -- interpret generously and preserve all ideas. Motto: Strength and Honour.

## Compilation

```bash
cd "c:/Users/Bristol/Desktop/AI for Robotics/v3/report/personal"
pdflatex -interaction=nonstopmode main.tex && biber main && pdflatex -interaction=nonstopmode main.tex && pdflatex -interaction=nonstopmode main.tex
```

## What You Can Do

- Edit any `.tex` file in `report/personal/` and `report/personal/sections/`
- Edit `.bib` bibliography files in `report/personal/`
- Edit markdown files in `report/personal/reviews/`
- Create new `.tex` section files in `report/personal/sections/` if needed
- Run `pdflatex` / `biber` to compile
- Read any file in `v3/` for reference (but do NOT modify files outside `report/personal/`)

## What You Must NOT Do

- Do NOT modify any Python code (`.py` files) anywhere
- Do NOT modify files outside `report/personal/`
- Do NOT work on D6 (group report) or team process report
- Do NOT exceed 5 pages for the body sections
- Do NOT write generic reflections -- every statement must be grounded in project-specific evidence
- Do NOT summarise the technical system -- that is D6's job. This report is about YOU

## Coordination

If you need project evidence (code structure, test results, session history, design decisions):
- Describe what you need and I will get it from the codebase or my other Claude Code session
- Do not attempt to run Python scripts

Start by reading all the files listed above, then tell me the current state of each section and where the biggest scoring opportunities are.
