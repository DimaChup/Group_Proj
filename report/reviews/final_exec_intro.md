# Brutal Review: Executive Summary + Introduction

**Date:** 2026-03-27
**Files:** `report/sections/exec_summary.tex`, `report/sections/intro_d6.tex`

---

## EXECUTIVE SUMMARY

### Self-Containment (1-page test)

The exec summary is a single continuous block (no `\section`, no page breaks). At roughly 19 lines of dense LaTeX prose with 5 `\paragraph{}` headings, it will render to approximately **1 full page** in a two-column IEEE-style layout, or possibly **1.2 pages** in single-column with 11pt font. **Verdict: borderline.** If using single-column 12pt, the "Demonstration and weather adaptation" paragraph may push onto page 2. Recommend measuring the compiled PDF and trimming the last paragraph if needed.

### Key Numbers Present

| Number | Present? | Value |
|--------|----------|-------|
| mAP50 | YES | 0.995 |
| Inference speed | YES | 206 ms / 4.8 FPS |
| Lens distortion overhead | YES | 1.5 ms |
| CEP50 | YES | 2.3 m |
| Number of states | YES | 20 states, 32 transitions |
| Search pattern coverage time | YES | ~1.1 min, 18 waypoints |
| Training data size | YES | 366 images |
| Camera resolution | YES | 1456x1088 |
| Altitude range tested | YES | 15-50 m |
| Bench detection confidence | YES | 0.966 mean, 50 frames |
| Lens calibration RMS | YES | 0.399 |
| FOV / focal length | YES | 5.46 mm |
| Number of test scripts | YES | 58 |
| Number of figures in report | YES | 14 |
| Number of requirements satisfied | YES | R01-R12 (all 12) |
| Search speed | YES | 8 m/s at 35 m altitude |
| Number of MCDA trade studies | YES | 4 |

**Missing numbers:**
- Total lines of code / total Python files (shows project scale)
- Flight endurance / battery estimate (readers want to know if the mission fits in one battery)
- Total development time or person-hours (optional but impressive if large)
- Weight of payload / total takeoff weight (hardware context)
- Wi-Fi range of ground station link

### Content Issues

1. **"20 states" claim** -- The `states.py` enum and state machine documentation throughout the project mention varying numbers. The CLAUDE.md lists: INIT, CONNECTING, ARMING, TAKEOFF, SEARCH, CENTERING, DESCENDING, VERIFY, APPROACH, LANDING, DONE = 11 states. If there are truly 20, verify this matches the actual code. If the state machine was expanded for the report, make sure the number is consistent across exec summary, system description, and state machine sections. **This is a factual accuracy risk.**

2. **"14 figures" is fragile** -- If any section adds or removes a figure before submission, this number breaks. Either remove it or verify at the very end.

3. **No mention of the 15-page limit** -- The comment says "excluded from D6 page count" but never states this is an executive summary explicitly (no `\section*{Executive Summary}` heading visible). The reader needs to see the heading.

4. **"deployed a first-aid kit"** -- The mission objective says "lands within 10 m... to deploy a first-aid kit." Was a first-aid kit deployment mechanism actually built? The CLAUDE.md mentions a "first-aid release mechanism" in the hardware member's role but never confirms it works. If this is aspirational, say "to enable deployment of" or "to mark the location for."

5. **Weather adaptation paragraph is defensive** -- It reads like an excuse. Reframe: "Hardware integration was validated on the assembled airframe during an on-site field day, producing lens calibration data (RMS = 0.399), FOV characterisation, and inference benchmarks confirming 100% detection at 0.966 mean confidence. The complete mission pipeline was exercised end-to-end in SITL simulation." Cut the weather explanation or reduce it to one clause. Assessors want results, not apologies.

6. **"consumer-grade hardware and open-source software"** -- Good framing for broader impact. Keep.

7. **"pending outdoor flight validation"** -- Honest but weak as a closing line. End on the capability, not the gap. Something like: "...providing a flight-ready autonomous SAR capability validated through progressive bench and simulation testing."

### Style Issues

- "subject to geofencing constraints including" -- wordy. Try "respecting geofence constraints: an SSSI no-fly zone, 50 m ceiling, and defined flight boundaries."
- "inverse-variance-weighted spatial clustering" -- correct technical term but dense for an exec summary. Consider whether all readers will parse this.
- The sentence starting "A browser-based ground station streams..." is 42 words. Split it.

---

## INTRODUCTION (intro_d6.tex)

### Required Elements Checklist

| Element | Present? | Notes |
|---------|----------|-------|
| Context/background | YES | Fenswood scenario, well written |
| Hexsoon EDU-450 mention | YES | Lines 11, 21 |
| Cube Orange+ | YES | Lines 11, 21 |
| Raspberry Pi 5 | YES | Lines 11, 21 |
| Global-shutter camera | YES | Line 11, 21 (IMX296 named in line 21) |
| Here 3+ GPS | YES | Line 21 |
| GitHub link | YES | Line 25, footnote with URL |
| MIT licence | YES | Lines 21, 25 |
| Team bios | YES | Lines 31-44 |
| Member contributions table | YES | Lines 50-75 |
| Report structure | YES | Lines 77-79 |
| Company description | YES | Lines 23-27 |

### [NAME] Placeholders

**4 placeholders found**, all clearly marked with `\textcolor{red}{[NAME]}`:
- Line 34: Flight Dynamics and State Machine Testing
- Line 37: Designated Pilot and RC Systems
- Line 40: Hardware Integration
- Line 43: Project Management and Documentation

These appear in both the bio paragraphs AND the contributions table (lines 62, 65, 68, 71). **Total: 8 instances of `[NAME]` that must be replaced before submission.**

### Content Issues

1. **Hardware listed TWICE** -- Line 11 lists "Hexsoon EDU-450 hexacopter airframe, a Cube Orange+ flight controller, a Raspberry Pi 5 companion computer, and a global-shutter camera." Line 21 lists almost identically: "Hexsoon EDU-450 hexacopter airframe equipped with a Cube Orange+ flight controller, Here 3+ GPS, Raspberry Pi 5 companion computer, and an IMX296 global-shutter camera." This is redundant. Keep the detailed version in line 21 and shorten line 11 to "identical hardware" or "a standard platform" with a forward reference.

2. **Dmytro's bio is 4x longer than everyone else's** -- His bio is 5 lines of dense technical detail. The other four are 2-3 lines each. This imbalance screams "one person did everything." Whether true or not, it looks bad in a group project report. Options:
   - Trim Dmytro's to match the others (move technical detail to system description sections)
   - Expand the others with more specific technical contributions
   - The current version risks the assessor questioning whether this was truly a group effort

3. **Contribution table mirrors bios exactly** -- The table repeats almost verbatim what the bios say. Either make the table more granular (add specific deliverables, hours, or percentages) or cut the table and keep just the bios. Redundancy wastes the reader's time.

4. **"agile, workstream-based methodology"** -- Calling it "agile" without sprints, standups, or retrospectives is a stretch. "Workstream-based methodology with defined integration milestones" is more honest and still sounds good.

5. **Report structure paragraph references sections that must match actual LaTeX labels:**
   - `\ref{sec:rationale}` -- verify exists
   - `\ref{sec:sysdesc}` -- verify exists
   - `\ref{sec:groundstation}` -- verify exists
   - `\ref{sec:testing}` -- verify exists
   - `\ref{sec:requirements}` -- verify exists
   - `\ref{sec:evaluation}` -- verify exists
   If any label is wrong, you get "??" in the compiled PDF. **Check every `\ref` compiles.**

6. **"Sections~\ref{sec:sysdesc}--\ref{sec:groundstation}"** -- This implies a continuous range of sections. If they are not consecutively numbered (e.g., if testing or requirements fall between them), this is misleading.

7. **No mention of the 50 m altitude ceiling** -- The itemized list mentions SSSI no-fly zone but not the altitude ceiling. It's in the exec summary but should also be here since this is where requirements are introduced.

8. **PLB / Focus Area** -- Good scenario framing. But it's never mentioned again in the report (presumably). If the system doesn't actually use PLB data as input, don't imply it does. The current wording is fine -- it says "narrowing the probable location" which is just context.

### Style Issues

- Line 9: "At some point during the search the hiker activates a Personal Locator Beacon (PLB)" -- missing comma after "search."
- Line 21: The sentence is 52 words. Break it up.
- Line 25: "Our company was formed" -- passive. "We formed our company" or "The team formed" is more active.
- Line 27: "Day-to-day coordination relied on a group chat" -- this is honest but sounds informal for an academic report. "Daily coordination used a dedicated messaging channel" sounds marginally more professional. Or just keep it -- honesty is good.

---

## CROSS-CONSISTENCY: Exec Summary vs Introduction

| Claim | Exec Summary | Introduction | Match? |
|-------|-------------|--------------|--------|
| Platform | Hexsoon EDU-450 hexacopter | Hexsoon EDU-450 hexacopter | YES |
| Autopilot | Cube Orange+ | Cube Orange+ | YES |
| Companion | Raspberry Pi 5 | Raspberry Pi 5 | YES |
| Camera | not named | IMX296 global-shutter | OK (exec doesn't need model) |
| GPS | not mentioned | Here 3+ GPS | MINOR GAP in exec |
| Requirements | R01-R12 | R01-R12 implied | YES |
| Licence | MIT | MIT | YES |
| GitHub | not linked | footnote with URL | OK (exec doesn't need URL) |
| States | 20 states, 32 transitions | not mentioned | OK |
| MCDA | 4 trade studies | not mentioned | OK |
| Landing distance | within 10 m | within 10 m, no closer than 5 m | DISCREPANCY -- exec omits the 5 m minimum |

**Fix the 5 m minimum in exec summary** -- the brief requirement is 5-10 m, not just "within 10 m."

---

## PRIORITY FIXES (ordered by impact)

### CRITICAL (must fix before submission)

1. **Replace all 8 `[NAME]` placeholders** with real names
2. **Verify "20 states" claim** matches actual `states.py` enum -- if wrong, assessor loses trust in all numbers
3. **Fix landing distance in exec summary**: "within 10 m" should be "between 5 and 10 m" per brief
4. **Check all `\ref{}` labels compile** -- undefined references produce "??" in PDF

### HIGH (strongly recommended)

5. **Trim weather-apology paragraph** in exec summary -- reframe as results achieved, not excuses
6. **Balance team member bios** -- Dmytro's bio dwarfs others; redistribute detail or equalize length
7. **Remove duplicate hardware listing** in intro (lines 11 vs 21)
8. **Verify "14 figures" count** matches final compiled PDF
9. **Add altitude ceiling (50 m)** to intro's requirement list

### MEDIUM (polish)

10. Deduplicate bios vs contribution table (they say the same thing)
11. Drop "agile" label unless you can back it with specific agile practices
12. Add missing comma: "At some point during the search**,** the hiker..."
13. Split long sentences (42-word and 52-word offenders identified above)
14. Strengthen exec summary closing line -- end on capability, not "pending validation"

### LOW (nice to have)

15. Add total LOC / file count to exec summary for project scale
16. Add battery endurance estimate to exec summary
17. Consider whether "inverse-variance-weighted spatial clustering" needs simplification for exec summary audience
