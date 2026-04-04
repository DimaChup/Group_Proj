# Simulation vs Real Flight: Code Comparison and Report Accuracy Check

**Date:** 2026-04-04
**Reviewer:** Claude Opus 4.6
**Scope:** Compare sim vs real code paths, verify D6 goldmine report presents this honestly

---

## Part 1: All Sim-to-Real Differences in Code

### 1. Camera Source
| Aspect | SIMULATION | REAL |
|--------|-----------|------|
| Frame source | `simulation.py` extracts FOV-correct subimage from `map.jpg` satellite photo | `vision.py` captures from Pi camera (picamera2 IMX296) or webcam (OpenCV) |
| Resolution | Rendered at `IMAGE_W x IMAGE_H` (1456x1088) from satellite map | IMX296 native 1456x1088 via CSI-2 |
| Target appearance | `dummy.png` alpha-composited at altitude-correct scale | Real mannequin on real ground |
| Background | Satellite map texture (grass, paths, shadows from photo) | Real terrain, real-time lighting |
| **Report coverage** | **YES** -- 09_simulation.tex L88-98, mission_flow.tex L247-250 |

### 2. AI Backend
| Aspect | SIMULATION (laptop) | REAL (Pi 5) |
|--------|-------------------|-------------|
| Backend priority | NCNN > Ultralytics (skipped for .tflite) > TFLite | NCNN > TFLite (no Ultralytics installed) |
| Model file | Same `best.tflite` (11.7MB float32) | Same `best.tflite` |
| Input shape | Identical: [1, 640, 640, 3] | Identical |
| Inference speed | ~30ms (laptop GPU/CPU) | ~207ms TFLite / ~72ms NCNN (Pi 5 CPU) |
| FPS | ~30+ FPS | ~4.8 FPS (TFLite) / ~9 FPS (NCNN) |
| **Report coverage** | **YES** -- 09_simulation.tex L135 (same model weights), evaluation.tex D2 (inference rate), cv_extended.tex |

### 3. Connection
| Aspect | SIMULATION | REAL |
|--------|-----------|------|
| Target | SITL via `tcp:127.0.0.1:5762` | Cube via mavproxy `udpin:0.0.0.0:14550` |
| Auto-detection | `config.py` checks serial ports; none found = localhost | Serial port found = UDP bridge |
| Firmware | ArduPilot SITL (same C++ code as Cube) | ArduPilot on Cube Orange+ |
| Latency | Near-zero (localhost) | ~1-5ms (UART + UDP) |
| **Report coverage** | **YES** -- 09_simulation.tex L84, mission_flow.tex L251 |

### 4. GPS Accuracy
| Aspect | SIMULATION | REAL |
|--------|-----------|------|
| Noise level | ~0.5m (SITL default) | ~2-3m CEP (real GPS receiver) |
| Multipath | None | Buildings, terrain, trees |
| Timing lag | None in SITL; discoverable via DJI video replay | 100-200ms (Here3+ receiver) |
| Fix quality | Always 3D fix, high sat count | Weather/obstruction dependent |
| Mitigation | `--noise` flag injects ~2.8m CEP Gaussian noise | N/A (real conditions) |
| **Report coverage** | **YES** -- simulation_validation.tex L125 (SITL GPS optimistic), L29 table row, 09_simulation.tex L86 |

### 5. Wind and Turbulence
| Aspect | SIMULATION | REAL |
|--------|-----------|------|
| Wind model | SITL has wind parameters but not typically used | Real weather |
| Effect on flight | Minimal: SITL vehicle dynamics are simplified | Position drift, attitude changes, vibration |
| Effect on detection | None (synthetic frames are sharp) | Motion blur, camera shake, position error |
| Mitigation | `--blur`, `--shake`, `--noise` flags approximate effects | N/A |
| **Report coverage** | **YES** -- simulation_validation.tex L121-122 (wind is untestable), L123-124 (motion blur gap) |

### 6. Detection Target
| Aspect | SIMULATION | REAL |
|--------|-----------|------|
| Target | `dummy.png` composited on satellite map at correct scale | Physical mannequin on ground |
| Lighting | Static (from satellite photo capture time) | Dynamic (sun angle, shadows, clouds) |
| Pose/appearance | Single fixed image, always same orientation | May vary (posed differently, clothing, occlusion) |
| Background contrast | Known from satellite photo | Unpredictable (similar-coloured objects, debris) |
| **Report coverage** | **YES** -- simulation_validation.tex L27-28 table (real lighting/texture = "---" for sim), L59-61 (DJI 87% vs 100% synthetic) |

### 7. Timing and Loop Rate
| Aspect | SIMULATION | REAL |
|--------|-----------|------|
| Main loop | ~20-50 Hz (limited by rendering) | ~4.8 Hz (limited by TFLite inference) |
| Frame availability | Always available (rendered on demand) | Camera capture rate; may drop frames |
| State transitions | Instantaneous telemetry | ~100ms telemetry update rate |
| **Report coverage** | **PARTIAL** -- inference FPS is covered, but main loop rate difference not explicitly stated |

### 8. Disarm Recovery Behaviour
| Aspect | SIMULATION | REAL |
|--------|-----------|------|
| Unexpected disarm during takeoff | Re-enters ARMING, retries (SITL nuisance) | Terminates mission in DONE (genuine fault) |
| **Report coverage** | **YES** -- mission_flow.tex L253 |

### 9. Sensor Degradation Flags (Sim-only bridging)
| Flag | Effect | Report Coverage |
|------|--------|----------------|
| `--sim-tilt` | Perspective camera warp from SITL pitch/roll + ray-trace GPS correction | **YES** -- 09_simulation.tex L100-104 |
| `--blur F` | Directional motion blur (speed + yaw rate) | **YES** -- 09_simulation.tex L111 |
| `--shake N` | Random pixel offset per frame (vibration) | **YES** -- 09_simulation.tex L112 |
| `--noise L` | GPS/altitude/attitude Gaussian noise | **YES** -- 09_simulation.tex L113, mission_flow.tex L257 |
| `--compensate-tilt` | Ray-trace GPS correction for real camera tilt | **YES** -- gps_estimation_deep.tex L645-649 |

---

## Part 2: Report Honesty Assessment

### Q1: Does the report honestly acknowledge all sim-to-real gaps?
**YES.** The report is remarkably thorough and honest:
- `simulation_validation.tex` Section "Known Sim-to-Real Gaps" (L116-130) explicitly lists: wind/turbulence, motion blur at speed, real GPS accuracy, RF interference/MAVLink dropouts, sunlight/thermal effects.
- Table `tab:sim-val-matrix` (L10-33) uses checkmark / tilde / dash to show what each sim level validates vs cannot test.
- Table `tab:sim-val-results` (L77-90) directly compares sim results (100% detection, <0.5m GPS) vs real/video results (87% detection, 2.3m CEP).
- The "Confidence Assessment" section (L133-141) categorises properties into High / Moderate / Low confidence tiers.

### Q2: Does it claim sim results are equivalent to real results?
**NO.** The report consistently frames simulation as a complement, not a replacement:
- "Detection reliability is the primary gap" (09_simulation.tex L144)
- "SITL GPS noise (~0.5m) is optimistic relative to real conditions (~2-3m)" (L86)
- "Wind effects on flight stability...cannot be reproduced at Levels 1-2" (L144)
- The 87% vs 100% detection rate is presented as a "~13 percentage-point sim-to-real gap" (simulation_validation.tex L74)
- Offset landing accuracy: "Not yet flight-tested" (table row)

### Q3: Does it explain which results transfer and which don't?
**YES.** Sections "What Transfers Well" (09_simulation.tex L139-140) and "Known Sim-to-Real Gaps" (L142-144) directly address this. The simulation_validation.tex section provides even more granular coverage.

### Q4: Are --sim-tilt, --blur, --shake improvements mentioned as bridging the gap?
**YES.** All three are documented:
- 09_simulation.tex L100-116 (Perspective Camera Rendering + Configurable Sensor Degradation)
- simulation_validation.tex L123 explicitly calls them "approximations"
- gps_estimation_deep.tex covers --sim-tilt and --compensate-tilt extensively with equations and scatter plots

### Q5: Is there a clear "what we can't test in simulation" section?
**YES.** simulation_validation.tex L116-130 "Known Sim-to-Real Gaps" is exactly this, with 5 bullet points. Additionally, the Confidence Assessment (L133-141) categorises "Low confidence" items as those that only real flight can validate.

---

## Part 3: Recent Code Improvements -- Report Coverage Check

| Feature | In Code | In Report | Notes |
|---------|---------|-----------|-------|
| `--sim-tilt` (perspective camera) | main.py L52, simulation.py L335-546 | 09_simulation.tex L100-104 | Fully covered with equations |
| `--blur` (motion blur) | main.py L54, L674-712 | 09_simulation.tex L111 | Covered including kernel orientation |
| `--shake` (vibration) | main.py L49, L669-673 | 09_simulation.tex L112 | Covered |
| `--noise` (GPS/attitude noise) | main.py L55, L508-518 | 09_simulation.tex L113, mission_flow.tex L257 | Covered |
| `--compensate-tilt` (R matrix GPS correction) | main.py L53, L567-620 | gps_estimation_deep.tex L596-649 | Extensively covered with math, scatter plots |
| God view optimization | simulation.py L29-39 | Not explicitly mentioned in report | Not needed -- internal perf optimization, not user-facing |
| 5-layer geofence | geofence.py, config.py L122-131 | mission_flow.tex L219-228, 13_safety_risk.tex | Fully covered, all 5 layers listed |
| SMART detection (`--smart-detect`) | main.py L42 | mission_flow.tex L99, 06_state_machine.tex | Covered as consecutive-frame confirmation |
| Four-phase detection flow | state_machine.py | 06_state_machine.tex, mission_flow.tex | Covered across state descriptions |
| Two-step centering (tilt compensation) | state_machine.py CENTERING state | mission_flow.tex L138-139 | Covered including 3s hover |
| Lock-yaw (`--lock-yaw`) | main.py L46, config.py L174 | Not explicitly mentioned in report | **GAP** -- minor feature, but worth a sentence |
| Stream server + browser UI | stream_server.py, port 8090 | mission_flow.tex L14, system_description.tex L7, 08_ground_station.tex | Fully covered |
| Multi-class SAR_NAMES | vision.py L32 | evaluation.tex D6 acknowledges single-class limitation | Covered as limitation + future work |

### Missing from Report (minor):
1. **`--lock-yaw` flag**: Maintains search heading through sweep turns. Not mentioned in any report section. Low priority since it's a minor operational flag.
2. **God view optimization**: Internal rendering optimization (63MB -> 4MB per frame). Not report-worthy -- purely internal.
3. **Main loop rate difference**: The report mentions inference FPS (4.8 on Pi) but doesn't explicitly state that the main loop runs at different rates in sim vs real. This is implicit but could be clearer.

---

## Part 4: Framing Assessment

The report correctly frames simulation results as:

1. **"The simulation demonstrates the complete mission logic end-to-end"** -- YES, 09_simulation.tex L2-3 and simulation_validation.tex throughout.

2. **"The same code runs on both platforms -- only the camera source and AI backend change"** -- YES, 09_simulation.tex L128-136 (three mechanisms), mission_flow.tex L248-255 (explicit 3-point list).

3. **"Sensor degradation flags bridge key sim-to-real gaps"** -- YES, 09_simulation.tex L106-116, but the report is honest that these are "approximations" (simulation_validation.tex L123).

4. **"Known gaps that only real flight can validate: [list]"** -- YES, simulation_validation.tex L117-130 provides this exact list.

---

## Part 5: Overall Verdict

**The D6 goldmine report is HONEST and THOROUGH in its presentation of simulation vs real mission differences.**

Specific strengths:
- The validation coverage matrix (Table sim-val-matrix) is excellent -- transparent about what each level can/cannot test
- The quantitative comparison table (sim-val-results) directly juxtaposes sim vs real numbers without hiding the gaps
- The "Known Sim-to-Real Gaps" section is comprehensive and specific
- The confidence tiering (High/Moderate/Low) is a mature engineering assessment
- The "Lessons from Sim-to-Real Transfer" section provides genuine insight rather than hand-waving
- The progressive build-up narrative (Phase 1-5) shows the rationale, not just the result
- The bugs-caught-in-simulation section (L147-157) provides concrete evidence of simulation value

The only substantive gap is:
- **`--lock-yaw` not mentioned** -- very minor, one sentence would suffice
- **Main loop rate asymmetry not explicitly stated** -- the reader can infer this from the FPS numbers, but a sentence in the sim-vs-real comparison (mission_flow.tex L245-255) would make it explicit

**No corrections needed to claims or framing.** The report does not overclaim simulation fidelity and is transparent about what remains unvalidated. This is exactly the right approach for a project that did not achieve outdoor flight.

---

## Recommendations (optional polish)

1. Add one sentence about `--lock-yaw` to the search phase description in mission_flow.tex (currently L75: "the drone optionally aligns its yaw to the scan-line direction").
2. Consider adding a sentence to the sim-vs-real comparison (mission_flow.tex L245-255) noting the main loop rate difference: "In simulation, the main loop runs at 20-50 Hz; on the Pi, inference-limited throughput reduces this to approximately 5 Hz, meaning each state handler executes less frequently."
3. Both are minor and purely for completeness -- the report passes a thorough honesty check as-is.
