/**
 * NotesTab — All ideas, wants, and plans laid out clearly
 *
 * Data source: edit NOTES array below to add/update items.
 * Categories: want (things user wants built), idea (future possibility),
 *             fix (known issues), done (completed).
 */

type NoteStatus = "want" | "idea" | "doing" | "done" | "fix";

interface Note {
  status: NoteStatus;
  category: string;
  title: string;
  detail?: string;
}

const STATUS_STYLE: Record<NoteStatus, { color: string; bg: string; label: string }> = {
  want:  { color: "#f59e0b", bg: "rgba(245,158,11,0.08)", label: "WANT" },
  idea:  { color: "#8b5cf6", bg: "rgba(139,92,246,0.08)", label: "IDEA" },
  doing: { color: "#3b82f6", bg: "rgba(59,130,246,0.08)", label: "DOING" },
  done:  { color: "#22c55e", bg: "rgba(34,197,94,0.08)",  label: "DONE" },
  fix:   { color: "#ef4444", bg: "rgba(239,68,68,0.08)",  label: "FIX" },
};

const CATEGORIES = [
  "Dashboard", "Flight", "CV / Model", "Hardware", "Team", "Docs",
];

/** ─── ALL NOTES ─── edit here to add/update */
const NOTES: Note[] = [
  // Dashboard
  { status: "done", category: "Dashboard", title: "Copy GP v2 + WBS tabs from Orgnaiser" },
  { status: "done", category: "Dashboard", title: "Hub page with subsystems, flight steps, architecture" },
  { status: "done", category: "Dashboard", title: "Top bar overlay panels (Status, Team, Docs, Ref, Log)" },
  { status: "done", category: "Dashboard", title: "Mission tab — constraints, goals, hardware" },
  { status: "done", category: "Dashboard", title: "Levels tab — L1/L2/L3 with drone vs pilot actions" },
  { status: "done", category: "Dashboard", title: "Roadmap tab — stepping stones with dependencies" },
  { status: "done", category: "Dashboard", title: "Team tab — who does what, level focus, blockers" },
  { status: "done", category: "Dashboard", title: "Notes tab — all ideas laid out (this tab)" },
  { status: "want", category: "Dashboard", title: "Update WBS task statuses to match real progress", detail: "Many tasks show 'upcoming' but are actually done" },
  { status: "want", category: "Dashboard", title: "Flight test results tab", detail: "Dates, outcomes, config values from each test" },
  { status: "idea", category: "Dashboard", title: "Detection image gallery", detail: "Show images from --save-detections with GPS overlay" },
  { status: "idea", category: "Dashboard", title: "Timeline / Gantt view of project phases" },
  { status: "idea", category: "Dashboard", title: "Make WBS editable in browser (localStorage)" },
  { status: "idea", category: "Dashboard", title: "Connect to v3/CLAUDE.md session log for auto-progress" },
  { status: "fix", category: "Dashboard", title: "Ctrl+L / Ctrl+R sidebars removed", detail: "Were dead code, now deleted. All content moved to top bar panels + tabs." },

  // Flight
  { status: "want", category: "Flight", title: "Outdoor GPS fix test", detail: "Take Pi+Cube outside, get 3D lock, verify coordinates" },
  { status: "want", category: "Flight", title: "Mission Planner AUTO waypoints (Step 1)", detail: "Fly simple square, no custom code. Proves hardware." },
  { status: "want", category: "Flight", title: "Manual flight + passive CV (Step 3)", detail: "Pilot flies RC, Pi detects+logs. Zero commands." },
  { status: "want", category: "Flight", title: "pi_flight.py on real Pi", detail: "Test browser dashboard, video stream, commands on actual hardware" },
  { status: "want", category: "Flight", title: "Full semi-auto mission (Step 5)", detail: "Search → detect → confirm → centre → land" },
  { status: "idea", category: "Flight", title: "Z mode — offset centering for safety", detail: "Keep target in right half of frame, never hover directly above casualty" },
  { status: "idea", category: "Flight", title: "Add GPS navigation error to SITL", detail: "More realistic landing simulation" },

  // CV / Model
  { status: "want", category: "CV / Model", title: "Export COCO person detector to TFLite", detail: "yolov8n.pt → tflite. Fallback if custom model fails outdoors." },
  { status: "want", category: "CV / Model", title: "Export INT8 quantized model", detail: "Faster inference on Pi at cost of accuracy" },
  { status: "want", category: "CV / Model", title: "Retrain with real camera images", detail: "Current model trained on synthetic composites only" },
  { status: "idea", category: "CV / Model", title: "Try YOLOv8s (larger model)", detail: "More accurate but slower. Benchmark on Pi." },
  { status: "idea", category: "CV / Model", title: "Lower confidence threshold to 0.25-0.3", detail: "Catch more detections, more false positives" },
  { status: "idea", category: "CV / Model", title: "Motion blur handling", detail: "Shorter exposure / higher shutter speed in picamera2" },

  // Hardware
  { status: "done", category: "Hardware", title: "Pi 5 setup (camera, AI, Cube connection)" },
  { status: "done", category: "Hardware", title: "Camera color fix (IMX296 BGR)" },
  { status: "done", category: "Hardware", title: "mavproxy bridge stable" },
  { status: "want", category: "Hardware", title: "Configure RC kill switch", detail: "STABILIZE mode on switch = instant manual override" },
  { status: "want", category: "Hardware", title: "FOV calibration on bench", detail: "Camera + ruler → update FOCAL_LENGTH_MM in config.py" },

  // Team
  { status: "want", category: "Team", title: "Get detection images to Robin", detail: "Run --save-detections during flights, share folder" },
  { status: "want", category: "Team", title: "Get real photos to Edward", detail: "Capture photos of dummy in grass at various altitudes for retraining" },
  { status: "want", category: "Team", title: "Assign member 5 a role" },

  // Docs
  { status: "done", category: "Docs", title: "CLAUDE.md — project ground truth" },
  { status: "done", category: "Docs", title: "Flight Day Checklist" },
  { status: "done", category: "Docs", title: "Pi Setup Guide" },
  { status: "want", category: "Docs", title: "Update docs after first real flight", detail: "Config values, detection altitudes, GPS accuracy" },
];

export default function NotesTab() {
  const counts = {
    want: NOTES.filter(n => n.status === "want").length,
    idea: NOTES.filter(n => n.status === "idea").length,
    doing: NOTES.filter(n => n.status === "doing").length,
    done: NOTES.filter(n => n.status === "done").length,
    fix: NOTES.filter(n => n.status === "fix").length,
  };

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-5 min-w-0">
      {/* Summary bar */}
      <div className="flex items-center gap-4">
        {(Object.keys(STATUS_STYLE) as NoteStatus[]).map(s => (
          <div key={s} className="flex items-center gap-1.5">
            <div className="w-2 h-2 rounded-full" style={{ background: STATUS_STYLE[s].color }} />
            <span className="text-[9px] font-bold" style={{ color: STATUS_STYLE[s].color }}>
              {counts[s]} {STATUS_STYLE[s].label}
            </span>
          </div>
        ))}
      </div>

      {/* By category */}
      {CATEGORIES.map(cat => {
        const items = NOTES.filter(n => n.category === cat);
        if (items.length === 0) return null;

        return (
          <div key={cat}>
            <h2 className="text-[11px] font-bold text-zinc-300 uppercase tracking-wider mb-2">{cat}</h2>
            <div className="space-y-0.5">
              {items.map((note, i) => {
                const s = STATUS_STYLE[note.status];
                return (
                  <div key={i} className="flex items-start gap-3 px-3 py-1.5 rounded hover:bg-zinc-800/30 transition-all">
                    <span className="text-[7px] px-1.5 py-0.5 rounded font-bold mt-0.5 shrink-0 w-10 text-center"
                      style={{ color: s.color, background: s.bg }}>
                      {s.label}
                    </span>
                    <div className="min-w-0">
                      <div className="text-[10px] text-zinc-200">{note.title}</div>
                      {note.detail && (
                        <div className="text-[8px] text-zinc-600 mt-0.5">{note.detail}</div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        );
      })}
    </div>
  );
}
