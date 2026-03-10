/**
 * RightSidebar — Team Hub (Ctrl+R)
 * Everything team-related: members, comms, needs, blockers
 */
import { useState } from "react";
import { TEAM, CHAT_DIGEST } from "./hub-data";
import { ROADMAP, LEVEL_COLORS, STATUS_COLORS } from "./mission-data";

type Section = "team" | "chat" | "blockers";

/** Per-member level focus and current tasks */
const MEMBER_TASKS: Record<string, { level: number; tasks: string[] }> = {
  dima:    { level: 2, tasks: ["Pi integration + GPS pipeline", "pi_flight.py GS", "Dashboard", "Outdoor GPS test"] },
  robin:   { level: 1, tasks: ["GCS / detection image display", "Waiting for geotagged images"] },
  edward:  { level: 2, tasks: ["CV model training (YOLOv8)", "Needs real Pi camera photos"] },
  herish:  { level: 1, tasks: ["Hardware + GPS tested", "RC kill switch config"] },
  member5: { level: 0, tasks: ["Role TBD"] },
};

const LEVEL_NAMES: Record<number, string> = {
  0: "Foundation", 1: "L1", 2: "L2", 3: "L3",
};

export default function RightSidebar() {
  const [openSection, setOpenSection] = useState<Section>("team");

  return (
    <div className="w-64 bg-zinc-900/95 border-l border-zinc-800 flex flex-col h-full backdrop-blur-sm shrink-0">
      <div className="p-3 border-b border-zinc-800">
        <h2 className="text-[11px] font-bold text-zinc-300 tracking-wider uppercase">Team</h2>
        <p className="text-[9px] text-zinc-600 mt-0.5">People, comms, blockers</p>
      </div>

      {/* Section tabs */}
      <div className="flex border-b border-zinc-800">
        {([
          { id: "team" as Section, label: "Members" },
          { id: "chat" as Section, label: "Comms" },
          { id: "blockers" as Section, label: "Blockers" },
        ]).map(tab => (
          <button key={tab.id}
            onClick={() => setOpenSection(tab.id)}
            className={`flex-1 py-1.5 text-[9px] transition-all ${
              openSection === tab.id
                ? "text-white border-b border-blue-500 bg-zinc-800/30"
                : "text-zinc-600 hover:text-zinc-400"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <div className="flex-1 overflow-y-auto">
        {/* Team members */}
        {openSection === "team" && (
          <div className="p-2 space-y-1.5">
            {TEAM.map(m => {
              const mt = MEMBER_TASKS[m.id];
              const lvlColor = mt ? LEVEL_COLORS[mt.level] : "#6b7280";
              return (
                <div key={m.id} className="p-2.5 rounded bg-zinc-800/30 border border-zinc-800/50">
                  <div className="flex items-center gap-2">
                    <div className="w-2.5 h-2.5 rounded-full" style={{ background: m.color }} />
                    <span className="text-[10px] font-medium text-zinc-200">{m.name}</span>
                    {mt && (
                      <span className="text-[7px] px-1 rounded font-bold ml-auto"
                        style={{ color: lvlColor, background: lvlColor + "15" }}>
                        {LEVEL_NAMES[mt.level]}
                      </span>
                    )}
                  </div>
                  <div className="text-[8px] text-zinc-500 mt-0.5">{m.role}</div>
                  {mt && (
                    <div className="mt-1 space-y-0">
                      {mt.tasks.map((t, i) => (
                        <div key={i} className="text-[8px] text-zinc-400 pl-2 border-l border-zinc-800">
                          {t}
                        </div>
                      ))}
                    </div>
                  )}
                  {m.needsFromYou && (
                    <div className="text-[8px] text-amber-400/80 mt-1.5 px-2 py-1 bg-amber-500/5 rounded border border-amber-500/10">
                      Needs: {m.needsFromYou}
                    </div>
                  )}
                  {m.lastUpdate && (
                    <div className="text-[7px] text-zinc-700 mt-1">{m.lastUpdate}</div>
                  )}
                </div>
              );
            })}
          </div>
        )}

        {/* Chat digest */}
        {openSection === "chat" && (
          <div className="p-2 space-y-1.5">
            <p className="text-[8px] text-zinc-600 px-1">Key decisions from team comms</p>
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
        )}

        {/* Blockers */}
        {openSection === "blockers" && (
          <div className="p-2 space-y-1">
            <p className="text-[8px] text-zinc-600 px-1 mb-1">Steps blocking progress (L1 + L2)</p>
            {ROADMAP
              .filter(s => (s.status === "todo" || s.status === "ready" || s.status === "blocked") && s.level <= 2)
              .map(step => {
                const sc = STATUS_COLORS[step.status];
                const lc = LEVEL_COLORS[step.level];
                return (
                  <div key={step.id} className="px-2 py-1.5 rounded hover:bg-zinc-800/30">
                    <div className="flex items-center gap-2">
                      <div className="w-1.5 h-1.5 rounded-full shrink-0" style={{ background: sc.color }} />
                      <span className="text-[9px] text-zinc-300">{step.name}</span>
                      <span className="text-[7px] px-1 rounded font-bold ml-auto"
                        style={{ color: lc, background: lc + "15" }}>
                        L{step.level}
                      </span>
                    </div>
                    <div className="text-[8px] text-zinc-600 ml-4 mt-0.5">{step.description}</div>
                  </div>
                );
              })}
          </div>
        )}
      </div>
    </div>
  );
}
