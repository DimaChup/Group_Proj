/**
 * RightSidebar — unified right panel with four modes:
 *   [Team] = team members, comms, blockers
 *   [Prep] = Dima's pre-flight checklist (day before)
 *   [Focus] = Dima's personal priority areas (NFZ, vision, FOV/geotagging)
 *   [Day 1] = On-field flight day steps (sequential, 9 steps)
 * Toggle between modes with the top tab strip.
 * Ctrl+R toggles the whole sidebar on/off (handled in App.tsx).
 */
import { useState, useEffect } from "react";
import { TEAM, CHAT_DIGEST } from "./hub-data";
import { ROADMAP, LEVEL_COLORS, STATUS_COLORS } from "./mission-data";

/* ─── Types ─── */
type Mode = "team" | "prep" | "focus" | "day1";
type TeamSection = "members" | "chat" | "blockers";

/* ─── Team data ─── */
const MEMBER_TASKS: Record<string, { level: number; tasks: string[] }> = {
  dima:    { level: 2, tasks: ["Pi tested + working", "Dashboard + documentation", "Flight day prep", "Passive flight test next"] },
  robin:   { level: 1, tasks: ["GCS / detection image display", "Needs geotagged images from flights"] },
  edward:  { level: 2, tasks: ["CV model training (YOLOv8)", "Needs real Pi camera photos for retraining"] },
  herish:  { level: 1, tasks: ["Hardware + GPS confirmed outdoors", "RC kill switch config"] },
  member5: { level: 0, tasks: ["Role TBD"] },
};
const LEVEL_NAMES: Record<number, string> = { 0: "Foundation", 1: "L1", 2: "L2", 3: "L3" };

/* ─── Prep data ─── */
interface PrepTask {
  id: string;
  task: string;
  command?: string;
  detail: string;
  time: string;
}

const CORE_TASKS: PrepTask[] = [
  { id: "fov", task: "FOV Calibration", command: "python tests/calibration/fov_calibrate.py", detail: "Camera + ruler at known height. Update FOCAL_LENGTH_MM in config.py.", time: "10 min" },
  { id: "lens", task: "Lens Distortion Calibration", command: "python tests/calibration/lens_calibrate.py --board 9x6", detail: "Checkerboard, 10+ angles. Saves calibration_data.npz.", time: "15 min" },
  { id: "model", task: "Export Backup Model", command: "yolo export model=yolov8n.pt format=tflite", detail: "COCO person detector as TFLite fallback. Copy to models/.", time: "15 min" },
  { id: "compare", task: "Compare Models", command: "python tests/day_1_experiments/model_compare.py --frames 50", detail: "Benchmark all .tflite models. Pick the best.", time: "5 min" },
  { id: "dryrun", task: "Dry-Run Pattern", command: "python main.py --dry-run", detail: "Verify SEARCH_AREA_GPS covers the right field.", time: "2 min" },
  { id: "stream", task: "Test Video Stream", command: "python tests/diagnostics/camera_stream.py --with-detection", detail: "Open http://PI_IP:8090, confirm MJPEG feed + detection boxes.", time: "5 min" },
];

const BONUS_TASKS: PrepTask[] = [
  { id: "rc", task: "Test RC Connection", detail: "Bind RC to Cube, verify sticks in MP, test kill switch (STABILIZE), set failsafe = RTL.", time: "10 min" },
  { id: "arch", task: "Learn Connection Architecture", detail: "Cube-UART-Pi-mavproxy-UDP/TCP-MP-Browser-RC. Understand each link and port.", time: "15 min" },
  { id: "sim", task: "Run Simulations", command: "python simple_simulator.py", detail: "Practice field workflow: fly, detect, investigate, classify, land. Also test pi_flight.py in SIMULATION.", time: "30 min" },
  { id: "bench", task: "CV Benchmark on Pi", command: "python tests/hardware/benchmark.py", detail: "Get real FPS number. Set --fps flag to match on flight day.", time: "5 min" },
];

/* ─── Focus data (Dima's personal priority areas) ─── */
interface FocusArea {
  id: string;
  area: string;
  color: string;
  items: { id: string; task: string; detail: string; script?: string }[];
}

const FOCUS_AREAS: FocusArea[] = [
  {
    id: "nfz", area: "SSSI Geofence", color: "#ef4444",
    items: [
      { id: "nfz-1", task: "Research ArduCopter exclusion fences", detail: "FENCE_ENABLE, FENCE_TYPE, FENCE_ACTION params. Inclusion vs exclusion polygon." },
      { id: "nfz-2", task: "Test standalone geofence in SITL", detail: "Upload SSSI polygon in Mission Planner Fence tab. Fly toward it in GUIDED mode.", script: "Mission Planner → Fence tab" },
      { id: "nfz-3", task: "Test on real drone (cp-6b)", detail: "Fly toward SSSI boundary deliberately. Measure closest approach distance." },
      { id: "nfz-4", task: "Integrate NFZ into planning.py", detail: "Skip lawnmower waypoints inside SSSI. Route around the polygon.", script: "planning.py" },
      { id: "nfz-5", task: "Add SSSI check to main.py investigate", detail: "Don't fly to detections near/inside SSSI. Buffer zone.", script: "main.py" },
    ],
  },
  {
    id: "vision", area: "Vision & Models", color: "#8b5cf6",
    items: [
      { id: "vis-1", task: "Capture real training photos", detail: "Fly over dummy, save images with capture_training.py. 100+ photos at various altitudes.", script: "capture_training.py (http://PI_IP:8091)" },
      { id: "vis-2", task: "Retrain YOLOv8n on real data", detail: "Upload to Google Colab, train on real aerial photos. Export TFLite.", script: "docs/TRAINING_GUIDE.md" },
      { id: "vis-3", task: "Try NCNN backend on Pi", detail: "3x faster than TFLite (~83ms vs 250ms). Caveat: Ultralytics v8.4+ blocked NCNN on ARM64.", script: "Branch: ncnn-experiment" },
      { id: "vis-4", task: "Compare models on field", detail: "Swap with: cp models/X.tflite best.tflite or --model flag. Run model_compare.py.", script: "tests/day_1_experiments/model_compare.py" },
    ],
  },
  {
    id: "fov", area: "FPS / Resolution / FOV → Geotagging", color: "#06b6d4",
    items: [
      { id: "fov-1", task: "Understand the math chain", detail: "FOCAL_LENGTH_MM + SENSOR_WIDTH_MM + altitude → GSD (m/px) → pixel offset → GPS offset. GeoTransformer in utils.py.", script: "utils.py GeoTransformer" },
      { id: "fov-2", task: "Test resolution vs detection vs FPS", detail: "320x240 / 640x480 / 800x600. Each: measure FPS, detection rate, detection distance.", script: "tests/hardware/benchmark.py" },
      { id: "fov-3", task: "Verify FOV from altitude", detail: "Hover at known height, measure visible ground area. Compare with calculated FOV.", script: "tests/calibration/alt_test.py" },
      { id: "fov-4", task: "Measure geotagging error at each resolution", detail: "Lower resolution = faster but less accurate geotagging. Find the sweet spot.", script: "tests/day_1_experiments/gps_accuracy.py" },
    ],
  },
  {
    id: "lidar", area: "Rangefinder / Lidar", color: "#f59e0b",
    items: [
      { id: "lid-1", task: "Identify rangefinder model + specs", detail: "Team has one available (model TBD). Check range, accuracy, interface (I2C/serial/PWM)." },
      { id: "lid-2", task: "Wire to Cube + configure ArduCopter", detail: "RNGFND1_TYPE, RNGFND1_PIN, RNGFND1_MAX_CM. Connect to appropriate Cube port.", script: "Mission Planner → Full Parameter List" },
      { id: "lid-3", task: "Verify readings in Mission Planner", detail: "Point at floor, check sonarrange value matches ruler. Test outdoors on grass." },
      { id: "lid-4", task: "Terrain deduction: GPS_alt − rangefinder = ground_level", detail: "Useful for knowing slopes near casualty. Barometric alt = relative to launch, rangefinder = true AGL." },
      { id: "lid-5", task: "Low hover-drop approach", detail: "Descend to ~1m true AGL using rangefinder, release payload, fly away. Avoids terrain risk vs landing.", script: "main.py APPROACH state" },
    ],
  },
  {
    id: "servo", area: "Servo Release (Tarot)", color: "#ec4899",
    items: [
      { id: "srv-1", task: "Understand the mechanism", detail: "Tarot = double-throw servo. Two PWM values: hold position + release position. Pi sends DO_SET_SERVO via MAVLink → mavproxy → Cube → AUX OUT → servo." },
      { id: "srv-2", task: "Configure AUX output on Cube", detail: "SERVOx_FUNCTION, SERVOx_MIN/MAX/TRIM. Assign an AUX channel (e.g. SERVO9) for payload release.", script: "Mission Planner → Servo Output" },
      { id: "srv-3", task: "Bench test: trigger from Pi script", detail: "Send DO_SET_SERVO command, verify servo moves. No flying needed.", script: "tests/hardware/buzzer_test.py (adapt for servo)" },
      { id: "srv-4", task: "Integrate into state machine", detail: "After landing confirmation, send release command. Verify with visual check or limit switch.", script: "main.py LANDING state" },
    ],
  },
];

/* ─── Day 1 data (on-field sequential steps) ─── */
interface Day1Step {
  id: string;
  step: number;
  title: string;
  scripts?: string[];
  stream?: string;
  detail: string;
  proves: string;
  fallback?: string;
}

const DAY1_STEPS: Day1Step[] = [
  {
    id: "d1-diag", step: 1, title: "Run diagnostics",
    scripts: ["python tests/diagnostics/diagnostics.py"],
    stream: "http://PI_IP:8090",
    detail: "Nice UI on Pi side, or --headless via PuTTY. Optionally load vision model to verify camera + AI.",
    proves: "Camera, Cube connection, GPS, AI model all responding.",
    fallback: "If camera fails: check CSI cable. If Cube fails: check mavproxy + baud rate. If model fails: check best.tflite exists.",
  },
  {
    id: "d1-rc", step: 2, title: "Fly via RC only",
    detail: "No scripts, no Pi involvement. Pure RC manual flight. Takeoff, hover, move around, land. Test kill switch (STABILIZE on RC).",
    proves: "Drone flies, RC works, kill switch is reliable. No code needed.",
    fallback: "If RC doesn't bind: re-bind in Mission Planner. If motors don't spin: check arming checks (pre-arm).",
  },
  {
    id: "d1-mp-capture", step: 3, title: "Fly with Mission Planner + capture script",
    scripts: ["python capture_training.py"],
    stream: "http://PI_IP:8091",
    detail: "Connect Mission Planner via mavproxy TCP. Fly manually on RC while capture_training.py streams video. SPACE=photo, V=video.",
    proves: "MP telemetry works in-flight, video stream works over WiFi, camera data is usable for retraining.",
    fallback: "If stream laggy: reduce resolution (240x180) or quality. If MP disconnects: check TCP port 5762.",
  },
  {
    id: "d1-mp-auto", step: 4, title: "Mission Planner AUTO waypoints",
    detail: "Upload 4-waypoint square pattern in Mission Planner at 10-15m. Switch to AUTO on RC. Drone flies pattern + RTL. Your code NOT involved.",
    proves: "Cube GPS navigation works, AUTO mode works, RTL works.",
    fallback: "If drone drifts badly: tune WPNAV params. If doesn't switch to AUTO: check flight mode channel on RC.",
  },
  {
    id: "d1-waypoints", step: 5, title: "Waypoint mission via script",
    scripts: ["python tests/flight/2_waypoint_test.py"],
    detail: "Load waypoints from waypoints.json (drawn on laptop). Script arms, takes off, flies 3-4 GPS waypoints in GUIDED mode, lands. No camera, no CV.",
    proves: "Your MAVLink commands (arm, takeoff, goto, land) work on real hardware.",
    fallback: "If waypoints wrong: redraw with tests/flight/draw_waypoints.py on laptop, push, pull on Pi.",
  },
  {
    id: "d1-passive", step: 6, title: "Passive flight with CV + geotagging",
    scripts: ["python passive_watch.py", "python tests/flight/1_passive_flight.py"],
    stream: "http://PI_IP:8090",
    detail: "Pilot flies RC. Pi runs passive_watch.py: camera + AI + GPS estimation + video stream. Sends ZERO commands. Logs detections with geotagged positions. Buzzer beeps on detection.",
    proves: "CV works outdoors, detection altitude, geotagging accuracy. Safe — Pi never controls the drone.",
    fallback: "If no detections: lower CONFIDENCE in config.py (try 0.25). If GPS estimate way off: check FOV calibration.",
  },
  {
    id: "d1-nfz", step: 7, title: "Test geofence standalone",
    detail: "In Mission Planner Fence tab: upload SSSI polygon as exclusion zone. Fly toward it in GUIDED. Verify drone stops/RTLs at boundary. Create a separate small test NFZ area if needed.",
    proves: "ArduCopter fence enforcement works. FENCE_ENABLE, FENCE_TYPE, FENCE_ACTION params correct.",
    fallback: "If fence ignored: check FENCE_ENABLE=1, FENCE_TYPE=7, FENCE_ACTION=1 (RTL). Re-upload polygon.",
  },
  {
    id: "d1-sitl", step: 8, title: "Simulate full mission in SITL",
    scripts: ["python main.py (SIMULATION mode)", "python pi_flight.py (SIMULATION mode)"],
    detail: "Already have working components confirmed individually. Run full autonomous mission in SITL on laptop with all features enabled. Verify end-to-end.",
    proves: "State machine, search pattern, detection, centering, descent, verification — all work together in simulation.",
  },
  {
    id: "d1-real", step: 9, title: "Hook SITL simulation to real drone",
    scripts: ["python main.py", "python pi_flight.py"],
    stream: "http://PI_IP:8090",
    detail: "Same code that worked in SITL, now on real hardware. Config auto-detects Pi. Start with log-only mode (CV detects but doesn't trigger actions). Then full autonomous if safe.",
    proves: "Everything works on real hardware. The mission.",
    fallback: "If anything unexpected: RC kill switch to STABILIZE immediately. Review logs. Fall back to earlier step.",
  },
];

const DAY1_STORAGE_KEY = "dima-day1-checked";
function loadDay1Checked(): Set<string> {
  try {
    const raw = localStorage.getItem(DAY1_STORAGE_KEY);
    if (raw) return new Set(JSON.parse(raw));
  } catch { /* ignore */ }
  return new Set();
}

const FOCUS_STORAGE_KEY = "dima-focus-checked";
function loadFocusChecked(): Set<string> {
  try {
    const raw = localStorage.getItem(FOCUS_STORAGE_KEY);
    if (raw) return new Set(JSON.parse(raw));
  } catch { /* ignore */ }
  return new Set();
}

const PREP_STORAGE_KEY = "dima-prep-checked";
function loadChecked(): Set<string> {
  try {
    const raw = localStorage.getItem(PREP_STORAGE_KEY);
    if (raw) return new Set(JSON.parse(raw));
  } catch { /* ignore */ }
  return new Set();
}

/* ─── Component ─── */
export default function RightSidebar() {
  const [mode, setMode] = useState<Mode>("team");
  const [teamSection, setTeamSection] = useState<TeamSection>("members");
  const [checked, setChecked] = useState<Set<string>>(loadChecked);
  const [focusChecked, setFocusChecked] = useState<Set<string>>(loadFocusChecked);
  const [day1Checked, setDay1Checked] = useState<Set<string>>(loadDay1Checked);

  useEffect(() => {
    localStorage.setItem(PREP_STORAGE_KEY, JSON.stringify([...checked]));
  }, [checked]);

  useEffect(() => {
    localStorage.setItem(FOCUS_STORAGE_KEY, JSON.stringify([...focusChecked]));
  }, [focusChecked]);

  useEffect(() => {
    localStorage.setItem(DAY1_STORAGE_KEY, JSON.stringify([...day1Checked]));
  }, [day1Checked]);

  const toggleCheck = (id: string) => {
    setChecked(prev => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id); else next.add(id);
      return next;
    });
  };

  const toggleFocus = (id: string) => {
    setFocusChecked(prev => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id); else next.add(id);
      return next;
    });
  };

  const toggleDay1 = (id: string) => {
    setDay1Checked(prev => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id); else next.add(id);
      return next;
    });
  };

  const coreCount = CORE_TASKS.filter(t => checked.has(t.id)).length;
  const bonusCount = BONUS_TASKS.filter(t => checked.has(t.id)).length;
  const totalDone = coreCount + bonusCount;
  const totalAll = CORE_TASKS.length + BONUS_TASKS.length;

  const focusTotal = FOCUS_AREAS.reduce((sum, a) => sum + a.items.length, 0);
  const focusDone = FOCUS_AREAS.reduce((sum, a) => sum + a.items.filter(i => focusChecked.has(i.id)).length, 0);

  const day1Total = DAY1_STEPS.length;
  const day1Done = DAY1_STEPS.filter(s => day1Checked.has(s.id)).length;

  return (
    <div className="w-72 bg-zinc-900/95 border-l border-zinc-800 flex flex-col h-full backdrop-blur-sm shrink-0">
      {/* ─── Mode tabs ─── */}
      <div className="flex border-b border-zinc-800 shrink-0">
        <button
          onClick={() => setMode("team")}
          className={`flex-1 py-2 text-[10px] font-bold tracking-wider uppercase transition-all ${
            mode === "team"
              ? "text-blue-400 border-b-2 border-blue-500 bg-zinc-800/20"
              : "text-zinc-600 hover:text-zinc-400"
          }`}
        >
          Team
        </button>
        <button
          onClick={() => setMode("prep")}
          className={`flex-1 py-2 text-[10px] font-bold tracking-wider uppercase transition-all relative ${
            mode === "prep"
              ? "text-amber-400 border-b-2 border-amber-500 bg-zinc-800/20"
              : "text-zinc-600 hover:text-zinc-400"
          }`}
        >
          Prep
          {totalDone > 0 && totalDone < totalAll && (
            <span className="ml-1.5 text-[8px] text-amber-500/70">{totalDone}/{totalAll}</span>
          )}
          {totalDone === totalAll && (
            <span className="ml-1.5 text-[8px] text-green-500">Done</span>
          )}
        </button>
        <button
          onClick={() => setMode("focus")}
          className={`flex-1 py-2 text-[10px] font-bold tracking-wider uppercase transition-all relative ${
            mode === "focus"
              ? "text-cyan-400 border-b-2 border-cyan-500 bg-zinc-800/20"
              : "text-zinc-600 hover:text-zinc-400"
          }`}
        >
          Focus
          {focusDone > 0 && focusDone < focusTotal && (
            <span className="ml-1.5 text-[8px] text-cyan-500/70">{focusDone}/{focusTotal}</span>
          )}
          {focusDone === focusTotal && focusTotal > 0 && (
            <span className="ml-1.5 text-[8px] text-green-500">Done</span>
          )}
        </button>
        <button
          onClick={() => setMode("day1")}
          className={`flex-1 py-2 text-[10px] font-bold tracking-wider uppercase transition-all relative ${
            mode === "day1"
              ? "text-green-400 border-b-2 border-green-500 bg-zinc-800/20"
              : "text-zinc-600 hover:text-zinc-400"
          }`}
        >
          Day 1
          {day1Done > 0 && day1Done < day1Total && (
            <span className="ml-1.5 text-[8px] text-green-500/70">{day1Done}/{day1Total}</span>
          )}
          {day1Done === day1Total && (
            <span className="ml-1.5 text-[8px] text-green-500">Done</span>
          )}
        </button>
      </div>

      {/* ─── TEAM MODE ─── */}
      {mode === "team" && (
        <>
          <div className="p-3 border-b border-zinc-800">
            <h2 className="text-[11px] font-bold text-zinc-300 tracking-wider uppercase">Team</h2>
            <p className="text-[9px] text-zinc-600 mt-0.5">People, comms, blockers</p>
          </div>

          <div className="flex border-b border-zinc-800">
            {([
              { id: "members" as TeamSection, label: "Members" },
              { id: "chat" as TeamSection, label: "Comms" },
              { id: "blockers" as TeamSection, label: "Blockers" },
            ]).map(tab => (
              <button key={tab.id}
                onClick={() => setTeamSection(tab.id)}
                className={`flex-1 py-1.5 text-[9px] transition-all ${
                  teamSection === tab.id
                    ? "text-white border-b border-blue-500 bg-zinc-800/30"
                    : "text-zinc-600 hover:text-zinc-400"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          <div className="flex-1 overflow-y-auto">
            {teamSection === "members" && (
              <div className="p-2 space-y-1.5">
                {TEAM.map(m => {
                  const mt = MEMBER_TASKS[m.id];
                  const lvlColor = mt ? LEVEL_COLORS[mt.level] : "#6b7280";
                  return (
                    <div key={m.id} className="p-2.5 rounded bg-zinc-800/30 border border-zinc-800/50">
                      <div className="flex items-center gap-2">
                        <div className="w-2.5 h-2.5 rounded-full" style={{ background: m.color }} />
                        <span className="text-[10px] font-medium text-zinc-200">{m.name}</span>
                        {mt && (
                          <span className="text-[7px] px-1 rounded font-bold ml-auto"
                            style={{ color: lvlColor, background: lvlColor + "15" }}>
                            {LEVEL_NAMES[mt.level]}
                          </span>
                        )}
                      </div>
                      <div className="text-[8px] text-zinc-500 mt-0.5">{m.role}</div>
                      {mt && (
                        <div className="mt-1 space-y-0">
                          {mt.tasks.map((t, i) => (
                            <div key={i} className="text-[8px] text-zinc-400 pl-2 border-l border-zinc-800">
                              {t}
                            </div>
                          ))}
                        </div>
                      )}
                      {m.needsFromYou && (
                        <div className="text-[8px] text-amber-400/80 mt-1.5 px-2 py-1 bg-amber-500/5 rounded border border-amber-500/10">
                          Needs: {m.needsFromYou}
                        </div>
                      )}
                      {m.lastUpdate && (
                        <div className="text-[7px] text-zinc-700 mt-1">{m.lastUpdate}</div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}

            {teamSection === "chat" && (
              <div className="p-2 space-y-1.5">
                <p className="text-[8px] text-zinc-600 px-1">Key decisions from team comms</p>
                {CHAT_DIGEST.map((c, i) => (
                  <div key={i} className="p-2.5 rounded bg-zinc-800/30 border border-zinc-800/50">
                    <div className="flex items-center gap-2">
                      <span className="text-[8px] text-zinc-600">{c.date}</span>
                      <span className="text-[10px] font-medium text-zinc-300">{c.from}</span>
                    </div>
                    <div className="text-[9px] text-zinc-400 mt-0.5">{c.summary}</div>
                    {c.actionNeeded && (
                      <div className="text-[8px] text-cyan-400/80 mt-1.5 px-2 py-1 bg-cyan-500/5 rounded border border-cyan-500/10">
                        Action: {c.actionNeeded}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}

            {teamSection === "blockers" && (
              <div className="p-2 space-y-1">
                <p className="text-[8px] text-zinc-600 px-1 mb-1">Steps blocking progress (L1 + L2)</p>
                {ROADMAP
                  .filter(s => (s.status === "todo" || s.status === "ready" || s.status === "blocked") && s.level <= 2)
                  .map(step => {
                    const sc = STATUS_COLORS[step.status];
                    const lc = LEVEL_COLORS[step.level];
                    return (
                      <div key={step.id} className="px-2 py-1.5 rounded hover:bg-zinc-800/30">
                        <div className="flex items-center gap-2">
                          <div className="w-1.5 h-1.5 rounded-full shrink-0" style={{ background: sc.color }} />
                          <span className="text-[9px] text-zinc-300">{step.name}</span>
                          <span className="text-[7px] px-1 rounded font-bold ml-auto"
                            style={{ color: lc, background: lc + "15" }}>
                            L{step.level}
                          </span>
                        </div>
                        <div className="text-[8px] text-zinc-600 ml-4 mt-0.5">{step.description}</div>
                      </div>
                    );
                  })}
              </div>
            )}
          </div>
        </>
      )}

      {/* ─── PREP MODE ─── */}
      {mode === "prep" && (
        <>
          <div className="p-3 border-b border-zinc-800">
            <div className="flex items-center justify-between">
              <h2 className="text-[11px] font-bold text-amber-400 tracking-wider uppercase">Dima's Prep</h2>
              <span className="text-[9px] text-zinc-500">{totalDone}/{totalAll}</span>
            </div>
            <p className="text-[9px] text-zinc-600 mt-0.5">Day before flight</p>
            <div className="mt-1.5 h-1 bg-zinc-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-amber-500 transition-all duration-300 rounded-full"
                style={{ width: `${(totalDone / totalAll) * 100}%` }}
              />
            </div>
          </div>

          <div className="flex-1 overflow-y-auto">
            <div className="p-2">
              <div className="flex items-center gap-2 px-2 mb-1">
                <span className="text-[9px] font-bold text-zinc-400 uppercase tracking-wider">Core</span>
                <span className="text-[8px] text-zinc-600">{coreCount}/{CORE_TASKS.length}</span>
                {coreCount === CORE_TASKS.length && <span className="text-[8px] text-green-500">Done</span>}
              </div>
              <div className="space-y-0.5">
                {CORE_TASKS.map(t => (
                  <PrepTaskRow key={t.id} t={t} done={checked.has(t.id)} onToggle={() => toggleCheck(t.id)} />
                ))}
              </div>
            </div>

            <div className="mx-3 border-t border-zinc-800/50 my-1" />

            <div className="p-2">
              <div className="flex items-center gap-2 px-2 mb-1">
                <span className="text-[9px] font-bold text-purple-400 uppercase tracking-wider">Bonus</span>
                <span className="text-[8px] text-zinc-600">{bonusCount}/{BONUS_TASKS.length}</span>
                {bonusCount === BONUS_TASKS.length && <span className="text-[8px] text-green-500">Done</span>}
              </div>
              <div className="space-y-0.5">
                {BONUS_TASKS.map(t => (
                  <PrepTaskRow key={t.id} t={t} done={checked.has(t.id)} onToggle={() => toggleCheck(t.id)} />
                ))}
              </div>
            </div>
          </div>

          <div className="p-2 border-t border-zinc-800">
            <button
              onClick={() => setChecked(new Set())}
              className="w-full text-[8px] text-zinc-600 hover:text-zinc-400 py-1 transition-all"
            >
              Reset all
            </button>
          </div>
        </>
      )}

      {/* ─── DAY 1 MODE ─── */}
      {mode === "day1" && (
        <>
          <div className="p-3 border-b border-zinc-800">
            <div className="flex items-center justify-between">
              <h2 className="text-[11px] font-bold text-green-400 tracking-wider uppercase">Flight Day 1</h2>
              <span className="text-[9px] text-zinc-500">{day1Done}/{day1Total}</span>
            </div>
            <p className="text-[9px] text-zinc-600 mt-0.5">On-field steps — follow in order</p>
            <div className="mt-1.5 h-1 bg-zinc-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-green-500 transition-all duration-300 rounded-full"
                style={{ width: `${(day1Done / day1Total) * 100}%` }}
              />
            </div>
          </div>

          <div className="flex-1 overflow-y-auto">
            <div className="p-2 space-y-1">
              {DAY1_STEPS.map(s => {
                const done = day1Checked.has(s.id);
                return (
                  <label
                    key={s.id}
                    className={`block px-2 py-2 rounded cursor-pointer transition-all hover:bg-zinc-800/40 ${
                      done ? "opacity-40" : ""
                    }`}
                  >
                    <div className="flex gap-2">
                      <input
                        type="checkbox"
                        checked={done}
                        onChange={() => toggleDay1(s.id)}
                        className="mt-0.5 shrink-0 accent-green-500"
                      />
                      <div className="min-w-0 flex-1">
                        <div className={`text-[10px] font-medium ${done ? "line-through text-zinc-500" : "text-zinc-200"}`}>
                          <span className="text-green-500/70 mr-1.5">{s.step}.</span>
                          {s.title}
                        </div>
                        <div className="text-[8px] text-zinc-500 leading-tight mt-0.5">{s.detail}</div>
                        {s.scripts && (
                          <div className="mt-1 space-y-0">
                            {s.scripts.map((sc, i) => (
                              <div key={i} className="text-[8px] text-blue-400/70 font-mono truncate">{sc}</div>
                            ))}
                          </div>
                        )}
                        {s.stream && (
                          <div className="text-[8px] text-purple-400/70 font-mono mt-0.5">{s.stream}</div>
                        )}
                        <div className="text-[8px] text-green-400/60 mt-1">
                          Proves: {s.proves}
                        </div>
                        {s.fallback && (
                          <div className="text-[8px] text-amber-400/50 mt-0.5">
                            If fails: {s.fallback}
                          </div>
                        )}
                      </div>
                    </div>
                  </label>
                );
              })}
            </div>
          </div>

          <div className="p-2 border-t border-zinc-800">
            <button
              onClick={() => setDay1Checked(new Set())}
              className="w-full text-[8px] text-zinc-600 hover:text-zinc-400 py-1 transition-all"
            >
              Reset all
            </button>
          </div>
        </>
      )}

      {/* ─── FOCUS MODE ─── */}
      {mode === "focus" && (
        <>
          <div className="p-3 border-b border-zinc-800">
            <div className="flex items-center justify-between">
              <h2 className="text-[11px] font-bold text-cyan-400 tracking-wider uppercase">Dima's Focus</h2>
              <span className="text-[9px] text-zinc-500">{focusDone}/{focusTotal}</span>
            </div>
            <p className="text-[9px] text-zinc-600 mt-0.5">Priority areas to work on next</p>
            <div className="mt-1.5 h-1 bg-zinc-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-cyan-500 transition-all duration-300 rounded-full"
                style={{ width: `${(focusDone / focusTotal) * 100}%` }}
              />
            </div>
          </div>

          <div className="flex-1 overflow-y-auto">
            {FOCUS_AREAS.map((area, ai) => {
              const areaDone = area.items.filter(i => focusChecked.has(i.id)).length;
              return (
                <div key={area.id}>
                  {ai > 0 && <div className="mx-3 border-t border-zinc-800/50 my-1" />}
                  <div className="p-2">
                    <div className="flex items-center gap-2 px-2 mb-1">
                      <div className="w-2 h-2 rounded-full" style={{ background: area.color }} />
                      <span className="text-[9px] font-bold uppercase tracking-wider" style={{ color: area.color }}>
                        {area.area}
                      </span>
                      <span className="text-[8px] text-zinc-600">{areaDone}/{area.items.length}</span>
                      {areaDone === area.items.length && <span className="text-[8px] text-green-500">Done</span>}
                    </div>
                    <div className="space-y-0.5">
                      {area.items.map(item => {
                        const done = focusChecked.has(item.id);
                        return (
                          <label
                            key={item.id}
                            className={`flex gap-2 px-2 py-1.5 rounded cursor-pointer transition-all hover:bg-zinc-800/40 ${
                              done ? "opacity-50" : ""
                            }`}
                          >
                            <input
                              type="checkbox"
                              checked={done}
                              onChange={() => toggleFocus(item.id)}
                              className="mt-0.5 shrink-0 accent-cyan-500"
                            />
                            <div className="min-w-0">
                              <div className={`text-[10px] font-medium ${done ? "line-through text-zinc-500" : "text-zinc-200"}`}>
                                {item.task}
                              </div>
                              {item.script && (
                                <div className="text-[8px] text-blue-400/70 font-mono mt-0.5 truncate">{item.script}</div>
                              )}
                              <div className="text-[8px] text-zinc-500 leading-tight mt-0.5">{item.detail}</div>
                            </div>
                          </label>
                        );
                      })}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          <div className="p-2 border-t border-zinc-800">
            <button
              onClick={() => setFocusChecked(new Set())}
              className="w-full text-[8px] text-zinc-600 hover:text-zinc-400 py-1 transition-all"
            >
              Reset all
            </button>
          </div>
        </>
      )}
    </div>
  );
}

/* ─── Prep task row ─── */
function PrepTaskRow({ t, done, onToggle }: { t: PrepTask; done: boolean; onToggle: () => void }) {
  return (
    <label
      className={`flex gap-2 px-2 py-1.5 rounded cursor-pointer transition-all hover:bg-zinc-800/40 ${
        done ? "opacity-50" : ""
      }`}
    >
      <input
        type="checkbox"
        checked={done}
        onChange={onToggle}
        className="mt-0.5 shrink-0 accent-amber-500"
      />
      <div className="min-w-0">
        <div className={`text-[10px] font-medium ${done ? "line-through text-zinc-500" : "text-zinc-200"}`}>
          {t.task}
          <span className="text-[8px] text-zinc-600 ml-1.5 font-normal">{t.time}</span>
        </div>
        {t.command && (
          <div className="text-[8px] text-blue-400/70 font-mono mt-0.5 truncate">{t.command}</div>
        )}
        <div className="text-[8px] text-zinc-500 leading-tight mt-0.5">{t.detail}</div>
      </div>
    </label>
  );
}
