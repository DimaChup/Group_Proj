/**
 * Mission WBS Tab — Work Breakdown Structure Tree
 *
 * Vertical decomposition tree: final goal at top, atomic tasks at bottom.
 * Progress flows bottom-up. Color-coded by assignee + ambition level.
 * Collapsible branches, progress bars per branch, legend.
 */
import { useState, useMemo, useCallback } from "react";
import { WBS_TREE, ASSIGNEE_COLORS, LEVEL_COLORS, type WBSNode, type WBSStatus } from "./wbs-data";

// ═══════════════════════════════════════════════════════════
// Helpers
// ═══════════════════════════════════════════════════════════

/** Build a children lookup map */
function buildChildrenMap(nodes: WBSNode[]): Map<string, WBSNode[]> {
  const map = new Map<string, WBSNode[]>();
  for (const n of nodes) {
    if (n.parentId) {
      const arr = map.get(n.parentId) || [];
      arr.push(n);
      map.set(n.parentId, arr);
    }
  }
  return map;
}

/** Count leaf-node statuses under a node (recursive) */
function countStatuses(nodeId: string, childMap: Map<string, WBSNode[]>): Record<WBSStatus, number> {
  const counts: Record<WBSStatus, number> = { done: 0, active: 0, upcoming: 0, blocked: 0 };
  const children = childMap.get(nodeId);
  if (!children || children.length === 0) return counts; // leaf — counted by parent
  for (const child of children) {
    const grandchildren = childMap.get(child.id);
    if (!grandchildren || grandchildren.length === 0) {
      // leaf node
      counts[child.status]++;
    } else {
      // branch — recurse
      const sub = countStatuses(child.id, childMap);
      counts.done += sub.done;
      counts.active += sub.active;
      counts.upcoming += sub.upcoming;
      counts.blocked += sub.blocked;
    }
  }
  return counts;
}

const STATUS_ICON: Record<WBSStatus, { symbol: string; color: string }> = {
  done:     { symbol: "\u2713", color: "#22c55e" },
  active:   { symbol: "\u25CF", color: "#f59e0b" },
  upcoming: { symbol: "\u25CB", color: "#6b7280" },
  blocked:  { symbol: "\u2716", color: "#ef4444" },
};

const LEVEL_LABELS: Record<string, string> = {
  all: "All",
  "1": "L1",
  "2": "L2",
  "3": "L3",
};

// ═══════════════════════════════════════════════════════════
// Filter state
// ═══════════════════════════════════════════════════════════

type FilterAssignee = string | null;
type FilterLevel = string | null;

// ═══════════════════════════════════════════════════════════
// Tree Node Component
// ═══════════════════════════════════════════════════════════

function TreeNode({
  node,
  childMap,
  depth,
  collapsed,
  toggleCollapse,
  filterAssignee,
  filterLevel,
  selectedId,
  setSelectedId,
}: {
  node: WBSNode;
  childMap: Map<string, WBSNode[]>;
  depth: number;
  collapsed: Set<string>;
  toggleCollapse: (id: string) => void;
  filterAssignee: FilterAssignee;
  filterLevel: FilterLevel;
  selectedId: string | null;
  setSelectedId: (id: string | null) => void;
}) {
  const children = childMap.get(node.id) || [];
  const isLeaf = children.length === 0;
  const isCollapsed = collapsed.has(node.id);
  const isSelected = selectedId === node.id;

  // Filter visibility
  const matchesFilter = (n: WBSNode) => {
    if (filterAssignee && n.assignee !== filterAssignee) return false;
    if (filterLevel && String(n.level) !== filterLevel && n.level !== "all") return false;
    return true;
  };

  // Check if any descendant matches filter (to keep branch visible)
  const hasMatchingDescendant = useCallback((id: string): boolean => {
    const ch = childMap.get(id) || [];
    for (const c of ch) {
      if (matchesFilter(c)) return true;
      if (hasMatchingDescendant(c.id)) return true;
    }
    return false;
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [childMap, filterAssignee, filterLevel]);

  // If filters active and neither this node nor descendants match, hide
  if ((filterAssignee || filterLevel) && !matchesFilter(node) && !hasMatchingDescendant(node.id)) {
    return null;
  }

  const filteredChildren = children.filter(c =>
    matchesFilter(c) || hasMatchingDescendant(c.id) || (!filterAssignee && !filterLevel)
  );

  // Progress bar for branches
  const counts = !isLeaf ? countStatuses(node.id, childMap) : null;
  const total = counts ? counts.done + counts.active + counts.upcoming + counts.blocked : 0;
  const donePct = counts && total > 0 ? (counts.done / total) * 100 : 0;
  const activePct = counts && total > 0 ? (counts.active / total) * 100 : 0;

  const st = STATUS_ICON[node.status];
  const ac = ASSIGNEE_COLORS[node.assignee];
  const lc = LEVEL_COLORS[String(node.level)] || LEVEL_COLORS.all;

  // Dim if filter active and this specific node doesn't match (but a descendant does)
  const dimmed = (filterAssignee || filterLevel) && !matchesFilter(node);

  return (
    <div className={depth === 0 ? "" : "ml-4 border-l border-zinc-800"}>
      {/* Node row */}
      <div
        className={`group flex items-center gap-1.5 py-1 px-2 rounded cursor-pointer transition-all
          ${isSelected ? "bg-zinc-800 ring-1 ring-zinc-600" : "hover:bg-zinc-800/60"}
          ${dimmed ? "opacity-40" : ""}`}
        onClick={() => setSelectedId(isSelected ? null : node.id)}
      >
        {/* Collapse toggle */}
        {!isLeaf ? (
          <button
            onClick={e => { e.stopPropagation(); toggleCollapse(node.id); }}
            className="w-4 h-4 flex items-center justify-center text-[9px] text-zinc-500 hover:text-zinc-300 shrink-0"
          >
            {isCollapsed ? "\u25B6" : "\u25BC"}
          </button>
        ) : (
          <span className="w-4 shrink-0" />
        )}

        {/* Status indicator */}
        <span className="text-[10px] shrink-0" style={{ color: st.color }}>{st.symbol}</span>

        {/* WBS code */}
        <span className="text-[9px] text-zinc-600 font-mono shrink-0 w-8">{node.wbs}</span>

        {/* Label */}
        <span className={`text-[11px] truncate ${depth === 0 ? "font-bold text-zinc-100" : depth === 1 ? "font-semibold text-zinc-200" : "text-zinc-300"}`}>
          {node.label}
        </span>

        {/* Spacer */}
        <span className="flex-1" />

        {/* Level badge */}
        <span
          className="text-[8px] px-1.5 py-0.5 rounded-full font-medium shrink-0"
          style={{ backgroundColor: lc + "20", color: lc, border: `1px solid ${lc}40` }}
        >
          {LEVEL_LABELS[String(node.level)]}
        </span>

        {/* Assignee badge */}
        {ac && (
          <span
            className="text-[8px] px-1.5 py-0.5 rounded font-medium shrink-0"
            style={{ backgroundColor: ac.bg + "25", color: ac.bg, border: `1px solid ${ac.bg}40` }}
          >
            {ac.label.split(" ")[0]}
          </span>
        )}

        {/* Branch progress mini-bar */}
        {counts && total > 0 && (
          <div className="w-12 h-1.5 bg-zinc-800 rounded-full overflow-hidden shrink-0" title={`${counts.done}/${total} done`}>
            <div className="h-full flex">
              <div className="bg-emerald-500 h-full" style={{ width: `${donePct}%` }} />
              <div className="bg-amber-500 h-full" style={{ width: `${activePct}%` }} />
            </div>
          </div>
        )}
      </div>

      {/* Detail panel (when selected) */}
      {isSelected && (
        <div className="ml-8 mr-2 mb-1 p-2 bg-zinc-800/80 rounded border border-zinc-700/50 text-[10px]">
          {node.description && <p className="text-zinc-300 mb-1">{node.description}</p>}
          <div className="flex items-center gap-3 text-zinc-500">
            <span>Status: <span style={{ color: st.color }}>{node.status}</span></span>
            <span>Assignee: <span style={{ color: ac?.bg }}>{ac?.label}</span></span>
            <span>Level: <span style={{ color: lc }}>{LEVEL_LABELS[String(node.level)]}</span></span>
            {counts && total > 0 && (
              <span className="text-zinc-400">
                {counts.done}/{total} subtasks done
                {counts.active > 0 && ` \u00B7 ${counts.active} active`}
                {counts.blocked > 0 && ` \u00B7 ${counts.blocked} blocked`}
              </span>
            )}
          </div>
        </div>
      )}

      {/* Children */}
      {!isLeaf && !isCollapsed && (
        <div>
          {filteredChildren.map(child => (
            <TreeNode
              key={child.id}
              node={child}
              childMap={childMap}
              depth={depth + 1}
              collapsed={collapsed}
              toggleCollapse={toggleCollapse}
              filterAssignee={filterAssignee}
              filterLevel={filterLevel}
              selectedId={selectedId}
              setSelectedId={setSelectedId}
            />
          ))}
        </div>
      )}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════
// Main Tab
// ═══════════════════════════════════════════════════════════

export default function MissionWBSTab() {
  const [collapsed, setCollapsed] = useState<Set<string>>(new Set());
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [filterAssignee, setFilterAssignee] = useState<FilterAssignee>(null);
  const [filterLevel, setFilterLevel] = useState<FilterLevel>(null);

  const childMap = useMemo(() => buildChildrenMap(WBS_TREE), []);
  const root = WBS_TREE.find(n => n.parentId === null)!;

  const toggleCollapse = useCallback((id: string) => {
    setCollapsed(prev => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  }, []);

  // Global stats
  const stats = useMemo(() => {
    const leaves = WBS_TREE.filter(n => !(childMap.get(n.id)?.length));
    const done = leaves.filter(l => l.status === "done").length;
    const active = leaves.filter(l => l.status === "active").length;
    const upcoming = leaves.filter(l => l.status === "upcoming").length;
    const blocked = leaves.filter(l => l.status === "blocked").length;
    return { total: leaves.length, done, active, upcoming, blocked };
  }, [childMap]);

  const expandAll = () => setCollapsed(new Set());
  const collapseAll = () => {
    const branches = WBS_TREE.filter(n => (childMap.get(n.id)?.length || 0) > 0).map(n => n.id);
    setCollapsed(new Set(branches));
  };

  const overallPct = stats.total > 0 ? Math.round((stats.done / stats.total) * 100) : 0;

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      {/* Top bar: stats + filters */}
      <div className="shrink-0 px-4 py-3 border-b border-zinc-800 bg-zinc-900/60 space-y-2">
        {/* Progress headline */}
        <div className="flex items-center gap-4">
          <h2 className="text-[14px] font-bold text-zinc-100">Mission Task Tree</h2>
          <span className="text-[10px] text-zinc-500">
            {stats.total} tasks \u00B7 {stats.done} done \u00B7 {stats.active} active \u00B7 {stats.upcoming} upcoming
            {stats.blocked > 0 && ` \u00B7 ${stats.blocked} blocked`}
          </span>
          <span className="text-[12px] font-bold" style={{ color: overallPct > 60 ? "#22c55e" : overallPct > 30 ? "#f59e0b" : "#6b7280" }}>
            {overallPct}%
          </span>
        </div>

        {/* Overall progress bar */}
        <div className="w-full h-2 bg-zinc-800 rounded-full overflow-hidden">
          <div className="h-full flex transition-all duration-500">
            <div className="bg-emerald-500 h-full transition-all" style={{ width: `${(stats.done / stats.total) * 100}%` }} />
            <div className="bg-amber-500 h-full transition-all" style={{ width: `${(stats.active / stats.total) * 100}%` }} />
            <div className="bg-red-500 h-full transition-all" style={{ width: `${(stats.blocked / stats.total) * 100}%` }} />
          </div>
        </div>

        {/* Filters row */}
        <div className="flex items-center gap-3 flex-wrap">
          {/* Assignee filter */}
          <span className="text-[9px] text-zinc-500 uppercase tracking-wide">Person:</span>
          {Object.entries(ASSIGNEE_COLORS).map(([id, c]) => (
            <button
              key={id}
              onClick={() => setFilterAssignee(filterAssignee === id ? null : id)}
              className={`text-[9px] px-2 py-0.5 rounded transition-all border ${
                filterAssignee === id
                  ? "font-bold"
                  : "opacity-60 hover:opacity-100"
              }`}
              style={{
                backgroundColor: filterAssignee === id ? c.bg + "30" : "transparent",
                borderColor: c.bg + (filterAssignee === id ? "80" : "40"),
                color: c.bg,
              }}
            >
              {c.label}
            </button>
          ))}

          <span className="text-zinc-700">|</span>

          {/* Level filter */}
          <span className="text-[9px] text-zinc-500 uppercase tracking-wide">Level:</span>
          {Object.entries(LEVEL_COLORS).map(([lv, color]) => (
            <button
              key={lv}
              onClick={() => setFilterLevel(filterLevel === lv ? null : lv)}
              className={`text-[9px] px-2 py-0.5 rounded transition-all border ${
                filterLevel === lv
                  ? "font-bold"
                  : "opacity-60 hover:opacity-100"
              }`}
              style={{
                backgroundColor: filterLevel === lv ? color + "30" : "transparent",
                borderColor: color + (filterLevel === lv ? "80" : "40"),
                color,
              }}
            >
              {LEVEL_LABELS[lv]}
            </button>
          ))}

          <span className="text-zinc-700">|</span>

          {/* Expand/collapse */}
          <button onClick={expandAll} className="text-[9px] px-2 py-0.5 rounded border border-zinc-700/50 text-zinc-500 hover:text-zinc-300 transition-all">
            Expand All
          </button>
          <button onClick={collapseAll} className="text-[9px] px-2 py-0.5 rounded border border-zinc-700/50 text-zinc-500 hover:text-zinc-300 transition-all">
            Collapse All
          </button>

          {(filterAssignee || filterLevel) && (
            <button
              onClick={() => { setFilterAssignee(null); setFilterLevel(null); }}
              className="text-[9px] px-2 py-0.5 rounded border border-red-800/50 text-red-400 hover:text-red-300 transition-all"
            >
              Clear Filters
            </button>
          )}
        </div>
      </div>

      {/* Tree */}
      <div className="flex-1 overflow-y-auto p-4">
        <TreeNode
          node={root}
          childMap={childMap}
          depth={0}
          collapsed={collapsed}
          toggleCollapse={toggleCollapse}
          filterAssignee={filterAssignee}
          filterLevel={filterLevel}
          selectedId={selectedId}
          setSelectedId={setSelectedId}
        />

        {/* Legend */}
        <div className="mt-6 p-3 bg-zinc-900/60 rounded border border-zinc-800 flex items-center gap-6 flex-wrap">
          <span className="text-[9px] text-zinc-500 uppercase tracking-wide">Legend:</span>
          {(Object.entries(STATUS_ICON) as [WBSStatus, { symbol: string; color: string }][]).map(([status, { symbol, color }]) => (
            <span key={status} className="flex items-center gap-1 text-[10px]">
              <span style={{ color }}>{symbol}</span>
              <span className="text-zinc-400 capitalize">{status}</span>
            </span>
          ))}
          <span className="text-zinc-700">|</span>
          <span className="flex items-center gap-1 text-[10px]">
            <span className="w-3 h-1.5 bg-emerald-500 rounded-full inline-block" /> <span className="text-zinc-400">Done</span>
          </span>
          <span className="flex items-center gap-1 text-[10px]">
            <span className="w-3 h-1.5 bg-amber-500 rounded-full inline-block" /> <span className="text-zinc-400">Active</span>
          </span>
          <span className="flex items-center gap-1 text-[10px]">
            <span className="w-3 h-1.5 bg-zinc-600 rounded-full inline-block" /> <span className="text-zinc-400">Upcoming</span>
          </span>
        </div>
      </div>
    </div>
  );
}
