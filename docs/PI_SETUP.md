# Pi Setup & Testing Guide

Step-by-step guide for getting the SAR drone code running on a Raspberry Pi.
Follow in order — each part builds on the previous.

---

## Part 1: Transfer Code to Pi

### 1.1 Connect to Pi

You need SSH access from your laptop to the Pi.

```bash
# Find Pi IP address (run on Pi with monitor, or check router)
hostname -I

# SSH from laptop
ssh pi@<PI-IP-ADDRESS>
# Default password: raspberry (change it with passwd)
```

**If no monitor**: connect Pi to same WiFi as laptop, scan with `ping raspberrypi.local` or use router admin page to find Pi's IP.

### 1.2 Create project folder on Pi

```bash
mkdir -p ~/sar-drone
```

### 1.3 Copy files to Pi

**From your laptop** (not on the Pi), open a terminal and run:

```bash
# Copy the essential files from your Windows machine to Pi
# Replace <PI-IP> with actual Pi IP address

# Core code files
scp config.py vision.py main.py planning.py states.py utils.py preflight.py pi@<PI-IP>:~/sar-drone/

# AI model
scp best.tflite pi@<PI-IP>:~/sar-drone/

# Test scripts (whole folder)
scp -r tests/ pi@<PI-IP>:~/sar-drone/tests/

# Dummy image (for bench testing with generated test images)
scp dummy.png pi@<PI-IP>:~/sar-drone/
```

**Or copy everything at once** (simpler but copies some unnecessary files):
```bash
# From your project folder on laptop:
scp -r . pi@<PI-IP>:~/sar-drone/
```

**Or use git** (if you have a remote repo):
```bash
# On the Pi:
cd ~/sar-drone
git clone <your-repo-url> .
# best.tflite is included in git, so it comes with the clone
```

### 1.4 Verify files are on Pi

SSH into Pi and check:
```bash
cd ~/sar-drone
ls -la
```

You MUST see these files:
```
config.py          ← settings (altitudes, camera, connection)
vision.py          ← AI detection (auto-picks TFLite on Pi)
main.py            ← full mission code
planning.py        ← search pattern generation
states.py          ← state machine definitions
utils.py           ← helper functions
preflight.py       ← pre-flight connectivity check
best.tflite        ← AI MODEL FILE (3.3 MB) — included in git
dummy.png          ← dummy image for test image generation
tests/             ← all test scripts
```

**If `best.tflite` is missing, nothing will detect anything.** It's tracked in git so `git clone` will include it, but double-check it's there after copying.

### What you DON'T need on Pi

| File | Why not needed |
|------|---------------|
| `venv/` | You'll create a fresh Pi venv |
| `map.jpg` (11.8 MB) | Simulation only — not used on Pi |
| `simulation.py` | Laptop simulation only |
| `generate_dataset.py` | Training data generation — laptop only |
| `project_data/` | Training/project data — laptop only |
| `requirements_dev.txt` | Laptop dev dependencies — not needed on Pi |
| `Dockerfile.pi-test` | Docker testing only |
| `.git/` | Not needed unless you want git on Pi |

---

## Part 2: Set Up Python Environment on Pi

### 2.1 Create virtual environment

```bash
cd ~/sar-drone
python3 -m venv --system-site-packages pienv
source pienv/bin/activate
```

**Why `--system-site-packages`?** Because `picamera2` is installed system-wide on Raspberry Pi OS and cannot be pip-installed. This flag lets the venv see it.

### 2.2 Install dependencies

```bash
pip install -r requirements_pi.txt
```

That's it. Only 4 packages (defined in `requirements_pi.txt`):

| Package | What it's for |
|---------|--------------|
| `pymavlink` | Talks to Cube (MAVLink over serial) |
| `opencv-python-headless` | Camera + image processing (no GUI needed on Pi) |
| `numpy<2` | Required by TFLite (v2 breaks things) |
| `tflite-runtime` | Lightweight AI inference (instead of full TensorFlow) |

**If `tflite-runtime` fails to install:**
```bash
# Try the official Google wheel
pip install --extra-index-url https://google-coral.github.io/py-repo/ tflite-runtime

# Or install full tensorflow lite (heavier but works)
pip install tensorflow
```

### 2.3 Verify the environment

```bash
python -c "import cv2; print('OpenCV:', cv2.__version__)"
python -c "import numpy; print('NumPy:', numpy.__version__)"
python -c "from tflite_runtime.interpreter import Interpreter; print('TFLite: OK')"
python -c "from pymavlink import mavutil; print('pymavlink: OK')"
```

All four should print without errors.

### 2.4 Every time you SSH in

```bash
cd ~/sar-drone
source pienv/bin/activate
```

Add to `~/.bashrc` to auto-activate (optional):
```bash
echo 'cd ~/sar-drone && source pienv/bin/activate' >> ~/.bashrc
```

---

## Part 3: Enable Hardware on Pi

### 3.1 Enable camera

```bash
sudo raspi-config
# → Interface Options → Camera → Enable
# → Reboot
```

Test camera hardware directly:
```bash
libcamera-hello    # should show a preview for 5 seconds
```

### 3.2 Enable serial (for Cube connection)

```bash
sudo raspi-config
# → Interface Options → Serial Port
# → "Login shell over serial?" → NO
# → "Enable serial hardware?" → YES
# → Reboot
```

After reboot, check serial port exists:
```bash
ls /dev/ttyAMA0
# Should show the file. If not, try /dev/ttyACM0 or /dev/ttyUSB0
```

### 3.3 Wiring: Pi to Cube

| Pi GPIO | Cube TELEM2 |
|---------|-------------|
| TX (GPIO 14, pin 8) | RX |
| RX (GPIO 15, pin 10) | TX |
| GND (pin 6) | GND |

**Most common mistake**: TX and RX swapped. If test_cube.py gets no heartbeat, swap the two data wires.

---

## Part 4: Run Tests (Step by Step)

**Always activate the venv first:**
```bash
cd ~/sar-drone
source pienv/bin/activate
```

### Step 1: Camera gives frames?

```bash
python tests/pi_1_camera.py
```

**Pass**: Prints "Camera opened successfully" + frame dimensions (e.g. 640x480).

**Fail**:
- Check ribbon cable is seated properly in CSI port
- Run `libcamera-hello` — if that fails, it's a hardware/config issue
- Script auto-tries picamera2 if OpenCV fails

### Step 2: AI detects dummy?

```bash
python tests/pi_2_detect.py           # with display (if monitor connected)
python tests/pi_2_detect.py --headless  # over SSH (no display needed)
```

Hold a printout of the dummy in front of the camera.

**Pass**: Bounding boxes on screen (or "DETECTED" prints in headless mode).

**Fail**:
- Is `best.tflite` in `~/sar-drone/`? Run `ls -la best.tflite`
- Run `python -c "from tflite_runtime.interpreter import Interpreter; print('OK')"`

### Step 3: Inference speed OK?

```bash
python tests/pi_3_benchmark.py
```

**Pass**: Average inference < 200ms per frame.

**Compare** with your laptop results — detection position should be similar.

### Step 3b: Camera FPS + blur test

```bash
python tests/pi_8_camera_test.py --headless
```

**What it tells you**: Camera FPS, pipeline FPS (camera + AI), whether motion blur kills detection.

### Step 3c: Resolution sweet spot

```bash
python tests/pi_9_resolution_test.py --headless
```

**What it tells you**: Which resolution is fastest while still detecting. If 320x240 is fast enough and still detects, update config.py:
```python
IMAGE_W = 320
IMAGE_H = 240
```

### Step 4: Bench FOV check

```bash
python tests/pi_6_fov_test.py --headless
```

Hold camera at a known height above a ruler. Enter measurements. Script checks if config.py FOV is correct.

### Step 5: Cube heartbeat + GPS?

**Requires Cube wired to Pi (see Part 3 wiring).**

```bash
python tests/test_cube.py
```

**Pass**: Heartbeat received, yaw/pitch/roll printed, GPS if outdoors.

**Fail**:
- Swap TX/RX wires
- Try different baud: `python tests/test_cube.py /dev/ttyAMA0 921600`
- Check serial is enabled: `ls /dev/ttyAMA0`

### Step 6: CV + Cube together (THE BIG TEST)

```bash
python tests/pi_4_detect_and_log.py
```

Carry the drone by hand over a dummy printout. You should get:
- Buzzer beeps on the Cube
- Guidance commands: LEFT / RIGHT / CENTRED
- CSV log entries in `detection_log.csv`

**This is the most important bench test.** If this works, the system is ready for flight day.

### Step 7: Pre-flight check

```bash
python preflight.py
```

**Pass**: All checks green (serial, heartbeat, camera, AI model).

---

## Part 5: Quick Troubleshooting

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError: No module named 'tflite_runtime'` | `pip install tflite-runtime` or `pip install ai-edge-litert` (Python 3.13+) |
| `ModuleNotFoundError: No module named 'cv2'` | `pip install opencv-python-headless` |
| `ModuleNotFoundError: No module named 'picamera2'` | Already installed system-wide. Did you use `--system-site-packages` when creating venv? |
| `[VISION] Model file not found` | `best.tflite` is missing. Copy it: `scp best.tflite pi@<IP>:~/sar-drone/` |
| `Camera failed to open` | `sudo raspi-config` → enable camera → reboot |
| `Camera busy` error | Another script is using the camera. Run `pkill -f python` first |
| `No heartbeat` from Cube | Use mavproxy bridge (see below). Check baud rate (921600). |
| `numpy` version error | `pip install "numpy<2"` |
| `Permission denied` on serial | `sudo usermod -a -G dialout $USER` then logout/login |
| Blue-tinted camera images | Do NOT use `cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)` — IMX296 outputs BGR already |
| `sudo python3` missing cv2 | Use venv python3 instead of sudo python3 |

### IMX296 Camera Color Note

The Pi Global Shutter Camera (IMX296) outputs **BGR data** despite picamera2 calling it RGB888.
Do NOT add `cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)` — this double-swaps channels and causes
a blue tint. Use frames directly from `picam.capture_array()`.

### Cube Connection via Mavproxy Bridge

Python 3.13 has a known issue with pyserial causing broken MAVLink reads over direct serial.
Use mavproxy as a UDP bridge instead:

```bash
# Terminal 1: Start mavproxy bridge
sudo /opt/mavlink/mavlink-venv/bin/mavproxy.py \
  --master=/dev/ttyAMA0 \
  --baudrate=921600 \
  --streamrate=10 \
  --out=udpout:127.0.0.1:14550 \
  --out=tcpin:0.0.0.0:5762

# Terminal 2: Run your scripts (they connect via UDP)
source pienv/bin/activate
python tests/test_cube.py
```

The `udpout:127.0.0.1:14550` output is for Pi scripts (config.py auto-detects this).
The `tcpin:0.0.0.0:5762` output is for Mission Planner on your laptop (connect TCP to Pi's IP).

---

## What's Different from Laptop

| | Laptop | Pi |
|---|--------|-----|
| AI backend | Ultralytics YOLO (fast, accurate) | TFLite (lightweight) |
| Camera | USB webcam / simulated | CSI ribbon (may need picamera2) |
| Cube connection | TCP to SITL simulator | Serial UART /dev/ttyAMA0 |
| Speed | Fast (GPU possible) | Slower (CPU only, target <200ms) |
| Display | OpenCV windows | Headless (use `--headless` flag) |

The code handles this automatically — `vision.py` picks the right AI backend, `config.py` picks the right connection.

---

## Checklist: Is Pi Ready?

```
[ ] Files copied to ~/sar-drone/ (including best.tflite)
[ ] Venv created and activated (source pienv/bin/activate)
[ ] pip packages installed (pymavlink, opencv, numpy<2, tflite-runtime)
[ ] Camera enabled (raspi-config)
[ ] Serial enabled (raspi-config)
[ ] Step 1 passes (camera frames)
[ ] Step 2 passes (AI detection)
[ ] Step 3 passes (speed < 200ms)
[ ] Step 5 passes (Cube heartbeat)
[ ] Step 6 passes (CV + Cube together)
[ ] Step 7 passes (preflight)
→ READY FOR FLIGHT DAY
```
