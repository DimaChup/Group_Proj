# SAR Drone Mission - Presentation Script

## State Count Clarification

The code defines 19 enum values, but functionally there are **15 distinct states**.
- **INIT** just immediately transitions to TAKEOFF (no logic)
- **TARGET_DETECTED** just calculates a GPS estimate then immediately goes to CENTERING (one timestep)
- **EMERGENCY** is defined but never actually used as a state
- **LAND_AT_HOME** is the same descend logic as LAND, just at home

For the presentation, group them into **5 phases with 15 states**.

---

## Slide 1: Introduction

**What to say:**

"Our SAR drone operates as a semi-autonomous system — what we classify as Level 2 autonomy. The drone handles all navigation, searching, and target detection on its own. But at every critical decision point, a human pilot has to confirm before the drone proceeds. We designed a finite state machine with 15 states organised into 5 mission phases."

---

## Slide 2: The 5 Mission Phases (use the flowchart here)

**What to say:**

"Looking at the flowchart, the mission flows through 5 clear phases:"

1. **Launch & Transit** (2 states: TAKEOFF, TRANSIT TO SEARCH)
   - "The drone takes off and climbs to 30 metres cruise altitude, then follows pre-planned transit waypoints to reach the search area. This is fully autonomous."

2. **Search** (2 states: SEARCH broad, SEARCH FOCUSED)
   - "The drone follows a lawnmower pattern of pre-planned waypoints across the search area. After completing 40% of the waypoints, a PLB — Personal Locator Beacon — signal is received. This narrows down the likely area, so the drone switches to a focused search. It generates its own optimised lawnmower sweep waypoints inside the PLB focus area — no human input needed for that."

3. **Detection & Verification** (3 states: CENTERING, DESCEND, VERIFY TARGET)
   - "When the camera spots something in its field of view, the drone centres itself above the target and descends from 30m to 15m for a closer look. It then hovers and asks the pilot: is this the casualty? The pilot presses Y to confirm or N to reject. If rejected, the drone climbs back up and resumes searching."

4. **Landing & Delivery** (4 states: SELECT LANDING SIDE, APPROACH LANDING, LAND, DEPLOY PAYLOAD)
   - "Once confirmed, the pilot selects which side to land — North, South, East, or West of the casualty. The drone flies to a spot 7.5 metres away in that direction, lands, and waits for the pilot to press R to release the first aid kit. After release, the pilot presses H to send it home."

5. **Return Home** (3 states: ASCEND, RETURN TO HOME, LAND AT HOME → MISSION COMPLETE)
   - "The drone climbs back to cruise altitude, retraces the transit waypoints in reverse, and lands at the home base. Mission complete."

---

## Slide 3: Level of Autonomy

**What to say:**

"We designed this as Level 2 semi-autonomous. What that means in practice:"

**Autonomous (the drone decides):**
- All navigation — waypoint following, path planning
- Target detection using camera field of view
- Auto-generating focused search waypoints from the PLB signal
- Position refinement — GPS estimate improves as the drone descends
- No-Fly Zone avoidance — the drone auto-pauses if it gets within 7.5 metres of a restricted boundary

**Human-in-the-loop (the pilot decides):**
- "There are 5 key moments where the pilot must act:"
  1. Verify target — Y or N, is this really the casualty?
  2. Select landing side — N/S/E/W relative to the target
  3. Release payload — press R to drop the first aid kit
  4. Return home — press H to send the drone back
  5. Focused search retry — after 2 sweeps, search again or give up?

"The pilot can also press M at any time to pause the drone in manual mode, then A to resume or L to emergency land."

---

## Slide 4: Safety Features

**What to say:**

"We built in several safety layers:"

- **NFZ Buffer Zone** — if the drone approaches within 7.5 metres of a No-Fly Zone boundary, it automatically pauses and switches to manual mode. The pilot then decides whether to resume or land.
- **NFZ Violation Logging** — if the drone actually enters the NFZ, it's logged as a violation for post-mission review.
- **Emergency Landing** — the pilot can trigger an immediate landing at the current position from any state, no questions asked.
- **False Positive Handling** — if the pilot rejects a detection, the system suppresses re-detection of the same object until it leaves the camera's field of view. This prevents the drone from circling back and re-alerting on something already rejected.
- **Manual Override** — available from any state. The drone holds position until the pilot resumes or chooses to land.

---

## Slide 5: Search Strategy Detail (optional, if asked)

**What to say:**

"The search uses two modes:"

- **Broad search** — pre-planned lawnmower waypoints covering the full search area. If nothing found on the first pass, waypoints are reversed for a second sweep.
- **Focused search** — triggered by PLB signal at 40% progress. The system generates a random polygon focus area around the beacon location, then uses scan-line polygon clipping to create an optimal lawnmower sweep inside that irregular shape. After 2 sweeps of the focus area with no result, the pilot chooses to either re-search or return home.

---

## Key Numbers (if anyone asks)

| What | Value |
|------|-------|
| Total functional states | 15 |
| Pilot decision points | 5 |
| Cruise altitude | 30m |
| Verify altitude | 15m |
| Camera FOV at 30m | 36m x 36m |
| Transit speed | 8 m/s |
| Search speed | 3 m/s |
| Landing offset | 7.5m from casualty |
| NFZ buffer | 7.5m |
| PLB trigger | at 40% of broad search |
