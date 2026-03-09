/**
 * Group Project Tab — SAR Drone Mission Architect (v3)
 *
 * 3-panel layout:
 *   LEFT  (~260px): SE Strategy & Methodology sidebar
 *   CENTER (flex-1): Main content — big picture, levels, approaches, layers, diagnostics
 *   RIGHT  (~220px): Compute trade study, team, test scope reference
 */
import { useState, useMemo } from "react";
import { LEVELS, TEAM } from "./group-project-v2-data";

// Extracted components
import {
  HolyGrailBanner, LevelSelector, AmbitionPanel, EvolutionTracker,
  DroneBlueprintSVG, SELayerStack, ApproachSelector, ApproachDetail,
  DiagnosticProtocol, RightSidebar,
} from "./GroupProjectV2Components";

// New v3 components
import MethodologySidebar from "./MethodologyV2Sidebar";
import BigPictureView from "./BigPictureV2View";
import ContributionMatrix from "./ContributionV2Matrix";
import IntegrationOversight from "./IntegrationV2Oversight";
import MissionReadiness from "./MissionV2Readiness";

export default function GroupProjectTab() {
  const [activeLevel, setActiveLevel] = useState(1);
  const [selectedApproachId, setSelectedApproachId] = useState<string>("1a");
  const [showLeftSidebar, setShowLeftSidebar] = useState(true);

  const level = useMemo(() => LEVELS.find(l => l.id === activeLevel)!, [activeLevel]);
  const approach = useMemo(
    () => level.approaches.find(a => a.id === selectedApproachId) || level.approaches[0],
    [level, selectedApproachId],
  );

  const handleLevelChange = (id: number) => {
    setActiveLevel(id);
    const newLevel = LEVELS.find(l => l.id === id)!;
    setSelectedApproachId(newLevel.approaches[0].id);
  };

  return (
    <>
      {/* LEFT SIDEBAR — SE Strategy & Methodology */}
      {showLeftSidebar && (
        <div className="w-64 border-r border-zinc-800 bg-zinc-900/60 p-3 overflow-y-auto shrink-0">
          <MethodologySidebar />
        </div>
      )}

      {/* MAIN CONTENT */}
      <div className="flex-1 overflow-y-auto p-6 space-y-0 min-w-0">
        {/* Toggle left sidebar */}
        <div className="flex justify-end mb-2">
          <button onClick={() => setShowLeftSidebar(s => !s)}
            className="text-[8px] px-2 py-1 rounded border border-zinc-700/50 text-zinc-500 hover:text-zinc-300 transition-all">
            {showLeftSidebar ? "\u25C0 Hide" : "\u25B6 Show"} Strategy
          </button>
        </div>

        <HolyGrailBanner />
        <BigPictureView activeLevel={activeLevel} onSelectLevel={handleLevelChange} />

        {/* Level detail */}
        <LevelSelector levels={LEVELS} activeId={activeLevel} onSelect={handleLevelChange} />
        <AmbitionPanel level={level} />
        <EvolutionTracker level={level} />

        {/* Approach selection */}
        <div className="mb-0">
          <h3 className="text-[13px] font-bold text-zinc-100 mb-1">Architectural Approaches</h3>
          <p className="text-[10px] text-zinc-500 mb-3">3 options for {level.name}. Selection changes Layers 3-5 in the stack below.</p>
          <ApproachSelector approaches={level.approaches} selectedId={selectedApproachId} onSelect={setSelectedApproachId} />
        </div>
        <ApproachDetail approach={approach} />

        {/* Contribution Matrix (tasks x people x goals) */}
        <ContributionMatrix approach={approach} />

        {/* SE Layer Stack */}
        <SELayerStack level={level} approach={approach} />

        {/* Drone Blueprint */}
        <DroneBlueprintSVG activeLevel={activeLevel} />

        {/* Integration Oversight */}
        <IntegrationOversight />

        {/* Mission Readiness (equipment tiers, emergency procedures, risk matrix) */}
        <MissionReadiness activeLevel={activeLevel} />

        {/* Diagnostic Protocol */}
        <DiagnosticProtocol />
      </div>

      {/* RIGHT SIDEBAR — Compute Trade Study + Reference */}
      <div className="w-56 border-l border-zinc-800 bg-zinc-900/60 p-3 overflow-y-auto shrink-0">
        <RightSidebar team={TEAM} />
      </div>
    </>
  );
}
