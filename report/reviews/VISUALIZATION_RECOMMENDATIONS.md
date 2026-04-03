# Visualization Recommendations for D6 Report

Reviewed: `design_rationale.tex`, `system_description.tex`, `requirements_verification.tex`, `evaluation.tex`
Generated figures: 31 `gen_*.py` scripts, 51 PDF figures in `report/figs/`
Available environments: `abstractbox` (grey background), `infobox` (blue-bordered)

---

## 1. Prose That Should Be Tables or Charts

### 1A. Parameter Derivation Chain (design_rationale.tex, Sec 3.4)
**Current**: 8 numbered paragraphs of prose (Steps 1-8) describing how each parameter was derived.
**Recommendation**: Replace with a **chain table** with columns: Step | Input | Derivation | Output Value | Sensitivity. This makes the dependency chain scannable and lets the reader trace any parameter to its root constraint in seconds. Keep one introductory sentence; the rest is tabular.

### 1B. "Decisions That Changed" (design_rationale.tex, Sec 3.8)
**Current**: Four paragraphs, each with the pattern "initial value -> measurement -> correction".
**Recommendation**: A **4-row table** with columns: Parameter | Initial Value | Measured Value | Error (%) | Impact if Uncorrected. The narrative before/after structure maps perfectly to tabular form. Follow with a 1-2 sentence summary rather than repeating the impact in prose.

### 1C. "Why Not ROS" (design_rationale.tex, Sec 3.9)
**Current**: Three numbered bullet points with substantial prose.
**Recommendation**: A **compact comparison table**: Dimension | pymavlink (chosen) | ROS 2 (rejected), covering: deployment size, learning curve, latency overhead, and multi-node value. The three factors become rows, making the trade-off immediately visible.

### 1D. Five-Tier Testing Framework (evaluation.tex, Table 5)
**Current**: Good table, but the text around it repeats the table content.
**Recommendation**: Add a **visual progression diagram** (horizontal pipeline with arrows, colour-coded by completion status: green=done, yellow=partial, red=outstanding). This replaces the "Tiers 1-3 were fully exercised..." paragraph with a visual that shows status at a glance.

### 1E. Per-Flyover Detection Probability (requirements_verification.tex, R05)
**Current**: A dense paragraph with inline equations calculating N_eff, P_detect, and two-pass probability.
**Recommendation**: A small **summary table**: Scenario | Speed | Frames | N_eff | P_single | P_two_pass. Show the nominal case (8 m/s) and the degraded case (10 m/s, p_d=0.7) as two rows. The equations can remain in the text, but the results should be in a table.

### 1F. R09 Safety Mechanisms (requirements_verification.tex)
**Current**: Three numbered items describing RC kill, software override, and automated failsafes.
**Recommendation**: A **3-row table** with columns: Layer | Mechanism | Trigger | Response | Independence Level. This highlights the defence-in-depth structure better than prose.

---

## 2. Existing Figures That Could Be Improved

### 2A. GPS Accuracy Pair (system_description.tex, Fig 9a-b)
**Current**: Two subfigures (bullseye scatter + directional error) side by side. Good.
**Improvement**: Add **CEP50 and CEP95 circles** with labelled radii directly on the bullseye plot. Currently CEP50 is mentioned in the caption as a "dashed circle" -- make sure CEP95 is also shown. Add a **wind/heading arrow** to the directional plot to make the GPS lag elongation direction explicit.

### 2B. Detection Sensitivity Pair (evaluation.tex, Fig 11a-b)
**Current**: Confidence vs altitude and detection rate vs speed as separate subfigures.
**Improvement**: Add **operating point annotations** -- a vertical dashed line at h=35m on conf_vs_alt and v=8m/s on det_vs_speed with a label "selected operating point". This ties the figures directly to the design decisions. Also add the **marginal zone** (shaded region where detection becomes unreliable) to make the safety margin visually obvious.

### 2C. Latency Breakdown (evaluation.tex, Fig 12a)
**Current**: Presumably a stacked bar or pie chart.
**Improvement**: Use a **horizontal stacked bar chart** (waterfall-style) showing the five stages left to right with cumulative time. Label each segment with both milliseconds and percentage. Add a **target budget line** at 300ms and a **goal line** at the NCNN/FP16 projected improvement. This turns a static measurement into a story about optimization headroom.

### 2D. State Machine Diagram (system_description.tex, Fig 6)
**Current**: Full 20-state FSM diagram at 0.95 textwidth.
**Improvement**: The body diagram should be a **simplified mission-flow version** (7-8 macro-states: Startup, Search, Engage, Verify, Land, Return, Override) with the full 20-state version only in the appendix. The current figure is too dense for the body section at this scale. Group states into swim lanes by mission phase.

### 2E. Mission Overview Map (system_description.tex, Fig 4)
**Current**: Lawnmower pattern on satellite image.
**Improvement**: Add **numbered annotations**: (1) takeoff, (2) transit, (3) search entry, (4) detection event, (5) verify descent, (6) RTL. Use different line colours/styles for transit vs search legs. This turns a static map into a narrative sequence the reader can follow.

### 2F. Geofence Diagram (system_description.tex, Fig 5)
**Current**: Four-panel visualisation (boundaries, force field, correction, emergency).
**Improvement**: Good concept, but ensure the four panels use **consistent coordinate scales** and share a common legend. Add **distance annotations** (30m buffer, 20m slow zone, 3m hard cutoff) directly on panel (a) with dimension lines.

---

## 3. New Visualizations to Create

### 3A. MCDA Sensitivity Radar Chart (HIGH PRIORITY)
**Where**: design_rationale.tex, after the MCDA sensitivity analysis paragraph (line 129).
**What**: A **radar/spider chart** overlaying Pi 5, Jetson Nano, and Intel NCS2 scores on the 6 criteria axes. This makes the Pi 5's dominance visually immediate and shows which criteria the Jetson is competitive on. You already have gen scripts for radar charts (sensitivity_spider.pdf exists).
**Generator**: Adapt `gen_sensitivity_matrix.py` to produce a companion radar overlay.

### 3B. Error Budget Waterfall (HIGH PRIORITY)
**Where**: system_description.tex, near Table 3 (error budget).
**What**: A **horizontal waterfall/stacked bar** showing the six error sources from Table 3 at 35m altitude, building up to the RSS total of 2.9m. Then show a second bar with the fused estimate (after 15+ observations), visually demonstrating the reduction to sub-metre. This communicates the multi-observation fusion benefit far better than the table alone.
**Generator**: New `gen_error_budget_waterfall.py`.

### 3C. Platform Cost Comparison Bar Chart (MEDIUM PRIORITY)
**Where**: design_rationale.tex, STEEPLE Economic paragraph.
**What**: A simple **horizontal bar chart** comparing total system cost (565 GBP) against DJI Matrice 30T (5800 GBP) and one intermediate option (e.g., DJI Mini 3 Pro at ~800 GBP). The 10x cost difference is mentioned in prose but deserves a visual.
**Generator**: New `gen_cost_comparison.py` (trivial, ~20 lines).

### 3D. Simulation Fidelity Ladder (MEDIUM PRIORITY)
**Where**: system_description.tex, Section 2.6 (Simulation Framework).
**What**: A **vertical progression diagram** showing the four simulation levels stacked bottom-to-top with increasing fidelity: (1) Interactive sim, (2) SITL, (3) SITL+webcam, (4) DJI video replay. Label each with: what it tests, what it can't test, and which bugs it caught (from Table 4). Use colour to indicate completion status.
**Generator**: New `gen_simulation_ladder.py`.

### 3E. Ground Station Screenshot (HIGH PRIORITY -- KNOWN GAP)
**Where**: system_description.tex, Section 2.5 (Ground Station).
**What**: An **actual screenshot** of the browser dashboard showing the three panels (MJPEG stream, GPS grid, command buttons). This is called out as a known gap in D6_GOLDMINE_WORKFLOW.md item 6. If a real screenshot is unavailable, a **mockup** generated from the actual HTML/CSS with placeholder data would be far better than the current `\fbox` placeholder.
**Action**: Capture from `http://localhost:8090` during a SITL run, or generate a styled mockup.

### 3F. Detection Examples Montage (MEDIUM PRIORITY)
**Where**: evaluation.tex, after the discussion of detection performance.
**What**: A **2x3 grid of detection examples** showing: (row 1) true positives at different altitudes (20m, 35m, 50m), (row 2) challenging cases -- partial occlusion, shadow, false positive. Each with bounding box, confidence score, and altitude label. This provides visual evidence of detection quality that prose cannot.
**Generator**: Extract frames from DJI video replay or bench test outputs.

### 3G. Inference Backend Comparison (LOW PRIORITY)
**Where**: evaluation.tex, discussion of D2/D9 (inference rate, float32).
**What**: A **grouped bar chart** comparing inference time across backends: TFLite float32 (207ms), TFLite FP16 (projected ~100ms), NCNN (72ms measured), with a horizontal line at the 300ms budget. This visualises the optimization headroom discussed in D2 and D9.
**Generator**: New `gen_backend_comparison.py`.

### 3H. Requirements Coverage Matrix (LOW PRIORITY)
**Where**: requirements_verification.tex, alongside Table 1.
**What**: A **visual matrix/heatmap** with requirements on the Y axis and verification methods on the X axis (SITL, Bench, Video Proxy, Flight, Design Review). Cells coloured by status (green/yellow/red). This is more visually scannable than the text-heavy Table 1 and immediately shows the testing gap (no flight column is all red).
**Generator**: New `gen_requirements_matrix.py`.

---

## 4. Infobox and Abstractbox Opportunities

The `infobox` (blue border) and `abstractbox` (grey background) environments are defined in `main.tex` but appear to be **unused in the four body sections**. These should be deployed for standout findings.

### 4A. Key Numerical Result (infobox)
**Where**: evaluation.tex, after the detection performance discussion.
**Content**:
```
\begin{infobox}
\textbf{Key result.} The YOLOv8n model achieves 4.8 FPS inference on the Pi 5 CPU
with 0.995 mAP50, providing 11--17 detection opportunities per target flyover at
8 m/s search speed. Two-pass detection probability exceeds 99.75\%.
\end{infobox}
```

### 4B. Weather Adaptation Finding (infobox)
**Where**: evaluation.tex, weather cancellation paragraph.
**Content**:
```
\begin{infobox}
\textbf{Adaptation outcome.} The cancelled flight day yielded four quantitative
calibrations (FOV, lens distortion, inference speed, GPS accuracy) that would
have required multiple flight sorties to collect under normal conditions.
\end{infobox}
```

### 4C. Cost Comparison Highlight (abstractbox)
**Where**: design_rationale.tex, STEEPLE Economic paragraph.
**Content**:
```
\begin{abstractbox}
The complete SAR drone system costs \pounds565 --- approximately one-tenth the
price of commercial alternatives --- while performing onboard inference that
eliminates the need for high-bandwidth communication equipment.
\end{abstractbox}
```

### 4D. GPS Estimation Key Finding (infobox)
**Where**: system_description.tex, target localisation section.
**Content**:
```
\begin{infobox}
\textbf{Localisation accuracy.} Single-observation CEP50 = 2.3 m (RSS = 2.9 m).
After inverse-variance fusion of 15+ multi-altitude observations, the fused
estimate converges to sub-metre accuracy, exceeding the 5--10 m landing
requirement (R07) with >99\% probability.
\end{infobox}
```

### 4E. Section Summaries (abstractbox)
**Where**: End of each body section (design_rationale, system_description, requirements_verification, evaluation).
**Content**: 2-3 sentence section summary in an `abstractbox`. This is recommended in D6_GOLDMINE_WORKFLOW.md but not yet implemented. Example for design rationale:
```
\begin{abstractbox}
\textbf{Section summary.} Every major design decision was evaluated using
weighted MCDA with documented sensitivity analysis. The selected operating
point (35 m, 70 deg, 8 m/s) provides 96\% coverage at 10.9\% battery
cost, with all four trade study winners robust to +/- 0.05 weight perturbation.
\end{abstractbox}
```

---

## 5. Remaining Placeholder Figures to Replace (CRITICAL)

These `\fbox` placeholders exist in the appendix sections and must be replaced before submission. They are not in the body sections (which use real figures), but they exist in older appendix files:

| File | Placeholder | Replacement Available? |
|------|------------|----------------------|
| `02_system_architecture.tex` | System Architecture Block Diagram | Yes: `architecture.pdf` |
| `02_system_architecture.tex` | Module Dependency Graph | Yes: `architecture.pdf` |
| `03_hardware_platform.tex` | Hardware Block Diagram | Needs: `gen_pi_system.py` output |
| `04_computer_vision.tex` | CV Pipeline Diagram | Yes: `cv_pipeline.pdf` |
| `06_state_machine.tex` | State Machine Diagram | Yes: `state_machine.pdf` |
| `07_target_localisation.tex` | GPS Scatter Plot | Yes: `gps_bullseye.pdf` |
| `08_ground_station.tex` | Dashboard Screenshot | **MISSING**: needs real screenshot |
| `09_simulation.tex` | Simulator Screenshot | **MISSING**: needs real screenshot |

Note: These appendix files (`02_*` through `09_*`) may be older versions superseded by the consolidated body sections. Verify whether they are still `\input`-ed from `main.tex`. If they are still included, swap the `\fbox` for the available PDFs.

---

## 6. Priority Ranking

| Priority | Action | Impact on Score | Effort |
|----------|--------|----------------|--------|
| 1 | Ground station screenshot (3E) | Communication +3 | Low (capture from SITL) |
| 2 | Replace remaining \fbox placeholders (Sec 5) | Communication +2 | Low (PDFs exist) |
| 3 | Add infobox/abstractbox for key findings (4A-4E) | Communication +2 | Low (text only) |
| 4 | MCDA sensitivity radar chart (3A) | Decision Making +2 | Medium |
| 5 | Error budget waterfall (3B) | Specialist +2 | Medium |
| 6 | Parameter chain table (1A) | Communication +1 | Low (reformat prose) |
| 7 | Decisions-that-changed table (1B) | Decision Making +1 | Low (reformat prose) |
| 8 | Annotate operating points on Fig 11 (2B) | Communication +1 | Low (edit gen script) |
| 9 | Detection examples montage (3F) | Specialist +2 | Medium |
| 10 | Cost comparison bar (3C) | Communication +1 | Low |
| 11 | Simplified body state machine (2D) | Communication +1 | Medium |
| 12 | Simulation fidelity ladder (3D) | Communication +1 | Medium |
| 13 | Requirements coverage matrix (3H) | Communication +1 | Medium |
| 14 | Backend comparison bar (3G) | Specialist +1 | Low |

Items 1-3 are quick wins that directly address known gaps from the v4 scoring. Items 4-7 strengthen the decision-making score. Items 8-14 are polish that cumulatively improve communication quality.
