# Quick-Start Cheatsheet

## 5-Minute Setup (Windows Laptop)

```bash
git clone https://github.com/DimaChup/Group_Proj.git
cd Group_Proj
git checkout MainOne2

python -m venv test_env
test_env\Scripts\activate          # Windows cmd
# source test_env/bin/activate     # Linux/WSL

python -m pip install -r requirements_dev.txt

python main.py --dry-run           # verify lawnmower pattern (no GPS/Cube needed)
```

## Run Passive Watch

### Fake Mode (laptop, replays DJI video)

```bash
python field_tools/passive_watch.py --fake --smart-estimate
# Open http://localhost:8090 in browser
```

### Real Mode (Pi, live camera + mavproxy)

```bash
source pienv/bin/activate
python field_tools/passive_watch.py --smart-estimate
# Browser dashboard: http://PI_IP:8090
```

Passive watch sends ZERO flight commands. Safe to run anytime.

## Run Full Mission (Simulation)

```bash
set DRONE_MODE=SIMULATION          # Windows
python main.py                     # needs SITL running in Mission Planner
python main.py --speed 5           # 5x speedup
python main.py --headless          # no cv2 windows (Pi/SSH)
```

## Key Files

| File | Purpose |
|------|---------|
| `main.py` | Full autonomous mission (state machine) |
| `field_tools/passive_watch.py` | Passive detection, ZERO commands |
| `config.py` | All settings (altitudes, speeds, camera, GPS) |
| `vision.py` | AI detection (TFLite on Pi, Ultralytics on laptop) |
| `best.tflite` | Active AI model (all scripts read this) |
| `planning.py` | Lawnmower search pattern generator |
| `utils.py` | GPS/pixel math (GeoTransformer) |

## Common Tasks

**Swap AI model:**
```bash
cp cv_models/sar_v2_1088/best.tflite best.tflite
```

**Run unit tests:**
```bash
python tests/run_all_tests.py
```

**Train a new model:** see `docs/TRAINING_WORKFLOW_V3.md`

**Calibrate camera FOV:** see `docs/CALIBRATION_GUIDE.md`

**Pre-flight checks:** see `docs/FLIGHT_DAY_CHECKLIST.md`

## Pi Setup (One-Time)

```bash
git clone https://github.com/DimaChup/Group_Proj.git ~/sar-drone
cd ~/sar-drone && git checkout MainOne2
python3 -m venv --system-site-packages pienv
source pienv/bin/activate
pip install -r requirements_pi.txt
```

Start mavproxy before any flight script:
```bash
sudo /opt/mavlink/mavlink-venv/bin/mavproxy.py \
  --master=/dev/ttyAMA0 --baudrate=921600 --streamrate=10 \
  --out=udpout:127.0.0.1:14550 --out=tcpin:0.0.0.0:5762
```

## Available Models

| Model | Path | Notes |
|-------|------|-------|
| SAR v2 (best) | `cv_models/sar_v2_1088/best.tflite` | 11.7MB, mAP50=0.995 |
| SAR 640 | `cv_models/sar_640/best.tflite` | Earlier training |
| COCO person | `models/human.tflite` | 80-class backup, 13MB |

All models are drop-in: same input `[1,640,640,3]`, same output `[1,5,8400]`.

## CLI Flags (main.py)

```
--dry-run          No arming/flying. Print waypoints + save pattern image.
--headless         No cv2 windows. Auto-enabled on Pi.
--alt <m>          Override search altitude (default 35m).
--speed <factor>   SITL speedup (default 1).
--model <path>     TFLite model path (default best.tflite).
--smart-detect     Require consecutive frames before investigating.
--no-nfz           Disable SSSI geofence.
```

## Further Reading

- `CLAUDE.md` — full project context (the ground truth document)
- `docs/ARCHITECTURE.md` — system overview and hardware
- `docs/PI_SETUP.md` — detailed Pi setup
- `docs/FLIGHT_DAY_CHECKLIST.md` — printable flight day checklist
