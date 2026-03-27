# BRUTAL REVIEW: Design Rationale Section

**Reviewer:** Claude Opus 4.6 | **Date:** 2026-03-27 | **File:** `report/sections/design_rationale.tex`

---

## Overall Score: 78/100

This is a strong section -- comfortably above the 75 threshold for Decision Making, but not yet in the 83+ "outstanding" band. The MCDA tables are rigorous, the STEEPLE is genuine, and the decisions-changed narrative is the best part of the entire section. What holds it back: some scores feel invented, one MCDA is borderline circular, and there are gaps in evidence traceability.

---

## Dimension Scores

| Dimension | Score | Notes |
|-----------|-------|-------|
| Evidence quality | 72 | Good bench data cited; some MCDA scores lack provenance |
| STEEPLE depth | 80 | All 7 dimensions substantive; not boilerplate filler |
| MCDA rigor | 75 | 5 tables, weights stated, but criteria sourcing unclear |
| Decisions-changed narrative | 90 | Best part. Four real pivots with measurement data |
| Tone / professionalism | 82 | Confident, evidence-forward, occasional over-claiming |

---

## 1. Evidence Quality (72/100)

**What works:**
- Bench data is real and specific: 207ms inference, 4.8 FPS, 0.966 confidence, 50/50 detection, RMS 0.399 calibration
- Focal length correction with exact measurements (92cm at 1m) and downstream impact (3m bias)
- Camera resolution argument with pixel-count math (20x14 vs 46x32)
- Cost comparison: GBP 565 vs GBP 5,800 DJI Matrice

**What's weak:**
- **SSD MobileNetV2 mAP of 0.88 -- where does this come from?** The text says "reported mAP values on the COCO benchmark" but this is a custom single-class dummy detector. Did you actually train/benchmark MobileNetV2 on your dataset? If not, the comparison is apples-to-oranges and the MCDA score is fabricated.
- **YOLOv8s at 450ms and YOLOv8m at 820ms on Pi 5** -- were these actually benchmarked? The session logs only show best.tflite (YOLOv8n) benchmarked at 207ms. If these numbers are extrapolated from FLOP ratios rather than measured, say so.
- **"Training data requirement" criterion** in the model MCDA (Table 5) -- YOLOv8n scored 5 ("small") and YOLOv8s scored 4 ("moderate"). These are the same architecture with different widths; they train on the same data. This criterion feels invented to pad YOLOv8n's lead.
- Wind speed measurements on field day (12 m/s sustained, 18 m/s gusts) -- source? Weather station? Phone app? Cite it.

---

## 2. STEEPLE Depth (80/100)

**What works:**
- Every dimension has a concrete, project-specific claim (not generic "drones help society")
- Social: operator-in-the-loop tied to public trust with Murphy citation
- Environmental: three-layer geofence + 30m waypoint filtering + firmware layer -- four independent defenses named
- Legal: local data storage, SSSI compliance, auditable distance logs
- Ethical: 120s timeout auto-reject tied to coverage-vs-investigation trade-off -- this is genuinely thoughtful

**What's weak:**
- **Political dimension is thin.** "Complied with CAA Open A3" and "tested within VLOS" is compliance description, not political analysis. A stronger version would discuss the political landscape: UK CAA's evolving BVLOS framework, the 2024 drone regulation updates, how volunteer SAR teams lobby for expanded permissions, or the tension between innovation policy and precautionary regulation.
- **Economic could quantify operational savings.** You state the BOM is GBP 565 but don't estimate the operational cost (cost per hour, cost per search mission) vs. helicopter SAR or human ground teams. That's the actual economic argument for adoption.
- **No stakeholder mapping.** STEEPLE is strongest when it shows tensions between dimensions (e.g., Economic pressure for cheaper hardware vs. Ethical requirement for reliable detection). The dimensions are presented in isolation.

---

## 3. MCDA Rigor (75/100)

**Five MCDA tables present:**
1. Companion computer (Table 2) -- Pi 5 vs Jetson Nano vs Intel NCS2
2. Communication architecture (Table 3) -- Direct serial vs MAVProxy vs ROS 2
3. Detection model (Table 4) -- YOLOv8n/s/m vs SSD MobileNet
4. Search pattern (Table 5) -- Lawnmower vs Spiral vs Expanding Square vs Random
5. (No table for state machine or autonomy level -- these are argued narratively)

**What works:**
- All tables use consistent format (1-5 scale, weights sum to 1.0, weighted totals computed)
- Weights are stated explicitly and claimed to be set before scoring
- The text repeats "criteria weights were established before candidate scoring" -- good practice

**What's weak:**
- **The phrase "criteria weights were established before candidate scoring based on mission requirements" appears verbatim four times.** This reads as a defensive formula rather than genuine methodology. A stronger version would show HOW the weights were derived (e.g., pairwise comparison, team ranking exercise, requirement traceability). Just saying "we set weights first" doesn't prove the weights are defensible.
- **Communication architecture MCDA (Table 3) is borderline circular.** Direct serial scores 1 on Python 3.13 compatibility AND 1 on multi-consumer AND 2 on reliability -- it was dead before the MCDA started. When a candidate is non-viable due to a blocking constraint, a proper decision method eliminates it as infeasible rather than dragging it through weighted scoring. The MCDA format here is cosmetic.
- **Pi 5 scores 5 on every single criterion in Table 2.** A candidate that dominates on all axes doesn't need a weighted MCDA -- it needs a one-sentence justification. The table exists to show process but actually shows there was no real trade-off.
- **No sensitivity analysis.** What if you change the weights? Does the winner flip? Even a one-sentence "the result is robust to +/-0.05 weight perturbation" would add credibility.
- **Random walk as a search pattern candidate (Table 5).** Including a straw-man option that scores 1 on coverage guarantee in a SAR context makes the MCDA look staged. Three genuine candidates would be more convincing.

---

## 4. Decisions-Changed Narrative (90/100)

**This is the section's crown jewel.** Four real pivots, each with the pattern: assumption -> measurement -> correction. This is exactly what the rubric means by "evidence-based decisions" and "adapting to changing circumstances."

- Focal length correction: specific measurement, quantified downstream impact (3m bias at 30m altitude)
- Camera resolution: pixel-count math with detection threshold reasoning
- TFLite runtime: real dependency conflict with no-code-change resolution
- Serial communication: real bug, real workaround, bonus multi-consumer capability

**The only weakness:** all four are discoveries/corrections, not trade-offs where the team deliberated between options. A stronger version would include at least one decision where the team genuinely disagreed, weighed evidence, and changed course -- something with human deliberation, not just "we measured and fixed it."

---

## 5. Tone & Professionalism (82/100)

**What works:**
- Confident without being arrogant
- Technical claims are specific and verifiable
- Good use of quantified statements ("22% deviation," "8% of endurance budget")
- The autonomy level justification (Section 3.6) reads like a conference paper -- false positive vs false negative cost asymmetry is well-argued

**What's weak -- WEAKEST PARAGRAPH:**

> "YOLOv8n is the only variant that achieves real-time inference on the Pi 5 CPU within the 300 ms-per-frame budget required for useful detection at search speed. Larger variants (YOLOv8s at 11.2 M parameters, YOLOv8m at 25.9 M) exceeded this budget by factors of two and four respectively. SSD MobileNetV2 matches YOLOv8n on speed but delivers lower accuracy, with reported mAP values on the COCO benchmark substantially below YOLO variants due to its simpler feature pyramid."

**Why it's the weakest:** Three problems: (1) The 300ms budget appears from nowhere -- it is never derived from search speed, frame rate, or detection probability. Why 300ms and not 500ms or 200ms? (2) "Reported mAP values on the COCO benchmark" is comparing COCO mAP to custom-dataset mAP for the YOLO variants -- the comparison is methodologically invalid unless you trained MobileNet on the same dataset. (3) "Due to its simpler feature pyramid" is a hand-wave explanation that wouldn't survive peer review.

---

## 6. Figures & Tables Referenced vs. Present

| Reference | In Section? | Status |
|-----------|-------------|--------|
| Table `tab:hw-bom` (hardware BOM, GBP 565) | Referenced in STEEPLE Economic | **MISSING from this section** -- must exist elsewhere in report |
| Table `tab:mcda-companion` (companion computer) | Defined here | PRESENT |
| Table `tab:mcda-comms` (communication architecture) | Defined here | PRESENT |
| Table `tab:mcda-model` (detection model) | Defined here | PRESENT |
| Table `tab:mcda-search` (search pattern) | Defined here | PRESENT |
| Appendix `app:states` (transition table) | Referenced in FSM section | **MUST EXIST in appendices** -- verify |
| Section `sec:results` | Referenced in camera resolution paragraph | **Cross-reference only** -- must exist |

**Missing figures:**
- **No figure showing the STEEPLE analysis visually** (e.g., a radar chart or matrix). Pure text STEEPLE is fine but a visual would hit the "innovative techniques" Communication criterion.
- **No figure showing the state machine or FSM diagram.** The section references 20 states and 32 transitions but includes no visual. Even if it's in Section 4, the Design Rationale section should at minimum reference the figure by number.
- **No figure of the geofence layers.** The Environmental dimension describes a "three-layer geofence" but there's no diagram showing how speed capping, repulsive field, and hard-boundary interact.
- **No photograph or diagram of the hardware platform.** The Hardware Platform Selection subsection discusses the airframe, Pi 5, IMX296, and MAVProxy bridge but includes no system photo, wiring diagram, or architecture figure.
- **No cost breakdown figure.** The GBP 565 claim references Table `tab:hw-bom` but doesn't include it.

**Verdict on figures:** The section is text-heavy with 4 MCDA tables and zero figures. For a 236-line section, at least 1-2 figures would improve readability and hit the Communication rubric criterion for "innovative techniques and resources."

---

## 7. Is This Section Alone Worth 75+ for Decision Making?

**Yes, barely.** Score: ~76-78 for Decision Making specifically.

**Why it clears 75:**
- Five formal MCDA tables with explicit weights
- STEEPLE with all 7 dimensions populated substantively
- Four evidence-based design corrections with real measurements
- Autonomy level justification with cost-asymmetry analysis and Sheridan levels
- Camera, ROS, and weather adaptation rationales are genuine engineering decisions

**Why it doesn't reach 83+:**
- Some MCDA scores appear fabricated (MobileNet mAP, YOLOv8s/m inference times)
- Weight derivation is asserted but never shown
- No sensitivity analysis on any MCDA
- One MCDA (comms) has a non-viable candidate dragged through scoring
- One MCDA (companion) has a dominant candidate that trivializes the analysis
- The section is figure-free despite describing complex multi-layer systems
- No stakeholder tension analysis in STEEPLE

---

## 8. What's Still Fake/Weak

| Item | Severity | Fix |
|------|----------|-----|
| YOLOv8s (450ms) and YOLOv8m (820ms) Pi 5 benchmarks | HIGH | Either benchmark them or say "estimated from FLOP scaling" |
| SSD MobileNetV2 mAP of 0.88 | HIGH | Train it on your dataset or remove from MCDA. COCO mAP is irrelevant for single-class dummy detection |
| "300ms-per-frame budget" | MEDIUM | Derive it: at 5 m/s and 30m altitude, the FOV sweeps X m/frame, so you need Y FPS to guarantee overlap, therefore Z ms budget |
| "Training data requirement" MCDA criterion | MEDIUM | Remove or justify why YOLOv8n needs less data than YOLOv8s (it doesn't -- same architecture, different width) |
| "Criteria weights established before scoring" x4 | LOW | Show the method once (team ranking, requirement traceability matrix) instead of repeating the claim |
| Wind measurement source | LOW | Add "(Met Office station / anemometer app / RC transmitter readout)" |
| Random walk in search MCDA | LOW | Replace with a real candidate (sector search, creeping line) or justify its inclusion as a baseline |
| "Automation advantage ~20x" (line 176) | MEDIUM | Citation \cite{goodrich2008} -- verify this number applies to SAR aerial search, not HRI in general |

---

## 9. Actionable Recommendations (Priority Order)

1. **Fix or flag the MobileNet and YOLOv8s/m numbers.** Either run benchmarks or add "estimated" qualifiers. An examiner who checks will immediately distrust the entire MCDA.
2. **Derive the 300ms budget from first principles.** One sentence: "At 5 m/s search speed with 54.4 deg HFOV at 30m altitude, each frame covers X m of ground; 10% overlap requires Y FPS, yielding a Z ms budget."
3. **Add one figure.** Best candidate: a system architecture diagram showing Pi 5 -> MAVProxy -> Cube -> actuators, with the detection pipeline overlaid. This would support Hardware, Communication, and Software Architecture subsections simultaneously.
4. **Show weight derivation once.** A 3-line paragraph explaining the team ranked criteria by requirement traceability (R01-R12 mapping) is enough.
5. **Strengthen Political STEEPLE.** One sentence on the UK CAA's 2024 BVLOS consultation or the SORA pathway for future operational approval.
6. **Add a "team deliberation" decision-change.** Even one example where a team vote or discussion led to a direction change would strengthen the narrative beyond measurement-triggered corrections.

---

## Summary Verdict

The Design Rationale section is the strongest section for the Decision Making criterion. The MCDA tables provide structure, the STEEPLE is genuine, and the decisions-changed subsection is excellent. The main risk is an examiner probing the fabricated/unverified benchmark numbers in the model MCDA -- if those are challenged, the credibility of all five tables comes into question. Fix the evidence gaps and this section moves from 78 to 85+.

**For Decision Making (40% of D6): this section alone scores ~76-78.** The other sections (System Description, Requirements Verification, Evaluation) can add 5-10 points through additional evidence of adaptive decision-making, but the heavy lifting is done here.
