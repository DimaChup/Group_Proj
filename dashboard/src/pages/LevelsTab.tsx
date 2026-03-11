/**
 * LevelsTab — The "How": 3 product levels (L1 Manual, L2 Semi-Auto, L3 Full Auto)
 */
import { useState } from "react";
import { LEVELS, L2_CRITICAL_PATH, L2_PARALLEL_TASKS, L2_MILESTONES, type MissionLevel, type SteppingStone, type ParallelTask, type IfScenario, type Milestone } from "./mission-data";

export default function LevelsTab() {
  const [expanded, setExpanded] = useState<number>(2); // default to L2 (the target)

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-4 min-w-0">
      {/* Philosophy intro */}
      <div className="rounded-lg border border-zinc-800/50 bg-zinc-900/40 p-5">
        <div className="text-[9px] text-purple-400 uppercase tracking-widest font-bold mb-2">Why Three Levels?</div>
        <div className="text-[10px] text-zinc-400 leading-relaxed mb-3">
          We break the mission into three product levels that increase in autonomy and complexity.
          Each level is a <span className="text-zinc-200">working, demonstrable product</span> — not just a milestone.
          If we only achieve L1, we still have a useful system. L2 is the target for the flight test.
          L3 is a stretch goal that removes the pilot from the decision loop entirely.
        </div>
        <div className="flex gap-6 text-[9px]">
          <div className="flex items-center gap-2">
            <div className="w-2.5 h-2.5 rounded" style={{ background: "#22c55e" }} />
            <span className="text-zinc-400"><span className="text-zinc-200 font-medium">L1</span> — Pilot does everything, drone observes</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2.5 h-2.5 rounded" style={{ background: "#3b82f6" }} />
            <span className="text-zinc-400"><span className="text-zinc-200 font-medium">L2</span> — Drone flies autonomously, pilot confirms decisions</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2.5 h-2.5 rounded" style={{ background: "#a855f7" }} />
            <span className="text-zinc-400"><span className="text-zinc-200 font-medium">L3</span> — Drone decides everything, pilot only monitors</span>
          </div>
        </div>
      </div>

      {/* Level cards */}
      {LEVELS.map(level => {
        const isExpanded = expanded === level.id;
        return (
          <div key={level.id}
            className="rounded-lg border transition-all"
            style={{
              borderColor: isExpanded ? level.color + "40" : "rgba(63,63,70,0.3)",
              background: isExpanded ? level.color + "05" : "rgba(24,24,27,0.5)",
            }}
          >
            {/* Header — only this part toggles expand/collapse */}
            <div className="p-4 flex items-center gap-4 cursor-pointer"
              onClick={() => setExpanded(isExpanded ? 0 : level.id)}>
              <div className="w-10 h-10 rounded-lg flex items-center justify-center text-[18px] font-black shrink-0"
                style={{ background: level.color + "15", color: level.color }}>
                L{level.id}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="text-[13px] font-bold text-zinc-100">{level.name}</span>
                  <span className="text-[8px] px-1.5 py-0.5 rounded font-bold tracking-wider"
                    style={{ color: level.color, background: level.color + "15" }}>
                    {level.tag}
                  </span>
                </div>
                <div className="text-[9px] text-zinc-500 mt-0.5">{level.autonomy}</div>
              </div>
              <span className="text-[10px] text-zinc-700">{isExpanded ? "\u25BC" : "\u25B6"}</span>
            </div>

            {/* Expanded content */}
            {isExpanded && <LevelDetail level={level} />}
          </div>
        );
      })}
    </div>
  );
}

/** L2 focus areas — the key pillars to build for semi-autonomous flight */
const L2_FOCUS_AREAS = [
  {
    label: "Computer Vision",
    color: "#8b5cf6",
    icon: "CV",
    summary: "Detect a person from 15-30m altitude",
    details: [
      "YOLOv8n TFLite model (~4 FPS on Pi)",
      "Confidence threshold tuning (currently 0.4)",
      "Synthetic training data — may need real photos",
      "Max detection altitude unknown (need flight test)",
    ],
    status: "Tested on bench, untested from altitude",
  },
  {
    label: "Flight Algorithm",
    color: "#3b82f6",
    icon: "FA",
    summary: "Search, detect, centre, land autonomously",
    details: [
      "Lawnmower search pattern from any polygon",
      "GPS estimation: clustering + inverse variance weighting",
      "Centre on target using visual servo + GPS lock",
      "7.5m offset landing (avoid propwash on casualty)",
      "SSSI geofence avoidance (R02) — not yet implemented",
      "PLB redirect mid-search (R06) — not yet implemented",
    ],
    status: "Full flow tested in simulation (SITL)",
  },
  {
    label: "Hardware Integration",
    color: "#f97316",
    icon: "HW",
    summary: "Pi + Cube + Camera + GPS all talking",
    details: [
      "Pi -> mavproxy -> Cube (921600 baud UART)",
      "Camera: IMX296 global shutter, BGR output",
      "GPS: Here 3+ on CAN2 (needs outdoor 3D fix)",
      "Tarot payload release for first aid kit (R07)",
    ],
    status: "Bench tested, needs outdoor + flight test",
  },
  {
    label: "Ground Station",
    color: "#06b6d4",
    icon: "GS",
    summary: "Pilot sees video + commands from browser",
    details: [
      "pi_flight.py: MJPEG stream + GPS grid + buttons",
      "Browser dashboard at http://PI_IP:8090",
      "Commands: N=investigate, Y=confirm, I=interest, X=FP, L=land",
      "Mission Planner on TCP:5762 for safety monitoring",
    ],
    status: "Tested in sim, not yet tested on Pi",
  },
  {
    label: "Safety & Failsafes",
    color: "#ef4444",
    icon: "SF",
    summary: "RC kill switch + failsafes + geofence",
    details: [
      "RC STABILIZE = instant manual override (R09)",
      "Battery failsafe -> RTL",
      "RC loss failsafe -> RTL",
      "50m altitude limit (R04)",
      "SSSI geofence exclusion (R02)",
      "VLOS at all times (R09)",
    ],
    status: "Kill switch configured, geofence not yet",
  },
  {
    label: "Payload Delivery",
    color: "#f59e0b",
    icon: "PL",
    summary: "Drop first aid kit near target (R07)",
    details: [
      "Tarot servo-actuated payload release",
      "Triggered via MAVLink DO_SET_SERVO after landing",
      "R07 is a 'should' — bonus, not mandatory",
      "Needs mounting, wiring, and testing",
    ],
    status: "Hardware available, not yet integrated",
  },
];

// ── Status dot ──
const STATUS_DOT: Record<string, { color: string; icon: string }> = {
  done:    { color: "#22c55e", icon: "✓" },
  ready:   { color: "#3b82f6", icon: "●" },
  todo:    { color: "#6b7280", icon: "○" },
  blocked: { color: "#ef4444", icon: "✕" },
};

const CATEGORY_LABELS: Record<string, { label: string; color: string }> = {
  calibration: { label: "CAL", color: "#f97316" },
  accuracy:    { label: "ACC", color: "#06b6d4" },
  tuning:      { label: "TUNE", color: "#8b5cf6" },
  data:        { label: "DATA", color: "#f59e0b" },
};

// ── Critical path step card (no timeline, just the card) ──
function StepCard({ step, isExpanded, onToggle }: {
  step: SteppingStone; isExpanded: boolean; onToggle: () => void;
}) {
  const dot = STATUS_DOT[step.status];
  return (
    <div className="rounded-lg border cursor-pointer transition-all hover:brightness-110 p-2.5"
      onClick={onToggle}
      style={{
        borderColor: step.status === "done" ? "#22c55e25" : "#3f3f4630",
        background: step.status === "done" ? "#22c55e05" : "#18181b80",
      }}>
      <div className="flex items-center gap-2 mb-0.5">
        <span className="text-[10px] font-medium text-zinc-200">{step.name}</span>
        <span className="text-[7px] font-bold px-1 py-0.5 rounded" style={{ color: dot.color, background: dot.color + "15" }}>
          {step.status.toUpperCase()}
        </span>
      </div>
      <div className="text-[8px] text-zinc-500 leading-tight">{step.description}</div>

      {isExpanded && (
        <div className="mt-2 pt-2 border-t border-zinc-800/40 space-y-1.5">
          <div className="text-[8px]">
            <span className="text-emerald-500/70 font-bold">PROVES: </span>
            <span className="text-zinc-400">{step.proves}</span>
          </div>
          {step.script && (
            <div className="text-[8px]">
              <span className="text-cyan-500/70 font-bold">SCRIPT: </span>
              <span className="text-cyan-400/60 font-mono">{step.script}</span>
              {step.scriptArgs && <span className="text-zinc-600"> {step.scriptArgs}</span>}
            </div>
          )}
          {step.output && (
            <div className="text-[8px]">
              <span className="text-amber-500/70 font-bold">OUTPUT: </span>
              <span className="text-zinc-500">{step.output}</span>
            </div>
          )}
          {step.requires && step.requires.length > 0 && (
            <div className="text-[8px]">
              <span className="text-zinc-600 font-bold">AFTER: </span>
              <span className="text-zinc-600">
                {step.requires.map(r => {
                  const dep = L2_CRITICAL_PATH.find(s => s.id === r);
                  return dep ? dep.name : r;
                }).join(", ")}
              </span>
            </div>
          )}
          {step.ifScenarios && step.ifScenarios.length > 0 && (
            <div className="mt-2 pt-2 border-t border-zinc-800/30 space-y-1">
              <div className="text-[7px] font-bold text-amber-500/70 uppercase tracking-wider">Decision Points</div>
              {step.ifScenarios.map((scenario, i) => (
                <div key={i} className="flex gap-1.5 text-[8px]">
                  <span className="text-amber-500/60 shrink-0 mt-0.5">&#9670;</span>
                  <div>
                    <span className="text-amber-400/80 font-medium">{scenario.condition}</span>
                    <span className="text-zinc-500"> → {scenario.outcome}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ── Group steps by row, render parallel steps side by side ──
function CriticalPathRows({ expandedStep, onToggleStep }: {
  expandedStep: string | null; onToggleStep: (id: string) => void;
}) {
  // Group steps by row number
  const rows: Map<number, SteppingStone[]> = new Map();
  for (const step of L2_CRITICAL_PATH) {
    const existing = rows.get(step.row) || [];
    existing.push(step);
    rows.set(step.row, existing);
  }
  const sortedRows = [...rows.entries()].sort((a, b) => a[0] - b[0]);
  const totalRows = sortedRows.length;

  return (
    <div>
      {sortedRows.map(([rowNum, steps], rowIdx) => {
        const milestone = L2_MILESTONES.find(m => m.afterRow === rowNum);
        return (
          <div key={rowNum}>
            {/* Row with timeline dot + cards */}
            <div className="flex gap-3">
              {/* Timeline dot + line */}
              <div className="flex flex-col items-center shrink-0">
                <div className="w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold border-2"
                  style={{
                    borderColor: steps.every(s => s.status === "done") ? "#22c55e" : "#6b7280",
                    color: steps.every(s => s.status === "done") ? "#22c55e" : "#6b7280",
                    background: steps.every(s => s.status === "done") ? "#22c55e15" : "#6b728015",
                  }}>
                  {steps.every(s => s.status === "done") ? "\u2713" : rowNum}
                </div>
                {(rowIdx < totalRows - 1 || milestone) && (
                  <div className="w-[2px] flex-1 min-h-[16px] rounded-full"
                    style={{ background: steps.every(s => s.status === "done") ? "#22c55e40" : "#3f3f4620" }} />
                )}
              </div>

              {/* Step cards — side by side if parallel */}
              <div className={`flex-1 pb-3 min-w-0 ${steps.length > 1 ? "grid grid-cols-2 gap-2" : ""}`}>
                {steps.map(step => (
                  <StepCard
                    key={step.id} step={step}
                    isExpanded={expandedStep === step.id}
                    onToggle={() => onToggleStep(step.id)}
                  />
                ))}
              </div>
            </div>

            {/* Milestone marker after this row */}
            {milestone && (
              <div className="flex gap-3 my-1">
                <div className="flex flex-col items-center shrink-0">
                  <div className="w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold border-2"
                    style={{ borderColor: "#a855f7", color: "#a855f7", background: "#a855f715" }}>
                    &#9733;
                  </div>
                  {rowIdx < totalRows - 1 && (
                    <div className="w-[2px] flex-1 min-h-[8px] rounded-full" style={{ background: "#3f3f4620" }} />
                  )}
                </div>
                <div className="flex-1 min-w-0 pb-2">
                  <div className="flex items-center gap-3">
                    <div className="h-[2px] flex-1 rounded-full" style={{ background: "linear-gradient(90deg, #a855f7, #a855f740)" }} />
                    <span className="text-[9px] font-bold text-purple-400 uppercase tracking-wider whitespace-nowrap shrink-0">Milestone</span>
                    <div className="h-[2px] flex-1 rounded-full" style={{ background: "linear-gradient(90deg, #a855f740, #a855f7)" }} />
                  </div>
                  <div className="text-[10px] text-purple-300 font-medium mt-1 text-center">{milestone.label}</div>
                  <div className="text-[8px] text-zinc-500 mt-0.5 text-center">{milestone.detail}</div>
                </div>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

// ── Parallel task card ──
function ParallelTaskCard({ task, isExpanded, onToggle }: {
  task: ParallelTask; isExpanded: boolean; onToggle: () => void;
}) {
  const dot = STATUS_DOT[task.status];
  const cat = CATEGORY_LABELS[task.category];
  return (
    <div className="rounded-lg border cursor-pointer transition-all hover:brightness-110 p-2"
      onClick={onToggle}
      style={{
        borderColor: task.status === "done" ? "#22c55e25" : "#3f3f4630",
        background: task.status === "done" ? "#22c55e05" : "#18181b80",
      }}>
      <div className="flex items-center gap-1.5 mb-0.5">
        <span className="text-[7px] font-bold px-1 py-0.5 rounded" style={{ color: cat.color, background: cat.color + "15" }}>
          {cat.label}
        </span>
        <span className="text-[9px] font-medium text-zinc-300 flex-1 min-w-0 truncate">{task.name}</span>
        <span className="text-[9px] shrink-0" style={{ color: dot.color }}>{dot.icon}</span>
      </div>
      {isExpanded ? (
        <div className="space-y-1 mt-1.5">
          <div className="text-[8px] text-zinc-500 leading-tight">{task.description}</div>
          {task.script && (
            <div className="text-[8px]">
              <span className="text-cyan-500/70 font-bold">SCRIPT: </span>
              <span className="text-cyan-400/60 font-mono">{task.script}</span>
            </div>
          )}
          {task.output && (
            <div className="text-[8px]">
              <span className="text-amber-500/70 font-bold">OUTPUT: </span>
              <span className="text-zinc-500">{task.output}</span>
            </div>
          )}
          {task.dependsOn && (
            <div className="text-[8px]">
              <span className="text-zinc-600 font-bold">AFTER: </span>
              <span className="text-zinc-600">
                {L2_PARALLEL_TASKS.find(t => t.id === task.dependsOn)?.name || task.dependsOn}
              </span>
            </div>
          )}
        </div>
      ) : (
        <div className="text-[8px] text-zinc-600 truncate">{task.description}</div>
      )}
    </div>
  );
}

// ── L2 Stepping Stones section ──
function L2SteppingStones() {
  const [expandedStep, setExpandedStep] = useState<string | null>(null);
  const [expandedTask, setExpandedTask] = useState<string | null>(null);

  const toggleStep = (id: string) => setExpandedStep(prev => prev === id ? null : id);
  const toggleTask = (id: string) => setExpandedTask(prev => prev === id ? null : id);

  const doneCount = L2_CRITICAL_PATH.filter(s => s.status === "done").length;
  const parallelDone = L2_PARALLEL_TASKS.filter(t => t.status === "done").length;

  const categories = ["calibration", "accuracy", "tuning", "data"] as const;

  return (
    <div className="rounded-lg border border-blue-500/20 bg-blue-500/3 p-4 space-y-3">
      <div className="flex items-center justify-between">
        <div>
          <div className="text-[9px] text-blue-400 uppercase tracking-wider font-bold">Stepping Stones to Full L2 Mission</div>
          <div className="text-[8px] text-zinc-600 mt-0.5">Left: critical path (do in order). Right: benchmarks, calibration &amp; fine-tuning (do alongside).</div>
        </div>
        <div className="flex gap-3 text-[8px]">
          <span className="text-zinc-500">Critical: <span className="text-emerald-400 font-bold">{doneCount}/{L2_CRITICAL_PATH.length}</span></span>
          <span className="text-zinc-500">Parallel: <span className="text-emerald-400 font-bold">{parallelDone}/{L2_PARALLEL_TASKS.length}</span></span>
        </div>
      </div>

      <div className="grid grid-cols-[1fr_auto_280px] gap-0">
        {/* LEFT: Critical path (sequential) */}
        <div className="pr-4">
          <div className="text-[8px] font-bold text-zinc-500 tracking-wider uppercase mb-2 flex items-center gap-2">
            <div className="w-[14px] h-[1px] bg-blue-500/40" />
            Critical Path — Do In Order
            <div className="flex-1 h-[1px] bg-zinc-800/40" />
          </div>
          <CriticalPathRows expandedStep={expandedStep} onToggleStep={toggleStep} />
        </div>

        {/* DIVIDER: Vertical orange line */}
        <div className="w-[2px] rounded-full self-stretch" style={{ background: "linear-gradient(180deg, #f97316, #f9731640, #f9731610)" }} />

        {/* RIGHT: Parallel tasks (grouped by category) */}
        <div className="pl-4">
          <div className="text-[8px] font-bold text-zinc-500 tracking-wider uppercase mb-2 flex items-center gap-2">
            <div className="w-[14px] h-[1px] bg-purple-500/40" />
            Benchmarks &amp; Fine-Tuning
            <div className="flex-1 h-[1px] bg-zinc-800/40" />
          </div>
          <div className="space-y-3">
            {categories.map(cat => {
              const tasks = L2_PARALLEL_TASKS.filter(t => t.category === cat);
              const catInfo = CATEGORY_LABELS[cat];
              return (
                <div key={cat}>
                  <div className="text-[7px] font-bold tracking-wider uppercase mb-1" style={{ color: catInfo.color + "90" }}>
                    {catInfo.label === "CAL" ? "Calibration" : catInfo.label === "ACC" ? "Accuracy Measurements" : catInfo.label === "TUNE" ? "Parameter Tuning" : "Data Collection"}
                  </div>
                  <div className="space-y-1">
                    {tasks.map(task => (
                      <ParallelTaskCard
                        key={task.id} task={task}
                        isExpanded={expandedTask === task.id}
                        onToggle={() => toggleTask(task.id)}
                      />
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}

function LevelDetail({ level }: { level: MissionLevel }) {
  return (
    <div className="px-4 pb-4 space-y-4">
      {/* Description */}
      <div className="text-[10px] text-zinc-400 leading-relaxed">{level.description}</div>

      {/* L2 Focus Areas — only for the target level */}
      {level.id === 2 && (
        <div>
          <div className="text-[9px] text-blue-400 uppercase tracking-wider font-bold mb-2">Focus Areas — What We Need to Build</div>
          <div className="grid grid-cols-3 gap-2">
            {L2_FOCUS_AREAS.map(area => (
              <div key={area.label} className="rounded-lg p-3 border transition-all hover:brightness-110"
                style={{ background: area.color + "08", borderColor: area.color + "25" }}>
                <div className="flex items-center gap-2 mb-1.5">
                  <div className="w-6 h-6 rounded flex items-center justify-center text-[9px] font-black"
                    style={{ background: area.color + "20", color: area.color }}>
                    {area.icon}
                  </div>
                  <span className="text-[10px] font-bold text-zinc-200">{area.label}</span>
                </div>
                <div className="text-[9px] text-zinc-300 mb-2">{area.summary}</div>
                <div className="space-y-0.5 mb-2">
                  {area.details.map((d, i) => (
                    <div key={i} className="text-[8px] text-zinc-500 flex gap-1.5">
                      <span className="shrink-0" style={{ color: area.color + "80" }}>&bull;</span>
                      <span>{d}</span>
                    </div>
                  ))}
                </div>
                <div className="text-[7px] px-1.5 py-0.5 rounded inline-block"
                  style={{ color: area.color, background: area.color + "12" }}>
                  {area.status}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* L2 Stepping Stones — below focus areas */}
      {level.id === 2 && <L2SteppingStones />}

      {/* State flow */}
      <div className="px-3 py-2 rounded bg-zinc-900/80 border border-zinc-800/50">
        <div className="text-[8px] text-zinc-600 uppercase tracking-wider font-bold mb-1">State Flow</div>
        <div className="text-[9px] font-mono text-zinc-300">{level.stateFlow}</div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        {/* Drone actions */}
        <div>
          <div className="text-[9px] text-zinc-500 uppercase tracking-wider font-bold mb-2">Drone Does</div>
          <div className="space-y-1">
            {level.droneActions.map((a, i) => (
              <div key={i} className="flex items-start gap-2 text-[9px]">
                <span className="mt-0.5 shrink-0" style={{ color: level.color }}>{"\u2022"}</span>
                <span className="text-zinc-300">{a}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Pilot actions */}
        <div>
          <div className="text-[9px] text-zinc-500 uppercase tracking-wider font-bold mb-2">Pilot Does</div>
          <div className="space-y-1">
            {level.pilotActions.map((a, i) => (
              <div key={i} className="flex items-start gap-2 text-[9px]">
                <span className="text-zinc-600 mt-0.5 shrink-0">{"\u2022"}</span>
                <span className="text-zinc-400">{a}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Scripts */}
      <div>
        <div className="text-[9px] text-zinc-500 uppercase tracking-wider font-bold mb-2">Scripts</div>
        <div className="space-y-1">
          {level.scripts.map(s => (
            <div key={s.name} className="flex items-center gap-2 px-2 py-1.5 rounded bg-zinc-900/50 border border-zinc-800/50">
              <span className="text-[9px] text-cyan-500 font-mono shrink-0">{s.name}</span>
              <span className="text-[8px] text-zinc-600">{s.purpose}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        {/* What's working */}
        <div>
          <div className="text-[9px] text-green-500/80 uppercase tracking-wider font-bold mb-2">Working</div>
          <div className="space-y-0.5">
            {level.whatsWorking.map((w, i) => (
              <div key={i} className="flex items-start gap-2 text-[9px]">
                <span className="text-green-500 shrink-0 mt-0.5">{"\u2713"}</span>
                <span className="text-zinc-400">{w}</span>
              </div>
            ))}
          </div>
        </div>

        {/* What's missing */}
        <div>
          <div className="text-[9px] text-amber-500/80 uppercase tracking-wider font-bold mb-2">Missing</div>
          <div className="space-y-0.5">
            {level.whatsMissing.map((m, i) => (
              <div key={i} className="flex items-start gap-2 text-[9px]">
                <span className="text-amber-500 shrink-0 mt-0.5">{"\u25CB"}</span>
                <span className="text-zinc-500">{m}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
