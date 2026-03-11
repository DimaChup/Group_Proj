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
