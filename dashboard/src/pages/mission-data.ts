/**
 * Mission & Levels Data — The "what" and "how" of the SAR drone project
 * Source: AENGM0074 Project Brief Release 2.1 (4 Feb 2026)
 *
 * Tab 1 (Mission): scenario, requirements, constraints, hardware, deliverables
 * Tab 2 (Levels): 3 product levels with stepping stones
 */

// ═══════════════════════════════════════════════════════════
// Mission — The "What" (from AENGM0074 brief)
// ═══════════════════════════════════════════════════════════

export const MISSION = {
  holyGrail: "Locate a missing person in a search area, avoid no-fly zones, safely land nearby to deliver a first aid kit, and return home.",
  module: "AENGM0074 — Group Design Project",
  briefVersion: "Release 2.1, 4 Feb 2026",
  university: "University of Bristol, MSc Robotics",
  teamSize: 5,
  location: "Fenswood Farm, Failand, North Somerset",

  scenario: [
    "A person has gone missing in a rural/wilderness area near Fenswood Farm.",
    "Emergency services have activated a Personal Locator Beacon (PLB) which gives an approximate search focus area.",
    "The PLB is activated mid-search (not at the start) — the drone must redirect when it receives the PLB signal.",
    "The search area includes a Site of Special Scientific Interest (SSSI) which is a designated no-fly zone.",
    "The drone must search the area, locate the person, deliver a first aid kit via payload release, and return to launch.",
    "The field contains hedgerows, uneven terrain, and potential false positives (animals, debris).",
  ],

  objectives: [
    { id: "search", label: "Search", description: "Fly a systematic search pattern over the designated area, avoiding the SSSI no-fly zone. Redirect to PLB Focus Area when signal received mid-search.", icon: "S" },
    { id: "focus", label: "Focus on PLB", description: "When PLB signal is received (simulated mid-mission), redirect search to the PLB Focus Area for higher priority coverage.", icon: "P" },
    { id: "land", label: "Land & Deliver", description: "Locate the missing person, land within 5-10m, and release a first aid kit via the Tarot payload release mechanism.", icon: "L" },
    { id: "return", label: "Return", description: "Return to launch point safely after mission completion. RTL on command, low battery, or failsafe.", icon: "R" },
  ],

  requirements: [
    { id: "R01", text: "The UAS shall be capable of autonomous flight in GNSS-enabled outdoor environments.", severity: "shall" as const, notes: "ArduCopter GUIDED mode + GPS" },
    { id: "R02", text: "The UAS shall be capable of navigating to GPS waypoints.", severity: "shall" as const, notes: "Lawnmower pattern generator + GUIDED goto" },
    { id: "R03", text: "The UAS shall be capable of detecting a person lying on the ground from the air.", severity: "shall" as const, notes: "YOLOv8n TFLite on Pi 5" },
    { id: "R04", text: "The UAS shall avoid designated no-fly zones during the mission.", severity: "shall" as const, notes: "SSSI geofence exclusion zone" },
    { id: "R05", text: "The UAS shall be capable of responding to a simulated PLB activation signal.", severity: "shall" as const, notes: "Redirect search to PLB Focus Area mid-mission" },
    { id: "R06", text: "The UAS shall be capable of landing within 5-10 metres of a detected person.", severity: "shall" as const, notes: "GPS estimation + offset landing" },
    { id: "R07", text: "The UAS should be capable of delivering a payload (first aid kit) to the detected person.", severity: "should" as const, notes: "Tarot payload release mechanism" },
    { id: "R08", text: "The UAS shall return to the launch location after task completion.", severity: "shall" as const, notes: "MAV_CMD_NAV_RETURN_TO_LAUNCH" },
    { id: "R09", text: "The UAS shall operate within Visual Line of Sight (VLOS) at all times.", severity: "shall" as const, notes: "Regulatory requirement" },
    { id: "R10", text: "The UAS shall have a manual override capability.", severity: "shall" as const, notes: "RC kill switch to STABILIZE" },
    { id: "R11", text: "The system shall log mission data for post-flight analysis.", severity: "shall" as const, notes: "CSV logging, detection images, GPS tracks" },
    { id: "R12", text: "The UAS shall not exceed 50m altitude AGL during the mission.", severity: "shall" as const, notes: "Brief specifies 50m max, not 120m" },
  ],

  constraints: [
    { label: "Max Altitude 50m", description: "The brief specifies 50m AGL maximum, not the general 120m legal limit. Operating at 30m search, 15m verify.", severity: "critical" as const },
    { label: "RC Kill Switch", description: "Pilot can override to STABILIZE/LOITER at ANY time via RC. Non-negotiable safety requirement (R10).", severity: "critical" as const },
    { label: "Visual Line of Sight", description: "Drone must remain within pilot's VLOS at all times (R09). Regulatory and brief requirement.", severity: "critical" as const },
    { label: "SSSI No-Fly Zone", description: "Site of Special Scientific Interest within search area. Must be geofenced and avoided (R04).", severity: "critical" as const },
    { label: "Landing Zone 5-10m", description: "Must land within 5-10m of detected person (R06). Not directly on top (propwash risk).", severity: "warning" as const },
    { label: "PLB Redirect Mid-Search", description: "PLB signal arrives during search. Drone must redirect to PLB Focus Area (R05).", severity: "warning" as const },
    { label: "Battery Life", description: "~15-20 min flight time. Mission must complete within one battery.", severity: "warning" as const },
    { label: "GPS Required", description: "3D GPS fix (fix_type >= 3) required before arming. Min 8 satellites recommended.", severity: "critical" as const },
  ],

  successCriteria: [
    { label: "Person detected from air", metric: "CV detects dummy from search altitude (15-30m)" },
    { label: "SSSI avoided", metric: "Drone never enters no-fly zone geofence" },
    { label: "PLB redirect works", metric: "Drone redirects to focus area on PLB signal" },
    { label: "Position estimated", metric: "GPS estimate within 5m of actual position" },
    { label: "Landed in zone", metric: "Within 5-10m of target, no damage" },
    { label: "Payload delivered", metric: "First aid kit released near target (R07, should)" },
    { label: "RTL successful", metric: "Drone returned to launch point after mission" },
  ],
};

export const HARDWARE = [
  { name: "Hexsoon EDU-450", role: "Airframe", details: "Quadcopter frame provided by university. Education platform, ~450mm wheelbase.", status: "verified" as const, specUrl: "https://www.hexsoon.com" },
  { name: "Cube Orange Plus", role: "Flight Controller", details: "ArduCopter V4.6.3, QUAD/X frame. Handles all flight dynamics, GPS nav, failsafes.", status: "verified" as const, specUrl: "https://docs.cubepilot.org" },
  { name: "Here 3+ GPS", role: "Navigation", details: "GNSS receiver connected to Cube CAN2. Multi-constellation (GPS+GLONASS+BeiDou). Needs outdoor clear sky.", status: "partial" as const, specUrl: "https://docs.cubepilot.org/user-guides/here-3/here-3+" },
  { name: "FrSky TW-Mini", role: "RC Receiver", details: "Receiver paired with FrSky Twin X14 transmitter. 2.4GHz, telemetry capable.", status: "verified" as const, specUrl: "" },
  { name: "Raspberry Pi 5", role: "Companion Computer", details: "Python 3.13, runs CV pipeline, communicates with Cube via mavproxy UDP bridge (921600 baud).", status: "verified" as const, specUrl: "https://www.raspberrypi.com/products/raspberry-pi-5/" },
  { name: "Global Shutter Camera", role: "Vision Sensor", details: "IMX296 sensor, 640x480, BGR output. Global shutter = no rolling shutter artifacts. ~4 FPS with TFLite.", status: "verified" as const, specUrl: "" },
  { name: "6mm CS-Mount Lens", role: "Optics", details: "6mm focal length lens for the global shutter camera. FOV suitable for 15-30m search altitude.", status: "verified" as const, specUrl: "" },
  { name: "FrSky Twin X14", role: "RC Transmitter", details: "Pilot's controller. Kill switch mapped to mode channel (STABILIZE). Always has override priority.", status: "verified" as const, specUrl: "" },
  { name: "Tarot Payload Release", role: "Delivery Mechanism", details: "Servo-actuated payload release for first aid kit delivery (R07). Triggered via MAVLink servo command.", status: "todo" as const, specUrl: "" },
  { name: "SanDisk MicroSD", role: "Storage", details: "For flight logs, detection images, mission data. Pi and Cube both have SD cards.", status: "verified" as const, specUrl: "" },
  { name: "YOLOv8n TFLite", role: "AI Model", details: "Custom trained on synthetic dummy images. ~256ms inference on Pi. 0.966 confidence on bench test.", status: "verified" as const, specUrl: "" },
  { name: "mavproxy", role: "MAVLink Router", details: "Bridges Cube serial (TELEM2) to UDP (Pi scripts) + TCP (Mission Planner). Runs as service on Pi.", status: "verified" as const, specUrl: "https://ardupilot.org/mavproxy/" },
];

export const DELIVERABLES = [
  { id: "D1", name: "Group Contract", date: "Week 2", weight: "2.5%", status: "done" as const, description: "Team roles, responsibilities, ways of working agreement." },
  { id: "D2", name: "Preliminary Design Review", date: "Week 5", weight: "10%", status: "done" as const, description: "Initial system design, requirements analysis, architecture decisions." },
  { id: "D3", name: "Critical Design Review", date: "Week 8", weight: "15%", status: "done" as const, description: "Detailed design, component selection, integration plan, risk assessment." },
  { id: "D4", name: "Flight Readiness Review", date: "Week 10", weight: "10%", status: "active" as const, description: "Pre-flight safety case, test results, operational procedures, checklists." },
  { id: "D5", name: "Flight Test", date: "Week 11-12", weight: "20%", status: "upcoming" as const, description: "Demonstrate mission at Fenswood Farm. Search, detect, land, deliver, return." },
  { id: "D6", name: "Final Report", date: "Week 13", weight: "30%", status: "upcoming" as const, description: "Full technical report: design, implementation, results, lessons learned." },
  { id: "D7", name: "Peer Assessment", date: "Week 13", weight: "12.5%", status: "upcoming" as const, description: "Individual peer review of team members contributions." },
];

// ═══════════════════════════════════════════════════════════
// Levels — The "How" (3 stepping stones)
// ═══════════════════════════════════════════════════════════

export interface MissionLevel {
  id: number;
  name: string;
  tag: string;
  autonomy: string;
  color: string;
  description: string;
  droneActions: string[];
  pilotActions: string[];
  scripts: { name: string; purpose: string }[];
  whatsWorking: string[];
  whatsMissing: string[];
  flightSteps: number[];
  stateFlow: string;
}

export const LEVELS: MissionLevel[] = [
  {
    id: 1,
    name: "Manual MVP",
    tag: "MINIMUM VIABLE",
    autonomy: "None — pilot flies everything",
    color: "#22c55e",
    description: "Pilot flies the drone manually via RC controller. Raspberry Pi runs camera + AI detection in the background, showing a live feed with detection overlays. When the pilot sees a detection on screen, they manually fly toward it and manually land. The Pi sends zero flight commands — it only observes and reports.",
    droneActions: [
      "Camera captures frames continuously",
      "AI model runs detection on each frame",
      "Detection overlay shown on video feed",
      "Buzzer beeps when detection found",
      "GPS + altitude logged with each detection",
      "Detection images saved with GPS in filename",
    ],
    pilotActions: [
      "Takes off manually (RC)",
      "Flies search pattern manually (RC)",
      "Watches video feed for detections",
      "Flies toward detected target manually",
      "Decides when to land",
      "Lands manually within 5-10m of target (R06)",
      "Can abort at any time (RC to STABILIZE)",
    ],
    scripts: [
      { name: "tests2/pi_passive_flight.py", purpose: "Passive CV during manual RC flight — zero commands sent" },
      { name: "tests/pi_camera_stream.py", purpose: "MJPEG video stream to browser (optional)" },
    ],
    whatsWorking: [
      "Camera + AI detection on Pi (tested, 3.9 FPS)",
      "Buzzer alerts via MAVLink",
      "--save-detections flag saves geotagged images",
      "Cube connection verified, all subsystems OK",
    ],
    whatsMissing: [
      "Outdoor GPS fix test (indoor only so far)",
      "Real flight test with detection (Step 3 in flight plan)",
      "Video stream latency in field conditions",
    ],
    flightSteps: [3],
    stateFlow: "MANUAL FLIGHT -> Pi observes -> Detection overlay -> Pilot decides -> Manual land",
  },
  {
    id: 2,
    name: "Semi-Autonomous",
    tag: "TARGET — WHAT WE'RE BUILDING",
    autonomy: "Partial — drone flies autonomously, pilot confirms decisions",
    color: "#3b82f6",
    description: "Drone autonomously takes off, flies a lawnmower search over the area while avoiding the SSSI geofence (R04). When CV detects a person, pilot is alerted. On PLB signal (R05), drone redirects to Focus Area. Pilot classifies: Y=target, I=interest, X=false positive. Confirmed target: drone centres, descends, lands 5-10m away (R06), releases first aid kit via Tarot (R07). Pilot has RC override at all times (R10).",
    droneActions: [
      "Arms and takes off autonomously (GUIDED mode)",
      "Flies lawnmower search pattern, avoids SSSI geofence (R04)",
      "CV runs continuously, builds GPS estimate of detections",
      "Spatial clustering groups nearby detections",
      "Redirects to PLB Focus Area on signal (R05)",
      "On pilot command (N): flies to estimated position, descends to 15m",
      "Sends detection image + GPS to pilot's browser dashboard",
      "On confirm (Y): centres on target, locks GPS estimate",
      "On land (L): flies to 5-10m offset, auto-lands, releases payload (R07)",
      "RTL on command, battery low, or RC failsafe (R08)",
    ],
    pilotActions: [
      "Defines search polygon on map (before flight)",
      "Monitors flight on Mission Planner + pi_flight.py dashboard",
      "Reviews detection images when drone alerts",
      "Classifies: Y (dummy), I (interest), X (false positive)",
      "Commands: N (investigate), L (land), M (resume search)",
      "RC override available at all times — STABILIZE = instant stop (R10)",
    ],
    scripts: [
      { name: "pi_flight.py", purpose: "Web ground station — browser dashboard with video + commands + GPS grid" },
      { name: "main.py", purpose: "Full state machine: INIT -> ARM -> TAKEOFF -> SEARCH -> CENTRE -> DESCEND -> VERIFY -> LAND" },
      { name: "simple_simulator.py", purpose: "Laptop simulation of full L2 flow (tested end-to-end)" },
    ],
    whatsWorking: [
      "Full state machine logic (main.py) — tested in SITL simulation",
      "simple_simulator.py: complete L2 flow tested end-to-end on laptop",
      "pi_flight.py: browser dashboard with video stream, GPS grid, commands",
      "GPS estimation: spatial clustering, inverse variance weighting, Kalman filter",
      "Pilot classification (Y/I/X) with estimate reset on false positives",
      "7.5m offset landing — tested in simulation",
      "Lawnmower search pattern generator from any polygon",
    ],
    whatsMissing: [
      "Real flight test (all 5 flight steps)",
      "SSSI geofence implementation (R04)",
      "PLB redirect logic (R05)",
      "Tarot payload release integration (R07)",
      "Outdoor GPS accuracy validation",
      "Detection performance from altitude (30m search alt)",
      "pi_flight.py not yet tested on real Pi hardware",
    ],
    flightSteps: [1, 2, 3, 4, 5],
    stateFlow: "ARM -> TAKEOFF -> SEARCH (avoid SSSI) -> DETECT -> pilot N -> INVESTIGATE -> pilot Y -> CENTRE -> DESCEND -> pilot L -> LAND (5-10m) + PAYLOAD -> RTL",
  },
  {
    id: 3,
    name: "Full Autonomous",
    tag: "STRETCH GOAL",
    autonomy: "Full — drone decides everything, pilot only monitors",
    color: "#a855f7",
    description: "Everything from L2, but the drone makes all decisions autonomously. Detection confidence threshold replaces pilot confirmation. Multiple passes over target build certainty. Drone auto-verifies (descends, re-detects from lower altitude) and auto-lands if confidence exceeds threshold. Pilot monitors but does not need to intervene unless something goes wrong.",
    droneActions: [
      "Everything from L2, plus:",
      "Autonomous detection verification (multi-pass, descending altitude)",
      "Confidence accumulation: N consecutive high-confidence frames = confirmed",
      "Auto-decides to investigate (no pilot N command needed)",
      "Auto-decides to land (no pilot Y/L command needed)",
      "Autonomous RTL after area fully searched or target found",
    ],
    pilotActions: [
      "Defines search area before flight",
      "Monitors progress on dashboard",
      "RC override available — STABILIZE = instant stop (R10)",
      "Reviews mission log after flight",
      "Intervenes ONLY if something goes wrong",
    ],
    scripts: [
      { name: "main.py (with auto-confirm flag)", purpose: "Same state machine but skips pilot confirmation steps" },
    ],
    whatsWorking: [
      "State machine already supports all transitions",
      "Detection confidence tracking exists",
      "GPS estimation pipeline is solid",
    ],
    whatsMissing: [
      "Everything from L2 must work first",
      "Autonomous verification logic (confidence accumulation)",
      "Extensive flight testing to calibrate thresholds",
      "False positive handling without pilot",
      "Regulatory considerations for fully autonomous flight",
      "Not attempted — L2 is the priority",
    ],
    flightSteps: [5],
    stateFlow: "ARM -> TAKEOFF -> SEARCH -> AUTO-DETECT -> AUTO-VERIFY (multi-pass) -> AUTO-LAND + PAYLOAD -> RTL",
  },
];

// ═══════════════════════════════════════════════════════════
// Roadmap — Stepping stones to reach each level
// ═══════════════════════════════════════════════════════════

export interface RoadmapStep {
  id: string;
  level: number;
  name: string;
  status: "done" | "ready" | "todo" | "blocked";
  description: string;
  depends?: string[];
}

export const ROADMAP: RoadmapStep[] = [
  // Foundation (all levels)
  { id: "f1", level: 0, name: "Simulation working", status: "done", description: "Full mission runs on laptop with SITL + simulated camera" },
  { id: "f2", level: 0, name: "Pi hardware verified", status: "done", description: "Camera, AI, Cube connection all tested on Pi 5" },
  { id: "f3", level: 0, name: "Camera colors fixed", status: "done", description: "IMX296 BGR output identified and fixed in all scripts" },
  { id: "f4", level: 0, name: "Cube commands work", status: "done", description: "All MAVLink commands reach Cube and get processed correctly" },
  { id: "f5", level: 0, name: "mavproxy bridge stable", status: "done", description: "UDP + TCP routing working, system services conflict resolved" },

  // L1 steps
  { id: "l1-1", level: 1, name: "Outdoor GPS fix", status: "todo", description: "Take Pi + Cube outside, get 3D satellite lock, verify coordinates", depends: ["f5"] },
  { id: "l1-2", level: 1, name: "MP AUTO waypoints", status: "todo", description: "Fly simple square pattern in Mission Planner AUTO mode. No custom code.", depends: ["l1-1"] },
  { id: "l1-3", level: 1, name: "Manual flight + passive CV", status: "ready", description: "Pilot flies RC, Pi runs camera + AI, logs detections. Zero commands.", depends: ["l1-1"] },
  { id: "l1-4", level: 1, name: "Detection from altitude", status: "todo", description: "Verify CV detects dummy from 15-30m altitude in real conditions", depends: ["l1-3"] },

  // L2 steps
  { id: "l2-1", level: 2, name: "Waypoint test script", status: "ready", description: "pi_waypoint_test.py: arm, takeoff, fly 4 waypoints, land. No CV.", depends: ["l1-2"] },
  { id: "l2-2", level: 2, name: "Autonomous search pattern", status: "todo", description: "main.py flies lawnmower pattern autonomously with CV logging only", depends: ["l2-1", "l1-4"] },
  { id: "l2-3", level: 2, name: "pi_flight.py on real Pi", status: "todo", description: "Test browser dashboard, video stream, commands on actual Pi hardware", depends: ["l1-3"] },
  { id: "l2-4", level: 2, name: "SSSI geofence (R04)", status: "todo", description: "Implement no-fly zone exclusion in search pattern and navigation", depends: ["l2-1"] },
  { id: "l2-5", level: 2, name: "PLB redirect (R05)", status: "todo", description: "Mid-search redirect to PLB Focus Area on simulated signal", depends: ["l2-2"] },
  { id: "l2-6", level: 2, name: "Tarot payload release (R07)", status: "todo", description: "Integrate servo-actuated payload release for first aid kit delivery", depends: ["l2-3"] },
  { id: "l2-7", level: 2, name: "Full semi-auto mission", status: "todo", description: "Search + avoid SSSI + PLB redirect + detect + land + deliver + RTL", depends: ["l2-4", "l2-5", "l2-6"] },

  // L3 steps
  { id: "l3-1", level: 3, name: "Confidence accumulation", status: "todo", description: "Auto-verify using N consecutive high-confidence detections", depends: ["l2-7"] },
  { id: "l3-2", level: 3, name: "Multi-pass verification", status: "todo", description: "Fly over target multiple times at decreasing altitude to build certainty", depends: ["l3-1"] },
  { id: "l3-3", level: 3, name: "Full autonomous mission", status: "todo", description: "No pilot confirmation needed. Drone decides everything.", depends: ["l3-2"] },
];

export const LEVEL_COLORS: Record<number, string> = {
  0: "#94a3b8", // foundation
  1: "#22c55e", // L1
  2: "#3b82f6", // L2
  3: "#a855f7", // L3
};

export const STATUS_COLORS: Record<string, { color: string; bg: string }> = {
  done:     { color: "#22c55e", bg: "rgba(34,197,94,0.1)" },
  active:   { color: "#f59e0b", bg: "rgba(245,158,11,0.1)" },
  ready:    { color: "#3b82f6", bg: "rgba(59,130,246,0.1)" },
  todo:     { color: "#6b7280", bg: "rgba(107,114,128,0.1)" },
  blocked:  { color: "#ef4444", bg: "rgba(239,68,68,0.1)" },
  upcoming: { color: "#6b7280", bg: "rgba(107,114,128,0.1)" },
  verified: { color: "#22c55e", bg: "rgba(34,197,94,0.1)" },
  partial:  { color: "#f59e0b", bg: "rgba(245,158,11,0.1)" },
};

// ═══════════════════════════════════════════════════════════
// Fenswood Farm — Flight Area Coordinates (from NFZ.kml)
// ═══════════════════════════════════════════════════════════

export interface GpsCoord {
  lat: number;
  lon: number;
}

export interface FlightZone {
  id: string;
  name: string;
  color: string;
  description: string;
  coords: GpsCoord[];
}

export const TAKEOFF_LOCATION: GpsCoord = { lat: 51.42340640, lon: -2.67144603 };

export const FLIGHT_ZONES: FlightZone[] = [
  {
    id: "flight-area",
    name: "Flight Area",
    color: "#22c55e",
    description: "Maximum boundary — do NOT fly outside this. Green outline in Google Earth.",
    coords: [
      { lat: 51.42342595, lon: -2.67172077 },
      { lat: 51.42124623, lon: -2.67013403 },
      { lat: 51.42244012, lon: -2.66568782 },
      { lat: 51.42469179, lon: -2.66706023 },
    ],
  },
  {
    id: "survey-area",
    name: "Survey Area",
    color: "#3b82f6",
    description: "Where the dummy/casualty will be placed. Search pattern covers this area.",
    coords: [
      { lat: 51.42326957, lon: -2.67094835 },
      { lat: 51.42287025, lon: -2.67004543 },
      { lat: 51.42336623, lon: -2.66816930 },
      { lat: 51.42421477, lon: -2.66880977 },
      { lat: 51.42354070, lon: -2.67127778 },
    ],
  },
  {
    id: "focus-area",
    name: "Focus Area (Example)",
    color: "#f59e0b",
    description: "Example smaller search area from brief. Can use as starting polygon for search.",
    coords: [
      { lat: 51.42330494, lon: -2.66982370 },
      { lat: 51.42344371, lon: -2.66949620 },
      { lat: 51.42352782, lon: -2.66980025 },
      { lat: 51.42334973, lon: -2.67001828 },
    ],
  },
  {
    id: "sssi",
    name: "SSSI (No-Fly Zone)",
    color: "#ef4444",
    description: "Site of Special Scientific Interest — DO NOT fly into this area. Hard boundary.",
    coords: [
      { lat: 51.42353587, lon: -2.67145175 },
      { lat: 51.42215640, lon: -2.66976824 },
      { lat: 51.42267105, lon: -2.66770544 },
      { lat: 51.42335592, lon: -2.66816460 },
      { lat: 51.42286083, lon: -2.67004342 },
      { lat: 51.42326667, lon: -2.67096542 },
      { lat: 51.42356862, lon: -2.67132430 },
    ],
  },
];
