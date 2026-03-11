# Pre-Flight Checklist

Run through this checklist before every flight. Each step tells you exactly what to do, what to expect, and what to try if it fails.

---

## 1. Hardware Checks (Visual Inspection)

| # | Check | How |
|---|-------|-----|
| 1.1 | Camera ribbon cable seated | Push ribbon firmly into Pi CSI port, lock the clip |
| 1.2 | Cube UART wiring correct | Pi TX (GPIO 14) -> Cube RX, Pi RX (GPIO 15) -> Cube TX, GND -> GND |
| 1.3 | Telemetry radio on Cube TELEM1 | Radio module plugged in, LED blinking |
| 1.4 | GS telemetry radio plugged in | USB radio on laptop, LED blinking |
| 1.5 | Battery connected and charged | Check voltage on Cube / Mission Planner |
| 1.6 | Props secure (if flight test) | All props tightened, correct rotation direction |

---

## 2. Software Setup

### On the Pi
```bash
# SSH into Pi from your laptop
ssh pi@<pi-ip-address>

# Activate virtual environment
source pienv/bin/activate

# Navigate to project
cd ~/sar-drone

# Set mode to REAL
export DRONE_MODE=REAL
```

### On the GS (laptop)
- Open Mission Planner
- Connect via COM port (telemetry radio) or TCP (SITL)
- Confirm HUD shows attitude data

---

## 3. Component Tests (Run in Order)

### 3.1 Camera
```bash
python tests/laptop/test_camera.py
```
**Expected**: "Camera opened successfully" + frame dimensions printed

**If it fails**:
- Check ribbon cable is seated and clipped
- Enable camera: `sudo raspi-config` -> Interface -> Camera
- Test hardware directly: `libcamera-hello`
- If OpenCV fails, the script auto-tries picamera2

### 3.2 AI Detection
```bash
python tests/laptop/test_cv.py
```
**Expected**: Live camera feed with bounding boxes drawn on detected targets, FPS counter shown

**If it fails**:
- Is `best.tflite` in the project root?
- Install runtime: `pip install tflite-runtime "numpy<2"`
- Run benchmark to check: `python tests/hardware/benchmark.py`

### 3.3 Cube Connection
```bash
python tests/laptop/test_cube.py
```
**Expected**: Heartbeat received, GPS fix, attitude data, battery voltage

**If it fails**:
- Check wiring: TX->RX, RX->TX, GND->GND
- Try different baud rate: `python tests/laptop/test_cube.py /dev/ttyAMA0 921600`
- Enable serial: `sudo raspi-config` -> Interface -> Serial -> Yes
- Make sure Cube is powered and booted

### 3.4 Full Connectivity
```bash
python tests/laptop/test_all.py
```
**Expected**: Connectivity map showing all links with OK/FAIL status

**If it fails**: Fix the individual component that failed (sections 3.1-3.3 above)

---

## 4. Pre-Flight Script

This is the final automated check. Run it after all component tests pass.

```bash
python preflight.py
```

### What it checks

| Check | What it does | Pass condition |
|-------|-------------|----------------|
| TCP PORT / SERIAL | Tests if flight controller is reachable | Port open or serial device exists |
| HEARTBEAT | Sends MAVLink request, waits for response | Heartbeat received within 5s |
| CAMERA | Opens camera, grabs a frame (REAL mode only) | Frame captured successfully |
| AI MODEL | Loads best.tflite with available backend | Model loads without error |

### Reading the output
```
=======================================================
         PRE-FLIGHT CONNECTIVITY TEST
=======================================================

  [PLATFORM]   PI
  [MODE]       REAL
  [CONNECTION] /dev/ttyAMA0, baud=57600 (auto-detected serial port)

-------------------------------------------------------
  RUNNING CHECKS...
-------------------------------------------------------

  [OK  ] SERIAL        /dev/ttyAMA0 EXISTS
  [OK  ] HEARTBEAT     Heartbeat received (system 1, baud=57600)
  [OK  ] CAMERA        Camera 0: 640x480
  [OK  ] AI MODEL      Model loaded (TFLite)

-------------------------------------------------------
  RESULT: 4 passed, 0 failed, 0 skipped
-------------------------------------------------------

  All checks passed. Ready to fly:
    python main.py
```

### If connection fails
- preflight.py will prompt you to enter an IP address manually
- If you enter one and it works, it tells you the export command:
  ```bash
  export DRONE_CONN=tcp:192.168.1.42:5762
  ```
- Run that command so you don't get prompted again this session

---

## 5. Mission Planner Verification

| # | Check | How |
|---|-------|-----|
| 5.1 | Drone appears on map | HUD shows attitude, map shows icon |
| 5.2 | GPS fix | Mission Planner shows 3D fix, HDOP < 2.0 |
| 5.3 | Battery voltage | Check voltage in Quick tab (should match battery spec) |
| 5.4 | Flight mode | Set to GUIDED (required for autonomous control) |
| 5.5 | Arming checks pass | Try arming in Mission Planner - all pre-arm green |

---

## 6. Go / No-Go Decision

All of these must be true before running `python main.py`:

- [ ] preflight.py shows 0 failures
- [ ] Camera capturing frames (tested with tests/laptop/test_camera.py)
- [ ] AI model detects target (tested with tests/laptop/test_cv.py)
- [ ] Cube heartbeat confirmed (tested with tests/laptop/test_cube.py)
- [ ] Mission Planner connected and showing live data
- [ ] GPS has 3D fix
- [ ] Battery fully charged
- [ ] Flight area clear of people and obstacles
- [ ] Weather conditions acceptable (low wind, no rain)

---

## 7. Launch

```bash
# On Pi via SSH
export DRONE_MODE=REAL
python main.py
```

The drone will:
1. Arm and take off to search altitude
2. Follow search pattern waypoints
3. When target detected: centre, descend, prompt Y/N on SSH terminal
4. On Y: land near target. On N: resume search.

---

## Quick Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| "No heartbeat" | Wrong baud or wiring | Swap TX/RX, try baud 921600 |
| "Camera NOT AVAILABLE" | Ribbon cable or not enabled | Reseat cable, run raspi-config |
| "Model file not found" | best.tflite missing | Copy model file to project root |
| "TCP TIMEOUT" | SITL/Mission Planner not running | Start SITL or check firewall |
| "TCP REFUSED" | Wrong port or firewall | Check port 5762, add firewall rule |
| Position always (0,0) | Old TFLite code bug | Update vision.py (should already be fixed) |

---

## Environment Variables Reference

| Variable | Default | When to change |
|----------|---------|----------------|
| DRONE_MODE | REAL | Set to SIMULATION for laptop-only testing |
| DRONE_CONN | auto-detect | Set manually if auto-detect picks wrong target |
| DRONE_BAUD | 57600 | Set to 921600 if Cube is configured for higher baud |
