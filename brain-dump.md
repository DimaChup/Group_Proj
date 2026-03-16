# Brain Dump — SAR Drone Project
> Append-only. Never delete entries. Ideas captured from every session.

---

## 2026-03-11 — Bootstrap workflow setup + flight day prep

- Split interactive drawing from flight scripts: draw on laptop → JSON → Pi loads headlessly
- draw_waypoints.py → waypoints.json → 2_waypoints.py (load, don't draw)
- draw_search_area.py → search_area.json → main.py/pi_flight.py (load, don't draw)
- Live map viewer (live_map.py): see drone on map.jpg in real-time, coverage overlay, zoom
- Y/N input over PuTTY: added terminal keyboard + browser buttons to main.py
- Want to use main.py on Pi tomorrow (not pi_flight.py) — added headless support
- Make video feed larger in browser + improve quality (70% → 85% JPEG)
- Apply BOOTSTRAP.md workflows: blueprints, brain-dump, NICE_TO_HAVE, slash commands
- Thorough review of all code and docs before flight day
- Multiple targets + pilot classification (Y/I/F) — plan exists but deferred

## 2026-03-11 (part 2) — Comprehensive review + documentation overhaul

- Need proper test guide: which scripts are essential, order, dependencies, what's redundant
- Compare our SAR workflow with industry/academic — are we doing it right?
- Document everything for report writing later (rationale, design decisions, performance)
- Make sure git/backup is solid, .gitignore covers secrets, rollback possible
- Clear env documentation: what venv is for what, Pi vs laptop differences
- Auto-update blueprints rule: blueprints go stale fast, need enforcement
- Session log in CLAUDE.md too long (1200 lines) — archive old sessions
- New sessions should catch up easily without user repeating themselves
- ai-edge-litert was MISSING from requirements_pi.txt — critical fix for Pi Python 3.13
- Path-scoped rules (.claude/rules/) for auto-loading context by file type
- Missing safety analysis doc for academic report (FMEA, risk matrix)
- Missing consolidated performance metrics (scattered across session logs)
- Need formal lessons learned doc (BGR fix, pyserial 3.13, mavproxy heartbeats)

## 2026-03-16 — Simulation testing, code review, state machine diagram

- Simulation seems to work well — ran mission in Mission Planner
- Mission Planner Servo/Relay tab — how does it work? Will servo release work in REAL mode?
- Need to configure SERVO9 in Mission Planner (SERVO9_FUNCTION, MIN/MAX) and wire to AUX OUT 1
- Code only opens servo (PWM 1100), never closes — need close command?
- Requested thorough 8-agent code review: main.py, simple_simulator, pi_flight, vision, config, utils, passive_watch, capture_training, preflight, all tests, all docs
- State machine diagram on dashboard was too linear — should show all loops, branches, edges properly
- Someone should be able to recreate our main.py logic exactly from the state machine diagram
- Dashboard config values were stale (TARGET_ALT=30 should be 50, speeds wrong)
- Need master blueprint document so future LLMs don't re-scan everything from scratch
- Always append to brain-dump every message — this is a rule, don't skip it
- Fix all 15 test scripts with wrong sys.path after reorganization
- Use proper MAV_CMD_NAV_LAND instead of altitude-0 position target for landing
- Run tests to verify they work (no crashes, expected outputs)
- Old branches have backup of everything — safe to fix on current branch
- Do a critical review of everything: is code ready to run? Does the dashboard capture things well?
- Review project organization: clear next steps, priorities, are we well organized?
- Use lots of agents for thorough review, orchestrate subagents
- TFLite coordinates confirmed CORRECT (normalized 0-1, verified by running model)
- Fixed main.py: home position from real GPS, LAND retry, CENTERING return after timeout
- Fixed pi_flight.py: RTL passive bypass, FP logging GPS, stale cluster index after pop
