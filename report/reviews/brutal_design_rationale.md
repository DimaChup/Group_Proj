# Brutal Review: Design Rationale (Section 3)

**Reviewer:** Claude Opus 4.6 | **Date:** 2026-03-27 | **Score: 82/100**

---

## Overall Assessment

This is a strong, evidence-rich section with quantitative backing for nearly every claim. The MCDA tables are well-structured, the parameter derivation chain is rigorous, and the "Decisions That Changed" subsection is genuinely impressive for a student report -- examiners love seeing honest evidence-based corrections. However, there are structural weaknesses, some logical gaps, and a few paragraphs that read more like project diary entries than academic rationale.

---

## Paragraph-by-Paragraph Analysis

### 3.1 STEEPLE Analysis (lines 8-33)

| Dimension | Verdict | Issue |
|-----------|---------|-------|
| Social | OK | Murphy 2014 is appropriate. "Volunteer mountain rescue teams" -- is this actually the target user? The rest of the report describes a university project. Slight mismatch in framing. |
| Technological | GOOD | Concrete numbers (4.8 FPS, 4 vs 90+ packages). Well-cited. |
| Economic | GOOD | 565 vs 5800 comparison is compelling. |
| Environmental | GOOD | Three-layer geofence is well-described. The 3kg AUW claim needs a source or measurement. |
| Political | WEAK | "Supports BVLOS but tested within VLOS" is a non-statement -- everything supports BVLOS if you don't actually do it. SORA citation is good but this paragraph says almost nothing substantive. |
| Legal | OK | Data protection point feels token -- "stored locally" is not a GDPR argument. No mention of data retention period, subject access rights, or DPIA. |
| Ethical | GOOD | The timeout auto-reject rationale is a nice touch. |

**Weakest paragraph: Political.** It makes a claim ("supports BVLOS") without evidence and then immediately admits it wasn't tested. This reads as padding. Either demonstrate the architectural feature that enables BVLOS (e.g., link-loss RTL, autonomous decision-making without operator) or cut the claim.

### 3.2 Search Parameter Optimisation (lines 35-63)

**Strong.** The coupling matrix figure, 216-configuration sweep, and dependency chain are excellent. The Pareto compromise is well-articulated with specific numbers (96% coverage, Pd > 99.97%, 12.6 Wh).

**Issues:**
- "Scan angle selection dominates altitude selection for energy efficiency" -- this is a key finding but is buried in a paragraph. Deserves its own callout or bold statement.
- The 4% coverage gap dismissal ("within a fenced wildlife reserve with negligible casualty probability") is asserted without evidence. How do you know it's fenced? Is there a reference or site survey? An examiner could challenge this.
- Figure 2 (altitude-speed trade-off) uses a composite score with weights (40/35/25%) but these weights are not justified. Why 40% detection, not 50%? Why not equal weights? This is the same criticism you'd make of anyone else's MCDA.

### 3.3 Parameter Derivation Chain (lines 64-91)

**Very strong.** This is the best part of the section. Eight steps, each traceable to a physical measurement. The chain from target size to altitude to speed to lane spacing to NFZ margin is rigorous and well-paced.

**Issues:**
- Step 1: "Below approximately 20 model-input pixels, detection confidence drops below the operational threshold of 0.2" -- where does this 20-pixel threshold come from? Is it from your own testing or literature? Needs a citation or reference to your own results section.
- Step 4: The RSS analysis is mentioned but not shown in the body. Even a one-line equation would help: sqrt(3^2 + ...) = 4.6m.
- Step 7: Repeats the 4% coverage / fenced reserve claim from 3.2 verbatim. Feels copy-pasted.

### 3.4 Hardware Platform Selection (lines 92-100)

**Adequate but thin.** Three bullet points for the entire hardware rationale. The global shutter justification is good. "No thermal imaging" is well-argued. The MAVProxy point is a workaround description, not a design rationale.

**Missing:** No discussion of airframe selection (EDU-450 vs alternatives), battery selection, or GPS receiver choice. These are mentioned in passing but never justified. Even a single sentence each would help.

### 3.5 Companion Computer Trade Study (lines 102-126)

**Good MCDA.** Clear table, reasonable weights, justified scores.

**Issues:**
- Intel NCS2 is a weak comparator -- it was discontinued in 2023 and is not a standalone SBC. Including it makes the comparison feel like a straw man. A Coral Dev Board or Orange Pi 5 would be more credible alternatives.
- "Scores highest across all criteria" (line 126) -- Pi 5 does NOT score highest on latency (implied by missing any score below 5). The text overstates the result.
- Weight justification is a single sentence. For an MCDA to be credible, you need to show WHY cost and compatibility get 0.20 each while power gets only 0.10.

### 3.6 Communication Architecture Trade Study (lines 128-151)

**Good.** The Python 3.13 pyserial regression is a real discovery and well-documented. The multi-consumer benefit is a genuine advantage.

**Issue:** Direct serial scores 1 on Python 3.13 compatibility and 1 on multi-consumer, but these are not inherent limitations of serial -- they are specific to this Python version and this application. The table conflates a temporary bug with a fundamental architectural weakness. Acknowledge this.

### 3.7 Software Architecture Rationale (lines 153-165)

**Adequate.** Four clear principles. The dual-backend point is good.

**Missing:** No discussion of why Python over C++ or Rust. No discussion of testing strategy (unit tests? integration tests?). The "same code, simulation and real" claim is strong but where is the evidence it actually worked without modification?

### 3.8 Detection Model Selection (lines 167-192)

**Good MCDA.**

**Issues:**
- SSD MobileNetV2 mAP of 0.88 -- on what dataset? Your custom dataset or COCO? If COCO, this is not comparable to YOLOv8n's 0.995 on your custom dataset. You are comparing apples to oranges. This is the most vulnerable point in the section to examiner challenge.
- "Training data requirement" criterion with scores 5/4/3/4 -- what does "small" mean? You trained on 366 images. Would YOLOv8s really need more? This criterion feels invented to pad YOLOv8n's score.
- The domain randomisation citation is good but the paragraph doesn't explain what domain randomisation actually is.

### 3.9 Coverage Path Planning (lines 194-217)

**Good.** IAMSAR reference is strong. The rotate-rasterise-rotate-back algorithm is well-described.

**Issue:** The expanding square "lacks a formal completeness guarantee for arbitrary polygons" -- citation needed. This is a strong claim used to eliminate a competitor.

### 3.10 State Machine Design (lines 219-221)

**Too short.** One paragraph for a 20-state, 32-transition FSM. This deserves at least a state diagram reference and a brief discussion of why 20 states (vs fewer/more). The O(1) dispatch is a trivial implementation detail, not a design rationale. The five safety mechanisms are listed but not prioritised or analysed for independence (do they share failure modes?).

### 3.11 Autonomy Level Justification (lines 223-233)

**Excellent.** This is the second-best part of the section after the parameter derivation chain. The false-positive vs false-negative cost analysis is well-reasoned. The Sheridan levels are correctly applied. The 20x automation advantage claim needs a citation or calculation.

**Issue:** The "lawnmower pattern's guarantee of revisiting every cell" (line 229) -- this is only true with zero drift and perfect navigation. In practice, GPS drift means cells near lane boundaries may not be revisited. Acknowledge this limitation.

### 3.12 Decisions That Changed (lines 235-249)

**Excellent.** This subsection alone could raise the section grade. Examiners value intellectual honesty and evidence-based iteration. All four corrections are concrete, quantified, and consequential.

**No issues.** This is the gold standard for the section.

### 3.13 Why Not ROS (lines 251-263)

**Good.** Three clear reasons, well-argued. The 40-60 hours learning curve estimate with citation is credible.

**Issue:** "Approximately 5 hours" for pymavlink learning -- this feels made up. Is there evidence? If not, remove the specific number.

### 3.14 Camera Selection (lines 265-273)

**Good.** The rolling shutter distortion calculation (7.5 pixels, 0.5m ground error) is well-quantified.

**Issue:** "The IMX296 was provided as part of the university equipment package" (line 267) undermines the entire trade study. If you didn't choose it, the rationale is post-hoc justification, not a design decision. Be honest about this -- "we validated the provided camera against alternatives" is more credible than pretending it was a free choice.

### 3.15 Field Day Adaptation (lines 275-292)

**Good narrative but questionable inclusion.** This reads like a project diary entry. The go/no-go framework is good SE practice but the level of detail (wind speed, gust factor) is excessive for a design rationale section. Consider moving to Testing/Results or an appendix.

---

## Weakest Paragraph

**The Political STEEPLE item (line 24-25).** It makes an unsubstantiated claim ("supports BVLOS"), immediately walks it back ("tested within VLOS"), and adds nothing beyond a regulation citation. It is the only paragraph in the section that contains no quantitative evidence or technical insight. An examiner would either ignore it or use it as evidence of superficial analysis.

---

## Charts/Tables That Would Strengthen This Section

| Proposed Visual | Where | Why |
|----------------|-------|-----|
| **Detection confidence vs target pixel size** (scatter/line plot from your own data) | After Step 1 of parameter chain (line 69) | The 20-pixel threshold is the foundation of the entire altitude calculation but has no visual evidence. Plot confidence vs pixel count from video_test.py data to show the drop-off. This is the single highest-impact addition. |
| **STEEPLE impact/likelihood matrix** (2x2 or radar chart) | After STEEPLE subsection (line 33) | The description list format makes all 7 dimensions look equally important. A visual weighting would show which dimensions actually drove decisions. |
| **Pareto front visualisation** (2D: energy vs detection probability) | After line 62 | You mention Pareto compromise but never show the Pareto front. Plot all 216 configurations as dots, highlight the Pareto-optimal set, mark the selected point. This would be the strongest figure in the section. |
| **Safety mechanism independence matrix** (table showing shared/independent failure modes) | After FSM rationale (line 221) | Five safety mechanisms are listed but their independence is not analysed. A simple matrix showing which mechanisms share failure modes (e.g., software crash kills both geofence and timeout) would demonstrate rigour. |
| **Decision timeline** (horizontal bar or Gantt showing when each "decision that changed" was discovered) | After Section 3.8 (line 249) | The narrative is strong but a timeline would visually reinforce the iterative development story. |

---

## Scoring Breakdown

| Criterion | Score | Notes |
|-----------|-------|-------|
| Clarity of writing | 85 | Clean, professional prose. Occasional verbosity. |
| Quantitative evidence | 90 | Nearly every claim has numbers. Standout for a student report. |
| Citation quality | 80 | Good mix of standards, textbooks, and papers. Some claims uncited (20-pixel threshold, 20x automation advantage, 5-hour pymavlink). |
| Logical coherence | 78 | Parameter chain is excellent. STEEPLE Political is weak. SSD mAP comparison is potentially invalid. |
| MCDA rigour | 75 | Tables are well-formatted but weight justifications are thin across all four MCDAs. Straw-man comparators in companion computer study. |
| Intellectual honesty | 92 | "Decisions That Changed" is outstanding. Camera "provided by university" admission is good. |
| Visual support | 70 | Two figures (coupling matrix, alt-speed trade-off) are good but the section needs 2-3 more. |
| Completeness | 80 | Missing airframe/battery rationale, testing strategy, and weight justification for MCDAs. |

**Overall: 82/100**

---

## Top 5 Actions to Reach 90+

1. **Add detection confidence vs pixel size plot** -- this is the foundation of the altitude calculation and currently has zero visual evidence.
2. **Justify MCDA weights** -- one sentence per table explaining WHY each weight was chosen (e.g., "Cost weighted 0.20 because the project budget is capped at 600 GBP").
3. **Fix the SSD MobileNet mAP comparison** -- either benchmark SSD on your custom dataset or explicitly state the COCO vs custom dataset difference and why the comparison is still informative.
4. **Expand FSM rationale to at least 2 paragraphs** -- the 20-state machine is a core contribution but gets less text than the camera selection.
5. **Cut or move Field Day Adaptation** -- it's good content but belongs in Testing/Results, not Design Rationale.
