# AENGM0074 Project Brief -- Complete Extraction

> **Source:** `docs/AENGM0074-project-brief.pdf`
> **Release:** 2.1 -- 4 February 2026
> **Author:** S Bullock
> **Unit:** AENGM0074 Group Project in Aerial Robotics, University of Bristol
> **Extracted:** 2026-04-03 (merged from BRIEF_EXTRACTED.md + BRIEF_VISUAL.md + PDF verification)

This is the single definitive extraction of the project brief. Every requirement, deliverable, rubric descriptor, footnote, and constraint from the 12-page PDF is captured here.

---

## 1. Overview

Student groups ("Companies") will deliver a mission plan, systems, and interfaces required to locate a wilderness casualty and deliver a first aid kit in appropriate proximity. A demonstration and validation flight will be conducted in the presence of Flight Lab members and external partners ("the Client").

The mission will be demonstrated at the UoB aerial robotics test facility ("Fenswood Wilderness", Figure 1) and comprises challenges based on current Search and Rescue (SAR) research activities.

This document should be considered 'live', i.e. amendments may be issued in response to discussions between Client and Companies. The most up-to-date version will be published via Teams.^1

> **Footnote 1:** For reassurance, no 'surprise amendments' are planned for this project. Amendments will be made in good faith in response to Company or other situational requirements.

### Figure 1: Fenswood Wilderness (kml file available)

Aerial/satellite photograph (Google Earth imagery) of a green agricultural field surrounded by hedgerows, trees, and roads. Three colored overlay zones are drawn on the field:

- **Teal/cyan semi-transparent polygon** -- the largest zone covering most of the central field. This is the **Flight Area** (outer boundary the drone must stay within).
- **Orange/amber semi-transparent polygon** -- a smaller zone inside the teal area. This is the **Search Area** where the drone must survey.
- **Small red polygon** -- an irregular shape inside the search area. This is the **SSSI** (Site of Specific Scientific Interest) no-fly zone.
- **Take-Off Location** -- a marker near the edge of the Flight Area.

A legend in the upper-right labels: Flight Area, Focus Area (example), SSSI, Survey Area, Take-Off Location.

Coordinates for all zones are provided in `AENGM0074.kml`.

---

## 2. Scenario

A hiker traversing the Fenswood Wilderness has been reported as lost. A description has been given of their height, clothing, and equipment, and a broad search region has been defined.

Mid-search the hiker activates a Personal Locator Beacon (PLB), giving a narrower region upon which to focus the search.

The search region contains a Site of Specific Scientific Interest (SSSI) where rare birds nest. This area is fenced off and inaccessible to hikers. The SSSI should not be overflown.

---

## 3. Requirements (R01--R12)

| R | Requirement | Note |
|---|-------------|------|
| R01 | The drone shall only fly within the Flight Area. | 1 |
| R02 | The drone shall not fly over the SSSI. | 1 |
| R03 | The drone shall take off from a region within 5m of the defined Take-Off Location (TOL). | 1 |
| R04 | The drone shall not exceed an altitude of 50m above TOL ground level. | 1 |
| R05 | The drone shall undertake a search of the Search Area and identify potential items of lost person clothing and equipment ("items of interest"). | 1 |
| R06 | Upon PLB activation, which is expected to occur 5-15 minutes into the search, teams will receive coordinates of a Focus Area, defined by *n* lat/long coordinates, where 3 <= *n* <= 10, upon which the drone should then focus its search. | |
| R07 | The drone shall land within 10 metres but not within 5 metres of the casualty, deploy the provided first aid kit, then return to TOL. | |
| R08 | The level of autonomy and interface format and functionality shall be determined and justified by the Company and approved by the Client. | |
| R09 | All interfaces (RC, Ground Station, and any others) shall include 'Return to Home' (RTH) and 'Motor Cutoff' commands and other appropriate failsafes. | |
| R10 | Latitude/longitude and images of detected items of interest and of the casualty shall be reported. Verification report appendix including relevant imagery, data, uncertainties, etc., with details agreed between Company and Client. | |
| R11 | The operation must have a designated Company Pilot, who will be responsible for compliant operation of the activity. The Company Pilot shall be supervised by a Flight Lab Safety Pilot, who shall have ultimate responsibility and absolute authority over all operations. Additional responsibilities may be allocated as required at Company and Lab discretion. | |
| R12 | All software and flight logs shall be delivered via a public GitHub repository linked from the Company Report, licensed under the MIT licence. | |

> **Footnote 1 (applies to R01--R05):** Coordinates are available in AENGM0074.kml. Areas will not be visibly marked in any field trials, but teams should report any excursions/incursions verbally during trials and in post-flight reports, and flight logs may be examined to verify compliance. **Use of automatic geofences is required.**

---

## 4. Equipment (Provided)

The Research Drone Platform will be provided preassembled. Companies may augment or modify elements with prior discussion with and approval of the Flight Lab team. The Platform shall be returned in its original state post-demonstration.

### Group 1 -- Core Drone Platform

| Item | Description | Qty | Specifications |
|------|-------------|-----|----------------|
| Hexsoon EDU-450 | Drone platform | 1 | https://ardupilot.org/copter/docs/reference-frames-hexsoon-edu450.html |
| Cube Orange | Flight controller | 1 | https://docs.cubepilot.org/user-guides/autopilot/the-cube-module-overview |
| Here 3+ | GPS receiver | 1 | https://docs.cubepilot.org/user-guides/here-3/here-3-manual |
| FrSky TW-Mini | RC receiver | 1 | https://www.frsky-rc.com/product/tw-mini/ |

### Group 2 -- Companion Computer and Camera

| Item | Description | Qty | Specifications |
|------|-------------|-----|----------------|
| Raspberry Pi 5 8GB | Computer | 1 | https://www.raspberrypi.com/products/raspberry-pi-5/ |
| Raspberry Pi camera (global shutter) | Camera | 1 | https://www.raspberrypi.com/products/raspberry-pi-global-shutter-camera/ |
| Pi camera lens (6mm wide angle) | Lens | 1 | https://thepihut.com/products/raspberry-pi-high-quality-camera-lens |
| Pi camera cable | Cable | 1 | -- |

### Group 3 -- Accessories and Peripherals

| Item | Description | Qty | Specifications |
|------|-------------|-----|----------------|
| SanDisk Extreme PRO 128GB | Micro SD storage | **2** | https://shop.sandisk.com/en-gb/products/memory-cards/microsd-cards/sandisk-extreme-pro-uhs-i-microsd |
| FrSky Twin X14 | RC transmitter | 1 | https://www.frsky-rc.com/product/twin-x14/ |
| Tarot Payload Release Mechanism (double throw) | Actuator | 1 | http://tarotrc.com/Product/Detail.aspx?Lang=en&Id=fc95cb53-74ae-4673-8fcc-541ac2d91631 |

Plus relevant cables, mounts, housings, etc. as required.

---

## 5. Imagery (Rescue Dummy)

Companies will have the opportunity to obtain their own datasets during trial flights.

**Photograph description:** A full-body photo of the rescue dummy (simulated SAR casualty) lying on a grey concrete workshop floor.

- **Posture:** Lying flat on its back with arms and legs spread out in an irregular pose (right arm extended to the side, left arm closer to body). Classic "unconscious casualty" spread-eagle position.
- **Clothing:** Dark green/black jacket and dark trousers (one-piece overalls/coveralls style, heavy-duty fabric). The dummy is fully clothed -- no visible "skin".
- **Head:** Dark red/maroon cap or balaclava. No visible facial features.
- **Surroundings:** Light grey concrete floor. Blue tarpaulin/mat at edge, yellow equipment case (Pelican-style) visible, metal rack/trolley in background.
- **Scale:** Approximately life-size, ~1.7--1.8m long.

**Caption:** "Rescue dummy -- simulated SAR casualty (will be attired differently)"

> **IMPORTANT:** The note "will be attired differently" means the clothing and colors during the actual demonstration flight WILL differ from this photo. The CV system must generalise beyond these specific colors.

---

## 6. Project Deliverables (D1--D7)

| D | Deliverable | Description | Due | % |
|---|-------------|-------------|-----|---|
| D1 | Preliminary Design Review presentation | Outline proposal including autonomy, timeline, technologies. | Wednesday wk16, In-person | Formative |
| D2 | Platform validation flight | Familiarisation flights, manual and waypoint. | Wednesday wk20 | Formative |
| D3 | Trial flights | Integrated system demonstration, trial data capture. | Wednesday wk21, In-person | Formative |
| D4 | Final Design Review presentation | Requirements verification, initial evaluation. | Wednesday wk22, In-person | Formative |
| D5 | Demonstration flights | Full system demonstration, final data capture. | Wednesday wk22, In-person | Formative |
| **D6** | **Group Report** | Process, outcomes, lessons learned. | **Thursday wk23**, Group submission (peer weighted) | **50%** |
| **D7** | **Individual Reflective Report** | Summary of contribution and personal development. | **Thursday wk23**, Individual submission | **50%** |

### Deliverable Notes

- Week numbers as given at https://www.bristol.ac.uk/university/dates/calendar/.
- Dates subject to weather- and logistics-dependent change.
- Blackboard (Bb) submission guidelines at https://www.bristol.ac.uk/digital-education/students/.
- Late penalties as detailed in section 17.4 (modular programmes) at https://www.bristol.ac.uk/academic-quality/assessment/regulations-and-code-of-practice-for-taught-programmes/penalties/.
- Submissions will be checked for academic integrity and are subject to University regulations, information at https://www.bristol.ac.uk/digital-education/assessment-online/academic-integrity/.

---

## 7. AI Usage Policy

AI usage is permitted per guidelines at https://www.bristol.ac.uk/bilt/sharing-practice/guidance/ai-in-the-assessment/, with restrictions:

- **Software development** -- **Category 3: Selective** (AI tools can be used selectively)
- **Reporting and presentation** -- **Category 2: Minimal** (minimal AI usage)

---

## 8. D1 Preliminary Design Review (PDR) Presentation (Formative)

**Format:**
- In-person presentation with accompanying slides
- 15 min presentation + 10 min questions
- Each company member should present at least one slide each

**Audience:**
- MSc peers
- Flight Lab academics and postgrads

**Demonstrate that:**
- Your planned work should meet project requirements
- You know what you need to do and when
- You are working together effectively to meet your goals

**You could include:**
- An overview of your planned system (schematics, flow diagrams)
- A summary of progress to-date (screenshots, video, or even a demo of your prototype?)
- How you intend to meet each Requirement
  - What data will you capture on your demonstration flight to evidence this?
  - Could be outputs, but also flight logs, photos, videos...
- Your plan from start to finish, or at least from now forwards (Gantt chart?)
- Initial reflections on working practices (Plus/Delta review -- what's working well/do more of, what are you considering changing)

**Logistics:**
- A computer with screen will be provided
- You should upload a PowerPoint deck or PDF of slides to the unit Team or bring on USB
- You may also connect your own device via a standard HDMI port if you wish

> The PDR does not contribute towards your final grade but is an important opportunity to shape your progress and gain an insight into what assessors will be looking for in your final deliverables.

---

## 9. D4 Final Design Review (Formative)

**Format:**
- In-person presentation with accompanying slides
- 15 min presentation + 10 min questions
- Each company member should present at least one slide each

**Audience:**
- MSc peers
- Flight Lab academics and postgrads
- **Wider University colleagues**
- **External collaborators and guests**

**Present:**
- An overview of your system and how it will meet design requirements
- What to expect in your demonstration flight
- How you worked together effectively to meet your goals

**Logistics:**
- A computer with screen will be provided
- You should upload a PowerPoint deck or PDF of slides to the unit Team or bring on USB
- You may also connect your own device via a standard HDMI port if you wish

> The FDR does not contribute towards your final grade but is an important opportunity to showcase your work to internal and external attendees.

---

## 10. D6 Company Report (50%)

**Submission:** Group submission of single PDF including link to public GitHub repository.
**Maximum length:** 15 pages, excluding cover page, exec summary, introduction, references, and appendices.
**Assessment:** Against relevant Level 7 criteria^3, via the tailored rubric in Appendix A.
**Peer weighting:** Details to follow.

### Required Sections

1. **Executive summary** -- Single page self-contained summary. *(excluded from page count)*
2. **Introduction** -- A summary of the context and background to the project. Company description including member bios and roles, and brief description of member contributions. *(excluded from page count)*
3. **Design rationale** -- Justification of design decisions including STEEPLE considerations.
4. **System description** -- The architecture of your final system. Flow charts, schematics, images recommended.
5. **Requirements verification** -- Process and evidence of satisfaction of requirements. Descriptions, images, technical details.
6. **Evaluation** -- Plus/delta review of system technical performance.^2
7. **References** -- As appropriate to cite research/design/code sources and to justify design decisions. *(excluded from page count)*
8. **Appendices** -- Further detail e.g. additional schematics, trade-off studies, etc. for completeness and portfolio purposes. Appendices will _not_ be assessed -- include excerpts and summaries in main sections. *(excluded from page count)*

> **Footnote 2:** This section should focus on things that contributed to technical success. Individual reflections on team working and self-development will be undertaken in D7.

> **Footnote 3:** https://www.bristol.ac.uk/academic-quality/assessment/regulations-and-code-of-practice-for-taught-programmes/marking-criteria/

---

## 11. Appendix A: D6 Company Report Assessment Rubric

Benchmarked against [University marking criteria -- level 7](https://www.bristol.ac.uk/academic-quality/assessment/regulations-and-code-of-practice-for-taught-programmes/marking-criteria/).

### Specialist Skills and Problem-Solving (40%)

| 0, 7, 15, 22, 29, 35 | 42, 45, 48 | 52, 55, 58 | 62, 65, 68 | 72, 75, 78 | 83, 94, 100 |
|---|---|---|---|---|---|
| Does not show ability to identify key aspects of complex problems or to use appropriate skills and resources to address them. | Little evidence of awareness of key aspects, weak deployment of appropriate tools and techniques. | Limited ability to identify key aspects and use appropriate resources to address them. Some understanding of technologies and approaches demonstrated. | Key aspects of task and challenges identified. Appropriate technologies and approaches selected and implemented effectively. | Key aspects of task and challenges identified. Appropriate technologies and approaches selected and implemented effectively, showing initiative and autonomy. | Confident and comprehensive identification of task and challenge aspects. Appropriate technologies and approaches selected and implemented highly effectively, showing initiative, autonomy, and creativity. |

### Decision Making (40%)

| 0, 7, 15, 22, 29, 35 | 42, 45, 48 | 52, 55, 58 | 62, 65, 68 | 72, 75, 78 | 83, 94, 100 |
|---|---|---|---|---|---|
| No evidence shown of ability to make decisions in complex and unpredictable circumstances. | Little evidence shown of ability to make decisions in complex and unpredictable circumstances. | Shows limited ability to make decisions in complex and unpredictable circumstances. | Confident in adapting to changing and unfamiliar or challenging circumstances and making evidence-based decisions. | Confident in adapting to changing and unfamiliar/challenging circumstances and making effective, evidence-based decisions. | Shows confidence and creativity in adapting to changing and unfamiliar/challenging circumstances and making effective, evidence-based decisions. |

### Communication (20%)

| 0, 7, 15, 22, 29, 35 | 42, 45, 48 | 52, 55, 58 | 62, 65, 68 | 72, 75, 78 | 83, 94, 100 |
|---|---|---|---|---|---|
| Very limited awareness of effective communication in reporting and presentation. | Limited awareness of effective communication in reporting and presentation. | Some awareness of effective communication in reporting and presentation. | Reporting and presentation are effective, making use of appropriate techniques and resources. | Reporting and presentation are effective, making use of appropriate techniques and resources. | Reporting and presentation are effective, engaging, and professional, making use of innovative techniques and resources. |

**Grade band visual coding in original PDF:** Column headers use a blue gradient -- white/no fill for 0-48, light/pale blue for 52-58, medium blue for 62-68, darker blue for 72-78, dark navy for 83-100.

---

## 12. D7 Individual Reflective Report (50%)

**Submission:** Individual submission of single PDF.
**Maximum length:** 5 pages, excluding cover page and appendices.
**Assessment:** Against relevant Level 7 criteria^5, via the tailored rubric in Appendix B.

### AHEP4 Standards

With reference to AHEP4 standards^4, specifically p32-37, M5, M7, M16, M17.

> **"DETAIL TO FOLLOW"** -- This phrase appears with **bright yellow highlight background** in the original PDF. It is the only instance of color highlighting in the entire document, signalling that further D7 specification may be issued later.

**M5.** Design solutions for complex problems that evidence some originality and meet a combination of societal, user, business and customer needs as appropriate. This will involve consideration of applicable health and safety, diversity, inclusion, cultural, societal, environmental and commercial matters, codes of practice and industry standards.

**M7.** Evaluate the environmental and societal impact of solutions to complex problems (to include the entire life-cycle of a product or process) and minimise adverse impacts.

**M16.** Function effectively as an individual, and as a member or leader of a team. Evaluate effectiveness of own and team performance.

**M17.** Communicate effectively on complex engineering matters with technical and non-technical audiences, evaluating the effectiveness of the methods used.

> **Footnote 4:** https://www.engc.org.uk/media/isd11em/the-accreditation-of-higher-education-programmes-ahep.pdf

> **Footnote 5:** https://www.bristol.ac.uk/academic-quality/assessment/regulations-and-code-of-practice-for-taught-programmes/marking-criteria/

---

## 13. Appendix B: D7 Individual Reflective Report Assessment Rubric

Benchmarked against [University marking criteria -- level 7](https://www.bristol.ac.uk/academic-quality/assessment/regulations-and-code-of-practice-for-taught-programmes/marking-criteria/).

**Note:** Unlike the D6 rubric, the D7 rubric rows do **not** show explicit percentage weights. All three criteria focus on personal/professional development rather than technical skills.

### Teamwork

| 0, 7, 15, 22, 29, 35 | 42, 45, 48 | 52, 55, 58 | 62, 65, 68 | 72, 75, 78 | 83, 94, 100 |
|---|---|---|---|---|---|
| Little or no demonstration of ability to work within a team setting. | Shows limited ability to work within a team setting. | Shows ability to work with others and contribute productively as a member of a team. | Works effectively within a team, recognising the value and contributions of others. Able to manage conflict. | Consistently demonstrates effective teamworking and leadership skills and able to ensure teams work effectively to meet their obligations and goals. Able to manage conflict. | Shows outstanding ability to work and lead a team with creativity and flexibility that is responsive to group members' interests and the obligations and goals of the team. Able to manage conflict. |

### Self-management

| 0, 7, 15, 22, 29, 35 | 42, 45, 48 | 52, 55, 58 | 62, 65, 68 | 72, 75, 78 | 83, 94, 100 |
|---|---|---|---|---|---|
| Shows very limited evidence of self-organisational skills and behaviours and ability to meet deadlines. | Shows limited evidence of self-organisational skills and behaviours and ability to meet deadlines. | Shows some evidence of self-organisational skills and behaviours. Able to complete most tasks by deadlines. | Demonstrates good self-organisational skills and behaviours. Has a professional attitude to completing tasks. | Works autonomously demonstrating very good self-organisational skills and behaviours. Has a professional attitude to completing tasks. | Works autonomously demonstrating outstanding self-organisational skills and behaviours. Has a professional attitude to completing all tasks. |

### Insight

| 0, 7, 15, 22, 29, 35 | 42, 45, 48 | 52, 55, 58 | 62, 65, 68 | 72, 75, 78 | 83, 94, 100 |
|---|---|---|---|---|---|
| Shows very limited awareness of own strengths and weaknesses. | Displays limited awareness of own strengths or weaknesses. | Shows some ability to identify own strengths and weaknesses. Some evidence of capacity to plan self-development to improve practical and professional skills. | Confident in self-reflection and expressing own strengths and weaknesses and able to take a proactive approach to self-development to improve practical and professional skills. | Demonstrates ability to work autonomously and assess own strengths and weaknesses. Demonstrates ability to identify and implement an effective programme of self-development to improve practical and professional skills. | Shows confidence in working autonomously and setting own goals. Can assess own strengths and weaknesses. Able to identify and implement an effective programme of self-development to improve practical and professional skills. Can provide effective feedback to others to aid their self-development. |

**Grade band visual coding:** Same blue gradient as Appendix A.

---

## 14. Key Constraints Summary

### Page Limits
1. **D6 is 15 pages max** (excluding cover page, exec summary, introduction, references, appendices)
2. **D7 is 5 pages max** (excluding cover page and appendices)

### Content Requirements
3. D6 must include **STEEPLE** analysis in design rationale (Section 3)
4. D6 must include **requirements verification** with evidence (Section 5)
5. D6 evaluation is **technical performance only** (plus/delta) -- team dynamics belong in D7
6. D7 must reference **AHEP4 M5, M7, M16, M17** standards

### Operational Requirements
7. **Automatic geofences required** for Flight Area (R01) and SSSI (R02)
8. Areas will NOT be visibly marked in the field -- geofences are the only enforcement
9. **GitHub repo must be public, MIT licence** (R12)
10. Must report **lat/lon + images** of all detections (R10)
11. **RTH and Motor Cutoff** commands required on all interfaces (R09)
12. **Landing zone:** 5--10m from casualty, deploy first aid kit, return to TOL (R07)
13. **Max altitude:** 50m above TOL ground level (R04)
14. **Take-off:** Within 5m of defined TOL (R03)
15. **PLB Focus Area:** Received 5--15 min into search, 3--10 coordinate points (R06)

### AI Policy
16. Software development: **Category 3 -- Selective**
17. Reporting and presentation: **Category 2 -- Minimal**

### Assessment
18. D6 assessed via **Appendix A rubric** (3 criteria: Specialist 40%, Decision 40%, Communication 20%)
19. D7 assessed via **Appendix B rubric** (3 criteria: Teamwork, Self-management, Insight -- no explicit weights)
20. D6 is **peer weighted** (details to follow)
21. Both D6 and D7 assessed at **Level 7** (Master's level)

---

## 15. Version History

| Release | Date | Sections | Changes | Author |
|---------|------|----------|---------|--------|
| 1.0 | 26 Nov 2025 | All | Initial release | S Bullock |
| 2.0 | 3 Feb 2026 | Deliverables | Reordered, dates updated | S Bullock |
| 2.1 | 4 Feb 2026 | Deliverables | Renumbered R07 onwards | S Bullock |

---

## 16. Document Formatting Notes (from PDF)

These notes describe the visual formatting of the original PDF for reference:

- **Section headings:** Dark red/maroon color, larger font
- **Body text:** Black, standard serif font
- **Hyperlinks:** Standard blue with underline
- **Tables:** Thin black borders, white cell backgrounds
- **Rubric grade headers:** Blue gradient (white on left to dark navy on right)
- **Page numbers:** Bottom-right corner
- **Footnotes:** Separated by horizontal line, smaller font
- **"DETAIL TO FOLLOW"** on page 9: Only text in the document with yellow highlight background
- **"not" in "Appendices will _not_ be assessed":** Underlined for emphasis
- **Equipment table (page 3):** Landscape orientation with visual separators between groups
- **Rubric tables (pages 11-12):** Landscape orientation, full-page width
- **Mark boundaries:** 0, 7, 15, 22, 29, 35 | 42, 45, 48 | 52, 55, 58 | 62, 65, 68 | 72, 75, 78 | 83, 94, 100 (representative marks within each band, not boundaries -- note gaps 79-82 and 95-99)
