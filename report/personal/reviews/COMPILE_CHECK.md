# D7 Individual Reflective Report -- Compile Check

**Date**: 2026-04-03
**Branch**: Working8.Robbin3
**File**: `report/personal/main.tex`

---

## Compilation

| Step | Result |
|------|--------|
| `pdflatex` pass 1 | OK |
| `biber main` | OK -- 15 citekeys found, all resolved |
| `pdflatex` pass 2 | OK |
| `pdflatex` pass 3 | OK -- no "Rerun" warnings remaining |

**LaTeX errors**: 0
**Undefined references**: 0
**Missing citations**: 0
**Overfull hbox warnings**: 1 (section 02, line 8-9: `detect_in_image(frame)` monospace runs 41pt wide -- cosmetic only, visible as text extending into right margin on page 1)
**Underfull warnings**: 0

---

## Page Count

| Page | Content |
|------|---------|
| 1 | Title block + Sec 1 (Introduction) + Sec 2.1 (Original Solutions) |
| 2 | Sec 2.2 (Safety-Critical) + Sec 2.3 (Diversity) + Sec 3.1 (Positive Potential) + Sec 3.2 (Environmental, starts) |
| 3 | Sec 3.2 (ends) + Sec 3.3 (Dual-Use) + Sec 4 (Teamwork, starts) |
| 4 | Sec 4 cont. (Disagreements, Feedback, Communication) |
| 5 | Sec 4 ends (2 lines: team effectiveness) + Sec 5 starts (5.1 Skills, 5.2 Self-Mgmt, 5.3 Strengths starts) |
| 6 | Sec 5.3 (ends) + Sec 5.4 (Helping Teammates) + Sec 5.5 (Development Programme, starts) |
| 7 | Sec 5.5 (ends) + Sec 5.6 (Career Goals) -- body ends ~1/3 down, rest blank |
| 8 | References (forced `\newpage`) |

**Total pages**: 8
**Body pages**: ~6.3 (pages 1 through 1/3 of page 7)
**Reference pages**: ~0.5 (top half of page 8)
**Blank/wasted**: ~0.7 (bottom 2/3 of page 7) + ~0.5 (bottom half of page 8)

---

## PAGE LIMIT VERDICT: OVER BY ~1.3 PAGES

The 5-page body limit is exceeded. Body content occupies approximately 6.3 pages. There is no separate cover/title page -- the title block is inline at the top of page 1 and counts toward the body.

### How much to cut

To fit within 5 body pages, approximately **1.3 pages (~55-60 lines of rendered text)** must be removed. This is roughly equivalent to removing one full subsection plus trimming several others.

### Recommended cuts (largest sections first)

Section 5 (Self-Assessment) is by far the longest at ~3 rendered pages (pages 5-7). It has 6 subsections -- more than any other section. Specific trim targets:

1. **Sec 5.3 (Strengths/Weaknesses)** -- 2 long paragraphs. The "delayed hardware testing" paragraph (lines 22-23 of 05_self_development.tex) repeats points already made in Sec 5.2. Cut or merge. Saves ~6-8 lines.

2. **Sec 5.4 (Helping Teammates)** -- largely repeats examples from Sec 4 (teamwork). The pilot walkthrough and Edward calibration examples appear in both. Either cut this subsection entirely (~10 lines saved) or reduce to 2-3 sentences that add NEW reflection not already in Sec 4.

3. **Sec 5.2 (Self-Management Failures)** -- the Docker/bench-test recovery paragraph (line 14) could be condensed to one sentence. Saves ~4-5 lines.

4. **Sec 5.5 (Development Programme)** -- the three numbered items are good but verbose. Each could lose 1 sentence. Saves ~4-5 lines.

5. **Sec 4 (Teamwork)** -- "Communication across skill gaps" paragraph is the longest in the section (~12 lines rendered). The cancelled-flight-day anecdote repeats information. Trim to essentials. Saves ~4-5 lines.

6. **Sec 5.6 (Career Goals)** -- already concise (7 lines), but the closing italic quote could be moved to the end of section 5.5 to eliminate the subsection header overhead. Saves ~2 lines.

**Total estimated savings from above**: ~35-45 lines. If insufficient, additionally trim:

7. **Sec 3.2 (Environmental)** -- the CO2 calculation and GPU power comparison, while good, are dense. Could lose 2-3 lines.

8. **Sec 2.3 (Diversity)** -- partially overlaps with Sec 4's communication discussion. Could be shortened by 3-4 lines.

### Alternative: formatting adjustments (risky)

Instead of cutting content, formatting changes could reclaim ~0.3-0.5 pages:
- Reduce `\setstretch{1.15}` to `\setstretch{1.08}` (~0.3 pages)
- Reduce `\parskip{4pt}` to `\parskip{2pt}` (~0.2 pages)
- Remove `\newpage` before references (saves blank space on page 7, refs start there)

**Warning**: markers may penalise tight formatting if it looks like limit-gaming. Content cuts are safer.

---

## Other Issues

1. **Overfull hbox** (page 1): `detect_in_image(frame)` in Sec 2.1 extends into the right margin. Fix: break the line or use `\mbox` or rephrase to avoid the long monospace string sitting mid-paragraph.

2. **Unused bib entries**: The following references.bib entries are defined but never cited:
   - `redmon2016yolo` (Redmon 2016 YOLO paper)
   - `aiedgelitert` (ai-edge-litert)
   - `mavproxy`
   - `abbeel2007helicopter`
   - `hartley2003` (Multiple View Geometry)
   - `opencv`
   - `picamera2`
   - `mcconnell2004` (Code Complete)
   - `humble2010` (Continuous Delivery)
   - `schon1983` (only cited in sec 02 via `\cite{schon1983}` -- actually IS cited, disregard)

   9 of 24 bib entries are unused. Not an error (biber only includes cited ones), but cleanup is good practice.

3. **References page**: The `\newpage` before `\printbibliography` forces references onto a new page even though page 7 has 2/3 blank space. Removing `\newpage` would let references flow immediately after the body, saving a page. This is the single easiest change to bring the report closer to the limit.

---

## Summary

| Metric | Value |
|--------|-------|
| Compiles cleanly | YES |
| Errors | 0 |
| Undefined refs | 0 |
| Missing citations | 0 |
| Body pages | ~6.3 |
| Page limit | 5 |
| **Over by** | **~1.3 pages** |
| Action needed | Cut ~55-60 lines of rendered text, primarily from Section 5 |
