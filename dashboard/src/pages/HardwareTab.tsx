/**
 * HardwareTab — All drone components, connections, setup guides, and links
 * Comprehensive hardware reference with expandable detail for each component
 */
import { useState } from "react";
import { HARDWARE_COMPONENTS, HARDWARE_CATEGORIES, CONNECTIONS, type HardwareComponent } from "./hardware-data";

const STATUS_STYLE: Record<string, { color: string; label: string }> = {
  verified: { color: "#22c55e", label: "VERIFIED" },
  partial:  { color: "#f59e0b", label: "PARTIAL" },
  todo:     { color: "#6b7280", label: "TODO" },
};

/** Styled hover tooltip — wrap any element, shows popup on hover */
function Tip({ children, text }: { children: React.ReactNode; text: string }) {
  return (
    <div className="relative group/tip">
      {children}
      <div className="absolute z-50 hidden group-hover/tip:block bottom-full left-1/2 -translate-x-1/2 mb-1.5 pointer-events-none">
        <div className="px-2.5 py-1.5 rounded-lg bg-zinc-800 border border-zinc-700/60 shadow-xl max-w-[220px] min-w-[140px]">
          <div className="text-[7px] text-zinc-300 leading-relaxed whitespace-normal">{text}</div>
        </div>
        <div className="w-2 h-2 bg-zinc-800 border-r border-b border-zinc-700/60 rotate-45 absolute left-1/2 -translate-x-1/2 -bottom-1" />
      </div>
    </div>
  );
}

export default function HardwareTab() {
  const [expandedId, setExpandedId] = useState<string | null>("cube");
  const [showConnections, setShowConnections] = useState(false);
  const [showCubeOverlay, setShowCubeOverlay] = useState(false);
  const [showPiOverlay, setShowPiOverlay] = useState(false);

  const verified = HARDWARE_COMPONENTS.filter(c => c.status === "verified").length;
  const partial = HARDWARE_COMPONENTS.filter(c => c.status === "partial").length;
  const todo = HARDWARE_COMPONENTS.filter(c => c.status === "todo").length;

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-4 min-w-0">
      {/* Connection Network Diagram */}
      <div className="rounded-lg border border-zinc-800/50 bg-zinc-900/40 p-5">
        <div className="text-[9px] text-orange-400 uppercase tracking-widest font-bold mb-3">System Architecture — Connection Diagram</div>

        <div className="grid grid-cols-[1fr_auto_1fr] gap-x-4 gap-y-0">

          {/* === ON-DRONE (bordered box) — spans first 2 columns, 3-col inner grid === */}
          <div className="border-2 border-dashed border-zinc-700/50 rounded-xl p-3 col-span-2 grid grid-cols-[1fr_auto_auto] gap-x-3">
            <div className="col-span-3 flex items-baseline gap-2 mb-2">
              <span className="text-[8px] text-zinc-500 uppercase tracking-widest font-bold">On-Drone</span>
              <span className="text-[7px] text-zinc-700 italic">Hexsoon EDU-450 frame</span>
            </div>

            {/* COL 1: peripherals grouped by destination — vertically aligned with brains */}
            <div className="flex flex-col">
              {/* Spacer to push Cube peripherals down to match Cube box (below Motors + PWM) */}
              <div className="h-[52px]" />
              {/* --- Connected to CUBE (aligned with Cube box) --- */}
              <div className="flex flex-col gap-px">
                <div className="text-[7px] text-red-400/60 uppercase tracking-widest font-bold mb-0.5">&rarr; Cube (flight control)</div>

                <Tip text="GPS + GLONASS + BeiDou + Galileo. ~2.5m accuracy. Built-in compass for yaw. CAN bus powered (no separate wire). Mount on mast, away from motors.">
                  <div className="flex items-center gap-1.5 text-[8px] cursor-help">
                    <span className="px-2 py-1 rounded bg-green-500/10 border border-green-500/20 text-green-400 font-bold shrink-0">Here 3+ GPS</span>
                    <span className="text-zinc-600 text-[7px] flex-1 text-center border-b border-dashed border-zinc-800">CAN2</span>
                    <span className="text-red-400/40">&rarr;</span>
                  </div>
                </Tip>

                <Tip text="4S LiPo = 14.8V nominal. Powers ALL systems via Power Distribution Board (PDB): Cube, Pi, motors, GPS, servos. Failsafe at 14.0V (3.5V/cell). ~15-20 min flight. Shows 0V on USB-only bench power.">
                  <div className="flex items-center gap-1.5 text-[8px] cursor-help">
                    <span className="px-2 py-1 rounded bg-orange-500/10 border border-orange-500/20 text-orange-300 font-bold shrink-0">LiPo 4S</span>
                    <span className="text-zinc-600 text-[7px] flex-1 text-center border-b border-dashed border-zinc-800">POWER1</span>
                    <span className="text-red-400/40">&rarr;</span>
                  </div>
                </Tip>
                <div className="text-[6px] text-zinc-700 italic ml-1 -mt-px">14.8V &bull; powers all systems via PDB &bull; ~15-20 min flight</div>

                <Tip text="Audio alerts. Arming tone, detection beeps, failsafe warnings. Controlled via MAVLink PLAY_TUNE command from Pi scripts.">
                  <div className="flex items-center gap-1.5 text-[7px] cursor-help">
                    <span className="px-1.5 py-0.5 rounded bg-amber-500/10 border border-amber-500/20 text-amber-400 font-bold shrink-0 text-[7px]">Buzzer</span>
                    <span className="text-zinc-600 text-[6px] flex-1 text-center border-b border-dashed border-zinc-800">BUZZER</span>
                    <span className="text-red-400/40">&larr;</span>
                  </div>
                </Tip>

                <Tip text="Tarot double-throw servo release mechanism. Deploys provided first aid kit after landing 5-10m from casualty (R07). Triggered via MAVLink DO_SET_SERVO. Status: not yet integrated.">
                  <div className="flex items-center gap-1.5 text-[8px] cursor-help">
                    <span className="px-1.5 py-0.5 rounded bg-amber-500/10 border border-amber-500/20 text-amber-300 font-bold shrink-0">Tarot Release</span>
                    <span className="text-zinc-600 text-[7px] flex-1 text-center border-b border-dashed border-zinc-800">AUX OUT</span>
                    <span className="text-red-400/40">&larr;</span>
                  </div>
                </Tip>
                <div className="text-[6px] text-zinc-700 italic ml-1 -mt-px">first aid kit deploy (R07) &bull; todo</div>
              </div>

              {/* --- Connected to PI (pushed to bottom, aligned with Pi box) --- */}
              <div className="mt-auto">
                <div className="text-[7px] text-blue-400/60 uppercase tracking-widest font-bold mb-0.5">&rarr; Pi (vision / AI)</div>

                <Tip text="Sony IMX296 global shutter sensor. No rolling shutter artifacts in flight. 6mm CS-mount wide angle lens. 640x480 @ ~4 FPS with AI inference. Outputs BGR (no cvtColor needed). CSI ribbon connects directly to Pi — frames go straight to CV/YOLOv8n for detection.">
                  <div className="flex items-center gap-1.5 text-[8px] cursor-help">
                    <span className="px-1.5 py-0.5 rounded bg-green-500/10 border border-green-500/20 text-green-400 font-bold shrink-0">IMX296 Camera</span>
                    <span className="text-zinc-600 text-[7px] flex-1 text-center border-b border-dashed border-zinc-800">CSI ribbon</span>
                    <span className="text-emerald-400/60">&rarr; CV</span>
                  </div>
                </Tip>
                <div className="text-[6px] text-zinc-700 italic ml-1 -mt-px">global shutter &bull; 6mm lens &bull; 640&times;480 &rarr; YOLOv8n</div>
              </div>
            </div>

            {/* COL 2: Motors → Cube → mavproxy → Pi */}
            <div className="flex flex-col items-center gap-1 pt-4">
              <Tip text="4x brushless motors + ESCs. QUAD/X layout. Motors 1,4 spin CW / 2,3 CCW. Powered from PDB (battery). PWM signals from Cube. ALWAYS remove props for bench testing.">
                <div className="px-3 py-1.5 rounded bg-orange-500/10 border border-orange-500/20 text-center cursor-help">
                  <div className="text-[9px] text-orange-400 font-bold">Motors &times;4</div>
                  <div className="text-[6px] text-zinc-600">brushless + ESC</div>
                </div>
              </Tip>

              <div className="h-3 w-px border-l-2 border-dashed border-orange-500/30 relative">
                <span className="absolute left-2 top-0 text-[6px] text-orange-500/50 whitespace-nowrap">PWM 1-4</span>
              </div>

              <div onClick={() => setShowCubeOverlay(true)}
                className="px-5 py-6 rounded-lg bg-red-500/10 border-2 border-red-500/30 text-center cursor-pointer min-w-[140px] hover:bg-red-500/15 hover:border-red-500/50 transition-all">
                <div className="text-[12px] text-red-400 font-black">Cube Orange+</div>
                <div className="text-[7px] text-zinc-500 mt-1">STM32H757 M7 400MHz</div>
                <div className="text-[7px] text-zinc-500"><span className="text-red-300 font-bold">1MB RAM</span> &bull; 2MB Flash</div>
                <div className="text-[7px] text-zinc-600 mt-0.5">Flight Controller</div>
                <div className="text-[6px] text-zinc-700 mt-2 pt-2 border-t border-red-500/10">GPS &bull; Motors &bull; RC</div>
                <div className="text-[6px] text-zinc-700">Buzzer &bull; Release &bull; LiPo</div>
                <div className="text-[6px] text-red-400/30 mt-1 italic">click for details</div>
              </div>

              {/* Physical serial wire: Cube ↔ Pi GPIO UART (bidirectional, single wire) */}
              <Tip text="Single bidirectional serial wire (TX/RX/GND). ALL MAVLink traffic shares this one channel. Down: GPS, altitude, attitude, battery, flight mode, heartbeat. Up: arm, takeoff, goto waypoint, change mode, land, buzzer. mavproxy on Pi multiplexes this for both Pi scripts and Mission Planner.">
                <div className="h-10 w-px border-l-2 border-dashed border-amber-500/40 relative cursor-help">
                  <span className="absolute -left-8 top-1 text-[6px] text-amber-500/60 whitespace-nowrap">TELEM2</span>
                  <span className="absolute left-2 top-0 text-[6px] text-amber-500/60 whitespace-nowrap">&harr; serial wire</span>
                  <span className="absolute left-2 top-2 text-[6px] text-amber-500/60 whitespace-nowrap">921600 baud</span>
                  <span className="absolute left-2 top-4 text-[6px] text-zinc-600 whitespace-nowrap">1 channel, all data</span>
                </div>
              </Tip>

              {/* Pi box with mavproxy + CV inside it — clickable for deep dive */}
              <Tip text="BCM2712 Quad Cortex-A76 @ 2.4GHz. 8GB LPDDR4X RAM. Click for deep dive.">
                <div onClick={() => setShowPiOverlay(true)}
                  className="px-4 py-3 rounded-lg bg-blue-500/10 border-2 border-blue-500/30 text-center cursor-pointer min-w-[160px] hover:bg-blue-500/15 hover:border-blue-500/50 transition-all">
                  <div className="text-[10px] text-blue-400 font-black">Raspberry Pi 5</div>
                  <div className="text-[7px] text-zinc-500">Quad A76 2.4GHz &bull; <span className="text-blue-300 font-bold">8GB RAM</span></div>
                  <div className="text-[7px] text-zinc-600">Companion Computer</div>

                  {/* CV / AI shown as software running ON the Pi */}
                  <Tip text="YOLOv8n model exported to TFLite for edge inference. Runs on Pi CPU (no GPU). ~250ms per frame = ~4 FPS. Detects dummy/casualty in camera frames. Camera physically connected via CSI ribbon (zero network latency). Can't run on Cube (only 1MB RAM, microcontroller). Could theoretically run on laptop but would need WiFi video stream (adds latency + WiFi dependency).">
                    <div className="mt-2 px-2 py-1.5 rounded bg-emerald-500/10 border border-emerald-500/20 cursor-help">
                      <div className="text-[8px] text-emerald-400 font-bold">CV / YOLOv8n TFLite</div>
                      <div className="text-[6px] text-zinc-600">~250ms/frame &bull; 4 FPS</div>
                      <div className="text-[6px] text-zinc-700 italic">CSI &rarr; detect &rarr; GPS estimate</div>
                    </div>
                  </Tip>

                  {/* mavproxy shown as software running ON the Pi */}
                  <Tip text="MAVLink router software. Bridges serial UART from Cube to network protocols. Required because Python 3.13 + pyserial has broken serial reads. Must run in Terminal 1 on Pi before anything else works. Exposes: UDP:14550 for local Pi scripts, TCP:5762 for Mission Planner over WiFi.">
                    <div className="mt-1.5 px-2 py-1 rounded bg-pink-500/10 border border-pink-500/20 cursor-help">
                      <div className="text-[8px] text-pink-400 font-bold">mavproxy</div>
                      <div className="text-[6px] text-zinc-600">serial &rarr; UDP + TCP</div>
                    </div>
                  </Tip>

                  <div className="flex justify-center gap-3 mt-1.5 text-[6px]">
                    <Tip text="UDP = connectionless, fire-and-forget. Fast, low overhead. Used locally on the Pi for pi_flight.py and other Python scripts to receive MAVLink messages from Cube.">
                      <span className="text-blue-400/50 cursor-help">UDP:14550 (local)</span>
                    </Tip>
                    <Tip text="TCP = reliable connection with acknowledgments. Handles packet loss over WiFi. Mission Planner connects here from laptop to monitor telemetry and send commands.">
                      <span className="text-pink-400/50 cursor-help">TCP:5762 (WiFi)</span>
                    </Tip>
                  </div>
                  <div className="text-[6px] text-zinc-600 mt-1.5 pt-1.5 border-t border-blue-500/10 text-left px-1">
                    <div className="text-blue-400/50">&darr; from Cube: GPS, alt, attitude, battery</div>
                    <div className="text-red-400/40">&uarr; to Cube: arm, goto, mode, land, buzzer</div>
                  </div>
                  <div className="text-[6px] text-blue-400/40 mt-1">built-in WiFi</div>
                  <div className="text-[6px] text-blue-400/30 mt-1 italic">click for details</div>
                </div>
              </Tip>
            </div>

            {/* COL 3 (inside drone box): FrSky receiver — right side, arrows to Cube + from outside */}
            <div className="flex flex-col items-center pt-4">
              <Tip text="FrSky TW-Mini receiver. Receives 2.4 GHz signal from pilot's Twin X14 controller. Passes RC commands to Cube via RCIN port. This is a direct independent radio link — NOT over WiFi. Pilot ALWAYS has override.">
                <div className="flex flex-col items-center gap-1 cursor-help">
                  {/* Arrow left toward Cube */}
                  <div className="flex items-center gap-1.5 mb-1">
                    <span className="text-red-400/40">&larr;</span>
                    <span className="text-zinc-600 text-[6px] border-b border-dashed border-zinc-800">RCIN</span>
                  </div>
                  <div className="px-2 py-1.5 rounded-lg bg-cyan-500/10 border-2 border-cyan-500/20 text-center">
                    <div className="text-[9px] text-cyan-400 font-bold">FrSky TW-Mini</div>
                    <div className="text-[6px] text-zinc-600">RC Receiver</div>
                  </div>
                  {/* Arrow up from outside (2.4 GHz) */}
                  <div className="text-[6px] text-cyan-500/40">&uarr; 2.4 GHz</div>
                  <div className="text-[6px] text-cyan-500/30 italic">from RC &rarr;</div>
                </div>
              </Tip>
            </div>
          </div>

          {/* === RIGHT: EXTERNAL / GROUND — vertically aligned with what they connect to === */}
          <div className="flex flex-col col-start-3 row-start-1">
            <div className="text-[8px] text-zinc-500 uppercase tracking-widest font-bold text-center mb-2">External / Ground</div>

            {/* RC Controller — aligned with Cube/FrSky level (top) */}
            <Tip text="FrSky Twin X14. 24 channels, 2.4GHz ACCESS protocol. Left stick: throttle + yaw. Right stick: pitch + roll. 3-position switch for flight modes. Kill switch position = STABILIZE (instant manual control). Independent radio link — NOT WiFi.">
              <div className="flex items-center gap-1.5 text-[8px] cursor-help">
                <span className="text-cyan-500/40">&larr;</span>
                <span className="text-zinc-600 text-[7px] flex-1 text-center border-b border-dashed border-cyan-800/40">2.4 GHz radio</span>
                <span className="px-2 py-1 rounded bg-cyan-500/10 border border-cyan-500/20 text-cyan-300 font-bold shrink-0">RC Controller</span>
              </div>
            </Tip>
            <div className="text-[6px] text-zinc-700 ml-1">Twin X14 &rarr; TW-Mini &rarr; RCIN &rarr; Cube</div>
            <div className="text-[6px] text-cyan-500/40 italic ml-1">independent safety link &bull; always has priority</div>

            {/* Spacer — pushes WiFi section to Pi level (bottom) */}
            <div className="flex-1" />

            {/* WiFi section — aligned with Pi box (mavproxy lives there) */}
            <div className="text-[7px] text-zinc-600 uppercase tracking-widest font-bold text-center mb-1">via WiFi (same router/hotspot)</div>
            <div className="text-[6px] text-zinc-700 italic text-center mb-2">Pi + laptop both join same network</div>

            {/* Mission Planner ↔ mavproxy on Pi → relays to Cube */}
            <Tip text="Connects TCP to Pi IP:5762 over WiFi. BIDIRECTIONAL: receives telemetry (GPS, attitude, battery, flight mode) AND can send commands (mode changes, waypoints, parameters, arm/disarm). Single MAVLink connection carries all message types. mavproxy on Pi relays everything to/from Cube via serial wire.">
              <div className="flex items-center gap-1.5 text-[8px] cursor-help">
                <span className="text-pink-400/40">&harr;</span>
                <span className="text-zinc-600 text-[7px] flex-1 text-center border-b border-dashed border-pink-800/40">TCP:5762</span>
                <span className="px-2 py-1 rounded bg-pink-500/10 border border-pink-500/20 text-pink-300 font-bold shrink-0">Mission Planner</span>
              </div>
            </Tip>
            <div className="text-[6px] text-zinc-700 ml-1 -mt-px">&harr; mavproxy (on Pi) &harr; Cube &bull; telemetry + commands</div>

            <div className="h-1.5" />

            {/* Browser Dashboard ↔ Pi */}
            <Tip text="pi_flight.py serves web dashboard at HTTP:8090. BIDIRECTIONAL: streams MJPEG video + GPS grid + detection clusters TO browser. Receives operator commands FROM browser (N=investigate, Y=confirm, I=interest, X=false pos, L=land). This is how you see the live camera in flight — NOT PuTTY/SSH.">
              <div className="flex items-center gap-1.5 text-[8px] cursor-help">
                <span className="text-blue-400/40">&harr;</span>
                <span className="text-zinc-600 text-[7px] flex-1 text-center border-b border-dashed border-blue-800/40">HTTP:8090</span>
                <span className="px-2 py-1 rounded bg-blue-500/10 border border-blue-500/20 text-blue-300 font-bold shrink-0">Browser Dashboard</span>
              </div>
            </Tip>
            <div className="text-[6px] text-zinc-700 ml-1 -mt-px">&harr; pi_flight.py &rarr; MAVLink &rarr; Cube</div>
          </div>
        </div>

        {/* Data flow legend */}
        <div className="flex items-center gap-4 text-[7px] mt-3 pt-2 border-t border-zinc-800/30">
          <span className="text-red-400/70">RED = Flight Controller (commands, sensors, failsafes)</span>
          <span className="text-blue-400/70">BLUE = Companion Computer (CV, estimation, ground station)</span>
          <span className="text-cyan-400/70">CYAN = Radio (pilot override, always independent)</span>
          <span className="text-zinc-600 ml-auto">{verified} verified &middot; {partial} partial &middot; {todo} todo</span>
        </div>
      </div>

      {/* Connection table — always visible */}
      <div className="rounded-lg border border-cyan-500/20 bg-cyan-500/5 overflow-hidden">
        <button onClick={() => setShowConnections(!showConnections)}
          className="w-full flex items-center gap-2 px-4 py-2.5 hover:bg-cyan-500/5 transition-all text-left">
          <span className="text-[9px] text-zinc-600">{showConnections ? "\u25BC" : "\u25B6"}</span>
          <span className="text-[9px] text-cyan-400 uppercase tracking-widest font-bold">All Physical Connections</span>
          <span className="text-[8px] text-zinc-600 ml-auto">{CONNECTIONS.length} connections</span>
        </button>
        {showConnections && (
          <div className="px-4 pb-3 grid grid-cols-3 gap-1">
            {CONNECTIONS.map((c, i) => {
              const fromComp = HARDWARE_COMPONENTS.find(h => h.id === c.from);
              const toComp = HARDWARE_COMPONENTS.find(h => h.id === c.to);
              return (
                <div key={i} className="flex items-center gap-2 text-[8px] px-2 py-1 rounded bg-zinc-900/50">
                  <span className="text-zinc-300 font-medium">{fromComp?.name || c.from}</span>
                  <span className="text-cyan-500/60">&rarr;</span>
                  <span className="text-zinc-300 font-medium">{toComp?.name || c.to}</span>
                  <span className="text-zinc-600 ml-auto truncate">{c.label}</span>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Cube Orange+ Detail Overlay */}
      {showCubeOverlay && (
        <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/70 backdrop-blur-sm"
          onClick={(e) => { if (e.target === e.currentTarget) setShowCubeOverlay(false); }}>
          <div className="w-[70vw] max-h-[80vh] overflow-y-auto rounded-2xl bg-zinc-900 border-2 border-red-500/30 shadow-2xl p-6">
            {/* Header */}
            <div className="flex items-center justify-between mb-5">
              <div>
                <div className="text-[16px] text-red-400 font-black">Cube Orange+ — Deep Dive</div>
                <div className="text-[9px] text-zinc-500 mt-0.5">CubePilot &bull; STM32H757 M7 400MHz &bull; 1MB RAM &bull; 2MB Flash &bull; ArduCopter 4.6.3</div>
              </div>
              <button onClick={() => setShowCubeOverlay(false)}
                className="text-zinc-500 hover:text-zinc-300 text-lg px-3 py-1 rounded hover:bg-zinc-800 transition-all">&times;</button>
            </div>

            <div className="grid grid-cols-2 gap-4">
              {/* Hardware Specs + Why it can't run CV */}
              <div className="rounded-lg border border-red-500/20 bg-red-500/5 p-4">
                <div className="text-[9px] text-red-400 uppercase tracking-widest font-bold mb-2">Hardware Specs</div>
                <div className="grid grid-cols-2 gap-2 text-[8px] mb-3">
                  <div className="px-2 py-1.5 rounded bg-zinc-800/40 border border-zinc-700/30">
                    <div className="text-red-300 font-bold">CPU</div>
                    <div className="text-zinc-400">STM32H757 dual-core</div>
                    <div className="text-zinc-500 text-[7px]">Cortex-M7 @ 400MHz + M4 @ 240MHz</div>
                  </div>
                  <div className="px-2 py-1.5 rounded bg-zinc-800/40 border border-zinc-700/30">
                    <div className="text-red-300 font-bold">Memory</div>
                    <div className="text-zinc-400">1MB SRAM &bull; 2MB Flash</div>
                    <div className="text-zinc-500 text-[7px]">Entire firmware + all sensor data fits in 1MB</div>
                  </div>
                </div>
                <div className="space-y-1.5 text-[8px] text-zinc-400 leading-relaxed">
                  <p>The Cube is the <span className="text-red-300 font-bold">brain of the drone</span>. It reads all sensors, runs flight control at <span className="text-red-300 font-bold">400Hz</span>, and outputs PWM to motors.</p>
                  <p>We don&apos;t write code for it — it runs <span className="text-zinc-300 font-medium">ArduCopter firmware</span> (C++). We configure via parameters and send commands via MAVLink.</p>
                  <p className="text-zinc-600 italic">Why no CV here? YOLOv8n needs ~50MB RAM minimum. Cube has 1MB total. It&apos;s a microcontroller optimised for real-time control, not image processing.</p>
                </div>
              </div>

              {/* 400Hz Control Loop Visualization */}
              <div className="rounded-lg border border-amber-500/20 bg-amber-500/5 p-4">
                <div className="text-[9px] text-amber-400 uppercase tracking-widest font-bold mb-2">400Hz Control Loop &mdash; Every 2.5ms</div>
                <div className="space-y-1 text-[8px] text-zinc-400 leading-relaxed mb-3">
                  <p>The main loop runs <span className="text-amber-300 font-bold">400 times per second</span>. Each cycle takes 2.5ms and does:</p>
                </div>
                <div className="flex flex-col gap-1 font-mono text-[7px]">
                  <div className="flex items-center gap-2">
                    <span className="w-3 h-3 rounded-full bg-green-500/30 border border-green-500/40 shrink-0" />
                    <span className="text-green-400 w-20 shrink-0">READ</span>
                    <span className="text-zinc-500">IMU (accel + gyro) &bull; barometer &bull; compass &bull; GPS</span>
                  </div>
                  <div className="w-px h-2 ml-1.5 border-l border-dashed border-zinc-700" />
                  <div className="flex items-center gap-2">
                    <span className="w-3 h-3 rounded-full bg-blue-500/30 border border-blue-500/40 shrink-0" />
                    <span className="text-blue-400 w-20 shrink-0">FUSE</span>
                    <span className="text-zinc-500">EKF combines all sensors &rarr; position, velocity, attitude</span>
                  </div>
                  <div className="w-px h-2 ml-1.5 border-l border-dashed border-zinc-700" />
                  <div className="flex items-center gap-2">
                    <span className="w-3 h-3 rounded-full bg-amber-500/30 border border-amber-500/40 shrink-0" />
                    <span className="text-amber-400 w-20 shrink-0">COMPUTE</span>
                    <span className="text-zinc-500">PID: desired vs actual &rarr; correction for each axis</span>
                  </div>
                  <div className="w-px h-2 ml-1.5 border-l border-dashed border-zinc-700" />
                  <div className="flex items-center gap-2">
                    <span className="w-3 h-3 rounded-full bg-orange-500/30 border border-orange-500/40 shrink-0" />
                    <span className="text-orange-400 w-20 shrink-0">MIX</span>
                    <span className="text-zinc-500">Roll/pitch/yaw/thrust &rarr; individual motor speeds (QUAD/X)</span>
                  </div>
                  <div className="w-px h-2 ml-1.5 border-l border-dashed border-zinc-700" />
                  <div className="flex items-center gap-2">
                    <span className="w-3 h-3 rounded-full bg-red-500/30 border border-red-500/40 shrink-0" />
                    <span className="text-red-400 w-20 shrink-0">OUTPUT</span>
                    <span className="text-zinc-500">PWM signals to ESCs &rarr; motors spin at computed speeds</span>
                  </div>
                </div>
                <div className="mt-3 px-3 py-2 rounded bg-zinc-800/60 border border-zinc-700/30 text-[7px]">
                  <div className="text-amber-400/70 font-bold mb-1">Cascaded PID (per axis: roll, pitch, yaw)</div>
                  <div className="font-mono text-zinc-500">Desired angle &rarr; <span className="text-amber-400">P</span> &rarr; Desired rate &rarr; <span className="text-amber-400">PID</span> &rarr; Motor output</div>
                  <div className="text-zinc-600 mt-1"><span className="text-zinc-400">P</span>=correct &bull; <span className="text-zinc-400">I</span>=eliminate steady error &bull; <span className="text-zinc-400">D</span>=dampen oscillation</div>
                  <div className="text-zinc-600 mt-0.5">Params: ATC_ANG_RLL_P, ATC_RAT_RLL_P/I/D &bull; AUTOTUNE mode finds optimal gains</div>
                </div>
              </div>

              {/* Sensors inside */}
              <div className="rounded-lg border border-green-500/20 bg-green-500/5 p-4">
                <div className="text-[9px] text-green-400 uppercase tracking-widest font-bold mb-2">Onboard Sensors</div>
                <div className="grid grid-cols-2 gap-2 text-[8px]">
                  <div className="px-2 py-1.5 rounded bg-zinc-800/40 border border-zinc-700/30">
                    <div className="text-green-300 font-bold">IMU &times;3</div>
                    <div className="text-zinc-500 text-[7px]">Triple redundant. Accelerometer + gyroscope. Measures acceleration and rotation rate. 1kHz sampling.</div>
                  </div>
                  <div className="px-2 py-1.5 rounded bg-zinc-800/40 border border-zinc-700/30">
                    <div className="text-green-300 font-bold">Barometer &times;2</div>
                    <div className="text-zinc-500 text-[7px]">Dual redundant. Measures air pressure for altitude estimation. ~10cm resolution. Affected by prop wash.</div>
                  </div>
                  <div className="px-2 py-1.5 rounded bg-zinc-800/40 border border-zinc-700/30">
                    <div className="text-green-300 font-bold">Compass &times;2</div>
                    <div className="text-zinc-500 text-[7px]">Internal + Here3 external. Magnetometer for heading. External preferred (less motor interference).</div>
                  </div>
                  <div className="px-2 py-1.5 rounded bg-zinc-800/40 border border-zinc-700/30">
                    <div className="text-green-300 font-bold">EKF Fusion</div>
                    <div className="text-zinc-500 text-[7px]">Extended Kalman Filter fuses all sensors into one state estimate: position, velocity, attitude. Two EKF instances run in parallel.</div>
                  </div>
                </div>
              </div>

              {/* Flight Modes — all ArduCopter modes */}
              <div className="rounded-lg border border-blue-500/20 bg-blue-500/5 p-4">
                <div className="text-[9px] text-blue-400 uppercase tracking-widest font-bold mb-2">ArduCopter Flight Modes (~25 total, we use 6)</div>
                <div className="text-[7px] text-zinc-600 mb-2">Flight modes are built into the firmware — we don&apos;t create new ones. We switch between them via MAVLink SET_MODE or RC switch.</div>
                <div className="space-y-0.5 text-[8px]">
                  <div className="text-[7px] text-cyan-400/70 uppercase tracking-widest font-bold mt-1 mb-0.5">Pilot-controlled (RC)</div>
                  <div className="flex gap-2 px-2 py-0.5 rounded bg-cyan-500/5 border border-cyan-500/10"><span className="text-cyan-300 font-bold w-20 shrink-0">STABILIZE</span><span className="text-zinc-500">Full manual. RC sticks = tilt angles. Cube only self-levels when sticks centred. No GPS, no alt hold. <span className="text-cyan-400 font-bold">Kill switch mode</span> — flip RC switch here for instant manual override.</span></div>
                  <div className="flex gap-2 px-2 py-0.5 rounded bg-cyan-500/5"><span className="text-cyan-300 font-bold w-20 shrink-0">LOITER</span><span className="text-zinc-500">GPS + alt hold. Hands off = drone stays exactly in place. Pilot can nudge with sticks. Good for hovering to observe target.</span></div>
                  <div className="text-[7px] text-blue-400/70 uppercase tracking-widest font-bold mt-2 mb-0.5">Autonomous (Pi / Mission Planner)</div>
                  <div className="flex gap-2 px-2 py-0.5 rounded bg-blue-500/10 border border-blue-500/20"><span className="text-blue-200 font-bold w-20 shrink-0">GUIDED</span><span className="text-zinc-400"><span className="text-blue-300 font-bold">Our main mode.</span> Cube accepts goto-waypoint commands from Pi via MAVLink. Our state machine sends coordinates. Pilot RC is ignored (unless kill switch).</span></div>
                  <div className="flex gap-2 px-2 py-0.5 rounded bg-blue-500/5"><span className="text-blue-300 font-bold w-20 shrink-0">AUTO</span><span className="text-zinc-500">Follows pre-loaded mission (uploaded from Mission Planner). Step 1 testing only — no Pi involved.</span></div>
                  <div className="flex gap-2 px-2 py-0.5 rounded bg-blue-500/5"><span className="text-blue-300 font-bold w-20 shrink-0">RTL</span><span className="text-zinc-500">Return To Launch. Auto-climbs, flies home, lands. Triggered by failsafe (low battery, signal loss) or manual command.</span></div>
                  <div className="flex gap-2 px-2 py-0.5 rounded bg-blue-500/5"><span className="text-blue-300 font-bold w-20 shrink-0">LAND</span><span className="text-zinc-500">Descend vertically at current position, disarm on touchdown. End of mission.</span></div>
                  <div className="text-[7px] text-zinc-600 uppercase tracking-widest font-bold mt-2 mb-0.5">Other ArduCopter modes (not used by us)</div>
                  <div className="grid grid-cols-2 gap-x-3 gap-y-0.5 text-[7px] text-zinc-600">
                    <div><span className="text-zinc-500 font-bold w-20 inline-block">ALT_HOLD</span> Manual + altitude hold (barometer)</div>
                    <div><span className="text-zinc-500 font-bold w-20 inline-block">POSHOLD</span> Like Loiter but with manual lean</div>
                    <div><span className="text-zinc-500 font-bold w-20 inline-block">ACRO</span> Rate-only control (3D flips, no self-level)</div>
                    <div><span className="text-zinc-500 font-bold w-20 inline-block">SPORT</span> Rate control + self-level on stick release</div>
                    <div><span className="text-zinc-500 font-bold w-20 inline-block">AUTOTUNE</span> Oscillates to find optimal PID gains</div>
                    <div><span className="text-zinc-500 font-bold w-20 inline-block">BRAKE</span> Emergency stop, hover in place</div>
                    <div><span className="text-zinc-500 font-bold w-20 inline-block">SMART_RTL</span> Retraces path back home</div>
                    <div><span className="text-zinc-500 font-bold w-20 inline-block">DRIFT</span> Easy flying like a car (yaw+roll mixed)</div>
                    <div><span className="text-zinc-500 font-bold w-20 inline-block">CIRCLE</span> Orbits around a point at fixed radius</div>
                    <div><span className="text-zinc-500 font-bold w-20 inline-block">ZIGZAG</span> Zig-zag survey pattern (not lawnmower)</div>
                    <div><span className="text-zinc-500 font-bold w-20 inline-block">FOLLOW</span> Follows another MAVLink vehicle</div>
                    <div><span className="text-zinc-500 font-bold w-20 inline-block">THROW</span> Literally throw the drone, it catches itself</div>
                    <div><span className="text-zinc-500 font-bold w-20 inline-block">FLOWHOLD</span> Position hold using optical flow (no GPS)</div>
                    <div><span className="text-zinc-500 font-bold w-20 inline-block">FLIP</span> Does a flip. Yes, really.</div>
                  </div>
                </div>
              </div>

              {/* Connections (full width) */}
              <div className="col-span-2 rounded-lg border border-zinc-700/30 bg-zinc-800/30 p-4">
                <div className="text-[9px] text-zinc-400 uppercase tracking-widest font-bold mb-2">Physical Ports</div>
                <div className="grid grid-cols-4 gap-2 text-[8px]">
                  <div className="px-2 py-1.5 rounded bg-zinc-900/60 border border-zinc-700/30">
                    <div className="text-red-300 font-bold">TELEM2 &rarr; Pi</div>
                    <div className="text-zinc-600 text-[7px]">Serial UART, 921600 baud. TX/RX/GND to Pi GPIO. Only connection to companion computer. mavproxy bridges this to UDP/TCP.</div>
                  </div>
                  <div className="px-2 py-1.5 rounded bg-zinc-900/60 border border-zinc-700/30">
                    <div className="text-cyan-300 font-bold">RCIN &larr; FrSky</div>
                    <div className="text-zinc-600 text-[7px]">RC receiver input. S.BUS protocol from TW-Mini. 24 channels. Pilot override always works regardless of flight mode.</div>
                  </div>
                  <div className="px-2 py-1.5 rounded bg-zinc-900/60 border border-zinc-700/30">
                    <div className="text-green-300 font-bold">CAN2 &larr; GPS</div>
                    <div className="text-zinc-600 text-[7px]">CAN bus to Here 3+. Carries GPS data + compass. Powers the GPS module (no separate power wire needed).</div>
                  </div>
                  <div className="px-2 py-1.5 rounded bg-zinc-900/60 border border-zinc-700/30">
                    <div className="text-orange-300 font-bold">MAIN OUT &rarr; Motors</div>
                    <div className="text-zinc-600 text-[7px]">PWM outputs 1-4 to ESCs. 400Hz signal. Motor mapping: 1=front-right CW, 2=back-left CW, 3=front-left CCW, 4=back-right CCW.</div>
                  </div>
                  <div className="px-2 py-1.5 rounded bg-zinc-900/60 border border-zinc-700/30">
                    <div className="text-orange-300 font-bold">POWER1 &larr; PDB</div>
                    <div className="text-zinc-600 text-[7px]">Power + voltage/current sensing from Power Distribution Board. Reports battery to GCS. Failsafe at 14.0V.</div>
                  </div>
                  <div className="px-2 py-1.5 rounded bg-zinc-900/60 border border-zinc-700/30">
                    <div className="text-amber-300 font-bold">BUZZER</div>
                    <div className="text-zinc-600 text-[7px]">Audio output. Arming tones, GPS lock notification, failsafe warnings. MAVLink PLAY_TUNE from Pi scripts.</div>
                  </div>
                  <div className="px-2 py-1.5 rounded bg-zinc-900/60 border border-zinc-700/30">
                    <div className="text-amber-300 font-bold">AUX OUT &rarr; Tarot Release</div>
                    <div className="text-zinc-600 text-[7px]">Servo output for Tarot double-throw payload release. Pi sends MAVLink DO_SET_SERVO &rarr; mavproxy &rarr; serial &rarr; Cube outputs PWM to servo &rarr; servo arm opens &rarr; first aid kit drops. Pi decides WHEN; Cube physically controls the servo. Status: not yet integrated (R07).</div>
                  </div>
                  <div className="px-2 py-1.5 rounded bg-zinc-900/60 border border-zinc-700/30">
                    <div className="text-zinc-400 font-bold">USB</div>
                    <div className="text-zinc-600 text-[7px]">Config/firmware update only. Connect to laptop for Mission Planner parameter setup. Not used in flight.</div>
                  </div>
                </div>
              </div>

              {/* 3 Command Paths */}
              <div className="col-span-2 rounded-lg border border-pink-500/20 bg-pink-500/5 p-4">
                <div className="text-[9px] text-pink-400 uppercase tracking-widest font-bold mb-2">3 Independent Command Paths to Cube</div>
                <div className="text-[8px] text-zinc-400 leading-relaxed space-y-2">
                  <p>The Cube receives commands from 3 sources. All share the same serial wire (paths 2 &amp; 3), but RC is completely independent:</p>

                  <div className="grid grid-cols-3 gap-2">
                    <div className="px-3 py-2 rounded bg-cyan-500/5 border border-cyan-500/20">
                      <div className="text-[8px] text-cyan-400 font-bold mb-1">1. RC Controller (direct)</div>
                      <div className="font-mono text-[7px] text-zinc-500">
                        <div>Pilot &rarr; <span className="text-cyan-400">Twin X14</span></div>
                        <div>&rarr; 2.4GHz radio</div>
                        <div>&rarr; <span className="text-cyan-400">FrSky TW-Mini</span></div>
                        <div>&rarr; RCIN &rarr; <span className="text-red-400">Cube</span></div>
                      </div>
                      <div className="text-[6px] text-cyan-500/50 mt-1">Bypasses Pi completely. Always works. Kill switch = STABILIZE.</div>
                    </div>

                    <div className="px-3 py-2 rounded bg-pink-500/5 border border-pink-500/20">
                      <div className="text-[8px] text-pink-400 font-bold mb-1">2. Mission Planner (WiFi)</div>
                      <div className="font-mono text-[7px] text-zinc-500">
                        <div>Laptop &rarr; <span className="text-pink-400">Mission Planner</span></div>
                        <div>&rarr; TCP:5762 (WiFi)</div>
                        <div>&rarr; <span className="text-pink-400">mavproxy</span> (on Pi)</div>
                        <div>&rarr; serial &rarr; <span className="text-red-400">Cube</span></div>
                      </div>
                      <div className="text-[6px] text-pink-500/50 mt-1">Modes, waypoints, params, arm/disarm. Bidirectional — also receives telemetry.</div>
                    </div>

                    <div className="px-3 py-2 rounded bg-blue-500/5 border border-blue-500/20">
                      <div className="text-[8px] text-blue-400 font-bold mb-1">3. Browser Dashboard (WiFi)</div>
                      <div className="font-mono text-[7px] text-zinc-500">
                        <div>Laptop &rarr; <span className="text-blue-400">Browser</span></div>
                        <div>&rarr; HTTP:8090 (WiFi)</div>
                        <div>&rarr; <span className="text-blue-400">pi_flight.py</span> (on Pi)</div>
                        <div>&rarr; pymavlink &rarr; UDP:14550</div>
                        <div>&rarr; <span className="text-pink-400">mavproxy</span> &rarr; serial</div>
                        <div>&rarr; <span className="text-red-400">Cube</span></div>
                      </div>
                      <div className="text-[6px] text-blue-500/50 mt-1">N/Y/I/X/L commands. Pi translates HTTP to MAVLink. Also streams video back.</div>
                    </div>
                  </div>

                  <div className="px-3 py-2 rounded bg-zinc-800/60 border border-zinc-700/30 mt-2">
                    <div className="text-[8px] text-zinc-300 font-bold mb-1">What flows on the serial wire (single channel, bidirectional):</div>
                    <div className="font-mono text-[7px] text-zinc-500">
                      <div><span className="text-red-400">&darr; Cube &rarr; Pi:</span> HEARTBEAT, GLOBAL_POSITION_INT (GPS), ATTITUDE (roll/pitch/yaw), SYS_STATUS (battery), GPS_RAW_INT</div>
                      <div><span className="text-blue-400">&uarr; Pi &rarr; Cube:</span> SET_MODE, COMMAND_LONG (arm/takeoff/land), SET_POSITION_TARGET (goto waypoint), PLAY_TUNE (buzzer)</div>
                    </div>
                  </div>
                </div>
              </div>

              {/* State Machine vs Flight Modes + Tarot Release */}
              <div className="col-span-2 rounded-lg border border-purple-500/20 bg-purple-500/5 p-4">
                <div className="text-[9px] text-purple-400 uppercase tracking-widest font-bold mb-2">State Machine vs Flight Modes &mdash; Two Layers of Control</div>
                <div className="text-[8px] text-zinc-400 leading-relaxed space-y-2">
                  <p>There are <span className="text-purple-300 font-bold">two separate layers</span> that people often confuse:</p>

                  <div className="grid grid-cols-2 gap-3">
                    <div className="px-3 py-2 rounded bg-red-500/5 border border-red-500/20">
                      <div className="text-[9px] text-red-400 font-bold mb-1">Flight Modes (Cube firmware)</div>
                      <div className="text-zinc-500 text-[7px] space-y-1">
                        <p>Built into ArduCopter C++ code. ~25 modes. Define <span className="text-zinc-400">how the drone responds to inputs</span>: does it hold altitude? GPS position? Follow waypoints? Self-level?</p>
                        <p>We do NOT create new flight modes. We <span className="text-zinc-400">switch between existing ones</span> via MAVLink SET_MODE command.</p>
                        <p>During our mission the Cube stays in <span className="text-blue-300 font-bold">GUIDED</span> mode — meaning &quot;accept goto-waypoint commands from companion computer.&quot;</p>
                      </div>
                    </div>
                    <div className="px-3 py-2 rounded bg-purple-500/5 border border-purple-500/20">
                      <div className="text-[9px] text-purple-400 font-bold mb-1">State Machine (our Python on Pi)</div>
                      <div className="text-zinc-500 text-[7px] space-y-1">
                        <p>Our code in main.py / pi_flight.py. Defines <span className="text-zinc-400">what the drone should do next</span>: search this area, detected something, investigate, classify, land.</p>
                        <p>Runs on the Pi. Sends high-level commands to Cube: &quot;go to this GPS coordinate&quot;, &quot;change altitude to 15m&quot;, &quot;switch to LAND mode&quot;, &quot;play buzzer tune.&quot;</p>
                        <p>The state machine is the <span className="text-purple-300 font-bold">mission brain</span>. The Cube is the <span className="text-red-300 font-bold">flight muscle</span>.</p>
                      </div>
                    </div>
                  </div>

                  <div className="px-3 py-2 rounded bg-zinc-800/60 border border-zinc-700/30">
                    <div className="text-[8px] text-purple-300 font-bold mb-1">State Machine Flow (main.py)</div>
                    <div className="flex flex-wrap items-center gap-1 font-mono text-[7px]">
                      <span className="px-1.5 py-0.5 rounded bg-zinc-700/40 text-zinc-400">INIT</span><span className="text-zinc-600">&rarr;</span>
                      <span className="px-1.5 py-0.5 rounded bg-zinc-700/40 text-zinc-400">CONNECTING</span><span className="text-zinc-600">&rarr;</span>
                      <span className="px-1.5 py-0.5 rounded bg-zinc-700/40 text-zinc-400">ARMING</span><span className="text-zinc-600">&rarr;</span>
                      <span className="px-1.5 py-0.5 rounded bg-zinc-700/40 text-zinc-400">TAKEOFF</span><span className="text-zinc-600">&rarr;</span>
                      <span className="px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-400">SEARCH</span><span className="text-zinc-600">&rarr;</span>
                      <span className="px-1.5 py-0.5 rounded bg-green-500/20 text-green-400">CENTERING</span><span className="text-zinc-600">&rarr;</span>
                      <span className="px-1.5 py-0.5 rounded bg-green-500/20 text-green-400">DESCENDING</span><span className="text-zinc-600">&rarr;</span>
                      <span className="px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-400">VERIFY</span><span className="text-zinc-600">&rarr;</span>
                      <span className="px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-400">APPROACH</span><span className="text-zinc-600">&rarr;</span>
                      <span className="px-1.5 py-0.5 rounded bg-red-500/20 text-red-400">LANDING</span><span className="text-zinc-600">&rarr;</span>
                      <span className="px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400">DONE</span>
                    </div>
                    <div className="text-zinc-600 text-[7px] mt-1">Each state sends different MAVLink commands to Cube. Cube stays in GUIDED the entire time. State machine decides WHERE to fly; Cube decides HOW to fly there.</div>
                  </div>

                  {/* Tarot release chain */}
                  <div className="px-3 py-2 rounded bg-amber-500/5 border border-amber-500/20">
                    <div className="text-[8px] text-amber-300 font-bold mb-1">Tarot Payload Release — Full Chain</div>
                    <div className="flex flex-wrap items-center gap-1 font-mono text-[7px]">
                      <span className="px-1.5 py-0.5 rounded bg-purple-500/20 text-purple-400">State machine: DONE</span><span className="text-zinc-600">&rarr;</span>
                      <span className="px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-400">Pi: pymavlink</span><span className="text-zinc-600">&rarr;</span>
                      <span className="text-zinc-500">DO_SET_SERVO(ch, PWM)</span><span className="text-zinc-600">&rarr;</span>
                      <span className="px-1.5 py-0.5 rounded bg-pink-500/20 text-pink-400">mavproxy</span><span className="text-zinc-600">&rarr;</span>
                      <span className="text-zinc-500">serial</span><span className="text-zinc-600">&rarr;</span>
                      <span className="px-1.5 py-0.5 rounded bg-red-500/20 text-red-400">Cube: AUX OUT</span><span className="text-zinc-600">&rarr;</span>
                      <span className="text-zinc-500">PWM signal</span><span className="text-zinc-600">&rarr;</span>
                      <span className="px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-400">Servo opens</span><span className="text-zinc-600">&rarr;</span>
                      <span className="text-zinc-500">kit drops</span>
                    </div>
                    <div className="text-zinc-600 text-[7px] mt-1">Tarot is a double-throw servo. Two PWM values: one to hold (closed), one to release (open). Pi decides WHEN to release (after landing 5-10m from casualty). Cube physically controls the servo — it&apos;s just another PWM output like the motors. Status: hardware ready, software not yet integrated (R07).</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Raspberry Pi 5 Detail Overlay */}
      {showPiOverlay && (
        <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/70 backdrop-blur-sm"
          onClick={(e) => { if (e.target === e.currentTarget) setShowPiOverlay(false); }}>
          <div className="w-[70vw] max-h-[80vh] overflow-y-auto rounded-2xl bg-zinc-900 border-2 border-blue-500/30 shadow-2xl p-6">
            {/* Header */}
            <div className="flex items-center justify-between mb-5">
              <div>
                <div className="text-[16px] text-blue-400 font-black">Raspberry Pi 5 — Deep Dive</div>
                <div className="text-[9px] text-zinc-500 mt-0.5">BCM2712 &bull; Quad Cortex-A76 @ 2.4GHz &bull; 8GB LPDDR4X &bull; Python 3.13 &bull; Companion Computer</div>
              </div>
              <button onClick={() => setShowPiOverlay(false)}
                className="text-zinc-500 hover:text-zinc-300 text-lg px-3 py-1 rounded hover:bg-zinc-800 transition-all">&times;</button>
            </div>

            <div className="grid grid-cols-2 gap-4">
              {/* Hardware Specs */}
              <div className="rounded-lg border border-blue-500/20 bg-blue-500/5 p-4">
                <div className="text-[9px] text-blue-400 uppercase tracking-widest font-bold mb-2">Hardware Specs</div>
                <div className="grid grid-cols-2 gap-2 text-[8px] mb-3">
                  <div className="px-2 py-1.5 rounded bg-zinc-800/40 border border-zinc-700/30">
                    <div className="text-blue-300 font-bold">CPU</div>
                    <div className="text-zinc-400">BCM2712 Quad Cortex-A76</div>
                    <div className="text-zinc-500 text-[7px]">2.4GHz &bull; 64-bit ARMv8.2-A &bull; out-of-order</div>
                  </div>
                  <div className="px-2 py-1.5 rounded bg-zinc-800/40 border border-zinc-700/30">
                    <div className="text-blue-300 font-bold">Memory</div>
                    <div className="text-zinc-400">8GB LPDDR4X</div>
                    <div className="text-zinc-500 text-[7px]">8000x more RAM than Cube (1MB)</div>
                  </div>
                  <div className="px-2 py-1.5 rounded bg-zinc-800/40 border border-zinc-700/30">
                    <div className="text-blue-300 font-bold">Storage</div>
                    <div className="text-zinc-400">microSD (32GB+)</div>
                    <div className="text-zinc-500 text-[7px]">OS + code + models + logs</div>
                  </div>
                  <div className="px-2 py-1.5 rounded bg-zinc-800/40 border border-zinc-700/30">
                    <div className="text-blue-300 font-bold">Interfaces</div>
                    <div className="text-zinc-400">CSI, UART, WiFi, USB</div>
                    <div className="text-zinc-500 text-[7px]">Camera ribbon, Cube serial, ground station</div>
                  </div>
                </div>
                <div className="text-[8px] text-zinc-400 leading-relaxed">
                  <p>The Pi is the <span className="text-blue-300 font-bold">companion computer</span> — it runs our Python code, captures camera frames, runs AI inference, estimates GPS positions, and serves the ground station dashboard. The Cube handles flight; the Pi handles intelligence.</p>
                </div>
              </div>

              {/* What runs on it */}
              <div className="rounded-lg border border-emerald-500/20 bg-emerald-500/5 p-4">
                <div className="text-[9px] text-emerald-400 uppercase tracking-widest font-bold mb-2">Software Running on Pi</div>
                <div className="space-y-1.5 text-[8px]">
                  <div className="flex gap-2 items-start">
                    <span className="text-emerald-300 font-bold w-28 shrink-0">YOLOv8n TFLite</span>
                    <span className="text-zinc-500">AI object detection. ~250ms/frame, 4 FPS on CPU. Detects dummy/casualty in camera frames. Uses ai-edge-litert (Python 3.13 compatible).</span>
                  </div>
                  <div className="flex gap-2 items-start">
                    <span className="text-pink-300 font-bold w-28 shrink-0">mavproxy</span>
                    <span className="text-zinc-500">MAVLink router. Bridges Cube serial UART to UDP:14550 (local) + TCP:5762 (WiFi). Must start first in Terminal 1.</span>
                  </div>
                  <div className="flex gap-2 items-start">
                    <span className="text-blue-300 font-bold w-28 shrink-0">pi_flight.py</span>
                    <span className="text-zinc-500">Web ground station. MJPEG video stream + GPS grid + detection clusters + command buttons. Serves at HTTP:8090.</span>
                  </div>
                  <div className="flex gap-2 items-start">
                    <span className="text-amber-300 font-bold w-28 shrink-0">picamera2</span>
                    <span className="text-zinc-500">Camera driver. Captures 640&times;480 BGR frames from IMX296 via CSI ribbon. Zero network latency.</span>
                  </div>
                  <div className="flex gap-2 items-start">
                    <span className="text-zinc-300 font-bold w-28 shrink-0">pymavlink</span>
                    <span className="text-zinc-500">MAVLink library. Sends arm/takeoff/goto/land commands to Cube via UDP:14550 through mavproxy.</span>
                  </div>
                </div>
              </div>

              {/* CV Pipeline visualization */}
              <div className="rounded-lg border border-emerald-500/20 bg-emerald-500/5 p-4">
                <div className="text-[9px] text-emerald-400 uppercase tracking-widest font-bold mb-2">CV Pipeline &mdash; Every ~250ms (1 capture, 2 outputs)</div>
                <div className="flex flex-col gap-1 font-mono text-[7px]">
                  <div className="flex items-center gap-2">
                    <span className="w-3 h-3 rounded-full bg-green-500/30 border border-green-500/40 shrink-0" />
                    <span className="text-green-400 w-20 shrink-0">CAPTURE</span>
                    <span className="text-zinc-500">picamera2 &rarr; 1 frame (640&times;480 BGR) via CSI ribbon</span>
                  </div>
                  <div className="w-px h-2 ml-1.5 border-l border-dashed border-zinc-700" />
                  <div className="flex items-center gap-2">
                    <span className="w-3 h-3 rounded-full bg-blue-500/30 border border-blue-500/40 shrink-0" />
                    <span className="text-blue-400 w-20 shrink-0">PREPROCESS</span>
                    <span className="text-zinc-500">Resize to 640&times;640, normalize to [0,1], add batch dim</span>
                  </div>
                  <div className="w-px h-2 ml-1.5 border-l border-dashed border-zinc-700" />
                  <div className="flex items-center gap-2">
                    <span className="w-3 h-3 rounded-full bg-emerald-500/30 border border-emerald-500/40 shrink-0" />
                    <span className="text-emerald-400 w-20 shrink-0">INFER</span>
                    <span className="text-zinc-500">YOLOv8n TFLite on CPU &rarr; ~250ms &bull; bounding boxes + confidence</span>
                  </div>
                  <div className="w-px h-2 ml-1.5 border-l border-dashed border-zinc-700" />
                  <div className="flex items-center gap-2">
                    <span className="w-3 h-3 rounded-full bg-amber-500/30 border border-amber-500/40 shrink-0" />
                    <span className="text-amber-400 w-20 shrink-0">DRAW</span>
                    <span className="text-zinc-500">Draw green boxes + confidence labels on frame</span>
                  </div>
                  <div className="w-px h-2 ml-1.5 border-l border-dashed border-zinc-700" />
                  {/* Dual output fork */}
                  <div className="flex gap-4 ml-1">
                    <div className="flex flex-col items-center gap-1">
                      <span className="w-3 h-3 rounded-full bg-red-500/30 border border-red-500/40 shrink-0" />
                      <span className="text-red-400 text-[6px]">OUTPUT 1</span>
                    </div>
                    <div className="flex flex-col gap-0.5">
                      <span className="text-zinc-400">(found, x, y, conf) &rarr; state machine &rarr; fly decisions</span>
                      <span className="text-zinc-600">pixel offset &rarr; GPS estimate (GeoTransformer)</span>
                    </div>
                  </div>
                  <div className="flex gap-4 ml-1 mt-1">
                    <div className="flex flex-col items-center gap-1">
                      <span className="w-3 h-3 rounded-full bg-amber-500/30 border border-amber-500/40 shrink-0" />
                      <span className="text-amber-400 text-[6px]">OUTPUT 2</span>
                    </div>
                    <div className="flex flex-col gap-0.5">
                      <span className="text-zinc-400">same frame (with boxes) &rarr; JPEG encode (~5ms) &rarr; MJPEG stream</span>
                      <span className="text-zinc-600">operator sees exactly what the AI sees in browser</span>
                    </div>
                  </div>
                </div>
                <div className="mt-3 px-3 py-2 rounded bg-zinc-800/60 border border-zinc-700/30 text-[7px] text-zinc-500">
                  <span className="text-emerald-400/70 font-bold">1 capture, 2 consumers.</span> Camera captures one frame. CV processes it and draws detection boxes. The same processed frame is reused for the MJPEG stream — NOT a second camera capture. The expensive part is inference (~250ms). JPEG encoding for the stream is ~5ms. Zero extra camera overhead.
                </div>
              </div>

              {/* Live Video Stream */}
              <div className="rounded-lg border border-amber-500/20 bg-amber-500/5 p-4">
                <div className="text-[9px] text-amber-400 uppercase tracking-widest font-bold mb-2">Live Video Stream to Ground Station</div>
                <div className="space-y-1.5 text-[8px] text-zinc-400 leading-relaxed">
                  <p><span className="text-amber-300 font-bold">pi_flight.py</span> serves MJPEG video at <span className="font-mono text-zinc-300">http://PI_IP:8090/stream</span>. The stream shows the <span className="text-emerald-300 font-bold">same frame the AI processed</span> — with green detection boxes and confidence scores overlaid. Operator sees exactly what the AI sees.</p>

                  <div className="px-3 py-2 rounded bg-zinc-800/60 border border-zinc-700/30 my-2">
                    <div className="text-[7px] text-amber-300 font-bold mb-1">What the operator sees in the browser:</div>
                    <div className="text-[7px] text-zinc-500">Live camera feed with <span className="text-green-400">green bounding boxes</span> around detected objects + <span className="text-green-400">confidence score</span> (e.g. 0.87) + GPS grid showing drone position + detection clusters + command buttons (N/Y/I/X/L)</div>
                  </div>

                  <div className="grid grid-cols-2 gap-2 my-2">
                    <div className="px-2 py-1.5 rounded bg-zinc-800/40 border border-zinc-700/30">
                      <div className="text-amber-300 font-bold">MJPEG (chosen)</div>
                      <div className="text-zinc-500 text-[7px]">~100ms latency &bull; ~0.5 Mbps at 320&times;240</div>
                      <div className="text-zinc-600 text-[7px]">Pure Python, zero deps, any browser</div>
                    </div>
                    <div className="px-2 py-1.5 rounded bg-zinc-800/40 border border-zinc-700/30">
                      <div className="text-zinc-400 font-bold">H.264/HLS (alternative)</div>
                      <div className="text-zinc-500 text-[7px]">2-4s latency &bull; ~0.05 Mbps</div>
                      <div className="text-zinc-600 text-[7px]">Needs ffmpeg, HLS segments</div>
                    </div>
                  </div>
                  <p><span className="text-amber-300 font-bold">Two places, one frame.</span> Camera captures once. CV draws boxes on the frame. That same frame gets: (1) analysed for detection results → state machine, and (2) JPEG-encoded → streamed to browser. Not two camera feeds — one frame, reused. JPEG encode ~5ms vs inference ~250ms. Negligible.</p>
                  <p><span className="text-amber-300 font-bold">Bandwidth:</span> 320&times;240 at 5 FPS, JPEG quality 60 = ~0.5 Mbps. WiFi handles 50+ Mbps. Trivial.</p>
                  <p><span className="text-amber-300 font-bold">If WiFi is slow:</span> drop to 240&times;180, reduce quality to 40, or cap FPS to 2. Stream is for operator awareness only.</p>
                  <p className="text-zinc-600 italic">Key insight: even if WiFi drops completely, the drone keeps detecting and flying. The stream is for monitoring, not for decision-making. CV runs locally on Pi regardless.</p>
                </div>
              </div>

              {/* Why CV runs here (full width) */}
              <div className="col-span-2 rounded-lg border border-zinc-700/30 bg-zinc-800/30 p-4">
                <div className="text-[9px] text-zinc-400 uppercase tracking-widest font-bold mb-2">Why CV Runs on Pi (not Cube, not Laptop)</div>
                <div className="grid grid-cols-3 gap-3 text-[8px]">
                  <div className="px-3 py-2 rounded bg-red-500/5 border border-red-500/20">
                    <div className="text-red-400 font-bold mb-1">Cube Orange+ &mdash; Can&apos;t</div>
                    <div className="text-zinc-500">1MB RAM. YOLOv8n needs ~50MB minimum. It&apos;s a <span className="text-zinc-400">microcontroller</span> — runs one tight control loop at 400Hz. No OS, no Python, no TFLite. Like asking a calculator to run Photoshop.</div>
                  </div>
                  <div className="px-3 py-2 rounded bg-blue-500/5 border border-blue-500/20">
                    <div className="text-blue-400 font-bold mb-1">Raspberry Pi 5 &mdash; Chosen</div>
                    <div className="text-zinc-500">8GB RAM, 2.4GHz quad-core. Camera on CSI ribbon = <span className="text-zinc-400">zero network latency</span>. Drone stays self-contained — if WiFi drops, CV still works. ~250ms/frame is fast enough for 3-5 m/s search speed.</div>
                  </div>
                  <div className="px-3 py-2 rounded bg-purple-500/5 border border-purple-500/20">
                    <div className="text-purple-400 font-bold mb-1">Laptop/GCS &mdash; Could, but...</div>
                    <div className="text-zinc-500">16-32GB RAM, GPU = ~30ms inference. But needs WiFi video stream (adds 100-500ms latency + dependency). If WiFi drops, drone is blind. Single point of failure. Only good for simulation.</div>
                  </div>
                </div>
              </div>

              {/* === Three Scripts: How CV & Flight Control Interact === */}
              <div className="col-span-2 rounded-lg border border-cyan-500/20 bg-cyan-500/5 p-4">
                <div className="text-[9px] text-cyan-400 uppercase tracking-widest font-bold mb-1">Three Scripts &mdash; From Observer to Autonomous</div>
                <div className="text-[7px] text-zinc-600 mb-3">Same camera, same AI model, same Pi. Different levels of autonomy. Each script is a real file in the codebase.</div>

                <div className="grid grid-cols-3 gap-3">
                  {/* --- PASSIVE: pi_passive_flight.py --- */}
                  <div className="rounded-lg border border-zinc-700/40 bg-zinc-800/30 p-3">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="px-2 py-0.5 rounded bg-zinc-700/40 border border-zinc-600/30 text-[7px] text-zinc-300 font-black">OBSERVER</span>
                    </div>
                    <div className="text-[8px] text-zinc-400 font-bold">pi_passive_flight.py</div>
                    <div className="text-[7px] text-zinc-600 mb-2 italic">No state machine. Just a while loop.</div>

                    {/* Flow */}
                    <div className="flex flex-col gap-0 font-mono text-[7px]">
                      <div className="flex items-start gap-1.5">
                        <div className="flex flex-col items-center shrink-0">
                          <span className="w-2 h-2 rounded-full bg-green-500/40 border border-green-500/50" />
                          <span className="w-px h-2.5 border-l border-dashed border-zinc-700" />
                        </div>
                        <span className="text-zinc-500"><span className="text-green-400">STARTUP</span> connect Cube (read-only) + camera + AI</span>
                      </div>
                      <div className="flex items-start gap-1.5">
                        <div className="flex flex-col items-center shrink-0">
                          <span className="w-2 h-2 rounded-full bg-blue-500/40 border border-blue-500/50" />
                          <span className="w-px h-2.5 border-l border-dashed border-zinc-700" />
                        </div>
                        <span className="text-zinc-500"><span className="text-blue-400">CAPTURE</span> picamera2 &rarr; frame</span>
                      </div>
                      <div className="flex items-start gap-1.5">
                        <div className="flex flex-col items-center shrink-0">
                          <span className="w-2 h-2 rounded-full bg-emerald-500/40 border border-emerald-500/50" />
                          <span className="w-px h-2.5 border-l border-dashed border-zinc-700" />
                        </div>
                        <span className="text-zinc-500"><span className="text-emerald-400">DETECT</span> YOLOv8n &rarr; (found, x, y, conf)</span>
                      </div>
                      <div className="flex items-start gap-1.5">
                        <div className="flex flex-col items-center shrink-0">
                          <span className="w-2 h-2 rounded-full bg-amber-500/40 border border-amber-500/50" />
                          <span className="w-px h-2.5 border-l border-dashed border-zinc-700" />
                        </div>
                        <span className="text-zinc-500"><span className="text-amber-400">LOG</span> beep + CSV + save image</span>
                      </div>
                      <div className="flex items-start gap-1.5">
                        <div className="flex flex-col items-center shrink-0">
                          <span className="w-2 h-2 rounded-full bg-zinc-600/40 border border-zinc-600/50" />
                        </div>
                        <span className="text-zinc-600"><span className="text-zinc-400">LOOP</span> &uarr; repeat forever</span>
                      </div>
                    </div>

                    <div className="mt-2.5 space-y-0.5 text-[6.5px]">
                      <div className="px-1.5 py-0.5 rounded bg-zinc-900/60 border border-zinc-800/50">
                        <span className="text-red-400 font-bold">COMMANDS:</span>
                        <span className="text-zinc-500 ml-1">Zero. Buzzer beeps only.</span>
                      </div>
                      <div className="px-1.5 py-0.5 rounded bg-zinc-900/60 border border-zinc-800/50">
                        <span className="text-zinc-400 font-bold">CUBE:</span>
                        <span className="text-zinc-500 ml-1">STABILIZE. Pilot has full RC control.</span>
                      </div>
                      <div className="px-1.5 py-0.5 rounded bg-zinc-900/60 border border-zinc-800/50">
                        <span className="text-zinc-400 font-bold">PURPOSE:</span>
                        <span className="text-zinc-500 ml-1">Calibrate CV outdoors. Zero risk.</span>
                      </div>
                    </div>

                    <div className="mt-2 px-1.5 py-1 rounded bg-zinc-700/20 border border-zinc-700/30 text-[6.5px] text-center">
                      <div className="text-zinc-500">CV and flight are <span className="text-zinc-300 font-bold">independent</span></div>
                      <div className="text-zinc-600">Vision watches. Drone flies. They never talk.</div>
                    </div>
                  </div>

                  {/* --- INTERACTIVE: simple_simulator.py / pi_flight.py --- */}
                  <div className="rounded-lg border border-cyan-500/30 bg-cyan-500/5 p-3">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="px-2 py-0.5 rounded bg-cyan-500/20 border border-cyan-500/30 text-[7px] text-cyan-300 font-black">INTERACTIVE</span>
                    </div>
                    <div className="text-[8px] text-cyan-400 font-bold">simple_simulator.py / pi_flight.py</div>
                    <div className="text-[7px] text-zinc-600 mb-2 italic">No enum state machine. Boolean flags + phase strings.</div>

                    {/* Flags diagram */}
                    <div className="text-[6.5px] text-zinc-600 mb-1.5 uppercase tracking-wider font-bold">Mode flags (toggleable, not a state machine):</div>
                    <div className="grid grid-cols-2 gap-1 text-[6.5px] mb-2">
                      <div className="px-1.5 py-0.5 rounded bg-blue-500/10 border border-blue-500/20 text-blue-300">C &rarr; centering</div>
                      <div className="px-1.5 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/20 text-emerald-300">V &rarr; visual_servo</div>
                      <div className="px-1.5 py-0.5 rounded bg-amber-500/10 border border-amber-500/20 text-amber-300">G &rarr; locking (30s)</div>
                      <div className="px-1.5 py-0.5 rounded bg-purple-500/10 border border-purple-500/20 text-purple-300">N &rarr; investigating</div>
                    </div>

                    {/* Investigation phase machine */}
                    <div className="text-[6.5px] text-zinc-600 mb-1 uppercase tracking-wider font-bold">N &rarr; investigate_phase (nested):</div>
                    <div className="flex flex-col gap-0 font-mono text-[7px]">
                      <div className="flex items-start gap-1.5">
                        <div className="flex flex-col items-center shrink-0">
                          <span className="w-2 h-2 rounded-full bg-amber-500/40 border border-amber-500/50" />
                          <span className="w-px h-2.5 border-l border-dashed border-zinc-700" />
                        </div>
                        <span className="text-zinc-500"><span className="text-amber-400">&quot;approaching&quot;</span> fly to cluster GPS</span>
                      </div>
                      <div className="flex items-start gap-1.5">
                        <div className="flex flex-col items-center shrink-0">
                          <span className="w-2 h-2 rounded-full bg-purple-500/40 border border-purple-500/50" />
                          <span className="w-px h-2.5 border-l border-dashed border-zinc-700" />
                        </div>
                        <span className="text-zinc-500"><span className="text-purple-400">&quot;descending&quot;</span> drop to 15m, hold</span>
                      </div>
                      <div className="flex items-start gap-1.5">
                        <div className="flex flex-col items-center shrink-0">
                          <span className="w-2 h-2 rounded-full bg-cyan-500/40 border border-cyan-500/50" />
                        </div>
                        <span className="text-zinc-500"><span className="text-cyan-400">&quot;observing&quot;</span> hover, pilot classifies:</span>
                      </div>
                    </div>

                    {/* Classification */}
                    <div className="ml-4 mt-1 space-y-0.5 text-[6.5px]">
                      <div className="px-1.5 py-0.5 rounded bg-green-500/5 border border-green-500/20">
                        <span className="text-green-400 font-black">Y</span>
                        <span className="text-zinc-500 ml-1">confirm &rarr; L &rarr; fly 7.5m north &rarr; land</span>
                      </div>
                      <div className="px-1.5 py-0.5 rounded bg-cyan-500/5 border border-cyan-500/20">
                        <span className="text-cyan-400 font-black">I</span>
                        <span className="text-zinc-500 ml-1">interest &rarr; log GPS &rarr; reset &rarr; resume</span>
                      </div>
                      <div className="px-1.5 py-0.5 rounded bg-red-500/5 border border-red-500/20">
                        <span className="text-red-400 font-black">X</span>
                        <span className="text-zinc-500 ml-1">false pos &rarr; delete cluster &rarr; resume</span>
                      </div>
                    </div>

                    <div className="mt-2.5 space-y-0.5 text-[6.5px]">
                      <div className="px-1.5 py-0.5 rounded bg-zinc-900/60 border border-zinc-800/50">
                        <span className="text-cyan-400 font-bold">COMMANDS:</span>
                        <span className="text-zinc-500 ml-1">goto(), land() &mdash; only on operator input</span>
                      </div>
                      <div className="px-1.5 py-0.5 rounded bg-zinc-900/60 border border-zinc-800/50">
                        <span className="text-zinc-400 font-bold">CUBE:</span>
                        <span className="text-zinc-500 ml-1">GUIDED. WASD/RC always overrides.</span>
                      </div>
                      <div className="px-1.5 py-0.5 rounded bg-zinc-900/60 border border-zinc-800/50">
                        <span className="text-zinc-400 font-bold">SEARCH:</span>
                        <span className="text-zinc-500 ml-1">Manual (pilot flies). No lawnmower.</span>
                      </div>
                    </div>

                    <div className="mt-2 px-1.5 py-1 rounded bg-cyan-500/10 border border-cyan-500/20 text-[6.5px] text-center">
                      <div className="text-zinc-400">AI proposes. <span className="text-cyan-300 font-bold">Human decides.</span> Drone executes.</div>
                      <div className="text-zinc-600">Flags, not states. Any WASD cancels autonomy.</div>
                    </div>
                  </div>

                  {/* --- AUTONOMOUS: main.py --- */}
                  <div className="rounded-lg border border-red-500/30 bg-red-500/5 p-3">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="px-2 py-0.5 rounded bg-red-500/20 border border-red-500/30 text-[7px] text-red-300 font-black">AUTONOMOUS</span>
                    </div>
                    <div className="text-[8px] text-red-400 font-bold">main.py</div>
                    <div className="text-[7px] text-zinc-600 mb-2 italic">Real state machine. Enum in states.py. 15 states.</div>

                    {/* State machine flow */}
                    <div className="flex flex-col gap-0 font-mono text-[7px]">
                      <div className="flex items-start gap-1.5">
                        <div className="flex flex-col items-center shrink-0">
                          <span className="w-2 h-2 rounded-full bg-zinc-600/40 border border-zinc-600/50" />
                          <span className="w-px h-2.5 border-l border-dashed border-zinc-700" />
                        </div>
                        <span className="text-zinc-500"><span className="text-zinc-300">INIT &rarr; CONNECTING</span> heartbeat</span>
                      </div>
                      <div className="flex items-start gap-1.5">
                        <div className="flex flex-col items-center shrink-0">
                          <span className="w-2 h-2 rounded-full bg-amber-500/40 border border-amber-500/50" />
                          <span className="w-px h-2.5 border-l border-dashed border-zinc-700" />
                        </div>
                        <span className="text-zinc-500"><span className="text-amber-400">ARMING &rarr; TAKEOFF</span> GUIDED + arm</span>
                      </div>
                      <div className="flex items-start gap-1.5">
                        <div className="flex flex-col items-center shrink-0">
                          <span className="w-2 h-2 rounded-full bg-blue-500/40 border border-blue-500/50" />
                          <span className="w-px h-2.5 border-l border-dashed border-zinc-700" />
                        </div>
                        <span className="text-zinc-500"><span className="text-blue-400">SEARCH</span> auto lawnmower pattern</span>
                      </div>
                      <div className="flex items-start gap-1.5">
                        <div className="flex flex-col items-center shrink-0">
                          <span className="w-2 h-2 rounded-full bg-emerald-500/40 border border-emerald-500/50" />
                          <span className="w-px h-2.5 border-l border-dashed border-zinc-700" />
                        </div>
                        <span className="text-zinc-500"><span className="text-emerald-400">CENTERING</span> auto-fly to detection GPS</span>
                      </div>
                      <div className="flex items-start gap-1.5">
                        <div className="flex flex-col items-center shrink-0">
                          <span className="w-2 h-2 rounded-full bg-purple-500/40 border border-purple-500/50" />
                          <span className="w-px h-2.5 border-l border-dashed border-zinc-700" />
                        </div>
                        <span className="text-zinc-500"><span className="text-purple-400">DESCENDING</span> drop to 15m verify alt</span>
                      </div>
                      <div className="flex items-start gap-1.5">
                        <div className="flex flex-col items-center shrink-0">
                          <span className="w-2 h-2 rounded-full bg-cyan-500/40 border border-cyan-500/50" />
                          <span className="w-px h-2.5 border-l border-dashed border-zinc-700" />
                        </div>
                        <span className="text-zinc-500"><span className="text-cyan-400">VERIFY</span> operator Y/N only</span>
                      </div>
                      <div className="flex items-start gap-1.5">
                        <div className="flex flex-col items-center shrink-0">
                          <span className="w-2 h-2 rounded-full bg-green-500/40 border border-green-500/50" />
                          <span className="w-px h-2.5 border-l border-dashed border-zinc-700" />
                        </div>
                        <span className="text-zinc-500"><span className="text-green-400">APPROACH</span> fly 7.5m offset (N/E/S/W)</span>
                      </div>
                      <div className="flex items-start gap-1.5">
                        <div className="flex flex-col items-center shrink-0">
                          <span className="w-2 h-2 rounded-full bg-red-500/40 border border-red-500/50" />
                        </div>
                        <span className="text-zinc-500"><span className="text-red-400">LANDING &rarr; DONE</span> touch down + disarm</span>
                      </div>
                    </div>

                    <div className="mt-2.5 space-y-0.5 text-[6.5px]">
                      <div className="px-1.5 py-0.5 rounded bg-zinc-900/60 border border-zinc-800/50">
                        <span className="text-red-400 font-bold">COMMANDS:</span>
                        <span className="text-zinc-500 ml-1">arm, takeoff, goto, land &mdash; automatic</span>
                      </div>
                      <div className="px-1.5 py-0.5 rounded bg-zinc-900/60 border border-zinc-800/50">
                        <span className="text-zinc-400 font-bold">CUBE:</span>
                        <span className="text-zinc-500 ml-1">GUIDED entire mission. M key = manual.</span>
                      </div>
                      <div className="px-1.5 py-0.5 rounded bg-zinc-900/60 border border-zinc-800/50">
                        <span className="text-zinc-400 font-bold">SEARCH:</span>
                        <span className="text-zinc-500 ml-1">Auto lawnmower. CV auto-triggers centering.</span>
                      </div>
                      <div className="px-1.5 py-0.5 rounded bg-zinc-900/60 border border-zinc-800/50">
                        <span className="text-zinc-400 font-bold">VERIFY:</span>
                        <span className="text-zinc-500 ml-1">Y/N only. No I/X (no multi-target).</span>
                      </div>
                    </div>

                    <div className="mt-2 px-1.5 py-1 rounded bg-red-500/10 border border-red-500/20 text-[6.5px] text-center">
                      <div className="text-zinc-400">Real <span className="text-red-300 font-bold">enum state machine</span> in states.py</div>
                      <div className="text-zinc-600">One state at a time. Each transition explicit.</div>
                    </div>
                  </div>
                </div>

                {/* Key differences table */}
                <div className="mt-3 rounded bg-zinc-800/40 border border-zinc-700/30 overflow-hidden">
                  <table className="w-full text-[7px]">
                    <thead>
                      <tr className="border-b border-zinc-700/30">
                        <th className="text-left px-2 py-1 text-zinc-500 font-bold"></th>
                        <th className="text-center px-2 py-1 text-zinc-400 font-bold">pi_passive_flight</th>
                        <th className="text-center px-2 py-1 text-cyan-400 font-bold">simple_sim / pi_flight</th>
                        <th className="text-center px-2 py-1 text-red-400 font-bold">main.py</th>
                      </tr>
                    </thead>
                    <tbody className="text-zinc-500">
                      <tr className="border-b border-zinc-800/50">
                        <td className="px-2 py-0.5 text-zinc-400 font-bold">Architecture</td>
                        <td className="px-2 py-0.5 text-center">while loop</td>
                        <td className="px-2 py-0.5 text-center">bool flags + phase strings</td>
                        <td className="px-2 py-0.5 text-center">enum state machine</td>
                      </tr>
                      <tr className="border-b border-zinc-800/50">
                        <td className="px-2 py-0.5 text-zinc-400 font-bold">Search</td>
                        <td className="px-2 py-0.5 text-center">pilot flies RC</td>
                        <td className="px-2 py-0.5 text-center">pilot flies (WASD / RC)</td>
                        <td className="px-2 py-0.5 text-center">auto lawnmower</td>
                      </tr>
                      <tr className="border-b border-zinc-800/50">
                        <td className="px-2 py-0.5 text-zinc-400 font-bold">On detection</td>
                        <td className="px-2 py-0.5 text-center">log + beep</td>
                        <td className="px-2 py-0.5 text-center">cluster + wait for N</td>
                        <td className="px-2 py-0.5 text-center">auto &rarr; CENTERING</td>
                      </tr>
                      <tr className="border-b border-zinc-800/50">
                        <td className="px-2 py-0.5 text-zinc-400 font-bold">Classification</td>
                        <td className="px-2 py-0.5 text-center">none</td>
                        <td className="px-2 py-0.5 text-center">Y / I / X (3 options)</td>
                        <td className="px-2 py-0.5 text-center">Y / N (2 options)</td>
                      </tr>
                      <tr className="border-b border-zinc-800/50">
                        <td className="px-2 py-0.5 text-zinc-400 font-bold">Multi-target</td>
                        <td className="px-2 py-0.5 text-center">no</td>
                        <td className="px-2 py-0.5 text-center text-cyan-400">yes (spatial clusters)</td>
                        <td className="px-2 py-0.5 text-center">no (first detection)</td>
                      </tr>
                      <tr>
                        <td className="px-2 py-0.5 text-zinc-400 font-bold">Flight commands</td>
                        <td className="px-2 py-0.5 text-center text-red-400">zero</td>
                        <td className="px-2 py-0.5 text-center">on operator input</td>
                        <td className="px-2 py-0.5 text-center">automatic</td>
                      </tr>
                    </tbody>
                  </table>
                </div>

                {/* Bottom: progression */}
                <div className="mt-3 px-3 py-2 rounded bg-zinc-800/40 border border-zinc-700/30 text-[7px] text-zinc-500">
                  <span className="text-cyan-400/80 font-bold">Flight testing progression:</span> Start with <span className="text-zinc-300">passive</span> (Step 2 &mdash; prove CV works outdoors, zero risk). Then <span className="text-cyan-300">interactive</span> (Step 3 &mdash; pilot searches manually, operator classifies detections via dashboard). Then <span className="text-red-300">autonomous</span> (Step 5 &mdash; drone searches, detects, verifies, and lands by itself). Each step builds trust before adding autonomy.
                </div>
              </div>

              {/* Startup sequence */}
              <div className="col-span-2 rounded-lg border border-blue-500/20 bg-blue-500/5 p-4">
                <div className="text-[9px] text-blue-400 uppercase tracking-widest font-bold mb-2">Pi Startup Sequence (3 terminals)</div>
                <div className="grid grid-cols-3 gap-3 text-[8px]">
                  <div className="px-3 py-2 rounded bg-zinc-800/40 border border-zinc-700/30">
                    <div className="text-pink-400 font-bold mb-1">Terminal 1: mavproxy</div>
                    <div className="font-mono text-[6px] text-zinc-500 break-all">sudo /opt/mavlink/mavlink-venv/bin/mavproxy.py --master=/dev/ttyAMA0 --baudrate=921600 --streamrate=10 --out=udpout:127.0.0.1:14550 --out=tcpin:0.0.0.0:5762</div>
                    <div className="text-zinc-600 text-[7px] mt-1">Must start FIRST. Bridges serial &rarr; network.</div>
                  </div>
                  <div className="px-3 py-2 rounded bg-zinc-800/40 border border-zinc-700/30">
                    <div className="text-blue-400 font-bold mb-1">Terminal 2: flight script</div>
                    <div className="font-mono text-[6px] text-zinc-500">cd ~/dima/Group_Proj && source pienv/bin/activate && python3 pi_flight.py</div>
                    <div className="text-zinc-600 text-[7px] mt-1">Camera + CV + ground station at :8090</div>
                  </div>
                  <div className="px-3 py-2 rounded bg-zinc-800/40 border border-zinc-700/30">
                    <div className="text-zinc-400 font-bold mb-1">Laptop: browser</div>
                    <div className="font-mono text-[6px] text-zinc-500">http://192.168.1.121:8090</div>
                    <div className="text-zinc-600 text-[7px] mt-1">Opens dashboard. Also connect Mission Planner TCP to :5762.</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Components by category */}
      {HARDWARE_CATEGORIES.map(cat => {
        const items = HARDWARE_COMPONENTS.filter(c => c.category === cat.id);
        if (items.length === 0) return null;
        return (
          <div key={cat.id}>
            <div className="flex items-center gap-2 mb-2">
              <div className="w-2 h-2 rounded-full" style={{ background: cat.color }} />
              <span className="text-[10px] font-bold" style={{ color: cat.color }}>{cat.label}</span>
              <span className="text-[8px] text-zinc-600">{items.length}</span>
            </div>
            <div className="grid grid-cols-2 gap-1">
              {items.map(comp => (
                <ComponentCard
                  key={comp.id}
                  comp={comp}
                  catColor={cat.color}
                  isExpanded={expandedId === comp.id}
                  onToggle={() => setExpandedId(expandedId === comp.id ? null : comp.id)}
                />
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}

function ComponentCard({ comp, catColor, isExpanded, onToggle }: {
  comp: HardwareComponent;
  catColor: string;
  isExpanded: boolean;
  onToggle: () => void;
}) {
  const st = STATUS_STYLE[comp.status];
  return (
    <div className={`rounded-lg border transition-all overflow-hidden ${isExpanded ? "col-span-2" : ""}`}
      style={{
        borderColor: isExpanded ? catColor + "40" : "rgba(63,63,70,0.3)",
        background: isExpanded ? catColor + "03" : "rgba(24,24,27,0.3)",
      }}>
      {/* Header */}
      <button onClick={onToggle}
        className="w-full flex items-center gap-3 px-4 py-2.5 hover:bg-zinc-800/20 transition-all text-left">
        <span className="text-[9px] text-zinc-600">{isExpanded ? "\u25BC" : "\u25B6"}</span>
        <span className="text-[11px] font-bold text-zinc-200">{comp.name}</span>
        <span className="text-[8px] text-zinc-500">{comp.role}</span>
        <span className="text-[7px] font-bold px-1.5 py-0.5 rounded ml-auto"
          style={{ color: st.color, background: st.color + "15" }}>
          {st.label}
        </span>
      </button>

      {/* Expanded detail */}
      {isExpanded && (
        <div className="px-4 pb-4 space-y-3">
          <div className="text-[9px] text-zinc-400 leading-relaxed">{comp.description}</div>

          {/* Connection info */}
          {comp.connectionDetails && (
            <div className="px-3 py-2 rounded bg-zinc-900/80 border border-zinc-800/50">
              <div className="text-[8px] text-cyan-500 uppercase tracking-wider font-bold mb-1">Physical Connection</div>
              <div className="text-[9px] text-zinc-400">{comp.connectionDetails}</div>
            </div>
          )}

          {/* Specs */}
          {comp.specs && comp.specs.length > 0 && (
            <div>
              <div className="text-[8px] text-zinc-500 uppercase tracking-wider font-bold mb-1">Specs</div>
              <div className="grid grid-cols-2 gap-x-4 gap-y-0.5">
                {comp.specs.map(s => (
                  <div key={s.label} className="flex items-baseline gap-2 text-[8px]">
                    <span className="text-zinc-600 shrink-0">{s.label}:</span>
                    <span className="text-zinc-300">{s.value}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Setup steps */}
          <div>
            <div className="text-[8px] text-zinc-500 uppercase tracking-wider font-bold mb-1">Setup Steps</div>
            <div className="space-y-0.5">
              {comp.setupSteps.map((step, i) => (
                <div key={i} className="flex gap-2 text-[8px]">
                  <span className="text-zinc-700 shrink-0 w-4 text-right">{i + 1}.</span>
                  <span className="text-zinc-400 font-mono leading-relaxed">{step}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Test commands */}
          {comp.testCommands && comp.testCommands.length > 0 && (
            <div>
              <div className="text-[8px] text-green-500/80 uppercase tracking-wider font-bold mb-1">How to Test</div>
              <div className="space-y-1">
                {comp.testCommands.map((t, i) => (
                  <div key={i} className="px-2 py-1.5 rounded bg-zinc-900/50 border border-zinc-800/50">
                    <div className="text-[9px] text-green-400 font-mono">{t.command}</div>
                    <div className="text-[8px] text-zinc-600 mt-0.5">Expected: {t.expect}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Guides & links */}
          {comp.guides.length > 0 && (
            <div>
              <div className="text-[8px] text-zinc-500 uppercase tracking-wider font-bold mb-1">Guides & Documentation</div>
              <div className="space-y-1">
                {comp.guides.map(g => (
                  <div key={g.label} className="flex items-start gap-2 px-2 py-1.5 rounded bg-zinc-900/50 border border-zinc-800/50 hover:bg-zinc-800/30 transition-all">
                    {g.url ? (
                      <a href={g.url} target="_blank" rel="noopener noreferrer"
                        className="text-[9px] text-blue-400 hover:text-blue-300 shrink-0 font-medium">
                        {g.label}
                      </a>
                    ) : (
                      <span className="text-[9px] text-zinc-300 shrink-0 font-medium">{g.label}</span>
                    )}
                    <span className="text-[8px] text-zinc-600">{g.description}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Notes */}
          {comp.notes && comp.notes.length > 0 && (
            <div>
              <div className="text-[8px] text-amber-500/80 uppercase tracking-wider font-bold mb-1">Notes</div>
              <div className="space-y-0.5">
                {comp.notes.map((n, i) => (
                  <div key={i} className="flex items-start gap-2 text-[8px]">
                    <span className="text-amber-500 shrink-0 mt-0.5">!</span>
                    <span className="text-zinc-500">{n}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
