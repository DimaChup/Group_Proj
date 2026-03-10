/**
 * TeamTab — Who's doing what, at which level, blocking items
 */
import { TEAM } from "./hub-data";
import { LEVELS, ROADMAP, STATUS_COLORS, LEVEL_COLORS } from "./mission-data";

/** Per-member level assignments and tasks */
const MEMBER_FOCUS: Record<string, {
  level: number;
  tasks: string[];
  blocking?: string;
}> = {
  dima: {
    level: 2,
    tasks: [
      "Pi integration + GPS estimation pipeline",
      "simple_simulator.py (L2 flow tested end-to-end)",
      "pi_flight.py web ground station",
      "Dashboard (this app)",
      "Push code to Pi, outdoor GPS test",
    ],
    blocking: "Outdoor GPS fix test not done yet",
  },
  robin: {
    level: 1,
    tasks: [
      "Ground control station / detection image display",
      "Needs geotagged detection images from flights",
      "May build separate GCS UI or integrate with pi_flight.py",
    ],
    blocking: "Waiting for real flight images (--save-detections)",
  },
  edward: {
    level: 2,
    tasks: [
      "CV model training (YOLOv8)",
      "Retrain with real camera images once available",
      "Explore INT8 quantization for faster Pi inference",
    ],
    blocking: "Needs real photos of dummy from Pi camera",
  },
  herish: {
    level: 1,
    tasks: [
      "Hardware assembly + GPS testing",
      "Confirmed GPS works outdoors",
      "RC controller setup + kill switch configuration",
    ],
  },
  member5: {
    level: 0,
    tasks: ["Role to be assigned"],
  },
};

const LEVEL_NAMES: Record<number, string> = {
  0: "Foundation", 1: "L1 Manual", 2: "L2 Semi-Auto", 3: "L3 Full Auto",
};

export default function TeamTab() {
  const currentLevel = 2; // team is targeting L2

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-5 min-w-0">
      {/* Current target */}
      <div className="flex items-center gap-3">
        <div className="text-[9px] text-zinc-600 uppercase tracking-wider font-bold">Team Target</div>
        <div className="px-2 py-0.5 rounded text-[10px] font-bold"
          style={{ color: LEVELS[1].color, background: LEVELS[1].color + "15" }}>
          {LEVELS[1].name}
        </div>
        <div className="text-[9px] text-zinc-500">{LEVELS[1].autonomy}</div>
      </div>

      {/* Level progress summary */}
      <div className="grid grid-cols-4 gap-2">
        {[0, 1, 2, 3].map(lvl => {
          const steps = ROADMAP.filter(s => s.level === lvl);
          const done = steps.filter(s => s.status === "done").length;
          const color = LEVEL_COLORS[lvl];
          return (
            <div key={lvl} className="rounded-lg bg-zinc-900/50 border border-zinc-800/50 p-3">
              <div className="text-[8px] text-zinc-600 uppercase">{LEVEL_NAMES[lvl]}</div>
              <div className="flex items-baseline gap-1 mt-1">
                <span className="text-[16px] font-bold" style={{ color }}>{done}</span>
                <span className="text-[10px] text-zinc-600">/ {steps.length}</span>
              </div>
              <div className="w-full h-1 bg-zinc-800 rounded-full mt-1.5 overflow-hidden">
                <div className="h-full rounded-full transition-all"
                  style={{ width: `${steps.length ? (done / steps.length) * 100 : 0}%`, background: color }} />
              </div>
            </div>
          );
        })}
      </div>

      {/* Team members */}
      <div className="space-y-2">
        {TEAM.map(member => {
          const focus = MEMBER_FOCUS[member.id];
          const lvlColor = focus ? LEVEL_COLORS[focus.level] : "#6b7280";

          return (
            <div key={member.id} className="rounded-lg bg-zinc-900/50 border border-zinc-800/50 p-4">
              <div className="flex items-center gap-3">
                {/* Avatar dot */}
                <div className="w-3 h-3 rounded-full shrink-0" style={{ background: member.color }} />

                {/* Name + role */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-[12px] font-bold text-zinc-100">{member.name}</span>
                    {focus && (
                      <span className="text-[7px] px-1.5 py-0.5 rounded font-bold"
                        style={{ color: lvlColor, background: lvlColor + "15" }}>
                        {LEVEL_NAMES[focus.level]}
                      </span>
                    )}
                    {member.lastUpdate && (
                      <span className="text-[7px] text-zinc-700 ml-auto">updated {member.lastUpdate}</span>
                    )}
                  </div>
                  <div className="text-[9px] text-zinc-500">{member.role}</div>
                </div>
              </div>

              {/* Tasks */}
              {focus && (
                <div className="mt-2 ml-6 space-y-0.5">
                  {focus.tasks.map((t, i) => (
                    <div key={i} className="flex items-start gap-2 text-[9px]">
                      <span className="text-zinc-600 shrink-0 mt-0.5">{"\u2022"}</span>
                      <span className="text-zinc-400">{t}</span>
                    </div>
                  ))}
                </div>
              )}

              {/* Blocking */}
              {focus?.blocking && (
                <div className="mt-2 ml-6 px-2 py-1.5 rounded bg-amber-500/5 border border-amber-500/10">
                  <div className="text-[8px] text-amber-400/80">
                    Blocked: {focus.blocking}
                  </div>
                </div>
              )}

              {/* Needs */}
              {member.needsFromYou && (
                <div className="mt-2 ml-6 px-2 py-1.5 rounded bg-cyan-500/5 border border-cyan-500/10">
                  <div className="text-[8px] text-cyan-400/80">
                    Needs from you: {member.needsFromYou}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Next blockers to unblock */}
      <div>
        <h2 className="text-[11px] font-bold text-zinc-200 mb-2">Next Steps to Unblock</h2>
        <div className="space-y-1">
          {ROADMAP.filter(s => s.status === "ready" || s.status === "todo")
            .filter(s => s.level <= currentLevel)
            .slice(0, 5)
            .map(step => {
              const sc = STATUS_COLORS[step.status];
              return (
                <div key={step.id} className="flex items-center gap-3 px-3 py-2 rounded hover:bg-zinc-800/30">
                  <div className="w-1.5 h-1.5 rounded-full shrink-0" style={{ background: sc.color }} />
                  <div className="flex-1">
                    <div className="text-[10px] text-zinc-300">{step.name}</div>
                    <div className="text-[8px] text-zinc-600">{step.description}</div>
                  </div>
                  <span className="text-[7px] px-1 rounded font-bold"
                    style={{ color: sc.color, background: sc.bg }}>
                    {step.status.toUpperCase()}
                  </span>
                </div>
              );
            })}
        </div>
      </div>
    </div>
  );
}
