# User Requirements Check — reportflow/main.tex

Reviewed against the 10 specific instructions.

## Results

| # | Requirement | Status | Location | Notes |
|---|-------------|--------|----------|-------|
| 1 | Safety margin is 15% NOT 30% | PASS | L187: "15\% margin below detection ceiling", L268: "Chosen speed (15\% margin)" | The only "30%" in the file (L113) refers to swath overlap range (10--30%), not safety margin. No fixes needed. |
| 2 | Mission is to find casualty the fastest given constraints | PASS (after user edit) | L84: "The mission is to locate a lost casualty as quickly as possible. Given our hardware constraints..." | User rewrote L84 during session. Clear and explicit. |
| 3 | 5 dimensions clearly stated | PASS | L86-92: Coverage, Detection, Time, Energy, Safety as bullet list | Five items, bolded, with explanations. |
| 4 | Strategy follows FROM the 5 dimensions | PASS (fixed) | L96: "These five dimensions define the strategy. Because they conflict, we must decide what to prioritise..." | Added explicit link: dimensions -> conflict -> priority stack -> design choices. |
| 5 | Energy/path figures included | PASS | L141: energy heatmap (Fig 4), L167: top3 paths (Fig 5), L135: altitude-speed tradeoff (Fig 3) | Three figures quantify energy across configurations. |
| 6 | Clear flow: mission -> constraints -> optimisation targets -> priority -> strategy | PASS (fixed) | L239: "mission (find casualty fastest) -> constraints (battery, camera, NFZ) -> what we optimise (five dimensions) -> what we prioritise (safety > detection > speed > energy) -> strategy (sequential parameter lock-in)" | Explicit decision-tree chain added to Section 7 intro. |
| 7 | Speed varies with light conditions | PASS | L268-277: speed envelope table (bright=10, overcast=8.5, dusk=6 m/s), L279: "search speed adapts to ambient lighting", L291: speed adaptation bullet in qualitative choices | Both quantitative (table) and qualitative (design choice) coverage. |
| 8 | Turning vs not turning the drone — not turning is more energy efficient | PASS (fixed) | L290: "compared configurations where the drone yaws to face the direction of travel on each leg versus maintaining a fixed heading... The fixed-heading (no-yaw) approach proved more energy-efficient: eliminating yaw rotations at each U-turn saves both the energy cost of the rotation itself and the time spent decelerating, turning, and re-accelerating." | Added to lawnmower bullet. Removed duplicate standalone bullet that was redundant. |
| 9 | Clear decision-tree flow of reasoning | PASS (fixed) | L237: Section renamed "Sequential Decision Chain", L239: explicit chain notation with arrows showing mission -> constraints -> optimise -> prioritise -> strategy | Reframed from "measurement chain" to "decision tree" with node-by-node logic. |
| 10 | Safety margin 15% not 30% everywhere | PASS | Searched all instances: L187 (15%), L268 (15%), L239 (15%). Only "30%" is L113 (swath overlap range) and L191 (NFZ buffer distance in metres, not a percentage margin). | No 30% safety margin exists anywhere. |

## Fixes Applied

1. **Section 7 renamed** from "Sequential Measurement Chain" to "Sequential Decision Chain"
2. **Section 7 intro rewritten** with explicit decision-tree flow: mission -> constraints -> what we optimise -> what we prioritise -> strategy
3. **Yaw/turning comparison added** to lawnmower bullet in Section 8 (non-quantifiable choices)
4. **Duplicate "Fixed heading" bullet removed** (was redundant with lawnmower bullet)
5. **Item count corrected** from "Three choices" to "Four choices" in Section 8 intro

## Items Already Fixed by User (during session)

- L84: Mission statement rewritten to be explicit about finding casualty fastest given constraints
- L96: "These five dimensions define the strategy" sentence added
- L279: Speed adaptation paragraph added to Step 3
- L291: Speed adaptation bullet added to qualitative choices

## Compilation

- pdflatex: SUCCESS, 9 pages, no errors (only cosmetic underfull hbox warnings in tables)
