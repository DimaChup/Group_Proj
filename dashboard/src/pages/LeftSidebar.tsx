/**
 * LeftSidebar — Documentation Hub (Ctrl+L)
 * Grouped docs: guides, hardware, config, tests, reference, external manuals
 */
import { useState } from "react";
import { DOCS, type DocEntry } from "./hub-data";

const CATEGORIES: { id: DocEntry["category"]; label: string; color: string }[] = [
  { id: "guide", label: "Guides", color: "#22c55e" },
  { id: "hardware", label: "Hardware", color: "#f97316" },
  { id: "config", label: "Config", color: "#3b82f6" },
  { id: "test", label: "Test Scripts", color: "#8b5cf6" },
  { id: "reference", label: "Reference", color: "#6b7280" },
];

export default function LeftSidebar() {
  const [expandedCat, setExpandedCat] = useState<string | null>("guide");

  return (
    <div className="w-64 bg-zinc-900/95 border-r border-zinc-800 flex flex-col h-full backdrop-blur-sm shrink-0">
      <div className="p-3 border-b border-zinc-800">
        <h2 className="text-[11px] font-bold text-zinc-300 tracking-wider uppercase">Documentation</h2>
        <p className="text-[9px] text-zinc-600 mt-0.5">Project files & manuals</p>
      </div>

      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        {CATEGORIES.map(cat => {
          const items = DOCS.filter(d => d.category === cat.id);
          const isOpen = expandedCat === cat.id;

          return (
            <div key={cat.id}>
              <button
                onClick={() => setExpandedCat(isOpen ? null : cat.id)}
                className="w-full flex items-center gap-2 px-2 py-1.5 rounded hover:bg-zinc-800/50 transition-all"
              >
                <span className="text-[9px]" style={{ color: cat.color }}>
                  {isOpen ? "\u25BC" : "\u25B6"}
                </span>
                <span className="text-[10px] font-medium" style={{ color: cat.color }}>
                  {cat.label}
                </span>
                <span className="text-[8px] text-zinc-600 ml-auto">{items.length}</span>
              </button>

              {isOpen && (
                <div className="ml-4 space-y-0.5 mb-1">
                  {items.map(doc => (
                    <div key={doc.path}
                      className="px-2 py-1.5 rounded hover:bg-zinc-800/40 cursor-pointer transition-all group"
                    >
                      <div className="text-[10px] text-zinc-300 group-hover:text-white">{doc.title}</div>
                      <div className="text-[8px] text-zinc-600 leading-tight mt-0.5">{doc.description}</div>
                      <div className="text-[7px] text-zinc-700 mt-0.5 font-mono">{doc.path}</div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* External manuals */}
      <div className="p-3 border-t border-zinc-800">
        <h3 className="text-[9px] font-bold text-zinc-500 uppercase tracking-wider mb-1">External Manuals</h3>
        <div className="space-y-1">
          {[
            { label: "CubePilot Docs", desc: "CubeOrangePlus hardware" },
            { label: "ArduCopter Params", desc: "Full parameter reference" },
            { label: "MAVLink Messages", desc: "Protocol reference" },
            { label: "picamera2 Docs", desc: "Pi camera library" },
          ].map(m => (
            <div key={m.label} className="px-2 py-1 rounded hover:bg-zinc-800/40 cursor-pointer">
              <div className="text-[9px] text-zinc-400">{m.label}</div>
              <div className="text-[7px] text-zinc-600">{m.desc}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
