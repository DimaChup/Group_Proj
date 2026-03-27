# Optimization & Trade-Off Approaches: Cross-Project Research

Findings from the Aerial Robotics report (AENGM0073), the v3 `analysis/` scripts, and the dashboard data.
Goal: identify proven frameworks, figures, tables, and patterns to replicate in the SAR drone (AENGM0074) report.

---

## 1. Frameworks Used in the Aerial Robotics Report (Final_v2.tex)

### 1.1 Two-Stage AHP-Weighted MCDA (Platform Selection)

The strongest reusable pattern. Used for selecting the JOUAV PH-20 from six candidates.

**Stage 1 -- Configuration downselection** (`tab:config-mcda`):
- 3 configurations (multi-rotor, fixed-wing, hybrid VTOL) scored against 6 criteria.
- Each criterion given a weight (2-5) reflecting mission priorities.
- Scores on a 1-5 scale (1=poor, 5=excellent).
- Weighted total computed, winner justified narratively.

**Stage 2 -- COTS platform MCDA** (`tab:platform-mcda`):
- 6 candidate platforms scored against 10 criteria.
- Criteria weights derived via AHP pairwise comparison (Saaty 9-point scale).
- Full AHP matrix with geometric mean method, consistency ratio CR=0.036 < 0.10.
- Binary pass/fail gate BEFORE the scored MCDA (payload >= 0.82 kg, VTOL, wind >= 10 m/s, open SDK).
- Sensitivity analysis: weights perturbed +/-20%, selection remained robust.

**Tables to replicate:**
1. AHP pairwise comparison matrix (7x7, Saaty scale, CR verified)
2. AHP-derived weights table (rank, criterion, geometric mean, weight, priority tier)
3. AHP consistency verification table (lambda_max, CI, RI, CR)
4. Configuration MCDA scoring table (criterion x alternative, weighted totals)
5. Platform MCDA scoring table (criterion x 6 candidates, weighted totals)

**Key LaTeX patterns:**
- `\rowcolor{lightrow}` alternating rows
- `\compactTable` macro for consistent sizing
- `\tabularx` with centered X columns for multi-candidate comparisons
- Weights column (Wt) alongside scores

### 1.2 Design Optimisation Metrics Table (Two-Sided)

`tab:design-objectives` -- a two-column layout:
- Left: "Maximise -- Data Quality" (DQ-1 through DQ-6)
- Right: "Minimise -- Cost" (C-1 through C-4)
- C-1 (personnel health risk) marked as **hard constraint**, not a trade-off variable.

**Replicable for SAR:** Maximise detection probability vs Minimise energy/time/risk. Mark safety constraints (geofence, kill switch) as hard constraints separate from trade-off variables.

### 1.3 Design Decision Pipeline Table

`tab:design-pipeline` -- a numbered sequence of 9 decisions, each with:
- Step number
- Decision description
- Method used (stakeholder analysis, 4-way trade study, weighted MCDA, pass/fail gate, etc.)
- Output section reference

**Replicable for SAR:** Map our design decisions (path strategy, CV model, NFZ approach, landing offset, altitude profile) to methods.

### 1.4 Sensitivity Analysis (Paragraph-Level)

Brief but effective: "Criteria weights were perturbed by +/-20%. Under all perturbations, the PH-20 remained first or second; the Acecore Noa overtook it only when wind tolerance weight was reduced below 3, which contradicts the SHV environment."

**Key elements:**
- Perturbation range (+/-20%)
- What changed and what did not
- Under what extreme condition the choice flips (and why that condition is unrealistic)

### 1.5 Endurance Derating Equation

A multiplicative derating chain:
```
E_mission = E_spec x f_payload x f_alt x f_turb x f_reserve
```
Each factor justified individually (0.95, 0.90, 0.85, 0.80). Final answer: 32 min.

**Replicable for SAR:** Battery derating for our drone (payload, wind, safety margin).

### 1.6 Smear Budget (Central Design Coupling)

The most elegant analysis in the report. Links sensor response time to flight speed to transect duration to sortie count, showing how one parameter (tau_eff) constrains the entire mission. Equation:
```
v_perp_max = d_smear_max / tau_eff = 50/17 ~ 3 m/s
```

**Replicable for SAR:** Our "central design coupling" is inference FPS constraining speed constraining coverage time. Document this chain explicitly.

### 1.7 Payload Pod Mass Budget Table

Simple component-by-component mass table with subtotals. Professional and clear.

---

## 2. Analysis Scripts Already Built (v3/analysis/)

### 2.1 Path Optimization (`analysis/path_optimization/optimize_path.py`)

**What it does:**
- Sweeps 6 altitudes x 36 scan angles (216 configurations)
- For each: computes scan lines, path length, time, energy, NFZ slowdown penalty
- Energy model: 150W hover + speed-squared drag + 2s U-turn penalty
- NFZ model: linear speed ramp within 20m of SSSI boundary

**Outputs (6 plots already generated):**
1. `plot1_energy_vs_altitude.png` -- energy with/without NFZ
2. `plot2_time_vs_altitude.png` -- time with/without NFZ
3. `plot3_scan_angle_vs_altitude.png` -- optimal angle per altitude
4. `plot4_scan_lines_vs_altitude.png` -- scan lines + swath width
5. `plot5_energy_heatmap.png` -- **2D heatmap** of energy across altitude x angle (Pareto-like)
6. `plot6_survey_and_pattern.png` -- map with optimal lawnmower overlaid

**Report-ready:** These plots can go directly into the report. The energy heatmap (plot5) is essentially a Pareto front visualization -- shows the trade-off space.

### 2.2 Vision Performance Plots (`analysis/vision_performance_plots.py`)

Generates 5 plots analyzing detection as a function of altitude and speed:
1. `plot1_altitude_vs_px.png` -- dummy pixel size vs altitude
2. `plot2_speed_vs_blur.png` -- motion blur vs speed
3. `plot3_speed_vs_frames.png` -- frames per target flyover vs speed
4. `plot4_coverage.png` -- coverage analysis
5. `plot5_detection_envelope.png` -- **detection envelope** (altitude x speed)

**Key analysis:** Shows blur is sub-pixel (never the limiting factor), frames-in-view always >10, and the real limit is altitude (pixel size). Detection envelope plot is a trade-off visualization.

### 2.3 Path Strategy Comparison (`analysis/path_simulation.py`)

Compares 4 path strategies (lawnmower, rotated lawnmower, spiral, random-start) at two altitudes. Outputs:
- `path_comparison.png` -- bar chart of metrics
- `path_patterns.png` -- all patterns overlaid on polygon

### 2.4 Path Strategies Document (`analysis/path_strategies.md`)

530-line comparative analysis of 6 search strategies. Contains:
- Summary comparison table (6 strategies x 6 metrics)
- Per-strategy estimates (path length, time, energy at 35m and 50m)
- Pros/cons analysis with quantitative backing
- 5-factor justification for lawnmower selection
- NFZ approach comparison table (3 methods: REPEL, SLOW, CARROT)

### 2.5 Speed/Blur/Detection Analysis (`analysis/speed_blur_detection.md`)

353-line document with:
- Ground footprint and GSD tables by altitude
- Dummy pixel size tables (full frame and model input)
- Speed vs FPS frame coverage tables
- Motion blur tables (speed x exposure x altitude)
- Detection constraint summary table (6 factors, limiting/not-limiting)
- NFZ approach comparison with properties table

### 2.6 GPS Accuracy Analysis (`analysis/gps_accuracy_analysis.md`)

525-line error budget analysis with:
- 6 error sources quantified (GPS noise, barometer, yaw, quantization, timing lag, camera mount)
- RSS error budget at two altitudes (35m search, 15m centering)
- Multi-observation averaging table (N observations vs accuracy improvement)
- Offset landing probability calculation
- 6 improvement strategies with gain/trade-off/recommendation

---

## 3. Dashboard Data (`dashboard/src/pages/group-project-v2-data.ts`)

### 3.1 Systems Engineering Layer Model

6-layer architecture with per-layer:
- `seApproach`: methodology text (trade study, protocol comparison, compute allocation matrix)
- `testPhilosophy`: testing strategy
- `decisions`: question/answer/reasoning triples for each design choice

### 3.2 Approach Comparison Structure

`Approach` interface with scalability rating ("high"/"medium"/"low"), evolution tracking (carriedOver/discarded/newChallenges), and per-layer content for each approach variant.

### 3.3 Integration Duties per Team Member

Each team member has `integrationDuties` listing cross-cutting concerns:
- "Power budget across all subsystems"
- "Weight budget vs flight time"
- "Frame rate vs compute tradeoff"
- "CV pipeline output format matches planner input"

---

## 4. Recommended Approaches to Replicate in SAR Report

### Priority 1: Weighted MCDA Tables (MUST HAVE)

Apply the two-stage MCDA pattern to our key decisions:

| Decision | Candidates | Criteria | Method |
|----------|-----------|----------|--------|
| Search pattern | 6 strategies (from path_strategies.md) | Coverage, energy, time, complexity, NFZ compat. | Weighted scoring |
| CV model | YOLOv8n vs YOLOv8s vs COCO person | Speed, accuracy, size, trainability | Weighted scoring |
| NFZ avoidance | REPEL, SLOW, CARROT | Smooth movement, complexity, controller conflict | Properties comparison (already in speed_blur_detection.md) |
| Altitude profile | 20-50m options | Detection pixel size, coverage efficiency, energy | Quantitative sweep (already done in optimize_path.py) |

For the search pattern MCDA, we already have the full data in `path_strategies.md` -- just needs to be formatted as a LaTeX table.

### Priority 2: Error Budget Table (MUST HAVE)

The GPS accuracy RSS error budget from `gps_accuracy_analysis.md` is report-ready. Format as:

| Error Source | At 35m | At 15m | Notes |
|---|---|---|---|
| GPS receiver | 2.3m | 2.3m | Dominant |
| ... | ... | ... | ... |
| **Total (RSS)** | **2.5m** | **2.3m** | Conservative |

### Priority 3: Detection Envelope (SHOULD HAVE)

The altitude-speed trade-off from `speed_blur_detection.md` showing that altitude (pixel size) is the real limit, not speed or blur. The detection envelope plot from `vision_performance_plots.py` visualizes this.

### Priority 4: Design Decision Pipeline (SHOULD HAVE)

Replicate the numbered pipeline table from the Aerial Robotics report, mapping each SAR design decision to its method and output section.

### Priority 5: Sensitivity Analysis (SHOULD HAVE)

For whichever MCDA we include, add a brief sensitivity paragraph: "Weights perturbed +/-20%, lawnmower remained optimal under all perturbations except [unrealistic scenario]."

### Priority 6: Central Design Coupling (NICE TO HAVE)

Document the inference FPS -> speed -> coverage chain as our equivalent of the smear budget. Show that 4.8 FPS at 10 m/s gives 94% frame overlap at 35m -- the system is never FPS-limited within the operational envelope.

---

## 5. Figures Already Available for the Report

All in `analysis/` directory, generated by Python scripts:

| Plot | File | What It Shows | Report Section |
|------|------|--------------|----------------|
| Energy vs altitude | `path_optimization/plot1_energy_vs_altitude.png` | NFZ impact on energy | Path planning |
| Time vs altitude | `path_optimization/plot2_time_vs_altitude.png` | NFZ impact on time | Path planning |
| Optimal scan angle | `path_optimization/plot3_scan_angle_vs_altitude.png` | Angle selection | Path planning |
| Scan lines vs altitude | `path_optimization/plot4_scan_lines_vs_altitude.png` | Coverage geometry | Path planning |
| Energy heatmap | `path_optimization/plot5_energy_heatmap.png` | 2D trade-off space | Path planning |
| Survey pattern | `path_optimization/plot6_survey_and_pattern.png` | Optimal pattern on map | Path planning |
| Altitude vs pixel size | `plot1_altitude_vs_px.png` | Detection vs altitude | CV / detection |
| Speed vs blur | `plot2_speed_vs_blur.png` | Blur is negligible | CV / detection |
| Speed vs frames | `plot3_speed_vs_frames.png` | Frame coverage margin | CV / detection |
| Coverage analysis | `plot4_coverage.png` | Coverage guarantee | CV / detection |
| Detection envelope | `plot5_detection_envelope.png` | Operating envelope | CV / detection |
| Path comparison | `path_comparison.png` | Strategy comparison bars | Path planning |
| Path patterns | `path_patterns.png` | 4 patterns on polygon | Path planning |

---

## 6. Key Differences: What the SAR Report Can Do Better

1. **Quantitative backing is stronger.** The Aerial Robotics report uses estimated scores (1-5 scale) for the MCDA. Our SAR project has actual computed values (path length, energy, time, pixel counts) from the analysis scripts. Use real numbers instead of subjective scores where possible.

2. **Visualization is richer.** The energy heatmap and detection envelope plots are more informative than simple scoring tables. Include both: tables for rigor, plots for intuition.

3. **Error budget is unique.** The GPS accuracy RSS analysis with multi-observation averaging is a level of rigor not present in the Aerial Robotics report. Highlight this.

4. **The NFZ comparison table** (REPEL vs SLOW vs CARROT with 6 properties) is already a clean trade study that maps directly to the Aerial Robotics format.

5. **Field validation.** The Aerial Robotics report relies on simulation alone. Our SAR project has bench test data (206ms inference, 4.8 FPS, 0.966 confidence). Include measured values alongside computed predictions.
