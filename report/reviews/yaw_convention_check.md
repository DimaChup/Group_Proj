# Yaw Convention Check

**Date**: 2026-03-29
**Question**: Is `self.yaw` in degrees or radians across SIMULATION and REAL modes?
**Related bug**: Pressing East in NFZ buffer zone moved drone West.

---

## 1. Where self.yaw Is Set

| File | Line | Source | Units |
|------|------|--------|-------|
| `main.py` | 249 | Init: `self.yaw = 0` | n/a (zero) |
| `main.py` | 364 | `self.yaw = msg.yaw` from MAVLink `ATTITUDE` | **radians** |
| `pi_flight.py` | 409 | Init: `self.yaw = 0.0` with comment `# radians` | n/a (zero) |
| `pi_flight.py` | 535 | `self.yaw = msg.yaw` from MAVLink `ATTITUDE` | **radians** |
| `simple_simulator.py` | 161 | Init: `self.yaw = 0.0` | n/a (zero) |
| `simple_simulator.py` | 334 | `self.yaw = msg.yaw` from MAVLink `ATTITUDE` | **radians** |

**Conclusion**: `self.yaw` is **always radians** in every script, in both SIMULATION and REAL modes. The MAVLink ATTITUDE message sends `yaw` in radians per the MAVLink spec. SITL sends the same ATTITUDE message format, so SIMULATION and REAL are identical.

---

## 2. The Bug: Double Conversion in state_machine.py

**Commit**: `06b42d4` — "Fix manual NFZ sign bug: yaw already in radians, don't double-convert"

The bug was in `state_machine.py`, `_handle_manual_flight()` (line ~882):

```python
# BEFORE (broken):
yaw = math.radians(getattr(self, 'yaw', 0))

# AFTER (fixed):
yaw = getattr(self, 'yaw', 0)  # already in radians from MAVLink ATTITUDE
```

**What happened**: `self.yaw` was already in radians (e.g., 2.7 rad = ~155 deg). Wrapping it in `math.radians()` treated it as if it were degrees, producing `math.radians(2.7) = 0.047 rad = ~2.7 deg`. This near-zero rotation meant body-frame directions were barely rotated, so commands mapped to roughly cardinal NED directions regardless of actual heading. When the drone was facing roughly south (~180 deg = pi rad), the double conversion produced ~3.14 deg, making East appear as West.

**The fix is correct.** Removing `math.radians()` passes the raw radians value through, which `math.cos()` and `math.sin()` expect.

---

## 3. Audit of All Yaw Usage (is there still a problem?)

### Correct usage (radians throughout):

| Location | Code | Correct? |
|----------|------|----------|
| `state_machine.py:882` | `yaw = getattr(self, 'yaw', 0)` then `cos(yaw)`, `sin(yaw)` | YES (fixed) |
| `state_machine.py:345` | `math.degrees(self.yaw)` to compare with degree target | YES |
| `navigation.py:69-73` | `cos(current_yaw)`, `sin(current_yaw)` where `current_yaw` comes from `self.yaw` via `_get_yaw` | YES |
| `main.py:426` | `self.yaw` passed to `calculate_target_from_pixels()` which expects radians | YES |
| `gps_utils.py:106-107` | `cos(drone_yaw)`, `sin(drone_yaw)` — documented as "radians" at line 76 | YES |
| `pi_flight.py:641-642` | `cos(self.yaw)`, `sin(self.yaw)` | YES |
| `pi_flight.py:711-712` | `cos(self.yaw)`, `sin(self.yaw)` | YES |
| `pi_flight.py:958` | `math.degrees(self.yaw)` for JSON status to browser | YES |
| `pi_flight.py:262` (JS) | `S.yaw * Math.PI / 180` — receives degrees from JSON, converts back | YES |
| `simple_simulator.py:505,548` | `math.degrees(self.yaw)` for logging | YES |
| `simple_simulator.py:687-688` | `cos(self.yaw)`, `sin(self.yaw)` | YES |
| `simple_simulator.py:839,866` | `cos(-self.yaw)`, `sin(-self.yaw)` for camera view rotation | YES |
| `simulation.py:299` | `math.degrees(yaw)` for `cv2.getRotationMatrix2D` (expects degrees) | YES |
| `capture_training.py:125` | `math.degrees(msg.yaw) % 360` for metadata | YES |
| `passive_watch.py:362` | `msg.yaw * 57.2958` (rad to deg) then `math.radians()` at line 275 | YES (redundant but correct) |

### Repulsion code (main.py:800):

```python
self.nav.send_velocity(push_n/mag*s, push_e/mag*s, 0, current_yaw=0.0)
```

This passes `current_yaw=0.0` intentionally because `push_n` and `push_e` are **already in NED frame** (computed from GPS offsets). Setting `current_yaw=0.0` means `send_velocity()` applies cos(0)=1, sin(0)=0 — no rotation — which is correct for pre-rotated NED velocities.

### NFZ viscous field (state_machine.py:893):

```python
self.nav.send_velocity(vn, ve, vd, current_yaw=0)
```

Same pattern: `vn` and `ve` are already NED (body-frame was rotated at lines 883-884 using the correct `self.yaw`). Passing `current_yaw=0` avoids double rotation. Correct.

---

## 4. Remaining Risk: None

The fix at commit `06b42d4` was the only place where yaw was double-converted. All other usages are consistent:

- `self.yaw` is **always radians** (from MAVLink ATTITUDE)
- When degrees are needed for display/logging, `math.degrees()` is applied
- When NED velocity is pre-computed, `current_yaw=0` is passed to `send_velocity()` to skip rotation
- `gps_utils.py` documents the parameter as radians and receives radians

**No remaining yaw convention bugs found.**

---

## 5. Summary

| Question | Answer |
|----------|--------|
| Is `self.yaw` degrees or radians? | **Radians** — always, in all modes |
| Same in SIMULATION and REAL? | **Yes** — both receive MAVLink ATTITUDE (radians) |
| Did the fix resolve the East-moves-West bug? | **Yes** — removed erroneous `math.radians()` wrapper |
| Any remaining yaw bugs? | **No** — all 15+ usage sites audited, all correct |
