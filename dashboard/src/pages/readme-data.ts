// readme-data.ts — Comprehensive project overview data for README tab

// ── Section types ────────────────────────────────────────────────────
export interface Section {
  id: string;
  title: string;
  items: string[];
}

export interface TestScript {
  name: string;
  path: string;
  purpose: string;
  when: string;
  flags?: string[];
  output?: string;
  risk: "none" | "low" | "medium" | "high";
}

export interface CalibrationStep {
  id: string;
  name: string;
  location: "bench" | "field" | "both";
  script: string;
  what: string;
  configUpdate?: string;
}

export interface FlightStep {
  id: string;
  name: string;
  script: string;
  risk: string;
  purpose: string;
  details: string[];
}

export interface Deliverable {
  id: string;
  name: string;
  status: "done" | "ready" | "needs-testing" | "todo";
  description: string;
}

// ── Personal pre-flight checklist (CV person) ───────────────────────
export interface ChecklistItem {
  id: string;
  task: string;
  command: string;
  detail: string;
  location: "home" | "field";
  time: string;
}

export const MY_CHECKLIST: ChecklistItem[] = [
  { id: "1", task: "FOV Calibration", command: "python tests/calibration/fov_calibrate.py", detail: "Hold camera at known height (50cm) above ruler. Measure visible width. Update FOCAL_LENGTH_MM in config.py. Most important calibration.", location: "home", time: "10 min" },
  { id: "2", task: "Lens Distortion Calibration", command: "python tests/calibration/lens_calibrate.py --board 9x6", detail: "Print checkerboard (9x6 inner corners). Hold at 10-20 angles, SPACE each. Press C when 10+ done. Saves calibration_data.npz.", location: "home", time: "15 min" },
  { id: "3", task: "Generate Backup Model", command: "yolo export model=yolov8n.pt format=tflite", detail: "Export COCO person detector as TFLite fallback (dummy is human-shaped). Copy output to models/coco_person.tflite.", location: "home", time: "15 min" },
  { id: "4", task: "Compare Models", command: "python tests/day_1_experiments/model_compare.py --frames 50", detail: "Benchmarks every .tflite in models/. Prints speed, detection rate, confidence. Pick the best one.", location: "home", time: "5 min" },
  { id: "5", task: "Dry-Run Pattern Check", command: "python main.py --dry-run", detail: "Verify SEARCH_AREA_GPS in config.py has real field coordinates. Check waypoint count and flight time.", location: "home", time: "2 min" },
  { id: "6", task: "Test Video Stream Link", command: "python tests/diagnostics/camera_stream.py --with-detection", detail: "Start stream on Pi, open http://PI_IP:8090 in laptop browser. Confirm MJPEG video shows with detection boxes overlaid.", location: "home", time: "5 min" },
  { id: "7", task: "Test RC Connection (bonus)", command: "Mission Planner → Config → Failsafe", detail: "Bind RC to Cube, verify sticks respond in MP, test kill switch (flip to STABILIZE, confirm mode changes). Set failsafe: RC loss = RTL.", location: "home", time: "10 min" },
  { id: "8", task: "Push Code to Git", command: "git add -A && git commit -m \"pre-flight\" && git push", detail: "Everything needs to be on the Pi. Then on Pi: git pull.", location: "home", time: "2 min" },
  { id: "9", task: "Connectivity Check", command: "python tests/diagnostics/diagnostics.py", detail: "All 5 green: Camera, AI, Cube, GPS, GS. Run first thing at the field.", location: "field", time: "2 min" },
  { id: "10", task: "Test Live Video Link (field)", command: "python tests/diagnostics/camera_stream.py --with-detection", detail: "Open http://PI_IP:8090 in browser. Confirm video with detection boxes over WiFi hotspot.", location: "field", time: "2 min" },
  { id: "11", task: "Run Passive Detection (during ANY flight)", command: "python tests/flight/1_passive_flight.py --headless --stream --save-detections", detail: "THE main script. Launch it, fly the drone. Detects targets (zero commands), saves geotagged photos (detections/TIMESTAMP_LAT_LON_CONF.jpg), logs CSV, streams video, buzzer beeps.", location: "field", time: "per flight" },
  { id: "12", task: "Review Results Between Flights", command: "ls detections/ && cat passive_flight_log.csv", detail: "Check detection images and CSV. At what altitude does it detect? False positives? Blur at speed? Swap models if needed.", location: "field", time: "5 min" },
];

// ── Project overview ─────────────────────────────────────────────────
export const PROJECT_OVERVIEW = {
  title: "SAR Drone — Autonomous Search & Rescue",
  course: "University of Bristol MSc — AENGM0074",
  team: "Team of 5",
  summary: [
    "Autonomous drone that searches a defined area using a lawnmower flight pattern, avoiding SSSI no-fly zones",
    "Onboard AI (YOLOv8 / TFLite) detects a casualty and items of interest (clothing, equipment) from altitude",
    "Centres on target, descends for operator classification (Y=casualty, I=item of interest, X=false positive)",
    "Redirects PLB (Personal Locator Beacon) signal to aid search prioritisation",
    "Delivers first aid kit via payload release mechanism",
    "Lands within 10m but NOT within 5m of target (R07 safe landing zone, centred at ~7.5m offset)",
  ],
  stateFlow: "INIT → CONNECTING → ARMING → TAKEOFF → SEARCH → CENTERING → DESCENDING → VERIFY → APPROACH → LANDING → DONE",
};

// ── Architecture ─────────────────────────────────────────────────────
export const ARCHITECTURE = {
  coreFiles: [
    { file: "config.py", desc: "All settings: altitudes, speeds, camera, connection. Auto-detects hardware (Pi vs laptop)." },
    { file: "states.py", desc: "State enum (SEARCH, VERIFY, LANDING, etc.)" },
    { file: "utils.py", desc: "Geo math: GPS ↔ pixel conversion (GeoTransformer). WGS84-accurate." },
    { file: "vision.py", desc: "Camera + AI detection. Dual backend: Ultralytics (laptop) / TFLite (Pi). Interface: detect_in_image(frame) → (found, x, y, conf). This is the ONLY file that touches CV/AI." },
    { file: "planning.py", desc: "Lawnmower search pattern generator from any polygon. Independent module." },
    { file: "main.py", desc: "Mission orchestrator — the full state machine. Ties everything together. Flags: --dry-run, --model PATH." },
    { file: "simple_simulator.py", desc: "Interactive MVP: keyboard flight + CV + GPS estimation + offset landing. Laptop-only. Keys: SPACE=arm WASD=fly C=gps V=vision G=lock L=land." },
    { file: "pi_flight.py", desc: "Web ground station: browser dashboard + MJPEG stream + commands. Works headless on Pi. http://localhost:8090." },
    { file: "simulation.py", desc: "Laptop-only simulation environment: map.jpg + simulated drone camera view." },
  ],
  designDecisions: [
    "vision.py is the ONLY file that touches CV/AI — everything else calls detect_in_image()",
    "config.py auto-detects hardware — serial port → Cube, no serial → SITL. No code changes between platforms.",
    "Same main.py runs on simulation and real hardware — only camera source and connection string change",
    "Interactive polygon drawing in REAL mode (map.jpg), headless fallback to SEARCH_AREA_GPS in config.py",
    "All code developed on laptop, pushed to GitHub, pulled onto Pi — Pi is never the source of truth",
  ],
};

// ── Hardware ─────────────────────────────────────────────────────────
export const HARDWARE_SUMMARY = [
  { component: "Flight Controller", model: "CubeOrange+", detail: "ArduCopter V4.6.3, QUAD/X frame" },
  { component: "GPS", model: "Here 3+", detail: "Connected via CAN2. LED: blue=no lock, green=locked" },
  { component: "Companion Computer", model: "Raspberry Pi 5", detail: "Python 3.13, picamera2, ai-edge-litert" },
  { component: "Camera", model: "IMX296 Global Shutter", detail: "640×480, BGR output (no cvtColor needed), 6mm lens" },
  { component: "AI Model", model: "YOLOv8n → TFLite", detail: "~6MB, ~250ms inference on Pi (~4 FPS)" },
  { component: "Connection", model: "TELEM2 → Pi GPIO UART", detail: "921600 baud, via mavproxy UDP bridge" },
  { component: "Rangefinder", model: "Lidar / Rangefinder", detail: "Downward-facing, provides precise AGL altitude for landing and low-altitude operations" },
  { component: "RC Controller", model: "Standard RC TX/RX", detail: "Kill switch = STABILIZE mode (hardware-level override)" },
];

// ── What's been built & tested ───────────────────────────────────────
export const COMPLETED: Deliverable[] = [
  { id: "sim", name: "Full simulation on laptop", status: "done", description: "State machine, search pattern, detection, centering, descent, verification, landing — all work end-to-end in SITL." },
  { id: "pi-cam", name: "Pi camera working", status: "done", description: "picamera2 at 640×480, BGR format confirmed. IMX296 global shutter. Color fix applied (no cvtColor needed)." },
  { id: "pi-ai", name: "TFLite inference on Pi", status: "done", description: "~250ms avg inference, ~4 FPS. 50/50 detection at 0.966 confidence on bench." },
  { id: "pi-cube", name: "Pi ↔ Cube connection", status: "done", description: "Via mavproxy UDP bridge (Python 3.13 serial is broken). All commands reach Cube and get ACKs." },
  { id: "mp-conn", name: "Mission Planner via Pi", status: "done", description: "MP connects TCP to Pi (port 5762). Full telemetry, map view, parameter editing." },
  { id: "sim-mvp", name: "Interactive simulator (simple_simulator.py)", status: "done", description: "Keyboard flight, CV detection, GPS estimation with clustering, Kalman filter, inverse variance weighting, offset landing. Full mission tested." },
  { id: "gs", name: "Web ground station (pi_flight.py)", status: "ready", description: "Browser dashboard at :8090 — MJPEG stream, GPS grid, detection clusters, N/Y/I/X/L commands. Tested in simulation, not yet on Pi." },
  { id: "passive", name: "Passive flight script", status: "ready", description: "1_passive_flight.py — pilot flies RC, Pi detects + logs + buzzer. Saves geotagged detection images. Zero commands sent." },
  { id: "tests", name: "Organized test suite", status: "done", description: "30+ scripts in 6 categories: hardware, flight (numbered 0a-4), diagnostics, calibration, experiments, laptop." },
  { id: "dry-run", name: "Dry-run mode", status: "done", description: "main.py --dry-run: prints lawnmower waypoints, state machine walkthrough, map visualization. No GPS/Cube needed." },
  { id: "model-swap", name: "Model switching", status: "done", description: "--model flag on main.py and pi_flight.py. Compare models with model_compare.py." },
  { id: "docs", name: "Flight day documentation", status: "done", description: "FLIGHT_DAY_CHECKLIST.md (printable), FLIGHT_DAY_TESTS.md (master test reference), all protocols documented." },
];

export const TODO: Deliverable[] = [
  { id: "colors-pi", name: "Test detection with corrected colors on Pi", status: "needs-testing", description: "Push BGR fix to Pi, verify detection with real dummy." },
  { id: "gps-outdoor", name: "Outdoor GPS fix test", status: "needs-testing", description: "Verify GPS locks outdoors (3D fix, 8+ sats, green LED)." },
  { id: "models", name: "Prepare alternative CV models", status: "todo", description: "Export COCO person detector, INT8 quantized, YOLOv8s. Copy to models/ folder." },
  { id: "fov-cal", name: "FOV calibration on bench", status: "todo", description: "Run fov_calibrate.py with ruler, update FOCAL_LENGTH_MM in config.py." },
  { id: "passive-flight", name: "Manual flight with passive detection", status: "todo", description: "Step 2: pilot flies RC, Pi logs detections. First real outdoor CV test." },
  { id: "full-auto", name: "Full autonomous flight", status: "todo", description: "The final test: search → detect → center → descend → verify → land." },
];

// ── Test scripts explained ───────────────────────────────────────────
export const TEST_CATEGORIES = [
  {
    category: "Hardware Tests",
    folder: "tests/hardware/",
    purpose: "DOES THIS PART WORK? — Individual component checks. Run these when a specific piece seems broken.",
    scripts: [
      { name: "benchmark.py", path: "tests/hardware/benchmark.py", purpose: "Measure AI inference speed on current hardware (50 runs, timing report)", when: "Before first flight, and anytime you swap models", flags: [], output: "Terminal: avg ms, FPS, detection count", risk: "none" as const },
      { name: "cv_benchmark.py", path: "tests/hardware/cv_benchmark.py", purpose: "Detection rate + speed with live camera. Includes blur simulation.", when: "After camera setup, to verify AI sees real frames", flags: ["--headless"], output: "Terminal: FPS, detection rate, blur metric", risk: "none" as const },
      { name: "gps_test.py", path: "tests/hardware/gps_test.py", purpose: "GPS lock status: fix type, satellites, coordinates. Live updating table.", when: "At field, wait until fix_type=3 and sats>=8", flags: [], output: "Terminal: live GPS table", risk: "none" as const },
      { name: "gps_health.py", path: "tests/hardware/gps_health.py", purpose: "Deep GPS diagnostics: CAN bus, parameters, hardware data, satellite tracking", when: "If GPS doesn't lock or seems wrong", flags: [], output: "Terminal: step-by-step verification", risk: "none" as const },
      { name: "buzzer_test.py", path: "tests/hardware/buzzer_test.py", purpose: "Test buzzer melodies via MAVLink PLAY_TUNE", when: "Verify buzzer works (used for detection alerts)", flags: [], output: "Buzzer plays melodies", risk: "none" as const },
    ] as TestScript[],
  },
  {
    category: "Calibration",
    folder: "tests/calibration/",
    purpose: "ARE THE NUMBERS RIGHT? — FOV and lens calibration. Wrong FOV = wrong GPS estimates from pixel positions.",
    scripts: [
      { name: "fov_calibrate.py", path: "tests/calibration/fov_calibrate.py", purpose: "Measure camera FOV with ruler → compute correct FOCAL_LENGTH_MM. Most important calibration.", when: "Before first flight (bench, indoors OK). Re-check on flight day.", flags: ["--headless"], output: "Terminal: corrected FOCAL_LENGTH_MM to put in config.py", risk: "none" as const },
      { name: "fov_test_simple.py", path: "tests/calibration/fov_test_simple.py", purpose: "Quick single-measurement FOV sanity check", when: "Quick verify after calibration", flags: [], output: "Terminal: measured vs expected FOV", risk: "none" as const },
      { name: "alt_test.py", path: "tests/calibration/alt_test.py", purpose: "FOV calibration at real altitude (needs Cube telemetry for altitude)", when: "Flight day: fly to known altitude, measure FOV from real image", flags: [], output: "Terminal: FOV at altitude", risk: "none" as const },
      { name: "lens_calibrate.py", path: "tests/calibration/lens_calibrate.py", purpose: "Lens distortion calibration using checkerboard pattern. Fixes barrel distortion for edge-of-frame accuracy.", when: "Optional: only if detections near frame edges are inaccurate", flags: ["--headless", "--board 9x6", "--load"], output: "Saves calibration_data.npz", risk: "none" as const },
    ] as TestScript[],
  },
  {
    category: "Diagnostics",
    folder: "tests/diagnostics/",
    purpose: "IS IT WORKING? — System health dashboards. Run when you need to check if everything is connected.",
    scripts: [
      { name: "diagnostics.py", path: "tests/diagnostics/diagnostics.py", purpose: "3-view dashboard: connectivity / camera+AI / telemetry. The main 'is everything working?' check.", when: "First thing at field, and whenever something seems wrong", flags: ["--headless"], output: "Terminal: 5 subsystems (Camera, AI, Cube, GPS, GS) — green/red status", risk: "none" as const },
      { name: "cube_monitor.py", path: "tests/diagnostics/cube_monitor.py", purpose: "Raw MAVLink message inspector — see all message types, rates, latest values", when: "Debug Cube communication issues", flags: [], output: "Terminal: live MAVLink message table", risk: "none" as const },
      { name: "camera_stream.py", path: "tests/diagnostics/camera_stream.py", purpose: "MJPEG video stream to browser. Verify laptop can see Pi camera.", when: "Verify camera + network before flight", flags: ["--with-detection", "--res 320x240", "--fps 5"], output: "Browser: http://PI_IP:8090/stream", risk: "none" as const },
    ] as TestScript[],
  },
  {
    category: "Flight Tests (Progressive — numbered by risk)",
    folder: "tests/flight/",
    purpose: "CAN IT FLY? — Each step builds trust. Never skip a step. Numbered 0a→4.",
    scripts: [
      { name: "0a_cube_commands.py", path: "tests/flight/0a_cube_commands.py", purpose: "Bench: test individual MAVLink commands (mode changes, arm). Verify Pi→Cube command path works.", when: "Before first flight, on bench with no props", flags: [], output: "Terminal: command ACKs from Cube", risk: "none" as const },
      { name: "0b_bench_mission.py", path: "tests/flight/0b_bench_mission.py", purpose: "Bench: walk Cube through full mission sequence (GUIDED, waypoints, LAND). No props, won't fly.", when: "After 0a passes. Proves full command sequence reaches Cube.", flags: [], output: "Terminal: mode changes + ACKs", risk: "none" as const },
      { name: "0c_feedback_test.py", path: "tests/flight/0c_feedback_test.py", purpose: "Bench: vision→GPS pipeline proof. Camera sees dummy → AI detects → GPS estimate updates. No commands sent.", when: "Before flight day. Carry drone over printed dummy on table.", flags: ["--headless"], output: "Terminal: detection coords, GPS estimates", risk: "none" as const },
      { name: "1_passive_flight.py", path: "tests/flight/1_passive_flight.py", purpose: "Manual RC flight — pilot flies, Pi watches with camera + AI. Logs detections, buzzer beeps. Sends ZERO commands to Cube.", when: "First real outdoor test. Fly over dummy at different altitudes.", flags: ["--headless", "--stream", "--save-detections"], output: "CSV log + geotagged detection images + MJPEG stream", risk: "low" as const },
      { name: "2_waypoints.py", path: "tests/flight/2_waypoints.py", purpose: "Fly 4 GPS waypoints in GUIDED mode. No camera, no CV — just arm, takeoff, fly, land. Proves MAVLink commands work on real hardware.", when: "After Step 1 (MP AUTO) passes. Tests YOUR code on real Cube.", flags: ["--dry-run", "--alt 10"], output: "Terminal: waypoint progress", risk: "medium" as const },
      { name: "3_auto_detect.py", path: "tests/flight/3_auto_detect.py", purpose: "Fly Mission Planner AUTO waypoints + AI detection. On detection → switch to GUIDED and hover. SENDS COMMANDS.", when: "After passive flight proves CV works outdoors", flags: [], output: "Terminal: detection + mode switch", risk: "medium" as const },
      { name: "4_detect_and_center.py", path: "tests/flight/4_detect_and_center.py", purpose: "Autonomous: fly waypoints + AI → center on target → hover. Intermediate test before full main.py.", when: "After 3_auto_detect works. Operator controls: l=land, r=resume, q=RTL.", flags: ["--alt 15", "--dry-run"], output: "Terminal: centering progress", risk: "high" as const },
    ] as TestScript[],
  },
  {
    category: "Day 1 Experiments (all passive, CSV output)",
    folder: "tests/day_1_experiments/",
    purpose: "WHAT'S THE DATA? — Structured experiments during flight. All passive (zero commands). Each produces a CSV for post-flight analysis.",
    scripts: [
      { name: "altitude_sweep.py", path: "tests/day_1_experiments/altitude_sweep.py", purpose: "Detection rate vs altitude. Pilot hovers at 10/15/20/25/30m above dummy, 30s each. Auto-bins by altitude.", when: "During passive flight (Step 2). Determines max reliable detection altitude.", flags: ["--headless", "--stream"], output: "exp_altitude_TIMESTAMP.csv + summary table", risk: "none" as const },
      { name: "speed_sweep.py", path: "tests/day_1_experiments/speed_sweep.py", purpose: "Detection rate vs flyover speed. Pilot flies over dummy at 3/5/7 m/s. Measures blur metric per frame.", when: "During passive flight. Determines max reliable speed.", flags: ["--headless", "--stream", "--alt 15"], output: "exp_speed_TIMESTAMP.csv + summary table", risk: "none" as const },
      { name: "gps_accuracy.py", path: "tests/day_1_experiments/gps_accuracy.py", purpose: "GPS estimate error vs known dummy position. Uses pixel→GPS conversion. Needs known dummy GPS coordinates.", when: "During any flight over dummy. Predicts landing accuracy.", flags: ["--headless", "--stream", "--dummy-gps LAT,LON"], output: "exp_gps_TIMESTAMP.csv", risk: "none" as const },
      { name: "gps_drift.py", path: "tests/day_1_experiments/gps_drift.py", purpose: "GPS noise floor while hovering. Records GPS at 4 Hz, computes CEP50/CEP95.", when: "During any hover. Measures minimum possible GPS error.", flags: ["--headless", "--duration 60"], output: "exp_drift_TIMESTAMP.csv", risk: "none" as const },
      { name: "model_compare.py", path: "tests/day_1_experiments/model_compare.py", purpose: "Benchmark all .tflite models in models/ folder. Speed, detection rate, confidence comparison.", when: "Before flight day (bench). Pick best model for conditions.", flags: ["--list", "--frames 50", "--model PATH"], output: "Terminal: comparison table + winner", risk: "none" as const },
      { name: "detection_log.py", path: "tests/day_1_experiments/detection_log.py", purpose: "General catch-all flight logger. Logs everything: detection, telemetry, GPS, battery. Optional image saving.", when: "Any flight. The general-purpose recorder.", flags: ["--headless", "--stream", "--save-detections"], output: "exp_detlog_TIMESTAMP.csv + detection_images/", risk: "none" as const },
    ] as TestScript[],
  },
  {
    category: "Laptop Development Tools",
    folder: "tests/laptop/",
    purpose: "DEVELOPMENT ONLY — for testing on laptop, not for Pi or flight day.",
    scripts: [
      { name: "test_all.py", path: "tests/laptop/test_all.py", purpose: "Full system connectivity check (camera + AI + Cube)", when: "Quick sanity check on laptop", flags: [], output: "Terminal: pass/fail for each", risk: "none" as const },
      { name: "test_camera.py", path: "tests/laptop/test_camera.py", purpose: "Camera preview + snapshot", when: "Verify camera works on laptop", flags: [], output: "Camera window", risk: "none" as const },
      { name: "test_cv.py", path: "tests/laptop/test_cv.py", purpose: "AI model loading + detection test", when: "Verify model loads and detects", flags: ["--camera"], output: "Terminal: detection results", risk: "none" as const },
      { name: "test_cube.py", path: "tests/laptop/test_cube.py", purpose: "Cube heartbeat, GPS, attitude, battery", when: "Verify Cube connection (SITL or real)", flags: [], output: "Terminal: telemetry data", risk: "none" as const },
      { name: "test_tflite.py", path: "tests/laptop/test_tflite.py", purpose: "TFLite inference on laptop (same code path as Pi)", when: "Verify TFLite works without Ultralytics", flags: [], output: "Terminal: inference results", risk: "none" as const },
    ] as TestScript[],
  },
];

// ── Calibration steps ────────────────────────────────────────────────
export const CALIBRATIONS: CalibrationStep[] = [
  { id: "fov", name: "FOV / Focal Length", location: "both", script: "tests/calibration/fov_calibrate.py --headless", what: "Measures camera field of view with ruler. Computes FOCAL_LENGTH_MM. This is the most important calibration — wrong FOV means wrong GPS estimates from pixel positions.", configUpdate: "config.py → FOCAL_LENGTH_MM" },
  { id: "lens", name: "Lens Distortion", location: "bench", script: "tests/calibration/lens_calibrate.py", what: "Checkerboard pattern → camera matrix + distortion coefficients. Fixes barrel distortion that causes pixel→GPS errors near frame edges. Optional but improves accuracy.", configUpdate: "Saves calibration_data.npz" },
  { id: "alt-fov", name: "Altitude FOV Check", location: "field", script: "tests/calibration/alt_test.py", what: "Verify FOV measurement at real altitude. Fly to known height, compare measured vs expected visible area on ground. Confirms bench calibration holds at flight altitude." },
  { id: "model", name: "Model Selection", location: "bench", script: "tests/day_1_experiments/model_compare.py --frames 50", what: "Benchmark all available TFLite models. Compare speed, detection rate, confidence. Pick best model for flight day conditions.", configUpdate: "cp models/BEST.tflite best.tflite" },
];

// ── Flight day plan ──────────────────────────────────────────────────
export const FLIGHT_STEPS: FlightStep[] = [
  { id: "0", name: "Setup & Diagnostics", script: "tests/diagnostics/diagnostics.py", risk: "None", purpose: "Verify all systems connected and working at the field.", details: ["Connect Pi + laptop to same WiFi", "Start mavproxy on Pi", "Run diagnostics — all 5 green", "Connect Mission Planner via TCP", "Wait for GPS lock (fix_type=3, sats>=8)"] },
  { id: "1", name: "Mission Planner AUTO (no code)", script: "Mission Planner only", risk: "Low (standard MP flight)", purpose: "Prove drone flies, GPS works, RTL works. YOUR code is NOT running.", details: ["Upload 4 waypoints in MP", "Arm via RC", "Switch to AUTO", "Drone flies pattern and RTLs", "Kill switch: RC → STABILIZE"] },
  { id: "1.5", name: "Waypoint Test (your code, no CV)", script: "tests/flight/2_waypoints.py --alt 10", risk: "Medium (your commands)", purpose: "Prove YOUR MAVLink commands work on real hardware. No camera, no AI.", details: ["Arms, takes off to 10m", "Flies 4 GPS waypoints", "Lands at launch point", "Kill switch: RC override always active"] },
  { id: "2", name: "Passive CV Flight", script: "tests/flight/1_passive_flight.py --headless --stream", risk: "None (zero commands)", purpose: "First real CV test outdoors. Pilot flies RC, Pi watches and logs. ZERO commands sent.", details: ["Pilot hovers above dummy at different altitudes", "Pi detects + buzzer + logs CSV", "Saves geotagged detection images", "Review after: at what altitude does it detect?", "Run altitude_sweep.py simultaneously"] },
  { id: "3", name: "Full Dashboard (pi_flight.py)", script: "pi_flight.py --fps 4", risk: "High (sends commands)", purpose: "Test complete N→investigate→classify→L→land flow.", details: ["Browser dashboard at http://PI_IP:8090", "Fly over dummy → detection alert", "Press N → drone flies to estimate", "Classify: Y=casualty, I=item of interest, X=false positive", "Press L → land within 5-10m of target (R07 safe zone)", "FAKE DET button if CV not working"] },
  { id: "4", name: "Full Autonomous (main.py)", script: "main.py", risk: "High (full auto)", purpose: "The real mission: search → detect → center → descend → verify → land.", details: ["Full state machine runs", "Lawnmower search pattern", "AI detection triggers centering", "Operator classifies: Y=casualty, I=item of interest, X=false positive", "Lands within 5-10m of target (R07 safe zone, ~7.5m offset)"] },
];

// ── GPS estimation (how it works) ────────────────────────────────────
export const GPS_ESTIMATION = {
  title: "How GPS Estimation Works",
  steps: [
    "Camera captures frame at known altitude + GPS position + yaw",
    "AI detects target → returns pixel position (x, y) in frame",
    "pixel_to_gps() uses camera geometry (FOV, altitude, yaw) to project pixel → ground GPS coordinate",
    "Each observation weighted by 1/altitude² (lower altitude = more accurate = higher weight)",
    "Centre-snap observations get 10× bonus weight (target at frame centre = minimal projection error)",
    "Spatial clustering groups observations by GPS distance (30m threshold)",
    "Running total average (most stable) + Kalman filter (Bayesian, adapts over time)",
    "Result: estimated dummy GPS position with ~0.5-3m accuracy depending on altitude and calibration",
  ],
  whyCalibrationMatters: "The pixel→GPS conversion uses FOCAL_LENGTH_MM from config.py. If this value is wrong (not calibrated), every GPS estimate will have a systematic offset. This is the ONE thing you can fix before flying — all other errors (GPS drift, wind) are random and average out over multiple observations.",
};

// ── Connection architecture ──────────────────────────────────────────
export const CONNECTIONS = {
  diagram: [
    "Cube (ArduCopter) ← TELEM2 UART → Pi GPIO (921600 baud)",
    "Pi ← mavproxy bridge → UDP (Pi scripts) + TCP (Mission Planner)",
    "Pi ← picamera2 → Camera (IMX296, 640×480, BGR)",
    "Pi ← WiFi → Laptop browser (http://PI_IP:8090)",
    "Rangefinder/Lidar → Cube (I2C/serial, precise AGL altitude for descent + landing)",
    "RC Controller → Cube (hardware-level, always overrides software)",
  ],
  mavproxy: "sudo /opt/mavlink/mavlink-venv/bin/mavproxy.py --master=/dev/ttyAMA0 --baudrate=921600 --streamrate=10 --out=udpout:127.0.0.1:14550 --out=tcpin:0.0.0.0:5762",
  whyMavproxy: "Python 3.13 + pyserial has broken serial reads on Pi (bytes dropped, BAD_DATA). mavproxy runs in its own venv with Python 3.11 and bridges the serial to UDP/TCP.",
};

// ── Key config values ────────────────────────────────────────────────
export const KEY_CONFIG = [
  { param: "TARGET_ALT", value: "30m", desc: "Search altitude. Lower if AI can't detect from this height.", tuneWith: "altitude_sweep.py" },
  { param: "VERIFY_ALT", value: "15m", desc: "Descent altitude for close confirmation before landing." },
  { param: "SEARCH_SPEED_MPS", value: "10 m/s", desc: "Lawnmower speed. Lower if motion blur kills detection.", tuneWith: "speed_sweep.py" },
  { param: "FOCAL_LENGTH_MM", value: "6.0", desc: "Camera focal length. MUST calibrate with ruler.", tuneWith: "fov_calibrate.py" },
  { param: "SENSOR_WIDTH_MM", value: "5.02", desc: "IMX296 sensor chip width. From datasheet, don't change." },
  { param: "CONFIDENCE_THRESHOLD", value: "0.4", desc: "Min detection confidence. Lower = more detections + more false positives." },
  { param: "SEARCH_AREA_GPS", value: "[4 GPS corners]", desc: "Search polygon for real flights. Update before each flight.", tuneWith: "main.py --dry-run" },
];

// ── Model management ─────────────────────────────────────────────────
export const MODELS = {
  current: [
    { name: "best.tflite", desc: "Primary model (YOLOv8n custom-trained on synthetic dummy images)", size: "~6MB" },
    { name: "models/custom_yolov8n.tflite", desc: "Copy of best.tflite (baseline for comparison)", size: "~6MB" },
    { name: "models/human.tflite", desc: "COCO YOLOv8n person detector (80 classes, backup if custom model fails)", size: "~13MB" },
    { name: "models/best2.tflite", desc: "Placeholder — replace with retrained model", size: "~6MB" },
  ],
  howToSwap: [
    "Option A: cp models/OTHER.tflite best.tflite (then restart script)",
    "Option B: python main.py --model models/OTHER.tflite (no copy needed)",
    "Compare all: python tests/day_1_experiments/model_compare.py --frames 50",
  ],
  toPrepare: [
    "Export COCO person detector: yolo export model=yolov8n.pt format=tflite",
    "Export INT8 quantized: yolo export model=best.pt format=tflite int8=True",
    "Optionally retrain with real photos of dummy in grass at various angles",
  ],
};
