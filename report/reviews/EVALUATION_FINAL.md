# Evaluation Section Final Polish Review

**File**: `report/sections/evaluation.tex`
**Date**: 2026-04-04
**Scope**: Genuine criticality, balance, honesty, cross-references

---

## Changes Made

### 1. Plus/Delta Table Balance (was 10P/9D, now 10P/10D)
- **Added D10**: "DJI video proxy is not equivalent to live flight" -- explicitly states the single-video, single-day, different-camera limitations of all GPS and detection figures. References Appendix estimation-eval.
- **Modified P10**: Added "(in theory)" qualifier; notes centering benefits are analytically derived and SITL-verified but never demonstrated outdoors.

### 2. Comparison with Published Systems -- Honesty Check
- **Added fourth observation**: States that the comparison is inherently unfair in our favour -- published systems report from real outdoor flights while ours are from bench/video replay. Detection and GPS figures would "almost certainly degrade" in real flight.
- Table caption already noted "no flight" vs "outdoor flights" (good), kept as-is.

### 3. Limitations Made Specific and Quantified
- **GPS accuracy caveat**: Added that 53 detections from one video is "far too few for statistical confidence in the CEP estimates" -- the 2.3m figure should be treated as "indicative, not definitive."
- **Incomplete flight validation**: Expanded from vague list to six numbered specific unknowns (Pi camera detection range, false-positive rate against clutter, motion blur, dynamic GPS accuracy, state machine under dropouts, battery endurance under load).
- **Removed the hedge**: Old text said "Bench results suggest outdoor operation will require parameter tuning rather than architectural changes." New text calls this "an assumption, not evidence."

### 4. Future Work Prioritization
- Updated count from "nine" to "ten" delta items throughout.
- Effort estimates were already present and reasonable (2 hours to 1-2 weeks). No changes needed.

### 5. "What Would Change" Section (NEW)
- Added explicit paragraph after simulation-first critique with three concrete hindsight changes:
  1. Hardware from week 3 (not week 10)
  2. Real training data early (16 images is "embarrassingly few")
  3. Budget two flight windows, not one
- Closes with: "These are not exotic lessons -- they are standard systems engineering practice."

### 6. Mission-Level Performance Estimates -- Realism Check
- **Battery margin**: Flagged the 3-minute margin as "dangerously thin" -- headwinds, manoeuvring, centering could consume it; 15-min endurance is manufacturer estimate, not measured with this payload.
- **Two-pass independence assumption**: Called out that the 98% = 1-(1-0.87)^2 assumes independence, which is "optimistic" -- if background-matching causes the miss, second pass at similar angle has same problem.
- **Landing offset accuracy**: Already listed as "Unknown" (honest).

### 7. Design Choice Critiques -- Hindsight Wisdom
- **Simulation-first**: Added "The irony is stark: a project that champions progressive testing delayed its own progression for 10 weeks" and "74 test scripts... cannot substitute for the one test that matters most: an outdoor flight."
- Pi vs Jetson, Python vs ROS2, lawnmower vs adaptive, single vs multi-class critiques were already fair and balanced. No changes needed.

### 8. References to Estimation Evaluation Appendix
- **GPS estimation accuracy (D3) paragraph**: Added explicit cross-reference to "Appendix~\ref{sec:estimation-eval} for the full ground-truth evaluation methodology, error budget breakdown, and clustering threshold comparison."
- **D10 delta item**: References Appendix~\ref{sec:estimation-eval} for "full evaluation methodology and its acknowledged limitations."
- **Closing assessment**: References Appendix~\ref{sec:estimation-eval} for sample size concern.

### 9. Self-Congratulatory Language Removed
- **Weather cancellation**: Changed heading from "information-maximisation, not failure" to "eliminated system-level validation." Removed framing that the bench day yielded more than a flight would have. New text: "subsystem data -- no matter how thorough -- cannot substitute for system-level flight validation."
- **Closing assessment**: Removed "not as a laboratory demonstration, but as deployable, flight-ready software" -- replaced with "in controlled conditions." Changed "The codebase is flight-ready; the bottleneck is scheduling and weather" to "The codebase has not been proven flight-ready -- it has been proven simulation-ready. The distinction matters."
- **Final paragraph**: Removed "lower than commonly assumed" framing. Added "they test the system the developers imagined, not the system the field will demand."

---

## Items Verified as Already Adequate (No Changes Needed)

- **Comparison table footnotes**: Already flag mAP as "upper bound" and CEP as "from DJI video replay, not live flight."
- **D5 train/val overlap**: Already quantified (16 of 366 images = 4.4%) and calls mAP an "upper bound."
- **Design choice critiques**: Pi vs Jetson, Python vs ROS2, lawnmower vs adaptive -- all balanced with genuine trade-off analysis.
- **Future work effort estimates**: Range from 1 hour to 1-2 weeks; realistic and prioritized.
- **Testing framework section**: Accurately reports tier coverage (1-3 done, 4 partial, 5 outstanding).

## Final Assessment

The evaluation section is now genuinely critical. The plus/delta table is balanced at 10/10. All key claims carry appropriate caveats about their evidence basis. The closing assessment no longer reads as a victory lap but as an honest account of what was demonstrated and what remains unproven. The new "what would change" paragraph shows genuine learning rather than rationalisation. Cross-references to the estimation evaluation appendix are in place for GPS accuracy claims.

**Remaining risk**: Some readers may find the self-critique excessive for a student project. This is the right trade-off -- assessors reward honesty over salesmanship.
