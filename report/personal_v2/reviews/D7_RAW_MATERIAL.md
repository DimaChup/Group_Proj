# D7 Raw Material Bank — Apollo (Dmytro)

Concrete, citable incidents and contributions for the D7 reflective report.
All commits authored by `Apollo` on branches MainOne2/Working7-9/MainWorking1-4.
Total commits across branches: 820+.

---

## TEAMWORK

### Handoff to Robin (teammate, mission-script owner)
- **Commit `a5b1ab7`** `passive_watch_2.py: Robin integration (--robin flag, cv_mode polling, 2-image output)` — Apollo built a dedicated integration path so Robin's state machine could poll vision results over HTTP without touching the CV code.
- **Commit `885cee4`** `Passive_watch docs restructured for Robin: exact command, JSON format, parsing` — wrote a README specifically for Robin: exact CLI, JSON schema, parsing examples. Evidence of anticipating a teammate's needs instead of dumping code.
- **Commit `36b6069`** `Robin package, design rationale +3 MCDA tables, energy fix, passive_watch_2` — packaged a self-contained deliverable for Robin.
- `docs/DESIGN_DECISIONS.md:107-109` — explicit split of responsibilities: "Robin's script handles flight only (no camera). Our `pi_flight.py` handles camera + vision + stream. Both run in parallel, no conflict."
- **Commit `24783d9`** `CHECKLIST: clarify our role = passive_watch providing GPS to Robin's state machine` — publicly documented division of labour.
- **Commit `2bbad/cec899e/56055e0`** auto-clear flag for passive_watch SMART cycle — built specifically because Robin's mission script needs a clean re-lock after first target.
- `docs/VISION_PIPELINE_FOR_COLLEAGUE.md` + `docs/COLLEAGUE_CHECKLIST.md` (CLAUDE.md line 995-997) — wrote full onboarding docs for a colleague taking over the vision pipeline.

### Demetro (FDR slides teammate)
- **Commit `32fb0c5`** `FDR presentation slides HTML: 2 full-screen slides for Demetro` — Apollo built Demetro's presentation materials.
- **Commit `b2a9cd4`** `FDR presentation: Demetro's 2 slides with full speaking scripts` — went further and wrote the speaking scripts (246 + 219 = 465 words, 3.1 min, commit `ba667f2`).
- **Commits `9b826f8, 7920e5a, 794ef5c`** — teleprompter sidebar, iterated 4-5 times on polishing the scripts for his teammate's delivery.
- Evidence of team-first behaviour: Apollo wrote and polished HIS TEAMMATE's slides AND speaking scripts.

### Team-wide advocacy (complaint letter)
- `docs/COMPLAINT_LETTER.md` — Apollo drafted a detailed, measured, factual complaint about hardware failures on behalf of the whole team. Tone is notably restrained: "We are not assigning personal blame. We are documenting what happened."
- `docs/COMPLAINT_LETTER.md:98+` — appended full chat history with Steve as evidence. Professional grievance handling, not venting.
- Commits `26e3255, f3401e4, d946838, 5af87d0, 847518e` — six iterations on the Steve communication strategy, tone, phrasing. Apollo chose to lead the team's external communication.
- **Commit `4b0fd91`** `D6 clarity letter to Steve: ready to send tomorrow morning` — turned grievance into a constructive clarification request.

### Cross-team awareness
- `COMPLAINT_LETTER.md:39` — notes that borrowing the green team's drone "does not constitute a plan" because it risks "disruption to a team whose hardware actually works." Apollo explicitly considered impact on OTHER teams, not just his own.

---

## SELF-MANAGEMENT

### Resilience when flight days collapsed (hardware failures)
- `COMPLAINT_LETTER.md:19-21` — "Three flight days were scheduled. Our team completed zero successful flights... approximately eight weeks... zero seconds of real flight data." This is the defining constraint of the project.
- **CLAUDE.md Session 2026-03-11 part 2** — FLIGHT DAY 1: weather cancelled flight. Instead of going home, Apollo did bench testing, FOV calibration (92cm at 1m → FOCAL_LENGTH_MM=5.46, commit `fbc9a99`), lens calibration with checkerboard (commit `319c69f`), built `FIELD_QUICK_REF.md` (commit `12f1c4d`) for no-internet field use, and ran comprehensive benchmarks (commits `b7ff98a, da42e96`). 10+ commits in one cancelled field day.
- **CLAUDE.md Session 2026-03-30/31** — Pi field day: "calibration_data.npz was corrupt → deleted, everything works without it." Apollo diagnosed the mangled-frames bug on-site and made undistortion optional.
- `COMPLAINT_LETTER.md:51-60` — entire "What we built despite this" section: 40+ test scripts, SITL, state machine, retrained model, web GS — all in response to having no drone.

### Progressive test methodology (ownership / planning under pressure)
- `tests/flight/` numbered 0a → 4 (CLAUDE.md Session 2026-03-09): Apollo organised all flight tests into a "never skip a step" ladder. `memory/testing-pattern.md` documents it as a reusable pattern.
- 6 new "gap-fill" test scripts created in one session (`0d_planning_test.py`, `0e_geofence_test.py`, `0f_servo_test.py`) — filled holes in the test ladder before flight day.
- 127 unit test functions across 6 files (CLAUDE.md Session 2026-04-03) — Apollo built a full test harness voluntarily, not because it was required.

### Sustained technical ownership of modules
- **main.py refactor**: 1411 → 754 lines, 6 modules extracted, 146 pytest tests (MEMORY.md "Session 2026-03-20 (Major)"). Commit session `session-2026-03-20.md` in memory.
- **GPS estimation math ownership**: IVW weighting, Kalman filter, SMART clustering — Apollo owned the full pipeline. Commits `1d8c383` (Level 1 IVW/Kalman detail), `dbd24f3` (three-level architecture), `94144bd` (7-method comparison), `aab8a1f` (CEP progression visual), `dc67a8e` (accuracy table 7m→3.5m→1.8m→1.5m).
- **Tilt compensation saga** (12+ commits: `ad207ae, f47ed72, 841b490, 2fe1b63, 9df06f3, 65141c9, 60f362b, 4bf0213, 34c2161, a169a67, 7092794, 831c47d`) — Apollo discovered the GPS offset was wrong when the camera wasn't nadir, iterated ray-tracing math until it matched simulation, verified against a 1440-test sweep, then back-ported the fix to passive_watch.py for Robin.

### Debugging under frustration (self-management evidence)
- **Camera BGR/RGB fix** (SESSION_ARCHIVE.md 2026-02-17 part 2): "spent hours trying AWB modes, manual gains, gray world correction, ISP tuning file edits, kernel update (rpi-update) before discovering root cause." Then systematically tested all 6 channel permutations to nail the root cause. 10 files fixed in one commit.
- **Python 3.13 / tflite-runtime migration** (SESSION_ARCHIVE.md 2026-02-17): diagnosed that tflite-runtime doesn't work on 3.13, migrated to `ai-edge-litert`, updated vision.py import chain. Unblocked the entire Pi platform.
- **Cube serial / pyserial 3.13 bug** (SESSION_ARCHIVE.md 2026-02-17): "Raw `cat /dev/ttyAMA0` gets data fine, pymavlink can't parse it." Solved by routing through mavproxy UDP bridge. Documented the exact command in MEMORY.md so the team wouldn't rediscover it.
- **Three mavproxy issues debugged and fixed in one session** (SESSION_ARCHIVE.md 2026-02-18 part 2): (1) GCS heartbeat filtering, (2) target_system extraction, (3) mode name mapping — all traced through patient log analysis. Fixes pushed to `cube_commands.py`, `bench_mission.py`, AND `main.py`.
- **Double-scaling GPS estimation bug** (CLAUDE.md Session 2026-03-30/31, commit `7eb7cc8`): `detect_in_image` returned pixel coords but passive_watch multiplied by w,h again → overlay 100m+ off. Apollo diagnosed and fixed both the overlay and the GPS normalisation (commit `297aab2`).
- **TFLite bbox coord bug** (commit `3d62e6a`): treating pixel coords (0-640) as normalised (0-1) → green boxes drawn off-screen. Added `PIXEL_COORD_THRESHOLD` check.
- **Geofence RTL crash** (CLAUDE.md Session 2026-04-03 part 2, commit `ce5c036`): mode 6 (RTL) wasn't in the allowed-modes tuple → RC override guard skipped cv2.waitKey(1) → window froze. Apollo used 5 parallel agents to diagnose, then fixed three things at once (allowed modes, waitKey inside guard, state transition to LANDING).
- **Descent stall bug** (`memory/descent-stall-bug.md`): accepted as unresolved, labelled SITL-specific. Evidence of pragmatic judgement — not every bug is worth chasing when the real hardware is unavailable to verify.

### Sustained delivery pace
- 820+ commits on Apollo's branches; ~70+ commits on reports alone in the last two weeks pre-submission (D6 goldmine v1-v19, Reportflow v1-v5+final).
- D6 Goldmine iterated from score 74 → 85.2 across 6 scoring cycles (MEMORY.md "Report Improvement Progress").
- D6 Reportflow iterated from 81.0 → 87.2 with 4 new sections, bibliography added, 18→67 unique citations (commit `d0e684d`).
- D7 reflection iterated 6-7 times (68 → 83-84) before accepting "at ceiling" (MEMORY.md).

---

## INSIGHT

### Recognising what mattered most
- **brain-dump.md line 29** (2026-03-11 part 2): "ai-edge-litert was MISSING from requirements_pi.txt — critical fix for Pi Python 3.13." Spotted a single missing line that would have broken a teammate's setup.
- **brain-dump.md line 13** (2026-03-11): "Y/N input over PuTTY: added terminal keyboard + browser buttons to main.py." Apollo noticed the real blocker was the operator UX over SSH, not the mission logic. Built terminal input thread + HTTP `/cmd?key=` endpoint + browser buttons all in one session.
- **brain-dump.md line 10** (2026-03-11): "Split interactive drawing from flight scripts: draw on laptop → JSON → Pi loads headlessly." Recognised the headless/GUI split should be a boundary, not an `if` branch.

### Meta-reflection on process
- **brain-dump.md line 28** (2026-03-11): "New sessions should catch up easily without user repeating themselves." Built blueprints, MEMORY.md, `.claude/rules/` around this insight — clear evidence of thinking about his OWN workflow as something to improve, not just code.
- Created blueprint system: `docs/main_blueprint.md`, `docs/simple_simulator_blueprint.md`, `docs/pi_flight_blueprint.md`, `docs/passive_watch_blueprint.md` — all >500 line files mapped with line ranges.
- MEMORY.md "User Preferences": "Never edit code directly on Pi — laptop is single source of truth." Apollo articulated and enforced his own development discipline.

### Learning from specific failures
- **GPS timing lag** (`memory/gps-timing-lag.md`, CLAUDE.md 2026-03-16): discovered GPS has 100-200ms latency → 1m error at 5m/s. Not a bug to fix in code — a calibration insight gained from DJI video analysis. Apollo turned a dataset exploration into a lesson.
- **FOV miscalibration** (CLAUDE.md 2026-03-16): hardcoded 73° HFOV was wrong for cropped DJI video; real value 54.4°. Built `tools/fov_calibrate_video.py` (click top/bottom of dummy at 9 altitudes) to derive it empirically.
- **Geofence sign conventions** (`memory/geofence-signs.md`): "cv2.pointPolygonTest: positive = INSIDE (not outside!)" — Apollo wrote a dedicated memory file to prevent himself/future sessions from repeating the sign mistake.
- `docs/LESSONS_LEARNED.md` — Apollo initiated a formal lessons-learned doc (8 lessons) instead of leaving them scattered.

### Judgement calls under uncertainty
- **God view optimization** (commit `374a462`): pre-scaled map 63MB→4MB per frame (94% reduction). Apollo's own commit message acknowledges the tradeoff and flags the risk ("If `_god_scale` coordinate multiplication is wrong anywhere, polygons/drone could appear offset. Watch for this."). Wrote `memory/god-view-optimization.md` documenting what was sacrificed.
- **Sim vs real honesty pass** (commits `62a8136, 77f0238`): "Simulation accuracy: 3 wrong claims fixed, 2 missing features documented" — Apollo audited his OWN report for over-claims and corrected them before submission. Rare insight behaviour.
- **Two-step centering** (commit `22bcade`): hover 3s at rough estimate before nadir re-detection. Insight that a single detection is insufficient; hover-then-verify dramatically improves accuracy.
- **Multi-pass heading bias cancellation** (commit `53a7224`): realised GPS timing lag averages out if flights use bidirectional passes. Not just "fix the bug," but design around it.

### Framing the simulation-first strategy
- `COMPLAINT_LETTER.md:60`: "The simulation framework we created ourselves is the only reason this project produced any verifiable engineering output at all." This is Apollo's one-line thesis about the project — earned, not borrowed.
- `simple_simulator.py` (2508 lines): built from scratch with GPS drift simulation, camera shake, CV throttle, TFLite backend — the tool that let the team develop without hardware.
- Commit `3dec8e8` and similar: "four-phase confident detection flow" — Apollo structured the mission logic around increasing confidence as altitude drops.

### Quantified self-audit
- **MEMORY.md**: "Modularity audit: 3.8/5.0 overall (vision.py highest at 4.5, main.py lowest at 3.0)." Apollo ran a formal scoring of his own architecture and published the weakest module.
- **MEMORY.md**: "Needs vs capabilities scoring: Simulation 7.7/10, Real hardware 2.1/10." Brutally honest capability self-assessment.
- `docs/NEEDS_VS_CAPABILITIES.md` — created a requirements traceability matrix.
- Commit `ce5c036`: "R01-R12 code fixes (all 12 requirements now MET in simulation)" — Apollo walked through the brief requirements one-by-one and closed gaps (geofence, altitude cap, TOL distance check, landing distance print, detection photos, LICENSE file).

---

## BONUS: Specific technical artifacts to name in the report

- `passive_watch.py` (752 lines) — Apollo's standalone observer with MJPEG stream + SMART clustering + GPS estimation + map panel with SSSI/search-area polygons (commit `41e713c`, `c89127b`).
- `simple_simulator.py` (2508 lines) — interactive MVP covering the whole mission with keyboard flight.
- `tests/unit/` — 127 test functions Apollo wrote voluntarily.
- `cv_models/sar_v2_1088/best.tflite` — retrained model at mAP50=0.995 (300 syn + 16 real + 50 neg at 1456×1088). Apollo owned the dataset generator, label tool, FOV calibration, and Colab training.
- `dataset_v3` multi-class (5-class: dummy, pants, tshirt, backpack, cone) — 3500 images generated for the second training run (CLAUDE.md Session 2026-04-03 part 2).
- `FIELD_QUICK_REF.md` — no-internet field reference Apollo wrote on the first cancelled flight day.
- `docs/MAIN_FEATURES.md` — 19 verified safety features documented by Apollo.
- Headless support in main.py: terminal input thread + `/cmd?key=` HTTP endpoint + browser buttons, all in one session (2026-03-11).

---

## KEY TEAMMATE NAMES (for report prose)

- **Robin** — owned flight/state-machine script; Apollo built passive_watch integration for him.
- **Demetro** — gave FDR presentation; Apollo built his slides and speaking scripts.
- **Zian** — mentioned in working directory (`Zian/` folder in git status). Role unclear from code history.
- **Steve** — course organiser (NOT a teammate). Subject of the formal clarification letter.
- **Sid** — technical assistant; provided the single DJI training video Apollo used for FOV calibration.
