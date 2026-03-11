# Connectivity Guide

## System Architecture
```
[Camera] --CSI--> [Pi] --Serial UART--> [Cube] --Telemetry Radio--> [GS / Mission Planner]
                   |                                                    |
                   +------------------ WiFi (SSH) ---------------------+
```

## All Connections

| # | From | To | Protocol | Cable/Link | What flows |
|---|------|----|----------|------------|------------|
| 1 | Camera | Pi | CSI | Ribbon cable | Video frames |
| 2 | Pi | Cube | Serial UART | Wire to TELEM2 | MAVLink commands + telemetry |
| 3 | Cube | GS | Telemetry radio | Wireless (433/915MHz) | Live monitoring data |
| 4 | GS | Pi | WiFi SSH | Wireless | Operator control (Y/N, start/stop) |

## Connection Details

### 1. Camera -> Pi (CSI)
- **Physical**: Ribbon cable from camera module to Pi CSI port
- **Software**: OpenCV `cv2.VideoCapture(0)` or `picamera2`
- **Test**: `python tests/laptop/test_camera.py`
- **Common issues**:
  - Ribbon cable not seated properly
  - Camera not enabled: `sudo raspi-config` -> Interface -> Camera
  - picamera2 needed instead of OpenCV

### 2. Pi -> Cube (Serial UART)
- **Physical**: Pi GPIO TX/RX to Cube TELEM2 port
- **Wiring**:
  | Pi GPIO | Cube TELEM2 |
  |---------|-------------|
  | TX (GPIO 14) | RX |
  | RX (GPIO 15) | TX |
  | GND | GND |
- **Software**: pymavlink `mavutil.mavlink_connection('/dev/ttyAMA0', baud=57600)`
- **Config**: Auto-detected by config.py (checks /dev/ttyAMA0, /dev/ttyACM0, /dev/ttyUSB0)
- **Baud rate**: 57600 default (override with `export DRONE_BAUD=921600`)
- **Test**: `python tests/test_cube.py`
- **Common issues**:
  - Wrong baud rate (try 57600, 115200, 921600)
  - Serial port not enabled: `sudo raspi-config` -> Interface -> Serial
  - TX/RX wires swapped

### 3. Cube -> GS (Telemetry Radio)
- **Physical**: Radio module on Cube TELEM1, matching radio on USB to laptop
- **Software**: Mission Planner auto-detects on COM port
- **No Python code needed** - this is independent of the Pi
- **Test**: Connect in Mission Planner -> check HUD shows attitude data

### 4. GS -> Pi (WiFi SSH)
- **Purpose**: Operator runs main.py remotely, presses Y/N to confirm target
- **Setup**: Pi and laptop on same WiFi network
- **Connect**: `ssh pi@<pi-ip-address>`
- **Find Pi IP**: On Pi run `hostname -I`

## Auto-Detection (config.py)

config.py automatically detects the right connection. Priority order:

```
1. DRONE_CONN environment variable    (always wins)
2. Serial port /dev/ttyAMA0 etc.      (Pi with Cube wired)
3. WSL gateway IP                      (WSL connecting to Windows SITL)
4. tcp:127.0.0.1:5762                  (Windows localhost default)
```

To override: `export DRONE_CONN=tcp:192.168.1.42:5762`

## Pre-Flight Check

Run `python preflight.py` before every flight. It checks:

| Check | What | Auto |
|-------|------|------|
| TCP PORT / SERIAL | Is flight controller reachable? | Detects IP/port from config |
| HEARTBEAT | Is MAVLink responding? | Tests baud rate |
| CAMERA | Does camera open? (REAL mode) | Tests capture |
| AI MODEL | Does detection model load? | Detects backend |

If TCP fails, it prompts you to enter the IP manually and tells you the export command to save it.

## Test Scripts

Run these in order when setting up new hardware:

```
# Phase 1: Pi + Camera
python tests/laptop/test_camera.py    # Camera gives frames?
python tests/laptop/test_cv.py       # Camera + AI detects?
python tests/hardware/benchmark.py   # Inference speed ok?

# Phase 2: Pi + Cube
python tests/test_cube.py        # Heartbeat + GPS + attitude?

# Phase 3: Full system
python tests/test_all.py         # Connectivity map
python preflight.py              # Final check
python main.py                   # Fly
```

## Troubleshooting

### "No heartbeat" on serial
- Check wiring: TX->RX, RX->TX, GND->GND
- Try different baud: `python tests/test_cube.py /dev/ttyAMA0 921600`
- Enable serial: `sudo raspi-config` -> Interface -> Serial -> Yes

### Camera not opening on Pi
- Test hardware: `libcamera-hello`
- Enable camera: `sudo raspi-config` -> Interface -> Camera
- Check ribbon cable is seated properly
- If OpenCV fails, test_camera.py auto-tries picamera2

### TCP connection refused (WSL or Pi to laptop)
- Is Mission Planner / SITL running?
- Firewall rule needed:
  ```
  netsh advfirewall firewall add rule name="SITL" dir=in action=allow protocol=TCP localport=5762
  ```
- Check laptop IP: `ipconfig` (Windows) or `hostname -I` (Linux)

### AI model not loading
- Is `best.tflite` in the project root?
- On Pi: `pip install tflite-runtime "numpy<2"`
- On Windows: `pip install ultralytics`

## Environment Variables

| Variable | Default | Example |
|----------|---------|---------|
| DRONE_MODE | SIMULATION | `export DRONE_MODE=REAL` |
| DRONE_CONN | auto-detect | `export DRONE_CONN=tcp:192.168.1.42:5762` |
| DRONE_BAUD | 57600 | `export DRONE_BAUD=921600` |
