# System Description -- Brutal Goldmine Review

**Section:** `report/sections/system_description.tex` (241 lines)
**Rendered pages:** D6 pages 8--10 (approx 2.5 pages of body content)
**Date:** 2026-03-27

---

## Overall Score: 72 / 100

| Dimension | Score | Notes |
|-----------|-------|-------|
| Architecture clarity | 78 | Good layered breakdown, module graph present, but text-heavy architecture diagram is barely readable |
| Figure quality | 62 | 12 figures referenced but several are text-box placeholders, not real diagrams; key figures missing entirely from rendered PDF |
| Completeness (all subsystems) | 75 | All major subsystems present; payload release, comms link budget, and power/endurance absent |
| Technical depth | 73 | GPS estimation math is strong; CV pipeline and geofence are solid; state machine and ground station are surface-level |

---

## Figure Audit (12 referenced)

| # | Label | Caption quality | Actually rendered? | Verdict |
|---|-------|----------------|-------------------|---------|
| 1 | `mission_overview` | Good -- site map with pattern, NFZ, RTL | Yes (page 8) | OK but small; hard to read zone labels |
| 2 | `architecture` | OK -- "module dependency graph" | Yes but it is a TEXT BOX with arrows described in monospace text, not a real diagram | WEAK -- replace with a proper block diagram |
| 3 | `pi_system` | Good -- hardware interfaces and data flow | Yes (page 8) | OK |
| 4 | `geofence_diagram` | Excellent -- four-panel caption | Yes | STRONG -- best figure in section |
| 5 | `cv_pipeline` | Good -- pipeline stages with timing | Yes (page 9) | OK |
| 6 | `coverage_vs_time` | OK -- linear coverage progression | NOT visible in rendered pages 8--10 | Likely pushed to next page or float collision |
| 7 | `state_machine` | Good caption | Rendered on page 10 as TEXT listing, not a real FSM diagram | WEAK -- the "Figure 2" is just monospace text of state names with arrows. This is the single most important diagram in the section and it looks like a terminal printout |
| 8 | `gps_bullseye` | Good -- CEP50 circle | Subfigure, not visible in rendered pages | Float pushed out |
| 9 | `gps_error_direction` | Good -- directional elongation | Subfigure, not visible in rendered pages | Float pushed out |
| 10 | `gps_convergence` | Good -- Kalman convergence | Subfigure, not visible in rendered pages | Float pushed out |
| 11 | `estimator_comparison` | Good -- three estimators compared | Subfigure, not visible in rendered pages | Float pushed out |
| 12 | `mission_timeline` | Good -- state transitions over time | Not visible in rendered pages | Float pushed out |

**Verdict:** 5 of 12 figures are confirmed visible in the rendered system description pages. The remaining 7 are either floated away from their text or pushed into later sections. The two most critical figures (architecture diagram, state machine diagram) are the weakest visually -- both are text-box placeholders, not proper diagrams.

---

## Subsystem-by-Subsystem Critique

### 2.1 Hardware Platform (lines 18--41) -- ADEQUATE
- BOM table is clean and professional. Costs are reasonable.
- UART baud rate, MAVProxy bridge, TCP port, lens calibration RMS, focal length all stated. Good.
- **Missing:** No physical photo of the assembled drone or wiring diagram. The brief says "schematics, images recommended." A single photo of the Pi+Cube+camera assembly would add credibility.
- **Missing:** No mention of battery endurance / flight time budget. At 5200 mAh 4S, what is the expected mission duration? This directly affects feasibility.
- **Missing:** Weight breakdown. Total AUW matters for flight dynamics and endurance.
- **Thin:** The Here3 GPS is listed as "5 Hz updates" but the text later discusses 100-200 ms GPS latency. This deserves a sentence connecting the two.

### 2.2 Software Architecture (lines 44--98) -- GOOD but diagram is embarrassing
- Four-layer decomposition is clear and well-structured.
- MAVLink command table (Table 12) is professional and useful.
- Five-stage data pipeline paragraph is excellent -- concise, complete, ordered.
- Geofence paragraph with three nested layers and `cv2.pointPolygonTest` is strong technical content.
- **CRITICAL:** The architecture diagram (Figure 1) renders as a grey text box with monospace text reading "Config -> Independent Modules (vision, planning, geofence, gps_utils) -> Domain (navigation, stream_server) -> Orchestrator (state_machine -> main.py)". This is not a figure -- it is placeholder text masquerading as a diagram. For a section that is supposed to showcase the system, this is the weakest element. Replace with a proper layered block diagram showing modules, data flow arrows, and the hardware they touch.
- **Missing:** No mention of error handling strategy (what happens when MAVLink times out? when camera fails?). The rubric asks for "problem-solving" -- showing fault tolerance would score points.
- **Missing:** Threading model. The system has concurrent camera capture, inference, MAVLink heartbeats, and HTTP server. One sentence on how these are managed (threads? main loop with polling?) would add depth.

### 2.3 Computer Vision Pipeline (lines 100--119) -- SOLID
- Single-interface design (`detect_in_image -> (found, cx, cy, conf)`) is well explained and shows good software engineering.
- Preprocessing chain is complete: undistort, colour handling (BGR note), resize, normalise.
- Three backends (NCNN, Ultralytics, TFLite) with automatic selection is impressive.
- Smart detection mode with consecutive-frame filtering is a nice detail.
- Performance numbers are concrete: 206.5 ms, 4.8 FPS, 0.966 confidence.
- Frame overlap calculation (91%, 11-17 opportunities) directly addresses detection reliability. Strong.
- **Thin:** No mention of false positive rate or how negatives were handled in training. The model was trained on 50 negatives -- this is worth a sentence.
- **Missing:** No mention of the model architecture (YOLOv8n -- nano variant, 3.2M params). The text says "TFLite model" but never names YOLOv8 or explains why nano was chosen over small/medium.
- **Missing:** Confidence threshold (0.2 in text, 0.4 in config) -- which is it? Inconsistency.

### 2.4 Search Pattern Generation (lines 122--145) -- STRONG
- Best-written subsection. Rotated-mask algorithm is clearly explained in 6 steps.
- Coverage guarantee with proper equation and numerical substitution is exactly what an MSc report needs.
- Scan angle optimisation with 216-configuration sweep is evidence-based and impressive.
- PLB redirect mention connects to R06.
- **Minor:** The equation uses $w_s$, $f$, $h$, $\alpha$ but the overlap fraction $\alpha = 0.20$ could be justified (why 20%? industry standard? GPS drift compensation?).
- **Missing:** The coverage_vs_time figure may not render on the same page -- verify float placement.

### 2.5 Mission State Machine (lines 148--167) -- THIN
- 20 states are listed in four phases (Startup, Search, Engagement, Recovery). The grouping is logical.
- Detection queue with spatial deduplication and bounded capacity shows engineering maturity.
- Five safety mechanisms listed.
- **CRITICAL:** The state machine diagram (Figure 2) renders as monospace text, not a real FSM diagram. For a 20-state machine with 32+ transitions, this is unacceptable. This should be a proper directed graph with boxes, arrows, and colour-coded phases. The caption promises "Primary mission path flows left to right; engagement branches downward" but the rendered figure is just a text listing.
- **Thin:** Only 18 lines of text for a 20-state machine. There is no discussion of: timeout values, altitude schedule during descent, what triggers transitions (specific conditions), or how the detection queue feeds into CENTERING. The four bullet points read like a list, not an explanation.
- **Missing:** No mention of how the operator interacts with the state machine (Y/N/I/X buttons). The VERIFY state is mentioned ("operator Y/N/I with 120s timeout") but the interaction flow is not explained.
- **Missing:** No mention of what happens on failure at each state (e.g., arming fails, GPS lost during search, target lost during centering).

### 2.6 Target Localisation (lines 169--217) -- STRONG
- Pinhole camera model, GSD formula, heading rotation, WGS84 conversion -- complete chain.
- Three fusion methods (clustering, inverse-variance, Kalman) are well described with formulas.
- CEP50 = 2.3 m from real DJI footage is excellent empirical evidence.
- GPS timing lag attribution (100-200 ms) shows root-cause analysis.
- Four subfigures (bullseye, directional error, convergence, estimator comparison) -- if they render properly, this is the most evidence-rich subsection.
- **Risk:** All four subfigures may float away from the text. Verify in rendered PDF.

### 2.7 Ground Station (lines 220--228) -- ADEQUATE but brief
- Three panels described (video, GPS grid, command buttons). Nine buttons listed.
- MJPEG rationale (vs H.264/WebRTC) with three reasons is good.
- Headless auto-detection and passive monitoring mode mentioned.
- **Thin:** Only 9 lines of prose. No screenshot of the ground station UI. For a browser-based dashboard with live video, GPS grid, and 9 command buttons, a screenshot would be worth 500 words. The brief explicitly says "images recommended."
- **Missing:** No mention of latency beyond "approximately 300 ms." What is acceptable? How does this affect operator decision-making in VERIFY state?
- **Missing:** No mention of the operator workflow in detail. The text says "press N to investigate, watch video, confirm Y or reject X" in one sentence. This is the human-in-the-loop -- it deserves more space.

### 2.8 Simulation Framework (lines 231--240) -- THIN
- Four simulation levels listed in one sentence. Good breadth.
- "Same detection model, GPS estimation, MAVLink interface at every level" is a strong claim.
- Bugs caught in simulation listed (4 specific bugs). Excellent.
- **Thin:** Only 9 lines. No depth on any simulation level. The interactive simulator (simple_simulator.py, 2508 lines) has keyboard flight, GPS estimation, multi-target tracking, Kalman filter, offset landing -- none of this is mentioned.
- **Missing:** No figure or screenshot of the simulation environment. The mission_timeline figure is referenced but likely floats away.
- **Missing:** No mention of how simulation fidelity was validated (i.e., does SITL behaviour match real Cube behaviour? Were there surprises when moving from sim to hardware?).

---

## What is Missing Entirely

1. **Payload release mechanism.** R07 requires landing near the casualty and deploying a first aid kit. The Tarot payload release is in the equipment table but NEVER mentioned in the system description. How is it triggered? What MAVLink command? What state (HOVER_TARGET mentions "servo payload release" in the state machine but no technical detail).

2. **Communications link budget / range.** The Pi uses built-in Wi-Fi. What is the range? What happens when the drone is 200m away? Is the MJPEG stream still viable? Link loss is mentioned as a safety mechanism but not characterised.

3. **Power / endurance analysis.** No flight time estimate. No power draw breakdown (Pi, camera, servos, motors). The brief requires a full mission (search + engage + return). Can the battery last?

4. **Physical integration.** No photo, no mounting description, no vibration isolation, no wiring diagram. Where is the Pi mounted? How is the camera oriented (nadir)? Is there vibration damping?

5. **RC override and kill switch details.** Listed as safety mechanisms but not described technically. Which RC channel? What mode does it switch to? How fast is the response?

---

## Float / Layout Issues (from rendered PDF)

The section spans pages 8--10 in the rendered PDF. Key observations:
- Page 8: Hardware table + architecture text box + Pi system diagram. Crowded.
- Page 9: CV pipeline figure + search pattern text. Reasonably laid out.
- Page 10: State machine "figure" (text box) + localisation text + ground station + simulation (very compressed). The last three subsections are crammed into less than half a page each.
- GPS accuracy subfigures (4 plots), coverage_vs_time, and mission_timeline are NOT visible on pages 8--10. They have floated elsewhere, meaning the text references figures the reader cannot see nearby. This breaks reading flow.

**Recommendation:** Use `[H]` float specifier (requires `\usepackage{float}`) or `[!htbp]` with `\FloatBarrier` to force critical figures near their text.

---

## Top 10 Fixes (Priority Order)

1. **Replace state machine diagram** with a proper FSM graph (boxes, arrows, colour-coded phases). This is the centrepiece of the section.
2. **Replace architecture diagram** with a real layered block diagram (not a text box).
3. **Add ground station screenshot.** One figure showing the browser dashboard with video + GPS grid + buttons.
4. **Add drone photo.** One image of the assembled hardware (Pi, Cube, camera, frame).
5. **Fix float placement** for GPS accuracy subfigures and coverage_vs_time -- they must appear near their text.
6. **Expand state machine text** -- add transition conditions, timeout values, failure handling. Currently 18 lines for 20 states is too thin.
7. **Add payload release description** -- even 2-3 sentences connecting R07 to the servo command.
8. **Add flight time / endurance estimate** -- even a rough one (e.g., "estimated 12 min flight time based on 5200 mAh at ~25A hover current").
9. **Name the model** -- say "YOLOv8n (nano)" explicitly, mention 3.2M parameters, explain why nano was chosen.
10. **Fix confidence threshold inconsistency** -- text says 0.2, config says 0.4. Pick one and be consistent.

---

## Rubric Alignment

| D6 Criterion | How this section scores | Estimate |
|-------------|------------------------|----------|
| **Specialist Skills (40%)** | Good: multi-backend CV, geofence layers, Kalman filter, coverage guarantee equation. Weak: placeholder diagrams undermine "comprehensive identification of task." | 70 |
| **Decision Making (40%)** | Good: MJPEG rationale, scan angle sweep, smart detection mode. Weak: no justification for YOLOv8n choice, no endurance analysis, no discussion of what changed when moving sim->real. | 72 |
| **Communication (20%)** | Good: clean tables, proper SI units, equation numbering. Weak: two placeholder diagrams, float chaos, ground station has no screenshot, three subsections crammed into half-pages. | 68 |

---

## Bottom Line

The technical content is genuinely strong -- GPS estimation math, coverage guarantee equation, geofence enforcement, and CV pipeline are all MSc-quality. But the presentation has two fatal wounds: the state machine and architecture "diagrams" are text boxes, and half the figures float away from their text. Fix the two placeholder figures, add a ground station screenshot and drone photo, force floats near their text, and expand the state machine subsection. That alone would push this from 72 to 80+.
