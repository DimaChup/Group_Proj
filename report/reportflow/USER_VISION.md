# User's Vision for Reportflow — What It MUST Convey

## The Structure (in this order)

1. **THE GOAL**: Find the casualty as fast as possible

2. **THE CONSTRAINTS**: Hardware (Pi 5, 4.8 FPS, single battery), regulatory (flight area, SSSI NFZ, 50m max), operational (one search pass)

3. **THESE CONSTRAINTS GIVE US 5 THINGS TO OPTIMIZE FOR**:
   - Coverage, Detection, Time, Energy, Safety
   - State clearly: "these constraints break the problem into 5 competing dimensions"

4. **ALL THE VARIABLES WE CONTROL** + **HOW THEY INTERCONNECT**:
   - Altitude, speed, scan angle, overlap, NFZ margin, heading mode
   - Show the coupling/dependency (sensitivity matrix, network diagram)
   - Make clear: altitude affects ALL 5 dimensions, speed affects 3, etc.

5. **OUR OPTIMIZATION APPROACH — start with what's obvious/measurable**:

   a) **Max altitude for detection** — we can measure this ourselves at different light conditions. We found the ceiling. Drop by 15% (NOT 30%) for safety margin. This gives us operating altitude.

   b) **Max speed at that altitude** — limited by blur, inference FPS (4.8), effective FPS, frames needed on target. We measured this. Drop by 15% margin. This gives us operating speed.

   c) **Speed also varies with lighting** — brighter = faster allowed. We have a table for this.

   d) **Once altitude and speed are settled** — decide on search pattern. Needs to be energy efficient, safe (NFZ margins), give good coverage. Several parameters to consider: scan angle, overlap, turning vs not turning, pattern type.

   e) **We quantify search pattern quality** by doing energy efficiency simulation with physics (momentum theory hover, quadratic drag). We score patterns on how well they achieve safety, detection coverage, energy efficiency. 216-config sweep.

   f) **NFZ margins** — camera footprint + GPS error + reaction time = buffer distance

6. **THE RESULT**: Selected configuration with rationale

## Key Requirements
- Safety margin is **15%** everywhere (NOT 30%)
- The logic chain must feel INEVITABLE — each step MUST follow from the previous
- Show that we start with things we can MEASURE (detection altitude, speed limits) then move to things we OPTIMIZE (path, margins)
- Energy efficiency figures should be included to show we properly quantified paths
- Pattern alternatives mentioned (lawnmower, spiral, etc.)
- Drone turning vs not turning tradeoff
- Speed adaptation to lighting
