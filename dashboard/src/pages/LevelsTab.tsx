/**
 * LevelsTab — The "How": 3 product levels (L1 Manual, L2 Semi-Auto, L3 Full Auto)
 */
import { useState } from "react";
import { LEVELS, type MissionLevel } from "./mission-data";

export default function LevelsTab() {
  const [expanded, setExpanded] = useState<number>(2); // default to L2 (the target)

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-4 min-w-0">
      {/* Philosophy intro */}
      <div className="rounded-lg border border-zinc-800/50 bg-zinc-900/40 p-5">
        <div className="text-[9px] text-purple-400 uppercase tracking-widest font-bold mb-2">Why Three Levels?</div>
        <div className="text-[10px] text-zinc-400 leading-relaxed mb-3">
          We break the mission into three product levels that increase in autonomy and complexity.
          Each level is a <span className="text-zinc-200">working, demonstrable product</span> — not just a milestone.
          If we only achieve L1, we still have a useful system. L2 is the target for the flight test.
          L3 is a stretch goal that removes the pilot from the decision loop entirely.
        </div>
        <div className="flex gap-6 text-[9px]">
          <div className="flex items-center gap-2">
            <div className="w-2.5 h-2.5 rounded" style={{ background: "#22c55e" }} />
            <span className="text-zinc-400"><span className="text-zinc-200 font-medium">L1</span> — Pilot does everything, drone observes</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2.5 h-2.5 rounded" style={{ background: "#3b82f6" }} />
            <span className="text-zinc-400"><span className="text-zinc-200 font-medium">L2</span> — Drone flies autonomously, pilot confirms decisions</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2.5 h-2.5 rounded" style={{ background: "#a855f7" }} />
            <span className="text-zinc-400"><span className="text-zinc-200 font-medium">L3</span> — Drone decides everything, pilot only monitors</span>
          </div>
        </div>
      </div>

      {/* Level cards */}
      {LEVELS.map(level => {
        const isExpanded = expanded === level.id;
        return (
          <div key={level.id}
            className="rounded-lg border transition-all cursor-pointer"
            style={{
              borderColor: isExpanded ? level.color + "40" : "rgba(63,63,70,0.3)",
              background: isExpanded ? level.color + "05" : "rgba(24,24,27,0.5)",
            }}
            onClick={() => setExpanded(isExpanded ? 0 : level.id)}
          >
            {/* Header */}
            <div className="p-4 flex items-center gap-4">
              <div className="w-10 h-10 rounded-lg flex items-center justify-center text-[18px] font-black shrink-0"
                style={{ background: level.color + "15", color: level.color }}>
                L{level.id}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="text-[13px] font-bold text-zinc-100">{level.name}</span>
                  <span className="text-[8px] px-1.5 py-0.5 rounded font-bold tracking-wider"
                    style={{ color: level.color, background: level.color + "15" }}>
                    {level.tag}
                  </span>
                </div>
                <div className="text-[9px] text-zinc-500 mt-0.5">{level.autonomy}</div>
              </div>
              <span className="text-[10px] text-zinc-700">{isExpanded ? "\u25BC" : "\u25B6"}</span>
            </div>

            {/* Expanded content */}
            {isExpanded && <LevelDetail level={level} />}
          </div>
        );
      })}
    </div>
  );
}

/** L2 focus areas — the key pillars to build for semi-autonomous flight */
const L2_FOCUS_AREAS = [
  {
    label: "Computer Vision",
    color: "#8b5cf6",
    icon: "CV",
    summary: "Detect a person from 15-30m altitude",
    details: [
      "YOLOv8n TFLite model (~4 FPS on Pi)",
      "Confidence threshold tuning (currently 0.4)",
      "Synthetic training data — may need real photos",
      "Max detection altitude unknown (need flight test)",
    ],
    status: "Tested on bench, untested from altitude",
  },
  {
    label: "Flight Algorithm",
    color: "#3b82f6",
    icon: "FA",
    summary: "Search, detect, centre, land autonomously",
    details: [
      "Lawnmower search pattern from any polygon",
      "GPS estimation: clustering + inverse variance weighting",
      "Centre on target using visual servo + GPS lock",
      "7.5m offset landing (avoid propwash on casualty)",
      "SSSI geofence avoidance (R04) — not yet implemented",
      "PLB redirect mid-search (R05) — not yet implemented",
    ],
    status: "Full flow tested in simulation (SITL)",
  },
  {
    label: "Hardware Integration",
    color: "#f97316",
    icon: "HW",
    summary: "Pi + Cube + Camera + GPS all talking",
    details: [
      "Pi -> mavproxy -> Cube (921600 baud UART)",
      "Camera: IMX296 global shutter, BGR output",
      "GPS: Here 3+ on CAN2 (needs outdoor 3D fix)",
      "Tarot payload release for first aid kit (R07)",
    ],
    status: "Bench tested, needs outdoor + flight test",
  },
  {
    label: "Ground Station",
    color: "#06b6d4",
    icon: "GS",
    summary: "Pilot sees video + commands from browser",
    details: [
      "pi_flight.py: MJPEG stream + GPS grid + buttons",
      "Browser dashboard at http://PI_IP:8090",
      "Commands: N=investigate, Y=confirm, I=interest, X=FP, L=land",
      "Mission Planner on TCP:5762 for safety monitoring",
    ],
    status: "Tested in sim, not yet tested on Pi",
  },
  {
    label: "Safety & Failsafes",
    color: "#ef4444",
    icon: "SF",
    summary: "RC kill switch + failsafes + geofence",
    details: [
      "RC STABILIZE = instant manual override (R10)",
      "Battery failsafe -> RTL",
      "RC loss failsafe -> RTL",
      "50m altitude limit (R12)",
      "SSSI geofence exclusion (R04)",
      "VLOS at all times (R09)",
    ],
    status: "Kill switch configured, geofence not yet",
  },
  {
    label: "Payload Delivery",
    color: "#f59e0b",
    icon: "PL",
    summary: "Drop first aid kit near target (R07)",
    details: [
      "Tarot servo-actuated payload release",
      "Triggered via MAVLink DO_SET_SERVO after landing",
      "R07 is a 'should' — bonus, not mandatory",
      "Needs mounting, wiring, and testing",
    ],
    status: "Hardware available, not yet integrated",
  },
];

function LevelDetail({ level }: { level: MissionLevel }) {
  return (
    <div className="px-4 pb-4 space-y-4">
      {/* Description */}
      <div className="text-[10px] text-zinc-400 leading-relaxed">{level.description}</div>

      {/* L2 Focus Areas — only for the target level */}
      {level.id === 2 && (
        <div>
          <div className="text-[9px] text-blue-400 uppercase tracking-wider font-bold mb-2">Focus Areas — What We Need to Build</div>
          <div className="grid grid-cols-3 gap-2">
            {L2_FOCUS_AREAS.map(area => (
              <div key={area.label} className="rounded-lg p-3 border transition-all hover:brightness-110"
                style={{ background: area.color + "08", borderColor: area.color + "25" }}>
                <div className="flex items-center gap-2 mb-1.5">
                  <div className="w-6 h-6 rounded flex items-center justify-center text-[9px] font-black"
                    style={{ background: area.color + "20", color: area.color }}>
                    {area.icon}
                  </div>
                  <span className="text-[10px] font-bold text-zinc-200">{area.label}</span>
                </div>
                <div className="text-[9px] text-zinc-300 mb-2">{area.summary}</div>
                <div className="space-y-0.5 mb-2">
                  {area.details.map((d, i) => (
                    <div key={i} className="text-[8px] text-zinc-500 flex gap-1.5">
                      <span className="shrink-0" style={{ color: area.color + "80" }}>&bull;</span>
                      <span>{d}</span>
                    </div>
                  ))}
                </div>
                <div className="text-[7px] px-1.5 py-0.5 rounded inline-block"
                  style={{ color: area.color, background: area.color + "12" }}>
                  {area.status}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* State flow */}
      <div className="px-3 py-2 rounded bg-zinc-900/80 border border-zinc-800/50">
        <div className="text-[8px] text-zinc-600 uppercase tracking-wider font-bold mb-1">State Flow</div>
        <div className="text-[9px] font-mono text-zinc-300">{level.stateFlow}</div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        {/* Drone actions */}
        <div>
          <div className="text-[9px] text-zinc-500 uppercase tracking-wider font-bold mb-2">Drone Does</div>
          <div className="space-y-1">
            {level.droneActions.map((a, i) => (
              <div key={i} className="flex items-start gap-2 text-[9px]">
                <span className="mt-0.5 shrink-0" style={{ color: level.color }}>{"\u2022"}</span>
                <span className="text-zinc-300">{a}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Pilot actions */}
        <div>
          <div className="text-[9px] text-zinc-500 uppercase tracking-wider font-bold mb-2">Pilot Does</div>
          <div className="space-y-1">
            {level.pilotActions.map((a, i) => (
              <div key={i} className="flex items-start gap-2 text-[9px]">
                <span className="text-zinc-600 mt-0.5 shrink-0">{"\u2022"}</span>
                <span className="text-zinc-400">{a}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Scripts */}
      <div>
        <div className="text-[9px] text-zinc-500 uppercase tracking-wider font-bold mb-2">Scripts</div>
        <div className="space-y-1">
          {level.scripts.map(s => (
            <div key={s.name} className="flex items-center gap-2 px-2 py-1.5 rounded bg-zinc-900/50 border border-zinc-800/50">
              <span className="text-[9px] text-cyan-500 font-mono shrink-0">{s.name}</span>
              <span className="text-[8px] text-zinc-600">{s.purpose}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        {/* What's working */}
        <div>
          <div className="text-[9px] text-green-500/80 uppercase tracking-wider font-bold mb-2">Working</div>
          <div className="space-y-0.5">
            {level.whatsWorking.map((w, i) => (
              <div key={i} className="flex items-start gap-2 text-[9px]">
                <span className="text-green-500 shrink-0 mt-0.5">{"\u2713"}</span>
                <span className="text-zinc-400">{w}</span>
              </div>
            ))}
          </div>
        </div>

        {/* What's missing */}
        <div>
          <div className="text-[9px] text-amber-500/80 uppercase tracking-wider font-bold mb-2">Missing</div>
          <div className="space-y-0.5">
            {level.whatsMissing.map((m, i) => (
              <div key={i} className="flex items-start gap-2 text-[9px]">
                <span className="text-amber-500 shrink-0 mt-0.5">{"\u25CB"}</span>
                <span className="text-zinc-500">{m}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
