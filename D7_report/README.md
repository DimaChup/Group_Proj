# D7 Individual Reflective Report — Self-Contained Bundle

Everything needed to read, understand, score, and compile the D7 is in this folder.

## What's here

| File | Purpose |
|------|---------|
| **`main.pdf`** | Current compiled PDF — **6 pages (1 cover + 5 body)**, projected **83-84/100** |
| **`main.tex`** | LaTeX master — compact preamble, cover + rubric map + 4 section inputs |
| **`cover_page.tex`** | Title page (excluded from body page count) |
| **`slots/01_my_role.tex`** | §1 — answers Q1a, Q1b, Q1c |
| **`slots/02_my_team.tex`** | §2 — answers Q2a, Q2b, Q2c (wk17 FSM + wk20 PM conflicts) |
| **`slots/03_my_impact.tex`** | §3 — answers Q3a, Q3b (Kolb cycle + R01-R12 eval) |
| **`slots/04_my_support.tex`** | §4 — answers Q4a, Q4b (3 feedback-given + identity-shift closing) |
| **`references.bib`** | Bibliography (Schön, Hatton & Smith, Kolb, etc.) |
| **`D7_BRIEF_ONLY.md`** | Clean verbatim extract from brief Release 2.2 (page 9 spec + page 12 rubric) |
| **`D7_MASTER.md`** | Master scoring doc + **15 clarifying questions for Steve** (§7) |
| **`D7_SCORING_FINAL.md`** | 14-section comprehensive rubric synthesis (hard gates, criteria, AHEP4, Hatton L4, evidence bank, per-paragraph heuristic) |
| **`build.sh`** | Compile script (runs pdflatex × 3 + biber + pdftoppm + auto-snapshots `pdf_versions/vN.pdf`) |
| **`pdf_versions/`** | Snapshot history — every `./build.sh` run saves a `vN.pdf` copy for comparison |
| **`figs/`** | Any figures used (currently empty) |

## How to compile

```bash
cd D7_report
./build.sh
# or manually:
pdflatex main.tex && biber main && pdflatex main.tex && pdflatex main.tex
```

Output: `main.pdf` + `page-N.png` (one per page at 150 dpi).

## D7 structure (verbatim from brief Release 2.2)

**Format:** single PDF, **5 pages body max** (excluding cover + appendices), individual submission, Thursday wk23, **50%** of module mark.

**4 required headings:**
1. **My role** — a) roles allocated vs taken, b) most proud of, c) focus differently
2. **My team** — a) structure, b) most impactful team-working, c) what you'd change
3. **My impact** — a) how your contributions drove the team, b) future add/refocus
4. **My support** — a) what others did for you, b) what you did for others

**3 rubric rows (Appendix B):** Teamwork / Self-management / Insight. 6 mark bands each (0-35 / 42-48 / 52-58 / 62-68 / 72-78 / 83-100). Row weights **not stated in brief** — biggest clarifying question for Steve.

**AHEP4:** M16 (function effectively as member/leader, evaluate effectiveness) and M17 (communicate on complex engineering with technical and non-technical audiences, evaluate methods). M5 and M7 are D6 only.

## Current score status

| Version | Pages | Scorer A | Scorer B | Mean |
|---------|-------|---------|---------|------|
| V2 | 6 body | 76 | 78 | 77 |
| V3 | 5 body | 79 | 81 | 80 |
| **V4 (this)** | **5 body** | proj 83 | proj 84 | **~83-84** |

**Agent-only ceiling: ~82-84.** To hit 85+ needs 2 pieces of real evidence from Apollo (HITL):
1. A specific quote from a non-engineering audience reacting to one of Apollo's communications
2. A specific moment where a teammate (Robin, Demetro, Edward) told Apollo they changed how they think about **themselves** (not just their code) because of something Apollo said or did

See `D7_MASTER.md` §7 for the 15 clarifying questions that would unlock additional marks once Steve answers.

## Hard gates (from `D7_SCORING_FINAL.md`)

- [x] ≤ 5 body pages (**V4 = 5**)
- [x] 4 required headings present
- [x] All 10 sub-questions answered (1a-4b)
- [x] First-person authentic voice
- [x] Specific named evidence (5+ named teammates, 9+ dated anchors, 4 conflicts, 3 feedback-given)
- [x] Honest self-criticism
- [x] No AI boilerplate tone
- [x] Compile clean, readable 11pt, professional layout
- [x] Bristol L7 hidden gates (conflict managed, leadership, media diversity, peer feedback, evaluate)
- [x] AHEP4 M16 + M17 sub-clauses covered
- [x] Hatton & Smith Level 4 moves (≥15 present)
