/**
 * Group Project — SAR Drone Mission Architect Data (v2)
 *
 * 6 SE Layers (bottom-up):
 *   L1 Hardware/Physical → L2 Signals/Sensing → L3 Communication Protocols
 *   → L4 Compute Allocation → L5 Software/Logic → L6 Orchestration/Diagnostics
 *
 * Structure: Holy Grail → Levels → Base Layers (shared) + Approaches (override layers)
 */

// ═══════════════════════════════════════════════════════════
// Types
// ═══════════════════════════════════════════════════════════

export interface TeamMember {
  id: string; name: string; role: string; color: string; icon: string;
  integrationDuties: string[];
}

export interface DecisionNode {
  id: string;
  question: string;
  answer: string;
  status: "locked" | "exploring" | "backtracked";
  children: string[];
  backtrackTo?: string;
  level: number;
}

export interface DesignPhase {
  id: string;
  number: number;
  name: string;
  status: "completed" | "active" | "upcoming";
  description: string;
  outputs: string[];
  backtrackTarget?: boolean;
}

export interface SEMethod {
  name: string;
  why: string;
  appliedAt: string;
}

export interface CrossCuttingConcern {
  concern: string;
  affectedLayers: string[];
  owner: string;
  status: "healthy" | "at-risk" | "critical";
}

export interface LevelBridge {
  from: number;
  to: number;
  bridges: string[];
}

export type RequirementTier = "must-have" | "nice-to-have" | "stretch";
export interface TieredRequirement {
  item: string;
  tier: RequirementTier;
  category: "hardware" | "software" | "ground-station" | "safety" | "operations";
  rationale: string;
  levelNeeded: number; // minimum level where this is needed
}

export interface EmergencyProcedure {
  id: string;
  trigger: string;
  severity: "critical" | "warning" | "caution";
  immediateAction: string;
  steps: string[];
  outcome: string;
  levelApplicable: number[]; // which levels this applies to
}

export interface MissionRisk {
  id: string;
  risk: string;
  likelihood: 1 | 2 | 3 | 4 | 5;
  impact: 1 | 2 | 3 | 4 | 5;
  category: "safety" | "technical" | "operational" | "environmental";
  mitigation: string;
  residualRisk: string;
  owner: string; // team member id
  levelApplicable: number[];
}

export interface SELayer {
  id: string; number: number; name: string; icon: string; color: string;
  description: string;
  seApproach: string; // methodology at this layer
  testPhilosophy: string;
}

export interface DroneComponent {
  id: string; name: string; group: ComponentGroup;
  x: number; y: number; // SVG position
  activeAtLevels: number[]; // which levels use this
}

export type ComponentGroup = "propulsion" | "power" | "sensing" | "compute" | "comms" | "ground" | "payload";

export interface DroneConnection {
  from: string; to: string; type: "power" | "data" | "signal";
  protocol?: string;
}

export interface LayerTest {
  name: string; scope: "component" | "pair" | "system" | "diagnostic"; pass: string;
}

export interface LayerContent {
  summary: string;
  components?: { group: string; items: string[] }[];
  decisions?: { question: string; answer: string; reasoning: string }[];
  tests: LayerTest[];
}

export interface Approach {
  id: string; name: string; subtitle: string;
  scalability: "high" | "medium" | "low";
  pathToNext: string; pros: string[]; cons: string[];
  layerOverrides: Record<string, LayerContent>; // keyed by SE layer id
  teamTasks: Record<string, string[]>;
}

// Goal contribution categories (map tasks to Holy Grail aspects)
export type GoalAspect = "locate" | "navigate" | "deliver" | "return" | "infrastructure";
export const GOAL_ASPECTS: Record<GoalAspect, { label: string; color: string; icon: string }> = {
  locate:         { label: "Locate Person",    color: "#8b5cf6", icon: "\u{1F50D}" },
  navigate:       { label: "Avoid NFZ",        color: "#ef4444", icon: "\u{1F6A7}" },
  deliver:        { label: "Deliver Package",  color: "#22c55e", icon: "\u{1F4E6}" },
  return:         { label: "Return Home",      color: "#06b6d4", icon: "\u{1F3E0}" },
  infrastructure: { label: "Infrastructure",   color: "#71717a", icon: "\u{2699}" },
};

export function categorizeTask(task: string): GoalAspect {
  const t = task.toLowerCase();
  if (/detect|cv|camera|vision|target|search|track|yolo|optic|aruco|recogni/.test(t)) return "locate";
  if (/nfz|geofenc|no.fly|obstacle|avoid|polygon/.test(t)) return "navigate";
  if (/payload|deliver|landing|care.?pack|release|drop|precision.?land|precland/.test(t)) return "deliver";
  if (/rth|return|home|failsafe|fail.safe|rtl/.test(t)) return "return";
  return "infrastructure";
}

export interface AmbitionLevel {
  id: number; name: string; subtitle: string; color: string;
  description: string; coreChallenge: string; challengeDetail: string; videoStrategy: string;
  evolution: { carriedOver: string[]; discarded: string[]; newChallenges: string[] };
  baseLayers: Record<string, LayerContent>; // shared across approaches
  approaches: Approach[];
}

export interface ComputeNode {
  id: string; name: string; type: string; scores: Record<string, number>;
}

export interface ComputeTopology {
  id: string; name: string; description: string;
  allocation: { task: string; node: string }[];
  bottleneck: string; suitableForLevels: number[];
}

export interface DiagnosticStep {
  symptom: string;
  checkLayer: string; // SE layer id
  checks: { test: string; ifPass: string; ifFail: string }[];
}

// ═══════════════════════════════════════════════════════════
// Constants
// ═══════════════════════════════════════════════════════════

export const HOLY_GRAIL = "Locate a person in a search area while avoiding no-fly zones, safely deliver them a care package, and fly back home.";

export const GUIDING_PRINCIPLE = "Find the best way to solve the problem at each level of complexity. Levels should build cleanly on top of one another \u2014 avoid messy technical debt, but don't let perfect be the enemy of good.";

export const TEAM: TeamMember[] = [
  { id: "hw",  name: "Hardware Lead",     role: "Airframe, wiring, power systems, physical integration", color: "#f97316", icon: "\u{1F527}",
    integrationDuties: ["Power budget across all subsystems", "Weight budget vs flight time", "Physical mounting compatibility"] },
  { id: "cv",  name: "CV / Optics Lead",  role: "Camera selection, computer vision, image processing",   color: "#8b5cf6", icon: "\u{1F441}",
    integrationDuties: ["CV pipeline output format matches planner input", "Frame rate vs compute tradeoff"] },
  { id: "fd",  name: "Flight Dynamics",    role: "Autopilot, PID tuning, path planning, geofencing",     color: "#06b6d4", icon: "\u{2708}",
    integrationDuties: ["MAVLink message compatibility", "Failsafe coordination with all subsystems"] },
  { id: "gcs", name: "GCS / UI Dev",       role: "Ground station software, telemetry display, live feed", color: "#22c55e", icon: "\u{1F4BB}",
    integrationDuties: ["Telemetry protocol agreement", "Data format standardization"] },
  { id: "pm",  name: "Project Manager",    role: "Integration testing, timeline, risk management, system integrator", color: "#eab308", icon: "\u{1F4CB}",
    integrationDuties: ["Overall system integration oversight", "Cross-team dependency tracking", "Integration test coordination", "Interface specification enforcement"] },
];

// ═══════════════════════════════════════════════════════════
// 6 SE Layers
// ═══════════════════════════════════════════════════════════

export const SE_LAYERS: SELayer[] = [
  {
    id: "hardware", number: 1, name: "Hardware / Physical", icon: "\u{1F527}", color: "#f97316",
    description: "Are parts physically hooked up properly? Getting enough power? Each component works on its own?",
    seApproach: "Bill of Materials + Wiring Diagram + Power Budget. In our case hardware is given \u2014 we just need to connect it correctly.",
    testPhilosophy: "Test each component in isolation BEFORE connecting to the system. Don't rely on software \u2014 check if hardware physically works first.",
  },
  {
    id: "signals", number: 2, name: "Signals & Sensing", icon: "\u{1F4E1}", color: "#84cc16",
    description: "Are sensors reading correctly? Getting the right signals? Calibrated? GPS lock, IMU drift, camera image quality, battery voltage accuracy.",
    seApproach: "Sensor characterisation + calibration protocol. Verify raw data quality before trusting it in control loops.",
    testPhilosophy: "Feed known inputs, check outputs. Compare sensor readings against ground truth. Calibrate before flight.",
  },
  {
    id: "comms", number: 3, name: "Communication Protocols", icon: "\u{1F4AC}", color: "#06b6d4",
    description: "How do parts talk to each other? Which protocols? On-board (FC\u2194Pi, FC\u2194ESCs) and off-board (drone\u2194GCS, drone\u2194RC). This is where we get design choices.",
    seApproach: "Protocol trade study: latency vs bandwidth vs reliability vs complexity. Interface Control Document (ICD) for each link.",
    testPhilosophy: "Test each link in isolation (pair test), then orchestrate. If comms fail, is it hardware (Layer 1) or protocol config (Layer 3)?",
  },
  {
    id: "compute", number: 4, name: "Compute Allocation", icon: "\u{1F9E0}", color: "#a855f7",
    description: "Where does processing happen? Cube (real-time flight), Pi (CV, streaming), or GCS (heavy compute)? Trade-offs: power, latency, RF dependency.",
    seApproach: "Compute Trade Study Matrix: score each node against constraints. Then pick topology (Thick Ground / Thick Edge / Hybrid).",
    testPhilosophy: "Benchmark each node independently. Measure actual latency, throughput, thermal. Compare against requirements.",
  },
  {
    id: "software", number: 5, name: "Software & Logic", icon: "\u{1F4BB}", color: "#3b82f6",
    description: "What's the actual code logic? State machines, flight modes, automation level. How is the mission orchestrated in software?",
    seApproach: "State machine design + flow diagrams. Define states, transitions, triggers. SITL (Software-In-The-Loop) testing before flight.",
    testPhilosophy: "Simulate first (SITL/HITL). Test state transitions exhaustively. Inject faults to verify error handling.",
  },
  {
    id: "integration", number: 6, name: "Orchestration & Diagnostics", icon: "\u{1F3AF}", color: "#ec4899",
    description: "Does everything work together? End-to-end mission test. And when something breaks \u2014 systematic fault isolation: hardware or software?",
    seApproach: "V-model integration: bottom-up assembly + top-down requirements. Pre-flight checklist. Diagnostic decision tree.",
    testPhilosophy: "Full system tests with go/no-go criteria. When failure occurs, trace DOWN through layers to isolate root cause.",
  },
];

// ═══════════════════════════════════════════════════════════
// Drone Blueprint Components
// ═══════════════════════════════════════════════════════════

export const GROUP_COLORS: Record<ComponentGroup, string> = {
  propulsion: "#f97316", power: "#eab308", sensing: "#84cc16",
  compute: "#a855f7", comms: "#06b6d4", ground: "#6b7280", payload: "#ec4899",
};

export const DRONE_COMPONENTS: DroneComponent[] = [
  // Propulsion
  { id: "motors",   name: "Motors (x4)",     group: "propulsion", x: 60,  y: 280, activeAtLevels: [1,2,3] },
  { id: "escs",     name: "ESCs (x4)",       group: "propulsion", x: 180, y: 280, activeAtLevels: [1,2,3] },
  // Power
  { id: "battery",  name: "LiPo Battery",    group: "power",      x: 60,  y: 340, activeAtLevels: [1,2,3] },
  { id: "pdb",      name: "PDB + BECs",      group: "power",      x: 180, y: 340, activeAtLevels: [1,2,3] },
  // Compute
  { id: "cube",     name: "Cube (FC)",       group: "compute",    x: 320, y: 200, activeAtLevels: [1,2,3] },
  { id: "pi",       name: "Raspberry Pi",    group: "compute",    x: 460, y: 200, activeAtLevels: [2,3] },
  // Sensing
  { id: "gps",      name: "GPS",             group: "sensing",    x: 200, y: 140, activeAtLevels: [1,2,3] },
  { id: "imu",      name: "IMU (in FC)",     group: "sensing",    x: 320, y: 140, activeAtLevels: [1,2,3] },
  { id: "camera",   name: "Camera",          group: "sensing",    x: 460, y: 140, activeAtLevels: [1,2,3] },
  { id: "cam_down", name: "Downward Cam",    group: "sensing",    x: 460, y: 80,  activeAtLevels: [3] },
  // Comms
  { id: "rc_rx",    name: "RC Receiver",     group: "comms",      x: 200, y: 200, activeAtLevels: [1,2,3] },
  { id: "telem",    name: "Telemetry Radio", group: "comms",      x: 200, y: 260, activeAtLevels: [1,2,3] },
  { id: "wifi",     name: "WiFi/LTE",        group: "comms",      x: 580, y: 200, activeAtLevels: [2,3] },
  // Ground
  { id: "gcs",      name: "GCS Laptop",      group: "ground",     x: 380, y: 30,  activeAtLevels: [1,2,3] },
  { id: "rc_tx",    name: "RC Transmitter",  group: "ground",     x: 200, y: 30,  activeAtLevels: [1,2,3] },
  // Payload
  { id: "servo",    name: "Payload Release",  group: "payload",   x: 580, y: 280, activeAtLevels: [3] },
];

export const DRONE_CONNECTIONS: DroneConnection[] = [
  { from: "battery",  to: "pdb",    type: "power" },
  { from: "pdb",      to: "escs",   type: "power" },
  { from: "pdb",      to: "cube",   type: "power" },
  { from: "pdb",      to: "pi",     type: "power" },
  { from: "escs",     to: "motors", type: "signal", protocol: "DSHOT" },
  { from: "cube",     to: "escs",   type: "data",   protocol: "PWM/DSHOT" },
  { from: "cube",     to: "gps",    type: "data",   protocol: "I2C/UART" },
  { from: "cube",     to: "rc_rx",  type: "data",   protocol: "SBUS/CRSF" },
  { from: "cube",     to: "telem",  type: "data",   protocol: "MAVLink" },
  { from: "cube",     to: "pi",     type: "data",   protocol: "MAVLink USB" },
  { from: "pi",       to: "camera", type: "data",   protocol: "CSI/USB" },
  { from: "pi",       to: "cam_down", type: "data", protocol: "USB" },
  { from: "pi",       to: "wifi",   type: "data",   protocol: "TCP/UDP" },
  { from: "cube",     to: "servo",  type: "signal", protocol: "PWM" },
  { from: "rc_tx",    to: "rc_rx",  type: "signal", protocol: "CRSF/ELRS" },
  { from: "telem",    to: "gcs",    type: "data",   protocol: "MAVLink" },
  { from: "wifi",     to: "gcs",    type: "data",   protocol: "WebRTC/RTSP" },
];

// ═══════════════════════════════════════════════════════════
// Levels of Ambition
// ═══════════════════════════════════════════════════════════

export const LEVELS: AmbitionLevel[] = [
  // ── Level 1: Manual MVP ─────────────────────────────────
  {
    id: 1, name: "Level 1: Manual MVP", subtitle: "Human-in-the-Loop", color: "#22c55e",
    description: "A human pilot flies the drone manually through the search area. They watch a live camera feed on a screen and visually scan for the missing person. The pilot manually navigates around no-fly zones using a map. When they spot the person, they fly over and land nearby to deliver the care package, then fly home.",
    coreChallenge: "Continuous high-bandwidth video stream",
    challengeDetail: "The human IS the processor. If the video feed drops, stutters, or lags, the mission fails. Every architectural choice revolves around maintaining a reliable, low-latency video pipe from drone to pilot.",
    videoStrategy: "CONSTANT STREAM \u2014 pilot needs uninterrupted visual feed at all times",
    evolution: {
      carriedOver: [],
      discarded: [],
      newChallenges: [
        "Zero computer vision \u2014 if the human blinks, they miss the target",
        "Continuous video bandwidth requirement (~5-20 Mbps)",
        "Pilot fatigue limits effective search time to 15-20 minutes",
        "NFZ avoidance relies entirely on pilot awareness + map overlay",
        "RF range limits the operational area",
      ],
    },
    baseLayers: {
      hardware: {
        summary: "Hardware is given \u2014 assemble airframe, mount components, wire power distribution. Only one way to physically connect things.",
        components: [
          { group: "Propulsion", items: ["Motors (x4)", "ESCs (x4)", "Propellers"] },
          { group: "Power", items: ["LiPo Battery (4S/6S)", "PDB", "5V BEC for FC", "XT60 connector"] },
          { group: "Compute", items: ["Cube Orange (FC)"] },
          { group: "Sensing", items: ["GPS (Here3)", "IMU (built into Cube)", "Barometer (built in)", "FPV Camera"] },
          { group: "Comms", items: ["RC Receiver (ELRS/Crossfire)"] },
        ],
        tests: [
          { name: "Motor spin test", scope: "component", pass: "Each motor spins correct direction, no vibration" },
          { name: "Power continuity", scope: "component", pass: "Multimeter shows correct voltage at each BEC output" },
          { name: "GPS lock test", scope: "component", pass: "GPS gets 3D fix within 60s outdoors" },
          { name: "RC bind test", scope: "component", pass: "Receiver binds, solid LED, channels in configurator" },
          { name: "Camera power test", scope: "component", pass: "Camera produces image when powered directly" },
        ],
      },
      signals: {
        summary: "Verify all sensors read correctly. GPS gives position, IMU gives attitude, battery sensor gives voltage. Calibrate before trusting.",
        components: [
          { group: "Position", items: ["GPS coordinates", "Altitude (baro + GPS fusion)"] },
          { group: "Attitude", items: ["Accelerometer (3-axis)", "Gyroscope (3-axis)", "Magnetometer (compass)"] },
          { group: "Health", items: ["Battery voltage", "Battery current", "ESC temperature (if available)"] },
          { group: "Video", items: ["Camera image (resolution, FOV, frame rate)"] },
        ],
        tests: [
          { name: "GPS accuracy", scope: "component", pass: "Position matches known location within 2m CEP" },
          { name: "IMU calibration", scope: "component", pass: "Level calibration passes, compass matches real north" },
          { name: "Battery voltage accuracy", scope: "pair", pass: "FC reading matches multimeter within 0.1V" },
          { name: "Camera FOV check", scope: "component", pass: "FOV covers expected ground area at flight altitude" },
        ],
      },
      integration: {
        summary: "Full system test: arm, take off, hover, maneuver, land. Pre-flight checklist. If something fails mid-mission, trace back through layers.",
        tests: [
          { name: "Tethered hover test", scope: "system", pass: "Stable hover for 30s, no drift, correct heading" },
          { name: "RC failsafe test", scope: "system", pass: "Drone RTHs or lands within 3s of TX power-off" },
          { name: "Full mission rehearsal", scope: "system", pass: "Complete search pattern + simulated delivery + RTH" },
          { name: "Video dropout diagnostic", scope: "diagnostic", pass: "Layer trace: is it camera (L1)? VTX/encoder (L1)? Protocol (L3)? Range (L3)?" },
          { name: "Motor failure diagnostic", scope: "diagnostic", pass: "Layer trace: ESC (L1)? Signal wire (L1)? FC output (L3)? PID config (L5)?" },
        ],
      },
    },
    approaches: [
      {
        id: "1a", name: "Analog FPV", subtitle: "Classic analog VTX + FPV goggles",
        scalability: "low",
        pathToNext: "Dead end. Analog video cannot interface with CV. VTX and camera must be ripped out entirely for Level 2.",
        pros: ["Cheapest and simplest", "Near-zero latency (~10ms)", "No software config needed", "Battle-tested in FPV community"],
        cons: ["Signal degrades with range (static)", "Cannot interface with onboard computer", "Single viewer only (goggles)", "No digital recording without DVR"],
        layerOverrides: {
          comms: {
            summary: "Minimal: analog video broadcast + RC link. No digital telemetry to GCS. Pilot relies on goggles OSD for flight data.",
            decisions: [
              { question: "Video link type?", answer: "Analog NTSC/PAL", reasoning: "Simplest, lowest latency. No encoding/decoding. But cannot be processed by CV later." },
              { question: "RC protocol?", answer: "CRSF (Crossfire) or ELRS", reasoning: "Both offer low-latency bidirectional control. ELRS is cheaper, CRSF has better range." },
            ],
            tests: [
              { name: "Video frequency check", scope: "pair", pass: "VTX and goggles on same band/channel, clear image" },
              { name: "RC channel mapping", scope: "pair", pass: "All sticks and switches move correct channels in Betaflight" },
              { name: "Range test (200m)", scope: "system", pass: "Video clear, RSSI > 50% at 200m" },
            ],
          },
          compute: {
            summary: "Minimal compute: Cube handles everything. No Pi, no GCS software. Goggles are the only display.",
            decisions: [
              { question: "Where does compute happen?", answer: "Cube only", reasoning: "No onboard computer needed. FC does stabilisation, GPS, failsafe. Video is analog bypass \u2014 no processing." },
            ],
            tests: [
              { name: "FC boot + sensor init", scope: "component", pass: "Cube boots, all sensors green in Mission Planner" },
            ],
          },
          software: {
            summary: "Flight firmware only: ArduPilot or Betaflight. Flight modes, PID tuning, failsafe. No custom software.",
            decisions: [
              { question: "Flight firmware?", answer: "ArduPilot (if GPS nav needed) or Betaflight (if pure manual)", reasoning: "ArduPilot for RTH and position hold; Betaflight if we want simplest FPV experience." },
            ],
            tests: [
              { name: "Flight mode switching", scope: "pair", pass: "RC switch changes modes (Stabilize \u2192 AltHold \u2192 RTL)" },
              { name: "Failsafe logic", scope: "system", pass: "TX off \u2192 RTL triggers within 2s" },
            ],
          },
        },
        teamTasks: {
          hw: ["Assemble airframe, mount all components", "Solder VTX power and signal wires", "Balance props and verify CG"],
          cv: ["Select camera lens (wide angle for search)", "Test image quality at flight altitude", "Document FOV calculations"],
          fd: ["Flash and configure ArduPilot", "PID tune for stable hover", "Set up failsafe and arming sequence"],
          gcs: ["Set up FPV goggles frequency/band", "Configure OSD (battery, RSSI, GPS)", "Print NFZ map for ground spotter"],
          pm: ["Write pre-flight checklist", "Plan search grid pattern", "Coordinate ground NFZ spotter"],
        },
      },
      {
        id: "1b", name: "Digital FPV", subtitle: "DJI O3 / HDZero digital video link",
        scalability: "medium",
        pathToNext: "Partial stepping stone. HD video quality, but still one-way broadcast. Need to add SBC + camera tap for CV.",
        pros: ["HD video (720p-1080p)", "Better range than analog (up to 10km DJI)", "Recording built into goggles", "OSD with flight data"],
        cons: ["Higher latency (~25-40ms)", "More expensive ($200-400)", "Proprietary ecosystems", "Still cannot tap for CV without extra hardware"],
        layerOverrides: {
          comms: {
            summary: "Digital video link (DJI O3 or HDZero) + independent RC link. HD quality with OSD overlay. Still broadcast only \u2014 no bidirectional data.",
            decisions: [
              { question: "Digital system?", answer: "DJI O3 Air Unit", reasoning: "Best range and video quality. Lock-in to DJI ecosystem is the trade-off." },
              { question: "RC integrated or separate?", answer: "Separate ELRS", reasoning: "Don't depend on DJI for RC \u2014 keep independent control link for reliability." },
            ],
            tests: [
              { name: "Air unit pairing", scope: "pair", pass: "Goggles link to air unit, HD image visible" },
              { name: "OSD data feed", scope: "pair", pass: "FC UART to air unit shows battery, GPS, altitude on goggles" },
              { name: "Latency measurement", scope: "system", pass: "Stopwatch on camera vs goggles: < 50ms" },
            ],
          },
          compute: {
            summary: "Same as analog: Cube only. Digital link handles video encoding/decoding internally.",
            decisions: [
              { question: "Where does compute happen?", answer: "Cube + DJI Air Unit (internal video processing)", reasoning: "Air unit has its own encoder. No need for Pi." },
            ],
            tests: [
              { name: "FC + Air Unit integration", scope: "pair", pass: "OSD data renders correctly on goggles feed" },
            ],
          },
          software: {
            summary: "Same as analog approach: ArduPilot firmware. Air unit configuration via DJI tools.",
            decisions: [
              { question: "Firmware?", answer: "ArduPilot (for GPS nav + RTH)", reasoning: "ArduPilot gives us waypoint capability we'll need for Level 2 transition." },
            ],
            tests: [
              { name: "Waypoint mission upload", scope: "pair", pass: "Mission Planner uploads waypoints, FC acknowledges" },
              { name: "Flight mode transitions", scope: "system", pass: "Clean switching between Manual, AltHold, Auto, RTL" },
            ],
          },
        },
        teamTasks: {
          hw: ["Mount air unit + camera module", "Route antenna for optimal placement", "Verify power delivery to air unit"],
          cv: ["Evaluate sensor specs (lens, FOV, low-light)", "Test person detection distance at various altitudes", "Recommend camera angle for search"],
          fd: ["Configure FC UART for air unit OSD", "PID tune for smooth video flight", "Program waypoint grid as search guide"],
          gcs: ["Configure goggles recording", "Set up OSD layout", "Prepare tablet with airspace overlay"],
          pm: ["DJI vs HDZero trade study", "Range and interference test protocol", "Document operational limits"],
        },
      },
      {
        id: "1c", name: "SBC + IP Stream", subtitle: "Pi streams video over WiFi/LTE to GCS",
        scalability: "high",
        pathToNext: "Direct stepping stone. For Level 2, hardware stays identical \u2014 just add CV software to the Pi.",
        pros: ["Hardware directly reusable for Level 2", "Software-defined pipeline (adjustable)", "Dual use: stream + record + future CV", "Telemetry overlay in software"],
        cons: ["Most complex setup at Level 1", "Higher latency (~100-300ms)", "Pi draws significant power (15W)", "WiFi range limited without directional antenna"],
        layerOverrides: {
          comms: {
            summary: "Full digital stack: MAVLink for telemetry (Cube\u2194Pi\u2194GCS), GStreamer/RTSP for video (Pi\u2192GCS), CRSF for RC. Backup SiK telemetry radio.",
            decisions: [
              { question: "Video protocol?", answer: "GStreamer H.264 over RTSP/UDP", reasoning: "Software-defined, adjustable bitrate/resolution. Same pipeline serves CV in Level 2." },
              { question: "Telemetry path?", answer: "MAVLink via Pi (primary) + SiK radio (backup)", reasoning: "Pi relays telemetry over WiFi to GCS. SiK radio as independent backup if WiFi fails." },
              { question: "Video link medium?", answer: "WiFi (2.4GHz or 5GHz) with directional antenna", reasoning: "Simplest for prototype. LTE adds cost/weight but extends range. WiFi sufficient for demos." },
            ],
            tests: [
              { name: "MAVLink heartbeat", scope: "pair", pass: "Pi receives heartbeat from Cube at 1Hz via USB" },
              { name: "Video stream test", scope: "pair", pass: "GStreamer pipeline: Pi camera visible on GCS laptop < 500ms delay" },
              { name: "Dual link test", scope: "system", pass: "RC control works when WiFi disconnected (independent link)" },
              { name: "WiFi range test", scope: "system", pass: "Stable stream at 200m+ with directional antenna" },
            ],
          },
          compute: {
            summary: "Distributed: Cube flies, Pi streams video + relays telemetry, GCS displays + records. Pi is present but not running CV yet.",
            decisions: [
              { question: "Where does compute happen?", answer: "Cube (flight) + Pi (video encoding + relay) + GCS (display)", reasoning: "Pi earns its place by handling video pipeline. This exact setup carries forward to Level 2 with CV added." },
            ],
            tests: [
              { name: "Pi CPU load (stream only)", scope: "component", pass: "< 30% CPU when streaming, temperature < 60\u00B0C" },
              { name: "End-to-end latency", scope: "system", pass: "Camera to GCS screen < 300ms" },
            ],
          },
          software: {
            summary: "ArduPilot on Cube + GStreamer pipeline on Pi + QGroundControl or custom GCS on laptop. Mission Planner for configuration.",
            decisions: [
              { question: "GCS software?", answer: "QGroundControl (primary) + custom overlay (optional)", reasoning: "QGC is free, supports MAVLink natively, has map + video + telemetry. Can build custom later." },
              { question: "Pi operating system?", answer: "Raspberry Pi OS Lite (no desktop)", reasoning: "Headless, lower overhead. GStreamer runs from command line." },
            ],
            tests: [
              { name: "GStreamer auto-start", scope: "component", pass: "Pi boots and starts streaming within 30s" },
              { name: "QGC telemetry display", scope: "pair", pass: "QGC shows attitude, GPS, battery from MAVLink stream" },
              { name: "Mission upload + execute", scope: "system", pass: "Upload waypoint grid, drone follows autonomously" },
            ],
          },
        },
        teamTasks: {
          hw: ["Mount Pi with vibration dampening", "Wire dedicated 5V 3A BEC for Pi", "Mount camera with adjustable tilt", "Route WiFi antenna away from ESC noise"],
          cv: ["Select camera (resolution, FOV, frame rate)", "Set up GStreamer capture pipeline", "Optimise H.264 encoding (bitrate vs latency)", "Test image quality at 30m, 50m, 100m"],
          fd: ["Configure ArduPilot with companion computer", "MAVProxy on Pi for telemetry forwarding", "Program waypoint grid mission", "Configure geofence with NFZ boundaries"],
          gcs: ["Set up QGroundControl", "Integrate video stream + telemetry + map", "Add NFZ boundaries to map", "Set up recording with timestamps"],
          pm: ["Power budget (flight time with Pi)", "Weight budget analysis", "Risk: what fails if WiFi drops?", "Integration test plan: L1 \u2192 L3 \u2192 L6"],
        },
      },
    ],
  },

  // ── Level 2: Semi-Autonomous ────────────────────────────
  {
    id: 2, name: "Level 2: Semi-Auto", subtitle: "Edge CV + Human Confirmation", color: "#3b82f6",
    description: "The drone flies a pre-programmed search pattern autonomously. An onboard computer runs computer vision to scan for people. When CV detects a potential target, it alerts the pilot and opens a video stream for human confirmation. The pilot takes manual control to land near the person and deliver the care package.",
    coreChallenge: "Edge compute \u2014 running CV on a power-constrained SBC",
    challengeDetail: "The Pi IS the processor now. It must run inference fast enough to detect in real-time while staying within power/thermal budget. The video stream is ON-DEMAND, only activated when CV triggers \u2014 saving bandwidth.",
    videoStrategy: "ON-DEMAND \u2014 silent search with telemetry only, video activates on CV trigger",
    evolution: {
      carriedOver: [
        "Airframe and propulsion system (motors, ESCs, props)",
        "Flight controller (Cube) with ArduPilot",
        "RC control link as manual override / safety backup",
        "Pi mounting and power delivery (from Approach 1C)",
        "GCS telemetry display and map overlay",
      ],
      discarded: [
        "Analog/digital FPV link (replaced by software-defined stream)",
        "Continuous video stream (CV handles scanning, human doesn't need constant feed)",
        "Human as primary sensor (now just confirms CV detections)",
        "Manual search pattern (replaced by autonomous waypoints)",
      ],
      newChallenges: [
        "CV model selection and optimisation for edge deployment",
        "Thermal management \u2014 Pi under sustained ML inference load",
        "False positive handling \u2014 alert without crying wolf",
        "Handoff protocol: CV detect \u2192 stream open \u2192 pilot takes control",
        "Autonomous waypoint navigation for systematic search coverage",
        "Geofence enforcement (hard boundaries, not just warnings)",
      ],
    },
    baseLayers: {
      hardware: {
        summary: "Same airframe as Level 1. Add heatsink/fan to Pi. Verify power delivery under full compute load. Camera unchanged but vibration isolation critical for CV.",
        components: [
          { group: "Propulsion", items: ["Motors (x4)", "ESCs (x4)", "Propellers"] },
          { group: "Power", items: ["LiPo Battery", "PDB", "5V BEC (FC)", "5V 3A BEC (Pi \u2014 dedicated)"] },
          { group: "Compute", items: ["Cube Orange (FC)", "Raspberry Pi 4/5 + heatsink + fan"] },
          { group: "Sensing", items: ["GPS", "IMU", "Pi Camera (CSI) \u2014 now CV primary"] },
          { group: "Comms", items: ["RC Receiver", "Telemetry Radio (SiK)", "WiFi antenna"] },
        ],
        tests: [
          { name: "Pi thermal test (idle)", scope: "component", pass: "Temperature < 50\u00B0C with heatsink, no throttling" },
          { name: "Power draw measurement", scope: "component", pass: "Total system draw documented, flight time > 15 min" },
          { name: "Vibration isolation check", scope: "component", pass: "Camera image sharp during hover, no jello" },
        ],
      },
      signals: {
        summary: "Same sensors as Level 1, but camera feed quality is now CRITICAL \u2014 it feeds CV, not just human eyes. Frame rate, resolution, and exposure must be tuned for detection.",
        tests: [
          { name: "Camera frame rate under load", scope: "pair", pass: "Consistent 15+ FPS while Pi runs inference" },
          { name: "Image quality at altitude", scope: "component", pass: "Person distinguishable at 50m in test images" },
          { name: "GPS + compass interference", scope: "pair", pass: "No magnetic interference from Pi/wires near compass" },
        ],
      },
      integration: {
        summary: "Full autonomous search mission: takeoff \u2192 fly grid \u2192 CV scans \u2192 detect \u2192 alert \u2192 pilot confirms \u2192 pilot lands \u2192 RTH. Diagnostic protocol for CV vs comms vs hardware failures.",
        tests: [
          { name: "Full search mission", scope: "system", pass: "Drone flies grid, CV detects test target, alert reaches GCS" },
          { name: "False positive test", scope: "system", pass: "GCS receives alert, pilot rejects, drone resumes search" },
          { name: "Handoff test", scope: "system", pass: "CV alert \u2192 video opens \u2192 pilot takes control in < 10s total" },
          { name: "CV failure diagnostic", scope: "diagnostic", pass: "Is it camera (L1)? Image quality (L2)? Model (L5)? Pi thermal (L4)?" },
          { name: "Link loss during search", scope: "diagnostic", pass: "Does drone continue searching (edge CV)? Or does it RTH?" },
        ],
      },
    },
    approaches: [
      {
        id: "2a", name: "Edge CV + Triggered Stream", subtitle: "Pi runs lightweight CV, only streams on detection",
        scalability: "high",
        pathToNext: "Strong stepping stone. For Level 3, extend Pi autonomy from 'detect + alert' to 'detect + track + land'. Same hardware.",
        pros: ["Minimal bandwidth during search (telemetry only)", "Pi handles detection locally \u2014 no RF dependency for CV", "Clean handoff protocol", "Hardware identical to 1C"],
        cons: ["Pi limits model complexity (YOLOv5n/MobileNet)", "Stream startup delay (~1-2s) on detection", "Pi thermal throttling under sustained inference", "Detection quality depends on altitude + lighting"],
        layerOverrides: {
          comms: {
            summary: "Silent search: telemetry only over SiK radio (~1 kbps). On CV trigger: Pi starts WebRTC/RTSP stream over WiFi for human confirmation. RC always active.",
            decisions: [
              { question: "When does video stream?", answer: "On-demand: CV detection triggers GStreamer pipeline start", reasoning: "Saves bandwidth and power during search. Only streams when human confirmation needed." },
              { question: "Alert mechanism?", answer: "Custom MAVLink message (DETECTION_ALERT) via telemetry", reasoning: "Uses existing telemetry link. GCS parses custom message type, shows alert + GPS coords." },
            ],
            tests: [
              { name: "Alert propagation latency", scope: "pair", pass: "Pi detection \u2192 GCS alert < 500ms" },
              { name: "Triggered stream startup", scope: "pair", pass: "Detection \u2192 video visible on GCS < 3s" },
              { name: "Silent search bandwidth", scope: "system", pass: "Telemetry only: < 5 kbps total" },
            ],
          },
          compute: {
            summary: "Edge-heavy: Pi runs CV inference (YOLOv5n) + on-demand video encoding. Cube flies autonomous waypoints. GCS monitors + confirms.",
            decisions: [
              { question: "CV on Pi or GCS?", answer: "Pi (edge)", reasoning: "No RF dependency for detection. Drone works even if WiFi drops. GCS is just for human confirmation." },
              { question: "CV model?", answer: "YOLOv5n or MobileNet-SSD", reasoning: "Lightweight enough for Pi 4 at 5-10 FPS. Good enough for person detection at drone altitudes." },
            ],
            tests: [
              { name: "Inference benchmark", scope: "component", pass: "> 5 FPS sustained, CPU < 80\u00B0C" },
              { name: "Detection accuracy", scope: "component", pass: "> 80% detection at 50m altitude with test mannequin" },
              { name: "Thermal soak (20 min)", scope: "component", pass: "No throttling with heatsink + fan, < 85\u00B0C" },
            ],
          },
          software: {
            summary: "ArduPilot autonomous mission on Cube + CV pipeline on Pi (capture \u2192 infer \u2192 threshold \u2192 alert) + triggered GStreamer + GCS alert handler.",
            decisions: [
              { question: "State machine for detection?", answer: "SEARCHING \u2192 DETECTED \u2192 STREAMING \u2192 CONFIRMED/REJECTED", reasoning: "Clear states. Pi manages SEARCHING\u2192DETECTED. GCS manages CONFIRMED/REJECTED. Cube manages flight." },
              { question: "What happens on detection?", answer: "Drone loiters, Pi starts stream, GCS shows alert with crop + GPS", reasoning: "Loiter keeps drone near target. Stream gives pilot visual. GPS marks location." },
            ],
            tests: [
              { name: "State machine walk-through", scope: "component", pass: "All transitions work: search \u2192 detect \u2192 stream \u2192 confirm/reject \u2192 resume/hand-off" },
              { name: "SITL mission with fake detection", scope: "system", pass: "Full flow in simulation: waypoints \u2192 fake detect \u2192 loiter \u2192 resume" },
            ],
          },
        },
        teamTasks: {
          hw: ["Add heatsink + cooling fan to Pi", "Verify power under full compute load", "Test vibration isolation for camera", "Add status LED for detection events"],
          cv: ["Select and optimise CV model for Pi", "Collect training data: people from drone angles", "Implement detection pipeline with thresholds", "Build triggered-stream logic"],
          fd: ["Program autonomous waypoint search grid", "Configure hard geofence boundaries", "Implement guided mode for adjustments", "Set up loiter-on-detection"],
          gcs: ["Build alert notification system", "Implement auto-opening stream viewer", "Add detection log with timestamps + GPS + confidence", "Build 'Confirm / Reject' buttons"],
          pm: ["Define confidence threshold with team", "Test matrix: altitude x distance x lighting", "Plan field test with volunteer 'targets'", "Risk: false positives draining battery?"],
        },
      },
      {
        id: "2b", name: "GCS-Side CV", subtitle: "Continuous stream to GCS, CV runs on powerful laptop",
        scalability: "medium",
        pathToNext: "Partial stepping stone. For Level 3, CV must move to edge. This approach delays that migration.",
        pros: ["More powerful CV models (full YOLOv8)", "Pi stays cool \u2014 just streams", "Easier to iterate on models (develop on laptop)", "Can run multiple models simultaneously"],
        cons: ["Requires continuous video stream (back to L1 problem)", "If RF drops, CV stops entirely", "Higher end-to-end latency", "Doesn't scale to Level 3 without rearchitecture"],
        layerOverrides: {
          comms: {
            summary: "Continuous video stream from Pi to GCS over WiFi. GCS runs CV on the video. Same bandwidth problem as Level 1 but now the stream feeds AI, not human eyes.",
            decisions: [
              { question: "When does video stream?", answer: "Always \u2014 continuous H.264 to GCS", reasoning: "GCS needs constant feed for CV processing. This is the main trade-off: powerful CV but RF-dependent." },
            ],
            tests: [
              { name: "Stream stability (20 min)", scope: "system", pass: "< 3 drops in 20 min, auto-reconnect < 2s" },
              { name: "CV latency end-to-end", scope: "system", pass: "Camera capture to detection alert on screen < 1s" },
            ],
          },
          compute: {
            summary: "Thick Ground: Pi only streams, GCS does all CV. Single point of failure at RF link.",
            decisions: [
              { question: "CV on Pi or GCS?", answer: "GCS (laptop/PC)", reasoning: "Full YOLOv8 at 30+ FPS on laptop GPU. Much better accuracy. But completely dependent on WiFi link." },
            ],
            tests: [
              { name: "GCS CV FPS", scope: "component", pass: "> 15 FPS on laptop with YOLOv8 medium" },
              { name: "Detection during stream drop", scope: "system", pass: "CV stops immediately on stream loss \u2014 alert pilot" },
            ],
          },
          software: {
            summary: "ArduPilot on Cube + GStreamer on Pi + CV pipeline on GCS (OpenCV + YOLO + alert logic). GCS is the brain.",
            decisions: [
              { question: "What if WiFi drops?", answer: "Drone continues waypoint mission, but CV is blind. GCS alerts pilot to take over.", reasoning: "Cube flies autonomously regardless. But without CV, we're back to Level 1 (human scanning)." },
            ],
            tests: [
              { name: "WiFi dropout recovery", scope: "system", pass: "Stream resumes within 5s, CV catches up" },
            ],
          },
        },
        teamTasks: {
          hw: ["Optimise antenna for maximum range", "Test directional antenna on GCS side", "Ensure stream reliability"],
          cv: ["Develop CV on GCS laptop (YOLOv8)", "Real-time inference on video stream", "Detection overlay with bounding boxes", "Confidence scoring + alert logic"],
          fd: ["Program waypoint search grid", "Configure geofence", "Guided mode for pilot takeover"],
          gcs: ["Integrated video + CV + telemetry display", "Detection alerts with bounding boxes", "Recording with CV annotation"],
          pm: ["Risk: entire CV lost if RF drops", "Test operational range limits", "Plan CV migration to edge for L3"],
        },
      },
      {
        id: "2c", name: "Hybrid Split CV", subtitle: "Lightweight detection on Pi, heavy confirmation on GCS",
        scalability: "high",
        pathToNext: "Strong stepping stone. Pi already detects \u2014 for Level 3, upgrade model and add tracking + landing logic.",
        pros: ["Fast edge detection + powerful GCS confirmation", "Low bandwidth during search", "Redundant: Pi detects even if RF drops", "Smooth Level 3 migration"],
        cons: ["Most complex software architecture", "Two CV models to manage", "Potential disagreement between edge and GCS", "More testing surface area"],
        layerOverrides: {
          comms: {
            summary: "Two-tier: Pi sends detection crops (small images) to GCS for confirmation. Full video only after GCS confirms. Minimal bandwidth during search.",
            decisions: [
              { question: "What data flows on detection?", answer: "Pi sends: GPS coords + confidence score + cropped image region (50-100 KB)", reasoning: "Much less bandwidth than full video. GCS runs heavy model on the crop to confirm/reject." },
            ],
            tests: [
              { name: "Crop transfer latency", scope: "pair", pass: "Pi crop \u2192 GCS receipt < 1s" },
              { name: "Escalation pipeline", scope: "system", pass: "Pi detect \u2192 crop \u2192 GCS confirm \u2192 full stream: < 5s total" },
            ],
          },
          compute: {
            summary: "Hybrid: Pi runs lightweight screening (MobileNet), GCS runs heavy confirmation (YOLOv8). Best of both worlds.",
            decisions: [
              { question: "How to split compute?", answer: "Pi: fast first-pass (MobileNet, ~10 FPS). GCS: accurate second-pass (YOLOv8, on crop only)", reasoning: "Pi screens thousands of frames. Only sends ~1% to GCS. GCS has high accuracy on small workload." },
            ],
            tests: [
              { name: "Dual model agreement", scope: "component", pass: "> 90% agreement on true positives in test set" },
              { name: "Split brain resolution", scope: "system", pass: "When Pi says 'yes' but GCS says 'no': GCS verdict wins" },
            ],
          },
          software: {
            summary: "Two-tier state machine: Pi runs SEARCH \u2192 CANDIDATE. GCS runs CANDIDATE \u2192 CONFIRMED/REJECTED. Cube handles flight throughout.",
            decisions: [
              { question: "Who makes the final call?", answer: "GCS (human confirms GCS's confirmation)", reasoning: "Pi proposes, GCS verifies, human confirms. Three layers of checking before action." },
            ],
            tests: [
              { name: "Three-tier confirmation", scope: "system", pass: "Pi detect \u2192 GCS confirm \u2192 human approve: all steps traced" },
            ],
          },
        },
        teamTasks: {
          hw: ["Same as 2A: heatsink, power, vibration isolation"],
          cv: ["Build two-tier model pipeline", "Implement crop + send protocol", "Tune thresholds: Pi trigger vs GCS confirm", "Handle edge case: Pi detects but WiFi down"],
          fd: ["Waypoint grid + geofence (same as 2A)", "Loiter-on-detection triggered by Pi"],
          gcs: ["Build confirmation UI with Pi crops + GCS re-analysis", "Implement Confirm / Reject / Override workflow", "Display both Pi and GCS confidence scores"],
          pm: ["Define escalation protocol", "Test false positive rate: Pi vs GCS", "Decision: what confidence triggers alert?"],
        },
      },
    ],
  },

  // ── Level 3: Fully Autonomous ───────────────────────────
  {
    id: 3, name: "Level 3: Fully Autonomous", subtitle: "No Human Required", color: "#a855f7",
    description: "The drone executes the entire mission autonomously. It takes off, navigates the search area while avoiding no-fly zones using onboard path planning, detects the person with CV, approaches and confirms, lands nearby, releases the care package, and flies home. Human role: mission planning, launch, emergency override only.",
    coreChallenge: "Full autonomy stack \u2014 planning, perception, decision-making, precision landing",
    challengeDetail: "Everything must work without a human. The drone plans paths around NFZs in real-time, detects and classifies targets, makes go/no-go decisions, executes precision landing, deploys payload, and navigates home \u2014 managing battery, thermals, and contingencies.",
    videoStrategy: "TELEMETRY ONLY \u2014 human monitors status, video on-demand for oversight",
    evolution: {
      carriedOver: [
        "Airframe, propulsion, power system",
        "FC with ArduPilot (waypoint nav + geofence)",
        "Pi with CV inference pipeline (from Level 2)",
        "MAVLink telemetry and GCS monitoring",
        "RC override as emergency safety link",
      ],
      discarded: [
        "Human confirmation step (drone decides autonomously)",
        "Manual pilot landing (replaced by precision auto-land)",
        "Triggered video stream (unnecessary \u2014 drone acts on its own)",
        "Human as decision-maker (now just monitor + emergency stop)",
      ],
      newChallenges: [
        "Real-time path planning around dynamic NFZs (A* / RRT on edge)",
        "Target tracking during approach (CV + control loop coupling)",
        "Precision landing near person (vision-based or GPS-guided)",
        "Payload release mechanism (servo/actuator control)",
        "Contingency handling: low battery, lost GPS, target moves, obstacle",
        "Regulatory compliance: BVLOS operations, detect-and-avoid",
        "Full mission state machine: takeoff \u2192 search \u2192 detect \u2192 approach \u2192 land \u2192 release \u2192 RTH",
      ],
    },
    baseLayers: {
      hardware: {
        summary: "Level 2 hardware + downward camera for precision landing + payload release mechanism (servo + cradle). Pi 5 recommended for compute headroom.",
        components: [
          { group: "Propulsion", items: ["Motors (x4)", "ESCs (x4)", "Propellers"] },
          { group: "Power", items: ["LiPo Battery", "PDB", "5V BECs (FC + Pi + servo)"] },
          { group: "Compute", items: ["Cube Orange (FC)", "Raspberry Pi 5 + active cooling"] },
          { group: "Sensing", items: ["GPS", "IMU", "Front Camera (CSI \u2014 CV)", "Downward Camera (USB \u2014 landing)"] },
          { group: "Comms", items: ["RC Receiver", "Telemetry Radio", "WiFi/LTE"] },
          { group: "Payload", items: ["Servo actuator", "Payload cradle/release mechanism"] },
        ],
        tests: [
          { name: "Payload release test", scope: "component", pass: "Servo actuates cleanly, package drops, servo returns" },
          { name: "Downward camera test", scope: "component", pass: "Clear downward image at 10m, 5m, 2m height" },
          { name: "Pi 5 power/thermal", scope: "component", pass: "Sustained full load: < 80\u00B0C with active cooling" },
        ],
      },
      signals: {
        summary: "Two cameras feeding Pi simultaneously. Downward camera used for precision landing (ArUco marker or visual features). All Level 2 sensors plus payload servo feedback.",
        tests: [
          { name: "Dual camera feed", scope: "pair", pass: "Pi captures from both cameras simultaneously at 15+ FPS each" },
          { name: "ArUco detection at altitude", scope: "component", pass: "Landing marker detected reliably at 10m, 5m, 2m" },
          { name: "Servo position feedback", scope: "component", pass: "FC reports servo position correctly (open/closed)" },
        ],
      },
      integration: {
        summary: "Full autonomous mission: takeoff \u2192 search grid \u2192 detect \u2192 approach \u2192 confirm \u2192 precision land \u2192 release \u2192 RTH. Exhaustive failure mode testing.",
        tests: [
          { name: "SITL full mission", scope: "system", pass: "Complete mission in simulation without intervention" },
          { name: "Field test (supervised)", scope: "system", pass: "Full mission with safety pilot ready to override" },
          { name: "Battery contingency", scope: "system", pass: "Low battery mid-search \u2192 drone RTHs safely" },
          { name: "GPS loss diagnostic", scope: "diagnostic", pass: "Trace: antenna (L1)? Interference (L2)? Firmware (L5)?" },
          { name: "CV false negative", scope: "diagnostic", pass: "Trace: image quality (L2)? Model (L5)? Altitude (L6 planning)?" },
          { name: "Payload stuck", scope: "diagnostic", pass: "Trace: servo (L1)? Signal (L3)? Command (L5)?" },
        ],
      },
    },
    approaches: [
      {
        id: "3a", name: "Full Edge ROS2", subtitle: "Complete autonomy stack on Pi using ROS2",
        scalability: "high",
        pathToNext: "End-state architecture. Extensible to multi-drone, new sensors, new mission types.",
        pros: ["Fully autonomous beyond RF range", "ROS2: modular, testable, industry-standard", "Skills transfer to career", "Easy to add capabilities"],
        cons: ["Most complex software stack", "ROS2 on Pi can be resource-heavy", "Debugging autonomous behaviour harder", "Longest development time"],
        layerOverrides: {
          comms: {
            summary: "ROS2 DDS for all on-board inter-process communication. MAVSDK for Pi\u2194Cube. SiK + optional WiFi for GCS monitoring. Fully autonomous \u2014 GCS is passive.",
            decisions: [
              { question: "On-board middleware?", answer: "ROS2 (DDS-based)", reasoning: "Industry standard for robotics. Nodes for perception, planning, execution. Testable, modular, documented." },
              { question: "Pi\u2194Cube interface?", answer: "MAVSDK (Python/C++)", reasoning: "Clean API over MAVLink. Easier than raw MAVLink message parsing. Well-maintained." },
            ],
            tests: [
              { name: "ROS2 topic latency", scope: "pair", pass: "/detection \u2192 /planning \u2192 /command pipeline < 200ms" },
              { name: "MAVSDK command test", scope: "pair", pass: "Pi sends goto command, Cube executes within 1s" },
            ],
          },
          compute: {
            summary: "Full Edge: Pi 5 runs entire autonomy stack (ROS2). Cube handles low-level flight. GCS is passive monitor.",
            decisions: [
              { question: "Autonomy on Pi or GCS?", answer: "All on Pi", reasoning: "Must work beyond RF range. Pi runs perception + planning + execution. GCS monitors only." },
            ],
            tests: [
              { name: "ROS2 node health (5 min)", scope: "component", pass: "All nodes active, no crashes, memory stable" },
              { name: "Full stack CPU/RAM", scope: "component", pass: "< 80% CPU, < 3GB RAM under full mission load" },
            ],
          },
          software: {
            summary: "ROS2 nodes: /perception (CV), /planner (path + mission FSM), /executor (MAVSDK). Full mission state machine: IDLE \u2192 TAKEOFF \u2192 SEARCH \u2192 DETECT \u2192 APPROACH \u2192 LAND \u2192 RELEASE \u2192 RTH.",
            decisions: [
              { question: "Path planning algorithm?", answer: "A* with NFZ polygon avoidance", reasoning: "Simple, deterministic, fast enough for 2D waypoint planning. RRT for dynamic obstacles if needed later." },
              { question: "Precision landing method?", answer: "ArUco marker detection + visual servoing", reasoning: "ArduPilot has built-in PrecLand support. Pi detects marker via downward cam, sends corrections." },
            ],
            tests: [
              { name: "State machine walk-through", scope: "component", pass: "All 8 states and transitions work in SITL" },
              { name: "NFZ avoidance", scope: "system", pass: "Drone replans path when NFZ blocks direct route" },
              { name: "Failsafe cascade", scope: "system", pass: "GPS loss \u2192 hover. Link loss \u2192 RTH. Low battery \u2192 land." },
            ],
          },
        },
        teamTasks: {
          hw: ["Upgrade to Pi 5 if needed", "Add downward camera for landing", "Build payload release mechanism", "Active cooling solution"],
          cv: ["Upgrade detection model (fine-tuned YOLOv8n)", "Add target tracking (DeepSORT)", "ArUco marker detection for landing", "Confidence-based decision logic"],
          fd: ["ROS2 path planner with NFZ avoidance", "Precision landing controller", "Full mission state machine", "SITL testing: 50+ scenarios"],
          gcs: ["Mission monitoring dashboard", "Emergency override controls", "Mission replay / post-flight analysis", "Real-time map with search progress"],
          pm: ["SITL test matrix", "Regulatory research (BVLOS)", "Risk matrix: autonomous failure modes", "Demo day planning"],
        },
      },
      {
        id: "3b", name: "ArduPilot Scripting", subtitle: "Lua scripts on FC + Pi for CV only",
        scalability: "medium",
        pathToNext: "Functional end-state, less extensible than ROS2. Good for faster delivery.",
        pros: ["Simpler than ROS2", "ArduPilot Lua well-documented", "Tighter FC integration", "Faster development"],
        cons: ["Lua has limited libraries", "Harder to add complex behaviours", "Less modular (monolithic scripts)", "Less industry-transferable"],
        layerOverrides: {
          comms: {
            summary: "MAVLink for Pi\u2194Cube. Lua scripts run directly on Cube. No ROS2 overhead.",
            decisions: [
              { question: "Mission logic where?", answer: "Lua scripts on Cube (FC)", reasoning: "ArduPilot's Lua scripting runs mission FSM on the FC itself. Pi just sends detection coords." },
            ],
            tests: [
              { name: "CV-to-Lua bridge", scope: "pair", pass: "Pi sends detection via MAVLink, Lua script acts within 500ms" },
            ],
          },
          compute: {
            summary: "Split: Cube runs mission logic (Lua), Pi runs CV only. Simpler than ROS2 but less modular.",
            decisions: [
              { question: "Mission logic on Pi or Cube?", answer: "Cube (Lua)", reasoning: "Tighter integration with flight controller. No inter-process overhead. But Lua is limited." },
            ],
            tests: [
              { name: "Lua script stress test", scope: "component", pass: "Script runs for 30 min without memory leak or crash" },
            ],
          },
          software: {
            summary: "ArduPilot + Lua mission FSM on Cube. Pi runs CV pipeline, sends detections as MAVLink messages. Simpler architecture, faster to build.",
            decisions: [
              { question: "Precision landing?", answer: "ArduPilot's built-in PrecLand + Pi ArUco feed", reasoning: "Native support in ArduPilot. No custom controller needed." },
            ],
            tests: [
              { name: "Full mission SITL", scope: "system", pass: "Search \u2192 detect \u2192 land \u2192 release \u2192 RTH in simulation" },
            ],
          },
        },
        teamTasks: {
          hw: ["Same as 3A: downward cam, payload, cooling"],
          cv: ["CV pipeline outputting MAVLink messages", "Simpler integration: lat/lon/confidence to Cube"],
          fd: ["Lua mission state machine", "PrecLand via ArduPilot built-in", "Path planning via mission scripting"],
          gcs: ["Monitor via QGroundControl", "Custom MAVLink messages for detection events"],
          pm: ["Faster timeline than ROS2", "Plan for extensibility limits"],
        },
      },
      {
        id: "3c", name: "4G/5G Cloud-Assisted", subtitle: "Cellular link for heavy compute, Pi for real-time safety",
        scalability: "high",
        pathToNext: "Maximum capability. Enables fleet management, OTA model updates, remote control.",
        pros: ["Unlimited cloud compute (GPU)", "Real-time model updates OTA", "Fleet management from anywhere", "HD streaming for remote oversight"],
        cons: ["Cellular coverage not guaranteed in SAR areas", "Added weight/power (4G modem)", "Cloud round-trip latency (~50-200ms)", "Monthly costs + single point of failure"],
        layerOverrides: {
          comms: {
            summary: "4G/5G modem on drone \u2192 cloud backend. Pi keeps edge CV as fallback. WebSocket for GCS\u2194Cloud remote monitoring.",
            decisions: [
              { question: "Primary compute link?", answer: "4G/5G cellular to cloud", reasoning: "Unlimited compute in cloud. But must handle coverage gaps \u2014 edge fallback is mandatory." },
              { question: "What if no coverage?", answer: "Pi falls back to edge-only mode (Level 2 equivalent)", reasoning: "Graceful degradation: cloud for best performance, edge for resilience." },
            ],
            tests: [
              { name: "Cellular latency at altitude", scope: "component", pass: "RTT < 200ms at operating altitude" },
              { name: "Failover test", scope: "system", pass: "Kill cellular \u2192 Pi continues with edge CV, alerts queued" },
            ],
          },
          compute: {
            summary: "Cloud-Heavy: best AI runs in cloud. Pi handles real-time safety + edge fallback. Cube flies.",
            decisions: [
              { question: "Cloud provider?", answer: "Any with GPU instances (AWS/GCP/Azure)", reasoning: "Run YOLOv8 large or custom models. No Pi constraints. Pi keeps lightweight model as backup." },
            ],
            tests: [
              { name: "Cloud inference speed", scope: "pair", pass: "Frame to detection result < 300ms including network" },
            ],
          },
          software: {
            summary: "Pi: edge CV fallback + video encoding + cellular relay. Cloud: heavy CV + path planning + fleet management. Cube: flight control + local failsafes.",
            decisions: [
              { question: "Architecture pattern?", answer: "Edge-cloud hybrid with graceful degradation", reasoning: "Cloud enhances but isn't required. Edge provides baseline autonomy. Best of both worlds." },
            ],
            tests: [
              { name: "Graceful degradation", scope: "system", pass: "Cloud down \u2192 seamless switch to edge mode" },
            ],
          },
        },
        teamTasks: {
          hw: ["Mount 4G modem + antenna", "Power budget with modem", "Cellular signal survey at operating areas"],
          cv: ["Cloud CV model (YOLOv8 large)", "Edge fallback model (lightweight)", "Cloud inference API (FastAPI + ONNX)"],
          fd: ["Cellular failover logic", "If cloud unavailable, edge-only autonomy"],
          gcs: ["Cloud-based mission control dashboard", "Remote override via cellular", "Fleet management UI"],
          pm: ["Cellular coverage survey", "Cost analysis: cloud + cellular", "Regulatory: remote piloting via cellular?"],
        },
      },
    ],
  },
];

// ═══════════════════════════════════════════════════════════
// Compute Trade Study
// ═══════════════════════════════════════════════════════════

export const COMPUTE_DIMENSIONS = ["Compute Power", "Control Latency", "RF Independence", "SWaP"];

export const COMPUTE_NODES: ComputeNode[] = [
  { id: "cube", name: "The Cube (FC)", type: "Microcontroller \u2014 Hard Real-Time",
    scores: { "Compute Power": 1, "Control Latency": 5, "RF Independence": 5, "SWaP": 4 } },
  { id: "pi", name: "Raspberry Pi", type: "Microprocessor \u2014 Soft Real-Time",
    scores: { "Compute Power": 3, "Control Latency": 3, "RF Independence": 5, "SWaP": 2 } },
  { id: "gcs", name: "Ground Station", type: "Full PC \u2014 No Real-Time",
    scores: { "Compute Power": 5, "Control Latency": 1, "RF Independence": 1, "SWaP": 5 } },
];

export const COMPUTE_TOPOLOGIES: ComputeTopology[] = [
  { id: "thick-ground", name: "Thick Ground",
    description: "All compute on GCS. Drone is a 'dumb' flying camera.",
    allocation: [
      { task: "Flight Control", node: "cube" }, { task: "Video Capture", node: "pi" },
      { task: "CV Processing", node: "gcs" }, { task: "Path Planning", node: "gcs" },
      { task: "Mission Logic", node: "gcs" },
    ],
    bottleneck: "RF Video Link \u2014 single point of failure.", suitableForLevels: [1, 2] },
  { id: "thick-edge", name: "Thick Edge",
    description: "All compute on Pi. Drone operates independently.",
    allocation: [
      { task: "Flight Control", node: "cube" }, { task: "Video Capture", node: "pi" },
      { task: "CV Processing", node: "pi" }, { task: "Path Planning", node: "pi" },
      { task: "Mission Logic", node: "pi" },
    ],
    bottleneck: "Pi Power/Thermal \u2014 sustained ML drains battery.", suitableForLevels: [2, 3] },
  { id: "hybrid", name: "Hybrid Split",
    description: "Time-critical on Pi, heavy processing on GCS.",
    allocation: [
      { task: "Flight Control", node: "cube" }, { task: "Video Capture", node: "pi" },
      { task: "CV Processing", node: "pi" }, { task: "Path Planning", node: "gcs" },
      { task: "Mission Logic", node: "pi" },
    ],
    bottleneck: "Coordination complexity \u2014 two nodes must stay in sync.", suitableForLevels: [2, 3] },
];

// ═══════════════════════════════════════════════════════════
// Diagnostic Protocol
// ═══════════════════════════════════════════════════════════

// ═══════════════════════════════════════════════════════════
// SE Methodology — Our Paradigm & Methods
// ═══════════════════════════════════════════════════════════

export const SE_METHODOLOGY = {
  paradigm: "Incremental V-Model with Set-Based Elements",
  paradigmShort: "Build-Test-Evolve across 3 ambition levels",
  paradigmJustification: "We use the V-Model's verification structure (bottom-up testing mirrors top-down decomposition) because our system is hardware-heavy and needs layer-by-layer verification. But we operate incrementally across 3 ambition levels rather than one monolithic pass. Set-based elements come from keeping 3 architectural approaches open per level before locking in \u2014 we narrow by evidence, not by gut feeling.",
  whyNotOthers: [
    { paradigm: "Pure Sequential", reason: "Too rigid \u2014 we'd commit to one architecture before knowing if it works. No room for the learning that happens at each level." },
    { paradigm: "Pure Simultaneous", reason: "Can't brute-force 9 physical architectures \u2014 we'd need to build all of them. Works for software configs, not hardware." },
    { paradigm: "Pure Evolutionary", reason: "Can't mutate hardware randomly. Evolutionary works for parameter tuning, not for choosing between ROS2 vs Lua vs cloud architectures." },
    { paradigm: "Pure Set-Based", reason: "Closest to our approach, but we add the V-Model's structured testing hierarchy. Toyota can test car designs in simulation; we need real hardware tests at each layer." },
  ],
  methods: [
    { name: "V-Model Integration Testing", why: "Hardware-heavy system needs layer-by-layer verification. Test components alone (L1), then pairs (L1+L2), then system (all layers). Each layer has specific pass criteria before moving up.", appliedAt: "Every level, every approach" },
    { name: "Trade Study Matrix", why: "Compute allocation has 3 viable topologies (Thick Ground, Thick Edge, Hybrid). Need systematic comparison across 4 dimensions (power, latency, RF independence, SWaP).", appliedAt: "Compute layer (L4)" },
    { name: "Morphological Box", why: "3 levels \u00D7 3 approaches = 9 possible system configurations. Morphological analysis ensures we've covered the design space systematically rather than jumping to the obvious answer.", appliedAt: "Level/approach selection" },
    { name: "FMEA / Diagnostic Protocol", why: "Field failures are inevitable. Systematic fault isolation (trace DOWN through SE layers) is faster than ad-hoc debugging. Maps symptoms to root-cause layers.", appliedAt: "L6 Orchestration / field testing" },
    { name: "Incremental Prototyping", why: "Each level delivers a working drone that does something useful. Level 1 flies and streams video. Level 2 flies waypoints and detects targets. Level 3 does it all autonomously. No level is wasted.", appliedAt: "Cross-level progression" },
  ] as SEMethod[],
};

// ═══════════════════════════════════════════════════════════
// Decision Tree — Design Strategy with Backtrack Points
// ═══════════════════════════════════════════════════════════

export const DECISION_TREE: DecisionNode[] = [
  { id: "d1", question: "Mission type?", answer: "SAR with payload delivery", status: "locked", children: ["d2", "d3"], level: 0 },
  { id: "d2", question: "Platform type?", answer: "Multi-rotor (VTOL required for hover + precision)", status: "locked", children: ["d4"], level: 1 },
  { id: "d3", question: "Autonomy strategy?", answer: "Progressive: Manual \u2192 Semi \u2192 Full", status: "locked", children: ["d5", "d6"], level: 1 },
  { id: "d4", question: "Flight controller?", answer: "The Cube (ArduPilot)", status: "locked", children: ["d7"], level: 2 },
  { id: "d5", question: "CV framework?", answer: "YOLOv8 on Pi (edge inference)", status: "locked", children: [], level: 2 },
  { id: "d6", question: "Where does autonomy live?", answer: "Exploring: Pi-only vs Cube Lua vs Cloud", status: "exploring", children: ["d8", "d9", "d10"], level: 2 },
  { id: "d7", question: "Companion computer?", answer: "Raspberry Pi 5", status: "locked", children: [], level: 3 },
  { id: "d8", question: "Full ROS2 on Pi?", answer: "Maximum flexibility, industry standard", status: "exploring", children: [], level: 3 },
  { id: "d9", question: "Lua on Cube + Pi CV only?", answer: "Simpler, faster to build, less extensible", status: "exploring", children: [], level: 3 },
  { id: "d10", question: "Cloud-assisted via 4G?", answer: "Unlimited compute, coverage dependency", status: "exploring", children: [], level: 3 },
  { id: "d11", question: "Comms: RC only or digital?", answer: "CRSF/ELRS at L1, upgrade to MAVLink at L2+", status: "locked", children: [], level: 2 },
  { id: "d12", question: "Payload mechanism?", answer: "Servo-actuated release (simple, reliable)", status: "locked", children: [], level: 2 },
];

// ═══════════════════════════════════════════════════════════
// Design Phases — Sequence of Events
// ═══════════════════════════════════════════════════════════

export const DESIGN_PHASES: DesignPhase[] = [
  { id: "p1", number: 1, name: "Mission Analysis", status: "completed",
    description: "Understand the SAR mission: locate person, avoid NFZ, deliver package, return. Define success criteria and operational environment.",
    outputs: ["Holy Grail statement", "Guiding principle", "Environmental constraints"], backtrackTarget: false },
  { id: "p2", number: 2, name: "Requirements Capture", status: "completed",
    description: "Define what 'good enough' means at each ambition level. Translate mission into measurable requirements per SE layer.",
    outputs: ["3 ambition levels defined", "Per-layer requirements", "Test pass criteria"], backtrackTarget: true },
  { id: "p3", number: 3, name: "Design Space Exploration", status: "active",
    description: "Generate architectural approaches. 3 per level = 9 total. Map component options, compute topologies, communication strategies.",
    outputs: ["9 approaches defined", "Morphological box", "Compute trade study matrix"], backtrackTarget: true },
  { id: "p4", number: 4, name: "Architecture Selection", status: "upcoming",
    description: "Evaluate approaches using trade study methods. Score pros/cons/scalability. Select primary approach per level.",
    outputs: ["Scored approach matrix", "Primary selection per level", "Justification rationale"], backtrackTarget: true },
  { id: "p5", number: 5, name: "Detailed Design", status: "upcoming",
    description: "Lock in component choices, wiring diagrams, software architecture, interface specs. Full technical documentation.",
    outputs: ["Wiring diagrams", "Software architecture", "Interface control documents"], backtrackTarget: false },
  { id: "p6", number: 6, name: "Build & Test", status: "upcoming",
    description: "Build Level 1 first. Test bottom-up through SE layers. Component \u2192 pair \u2192 system tests. Fix issues, iterate.",
    outputs: ["Working L1 prototype", "Test results per layer", "Defect log"], backtrackTarget: true },
  { id: "p7", number: 7, name: "Integration & Flight", status: "upcoming",
    description: "Full system integration. Field testing. Demo preparation. Lessons learned feed into next level.",
    outputs: ["Flight test results", "Demo video", "Lessons learned for L2"], backtrackTarget: false },
];

// ═══════════════════════════════════════════════════════════
// Integration Oversight — Cross-Cutting Concerns
// ═══════════════════════════════════════════════════════════

export const INTEGRATION_OVERVIEW = {
  integrator: "pm",
  crossCuttingConcerns: [
    { concern: "Power Budget", affectedLayers: ["hardware", "compute", "comms"], owner: "hw", status: "at-risk" as const,
      detail: "Motors + Pi + camera + telemetry radio + payload servo. Total draw must stay under battery capacity with 20% reserve." },
    { concern: "Weight Budget", affectedLayers: ["hardware", "payload"], owner: "hw", status: "healthy" as const,
      detail: "Airframe max takeoff weight minus battery = available payload. Camera + Pi + payload + wiring must fit." },
    { concern: "Data Throughput", affectedLayers: ["comms", "compute", "software"], owner: "gcs", status: "healthy" as const,
      detail: "Video stream + telemetry + CV detections must all flow without saturating bandwidth. WiFi for video, SiK for telemetry." },
    { concern: "Latency Chain", affectedLayers: ["sensing", "compute", "software", "comms"], owner: "fd", status: "at-risk" as const,
      detail: "Camera frame \u2192 CV detection \u2192 decision \u2192 flight command. End-to-end latency determines reaction speed. Target: < 500ms at L2, < 200ms at L3." },
    { concern: "Failsafe Cascade", affectedLayers: ["software", "comms", "orchestration"], owner: "fd", status: "healthy" as const,
      detail: "What happens when things fail? GPS loss \u2192 hover. Link loss \u2192 RTH. Low battery \u2192 land. Each failsafe must be tested independently and in combination." },
  ] as (CrossCuttingConcern & { detail: string })[],
};

// ═══════════════════════════════════════════════════════════
// Level Pathway — MVP to Stretch Goal Bridges
// ═══════════════════════════════════════════════════════════

export const LEVEL_PATHWAY: LevelBridge[] = [
  { from: 1, to: 2, bridges: [
    "Add GPS waypoint following (ArduPilot missions)",
    "Replace pure RC with MAVLink command interface",
    "Mount Pi + camera, run CV detection pipeline",
    "Add WiFi video streaming to GCS",
    "Build basic GCS dashboard (map + telemetry + video)",
  ]},
  { from: 2, to: 3, bridges: [
    "Upgrade CV model for reliable field detection",
    "Add onboard path planning (A* with NFZ avoidance)",
    "Implement mission state machine (IDLE\u2192SEARCH\u2192DETECT\u2192LAND\u2192RELEASE\u2192RTH)",
    "Add precision landing (ArUco marker + visual servoing)",
    "Build payload release mechanism + servo control",
    "Remove GCS dependency for mission-critical decisions",
  ]},
];

export const DIAGNOSTIC_STEPS: DiagnosticStep[] = [
  {
    symptom: "No video feed",
    checkLayer: "hardware",
    checks: [
      { test: "Camera powered?", ifPass: "Check Layer 3 (comms)", ifFail: "Fix power wiring (L1)" },
      { test: "Camera detected by Pi?", ifPass: "Check GStreamer pipeline (L5)", ifFail: "Check CSI/USB connection (L1)" },
      { test: "GStreamer running?", ifPass: "Check WiFi link (L3)", ifFail: "Restart pipeline (L5)" },
      { test: "WiFi connected?", ifPass: "Check GCS software (L5)", ifFail: "Check antenna/range (L1/L3)" },
    ],
  },
  {
    symptom: "Drone drifts / won't hold position",
    checkLayer: "signals",
    checks: [
      { test: "GPS has 3D fix?", ifPass: "Check compass calibration (L2)", ifFail: "Check GPS antenna placement (L1)" },
      { test: "Compass calibrated?", ifPass: "Check PID tuning (L5)", ifFail: "Recalibrate, check for magnetic interference (L2)" },
      { test: "PIDs reasonable?", ifPass: "Check motor balance (L1)", ifFail: "Retune PIDs (L5)" },
    ],
  },
  {
    symptom: "CV not detecting targets",
    checkLayer: "software",
    checks: [
      { test: "Camera image clear?", ifPass: "Check model loading (L5)", ifFail: "Check vibration isolation, focus (L1/L2)" },
      { test: "Model loaded and running?", ifPass: "Check altitude/angle (L6)", ifFail: "Check Pi resources, model path (L4/L5)" },
      { test: "Pi thermal throttling?", ifPass: "Check model accuracy (L5)", ifFail: "Improve cooling (L1), reduce load (L4)" },
      { test: "Test images detect correctly?", ifPass: "Problem is real-world conditions (lighting, altitude)", ifFail: "Retrain or swap model (L5)" },
    ],
  },
  {
    symptom: "Telemetry lost to GCS",
    checkLayer: "comms",
    checks: [
      { test: "SiK radio powered?", ifPass: "Check MAVLink config (L3)", ifFail: "Check power wiring (L1)" },
      { test: "MAVLink heartbeat on Pi?", ifPass: "Check GCS connection (L5)", ifFail: "Check Cube\u2194Pi USB/UART (L1/L3)" },
      { test: "GCS receiving any data?", ifPass: "Check specific stream (L5)", ifFail: "Check SiK radio pairing (L3)" },
    ],
  },
];

// ═══════════════════════════════════════════════════════════
// Equipment & Setup Requirements (Tiered)
// ═══════════════════════════════════════════════════════════

export const TIERED_REQUIREMENTS: TieredRequirement[] = [
  // ── MUST-HAVE (absolute minimum for safe operation) ──
  { item: "RC transmitter + receiver with failsafe", tier: "must-have", category: "hardware", rationale: "Manual override at ALL times. Non-negotiable safety requirement. If anything goes wrong, pilot must be able to take control instantly.", levelNeeded: 1 },
  { item: "ArduPilot with RTH failsafe configured", tier: "must-have", category: "software", rationale: "Drone must return home on signal loss. This is the absolute baseline safety net.", levelNeeded: 1 },
  { item: "Battery voltage monitoring + low-battery RTH", tier: "must-have", category: "safety", rationale: "Drone falling out of the sky is unacceptable. Auto-land or RTH when battery hits threshold.", levelNeeded: 1 },
  { item: "Pre-flight checklist (paper or digital)", tier: "must-have", category: "operations", rationale: "Systematic verification before every flight. Prevents 'forgot to plug in GPS' scenarios.", levelNeeded: 1 },
  { item: "Mission Planner or QGroundControl on laptop", tier: "must-have", category: "ground-station", rationale: "Need to configure ArduPilot, upload missions, monitor telemetry. These are free, proven tools.", levelNeeded: 1 },
  { item: "Telemetry radio (SiK 433/915MHz)", tier: "must-have", category: "hardware", rationale: "Real-time battery, GPS, attitude data to GCS. Flying blind without this. Independent of video link.", levelNeeded: 1 },
  { item: "Geofence boundaries configured", tier: "must-have", category: "software", rationale: "Hard boundaries the drone cannot cross. NFZ compliance is a mission requirement, not optional.", levelNeeded: 1 },
  { item: "Kill switch on RC (motor disarm)", tier: "must-have", category: "safety", rationale: "Instant motor stop in emergency. Mapped to a physical switch, not buried in menus.", levelNeeded: 1 },
  { item: "Spotter with line-of-sight to drone", tier: "must-have", category: "operations", rationale: "Legal requirement for VLOS operations. Spotter watches drone while pilot watches screen.", levelNeeded: 1 },
  { item: "GPS with 3D fix before arming", tier: "must-have", category: "safety", rationale: "No GPS = no position hold, no RTH, no geofence. ArduPilot enforces this as arming check.", levelNeeded: 1 },

  // ── NICE-TO-HAVE (significantly improves capability) ──
  { item: "Raspberry Pi with camera (CV-ready)", tier: "nice-to-have", category: "hardware", rationale: "Enables CV at L2+. At L1 it adds video streaming capability. Hardware investment that carries forward.", levelNeeded: 1 },
  { item: "WiFi video streaming to GCS", tier: "nice-to-have", category: "ground-station", rationale: "Live video feed on GCS laptop vs FPV goggles. Better for team collaboration and recording.", levelNeeded: 1 },
  { item: "Custom GCS dashboard (telemetry + video + map)", tier: "nice-to-have", category: "ground-station", rationale: "Unified view: map with drone position, NFZ overlay, live video, telemetry gauges. Better than toggling between QGC tabs.", levelNeeded: 2 },
  { item: "CV detection pipeline on Pi", tier: "nice-to-have", category: "software", rationale: "Automated target detection. Transforms drone from 'flying camera' to 'intelligent sensor'. Core of L2.", levelNeeded: 2 },
  { item: "Automated waypoint search patterns", tier: "nice-to-have", category: "software", rationale: "Systematic search coverage. Drone follows optimised grid instead of pilot guessing. More thorough, less fatigue.", levelNeeded: 2 },
  { item: "Detection alert system (GCS notification)", tier: "nice-to-have", category: "ground-station", rationale: "Popup alert when CV spots potential target. Sound + visual + GPS coords. Pilot confirms/rejects.", levelNeeded: 2 },
  { item: "Post-flight log analysis tools", tier: "nice-to-have", category: "operations", rationale: "Review flight logs, telemetry, CV detections after mission. Learn from each flight. ArduPilot logs + custom analytics.", levelNeeded: 1 },
  { item: "Heatsink + active cooling for Pi", tier: "nice-to-have", category: "hardware", rationale: "Prevents thermal throttling under sustained CV inference. Critical for reliable L2+ operation.", levelNeeded: 2 },

  // ── STRETCH (would be great but not blocking) ──
  { item: "Full ROS2 autonomy stack", tier: "stretch", category: "software", rationale: "Industry-standard robotics middleware. Maximum flexibility and extensibility. But complex to set up and debug.", levelNeeded: 3 },
  { item: "Precision landing (ArUco + downward camera)", tier: "stretch", category: "hardware", rationale: "Land precisely near target for package delivery. Requires second camera, ArUco detection, visual servoing.", levelNeeded: 3 },
  { item: "Payload release mechanism", tier: "stretch", category: "hardware", rationale: "Servo-actuated package drop. Mechanical + electrical + software integration. Core of L3 delivery mission.", levelNeeded: 3 },
  { item: "4G/LTE modem for BVLOS", tier: "stretch", category: "hardware", rationale: "Cellular link for beyond-visual-line-of-sight. Enables remote monitoring + cloud compute. Adds weight + cost + coverage dependency.", levelNeeded: 3 },
  { item: "Cloud inference backend (GPU)", tier: "stretch", category: "software", rationale: "Run heavy CV models in cloud. Unlimited compute. But adds latency + coverage dependency.", levelNeeded: 3 },
  { item: "Fleet management dashboard", tier: "stretch", category: "ground-station", rationale: "Multi-drone coordination from single GCS. Future capability for scaling SAR operations.", levelNeeded: 3 },
  { item: "Mission replay / digital twin", tier: "stretch", category: "ground-station", rationale: "3D replay of mission with telemetry overlay. Great for debriefing and reports but not mission-critical.", levelNeeded: 2 },
  { item: "OTA model updates via cellular", tier: "stretch", category: "software", rationale: "Push improved CV models to drone without physical access. Great for iteration but requires 4G link.", levelNeeded: 3 },
];

// ═══════════════════════════════════════════════════════════
// Emergency Procedures
// ═══════════════════════════════════════════════════════════

export const EMERGENCY_PROCEDURES: EmergencyProcedure[] = [
  {
    id: "ep1", trigger: "Loss of RC control link", severity: "critical",
    immediateAction: "DO NOTHING \u2014 ArduPilot failsafe activates automatically",
    steps: [
      "ArduPilot detects no RC input for 1.5s \u2192 enters RC_FAILSAFE mode",
      "Pre-configured action executes: RTH (recommended) or LAND",
      "Drone climbs to RTH altitude, navigates home, lands at launch point",
      "If RC regained during RTH: pilot can take back control immediately",
      "If drone does NOT respond: call spotter, prepare for manual retrieval",
    ],
    outcome: "Drone returns home and lands autonomously. Pilot regains control when in range.",
    levelApplicable: [1, 2, 3],
  },
  {
    id: "ep2", trigger: "Low battery warning (configurable threshold)", severity: "critical",
    immediateAction: "Assess: enough battery to RTH? If yes, initiate RTH. If no, LAND immediately.",
    steps: [
      "BATT_LOW_VOLT threshold triggers audible + visual alarm on GCS",
      "Pilot assesses distance to home vs remaining capacity",
      "Option A: Switch to RTL mode \u2192 drone returns at safe speed",
      "Option B: Switch to LAND mode \u2192 drone descends and lands at current position",
      "BATT_CRT_VOLT (critical): ArduPilot auto-lands regardless of pilot input",
      "Log landing coordinates for retrieval",
    ],
    outcome: "Drone lands safely before battery depletion. Avoids crash from power loss.",
    levelApplicable: [1, 2, 3],
  },
  {
    id: "ep3", trigger: "GPS loss during flight", severity: "warning",
    immediateAction: "Switch to STABILIZE or ALT_HOLD mode (no GPS required)",
    steps: [
      "ArduPilot detects GPS glitch or loss of 3D fix",
      "If in AUTO/GUIDED: switches to LAND or continues on last known position (configurable)",
      "Pilot takes manual control in STABILIZE (manual) or ALT_HOLD (altitude maintained)",
      "Fly visually back to launch point using line of sight",
      "If GPS returns: switch back to LOITER for position hold",
      "Investigate cause: antenna (L1)? Interference (L2)? Firmware (L5)?",
    ],
    outcome: "Drone stabilised manually. Pilot brings it home using visual reference.",
    levelApplicable: [1, 2, 3],
  },
  {
    id: "ep4", trigger: "Video feed lost (pilot can't see)", severity: "warning",
    immediateAction: "Switch to RTH mode immediately. Don't try to fly blind.",
    steps: [
      "Pilot notices frozen/black video \u2192 switch to RTL on RC",
      "Telemetry radio should still show position on GCS map",
      "Spotter maintains visual contact and gives verbal guidance",
      "Drone follows RTH path at safe altitude",
      "Once drone is overhead and visible: switch to LOITER, then LAND manually",
      "Diagnose: camera (L1)? Encoding (L5)? WiFi (L3)? Antenna (L1)?",
    ],
    outcome: "Drone returns home via telemetry guidance. Video investigated on ground.",
    levelApplicable: [1, 2, 3],
  },
  {
    id: "ep5", trigger: "Drone behaves erratically (oscillation, drift, wrong direction)", severity: "critical",
    immediateAction: "Switch to STABILIZE mode. If controllable, land. If not, KILL SWITCH.",
    steps: [
      "Pilot detects abnormal behaviour: oscillation, uncommanded movement, altitude change",
      "Step 1: Switch to STABILIZE (manual control, no GPS dependency)",
      "Step 2: If stable in STABILIZE \u2192 gently descend and land",
      "Step 3: If still unstable \u2192 assess risk to people/property",
      "Step 4: If clear area below \u2192 LAND mode (auto-descend)",
      "Step 5: If danger to people \u2192 KILL SWITCH (motors off immediately)",
      "KILL SWITCH = last resort. Drone WILL fall. Only use if crash is safer than continued flight.",
    ],
    outcome: "Drone landed or crashed in safe area. Investigate: PIDs (L5)? IMU (L2)? Motor (L1)?",
    levelApplicable: [1, 2, 3],
  },
  {
    id: "ep6", trigger: "CV false positive: drone approaches wrong target (L2/L3)", severity: "caution",
    immediateAction: "Pilot rejects detection via GCS. Drone resumes search pattern.",
    steps: [
      "CV triggers detection alert on GCS with crop image + confidence score",
      "Pilot evaluates: is this a real person or false positive?",
      "If false positive: click 'Reject' \u2192 drone exits loiter, resumes waypoints",
      "If uncertain: request higher-res image or manual fly-over",
      "If drone is in autonomous mode (L3): override to GUIDED, inspect manually",
      "Log false positive for model improvement (image + GPS + conditions)",
    ],
    outcome: "False detection handled gracefully. Search continues. Data captured for model improvement.",
    levelApplicable: [2, 3],
  },
  {
    id: "ep7", trigger: "Autonomy malfunction: drone does unexpected action (L3)", severity: "critical",
    immediateAction: "TAKE MANUAL CONTROL IMMEDIATELY via RC. Switch to STABILIZE or LOITER.",
    steps: [
      "Pilot detects: drone flying wrong direction, landing in wrong spot, not responding to mission commands",
      "Step 1: RC override \u2192 STABILIZE or LOITER (regain control)",
      "Step 2: Assess situation: is drone safe? Position? Battery?",
      "Step 3: If safe to continue manually: fly home under pilot control",
      "Step 4: If unsure: LAND at current position",
      "Step 5: Retrieve and diagnose: state machine bug? Sensor error? Planning error?",
      "RC override ALWAYS takes priority over autonomous commands \u2014 this is hardcoded in ArduPilot",
    ],
    outcome: "Pilot regains control. Autonomous mode disabled. Investigate root cause before re-enabling.",
    levelApplicable: [3],
  },
];

// ═══════════════════════════════════════════════════════════
// Mission Risks + Mitigations
// ═══════════════════════════════════════════════════════════

export const MISSION_RISKS: MissionRisk[] = [
  { id: "r1", risk: "Complete loss of power mid-flight (battery failure)", likelihood: 1, impact: 5, category: "safety",
    mitigation: "Pre-flight voltage check, battery health monitoring, conservative voltage thresholds, quality LiPo batteries",
    residualRisk: "Very low. Modern LiPos with health monitoring rarely fail catastrophically.", owner: "hw", levelApplicable: [1, 2, 3] },
  { id: "r2", risk: "Fly-away (loss of control + GPS in wrong direction)", likelihood: 2, impact: 4, category: "safety",
    mitigation: "Geofence with LAND action, compass calibration, pre-flight GPS fix check, RC failsafe to RTH",
    residualRisk: "Low. ArduPilot geofence is proven. Compass interference is the main trigger \u2014 keep wires away.", owner: "fd", levelApplicable: [1, 2, 3] },
  { id: "r3", risk: "Mid-air collision with obstacle or bird", likelihood: 2, impact: 4, category: "environmental",
    mitigation: "Flight altitude >30m above obstacles, spotter with visual contact, avoid bird migration areas",
    residualRisk: "Moderate. No onboard obstacle detection at L1-L2. Spotter is the primary mitigation.", owner: "pm", levelApplicable: [1, 2, 3] },
  { id: "r4", risk: "Pi thermal throttling degrades CV performance", likelihood: 3, impact: 3, category: "technical",
    mitigation: "Active cooling (heatsink + fan), thermal monitoring, throttle workload if temp > 80\u00B0C",
    residualRisk: "Manageable. Pi 5 with active cooling handles YOLOv5n. Monitor in real-time.", owner: "cv", levelApplicable: [2, 3] },
  { id: "r5", risk: "CV misses target (false negative)", likelihood: 3, impact: 3, category: "technical",
    mitigation: "Overlapping search grid (no gaps), lower confidence threshold, multiple passes, human backup",
    residualRisk: "Moderate. Altitude + lighting conditions are unpredictable. Redundant search patterns help.", owner: "cv", levelApplicable: [2, 3] },
  { id: "r6", risk: "RF interference at demo/competition venue", likelihood: 3, impact: 3, category: "environmental",
    mitigation: "Frequency scan before flight, use 900MHz ELRS (less crowded), have backup frequency",
    residualRisk: "Moderate. Venues with many drones are noisy. ELRS handles this better than 2.4GHz.", owner: "hw", levelApplicable: [1, 2, 3] },
  { id: "r7", risk: "Weather: wind exceeds drone capability", likelihood: 2, impact: 3, category: "environmental",
    mitigation: "Check forecast, set wind speed limits (abort if >25 km/h), test in wind beforehand",
    residualRisk: "Low. Weather is checkable. Don't fly in bad conditions.", owner: "pm", levelApplicable: [1, 2, 3] },
  { id: "r8", risk: "Precision landing fails, payload not delivered", likelihood: 3, impact: 2, category: "technical",
    mitigation: "Practice landing sequence, ArUco marker testing at various heights, fallback: manual landing",
    residualRisk: "Moderate at L3. Vision-based landing is the hardest autonomous task. Manual backup essential.", owner: "fd", levelApplicable: [3] },
  { id: "r9", risk: "Payload release mechanism jams", likelihood: 2, impact: 2, category: "technical",
    mitigation: "Test servo 100+ times on ground, use simple mechanism (gravity-assisted), carry spare servo",
    residualRisk: "Low. Simple servo mechanisms are reliable. Over-engineering this is unnecessary.", owner: "hw", levelApplicable: [3] },
  { id: "r10", risk: "Team member unavailable (illness, schedule conflict)", likelihood: 3, impact: 3, category: "operational",
    mitigation: "Cross-training: each member documents their work, at least one backup person knows each system",
    residualRisk: "Moderate. Knowledge sharing is key. No single-person dependencies.", owner: "pm", levelApplicable: [1, 2, 3] },
  { id: "r11", risk: "Autonomous state machine enters invalid state (L3)", likelihood: 2, impact: 4, category: "technical",
    mitigation: "SITL testing of all state transitions, watchdog timer, fallback to LOITER on any invalid state",
    residualRisk: "Low if thoroughly tested. SITL catches most bugs. Real-world edge cases need field testing.", owner: "fd", levelApplicable: [3] },
  { id: "r12", risk: "WiFi/telemetry range exceeded during mission", likelihood: 3, impact: 2, category: "operational",
    mitigation: "Pre-flight range check, directional antennas, failsafe RTH on link loss, edge CV continues independently",
    residualRisk: "Low at L2+ (edge CV works without link). Higher at L1 (no CV, no video = blind).", owner: "gcs", levelApplicable: [1, 2, 3] },
];
