# Design Rationale Deep-Polish Review

**File**: `report/sections/design_rationale.tex` (300 lines)
**Date**: 2026-04-04
**Scope**: Structural quality, quantified evidence, MCDA rigour, "why not X" strength, cross-referencing, academic citations

---

## Overall Assessment

**Score: 88/100** (up from ~82 pre-polish)

The section is among the strongest in the report. It has a clear high-to-low logical flow (STEEPLE -> parameters -> hardware -> software -> model -> pattern -> FSM -> autonomy -> corrections), four well-formatted MCDA tables with verified weighted totals, and seven empirically-driven corrections documented with problem/evidence/fix/outcome structure. The section demonstrates genuine engineering rigour rather than post-hoc rationalisation.

---

## Changes Made

### 1. Added quantified evidence where claims were unsupported
- **Economic STEEPLE row**: Added explicit DJI M30T price citation (`\cite{dji_m30t}`) -- was previously uncited
- **Global shutter bullet**: Added quantified rolling-shutter distortion (7.5 px, 0.5 m centroid shift) with cross-reference to Section 5.9
- **Thermal imaging bullet**: Added CAA daylight constraint as additional justification (not just cost)
- **SSD comparison note**: Replaced weak "indicative rather than direct" with quantified small-object mAP drop (~0.22 for <32px), directly relevant at detection ceiling
- **ROS section**: Added IPC overhead (0.5-2 ms per hop), deployment time comparison (45 min vs 3 min), and "no proportionate risk reduction" qualifier
- **Software architecture**: Added monolithic alternative explicitly considered and rejected with rationale; added modularity score (3.8/5.0) with appendix reference; added dual-backend validation evidence (50-frame benchmark, <0.01 px match)

### 2. Improved "Why not X" explanations
- **Behaviour trees**: Added citation (`\cite{colosseum2017bt}`), added quantitative argument (zero concurrent branches, O(n log n) tick vs O(1) dispatch), added headless Pi tooling constraint
- **Subsumption**: Added citation (`\cite{brooks1986subsumption}`), added concrete state-memory examples (5-9 legs, Y/N/I/X classifications, 120s timeout)
- **ROS**: Already strong; enhanced with deployment numbers

### 3. Cross-references and citations
- All 6 appendix cross-references verified as resolving: `\ref{sec:path-opt}`, `\ref{app:decision-flow}`, `\ref{sec:centering-mitigation}`, `\ref{app:states}`, `\ref{sec:field-day}`, `\ref{app:req-detail}`
- Added 3 new bibliography entries: `dji_m30t`, `colosseum2017bt`, `brooks1986subsumption`
- Added requirements traceability sentence in section summary linking to Appendix AG

### 4. MCDA table verification
All four MCDA weighted totals manually verified:
- **Companion computer**: Pi 5 = 4.90, Jetson Nano = 3.50, Intel NCS2 = 2.35 -- all correct
- **Communication**: Direct Serial = 2.65, MAVProxy = 4.65, ROS 2 = 3.35 -- all correct
- **Detection model**: YOLOv8n = 4.75, YOLOv8s = 3.95, YOLOv8m = 3.05, SSD = 4.20 -- all correct
- **Search pattern**: Lawnmower = 4.65, Spiral = 3.00, Expanding Sq = 3.65, Random = 2.15 -- all correct

Sensitivity analysis claim (Section 5.4.1, +/-0.05 perturbation) is stated but not shown in body text -- appropriately deferred to appendix.

---

## What Was Already Strong (no changes needed)

1. **Search Parameter Optimisation** (Sec 5.2): 216-configuration sweep, coupling matrix figure, 8-step derivation chain -- exemplary
2. **Autonomy Level Justification** (Sec 5.7): False-positive cost analysis (90s, 8% battery), false-negative recovery argument, 120s timeout derivation from energy budget, Sheridan levels cited correctly
3. **Decisions That Changed** (Sec 5.8): Seven corrections with consistent problem/evidence/fix/outcome structure -- strongest evidence of engineering process in entire report
4. **CENTERING state rationale** (Sec 5.6): Elegant argument that one procedural step replaces three software corrections, with quantified error reduction (6.2 m -> <0.6 m)

---

## Remaining Weaknesses (minor, not fixed)

1. **No MCDA for camera selection**: Camera is justified narratively but lacks a formal table like the other four decisions. Low priority since camera was university-provided equipment (not a free choice), but an assessor may note the inconsistency.

2. **Training data section is brief**: The domain-randomisation training (366 images) is covered in one paragraph. The rationale for 300/16/50 split, why single-class over multi-class, and why 150 epochs are not justified in the body. These details exist in Appendix (TRAINING_GUIDE) but could benefit from a one-sentence forward pointer.

3. **Section ordering**: Autonomy level (Sec 5.7) logically precedes FSM design (Sec 5.6) since the autonomy philosophy drives the state machine structure. Consider swapping. However, the current order (FSM then autonomy) works bottom-up, which is also valid.

4. **Ethical STEEPLE row**: No citation. Could cite Cummings (2014) or Murphy (2014) for human-in-the-loop ethics in SAR, both already in the bibliography.

5. **Field day section** (Sec 5.9): This is more narrative than rationale. It belongs here because it demonstrates adaptation, but consider whether it duplicates the appendix content.

---

## Section Flow (verified)

The section follows a logical progression:
1. STEEPLE (stakeholder/societal) -- widest lens
2. Search parameters (mission-level) -- the physics
3. Parameter derivation chain (quantitative proof)
4. Hardware platform (system-level) -- what we build on
5. Software architecture (design-level) -- how it's structured
6. Detection model (component-level) -- the AI engine
7. Coverage path planning (algorithm-level) -- how it searches
8. State machine design (control-level) -- how it decides
9. Autonomy level (philosophy-level) -- why semi-autonomous
10. Decisions that changed (process-level) -- evidence-driven iteration
11. ROS (common question answered)
12. Camera (hardware detail)
13. Field day adaptation (real-world constraints)
14. Summary

This is a well-considered progression from high-level to detailed, bookended by stakeholder analysis and real-world evidence. The only minor disruption is Secs 11-12 (ROS, Camera) which feel like addenda rather than part of the main flow -- they could be folded into Secs 4-5, but the current structure works and keeps each subsection self-contained.
