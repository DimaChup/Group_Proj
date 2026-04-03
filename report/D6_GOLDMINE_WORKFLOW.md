# D6 Goldmine Report -- Master Workflow & Needs Document

**Report**: D6 Company Report (50% of grade)
**Current score**: 84.0/100 (v5 scoring, 2026-04-03)
**Target**: 85+ (top first-class band)
**Pages**: 151 total (15 counted body + cover/exec/intro/refs + 29 appendices A-AB)
**File**: `report/main.tex`

---

## Scoring History

| Version | Date | Specialist (40%) | Decision (40%) | Communication (20%) | Total |
|---------|------|-------------------|----------------|----------------------|-------|
| v1 | 2026-03-24 | -- | -- | -- | ~74 |
| v4 | 2026-03-27 | 82 | 80 | 78 | 80.4 |
| v5 | 2026-04-03 | 85 | 85 | 80 | 84.0 |

---

## What I Want From This Report

### Must-Haves
1. **Table of Contents** at the start (after cover page, before exec summary)
2. **Comprehensive yet well-organized** -- 151 pages is a goldmine but must be navigable
3. **Every claim backed by data** -- no vague statements, every metric cited
4. **All placeholder figures replaced** -- no `\fbox{\parbox{}}` remaining
5. **Cross-references working** -- every \figref, \tabref, \secref resolves
6. **Clean compilation** -- zero errors, minimal warnings
7. **Professional appendix lettering** -- A through AB, consistently labeled

### Ways to Present Data Better
- **Comparison tables** instead of prose for A/B decisions
- **Before/after screenshots** (simulation, ground station, detection)
- **Radar/spider charts** for multi-criteria comparisons
- **Timeline diagrams** for development progression
- **Flowcharts** for decision processes (not just state machine)
- **Box plots / violin plots** for distribution data (GPS accuracy, inference times)
- **Heatmaps** for spatial data (detection density, search coverage)
- **Pareto fronts** for optimization tradeoffs (already have some)
- **Annotated photographs** of hardware with callouts
- **Side-by-side subfigures** for model comparison results

### Ways to Optimize Structure
- **Appendix index/guide** at the start of appendices
- **Each appendix starts with a 1-line "why this matters" summary**
- **Body sections reference appendices explicitly** ("see Appendix H for full analysis")
- **Consistent heading hierarchy** across all sections
- **Key findings boxes** (infobox environment) for standout results
- **Section summaries** at end of each body section (1-2 sentences)

### Known Gaps (from v4 scoring)
1. No outdoor flight data (simulation/bench only) -- mitigate with honest evaluation
2. Some MCDA scores feel self-serving -- add sensitivity analysis on weights
3. No precision-recall curve for threshold selection
4. Intro has [NAME] placeholders for 4/5 team members
5. No hardware photographs (assembled drone, Pi setup, field day)
6. No ground station screenshot
7. Train/val overlap acknowledged but not resolved
8. Missing decisions: why 20% overlap? why 30m NFZ buffer? why 120s verify timeout?

### Improvement Checklist (iterate until all checked)
- [x] TOC added and rendering correctly
- [ ] All [NAME] placeholders filled
- [ ] All \fbox placeholders replaced with real figures
- [x] Exec summary mentions field day pivot and weather adaptation
- [ ] MCDA sensitivity analysis added (change weights, does winner change?)
- [ ] Missing decision rationale added (overlap, NFZ buffer, verify timeout)
- [ ] Hardware photos included (or noted as unavailable with explanation)
- [ ] Ground station screenshot included
- [x] Each body section has summary sentence at end
- [x] Appendix index/guide page added (appendix labels fixed)
- [ ] Cross-references all resolve (no ?? in compiled PDF)
- [ ] Bibliography cleaned (no duplicate entries, all cited)
- [ ] Page count verified (15 pages body)
- [ ] Compiles cleanly with zero errors

---

## Scoring Rubric (score against this every cycle)

### Specialist Skills & Problem-Solving (40%)
- **90+**: Exceptional system with evidence of independent problem-solving beyond taught material
- **83-89**: Complete pipeline with quantified results, creative solutions, initiative
- **72-82**: Working system with good evidence, some gaps in testing
- **Below 72**: Incomplete or poorly evidenced

### Decision Making (40%)
- **90+**: Every decision evidence-based with sensitivity analysis, stakeholder considered
- **83-89**: MCDA tables, STEEPLE, decisions-that-changed, pre-emptive Q&A
- **72-82**: Decisions documented but some feel post-hoc
- **Below 72**: Decisions not justified

### Communication (20%)
- **90+**: Professional publication quality, innovative visualizations, no placeholders
- **83-89**: Clean LaTeX, real figures from real data, good tables, clear equations
- **72-82**: Functional but some rough edges (placeholders, missing photos)
- **Below 72**: Poor formatting, missing figures

---

## Wave 1 Findings (2026-04-03)

### Body & Structure
- Body is **29 pages** -- needs trimming to stay within limits
- TOC added, appendix labels fixed, exec summary updated, section summaries added

### Broken References
- **5 broken refs** found (1 already fixed, 4 remaining)
- Check all `\ref{}`, `\figref{}`, `\tabref{}`, `\secref{}` for `??` in compiled PDF

### Bibliography
- **6 duplicate bib entries** -- deduplicate in `.bib` file
- **15 duplicate labels** across sections -- rename to unique identifiers

### Acronyms
- **17 undefined acronyms** -- add `\newacronym` or inline definitions on first use

### Missing Visuals (3 critical)
1. **Hardware photo** -- assembled drone, Pi setup, or field day equipment
2. **Ground station screenshot** -- browser dashboard (pi_flight.py or passive_watch.py)
3. **Detection examples** -- montage of successful detections at various altitudes

---

## Top 5 Actions to Reach 87+ (from v5 scoring)

1. **Hardware photos** -- even bench photos of Pi + Cube + camera assembly (Specialist +2)
2. **Ground station screenshot** -- capture from browser dashboard (Communication +3)
3. **MCDA sensitivity analysis** -- vary weights per table, show winner stability (Decision +3)
4. **Detection montage** -- grid of detections at 15m/25m/35m from video analysis (Specialist +2)
5. **Clarify preliminary measurements** -- label bench/sim results honestly, note what outdoor data would add (Decision +1)

---

## Cycle Tracking

### Cycle 1 (current)
- [x] Score (v5) -- 84.0 (Specialist 85, Decision 85, Communication 80)
- [x] Section-by-section review -- Wave 1 agents completed
- [ ] Apply improvements (in progress)
- [ ] Re-score

### Cycle 2
- [ ] Score (v6)
- [ ] Focus on weakest areas
- [ ] Apply improvements
- [ ] Re-score

### Cycle 3
- [ ] Final score (v7)
- [ ] Polish pass
- [ ] Compile verification
- [ ] Final assessment
