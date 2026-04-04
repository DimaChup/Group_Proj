# Body Page Check (15-Page Limit)

Compiled: 2026-04-04 from `report/main.tex` (244 pages total, pdflatex + biber, 3 passes).

## Current Page Counts

| Section | Start Page | End Page | Actual Pages | Target Pages | Over/Under |
|---------|-----------|----------|-------------|-------------|------------|
| Design Rationale | 16 | 24 | **9** | ~6 | **+3 over** |
| System Description | 25 | 33 | **9** | ~5 | **+4 over** |
| Requirements Verification | 34 | 34 | **1** | ~2 | -1 under |
| Evaluation | 35 | 42 | **8** | ~2 | **+6 over** |
| **TOTAL BODY** | **16** | **42** | **27** | **15** | **+12 over** |

The body is **27 pages -- nearly double the 15-page limit.** 12 pages must be cut.

## Content Inventory

| Section | Lines | Figures | Tables | Key Content |
|---------|-------|---------|--------|-------------|
| design_rationale.tex | 306 | 3 | 6 | STEEPLE, search param optimisation, parameter chain, HW selection, 4 MCDA trade studies, SW arch rationale, model selection, coverage planning, FSM rationale, autonomy justification, 7 evidence-based corrections, ROS rationale, camera rationale, field day adaptation |
| system_description.tex | 241 | 12 | 2 | HW BOM, SW architecture, geofence (5 layers), CV pipeline, search pattern, state machine (20 states), target localisation, ground station, simulation framework |
| requirements_verification.tex | 34 | 0 | 1 | R01-R12 table + 2 paragraphs |
| evaluation.tex | 272 | 6 | 5 | Plus/delta (P1-P10, D1-D9), discussion, SAR comparison, design choice evaluation, mission metrics, future work, testing framework, closing assessment |

## What to Move to Appendices (by section, largest savings first)

### Design Rationale (9 pages -> target 6, need to cut ~3 pages)

1. **Four MCDA trade study tables (Tables 3-6)** -- ~2.5 pages. These are detailed scoring matrices for companion computer, communication architecture, model selection, and search pattern. Keep the *conclusion* (1 sentence each: "Pi 5 selected because..."), move the full tables to an appendix. The MCDA heatmap figure (Fig 4) can also move.

2. **Seven "Decisions That Changed" paragraphs** (Sec 1.11) -- ~1.5 pages. This is valuable but detailed evidence that works better as an appendix. Keep a 3-line summary table (decision, old value, new value, impact) in the body; move the narratives to an appendix.

3. **"Why Not ROS" subsection** (Sec 1.12) -- ~0.5 page. Already a design rationale detail. Merge into the communication MCDA appendix or a "Rejected Alternatives" appendix.

4. **Camera selection subsection** (Sec 1.14) -- ~0.3 page. The rolling shutter argument is strong but brief; could be folded into the HW platform paragraph.

5. **Companion computer trade study text** around Table 3 -- the post-table sensitivity analysis paragraph can move to appendix.

**Estimated saving: 3-4 pages** (move MCDA tables, compress Decisions That Changed, drop ROS subsection)

### System Description (9 pages -> target 5, need to cut ~4 pages)

1. **Geofence enforcement paragraph + Figure 7** -- ~1.5 pages. The five-layer geofence description is very detailed. Keep 3 sentences summarising the approach; move the layer-by-layer description and the 4-panel figure to Appendix (already has Appendix Y for repulsive field). 

2. **State machine detail (Sec 2.5)** -- ~1.5 pages with two large figures. Keep ONE state machine figure (the auto-generated one is clearer). Move the hand-drawn overview OR the auto-generated diagram to appendix. The 6-item safety mechanisms enumeration can be compressed to a 3-row table.

3. **Target localisation equations and detail (Sec 2.6)** -- ~1 page. The GSD equation, fusion bullet points, and error budget discussion overlap heavily with Appendix K (GPS estimation deep dive). Keep the CEP50=2.3m result and the subfigure; move the equation derivation and error source breakdown to the appendix.

4. **Simulation framework (Sec 2.8)** -- ~0.5 page. Four simulation levels are described in full; compress to a 4-row table (level, tool, what it tests) and move the narrative to Appendix Q (simulation validation).

5. **MAVLink commands table (Table 8)** -- ~0.3 page. Six-row reference table that adds little to the narrative. Move to appendix.

**Estimated saving: 4-5 pages** (compress geofence, drop one state machine fig, move localisation equations, compress simulation)

### Requirements Verification (1 page -- under target, leave as-is)

This section is already lean. Could absorb 0.5 page more prose if needed for flow.

### Evaluation (8 pages -> target 2, need to cut ~6 pages)

This is the most over-target section.

1. **Plus tables (P1-P10 and D1-D9)** -- ~3 pages. Two large tables dominate this section. Options:
   - Keep only the top 5 plus and top 5 delta items in the body. Move the rest to appendix.
   - OR condense into a single compact table with 1-line entries (no "Evidence/Detail" column), and reference the appendix for full evidence.

2. **"Evaluation of Design Choices" subsection** (Sec 4.4) -- ~1.5 pages. Five alternative-analysis paragraphs (Pi vs Jetson, Python vs ROS, lawnmower vs adaptive, single vs multi-class, simulation-first assessment). This overlaps with Design Rationale (which already justifies each choice). Move entirely to appendix or merge into the "Decisions That Changed" appendix.

3. **SAR Comparison table + radar chart** (Sec 4.3) -- ~1 page. The comparison is valuable context but the radar chart is the most space-efficient way to show it. Keep the radar chart; move the table and the 4-observation discussion paragraph to appendix.

4. **Mission-Level Performance Estimates table** (Sec 4.5) -- ~0.5 page. Useful summary but could be merged into the closing assessment paragraph.

5. **Prioritised Future Work** (Sec 4.6) -- ~0.5 page. A 7-item numbered list. Compress to a 3-item summary (fly, collect data, deploy NCNN); move the full list to the Future Work appendix (Appendix G).

6. **Testing Framework Summary table** (Sec 4.7) -- ~0.3 page. Already covered in System Description and has a full appendix (Appendix E). Remove from evaluation or keep as a 2-line reference.

**Estimated saving: 6-7 pages** (compress plus/delta, remove design-choice overlap, move SAR table, compress future work)

## Recommended Cut Plan (12 pages to remove)

| Action | Section | Pages Saved | Priority |
|--------|---------|-------------|----------|
| Move 4 MCDA tables + heatmap to appendix, keep 1-sentence verdicts | Design Rationale | 2.5 | HIGH |
| Compress "Decisions That Changed" to summary table | Design Rationale | 1.0 | HIGH |
| Drop "Why Not ROS" subsection (covered by MCDA) | Design Rationale | 0.5 | MEDIUM |
| Compress geofence to 3 sentences, move figure to appendix | System Description | 1.5 | HIGH |
| Remove one state machine figure (keep auto-generated) | System Description | 0.5 | MEDIUM |
| Move localisation equations to Appendix K, keep result | System Description | 0.8 | HIGH |
| Compress simulation to 4-row table | System Description | 0.5 | MEDIUM |
| Condense plus/delta to top-5 each, 1-line entries | Evaluation | 2.5 | HIGH |
| Remove "Design Choices" subsection (overlaps Design Rationale) | Evaluation | 1.5 | HIGH |
| Move SAR comparison table to appendix, keep radar chart | Evaluation | 0.5 | MEDIUM |
| Compress future work to 3 items | Evaluation | 0.3 | LOW |
| Remove testing framework table (exists in System Description) | Evaluation | 0.3 | LOW |
| **TOTAL** | | **~12.4** | |

## Key Principle

The body must carry the *argument*, not the *evidence*. Every MCDA table, every equation derivation, every detailed narrative is evidence -- that is what appendices are for. The body should state the decision, the reason (1-2 sentences), and point to the appendix for proof.

## Risk: Removing Content That Carries Marks

The design rationale MCDA tables demonstrate "specialist knowledge" and "evidence-based decision making". Removing them entirely would lose marks. The solution is to keep the *conclusion* in the body ("Pi 5 was selected via weighted MCDA scoring 4.90/5.00, see Appendix X") and the full table in the appendix. Assessors who want detail will check the appendix; the body argument is unbroken.

Similarly, the 7 "Decisions That Changed" entries demonstrate "reflective practice" and "evidence-based correction". A body summary table (3 columns, 7 rows) preserves this signal in ~0.3 pages instead of 1.5.

## After Cuts: Projected Page Counts

| Section | Current | After Cuts | Target |
|---------|---------|-----------|--------|
| Design Rationale | 9 | ~5 | 6 |
| System Description | 9 | ~6 | 5 |
| Requirements Verification | 1 | ~1-2 | 2 |
| Evaluation | 8 | ~3 | 2 |
| **TOTAL** | **27** | **~15-16** | **15** |

System Description may still be ~1 page over after cuts. If so, the MAVLink commands table and the ground station paragraph are the next candidates to compress (the ground station has very little to prove at the design level -- it is an implementation detail).
