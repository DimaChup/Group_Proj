# Slides Text Flow & Design Notes

## Overall Flow

Two slides, ~1.5 min each. Edward covers training/data before us. Herish follows after us.

**Slide 1: Vision Pipeline** — what happens AFTER the model exists, on the drone
**Slide 2: Simulation & Testing** — how we validated everything before flying

---

## Slide 1: Vision Pipeline

### Key message
Camera pixels → GPS coordinates, running on Pi 5 CPU with no GPU.

### Flow of talking points
1. **Pipeline** (hero element, full width) — walk through each stage:
   - Camera capture: 1456×1088 from IMX296 global shutter (same resolution in sim and real)
   - YOLOv8n inference: NCNN backend chosen after benchmarking (73ms vs 200ms TFLite)
   - Pixel→GPS projection: FOV + altitude → real-world offset
   - Attitude correction: pitch+roll ray-trace from flight controller
   - Output: ~9 FPS effective, target GPS estimate

2. **Why NCNN?** — bar chart showing TFLite 4.8 FPS vs NCNN 10.9 FPS. 2.3× faster, same accuracy.

3. **Tilt compensation** — the drone is never level. Without correction: 6.2m error. With ray-trace: 0.3m. This is the same principle military surveillance drones use.

4. **GPS estimation accuracy** — heatmap showing estimates coloured by frame centrality. CEP50 = 2.2m. Multiple observations weighted by inverse altitude squared + centrality bonus.

5. **Four-phase refinement** — detect from altitude (~3.5m) → approach (~2.5m) → hover lock (~1.8m) → verify & land. At hover, pixel offset = 0, so drone GPS IS target GPS.

### Design notes
- Pipeline is the MOST prominent element — full width chevron ribbon
- Bullseye faintly visible in the pipeline output box
- Estimation heatmap (not plain bullseye) shows the different estimate types
- Bar chart compact, beside heatmap
- Four-phase refinement on the right, compact

---

## Slide 2: Simulation & Testing

### Key message
Simulation is the FOUNDATION — everything proven there before touching real hardware. The ladder shows how we bridge from sim to real.

### Flow of talking points

1. **Simulation foundation** (MOST PROMINENT — bottom of ladder, big)
   - This is where we start talking. The simulation is comprehensive:
   - All 12 mission requirements verified end-to-end
   - NOT just waypoints — full state machine: search pattern → detect → centre → descend → verify → land
   - Search pattern: spiral (not lawnmower — updated)
   
   **Simulated realism (this is the impressive part):**
   - Same pixel resolution as real camera (1456×1088)
   - Camera attitude simulation (pitch/roll during flight)
   - Motion blur at speed
   - GPS drift noise (±3m)
   - Synthetic detection targets composited at altitude-correct scale
   - Geofence with repulsive fields
   - Wind effects on detection timing
   
   "We didn't just simulate waypoints — we simulated the camera seeing the target from altitude with realistic tilt, blur, and GPS noise"

2. **Sim2Real Ladder** — how we progressively build confidence:
   - The subtitle (in brackets) captures the philosophy: "never fly something you haven't proven at every level below it"
   
   **Ground Verification (done):**
   - G1: 127 unit tests + dry-run visualization
   - G2: Outdoor calibration (FOV, GPS accuracy, real altitude detection)
   
   **Flight Missions (progressive, checkboxes):**
   - M1: Bench integration — Pi+Cube+Camera talking, no props ✓
   - M2: Passive flight — pilot flies RC, AI watches, zero commands ✓  
   - M3: Waypoint flight — autonomous GPS nav, no CV (planned)
   - M4: Auto detect + hover — search + AI triggers guided hover (planned)
   
   **Real Mission (goal):**
   - Full autonomous SAR — demo day

3. **Video** (left side) — simulation recording showing full mission

### Design intent
- Simulation foundation should be TALL (twice current height) and visually dominant
- It's the base of everything — the bedrock
- Ladder steps are compact (70% width, centered)
- Checkboxes are interactive — can tick M3/M4 live during presentation as they complete
- Real Mission box at top with star emoji

### Text flow refinement (user's thinking process)
- User wants simulation to be the star of this slide, not the ladder
- "The simulation bit should be most prominent, then we talk about the ladder — how we get from sim to real"
- Simulation is NOT just "we ran it in sim" — it's "we simulated realistic camera behavior, tilt, blur, GPS noise at the same resolution as the real camera"
- The ladder is the bridge: each step proves one more thing works in reality
- Unchecked boxes (M3, M4) are honest — we haven't flown full missions yet
- But the simulation + ground verification + passive flight show we've done everything possible

---

## Speaking Script (draft — needs updating with new content)

### Slide 1 (~1.5 min)
"Edward showed you how we trained the model. Now let me walk through what happens when it runs on the drone..."
[walk through pipeline, NCNN choice, tilt compensation, four-phase refinement]
"...and importantly, the exact same code runs in simulation on a laptop and live on the Pi."

### Slide 2 (~1.5 min)  
"Our testing philosophy: never fly something you haven't proven at every level below it..."
[start with simulation foundation — emphasize realism]
[walk up the ladder — ground verification, flight missions]
[honest about what's done vs planned]
"...the software is proven. Demo day brings it together."

---

## Open questions / decisions
- Search pattern: spiral (confirmed, not lawnmower)
- Should video placeholder be replaced with actual sim recording before demo day?
- Teleprompter script needs updating to match new slide content
