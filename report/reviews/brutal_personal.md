# Brutal Review: Personal Reflective Report

**Date**: 2026-03-27
**Reviewer**: Claude (automated)
**Estimated word count**: ~1,650 (body text, excluding LaTeX commands and references)
**Page estimate**: ~3.5 pages (11pt, 20mm margins, 1.15 spacing)

---

## AHEP4 Coverage Checklist

| LO | Status | Evidence |
|----|--------|----------|
| **M5** (Design & problem-solving) | COVERED | Sec 2: dual-backend vision, simulation-first, inverse-variance localisation, progressive testing, STEEPLE |
| **M7** (Societal & environmental) | COVERED | Sec 3: SAR lives saved, surveillance dual-use, SSSI geofencing, power consumption, MIT licence |
| **M16** (Teamwork & leadership) | COVERED | Sec 4: Belbin roles, Edward CV sub-team, workload honesty, conflict resolution, pilot feedback |
| **M17** (Communication) | COVERED | Sec 4: simulator as communication device, ground station UX, live demos at PDR/FDR |

**Verdict**: All four LOs addressed. M5 and M16 are strong. M7 is adequate but thin. M17 is folded into M16 rather than given distinct treatment.

---

## Specific Element Checklist

| Element | Present? | Notes |
|---------|----------|-------|
| Edward mentioned | YES | Sec 2 (FOV calibration), Sec 4 (CV sub-team paragraph) |
| Conflict example | YES | ROS 2 vs MAVLink disagreement, resolved by working demo |
| Second conflict/tension | YES | Frustration over uneven workload (persistent tension) |
| Self-development programme | YES | Sec 5.4: three numbered actions with success metrics |
| Honest about weaknesses | YES | Three weaknesses: collaboration design, speed over inclusion, delayed hardware testing |
| Reflective frameworks used | YES | Schon, Kolb, Gibbs, Tuckman, Belbin -- all cited and applied |
| Career connection | YES | Ukraine context, humanitarian/defence applications |

---

## SCORE: 72/100

---

## Section-by-Section Critique

### Section 1 -- Introduction (4 lines)
- GOOD: Concise, sets scope, names all four AHEP4 LOs.
- ISSUE: "~15,000 lines of Python" -- is this verified? Inflated numbers undermine credibility. If true, keep it. If it includes blank lines and comments, say "~15,000 lines including tests and tooling".

### Section 2 -- Design & Problem-Solving (M5)
- GOOD: Three concrete technical contributions, each with clear engineering reasoning.
- GOOD: Edward's contribution naturally integrated, not tokenistic.
- GOOD: STEEPLE subsection covers breadth efficiently.
- ISSUE: **No failure discussed.** Everything reads as "I designed it, it worked." The GPS timing lag is mentioned as a discovery, not a design failure. Where did a design decision go wrong? The BGR camera issue from your session log is a perfect candidate -- a wrong assumption about sensor output that cost days. Including one genuine design failure and what you changed would be far more reflective than three successes.
- ISSUE: Schon's "reflection-in-action" is name-dropped but not actually applied. You cite it and then describe building a simulator. Reflection-in-action means adjusting your approach mid-task based on unexpected feedback. Show the moment you changed direction.
- ISSUE: The inverse-variance weighting formula is nice but reads like a technical report, not a reflection. What did you *learn* from having to develop this? What assumption failed first?

### Section 3 -- Societal & Environmental (M7)
- GOOD: Dual-use tension (SAR vs surveillance) is the right framing.
- GOOD: Concrete measures (human-in-loop, local logging, geofencing, 5W power).
- ISSUE: **This is the weakest section.** It reads like a checklist of good things rather than genuine ethical reasoning. "The same technology enables unauthorised surveillance" -- and then what? You installed human-in-the-loop, but did you actually wrestle with the tension? Did the team discuss it? Was there disagreement? A reflective report should show thought process, not just conclusions.
- ISSUE: "Simulation replaced approximately 50 physical flights" -- where does this number come from? If estimated, say so. If precise, explain how you counted.
- ISSUE: No mention of **data privacy** for detected persons. The system photographs people from above. Even in SAR, this raises GDPR questions. Acknowledging this gap would show deeper thinking.
- ISSUE: The MIT licence point is weak -- releasing code open-source is standard for student projects, not an ethical achievement.

### Section 4 -- Teamwork & Leadership (M16/M17)
- GOOD: **This is the strongest section.** Honest about writing all the software alone, honest about optimising for output over team development, honest about the contribution-points lesson.
- GOOD: Edward sub-team paragraph is specific and credible.
- GOOD: Pilot safety feedback example is excellent -- concrete, consequential, and shows you responding to criticism.
- GOOD: ROS vs MAVLink conflict resolved by demonstration, not authority -- good framing.
- ISSUE: **M17 (communication) deserves its own subsection.** Currently it is woven into teamwork. The marking scheme likely expects distinct treatment. You have good material (simulator as communication tool, ground station for non-technical users, demos > slides) -- give it a heading.
- ISSUE: "the project manager booked field slots and submitted risk assessments I would have neglected" -- this is a nice honest touch but could be read as dismissive. Reframe: the PM's work was *essential*, not just stuff you would have skipped.
- ISSUE: The Kolb cycle reference is surface-level. You say "reflecting through Kolb's cycle" and then describe one insight. Actually walk through the four stages: concrete experience (I built it alone) -> reflective observation (output was high but team felt excluded) -> abstract conceptualisation (contribution points must be designed in) -> active experimentation (I tried numbered scripts and docs, which partially worked). This would demonstrate genuine understanding of the framework, not just citation.

### Section 5 -- Self-Development
- GOOD: Three specific weaknesses, not vague ones. "Speed over inclusion" is genuinely honest.
- GOOD: Development programme has measurable success metrics.
- GOOD: Career connection to Ukraine is personal and compelling.
- GOOD: Final sentence is strong and quotable.
- ISSUE: **Time management subsection is filler.** "Weekly milestones" and "living document" are process descriptions, not reflections. What went wrong with time? Did you underestimate Pi deployment (your session log says you did)? Did the weather-cancelled flight day force replanning? Show the struggle, not just the system.
- ISSUE: "Skills Developed" reads like a CV bullet list. Pick ONE skill (e.g., field debugging with no internet) and tell the story: what happened, what you tried, what you learned. That is worth more than listing five things.
- ISSUE: Development programme action 3 ("one sentence, one diagram, one demo") is catchy but has no success metric unlike actions 1 and 2. Add one.

---

## What Would Push This to 85+

### Critical fixes (would add ~8-10 points):

1. **Add a design failure to Section 2.** The camera BGR/RGB issue is perfect: you assumed the sensor output matched the API label, it didn't, it cost days, you learned to verify hardware assumptions with direct testing. This is genuine reflection-in-action (Schon), not just "I built a simulator."

2. **Give M17 its own subsection in Section 4.** Rename current section to "Teamwork and Leadership (M16)" and add "Communication (M17)" with the simulator-as-communication, ground-station-for-non-technical-users, and demos-beat-slides material. This is not padding -- it is giving the marking scheme what it explicitly asks for.

3. **Deepen one reflective cycle properly.** The Kolb reference in Section 4 is your best candidate. Walk through all four stages in 3-4 sentences. Show the examiner you understand the framework, not just the citation.

4. **Add ethical nuance to Section 3.** One paragraph on data privacy (photographing people from altitude, GDPR implications, what you would add in a production system). This turns a checkbox section into actual ethical reasoning.

### Moderate fixes (would add ~3-5 points):

5. **Replace the time management subsection** with a genuine scheduling failure and recovery. The weather-cancelled flight day is real material -- you pivoted to bench testing. That is reflection.

6. **Pick one skill in 5.1 and tell its story** instead of listing four. Field debugging on a Pi over PuTTY with no internet, discovering the camera colour issue by testing all 6 channel permutations -- that is memorable and demonstrates learning depth.

7. **Strengthen the PM framing** -- "essential logistics work" rather than "things I would have neglected."

### Polish (would add ~1-2 points):

8. **Verify the 15,000-line claim** or qualify it ("including test scripts and tooling").
9. **Verify the "50 physical flights" claim** or say "an estimated."
10. **Add a success metric to development action 3.**

---

## Structural Issues

- **No figures or tables.** A reflective report does not require them, but a small table mapping AHEP4 LOs to sections (as a signpost) or a timeline figure could help the examiner navigate. Not essential but helpful.
- **Reference density is appropriate** -- 15 references, mix of academic and technical. No concerns.
- **Page count**: ~3.5 pages is likely fine for a personal reflection (typical limit is 4-6 pages or 2000 words). Check the assignment brief for the exact limit.
- **Tone is appropriate**: professional but personal. Does not read like a group report. Good.

---

## Summary

| Category | Score | Notes |
|----------|-------|-------|
| AHEP4 coverage | 8/10 | All four LOs addressed; M17 needs separation |
| Depth of reflection | 6/10 | Frameworks cited but not fully applied; needs one deep cycle |
| Honesty/self-awareness | 9/10 | Genuinely honest about weaknesses; rare for student work |
| Technical credibility | 8/10 | Concrete details throughout; verify quantitative claims |
| Ethical reasoning | 5/10 | Checkbox approach; needs genuine wrestling with tensions |
| Writing quality | 8/10 | Clean, concise, professional; no padding |
| Structure | 7/10 | M17 needs own heading; time management needs replacing |
| **OVERALL** | **72/100** | Solid B+. The honesty and technical depth are there. Missing: deeper reflection, one failure story, ethical nuance, M17 separation. |

**Bottom line**: This is a competent report held back by surface-level application of reflective frameworks and a Section 3 that reads like a compliance exercise. The raw material in your session logs (camera colour bug, weather-cancelled flight, Python 3.13 incompatibilities) is more reflective than what is currently on the page. Put the real stories in.
