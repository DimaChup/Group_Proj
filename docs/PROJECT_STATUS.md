# Project Status Summary

> Generated 2026-04-03. Source: `dashboard/src/pages/mission-data.ts`, `wbs-data.ts`, `group-project-v2-data.ts`, `LevelsTab.tsx`, `GroupProjectV2Tab.tsx`.

---

## 1. The Three Levels

The project is structured as three product levels, each a working, demonstrable system. If we only achieve L1, we still have something useful. L2 is the target. L3 is a stretch.

| Level | Name | Autonomy | What It Achieves |
|-------|------|----------|-----------------|
| **L1** | Manual MVP | None -- pilot flies everything | Pilot flies RC manually. Pi runs camera + AI passively (zero commands). Detection overlay on video stream, buzzer alerts, geotagged detection images saved. Pilot manually flies to target and lands. |
| **L2** | Semi-Autonomous | Partial -- drone flies, pilot confirms | Drone arms, takes off, flies lawnmower search avoiding SSSI. CV detects targets, pilot classifies (Y/I/X). On confirm: drone centres, descends, lands at 7.5m offset, releases payload. Pilot has RC override at all times. |
| **L3** | Full Autonomous | Full -- drone decides, pilot monitors | Everything from L2, but confidence accumulation replaces pilot confirmation. Multi-pass verification at decreasing altitude. Drone auto-decides to investigate and land. Pilot intervenes only if needed. |

### State Flows

- **L1**: `MANUAL FLIGHT -> Pi observes -> Detection overlay -> Pilot decides -> Manual land`
- **L2**: `ARM -> TAKEOFF -> SEARCH (avoid SSSI) -> DETECT -> pilot N -> INVESTIGATE -> pilot Y -> CENTRE -> DESCEND -> pilot L -> LAND (7.5m offset) + PAYLOAD -> RTL`
- **L3**: `ARM -> TAKEOFF -> SEARCH -> AUTO-DETECT -> AUTO-VERIFY (multi-pass) -> AUTO-LAND + PAYLOAD -> RTL`

### Key Scripts Per Level

| Level | Scripts |
|-------|---------|
| L1 | `tests/flight/1_passive_flight.py`, `tests/diagnostics/camera_stream.py` |
| L2 | `main.py` (state machine), `pi_flight.py` (browser dashboard), `simple_simulator.py` (laptop sim) |
| L3 | `main.py` with auto-confirm flag (not yet implemented) |

---

## 2. L2 Stepping Stones

L2 has a 13-step critical path organized into 12 rows, with 3 milestones. Steps on the same row can run in parallel.

### Critical Path (1/13 done)

| Row | Step | Status | What It Proves |
|-----|------|--------|----------------|
| 1 | All components healthy | **DONE** | Every subsystem talks to every other subsystem |
| 2 | Outdoor GPS 3D fix | TODO | GPS works outdoors, real coordinates available |
| 3 | Mission Planner AUTO waypoints | TODO | Aircraft flies, GPS nav works, RC kill switch reliable |
| 4 | Manual flight + CV check | TODO | CV works from the air (not just bench) |
| 4 | Fly GPS waypoints + RC override | TODO | MAVLink commands make drone fly to GPS coords |
| 5 | Geotagging from flyover | TODO | Pixel-to-GPS conversion accuracy from moving flyover |
| 5 | CV centering accuracy | TODO | Visual servo centering works in real flight |
| 5 | Test geofence standalone | TODO | ArduCopter exclusion fence prevents SSSI entry |
| 6 | Fly search pattern (no CV action) | TODO | Autonomous lawnmower pattern works in the real world |
| 7 | Search + detect + confirm (Y/X) | TODO | Core detect-investigate-confirm loop works |
| 8 | Offset landing + payload delivery | TODO | R07 compliance -- payload in 5-10m zone |
| 9 | PLB focused search redirect | TODO | R06 compliance -- drone redirects to Focus Area |
| 10 | Items of interest (Y/I/X) | TODO | Full classification workflow, IOI logged with GPS |
| 11 | SSSI geofence in search | TODO | R02 compliance in full search mission |
| 12 | Full L2 mission | TODO | All requirements (R01-R12) in a single flight |

### Milestones

| After Row | Milestone | Status |
|-----------|-----------|--------|
| 2 | All components working and talking | Partially met (bench only, no outdoor GPS) |
| 5 | Can reliably geotag a dummy from the air | Not started |
| 8 | Can find, confirm, and deliver to a target | Not started |

### Parallel Tasks (5/19 done)

| Category | Done | Remaining |
|----------|------|-----------|
| Calibration | 2/3 | Real-altitude FOV verification |
| Accuracy | 0/4 | GPS noise floor, GPS hover drift, GPS estimation error, rangefinder accuracy, battery endurance |
| Tuning | 1/7 | Altitude sweep, speed sweep, model compare, confidence threshold, NCNN backend, resolution tradeoff |
| Data | 2/5 | Stream latency, comms range |

**Done parallel tasks**: FOV calibration, lens distortion calibration, Pi inference benchmark, training data capture, model retraining (sar_v2_1088).

---

## 3. WBS Completion by Subsystem

Total: 121 nodes across 7 subsystems.

| # | Subsystem | Done | Total | % | Active | Upcoming |
|---|-----------|------|-------|---|--------|----------|
| 1 | Hardware Platform | 13 | 20 | 65% | 3 | 4 |
| 2 | Sensing & Perception | 14 | 16 | **87%** | 1 | 1 |
| 3 | Communications | 9 | 14 | 64% | 5 | 0 |
| 4 | Compute & Processing | 6 | 15 | 40% | 3 | 6 |
| 5 | Software & Autonomy | 12 | 24 | 50% | 5 | 7 |
| 6 | Ground Control Station | 10 | 14 | **71%** | 4 | 0 |
| 7 | Integration & Testing | 3 | 17 | **17%** | 3 | 11 |

**Strongest**: Sensing & Perception (87%) -- camera, CV pipeline, model training all done.
**Weakest**: Integration & Testing (17%) -- no real flights yet, no system-level validation.

### Deliverables Timeline

| ID | Deliverable | Weight | Status |
|----|-------------|--------|--------|
| D1 | Group Contract | 2.5% | DONE |
| D2 | Preliminary Design Review | 10% | DONE |
| D3 | Critical Design Review | 15% | DONE |
| D4 | Flight Readiness Review | 10% | ACTIVE |
| D5 | Flight Test | 20% | UPCOMING |
| D6 | Final Report | 30% | UPCOMING |
| D7 | Peer Assessment | 12.5% | UPCOMING |

27.5% of marks secured (D1+D2+D3). 72.5% remaining (D4+D5+D6+D7).

---

## 4. Critical Path Items

The critical path to achieving L2 at the flight test runs through these blockers:

1. **Outdoor GPS 3D fix** (Row 2) -- All flight testing is blocked until GPS is verified outdoors. This is the single gate to every subsequent step.

2. **Mission Planner AUTO waypoints** (Row 3) -- First real flight, no custom code. Proves the aircraft flies safely. Blocks all code-controlled flights.

3. **Manual flight + CV check** (Row 4) -- Validates that CV actually detects from altitude (not just bench). If detection fails above 15m, TARGET_ALT must be lowered. Blocks all autonomous detection steps.

4. **Fly GPS waypoints** (Row 4, parallel) -- Proves MAVLink GUIDED commands work. Blocks autonomous search pattern.

5. **Search + detect + confirm** (Row 7) -- The core semi-autonomous loop. Everything before this is building blocks; this is where L2 becomes real.

6. **Offset landing + payload** (Row 8) -- R07 compliance. Without this, the drone finds but cannot deliver.

### Minimum Viable L2 (if time is short)

If only a subset of L2 can be demonstrated, the highest-value items are:
- Autonomous search pattern (Row 6)
- Detection + pilot confirm (Row 7)
- Offset landing (Row 8)

SSSI geofence (Row 11), PLB redirect (Row 9), and items of interest (Row 10) can be dropped and still demonstrate core semi-autonomous SAR capability.

---

## 5. Passive Detection Workflow (Colleague's Role)

The passive detection workflow is `passive_watch.py` (and `tests/flight/1_passive_flight.py`). This is the **L1 (Manual MVP)** product:

- Pi runs camera + AI model continuously
- Detections overlaid on MJPEG stream at `http://PI_IP:8090`
- Detection images saved with GPS metadata
- Buzzer beeps on detection
- **Zero commands sent to the drone** -- completely safe

**Where it fits in the levels**:
- It IS Level 1 -- the minimum viable product
- It is also L2 Critical Path Step 3 (Row 4: "Manual flight + CV check") -- the step where we validate that CV works from real altitude
- Results from passive flights (detection rate, max altitude, false positive rate) directly inform L2 config values (TARGET_ALT, CONFIDENCE_THRESHOLD, SEARCH_SPEED_MPS)

**Current state**: `passive_watch.py` has been tested on Pi bench with real camera. It has `--simple-names` mode for clean filenames with GPS, `--class-filter` for model-specific filtering, and saves detection photos + JSON metadata. Bug fixes applied (GPS estimate normalisation, TFLite bbox coords, double-scaling). Ready for outdoor flight test.

**What the colleague needs to do**:
1. Fly the drone manually over the dummy at various altitudes (10m, 15m, 20m, 25m, 30m)
2. Run `passive_watch.py --headless --stream` on Pi during flight
3. Review saved detection images and CSV log after landing
4. Report: max detection altitude, detection rate per altitude, false positive count
5. This data directly determines whether L2 search altitude (currently 30m) needs to be lowered

---

## 6. Where We Are Now

### Achieved
- Full simulation works end-to-end on laptop (SITL + state machine + CV)
- Pi hardware verified: camera, AI inference (4.8 FPS), Cube connection, mavproxy bridge
- Retrained model (sar_v2_1088) with mAP50=0.995 on real+synthetic data
- Browser ground station (pi_flight.py) tested in simulation
- Geofence, safety failsafes, RC override all implemented in code
- FOV and lens calibrated on bench
- 3 out of 7 deliverables submitted (27.5% of marks)

### Not Yet Achieved
- No outdoor GPS fix test
- No real flights at all -- zero airborne testing
- No validation that CV detects from altitude (only bench-tested)
- Payload release mechanism not integrated
- PLB redirect not implemented end-to-end
- Integration & Testing subsystem at 17%

### Gap Analysis

| Level | Gap to Achievement | Effort Estimate |
|-------|-------------------|-----------------|
| **L1** | Outdoor GPS fix + one manual flight with passive CV running. Smallest gap. | 1 flight day |
| **L2** | 12/13 critical path steps remaining. Need GPS fix, multiple progressive flights, payload integration, geofence validation, PLB redirect. | 2-3 flight days minimum |
| **L3** | Everything from L2 plus autonomous verification logic and extensive threshold calibration. Not realistic without L2 working first. | Not feasible in current timeline |

### Realistic Target

**L1 is achievable in one good flight day.** This gives a working demonstrable product (passive detection during manual flight) and collects the data needed for L2.

**Partial L2** (search + detect + confirm + land, without PLB/SSSI/IOI) is achievable in 2-3 flight days if L1 data shows CV works from altitude. The minimum viable L2 demonstration is: autonomous search pattern, detection, pilot confirmation, offset landing.

**Full L2** (all 13 steps including PLB redirect, SSSI geofence, items of interest, payload delivery) requires significant flight testing time and iterative tuning.

---

## 7. Recommended Next Actions (Priority Order)

1. **Get outdoors and verify GPS** (Critical Path Step 2) -- everything else is blocked
2. **Fly Mission Planner AUTO waypoints** (Step 3) -- prove the aircraft flies
3. **Manual flight with passive_watch.py** (Step 4, L1) -- prove CV works from altitude
4. **Fly GPS waypoints with code** (Step 4) -- prove MAVLink GUIDED works
5. **Wire and test Tarot payload servo** (parallel) -- can be done on bench while waiting for weather
6. **Review detection data from Step 3** -- set TARGET_ALT and CONFIDENCE_THRESHOLD based on real results
