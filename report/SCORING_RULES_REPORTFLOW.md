# Scoring Rules -- D6 Reportflow (Concise Company Report)

---

## What We Want From This Report

**Purpose:** A concise, self-contained version of the D6 company report. Where the "Goldmine" is 151 pages with 32 appendices, the Reportflow is ~20 pages with the same 4 required body sections condensed. This is the version that respects the 15-page body limit strictly while still hitting every rubric criterion.

**Audience:** Same MSc markers as the Goldmine. The Reportflow is the version we would submit if forced to choose one. It must be readable in a single sitting and leave the marker convinced of High First quality.

**Page limit:** 15 pages body (same as D6 brief). Currently ~20 pages total including cover, exec summary, and references.

**Key content that MUST be present (same 4 body sections as D6):**
1. **Design Rationale** (~4 pages) -- STEEPLE analysis, MCDA tables, parameter derivation chain, autonomy justification, "Decisions That Changed"
2. **System Description** (~5 pages) -- architecture, CV pipeline, state machine, ground station, geofence, error budget, BOM
3. **Requirements Verification** (~3 pages) -- R01-R12 matrix with method + evidence + status, detection probability, landing probability
4. **Evaluation** (~3 pages) -- plus/delta, bug-cost table, progressive testing, lessons learned, what would change

**What makes it score 90+:**
- Everything in the Goldmine scoring rules PLUS:
- Tight writing with no padding -- every sentence earns its space
- Figures that replace paragraphs of text (worth more in a page-limited report)
- Smooth section transitions (not just topic dumps)
- Bibliography with real citations (currently ZERO -- major gap)

---

## Scoring Rubric (from AENGM0074 Appendix A)

Same rubric as D6 Goldmine -- identical criteria, identical bands, identical weightings:

### Specialist Skills and Problem-Solving (40%)
- **83+ requires:** "Confident and comprehensive identification of task and challenge aspects. Appropriate technologies and approaches selected and implemented highly effectively, showing initiative, autonomy, and creativity."
- In practice: Name every hard sub-problem. Justify every technology choice. Show initiative beyond requirements. Quantify performance.

### Decision Making (40%)
- **83+ requires:** "Shows confidence and creativity in adapting to changing and unfamiliar/challenging circumstances and making effective, evidence-based decisions."
- In practice: Problem -> Response -> Evidence -> Outcome for every adaptation. MCDA with sensitivity. Sequential measurement chain. Numbers, not adjectives.

### Communication (20%)
- **83+ requires:** "Reporting and presentation are effective, engaging, and professional, making use of innovative techniques and resources."
- In practice: Hardware photos, screenshots, real data plots. Professional LaTeX. Figures captioned and cross-referenced. Tight page budget means every figure must pull double duty.

---

## Priority Checklist (ordered by impact on score)

### Critical (must fix before submission):
- [ ] **Add bibliography** -- currently ZERO citations. This is a glaring omission. A professional engineering report without references cannot score above 72 on Communication. Need 15-25 references minimum: YOLOv8 paper, ArduPilot docs, MAVLink spec, STEEPLE framework, Sheridan autonomy levels, photogrammetry references, CAA regulations.
- [ ] **Hardware photograph** -- same as Goldmine, one annotated photo of the assembled system.
- [ ] **Ground station screenshot** -- same as Goldmine.
- [ ] **Detection examples** -- 2-3 subfigures with bounding boxes at different altitudes.

### High priority:
- [ ] **Section transitions** -- currently reads as 4 separate documents glued together. Add 1-2 sentence transitions between sections that show the narrative flow (design rationale -> these choices produced this system -> we verified it meets requirements -> here is the honest evaluation).
- [ ] **Conclusion** -- was missing in v1. Should be present: summarise key achievements, state limitations honestly, point to future work.
- [ ] **Cross-references to appendices** -- if the Goldmine appendices are submitted alongside, reference them (e.g., "see Appendix C for full detection envelope analysis").
- [ ] **MCDA sensitivity analysis** -- present in Goldmine, may need condensing for Reportflow.

### Nice to have:
- [ ] **Error budget table** -- from Goldmine system description.
- [ ] **Bug-cost table** -- from Goldmine evaluation (12 defects with counterfactual cost).
- [ ] **Detection probability calculation** -- correlation-aware N_eff from Goldmine requirements verification.

---

## Current Score and Gaps

**Current score: ~87.2/100** (High First band)
- Score estimated from previous session review
- Was 81.0 before adding all 4 D6 sections; jumped to 87.2 after structural completion

**What improved from 81 to 87:**
- Was optimization-only report (missing 3 of 4 required sections)
- Added STEEPLE, MCDA, system description, requirements verification, evaluation
- Section transitions added
- Conclusion added

**Critical gap: ZERO bibliography citations**
This is the single most damaging issue. The Goldmine has 30+ citations. The Reportflow has none. A report at this level without citations is a red flag for any academic marker. Every STEEPLE claim, every framework reference (Sheridan, MCDA), every technology choice needs at least one citation.

**Other gaps:**
1. No hardware photographs (same as Goldmine)
2. No ground station screenshot
3. No detection example images
4. Writing may be too condensed in places -- check readability
5. Unclear if MCDA sensitivity analysis is included (present in Goldmine v6)

**Estimated score breakdown:**
- Specialist Skills: ~87 (strong technical content carried from Goldmine)
- Decision Making: ~88 (strong MCDA, adaptation stories)
- Communication: ~85 (clean LaTeX, but no photos/screenshots, no bibliography)

**If bibliography added + photos/screenshots: estimated 89-90**

---

## Figures That Would Be Impressive

### Must have (essential for page-limited report):
- [ ] **System architecture diagram** -- replaces 2 pages of text description
- [ ] **State machine diagram** -- replaces state transition text
- [ ] **Requirements verification table** -- compact R01-R12 matrix
- [ ] **MCDA comparison table** -- at least companion computer selection
- [ ] **Hardware photo** -- annotated, replaces hardware description text

### Should have (strong impact):
- [ ] **Lawnmower pattern overlaid on search polygon** -- visual proof of coverage
- [ ] **CV pipeline flow diagram** -- frame -> resize -> inference -> NMS -> GPS
- [ ] **Detection examples** at 2-3 altitudes
- [ ] **Ground station screenshot**
- [ ] **Error budget table** (6 sources, RSS)

### Nice to have (if space permits):
- [ ] **GPS scatter plot** -- CEP50 = 2.3m visualised
- [ ] **MCDA sensitivity bar chart** -- visual version of perturbation analysis
- [ ] **Bug-cost table** -- 12 defects with counterfactual analysis
- [ ] **Progressive testing pyramid** -- 5-tier framework diagram
- [ ] **Plus/delta table** -- compact evaluation summary

### Key difference from Goldmine:
In the Reportflow, figures are MORE important because page budget is tighter. A good figure replaces a full paragraph. Prioritise diagrams that eliminate text over diagrams that supplement text.
