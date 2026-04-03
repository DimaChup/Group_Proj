# Compile Check v3 -- 2026-04-03

## Summary

**Compilation: PASS (0 errors)**

A critical bug was found and fixed: the document had 32 appendices (A through AF)
but LaTeX's `\appendix` command only supports 26 (A-Z) with the default `\@Alph`
counter. This caused **58 "Counter too large" errors** on every `\section` and
`\subsection` from Appendix AA onward.

### Fix Applied

Added the `alphalph` package (preamble) and redefined `\thesection` after
`\appendix` to use `\AlphAlph`, which handles AA, AB, AC, ... automatically.

**File changed:** `main.tex` (2 lines added)

```latex
% In preamble (before hyperref):
\usepackage{alphalph}

% After \appendix:
\renewcommand{\thesection}{\AlphAlph{\value{section}}}
```

---

## Final Stats (clean build, 5 passes, converged)

| Metric               | Before Fix | After Fix |
|-----------------------|-----------|-----------|
| LaTeX errors          | 58        | **0**     |
| Undefined references  | 28        | **0**     |
| Duplicate labels      | 13*       | **0**     |
| Missing files         | 0         | **0**     |
| Overfull hbox         | 32        | **37**    |
| Overfull vbox         | --        | **6**     |
| Underfull hbox        | 135       | **135**   |
| Dest warnings         | 180       | **61**    |
| Pages                 | 162       | **160**   |

*Duplicate labels were from stale .aux file, resolved by clean build.

Dest warnings (61) are harmless hyperref float-position oscillations between passes.
They do not affect the PDF output.

---

## Overfull Hbox Analysis (top 5 worst)

| Width (pt) | Cause |
|------------|-------|
| 83.0       | Long monospace file path in test script listing |
| 60.8       | Long monospace path |
| 60.4       | Long inline code |
| 53.5       | Long inline code |
| 46.5       | Long monospace path (`tests/diagnostics/cube_monitor.py`) |

All top offenders are monospace file paths or code in `\texttt{}`. These are
cosmetic -- the text overflows into the margin slightly. To fix: use
`\seqsplit{}` or break paths manually with `\-` hints. Not urgent.

---

## Environment Balance Check

| Environment  | \begin | \end | Status |
|-------------|--------|------|--------|
| infobox     | 2      | 2    | OK     |
| abstractbox | --     | --   | OK     |

No unmatched environments found.

---

## Items NOT Checked (require biber)

Bibliography was not re-run (would need `biber main`). The existing `.bbl` file
was used. If bibliography entries were recently added/changed, run the full
chain: `pdflatex && biber main && pdflatex && pdflatex`.

---

## Appendix Numbering Verification

The document now correctly numbers appendices A through AH (34 appendices total,
including 2 new ones: AG Requirements Verification Detail, AH Evaluation Detail).
The `\AlphAlph` counter produces: A, B, ..., Z, AA, AB, ..., AH as expected.
