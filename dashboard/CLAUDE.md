# SAR Drone Dashboard

## What This Is

Standalone React web app that visualizes the SAR drone group project's:
- **Systems engineering strategy** (SE layers, ambition levels, approaches, team roles)
- **Work breakdown structure** (~90 tasks, assignees, progress tracking)

Lives inside v3/ but is completely independent — its own node_modules, own Vite server.
Does NOT interfere with the Python drone code at all.

## Origin

Copied from the Orgnaiser project (`../Orgnaiser/client/src/pages/trade-study-lab/`).
The original has 15+ tabs for a volcanic drone assignment; we only took the last 3 tabs
that are specific to the SAR group project (GP v2, Mission WBS).

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
└── src/
    ├── main.tsx, App.tsx, index.css
    └── pages/
        ├── GroupProjectV2Tab.tsx         ← GP v2 page (3-panel, 103 lines)
        ├── GroupProjectV2Components.tsx  ← 11 UI components (587 lines)
        ├── group-project-v2-data.ts     ← ALL data: levels, team, SE (1312 lines)
        ├── MethodologyV2Sidebar.tsx      ← Left sidebar (322 lines)
        ├── BigPictureV2View.tsx          ← Level pathway L1→L2→L3 (117 lines)
        ├── ContributionV2Matrix.tsx      ← Team × goal matrix (139 lines)
        ├── IntegrationV2Oversight.tsx    ← Cross-cutting concerns (111 lines)
        ├── MissionV2Readiness.tsx        ← Equipment, emergencies, risks (347 lines)
        ├── MissionWBSTab.tsx             ← WBS tree + filtering (415 lines)
        └── wbs-data.ts                  ← 93 WBS nodes (337 lines)
```

## Data Files (where to update progress)

**Task status:** Edit `src/pages/wbs-data.ts` — status: `"done"` | `"active"` | `"upcoming"` | `"blocked"`
**Team/SE/approaches:** Edit `src/pages/group-project-v2-data.ts`
**Team IDs:** hw (Hardware), cv (CV/Optics), fd (Flight Dynamics), gcs (GCS/UI), pm (Project Manager)

## Tabs

1. **GP v2 (Snapshot)** — SE overview: Holy Grail, 3 ambition levels, 6 SE layers, approaches, contribution matrix, integration, readiness
2. **Mission WBS** — ~90 tasks in collapsible tree, color-coded, filterable, progress bars

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

- [ ] Update WBS task statuses to reflect current real progress
- [ ] Add "Live Status" tab (tested vs not, from v3/CLAUDE.md checklist)
- [ ] Add flight test results tab (dates, outcomes, config values)
- [ ] Add team contributions view (who did what, when)
- [ ] Add detection image gallery (from --save-detections output)
- [ ] Make WBS editable in browser (save to localStorage)
- [ ] Timeline/Gantt view of project phases
