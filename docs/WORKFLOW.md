# SAR Drone — Complete Workflow

The full development-to-flight cycle. Follow top to bottom, repeat.

---

## Phase 1: Develop (Laptop)

**Where:** Laptop, any network
**Env:** `venv\Scripts\activate`

1. Make code changes
2. Test in simulation:
   ```bash
   DRONE_MODE=SIMULATION python main.py --search-area --speed 5
   ```
3. Run tests to make sure nothing broke:
   ```bash
   python -m pytest tests/unit/ tests/integration/ -v
   ```
4. All 127+ tests green? Push:
   ```bash
   git add -A && git commit -m "description" && git push
   ```

---

## Phase 2: Pre-Flight (Pi via PuTTY)

**Where:** Field, Pi connected via PuTTY
**Env:** `source pienv/bin/activate`
**Terminals:** T1 = mavproxy, T2 = scripts

### Terminal 1 — Start mavproxy (stays running)
```bash
sudo /opt/mavlink/mavlink-venv/bin/mavproxy.py \
  --master=/dev/ttyAMA0 --baudrate=921600 --streamrate=10 \
  --out=udpout:127.0.0.1:14550 --out=tcpin:0.0.0.0:5762
```
Wait for `online system 1` and `Mode STABILIZE`.

### Terminal 2 — Pull latest code
```bash
cd ~/dima/Group_Proj
git pull
source pienv/bin/activate
```

### Terminal 2 — System readiness check
```bash
python field_tools/system_readiness.py
```
All critical checks must be **PASS** or **WARN**. Any **FAIL** = fix before flying.

### Terminal 2 — Quick benchmark (optional)
```bash
python tests/day_1_experiments/model_compare.py --frames 20
```

---

## Phase 3: Fly

**Progressive steps — never skip one:**

### Step 1: Manual flight + passive watch (ZERO commands)
Pilot flies on RC. Pi watches and logs.
```bash
python field_tools/passive_watch.py --model cv_models/sar_v2_1088/best.tflite
```
Open browser: `http://PI_IP:8090/`

Review after: Did it detect the dummy? At what altitude? False positives?

### Step 2: Waypoint test (no CV)
Your code flies 4 GPS waypoints. No camera, no detection.
```bash
python tests/flight/2_waypoints.py
```
Proves: arm, takeoff, GUIDED waypoints, land all work.

### Step 3: Full mission
Everything enabled: search, detect, centre, descend, verify, land.
```bash
python main.py --search-area --model cv_models/sar_v2_1088/best.tflite
```
Or with web dashboard:
```bash
python pi_flight.py
```
Open browser: `http://PI_IP:8090/`

---

## Phase 4: Collect Data (Pi, after flight)

**Still on Pi via PuTTY.** Gather everything before packing up.

### Save benchmarks and system state
```bash
mkdir -p pi_data/mavproxy_logs pi_data/cube_logs pi_data/sample_detections

python field_tools/system_readiness.py > pi_data/readiness_report.txt
python tests/day_1_experiments/model_compare.py --frames 50 > pi_data/benchmark_results.txt
```

### Copy hardware-specific data
```bash
cp calibration_data.npz pi_data/ 2>/dev/null
cp logs/flight_log.csv pi_data/
cp mav.tlog mav.parm pi_data/mavproxy_logs/ 2>/dev/null
```

### Download Cube flight logs (in mavproxy Terminal 1)
```
log list
log download latest
```
Then in Terminal 2:
```bash
cp log*.bin pi_data/cube_logs/
```

### Select best detection photos
Don't copy all 200+ photos — pick the useful ones:
```bash
ls detections/
cp detections/CHOSEN_PHOTOS.jpg pi_data/sample_detections/
```

### Push to GitHub
```bash
git add pi_data/
git commit -m "Flight day data: benchmarks + detections + logs"
git push
```

---

## Phase 5: Post-Flight Analysis (Laptop)

**Where:** Laptop, back home
**Env:** `venv\Scripts\activate` (or `test_env` for video analysis)

### Pull flight data
```bash
git pull
```

### Review flight log
Open `pi_data/flight_log.csv` — check timing, states, GPS, detections.

### Review Cube logs
Open `pi_data/cube_logs/log*.bin` in Mission Planner:
- DataFlash Logs → Review a Log
- Check: GPS tracks, altitude profile, battery voltage, vibration

### Review detection photos
Look at `pi_data/sample_detections/` — any false positives? Good detections from what altitude?

### Replay DJI video (if recorded)
```bash
test_env\Scripts\activate
python tests/laptop/video_test.py RealVideo/VIDEO.mp4 --model cv_models/sar_v2_1088/best.tflite
```

### Compare benchmarks
Check `pi_data/benchmark_results.txt` against previous runs in `MEMORY.md`.

---

## Phase 6: Improve Model (Laptop)

**When:** After collecting new detection photos or identifying false positives.

### Label real frames
```bash
python training/label_tool.py --full pi_data/sample_detections/
```

### Add hard negatives (false positive frames)
Copy false positive images to `training/dataset_v2/images/` with empty label files.

### Regenerate dataset
```bash
python training/generate_dataset_v2.py
```

### Train on Colab
1. Upload `training/dataset_v2.zip` to Google Drive
2. Follow `docs/TRAINING_GUIDE.md` Colab cells
3. Download new `best.tflite`

### Deploy new model
```bash
cp new_best.tflite cv_models/sar_v3_NEW/best.tflite
cp new_best.tflite best.tflite
git add best.tflite cv_models/
git commit -m "New model: trained on flight day detections"
git push
```

### Verify
```bash
python -m pytest tests/unit/ tests/integration/ -v
```

Go back to Phase 1.

---

## Quick Reference

| I want to... | Command |
|---|---|
| Run simulation | `DRONE_MODE=SIMULATION python main.py --search-area --speed 5` |
| Run all tests | `python -m pytest tests/unit/ tests/integration/ -v` |
| Check system readiness | `python field_tools/system_readiness.py` |
| Passive watch (safe) | `python field_tools/passive_watch.py` |
| Full mission | `python main.py --search-area --model cv_models/sar_v2_1088/best.tflite` |
| Benchmark models | `python tests/day_1_experiments/model_compare.py --frames 50` |
| Swap model on Pi | `cp cv_models/sar_v2_1088/best.tflite best.tflite` |
| Pull Pi data | `git pull` (after Pi pushes) |
| Label detections | `python training/label_tool.py --full pi_data/sample_detections/` |
| Draw flight plan | `python flight_plans/draw_search_area.py` |

---

## Data Flow Diagram

```
LAPTOP                          GITHUB                         PI
  |                               |                             |
  |-- code changes + git push --> |                             |
  |                               | <-- git pull ------------  |
  |                               |                             |
  |                               |            FLY + COLLECT    |
  |                               |                             |
  |                               | <-- pi_data/ + git push -- |
  | <-- git pull ---------------- |                             |
  |                               |                             |
  |   ANALYSE + RETRAIN           |                             |
  |   new model + git push -----> |                             |
  |                               | <-- git pull ------------  |
  |                               |                             |
  |                          REPEAT                             |
```
