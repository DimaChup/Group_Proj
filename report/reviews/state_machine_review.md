# State Machine Diagram Review

Validated against: `states.py` (20 states), `state_machine.py` (all `_handle_*` methods), `A1_state_table.tex`.

## State Count

- `states.py`: **20 states** (INIT, CONNECTING, ARMING, TAKEOFF, PRE_WAYPOINTS, TRANSIT_TO_SEARCH, SEARCH, CENTERING, DESCENDING, VERIFY, HOVER, APPROACH, RETURN_TO_SEARCH, RETURN_FROM_MANUAL, HOVER_TARGET, RETURN_TRANSIT, RETURN_HOME, LANDING, MANUAL, DONE)
- `A1_state_table.tex`: Claims "20 states, 32 transitions" -- **correct** (all 20 listed)
- `gen_state_machine_full.py`: Positions dict `P` has all 20 states -- **correct**
- `CLAUDE.md` header says "19 states" -- **wrong**, should be 20

## Simplified Diagram (`state_machine.pdf` / `state_machine_simple`)

Shows 10 states: INIT, TAKEOFF, SEARCH, CENTERING, VERIFY, APPROACH, LANDING, DONE, MANUAL, RTL.

### Issues Found

1. **RTL is NOT a state in the code.** It is firmware-level behaviour (ArduPilot RTL on RC failsafe). Showing it as a state box is misleading. Should be an annotation/note, not a box. The full diagram handles this correctly with a text annotation.

2. **VERIFY -> SEARCH (N):** Shown as the only rejection path. In code, VERIFY N can go to CENTERING (queued target), RETURN_TO_SEARCH, RETURN_FROM_MANUAL, or SEARCH. Acceptable simplification but the label "Rejected [N]" going only to SEARCH is slightly misleading since there are intermediate states.

3. **MANUAL -> SEARCH (resume):** In code, MANUAL can resume to ANY previous state, go to RETURN_FROM_MANUAL, or go to CENTERING. Showing it returning only to SEARCH is a simplification.

4. **Missing "I" (interest) path from VERIFY.** Only Y and N shown. Acceptable for simplified view.

**Verdict: Fair representation of the main flow.** The RTL box is the only real concern -- it should be styled differently (annotation, not a state box) to avoid confusion with actual states.

## Full Diagram (`state_machine_full.pdf`)

Shows all 20 states with phase groupings. More detailed analysis:

### Correct Transitions

- INIT -> CONNECTING -> ARMING -> TAKEOFF (startup flow)
- TAKEOFF -> PRE_WAYPOINTS -> TRANSIT_TO_SEARCH -> SEARCH
- SEARCH -> CENTERING (detection)
- CENTERING -> DESCENDING -> VERIFY (engagement)
- VERIFY -> HOVER_TARGET (Y confirm)
- HOVER_TARGET -> APPROACH -> LANDING -> DONE
- VERIFY -> RETURN_TO_SEARCH (N reject, I interest)
- RETURN_TO_SEARCH -> SEARCH
- HOVER_TARGET -> RETURN_TRANSIT -> RETURN_HOME -> LANDING
- MANUAL -> RETURN_FROM_MANUAL -> TRANSIT_TO_SEARCH
- SEARCH -> HOVER (no WPs)
- SEARCH -> DONE (all waypoints exhausted)
- Any -> MANUAL (M key)

### Missing Transitions (not shown)

1. **TAKEOFF -> ARMING** (SIM disarm retry) -- important for simulation debugging
2. **TAKEOFF -> DONE** (REAL disarm -- safety stop)
3. **CENTERING -> SEARCH** (60s timeout) -- important safety timeout
4. **VERIFY -> SEARCH** (120s timeout auto-reject) -- important safety timeout
5. **VERIFY -> CENTERING** (N/I when queued target exists) -- the code pops queued targets on reject/interest
6. **VERIFY -> RETURN_FROM_MANUAL** (N when previous_state was MANUAL)
7. **PRE_WAYPOINTS -> HOVER** (no search waypoints generated)
8. **MANUAL -> CENTERING** (M resume when target visible or queued)
9. **MANUAL -> previous_state** (M resume when close to departure, <5m)
10. **SEARCH -> SEARCH** (rescan at lower altitude -- self-loop)
11. **HOVER -> DONE** (60s timeout)

### Incorrect/Misleading Labels

1. **HOVER_TARGET -> RETURN_TRANSIT label says "Beacon timeout"**: This is wrong. The actual trigger is `elapsed > 15s` after the servo deploy sequence completes. It has nothing to do with a beacon. Should say "Deploy complete (15s)" or "Servo sequence done".

2. **RETURN_FROM_MANUAL -> TRANSIT_TO_SEARCH**: The code actually returns to `self.previous_state`, which could be ANY state (SEARCH, CENTERING, PRE_WAYPOINTS, etc.), not specifically TRANSIT_TO_SEARCH. The arrow target is misleading.

### Color Categories

- Green (Start/End): DONE = green, INIT = grey (should arguably be green for "start"). In simplified diagram INIT is green. **Inconsistency** between simplified and full diagram.
- Blue (Transit/Autonomous): PRE_WAYPOINTS, TRANSIT_TO_SEARCH, APPROACH, LANDING = correct
- Orange (Engagement/Verify): CENTERING, DESCENDING, VERIFY, HOVER_TARGET = correct
- Yellow (Recovery): RETURN_TO_SEARCH, RETURN_FROM_MANUAL, RETURN_TRANSIT, RETURN_HOME = correct
- Red (Safety): MANUAL = correct
- Grey (Startup): INIT, CONNECTING, ARMING, TAKEOFF, HOVER = correct
- **SEARCH is green_dark** but it is the core autonomous phase. Could be blue for consistency with "autonomous" or keep green_dark as its own category. Current grouping is fine.

### Phase Background Groupings

- Startup (INIT, CONNECTING, ARMING, TAKEOFF): Correct
- Transit (PRE_WAYPOINTS, TRANSIT_TO_SEARCH): Correct
- Search (SEARCH): Correct
- Engagement (CENTERING, DESCENDING, VERIFY, HOVER_TARGET, APPROACH, LANDING, DONE): Partially correct. APPROACH and LANDING are more "landing sequence" than "engagement". DONE is terminal.
- Recovery (RETURN_TO_SEARCH, RETURN_FROM_MANUAL, RETURN_TRANSIT, RETURN_HOME): Correct
- Safety (MANUAL): Correct

## A1_state_table.tex Comparison

The tex table is the most accurate document. Cross-checking against code:

### Correct in tex table
- All 20 states listed with correct entry conditions
- Timeout values match code (CENTERING 60s, VERIFY 120s, HOVER 60s, LANDING 90s)
- DESCENDING correctly noted as "bypassed"
- Global overrides (M, K, B, ESC, geofence, RC failsafe) all correct

### Issues in tex table
1. **CENTERING exit says "dist to TGT < 1m -> VERIFY"**: Correct, but code goes CENTERING -> VERIFY directly (skips DESCENDING). The tex table lists DESCENDING as a separate state that immediately transitions. This is accurate to code.
2. **VERIFY N exit lists 4 options**: CENTERING / RETURN_FROM_MANUAL / RETURN_TO_SEARCH / SEARCH. **Correct and comprehensive.**
3. **APPROACH exit says "dist < 2m and alt < 4m -> HOVER_TARGET"**: Code says the same. **Correct.**
4. **Claims "20 states, 32 transitions"**: The transition count is approximately correct but the actual distinct transitions from code analysis is ~35+ depending on how you count conditional branches.

## Recommended Fixes

### Critical (affects accuracy)
1. Full diagram: Change "Beacon timeout" label on HOVER_TARGET -> RETURN_TRANSIT to "Deploy complete (15s)"
2. Full diagram: Change RETURN_FROM_MANUAL arrow to point to a generic "previous state" annotation instead of TRANSIT_TO_SEARCH specifically

### Important (completeness)
3. Full diagram: Add CENTERING -> SEARCH (60s timeout, dashed line)
4. Full diagram: Add VERIFY -> SEARCH (120s timeout, dashed line)
5. Full diagram: Add HOVER -> DONE (60s timeout)
6. Full diagram: Add VERIFY -> CENTERING (queued target on N/I)

### Minor (nice to have)
7. Simplified diagram: Change RTL from a state box to a text annotation
8. Full diagram: Make INIT green to match simplified diagram convention
9. Full diagram: Add SEARCH self-loop for rescan
10. Full diagram: Add TAKEOFF -> DONE and TAKEOFF -> ARMING fallback paths
