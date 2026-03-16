/**
 * Hub Data — Central project data for the SAR Drone Dashboard
 *
 * All project status, team, docs, session log, quick reference.
 * Edit this file to update the hub page.
 */

// ═══════════════════════════════════════════════════════════
// Types
// ═══════════════════════════════════════════════════════════

export type SubsystemStatus = "done" | "working" | "partial" | "todo" | "blocked";

export interface Subsystem {
  id: string;
  name: string;
  status: SubsystemStatus;
  notes: string;
  lastTested?: string;
}

export interface FlightStep {
  id: number;
  name: string;
  description: string;
  status: "done" | "ready" | "todo" | "blocked";
  script?: string;
  notes?: string;
}

export interface TeamMember {
  id: string;
  name: string;
  role: string;
  color: string;
  currentTask: string;
  needsFromYou?: string;
  lastUpdate?: string;
}

export interface DocEntry {
  title: string;
  path: string;
  description: string;
  category: "guide" | "hardware" | "config" | "test" | "manual" | "reference";
}

export interface SessionEntry {
  date: string;
  summary: string;
  highlights: string[];
}

export interface QuickRef {
  label: string;
  value: string;
  copyable?: boolean;
}

export interface ChatDigest {
  date: string;
  from: string;
  summary: string;
  actionNeeded?: string;
}

// ═══════════════════════════════════════════════════════════
// Project Phase
// ═══════════════════════════════════════════════════════════

export const PROJECT_PHASE = {
  current: "Pi Hardware Testing",
  next: "Outdoor GPS Fix Test",
  blocker: null as string | null,
  progress: 65, // percent toward flight day
};

// ═══════════════════════════════════════════════════════════
// Subsystem Status
// ═══════════════════════════════════════════════════════════

export const SUBSYSTEMS: Subsystem[] = [
  { id: "sim", name: "Simulation (SITL)", status: "done", notes: "Full mission runs on laptop with simulated camera", lastTested: "2026-02-20" },
  { id: "pi-hw", name: "Pi Hardware", status: "done", notes: "Camera, AI detection, Cube connection all verified on Pi 5", lastTested: "2026-02-17" },
  { id: "camera", name: "Pi Camera (IMX296)", status: "done", notes: "1456x1088, BGR output (no cvtColor needed), global shutter", lastTested: "2026-03-11" },
  { id: "ai", name: "AI Detection (TFLite)", status: "done", notes: "~207ms avg, 4.8 FPS, 50/50 detection at 0.966 confidence. Recommended model: sar_v2_1088", lastTested: "2026-03-11" },
  { id: "cube", name: "Cube Connection", status: "done", notes: "Via mavproxy UDP bridge (921600 baud). All commands reach Cube.", lastTested: "2026-02-18" },
  { id: "gps", name: "GPS Lock", status: "partial", notes: "Hardware works (fix_type=1 indoors). Needs outdoor test for 3D fix.", lastTested: "2026-02-18" },
  { id: "mp", name: "Mission Planner", status: "done", notes: "Connected to Cube via mavproxy TCP bridge (tcpin:5762)", lastTested: "2026-02-18" },
  { id: "colors", name: "Camera Colors (BGR fix)", status: "done", notes: "IMX296 outputs BGR despite RGB888 label. Fix applied, needs Pi retest.", lastTested: "2026-02-17" },
  { id: "buzzer", name: "Buzzer", status: "done", notes: "MAVLink PLAY_TUNE works. 15 melodies tested.", lastTested: "2026-03-09" },
  { id: "sim-mvp", name: "simple_simulator.py", status: "done", notes: "Full interactive MVP: keyboard flight, CV, GPS estimation, offset landing", lastTested: "2026-02-20" },
  { id: "pi-flight", name: "pi_flight.py (Web GS)", status: "partial", notes: "Tested in SIMULATION on laptop. Not yet tested on Pi.", lastTested: "2026-02-20" },
  { id: "passive", name: "Passive Flight Script", status: "working", notes: "1_passive_flight.py ready with --save-detections flag", lastTested: "2026-03-09" },
  { id: "flight", name: "Real Flight Test", status: "todo", notes: "Not attempted yet. Follow 5-step progressive testing.", },
  { id: "sssi", name: "SSSI Geofence", status: "done", notes: "SSSI polygon in config.py (SSSI_GPS). Planner avoids SSSI zone.", lastTested: "2026-02-20" },
  { id: "plb", name: "PLB Redirect", status: "todo", notes: "Redirect Personal Locator Beacon signal to aid search prioritisation." },
  { id: "payload", name: "Payload Release", status: "todo", notes: "First aid kit delivery via servo/release mechanism. Hardware TBD." },
  { id: "rangefinder", name: "Rangefinder / LiDAR", status: "todo", notes: "Altitude sensor for precise AGL during descent. Hardware TBD." },
];

// ═══════════════════════════════════════════════════════════
// Flight Testing Steps (in order)
// ═══════════════════════════════════════════════════════════

export const FLIGHT_STEPS: FlightStep[] = [
  {
    id: 1, name: "MP AUTO Waypoints",
    description: "Upload 4-waypoint square in Mission Planner. Switch to AUTO. Drone flies pattern, RTLs. No custom code.",
    status: "todo",
    notes: "Proves: Cube, GPS, motors, RTL all work. Kill switch: RC to STABILIZE.",
  },
  {
    id: 2, name: "Waypoint Test Script",
    description: "Your code arms, takes off to 10m, flies 3-4 GPS waypoints in GUIDED mode, lands. No camera, no CV.",
    status: "ready", script: "tests/flight/2_waypoint_test.py",
    notes: "Script ready (--dry-run for bench test). Proves: your mavlink commands work on real hardware.",
  },
  {
    id: 3, name: "Manual Flight + Passive CV",
    description: "Pilot flies manually on RC. Pi runs camera + AI, logs detections, buzzer beeps. Sends ZERO commands.",
    status: "ready", script: "tests/flight/1_passive_flight.py",
    notes: "Script ready with --save-detections. Proves: CV works in real outdoor conditions.",
  },
  {
    id: 4, name: "Autonomous Search + CV Logging",
    description: "Run main.py with CV in log-only mode. Drone flies search pattern. CV detects and logs but never triggers descent.",
    status: "todo",
    notes: "Needs log-only flag in main.py. Proves: full search pattern + CV from altitude.",
  },
  {
    id: 5, name: "Full Autonomous Mission",
    description: "Everything enabled: search, detect, centre, descend, verify, land. Operator classifies: Y=casualty, I=item of interest, X=false positive.",
    status: "todo",
    notes: "The real thing. Only after steps 1-4 pass.",
  },
];

// ═══════════════════════════════════════════════════════════
// Team
// ═══════════════════════════════════════════════════════════

export const TEAM: TeamMember[] = [
  {
    id: "dima", name: "Dima", role: "Software / CV / Pi Integration",
    color: "#3b82f6",
    currentTask: "Flight day prep, dashboard, documentation. Pi hardware all tested.",
    needsFromYou: undefined,
    lastUpdate: "2026-03-11",
  },
  {
    id: "robin", name: "Robin Carter", role: "GCS / Detection Images",
    color: "#22c55e",
    currentTask: "Needs geotagged detection images from flights",
    needsFromYou: "Run --save-detections during flights, share folder of JPGs with GPS in filename",
    lastUpdate: "2026-03-09",
  },
  {
    id: "edward", name: "Edward", role: "CV Model Training",
    color: "#8b5cf6",
    currentTask: "Training CV model (separate effort)",
    needsFromYou: "Real detection images from Pi camera for retraining",
    lastUpdate: "2026-02-20",
  },
  {
    id: "herish", name: "Herish", role: "Hardware / GPS",
    color: "#f97316",
    currentTask: "Confirmed GPS works outdoors",
    needsFromYou: undefined,
    lastUpdate: "2026-02-18",
  },
  {
    id: "member5", name: "Team Member 5", role: "TBD",
    color: "#6b7280",
    currentTask: "Unknown",
    lastUpdate: undefined,
  },
];

// ═══════════════════════════════════════════════════════════
// Documentation Hub
// ═══════════════════════════════════════════════════════════

export const DOCS: DocEntry[] = [
  // Guides
  { title: "Pi Setup Guide", path: "docs/PI_SETUP.md", description: "Step-by-step Pi setup, venv, dependencies, hardware", category: "guide" },
  { title: "Flight Day Checklist", path: "docs/FLIGHT_DAY_CHECKLIST.md", description: "Single printable doc — follow top to bottom on flight day", category: "guide" },
  { title: "CV Guide", path: "docs/CV_GUIDE.md", description: "Vision system, optimization stages, model swapping, GPS estimation", category: "guide" },
  { title: "First Flight Plan", path: "docs/FIRST_FLIGHT.md", description: "Progressive flight testing steps with safety checks", category: "guide" },
  { title: "Preflight Checklist", path: "docs/PREFLIGHT_CHECKLIST.md", description: "Pre-flight safety checks", category: "guide" },

  // Hardware
  { title: "Architecture", path: "docs/ARCHITECTURE.md", description: "System overview, hardware checklist, evolving diagrams", category: "hardware" },
  { title: "Connectivity Guide", path: "docs/CONNECTIVITY.md", description: "Connection debugging: Pi↔Cube, mavproxy, MP", category: "hardware" },
  { title: "Team Plan", path: "docs/TEAM_PLAN.md", description: "Team workstreams and responsibilities", category: "hardware" },

  // Config
  { title: "config.py", path: "config.py", description: "ALL settings: altitudes, speeds, camera, connection, mode", category: "config" },
  { title: "vision.py", path: "vision.py", description: "Camera + AI detection. Dual backend: Ultralytics/TFLite", category: "config" },

  // Test scripts
  { title: "Camera Test", path: "tests/laptop/test_camera.py", description: "Does camera give frames?", category: "test" },
  { title: "Detection Test", path: "tests/laptop/test_cv.py", description: "Does AI detect dummy? (--camera)", category: "test" },
  { title: "Benchmark", path: "tests/hardware/benchmark.py", description: "Inference speed (50 runs, timing)", category: "test" },
  { title: "Buzzer Test", path: "tests/hardware/buzzer_test.py", description: "Buzzer melodies via MAVLink (15 tunes)", category: "test" },
  { title: "CV Benchmark", path: "tests/hardware/cv_benchmark.py", description: "Detection rate + speed with live camera", category: "test" },
  { title: "Passive Flight", path: "tests/flight/1_passive_flight.py", description: "Passive detection during manual RC flight (zero commands)", category: "test" },
  { title: "Diagnostics", path: "tests/diagnostics/diagnostics.py", description: "Visual dashboard: all subsystem connectivity", category: "test" },
  { title: "Waypoint Test", path: "tests/flight/2_waypoint_test.py", description: "Fly 4 GPS waypoints in GUIDED mode (--dry-run)", category: "test" },

  // Reference
  { title: "Roadmap", path: "docs/ROADMAP.md", description: "Full 10-phase development history", category: "reference" },
  { title: "Next Steps", path: "docs/NEXT_STEPS.md", description: "Phase-by-phase development plan", category: "reference" },
];

// ═══════════════════════════════════════════════════════════
// Session Log (from CLAUDE.md, most recent first)
// ═══════════════════════════════════════════════════════════

export const SESSION_LOG: SessionEntry[] = [
  {
    date: "2026-03-16",
    summary: "DJI video analysis, model retraining v2, FOV calibration",
    highlights: [
      "Built video replay pipeline (video_test.py) with detection overlay, SRT telemetry, GPS estimation, scale bar, measure tool",
      "A/B model comparison tool (video_test_compare.py) — M key switches models live",
      "FOV calibrated to 54.4 deg HFOV for cropped DJI video (1456x1088) using tools/fov_calibrate_video.py",
      "Retrained YOLOv8n on 300 synthetic + 16 real + 50 negatives at 1456x1088 — mAP50=0.995 (sar_v2_1088)",
      "Created generate_dataset_v2.py + tools/label_tool.py for native resolution training data",
      "dataset_v2/ with 366 images ready for Colab, cv_models/ with 3 model variants",
    ],
  },
  {
    date: "2026-03-11 (field day)",
    summary: "FOV calibration, lens calibration, Pi benchmark — weather cancelled flight",
    highlights: [
      "FOV calibration: FOCAL_LENGTH_MM = 5.46 (92cm visible at 1m)",
      "Lens calibration with checkerboard (RMS 0.399), undistortion added to vision.py (+1.5ms)",
      "Pi benchmark: best.tflite 207ms avg / 4.8 FPS, 50/50 detection at 0.966 confidence",
      "passive_watch.py improvements: GPS estimate at ground level, pink dot on detection center",
      "CV speed research: FP16 XNNPACK (~10 FPS), threaded pipeline, NCNN (~15 FPS)",
      "Weather cancelled actual flight — bench testing only",
    ],
  },
  {
    date: "2026-03-11",
    summary: "BOOTSTRAP.md workflows, headless main.py, blueprints, code review",
    highlights: [
      "Applied BOOTSTRAP.md workflows: brain-dump.md, NICE_TO_HAVE.md, .claude/commands/, blueprints for all files >500 lines",
      "main.py headless support: --headless flag, terminal keyboard input, browser buttons at http://PI_IP:8090",
      "Thorough code review (6 parallel agents): found 3 bugs, 4 security issues in main.py, fixed pi_flight.py self.investigating bug",
      "Drawing/flight script separation: draw on laptop → JSON → Pi loads headlessly",
      "Fixed stale script references across 7+ docs",
    ],
  },
  {
    date: "2026-03-09",
    summary: "Dashboard setup, buzzer tunes, --save-detections flag",
    highlights: [
      "Created dashboard/ (React+Vite) with GP v2 + WBS tabs from Orgnaiser",
      "Added --save-detections flag to pi_passive_flight.py and simple_simulator.py",
      "Expanded buzzer test to 15 tunes (Fur Elise, Mario, Tetris, Imperial March, Rickroll...)",
      "Set up workflow system (CLAUDE.md, rules, commands, brain-dump, NICE_TO_HAVE)",
      "Copied BOOTSTRAP2.md to parent directory for universal project setup",
      "Diagnosed mavproxy conflicts (system services at wrong baud rate)",
    ],
  },
  {
    date: "2026-02-20 (p2)",
    summary: "pi_flight.py web ground station + flight day prep",
    highlights: [
      "Created pi_flight.py — browser dashboard with MJPEG stream + commands",
      "Works headless (Pi) or laptop at http://localhost:8090",
      "FAKE DET button for testing without CV",
      "Created FLIGHT_DAY_CHECKLIST.md (single printable document)",
    ],
  },
  {
    date: "2026-02-20 (p1)",
    summary: "Multi-target, clustering, estimation improvements",
    highlights: [
      "Multiple dummies on map, pilot classification (Y/I/X)",
      "Spatial clustering with permanent IDs",
      "Running total average + Kalman filter + inverse variance weighting",
      "Altitude test (H key) — confirmed lower altitude = better estimate",
    ],
  },
  {
    date: "2026-02-19",
    summary: "simple_simulator.py — interactive MVP",
    highlights: [
      "Keyboard flight + CV + GPS estimation + 7.5m offset landing",
      "GPS centering (C), visual servo (V), GPS lock (G), offset land (L)",
      "Camera shake + GPS drift simulation",
      "End-to-end mission tested in simulation",
    ],
  },
  {
    date: "2026-02-18 (p3)",
    summary: "Camera stream detection fix, H.264 alternative",
    highlights: [
      "Fixed pi_camera_stream.py detection (camera + model separation)",
      "MJPEG chosen over H.264/HLS (low latency > compression)",
    ],
  },
  {
    date: "2026-02-18 (p2)",
    summary: "Cube command testing, mavproxy fixes, flight prep",
    highlights: [
      "Tested all commands: GUIDED, STABILIZE, LOITER, LAND, ARM, waypoints",
      "Fixed 3 mavproxy issues: heartbeat filtering, target_system, mode mapping",
      "Created pi_waypoint_test.py and pi_camera_stream.py",
      "All commands reach Cube — failures are from missing RC/GPS (expected indoors)",
    ],
  },
  {
    date: "2026-02-18 (p1)",
    summary: "GPS diagnostics, Cube wiring, diagnostics GS fix",
    highlights: [
      "GPS hardware confirmed (fix_type=1 indoors, needs outdoor for satellites)",
      "Here 3+ GPS on CAN2, Pi on TELEM2",
      "Fixed diagnostics Mission Planner detection (ss -tna vs socket)",
    ],
  },
  {
    date: "2026-02-17 (p2)",
    summary: "Camera color fix (BGR/RGB) — CRITICAL",
    highlights: [
      "IMX296 outputs BGR despite picamera2 labeling it RGB888",
      "Removed incorrect cvtColor conversion from ALL scripts",
      "Colors now correct — fixed blue tint issue",
    ],
  },
  {
    date: "2026-02-17 (p1)",
    summary: "Pi setup and hardware testing — first Pi session",
    highlights: [
      "Pi 5 with Python 3.13, ai-edge-litert instead of tflite-runtime",
      "Camera: PASS, Detection: PASS (206ms avg), Cube: PASS via mavproxy",
      "Buzzer: PASS, Main.py runs on Pi (stuck at ARMING indoors — expected)",
      "Mission Planner connected to real Cube via Pi",
    ],
  },
  {
    date: "2026-02-16",
    summary: "Project setup, cross-platform testing, documentation",
    highlights: [
      "Audited all docs, created ARCHITECTURE.md",
      "Fixed REAL mode gap (interactive polygon drawing)",
      "Tested: Windows sim, WSL sim, Docker Pi test — all pass",
      "Requirements files strategy (platform-specific freezes)",
    ],
  },
];

// ═══════════════════════════════════════════════════════════
// Quick Reference
// ═══════════════════════════════════════════════════════════

export const QUICK_REF: QuickRef[] = [
  { label: "Pi IP", value: "192.168.1.3", copyable: true },
  { label: "Cube Baud", value: "921600" },
  { label: "AI Model", value: "best.tflite (YOLOv8n) — recommended: sar_v2_1088 (mAP50=0.995)" },
  { label: "Confidence", value: "0.4 (vision.py)" },
  { label: "Pi Inference", value: "~207ms / 4.8 FPS" },
  { label: "Camera", value: "IMX296 1456x1088 BGR (no cvtColor)" },
  { label: "Dashboard", value: "http://localhost:5050", copyable: true },
  { label: "pi_flight.py", value: "http://PI_IP:8090", copyable: true },
  { label: "mavproxy", value: "sudo /opt/mavlink/mavlink-venv/bin/mavproxy.py --master=/dev/ttyAMA0 --baudrate=921600 --streamrate=10 --out=udpout:127.0.0.1:14550 --out=tcpin:0.0.0.0:5762", copyable: true },
  { label: "SITL Home", value: "--home=51.423412,-2.671414,50,155", copyable: true },
];

// ═══════════════════════════════════════════════════════════
// Group Chat Digest (key decisions from team WhatsApp)
// ═══════════════════════════════════════════════════════════

export const CHAT_DIGEST: ChatDigest[] = [
  { date: "2026-03-09", from: "Robin", summary: "Needs geotagged detection images — JPGs with GPS coords in filename", actionNeeded: "Run --save-detections during flights, share output folder" },
  { date: "2026-02-18", from: "Herish", summary: "Confirmed GPS works outdoors — got satellite lock", actionNeeded: undefined },
  { date: "2026-02-18", from: "Edward", summary: "Working on CV model training separately", actionNeeded: "Share real detection images from Pi camera when available" },
];

// ═══════════════════════════════════════════════════════════
// Status helpers
// ═══════════════════════════════════════════════════════════

export const STATUS_CONFIG: Record<SubsystemStatus, { color: string; bg: string; label: string }> = {
  done:    { color: "#22c55e", bg: "rgba(34,197,94,0.1)",  label: "DONE" },
  working: { color: "#3b82f6", bg: "rgba(59,130,246,0.1)", label: "WORKING" },
  partial: { color: "#f59e0b", bg: "rgba(245,158,11,0.1)", label: "PARTIAL" },
  todo:    { color: "#6b7280", bg: "rgba(107,114,128,0.1)", label: "TODO" },
  blocked: { color: "#ef4444", bg: "rgba(239,68,68,0.1)",  label: "BLOCKED" },
};

export const STEP_CONFIG: Record<FlightStep["status"], { color: string; symbol: string }> = {
  done:    { color: "#22c55e", symbol: "\u2713" },
  ready:   { color: "#3b82f6", symbol: "\u25B6" },
  todo:    { color: "#6b7280", symbol: "\u25CB" },
  blocked: { color: "#ef4444", symbol: "\u2716" },
};
