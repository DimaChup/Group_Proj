# Report Directory Structure

All report-related files for AENGM0074 Group Design Project.

## Layout

```
report/
├── main.tex                 <- Group report (compile from this directory)
├── references.bib           <- Group report bibliography
├── extra_refs.bib           <- Additional references (not currently used)
├── sections/                <- All .tex section files (\input{sections/...})
├── figs/                    <- All figures + generator scripts (gen_*.py)
├── reviews/                 <- Review/scoring markdown files
├── guides/                  <- Briefs, checklists, brainstorm documents
├── report_pages/            <- Rendered page images (page_01.png .. page_86.png)
├── individual/              <- Empty placeholder (individual section drafts)
├── personal/                <- Individual reflective report (D7)
│   ├── main.tex             <- Compile from report/personal/
│   ├── references.bib
│   ├── sections/            <- Personal report sections
│   └── reviews/             <- D7 scoring/review files
└── team/                    <- Team process report
    ├── main.tex             <- Compile from report/team/
    ├── references.bib
    └── sections/            <- Team report sections
```

## Compilation

Each report compiles independently from its own directory:

```bash
# Group report (main)
cd report && pdflatex -interaction=nonstopmode main.tex

# Personal reflective report
cd report/personal && pdflatex -interaction=nonstopmode main.tex

# Team process report
cd report/team && pdflatex -interaction=nonstopmode main.tex
```

For full bibliography resolution, run biber between pdflatex passes:
```bash
pdflatex main.tex && biber main && pdflatex main.tex && pdflatex main.tex
```

## Figure Generation

Figure generator scripts live in `figs/` alongside their output:
- `gen_*.py` scripts produce PDF/PNG figures
- Run from `report/figs/`: `python gen_architecture.py`
- Generated figures are referenced by `\includegraphics` in section files

## Key Files

| File | Purpose |
|------|---------|
| `reviews/FINAL_SCORE.md` | Current scoring assessment |
| `reviews/SCORING_D6_v4.md` | Latest D6 scoring rubric analysis |
| `guides/CHECKLIST.md` | Report completion checklist |
| `guides/GOLDMINE_CHECKLIST.md` | Comprehensive improvement checklist |
| `guides/CONTENT_BRAINSTORM.md` | Content ideas and section planning |
