# GPS Estimation Deep Appendix -- Final Review

**File**: `report/sections/gps_estimation_deep.tex` (2233 lines, ~31 pages)
**Reviewed**: 2026-04-04
**Companion appendices**: `localization_approaches.tex`, `estimation_evaluation.tex`

---

## 1. Cross-References to New Appendices

### Before this review
- Only 2 references to `\ref{sec:estimation-eval}` (lines 1217, 2024)
- Zero references to `\ref{sec:loc-approaches}`

### After this review (FIXED)
- **New "Companion appendices" paragraph** added at the top (after line 9), introducing both appendices and explaining their relationship
- **localization_approaches.tex** now referenced in:
  - Top companion paragraph (new)
  - GSD equation explanation (Eq. 1, referencing Approach 1: Direct Georeferencing)
  - Three-level estimation architecture (Section 5, Sec. V), pointing readers to the full 10-approach survey
- **estimation_evaluation.tex** now referenced in:
  - Top companion paragraph (new)
  - Error budget section (pointing to Figure error_budget_breakdown)
  - DJI validation section (new "Extended evaluation" paragraph pointing to bullseye_comparison, convergence_plot_eval)
  - Ground-truth comparison (pointing to Section ground-truth-comparison, Figure estimator_comparison)
  - Convergence behaviour (pointing to Figure convergence_plot_eval)
  - Spatial clustering (pointing to Table clustering_tradeoffs)
  - Multi-pass section already had a reference to Figure heading_bias (no change needed)

---

## 2. Three Accuracy Tables -- Are They Clearly Distinguished?

The appendix contains three tables that track accuracy progression. They are now well-differentiated:

| Table | Label | Purpose | Scope |
|-------|-------|---------|-------|
| `tab:accuracy-progression` (line 55) | **Preview table** | Quick overview of CEP at each phase | 4 rows, compact, in the Strategy Roadmap |
| `tab:accuracy-journey` (line 1015) | **Consolidation table** | Full per-phase analysis with "Why it improves" column | 6 rows including measured DJI data |
| `tab:state-accuracy` (line 1348) | **Detailed breakdown** | Per-state with specific error sources eliminated | 5 rows with detailed conditions and N_obs |

**Assessment**: The three tables serve distinct purposes. The text at line 1010 explicitly says "consolidates the preceding analysis... (cf. the preview in Table accuracy-progression; a more detailed breakdown appears in Table state-accuracy)". This is good. No confusion expected.

---

## 3. Four-Phase Detection Flow -- Is It Well-Illustrated?

The four-phase flow is illustrated by **four** figures plus a decision-flow diagram:

1. **Figure `fig:accuracy-progression`** (line 1471): TikZ state boxes with proportional CEP circles below, arrows showing phase transitions
2. **Figure `fig:creep-up`** (line 1643): Progressive refinement trajectory showing pitch angle decreasing, error circles shrinking, false positive branch
3. **Figure `fig:two-step-decision-flow`** (line 1753): Complete decision flow diagram with false positive recovery path
4. **Figure `fig:cooperative-loop`** (line 1795): Cooperative vision-flight feedback loop (triangle diagram)

Plus the side-by-side three-level comparison (Figure `fig:three-level-comparison`, line 985) and the before/after tilt compensation (Figure `fig:tilt-before-after`, line 594).

**Assessment**: Excellent coverage. The four-phase flow is illustrated from multiple perspectives: accuracy progression (quantitative), trajectory (spatial), decision flow (logic), and feedback loop (architecture). No gaps.

---

## 4. New Figures -- Are They Referenced?

| Figure | Defined In | Referenced in gps_estimation_deep.tex? |
|--------|-----------|---------------------------------------|
| `fig:bullseye-comparison` | estimation_evaluation.tex:71 | YES (new, via "Extended evaluation" paragraph) |
| `fig:convergence-plot-eval` | estimation_evaluation.tex:246 | YES (new, in two places: DJI validation and convergence sections) |
| `fig:centrality-weighting` | estimation_evaluation.tex:183 | YES (already existed at line 1217) |
| `fig:heading-bias` | estimation_evaluation.tex:273 | YES (already existed at line 2024) |
| `fig:error-budget-breakdown` | estimation_evaluation.tex:168 | YES (new, added after error waterfall figure) |

**Assessment**: All five new figures are now referenced. Previously only centrality_weighting and heading_bias had references.

---

## 5. Content Duplication with estimation_evaluation.tex

### Overlapping topics identified:

| Topic | In gps_estimation_deep.tex | In estimation_evaluation.tex | Duplication? |
|-------|--------------------------|----------------------------|-------------|
| Error budget table | Table `tab:error-budget` (9 sources, line 279) | Table `tab:error-budget-relative` (6 sources, line 140) | **Partial**: deep has 9 sources, eval has 6 with variance percentages. Different perspectives. |
| DJI validation results | Table `tab:dji-results` (line 1288) | Table `tab:ground-truth-results` (line 196) | **Significant overlap**: both show CEP from DJI replay. Deep has 7 metrics, eval has 7 strategies. |
| Convergence behaviour | Figure `fig:convergence-plot` (TikZ, line 2005) | Figure `fig:convergence-plot-eval` (included PDF, line 246) | **Moderate**: both show error vs time, but deep's is TikZ with SITL data, eval's is PDF with DJI data. |
| Error waterfall | Figure `fig:error-waterfall` (included PDF, line 307) | Figure `fig:error-waterfall` (included PDF, line 159) | **Same file reference**: both include `error_waterfall.pdf`. |
| Clustering thresholds | Not in deep | Table `tab:clustering-tradeoffs` (line 107) | No duplication (only in eval). |

### Actions taken:
- Added cross-references where deep discusses DJI results, pointing to eval's extended treatment
- Added "Extended evaluation" paragraph before directional bias discussion, steering readers to eval for the full comparison
- Added cross-reference from clustering section to eval's threshold comparison table
- **Did NOT delete any content** -- the overlap is complementary (deep derives theory, eval validates empirically)

### Remaining acceptable overlap:
The DJI results table (`tab:dji-results`) and the ground-truth results table (`tab:ground-truth-results`) overlap conceptually but present different cuts of the data. Deep shows metrics (CEP50, CEP95, max, mean, fused), while eval shows strategy comparison (single frame through multi-pass). Both tables are needed in their respective contexts.

---

## 6. Equations -- Numbered and Referenced?

### Before this review: 8 unreferenced equations
- `eq:gsd-deep` -- FIXED (added reference in GSD paragraph)
- `eq:resize` -- FIXED (added reference before model output paragraph)
- `eq:tilt-offset` -- FIXED (added reference in geometry paragraph)
- `eq:focal-px` -- FIXED (added reference in focal length explanation)
- `eq:zero-offset` -- FIXED (added reference in zero-offset proof)
- `eq:full-projection` -- FIXED (added reference in proof paragraph)
- `eq:rolling` -- FIXED (added reference in rolling average description)
- `eq:cumulative` -- FIXED (added reference in cumulative average description)
- `eq:kalman-R-deep` -- FIXED (added reference in noise model explanation)
- `eq:haversine` -- FIXED (added reference in clustering section)
- `eq:multi-pass-cep` -- FIXED (added reference in multi-pass model description)

### After this review: All 24 labeled equations are referenced at least once.

---

## 7. Overall Assessment

**Strengths:**
- Exceptionally thorough mathematical treatment (24 numbered equations, all now referenced)
- Progressive structure from fundamentals (Part I) to validation (Part VII) is well-organized
- 15 TikZ diagrams generated inline -- impressive visual quality
- Three accuracy tables serve distinct purposes and are clearly distinguished
- Four-phase flow is illustrated from multiple angles (6 figures)
- Literature comparison (Table literature-comparison) positions the work well

**Minor notes (not actioned, just observations):**
- The appendix is long (~31 pages). The roadmap at the top helps, but a reader who only wants the validation results needs to scroll far. The companion estimation_evaluation.tex helps by providing a focused evaluation document.
- The error waterfall figure (`error_waterfall.pdf`) is referenced in both this appendix and estimation_evaluation.tex with the same filename. This is fine (LaTeX will include the same file), but the captions describe it differently.

**Edits made in this review:**
- 1 new "Companion appendices" paragraph (top of appendix)
- 11 equation cross-references added (all previously unreferenced equations now referenced)
- 6 new cross-references to estimation_evaluation.tex figures and sections
- 2 new cross-references to localization_approaches.tex
- 0 content deleted
