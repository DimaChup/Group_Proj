# Complaint — AENGM0074 Drone Hardware & Flight Day Issues

**To:** Course organiser / Steve
**From:** Blue Team
**Date:** 2026-03-30
**Re:** Inadequate hardware provision and insufficient flight testing opportunities

---

## Raw Context (to be refined into formal letter)

### The Setup

- AENGM0074 MSc group project — autonomous SAR drone
- 3 teams total, each provided with a drone
- Our job: develop the **software** (autonomous search, AI detection, payload deploy, ground station)
- We were **supposed to be provided with a working drone** — hardware is not our responsibility
- The other two teams' drones worked. Ours didn't.

### Flight Opportunities

| Date | What | Outcome |
|------|------|---------|
| ~12 March | Flight Day 1 | Weather cancelled / drone hardware didn't work |
| ~19 March | Flight Day 2 | Drone didn't take off — hardware issues (GPS 2, joints) |
| 12 April | Demo Day | Not marked, industry guests, presentation — not a real testing day |
| 30 April | Extra day 1 (Easter) | Steve found extra days — but this is Easter holiday |
| 31 April | Extra day 2 (Easter) | Same — shouldn't need to test during holidays |

**Total real flight opportunities: 2. Both failed due to hardware. Not our fault.**

### Core Grievances

1. **We were given a broken drone.** The other two teams' drones were built properly and their hardware worked. Ours didn't take off on either flight day. This is not a software problem — our software is simulation-proven and ready.

2. **Flight days wasted on hardware debugging.** The person who built/provided the drones should have tested them BEFORE the flight days. Those flight days should be for US to test our SOFTWARE. Instead, twice now, we discovered on the flight day itself that the drone doesn't work.

3. **Only 2 opportunities to fly.** For a course that requires autonomous drone flight, 2 flight days is already very tight. Losing both to hardware failures leaves us with zero real-world data.

4. **Extra days are during Easter holiday.** Steve found 2 more days (30-31 April) which is appreciated, but these are during Easter break. Students shouldn't have to give up their holiday to compensate for hardware that should have been working from day one.

5. **Assessment impact.** We have no real-world flight data to show. Our entire assessment relies on demonstrating the system works on real hardware, but we've never had working hardware to test on.

### What Our Team Has Done (despite hardware failures)

- Complete autonomous mission working in simulation (search, detect, descend, deploy, return)
- AI detection system with 3 backends (Ultralytics, TFLite, NCNN)
- Pi 5 integration: camera, Cube connection, benchmarks all verified
- Web-based ground station with live video stream
- 40+ test scripts covering every component
- Progressive flight test methodology (bench → passive → waypoint → autonomous)
- Retrained YOLOv8n model on real + synthetic data (mAP50 = 0.995)
- We arrived at BOTH flight days fully prepared with tested software

### Inadequate Flight Opportunities

6. **3 flight days is not enough.** Even if the hardware worked, 3 days (including a demo day) is nowhere near enough to develop, test, iterate, and showcase an autonomous drone system. Easter days should NOT count — that's a holiday.

7. **"Not enough staff" is not acceptable.** The cohort pays hundreds of thousands in tuition collectively. You're telling us it's not possible to find one person to supervise us at the farm so we can test our hardware? We're paying for this education.

8. **Weeks wasted without hardware feedback.** We don't know what's wrong, we might be going in the wrong direction. We built our own SITL simulation to keep pushing the project forward — but we shouldn't HAVE to. The course assumes working hardware. What if we hadn't built that simulation? We'd have nothing.

9. **Grade ceiling imposed by hardware failures.** Could a student realistically get 90%+ on this course? It's ambitious but fair to ask. The grade now entirely depends on working hardware showing up on Easter holiday. If the hardware is our responsibility to build, fine — but it's not. The course brief says we plan the mission. The whole unit assumes a working drone.

### The Irony

10. **We were told to "come prepared."** Steve made comments about teams being ready, little jokes about preparedness. But it's the hardware provision that wasn't prepared. The drones should have been built, tested, and verified BEFORE being handed to teams. Not tested for the first time on our precious flight days.

11. **Promises to fix weren't kept.** After each failed flight day, we were told the hardware issues would be mitigated and fixed. They weren't. We arrived at the next flight day to the same problems.

### What We Need

1. A drone that actually flies
2. Acknowledgement that delays are hardware-provision failures, not our team's shortcoming
3. Fair assessment consideration given circumstances beyond our control
4. Guarantee that the Easter flight days will have working hardware — tested BEFORE we arrive
5. More supervised flight days — not during holidays
6. Recognition that 3 days was never enough for a course requiring real autonomous flight

---

## Raw Details (from user, March 30)

### Steve's assurance after Flight Day 2
- User asked directly: "Our hardware doesn't work, are you going to make sure it does?"
- Steve said yes, just like that, casually
- Come 30 April (Easter) — hardware STILL doesn't work
- Now told to "build it yourselves" — but course brief never said that

### Mitigation offer: fly on other team's drone
- Steve suggested asking another team to "kindly let you use their drone"
- This shouldn't be the plan — why is OUR drone not working?
- Problem: team spent weeks configuring their Pi environment, benchmarks, calibration
- Swapping hardware mid-project is not trivial — undermines all that setup work
- And the other hardware still didn't work properly either

### Drone not even assembled properly
- Other two teams got fully assembled drones
- Ours wasn't assembled for weeks
- Missing servo — took ages to be provided. Why wasn't it there from day one?
- Team spent weeks not knowing if problems were hardware or software
- That ambiguity wasted enormous development time
- "It just doesn't seem like a priority to you"

### Farm logistics issues
- Can't get GPS lock indoors — need farm access for even basic testing
- Shared Wi-Fi router at farm conflicts: people indoors on drones vs people flying outdoors
- Outdoor flying takes priority → indoor teams can't use router properly
- IP addresses keep changing (Sid changes them?) → constant re-login, re-configuration
- These eat into already scarce farm time

### Industry demo day (12 April)
- Ambitious: invite industry partners to see student work
- But ambition not matched by support — can't demo real flight without real testing
- Feels performative without the infrastructure to back it up

### Course brief point (KEY)
- Course brief says: plan the mission. Assumes working drone provided.
- Students were NOT told to build the drone
- Took weeks to figure out why things weren't working (GPS, hardware faults)
- That debugging time should never have been the students' problem

### Blame misdirection
- Tone from Steve feels like it's our fault things aren't working
- "We need to figure out why it's not working" — but we weren't told to build the hardware
- Don't have opportunities to play with hardware, can't troubleshoot what we didn't build
- Sharing another team's drone: limited time, risk of messing up their setup, disheartening
- "A lot of people will agree — it's been very poorly run"

### Development blocked since first flight day (~early March)
- Can't build on top of something that might not work
- Can't iterate on failures or successes without flights
- Without simulation (which WE built), there's not much we could have done for nearly 2 months
- Did everything possible in labs: camera, benchmarks, Pi config, lens calibration
- But there's only so far you can push without real flight data

### Training data provided late
- Got ONE aerial video from Sid only a few weeks ago
- Retrained model on it + synthetic data, but don't know if it'll work on real dummy
- Could be overtrained on that single video
- Proper aerial imagery from different altitudes/conditions should have been available much earlier
- No way to collect our own without a flying drone

### Course structure criticism
- "Very interesting and ambitious" course — would have been great if run properly
- Not enough effort to accommodate students
- Fair enough: bought Pi, screens, keyboards — useful for Pi work
- But apart from that, it's the course that hasn't been ready, not us
- "You're the one not prepared for flight day, not us"
- Not mitigating unforeseen circumstances properly
- Should be learning, iterating, playing with hardware — that's the whole point
- Every opportunity missed: flight day 1 failed, flight day 2 failed
- Can't make improvements because we don't know what works

### Emotional context
- Team is stressed and frustrated
- Weeks wasted going in circles
- "He keeps saying he'll mitigate but doesn't take it seriously enough"
- "It should have been done by now"
- "Very disheartening"

---

*Raw notes preserved. Formal letter at COMPLAINT_LETTER.md*
