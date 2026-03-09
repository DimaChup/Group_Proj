/**
 * Group Project — Extracted Sub-Components
 *
 * Reusable pieces from the original GroupProjectTab, now importable
 * by the orchestrator shell and other Group Project panels.
 */
import { useState } from "react";
import {
  HOLY_GRAIL, GUIDING_PRINCIPLE, LEVELS, SE_LAYERS,
  DRONE_COMPONENTS, DRONE_CONNECTIONS, GROUP_COLORS,
  COMPUTE_DIMENSIONS, COMPUTE_NODES, COMPUTE_TOPOLOGIES,
  DIAGNOSTIC_STEPS,
  type AmbitionLevel, type Approach, type LayerContent, type SELayer, type TeamMember,
} from "./group-project-v2-data";

// ═══════════════════════════════════════════════════════════
// Shared Helpers
// ═══════════════════════════════════════════════════════════

export const SCAL_COLORS: Record<string, string> = { high: "#22c55e", medium: "#eab308", low: "#ef4444" };
const SCORE_COLORS = ["", "#ef4444", "#f97316", "#eab308", "#84cc16", "#22c55e"];
export const SCOPE_COLORS: Record<string, string> = { component: "#06b6d4", pair: "#a855f7", system: "#22c55e", diagnostic: "#ec4899" };

export function Badge({ text, color }: { text: string; color: string }) {
  return (
    <span className="px-1.5 py-0.5 rounded text-[9px] font-bold uppercase" style={{ background: color + "22", color, border: `1px solid ${color}44` }}>
      {text}
    </span>
  );
}

export function ScoreBar({ value, max = 5 }: { value: number; max?: number }) {
  return (
    <div className="flex gap-0.5">
      {Array.from({ length: max }, (_, i) => (
        <div key={i} className="w-3 h-2 rounded-sm" style={{ background: i < value ? SCORE_COLORS[value] : "#27272a" }} />
      ))}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════
// Holy Grail Banner
// ═══════════════════════════════════════════════════════════

export function HolyGrailBanner() {
  return (
    <div className="rounded-lg border border-amber-500/30 bg-gradient-to-r from-amber-500/10 via-amber-500/5 to-transparent p-4 mb-4">
      <div className="flex items-start gap-3">
        <span className="text-2xl mt-0.5">{"\u{1F3AF}"}</span>
        <div className="flex-1">
          <h2 className="text-[14px] font-bold text-amber-400 mb-1">The Holy Grail</h2>
          <p className="text-[12px] text-zinc-200 leading-relaxed">{HOLY_GRAIL}</p>
        </div>
      </div>
      <div className="mt-3 pt-3 border-t border-amber-500/20 flex items-start gap-3">
        <span className="text-lg mt-0.5">{"\u{1F9ED}"}</span>
        <div>
          <h3 className="text-[11px] font-bold text-zinc-400 uppercase tracking-wider mb-0.5">Guiding Principle</h3>
          <p className="text-[11px] text-zinc-400 leading-relaxed">{GUIDING_PRINCIPLE}</p>
        </div>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════
// Level Selector
// ═══════════════════════════════════════════════════════════

export function LevelSelector({ levels, activeId, onSelect }: { levels: AmbitionLevel[]; activeId: number; onSelect: (id: number) => void }) {
  return (
    <div className="grid grid-cols-3 gap-2 mb-4">
      {levels.map(lv => {
        const active = lv.id === activeId;
        return (
          <button key={lv.id} onClick={() => onSelect(lv.id)}
            className={`rounded-lg border p-3 text-left transition-all ${active ? "border-zinc-500 bg-zinc-800/80 shadow-lg" : "border-zinc-800 bg-zinc-900/40 hover:border-zinc-700 hover:bg-zinc-800/40"}`}>
            <div className="flex items-center gap-2 mb-1">
              <div className="w-2 h-2 rounded-full" style={{ background: active ? lv.color : "#52525b" }} />
              <span className={`text-[12px] font-bold ${active ? "text-zinc-100" : "text-zinc-500"}`}>{lv.name}</span>
            </div>
            <p className={`text-[10px] ${active ? "text-zinc-400" : "text-zinc-600"}`}>{lv.subtitle}</p>
          </button>
        );
      })}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════
// Ambition Panel
// ═══════════════════════════════════════════════════════════

export function AmbitionPanel({ level }: { level: AmbitionLevel }) {
  return (
    <div className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-4 mb-4">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <h3 className="text-[11px] font-bold text-zinc-400 uppercase tracking-wider mb-1.5">Operational Ambition</h3>
          <p className="text-[11px] text-zinc-300 leading-relaxed">{level.description}</p>
        </div>
        <div>
          <h3 className="text-[11px] font-bold uppercase tracking-wider mb-1.5" style={{ color: level.color }}>Core Challenge</h3>
          <p className="text-[12px] font-semibold text-zinc-200 mb-1">{level.coreChallenge}</p>
          <p className="text-[10px] text-zinc-500 leading-relaxed">{level.challengeDetail}</p>
          <div className="mt-2 px-2 py-1 rounded bg-zinc-800/80 border border-zinc-700/50">
            <span className="text-[9px] text-zinc-500 uppercase tracking-wider">Video: </span>
            <span className="text-[10px] font-mono" style={{ color: level.color }}>{level.videoStrategy}</span>
          </div>
        </div>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════
// Evolution Tracker
// ═══════════════════════════════════════════════════════════

export function EvolutionTracker({ level }: { level: AmbitionLevel }) {
  const { carriedOver, discarded, newChallenges } = level.evolution;
  const cols = [
    { title: "Building On Top", icon: "\u2705", items: carriedOver, color: "#22c55e", empty: "First level \u2014 nothing to inherit" },
    { title: "Discarding the Messy", icon: "\u{1F5D1}", items: discarded, color: "#ef4444", empty: "Nothing discarded" },
    { title: "New Complexities", icon: "\u26A1", items: newChallenges, color: "#f59e0b", empty: "No new challenges" },
  ];
  return (
    <div className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-4 mb-4">
      <h3 className="text-[13px] font-bold text-zinc-100 mb-1">System Evolution & Technical Debt</h3>
      <p className="text-[10px] text-zinc-500 mb-3">How this level builds on, replaces, and introduces new challenges</p>
      <div className="grid grid-cols-3 gap-3">
        {cols.map(col => (
          <div key={col.title} className="rounded border border-zinc-800 bg-zinc-950/50 p-3">
            <div className="flex items-center gap-1.5 mb-2">
              <span className="text-sm">{col.icon}</span>
              <h4 className="text-[10px] font-bold uppercase tracking-wider" style={{ color: col.color }}>{col.title}</h4>
            </div>
            {col.items.length === 0 ? (
              <p className="text-[10px] text-zinc-600 italic">{col.empty}</p>
            ) : (
              <ul className="space-y-1">
                {col.items.map((item, i) => (
                  <li key={i} className="text-[10px] text-zinc-400 leading-relaxed flex items-start gap-1.5">
                    <span className="mt-0.5 w-1 h-1 rounded-full shrink-0" style={{ background: col.color }} />
                    {item}
                  </li>
                ))}
              </ul>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════
// Drone Systems Blueprint (SVG)
// ═══════════════════════════════════════════════════════════

export function DroneBlueprintSVG({ activeLevel }: { activeLevel: number }) {
  const activeIds = new Set(DRONE_COMPONENTS.filter(c => c.activeAtLevels.includes(activeLevel)).map(c => c.id));

  return (
    <div className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-4 mb-4">
      <h3 className="text-[13px] font-bold text-zinc-100 mb-1">Drone Systems Blueprint</h3>
      <p className="text-[10px] text-zinc-500 mb-3">Components coloured by subsystem group. Dimmed = inactive at this level.</p>

      <div className="flex gap-3 mb-3 flex-wrap">
        {(Object.entries(GROUP_COLORS) as [string, string][]).map(([group, color]) => (
          <div key={group} className="flex items-center gap-1">
            <div className="w-2.5 h-2.5 rounded-sm" style={{ background: color }} />
            <span className="text-[9px] text-zinc-500 capitalize">{group}</span>
          </div>
        ))}
      </div>

      <svg viewBox="0 0 680 380" className="w-full" style={{ maxHeight: 340 }}>
        <line x1="0" y1="65" x2="680" y2="65" stroke="#3f3f46" strokeDasharray="6,4" strokeWidth="1" />
        <text x="10" y="58" fill="#52525b" fontSize="9" fontFamily="monospace">GROUND</text>
        <text x="10" y="78" fill="#52525b" fontSize="9" fontFamily="monospace">AIRBORNE</text>

        {DRONE_CONNECTIONS.map((conn, i) => {
          const from = DRONE_COMPONENTS.find(c => c.id === conn.from);
          const to = DRONE_COMPONENTS.find(c => c.id === conn.to);
          if (!from || !to) return null;
          const bothActive = activeIds.has(conn.from) && activeIds.has(conn.to);
          const color = conn.type === "power" ? "#eab308" : conn.type === "signal" ? "#06b6d4" : "#71717a";
          return (
            <line key={i}
              x1={from.x + 45} y1={from.y + 12} x2={to.x + 45} y2={to.y + 12}
              stroke={color} strokeWidth={bothActive ? 1.2 : 0.5} opacity={bothActive ? 0.5 : 0.15}
              strokeDasharray={conn.type === "power" ? "3,3" : conn.type === "signal" ? "2,2" : undefined}
            />
          );
        })}

        {DRONE_COMPONENTS.map(comp => {
          const active = activeIds.has(comp.id);
          const color = GROUP_COLORS[comp.group];
          return (
            <g key={comp.id} opacity={active ? 1 : 0.25}>
              <rect x={comp.x} y={comp.y} width={90} height={24} rx={4}
                fill={color + "18"} stroke={color} strokeWidth={active ? 1.2 : 0.5} />
              <text x={comp.x + 45} y={comp.y + 14} textAnchor="middle" fill={active ? "#e4e4e7" : "#52525b"}
                fontSize="9" fontFamily="monospace" fontWeight={active ? "600" : "400"}>
                {comp.name}
              </text>
            </g>
          );
        })}

        <g transform="translate(520, 340)">
          <line x1="0" y1="5" x2="20" y2="5" stroke="#eab308" strokeDasharray="3,3" strokeWidth="1" />
          <text x="25" y="8" fill="#71717a" fontSize="8">Power</text>
          <line x1="65" y1="5" x2="85" y2="5" stroke="#71717a" strokeWidth="1" />
          <text x="90" y="8" fill="#71717a" fontSize="8">Data</text>
          <line x1="120" y1="5" x2="140" y2="5" stroke="#06b6d4" strokeDasharray="2,2" strokeWidth="1" />
          <text x="145" y="8" fill="#71717a" fontSize="8">Signal</text>
        </g>
      </svg>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════
// SE Layer Stack
// ═══════════════════════════════════════════════════════════

function LayerContentView({ content, layer }: { content: LayerContent; layer: SELayer }) {
  return (
    <div className="space-y-3">
      <p className="text-[10px] text-zinc-300 leading-relaxed">{content.summary}</p>

      {content.components && content.components.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {content.components.map((g, i) => (
            <div key={i} className="rounded border border-zinc-800/50 bg-zinc-950/30 px-2 py-1.5">
              <h6 className="text-[8px] font-bold uppercase tracking-wider mb-1" style={{ color: layer.color }}>{g.group}</h6>
              <div className="flex flex-wrap gap-1">
                {g.items.map((item, j) => (
                  <span key={j} className="text-[9px] text-zinc-400 bg-zinc-800/50 px-1.5 py-0.5 rounded">{item}</span>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {content.decisions && content.decisions.length > 0 && (
        <div>
          <h6 className="text-[9px] font-bold text-zinc-500 uppercase tracking-wider mb-1.5">Design Decisions</h6>
          <div className="space-y-1.5">
            {content.decisions.map((d, i) => (
              <div key={i} className="rounded border border-zinc-800/50 bg-zinc-950/30 px-2 py-1.5">
                <div className="flex items-start gap-2">
                  <span className="text-[9px] text-zinc-500 shrink-0">Q:</span>
                  <span className="text-[9px] text-zinc-400">{d.question}</span>
                </div>
                <div className="flex items-start gap-2 mt-0.5">
                  <span className="text-[9px] font-bold shrink-0" style={{ color: layer.color }}>A:</span>
                  <span className="text-[9px] font-semibold text-zinc-200">{d.answer}</span>
                </div>
                <p className="text-[8px] text-zinc-600 mt-0.5 ml-4 italic">Why: {d.reasoning}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {content.tests.length > 0 && (
        <div>
          <h6 className="text-[9px] font-bold text-zinc-500 uppercase tracking-wider mb-1.5">Tests</h6>
          <div className="space-y-1">
            {content.tests.map((t, i) => (
              <div key={i} className="flex items-start gap-2 text-[9px] bg-zinc-950/30 rounded px-2 py-1 border border-zinc-800/30">
                <Badge text={t.scope} color={SCOPE_COLORS[t.scope] || "#71717a"} />
                <div className="flex-1">
                  <span className="text-zinc-300 font-medium">{t.name}</span>
                  <span className="text-emerald-500/70 ml-2">{"\u2713"} {t.pass}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export function SELayerStack({ level, approach }: { level: AmbitionLevel; approach: Approach }) {
  const [expanded, setExpanded] = useState<Set<string>>(new Set(["hardware"]));

  const toggle = (id: string) => {
    setExpanded(prev => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id); else next.add(id);
      return next;
    });
  };

  const getContent = (layerId: string): LayerContent | null => {
    return approach.layerOverrides[layerId] || level.baseLayers[layerId] || null;
  };

  return (
    <div className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-4 mb-4">
      <h3 className="text-[13px] font-bold text-zinc-100 mb-1">SE Layer Stack</h3>
      <p className="text-[10px] text-zinc-500 mb-3">6 layers from hardware (bottom) to orchestration (top). Click to expand. Layers 3-5 change with selected approach.</p>

      <div className="space-y-1">
        {[...SE_LAYERS].reverse().map(layer => {
          const content = getContent(layer.id);
          const isExpanded = expanded.has(layer.id);
          const isOverride = !!approach.layerOverrides[layer.id];

          return (
            <div key={layer.id} className="rounded border border-zinc-800/50 overflow-hidden">
              <button onClick={() => toggle(layer.id)}
                className={`w-full flex items-center gap-2 px-3 py-2 text-left transition-all ${isExpanded ? "bg-zinc-800/60" : "bg-zinc-950/30 hover:bg-zinc-800/30"}`}>
                <span className="text-sm">{layer.icon}</span>
                <div className="flex items-center gap-2 flex-1">
                  <span className="text-[10px] font-mono text-zinc-600">L{layer.number}</span>
                  <span className="text-[11px] font-bold" style={{ color: layer.color }}>{layer.name}</span>
                  {isOverride && (
                    <span className="text-[8px] px-1.5 py-0.5 rounded bg-sky-500/15 text-sky-400 border border-sky-500/30">
                      Approach-specific
                    </span>
                  )}
                </div>
                <span className="text-zinc-600 text-[10px]">{isExpanded ? "\u25B2" : "\u25BC"}</span>
              </button>

              {isExpanded && content && (
                <div className="px-3 pb-3 pt-1 border-t border-zinc-800/30">
                  <div className="mb-2 px-2 py-1 rounded bg-zinc-800/40 border border-zinc-700/30">
                    <span className="text-[8px] text-zinc-500 uppercase tracking-wider">SE Methodology: </span>
                    <span className="text-[9px] text-zinc-400">{layer.seApproach}</span>
                  </div>
                  <div className="mb-2 px-2 py-1 rounded bg-zinc-800/40 border border-zinc-700/30">
                    <span className="text-[8px] text-zinc-500 uppercase tracking-wider">Test Philosophy: </span>
                    <span className="text-[9px] text-zinc-400">{layer.testPhilosophy}</span>
                  </div>
                  <LayerContentView content={content} layer={layer} />
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════
// Approach Selector & Detail
// ═══════════════════════════════════════════════════════════

export function ApproachSelector({ approaches, selectedId, onSelect }: { approaches: Approach[]; selectedId: string; onSelect: (id: string) => void }) {
  return (
    <div className="grid grid-cols-3 gap-2 mb-4">
      {approaches.map(a => {
        const active = a.id === selectedId;
        return (
          <button key={a.id} onClick={() => onSelect(a.id)}
            className={`rounded-lg border p-3 text-left transition-all ${active ? "border-zinc-500 bg-zinc-800/80" : "border-zinc-800 bg-zinc-900/40 hover:border-zinc-700"}`}>
            <div className="flex items-center justify-between mb-1">
              <span className={`text-[11px] font-bold ${active ? "text-zinc-100" : "text-zinc-500"}`}>{a.name}</span>
              <Badge text={a.scalability} color={SCAL_COLORS[a.scalability]} />
            </div>
            <p className={`text-[9px] mb-2 ${active ? "text-zinc-400" : "text-zinc-600"}`}>{a.subtitle}</p>
            <div className="grid grid-cols-3 gap-1 text-[8px]">
              <span className="text-emerald-500">+{a.pros.length} pros</span>
              <span className="text-red-400">-{a.cons.length} cons</span>
              <span className="text-sky-400">{Object.keys(a.layerOverrides).length} layers</span>
            </div>
          </button>
        );
      })}
    </div>
  );
}

export function ApproachDetail({ approach }: { approach: Approach }) {
  return (
    <div className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-4 mb-4">
      <div className="flex items-center gap-2 mb-3">
        <h3 className="text-[13px] font-bold text-zinc-100">{approach.name}</h3>
        <Badge text={approach.scalability + " scalability"} color={SCAL_COLORS[approach.scalability]} />
      </div>
      <div className="grid grid-cols-3 gap-3">
        <div className="rounded border border-emerald-500/20 bg-emerald-500/5 p-3">
          <h4 className="text-[10px] font-bold text-emerald-400 uppercase mb-2">Pros</h4>
          <ul className="space-y-1">
            {approach.pros.map((p, i) => (
              <li key={i} className="text-[10px] text-zinc-300 flex items-start gap-1.5"><span className="text-emerald-500 shrink-0">+</span> {p}</li>
            ))}
          </ul>
        </div>
        <div className="rounded border border-red-500/20 bg-red-500/5 p-3">
          <h4 className="text-[10px] font-bold text-red-400 uppercase mb-2">Cons</h4>
          <ul className="space-y-1">
            {approach.cons.map((c, i) => (
              <li key={i} className="text-[10px] text-zinc-300 flex items-start gap-1.5"><span className="text-red-400 shrink-0">-</span> {c}</li>
            ))}
          </ul>
        </div>
        <div className="rounded border border-sky-500/20 bg-sky-500/5 p-3">
          <h4 className="text-[10px] font-bold text-sky-400 uppercase mb-2">Path to Next Level</h4>
          <p className="text-[10px] text-zinc-300 leading-relaxed">{approach.pathToNext}</p>
        </div>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════
// Diagnostic Protocol
// ═══════════════════════════════════════════════════════════

export function DiagnosticProtocol() {
  const [expanded, setExpanded] = useState<number | null>(null);

  return (
    <div className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-4 mb-4">
      <h3 className="text-[13px] font-bold text-zinc-100 mb-1">Diagnostic Protocol</h3>
      <p className="text-[10px] text-zinc-500 mb-3">When something breaks: trace DOWN through layers to isolate root cause. Is it hardware (L1)? Signals (L2)? Comms (L3)? Software (L5)?</p>
      <div className="space-y-1.5">
        {DIAGNOSTIC_STEPS.map((diag, i) => {
          const isOpen = expanded === i;
          const startLayer = SE_LAYERS.find(l => l.id === diag.checkLayer);
          return (
            <div key={i} className="rounded border border-zinc-800/50 overflow-hidden">
              <button onClick={() => setExpanded(isOpen ? null : i)}
                className={`w-full flex items-center gap-2 px-3 py-2 text-left ${isOpen ? "bg-zinc-800/60" : "bg-zinc-950/30 hover:bg-zinc-800/30"}`}>
                <span className="text-red-400 text-[12px]">{"\u26A0"}</span>
                <span className="text-[10px] font-bold text-zinc-200 flex-1">{diag.symptom}</span>
                {startLayer && <Badge text={`Start: L${startLayer.number}`} color={startLayer.color} />}
                <span className="text-zinc-600 text-[10px]">{isOpen ? "\u25B2" : "\u25BC"}</span>
              </button>
              {isOpen && (
                <div className="px-3 pb-3 pt-1 border-t border-zinc-800/30 space-y-1">
                  {diag.checks.map((check, j) => (
                    <div key={j} className="flex items-start gap-2 text-[9px] bg-zinc-950/30 rounded px-2 py-1.5">
                      <span className="text-zinc-500 font-mono shrink-0">{j + 1}.</span>
                      <div className="flex-1">
                        <span className="text-zinc-300 font-semibold">{check.test}</span>
                        <div className="flex gap-4 mt-0.5">
                          <span className="text-emerald-500">{"\u2713"} Pass: {check.ifPass}</span>
                          <span className="text-red-400">{"\u2717"} Fail: {check.ifFail}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════
// Right Sidebar (Compute Trade Study + Team + Test Legend)
// ═══════════════════════════════════════════════════════════

export function RightSidebar({ team }: { team: TeamMember[] }) {
  const [selectedTopo, setSelectedTopo] = useState(0);
  const topo = COMPUTE_TOPOLOGIES[selectedTopo];

  return (
    <div className="space-y-3">
      {/* SE Layer Reference */}
      <div>
        <h3 className="text-[10px] font-bold text-zinc-400 uppercase tracking-wider mb-2">SE Layers</h3>
        <div className="space-y-0.5">
          {SE_LAYERS.map(l => (
            <div key={l.id} className="flex items-center gap-1.5 text-[9px] px-1.5 py-1 rounded hover:bg-zinc-800/30">
              <span>{l.icon}</span>
              <span className="font-mono text-zinc-600">L{l.number}</span>
              <span style={{ color: l.color }}>{l.name.split("/")[0].trim()}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Compute Trade Study */}
      <div>
        <h3 className="text-[10px] font-bold text-zinc-400 uppercase tracking-wider mb-2">Compute Trade Study</h3>
        <table className="w-full text-[9px]">
          <thead>
            <tr className="border-b border-zinc-800">
              <th className="text-left text-zinc-500 pb-1">Node</th>
              {COMPUTE_DIMENSIONS.map(d => (
                <th key={d} className="text-center text-zinc-600 pb-1 px-0.5" title={d}>{d.slice(0, 4)}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {COMPUTE_NODES.map(node => (
              <tr key={node.id} className="border-b border-zinc-800/50">
                <td className="py-1.5">
                  <div className="text-[9px] font-semibold text-zinc-300">{node.name}</div>
                  <div className="text-[7px] text-zinc-600">{node.type}</div>
                </td>
                {COMPUTE_DIMENSIONS.map(d => (
                  <td key={d} className="text-center py-1.5 px-0.5"><ScoreBar value={node.scores[d]} /></td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Topologies */}
      <div>
        <h3 className="text-[10px] font-bold text-zinc-400 uppercase tracking-wider mb-2">Topologies</h3>
        <div className="space-y-1 mb-2">
          {COMPUTE_TOPOLOGIES.map((t, i) => (
            <button key={t.id} onClick={() => setSelectedTopo(i)}
              className={`w-full text-left px-2 py-1.5 rounded text-[9px] transition-all ${i === selectedTopo ? "bg-zinc-700/80 text-zinc-100 font-medium" : "text-zinc-500 hover:text-zinc-300 hover:bg-zinc-800/50"}`}>
              {t.name}
            </button>
          ))}
        </div>
        <div className="rounded border border-zinc-800 bg-zinc-950/50 p-2">
          <p className="text-[9px] text-zinc-400 mb-2">{topo.description}</p>
          <div className="space-y-1 mb-2">
            {topo.allocation.map((a, i) => (
              <div key={i} className="flex items-center justify-between text-[9px]">
                <span className="text-zinc-500">{a.task}</span>
                <span className="font-mono text-[8px]" style={{ color: a.node === "cube" ? "#f97316" : a.node === "pi" ? "#a855f7" : "#22c55e" }}>
                  {a.node.toUpperCase()}
                </span>
              </div>
            ))}
          </div>
          <div className="rounded bg-red-500/10 border border-red-500/20 px-2 py-1">
            <span className="text-[8px] text-red-400 font-bold">Bottleneck: </span>
            <span className="text-[8px] text-red-300">{topo.bottleneck}</span>
          </div>
          <div className="mt-1.5 flex gap-1">
            {topo.suitableForLevels.map(l => (
              <span key={l} className="text-[8px] px-1.5 py-0.5 rounded bg-zinc-800 text-zinc-400">L{l}</span>
            ))}
          </div>
        </div>
      </div>

      {/* Team */}
      <div>
        <h3 className="text-[10px] font-bold text-zinc-400 uppercase tracking-wider mb-2">Team</h3>
        <div className="space-y-1">
          {team.map(m => (
            <div key={m.id} className="flex items-center gap-1.5 text-[9px]">
              <span>{m.icon}</span>
              <span style={{ color: m.color }}>{m.name}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Test Scope Legend */}
      <div>
        <h3 className="text-[10px] font-bold text-zinc-400 uppercase tracking-wider mb-2">Test Scopes</h3>
        <div className="space-y-1">
          {[
            { scope: "component", desc: "Single part, isolated" },
            { scope: "pair", desc: "Two parts together" },
            { scope: "system", desc: "Full system end-to-end" },
            { scope: "diagnostic", desc: "Fault isolation" },
          ].map(s => (
            <div key={s.scope} className="flex items-center gap-1.5 text-[9px]">
              <div className="w-2.5 h-2.5 rounded-sm" style={{ background: SCOPE_COLORS[s.scope] }} />
              <span className="text-zinc-400 capitalize">{s.scope}</span>
              <span className="text-zinc-600">- {s.desc}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
