# CRITIQUE: SAR Drone Search Parameter Optimisation Decision Flow

**Score: 72 / 100**

Reviewed as a standalone document by a teammate seeing it for the first time.

---

## Overall Verdict

The document is well-structured and the sequential-chain argument (target size -> altitude -> speed -> angle -> NFZ -> overlap) is genuinely compelling. A reader CAN follow the logic from start to finish. The priority stack (safety > detection > speed > energy) is stated early and mostly honoured. The figures are relevant and placed correctly.

But it has real problems. Several numbers appear without derivation, the lighting tables look invented, and the Pareto argument is hand-waved rather than demonstrated. It reads more like a polished sales pitch than an engineering justification, which will raise red flags with a technical examiner.

---

## Detailed Critique (by question)

### 1. Does it flow logically?

**Mostly yes, but with two breaks.**

The six-step chain in Section 3 is the backbone and it works: detection ceiling -> altitude -> speed -> scan angle -> NFZ -> coverage. That chain is clear.

Break 1: Section 7 ("Sequential Measurement Chain") repeats the exact same chain from Section 3 but adds the lighting tables. It feels like two drafts were merged. A first-time reader hits the same argument twice and wonders if they missed something or if the authors are padding.

Break 2: Section 8 ("Non-Quantifiable Design Choices") comes AFTER the Pareto and sensitivity analysis, which feels like an afterthought. Pattern choice and operator-in-the-loop are design decisions that should come BEFORE the quantitative optimisation, not after. You chose lawnmower, THEN optimised its parameters. Say so earlier.

### 2. Is the priority ordering stated early and followed through?

**Stated early: yes (end of Section 1). Followed through: mostly.**

Safety is genuinely treated first (NFZ buffer, 2.2x factor, speed ramp). Detection is treated second (altitude ceiling, 30% margin). Good.

But energy and speed ordering is muddled. The document says speed > energy, but then Section 3 Step 4 optimises for energy (scan angle), and the composite score weights are 40% detection + 35% coverage + 25% energy. Speed/time is buried inside "coverage" with no explicit weight. If speed matters more than energy, why does energy get 25% weight and time gets... nothing explicit? This is a quiet contradiction.

### 3. Does each step clearly follow from the previous?

**Steps 1-3: yes, very clearly. Steps 4-6: weaker.**

Step 4 (scan angle) follows from Steps 1-3 only in the sense that altitude and speed are now locked. But the jump from "how fast can we fly" to "what angle minimises energy" is abrupt. There is no bridging sentence explaining WHY energy is the next thing to optimise. The priority stack says speed > energy, so a reader expects the next step to address time/coverage, not energy. One sentence of justification would fix this.

Steps 5-6 (NFZ buffer, coverage) follow logically but feel rushed compared to the detail given to altitude and speed.

### 4. Are the lighting condition tables plausible?

**No. These are the weakest part of the document.**

Table 4 claims max detection altitude of 63m in bright sun, 52m overcast, 38m at dusk. Table 5 gives max detectable speed by lighting condition. But:

- The document states the model was validated at mAP50=0.995 but says NOTHING about testing under different lighting. There is no mention of a dusk dataset, overcast dataset, or any lighting variation in training or testing.
- The confidence values (0.94, 0.91, 0.85 at 35m) are suspiciously round and evenly spaced.
- The speed envelope table (12, 10, 7 m/s) also has suspiciously clean numbers.
- There is no citation, no test methodology, no sample size. Were these measured? Simulated? Estimated?

An examiner will immediately ask: "How were these numbers obtained?" If the answer is "we extrapolated from synthetic data," the tables actively hurt credibility. If they were measured during real flights, that needs to be stated explicitly. If they are theoretical estimates, label them as such.

### 5. Are the figures in the right place?

**Yes, all seven figures are placed immediately after their first reference.** This is good practice. The decision flow infographic at the top provides a visual roadmap before the text begins. The altitude-speed tradeoff (Fig 3) supports the speed discussion. The energy heatmap (Fig 4) supports the scan angle discussion. The top-3 paths (Fig 5) supports the evaluation table. The tornado and spider plots (Figs 6-7) support the sensitivity discussion. The Pareto parallel coordinates (Fig 8) supports the optimality argument.

One issue: Figure 1 (decision flow infographic) is referenced in the caption but never discussed in the text. It just sits there. Either reference it explicitly ("as shown in Figure 1, the chain begins with...") or remove the figure number.

### 6. Is anything confusing, redundant, or missing?

**Redundant:**
- Section 3 and Section 7 tell the same story. Section 7 adds the lighting tables but otherwise duplicates the six-step chain. Merge them or clearly differentiate their purpose ("Section 3 gave the logic; Section 7 adds experimental validation").

**Confusing:**
- The composite score formula (40% detection + 35% coverage + 25% energy) appears in Table 2 and Figure 3 but is never justified. Why these weights? They directly determine which configuration "wins." If you change the weights, a different configuration tops the table. An examiner will ask: "Why 40/35/25 and not 50/30/20?"
- "Coverage" and "time" are used interchangeably in some places. Coverage appears as a score component (35%), but coverage in the NFZ discussion means spatial completeness (96%). These are different things.
- The "cumulative detection probability above 99.97%" (Section 3 Step 3) assumes independent frame detections. This is stated nowhere. If consecutive frames are correlated (same viewing angle, same lighting), the real probability is lower.

**Missing:**
- No discussion of what happens if conditions are WORSE than expected (wind, rain, fog). The sensitivity analysis perturbs parameters one at a time but never considers correlated failure (e.g., low light AND wind simultaneously).
- No mention of the actual battery capacity or what "10.9% of battery" means in absolute terms.
- No discussion of the transit energy budget. The document says the battery must cover transit, descent, verification, and return, but only quantifies the search phase.
- The swath overlap (20%) appears in the final table but is barely discussed. Step 3 mentions dwell time for detection, but overlap is about spatial coverage gaps, not temporal detection. These are different failure modes and both matter.

### 7. Would a teammate understand WHY we chose 35m, 8 m/s, 70deg?

**35m: yes.** The detection ceiling argument (63m max, 30% margin) is clear and intuitive.

**8 m/s: mostly.** The dwell-time argument (14 frames, 10 required) makes sense, but the jump from "max 11.5 m/s" to "chose 8 m/s" is a 30% margin, not the stated 15% in Table 5. Which margin are we using? The document uses 30% for altitude and apparently 30% for speed too, but Table 5 says 15%. Inconsistent.

**70deg: yes.** The energy heatmap makes the longest-edge alignment argument visually obvious.

### 8. Is the "we're on the Pareto frontier" argument convincing?

**Partially.** The parallel coordinates plot exists and the text claims the selected point is Pareto-optimal, but:

- The document never defines what Pareto optimality means for this problem. A reader unfamiliar with the concept gets no explanation.
- The claim "no other Pareto-optimal configuration achieves a better balance" is tautological. Every point on a Pareto frontier is by definition non-dominated. The argument should be: "we are on the frontier AND at the knee," which is a different (stronger) claim.
- The composite score already bakes in the weight preferences. Saying the highest-scoring point is also Pareto-optimal is circular if the score was designed to select it.

### 9. Does it read like a story or a list of facts?

**It reads like a well-structured technical argument -- neither a story nor a list.** The six-step chain gives it narrative momentum. The problem statement sets stakes. The numbered steps create a logical flow. This is one of the document's strengths.

However, the tone is slightly too confident. Phrases like "unbroken chain," "no value was assumed or rounded for convenience," and "the only one that avoids a worst-in-class ranking" are strong claims that invite scrutiny. Technical writing should let the evidence speak; superlatives weaken it.

### 10. Is it too long?

**It is about 1-2 pages too long because of the redundancy between Section 3 and Section 7.** Merging them would bring it to 7 pages, which is right for the content. The sensitivity and Pareto sections (Sections 5-6) are appropriately concise. Section 8 (qualitative choices) could be tightened to a single paragraph.

### 11. Any self-congratulatory language?

A few instances:

- "No value was assumed or rounded for convenience" (Section 5) -- this is almost certainly false. 30% margin is a round number. 8 m/s is a round number. 30m buffer is a round number.
- "the only one that avoids a worst-in-class ranking on any single axis" -- unprovable without showing all Pareto points.
- "unbroken chain" -- let the reader judge that.

None of these are egregious, but collectively they create a slight air of overselling.

### 12. Any claims without justification?

- **Lighting tables (Tables 4 and 5)**: no methodology, no data source, no sample size.
- **Composite score weights (40/35/25)**: never justified.
- **"cumulative detection probability above 99.97%"**: assumes frame independence, not stated.
- **"4.8 frames per second (benchmarked on the Pi 5)"**: this is justified elsewhere in the project but not in THIS standalone document. A reader of this document alone has no evidence for it.
- **"halves the energy compared to the worst orientation"**: vague. Halves from what to what?
- **"RSS combination gives a 23m requirement"**: the RSS formula is not shown. What values went in?
- **mAP50 = 0.995**: no test set size, no cross-validation mention, no discussion of whether this generalises to real conditions.

---

## TOP 5 IMPROVEMENTS (highest impact)

### 1. Kill or justify the lighting tables (Tables 4 and 5)
These are the single biggest credibility risk. Either: (a) describe exactly how these numbers were obtained (test methodology, dataset, conditions), (b) label them explicitly as theoretical estimates derived from pixel-size scaling and state the assumptions, or (c) remove them entirely. Right now they look fabricated and an examiner will zero in on them.

### 2. Merge Section 3 and Section 7
The six-step chain and the "sequential measurement chain" are the same argument told twice. Merge them into one section that interleaves the logic with the experimental evidence (lighting tables, if kept). This eliminates redundancy and tightens the document by 1-2 pages.

### 3. Justify the composite score weights (40/35/25)
The entire ranking in Table 2 depends on these weights. Add 2-3 sentences explaining why detection gets 40%, coverage 35%, and energy 25%. Tie them back to the priority stack. Even better: show that the ranking is robust to weight perturbation (e.g., "configuration #1 remains top-ranked for any detection weight above 30%").

### 4. Fix the margin inconsistency (30% vs 15%)
Section 3 uses a 30% margin for altitude (63m ceiling -> 35m chosen). Table 5 uses a 15% margin for speed. Section 3 Step 3 implies 8 m/s is chosen from 11.5 m/s max, which is also 30%. Pick one margin philosophy and apply it consistently, or explain why different margins apply to different parameters.

### 5. State the independence assumption for cumulative detection probability
The 99.97% figure is the headline number. It assumes each of the 14 frames is an independent detection trial with 95% per-frame probability. If frames are correlated (same angle, same lighting, temporal proximity), the real cumulative probability is lower. Either: (a) state the assumption explicitly, (b) argue why it is reasonable (e.g., target moves through the frame, changing appearance), or (c) compute a conservative estimate with a correlation factor.

---

## Minor Issues (not in top 5 but worth fixing)

- Figure 1 is never referenced in the body text. Add a reference or remove the figure number.
- "golden hour of hypothermia survivability" -- the golden hour is typically associated with trauma, not hypothermia. If this is a deliberate analogy, make it explicit. If it is a mistake, correct it.
- The document never states the battery capacity in Wh. "10.9% of battery" is meaningless without knowing the total.
- "fenced wildlife reserve with no public access" -- is this a fact or an assumption? If a fact, cite or state the source.
- Move Section 8 (qualitative choices) earlier, perhaps after Section 2, since lawnmower pattern choice precedes the quantitative optimisation.
