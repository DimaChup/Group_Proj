# Group Project Status Tracker

> What the group has discussed, decided, and where everyone is at.
> Dima maintains this in parallel to his own development work.
> Update after every group meeting, chat, or significant decision.

---

## Team Members & Roles

| Name | Role | Focus Area | Contact |
|------|------|-----------|---------|
| Dima | CV / Software Lead | Pi code, AI detection, simulator, ground station | - |
| Robin | Flight Dynamics | State machine, main.py testing, flight parameters | - |
| | Pilot | RC flying, kill switch, manual override | - |
| | Hardware | Frame assembly, wiring, Cube setup | - |
| | PM / Report | Project management, report writing, deliverables | - |

*Fill in names as confirmed.*

---

## Group Decisions Log

> Record every decision with date, who was involved, and what was decided.
> This prevents "I thought we agreed..." confusion.

| Date | Decision | Who | Notes |
|------|----------|-----|-------|
| | | | |

*Example:*
*| 2026-03-01 | Use 7.5m offset landing, not direct overhead | Dima, Robin | Safety — propwash risk to casualty |*

---

## Meeting Notes

### Meeting: [DATE]
**Attendees:**
**Duration:**
**Key points:**
-
-
-

**Action items:**
- [ ] [Who] — [What] — [By when]
- [ ] [Who] — [What] — [By when]

**Next meeting:**

---

## What Each Person Needs To Do (Current Sprint)

### Dima
- [ ] Push latest code to MainOne5
- [ ] Export COCO model as TFLite fallback (P2)
- [ ] FOV calibration on bench (P11b)
- [ ] Prepare multiple vision models (P15)
- [ ] Test pi_passive_flight.py in simulation (P3)

### Robin
- [ ] Test main.py state machine in simulation (P5)
- [ ] Test bench_mission.py on Pi (P6)
- [ ] Understand flight modes (GUIDED, LOITER, STABILIZE, LAND)

### Pilot
- [ ] Configure RC kill switch (P7)
- [ ] Practice STABILIZE mode in simulation
- [ ] Know the abort procedure (flip switch → STABILIZE → land manually)

### Hardware Lead
- [ ] Verify all wiring (TELEM2, CAN2, RCIN, camera CSI)
- [ ] Mount Pi + camera securely on frame
- [ ] Compass calibration (D14)

### PM / Report
- [ ] Book flight slot at Fenswood Farm
- [ ] Risk assessment paperwork
- [ ] Pre-measure search area GPS coords (P10)
- [ ] Prepare data recording sheets (P12)

---

## What The Group Has Discussed So Far

> Chronological summary of group discussions. Add new entries at the top.

### [DATE] — [Topic]
**Summary:**

**Outcome:**

---

## Blockers & Dependencies

| Blocker | Owned By | Blocks | Status |
|---------|----------|--------|--------|
| No flight slot booked | PM | All flight testing | ? |
| RC controller not configured | Pilot | Kill switch test, all flights | todo |
| COCO model not exported | Dima | Model swap fallback | todo |
| Pienv may need recreating | Dima | All Pi testing | todo |

---

## What Dima Is Doing In Parallel

> Context for the group: Dima's development work that runs ahead of group coordination.

**Completed (ready for group to use):**
- Full simulator with multi-target, GPS estimation, classification (simple_simulator.py)
- Web ground station for real flights (pi_flight.py)
- Passive flight script — zero risk, logs everything (tests/flight/passive_flight.py)
- Waypoint test script (tests/flight/waypoint_test.py)
- Dashboard with flight day prep, hardware inventory, WBS (dashboard/)
- Pi hardware tested: camera, TFLite inference, Cube connection, buzzer
- BGR camera color fix applied and verified
- All test scripts categorized in tests/ (hardware/, flight/, diagnostics/, calibration/, laptop/)

**In progress:**
- Vision model variants for flight day comparison
- FOV calibration (can do on bench before flight day)

**Waiting on group:**
- Flight slot booking
- RC controller setup and kill switch configuration
- Outdoor GPS test (needs field trip)
- Agreement on search area location and size

---

## Flight Day Readiness Checklist (Group Level)

| Item | Status | Owner |
|------|--------|-------|
| Flight slot booked | ? | PM |
| Risk assessment submitted | ? | PM |
| All code pushed and pulled on Pi | todo | Dima |
| RC configured + kill switch tested | todo | Pilot |
| All batteries charged | todo | Hardware |
| Dummy printed (A1/A0 size) | ? | ? |
| Search area GPS coords measured | todo | Dima/PM |
| Everyone knows abort procedure | todo | All |
| Everyone has read FLIGHT_DAY_CHECKLIST.md | todo | All |
| Transport arranged | ? | ? |

---

## Communication Channels

| Channel | Purpose |
|---------|---------|
| | Group chat (day-to-day) |
| | Meetings (weekly?) |
| GitHub Issues | Bug reports, feature requests |
| This document | Status tracking, decisions, blockers |
