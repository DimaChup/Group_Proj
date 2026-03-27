# TEST CHECKLIST 5.8 — Complete Documentation Index

**Created**: 2026-03-27  
**Branch**: Working5.8  
**Total Documentation**: 3 files, 1,216 lines

---

## Files Overview

### 1. TEST_CHECKLIST_5.8.md (823 lines)
**Main checklist document** — The authoritative test procedure

Contains:
- **Pre-Test Setup** (3 sections)
  - Environment verification (SITL, venv, DRONE_MODE)
  - Simulation environment setup
  - Dummy placement workflow

- **22 Comprehensive Tests**
  - Test 1: Full autonomous mission (baseline)
  - Test 2: Smart detection (--smart-detect)
  - Test 3: Center verify (--center-verify)
  - Test 4-5: Geofence enforcement (--no-nfz)
  - Test 6-7: Manual override & multi-target queue
  - Test 8-9: NFZ speed capping & detection filtering
  - Test 10-14: CLI flags (--beacon-delay, --transit, --alt, --dry-run, --headless)
  - Test 15-22: Refactoring, stream server, thresholds, queues, logs

- **Structure for each test**:
  - Purpose (what is tested)
  - Command (exact CLI)
  - Test steps (numbered walkthrough)
  - Pass criteria (checklist)
  - Fail/Investigate (troubleshooting)

- **Summary section**
  - Quick run (5 critical tests, ~20 min)
  - Full run (all 22 tests, ~45-60 min)
  - Pass definition (0 crashes, all states reachable)

**Use this for**: Actual testing, step-by-step walkthrough, issue diagnosis

---

### 2. TEST_CHECKLIST_5.8_FEATURES.md (294 lines)
**Feature-to-test mapping** — Links commits/features to tests

Contains:
- **Code Refactoring** (3 commits, 5 files affected)
  - main.py 909 lines (was 1800)
  - state_machine.py, navigation.py, gps_utils.py, stream_server.py

- **Safety & Geofence** (2 commits)
  - KML loading, speed capping, repulsive force, auto-manual mode

- **Detection Pipeline** (6 commits)
  - Queue, polygon filtering, dedup, reject radius, manual queueing, persistence

- **Confidence Threshold** (1 commit)
  - Threshold 0.2 (tuned for deployment)

- **Manual Override** (keyboard input)
  - M key (manual mode), Y/N/I/X (mark detections), L (land)

- **CLI Flags** (detailed for each)
  - --speed, --smart-detect, --center-verify, --no-nfz, --beacon-delay
  - --transit, --alt, --dry-run, --headless, --model

- **Web UI & Stream Server** (1 commit)
  - MJPEG stream, state display, queue viz, HTTP buttons

- **Summary Table** (22 rows)
  - Maps test number → feature → commit(s)

- **Known Limitations** (5 items)
  - Beacon delay, FP16 quantization, NCNN testing, INT8, multi-threading

- **Before Flight Day** (5 steps)
  - Merge procedure, Pi deployment, first flight

**Use this for**: Understanding what changed, validating test coverage, mapping commits

---

### 3. TEST_CHECKLIST_5.8_SUMMARY.txt (99 lines)
**Quick reference** — Single-page overview

Contains:
- What's covered (7 categories)
- Quick run (5 tests, 20 min)
- Full run (22 tests, 45-60 min)
- Pass criteria (4 metrics)
- Structure (what each test includes)
- Testing environment (platform, mode, venv, SITL, map, model)
- Next steps (setup → test → deploy)

**Use this for**: Quick briefing, printing, one-page summary

---

## Quick Navigation

| Need to... | Read... |
|-----------|---------|
| Run the tests | TEST_CHECKLIST_5.8.md |
| Understand commits | TEST_CHECKLIST_5.8_FEATURES.md |
| Quick overview | TEST_CHECKLIST_5.8_SUMMARY.txt |
| Print a reference | TEST_CHECKLIST_5.8_SUMMARY.txt |
| Troubleshoot failure | TEST_CHECKLIST_5.8.md + Fail/Investigate section |
| Check test coverage | TEST_CHECKLIST_5.8_FEATURES.md (Summary Table) |
| Brief team | TEST_CHECKLIST_5.8_SUMMARY.txt |

---

## Key Statistics

| Metric | Value |
|--------|-------|
| Total tests | 22 |
| Quick run duration | ~20 minutes |
| Full run duration | ~45-60 minutes |
| Critical tests (quick run) | 5 |
| Code files modified | 5 main modules + extracted 4 modules |
| Main.py reduction | 1800 → 909 lines |
| CLI flags covered | 10+ (--speed, --smart-detect, etc.) |
| Safety-critical tests | 4 (geofence, NFZ, queue validation) |
| Documentation lines | 1,216 total |

---

## Testing Workflow

### Before Testing
1. Open TEST_CHECKLIST_5.8.md
2. Read "Pre-Test Setup" (verify environment)
3. Start SITL (Mission Planner or mavproxy)
4. Activate test_env venv
5. Set DRONE_MODE=SIMULATION

### During Testing
1. Pick Quick Run or Full Run
2. For each test:
   - Read Purpose and Command
   - Follow Test Steps (numbered)
   - Check Pass Criteria (use checklist)
   - If fail, see Fail/Investigate
3. Log results (pass/fail, times)

### After Testing
1. Review all pass/fail results
2. If all pass: ready for deployment
3. If failures: fix and re-test before merge
4. Document issues in CLAUDE.md session log
5. Merge Working5.8 to MainOne2

---

## Testing Environments

| What | Laptop | Pi |
|-----|--------|---|
| Simulation | YES (SITL) | NO (no SITL) |
| Real (camera) | YES (webcam) | YES (Pi camera) |
| Real (Cube) | NO (SITL) | YES (mavproxy) |
| Headless | N/A | YES (--headless) |
| Web UI | http://localhost:8090 | http://PI_IP:8090 |
| Recommended | Full checklist | Field tests only |

---

## Safety Notes

**Before ANY flight**:
- [ ] Geofence logic tested (TEST 4, 8)
- [ ] Detection filtering working (TEST 9)
- [ ] Queue deduplication verified (TEST 7)
- [ ] Manual mode tested (TEST 6)
- [ ] Log file generation confirmed (TEST 22)

**On Flight Day**:
1. Run at least Quick Run (5 tests) beforehand
2. Verify all safety systems (NFZ, queue, reject radius)
3. Test manual override on ground (M key responsive)
4. Confirm battery and GPS work in REAL mode
5. Have backup plan if any test fails

---

## Troubleshooting Quick Links

| Issue | Test | Section |
|-------|------|---------|
| Drone doesn't fly | TEST 1 | Fail/Investigate |
| Detections unreliable | TEST 2, 17 | Smart detect, Confidence |
| NFZ not working | TEST 4, 8 | Geofence Enforce, Speed Cap |
| Manual mode broken | TEST 6 | M key Workflow |
| Queue issues | TEST 7, 19 | Multiple dummies, Manual queue |
| Web UI not loading | TEST 16 | Stream Server |
| Code crashes | TEST 15 | Refactoring Validation |
| Log file missing | TEST 22 | Log File Generation |

---

## Version Control

**Branch**: Working5.8  
**Based on**: MainOne2 (remote origin)  
**Merge target**: MainOne2 (after all tests pass)  
**Latest commits**:
- e5b312f: Refactor _handle_keys into 3 focused methods
- db481f2: Real flight workflow, report notes, path simulation script
- f75a58e: Refactor _handle_search into 4 focused methods

---

## Contact & Support

If tests fail:
1. Check Fail/Investigate section in TEST_CHECKLIST_5.8.md
2. Review relevant commits in TEST_CHECKLIST_5.8_FEATURES.md
3. Check CLAUDE.md for hardware/config details
4. Run TEST 15 (refactoring) to ensure integration OK
5. Report issue with test number, command, and error output

---

**Generated**: 2026-03-27  
**For**: Working5.8 pre-deployment validation  
**Audience**: Test lead, team members, flight day coordinator
