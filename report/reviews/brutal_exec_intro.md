# Brutal Review: Executive Summary + Introduction

**Date**: 2026-03-27
**Files**: `report/sections/exec_summary.tex`, `report/sections/intro_d6.tex`

---

## EXECUTIVE SUMMARY

### Self-containedness check

The exec summary SHOULD be readable by someone who never opens the rest of the report. Scorecard:

| Element | Present? | Notes |
|---------|----------|-------|
| What the system is | YES | SAR drone for AENGM0074 |
| Platform hardware | YES | EDU-450, Cube Orange+, Pi 5 |
| Detection model | YES | YOLOv8n / TFLite |
| Key performance numbers | YES | mAP50=0.995, 206ms, 4.8FPS, CEP50=2.3m |
| Search pattern coverage | YES | 1.1 min, 18 waypoints |
| State machine size | YES | 20 states, 32 transitions |
| Trade studies mentioned | YES | 4 MCDA |
| Testing methodology | YES | 5-tier, 71 scripts |
| Geofencing | YES | SSSI, altitude ceiling, boundaries |
| Operator-in-the-loop | YES | Verification stage, ground station |
| Landing requirement (10m) | YES | "lands within 10m" |
| What was NOT achieved | PARTIAL | "pending outdoor flight validation" is there but buried in the last sentence |
| Team size | NO | Never mentions 5 people |
| Camera type | NO | IMX296 global shutter not mentioned |
| Lens calibration numbers | YES | RMS=0.399, focal=5.46mm |
| Confidence score | YES | 0.966 mean confidence |

**Verdict**: Mostly self-contained. The biggest gap is that the reader never learns the team size or camera sensor from the exec summary alone.

### Claims that overstate what was done

1. **"The system locates a lost hiker"** (line 3) -- It does NOT. It locates a dummy in simulation and post-hoc video analysis. No autonomous outdoor flight was conducted. This sentence implies operational capability. **OVERSTATEMENT**.

2. **"The project satisfies all twelve brief requirements (R01--R12)"** (line 3) -- This is a bold claim for a system that never flew autonomously outdoors. Several requirements (e.g., "land within 10m of casualty") were only demonstrated in simulation. The requirements section presumably has caveats, but the exec summary presents this as unqualified fact. **BORDERLINE OVERSTATEMENT** -- at minimum, add "in simulation" or "with the exception of outdoor flight validation".

3. **"lands within 10m of the casualty to deploy a first-aid kit"** (line 6) -- Same issue. This was never demonstrated on real hardware. Stating it as something the drone does (present tense) is misleading.

4. **"Post-hoc analysis of DJI flight video over the test site confirmed detection across a 15--50m altitude range"** (line 15) -- This is from DJI video, not the Pi camera. The detection was done on a laptop with Ultralytics, not TFLite on the Pi. The sentence is technically true but could mislead the reader into thinking the Pi detected targets from 15-50m altitude during flight.

5. **"sufficient for the altitude-dependent search speed (8 m/s at the nominal 35 m altitude)"** (line 15) -- Where does 8 m/s and 35m come from? config.py says `SEARCH_SPEED_MPS = 5` and `TARGET_ALT = 30`. If these were changed, fine, but verify consistency with the rest of the report.

6. **"This weather-adapted session yielded quantitative calibration results that directly improved the vision pipeline for subsequent flights"** (line 18) -- "subsequent flights" implies flights happened after the bench session. Did they? If not, this is misleading. Should be "for future flights" or "for the deployed pipeline".

### Missing key numbers

- **No mention of dataset composition breakdown** in the results paragraph. The "366 mixed synthetic and real-world images" is there, but the split (300 syn + 16 real + 50 neg) would strengthen credibility.
- **No Wi-Fi range or latency** for the ground station.
- **No mention of the 5m minimum landing distance** (brief says 5-10m corridor).

### Structural / language issues

1. **Paragraph "Results achieved" is overloaded** -- It contains detection performance, inference speed, lens correction, video analysis, GPS accuracy, search pattern coverage, AND figure count. That is 7 distinct results crammed into one paragraph. Consider splitting into "Detection performance" and "System integration results".

2. **"The report contains 14 figures"** -- This is meta-information about the report itself, not a result. It feels out of place in a "Results achieved" paragraph. Either move it to the end or drop it.

3. **"pending outdoor flight validation"** is the most important caveat in the entire document and it appears as the last 4 words of the last sentence. It should be more prominent. A reader skimming the exec summary could miss it entirely.

### Suggestions

- Change "The system locates a lost hiker" to "The system is designed to locate a casualty surrogate" or similar.
- Add "in simulation" qualifier to the R01-R12 satisfaction claim, or say "verified in simulation; outdoor flight pending".
- Move the "pending outdoor flight validation" caveat earlier -- possibly its own sentence after the results paragraph.
- Verify 8 m/s and 35m altitude against config.py and the rest of the report.
- Drop or relocate the "14 figures" claim.

---

## INTRODUCTION (intro_d6.tex)

### [NAME] placeholders

**4 placeholders found** (lines 34, 37, 41, 43):
- `\textcolor{red}{[NAME]}` -- Flight Dynamics and State Machine Testing
- `\textcolor{red}{[NAME]}` -- Designated Pilot and RC Systems
- `\textcolor{red}{[NAME]}` -- Hardware Integration
- `\textcolor{red}{[NAME]}` -- Project Management and Documentation

These also appear in the contributions table (lines 62, 65, 68, 71).

**Total: 8 [NAME] placeholders that MUST be replaced before submission.**

### Decision chain check

The intro does NOT contain a "decision chain" per se. It describes:
1. The scenario (context)
2. The hardware provided
3. The company structure
4. Team roles
5. Report structure

The "decision chain" -- why we chose YOLOv8n, why lawnmower, why Pi, why browser ground station -- is deferred to Section "Design Rationale" (referenced in the report structure paragraph). This is **correct** for an intro that is excluded from the page count and serves the D6 brief's purpose (context, background, company description, member bios/roles, contributions).

However, the report structure paragraph (line 79) references sections by label (`\ref{sec:rationale}`, `\ref{sec:sysdesc}`, etc.) which is good -- the reader can follow the thread.

### Claims that overstate what was done

1. **"All development was managed through a shared GitHub repository"** (line 25) -- This implies all 5 team members actively used GitHub. If only 1-2 people committed code, this is misleading. Consider "All software development" instead of "All development".

2. **"five parallel streams---Computer Vision, Hardware Integration, Search Logic, Ground Station, and Safety/Testing"** (line 25) -- Were these truly parallel and staffed? The contributions table suggests Dmytro did CV, path planning, ground station, simulation, AND testing -- that is 4 of the 5 streams. If one person did most of the work, calling them "five parallel streams" is a stretch.

3. **Dmytro's bio** (line 32) -- Lists essentially the entire project. This is honest but politically awkward. The other 4 bios are thin by comparison. This is a team report; the contrast may raise examiner eyebrows. Consider whether some contributions could be shared more diplomatically (e.g., "with input from [NAME]").

### Structural issues

1. **Platform described twice**: Line 11 ("a Hexsoon EDU-450 hexacopter airframe, a Cube Orange+ flight controller, a Raspberry Pi 5 companion computer, and a global-shutter camera") and line 21 ("The provided platform is a Hexsoon EDU-450 hexacopter airframe equipped with a Cube Orange+ flight controller, Here 3+ GPS, Raspberry Pi 5 companion computer, and an IMX296 global-shutter camera"). The second occurrence adds GPS and camera model but is otherwise redundant. **Merge or cut one.**

2. **"Here 3+ GPS"** (line 21) -- Should this be "Here3+" or "Here 3+" with a space? Verify the official product name. (CubePilot writes it as "Here3+".)

3. **Report structure paragraph** (line 79) -- References "Sections~\ref{sec:sysdesc}--\ref{sec:groundstation}" which implies a range. If these are not consecutive section numbers, the range notation is misleading. Verify the actual section numbering.

4. **No mention of the D6 brief explicitly in the intro body** -- The comment on line 4 says "D6 brief" but the text never says "This report constitutes Deliverable 6 (D6)". The reader (examiner) knows this, but explicitly stating it would be more professional.

### Contribution table honesty check

The table is honest but lopsided:
- **Dmytro**: 4 lines of dense contributions spanning nearly every subsystem
- **Others**: 1-2 lines each, mostly support roles

This is fine if accurate, but examiners grading a GROUP project may question whether this was truly collaborative. No action needed if the team agrees, but be aware of the optics.

### Language / grammar

- **"Day-to-day coordination relied on a group chat for informal updates and weekly in-person meetings"** -- Slightly informal for a technical report. Consider "Daily coordination was conducted via..." or similar.
- **"fed into defined integration milestones"** -- Vague. Which milestones? When? This sentence promises structure but delivers none.

---

## OVERALL SEVERITY MATRIX

| Issue | Severity | Action |
|-------|----------|--------|
| 8 [NAME] placeholders in intro | **CRITICAL** | Must replace before submission |
| "System locates a lost hiker" overstatement | **HIGH** | Reword to "designed to locate a casualty surrogate" |
| R01-R12 satisfaction without "in simulation" caveat | **HIGH** | Add qualifier |
| "pending outdoor flight" buried at end | **HIGH** | Make more prominent |
| Platform described twice in intro | **MEDIUM** | Merge into one occurrence |
| 8 m/s and 35m altitude -- verify consistency | **MEDIUM** | Check against config.py and other sections |
| "subsequent flights" implies flights happened | **MEDIUM** | Change to "future flights" |
| Contribution table lopsidedness | **LOW** | Team decision, but be aware |
| "14 figures" in results paragraph | **LOW** | Relocate or remove |
| DJI video analysis framing | **LOW** | Clarify it was laptop-based post-hoc analysis |

---

## BOTTOM LINE

The exec summary is well-written and hits most key numbers, but **overstates readiness** by using present tense for capabilities only demonstrated in simulation. The single most important fix is making "no outdoor autonomous flight was achieved" unmissable rather than a buried afterthought.

The introduction is solid for its purpose (D6 context + team bios) but has **8 [NAME] placeholders** that are a submission blocker, and **duplicates the platform description**. The contribution split is honest but visually lopsided -- a team decision on whether to rebalance.
