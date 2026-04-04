# Demetro's FDR Slides — Speaking Script

**2 slides, ~1.5 min each = 3 min total**
**Comes after Edward (data collection + training)**

Open slides: `presentation/demetro_slides.html`

---

## SLIDE 1: Vision Pipeline (1.5 min)

**Transition from Edward:** "Edward just showed you how we collected data and trained the model. Now I'll show you what happens when that model runs on the Pi during a real mission."

**[Point to pipeline flow]**
"So the camera captures frames, YOLOv8 detects the target at about 5 frames per second on the Pi, and then we need to turn that pixel position into actual GPS coordinates. We use the camera geometry, the drone's altitude, and its heading to compute where on the ground that detection actually is."

**[Point to tilt comparison]**
"Now here's the problem — when the drone is flying, it's tilted forward. The camera isn't looking straight down. If we ignore that, we're off by 6 metres. So we read the actual pitch and roll from the flight controller and ray-trace through the tilt — same maths used in military drone systems. That brings the error down to about 30 centimetres."

**[Point to four phases]**
"But we don't rely on that alone. The system uses a four-phase process to progressively get more accurate. First detection while flying — rough estimate. Then fly toward it, slow down — estimate improves. Then hover directly above — now the camera IS pointing straight down and the drone's GPS IS the target's GPS. No complex maths needed at that point. Finally the operator confirms yes or no. So we go from 3.5 metres down to 1.8 metres accuracy — well within the 5 to 10 metre landing requirement."

---

## SLIDE 2: Simulation + Ladder to Real (1.5 min)

**[Point to ladder visual]**
"Here's our journey from simulation to reality. At the bottom — full simulation. All 12 requirements verified. The same code that runs here runs on the Pi. Above that — Pi bench testing. Camera working, AI running at 4.8 FPS, Cube connected. Above that — Easter field testing. FOV calibrated, GPS verified, first real data. And at the top — real autonomous flight. We could attempt it now, but it would be risky without the progressive testing we planned."

**[Point to features]**
"The simulation isn't a toy. It includes the full geofence — five layers protecting the flight area and the SSSI. It simulates camera tilt, motion blur, vibration, GPS noise. We have 58 test scripts and 127 unit tests. Everything the brief asks for works end-to-end in simulation."

**[Point to why box]**
"We built this because we had to — our drone hardware wasn't available for most of the term. But honestly, it turned out to be one of our biggest strengths. When the drone finally worked at Easter, we already knew the software was solid. We didn't have to debug software AND hardware at the same time."

**[Closing thought]**
"We're confident in the system. The simulation proves the logic works. The Easter testing proves the hardware integration works. Demo day is where we bring it all together."

**[Hand over to next speaker — Herish for PLB]**

---

## The Ladder Visual (for slide 2)

```
  ┌─────────────────────────────┐
  │  🚁 REAL AUTONOMOUS FLIGHT  │  ← Goal (risky without progressive testing)
  │  All requirements on real HW │
  └──────────────┬──────────────┘
                 │ ↑ we're here, ready but cautious
  ┌──────────────┴──────────────┐
  │  🌿 EASTER FIELD TESTING    │  ✅ Done
  │  FOV calibrated, GPS tested  │
  │  Camera + Cube + Pi working  │
  └──────────────┬──────────────┘
                 │
  ┌──────────────┴──────────────┐
  │  🔧 PI BENCH TESTING        │  ✅ Done
  │  4.8 FPS inference, 0.966   │
  │  confidence, Cube connected  │
  └──────────────┬──────────────┘
                 │
  ┌──────────────┴──────────────┐
  │  💻 FULL SIMULATION (SITL)  │  ✅ Done
  │  12/12 requirements met      │
  │  58 tests, 4400+ lines       │
  │  Same code as real drone     │
  └─────────────────────────────┘
```

---

## Key Numbers to Remember
- 99.5% detection accuracy
- 4.8 FPS on Pi 5
- 2.3m GPS accuracy (CEP50)
- 6.2m → 0.3m with attitude compensation
- 3.5m → 1.8m through four-phase refinement
- 12/12 requirements met in simulation
- 58 test scripts, 127 unit tests
- 4,400+ lines of code
