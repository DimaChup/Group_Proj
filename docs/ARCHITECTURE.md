# System Architecture

## The Goal

### Minimum Viable Mission (build this first)

1. Drone takes off autonomously
2. Flies a lawnmower search pattern over a defined area
3. Camera + AI detects a dummy/casualty on the ground
4. Drone centres on target, descends, operator confirms Y/N over SSH
5. On Y: lands near the target. On N: resumes search
6. Operator monitors on Mission Planner throughout

### Future Enhancements (after minimum works reliably)

- PLB focused search (narrow area after beacon signal)
- Multi-frame confirmation (reduce false positives)
- Auto-confirm at high confidence (skip Y/N)
- Detection image sent to ground station before Y/N
- Multiple target support

---

## How the System Evolves

We don't build the final system all at once. Each phase adds ONE new thing, and we test it before moving on.

### Phase 0: Laptop Only -- Prove the Logic

Everything runs on your laptop. No hardware needed.

```
┌──────────────────────────────────────────┐
│              YOUR LAPTOP                 │
│                                          │
│  simulation.py                           │
│    ├── map.jpg (simulated terrain)       │
│    ├── vision.py (Ultralytics YOLO)      │
│    ├── planning.py (lawnmower pattern)   │
│    └── main.py (state machine)           │
│              │                           │
│              v                           │
│    SITL (simulated flight controller)    │
│              │                           │
│              v                           │
│    Mission Planner (map display)         │
└──────────────────────────────────────────┘
```

**What you're testing**: Does the search pattern work? Does AI detect the dummy? Does the state machine flow correctly?

**What runs where**: Everything on laptop. Camera is simulated (crops from map.jpg). Flight controller is simulated (SITL).

---

### Phase 1: Pi + Camera -- Prove Vision Works on Real Hardware

Pi has camera and AI model. No Cube, no flying.

```
┌──────────────────────────────────────┐
│         RASPBERRY PI                  │
│                                       │
│  [Camera] --CSI--> vision.py          │
│                      │                │
│                      v                │
│              best.tflite (TFLite)     │
│                      │                │
│                      v                │
│           (found, x, y, conf)         │
│                                       │
│  Test: pi_1, pi_2, pi_3, pi_8, pi_9  │
└──────────────────────────────────────┘
```

**What you're testing**: Does the real camera capture frames? Does AI detect a dummy printout? How fast is inference?

**What runs where**: Only Pi. No Cube, no flight controller, no ground station.

---

### Phase 2: Pi + Camera + Cube -- Prove They Talk to Each Other

Add the Cube (wired on the bench). Still no flying.

```
┌──────────────────────────────────────┐     ┌─────────────┐
│         RASPBERRY PI                  │     │    CUBE      │
│                                       │     │             │
│  [Camera] --CSI--> vision.py          │     │  GPS        │
│                      │                │     │  IMU        │
│                      v                │     │  Buzzer     │
│           (found, x, y, conf)         │     │             │
│                      │                │     │             │
│                      v                │     │             │
│              pi_4_detect_and_log.py ──UART──>  reads yaw  │
│              (guidance + buzzer)       │     │  beeps      │
│                                       │     │             │
└──────────────────────────────────────┘     └─────────────┘
                │
                v
        detection_log.csv
```

**What you're testing**: Carry drone by hand over dummy. Does vision detect? Does Cube report yaw/GPS? Does buzzer beep? Do guidance commands make sense?

**What runs where**: Pi runs vision + guidance. Cube provides telemetry. No flying.

---

### Phase 3: First Flight (Manual RC) -- Calibrate with Real Data

Pilot flies with RC controller. Pi runs detection passively. No autonomous commands.

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   CAMERA    │     │     PI      │     │    CUBE     │
│             │     │             │     │             │
│  Real       │CSI  │ vision.py   │UART │ Flight      │
│  aerial     ├────>│ (detect)    ├────>│ controller  │
│  frames     │     │             │<────┤ (GPS, yaw)  │
│             │     │ pi_2_detect │     │             │
│             │     │ (logging)   │     │  Telemetry  │
└─────────────┘     └──────┬──────┘     │  radio      │
                           │            └──────┬──────┘
                      WiFi (SSH)               │
                           │            Telemetry radio
                           v                   v
                    ┌──────────────────────────────┐
                    │     GROUND STATION (laptop)   │
                    │                               │
                    │  SSH terminal (see detections) │
                    │  Mission Planner (see flight)  │
                    │                               │
                    │  RC Controller (pilot flies)   │
                    └──────────────────────────────┘
```

**What you're testing**: At what altitude does AI detect the dummy? What's the real camera FOV? Does detection work from the air?

**What runs where**: Pi runs vision. Cube handles flight (controlled by pilot via RC). Laptop monitors via Mission Planner + SSH. No autonomous commands from Pi to Cube.

---

### Phase 4: Ground Test (No Props) -- Prove Autonomous Logic

Run the full main.py connected to real Cube. Props OFF. Verify commands are correct.

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   CAMERA    │     │     PI      │     │    CUBE     │
│             │     │             │     │             │
│  Real       │CSI  │ vision.py   │UART │ Flight      │
│  frames     ├────>│ planning.py ├────>│ controller  │
│             │     │ main.py     │<────┤ (GPS, yaw)  │
│             │     │             │     │             │
│             │     │ State:      │     │ Receives:   │
│             │     │  SEARCH     │     │  ARM cmd    │
│             │     │  CENTERING  │     │  GOTO cmds  │
│             │     │  DESCENDING │     │  LAND cmd   │
│             │     │  VERIFY     │     │             │
└─────────────┘     └──────┬──────┘     └──────┬──────┘
                           │                    │
                      WiFi (SSH)         Telemetry radio
                           │                    │
                           v                    v
                    ┌──────────────────────────────┐
                    │     GROUND STATION (laptop)   │
                    │                               │
                    │  SSH: run main.py, press Y/N   │
                    │  MP: see commands being sent    │
                    │                               │
                    │  NO PROPS! Just verify logic.  │
                    └──────────────────────────────┘
```

**What you're testing**: Does main.py arm, send waypoints, detect, centre, descend, prompt Y/N? Does Mission Planner show the commands? Does kill switch work?

**What runs where**: Pi runs full main.py. Cube receives real MAVLink commands but motors don't spin (no props). Operator monitors and confirms.

---

### Phase 5: Full Autonomous Flight -- The Final System

Everything connected. Props on. Pilot ready with RC override.

```
                         [RC Controller]
                              │
                         (kill switch)
                              │
┌─────────────┐     ┌────────v──────┐     ┌─────────────┐
│   CAMERA    │     │      PI       │     │    CUBE     │
│             │     │               │     │             │
│  Aerial     │CSI  │  vision.py    │UART │  Autopilot  │
│  video      ├────>│  planning.py  ├────>│  Motors     │
│  frames     │     │  main.py      │<────┤  GPS + IMU  │
│             │     │  states.py    │     │  Safety     │
│             │     │               │     │             │
│  Detects    │     │  AI decides   │     │  Flies the  │
│  casualty   │     │  where to fly │     │  drone      │
└─────────────┘     └──────┬──────┘     └──────┬──────┘
                           │                    │
                      WiFi (SSH)         Telemetry radio
                           │                    │
                           v                    v
                    ┌──────────────────────────────┐
                    │     GROUND STATION (laptop)   │
                    │                               │
                    │  SSH: Y/N target confirmation  │
                    │  MP: live flight on map         │
                    │  RC: manual override if needed  │
                    └──────────────────────────────┘
```

**What you're testing**: Full mission: takeoff, search, detect, centre, descend, verify, land. Then iterate.

---

## Software: Code Modules

```
config.py ............. Settings (altitudes, camera, connection)
states.py ............. State definitions (SEARCH, VERIFY, etc.)
utils.py .............. Geo math (GPS <-> pixels)

vision.py ............. Camera + AI detection        [INDEPENDENT MODULE]
planning.py ........... Search pattern generation    [INDEPENDENT MODULE]

main.py ............... Mission orchestrator (ties everything together)
simulation.py ......... Laptop-only simulation (map + simulated drone view)
preflight.py .......... Connectivity checker (standalone tool)
```

| File | What it does | Depends on | Test independently? |
|------|-------------|-----------|---------------------|
| config.py | All settings in one place | -- | -- |
| states.py | State names (SEARCH, VERIFY...) | -- | -- |
| utils.py | GPS/pixel conversion | config | -- |
| vision.py | Camera frames + AI detection | config, model file | YES: pi_1 through pi_9 |
| planning.py | Lawnmower search pattern | config, utils | YES: simulation.py |
| main.py | Full mission state machine | everything | Full system test |
| simulation.py | Simulated drone on map.jpg | config, utils, vision | YES: laptop only |
| preflight.py | Check all connections work | config, vision | YES: standalone |

---

## What Can Be Worked On Independently

```
VISION (vision.py)               FLIGHT CONTROL (main.py + Cube)
  Camera captures frames           MAVLink connection
  AI model loads + detects          Arm, takeoff, goto, land
  Returns (found, x, y, conf)      State machine logic
  Test: pi_1 through pi_9          Test: test_cube.py
  --> No Cube needed                --> No camera needed

SEARCH PLANNING (planning.py)    GROUND STATION (Mission Planner)
  Lawnmower pattern generation      Telemetry radio connection
  Optimal entry point               Map display, geofence
  Test: simulation.py               Failsafe configuration
  --> Laptop only, no hardware      --> Independent of Pi code
```

These 4 areas can be developed and tested completely independently.
They only come together when main.py runs on the Pi with everything connected.

---

## Simulation vs Real: What Changes

| | Simulation (laptop) | Real (Pi + Cube) |
|---|---------------------|-------------------|
| Camera | Simulated: crops from map.jpg | Real: Pi CSI camera |
| AI backend | Ultralytics YOLO (fast, GPU) | TFLite (lightweight, CPU) |
| Flight controller | SITL over TCP (localhost) | Real Cube over Serial UART |
| Search area | Drawn on map with mouse click | Pre-defined GPS waypoints |
| Display | OpenCV windows | Headless (SSH terminal) |

**What stays exactly the same:**
- main.py (state machine logic -- identical)
- planning.py (search pattern generation)
- states.py, utils.py, config.py (structure)
- vision.py interface: `detect_in_image(frame)` returns `(found, x, y, conf)`

**The transition from simulation to real is about swapping connections, not rewriting code.**

### The Progression: Same Code, Different Hardware

You don't jump straight from simulation to a flying drone. There are intermediate steps,
and the same codebase handles all of them:

```
                          same main.py
                          same vision.py
                          same planning.py
                               │
                ┌──────────────┼──────────────┐
                │              │              │
           Laptop+SITL    Laptop+SITL    Pi+Real Cube
           simulated cam   real webcam    real CSI cam
           (SIMULATION)     (REAL)         (REAL)
                │              │              │
           "Does the      "Does real     "Full autonomous
            logic work?"   camera+AI       mission"
                            detect?"
```

**Step 1 — Simulation (where you are now):**
Run `DRONE_MODE=SIMULATION`. Camera is simulated (crops from map.jpg). Flight controller
is SITL. Everything on your laptop. Test the state machine, search pattern, detection logic.

**Step 2 — Real camera, still SITL:**
Run `DRONE_MODE=REAL`. Your laptop webcam (or USB camera) replaces the simulated camera.
SITL still handles flight. This proves your real camera + AI model can detect targets
while the drone logic runs against the simulator. Point camera at a printout of the dummy.

**Step 3 — Real camera + Real Cube (bench, no props):**
Same code, now on the Pi with Cube wired via UART. Props OFF. config.py auto-detects
the serial port (`/dev/ttyAMA0`). Run main.py over SSH — verify it arms, sends waypoints,
and the state machine transitions correctly. Mission Planner shows commands on the map.

**Step 4 — Full flight:**
Same code. Props on. Pilot has RC override. The only change from step 3 is putting
propellers on and flying outdoors.

### How config.py Auto-Detects the Connection

No code changes needed between steps. config.py figures out what you're connected to:

```
On your laptop right now:
  No serial ports found
  → Falls through to tcp:127.0.0.1:5762
  → Connects to SITL
  → You're in simulation/testing mode

On the Pi with Cube wired to UART:
  /dev/ttyAMA0 exists
  → Returns /dev/ttyAMA0
  → Connects to real Cube
  → You're controlling real hardware

Override anytime:
  export DRONE_CONN=tcp:192.168.1.42:5762
  → Environment variable always wins
```

The same `python main.py` command works everywhere. The hardware decides the connection.

### What You Still Need (Hardware Checklist)

The code is ready. These are the hardware/setup steps remaining:

```
STATUS    WHAT                          WHY                                    TEST
──────    ────                          ───                                    ────
[DONE]    Simulation working            Logic, search pattern, detection       main.py SIMULATION mode
[ ]       Raspberry Pi set up           Transfer code, install dependencies    SSH in, python --version
[ ]       CSI camera on Pi              Real frames instead of simulated       pi_1_test_camera.py
[ ]       best.tflite model on Pi       Ultralytics too heavy for Pi CPU       pi_2_detect_image.py
[ ]       AI detection on Pi            Confirm it detects dummy printout      pi_3_live_detect.py
[ ]       Cube wired to Pi (UART)       Real flight controller connection      pi_4_detect_and_log.py
[ ]       Bench test (no props)         Verify commands in Mission Planner     main.py REAL mode, props OFF
[ ]       Manual flight with detection  Calibrate detection altitude           Pilot flies, Pi logs detections
[ ]       Full autonomous flight        The real mission                       main.py REAL mode, props ON
```

Each step proves the previous one works. If something breaks, you know exactly which step caused it.

### Biggest Risk Unknowns

These are the things simulation can't tell you — you find out on real hardware:

1. **Detection altitude**: Does the AI see the dummy from 30m with the real camera?
   The real camera has different resolution, lens, and lighting than map.jpg crops.
   Phase 3 (manual flight with passive detection) answers this before any autonomous flight.

2. **Inference speed on Pi**: TFLite on Pi CPU will be slower than Ultralytics on your
   laptop GPU. If it's too slow, the drone might fly past a target before detection fires.
   pi_3 and pi_8 test scripts measure this.

3. **GPS accuracy**: SITL has perfect GPS. Real GPS drifts ~2-3m. The centering and
   landing logic may need tuning based on real GPS behaviour.

4. **Wind and movement**: Simulation has no wind. Real flight means the camera frame
   is moving and tilting. Detection confidence may drop.

None of these require code rewrites — just tuning config.py values (altitudes, speeds,
thresholds) based on real test data.

---

## The Mission State Machine

This is the core logic in main.py. It's identical in simulation and real mode.

```
INIT -> CONNECTING -> ARMING -> TAKEOFF
                                   |
                          TRANSIT_TO_SEARCH (fast fly to first waypoint)
                                   |
           +--------------------SEARCH (lawnmower pattern)
           |                       |
           |              (target detected)
           |                       |
           |                  CENTERING (fly over target)
           |                       |
           |                  DESCENDING (drop to verify altitude)
           |                       |
           |                    VERIFY (operator Y/N)
           |                   /       \
           +--- N (resume) --+         Y
                                       |
                                   APPROACH (fly to landing spot)
                                       |
                                    LANDING
                                       |
                                     DONE
```

Manual override (M key) can interrupt any state. RC kill switch works at all times.

---

## Connection Auto-Detection

config.py picks the right connection automatically:

```
Priority:
  1. DRONE_CONN environment variable     (always wins)
  2. Serial port /dev/ttyAMA0 etc.       (Pi with Cube wired)
  3. WSL gateway IP                       (WSL connecting to Windows SITL)
  4. tcp:127.0.0.1:5762                   (Windows localhost default)
```

Environment variables:
```bash
export DRONE_MODE=REAL                        # or SIMULATION
export DRONE_CONN=tcp:192.168.1.42:5762       # override auto-detect
export DRONE_BAUD=57600                       # serial baud rate (default 57600)
```

---

## Testing Strategy

Test each layer independently, then combine:

```
Layer 1: Vision alone         pi_1, pi_2, pi_3, pi_8, pi_9     No Cube needed
Layer 2: Cube alone           test_cube.py                      No camera needed
Layer 3: Vision + Cube        pi_4_detect_and_log.py            Bench test (carry by hand)
Layer 4: Full system (bench)  preflight.py + main.py (no props) Real Cube, no flying
Layer 5: Full system (flight) main.py (with props)              First autonomous flight
```

Each layer proves the previous one works. If something breaks, you know exactly which layer caused it.

---

## Doc Guide

| Doc | Read when you want to... |
|-----|--------------------------|
| ARCHITECTURE.md (this) | Understand the system, modules, and connections |
| NEXT_STEPS.md | Know what to do next (phases 0-5, step by step) |
| PI_SETUP.md | Set up the Raspberry Pi (transfer, install, test) |
| CV_GUIDE.md | Improve the vision system (retrain, calibrate, swap models) |
| CONNECTIVITY.md | Debug a specific connection issue |
| PREFLIGHT_CHECKLIST.md | Run through checks before a real flight |
| TEAM_PLAN.md | See workstreams and flight test data collection plans |
| ROADMAP.md | See the full 10-phase development history |
