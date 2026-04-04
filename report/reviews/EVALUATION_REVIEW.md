# Evaluation Section Review

**Date**: 2026-04-04
**Files reviewed**: `report/sections/evaluation.tex`, `report/sections/evaluation_detail.tex`, `report/sections/simulation_validation.tex`, `report/sections/requirements_verification.tex`

---

## Overall Assessment: 7.5/10 — Strong but Missing Critical Depth

The evaluation is **significantly above average** for a university report. The plus/delta table is well-structured, the defect register is excellent, and the honesty about no flight testing is commendable. However, several areas prevent it from reaching top marks.

---

## Criterion-by-Criterion Analysis

### 1. Critical Assessment of What Worked / What Didn't — Score: 8/10

**Strengths:**
- The plus/delta table (P1-P10, D1-D9) is genuinely balanced — 10 positives vs 9 deltas
- D1 (no flight) is not hidden — it's the first delta and discussed extensively
- D5 (train/val overlap) is a sophisticated self-critique most students would not catch
- The "information maximisation" framing of the weather cancellation is smart

**Weaknesses:**
- The "Plus" items read slightly promotional (P9 "programmatically generated figures" is padding — this is expected, not a strength)
- P7 "74 test scripts" emphasises quantity over quality — how many of those 74 scripts actually caught bugs? Only 12 defects across 74 scripts suggests many scripts were never truly exercised
- Missing: no discussion of state machine complexity vs. necessity. 19 states and 32 transitions — was this over-engineered for a project that never flew? A top evaluation would question whether a simpler 5-state machine would have been sufficient
- Missing: no honest assessment of the team's time allocation. If the code was mature by week 10 but the first hardware test was week 16, was too much time spent on simulation polish?

### 2. Comparison Against Alternatives — Score: 5/10 **WEAKEST AREA**

**What's there:**
- D2 mentions NCNN as an alternative backend (4.5x faster)
- D6 mentions multi-class detector as alternative to single-class
- D9 mentions FP16/INT8 as alternatives to float32

**What's missing (critical gap):**
- No comparison to alternative architectures: Why Python + MAVLink + TFLite instead of ROS2? Why not DroneKit? Why not an onboard Jetson instead of Pi 5? These decisions are discussed in design_rationale.tex but NOT evaluated — the evaluation should ask "was this the right choice?" with hindsight
- No comparison to alternative search strategies: Lawnmower vs. spiral vs. expanding square vs. RL-based adaptive search. The evaluation should quantify coverage efficiency vs. these alternatives
- No comparison to how other university SAR projects performed. The SAR_COMPARISON.md doc exists but none of it appears in the evaluation
- No comparison of the GPS estimation approach (Kalman + inverse variance) against simpler alternatives — did the complexity actually improve accuracy vs. a simple rolling average?
- The evaluation never asks: "Would buying a thermal camera for £200 have been more effective than 16 weeks of CV development?"

### 3. Quantify Performance Against Targets — Score: 8/10

**Strengths:**
- Excellent quantitative data: 206.5ms inference, 4.8 FPS, CEP50=2.3m, mAP50=0.995
- Detection confidence vs altitude curve (Figure conf_vs_alt)
- Detection rate vs speed curve (Figure det_vs_speed)
- 12 defects with measured fix times (git commit timestamps — very good)
- Latency breakdown figure

**Weaknesses:**
- R07 (land 5-10m from casualty) has no quantitative validation — only "probability analysis" and SITL. This is the most important metric and has no real data
- The 0.995 mAP is presented with the caveat about train/val overlap, but no alternative figure is given. What is a realistic mAP estimate? Even stating "likely 0.85-0.90 based on video replay detection rate" would be more useful
- No mission-level metrics: total search time, area coverage rate (m²/min), probability of detection per pass, time-to-first-detection. These are the metrics SAR operators actually care about
- No comparison of actual vs planned timeline

### 4. Discuss Limitations Honestly — Score: 9/10

**This is the strongest aspect.** The evaluation is genuinely honest:
- D1 openly states 0 outdoor flights
- D5 questions the validity of its own mAP figure
- The sim-to-real gap section (simulation_validation.tex) lists 5 specific unknowns
- The confidence assessment categorises properties into high/moderate/low confidence
- The NEEDS_VS_CAPABILITIES scoring (7.7 sim vs 2.1 real) is brutally honest

**Minor weakness:**
- The limitations are presented as things that "couldn't" be done (weather, time), not things that "shouldn't" have been done. A top evaluation would also question design decisions that turned out suboptimal

### 5. Future Work with Specific Priorities — Score: 7/10

**Strengths:**
- Every delta item has a concrete "Next step" action
- D2's next step is specific: "deploy NCNN, validate accuracy parity, thread pipeline"
- The four "what would change" items in evaluation_detail.tex are excellent

**Weaknesses:**
- No prioritisation matrix. Which future work items have highest impact vs effort? D3 (GPS lag compensation) is a one-line code change; D8 (payload integration) requires hardware. They should be ranked
- No timeline estimate for future work
- Future work doesn't mention the most impactful improvement: collecting a proper held-out test dataset. This is buried in D5's next step but should be the #1 priority
- Missing: no discussion of what would make this system genuinely deployable (regulatory approval, BVLOS certification, redundancy requirements)

### 6. Reflect on Development Process — Score: 7/10

**Strengths:**
- The four "lessons learned" in evaluation_detail.tex are genuinely insightful
- Lesson 3 (simulation fidelity has diminishing returns) is a sophisticated observation
- Lesson 4 (schedule multiple flight days) is practical and honest

**Weaknesses:**
- No reflection on team dynamics or workload distribution (deferred to D7, but the evaluation should at least acknowledge if certain team members were bottlenecked)
- No reflection on tool choices: Did using Claude/AI assistance change the development process? Was the 74-script test suite a result of AI-assisted development that wouldn't have existed otherwise?
- No reflection on whether the simulation-first approach was actually the right choice for THIS project. The team had 16 weeks. Was spending 10 weeks in simulation before touching hardware optimal, or did it create a false sense of readiness?
- Lesson 1 mentions building label_tool.py in week 16 — but doesn't ask why the team didn't prioritise data collection earlier. Was it a planning failure or a resource constraint?

### 7. Compare Against Industry/Academic State-of-the-Art — Score: 4/10 **CRITICAL GAP**

**What's there:**
- Brief mention of V-model verification philosophy
- Sheridan framework for autonomy levels (R08)
- Implicit comparison to "most university drone projects" (claimed progressive testing is rare)

**What's missing:**
- No citation of specific competing systems or their performance metrics
- No comparison table: "Our system achieves X; SystemY achieves Y; commercial FLIR SkyRanger achieves Z"
- The SAR_COMPARISON.md has 7 academic references ready to cite — none appear in the evaluation
- No mention of AUSPEX, SearchWing, or other open-source SAR frameworks
- No comparison of detection performance: other YOLOv8 SAR papers report specific metrics that could be compared
- No comparison of GPS estimation accuracy against published civilian drone SAR results
- The 4.8 FPS inference rate is presented without context — is this competitive? (It is, for CPU-only Pi, but this should be stated with citations)

---

## Specific Line-Level Issues

1. **Line 23 (P3)**: "estimated cost if discovered in flight: 2 crashed airframes (£2,000+)" — This is speculative and slightly dramatic. Two of the 12 defects (geofence sign, repulsive force) would have caused SSSI incursion, not crashes. Be precise about which defects cause crashes vs regulatory violations vs mission failure.

2. **Line 35 (P9)**: "15 body figures generated programmatically" — This is not a system strength, it's a report-writing practice. Remove from plus/delta table or reframe as "reproducible quantitative evidence."

3. **Line 107**: "The confidence threshold (0.2) was set by visual inspection" — Good honesty, but this contradicts config.py where the threshold is 0.4. Clarify which value is deployed.

4. **evaluation_detail.tex line 56**: "Start with Pi hardware from week 1, not week 16" — This is the most impactful lesson but doesn't acknowledge WHY hardware was delayed. Was it procurement? Team availability? This context matters for the reflection to be genuine.

---

## Summary of Required Improvements

| Priority | Issue | Action |
|----------|-------|--------|
| HIGH | No industry/academic comparison | Add comparison subsection with cited metrics from 3-4 papers |
| HIGH | No alternative architecture evaluation | Add paragraph evaluating Python+MAVLink+Pi vs ROS2+Jetson |
| HIGH | No mission-level performance metrics | Add coverage rate, detection probability, search time estimates |
| MEDIUM | P9 is padding | Remove or reframe |
| MEDIUM | No future work prioritisation | Add impact/effort ranking |
| MEDIUM | Process reflection lacks depth | Add paragraph on simulation-first tradeoffs |
| LOW | Confidence threshold inconsistency | Fix 0.2 vs 0.4 |
| LOW | Cost estimates speculative | Tighten language on P3 |

---

## Verdict

The evaluation is honest and well-structured — better than 80% of university reports. But it stays within its comfort zone: it evaluates what WAS done thoroughly, but avoids evaluating whether the RIGHT things were done. The missing industry comparison and alternative architecture analysis are the biggest gaps preventing a top grade. A marker reading this would think: "Good self-awareness about limitations, but where's the wider context?"
