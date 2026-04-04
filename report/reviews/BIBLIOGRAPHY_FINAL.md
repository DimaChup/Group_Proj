# Bibliography Final Audit — 2026-04-04

## Summary

| Metric | Value | Status |
|--------|-------|--------|
| Unique citation keys in .tex | **108** | GOOD (target 30-50, we exceed it) |
| Bib entries (references.bib + extra_refs.bib) | **109** | OK |
| Missing from bib (would show [?]) | **0** | PASS |
| Duplicate bib entries | **0** | PASS |
| Unused bib entries | **1** (`mavlink`) | Acceptable |

## Verdict

**No [?] citations in the PDF.** Every `\cite{}` key resolves to a bib entry. Zero duplicates. 108 unique references is strong for an MSc group report.

## Fixes Applied

Three localization citations existed in `references.bib` but were never `\cite`d in any `.tex` file. Added to `localization_approaches.tex`:

1. **`spagnolo2025kalman`** -- Added to Approach 3 (Kalman Filter Tracking) description. Demonstrates Kalman-based geolocation with gimbal camera on UAV.
2. **`wang2017realtime`** -- Added to Justification section preamble. Validates real-time multi-target localisation from UAV imagery.
3. **`paulin2024raycast`** -- Added to Justification section preamble. Extends geolocation with terrain-aware raycast method against DEM.

All three now cited in `localization_approaches.tex`, section "Justification of Our Approach".

## Localization Citations Status (all 7)

| Key | In bib | Cited | Where |
|-----|--------|-------|-------|
| barber2006vision | Yes | Yes | estimation_evaluation.tex, gps_estimation_deep.tex, localization_approaches.tex |
| sun2016sar | Yes | Yes | estimation_evaluation.tex, localization_approaches.tex |
| wang2017realtime | Yes | Yes | localization_approaches.tex (FIXED) |
| spagnolo2025kalman | Yes | Yes | localization_approaches.tex (FIXED) |
| paulin2024raycast | Yes | Yes | localization_approaches.tex (FIXED) |
| sambolek2025person | Yes | Yes | estimation_evaluation.tex |
| gautam2018error | Yes | Yes | estimation_evaluation.tex |

## Unused Bib Entry

- **`mavlink`** -- MAVLink v1 protocol reference (Meier et al., 2013). The report cites `mavlink2` (v2 protocol) instead. Harmless to keep; BibTeX ignores uncited entries.

## Citation Count Assessment

108 unique references for an MSc group project report is well above the 30-50 target. The bibliography covers:
- SAR operations and regulations (murphy2014, caa2024uas, cap722, sarh2024stats, etc.)
- Computer vision and YOLO family (yolov3, yolov8, bochkovskiy2020yolov4, lin2014coco, etc.)
- Path planning and coverage (galceran2013survey, choset2001coverage, boustrophedon, etc.)
- Target geolocation and estimation (barber2006vision, sun2016sar, kalman1960, etc.)
- Hardware and software tools (ardupilot, raspberrypi5, opencv, tflite, ncnn, etc.)
- Safety and autonomy (sheridan2002humans, endsley1999loa, jarus2019sora, etc.)
- Streaming and communications (rfc2435, apple_hls, wiegand2003h264, etc.)

No action needed on citation count.
