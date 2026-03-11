# SAR Drone Dashboard

## What This Is

Standalone React web app that visualizes the SAR drone group project's:
- **Systems engineering strategy** (SE layers, ambition levels, approaches, team roles)
- **Work breakdown structure** (~90 tasks, assignees, progress tracking)
- **Flight day roadmap** (prep tiers, technical steps, timeline)
- **Hardware inventory** (components, connections, setup guides)
- **Mission overview** (scenario, requirements, constraints, deliverables)

Lives inside v3/ but is completely independent — its own node_modules, own Vite server.
Does NOT interfere with the Python drone code at all.

## Origin

Copied from the Orgnaiser project (`../Orgnaiser/client/src/pages/trade-study-lab/`).
The original has 15+ tabs for a volcanic drone assignment; we only took the last 3 tabs
that are specific to the SAR group project (GP v2, Mission WBS), then expanded with
Mission, Hardware, Levels, Roadmap, Team, Notes, and Hub tabs.

## How to Run

```bash
cd v3/dashboard
npm install      # first time only
npm run dev      # opens on http://localhost:5050
```

## Tech Stack

React 18 + TypeScript + Vite + Tailwind CSS. No backend, no database — all data in TypeScript constants.

## Structure

```
dashboard/
├── CLAUDE.md              ← THIS FILE — ground truth for LLM sessions
├── package.json           ← React + Vite + Tailwind
├── brain-dump.md          ← Append-only user messages (ideas preserved)
├── NICE_TO_HAVE.md        ← Improvement backlog with impact/effort scoring
├── .claude/
│   ├── rules/
│   │   ├── design.md      ← Always loads: philosophy, quality ratchet, post-task checklist
│   │   └── ui.md          ← Loads for src/**: component patterns, data update rules
│   └── commands/
│       ├── status.md      ← /status — type check, task counts, doc freshness
│       ├── whats-next.md  ← /whats-next — top priorities from NICE_TO_HAVE
│       └── wrap-up.md     ← /wrap-up — end-of-session checklist
├── docs/                  ← Module blueprints (when files >500 lines)
│   ├── levels-tab-blueprint.md  ← LevelsTab + mission-data L2 data map
└── src/
    ├── main.tsx               (10 lines)
    ├── App.tsx                (100 lines) — tab routing, sidebar toggles
    ├── index.css              (16 lines)
    └── pages/
        │
        │── Tab pages
        ├── ReadmeTab.tsx                ← README overview — first tab, share with team (350 lines)
        ├── GroupProjectV2Tab.tsx         ← GP v2 page — 3-panel SE overview (103 lines)
        ├── MissionWBSTab.tsx             ← WBS tree + filtering (415 lines)
        ├── RoadmapTab.tsx               ← Flight day + full timeline + technical steps (883 lines)
        ├── HardwareTab.tsx              ← Components, connections, guides (227 lines)
        ├── MissionTab.tsx               ← Scenario, requirements, constraints (200 lines)
        ├── LevelsTab.tsx                ← 3 product levels + L2 stepping stones (573 lines)
        ├── TeamTab.tsx                  ← Who's doing what, blockers (188 lines)
        ├── NotesTab.tsx                 ← Ideas, wants, plans (140 lines)
        │
        │── Navigation / layout
        ├── HubPage.tsx                  ← Landing page — project status grid (173 lines)
        ├── TopBar.tsx                   ← Icon strip + panel toggles (76 lines)
        ├── TopPanels.tsx                ← Overlay panels from top bar (294 lines)
        ├── LeftSidebar.tsx              ← Left sidebar (83 lines)
        ├── RightSidebar.tsx             ← Right sidebar: Team/Prep/Focus/Day1 modes (676 lines)
        │
        │── Shared components (used by GP v2 tab)
        ├── GroupProjectV2Components.tsx ← 11 UI components (586 lines)
        ├── MethodologyV2Sidebar.tsx     ← Left sidebar for GP v2 (321 lines)
        ├── BigPictureV2View.tsx         ← Level pathway L1→L2→L3 (116 lines)
        ├── ContributionV2Matrix.tsx     ← Team x goal matrix (138 lines)
        ├── IntegrationV2Oversight.tsx   ← Cross-cutting concerns (110 lines)
        ├── MissionV2Readiness.tsx       ← Equipment, emergencies, risks (346 lines)
        │
        │── Data files
        ├── flight-day-data.ts           ← Flight day data — BEING SPLIT INTO 3 FILES (1709 lines)
        │   ├── flight-day-types.ts      ← (planned) Type definitions
        │   ├── flight-day-prep.ts       ← (planned) Prep status & checklists
        │   └── flight-day-tiers.ts      ← (planned) Tier steps & operations
        ├── group-project-v2-data.ts     ← SE layers, team, approaches (1312 lines)
        ├── hardware-data.ts             ← Component specs, connections (539 lines)
        ├── hub-data.ts                  ← Hub navigation cards (361 lines)
        ├── mission-data.ts              ← Mission levels, roadmap, L2 stepping stones (800 lines)
        ├── readme-data.ts               ← README tab data: overview, tests, calibration, flight plan
        └── wbs-data.ts                 ← 93 WBS nodes (336 lines)
```

## Tabs

1. **README** — Complete project overview for the team: what we built, test scripts, calibration, flight day plan, architecture
2. **Mission** — The what: scenario, requirements, constraints, deliverables
2. **Hardware** — All components, connections, setup guides, and links
3. **Levels** — The how: 3 product levels + L2 stepping stones (14-step critical path, 3 milestones, 20 parallel tasks, IF scenarios)
4. **Roadmap** — Flight Day 1 prep / Full Timeline / Technical Steps (3 sub-views)
5. **Hub** — Landing page: project status, flight testing, architecture
6. **Team** — Who's doing what, level focus, blockers
7. **Notes** — All ideas, wants, and plans
8. **GP v2 (Snapshot)** — SE overview: Holy Grail, 3 ambition levels, 6 SE layers, approaches, contribution matrix, integration, readiness
9. **Mission WBS** — ~90 tasks in collapsible tree, color-coded, filterable, progress bars

## Data Files (where to update progress)

| What to edit | File | Notes |
|-------------|------|-------|
| Flight day prep status | `flight-day-prep.ts` (planned) / `flight-day-data.ts` (current) | Checklist status changes |
| Flight day operations | `flight-day-tiers.ts` (planned) / `flight-day-data.ts` (current) | Tier steps, procedures |
| Flight day types | `flight-day-types.ts` (planned) / `flight-day-data.ts` (current) | Shared type definitions |
| WBS tasks | `wbs-data.ts` | status: `"done"` / `"active"` / `"upcoming"` / `"blocked"` |
| SE / team / approaches | `group-project-v2-data.ts` | Levels, SE layers, team roles |
| Hardware inventory | `hardware-data.ts` | Components, connections, specs |
| Mission levels / roadmap | `mission-data.ts` | Level definitions, roadmap steps |
| L2 stepping stones | `mission-data.ts` L2_CRITICAL_PATH | 14 steps, status: done/ready/todo/blocked |
| L2 milestones | `mission-data.ts` L2_MILESTONES | afterRow: 2, 5, 8 |
| L2 parallel tasks | `mission-data.ts` L2_PARALLEL_TASKS | 20 tasks, status: done/ready/todo |
| Hub navigation | `hub-data.ts` | Landing page cards and links |

**Team IDs:** hw (Hardware), cv (CV/Optics), fd (Flight Dynamics), gcs (GCS/UI), pm (Project Manager)

## Workflow (adapted from Orgnaiser BOOTSTRAP.md)

### Context Tiers
| Tier | What | Loaded |
|------|------|--------|
| 0 | `CLAUDE.md` + `.claude/rules/` | Every message |
| 1 | `docs/<module>.md` blueprints | On demand |
| 2 | `brain-dump.md`, source code | Search only |

### Rules
1. Finish tasks before switching — queue new requests, don't abandon
2. Record every user message to `brain-dump.md` (cleaned up, all ideas)
3. Route ideas: feature → `NICE_TO_HAVE.md`, vision → future plans
4. Run post-task doc checklist (`.claude/rules/design.md`) after every change
5. Read blueprint before scanning 1000+ line source files
6. Don't over-engineer — minimum complexity for current task

### Commands
- `/status` — type check + task counts + doc freshness
- `/whats-next` — top priorities from NICE_TO_HAVE.md
- `/wrap-up` — end-of-session checklist

## Future Plans

- [ ] Split `flight-day-data.ts` (1709 lines) into `flight-day-types.ts`, `flight-day-prep.ts`, `flight-day-tiers.ts`
- [ ] Interactive pre-flight checklist tab (with localStorage persistence)
- [ ] Data entry forms for flight day measurements (GPS accuracy, detection altitude, FPS)
- [ ] Post-flight CSV analysis tab (import detection_log.csv, visualize results)
- [ ] Update WBS task statuses to reflect current real progress
- [ ] Add "Live Status" tab (tested vs not, from v3/CLAUDE.md checklist)
- [ ] Add flight test results tab (dates, outcomes, config values)
- [ ] Add team contributions view (who did what, when)
- [ ] Add detection image gallery (from --save-detections output)
- [ ] Make WBS editable in browser (save to localStorage)
- [ ] Timeline/Gantt view of project phases
