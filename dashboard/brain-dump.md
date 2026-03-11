# Brain Dump — SAR Drone Dashboard

> Append-only. Every user message captured here (cleaned up, ideas preserved). Never delete entries.

---

## 2026-03-09

- Want a web page to organize and visualize everything related to the SAR drone project
- Should track progress, who's doing what, addons
- Connection diagram: motors should be above Cube box (separate from sensors, keep it distinct since we'll add more motor details later)
- Cube Orange+ clickable overlay page idea: when you click on Cube box, open a detailed overlay/page that explains what's inside — schematics, PID tuning, how it connects to everything, how stabilisation works, nice visuals and deep explanations of flight controller internals
- Confusion about mavproxy: is it on Cube or Pi? Where does Mission Planner actually connect? Needs clear understanding of TCP vs UDP. Want the diagram to make this obvious — mavproxy is software on Pi, not a separate device
- Started something similar before in the Orgnaiser project (Trade Study Lab, last 3 tabs: GP v2, Mission WBS)
- Copy those tabs into v3 project, keep it separate so it doesn't interfere with Python drone code
- Want good documentation so new LLM chat sessions don't have to figure everything out from scratch
- Comments and docs should be maximally useful
- Web app is for visualizing what's going on with the project
- Want to implement the same workflow system from Orgnaiser's BOOTSTRAP.md — thorough documentation, slash commands, rules, context management
- Keep track of where team is at, what level, what each person should be doing
- Tab with all notes/ideas laid out clearly
- Likes structure: left sidebar (Ctrl+L) + right sidebar (Ctrl+R) + top bar overlays
- Right sidebar = team-dedicated (comms, who's doing what, blockers)
- Left sidebar = documentation hub
- Will build up exactly what's wanted gradually — sidebars are the foundation
- Mission tab should be comprehensive with expandable details, pulling from actual AENGM0074 brief
- Use agents to extract all relevant stuff from the brief into the right places on the hub
- Extract equipment, links, documentation for hardware — especially Cube and Pi and how to connect
- Field map image (map_1.jpg) should go in Mission tab — shows Fenswood Farm operational area
- Levels tab: good having 3 levels, but needs short explanation on top (why levels, increasing complexity)
- Hardware tab: list all components, how they connect, setup guides, links — comprehensive reference
- Will add drone image to hardware tab later
- Git: pulling whole repo to Pi is fine since dashboard is in its own folder, tiny extra data
- Look at GP2 folder images — team WhatsApp chat with Robin's handwritten flight day plans
- Robin has state machine flow: IDLE → Setup Mission → PRE_AUTO_CHECK → Generate Pattern → SEARCH (Phase 1, Phase 2)
- Robin NOT integrating CV with state machine until AFTER flight day 1 — CV runs passively on Day 1
- Detection output: images with metadata in filename (object type, lat/lon/alt) — Robin's state machine monitors directory
- Flight day deliverables to demonstrate: setup mission, pre-flight checklist, start search (GUIDED/lawnmower), RC override, PLB plan
- For each test record T/F (working or not), identify faulty states and causes
- If autonomous fails in single mission → demonstrate over 2 missions as fallback
- State machine robustness = crucial
- Dima: CV models (dummy + cone), simulation, GPS estimation
- Robin: state machine, flight control, GUI integration
- Adding cone detection alongside dummy detection
- Incorporate team's flight plan into Roadmap timeline tab with owner tags
- For Flight Day 1: want 3 progressive columns (tiers) getting more ambitious but still realistic
- Need contingencies clearly shown — what if things go wrong at each step
- Need verification steps — what do we check works
- Pre-flight day preparation subsection — everything before we leave
- Decision gates between tiers — clear go/no-go criteria
- Think deeply about what we'll actually be doing on the day
- Leading up to the day: what needs to be done in preparation
- Establish live video link before flying — prove camera + AI + WiFi stream work end-to-end
- Ground-level vision test on actual dummy before flying (first time model sees real dummy!)
- Collect aerial images from drone for CV retraining — even if detection fails, raw frames are valuable
- Progressive autonomy mini-tests: manual → 1 waypoint → 3 waypoints → search pattern
- Comprehensive preflight diagnostics with troubleshooting trees (11 checks, each with fail steps)
- Measure: max detection altitude, max speed for detection, GPS accuracy — clear test lists
- Flight Day 1 tab should be same content as expanded Day 1 in timeline (DONE)
- Flight Day 1 tab: use 2-3 column layout, too much horizontal space wasted as single column (DONE)
- Flight Day 1 tab: more detailed context, add diagnostics table, files to collect section (DONE)
- Key philosophy: test things SEPARATELY first → combine gradually → then real mission
- Measure accuracy of altitude meter, GPS geolocation, drone stability — separately
- Video link: does it affect flight? Can pilot fly with just video? Adjust resolution for less lag?
- Stream is completely separate from flight control (camera on Pi, flight on Cube via mavproxy)
- Simple autonomous mission (3 waypoints), always test manual override can be taken
- CV: test at what speed and altitude detection works — systematic measurement
- Auto-geotagged pictures of dummy — evidence + retraining data
- GPS estimation accuracy: how reliably and accurately does it get position? At what altitude?
- Test everything separately on ground first, then simplest flight, then combine (DONE — restructured tiers)

## 2026-03-09 (part 2)

- CV box inside Pi on diagram — camera CSI arrow should point directly to CV part of Pi
- Show RAM/compute specs on each device to explain why CV runs on Pi not Cube
- Cube overlay: show CPU (STM32H757, 400MHz) and RAM (1MB) specs, visualize 400Hz control loop — reads sensors, fuses, PID computes, mixes motors, outputs PWM — 400 times per second, every 2.5ms
- Pi overlay: similar clickable deep-dive — specs, what software runs on it, CV pipeline, startup sequence
- Live video stream concern: will streaming video to GCS slow down the Pi? Worth enabling?
  - Answer: no — MJPEG in separate thread, ~0.5 Mbps at 320x240, WiFi handles 50+ Mbps easily
  - Can drop quality/resolution if WiFi is slow (240x180, quality 40, cap FPS to 2)
  - Key: even if WiFi drops, drone keeps detecting — stream is for monitoring, not decision-making
  - Most efficient: MJPEG (chosen) — pure Python, 100ms latency, any browser. H.264 saves bandwidth but adds 2-4s latency
- Tarot release: how does it work? Is it Cube giving the command?
  - Answer: Pi decides WHEN (state machine), sends DO_SET_SERVO via MAVLink → mavproxy → serial → Cube → AUX OUT PWM → servo opens → kit drops
  - Tarot is a double-throw servo — two PWM values (hold/release). Cube is the muscle, Pi is the brain
- Flight modes: how many are there? Do we need to add new ones?
  - ArduCopter has ~25+ built-in modes (STABILIZE, LOITER, GUIDED, AUTO, RTL, LAND, ALT_HOLD, POSHOLD, ACRO, SPORT, AUTOTUNE, BRAKE, SMART_RTL, DRIFT, CIRCLE, ZIGZAG, FOLLOW, THROW, FLOWHOLD, FLIP, etc.)
  - We do NOT create new modes — we use existing ones, primarily GUIDED
  - We switch between them via MAVLink SET_MODE command
- State machine vs flight modes: two separate layers
  - Flight modes (Cube firmware) = HOW the drone flies (stabilise? hold position? follow waypoints?)
  - State machine (our Python on Pi) = WHAT the drone does next (search → detect → centre → descend → verify → land)
  - Cube stays in GUIDED the entire mission; state machine sends waypoint commands
  - State machine is NOT a flight mode — it's higher-level mission logic running on companion computer
- Camera feed to two places concern: does streaming to both CV and GS browser cause problems?
  - Answer: no — it's 1 capture, 2 consumers. Camera captures one frame. CV processes it (draws green detection boxes). Same processed frame gets JPEG-encoded for MJPEG stream. Not two camera captures.
  - Expensive part: inference ~250ms. JPEG encode for stream: ~5ms. Negligible extra overhead.
  - Stream already overlays detection boxes + confidence scores — operator sees exactly what AI sees
  - Manual flight mode = STABILIZE (full manual, RC sticks = tilt angles, Cube only self-levels)
- Want to see two state machines side by side: passive flight vs active flight
  - Passive (pi_passive_flight.py): pilot flies RC, CV runs independently, logs detections, beeps buzzer. Zero flight commands. Vision and flight completely independent.
  - Active (pi_flight.py / main.py): CV detection triggers investigation. Drone auto-flies to estimate, descends to 15m. Human classifies: Y=confirm (land), I=interest (log, resume), X=false positive (discard, resume). AI proposes, human disposes.
  - Present clearly with detail, show the contrast between "CV is just watching" vs "CV drives decisions"
- Flight day 1 planning: want to try different elements separately, progressively
  - Ambitiously, main.py already works in SITL — could we run it on real drone?
  - What might stop it: no GPS lock wait, hardcoded coords, no pre-arm feedback, no state timeouts, no RC failsafe detection
  - All fixable with ~60 lines of guard code — same state machine, just adding real-world validation
  - SITL doesn't need these guards (instant GPS, instant arm, no RC) but real hardware does
  - Once fixed, SITL and REAL should behave identically
- Flight day checklist review: found issues
  - All script paths wrong (tests2/ doesn't exist, tests reorganized into tests/flight/, tests/hardware/, etc.)
  - Missing Step 1.5 (waypoint test — prove MAVLink commands work before trusting CV)
  - Missing stream verification, pi_flight.py bench check, battery voltage check
  - No time estimates (need ~2.5 hours, minimum 2 batteries)
  - FIRST_FLIGHT.md is redundant/contradicts checklist — should be deprecated
  - Model swap section lists non-existent backup models
  - Two state machine comparison updated: now shows 3 scripts (passive/interactive/autonomous) accurately based on actual code

## 2026-03-11 (part 2) — Pipeline, Levels, Rangefinder

- Pipeline tab: mission goal at top with all rules/constraints from brief, then design choices, then 13-stage pipeline
- Design choices: exhaustive list of every configurable parameter (camera, model, flight, GPS, safety, comms)
- Levels: don't replace existing content, ADD stepping stones below
  - Left column: critical path in sequence (diagnostics → GPS fix → fly waypoints → CV from altitude → geotagging accuracy → autonomous search → detect+centre+classify → SSSI → PLB → offset landing → payload → full L2)
  - Right column: parallel fine-tuning tasks (calibration, accuracy measurements, parameter tuning, data collection)
- Rangefinder/lidar: team has one available (model TBD). Key insight:
  - Barometric altitude = relative to launch point. Ground level varies across field. Could be 2-3m off.
  - Rangefinder = actual distance to ground. Use for: safe landing on uneven terrain, low hover-drop (~1m AGL)
  - New approach: instead of landing, descend to ~1m true AGL using rangefinder, release payload, fly away. Avoids terrain risk.
  - Can deduce terrain elevation: GPS_alt − rangefinder = ground_level. Useful for knowing slopes near casualty.
  - Added to pipeline: "Rangefinder Low Drop" in payload stage, "Rangefinder-Assisted Landing" in landing stage
  - Added to design choices: Altitude & Terrain category (altitude source, rangefinder sensor, terrain deduction)
- Site consistency: all stale script references fixed (last one was pi_9_resolution_test.py in flight-day-tiers.ts)
- All requirements R01-R12 now match actual AENGM0074 brief across all tabs

### 2026-03-11 (continued) — Enrichment, documentation, cross-reference audit

- **Stepping stone enrichment**: All 14 critical path steps and 20 parallel tasks now have specific scripts, flags (--headless --stream, --dry-run, --model), stream URLs (http://PI_IP:8090/8091), config.py variable names, simulator rehearsal options, bench pre-test scripts, companion experiment scripts
- **Documentation audit**: LevelsTab has grown to 573 lines (was 279) with no blueprint. Created `docs/levels-tab-blueprint.md` with full component hierarchy, data source map, update instructions. Updated CLAUDE.md line counts and data update table.
- **Cross-reference audit against flight day docs**: Found critical gap — Mission Planner AUTO test (STEP 1 in FLIGHT_DAY_CHECKLIST.md) was missing from L2_CRITICAL_PATH. Added as cp-2a "Mission Planner AUTO waypoints" (row 3). Also includes RC kill switch safety test. All rows bumped by 1, milestones updated.
- **Clarification needed**: passive_watch.py vs tests/flight/1_passive_flight.py — which is canonical for cp-3? Both listed as options currently.
- **Still missing from flight day docs**: cp-6b (geofence standalone test) not in FLIGHT_DAY_CHECKLIST.md; cp-10 (PLB redirect) has no standalone test procedure; servo/payload standalone test not documented

### 2026-03-11 (continued) — Flight Day 1 plan + personal focus areas

- **Flight Day 1 practical plan**: Want clear steps somewhere (not Levels tab):
  1. Run diagnostics.py (nice UI or headless via PuTTY, with vision model)
  2. Fly drone via RC only (prove it flies, no scripts)
  3. Fly with Mission Planner connected + capture_training.py for video stream
  4. Run waypoint mission + passive script with geotagging + stream
  5. Test geofence standalone (create separate NFZ area)
  6. Simulate full mission in SITL (already have working components)
  7. Hook confirmed SITL simulation to real drone
- **Personal focus areas** (want in sidebar control or somewhere visible):
  1. Test standalone NFZ (geofence exclusion in ArduCopter)
  2. Add NFZ to main.py (integrate geofence into search pattern)
  3. Improve vision: retraining with real photos, try NCNN backend
  4. Understand FPS / image resolution / FOV → geotagging accuracy relationship
- **Model switching**: Want easy switching between models + compare on the field
- **Passive watch**: Should include geotagging logic + video stream + manual override option

### 2026-03-11 (continued) — Flight Day 1 in sidebar

- Flight Day 1 steps should be built into the dashboard as a visible checklist (right sidebar "Day 1" tab)
- Sequential on-field steps with scripts, stream URLs, what each step proves, and fallbacks
- Separate from Prep (day before) and Focus (dev areas) — this is the actual field day sequence

### 2026-03-11 (continued) — Documentation, BOOTSTRAP, Focus additions

- Want detailed documentation of how everything works — all in project directory since it's a group project
- Will write two reports later using this project as reference — everything needs to be properly documented
- BOOTSTRAP workflow concern: brain-dump.md should be appended after every user message, plus other workflow steps
- **New Focus items to add**:
  - Play around with lidar/rangefinder for distance-above-ground measurements
  - Servo release mechanism (Tarot) — not sure exactly how it's meant to work, need to understand and test
