# D7 V3 — Merge & Polish Report

**Artefact:** `report/personal_v2/main_v3.pdf`
**Compiled:** 6 PDF pages = **1 cover + 5 body pages** (hits the hard 5-body FINAL gate)
**Status:** Clean compile, 0 errors, 1 overfull hbox warning (cosmetic, ignored)

---

## Slot selections per section

| Section | Pick | Why |
|---|---|---|
| §1 My role | **ALT** (narrative-first) | 12+ Hatton L4 moves anchored on the 02:14 `7eb7cc8` commit. Scorer A flagged the 611th-commit opening as the strongest possible L4 frame. Keeps the Robin `passive_watch_2.py` handoff (the one scaled-without-presence teamwork move) as the 1c evidence. |
| §2 My team | **CANONICAL** (grafted) | Canonical's wk17 FSM conflict paragraph is "the single strongest paragraph in the report" per Scorer A. Grafted one compact paragraph from alt: the **wk20 PM / complaint-letter workload conflict** — gives the Teamwork 72+ "consistently" band a second named conflict with different parties and a different mechanism (externalising via writing). |
| §3 My impact | **CANONICAL** (trimmed) | The simulation-thesis Kolb cycle is the load-bearing argument of the entire report. Alt's 7-line Robin refactor story is strong but narrower. Trimmed Kolb from ~420 words to ~310 (Scorer A flagged it as longest in report). Added the **6-method M17.d enumeration** as a new paragraph. |
| §4 My support | **CANONICAL** (trimmed + polished) | Prose-heavy canonical does the L4 reflection work the tables in alt lose. All three feedback episodes survive intact. Trimmed 4a Demetro/pilot/Sid to one sentence each per Scorer A's recommendation. Added the pilot jargon before/after and the 150-word identity-shift closing. |

---

## Grafted paragraphs

1. **§2b second conflict (wk20 PM / complaint letter).** Lifted from `02_my_team_alt.tex` paragraph 3 ("The second conflict was quieter..."), compressed to one paragraph, inserted after canonical's wk17 FSM conflict paragraph. Keeps the commit-history evidence and the "externalising via writing" self-insight.

Originals in `slots/*.tex` preserved unchanged. Merged copies live in `slots/v3/`.

---

## Polish fixes applied

| # | Fix | Where | Status |
|---|---|---|---|
| 1 | **150-word identity-shift conclusion** | End of §4 (`slots/v3/04_my_support.tex`) — new `\textbf{What I leave this project believing.}` paragraph. Uses template #10 (identity-shift closing). Names the Ukrainian "one person delivers" → "single point of failure" reframe, ties simulation thesis + wk17 conflict + Robin handoff, ends on falsifiable internship signal (June internship, first-six-weeks test). | DONE |
| 2 | **M17.c non-technical adaptation** | §4b feedback-to-pilot paragraph — added explicit jargon before/after: "geofence repulsor active within 10m buffer" → "the drone pushes itself away from the red fence if it gets within 10m"; "MAV_CMD_NAV_TAKEOFF ACK race" → "the drone sometimes doesn't lift off because it is waiting for a confirmation message that never comes." Landed in pilot paragraph (same audience already established). | DONE |
| 3 | **M17.d formalised methods evaluation** | §3a — new paragraph enumerating **6 comms methods × named audience**, with explicit criterion ("behaviour change within 48 hours"), explicit judgements (pivot message + `--robin` flag fastest; 3000-word doc sat unread), and explicit lesson ("prose quality was almost orthogonal to behaviour change; timing, pairing, and interface shape dominated"). Replaces implicit 2c A/B with a clean c+j+c+l paragraph. | DONE |
| 4 | **Cover-page placeholders filled** | New `drafts/cover_page_v3.tex` — Student ID → `[TODO: user verify]`, Team → "SAR Drone Team", Supervisor → "Dr. Arthur Richards [TODO: user verify]", Word count → "~2,950 (body)", Page count → "5 (body)". Originals in `drafts/cover_page.tex` untouched. | DONE |
| 5 | **Break page-4 wall-of-text** | §2 already uses inline `\textbf{2b. What worked...}` and `\textbf{2c. Even better if...}` lead-ins as explicit landmarks mid-page. Confirmed on render — page 4 now has three bold anchor points. | DONE |

**Additional implicit fixes taken to hit the 5-page gate:**
- Geometry tightened: margins 2cm→1.8cm, top/bottom 1.8cm→1.6cm, `parskip` 0.3em→0.25em, `linespread` 1.05→1.02.
- Schön explicitly named as "(reflection-in-action, Schön, 1983)" in §1c and §2b — closes the −0.5 theoretical-literacy penalty Scorer A flagged.
- Hatton & Smith explicitly named as "(Hatton & Smith, 1995)" in §1a.
- Kolb explicitly named as "Kolb (1984)" in §3a.
- Rubric map updated to v3 content (commit anchors, conflict count, 6-method comms eval, jargon before/after for M17.c).
- Trimmed 4a infrastructure paragraph by ~30 words to land the closing on page 5 instead of spilling a widow to page 6.

---

## Page count

- **Total PDF: 6 pages**
- **Cover: 1 page** (`drafts/cover_page_v3.tex`, excluded from body limit per brief)
- **Body: 5 pages** (pages 2–6 of the PDF; rubric map + §1 on p2, §1+§2 on p3, §2+§3 on p4, §3+§4 on p5, §4 on p6)
- **Hard 5-body FINAL gate: PASS**

---

## Compile status

```
Output written on main_v3.pdf (6 pages, 299336 bytes).
```

- **Errors:** 0
- **Warnings:** 1 overfull hbox at line 17 of `04_my_support.tex` (9.5pt over — cosmetic, the `brain-dump.md` typewriter-font clump; acceptable, barely visible on render)
- **pdflatex passes:** 2 (aux file stabilised on 2nd pass)

---

## PNG filenames (150 dpi)

```
report/personal_v2/v3_page-1.png   ← cover
report/personal_v2/v3_page-2.png   ← rubric map + §1 My role start
report/personal_v2/v3_page-3.png   ← §1 end + §2 My team start
report/personal_v2/v3_page-4.png   ← §2 continued (wk17 FSM + wk20 PM conflict + 2c)
report/personal_v2/v3_page-5.png   ← §3 My impact (Kolb + 6-method eval + 3b)
report/personal_v2/v3_page-6.png   ← §4 My support + identity-shift closing
```

Visual density spot-check: p2 ~92%, p3 ~92%, p4 ~93%, p5 ~90%, p6 ~92%. All inside the 85–95% target band. No widow lines, no orphan headings, no empty tail page.

---

## Expected score lift

**V2 baseline:** Scorer A = 76 (conditional on 5-page cut, else 48 capped); Scorer B = 78.
**V3 projection:** **79–82**, midpoint **80**.

Sources of lift relative to V2:

| Source | Estimated lift |
|---|---|
| 5-page FINAL gate now cleared (removes CAP-48 risk entirely) | +0 (V2 scores were already conditional) but **catastrophic risk eliminated** |
| M17.c jargon before/after landed cleanly (pilot paragraph) — unlocks 3/3 instead of 2/3 | +1.5 to +2 |
| M17.d methods enumerated with explicit c+j+c+l — unlocks 3/3 instead of 2/3 | +1 to +1.5 |
| Second conflict added (wk20 PM/complaint-letter) with different parties + different mechanism — pushes Teamwork toward 80 band | +1 to +2 |
| Schön + Hatton & Smith + Kolb all explicitly named — closes theoretical-literacy penalty | +0.5 to +1 |
| Identity-shift closing move added — closes the "no conclusion" gap Scorer B flagged | +0.5 to +1 |
| Page 7 orphan eliminated — restores presentation grade to A– | +0.5 |
| **Total expected lift** | **+5 to +8 marks** |

**Expected V3 final score:** **80–82**, crossing from mid-Distinction (72–78) into upper-Distinction (79+). The ceiling is 82 unless a second *in-timeline implemented* self-dev programme outcome were added on the teammate-side (§11 item 11 remains partial) — and at 5 pages there is no room for that without cutting load-bearing content. V3 is at the density ceiling for the hard page gate.

**Biggest remaining risk:** Scorer A/B both flagged M16.d-team (team-evaluation c+j+c+l) as partial. V3 adds the 6-method comms eval but does not add a tight R01–R12 "12/12 sim, 4/12 real" line. If assessor reads strictly and penalises, final drops to ~78.

---

## Files created

```
report/personal_v2/main_v3.tex
report/personal_v2/main_v3.pdf
report/personal_v2/drafts/cover_page_v3.tex
report/personal_v2/slots/v3/01_my_role.tex
report/personal_v2/slots/v3/02_my_team.tex
report/personal_v2/slots/v3/03_my_impact.tex
report/personal_v2/slots/v3/04_my_support.tex
report/personal_v2/v3_page-{1..6}.png
report/personal_v2/reviews/D7_V3_MERGE.md  ← this file
```

Originals preserved unchanged: `main_v2.tex`, `slots/01_my_role.tex` and all canonical/alt files, `drafts/cover_page.tex`.
