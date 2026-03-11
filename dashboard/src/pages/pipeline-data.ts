// pipeline-data.ts — Mission pipeline stages and design alternatives

// ═══════════════════════════════════════════════════════════
//  MISSION GOAL — The big picture (displayed at top of Pipeline tab)
// ═══════════════════════════════════════════════════════════

export interface MissionRule {
  id: string;
  text: string;
  severity: "shall" | "should";
  tag: string;
}

export const MISSION_GOAL = {
  holyGrail: "Search the Fenswood Wilderness for a missing hiker (mannequin dummy). Detect and report items of interest (clothing, equipment) scattered in the field. When a PLB signal arrives mid-search, redirect to the Focus Area. Locate the casualty, land within 5–10m, deploy a first aid kit via Tarot release, and return to the Take-Off Location. Avoid the SSSI no-fly zone at all times.",
  module: "AENGM0074 — Group Design Project",
  location: "Fenswood Farm, Failand, North Somerset",
  scene: [
    "A mannequin dummy (the 'casualty') lies somewhere in the search area, dressed in hiker clothing.",
    "Scattered around the area are items of interest — clothing, equipment, bags — that the drone must also detect, log (GPS + image), and report.",
    "The SSSI (rare bird nesting site) is fenced off and inside the search area — must NOT be overflown.",
    "5–15 minutes into the search, a PLB signal gives a narrower Focus Area to prioritise.",
    "The field contains hedgerows, uneven terrain, and potential false positives (animals, debris).",
  ],
  rules: [
    { id: "R01", text: "Fly only within the Flight Area", severity: "shall" as const, tag: "BOUNDARY" },
    { id: "R02", text: "Do not fly over the SSSI", severity: "shall" as const, tag: "SSSI" },
    { id: "R03", text: "Take off within 5m of the defined Take-Off Location", severity: "shall" as const, tag: "TAKEOFF" },
    { id: "R04", text: "Do not exceed 50m altitude above TOL ground level", severity: "shall" as const, tag: "ALT" },
    { id: "R05", text: "Search the Search Area and identify items of interest (clothing, equipment)", severity: "shall" as const, tag: "SEARCH" },
    { id: "R06", text: "On PLB activation (5–15 min in), redirect to Focus Area (3–10 GPS coords)", severity: "shall" as const, tag: "PLB" },
    { id: "R07", text: "Land within 10m but NOT within 5m of casualty, deploy first aid kit, return to TOL", severity: "shall" as const, tag: "LAND" },
    { id: "R08", text: "Autonomy level and interface format determined and justified by Company", severity: "shall" as const, tag: "DESIGN" },
    { id: "R09", text: "All interfaces include RTH and Motor Cutoff commands + failsafes", severity: "shall" as const, tag: "SAFETY" },
    { id: "R10", text: "Report lat/lon + images of all items of interest AND the casualty", severity: "shall" as const, tag: "REPORT" },
    { id: "R11", text: "Designated Company Pilot, supervised by Flight Lab Safety Pilot", severity: "shall" as const, tag: "OPS" },
    { id: "R12", text: "All software + flight logs on public GitHub (MIT licence)", severity: "shall" as const, tag: "DELIVER" },
  ],
  constraints: [
    "SSSI no-fly zone INSIDE the search area — must be geofenced and never overflown (R02)",
    "PLB signal arrives 5–15 min into search — drone must redirect to Focus Area (R06)",
    "Items of interest (clothing, equipment) must be detected, geotagged, and reported (R05, R10)",
    "Land 5–10m from casualty (NOT closer than 5m, NOT further than 10m) (R07)",
    "Deploy first aid kit via Tarot release mechanism, then RTL (R07)",
    "50m max altitude above TOL ground level (R04)",
    "Flight Lab Safety Pilot has ultimate authority — RC kill switch always overrides (R09, R11)",
    "~15–20 min battery — entire mission in one flight",
    "Flight Area geofence — do NOT leave the boundary (R01)",
  ],
};

// ═══════════════════════════════════════════════════════════
//  TYPES
// ═══════════════════════════════════════════════════════════

export type ApproachStatus = "selected" | "available" | "planned" | "research" | "rejected";

export interface Approach {
  id: string;
  name: string;
  subtitle: string;
  status: ApproachStatus;
  scores: { speed: number; accuracy: number; reliability: number; simplicity: number; cost: number }; // 1-5 each
  pros: string[];
  cons: string[];
  notes?: string;
  depends?: string[];  // what this approach relies on (e.g. "GPS 3D fix", "CV detection working")
}

export interface Stage {
  id: string;
  number: number;
  name: string;
  subGoal: string;
  phase: "pre-mission" | "flight" | "action";
  icon: string;
  requirements?: string[];  // R01, R04, etc. — which rules this stage addresses
  approaches: Approach[];
}

export const PHASE_COLORS: Record<string, { bg: string; text: string; border: string }> = {
  "pre-mission": { bg: "bg-amber-500/8", text: "text-amber-400", border: "border-amber-500/30" },
  "flight":      { bg: "bg-cyan-500/8",   text: "text-cyan-400",   border: "border-cyan-500/30" },
  "action":      { bg: "bg-purple-500/8",  text: "text-purple-400",  border: "border-purple-500/30" },
};

export const STATUS_COLORS: Record<ApproachStatus, { bg: string; text: string; border: string; label: string }> = {
  selected:  { bg: "bg-emerald-500/10", text: "text-emerald-400", border: "border-emerald-500/50", label: "SELECTED" },
  available: { bg: "bg-zinc-800/40",    text: "text-zinc-400",    border: "border-zinc-700",       label: "AVAILABLE" },
  planned:   { bg: "bg-blue-500/8",     text: "text-blue-400",    border: "border-blue-500/30",    label: "PLANNED" },
  research:  { bg: "bg-purple-500/8",   text: "text-purple-400",  border: "border-purple-500/30",  label: "RESEARCH" },
  rejected:  { bg: "bg-red-500/5",      text: "text-red-400/60",  border: "border-red-500/20",     label: "REJECTED" },
};

export const SCORE_LABELS = ["speed", "accuracy", "reliability", "simplicity", "cost"] as const;

// ═══════════════════════════════════════════════════════════
//  DESIGN CHOICES — Every configurable parameter & decision
// ═══════════════════════════════════════════════════════════

export interface DesignChoice {
  id: string;
  name: string;
  currentValue: string;
  unit?: string;
  alternatives?: string[];
  tuningNotes: string;
  configFile: string;
  configKey?: string;
}

export interface DesignCategory {
  category: string;
  icon: string;
  choices: DesignChoice[];
}

export const DESIGN_CHOICES: DesignCategory[] = [
  {
    category: "Camera & Sensor",
    icon: "📸",
    choices: [
      {
        id: "cam-resolution", name: "Camera Resolution",
        currentValue: "640 × 480", unit: "px",
        alternatives: ["320×240 (faster inference, less detail)", "1280×720 (more detail, slower)", "1920×1080 (full HD, very slow on Pi)"],
        tuningNotes: "Lower = faster inference, higher = detect from higher altitude. 640×480 is the sweet spot for Pi 5 TFLite at ~4 FPS.",
        configFile: "config.py", configKey: "IMAGE_W / IMAGE_H",
      },
      {
        id: "cam-fps", name: "Camera Capture FPS",
        currentValue: "30", unit: "FPS",
        alternatives: ["15 (save CPU for inference)", "60 (if using hardware acceleration)"],
        tuningNotes: "Camera captures at 30 but inference bottleneck is ~4 FPS (TFLite). Excess frames are dropped. Lower capture FPS saves CPU.",
        configFile: "vision.py", configKey: "hardcoded in PiCameraBackend",
      },
      {
        id: "cam-sensor-width", name: "Sensor Width",
        currentValue: "5.02", unit: "mm",
        alternatives: ["Calibrate with tests/calibration/fov_calibrate.py"],
        tuningNotes: "IMX296 global shutter. Used in GSD calculation: GSD = (sensor_width × altitude) / (focal_length × image_width). Wrong value = wrong GPS estimate.",
        configFile: "config.py", configKey: "SENSOR_WIDTH_MM",
      },
      {
        id: "cam-focal-length", name: "Focal Length",
        currentValue: "5.46", unit: "mm",
        alternatives: ["6.0 (original estimate)", "Calibrate with fov_calibrate.py"],
        tuningNotes: "Combined with sensor width determines FOV. Directly affects GPS estimation accuracy. Must calibrate on actual hardware.",
        configFile: "config.py", configKey: "FOCAL_LENGTH_MM",
      },
      {
        id: "cam-flip", name: "Camera Flip 180°",
        currentValue: "True",
        tuningNotes: "Camera mounted upside-down on drone frame. Flip in software. Set False if mounted normally.",
        configFile: "config.py", configKey: "CAMERA_FLIP_180",
      },
      {
        id: "cam-color", name: "Color Space",
        currentValue: "BGR (raw from IMX296)",
        alternatives: ["RGB (would need cvtColor)"],
        tuningNotes: "IMX296 outputs BGR despite picamera2 labeling it RGB888. Do NOT add cvtColor conversion — data is already BGR for OpenCV.",
        configFile: "vision.py", configKey: "N/A — no conversion applied",
      },
    ],
  },
  {
    category: "AI Model & Detection",
    icon: "🧠",
    choices: [
      {
        id: "model-arch", name: "Model Architecture",
        currentValue: "YOLOv8n (nano)",
        alternatives: ["YOLOv8s (small, more accurate, slower)", "YOLO11n (newer, faster)", "YOLO26n (bleeding edge)"],
        tuningNotes: "Nano is smallest/fastest. Each step up: ~2× slower, ~5-10% better mAP. Pi 5 can barely handle nano at 4 FPS.",
        configFile: "best.tflite", configKey: "model file swap",
      },
      {
        id: "model-format", name: "Inference Backend",
        currentValue: "TFLite (float32)",
        alternatives: ["NCNN (3× faster on ARM)", "FP16 TFLite (~2× faster)", "INT8 TFLite (no speedup on Pi 5)", "Hailo-8L NPU (60+ FPS, $70)"],
        tuningNotes: "TFLite is reliable baseline. NCNN is top priority upgrade (83ms vs 250ms). INT8 gives ZERO speedup on ARM — skip it. Hailo needs hardware.",
        configFile: "vision.py", configKey: "backend selection logic",
      },
      {
        id: "model-input", name: "Model Input Size",
        currentValue: "640 × 640", unit: "px",
        alternatives: ["320×320 (2-4× faster, less accurate)", "480×480 (compromise)"],
        tuningNotes: "Image resized from camera 640×480 to model 640×640 (letterboxed). Smaller input = faster but misses small targets at altitude.",
        configFile: "best.tflite", configKey: "baked into model at export",
      },
      {
        id: "conf-threshold", name: "Confidence Threshold",
        currentValue: "0.4",
        alternatives: ["0.25 (catch more, more false positives)", "0.3 (balanced)", "0.5 (fewer false positives, miss weak detections)"],
        tuningNotes: "0.4 = 50/50 detection at 0.966 confidence on bench. Try 0.25-0.3 outdoors where lighting varies. Lower catches more but needs better classification.",
        configFile: "config.py", configKey: "CONFIDENCE_THRESHOLD",
      },
      {
        id: "model-warmup", name: "Warmup Frames",
        currentValue: "10",
        tuningNotes: "First N frames after model load are slow (JIT compilation, cache warm). Skip these before timing. Doesn't affect flight.",
        configFile: "vision.py", configKey: "hardcoded",
      },
      {
        id: "model-normalize", name: "Input Normalization",
        currentValue: "÷ 255.0 (0–1 range)",
        tuningNotes: "YOLOv8 TFLite expects float32 input in 0–1 range. COCO model may expect 0–255. Check model metadata before swapping.",
        configFile: "vision.py", configKey: "hardcoded in detect_in_image()",
      },
    ],
  },
  {
    category: "Flight Parameters",
    icon: "✈️",
    choices: [
      {
        id: "flight-search-alt", name: "Search Altitude",
        currentValue: "30", unit: "m AGL",
        alternatives: ["20 (better detection, slower coverage)", "25 (compromise)", "40 (wider coverage, harder detection)"],
        tuningNotes: "Higher = wider FOV = faster coverage but smaller target in frame. Must verify detection works at chosen altitude. FOV at 30m ≈ 25m × 19m.",
        configFile: "config.py", configKey: "TARGET_ALT",
      },
      {
        id: "flight-verify-alt", name: "Verify/Investigate Altitude",
        currentValue: "15", unit: "m AGL",
        alternatives: ["10 (clearer image, risk of obstacle)", "20 (safer, less detail)"],
        tuningNotes: "Drone descends here after detection to let operator verify. Lower = clearer image = better classification. Must stay above obstacles.",
        configFile: "config.py", configKey: "VERIFY_ALT",
      },
      {
        id: "flight-search-speed", name: "Search Speed",
        currentValue: "10", unit: "m/s",
        alternatives: ["5 (more frames per ground area)", "7 (compromise)", "15 (fast but may miss targets)"],
        tuningNotes: "At 10 m/s + 4 FPS: 1 frame per 2.5m traveled. FOV width ~25m at 30m alt → each strip gets ~10 frames. Lower speed = more detections but uses more battery.",
        configFile: "config.py", configKey: "SEARCH_SPEED_MPS",
      },
      {
        id: "flight-wp-radius", name: "Waypoint Accept Radius",
        currentValue: "5", unit: "m",
        alternatives: ["3 (tighter turns, slower)", "8 (looser, faster coverage)", "10 (very loose)"],
        tuningNotes: "How close drone must get to waypoint before moving to next. Smaller = better coverage but slower + more battery. 5m balances coverage and speed.",
        configFile: "config.py", configKey: "WP_RADIUS",
      },
      {
        id: "flight-overlap", name: "Search Strip Overlap",
        currentValue: "20", unit: "%",
        alternatives: ["10% (faster, risk gaps)", "30% (thorough, slower)", "50% (very thorough, doubles time)"],
        tuningNotes: "Accounts for GPS drift + wind pushing drone off planned track. 20% overlap means adjacent strips share 20% of FOV width.",
        configFile: "planning.py", configKey: "overlap parameter",
      },
      {
        id: "flight-max-alt", name: "Maximum Altitude (R04)",
        currentValue: "50", unit: "m AGL",
        alternatives: ["Not configurable — set by assessment rules"],
        tuningNotes: "Hard limit from AENGM0074 R04. Must not exceed 50m above TOL ground level. RTL altitude should be below this.",
        configFile: "config.py", configKey: "MAX_ALT (enforced in state machine)",
      },
      {
        id: "flight-land-offset", name: "Landing Offset from Casualty",
        currentValue: "7.5", unit: "m",
        alternatives: ["6 (closer, risk <5m with GPS error)", "8 (safer margin)", "9 (near outer limit of 10m zone)"],
        tuningNotes: "R07 requires 5-10m. 7.5m is center of zone. GPS error ±2-3m still keeps us in range. Operator picks N/E/S/W direction.",
        configFile: "simple_simulator.py / pi_flight.py", configKey: "LANDING_OFFSET_M",
      },
    ],
  },
  {
    category: "GPS & Navigation",
    icon: "🛰️",
    choices: [
      {
        id: "gps-min-sats", name: "Minimum Satellites for Arm",
        currentValue: "8",
        alternatives: ["6 (minimum for 3D fix)", "10 (better accuracy)", "12 (high confidence)"],
        tuningNotes: "More sats = better accuracy. 8 is safe minimum for outdoor flight. Pre-flight check verifies GPS fix quality.",
        configFile: "config.py", configKey: "MIN_SATS",
      },
      {
        id: "gps-hdop", name: "Max HDOP for Arm",
        currentValue: "2.0",
        alternatives: ["1.5 (stricter)", "3.0 (looser, may need in poor sky view)"],
        tuningNotes: "Horizontal Dilution of Precision. Lower = better. <1.0 excellent, 1-2 good, >5 poor. Don't fly with HDOP >3.",
        configFile: "config.py", configKey: "MAX_HDOP",
      },
      {
        id: "gps-cluster-radius", name: "Detection Cluster Radius",
        currentValue: "30", unit: "m",
        alternatives: ["15 (tighter, may split one target)", "50 (looser, may merge nearby targets)"],
        tuningNotes: "Detections within this radius are considered the same target. Must be larger than GPS drift but smaller than distance between real targets.",
        configFile: "simple_simulator.py", configKey: "CLUSTER_RADIUS_M",
      },
      {
        id: "gps-max-obs", name: "Max Observations per Cluster",
        currentValue: "50",
        alternatives: ["20 (faster convergence estimate)", "100 (more data, slower)"],
        tuningNotes: "After N observations, oldest are discarded (FIFO). Inverse variance weighting means recent accurate readings dominate anyway.",
        configFile: "simple_simulator.py", configKey: "MAX_OBS",
      },
      {
        id: "gps-kalman", name: "Kalman Filter for GPS Estimate",
        currentValue: "Enabled (process noise 0.5, measurement noise varies)",
        alternatives: ["Simple average (less accurate but simpler)", "Particle filter (better for non-Gaussian noise)"],
        tuningNotes: "Kalman smooths GPS estimate. Process noise 0.5 = slow response to real changes. Measurement noise varies by detection confidence.",
        configFile: "simple_simulator.py / pi_flight.py", configKey: "KalmanFilter class",
      },
    ],
  },
  {
    category: "Altitude & Terrain",
    icon: "📏",
    choices: [
      {
        id: "alt-source", name: "Altitude Source for Landing",
        currentValue: "Barometric (relative to launch)",
        alternatives: ["Rangefinder/Lidar (true AGL — actual distance to ground)", "GPS altitude (least accurate, ±5m)", "Fused baro+rangefinder (ArduCopter EKF)"],
        tuningNotes: "Barometric gives altitude relative to takeoff point. If terrain is uneven (hills, slopes), baro altitude ≠ actual height above ground. Rangefinder gives true distance to ground — critical for low-altitude payload drop and safe landing on varied terrain.",
        configFile: "ArduCopter params", configKey: "RNGFND_LANDING / EK3_RNG_USE_HGT",
      },
      {
        id: "alt-rangefinder", name: "Rangefinder/Lidar Sensor",
        currentValue: "Available (model TBD)",
        alternatives: ["TFmini-S (~$30, 12m range, lightweight)", "TFmini Plus (~$40, 12m range)", "VL53L1X (~$5, 4m max — too short)", "Benewake TF-Luna (~$20, 8m range)"],
        tuningNotes: "Team has a lidar/rangefinder available. Needs mounting, wiring to Cube I2C/serial, ArduCopter RNGFND params. Gives true AGL for landing and payload drop. Can also deduce terrain elevation: GPS alt − rangefinder reading = ground level at that point.",
        configFile: "ArduCopter params", configKey: "RNGFND1_TYPE / RNGFND1_MAX_CM / RNGFND1_MIN_CM",
      },
      {
        id: "alt-terrain-deduce", name: "Terrain Elevation Deduction",
        currentValue: "Not implemented",
        alternatives: ["Record GPS alt + rangefinder reading at each point → build terrain map", "Pre-load terrain data from map"],
        tuningNotes: "If we have both GPS altitude (above sea level) and rangefinder (above ground), we can calculate: ground_elevation = gps_alt − rangefinder. Useful for knowing if the ground slopes near the casualty before committing to land/drop.",
        configFile: "Custom logic", configKey: "Not yet implemented",
      },
    ],
  },
  {
    category: "Safety & Failsafes",
    icon: "🛡️",
    choices: [
      {
        id: "safe-rtl-alt", name: "RTL Altitude",
        currentValue: "30", unit: "m",
        alternatives: ["40 (safer, avoids SSSI overfly risk)", "50 (max allowed)"],
        tuningNotes: "Altitude drone climbs to before flying home. Must clear all obstacles and ideally be above SSSI risk altitude.",
        configFile: "Mission Planner param", configKey: "RTL_ALT",
      },
      {
        id: "safe-battery-failsafe", name: "Battery Failsafe Level",
        currentValue: "30%",
        alternatives: ["25% (more flight time, riskier)", "35% (conservative)"],
        tuningNotes: "Triggers RTL when battery drops below this. Must have enough remaining to fly home from furthest point.",
        configFile: "Mission Planner param", configKey: "BATT_LOW_VOLT / BATT_FS_LOW_ACT",
      },
      {
        id: "safe-link-loss", name: "Link Loss Failsafe",
        currentValue: "RTL after 3s",
        alternatives: ["Continue mission (risky)", "Land immediately (safe but may land in SSSI)", "Hover and wait (uses battery)"],
        tuningNotes: "What happens if Pi → Cube link drops. RTL is safest. Cube handles this natively via GCS_FS params.",
        configFile: "Mission Planner param", configKey: "FS_GCS_ENABLE",
      },
      {
        id: "safe-geofence", name: "Geofence Action",
        currentValue: "RTL on breach",
        alternatives: ["Loiter at boundary", "Land immediately", "Report only (dangerous)"],
        tuningNotes: "Upload Flight Area (R01) as inclusion fence + SSSI (R02) as exclusion fence in Mission Planner. Hardware-enforced.",
        configFile: "Mission Planner param", configKey: "FENCE_ACTION / FENCE_ENABLE",
      },
      {
        id: "safe-rc-override", name: "RC Override (Kill Switch)",
        currentValue: "Always active — any RC input overrides code",
        tuningNotes: "Safety pilot can take over at any time by moving RC sticks. Flight mode switch to STABILIZE/LOITER for instant manual control. Non-negotiable.",
        configFile: "ArduCopter default behavior", configKey: "N/A — always on",
      },
    ],
  },
  {
    category: "Communication & Ground Station",
    icon: "📡",
    choices: [
      {
        id: "comm-cube-baud", name: "Cube Serial Baud Rate",
        currentValue: "921600",
        alternatives: ["115200 (safer, slower)", "57600 (most compatible)"],
        tuningNotes: "Higher = faster telemetry. 921600 works reliably with mavproxy UDP bridge. Direct serial from Python 3.13 is broken (use mavproxy).",
        configFile: "config.py", configKey: "BAUD_RATE",
      },
      {
        id: "comm-stream-rate", name: "MAVLink Stream Rate",
        currentValue: "10", unit: "Hz",
        alternatives: ["4 (save bandwidth)", "20 (more responsive but more CPU)"],
        tuningNotes: "How often Cube sends GPS/attitude/battery data. 10 Hz = new GPS position every 100ms. Good balance of responsiveness and bandwidth.",
        configFile: "mavproxy --streamrate", configKey: "mavproxy flag",
      },
      {
        id: "comm-video-quality", name: "MJPEG Stream Quality",
        currentValue: "85%",
        alternatives: ["50% (faster, blurrier)", "70% (compromise)", "95% (sharp, slow)"],
        tuningNotes: "JPEG quality for web stream to operator. Lower = less bandwidth = smoother stream over WiFi. 85% is good balance.",
        configFile: "pi_flight.py", configKey: "cv2.imencode quality param",
      },
      {
        id: "comm-web-port", name: "Ground Station Web Port",
        currentValue: "8090",
        alternatives: ["8080 (common, may conflict)", "5000 (Flask default)"],
        tuningNotes: "Browser connects to http://PI_IP:8090 for live video, commands, and status. capture_training.py uses 8091 to avoid conflict.",
        configFile: "pi_flight.py / passive_watch.py", configKey: "PORT constant",
      },
    ],
  },
];

export const PIPELINE: Stage[] = [
  // ══════════════════════════════════════════════
  //  PHASE: PRE-MISSION
  // ══════════════════════════════════════════════
  {
    id: "preflight", number: 1, name: "Preflight Check", phase: "pre-mission", icon: "🔍",
    subGoal: "Confirm all subsystems operational before arming",
    requirements: ["R09"],
    approaches: [
      {
        id: "preflight-script", name: "preflight.py Script", subtitle: "Automated HW checks",
        status: "selected",
        scores: { speed: 4, accuracy: 4, reliability: 4, simplicity: 4, cost: 5 },
        pros: ["Automated camera/Cube/GPS/model checks", "Pass/fail per subsystem", "Runs in 10s"],
        cons: ["No abort enforcement — operator can ignore failures"],
      },
      {
        id: "preflight-paper", name: "Paper Checklist", subtitle: "Manual walk-through",
        status: "available",
        scores: { speed: 2, accuracy: 3, reliability: 2, simplicity: 5, cost: 5 },
        pros: ["No software needed", "Works with no power"],
        cons: ["Easy to skip items", "No automated verification"],
      },
      {
        id: "preflight-gate", name: "Software Gate", subtitle: "main.py refuses to arm until all pass",
        status: "planned",
        scores: { speed: 4, accuracy: 5, reliability: 5, simplicity: 3, cost: 5 },
        pros: ["Cannot fly with broken subsystem", "Enforced safety"],
        cons: ["May block in edge cases", "Needs all checks implemented"],
      },
    ],
  },
  {
    id: "search-area", number: 2, name: "Search Area & Geofencing", phase: "pre-mission", icon: "📐",
    subGoal: "Define search polygon, SSSI exclusion zone, and flight boundary (R01, R02)",
    requirements: ["R01", "R02", "R03"],
    approaches: [
      {
        id: "area-kml", name: "KML File Import", subtitle: "Load AENGM0074.kml — all zones pre-defined",
        status: "selected",
        scores: { speed: 5, accuracy: 5, reliability: 5, simplicity: 4, cost: 5 },
        pros: ["Standard format", "Pre-defined by assessment", "Includes SSSI + flight area + survey area"],
        cons: ["Not editable in field without laptop"],
        notes: "KML contains: Flight Area boundary (R01), SSSI no-fly zone (R02), Survey Area, Focus Area, TOL.",
      },
      {
        id: "area-draw", name: "Interactive Drawing", subtitle: "draw_search_area.py on laptop",
        status: "available",
        scores: { speed: 3, accuracy: 4, reliability: 3, simplicity: 3, cost: 5 },
        pros: ["Visual, intuitive", "Field-adjustable"],
        cons: ["Needs display (laptop)", "Not headless", "Must manually exclude SSSI"],
      },
      {
        id: "area-config", name: "Hardcoded Config", subtitle: "GPS coords in config.py",
        status: "available",
        scores: { speed: 5, accuracy: 3, reliability: 5, simplicity: 5, cost: 5 },
        pros: ["Zero setup", "Always available as fallback"],
        cons: ["Inflexible", "Requires code change to update"],
      },
      {
        id: "area-mp", name: "Mission Planner Geofence", subtitle: "ArduCopter inclusion/exclusion zones",
        status: "planned",
        scores: { speed: 3, accuracy: 5, reliability: 5, simplicity: 3, cost: 5 },
        pros: ["Hardware-enforced geofence", "Cube rejects commands outside boundary", "Industry standard"],
        cons: ["Separate software", "Extra setup step"],
        notes: "Upload Flight Area as inclusion fence + SSSI as exclusion fence. Cube enforces automatically.",
      },
    ],
  },
  {
    id: "path-planning", number: 3, name: "Path Planning", phase: "pre-mission", icon: "🗺️",
    subGoal: "Generate flight path covering search area, excluding SSSI, within battery (R01, R02, R04, R05)",
    requirements: ["R01", "R02", "R04", "R05"],
    approaches: [
      {
        id: "path-lawnmower", name: "Lawnmower Pattern", subtitle: "Boustrophedon, 20% overlap, SSSI-excluded",
        status: "selected",
        scores: { speed: 4, accuracy: 5, reliability: 5, simplicity: 4, cost: 5 },
        pros: ["100% coverage guaranteed", "Predictable timing", "Simple math", "Can clip waypoints outside SSSI"],
        cons: ["Inefficient for irregular shapes", "No adaptation to detections"],
        notes: "Auto-aligns to longest polygon edge (PCA). 20% overlap for GPS drift. Waypoints inside SSSI polygon are skipped.",
        depends: ["Search area polygon defined", "SSSI boundary loaded", "Flight area boundary loaded"],
      },
      {
        id: "path-spiral", name: "Spiral Inward", subtitle: "Converge to center",
        status: "available",
        scores: { speed: 3, accuracy: 3, reliability: 3, simplicity: 3, cost: 5 },
        pros: ["Natural convergence", "Good for round areas"],
        cons: ["Poor edge coverage", "Harder overlap math", "Hard to exclude SSSI"],
      },
      {
        id: "path-adaptive", name: "Adaptive Re-plan", subtitle: "Re-route on detection or PLB",
        status: "research",
        scores: { speed: 4, accuracy: 4, reliability: 2, simplicity: 1, cost: 5 },
        pros: ["Concentrates on detection clusters", "Battery-efficient", "Natural PLB redirect"],
        cons: ["Complex real-time replanning", "Risk of missing areas"],
      },
      {
        id: "path-operator", name: "Operator-Guided", subtitle: "Manual joystick/waypoints",
        status: "available",
        scores: { speed: 2, accuracy: 3, reliability: 3, simplicity: 5, cost: 5 },
        pros: ["Human intuition", "Adapts to visual cues"],
        cons: ["Slow, fatiguing", "Inconsistent coverage"],
      },
    ],
  },

  // ══════════════════════════════════════════════
  //  PHASE: FLIGHT
  // ══════════════════════════════════════════════
  {
    id: "takeoff", number: 4, name: "Takeoff & Transit", phase: "flight", icon: "🛫",
    subGoal: "Arm within 5m of TOL, climb to 30m, fly to first search waypoint (R03, R04)",
    requirements: ["R03", "R04"],
    approaches: [
      {
        id: "takeoff-guided", name: "GUIDED + pymavlink", subtitle: "Full Python control",
        status: "selected",
        scores: { speed: 4, accuracy: 4, reliability: 4, simplicity: 3, cost: 5 },
        pros: ["State tracking in Python", "Graceful abort possible"],
        cons: ["Requires reliable MAVLink link"],
        notes: "Arms in GUIDED mode, takeoff to TARGET_ALT (30m), transit at 15 m/s.",
      },
      {
        id: "takeoff-auto", name: "AUTO Mode Plan", subtitle: "Mission Planner waypoints",
        status: "available",
        scores: { speed: 5, accuracy: 5, reliability: 5, simplicity: 4, cost: 5 },
        pros: ["Cube handles everything", "Industry proven"],
        cons: ["Less Python control", "Harder to abort mid-mission"],
      },
      {
        id: "takeoff-manual", name: "Manual + Handoff", subtitle: "Pilot takes off, hands to code",
        status: "available",
        scores: { speed: 2, accuracy: 3, reliability: 5, simplicity: 5, cost: 5 },
        pros: ["Pilot confirms everything", "Safest for first flights"],
        cons: ["Requires skilled pilot", "Human delay"],
      },
    ],
  },
  {
    id: "search-scan", number: 5, name: "Search & Scan", phase: "flight", icon: "🔎",
    subGoal: "Fly waypoint path at 30m, 10 m/s, avoid SSSI, run CV continuously, log items of interest (R01, R02, R05)",
    requirements: ["R01", "R02", "R05"],
    approaches: [
      {
        id: "scan-guided-wp", name: "GUIDED Waypoints", subtitle: "Python sends each waypoint, skipping SSSI",
        status: "selected",
        scores: { speed: 3, accuracy: 4, reliability: 4, simplicity: 3, cost: 5 },
        pros: ["Can pause/redirect mid-leg (for PLB or detection)", "Python controls flow", "Easy SSSI avoidance (skip waypoints)"],
        cons: ["Slower than AUTO (command latency)", "More MAVLink traffic"],
        notes: "10 m/s search, 30m alt. planning.py generates waypoints from polygon. Waypoints inside SSSI skipped.",
        depends: ["GPS 3D fix", "Lawnmower waypoints generated", "SSSI boundary loaded"],
      },
      {
        id: "scan-auto", name: "AUTO + Servo Triggers", subtitle: "Cube flies, Pi watches",
        status: "available",
        scores: { speed: 5, accuracy: 4, reliability: 5, simplicity: 2, cost: 5 },
        pros: ["Smoother flight (native nav)", "Faster coverage"],
        cons: ["Hard to interrupt for PLB redirect", "Less Python control", "SSSI exclusion must be in Mission Planner"],
      },
      {
        id: "scan-adaptive-speed", name: "Adaptive Speed", subtitle: "Slow in interesting areas",
        status: "research",
        scores: { speed: 4, accuracy: 5, reliability: 3, simplicity: 1, cost: 5 },
        pros: ["More frames on targets", "Battery-efficient"],
        cons: ["Complex feedback loop", "Needs reliable detection to trigger"],
      },
    ],
  },
  {
    id: "plb-redirect", number: 6, name: "PLB Redirect", phase: "flight", icon: "📡",
    subGoal: "When PLB signal received (5–15 min in), redirect search to Focus Area (R06)",
    requirements: ["R06"],
    approaches: [
      {
        id: "plb-replan", name: "Re-Plan Lawnmower", subtitle: "Generate new waypoints for Focus Area polygon",
        status: "planned",
        scores: { speed: 4, accuracy: 5, reliability: 4, simplicity: 3, cost: 5 },
        pros: ["Systematic coverage of Focus Area", "Reuses existing planner", "Guaranteed coverage"],
        cons: ["Brief pause to regenerate waypoints", "May overlap already-searched ground"],
        notes: "Receive 3–10 GPS coords defining Focus Area. Generate new lawnmower pattern. Resume search in narrower area.",
        depends: ["Focus Area coords received (3–10 GPS points)", "Lawnmower planner working", "Mid-flight waypoint injection"],
      },
      {
        id: "plb-fly-to-center", name: "Fly to Center + Spiral", subtitle: "Fly to Focus Area centroid, spiral outward",
        status: "selected",
        scores: { speed: 5, accuracy: 3, reliability: 3, simplicity: 4, cost: 5 },
        pros: ["Fast response — fly straight to center", "Simple math"],
        cons: ["Coverage not guaranteed", "May miss edges"],
      },
      {
        id: "plb-operator", name: "Operator Redirect", subtitle: "Pilot manually directs drone to Focus Area",
        status: "available",
        scores: { speed: 2, accuracy: 4, reliability: 4, simplicity: 5, cost: 5 },
        pros: ["Pilot sees the map, makes judgement call", "Zero code needed"],
        cons: ["Slow, dependent on operator attention"],
      },
    ],
  },
  {
    id: "detection", number: 7, name: "Object Detection", phase: "flight", icon: "👁️",
    subGoal: "Detect casualty AND items of interest (clothing, equipment) from each frame (R05, R10)",
    requirements: ["R05", "R10"],
    approaches: [
      {
        id: "det-tflite-yolov8n", name: "TFLite YOLOv8n", subtitle: "Custom-trained, 4.8 FPS, 206ms",
        status: "selected",
        scores: { speed: 2, accuracy: 4, reliability: 4, simplicity: 4, cost: 5 },
        pros: ["Custom-trained on dummy", "3.2MB lightweight", "50/50 detection at 0.966"],
        cons: ["4.8 FPS limits search speed", "Synthetic training data only"],
        notes: "640x640 float32 input. XNNPACK CPU delegate. Conf threshold 0.4.",
      },
      {
        id: "det-ncnn", name: "NCNN YOLOv8n", subtitle: "~15 FPS, ARM NEON optimized",
        status: "planned",
        scores: { speed: 4, accuracy: 4, reliability: 3, simplicity: 3, cost: 5 },
        pros: ["3x faster than TFLite on Pi 5", "Same model accuracy"],
        cons: ["Ultralytics ARM64 export was blocked (v8.4+)", "Needs standalone inference code"],
        notes: "Export on laptop: .pt → .onnx → ncnn. pip install ncnn on Pi.",
      },
      {
        id: "det-fp16", name: "FP16 TFLite", subtitle: "~10 FPS, same model",
        status: "planned",
        scores: { speed: 3, accuracy: 4, reliability: 4, simplicity: 4, cost: 5 },
        pros: ["Pi 5 Cortex-A76 has native FP16", "~2x speedup, drop-in"],
        cons: ["May already be active (need to verify)", "Some ops fall back to FP32"],
      },
      {
        id: "det-coco", name: "COCO Person Detector", subtitle: "Pre-trained YOLOv8n, 80 classes",
        status: "available",
        scores: { speed: 2, accuracy: 3, reliability: 4, simplicity: 5, cost: 5 },
        pros: ["Pre-trained, robust person detection", "No custom training needed"],
        cons: ["13MB (larger)", "Not dummy-specific", "Slower"],
      },
      {
        id: "det-yolo11n", name: "YOLO11n + NCNN", subtitle: "~56ms, newer architecture",
        status: "research",
        scores: { speed: 5, accuracy: 5, reliability: 3, simplicity: 2, cost: 5 },
        pros: ["18 FPS on Pi 5", "Better accuracy (40.1 vs 37.3 mAP)"],
        cons: ["Requires full retrain", "Newer framework, less tested"],
      },
      {
        id: "det-hailo", name: "Hailo-8L AI HAT+", subtitle: "60+ FPS, dedicated NPU",
        status: "research",
        scores: { speed: 5, accuracy: 4, reliability: 3, simplicity: 1, cost: 2 },
        pros: ["80+ FPS", "Offloads CPU entirely"],
        cons: ["$70 hardware", "Complex toolchain", "Driver compatibility risk"],
      },
    ],
  },
  {
    id: "geotagging", number: 8, name: "Target Geotagging", phase: "flight", icon: "📍",
    subGoal: "Convert pixel detection into GPS coordinate for items of interest AND casualty (R10)",
    requirements: ["R10"],
    approaches: [
      {
        id: "geo-gsd", name: "Pixel-to-GPS Projection", subtitle: "GSD math + yaw rotation",
        status: "selected",
        scores: { speed: 5, accuracy: 3, reliability: 4, simplicity: 3, cost: 5 },
        pros: ["Instant (no hovering)", "Works during flight for items of interest", "Altitude-weighted"],
        cons: ["~3-5m error from GPS drift + yaw + altitude", "Edge pixels more error"],
        notes: "GSD = (sensor_width × alt) / (focal_length × image_width). Kalman filter smooths.",
        depends: ["GPS 3D fix active", "Altitude reading from Cube", "Yaw/heading from compass", "Camera FOV calibrated (focal length + sensor width)"],
      },
      {
        id: "geo-multiframe", name: "Multi-Frame Clustering", subtitle: "Kalman + inverse variance weighting",
        status: "selected",
        scores: { speed: 4, accuracy: 4, reliability: 4, simplicity: 2, cost: 5 },
        pros: ["Averages noise over many detections", "Converges to true position", "Works for casualty (multiple passes)"],
        cons: ["Needs multiple passes or slow speed", "Complex math"],
        notes: "In simulator + pi_flight. Clusters within 30m. Max 50 obs per cluster. Best for casualty position. Complementary with GSD projection — GSD for flyover items, multi-frame for casualty position. Both selected because they serve different purposes.",
        depends: ["GPS 3D fix", "Multiple detections of same target", "Spatial clustering algorithm"],
      },
      {
        id: "geo-hover-avg", name: "Hover + GPS Average", subtitle: "Fly above target, average 10-15s of GPS",
        status: "available",
        scores: { speed: 2, accuracy: 4, reliability: 4, simplicity: 5, cost: 5 },
        pros: ["Very simple", "Averages out GPS drift"],
        cons: ["Wastes battery hovering", "Needs CV centering first to be above target"],
        depends: ["GPS 3D fix", "CV visual servo (to center drone above target first)", "Stable hover capability"],
      },
      {
        id: "geo-visual-servo", name: "CV Feedback Centering", subtitle: "CV tells controller where to fly → center target in frame → read GPS",
        status: "available",
        scores: { speed: 2, accuracy: 5, reliability: 3, simplicity: 3, cost: 5 },
        pros: ["Eliminates GSD error (target at image center = drone GPS)", "Most accurate geotagging"],
        cons: ["Time-consuming descent", "Wind disturbs centering", "Needs CV running at decent FPS"],
        notes: "CV detects target offset from frame center → sends velocity commands to move drone → when centered, GPS reading = target position. Best accuracy for casualty.",
        depends: ["CV detection running (>3 FPS)", "GUIDED mode velocity commands", "Stable GPS", "Low wind conditions"],
      },
      {
        id: "geo-rtk", name: "RTK GPS", subtitle: "Centimeter-level accuracy",
        status: "rejected",
        scores: { speed: 5, accuracy: 5, reliability: 5, simplicity: 2, cost: 1 },
        pros: ["±2cm accuracy", "Gold standard for surveying"],
        cons: ["$500+ hardware", "Needs base station", "Overkill for this project"],
      },
    ],
  },
  {
    id: "classification", number: 9, name: "Classification & Verify", phase: "flight", icon: "✅",
    subGoal: "Classify each detection: casualty vs item of interest vs false positive (R05, R10)",
    requirements: ["R05", "R10"],
    approaches: [
      {
        id: "class-operator", name: "Operator Y/N/I/X", subtitle: "Human-in-the-loop via browser",
        status: "selected",
        scores: { speed: 2, accuracy: 5, reliability: 4, simplicity: 4, cost: 5 },
        pros: ["Zero false positive landings", "Human judgement for ambiguous cases"],
        cons: ["Requires network link", "Operator attention + latency"],
        notes: "Y=dummy, I=item of interest (logged), X=false positive (discarded). Descend to 15m first.",
      },
      {
        id: "class-multipass", name: "Multi-Pass Confidence", subtitle: "3/5 detections = confirm",
        status: "planned",
        scores: { speed: 4, accuracy: 3, reliability: 3, simplicity: 3, cost: 5 },
        pros: ["Autonomous, no operator needed"],
        cons: ["Can false-positive on persistent objects (bags, logs)"],
      },
      {
        id: "class-descend-redetect", name: "Descend + Re-Detect", subtitle: "Lower alt = better image",
        status: "planned",
        scores: { speed: 2, accuracy: 4, reliability: 3, simplicity: 3, cost: 5 },
        pros: ["Higher confidence at lower altitude"],
        cons: ["Time + battery cost per candidate"],
      },
      {
        id: "class-dual-model", name: "Dual-Model Cross-Validate", subtitle: "Custom + COCO must agree",
        status: "research",
        scores: { speed: 1, accuracy: 5, reliability: 4, simplicity: 2, cost: 5 },
        pros: ["Independent validation", "Reduces shared failure modes"],
        cons: ["Doubles inference time", "Both models may share biases"],
      },
      {
        id: "class-thermal", name: "Thermal Camera", subtitle: "Heat signature confirmation",
        status: "rejected",
        scores: { speed: 4, accuracy: 5, reliability: 5, simplicity: 2, cost: 1 },
        pros: ["Definitive for live person detection"],
        cons: ["$200+ hardware", "Weight penalty", "Scope creep"],
      },
    ],
  },

  // ══════════════════════════════════════════════
  //  PHASE: ACTION
  // ══════════════════════════════════════════════
  {
    id: "approach", number: 10, name: "Approach Casualty", phase: "action", icon: "🎯",
    subGoal: "Navigate to landing position 5–10m from confirmed casualty (R07)",
    requirements: ["R07"],
    approaches: [
      {
        id: "app-offset", name: "GPS Offset 7.5m", subtitle: "Operator picks N/E/S/W — lands in 5–10m zone",
        status: "selected",
        scores: { speed: 4, accuracy: 3, reliability: 4, simplicity: 4, cost: 5 },
        pros: ["Safe distance from casualty (R07: 5–10m)", "Simple math", "Operator picks direction"],
        cons: ["Fixed offset may hit obstacle", "No terrain awareness", "GPS error could push outside 5–10m zone"],
        notes: "7.5m offset = center of 5–10m zone. GPS error ±2-3m still keeps us in range. Cardinal direction via buttons.",
        depends: ["GPS estimate of casualty position", "Operator selects offset direction"],
      },
      {
        id: "app-direct", name: "Direct Fly-to-Target", subtitle: "Shortest path",
        status: "rejected",
        scores: { speed: 5, accuracy: 4, reliability: 4, simplicity: 5, cost: 5 },
        pros: ["Simplest, fastest"],
        cons: ["Risk of landing on person", "Dangerous"],
      },
      {
        id: "app-operator-guided", name: "Operator-Guided", subtitle: "Pilot picks exact spot via map",
        status: "available",
        scores: { speed: 2, accuracy: 5, reliability: 4, simplicity: 3, cost: 5 },
        pros: ["Human picks safe landing spot"],
        cons: ["Requires live video + map + skill"],
      },
      {
        id: "app-terrain", name: "Terrain-Aware Offset", subtitle: "Check DEM for obstacles",
        status: "research",
        scores: { speed: 3, accuracy: 4, reliability: 4, simplicity: 1, cost: 4 },
        pros: ["Avoids slopes, water, obstacles"],
        cons: ["Needs terrain data", "Complex implementation"],
      },
    ],
  },
  {
    id: "landing", number: 11, name: "Landing", phase: "action", icon: "🛬",
    subGoal: "Land within 5–10m of casualty (NOT closer than 5m) (R07)",
    requirements: ["R07"],
    approaches: [
      {
        id: "land-mavlink", name: "MAVLink LAND", subtitle: "LAND command at offset GPS point",
        status: "selected",
        scores: { speed: 4, accuracy: 3, reliability: 4, simplicity: 5, cost: 5 },
        pros: ["Simple — Cube handles descent", "Well-tested", "GPS drift during descent stays in 5–10m zone"],
        cons: ["No precision, may drift in wind"],
        notes: "Send LAND command at 7.5m offset point. Cube manages descent rate. Disarm on ground.",
        depends: ["Offset GPS point calculated", "Drone at offset position", "Clear landing surface"],
      },
      {
        id: "land-precision", name: "Precision Landing", subtitle: "ArUco marker or IR beacon",
        status: "research",
        scores: { speed: 3, accuracy: 5, reliability: 3, simplicity: 1, cost: 3 },
        pros: ["Centimeter accuracy using downward camera"],
        cons: ["Requires marker placement near casualty", "Extra hardware/software", "Overkill for 5–10m zone"],
      },
      {
        id: "land-visual-descent", name: "Visual Servo Descent", subtitle: "CV keeps target visible while descending",
        status: "research",
        scores: { speed: 2, accuracy: 4, reliability: 2, simplicity: 1, cost: 5 },
        pros: ["Adjusts for wind drift during descent", "Maintains offset using CV feedback"],
        cons: ["Complex control loop", "Wind sensitivity"],
        depends: ["CV detection at low altitude", "GUIDED velocity commands"],
      },
      {
        id: "land-rangefinder", name: "Rangefinder-Assisted Landing", subtitle: "True AGL for safe touchdown on uneven terrain",
        status: "planned",
        scores: { speed: 4, accuracy: 4, reliability: 4, simplicity: 3, cost: 4 },
        pros: ["Knows true height above ground (not baro estimate)", "Safe on slopes/uneven terrain", "ArduCopter natively supports RNGFND_LANDING"],
        cons: ["Needs rangefinder hardware configured", "Vegetation may give false readings"],
        notes: "Enable RNGFND_LANDING in ArduCopter. During LAND, Cube uses rangefinder for final descent instead of baro. Critical because field is uneven — baro alt from launch could be 2-3m off actual ground level.",
        depends: ["Rangefinder mounted and configured", "RNGFND_LANDING param enabled"],
      },
    ],
  },
  {
    id: "payload", number: 12, name: "Payload Delivery", phase: "action", icon: "🎁",
    subGoal: "Deploy first aid kit near casualty via Tarot release mechanism (R07)",
    requirements: ["R07"],
    approaches: [
      {
        id: "pay-land-release", name: "Land Then Release", subtitle: "Land at offset, release payload on ground",
        status: "planned",
        scores: { speed: 4, accuracy: 4, reliability: 4, simplicity: 4, cost: 5 },
        pros: ["Payload doesn't drift or break", "Simple — release after touchdown"],
        cons: ["Kit lands at drone position, not casualty position"],
        notes: "MAV_CMD_DO_SET_SERVO triggers Tarot release after landing confirmed. Kit drops <0.5m.",
        depends: ["Tarot release mechanism wired to AUX port", "MAVLink servo command working", "Drone landed safely"],
      },
      {
        id: "pay-hover-drop", name: "Hover + Drop (barometric)", subtitle: "Release from 3–5m baro altitude",
        status: "available",
        scores: { speed: 3, accuracy: 2, reliability: 3, simplicity: 3, cost: 5 },
        pros: ["Can drop closer to casualty than landing point", "Drone doesn't need to touch down first"],
        cons: ["Payload drift in wind", "May break on impact", "Baro altitude relative to launch — ground level may differ"],
        notes: "Hover at 3-5m baro above target, trigger servo. Ground may be higher/lower than launch → actual height unknown.",
        depends: ["Tarot release mechanism", "Stable hover above target", "Low wind"],
      },
      {
        id: "pay-rangefinder-drop", name: "Rangefinder Low Drop", subtitle: "Descend to ~1m AGL using rangefinder, release",
        status: "planned",
        scores: { speed: 4, accuracy: 5, reliability: 4, simplicity: 3, cost: 4 },
        pros: ["Actual distance to ground (not baro estimate)", "~1m drop = no payload damage", "Avoids tricky terrain landing", "Works on slopes/uneven ground"],
        cons: ["Needs rangefinder hardware + ArduCopter config", "Vegetation/grass may confuse sensor", "Still need to avoid <5m from casualty"],
        notes: "Use onboard lidar/rangefinder to descend to true 1m AGL at offset point. Release payload. Avoids landing entirely — no gear damage, no terrain risk. Key advantage: barometric alt is relative to launch, but ground level varies across the field. Rangefinder gives true distance to ground.",
        depends: ["Lidar/rangefinder mounted + configured in ArduCopter", "Tarot release mechanism", "Stable hover at offset point", "RNGFND_LANDING param enabled"],
      },
      {
        id: "pay-manual", name: "Manual Release", subtitle: "Pilot triggers release via RC/dashboard button",
        status: "available",
        scores: { speed: 2, accuracy: 4, reliability: 5, simplicity: 5, cost: 5 },
        pros: ["Pilot confirms exact moment", "Zero automation risk"],
        cons: ["Requires operator attention", "Delay"],
      },
    ],
  },
  {
    id: "rtl", number: 13, name: "Return to Launch", phase: "action", icon: "🏠",
    subGoal: "Return safely to Take-Off Location after payload delivery (R07, R09)",
    requirements: ["R07", "R09"],
    approaches: [
      {
        id: "rtl-mavlink", name: "MAV_CMD RTL", subtitle: "ArduCopter built-in Return to Launch",
        status: "selected",
        scores: { speed: 5, accuracy: 5, reliability: 5, simplicity: 5, cost: 5 },
        pros: ["Battle-tested ArduCopter feature", "Climbs to RTL_ALT, flies home, auto-lands", "Works even on link loss"],
        cons: ["Straight line — may cross SSSI if not at altitude"],
        notes: "RTL_ALT should be set above SSSI overfly risk. Failsafe triggers RTL on battery low or link loss.",
        depends: ["GPS 3D fix", "RTL_ALT configured above obstacles"],
      },
      {
        id: "rtl-guided", name: "GUIDED Waypoints Home", subtitle: "Python flies SSSI-safe route back",
        status: "available",
        scores: { speed: 3, accuracy: 5, reliability: 3, simplicity: 2, cost: 5 },
        pros: ["Can route around SSSI explicitly", "Full Python control of return path"],
        cons: ["More complex", "If link drops, no built-in failsafe path"],
        depends: ["SSSI boundary in memory", "Path planning around exclusion zone"],
      },
      {
        id: "rtl-operator", name: "Manual RC Return", subtitle: "Pilot flies drone home",
        status: "available",
        scores: { speed: 2, accuracy: 4, reliability: 5, simplicity: 5, cost: 5 },
        pros: ["Full pilot control", "Can avoid any obstacle"],
        cons: ["Slow, requires skill", "Pilot fatigue after long mission"],
      },
    ],
  },
];
