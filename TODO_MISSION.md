# TODO: Simulation, Mission & Flight Day

**Priority order: top = most urgent**

---

## Simulation Testing (on laptop)

- [x] All 12 requirements met in SITL
- [x] --sim-tilt: perspective warp camera simulation
- [x] Tilt compensation: 1440 tests pass, exact inverse verified
- [x] --noise flag: GPS/attitude noise simulation
- [x] --blur, --shake: motion effects
- [x] Two-step centering: hover 3s at rough estimate
- [x] Detection photos saved to mission_detections/
- [x] Landing distance from casualty displayed
- [x] Geofence RTL works without crashing dashboard
- [ ] Test with `--sim-tilt --noise 1.0` (realistic noise)
- [ ] Test with `--sim-tilt --noise 2.0` (stress test)
- [ ] Verify two-step centering visually works with tilt
- [ ] Colab multi-class training (retry when GPU quota resets)
- [ ] If trained: deploy new 5-class model, test in simulation

## Flight Day Preparation (on Pi)

**YOUR JOB: calibrate + give Robin passive_watch**

### Before Flight Day
- [ ] Push latest code to GitHub: `git push`
- [ ] Pull on Pi: `cd ~/dima/Group_Proj && git pull`
- [ ] Copy best model: `cp cv_models/sar_v2_1088/best.tflite best.tflite`
- [ ] Charge batteries + power bank
- [ ] Print CHECKLIST.md

### Calibration (at desk or at field)
- [ ] **FOV calibration**: camera at 1m, measure visible width (~92cm)
  - If different: `FOCAL_LENGTH_MM = (5.02 × 1000) / visible_width_mm`
  - Update config.py
- [ ] **Lens undistort** (optional): `python tests/calibration/lens_calibrate.py`
- [ ] **Camera color check**: stream looks natural (blue sky, not red)
- [ ] **Detection test**: point at mannequin, confidence > 0.4
- [ ] **Inference speed**: `python tests/hardware/benchmark.py` (<250ms)

### Terminal Setup (3 PuTTY windows to Pi)

**Terminal 1: mavproxy**
```bash
sudo /opt/mavlink/mavlink-venv/bin/mavproxy.py \
  --master=/dev/ttyAMA0 --baudrate=921600 --streamrate=10 \
  --out=udpout:127.0.0.1:14550 \
  --out=udpout:127.0.0.1:14551 \
  --out=tcpin:0.0.0.0:5762
```

**Terminal 2: Robin's passive_watch (YOUR MAIN JOB)**
```bash
cd ~/dima/Group_Proj && source pienv/bin/activate
python passive_watch.py --compensate-tilt --conf 0.3 \
  --smart-estimate --smart-min 5 --smart-radius 2.0 \
  --smart-dir robin_detections --model best.tflite
```
Browser: `http://PI_IP:8090`

**Terminal 3: Our main.py (OPTIONAL, only if testing separately)**
```bash
python main.py --headless --compensate-tilt --center-verify --clean
```
⚠️ Camera conflict: stop passive_watch FIRST with Ctrl+C

### What Robin Gets
- GPS coordinates in `robin_detections/` folder
- JSON files with lat, lon, confidence, altitude
- His state machine reads from that directory
- See `docs/PASSIVE_WATCH_USAGE.md` for full details

### Post-Flight
- [ ] Copy logs: `scp pi@PI_IP:~/dima/Group_Proj/logs/* .`
- [ ] Copy detections: `scp -r pi@PI_IP:~/dima/Group_Proj/mission_detections/* .`
- [ ] Copy Robin's detections: `scp -r pi@PI_IP:~/dima/Group_Proj/robin_detections/* .`
- [ ] Screenshot ground station browser for report
- [ ] Git commit on Pi

## Key Files

| File | What |
|------|------|
| `CHECKLIST.md` | Print this for flight day |
| `docs/MAIN_FLAGS.md` | All 23 CLI flags |
| `docs/PASSIVE_WATCH_USAGE.md` | Robin's guide |
| `docs/GEOFENCE_EXPLAINED.md` | How geofence works |
| `TODO_NEXT_SESSION.md` | Tilt testing details (may be stale) |
