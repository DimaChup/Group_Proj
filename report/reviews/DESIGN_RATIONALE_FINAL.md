# Design Rationale Final Review (2026-04-04)

## Summary

The design rationale section is strong -- approximately 6 pages, well-structured, with quantified evidence throughout. Four MCDA tables are complete with weights summing to 1.0, all weighted totals verified correct. Seven "Decisions That Changed" entries each follow the problem-evidence-fix-outcome pattern. Writing is concise, active voice predominates.

## Issues Found and Fixed

### 1. Missing cross-references to localization appendices (CRITICAL -- FIXED)
- **Problem**: No mention of `\ref{sec:loc-approaches}` (10-method localization survey) or `\ref{sec:estimation-eval}` (ground-truth validation). Target localization is a key design decision that was entirely absent from the body section.
- **Fix**: Added new subsection "Target Localization Strategy" (Section 3.7) between Coverage Path Planning and State Machine Design. Covers: problem statement, ten approaches surveyed, selection criteria (compute budget, sensor requirements, GPS noise, complexity), why IVW clustering was chosen over Kalman filter / visual odometry / bundle adjustment, and CEP50 = 2.3m validation result.
- **Also added**: Cross-reference from CENTERING state paragraph to estimation evaluation appendix. Updated section summary to mention localization strategy and both appendices.

### 2. STEEPLE Social row lacked quantification (MINOR -- FIXED)
- **Problem**: "Reduces volunteer foot-search time from hours to minutes" -- vague claim without numbers.
- **Fix**: Replaced with "covers the 0.12 km^2 survey area in ~6 min versus ~4 h for a 6-person ground team at 1 m/s" -- derived from the search pattern parameters.

### 3. Circular camera self-reference (MINOR -- FIXED)
- **Problem**: Hardware platform section referenced `Section~\ref{sec:camera-rationale}` for the rolling-shutter claim, but that label points to the Camera Selection subsection later in the same section -- creating a forward self-reference that reads as circular.
- **Fix**: Added "see ... for the full validation" to clarify it's a forward reference to detailed analysis, not a circular citation.

## Verified Correct (No Changes Needed)

### MCDA Tables
All four tables verified:
- **Companion computer**: Weights sum to 1.00. Pi 5 = 4.90 (correct), Jetson = 3.50, NCS2 = 2.35.
- **Communication**: Weights sum to 1.00. MAVProxy = 4.65 (correct), Direct = 2.65, ROS = 3.35.
- **Detection model**: Weights sum to 1.00. YOLOv8n = 4.75 (correct), SSD = 4.20, YOLOv8s = 3.95, YOLOv8m = 3.05.
- **Search pattern**: Weights sum to 1.00. Lawnmower = 4.65 (correct), Expanding = 3.65, Spiral = 3.00, Random = 2.15.

### Decision structure (problem -> alternatives -> criteria -> selection -> evidence)
Every subsection follows this pattern:
- Search params: 216-config sweep, coupling matrix, Pareto analysis
- Hardware: MCDA + sensitivity analysis, thermal/offboard alternatives fairly discussed
- Software: monolithic vs modular with quantified interface counts
- Detection model: MCDA, runtime comparison, SSD dataset caveat acknowledged
- Path planning: MCDA, IAMSAR compliance
- State machine: FSM vs BT vs reactive, quantified O(1) vs O(n log n) argument
- Autonomy: Sheridan levels, asymmetric cost analysis, timeout energy derivation

### Alternatives treated fairly
- Thermal imaging: acknowledged as superior for night/foliage, rejected on cost (4-18x budget)
- Jetson Nano: acknowledged as having strong community, scored fairly on each criterion
- ROS 2: acknowledged as recommended for multi-drone, rejected on complexity/timeline for single-node
- Behaviour trees: acknowledged composability advantage, rejected on audit complexity for sequential mission
- SSD MobileNet: caveat about COCO vs custom dataset comparison explicitly noted

### STEEPLE analysis
Project-specific content throughout -- references specific numbers (150 GBP, 3 kg AUW, 30m buffer, 120s timeout, 640x512 thermal resolution, SSSI boundary distances). Not generic.

### Cross-references to appendices
Now references: path-opt, decision-flow, states, centering-mitigation, evaluation, field-day, req-detail, loc-approaches, estimation-eval. Good coverage.

### Writing quality
- Active voice predominates
- Concise (no filler paragraphs)
- Every paragraph contains at least one quantified claim
- Technical terms defined on first use (GSD, FSM, MCDA, IVW, CEP)

## Remaining Minor Observations (Not Fixed -- Low Priority)

1. **SSD comparison fairness**: The text correctly notes the COCO vs custom dataset issue but could go further by stating "a definitive comparison would require retraining SSD on the same 366-image dataset, which was not performed due to time constraints." Current phrasing is adequate.

2. **Sensitivity analysis detail**: The text claims +/-0.05 weight perturbation across all 12 scenarios confirms Pi 5 rank, but the 12 scenarios are not enumerated. Acceptable for body text -- detail belongs in appendix.

3. **Field Day section**: Could cross-reference the localization appendix since FOV calibration directly feeds the estimation pipeline. Low priority since the connection is implicit.

## Final Assessment

Section is publication-ready. The localization subsection addition fills the most significant gap -- it was the only major design decision without body-section coverage. All eight checklist items from the review brief are satisfied.
