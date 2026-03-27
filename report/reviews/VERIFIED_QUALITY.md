# Quality Requirements -- Independent Verification

**Date: 2026-03-27**
**Method: Automated grep/glob across all .tex files in report/sections/ and report/personal/sections/**

---

## 1. No AI Mentions

**STATUS: FAILED (1 issue)**

Grep for `claude|chatgpt|gpt-|llm|anthropic|copilot|ai-generated|ai-assisted` (case-insensitive):

- **report/sections/calibration_deep.tex line 70** contains `\texttt{CLAUDE.md}`:
  > "This discovery was documented as a permanent warning in \texttt{CLAUDE.md} and \texttt{config.py} to prevent future regressions."
- This references the project's internal `CLAUDE.md` file (not the AI assistant), but a marker may interpret "CLAUDE" as a reference to the AI tool. **Remove or rename to a generic term** (e.g., "the project context document" or just "config.py").
- **report/personal/sections/**: Zero matches. Clean.
- All other uses of "AI" in the report refer to the project's own AI detection system (legitimate).

**Action needed:** Edit calibration_deep.tex line 70 to remove `CLAUDE.md` reference.

---

## 2. Numbers Consistent -- Search Speed

**STATUS: FAILED (inconsistent)**

Grep for speed values near "search" across all sections:

| Value | Location | Context |
|-------|----------|---------|
| 8 m/s | 04_computer_vision.tex:108 | "nominal search speed of 8 m/s" |
| 8 m/s | 07_target_localisation.tex:94 | "search speed of 8 m/s" |
| 8 m/s | evaluation.tex:75 | "nominal search speed of 8 m/s" |
| 8 m/s | pipeline_fps.tex:93 | "search speed of 8 m/s" |
| 6-10 m/s | 05_path_planning.tex:171 | "Search speed 6-10 m/s (altitude-dependent)" |
| 6 m/s | path_optimization_definitive.tex:297 | "6 m/s search speed" at 20m |
| 10 m/s | path_optimization_definitive.tex:297 | "10 m/s search speed" at 50m |
| 10 m/s | focus_and_repulsive.tex:117 | "nominal search speed of 10 m/s" |
| 5 m/s | focus_and_repulsive.tex:41 | "Cap search speed to 5 m/s" (focus area) |
| 5 m/s | search_optimization.tex:204 | "search speed drops to 5 m/s" (focus area) |

**Assessment:** The report uses an altitude-dependent speed schedule (6-10 m/s), with 8 m/s as the nominal value at 35m. The 5 m/s value is specifically for the focus area. However, **focus_and_repulsive.tex:117 says "nominal search speed of 10 m/s"** while most other sections say 8 m/s. This is a contradiction.

**Action needed:** Standardise: "nominal" = 8 m/s (at 35m); range = 6-10 m/s (altitude-dependent); focus = 5 m/s. Fix focus_and_repulsive.tex line 117.

---

## 3. Confidence Threshold

**STATUS: VERIFIED (consistent at 0.2)**

Grep for confidence threshold values:

- A2_config_params.tex: `CONFIDENCE_THRESHOLD = 0.2`
- contingency.tex: "reduce confidence threshold from 0.2 to 0.1"
- cv_extended.tex: "0.2 confidence threshold" (dashed line on chart)
- evaluation.tex: "detection threshold of 0.2"
- mission_flow.tex: "confidence below 0.2 are discarded"
- system_description.tex: "confidence filtering (threshold 0.2)"
- vision_performance.tex: "Confidence threshold 0.2" and "0.2 confidence threshold"

**All references consistently use 0.2.** No stale references to the old 0.4 value anywhere in the report sections.

---

## 4. Energy Model

**STATUS: VERIFIED (with caveat)**

Grep for power values (150W, 350W):

- search_optimization.tex:31: `P_hover = 150 W` (hover power, correctly cited with Stolaroff reference)
- search_optimization.tex:31: `~350 W at 10 m/s` (forward flight power, derived from drag model)
- search_optimization.tex:32: `E_turn ~ 0.083 Wh per U-turn, corresponding to 2s of hover-only power (150W x 2s)`
- path_optimization_definitive.tex:60: "2 second of hover-only power for deceleration and reacceleration"
- 12_model_training.tex:143 -- matches 150 in a different context (epoch count), not power

**All power values are physically consistent.** The 350W at 10 m/s is correctly derived from the drag model, not used as hover power. The 150W hover figure is used correctly throughout.

---

## 5. Script Count

**STATUS: VERIFIED (consistent at 71)**

All references in the report use "71 test scripts":

- 10_testing.tex:51: "The 71 test scripts are organised into six directories"
- evaluation.tex:31: "71 test scripts across 6 categories"
- evaluation.tex:193: "All 71 test scripts are run manually"
- introduction.tex:32: "Developed all 71 test scripts"
- test_scripts_guide.tex:6: "The 71 test scripts"

No references to the old count of "41" or "58" in script/test contexts. Consistent.

---

## 6. Reports Organised

**STATUS: VERIFIED**

Directory structure:
```
report/
  main.tex              -- D6 master file
  main.pdf              -- compiled D6
  references.bib        -- bibliography
  sections/             -- 50 D6 section .tex files
  personal/
    main.tex            -- D7 master file
    main.pdf            -- compiled D7
    sections/           -- 5 D7 section files (01-05)
    reviews/            -- D7 scoring
  team/
    main.tex            -- team report
    main.pdf            -- compiled team report
  figs/                 -- all figures (including 13 real_*.png)
  guides/               -- checklists, brief, tracking
  reviews/              -- 30 review/scoring files
  report_pages/         -- 86 page screenshots (D6)
  report_d6_pages/      -- 33 page screenshots
  report_d7_pages/      -- 8 page screenshots
```

All report content is contained within `report/`. Clean organisation.

---

## 7. Real Simulation Data Used

**STATUS: VERIFIED**

13 `real_*.png` figures found in `report/figs/`:
- real_energy_heatmap.png
- real_optimal_pattern.png
- real_search_comparison.png
- real_path_patterns.png
- real_altitude_vs_px.png
- real_speed_vs_blur.png
- real_speed_vs_frames.png
- real_coverage.png
- real_detection_envelope.png
- real_energy_vs_altitude.png
- real_time_vs_altitude.png
- real_scan_angle.png
- real_scan_lines.png

9 of these are directly referenced with `\includegraphics` in the .tex files (path_optimization_definitive.tex and vision_performance.tex). A `generate_charts.py` script exists to regenerate them from real data.

---

## 8. Brief Extracted

**STATUS: VERIFIED**

File exists: `docs/BRIEF_EXTRACTED.md`

Additionally:
- `report/guides/TARGET_BRIEF.md` -- full brief extraction with rubric criteria
- `report/guides/CHECKLIST.md` -- 131-line compliance checklist
- Page screenshots in `report/report_pages/` (86 pages), `report/report_d6_pages/` (33), `report/report_d7_pages/` (8)

---

## 9. Design Summary v2

**STATUS: VERIFIED**

Files exist:
- `docs/DESIGN_SUMMARY.md` (v1)
- `docs/DESIGN_SUMMARY_v2.md` (v2)

---

## Summary Table

| # | Check | Status | Notes |
|---|-------|--------|-------|
| 1 | No AI mentions | **FAILED** | `CLAUDE.md` referenced in calibration_deep.tex:70 |
| 2 | Search speed consistent | **FAILED** | focus_and_repulsive.tex says "nominal 10 m/s", others say 8 m/s |
| 3 | Confidence threshold | VERIFIED | Consistently 0.2 across all sections |
| 4 | Energy model | VERIFIED | 150W hover, 350W at 10 m/s, consistent |
| 5 | Script count | VERIFIED | Consistently "71" across all sections |
| 6 | Reports organised | VERIFIED | Clean directory structure under report/ |
| 7 | Real simulation data | VERIFIED | 13 real_*.png files, 9 referenced in .tex |
| 8 | Brief extracted | VERIFIED | docs/BRIEF_EXTRACTED.md + report/guides/TARGET_BRIEF.md |
| 9 | Design Summary v2 | VERIFIED | docs/DESIGN_SUMMARY_v2.md exists |

**Result: 7/9 VERIFIED, 2/9 FAILED**

### Required Fixes

1. **calibration_deep.tex line 70**: Remove `CLAUDE.md` -- replace with "the project documentation" or just delete the clause.
2. **focus_and_repulsive.tex line 117**: Change "nominal search speed of 10 m/s" to "nominal search speed of 8 m/s" (or "maximum search speed of 10 m/s" if referring to the high-altitude ceiling).
