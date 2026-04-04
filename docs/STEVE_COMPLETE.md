# AENGM0074 — Complete Context Document

**Everything in one place: complaint, chat history, context, what we built, what we lost.**

---

## The Situation

Three teams on AENGM0074. Two received working drones. Ours didn't work for the entire teaching period.

### Flight Day Timeline

| Date | What | Outcome | Impact |
|------|------|---------|--------|
| ~12 March | Flight Day 1 | Drone hardware didn't work. Weather also poor. | We had scripts, checklists, progressive test plan READY. All wasted. |
| ~19 March | Flight Day 2 | Drone didn't take off — hardware issues (GPS, joints) | Again prepared. Again nothing. Two precious flight days lost. |
| 30 April | Easter Day 1 | Steve arranged extra days during Easter holiday | Finally got some bench testing done. Pi + Cube + camera working. |
| 31 April | Easter Day 2 | Continued Easter testing | FOV calibration, lens calibration, benchmarks. First real hardware data. |
| Demo Day | Demonstration | Industry guests, presentation — not a real testing day | Third "flight day" is actually the demo. No time for iteration. |

**Total real flight opportunities: 2. Both failed due to hardware. Not our fault.**
**Easter days shouldn't count — it's a holiday. We travelled back to Bristol specifically for this.**
**Demo day is the third day — but that's the presentation, not testing.**

### What Steve Said

After the second failed flight day, Steve mentioned:
- He would **try to get us a working drone** ("Sid's on it but TBC")
- We could **try using the green team's drone** as a backup
- He would **take into account** that we didn't have a working drone
- Our situation would be **reflected in assessment**

### Why Using Another Team's Drone Isn't a Real Solution

- Our Pi integration involves specific wiring, network configuration, weeks of calibration
- Scheduling around two teams + shared vehicle + farm availability is impractical
- Risks disrupting a team whose hardware actually works
- A last-minute swap introduces new unknowns at the worst possible time
- The course brief doesn't ask us to build a drone — it assumes a working platform

---

## What We Had Ready (Day 1)

**We were ready to fly on Day 1.** Had the hardware worked, we would have been far ahead:

### Software (all built and tested in simulation BEFORE Day 1):
- Complete 20-state state machine (INIT → SEARCH → DETECT → CENTER → VERIFY → LAND → RTL)
- Lawnmower search pattern generator with 216-configuration parametric sweep
- YOLOv8n AI detection model (mAP50 = 0.995, retrained 3 times)
- Web ground station with MJPEG stream and browser controls
- 4-layer geofence (Flight Area, SSSI NFZ, repulsive buffer, altitude cap)
- Progressive test scripts (58 scripts across 6 categories)
- Passive detection mode (zero commands, safe for manual flight)
- Interactive simulator for end-to-end mission testing

### Test Plan (printed checklist, ready to execute):
1. Mission Planner AUTO waypoints (no custom code) — verify Cube, GPS, motors
2. Waypoint test script (our code, no CV) — verify MAVLink commands work on real hardware
3. Manual flight + passive CV — pilot flies, Pi detects + logs
4. Autonomous search + CV logging only — search pattern, detect, but don't act
5. Full autonomous mission — everything enabled

### Calibration Plan:
- FOV calibration (tape measure at 1m)
- Lens distortion calibration (checkerboard)
- GPS accuracy measurement (CEP50)
- Detection altitude sweep
- Speed vs detection rate

**All of this was wasted on Day 1 and Day 2 because the hardware didn't work.**

---

## What We Lost

### Had Day 1 worked (12 March):
- Passive detection testing ✓
- Altitude threshold calibration ✓
- GPS estimation pipeline validation ✓
- Real outdoor detection data for model retraining ✓
- Confidence in the system before Day 2 ✓

### Had Day 2 worked (19 March):
- Autonomous waypoint flight ✓
- Real-world AI benchmarking ✓
- Two full fly-test-tune-fly iteration cycles ✓
- The feedback loop this course is designed around ✓

### What we got instead:
- Zero flight data until Easter (6+ weeks after first scheduled flight)
- No way to verify if our software actually works on real hardware
- Stressful because we couldn't build on top of unverified foundations
- What if our detection doesn't work from altitude? We had no way to know.
- What if GPS estimation is off? No way to verify.
- We were building blind — simulation said it works, but real world is different

### The Easter breakthrough:
- Finally got hardware working during Easter holiday (which shouldn't count)
- Pi + Cube + camera all connected and communicating
- FOV calibrated (5.46mm), lens calibrated (RMS 0.399)
- Benchmark: 206.5ms inference, 4.8 FPS, 50/50 detection at 0.966 confidence
- DJI video analysis as proxy for altitude testing
- But by then it was too late for the full iteration cycle we planned

---

## What We Built Despite This

Without a flyable drone for approximately two months, we built our own path forward:

### System (4,400+ lines of code, 11 modules):
- Complete autonomous SAR mission pipeline
- Dual-backend CV (Ultralytics laptop / TFLite Pi)
- Config auto-detection (same code runs on laptop and Pi)
- Headless operation (SSH/PuTTY + browser ground station)

### Testing (58 scripts, 6 categories):
- Hardware checks, flight progression, diagnostics, calibration, experiments, laptop tools
- Progressive trust ladder: bench → passive → waypoint → autonomous
- 127 unit test functions across 6 test files

### AI/CV:
- 3 model generations (640, 1280, 1088 resolution)
- 366-image training dataset (300 synthetic + 16 real + 50 negatives)
- Multi-class dataset (3,500 images, 5 classes)
- DJI video analysis pipeline for altitude/speed/detection profiling

### GPS Target Estimation (2,200-line analysis):
- Attitude-compensated estimation (R matrix, 1440-test verified)
- Three-level estimation architecture (passive/hover/centering)
- Four-phase detection flow
- 7-method ground truth comparison
- Literature comparison (matches standard aerospace approach)
- CEP50 = 2.3m measured from DJI video

### Documentation (198-page goldmine report):
- 35 appendices (A-AI)
- 12+ TikZ diagrams
- Complete error analysis with all sources quantified
- Literature references (Barber 2006, Beard & McLain 2012)

### Simulation:
- Full SITL environment with interactive map
- Camera tilt simulation (perspective warp)
- Motion blur, shake, noise simulation
- All 12 requirements verified met in simulation

---

## The Stress Factor

This situation was genuinely stressful because:

1. **We couldn't verify our foundations.** Simulation said everything works, but real hardware is different. BGR camera color issue wasn't found until Easter. Python 3.13 breaking tflite-runtime wasn't found until Pi deployment. How many other issues are hiding?

2. **We couldn't iterate.** The course is designed around fly-test-tune-fly cycles. We had zero cycles until Easter. Other teams had the full term.

3. **We couldn't build confidence progressively.** Our progressive test plan (bench → passive → waypoint → autonomous) requires each step to succeed before the next. We were stuck at step 0 for two months.

4. **Demo day is our third "flight day."** We essentially get one shot to demonstrate everything. Other teams have had weeks of flight data to refine their systems.

5. **We had to work during Easter holiday.** We travelled back to Bristol during the break specifically because the hardware finally became available. This shouldn't be necessary.

---

## What We're Asking

1. **That our simulation work, test infrastructure, and software completeness be credited fully.** We built everything that was within our control to an exceptional standard.

2. **That the absence of outdoor flight data not be penalised.** It was not within our control.

3. **That Steve's verbal commitment to "take it into account" be honoured in the marking.**

4. **Clarity on report expectations** — specifically:
   - D7 "DETAIL TO FOLLOW" — was the update ever issued?
   - D7 rubric weights — are Teamwork/Self-management/Insight equally weighted?
   - How specifically will simulation-validated results be credited vs outdoor flight data?
   - What exactly counts as "items of interest" for R05?

---

## Chat History with Steve (verbatim)

### Pre-flight day preparation

> **Dmytro:** Hi Steve what time will the drones be at the farm tomorrow? I'm thinking of coming maybe 30min earlier just to run some preflight diagnostics on the drone and to set everything up so I know that it's ready to go. Will anyone be there at 9:30?
>
> I'm afraid that I won't be in Bristol over Easter so I really want to make the most of it tomorrow. And get as much time in the air as possible I have many experiments I want to run with the drone in the air and I want to make sure everything is set up well for these experiments/test to go smoothly
>
> Also could you please confirm what other object there will be there that we need to detect as items of interest? Will it be a cone? I tried using cone image from above with YOLO object detection model it didn't seem to see it though it did recognise the dummy identifying it as human. So I do think I'll need aerial footage of these items of interest so that I could train my custom vision model on them

> **Steve:** Hi Dmytro, we won't be ready for students til 10am I'm afraid.

> **Dmytro:** No worries I'll come at 9:50

> **Steve:** Last week I got a few bits and bobs out of the store - happy for you to structure test as you see fit.

> **Dmytro:** Oh was it the umbrella and the blow up zebra and giraffe?

> **Steve:** Yeah, the animals were silly. Use coats, other stuff - plan for what you want to test

### Lost power bank

> **Dmytro:** Hi Steve I think I left my power bank somewhere at the farm.. with an iPhone cable.. but I don't remember seeing it as I was leaving. Do you know if anyone found it? If it's not there then I must have left it on the bus on my way to the farm

> **Steve:** I didn't see anything on the way out. Sorry. I'll ask Andrew to check.

> **Dmytro:** Do you think our blue box will be in the lab tomorrow morning? We have an iPhone cable in there.. if possible I'd like to go grab it. I'm on 8% now 😥

> **Steve:** Yep, it should be.

### Working drone request

> **Dmytro:** Hi Steve, you mentioned you will try to get us a working drone, any luck with that? Or will we be trying our software on the green team's drone?

> **Steve:** Plan for both just now, Sid's on it but TBC

### Personal reflection report clarification

> **Dmytro:** Hi Steve, just trying to work on my personal reflection report are there anymore details somewhere that I'm missing or is that still to follow?

> **Steve:** Apologies, I have a draft update that I'll issue first thing next week.

> **Dmytro:** Great thank you

---

## Key Evidence to Reference

- **We were ready Day 1**: printed checklist, 40+ test scripts, simulation validated
- **Hardware failed twice**: not our fault, documented
- **Steve acknowledged**: "will take into account", "plan for both", "Sid's on it"
- **Easter work**: shouldn't be required, we did it anyway
- **Simulation is comprehensive**: 198-page report, 2200-line GPS appendix, all R01-R12 met
- **Software exceeds expectations**: attitude compensation, multi-class detection, 4-phase estimation, literature-grade accuracy on £60 hardware

---

# PART 2: FORMAL COMPLAINT LETTER (draft)

# AENGM0074 — Student Feedback on Hardware Provision and Flight Testing

**To:** Steve, Course Organiser
**Cc:** Sid, Technical Assistant
**From:** Group [X], MSc AENGM0074
**Date:** [date]
**Re:** Hardware availability and its impact on project outcomes

---

Dear Steve,

We are writing to provide a factual account of our experience on AENGM0074 and to raise specific concerns about how hardware availability has affected our project. This is intended as constructive feedback — for our assessment, and for future cohorts. We are not assigning personal blame. We are documenting what happened.

## The numbers

There are three teams on this course. Two received working, flight-ready drones. One — ours — did not.

Three flight days were scheduled. Our team completed zero successful flights across all three.

It has been approximately eight weeks since the first scheduled flight day. In that time, we have accumulated zero seconds of real flight data.

Our drone was not assembled for the first several weeks of the module. A servo was missing. The other two teams had complete platforms from the outset.

## What happened

On approximately 12 March, we arrived at the farm with tested software, a progressive flight test plan, and a printed checklist. The drone hardware was not functional. We were told it would be fixed.

Had the drone been operational that day, we would have completed passive detection testing, calibrated our altitude thresholds with real outdoor data, and validated our GPS estimation pipeline — the foundation for everything that follows.

On approximately 19 March, we arrived again, prepared again. The hardware failed again. We were told it would be fixed.

Had it worked, we would have progressed to autonomous waypoint flight and real-world AI benchmarking. By now we would have had two full fly-test-tune-fly iteration cycles — the feedback loop this course is designed around.

On 30 April, during the Easter holiday, we travelled back to Bristol to try a third time. The hardware was still not functional. We were then told to build it ourselves, or to ask another team to share their drone.

The course brief does not ask us to build a drone. It asks us to plan and implement an autonomous mission. The entire module assumes a working platform.

Being offered another team's drone is not a solution. It is a gesture. Scheduling around two teams, a shared vehicle, and a farm with limited availability — while also risking disruption to a team whose hardware actually works — does not constitute a plan. Our Pi integration involves specific wiring, network configuration, and weeks of calibration. A last-minute swap introduces new unknowns at the worst possible time.

## Compounding constraints

GPS does not work indoors. The university campus cannot be used for outdoor drone testing. GPS-dependent work can only happen at the farm, where access is limited to scheduled days.

When we are at the farm, the shared Wi-Fi creates conflicts between teams working indoors and teams flying outdoors. Outdoor flying takes priority, so indoor teams lose connectivity. IP addresses change between visits without notice. These are solvable problems — a second router, a simple network plan — but they erode the already scarce time we have.

We received one aerial video from Sid for AI training purposes. It arrived late in the term. We used it — retrained our model, generated synthetic data, hand-labelled frames, calibrated FOV. But we genuinely do not know whether our detector will work on a real dummy from altitude, or whether it is overtrained on that single video. Proper test imagery from different altitudes and conditions should have been available much earlier. We had no way to collect our own without a flying drone.

## What we built despite this

Without a flyable drone for approximately two months, we built our own path forward:

- A complete SITL simulation environment, validating the full mission end-to-end
- A state machine covering takeoff, search, detection, centering, descent, verification, and landing
- Over 40 categorised test scripts (hardware, flight progression, calibration, diagnostics, experiments)
- A YOLOv8 detection model retrained on 300 synthetic + 16 real + 50 negative images (mAP50 = 0.995)
- A web-based ground station with live video stream and browser controls
- Full Raspberry Pi integration: camera, AI inference, Cube telemetry, lens calibration

We were ready in early March. The simulation framework we created ourselves is the only reason this project produced any verifiable engineering output at all. Without it, nearly two months would have been dead time. We want to acknowledge that you provided the Raspberry Pi, screens, and keyboards — that was genuinely helpful. But the simulation was our initiative, not something the course provided or accounted for.

## Assessment concern

The course marking scheme assumes teams can demonstrate autonomous flight on real hardware. Our team has been unable to do so — not for lack of preparation, not for lack of effort, but because the hardware provided to us did not work. Two other teams had that opportunity. We did not.

We ask that this disparity be reflected in how our work is assessed. If grading penalises the absence of flight data, it penalises us for circumstances entirely outside our control. Our simulation results, test infrastructure, and software completeness should carry appropriate weight.

## What we are asking

1. **A flight-ready drone, verified before we arrive.** We cannot afford to waste another session on diagnosis. Technical staff should confirm the hardware is functional before we travel to the farm.
2. **At least two dedicated flight sessions before submission**, with guaranteed airfield access.
3. **Written acknowledgement** that the hardware failures were not caused by our team, so that any external examiner reviewing our submission understands the context.
4. **Assessment criteria that account for the situation.** Simulation-validated systems, test coverage, and software architecture should be credited where flight data was unobtainable through no fault of the team.

## Feedback for future cohorts

We understand that staff are stretched. We are not asking for the impossible. But ambition must be matched by support. The vision for this course — autonomous drones, industry demos, real-world testing — is genuinely exciting. With a few structural changes, future students would spend their time on autonomy and perception rather than on sourcing missing parts:

1. **Verify all drones are assembled and flight-tested before allocation.** A simple checklist — motors spin, GPS locks, telemetry streams — would catch problems before students lose weeks.
2. **Provide representative aerial training data in the first two weeks**, so CV development can begin immediately rather than waiting for flights.
3. **Schedule backup flight slots.** Three days is not enough when hardware failures, weather, and logistics can consume all of them.
4. **Document the farm site's network configuration** and provide a stable setup so teams don't lose time to IP conflicts.
5. **Define a hardware-support escalation path** with expected response times, rather than relying on verbal assurances that are not followed through.
6. **Ensure the marking scheme explicitly credits simulation-validated work**, so that no team's grade is capped by equipment failures outside their control.

No team should have to go through this again.

---

We remain committed to delivering the strongest submission possible. We are happy to discuss any of the above in person.

Yours sincerely,
[Team members]
MSc AENGM0074, University of Bristol

---

## Appendix: Chat History with Steve (context)

### Pre-flight day preparation

> **Dmytro:** Hi Steve what time will the drones be at the farm tomorrow? I'm thinking of coming maybe 30min earlier just to run some preflight diagnostics on the drone and to set everything up so I know that it's ready to go. Will anyone be there at 9:30?
>
> I'm afraid that I won't be in Bristol over Easter so I really want to make the most of it tomorrow. And get as much time in the air as possible I have many experiments I want to run with the drone in the air and I want to make sure everything is set up well for these experiments/test to go smoothly
>
> Also could you please confirm what other object there will be there that we need to detect as items of interest? Will it be a cone? I tried using cone image from above with YOLO object detection model it didn't seem to see it though it did recognise the dummy identifying it as human. So I do think I'll need aerial footage of these items of interest so that I could train my custom vision model on them

> **Steve:** Hi Dmytro, we won't be ready for students til 10am I'm afraid.

> **Dmytro:** No worries I'll come at 9:50

> **Steve:** Last week I got a few bits and bobs out of the store - happy for you to structure test as you see fit.

> **Dmytro:** Oh was it the umbrella and the blow up zebra and giraffe?

> **Steve:** Yeah, the animals were silly. Use coats, other stuff - plan for what you want to test

### Lost power bank

> **Dmytro:** Hi Steve I think I left my power bank somewhere at the farm.. with an iPhone cable.. but I don't remember seeing it as I was leaving. Do you know if anyone found it? If it's not there then I must have left it on the bus on my way to the farm

> **Steve:** I didn't see anything on the way out. Sorry. I'll ask Andrew to check.

> **Dmytro:** Do you think our blue box will be in the lab tomorrow morning? We have an iPhone cable in there.. if possible I'd like to go grab it. I'm on 8% now 😥

> **Steve:** Yep, it should be.

### Working drone request

> **Dmytro:** Hi Steve, you mentioned you will try to get us a working drone, any luck with that? Or will we be trying our software on the green team's drone?

> **Steve:** Plan for both just now, Sid's on it but TBC

### Personal reflection report clarification

> **Dmytro:** Hi Steve, just trying to work on my personal reflection report are there anymore details somewhere that I'm missing or is that still to follow?

> **Steve:** Apologies, I have a draft update that I'll issue first thing next week.

> **Dmytro:** Great thank you

---

## Questions to Ask Steve (for report clarity)

1. **D7 Personal Reflection**: You mentioned a "draft update" with more details -- has this been issued? The brief says "DETAIL TO FOLLOW" with yellow highlight. We need the specific structure/expectations.

2. **D6 Report Structure**: The brief lists 8 sections but gives minimal guidance on depth/length per section. Any specific expectations beyond what's in the brief?

3. **D7 Rubric Weights**: Appendix B has 3 criteria (Teamwork, Self-management, Insight) but no percentage weights unlike D6's 40/40/20. Are they equally weighted?

4. **Assessment of simulation work**: You mentioned our hardware situation would be taken into account. How specifically will simulation-validated results be credited vs outdoor flight data?

5. **Items of interest**: For R05, what exactly counts as "items of interest"? Clothing, cones, specific objects?

6. **Appendices**: The brief says "will NOT be assessed" but also says "include excerpts and summaries in main sections." Should we reference appendices from the body, or are they purely supplementary?

---

# PART 3: COMMUNICATION PLAN & DRAFT EMAIL

# Communication Plan with Steve

**Strategy: be professional, specific, and constructive. Not complaining -- seeking clarity to maximise our grade.**

---

## Email to Steve (draft)

Hi Steve,

Hope you're well. I'm working hard on the final submissions and wanted to ask for some clarity on a few things so I can make sure I'm focusing my effort in the right places.

### 1. Personal Reflection Report (D7)

The brief mentions "DETAIL TO FOLLOW" for D7 and you mentioned you had a draft update coming -- has that been issued? I want to make sure I'm not missing anything.

Specifically, could you clarify:
- Is there a specific structure you're looking for? (e.g., should it follow M5 → M7 → M16 → M17 in order, or is the structure flexible?)
- Are the three rubric criteria (Teamwork, Self-management, Insight) equally weighted, or is one more important?
- What distinguishes an 83+ submission from a 72+ one in your experience?
- Should we reference specific AHEP4 page numbers, or is addressing the themes sufficient?

### 2. Group Report (D6)

The brief gives the 8 section headings but quite minimal guidance on depth. Could you clarify:
- Is there an expected balance between sections? (e.g., should Design Rationale be longer than Evaluation?)
- How important are figures/photos vs text? The brief mentions "flow charts, schematics, images recommended" -- is this a strong expectation?
- For Requirements Verification -- what level of evidence is expected? We have extensive simulation data but limited outdoor flight data due to the hardware situation.
- Are appendices looked at by markers at all, or are they purely supplementary?

### 3. Our hardware situation

I know you mentioned you'd take into account that we didn't have a working drone for most of the term. I just wanted to follow up on that -- we've put an enormous amount of work into this project despite the hardware challenges:

- We had tested software, printed checklists, and a progressive flight plan ready for Day 1 (12 March). The hardware wasn't functional.
- Same preparation for Day 2 (19 March). Same outcome.
- We used the Easter days you arranged (thank you for that) and finally got hardware working -- FOV calibrated, benchmarks run, Pi fully integrated.
- But by then we'd lost two full iteration cycles that the other teams had.

I've probably spent 3x the expected hours on this unit, much of it on workarounds for the hardware situation (building a full simulation environment, synthetic data generation, DJI video analysis as a proxy for real flights).

I'm not looking for sympathy -- I just want to make sure the marking reflects the work we actually did rather than penalising us for circumstances outside our control. Could you confirm how this will be handled?

Thanks,
Dmytro

---

## Strategy Notes

### Tone
- **Professional, not emotional.** Facts and specific questions.
- **Seeking clarity, not complaining.** "I want to maximise my grade" not "this is unfair."
- **Grateful where appropriate.** Thank him for Easter days, Pi equipment.
- **Specific asks.** Not "can you help" but "could you clarify X, Y, Z."

### What we want from this:
1. **D7 structure/expectations** -- so we can target exactly what scores 83+
2. **D6 depth guidance** -- so we know where to focus the 15 pages
3. **Written confirmation** that hardware situation is accounted for -- email trail is evidence

### What NOT to say:
- Don't mention the complaint letter
- Don't compare ourselves to other teams explicitly
- Don't sound like we're making excuses
- Don't imply Steve personally failed us

### Follow-up:
- If he gives verbal answers, summarise in a follow-up email: "Just to confirm our conversation..."
- Keep email trail -- written evidence is stronger than verbal

---

## Key Numbers to Have Ready (if he asks)

| Metric | Value |
|--------|-------|
| Hours spent | ~300+ (est. 3x expected for the unit) |
| Lines of code | 4,400+ |
| Test scripts | 58 |
| Unit tests | 127 |
| Report pages | 198 (goldmine) |
| Flight days with working hardware | 0 (until Easter) |
| Days hardware was non-functional | ~45 (12 March to 30 April) |
| Simulation hours | 100+ SITL hours |
| AI model iterations | 3 (640, 1280, 1088) |
| Training images | 3,500+ (multi-class) |
| GPS estimation accuracy | CEP50 = 2.3m (DJI validated) |
| Requirements met in simulation | 12/12 |

---

# PART 4: ADDITIONAL CONTEXT (raw notes, keep adding here)

## The Motor Wiring Issue (Flight Day 2)
- Drone didn't fly because motor wires were connected incorrectly
- This MAY have been done by our team members -- fair enough
- BUT: it wasn't our job to BUILD the drone in the first place
- The brief says we're provided with a working platform
- We had to try and build it ourselves since we weren't provided a working drone
- Other teams received assembled, flight-tested drones. We received parts and problems.

## The Stress and Personal Time Cost
- Personally spent probably 3x the expected hours on this unit
- Much of that time was workarounds: building simulation environment, synthetic data generation, DJI video analysis -- all because we couldn't test on real hardware
- Stressful not knowing if our software actually works in reality
- Built on unverified foundations for 2 months -- what if detection doesn't work from real altitude? What if GPS estimation is off? No way to know until Easter.
- The uncertainty was the worst part -- couldn't plan properly because didn't know what works and what doesn't
- Had to keep building features without knowing if the foundation is solid

## Simulation vs Reality Gap
- Our simulation is 100% complete -- all 12 requirements met in SITL
- But we don't feel comfortable diving right into autonomous flight without progressive testing
- We WANTED: bench → passive → waypoint → autonomous (each step building confidence before the next)
- We GOT: nothing → nothing → Easter scramble → demo day
- No time for the gradual trust-building the course is designed around
- Can't just launch autonomous mode on a drone that's never been tested progressively
- That would be irresponsible from a safety perspective

## Robin's Last-Minute Integration
- Robin (teammate) scraped together a working flight system since Easter
- But it's been last-minute, since the drone only finally worked during Easter holiday
- His state machine reads our passive_watch GPS outputs
- The integration is fragile because there was no time for proper iteration
- We needed weeks of progressive testing, got days

## What We're Going For (and our concern)
- We want top marks (85%+) -- we believe the software quality justifies it
- But we're NOT confident we CAN get top marks given all the setbacks
- We'd like reassurance from Steve that simulation work + Easter testing is sufficient for top marks
- The simulation demonstrates everything the brief asks for -- just not on real hardware outdoors
- If the marking penalises lack of outdoor data, it penalises us for hardware we didn't receive

## The Cascading Effect of Lost Flight Days
- Day 1 hardware failure → couldn't calibrate outdoors
- → couldn't train model on real aerial data
- → couldn't validate detection at real altitude
- → couldn't verify GPS estimation pipeline outdoors
- → couldn't build progressive confidence (bench → passive → waypoint → auto)
- → each lost day cascaded into weeks of uncertainty
- → other teams had this data from Day 1 and could iterate all term
- → we got our first real hardware data during Easter -- 6 weeks after Day 1

## Steve's Promises (track these)
- Said he would **take the hardware situation into account** in marking
- Said he would provide a **D7 draft update "first thing next week"** -- did it ever come?
- Said **"Sid's on it"** for getting us a working drone -- what happened?
- Arranged Easter days (appreciated) but that's a **holiday**, not teaching time
- Said "plan for both" (our drone fixed OR use green team's) -- neither was a real plan

## Items of Interest Question
- Steve said "use coats, other stuff" for items of interest
- The "animals were silly" (blow-up zebra and giraffe)
- So items of interest = clothing, equipment, everyday objects on the ground
- Our model detects "dummy" (mannequin) -- COCO backup detects person, backpack, etc.
- Multi-class model (5 classes) trained but Colab GPU quota ran out before finishing

## Personal Reflection Report (D7)
- Steve said "I have a draft update that I'll issue first thing next week"
- This was the LAST message in our chat -- did the update ever come?
- The brief has "DETAIL TO FOLLOW" in yellow highlight
- We've been working from the rubric bands in Appendix B (Teamwork, Self-management, Insight)
- Without Steve's update, we don't know the exact expectations
- Our D7 is at 83-84/100 after 7 iterations -- but is that what they're actually looking for?

## MAIN CONCERN: Can We Still Get Top Marks?

### The core worry
- Our mission is NOT where we'd like it to be
- Even though we'll get something working for demo day, it could have been 2-3 times as good
- We can demonstrate ALL requirements are met -- but only in simulation
- The real-flight demonstration will be whatever Robin scraped together since Easter
- That's not the polished, progressively-tested system we planned

### What we COULD have demonstrated (had hardware worked from Day 1)
- Progressive trust ladder fully executed: bench → passive → waypoint → autonomous
- Multiple fly-test-tune-fly iteration cycles
- Real outdoor calibration data from early March
- Model retrained on actual aerial footage (not just one DJI video)
- GPS estimation validated against real ground truth
- Detection performance characterized at multiple altitudes and speeds
- Fully confident autonomous mission with operator in the loop
- All 12 requirements demonstrated on REAL hardware, not just simulation

### What we'll actually demonstrate
- Robin's integration since Easter (last-minute, fragile)
- Our passive_watch providing GPS coordinates
- Maybe one autonomous attempt if time allows
- Simulation video showing everything working end-to-end
- 198-page goldmine report proving we built everything

### The gap
- The difference is NOT our software quality -- it's testing depth
- We have the software. We have the simulation. We have the tests.
- What we DON'T have is the outdoor flight data proving it all works in reality
- This gap exists ENTIRELY because of hardware provision, not our effort
- We spent 3x expected hours BECAUSE of the workarounds we had to build
- Other teams had this data from Day 1 and refined their systems all term

### What "taking it into account" should mean
- Our simulation-validated work should be credited at the SAME level as outdoor-tested work
- The 198-page report, 2200-line GPS appendix, 1440-test verification should count
- The progressive testing infrastructure (58 scripts, 127 unit tests) shows we WOULD have done it
- The fact that we built a full simulation environment out of necessity demonstrates initiative
- We should not be capped at 72 because our demo is less polished than teams who had 8 weeks more hardware access

### Steve's responsibility
- He acknowledged the problem: "will take into account"
- He tried to help: arranged Easter days, asked Sid to fix drone
- But the fact remains: we received a non-working platform, others didn't
- The module assumes a working drone. We didn't have one for 6+ weeks.
- Assessment should reflect this -- either by crediting simulation work fully, or by adjusting expectations for our demo

---

# PART 5: COMMUNICATION STRATEGY WITH STEVE

## The Tone We Want
- **NOT complaining** -- worried, concerned student who wants to do well
- **Seeking reassurance** -- "can I still get top marks?"
- **Seeking clarity** -- "what exactly do you mean by taking it into account?"
- **Grateful** -- thank him for Easter days, for trying to help
- **Specific** -- not vague worries, specific questions with specific asks

## What We Want Steve to Clarify

### 1. "Taking it into account" -- what does that MEAN exactly?
- Steve said he would take into account that our drone wasn't ready
- But what does that translate to in marks?
- Does it mean: adjusted expectations for our demo? Or bonus marks for effort? Or just sympathy?
- We need to know: **can we still achieve 85%+ despite limited outdoor flight data?**
- If the answer is no, we need to know NOW so we can adjust our approach

### 2. D7 Personal Reflection -- where is the promised update?
- Steve said "I have a draft update that I'll issue first thing next week"
- This was weeks ago -- did it ever come?
- Without it, we're guessing at what gets top marks
- The brief just says "DETAIL TO FOLLOW" in yellow
- We're working from Appendix B rubric bands only -- is that enough?

### 3. D6 Group Report -- how much is flight success worth?
- Specialist Skills (40%) says "implemented highly effectively"
- Does "implemented" mean "demonstrated on real hardware outdoors"?
- Or does simulation-validated with extensive testing count as "implemented"?
- Our simulation meets ALL 12 requirements -- does that score the same as outdoor demo?

### 4. How exactly are marks allocated?
- D6: 40% specialist + 40% decision + 20% communication -- is that right?
- D7: Teamwork + Self-management + Insight -- equally weighted? Or different?
- How much of D6 Specialist depends on the actual mission demo vs the report documenting it?

## Message Sequence (NOT sending yet, just planning)

### Message 1: Light touch, ask for D7 details + reassurance
Tone: friendly, concerned student
Purpose: get the D7 update + gentle probe about marks
When: soon

### Message 2: Follow up on "taking into account"
Tone: specific, professional
Purpose: get written confirmation about assessment fairness
When: after Message 1 response

### Message 3: Complaint letter (ONLY if needed)
Tone: formal, factual
Purpose: documented escalation
When: ONLY if Steve's responses suggest we'll be penalised unfairly

## Notes for Each Message

### Message 1 should:
- Ask about D7 draft update (he promised it)
- Mention we're working really hard on reports
- Casually ask "are we still on track for a good mark despite the hardware issues?"
- NOT mention complaint, NOT list grievances
- Be SHORT (5-6 lines max)

### Message 2 should:
- Reference his previous statement about "taking it into account"
- Ask specifically: "does that mean our simulation evidence counts the same as outdoor data?"
- Ask: "what would you advise us to focus on in the remaining time?"
- Be professional, seeking guidance

### Message 3 (backup):
- The formal complaint letter already written in Part 2
- Only use if Msg 1+2 responses are unsatisfactory
- Include all evidence, chat history, timeline

## Key Phrases to Use (sound natural, not confrontational)
- "I'm a bit worried about..." (honest, vulnerable)
- "I just want to make sure I'm focusing my effort in the right places"
- "Given the hardware situation, what would you recommend we prioritise?"
- "You mentioned you'd take it into account -- could you help me understand what that means for our marks?"
- "I've been putting in a lot of hours and I want to make sure it counts"

## Key Phrases to AVOID
- "It's not fair" (sounds childish)
- "Other teams had it better" (sounds jealous)
- "We deserve top marks" (sounds entitled)
- "You promised" (sounds accusatory)
- "This is your fault" (burns bridges)
