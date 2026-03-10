/**
 * TopPanels — Overlay panels that slide down from the top bar
 *
 * One panel at a time. Backdrop click closes.
 * Each panel is a self-contained view. Add new panels here gradually.
 */
import { useState } from "react";
import type { TopPanel } from "./TopBar";
import {
  SUBSYSTEMS, FLIGHT_STEPS, TEAM, DOCS, QUICK_REF, SESSION_LOG,
  CHAT_DIGEST, STATUS_CONFIG, STEP_CONFIG, type DocEntry,
} from "./hub-data";

interface TopPanelsProps {
  activePanel: TopPanel;
  onClose: () => void;
}

export default function TopPanels({ activePanel, onClose }: TopPanelsProps) {
  if (!activePanel) return null;

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/30 z-[40] transition-opacity"
        onClick={onClose}
      />

      {/* Panel */}
      <div className="absolute left-0 right-0 top-9 z-[45] max-h-[70vh] overflow-y-auto
        bg-zinc-900/98 border-b border-zinc-700/50 shadow-2xl backdrop-blur-md">
        {activePanel === "status" && <StatusPanel />}
        {activePanel === "team" && <TeamPanel />}
        {activePanel === "docs" && <DocsPanel />}
        {activePanel === "ref" && <RefPanel />}
        {activePanel === "log" && <LogPanel />}
      </div>
    </>
  );
}

// ═══════════════════════════════════════════════════════════
// Status Panel
// ═══════════════════════════════════════════════════════════

function StatusPanel() {
  return (
    <div className="p-4 max-w-5xl mx-auto">
      <div className="grid grid-cols-2 gap-6">
        {/* Subsystems */}
        <div>
          <h3 className="text-[11px] font-bold text-zinc-300 uppercase tracking-wider mb-2">Subsystems</h3>
          <div className="space-y-0.5">
            {SUBSYSTEMS.map(s => {
              const cfg = STATUS_CONFIG[s.status];
              return (
                <div key={s.id} className="flex items-center gap-2 px-2 py-1 rounded hover:bg-zinc-800/30">
                  <div className="w-1.5 h-1.5 rounded-full shrink-0" style={{ background: cfg.color }} />
                  <span className="text-[10px] text-zinc-300 w-36 shrink-0">{s.name}</span>
                  <span className="text-[7px] px-1 rounded font-medium shrink-0"
                    style={{ color: cfg.color, background: cfg.bg }}>{cfg.label}</span>
                  <span className="text-[8px] text-zinc-600 truncate">{s.notes}</span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Flight steps */}
        <div>
          <h3 className="text-[11px] font-bold text-zinc-300 uppercase tracking-wider mb-2">Flight Testing</h3>
          <div className="space-y-1.5">
            {FLIGHT_STEPS.map(step => {
              const cfg = STEP_CONFIG[step.status];
              return (
                <div key={step.id} className="flex items-start gap-2 px-2 py-1.5 rounded hover:bg-zinc-800/30">
                  <span className="text-[11px] mt-0.5 shrink-0" style={{ color: cfg.color }}>{cfg.symbol}</span>
                  <div>
                    <div className="text-[10px] text-zinc-200">Step {step.id}: {step.name}</div>
                    <div className="text-[8px] text-zinc-500">{step.description}</div>
                    {step.script && <div className="text-[8px] text-cyan-600 font-mono">{step.script}</div>}
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

// ═══════════════════════════════════════════════════════════
// Team Panel
// ═══════════════════════════════════════════════════════════

function TeamPanel() {
  return (
    <div className="p-4 max-w-4xl mx-auto">
      <div className="grid grid-cols-2 gap-4">
        {/* Team members */}
        <div>
          <h3 className="text-[11px] font-bold text-zinc-300 uppercase tracking-wider mb-2">Team</h3>
          <div className="space-y-1.5">
            {TEAM.map(m => (
              <div key={m.id} className="p-2.5 rounded bg-zinc-800/30 border border-zinc-800/50">
                <div className="flex items-center gap-2">
                  <div className="w-2.5 h-2.5 rounded-full" style={{ background: m.color }} />
                  <span className="text-[11px] font-medium text-zinc-200">{m.name}</span>
                  <span className="text-[8px] text-zinc-600 ml-auto">{m.lastUpdate}</span>
                </div>
                <div className="text-[9px] text-zinc-500 mt-0.5">{m.role}</div>
                <div className="text-[9px] text-zinc-400 mt-1">{m.currentTask}</div>
                {m.needsFromYou && (
                  <div className="text-[8px] text-amber-400/80 mt-1.5 px-2 py-1 bg-amber-500/5 rounded border border-amber-500/10">
                    Needs: {m.needsFromYou}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Chat digest */}
        <div>
          <h3 className="text-[11px] font-bold text-zinc-300 uppercase tracking-wider mb-2">Team Comms</h3>
          <p className="text-[8px] text-zinc-600 mb-2">Key decisions from group chat</p>
          <div className="space-y-1.5">
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
        </div>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════
// Docs Panel
// ═══════════════════════════════════════════════════════════

const DOC_CATEGORIES: { id: DocEntry["category"]; label: string; color: string }[] = [
  { id: "guide", label: "Guides", color: "#22c55e" },
  { id: "hardware", label: "Hardware", color: "#f97316" },
  { id: "config", label: "Config", color: "#3b82f6" },
  { id: "test", label: "Test Scripts", color: "#8b5cf6" },
  { id: "reference", label: "Reference", color: "#6b7280" },
  { id: "manual", label: "External Manuals", color: "#a855f7" },
];

function DocsPanel() {
  const [activeCat, setActiveCat] = useState<string>("guide");

  return (
    <div className="p-4 max-w-5xl mx-auto">
      {/* Category tabs */}
      <div className="flex gap-1 mb-3">
        {DOC_CATEGORIES.map(cat => {
          const count = DOCS.filter(d => d.category === cat.id).length;
          if (count === 0 && cat.id !== "manual") return null;
          return (
            <button key={cat.id}
              onClick={() => setActiveCat(cat.id)}
              className={`px-2.5 py-1 rounded text-[9px] transition-all ${
                activeCat === cat.id ? "text-white" : "text-zinc-600 hover:text-zinc-400"
              }`}
              style={activeCat === cat.id ? { background: cat.color + "20", color: cat.color } : undefined}
            >
              {cat.label} {count > 0 && <span className="text-[7px] opacity-50">({count})</span>}
            </button>
          );
        })}
      </div>

      {/* Doc list */}
      {activeCat === "manual" ? (
        <div className="grid grid-cols-4 gap-2">
          {[
            { label: "CubePilot Docs", desc: "CubeOrangePlus hardware reference" },
            { label: "ArduCopter Parameters", desc: "Full parameter list" },
            { label: "MAVLink Protocol", desc: "Message reference" },
            { label: "picamera2 Docs", desc: "Pi camera library API" },
          ].map(m => (
            <div key={m.label} className="p-2.5 rounded bg-zinc-800/30 border border-zinc-800/50 hover:bg-zinc-800/50 cursor-pointer">
              <div className="text-[10px] text-zinc-300">{m.label}</div>
              <div className="text-[8px] text-zinc-600">{m.desc}</div>
            </div>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-3 gap-2">
          {DOCS.filter(d => d.category === activeCat).map(doc => (
            <div key={doc.path}
              className="p-2.5 rounded bg-zinc-800/30 border border-zinc-800/50 hover:bg-zinc-800/50 cursor-pointer transition-all"
            >
              <div className="text-[10px] text-zinc-200">{doc.title}</div>
              <div className="text-[8px] text-zinc-500 mt-0.5">{doc.description}</div>
              <div className="text-[7px] text-zinc-700 font-mono mt-1">{doc.path}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════
// Quick Ref Panel
// ═══════════════════════════════════════════════════════════

function RefPanel() {
  const [copied, setCopied] = useState<string | null>(null);

  const copy = (val: string, label: string) => {
    navigator.clipboard.writeText(val).then(() => {
      setCopied(label);
      setTimeout(() => setCopied(null), 1500);
    });
  };

  return (
    <div className="p-4 max-w-3xl mx-auto">
      <h3 className="text-[11px] font-bold text-zinc-300 uppercase tracking-wider mb-2">Quick Reference</h3>
      <div className="grid grid-cols-2 gap-x-6 gap-y-0.5">
        {QUICK_REF.map(r => (
          <div key={r.label}
            className={`flex items-center gap-2 px-2 py-1.5 rounded ${r.copyable ? "hover:bg-zinc-800/40 cursor-pointer" : ""}`}
            onClick={() => r.copyable && copy(r.value, r.label)}
          >
            <span className="text-[9px] text-zinc-600 w-20 shrink-0">{r.label}</span>
            <span className="text-[9px] text-zinc-300 font-mono break-all flex-1">{r.value}</span>
            {r.copyable && (
              <span className="text-[7px] text-zinc-700 shrink-0">
                {copied === r.label ? "\u2713 copied" : "click to copy"}
              </span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════
// Session Log Panel
// ═══════════════════════════════════════════════════════════

function LogPanel() {
  const [expanded, setExpanded] = useState<number | null>(0);

  return (
    <div className="p-4 max-w-4xl mx-auto">
      <h3 className="text-[11px] font-bold text-zinc-300 uppercase tracking-wider mb-2">Session Log</h3>
      <div className="space-y-1">
        {SESSION_LOG.map((s, i) => (
          <div key={i}
            className="rounded hover:bg-zinc-800/30 transition-all cursor-pointer"
            onClick={() => setExpanded(expanded === i ? null : i)}
          >
            <div className="flex items-center gap-3 px-3 py-1.5">
              <span className="text-[8px] text-zinc-600 font-mono w-24 shrink-0">{s.date}</span>
              <span className="text-[10px] text-zinc-300">{s.summary}</span>
              <span className="text-[8px] text-zinc-700 ml-auto">
                {expanded === i ? "\u25BC" : `${s.highlights.length} items \u25B6`}
              </span>
            </div>
            {expanded === i && (
              <div className="px-3 pb-2 ml-28 space-y-0.5">
                {s.highlights.map((h, j) => (
                  <div key={j} className="text-[8px] text-zinc-500 pl-2 border-l border-zinc-800">
                    {h}
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
