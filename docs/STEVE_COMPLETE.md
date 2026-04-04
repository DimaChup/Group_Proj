# AENGM0074 -- Communication with Steve: Scoring Clarity and Assessment Fairness

---

## Key Points to Make

1. **D7 update is overdue.** Steve promised a draft update for the personal reflection report -- it has not been issued. The brief still reads "DETAIL TO FOLLOW."
2. **"Implemented" needs defining.** The top rubric band says technologies "implemented highly effectively." We need to know whether simulation-validated work counts at the same level as outdoor flight demonstration.
3. **"Taking it into account" needs specifics.** Steve acknowledged our hardware situation verbally. We need written clarity on what that means for assessment.
4. **Our evidence base is strong.** 12/12 requirements met in SITL, 58 test scripts, retrained AI model (mAP50 = 0.995), Pi hardware integration verified, 198-page report. The gap is outdoor flight data -- and that gap is not our fault.
5. **We are seeking guidance, not lodging a complaint.** The goal is clarity so we can focus remaining effort effectively.

---

# PART 1: PRIMARY MESSAGE TO STEVE

**Send: Friday 4 April morning**

---

Hi Steve,

I am working through the final submissions and want to make sure I am targeting the right areas. I have read the brief carefully and have a few specific questions, if you do not mind.

**Specialist Skills (40%)**

The top band refers to technologies "implemented highly effectively, showing initiative, autonomy, and creativity." I would like to understand what "implemented" means in practice. Does it require outdoor flight demonstration with real data, or can a system that is fully validated in simulation, bench-tested on Pi hardware, and supported by quantitative evidence reach the same level?

To give context: we have all 12 requirements met end-to-end in SITL, 58 test scripts across 6 categories, attitude-compensated GPS target estimation verified against DJI flight video (CEP50 = 2.3 m), a retrained YOLOv8 model (mAP50 = 0.995 on 366 images), Pi hardware integration verified (camera, Cube, inference at 4.8 FPS), and a geofence with SSSI avoidance. What we do not have is extensive outdoor flight data, because our drone hardware was not functional until the Easter sessions you arranged.

Can a simulation-validated system with this depth of evidence realistically score 90+ on Specialist Skills, or is there an implicit expectation of demonstrated outdoor flight that would cap us lower regardless of software quality?

**Decision Making (40%)**

The top band mentions "confidence and creativity in adapting to changing and unfamiliar circumstances." We have MCDA trade studies, STEEPLE analysis, a 216-configuration parameter sweep for the search pattern, weather adaptation, and a section on decisions that changed during the project. Our hardware situation essentially required us to develop a simulation-first approach -- building a complete SITL environment, synthetic training data pipeline, and DJI video analysis as proxies for real-world data we could not collect. Is that the kind of adaptation this criterion rewards? Is there anything specific that separates a strong submission from an outstanding one here?

**Communication (20%)**

The top band says "engaging and professional, making use of innovative techniques and resources." We have TikZ-generated diagrams, pgfplots data visualisations, a professional LaTeX layout, and a comprehensive report. What we do not have many of are photographs of real hardware in the field or screenshots from outdoor ground station use. How important are real-world photographs compared to generated technical diagrams? Would the absence of hardware photography significantly affect the Communication score?

**D7 Personal Reflection**

You mentioned a draft update for D7 with more details on what is expected -- has that been issued? The brief still says "DETAIL TO FOLLOW" with a yellow highlight, and I want to make sure I am not missing something. We have been working from the Appendix B rubric (Teamwork, Self-management, Insight) and the AHEP4 standards (M5, M7, M16, M17), but I am unsure whether there is a specific structure you expect or whether the three criteria are equally weighted.

**Final question**

I have spent considerably more hours than expected on this unit, much of it building workarounds for the hardware situation -- the simulation environment, synthetic data generation, video analysis tools, the entire progressive testing infrastructure. I built all of that because the drone was not available and I wanted to ensure the engineering output was still substantive even without flight data. I am not looking for special treatment; I would simply appreciate your guidance on where to focus my remaining time before submission.

Thanks,
Dmytro

---

## Strategy Notes

### Possible responses and how to handle them

1. **Best case:** "Simulation-validated work absolutely counts. Focus on showing the depth of your testing and decision-making process. 90+ is achievable." This gives written confirmation and a clear target.
2. **Good case:** "The rubric does not require outdoor flight. Show comprehensive evidence and justified decisions." Implicit confirmation.
3. **Neutral case:** "It depends on the quality of the report." Follow up with: "Could you give an example of what would push a report from 83 to 90+ in Specialist Skills?"

### If he indicates simulation does not fully count

- The rubric says "implemented highly effectively" -- it does not say "demonstrated outdoors."
- Ask: "Is there anything we can do in the remaining time to strengthen that area? Would additional quantitative analysis from Easter bench testing help?"
- Adjust report framing: emphasise process and evidence-based decisions, not just the end product.
- Lean into Decision Making (40%) where the adaptation narrative is genuinely strong -- hardware constraints forced creative solutions, which is what the criterion rewards.
- If necessary: accept 75-78 on Specialist, target 90+ on Decision Making and Communication to keep the overall above 83.

### Follow-up plan

1. **If he replies by text:** save the reply immediately -- this is written evidence.
2. **If he gives a vague reply:** send a clarifying follow-up: "Just to make sure I understand -- you are saying [paraphrase]. Is that correct?" Seek specificity.
3. **If he says "come talk to me":** go, then follow up by email: "Hi Steve, just to confirm our conversation today -- you said [X, Y, Z]. Thanks for the guidance." Create a paper trail.
4. **If he does not reply by Monday:** send a brief follow-up: "Hi Steve, just following up on my message from Friday -- any guidance you could share would be really helpful as I am finalising the reports this week."
5. **If his reply raises concerns** (e.g., outdoor data is required for top marks): consider the formal feedback letter (Part 2 below) as a last resort. Try to resolve informally first.

---

# PART 2: FORMAL FEEDBACK LETTER (draft -- use only if needed)

**To:** Steve, Course Organiser
**Cc:** Sid, Technical Assistant
**From:** Group [X], MSc AENGM0074
**Date:** [date]
**Re:** Hardware availability and its impact on project outcomes

---

Dear Steve,

We are writing to provide a factual account of our experience on AENGM0074 and to raise specific concerns about how hardware availability has affected our project. This is intended as constructive feedback -- for our assessment and for future cohorts. We are not assigning blame. We are documenting what happened.

## Summary of the situation

There are three teams on this course. Two received working, flight-ready drones. Ours did not.

Three flight days were scheduled. Our team completed zero successful flights across all three.

It has been approximately eight weeks since the first scheduled flight day. In that time, we have accumulated zero seconds of real flight data.

Our drone was not assembled for the first several weeks of the module. A servo was missing. The other two teams had complete platforms from the outset.

## Timeline

| Date | Event | Outcome |
|------|-------|---------|
| ~12 March | Flight Day 1 | Drone hardware not functional. We had scripts, checklists, and a progressive test plan ready. |
| ~19 March | Flight Day 2 | Drone did not take off (GPS, joint issues). Again fully prepared. |
| 30 March | Easter Day 1 | Steve arranged extra days during Easter. Bench testing completed: Pi + Cube + camera working. |
| 31 March | Easter Day 2 | FOV calibration, lens calibration, benchmarks. First real hardware data. |
| Demo Day | Demonstration | Industry guests and presentation -- not a testing day. |

## What happened at each stage

On approximately 12 March, we arrived at the farm with tested software, a progressive flight test plan, and a printed checklist. The drone hardware was not functional. We were told it would be fixed.

Had the drone been operational, we would have completed passive detection testing, calibrated altitude thresholds with real outdoor data, and validated the GPS estimation pipeline.

On approximately 19 March, we arrived again, prepared again. The hardware failed again.

Had it worked, we would have progressed to autonomous waypoint flight and real-world AI benchmarking -- two full iteration cycles of the feedback loop this course is designed around.

During the Easter holiday, we travelled back to Bristol to try a third time. The hardware was still not fully functional. We were advised to build it ourselves or to ask another team to share their drone.

The course brief does not ask us to build a drone. It asks us to plan and implement an autonomous mission. The module assumes a working platform.

## Why sharing another team's drone is not a practical solution

- Our Pi integration involves specific wiring, network configuration, and weeks of calibration.
- Scheduling around two teams, a shared vehicle, and limited farm availability is impractical.
- It risks disrupting a team whose hardware works.
- A last-minute swap introduces new unknowns at the worst possible time.

## Additional constraints

- GPS does not work indoors. Outdoor testing is only possible at the farm on scheduled days.
- Shared Wi-Fi at the farm creates conflicts between teams. Outdoor flying takes priority, so indoor teams lose connectivity. IP addresses change between visits.
- We received one aerial video for AI training. It arrived late in the term. We used it -- retrained the model, generated synthetic data, hand-labelled frames, calibrated FOV -- but we cannot know whether our detector generalises beyond that single video without further test data.

## What we built despite the constraints

Without a flyable drone for approximately two months, we created our own development path:

- A complete SITL simulation environment validating the full mission end-to-end
- A state machine covering takeoff, search, detection, centering, descent, verification, and landing
- 58 categorised test scripts (hardware, flight progression, calibration, diagnostics, experiments)
- A YOLOv8 detection model retrained on 300 synthetic + 16 real + 50 negative images (mAP50 = 0.995)
- A web-based ground station with live video stream and browser controls
- Full Raspberry Pi integration: camera, AI inference, Cube telemetry, lens calibration

We were ready in early March. The simulation framework is the only reason this project produced verifiable engineering output. We acknowledge that you provided the Raspberry Pi, screens, and keyboards -- that was genuinely helpful. But the simulation was our initiative, not something the course provided or anticipated.

## Assessment concern

The marking scheme assumes teams can demonstrate autonomous flight on real hardware. Our team has been unable to do so -- not for lack of preparation or effort, but because the hardware provided to us did not work. Two other teams had that opportunity. We did not.

We ask that this disparity be reflected in how our work is assessed. If grading penalises the absence of flight data, it penalises us for circumstances entirely outside our control.

## Specific requests

1. **A flight-ready drone, verified before we arrive.** Technical staff should confirm the hardware is functional before we travel to the farm.
2. **At least two dedicated flight sessions before submission**, with guaranteed airfield access.
3. **Written acknowledgement** that the hardware failures were not caused by our team, so that any external examiner reviewing our submission understands the context.
4. **Assessment criteria that account for the situation.** Simulation-validated systems, test coverage, and software architecture should be credited where flight data was unobtainable through no fault of the team.

## Recommendations for future cohorts

1. Verify all drones are assembled and flight-tested before allocation.
2. Provide representative aerial training data in the first two weeks.
3. Schedule backup flight slots -- three days is not sufficient when hardware failures and weather can consume all of them.
4. Document the farm network configuration and provide a stable setup.
5. Define a hardware-support escalation path with expected response times.
6. Ensure the marking scheme explicitly credits simulation-validated work.

---

We remain committed to delivering the strongest submission possible and are happy to discuss any of the above in person.

Yours sincerely,
[Team members]
MSc AENGM0074, University of Bristol

---

# PART 3: CHAT HISTORY WITH STEVE (verbatim)

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

> **Dmytro:** Do you think our blue box will be in the lab tomorrow morning? We have an iPhone cable in there.. if possible I'd like to go grab it. I'm on 8% now

> **Steve:** Yep, it should be.

### Working drone request

> **Dmytro:** Hi Steve, you mentioned you will try to get us a working drone, any luck with that? Or will we be trying our software on the green team's drone?

> **Steve:** Plan for both just now, Sid's on it but TBC

### Personal reflection report clarification

> **Dmytro:** Hi Steve, just trying to work on my personal reflection report are there anymore details somewhere that I'm missing or is that still to follow?

> **Steve:** Apologies, I have a draft update that I'll issue first thing next week.

> **Dmytro:** Great thank you

---

# PART 4: QUESTIONS REQUIRING ANSWERS

These are the specific questions that remain unresolved:

| # | Topic | Question | Status |
|---|-------|----------|--------|
| 1 | D7 structure | Has the promised draft update with D7 details been issued? | Unresolved -- Steve said "first thing next week" |
| 2 | D7 weighting | Are Teamwork, Self-management, and Insight equally weighted? | Unknown |
| 3 | D6 Specialist | Does "implemented highly effectively" require outdoor flight, or does simulation validation count? | Unknown |
| 4 | Assessment fairness | What does "taking it into account" mean in terms of marks? | Verbal only -- no written confirmation |
| 5 | Items of interest | For R05, what exactly counts? Steve said "coats, other stuff." | Partially answered |
| 6 | Appendices | The brief says appendices "will NOT be assessed" but also says "include excerpts and summaries." How should we handle this? | Unknown |

---

# PART 5: EVIDENCE SUMMARY

Key metrics to reference if needed:

| Metric | Value |
|--------|-------|
| Lines of code | 4,400+ |
| Test scripts | 58 |
| Unit test functions | 127 |
| Report pages | 198 (goldmine) |
| Flight days with working hardware | 0 (until Easter) |
| Days hardware was non-functional | ~45 |
| AI model iterations | 3 (640, 1280, 1088) |
| Training images | 3,500+ (multi-class) |
| GPS estimation accuracy | CEP50 = 2.3 m (DJI validated) |
| Requirements met in simulation | 12/12 |
| Estimated hours spent | 300+ (~3x expected) |
| SITL simulation hours | 100+ |

---

# PART 6: COMMUNICATION STRATEGY

## Guiding principles

- **Seek clarity, not sympathy.** Frame every message as "help me focus my effort" rather than "this is unfair."
- **Be specific.** Not "can you help" but "could you clarify X."
- **Acknowledge support.** Thank Steve for Easter days, Pi equipment, and effort to resolve the drone issue.
- **Create a paper trail.** Every verbal answer should be confirmed in writing.

## Phrases to use

- "I want to make sure I am focusing my effort in the right places."
- "Given the hardware situation, what would you recommend we prioritise?"
- "You mentioned you would take it into account -- could you help me understand what that means for assessment?"

## Phrases to avoid

- "It is not fair" -- sounds adversarial.
- "Other teams had it better" -- sounds like blame-shifting.
- "We deserve top marks" -- sounds presumptuous.
- "You promised" -- sounds accusatory.

## Message sequence

### Message 1 (Part 1 of this document): Comprehensive, professional

Covers all four rubric areas, asks specific questions, demonstrates effort, seeks guidance. Send Friday morning.

### Message 2 (if needed): Short follow-up

If Message 1 gets a vague reply, send a brief clarification: "Just to confirm I understand correctly -- you are saying [paraphrase]. Is that right?"

### Message 3 (last resort): Formal feedback letter

The letter in Part 2. Only send if Messages 1-2 indicate the marking will penalise us for circumstances outside our control.

---

# PART 7: RAW NOTES AND ADDITIONAL CONTEXT

## Motor wiring issue (Flight Day 2)

The drone did not fly because motor wires were connected incorrectly. This may have been done by a team member. However, the brief does not ask students to build the drone -- it assumes a working platform. Other teams received assembled, flight-tested drones.

## Simulation vs reality gap

Our simulation is complete -- all 12 requirements met in SITL. However, responsible engineering requires progressive testing (bench, passive, waypoint, autonomous), with each step building confidence before the next. We planned for this. What we got was: nothing, nothing, Easter scramble, demo day. There was no time for the gradual trust-building the course is designed around.

## Cascading effect of lost flight days

- Day 1 failure meant no outdoor calibration.
- No calibration meant no model retraining on real aerial data.
- No retraining meant no validated detection at real altitude.
- No validated detection meant no confidence in GPS estimation outdoors.
- No confidence meant no progressive testing ladder.
- Each lost day cascaded into weeks of uncertainty.
- Other teams had this data from Day 1 and iterated all term.

## Steve's commitments (for reference)

| What he said | Context | Status |
|--------------|---------|--------|
| Would take hardware situation into account in marking | After second failed flight day | Verbal only |
| Would issue D7 draft update "first thing next week" | Last message in chat | Not received |
| "Sid's on it" for getting a working drone | In response to drone request | Outcome unclear |
| Arranged Easter testing days | Proactive | Completed -- appreciated |

## Items of interest (R05)

Steve indicated "use coats, other stuff" and that the inflatable animals "were silly." Items of interest therefore appear to be everyday objects: clothing, equipment, personal effects. Our model detects the dummy (mannequin). The COCO backup model detects person, backpack, and other common objects.

## D7 personal reflection

Steve said he had a draft update to issue "first thing next week." This was the last exchange in the chat history. The brief retains the "DETAIL TO FOLLOW" yellow highlight. We have been working from the Appendix B rubric (Teamwork, Self-management, Insight) and AHEP4 standards (M5, M7, M16, M17). Current D7 score after 7 iterations: 83-84/100.

## Core concern

The difference between what we can demonstrate and what we could have demonstrated is not software quality -- it is testing depth. We have the software, the simulation, and the tests. What we lack is outdoor flight data proving it works in reality. This gap exists entirely because of hardware provision, not effort. Our simulation-validated work should be credited at the same level as outdoor-tested work from teams that had functioning hardware from the start.

---

# PART 8: ALTERNATIVE SHORT MESSAGE (if Part 1 feels too long)

> Hi Steve,
>
> Hope you are well. Just following up on our last chat -- you mentioned you had a draft update for the D7 personal reflection report with more details on what is expected. Has that been issued? I want to make sure I am not missing anything as I am working on it now.
>
> Also had a quick question about the group report -- for the top mark band, the rubric mentions technologies "implemented highly effectively." Given our hardware situation this term, would our simulation-validated work (all 12 requirements met in SITL, extensive testing, benchmarks) be credited the same as outdoor flight data? I have been putting in a significant amount of work and want to make sure I am focusing in the right areas.
>
> I know you mentioned you would take our situation into account and I appreciate that. I would just value some clarity on whether we can still achieve a strong mark given the constraints. Any guidance on what to prioritise would be very helpful.
>
> Thanks,
> Dmytro
