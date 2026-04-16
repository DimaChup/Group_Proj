# Writer B — D7 Draft Summary

**Files produced:**
- `writer_b_main.tex` — compact preamble (geometry 2cm, parskip 0.3em, linespread 1.05, 11pt), rubric mapping table at top, `\input{}` of four sections
- `writer_b_my_role.tex` (§1, Q1a–c)
- `writer_b_my_team.tex` (§2, Q2a–c) + feedback evidence table
- `writer_b_my_impact.tex` (§3, Q3a–b) + Kolb deep-dive + self-development actions table
- `writer_b_my_support.tex` (§4, Q4a–b) + M17.d method-effectiveness evaluation + conclusion
- `writer_b_main.pdf` — **6 pages** (working target was 7, under budget)
- `writer_b_page-1.png` … `writer_b_page-6.png` — 120 dpi renders

## Approach (explicitly different from Writer A)

| Device | How Writer B uses it |
|---|---|
| **STAR per anecdote** | Every concrete story is explicitly Situation / Task / Action / Result with active-voice "I did X". 9 STAR anecdotes total. |
| **WWW / EBI sub-tags** | Each sub-question opens with `\www` ("What went well.") and most close with `\ebi` ("Even better if."). Italicised inline — signals rubric vocabulary without eating headings. |
| **Inline rubric margin tags** | `\rtag{1a}` etc. — small red margin markers next to each sub-question so the marker can find Q1a, Q1b … Q4b instantly. |
| **Compact evidence tables** | 3 tables total: (i) top-of-doc rubric mapping table, (ii) feedback given/received log in §2, (iii) self-development actions log in §3. Each collapses 400+ words of narrative into 5–7 rows. |
| **One full Kolb deep-dive** | §3a contains a single named 4-stage walkthrough of the simulator-solo story, each stage in italics: *concrete experience* → *reflective observation* → *abstract conceptualisation* → *active experimentation*. ~200 words. |
| **Schön label — once** | §1c tags the IMX296 BGR 6-permutation debugging as "a *Schön reflection-in-action* moment" — single inline mention, no expansion. |
| **Team-performance evaluation** | §3a explicitly names criterion, judgement, cause, lesson applied in-project (M16.d). |
| **Method-effectiveness evaluation** | §4b closing paragraph enumerates 5 media (prose, simulator demo, blueprints, teammate READMEs, complaint letter) and judges each against time-to-understanding (M17.d). |

## Rubric hit list (AHEP4 / Bristol L7)

| Rubric line | Where | Evidence |
|---|---|---|
| **M16.a** individual delivery | §1b | `simple_simulator.py` (2508 L), 12/12 R requirements in sim, 127 unit tests |
| **M16.b** member of team | §2a, §2b, §4a | FSM renegotiation with Robin; camera-conflict split; Demetro script polish ×4 |
| **M16.c** leadership (claimed honestly) | §1a | Explicitly downgrades "led" to "owned"; claims ownership, not formal leadership |
| **M16.d** team evaluation | §3a | Criterion (WBS velocity, R-coverage), judgement, cause (late contracts), lesson applied in wk20 |
| **M16.d** own evaluation | §3b + table | Self-dev table shows 6 weaknesses → actions → measurable outcomes inside project timeline |
| **M17.a** complex engineering content | §1b, §3a | Vision pipeline, SITL sim, GPS estimation math, Kolb walkthrough |
| **M17.b** technical audience | §2b, §4b | Robin consumed `passive_watch_2.py` via HTTP contract; Robbin onboarded in 48h |
| **M17.c** non-technical audience | §4b | Complaint letter to course organiser: explicit jargon strip, before/after phrase ("detection pipeline" → "our software that recognises people from the air") |
| **M17.d** evaluate methods | §4b | 5 methods enumerated, criterion (time-to-understanding), judgement, lesson applied |
| **Bristol Teamwork 70+** conflict mgmt | §2a | 11-state vs 6-state FSM disagreement resolved by simulator data, not authority |
| **Bristol Insight 70+** self-dev programme | §3b table | 6 named weaknesses each with action + measurable outcome |
| **Bristol Insight 83+** feedback to others | §4b + §2 table | STAR feedback to Edward (outcome measured in *his* capability); feedback log with 3 peer-development actions |
| **Bristol Comms 60+** range of media | §4b | Prose / simulator demo / blueprints / READMEs / letter — five distinct media |
| **Bristol Decision-making 70+** evidence-based under challenge | §4a, §3a | Pilot's abort-button feedback → concrete UX change; FSM sim-test resolution |

**Heuristic scoring (from D7_AHEP4_GUIDE §9 checklist):**
- M16 sub-lines: ~3/3 on a/b/d-own/d-team; ~2/3 on leader (correctly downgraded); ~3/3 Bristol 70+
- M17 sub-lines: ~3/3 on a/b/c/d; ~3/3 media variety; ~2/3 engaging manner (no figures)
- Quality multipliers: evidence spine ~3/3, alternative perspective ~2/3, forward-looking ~3/3
- Estimated band: **mid-70s** (Bristol L7 = Master 70s band)

## Strengths

1. **Strict STAR discipline.** Every story has a measurable R. No "the team worked well" filler.
2. **Margin tags + top table** give the marker a two-second navigation experience — supports M17 "engaging and professional" without needing imagery.
3. **Evidence tables collapse narrative** — the feedback log (§2) and self-dev log (§3) each hit a rubric line that normally eats a full paragraph, freeing space for STAR density.
4. **Single Kolb deep-dive** rather than multiple — disciplined use of the framework, not name-dropping.
5. **Peer-development evidence is structured** — the Edward STAR ends with *his* outcome (owning the number), which is the Bristol Insight 83+ differentiator.
6. **Honest leadership language** — downgrades "led" to "owned" in §1a, explicitly addressing the D7_AHEP4_GUIDE §5 threshold test.
7. **Non-technical audience is real** — the complaint letter to Steve is a genuine non-engineering reader with a concrete jargon-strip example (M17.c threshold met).

## Weaknesses

1. **6 pages not 5.** Target was 7-page working / 5-page final. This draft is 6 pages; it needs ~15–20% trimming to reach the 5-page D7 brief limit. Easiest cuts: the conclusion paragraph in §4, table 3 row count, and one of the two STARs in §2b.
2. **No figures.** Bristol Comms 80+ wants "engaging and professional manner" — a system diagram or a GPS-CEP-over-time chart would push Comms from 70s to 80s. Writer B is text-and-tables only.
3. **Placeholders not filled** — `[PLACEHOLDER: Edward]`, `[PLACEHOLDER: pilot]`, `[PLACEHOLDER: mechanical lead]`, `[PLACEHOLDER: PM]`. User must fill in real teammate names before submission.
4. **Kolb deep-dive is in §3a, not a separate "Self-development" section.** The D7_FRAMEWORKS doc suggested a dedicated self-dev section; Writer B embedded it in "My impact" to stay within the four mandatory headings. This is a conscious trade-off.
5. **M5/M7 (STEEPLE / life-cycle) not explicit.** The D7 brief says D7 focuses on M16/M17; M5/M7 live in D6. Writer B does not re-cover them. If markers expect any M5/M7 appearance, add one sentence in §3b (ethical self-audit of the sim-vs-real claims).
6. **Compile warnings:** two underfull/overfull hboxes in the table captions — cosmetic only, no layout breakage. Can be cleaned with `\raggedright` in the table column if preferred.
7. **"Even better if" is thinner in §3 than §1/§2.** Some sub-questions have stronger forward-looking than others.

## What to compare vs Writer A

- **Heading structure:** identical (the 4 mandatory headings, 10 sub-questions)
- **Framework mix:** Writer B = STAR + WWW/EBI + one Kolb + one Schön label + three tables. Writer A's mix is unknown to this agent.
- **Navigation affordances:** Writer B has margin tags + rubric mapping table. Writer A may not.
- **Evidence density per page:** Writer B uses tables to compress 3 separate rubric lines into ~12 rows that would otherwise cost a full page of prose.
- **Voice:** Writer B is declarative, clipped, outcome-first ("I did X, result was Y"). A "CV-on-steroids" voice deliberately trading warmth for marker-friendliness.

## Known gaps the user should fill before submission

1. Replace all `[PLACEHOLDER: ...]` with real names.
2. Confirm the 6-state FSM story matches Robin's memory.
3. Confirm the altitude/9-point FOV story is attributable to Edward (if not Edward, rename).
4. Trim 15% for the 5-page final limit, OR request a 6-page waiver if the brief allows.
5. Add one figure (system diagram or GPS-CEP plot) in §3 if chasing the 80+ Comms band.
