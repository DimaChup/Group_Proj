# Error Handling Audit — main.py & state_machine.py
**Date**: 2026-03-27
**Assessment**: 8 error scenarios analyzed for graceful degradation vs crashes

---

## Summary
- **Critical Issues**: 3 (will crash or silently fail)
- **High Issues**: 2 (degraded but won't crash)
- **Handled**: 3 (graceful recovery or timeouts)

---

## 1. Camera Returns None Frames for 30+ Seconds

**Status**: ✅ **GRACEFUL** (degraded, not crash)

**Code Path**:
```python
main.py:413-415:
    frame = self.eyes.get_frame()
    if frame is None:
        frame = np.zeros((config.IMAGE_H, config.IMAGE_W, 3), dtype=np.uint8)
```

**What Happens**:
- If `get_frame()` returns `None` for 30+ seconds, main.py **creates a black frame** (zeros array)
- HUD still draws (crosshair, state info, target location) on blank frame
- Detection returns `False, 0, 0, 0.0` (vision.py:229 guards against None)
- **Result**: Mission continues with no detections, operator can still fly manually with M key

**⚠️ Potential Issue**: Operator won't know camera is offline—HUD still displays. Add warning banner.

**Recommendation**: Add elapsed-time check in `update_dashboard()`:
```python
if time.time() - self.last_valid_frame > 10:
    cv2.putText(frame, "⚠ CAMERA OFFLINE", (cx-100, 20), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)
```

---

## 2. MAVLink Connection Drops

**Status**: ⚠️ **PARTIALLY HANDLED** (stays alive, but dangerous)

**Code Path**:
- **Initial connect** (state_machine.py:152-173): 15-second warning loop, never exits CONNECTING
- **Mid-flight**: No heartbeat monitoring after CONNECTING state
- **Recovery**: None—once lost, no reconnection attempt

**What Happens**:

### During CONNECTING (Before Arming)
```python
state_machine.py:157-161:
    if self.connect_start_time > 0 and self.last_heartbeat == 0:
        elapsed = time.time() - self.connect_start_time
        if elapsed > 15 and int(elapsed) % 15 == 0:
            print(f"ERROR: No heartbeat from Cube in {int(elapsed)}s...")
```
- **Prints warning every 15 seconds**, never times out
- **Never arms**—stuck in CONNECTING state
- **Operator must manually kill with Ctrl+C**

### After Arming (Mid-Flight)
- **NO monitoring of heartbeat loss** after leaving CONNECTING
- If Cube drops (radio loss, power, serial), mission continues with stale telemetry
- `update_telemetry()` (main.py:331-370) pulls messages but doesn't check if they stop arriving
- **Last known position replayed forever**—drone may be crashing but code thinks it's on course

**Result**: **DANGEROUS — Drone can crash undetected**

**Recommendations**:
1. **Add heartbeat timeout in main loop**:
```python
main.py:664+ in run():
    if time.time() - self.last_heartbeat > 5.0 and self.state not in (State.INIT, State.CONNECTING):
        print("[CRITICAL] Heartbeat lost! Initiating RTL...")
        self.nav.send_global_target(self.home_lat, self.home_lon, config.TARGET_ALT)
        self.state = State.RETURN_HOME
```
2. **Set explicit timeout in CONNECTING**:
```python
if arming_elapsed > 30:  # Give 30s to get heartbeat
    print("[FATAL] No heartbeat after 30s. Aborting.")
    sys.exit(1)
```

---

## 3. Model File is Missing

**Status**: ⚠️ **FAILS GRACEFULLY** (with warning)

**Code Path**:
```python
vision.py:191-219:
    try:
        model = YOLO(model_path)  # Ultralytics
        self.using_ai = True
    except Exception as e:
        print(f"[VISION] Model Load Failed: {e}")
```

**What Happens**:
- `best.tflite` missing → TFLite load fails (vision.py:216-217)
- Sets `self.using_ai = False`, `self.model = None`
- **Returns False for all detections** (vision.py:229-230)
- **Mission continues without AI**
  - Flies search pattern autonomously
  - Never detects anything
  - Operator can manually verify and land with keyboard Y/N

**Result**: ✅ **Graceful degradation** — no crash, but mission fails silently

**⚠️ Potential Issue**: Operator won't know AI failed until well into search. Add preflight check.

**Recommendation**: Use existing `preflight.py` tool:
```bash
python preflight.py  # Check camera + AI + Cube before flight
```

---

## 4. KML File is Missing

**Status**: ✅ **HANDLED GRACEFULLY** (fallback to hardcoded)

**Code Path**:
```python
config.py:139-146:
    def load_kml_zones(kml_path="flight_plans/AENGM0074.kml"):
        if not os.path.exists(kml_path):
            print(f"[CONFIG] KML not found: {kml_path} — using fallback SEARCH_AREA_GPS")
            return False
```

**What Happens**:
- `load_kml_zones()` prints warning, returns False
- Hardcoded fallback zones in config.py:123-133 remain active
- Mission uses `SEARCH_AREA_GPS = [(51.423406, -2.671446), ...]` (hardcoded)
- **Result**: ✅ Mission flies default search area

**⚠️ Minor Issue**: Fallback area is hardcoded to specific university location. Only works for that site.

**Recommendation**: Document fallback coordinates in CLAUDE.md (already done) and ensure KML is in git.

---

## 5. flight_plans/ Directory is Missing

**Status**: ⚠️ **HANDLED PARTIALLY** (creates on first write, but may crash if read-only filesystem)

**Code Path**:
```python
main.py:154-161:
    os.makedirs("flight_plans", exist_ok=True)  # Create if missing
    with open("flight_plans/focus_area.json", "w") as f:
        json.dump(focus_area, f)
```

**What Happens**:
- **On first write**: `os.makedirs("flight_plans", exist_ok=True)` creates it
- **If filesystem is read-only** (e.g., Pi with `/` read-only): **CRASH**
  ```
  PermissionError: [Errno 13] Permission denied: 'flight_plans/focus_area.json'
  ```
- **If directory exists**: No issue
- **Transit loading** (main.py:275-281): Checks `os.path.exists()` first, gracefully skips if missing

**Result**: ⚠️ **Crash possible on read-only FS, OK on writable**

**Recommendation**:
```python
# Wrap all mkdir calls in try-except
try:
    os.makedirs("flight_plans", exist_ok=True)
except PermissionError:
    print("[WARNING] Cannot write to flight_plans/ — read-only filesystem?")
    # Continue anyway (focus area won't be saved, but mission runs)
```

---

## 6. GPS Fix is Lost Mid-Flight

**Status**: ⚠️ **NOT MONITORED** (dangerous)

**Code Path**:
```python
state_machine.py:184-204:
    # GPS fix check only happens in ARMING state, never again
    if not self.gps_fix_ok:
        if fix_type >= 3 and sats >= 6:
            self.gps_fix_ok = True  # Set once, never checked again
```

**What Happens**:
- **In ARMING**: Waits for `fix_type >= 3` (3D fix) and 6+ satellites
- **After arming**: GPS status **never checked again**
- If GPS locks are lost (tunnel, rain, RFI), drone:
  - Still sends position targets to Cube (Cube falls back to internal EKF)
  - Code thinks it has GPS but actually uses dead reckoning
  - Position estimates drift by 1-3m/minute
  - Target centering becomes increasingly inaccurate

**Current Code**:
```python
# update_telemetry (line 331+) receives GPS_RAW_INT but never validates fix_type
```

**Result**: ⚠️ **Silent failure** — mission degrades gracefully but operator unaware

**Recommendation**:
```python
# Add to update_telemetry() or main loop:
if gps_msg.fix_type < 3:
    if time.time() - self._last_gps_warning > 10:
        print(f"[WARNING] GPS fix degraded: fix_type={gps_msg.fix_type} (need 3+)")
        self._last_gps_warning = time.time()
    if self.state == State.VERIFY:
        print("[ALERT] GPS unstable during VERIFY — recommend manual landing")
```

---

## 7. Operator Never Presses Y/N/I During VERIFY

**Status**: ✅ **HANDLED WITH TIMEOUT**

**Code Path**:
```python
state_machine.py:586-594:
    def _handle_verify(self, target_found, px_u, px_v, key):
        self.waiting_for_confirmation = True
        if time.time() - self.state_start_time > 120:
            print("WARNING: VERIFY timeout (120s). No operator response — rejecting target.")
            self.rejected_targets.append((self.target_lat, self.target_lon))
            self.waiting_for_confirmation = False
            self._set_state(State.SEARCH)
```

**What Happens**:
- Drone hovers at target for **120 seconds max**
- If no key pressed (Y/N/I):
  - Target added to `rejected_targets` list
  - Returns to SEARCH state
  - Continues pattern autonomously
- **Result**: ✅ Auto-recovery, no crash

**⚠️ Potential Issue**: 120s is a long time to hover. If battery critical, drone may land before timeout.

**Recommendation**: Make timeout shorter and adjustable:
```python
VERIFY_TIMEOUT_S = 60  # config.py
# Or reduce to 30s for field testing
```

---

## 8. Battery Runs Low

**Status**: ❌ **NOT MONITORED AT ALL**

**Code Path**:
```
# NO battery monitoring in main.py or state_machine.py
# Cube has built-in failsafe (auto-RTL at ~3.5V)
# But no app-level checks
```

**What Happens**:
- **No battery telemetry parsing** (main.py:331-370 doesn't read SYS_STATUS)
- Mission continues until Cube's firmware RTL kicks in
- **Operator has no warning** that battery is low
- If in VERIFY state when battery dies:
  - Drone lands unexpectedly
  - Payload not released (servo commands queued but not executed)

**Result**: ❌ **DANGEROUS — Silent failure with real consequences**

**Recommendation**:
```python
# Parse SYS_STATUS message (available via mavlink)
sys_status_msg = master.recv_match(type='SYS_STATUS', blocking=False)
if sys_status_msg:
    voltage = sys_status_msg.voltage_battery / 1000.0  # mV → V
    current = sys_status_msg.current_battery / 100.0   # cA → A

    if voltage < 10.0:  # 3S LiPo critical
        print(f"[CRITICAL] Battery low: {voltage:.1f}V — initiating RTL")
        self.state = State.RETURN_HOME
    elif voltage < 11.0:
        if time.time() - self._last_batt_warning > 5:
            print(f"[WARNING] Battery: {voltage:.1f}V")
            self._last_batt_warning = time.time()
```

---

## Summary Table

| Scenario | Status | Crash Risk | Recovery | Recommendation |
|----------|--------|-----------|----------|-----------------|
| **1. Camera offline 30+s** | ✅ Graceful | No | Black frame, mission continues | Add visual warning banner |
| **2. MAVLink drops** | ⚠️ Partial | **CRITICAL** | None after arming | Add heartbeat timeout monitoring |
| **3. Model missing** | ✅ Graceful | No | No detections, manual verify | Use `preflight.py` before flight |
| **4. KML missing** | ✅ Graceful | No | Fallback to hardcoded zone | N/A (handled) |
| **5. flight_plans/ missing** | ⚠️ Partial | Yes* | Creates if writable | Wrap mkdir in try-except |
| **6. GPS fix lost mid-flight** | ❌ Not monitored | Low | Dead reckoning, drifts | Add GPS status checking loop |
| **7. Operator timeout** | ✅ Handled | No | Resume search after 120s | Reduce timeout to 30s |
| **8. Battery low** | ❌ Not monitored | **CRITICAL** | Cube firmware RTL | Parse SYS_STATUS + alert |

**Risk Level**: 🔴 **3 CRITICAL** (MAVLink drop, battery, read-only FS)

---

## Pre-Flight Checklist Additions

Before every flight, add these checks:

```bash
# 1. Verify files exist
ls -l best.tflite flight_plans/AENGM0074.kml flight_plans/

# 2. Run preflight checks
python preflight.py

# 3. Test heartbeat with 30-second connection loss simulation
# (manually unplug Cube USB briefly, verify recovery message)

# 4. Check battery voltage
# (use preflight.py or Mission Planner SYS_STATUS)

# 5. Verify flight_plans is writable
touch flight_plans/.write_test && rm flight_plans/.write_test
```

---

## Code Review Priority

**MUST FIX before flight**:
1. ✅ Add MAVLink heartbeat timeout monitoring (lines 662-737 main.py run loop)
2. ✅ Add battery voltage parsing (update_telemetry)
3. ✅ Add GPS fix status checking (every state, not just ARMING)

**NICE TO HAVE**:
- Camera offline warning banner
- Shorter VERIFY timeout (30s instead of 120s)
- Permission error handling for flight_plans/

