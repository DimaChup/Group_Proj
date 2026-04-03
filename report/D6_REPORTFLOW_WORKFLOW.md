# D6 Reportflow (17-page) -- Workflow & Scoring Document

**Report**: D6 Reportflow -- condensed focused version of Goldmine
**Current score**: v2 pending re-score (v1: 81.0)
**Target**: 83+ (matching or exceeding goldmine body quality)
**Pages**: ~17 (self-contained, follows D6 structure)
**File**: `report/reportflow/main.tex`

---

## What This Report Should Be

The reportflow is a **standalone focused version** that follows the D6 structure exactly:
1. Executive summary
2. Design rationale (with MCDA, STEEPLE)
3. System description (architecture, CV, path planning, state machine, GPS)
4. Requirements verification (R01-R12 evidence)
5. Evaluation (plus/delta, honest assessment)

It should read like a polished submission-ready D6 body -- the "if we could only submit 17 pages" version.

**NOT a summary of the goldmine.** It follows the same structure but is tighter, with the best content from the goldmine distilled.

---

## Scoring Rubric (same as D6)

Score against the same 3 criteria:
- Specialist Skills & Problem-Solving (40%)
- Decision Making (40%)
- Communication (20%)

---

## Scoring History

| Version | Date | Specialist (40%) | Decision (40%) | Communication (20%) | Total |
|---------|------|-------------------|----------------|----------------------|-------|
| v1 | 2026-04-03 | 78 | 82 | 85 | **81.0** |
| v2 | 2026-04-03 | -- | -- | -- | pending |

---

## Improvement Checklist
- [x] Follows D6 4-section structure exactly (exec summary, design rationale, system desc, req verification, evaluation)
- [x] All key metrics included (mAP50=0.995, 4.8 FPS TFLite / 9 FPS NCNN, CEP50=2.3m, 20 states, 58 test scripts, 127 unit tests)
- [x] At least 1 MCDA table (inference backend trade-off, Table 5)
- [x] STEEPLE coverage (all 7 dimensions, Table 4)
- [x] Requirements verification table (R01-R12, Table 13)
- [x] Plus/delta evaluation (6 plus, 6 delta, honest assessment)
- [x] Real figures -- architecture.pdf exists, all 14 figure references verified against ../figs/
- [x] Section transitions -- all major section boundaries now have narrative bridges
- [x] MCDA sensitivity note added (weight perturbation robustness)
- [x] Composite score weight robustness note added (Section 11)
- [x] Requirements table references specific test scripts and sections
- [x] Conclusion section added (3 sentences)
- [x] STEEPLE intro rewritten to integrate with priority ordering
- [x] System description intro strengthened with "what/why/how" framing
- [x] Architecture subsection rewritten (code scale, design principle upfront)
- [ ] Bibliography -- currently zero citations in reportflow (needs \cite{} entries)
- [ ] Hardware photos -- assembled drone, Pi setup
- [ ] Compiles cleanly -- verify with pdflatex/lualatex
- [ ] Page count verified (~17-20 pages)
- [ ] Score independently (v3)

---

## v2 Changes (2026-04-03)

### Added sections (Agent 17):
1. **Executive Summary** -- concise overview with all key metrics (mAP50, FPS, CEP50, states, tests)
2. **STEEPLE Context Analysis** (Section 4) -- all 7 dimensions with design impact column
3. **MCDA: Inference Backend Trade-off** (Section 5) -- 4 backends scored on 6 weighted criteria; NCNN wins at 4.4/5
4. **System Description** (Section 17) -- architecture, state machine (20 states), CV pipeline, GPS estimation (CEP50=2.3m), testing infrastructure (58 scripts, 127 unit tests)
5. **Requirements Verification** (Section 18) -- R01-R12 with quantitative evidence; 10 met, 2 partially met
6. **Evaluation: Plus/Delta** (Section 19) -- 6 plus items, 6 delta items, honest assessment (sim 7.7/10, real 2.1/10)

**Note**: Agent 17 added all 6 missing sections in a single pass. Report went from skeleton to complete D6 structure.

### Key metrics now present:
- mAP50 = 0.995
- 4.8 FPS (TFLite) / 9 FPS (NCNN) on Pi 5
- CEP50 = 2.3m GPS estimation accuracy
- 20-state FSM
- 58 test scripts, 127 unit test functions
- 216-configuration parameter sweep
- 12.6 Wh search energy (10.9% of battery)
- >99.97% single-pass detection probability

### Figures needed:
- `architecture_overview.pdf` -- system architecture diagram (referenced in Section 17)
  - If not available, remove the \includegraphics and figure environment

---

## Cycle Tracking

### Cycle 1 (v1 -> v2)
- [x] Score current state (v1: 81.0)
- [x] Identify gaps: missing STEEPLE, MCDA, system description, requirements verification, plus/delta
- [x] Apply improvements: added 6 new sections
- [ ] Re-score (v2)

### Cycle 2 (planned)
- [ ] Add architecture_overview figure (or remove reference)
- [ ] Compile and verify page count
- [ ] Score v2
- [ ] Address any remaining gaps
