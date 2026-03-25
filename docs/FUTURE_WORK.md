# Future Work

## Automated Regression Testing

Currently all testing is manual (human launches sim, observes, confirms). This means every code change requires a human to re-test. Ideas for partial automation:

### What CAN be automated (unit/integration tests)
- **Compile checks**: `py_compile` all files after changes
- **Dry-run pattern**: `--dry-run` generates waypoints → verify count, bounds, spacing
- **NFZ speed formula**: feed (lat, lon, dist_to_NFZ) → verify speed output matches expected
- **State machine transitions**: mock GPS + detections → verify state sequence (SEARCH → VERIFY → SEARCH etc.)
- **Waypoint generation**: give polygon + altitude → check waypoints inside polygon, correct swath width
- **Config validation**: all config values within sane ranges
- **Geofence math**: feed coordinates near/inside NFZ → verify repulsion direction/magnitude

### What CANNOT be automated (needs human)
- Visual correctness: map rendering, drone movement smoothness, overlay accuracy
- Timing feel: speed cap responsiveness, repulsion smoothness
- Full integration: SITL + camera + CV detection + state machine together
- Real hardware: camera, GPS, RC, actual flight

### Approach: Record-and-Replay
One possible middle ground: record a successful simulation run (GPS trace, detections, key presses, state transitions) as a JSON log. Then replay it against new code and diff the state sequences. If states diverge, something broke. This doesn't test visuals but catches logic regressions.

### Approach: Headless SITL Scripting
Run SITL + main.py in headless mode with `--beacon-delay` and auto-confirm keys piped via `/cmd?key=` HTTP endpoint. Compare output log against expected patterns (waypoint count, state transitions, detection count). Could run in CI.

## Code Simplification (Post-Experimentation)

Current code has multiple experimental flags from development:
- 3 NFZ modes: `--nfz-repel`, `--nfz-slow`, `--nfz-carrot`
- 3 no-turn variants: `--no-turn`, `--no-turn-realign`, `--no-turn-realign-diag`
- Smooth path options: `--smooth-bezier`, `--smooth-extra`

**Winner settings** (bake as defaults, remove others):
- `--nfz-carrot` (scalar field + vector field repulsion)
- `--no-turn-realign-diag` (diagonal footprint, realign each pass)
- `--no-descend` (verify at search altitude)

On a clean branch: remove unused NFZ modes, remove unused path options, make the winning config the only config. Simpler code, fewer bugs, easier for teammates to read.

## Plug-in Path Planning

`planning.py` has a clean interface: polygon in → waypoints out. A colleague can add alternative patterns (spiral, sector, adaptive) by adding a method to `PathPlanner` that returns `[(lat, lon), ...]`. The rest of the system just flies the waypoints.

## Cube Firmware Geofence

For real flights, configure ArduCopter's built-in geofence in Mission Planner:
- `FENCE_ENABLE = 1`
- `FENCE_ACTION = LOITER` (or RTL)
- Upload SSSI polygon as fence
- This is firmware-level safety — our code is software-level (speed cap + repulsion)
- Two layers: our code prevents approach, Cube firmware is the hard stop
