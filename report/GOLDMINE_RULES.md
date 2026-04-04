# D6 Goldmine Report — Rules & Scoring Guide

## What This Is

The goldmine is a **240+ page comprehensive reference document**. It is NOT submitted directly.
The team mines from it to write the final 15-page D6 submission. It should contain:
- Every piece of data, analysis, and evidence the project produced
- Multiple presentations of the same data (tables, charts, prose)
- Honest evaluation alongside achievements
- Literature context for every design decision

## Purpose

1. **Colleagues can pick content** for their sections of the final report
2. **All claims are backed by evidence** — no unsupported statements
3. **Data is presented visually where possible** — charts > tables > prose
4. **Structure is clear and navigable** — TOC + appendix guide + cross-references

## Scoring Criteria (3 axes, each 0-100)

### Specialist Knowledge (weight: ~35%)
- Deep understanding of SAR, CV, GPS estimation, flight control
- Accurate technical content (no factual errors)
- Literature context (how does our work compare to published systems?)
- Quantified claims (not "good accuracy" but "CEP50 = 2.3m")
- Appropriate use of equations, models, error analysis

### Decision Making (weight: ~35%)
- Every design decision has: problem → alternatives → criteria → selection → evidence
- MCDA tables with weighted scores
- "Decisions That Changed" — evidence-based adaptation
- Alternatives treated fairly (not strawman dismissals)
- Risk management and contingency planning

### Communication (weight: ~30%)
- Clear, professional writing (active voice, no filler)
- Figures: properly captioned, referenced, and informative
- Tables: labeled, referenced, no duplicate data
- Logical flow (transitions between sections)
- Hardware photos, screenshots, real-world evidence
- Consistent terminology and numbers throughout

## Quality Rules

### Content
- Every claim must have a number or reference
- Every design decision must list alternatives considered
- Every figure must be captioned with what to look for
- Every appendix must be cross-referenced from the body
- Present same data multiple ways (table + chart + prose summary)
- Literature comparison for every major technical area

### Writing
- Active voice ("we designed" not "the system was designed")
- No self-congratulatory language ("comprehensive", "robust", "novel")
- Quantify everything ("reduces error by 42%" not "significantly improves")
- Each paragraph starts with a topic sentence
- Sentences under 40 words
- Consistent tense (present for system description, past for what was done)

### Visual
- Every section >1 page should have at least one figure or table
- Figures use consistent style (serif font, 300 DPI, same color palette)
- Data better as chart than table, table better than prose
- Photos for hardware, screenshots for software, generated charts for data
- [PHOTO NEEDED] placeholders where real images are required

### Structure
- Body sections: 15 pages (design rationale, system desc, requirements, evaluation)
- Appendices: unlimited, organized by theme with guide table
- Every appendix letter matches the guide table
- Cross-references: body → appendix (not orphan appendices)
- FloatBarrier between heavy figure/table sections

## Current Status (v16)

| Metric | Value |
|--------|-------|
| Pages | ~246 |
| Errors | 0 |
| Score | 86.8/100 |
| Figures | ~110+ |
| Tables | ~115 |
| Citations | 108 |
| Appendices | 36 |
| Cross-refs | All 36 linked from body |

## Path to 90+

| Action | Time | Impact |
|--------|------|--------|
| Hardware photo (annotated) | 15 min | +1.5 |
| Ground station screenshot | 10 min | +1.0 |
| Detection montage at altitudes | 15 min | +1.0 |
| Fill teammate names | 5 min | +0.5 |
| Confusion matrix in body | 10 min | +0.5 |
| **Total** | **55 min** | **+4.5 → ~91** |

## Ceiling

- Without flight data: ~89
- With one outdoor flight: ~92
- With full demo day data: ~95+

## Version History

| Version | Commit | Pages | Score | Key Changes |
|---------|--------|-------|-------|-------------|
| v8 | 26bbd70 | 206 | 85.2 | STEEPLE, alternatives, figure insertions |
| v9 | 61ae97b | 206→238 | 85.2 | 10 new figures, transitions, requirements fixes |
| v13 | 9d08daa | 238 | 86.3 | All figures inserted, bibliography fixed |
| v14 | a65036b | 246 | 86.8 | Final polish wave — all body sections |
| v16 | 79bed38 | 246 | 86.8 | Consistency, GPS deep, captions, cross-refs |
