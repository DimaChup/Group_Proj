/**
 * HubPage — Main dashboard home page
 *
 * Center content: project status, flight testing, subsystems
 */
import { SUBSYSTEMS, FLIGHT_STEPS, STATUS_CONFIG, STEP_CONFIG } from "./hub-data";

export default function HubPage() {
  const doneCount = SUBSYSTEMS.filter(s => s.status === "done").length;
  const totalCount = SUBSYSTEMS.length;
  const flightReady = FLIGHT_STEPS.filter(s => s.status === "done").length;

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-6 min-w-0">
      {/* Header */}
      <div>
        <h1 className="text-lg font-bold text-zinc-100">SAR Drone Mission Hub</h1>
        <p className="text-[10px] text-zinc-500 mt-0.5">
          Locate a person in a search area, safely deliver a care package, and fly back home.
        </p>
      </div>

      {/* Status overview cards */}
      <div className="grid grid-cols-4 gap-3">
        <StatCard label="Subsystems" value={`${doneCount}/${totalCount}`}
          sub="verified" color={doneCount === totalCount ? "#22c55e" : "#f59e0b"} />
        <StatCard label="Flight Steps" value={`${flightReady}/5`}
          sub="completed" color={flightReady >= 3 ? "#22c55e" : "#6b7280"} />
        <StatCard label="Pi Inference" value="3.9 FPS"
          sub="256ms avg" color="#3b82f6" />
        <StatCard label="GPS" value="Needs Test"
          sub="outdoor required" color="#f59e0b" />
      </div>

      {/* Two column: subsystems + flight steps */}
      <div className="grid grid-cols-2 gap-4">
        {/* Subsystems */}
        <div className="bg-zinc-900/50 rounded-lg border border-zinc-800/50 p-4">
          <h2 className="text-[12px] font-bold text-zinc-200 mb-3">Subsystem Status</h2>
          <div className="space-y-1">
            {SUBSYSTEMS.map(s => {
              const cfg = STATUS_CONFIG[s.status];
              return (
                <div key={s.id} className="flex items-start gap-2 px-2 py-1.5 rounded hover:bg-zinc-800/30 transition-all">
                  <div className="w-1.5 h-1.5 rounded-full mt-1 shrink-0" style={{ background: cfg.color }} />
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] text-zinc-200">{s.name}</span>
                      <span className="text-[7px] px-1 py-0 rounded font-medium"
                        style={{ color: cfg.color, background: cfg.bg }}>
                        {cfg.label}
                      </span>
                      {s.lastTested && (
                        <span className="text-[7px] text-zinc-700 ml-auto">{s.lastTested}</span>
                      )}
                    </div>
                    <div className="text-[8px] text-zinc-600 leading-tight">{s.notes}</div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Flight testing */}
        <div className="bg-zinc-900/50 rounded-lg border border-zinc-800/50 p-4">
          <h2 className="text-[12px] font-bold text-zinc-200 mb-3">Flight Testing Progress</h2>
          <div className="space-y-2">
            {FLIGHT_STEPS.map((step, i) => {
              const cfg = STEP_CONFIG[step.status];
              return (
                <div key={step.id} className="relative">
                  {/* Connector line */}
                  {i < FLIGHT_STEPS.length - 1 && (
                    <div className="absolute left-[7px] top-6 w-px h-full"
                      style={{ background: STEP_CONFIG[FLIGHT_STEPS[i + 1].status].color + "30" }} />
                  )}

                  <div className="flex items-start gap-3 relative">
                    {/* Step number */}
                    <div className="w-4 h-4 rounded-full flex items-center justify-center text-[9px] font-bold shrink-0 border"
                      style={{
                        color: cfg.color,
                        borderColor: cfg.color + "50",
                        background: cfg.color + "15",
                      }}>
                      {cfg.symbol}
                    </div>

                    <div className="flex-1 pb-2">
                      <div className="flex items-center gap-2">
                        <span className="text-[10px] font-medium text-zinc-200">
                          Step {step.id}: {step.name}
                        </span>
                        <span className="text-[7px] px-1 rounded" style={{ color: cfg.color }}>
                          {step.status.toUpperCase()}
                        </span>
                      </div>
                      <div className="text-[8px] text-zinc-500 mt-0.5">{step.description}</div>
                      {step.script && (
                        <div className="text-[8px] text-cyan-600 font-mono mt-0.5">{step.script}</div>
                      )}
                      {step.notes && (
                        <div className="text-[7px] text-zinc-600 mt-0.5 italic">{step.notes}</div>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Safety note */}
          <div className="mt-4 px-3 py-2 rounded bg-red-500/5 border border-red-500/10">
            <div className="text-[8px] text-red-400 font-bold">SAFETY: Never skip a step.</div>
            <div className="text-[7px] text-red-400/60">Each step builds trust before adding risk. RC kill switch always active.</div>
          </div>
        </div>
      </div>

      {/* Architecture quick view */}
      <div className="bg-zinc-900/50 rounded-lg border border-zinc-800/50 p-4">
        <h2 className="text-[12px] font-bold text-zinc-200 mb-3">System Architecture</h2>
        <div className="grid grid-cols-3 gap-4 text-[9px]">
          <div>
            <div className="text-zinc-500 font-bold mb-1">ON THE DRONE</div>
            <div className="space-y-0.5">
              <div className="text-zinc-300">CubeOrangePlus <span className="text-zinc-600">(flight controller)</span></div>
              <div className="text-zinc-300">Raspberry Pi 5 <span className="text-zinc-600">(companion computer)</span></div>
              <div className="text-zinc-300">IMX296 Camera <span className="text-zinc-600">(global shutter)</span></div>
              <div className="text-zinc-300">Here 3+ GPS <span className="text-zinc-600">(CAN2)</span></div>
              <div className="text-zinc-300">Buzzer <span className="text-zinc-600">(MAVLink PLAY_TUNE)</span></div>
            </div>
          </div>
          <div>
            <div className="text-zinc-500 font-bold mb-1">CONNECTIONS</div>
            <div className="space-y-0.5 font-mono text-[8px]">
              <div className="text-zinc-400">Cube TELEM2 → Pi GPIO UART</div>
              <div className="text-zinc-400">Pi → mavproxy (UDP bridge)</div>
              <div className="text-zinc-400">mavproxy → Pi scripts (:14550)</div>
              <div className="text-zinc-400">mavproxy → Mission Planner (:5762)</div>
              <div className="text-zinc-400">RC → Cube (always override)</div>
            </div>
          </div>
          <div>
            <div className="text-zinc-500 font-bold mb-1">SOFTWARE</div>
            <div className="space-y-0.5">
              <div className="text-zinc-300">main.py <span className="text-zinc-600">(state machine)</span></div>
              <div className="text-zinc-300">simple_simulator.py <span className="text-zinc-600">(laptop sim)</span></div>
              <div className="text-zinc-300">pi_flight.py <span className="text-zinc-600">(web GS :8090)</span></div>
              <div className="text-zinc-300">vision.py <span className="text-zinc-600">(YOLOv8n TFLite)</span></div>
              <div className="text-zinc-300">config.py <span className="text-zinc-600">(auto-detect hw)</span></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════
// Sub-components
// ═══════════════════════════════════════════════════════════

function StatCard({ label, value, sub, color }: { label: string; value: string; sub: string; color: string }) {
  return (
    <div className="bg-zinc-900/50 rounded-lg border border-zinc-800/50 p-3">
      <div className="text-[8px] text-zinc-600 uppercase tracking-wider">{label}</div>
      <div className="text-lg font-bold mt-0.5" style={{ color }}>{value}</div>
      <div className="text-[8px] text-zinc-600">{sub}</div>
    </div>
  );
}
