# Design Rationale Section -- Deep Review

Reviewed: `report/sections/design_rationale.tex` (236 lines)

---

## 1. STEEPLE: All 7 Dimensions Covered with Specific Examples?

**Verdict: 6/7 strong, 1 weak.**

| Dimension | Project-specific? | Notes |
|-----------|-------------------|-------|
| Social | YES | Volunteer mountain rescue teams, operator-in-the-loop verification, public trust. Specific and grounded. |
| Technological | YES | Pi 5 cost, 4.8 FPS benchmark, TFLite vs Ultralytics package count (4 vs 90+), dual-backend architecture. Strong. |
| Economic | YES | GBP 565 vs GBP 5,800 DJI Matrice 30T. Onboard inference eliminating bandwidth equipment. Concrete numbers. |
| Environmental | YES | SSSI exclusion zone, three-layer geofence, 30m waypoint filtering, 3kg AUW noise claim. Specific. |
| Political | YES | CAA Open Category A3, BVLOS/SORA distinction, MIT licence. Concrete regulatory references. |
| Legal | ADEQUATE but thin | "Detection images stored locally" is good. SSSI/WCA 1981 cross-reference is good. But no mention of GDPR implications if the camera captures bystanders, which a reviewer might flag. |
| Ethical | YES | Operator-in-the-loop gate, 120s auto-reject timeout with ethical framing (coverage > uncertain investigation). The reasoning is well-articulated. |

**Issue -- Legal (line 27-28):** The claim "detection images are stored locally on the Pi and not transmitted to cloud services" is good, but a reviewer could ask: what about images of non-target individuals captured incidentally? Under UK GDPR, processing personal data (images of identifiable people) even locally still has obligations. Consider adding one sentence acknowledging this or noting the low-resolution/altitude makes individuals non-identifiable.

**Issue -- Environmental (line 22):** "The lightweight airframe (3 kg AUW) minimises noise disturbance to wildlife" -- this is asserted without evidence. What decibel level? At what distance? A reviewer could challenge this as wishful thinking. Either cite a noise study or soften to "the relatively lightweight airframe is expected to reduce noise disturbance compared to larger commercial platforms."

---

## 2. MCDA Tables: Are Scores Justified? Could a Reviewer Challenge Any Score?

### Table 1: Companion Computer (lines 49-67)

**Challengeable scores:**

- **Pi 5 Python 3.13 compatibility = 5**: Fair, Pi 5 runs Python 3.13 natively.
- **Jetson Nano Python 3.13 compatibility = 3**: A reviewer might ask "why not 2?" -- JetPack is notoriously slow to update and was still on Python 3.8 as of 2025. Score of 3 seems generous.
- **Intel NCS2 Python 3.13 = 2**: The NCS2 was discontinued. Score of 1 would be more honest since OpenVINO dropped support for it entirely.
- **Pi 5 cost = 5 (GBP 75)**: The Pi 5 8GB is closer to GBP 80-90 in 2026, but still the cheapest option. Minor.

**Missing alternatives a reviewer might raise:**
- Jetson Orin Nano (released 2023, much more relevant than the old Nano). Not including it is a gap because a reviewer familiar with NVIDIA's lineup will notice the comparison is against a discontinued product.
- Orange Pi 5 or similar ARM SBC alternatives.

**Suggestion:** Either add Jetson Orin Nano as a fourth column or add a footnote: "The Jetson Orin Nano was considered but excluded due to its GBP 250+ price point and JetPack dependency."

### Table 2: Communication Architecture (lines 75-92)

**Challengeable scores:**

- **Direct Serial reliability = 2**: The score conflates a Python 3.13-specific bug with the architecture's inherent reliability. Direct serial at 921,600 baud works perfectly on Python 3.11. A reviewer might argue this is unfair scoring -- you are penalising the architecture for a language-version bug, not an architectural weakness.
- **ROS 2 implementation complexity = 1**: Harsh but defensible given the team context. Could be 2.
- **Direct Serial Python 3.13 compatibility = 1 (broken)**: Accurate but the text should clarify this is a pyserial-specific regression, not a fundamental serial incompatibility.

**Overall:** The tables are well-structured and the parenthetical justifications (e.g., "5 (C-level read)") are good practice. Weights sum to 1.0 in all tables. Totals appear arithmetically correct.

### Table 3: Detection Model (lines 114-131)

**Challengeable scores:**

- **YOLOv8n mAP50 = 4 (0.995) but YOLOv8s = 5 (0.997)**: The difference between 0.995 and 0.997 is statistically negligible on a 366-image dataset. Giving them different scores (4 vs 5) overstates the distinction. Both should be 5, or the criterion should be redefined.
- **SSD MobileNet mAP50 = 3 (0.88)**: Was this actually benchmarked on the same dataset? If not, the number needs a citation or caveat. If it is from literature, say so.
- **"Training data requirement" criterion**: The scores (5=small, 4=moderate, 3=large) are subjective. YOLOv8n and YOLOv8s use transfer learning from the same COCO backbone -- the actual data requirement difference between n and s variants is minimal. A reviewer could challenge this.

### Table 4: Search Pattern (lines 141-158)

**Challengeable scores:**

- **Expanding Square coverage = 4 (approx.)**: Expanding square does guarantee coverage if the step size equals the sensor footprint. Score of 4 seems artificially depressed to favour lawnmower. A fairer score would be 5 with a note about polygon-fit complexity.
- **Spiral centre gap = 3**: Fair -- spirals do leave a coverage gap at the start/end depending on implementation.
- **"SAR standard compliance" criterion**: The IAMSAR Manual actually recommends expanding square for point-datum searches (known last position) and parallel track (lawnmower) for area searches. The text correctly identifies lawnmower for area search, but the expanding square score of 4 for "land SAR" is slightly misleading -- it is actually the primary SAR pattern for point searches.

**General MCDA concern:** All four tables produce a clear winner with a comfortable margin. A sceptical reviewer might suspect the criteria and weights were chosen post-hoc to justify pre-made decisions. Consider adding one sentence like "Criteria weights were established before scoring based on project requirements R01--R12" to pre-empt this.

---

## 3. "Decisions That Changed": Are All 4 Clearly Framed as Evidence -> Correction?

**Verdict: Yes, all four follow the pattern well.**

| Decision | Initial Assumption | Measurement | Correction | Clear? |
|----------|-------------------|-------------|------------|--------|
| Focal length | 7.0mm (conservative estimate) | Tape measure: 92cm at 1m | 5.46mm | YES -- quantified impact (3m bias at 30m) |
| Camera resolution | 640x480 (match training) | DJI video: 20x14 px target at 30m | 1456x1088 (46x32 px) | YES -- clear threshold argument |
| TFLite runtime | tflite-runtime (Python 3.11 downgrade needed) | ai-edge-litert exists for 3.13 | Zero code changes | YES -- clean |
| Serial comms | Direct pyserial | BAD_DATA errors at 921,600 baud | MAVProxy UDP bridge | YES -- cross-references Table 2 |

**Minor issues:**

- **Focal length (line 182-183):** "The lens datasheet specifies a 6mm nominal focal length. Initial FOV calculations assumed 7.0mm based on a conservative estimate." -- This is slightly confusing. Why would a "conservative estimate" be HIGHER than the datasheet value? A conservative estimate for FOV calculations would use a shorter focal length (wider FOV, larger ground footprint, more pessimistic GSD). The 7.0mm assumption is actually an aggressive estimate (narrower FOV, smaller footprint, better GSD). Consider rephrasing to "an initial overestimate" rather than "conservative estimate."

- **Camera resolution (line 185-186):** The text says "640 x 480" was the initial config, but YOLOv8's standard training resolution is 640 x 640 (square). The 640 x 480 was presumably the camera capture resolution, not the training resolution. The distinction matters -- clarify that this is the capture resolution.

---

## 4. Why-Not-ROS: Convincing? Counter-Arguments Not Addressed?

**Verdict: Mostly convincing, but missing two counter-arguments a robotics reviewer would raise.**

**What works:**
- The architectural mismatch argument (single-node pipeline) is strong and specific.
- The deployment complexity argument (2 GB vs 50 MB) is concrete and compelling.
- The timeline argument (40-60 hours per developer) is honest and well-cited.
- The closing sentence acknowledging ROS for future work shows intellectual honesty.

**Missing counter-arguments:**

1. **"ROS 2 micro" / minimal installations.** ROS 2 can be installed as a minimal client library (rclpy only), not the full desktop. A reviewer who knows ROS well might argue the 2 GB figure is the full desktop install, not the minimal footprint relevant here. Address this by noting that even rclpy requires DDS middleware setup and colcon build tooling.

2. **Logging, replay, and debugging.** ROS 2's rosbag2 provides timestamped recording and replay of all data streams, which is extremely valuable for post-flight analysis. The current system uses CSV logging and custom tools. A reviewer might argue that the debugging/replay capability alone justifies the ROS overhead. Consider adding a sentence: "Post-flight analysis is handled through CSV telemetry logs and video replay tools (Section~X), which provide sufficient debugging capability for this single-sensor system."

3. **"MAVROS exists."** A ROS-aware reviewer will immediately think "but MAVROS wraps pymavlink and gives you topics for free." Address this directly or it looks like an oversight. One sentence would suffice: "MAVROS provides a ROS wrapper around the same pymavlink API used here, but adds no functionality beyond topic-based access to data already available through direct function calls in a single-process architecture."

---

## 5. Autonomy Justification: Sheridan Taxonomy Used Correctly?

**Verdict: Mostly correct, with one significant misuse.**

- **Level 5 for search phase**: The text says "computer decides, human can veto." Sheridan's Level 5 is actually "The computer executes the suggestion if the human approves within a time limit." This matches the VERIFY state's 120s timeout. However, during SEARCH the drone flies autonomously with no human approval gate -- this is closer to Level 7 ("The computer executes automatically and necessarily informs the human") or Level 8 ("informs the human only if asked"). The human CAN override via M key, but that is not the same as "human can veto." A veto implies the system pauses and waits; override implies the human forcibly interrupts.

- **Level 3 for landing decision**: "Computer suggests, human approves." Sheridan's Level 3 is "The computer narrows the selection down to a few alternatives." Level 4 is "The computer suggests one alternative." The VERIFY state suggests one action (land here) and waits for approval -- this is Level 4, not Level 3.

**Recommendation:** Either adjust the level numbers or add a note that Sheridan's original 10-level taxonomy has been adapted. Many papers use simplified versions, so this is defensible with a caveat.

**Strengths:**
- The asymmetric cost analysis (false positive vs false negative) is excellent and well-structured.
- The three compounding penalties of false positive landing are concrete (90s, 8% battery, coverage pause).
- The argument that lawnmower revisiting mitigates false negatives is clever and sound.
- The 20x coverage rate advantage over manual operation is a strong quantitative claim -- but needs a citation or derivation. Where does 20x come from?

---

## 6. Camera Selection: Global vs Rolling Shutter Argument Clear?

**Verdict: Clear and well-quantified, with one gap.**

**Strengths:**
- The pixel-shift calculation (250 px/s ground motion, 7.5 px shift over 30ms readout) is specific and verifiable.
- The 0.5m ground error from centroid shift is a concrete consequence.
- The trade-off (lower light sensitivity) is honestly acknowledged.
- The Zhang calibration simplification point is a nice technical detail.
- The BGR channel order discovery is a good "lessons learned" inclusion.

**Gap:**
- Line 210: "The provided IMX296 global shutter camera was selected over alternative rolling-shutter modules." The word "provided" implies the camera was given to the team (perhaps by the university?). If so, this undermines the entire trade study -- if the camera was provided, there was no selection decision. Clarify: was this a genuine choice, or is the analysis post-hoc justification of hardware that was already available? If the latter, frame it honestly: "The IMX296 global shutter camera was provided as part of the university equipment allocation. Post-hoc analysis confirms this was the appropriate choice for the following reasons..."

- Line 210: The citation `sukhatme2012rolling_global` suggests a 2012 source. More recent references on global vs rolling shutter for drone CV would strengthen this (e.g., work from 2020+ on UAV inspection or mapping).

---

## 7. Weather Adaptation: Framed as Strength Not Weakness?

**Verdict: Excellently framed. This is one of the strongest paragraphs in the section.**

- The go/no-go framework (three criteria, 80% margin, gust factor) shows professional risk management.
- "Information-maximisation fallback" is a strong phrase -- it reframes cancellation as opportunity.
- The four bench-test items are all concrete with measurable outcomes.
- The closing argument ("higher-quality calibration data than a rushed mid-flight measurement") is compelling and likely true.
- The link back to simulation-first methodology ties it to the project philosophy.

**One minor issue (line 223):** "sustained wind measured 12 m/s with gusts to 18 m/s, failing criterion (1) by 50%" -- the 50% figure is misleading. The criterion is <8 m/s, the measurement is 12 m/s. 12 is 50% above 8, so the phrasing is technically correct, but "exceeding the limit by 50%" reads more clearly than "failing by 50%."

---

## 8. Claims Without Evidence

| Line | Claim | Evidence provided? | Action needed |
|------|-------|--------------------|---------------|
| 13 | "volunteer mountain rescue teams who lack the budget for commercial platforms" | No citation or survey | Add a brief citation or qualify with "typically" |
| 22 | "lightweight airframe (3 kg AUW) minimises noise disturbance to wildlife" | No noise data | Soften language or cite a UAV noise study |
| 133 | "SSD MobileNetV2... substantially lower accuracy on the custom SAR dataset" | No benchmark shown | Add benchmark numbers or cite the test |
| 135 | "Training at higher resolution than the 640x640 inference input allows the network to learn fine-grained features that survive downscaling" | Citation to [yolov8] which is the Ultralytics docs, not a study on multi-resolution training | Find a proper citation for this claim |
| 160 | "216-configuration parametric sweep (6 altitudes x 36 angles)" | Not shown anywhere | Reference an appendix or supplementary material |
| 164 | "20 states and 32 transitions" | References Appendix but reader must verify | Acceptable -- appendix reference is sufficient |
| 176 | "automation advantage in coverage rate is approximately 20x compared to an operator watching a live stream" | Cites [goodrich2008] | Verify this citation actually supports the 20x claim |
| 214 | "IMX296's smaller pixel pitch (3.45 um vs 1.55 um for IMX219)" | Common spec sheet data | Fine, but note that smaller pixel pitch means HIGHER noise (less light per pixel). The text says "smaller pixel pitch... yields higher noise" which is correct but counterintuitive -- a reviewer might misread. Consider "larger pixels on the IMX219 (1.55 um vs 3.45 um) gather more light" |

---

## 9. Alternative Text Suggestions

### Alternative 1: Stronger STEEPLE Opening (replacing line 6)

**Current:**
> Every major design decision was evaluated against the seven STEEPLE dimensions (Social, Technological, Economic, Environmental, Political, Legal, Ethical) before proceeding to technical trade studies for hardware, software architecture, detection, path planning, and mission control.

**Suggested (more assertive, sets up the narrative better):**
> Design decisions were not made in isolation. Each choice---from companion computer to search pattern---was first screened against seven STEEPLE dimensions to identify constraints and stakeholder impacts, then subjected to weighted multi-criteria trade studies with documented scores. This two-stage process ensures that technical optimality does not override social, environmental, or legal obligations.

**Why better:** The current version reads as a checklist statement ("we did STEEPLE"). The alternative shows the methodology has two stages and explains WHY it matters.

### Alternative 2: Stronger Autonomy Justification Opening (replacing lines 168-172)

**Current:**
> This hybrid was chosen after analysing the asymmetric cost structure of SAR false positives versus false negatives.

**Suggested (foregrounds the key insight):**
> This split-level autonomy was chosen because false positives and false negatives carry fundamentally asymmetric costs in single-drone SAR. A false negative (missed detection) is recoverable: the lawnmower pattern guarantees the cell will be revisited on the return leg. A false positive landing is not recoverable: it consumes approximately 8\% of the battery budget (90 seconds of descent, hover, verification, and re-climb), pauses all search coverage, and risks mechanical damage at an uncharacterised landing site. The operator gate is therefore placed at the irreversible decision point.

**Why better:** The current version buries the key insight (asymmetry + recoverability) across two paragraphs. The alternative puts the punchline first and makes the logic immediately clear.

### Alternative 3: Stronger Why-Not-ROS Closing (replacing line 206)

**Current:**
> ROS remains the recommended path for future extensions (multi-drone coordination, SLAM, sensor fusion) where inter-process communication becomes essential.

**Suggested (more specific, shows the team understands when ROS becomes necessary):**
> For future work involving multi-drone coordination, simultaneous localisation and mapping (SLAM), or heterogeneous sensor fusion, the inter-process communication and standardised message types provided by ROS 2 would justify the deployment overhead. The current architecture's modular interfaces (Section~\ref{sec:arch-rationale}) were designed with this migration path in mind: each module's narrow public API maps naturally to a ROS topic or service.

**Why better:** Shows the team has already thought about the migration path, not just acknowledged ROS exists. The reference to the modular interfaces demonstrates forward planning.

---

## Summary of Priority Fixes

**Must fix (a reviewer would challenge these):**

1. Focal length "conservative estimate" is backwards -- should be "initial overestimate" (line 182)
2. Sheridan levels are slightly wrong: search is Level 7-8 not 5, landing is Level 4 not 3 (line 168)
3. "Provided" camera undermines the selection trade study -- clarify if genuine choice or post-hoc justification (line 210)
4. Pixel pitch explanation is counterintuitive -- clarify directionality (line 214)
5. SSD MobileNetV2 mAP claim (0.88) needs citation or benchmark reference (line 133)
6. MCDA weights declared post-hoc concern -- add one sentence about when weights were set (all tables)

**Should fix (strengthens the section):**

7. Legal/STEEPLE: add one sentence on GDPR for incidental bystander capture (line 27)
8. Environmental noise claim: soften or cite (line 22)
9. Add Jetson Orin Nano to companion computer trade study or explain exclusion (line 69)
10. Address MAVROS counter-argument in Why-Not-ROS (line 206)
11. 20x coverage rate claim: verify citation [goodrich2008] supports this number (line 176)
12. 216-configuration sweep: reference supplementary material or appendix (line 160)
13. YOLOv8n vs YOLOv8s mAP scores: both should be 5 given statistical insignificance (line 124)

**Nice to fix (polish):**

14. Apply Alternative Text 1 (STEEPLE opening) for stronger framing
15. Apply Alternative Text 2 (autonomy justification) for clearer argument structure
16. Apply Alternative Text 3 (ROS closing) for forward-planning demonstration
17. Wind criterion: "exceeding the limit by 50%" reads better than "failing by 50%" (line 223)
