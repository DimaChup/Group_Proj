# Field Day Narrative Review

**File:** `report/sections/field_day_narrative.tex`
**Reviewed:** 2026-04-04
**Status:** DEEP-POLISHED

---

## Changes Made

### Structural
1. **Added entire Field Day 2 (31 March 2026)** -- previously missing. Four subsections covering corrupt calibration file, TFLite bbox coordinate bug, GPS double-scaling bug, and NCNN benchmark.
2. **Added "What Did Not Work" section** (sec:field-not-work) -- honest accounting of failures: no flight, incomplete GPS calibration, no outdoor detection test, fragile calibration file management.
3. **Added "Cumulative Impact" section** with consolidated Table 5 tracing all 11 field findings to their system-level impact.
4. **Added FOV impact table** (tab:fov-impact) quantifying the GPS error at 10/20/30/35m altitude -- makes the 22% error concrete.
5. **Added NCNN benchmark table** (tab:ncnn-bench) comparing TFLite vs NCNN on identical hardware.
6. **Restructured from flat subsections to two clear field-day blocks** with subsubsections, improving readability and chronological flow.
7. **Compressed team coordination** from 3 verbose paragraphs to tight paragraphs covering roles, comms, and go/no-go discipline.
8. **Updated lessons section** from 6 items to 7, adding calibration file validation and backend testing lessons from Day 2.

### Content Depth Improvements
- **Specific hardware listed** in opening paragraph (BCM2712, STM32H7, 1456x1088 native)
- **Corrupt .npz debugging narrative** -- detection confidence drop from 0.966 to 0.82, tracing to identity remap maps from empty file
- **TFLite bbox bug explanation** -- coordinates in [0, 640] treated as [0, 1], multiplied to [0, 409600]
- **Double-scaling cascade** -- how fixing one bug exposed the next, GPS estimates 100m+ off
- **NCNN speedup explained** -- ARM NEON SIMD, Python overhead bypass, 2.9x improvement
- **Platform-specific crashes** -- cv2.CAP_DSHOW on Linux, TTY-less SSH sessions
- **DJI analysis** restructured into 3 numbered findings for clarity

### What Was Removed
- Redundant "Pivot" subsection (content merged into impact table and intro paragraph)
- Verbose weather cancellation prose (tightened to one paragraph)
- Repetitive "this justified the field day" statements (now said once in the intro, proven by the impact table)

---

## Remaining Gaps (cannot fix without external input)

| Gap | Impact on Score | Action Needed |
|-----|----------------|---------------|
| No hardware photos | -2 to -4 Communication | Add photo of Pi+Cube+camera assembly, checkerboard calibration setup, or three-terminal screenshot |
| No screenshot of detection overlay | -1 Communication | Screenshot from passive_watch.py stream showing bounding box on dummy |
| Benchmark plot missing | -1 Specialist | Generate bar chart comparing TFLite vs NCNN latency (gen script exists for benchmark_comparison but not field-specific) |
| No before/after detection image | -1 Communication | Side-by-side of distorted (corrupt .npz) vs clean frame would be very compelling |
| DJI GPS scatter plot not referenced | -0.5 Specialist | The scatter plot exists in video_test.py output but is not included as a figure |

---

## Cross-Reference Integrity

| Reference | Target | Status |
|-----------|--------|--------|
| `\ref{sec:testing-deep}` | Testing methodology | OK (exists in 10_testing.tex) |
| `\ref{sec:five-tier}` | Five-tier framework | OK |
| `\ref{tab:fov-impact}` | FOV error table | NEW -- defined in this file |
| `\ref{tab:bench-results}` | Benchmark table | NEW -- defined in this file |
| `\ref{tab:ncnn-bench}` | NCNN comparison | NEW -- defined in this file |
| `\ref{tab:field-outputs}` | Consolidated outputs | NEW -- defined in this file |

---

## Scoring Assessment

| Criterion | Before | After | Notes |
|-----------|--------|-------|-------|
| Data richness | 6/10 | 9/10 | 4 tables, specific numbers throughout, before/after comparisons |
| Honesty | 5/10 | 9/10 | "What Did Not Work" section added, no flight acknowledged directly |
| Narrative quality | 8/10 | 8/10 | Already strong, maintained |
| Engineering evidence | 6/10 | 9/10 | Bug cascade (bbox -> double-scaling -> GPS), NCNN benchmarks, corrupt file debugging |
| Coverage | 5/10 | 9/10 | Was missing entire second field day |
| Connection to design | 6/10 | 8/10 | Impact table traces every finding to system change |
| **Overall** | **6/10** | **8.5/10** | Ceiling is ~9.5 with hardware photos |

---

## Summary

The section went from a single-session narrative to a two-session evidence portfolio with 4 tables, 11 quantified findings, an honest "what didn't work" section, and clear traceability from field discovery to system improvement. The main remaining gap is visual evidence (photos/screenshots) which requires files that don't currently exist in `report/figs/`.
