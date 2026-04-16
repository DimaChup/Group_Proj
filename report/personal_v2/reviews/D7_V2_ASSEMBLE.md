# D7 V2 Assembly Report

## Output
- File: `report/personal_v2/main_v2.tex` (new, does not overwrite `main.tex`)
- PDF: `report/personal_v2/main_v2.pdf`
- Total pages: **7** (1 cover + 6 body including rubric map)
- Body-only page count (excluding cover): **6** pages
- PNG render: `v2_page-1.png` ... `v2_page-7.png` at 150 dpi

## Compile
- Two passes of `pdflatex -interaction=nonstopmode main_v2.tex` ran clean.
- Only warnings (not errors):
  - A couple of underfull hboxes inside the rubric-map table cells (long `DESIGN_DECISIONS.md:107-109` token wrapping) — cosmetic, no action.
  - One 9.5pt overfull hbox in slot 04 around "brain-dump.md" (long verbatim token at a line break) — not fixed; well below the visible-bleed threshold.
  - `rerunfilecheck` warning on first pass (expected, fixed by second pass).
- No actual LaTeX errors, no missing packages, no broken `\input`.

## Preamble
Compact preamble per spec:
- `11pt,a4paper`
- Geometry 1.8/1.8/2/2 cm
- `parskip` 0.3em + `parindent 0pt`
- `titlesec [compact]` with `titlespacing* {\section}{0pt}{0.6em}{0.3em}`
- `linespread 1.05`
- `enumitem` with `itemsep=0pt,topsep=2pt,partopsep=0pt`
- `lmodern` + `microtype` (no font-expansion error)
- `tabularx,booktabs,array,xcolor,graphicx,hyperref`
- `\definecolor{headblue}` added here (cover page references it)

Cover page input via `\input{drafts/cover_page}` — renders correctly.

## Rubric Map Table
Placed immediately after `\input{drafts/cover_page}` on page 2, above slot 01:

| Question | Section | Key evidence | Rubric hit |
|---|---|---|---|
| Q1 My role | S1 My role | Allocated CV lead vs emergent infra owner; scope-drift mechanism; Kolb reframing of "trust my hands over a conversation." | Specialist; Self-awareness |
| Q2 My team | S2 My team | Kickoff structure, two drifts, renegotiation (DESIGN_DECISIONS.md:107-109); cadence vs task-division trade-off. | Team; Decision |
| Q3 My impact | S3 My impact | Full Kolb cycle; sim-first architecture; 1411->754-line refactor, 146 pytests; bbox bug 3d62e6a. | Specialist; Communication |
| Q4 My support | S4 My support | Edward (mavproxy), Robin (state-machine renegotiation), Demetro (FDR), PM (cadence); specific mechanisms. | Team; Self-awareness |

Uses `tabularx` with an X-column so the "Key evidence" column wraps cleanly.

## PNG filenames
```
v2_page-1.png  cover
v2_page-2.png  rubric map + start of S1 My role
v2_page-3.png  S1 tail / S2 My team
v2_page-4.png  S2 tail / S3 My impact
v2_page-5.png  S3 My impact
v2_page-6.png  S4 My support
v2_page-7.png  S4 tail (ends mid-page)
```

## First visual observations
- Cover page (p1) renders identically to the V1 build (headblue colour defined in preamble).
- Rubric map (p2) is compact, 4 rows, X-column wraps nicely — assessor scan target achieved.
- Body typography is tight but not cramped; single-column, clear section headings, inline `\texttt{}` citations to commits and files read fine at 150 dpi.
- S3 My impact is the densest section (it is the Kolb-cycle spine) and sits roughly in the middle (pp 4-5), which is the right rhythm.
- Last body page (p7) ends comfortably mid-page — room for minor trims or an extra bullet without spilling to page 8.
- No overflows into margins visible in the PNGs; no orphaned headings; no section starts on the last line of a page.
- Estimated body length: ~4177 input words rendering to 6 body pages is consistent with the compact preamble targeting ~700 wpp.

## Next steps (suggested, not done)
- Consider a short (4-6 item) "evidence index" at end of slot 04 if the last page looks empty in the printed version.
- If the brief caps the body at 5 pages, V2 is one page over and would need either: (a) tightening slot 01 intro, or (b) moving the rubric map to the cover page back. Flag for the user.
