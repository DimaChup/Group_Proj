# Process Map -- SAR Drone Project

> Every major workflow in the project, step by step. Follow the arrows. Know what feeds what.

---

## 1. Development Workflow

The laptop is the single source of truth. Code never gets edited on the Pi.

```
LAPTOP                          GITHUB                     PI
  |                               |                        |
  |  1. Edit code (VS Code)       |                        |
  |  2. Test in SIMULATION        |                        |
  |     (SITL + simulated cam)    |                        |
  |  3. git add + commit + push ---->                      |
  |                               |   4. git pull  <-------|
  |                               |                        |
  |                               |   5. Test on hardware  |
  |                               |      (real camera,     |
  |                               |       real Cube,       |
  |                               |       real GPS)        |
  |  6. Review results,           |                        |
  |     fix issues, repeat        |                        |
```

### Steps in detail

| # | Step | Input | Output | Tool / Command | Notes |
|---|------|-------|--------|----------------|-------|
| 1 | Edit code | Bug report, feature idea | Modified `.py` files | VS Code on laptop | Always edit on laptop, never on Pi |
| 2 | Simulate on laptop | Modified code | Pass/fail, logs | `set DRONE_MODE=SIMULATION && python main.py` | SITL must be running (Mission Planner or mavproxy) |
| 3 | Push to GitHub | Tested code | Remote branch updated | `git add -A && git commit -m "msg" && git push` | Commit after each working milestone |
| 4 | Pull on Pi | Remote branch | Local code on Pi | `cd ~/dima/Group_Proj && git pull` | Over SSH (PuTTY) |
| 5 | Test on hardware | Code on Pi, assembled drone | Pass/fail, detection images, logs | `source pienv/bin/activate && python <script>` | Progressive: bench first, then flight |
| 6 | Iterate | Test results | Code fixes | Back to step 1 | Never edit on Pi -- bring fixes back to laptop |

**What can be parallel**: Steps 1-2 (laptop dev) and unrelated Pi hardware tests are independent. Multiple scripts can be tested in simulation without waiting for Pi.

**What must be sequential**: Push (3) before pull (4). Simulation pass (2) before pushing to Pi. Bench test before flight test.

### Environment differences

| Platform | Venv | Requirements file | Camera | AI backend |
|----------|------|-------------------|--------|------------|
| Windows laptop | `test_env` | `requirements_dev.txt` | Webcam or simulated | Ultralytics (PyTorch) |
| WSL/Linux | `venv` | `requirements_linux.txt` | None (sim only) | Ultralytics (PyTorch) |
| Raspberry Pi 5 | `pienv` | `requirements_pi.txt` | picamera2 (IMX296) | TFLite (`ai-edge-litert`) or NCNN |

---

## 2. Model Training Pipeline

End-to-end: from raw data to a deployed `.tflite` on the Pi.

```
[Flight video / Photos]
        |
        v
  1. Collect frames -----> raw images (JPG)
        |
        v
  2. Label frames -------> images/ + labels/ (YOLO format)
        |
        v
  3. Generate synthetic --> syn_*.jpg + neg_*.jpg + labels
        |
        v
  4. Zip dataset --------> dataset_v2.zip
        |
        v
  5. Upload to Drive ----> Google Drive
        |
        v
  6. Train on Colab -----> best.pt (YOLO weights)
        |
        v
  7. Export TFLite+NCNN -> best.tflite + ncnn/
        |
        v
  8. Download to laptop -> cv_models/sar_vN/
        |
        v
  9. Test on laptop -----> video_test.py results
        |
        v
  10. Deploy to Pi ------> cp best.tflite ~/dima/Group_Proj/best.tflite
```

### Steps in detail

| # | Step | Input | Output | Tool / Command | Where |
|---|------|-------|--------|----------------|-------|
| 1 | Collect frames | DJI video or `capture_training.py` output | Raw JPG frames | `capture_training.py` (SPACE=photo, V=video) | Pi (field) or laptop (video) |
| 2 | Label frames | Raw JPGs with dummy visible | `real_*.jpg` + `real_*.txt` (YOLO labels) | `python training/label_tool.py --full <dir>` | Laptop |
| 3 | Generate synthetic | `dummy.png` + DJI backgrounds | 300 synthetic + 50 negatives + labels | `python training/generate_dataset_v2.py` | Laptop |
| 4 | Zip dataset | `dataset_v2/` directory | `dataset_v2.zip` | Right-click zip or `zip -r` | Laptop |
| 5 | Upload to Drive | `dataset_v2.zip` | File on Google Drive | Browser upload | Laptop |
| 6 | Train | `dataset.yaml`, images, labels | `best.pt`, `results.png`, `confusion_matrix.png` | Colab: `model.train(data=..., imgsz=1088, epochs=150, batch=8)` | Google Colab (T4 GPU) |
| 7 | Export | `best.pt` | `best.tflite` (float32) + `ncnn/` dir | Colab: `model.export(format='tflite', imgsz=640)` | Google Colab |
| 8 | Download | Colab export zip | `cv_models/sar_vN/` with tflite + pt + ncnn | Colab download + unzip | Laptop |
| 9 | Test on laptop | Model + DJI video | Detection overlay, mAP, confidence stats | `python tests/laptop/video_test.py` | Laptop |
| 10 | Deploy to Pi | Tested model file | Active model on Pi | `cp cv_models/sar_v2_1088/best.tflite best.tflite` + git push + git pull on Pi | Laptop then Pi |

**What can be parallel**: Steps 2 (labelling) and 3 (synthetic generation) are independent -- real labels and synthetic labels are separate. Step 9 (laptop test) can happen while Pi is doing other tasks.

**What must be sequential**: Label (2) before zip (4). Train (6) before export (7). Test on laptop (9) before deploying to Pi (10).

### Key parameters

```
Training:     imgsz=1088, epochs=150, batch=8, patience=30
Export:        imgsz=640 (TFLite runtime always resizes to 640)
Input shape:   [1, 640, 640, 3]
Output shape:  [1, 5, 8400]
Current best:  cv_models/sar_v2_1088/best.tflite (mAP50=0.995)
```

---

## 3. Calibration Pipeline

Order matters. Each calibration depends on the previous one being correct.

```
  1. Lens distortion calibration
        |
        v
  2. FOV / focal length calibration
        |
        v
  3. GPS estimate calibration
        |
        v
  4. Ground truth validation
```

### Steps in detail

| # | Step | Input | Output | Tool / Command | Why this order |
|---|------|-------|--------|----------------|----------------|
| 1 | Lens calibration | Checkerboard images (calib.io 14x9, 28mm squares) | `calibration_data.npz` (camera matrix, distortion coefficients) | `python tests/calibration/lens_calibrate.py` | Undistortion corrects all downstream pixel measurements |
| 2 | FOV calibration | Camera at known height, ruler on ground | `FOCAL_LENGTH_MM` value for `config.py` | `python tests/calibration/fov_calibrate.py --headless` (bench) or `python tools/fov_calibrate_video.py` (from video) | Wrong FOV = wrong GPS estimates. Must use undistorted images. |
| 3 | GPS estimate calibration | Dummy at known GPS position, drone hovering overhead | Corrected focal length, GPS offset | `python tests/calibration/gps_estimate_calibrate.py` or `gps_calibrate_gui.py` | Validates pixel-to-GPS conversion accuracy |
| 4 | Ground truth validation | Multiple flyovers of known-position dummy | CEP50, CEP95 error stats | `python tests/calibration/gps_ground_truth.py` or `tests/day_1_experiments/gps_accuracy.py` | Confirms end-to-end accuracy under real conditions |

**What can be parallel**: Nothing. This pipeline is strictly sequential.

**What must be sequential**: Lens (1) before FOV (2), because undistortion changes pixel geometry. FOV (2) before GPS estimate (3), because focal length is an input. GPS estimate (3) before ground truth (4), because you need the calibrated pipeline to validate.

### Current calibration values

```python
# config.py
SENSOR_WIDTH_MM = 5.02    # IMX296 datasheet (fixed)
FOCAL_LENGTH_MM = 5.46    # Calibrated 2026-03-11 (92cm visible at 1m)
IMAGE_W = 1456            # Pi camera native
IMAGE_H = 1088            # Pi camera native
```

---

## 4. Flight Testing Pipeline

Progressive trust-building. Each step proves something new before adding risk. Never skip a step.

```
  Step 0: Bench tests (no props, no flying)
    0a. Cube commands -----> Pi can talk to Cube
    0b. Bench mission -----> Full command sequence works
    0c. Feedback test -----> Vision-to-GPS pipeline works
    0d. Planning test -----> Lawnmower pattern is correct
    0e. Geofence test -----> NFZ boundaries work
    0f. Servo test --------> Payload release works
        |
        v
  Step 1: Mission Planner AUTO (no custom code)
    Upload 4 waypoints in MP, fly in AUTO, RTL
    Proves: Cube, GPS, motors, RTL all work
        |
        v
  Step 2: Waypoint script (no CV)
    python tests/flight/2_waypoint_test.py
    Proves: MAVLink GUIDED commands work on real hardware
        |
        v
  Step 3: Manual flight + passive CV (ZERO commands)
    Pilot flies RC, Pi runs passive_watch.py
    Proves: CV detects from altitude, calibrates detection range
        |
        v
  Step 4: Autonomous search + CV logging only (no action)
    main.py with detect-only mode
    Proves: Lawnmower pattern works, CV detects, no surprises
        |
        v
  Step 5: Full autonomous mission
    main.py with everything enabled
    Operator confirms Y/N at verify stage
```

### Steps in detail

| Step | Script | Sends commands? | Uses CV? | Requires flight? | What it proves |
|------|--------|-----------------|----------|-------------------|----------------|
| 0a | `tests/flight/0a_cube_commands.py` | Yes (bench) | No | No | Pi-to-Cube command path works |
| 0b | `tests/flight/0b_bench_mission.py` | Yes (bench) | No | No | Full mission command sequence (no props) |
| 0c | `tests/flight/0c_feedback_test.py` | No | Yes | No | Vision-to-GPS estimation pipeline |
| 0d | `tests/flight/0d_planning_test.py` | No | No | No | Lawnmower pattern, bounds, NFZ avoidance |
| 0e | `tests/flight/0e_geofence_test.py` | No | No | No | NFZ boundaries, waypoint filter, repulsion |
| 0f | `tests/flight/0f_servo_test.py` | Yes (servo) | No | No | Payload servo PWM |
| 1 | Mission Planner UI | Via MP | No | Yes | Aircraft flies, GPS nav works, kill switch works |
| 2 | `tests/flight/2_waypoint_test.py` | Yes | No | Yes | MAVLink GUIDED commands fly to GPS coords |
| 3 | `passive_watch.py` or `tests/flight/1_passive_flight.py` | No (zero) | Yes | Yes (manual RC) | CV works from real altitude |
| 4 | `main.py` (detect-only) | Yes | Yes (log only) | Yes | Full search pattern, detection logging |
| 5 | `main.py` | Yes | Yes | Yes | Complete L2 mission |

**What can be parallel**: Step 0a-0f bench tests are independent of each other. Step 1 (MP AUTO) and Step 2 (waypoint script) can happen in either order, but MP AUTO is safer first. Step 3 (passive CV) can run simultaneously with Steps 1-2 if a colleague flies.

**What must be sequential**: All bench tests (0) before any flight (1+). Step 1 before Step 2. Steps 1-3 before Step 4. Step 4 before Step 5.

### Safety hierarchy

```
RC pilot  >  kill switch (STABILIZE)  >  RC override  >  Python script  >  geofence
```

The pilot always wins. If RC switches away from GUIDED, the script stops all commands.

---

## 5. Report Writing Pipeline

What feeds into D4 (Flight Readiness Review), D5 (Flight Test), D6 (Final Report), and D7 (Peer Assessment).

```
Code + Simulation results -----> D4: Flight Readiness Review (10%)
          |
          v
Flight test data + videos -----> D5: Flight Test (20%)
          |
          v
All of the above + analysis ---> D6: Final Report (30%)
          |
          v
Individual reflections --------> D7: Peer Assessment (12.5%)
```

### Evidence sources for D6 Final Report

| Report section | Source | Files / Scripts |
|----------------|--------|-----------------|
| System architecture | Code + docs | `CLAUDE.md`, `docs/ARCHITECTURE.md`, `docs/DESIGN_DECISIONS.md` |
| CV pipeline | Model training, benchmarks | `cv_models/`, `docs/TRAINING_GUIDE.md`, `tests/hardware/benchmark.py` results |
| Search pattern | Planning algorithm | `planning.py`, `main.py --dry-run` output, `pattern_visualizer_v7.py` |
| State machine | State flow diagrams | `states.py`, `main.py`, `docs/main_blueprint.md` |
| Calibration results | Calibration pipeline output | `tests/calibration/` results, `config.py` values |
| Flight test results | Flight data | Detection images, CSV logs, `flight_log.csv`, video recordings |
| GPS accuracy | Experiment data | `tests/day_1_experiments/gps_accuracy.py` CSV output |
| Detection performance | Altitude/speed sweeps | `tests/day_1_experiments/altitude_sweep.py`, `speed_sweep.py` CSV output |
| Ground station UI | Screenshots | `pi_flight.py` browser dashboard, `passive_watch.py` stream |
| Safety case | Geofence, RC override, kill switch | `docs/FLIGHT_DAY_CHECKLIST.md`, test logs |
| Comparison to literature | Reference analysis | `docs/SAR_COMPARISON.md` |
| Requirements compliance | R01-R12 traceability | `docs/PROJECT_STATUS.md` L2 stepping stones |
| SE process | WBS, Gantt, trade studies | `dashboard/` (React app at localhost:5050) |

### Evidence collection during flights

| Data type | How it is collected | Where it is saved |
|-----------|--------------------|--------------------|
| Detection images | `passive_watch.py --simple-names` | `detections/` dir on Pi, with GPS in filename |
| Detection metadata | `passive_watch.py` (JSON mode) | `detections/*.json` on Pi |
| Flight log | `main.py`, `pi_flight.py` | `flight_log.csv` |
| Video recording | `capture_training.py --record` | `.mp4` + per-frame GPS `.csv` on Pi |
| GPS experiment data | `tests/day_1_experiments/*.py` | CSV files on Pi |
| Telemetry | Mission Planner `.tlog` | Laptop (MP auto-saves) |

---

## 6. Colleague Integration -- Passive Detection During Manual Flight

How `passive_watch.py` fits into a colleague's manual RC flight. This is the L1 (Manual MVP) workflow.

```
COLLEAGUE (RC Pilot)              PI (passive_watch.py)           LAPTOP (Ground Station)
      |                                    |                              |
      |  1. Fly drone manually             |                              |
      |     over search area               |                              |
      |                                    |                              |
      |                           2. Camera captures frames               |
      |                           3. AI runs detection                    |
      |                           4. GPS estimate calculated              |
      |                           5. Detection image saved                |
      |                           6. MJPEG stream updated                 |
      |                                    |                              |
      |                                    |-----> 7. Browser shows       |
      |                                    |       stream + detections    |
      |                                    |       http://PI_IP:8090      |
      |  8. Buzzer beeps on detection      |                              |
      |  9. Pilot notes location,          |                              |
      |     flies to investigate           |                              |
      |                                    |                              |
      | 10. Land, review saved images      |                              |
```

### What the colleague needs

| Item | Details |
|------|---------|
| **Script** | `passive_watch.py --headless --stream` on Pi |
| **URL** | `http://PI_IP:8090` in browser on laptop |
| **Commands sent to drone** | Zero. Completely safe. |
| **What Pi does** | Camera + AI + GPS estimate + save images + buzzer |
| **Flags for training data** | `--simple-names` (clean filenames with GPS), `--class-filter person` (for human.tflite model) |

### Pre-flight setup for colleague

```bash
# Terminal 1 on Pi: start mavproxy
sudo /opt/mavlink/mavlink-venv/bin/mavproxy.py \
  --master=/dev/ttyAMA0 --baudrate=921600 --streamrate=10 \
  --out=udpout:127.0.0.1:14550 --out=tcpin:0.0.0.0:5762

# Terminal 2 on Pi: start passive watch
cd ~/dima/Group_Proj && source pienv/bin/activate
python passive_watch.py --headless --stream --simple-names
```

### Flight plan for data collection

Fly over the dummy at these altitudes (one pass each):
- 10m, 15m, 20m, 25m, 30m

After landing, the saved images + CSV tell us:
- Maximum detection altitude
- Detection rate per altitude
- False positive count
- GPS estimate accuracy (compare saved GPS to known dummy position)

These results directly feed into `config.py` tuning (TARGET_ALT, CONFIDENCE_THRESHOLD, SEARCH_SPEED_MPS) and into the D6 report.

---

## 7. Data Collection Pipeline

From raw flight footage to a trained model, with all the tools in between.

```
[Manual RC flight with capture_training.py]
        |
        v
  Raw video (.mp4) + GPS telemetry (.csv)
        |
        v
  Extract frames (ffmpeg or capture_training SPACE key)
        |
        v
  Label with label_tool.py --full
        |
        v
  real_*.jpg + real_*.txt (YOLO labels)
        |                                  [dummy.png + DJI backgrounds]
        |                                          |
        v                                          v
  Copy into dataset_v2/              training/generate_dataset_v2.py
        |                                          |
        |    syn_*.jpg + neg_*.jpg + labels  <------
        |                   |
        v                   v
      dataset_v2/ (merged: real + synthetic + negatives)
              |
              v
        dataset_v2.zip --> upload to Drive --> Colab train
              |
              v
        best.tflite --> deploy to Pi
```

### Tools at each step

| Step | Script | Input | Output | Flags |
|------|--------|-------|--------|-------|
| Capture video | `capture_training.py` | Live camera + GPS | `.mp4` + per-frame GPS `.csv` | `--record`, `--undistort` |
| Capture photos | `capture_training.py` | Live camera | Individual `.jpg` frames | SPACE key for single frame |
| Save detection images | `passive_watch.py` | Flight with detections | Detection crops with GPS in filename | `--simple-names` |
| Label frames | `training/label_tool.py` | Directory of JPGs | YOLO-format `.txt` labels | `--full` (native res), `--output <dir>` |
| Generate synthetic | `training/generate_dataset_v2.py` | `dummy.png` + backgrounds | 300 synthetic + 50 negatives | Hardcoded in script |
| Merge dataset | Manual copy | Real labels + synthetic | `dataset_v2/` with `dataset.yaml` | -- |
| Train | Colab notebook | `dataset_v2.zip` | `best.pt` | `imgsz=1088, epochs=150, batch=8` |
| Export | Colab | `best.pt` | `best.tflite` + `ncnn/` | `format='tflite', imgsz=640` |
| Test model on video | `tests/laptop/video_test.py` | Model + DJI video | Visual overlay, detection stats | -- |
| Compare models | `tests/laptop/video_test_compare.py` | Two models + video | Side-by-side A/B comparison | M key switches models |

### What can be parallel

- Capturing photos (`capture_training.py`) and passive detection (`passive_watch.py`) can run on different flights
- Labelling real frames and generating synthetic data are independent
- Testing model on laptop video and deploying to Pi are independent

### What must be sequential

- Capture before label
- Label + generate before merge
- Merge before zip
- Zip before train
- Train before export
- Export before deploy
- Test on laptop before deploying to Pi (catch issues early)

---

## Summary: What Feeds What

```
Calibration Pipeline -----> config.py values -----> All flight scripts
                                                         |
Development Workflow -----> Tested code on Pi            |
                                |                        |
Flight Testing Pipeline -----> Flight data + logs        |
         |                          |                    |
         |   Colleague Integration -|                    |
         |                          |                    |
         v                          v                    v
Data Collection Pipeline -----> Training data -----> Model Training Pipeline
                                                         |
                                                         v
                                                    Deployed model
                                                         |
                                   All results + data + code
                                                         |
                                                         v
                                              Report Writing Pipeline
                                                         |
                                                    D4, D5, D6, D7
```
