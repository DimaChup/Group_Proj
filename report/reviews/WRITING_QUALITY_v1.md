# Writing Quality Review -- D6 Body Sections

**Reviewed**: design_rationale.tex, system_description.tex, requirements_verification.tex, evaluation.tex
**Date**: 2026-04-03

---

## 1. Grammar and Spelling Errors

### design_rationale.tex
- **Line 6**: "before proceeding to technical trade studies" -- acceptable but slightly awkward. Consider: "before conducting technical trade studies".
- **Line 232**: "sustained visual scanning of a video feed at the frame rate and field-of-view changes produced during an 8 m/s search" -- grammatically tangled. The phrase "at the frame rate and field-of-view changes" reads as if the operator scans *at* the changes. Suggested fix: "...cannot sustain visual scanning of a video feed given the rapid frame-rate and field-of-view changes that occur during an 8 m/s search".
- **Line 236**: Missing full stop or transition after the Goodrich citation at the end of the autonomy section. The paragraph ends cleanly, but it could benefit from a brief concluding sentence.

### system_description.tex
- **Line 41**: "yielding a horizontal FOV of approximately 49.3 degrees" -- this conflicts with the 54.4-degree HFOV mentioned in the CLAUDE.md memory for DJI footage. If these are different cameras, clarify; if the same, reconcile the discrepancy.
- **Line 87**: "Geofencing always runs *after* the state handler, so waypoint commands can be overridden by repulsive velocities." -- correct but consider "so that waypoint commands can be overridden" for clearer subordination.
- **Line 127**: "Bezier-smoothed U-turns maintain momentum through turns" -- "through turns" is slightly redundant with "U-turns". Consider: "Bezier-smoothed U-turns preserve kinetic energy and reduce overshoot."
- **Line 138**: "Deviating by 30 degrees increases scan-line count by ~40%." -- grammatically fine but the tilde (~) should be \textasciitilde{} or $\sim$ in LaTeX for consistent rendering (already uses ${\sim}$, good).

### requirements_verification.tex
- **Line 34**: "verified via telemetry playback of latitude and longitude tracks against the KML polygon" -- "tracks" is slightly ambiguous (noun vs verb). Consider: "verified by overlaying telemetry-recorded latitude and longitude onto the KML polygon".
- **Line 54**: "The Here 3+ GPS receiver's 2.5 m CEP provides sub-5 m accuracy at the home position fix" -- "at the home position fix" is awkward. Try: "for the home position fix".
- **Line 99**: "selecting an action from system-generated options, which defines Level 3--4 in Sheridan's framework" -- the relative clause "which defines" is ambiguous (what does "which" refer to?). Rewrite: "...selecting an action from system-generated options -- a process that corresponds to Level 3--4 in Sheridan's framework".

### evaluation.tex
- **Line 155**: "This approach produced quantitative performance data that would otherwise have required multiple flight sorties." -- this sentence repeats the idea from the previous sentence almost verbatim ("yielded...that would otherwise have required multiple flight sorties"). **Delete one of these two sentences.**
- **Line 200-201**: "Four technical lessons emerged that would shape a second iteration of this project:" -- this duplicates the section title "Lessons Learned" combined with the "What Would Change" section above. Consider rewording to avoid the overlap: "Four technical lessons generalise beyond this project:".

---

## 2. Inconsistent Terminology

### "Drone" vs "UAV" vs "aircraft" vs "system"
The report predominantly uses "aircraft" and "system" but inconsistently mixes in other terms:
- **design_rationale.tex line 22**: "routing the aircraft near the protected area" (aircraft)
- **system_description.tex line 13**: "the take-off point, return-to-launch path" (implicit aircraft)
- **requirements_verification.tex line 34**: "the aircraft completed" (aircraft)
- **requirements_verification.tex line 50**: "the aircraft enters within" (aircraft)
- **evaluation.tex line 39**: "Weather cancelled the scheduled flight day" (no term used)

**Verdict**: "aircraft" and "system" are used consistently. The word "drone" appears only in the CLAUDE.md context, not in the .tex files. This is good. **No action needed** -- the terminology is acceptably consistent throughout the body sections.

### "Dummy" vs "casualty" vs "mannequin" vs "target"
- **design_rationale.tex line 49**: "mannequin" (used once)
- **design_rationale.tex line 69**: "rescue dummy" (used once)
- **design_rationale.tex line 243**: "dummy" (multiple uses)
- **requirements_verification.tex line 72**: "dummy target" (once)
- **evaluation.tex line 158**: "casualties from bystanders or debris"

**Recommendation**: Standardise on "rescue dummy" for the physical test object and "target" or "casualty" for the operational concept. Define "rescue dummy" at first use: "a 1.8 m rescue dummy (mannequin) representing a casualty". Then use "dummy" or "target" consistently thereafter. Avoid switching between "mannequin" and "dummy" without reason.

### "SITL" vs "simulation"
Both are used, but SITL is never spelled out in the body sections.
- **Recommendation**: At first use, write "Software-in-the-Loop (SITL) simulation" then use "SITL" thereafter. Currently, SITL first appears at design_rationale.tex line 16 without expansion.

### "Pi" vs "Raspberry Pi 5" vs "Pi 5"
- First use at design_rationale.tex line 16: "Raspberry Pi 5" (good, full form).
- Subsequent uses: "Pi 5" and "Pi" are mixed freely.
- **Recommendation**: After the first full mention "Raspberry Pi 5 (hereafter Pi 5)", use "Pi 5" consistently. Avoid bare "Pi" without the version number.

---

## 3. Passive Voice Overuse

The report generally does well with active voice, but there are notable lapses:

### design_rationale.tex
- **Line 6**: "Every major design decision **was evaluated** against..." -- passive. Fix: "We evaluated every major design decision against..."
- **Line 13**: "The system **is designed** for volunteer mountain rescue teams" -- passive. Fix: "We designed the system for volunteer mountain rescue teams".
- **Line 16**: "The Raspberry Pi 5 **was selected**" -- passive. Fix: "We selected the Raspberry Pi 5".
- **Line 25**: "All flights comply..." -- good, active.
- **Line 46**: "The sweep **reveals** that..." -- good, active.
- **Line 75**: "A conservative schedule of 8 m/s at 35 m **was adopted**" -- passive. Fix: "We adopted a conservative schedule of 8 m/s at 35 m".
- **Line 129**: "weights **were established** before candidate scoring" -- passive. This phrase appears verbatim 4 times across lines 104, 129, 172, 199. Fix all four: "We established criteria weights before scoring candidates".

### system_description.tex
- **Line 20**: "All hardware **was provided** by the university" -- passive but acceptable (the university is the agent, not the team).
- **Line 249**: "MJPEG **was selected** over H.264/WebRTC for three reasons" -- passive. Fix: "We selected MJPEG over H.264/WebRTC for three reasons".

### requirements_verification.tex
- **Line 42**: "This ensures no planned trajectory approaches the boundary" -- good, active subject.
- Generally well-written with active constructions. Fewer passive issues than other sections.

### evaluation.tex
- **Line 3**: "Where outdoor flight data is unavailable due to weather cancellation, we state so explicitly" -- good active voice.
- **Line 155**: "This approach **produced** quantitative performance data" -- good.
- The evaluation section is the strongest for active voice overall.

**Summary**: The passive voice issue is concentrated in design_rationale.tex, particularly in the STEEPLE analysis and MCDA introductions. The repeated phrase "Criteria weights were established before candidate scoring" appears 4 times and should be rewritten to active voice in all instances.

---

## 4. Vague Claims Without Evidence

The report is generally strong on providing specific numbers. A few exceptions:

### design_rationale.tex
- **Line 16**: "extensive community support" -- vague. Consider quantifying: "a community of 45M+ forum posts and 100K+ Stack Overflow questions" or simply "the largest SBC community ecosystem".
- **Line 104**: "Cost and Python ecosystem compatibility are paramount" -- assertion without ranking justification. The weights in the table (0.20 each) already show this; just reference the table.
- **Line 263**: "40--60 hours per developer" for the ROS learning curve -- this is attributed to the Quigley citation, but is it actually in that source? Verify the citation supports the specific number.

### system_description.tex
- **Line 46**: "approximately 4,400 lines of code" -- good, specific.
- **Line 167**: "bounded capacity (20 entries)" -- good.
- No significant vague claims found.

### requirements_verification.tex
- **Line 64**: "100% recall on the validation set" -- strong claim. Consider adding the caveat inline: "100% recall on the 73-image validation set (noting the train/val overlap discussed in Section X)".
- **Line 127**: "268+ commits" -- good, specific.

### evaluation.tex
- **Line 115**: "resolved in minutes to hours at zero hardware risk" -- slightly vague. The table itself gives specific fix times (5 min to 2 hr), so this is acceptable as a summary.
- No other significant vague claims.

**Verdict**: The report is above average for evidence-backed claims. The few vague spots noted above are minor.

---

## 5. Transitions Between Sections

### design_rationale.tex
- The STEEPLE section flows well internally but ends abruptly at line 33 with `\end{description}` and then jumps straight into "Search Parameter Optimisation" without a transition. **Add a bridging sentence**: "With the STEEPLE framework confirming viability, we now detail the technical trade studies that determined the system's operating parameters."
- The transition from Section 2.2 (Search Parameters) to 2.3 (Parameter Derivation Chain) is smooth -- the latter explicitly builds on the former.
- The transition from "Hardware Platform Selection" (2.4) to "Software Architecture Rationale" (2.6) is fine.
- Section 2.9 (Camera Selection) feels out of place after Section 2.8 (Autonomy Level). It would flow more naturally after Section 2.4 (Hardware Platform Selection) or as a subsection thereof.
- Section 2.10 (Field Day Adaptation) provides a good narrative closure.

### system_description.tex
- Section transitions are smooth. Hardware -> Software -> CV -> Search Pattern -> State Machine -> Localisation -> Ground Station -> Simulation is a logical progression from physical to abstract.
- The only weak transition is between the state machine (3.6) and target localisation (3.7) -- there is no bridging sentence explaining how detections from the search state feed into the localisation pipeline.

### requirements_verification.tex
- The section opens with a summary table (good) and then expands each requirement in order (R01-R12). This is a natural and effective structure.
- No transition issues -- the requirements numbering provides its own flow.

### evaluation.tex
- The plus/delta table at the start is effective.
- The "Discussion of Key Findings" section groups related plus/delta items (P1+P2+P5+P8, then P4+D2+D4+D5+D9, etc.) -- this is a good analytical structure.
- The transition from "Testing Framework Summary" to "What Would Change" to "Lessons Learned" creates some redundancy: both sections discuss what went wrong and what to do next. **Consider merging** "What Would Change" into "Lessons Learned" to avoid repetition.

---

## 6. Jargon Without Definition

The following acronyms/terms are used without being spelled out at first use **in the body sections**:

| Term | First use | Status | Fix |
|------|-----------|--------|-----|
| STEEPLE | design_rationale.tex line 6 | Spelled out in parentheses | OK |
| TFLite | design_rationale.tex line 16 | Never spelled out | Add: "TensorFlow Lite (TFLite)" |
| SITL | design_rationale.tex line 16 (implied) | Never spelled out in body | Add: "Software-in-the-Loop (SITL)" at first use |
| CSI | design_rationale.tex line 97 | Never spelled out | Add: "Camera Serial Interface (CSI)" |
| FSM | design_rationale.tex line 224 | Spelled out | OK |
| MCDA | design_rationale.tex line 104 | Spelled out | OK |
| GSD | system_description.tex line 172 | Spelled out in context | OK |
| MJPEG | system_description.tex line 249 | Never spelled out | Add: "Motion JPEG (MJPEG)" |
| CEP | system_description.tex line 180 | Never spelled out | Add: "Circular Error Probable (CEP)" or "Circular Error Probable at the 50th percentile (CEP50)" |
| XNNPACK | design_rationale.tex line 119 | Never explained | Add a brief parenthetical: "XNNPACK (an optimised CPU inference delegate)" |
| RSS | design_rationale.tex line 52 | Never spelled out | Add: "root sum of squares (RSS)" |
| NMS | system_description.tex line 106 | Never spelled out | Add: "Non-Maximum Suppression (NMS)" |
| DDS | design_rationale.tex line 259 | Never spelled out | Add: "Data Distribution Service (DDS)" |
| AUW | design_rationale.tex line 22 | Never spelled out | Add: "all-up weight (AUW)" |
| PLB | requirements_verification.tex line 76 | Never spelled out in body | Add: "Personal Locator Beacon (PLB)" |
| RTL | requirements_verification.tex line 58 | Never spelled out | Add: "Return to Launch (RTL)" at first body use |
| VLOS / BVLOS | design_rationale.tex line 25 | Not spelled out | Add: "Visual Line of Sight (VLOS)" and "Beyond VLOS (BVLOS)" |
| SORA | design_rationale.tex line 25 | Not spelled out | Add: "Specific Operations Risk Assessment (SORA)" |
| SBC | design_rationale.tex line 126 | Never spelled out | Add: "single-board computer (SBC)" |
| PWM | requirements_verification.tex line 95 | Never spelled out | Add: "Pulse Width Modulation (PWM)" |
| HFOV | design_rationale.tex line varies | Never spelled out | Add: "horizontal field of view (HFOV)" |

**This is the most significant issue in the report.** There are approximately 17 acronyms used without expansion. Some may be defined in the introduction or appendices, but each body section should be readable without requiring the reader to search elsewhere for definitions.

---

## 7. Sentence Length (>40 words)

### design_rationale.tex
- **Line 6** (56 words): "Every major design decision was evaluated against the seven STEEPLE dimensions (Social, Technological, Economic, Environmental, Political, Legal, Ethical) before proceeding to technical trade studies for hardware, software architecture, detection, path planning, and mission control." -- **Break up**: End after "Ethical)." New sentence: "Technical trade studies then addressed hardware, software architecture, detection, path planning, and mission control."
- **Line 16** (62 words): "The Raspberry Pi 5 was selected as the onboard computer for its sub-100 cost, 4.8 FPS inference capability with YOLOv8n/TFLite, native CSI camera interface, and extensive community support. TFLite was chosen over Ultralytics/PyTorch for deployment because it requires only 4 Python packages versus 90+, reducing attack surface and deployment complexity." -- This is already two sentences and each is under 40. **OK**.
- **Line 37** (65 words): "The search pattern is governed by three coupled decision variables---altitude h, scan angle theta, and speed v---that jointly determine five competing objectives: coverage completeness, detection probability, mission time, energy consumption, and NFZ safety margin." -- The sentence continues past the colon with another clause. **Break after the colon list**: end with "NFZ safety margin." Start new sentence: "These objectives cannot be optimised independently..."
- **Line 129** (83 words): The MCDA sensitivity analysis sentence is extremely long. **Break into 3 sentences**: (1) "To test robustness, every criterion weight was varied by +/-0.05..." (2) "In all cases the Pi 5 remained top-ranked (minimum score 4.72 vs Jetson Nano maximum 3.68)." (3) "The ranking inverts only under an extreme scenario..."
- **Line 220** (74 words): The lawnmower rationale sentence is too long. **Break at the semicolons**.

### system_description.tex
- **Line 87** (47 words): The geofencing-after-state-handler sentence. Borderline. Acceptable.
- **Line 172** (54 words): "Each detection is converted from pixel coordinates to GPS using the pinhole camera model..." -- Break after "drone's heading" and start a new sentence for the WGS 84 conversion.
- **Line 247** (53 words): The operator workflow sentence. Break after "press N to investigate." New sentence: "The operator then watches..."

### requirements_verification.tex
- **Line 66-70**: The detection probability paragraph contains a 70+ word sentence starting "However, with only 1.7 m advance per frame..." -- Break into two sentences at "meaning they observe nearly the same scene."
- **Line 91-93**: The Rician distribution sentence (53 words). Borderline, but the maths makes it harder to split. Acceptable for a technical report.

### evaluation.tex
- **Line 102** (54 words): "The AI model was retrained three times---from the original 640-pixel dataset, through a 1280-pixel variant, to the final 1088-pixel version on mixed synthetic and real data---and each swap required only replacing a single file with no changes to the orchestrator, state machine, or ground station." -- Break at the em-dash before "and each swap": make it a new sentence.
- **Line 155** (redundant sentence -- see Grammar section above, delete one).
- **Line 158** (64 words): "Several performance characteristics therefore remain theoretical: detection range as a function of altitude and lighting, false-positive rate against natural backgrounds (grass, shadows, debris), wind-induced motion blur, and GPS accuracy under dynamic manoeuvres." -- Long but structured as a colon-list. Acceptable.

---

## 8. Paragraph Structure and Topic Sentences

### design_rationale.tex
- Each STEEPLE item has a clear topic (the dimension name in bold). Good.
- Section 2.2 (Search Parameter Optimisation) opens with a strong topic sentence. Good.
- Section 2.7 (State Machine Design) is a single paragraph -- adequate given its length, but could benefit from separating the safety mechanisms into their own paragraph.

### system_description.tex
- Section 3.1 (Hardware Platform) opens with a table reference but no topic sentence. **Add one**: "The hardware platform integrates commercial-off-the-shelf components totalling approximately 565 pounds (Table X)."
- Section 3.5 (Search Pattern Generation) is well-structured with named paragraphs.
- Section 3.6 (State Machine) uses a bullet list effectively as its structure.

### requirements_verification.tex
- Each R## subsection starts with a clear statement of the requirement and how it is met. Excellent structure throughout.
- R05 is the longest subsection and is well-broken into named paragraphs. Good.

### evaluation.tex
- The plus/delta table dominates this section, which is appropriate.
- The "Discussion" subsection uses bold topic labels (Architecture resilience, Detection performance, etc.) as paragraph openers. This is effective.
- "Lessons Learned" numbered items each have a bold first sentence serving as a topic sentence. Good.

---

## 9. Cross-Section Consistency Issues

1. **FOV discrepancy**: design_rationale.tex uses "HFOV" values implicitly through focal length calculations. system_description.tex line 41 states "approximately 49.3 degrees" HFOV. requirements_verification.tex line 62 states "49.4 degrees". The CLAUDE.md states "54.4 deg" for DJI video. **Clarify** whether the 49.3/49.4 is for the Pi camera and 54.4 is for the DJI. If so, label explicitly: "Pi camera HFOV of 49.3 degrees" vs "DJI crop HFOV of 54.4 degrees".

2. **Confidence threshold**: design_rationale.tex does not specify the threshold. system_description.tex line 106 says "threshold 0.2". requirements_verification.tex line 64 says "0.2". evaluation.tex line 107 says "0.2". Consistent. Good.

3. **Speed values**: The "nominal search speed" is variously stated as "8 m/s" (most places) and "up to 10 m/s" (design_rationale.tex line 272 for rolling shutter analysis, where it says "up to 10 m/s" but the selected speed is 8 m/s). This is acceptable -- 10 m/s is used as a maximum, 8 m/s as nominal.

4. **Inference time**: Consistently stated as 206.5 ms / 4.8 FPS across all sections. Good.

5. **Repetition of the "criteria weights were established before candidate scoring" phrase**: This identical boilerplate appears at lines 104, 132, 172, and 199 of design_rationale.tex. It reads as copy-pasted. **Recommendation**: State this principle once at the start of the MCDA methodology, then omit from individual tables.

---

## 10. Priority Action Items

Ranked by impact on readability and grading:

1. **HIGH -- Expand 17 undefined acronyms** (Section 6). This is the single biggest issue. A marker will notice undefined jargon immediately.
2. **HIGH -- Break 8 sentences exceeding 40 words** (Section 7). Long sentences obscure meaning in a technical report.
3. **HIGH -- Delete the duplicate sentence in evaluation.tex line 155** (Section 1). An obvious copy-paste error.
4. **MEDIUM -- Convert repeated passive voice to active** (Section 3). Particularly the 4x repeated "Criteria weights were established before candidate scoring".
5. **MEDIUM -- Add transition sentence after STEEPLE analysis** (Section 5).
6. **MEDIUM -- Standardise "dummy" vs "mannequin" vs "target"** (Section 2).
7. **MEDIUM -- Reconcile or label the 49.3 vs 54.4 degree HFOV** (Section 9).
8. **LOW -- Consider merging "What Would Change" into "Lessons Learned"** (Section 5) to reduce repetition.
9. **LOW -- Move Camera Selection subsection closer to Hardware Platform** (Section 5).
10. **LOW -- Add topic sentence to system_description.tex Section 3.1** (Section 8).
