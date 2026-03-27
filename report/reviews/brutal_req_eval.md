# Brutal Review: Requirements Verification + Evaluation

## Requirements Verification: 72/100

### What works well
- **Table format is solid.** Clean summary table (Tab 1) with Req/Method/Evidence/Status columns gives the examiner a quick scan. Good.
- **R02 (SSSI) is the star subsection.** Four-layer defence described concretely with config parameter names, distances, and behavior. The firmware geofence as a fifth independent layer shows defence-in-depth thinking. This is how every requirement should be written.
- **R05 (Search + Identify) is mathematically rigorous.** The N_eff correction for overlapping frames is genuinely impressive -- most students would claim 19 independent observations and move on. The honest 92% single-pass figure with the two-pass recovery to 99.4% shows real statistical thinking.
- **R07 (Landing offset) probability analysis.** Rician distribution, Gaussian projection, fused sigma -- this is strong quantitative work. The >99% figure after fusion is well-derived.
- **R09 (RTH) three-layer independence.** RC, software, firmware -- each independently sufficient. Clean.

### What is weak

1. **Every single requirement says "Verified (SITL)" or "Verified (simulation)".** This is the elephant in the room. The table's "Verification Status" column is almost uniformly "SITL" with no outdoor flight. The examiner will read this as "verified in a toy environment." The table needs a column or footnote explicitly acknowledging this and stating the gap.

2. **R01 is vague compared to R02.** R01 says "telemetry playback of latitude and longitude tracks against the KML polygon" but gives no numbers. How close did it get to the boundary? What was the minimum margin? R02 is specific (30m buffer, 20m slow zone, 3m hard cutoff). R01 should quote the minimum distance to boundary observed in SITL.

3. **R03 is trivially satisfied and padded.** "Arms without commanding lateral movement" and "SITL home position is set to the TOL coordinates" -- this is tautological. The SITL test proves nothing because you set the home position to TOL yourself. The real test is GPS accuracy at power-on, which you acknowledge (2.5m CEP) but haven't tested. This subsection could be 2 sentences.

4. **R04 is also trivially satisfied.** "A code audit confirms no state commands an altitude above 35m." This is an inspection, not a test. The firmware fence is the real safeguard and gets one sentence. Weak.

5. **R06 (PLB Focus Area) evidence is thin.** "Verified (SITL)" but the description of the SITL test is one sentence: "the aircraft diverted... verified by comparing waypoint indices." No data on: how long the diversion took, coverage completeness of the focus area, whether the resume was seamless, whether any detections were missed during transition. This is a complex feature described with a hand-wave.

6. **R08 (Autonomy Justified) is design-level only.** "Verified (design)" is the weakest possible verification. The Sheridan levels are stated but never tested operationally. Did the operator actually respond to a VERIFY prompt in time? What was the mean response time? Was the 120s timeout ever triggered? None of this is evidenced.

7. **R10 (Report lat/lon + images) lacks quantitative evidence.** No example output shown, no GPS error bounds quoted here (they appear later in evaluation), no sample CSV or JSON. "Ground station logs, CSV, MJPEG stream" is a list of outputs, not evidence of correctness.

8. **R11 and R12 are one-paragraph fillers.** Fine for completeness but they add no technical content. R12 could literally be a single row in the table.

9. **No cross-referencing to evaluation section.** The requirements section and evaluation section cover overlapping ground (GPS accuracy, detection performance) but don't reference each other well. The requirements section should say "see Section X for quantitative analysis" rather than repeating partial figures.

10. **No figure in the entire section.** 128 lines of dense text with no visual aid. A single requirements traceability matrix figure (heatmap of requirement vs. testing tier) would dramatically improve readability and show coverage gaps at a glance.

---

## Evaluation: 78/100

### What works well
- **Plus/delta format is excellent.** 9 plus, 9 delta -- balanced and honest. Most students write 8 pluses and 2 deltas. The equal count signals maturity.
- **Every delta has a "Next step."** This is exactly what examiners want -- not just "we didn't do X" but "here's how we would." Shows engineering thinking.
- **D5 (train/val overlap) is brutally honest.** Admitting your own mAP is inflated takes courage. "The 0.995 mAP likely overestimates real-world accuracy" -- this single sentence could be worth several marks.
- **Bug discovery table (Tab 3) is outstanding.** 12 defects with tier, fix time, and consequence-if-missed. This is concrete, quantified evidence of testing value. The "SSSI incursion; regulatory violation" cost column makes the progressive testing framework tangible.
- **Weather cancellation framing is smart.** Turning the cancelled flight into a positive ("analyse what we have" produced quantitative data "that would otherwise have required multiple flight sorties") is good engineering narrative. Not overdone.
- **Lessons learned are genuine and specific.** Not generic platitudes. "Start with Pi hardware from week 1, not week 16" and "schedule one flight day per week, not per project" are actionable and project-specific.
- **The N_eff detection probability calculation is carried through consistently** from requirements into evaluation discussion.

### What is weak

1. **The biggest delta (D1: no outdoor flight) is understated.** It gets 2 lines in the table and one paragraph in discussion. This is THE critical weakness of the entire project and deserves a dedicated subsection: what specifically remains unverified, what the risk profile looks like, and what the first flight would test. The final paragraph tries to do this but is too compressed.

2. **D8 (payload release not integrated) is buried.** The report describes a servo deployment sequence in R07 (Tarot servo, AUX channel 9, two-stage PWM) as if it's implemented and working. Then D8 says "servo actuation is not wired into the state machine." This is a contradiction that an examiner will catch. R07 should clearly state the mechanism is designed but not integrated, or D8 should reference R07's description as aspirational.

3. **Figures are referenced but likely not generated from real data.** "conf_vs_alt" and "det_vs_speed" are from DJI video replay, which is a proxy. The figure captions should explicitly state "DJI video proxy data" not just "DJI flight video replay" -- the latter sounds like they flew.

4. **Detection heatmap (Fig detection_heatmap) is from simulation.** Caption says "during simulated search" which is honest, but this figure adds little value. A simulated heatmap just shows the lawnmower pattern works, which is trivially true.

5. **The "What Would Change" section repeats the deltas.** Items 1, 2, 4, 5 are restated from D1/D2/D5/D6. This is padding. The section should add NEW insights or synthesize, not echo. Only item 3 (CI/CD) and item 4 (weekly flights) are genuinely new observations.

6. **No quantitative comparison to related work.** The evaluation discusses performance in isolation. How does 4.8 FPS / 206ms compare to other university drone SAR projects? How does CEP 2.3m compare to industry systems? Without context, the examiner can't judge whether these numbers are good or bad.

7. **Lessons learned section could be stronger on team/process.** All four lessons are technical. No mention of: communication gaps, decision-making bottlenecks, what the team would do differently in terms of work allocation. The brief says D7 covers team working, but even one team-process lesson here would round out the section.

8. **The summary paragraph at the end is too generous.** "Architecturally sound and quantitatively characterised" is self-congratulatory for a system that never flew. "Remaining risk is in parameter tuning and environmental validation rather than fundamental redesign" -- an examiner might disagree. The single-class detector (D6) and unintegrated payload (D8) are arguably architectural gaps, not parameter tuning.

9. **Testing framework summary (Tab five-tier-summary) is redundant.** This table appears in both the testing section and the evaluation section. Once is enough. The evaluation should reference it, not reproduce it.

10. **No failure mode analysis.** What happens if the system fails during a real flight? No discussion of: graceful degradation, partial mission completion metrics, what "success" looks like if only 60% of the area is searched. The evaluation is binary (works/doesn't) rather than graduated.

---

## Requirement-by-Requirement Weakness Summary

| Req | Score | Key Weakness |
|-----|-------|-------------|
| R01 | 70 | No minimum-margin numbers from SITL, vague compared to R02 |
| R02 | 90 | Excellent. Minor: no diagram shown inline (just referenced) |
| R03 | 60 | Tautological SITL test, no real GPS data |
| R04 | 65 | Code audit is inspection not testing, firmware fence under-emphasized |
| R05 | 88 | Strong math. Weak: mAP inflated by train/val overlap (honest about it though) |
| R06 | 55 | Thin evidence, one-sentence SITL test, no data on diversion performance |
| R07 | 75 | Good probability analysis but R07/D8 contradiction on servo integration |
| R08 | 50 | "Verified (design)" is not verification. No operational data. |
| R09 | 82 | Three layers well described, all SITL-tested |
| R10 | 60 | No example output, no error bounds, just a list of channels |
| R11 | 70 | Procedural, fine for what it is |
| R12 | 80 | Trivially verifiable, appropriately brief |

## Overall Scores

| Section | Score | Rationale |
|---------|-------|-----------|
| Requirements Verification | **72/100** | Strong on R02, R05, R07 math. Weak on: everything being SITL-only, R06/R08 thin evidence, R07/D8 contradiction, no figures, R03/R04 trivially satisfied |
| Evaluation | **78/100** | Honest plus/delta balance, excellent bug table, good lessons. Weak on: D1 understated, redundancy with deltas in "what would change", no comparison to related work, self-congratulatory summary, no failure mode analysis |

## Top 5 Fixes (highest impact, lowest effort)

1. **Fix the R07/D8 contradiction.** Either remove the servo deployment details from R07 and say "designed, not integrated" or merge D8 into R07. Takes 10 minutes, prevents examiner catching you in an inconsistency.

2. **Add a requirements traceability figure.** A simple matrix (requirement vs. testing tier, colored by pass/fail/untested) would replace 500 words of text and make the SITL-only gap visible but also show how much WAS verified.

3. **Expand R06 evidence.** Add 3-4 sentences: how many focus area waypoints were generated, how long the diversion took, whether the search speed reduction was observed in telemetry, whether resume worked on the correct waypoint.

4. **Add one quantitative comparison to related work in evaluation.** Even one sentence: "University of X achieved Y FPS on Z hardware; our 4.8 FPS on Pi 5 is comparable/lower/higher because..." gives the examiner context.

5. **Trim "What Would Change" to remove delta repetition.** Keep items 3 (CI) and 4 (weekly flights) as genuinely new. For items 1, 2, 5: just reference the delta number ("addressing D2 would require...") instead of restating.
