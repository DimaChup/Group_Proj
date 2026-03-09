/**
 * BigPictureView — Level Pathway + Progress Stats
 *
 * Shows L1 → L2 → L3 as connected cards with bridge items between them,
 * plus progress stats (decisions locked, current phase).
 */
import {
  LEVELS, LEVEL_PATHWAY, DECISION_TREE, DESIGN_PHASES,
  type AmbitionLevel,
} from "./group-project-v2-data";

interface BigPictureViewProps {
  activeLevel: number;
  onSelectLevel: (id: number) => void;
}

export default function BigPictureView({ activeLevel, onSelectLevel }: BigPictureViewProps) {
  const locked = DECISION_TREE.filter(n => n.status === "locked").length;
  const total = DECISION_TREE.length;
  const currentPhase = DESIGN_PHASES.find(p => p.status === "active");

  return (
    <div className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-4 mb-4">
      <div className="flex items-center justify-between mb-3">
        <div>
          <h3 className="text-[13px] font-bold text-zinc-100">Mission Pathway</h3>
          <p className="text-[10px] text-zinc-500">How each level builds toward the Holy Grail. Click a level to focus.</p>
        </div>
        {/* Progress stats */}
        <div className="flex gap-3">
          <div className="rounded border border-zinc-800 bg-zinc-950/50 px-2.5 py-1.5 text-center">
            <div className="text-[14px] font-bold text-emerald-400">{locked}/{total}</div>
            <div className="text-[8px] text-zinc-500 uppercase">Decisions Locked</div>
          </div>
          {currentPhase && (
            <div className="rounded border border-amber-500/30 bg-amber-500/5 px-2.5 py-1.5 text-center">
              <div className="text-[11px] font-bold text-amber-400">{currentPhase.name}</div>
              <div className="text-[8px] text-zinc-500 uppercase">Current Phase</div>
            </div>
          )}
        </div>
      </div>

      {/* Level Pathway */}
      <div className="flex items-stretch gap-0">
        {LEVELS.map((level, i) => {
          const isActive = level.id === activeLevel;
          const bridge = LEVEL_PATHWAY.find(b => b.from === level.id);
          const isLast = i === LEVELS.length - 1;

          return (
            <div key={level.id} className="flex items-stretch flex-1">
              {/* Level card */}
              <button
                onClick={() => onSelectLevel(level.id)}
                className={`flex-1 rounded-lg border p-3 text-left transition-all ${
                  isActive
                    ? "border-zinc-500 bg-zinc-800/80 shadow-lg shadow-zinc-900"
                    : level.id < activeLevel
                    ? "border-emerald-500/20 bg-emerald-500/5 hover:bg-emerald-500/10"
                    : "border-zinc-800 bg-zinc-950/30 hover:bg-zinc-800/30 opacity-60"
                }`}>
                <div className="flex items-center gap-2 mb-1.5">
                  <div className="w-2.5 h-2.5 rounded-full" style={{ background: isActive ? level.color : level.id < activeLevel ? "#22c55e" : "#3f3f46" }} />
                  <span className={`text-[11px] font-bold ${isActive ? "text-zinc-100" : level.id < activeLevel ? "text-emerald-400" : "text-zinc-500"}`}>
                    L{level.id}: {level.name}
                  </span>
                </div>
                <p className={`text-[9px] leading-relaxed ${isActive ? "text-zinc-400" : "text-zinc-600"}`}>{level.subtitle}</p>
                <div className="mt-2 flex items-center gap-1">
                  {level.id < activeLevel && (
                    <span className="text-[8px] px-1.5 py-0.5 rounded bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">{"\u2713"} Complete</span>
                  )}
                  {isActive && (
                    <span className="text-[8px] px-1.5 py-0.5 rounded bg-amber-500/15 text-amber-400 border border-amber-500/30">{"\u25CF"} Active</span>
                  )}
                  {level.id > activeLevel && (
                    <span className="text-[8px] px-1.5 py-0.5 rounded bg-zinc-800 text-zinc-600">Upcoming</span>
                  )}
                </div>
                {/* Approach count */}
                <div className="mt-1.5 text-[8px] text-zinc-600">
                  {level.approaches.length} approaches {"\u00B7"} {Object.keys(level.baseLayers).length + level.approaches.reduce((sum, a) => sum + Object.keys(a.layerOverrides).length, 0)} layer specs
                </div>
              </button>

              {/* Bridge arrow between levels */}
              {!isLast && bridge && (
                <div className="flex flex-col items-center justify-center px-2 min-w-[120px]">
                  <div className="w-full relative">
                    {/* Arrow line */}
                    <div className="absolute top-1/2 left-0 right-0 h-px bg-zinc-700" />
                    <div className="absolute top-1/2 right-0 -translate-y-1/2">
                      <span className="text-zinc-600 text-[10px]">{"\u25B6"}</span>
                    </div>
                  </div>
                  {/* Bridge items */}
                  <div className="mt-1 space-y-0.5 w-full">
                    {bridge.bridges.slice(0, 3).map((b, j) => (
                      <div key={j} className="text-[7px] text-zinc-500 leading-tight truncate px-1 py-0.5 rounded bg-zinc-900/50 border border-zinc-800/30">
                        {b}
                      </div>
                    ))}
                    {bridge.bridges.length > 3 && (
                      <div className="text-[7px] text-zinc-600 px-1">+{bridge.bridges.length - 3} more</div>
                    )}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
