# D7 Rewrite V1 — Summary

**Date:** 2026-04-11
**Branch:** MainWorking4
**Target:** `report/personal_v2/main.pdf`
**Result:** 5 pages, clean compile, 0 errors / 0 LaTeX warnings, bibliography built via biber.

---

## What changed (structural)

1. **Deleted** the five old section files (`01_introduction.tex`, `02_design_problem_solving.tex`, `03_societal_environmental.tex`, `04_teamwork_leadership.tex`, `05_self_development.tex`). These mapped to the D6-style AHEP structure and were the main reason the prior draft scored 42/100.
2. **Created** four new section files matching the Release 2.2 brief §10.1 headings exactly:
   - `sections/01_my_role.tex` — answers Q1a, 1b, 1c
   - `sections/02_my_team.tex` — answers Q2a, 2b, 2c
   - `sections/03_my_impact.tex` — answers Q3a, 3b
   - `sections/04_my_support.tex` — answers Q4a, 4b
3. **Rewrote** `main.tex` preamble for density:
   - `geometry top=1.8cm bottom=1.8cm left=2cm right=2cm`
   - `\setstretch{1.05}`, `\setlength{\parskip}{0.3em}`, `\parindent=0pt`
   - `titlespacing*` compressed for section/subsection
   - `enumitem` global `itemsep=0pt, topsep=2pt, partopsep=0pt`
   - `tabularx` + `\arraystretch{1.05}` + `\footnotesize` for all tables
4. **Added** a rubric mapping table at the top of `main.tex` showing Q → heading → §X → one-line evidence. Proves assessor coverage at a glance.
5. **Added** three bibliography entries for evidence I cite: `complaintletter`, `mainrefactor`, `gpsestaccuracy`.

## Where each of the 10 questions is answered

| Q | Section | Paragraph / cue |
|---|---|---|
| 1a | §1 My role | `\textbf{1a.}` lead paragraph — explicit vs implicit split, Belbin arc |
| 1b | §1 My role | `\textbf{1b.}` two things: simulation framework + IMX296 debugging session |
| 1c | §1 My role | `\textbf{1c.}` less solo building, earlier pair-programming, shared complaint letter |
| 2a | §2 My team | `\textbf{2a.}` wk12 kickoff, wk17 FSM pushback, wk20 re-division |
| 2b | §2 My team | `\textbf{2b.}` ranked list: handoff contracts, Edward pairing, pilot on GS |
| 2c | §2 My team | `\textbf{2c.}` bullets: contribution-design, 2 pairs on SW, shared MEMORY file |
| 3a | §3 My impact | 8-row table of gap → action → measurable outcome (all past tense) |
| 3b | §3 My impact | `\textbf{3b.}` pair-programming, teaching-first docs, lead by proposing not fait-accompli |
| 4a | §4 My support | 5-row table of teammate → action → impact on my work |
| 4b | §4 My support | 6-row table of recipient → action → behaviour change; closing paragraph on feedback given |

## Named teammates

- **Robin** — mission state-machine owner; passive_watch_2 integration, JSON contract, README handoff
- **Demetro** — FDR presenter; 2 slides + 465-word speaking scripts + 4 iterations
- **Edward** — CV/optics calibration; FOV click-calibration pair, lens distortion
- **Pilot** — RC pilot; abort-button feedback, ground-station button layout redesign
- **Project manager** — field slots, risk assessments, docs-too-dense feedback

(5 named teammates; rubric floor was 3.) No external supervisor named — that remains a known gap.

## Dated / anchored incidents

- **wk12** kickoff meeting, roles drawn on whiteboard
- **wk14** docs feedback from PM, `COLLEAGUE_CHECKLIST` created later in response
- **wk16 / ~12 March** flight day 1 cancelled (hardware)
- **wk17** 11-state FSM pushback; main.py refactor 1411 → 754 lines, 146 pytest tests
- **wk18 / ~19 March** flight day 2 cancelled
- **wk20** re-division of work; Robin integration contract; passive_watch_2 built
- **wk20 / 30 April** flight day 3 cancelled
- **wk21** Demetro FDR script polishing, pilot bench walkthroughs
- **wk22** complaint letter iterations; R01–R12 compliance audit; colleague onboarding docs
- Specific commits cited inline: `a5b1ab7, 885cee4, 36b6069, 32fb0c5, b2a9cd4, ba667f2, 26e3255, 4b0fd91, ce5c036, 374a462`, plus the 12-commit tilt compensation saga

## Conflicts managed (named parties + mediating action)

1. **11-state FSM vs simplified FSM (wk17)** — Robin and one other teammate pushed back; I slept on feedback, refactored next day (1411 → 754 lines). Named as "the first time I genuinely changed a technical direction because of team input rather than my own evidence."
2. **ROS 2 vs raw MAVLink** — disagreement with Robin; I "resolved" it by writing a 20-line heartbeat demo overnight. Explicitly self-critiqued in §3b as *persuasion-by-fait-accompli, not leadership*.
3. **Pilot workload and button safety** — pilot flagged dangerous abort/confirm button proximity; I separated controls and added confirmation dialog.
4. **PM feeling sidelined** — PM said docs were too dense; I restructured into one-page quick-ref + colleague checklist (actual remediation, not reassurance).

## Development programme — past tense

Every action in the §3a and §4b tables is past tense with a measurable outcome. Items include: modularity audit 3.8/5.0, capability audit 7.7 vs 2.1, main.py refactor, R01–R12 compliance closure, GPS estimation accuracy progression 7m → 1.5m, simulator build.

## Feedback given to others (for 72+ insight band)

Three explicit instances named in §4b closing paragraph:
1. **Demetro** — told him his FDR slides were reading as a list of components, not a story about uncertainty; rewrote opening. He adopted it.
2. **Robin** — told him we needed to move from "calling each other's functions" to "contracts and JSON." He adopted it; pattern stuck.
3. **Pilot** — told him the ground-station buttons were following my mental model not his hand position; asked him to redesign the layout. He did; I implemented what he drew.

## Voice / tone

- First-person throughout ("I wrote", "I proposed", "I slept on it")
- Short sentences, concrete verbs, named things, dated events
- Complaint-letter thesis woven into §1b ("the only reason this project produced any verifiable engineering output at all")
- Self-critical: §3b explicitly calls out "persuasion by fait-accompli, not leadership" as a failure pattern; §3a closing paragraph acknowledges the simulator does not substitute for real flight data
- No hedged abstractions like "I recognise this as a leadership gap"

## Page count

**5 pages** — exactly at the hard ceiling. No reference page bleeds over (bibliography rendered `heading=none` at tail of §4).

## Density tactics applied

- Compact rubric mapping table in preamble (`\footnotesize`, `tabularx`)
- Three major evidence tables (§3a gap/action/outcome, §4a teammate/action/impact, §4b recipient/action/behaviour-change) all `\footnotesize` + `tabularx` + `\arraystretch{1.05}`
- Inline evidence markers `[commit 26e3255]`, `[wk20]` instead of long footnotes
- Bold lead-in mini-headings (`\textbf{1a.}`, `\textbf{1b.}`) save full heading lines
- `itemsep=0pt, topsep=2pt` everywhere
- Page margins 2cm / 1.8cm

## Known gaps / risks

1. **Supervisor / advisor not named** — Q4a does not name any academic staff support. The rubric does not explicitly require this, but it is a natural absence for a reader to notice.
2. **"Zian" teammate unmentioned** — raw material noted a Zian folder in git status but role was unclear; not cited.
3. **Ukraine framing dropped** — prior draft had a paragraph on Ukraine engineering culture. I kept a short "Strength and Honour" implicit voice but removed the explicit Ukraine paragraph to save space. Consider adding back in a final-pass cut if we recover space.
4. **No figure / photo** — no hardware photo, no screenshot, no diagram. Could add one small figure (simulator god-view screenshot or mission state diagram) if space permits without going over 5 pages. Would probably add 0.2–0.3pp and need a cut elsewhere.
5. **References rendered inline** — only 3 cites actually appear in text. References section is small and could be removed entirely if a reviewer prefers. Keeping it because the complaint-letter cite is load-bearing for §1b and §3a.
6. **Sentence-level polish** — a few paragraphs (§1b "the lesson was bigger than the bug") could be trimmed further; left as is because the voice feels more authentic with them.
7. **Rubric mapping table uses "\S"** symbol which may render slightly differently on different engines — tested with pdflatex + MiKTeX, renders fine.

## PNG filenames (for visual review)

- `report/personal_v2/page-1.png`
- `report/personal_v2/page-2.png`
- `report/personal_v2/page-3.png`
- `report/personal_v2/page-4.png`
- `report/personal_v2/page-5.png`

## Expected score lift (from V1 baseline 42/100)

Based on the D7_SCORING_HARSH.md rubric:
- Hard gates: **all passed** (5 pages, 4 headings, 10/10 questions, specific evidence, first-person voice) — removes the 48-cap
- Teamwork: named teammates + conflicts managed with mediating actions → **62–68 band**
- Self-management: brain-dump/MEMORY/NICE_TO_HAVE/blueprints/unit tests + autonomous initiative (simulator, complaint letter) → **62–72 band**
- Insight: feedback-given-to-others explicit + past-tense development programme + changed-thinking (11-state FSM → simplified) → **68–75 band**

Realistic target: **65–72**. Ceiling of ~75 requires a creative team-restructuring story I don't have authentic material for.
