# Writer A — D7 Rewrite Summary

## Output
- **File**: `writer_a_main.tex` (+ 4 section files)
- **Page count**: 7 pages (target hit)
- **Compile**: clean, zero errors, 199 KB PDF
- **PNG renders**: `writer_a_page-1.png` through `writer_a_page-7.png` at 150 dpi

## Approach

Wrote from scratch without reading the existing `sections/*.tex` draft. Treated the D7 as a prose-heavy personal reflection, not a report — short paragraphs, active first-person, dated incidents, named teammates (Robin, Demetro, Edward, Sid), bracketed placeholders where names were unknown.

Structured strictly by the brief's 4 required headings and 10 sub-questions:
1. My role (1a/1b/1c)
2. My team (2a/2b/2c)
3. My impact (3a/3b)
4. My support (4a/4b)

Each sub-question is a labelled subsection so the examiner can check rubric coverage at a glance without hunting through chronological prose.

## How It Hits Each Rubric Criterion

### Teamwork (M16 + Bristol 70+)
- **M16.a individual**: §3a quantifies my own delivery — 820+ commits, 2508-line simulator, 127 unit tests, 12/12 requirements closed in sim, plus the wk18 simulation pivot on the day flight 1 cancelled.
- **M16.b member**: §4a names Edward's mavproxy UDP bridge fix, Sid's single DJI video, Robin's wk17 pushback. §4b names the Robin integration path (`a5b1ab7`), Demetro slide-building.
- **M16.c leader** (safely claimed): complaint letter drafting on behalf of whole team (§1b, §4b); FSM renegotiation with Robin (§2b). Uses ownership language ("I drove", "I built") where leadership threshold not met.
- **M16.d evaluate** (load-bearing Master's increment): §3a uses the R01–R12 matrix as an explicit criterion — judgement (12/12 sim, 4/12 hw), cause (hardware access), lesson (front-load interface contracts). §2a team-level evaluation of the silent drift in wk16.
- **Conflict named** (Bristol 70+ gate): wk17 FSM disagreement with Robin (§2b) — specific mechanism, 24-hour cool-off, compromise commit `a5b1ab7`. Meets the "named mechanism, not better communication" requirement from the exemplar guide.

### Self-management
- §1a: drift narrative under hardware failure; took on 4 roles instead of 1.
- §1b: wk18 simulation pivot, sustained delivery across hardware cancellations.
- §1c: explicit CPD commitments with falsifiable signals (no module >300 lines without walkthrough; observable signal = teammates editing my files).

### Insight (Bristol 80+ gates)
- **Belief revision**: §1c ("preference for writing over talking is a cost-avoidance move"), §2b ("I was right about the FSM and wrong about the context"), §3b ("bias toward full-coverage design is partly a risk-aversion move on my own part"), §4a ("instinct to finish debugging before asking for help is a cost I pay, not a professionalism I exhibit").
- **Feedback given** (Bristol Insight 72+ gate): §4b names specific feedback to Robin on CENTERING state timeout, his reaction, the downstream effect ("looked for that shape of bug"), generalisable lesson ("scarce resource is specificity, not softness").
- **Feedback received**: §2b Robin's FSM pushback, §4b Robin's edit of the complaint-letter drafts.
- **Applied self-development**: §3b references the D7 scoring-rubric iteration pass (68 → 83–84) and the `ce5c036` requirements audit — both structured rubrics I applied to my own work.

### Communication (M17 + Bristol 60+/70+)
- **M17.a complex engineering**: specific artefacts named — `passive_watch_2.py --robin`, `PIXEL_COORD_THRESHOLD`, FSM, geofence `_emergency_rtl`, FOV calibration, tilt compensation.
- **M17.b technical audience**: Robin consumed integration README; Edward reviewed mavproxy workaround.
- **M17.c non-technical audience**: Demetro's FDR speaking scripts (for external guest audience — non-technical), complaint letter (for course organiser / external examiner reader — non-specialist in our codebase), scenario-led framing.
- **M17.d evaluate methods**: §2c enumerates three comms methods and judges them — short Teams message (worked), complaint letter with pre-send call (worked), 3000-word VISION_PIPELINE doc (did not, because no walkthrough). Explicit A/B with criterion (behaviour change).
- **Multi-media** (Bristol 60+ floor): written report, speaking scripts, integration README, slide decks, Teams messages, code comments. Named across §4.

### Decision-making
- Flight-day cancellation as "changing/challenging circumstance" (wk18, explicitly named).
- Evidence-based decisions: simulation pivot, model retraining on single DJI video, FSM scope compromise, god-view optimization tradeoff.

## Strong Points of This Draft
1. **Every reflective paragraph anchors to a specific incident** — wk17 FSM argument, wk18 simulation pivot, complaint letter drafting, Robin's timeout fix. No floating generalities.
2. **Belief-revision moves in every section** — the "I now see this is because..." Hatton & Smith Level 4 move appears 8+ times.
3. **Honest unresolved gaps** — the closing admits I never paired with Edward, the FSM is unmaintainable, and the 12/4 sim/hw split cannot be closed by my code. The exemplar guide explicitly rewards this kind of non-triumphal closing.
4. **Named teammates doing specific things** — Robin pushed back, Demetro accepted my voice, Edward fixed the serial bug, Sid gave us one video. Not "the team".
5. **Falsifiable future commitments** — "no module >300 lines without walkthrough", "state diagrams with >10 states must be reviewed and cut", "observable signal = teammates editing my files". Not "I will communicate better".
6. **Conflict handled without smoothing** — the wk17 FSM disagreement is described with its emotional register preserved ("I took 24 hours to calm down") and its outcome ("I was right about the FSM and wrong about the context").

## Weak Points / Risks
1. **7 pages vs the brief's 5-page limit.** The user asked for 7 working pages but the brief caps D7 at 5. Will need trimming for final submission — suggest cutting §1c paragraph 2 and §2c items 2+3 to fit.
2. **Several `[PLACEHOLDER: ...]` tags** — kickoff date, PM name, hardware-lead name. User needs to fill in before submission.
3. **Demetro as "non-technical audience" is a stretch** — he is an engineering student. The stronger M17.c evidence is the complaint letter (external reader) but that is positioned mainly as a teamwork item. Consider re-framing the complaint letter explicitly as a non-technical comms artefact in a revision.
4. **No citations.** Hatton & Smith / Schön move is mentioned but not cited. A 70+ D7 usually has 2–6 anchoring references. Adding 3 refs (Hatton & Smith 1995, Schön 1983, AHEP4 M16/M17) would lift the insight line without hurting the page count much.
5. **FDR audience adaptation** in §4b is evidenced for Demetro's slides but not shown in before/after prose. The exemplar guide explicitly wants jargon-removal evidence side-by-side.
6. **Commit hashes** appear throughout. Useful for evidence, possibly off-putting to the marker if over-used. May want to move half of them to footnotes.

## Design Choices I Made Independently
- **Structure by sub-question, not by theme.** Chose the rubric-aligned split because a marker with a checklist can tick each question. Risked chronological feel; mitigated by making each subsection thematic.
- **Strong first-person.** Every reflective paragraph has "I" as subject. No "we learned" evasions.
- **Named one specific episode of conflict** rather than several — concentration over breadth. The wk17 FSM argument carries the teamwork-conflict load for the entire report.
- **Named one specific episode of feedback-giving** (Robin's CENTERING timeout bug) — same concentration logic, Insight 72+ gate hit with depth not list.
- **Closed with non-triumph** per the exemplar guide — explicit admission of unfinished business (never paired with Edward, FSM brittle, 4/12 hw gap).
- **Used the complaint letter as the "hardest thing" narrative anchor** — converts an institutional grievance into personal insight about conflict-avoidance masquerading as professionalism. This is the most Level-4 move in the whole draft.

## Predicted Band (self-assessed against the guide's scoring heuristic)
- Estimated sum on the 13-item checklist: 34–38 of 42
- Predicted band: **high 70s** (Distinction, pre-trim)
- Post-trim to 5 pages with refs added: **holds 74–78** if trimming is done carefully on §1c and §2c tail items only.
