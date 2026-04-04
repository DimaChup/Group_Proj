# GPS Estimation Appendix Review

**File**: `report/sections/gps_estimation_deep.tex` (2212 lines)
**Reviewed**: 2026-04-03

---

## Overall Assessment: STRONG

This is a thorough, technically rigorous appendix that would score well in any engineering report. The mathematical derivations are correct, the error analysis is quantified, and the design decisions are well-justified with empirical data. The writing quality is high throughout.

---

## 1. Flow: "We detect something" to "We know exactly where it is"

**Verdict: Clear and logical.**

The narrative progression is:
- Problem statement (line 71): what inputs we have, what noise they carry
- Pipeline overview (line 86): 15-stage TikZ diagram showing full data flow
- Mathematics (line 181): GSD, body-frame projection, heading rotation, WGS-84
- Resize pipeline (line 251): how 1456x1088 maps to/from 640x640
- Error budget (line 272): nine sources, quantified
- Roll/pitch deep-dive (line 320): dominant error source, h*tan(theta) geometry
- Attitude compensation (line 392): the ray-tracing fix, 1440-test verification
- Centering mitigation (line 683): operational elimination of errors
- Three estimation levels (line 721): passive / hover / centering comparison
- Four-phase flow (line 1472): how the mission architecture implements all of this
- Validation (line 1257): DJI video and simulator confirmation

Each section builds on the previous one. A reader can follow the chain from pixel to GPS coordinate without jumping around.

## 2. Roadmap Accuracy

**Verdict: Accurate, with one omission (now fixed).**

All seven parts are present and match the descriptions. The Passive Estimation section (sec:passive-estimation, line 2125) was not mentioned in the Part VII roadmap entry. **Fixed**: added reference to Section passive-estimation in the Part VII roadmap description.

## 3. Error Sources

**Verdict: Comprehensive and well-quantified.**

Nine sources in Table 3 (tab:error-budget) with:
- GPS receiver noise: 2-3m CEP (hardware limit)
- Roll/pitch: 6.2m at 10 deg (dominant during flight)
- GPS timing lag: ~1m at 5 m/s (systematic)
- Barometric altitude: 0.5-1m drift
- Compass/yaw: +/-1-2 deg
- FOV/focal length: 0-5%
- Detection pixel noise: +/-2-3 px
- Resize mapping: 0 (exact inverse)
- Lens distortion: <0.5m at edges
- Camera vibration: discussed in prose (negligible, <0.1m after averaging)

All values are backed by either measurement (calibration sessions, DJI video) or calculation. The RSS totals (~7m flight, ~3m hover) are presented with an honest note that the measured CEP50 (2.3m) is lower than the theoretical RSS, and three reasons why are given.

## 4. Mitigation Strategies

**Verdict: All documented thoroughly.**

- **Attitude compensation**: Full rotation matrix derivation (Eq 5-10), 1440-test verification, before/after TikZ diagram, comparison with published approaches (Barber et al., NATO STANAG, DJI). Reduces 6.2m to 0.3m.
- **Centering**: Zero-offset proof (Eq 15-16), five independent error sources eliminated simultaneously (Table tab:centering-reduction). Well-argued as "elegant engineering" -- operational procedure eliminates errors rather than complex software.
- **GPS averaging**: Duration analysis with 1/sqrt(T) convergence, CEP vs time plot, five-point justification for 10s window. Clear diminishing returns argument.
- **Multi-pass averaging**: Heading diversity cancellation, quantified for 1-5 passes (Table tab:pass-accuracy), lawnmower pattern exploited as inherent source of heading diversity.
- **Spatial deduplication**: Haversine clustering with 30m threshold, rejected-targets list prevents reinvestigation.
- **SMART detection**: Consecutive-frame filter for false positive suppression.

## 5. Four-Phase Detection Flow

**Verdict: Clearly laid out with good diagrams.**

The four phases (SEARCH detection, CENTERING approach, CENTERING hover lock, VERIFY confirmation) are described in:
- Section sec:two-step (line 1472): narrative description of all four phases
- Section sec:detailed-accuracy (line 1334): per-state accuracy table
- Figure fig:creep-up: progressive refinement trajectory TikZ
- Figure fig:two-step-decision-flow: complete decision flow including false positive recovery
- Figure fig:accuracy-progression: CEP circles shrinking per phase

The false positive handling (sec:false-positive-handling) is well-integrated: 15s timeout, spatial deduplication, <1% mission time cost, four mitigation mechanisms.

## 6. Figures Placement

**Verdict: Good placement overall.**

Key figures are positioned correctly:
- Pipeline TikZ (fig:pipeline-flow): immediately after pipeline description
- Nadir geometry (fig:nadir-geometry): in the roll/pitch section
- Before/after compensation (fig:tilt-before-after): in the compensation section
- Three-level comparison (fig:three-level-comparison): after the comparative evaluation
- CEP vs time (fig:cep-vs-time): in the GPS averaging section
- Cooperative loop (fig:cooperative-loop): in the cooperative architecture section
- CEP comparison bar chart (fig:cep-comparison): in the empirical comparison
- Convergence plot (fig:convergence-plot): after the empirical comparison
- Multi-pass bias (fig:multi-pass-bias): in the multi-pass section

No figures are orphaned or misplaced.

## 7. Error Analysis to Design Decisions Connection

**Verdict: Strong and explicit.**

The connection is made in multiple places:
- Error budget (Table 3) directly motivates the three-level architecture
- Roll/pitch analysis motivates attitude compensation AND centering
- GPS timing lag motivates multi-pass averaging AND centering (v=0)
- Altitude effect motivates IVW weighting scheme
- Literature comparison (Table tab:literature-comparison) justifies deliberate simplifications
- "Design rationale" paragraph (line 974) explicitly connects levels to trade-offs
- Seven-method empirical comparison confirms analytical predictions

---

## Structural Issues Found and Fixed

### 1. Passive estimation missing from roadmap (FIXED)
The Part VII roadmap entry did not mention sec:passive-estimation. Added reference.

### 2. Three near-identical accuracy tables (CLARIFIED)
Tables tab:accuracy-progression (line 52), tab:accuracy-journey (line 1005), and tab:state-accuracy (line 1338) present overlapping CEP-per-phase data. This is intentional pedagogy (preview, consolidation, detailed breakdown), but it was not signposted. Added cross-references between the three tables so readers understand the progression is deliberate.

---

## Minor Observations (No Action Taken)

- The appendix is very long (~2200 lines, ~50 pages typeset). This is appropriate for an appendix but would benefit from a reader knowing it is optional deep-dive material.
- The "Centering as Multi-Error Mitigation" section (line 683) and the "Phase 3: Hover Lock" description (line 1496) overlap significantly. Both explain how centering eliminates errors by driving pixel offset to zero. This is acceptable repetition (different rhetorical contexts -- one is analysis, the other is operational flow) but a reader may notice.
- The cooperative architecture section (sec:cooperative-arch) is a nice addition that reframes the system as a closed-loop feedback system rather than a simple pipeline. Good for marks.
- The passive estimation section (sec:passive-estimation) is substantial (~90 lines) and adds genuine value by documenting an alternative operational mode. Correctly positioned at the end as a complement to the active estimation analysis.

---

## Verdict

No major structural reorganization needed. The document flows logically from low-level math to system-level validation, with clear connections between error analysis and design decisions. The three fixes applied (roadmap update, cross-references between redundant tables) improve navigability without changing content. The appendix is ready for submission.
