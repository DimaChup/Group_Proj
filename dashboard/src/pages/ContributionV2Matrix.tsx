/**
 * ContributionMatrix — Tasks x People x Goals
 *
 * Grid showing team members as rows, goal aspects as columns,
 * with tasks categorized by which part of the Holy Grail they serve.
 */
import { useMemo } from "react";
import {
  TEAM, GOAL_ASPECTS, categorizeTask,
  type Approach, type GoalAspect, type TeamMember,
} from "./group-project-v2-data";
import { Badge } from "./GroupProjectV2Components";

interface ContributionMatrixProps {
  approach: Approach;
}

export default function ContributionMatrix({ approach }: ContributionMatrixProps) {
  // Categorize all tasks by member and goal
  const matrix = useMemo(() => {
    const result: Record<string, Record<GoalAspect, string[]>> = {};
    for (const member of TEAM) {
      result[member.id] = { locate: [], navigate: [], deliver: [], return: [], infrastructure: [] };
      const tasks = approach.teamTasks[member.id] || [];
      for (const task of tasks) {
        const goal = categorizeTask(task);
        result[member.id][goal].push(task);
      }
    }
    return result;
  }, [approach]);

  // Count totals per goal
  const goalTotals = useMemo(() => {
    const totals: Record<GoalAspect, number> = { locate: 0, navigate: 0, deliver: 0, return: 0, infrastructure: 0 };
    for (const memberId in matrix) {
      for (const goal of Object.keys(totals) as GoalAspect[]) {
        totals[goal] += matrix[memberId][goal].length;
      }
    }
    return totals;
  }, [matrix]);

  const goalKeys = Object.keys(GOAL_ASPECTS) as GoalAspect[];

  return (
    <div className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-4 mb-4">
      <h3 className="text-[13px] font-bold text-zinc-100 mb-1">Contribution Matrix</h3>
      <p className="text-[10px] text-zinc-500 mb-3">
        How each team member's tasks map to the Holy Grail goals for {approach.name}.
      </p>

      <div className="overflow-x-auto">
        <table className="w-full text-[9px] border-collapse">
          <thead>
            <tr>
              <th className="text-left text-zinc-500 pb-2 pr-2 border-b border-zinc-800 w-[100px]">Member</th>
              {goalKeys.map(g => {
                const ga = GOAL_ASPECTS[g];
                return (
                  <th key={g} className="text-center pb-2 px-1 border-b border-zinc-800">
                    <div className="flex flex-col items-center gap-0.5">
                      <span className="text-[10px]">{ga.icon}</span>
                      <span style={{ color: ga.color }} className="text-[8px] font-bold">{ga.label}</span>
                      <span className="text-zinc-600 text-[7px]">{goalTotals[g]} tasks</span>
                    </div>
                  </th>
                );
              })}
              <th className="text-center pb-2 px-1 border-b border-zinc-800 text-zinc-500 text-[8px]">Total</th>
            </tr>
          </thead>
          <tbody>
            {TEAM.map(member => {
              const memberTasks = matrix[member.id];
              const memberTotal = goalKeys.reduce((sum, g) => sum + memberTasks[g].length, 0);

              return (
                <tr key={member.id} className="border-b border-zinc-800/30 hover:bg-zinc-800/20">
                  <td className="py-2 pr-2">
                    <div className="flex items-center gap-1.5">
                      <span className="text-[10px]">{member.icon}</span>
                      <div>
                        <div className="text-[9px] font-semibold" style={{ color: member.color }}>{member.name}</div>
                        <div className="text-[7px] text-zinc-600">{member.role.split(",")[0]}</div>
                      </div>
                    </div>
                  </td>
                  {goalKeys.map(g => {
                    const tasks = memberTasks[g];
                    const ga = GOAL_ASPECTS[g];
                    return (
                      <td key={g} className="py-2 px-1 text-center align-top">
                        {tasks.length > 0 ? (
                          <div className="space-y-0.5">
                            {tasks.map((t, i) => (
                              <div key={i} className="text-[8px] text-zinc-400 leading-tight rounded px-1 py-0.5"
                                style={{ background: ga.color + "08", border: `1px solid ${ga.color}15` }}>
                                {t}
                              </div>
                            ))}
                          </div>
                        ) : (
                          <span className="text-zinc-800">{"\u2014"}</span>
                        )}
                      </td>
                    );
                  })}
                  <td className="py-2 px-1 text-center">
                    <span className="text-[10px] font-bold text-zinc-400">{memberTotal}</span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Summary bar */}
      <div className="flex gap-2 mt-3 pt-3 border-t border-zinc-800/50">
        {goalKeys.map(g => {
          const ga = GOAL_ASPECTS[g];
          const total = goalTotals[g];
          const allTasks = goalKeys.reduce((sum, gk) => sum + goalTotals[gk], 0);
          const pct = allTasks > 0 ? Math.round((total / allTasks) * 100) : 0;
          return (
            <div key={g} className="flex-1 text-center">
              <div className="h-1.5 rounded-full bg-zinc-800 overflow-hidden mb-1">
                <div className="h-full rounded-full" style={{ width: `${pct}%`, background: ga.color + "80" }} />
              </div>
              <span className="text-[7px]" style={{ color: ga.color }}>{pct}%</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
