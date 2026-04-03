# BRIEF_EXTRACTION Verification Report

> Verified: 2026-04-03
> Source: `docs/AENGM0074-project-brief.pdf` (Release 2.1, 4 February 2026, 12 pages)
> Checked against: `docs/BRIEF_EXTRACTED.md` + `docs/BRIEF_VISUAL.md`

---

## 1. Total Information Items Found in PDF

Counted by page, every discrete piece of information (sentences, table cells, footnotes, URLs, figure descriptions, formatting details):

| Page | Content | Items |
|------|---------|-------|
| 1 | Title, overview (3 paragraphs), Figure 1 (map + legend with 5 entries), footnote 1 | 14 |
| 2 | Scenario (3 paragraphs), Requirements table (12 rows x 3 cols = 36 cells), footnote 1 | 42 |
| 3 | Equipment intro paragraph, equipment table (13 rows x 4 cols = 52 cells incl. separators), 10 URLs | 63 |
| 4 | Imagery intro sentence, dummy photo description, caption | 3 |
| 5 | Deliverables table (7 rows x 5 cols = 35 cells), 6 bullet notes with 7 URLs, AI categories | 48 |
| 6 | D1 PDR details (format 3 bullets, audience 2 bullets, demonstrate 3 bullets, include 5+5 sub-bullets, logistics 3 bullets, final note) | 22 |
| 7 | D4 FDR details (format 3 bullets, audience 4 bullets, present 3 bullets, logistics 3 bullets, final note) | 14 |
| 8 | D6 structure (submission 2 bullets, 8 sections with descriptions), assessment note, peer weighting note, footnotes 2-3 | 15 |
| 9 | D7 structure (submission 2 bullets, AHEP4 reference, "DETAIL TO FOLLOW", 4 AHEP standards, assessment note, footnotes 4-5) | 12 |
| 10 | Version history table (3 rows x 5 cols = 15 cells) | 16 |
| 11 | Appendix A header, D6 rubric table (3 criteria x 6 bands = 18 cells + 3 weight labels) | 22 |
| 12 | Appendix B header, D7 rubric table (3 criteria x 6 bands = 18 cells) | 19 |
| **Total** | | **~290** |

---

## 2. Items Present in Extractions

| File | Coverage |
|------|----------|
| BRIEF_EXTRACTED.md | ~245 items captured (requirements, deliverables, D6/D7 structure, rubric top bands, key constraints, visual descriptions, URLs, footnotes, version history) |
| BRIEF_VISUAL.md | ~260 items captured (page-by-page visual layout, all table contents, all rubric bands word-for-word, formatting details) |
| **Combined** | **~280 of ~290 items** |

---

## 3. MISSING Items

### 3.1 Missing from BRIEF_EXTRACTED.md

| # | Item | Location in PDF |
|---|------|----------------|
| M1 | **Pi camera cable** -- equipment table row (Item: "Pi camera cable", Description: "Cable", Qty: 1, no URL) | Page 3, equipment table |
| M2 | **"Plus relevant cables, mounts, housings, etc. as required."** -- final equipment table row | Page 3, equipment table |
| M3 | **Equipment intro paragraph**: "The Research Drone Platform will be provided preassembled. Companies may augment or modify elements with prior discussion with and approval of the Flight Lab team. The Platform shall be returned in its original state post-demonstration." | Page 3 |
| M4 | **Overview text** (3 paragraphs from page 1): Companies deliver mission plan/systems/interfaces, Fenswood Wilderness location, document is "live" | Page 1 |
| M5 | **Imagery section text**: "Companies will have the opportunity to obtain their own datasets during trial flights." | Page 4 |
| M6 | **D1 PDR full details** (format, audience, demonstrate, include suggestions, logistics, formative note) | Page 6 |
| M7 | **D4 FDR full details** (format, audience, present, logistics, formative note) | Page 7 |
| M8 | **"Peer weighting details to follow."** statement on D6 page | Page 8 |
| M9 | **D6 submission includes "link to public GitHub repository"** (mentioned in D6 section, not just R12) | Page 8 |
| M10 | **Rubric lower bands** (0-35, 42-48, 52-58, 62-68) -- only top band (72-100) is captured for both D6 and D7 rubrics | Pages 11-12 |
| M11 | **D7 AHEP4 page reference**: "specifically p32-37" | Page 9 |
| M12 | **Figure 1 legend entries**: Flight Area, Focus Area (example), SSSI, Survey Area, Take-Off Location -- the legend includes "Focus Area (example)" which is not mentioned in extracted requirements summary | Page 1 |
| M13 | **D5 deliverable description**: "Full system demonstration, final data capture" | Page 5 |
| M14 | **D3 deliverable description**: "Integrated system demonstration, trial data capture" | Page 5 |
| M15 | **Deliverable table "Due" column details**: e.g., D2 is "Wednesday wk20" (no "In-person" listed for D2, unlike D1/D3/D4/D5) | Page 5 |
| M16 | **URL for AI usage policy**: https://www.bristol.ac.uk/bilt/sharing-practice/guidance/ai-in-the-assessment/ (listed as guidance, but different URL path than in BRIEF_VISUAL) | Page 5 |

### 3.2 Missing from BRIEF_VISUAL.md

| # | Item | Location in PDF |
|---|------|----------------|
| V1 | **Figure 1 legend "Focus Area (example)"** entry -- the legend has 5 entries but BRIEF_VISUAL only describes 4 (Flight Area, Search Area, SSSI, Take-Off Location) | Page 1 |
| V2 | **Figure 1 legend uses "Survey Area"** not "Search Area" -- the legend text in the PDF reads "Survey Area" | Page 1 |
| V3 | **D2 delivery format**: the PDF deliverables table shows D2 as "Wednesday wk20" without "In-person" (just the date), but BRIEF_VISUAL does not note this distinction | Page 5 |

### 3.3 Missing from BOTH files

| # | Item | Location in PDF |
|---|------|----------------|
| B1 | **Figure 1 legend "Focus Area (example)"** -- neither file mentions this legend entry. This is significant because it confirms Focus Area is a dynamic zone received mid-flight. | Page 1 |
| B2 | **Legend uses "Survey Area"** not "Search Area" -- the map legend uses "Survey Area" as the label for the orange zone, though the requirements text uses "Search Area". Neither file notes this terminology discrepancy. | Page 1 |

---

## 4. INCORRECT Items

### 4.1 Errors in BRIEF_EXTRACTED.md

| # | Issue | Extracted Says | PDF Actually Says |
|---|-------|---------------|-------------------|
| E1 | **R06 Note column** -- BRIEF_EXTRACTED does not track Note column values, but the summary on line 29 implies R01-R04 have Note 1. In the PDF, R01-R05 have Note "1". R06 does NOT have Note 1 despite referencing coordinates. | "Note on R01, R02, R03, R04" | R01, R02, R03, R04, R05 all have Note "1" |
| E2 | **D6 page exclusions** -- line 68 says "EXCLUDING cover page, exec summary, introduction, references, appendices". The PDF says "excluding cover page, exec summary, introduction, references, and appendices." Minor: missing "and" is cosmetic only. | No "and" | Has "and" before "appendices" |
| E3 | **Equipment table "Companion computer"** -- line 39 says "Raspberry Pi 5 8GB | Companion computer". The PDF says Description is "Computer", not "Companion computer". | "Companion computer" | "Computer" |
| E4 | **D6 rubric Specialist Skills top band** -- line 85 says "Technologies selected and implemented highly effectively with initiative, autonomy, creativity". PDF rubric cell says "Appropriate technologies and approaches selected and implemented highly effectively, showing initiative, autonomy, and creativity." | Paraphrased, missing "Appropriate", "approaches", "showing", "and" | Full wording as in PDF |
| E5 | **D6 rubric Decision Making top band** -- line 86 says "Confidence and creativity in adapting to changing/unfamiliar/challenging circumstances. Effective evidence-based decisions". PDF cell says "Shows confidence and creativity in adapting to changing and unfamiliar/challenging circumstances and making effective, evidence-based decisions." | Paraphrased | Different wording |
| E6 | **D7 rubric top band** -- line 107-109 show paraphrased versions of the D7 rubric descriptors. The PDF has specific wording (e.g., "responsive to group members' interests and the obligations and goals of the team" vs extraction's "Responsive to group members' interests and obligations"). | Shortened | "...and the obligations and goals of the team" |
| E7 | **D6 rubric Communication 72-78 band** vs 83-100 band -- in the PDF, the 72-78 band says "Reporting and presentation are effective, making use of appropriate techniques and resources." which is IDENTICAL to the 62-68 band. This subtlety is not captured. | Not distinguished | 72-78 repeats 62-68 wording for Communication |
| E8 | **D7 "DETAIL TO FOLLOW"** -- BRIEF_EXTRACTED line 291 (in VISUAL section) mentions yellow highlighting. The main extracted section does not mention this warning at all. | Missing from main extract | Yellow-highlighted "DETAIL TO FOLLOW" warning |

### 4.2 Errors in BRIEF_VISUAL.md

| # | Issue | VISUAL Says | PDF Actually Says |
|---|-------|-------------|-------------------|
| V-E1 | **Page 1 polygon colors swapped** -- lines 26-27 describe "large orange/brown polygon covering most of the central field area" as the search/survey region and "teal/cyan polygon in the upper-left" as SSSI. From the actual PDF image, the teal/cyan is the largest polygon (Flight Area) and the orange is the Search/Survey Area inside it. The small red polygon is the SSSI. | Orange = search, Teal = SSSI | Teal = Flight Area (largest), Orange = Search Area, Red = SSSI |
| V-E2 | **Page 1 "red marker pin"** -- line 27 says "small red marker pin roughly in the center-left area." Looking at the PDF, there IS a small marker labeled "Take-Off Location" in the upper-left area of the map near the edge, not center-left. | "center-left" | Upper-left, near Flight Area edge |
| V-E3 | **Page 4 dummy clothing** -- line 119 says "dark green/black jacket and dark trousers". The actual photo shows the dummy in dark/black coveralls or overalls (one-piece), not a separate jacket and trousers combination. The BRIEF_EXTRACTED (line 196) more accurately describes "dark green/olive overalls or coveralls." | "dark green/black jacket and dark trousers" | Dark coveralls/overalls (one-piece) |
| V-E4 | **Page 4 dummy arm position** -- line 120 says "right arm extended out to the side, left arm closer to body." Looking at the photo, both arms appear extended outward, with the dummy in a spread-eagle pose. | One arm in, one out | Both arms extended |
| V-E5 | **Page 5 D2 "In-person"** -- the deliverables table in BRIEF_VISUAL does not note whether D2 is In-person or not. Looking at the PDF image, D2's Due column appears to show just "Wednesday wk20" without "In-person". This is accurately captured but worth noting -- D2 may be the only formative deliverable without "In-person" specified. | Silent on D2 format | D2 may lack "In-person" designation |
| V-E6 | **Page 5 AI URL** -- line 156 gives URL as `https://www.bristol.ac.uk/bilt/sharing-practice/guidance/ai-in-the-assessment/`. The actual PDF shows `https://www.bristol.ac.uk/bilt/sharing-practice/guides/guidance-on-ai/using-ai-in-assessment/`. | Different URL path | Different URL path |
| V-E7 | **D6 rubric Decision Making 83-100** -- line 356 stops at "...unfamiliar/challenging circumstances." but the PDF cell continues with "and making effective, evidence-based decisions." | Truncated | Full sentence includes "and making effective, evidence-based decisions." |

---

## 5. Pass/Fail Assessment

### Overall: CONDITIONAL PASS

**Coverage**: ~96% (280/290 items captured across both files combined). No critical requirement or rubric criterion is completely absent.

**Critical issues (must fix):**
1. **V-E1**: Page 1 polygon color assignments are WRONG in BRIEF_VISUAL -- teal is Flight Area (not SSSI), orange is Search Area. This is a factual error that could mislead report writing.
2. **E1**: R05 also has Note "1" (geofence-relevant), not just R01-R04.
3. **V-E7 / E5**: D6 Decision Making rubric top band is truncated in both files -- missing "and making effective, evidence-based decisions."
4. **B1/B2**: "Focus Area (example)" legend entry and "Survey Area" vs "Search Area" terminology are missing from both files.

**Minor issues (nice to fix):**
- Pi camera cable missing from BRIEF_EXTRACTED equipment table
- Rubric lower bands (0-68) only in BRIEF_VISUAL, not in BRIEF_EXTRACTED
- D1/D4 presentation details only in BRIEF_VISUAL, not in BRIEF_EXTRACTED
- Several paraphrased rubric descriptors differ from exact PDF wording
- Equipment description "Computer" rendered as "Companion computer" in BRIEF_EXTRACTED
- "Peer weighting details to follow" statement missing from BRIEF_EXTRACTED

**Verdict**: The combined extractions capture all requirements (R01-R12), all deliverables (D1-D7), all D6/D7 section structures, all rubric criteria and top-band descriptors, all equipment, all URLs, all footnotes, and all version history. The map polygon color error in BRIEF_VISUAL is the most significant factual mistake. The rubric truncation in Decision Making should be corrected. With these fixes applied, the extraction would be a reliable reference document.
