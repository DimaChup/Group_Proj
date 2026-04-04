# Demetro's FDR Slides (2 slides, ~1.5 min total)

**Follows after Edward (data collection and vision training)**

---

## SLIDE 1: Simulation (~45 sec)

### Visual: Screenshot of Mission Dashboard (god view + camera)

### On slide (3 bullets max):
- Same code runs on laptop and Pi — no separate sim
- All 12 requirements verified end-to-end
- Drone hardware wasn't available → simulation let us test everything

### Say:

"I built a full simulation environment so we could develop without waiting for the drone. The key thing is — it's the same code. What runs in simulation is exactly what runs on the Pi. So when we say all 12 requirements are met, they're met with the actual code that flies the drone.

[Point to screenshot] Here you can see the search pattern, the geofence zones, and the detection happening in real time."

---

## SLIDE 2: How Vision Works (~45 sec)

### Visual: Detection screenshot (green box + confidence) OR pipeline diagram

### On slide (3 bullets max):
- YOLOv8n: 99.5% accuracy, 5 FPS on Pi
- Detects → estimates GPS position → drone responds
- Attitude compensation: 2.3m accuracy even during flight

### Say:

"Following on from Edward's data work — once the model is trained, here's how it runs on the Pi. The camera captures frames, the AI detects the target, and we estimate its GPS position using the camera geometry and the drone's altitude.

The clever bit is we compensate for the drone's tilt during flight — it's not looking straight down when it's moving. We use the flight controller's attitude data to correct for that, which gives us about 2.3 metre accuracy.

When it finds something, the drone stops, hovers to get a better lock, and asks the operator to confirm."

---

## Screenshots to Prepare
1. Mission Dashboard with detection (green box visible)
2. Detection close-up OR the pipeline flow diagram from the report
3. Dry-run pattern as backup

Run: `python main.py --speed 5 --lock-yaw` → screenshot during detection
