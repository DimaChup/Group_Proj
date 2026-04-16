# D7 V2 — Space Utilisation & Visual Presentation Evaluation

**Scope:** Layout, density, readability, visual weight. Content scoring is separate.
**Artifact:** `report/personal_v2/v2_page-1.png` … `v2_page-7.png` (working draft, 7 body-pages incl. cover).
**Rubric targets (from D7_SCORING_FINAL.md §1.4 / "Visual targets"):**
- Every body page **85–95% filled**
- No orphaned headings at page bottom
- No widow lines (single-line tails)
- Balanced visual weight L-R and T-B
- Consistent heading hierarchy throughout

---

## 1. Per-page evaluation

### Page 1 — Cover
```
fill_percent: ~55%
whitespace_zones: [band above title ~15%, band below rubric map ~18%, margins on metadata block]
visual_balance: good (classical centred cover; slight bottom-heaviness from confirmation italics)
readability_floor: PASS
orphan_or_widow: none (cover exempt)
heading_hierarchy: clear (University → Faculty → Degree → Title → Subtitle → Epigraph → Metadata)
table_quality: N/A (no table, but the Unit/Deliv/Supervisor/Submission/Word count/Page count key-value block acts as one; compact and well-aligned)
font_legibility: good
overall_grade: A-
```
**Notes:** The cover is genuinely nice — title has weight, italic subtitle is restrained, the Kolb epigraph ("An honest reflection on an 820-commit, solo-led build…") is a strong tone-setter. Placeholders still visible: `[STUDENT_ID]`, `[TEAM_NAME]`, `Dr. [SUPERVISOR]`, `[WORD_COUNT]`, `[PAGE_COUNT]`. These **must** be filled before submission; leaving them would look amateur and cost marks on Communication. Otherwise this is distinction-level cover presentation.

---

### Page 2 — Rubric Map + start of §1 My role
```
fill_percent: ~92%
whitespace_zones: [thin gutter above Rubric Map title (~3%), normal inter-paragraph spacing only]
visual_balance: good (table at top, heading mid, dense prose below — balanced T-B)
readability_floor: PASS
orphan_or_widow: none — "My role" heading has 3+ lines of body beneath it, safe
heading_hierarchy: clear (table title "Rubric Map" → section heading "My role" → bold lead-in "1a.")
table_quality: compact (4 rows × 4 cols, `\scriptsize`-ish, text wraps cleanly; "1411 → 754-line refactor, 146 pytests" is a bit dense in a single cell but readable)
font_legibility: good (body), borderline on Rubric Map cells (small but still legible at 150 dpi render — verify on print)
overall_grade: A-
```
**Notes:** Best-filled page in the document. The Rubric Map is genuinely useful — a marker can skim it and see where evidence lives. One concern: the "Key evidence" column has inconsistent wrap (Q2 row has broken whitespace around "two drifts,"), which looks slightly uneven. Consider `\raggedright` in that column or tightening to two lines max.

---

### Page 3 — §1 My role continued + start of §2 My team
```
fill_percent: ~90%
whitespace_zones: [normal para spacing]
visual_balance: good
readability_floor: PASS
orphan_or_widow: none — "2a. Structure" heading sits near bottom but has ~4 lines of body below before page break, which is acceptable
heading_hierarchy: clear
table_quality: N/A
font_legibility: good
overall_grade: A
```
**Notes:** Cleanest body page. Compact `\textbf{1b.}`, `\textbf{1c.}`, `\textbf{2a.}` inline lead-ins are **working** — they read as subsection markers without eating a line. Prose density is at the sweet spot.

---

### Page 4 — §2 My team continued
```
fill_percent: ~93%
whitespace_zones: [minimal; one slightly larger inter-paragraph gap mid-page]
visual_balance: good (very uniform grey block of text)
readability_floor: CONCERN-light — this page is the densest; a wall-of-text feel without any heading break. A marker scanning quickly sees no landmarks.
orphan_or_widow: none
heading_hierarchy: N/A (no headings on this page — by itself not a bug, but combined with the density it makes the page feel monolithic)
table_quality: N/A
font_legibility: good
overall_grade: B+
```
**Notes:** Page is *too* uniform. Consider breaking with a `\textbf{2b.}` / `\textbf{2c.}` inline lead-in somewhere, or a one-line block-quote pulled out — just to give the eye a rest point. Grade drops half-step for readability.

---

### Page 5 — §3 My impact
```
fill_percent: ~88%
whitespace_zones: [normal; one ~4% gap before "My impact" heading which is correct]
visual_balance: good
readability_floor: PASS
orphan_or_widow: none
heading_hierarchy: clear ("My impact" section heading + bold lead-ins)
table_quality: N/A
font_legibility: good
overall_grade: A-
```
**Notes:** Good section landing. The `\textbf{3a.}` lead-in is discoverable. Density drops very slightly vs page 4, giving welcome breathing room after the page-4 wall.

---

### Page 6 — §4 My support (start)
```
fill_percent: ~90%
whitespace_zones: [normal]
visual_balance: good
readability_floor: PASS
orphan_or_widow: none
heading_hierarchy: clear ("My support" heading + `\textbf{4a.}` lead-in)
table_quality: N/A
font_legibility: good
overall_grade: A-
```
**Notes:** Mirrors page 5 — clean, well-spaced. No issues.

---

### Page 7 — §4 My support continued (tail page)
```
fill_percent: ~35–40%  ← WORST PAGE
whitespace_zones: [bottom ~55% of page entirely blank, single orphaned paragraph from previous page flow]
visual_balance: top-heavy (severely)
readability_floor: PASS (what's there reads fine)
orphan_or_widow: ORPHAN PARAGRAPH — final paragraph is ~8 lines, then the page is empty. No conclusion/identity-shift closing present (the rubric calls for a conclusion move per §1 of scoring guide).
heading_hierarchy: none (tail page)
table_quality: N/A
font_legibility: good
overall_grade: C
```
**Notes:** **This is the single biggest layout problem.** A Distinction-level report never has a 40%-full final page with no closing move. Two options:
1. **Cut to fit page 6** (preferred for FINAL submission at 5 pages anyway) — merge tail into §4b and end on page 6.
2. **Add the missing conclusion** (identity-shift closing, Section 9 Move 10 per the scoring guide, ~150 words) to fill the bottom half and give the document a real ending.

Right now the document *stops* rather than *ends*.

---

## 2. Cross-cutting checks

### Rubric Map (page 2)
- **Clear?** Yes. 4 columns (Question, Section, Key evidence, Rubric hit) with rows for Q1/Q2/Q3/Q4.
- **Skimmable?** Yes — a marker can read in <15 seconds.
- **Useful?** Very. Explicitly maps each section to the rubric bucket it targets ("Specialist: Self-awareness", "Team: Decision", "Specialist: Communication", "Team: Self-awareness"). This is a marks-defence mechanism and belongs in the final.
- **Issue:** Q2 row has awkward mid-cell whitespace in "Key evidence". Fix with `\raggedright`.

### Cover page
- Professional: **yes**. Classical centred layout, hierarchy is correct, epigraph works.
- Sparse: **slightly** (~55% fill) but that is conventional for a cover and not a defect.
- **Blockers:** unresolved placeholders (`[STUDENT_ID]`, `[TEAM_NAME]`, `[SUPERVISOR]`, `[WORD_COUNT]`, `[PAGE_COUNT]`). Must be resolved.

### Section boundaries
- Clean on pages 2→3 (§1 tail, §2 start mid-page).
- Clean on pages 4→5 (§2 tail, §3 start).
- Clean on pages 5→6 (§3 tail, §4 start).
- **Page 6→7 is the problem** — section bleeds but then dies without a conclusion.

### Paragraph density (target 85–95%)
| Page | Fill | Verdict |
|------|------|---------|
| 1 (cover) | ~55% | OK (cover) |
| 2 | ~92% | on target |
| 3 | ~90% | on target |
| 4 | ~93% | on target (but monolithic) |
| 5 | ~88% | on target |
| 6 | ~90% | on target |
| 7 | ~37% | **FAIL** |

5 of 6 body pages hit the target band. Page 7 blows it.

### Compact lead-ins (`\textbf{1a.}` etc.)
**Working.** They read as inline micro-headings without consuming a vertical line. The bold weight is distinct enough to anchor the eye. Confirmed visible on pages 2, 3, 5, 6. Keep.

### Consistency
- Font: consistent (serif body, bold for lead-ins and section headings, italics for epigraph and technical terms).
- Margins: consistent throughout.
- Heading style: consistent ("My role" / "My team" / "My impact" / "My support" — same weight, same spacing).
- Line spacing: consistent (`\linespread{1.05}` visible).
- Typewriter for code identifiers (`vision.py`, `DESIGN_DECISIONS.md`, `calibration_data.npz`) — consistent and appropriate.

**Consistency grade: A.**

---

## 3. Overall presentation grade

**B+ (working draft), with a clear path to A– if fixed.**

- Everything **except page 7** is at Distinction level.
- Page 7 pulls the overall grade down by ~one step because the document has no closing and ~60% of its final page is empty.
- Cover placeholders must be resolved before the verdict can move above B+.

---

## 4. Top 5 layout improvements (ranked by impact)

| # | Fix | Impact | Effort |
|---|-----|--------|--------|
| 1 | **Fix page 7** — either cut the tail into page 6 (targets the 5-page FINAL anyway) OR add the missing ~150-word identity-shift conclusion to fill the page and deliver the required closing move | **High** (fixes both the Communication cap risk AND a rubric content gap) | 30–60 min |
| 2 | **Fill cover placeholders** — `[STUDENT_ID]`, `[TEAM_NAME]`, supervisor name, final word count, final page count | **High** (unresolved placeholders look amateur; easy marks) | 5 min |
| 3 | **Break up page 4 wall-of-text** — insert a `\textbf{2b.}` or `\textbf{2c.}` inline lead-in midway, or a single block-quote, to give the eye a landmark | Medium (readability at pace) | 15 min |
| 4 | **Rubric Map Q2 cell** — add `\raggedright` to the Key-evidence column to kill the mid-cell whitespace in the "two drifts," row | Low (cosmetic) | 2 min |
| 5 | **Bold-consistency sweep** — confirm every `\textbf{Na.}` lead-in uses the same trailing punctuation (period vs space) and the same font weight; skim pages 2, 3, 5, 6 side-by-side | Low (polish) | 10 min |

---

## 5. Rubric §1.4 PRESENTATION CAP violations

Per `D7_SCORING_FINAL.md` hard gates:

| Gate | Rule | V2 status |
|------|------|-----------|
| Working draft page limit | ≤ 7 pages body | **PASS** (exactly 7 incl. cover → 6 body, under cap) |
| Final submission page limit | ≤ 5 pages body (excl. cover + appendices) | **FAIL if submitted as-is** (currently 6 body pages) — CAP 48 would trigger |
| 4 required headings | My role / My team / My impact / My support | **PASS** (all present, correct wording) |
| AI-policy boilerplate prose | No generic language without personal voice | **PASS** from a layout perspective (cover epigraph is voiced, sections are specific) — CAP 48 not triggered on prose style |
| Consistent visual hierarchy | Bold, distinct, consistent | **PASS** |
| 85–95% fill per body page | Density target | **FAIL on page 7 only** (~37%) — does not automatically cap but signals "working draft, not final" to markers |
| No orphans/widows | No single-line heading tails | **PASS** (no headings stranded at bottom of any page) |

**Verdict:** No hard CAP violations **as a working draft**. The **5-page FINAL cap will fire** if this is submitted without cutting. Page 7's density failure is a signal of incompleteness, not an automatic cap.

---

## 6. Whitespace budget — add content vs cut to 5 pages

**Current:** 6 body pages (pages 2–7). Target for final: **5 body pages**.

**Whitespace available to absorb content (if you wanted to add):**
- Page 7: ~60% of one page empty → roughly **350–400 words** of room.
- Pages 2–6: maybe 2–3% slack each → negligible (~100 words total).
- **Total absorb capacity: ~450–500 words of new content** before hitting density ceiling.

**Cut required to hit 5-page FINAL:**
- Remove 1 body page worth of material = **~420–480 words** (pages 3–6 are running at ~440 words each based on observed density).
- Realistic strategy: **merge page 7's orphan tail into §4b on page 6** (already recovers ~150 words of the overflow), **then tighten pages 4 and 5 by ~150 words each** by compressing the weakest anecdote per section into a one-sentence summary. That gets you to 5 body pages without losing any rubric move.

**Recommended path:** Cut, don't add.
- Keeps word budget safe
- Hits the 5-page FINAL gate
- Forces the weakest anecdote-per-section out, which raises average quality
- The missing conclusion (Move 10, ~150 words) can be accommodated by the cuts — write it during the compression pass, don't add it on top.

**Net word delta to reach 5-page FINAL with conclusion included:** cut ~450 words from body, write ~150 words of conclusion → **net −300 words from current draft.**

---

## Summary line

**Working-draft grade: B+.** Pages 1–6 are A/A–. Page 7 is a C that drags the average. No hard CAP violations at 7-page working-draft level, but the document will **fail the 5-page FINAL cap** unless ~450 words are cut. Fix page 7 + cover placeholders + page-4 readability break and the FINAL can land at **A–/A** on presentation.
