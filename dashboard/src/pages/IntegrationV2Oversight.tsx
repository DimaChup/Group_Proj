/**
 * IntegrationOversight — Cross-Cutting Concerns + Integration View
 *
 * Shows concerns that span multiple SE layers: power budget, weight,
 * data throughput, latency chain, failsafe cascade.
 * Each card shows affected layers, owner, and status.
 */
import {
  INTEGRATION_OVERVIEW, TEAM, SE_LAYERS,
} from "./group-project-v2-data";
import { Badge } from "./GroupProjectV2Components";

const STATUS_STYLE: Record<string, { bg: string; border: string; text: string; label: string }> = {
  healthy:  { bg: "bg-emerald-500/5",  border: "border-emerald-500/20", text: "text-emerald-400", label: "Healthy" },
  "at-risk": { bg: "bg-amber-500/5",   border: "border-amber-500/20",   text: "text-amber-400",   label: "At Risk" },
  critical: { bg: "bg-red-500/5",      border: "border-red-500/20",     text: "text-red-400",     label: "Critical" },
};

export default function IntegrationOversight() {
  const integrator = TEAM.find(m => m.id === INTEGRATION_OVERVIEW.integrator);

  return (
    <div className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-4 mb-4">
      <div className="flex items-center justify-between mb-3">
        <div>
          <h3 className="text-[13px] font-bold text-zinc-100">Integration Oversight</h3>
          <p className="text-[10px] text-zinc-500">Cross-cutting concerns that span multiple SE layers. These need a system-level view, not just layer-by-layer.</p>
        </div>
        {integrator && (
          <div className="flex items-center gap-1.5 rounded border border-zinc-800 bg-zinc-950/50 px-2 py-1">
            <span className="text-[10px]">{integrator.icon}</span>
            <div>
              <div className="text-[9px] font-bold" style={{ color: integrator.color }}>System Integrator</div>
              <div className="text-[8px] text-zinc-500">{integrator.name}</div>
            </div>
          </div>
        )}
      </div>

      <div className="grid grid-cols-5 gap-2">
        {INTEGRATION_OVERVIEW.crossCuttingConcerns.map((cc, i) => {
          const style = STATUS_STYLE[cc.status];
          const owner = TEAM.find(m => m.id === cc.owner);
          return (
            <div key={i} className={`rounded-lg border ${style.border} ${style.bg} p-3`}>
              {/* Header */}
              <div className="flex items-center justify-between mb-2">
                <h4 className="text-[10px] font-bold text-zinc-200">{cc.concern}</h4>
                <span className={`text-[7px] font-bold uppercase px-1.5 py-0.5 rounded ${style.text}`}
                  style={{ background: style.text.replace("text-", "").replace("400", "500") + "15" }}>
                  {style.label}
                </span>
              </div>

              {/* Detail */}
              <p className="text-[8px] text-zinc-500 leading-relaxed mb-2">{cc.detail}</p>

              {/* Affected layers */}
              <div className="mb-2">
                <span className="text-[7px] text-zinc-600 uppercase tracking-wider">Layers:</span>
                <div className="flex flex-wrap gap-1 mt-0.5">
                  {cc.affectedLayers.map(layerId => {
                    const layer = SE_LAYERS.find(l => l.id === layerId);
                    if (!layer) return null;
                    return (
                      <span key={layerId} className="text-[7px] px-1 py-0.5 rounded"
                        style={{ background: layer.color + "15", color: layer.color, border: `1px solid ${layer.color}25` }}>
                        L{layer.number}
                      </span>
                    );
                  })}
                </div>
              </div>

              {/* Owner */}
              {owner && (
                <div className="flex items-center gap-1 text-[8px] pt-1 border-t border-zinc-800/30">
                  <span>{owner.icon}</span>
                  <span style={{ color: owner.color }}>{owner.name}</span>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Integration duties summary */}
      <div className="mt-3 pt-3 border-t border-zinc-800/50">
        <h4 className="text-[10px] font-bold text-zinc-400 uppercase tracking-wider mb-2">Integration Responsibilities</h4>
        <div className="grid grid-cols-5 gap-2">
          {TEAM.map(member => (
            <div key={member.id} className="text-[8px]">
              <div className="flex items-center gap-1 mb-1">
                <span>{member.icon}</span>
                <span className="font-semibold" style={{ color: member.color }}>{member.name}</span>
              </div>
              <ul className="space-y-0.5">
                {member.integrationDuties.map((duty, j) => (
                  <li key={j} className="text-zinc-500 leading-tight flex items-start gap-1">
                    <span className="text-zinc-700 shrink-0">{"\u2022"}</span>{duty}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
