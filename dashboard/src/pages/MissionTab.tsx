/**
 * MissionTab — The "What": scenario, requirements, constraints, hardware, deliverables
 * Comprehensive view with expandable sections, pulling from AENGM0074 brief
 */
import { useState } from "react";
import { MISSION, HARDWARE, DELIVERABLES, STATUS_COLORS } from "./mission-data";

const SEVERITY_STYLE = {
  critical: { color: "#ef4444", bg: "rgba(239,68,68,0.08)", border: "rgba(239,68,68,0.2)" },
  warning:  { color: "#f59e0b", bg: "rgba(245,158,11,0.08)", border: "rgba(245,158,11,0.2)" },
  info:     { color: "#3b82f6", bg: "rgba(59,130,246,0.08)", border: "rgba(59,130,246,0.2)" },
  shall:    { color: "#ef4444", bg: "rgba(239,68,68,0.06)", border: "rgba(239,68,68,0.15)" },
  should:   { color: "#f59e0b", bg: "rgba(245,158,11,0.06)", border: "rgba(245,158,11,0.15)" },
};

type SectionId = "scenario" | "requirements" | "constraints" | "hardware" | "deliverables" | "success";

export default function MissionTab() {
  const [expanded, setExpanded] = useState<Set<SectionId>>(new Set(["scenario", "requirements"]));

  const toggle = (id: SectionId) => {
    setExpanded(prev => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  const Section = ({ id, title, count, children }: { id: SectionId; title: string; count?: number; children: React.ReactNode }) => (
    <div className="rounded-lg border border-zinc-800/50 overflow-hidden">
      <button onClick={() => toggle(id)}
        className="w-full flex items-center gap-3 px-4 py-3 bg-zinc-900/50 hover:bg-zinc-800/30 transition-all text-left">
        <span className="text-[9px] text-zinc-600">{expanded.has(id) ? "\u25BC" : "\u25B6"}</span>
        <span className="text-[11px] font-bold text-zinc-200">{title}</span>
        {count !== undefined && <span className="text-[8px] text-zinc-600 ml-auto">{count} items</span>}
      </button>
      {expanded.has(id) && <div className="px-4 pb-4 pt-2">{children}</div>}
    </div>
  );

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-4 min-w-0">
      {/* Holy Grail */}
      <div className="rounded-lg border border-amber-500/20 bg-amber-500/5 p-5">
        <div className="text-[9px] text-amber-500 uppercase tracking-widest font-bold mb-1">The Mission</div>
        <div className="text-[14px] text-amber-200 font-medium leading-relaxed">{MISSION.holyGrail}</div>
        <div className="flex flex-wrap gap-x-4 gap-y-1 mt-3 text-[9px] text-zinc-500">
          <span>{MISSION.module}</span>
          <span>{MISSION.briefVersion}</span>
          <span>{MISSION.location}</span>
          <span>Team of {MISSION.teamSize}</span>
        </div>
      </div>

      {/* Field map — Fenswood Farm operational area */}
      <div className="rounded-lg border border-zinc-800/50 overflow-hidden">
        <div className="px-4 py-2 bg-zinc-900/50 flex items-center gap-2">
          <span className="text-[10px] font-bold text-zinc-200">Fenswood Farm — Operational Area</span>
          <span className="text-[8px] text-zinc-600 ml-auto">Green=flight area, Cyan=survey area, Orange=SSSI no-fly, Pink=PLB focus area</span>
        </div>
        <img src="/field-map.jpg" alt="Fenswood Farm field map showing flight area, survey area, SSSI no-fly zone, and PLB focus area"
          className="w-full max-h-[350px] object-contain bg-zinc-900" />
      </div>

      {/* Objectives — always visible */}
      <div>
        <h2 className="text-[11px] font-bold text-zinc-200 mb-2">Mission Objectives</h2>
        <div className="grid grid-cols-4 gap-2">
          {MISSION.objectives.map(obj => (
            <div key={obj.id} className="rounded-lg bg-zinc-900/50 border border-zinc-800/50 p-3">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-[14px] font-bold text-zinc-400">{obj.icon}</span>
                <span className="text-[10px] font-bold text-zinc-200">{obj.label}</span>
              </div>
              <div className="text-[8px] text-zinc-500 leading-relaxed">{obj.description}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Scenario */}
      <Section id="scenario" title="Mission Scenario" count={MISSION.scenario.length}>
        <div className="space-y-1.5">
          {MISSION.scenario.map((s, i) => (
            <div key={i} className="flex gap-2 text-[9px]">
              <span className="text-zinc-600 shrink-0 w-4 text-right">{i + 1}.</span>
              <span className="text-zinc-400 leading-relaxed">{s}</span>
            </div>
          ))}
        </div>
      </Section>

      {/* Requirements R01-R12 */}
      <Section id="requirements" title="Formal Requirements (R01-R12)" count={MISSION.requirements.length}>
        <div className="space-y-1">
          {MISSION.requirements.map(r => {
            const s = SEVERITY_STYLE[r.severity];
            return (
              <div key={r.id} className="flex items-start gap-3 px-3 py-2 rounded"
                style={{ background: s.bg, border: `1px solid ${s.border}` }}>
                <span className="text-[9px] font-bold shrink-0 w-7 mt-0.5" style={{ color: s.color }}>{r.id}</span>
                <div className="flex-1 min-w-0">
                  <div className="text-[9px] text-zinc-300 leading-relaxed">{r.text}</div>
                  {r.notes && <div className="text-[8px] text-zinc-600 mt-0.5">{r.notes}</div>}
                </div>
                <span className="text-[7px] font-bold uppercase shrink-0 px-1.5 py-0.5 rounded"
                  style={{ color: s.color, background: s.color + "15" }}>
                  {r.severity}
                </span>
              </div>
            );
          })}
        </div>
      </Section>

      <div className="grid grid-cols-2 gap-4">
        {/* Constraints */}
        <Section id="constraints" title="Constraints" count={MISSION.constraints.length}>
          <div className="space-y-1">
            {MISSION.constraints.map(c => {
              const s = SEVERITY_STYLE[c.severity];
              return (
                <div key={c.label} className="flex items-start gap-2 px-3 py-2 rounded"
                  style={{ background: s.bg, border: `1px solid ${s.border}` }}>
                  <div className="w-1.5 h-1.5 rounded-full mt-1.5 shrink-0" style={{ background: s.color }} />
                  <div>
                    <div className="text-[9px] font-medium" style={{ color: s.color }}>{c.label}</div>
                    <div className="text-[8px] text-zinc-500">{c.description}</div>
                  </div>
                </div>
              );
            })}
          </div>
        </Section>

        {/* Success Criteria */}
        <Section id="success" title="Success Criteria" count={MISSION.successCriteria.length}>
          <div className="space-y-1.5">
            {MISSION.successCriteria.map((sc, i) => (
              <div key={i} className="flex items-center gap-3 px-3 py-2 rounded bg-zinc-900/30 border border-zinc-800/30">
                <span className="text-[11px] text-zinc-700 w-4 shrink-0">{i + 1}</span>
                <div>
                  <div className="text-[9px] text-zinc-200">{sc.label}</div>
                  <div className="text-[8px] text-zinc-500">{sc.metric}</div>
                </div>
              </div>
            ))}
          </div>
        </Section>
      </div>

      {/* Hardware */}
      <Section id="hardware" title="Hardware Platform" count={HARDWARE.length}>
        <div className="space-y-0.5">
          {HARDWARE.map(hw => {
            const sc = STATUS_COLORS[hw.status] || STATUS_COLORS.todo;
            return (
              <div key={hw.name} className="flex items-center gap-2 px-3 py-1.5 rounded hover:bg-zinc-800/30 group">
                <div className="w-1.5 h-1.5 rounded-full shrink-0" style={{ background: sc.color }} />
                <span className="text-[9px] text-zinc-200 w-36 shrink-0 font-medium">{hw.name}</span>
                <span className="text-[8px] text-zinc-500 w-28 shrink-0">{hw.role}</span>
                <span className="text-[8px] text-zinc-600 truncate flex-1">{hw.details}</span>
                <span className="text-[7px] px-1.5 py-0.5 rounded shrink-0"
                  style={{ color: sc.color, background: sc.bg }}>
                  {hw.status}
                </span>
              </div>
            );
          })}
        </div>
      </Section>

      {/* Deliverables */}
      <Section id="deliverables" title="Deliverables (D1-D7)" count={DELIVERABLES.length}>
        <div className="space-y-1.5">
          {DELIVERABLES.map(d => {
            const sc = STATUS_COLORS[d.status] || STATUS_COLORS.todo;
            return (
              <div key={d.id} className="flex items-center gap-3 px-3 py-2.5 rounded bg-zinc-900/30 border border-zinc-800/30">
                <span className="text-[10px] font-bold text-zinc-400 w-6 shrink-0">{d.id}</span>
                <div className="flex-1 min-w-0">
                  <div className="text-[10px] text-zinc-200 font-medium">{d.name}</div>
                  <div className="text-[8px] text-zinc-500 mt-0.5">{d.description}</div>
                </div>
                <div className="text-right shrink-0">
                  <div className="text-[8px] text-zinc-500">{d.date}</div>
                  <div className="text-[9px] font-bold" style={{ color: sc.color }}>{d.weight}</div>
                </div>
                <span className="text-[7px] px-1.5 py-0.5 rounded shrink-0 w-14 text-center"
                  style={{ color: sc.color, background: sc.bg }}>
                  {d.status}
                </span>
              </div>
            );
          })}
        </div>
      </Section>
    </div>
  );
}
