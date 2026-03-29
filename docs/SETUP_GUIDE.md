# Quick Setup Guide

**Branch:** `Working7.0`
**Repo:** https://github.com/DimaChup/Group_Proj

## Clone & Setup

```bash
git clone https://github.com/DimaChup/Group_Proj.git
cd Group_Proj
git checkout Working7.0
```

## Create Python Environment

### Windows
```bash
python -m venv venv
venv\Scripts\activate
python -m pip install -r requirements_dev.txt
```

### Linux / WSL
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements_linux.txt
```

### Raspberry Pi
```bash
python3 -m venv --system-site-packages pienv
source pienv/bin/activate
pip install -r requirements_pi.txt
```

## Verify Install

```bash
python -c "import cv2; print('OpenCV:', cv2.__version__)"
python -c "import ultralytics; print('YOLO:', ultralytics.__version__)"
python -c "from pymavlink import mavutil; print('pymavlink: OK')"
```

## Run

You need SITL running first (Mission Planner or mavproxy):
```
--home=51.423406,-2.671446,50,155
```

### Lawnmower (default)
```bash
set DRONE_MODE=SIMULATION
python main.py
```

### Spiral pattern
```bash
set DRONE_MODE=SIMULATION
python main.py --spiral
```

### Dry run (no SITL needed)
```bash
python main.py --dry-run
python main.py --dry-run --spiral
```

## Key Flags

| Flag | What it does |
|------|-------------|
| `--spiral` | Use perimeter spiral instead of lawnmower |
| `--dry-run` | Print waypoints, no flying |
| `--headless` | No GUI windows (for SSH/Pi) |
| `--alt 25` | Override search altitude |
| `--no-nfz` | Disable SSSI geofence |
| `--smart-detect` | Require consecutive detections |

## What Changed (Working7.0)

- `--spiral` flag: Zian's perimeter spiral as alternative search pattern
- Same state machine, same detection, same NFZ — only waypoint shape changes
- Pattern comparison analysis in `tools/pattern_analysis/`
- Visualizer improvements in `tools/pattern_visualizer.py`
