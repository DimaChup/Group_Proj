
sudo pkill -f mavproxy; sleep 2
sudo /opt/mavlink/mavlink-venv/bin/mavproxy.py \
  --master=/dev/ttyAMA0 --baudrate=921600 --streamrate=10 \
  --out=udpout:127.0.0.1:14550 --out=udpout:127.0.0.1:14551 --out=tcpin:0.0.0.0:5762


===================================================================================

cd ~/dima/Group_Proj && source pienv/bin/activate
python capture_training.py

http://PI_IP:8091/stream


================================================================================

python passive_watch.py


http://PI_IP:8090/

================================================================================











# Field Quick Reference (No Internet Needed)

Pi IP: `172.20.10.2` or `192.168.1.3` (depends on network — check with `hostname -I` on Pi)

## Terminal Setup (after every reboot)

### Terminal 1 — Mavproxy (ALWAYS first, before anything else)
```bash
sudo /opt/mavlink/mavlink-venv/bin/mavproxy.py \
  --master=/dev/ttyAMA0 --baudrate=921600 --streamrate=10 \
  --out=udpout:127.0.0.1:14550 --out=tcpin:0.0.0.0:5762
```
Wait for: `Detected vehicle 1:0` + `online system 1` + `Mode STABILIZE`

### Terminal 2 — Scripts (new PuTTY window, same IP)
```bash
cd ~/dima/Group_Proj && source pienv/bin/activate
```

### Laptop — Mission Planner
TCP → PI_IP → port 5762

### Laptop — Browser (for camera stream)
- Scripts on port 8090: `http://PI_IP:8090`
- capture_training on port 8091: `http://PI_IP:8091`

## Camera Troubleshooting
```bash
# Check camera detected:
libcamera-hello --list-cameras

# Kill stuck camera process:
sudo pkill -f libcamera; sudo pkill -f python; sleep 2

# Quick test (no display needed):
python -c "
from picamera2 import Picamera2
cam = Picamera2()
cam.configure(cam.create_still_configuration(main={'size': (640,480), 'format': 'RGB888'}))
cam.start()
import time; time.sleep(1)
frame = cam.capture_array()
print('Camera OK:', frame.shape)
cam.stop(); cam.close()
"
```

---

## Scripts In Order

### 1. Diagnostics (all systems check)
```bash
python tests/diagnostics/diagnostics.py
```
Need: camera, AI, Cube, GPS all green. Run on Pi screen (not PuTTY — needs display).

### 2. Benchmark (inference speed)
```bash
python tests/hardware/benchmark.py
```
Note FPS and avg ms.

### 3. FOV Calibration (use capture_training stream)
```bash
python capture_training.py
```
Browser: http://PI_IP:8091/stream
1. Hold camera pointing straight down, exactly 1m above a tape measure
2. Count how many cm visible left-to-right in the stream
3. Calculate: `FOCAL_LENGTH_MM = (5.02 × 100) / visible_width_cm`
4. Update config.py with new FOCAL_LENGTH_MM value

### 4. Capture Training Photos
```bash
python capture_training.py
```
Browser: http://PI_IP:8091. SPACE=photo, V=video, Q=quit. ZERO commands.

### 5. GPS Check
```bash
python tests/hardware/gps_test.py
```
Wait for fix_type=3, 8+ sats.

### 6. Waypoint Flight (no CV)
```bash
python tests/flight/2_waypoints.py --dry-run          # check plan
python tests/flight/2_waypoints.py --alt 10            # real flight
```
Loads flight_plans/waypoints.json (4 waypoints already saved). Arms, flies waypoints, RTL.

### 7. Passive CV (pilot flies RC, Pi watches)
```bash
python tests/flight/1_passive_flight.py --headless --stream
```
Browser: http://PI_IP:8090. ZERO commands. Log detections at various altitudes.

### 8. Full Dashboard (N/Y/I/X/L buttons)
```bash
python pi_flight.py --fps 4
```
Browser: http://PI_IP:8090.
- N = investigate cluster
- Y = confirm dummy
- I = item of interest
- X = false positive
- L = land 7.5m north
- FAKE DET = test without real detection

### 9. Full Autonomous Mission
```bash
python main.py
```
Full search pattern → detect → centre → verify → land.

---

## Kill Switch
**RC mode switch → STABILIZE.** Always overrides everything. RC pilot's hand on switch at all times.

## Ctrl+C
All flight scripts trigger RTL on Ctrl+C.

## Model Swap (if CV not detecting)
```bash
cp cv_models/sar_v2_1088/best.tflite best.tflite   # retrained v2 model (BEST)
cp cv_models/sar_640/best.tflite best.tflite        # earlier 640 model
cp cv_models/sar_1280/best.tflite best.tflite       # earlier 1280 model
```
Or use `--model` flag: `python pi_flight.py --fps 4 --model cv_models/sar_v2_1088/best.tflite`

## Lower Confidence (if missing detections)
Edit vision.py line ~174: change `0.4` to `0.3` or `0.25`

## Servo (First Aid Kit Release)
```bash
python -c "
from pymavlink import mavutil
mav = mavutil.mavlink_connection('udpin:0.0.0.0:14550')
mav.wait_heartbeat()
CH = 9        # AUX1=9, AUX2=10, etc — change to your channel
RELEASE = 2000  # open
HOLD = 1000     # closed
mav.mav.command_long_send(mav.target_system, mav.target_component,
    mavutil.mavlink.MAV_CMD_DO_SET_SERVO, 0, CH, RELEASE, 0,0,0,0,0)
print('Released!')
"
```
Change `CH` to match your AUX port. Change `RELEASE`/`HOLD` PWM if servo direction is flipped.

## Common Issues
- **Camera "in use"**: `sudo pkill -f libcamera; sudo pkill -f python` then retry
- **No heartbeat**: Is Cube powered? Check serial cable TX↔RX, shared ground.
- **Qt crash in PuTTY**: Script needs display. Run on Pi screen or add `--headless`.
- **GPS won't lock**: Move to open area, wait 5-15 min, Here 3+ LED green=locked.
- **Reboot Pi**: `sudo reboot` — then start from Terminal Setup again.
- **Git pull**: `cd ~/dima/Group_Proj && git pull` (needs internet)
