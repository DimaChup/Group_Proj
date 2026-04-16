# D7 Context Extracted from Reports, Docs, and Raw Material

Comprehensive summary of team dynamics, personal reflections, named incidents, conflicts,
collaboration moments, and things that went wrong. Sourced from D7_RAW_MATERIAL.md,
old D7 LaTeX sections, COMPLAINT_LETTER.md, LESSONS_LEARNED.md, and GROUP_STATUS.md.

---

## NAMED TEAMMATES AND WHAT THEY DID

### Robin — Flight Dynamics / State Machine Owner
- Owned the flight/state-machine script; Apollo built passive_watch integration specifically for him.
- Commits `a5b1ab7`, `885cee4`, `36b6069`: Apollo created a `--robin` flag in passive_watch_2.py so Robin's state machine could poll vision results over HTTP without touching CV code.
- Apollo wrote a README specifically for Robin: exact CLI command, JSON schema, parsing examples (commit `885cee4`).
- `docs/DESIGN_DECISIONS.md:107-109`: explicit responsibility split documented: "Robin's script handles flight only (no camera). Our `pi_flight.py` handles camera + vision + stream. Both run in parallel, no conflict."
- Commit `24783d9`: publicly documented division of labour in the checklist.
- Auto-clear flag for passive_watch SMART cycle (commits `2bbad/cec899e/56055e0`) built specifically because Robin's mission script needs a clean re-lock after first target.

### Demetro — FDR Presentation Slides
- Gave the FDR presentation to the class/assessors.
- Apollo built Demetro's presentation materials (commit `32fb0c5`: 2 full-screen slides for Demetro).
- Apollo went further and wrote Demetro's speaking scripts: 246 + 219 = 465 words, 3.1 min (commits `b2a9cd4`, `ba667f2`).
- Teleprompter sidebar added, iterated 4-5 times on polishing the scripts for Demetro's delivery (commits `9b826f8, 7920e5a, 794ef5c`).
- Evidence of team-first behaviour: Apollo wrote AND polished his TEAMMATE's slides AND speaking scripts.

### Edward — Computer Vision / Optics
- Edward is described as the most productive sub-team pairing with Apollo.
- His optics knowledge complemented Apollo's software skills: he calibrated camera FOV and evaluated lens distortion while Apollo built the detection pipeline.
- Edward observed that Apollo "built things faster than anyone could review them" — meant as a compliment but accurately describing the collaboration failure.
- Edward noted that Apollo's iteration pace made it hard to track which module version was current; Apollo responded with explicit version tags and a living ground-truth document.

### Zian — Unknown Role
- Mentioned in working directory (`Zian/` folder in git status). Role unclear from code history.

### Steve — Course Organiser (NOT a teammate)
- Subject of the formal clarification/complaint letter drafted by Apollo on behalf of the team.
- Provided verbal assurances about drone fixes that were not followed through.
- Chat history preserved in COMPLAINT_LETTER.md appendix.
- Steve mentioned a "draft update" for D7 personal reflection details that may not have been issued.

### Sid — Technical Assistant (NOT a teammate)
- Provided the single DJI training video Apollo used for FOV calibration and model retraining.
- The video arrived late in the term.

### The Pilot (unnamed in docs)
- Practised RC and understood abort procedures without engaging with code.
- Identified that abort and confirm-target buttons in the ground station were dangerously close — a genuine safety risk Apollo had missed. Apollo immediately separated the controls and added a confirmation step.
- On the cancelled flight day, the pilot navigated the ground station independently — confirming targets and reading telemetry without verbal guidance.

### The Project Manager (unnamed in docs)
- Booked field slots and submitted risk assessments.
- Told Apollo his documentation was too dense; Apollo restructured key guides around numbered steps and created a one-page colleague checklist.
- Raised that she felt unable to contribute meaningfully beyond logistics. Apollo offered reassurance that her coordination was essential — but in retrospect this was "conflict avoidance disguised as appreciation."
- Apollo learned (too late) to replace code-level updates with outcome-focused summaries for her.

### The Hardware Lead (unnamed in docs)
- Assembled the drone independently, consulting Apollo only for Pi-to-Cube wiring.

---

## CONFLICTS AND RESOLUTIONS

### Conflict 1: ROS 2 vs Raw MAVLink
- First technical disagreement in the team.
- Apollo resolved it by building a 20-line working heartbeat demo.
- In Tuckman's model, this was a brief storming phase because the team deferred to demonstrated results.
- **Self-critique**: "This was persuasion by fait accompli, not negotiation — I had already decided the answer and used a demo to close debate rather than opening a genuine discussion."

### Conflict 2: Workload Imbalance / PM Feeling Sidelined
- The project manager raised that she felt unable to contribute meaningfully beyond logistics.
- Apollo offered reassurance that her coordination was essential.
- **Self-critique**: "This was conflict avoidance disguised as appreciation — I protected my autonomy by reframing the problem as solved rather than engaging with it."
- Broader pattern: teammates expressed frustration at feeling sidelined. Apollo bears "primary responsibility" for this.
- Root cause: Apollo had the strongest programming background and found it faster to build than onboard.
- "The lesson: contribution points must be designed in from the start, not retrofitted."

### Conflict 3: State Machine Complexity
- Apollo designed a state machine with 11 states and multiple sub-modes.
- Team pushed back, arguing it was too complex for anyone else to debug under pressure.
- After sitting with their feedback overnight, Apollo recognised they were right about the maintainability risk.
- Simplified the state transitions, removed two experimental sub-modes, wrote explicit transition diagrams.
- Cost: a week of refactoring. Benefit: a system the whole team could reason about on flight day.
- **Self-critique**: "It was the first time I genuinely changed a technical direction because of team input rather than technical evidence. Yet this was once in twenty weeks — a ratio that reveals collaborative decision-making is still my exception, not my norm."

### Conflict 4: Hardware Failures / Complaint Letter to Steve
- Three flight days scheduled. Zero successful flights across all three.
- ~8 weeks with zero seconds of real flight data.
- Drone was not assembled for the first several weeks; a servo was missing. Other two teams had complete platforms.
- Flight Day 1 (~12 March): arrived with tested software, progressive test plan, printed checklist. Hardware not functional.
- Flight Day 2 (~19 March): arrived again, prepared again. Hardware failed again.
- Flight Day 3 (30 April, Easter holiday): travelled back to Bristol. Hardware still not functional. Told to build it themselves or share another team's drone.
- Apollo drafted a measured, factual complaint letter on behalf of the whole team.
- Tone: "We are not assigning personal blame. We are documenting what happened."
- 6 iterations on the Steve communication strategy, tone, phrasing (commits `26e3255, f3401e4, d946838, 5af87d0, 847518e, 4b0fd91`).
- Apollo chose to lead the team's external communication.
- Turned grievance into a constructive clarification request (commit `4b0fd91`).
- Cross-team awareness: noted that borrowing the green team's drone "does not constitute a plan" because it risks "disruption to a team whose hardware actually works."

---

## APOLLO'S SELF-CRITIQUE (from old D7 LaTeX sections)

### Speed Over Inclusion (Primary Weakness)
- "The same instinct that produced a working state machine in two days also meant I built it alone and presented teammates with a finished system rather than an opportunity to contribute."
- "I optimised for output over team development."
- "I suspect this stems from Ukraine's engineering culture, where individual competence is prized above collaborative process."
- "Learning to value slower, inclusive approaches as equally 'productive' is an ongoing adjustment."
- Invested ~25-30 hours/week (weeks 12-20) vs ~8-12 hours from most teammates — partly by necessity, partly by choice.

### Communication Gaps
- Communicates well through demonstrations and visual tools but weaker at spontaneous verbal explanation.
- This compounds the inclusion problem: "teammates who needed verbal context received visual answers instead."
- Documentation alone didn't work: "despite 16 guide files, teammates engaged only when I demonstrated in person."
- "For non-technical audiences, documentation is reference material, not a teaching tool; the teaching must happen live."

### Helping vs Developing Teammates
- "I lowered barriers to contribution (numbered scripts, documentation, browser-based tools) but did not invest in developing teammates' technical skills."
- "Creating a checklist is accessibility; sitting with someone while they write their first MAVLink command is development."
- "Edward grew because we paired on complementary tasks; the others did not because I handed them finished systems instead of learning opportunities."
- "This is the difference between making a system usable and making a team capable — and I failed at the latter."

### Delayed Hardware Testing
- Treated simulation as sufficient validation for too long.
- Underestimated Pi integration by at least three weeks, assuming "same code runs everywhere."
- Platform-specific bugs (Python 3.13, camera colour, serial baud rates) are invisible in simulation by definition.
- Correction: adopted "day-one deployment" rule, created Docker-based Pi environment test.

### Team Structure Assessment
- "The team delivered a working system, but the five-person structure was suboptimal for a software-heavy project."
- "Three roles had low sustained workload, while software demanded 25-30 hours per week from me alone."
- "A more effective allocation would have paired two people on software from day one with explicit interface contracts and code review cycles, treating skill transfer as a project deliverable rather than an afterthought."

---

## COLLABORATION WINS

### Simulator as Communication Device
- The simulator proved the most effective communication tool: "teammates understood the system intuitively when they saw the drone flying, detecting, and descending on screen — more effective than any slide deck or written specification."

### Ground Station for Pilot
- The ground station translated complex state into large buttons usable outdoors.
- Apollo adapted communication entirely for the pilot: replacing technical explanations with hands-on bench walkthroughs.
- On cancelled flight day, pilot navigated ground station independently — confirming targets and reading telemetry without verbal guidance.

### Edward Pairing on CV
- The most productive sub-team pairing. Complementary expertise: Edward's optics + Apollo's software. Produced faster results than either working alone.

### Receiving and Acting on Feedback
- Pilot: identified dangerously close abort/confirm buttons → Apollo immediately separated controls and added confirmation step.
- PM: documentation too dense → Apollo restructured around numbered steps and created colleague checklist.
- Edward: iteration pace too fast to track → Apollo added version tags and living ground-truth document.

### Building for Robin's Integration
- Rather than forcing Robin to learn the CV codebase, Apollo created an HTTP polling interface, wrote Robin-specific documentation, and packaged a self-contained deliverable. Evidence of designing interfaces around teammate capabilities.

### Resilience on Cancelled Flight Days
- Flight Day 1 cancelled by weather: instead of going home, Apollo did bench testing, FOV calibration, lens calibration, built field reference doc, ran comprehensive benchmarks. 10+ commits in one cancelled day.
- Flight Day 3 (Pi field day): diagnosed corrupt calibration file on-site, made undistortion optional, fixed GPS normalisation bugs in the field.

### Team Advocacy
- Apollo drafted and iterated a formal complaint letter on behalf of the entire team — not just venting but constructive, evidence-backed, with specific asks and suggestions for future cohorts.

---

## THINGS THAT WENT WRONG

### Zero Real Flight Data
- Three flight days, zero successful flights, ~8 weeks without a flyable drone.
- Hardware was provided broken; other two teams had working platforms.
- "The simulation framework we created ourselves is the only reason this project produced any verifiable engineering output at all."

### Python 3.13 Compatibility Crisis
- tflite-runtime completely broken on Python 3.13.
- pyserial serial reads broken — bytes dropped, MAVLink framing errors.
- Consumed two full days Apollo could not afford.
- Fix: ai-edge-litert (replacement package) + mavproxy UDP bridge.

### IMX296 Camera BGR/RGB Confusion
- Spent hours trying AWB modes, manual gains, ISP tuning before discovering the root cause.
- The sensor outputs BGR despite picamera2 labelling it RGB888.
- Fixed by systematically testing all 6 channel permutations on a PuTTY terminal with no internet.

### TFLite Bounding Box Coordinate Bug
- Green detection boxes drawn off-screen — pixel coords (0-640) treated as normalised (0-1).
- Multiplied by frame dimensions, producing positions like (466560, 261120).

### Double-Scaling GPS Estimation Bug
- detect_in_image returned pixel coords but passive_watch multiplied by w,h again → overlay 100m+ off.

### Calibration Data Corruption on Pi
- calibration_data.npz was empty (0 bytes) → cv2.remap() used garbage matrices → detection stopped.
- NumPy didn't crash on empty .npz — returned empty arrays silently.

### Geofence Sign Convention Errors
- Early code pushed drone TOWARD NFZ instead of away.
- cv2.pointPolygonTest positive = INSIDE (counter-intuitive).
- Repulsive offsets needed negation.

### Geofence RTL Crash
- RTL mode (6) wasn't in allowed-modes tuple → RC override guard skipped cv2.waitKey(1) → window froze.
- 5 parallel agents used to diagnose.

### GPS Timing Lag
- GPS has 100-200ms latency → 1m error at 5m/s, diagonal spread in estimates.
- CEP50=2.3m, max=16.5m from DJI video analysis.

### DISARM_DELAY Auto-Disarm
- ArduCopter's default 10s DISARM_DELAY caused auto-disarm during autonomous startup sequence.

### Mode-Fighting Near-Crash (Another Team's Lesson)
- A colleague's drone crashed because software kept switching to GUIDED while RC was in LOITER.
- ArduCopter oscillated between modes, lost control authority, drone fell.
- Apollo implemented RC Override Guard in main.py to prevent this.

---

## KEY TECHNICAL ARTIFACTS APOLLO BUILT (for report evidence)

- `passive_watch.py` (752 lines): standalone observer with MJPEG stream + SMART clustering + GPS estimation + map panel.
- `simple_simulator.py` (2508 lines): interactive MVP covering the whole mission with keyboard flight.
- `tests/unit/`: 127 test functions written voluntarily.
- `cv_models/sar_v2_1088/best.tflite`: retrained model (mAP50=0.995, 300 syn + 16 real + 50 neg at 1456x1088).
- `dataset_v3` multi-class (5-class): 3500 images generated for second training run.
- `FIELD_QUICK_REF.md`: no-internet field reference written on first cancelled flight day.
- `docs/MAIN_FEATURES.md`: 19 verified safety features documented.
- Headless support: terminal input thread + `/cmd?key=` HTTP endpoint + browser buttons.
- 820+ commits across branches; ~70+ commits on reports alone in last two weeks.
- D6 Goldmine: 74 → 85.2 across 6 scoring cycles.
- D6 Reportflow: 81.0 → 87.2.
- D7 reflection: 68 → 83-84 across 7 iterations.
- main.py refactor: 1411 → 754 lines, 6 modules extracted, 146 pytest tests.
- GPS estimation pipeline: IVW weighting, Kalman filter, SMART clustering, tilt compensation (12+ commits).

---

## DEVELOPMENT ACTIONS (from old D7 self-assessment)

1. **Collaborative architecture from day one**: Define contribution points and interface contracts BEFORE implementation. Applied mid-project with vision.py's single-function interface and numbered test scripts — but these must exist from week 1.

2. **Day-one hardware deployment**: Run a trivial script on target hardware within the first week. Implemented after Python 3.13 incident: Docker Pi test + preflight connectivity checker.

3. **Structured communication cadence**: "One sentence, one diagram, one demo" framework. Schedule regular check-ins. Measured by whether a teammate can independently modify a module within one sprint.

---

## CAREER CONTEXT

- Ukrainian robotics student at University of Bristol.
- Skills developed (MAVLink, edge AI, safety-critical design) transfer directly to autonomous systems Ukraine needs for mine clearance, reconnaissance, disaster response.
- Project lesson: "The quality of an autonomous system is determined not by its algorithms' cleverness, but by the rigour of its testing and the honesty of its failure analysis."
