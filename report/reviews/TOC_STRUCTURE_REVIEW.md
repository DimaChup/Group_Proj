# TOC Structure Review — D6 Goldmine Report

**Date:** 2026-04-04
**Report:** `report/main.tex` (~206 pages, 35 appendices A–AI)
**Reviewer:** Claude Opus 4.6

---

## Overall Verdict

**The report structure is strong and professional.** The main body follows a clean, logical engineering-report flow. The Appendix Guide on a dedicated page is an excellent touch that few student reports include. Numbering is clean, no gaps exist, and the TOC reads impressively. Below are findings organized by severity.

---

## 1. Main Body Flow — EXCELLENT

The 15-page assessed body follows a textbook engineering report progression:

| Section | Pages | Verdict |
|---------|-------|---------|
| Executive Summary (unnumbered) | 1 | Correct placement, excluded from limit |
| Introduction (unnumbered) | 2 | Context, company, team — excluded from limit |
| 1. Design Rationale | ~6 | Why we made each choice |
| 2. System Description | ~7 | What we built |
| 3. Requirements Verification | ~1 | Did it meet R01–R12 |
| 4. Evaluation | ~2 | Plus/delta, lessons |
| References (unnumbered) | 2 | Two-column, excluded from limit |

**Flow is logical**: rationale → description → verification → evaluation. This is the standard V-model reporting order and reads professionally.

**No issues found in the main body structure.**

---

## 2. Appendix Organization — GOOD, with observations

### 2.1 Appendix Guide Categories

The Appendix Guide groups 35 appendices into 5 categories:

1. **Core system detail** (A–D): State table, config, training, safety
2. **Verification and validation** (E–G): Testing, field results, future work
3. **Subsystem deep dives** (H–U): 14 appendices covering inference, CV, GPS, streaming, comms, etc.
4. **Search and flight optimisation** (V–AF): 11 appendices on path/search optimization
5. **Extended body sections** (AG–AI): Requirements detail, evaluation detail, development methodology

**This grouping is logical and the Appendix Guide table is a professional touch.**

### 2.2 Observation: Optimization Appendix Cluster (V–AF) is Dense

Nine of the eleven appendices in the "Search and flight optimisation" category deal with overlapping optimization topics:

| App | Title | Core topic |
|-----|-------|------------|
| V | Flight Path Optimisation | Strategy comparison |
| Y | Multi-Objective Search Optimisation | Energy, rotation, coverage trade-offs |
| AA | Search Path Optimisation | 216-config sweep, strategy comparison |
| AB | Search Parameter Optimisation | Physics sim, Pareto front, sensitivity |
| AC | Multi-Objective Search Optimisation | Formal mathematical formulation |
| AD | Design Strategy: Parameter Derivation Chain | Logical dependency reasoning |
| AE | Vision Performance Analysis | Altitude/speed/detection envelope |
| AF | Decision Flow | Executive narrative of parameter selection |

**Assessment:** While there is thematic overlap, each appendix serves a distinct purpose — V is qualitative trade-offs, AA is the data, AB is the simulation, AC is the formal math, AD is the reasoning chain, AF is the narrative. This is actually a strength: it shows deep, multi-perspective analysis of a critical design decision. The Appendix Guide descriptions make the distinctions clear.

**Risk:** A marker skimming the TOC might initially think "why are there 9 optimization appendices?" but the Appendix Guide mitigates this. No structural change recommended — the content is distinct enough to justify separate appendices.

### 2.3 Observation: Appendix K (GPS Estimation) is 31 Pages

Appendix K spans pages 68–99 with 24 subsections (K.1–K.24). This is the longest single appendix by far. It covers:
- Mathematical foundations (K.2–K.7)
- Three-level estimation architecture (K.9)
- Fusion strategies and clustering (K.13–K.15)
- Empirical validation (K.16, K.21)
- Four-phase detection-to-landing flow (K.18)
- Multi-pass observation (K.23)
- Passive estimation (K.24)

**Assessment:** This is a comprehensive treatment of a critical subsystem. The depth is appropriate for a "deep dive" appendix. However, K.18 (Four-Phase Detection-to-Landing Flow) and K.19 (Cooperative Vision-Flight Architecture) are more operational/architectural than GPS estimation. They describe mission flow rather than estimation math.

**Recommendation (minor):** No action needed. K.18 and K.19 bridge GPS estimation with mission operations, which is a natural extension. Splitting would create orphan appendices.

### 2.4 Observation: H.5 (Video Streaming) Inside Edge Inference Appendix

Appendix H "Edge Inference Architecture" contains subsection H.5 "Video Streaming Architecture" (MJPEG protocol selection, alternatives). Meanwhile, Appendix J is entirely dedicated to "Video Streaming and Ground Station Architecture."

**Assessment:** This is a minor structural redundancy. H.5 is brief (~1 page) and frames streaming as a pipeline output concern, while J is a full 3-page deep dive. They serve slightly different purposes (H.5 = "how does the inference output reach the operator", J = "full streaming system design").

**Recommendation (minor):** Could add a forward-reference in H.5: "For a comprehensive treatment of the streaming architecture, see Appendix~J." This is cosmetic — not a structural defect.

### 2.5 Observation: Testing Overlap Between E and L

Appendix E "Testing Methodology" and Appendix L "Progressive Testing Methodology" cover related ground:
- E: V-model, five tiers, stress testing, team roles, expected outcomes
- L: Philosophy, five tiers in detail, defect discovery, V-model mapping, cost-risk gradient

**Assessment:** E is the "what and how" (methodology), L is the "why and philosophy" (deep dive). The Appendix Guide correctly places E under "Verification and validation" and L under "Subsystem deep dives." The overlap is intentional — E summarizes, L elaborates.

**Recommendation:** No change needed. The distinction is valid.

---

## 3. Numbering and Formatting — CLEAN

- **No gaps**: Sections 1–4, Appendices A–AI (continuous)
- **No weird nesting**: Maximum depth is 3 levels (e.g., K.18.8), which is appropriate
- **AlphAlph counter**: Correctly handles >26 appendices (AA, AB, ... AI)
- **Unnumbered sections**: Executive Summary, Introduction, References, Appendix Guide all use `\section*` with `\addcontentsline` — correct
- **Paragraph entries in TOC**: Some `\paragraph` entries appear in the TOC (e.g., "Mission objective.", "Why TFLite?"). This is unusual but not wrong — it adds granularity for a 206-page document

---

## 4. Page Jump: AD → AE (pages 164 → 187)

Appendix AD (Design Strategy) ends at page 164, but AE (Vision Performance) starts at page 187. This 23-page gap is caused by 7 full-width figures in design_strategy.tex (optimization_network, sensitivity_matrix, sensitivity_spider, coupling_matrix, altitude_speed_tradeoff, function_chain, tornado_sensitivity). LaTeX's float placement algorithm pushes these figures to dedicated float pages after the text.

**Assessment:** This is a LaTeX float behavior issue, not a structural problem. The TOC page numbers are correct. No action needed unless the author wants tighter figure placement (which risks worse page breaks).

---

## 5. Does It Look Like a Top-Grade Report?

**Yes.** Reading just the TOC conveys:

1. **Professional structure**: Clear separation of assessed body, references, and appendices
2. **Depth**: 35 appendices covering every aspect of the system
3. **Categorization**: The Appendix Guide groups appendices into logical clusters
4. **Technical sophistication**: Topics like Kalman filtering, Pareto optimization, multi-objective formulation, attitude-compensated GPS estimation signal graduate-level engineering work
5. **Completeness**: Requirements verification, evaluation, safety, testing, field results, future work — nothing is missing
6. **Self-awareness**: "Decisions That Changed" (Section 1.10) and "Lessons Learned" (AH.3) show reflective practice

**The TOC alone would give a marker confidence that this is a thorough, well-organized engineering report.**

---

## 6. Summary of Findings

| # | Finding | Severity | Action |
|---|---------|----------|--------|
| 1 | Main body flow is logical and professional | None | None needed |
| 2 | 9 optimization appendices (V–AF) overlap thematically | Minor | None — distinct purposes, Guide explains |
| 3 | Appendix K is 31 pages (longest single appendix) | Observation | None — depth justified for critical subsystem |
| 4 | H.5 streaming section inside inference appendix, while J is full streaming appendix | Minor | Could add cross-reference in H.5 |
| 5 | Testing overlap between E and L | Minor | None — E summarizes, L elaborates |
| 6 | Page jump AD→AE (23 pages of figures) | Cosmetic | LaTeX float behavior, not structural |
| 7 | Paragraph-level TOC entries | Style choice | Acceptable for 206-page document |
| 8 | Numbering clean, no gaps | None | None needed |

**No structural changes recommended.** The report structure is impressive and professional as-is.
