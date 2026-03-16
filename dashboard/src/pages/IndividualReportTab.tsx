import { useState } from "react";
import {
  REPORT_META,
  RUBRIC,
  REPORT_SECTIONS,
  PAGE_BUDGET,
  TOP_MARK_STRATEGIES,
  STATUS_COLORS,
  type SectionStatus,
  type Criterion,
  type ReportSection,
} from "./individual-report-data";

// ── Status badge ──
function StatusBadge({ status }: { status: SectionStatus }) {
  const s = STATUS_COLORS[status];
  return (
    <span className={`text-[7px] font-bold tracking-wider px-1.5 py-0.5 rounded ${s.bg} ${s.text}`}>
      {s.label}
    </span>
  );
}

// ── Page budget bar colors ──
const BUDGET_COLORS = [
  { bg: "bg-rose-500", label: "text-rose-200" },
  { bg: "bg-violet-500", label: "text-violet-200" },
  { bg: "bg-cyan-500", label: "text-cyan-200" },
  { bg: "bg-amber-500", label: "text-amber-200" },
  { bg: "bg-emerald-500", label: "text-emerald-200" },
];

// ── Criterion color mapping ──
function criterionColor(name: string): string {
  if (name.includes("Teamwork")) return "text-violet-400";
  if (name.includes("Self-Management")) return "text-amber-400";
  if (name.includes("Insight")) return "text-cyan-400";
  return "text-zinc-400";
}

function criterionBorder(name: string): string {
  if (name.includes("Teamwork")) return "border-violet-500/30";
  if (name.includes("Self-Management")) return "border-amber-500/30";
  if (name.includes("Insight")) return "border-cyan-500/30";
  return "border-zinc-700/30";
}

function criterionBg(name: string): string {
  if (name.includes("Teamwork")) return "bg-violet-900/10";
  if (name.includes("Self-Management")) return "bg-amber-900/10";
  if (name.includes("Insight")) return "bg-cyan-900/10";
  return "bg-zinc-900/10";
}

export default function IndividualReportTab() {
  // Collapse state: sets of expanded IDs
  const [expandedBands, setExpandedBands] = useState<Set<string>>(new Set());
  const [expandedOutlines, setExpandedOutlines] = useState<Set<string>>(new Set());
  const [expandedEvidence, setExpandedEvidence] = useState<Set<string>>(new Set());
  const [expandedPrompts, setExpandedPrompts] = useState<Set<string>>(new Set());

  const toggleSet = (set: Set<string>, id: string, setter: (s: Set<string>) => void) => {
    const next = new Set(set);
    if (next.has(id)) next.delete(id);
    else next.add(id);
    setter(next);
  };

  // Which rubric bands to show by default (top 2)
  const isTopBand = (range: string) => range.includes("72") || range.includes("83");

  // Collect all reflection prompts across criteria
  const allPrompts = RUBRIC.map(crit => ({
    criterion: crit.name,
    ahep: crit.ahep,
    prompts: crit.reflectionPrompts,
  }));

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-6 min-w-0">

      {/* 1. HEADER */}
      <div className="rounded-xl border border-zinc-700/40 bg-zinc-900/60 p-5">
        <div className="flex items-baseline gap-3 mb-2">
          <span className="text-[10px] font-bold tracking-wider text-zinc-500 bg-zinc-800 px-2 py-0.5 rounded">
            {REPORT_META.code}
          </span>
          <h1 className="text-[22px] font-bold text-zinc-100 leading-none">
            {REPORT_META.title}
          </h1>
        </div>
        <div className="flex flex-wrap gap-x-6 gap-y-1 text-[11px] text-zinc-400">
          <span>
            Weight: <span className="text-amber-400 font-bold">{REPORT_META.weight}</span>
          </span>
          <span>
            Page limit: <span className="text-cyan-400 font-bold">{REPORT_META.pageLimit}</span>
          </span>
          <span>
            Due: <span className="text-red-400 font-bold">{REPORT_META.due}</span>
          </span>
          <span>
            Format: <span className="text-zinc-300">{REPORT_META.format}</span>
          </span>
        </div>
        <div className="mt-2 text-[9px] text-zinc-500">
          Standards: {REPORT_META.standards} &middot; AI Policy: {REPORT_META.aiPolicy} &middot; Submission: {REPORT_META.submission}
        </div>
      </div>

      {/* 2. PAGE BUDGET BAR */}
      <div className="rounded-xl border border-zinc-700/40 bg-zinc-900/60 p-4">
        <h2 className="text-[11px] font-bold text-zinc-300 tracking-wider mb-3">
          PAGE BUDGET &mdash; {PAGE_BUDGET.total} PAGES
        </h2>
        {/* Bar */}
        <div className="flex h-7 rounded-lg overflow-hidden border border-zinc-700/30">
          {PAGE_BUDGET.sections.map((sec, i) => {
            const pct = (sec.pages / PAGE_BUDGET.total) * 100;
            const c = BUDGET_COLORS[i % BUDGET_COLORS.length];
            return (
              <div
                key={sec.id}
                className={`${c.bg}/30 flex items-center justify-center border-r border-zinc-900/50 last:border-r-0 relative group`}
                style={{ width: `${pct}%` }}
              >
                <span className={`text-[8px] font-bold ${c.label} truncate px-1`}>
                  {sec.label} ({sec.pages}p)
                </span>
              </div>
            );
          })}
        </div>
        {/* Legend */}
        <div className="flex flex-wrap gap-x-4 gap-y-1 mt-2">
          {PAGE_BUDGET.sections.map((sec, i) => {
            const c = BUDGET_COLORS[i % BUDGET_COLORS.length];
            return (
              <div key={sec.id} className="flex items-center gap-1.5">
                <div className={`w-2 h-2 rounded-sm ${c.bg}/50`} />
                <span className="text-[9px] text-zinc-500">
                  {sec.label}: {sec.pages} pages
                </span>
              </div>
            );
          })}
          <div className="text-[9px] text-zinc-600 ml-auto">
            + Cover and appendices (not counted)
          </div>
        </div>
      </div>

      {/* 3. RUBRIC */}
      <div>
        <h2 className="text-[11px] font-bold text-zinc-300 tracking-wider mb-3">
          MARKING CRITERIA
        </h2>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-3">
          {RUBRIC.map((crit: Criterion) => {
            const bandKey = `bands-${crit.name}`;
            const promptKey = `prompts-${crit.name}`;
            const showAllBands = expandedBands.has(bandKey);
            const showPrompts = expandedPrompts.has(promptKey);
            const visibleBands = showAllBands
              ? crit.bands
              : crit.bands.filter(b => isTopBand(b.range));

            return (
              <div
                key={crit.name}
                className={`rounded-xl border ${criterionBorder(crit.name)} bg-zinc-900/60 p-4 space-y-3`}
              >
                {/* Criterion header */}
                <div>
                  <div className="flex items-baseline justify-between">
                    <h3 className={`text-[12px] font-bold ${criterionColor(crit.name)}`}>
                      {crit.name}
                    </h3>
                  </div>
                  <div className="text-[8px] text-zinc-500 mt-0.5">
                    {crit.ahep}
                  </div>
                </div>

                {/* Band descriptors */}
                <div className="space-y-1.5">
                  {visibleBands.map(band => (
                    <div key={band.range} className="flex gap-2">
                      <span className={`text-[9px] font-mono font-bold shrink-0 w-[42px] text-right ${
                        band.range.includes("83") ? "text-emerald-400" :
                        band.range.includes("72") ? "text-blue-400" :
                        "text-zinc-600"
                      }`}>
                        {band.range}
                      </span>
                      <span className="text-[9px] text-zinc-400 leading-tight">
                        {band.descriptor}
                      </span>
                    </div>
                  ))}
                </div>

                {/* Toggle lower bands */}
                {crit.bands.length > visibleBands.length || showAllBands ? (
                  <button
                    onClick={() => toggleSet(expandedBands, bandKey, setExpandedBands)}
                    className="text-[8px] text-zinc-600 hover:text-zinc-400 transition-colors cursor-pointer"
                  >
                    {showAllBands
                      ? `\u25B2 Hide lower bands`
                      : `\u25BC Show all ${crit.bands.length} bands`}
                  </button>
                ) : null}

                {/* Top mark tips */}
                <div className="border-t border-zinc-800/50 pt-2">
                  <div className="text-[8px] font-bold tracking-wider text-emerald-500/70 mb-1">
                    TOP MARK TIPS
                  </div>
                  <ul className="space-y-1">
                    {crit.topMarkTips.map((tip, i) => (
                      <li key={i} className="text-[8px] text-zinc-400 leading-tight pl-2 relative">
                        <span className="absolute left-0 text-emerald-500/50">&bull;</span>
                        {tip}
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Reflection prompts (collapsible) */}
                <div className="border-t border-zinc-800/50 pt-2">
                  <button
                    onClick={() => toggleSet(expandedPrompts, promptKey, setExpandedPrompts)}
                    className={`text-[8px] font-bold tracking-wider ${criterionColor(crit.name)} opacity-70 hover:opacity-100 transition-opacity cursor-pointer`}
                  >
                    {showPrompts
                      ? `\u25B2 Hide reflection prompts`
                      : `\u25BC Reflection prompts (${crit.reflectionPrompts.length})`}
                  </button>
                  {showPrompts && (
                    <ul className="space-y-1.5 mt-2">
                      {crit.reflectionPrompts.map((prompt, i) => (
                        <li key={i} className="text-[9px] text-zinc-300 leading-tight pl-3 relative">
                          <span className={`absolute left-0 font-bold ${criterionColor(crit.name)} opacity-60`}>
                            {i + 1}.
                          </span>
                          {prompt}
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* 4. REPORT SECTIONS */}
      <div>
        <h2 className="text-[11px] font-bold text-zinc-300 tracking-wider mb-3">
          REPORT SECTIONS
        </h2>
        <div className="space-y-3">
          {REPORT_SECTIONS.map((sec: ReportSection) => {
            const outlineKey = `outline-${sec.id}`;
            const evidenceKey = `evidence-${sec.id}`;
            const showOutline = expandedOutlines.has(outlineKey);
            const showEvidence = expandedEvidence.has(evidenceKey);

            return (
              <div
                key={sec.id}
                className="rounded-xl border border-zinc-700/30 bg-zinc-900/60 p-4 space-y-2"
              >
                {/* Section header row */}
                <div className="flex items-center gap-3 flex-wrap">
                  <h3 className="text-[13px] font-bold text-zinc-100">
                    {sec.title}
                  </h3>
                  <StatusBadge status={sec.status} />
                  <span className="text-[9px] text-zinc-500 ml-auto">
                    {sec.suggestedPages}
                  </span>
                </div>

                {/* Guidance */}
                <p className="text-[10px] text-zinc-400 leading-relaxed">
                  {sec.guidance}
                </p>

                {/* Toggle buttons */}
                <div className="flex gap-3">
                  {sec.outline.length > 0 && (
                    <button
                      onClick={() => toggleSet(expandedOutlines, outlineKey, setExpandedOutlines)}
                      className="text-[8px] text-cyan-500/70 hover:text-cyan-400 transition-colors cursor-pointer"
                    >
                      {showOutline ? "\u25B2 Hide outline" : `\u25BC Outline (${sec.outline.length})`}
                    </button>
                  )}
                  {sec.evidence.length > 0 && (
                    <button
                      onClick={() => toggleSet(expandedEvidence, evidenceKey, setExpandedEvidence)}
                      className="text-[8px] text-emerald-500/70 hover:text-emerald-400 transition-colors cursor-pointer"
                    >
                      {showEvidence ? "\u25B2 Hide evidence" : `\u25BC Evidence (${sec.evidence.length})`}
                    </button>
                  )}
                </div>

                {/* Outline */}
                {showOutline && (
                  <div className="border-t border-zinc-800/40 pt-2 space-y-1">
                    {sec.outline.map((item, i) => {
                      const isSubItem = item.startsWith("  ");
                      return (
                        <div
                          key={i}
                          className={`text-[9px] leading-tight ${
                            isSubItem
                              ? "text-zinc-500 pl-4"
                              : "text-zinc-300 pl-2"
                          } relative`}
                        >
                          <span className={`absolute ${isSubItem ? "left-2" : "left-0"} ${
                            isSubItem ? "text-zinc-600" : "text-cyan-500/50"
                          }`}>
                            {isSubItem ? "\u2013" : "\u2022"}
                          </span>
                          {item.trimStart()}
                        </div>
                      );
                    })}
                  </div>
                )}

                {/* Evidence */}
                {showEvidence && (
                  <div className="border-t border-zinc-800/40 pt-2 space-y-1">
                    <div className="text-[8px] font-bold tracking-wider text-emerald-500/60 mb-1">
                      EXISTING EVIDENCE
                    </div>
                    {sec.evidence.map((item, i) => (
                      <div key={i} className="text-[9px] text-emerald-400/70 leading-tight pl-2 relative">
                        <span className="absolute left-0 text-emerald-500/40">{"\u2713"}</span>
                        {item}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* 5. TOP MARK STRATEGIES */}
      <div>
        <h2 className="text-[11px] font-bold text-zinc-300 tracking-wider mb-3">
          TOP MARK STRATEGIES
        </h2>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-3">
          {TOP_MARK_STRATEGIES.map(strat => {
            const color = strat.criterion.includes("Teamwork")
              ? { heading: "text-violet-400", border: "border-violet-500/30", badge: "bg-violet-900/30 text-violet-400" }
              : strat.criterion.includes("Self-Management")
                ? { heading: "text-amber-400", border: "border-amber-500/30", badge: "bg-amber-900/30 text-amber-400" }
                : { heading: "text-cyan-400", border: "border-cyan-500/30", badge: "bg-cyan-900/30 text-cyan-400" };

            return (
              <div
                key={strat.criterion}
                className={`rounded-xl border ${color.border} bg-zinc-900/60 p-4 space-y-2`}
              >
                <div className="flex items-baseline justify-between">
                  <h3 className={`text-[11px] font-bold ${color.heading}`}>
                    {strat.criterion}
                  </h3>
                  <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded ${color.badge}`}>
                    Target: {strat.target}
                  </span>
                </div>
                <ul className="space-y-1.5">
                  {strat.strategies.map((s, i) => (
                    <li key={i} className="text-[9px] text-zinc-400 leading-tight pl-3 relative">
                      <span className={`absolute left-0 font-bold ${color.heading} opacity-60`}>
                        {i + 1}.
                      </span>
                      {s}
                    </li>
                  ))}
                </ul>
              </div>
            );
          })}
        </div>
      </div>

      {/* 6. REFLECTION PROMPTS PANEL (writing worksheet) */}
      <div className="rounded-xl border border-zinc-700/40 bg-zinc-900/60 p-5">
        <h2 className="text-[13px] font-bold text-zinc-100 mb-1">
          Reflection Prompts Worksheet
        </h2>
        <p className="text-[9px] text-zinc-500 mb-4">
          Sit down and answer these questions. Your answers become the raw material for each section of the report.
        </p>

        <div className="space-y-5">
          {allPrompts.map(group => (
            <div key={group.criterion}>
              <div className="flex items-baseline gap-2 mb-2">
                <h3 className={`text-[11px] font-bold ${criterionColor(group.criterion)}`}>
                  {group.criterion}
                </h3>
                <span className="text-[8px] text-zinc-600">
                  {group.ahep}
                </span>
              </div>
              <div className={`rounded-lg border ${criterionBorder(group.criterion)} ${criterionBg(group.criterion)} p-3 space-y-2.5`}>
                {group.prompts.map((prompt, i) => (
                  <div key={i} className="flex gap-2">
                    <span className={`text-[10px] font-bold shrink-0 w-5 text-right ${criterionColor(group.criterion)} opacity-60`}>
                      {i + 1}.
                    </span>
                    <span className="text-[10px] text-zinc-300 leading-relaxed">
                      {prompt}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Bottom spacer */}
      <div className="h-8" />
    </div>
  );
}
