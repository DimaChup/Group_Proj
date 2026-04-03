# Narrative Coherence Review

**Sections reviewed (in order):**
1. `exec_summary.tex`
2. `intro_d6.tex`
3. `design_rationale.tex`
4. `decision_flow.tex`
5. `system_description.tex`
6. `requirements_verification.tex`
7. `evaluation.tex`

---

## 1. Does the exec summary accurately preview the report?

**Verdict: Yes, with minor gaps.**

The exec summary covers every major theme: mission objective, system architecture, key design decisions (modular codebase, dual-backend vision, simulation-first), quantitative results (mAP50=0.995, 206ms/4.8FPS, CEP50=2.3m), field day adaptation, and the honest "no outdoor flight" disclaimer. It reads as a self-contained one-pager that a reader could use to decide whether to read further.

**One gap:** The exec summary mentions "20 states and 32 transitions" but never mentions the 216-configuration parametric sweep, which is a significant analytical contribution featured prominently in the design rationale and decision flow. Consider adding a single clause about the parametric optimisation.

---

## 2. Does the intro set up the problem clearly?

**Verdict: Yes, very well.**

The intro opens with a concrete scenario (missing hiker in Fenswood Wilderness), introduces the hardware constraints (all teams get identical kit), lists the five task requirements clearly, and explains the compressed timeline. The company description, team roles, and report structure roadmap are all present and well-organised.

**Minor note:** The report structure paragraph (line 77-79) says "Sections \ref{sec:sysdesc}--\ref{sec:groundstation} provide the System Description" but the ground station is a subsection of system_description.tex, not a separate section. This is technically correct (LaTeX will resolve the refs) but might read oddly if the refs resolve to the same section number. Not a real issue.

---

## 3. Do sections flow logically?

**Verdict: Yes. The narrative arc is strong.**

The flow is: Problem setup (intro) -> Why we made these choices (design rationale) -> Detailed parameter derivation (decision flow) -> What we built (system description) -> Did it meet requirements (requirements verification) -> Honest assessment (evaluation).

This is a textbook engineering report structure. Each section builds on the previous one:
- Design rationale establishes *why* (STEEPLE, MCDA trade studies, autonomy level justification)
- Decision flow shows *how the numbers were derived* (altitude -> speed -> scan angle -> NFZ margin)
- System description shows *what was built* using those parameters
- Requirements verification maps the built system back to the brief
- Evaluation closes the loop with plus/delta and lessons learned

**One structural question:** The decision_flow.tex is labelled as an appendix (`\section{Decision Flow...}\label{app:decision-flow}`) but appears to be placed in the body flow between design_rationale and system_description. If it is actually an appendix, this review doesn't apply. If it is in the body, it works well as a "bridge" section that makes the parameter derivation accessible before diving into the technical system description. Clarify whether this is body or appendix -- the label says `app:` but the narrative placement suggests body.

---

## 4. Are there transitions between sections?

**Verdict: Mixed. Some transitions are strong, others are abrupt.**

**Strong transitions:**
- design_rationale.tex ends with "Every design decision in this project traces to a quantified rationale..." which sets up the decision flow nicely.
- system_description.tex ends with a "Section summary" paragraph that recaps key numbers, providing closure.
- evaluation.tex opens by naming its four evidence sources, clearly framing what follows.

**Weak transitions:**
- The jump from intro to design_rationale has no bridging text. The intro ends with a report structure paragraph, then the next section just starts with STEEPLE. This is fine for an academic report but could benefit from a one-sentence opening that says "Before describing the system, we present the rationale that guided its design."
- The jump from decision_flow to system_description is abrupt. Decision flow ends with qualitative choices (lawnmower vs spiral, operator-in-the-loop, single-class detector) then system_description begins with a dense opening paragraph. A transitional sentence would help.

---

## 5. Is there a consistent voice?

**Verdict: Mostly yes, with one notable shift.**

The report maintains a consistent formal-but-readable academic voice throughout. First-person plural ("we") is used appropriately. Technical terms are introduced with definitions on first use. The writing is confident without being boastful.

**The one shift:** The decision_flow.tex has a markedly more accessible, "executive briefing" tone compared to the rest of the report. Phrases like "A hiker is missing. The drone has one battery..." and "No single configuration maximises all five simultaneously" read more like a technical blog post. This is not necessarily bad -- it makes the optimisation story very readable -- but it does feel different from the formal tone of design_rationale.tex and system_description.tex. If decision_flow is an appendix, this contrast is fine (appendices can have different register). If it is a body section, consider whether the tonal shift is intentional.

---

## 6. Does the evaluation reference back to the design rationale?

**Verdict: Yes, extensively. This is a strength of the report.**

Specific callbacks:
- Evaluation P1 (dual-backend CV architecture) directly references the design rationale's "dual inference backend" principle
- Evaluation P5 (modular vision interface) references the design rationale's "modular separation" principle
- Evaluation D5 (train/val overlap) references the 366-image dataset described in design_rationale model selection
- Evaluation D6 (single-class detector) explicitly connects to the design rationale's "single-class detector" non-quantifiable choice
- The "Decisions That Changed" subsection in design_rationale (focal length, camera resolution, TFLite runtime, pyserial) is directly reflected in the bug discovery table in evaluation (Table bug-cost)
- The weather cancellation story is told consistently in both design_rationale (Section 9, "Field Day Adaptation Under Uncertainty") and evaluation ("Weather cancellation as information-maximisation, not failure")

The loop is closed well.

---

## 7. Are key metrics consistent across sections?

**Verdict: Mostly consistent, with several inconsistencies found.**

### Consistent metrics (verified across all sections):
- mAP50 = 0.995 (exec_summary, decision_flow, system_description, requirements_verification, evaluation)
- 206.5ms / 4.8 FPS inference (exec_summary, decision_flow, system_description, requirements_verification, evaluation)
- CEP50 = 2.3m (exec_summary, system_description, requirements_verification, evaluation)
- Maximum error = 16.5m (system_description line 186, evaluation line 112)
- Lens calibration RMS = 0.399 (exec_summary, system_description, evaluation)
- Focal length = 5.46mm (system_description line 41, design_rationale line 246, requirements_verification line 137)
- 366 images (300 syn + 16 real + 50 neg) -- consistent everywhere
- 50/50 detection at 0.966 mean confidence -- consistent everywhere
- 20 states, 32 transitions -- consistent everywhere
- 30m NFZ buffer -- consistent everywhere
- 7.5m landing offset -- consistent everywhere
- 120s verify timeout -- consistent everywhere

### INCONSISTENCIES FOUND:

**INC-1: HFOV value differs between sections**
- `system_description.tex` line 41: "HFOV of approximately 49.3 degrees (Pi IMX296 camera)"
- `requirements_verification.tex` line 70: "calibrated HFOV (49.4 degrees, Pi IMX296 camera)"
- `decision_flow.tex` does not state HFOV explicitly for the Pi camera
- `CLAUDE.md` / memory files reference "54.4 deg HFOV" but this is for the DJI cropped video, not the Pi camera, so that is a different measurement and not an inconsistency

These are close (49.3 vs 49.4) but should be one number. Pick one and use it everywhere.

**INC-2: Number of test scripts differs**
- `exec_summary.tex` line 12: "58 test scripts"
- `system_description.tex` line 46: "58 test and calibration scripts"
- `evaluation.tex` line 31 (P7): "71 test scripts across 6 categories"
- `evaluation.tex` line 115: "71 test scripts across six categories"
- `evaluation.tex` line 211: "All 71 test scripts are run manually"

This is a real inconsistency: 58 vs 71. Either the count grew during writing, or the evaluation counts unit tests that the exec summary does not. Reconcile to a single number with a clear definition of what counts.

**INC-3: Number of frames per flyover differs**
- `decision_flow.tex` line 57: "14 frames per flyover" (at 8m/s, 4.8FPS)
- `system_description.tex` line 119: "11--17 detection opportunities per target"
- `requirements_verification.tex` lines 73-74: "approximately 19 frames in which the target is visible"

The decision_flow computes 14 frames from along-track footprint (24m); system_description says 11-17; requirements_verification computes 19 from cross-track footprint (32.2m). These are measuring different things (along-track vs cross-track footprint), but since all three are presented as "frames during a single flyover" without qualification, a reader would see three different numbers. The requirements_verification section then addresses this by computing N_eff ~= 1.0, which is good -- but the headline "19 frames" contradicts the decision_flow's "14 frames". Add a note clarifying which footprint dimension is being used in each calculation.

**INC-4: Detection probability differs**
- `decision_flow.tex` line 84: "Pd > 99.97%" (from 14 frames x 95% per-frame)
- `design_rationale.tex` line 64: "Pd > 99.97%" (same)
- `requirements_verification.tex` lines 76-77: Per-pass detection probability = 95% (after accounting for frame overlap correlation)

The decision_flow assumes 14 independent frames and gets 99.97%. The requirements_verification correctly accounts for inter-frame correlation and gets 95% per pass (99.75% two-pass). These are not contradictory -- they use different independence assumptions -- but the report presents both without clearly reconciling them. A reader might wonder why the exec summary's implied near-certainty doesn't match the requirements section's 95%. The requirements_verification analysis is more rigorous; consider updating the decision_flow to acknowledge the correlation or cross-reference the requirements section.

**INC-5: Geofence layer count**
- `exec_summary.tex` line 3: "four-layer automatic geofence"
- `design_rationale.tex` line 22: "three-layer geofence" (speed capping, repulsive potential field, hard-boundary cutoff) with firmware as a "fourth independent layer"
- `system_description.tex` line 90: "three nested protection layers" (Figure reference)
- `requirements_verification.tex` lines 40-52: "Four independent protection layers" (plan-time filtering, speed scalar field, repulsive vector field, hard cutoff) plus firmware as fifth

The count varies between 3 and 4 depending on whether plan-time filtering is counted as a layer and whether firmware geofence is counted. system_description says "three" but requirements_verification says "four" software layers plus a firmware fifth layer. The exec summary says "four-layer automatic geofence." Reconcile: define clearly which layers are counted, use one number consistently.

**INC-6: Confidence threshold**
- `system_description.tex` line 106: "confidence filtering (threshold 0.2)"
- `requirements_verification.tex` line 72: "CONFIDENCE_THRESHOLD = 0.2"
- `evaluation.tex` line 45 (D4): "detection threshold of 0.2"
- `exec_summary.tex`: does not mention threshold
- `design_rationale.tex` line 71: "operational threshold of 0.2"
- `CLAUDE.md`: "Confidence threshold: 0.4 (in vision.py)"

The report is internally consistent at 0.2, but CLAUDE.md says 0.4. This may mean the code was changed but CLAUDE.md was not updated, or vice versa. Not a report inconsistency per se, but worth checking that the deployed code matches the report's claim of 0.2.

**INC-7: Along-track footprint**
- `decision_flow.tex` line 56: "24m strip of ground along the flight direction"
- `design_rationale.tex` line 77: "along-track camera footprint is 24.0m"
- `system_description.tex` line 135: Does not state along-track explicitly, only cross-track (32.2m)

These are consistent where stated, but the along-track vs cross-track distinction is never explicitly defined. The along-track footprint (24m) comes from the image height dimension (1088px), while the cross-track (32.2m) comes from image width (1456px). A single sentence defining this would prevent confusion.

**INC-8: Wind speed at cancellation**
- `design_rationale.tex` line 283: "sustained winds exceeding the EDU-450's 10 m/s operational limit (measured 12 m/s, gusts to 18 m/s)"
- `exec_summary.tex` line 18: "sustained high winds exceeding safe flight limits"
- `evaluation.tex` line 157: "sustained winds exceeding 25 kn" and "the EDU-450's 15 kn safe limit"

12 m/s = 23.3 kn, not 25 kn. And design_rationale says the limit is 10 m/s (19.4 kn), while evaluation says 15 kn (7.7 m/s). These are contradictory. Pick one wind speed limit and one measured wind speed, and use them consistently.

---

## 8. Is the weather cancellation / field day story told consistently?

**Verdict: Mostly consistent, with the wind speed discrepancy noted above (INC-8).**

The narrative arc is consistent across sections:
- Scheduled flight day -> adverse weather -> cancelled -> pivoted to bench testing
- Four activities performed: FOV calibration, lens distortion mapping, inference benchmarking, DJI video analysis pipeline
- Results fed back into the vision pipeline

The framing is also consistent: not presented as failure, but as "information-maximising" adaptation. The evaluation section handles this particularly well with the explicit statement "A successful flight would have validated end-to-end operation but would likely not have produced the same depth of per-subsystem characterisation."

The only issue is the wind speed numbers (INC-8 above).

---

## Summary of Actionable Items

### Must Fix (numerical inconsistencies that would undermine credibility):

| ID | Issue | Files | Action |
|----|-------|-------|--------|
| INC-2 | Test script count: 58 vs 71 | exec_summary:12, system_description:46 vs evaluation:31,115,211 | Pick one number, define what counts |
| INC-4 | Detection probability: 99.97% vs 95% per pass | decision_flow:84 vs requirements_verification:76-77 | Cross-reference or reconcile assumptions |
| INC-5 | Geofence layer count: 3 vs 4 vs 5 | exec_summary:3, design_rationale:22, system_description:90, requirements_verification:40-52 | Define layers clearly, use one count |
| INC-8 | Wind speed: 10m/s vs 15kn limit; 12m/s vs 25kn measured | design_rationale:283 vs evaluation:157 | Use one set of numbers |

### Should Fix (minor but noticeable):

| ID | Issue | Files | Action |
|----|-------|-------|--------|
| INC-1 | HFOV: 49.3 vs 49.4 degrees | system_description:41 vs requirements_verification:70 | Pick one |
| INC-3 | Frames per flyover: 14 vs 19 | decision_flow:57 vs requirements_verification:73-74 | Clarify along-track vs cross-track |
| INC-6 | Confidence threshold: report says 0.2, CLAUDE.md says 0.4 | Multiple report files vs CLAUDE.md | Verify code matches report |

### Nice to Have (narrative polish):

- Add a transitional sentence at the start of design_rationale connecting it to the intro
- Consider whether decision_flow's informal tone is intentional (fine if it is an appendix)
- Define along-track vs cross-track footprint on first use

---

## Overall Assessment

**The report tells a coherent, well-structured story.** The narrative arc from problem definition through design rationale, system description, requirements verification, and honest evaluation is logical and complete. The evaluation section is notably strong -- it closes the loop on design decisions, acknowledges limitations honestly, and frames the weather cancellation constructively rather than defensively. The key metrics are mostly consistent, with the exceptions noted above. Fixing the 6-8 inconsistencies listed would bring the report to a very high standard of internal coherence.

The strongest aspect of the narrative is how the evaluation references back to the design rationale and the "decisions that changed" subsection. This creates a compelling evidence-based engineering story where initial assumptions are stated, tested, and corrected -- exactly what an examiner wants to see.
