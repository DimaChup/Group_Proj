# main.py Blueprint (687 lines) — Mission Orchestrator

> This is a MAP, not a copy of code. Use it to navigate main.py without reading 687 lines.
> Update this file whenever main.py changes structurally.

## Section Map

| Section | Lines | Purpose |
|---------|-------|---------|
| Imports + config check | 1-27 | Standard lib + project modules |
| CLI flags & config | 29-57 | `--model`, `--dry-run`, `--transit`, `--speed`, `--alt`, `--beacon-delay`, `--no-nfz`, etc. |
| HEADLESS detection | 59-67 | Auto-detect display availability |
| `_terminal_input_thread` | 69-82 | Terminal key input (PuTTY/SSH), feeds `stream_cmd_queue` |
| `_draw_servo_animation` | 85-138 | Payload drop animation (bottom-right corner during HOVER_TARGET) |
| `__init__` | 143-254 | SimulationEnvironment or real setup, VisionSystem, geofence, planner, telemetry vars, CSV logger |
| `_load_waypoints_json` | 256-262 | Static: load JSON waypoints (supports dict and list formats) |
| `_load_transit_from_file` | 264-273 | Load transit waypoints from JSON for simulation preload |
| `_setup_real_search_area` | 275-291 | Load from `search_area.json` -> config GPS -> fallback |
| `update_telemetry` | 293-319 | Parse GLOBAL_POSITION_INT, ATTITUDE, HEARTBEAT; RC failsafe detection |
| `calculate_target_gps` | 321-327 | Pixel (u,v) -> GPS via gps_utils wrapper |
| `calculate_landing_spot` | 329-332 | 7.5m offset via gps_utils wrapper |
| `update_dashboard` | 334-428 | Frame capture, CV detection, HUD overlay, servo animation, composite view |
| `run()` | 430-508 | Main loop: telemetry -> dashboard -> keys -> state dispatch -> geofence -> done |
| `_enforce_geofence` | 510-541 | NFZ hard boundary -> MANUAL, speed cap ramp, inner polygon repulsion |
| `on_dashboard_mouse` | 543-546 | Zoom via mousewheel (simulation only) |
| `_dry_run` | 549-630 | No-fly visualization: pattern stats, state walkthrough, map display |
| `__main__` | 633-687 | Entry point: DRY_RUN or mission.run() with error handling |

## State Machine Flow

```
INIT -> CONNECTING -> ARMING -> TAKEOFF -> PRE_WAYPOINTS -> TRANSIT_TO_SEARCH -> SEARCH
                                                                                   |
                                                         detect target             v
                                                                             CENTERING
                                                                                   |
                                                                                   v
                                                                             DESCENDING
                                                                                   |
                                                                                   v
                                                                               VERIFY
                                                                              /      \
                                                                           Y           N
                                                                          /             \
                                                               select side          RETURN_TO_SEARCH
                                                              (N/E/W/S)
                                                                   |
                                                                   v
                                                    APPROACH -> HOVER_TARGET -> RETURN_TRANSIT -> RETURN_HOME -> LANDING -> DONE

Any state: M -> MANUAL -> M -> RETURN_FROM_MANUAL -> resume
```

## Key Instance Variables

| Variable | Type | Purpose |
|----------|------|---------|
| `self.master` | `mavutil.mavlink_connection` | pymavlink connection to Cube |
| `self.eyes` | `VisionSystem` | Camera + AI detection (dual backend) |
| `self.planner` | `PathPlanner` | Lawnmower search pattern generator |
| `self.geo` | `GeoTransformer` | GPS <-> pixel coordinate conversion |
| `self.nav` | `NavigationController` | Velocity/position commands to Cube |
| `self.geofence` | `NFZGeofence` or None | SSSI no-fly zone enforcement |
| `self.waypoints` | `list[(lat, lon)]` | Generated lawnmower waypoints |
| `self.pre_waypoints` | `list[(lat, lon)]` | Transit waypoints (before search) |
| `self.target_lat/lon` | `float` | Detected target GPS position |
| `self.landing_lat/lon` | `float` | 7.5m offset landing spot |
| `self.state` | `State` enum | Current state machine state |

## Dependencies

```
main.py
  |-- config.py        All settings
  |-- states.py        State enum
  |-- utils.py         GeoTransformer
  |-- vision.py        VisionSystem
  |-- planning.py      PathPlanner
  |-- state_machine.py StateHandlersMixin (all state handlers)
  |-- navigation.py    NavigationController
  |-- stream_server.py HTTP stream + cmd queue
  |-- gps_utils.py     GPS math (target from pixels, landing offset)
  |-- geofence.py      NFZGeofence (optional)
  |-- simulator/       SimulationEnvironment (SIM mode only)
```

## Modification Guide

| To change... | Edit... |
|--------------|---------|
| Add a new state | `states.py` + `state_machine.py` + dispatch table in `run()` |
| Change detection logic | `vision.py` only |
| Change search pattern | `planning.py` only |
| Change altitudes/speeds | `config.py` only |
| Change HUD layout | `update_dashboard()` (~line 334) |
| Change landing offset | `gps_utils.py` |
| Add new CLI flag | CLI block (~line 29) |
| Change geofence behavior | `_enforce_geofence()` (~line 510) or `geofence.py` |
