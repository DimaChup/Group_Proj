import { useState } from "react";
import GroupProjectV2Tab from "./pages/GroupProjectV2Tab";
import MissionWBSTab from "./pages/MissionWBSTab";

type Tab = "gp-v2" | "wbs";

const TABS: { id: Tab; label: string; description: string }[] = [
  { id: "gp-v2", label: "GP v2 (Snapshot)", description: "SE Strategy, Levels, Approaches, Team" },
  { id: "wbs", label: "Mission WBS", description: "90 tasks, 7 subsystems, bottom-up progress" },
];

export default function App() {
  const [activeTab, setActiveTab] = useState<Tab>("gp-v2");

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100">
      {/* Header */}
      <div className="border-b border-zinc-800 bg-zinc-900/80 px-6 py-3">
        <div className="flex items-center gap-6">
          <h1 className="text-lg font-bold tracking-tight">SAR Drone Dashboard</h1>
          <div className="flex gap-1">
            {TABS.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-2 text-sm rounded-t transition-all ${
                  activeTab === tab.id
                    ? "bg-zinc-800 text-white border border-zinc-700 border-b-0"
                    : "text-zinc-500 hover:text-zinc-300 hover:bg-zinc-800/50"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
          <span className="text-[10px] text-zinc-600 ml-auto">
            {TABS.find(t => t.id === activeTab)?.description}
          </span>
        </div>
      </div>

      {/* Content */}
      <div className="flex flex-1" style={{ height: "calc(100vh - 57px)" }}>
        {activeTab === "gp-v2" && <GroupProjectV2Tab />}
        {activeTab === "wbs" && <MissionWBSTab />}
      </div>
    </div>
  );
}
