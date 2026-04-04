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
