# Dashboard Blueprint

> Line-map reference for LLM sessions. Covers every file, every component, every data export.
> Read this INSTEAD of scanning source files. Update when you change the dashboard.

---

## 1. Architecture Overview

**Stack:** React 18.3.1 + TypeScript 5.5.3 + Vite 5.3.4 + Tailwind 3.4.4
**No backend, no database.** All data lives in TypeScript constant files (`*-data.ts`).
**Port:** 5050 (configured in `vite.config.ts`).

### App Shell (`App.tsx`, 100 lines)

```
+------------------------------------------------------------------+
| TopBar (status/team/docs/ref/log toggles, PROJECT_PHASE bar)     |
+------+-------------------------------------------+---------------+
| Left | Tab Content (one page component rendered)  | Right         |
| Side | based on activeTab state                   | Sidebar       |
| bar  |                                            | (Ctrl+R)      |
|(Ctrl |                                            |               |
| +L)  |                                            |               |
+------+-------------------------------------------+---------------+
| Tab Bar: mission | hardware | levels | roadmap | hub | team |    |
|          notes | gp-v2 | wbs                                     |
+------------------------------------------------------------------+
```

**State in App.tsx:**
- `activeTab`: `"mission" | "hardware" | "levels" | "roadmap" | "hub" | "team" | "notes" | "gp-v2" | "wbs"`
- `activePanel`: `"status" | "team" | "docs" | "ref" | "log" | null` (top overlay)
- `showLeft`: boolean (Ctrl+L toggle)
- `showRight`: boolean (Ctrl+R toggle)

**Keyboard shortcuts** (useEffect in App.tsx):
- `Ctrl+L` toggles left sidebar
- `Ctrl+R` toggles right sidebar

### Data Flow

```
*-data.ts (TypeScript constants + types)
    |
    v
Page components (import constants, render with local UI state)
    |
    v
No persistence — refresh resets all UI state
```

To change data: edit the `*-data.ts` file, save, Vite hot-reloads.

---

## 2. File Structure

### Config & Entry (root)

| File | Lines | Purpose |
|------|-------|---------|
| `package.json` | 25 | Dependencies: react 18.3.1, vite 5.3.4, tailwind 3.4.4, typescript 5.5.3 |
| `vite.config.ts` | 7 | Dev server port 5050 |
| `tailwind.config.js` | 6 | Default config, scans `./src/**/*.{js,ts,jsx,tsx}` |
| `tsconfig.json` | 19 | ES2020 target, strict, noUnusedLocals/Params disabled |
| `postcss.config.js` | 6 | tailwindcss + autoprefixer plugins |
| `index.html` | 12 | `<html class="dark">`, body bg zinc-950 |
| `CLAUDE.md` | ~120 | Dashboard project ground truth for LLM sessions |
| `brain-dump.md` | ~67 | Append-only user messages |
| `NICE_TO_HAVE.md` | ~30 | Improvement backlog with impact/effort scoring |

### Source Entry

| File | Lines | Purpose |
|------|-------|---------|
| `src/main.tsx` | 10 | React.StrictMode, renders `<App />` into `#root` |
| `src/index.css` | 16 | Tailwind directives (`@tailwind base/components/utilities`), hidden scrollbars globally |
| `src/App.tsx` | 100 | App shell: tab bar, sidebar toggles, TopBar, TopPanels, routes to page components |

### Data Files

| File | Lines | Purpose |
|------|-------|---------|
| `src/pages/flight-day-data.ts` | 1709 | Flight day phases, tiers, diagnostics, measurements, logging |
| `src/pages/group-project-v2-data.ts` | 1312 | SE layers, levels, team, approaches, risks, emergencies |
| `src/pages/hardware-data.ts` | 539 | 13 hardware components with specs, connections, setup steps |
| `src/pages/mission-data.ts` | 390 | Mission objectives, requirements, hardware, levels, roadmap, flight zones |
| `src/pages/hub-data.ts` | 361 | Project phase, subsystems, flight steps, team, docs, session log |
| `src/pages/wbs-data.ts` | 336 | ~93 WBS nodes (7 subsystems), assignee/level colors |

### Page Components

| File | Lines | Purpose |
|------|-------|---------|
| `src/pages/RoadmapTab.tsx` | 883 | 3 sub-tabs: day1, timeline, steps. Flight day detail view |
| `src/pages/GroupProjectV2Components.tsx` | 586 | 11 shared components for GP v2 tab |
| `src/pages/MissionWBSTab.tsx` | 415 | Recursive WBS tree with filters |
| `src/pages/MissionV2Readiness.tsx` | 346 | Equipment tiers, emergencies, risk heatmap |
| `src/pages/MethodologyV2Sidebar.tsx` | 321 | SE methodology left sidebar (5 sections) |
| `src/pages/TopPanels.tsx` | 294 | 5 overlay panels (status, team, docs, ref, log) |
| `src/pages/LevelsTab.tsx` | 279 | L1/L2/L3 level cards with expandable detail |
| `src/pages/HardwareTab.tsx` | 227 | Hardware grouped by category, expandable cards |
| `src/pages/MissionTab.tsx` | 200 | Mission overview with expandable sections |
| `src/pages/TeamTab.tsx` | 188 | Team member cards, level progress, blockers |
| `src/pages/HubPage.tsx` | 173 | Dashboard home: stats, subsystems, flight progress |
| `src/pages/RightSidebar.tsx` | 146 | Team hub: Members, Comms, Blockers sub-tabs |
| `src/pages/NotesTab.tsx` | 140 | Inline notes array, categorized, status-tagged |
| `src/pages/ContributionV2Matrix.tsx` | 138 | Team x GoalAspect table |
| `src/pages/BigPictureV2View.tsx` | 116 | L1->L2->L3 pathway with bridge items |
| `src/pages/IntegrationV2Oversight.tsx` | 110 | Cross-cutting concerns grid |
| `src/pages/GroupProjectV2Tab.tsx` | 103 | GP v2 page shell: 3-panel layout |
| `src/pages/LeftSidebar.tsx` | 83 | Docs hub, grouped by category |
| `src/pages/TopBar.tsx` | 76 | Panel toggle buttons + PROJECT_PHASE bar |

### Public Assets

| File | Purpose |
|------|---------|
| `public/field-map.jpg` | Fenswood Farm operational area image (used in MissionTab) |

### Claude Config

| File | Purpose |
|------|---------|
| `.claude/rules/design.md` | Always loads: philosophy, quality ratchet, React/Tailwind rules, post-task checklist |
| `.claude/rules/ui.md` | Loads for `src/**`: component architecture, interaction patterns, data update pattern |
| `.claude/commands/status.md` | `/status` command: type check + task counts + doc freshness |
| `.claude/commands/whats-next.md` | `/whats-next` command: top priorities from NICE_TO_HAVE |
| `.claude/commands/wrap-up.md` | `/wrap-up` command: end-of-session checklist |

---

## 3. Each Page/Tab in Detail

### Mission Tab (`MissionTab.tsx`, 200 lines)

**Data:** imports from `mission-data.ts`
**State:** `expanded: Set<string>` (accordion sections)
**Sections:** scenario, requirements (R01-R12), constraints, hardware (12 items), deliverables (D1-D7), success criteria
**Notable:** Embeds `public/field-map.jpg` image. Each requirement has id, text, priority, status.

### Hardware Tab (`HardwareTab.tsx`, 227 lines)

**Data:** imports `HARDWARE_COMPONENTS`, `HARDWARE_CATEGORIES`, `CONNECTIONS` from `hardware-data.ts`
**State:** `expandedId: string | null` (single item expand)
**Layout:** Components grouped by 8 categories (Airframe, Autopilot, Navigation, Compute, Vision, Communication, Power, Software). Each `ComponentCard` expands to show: connection info, specs table, setup steps, test commands, guide links, notes.
**Pattern:** Click card to expand, click again to collapse. Only one card expanded at a time.

### Levels Tab (`LevelsTab.tsx`, 279 lines)

**Data:** imports `LEVELS` from `mission-data.ts`
**State:** `expandedLevel: number | null`
**Layout:** Three level cards (L1 Basic, L2 Standard, L3 Advanced). Each shows droneActions, pilotActions, scripts, whatsWorking, whatsMissing.
**Special:** L2 card has a "Focus Areas" grid (6 areas: CV, Flight Algorithm, HW Integration, Ground Station, Safety, Payload) with color-coded status.

### Roadmap Tab (`RoadmapTab.tsx`, 883 lines) — see Section 5 for full blueprint

**Data:** imports from `flight-day-data.ts` + inline `TIMELINE` constant
**Sub-tabs:** `"day1" | "timeline" | "steps"` (state: `activeView`)
**Most complex tab.** Contains 4 inline components. Full blueprint in Section 5.

### Hub Tab (`HubPage.tsx`, 173 lines)

**Data:** imports from `hub-data.ts`
**Layout:** StatCard grid (4 cards), subsystem status list (13 items with status dots), flight testing progress (5 steps as vertical timeline), system architecture quick view.
**No accordion state.** Static display.

### Team Tab (`TeamTab.tsx`, 188 lines)

**Data:** imports `TEAM`, `LEVELS` from `hub-data.ts`; inline `MEMBER_TASKS` constant
**State:** none (static display)
**Layout:** Level progress bars (L1/L2/L3), team member cards with tasks and blockers, "Next Steps to Unblock" section.
**Special:** `MEMBER_TASKS` is defined inline (not in a data file) — maps member IDs to task arrays with status.

### Notes Tab (`NotesTab.tsx`, 140 lines)

**Data:** inline `NOTES` array (NOT from a data file)
**State:** `filter: string` (category filter)
**Layout:** Filterable grid of note cards. Categories: Dashboard, Flight, CV/Model, Hardware, Team, Docs. Statuses: want, idea, doing, done, fix — each with distinct color.
**To add notes:** edit the `NOTES` array inside `NotesTab.tsx` directly.

### GP v2 Tab (`GroupProjectV2Tab.tsx`, 103 lines)

**Data:** imports from `group-project-v2-data.ts`
**State:** `activeLevel: number` (1-3), `selectedApproachId: string | null`, `showLeftSidebar: boolean`
**Layout:** 3-panel:
- Left (~260px): `MethodologySidebar` — SE methodology sections
- Center: scrollable main content with 13 components stacked vertically
- Right (~220px): `RightSidebar` — compute trade study, team, test legend

**Center content order (top to bottom):**
1. `HolyGrailBanner` — mission statement
2. `BigPictureView` — L1->L2->L3 pathway
3. `LevelSelector` — pick active level
4. `AmbitionPanel` — level detail
5. `EvolutionTracker` — progress indicators
6. `ApproachSelector` — approach options
7. `ApproachDetail` — selected approach detail
8. `ContributionMatrix` — team x goal table
9. `SELayerStack` — 6 SE layers accordion
10. `DroneBlueprintSVG` — SVG schematic (viewBox 680x380)
11. `IntegrationOversight` — cross-cutting concerns
12. `MissionReadiness` — equipment + emergencies + risks
13. `DiagnosticProtocol` — diagnostic steps

### Mission WBS Tab (`MissionWBSTab.tsx`, 415 lines)

**Data:** imports `WBS_TREE`, `ASSIGNEE_COLORS`, `LEVEL_COLORS` from `wbs-data.ts`
**State:** `collapsed: Set<string>`, `selectedId: string | null`, `filterAssignee: string`, `filterLevel: string`
**Layout:** Recursive tree. Each `TreeNode` component renders its children indented. Filter bar at top (assignee dropdown, level dropdown). Expand All / Collapse All buttons.
**Helpers:** `buildChildrenMap(nodes)` groups nodes by parentId. `countStatuses(nodeId, childrenMap)` recursively counts done/active/upcoming/blocked.
**Status colors:** done=green, active=amber, upcoming=zinc-500, blocked=red.
**Legend** at bottom shows all status + assignee colors.

### Top Bar (`TopBar.tsx`, 76 lines)

**Data:** imports `PROJECT_PHASE` from `hub-data.ts`
**Props:** `activePanel`, `setActivePanel`
**Layout:** 5 toggle buttons (Status, Team, Docs, Ref, Log) + PROJECT_PHASE progress bar.
**Click a button** to open/close the corresponding overlay panel.

### Top Panels (`TopPanels.tsx`, 294 lines)

**Data:** imports from `hub-data.ts`
**Props:** `activePanel: string | null`
**5 panels (rendered as overlays on top of main content):**
1. **StatusPanel** (~60 lines): subsystem status list + flight steps progress
2. **TeamPanel** (~50 lines): team member cards + CHAT_DIGEST accordion
3. **DocsPanel** (~60 lines): categorized doc links with sub-tabs (All, Setup, Safety, Flight, System)
4. **RefPanel** (~40 lines): copyable quick reference items (click to copy)
5. **LogPanel** (~50 lines): session log accordion (expandable entries)

### Left Sidebar (`LeftSidebar.tsx`, 83 lines)

**Data:** imports `DOCS` from `hub-data.ts`
**Layout:** Documentation links grouped by category, collapsible sections.
**Toggle:** Ctrl+L in App.tsx

### Right Sidebar (`RightSidebar.tsx`, 146 lines)

**Data:** imports `TEAM` from `hub-data.ts`; inline `MEMBER_TASKS`
**State:** `subTab: "members" | "comms" | "blockers"`
**Layout:** 3 sub-tabs. Members shows team list. Comms shows communication channels. Blockers shows per-member blocking issues.
**Toggle:** Ctrl+R in App.tsx

---

## 4. flight-day-data.ts Blueprint (1709 lines)

### Types (lines 1-77)

| Type | Key Fields |
|------|------------|
| `FlightStep` | id, phase, title, description, duration?, status, detailedSteps?, expectedOutput?, notes?, goNoGo? |
| `FlightPhase` | id, name, color |
| `GoNoGo` | criteria, threshold, actual?, passed? |
| `FlightTier` | id, name, color, description, steps: FlightStep[] |
| `PrepTask` | id, category, task, status, notes?, priority |
| `DiagnosticCheck` | id, system, check, command?, expected, status |
| `Measurement` | id, test, metric, expected, actual?, unit, notes? |
| `LogRequirement` | id, category, item, format, when, notes? |

### Exported Constants

| Export | Lines | Description |
|--------|-------|-------------|
| `PRE_FLIGHT_PREP` | 79-180 | `PrepTask[]` — pre-flight preparation checklist (~30 tasks in categories: code, hardware, logistics, safety) |
| `PREFLIGHT_DIAGNOSTICS` | 182-363 | `DiagnosticCheck[]` — 40+ system checks (Pi, camera, Cube, GPS, RC, model, mavproxy, GCS, safety) |
| `TIER_1` | 365-835 | `FlightTier` — "Must Complete" tier with ~15 steps (MP waypoints, passive CV, GPS test, etc.). Each step has detailedSteps array with sub-step instructions. |
| `TIER_2` | 837-1238 | `FlightTier` — "Should Complete" tier (~12 steps: autonomous search, CV dashboard, guided waypoints, etc.) |
| `TIER_3` | 1240-1497 | `FlightTier` — "Nice to Have" tier (~8 steps: descent test, full autonomous, multi-pass, etc.) |
| `TIME_SLOTS` | 1499-1519 | `Array<{slot, activity, duration, tier, notes}>` — flight day schedule |
| `WORST_CASES` | 1521-1537 | `Array<{scenario, response, fallback}>` — contingency plans |
| `CONFIG_UPDATES` | 1539-1551 | `Array<{parameter, currentValue, updateFrom, notes}>` — config values to tune |
| `FILES_TO_COLLECT` | 1553-1573 | `Array<{file, location, contains, priority}>` — files to collect post-flight |
| `MEASUREMENTS` | 1575-1670 | `Measurement[]` — 20+ measurements to record (GPS accuracy, detection altitude, inference speed, etc.) |
| `LOGGING_REQUIREMENTS` | 1672-1709 | `LogRequirement[]` — what to log, format, when |

### Data Patterns

- **FlightStep.detailedSteps**: Array of `{step, details, duration?}` — provides expand-on-click drill-down. Most steps have 5-15 detailed sub-steps.
- **FlightStep.expectedOutput**: String describing what success looks like — shown in green when expanded.
- **FlightStep.goNoGo**: Array of `{criteria, threshold, actual?, passed?}` — go/no-go gate items.
- **Status values**: `"not-started" | "ready" | "in-progress" | "done" | "blocked"`
- **Tier colors**: TIER_1 green, TIER_2 blue, TIER_3 purple

---

## 5. RoadmapTab.tsx Blueprint (883 lines)

### State (line ~30)

```typescript
activeView: "day1" | "timeline" | "steps"  // sub-tab selector
```

### Inline Data (lines ~35-145)

`TIMELINE: TimelinePhase[]` — defined inline, NOT in a data file. ~8 phases with id, name, dateRange, status, items array. Special: `phase.id === "day1"` triggers embedded `FlightDay1View`.

### Component Hierarchy

```
RoadmapTab (line ~30)
├── Sub-tab bar: day1 | timeline | steps
├── if "day1":  <FlightDay1View />
├── if "timeline": <TimelineView />
└── if "steps":  <StepsView />
```

### FlightDay1View (lines ~150-435)

**The most complex component in the dashboard.**

**State:**
- `expandedPrep: Set<string>` — prep task accordion
- `expandedDiag: Set<string>` — diagnostics accordion
- `expandedMeasurements: Set<string>` — measurements accordion
- `expandedTiers: Set<string>` — tier step accordion
- `expandedGates: Set<string>` — go/no-go gates accordion
- `expandedWorst: Set<string>` — worst-case accordion
- `expandedConfig: Set<string>` — config updates accordion
- `expandedFiles: Set<string>` — files-to-collect accordion
- `expandedLogging: Set<string>` — logging requirements accordion

**Sections rendered (top to bottom):**
1. **Pre-Flight Prep** — `PRE_FLIGHT_PREP` grouped by category, expandable tasks
2. **Pre-Flight Diagnostics** — `PREFLIGHT_DIAGNOSTICS` via `DiagnosticsTable` component
3. **Tier columns** (3-column grid) — `TIER_1`, `TIER_2`, `TIER_3` via `TierColumn` component
4. **Time Slots** — `TIME_SLOTS` as simple table
5. **Go/No-Go Gates** — extracted from tier steps that have `.goNoGo` arrays
6. **Worst Case Scenarios** — `WORST_CASES` expandable list
7. **Config Updates** — `CONFIG_UPDATES` table
8. **Files to Collect** — `FILES_TO_COLLECT` table
9. **Measurements** — `MEASUREMENTS` via `MeasurementsGrid` component
10. **Logging Requirements** — `LOGGING_REQUIREMENTS` grouped by category

### DiagnosticsTable (lines 441-479)

**Props:** `checks: DiagnosticCheck[]`, `expanded: Set<string>`, `toggle: (id) => void`
**Layout:** Table with system, check, command (monospace), expected, status badge. Click row to expand (shows command + expected in detail).

### MeasurementsGrid (lines 492-527)

**Props:** `measurements: Measurement[]`, `expanded: Set<string>`, `toggle: (id) => void`
**Layout:** Grid cards. Each shows test name, metric, expected value, actual (if set), unit. Click to expand notes.

### TierColumn (lines 533-611)

**Props:** `tier: FlightTier`, `expanded: Set<string>`, `toggle: (id) => void`
**Layout:** Column header (tier name, color bar, description), then list of `StepCard` components.
**Color:** Uses `tier.color` for header bar and accent.

### StepCard (lines 613-700)

**Props:** `step: FlightStep`, `isExpanded: boolean`, `onToggle: () => void`
**Layout:** Collapsed: title + status badge + duration. Expanded: description, detailedSteps (numbered list), expectedOutput (green box), goNoGo items (pass/fail badges), notes.
**Status badge colors:** done=green, in-progress=amber, ready=blue, not-started=zinc, blocked=red.

### TimelineView (lines 706-816)

**Props:** none (uses inline `TIMELINE` data)
**State:** `expandedPhases: Set<string>`
**Layout:** Vertical timeline with colored dots. Each phase: name, dateRange, status, expandable items list.
**Special case:** When `phase.id === "day1"`, renders `<FlightDay1View />` inline instead of simple item list.

### StepsView (lines 822-883)

**Props:** none
**Data:** imports `ROADMAP` from `mission-data.ts`
**Layout:** Roadmap steps grouped by level (L1, L2, L3). Each step shows title, description, dependencies, status. Simple list, no accordion.

---

## 6. Data Update Guide

### Update task status (WBS)

**File:** `src/pages/wbs-data.ts`
**Find:** the node by `id` or `label` in the `WBS_TREE` array
**Change:** `status` field to `"done" | "active" | "upcoming" | "blocked"`

```typescript
// Example: mark task as done
{ id: "1.2.3", wbs: "1.2.3", label: "Test camera", ..., status: "done" },
```

### Update hardware component

**File:** `src/pages/hardware-data.ts`
**Find:** component by `id` in `HARDWARE_COMPONENTS` array
**Fields:** name, category, role, description, status (`"tested" | "connected" | "ready" | "missing"`), connectsTo, connectionDetails, setupSteps, guides (with URL), specs (key-value), testCommands, notes

### Update flight day step status

**File:** `src/pages/flight-day-data.ts`
**Find:** step by `id` in `TIER_1.steps`, `TIER_2.steps`, or `TIER_3.steps`
**Change:** `status` to `"done" | "in-progress" | "ready" | "not-started" | "blocked"`
**Optional:** set `goNoGo[].actual` and `goNoGo[].passed` after real testing

### Update measurement actual values

**File:** `src/pages/flight-day-data.ts`
**Find:** measurement by `id` in `MEASUREMENTS` array
**Change:** set `actual` field to recorded value string

### Update mission levels

**File:** `src/pages/mission-data.ts`
**Find:** level in `LEVELS` array (index 0=L1, 1=L2, 2=L3)
**Change:** `whatsWorking`, `whatsMissing` arrays; `droneActions`, `pilotActions`, `scripts`

### Update SE layers / approaches / team

**File:** `src/pages/group-project-v2-data.ts`
**Exports to look for:**
- `TEAM` (line 180) — team member details
- `SE_LAYERS` (line 197) — 6 SE layers
- `LEVELS` (line 295) — 3 ambition levels (~637 lines of data)
- `SE_METHODOLOGY` (line 978) — methods list
- `DECISION_TREE` (line 1001) — decision nodes
- `MISSION_RISKS` (line 1275) — risk items with likelihood/impact scores

### Update project phase / subsystems

**File:** `src/pages/hub-data.ts`
**Exports:**
- `PROJECT_PHASE` — overall project progress
- `SUBSYSTEMS` (13 items) — status of each subsystem
- `FLIGHT_STEPS` (5 items) — progressive flight test status
- `DOCS` (20 entries) — documentation links
- `SESSION_LOG` (10 entries) — session history

### Add notes

**File:** `src/pages/NotesTab.tsx` (inline `NOTES` array, NOT a data file)
**Add:** new object to the `NOTES` array with `{id, category, text, status, date?}`

### Add a new data source

1. Create `src/pages/new-thing-data.ts` with exported constants and TypeScript types
2. Import in the page component that uses it
3. Update this blueprint with the new file

---

## 7. Design Conventions

### Color System

| Meaning | Color | Tailwind |
|---------|-------|----------|
| Done / success | Green | `text-green-400`, `bg-green-500/10`, `border-green-500/30` |
| Active / warning | Amber | `text-amber-400`, `bg-amber-500/10`, `border-amber-500/30` |
| Blocked / urgent | Red | `text-red-400`, `bg-red-500/10`, `border-red-500/30` |
| Strategic / stretch | Purple | `text-purple-400`, `bg-purple-500/10` |
| Info / reference | Cyan | `text-cyan-400`, `bg-cyan-500/10` |
| Neutral / upcoming | Zinc-500 | `text-zinc-500`, `bg-zinc-800` |

### Tier Colors

| Tier | Color | Usage |
|------|-------|-------|
| T1 (Must) | Green | `border-green-500`, `text-green-400` |
| T2 (Should) | Blue | `border-blue-500`, `text-blue-400` |
| T3 (Nice) | Purple | `border-purple-500`, `text-purple-400` |

### Assignee Colors (WBS)

| ID | Role | Color |
|----|------|-------|
| hw | Hardware | Orange |
| cv | CV/Optics | Purple |
| fd | Flight Dynamics | Cyan |
| gcs | GCS/UI | Green |
| pm | Project Manager | Yellow |

### Typography

- **Dense information display**: text sizes 6px to 14px
- Default body: `text-[11px]` or `text-xs` (12px)
- Headers: `text-sm` (14px) or `text-[13px]`
- Fine print / labels: `text-[8px]` to `text-[10px]`
- Monospace for commands/code: `font-mono`

### Theme

- Background: `bg-zinc-950` (page), `bg-zinc-900` (cards), `bg-zinc-800` (nested)
- Text: `text-zinc-100` (primary), `text-zinc-400` (secondary), `text-zinc-500` (muted)
- Borders: `border-zinc-700/20` to `border-zinc-700/40`
- Opacity layering: `text-zinc-500/40`, `bg-zinc-800/50`

### Spacing

- Compact by default: `gap-1`, `p-2`, `space-y-1`
- Cards: `p-2` to `p-3`, `rounded-lg`
- Sections: `space-y-3` to `space-y-4`

### UI Patterns

**Set-based accordion (most common):**
```typescript
const [expanded, setExpanded] = useState<Set<string>>(new Set());
const toggle = (id: string) => {
  setExpanded(prev => {
    const next = new Set(prev);
    next.has(id) ? next.delete(id) : next.add(id);
    return next;
  });
};
```
Used in: FlightDay1View (9 separate sets), TimelineView, SELayerStack, MethodologyV2Sidebar, MissionTab, TopPanels (LogPanel).

**Single-item expand:**
```typescript
const [expandedId, setExpandedId] = useState<string | null>(null);
const toggle = (id: string) => setExpandedId(prev => prev === id ? null : id);
```
Used in: HardwareTab, LevelsTab.

**Hover/focus states:** All interactive elements must have `hover:bg-zinc-700/30` or similar + `cursor-pointer` on clickable non-button elements.

**Tailwind conventions:**
- Arbitrary values: `z-[45]` not `z-45`
- Opacity on colors: `text-zinc-500/40`, `border-zinc-700/20`
- Conditional classes: template literals or ternary, no classnames library

### Component Extraction Rule

Extract a component when a file exceeds ~500 lines. Current extractions:
- `GroupProjectV2Tab.tsx` (103) -> `GroupProjectV2Components.tsx` (586) + `MethodologyV2Sidebar.tsx` (321) + `BigPictureV2View.tsx` (116) + `ContributionV2Matrix.tsx` (138) + `IntegrationV2Oversight.tsx` (110) + `MissionV2Readiness.tsx` (346)
- `RoadmapTab.tsx` (883) has inline components (DiagnosticsTable, MeasurementsGrid, TierColumn, StepCard) — candidates for extraction if it grows further

### React Rules

- All hooks at top level -- NEVER inside conditionals, loops, or after early returns
- JSON.parse() always in try-catch with fallback
- Prefer pure data files (TypeScript constants) over API calls
- Type imports from shared data files, avoid `any`
