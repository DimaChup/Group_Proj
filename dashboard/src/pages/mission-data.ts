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
    { id: "search", label: "Search", description: "Fly a systematic search pattern over the designated area, avoiding the SSSI no-fly zone. Identify items of interest (clothing, equipment). Redirect to PLB Focus Area when signal received mid-search.", icon: "S" },
    { id: "focus", label: "Focus on PLB", description: "When PLB signal is received (simulated mid-mission), redirect search to the PLB Focus Area for higher priority coverage.", icon: "P" },
    { id: "land", label: "Land & Deliver", description: "Locate the missing person, land within 10m but NOT within 5m, and release a first aid kit via the Tarot payload release mechanism.", icon: "L" },
    { id: "return", label: "Return", description: "Return to launch point safely after mission completion. RTL on command, low battery, or failsafe.", icon: "R" },
  ],

  requirements: [
    { id: "R01", text: "The drone shall only fly within the Flight Area.", severity: "shall" as const, notes: "Geofence: coords in AENGM0074.kml. Report any excursions." },
    { id: "R02", text: "The drone shall not fly over the SSSI.", severity: "shall" as const, notes: "SSSI exclusion zone. Automatic geofence required." },
    { id: "R03", text: "The drone shall take off from within 5m of the defined Take-Off Location.", severity: "shall" as const, notes: "TOL coords in AENGM0074.kml." },
    { id: "R04", text: "The drone shall not exceed 50m altitude above TOL ground level.", severity: "shall" as const, notes: "Operating at 30m search, 15m verify." },
    { id: "R05", text: "The drone shall search the Search Area and identify items of interest (clothing, equipment).", severity: "shall" as const, notes: "Items must be detected, geotagged, and reported." },
    { id: "R06", text: "Upon PLB activation (5–15 min into search), redirect to Focus Area (3–10 GPS coords).", severity: "shall" as const, notes: "Teams receive Focus Area coords mid-flight." },
    { id: "R07", text: "Land within 10m but NOT within 5m of casualty, deploy first aid kit, return to TOL.", severity: "shall" as const, notes: "Tarot payload release mechanism. 7.5m offset = center of 5–10m zone." },
    { id: "R08", text: "Autonomy level and interface format determined and justified by Company.", severity: "shall" as const, notes: "We chose L2 semi-autonomous with browser dashboard." },
    { id: "R09", text: "All interfaces shall include RTH and Motor Cutoff commands + failsafes.", severity: "shall" as const, notes: "RC kill switch (STABILIZE), RTL button, link-loss failsafe." },
    { id: "R10", text: "Report lat/lon and images of all items of interest AND the casualty.", severity: "shall" as const, notes: "Detection log + saved images with GPS metadata." },
    { id: "R11", text: "Designated Company Pilot, supervised by Flight Lab Safety Pilot.", severity: "shall" as const, notes: "Safety Pilot has ultimate authority over all operations." },
    { id: "R12", text: "All software and flight logs on public GitHub (MIT licence).", severity: "shall" as const, notes: "https://github.com/DimaChup/Group_Proj" },
  ],

  constraints: [
    { label: "Max Altitude 50m", description: "The brief specifies 50m AGL maximum, not the general 120m legal limit. Operating at 30m search, 15m verify.", severity: "critical" as const },
    { label: "RC Kill Switch", description: "Pilot can override to STABILIZE/LOITER at ANY time via RC. Non-negotiable safety requirement (R09).", severity: "critical" as const },
    { label: "Visual Line of Sight", description: "Drone must remain within pilot's VLOS at all times (R09). Regulatory and brief requirement.", severity: "critical" as const },
    { label: "SSSI No-Fly Zone", description: "Site of Special Scientific Interest within search area. Must be geofenced and avoided (R02).", severity: "critical" as const },
    { label: "Landing Zone", description: "Must land within 10m but NOT within 5m of detected person (R07). Not directly on top (propwash risk). 7.5m offset = center of safe zone.", severity: "warning" as const },
    { label: "PLB Redirect Mid-Search", description: "PLB signal arrives during search. Drone must redirect to PLB Focus Area (R06).", severity: "warning" as const },
    { label: "Battery Life", description: "~15-20 min flight time. Mission must complete within one battery.", severity: "warning" as const },
    { label: "GPS Required", description: "3D GPS fix (fix_type >= 3) required before arming. Min 8 satellites recommended.", severity: "critical" as const },
  ],

  successCriteria: [
    { label: "Person detected from air", metric: "CV detects dummy from search altitude (15-30m)" },
    { label: "SSSI avoided", metric: "Drone never enters no-fly zone geofence" },
    { label: "PLB redirect works", metric: "Drone redirects to focus area on PLB signal" },
    { label: "Position estimated", metric: "GPS estimate within 5m of actual position" },
    { label: "Landed in zone", metric: "Within 10m but NOT within 5m of target, no damage" },
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
  { name: "Global Shutter Camera", role: "Vision Sensor", details: "IMX296 sensor, 1456x1088, BGR output. Global shutter = no rolling shutter artifacts. ~4.8 FPS with TFLite.", status: "verified" as const, specUrl: "" },
  { name: "6mm CS-Mount Lens", role: "Optics", details: "6mm focal length lens for the global shutter camera. FOV suitable for 15-30m search altitude.", status: "verified" as const, specUrl: "" },
  { name: "FrSky Twin X14", role: "RC Transmitter", details: "Pilot's controller. Kill switch mapped to mode channel (STABILIZE). Always has override priority.", status: "verified" as const, specUrl: "" },
  { name: "Tarot Payload Release", role: "Delivery Mechanism", details: "Servo-actuated payload release for first aid kit delivery (R07). Triggered via MAVLink servo command.", status: "todo" as const, specUrl: "" },
  { name: "SanDisk MicroSD", role: "Storage", details: "For flight logs, detection images, mission data. Pi and Cube both have SD cards.", status: "verified" as const, specUrl: "" },
  { name: "YOLOv8n TFLite", role: "AI Model", details: "Retrained on 366 real+synthetic images (mAP50=0.995). ~207ms inference on Pi (4.8 FPS). 0.966 confidence on bench test.", status: "verified" as const, specUrl: "" },
  { name: "mavproxy", role: "MAVLink Router", details: "Bridges Cube serial (TELEM2) to UDP (Pi scripts) + TCP (Mission Planner). Runs as service on Pi.", status: "verified" as const, specUrl: "https://ardupilot.org/mavproxy/" },
  { name: "Rangefinder / LiDAR", role: "AGL Altitude Sensor", details: "Measures true Above Ground Level altitude via laser or ultrasonic pulse. Provides accurate height data independent of barometer or GPS altitude, critical for precision landing in the 5-10m offset zone.", status: "todo" as const, specUrl: "" },
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
      "Lands manually within 10m but NOT within 5m of target (R07)",
      "Can abort at any time (RC to STABILIZE)",
    ],
    scripts: [
      { name: "tests/flight/1_passive_flight.py", purpose: "Passive CV during manual RC flight — zero commands sent" },
      { name: "tests/diagnostics/camera_stream.py", purpose: "MJPEG video stream to browser (optional)" },
    ],
    whatsWorking: [
      "Camera + AI detection on Pi (tested, 4.8 FPS)",
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
    description: "Drone autonomously takes off, flies a lawnmower search over the area while avoiding the SSSI geofence (R02). When CV detects a person, pilot is alerted. On PLB signal (R06), drone redirects to Focus Area. Pilot classifies: Y=target, I=interest, X=false positive. Confirmed target: drone centres, descends, lands within 10m but NOT within 5m (R07), releases first aid kit via Tarot (R07). Pilot has RC override at all times (R09).",
    droneActions: [
      "Arms and takes off autonomously (GUIDED mode)",
      "Flies lawnmower search pattern, avoids SSSI geofence (R02)",
      "CV runs continuously, builds GPS estimate of detections",
      "Spatial clustering groups nearby detections",
      "Redirects to PLB Focus Area on signal (R06)",
      "On pilot command (N): flies to estimated position, descends to 15m",
      "Sends detection image + GPS to pilot's browser dashboard",
      "On confirm (Y): centres on target, locks GPS estimate",
      "On land (L): flies to 7.5m offset (within 10m, NOT within 5m), auto-lands, releases payload (R07)",
      "RTL on command, battery low, or RC failsafe (R09)",
    ],
    pilotActions: [
      "Defines search polygon on map (before flight)",
      "Monitors flight on Mission Planner + pi_flight.py dashboard",
      "Reviews detection images when drone alerts",
      "Classifies: Y (dummy), I (interest), X (false positive)",
      "Commands: N (investigate), L (land), M (resume search)",
      "RC override available at all times — STABILIZE = instant stop (R09)",
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
      "SSSI geofence implementation (R02)",
      "PLB redirect logic (R06)",
      "Tarot payload release integration (R07)",
      "Outdoor GPS accuracy validation",
      "Detection performance from altitude (30m search alt)",
      "pi_flight.py not yet tested on real Pi hardware",
    ],
    flightSteps: [1, 2, 3, 4, 5],
    stateFlow: "ARM -> TAKEOFF -> SEARCH (avoid SSSI) -> DETECT -> pilot N -> INVESTIGATE -> pilot Y -> CENTRE -> DESCEND -> pilot L -> LAND (7.5m offset) + PAYLOAD -> RTL",
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
      "RC override available — STABILIZE = instant stop (R09)",
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
  { id: "l2-1", level: 2, name: "Waypoint test script", status: "ready", description: "2_waypoint_test.py: arm, takeoff, fly 4 waypoints, land. No CV.", depends: ["l1-2"] },
  { id: "l2-2", level: 2, name: "Autonomous search pattern", status: "todo", description: "main.py flies lawnmower pattern autonomously with CV logging only", depends: ["l2-1", "l1-4"] },
  { id: "l2-3", level: 2, name: "pi_flight.py on real Pi", status: "todo", description: "Test browser dashboard, video stream, commands on actual Pi hardware", depends: ["l1-3"] },
  { id: "l2-4", level: 2, name: "SSSI geofence (R02)", status: "todo", description: "Implement no-fly zone exclusion in search pattern and navigation", depends: ["l2-1"] },
  { id: "l2-5", level: 2, name: "PLB redirect (R06)", status: "todo", description: "Mid-search redirect to PLB Focus Area on simulated signal", depends: ["l2-2"] },
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

// ═══════════════════════════════════════════════════════════
// L2 Stepping Stones — Critical path + parallel fine-tuning
// ═══════════════════════════════════════════════════════════

export interface IfScenario {
  condition: string;   // "If geotagging from flyover is accurate enough (<3m error)"
  outcome: string;     // "Skip centering step — go straight to search"
  affectedSteps?: string[];  // IDs of steps that get skipped/changed
}

export interface SteppingStone {
  id: string;
  name: string;
  description: string;
  script?: string;
  scriptArgs?: string;
  status: "done" | "ready" | "todo" | "blocked";
  proves: string;  // what this step proves/validates
  requires?: string[];  // what must work before this
  output?: string;  // what you get from running this
  row: number;  // steps with same row number can happen in parallel (shown side by side)
  ifScenarios?: IfScenario[];  // conditional branches based on results
}

export interface ParallelTask {
  id: string;
  name: string;
  description: string;
  script?: string;
  status: "done" | "ready" | "todo";
  category: "calibration" | "accuracy" | "tuning" | "data";
  output?: string;
  dependsOn?: string; // optional: must follow another parallel task
}

/** Critical path: sequential steps that build up to the full L2 mission.
 *  Steps on the same row can happen in parallel (shown side by side).
 *  ifScenarios show conditional branches — what changes based on results. */
export const L2_CRITICAL_PATH: SteppingStone[] = [
  // ── Row 1: Foundation ──
  {
    id: "cp-1", name: "All components healthy", row: 1,
    description: "Run preflight diagnostics on Pi. Camera gives frames, Cube responds to heartbeat, AI model loads, GPS module reports (even without outdoor fix). Also run bench tests: tests/flight/0a_cube_commands.py (mode + arm), tests/flight/0b_bench_mission.py (full command sequence, no props), tests/flight/0c_feedback_test.py (vision→GPS pipeline). On laptop: rehearse in simple_simulator.py to verify the full UI loop before touching hardware.",
    script: "preflight.py", scriptArgs: "Also: 0a_cube_commands.py, 0b_bench_mission.py, 0c_feedback_test.py", status: "done",
    proves: "Every subsystem talks to every other subsystem.",
    output: "PASS/FAIL per subsystem. If anything fails, fix before proceeding.",
  },

  // ── Row 2: GPS baseline ──
  {
    id: "cp-2", name: "Outdoor GPS 3D fix", row: 2,
    description: "Take Pi + Cube outside. Wait for 3D satellite lock (fix_type ≥ 3, >8 sats, HDOP <2). Verify coordinates match known location on map. Run tests/hardware/gps_test.py for continuous tracking, then tests/hardware/gps_health.py for step-by-step verification. Also run tests/day_1_experiments/gps_drift.py for stationary noise floor (CEP50/CEP95) — do this while waiting anyway. Compare lat/lon against TAKEOFF_LOCATION in config.py (51.4234, -2.6714).",
    script: "tests/hardware/gps_test.py", scriptArgs: "Also: gps_health.py, gps_drift.py (stationary)", status: "todo",
    proves: "GPS works outdoors. We have real coordinates to work with.",
    requires: ["cp-1"],
    output: "Fix type, sat count, HDOP, lat/lon vs known position. Stationary drift CEP50/CEP95.",
  },

  // ── Row 3: Safest first flight (no custom code) ──
  {
    id: "cp-2a", name: "Mission Planner AUTO waypoints", row: 3,
    description: "Upload a simple 4-waypoint square pattern in Mission Planner at 10-15m altitude. Switch to AUTO on RC — drone flies the pattern and RTLs. Your code is NOT involved — this is pure Cube + GPS + motors + Mission Planner. Proves the aircraft actually flies safely before adding any Python code. This is STEP 1 in docs/FLIGHT_DAY_CHECKLIST.md. Also verify: RC kill switch works mid-flight (switch to STABILIZE on RC — does it stop immediately?). If this fails, do not proceed to any autonomous code.",
    status: "todo",
    proves: "The aircraft flies, GPS navigation works, Cube is configured correctly, RTL works. RC kill switch is reliable.",
    requires: ["cp-2"],
    output: "Drone completed 4-waypoint pattern and returned. RC override tested mid-flight. Flight log reviewed in Mission Planner.",
    ifScenarios: [
      { condition: "If drone flies pattern but drifts badly", outcome: "Tune PID/WPNAV params in Mission Planner before proceeding." },
      { condition: "If RC kill switch doesn't respond instantly", outcome: "STOP. Fix RC override before any autonomous code runs. Safety-critical." },
    ],
  },

  // ── Row 4: Two independent first flights with code ──
  {
    id: "cp-3", name: "Manual flight + CV check", row: 4,
    description: "Pilot flies manually on RC over the dummy at search altitude (15-30m). Pi runs camera + AI passively — sends ZERO commands. Logs every detection with GPS, confidence, altitude. Live video stream at http://PI_IP:8090. Review: did it see the dummy? At what altitude? How often? Any false positives? Can also use passive_watch.py (saves detection photos + JSON metadata automatically). Run tests/day_1_experiments/altitude_sweep.py and speed_sweep.py alongside this flight to collect structured CSV data — saves battery by combining experiments. On laptop: rehearse detection flow in simple_simulator.py (--fps 4 --tflite to match Pi performance).",
    script: "passive_watch.py or tests/flight/1_passive_flight.py", scriptArgs: "--headless --stream (Pi). Also: altitude_sweep.py, speed_sweep.py alongside", status: "todo",
    proves: "CV actually works from the air, not just on the bench. Detection altitude range known.",
    requires: ["cp-2a"],
    output: "Detection rate per altitude. Max reliable detection altitude. Confidence levels. False positive count. Saved detection images.",
    ifScenarios: [
      { condition: "If detection only works below 15m", outcome: "Lower TARGET_ALT in config.py. Search takes longer but detections are reliable." },
      { condition: "If too many false positives", outcome: "Raise confidence threshold or swap to human.tflite model." },
    ],
  },
  {
    id: "cp-4", name: "Fly GPS waypoints + RC override", row: 4,
    description: "Drone arms, takes off to 10m, flies 3-4 GPS waypoints in GUIDED mode, lands. No camera, no AI, no decisions. Waypoints loaded from waypoints.json (draw on laptop with tests/flight/draw_waypoints.py). Also test: mid-waypoint, pilot switches to STABILIZE on RC — does it stop immediately? Pre-reqs: verify with tests/flight/0a_cube_commands.py (mode switch, arm/disarm) and 0b_bench_mission.py (full command sequence on bench, no props) before attempting real flight. Use main.py --dry-run to visualize the waypoint pattern on map.jpg without flying.",
    script: "tests/flight/2_waypoints.py", scriptArgs: "Loads waypoints.json. Pre-test: 0a + 0b on bench. Dry-run: main.py --dry-run", status: "todo",
    proves: "Our MAVLink commands make the drone fly to GPS coordinates. RC override works as safety net.",
    requires: ["cp-2a"],
    output: "Drone visited all waypoints and returned. RC override tested. Flight log confirms GPS accuracy.",
  },

  // ── Row 4: Position accuracy + standalone geofence test ──
  {
    id: "cp-5", name: "Geotagging from flyover", row: 5,
    description: "Fly over dummy (don't stop). CV estimates dummy GPS position from detection frames using pixel→GPS math (GeoTransformer in utils.py). Compare estimate vs actual dummy position. This is geotagging 'from the side' — the drone doesn't centre, just flies past. Run tests/day_1_experiments/gps_accuracy.py for structured CSV data. Depends on correct FOCAL_LENGTH_MM and SENSOR_WIDTH_MM in config.py (set in pt-fov calibration). On laptop: rehearse in simple_simulator.py — fly over targets with C key (GPS centering mode), check scatter plot accuracy.",
    script: "tests/calibration/gps_ground_truth.py", scriptArgs: "Also: gps_accuracy.py for CSV. Simulator: simple_simulator.py + C key", status: "todo",
    proves: "Pixel→GPS conversion accuracy from a moving flyover. Can we geotag without stopping?",
    requires: ["cp-3"],
    output: "GPS estimate error in metres from flyover. Multiple passes at different altitudes. CSV data for report.",
    ifScenarios: [
      { condition: "If flyover geotagging is accurate (<3m error)", outcome: "May not need centering step at all — just geotag and land at offset. Faster mission." },
      { condition: "If flyover error is 5-10m", outcome: "Need centering (cp-6) to refine position before landing." },
      { condition: "If flyover error is >10m", outcome: "Camera calibration is off. Run FOV calibration (parallel task) before continuing." },
    ],
  },
  {
    id: "cp-6", name: "CV centering accuracy", row: 5,
    description: "Hover above dummy, use visual servo to centre drone directly over target (V key = visual servo mode in pi_flight.py or simple_simulator.py). Record drone's GPS when centred — this is the 'centred geotag'. Compare with flyover estimate (cp-5). Which is more accurate? This is an integrated experiment: side-view vs top-down geotagging. Also tests the auto-investigate flow from pi_flight.py: press N in browser → drone flies to estimate → CV auto-refines. Monitor live at http://PI_IP:8090. On laptop: rehearse in simple_simulator.py — press V (visual servo) then G (GPS lock) to test centering accuracy on scatter plot.",
    script: "tests/flight/4_detect_and_center.py", scriptArgs: "Also: pi_flight.py (N→auto-investigate). Simulator: V + G keys", status: "todo",
    proves: "CV centering works in real flight. Centred position is more accurate than flyover estimate.",
    requires: ["cp-3", "cp-4"],
    output: "Centred GPS vs actual. Flyover GPS vs actual. Error comparison. Decide: do we need centering or is flyover enough?",
    ifScenarios: [
      { condition: "If centering gives <2m accuracy", outcome: "Use centering as primary approach. Flyover geotag is just the initial estimate to fly toward." },
      { condition: "If centering works really well AND flyover is poor", outcome: "Skip flyover geotagging in mission — go straight to centering on every detection.", affectedSteps: ["cp-5"] },
      { condition: "If both are similar accuracy", outcome: "Use flyover only (faster, no need to stop and centre). Skip centering in mission flow." },
    ],
  },
  {
    id: "cp-6b", name: "Test geofence standalone", row: 5,
    description: "Upload SSSI polygon as exclusion fence in ArduCopter via Mission Planner (Fence tab → polygon exclusion). SSSI coordinates in config.py SSSI_GPS. Fly the drone toward the SSSI boundary deliberately in LOITER/GUIDED mode. Does it stop? Does it BRAKE/LOITER at the edge? How close does it get before refusing? Key ArduCopter params: FENCE_ENABLE=1, FENCE_TYPE=7, FENCE_ACTION (RTL or BRAKE). This is a standalone test — no search pattern, no CV, just proving the fence works. Research inclusion vs exclusion fences in ArduCopter docs.",
    status: "todo",
    proves: "ArduCopter geofence exclusion actually prevents the drone from entering SSSI. We know the behaviour at the boundary.",
    requires: ["cp-4"],
    output: "Closest GPS point to SSSI boundary. Drone behaviour at edge (BRAKE/LOITER/bounce back). Config params that worked.",
    ifScenarios: [
      { condition: "If ArduCopter native exclusion fence works reliably", outcome: "Use it as-is. Just upload polygon and trust the firmware. Row 8 integration becomes trivial." },
      { condition: "If fence is flaky or overshoots into SSSI", outcome: "Add software buffer (shrink SSSI polygon by 5-10m). Or implement in-code check as backup." },
      { condition: "If exclusion fence not supported in our ArduCopter version", outcome: "Must implement entirely in software: check every waypoint + runtime position against SSSI polygon." },
    ],
  },

  // ── Row 5: Search pattern alone ──
  {
    id: "cp-7", name: "Fly search pattern (no CV action)", row: 6,
    description: "Drone flies the full lawnmower search pattern autonomously over the search area. CV may be running and logging, but it does NOT trigger any behaviour — no investigating, no stopping. Drone completes the pattern and comes home. Search area from search_area.json (draw on laptop with tests/flight/draw_search_area.py, or use SEARCH_AREA_GPS from config.py). Preview pattern with main.py --dry-run (shows lawnmower on map, no Cube needed). Key config: TARGET_ALT (search altitude), SEARCH_SPEED_MPS, planning.py overlap %. Stream at http://PI_IP:8090 if using --headless --stream. Live coverage overlay: tests/flight/live_map.py on laptop.",
    script: "main.py", scriptArgs: "--headless --stream (Pi). Preview: main.py --dry-run. Draw area: draw_search_area.py", status: "todo",
    proves: "Autonomous lawnmower pattern works in the real world. Drone can fly a search area and come home.",
    requires: ["cp-3", "cp-4"],
    output: "Complete flight log. Lawnmower coverage map. Any CV detections logged but not acted on.",
    ifScenarios: [
      { condition: "If search pattern misses edges or has gaps", outcome: "Tune overlap percentage in planning.py. May need tighter lawnmower spacing." },
      { condition: "If drone drifts off waypoints in wind", outcome: "Check WPNAV parameters. May need to reduce search speed for accuracy." },
    ],
  },

  // ── Row 6: Search + detect dummy + pilot Y/X ──
  {
    id: "cp-8", name: "Search + detect dummy + confirm (Y/X)", row: 7,
    description: "Now CV is active during search. When it detects something, drone auto-geotags it and flies to the estimated position (GUIDED). CV centering auto-refines position as drone approaches. At VERIFY_ALT (15m), pilot sees live feed on browser (http://PI_IP:8090) and decides: Y=it's the dummy, X=false positive. On Y → proceed to landing. On X → estimate resets, drone resumes search. Simple binary decision — just dummy or not. No items of interest yet. Use pi_flight.py for browser dashboard (N=investigate, Y=confirm, X=reject buttons). On laptop: full rehearsal in simple_simulator.py — place one dummy, fly lawnmower, press N to investigate, Y/X to classify. Use main.py --dry-run to verify search pattern first.",
    script: "pi_flight.py + main.py", scriptArgs: "--headless --stream (Pi). Browser: Y/X buttons. Simulator: simple_simulator.py full loop", status: "todo",
    proves: "Core detect→investigate→confirm loop works. Pilot can see detections and decide. CV centering refines position automatically.",
    requires: ["cp-5", "cp-6", "cp-7"],
    output: "Detection events with Y/X classifications. Centred GPS vs flyover GPS comparison. False positive rate.",
    ifScenarios: [
      { condition: "If too many false positives interrupt the search", outcome: "Raise confidence threshold. Or require N consecutive detections before auto-investigating." },
      { condition: "If auto-investigate + centering gives great accuracy", outcome: "Centering IS the geotag. Simplifies pipeline." },
      { condition: "If pilot override + return to GUIDED works smoothly", outcome: "Semi-autonomy validated. Pilot trusts the system." },
    ],
  },

  // ── Row 7: Landing + payload delivery ──
  {
    id: "cp-9", name: "Offset landing + payload delivery", row: 8,
    description: "After Y confirmation: drone flies to 7.5m offset (operator picks direction), descends. Two approaches: (A) Full landing at offset, release payload on ground. (B) Rangefinder descent to ~1m AGL, drop payload mid-air, climb back up. Option B avoids tricky terrain. Wire Tarot servo to Cube AUX port, trigger with MAV_CMD_DO_SET_SERVO. In pi_flight.py: press L button for landing sequence. On laptop: rehearse offset landing in simple_simulator.py — press L key to land 7.5m from target, see landing accuracy on scatter plot. Test servo command independently on bench first (tests/flight/0a_cube_commands.py can be extended for servo test).",
    script: "pi_flight.py", scriptArgs: "L button → offset landing. Servo: MAV_CMD_DO_SET_SERVO. Simulator: L key", status: "todo",
    proves: "R07 compliance — payload delivered within 5-10m zone. Landing or hover-drop works.",
    requires: ["cp-8"],
    output: "Measured distance from dummy to delivery point. Must be 5-10m. Payload released cleanly.",
    ifScenarios: [
      { condition: "If rangefinder available + working", outcome: "Use hover-drop at 1m AGL. Safer on uneven terrain. Rangefinder gives true ground distance." },
      { condition: "If no rangefinder or unreliable", outcome: "Full landing at 7.5m offset. Barometric altitude only (relative to launch, not terrain)." },
      { condition: "If terrain is flat at test site", outcome: "Either approach works. Test both, pick the more reliable one." },
    ],
  },

  // ── Row 8: Add PLB focused search ──
  {
    id: "cp-10", name: "PLB focused search redirect", row: 9,
    description: "Mid-search, simulate PLB signal (button press in pi_flight.py browser dashboard, or timed trigger at 5-15 min). Drone abandons current lawnmower, receives 3-10 GPS coords defining a smaller Focus Area (FOCUS_AREA_GPS in config.py, or from brief's example polygon). planning.py generates new lawnmower over Focus Area. Still only looking for the dummy (Y/X). Focus Area coordinates from AENGM0074.kml — see FLIGHT_ZONES in mission-data.ts for the exact polygon. Can test PLB redirect in simple_simulator.py if trigger is added.",
    status: "todo",
    proves: "R06 compliance — drone redirects to PLB Focus Area on signal. Search + detect still works in new area.",
    requires: ["cp-8"],
    output: "Drone re-routes mid-search. Log shows transition point. New pattern covers Focus Area. Dummy still detected + confirmed.",
  },

  // ── Row 9: Add items of interest (Y/I/X) ──
  {
    id: "cp-11", name: "Add items of interest (Y/I/X)", row: 10,
    description: "Now the field has scattered objects — not just the dummy. Pilot classification expands from Y/X to Y/I/X: Y=dummy (land near it), I=item of interest (log GPS + photo, resume search), X=false positive (discard, resume). Items of interest get geotagged and reported (R10). In pi_flight.py browser: Y/I/X buttons available during investigation hover. Items of interest appear as cyan markers on the 2D GPS grid. In simple_simulator.py: already fully implemented — place multiple targets, classify each with Y/I/X keys, see IOI markers on god view + scatter plot. Use capture_training.py (http://PI_IP:8091) alongside to save photos of every detected object for later review.",
    script: "pi_flight.py + main.py", scriptArgs: "Browser: Y/I/X buttons. Simulator: Y/I/X keys (already working). capture_training.py alongside", status: "todo",
    proves: "Full classification workflow. Items of interest logged with GPS and images. Pilot can distinguish between targets.",
    requires: ["cp-10"],
    output: "Detection log with Y/I/X classifications. Items of interest with GPS + saved images (R10). Dummy confirmed separately.",
    ifScenarios: [
      { condition: "If pilot struggles to distinguish from 15m altitude", outcome: "Add zoom/crop of detection box on dashboard. Or descend lower (10m) for investigation." },
      { condition: "If items of interest and dummy look identical to CV", outcome: "Expected — CV detects, human classifies. This is the L2 design (semi-autonomous)." },
    ],
  },

  // ── Row 10: Add SSSI geofence ──
  {
    id: "cp-12", name: "SSSI geofence in search", row: 11,
    description: "Now that standalone geofence works (cp-6b), integrate it into the full search. Lawnmower pattern from planning.py must skip waypoints inside SSSI (SSSI_GPS in config.py). If search area spans both sides of SSSI, drone needs a path AROUND the no-fly zone. Verify: full search completes with zero GPS points inside SSSI. Also test: what if a detection is near/inside SSSI? Drone should not enter to investigate — add buffer zone. Preview with main.py --dry-run to see which waypoints fall inside SSSI before flying. Use tests/flight/live_map.py to overlay SSSI boundary on real-time position.",
    status: "todo",
    proves: "R02 compliance in a real search mission. Everything works together: search + detect + classify + avoid SSSI.",
    requires: ["cp-6b", "cp-11"],
    output: "Flight log shows full search coverage with zero SSSI incursions. Path-around-fence works. Detections near SSSI handled safely.",
    ifScenarios: [
      { condition: "If lawnmower generator can trim SSSI waypoints automatically", outcome: "Clean integration. planning.py handles it. No runtime overhead." },
      { condition: "If drone needs to navigate around SSSI mid-search", outcome: "Add waypoint routing around SSSI polygon. More complex but necessary." },
      { condition: "If detection occurs near SSSI boundary", outcome: "Add buffer zone — don't investigate detections within Xm of SSSI edge." },
    ],
  },

  // ── Row 11: Full integrated mission ──
  {
    id: "cp-13", name: "Full L2 mission", row: 12,
    description: "Everything combined end-to-end: takeoff → lawnmower search (avoid SSSI) → CV detects → pilot classifies (Y/I/X) → items of interest geotagged + reported → PLB redirect to Focus Area → find dummy → centre → land/hover at offset → deploy payload → RTL. The complete semi-autonomous mission as described in the AENGM0074 brief. Run main.py --headless --stream on Pi + pi_flight.py for browser dashboard at http://PI_IP:8090. Preview full mission with main.py --dry-run first. Monitor with tests/flight/live_map.py on laptop. Log everything with tests/day_1_experiments/detection_log.py alongside for report data. Final checks: docs/FLIGHT_DAY_CHECKLIST.md (printable, follow top to bottom), docs/PREFLIGHT_CHECKLIST.md.",
    script: "main.py + pi_flight.py", scriptArgs: "--headless --stream (Pi). --dry-run to preview. Checklist: FLIGHT_DAY_CHECKLIST.md", status: "todo",
    proves: "Level 2 complete. All requirements (R01-R12) addressed in a single flight.",
    requires: ["cp-9", "cp-10", "cp-11", "cp-12"],
    output: "Complete flight log. Detection images. Items of interest with GPS. Landing accuracy. Payload delivered. Mission success.",
  },
];

/** Milestones: purple horizontal markers between rows in the critical path.
 *  afterRow = the row number AFTER which this milestone appears. */
export interface Milestone {
  afterRow: number;
  label: string;
  detail: string;
}

export const L2_MILESTONES: Milestone[] = [
  {
    afterRow: 2,
    label: "All components are working and talking to each other",
    detail: "Camera, Cube, AI model, GPS with outdoor 3D fix — every subsystem verified. Hardware integration complete. Ready to fly.",
  },
  {
    afterRow: 5,
    label: "We can reliably geotag a dummy from the air",
    detail: "Geotagging, centering, and geofence boundary all validated. Position accuracy known. Ready to build the full search loop on top of this foundation.",
  },
  {
    afterRow: 8,
    label: "We can find, confirm, and deliver to a target",
    detail: "Search + detect dummy + pilot confirms + land at offset + payload released. The core mission works. Remaining steps layer on PLB redirect, items of interest, and SSSI avoidance.",
  },
];

/** Parallel tasks: can happen alongside critical path steps.
 *  These improve accuracy and confidence but don't block the main sequence. */
export const L2_PARALLEL_TASKS: ParallelTask[] = [
  // Calibration
  {
    id: "pt-fov", name: "Calibrate FOV (focal length + sensor width)",
    description: "Measure real camera FOV with ruler at known height. Calculate correct FOCAL_LENGTH_MM and SENSOR_WIDTH_MM for config.py. Directly affects GPS estimation accuracy (GeoTransformer in utils.py uses these). Done on bench — can re-verify from altitude later with alt_test.py. Also: tests/calibration/fov_test_simple.py for a quick single measurement.",
    script: "tests/calibration/fov_calibrate.py",
    status: "done", category: "calibration",
    output: "Updated FOCAL_LENGTH_MM and SENSOR_WIDTH_MM values for config.py.",
  },
  {
    id: "pt-lens", name: "Lens distortion calibration",
    description: "Print checkerboard, capture from multiple angles. Generate undistortion matrix. Fixes barrel/pincushion at frame edges — improves geotagging accuracy for edge detections. Done on bench — can recalibrate with more samples later.",
    script: "tests/calibration/lens_calibrate.py",
    status: "done", category: "calibration",
    output: "calibration_data.npz file. Undistortion matrix for vision.py.",
  },
  {
    id: "pt-alt-fov", name: "Real-altitude FOV verification",
    description: "Hover at known altitude, measure visible ground area on camera. Compare with calculated FOV. Confirms bench calibration is correct at flight altitude.",
    script: "tests/calibration/alt_test.py",
    status: "todo", category: "calibration",
    dependsOn: "pt-fov",
    output: "Verified FOV at altitude. Corrections if bench values were off.",
  },

  // Accuracy measurements
  {
    id: "pt-gps-drift", name: "GPS noise floor (stationary drift)",
    description: "Drone sits still for 60s on ground. Log GPS every 0.25s. Measure std dev, max drift. This is the baseline error — our GPS estimate can never be better than this.",
    script: "tests/day_1_experiments/gps_drift.py",
    status: "todo", category: "accuracy",
    output: "CEP50, CEP95 in metres. Typical: 1-3m drift.",
  },
  {
    id: "pt-gps-hover", name: "GPS drift in hover",
    description: "Hover at 15m and 30m for 30s each. Log GPS. Measure position drift while airborne. Wind + vibration may make it worse than ground.",
    script: "tests/day_1_experiments/gps_drift.py",
    status: "todo", category: "accuracy",
    dependsOn: "pt-gps-drift",
    output: "Hover drift at different altitudes. Informs landing offset margin.",
  },
  {
    id: "pt-gps-accuracy", name: "GPS estimation error vs ground truth",
    description: "Fly over dummy at multiple altitudes. Compare CV's GPS estimate with known dummy position. Measures full pipeline error: camera + AI + GSD + Kalman.",
    script: "tests/day_1_experiments/gps_accuracy.py",
    status: "todo", category: "accuracy",
    output: "Error in metres per altitude. Determines if 7.5m offset is safe.",
  },

  // Tuning
  {
    id: "pt-pi-fps", name: "Pi inference FPS benchmark",
    description: "Run TFLite model on Pi with real camera frames. Bench result: 207ms / 4.8 FPS with TFLite. Done for TFLite — can revisit with NCNN backend (3x faster expected) or different resolution.",
    script: "tests/hardware/benchmark.py",
    status: "done", category: "tuning",
    output: "207ms / 4.8 FPS TFLite on Pi 5. Next: try NCNN (~12 FPS expected) or reduce resolution.",
  },
  {
    id: "pt-altitude-sweep", name: "Detection rate vs altitude",
    description: "Hover at 10m, 15m, 20m, 25m, 30m (30s each). Log detection rate and confidence at each altitude. Find max reliable detection altitude.",
    script: "tests/day_1_experiments/altitude_sweep.py",
    status: "todo", category: "tuning",
    output: "Detection rate + confidence per altitude bucket. Informs TARGET_ALT in config.py.",
  },
  {
    id: "pt-speed-sweep", name: "Detection rate vs speed + blur",
    description: "Fly over dummy at 3, 5, 7, 10 m/s. Measure detection rate and motion blur metric (Laplacian variance). Find max speed where detection still works. Global shutter helps but blur from movement is still possible.",
    script: "tests/day_1_experiments/speed_sweep.py",
    status: "todo", category: "tuning",
    output: "Detection rate + blur metric per speed. Informs SEARCH_SPEED_MPS in config.py. Blur threshold for reliable detection.",
  },
  {
    id: "pt-model-compare", name: "Compare all TFLite models",
    description: "Run benchmark on all models in models/ folder: custom_yolov8n.tflite (dummy detector), human.tflite (COCO person, 80 classes, 13MB backup), best2.tflite (placeholder for retrained). Compare speed, detection rate, confidence. Pick best for flight day. Swap active model: cp models/X.tflite best.tflite (or use main.py --model models/X.tflite). On Pi: also try with different resolutions (pt-resolution-tradeoff).",
    script: "tests/day_1_experiments/model_compare.py",
    status: "todo", category: "tuning",
    output: "Table: model x speed x detection rate x confidence. Best model → best.tflite.",
  },
  {
    id: "pt-conf-threshold", name: "Tune confidence threshold",
    description: "After altitude/speed sweeps: review detection CSV data. If too many misses → lower threshold (0.25-0.3). If too many false positives → raise (0.5+). Current threshold: 0.4 in vision.py. Update config.py CONFIDENCE_THRESHOLD. Use tests/day_1_experiments/detection_log.py for a catch-all logger to review all detections.",
    status: "todo", category: "tuning",
    dependsOn: "pt-altitude-sweep",
    output: "Optimal CONFIDENCE_THRESHOLD value for real conditions.",
  },

  // Data collection
  {
    id: "pt-training-data", name: "Capture real training images",
    description: "16 real frames labelled from DJI video + 300 synthetic + 50 negatives at 1456x1088 (dataset_v2/)",
    script: "capture_training.py",
    status: "done", category: "data",
    output: "dataset_v2/ with 366 images (300 syn + 16 real + 50 neg) at 1456x1088. Ready for Colab.",
  },
  {
    id: "pt-stream-latency", name: "Test video stream latency",
    description: "Run pi_flight.py on Pi, open http://PI_IP:8090 on laptop. Measure delay between real event (wave hand in front of camera) and browser display. Critical for operator's Y/I/X classification in real time. Also test: tests/diagnostics/camera_stream.py (basic MJPEG), camera_stream_fast.py (threaded), camera_stream_h264.py (H.264/HLS via FFmpeg). Compare latency of each approach.",
    script: "pi_flight.py",
    status: "todo", category: "data",
    output: "Latency in ms. If >500ms, consider reducing resolution or quality.",
  },

  // Tuning (additional)
  {
    id: "pt-ncnn-backend", name: "Try NCNN inference backend",
    description: "NCNN confirmed 3x faster than TFLite on Pi 5 (~83ms vs 250ms). Export model to NCNN format, integrate as vision.py backend option. Caveat: Ultralytics v8.4.0+ blocked NCNN on ARM64 — may need older version or standalone ncnn lib.",
    status: "todo", category: "tuning",
    dependsOn: "pt-pi-fps",
    output: "NCNN FPS on Pi. If 10+ FPS, make it the default backend.",
  },
  {
    id: "pt-resolution-tradeoff", name: "Resolution vs FPS vs detection",
    description: "Test 320x240, 640x480, 800x600 on Pi. For each: measure FPS, detection rate, detection distance. Lower resolution = faster but may miss detections from altitude. Find the sweet spot.",
    script: "tests/hardware/benchmark.py",
    status: "todo", category: "tuning",
    output: "Table: resolution x FPS x detection rate. Optimal IMAGE_W/IMAGE_H for config.py.",
  },

  // Accuracy (additional)
  {
    id: "pt-rangefinder-accuracy", name: "Rangefinder accuracy test",
    description: "If rangefinder/lidar available: measure AGL at known heights (1m, 5m, 10m, 15m). Compare with barometric alt. Test over different surfaces (grass, concrete, water). This determines if hover-drop landing is viable.",
    status: "todo", category: "accuracy",
    output: "Rangefinder error vs actual height. Surface-dependent accuracy. Max reliable range.",
  },
  {
    id: "pt-battery-endurance", name: "Battery endurance profiling",
    description: "Time a full flight from takeoff to low-battery RTL. Measure at different speeds and with/without payload. Mission must complete within one battery (~15-20 min expected). This sets the time budget for search pattern size.",
    status: "todo", category: "accuracy",
    output: "Flight time at cruise speed. Time with payload. Safe margin for RTL reserve.",
  },

  // Data (additional)
  {
    id: "pt-comms-range", name: "Wi-Fi + video stream range test",
    description: "Walk away from Pi with laptop, measure video stream quality and latency at 50m, 100m, 200m, 300m. Find the max reliable range. If VLOS range > Wi-Fi range, need to plan for link loss (drone RTLs automatically).",
    status: "todo", category: "data",
    output: "Max reliable stream distance. Latency vs range. Link-loss RTL verified.",
  },
  {
    id: "pt-retrain-model", name: "Retrain model on real aerial photos",
    description: "Retrained YOLOv8n on 366 images at 1088, mAP50=0.995. Stored in cv_models/sar_v2_1088/",
    script: "generate_dataset_v2.py → Colab → export",
    status: "done", category: "data",
    dependsOn: "pt-training-data",
    output: "cv_models/sar_v2_1088/best.tflite (11.7MB float32). Drop-in replacement. Deploy: cp cv_models/sar_v2_1088/best.tflite best.tflite",
  },
];
