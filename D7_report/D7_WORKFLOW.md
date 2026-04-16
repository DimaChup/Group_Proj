# D7 Development Workflow

**Status:** Phase 2 (Goldmine) in progress
**Due:** Thursday wk23 (50% of module)
**Canonical rubric:** `D7_SCORING.md` (1098 lines, 19 sections) — if anything conflicts, this file wins.

---

## Phase 1: Research & Extract (DONE)

- [x] Extract brief verbatim -> `D7_BRIEF_ONLY.md`
- [x] Build scoring rubric -> `D7_SCORING.md` (v5.0, synthesised from brief + AHEP4 + Bristol L7 + Hatton & Smith)
- [x] Extract all Professional Practice lectures (8 extractions across 6 topics):
  - [x] Five Dysfunctions of a Team (`professional_practice/five_dysfunctions/`)
  - [x] Innovation Tools (`professional_practice/innovation_tools/`)
  - [x] Down-selection & Risk (`professional_practice/project_management/1_...`)
  - [x] Project Management 1 (`professional_practice/project_management/2_...`)
  - [x] Project Management 2 (`professional_practice/project_management/3_...`)
  - [x] PM Specialist Session (`professional_practice/project_management/4_...`)
  - [x] Risk & Safety Management (`professional_practice/risk_management/`)
  - [x] Tuckman / Team Development (`professional_practice/team_development/`)
  - [x] Cultural Competence (`professional_practice/working_across_cultures/`)
- [x] Set up build pipeline (`build.sh` — pdflatex x3 + biber + pdftoppm + auto-snapshots)
- [x] Build goldmine V1 (18 pages, unlimited content) -> `goldmine/main.pdf`
- [x] Build strict_A V1 (5pp prose-heavy) -> `strict_A/main.pdf`
- [x] Build strict_B V1 (5pp table-heavy) -> `strict_B/main.pdf`
- [x] Score V1-V4 iterations (V4 = 83-84 projected)
- [ ] **Apollo fills QUESTIONNAIRE_FOR_APOLLO.md** (HITL — NEXT STEP, see below)

---

## Phase 2: Goldmine (IN PROGRESS)

- [ ] **Apollo answers questionnaire** — the 2 critical HITL items:
  1. A specific quote from a **non-engineer** reacting to one of Apollo's communications (M17.c)
  2. A specific moment where a **teammate told Apollo they changed how they think** about themselves (not just their code) because of something Apollo said/did (Insight 70+ gate)
- [ ] Map PP frameworks -> D7 sections (`PP_TO_D7_MAPPING.md`) — which PP concept goes where
- [ ] Rewrite goldmine with Apollo's real answers + PP framework references
- [ ] Score goldmine against `D7_SCORING.md` (full 19-section scorecard)
- [ ] Iterate goldmine until content score 85+
- [ ] Identify which anecdotes/paragraphs are strongest for the 5-page strict versions

---

## Phase 3: Strict versions (AFTER goldmine hits 85+)

- [ ] Compress goldmine -> Strict A (5pp prose-heavy, in `strict_A/`)
- [ ] Compress goldmine -> Strict B (5pp table-heavy, in `strict_B/`)
- [ ] Dual-score both A and B (two independent scoring passes)
- [ ] Pick strongest, iterate on it
- [ ] Run AI detection scan, fix any flagged paragraphs (see D7_SCORING.md §18)
- [ ] Screenshot every page PNG, visual scoring (see D7_SCORING.md §19)
- [ ] Apollo reviews: fills [PLACEHOLDER] tags, adjusts voice, adds personal details

---

## Phase 4: Final polish

- [ ] Apollo final review (voice authenticity, missing personal details)
- [ ] Fill ALL remaining [PLACEHOLDER] tags — none may survive to submission
- [ ] Cover page finalized (`cover_page.tex`)
- [ ] Final compile + AI scan + screenshot every page
- [ ] Dual-score final -> must be 85+ consensus
- [ ] Save final snapshot to `pdf_versions/`
- [ ] Submit single PDF to Blackboard

---

## Per-Iteration Checklist (run EVERY time content changes)

```
1. Compile
   cd D7_report && ./build.sh
   (or: pdflatex main.tex && biber main && pdflatex main.tex && pdflatex main.tex)

2. AI check
   Read ai_check_report.txt (if build.sh generates one)
   -> Must be PASS. Any flagged paragraph -> rewrite per §17.4 humanising rules

3. Page count
   Goldmine: unlimited (working draft)
   Strict A/B: exactly 5 body pages (excl. cover + appendices)
   -> >5 body pages = CAP 48 hard gate

4. Screenshot review
   Read every page-N.png
   Score per §19.2: fill 85-95%, no orphans, no widows, consistent headings
   -> <70% fill on any page = CAP 62

5. Content score (D7_SCORING.md §15)
   Hard gates (§1) -> all PASS?
   Criteria scores: Teamwork / Self-management / Insight (§4)
   AHEP4 sub-clauses /48 (§6)
   10 questions coverage (§3)
   Bristol L7 hidden reqs (§5)
   Level-4 moves count (§7) -> target 10+ total (2/page)
   -> Fill in scorecard template from §15

6. Fix top 3 issues
   Priority: Content (§1-16) > Voice (§17) > Formatting (§19) > AI detection (§18)

7. Re-compile, re-check (repeat steps 1-5)

8. Snapshot
   cp main.pdf pdf_versions/vN.pdf
   (build.sh does this automatically)
```

---

## Directory Structure

```
D7_report/
├── main.tex                    <- LaTeX master (includes cover + 4 slots)
├── main.pdf                    <- Current compiled PDF
├── cover_page.tex              <- Title page (excluded from page count)
├── references.bib              <- Bibliography
├── build.sh                    <- Compile + snapshot script
├── slots/                      <- 4 body sections
│   ├── 01_my_role.tex
│   ├── 02_my_team.tex
│   ├── 03_my_impact.tex
│   └── 04_my_support.tex
├── goldmine/                   <- Unlimited-page working draft (18pp)
│   ├── main.tex
│   ├── main.pdf
│   ├── slots/
│   └── page-*.png
├── strict_A/                   <- 5pp prose-heavy version
│   ├── main.tex, main.pdf, slots/, page-*.png
├── strict_B/                   <- 5pp table-heavy version
│   ├── main.tex, main.pdf, slots/, page-*.png
├── pdf_versions/               <- Snapshot history (v1.pdf, v2.pdf, ...)
├── professional_practice/      <- 8 PP lecture extractions (6 topic folders)
│   ├── five_dysfunctions/      <- Lencioni model
│   ├── innovation_tools/       <- Innovation frameworks
│   ├── project_management/     <- 4 PM lectures (downselection, PM1, PM2, specialist)
│   ├── risk_management/        <- Safety + risk
│   ├── team_development/       <- Tuckman stages
│   └── working_across_cultures/ <- Cultural competence
├── brief_pages/                <- Brief page screenshots (p01-p12.png)
├── figs/                       <- Figures (currently empty)
├── D7_SCORING.md               <- THE canonical rubric (1098 lines, 19 sections) — AUTHORITATIVE
├── D7_BRIEF_ONLY.md            <- Verbatim brief extract
├── D7_MASTER.md                <- Master doc + 15 clarifying questions for Steve
├── D7_SCORING_FINAL.md         <- Archived (superseded by D7_SCORING.md)
├── GAP_HUNTER.md               <- Gap analysis notes
├── VERIFY_A.md / VERIFY_B.md   <- Verification docs
└── README.md                   <- Bundle overview
```

---

## 3 Parallel Tracks

| Track | Location | Purpose | Current state |
|-------|----------|---------|---------------|
| **Goldmine** | `goldmine/` | Unlimited pages, ALL content, ALL frameworks | 18pp, scored ~83-84 |
| **Strict A** | `strict_A/` | 5pp prose-heavy compression | Built, needs re-score after goldmine update |
| **Strict B** | `strict_B/` | 5pp table-heavy compression | Built, needs re-score after goldmine update |

**Flow:** Goldmine (research + write everything) -> Score -> Iterate -> Compress to Strict A+B -> Score both -> Pick best -> Polish -> Submit

---

## Scoring Quick Reference

**Target:** 85+ (current V4 = 83-84, agent ceiling ~82-84 without HITL)

**Hard gates** (any violation caps the mark):
- 5pp body limit -> CAP 48
- 4 required headings -> CAP 58
- 10 questions answered -> -3 per missing
- First-person voice -> CAP 52
- Named specifics (5+ people, 3+ dates, 1+ conflict) -> CAP 58
- Honest weakness -> CAP 58
- Peer feedback given with outcome -> CAP 68 (Insight)
- Non-technical audience named -> part of M17.c

**Priority order:** Content > Voice > Formatting > AI detection

**Top 5 levers:**
1. Peer-development evidence (4b) — Insight 70+ gate
2. M16.d / M17.d evaluate clauses — Master's increment
3. Conflict management specificity — named mechanism, named outcome
4. Leadership threshold — 2/5 test
5. Level-4 Hatton depth — "I now see this is because..." moves, 2+/page

---

## Critical HITL Items (agent cannot fabricate these)

### HITL 1: Non-engineer quote (M17.c)
Apollo needs to provide a real quote or reaction from a non-engineering audience member who received one of his communications. Examples: a pilot he briefed, a supervisor's admin, a family member he explained the project to. Must show 2/5 adaptations (jargon removal, analogy, visual substitution, audience-first structure, feedback loop).

### HITL 2: Teammate self-reflection quote (Insight 70+)
Apollo needs a specific moment where Robin, Demetro, Edward (or another teammate) told him they changed how they think about themselves — not just their code — because of something Apollo said or did. This is the peer-development evidence that unlocks the Insight 70+ band.

**Without these 2 items, the ceiling is ~82-84. With them, 85+ is achievable.**

---

## Agent Rules for D7 Sessions

1. **Read `D7_SCORING.md` first** — it is the ONLY scoring document. Self-contained. If any other doc conflicts, D7_SCORING.md wins.
2. **Never fabricate HITL content** — mark items as [PLACEHOLDER: Apollo to fill] and explain what's needed.
3. **Score after every rewrite** — use the scorecard template from D7_SCORING.md §15.
4. **Check all 20 failure modes** (D7_SCORING.md §8) on every draft.
5. **Voice target: 7-8/10** on the authenticity scale (D7_SCORING.md §17.3). Below 5 = academic integrity risk.
6. **Compile before scoring** — never score LaTeX source, always score the compiled PDF/screenshots.
7. **Update this workflow** when a phase completes or state changes.
