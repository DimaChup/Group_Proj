# Context Extracted from Project Documentation

## Team Composition & Roles (from GROUP_STATUS.md)
- **Dmytro (Apollo)**: CV/Software Lead — Pi code, AI detection, simulator, ground station
- **Robin**: Flight Dynamics, Pilot (RC flying), Hardware (frame assembly), PM/Report writing
- **Harish**: Hardware + communications
- **Edward**: CV model training (shared with Apollo)
- **Zian**: Path planning

## Hardware Crisis (from COMPLAINT_LETTER.md + STEVE_CONTEXT.md)
- Team received non-functional drone while other two teams had working hardware
- 0 successful flights out of 3 scheduled flight days (practice 1 + 2 failed)
- Drone wasn't assembled for first several weeks (missing servo)
- Failures discovered ON flight days, not before
- No pre-flight verification by technical staff
- Other teams' hardware worked from day one
- Team escalated to formal complaint letter to Steve (course organiser)

## Emotional Context (from COMPLAINT_DRAFT.md)
- "It just doesn't seem like a priority to you" (directed at course staff)
- Repeated broken promises: Steve said hardware would be fixed after Flight Day 2 — it wasn't
- Easter sacrifice: team worked during holiday break when hardware finally became available
- Couldn't verify if software actually works until Easter (~6 weeks after first scheduled flight)
- "Very disheartening", "Weeks wasted going in circles"

## Team Preparation (contrast with hardware failure)
- Printed flight checklists ready before Day 1
- 40+ test scripts developed in advance
- Progressive test plan validated in simulation
- 5-step structured approach (bench → passive → waypoint → autonomous)
- FOV and lens calibration completed during Easter break

## What Was Built Despite Crisis
- 4,400+ lines of code across 11 modules
- 58 test scripts across 6 categories
- 3 AI model generations with mAP50 = 0.995
- 366-image training dataset
- GPS target estimation with attitude compensation, CEP50 = 2.3m
- 198-page report with 35 appendices
- Complete simulation with all 12 requirements verified

## 8 Lessons Learned (from LESSONS_LEARNED.md)
- LL-01: Flight mode fighting (GUIDED/LOITER oscillation)
- LL-02: Camera color correction (BGR issue)
- LL-03: TFLite coordinate system (pixel vs normalized)
- LL-04: Calibration file corruption
- LL-05: GPS timing lag
- LL-06: DISARM_DELAY parameter
- LL-07: Python 3.13 compatibility
- LL-08: Geofence sign conventions

## Communication with Steve (from STEVE_CONTEXT.md)
- Dmytro proactive: asking clarifying questions, preparing
- Steve non-committal: "Plan for both just now, Sid's on it but TBC"
- Promises not delivered: Steve said he'd issue draft D7 update "first thing next week"
- Tone in complaints: respectful escalation, factual, not accusatory
