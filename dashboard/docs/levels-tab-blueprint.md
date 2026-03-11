# LevelsTab Blueprint

> Line-range map for LevelsTab.tsx (573 lines) + mission-data.ts L2 data (~350 lines).
> Read this BEFORE the source files.

## Component Hierarchy

```
LevelsTab (7-75)
├── Philosophy intro (13-35) — "Why Three Levels?" card
├── Level cards (38-72) — L1/L2/L3 expandable cards
│   └── LevelDetail (454-573) — expanded content for each level
│       ├── Description (458)
│       ├── L2 Focus Areas (461-492) — 6 pillars grid (L2 only)
│       ├── L2SteppingStones (495) — the big section (L2 only)
│       │   ├── CriticalPathRows (249-326) — LEFT column
│       │   │   └── StepCard (178-246) — individual step with IF scenarios
│       │   ├── Orange divider (417) — vertical gradient line
│       │   └── ParallelTaskCard (328-377) — RIGHT column items
│       ├── State flow (498-501)
│       ├── Drone/Pilot actions grid (503-529)
│       ├── Scripts list (532-542)
│       └── Working/Missing grid (544-570)
```

## Layout: 3-Column Stepping Stones

```
┌───────────────────────────┬──┬─────────────────┐
│  CRITICAL PATH (left)     │▌│ BENCHMARKS (right)│
│  Steps in sequential rows │▌│ Grouped by:       │
│  ① → ② → ③ → ④ ...      │▌│ • Calibration     │
│  Steps on same row =      │▌│ • Accuracy        │
│  parallel (side by side)  │▌│ • Tuning          │
│                           │▌│ • Data            │
│  ★ Milestones between     │▌│                   │
│    rows (purple bars)     │▌│ 20 tasks total    │
└───────────────────────────┴──┴─────────────────┘
Grid: grid-cols-[1fr_auto_280px]
Divider: 2px orange gradient (vertical)
```

## Data Sources (all in mission-data.ts)

| Export | Lines | What |
|--------|-------|------|
| `L2_CRITICAL_PATH` | 435-620 | 14 steps across 12 rows, with IfScenarios |
| `L2_MILESTONES` | 630-650 | 3 purple markers (afterRow: 2, 5, 8) |
| `L2_PARALLEL_TASKS` | 655-800 | 20 tasks in 4 categories |
| `LEVELS` | 124-261 | L1/L2/L3 definitions (droneActions, pilotActions, etc.) |
| Interfaces | 397-430 | IfScenario, SteppingStone, ParallelTask, Milestone |

### L2_CRITICAL_PATH Steps (14 steps, 12 rows)

| Row | ID | Name | Status |
|-----|----|------|--------|
| 1 | cp-1 | All components healthy | done |
| 2 | cp-2 | Outdoor GPS 3D fix | todo |
| 3 | cp-2a | Mission Planner AUTO waypoints | todo |
| 4 | cp-3 / cp-4 | Manual flight + CV ‖ Fly GPS waypoints | todo |
| 5 | cp-5 / cp-6 / cp-6b | Geotagging ‖ CV centering ‖ Geofence test | todo |
| 6 | cp-7 | Fly search pattern (no CV action) | todo |
| 7 | cp-8 | Search + detect + confirm Y/X | todo |
| 8 | cp-9 | Offset landing + payload | todo |
| 9 | cp-10 | PLB focused search redirect | todo |
| 10 | cp-11 | Items of interest Y/I/X | todo |
| 11 | cp-12 | SSSI geofence in search | todo |
| 12 | cp-13 | Full L2 mission | todo |

Milestones: ★ after row 2 ("components working"), ★ after row 5 ("can geotag"), ★ after row 8 ("can find + deliver")

### L2_PARALLEL_TASKS (20 tasks, 4 categories)

**Calibration (3):** FOV (done), Lens distortion (done), Real-altitude FOV (todo)
**Accuracy (5):** GPS drift, GPS hover, GPS estimation error, Rangefinder, Battery endurance
**Tuning (6):** Pi FPS (done), Altitude sweep, Speed sweep, Model compare, Confidence threshold, NCNN, Resolution
**Data (4):** Training images, Stream latency, Comms range, Retrain model

## Inline Data (in LevelsTab.tsx, NOT in mission-data.ts)

**L2_FOCUS_AREAS** (lines 78-161): 6 focus pillars rendered as a 3x2 grid for L2 only.
- Computer Vision (CV), Flight Algorithm (FA), Hardware Integration (HW)
- Ground Station (GS), Safety & Failsafes (SF), Payload Delivery (PL)
- Each has: label, color, icon, summary, details[], status

**STATUS_DOT** (164-169): done=green✓, ready=blue●, todo=gray○, blocked=red✕
**CATEGORY_LABELS** (171-176): CAL=orange, ACC=cyan, TUNE=purple, DATA=amber

## Key Components

### StepCard (178-246)
Expandable card for critical path steps. Shows:
- Name + status badge (collapsed)
- Description text (collapsed)
- PROVES / SCRIPT / OUTPUT / AFTER / Decision Points (expanded)
- IfScenarios render as amber diamond bullets with condition → outcome

### CriticalPathRows (249-326)
Groups steps by `row` number. Same-row steps render side-by-side (`grid-cols-2`).
Timeline: numbered circles (green checkmark if all done) + connecting vertical line.
Milestones: purple star + gradient lines + label between rows.

### ParallelTaskCard (328-377)
Similar to StepCard but shows category badge (CAL/ACC/TUNE/DATA).
Collapsed: truncated description. Expanded: script, output, dependencies.

### L2SteppingStones (380-452)
Container for the 3-column layout. Progress counters: "Critical: X/14, Parallel: Y/20".
Parallel tasks grouped by category with sub-headers.

### LevelDetail (454-573)
Full expanded content for any level. L2-specific sections (focus areas, stepping stones)
render only when `level.id === 2`.

## How to Update Data

| What | Where | How |
|------|-------|-----|
| Step status | mission-data.ts `L2_CRITICAL_PATH` | Change `status` field |
| Add new step | mission-data.ts `L2_CRITICAL_PATH` | Add object, set `row` for position |
| Add milestone | mission-data.ts `L2_MILESTONES` | Add `{ afterRow, label, detail }` |
| Parallel task status | mission-data.ts `L2_PARALLEL_TASKS` | Change `status` field |
| Add IF scenario | mission-data.ts step's `ifScenarios` | Add `{ condition, outcome }` |
| Focus areas | LevelsTab.tsx `L2_FOCUS_AREAS` (line 78) | Edit inline constant |

## Cross-References

- Flight day checklist: `docs/FLIGHT_DAY_CHECKLIST.md` (step order should match critical path)
- Test scripts: `tests/flight/` (numbered 0a-4, maps to critical path steps)
- Config values referenced: `config.py` (TARGET_ALT, SEARCH_SPEED_MPS, FOCAL_LENGTH_MM, etc.)
- Simulator rehearsal: `simple_simulator.py` (practice before real flights)
