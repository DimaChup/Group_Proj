# Simple Simulator — What It Is and Why We Use It

## What Is It?

`simple_simulator.py` is an interactive flight simulator that runs on a laptop.
You fly a virtual drone over a satellite image (map.jpg) using your keyboard,
and the onboard AI (same model as the real drone) tries to detect the dummy
in the simulated camera view.

It lets us test and tune **everything** before a single real flight.

## Why Do We Need It?

Real flights are:
- Expensive (battery time, travel, setup)
- Risky (crash = broken drone)
- Hard to repeat (wind, lighting, GPS conditions change)

The simulator gives us **unlimited free test flights** with full control over
conditions. We can test edge cases that would be dangerous or impossible to
reproduce in real life.

## What Can We Test?

### 1. CV Detection Quality
- Does the AI detect the dummy from 30m? 20m? 10m?
- At what altitude does detection start/stop?
- How many false positives on grass/trees/shadows?
- **Ground truth comparison**: we know exactly where the dummy is, so we can
  measure how accurate the GPS estimate is (impossible in real flight without
  survey equipment)

### 2. Resolution & FPS Impact
- `--fps 4` simulates Pi's real inference speed (~4 fps on TFLite)
- `--tflite` forces the same TFLite backend the Pi uses
- See how limited FPS affects detection during movement

### 3. Camera Shake / Motion Blur
- `--shake 5` adds altitude-dependent camera shake
- Higher altitude = more ground movement per pixel of shake
- HUD shows: "SHAKE: 5px = 20cm on ground" so you see real-world impact
- Tests: can the AI still detect when the image is shaky?

### 4. GPS Drift / Signal Quality
- `--gps-drift 3` adds realistic GPS random walk (3m standard deviation)
- Simulates real GPS accuracy (~2-3m in open sky, worse near buildings)
- Tests: how does GPS drift affect our position estimates?

### 5. GPS Estimation Accuracy
Three estimators run simultaneously, compared against ground truth:
- **Rolling average** (last 50 observations)
- **Running total average** (all observations ever, weighted)
- **Kalman filter** (Bayesian, adapts over time)

All use **inverse variance weighting** — observations from lower altitude
count more (10m observation = 9x more valuable than 30m).

### 6. Landing Sequence
- **L key**: fly to a point 7.5m north of estimated dummy position, then land
- Tests the full sequence: estimate → offset calculation → fly to → descend → land
- Measures: how far from the dummy did we actually land?
- In simulation, navigation is perfect. Real Cube adds ~2.5m error.

### 7. Multi-Target Scenarios
- Place multiple dummies on the map
- AI must cluster detections (which observations belong to which target?)
- Pilot classifies each: Y=dummy, I=item of interest, X=false positive
- Tests the full operational workflow

## How To Run

```bash
# Basic (ideal conditions):
set DRONE_MODE=SIMULATION
python simple_simulator.py

# Simulating real Pi conditions (recommended):
set DRONE_MODE=SIMULATION
python simple_simulator.py --fps 4 --tflite --gps-drift 3 --shake 5
```

**Requires**: SITL running (Mission Planner simulation or mavproxy).
SITL home: `--home=51.423412,-2.671414,50,155`

## Controls

| Key | Action |
|-----|--------|
| SPACE | Arm motors |
| W/A/S/D | Fly forward/left/back/right |
| R/F | Altitude up/down |
| Q/E | Yaw left/right |
| C | GPS centering — auto-fly to estimated dummy position |
| V | Visual servo — center dummy in camera using pixel offset |
| G | GPS lock — 30s averaging while centered (most accurate estimate) |
| L | Land — fly to 7.5m north of estimate, descend, land |
| Y | Classify target as dummy (confirmed) |
| I | Classify as item of interest (log GPS, move on) |
| X | Classify as false positive (discard) |
| H | Altitude test — step through 30/25/20/15/10m, compare estimators |
| B | Toggle recording GPS estimates |
| TAB | Cycle scatter plot reference between dummies |
| ESC | End flight, show summary charts |

## What The Screen Shows

- **Left panel**: simulated drone camera view (what the AI sees)
- **Right panel**: god view — satellite map with drone position, dummy locations,
  detection clusters, GPS estimates, flight path
- **HUD overlay**: altitude, GPS position, drift, dummy estimates, errors vs ground truth

## The Mission Sequence (End-to-End Test)

1. Fly manually over the area → AI detects dummy during flyover
2. Press **C** → drone auto-flies to GPS estimate (~1-3m error)
3. Descend to 10m → press **V** → visual servo centers precisely
4. Press **G** → 30s GPS lock while centered → ~0.5m estimate error
5. Press **L** → fly to 7.5m north of estimate → auto-land
6. **ESC** → see summary: estimate error, landing distance, scatter plots

## Simulation vs Reality

| Factor | Simulation | Real Flight |
|--------|-----------|-------------|
| GPS accuracy | Configurable (--gps-drift) | ~2-3m real drift |
| Camera shake | Configurable (--shake) | Depends on wind/speed |
| Detection speed | Configurable (--fps) | ~4 fps on Pi (250ms/frame) |
| Navigation | Perfect (SITL) | ~2.5m error (real Cube) |
| Lighting | Map image (constant) | Sun, shadows, time of day |
| Model | Same best.tflite | Same best.tflite |
| Wind | None | Real wind gusts |
| Detection quality | Synthetic (map + dummy overlay) | Real camera, real dummy |

**Key insight**: simulation can't test lighting, wind, or real camera quality.
But it CAN validate all the logic, algorithms, and edge cases. If it works
in simulation with `--fps 4 --gps-drift 3 --shake 5`, the algorithms are
solid — only the CV model quality is unknown until real flight.

## Why We Built This — Problems We Anticipate

The simulator exists because we expect real-world problems that are hard
to debug mid-flight. Here's what we're worried about and how we test each one.

### Problem 1: GPS alone isn't accurate enough to land near the target

GPS drifts 2-3m in open sky. If we only use GPS to estimate where the dummy
is, our best estimate could be 3m off. At 7.5m offset landing, that's the
difference between landing 5m away vs 10m away.

**What the simulator tests**: run with `--gps-drift 3` and see how much
the GPS estimate wanders. Compare the three estimators (rolling avg, total
avg, Kalman) against ground truth. Find which one handles drift best.

### Problem 2: Vision centering can compensate for GPS error

This is the key insight: **even if GPS is wrong, the camera doesn't lie**.
If the dummy is in the right half of the frame, move right. If it's centred,
you're directly above it — regardless of what GPS says.

The simulator tests this with **C mode vs V mode**:
- **C mode (GPS only)**: fly to GPS estimate. Limited by GPS accuracy (~1-3m error)
- **V mode (vision servo)**: ignore GPS, use pixel offset to centre. Sub-metre
  accuracy because you're directly measuring where the target is in the frame

So even with 3m GPS drift, V mode centres the drone precisely above the dummy
because it uses the camera as the ground truth, not GPS.

### Problem 3: We need GPS for the final landing coordinate

Vision can centre the drone perfectly, but we can't hover forever — we need
a GPS coordinate to fly to for landing (7.5m north of the target). So we need
both: vision to get precise centering, then capture the drone's GPS at that
moment as our best estimate of the dummy's location.

**What the simulator tests**: the **G mode** (GPS lock) does exactly this.
V mode keeps the drone centred, G mode averages the drone's GPS position
over 30 seconds while centred. Because the drone is directly above the dummy
(confirmed by vision), the averaged GPS = the dummy's GPS. This combines
vision precision with GPS coordinates.

### Problem 4: FOV calibration affects everything

The pixel-to-GPS conversion depends on knowing the camera's field of view.
If `FOCAL_LENGTH_MM` or `SENSOR_WIDTH_MM` in config.py are wrong, every GPS
estimate from pixel position will have a systematic error (always off in the
same direction by the same amount).

**What the simulator tests**: the **H key** (altitude test) steps through
different altitudes and shows estimate error at each. If FOV is miscalibrated,
error will scale linearly with altitude — bigger at 30m than 10m. This tells
us we need to run `fov_calibrate.py` on the real camera before flight.

### Problem 5: Detection may fail at altitude or speed

The AI model was trained on synthetic images (map.jpg + dummy.png composites).
Real conditions — sun glare, shadows, motion blur, small target at 30m — may
cause the model to miss detections or produce false positives.

**What the simulator tests**:
- `--fps 4` shows whether 4 frames per second is enough to catch the dummy
  during a flyover at 3-5 m/s
- `--shake 5` shows whether camera shake kills detection confidence
- Flying at different altitudes shows the detection ceiling (above which
  the dummy is too small to detect)

### Problem 6: False positives could send the drone to the wrong place

If the AI detects a shadow or rock as a dummy, the drone wastes battery
flying to nothing. Worse, it might land in an unsafe location.

**What the simulator tests**: multi-target scenarios. Place multiple dummies,
fly over the area, see how many false clusters form. The pilot classification
system (Y/I/X) tests the operator's ability to reject false positives before
committing to a landing.

### Problem 7: What if the target is lost during centering?

Turbulence, a gust of wind, or a brief detection gap could cause the drone
to lose sight of the target mid-approach. Should it keep going? Stop? Search?

**What the simulator tests**: V mode handles this — if the target is lost,
it falls back to the last GPS estimate and holds position. If the target
reappears, it re-centres. You can test this by flying away from the dummy
during V mode and seeing how it recovers.

### Summary: GPS vs Vision — when to use which

| Situation | Use GPS | Use Vision |
|-----------|---------|------------|
| Flying to search area | Yes | No target yet |
| First detection (flyover at 30m) | GPS estimate from pixel | AI detects |
| Getting closer (centering) | Rough direction | Precise centering |
| Hovering above target | Capture GPS while centred | Confirms position |
| Final landing coordinate | Yes (averaged from hover) | N/A (can't see while landing) |
| Offset landing (7.5m away) | Yes (fly to coordinate) | N/A (target out of frame) |

**The core strategy**: vision is more accurate than GPS for positioning,
but GPS is needed for navigation. Use vision to get centred, capture GPS
while centred, then navigate to the landing point using GPS.

## After Simulation: Progressive Real Testing

1. **simple_simulator.py** ← you are here (validate algorithms)
2. **pi_passive_flight.py** — pilot flies RC, Pi watches + logs (zero commands)
3. **pi_detect_and_center.py** — autonomous waypoints + detect + center + hover
4. **main.py** — full mission (search + detect + center + descend + verify + land)

Each step builds trust. Never skip a step.
