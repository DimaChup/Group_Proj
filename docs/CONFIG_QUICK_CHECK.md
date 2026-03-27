# config.py Quick Check — Flight Day Checklist

**Print this page. Check every item before takeoff.**

---

## 5-Minute Config Audit

```bash
# 1. Verify file is readable
python -c "import config; print(f'MODE={config.MODE}'); print(f'CONNECTION={config.CONNECTION_STR}')"

# 2. Check critical values
python -c "
import config
critical = {
    'TARGET_ALT': config.TARGET_ALT,
    'VERIFY_ALT': config.VERIFY_ALT,
    'SEARCH_SPEED_MPS': config.SEARCH_SPEED_MPS,
    'CONFIDENCE_THRESHOLD': config.CONFIDENCE_THRESHOLD,
    'FOCAL_LENGTH_MM': config.FOCAL_LENGTH_MM,
    'NFZ_HARD_BOUNDARY_M': config.NFZ_HARD_BOUNDARY_M,
    'BAUD_RATE': config.BAUD_RATE,
}
for k,v in critical.items():
    print(f'{k}: {v}')
"
```

---

## Critical Values Checklist

✓ = Correct, ✗ = STOP, call lead

| Setting | Should Be | Check? | Issue? |
|---------|-----------|--------|--------|
| **TARGET_ALT** | 20–30 m (conservative) | ☐ | ☐ |
| **VERIFY_ALT** | 10–15 m | ☐ | ☐ |
| **SEARCH_SPEED_MPS** | 6–10 m/s | ☐ | ☐ |
| **CONFIDENCE_THRESHOLD** | 0.2–0.4 | ☐ | ☐ |
| **FOCAL_LENGTH_MM** | 5.46 (fixed) | ☐ | ☐ |
| **NFZ_HARD_BOUNDARY_M** | 3.0 m (do NOT change) | ☐ | ☐ |
| **BAUD_RATE** | 921600 (do NOT change) | ☐ | ☐ |
| **IMAGE_W, IMAGE_H** | 1456 × 1088 | ☐ | ☐ |
| **CAMERA_FLIP_180** | True | ☐ | ☐ |
| **MODE** | "REAL" or "SIMULATION" | ☐ | ☐ |
| **CONNECTION_STR** | Matches hardware (Pi/SITL) | ☐ | ☐ |

---

## What If...?

### CONFIG ERROR → What to do:

**VALUE IS WAY OFF (e.g., TARGET_ALT = 100m, or FOCAL_LENGTH_MM = 1.0)**
→ **STOP.** Do NOT fly. Find who last edited config.py. Revert to last known-good commit.
```bash
git log --oneline config.py | head -5
git checkout <good-commit> -- config.py
python field_tools/system_readiness.py  # re-verify
```

**VALUE IS WITHIN BOUNDS BUT FEELS WRONG (e.g., TARGET_ALT = 50m when site is small)**
→ Edit config.py directly. Recommended conservative values:
- TARGET_ALT: 20–25 m (start low, increase after first detection)
- SEARCH_SPEED_MPS: 6–8 m/s (tight frame spacing)
- CONFIDENCE_THRESHOLD: 0.3 (conservative model filtering)

**FOCAL_LENGTH_MM, BAUD_RATE, NFZ_HARD_BOUNDARY_M are WRONG**
→ **STOP.** These are hardware-calibrated constants. Do NOT fly. Contact project lead.

---

## Fields That Should NEVER Change Between Flights

These are hardware constants. If you touch them, you've broken something fundamental.

| Setting | Reason | If Changed → |
|---------|--------|-------------|
| **FOCAL_LENGTH_MM = 5.46** | Camera calibration (field-verified 2026-03-11) | GPS landing 5–10m off ✗ |
| **IMAGE_W = 1456, IMAGE_H = 1088** | Pi camera native resolution | Image stretching; AI sees distorted target ✗ |
| **BAUD_RATE = 921600** | Cube serial speed | Mavproxy fails to connect ✗ |
| **NFZ_HARD_BOUNDARY_M = 3.0** | Legal SAR requirement (UK regulations) | Potential legal violation ✗ |
| **CAMERA_FLIP_180 = True** | Hardware mounting (inverted on airframe) | Image upside-down ✗ |
| **SENSOR_WIDTH_MM = 5.02** | IMX296 spec sheet | FOV calculation wrong ✗ |

---

## Fields You CAN Tune Between Flights

These are operational tuning parameters. Safe to adjust based on field observations.

| Setting | Range | Change If | Don't Change If |
|---------|-------|-----------|-----------------|
| **TARGET_ALT** | 15–50 m | AI can't detect from current alt | Detection is working well |
| **VERIFY_ALT** | 8–20 m | Operator can't see landing zone | Landing zone clear at 15m |
| **SEARCH_SPEED_MPS** | 4–12 m/s | Missing targets / false positives | Frame spacing is working |
| **CONFIDENCE_THRESHOLD** | 0.1–0.6 | Too many FPs (↑) or misses (↓) | Model is balanced |
| **NFZ_WAYPOINT_BUFFER_M** | 20–50 m | Too close to NFZ or too far away | 30m is conservative default |

---

## Last Known-Good Commit

If config.py gets corrupted or someone makes a mistake, revert to:

```bash
git log --oneline -n 5 config.py
# Pick the most recent "Update config.py" commit before your changes
git checkout <commit-hash> -- config.py
```

Current main branch: **Working5.8** or **MainOne2**
Last reliable config.py: Check git log; usually last update is safe.

---

## Emergency Rollback (If Values Are Wrong)

```bash
# 1. Identify the problem (run system readiness)
python field_tools/system_readiness.py

# 2. If config is reported FAIL, find the last good version
git log --oneline config.py | head -10

# 3. Revert to a known-good commit
git checkout <commit-hash> -- config.py
git status  # verify config.py is reverted

# 4. Re-verify
python field_tools/system_readiness.py --quick

# 5. If still broken, contact project lead
```

---

**Printed**: _______________
**Checked By**: _______________
**All Items Passed**: ☐ YES ☐ NO (if NO, do not fly)
