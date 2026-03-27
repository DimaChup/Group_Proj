# config.py Failure Modes & Root Cause Diagnosis

**Use this when the drone doesn't do what you expect.**

---

## Top 10 "Why Didn't That Work?" Scenarios

### 1. 🔴 **Drone Takes Off But Immediately RTLs**
(Climbs for 3-5s, then returns to home)

**Likely causes** (check in order):
1. `BAUD_RATE` wrong (921600 assumed, but set to 115200)
   - → Cube heartbeat dropout → autopilot RTLs on GPS failure
   - **FIX**: `BAUD_RATE = 921600` only. Verify mavproxy started with `--baudrate=921600`

2. `CONNECTION_STR` doesn't match actual hardware
   - → Can't reach Cube → heartbeat timeout
   - **FIX**: Check Pi IP, verify mavproxy running, telemetry reaching port 14550

3. GPS lock not acquired
   - → Not a config.py issue, but check `TAKEOFF_GPS` loaded correctly from KML

---

### 2. 🔴 **AI Never Detects Dummy (or Detects False Positives Constantly)**

**Likely causes** (in priority order):

| Problem | Symptom | config.py Culprit | Solution |
|---------|---------|------------------|----------|
| Altitude too high | Dummy appears < 5 pixels in frame | TARGET_ALT = 50m (should be ≤ 30m) | Reduce TARGET_ALT → 25m |
| Speed too fast | 1 frame every 3m; dummy only in 1–2 frames | SEARCH_SPEED_MPS = 15 (should be ≤ 10) | Reduce speed → 8 m/s |
| Confidence threshold too high | Detections at 0.7+ confidence missed | CONFIDENCE_THRESHOLD = 0.5 (should be ≤ 0.4) | Lower threshold → 0.3 |
| Confidence threshold too low | 50+ false positives/minute | CONFIDENCE_THRESHOLD = 0.05 | Raise threshold → 0.2–0.3 |
| Image not being captured at native res | Blurry/stretched input to model | IMAGE_W, IMAGE_H not matching camera | Check Pi camera native res (usually 1456×1088) |
| Model path wrong or model corrupted | `best.tflite` not found or won't load | No direct config var; check file exists | `ls -la best.tflite` in project root |

**Diagnostic command**:
```bash
python -c "
import config
print(f'TARGET_ALT: {config.TARGET_ALT}')
print(f'SEARCH_SPEED_MPS: {config.SEARCH_SPEED_MPS}')
print(f'CONFIDENCE_THRESHOLD: {config.CONFIDENCE_THRESHOLD}')
print(f'IMAGE_W x IMAGE_H: {config.IMAGE_W} x {config.IMAGE_H}')
"
```

---

### 3. 🟠 **Drone Flies Lawnmower But GPS Landing Is 5–10m Off**

**Likely causes**:

1. **FOCAL_LENGTH_MM is wrong**
   - Symptom: Landing offset is consistent in same direction/distance
   - **Solution**: Re-calibrate with `tools/fov_calibrate_video.py`
   - Current: 5.46 (verified) — do NOT change without re-test

2. **TARGET_ALT different than when FOCAL_LENGTH_MM was calibrated**
   - Symptom: Landing offset depends on actual altitude (windy day = drift)
   - **Solution**: Use `calibration/alt_test.py` to check actual vs. config altitude
   - Pressure/temperature variations can cause ±2m error

3. **GPS receiver having lag**
   - Symptom: Landing is offset in direction of last travel direction
   - **Solution**: This is not a config.py problem (GPS timing lag is in hardware)
   - Workaround: Plan search area farther from actual target to account for drift

**Diagnostic**:
```bash
# Check focal length value
python -c "import config; print(f'FOCAL_LENGTH_MM = {config.FOCAL_LENGTH_MM}')"

# If wrong, check when it was last calibrated
git log --oneline -p config.py | grep -A5 -B5 FOCAL_LENGTH_MM | head -20
```

---

### 4. 🟠 **Drone Enters Geofence (SSSI) by Mistake**

**Likely causes**:

1. **NFZ_HARD_BOUNDARY_M too small**
   - Symptom: Drone enters MANUAL mode 2–3m from SSSI, which is inside legal limit
   - **Solution**: Keep at 3.0m minimum. If still hitting NFZ, increase to 5.0m (requires geofence redesign approval)

2. **NFZ_WAYPOINT_BUFFER_M too small**
   - Symptom: Lawnmower pattern planned waypoints within 10m of NFZ; some waypoints are skipped
   - **Solution**: Increase to 30–50m depending on survey area size
   - Current: 30m is conservative and recommended

3. **SSSI polygon not loaded** (KML file missing)
   - Symptom: No geofence active; drone can go anywhere
   - **Solution**: Verify `flight_plans/AENGM0074.kml` exists and loaded
   ```bash
   python -c "import config; config.load_kml_zones(); print(f'SSSI: {config.SSSI_GPS}')"
   ```

**Safety check**:
```bash
python -c "
import config
config.load_kml_zones()
print(f'NFZ Hard Boundary: {config.NFZ_HARD_BOUNDARY_M}m')
print(f'NFZ Waypoint Buffer: {config.NFZ_WAYPOINT_BUFFER_M}m')
print(f'SSSI loaded: {len(config.SSSI_GPS)} corners')
if len(config.SSSI_GPS) < 3:
    print('⚠️ WARNING: SSSI not loaded!')
"
```

---

### 5. 🟡 **Drone Hovers Too High During Verification (Can't See Landing Site)**

**Likely causes**:

1. **VERIFY_ALT set too high**
   - Symptom: From ground, drone looks like a dot; can't see where it will land
   - **Current**: 15m (should allow clear view of 50–100m radius landing zone)
   - **Solution**: Reduce to 10–12m if operator can't see landing details

2. **CAMERA_FLIP_180 is wrong**
   - Symptom: Operator panel shows inverted image; looks confusing
   - **Solution**: Toggle True ↔ False and re-test
   - Current: True (camera mounted inverted on airframe)

---

### 6. 🟡 **Search Takes Too Long (Battery Running Low Before Finding Dummy)**

**Likely causes**:

1. **TRANSIT_SPEED_MPS or SEARCH_SPEED_MPS too slow**
   - Symptom: Survey taking 10+ minutes for small area; battery dips below 30%
   - Current defaults: TRANSIT=15 m/s, SEARCH=10 m/s (reasonable)
   - **Solution**: Increase to SEARCH=12 m/s (requires re-tuning CONFIDENCE_THRESHOLD to prevent FPs)

2. **TARGET_ALT too low**
   - Symptom: Flying 15m altitude when 30m would cover more area faster
   - **Solution**: Check TARGET_ALT vs. actual search area size
   - If area is >200m×200m, increase ALT; if <100m×100m, can lower

---

### 7. 🟡 **Drone Flies Lawnmower But Misses Dummy (Appears to Fly Right Over It)**

**Likely causes**:

1. **SEARCH_SPEED_MPS too fast relative to frame rate**
   - Symptom: Dummy enters frame, exits frame, never triggers CENTERING
   - Spacing = speed / fps = 10 m/s / 4.8 fps = 2.08m
   - Dummy height = 1.8m → fits in ~1.2 frame widths; risky
   - **Solution**: Reduce SEARCH_SPEED_MPS to 6–8 m/s (spacing = 1.25–1.67m; safer)

2. **DETECT_CONFIRM_FRAMES too high**
   - Symptom: Single detection won't trigger CENTERING; requires 5+ consecutive frames
   - Current: 3 frames (reasonable)
   - **Solution**: Reduce to 2 frames if missing targets

3. **CONFIDENCE_THRESHOLD too high**
   - Symptom: Edge-case detections (partial view, shadows) filtered out
   - Current: 0.2 (permissive)
   - **Solution**: Already very low; increase retraining dataset size instead

---

### 8. 🟡 **Drone Doesn't Descend to Landing (Hovers at VERIFY_ALT Indefinitely)**

**Likely causes**:

1. **State machine stuck** (not a config.py issue, but check operator input)
   - Operator never presses Y to confirm landing
   - **Solution**: Ensure N/Y buttons wired correctly; test with preflight.py

2. **VERIFY_ALT so high operator can't assess landing safely**
   - Symptom: "I can't see if it's safe, so I'm not pressing Y"
   - **Solution**: Reduce VERIFY_ALT to 10–12m

---

### 9. 🔴 **Connection Dropped; Drone Lost Signal (Emergency RTL)**

**Likely causes**:

1. **BAUD_RATE mismatch**
   - Cube configured for 921600, but Python requests 115200 (or vice versa)
   - **FIX**: Verify Cube parameter CAN_BAUDRATE = 921600
   - **FIX**: Verify config.py has `BAUD_RATE = 921600`

2. **CONNECTION_STR doesn't reach Cube**
   - Pi connection: Should be `udpin:0.0.0.0:14550` (mavproxy bridge)
   - SITL connection: Should be `tcp:127.0.0.1:5762` or `tcp:<gateway>:5762` (WSL)
   - **FIX**: Run `python -c "import config; print(config.CONNECTION_STR)"`

3. **Mavproxy not running on Pi**
   - **FIX**: `sudo /opt/mavlink/mavlink-venv/bin/mavproxy.py --master=/dev/ttyAMA0 --baudrate=921600 --out=udpout:127.0.0.1:14550`

---

### 10. 🟡 **Image Upside Down / Colors Wrong**

**Likely causes**:

1. **CAMERA_FLIP_180 = False (but camera mounted inverted)**
   - Symptom: All imagery is upside-down; AI sees sky instead of ground
   - **FIX**: Set `CAMERA_FLIP_180 = True`

2. **CAMERA_AWB_MODE = "auto" (in overcast/variable lighting)**
   - Symptom: Image has blue tint; AI struggles with white balance shifts
   - **FIX**: Use `CAMERA_AWB_MODE = "daylight"` for outdoor flights

---

## Quick Diagnosis Flowchart

```
Drone not working as expected?

├─ DOESN'T CONNECT TO CUBE
│  └─ Check: BAUD_RATE = 921600, CONNECTION_STR matches hardware
│
├─ TAKES OFF THEN RTLs IMMEDIATELY
│  └─ Check: GPS lock, heartbeat, BAUD_RATE
│
├─ FLIES BUT AI DOESN'T DETECT
│  └─ Check: TARGET_ALT (too high?), SEARCH_SPEED_MPS (too fast?), CONFIDENCE_THRESHOLD (wrong value?)
│
├─ DETECTS DUMMY BUT GPS LANDING WRONG
│  └─ Check: FOCAL_LENGTH_MM (calibrated?), TARGET_ALT (matches calibration?)
│
├─ ENTERS GEOFENCE / SKIPS WAYPOINTS
│  └─ Check: NFZ_HARD_BOUNDARY_M, NFZ_WAYPOINT_BUFFER_M, SSSI polygon loaded
│
├─ IMAGE UPSIDE DOWN / BLUE TINT
│  └─ Check: CAMERA_FLIP_180, CAMERA_AWB_MODE
│
└─ SEARCH TAKES TOO LONG / RUNS OUT OF BATTERY
   └─ Check: SEARCH_SPEED_MPS, TARGET_ALT (covers enough area?), TRANSIT_SPEED_MPS
```

---

## Nuclear Option: Reset to Last Known-Good State

If config.py is corrupted beyond recognition:

```bash
# 1. Find the last commit before the problem started
git log --oneline config.py | head -10

# 2. Identify which is "good"
# (Usually the most recent one; if not, ask project lead)

# 3. Revert to that commit
git checkout <good-commit-hash> -- config.py

# 4. Verify
python field_tools/system_readiness.py --quick

# 5. Re-run mission
python main.py
```

---

## When to Contact Project Lead

✋ **STOP and call for help if:**

1. **BAUD_RATE, FOCAL_LENGTH_MM, or NFZ_HARD_BOUNDARY_M are wrong**
   - These are hardware-calibrated constants

2. **SSSI polygon won't load** (geofence missing)
   - Safety-critical; cannot proceed without verification

3. **Drone RTLs within 30 seconds of takeoff** (repeatable)
   - Something fundamentally broken

4. **GPS landing is >10m off after FOCAL_LENGTH_MM verified**
   - Possible new hardware issue (camera shift, etc.)

5. **Unsure whether to adjust a value**
   - Ask first; easier than fixing broken mission mid-flight

---

**Last Updated**: 2026-03-27
**For questions**: See CONFIG_SAFETY_ANALYSIS.md (full reference)
