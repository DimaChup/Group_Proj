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
