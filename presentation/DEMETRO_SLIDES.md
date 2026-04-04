# Demetro's FDR Slides — Speaking Script

**2 slides, ~1.5 min each = 3 min total**
**Comes after Edward (data collection + training)**

Open slides: `presentation/demetro_slides.html`

---

## SLIDE 1: Vision Pipeline (1.5 min)

**Transition from Edward:** "Edward just showed you how we collected data and trained the model. Now I'll show you what happens when that model runs on the Pi during a mission."

**[Point to pipeline flow at top]**
"The camera captures frames at 1456 by 1088 pixels. YOLOv8 runs inference at about 5 frames per second on the Pi. When it detects something, we convert that pixel position into a GPS coordinate using the camera geometry and the drone's altitude."

**[Point to tilt comparison boxes]**
"Here's the clever bit. When the drone is flying, it's not looking straight down — it tilts forward. Without correcting for that, our position estimate is off by over 6 metres. We read the actual pitch and roll from the flight controller and ray-trace through the tilt. That brings the error down to 0.3 metres."

**[Point to four-phase progression on right]**
"The system doesn't just detect once and hope for the best. It progressively refines. First detection gives a rough position — about 3.5 metres. The drone flies toward it and slows down — the estimate improves. Then it hovers directly above — now the camera IS looking straight down, and the drone's GPS IS the target's GPS. Finally the operator confirms: is this the casualty? That process takes us from 3.5 metres down to 1.8."

---

## SLIDE 2: Simulation (1.5 min)

**[Open with why]**
"Because our drone hardware wasn't available for most of the term, I built a full simulation environment. The important thing is — it's the same code. What runs in this simulation is exactly what runs on the Raspberry Pi. No separate version."

**[Point to feature grid]**
"The simulation includes everything: the lawnmower search pattern, AI detection, a five-layer geofence that keeps the drone inside the flight area and away from the SSSI, PLB redirect, payload deployment, and return to home."

"We even simulate camera effects — tilt, motion blur, vibration, GPS noise — so we can stress-test the vision system under realistic conditions."

**[Point to metrics]**
"All 12 requirements from the brief are verified end-to-end. 58 test scripts, 127 unit tests, over 4,400 lines of mission code."

**[Point to why box]**
"We built this because we had to. But it turned out to be one of our biggest strengths — we could iterate rapidly, test edge cases, and verify the complete mission without risking hardware. When the drone finally worked at Easter, we already knew the software was solid."

**[Hand over to next speaker — Herish for PLB]**

---

## Screenshots Needed

1. **Mission Dashboard** — run `python main.py --speed 5 --lock-yaw`, screenshot during detection
2. Put screenshot in place of the placeholder box on slide 2

## Key Numbers to Remember

- 99.5% detection accuracy
- 4.8 FPS on Pi 5
- 2.3m GPS accuracy
- 6.2m → 0.3m with tilt compensation
- 12/12 requirements met
- 58 test scripts
- 4,400+ lines of code
