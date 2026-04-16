# Writer C — D7 V2 Rewrite Summary

**Date:** 2026-04-12
**Branch:** MainWorking4
**Target:** `report/personal_v2/main.pdf` (Writer C)
**Result:** 7 pages main body, clean compile, bibliography built via biber, 19 numbered references.

---

## Brief recap

Asked to evolve the existing V1 rewrite in `sections/01-04.tex` to fix 7 known
gaps, expand from 5 to 7 working pages with **depth not padding**, hit Hatton &
Smith Level-4 reflection throughout, diversify media evidence for M17, and add
inline rubric tags for the assessor.

---

## Gaps fixed (against V1 known-gaps list)

| # | Gap (V1) | Fix in V2 (writer C) |
|---|---|---|
| 1 | Supervisor / advisor not named | Added in §1a (milestone feedback at PDR/IDR/FDR, no day-to-day visibility of load concentration) and as a dedicated row in §4a table (the "evaluation story" comment that reframed the final deliverables) |
| 2 | Zian (5th/6th teammate) unmentioned | Added in §2a (wk18 late arrival, mechanical/CAD, no direct SW collaboration — explicitly cited as evidence for the §3b problem) and as a dedicated row in §4a table (unblocked a week of Edward's optics attention) |
| 3 | Ukraine culture paragraph dropped | Reinstated in §1a as "The cultural frame I brought, and what it cost me" — frames the Ukrainian solo-problem-solver disposition as the through-line strength/weakness of the whole report |
| 4 | Only 3 inline citations | Expanded to **19 unique cited references** including Hatton & Smith 1995, Moon 2004, Schön 1983, Edmondson 1999, Tuckman 1965, Belbin 2010, McConnell 2004, Leveson 2011, hattonsmith1995 used verbatim as reflection theory anchor |
| 5 | Insufficient Hatton Level-4 depth | Every sub-section now contains at least one explicit "I now see this is because..." reframing move (§1a x2, §1b x1, §1c x1, §2a x2, §2b x1, §2c x1, §3a x1, §3b x2, §4a x1). Also added: "The uncomfortable realisation was that..." (§1a), "I initially framed X — in fact it was Y, and I now see I preferred the X framing because..." (§2a), "The tension between two values I had not previously noticed in myself..." (§3b closing). |
| 6 | Possible Communication 59 cap — insufficient media diversity | Complete overhaul of §4b. Restructured table to make **Medium** its own explicit column (7 distinct media enumerated: Markdown prose, JSON schema + CLI contract, running demo, browser GUI, HTML slides + teleprompter, formal letter, face-to-face walkthrough). Added an explicit M17.d **evaluation of methods** paragraph with criterion, judgement per method, comparison, and lesson. Added an explicit **non-technical audience** paragraph (pilot + PM) with adaptation evidence and feedback loop. Added a dedicated "next cohort" row for the colleague onboarding docs as different-audience communication. |
| 7 | Page 5 bottom whitespace | Fixed by expansion to 7pp — every page now fills. Page 7 carries the full bibliography in 2-col layout, plus the closing paragraph of §4. |

## Structural improvements beyond the gap list

- **Five phrase templates from D7_EXEMPLARS §14 used literally:**
  1. "The uncomfortable realisation was that..." — §1a closing
  2. "I initially framed X — in fact it was Y, and I now see I preferred the X framing because..." — §2a wk17 FSM pushback
  3. "What looked like a technical problem was actually a [trust-and-authority] problem, because..." — §2b handoff contracts
  4. "The tension between my commitment to [delivering] and my commitment to [developing people] surfaced in..." — §3b closing (self-discovery move)
  5. "I leave this project believing that engineering leadership is less about X and more about Y. The moment this became clear to me was [specific incident]." — §4 closing (identity-shift close)

- **Inline rubric tags**: added an `\rtag{...}` command and used it in-line at the head of every sub-section so the assessor can see rubric coverage at a glance — `[M16.a]`, `[M16.b]`, `[M16.c]`, `[M16.d-own]`, `[M16.d-team]`, `[M17.a]`, `[M17.b]`, `[M17.c]`, `[M17.d]`, `[Insight 70+]`. Colour-matched to section heading blue.

- **WWW / EBI mini-table** used as italic in-paragraph framing in §1b (not a separate table) — satisfies the brief's explicit permission of that frame without costing a full table block.

- **Conflict management** named explicitly and enumerated (§2c) — three episodes, three different resolution mechanisms, honest self-criticism that only case (3) actually listened to the specific concern as stated. Hits Bristol Teamwork 62+ floor and Bristol Decision-making 62+ floor.

- **Named self-development programme** (§4b closing) — falsifiable, started inside project timeline (Schön wk18, Edmondson wk21, McConnell next), with an observable six-month falsifiability test ("if I cannot point to a teammate who can do a piece of my job without me, the programme has failed"). Hits Insight 70+ "implement an effective programme of self-development".

- **Feedback given** block (§4b) — three named instances with self-critique of delivery, not just outcome. Hits Insight 72+ "provide effective feedback to others to aid their self-development".

- **Self-evaluation paragraph with criterion + judgement + cause + lesson** (§3a closing) — evaluates own performance against the brief's D-deliverables and R-requirements, reports 9/10 deliverables on time, 12/12 R's met in sim / 0/12 in air, and extracts a forward-looking procedural lesson ("rebuild the test ladder so every R-requirement has a bench-executable test script by default").

## Scanned against the D7_EXEMPLARS 20 failure modes

No chronological trap (structure is thematic, bound by the brief's four-section schema). No teamwork platitudes. No hidden self-praise. No unsupported leadership claims (uses "I owned" and "I was responsible for"; only claims "leadership" in the negative case where I explicitly label ROS2-vs-MAVLink as *persuasion by fait-accompli, not leadership*). Conflict is named three times. Feedback given is in first-person singular, specific, with named recipient and honest reception. Bullet lists kept short (≤4 items). No "This report will..." opener. No triumphalism. Bibliography is used (Schön, Edmondson, Moon, Hatton & Smith) as reflection anchors, not decoration.

## Page structure (7 pages main body)

1. **Page 1** — Title block, compact rubric one-liner, §1 My role 1a (explicit/implicit split, supervisor mention, Belbin arc, Ukraine cultural frame, solo-strength-as-SPOF thesis), start of 1b
2. **Page 2** — §1 My role 1b (simulator thesis + IMX296 debug), WWW/EBI, 1c, §2 My team 2a (Zian, wk12/17/18/20, Tuckman, McConnell-readability frame)
3. **Page 3** — §2 My team 2b (4 ranked items incl. Edmondson psych safety), 2c (bullets), conflict management episodes named
4. **Page 4** — §3 My impact 3a (8-row gap/action/outcome table + Leveson citation + self-evaluation paragraph)
5. **Page 5** — §3 My impact 3b (bullets + values-tension closing), §4 My support 4a (7-row teammate table incl. Zian + supervisor)
6. **Page 6** — §4 My support 4b (7-row recipient/medium table + M17.d evaluation + non-technical audience paragraph)
7. **Page 7** — §4 My support feedback-given paragraph + self-development programme + closing, two-column bibliography (19 refs)

## Density tactics applied

- Margins tightened to `top=1.5cm bottom=1.5cm left=1.7cm right=1.7cm`
- `\setstretch{1.0}`, `\parskip=0.15em`, `\parindent=0pt`
- Bibliography in two columns via `multicols`, `\scriptsize` bib font
- All tables `\footnotesize` + `tabularx` + `arraystretch=1.05`
- Compact rubric coverage line in preamble (replaces full table, saves 0.4pp, still proves coverage)
- Inline `\rtag` command — footnotesize sans-serif blue — minimal visual weight

## Named evidence items checklist (from D7_AHEP4_GUIDE §11 — minimum 12 for a 70+ mark)

| # | Required item | Where |
|---|---|---|
| 1 | Quantified individual-delivery metric | §1a (line counts), §3a (commits, refactor 1411→754, 146 tests, 7m→1.5m GPS error) |
| 2 | Cross-team collaboration with named interface | §2b Edward pairing (FOV derivation), §3a Robin JSON schema |
| 3 | Decision under uncertainty | §3a flight cancellation → bench-first R-gap closure, §2a wk17 FSM refactor |
| 4 | Conflict episode with resolution | §2c three episodes (FSM, ROS2 vs MAVLink, pilot buttons) |
| 5 | Self-evaluation paragraph (criterion + judgement + cause + lesson) | §3a closing ("Evaluating my own performance against a criterion") |
| 6 | Team-evaluation paragraph (same structure) | §3a closing ("What I would not want the reader to mistake" + capability audit 7.7/2.1), §2c bullets with velocity 9→4 causal signature |
| 7 | Two distinct media with audience named | §4b table with **seven** media enumerated |
| 8 | Non-technical audience with adaptation evidenced | §4b dedicated "non-technical audience" paragraph (pilot + PM, jargon removal, button spacing, one-page quick-ref, verbal brief) |
| 9 | A/B or before/after comparison of methods | §4b M17.d evaluation — same underlying content (drone pipeline) as Markdown vs GUI+JSON contract |
| 10 | Peer-development action | §4b Edward tool (now owns FOV maintenance), Robin contract, colleague onboarding docs |
| 11 | Applied lesson with measurable outcome inside timeline | §3a R-gap closure one session, §4a PM feedback → COLLEAGUE_CHECKLIST |
| 12 | Forward-looking CPD/career plan tied to weakness | §4b self-development programme (a–d with falsifiability test) |

All 12 load-bearing items present. Items 5, 6, 8, 9 (the four load-bearing ones per the AHEP4 guide) are all explicit.

## Named teammates

- **Robin** — mission state-machine owner; FSM pushback; JSON contract recipient
- **Demetro** — FDR presenter; HTML slides + teleprompter speaking script
- **Edward** — CV/optics calibration; FOV pairing; now owns FOV tool
- **Pilot** — RC pilot + non-technical audience; abort-button feedback; redesigned the button layout on paper
- **Project manager** — logistics; "docs too dense" feedback; non-technical audience for one-pager
- **Zian** — late-arriving (wk18) mechanical/CAD; not directly collaborated with (absence cited as evidence)
- **Academic supervisor** — PDR/IDR/FDR milestone feedback, notably the "evaluation story stronger than build story" remark

**7 named people.** Rubric floor was 3 and V1 had 5.

## Compile

```
pdflatex main.tex
biber main
pdflatex main.tex
pdflatex main.tex
```

Result: `main.pdf`, 7 pages, 471 KB. No LaTeX errors. One residual `Warning: undefined references` (non-fatal, resolves after second biber+pdflatex cycle in the build — final pdf has all refs resolved).

Rendered at 150 dpi to `page-1.png` through `page-7.png`.

## Files changed

- `main.tex` — preamble density tightened, rubric table replaced with compact one-liner, `\rtag` command added, bibliography moved to 2-col
- `sections/01_my_role.tex` — fully expanded with supervisor, Ukraine frame, Hatton & Smith reframing moves, WWW/EBI, NSPE ethics frame (later pruned back to fit 7pp)
- `sections/02_my_team.tex` — Zian added, Tuckman framing, McConnell readability frame, Edmondson psych safety as 4th impact item, conflict management enumerated
- `sections/03_my_impact.tex` — Leveson safety framing, self-evaluation paragraph with criterion, values-tension closing
- `sections/04_my_support.tex` — 7-row teammate table (adds Zian + supervisor), restructured 4b table with explicit medium column, M17.d method evaluation, non-technical audience paragraph, feedback-given with delivery self-critique, named falsifiable self-development programme, compact closing
- `references.bib` — added hattonsmith1995, moon2004, edmondson1999psychsafety, robinhandoff (others left in place; only cited entries print via biblatex sorting=none)

## Drafts folder outputs

- `drafts/writer_c_main.pdf` — 7-page compiled PDF
- `drafts/writer_c_page-{1..7}.png` — 150 dpi page renders

## Realistic expected score (vs V1 baseline 65–72 band)

- **Teamwork**: conflicts named + leadership-vs-not-leadership honesty + psychological safety evidence → **68–74 band** (up from 62–68)
- **Self-management**: simulator autonomy + falsifiable development programme + inside-timeline applied lessons (R-gap session, test-ladder rebuild) → **70–76 band**
- **Insight**: feedback-given with delivery self-critique + explicit values-tension discovery + Hatton & Smith reframing throughout + forward-looking falsifiability tests → **72–78 band**
- **Communication (Bristol line, tracked independently because of Appendix B layering)**: 7 distinct media named with per-method M17.d evaluation + non-technical audience paragraph with adaptation evidence → **lifts the Communication 59 cap**, realistic **65–72 band**

Target overall mark: **72–78**. Ceiling of 80+ requires live-flight photo evidence and a more substantial peer-development outcome trace that I cannot honestly produce. Floor is 68.

## Known residual risks

1. **7 pages over the 5-page cap** — deliberate, user-instructed, documented here as an informed decision. If the assessor is strict on page count this is a rubric hit; if they read for content depth (which the p9 brief encourages via "free to discuss specifics") the extra depth should net positive.
2. **Bibliography uses a subset of bib entries** — `biblatex sorting=none` only prints cited entries so the references list shows only the 19 anchors actually used.
3. **No hardware photos / simulator screenshots** — would add Bristol Communication "engaging/professional manner" evidence for 80+. Could be added as an **appendix** (appendices excluded from page count per p9) in a follow-up pass.
4. **Rubric tags `\rtag{...}`** — assessor may read these as clutter rather than scaffolding. Easy to hide via `\renewcommand{\rtag}[1]{}` in the preamble if that call is made.
