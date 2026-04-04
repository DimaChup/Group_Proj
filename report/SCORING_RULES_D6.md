# Scoring Rules -- D6 Group Company Report ("Goldmine")

---

## What We Want From This Report

**Purpose:** Group company report documenting the design, implementation, and evaluation of an autonomous SAR drone system. This is the technical portfolio -- it must prove the team can identify complex problems, make evidence-based decisions, and communicate engineering work professionally.

**Audience:** MSc markers (academics), likely 1-2 examiners. They will skim before reading. Exec summary, figures, and tables get read first. Body text gets read second. Appendices get read only if referenced from the body.

**Page limit:** 15 pages body (excluding cover, exec summary, introduction, references, appendices). Appendices are NOT assessed but can be referenced.

**Key content that MUST be present:**
1. STEEPLE analysis (brief explicitly requires it)
2. MCDA trade-off tables with sensitivity analysis
3. System description with flow charts, schematics, images
4. Requirements verification matrix (R01-R12) with method + evidence + status
5. Evaluation (plus/delta of TECHNICAL performance only -- NOT teamwork)
6. Executive summary that stands alone
7. Introduction with team bios, roles, member contributions
8. AI usage declaration (Category 2: Minimal for reporting)
9. GitHub repository link (R12)

**What makes it score 90+:**
- Outdoor flight data with detection logs (currently blocked)
- Independent held-out test set with credible mAP
- Precision-recall curve with formal threshold selection
- Hardware photographs annotated with component labels
- Ground station screenshots showing live operation
- Detection example images at multiple altitudes
- Comparison to 2+ commercial/academic SAR systems
- Every claim backed by a number, not an adjective

---

## Scoring Rubric (from AENGM0074 Appendix A)

### Specialist Skills and Problem-Solving (40%)

| Band | Marks | What It Means in Practice |
|------|-------|---------------------------|
| 2:1 (62-68) | "effectively" | Identified key problems. Selected appropriate tech. Implemented it and it works. |
| First (72-78) | + "initiative and autonomy" | Did things not asked for (simulator, video analysis, web GCS, 71 test scripts, synthetic dataset). Worked independently. |
| High First (83-100) | + "confident, comprehensive, highly effectively, creativity" | Named EVERY hard sub-problem. Justified EVERY technology choice with rejected alternatives. Non-obvious solutions (config auto-detect, BGR discovery, inverse-variance GPS). Quantified everything. |

**The 83+ differentiator:** "Confident and comprehensive identification" means you do not just solve problems -- you enumerate them exhaustively. "Creativity" means non-obvious solutions that a generic team would not have done.

### Decision Making (40%)

| Band | Marks | What It Means in Practice |
|------|-------|---------------------------|
| 2:1 (62-68) | "confident, evidence-based" | Decisions backed by data, not guesses. |
| First (72-78) | + "effective" | Decisions that actually worked. Adapted when circumstances changed. |
| High First (83-100) | + "creativity" | Every adaptation follows Problem -> Response -> Evidence -> Outcome. MCDA with sensitivity analysis. Sequential measurement chains. "Decisions That Changed" section showing measurement -> correction. |

**The 83+ differentiator:** "Creativity in adapting" means you did not just react -- you found non-obvious adaptations (weather cancelled flight -> DJI video analysis pipeline, Python 3.13 broke tflite -> ai-edge-litert, camera BGR despite RGB888 label -> tested all 6 permutations).

### Communication (20%)

| Band | Marks | What It Means in Practice |
|------|-------|---------------------------|
| 2:1 AND First (62-78) | "effective, appropriate techniques" | Professional LaTeX, proper figures and tables, cross-references. IDENTICAL wording for both bands. |
| High First (83-100) | + "engaging, professional, innovative" | Hardware photos, screenshots, annotated diagrams, real data plots. Not just competent -- visually compelling. |

**The 83+ differentiator:** There is a binary jump. 62-78 is "appropriate." 83+ requires "engaging, professional, innovative." This means visual content that makes the reader want to keep reading -- real photos, live screenshots, detection examples. Text-only reports cap at 78.

---

## Priority Checklist (ordered by impact on score)

### Quick wins (30 min each, +2-4 marks total):
- [ ] **Hardware photograph** -- one annotated photo of assembled drone with Pi, camera, Cube labelled. Phone photo is fine. This is the #1 recommendation since v4. Impact: +2-3 on Communication.
- [ ] **Ground station screenshot** -- run pi_flight.py in simulation, screenshot the browser dashboard. Impact: +1 on Communication.
- [ ] **Detection example images** -- three subfigures with YOLOv8n bounding boxes at 15m, 30m, 50m from video_test.py output. Impact: +1 Communication, +0.5 Specialist.
- [ ] **Confusion matrix in body** -- already exists as PNG in cv_models/sar_v2_1088/. Standard ML reporting. Impact: +0.5 Communication, +0.5 Specialist.
- [ ] **Clarify "preliminary measurements"** in decision_flow envelope tables -- one sentence specifying data source. Impact: +1 Decision Making.

### Medium effort (1-2 hours each):
- [ ] **Promote key decision_flow tables** into body (top-3 configs, final config) -- strongest decision-making evidence is currently in appendix.
- [ ] **8-step parameter chain as flowchart** -- currently wall of text, convert to numbered diagram.
- [ ] **Comparison to 1-2 commercial SAR systems** with structured table.
- [ ] **Precision-recall curve** with threshold selection rationale.

### Blocked / high effort:
- [ ] **Outdoor flight data** -- even one pass with detection logs would push Specialist to 90+. Weather/scheduling dependent.
- [ ] **Independent test set** -- 50+ labelled frames from separate flight for credible held-out mAP.
- [ ] **Payload release integrated into state machine** (D8).

---

## Current Score and Gaps

**Current score: 85.2/100** (High First band, solidly in 83-89)
- Specialist Skills: 86/100
- Decision Making: 87/100
- Communication: 80/100

**Scoring trajectory:**
| Version | Specialist | Decision | Communication | Total |
|---------|-----------|----------|---------------|-------|
| v4 | 82 | 80 | 78 | 80.4 |
| v5 | 85 | 85 | 80 | 84.0 |
| v6 | 86 | 87 | 80 | 85.2 |

**Communication is the bottleneck.** Specialist and Decision Making are strong (86-87). Communication is stuck at 80 because there are zero hardware photos, zero screenshots, and zero detection example images in the body.

**Gaps preventing 88+:**
1. No hardware photographs (mentioned since v4, still missing)
2. No ground station screenshot
3. No detection examples at multiple altitudes
4. No precision-recall curve
5. No outdoor flight data (structural constraint)
6. "Preliminary measurements" in envelope tables still vague
7. No comparison to commercial/academic SAR systems

**Gaps preventing 90+:**
- Outdoor flight data (cannot be manufactured)
- Independent held-out test set
- All of the 88+ gaps above

**Hard ceiling without outdoor flight: ~87-88**

---

## Figures That Would Be Impressive

### Already exist (just need including):
- [x] State machine diagram (20 states, 32 transitions) -- in body
- [x] System architecture block diagram -- in body
- [x] Lawnmower pattern with polygon overlay -- in body
- [x] GPS scatter plots -- in body
- [x] MCDA sensitivity analysis plots -- in body
- [ ] Confusion matrix -- exists as PNG in cv_models/, not in body
- [ ] Training curves -- exists in cv_models/, not in body

### Need creating (30 min each):
- [ ] **Annotated hardware photo** -- drone on bench with Pi, camera, GPS, Cube labelled
- [ ] **Ground station screenshot** -- browser dashboard showing MJPEG stream + GPS grid + buttons
- [ ] **Detection examples triptych** -- bounding boxes at 15m, 30m, 50m from DJI video
- [ ] **CV pipeline block diagram** -- replace \fbox placeholder in 04_computer_vision.tex
- [ ] **8-step parameter derivation flowchart** -- currently text wall
- [ ] **Latency breakdown bar chart** -- data exists in timing table
- [ ] **Error budget waterfall chart** -- 6 sources with RSS, currently table only

### Would be impressive but high effort:
- [ ] **Detection heatmap** overlaid on search polygon (altitude vs position vs confidence)
- [ ] **Precision-recall curve** at the operating threshold
- [ ] **Battery budget Sankey diagram** (search vs hover vs CV vs comms)
- [ ] **Side-by-side simulation vs DJI video** detection comparison
- [ ] **Flight path + detection timeline** from SITL logs
