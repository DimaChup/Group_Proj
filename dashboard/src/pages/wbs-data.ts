/**
 * Work Breakdown Structure — SAR Drone Mission
 *
 * ~90 tasks decomposed from final goal down to atomic work items.
 * Tree flows: Goal (top) → Subsystems → Components → Tasks (bottom).
 * Progress flows bottom-up: complete lowest tasks first to climb toward the goal.
 *
 * Assignees match TEAM ids: hw, cv, fd, gcs, pm
 * Levels: 1 = Manual MVP, 2 = Semi-Autonomous, 3 = Full Autonomy, "all" = foundation
 */

// ═══════════════════════════════════════════════════════════
// Types
// ═══════════════════════════════════════════════════════════

export type WBSStatus = "done" | "active" | "upcoming" | "blocked";
export type AmbitionScope = 1 | 2 | 3 | "all";

export interface WBSNode {
  id: string;
  wbs: string;            // hierarchical code e.g. "1.2.3"
  label: string;
  parentId: string | null;
  assignee: string;        // team member id
  level: AmbitionScope;    // which ambition level this belongs to
  status: WBSStatus;
  description?: string;
}

// ═══════════════════════════════════════════════════════════
// Colours per team member (matches TEAM in group-project-data)
// ═══════════════════════════════════════════════════════════

export const ASSIGNEE_COLORS: Record<string, { bg: string; text: string; label: string }> = {
  hw:  { bg: "#f97316", text: "#fff", label: "Hardware Lead" },
  cv:  { bg: "#8b5cf6", text: "#fff", label: "CV / Optics" },
  fd:  { bg: "#06b6d4", text: "#fff", label: "Flight Dynamics" },
  gcs: { bg: "#22c55e", text: "#fff", label: "GCS / UI" },
  pm:  { bg: "#eab308", text: "#000", label: "Project Manager" },
};

export const LEVEL_COLORS: Record<string, string> = {
  "all": "#94a3b8",  // slate
  "1":   "#22c55e",  // green
  "2":   "#3b82f6",  // blue
  "3":   "#a855f7",  // purple
};

// ═══════════════════════════════════════════════════════════
// WBS Tree (~90 nodes)
// ═══════════════════════════════════════════════════════════

export const WBS_TREE: WBSNode[] = [
  // ── ROOT ──
  { id: "root", wbs: "0", label: "SAR Drone Mission System", parentId: null, assignee: "pm", level: "all", status: "active",
    description: "Complete search-and-rescue drone: find missing person, deliver care package, return safely" },

  // ══════════════════════════════════════════════════════════
  // 1. HARDWARE PLATFORM
  // ══════════════════════════════════════════════════════════
  { id: "hw-platform", wbs: "1", label: "Hardware Platform", parentId: "root", assignee: "hw", level: "all", status: "active" },

  // 1.1 Frame Assembly
  { id: "hw-frame", wbs: "1.1", label: "Frame Assembly", parentId: "hw-platform", assignee: "hw", level: "all", status: "done" },
  { id: "hw-frame-1", wbs: "1.1.1", label: "Inventory all frame parts", parentId: "hw-frame", assignee: "hw", level: "all", status: "done",
    description: "Unbox, catalog, verify against BOM" },
  { id: "hw-frame-2", wbs: "1.1.2", label: "Assemble X-frame chassis", parentId: "hw-frame", assignee: "hw", level: "all", status: "done",
    description: "Mount arms, center plate, landing gear" },
  { id: "hw-frame-3", wbs: "1.1.3", label: "Vibration dampening mount", parentId: "hw-frame", assignee: "hw", level: "all", status: "done",
    description: "Install FC anti-vibration plate, verify with accelerometer" },

  // 1.2 Power System
  { id: "hw-power", wbs: "1.2", label: "Power System", parentId: "hw-platform", assignee: "hw", level: "all", status: "active" },
  { id: "hw-power-1", wbs: "1.2.1", label: "Wire power distribution board", parentId: "hw-power", assignee: "hw", level: "all", status: "done",
    description: "Solder main power leads, ESC pads" },
  { id: "hw-power-2", wbs: "1.2.2", label: "ESC power connections", parentId: "hw-power", assignee: "hw", level: "all", status: "done",
    description: "Solder ESC signal + power wires to PDB" },
  { id: "hw-power-3", wbs: "1.2.3", label: "BEC voltage regulation (5V/12V)", parentId: "hw-power", assignee: "hw", level: "all", status: "done",
    description: "Step-down for FC, camera, companion computer" },
  { id: "hw-power-4", wbs: "1.2.4", label: "Battery mount + strap", parentId: "hw-power", assignee: "hw", level: "all", status: "done" },
  { id: "hw-power-5", wbs: "1.2.5", label: "Full power budget validation", parentId: "hw-power", assignee: "hw", level: "all", status: "active",
    description: "Measure total draw at hover, verify margin vs battery capacity" },

  // 1.3 Propulsion
  { id: "hw-prop", wbs: "1.3", label: "Propulsion", parentId: "hw-platform", assignee: "hw", level: "all", status: "done" },
  { id: "hw-prop-1", wbs: "1.3.1", label: "Mount motors (x4)", parentId: "hw-prop", assignee: "hw", level: "all", status: "done" },
  { id: "hw-prop-2", wbs: "1.3.2", label: "ESC calibration", parentId: "hw-prop", assignee: "hw", level: "all", status: "done",
    description: "Throttle range calibration per ESC" },
  { id: "hw-prop-3", wbs: "1.3.3", label: "Motor spin direction test", parentId: "hw-prop", assignee: "hw", level: "all", status: "done",
    description: "Verify CW/CCW pattern matches frame config" },
  { id: "hw-prop-4", wbs: "1.3.4", label: "Propeller balancing", parentId: "hw-prop", assignee: "hw", level: "all", status: "done" },

  // 1.4 Payload
  { id: "hw-payload", wbs: "1.4", label: "Payload System", parentId: "hw-platform", assignee: "hw", level: "all", status: "upcoming" },
  { id: "hw-payload-1", wbs: "1.4.1", label: "Payload bay design", parentId: "hw-payload", assignee: "hw", level: "all", status: "upcoming",
    description: "Mounting location, weight limit, CG impact" },
  { id: "hw-payload-2", wbs: "1.4.2", label: "Release mechanism prototype", parentId: "hw-payload", assignee: "hw", level: 2, status: "upcoming",
    description: "Servo-actuated drop mechanism" },
  { id: "hw-payload-3", wbs: "1.4.3", label: "Payload weight budget validation", parentId: "hw-payload", assignee: "hw", level: "all", status: "upcoming",
    description: "Flight time impact at various payload weights" },

  // ══════════════════════════════════════════════════════════
  // 2. SENSING & PERCEPTION
  // ══════════════════════════════════════════════════════════
  { id: "sensing", wbs: "2", label: "Sensing & Perception", parentId: "root", assignee: "cv", level: "all", status: "active" },

  // 2.1 Navigation Sensors
  { id: "sen-nav", wbs: "2.1", label: "Navigation Sensors", parentId: "sensing", assignee: "hw", level: "all", status: "done" },
  { id: "sen-nav-1", wbs: "2.1.1", label: "GPS module mount + lock test", parentId: "sen-nav", assignee: "hw", level: "all", status: "done",
    description: "Here3 GPS — verify <1m accuracy, TTFF <30s" },
  { id: "sen-nav-2", wbs: "2.1.2", label: "IMU calibration", parentId: "sen-nav", assignee: "fd", level: "all", status: "done",
    description: "Accelerometer + gyro calibration, vibration check" },
  { id: "sen-nav-3", wbs: "2.1.3", label: "Barometer verification", parentId: "sen-nav", assignee: "fd", level: "all", status: "done",
    description: "Altitude hold accuracy within 0.5m" },

  // 2.2 Camera System
  { id: "sen-cam", wbs: "2.2", label: "Camera System", parentId: "sensing", assignee: "cv", level: "all", status: "active" },
  { id: "sen-cam-1", wbs: "2.2.1", label: "FPV camera mount + angle", parentId: "sen-cam", assignee: "cv", level: 1, status: "done",
    description: "Analog FPV camera for pilot view" },
  { id: "sen-cam-2", wbs: "2.2.2", label: "Camera FOV characterization", parentId: "sen-cam", assignee: "cv", level: "all", status: "done",
    description: "Measure actual FOV, calculate ground coverage at altitude" },
  { id: "sen-cam-3", wbs: "2.2.3", label: "HD camera selection + mount", parentId: "sen-cam", assignee: "cv", level: 2, status: "active",
    description: "Pi Camera / USB cam for CV pipeline" },
  { id: "sen-cam-4", wbs: "2.2.4", label: "Camera gimbal integration", parentId: "sen-cam", assignee: "cv", level: 3, status: "upcoming",
    description: "2-axis stabilized gimbal for tracking" },

  // 2.3 Computer Vision
  { id: "sen-cv", wbs: "2.3", label: "Computer Vision Pipeline", parentId: "sensing", assignee: "cv", level: 2, status: "upcoming" },
  { id: "sen-cv-1", wbs: "2.3.1", label: "Training dataset collection", parentId: "sen-cv", assignee: "cv", level: 2, status: "upcoming",
    description: "Aerial person images from various heights + angles" },
  { id: "sen-cv-2", wbs: "2.3.2", label: "Person detection model selection", parentId: "sen-cv", assignee: "cv", level: 2, status: "upcoming",
    description: "YOLOv8-nano vs MobileNet-SSD vs custom" },
  { id: "sen-cv-3", wbs: "2.3.3", label: "Model optimization for edge", parentId: "sen-cv", assignee: "cv", level: 2, status: "upcoming",
    description: "Quantization, pruning, TensorRT conversion" },
  { id: "sen-cv-4", wbs: "2.3.4", label: "Detection pipeline integration", parentId: "sen-cv", assignee: "cv", level: 2, status: "upcoming",
    description: "Camera → inference → bounding box → GCS overlay" },
  { id: "sen-cv-5", wbs: "2.3.5", label: "CV-to-planner interface", parentId: "sen-cv", assignee: "cv", level: 3, status: "upcoming",
    description: "Detection triggers autonomous approach behavior" },

  // ══════════════════════════════════════════════════════════
  // 3. COMMUNICATIONS
  // ══════════════════════════════════════════════════════════
  { id: "comms", wbs: "3", label: "Communications", parentId: "root", assignee: "gcs", level: "all", status: "active" },

  // 3.1 RC Link
  { id: "com-rc", wbs: "3.1", label: "RC Control Link", parentId: "comms", assignee: "fd", level: 1, status: "done" },
  { id: "com-rc-1", wbs: "3.1.1", label: "RC receiver binding + test", parentId: "com-rc", assignee: "fd", level: 1, status: "done" },
  { id: "com-rc-2", wbs: "3.1.2", label: "Channel mapping (AETR)", parentId: "com-rc", assignee: "fd", level: 1, status: "done",
    description: "Map sticks → aileron, elevator, throttle, rudder" },
  { id: "com-rc-3", wbs: "3.1.3", label: "RC range test", parentId: "com-rc", assignee: "fd", level: 1, status: "done",
    description: "Verify control link at max mission distance" },

  // 3.2 Telemetry
  { id: "com-telem", wbs: "3.2", label: "Telemetry Link", parentId: "comms", assignee: "gcs", level: "all", status: "active" },
  { id: "com-telem-1", wbs: "3.2.1", label: "Telemetry radio setup", parentId: "com-telem", assignee: "gcs", level: "all", status: "done",
    description: "SiK radio pair, 915MHz, MAVLink v2" },
  { id: "com-telem-2", wbs: "3.2.2", label: "MAVLink parameter config", parentId: "com-telem", assignee: "gcs", level: "all", status: "done",
    description: "Stream rates, message filtering" },
  { id: "com-telem-3", wbs: "3.2.3", label: "Telemetry range + latency test", parentId: "com-telem", assignee: "gcs", level: "all", status: "active",
    description: "Verify at operational distances, measure round-trip latency" },

  // 3.3 Video Link
  { id: "com-video", wbs: "3.3", label: "Video Downlink", parentId: "comms", assignee: "gcs", level: "all", status: "active" },
  { id: "com-video-1", wbs: "3.3.1", label: "Video transmitter setup", parentId: "com-video", assignee: "gcs", level: 1, status: "done",
    description: "Analog VTX for L1, digital for L2+" },
  { id: "com-video-2", wbs: "3.3.2", label: "Antenna selection + placement", parentId: "com-video", assignee: "hw", level: "all", status: "done",
    description: "Circular polarized, clear of carbon fiber" },
  { id: "com-video-3", wbs: "3.3.3", label: "Video latency measurement", parentId: "com-video", assignee: "gcs", level: "all", status: "active",
    description: "End-to-end: camera → display, target <200ms" },
  { id: "com-video-4", wbs: "3.3.4", label: "IP video streaming setup", parentId: "com-video", assignee: "gcs", level: 2, status: "upcoming",
    description: "GStreamer / RTSP for digital HD stream" },

  // ══════════════════════════════════════════════════════════
  // 4. COMPUTE & PROCESSING
  // ══════════════════════════════════════════════════════════
  { id: "compute", wbs: "4", label: "Compute & Processing", parentId: "root", assignee: "fd", level: "all", status: "active" },

  // 4.1 Flight Controller
  { id: "cmp-fc", wbs: "4.1", label: "Flight Controller", parentId: "compute", assignee: "fd", level: "all", status: "active" },
  { id: "cmp-fc-1", wbs: "4.1.1", label: "Cube Orange firmware flash", parentId: "cmp-fc", assignee: "fd", level: "all", status: "done",
    description: "ArduCopter 4.x stable" },
  { id: "cmp-fc-2", wbs: "4.1.2", label: "ArduPilot parameter setup", parentId: "cmp-fc", assignee: "fd", level: "all", status: "done",
    description: "Frame type, motor mapping, failsafes, EKF config" },
  { id: "cmp-fc-3", wbs: "4.1.3", label: "PID tuning (bench)", parentId: "cmp-fc", assignee: "fd", level: "all", status: "active",
    description: "Initial rate PIDs from motor test stand" },
  { id: "cmp-fc-4", wbs: "4.1.4", label: "PID tuning (flight)", parentId: "cmp-fc", assignee: "fd", level: "all", status: "upcoming",
    description: "AutoTune or manual refinement in hover" },

  // 4.2 Companion Computer
  { id: "cmp-comp", wbs: "4.2", label: "Companion Computer", parentId: "compute", assignee: "cv", level: 2, status: "upcoming" },
  { id: "cmp-comp-1", wbs: "4.2.1", label: "RPi / Jetson OS setup", parentId: "cmp-comp", assignee: "cv", level: 2, status: "upcoming",
    description: "Ubuntu + driver stack" },
  { id: "cmp-comp-2", wbs: "4.2.2", label: "MAVLink bridge (MAVROS)", parentId: "cmp-comp", assignee: "fd", level: 2, status: "upcoming",
    description: "Serial connection FC ↔ companion" },
  { id: "cmp-comp-3", wbs: "4.2.3", label: "Power + thermal management", parentId: "cmp-comp", assignee: "hw", level: 2, status: "upcoming",
    description: "Heatsink, power draw, brown-out protection" },
  { id: "cmp-comp-4", wbs: "4.2.4", label: "Boot-on-power + watchdog", parentId: "cmp-comp", assignee: "cv", level: 2, status: "upcoming",
    description: "Auto-start services, hardware watchdog timer" },

  // 4.3 Edge AI
  { id: "cmp-edge", wbs: "4.3", label: "Edge AI Compute", parentId: "compute", assignee: "cv", level: 3, status: "upcoming" },
  { id: "cmp-edge-1", wbs: "4.3.1", label: "TensorRT / ONNX runtime", parentId: "cmp-edge", assignee: "cv", level: 3, status: "upcoming",
    description: "Inference framework setup on Jetson" },
  { id: "cmp-edge-2", wbs: "4.3.2", label: "Model inference benchmarking", parentId: "cmp-edge", assignee: "cv", level: 3, status: "upcoming",
    description: "FPS, latency, power draw per model" },
  { id: "cmp-edge-3", wbs: "4.3.3", label: "GPU resource allocation", parentId: "cmp-edge", assignee: "cv", level: 3, status: "upcoming",
    description: "Shared GPU between CV and mapping" },

  // ══════════════════════════════════════════════════════════
  // 5. SOFTWARE & AUTONOMY
  // ══════════════════════════════════════════════════════════
  { id: "software", wbs: "5", label: "Software & Autonomy", parentId: "root", assignee: "fd", level: "all", status: "active" },

  // 5.1 Flight Modes
  { id: "sw-modes", wbs: "5.1", label: "Flight Modes", parentId: "software", assignee: "fd", level: "all", status: "active" },
  { id: "sw-modes-1", wbs: "5.1.1", label: "Manual / Stabilize mode test", parentId: "sw-modes", assignee: "fd", level: 1, status: "done" },
  { id: "sw-modes-2", wbs: "5.1.2", label: "Loiter mode test", parentId: "sw-modes", assignee: "fd", level: 1, status: "done",
    description: "GPS hold, verify position accuracy" },
  { id: "sw-modes-3", wbs: "5.1.3", label: "RTL (Return to Launch) test", parentId: "sw-modes", assignee: "fd", level: 1, status: "active",
    description: "Verify return altitude, landing accuracy" },
  { id: "sw-modes-4", wbs: "5.1.4", label: "Auto waypoint mode", parentId: "sw-modes", assignee: "fd", level: 2, status: "upcoming",
    description: "Follow uploaded mission plan autonomously" },
  { id: "sw-modes-5", wbs: "5.1.5", label: "Guided mode API control", parentId: "sw-modes", assignee: "fd", level: 2, status: "upcoming",
    description: "Companion computer sends position commands" },

  // 5.2 Path Planning
  { id: "sw-path", wbs: "5.2", label: "Path Planning", parentId: "software", assignee: "fd", level: 2, status: "upcoming" },
  { id: "sw-path-1", wbs: "5.2.1", label: "Search pattern generation", parentId: "sw-path", assignee: "fd", level: 2, status: "upcoming",
    description: "Lawnmower / expanding square for search area" },
  { id: "sw-path-2", wbs: "5.2.2", label: "NFZ boundary definition", parentId: "sw-path", assignee: "gcs", level: 2, status: "upcoming",
    description: "Geofence polygons for no-fly zones" },
  { id: "sw-path-3", wbs: "5.2.3", label: "Dynamic replanning", parentId: "sw-path", assignee: "fd", level: 3, status: "upcoming",
    description: "Replan path when detection triggers approach" },
  { id: "sw-path-4", wbs: "5.2.4", label: "Delivery approach path", parentId: "sw-path", assignee: "fd", level: 2, status: "upcoming",
    description: "Descent profile to target, payload drop sequence" },

  // 5.3 Autonomy Stack
  { id: "sw-auto", wbs: "5.3", label: "Autonomy Stack", parentId: "software", assignee: "fd", level: 3, status: "upcoming" },
  { id: "sw-auto-1", wbs: "5.3.1", label: "ROS2 workspace setup", parentId: "sw-auto", assignee: "fd", level: 3, status: "upcoming",
    description: "Humble/Iron workspace, launch files" },
  { id: "sw-auto-2", wbs: "5.3.2", label: "Perception node", parentId: "sw-auto", assignee: "cv", level: 3, status: "upcoming",
    description: "CV results → ROS2 topic, world-frame localization" },
  { id: "sw-auto-3", wbs: "5.3.3", label: "Decision / behavior tree", parentId: "sw-auto", assignee: "fd", level: 3, status: "upcoming",
    description: "Search → Detect → Approach → Deliver → RTL" },
  { id: "sw-auto-4", wbs: "5.3.4", label: "Navigation node", parentId: "sw-auto", assignee: "fd", level: 3, status: "upcoming",
    description: "Waypoint tracking + obstacle-aware navigation" },
  { id: "sw-auto-5", wbs: "5.3.5", label: "End-to-end autonomous test", parentId: "sw-auto", assignee: "pm", level: 3, status: "upcoming",
    description: "Full loop: takeoff → search → detect → deliver → RTL" },

  // 5.4 Safety Logic
  { id: "sw-safety", wbs: "5.4", label: "Safety Logic", parentId: "software", assignee: "fd", level: "all", status: "active" },
  { id: "sw-safety-1", wbs: "5.4.1", label: "Geofence setup", parentId: "sw-safety", assignee: "fd", level: "all", status: "done",
    description: "Hard boundary, RTL on breach" },
  { id: "sw-safety-2", wbs: "5.4.2", label: "Battery failsafe", parentId: "sw-safety", assignee: "fd", level: "all", status: "done",
    description: "Low voltage → RTL, critical → land immediately" },
  { id: "sw-safety-3", wbs: "5.4.3", label: "RC failsafe", parentId: "sw-safety", assignee: "fd", level: 1, status: "done",
    description: "No RC signal → hover 5s → RTL" },
  { id: "sw-safety-4", wbs: "5.4.4", label: "Sensor failsafe (GPS loss)", parentId: "sw-safety", assignee: "fd", level: "all", status: "active",
    description: "EKF fallback, land if no position estimate" },
  { id: "sw-safety-5", wbs: "5.4.5", label: "Emergency land procedure", parentId: "sw-safety", assignee: "pm", level: "all", status: "upcoming",
    description: "Kill switch, immediate descend, log dump" },

  // ══════════════════════════════════════════════════════════
  // 6. GROUND CONTROL STATION
  // ══════════════════════════════════════════════════════════
  { id: "gcs-sys", wbs: "6", label: "Ground Control Station", parentId: "root", assignee: "gcs", level: "all", status: "active" },

  // 6.1 GCS Software
  { id: "gcs-sw", wbs: "6.1", label: "GCS Software", parentId: "gcs-sys", assignee: "gcs", level: "all", status: "active" },
  { id: "gcs-sw-1", wbs: "6.1.1", label: "Mission Planner / QGC setup", parentId: "gcs-sw", assignee: "gcs", level: 1, status: "done",
    description: "Connect, configure, verify telemetry display" },
  { id: "gcs-sw-2", wbs: "6.1.2", label: "Custom telemetry dashboard", parentId: "gcs-sw", assignee: "gcs", level: 2, status: "upcoming",
    description: "Real-time battery, altitude, GPS, signal strength" },
  { id: "gcs-sw-3", wbs: "6.1.3", label: "Map overlay + NFZ display", parentId: "gcs-sw", assignee: "gcs", level: "all", status: "active",
    description: "Search area, NFZ polygons, drone position on map" },
  { id: "gcs-sw-4", wbs: "6.1.4", label: "Target marking interface", parentId: "gcs-sw", assignee: "gcs", level: 2, status: "upcoming",
    description: "Click to mark detected person on map" },

  // 6.2 Mission Planning
  { id: "gcs-plan", wbs: "6.2", label: "Mission Planning Tools", parentId: "gcs-sys", assignee: "gcs", level: "all", status: "upcoming" },
  { id: "gcs-plan-1", wbs: "6.2.1", label: "Search area definition tool", parentId: "gcs-plan", assignee: "gcs", level: 2, status: "upcoming",
    description: "Draw polygon, auto-generate search pattern" },
  { id: "gcs-plan-2", wbs: "6.2.2", label: "Waypoint upload pipeline", parentId: "gcs-plan", assignee: "gcs", level: 2, status: "upcoming",
    description: "GCS → MAVLink → FC mission upload" },
  { id: "gcs-plan-3", wbs: "6.2.3", label: "Pre-flight checklist app", parentId: "gcs-plan", assignee: "pm", level: "all", status: "upcoming",
    description: "Mandatory checks before arming: GPS, battery, comms" },

  // 6.3 Live Operations
  { id: "gcs-ops", wbs: "6.3", label: "Live Operations", parentId: "gcs-sys", assignee: "gcs", level: "all", status: "active" },
  { id: "gcs-ops-1", wbs: "6.3.1", label: "Real-time video display", parentId: "gcs-ops", assignee: "gcs", level: 1, status: "done",
    description: "Video receiver → monitor, low-latency" },
  { id: "gcs-ops-2", wbs: "6.3.2", label: "Telemetry logging", parentId: "gcs-ops", assignee: "gcs", level: "all", status: "active",
    description: "MAVLink .tlog recording for post-flight review" },
  { id: "gcs-ops-3", wbs: "6.3.3", label: "Mission abort interface", parentId: "gcs-ops", assignee: "gcs", level: "all", status: "upcoming",
    description: "One-click RTL / land / kill buttons" },

  // ══════════════════════════════════════════════════════════
  // 7. INTEGRATION & TESTING
  // ══════════════════════════════════════════════════════════
  { id: "integration", wbs: "7", label: "Integration & Testing", parentId: "root", assignee: "pm", level: "all", status: "active" },

  // 7.1 Component Integration
  { id: "int-comp", wbs: "7.1", label: "Component Integration", parentId: "integration", assignee: "pm", level: "all", status: "active" },
  { id: "int-comp-1", wbs: "7.1.1", label: "Hardware-FC integration test", parentId: "int-comp", assignee: "pm", level: "all", status: "done",
    description: "Motors respond to FC commands, correct direction" },
  { id: "int-comp-2", wbs: "7.1.2", label: "Sensor-FC integration test", parentId: "int-comp", assignee: "pm", level: "all", status: "done",
    description: "GPS, IMU, baro all feeding EKF correctly" },
  { id: "int-comp-3", wbs: "7.1.3", label: "Comms range integration test", parentId: "int-comp", assignee: "pm", level: "all", status: "active",
    description: "RC + telemetry + video all working at range" },
  { id: "int-comp-4", wbs: "7.1.4", label: "Camera-compute pipeline test", parentId: "int-comp", assignee: "cv", level: 2, status: "upcoming",
    description: "Camera → companion → inference → GCS display" },

  // 7.2 System Testing
  { id: "int-sys", wbs: "7.2", label: "System Testing", parentId: "integration", assignee: "pm", level: "all", status: "upcoming" },
  { id: "int-sys-1", wbs: "7.2.1", label: "First hover test", parentId: "int-sys", assignee: "fd", level: 1, status: "upcoming",
    description: "Tethered → untethered, 1m hover, verify stability" },
  { id: "int-sys-2", wbs: "7.2.2", label: "Stabilized flight test", parentId: "int-sys", assignee: "fd", level: 1, status: "upcoming",
    description: "Manual flight, verify handling in all axes" },
  { id: "int-sys-3", wbs: "7.2.3", label: "Waypoint following test", parentId: "int-sys", assignee: "fd", level: 2, status: "upcoming",
    description: "Auto mode, follow 5-point mission" },
  { id: "int-sys-4", wbs: "7.2.4", label: "Full autonomous mission test", parentId: "int-sys", assignee: "pm", level: 3, status: "upcoming",
    description: "Search → detect → approach → deliver → RTL" },
  { id: "int-sys-5", wbs: "7.2.5", label: "Failsafe trigger tests", parentId: "int-sys", assignee: "pm", level: "all", status: "upcoming",
    description: "Intentionally trigger each failsafe, verify response" },

  // 7.3 Mission Rehearsal
  { id: "int-rehearse", wbs: "7.3", label: "Mission Rehearsal", parentId: "integration", assignee: "pm", level: "all", status: "upcoming" },
  { id: "int-rehearse-1", wbs: "7.3.1", label: "Simulated SAR (manual pilot)", parentId: "int-rehearse", assignee: "fd", level: 1, status: "upcoming",
    description: "Full L1 scenario: pilot flies, spots mannequin, delivers" },
  { id: "int-rehearse-2", wbs: "7.3.2", label: "Simulated SAR (semi-auto)", parentId: "int-rehearse", assignee: "fd", level: 2, status: "upcoming",
    description: "Auto search pattern, human confirms detection" },
  { id: "int-rehearse-3", wbs: "7.3.3", label: "Full mission dry run", parentId: "int-rehearse", assignee: "pm", level: 3, status: "upcoming",
    description: "Complete autonomous scenario, all systems active" },
  { id: "int-rehearse-4", wbs: "7.3.4", label: "Final demonstration", parentId: "int-rehearse", assignee: "pm", level: "all", status: "upcoming",
    description: "Assessed demo for stakeholders / assessors" },
];
