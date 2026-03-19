# MAVLink Command Mapping — SITL vs Real Cube

Every MAVLink command our code sends, where it's used, and verification status.

---

## All Commands We Send

| # | Command | Where used | SITL tested | Real tested |
|---|---|---|---|---|
| 1 | `MAV_CMD_DO_SET_MODE` (GUIDED=4) | state_machine.py:174 | YES | NO |
| 2 | `MAV_CMD_DO_SET_MODE` (RTL=6) | state_machine.py:322, navigation.py | YES | NO |
| 3 | `MAV_CMD_DO_SET_MODE` (LAND=9) | navigation.py | YES | NO |
| 4 | `MAV_CMD_DO_SET_MODE` (STABILIZE=0) | navigation.py | YES | NO |
| 5 | `MAV_CMD_COMPONENT_ARM_DISARM` (arm) | state_machine.py:188 | YES | BLOCKED (GPS2) |
| 6 | `MAV_CMD_COMPONENT_ARM_DISARM` (disarm) | state_machine.py:501 | YES | NO |
| 7 | `MAV_CMD_NAV_TAKEOFF` | state_machine.py:168 | YES | NO |
| 8 | `MAV_CMD_NAV_LAND` | state_machine.py:515 | YES | NO |
| 9 | `MAV_CMD_DO_CHANGE_SPEED` | navigation.py:135 | YES | NO |
| 10 | `MAV_CMD_DO_SET_SERVO` (ch9, 1100) | state_machine.py:457 | YES (ignored) | **NOT TESTED** |
| 11 | `SET_POSITION_TARGET_GLOBAL_INT` | navigation.py:75 | YES | NO |
| 12 | `SET_POSITION_TARGET_LOCAL_NED` | navigation.py:110 | YES | NO |
| 13 | `REQUEST_DATA_STREAM` | state_machine.py:126 | YES | YES (via mavproxy) |
| 14 | `SIM_SPEEDUP` param set | state_machine.py:131 | YES | N/A (real only) |

---

## Telemetry We Read

| Message | What we extract | Used in | Real tested |
|---|---|---|---|
| `GLOBAL_POSITION_INT` | lat, lon, alt, relative_alt, yaw | update_telemetry() | YES (mavproxy) |
| `ATTITUDE` | roll, pitch, yaw | update_telemetry() | YES (mavproxy) |
| `HEARTBEAT` | mode, armed state | update_telemetry() | YES (diagnostics) |
| `GPS_RAW_INT` | fix_type, satellites, hdop | arming check | YES (diagnostics) |
| `SYS_STATUS` | battery voltage, remaining | system_readiness | YES |
| `COMMAND_ACK` | command result | arm/mode checks | YES |

---

## SITL Verification Plan (run today on laptop)

### Test 1: Full mission dry run
```bash
DRONE_MODE=SIMULATION python main.py --search-area --dry-run
```
Verifies: pattern generation, state machine flow, no crashes.
**Status: PASSED**

### Test 2: Full mission with SITL
```bash
DRONE_MODE=SIMULATION python main.py --search-area --transit flight_plans/transit.json --speed 5
```
Verifies: arm, takeoff, waypoint nav, detection, centering, descent, verify, land, return home.
**Status: PASSED** (multiple times, mission complete)

### Test 3: Two waypoints only
```bash
DRONE_MODE=SIMULATION python tests/flight/2_waypoints.py
```
Verifies: arm, takeoff, GUIDED waypoint following, land.
Run in SITL and visually confirm on Mission Planner map.

### Test 4: Servo command
```bash
DRONE_MODE=SIMULATION python tests/flight/0a_cube_commands.py
```
Verifies: mode changes, arm command, buzzer. SITL ignores servo but confirms command path.

### Test 5: RTL trigger
In SITL mission, press M for manual override then observe RTL behaviour.

---

## Real Drone Verification Plan (when drone available)

### Bench tests (no props, indoor):
1. `param set GPS_TYPE2 0` then `reboot` — fix GPS2 blocker
2. `0a_cube_commands.py` — mode changes, arm attempt
3. Check servo in Mission Planner → Servo/Relay tab
4. Send servo command, listen for click
5. `0b_bench_mission.py` — full state machine, no flight

### First flight (props on, outdoor):
6. Manual RC takeoff, passive_watch.py running — confirm detection from altitude
7. `2_waypoints.py` — two simple waypoints and back
8. Confirm in Mission Planner: did it fly the waypoints correctly?

### Full mission:
9. `main.py --search-area --no-descend` — search, detect at altitude, verify Y/N
10. If Y works: `main.py --search-area` — full descent + landing

---

## Servo Release — What to Check on Real Drone

```
Current code sends:
  Channel: 9
  PWM: 1100 (release/open)

Need to confirm:
  1. Which SERVO output is the release mechanism?
     → In mavproxy: param show SERVO9_FUNCTION
     → If 0 (disabled) — wrong channel, find the right one

  2. What PWM values?
     → param show SERVO9_MIN  (fully closed?)
     → param show SERVO9_MAX  (fully open?)
     → param show SERVO9_TRIM (neutral?)

  3. Two-level release:
     → Level 1: partial open (e.g., PWM 1300?)
     → Level 2: full open (e.g., PWM 1100?)
     → Or: separate channels for each level?

  4. Test on bench:
     → Power Cube, connect mavproxy
     → In mavproxy terminal: servo set 9 1100
     → Does the mechanism click/release?
     → Try different PWM values to find the range
```

---

## Confidence Level Per Feature

| Feature | SITL confidence | Real confidence | Gap |
|---|---|---|---|
| State machine logic | 95% | 95% (same code) | None |
| Waypoint navigation | 90% | 70% (GPS drift) | Test needed |
| Detection from altitude | 85% | 50% (real conditions) | Flight test needed |
| GPS estimation accuracy | 80% | 50% (real GPS noise) | Flight test needed |
| Servo release | 10% | 0% | Channel/PWM unknown |
| Centering on target | 85% | 60% (wind, GPS) | Flight test needed |
| Landing accuracy | 80% | 60% (wind, GPS) | Flight test needed |
| RC kill switch | N/A | 90% (tested day 1) | Confirm |
| Stream to browser | 95% | 95% (tested day 2) | Confirmed |
| Headless operation | 90% | 90% (tested day 2) | Confirmed |
