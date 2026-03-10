# Flight Features Plan

> New dashboard tabs to support all phases of flight day: pre-flight, in-flight, post-flight.
> Written 2026-03-09. Target: implement before next flight day.

---

## Current Dashboard State

The dashboard is a React 18 + TypeScript + Vite + Tailwind app at `v3/dashboard/`.
All data lives in TypeScript constants (no backend, no database). Tabs:

- **Mission** — scenario, requirements, constraints
- **Hardware** — components, connections, setup
- **Levels** — L1/L2/L3 product levels
- **Roadmap** — Flight Day 1 tiers, timeline, technical steps (uses `flight-day-data.ts`)
- **Hub** — subsystem status, flight testing progress, architecture
- **Team** — assignments and blockers
- **Notes** — ideas and plans
- **GP v2** — systems engineering strategy overview
- **Mission WBS** — 90 tasks with progress tracking

Key existing data file: `flight-day-data.ts` (~1300 lines) already contains:
- `PRE_FLIGHT_PREP` (P1-P14 tasks with detailed notes)
- `PREFLIGHT_DIAGNOSTICS` (D1-D14 with troubleshooting trees)
- `TIER_1`, `TIER_2`, `TIER_3` (flight tiers with phases, steps, contingencies)
- `MEASUREMENTS`, `CONFIG_UPDATES`, `FILES_TO_COLLECT`, `LOGGING_REQUIREMENTS`
- `TIME_SLOTS`, `WORST_CASES`

---

## Feature 1: Pre-Flight Checklist Tab (Interactive)

**Priority:** MUST-HAVE — this replaces the printed checklist and tracks real-time readiness.

**Complexity:** M (medium) — mostly rendering existing data with localStorage state.

**Data source:** `flight-day-data.ts` (`PRE_FLIGHT_PREP`, `PREFLIGHT_DIAGNOSTICS`)

### What It Does

An interactive checklist that the team works through on flight day morning. Each item
is checkable, state persists in localStorage, and a progress bar shows overall readiness.
Replaces the printable `FLIGHT_DAY_CHECKLIST.md` with a live, stateful version.

### Component Structure

```
PreFlightTab.tsx (~400 lines)
  ├── ReadinessBar         — top banner: X/28 complete, % bar, estimated time remaining
  ├── PrepSection          — P1-P14 tasks, each expandable with full notes/commands
  │   └── PrepTaskCard     — checkbox + task + owner + expand for detailed steps
  ├── DiagnosticsSection   — D1-D14 checks, severity-colored, expandable troubleshoot trees
  │   └── DiagnosticCard   — checkbox + system + severity badge + expand for fail steps
  ├── TimerWidget          — stopwatch per tier (start when tier begins, auto-records duration)
  └── PrintButton          — window.print() with @media print CSS (clean, no chrome)
```

### localStorage Schema

```typescript
interface ChecklistState {
  date: string;              // ISO date — auto-reset if different day
  prep: Record<string, boolean>;    // { "P1": true, "P2": false, ... }
  diag: Record<string, boolean>;    // { "D1": true, "D2": false, ... }
  tierTimers: {
    tier1Start?: number;     // Date.now() when started
    tier1End?: number;
    tier2Start?: number;
    tier2End?: number;
    tier3Start?: number;
    tier3End?: number;
  };
  notes: Record<string, string>;    // per-item notes entered on the day
}
```

Key: `sar-checklist-state`. Auto-resets when date changes (fresh checklist each flight day).
Manual "Reset All" button with confirmation dialog.

### Behavior Details

- **Progress bar:** `(checkedPrep + checkedDiag) / (totalPrep + totalDiag) * 100`
  Color: red <50%, amber 50-80%, green >80%.
- **Severity filtering:** toggle to show only "blocking" diagnostics (the must-fix items).
- **Command copy:** click icon next to any `command` field to copy to clipboard.
- **Expand/collapse all:** button to expand or collapse all task details at once.
- **Owner filter:** show only tasks for a specific team member (dropdown: Dima, Robin, Pilot, All).
- **Timer per tier:** simple stopwatch — press "Start Tier 1" when beginning field setup.
  Records wall-clock duration. Useful for report (how long each phase took).
- **Print mode:** `@media print` hides chrome, shows all items expanded, includes check marks.

### Implementation Notes

- Wrap `JSON.parse(localStorage.getItem(...))` in try-catch with fallback to empty state.
- All hooks at top level (React rule). State is a single `useState<ChecklistState>`.
- No new npm dependencies needed.
- Reuse existing color conventions: green=done, amber=warning, red=blocking.

---

## Feature 2: Flight Day Data Entry (In-Flight / Post-Flight)

**Priority:** MUST-HAVE — without this, measurements are in a notebook and never digitized.

**Complexity:** M (medium) — forms with localStorage persistence + structured data types.

**Data source:** New data file `flight-entry-data.ts` (form schemas), stored in localStorage.

### What It Does

Structured forms to record altitude ladder results, speed tests, GPS measurements, landing
accuracy, and general flight notes. Auto-timestamps every entry. Can be filled in the field
on a phone/tablet browser or on the laptop between flights.

### Component Structure

```
DataEntryTab.tsx (~500 lines)
  ├── FlightSelector       — dropdown: which flight # and tier (auto-creates new)
  ├── AltitudeLadderForm   — table: altitude → detected? → confidence → notes
  ├── SpeedTestForm        — table: speed → detected? → confidence → blur rating → notes
  ├── LandingForm          — dummy GPS, estimated GPS, actual landing GPS, measured distance
  ├── ModelComparisonForm  — model name → altitude → detected? → confidence → FPS
  ├── WaypointAccuracyForm — waypoint # → target GPS → actual GPS → error
  ├── GeneralNotesForm     — freetext: weather, wind, issues, observations
  └── ExportButton         — download all entries as JSON or CSV
```

### Data Model

```typescript
interface FlightEntry {
  id: string;               // auto-generated UUID
  flightNumber: number;
  tier: "tier1" | "tier2" | "tier3";
  timestamp: string;        // ISO datetime, auto-filled
  weather?: string;
  wind?: string;
  battery?: string;
  model?: string;           // which .tflite was active
  altitudeLadder: {
    altitude: number;       // 10, 15, 20, 25, 30
    detected: boolean;
    confidence?: number;
    notes?: string;
  }[];
  speedTests: {
    speed: number;          // m/s
    detected: boolean;
    confidence?: number;
    motionBlur: "none" | "mild" | "bad";
    notes?: string;
  }[];
  landings: {
    dummyGPS: { lat: number; lon: number };
    estimatedGPS: { lat: number; lon: number };
    landingGPS: { lat: number; lon: number };
    measuredDistance: number;  // metres, tape measure
    notes?: string;
  }[];
  waypointAccuracy: {
    waypointNum: number;
    targetGPS: { lat: number; lon: number };
    actualGPS: { lat: number; lon: number };
    errorM: number;
  }[];
  generalNotes: string;
}
```

localStorage key: `sar-flight-entries`. Array of `FlightEntry` objects.

### Behavior Details

- **Auto-timestamp:** every form section gets `new Date().toISOString()` when first edited.
- **Pre-filled altitude rows:** 10m, 15m, 20m, 25m, 30m (from `MEASUREMENTS` in flight-day-data).
- **Pre-filled speed rows:** 3, 5, 7, 10 m/s.
- **GPS input:** two formats accepted — paste "51.423412, -2.671414" or separate lat/lon fields.
- **Error auto-calc:** if target + actual GPS both entered, distance error calculated automatically
  using Haversine formula (copy from `utils.py` GeoTransformer logic, trivial in TS).
- **Export:** JSON download for programmatic analysis, CSV download for Excel/report.
- **Flight selector:** dropdown to switch between flights. "New Flight" button increments number.

### Stretch Goal: Pi CSV Connection

If on the same network as the Pi, a "Fetch Pi Log" button could:
1. `fetch('http://PI_IP:8090/api/log')` — if pi_flight.py exposes an endpoint
2. Or user manually uploads the CSV (more reliable, less coupling)

Recommendation: **manual upload** for v1 (Feature 3 handles CSV parsing). The Pi scripts
don't currently expose a log download API, and adding one adds complexity to flight-critical code.

### Implementation Notes

- Pure client-side, localStorage only. No backend needed.
- Haversine distance function: ~10 lines of TypeScript, put in a shared `geo-utils.ts`.
- GPS parsing helper: accept "lat, lon" string or separate fields.
- Form validation: confidence 0.0-1.0, altitude >0, speed >0.
- New data file: `flight-entry-data.ts` for form field definitions and defaults.

---

## Feature 3: Post-Flight Analysis Tab

**Priority:** MUST-HAVE for report, NICE-TO-HAVE timing (can be built after flight day
since it processes data that doesn't exist yet).

**Complexity:** L (large) — CSV parsing, chart rendering, statistical calculations.

**Data source:** Uploaded CSV from `passive_flight_log.csv`, uploaded detection images,
and `FlightEntry` data from Feature 2's localStorage.

### What It Does

Upload the CSV log from `pi_passive_flight.py`, parse it, and generate charts and statistics
for the university report. Also displays detection images for manual review (true/false positive
classification).

### Component Structure

```
AnalysisTab.tsx (~600 lines)
  ├── CSVUploader          — drag-and-drop or file picker, parses CSV on load
  ├── FlightSummaryCard    — duration, total frames, detection count, avg confidence
  ├── DetectionVsAltitude  — scatter/bar chart: detection rate at each altitude band
  ├── ConfidenceHistogram  — histogram of confidence values for all detections
  ├── TimelineChart        — detection events plotted over flight time
  ├── GPSTrackMap          — 2D scatter of drone GPS positions + detection positions
  ├── SpeedVsDetection     — scatter: groundspeed vs confidence (motion blur analysis)
  ├── ImageReview          — upload detection images, classify as true/false positive
  ├── ConfigRecommendations— based on data, suggest config.py updates
  └── ExportReport         — download summary as formatted text/HTML for report
```

### CSV Format (from pi_passive_flight.py)

```
time, flight_sec, lat, lon, alt_m, yaw, pitch, roll, groundspeed,
detection, confidence, pixel_x, pixel_y, guidance, dummy_expected_px,
battery_v, battery_pct
```

17 columns. Detection rows have `detection="YES"`, non-detection rows have `detection="no"`.
Rows are logged every detection + once per second for telemetry.

### Chart Rendering

**No new npm dependencies for v1.** Use inline SVG or HTML canvas.

All charts are simple enough to render with:
- **Bar charts:** CSS flexbox with percentage-width divs (Tailwind).
- **Scatter plots:** `<svg>` with `<circle>` elements, scaled to container.
- **Histograms:** same as bar charts with binned data.

If charts need to be fancier for the report, add `recharts` (lightweight, React-native)
as a single dependency. But try without first.

### Analysis Calculations

```typescript
// Detection rate by altitude band
function detectionRateByAltitude(rows: CSVRow[]): { altitude: string; rate: number; count: number }[]
// Bin into 5m bands: 0-10, 10-15, 15-20, 20-25, 25-30, 30+
// rate = detections / total frames in that altitude band

// Confidence statistics
function confidenceStats(detections: CSVRow[]): { mean: number; median: number; std: number; min: number; max: number }

// Speed vs detection
function speedVsDetection(rows: CSVRow[]): { speed: number; detected: boolean; confidence: number }[]

// GPS estimation accuracy (if we have both estimated and actual dummy GPS)
function gpsAccuracy(entries: FlightEntry[]): { estimateError: number; landingError: number }[]
```

### Config Recommendations Engine

Based on the analysis, generate actionable recommendations:

```
IF max_reliable_altitude < 25m:
  → "Recommend TARGET_ALT = {max_reliable_alt - 5}m (currently 30m)"

IF detection_rate drops significantly above speed X:
  → "Recommend SEARCH_SPEED_MPS = {X - 1} (currently 5)"

IF average_confidence < 0.5:
  → "Consider lowering CONFIDENCE_THRESHOLD from 0.4 to 0.25"
  → "Consider retraining model with real flight images"

IF false_positive_rate > 20%:
  → "Raise CONFIDENCE_THRESHOLD from 0.4 to 0.6"
```

Output as a list of `{ parameter: string, current: string, recommended: string, reason: string }`.

### Image Review Panel

- Drag-and-drop folder of detection images (from `detections/` on Pi).
- Display in a grid, click to enlarge.
- Two buttons per image: "True Positive" (green) / "False Positive" (red).
- Calculates: precision = TP / (TP + FP).
- State in localStorage: `sar-image-classifications`.

### Implementation Notes

- CSV parsing: split by newlines, split by commas, map to typed objects. ~30 lines.
  Wrap in try-catch — malformed CSVs should show an error, not crash.
- File upload: `<input type="file" accept=".csv" />` with FileReader API.
- Image upload: `<input type="file" multiple accept="image/*" />` with URL.createObjectURL.
- Charts: start with pure SVG. Add recharts only if SVG is too limiting.
- All calculations are pure functions — easy to test.

---

## Feature 4: Auto-Logging Documentation

**Priority:** MUST-HAVE (documentation, not code) — team needs to know what's automatic
vs manual BEFORE flight day.

**Complexity:** S (small) — add a section to the dashboard as an info panel, or as a
dedicated sub-view within an existing tab.

### Where It Lives

Two options:
1. **Info panel in the Roadmap tab** (under Flight Day 1 view) — most discoverable.
2. **Collapsible section at the top of the Data Entry tab** — right where you need it.

Recommendation: **Option 2** — put it in the Data Entry tab as a permanent reference header.

### Content (rendered as a styled info card)

#### What pi_passive_flight.py Logs Automatically

| Output | Location | Content | Flags Needed |
|--------|----------|---------|--------------|
| CSV log | `passive_flight_log.csv` | 17 columns: time, flight_sec, lat, lon, alt_m, yaw, pitch, roll, groundspeed, detection, confidence, pixel_x, pixel_y, guidance, dummy_expected_px, battery_v, battery_pct | Always (default) |
| Detection images | `detections/` | Full frame with bbox drawn, filename = `YYYYMMDD_HHMMSS_lat_lon_conf.jpg` | `--save-detections` |
| Raw frames | `flight_frames/` | Every Nth frame, filename = `DET_conf_alt_spd_frame#.jpg` or `MISS_alt_spd_frame#.jpg` | `--save-frames --save-every N` |
| MJPEG stream | `http://PI_IP:8090/stream` | Live video with detection overlay | `--stream` |

**Recommended command for flight day:**
```
python tests2/pi_passive_flight.py --headless --stream --save-detections --save-frames --save-every 4
```

#### What pi_flight.py Logs

| Output | Location | Content |
|--------|----------|---------|
| Web dashboard | `http://PI_IP:8090` | Live video + GPS grid + detection clusters + commands |
| Operator commands | Terminal output | All N/Y/I/X/L commands with timestamps |
| Detection clusters | In-memory | GPS estimates, cluster IDs, classification results |

Note: pi_flight.py does NOT currently write a CSV log file. Detection data is displayed
live in the browser but not persisted to disk. **This is a gap** — either:
- Use pi_passive_flight.py for data collection (zero commands, safe)
- Or add CSV logging to pi_flight.py (future enhancement)

#### What Mission Planner Records

| Output | Location | Content |
|--------|----------|---------|
| Telemetry log | `*.tlog` in MP logs folder | Full MAVLink stream: GPS, attitude, battery, mode changes, every message |
| KMZ flight path | Exportable from MP | GPS track viewable in Google Earth |
| Messages log | MP Messages tab | Pre-arm failures, mode changes, errors, warnings |

#### What Must Be Recorded MANUALLY

| Data | Tool | Why Not Automatic |
|------|------|-------------------|
| Landing distance to dummy | Tape measure + notebook / Data Entry tab | Physical measurement, drone doesn't know |
| Weather conditions | Notebook / Data Entry tab | No weather sensor on drone |
| Which model was active | Notebook / Data Entry tab | Filename of best.tflite at time of flight |
| Altitude ladder results | Notebook / Data Entry tab | Requires hovering at set altitudes, reading terminal |
| Speed test results | Notebook / Data Entry tab | Requires flying at set speeds, reading terminal |
| Waypoint accuracy | Mission Planner map + notebook | Read actual position from MP, compare to target |
| Team observations | Notebook / Data Entry tab | Qualitative notes, things noticed during flight |

#### Post-Flight Data Processing Pipeline

```
1. COLLECT (on Pi, immediately after landing):
   scp pi@PI_IP:~/dima/Group_Proj/passive_flight_log.csv ./flight_data/
   scp -r pi@PI_IP:~/dima/Group_Proj/detections/ ./flight_data/detections/
   scp -r pi@PI_IP:~/dima/Group_Proj/flight_frames/ ./flight_data/frames/

2. ANALYZE (on laptop, same day or next):
   → Upload CSV to Post-Flight Analysis tab (Feature 3)
   → Upload detection images for T/F positive review
   → Enter manual measurements in Data Entry tab (Feature 2)

3. CALCULATE (automatic in Analysis tab):
   → Detection rate vs altitude
   → Confidence distribution
   → Speed vs detection quality
   → GPS estimation accuracy (if landing measurements entered)
   → Config update recommendations

4. UPDATE (before next flight):
   → Apply recommended config.py changes
   → Retrain model if false positive rate high (use saved frames as training data)
   → Update dashboard WBS task statuses

5. REPORT (for university submission):
   → Export charts from Analysis tab
   → Export data tables from Data Entry tab
   → Screenshots of dashboard state
   → Include raw CSV + images as appendix
```

### Implementation

This is a static info card — no interactivity needed. Render as a styled `<div>` with
tables and code blocks. Use the existing dark theme zinc color palette.

Could be a collapsible `<details>` element or always-visible reference panel.

---

## Implementation Priority Order

| Order | Feature | Priority | Complexity | Effort | Value on Flight Day |
|-------|---------|----------|------------|--------|---------------------|
| 1 | Pre-Flight Checklist | Must-have | M | 3-4 hrs | HIGH — replaces paper, tracks readiness live |
| 2 | Data Entry Forms | Must-have | M | 3-4 hrs | HIGH — structured recording beats scribbled notes |
| 3 | Logging Documentation | Must-have | S | 1 hr | HIGH — team knows what to collect and how |
| 4 | Post-Flight Analysis | Must-have (for report) | L | 5-8 hrs | MEDIUM now, HIGH after flight day |

**Recommended approach:** Build features 1-3 before flight day (7-9 hours total).
Build feature 4 after flight day when real data exists to test against.

---

## New Files to Create

```
src/pages/
  PreFlightTab.tsx          — Feature 1: interactive checklist
  DataEntryTab.tsx          — Feature 2: flight data entry forms
  AnalysisTab.tsx           — Feature 4: post-flight CSV analysis + charts
  flight-entry-data.ts      — Feature 2: form field definitions, defaults, types
  geo-utils.ts              — Shared: Haversine distance, GPS parsing helpers
  logging-info.ts           — Feature 3: auto-logging documentation content as TS constants
```

Files to modify:
```
App.tsx                     — Add 3 new tabs to TABS array and render switches
flight-day-data.ts          — No changes needed (already has all pre-flight data)
```

No new npm dependencies for the initial implementation. Consider `recharts` later
if SVG charts are insufficient for the report.

---

## Tab Organization (After Implementation)

Current + new tabs, logically grouped:

```
Planning:     Mission | Hardware | Levels | Roadmap | Hub | Team | Notes
Engineering:  GP v2 | Mission WBS
Flight Ops:   Pre-Flight | Data Entry | Analysis
```

Consider adding a visual separator or tab group labels in the tab bar to distinguish
these three categories. A simple `|` divider or subtle background color shift works.

---

## Open Questions

1. **Phone/tablet layout?** The Data Entry tab would ideally work on a phone in the field.
   Current dashboard is desktop-optimized. Adding `sm:` responsive breakpoints to the
   Data Entry forms specifically would help. Not needed for other tabs.

2. **Data persistence beyond localStorage?** If localStorage is cleared or browser changes,
   all flight day data is lost. Options:
   - Export to JSON file after each flight (Feature 2 ExportButton — already planned)
   - Use IndexedDB for larger data (detection images)
   - Keep it simple: localStorage + export button is sufficient for a uni project

3. **Recharts dependency?** Adding recharts (~150KB gzipped) gives much nicer charts
   for the report. Worth it if Feature 4 is built. Not needed for Features 1-3.
