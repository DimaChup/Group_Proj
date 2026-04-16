# Context Extracted from Git History & Project Files

## Commit Statistics

### Commit Volume by Author
- **Apollo (Dmytro)**: 799 commits
- **Dima (Dmytro, separate account)**: 8 commits (early Pi work: calibration data, benchmark results, pienv freeze)
- **No other team members have commits in this repository.**

This means Dmytro authored 100% of the codebase commits. The 8 "Dima" commits were made directly on the Pi during field testing (saving calibration data, benchmark results).

### Commit Pattern
- Earliest commits (Feb 2026): single-letter messages ("d", "srg") -- rapid prototyping phase
- Mid-project: detailed commit messages with version tracking ("D6 goldmine v8", "D6 goldmine v19")
- Late project: highly structured ("Reportflow v5: exec summary rewrite, structure review, body split, V3 scoring 89.7")
- Report iterations dominate recent history: D6 went through 19+ versions, D7 through 4+ versions
- ~50+ agents deployed for report scoring and improvement

---

## Team Members & Roles (pieced from GROUP_STATUS.md + brain-dump + commits)

| Name | Role | Evidence of Contribution |
|------|------|--------------------------|
| **Dmytro (Apollo)** | CV/Software Lead | 799 commits, all code, all reports, all docs, all test scripts |
| **Robin** | Flight Dynamics / State Machine / Pilot | Separate state machine (not in this repo). Dmytro built passive_watch integration for Robin's system. Robin flew RC during field tests. |
| **Harish** | Hardware + Communications | Named in CONTEXT_FROM_DOCS.md. No commits in repo. |
| **Edward** | CV model training (shared) | Named in CONTEXT_FROM_DOCS.md. No commits in repo. |
| **Zian** | Path planning | Contributed spiral search pattern idea (commit 4668c4b: "Add Zian's perimeter spiral as 3rd pattern option"). Directory "Zian" exists (untracked). No commits. |

### Key Observation
GROUP_STATUS.md has empty role assignments for Pilot, Hardware, and PM/Report -- only "Dima" and "Robin" have names filled in. The Meeting Notes section is entirely empty (template only). The Group Decisions Log is blank. This suggests meetings were informal/chat-based, not documented.

---

## Team Dynamics Evidence

### Robin Integration (the clearest collaboration thread)
Commits show a specific integration pattern between Dmytro and Robin:
1. `885cee4` -- "Passive_watch docs restructured for Robin: exact command, JSON format, parsing"
2. `87e386d` -- "docs/PASSIVE_WATCH_USAGE.md: comprehensive passive_watch documentation"
3. `24783d9` -- "CHECKLIST: clarify our role = passive_watch providing GPS to Robin's state machine"
4. `a5b1ab7` -- "passive_watch_2.py: Robin integration (--robin flag, cv_mode polling, 2-image output)"

The architecture: Dmytro's CV system (passive_watch.py) detects targets and writes GPS coordinates + images to a directory. Robin's state machine (in a separate repo/system) reads from that directory. This is a clean API boundary -- they agreed on a file-based interface.

From CHECKLIST.md: "Our role: detect targets + provide precise GPS coordinates to Robin's state machine." and "Robin's state machine reads from this directory to get target positions."

### Zian's Contribution
- Zian proposed a perimeter spiral search pattern as an alternative to the lawnmower
- Dmytro implemented it (commits fc2ac17, 83e0cfe, 4668c4b) as a selectable option
- Pattern comparison tool built to evaluate lawnmower vs spiral quantitatively

### Presentation / FDR
- Dmytro prepared 2 presentation slides specifically labeled "for Demetro" (his name)
- Commits: `32fb0c5` "FDR presentation slides HTML: 2 full-screen slides for Demetro"
- `b2a9cd4` "FDR presentation: Demetro's 2 slides with full speaking scripts"
- Built teleprompter with speaking scripts (465 words, 3.1 min total)
- Later: native PPTX build "matching team style" -- suggesting other team members had slides too

---

## Hardware Crisis Timeline (from STEVE_CONTEXT.md + commits)

| Date | Event | Outcome |
|------|-------|---------|
| ~12 March | Flight Day 1 | Drone hardware not functional. Dmytro had printed checklists, 40+ scripts ready. Weather also poor. |
| ~19 March | Flight Day 2 | Drone didn't take off -- GPS, joint issues. Again fully prepared, again wasted. |
| 30 March | Easter Day 1 (holiday) | Steve arranged extra days. Bench testing: Pi + Cube + camera working. |
| 31 March | Easter Day 2 (holiday) | FOV calibration, lens calibration, benchmarks. First real hardware data. |
| Demo Day | Demonstration | Industry guests + presentation -- not a real testing day. |

**Key facts:**
- Team received non-functional drone while other two teams had working hardware from the start
- Drone wasn't assembled for first several weeks (missing servo)
- 0 successful flights across all scheduled days
- Dmytro travelled back to Bristol during Easter holiday specifically for testing
- "Easter days shouldn't count -- it's a holiday"

### Steve Communication
From verbatim chat logs in STEVE_CONTEXT.md:
- **Dmytro proactive**: Asked to come 30min early to set up, prepared experiments, asked about detection objects
- **Steve non-committal**: "Plan for both just now, Sid's on it but TBC" (re: getting a working drone)
- **Broken promise**: Steve said he'd issue D7 draft update "first thing next week" -- it was never issued (brief still says "DETAIL TO FOLLOW")
- **Assessment assurance**: Steve said he would "take into account" the hardware situation and it would be "reflected in assessment"

### Emotional Context (from complaint documents)
- "It just doesn't seem like a priority to you" (directed at course staff)
- "Very disheartening", "Weeks wasted going in circles"
- "We were building blind -- simulation said it works, but real world is different"
- Couldn't verify software foundations until 6 weeks after first scheduled flight
- Formal complaint letter drafted (STEVE_COMPLETE.md) but framed as "seeking guidance, not lodging a complaint"

---

## Collaboration Friction Points

### LL-01: Mode-Fighting Crash (from LESSONS_LEARNED.md)
"A colleague's drone crashed because the onboard software kept switching the flight mode to GUIDED while the pilot's RC transmitter was set to LOITER." This was a teammate's code, not Dmytro's. Dmytro's response: built an RC Override Guard in main.py that prevents ALL commands when the pilot takes control. This is evidence of learning from a teammate's mistake and implementing a systematic fix.

### Integration Architecture
The file-based interface between passive_watch (Dmytro) and Robin's state machine suggests the teams worked somewhat independently. Dmytro built comprehensive documentation for Robin:
- PASSIVE_WATCH_USAGE.md
- CHECKLIST.md with "Robin's" sections
- --robin flag in passive_watch_2.py
- JSON output format specification

This is professional integration work, but also suggests the two subsystems were developed in parallel with limited real-time collaboration.

### Conflict Evidence
- CHECKLIST.md warns: "If Robin/Zian run their OWN mavproxy: two mavproxy on the same serial port will NOT work" -- suggests potential resource conflicts during field testing
- Port conflict management documented extensively (passive_watch on 8090, main.py would need different port)
- Camera conflict: "passive_watch and main.py CANNOT run simultaneously" -- hardware sharing constraints

---

## What Dmytro Built (scope of individual contribution)

### Code (all in this repo, all by Dmytro)
- main.py -- full autonomous mission state machine (908 lines, refactored to 754)
- simple_simulator.py -- interactive MVP (2508 lines)
- pi_flight.py -- web ground station (1097 lines)
- passive_watch.py -- passive observer (752 lines)
- vision.py -- dual-backend CV system
- planning.py -- search pattern generator (lawnmower + spiral)
- config.py, states.py, utils.py -- core infrastructure
- 58 test scripts across 6 categories
- 146 pytest unit tests
- generate_dataset_v2.py, generate_dataset_v3.py -- training data pipelines
- tools/label_tool.py, tools/fov_calibrate_video.py -- analysis tools

### Reports (all by Dmytro with Claude assistance)
- D6 "Goldmine" report: 198+ pages, 35 appendices, 19 versions (74 -> 85.2 score)
- D6 "Reportflow" report: 40 pages, 5 versions (81 -> 87.2+ score)
- D7 individual reflection: 4 versions (68 -> 83-84 score)
- CV standalone report: 998 lines, 10 sections
- ~16 new documentation files in docs/

### Documentation
- CLAUDE.md (650+ lines, single source of truth)
- 4 blueprints for large files
- FLIGHT_DAY_CHECKLIST.md, FLIGHT_DAY_TESTS.md
- STEVE_CONTEXT.md, STEVE_COMPLETE.md (complaint/communication strategy)
- LESSONS_LEARNED.md (8 engineering lessons)
- 35+ documentation files total

---

## Key Narrative Threads for D7

### 1. Preparedness vs Hardware Failure
Dmytro was exceptionally prepared (40+ scripts, printed checklists, progressive test plan) but couldn't execute because the hardware was broken. This is a story about external constraints, resilience, and adaptation -- shifting to simulation-first development when the physical platform was unavailable.

### 2. Lone Wolf vs Team Integration
799/807 commits are Dmytro's. He built essentially the entire software system. But he also built integration points for Robin (passive_watch API, documentation, --robin flag) and incorporated Zian's ideas (spiral pattern). The question is whether this represents exceptional initiative or a team that wasn't pulling equal weight.

### 3. Communication with Authority
The Steve correspondence shows professional escalation: starting with questions, then seeking clarity, then formal feedback. The tone is always respectful and evidence-based, never emotional (despite clear frustration in internal documents).

### 4. Simulation as Adaptation
When hardware failed, Dmytro built a complete simulation environment as a proxy. This is a genuine engineering adaptation -- not just making do, but creating an alternative validation pathway. The DJI video analysis pipeline, synthetic data generation, and attitude-compensated GPS estimation all emerged from this constraint.

### 5. Engineering Depth vs Breadth
The commit history shows Dmytro going extremely deep: 19 versions of the D6 report, 1440-test tilt compensation verification, 4.5x inference speedup discovery, literature-grade GPS estimation on a 60-pound platform. This depth came at the cost of relying on teammates for breadth (Robin for flight dynamics, Zian for alternative patterns).

### 6. Easter Sacrifice
Working during Easter holiday to test hardware that should have been available weeks earlier. This is concrete evidence of commitment beyond expectations.

---

## Gaps / What's Missing from Git

1. **No meeting minutes or decision logs in the repo** -- GROUP_STATUS.md template is blank
2. **No commits from Robin, Harish, Edward, or Zian** -- their work is in separate repos or not version-controlled
3. **Robin's state machine code is not in this repository** -- integration was via file interface
4. **No WhatsApp/chat logs archived** (mentioned in brain-dump: "Look at GP2 folder images -- team WhatsApp chat with Robin's handwritten flight day plans")
5. **No explicit record of task allocation meetings** -- roles were apparently informal
6. **brain-dump.md references "Robin has state machine flow: IDLE -> Setup Mission -> PRE_AUTO_CHECK -> Generate Pattern -> SEARCH (Phase 1, Phase 2)" but this code is external**
