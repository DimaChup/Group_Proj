# Appendix Flow Review

## Overview

35 appendices (A through AI), spanning approximately 100+ pages. Organised into five thematic groups in the Appendix Guide. This review assesses purpose, redundancy, body-text referencing, ordering, and merge/removal candidates.

---

## 1. Does Each Appendix Have a Clear Purpose?

All 35 appendices have stated purposes. However, several are unclear about what they add *beyond* other appendices:

| App | File | Purpose Clarity | Issue |
|-----|------|-----------------|-------|
| A | A1_state_table | Clear | Authoritative state reference |
| B | A2_config_params | Clear | Parameter table for reproducibility |
| C | 12_model_training | Clear | Full training pipeline detail |
| D | 13_safety_risk | Clear | Safety architecture + risk register |
| E | 10_testing | Clear | Five-tier framework + stress tests |
| F | 11_field_results | Clear | Bench + DJI video results |
| G | 14_future_work | Clear | Roadmap |
| H | inference_architecture | Clear | Backend selection rationale |
| I | cv_extended | Clear | Extended CV benchmarks + pipeline |
| J | streaming_architecture | Clear | MJPEG protocol decision |
| K | gps_estimation_deep | Clear | GPS math deep dive |
| L | testing_deep | **Redundant** | Repeats E (testing) with more detail |
| M | field_day_narrative | Clear | Narrative + lessons learned |
| N | contingency | Clear | Three-tier deliverables + fallbacks |
| O | test_scripts_guide | **Redundant** | Catalogues same scripts as E and L |
| P | calibration_deep | Clear | FOV, lens, colour calibration |
| Q | simulation_validation | Clear | Sim-to-real gap analysis |
| R | mission_flow | Clear | End-to-end flight narrative |
| S | centering_analysis | Clear | Landing strategy trade-off |
| T | comms_architecture | Clear | MAVLink topology + failsafes |
| U | pipeline_fps | **Overlaps H** | Raw vs effective FPS (H already covers this) |
| V | path_tradeoffs | **Overlaps AA** | Search parameter trade-offs |
| W | payload_release | Clear | Servo mechanism + offset rationale |
| X | model_comparison | **Overlaps C** | Model generations (C already covers results) |
| Y | search_optimization | **SUPERSEDED** | File header says "SUPERSEDED by AA" |
| Z | focus_and_repulsive | Clear | PLB redirect + NFZ repulsive field |
| AA | path_optimization_definitive | Clear | Definitive 216-config sweep |
| AB | optimization_master | **Overlaps AA, AC** | Physics sim + Pareto (shares content with AA) |
| AC | optimization_formal | **Overlaps AA, AB** | Formal math statement (same problem) |
| AD | design_strategy | Clear | Step-by-step parameter derivation |
| AE | vision_performance | Clear | Altitude/pixel/blur envelope |
| AF | decision_flow | **Overlaps AD** | Executive narrative of parameter selection |
| AG | requirements_detail | Clear | R01-R12 evidence narratives |
| AH | evaluation_detail | Clear | Defect register + lessons |
| AI | development_methodology | Clear | Dev philosophy + timeline |

---

## 2. Redundancy Analysis

### Critical Redundancy Clusters

**Cluster 1: Testing (E, L, O)**
- **E** (10_testing.tex): Five-tier framework, stress tests, DJI analysis, preflight checklist
- **L** (testing_deep.tex): Five-tier framework (repeated), defect discovery, V-model mapping, cost-risk gradient
- **O** (test_scripts_guide.tex): Complete script catalogue with tables

E and L both describe the same five-tier framework, the same defect table, and the same V-model mapping. L adds cost-risk gradient and experiment script detail. O catalogues every script -- useful but duplicates the script listing in E. 

**Recommendation**: Merge L into E (add cost-risk gradient and defect discovery tables). Merge O's script catalogue tables into E as subsections. This eliminates 2 appendices and ~15 pages of repeated content.

**Cluster 2: Search Optimisation (V, Y, AA, AB, AC, AD, AF)**
Seven appendices cover search parameter optimisation. This is the worst redundancy in the report.
- **Y** (search_optimization.tex): File header literally says "SUPERSEDED by AA". Still included.
- **V** (path_tradeoffs.tex): Trade-off analysis (diagonal vs axis-aligned, lane width vs altitude)
- **AA** (path_optimization_definitive.tex): 216-config sweep, energy model, strategy comparison
- **AB** (optimization_master.tex): Physics sim, Pareto analysis, sensitivity -- shares content with AA
- **AC** (optimization_formal.tex): Formal mathematical problem statement -- same 5 objectives as AA/AB
- **AD** (design_strategy.tex): Step-by-step parameter derivation chain
- **AF** (decision_flow.tex): Executive narrative of parameter selection

The same 5-objective problem statement appears in Y, AA, AB, and AC. The same decision vector equation appears in AB and AC. The same 216-config sweep is referenced in V, Y, AA, and AB. The same coupling matrix appears in the body and AD.

**Recommendation**: 
- **Remove Y entirely** (self-declared superseded)
- **Merge V into AA** (V's trade-off subsections fit naturally into AA's analysis)
- **Merge AC into AB** (formal statement belongs in the master optimisation appendix)
- **Keep AD and AF** (they serve distinct purposes: derivation chain vs executive narrative)
- Result: 7 appendices reduced to 3 (AA, AD, AF) -- saves ~12 pages

**Cluster 3: CV/Inference (H, I, U, X)**
- **H** (inference_architecture.tex): Backend comparison, quantisation, pipeline, streaming section
- **I** (cv_extended.tex): Pipeline timing, benchmarks, detection probability, dual backend
- **U** (pipeline_fps.tex): Raw vs effective FPS -- a subset of what H and I cover
- **X** (model_comparison.tex): Three model generations, COCO fallback, tiling

H already includes a video streaming subsection (5.4) that overlaps with J. U's content (raw vs effective FPS) is largely covered in both H and I. X's model generation comparison is partially covered in C (training).

**Recommendation**:
- **Merge U into H** (pipeline FPS analysis belongs with inference architecture)
- **Move H's streaming subsection to J** (streaming_architecture.tex already covers this more thoroughly)
- **Keep X** (model comparison is distinct enough from C's training focus)
- Result: saves 1 appendix and ~4 pages

### Minor Overlaps

- **F** (field_results) and **M** (field_day_narrative): F presents quantitative results; M presents the narrative. Some overlap in FOV calibration, benchmark results, and DJI analysis. Both are worth keeping -- F is data, M is story.
- **AH** (evaluation_detail) and **L** (testing_deep): Both contain defect discovery tables. If L is merged into E, AH's table becomes the only instance.

---

## 3. Are Appendices Referenced from the Body Text?

### Well-referenced appendices (cited from body sections):
- A (app:states) -- from system_description
- B (app:config) -- from system_description  
- C (sec:training) -- from evaluation
- E (sec:testing / sec:five-tier) -- from evaluation
- F (sec:results) -- from evaluation
- H (sec:cv:inference) -- from system_description
- I (app:cv-extended) -- from system_description
- J (sec:streaming-arch) -- from system_description (comms reference)
- K (sec:gps-deep) -- from evaluation
- O (sec:test-scripts) -- from system_description
- P (sec:calibration) -- from system_description
- Q (sec:sim-validation) -- from design_rationale
- AA (sec:path-opt) -- from design_rationale
- AD (sec:design-strategy) -- from design_rationale
- AF (app:decision-flow) -- from design_rationale
- AG (app:req-detail) -- from requirements_verification
- AH (app:eval-detail / app:bug-cost) -- from evaluation

### Potentially orphaned (not clearly referenced from body):
- **G** (future work) -- not explicitly cited from body, but standard appendix
- **L** (testing_deep) -- referenced from evaluation but duplicates E
- **M** (field_day_narrative) -- referenced from evaluation ("Appendix~\ref{sec:field-day}")
- **N** (contingency) -- not clearly cited from body text
- **R** (mission_flow) -- not clearly cited from body text
- **S** (centering_analysis) -- referenced from evaluation P10
- **T** (comms_architecture) -- referenced indirectly
- **U** (pipeline_fps) -- not clearly cited from body
- **V** (path_tradeoffs) -- not clearly cited from body
- **W** (payload_release) -- not clearly cited from body
- **X** (model_comparison) -- not clearly cited from body
- **Y** (search_optimization) -- SUPERSEDED, should be removed
- **AB** (optimization_master) -- referenced from design_rationale indirectly
- **AC** (optimization_formal) -- not clearly cited from body
- **AE** (vision_performance) -- not clearly cited from body
- **AI** (development_methodology) -- not clearly cited from body

Many "subsystem deep dives" (H-U) and "search optimisation" (V-AF) appendices are not directly cited from the body. The Appendix Guide directs readers to them, but body-text cross-references are sparse for the later appendices.

---

## 4. Is the Ordering Logical?

### Current grouping (from Appendix Guide):

1. Core system detail (A-D) -- Good
2. Verification and validation (E-G) -- Good
3. Subsystem deep dives (H-U) -- **14 appendices, too many, no clear progression**
4. Search and flight optimisation (V-AF) -- **11 appendices, heavy redundancy**
5. Extended body sections (AG-AI) -- Good

### Problems with current ordering:

1. **"Subsystem deep dives" is a catch-all bucket.** It contains CV (H,I), streaming (J), GPS (K), testing (L), field day (M), contingency (N), test scripts (O), calibration (P), simulation (Q), mission flow (R), centering (S), comms (T), and FPS (U). There is no logical progression.

2. **Search optimisation has 11 appendices** -- more than any other group -- but the content is heavily duplicated. A reader trying to understand parameter selection would be confused about which appendix to read.

3. **AG-AI feel like afterthoughts** at position 33-35, but they contain body-section overflow (requirements detail, evaluation detail) that readers are most likely to look up. They should be closer to the front.

### Recommended reordering:

After removing/merging redundant appendices (Y removed, L+O merged into E, U merged into H, V merged into AA, AC merged into AB), the remaining ~28 appendices should be reordered as:

**Group 1: Extended body sections (most likely to be consulted)**
- AG: Requirements verification detail
- AH: Evaluation detail  
- AI: Development methodology

**Group 2: Core system reference**
- A: State transition table
- B: Configuration parameters
- C: Model training and dataset
- D: Safety and risk management

**Group 3: Verification and validation**
- E: Testing methodology (now includes L's defect table, O's script catalogue)
- F: Field testing results
- M: Field day narrative

**Group 4: Subsystem architecture**
- H: Edge inference (now includes U's pipeline FPS)
- I: CV extended analysis
- X: Model comparison
- J: Streaming architecture  
- K: GPS estimation deep dive
- T: MAVLink communication
- P: Sensor calibration

**Group 5: Mission operations**
- R: Mission flow
- N: Contingency planning
- S: Centering vs direct offset
- W: Payload release
- Z: Focus area redirect + repulsive field
- Q: Simulation validation

**Group 6: Search optimisation**
- AA: Search path optimisation (now includes V's trade-offs)
- AB: Search parameter optimisation (now includes AC's formal statement)
- AD: Design strategy (parameter derivation chain)
- AE: Vision performance analysis
- AF: Decision flow (executive narrative)

**Group 7: Future work**
- G: Future work

---

## 5. Could Any Appendices Be Merged or Removed?

### Remove (1 appendix):
| App | Action | Reason |
|-----|--------|--------|
| Y | **Remove** | File header says "SUPERSEDED by path_optimization_definitive.tex". Content duplicated in AA. |

### Merge (5 appendices absorbed):
| Source | Into | Reason |
|--------|------|--------|
| L (testing_deep) | E (10_testing) | Same five-tier framework, same V-model, same defect table. L adds cost-risk gradient. |
| O (test_scripts_guide) | E (10_testing) | Script catalogue tables belong with the testing methodology. |
| U (pipeline_fps) | H (inference_architecture) | Raw-vs-effective FPS is a natural subsection of inference architecture. |
| V (path_tradeoffs) | AA (path_optimization_definitive) | Trade-off analysis belongs in the definitive optimisation appendix. |
| AC (optimization_formal) | AB (optimization_master) | Formal problem statement belongs in the master optimisation section. |

### Result:
- 35 appendices reduced to **29** (6 removed/absorbed)
- Estimated page savings: ~20-25 pages of duplicated content
- No information lost -- all content preserved in the merge targets

---

## Summary of Action Items

1. **IMMEDIATE**: Remove Y (search_optimization.tex) from main.tex -- it is self-declared superseded
2. **HIGH VALUE**: Merge L+O into E to consolidate all testing content
3. **HIGH VALUE**: Merge V into AA and AC into AB to consolidate optimisation content
4. **MEDIUM VALUE**: Merge U into H to consolidate inference content
5. **LOW PRIORITY**: Reorder appendices to put AG-AI closer to front (reader convenience)
6. **LOW PRIORITY**: Add body-text cross-references for orphaned appendices (N, R, W, AE, AI)

The most impactful single change is removing the search optimisation redundancy cluster (items 1 and 3), which eliminates ~15 pages of repeated 5-objective problem statements, decision vectors, and 216-config sweep references.
