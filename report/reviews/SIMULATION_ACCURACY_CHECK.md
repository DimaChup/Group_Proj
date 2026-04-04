# Simulation Accuracy Check: Code vs Report

**Date:** 2026-04-04
**Files examined (code):** `simulator/simulation.py`, `main.py`, `state_machine.py`, `config.py`, `vision.py`, `states.py`
**Files examined (report):** `09_simulation.tex`, `simulation_validation.tex`, `design_strategy.tex`, `system_description.tex`, `evaluation.tex`, `gps_estimation_deep.tex`

---

## Summary

The report is broadly accurate and detailed. The simulation framework is well-described across multiple sections. However, there are **3 factually wrong claims**, **5 missing features** that deserve mention, and **2 understated capabilities**. No exaggerations were found -- the report is appropriately cautious.

---

## WRONG Claims (code contradicts report)

### W1. "SITL camera views are static screenshots" (design_strategy.tex:129)

**Report says:** "SITL camera views are static screenshots; real aerial imagery exhibits motion blur proportional to speed and altitude."

**Code reality:** `main.py` lines 49-67 implement three configurable degradation effects for the SITL camera view (Level 2):
- `--blur <factor>`: Physics-based directional motion blur using a kernel aligned to yaw angle. Computes pixel motion from both translational speed (GSD-based) and rotational yaw rate. Kernel size capped at 51px. (lines 674-712)
- `--shake <pixels>`: Random per-frame pixel translation simulating vibration (lines 669-673)
- `--noise <level>`: Gaussian noise injection into GPS position (~2.8m std), altitude (~0.5m std), and attitude (~0.5 deg std) (lines 508-518)

**Verdict:** The claim is factually wrong. SITL camera views are NOT static screenshots when these flags are enabled. The blur implementation is physically grounded (exposure time, GSD, yaw rate).

**Fix needed:** design_strategy.tex line 129 should acknowledge that `--blur`, `--shake`, and `--noise` flags are available in the SITL mode.

### W2. Validation matrix marks motion blur/vibration as "---" for both Interactive and SITL (simulation_validation.tex:28)

**Report says:** `Motion blur and vibration effects & --- & --- & --- & ~`

**Code reality:**
- Interactive simulator (simple_simulator.py) has `--shake` for camera jitter and `--gps-drift` for GPS noise (acknowledged elsewhere in the report at 09_simulation.tex:43)
- SITL mode (main.py) has `--blur`, `--shake`, and `--noise` as described in W1

**Verdict:** The matrix should show `$\sim$` for both Interactive and SITL columns, not "---".

### W3. "The interactive simulator and SITL produce sharp synthetic frames regardless of drone velocity" (simulation_validation.tex:123)

**Report says:** This is the Known Gaps section.

**Code reality:** Both simulators have blur/shake injection as described above. The frames are sharp BY DEFAULT, but the capability exists. The statement should say "by default" or "without the `--blur` flag".

**Fix needed:** Add qualifier "by default" and note the existence of `--blur`/`--shake` flags.

---

## MISSING Features (code does something the report doesn't mention)

### M1. Perspective ray-traced camera view with attitude compensation (main.py + simulation.py)

The `--sim-tilt` flag enables a sophisticated perspective camera rendering in simulation.py (lines 416-546): ray-tracing 4 image corners through a full rotation matrix R = Rz(yaw) @ Ry(-pitch) @ Rx(-roll) onto the ground plane, then performing a perspective warp. Targets are composited BEFORE the warp so they receive the same perspective distortion. Falls back to nadir view if any corner ray points upward.

**This IS mentioned in gps_estimation_deep.tex:645** but is NOT mentioned in 09_simulation.tex (the main simulation section) or simulation_validation.tex. It should be -- it's a significant technical achievement that validates the tilt compensation mathematics in a closed loop.

### M2. Five target types in simulation (dummy, cone, pants, tshirt, backpack)

simulation.py lines 63-67 support 5 target types with individual PNG assets, height scaling, and cycle-through selection (C key). The report only mentions "dummy" targets and "multiple targets" but never mentions the multi-class aspect of the simulation (cones, clothing items, backpack).

### M3. God view coverage overlay with rescan pass colouring

simulation.py lines 682-690: The god view tracks camera coverage during SEARCH state, drawing colour-coded swept area (yellow for pass 1, orange for pass 2, green for pass 3+). This is overlaid at 20% opacity. Not mentioned anywhere in the report. This is a useful visualization for assessing search completeness.

### M4. Focus Area (PLB beacon redirect) support in simulation

simulation.py lines 188-195 and 251-258: The interactive setup supports drawing a magenta "Focus Area" polygon for PLB (Personal Locator Beacon) redirect scenarios. This isn't mentioned in the simulation section.

### M5. NFZ vector field visualization in god view

simulation.py lines 624-650: When `--arrows` flag is used, the god view renders a vector field around the SSSI NFZ showing repulsive force direction and magnitude at grid points. Color-coded by distance (red < 4m, orange < 7m, yellow otherwise). Not mentioned in the report.

---

## UNDERSTATED Features (report mentions but undersells)

### U1. SITL camera effects are more sophisticated than presented

The report mentions `--shake` for the interactive simulator (09_simulation.tex:43) but does NOT mention that main.py (SITL Level 2) also has:
- `--blur`: Physics-based directional motion blur with both translational AND rotational components (yaw rate contributes to blur at frame edges)
- `--noise`: Full 6-DOF noise injection (lat, lon, alt, pitch, roll, yaw) with configurable level
- `--sim-tilt`: Full perspective camera rendering with ray-tracing
- `--sim-roll`: Random roll oscillation (cosmetic frame rotation)
- `--sim-pitch`: Camera pitch offset during forward flight

These make the SITL level significantly more capable than the report suggests. The report presents the interactive simulator as having the error injection capabilities and the SITL level as only validating MAVLink commands -- in reality, SITL has BOTH.

### U2. God view rendering is highly optimized

simulation.py lines 29-39: The god view uses pre-scaled maps (~4MB vs ~63MB per frame) with a 94% memory reduction. All drawing happens at display resolution. This is an engineering optimization worth mentioning in a technical report, especially in the context of real-time performance.

---

## ACCURATE Claims (verified correct)

- **20 states** -- confirmed in states.py (20 state values)
- **Four simulation levels** -- accurately described
- **FOV computation** -- equation matches simulation.py line 336-340
- **Satellite map subimage extraction** -- accurately described (simulation.py lines 354-385)
- **SITL home location** -- 51.423406N, 2.671446W matches config.py
- **Configuration auto-detection** -- accurately described
- **Same model file** -- best.tflite used across all levels
- **Interactive simulator keyboard controls** -- WASD/RF/QE accurately described
- **GPS estimation pipeline** -- three concurrent estimators accurately described
- **Bugs caught in simulation** -- all 5 listed bugs verified in CLAUDE.md session logs
- **Multi-target placement** -- accurately described
- **Video replay SRT synchronization** -- accurately described
- **Dual backend vision system** -- accurately described as Ultralytics/TFLite
- **Geofence enforcement** -- 5-layer system accurately described elsewhere
- **Stream server** -- ThreadingMixIn HTTP server at port 8090, MJPEG, /cmd endpoint all correct
- **Headless auto-detection** -- correctly described
- **Docker Pi test** -- correctly described

---

## Recommended Fixes

### Priority 1: Fix wrong claims

1. **design_strategy.tex:129** -- Change "SITL camera views are static screenshots" to acknowledge --blur/--shake/--noise flags
2. **simulation_validation.tex:28** -- Change motion blur/vibration from "---/---" to "$\sim$/$\sim$" for Interactive and SITL columns
3. **simulation_validation.tex:123** -- Add "by default" qualifier and mention --blur/--shake capability

### Priority 2: Add missing features to 09_simulation.tex

4. Add a paragraph about `--sim-tilt` perspective rendering in the SITL Integration subsection -- this is a significant technical feature -- **DONE**
5. Mention the `--blur` and `--noise` flags in the SITL subsection (currently only --shake is mentioned, and only for the interactive simulator) -- **DONE**

### Priority 3: Nice-to-have additions

6. Mention 5 target types in the multi-target subsection
7. Mention the coverage overlay visualization
8. Mention the NFZ vector field visualization (if space permits)

### Additional fix applied

9. **simulation_validation.tex:29** -- Changed "Real GPS noise" from "---" to "$\sim$" for Interactive column, since the interactive simulator has `--gps-drift` which simulates GPS noise via Ornstein-Uhlenbeck random walk.

---

## All Fixes Applied

| # | File | Line | Issue | Status |
|---|------|------|-------|--------|
| 1 | design_strategy.tex | 129 | "static screenshots" claim | FIXED |
| 2 | simulation_validation.tex | 28 | Motion blur "---/---" in matrix | FIXED to "$\sim$/$\sim$" |
| 3 | simulation_validation.tex | 123 | "sharp frames regardless" claim | FIXED with qualifier |
| 4 | 09_simulation.tex | after 98 | Missing --sim-tilt perspective rendering | ADDED subsubsection |
| 5 | 09_simulation.tex | after 98 | Missing --blur/--shake/--noise for SITL | ADDED subsubsection |
| 6 | simulation_validation.tex | 29 | GPS noise "---" for Interactive | FIXED to "$\sim$" |
