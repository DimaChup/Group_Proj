# D7 "Free Pages" Strategy

**Brief constraint:** 5 pages body. Cover page and appendices are *excluded*
from the page limit. Everything else is ambiguous — this note fixes it.

**Guiding principle:** pages outside the body limit are not "free" — they cost
marker attention. Every free page must either (a) help the marker navigate,
(b) prove compliance with a rubric item, or (c) house evidence the body
refers back to. If it does none of those three, cut it.

---

## Decision table

| Element | Counts as body? | Include? | Reason |
|---|---|---|---|
| **Cover page** | No (excluded by brief) | **YES** | Professional baseline; houses title, ID, team, word count, epigraph. Required by convention. 1 page. |
| **Table of contents** | Ambiguous | **NO** | A 5-page report with 4–6 named sections does not need a TOC. Markers can see the whole report at once. A TOC signals padding. |
| **List of figures** | Ambiguous | **NO** | Same reason. A 5-page reflective report with 0–2 figures has nothing to list. |
| **List of tables** | Ambiguous | **NO** | Same. |
| **Acronyms / glossary** | Excluded (like appendix) | **NO** (conditional) | Only include if the report uses >6 project-specific acronyms that a non-specialist marker cannot Google. SAR, CV, YOLO, TFLite, MAVLink, GPS are all common enough. If the body is written clearly (first use spells out the acronym), a separate list is redundant. **Decision: skip, keep first-use expansion in body.** |
| **Word count declaration** | n/a | **YES** | One line on the cover page: `Word count: [N] (body, excluding cover, references, and appendices)`. Cheap compliance. Already in the cover template. |
| **Acknowledgements** | n/a | **NO** | A reflective report *is* the acknowledgement — it discusses teammates by role. A separate "thanks to" section is stylistically wrong here and risks sounding sycophantic or ironic given the honest stance of the body. |
| **Peer weighting disclosure** | n/a | **NO** | That is a D6 (team report) artefact, not D7. Do not import it into a personal reflection. |
| **References / bibliography** | Excluded (like appendix per brief) | **YES** | 5–7 entries max. Placed after body. See `references_guide.md`. |
| **Appendices** | Excluded (by brief) | **CONDITIONAL** | Only include an appendix if the body has a hook that genuinely requires evidence the 5 pages cannot carry. Candidates: (A) commit-count / contribution graph proving the 820-commit claim, (B) the team-contribution matrix, (C) a screenshot of one artefact (e.g. simulator UI or state-machine diagram) that the body references. **Rule: appendices must be referenced from the body** (`see Appendix A`), otherwise cut. Markers dislike "dumped" appendices. |
| **Declaration of originality** | n/a | **YES** (on cover) | Already in the cover page template as a single small-font paragraph at the bottom. Nothing more needed. |

---

## Recommended final layout (page-by-page)

```
[Page 0]  Cover page       (excluded — title, author, epigraph, declaration, word count)
[Page 1]  Body §1–§2       (reflection framing + my role)
[Page 2]  Body §3          (deep-dive learning episode)
[Page 3]  Body §4–§5       (team dynamics + critical self-examination)
[Page 4]  Body §6          (what I would do differently)
[Page 5]  Body §7          (forward commitments / professional development)
[Page 6]  References       (excluded — 5–7 entries, footnote-size, single column)
[Page 7+] Appendices       (excluded — only if referenced from body)
```

Total marker-visible pages: **5 body + ~2 extras = 7**. Anything more is padding.

---

## What the cover page MUST carry (non-negotiables)

1. Title + subtitle + unit code (AENGM0074).
2. Author full name + student ID + team name.
3. Role on the team (one line — CV / autonomy lead).
4. Submission date.
5. Word count of the body.
6. Originality declaration (one small paragraph).
7. An epigraph or stance statement (3–4 lines) — this is the only "soft"
   element and it earns its place because it *frames* the honest tone
   of the report before the marker reaches the body.

## What the cover page MUST NOT carry

- A long abstract — this is a reflective report, not a research paper.
- A figure, photograph, or rendering — cover-page hero images look
  amateurish on a 5-page reflection.
- A version number or draft marker.
- A "to my family" dedication.
- Any content that belongs in the body.

---

## Appendix rules (if you choose to include any)

1. **Reference from the body** — every appendix must be `see Appendix A` in the body, otherwise cut.
2. **Label and caption** — `Appendix A — 820-commit contribution graph. Source: git log, repo@<sha>.`
3. **Cap at 2 pages total** — markers will not read more. If you have more evidence, put it in D6.
4. **No new argument in an appendix** — appendices carry evidence, not claims. Any claim belongs in the body where it can be marked.

**Recommended appendix set for Apollo (pick 1–2, not all three):**

- **A. Contribution timeline** — commit graph by week, colour-coded by module (vision / state-machine / simulation / tests / docs). Proves the 820-commit solo-led claim.
- **B. Team contribution matrix** — who touched which module, one table. Proves the "de-facto" role claims.
- **C. Lessons-learned log extract** — 5–8 bullet rows from `docs/LESSONS_LEARNED.md`, chosen to match the reflection moments in the body.

If in doubt, include only **A**. One appendix is clean. Three is noise.
