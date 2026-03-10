import { useState, useEffect } from "react";
import ReadmeTab from "./pages/ReadmeTab";
import MissionTab from "./pages/MissionTab";
import LevelsTab from "./pages/LevelsTab";
import RoadmapTab from "./pages/RoadmapTab";
import HubPage from "./pages/HubPage";
import GroupProjectV2Tab from "./pages/GroupProjectV2Tab";
import MissionWBSTab from "./pages/MissionWBSTab";
import TeamTab from "./pages/TeamTab";
import NotesTab from "./pages/NotesTab";
import HardwareTab from "./pages/HardwareTab";
import TopBar, { type TopPanel } from "./pages/TopBar";
import TopPanels from "./pages/TopPanels";
import LeftSidebar from "./pages/LeftSidebar";
import RightSidebar from "./pages/RightSidebar";
import PrepSidebar from "./pages/PrepSidebar";

type Tab = "readme" | "mission" | "hardware" | "levels" | "roadmap" | "hub" | "team" | "notes" | "gp-v2" | "wbs";

const TABS: { id: Tab; label: string; description: string }[] = [
  { id: "readme", label: "README", description: "Complete project overview — share with your team to understand everything" },
  { id: "mission", label: "Mission", description: "The what: scenario, requirements, constraints, deliverables" },
  { id: "hardware", label: "Hardware", description: "All components, connections, setup guides, and links" },
  { id: "levels", label: "Levels", description: "The how: 3 product levels — Manual → Semi-Auto → Full Auto" },
  { id: "roadmap", label: "Roadmap", description: "Stepping stones to reach each level" },
  { id: "hub", label: "Hub", description: "Project status, flight testing, architecture" },
  { id: "team", label: "Team", description: "Who's doing what, level focus, blockers" },
  { id: "notes", label: "Notes", description: "All ideas, wants, and plans" },
  { id: "gp-v2", label: "GP v2 (Snapshot)", description: "SE Strategy, Levels, Approaches, Team" },
  { id: "wbs", label: "Mission WBS", description: "90 tasks, 7 subsystems, bottom-up progress" },
];

export default function App() {
  const [activeTab, setActiveTab] = useState<Tab>("readme");
  const [activePanel, setActivePanel] = useState<TopPanel>(null);
  const [showLeft, setShowLeft] = useState(false);
  const [showRight, setShowRight] = useState(false);
  const [showPrep, setShowPrep] = useState(true);

  // Ctrl+L = toggle left sidebar, Ctrl+R = toggle right sidebar
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.ctrlKey && e.key === "l") {
        e.preventDefault();
        setShowLeft(prev => !prev);
      }
      if (e.ctrlKey && e.key === "r") {
        e.preventDefault();
        setShowRight(prev => !prev);
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, []);

  return (
    <div className="h-screen flex flex-col bg-zinc-950 text-zinc-100 overflow-hidden relative">
      {/* Top bar — icon strip with panel toggles */}
      <TopBar activePanel={activePanel} onTogglePanel={setActivePanel} />

      {/* Overlay panels (from top bar) */}
      <TopPanels activePanel={activePanel} onClose={() => setActivePanel(null)} />

      {/* Tab bar */}
      <div className="border-b border-zinc-800 bg-zinc-900/60 px-4 flex items-center gap-1 shrink-0">
        {TABS.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-3 py-1.5 text-[11px] transition-all border-b-2 ${
              activeTab === tab.id
                ? "text-white border-blue-500"
                : "text-zinc-500 border-transparent hover:text-zinc-300 hover:border-zinc-700"
            }`}
          >
            {tab.label}
          </button>
        ))}
        <span className="text-[9px] text-zinc-600 ml-auto">
          {TABS.find(t => t.id === activeTab)?.description}
        </span>
        <button
          onClick={() => setShowPrep(prev => !prev)}
          className={`ml-2 px-2 py-1 text-[9px] rounded transition-all ${
            showPrep ? "text-amber-400 bg-amber-500/10" : "text-zinc-600 hover:text-zinc-400"
          }`}
        >
          Prep
        </button>
      </div>

      {/* Main content with optional sidebars */}
      <div className="flex flex-1 overflow-hidden">
        {showLeft && <LeftSidebar />}

        <div className="flex-1 flex overflow-hidden">
          {activeTab === "readme" && <ReadmeTab />}
          {activeTab === "mission" && <MissionTab />}
          {activeTab === "hardware" && <HardwareTab />}
          {activeTab === "levels" && <LevelsTab />}
          {activeTab === "roadmap" && <RoadmapTab />}
          {activeTab === "hub" && <HubPage />}
          {activeTab === "team" && <TeamTab />}
          {activeTab === "notes" && <NotesTab />}
          {activeTab === "gp-v2" && <GroupProjectV2Tab />}
          {activeTab === "wbs" && <MissionWBSTab />}
        </div>

        {showRight && <RightSidebar />}
        {showPrep && <PrepSidebar />}
      </div>
    </div>
  );
}
