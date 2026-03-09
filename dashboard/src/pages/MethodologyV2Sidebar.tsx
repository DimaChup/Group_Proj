/**
 * MethodologySidebar — Left sidebar for Group Project tab
 *
 * 5 collapsible sections:
 *   1. Our Paradigm (green callout)
 *   2. Methods Toolkit
 *   3. Decision Tree
 *   4. Design Timeline
 *   5. Strategy Lock-In
 */
import { useState } from "react";
import {
  SE_METHODOLOGY, DECISION_TREE, DESIGN_PHASES,
  type DecisionNode, type DesignPhase,
} from "./group-project-v2-data";

const STATUS_COLORS: Record<string, string> = {
  locked: "#22c55e",
  exploring: "#eab308",
  backtracked: "#ef4444",
};

const PHASE_COLORS: Record<string, { bg: string; text: string; border: string }> = {
  completed: { bg: "bg-emerald-500/10", text: "text-emerald-400", border: "border-emerald-500/30" },
  active:    { bg: "bg-amber-500/10",   text: "text-amber-400",   border: "border-amber-500/30" },
  upcoming:  { bg: "bg-zinc-800/30",    text: "text-zinc-600",    border: "border-zinc-800/50" },
};

function SectionHeader({ title, icon, open, onToggle }: { title: string; icon: string; open: boolean; onToggle: () => void }) {
  return (
    <button onClick={onToggle}
      className="w-full flex items-center gap-1.5 text-left py-1.5 px-1 rounded hover:bg-zinc-800/30 transition-all">
      <span className="text-[11px]">{icon}</span>
      <span className="text-[10px] font-bold text-zinc-300 flex-1">{title}</span>
      <span className="text-zinc-600 text-[9px]">{open ? "\u25B2" : "\u25BC"}</span>
    </button>
  );
}

// ═══════════════════════════════════════════════════════════
// 1. Our Paradigm
// ═══════════════════════════════════════════════════════════

function ParadigmSection() {
  const [showDetail, setShowDetail] = useState(false);
  const m = SE_METHODOLOGY;

  return (
    <div>
      {/* Green callout — inspired by ParadigmsTab "Our Approach" */}
      <div className="rounded border border-emerald-500/30 bg-emerald-500/8 p-2.5">
        <div className="flex items-center gap-1.5 mb-1">
          <span className="text-[10px]">{"\u2705"}</span>
          <h4 className="text-[10px] font-bold text-emerald-400 uppercase tracking-wider">Our Paradigm</h4>
        </div>
        <p className="text-[11px] font-semibold text-zinc-200 mb-1">{m.paradigm}</p>
        <p className="text-[9px] text-zinc-400 leading-relaxed">{m.paradigmShort}</p>

        <button onClick={() => setShowDetail(!showDetail)}
          className="text-[8px] text-emerald-400/70 hover:text-emerald-400 mt-1.5 underline">
          {showDetail ? "Hide" : "Show"} justification
        </button>

        {showDetail && (
          <div className="mt-2 space-y-2">
            <p className="text-[9px] text-zinc-400 leading-relaxed">{m.paradigmJustification}</p>
            <div className="space-y-1">
              <h5 className="text-[8px] font-bold text-zinc-500 uppercase">Why not these?</h5>
              {m.whyNotOthers.map((w, i) => (
                <div key={i} className="flex items-start gap-1.5 text-[8px]">
                  <span className="text-red-400 shrink-0 mt-0.5">{"\u2717"}</span>
                  <div>
                    <span className="text-zinc-400 font-semibold">{w.paradigm}: </span>
                    <span className="text-zinc-500">{w.reason}</span>
                  </div>
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
// 2. Methods Toolkit
// ═══════════════════════════════════════════════════════════

function MethodsSection() {
  const [expandedIdx, setExpandedIdx] = useState<number | null>(null);

  return (
    <div className="space-y-1">
      {SE_METHODOLOGY.methods.map((method, i) => (
        <div key={i} className="rounded border border-zinc-800/50 overflow-hidden">
          <button onClick={() => setExpandedIdx(expandedIdx === i ? null : i)}
            className={`w-full text-left px-2 py-1.5 flex items-start gap-1.5 text-[9px] transition-all ${expandedIdx === i ? "bg-zinc-800/50" : "bg-zinc-950/20 hover:bg-zinc-800/20"}`}>
            <span className="text-zinc-500 font-mono shrink-0 mt-px">{i + 1}.</span>
            <div className="flex-1">
              <span className="text-zinc-200 font-semibold">{method.name}</span>
              <span className="text-zinc-600 ml-1.5 text-[8px]">{method.appliedAt}</span>
            </div>
          </button>
          {expandedIdx === i && (
            <div className="px-2 pb-2 pt-1 border-t border-zinc-800/30">
              <p className="text-[8px] text-zinc-400 leading-relaxed">
                <span className="text-sky-400 font-bold">Why? </span>{method.why}
              </p>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════
// 3. Decision Tree
// ═══════════════════════════════════════════════════════════

function DecisionTreeSection() {
  const [expandedNode, setExpandedNode] = useState<string | null>(null);

  // Build tree structure by levels
  const maxLevel = Math.max(...DECISION_TREE.map(n => n.level));
  const nodesByLevel: DecisionNode[][] = [];
  for (let l = 0; l <= maxLevel; l++) {
    nodesByLevel.push(DECISION_TREE.filter(n => n.level === l));
  }

  return (
    <div className="space-y-1">
      {nodesByLevel.map((nodes, levelIdx) => (
        <div key={levelIdx}>
          {levelIdx > 0 && (
            <div className="flex justify-center py-0.5">
              <div className="w-px h-2 bg-zinc-700" />
            </div>
          )}
          <div className="flex flex-wrap gap-1">
            {nodes.map(node => {
              const isOpen = expandedNode === node.id;
              const statusColor = STATUS_COLORS[node.status];
              return (
                <button key={node.id} onClick={() => setExpandedNode(isOpen ? null : node.id)}
                  className={`flex-1 min-w-0 rounded border px-1.5 py-1 text-left transition-all ${isOpen ? "bg-zinc-800/60 border-zinc-600" : "bg-zinc-950/30 border-zinc-800/50 hover:border-zinc-700"}`}
                  style={{ borderLeftColor: statusColor, borderLeftWidth: 2 }}>
                  <div className="flex items-center gap-1">
                    <div className="w-1.5 h-1.5 rounded-full" style={{ background: statusColor }} />
                    <span className="text-[8px] text-zinc-400 truncate">{node.question}</span>
                  </div>
                  {isOpen && (
                    <div className="mt-1 pt-1 border-t border-zinc-800/30">
                      <p className="text-[8px] text-zinc-200 font-semibold">{node.answer}</p>
                      <span className="text-[7px] px-1 py-0.5 rounded mt-0.5 inline-block"
                        style={{ background: statusColor + "18", color: statusColor }}>
                        {node.status}
                      </span>
                    </div>
                  )}
                </button>
              );
            })}
          </div>
        </div>
      ))}

      {/* Legend */}
      <div className="flex gap-2 pt-1 border-t border-zinc-800/30">
        {(["locked", "exploring", "backtracked"] as const).map(s => (
          <div key={s} className="flex items-center gap-1 text-[7px]">
            <div className="w-1.5 h-1.5 rounded-full" style={{ background: STATUS_COLORS[s] }} />
            <span className="text-zinc-500 capitalize">{s}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════
// 4. Design Timeline
// ═══════════════════════════════════════════════════════════

function TimelineSection() {
  return (
    <div className="relative">
      {/* Vertical line */}
      <div className="absolute left-[7px] top-2 bottom-2 w-px bg-zinc-800" />

      <div className="space-y-0.5">
        {DESIGN_PHASES.map((phase, i) => {
          const colors = PHASE_COLORS[phase.status];
          return (
            <div key={phase.id} className="flex items-start gap-2 relative">
              {/* Status dot */}
              <div className="relative z-10 mt-1.5 shrink-0">
                {phase.status === "completed" ? (
                  <div className="w-[15px] h-[15px] rounded-full bg-emerald-500/20 border border-emerald-500/50 flex items-center justify-center">
                    <span className="text-[8px] text-emerald-400">{"\u2713"}</span>
                  </div>
                ) : phase.status === "active" ? (
                  <div className="w-[15px] h-[15px] rounded-full bg-amber-500/20 border border-amber-500/50 flex items-center justify-center">
                    <div className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse" />
                  </div>
                ) : (
                  <div className="w-[15px] h-[15px] rounded-full bg-zinc-800 border border-zinc-700 flex items-center justify-center">
                    <span className="text-[7px] text-zinc-600">{phase.number}</span>
                  </div>
                )}
              </div>

              {/* Content */}
              <div className={`flex-1 rounded border px-2 py-1.5 ${colors.bg} ${colors.border}`}>
                <div className="flex items-center gap-1.5">
                  <span className={`text-[9px] font-bold ${colors.text}`}>{phase.name}</span>
                  {phase.backtrackTarget && (
                    <span className="text-[7px] text-amber-500/60">{"\u21A9"}</span>
                  )}
                </div>
                <p className="text-[8px] text-zinc-500 leading-relaxed mt-0.5">{phase.description}</p>
                {phase.status !== "upcoming" && (
                  <div className="flex flex-wrap gap-1 mt-1">
                    {phase.outputs.map((o, j) => (
                      <span key={j} className="text-[7px] px-1 py-0.5 rounded bg-zinc-800/50 text-zinc-500">{o}</span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════
// 5. Strategy Lock-In
// ═══════════════════════════════════════════════════════════

function LockInSection() {
  const locked = DECISION_TREE.filter(n => n.status === "locked");
  const exploring = DECISION_TREE.filter(n => n.status === "exploring");
  const total = DECISION_TREE.length;
  const pct = Math.round((locked.length / total) * 100);

  return (
    <div>
      {/* Progress bar */}
      <div className="flex items-center gap-2 mb-2">
        <div className="flex-1 h-1.5 rounded-full bg-zinc-800 overflow-hidden">
          <div className="h-full rounded-full bg-emerald-500/60 transition-all" style={{ width: `${pct}%` }} />
        </div>
        <span className="text-[9px] text-zinc-400 font-mono">{locked.length}/{total}</span>
      </div>

      <div className="space-y-1">
        <div className="text-[8px]">
          <span className="text-emerald-400 font-bold">{locked.length} locked</span>
          <span className="text-zinc-600 mx-1">{"\u00B7"}</span>
          <span className="text-amber-400 font-bold">{exploring.length} exploring</span>
        </div>

        {exploring.length > 0 && (
          <div className="rounded border border-amber-500/20 bg-amber-500/5 p-1.5">
            <h5 className="text-[8px] font-bold text-amber-400 uppercase mb-1">Open Questions</h5>
            {exploring.map(n => (
              <div key={n.id} className="text-[8px] text-zinc-400 flex items-start gap-1 mb-0.5">
                <span className="text-amber-400 shrink-0">{"\u2022"}</span>
                <span>{n.question} <span className="text-zinc-600 italic">({n.answer})</span></span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════
// Main Sidebar Component
// ═══════════════════════════════════════════════════════════

export default function MethodologySidebar() {
  const [openSections, setOpenSections] = useState<Set<string>>(new Set(["paradigm", "timeline", "lock-in"]));

  const toggle = (id: string) => {
    setOpenSections(prev => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id); else next.add(id);
      return next;
    });
  };

  const sections = [
    { id: "paradigm",  title: "Our Paradigm",    icon: "\u{1F9ED}", content: <ParadigmSection /> },
    { id: "methods",   title: "Methods Toolkit",  icon: "\u{1F9F0}", content: <MethodsSection /> },
    { id: "tree",      title: "Decision Tree",    icon: "\u{1F333}", content: <DecisionTreeSection /> },
    { id: "timeline",  title: "Design Timeline",  icon: "\u{23F1}",  content: <TimelineSection /> },
    { id: "lock-in",   title: "Strategy Lock-In", icon: "\u{1F512}", content: <LockInSection /> },
  ];

  return (
    <div className="space-y-2">
      <h3 className="text-[11px] font-bold text-zinc-300 uppercase tracking-wider px-1">SE Strategy</h3>

      {sections.map(s => (
        <div key={s.id} className="rounded-lg border border-zinc-800/50 bg-zinc-900/40 overflow-hidden">
          <SectionHeader title={s.title} icon={s.icon} open={openSections.has(s.id)} onToggle={() => toggle(s.id)} />
          {openSections.has(s.id) && (
            <div className="px-2 pb-2 border-t border-zinc-800/30">
              {s.content}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
