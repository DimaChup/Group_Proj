/**
 * RoadmapTab — Three sub-views:
 *   "Flight Day 1" = 3-tier progressive plan with contingencies
 *   "Flight Timeline" = vertical timeline: prep -> day 1 -> analysis -> day 2 -> post
 *   "Technical Steps" = stepping stones by level (Foundation, L1, L2, L3)
 */
import { useState } from "react";
import { ROADMAP, LEVEL_COLORS, STATUS_COLORS } from "./mission-data";
import type { FlightTier, FlightStep, Measurement } from "./flight-day-types";
import { PRE_FLIGHT_PREP, PREFLIGHT_DIAGNOSTICS } from "./flight-day-prep";
import {
  TIER_1, TIER_2, TIER_3,
  TIME_SLOTS, WORST_CASES, CONFIG_UPDATES, FILES_TO_COLLECT,
  MEASUREMENTS, LOGGING_REQUIREMENTS,
} from "./flight-day-tiers";

type SubTab = "day1" | "timeline" | "steps";

const LEVEL_LABELS: Record<number, string> = {
  0: "Foundation",
  1: "L1 — Manual MVP",
  2: "L2 — Semi-Autonomous",
  3: "L3 — Full Autonomous",
};

const STATUS_LABELS: Record<string, string> = {
  done: "DONE",
  ready: "READY",
  todo: "TODO",
  blocked: "BLOCKED",
};

// ═══════════════════════════════════════════════════════════
// Flight Timeline Data (for the timeline sub-tab)
// ═══════════════════════════════════════════════════════════

interface TimelineItem {
  text: string;
  detail: string;
  status: "done" | "ready" | "todo";
  script?: string;
  owner?: string;
}

interface TimelinePhase {
  id: string;
  label: string;
  date: string;
  color: string;
  icon: string;
  summary: string;
  items: TimelineItem[];
}

const TIMELINE: TimelinePhase[] = [
  {
    id: "prep",
    label: "Pre-Flight Prep",
    date: "Before Flight Day 1",
    color: "#94a3b8",
    icon: "P",
    summary: "Everything that must be done before Fenswood Farm — see Flight Day 1 tab for full detail",
    items: [
      { text: "Push all code to GitHub", detail: "Laptop is source of truth. Pi pulls from git.", status: "done", owner: "Dima" },
      { text: "Prepare trained CV models", detail: "Custom dummy + COCO person + cone detector. All .tflite in models/.", status: "todo", owner: "Dima" },
      { text: "Test scripts in SIMULATION", detail: "pi_passive_flight.py, pi_flight.py, main.py — all must work in sim before flight day.", status: "todo", owner: "Dima + Robin" },
      { text: "RC + kill switch configured", detail: "Bind TX/RX, calibrate in MP, kill switch → STABILIZE.", status: "todo" },
      { text: "Charge all batteries + pack", detail: "3x LiPo, Pi power bank, RC TX, laptop, phone. Print checklist.", status: "todo" },
    ],
  },
  {
    id: "day1",
    label: "Flight Day 1",
    date: "TBD — First field session",
    color: "#22c55e",
    icon: "1",
    summary: "3-tier progressive plan — see Flight Day 1 tab for full detail with contingencies",
    items: [
      { text: "Tier 1: Prove it flies", detail: "MP AUTO waypoints, RC kill switch, GPS lock. No custom code.", status: "todo" },
      { text: "Tier 2: Pi commands + CV from altitude", detail: "Robin's waypoint script, Dima's passive CV flight. Altitude ladder test.", status: "todo" },
      { text: "Tier 3: Dashboard + investigate/land cycle", detail: "pi_flight.py full flow. N/Y/L commands. Landing accuracy measurement.", status: "todo" },
    ],
  },
  {
    id: "analysis",
    label: "Between Days — Analyse & Tune",
    date: "Between Flight Day 1 and 2",
    color: "#f59e0b",
    icon: "A",
    summary: "Use Day 1 data to tune parameters. Robin integrates CV with state machine.",
    items: [
      { text: "Max detection altitude", detail: "From passive CV logs: update TARGET_ALT in config.py.", status: "todo", owner: "Dima" },
      { text: "GPS drift + false positive rate", detail: "Compare logged GPS vs actual. Tune confidence threshold.", status: "todo", owner: "Dima" },
      { text: "CV → State Machine integration", detail: "Robin integrates CV detection output. State monitors image directory, reads metadata, shows in GUI.", status: "todo", owner: "Robin" },
      { text: "State machine robustness review", detail: "CRUCIAL: review all search phases, exit clauses, failsafe transitions. Identify faulty states.", status: "todo", owner: "Robin" },
      { text: "Model swap / retrain if needed", detail: "If custom model failed: try COCO. If time: retrain with real aerial photos from Day 1.", status: "todo", owner: "Dima" },
    ],
  },
  {
    id: "day2",
    label: "Flight Day 2",
    date: "TBD — Full mission attempts",
    color: "#3b82f6",
    icon: "2",
    summary: "L2 mission with CV integrated. Multiple attempts across 2 missions if needed.",
    items: [
      { text: "PLB plan + Phase 2 search", detail: "Demonstrate PLB redirect (R05). Phase 2 search pattern.", status: "todo", owner: "Robin", script: "state machine" },
      { text: "Dashboard flight", detail: "Full ground station. N/Y/I/X/L commands with CV integrated.", status: "todo", owner: "Dima", script: "pi_flight.py" },
      { text: "Full L2 semi-auto mission", detail: "Search → detect → confirm → centre → descend → land → payload → RTL.", status: "todo", script: "pi_flight.py + main.py" },
      { text: "Record results for report", detail: "GPS accuracy, detection stats, video recording. T/F for each test.", status: "todo" },
    ],
  },
  {
    id: "post",
    label: "Post-Flight",
    date: "After Flight Day 2",
    color: "#a855f7",
    icon: "R",
    summary: "Write up results, prepare deliverables D4-D7.",
    items: [
      { text: "Flight Readiness Review (D4)", detail: "Pre-flight safety case, test results, procedures. Week 10.", status: "todo" },
      { text: "Flight Test evidence (D5)", detail: "Video, GPS logs, detection logs, landing accuracy. Week 11-12.", status: "todo" },
      { text: "Final Report (D6)", detail: "Full technical report. 30% of grade. Week 13.", status: "todo" },
      { text: "Peer Assessment (D7)", detail: "Individual peer review. 12.5% of grade. Week 13.", status: "todo" },
    ],
  },
];

// ═══════════════════════════════════════════════════════════
// Main Component
// ═══════════════════════════════════════════════════════════

export default function RoadmapTab() {
  const [subTab, setSubTab] = useState<SubTab>("day1");

  return (
    <div className="flex-1 overflow-hidden min-w-0 flex flex-col">
      <div className="flex border-b border-zinc-800 px-6 shrink-0">
        {([
          { id: "day1" as SubTab, label: "Flight Day 1" },
          { id: "timeline" as SubTab, label: "Full Timeline" },
          { id: "steps" as SubTab, label: "Technical Steps" },
        ]).map(t => (
          <button key={t.id} onClick={() => setSubTab(t.id)}
            className={`px-4 py-2 text-[10px] transition-all border-b-2 ${
              subTab === t.id
                ? "text-white border-blue-500"
                : "text-zinc-500 border-transparent hover:text-zinc-300"
            }`}>
            {t.label}
          </button>
        ))}
      </div>

      <div className="flex-1 overflow-y-auto p-6">
        {subTab === "day1" && <FlightDay1View />}
        {subTab === "timeline" && <TimelineView />}
        {subTab === "steps" && <StepsView />}
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════
// Flight Day 1 — 3-Tier Progressive Plan
// ═══════════════════════════════════════════════════════════

function FlightDay1View() {
  const [openSections, setOpenSections] = useState<Set<string>>(new Set(["tiers"]));
  const toggle = (id: string) => {
    setOpenSections(prev => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id); else next.add(id);
      return next;
    });
  };
  const isOpen = (id: string) => openSections.has(id);

  const prepDone = PRE_FLIGHT_PREP.filter(t => t.status === "done").length;
  const prepTotal = PRE_FLIGHT_PREP.length;
  const prepCritical = PRE_FLIGHT_PREP.filter(t => t.critical && t.status === "todo").length;

  return (
    <div className="space-y-3">
      {/* Top row: strategy (2/3) + time schedule (1/3) */}
      <div className="grid grid-cols-3 gap-3">
        <div className="col-span-2 rounded-lg border border-zinc-800/50 bg-zinc-900/40 p-4">
          <div className="text-[9px] text-green-400 uppercase tracking-widest font-bold mb-1.5">Flight Day 1 — Progressive Plan</div>
          <div className="text-[9px] text-zinc-400 leading-relaxed mb-2">
            Three tiers of increasing ambition. Each tier is a <span className="text-zinc-200">self-contained success</span> — if we only complete Tier 1, we still have valuable data.
            Clear <span className="text-zinc-200">go/no-go gates</span> between tiers. <span className="text-zinc-200">Contingencies</span> at every step.
            <span className="text-zinc-200"> Day 1 = NO CV integration with state machine</span> — CV runs passively, Robin flies autonomously, they merge after.
          </div>
          <div className="flex gap-2">
            {[TIER_1, TIER_2, TIER_3].map(t => (
              <div key={t.id} className="flex items-center gap-1.5 px-2 py-1 rounded text-[8px]"
                style={{ background: t.color + "10", color: t.color }}>
                <span className="font-bold">{t.title}</span>
                <span className="text-zinc-600">{t.time}</span>
                <span className="text-zinc-700">{t.batteries}</span>
              </div>
            ))}
          </div>
          <div className="mt-2 text-[8px] text-zinc-500 leading-relaxed font-mono px-2 py-1.5 rounded bg-zinc-900/60 border border-zinc-800/30">
            Robin: IDLE → Setup Mission → PRE_AUTO_CHECK → Generate Pattern → SEARCH (Phase 1 → 2)
          </div>
          <div className="flex gap-4 mt-1.5 text-[8px]">
            <span className="text-purple-400/70">Dima: CV models, detection, GPS estimation, ground station</span>
            <span className="text-purple-400/70">Robin: State machine, flight control, GUIDED commands</span>
          </div>
        </div>

        {/* Time schedule compact */}
        <div className="rounded-lg border border-zinc-800/50 bg-zinc-900/40 p-3 overflow-y-auto max-h-[250px]">
          <div className="text-[9px] text-zinc-300 font-bold mb-2">Time Schedule</div>
          <div className="space-y-0.5">
            {TIME_SLOTS.map((slot, i) => {
              const tierColor = slot.tier === "1" ? TIER_1.color : slot.tier === "2" ? TIER_2.color : slot.tier === "3" ? TIER_3.color : slot.tier === "gate" ? "#06b6d4" : "#6b7280";
              const isGate = slot.tier === "gate";
              return (
                <div key={i} className={`flex items-start gap-1.5 px-1.5 py-0.5 rounded text-[7px] ${isGate ? "border border-cyan-500/20 bg-cyan-500/5" : ""}`}>
                  <span className="text-zinc-600 font-mono shrink-0 w-16">{slot.time}</span>
                  <div className="w-1 h-1 rounded-full shrink-0 mt-1" style={{ background: tierColor }} />
                  <span className={`leading-tight ${isGate ? "text-cyan-400 font-bold" : "text-zinc-500"}`}>{slot.activity}</span>
                </div>
              );
            })}
          </div>
          <div className="mt-1 text-[7px] text-zinc-600">Each LiPo ≈ 10-15 min flight.</div>
        </div>
      </div>

      {/* Pre-flight preparation — 2-column compact */}
      <div className="rounded-lg border border-zinc-800/50 overflow-hidden">
        <button onClick={() => toggle("prep")} className="w-full flex items-center gap-3 px-4 py-2.5 hover:bg-zinc-800/20 transition-all text-left">
          <span className="text-[9px] text-zinc-600">{isOpen("prep") ? "▼" : "▶"}</span>
          <span className="text-[10px] text-amber-400 font-bold">Pre-Flight Day Preparation</span>
          <span className="text-[8px] text-zinc-500">{prepDone}/{prepTotal} done</span>
          {prepCritical > 0 && <span className="text-[7px] text-red-400 font-bold">{prepCritical} critical remaining</span>}
        </button>
        {isOpen("prep") && (
          <div className="px-4 pb-3">
            <div className="text-[8px] text-zinc-500 mb-2">Must be done <span className="text-zinc-300">before leaving for Fenswood</span>. Failure = wasted day.</div>
            <div className="grid grid-cols-2 gap-1.5">
              {PRE_FLIGHT_PREP.map(t => {
                const isDone = t.status === "done";
                return (
                  <div key={t.id} className={`flex items-start gap-2 px-2.5 py-1.5 rounded border ${isDone ? "border-green-500/10 bg-green-500/5" : t.critical ? "border-red-500/10 bg-red-500/3" : "border-zinc-800/30 bg-zinc-900/30"}`}>
                    <div className={`w-1.5 h-1.5 rounded-full mt-1 shrink-0 ${isDone ? "bg-green-500" : t.critical ? "bg-red-400" : "bg-zinc-600"}`} />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-1.5">
                        <span className="text-[8px] text-zinc-200 font-medium">{t.task}</span>
                        {t.critical && !isDone && <span className="text-[6px] text-red-400 font-bold">CRIT</span>}
                        {isDone && <span className="text-[6px] text-green-500 font-bold">DONE</span>}
                        {t.owner && <span className="text-[6px] text-purple-400/60">{t.owner}</span>}
                      </div>
                      {t.command && <div className="text-[7px] text-cyan-500/70 font-mono mt-0.5 truncate">{t.command}</div>}
                      {t.notes && <div className="text-[7px] text-zinc-500 mt-0.5 leading-tight">{t.notes}</div>}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* Preflight Diagnostics — compact table */}
      <div className="rounded-lg border border-zinc-800/50 overflow-hidden">
        <button onClick={() => toggle("diag")} className="w-full flex items-center gap-3 px-4 py-2.5 hover:bg-zinc-800/20 transition-all text-left">
          <span className="text-[9px] text-zinc-600">{isOpen("diag") ? "▼" : "▶"}</span>
          <span className="text-[10px] text-cyan-400 font-bold">Preflight Diagnostics</span>
          <span className="text-[8px] text-zinc-500">{PREFLIGHT_DIAGNOSTICS.length} checks</span>
          <span className="text-[7px] text-zinc-600">run on field before flying</span>
        </button>
        {isOpen("diag") && (
          <div className="px-4 pb-3">
            <DiagnosticsTable />
          </div>
        )}
      </div>

      {/* Scientific Measurements — what to measure */}
      <div className="rounded-lg border border-zinc-800/50 overflow-hidden">
        <button onClick={() => toggle("measurements")} className="w-full flex items-center gap-3 px-4 py-2.5 hover:bg-zinc-800/20 transition-all text-left">
          <span className="text-[9px] text-zinc-600">{isOpen("measurements") ? "▼" : "▶"}</span>
          <span className="text-[10px] text-purple-400 font-bold">Scientific Measurements</span>
          <span className="text-[8px] text-zinc-500">{MEASUREMENTS.length} metrics to log</span>
          <span className="text-[7px] text-zinc-600">altitude, speed, GPS, detection, accuracy</span>
        </button>
        {isOpen("measurements") && (
          <div className="px-4 pb-3">
            <div className="text-[8px] text-zinc-500 mb-2">Every test must produce <span className="text-zinc-300">measurable data</span>. Log everything — post-flight analysis depends on it.</div>
            <MeasurementsGrid />
          </div>
        )}
      </div>

      {/* 3-Tier columns */}
      <div className="rounded-lg border border-zinc-800/50 overflow-hidden">
        <button onClick={() => toggle("tiers")} className="w-full flex items-center gap-3 px-4 py-2.5 hover:bg-zinc-800/20 transition-all text-left">
          <span className="text-[9px] text-zinc-600">{isOpen("tiers") ? "▼" : "▶"}</span>
          <span className="text-[10px] text-green-400 font-bold">Three Tiers — On the Day</span>
          <span className="text-[8px] text-zinc-500">progressively more ambitious</span>
        </button>
        {isOpen("tiers") && (
          <div className="px-4 pb-4">
            <div className="grid grid-cols-3 gap-3">
              <TierColumn tier={TIER_1} />
              <TierColumn tier={TIER_2} />
              <TierColumn tier={TIER_3} />
            </div>
          </div>
        )}
      </div>

      {/* Bottom row: gates + worst cases + config — 3 columns */}
      <div className="grid grid-cols-3 gap-3">
        {/* Decision gates */}
        <div className="rounded-lg border border-zinc-800/50 overflow-hidden">
          <button onClick={() => toggle("gates")} className="w-full flex items-center gap-2 px-3 py-2.5 hover:bg-zinc-800/20 transition-all text-left">
            <span className="text-[9px] text-zinc-600">{isOpen("gates") ? "▼" : "▶"}</span>
            <span className="text-[9px] text-cyan-400 font-bold">Decision Gates</span>
          </button>
          {isOpen("gates") && (
            <div className="px-3 pb-3 space-y-2">
              {[TIER_1, TIER_2].map(t => t.gate && (
                <div key={t.id} className="rounded p-2 border" style={{ borderColor: t.color + "20", background: t.color + "05" }}>
                  <div className="text-[8px] font-bold mb-1" style={{ color: t.color }}>
                    {t.title} → {t === TIER_1 ? TIER_2.title : TIER_3.title}
                  </div>
                  <div className="text-[8px] text-zinc-300 mb-1.5">{t.gate.question}</div>
                  <div className="space-y-0.5">
                    <div className="flex gap-1.5 text-[7px]">
                      <span className="text-green-500 font-bold shrink-0 w-7">GO</span>
                      <span className="text-zinc-400">{t.gate.go}</span>
                    </div>
                    <div className="flex gap-1.5 text-[7px]">
                      <span className="text-red-400 font-bold shrink-0 w-7">STOP</span>
                      <span className="text-zinc-400">{t.gate.noGo}</span>
                    </div>
                    {t.gate.partialGo && (
                      <div className="flex gap-1.5 text-[7px]">
                        <span className="text-amber-400 font-bold shrink-0 w-7">PART</span>
                        <span className="text-zinc-400">{t.gate.partialGo}</span>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Worst cases */}
        <div className="rounded-lg border border-zinc-800/50 overflow-hidden">
          <button onClick={() => toggle("worst")} className="w-full flex items-center gap-2 px-3 py-2.5 hover:bg-zinc-800/20 transition-all text-left">
            <span className="text-[9px] text-zinc-600">{isOpen("worst") ? "▼" : "▶"}</span>
            <span className="text-[9px] text-red-400 font-bold">Worst Cases</span>
          </button>
          {isOpen("worst") && (
            <div className="px-3 pb-3 space-y-1">
              {WORST_CASES.map((wc, i) => (
                <div key={i} className="rounded px-2 py-1 bg-zinc-900/50 border border-zinc-800/30">
                  <div className="text-[7px] text-red-400/80 font-bold">{wc.scenario}</div>
                  <div className="text-[7px] text-zinc-500 mt-0.5 leading-tight">{wc.response}</div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Config updates + files to collect */}
        <div className="space-y-3">
          <div className="rounded-lg border border-zinc-800/50 overflow-hidden">
            <button onClick={() => toggle("config")} className="w-full flex items-center gap-2 px-3 py-2.5 hover:bg-zinc-800/20 transition-all text-left">
              <span className="text-[9px] text-zinc-600">{isOpen("config") ? "▼" : "▶"}</span>
              <span className="text-[9px] text-amber-400 font-bold">Config Updates After</span>
            </button>
            {isOpen("config") && (
              <div className="px-3 pb-3 space-y-0.5">
                {CONFIG_UPDATES.map(c => (
                  <div key={c.param} className="flex items-baseline gap-1.5 text-[7px] px-1.5 py-0.5 rounded bg-zinc-900/50 border border-zinc-800/30">
                    <span className="text-cyan-500 font-mono shrink-0">{c.param}</span>
                    <span className="text-zinc-600">{c.current} →</span>
                    <span className="text-zinc-400 truncate">{c.updateTo}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
          <div className="rounded-lg border border-zinc-800/50 overflow-hidden">
            <button onClick={() => toggle("files")} className="w-full flex items-center gap-2 px-3 py-2.5 hover:bg-zinc-800/20 transition-all text-left">
              <span className="text-[9px] text-zinc-600">{isOpen("files") ? "▼" : "▶"}</span>
              <span className="text-[9px] text-green-400 font-bold">Files to Collect</span>
            </button>
            {isOpen("files") && (
              <div className="px-3 pb-3 space-y-0.5">
                {FILES_TO_COLLECT.map(f => (
                  <div key={f.file} className="px-1.5 py-0.5 rounded bg-zinc-900/50 border border-zinc-800/30">
                    <div className="text-[7px] text-cyan-500/70 font-mono">{f.file}</div>
                    <div className="text-[7px] text-zinc-500">{f.purpose}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Post-flight logging requirements */}
      <div className="rounded-lg border border-zinc-800/50 overflow-hidden">
        <button onClick={() => toggle("logging")} className="w-full flex items-center gap-3 px-4 py-2.5 hover:bg-zinc-800/20 transition-all text-left">
          <span className="text-[9px] text-zinc-600">{isOpen("logging") ? "▼" : "▶"}</span>
          <span className="text-[10px] text-blue-400 font-bold">Post-Flight Data & Analysis</span>
          <span className="text-[8px] text-zinc-500">{LOGGING_REQUIREMENTS.length} data sources</span>
        </button>
        {isOpen("logging") && (
          <div className="px-4 pb-3">
            <div className="text-[8px] text-zinc-500 mb-2">Everything we need to <span className="text-zinc-300">collect and analyse</span> after flying. Scientific approach = proper logging.</div>
            <div className="grid grid-cols-2 gap-1.5">
              {LOGGING_REQUIREMENTS.map(l => (
                <div key={l.id} className="rounded px-2.5 py-1.5 bg-zinc-900/50 border border-zinc-800/20">
                  <div className="text-[8px] text-zinc-200 font-medium">{l.what}</div>
                  <div className="text-[7px] text-cyan-500/60 font-mono mt-0.5">{l.source}</div>
                  <div className="text-[7px] text-zinc-600 mt-0.5">{l.format}</div>
                  <div className="text-[7px] text-zinc-500 mt-0.5 leading-tight"><span className="text-zinc-600">Analysis:</span> {l.analysis}</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════
// Diagnostics Table Component
// ═══════════════════════════════════════════════════════════

function DiagnosticsTable() {
  const [expandedDiag, setExpandedDiag] = useState<string | null>(null);

  const severityColor = (s: string) => s === "blocking" ? "#ef4444" : s === "warning" ? "#f59e0b" : "#6b7280";

  return (
    <div className="grid grid-cols-2 gap-x-3 gap-y-1">
      {PREFLIGHT_DIAGNOSTICS.map(d => (
        <div key={d.id} className="rounded border border-zinc-800/20 bg-zinc-900/30 overflow-hidden">
          <button onClick={() => setExpandedDiag(expandedDiag === d.id ? null : d.id)}
            className="w-full flex items-start gap-2 px-2 py-1.5 hover:bg-zinc-800/20 transition-all text-left">
            <div className="w-1.5 h-1.5 rounded-full mt-1 shrink-0" style={{ background: severityColor(d.severity) }} />
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-1.5">
                <span className="text-[8px] text-zinc-200 font-medium">{d.system}</span>
                <span className="text-[6px] font-bold uppercase ml-auto shrink-0" style={{ color: severityColor(d.severity) }}>
                  {d.severity === "blocking" ? "BLOCK" : d.severity === "warning" ? "WARN" : "INFO"}
                </span>
              </div>
              <div className="text-[7px] text-cyan-500/60 font-mono truncate mt-0.5">{d.command}</div>
              <div className="text-[7px] text-zinc-500 leading-tight mt-0.5">{d.expect}</div>
            </div>
          </button>
          {expandedDiag === d.id && (
            <div className="px-2 pb-1.5 mx-2 mb-1 rounded bg-zinc-950/40 border border-zinc-800/20">
              <div className="text-[7px] text-red-400/70 font-bold mb-0.5">If it fails:</div>
              {d.failSteps.map((step, i) => (
                <div key={i} className="text-[7px] text-zinc-500 flex gap-1.5 leading-tight">
                  <span className="text-zinc-600 shrink-0">{i + 1}.</span>
                  <span>{step}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════
// Measurements Grid Component
// ═══════════════════════════════════════════════════════════

const CATEGORY_META: Record<string, { label: string; color: string }> = {
  calibration: { label: "Calibration", color: "#f59e0b" },
  performance: { label: "Performance", color: "#3b82f6" },
  detection: { label: "Detection", color: "#22c55e" },
  accuracy: { label: "Accuracy", color: "#a855f7" },
};

function MeasurementsGrid() {
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const categories = ["calibration", "performance", "detection", "accuracy"] as const;

  return (
    <div className="grid grid-cols-2 gap-3">
      {categories.map(cat => {
        const meta = CATEGORY_META[cat];
        const items = MEASUREMENTS.filter(m => m.category === cat);
        return (
          <div key={cat} className="rounded-lg border p-2.5" style={{ borderColor: meta.color + "20", background: meta.color + "03" }}>
            <div className="text-[8px] font-bold mb-1.5 uppercase tracking-wider" style={{ color: meta.color }}>{meta.label}</div>
            <div className="space-y-1">
              {items.map(m => (
                <div key={m.id} className="rounded px-2 py-1 bg-zinc-900/50 border border-zinc-800/20 hover:bg-zinc-800/20 transition-all cursor-pointer"
                  onClick={() => setExpandedId(expandedId === m.id ? null : m.id)}>
                  <div className="flex items-center gap-1.5">
                    <span className="text-[8px] text-zinc-200">{m.metric}</span>
                    {m.currentValue && <span className="text-[7px] text-cyan-500/70 font-mono ml-auto">{m.currentValue}</span>}
                    <span className="text-[7px] text-zinc-600">{m.unit}</span>
                  </div>
                  {expandedId === m.id && (
                    <div className="mt-1 space-y-0.5">
                      <div className="text-[7px] text-zinc-500"><span className="text-zinc-600">How:</span> {m.how}</div>
                      {m.notes && <div className="text-[7px] text-zinc-500 leading-tight">{m.notes}</div>}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════
// Tier Column Component
// ═══════════════════════════════════════════════════════════

function TierColumn({ tier }: { tier: FlightTier }) {
  const [expandedPhase, setExpandedPhase] = useState<string | null>(tier.phases[0]?.id || null);

  return (
    <div className="rounded-lg border p-3 space-y-2"
      style={{ borderColor: tier.color + "25", background: tier.color + "03" }}>
      {/* Header */}
      <div>
        <div className="flex items-center gap-2 mb-1">
          <div className="w-5 h-5 rounded flex items-center justify-center text-[8px] font-black"
            style={{ background: tier.color + "20", color: tier.color }}>
            {tier.id === "tier1" ? "1" : tier.id === "tier2" ? "2" : "3"}
          </div>
          <span className="text-[10px] font-bold" style={{ color: tier.color }}>{tier.title}</span>
        </div>
        <div className="text-[8px] text-zinc-400 leading-relaxed">{tier.subtitle}</div>
        <div className="flex gap-2 mt-1 text-[7px]">
          <span className="text-zinc-600">{tier.time}</span>
          <span className="text-zinc-700">{tier.batteries}</span>
        </div>
      </div>

      {/* Entry requirements */}
      <div className="px-2 py-1.5 rounded bg-zinc-900/60 border border-zinc-800/30">
        <div className="text-[7px] text-zinc-600 uppercase tracking-wider font-bold mb-0.5">Entry Requirements</div>
        {tier.entryRequirements.map((r, i) => (
          <div key={i} className="text-[7px] text-zinc-500 flex gap-1">
            <span className="text-zinc-700 shrink-0">&bull;</span>
            <span>{r}</span>
          </div>
        ))}
      </div>

      {/* Phases */}
      {tier.phases.map(phase => {
        const isOpen = expandedPhase === phase.id;
        return (
          <div key={phase.id} className="rounded border border-zinc-800/30 overflow-hidden">
            <button onClick={() => setExpandedPhase(isOpen ? null : phase.id)}
              className="w-full flex items-center gap-1.5 px-2 py-1.5 hover:bg-zinc-800/20 transition-all text-left">
              <span className="text-[7px] text-zinc-700">{isOpen ? "\u25BC" : "\u25B6"}</span>
              <span className="text-[8px] text-zinc-200 font-medium">{phase.title}</span>
              {phase.subtitle && <span className="text-[7px] text-zinc-600 ml-auto">{phase.subtitle}</span>}
            </button>
            {isOpen && (
              <div className="px-2 pb-2 space-y-1">
                {phase.steps.map(step => (
                  <StepCard key={step.id} step={step} tierColor={tier.color} />
                ))}
              </div>
            )}
          </div>
        );
      })}

      {/* Contingencies */}
      <div className="px-2 py-1.5 rounded bg-zinc-900/60 border border-zinc-800/30">
        <div className="text-[7px] text-red-400/70 uppercase tracking-wider font-bold mb-0.5">If Things Go Wrong</div>
        {Object.entries(tier.contingencies).map(([k, v]) => (
          <div key={k} className="mb-1">
            <div className="text-[7px] text-amber-400/70 font-bold">{k}</div>
            <div className="text-[7px] text-zinc-600 leading-relaxed">{v}</div>
          </div>
        ))}
      </div>

      {/* Data collected */}
      <div className="px-2 py-1.5 rounded bg-zinc-900/60 border border-zinc-800/30">
        <div className="text-[7px] text-green-500/70 uppercase tracking-wider font-bold mb-0.5">Data We Get</div>
        {tier.dataCollected.map((d, i) => (
          <div key={i} className="text-[7px] text-zinc-500 flex gap-1">
            <span className="text-green-500/50 shrink-0">&bull;</span>
            <span>{d}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function StepCard({ step, tierColor }: { step: FlightStep; tierColor: string }) {
  const [open, setOpen] = useState(false);
  const hasDetail = step.how || step.command || step.verify || step.contingency || step.data || step.notes || step.detailedSteps || step.expectedOutput;

  return (
    <div className="rounded px-2 py-1.5 border border-zinc-800/20 bg-zinc-900/40 hover:bg-zinc-800/20 transition-all">
      <div className={`flex items-start gap-1.5 ${hasDetail ? "cursor-pointer" : ""}`}
        onClick={() => hasDetail && setOpen(!open)}>
        <div className="w-1.5 h-1.5 rounded-full mt-1 shrink-0" style={{ background: tierColor + "60" }} />
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-1">
            <span className="text-[8px] text-zinc-200">{step.task}</span>
            {step.duration && <span className="text-[6px] text-zinc-600 shrink-0">~{step.duration}</span>}
            {step.owner && <span className="text-[6px] text-purple-400/50 ml-auto shrink-0">{step.owner}</span>}
          </div>
        </div>
        {hasDetail && <span className="text-[6px] text-zinc-700 shrink-0 mt-0.5">{open ? "\u25BC" : "\u25B6"}</span>}
      </div>
      {open && (
        <div className="mt-1.5 ml-3 space-y-1.5">
          {/* Why / overview */}
          {step.how && <div className="text-[7px] text-zinc-400 leading-relaxed">{step.how}</div>}

          {/* Command to run */}
          {step.command && (
            <div className="rounded px-2 py-1 bg-zinc-950/60 border border-zinc-800/30">
              <div className="text-[6px] text-zinc-600 uppercase tracking-wider mb-0.5">Run</div>
              <div className="text-[7px] text-cyan-400/80 font-mono leading-relaxed whitespace-pre-wrap">{step.command}</div>
            </div>
          )}

          {/* Detailed sub-steps (the recipe) */}
          {step.detailedSteps && step.detailedSteps.length > 0 && (
            <div className="rounded px-2 py-1.5 bg-zinc-950/40 border border-zinc-800/20">
              <div className="text-[6px] text-zinc-500 uppercase tracking-wider mb-1 font-bold">Step by step</div>
              {step.detailedSteps.map((s, i) => (
                <div key={i} className="flex gap-1.5 text-[7px] leading-relaxed mb-0.5">
                  <span className="text-zinc-600 shrink-0 w-3 text-right font-mono">{i + 1}.</span>
                  <span className="text-zinc-400">{s}</span>
                </div>
              ))}
            </div>
          )}

          {/* Expected output */}
          {step.expectedOutput && (
            <div className="rounded px-2 py-1 bg-green-950/20 border border-green-800/20">
              <div className="text-[6px] text-green-600 uppercase tracking-wider mb-0.5">Expected output</div>
              <div className="text-[7px] text-green-400/70 font-mono leading-relaxed whitespace-pre-wrap">{step.expectedOutput}</div>
            </div>
          )}

          {/* Verify */}
          {step.verify && (
            <div className="text-[7px] text-green-500/60 flex gap-1">
              <span className="text-green-600/60 shrink-0">&#x2713;</span>
              <span>{step.verify}</span>
            </div>
          )}

          {/* Notes */}
          {step.notes && <div className="text-[7px] text-zinc-500 leading-relaxed">{step.notes}</div>}

          {/* If it fails */}
          {step.contingency && (
            <div className="rounded px-2 py-1 bg-amber-950/10 border border-amber-800/15">
              <div className="text-[6px] text-amber-600 uppercase tracking-wider mb-0.5">If it fails</div>
              <div className="text-[7px] text-amber-400/60 leading-relaxed">{step.contingency}</div>
            </div>
          )}

          {/* Data to record */}
          {step.data && step.data.length > 0 && (
            <div className="rounded px-2 py-1 bg-zinc-950/40 border border-zinc-800/20">
              <div className="text-[6px] text-zinc-500 uppercase tracking-wider mb-0.5">Record</div>
              {step.data.map((d, i) => (
                <div key={i} className="text-[7px] text-zinc-500 flex gap-1.5 leading-tight">
                  <span className="text-zinc-600 shrink-0">&#x25A2;</span>
                  <span>{d}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════
// Flight Timeline View (simplified overview)
// ═══════════════════════════════════════════════════════════

function TimelineView() {
  const [expandedPhase, setExpandedPhase] = useState<string | null>("day1");

  const totalItems = TIMELINE.reduce((sum, p) => sum + p.items.length, 0);
  const doneItems = TIMELINE.reduce((sum, p) => sum + p.items.filter(i => i.status === "done").length, 0);

  return (
    <div className="space-y-0 max-w-3xl">
      {/* Team strategy note */}
      <div className="rounded-lg border border-zinc-800/50 bg-zinc-900/40 p-4 mb-4">
        <div className="text-[9px] text-green-400 uppercase tracking-widest font-bold mb-1.5">Team Flight Strategy</div>
        <div className="text-[9px] text-zinc-400 leading-relaxed mb-2">
          <span className="text-zinc-200">Day 1: NO CV integration with state machine.</span> CV runs passively (detection + geotagged images only).
          Robin's state machine handles flight autonomy independently. CV integration happens <span className="text-zinc-200">between days</span>.
        </div>
        <div className="text-[8px] text-zinc-500 leading-relaxed font-mono px-2 py-1.5 rounded bg-zinc-900/60 border border-zinc-800/30">
          Robin: IDLE → Setup Mission → PRE_AUTO_CHECK → Generate Pattern → [Abort | Start] → Upload Mission → SEARCH (Phase 1 → 2)
        </div>
        <div className="flex gap-4 mt-2 text-[8px]">
          <span className="text-purple-400/70">Dima: CV models, detection, GPS estimation</span>
          <span className="text-purple-400/70">Robin: State machine, flight control, GUI</span>
        </div>
      </div>

      {/* Progress */}
      <div className="flex items-center gap-3 mb-5">
        <div className="flex-1 h-1.5 bg-zinc-800 rounded-full overflow-hidden">
          <div className="h-full rounded-full bg-green-500 transition-all"
            style={{ width: `${totalItems > 0 ? (doneItems / totalItems) * 100 : 0}%` }} />
        </div>
        <span className="text-[10px] text-zinc-500 shrink-0">{doneItems}/{totalItems} tasks</span>
      </div>

      {/* Vertical timeline */}
      {TIMELINE.map((phase, phaseIdx) => {
        const isExpanded = expandedPhase === phase.id;
        const phaseDone = phase.items.filter(i => i.status === "done").length;
        const isLast = phaseIdx === TIMELINE.length - 1;

        return (
          <div key={phase.id} className="flex gap-4">
            <div className="flex flex-col items-center shrink-0 w-8">
              <div className="w-8 h-8 rounded-lg flex items-center justify-center text-[13px] font-black shrink-0 cursor-pointer hover:brightness-125 transition-all"
                style={{ background: phase.color + "20", color: phase.color }}
                onClick={() => setExpandedPhase(isExpanded ? null : phase.id)}>
                {phase.icon}
              </div>
              {!isLast && (
                <div className="w-0.5 flex-1 min-h-[16px]"
                  style={{ background: `linear-gradient(to bottom, ${phase.color}40, ${TIMELINE[phaseIdx + 1]?.color || phase.color}40)` }} />
              )}
            </div>

            <div className={`flex-1 min-w-0 ${isLast ? "" : "pb-4"}`}>
              <button onClick={() => setExpandedPhase(isExpanded ? null : phase.id)}
                className="w-full text-left">
                <div className="flex items-center gap-2">
                  <span className="text-[12px] font-bold" style={{ color: phase.color }}>{phase.label}</span>
                  <span className="text-[8px] text-zinc-600">{phase.date}</span>
                  <span className="text-[7px] ml-auto" style={{ color: phaseDone === phase.items.length && phaseDone > 0 ? "#22c55e" : "#6b7280" }}>
                    {phaseDone}/{phase.items.length}
                  </span>
                  <span className="text-[9px] text-zinc-700">{isExpanded ? "\u25BC" : "\u25B6"}</span>
                </div>
                <div className="text-[9px] text-zinc-500 mt-0.5">{phase.summary}</div>
              </button>

              {isExpanded && (
                phase.id === "day1" ? (
                  <div className="mt-3 -ml-12">
                    <FlightDay1View />
                  </div>
                ) : (
                  <div className="mt-3 space-y-1.5">
                    {phase.items.map((item, i) => {
                      const sc = STATUS_COLORS[item.status] || STATUS_COLORS.todo;
                      return (
                        <div key={i} className="rounded-lg px-3 py-2.5 border transition-all"
                          style={{ background: phase.color + "05", borderColor: phase.color + "15" }}>
                          <div className="flex items-start gap-2">
                            <div className="w-2 h-2 rounded-full mt-1 shrink-0" style={{ background: sc.color }} />
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2">
                                <span className="text-[10px] text-zinc-200 font-medium">{item.text}</span>
                                <span className="text-[7px] px-1 rounded font-bold"
                                  style={{ color: sc.color, background: sc.bg }}>
                                  {item.status.toUpperCase()}
                                </span>
                              </div>
                              <div className="text-[8px] text-zinc-500 mt-1 leading-relaxed">{item.detail}</div>
                              {item.script && (
                                <div className="text-[8px] text-cyan-500/70 font-mono mt-1">{item.script}</div>
                              )}
                              {item.owner && (
                                <div className="text-[7px] text-purple-400/60 mt-0.5">{item.owner}</div>
                              )}
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════
// Steps View (original roadmap)
// ═══════════════════════════════════════════════════════════

function StepsView() {
  const levels = [0, 1, 2, 3];
  const totalDone = ROADMAP.filter(s => s.status === "done").length;
  const total = ROADMAP.length;

  return (
    <div className="space-y-5">
      <div className="flex items-center gap-3">
        <div className="flex-1 h-1.5 bg-zinc-800 rounded-full overflow-hidden">
          <div className="h-full rounded-full bg-green-500 transition-all"
            style={{ width: `${total > 0 ? (totalDone / total) * 100 : 0}%` }} />
        </div>
        <span className="text-[10px] text-zinc-500 shrink-0">{totalDone}/{total} steps done</span>
      </div>

      {levels.map(levelId => {
        const steps = ROADMAP.filter(s => s.level === levelId);
        const done = steps.filter(s => s.status === "done").length;
        const color = LEVEL_COLORS[levelId];

        return (
          <div key={levelId}>
            <div className="flex items-center gap-2 mb-2">
              <div className="w-1 h-4 rounded-full" style={{ background: color }} />
              <span className="text-[11px] font-bold" style={{ color }}>{LEVEL_LABELS[levelId]}</span>
              <span className="text-[8px] text-zinc-600">{done}/{steps.length}</span>
            </div>

            <div className="space-y-1 ml-3">
              {steps.map(step => {
                const sc = STATUS_COLORS[step.status];
                return (
                  <div key={step.id} className="flex items-start gap-3 px-3 py-2 rounded hover:bg-zinc-800/30 transition-all">
                    <div className="w-2 h-2 rounded-full mt-1 shrink-0" style={{ background: sc.color }} />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="text-[10px] text-zinc-200">{step.name}</span>
                        <span className="text-[7px] px-1 rounded font-bold"
                          style={{ color: sc.color, background: sc.bg }}>
                          {STATUS_LABELS[step.status]}
                        </span>
                      </div>
                      <div className="text-[8px] text-zinc-500 mt-0.5">{step.description}</div>
                      {step.depends && step.depends.length > 0 && (
                        <div className="text-[7px] text-zinc-700 mt-0.5">
                          depends on: {step.depends.map(d => {
                            const dep = ROADMAP.find(r => r.id === d);
                            return dep ? dep.name : d;
                          }).join(" + ")}
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        );
      })}
    </div>
  );
}
