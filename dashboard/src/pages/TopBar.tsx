/**
 * TopBar — Icon strip at top, click to toggle overlay panels
 *
 * Pattern from Orgnaiser: small buttons, one panel at a time,
 * backdrop click closes. Panels developed gradually.
 */
import { PROJECT_PHASE } from "./hub-data";

export type TopPanel = "status" | "team" | "docs" | "ref" | "log" | null;

interface TopBarProps {
  activePanel: TopPanel;
  onTogglePanel: (panel: TopPanel) => void;
}

const PANEL_DEFS: { id: Exclude<TopPanel, null>; label: string; icon: string; color: string }[] = [
  { id: "status", label: "Status", icon: "\u25C9", color: "#f59e0b" },
  { id: "team", label: "Team", icon: "\u2302", color: "#22c55e" },
  { id: "docs", label: "Docs", icon: "\u2630", color: "#3b82f6" },
  { id: "ref", label: "Quick Ref", icon: "\u2318", color: "#8b5cf6" },
  { id: "log", label: "Session Log", icon: "\u2261", color: "#6b7280" },
];

export default function TopBar({ activePanel, onTogglePanel }: TopBarProps) {
  const p = PROJECT_PHASE;

  return (
    <div className="h-9 bg-zinc-900/95 border-b border-zinc-800 flex items-center px-3 gap-1 shrink-0 z-50 select-none backdrop-blur-sm">
      {/* Panel toggle buttons */}
      {PANEL_DEFS.map(def => {
        const isActive = activePanel === def.id;
        return (
          <button key={def.id}
            onClick={() => onTogglePanel(isActive ? null : def.id)}
            className={`h-6 px-2 rounded flex items-center gap-1.5 text-[10px] transition-all ${
              isActive
                ? "text-white shadow-sm"
                : "text-zinc-600 hover:text-zinc-300 hover:bg-zinc-800/50"
            }`}
            style={isActive ? { background: def.color + "20", color: def.color } : undefined}
            title={def.label}
          >
            <span className="text-[12px]">{def.icon}</span>
            <span>{def.label}</span>
          </button>
        );
      })}

      {/* Spacer */}
      <div className="flex-1" />

      {/* Phase + progress (compact, always visible) */}
      <div className="flex items-center gap-3 text-[9px]">
        <span className="text-zinc-600">Phase:</span>
        <span className="text-amber-400">{p.current}</span>
        <div className="w-px h-3 bg-zinc-800" />
        <span className="text-zinc-600">Next:</span>
        <span className="text-cyan-400">{p.next}</span>
        {p.blocker && (
          <>
            <div className="w-px h-3 bg-zinc-800" />
            <span className="text-red-500">BLOCKED: {p.blocker}</span>
          </>
        )}
        <div className="w-16 h-1 bg-zinc-800 rounded-full overflow-hidden">
          <div className="h-full rounded-full"
            style={{
              width: `${p.progress}%`,
              background: p.progress < 30 ? "#ef4444" : p.progress < 70 ? "#f59e0b" : "#22c55e",
            }} />
        </div>
        <span className="text-zinc-700">{p.progress}%</span>
      </div>
    </div>
  );
}
