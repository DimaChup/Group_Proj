/**
 * PrepSidebar — Dima's Pre-Flight Prep Checklist
 * Always-visible sidebar on the right with core + bonus tasks.
 * Checkbox state persists in localStorage.
 */
import { useState, useEffect } from "react";

interface PrepTask {
  id: string;
  task: string;
  command?: string;
  detail: string;
  time: string;
}

const CORE_TASKS: PrepTask[] = [
  { id: "fov", task: "FOV Calibration", command: "python tests/calibration/fov_calibrate.py", detail: "Camera + ruler at known height. Update FOCAL_LENGTH_MM in config.py.", time: "10 min" },
  { id: "lens", task: "Lens Distortion Calibration", command: "python tests/calibration/lens_calibrate.py --board 9x6", detail: "Checkerboard, 10+ angles. Saves calibration_data.npz.", time: "15 min" },
  { id: "model", task: "Export Backup Model", command: "yolo export model=yolov8n.pt format=tflite", detail: "COCO person detector as TFLite fallback. Copy to models/.", time: "15 min" },
  { id: "compare", task: "Compare Models", command: "python tests/day_1_experiments/model_compare.py --frames 50", detail: "Benchmark all .tflite models. Pick the best.", time: "5 min" },
  { id: "dryrun", task: "Dry-Run Pattern", command: "python main.py --dry-run", detail: "Verify SEARCH_AREA_GPS covers the right field.", time: "2 min" },
  { id: "stream", task: "Test Video Stream", command: "python tests/diagnostics/camera_stream.py --with-detection", detail: "Open http://PI_IP:8090, confirm MJPEG feed + detection boxes.", time: "5 min" },
];

const BONUS_TASKS: PrepTask[] = [
  { id: "rc", task: "Test RC Connection", detail: "Bind RC to Cube, verify sticks in MP, test kill switch (STABILIZE), set failsafe = RTL.", time: "10 min" },
  { id: "arch", task: "Learn Connection Architecture", detail: "Cube-UART-Pi-mavproxy-UDP/TCP-MP-Browser-RC. Understand each link and port.", time: "15 min" },
  { id: "sim", task: "Run Simulations", command: "python simple_simulator.py", detail: "Practice field workflow: fly, detect, investigate, classify, land. Also test pi_flight.py in SIMULATION.", time: "30 min" },
  { id: "bench", task: "CV Benchmark on Pi", command: "python tests/hardware/benchmark.py", detail: "Get real FPS number. Set --fps flag to match on flight day.", time: "5 min" },
];

const STORAGE_KEY = "dima-prep-checked";

function loadChecked(): Set<string> {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) return new Set(JSON.parse(raw));
  } catch { /* ignore */ }
  return new Set();
}

export default function PrepSidebar() {
  const [checked, setChecked] = useState<Set<string>>(loadChecked);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify([...checked]));
  }, [checked]);

  const toggle = (id: string) => {
    setChecked(prev => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id); else next.add(id);
      return next;
    });
  };

  const coreCount = CORE_TASKS.filter(t => checked.has(t.id)).length;
  const bonusCount = BONUS_TASKS.filter(t => checked.has(t.id)).length;
  const totalDone = coreCount + bonusCount;
  const totalAll = CORE_TASKS.length + BONUS_TASKS.length;

  const TaskRow = ({ t }: { t: PrepTask }) => (
    <label
      key={t.id}
      className={`flex gap-2 px-2 py-1.5 rounded cursor-pointer transition-all hover:bg-zinc-800/40 ${
        checked.has(t.id) ? "opacity-50" : ""
      }`}
    >
      <input
        type="checkbox"
        checked={checked.has(t.id)}
        onChange={() => toggle(t.id)}
        className="mt-0.5 shrink-0 accent-amber-500"
      />
      <div className="min-w-0">
        <div className={`text-[10px] font-medium ${checked.has(t.id) ? "line-through text-zinc-500" : "text-zinc-200"}`}>
          {t.task}
          <span className="text-[8px] text-zinc-600 ml-1.5 font-normal">{t.time}</span>
        </div>
        {t.command && (
          <div className="text-[8px] text-blue-400/70 font-mono mt-0.5 truncate">{t.command}</div>
        )}
        <div className="text-[8px] text-zinc-500 leading-tight mt-0.5">{t.detail}</div>
      </div>
    </label>
  );

  return (
    <div className="w-72 bg-zinc-900/95 border-l border-zinc-800 flex flex-col h-full backdrop-blur-sm shrink-0">
      {/* Header */}
      <div className="p-3 border-b border-zinc-800">
        <div className="flex items-center justify-between">
          <h2 className="text-[11px] font-bold text-amber-400 tracking-wider uppercase">Dima's Prep</h2>
          <span className="text-[9px] text-zinc-500">{totalDone}/{totalAll}</span>
        </div>
        <p className="text-[9px] text-zinc-600 mt-0.5">Day before flight</p>
        {/* Progress bar */}
        <div className="mt-1.5 h-1 bg-zinc-800 rounded-full overflow-hidden">
          <div
            className="h-full bg-amber-500 transition-all duration-300 rounded-full"
            style={{ width: `${(totalDone / totalAll) * 100}%` }}
          />
        </div>
      </div>

      <div className="flex-1 overflow-y-auto">
        {/* Core tasks */}
        <div className="p-2">
          <div className="flex items-center gap-2 px-2 mb-1">
            <span className="text-[9px] font-bold text-zinc-400 uppercase tracking-wider">Core</span>
            <span className="text-[8px] text-zinc-600">{coreCount}/{CORE_TASKS.length}</span>
            {coreCount === CORE_TASKS.length && <span className="text-[8px] text-green-500">Done</span>}
          </div>
          <div className="space-y-0.5">
            {CORE_TASKS.map(t => <TaskRow key={t.id} t={t} />)}
          </div>
        </div>

        {/* Divider */}
        <div className="mx-3 border-t border-zinc-800/50 my-1" />

        {/* Bonus tasks */}
        <div className="p-2">
          <div className="flex items-center gap-2 px-2 mb-1">
            <span className="text-[9px] font-bold text-purple-400 uppercase tracking-wider">Bonus</span>
            <span className="text-[8px] text-zinc-600">{bonusCount}/{BONUS_TASKS.length}</span>
            {bonusCount === BONUS_TASKS.length && <span className="text-[8px] text-green-500">Done</span>}
          </div>
          <div className="space-y-0.5">
            {BONUS_TASKS.map(t => <TaskRow key={t.id} t={t} />)}
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="p-2 border-t border-zinc-800">
        <button
          onClick={() => setChecked(new Set())}
          className="w-full text-[8px] text-zinc-600 hover:text-zinc-400 py-1 transition-all"
        >
          Reset all
        </button>
      </div>
    </div>
  );
}
