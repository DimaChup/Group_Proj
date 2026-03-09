/**
 * MissionReadiness — Equipment Tiers + Emergency Procedures + Risk Matrix
 *
 * Three collapsible sections:
 *   1. Equipment Requirements (must-have / nice-to-have / stretch)
 *   2. Emergency Procedures (realistic failsafe protocols)
 *   3. Risk Matrix (likelihood x impact with mitigations)
 */
import { useState, useMemo } from "react";
import {
  TIERED_REQUIREMENTS, EMERGENCY_PROCEDURES, MISSION_RISKS, TEAM,
  type RequirementTier, type EmergencyProcedure, type MissionRisk,
} from "./group-project-v2-data";
import { Badge } from "./GroupProjectV2Components";

const TIER_STYLE: Record<RequirementTier, { color: string; label: string; icon: string }> = {
  "must-have":    { color: "#ef4444", label: "Must-Have",    icon: "\u{1F534}" },
  "nice-to-have": { color: "#eab308", label: "Nice-to-Have", icon: "\u{1F7E1}" },
  "stretch":      { color: "#3b82f6", label: "Stretch",      icon: "\u{1F535}" },
};

const SEVERITY_STYLE: Record<string, { color: string; bg: string }> = {
  critical: { color: "#ef4444", bg: "bg-red-500/8" },
  warning:  { color: "#eab308", bg: "bg-amber-500/8" },
  caution:  { color: "#06b6d4", bg: "bg-cyan-500/8" },
};

const CAT_COLORS: Record<string, string> = {
  hardware: "#f97316", software: "#3b82f6", "ground-station": "#22c55e", safety: "#ef4444", operations: "#a855f7",
};

function SectionToggle({ title, icon, count, open, onToggle }: { title: string; icon: string; count: number; open: boolean; onToggle: () => void }) {
  return (
    <button onClick={onToggle}
      className={`w-full flex items-center gap-2 px-3 py-2.5 text-left rounded-lg border transition-all ${open ? "bg-zinc-800/60 border-zinc-700" : "bg-zinc-900/40 border-zinc-800 hover:bg-zinc-800/30"}`}>
      <span className="text-[12px]">{icon}</span>
      <span className="text-[11px] font-bold text-zinc-200 flex-1">{title}</span>
      <span className="text-[9px] text-zinc-500">{count} items</span>
      <span className="text-zinc-600 text-[10px]">{open ? "\u25B2" : "\u25BC"}</span>
    </button>
  );
}

// ═══════════════════════════════════════════════════════════
// Equipment Requirements
// ═══════════════════════════════════════════════════════════

function EquipmentSection({ activeLevel }: { activeLevel: number }) {
  const [filterTier, setFilterTier] = useState<RequirementTier | null>(null);

  const filtered = useMemo(() => {
    let items = TIERED_REQUIREMENTS.filter(r => r.levelNeeded <= activeLevel);
    if (filterTier) items = items.filter(r => r.tier === filterTier);
    return items;
  }, [activeLevel, filterTier]);

  const tiers = Object.keys(TIER_STYLE) as RequirementTier[];

  return (
    <div className="space-y-3">
      {/* Tier filters */}
      <div className="flex gap-1">
        {tiers.map(t => {
          const style = TIER_STYLE[t];
          const count = TIERED_REQUIREMENTS.filter(r => r.tier === t && r.levelNeeded <= activeLevel).length;
          const active = filterTier === t;
          return (
            <button key={t} onClick={() => setFilterTier(active ? null : t)}
              className={`flex items-center gap-1 px-2 py-1 rounded text-[9px] transition-all border ${
                active ? "border-zinc-600 bg-zinc-800" : "border-zinc-800/50 bg-zinc-950/30 hover:bg-zinc-800/30"
              }`}>
              <span className="text-[8px]">{style.icon}</span>
              <span style={{ color: active ? style.color : "#71717a" }}>{style.label}</span>
              <span className="text-zinc-600 text-[8px]">({count})</span>
            </button>
          );
        })}
      </div>

      {/* Items grouped by category */}
      {(["safety", "hardware", "software", "ground-station", "operations"] as const).map(cat => {
        const catItems = filtered.filter(r => r.category === cat);
        if (catItems.length === 0) return null;
        return (
          <div key={cat}>
            <h5 className="text-[9px] font-bold uppercase tracking-wider mb-1.5 capitalize" style={{ color: CAT_COLORS[cat] }}>{cat.replace("-", " ")}</h5>
            <div className="space-y-1">
              {catItems.map((req, i) => {
                const tierStyle = TIER_STYLE[req.tier];
                return (
                  <div key={i} className="flex items-start gap-2 rounded border border-zinc-800/30 bg-zinc-950/20 px-2 py-1.5"
                    style={{ borderLeftColor: tierStyle.color, borderLeftWidth: 2 }}>
                    <div className="flex-1">
                      <div className="flex items-center gap-1.5">
                        <span className="text-[9px] font-semibold text-zinc-200">{req.item}</span>
                        <span className="text-[7px] px-1 py-0.5 rounded" style={{ background: tierStyle.color + "15", color: tierStyle.color }}>
                          L{req.levelNeeded}+
                        </span>
                      </div>
                      <p className="text-[8px] text-zinc-500 mt-0.5 leading-relaxed">{req.rationale}</p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        );
      })}

      {/* Summary counts */}
      <div className="flex gap-3 pt-2 border-t border-zinc-800/30">
        {tiers.map(t => {
          const style = TIER_STYLE[t];
          const count = TIERED_REQUIREMENTS.filter(r => r.tier === t && r.levelNeeded <= activeLevel).length;
          return (
            <div key={t} className="flex items-center gap-1 text-[8px]">
              <span>{style.icon}</span>
              <span className="font-bold" style={{ color: style.color }}>{count}</span>
              <span className="text-zinc-600">{style.label}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════
// Emergency Procedures
// ═══════════════════════════════════════════════════════════

function EmergencySection({ activeLevel }: { activeLevel: number }) {
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const procedures = EMERGENCY_PROCEDURES.filter(p => p.levelApplicable.includes(activeLevel));

  return (
    <div className="space-y-1.5">
      <div className="rounded border border-red-500/20 bg-red-500/5 px-2 py-1.5 mb-2">
        <p className="text-[9px] text-red-300 font-semibold">
          {"\u26A0"} RC override ALWAYS takes priority over autonomous commands. At any point, the pilot can switch to STABILIZE (manual) or hit the KILL SWITCH.
        </p>
      </div>

      {procedures.map(proc => {
        const isOpen = expandedId === proc.id;
        const sev = SEVERITY_STYLE[proc.severity];
        return (
          <div key={proc.id} className={`rounded-lg border overflow-hidden ${isOpen ? "border-zinc-600" : "border-zinc-800/50"}`}>
            <button onClick={() => setExpandedId(isOpen ? null : proc.id)}
              className={`w-full flex items-center gap-2 px-3 py-2 text-left transition-all ${sev.bg}`}>
              <span className="text-[10px]" style={{ color: sev.color }}>
                {proc.severity === "critical" ? "\u{1F6A8}" : proc.severity === "warning" ? "\u26A0" : "\u{2139}"}
              </span>
              <span className="text-[10px] font-bold text-zinc-200 flex-1">{proc.trigger}</span>
              <Badge text={proc.severity} color={sev.color} />
              <span className="text-zinc-600 text-[10px]">{isOpen ? "\u25B2" : "\u25BC"}</span>
            </button>

            {isOpen && (
              <div className="px-3 pb-3 pt-2 border-t border-zinc-800/30 space-y-2">
                {/* Immediate action */}
                <div className="rounded border border-amber-500/30 bg-amber-500/8 px-2 py-1.5">
                  <span className="text-[8px] text-amber-400 font-bold uppercase">Immediate Action: </span>
                  <span className="text-[9px] text-zinc-200 font-semibold">{proc.immediateAction}</span>
                </div>

                {/* Steps */}
                <div>
                  <h6 className="text-[8px] font-bold text-zinc-500 uppercase tracking-wider mb-1">Procedure</h6>
                  <ol className="space-y-1">
                    {proc.steps.map((step, i) => (
                      <li key={i} className="flex items-start gap-2 text-[9px]">
                        <span className="text-zinc-500 font-mono shrink-0 mt-px">{i + 1}.</span>
                        <span className="text-zinc-400 leading-relaxed">{step}</span>
                      </li>
                    ))}
                  </ol>
                </div>

                {/* Outcome */}
                <div className="rounded bg-emerald-500/8 border border-emerald-500/20 px-2 py-1.5">
                  <span className="text-[8px] text-emerald-400 font-bold uppercase">Expected Outcome: </span>
                  <span className="text-[9px] text-zinc-300">{proc.outcome}</span>
                </div>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════
// Risk Matrix
// ═══════════════════════════════════════════════════════════

function RiskSection({ activeLevel }: { activeLevel: number }) {
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const risks = MISSION_RISKS.filter(r => r.levelApplicable.includes(activeLevel))
    .sort((a, b) => (b.likelihood * b.impact) - (a.likelihood * a.impact));

  const riskColor = (score: number) =>
    score >= 15 ? "#ef4444" : score >= 9 ? "#f97316" : score >= 4 ? "#eab308" : "#22c55e";

  return (
    <div className="space-y-2">
      {/* Risk heatmap summary */}
      <div className="grid grid-cols-5 gap-px rounded overflow-hidden border border-zinc-800">
        {/* Header row */}
        <div className="bg-zinc-900 p-1 text-[7px] text-zinc-500 text-center" />
        {[1, 2, 3, 4, 5].map(impact => (
          <div key={impact} className="bg-zinc-900 p-1 text-[7px] text-zinc-500 text-center">I:{impact}</div>
        ))}
        {/* Grid cells */}
        {[5, 4, 3, 2, 1].map(likelihood => (
          <>
            <div key={`l${likelihood}`} className="bg-zinc-900 p-1 text-[7px] text-zinc-500 text-center">L:{likelihood}</div>
            {[1, 2, 3, 4, 5].map(impact => {
              const score = likelihood * impact;
              const count = risks.filter(r => r.likelihood === likelihood && r.impact === impact).length;
              return (
                <div key={`${likelihood}-${impact}`}
                  className="p-1 text-center text-[8px] font-bold"
                  style={{ background: riskColor(score) + (count > 0 ? "30" : "08"), color: count > 0 ? riskColor(score) : "#3f3f46" }}>
                  {count > 0 ? count : ""}
                </div>
              );
            })}
          </>
        ))}
      </div>
      <div className="flex gap-2 text-[7px]">
        <span className="text-zinc-600">L = Likelihood, I = Impact</span>
        <span className="text-emerald-500">Low</span>
        <span className="text-amber-500">Medium</span>
        <span className="text-orange-500">High</span>
        <span className="text-red-500">Critical</span>
      </div>

      {/* Risk items */}
      <div className="space-y-1">
        {risks.map(risk => {
          const score = risk.likelihood * risk.impact;
          const color = riskColor(score);
          const isOpen = expandedId === risk.id;
          const owner = TEAM.find(m => m.id === risk.owner);
          return (
            <div key={risk.id} className="rounded border border-zinc-800/50 overflow-hidden"
              style={{ borderLeftColor: color, borderLeftWidth: 2 }}>
              <button onClick={() => setExpandedId(isOpen ? null : risk.id)}
                className={`w-full flex items-center gap-2 px-2 py-1.5 text-left ${isOpen ? "bg-zinc-800/40" : "bg-zinc-950/20 hover:bg-zinc-800/20"}`}>
                <span className="text-[10px] font-bold font-mono min-w-[20px] text-center" style={{ color }}>
                  {score}
                </span>
                <span className="text-[9px] text-zinc-300 flex-1">{risk.risk}</span>
                <Badge text={risk.category} color={CAT_COLORS[risk.category === "environmental" ? "operations" : risk.category === "technical" ? "software" : risk.category] || "#71717a"} />
                {owner && <span className="text-[9px]">{owner.icon}</span>}
                <span className="text-zinc-600 text-[9px]">{isOpen ? "\u25B2" : "\u25BC"}</span>
              </button>

              {isOpen && (
                <div className="px-2 pb-2 pt-1 border-t border-zinc-800/30 space-y-1.5">
                  <div className="flex gap-3 text-[8px]">
                    <span className="text-zinc-500">Likelihood: <span className="font-bold text-zinc-300">{risk.likelihood}/5</span></span>
                    <span className="text-zinc-500">Impact: <span className="font-bold text-zinc-300">{risk.impact}/5</span></span>
                    <span className="text-zinc-500">Score: <span className="font-bold" style={{ color }}>{score}</span></span>
                  </div>
                  <div>
                    <span className="text-[8px] text-emerald-400 font-bold">Mitigation: </span>
                    <span className="text-[8px] text-zinc-400">{risk.mitigation}</span>
                  </div>
                  <div>
                    <span className="text-[8px] text-amber-400 font-bold">Residual: </span>
                    <span className="text-[8px] text-zinc-500">{risk.residualRisk}</span>
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

// ═══════════════════════════════════════════════════════════
// Main Component
// ═══════════════════════════════════════════════════════════

interface MissionReadinessProps {
  activeLevel: number;
}

export default function MissionReadiness({ activeLevel }: MissionReadinessProps) {
  const [openSections, setOpenSections] = useState<Set<string>>(new Set(["equipment"]));

  const toggle = (id: string) => {
    setOpenSections(prev => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id); else next.add(id);
      return next;
    });
  };

  const equipCount = TIERED_REQUIREMENTS.filter(r => r.levelNeeded <= activeLevel).length;
  const emergCount = EMERGENCY_PROCEDURES.filter(p => p.levelApplicable.includes(activeLevel)).length;
  const riskCount = MISSION_RISKS.filter(r => r.levelApplicable.includes(activeLevel)).length;

  return (
    <div className="space-y-2 mb-4">
      {/* Equipment */}
      <div>
        <SectionToggle title="Equipment Requirements" icon={"\u{1F4CB}"} count={equipCount}
          open={openSections.has("equipment")} onToggle={() => toggle("equipment")} />
        {openSections.has("equipment") && (
          <div className="mt-1 rounded-lg border border-zinc-800 bg-zinc-900/60 p-4">
            <EquipmentSection activeLevel={activeLevel} />
          </div>
        )}
      </div>

      {/* Emergency Procedures */}
      <div>
        <SectionToggle title="Emergency Procedures" icon={"\u{1F6A8}"} count={emergCount}
          open={openSections.has("emergency")} onToggle={() => toggle("emergency")} />
        {openSections.has("emergency") && (
          <div className="mt-1 rounded-lg border border-zinc-800 bg-zinc-900/60 p-4">
            <EmergencySection activeLevel={activeLevel} />
          </div>
        )}
      </div>

      {/* Risk Matrix */}
      <div>
        <SectionToggle title="Risk Matrix" icon={"\u{26A0}"} count={riskCount}
          open={openSections.has("risk")} onToggle={() => toggle("risk")} />
        {openSections.has("risk") && (
          <div className="mt-1 rounded-lg border border-zinc-800 bg-zinc-900/60 p-4">
            <RiskSection activeLevel={activeLevel} />
          </div>
        )}
      </div>
    </div>
  );
}
