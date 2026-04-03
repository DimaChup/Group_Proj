# D7 Individual Reflective Report -- Scoring v3

> Scored against Appendix B rubric (Level 7) and AHEP4 standards.
> Previous scores: v1 (68/78/72), v2 (78/82/79).

---

## Rubric Criteria Scores

### 1. Teamwork (M16) -- Score: 76/100 (-2 from v2's 78)

**Why the downgrade from v2:** On re-reading with fresh eyes, v2 was generous. The report has improved structurally since v1, but some of v2's praise was for things that are *described* rather than *demonstrated*. Applying the rubric strictly:

**What works:**
- Belbin framework applied correctly (Specialist/Completer-Finisher) with genuine self-awareness that these roles created bottlenecks. This is real reflection, not name-dropping.
- The Edward CV sub-team paragraph is the strongest teamwork evidence in the entire report. It shows genuine collaboration: complementary skills (his optics vs your software), shared investigation, concrete output (FOV calibration informing GPS conversion). This is what the rubric means by "team effectiveness."
- ROS 2 vs MAVLink conflict is specific and resolved through evidence (20-line demo). The process is clear.
- Pilot feedback on button placement is concrete and shows responsive adaptation.
- Honest admission that solo coding "was not planned -- it evolved" is the most mature sentence in the teamwork section.

**What does NOT work:**

1. **Flexibility is still accommodation, not creative adaptation.** "I adapted to constraints by front-loading integration when the hardware lead had exam commitments." This is schedule accommodation. The rubric at 83+ wants you to show where team input changed your *technical approach*. Every technical disagreement in this report ends with you being right (ROS 2 demo, button placement was the pilot's idea but it's a UI fix not an architectural change). Where did a teammate's suggestion change how you designed a module, chose an algorithm, or structured the architecture?

2. **Conflict management remains thin.** You have exactly two conflicts: ROS 2 (resolved by winning) and workload frustration (managed by reframing). Neither shows genuine negotiation where you gave ground on something you cared about. "Managed by focusing on the shared goal and explicitly acknowledging the project manager's logistical contributions" -- this is coping, not conflict resolution. What was the PM's actual complaint? How did you change your behaviour in response?

3. **"No major interpersonal conflicts" is absent but the tone still implies it.** The report says the storming phase was "brief because the team deferred to demonstrated results." This frames the team as deferring to you, which is leadership but not teamwork. Where did YOU defer to someone else's judgement?

4. **Receiving feedback is still one example.** The pilot's button placement. That is it. What did the PM tell you about your communication pace? What did Edward push back on during CV work? What did any teammate say about your documentation being impenetrable? The rubric says "receiving and responding to feedback" -- one UI button example is not enough for 78+.

5. **Team effectiveness evaluation is about YOUR effectiveness, not the team's.** The rubric (M16) explicitly says "evaluate effectiveness of own AND team performance." You evaluate your own performance extensively. But: Was 5 people right for this project? Was the role allocation optimal? Would 3 strong developers + 2 support roles have been better than 1 developer + 4 other roles? You never evaluate the team structure itself.

**To reach 83+:**
- Add ONE example where a teammate's input changed your technical direction. Not button placement -- something architectural. If this genuinely never happened, then say so explicitly and reflect on what that means about your leadership style.
- Show at least two instances of receiving feedback. The pilot's button fix is one. You need another -- ideally about your *process or approach*, not just a UI element.
- Add 3 sentences evaluating the team's collective performance (not just yours within it).
- Show one moment where you deferred to someone else's judgement, even if you disagreed.

---

### 2. Self-Management (M17) -- Score: 80/100 (-2 from v2's 82)

**Why the adjustment:** The v2 score of 82 placed this one point below the 83 threshold. On strict re-read, the section is competent and well-structured but still too smooth. The rubric at 83+ demands evidence of failure AND recovery, not just planning that worked.

**What works:**
- Weekly milestone structure (weeks 12-15, 16-18, 19-20) is concrete and shows planning discipline. This is real evidence.
- "Living ground-truth document" as task management tool is a genuine professional practice, not a buzzword.
- Weather cancellation contingency (pre-planned bench tests) shows professional attitude -- engineering the schedule.
- The "day-one hardware deployment" lesson is a genuine insight earned through failure.
- Career connection (Ukraine, robotics) gives the self-development narrative authentic stakes.

**What does NOT work:**

1. **No quantified effort.** How many hours per week did you spend? 20? 40? 60? How did this compare to teammates? The rubric says "professional attitude to completing ALL tasks" -- without numbers, this is a claim, not evidence. Even approximate numbers ("I averaged 25 hours/week on software alone, roughly double the next most active contributor") would transform this section.

2. **No self-management failure.** Everything in the timeline reads as planned and executed. Where did you underestimate? Miss a self-imposed deadline? Get stuck on something that took 3x longer than expected? The BGR camera bug is mentioned as a weakness in the strengths/weaknesses section, but it is not framed as a self-management failure -- it is framed as a technical debugging challenge. The difference matters: a self-management failure would be "I allocated one day for Pi deployment and it took five, forcing me to cancel planned field tests."

3. **Version control discipline is unmentioned.** Your git log shows feature branches, progressive commits, meaningful commit messages, and multiple working branches. This is concrete evidence of professional practice that costs you zero words to reference but currently sits as unused evidence.

4. **"Balancing MSc coursework" is mentioned in the workflow doc as something to include, but it does not appear in the actual report.** If you were managing coursework deadlines alongside project milestones, that is relevant self-management evidence.

5. **The development programme actions are all forward-looking.** "Day-one deployment" is marked as "I have already begun applying this" in the workflow doc, but the report text says it generically. Items 1 (collaborative architecture) and 3 (concise communication) have no evidence of current implementation.

**To reach 83+:**
- Add ONE concrete self-management failure and recovery. The BGR bug or Python 3.13 issue would work if framed as "I should have tested on Pi in week 13 instead of week 18 -- this was a planning failure, not a technical one."
- Quantify effort: hours/week, comparison to team average.
- Mention version control discipline in one sentence as evidence of professional practice.
- For at least one development programme action, show you have already started implementing it.

---

### 3. Insight (M5/M7) -- Score: 77/100 (-2 from v2's 79)

**Why the adjustment:** v2 was slightly generous on the "strengths-weaknesses duality" criterion. The report names the duality (rapid prototyping = speed over inclusion) but does not fully develop it.

**What works:**
- Three named weaknesses, each with project-specific evidence. This is the right depth.
- "Designing for collaboration" is a non-trivial, mature self-assessment. It is not a humblebrag disguised as a weakness.
- "Choose speed over inclusion" precisely names the behaviour pattern and connects it to leadership consequences. This is strong.
- "Delayed hardware testing" with concrete consequences (Python 3.13, camera colour) shows technical self-awareness.
- Career connection to Ukraine is authentic and gives stakes to the development programme.
- Final sentence ("quality determined by rigour of testing, not cleverness of algorithms") is an earned insight, not a platitude.

**What does NOT work:**

1. **Strengths-as-weaknesses duality is stated but not developed.** You say "rapid prototyping and system integration" is your strength, and "speed over inclusion" is your weakness. These ARE two sides of the same coin, but you never explicitly connect them. The rubric at 83+ wants: "The same trait that makes me effective (rapid autonomous prototyping) is what made me a poor collaborator. I cannot fix the weakness without risking the strength, so I need to learn when each mode is appropriate." This metacognitive connection is missing.

2. **No external validation of self-assessment.** Every weakness is identified through your own reflection. Did any teammate confirm these observations? Did a module lead say "I felt locked out of the software"? Did the PM say "your documentation was too technical"? The rubric says self-assessment should be validated by external input, not just introspection. Even one sentence -- "The project manager later confirmed that..." -- would significantly strengthen this.

3. **"Helping others develop" is still about correcting work.** Section 04 mentions the pilot identifying a safety risk (button placement), which is the pilot helping YOU. The reverse is not shown. You mention numbered test scripts, simplified API, and documentation as lowering barriers -- but these are artefacts, not development. Helping someone develop means: teaching the pilot to read telemetry data so they could debug autonomously, walking the PM through the state machine so they could write the report section independently, pairing with Edward on TFLite post-processing so he could do it next time. Did any of these happen?

4. **Development programme actions lack measurability.** "Success metric: teammates contributing meaningful code without direct guidance" is good for item 1. Items 2 and 3 lack success metrics. How will you know if "one sentence, one diagram, one demo" works?

5. **The report does not address diversity and inclusion at all.** M5 explicitly includes "health and safety, diversity, inclusion, cultural, societal, environmental." The STEEPLE section covers safety and environmental. Diversity and inclusion are absent. One sentence about team composition, accessibility of the ground station interface, or language barriers in a multinational team would address this.

**To reach 83+:**
- Explicitly connect strength and weakness as the same trait. One sentence of metacognition.
- Add one piece of external validation: a teammate confirming or challenging your self-assessment.
- Replace one "correcting work" example with a "developing capability" example. Did you teach anyone to do something they could not do before?
- Add one sentence addressing diversity/inclusion (M5 requirement).

---

## AHEP4 Standards Scores

### M5 (Design solutions with originality) -- Score: 78/100 (-2 from 80)

**Strengths:** Dual-backend architecture is genuinely original. Simulation-first methodology well-articulated with Schon reference. Progressive testing sequence shows safety-critical thinking. STEEPLE coverage present.

**Weaknesses:**
- STEEPLE is compressed into a single paragraph that reads as a checklist (one clause per factor). At this length it cannot demonstrate depth in any factor.
- Diversity and inclusion are completely absent. M5 explicitly requires "health and safety, diversity, inclusion, cultural, societal, environmental considerations." This is a gap, not a minor omission.
- The "original solutions" are described technically but the *originality* is not justified. What alternatives did you consider and reject? Why is dual-backend better than the obvious alternative (single backend with if-else)? The answer exists in your head but not on paper.
- Political consideration ("CAA regulations") is one clause. Legal compliance is important but this is shallow.

### M7 (Environmental and societal impact) -- Score: 76/100 (-1 from 77)

**Strengths:** Dual-use discussion is honest and personal, not boilerplate. "Detects and localises but a human decides" is a clear design principle. Geofencing protecting SSSI habitats is concrete. "Simulation replaced ~50 physical flights" is quantified.

**Weaknesses:**
- Lifecycle analysis is qualitative. "5W vs 15-30W" is good but incomplete. What about manufacturing, shipping, disposal? You mention battery disposal nowhere in the actual report (only in v2 scoring feedback).
- "Same technology enables unauthorised surveillance" is stated but the mitigation (local-only logging, no persistent surveillance) is asserted without evaluation. How effective is this mitigation really? Someone could trivially modify the open-source code to add persistent surveillance. Does MIT licensing conflict with responsible disclosure?
- The societal benefit paragraph ("SAR drones save lives by surveying large areas faster") is generic. What is YOUR system's specific societal contribution vs existing commercial SAR drones? Your system costs 60 pounds -- that is the differentiator. Lead with it.
- "Released under MIT licence" -- is this actually responsible given dual-use concerns? This tension is not explored.

### M16 (Team effectiveness evaluation) -- Score: 74/100 (-2 from 76)

**Strengths:** Role descriptions are clear. Edward collaboration is the strongest evidence. Solo coding admission is honest and well-analysed. Pilot feedback example shows responsive adaptation.

**Weaknesses:**
- Evaluation is heavily self-focused. The rubric says "evaluate effectiveness of own AND team performance." Where is the evaluation of the team? Was the 5-person structure right? Was role allocation optimal?
- Flexibility evidence is weak (schedule accommodation only, not creative adaptation to input).
- Only one clear example of receiving and acting on feedback.
- No evaluation of what the team would do differently with hindsight.

### M17 (Communication effectiveness evaluation) -- Score: 76/100 (-2 from 78)

**Strengths:** Multiple communication channels described: simulator as demo tool, ground station with large buttons, live demonstrations at PDR/FDR. The insight that the simulator was more effective than documentation is a genuine finding about communication.

**Weaknesses:**
- PDR/FDR presentations are mentioned in one clause but not evaluated. How did you adapt communication for assessors vs teammates vs the pilot? The rubric says "technical and non-technical audiences."
- Documentation strategy (16+ docs, blueprints, ground-truth document) is mentioned in self-management but not framed as a communication tool and evaluated for effectiveness.
- "Frustration over uneven workload was the most persistent tension, managed by focusing on the shared goal" -- how was this COMMUNICATED? Was there a team meeting? A direct conversation? The management of interpersonal tension IS communication, but you do not describe the actual communication act.
- The ground station is described as a communication tool (translating complex state into buttons), which is creative -- but you do not evaluate whether it actually worked. Did the pilot find it usable? What was the error rate?

---

## Composite Scores

| Criterion | v1 | v2 | v3 | Delta v2->v3 | Band |
|-----------|-----|-----|-----|-------------|------|
| Teamwork (M16) | 68 | 78 | **76** | -2 | First (72-78 sub-band) |
| Self-management (M17) | 78 | 82 | **80** | -2 | First (78-83 sub-band) |
| Insight (M5/M7) | 72 | 79 | **77** | -2 | First (72-78 sub-band) |

| AHEP4 | v2 | v3 | Delta | Band |
|-------|-----|-----|-------|------|
| M5 (Design/originality) | 80 | **78** | -2 | First |
| M7 (Environmental/societal) | 77 | **76** | -1 | First |
| M16 (Team effectiveness) | 76 | **74** | -2 | First |
| M17 (Communication) | 78 | **76** | -2 | First |

**Overall estimated D7 mark: 76-77** (down from v2's 79-80)

**Note on score adjustment:** The v2 scores were slightly inflated by crediting structural improvements (section headings, framework references, honest tone) that do not actually satisfy the rubric criteria. The rubric does not reward structure -- it rewards evidence. This v3 scoring applies the rubric more strictly to the actual words on the page.

---

## Top 5 Improvements to Reach 83+

These are ranked by points-per-word -- the changes that will move the needle most in the fewest words.

### 1. Add a genuine compromise example (Teamwork: +4-5 points)

**The problem:** Every technical disagreement ends with you being right. ROS 2 resolved by demo (you won). Button placement was the pilot's idea (you accepted a UI fix, not a direction change). The rubric at 83+ demands "creative flexibility" and "genuine compromise."

**The fix:** Add 2-3 sentences showing where team input changed your technical approach. Examples from your project that could work:
- Did Edward's FOV calibration data cause you to change your GPS estimation approach?
- Did the hardware lead's wiring constraints force you to change your serial communication design?
- Did the PM's risk assessment requirements cause you to add safety features you would have skipped?
- If none of these happened, say so explicitly and reflect: "In every technical decision, the team deferred to my judgement. While this enabled rapid progress, it also meant I never had to defend my choices against a technically equal peer -- a gap in my professional development."

**Where to add:** Section 04, after the ROS 2 paragraph. Replace 2-3 sentences of description with this.

### 2. Add external validation of self-assessment (Insight: +4-5 points)

**The problem:** All three weaknesses are identified through introspection only. The rubric at 83+ wants external confirmation -- "I noticed X, and teammate Y confirmed it."

**The fix:** Add 1-2 sentences showing that your self-assessment is not just navel-gazing. Examples:
- "After the project, I asked the team for candid feedback. [PM name] confirmed that my pace made it hard to contribute: 'By the time I understood the module, you'd already finished the next one.'"
- "Edward observed that my documentation was thorough but assumed too much context -- the 16 documents were useful to me but overwhelming to someone joining mid-project."
- Even if you did not formally solicit feedback, you can reference observable behaviour: "The team's reluctance to modify my code -- even with documentation available -- validated my suspicion that I had optimised for personal velocity over collaborative access."

**Where to add:** Section 05, Strengths and Weaknesses subsection, after naming the primary weakness.

### 3. Add a self-management failure and recovery (Self-management: +3-4 points)

**The problem:** The timeline reads as planned and executed. No breakdowns, no recovery. The rubric at 83+ rewards honest failure narratives.

**The fix:** Frame the delayed hardware testing as a self-management failure, not just a technical weakness. 3-4 sentences:
- "My biggest self-management failure was allocating zero time for Pi deployment until week 18. I assumed laptop simulation would surface all integration issues. It did not: Python 3.13 broke tflite-runtime, the camera outputted BGR despite labelling it RGB888, and the serial library had compatibility issues. What should have been a one-day deployment consumed five days. I recovered by running parallel debugging sessions and creating a Docker-based Pi simulation to prevent similar surprises. The lesson was not technical -- it was about planning: test on target hardware in week one, not week eighteen."

**Where to add:** Section 05, between Time Management and Strengths/Weaknesses.

### 4. Show "developing people" not just "correcting work" (Insight: +3 points)

**The problem:** The rubric says "provide effective feedback to others to aid THEIR self-development." Current examples are artefact-based (numbered test scripts, documentation, simplified API). These lower barriers but do not develop people.

**The fix:** Add one concrete example of capability transfer. 2 sentences:
- "I paired with Edward on TFLite post-processing, walking through the output tensor structure ([1,5,8400]) and NMS filtering so he could independently swap models and evaluate detection quality. He later calibrated the camera FOV without my involvement -- evidence that the knowledge transfer worked."
- Or: "I taught [pilot name] to interpret the telemetry dashboard so they could verify GPS lock quality independently before each flight, rather than relying on my verbal confirmation."

**Where to add:** Section 04, in the Edward collaboration paragraph or after the pilot feedback paragraph.

### 5. Explicitly connect strength-weakness duality + address diversity (Insight + M5: +2-3 points)

**The problem:** (a) "Rapid prototyping" is listed as a strength and "speed over inclusion" as a weakness, but you never explicitly say they are the same trait. (b) M5 requires diversity/inclusion consideration, which is absent.

**The fix:** Two additions:
(a) One metacognitive sentence in Section 05: "These are not separate traits -- rapid prototyping IS speed over inclusion. The same autonomy that let me build 15,000 lines in 10 weeks made it impossible for teammates to keep pace. I cannot fix the weakness without constraining the strength; the skill is knowing when each mode is appropriate."

(b) One sentence in Section 02 or 03 addressing diversity/inclusion: "The ground station's large-button interface was designed for outdoor usability but also improved accessibility -- controls were operable with gloves and readable without close inspection, addressing the universal design principle that field-deployed systems must work for operators with varying technical backgrounds."

**Where to add:** (a) Section 05, Strengths and Weaknesses, after the third weakness. (b) Section 02, STEEPLE paragraph.

---

## Assessment Summary

The report is solidly in the first-class band (72-78 sub-range) across all criteria. It is honest, well-structured, and uses reflective frameworks appropriately rather than decoratively. The writing quality is high and concise.

**What keeps it from 83+:**

1. **Evidence of RECEIVING input is weak.** The report reads as a one-person operation where the author occasionally accepted minor corrections. The rubric rewards bidirectional influence.

2. **Everything works out.** Plans are made and executed. Conflicts are resolved by being right. Weaknesses are identified through introspection. There is no moment of genuine vulnerability -- where something went wrong that was YOUR fault (not a library bug or weather), and you had to recover. The BGR bug and Python 3.13 issues are framed as technical discoveries, not planning failures.

3. **Team evaluation is self-evaluation.** The report evaluates "my performance within the team" extensively but never evaluates "the team's performance as a collective." Was 5 people right? Was role allocation optimal? What would you redesign?

4. **Self-assessment is introspective only.** Strong introspection, but no external confirmation. This caps the insight score around 78.

**The good news:** All five improvements above require roughly 15-20 sentences total (~300 words). The report is already slightly over the 5-page limit, so these additions should replace existing descriptive content rather than being appended. Cut the STEEPLE paragraph (currently too compressed to add value) and trim the Introduction (currently 4 lines but could lose the line count boast) to make room.

**Realistic ceiling after v3 improvements: 82-84.** The structural foundation is strong enough that these targeted additions could push all three criteria into the 80+ band.
