# Needs vs Capabilities — Objective Scoring Matrix

> Generated 2026-04-03. Honest assessment of simulation vs real hardware readiness.
>
> **Scoring**: 0 = not started, 1-3 = partially implemented, 4-6 = works with caveats,
> 7-9 = works reliably, 10 = proven and validated.

---

## Scoring Matrix

| Req | Requirement | Sim | Real | Evidence | Gap | Priority |
|-----|-------------|:---:|:----:|----------|-----|:--------:|
| R01 | Autonomous takeoff | **9** | **2** | SITL: main.py arms + takes off to TARGET_ALT reliably. Pi: Cube connection verified on bench, arm command sent, but zero real takeoffs attempted. | No outdoor GPS fix test. No real arming/takeoff ever performed. DISARM_DELAY param must be set to 0. | CRITICAL |
| R02 | Search pattern coverage | **9** | **1** | SITL: planning.py generates lawnmower pattern from polygon, main.py flies it end-to-end. Dry-run verified. | Never flown a search pattern on real hardware. GPS waypoint following untested in air. Strip spacing and coverage efficiency unvalidated outdoors. | CRITICAL |
| R03 | AI target detection | **8** | **3** | SITL: Ultralytics detects dummy in simulated camera. Pi bench: TFLite detects at 0.966 conf, 4.8 FPS (benchmark.py, 50 runs). Retrained model mAP50=0.995 on synthetic+real data. | Never tested detection from altitude in real flight. Detection range vs altitude unknown. Motion blur impact unknown. False positive rate in real outdoor conditions unknown. | CRITICAL |
| R04 | Target centering & descent | **8** | **0** | SITL: state machine transitions CENTERING -> DESCENDING -> VERIFY work. simple_simulator.py: visual servo (V key) + GPS centering (C key) tested end-to-end. | Zero real-world centering or descent tests. Visual servo accuracy at real altitudes unvalidated. Wind disturbance effects on centering unknown. | HIGH |
| R05 | Operator verification | **8** | **2** | SITL: VERIFY state presents Y/N choice in terminal + browser buttons. pi_flight.py browser dashboard tested in simulation. Headless mode works over SSH. | Browser dashboard untested during actual flight. Stream latency in field unknown. Operator workflow under pressure not rehearsed. | MEDIUM |
| R06 | Offset landing | **7** | **0** | SITL: 7.5m offset landing logic implemented (center of 5-10m zone). simple_simulator.py: GPS lock -> offset landing tested. | Zero real landings. GPS accuracy for offset positioning unvalidated. No rangefinder for AGL altitude. Payload release (Tarot servo) not integrated. | HIGH |
| R07 | GPS accuracy (<5m) | **6** | **1** | SITL: GPS estimation uses spatial clustering + inverse variance weighting + Kalman filter. DJI video analysis: CEP50=2.3m but max=16.5m scatter. Known 100-200ms GPS timing lag at 5m/s. | No real GPS accuracy measurement. No ground truth calibration done outdoors. GPS drift/noise floor unmeasured in real conditions. Focal length calibration needed for Pi camera at altitude. | HIGH |
| R08 | Real-time video stream | **7** | **4** | SITL: MJPEG stream at :8090 works in pi_flight.py and passive_watch.py. Pi bench: stream tested over WiFi. Threaded inference keeps stream responsive. | Stream latency and reliability at operational distance (100m+ WiFi) untested. Frame rate drops during inference. No H.264/low-latency stream option deployed. | MEDIUM |
| R09 | Safety (RC override, geofence, RTL) | **8** | **3** | SITL: RC override guard stops all commands when pilot takes over. SSSI geofence active. RTL on link loss / low battery configured. ArduCopter failsafes set. Pi: RC failsafe and battery failsafe configured in Cube params. | Geofence never tested in flight. RC override -> resume flow untested in air. RTL accuracy and behavior at field site unknown. Kill switch tested on bench only. | CRITICAL |
| R10 | Headless operation (Pi) | **7** | **5** | main.py --headless flag auto-detects on Pi. Terminal input works over PuTTY/SSH. Browser buttons at :8090. passive_watch.py fully headless. Pi bench: all scripts run headless. | No auto-start on boot (systemd service not configured). No watchdog timer. mavproxy must be started manually. WiFi reliability for SSH in field untested. | LOW |

---

## Summary Scores

| Category | Simulation Average | Real Hardware Average |
|----------|:-----------------:|:--------------------:|
| All requirements | **7.7 / 10** | **2.1 / 10** |
| Flight-critical (R01, R02, R03, R04, R09) | **8.4 / 10** | **1.8 / 10** |
| Mission-critical (R05, R06, R07) | **7.0 / 10** | **1.0 / 10** |
| Infrastructure (R08, R10) | **7.0 / 10** | **4.5 / 10** |

---

## Key Observations

### What simulation proves
- The state machine logic is sound and handles all transitions correctly.
- The lawnmower search pattern generator works for arbitrary polygons.
- The CV pipeline detects targets and feeds the decision loop.
- Safety logic (RC override, geofence, RTL) is implemented and tested.
- The GPS estimation math (clustering, Kalman, inverse variance) is coded and produces reasonable results.

### What simulation cannot prove
- Whether the drone actually flies (motor/ESC/PID response in real air).
- Whether CV detects a dummy from 15-30m altitude outdoors with real lighting, shadows, and backgrounds.
- Whether GPS accuracy is sufficient for offset landing in the 5-10m zone.
- Whether the video stream is usable at operational WiFi range.
- Whether the RC override -> autonomous resume flow is safe under real conditions.
- Whether the geofence actually prevents SSSI entry during a real search pattern.

### The simulation-to-reality gap
The project has a **5.6-point gap** between simulation (7.7) and real hardware (2.1). This is the largest risk. The code is mature, but zero minutes of real flight time have been logged. Every flight-critical requirement has a real-hardware score below 3.

### Honest assessment
- **L1 (Manual MVP)** is closest to achievable: it only needs outdoor GPS + one manual flight with passive_watch.py running. Real hardware score for L1-relevant items (R03, R08, R10) averages ~4.0.
- **L2 (Semi-Autonomous)** requires all 10 requirements to score 7+ on real hardware. Current real average is 2.1. Multiple progressive flight days are needed.
- **L3 (Full Autonomous)** is not feasible without L2 working first.

---

## Priority Actions to Close Gaps

| Priority | Action | Closes gap for | Effort |
|----------|--------|---------------|--------|
| 1 | Outdoor GPS fix test | R01, R02, R07, R09 | 1 hour |
| 2 | Mission Planner AUTO waypoints (no custom code) | R01, R02, R09 | 1 flight |
| 3 | Manual flight + passive_watch.py | R03, R08 | 1 flight |
| 4 | Fly GPS waypoints with code (2_waypoint_test.py) | R01, R02, R04 | 1 flight |
| 5 | Search pattern flight (CV logs only, no action) | R02, R03, R07 | 1 flight |
| 6 | Full detect + confirm + offset land | R04, R05, R06, R07 | 1-2 flights |
| 7 | Payload servo integration + test | R06 | Bench + 1 flight |

Each step builds on the previous. Never skip a step.

---

## Requirement Traceability

| Req | Brief Requirement (AENGM0074) | Code Location | Test Script |
|-----|-------------------------------|---------------|-------------|
| R01 | Autonomous takeoff from TOL | main.py (ARMING/TAKEOFF states) | tests/flight/0b_bench_mission.py |
| R02 | Search area coverage, avoid SSSI | planning.py, config.py (SSSI_GPS) | tests/flight/0d_planning_test.py, 0e_geofence_test.py |
| R03 | AI target detection | vision.py, best.tflite | tests/hardware/benchmark.py, tests/laptop/test_cv.py |
| R04 | Centering and descent | main.py (CENTERING/DESCENDING) | tests/flight/4_detect_and_center.py |
| R05 | Operator Y/N verification | main.py (VERIFY state), pi_flight.py | tests/flight/3_auto_detect.py |
| R06 | Offset landing + payload | main.py (APPROACH/LANDING) | tests/flight/0f_servo_test.py |
| R07 | GPS accuracy <5m | utils.py (GeoTransformer), GPS estimation | tests/calibration/gps_estimate_calibrate.py |
| R08 | Real-time video stream | passive_watch.py, pi_flight.py (:8090) | tests/diagnostics/camera_stream.py |
| R09 | Safety: RC override, geofence, RTL | main.py (RC guard), config.py (geofence) | tests/flight/0e_geofence_test.py |
| R10 | Headless Pi operation | main.py --headless, passive_watch.py | (manual SSH test) |
