import { useState } from "react";
import {
  PIPELINE, PHASE_COLORS, STATUS_COLORS, SCORE_LABELS, MISSION_GOAL, DESIGN_CHOICES,
  type Stage, type Approach, type ApproachStatus, type DesignCategory,
} from "./pipeline-data";

// ── Score bar (5 blocks) ──
function ScoreBar({ value, color }: { value: number; color: string }) {
  return (
    <div className="flex gap-[2px]">
      {[1, 2, 3, 4, 5].map(i => (
        <div
          key={i}
          className={`w-[6px] h-[6px] rounded-[1px] ${i <= value ? color : "bg-zinc-800"}`}
        />
      ))}
    </div>
  );
}

// ── Mini radar chart (SVG) ──
function RadarChart({ scores, size = 48, color }: { scores: Record<string, number>; size?: number; color: string }) {
  const cx = size / 2;
  const cy = size / 2;
  const r = size / 2 - 4;
  const keys = SCORE_LABELS;
  const angleStep = (2 * Math.PI) / keys.length;

  const points = keys.map((k, i) => {
    const angle = i * angleStep - Math.PI / 2;
    const val = (scores[k] || 0) / 5;
    return { x: cx + r * val * Math.cos(angle), y: cy + r * val * Math.sin(angle) };
  });

  const pathD = points.map((p, i) => `${i === 0 ? "M" : "L"} ${p.x.toFixed(1)} ${p.y.toFixed(1)}`).join(" ") + " Z";

  // Grid rings
  const rings = [0.2, 0.4, 0.6, 0.8, 1.0];

  return (
    <svg width={size} height={size} className="shrink-0">
      {/* Grid */}
      {rings.map(rv => (
        <polygon
          key={rv}
          points={keys.map((_, i) => {
            const a = i * angleStep - Math.PI / 2;
            return `${(cx + r * rv * Math.cos(a)).toFixed(1)},${(cy + r * rv * Math.sin(a)).toFixed(1)}`;
          }).join(" ")}
          fill="none" stroke="rgb(63 63 70 / 0.3)" strokeWidth="0.5"
        />
      ))}
      {/* Axes */}
      {keys.map((_, i) => {
        const a = i * angleStep - Math.PI / 2;
        return (
          <line key={i}
            x1={cx} y1={cy}
            x2={cx + r * Math.cos(a)} y2={cy + r * Math.sin(a)}
            stroke="rgb(63 63 70 / 0.2)" strokeWidth="0.5"
          />
        );
      })}
      {/* Data */}
      <polygon points={points.map(p => `${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(" ")}
        fill={color} fillOpacity="0.15" stroke={color} strokeWidth="1.5"
      />
    </svg>
  );
}

// ── Status badge ──
function StatusBadge({ status }: { status: ApproachStatus }) {
  const s = STATUS_COLORS[status];
  return (
    <span className={`text-[7px] font-bold tracking-wider px-1.5 py-0.5 rounded ${s.bg} ${s.text}`}>
      {s.label}
    </span>
  );
}

// ── Approach card ──
function ApproachCard({ approach, isExpanded, onToggle, phaseColor }: {
  approach: Approach; isExpanded: boolean; onToggle: () => void; phaseColor: string;
}) {
  const s = STATUS_COLORS[approach.status];
  const radarColor = approach.status === "selected" ? "#22c55e"
    : approach.status === "rejected" ? "#ef4444"
    : approach.status === "planned" ? "#3b82f6"
    : approach.status === "research" ? "#8b5cf6"
    : "#71717a";

  return (
    <div
      onClick={onToggle}
      className={`
        relative rounded-lg border cursor-pointer transition-all shrink-0
        ${approach.status === "selected"
          ? `${s.border} ${s.bg} shadow-lg shadow-emerald-500/5`
          : approach.status === "rejected"
            ? `border-dashed ${s.border} ${s.bg} opacity-60`
            : `${s.border} ${s.bg} hover:border-zinc-600`
        }
        ${isExpanded ? "w-[240px]" : "w-[180px]"}
      `}
    >
      {/* Selected glow line */}
      {approach.status === "selected" && (
        <div className="absolute top-0 left-3 right-3 h-[2px] bg-emerald-500/60 rounded-full" />
      )}

      <div className="p-2.5 space-y-2">
        {/* Header */}
        <div className="flex items-start justify-between gap-1">
          <div className="min-w-0">
            <div className={`text-[11px] font-medium leading-tight ${approach.status === "selected" ? "text-emerald-300" : "text-zinc-200"}`}>
              {approach.name}
            </div>
            <div className="text-[8px] text-zinc-500 leading-tight mt-0.5">{approach.subtitle}</div>
          </div>
          <RadarChart scores={approach.scores} size={36} color={radarColor} />
        </div>

        {/* Status */}
        <StatusBadge status={approach.status} />

        {/* Score bars */}
        <div className="space-y-1">
          {SCORE_LABELS.map(label => (
            <div key={label} className="flex items-center gap-1.5">
              <span className="text-[7px] text-zinc-600 w-[44px] text-right capitalize">{label}</span>
              <ScoreBar
                value={approach.scores[label]}
                color={approach.status === "selected" ? "bg-emerald-500" : approach.status === "rejected" ? "bg-red-500/50" : phaseColor}
              />
            </div>
          ))}
        </div>

        {/* Expanded: pros/cons/depends */}
        {isExpanded && (
          <div className="space-y-1.5 pt-1 border-t border-zinc-800/50">
            {approach.pros.map((p, i) => (
              <div key={i} className="text-[8px] text-emerald-400/70 leading-tight">+ {p}</div>
            ))}
            {approach.cons.map((c, i) => (
              <div key={i} className="text-[8px] text-red-400/60 leading-tight">− {c}</div>
            ))}
            {approach.notes && (
              <div className="text-[8px] text-zinc-500 leading-tight italic mt-1">{approach.notes}</div>
            )}
            {approach.depends && approach.depends.length > 0 && (
              <div className="mt-1.5 pt-1 border-t border-zinc-800/30">
                <div className="text-[7px] text-amber-500/70 font-bold tracking-wider mb-0.5">DEPENDS ON</div>
                {approach.depends.map((d, i) => (
                  <div key={i} className="text-[8px] text-amber-400/50 leading-tight">⤷ {d}</div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

// ── Connection line between stages ──
function ConnectionLine({ phase }: { phase: string }) {
  const color = phase === "pre-mission" ? "bg-amber-500/30"
    : phase === "flight" ? "bg-cyan-500/30"
    : "bg-purple-500/30";
  return (
    <div className="flex justify-center py-1">
      <div className={`w-[2px] h-6 ${color} rounded-full`} />
    </div>
  );
}

// ── Stage row ──
function StageRow({ stage, expandedCard, onToggleCard }: {
  stage: Stage; expandedCard: string | null; onToggleCard: (id: string) => void;
}) {
  const pc = PHASE_COLORS[stage.phase];
  const scoreColor = stage.phase === "pre-mission" ? "bg-amber-500"
    : stage.phase === "flight" ? "bg-cyan-500"
    : "bg-purple-500";
  const selected = stage.approaches.find(a => a.status === "selected");

  return (
    <div className={`rounded-xl border ${pc.border} ${pc.bg} overflow-hidden`}>
      {/* Stage header */}
      <div className="px-4 py-2.5 flex items-center gap-3">
        <span className="text-lg">{stage.icon}</span>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className={`text-[9px] font-bold ${pc.text} opacity-60`}>STAGE {stage.number}</span>
            <span className="text-[12px] font-medium text-zinc-200">{stage.name}</span>
            {stage.requirements && stage.requirements.map(r => (
              <span key={r} className="text-[7px] font-mono text-zinc-500 bg-zinc-800/60 px-1 py-0.5 rounded">
                {r}
              </span>
            ))}
          </div>
          <div className="text-[9px] text-zinc-500">{stage.subGoal}</div>
        </div>
        {selected && (
          <div className="text-[9px] text-emerald-400/80 bg-emerald-500/10 px-2 py-0.5 rounded shrink-0">
            → {selected.name}
          </div>
        )}
        <span className="text-[9px] text-zinc-600">{stage.approaches.length} options</span>
      </div>

      {/* Approach cards row */}
      <div className="px-3 pb-3 flex gap-2 overflow-x-auto">
        {/* Selected first */}
        {stage.approaches
          .sort((a, b) => {
            const order: Record<ApproachStatus, number> = { selected: 0, available: 1, planned: 2, research: 3, rejected: 4 };
            return order[a.status] - order[b.status];
          })
          .map(approach => (
            <ApproachCard
              key={approach.id}
              approach={approach}
              isExpanded={expandedCard === approach.id}
              onToggle={() => onToggleCard(approach.id)}
              phaseColor={scoreColor}
            />
          ))
        }
      </div>
    </div>
  );
}

// ── Phase header ──
function PhaseHeader({ phase, label }: { phase: string; label: string }) {
  const pc = PHASE_COLORS[phase];
  return (
    <div className={`flex items-center gap-3 px-2 py-1`}>
      <div className={`h-[1px] flex-1 ${pc.border.replace("border-", "bg-")}`} />
      <span className={`text-[10px] font-bold tracking-widest ${pc.text} uppercase`}>{label}</span>
      <div className={`h-[1px] flex-1 ${pc.border.replace("border-", "bg-")}`} />
    </div>
  );
}

// ── Summary stats ──
function PipelineSummary() {
  const totalApproaches = PIPELINE.reduce((sum, s) => sum + s.approaches.length, 0);
  const selected = PIPELINE.reduce((sum, s) => sum + s.approaches.filter(a => a.status === "selected").length, 0);
  const planned = PIPELINE.reduce((sum, s) => sum + s.approaches.filter(a => a.status === "planned").length, 0);
  const rejected = PIPELINE.reduce((sum, s) => sum + s.approaches.filter(a => a.status === "rejected").length, 0);

  return (
    <div className="flex items-center gap-4 px-4 py-2 bg-zinc-900/40 rounded-lg border border-zinc-800/50">
      <div className="text-[11px] text-zinc-400">
        <span className="text-zinc-200 font-medium">{PIPELINE.length}</span> stages
      </div>
      <div className="text-[11px] text-zinc-400">
        <span className="text-zinc-200 font-medium">{totalApproaches}</span> approaches evaluated
      </div>
      <div className="w-[1px] h-3 bg-zinc-800" />
      <div className="text-[11px] text-emerald-400">
        <span className="font-medium">{selected}</span> selected
      </div>
      <div className="text-[11px] text-blue-400">
        <span className="font-medium">{planned}</span> planned
      </div>
      <div className="text-[11px] text-red-400/60">
        <span className="font-medium">{rejected}</span> rejected
      </div>
    </div>
  );
}

// ── Design choice card ──
function DesignChoiceCard({ choice, isExpanded, onToggle }: {
  choice: { id: string; name: string; currentValue: string; unit?: string; alternatives?: string[]; tuningNotes: string; configFile: string; configKey?: string };
  isExpanded: boolean;
  onToggle: () => void;
}) {
  return (
    <div
      onClick={onToggle}
      className="rounded-lg border border-zinc-800/60 bg-zinc-900/30 hover:border-zinc-700 cursor-pointer transition-all p-2.5 space-y-1"
    >
      <div className="flex items-center justify-between gap-2">
        <span className="text-[10px] font-medium text-zinc-200">{choice.name}</span>
        <span className="text-[9px] font-mono text-emerald-400 bg-emerald-500/10 px-1.5 py-0.5 rounded shrink-0">
          {choice.currentValue}{choice.unit ? ` ${choice.unit}` : ""}
        </span>
      </div>
      {isExpanded && (
        <div className="space-y-1.5 pt-1.5 border-t border-zinc-800/40">
          <div className="text-[8px] text-zinc-500 leading-tight">{choice.tuningNotes}</div>
          {choice.alternatives && choice.alternatives.length > 0 && (
            <div>
              <div className="text-[7px] text-cyan-500/70 font-bold tracking-wider mb-0.5">ALTERNATIVES</div>
              {choice.alternatives.map((a, i) => (
                <div key={i} className="text-[8px] text-cyan-400/50 leading-tight">◦ {a}</div>
              ))}
            </div>
          )}
          <div className="flex items-center gap-2 pt-0.5">
            <span className="text-[7px] text-zinc-600">File:</span>
            <span className="text-[7px] font-mono text-zinc-500">{choice.configFile}</span>
            {choice.configKey && (
              <>
                <span className="text-[7px] text-zinc-700">→</span>
                <span className="text-[7px] font-mono text-zinc-500">{choice.configKey}</span>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

// ── Design choices section ──
function DesignChoicesSection({ expandedChoice, onToggleChoice }: {
  expandedChoice: string | null; onToggleChoice: (id: string) => void;
}) {
  return (
    <div className="rounded-xl border border-zinc-700/40 bg-zinc-900/20 p-4 space-y-3">
      <div>
        <div className="text-[10px] font-bold tracking-widest text-zinc-400 uppercase">Design Choices & Parameters</div>
        <div className="text-[8px] text-zinc-600 mt-0.5">Every configurable value. Click to expand for alternatives and tuning notes.</div>
      </div>
      {DESIGN_CHOICES.map(cat => (
        <div key={cat.category} className="space-y-1.5">
          <div className="flex items-center gap-1.5">
            <span className="text-sm">{cat.icon}</span>
            <span className="text-[9px] font-bold text-zinc-400 tracking-wider uppercase">{cat.category}</span>
            <span className="text-[8px] text-zinc-600">({cat.choices.length})</span>
          </div>
          <div className="grid grid-cols-2 gap-1.5 pl-5">
            {cat.choices.map(c => (
              <DesignChoiceCard
                key={c.id}
                choice={c}
                isExpanded={expandedChoice === c.id}
                onToggle={() => onToggleChoice(c.id)}
              />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

// ══════════════════════════════════════════════════════════
//  MAIN TAB
// ══════════════════════════════════════════════════════════

export default function PipelineTab() {
  const [expandedCard, setExpandedCard] = useState<string | null>(null);
  const [expandedChoice, setExpandedChoice] = useState<string | null>(null);

  const toggleCard = (id: string) => {
    setExpandedCard(prev => prev === id ? null : id);
  };
  const toggleChoice = (id: string) => {
    setExpandedChoice(prev => prev === id ? null : id);
  };

  const phases: { key: string; label: string; stages: Stage[] }[] = [
    { key: "pre-mission", label: "Pre-Mission", stages: PIPELINE.filter(s => s.phase === "pre-mission") },
    { key: "flight", label: "Flight", stages: PIPELINE.filter(s => s.phase === "flight") },
    { key: "action", label: "Action", stages: PIPELINE.filter(s => s.phase === "action") },
  ];

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-4">
      {/* Mission Goal */}
      <div className="rounded-xl border border-blue-500/30 bg-blue-500/5 p-4 space-y-3">
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-bold tracking-widest text-blue-400 uppercase">Mission Goal</span>
          <span className="text-[8px] text-zinc-600">{MISSION_GOAL.module} — {MISSION_GOAL.location}</span>
        </div>
        <p className="text-[11px] text-zinc-200 leading-relaxed">{MISSION_GOAL.holyGrail}</p>

        {/* Scene description */}
        <div className="space-y-1 pt-2 border-t border-blue-500/15">
          <div className="text-[8px] font-bold text-zinc-500 tracking-wider">THE SCENE</div>
          {MISSION_GOAL.scene.map((s, i) => (
            <div key={i} className="text-[9px] text-zinc-400 leading-tight">• {s}</div>
          ))}
        </div>

        {/* Rules grid */}
        <div className="pt-2 border-t border-blue-500/15">
          <div className="text-[8px] font-bold text-zinc-500 tracking-wider mb-1.5">REQUIREMENTS (from brief R2.1)</div>
          <div className="grid grid-cols-2 gap-x-4 gap-y-1">
            {MISSION_GOAL.rules.map(r => (
              <div key={r.id} className="flex items-start gap-1.5">
                <span className={`text-[7px] font-mono font-bold shrink-0 px-1 py-0.5 rounded ${
                  r.severity === "shall" ? "text-red-400 bg-red-500/10" : "text-amber-400 bg-amber-500/10"
                }`}>{r.id}</span>
                <span className="text-[8px] text-zinc-400 leading-tight">{r.text}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Constraints */}
        <div className="pt-2 border-t border-blue-500/15">
          <div className="text-[8px] font-bold text-zinc-500 tracking-wider mb-1">KEY CONSTRAINTS</div>
          <div className="flex flex-wrap gap-1.5">
            {MISSION_GOAL.constraints.map((c, i) => (
              <span key={i} className="text-[8px] text-zinc-400 bg-zinc-800/60 px-2 py-0.5 rounded">
                {c}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Design Choices */}
      <DesignChoicesSection expandedChoice={expandedChoice} onToggleChoice={toggleChoice} />

      {/* Pipeline title */}
      <div>
        <h1 className="text-[16px] font-semibold text-zinc-100">Mission Pipeline</h1>
        <p className="text-[10px] text-zinc-500 mt-0.5">
          Every stage of the SAR mission with all evaluated approaches. Click any card to expand.
          Green = selected. Blue = planned. Purple = research. Amber dependencies shown on expand.
        </p>
      </div>

      <PipelineSummary />

      {/* Pipeline */}
      {phases.map((phase, pi) => (
        <div key={phase.key} className="space-y-2">
          <PhaseHeader phase={phase.key} label={phase.label} />
          {phase.stages.map((stage, si) => (
            <div key={stage.id}>
              <StageRow stage={stage} expandedCard={expandedCard} onToggleCard={toggleCard} />
              {/* Connection line (except after last stage of last phase) */}
              {!(pi === phases.length - 1 && si === phase.stages.length - 1) && (
                <ConnectionLine phase={stage.phase} />
              )}
            </div>
          ))}
        </div>
      ))}

      {/* Legend */}
      <div className="flex items-center gap-4 px-4 py-2 bg-zinc-900/30 rounded-lg border border-zinc-800/30 mt-4">
        <span className="text-[9px] text-zinc-600 font-medium">LEGEND:</span>
        {(["selected", "available", "planned", "research", "rejected"] as ApproachStatus[]).map(s => (
          <div key={s} className="flex items-center gap-1">
            <div className={`w-2 h-2 rounded-sm ${STATUS_COLORS[s].bg} border ${STATUS_COLORS[s].border}`} />
            <span className={`text-[8px] ${STATUS_COLORS[s].text}`}>{STATUS_COLORS[s].label}</span>
          </div>
        ))}
        <div className="ml-auto text-[8px] text-zinc-600">Scores: speed / accuracy / reliability / simplicity / cost (1-5)</div>
      </div>
    </div>
  );
}
