# Brutal Review: Evaluation Section (evaluation.tex)
**Date:** 2026-03-27 | **Reviewer:** Claude Opus 4.6 | **Verdict: STRONG with fixable gaps**

---

## 1. Is the Plus/Delta Balanced and Honest?

**Verdict: Yes -- genuinely balanced.** 9 plus items, 9 delta items. This is unusually honest for a student report. Most teams bury deltas or list 2 token weaknesses. The 9:9 ratio signals maturity.

**However:**
- P7 ("58 test scripts across 6 categories") is quantity-as-quality. Having 58 scripts is not inherently a strength -- having scripts that *caught real bugs* is. P3 already makes that argument with the bug table. P7 adds nothing that P3 doesn't already prove better. **Recommendation:** Either merge P7 into P3 ("the 58 scripts across six categories enabled the progressive framework that caught 12 defects") or replace P7 with something the project actually demonstrated differently -- e.g., the headless/SSH operation working on first attempt, or the config auto-detection surviving 3 platforms without modification.
- P9 ("14 figures generated programmatically") is meta-commentary about the report, not about the *system*. A marker reads this as padding. Programmatically generated figures are expected in an engineering report, not a distinguishing strength. **Cut or replace.**

**Missing delta that a marker will notice:** There is no delta about the team's late start on real data collection. Lesson Learned #1 says exactly this ("labelling tool was built late"), but it doesn't appear as a D-item in the table. This is the kind of thing markers flag as "the student knows but buried it."

---

## 2. Does Every Plus Have Evidence?

| Item | Evidence provided? | Verdict |
|------|--------------------|---------|
| P1 | Model swapped 3 times, zero code changes, section cross-ref | SOLID |
| P2 | Tested on Windows, WSL, Pi 5 -- specific platforms named | SOLID |
| P3 | Bug table with 12 entries, tier numbers, fix times | EXCELLENT |
| P4 | 4.8 FPS, 206.5 ms, 50/50 detection, 0.966 confidence, 0.995 mAP | EXCELLENT -- specific numbers |
| P5 | 1.5 ms added, 0.7% of inference, one-file change | SOLID |
| P6 | HTTP endpoint, PuTTY + phone browser tested | ADEQUATE -- "tested" is vague. Did it stream at what framerate? Any latency measurement? |
| P7 | "58 scripts across 6 categories" | WEAK -- count alone is not evidence of quality. See note above. |
| P8 | Dry-run mode, same main.py on both platforms | ADEQUATE -- but repeats P2's argument |
| P9 | "14 figures generated programmatically" | WEAK -- this is a report-writing practice, not a system strength |

**Actionable fixes:**
- P6: Add one concrete number (e.g., "MJPEG stream at ~3 FPS with 85% JPEG quality over WiFi").
- P7: Merge into P3 or replace.
- P8: Differentiate from P2 more sharply. P2 is about auto-detection. P8 should emphasize that simulation caught 5 of 12 bugs (the Tier 1 bugs) before any hardware was touched -- that's the payoff of simulation-first, distinct from config auto-detection.
- P9: Cut entirely. Use the freed row for something real.

---

## 3. Does Every Delta Have a Concrete Next-Step?

| Item | Next step provided? | Is it concrete? | Verdict |
|------|---------------------|-----------------|---------|
| D1 | "Rebook flight slot, execute Tiers 3-5" | Yes, specific tiers named | GOOD |
| D2 | "Export FP16 XNNPACK, thread pipeline" | Yes, specific technique + expected gain | GOOD |
| D3 | "Implement lag compensation, formula given" | Yes, includes the actual equation | EXCELLENT |
| D4 | "Run threshold sweep, produce PR curve" | Yes, specific analysis named | GOOD |
| D5 | "Collect 50+ real frames, held-out split" | Yes, specific number + methodology | GOOD |
| D6 | "Retrain multi-class or add classifier head" | Yes, two concrete options | GOOD |
| D7 | "Inject PLB mid-flight via HTTP endpoint during Tier 4" | Yes, specific mechanism + tier | EXCELLENT |
| D8 | "Add DEPLOY state with MAV_CMD_DO_SET_SERVO" | Yes, specific MAVLink command | EXCELLENT |
| D9 | "Export FP16, benchmark, compare accuracy" | Yes, but overlaps D2 heavily | REDUNDANT |

**Problem: D2 and D9 overlap significantly.** Both talk about FP16/INT8 inference optimization. D2 frames it as a speed problem, D9 frames it as a model-size problem, but the next steps are nearly identical. **Recommendation:** Merge D9 into D2 (mention float32 waste in D2's detail column) and replace D9 with something genuinely different -- e.g., "no night/low-light testing" or "no multi-drone coordination" or "landing accuracy unverified beyond simulation."

---

## 4. Is the Bug-Cost Table in the Body?

**YES.** Table 2 (tab:bug-cost) is properly in the body at lines 117-152. It has:
- 12 defects listed
- Testing tier for each
- Fix time for each
- "Cost if missed" column with specific consequences

**This is the strongest single element in the evaluation.** The "Cost if Missed" column is particularly effective -- it translates abstract testing into concrete risk reduction.

**Minor issues with the table:**
- "GPS timing lag" has tier "3*" with a footnote. The asterisk explanation is good (DJI video as proxy). But "Fix Time: N/A" is odd -- it was *discovered*, not fixed. Consider changing to "Identified" or "Unresolved" to be more precise, since the other entries list resolution times.
- The table would benefit from a total row: "12 defects, 0 in flight, total fix time ~6 hours" -- this is a powerful summary stat that markers love.

---

## 5. Are Lessons Learned Genuine Insights or Platitudes?

| Lesson | Platitude or Insight? | Verdict |
|--------|-----------------------|---------|
| 1. "Invest in data collection infrastructure before model training" | GENUINE INSIGHT -- backed by specific regret (label_tool built late, mAP treated as upper bound). This is a real mistake they made and understood. | PASS |
| 2. "Characterise sensor pipeline end-to-end before writing application code" | GENUINE INSIGHT -- names exactly which 3 of 12 bugs it would have prevented (BGR, FOV, GPS lag). Quantified impact. | PASS |
| 3. "Simulation fidelity has diminishing returns; real-world data does not" | GENUINE INSIGHT -- the DJI video pipeline as evidence is compelling. "More informative than additional simulation refinement" is a non-obvious claim supported by the confidence-vs-altitude curve they extracted. | PASS |
| 4. "Budget for weather and schedule one flight day per week" | BORDERLINE -- the insight is real (single scheduled day = binary outcome), but the recommendation ("schedule weekly") is logistically naive for a university project with shared airspace and booking systems. It reads slightly like an excuse. | SOFT PASS |

**Overall: 3.5/4 genuine.** This is well above average. Most student lessons learned are "we should have started earlier" and "communication is important." These are specific, evidence-backed, and actionable.

**Fix for Lesson 4:** Add one sentence acknowledging the scheduling constraint: "University airfield access is limited to booked slots, but even requesting two non-consecutive dates---one early for calibration, one late for full testing---would have halved the weather risk." This makes it a practical recommendation rather than wishful thinking.

---

## 6. Is the Weather Adaptation Framed as Strength?

**Yes, and it's done well (lines 154-155).** The paragraph:
- Does NOT claim the cancellation was good luck
- Frames the *response* as evidence of engineering adaptability
- Lists specific outputs from the pivot: FOV calibration, lens mapping, benchmark, DJI video pipeline
- Quantifies what the pivot produced: confidence-vs-altitude curve, detection-vs-speed analysis, CEP50 = 2.3m
- Makes a concrete comparison: "produced quantitative performance data that would otherwise have required multiple flight sorties"

**One problem:** The last sentence is nearly identical to a sentence earlier in the same paragraph. Lines 155 ends with "that would otherwise have required multiple flight sorties to collect" and then immediately says "This pivot from 'fly and hope' to 'analyse what we have' produced quantitative performance data that would otherwise have required multiple flight sorties." **This is a copy-paste duplication.** The "fly and hope" framing is also slightly flippant for an academic report. Fix: delete the duplicate sentence and keep the first occurrence, or rewrite the second to add new information.

---

## 7. Any Self-Congratulatory Language Remaining?

**Mostly clean, but a few spots:**

1. **Line 3 (intro paragraph):** "assesses technical performance honestly" -- saying you're honest is the kind of thing dishonest people say. Let the content demonstrate honesty; don't announce it. **Fix:** Delete "honestly" -- the 9:9 plus/delta ratio already proves it.

2. **Line 102:** "This architectural decision was validated empirically" -- fine in isolation, but the entire paragraph is a victory lap for the architecture. Every sentence says "our design was good because..." with no qualification. The delta items cover architectural gaps elsewhere, but this paragraph has zero self-criticism. **Fix:** Add one qualifying sentence, e.g., "The abstraction does impose a constraint: backend-specific optimisations (e.g., NCNN batch inference or Hailo DMA transfers) cannot be exposed through the current single-function interface without extending it."

3. **Line 178 (summary):** "architecturally sound and quantitatively characterised" -- this is the conclusion restating what the section already proved. Acceptable in a summary paragraph, but the phrase "architecturally sound" is self-awarded. Consider "architecturally consistent" (factual) instead of "sound" (evaluative).

4. **Line 178 continued:** "suggesting that the remaining risk is in parameter tuning and environmental validation rather than fundamental redesign" -- this is a strong claim that a marker might challenge. You have NOT flown. You cannot rule out fundamental problems (e.g., vibration-induced inference failures, GPS multipath in the survey area, electromagnetic interference from the Cube affecting the camera). **Fix:** Soften to "suggesting that the highest-probability remaining risks are in parameter tuning..." -- the word "highest-probability" acknowledges unknown unknowns.

---

## 8. Structural Issues

1. **The summary paragraph (line 177-178) is too long.** It's a single paragraph trying to summarize the entire evaluation. Break into 2-3 sentences or use a \paragraph{} structure.

2. **Figures 1-4 (lines 63-99) are referenced in the discussion but the figure content is vague.** The captions describe what the figures show but not what the reader should conclude. E.g., Figure \ref{fig:det_vs_speed} caption says "detection rate exceeds 95%" but doesn't say "therefore the 8 m/s search speed is validated." Captions should state the conclusion, not just describe the visual.

3. **The Discussion section (lines 101-158) mixes plus amplification with delta amplification.** The "Architecture resilience" paragraph is all positive. The "Detection performance" paragraph starts positive then pivots to caveats. The "GPS estimation" paragraph is all delta. This creates an uneven rhythm. Consider restructuring so each paragraph addresses both sides of its topic, or group all discussion by theme rather than by plus/delta polarity.

4. **Missing: comparison to requirements.** The evaluation never explicitly maps back to the system requirements (R01-R07 mentioned only for D7 and D8). A marker expects to see: "R01 (autonomous takeoff): verified in SITL, untested in field. R02 (search pattern): verified in SITL and dry-run..." This is standard SE evaluation practice and its absence will cost marks.

---

## 9. Factual Consistency Checks

- D2 says "nominal 8 m/s search speed" and "altitude-dependent schedule at 35 m" -- verify this matches config.py (SEARCH_SPEED_MPS and TARGET_ALT). CLAUDE.md says TARGET_ALT = 30 and SEARCH_SPEED_MPS = 5. **Potential inconsistency: the report says 8 m/s at 35 m but config says 5 m/s at 30 m.** If the values were updated for the report's analysis, note this. If not, this is a factual error.
- D3 says "100-200 ms latency" producing "~1.6 m position error at 8 m/s." Math check: 0.2s * 8 m/s = 1.6 m. Correct for the upper bound. But D3 uses the 8 m/s figure while config says 5. At 5 m/s the error is 1.0 m. Using the higher speed inflates the problem. Be consistent.
- P4 says "0.995 mAP50" -- this matches CLAUDE.md. Consistent.
- Bug table says 12 defects. Counting the table rows: 12 entries. Consistent.

---

## 10. Priority Fix List

| Priority | Fix | Impact |
|----------|-----|--------|
| HIGH | Remove duplicate sentence in weather adaptation paragraph (line 155) | Reads as sloppy editing |
| HIGH | Verify 8 m/s vs 5 m/s and 35 m vs 30 m against actual config values | Factual credibility |
| HIGH | Add requirements mapping (R01-R07 vs. verification status) | Missing standard SE content; marks at stake |
| MED | Merge D9 into D2, replace with a genuinely different delta | Avoids redundancy, shows broader awareness |
| MED | Cut P9, strengthen or merge P7 | Removes padding, tightens the plus list |
| MED | Delete "honestly" from intro paragraph | Removes self-congratulatory meta-claim |
| MED | Soften "architecturally sound" and "parameter tuning rather than fundamental redesign" | Avoids overclaiming without flight evidence |
| MED | Add qualifying sentence to architecture resilience paragraph | Prevents victory-lap reading |
| LOW | Add total row to bug-cost table | Small but effective summary stat |
| LOW | Fix Lesson 4 with scheduling constraint acknowledgment | Makes it practical, not wishful |
| LOW | Improve figure captions to state conclusions | Better reader guidance |

---

## Overall Assessment

**This is a genuinely strong evaluation section.** The bug-cost table is excellent and would impress any marker. The plus/delta balance is honest. The lessons learned are real insights, not platitudes. The weather adaptation is framed as engineering response, not excuse.

**Main weaknesses:** (1) Two items of padding in the plus column (P7, P9) dilute the genuine strengths. (2) D2/D9 redundancy suggests running out of distinct deltas. (3) No requirements mapping -- a standard SE evaluation element that's simply missing. (4) The 8 m/s / 35 m figures may not match the actual codebase, which would be embarrassing if a marker checks.

**Grade contribution estimate:** This section, as-is, would score well. With the HIGH fixes applied, it would be very strong.
