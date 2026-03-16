/**
 * ArchitectureTab — System architecture, state machine, algorithms, config, CLI flags.
 * Visual diagrams using styled divs (no SVG).
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
  { id: "states", label: "states.py", color: "bg-purple-500/15", border: "border-purple-500/40", desc: "State enum (SEARCH, VERIFY, LANDING, etc.)" },
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

/* ── State machine data ────────────────────────────────────────────── */

const MAIN_STATES = [
  "INIT", "CONNECTING", "ARMING", "TAKEOFF", "PRE_WAYPOINTS",
  "TRANSIT_TO_SEARCH", "SEARCH", "CENTERING", "DESCENDING", "VERIFY",
  "APPROACH", "HOVER_TARGET", "RETURN_TRANSIT", "RETURN_HOME", "LANDING", "DONE",
];

const SPECIAL_STATES = [
  { name: "MANUAL", desc: "Toggle from any state with M key" },
  { name: "RETURN_TO_SEARCH", desc: "After N rejection at VERIFY" },
  { name: "RETURN_FROM_MANUAL", desc: "Resume after manual flight" },
];

const KEY_TRANSITIONS: { from: string; to: string; trigger: string; color: string }[] = [
  { from: "SEARCH", to: "CENTERING", trigger: "Target detected", color: "text-green-400" },
  { from: "CENTERING", to: "DESCENDING", trigger: "Centered on target", color: "text-blue-400" },
  { from: "DESCENDING", to: "VERIFY", trigger: "Reached verify altitude", color: "text-blue-400" },
  { from: "VERIFY", to: "APPROACH", trigger: "Y (confirm) -> select side", color: "text-green-400" },
  { from: "VERIFY", to: "RETURN_TO_SEARCH", trigger: "N (reject)", color: "text-red-400" },
  { from: "APPROACH", to: "HOVER_TARGET", trigger: "Reached offset position", color: "text-blue-400" },
  { from: "HOVER_TARGET", to: "RETURN_TRANSIT", trigger: "Servo release 5s, complete 15s", color: "text-amber-400" },
  { from: "SEARCH", to: "SEARCH (rescan)", trigger: "Pattern complete + no find -> 80% alt", color: "text-amber-400" },
  { from: "Any", to: "MANUAL", trigger: "M key", color: "text-purple-400" },
  { from: "MANUAL", to: "RETURN_FROM_MANUAL", trigger: "M key again", color: "text-purple-400" },
];

/* ── Config values ─────────────────────────────────────────────────── */

const CONFIG_VALUES: { param: string; value: string; desc: string }[] = [
  { param: "TARGET_ALT", value: "30 m", desc: "Search altitude" },
  { param: "VERIFY_ALT", value: "15 m", desc: "Close confirmation altitude" },
  { param: "SEARCH_SPEED_MPS", value: "5 m/s", desc: "Speed during search pattern" },
  { param: "TRANSIT_SPEED_MPS", value: "8 m/s", desc: "Speed to/from search area" },
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
  { flag: "--search-area FILE", desc: "Load search polygon from JSON file", example: "--search-area search_area.json" },
  { flag: "--transit", desc: "Enable transit to/from search area", example: "--transit" },
  { flag: "--pattern TYPE", desc: "Search pattern type (lawnmower/spiral)", example: "--pattern lawnmower" },
  { flag: "--headless", desc: "No GUI windows, terminal + browser only (auto on Pi)", example: "--headless" },
  { flag: "--waypoints FILE", desc: "Load waypoints from JSON file", example: "--waypoints waypoints.json" },
];

/* ── Component ─────────────────────────────────────────────────────── */

export default function ArchitectureTab() {
  const [expanded, setExpanded] = useState<Set<SectionId>>(
    new Set(["deps", "state-machine", "lawnmower", "config", "cli"])
  );

  const toggle = (id: SectionId) => {
    setExpanded((prev) => {
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
          {expanded.has(id) ? "▼" : "▶"}
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

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-3 min-w-0">
      {/* Header */}
      <div className="mb-4">
        <h1 className="text-lg font-bold text-zinc-100">
          System Architecture
        </h1>
        <p className="text-[10px] text-zinc-500 mt-0.5">
          Script dependencies, state machine, search algorithm, configuration, CLI flags
        </p>
      </div>

      {/* ── Script Dependency Diagram ────────────────────────────────── */}
      <Section id="deps" title="Script Dependency Diagram" subtitle="How core files connect">
        <div className="space-y-4">
          {/* Central node */}
          <div className="flex justify-center">
            <div className="px-5 py-3 rounded-lg border-2 border-blue-500/60 bg-blue-500/15 text-center">
              <p className="text-[12px] font-bold text-blue-300">main.py</p>
              <p className="text-[9px] text-zinc-400">Mission Orchestrator</p>
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
      <Section id="state-machine" title="State Machine Diagram" subtitle={`${MAIN_STATES.length} main + ${SPECIAL_STATES.length} special states`}>
        <div className="space-y-4">
          {/* Main flow */}
          <div>
            <p className="text-[10px] font-bold text-zinc-300 mb-2">
              Main Flow (happy path)
            </p>
            <div className="flex flex-wrap items-center gap-1">
              {MAIN_STATES.map((state, i) => (
                <div key={state} className="flex items-center gap-1">
                  <span
                    className={`px-2 py-1 rounded text-[9px] font-mono font-bold border ${
                      state === "SEARCH"
                        ? "bg-green-500/15 border-green-500/40 text-green-300"
                        : state === "VERIFY"
                          ? "bg-amber-500/15 border-amber-500/40 text-amber-300"
                          : state === "DONE"
                            ? "bg-blue-500/15 border-blue-500/40 text-blue-300"
                            : state === "CENTERING" || state === "DESCENDING"
                              ? "bg-cyan-500/15 border-cyan-500/40 text-cyan-300"
                              : state === "APPROACH" || state === "HOVER_TARGET"
                                ? "bg-rose-500/15 border-rose-500/40 text-rose-300"
                                : "bg-zinc-800/40 border-zinc-700/40 text-zinc-300"
                    }`}
                  >
                    {state}
                  </span>
                  {i < MAIN_STATES.length - 1 && (
                    <span className="text-zinc-600 text-[10px]">{">"}</span>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Special states */}
          <div>
            <p className="text-[10px] font-bold text-zinc-300 mb-2">
              Special States
            </p>
            <div className="flex flex-wrap gap-2">
              {SPECIAL_STATES.map((s) => (
                <div
                  key={s.name}
                  className="px-3 py-2 rounded-lg border border-purple-500/40 bg-purple-500/15"
                >
                  <p className="text-[10px] font-mono font-bold text-purple-300">
                    {s.name}
                  </p>
                  <p className="text-[9px] text-zinc-400">{s.desc}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Key transitions */}
          <div>
            <p className="text-[10px] font-bold text-zinc-300 mb-2">
              Key Transitions
            </p>
            <div className="space-y-1.5">
              {KEY_TRANSITIONS.map((t, i) => (
                <div
                  key={i}
                  className="flex items-center gap-2 text-[10px] bg-zinc-800/20 rounded px-3 py-1.5 border border-zinc-800/30"
                >
                  <span className="font-mono text-zinc-300 shrink-0 w-36 text-right">
                    {t.from}
                  </span>
                  <span className="text-zinc-600">{"-->"}</span>
                  <span className="font-mono text-zinc-300 shrink-0 w-40">
                    {t.to}
                  </span>
                  <span className={`${t.color} ml-1`}>{t.trigger}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Decision points */}
          <div className="p-2 bg-amber-500/5 border border-amber-500/20 rounded">
            <p className="text-[9px] text-amber-400">
              <span className="font-bold">VERIFY is the decision point:</span>{" "}
              Operator sees close-up at 15m. Press Y to confirm target and select approach side,
              or N to reject and resume search. M key toggles manual override from any state
              (RC pilot takes over, press M again to resume autonomous).
            </p>
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

          <div className="p-3 bg-zinc-800/30 rounded font-mono text-[9px] text-zinc-400 space-y-0.5">
            <p className="text-zinc-300 font-bold mb-1">Visual representation:</p>
            <p>{"  +---------+"}</p>
            <p>{"  | >>>>>>> |  Line 1 (left to right)"}</p>
            <p>{"  |         |"}</p>
            <p>{"  | <<<<<<< |  Line 2 (right to left)"}</p>
            <p>{"  |         |"}</p>
            <p>{"  | >>>>>>> |  Line 3 (left to right)"}</p>
            <p>{"  |         |"}</p>
            <p>{"  | <<<<<<< |  Line 4 (right to left)"}</p>
            <p>{"  +---------+"}</p>
            <p className="mt-1 text-zinc-500">{"  [20% overlap between lines]"}</p>
          </div>

          <div className="p-2 bg-zinc-800/30 rounded text-[9px] text-zinc-400">
            <span className="text-zinc-300 font-bold">Coverage math:</span>{" "}
            At 30m altitude with FOV 54.4 deg HFOV, ground coverage per frame is ~30m wide.
            With 20% overlap, line spacing is ~24m. A 200x200m area needs ~8 lines.
            At 5 m/s, full sweep takes ~5 minutes.
          </div>
        </div>
      </Section>

      {/* ── Key Config Values ────────────────────────────────────────── */}
      <Section id="config" title="Key Config Values" subtitle="config.py — tune after real testing">
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
      <Section id="cli" title="CLI Flags" subtitle="main.py command-line options">
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
              <p><span className="text-green-400">sar_v2_1088</span> — retrained, 300 syn + 16 real + 50 neg (BEST)</p>
              <p><span className="text-zinc-400">sar_640</span> — earlier training at 640x640</p>
              <p><span className="text-zinc-400">sar_1280</span> — earlier training at 1280x1280</p>
              <p><span className="text-zinc-400">human.tflite</span> — COCO YOLOv8n person detector (backup)</p>
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
            detect_in_image(frame) → (found: bool, x: int, y: int, conf: float)
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
                    <span className="text-zinc-500 ml-1">— {s.desc}</span>
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
              <p>2. python tests/flight/draw_transit.py → transit.json</p>
              <p>3. DRONE_MODE=SIMULATION python main.py --search-area --transit transit.json</p>
              <p>4. Place dummy on map → right-click → press key to launch</p>
              <p>5. M = manual override, Y/N = confirm/reject, N/E/S/W = landing side</p>
            </div>
          </div>

          {/* Model Retraining Workflow */}
          <div className="border border-green-500/30 bg-green-500/5 rounded p-3">
            <h4 className="text-green-400 font-bold text-[11px] mb-2">Model Retraining Workflow</h4>
            <div className="text-[10px] text-zinc-300 space-y-1 font-mono">
              <p>1. python tools/label_tool.py --full "RealVideo/DJI_*.mp4"  (label real frames)</p>
              <p>2. python generate_dataset_v2.py  (300 syn + 50 neg at 1456x1088)</p>
              <p>3. Upload dataset_v2.zip to Google Drive → Colab GPU training</p>
              <p>4. Download best.tflite → cp to cv_models/sar_v2_1088/</p>
              <p>5. python tests/laptop/video_test.py --model cv_models/sar_v2_1088/best.tflite</p>
              <p>6. Deploy: cp cv_models/sar_v2_1088/best.tflite best.tflite</p>
            </div>
          </div>

          {/* Deployment Workflow */}
          <div className="border border-rose-500/30 bg-rose-500/5 rounded p-3">
            <h4 className="text-rose-400 font-bold text-[11px] mb-2">Pi Deployment Workflow</h4>
            <div className="text-[10px] text-zinc-300 space-y-1 font-mono">
              <p>1. Edit code on laptop → test in SIMULATION</p>
              <p>2. git add + commit + push</p>
              <p>3. SSH to Pi: cd ~/sar-drone && git pull</p>
              <p>4. source pienv/bin/activate</p>
              <p>5. Start mavproxy (T1) → run diagnostics (Pi screen) → run script (T2)</p>
              <p>6. Never edit code on Pi — laptop is single source of truth</p>
            </div>
          </div>

        </div>
      </Section>

      {/* Footer */}
      <div className="text-[9px] text-zinc-600 pt-4 pb-8 text-center">
        SAR Drone — University of Bristol — AENGM0074 — System Architecture Reference
      </div>
    </div>
  );
}
