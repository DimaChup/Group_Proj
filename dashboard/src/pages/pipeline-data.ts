// pipeline-data.ts — Mission pipeline stages and design alternatives

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
}

export interface Stage {
  id: string;
  number: number;
  name: string;
  subGoal: string;
  phase: "pre-mission" | "flight" | "action";
  icon: string;
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

export const PIPELINE: Stage[] = [
  // ══════════════════════════════════════════════
  //  PHASE: PRE-MISSION
  // ══════════════════════════════════════════════
  {
    id: "preflight", number: 1, name: "Preflight Check", phase: "pre-mission", icon: "🔍",
    subGoal: "Confirm all subsystems operational before arming",
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
    id: "search-area", number: 2, name: "Search Area Definition", phase: "pre-mission", icon: "📐",
    subGoal: "Define polygon boundary the drone will search",
    approaches: [
      {
        id: "area-kml", name: "KML File Import", subtitle: "Load AENGM0074.kml at startup",
        status: "selected",
        scores: { speed: 5, accuracy: 5, reliability: 5, simplicity: 4, cost: 5 },
        pros: ["Standard format", "Pre-defined by assessment", "Shareable"],
        cons: ["Not editable in field without laptop"],
      },
      {
        id: "area-draw", name: "Interactive Drawing", subtitle: "draw_search_area.py on laptop",
        status: "available",
        scores: { speed: 3, accuracy: 4, reliability: 3, simplicity: 3, cost: 5 },
        pros: ["Visual, intuitive", "Field-adjustable"],
        cons: ["Needs display (laptop)", "Not headless"],
      },
      {
        id: "area-config", name: "Hardcoded Config", subtitle: "GPS coords in config.py",
        status: "available",
        scores: { speed: 5, accuracy: 3, reliability: 5, simplicity: 5, cost: 5 },
        pros: ["Zero setup", "Always available as fallback"],
        cons: ["Inflexible", "Requires code change to update"],
      },
      {
        id: "area-mp", name: "Mission Planner Upload", subtitle: "Industry-standard GCS",
        status: "available",
        scores: { speed: 3, accuracy: 5, reliability: 4, simplicity: 2, cost: 5 },
        pros: ["Industry standard", "Full GCS integration"],
        cons: ["Separate software", "Extra step"],
      },
    ],
  },
  {
    id: "path-planning", number: 3, name: "Path Planning", phase: "pre-mission", icon: "🗺️",
    subGoal: "Generate flight path covering search area within battery",
    approaches: [
      {
        id: "path-lawnmower", name: "Lawnmower Pattern", subtitle: "Boustrophedon, 20% overlap",
        status: "selected",
        scores: { speed: 4, accuracy: 5, reliability: 5, simplicity: 4, cost: 5 },
        pros: ["100% coverage guaranteed", "Predictable timing", "Simple math"],
        cons: ["Inefficient for irregular shapes", "No adaptation to detections"],
        notes: "Auto-aligns to longest polygon edge (PCA). 20% overlap for GPS drift margin.",
      },
      {
        id: "path-spiral", name: "Spiral Inward", subtitle: "Converge to center",
        status: "available",
        scores: { speed: 3, accuracy: 3, reliability: 3, simplicity: 3, cost: 5 },
        pros: ["Natural convergence", "Good for round areas"],
        cons: ["Poor edge coverage", "Harder overlap math"],
      },
      {
        id: "path-adaptive", name: "Adaptive Re-plan", subtitle: "Re-route on detection",
        status: "research",
        scores: { speed: 4, accuracy: 4, reliability: 2, simplicity: 1, cost: 5 },
        pros: ["Concentrates on detection clusters", "Battery-efficient"],
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
    subGoal: "Arm, climb to 30m, fly to first search waypoint",
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
    subGoal: "Fly waypoint path at 30m, 10 m/s while running CV",
    approaches: [
      {
        id: "scan-guided-wp", name: "GUIDED Waypoints", subtitle: "Python sends each waypoint",
        status: "selected",
        scores: { speed: 3, accuracy: 4, reliability: 4, simplicity: 3, cost: 5 },
        pros: ["Can pause/redirect mid-leg", "Python controls flow"],
        cons: ["Slower than AUTO (command latency)", "More MAVLink traffic"],
        notes: "10 m/s search, 30m alt. planning.py generates waypoints from polygon.",
      },
      {
        id: "scan-auto", name: "AUTO + Servo Triggers", subtitle: "Cube flies, Pi watches",
        status: "available",
        scores: { speed: 5, accuracy: 4, reliability: 5, simplicity: 2, cost: 5 },
        pros: ["Smoother flight (native nav)", "Faster coverage"],
        cons: ["Hard to interrupt for detection", "Less Python control"],
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
    id: "detection", number: 6, name: "Object Detection", phase: "flight", icon: "👁️",
    subGoal: "Identify candidate targets (person/dummy) in each frame",
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
    id: "geotagging", number: 7, name: "Target Geotagging", phase: "flight", icon: "📍",
    subGoal: "Convert pixel detection into GPS coordinate estimate",
    approaches: [
      {
        id: "geo-gsd", name: "Pixel-to-GPS Projection", subtitle: "GSD math + yaw rotation",
        status: "selected",
        scores: { speed: 5, accuracy: 3, reliability: 4, simplicity: 3, cost: 5 },
        pros: ["Instant (no hovering)", "Works during flight", "Altitude-weighted"],
        cons: ["~3-5m error from GPS drift + yaw + altitude", "Edge pixels more error"],
        notes: "GSD = (sensor_width × alt) / (focal_length × image_width). Kalman filter smooths.",
      },
      {
        id: "geo-multiframe", name: "Multi-Frame Clustering", subtitle: "Kalman + inverse variance weighting",
        status: "selected",
        scores: { speed: 4, accuracy: 4, reliability: 4, simplicity: 2, cost: 5 },
        pros: ["Averages noise over many detections", "Converges to true position"],
        cons: ["Needs multiple passes or slow speed", "Complex math"],
        notes: "In simulator + pi_flight. Clusters within 30m. Max 50 obs per cluster.",
      },
      {
        id: "geo-hover-avg", name: "Hover + GPS Average", subtitle: "Fly above, average 10-15s of GPS",
        status: "available",
        scores: { speed: 2, accuracy: 4, reliability: 4, simplicity: 5, cost: 5 },
        pros: ["Very simple", "Averages out GPS drift"],
        cons: ["Wastes battery hovering", "Needs visual servo to center first"],
      },
      {
        id: "geo-visual-servo", name: "Visual Servo + Snapshot", subtitle: "Center target, then read GPS",
        status: "available",
        scores: { speed: 2, accuracy: 5, reliability: 3, simplicity: 3, cost: 5 },
        pros: ["Eliminates GSD error (target at image center)", "GPS = target position"],
        cons: ["Time-consuming descent", "Wind disturbs centering"],
        notes: "Descend to 10-15m, center target in frame, take GPS average. Best accuracy.",
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
    id: "classification", number: 8, name: "Classification & Verify", phase: "flight", icon: "✅",
    subGoal: "Confirm detection is real target, not false positive",
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
    id: "approach", number: 9, name: "Approach Target", phase: "action", icon: "🎯",
    subGoal: "Navigate to landing position near confirmed target",
    approaches: [
      {
        id: "app-offset", name: "GPS Offset 7.5m", subtitle: "Operator picks N/E/S/W",
        status: "selected",
        scores: { speed: 4, accuracy: 3, reliability: 4, simplicity: 4, cost: 5 },
        pros: ["Safe distance from casualty", "Simple math", "Operator picks direction"],
        cons: ["Fixed offset may hit obstacle", "No terrain awareness"],
        notes: "7.5m offset = GPS error buffer (±2-3m) + safety. Cardinal direction via buttons.",
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
    id: "landing", number: 10, name: "Landing & Recovery", phase: "action", icon: "🛬",
    subGoal: "Land safely near target, end mission",
    approaches: [
      {
        id: "land-mavlink", name: "MAVLink LAND", subtitle: "Command at offset GPS point",
        status: "selected",
        scores: { speed: 4, accuracy: 3, reliability: 4, simplicity: 5, cost: 5 },
        pros: ["Simple — Cube handles descent", "Well-tested"],
        cons: ["No precision, GPS drift during descent"],
        notes: "Send LAND command at offset point. Cube manages descent rate. Disarm on ground.",
      },
      {
        id: "land-precision", name: "Precision Landing", subtitle: "ArUco marker or IR beacon",
        status: "research",
        scores: { speed: 3, accuracy: 5, reliability: 3, simplicity: 1, cost: 3 },
        pros: ["Centimeter accuracy using downward camera"],
        cons: ["Requires marker placement", "Extra hardware/software"],
      },
      {
        id: "land-drop", name: "Hover + Drop Payload", subtitle: "Never land, release first aid kit",
        status: "available",
        scores: { speed: 3, accuracy: 3, reliability: 3, simplicity: 3, cost: 4 },
        pros: ["Safer for drone (no landing risk)", "Can drop from altitude"],
        cons: ["Needs release mechanism (servo)", "Payload may drift"],
        notes: "Servo on AUX port. MAV_CMD_DO_SET_SERVO. Already wired on our drone.",
      },
      {
        id: "land-visual-descent", name: "Visual Servo Descent", subtitle: "Keep target in view while descending",
        status: "research",
        scores: { speed: 2, accuracy: 4, reliability: 2, simplicity: 1, cost: 5 },
        pros: ["Adjusts for wind drift during descent"],
        cons: ["Complex control loop", "Wind sensitivity"],
      },
    ],
  },
];
