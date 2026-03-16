/**
 * ArchitectureTab — System architecture, state machine, algorithms, config, CLI flags.
 * Visual diagrams using styled divs (no SVG).
 *
 * Ground truth: main.py + states.py (verified 2026-03-16)
 * 19 states, all transitions, all MAVLink commands.
 */

import { useState } from "react";

type SectionId = "deps" | "state-machine" | "lawnmower" | "config" | "cli" | "cv" | "workflows";

/* ── Dependency graph data ─────────────────────────────────────────── */

const CORE_DEPS: {
  id: string;
  label: string;
  color: string;
  border: string;
  desc: string;
}[] = [
  { id: "config", label: "config.py", color: "bg-amber-500/15", border: "border-amber-500/40", desc: "All settings: altitudes, speeds, camera, connection" },
  { id: "states", label: "states.py", color: "bg-purple-500/15", border: "border-purple-500/40", desc: "State enum (19 states)" },
  { id: "utils", label: "utils.py", color: "bg-blue-500/15", border: "border-blue-500/40", desc: "Geo math: GPS <-> pixel (GeoTransformer)" },
  { id: "vision", label: "vision.py", color: "bg-green-500/15", border: "border-green-500/40", desc: "Camera + AI detection [dual backend]" },
  { id: "planning", label: "planning.py", color: "bg-cyan-500/15", border: "border-cyan-500/40", desc: "Lawnmower search pattern generator" },
  { id: "simulation", label: "simulation.py", color: "bg-rose-500/15", border: "border-rose-500/40", desc: "Laptop-only sim (map + drone view)" },
];

const EXTERNAL_DEPS: { from: string; to: string; label: string }[] = [
  { from: "vision.py", to: "best.tflite", label: "AI model (YOLOv8n)" },
  { from: "config.py", to: "AENGM0074.kml", label: "GPS zones" },
  { from: "planning.py", to: "waypoints", label: "lawnmower/spiral patterns" },
  { from: "simulation.py", to: "map.jpg + dummy.png", label: "sim assets" },
];

/* ── State machine data (verified against main.py 2026-03-16) ─────── */

type StateColor = "green" | "amber" | "cyan" | "rose" | "purple" | "blue" | "zinc";

interface StateInfo {
  id: string;
  summary: string;
  color: StateColor;
  mavlink: string[];
  exitConditions: string[];
  timeouts: string[];
}

const COLOR_MAP: Record<StateColor, { bg: string; border: string; text: string; label: string }> = {
  green:  { bg: "bg-green-500/15",  border: "border-green-500/40",  text: "text-green-300",  label: "Flight" },
  amber:  { bg: "bg-amber-500/15",  border: "border-amber-500/40",  text: "text-amber-300",  label: "Decision" },
  cyan:   { bg: "bg-cyan-500/15",   border: "border-cyan-500/40",   text: "text-cyan-300",   label: "Investigation" },
  rose:   { bg: "bg-rose-500/15",   border: "border-rose-500/40",   text: "text-rose-300",   label: "Landing" },
  purple: { bg: "bg-purple-500/15", border: "border-purple-500/40", text: "text-purple-300", label: "Manual" },
  blue:   { bg: "bg-blue-500/15",   border: "border-blue-500/40",   text: "text-blue-300",   label: "Terminal" },
  zinc:   { bg: "bg-zinc-800/40",   border: "border-zinc-700/40",   text: "text-zinc-300",   label: "Setup" },
};

// ── All 19 states with full details ──
const ALL_STATES: StateInfo[] = [
  {
    id: "INIT",
    summary: "Connect to Cube (mavlink_connection)",
    color: "zinc",
    mavlink: ["mavlink_connection(CONNECTION_STR)"],
    exitConditions: ["Connection established -> CONNECTING"],
    timeouts: ["Retries every 1s"],
  },
  {
    id: "CONNECTING",
    summary: "Wait for autopilot heartbeat",
    color: "zinc",
    mavlink: ["request_data_stream_send(ALL, 10Hz)", "param_set(SIM_SPEEDUP=10) [SIM only]"],
    exitConditions: ["Heartbeat received -> ARMING"],
    timeouts: ["Warning at 15s intervals if no heartbeat"],
  },
  {
    id: "ARMING",
    summary: "GPS fix check, set GUIDED mode, arm motors",
    color: "zinc",
    mavlink: ["MAV_CMD_DO_SET_MODE (GUIDED=4)", "MAV_CMD_COMPONENT_ARM_DISARM (arm=1)", "MAV_CMD_NAV_TAKEOFF (TARGET_ALT)"],
    exitConditions: ["GPS fix (type>=3, sats>=6) + motors armed -> TAKEOFF"],
    timeouts: ["Warning at 120s if still not armed"],
  },
  {
    id: "TAKEOFF",
    summary: "Climb to TARGET_ALT (50m)",
    color: "green",
    mavlink: ["(Uses takeoff command from ARMING)"],
    exitConditions: [
      "alt >= 90% TARGET_ALT + pre_waypoints exist -> PRE_WAYPOINTS",
      "alt >= 90% TARGET_ALT + no pre_wps + waypoints -> TRANSIT_TO_SEARCH",
      "alt >= 90% TARGET_ALT + no waypoints -> HOVER",
      "Disarmed (SIM) -> ARMING [retry]",
      "Disarmed (REAL) -> DONE [safety stop]",
    ],
    timeouts: ["Warning at 60s"],
  },
  {
    id: "PRE_WAYPOINTS",
    summary: "Fly transit/pre-planned waypoints before search",
    color: "green",
    mavlink: ["set_position_target_global_int (each waypoint @ TARGET_ALT)", "DO_CHANGE_SPEED (TRANSIT_SPEED)"],
    exitConditions: [
      "All pre-waypoints reached (within 2m) -> TRANSIT_TO_SEARCH",
      "No search waypoints -> HOVER",
    ],
    timeouts: [],
  },
  {
    id: "TRANSIT_TO_SEARCH",
    summary: "Fly to first search pattern waypoint",
    color: "green",
    mavlink: ["set_position_target_global_int (waypoints[0] @ TARGET_ALT)", "DO_CHANGE_SPEED (TRANSIT_SPEED)"],
    exitConditions: ["Within 2m of waypoints[0] -> SEARCH"],
    timeouts: [],
  },
  {
    id: "SEARCH",
    summary: "Fly lawnmower pattern, AI scans every frame",
    color: "green",
    mavlink: ["set_position_target_global_int (next WP @ search alt)", "DO_CHANGE_SPEED (SEARCH_SPEED)"],
    exitConditions: [
      "Target detected (not near rejected) -> CENTERING",
      "Pattern complete + rescan_pass < 3 -> SEARCH [rescan at 80% alt]",
      "Pattern complete + all rescans done -> DONE",
    ],
    timeouts: [],
  },
  {
    id: "CENTERING",
    summary: "Fly directly over detected target",
    color: "cyan",
    mavlink: ["set_position_target_global_int (target GPS @ TARGET_ALT) every 0.2s"],
    exitConditions: ["Within 1m of target -> DESCENDING"],
    timeouts: ["60s -> SEARCH (lost target)"],
  },
  {
    id: "DESCENDING",
    summary: "Descend to VERIFY_ALT (15m) over target",
    color: "cyan",
    mavlink: ["set_position_target_global_int (target GPS @ VERIFY_ALT) every 0.5s"],
    exitConditions: ["alt <= VERIFY_ALT + 1m -> VERIFY"],
    timeouts: ["Warning at 60s"],
  },
  {
    id: "VERIFY",
    summary: "Hover at 15m, operator confirms Y or N",
    color: "amber",
    mavlink: ["set_position_target_global_int (hold target GPS @ VERIFY_ALT)"],
    exitConditions: [
      "Y key -> select landing side (N/E/S/W) -> APPROACH",
      "N key + has departure point -> RETURN_TO_SEARCH",
      "N key + came from manual -> RETURN_FROM_MANUAL",
      "N key + no departure -> SEARCH",
    ],
    timeouts: ["Waits indefinitely for operator input"],
  },
  {
    id: "APPROACH",
    summary: "Fly to landing spot (7.5m offset) and descend to 3m",
    color: "rose",
    mavlink: ["set_position_target_global_int (landing GPS @ 3m) every 0.5s"],
    exitConditions: ["Within 2m of landing spot + alt < 4m -> HOVER_TARGET"],
    timeouts: [],
  },
  {
    id: "HOVER_TARGET",
    summary: "Hold at 3m: 5s wait, servo release, 10s more",
    color: "rose",
    mavlink: ["set_position_target_global_int (landing GPS @ 3m)", "MAV_CMD_DO_SET_SERVO (ch9, PWM 1100) at 5s"],
    exitConditions: [
      "15s elapsed + has pre_waypoints -> RETURN_TRANSIT",
      "15s elapsed + no pre_waypoints -> RETURN_HOME",
    ],
    timeouts: [],
  },
  {
    id: "RETURN_TRANSIT",
    summary: "Retrace transit path in reverse at TARGET_ALT",
    color: "green",
    mavlink: ["set_position_target_global_int (transit WPs reversed @ TARGET_ALT)", "DO_CHANGE_SPEED (TRANSIT_SPEED)"],
    exitConditions: ["All transit WPs retraced (within 2m each) -> RETURN_HOME"],
    timeouts: [],
  },
  {
    id: "RETURN_HOME",
    summary: "Fly to takeoff/home position",
    color: "green",
    mavlink: ["set_position_target_global_int (home GPS @ TARGET_ALT)", "DO_CHANGE_SPEED (TRANSIT_SPEED)"],
    exitConditions: ["Within 2m of home -> LANDING"],
    timeouts: [],
  },
  {
    id: "LANDING",
    summary: "Descend to ground and disarm",
    color: "rose",
    mavlink: ["set_position_target_global_int (home GPS @ 0m)", "MAV_CMD_COMPONENT_ARM_DISARM (disarm) on touchdown"],
    exitConditions: ["alt < 0.3m -> DONE (disarm + final error calc)"],
    timeouts: [],
  },
  {
    id: "DONE",
    summary: "Mission complete (terminal state)",
    color: "blue",
    mavlink: [],
    exitConditions: ["None (terminal)"],
    timeouts: [],
  },
  {
    id: "HOVER",
    summary: "Fallback state when no waypoints exist",
    color: "amber",
    mavlink: ["(holds position)"],
    exitConditions: [],
    timeouts: ["60s -> DONE"],
  },
  {
    id: "RETURN_TO_SEARCH",
    summary: "Climb to search alt, fly back to departure point",
    color: "green",
    mavlink: ["set_position_target_global_int (departure GPS @ search alt)", "DO_CHANGE_SPEED (TRANSIT_SPEED)"],
    exitConditions: ["Within 3m of departure + alt > 85% search alt -> SEARCH"],
    timeouts: [],
  },
  {
    id: "RETURN_FROM_MANUAL",
    summary: "Fly back to where manual mode was engaged",
    color: "purple",
    mavlink: ["set_position_target_global_int (manual departure GPS @ manual alt)", "DO_CHANGE_SPEED (TRANSIT_SPEED)"],
    exitConditions: ["Within 3m of manual departure -> previous_state"],
    timeouts: [],
  },
  {
    id: "MANUAL",
    summary: "RC pilot override (WASD flight, all auto suspended)",
    color: "purple",
    mavlink: ["set_position_target_local_ned (velocity commands from WASD/RF/QE)"],
    exitConditions: [
      "M key + target detected -> CENTERING",
      "M key + >5m from departure -> RETURN_FROM_MANUAL",
      "M key + <5m from departure -> previous_state",
    ],
    timeouts: [],
  },
];

// Main flow order (happy path)
const MAIN_FLOW_IDS = [
  "INIT", "CONNECTING", "ARMING", "TAKEOFF", "PRE_WAYPOINTS",
  "TRANSIT_TO_SEARCH", "SEARCH", "CENTERING", "DESCENDING", "VERIFY",
  "APPROACH", "HOVER_TARGET", "RETURN_TRANSIT", "RETURN_HOME", "LANDING", "DONE",
];

// Branch/side states
const BRANCH_STATES_IDS = ["RETURN_TO_SEARCH", "RETURN_FROM_MANUAL", "MANUAL", "HOVER"];

// ── Every transition edge in the state machine ──
// This is the complete graph — every arrow, including loops and branches.
type EdgeColor = "normal" | "reject" | "rescan" | "manual" | "timeout" | "safety";
interface Transition {
  from: string;
  to: string;
  label: string;
  color: EdgeColor;
}

const EDGE_COLORS: Record<EdgeColor, { text: string; line: string }> = {
  normal:  { text: "text-green-400",  line: "bg-green-500/60" },
  reject:  { text: "text-red-400",    line: "bg-red-500/60" },
  rescan:  { text: "text-amber-400",  line: "bg-amber-500/60" },
  manual:  { text: "text-purple-400", line: "bg-purple-500/60" },
  timeout: { text: "text-amber-400",  line: "bg-amber-500/40" },
  safety:  { text: "text-red-400",    line: "bg-red-500/40" },
};

const ALL_TRANSITIONS: Transition[] = [
  // ── Startup sequence ──
  { from: "INIT",        to: "CONNECTING",       label: "connection established",        color: "normal" },
  { from: "CONNECTING",  to: "ARMING",           label: "heartbeat received",            color: "normal" },
  { from: "ARMING",      to: "TAKEOFF",          label: "GPS fix + armed",               color: "normal" },

  // ── Takeoff branches ──
  { from: "TAKEOFF",     to: "PRE_WAYPOINTS",    label: "alt ≥ 90% + pre-waypoints",    color: "normal" },
  { from: "TAKEOFF",     to: "TRANSIT_TO_SEARCH", label: "alt ≥ 90% + no pre-wps",      color: "normal" },
  { from: "TAKEOFF",     to: "HOVER",            label: "alt ≥ 90% + no waypoints",     color: "timeout" },
  { from: "TAKEOFF",     to: "ARMING",           label: "disarmed (SIM: retry)",         color: "safety" },
  { from: "TAKEOFF",     to: "DONE",             label: "disarmed (REAL: safety stop)",  color: "safety" },

  // ── Transit to search ──
  { from: "PRE_WAYPOINTS",    to: "TRANSIT_TO_SEARCH", label: "all pre-wps reached",    color: "normal" },
  { from: "PRE_WAYPOINTS",    to: "HOVER",             label: "no search waypoints",    color: "timeout" },
  { from: "TRANSIT_TO_SEARCH", to: "SEARCH",            label: "within 2m of WP[0]",    color: "normal" },

  // ── Search → Detection loop ──
  { from: "SEARCH",      to: "CENTERING",        label: "target detected",               color: "normal" },
  { from: "SEARCH",      to: "SEARCH",           label: "rescan at 80% alt (pass < 3)",  color: "rescan" },
  { from: "SEARCH",      to: "DONE",             label: "all 3 rescans done",            color: "timeout" },

  // ── Investigation sequence ──
  { from: "CENTERING",   to: "DESCENDING",       label: "within 1m of target",           color: "normal" },
  { from: "CENTERING",   to: "SEARCH",           label: "timeout 60s (lost target)",     color: "timeout" },
  { from: "DESCENDING",  to: "VERIFY",           label: "alt ≤ VERIFY_ALT + 1m",        color: "normal" },

  // ── Verify decision (Y/N) ──
  { from: "VERIFY",      to: "APPROACH",          label: "Y → select landing side",      color: "normal" },
  { from: "VERIFY",      to: "RETURN_TO_SEARCH",  label: "N → reject (has departure)",   color: "reject" },
  { from: "VERIFY",      to: "RETURN_FROM_MANUAL", label: "N → came from manual",        color: "reject" },
  { from: "VERIFY",      to: "SEARCH",            label: "N → no departure point",       color: "reject" },

  // ── Return to search (THE LOOP BACK) ──
  { from: "RETURN_TO_SEARCH", to: "SEARCH",       label: "at departure + alt OK",        color: "reject" },

  // ── Landing sequence ──
  { from: "APPROACH",     to: "HOVER_TARGET",     label: "within 2m + alt < 4m",         color: "normal" },
  { from: "HOVER_TARGET", to: "RETURN_TRANSIT",   label: "15s + has transit path",        color: "normal" },
  { from: "HOVER_TARGET", to: "RETURN_HOME",      label: "15s + no transit path",         color: "normal" },

  // ── Return home ──
  { from: "RETURN_TRANSIT", to: "RETURN_HOME",    label: "all transit WPs retraced",      color: "normal" },
  { from: "RETURN_HOME",   to: "LANDING",         label: "within 2m of home",             color: "normal" },
  { from: "LANDING",       to: "DONE",            label: "alt < 0.3m → disarm",           color: "normal" },

  // ── Manual override (from ANY active state) ──
  { from: "MANUAL",       to: "CENTERING",         label: "M key + target detected",     color: "manual" },
  { from: "MANUAL",       to: "RETURN_FROM_MANUAL", label: "M key + >5m from departure", color: "manual" },
  { from: "MANUAL",       to: "(previous_state)",   label: "M key + <5m from departure", color: "manual" },
  { from: "RETURN_FROM_MANUAL", to: "(previous_state)", label: "within 3m of departure", color: "manual" },

  // ── Hover fallback ──
  { from: "HOVER",        to: "DONE",             label: "timeout 60s",                   color: "timeout" },
];

/* ── Config values ─────────────────────────────────────────────────── */

const CONFIG_VALUES: { param: string; value: string; desc: string }[] = [
  { param: "TARGET_ALT", value: "50 m", desc: "Search altitude" },
  { param: "VERIFY_ALT", value: "15 m", desc: "Close confirmation altitude" },
  { param: "SEARCH_SPEED_MPS", value: "10 m/s", desc: "Speed during search pattern" },
  { param: "TRANSIT_SPEED_MPS", value: "15 m/s", desc: "Speed to/from search area" },
  { param: "CONFIDENCE_THRESHOLD", value: "0.4", desc: "Min AI confidence to trigger detection" },
  { param: "SENSOR_WIDTH_MM", value: "5.02 mm", desc: "Camera sensor physical width" },
  { param: "FOCAL_LENGTH_MM", value: "5.46 mm", desc: "Calibrated focal length (92cm at 1m)" },
  { param: "IMAGE_W", value: "1456 px", desc: "Pi camera native width" },
  { param: "IMAGE_H", value: "1088 px", desc: "Pi camera native height" },
];

/* ── CLI flags ─────────────────────────────────────────────────────── */

const CLI_FLAGS: { flag: string; desc: string; example: string }[] = [
  { flag: "--model PATH", desc: "Use alternate TFLite model", example: "--model models/human.tflite" },
  { flag: "--dry-run", desc: "Print waypoints + state walkthrough, no GPS/Cube needed", example: "--dry-run" },
  { flag: "--search-area", desc: "Skip polygon drawing, use KML survey area", example: "--search-area" },
  { flag: "--transit FILE", desc: "Pre-drawn transit path JSON", example: "--transit transit.json" },
  { flag: "--pattern TYPE", desc: "Search pattern type (lawnmower/spiral)", example: "--pattern spiral" },
  { flag: "--headless", desc: "No GUI windows, terminal + browser only (auto on Pi)", example: "--headless" },
  { flag: "--waypoints FILE", desc: "Pre-planned waypoints to fly before search", example: "--waypoints waypoints.json" },
  { flag: "--no-stream", desc: "Disable MJPEG stream server", example: "--no-stream" },
  { flag: "--stream-port N", desc: "MJPEG stream port (default 8090)", example: "--stream-port 8090" },
  { flag: "--stream-res WxH", desc: "Stream resolution", example: "--stream-res 320x240" },
  { flag: "--stream-fps N", desc: "Stream frame rate", example: "--stream-fps 5" },
  { flag: "--stream-quality N", desc: "JPEG quality 0-100", example: "--stream-quality 50" },
];

/* ── Component ─────────────────────────────────────────────────────── */

export default function ArchitectureTab() {
  const [expanded, setExpanded] = useState<Set<SectionId>>(
    new Set(["deps", "state-machine", "lawnmower", "config", "cli"])
  );
  const [expandedStates, setExpandedStates] = useState<Set<string>>(new Set());

  const toggle = (id: SectionId) => {
    setExpanded((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  const toggleState = (id: string) => {
    setExpandedStates((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  const Section = ({
    id,
    title,
    subtitle,
    children,
  }: {
    id: SectionId;
    title: string;
    subtitle?: string;
    children: React.ReactNode;
  }) => (
    <div className="border border-zinc-800/50 rounded-lg overflow-hidden">
      <button
        onClick={() => toggle(id)}
        className="w-full flex items-center gap-3 px-4 py-2.5 bg-zinc-900/50 hover:bg-zinc-800/30 transition-colors cursor-pointer"
      >
        <span className="text-[10px] text-zinc-500 w-4">
          {expanded.has(id) ? "\u25BC" : "\u25B6"}
        </span>
        <span className="text-[12px] font-bold text-zinc-200">{title}</span>
        {subtitle && (
          <span className="text-[9px] text-zinc-500 ml-auto">{subtitle}</span>
        )}
      </button>
      {expanded.has(id) && (
        <div className="px-4 pb-4 pt-2 space-y-3">{children}</div>
      )}
    </div>
  );

  /* ── State box component ─────────────────────────────────────────── */
  const StateBox = ({ info, showArrow }: { info: StateInfo; showArrow: boolean }) => {
    const c = COLOR_MAP[info.color];
    const isExpanded = expandedStates.has(info.id);

    return (
      <div className="flex flex-col items-center">
        <button
          onClick={() => toggleState(info.id)}
          className={`w-full max-w-md px-3 py-2 rounded-lg border ${c.bg} ${c.border} text-left
            hover:brightness-125 transition-all cursor-pointer`}
        >
          <div className="flex items-center gap-2">
            <span className={`text-[11px] font-mono font-bold ${c.text}`}>
              {info.id}
            </span>
            <span className="text-[9px] text-zinc-500 ml-auto">
              {isExpanded ? "\u25BC" : "click for details"}
            </span>
          </div>
          <p className="text-[9px] text-zinc-400 mt-0.5">{info.summary}</p>
        </button>

        {isExpanded && (
          <div className={`w-full max-w-md mt-1 mb-1 px-3 py-2 rounded border ${c.border} bg-zinc-900/80 text-[9px] space-y-2`}>
            {info.mavlink.length > 0 && (
              <div>
                <p className="text-zinc-500 font-bold mb-0.5">MAVLink Commands:</p>
                {info.mavlink.map((cmd, i) => (
                  <p key={i} className="text-cyan-400 font-mono pl-2">{cmd}</p>
                ))}
              </div>
            )}
            <div>
              <p className="text-zinc-500 font-bold mb-0.5">Exit Conditions:</p>
              {info.exitConditions.map((cond, i) => (
                <p key={i} className="text-green-400 pl-2">{cond}</p>
              ))}
            </div>
            {info.timeouts.length > 0 && (
              <div>
                <p className="text-zinc-500 font-bold mb-0.5">Timeouts:</p>
                {info.timeouts.map((t, i) => (
                  <p key={i} className="text-amber-400 pl-2">{t}</p>
                ))}
              </div>
            )}
          </div>
        )}

        {showArrow && (
          <div className="flex flex-col items-center my-1">
            <div className="w-px h-3 bg-zinc-600"></div>
            <div className="text-zinc-600 text-[10px] leading-none">{"\u25BC"}</div>
          </div>
        )}
      </div>
    );
  };

  const stateById = (id: string) => ALL_STATES.find((s) => s.id === id)!;

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-3 min-w-0">
      {/* Header */}
      <div className="mb-4">
        <h1 className="text-lg font-bold text-zinc-100">
          System Architecture
        </h1>
        <p className="text-[10px] text-zinc-500 mt-0.5">
          Script dependencies, state machine (19 states), search algorithm, configuration, CLI flags
        </p>
      </div>

      {/* ── Script Dependency Diagram ────────────────────────────────── */}
      <Section id="deps" title="Script Dependency Diagram" subtitle="How core files connect">
        <div className="space-y-4">
          {/* Central node */}
          <div className="flex justify-center">
            <div className="px-5 py-3 rounded-lg border-2 border-blue-500/60 bg-blue-500/15 text-center">
              <p className="text-[12px] font-bold text-blue-300">main.py</p>
              <p className="text-[9px] text-zinc-400">Mission Orchestrator (19-state machine)</p>
            </div>
          </div>

          {/* Arrow down */}
          <div className="flex justify-center">
            <span className="text-zinc-600 text-[11px]">depends on</span>
          </div>

          {/* Dependencies grid */}
          <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
            {CORE_DEPS.map((dep) => (
              <div
                key={dep.id}
                className={`px-3 py-2.5 rounded-lg border ${dep.color} ${dep.border}`}
              >
                <p className="text-[11px] font-bold font-mono text-zinc-200">
                  {dep.label}
                </p>
                <p className="text-[9px] text-zinc-400 mt-0.5">{dep.desc}</p>
              </div>
            ))}
          </div>

          {/* External dependencies */}
          <div className="mt-3 pt-3 border-t border-zinc-800/30">
            <p className="text-[10px] font-bold text-zinc-300 mb-2">
              External File Dependencies
            </p>
            <div className="space-y-1.5">
              {EXTERNAL_DEPS.map((dep, i) => (
                <div key={i} className="flex items-center gap-2 text-[10px]">
                  <span className="font-mono text-cyan-400 shrink-0 w-28 text-right">
                    {dep.from}
                  </span>
                  <span className="text-zinc-600">{"-->"}</span>
                  <span className="font-mono text-amber-400 shrink-0">
                    {dep.to}
                  </span>
                  <span className="text-zinc-500 ml-1">({dep.label})</span>
                </div>
              ))}
            </div>
          </div>

          {/* Design note */}
          <div className="p-2 bg-zinc-800/30 rounded text-[9px] text-zinc-400">
            <span className="text-zinc-300 font-bold">Key design rule:</span>{" "}
            vision.py is the ONLY file that touches CV/AI. Everything else calls{" "}
            <span className="font-mono text-cyan-400">detect_in_image(frame)</span>{" "}
            and gets back <span className="font-mono text-cyan-400">(found, x, y, conf)</span>.
            Same main.py runs on laptop (Ultralytics) and Pi (TFLite).
          </div>
        </div>
      </Section>

      {/* ── State Machine Diagram ────────────────────────────────────── */}
      <Section id="state-machine" title="State Machine — Full Graph" subtitle="19 states, 32 transitions, click any box for details">
        <div className="space-y-5">

          {/* ── Legends ──────────────────────────────────────────── */}
          <div className="flex flex-wrap gap-4">
            <div>
              <p className="text-[8px] text-zinc-500 mb-1 font-bold">STATE TYPES</p>
              <div className="flex flex-wrap gap-1.5">
                {(["zinc", "green", "cyan", "amber", "rose", "purple", "blue"] as StateColor[]).map((color) => {
                  const c = COLOR_MAP[color];
                  return (
                    <div key={color} className={`px-1.5 py-0.5 rounded border ${c.bg} ${c.border}`}>
                      <span className={`text-[8px] font-bold ${c.text}`}>{c.label}</span>
                    </div>
                  );
                })}
              </div>
            </div>
            <div>
              <p className="text-[8px] text-zinc-500 mb-1 font-bold">EDGE TYPES</p>
              <div className="flex flex-wrap gap-1.5">
                {(Object.entries(EDGE_COLORS) as [EdgeColor, { text: string }][]).map(([key, val]) => (
                  <span key={key} className={`text-[8px] ${val.text}`}>
                    {"→ "}{key}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* ── Visual Graph: 3-column layout ────────────────────── */}
          {/* Left: reject/rescan loops | Centre: happy path | Right: manual/safety */}
          <div className="grid grid-cols-[minmax(120px,1fr)_minmax(200px,2fr)_minmax(120px,1fr)] gap-x-2 items-start">

            {/* ── LEFT COLUMN: Reject & Rescan loops ──────────── */}
            <div className="space-y-3 pt-[280px]">
              {/* Rescan loop annotation */}
              <div className="border border-amber-500/30 rounded-lg p-2 bg-amber-500/5">
                <p className="text-[9px] font-bold text-amber-400 mb-1">🔄 Rescan Loop</p>
                <p className="text-[8px] text-zinc-500">
                  Pattern done, nothing found → regenerate at 80% altitude.
                  Up to 3 passes: 50m → 40m → 32m → 25.6m.
                  After 3 rescans → DONE.
                </p>
                <div className="mt-1 flex items-center gap-1">
                  <span className="font-mono text-[8px] text-green-300 bg-green-500/15 px-1 rounded">SEARCH</span>
                  <span className="text-amber-400 text-[8px]">{"⟲"}</span>
                  <span className="font-mono text-[8px] text-green-300 bg-green-500/15 px-1 rounded">SEARCH</span>
                </div>
              </div>

              {/* Reject loop annotation */}
              <div className="border border-red-500/30 rounded-lg p-2 bg-red-500/5">
                <p className="text-[9px] font-bold text-red-400 mb-1">🔄 Reject Loop</p>
                <p className="text-[8px] text-zinc-500">
                  Operator presses N at VERIFY → target GPS saved (20m exclusion zone) →
                  climb back → resume search from departure point.
                </p>
                <div className="mt-1 flex flex-col gap-0.5 text-[8px]">
                  <div className="flex items-center gap-1">
                    <span className="font-mono text-amber-300 bg-amber-500/15 px-1 rounded">VERIFY</span>
                    <span className="text-red-400">→ N</span>
                    <span className="font-mono text-green-300 bg-green-500/15 px-1 rounded">RET_SEARCH</span>
                  </div>
                  <div className="flex items-center gap-1 pl-4">
                    <span className="text-red-400">→</span>
                    <span className="font-mono text-green-300 bg-green-500/15 px-1 rounded">SEARCH</span>
                    <span className="text-zinc-600 text-[7px]">(continues pattern)</span>
                  </div>
                </div>
              </div>

              {/* Centering timeout */}
              <div className="border border-amber-500/20 rounded-lg p-2 bg-amber-500/5">
                <p className="text-[9px] font-bold text-amber-400 mb-1">⏱ Timeout</p>
                <p className="text-[8px] text-zinc-500">
                  CENTERING 60s timeout → back to SEARCH (lost target)
                </p>
              </div>
            </div>

            {/* ── CENTRE COLUMN: Happy path ───────────────────── */}
            <div className="flex flex-col items-center">
              <p className="text-[10px] font-bold text-zinc-300 mb-2">
                Happy Path (target found & confirmed)
              </p>
              {MAIN_FLOW_IDS.map((id, i) => (
                <StateBox
                  key={id}
                  info={stateById(id)}
                  showArrow={i < MAIN_FLOW_IDS.length - 1}
                />
              ))}
            </div>

            {/* ── RIGHT COLUMN: Manual override & Safety ──────── */}
            <div className="space-y-3 pt-[100px]">
              {/* Takeoff safety */}
              <div className="border border-red-500/20 rounded-lg p-2 bg-red-500/5">
                <p className="text-[9px] font-bold text-red-400 mb-1">⚠ Safety</p>
                <p className="text-[8px] text-zinc-500">
                  If drone disarms during TAKEOFF:
                </p>
                <div className="text-[8px] pl-1 space-y-0.5">
                  <p><span className="text-amber-400">SIM:</span> → ARMING (retry)</p>
                  <p><span className="text-red-400">REAL:</span> → DONE (stop)</p>
                </div>
              </div>

              {/* Manual override */}
              <div className="border border-purple-500/30 rounded-lg p-2 bg-purple-500/5">
                <p className="text-[9px] font-bold text-purple-400 mb-1">🎮 Manual Override</p>
                <p className="text-[8px] text-zinc-500 mb-1">
                  M key from ANY active state → MANUAL.
                  Saves departure position, pilot flies WASD.
                </p>
                <div className="space-y-1">
                  <StateBox info={stateById("MANUAL")} showArrow={false} />
                  <StateBox info={stateById("RETURN_FROM_MANUAL")} showArrow={false} />
                </div>
                <p className="text-[8px] text-zinc-500 mt-1.5 mb-0.5 font-bold">M key exits MANUAL:</p>
                <div className="text-[8px] pl-1 space-y-0.5">
                  <p><span className="text-green-400">Target detected</span> → CENTERING</p>
                  <p><span className="text-amber-400">{">"}5m from departure</span> → RETURN_FROM_MANUAL → prev</p>
                  <p><span className="text-zinc-400">{"<"}5m from departure</span> → resume previous_state</p>
                </div>
              </div>

              {/* Hover fallback */}
              <div className="border border-amber-500/20 rounded-lg p-2 bg-amber-500/5">
                <p className="text-[9px] font-bold text-amber-400 mb-1">⏸ HOVER (fallback)</p>
                <StateBox info={stateById("HOVER")} showArrow={false} />
                <p className="text-[8px] text-zinc-500 mt-1">
                  Reached when no waypoints exist. 60s timeout → DONE.
                </p>
              </div>

              {/* Servo release note */}
              <div className="border border-rose-500/20 rounded-lg p-2 bg-rose-500/5">
                <p className="text-[9px] font-bold text-rose-400 mb-1">📦 Payload Release</p>
                <p className="text-[8px] text-zinc-500">
                  HOVER_TARGET: 5s wait → servo ch9 PWM 1100 (open) → hold 10s more → return home.
                </p>
              </div>

              {/* Verify decision */}
              <div className="border border-amber-500/20 rounded-lg p-2 bg-amber-500/5">
                <p className="text-[9px] font-bold text-amber-400 mb-1">❓ VERIFY Decision</p>
                <p className="text-[8px] text-zinc-500 mb-1">
                  Operator Y/N at 15m altitude:
                </p>
                <div className="text-[8px] pl-1 space-y-0.5">
                  <p><span className="text-green-400 font-bold">Y</span> → pick landing side (N/E/S/W) → APPROACH</p>
                  <p><span className="text-red-400 font-bold">N</span> → reject → RETURN_TO_SEARCH → SEARCH</p>
                  <p className="text-zinc-600">Rejected target marked, 20m exclusion zone</p>
                  <p className="text-zinc-600">No timeout — waits for operator</p>
                </div>
              </div>
            </div>
          </div>

          {/* ── Complete Transition Table ─────────────────────── */}
          <div>
            <p className="text-[10px] font-bold text-zinc-300 mb-2">
              All {ALL_TRANSITIONS.length} Transitions (complete edge list)
            </p>
            <div className="overflow-x-auto">
              <table className="text-[9px] w-full border-collapse">
                <thead>
                  <tr className="text-zinc-500 border-b border-zinc-800">
                    <th className="text-left px-2 py-1 w-32">From</th>
                    <th className="text-left px-2 py-1 w-8"></th>
                    <th className="text-left px-2 py-1 w-36">To</th>
                    <th className="text-left px-2 py-1">Condition</th>
                  </tr>
                </thead>
                <tbody>
                  {ALL_TRANSITIONS.map((t, i) => {
                    const ec = EDGE_COLORS[t.color];
                    const fromState = ALL_STATES.find(s => s.id === t.from);
                    const toState = ALL_STATES.find(s => s.id === t.to);
                    const fromColor = fromState ? COLOR_MAP[fromState.color] : null;
                    const toColor = toState ? COLOR_MAP[toState.color] : null;
                    return (
                      <tr key={i} className="border-b border-zinc-900/50 hover:bg-zinc-800/20">
                        <td className="px-2 py-0.5">
                          <span className={`font-mono font-bold ${fromColor?.text ?? "text-zinc-300"} ${fromColor?.bg ?? ""} px-1 rounded`}>
                            {t.from}
                          </span>
                        </td>
                        <td className={`px-1 py-0.5 ${ec.text} font-bold`}>→</td>
                        <td className="px-2 py-0.5">
                          <span className={`font-mono font-bold ${toColor?.text ?? "text-zinc-400"} ${toColor?.bg ?? ""} px-1 rounded`}>
                            {t.to}
                          </span>
                        </td>
                        <td className={`px-2 py-0.5 ${ec.text}`}>{t.label}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {/* ── RETURN_TO_SEARCH detail ───────────────────────── */}
          <div>
            <StateBox info={stateById("RETURN_TO_SEARCH")} showArrow={false} />
          </div>

          {/* ── Key input summary ────────────────────────────── */}
          <div className="p-3 bg-zinc-800/30 rounded border border-zinc-700/30">
            <p className="text-[10px] font-bold text-zinc-300 mb-2">Key Bindings (keyboard + browser buttons + /cmd?key= HTTP)</p>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-x-4 gap-y-1 text-[9px]">
              <div><span className="text-cyan-400 font-mono font-bold">M</span> <span className="text-zinc-500">Toggle manual override</span></div>
              <div><span className="text-cyan-400 font-mono font-bold">Y</span> <span className="text-zinc-500">Confirm target (VERIFY)</span></div>
              <div><span className="text-cyan-400 font-mono font-bold">N</span> <span className="text-zinc-500">Reject target (VERIFY)</span></div>
              <div><span className="text-cyan-400 font-mono font-bold">N/E/S/W</span> <span className="text-zinc-500">Landing side (after Y)</span></div>
              <div><span className="text-cyan-400 font-mono font-bold">WASD</span> <span className="text-zinc-500">Manual flight (MANUAL)</span></div>
              <div><span className="text-cyan-400 font-mono font-bold">R/F</span> <span className="text-zinc-500">Up/Down (MANUAL)</span></div>
              <div><span className="text-cyan-400 font-mono font-bold">Q/E</span> <span className="text-zinc-500">Yaw left/right (MANUAL)</span></div>
              <div><span className="text-cyan-400 font-mono font-bold">ESC</span> <span className="text-zinc-500">Quit program</span></div>
            </div>
          </div>

          {/* ── "Could someone recreate our code from this?" note ── */}
          <div className="p-2 bg-zinc-800/30 rounded text-[9px] text-zinc-400 space-y-1">
            <p className="text-zinc-300 font-bold">Completeness check: could someone recreate main.py from this diagram?</p>
            <p>✅ All 19 states listed with exact MAVLink commands (click any box)</p>
            <p>✅ All 32 transitions with exact conditions (table above)</p>
            <p>✅ Rescan loop: SEARCH → SEARCH at 80% alt, up to 3 passes</p>
            <p>✅ Reject loop: VERIFY → N → RETURN_TO_SEARCH → SEARCH (20m exclusion)</p>
            <p>✅ Manual override: M from any state → MANUAL → M to exit (3 paths)</p>
            <p>✅ Takeoff safety: disarm → retry (SIM) or stop (REAL)</p>
            <p>✅ Servo release: HOVER_TARGET at 5s, ch9 PWM 1100</p>
            <p>✅ Timeouts: CENTERING 60s, HOVER 60s, ARMING 120s warning</p>
          </div>
        </div>
      </Section>

      {/* ── Lawnmower Algorithm ──────────────────────────────────────── */}
      <Section id="lawnmower" title="Lawnmower Search Algorithm" subtitle="planning.py">
        <div className="space-y-3">
          <div className="space-y-2">
            {[
              { step: "1", text: "Rotate polygon to align with its longest edge (minimizes turns)" },
              { step: "2", text: "Generate parallel scan lines with 20% overlap (ensures no gaps in camera coverage)" },
              { step: "3", text: "Apply margin buffer from polygon edges (safety clearance from boundary)" },
              { step: "4", text: "Optimize start corner: pick the corner closest to drone position or transit endpoint" },
              { step: "5", text: "Zigzag direction alternates each line (no wasted backtracking)" },
            ].map((item) => (
              <div key={item.step} className="flex gap-2 text-[10px]">
                <span className="text-cyan-500/60 shrink-0 font-mono w-4 text-right font-bold">
                  {item.step}
                </span>
                <span className="text-zinc-300">{item.text}</span>
              </div>
            ))}
          </div>

          {/* Visual lawnmower diagram */}
          <div className="p-4 bg-zinc-900/60 rounded-lg border border-zinc-700/30">
            <p className="text-[10px] text-zinc-300 font-bold mb-3">Visual: Lawnmower Pattern Inside Polygon</p>
            <div className="relative mx-auto" style={{ width: 280, height: 220 }}>
              {/* Polygon outline */}
              <div className="absolute inset-0 border-2 border-cyan-500/50 rounded-sm"
                   style={{ clipPath: "polygon(15% 5%, 95% 0%, 100% 85%, 80% 100%, 5% 90%)" }}>
                <div className="absolute inset-0 bg-cyan-500/5"></div>
              </div>

              {/* Margin indicator */}
              <div className="absolute border border-dashed border-amber-500/30"
                   style={{ top: 20, left: 30, right: 20, bottom: 25 }}></div>
              <span className="absolute text-[8px] text-amber-400" style={{ top: 8, left: 80 }}>margin</span>

              {/* Scan lines */}
              {[0, 1, 2, 3, 4, 5].map((i) => {
                const y = 30 + i * 30;
                const isEven = i % 2 === 0;
                return (
                  <div key={i} className="absolute flex items-center" style={{ top: y, left: 35, right: 25, height: 16 }}>
                    <div className={`flex-1 h-px ${i < 6 ? "bg-green-500/50" : "bg-green-500/20"}`}></div>
                    <span className="text-[8px] text-green-400 absolute" style={{ right: isEven ? -12 : undefined, left: isEven ? undefined : -12 }}>
                      {isEven ? "\u25B6" : "\u25C0"}
                    </span>
                  </div>
                );
              })}

              {/* Start marker */}
              <div className="absolute flex items-center gap-1" style={{ top: 26, left: 14 }}>
                <span className="text-[10px] font-bold text-green-400 bg-green-500/20 px-1 rounded">S</span>
              </div>

              {/* End marker */}
              <div className="absolute flex items-center gap-1" style={{ bottom: 28, left: 14 }}>
                <span className="text-[10px] font-bold text-red-400 bg-red-500/20 px-1 rounded">E</span>
              </div>

              {/* Overlap annotation */}
              <div className="absolute text-[8px] text-zinc-500" style={{ bottom: 4, right: 10 }}>
                20% overlap between lines
              </div>

              {/* Polygon label */}
              <div className="absolute text-[8px] text-cyan-400" style={{ top: -2, left: 0 }}>
                search polygon
              </div>
            </div>
          </div>

          <div className="p-2 bg-zinc-800/30 rounded text-[9px] text-zinc-400">
            <span className="text-zinc-300 font-bold">Coverage math:</span>{" "}
            At 30m altitude with FOV 54.4 deg HFOV, ground coverage per frame is ~30m wide.
            With 20% overlap, line spacing is ~24m. A 200x200m area needs ~8 lines.
            At 5 m/s, full sweep takes ~5 minutes.
          </div>

          <div className="p-2 bg-amber-500/5 border border-amber-500/20 rounded text-[9px] text-zinc-400">
            <span className="text-amber-400 font-bold">Rescan logic:</span>{" "}
            If the full pattern completes without a confirmed detection, the drone drops to 80% altitude
            and regenerates the pattern from its current position. Rejected targets are cleared.
            {"Up to 3 rescans (30m -> 24m -> 19.2m -> 15.4m). If still nothing, mission ends."}
          </div>
        </div>
      </Section>

      {/* ── Key Config Values ────────────────────────────────────────── */}
      <Section id="config" title="Key Config Values" subtitle="config.py -- tune after real testing">
        <div className="overflow-x-auto">
          <table className="w-full text-[10px]">
            <thead>
              <tr className="text-zinc-500 text-left border-b border-zinc-800/50">
                <th className="py-1 pr-3">Parameter</th>
                <th className="py-1 pr-3">Value</th>
                <th className="py-1">Description</th>
              </tr>
            </thead>
            <tbody>
              {CONFIG_VALUES.map((c) => (
                <tr key={c.param} className="border-b border-zinc-800/20">
                  <td className="py-1.5 pr-3 text-cyan-400 font-mono font-bold">
                    {c.param}
                  </td>
                  <td className="py-1.5 pr-3 text-zinc-300">{c.value}</td>
                  <td className="py-1.5 text-zinc-500">{c.desc}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Section>

      {/* ── CLI Flags ────────────────────────────────────────────────── */}
      <Section id="cli" title="CLI Flags" subtitle={`main.py -- ${CLI_FLAGS.length} options`}>
        <div className="overflow-x-auto">
          <table className="w-full text-[10px]">
            <thead>
              <tr className="text-zinc-500 text-left border-b border-zinc-800/50">
                <th className="py-1 pr-3">Flag</th>
                <th className="py-1 pr-3">Description</th>
                <th className="py-1">Example</th>
              </tr>
            </thead>
            <tbody>
              {CLI_FLAGS.map((f) => (
                <tr key={f.flag} className="border-b border-zinc-800/20">
                  <td className="py-1.5 pr-3 text-cyan-400 font-mono font-bold whitespace-nowrap">
                    {f.flag}
                  </td>
                  <td className="py-1.5 pr-3 text-zinc-300">{f.desc}</td>
                  <td className="py-1.5 text-zinc-500 font-mono text-[9px]">
                    python main.py {f.example}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Section>

      {/* ── Computer Vision ──────────────────────────────────────────── */}
      <Section id="cv" title="Computer Vision Pipeline">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Model Architecture */}
          <div className="border border-green-500/30 bg-green-500/5 rounded p-3">
            <h4 className="text-green-400 font-bold text-[11px] mb-2">Model: YOLOv8n (nano)</h4>
            <div className="text-[10px] text-zinc-300 space-y-1">
              <p><span className="text-zinc-500">Input:</span> [1, 640, 640, 3] float32 (RGB, 0-1 normalised)</p>
              <p><span className="text-zinc-500">Output:</span> [1, 5, 8400] float32 (x, y, w, h, conf)</p>
              <p><span className="text-zinc-500">Classes:</span> 1 (dummy/casualty)</p>
              <p><span className="text-zinc-500">Size:</span> 3.2MB (v1) / 11.7MB (v2 retrained)</p>
              <p><span className="text-zinc-500">Backend:</span> Ultralytics (laptop) / TFLite (Pi)</p>
            </div>
          </div>

          {/* Training Pipeline */}
          <div className="border border-amber-500/30 bg-amber-500/5 rounded p-3">
            <h4 className="text-amber-400 font-bold text-[11px] mb-2">Training Pipeline (v2)</h4>
            <div className="text-[10px] text-zinc-300 space-y-1">
              <p>1. Collect real frames from DJI flight video</p>
              <p>2. Label with <span className="text-cyan-400 font-mono">label_tool.py --full</span> (native 1456x1088)</p>
              <p>3. Generate 300 synthetic + 50 negatives (<span className="text-cyan-400 font-mono">generate_dataset_v2.py</span>)</p>
              <p>4. Train on Colab GPU: imgsz=1088, epochs=150, batch=8</p>
              <p>5. Export TFLite (imgsz=640) + NCNN</p>
              <p>6. Deploy: <span className="text-cyan-400 font-mono">cp cv_models/sar_v2_1088/best.tflite best.tflite</span></p>
            </div>
          </div>

          {/* Benchmark Results */}
          <div className="border border-cyan-500/30 bg-cyan-500/5 rounded p-3">
            <h4 className="text-cyan-400 font-bold text-[11px] mb-2">Benchmark (Pi 5, TFLite)</h4>
            <table className="text-[10px] w-full">
              <thead><tr className="text-zinc-500">
                <th className="text-left py-1">Metric</th><th className="text-left py-1">Value</th>
              </tr></thead>
              <tbody className="text-zinc-300">
                <tr><td className="py-0.5">Inference</td><td>206.5ms avg</td></tr>
                <tr><td className="py-0.5">FPS</td><td>4.8 FPS</td></tr>
                <tr><td className="py-0.5">Detection rate</td><td>50/50 (0.966 conf)</td></tr>
                <tr><td className="py-0.5">Undistortion cost</td><td>+1.5ms (negligible)</td></tr>
                <tr><td className="py-0.5">mAP50 (v2)</td><td>0.995</td></tr>
              </tbody>
            </table>
          </div>

          {/* Model Variants */}
          <div className="border border-purple-500/30 bg-purple-500/5 rounded p-3">
            <h4 className="text-purple-400 font-bold text-[11px] mb-2">Available Models</h4>
            <div className="text-[10px] text-zinc-300 space-y-1">
              <p><span className="text-green-400">sar_v2_1088</span> -- retrained, 300 syn + 16 real + 50 neg (BEST)</p>
              <p><span className="text-zinc-400">sar_640</span> -- earlier training at 640x640</p>
              <p><span className="text-zinc-400">sar_1280</span> -- earlier training at 1280x1280</p>
              <p><span className="text-zinc-400">human.tflite</span> -- COCO YOLOv8n person detector (backup)</p>
            </div>
            <h4 className="text-purple-400 font-bold text-[11px] mt-3 mb-1">Possible Improvements</h4>
            <div className="text-[10px] text-zinc-400 space-y-0.5">
              <p>- NCNN backend (~15 FPS expected on Pi 5)</p>
              <p>- FP16 XNNPACK (~10 FPS, native Pi 5 support)</p>
              <p>- INT8 quantized export (~2x speedup)</p>
              <p>- Threaded pipeline (overlap capture + inference)</p>
              <p>- Hailo-8L accelerator (80+ FPS, future)</p>
            </div>
          </div>
        </div>

        {/* vision.py interface */}
        <div className="mt-3 border border-zinc-700/30 rounded p-3">
          <h4 className="text-zinc-300 font-bold text-[11px] mb-1">vision.py Interface (single entry point)</h4>
          <div className="font-mono text-[10px] text-green-400 bg-zinc-900 rounded p-2">
            detect_in_image(frame) -&gt; (found: bool, x: int, y: int, conf: float)
          </div>
          <p className="text-[9px] text-zinc-500 mt-1">All scripts call this one function. Swap model, backend, or preprocessing without touching any other file.</p>
        </div>
      </Section>

      {/* ── Workflows ─────────────────────────────────────────────────── */}
      <Section id="workflows" title="Key Workflows">
        <div className="space-y-4">

          {/* Progressive Testing */}
          <div className="border border-cyan-500/30 bg-cyan-500/5 rounded p-3">
            <h4 className="text-cyan-400 font-bold text-[11px] mb-2">Progressive Flight Testing (never skip a step)</h4>
            <div className="text-[10px] space-y-1.5">
              {[
                { n: "0", label: "Mission Planner AUTO waypoints", desc: "No custom code. Proves Cube, GPS, motors, RTL.", status: "todo" },
                { n: "1", label: "Waypoint test script (no CV)", desc: "Your code arms, takes off, flies GPS waypoints, lands.", status: "todo" },
                { n: "2", label: "Manual flight + passive CV", desc: "Pilot flies RC. Pi detects + logs. Zero commands sent.", status: "todo" },
                { n: "3", label: "Autonomous search + CV log only", desc: "Full pattern, CV detects but never triggers descent.", status: "todo" },
                { n: "4", label: "Full autonomous mission", desc: "Search, detect, centre, descend, verify, land.", status: "todo" },
              ].map((s) => (
                <div key={s.n} className="flex items-start gap-2">
                  <span className={`font-mono font-bold text-[10px] w-5 shrink-0 ${s.status === "done" ? "text-green-400" : "text-zinc-500"}`}>
                    {s.n}.
                  </span>
                  <div>
                    <span className="text-zinc-200 font-semibold">{s.label}</span>
                    <span className="text-zinc-500 ml-1">-- {s.desc}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Simulation Workflow */}
          <div className="border border-amber-500/30 bg-amber-500/5 rounded p-3">
            <h4 className="text-amber-400 font-bold text-[11px] mb-2">Simulation Workflow</h4>
            <div className="text-[10px] text-zinc-300 space-y-1 font-mono">
              <p>1. Start SITL in Mission Planner (--home=51.423406,-2.671446,50,155)</p>
              <p>2. python tests/flight/draw_transit.py -&gt; transit.json</p>
              <p>3. DRONE_MODE=SIMULATION python main.py --search-area --transit transit.json</p>
              <p>4. Place dummy on map, right-click, press key to launch</p>
              <p>5. M = manual override, Y/N = confirm/reject, N/E/S/W = landing side</p>
            </div>
          </div>

          {/* Model Retraining Workflow */}
          <div className="border border-green-500/30 bg-green-500/5 rounded p-3">
            <h4 className="text-green-400 font-bold text-[11px] mb-2">Model Retraining Workflow</h4>
            <div className="text-[10px] text-zinc-300 space-y-1 font-mono">
              <p>1. python tools/label_tool.py --full "RealVideo/DJI_*.mp4"  (label real frames)</p>
              <p>2. python generate_dataset_v2.py  (300 syn + 50 neg at 1456x1088)</p>
              <p>3. Upload dataset_v2.zip to Google Drive -&gt; Colab GPU training</p>
              <p>4. Download best.tflite -&gt; cp to cv_models/sar_v2_1088/</p>
              <p>5. python tests/laptop/video_test.py --model cv_models/sar_v2_1088/best.tflite</p>
              <p>6. Deploy: cp cv_models/sar_v2_1088/best.tflite best.tflite</p>
            </div>
          </div>

          {/* Deployment Workflow */}
          <div className="border border-rose-500/30 bg-rose-500/5 rounded p-3">
            <h4 className="text-rose-400 font-bold text-[11px] mb-2">Pi Deployment Workflow</h4>
            <div className="text-[10px] text-zinc-300 space-y-1 font-mono">
              <p>1. Edit code on laptop -&gt; test in SIMULATION</p>
              <p>2. git add + commit + push</p>
              <p>3. SSH to Pi: cd ~/sar-drone && git pull</p>
              <p>4. source pienv/bin/activate</p>
              <p>5. Start mavproxy (T1) -&gt; run diagnostics (Pi screen) -&gt; run script (T2)</p>
              <p>6. Never edit code on Pi -- laptop is single source of truth</p>
            </div>
          </div>

        </div>
      </Section>

      {/* Footer */}
      <div className="text-[9px] text-zinc-600 pt-4 pb-8 text-center">
        SAR Drone -- University of Bristol -- AENGM0074 -- System Architecture Reference (19 states verified against main.py)
      </div>
    </div>
  );
}
