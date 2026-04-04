# Bibliography Fix Report

**Date:** 2026-04-04

## Status of the 4 "Missing" Comparison Entries

The bibliography review (BIBLIOGRAPHY_REVIEW.md) identified 4 entries cited in `evaluation.tex` as missing. Upon inspection, **all 4 already exist** in `references.bib` (lines 1086-1123):

| Key | Status | Line |
|-----|--------|------|
| `auspex2025` | Already present | 1086 |
| `sambolek2021` | Already present | 1095 |
| `realtimesar2025` | Already present | 1105 |
| `searchwing2024` | Already present | 1117 |

These were likely added in the same session that created the review. No action needed.

## Localization Literature Entries Added

Added 6 new entries from `LOCALIZATION_LITERATURE.md` to `references.bib`:

| Key | Paper | Journal | Year |
|-----|-------|---------|------|
| `sun2016sar` | Sun et al., Camera-Based Target Detection and Positioning UAV System for SAR | Sensors 16(11) | 2016 |
| `wang2017realtime` | Wang et al., Real-Time Multi-Target Localization from UAVs | Sensors 17(2) | 2017 |
| `spagnolo2025kalman` | Spagnolo et al., Vision-Based Geolocation Using Kalman Filtering | Aerospace 12(12) | 2025 |
| `paulin2024raycast` | Paulin et al., Raycast Method for Person Geolocalization | Expert Systems with Applications 238 | 2024 |
| `sambolek2025person` | Sambolek & Ivasic-Kos, Person Detection and Geolocation in Drone Images | SN Computer Science 6 | 2025 |
| `gautam2018error` | Gautam et al., Error Budget for Geolocation from UAS | Sensors 18(10) | 2018 |

Note: `sambolek2025person` (2025, geolocation focus) is a different paper from `sambolek2021` (2021, detection focus). Both kept.

Note: `barber2006vision` was already present at line 1033. Not duplicated.

## Compilation Verification

```
pdflatex main.tex   -> OK (233 pages)
biber main          -> OK (1 warning: pre-existing ISBN issue in sheridan2002humans)
pdflatex main.tex   -> OK (0 undefined citations)
```

## Next Steps

These 6 localization entries are not yet `\cite`d in any .tex file. To use them, add citations in the GPS estimation or evaluation sections. Suggested placements are documented in `LOCALIZATION_LITERATURE.md` Section 4.
