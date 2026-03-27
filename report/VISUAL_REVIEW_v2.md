# Visual Review v2 -- Full 86-Page PDF Inspection

Rendered at 150 DPI from `report/main.pdf`. Every page visually inspected.

---

## Summary

**Overall quality: GOOD.** All figures render correctly (no grey placeholders), all tables
are properly formatted, equations render cleanly, and the layout is professional throughout.
There are a handful of issues worth addressing before final submission.

---

## CRITICAL Issues

### 1. Page 19 -- Completely blank page (wasted space)
- **Section 4.1 Plus/Delta Summary** has a 2-line intro paragraph ("Table 14 summarises...")
  then the rest of the page is entirely blank white space.
- Table 14 appears on page 20, meaning LaTeX pushed the table to the next page and left
  page 19 almost empty.
- **Fix:** Add `[h!]` or `[ht]` placement to the table, or add `\vspace` fill, or restructure
  so the intro text and table are on the same page. Alternatively, move some Section 4.2
  content up.

### 2. Page 23 -- Almost entirely blank
- Section 4.3 "Lessons Learned" ends with only 3 lines of text at the top of page 23,
  leaving ~90% of the page blank.
- The References section starts on page 24.
- **Fix:** This is a natural section break so it is less egregious, but consider using
  `\vfill` or adjusting page breaks so it looks intentional, or pull some content forward.

---

## HIGH Issues

### 3. Page 4 -- Team member names redacted as [NAME]
- Table 1 (Contribution Summary) and the preceding "Team Members and Roles" section show
  `[NAME]` placeholders in red for 4 of the 5 team members.
- Only "Dmytro Chuprynyuk" is filled in.
- **Fix:** Replace all `[NAME]` with actual team member names before submission.

### 4. Page 3 -- GitHub repo URL visible in footnote
- Footnote 1 shows the full GitHub URL: `https://github.com/DimaChup/Group_Proj`
- Confirm this is intentional (the report mentions a public MIT-licensed repo in R12,
  so it likely is). If the repo should remain private until after marking, remove or
  anonymise this URL.

---

## MEDIUM Issues

### 5. Pages 1 -- Title page is sparse
- Title, author ("Dmytro Chuprynyuk, et al."), course/date line, then blank for the
  remaining ~80% of the page.
- No abstract, no university logo, no student IDs.
- **Consider:** Adding a university logo or abstract to fill the title page, unless the
  course template mandates this minimal format.

### 6. Page 15 -- Mission timeline figure (Figure 7) label overlap
- The timeline bar chart is clear, but the colored state labels inside the bars are small
  and some overlap slightly at transitions (e.g., "Centering" is compressed).
- Readable but could be improved with slightly larger font or wider bars.

### 7. Page 37 -- Equation (1) rendering
- The FOV calibration equation on page 37 renders correctly, but the inline fraction
  `5.02 mm x 1000 mm / W_sensor` is dense. It is still legible.

### 8. Pages 85-86 -- Figures 17, 18, 19 are photographs (not diagrams)
- These are real photographs (detection frame, satellite overlay, bench setup).
- They render correctly but are somewhat dark/low-contrast in the PDF, especially
  Figure 19 (bench setup photo). The caption text for Figure 19 is also very dense.
- **Consider:** Increasing brightness/contrast on the source images, or using a slightly
  larger figure size.

---

## LOW Issues (Minor Polish)

### 9. Page 2 -- Executive Summary density
- The executive summary is a solid wall of text. It is readable but dense.
- Consider adding a line break between the major subsections (Mission objective,
  System overview, Key design decisions, Results achieved, Weather adaptation).

### 10. Page 14 -- Figure 5 and Figure 6 subfigures
- The GPS estimation scatter plot (Figure 5a) and directional error (Figure 5b) are
  clear and well-labeled.
- Figure 6a and 6b are slightly small but readable. The bar chart colors are distinct.

### 11. Page 21 -- Figure 8 and Figure 9 subfigures
- Four subfigures across two figure environments. All render correctly.
- Figure 9b (detection heatmap) is particularly effective.
- The subfigure captions are slightly small but legible.

### 12. Page 48 -- Figure 10 (confidence vs altitude)
- The scatter plot with error bars renders cleanly. The "Sweet spot" annotation is clear.
- The dashed threshold line is visible. Good figure.

### 13. Page 51 -- Figure 11 and Figure 12
- Detection probability per flyover (Figure 11) renders correctly -- clean line plot.
- Inference latency breakdown (Figure 12) bar chart is clear with good color coding.

### 14. Page 83 -- Figure 14 (MAVLink communication topology)
- ASCII-style box diagram renders as a proper figure. Clean and readable.
- Connection labels and arrows are clear.

### 15. Page 85 -- Figure 17 caption is very long
- The caption for Figure 17 (example detection frame) runs to ~5 lines.
- Consider shortening or moving detail to the main text.

### 16. Page 86 -- Figure 19 caption is extremely long
- The caption for Figure 19 (bench-test setup) is ~8 lines of dense description.
- This is essentially a paragraph embedded in a caption. Consider shortening.

---

## Tables Review

All tables render correctly with proper borders, alignment, and formatting:

| Table | Page | Status | Notes |
|-------|------|--------|-------|
| Table 1 (Contributions) | 4 | Has [NAME] placeholders | Fix before submission |
| Table 2 (Companion MCDA) | 6 | OK | Clean weighted comparison |
| Table 4 (Comm MCDA) | 6 | OK | |
| Table 5 (Detection MCDA) | 7 | OK | 5-column comparison |
| Table 6 (Search pattern MCDA) | 7 | OK | |
| Table 10 (BOM) | 10 | OK | Cost breakdown clear |
| Table 12 (MAVLink commands) | 10 | OK | |
| Table 13 (Requirements) | 16 | OK | Large table, spans full width, readable |
| Table 14 (Plus/Delta) | 20 | OK | Well-structured, but pushed to next page |
| Table 16 (State transitions) | 26-27 | OK | Large 2-page table, proper continuation |
| Table 17 (Config params) | 28 | OK | Clean parameter listing |
| Table 18 (Training hyperparams) | 30 | OK | |
| Table 19 (Model comparison) | 30 | OK | |
| Table 20 (Failure modes) | 32 | OK | |
| Table 21 (Risk register) | 33 | OK | |
| Tables 22-59 | 34-86 | OK | All appendix tables render properly |

---

## Figures Review

All figures render as actual images (no grey placeholder boxes):

| Figure | Page | Type | Status | Notes |
|--------|------|------|--------|-------|
| Figure 1 (Module dependency) | 11 | Diagram | OK | Clean block diagram with color coding |
| Figure 2 (Pi companion system) | 12 | Diagram | OK | Hardware interfaces clear |
| Figure 3 (CV pipeline) | 12 | Diagram | OK | Pipeline stages with timing |
| Figure 4 (State transition) | 13 | Diagram | OK | Color-coded states, clean layout |
| Figure 5a,b (GPS scatter/error) | 14 | Plot | OK | Dual subfigures, clear |
| Figure 6a,b (GPS convergence) | 14 | Plot | OK | Dual subfigures, clear |
| Figure 7 (Mission timeline) | 15 | Timeline | OK | Color bars, minor label compression |
| Figure 8a,b (Detection perf) | 21 | Plot | OK | Confidence + detection rate plots |
| Figure 9a,b (Inference + heatmap) | 21 | Plot/Map | OK | Bar chart + spatial heatmap |
| Figure 10 (Conf vs altitude) | 48 | Plot | OK | Error bars, sweet spot annotation |
| Figure 11 (Det prob per flyover) | 51 | Plot | OK | Clean line plot |
| Figure 12 (Latency breakdown) | 51 | Bar chart | OK | Stacked bars with legend |
| Figure 13 (Test tier progression) | 60 | Diagram | OK | Simple tier boxes with arrows |
| Figure 14 (MAVLink topology) | 83 | Diagram | OK | Communication flow diagram |
| Figure 15 (Ground station) | 84 | Screenshot | OK | Dashboard screenshot, readable |
| Figure 16 (Hardware assembly) | 85 | Photo | OK | Labeled arrows, clear |
| Figure 17 (Detection frame) | 85 | Photo | OK | Detection overlay visible |
| Figure 18 (Lawnmower overlay) | 85 | Satellite+overlay | OK | Search pattern on map |
| Figure 19 (Bench setup) | 86 | Photo | OK | Slightly dark but readable |

---

## Equations Review

| Location | Content | Status |
|----------|---------|--------|
| Page 37 (Eq 1) | FOV calibration | OK -- renders correctly |
| Page 46 (Eqs 2-3) | Ground footprint W_x, L_y | OK |
| Page 47 (Eqs 4-5) | N_frames, Overlap | OK |
| Page 47 (Eq 6) | Pixel size model | OK |
| Page 55 (Eqs 7-10) | GSD, body-frame, heading rotation, WGS84 | OK |
| Page 56 (Eqs 11-12) | Rolling weighted average | OK |
| Page 57 (Eqs 13-17) | Kalman filter cycle | OK |
| Page 57 (Eqs 18-20) | Inverse-variance weighting | OK |
| Page 58 (Eq 21) | Haversine distance | OK |
| Page 74 (Eqs 23-24) | Footprint, focal length | OK |
| Page 74 (Eq 25) | Radial distortion | OK |
| Page 75 (Eqs 26-28) | DJI FOV, focal pixel, HFOV | OK |
| Page 81 (Eq 29) | CEP to scale | OK |
| Page 82 (Eqs 30-31) | Landing probability CDF | OK |

All equations render with correct LaTeX formatting. No broken symbols or misaligned fractions.

---

## Page Break / Layout Issues

| Page | Issue | Severity |
|------|-------|----------|
| 19 | Almost blank -- table pushed to next page | CRITICAL |
| 23 | ~90% blank after Lessons Learned ends | HIGH |
| 86 | Last page has Figure 19 + long caption, ends ~40% down the page | OK (final page) |

No orphan paragraphs (single lines at top/bottom of page) were observed.
No widows detected. Section headings always have at least 2-3 lines of text following them.

---

## Action Items (Priority Order)

1. **[CRITICAL]** Fix page 19 blank space (Table 14 placement)
2. **[HIGH]** Replace all `[NAME]` placeholders on pages 3-4 with real team member names
3. **[MEDIUM]** Consider filling page 23 blank space or accepting it as section break
4. **[LOW]** Shorten Figure 17 and 19 captions
5. **[LOW]** Add spacing to Executive Summary for readability
6. **[LOW]** Confirm GitHub URL in footnote is intentional

---

*Review completed 2026-03-27. All 86 pages inspected at 150 DPI.*
