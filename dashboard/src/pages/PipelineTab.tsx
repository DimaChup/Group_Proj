import { useState } from "react";
import {
  PIPELINE, PHASE_COLORS, STATUS_COLORS, SCORE_LABELS,
  type Stage, type Approach, type ApproachStatus,
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

        {/* Expanded: pros/cons */}
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

// ══════════════════════════════════════════════════════════
//  MAIN TAB
// ══════════════════════════════════════════════════════════

export default function PipelineTab() {
  const [expandedCard, setExpandedCard] = useState<string | null>(null);

  const toggleCard = (id: string) => {
    setExpandedCard(prev => prev === id ? null : id);
  };

  const phases: { key: string; label: string; stages: Stage[] }[] = [
    { key: "pre-mission", label: "Pre-Mission", stages: PIPELINE.filter(s => s.phase === "pre-mission") },
    { key: "flight", label: "Flight", stages: PIPELINE.filter(s => s.phase === "flight") },
    { key: "action", label: "Action", stages: PIPELINE.filter(s => s.phase === "action") },
  ];

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-4">
      {/* Title */}
      <div>
        <h1 className="text-[16px] font-semibold text-zinc-100">Mission Pipeline</h1>
        <p className="text-[10px] text-zinc-500 mt-0.5">
          Every stage of the SAR mission with all evaluated approaches. Click any card to expand.
          Green = our current selection. Blue = planned improvement. Purple = research.
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
