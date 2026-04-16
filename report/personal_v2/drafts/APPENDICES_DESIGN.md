# D7 Appendices — Design Rationale

**Context:** Brief says "Maximum length: 5 pages, excluding cover page and appendices."
Appendices are free space but must be **purposeful and referenced from the body**. A D7
at 83–84/100 is "at ceiling" for the 5-page body; the next marginal marks come from
appendices that (a) evidence Master's-level *evaluation* clauses (M16.d, M17.d),
(b) provide **media diversity** (Bristol Communication 60+ floor requirement), and
(c) give the marker skimmable confirmation that nothing on the rubric was missed.

---

## Selection — which 4 appendices and why

From the 7 candidates (A–G) I selected **A, D, F, G** and dropped B, C, E. Reasoning:

| Cand. | Verdict | Reason |
|---|---|---|
| **A — Development Actions Log** | **KEEP** | Directly evidences Bristol Insight 70+ ("implement an effective programme of self-development"). This is the single biggest rubric gate for the 70→80 jump. Without a visible log of actions taken, the body claim "I implemented X" has no substantiation. |
| B — Feedback Log | drop | Overlaps with A and G. Feedback given/received is absorbed into A (as actions) and G (as teammate interactions). Keeping B would be padding. |
| C — Incident Timeline | drop | Weaker than A because it is descriptive not evaluative. A timeline alone hits no rubric clause that A doesn't already hit better. |
| **D — Rubric Coverage Map** | **KEEP** | The single highest-leverage appendix. Maps the 10 brief questions × the rubric criteria × AHEP4 M16.a–d / M17.a–d, cell-by-cell, pointing at body evidence. Forces the marker to tick every box — removes the risk that a rubric line is missed due to scan-reading. This is also the only appendix that directly supports *Logical argument* (alternative perspectives, every claim cited). |
| E — Reflection Framework Application | drop | Risk of pretension. A D7 that names-drops Kolb/Schön/STAR without earning it reads as box-ticking. The body can mention frameworks inline; a dedicated appendix gives diminishing returns. |
| **F — Screenshots / Media Grid** | **KEEP** | **Load-bearing for Bristol Communication.** The Bristol L7 Comms 60+ descriptor requires "a wide range of media". A text-only D7 is capped at 59 on this line. A single page of screenshots (ground station, dashboard, simulator, dataset, god view) lifts the D7 over the media-diversity floor at minimal cost. |
| **G — Named Contribution Map** | **KEEP** | Evidences M16.b (cross-boundary collaboration) in concrete form: one row per teammate (Robin, Demetro, Zian, Sid) with what I did, what they did, and the interaction artefact. Also hits Bristol Teamwork 60+ ("recognising the value and contributions of others") — a clause the body can only touch briefly. |

**Final set: A, D, F, G — 4 appendices, ~4 pages.**

---

## How each appendix supports a specific rubric gate

### Appendix A — Development Actions Log (~1 page table)
- **Primary gate:** Bristol Insight **70–79** → "implement an effective programme of self-development" + Insight **80+** → "effective feedback to others"
- **Secondary gate:** AHEP4 M16.d-own (self-evaluation with criterion + judgement + cause + lesson) — each row is a micro-evaluation loop
- **Failure mode closed:** failure mode #8 "lessons with no applied consequence" — every row has an Outcome column with a file/commit reference
- **Reference from body:** "(see Appendix A, row 4)" attached to any self-development claim

### Appendix D — Rubric Coverage Map (~1 page matrix)
- **Primary gate:** AHEP4 M16 + M17 full coverage; Bristol Logical Argument 60+ ("coherent substantiated arguments, critically evaluate alternative perspectives")
- **Secondary gate:** Gives the marker permission to award marks without hunting. Removes the risk that a busy marker reads the body once and misses that M17.c (non-technical audience) is actually addressed.
- **Failure mode closed:** failure modes #5, #10 — by forcing every rubric cell to point at a body paragraph, the writer discovers gaps before the marker does.
- **Reference from body:** single footnote in the conclusion: "A full mapping from the rubric to the body evidence is in Appendix D."

### Appendix F — Screenshots / Media Grid (~1 page 2×3 grid)
- **Primary gate:** Bristol Communication **60+** → "a wide range of media as appropriate". A text-only D7 is capped at 59 on this line regardless of prose quality. This appendix is the cheapest way to clear the floor.
- **Secondary gate:** Bristol Communication **80** → "engaging and professional manner" if the images are polished and annotated.
- **Failure mode closed:** failure mode #7 "single-medium communication caps Bristol Comms at 59".
- **Reference from body:** any sentence mentioning the ground station, dashboard, simulator, or dataset cites "(Appendix F, panel n)".

### Appendix G — Named Contribution Map (~1 page table)
- **Primary gate:** AHEP4 M16.b (member of a team — cross-boundary with named interface) + Bristol Teamwork **60+** ("recognising the value and contributions of others")
- **Secondary gate:** M16.c ownership language (avoids over-claiming leadership by making the division of labour explicit and mutual)
- **Failure mode closed:** failure mode #1 "descriptive narrative with no criterion" in the team dimension — the table forces concrete interface artefacts per teammate.
- **Reference from body:** every named-teammate anecdote cites "(see Appendix G)".

---

## Visual weight budget

| Appendix | Est. length | Visual density | Content type |
|---|---|---|---|
| A — Dev Actions Log | 1 page | High (table, ~15 rows) | Tabular evidence |
| D — Rubric Coverage Map | 1 page | Very high (matrix, ~10×8 cells) | Matrix |
| F — Media Grid | 1 page | Image-dominant (6 panels with captions) | Visual |
| G — Contribution Map | 1 page | Medium (table, 5 rows × 4 cols) | Tabular |
| **Total** | **~4 pages** | Mixed (tables + matrix + images) | — |

Media types achieved (against Bristol Comms "wide range of media" test):
1. Written prose (body)
2. Tables (A, G)
3. Matrix / structured layout (D)
4. Screenshots / photographs (F)
5. Diagrams / annotated images (F captions)
6. Code / commit references inline (A, G)

Six media types exceeds the "2+ distinct" floor for 60, giving headroom toward the 70+
band where Communication pairs the media count with the evaluation clause (M17.d —
evaluated in the body, not the appendix).

---

## Rule of thumb used in selection

Every appendix must satisfy all three of these tests, or it gets dropped:

1. **Marker test:** if the marker reads only this appendix (30 s skim), do they gain
   new evidence for a rubric line that the body alone did not prove?
2. **Reference test:** is there at least one body sentence that cites this appendix by
   name? If no, the appendix is padding and should be cut.
3. **Gate test:** does this appendix close a named failure mode from the D7 AHEP4 guide?
   If no, there is probably a better appendix to write instead.

A, D, F, G all pass. B, C, E fail the marker test (they describe, not prove).

---

## Placeholder items the user must fill

- **Appendix A**: ~5 rows are fully pre-filled from CLAUDE.md session log; ~10 rows
  have real commits cited but need the user to confirm the "Outcome measure" column
  (some use the D6 scores / Pi FPS numbers which the user should verify).
- **Appendix D**: filled. Cells cite body section numbers which the user must adjust
  to match the final body layout (the body is currently 5 sections labelled §1.a …
  §4.b matching the 10 brief questions; the matrix assumes that layout).
- **Appendix F**: image paths are `PLACEHOLDER` — user must drop in 6 screenshots.
  Suggested sources listed per panel with exact file hints.
- **Appendix G**: filled from D7_RAW_MATERIAL.md; user should confirm Zian's role
  (currently marked "role unclear" per raw material bank).
