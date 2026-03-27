# AENGM0074 Project Brief -- Visual Page-by-Page Description

Source: `docs/AENGM0074-project-brief.pdf` (Release 2.1, 4 February 2026)
Rendered at 200 DPI to `docs/brief_pages/page_01.png` through `page_12.png`.

---

## Page 1 -- Title Page and Overview

**Layout:** Portrait. University of Bristol logo (red shield crest) top-right with "University of BRISTOL" text. Header line: "AENGM0074 Group Project in Aerial Robotics".

**Title:** "Project Brief" in large red bold text, followed by "Release 2.1 -- 4 February 2026".

**Section: Overview** (red heading)

Text content:
- Student groups ("Companies") will deliver a mission plan, systems, and interfaces required to locate a wilderness casualty and deliver a first aid kit in appropriate proximity. A demonstration and validation flight will be conducted in the presence of Flight Lab members and external partners ("the Client").
- The mission will be demonstrated at the UoB aerial robotics test facility ("Fenswood Wilderness", Figure 1) and comprises challenges based on current Search and Rescue (SAR) research activities.
- This document should be considered 'live', i.e. amendments may be issued in response to discussions between Client and Companies. The most up-to-date version will be published via Teams.

**Figure 1: Fenswood Wilderness (kml file available)**
- Large aerial/satellite photograph taking up roughly the bottom half of the page.
- Shows a green grassy field surrounded by hedgerows and trees, with a road visible at the top-left.
- Overlaid on the image are semi-transparent colored polygons:
  - A large **orange/brown polygon** covering most of the central field area (the search/survey region).
  - A **teal/cyan polygon** in the upper-left portion of the field (appears to be the SSSI no-fly zone).
  - A small **red marker pin** roughly in the center-left area.
- A legend box in the upper-right of the image shows colored markers for different zones (though text is small at this resolution -- appears to label Flight Area, Search Area, SSSI, and Take-Off Location).
- "Google Earth" watermark in the bottom-left corner of the image.

**Footnote:** "For reassurance, no 'surprise amendments' are planned for this project. Amendments will be made in good faith in response to Company or other situational requirements."

Page number: 1 (bottom-right).

---

## Page 2 -- Scenario and Requirements

**Layout:** Portrait. No images or figures -- text only with a requirements table.

**Section: Scenario** (red heading)

Text content:
- A hiker traversing the Fenswood Wilderness has been reported as lost. A description has been given of their height, clothing, and equipment, and a broad search region has been defined.
- Mid-search the hiker activates a Personal Locator Beacon (PLB), giving a narrower region upon which to focus the search.
- The search region contains a Site of Specific Scientific Interest (SSSI) where rare birds nest. This area is fenced off and inaccessible to hikers. The SSSI should not be overflown.

**Section: Requirements** (red heading)

A table with columns: **R** (requirement number), **Requirement** (description), **Note** (reference number).

| R | Requirement | Note |
|---|-------------|------|
| R01 | The drone shall only fly within the Flight Area. | 1 |
| R02 | The drone shall not fly over the SSSI. | 1 |
| R03 | The drone shall take off from a region within 5m of the defined Take-Off Location (TOL). | 1 |
| R04 | The drone shall not exceed an altitude of 50m above TOL ground level. | 1 |
| R05 | The drone shall undertake a search of the Search Area and identify potential items of lost person clothing and equipment ('items of interest'). | 1 |
| R06 | Upon PLB activation, which is expected to occur 5-15 minutes into the search, teams will receive coordinates of a Focus Area, defined by n lat/long coordinates, where 3 <= n <= 10, upon which the drone should then focus its search. | 1 |
| R07 | The drone shall land within 10 metres but not within 5 metres of the casualty, deploy the provided first aid kit, then return to TOL. | |
| R08 | The level of autonomy and interface format and functionality shall be determined and justified by the Company and approved by the Client. | |
| R09 | All interfaces (RC, Ground Station, and any others) shall include 'Return to Home' (RTH) and 'Motor Cutoff' commands and other appropriate failsafes. | |
| R10 | Latitude/longitude and images of detected items of interest and of the casualty shall be reported. Verification report appendix including relevant imagery, data, uncertainties, etc., with details agreed between Company and Client. | |
| R11 | The operation must have a designated Company Pilot, who is responsible for compliant operation of the activity. The Company Pilot shall be supervised by a Flight Lab Safety Pilot, who shall have ultimate responsibility and absolute authority over all operations. Additional responsibilities may be allocated as required at Company and Lab discretion. | |
| R12 | All software and flight logs shall be delivered via a public GitHub repository linked from the Company Report, licensed under the MIT licence. | |

**Footnote 1:** Coordinates are available in AENGM0074.kml. Areas will not be visibly marked in any field trials, but teams should report any excursions/incursions verbally during trials and in post-flight reports, and flight logs may be examined to verify compliance. Use of automatic geofences is required.

Page number: 2 (bottom-right).

---

## Page 3 -- Equipment

**Layout:** Landscape orientation. Single section with a large equipment table.

**Section: Equipment** (red heading)

Introductory text: "The Research Drone Platform will be provided preassembled. Companies may augment or modify elements with prior discussion with and approval of the Flight Lab team. The Platform shall be returned in its original state post-demonstration."

**Equipment Table** with columns: **Item**, **Description**, **Quantity**, **Specifications** (URLs).

| Item | Description | Qty | Specifications |
|------|-------------|-----|----------------|
| Hexsoon EDU-450 | Drone platform | 1 | https://ardupilot.org/copter/docs/reference-frames-hexsoon-edu450.html |
| Cube Orange | Flight controller | 1 | https://docs.cubepilot.org/user-guides/autopilot/the-cube-module-overview |
| Here 3+ | GPS receiver | 1 | https://docs.cubepilot.org/user-guides/here-3/here-3-manual |
| FrSky TW-Mini | RC receiver | 1 | https://www.frsky-rc.com/product/tw-mini/ |
| | | | |
| Raspberry Pi 5 8GB | Computer | 1 | https://www.raspberrypi.com/products/raspberry-pi-5/ |
| Raspberry Pi camera (global shutter) | Camera | 1 | https://www.raspberrypi.com/products/raspberry-pi-global-shutter-camera/ |
| Pi camera lens (6mm wide angle) | Lens | 1 | https://thepihut.com/products/raspberry-pi-high-quality-camera-lens |
| Pi camera cable | Cable | 1 | |
| | | | |
| SanDisk Extreme PRO 128GB | Micro SD storage | 2 | https://shop.sandisk.com/en-gb/product/... |
| FrSky Twin X14 | RC transmitter | 1 | https://www.frsky-rc.com/product/twin-x14/ |
| Tarot Payload Release Mechanism (double throw) | Actuator | 1 | http://tarotrc.com/Product/Detail.aspx?... |
| | | | |
| Plus relevant cables, mounts, housings, etc. as required. | | | |

The table is organized into three visual groups separated by blank rows: (1) core drone platform components, (2) companion computer and camera, (3) accessories and peripherals.

All specification URLs are clickable hyperlinks in the original PDF.

Page number: 3 (bottom-right).

---

## Page 4 -- Imagery (Rescue Dummy Photo)

**Layout:** Portrait. Minimal text, dominated by a large photograph.

**Section: Imagery** (red heading)

Text: "Companies will have the opportunity to obtain their own datasets during trial flights."

**Photograph:** A large, clear photograph of the rescue dummy (simulated SAR casualty) lying on a grey concrete/workshop floor. The dummy is:
- Full human-sized mannequin, lying on its back with arms and legs spread out in an irregular pose (right arm extended out to the side, left arm closer to body).
- Dressed in dark clothing -- appears to be wearing a dark green/black jacket and dark trousers.
- Wearing a dark red/maroon cap or helmet on its head.
- The dummy's "skin" is not visible -- it is fully clothed.
- Surrounding environment: workshop/lab floor with blue mats or tarps visible at edges, a yellow equipment case (possibly Pelican case) in the bottom-right corner, and what appears to be a shopping trolley or metal rack in the upper-left.

**Caption:** "Rescue dummy -- simulated SAR casualty (will be attired differently)"

This is a critical reference image -- it shows the type of target the drone's CV system needs to detect. The note that it "will be attired differently" means the actual flight-day dummy may wear different colored clothing.

Page number: 4 (bottom-right).

---

## Page 5 -- Project Deliverables

**Layout:** Portrait. A deliverables table followed by bullet-point notes.

**Section: Project Deliverables** (red heading)

**Deliverables Table** with columns: **D** (number), **Deliverable**, **Description**, **Due**, **%** (weight).

| D | Deliverable | Description | Due | % |
|---|-------------|-------------|-----|---|
| D1 | Preliminary Design Review presentation | Outline proposal including autonomy, timeline, technologies. | Wednesday wk16, In-person | Formative |
| D2 | Platform validation flight | Familiarisation flights, manual and waypoint. | Wednesday wk20 | Formative |
| D3 | Trial flights | Integrated system demonstration, trial data capture. | Wednesday wk21, In-person | Formative |
| D4 | Final Design Review presentation | Requirements verification, initial evaluation. | Wednesday wk22, In-person | Formative |
| D5 | Demonstration flights | Full system demonstration, final data capture. | Wednesday wk22, In-person | Formative |
| D6 | Group Report | Process, outcomes, lessons learned. | Thursday wk23, Group submission (peer weighted) | 50% |
| D7 | Individual Reflective Report | Summary of contribution and personal development. | Thursday wk23, Individual submission | 50% |

**Notes (bullet points):**
- Week numbers as given at https://www.bristol.ac.uk/university/dates/calendar/.
- Dates subject to weather- and logistics-dependent change.
- Blackboard (Bb) submission guidelines at https://www.bristol.ac.uk/digital-education/students/.
- Late penalties as detailed in section 17.4 (modular programmes) at https://www.bristol.ac.uk/academic-quality/assessment/regulations-and-code-of-practice-for-taught-programmes/penalties/.
- Submissions will be checked for academic integrity and are subject to University regulations, information at https://www.bristol.ac.uk/digital-education/assessment-online/academic-integrity/.
- AI usage is permitted per guidelines at https://www.bristol.ac.uk/bilt/sharing-practice/guidance/ai-in-the-assessment/, with restrictions on:
  - Software development -- Category 3: Selective
  - Reporting and presentation -- Category 2: Minimal

Page number: 5 (bottom-right).

---

## Page 6 -- D1 Preliminary Design Review (PDR) Presentation

**Layout:** Portrait. Text only, structured with bullet points and sub-bullets.

**Section: D1 Preliminary Design Review (PDR) presentation (formative)** (red heading)

Format:
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
- An overview of your planned system
  - schematics, flow diagrams
- A summary of progress to-date
  - Screenshots, video, or even a demo of your prototype?
- How you intend to meet each Requirement
  - What data will you capture on your demonstration flight to evidence this?
  - Could be outputs, but also flight logs, photos, videos...
- Your plan from start to finish, or at least from now forwards
  - Gantt chart?
- Initial reflections on working practices
  - Plus/Delta review (what's working well/do more of, what are you considering changing)

**Logistics:**
- A computer with screen will be provided
- You should upload a PowerPoint deck or PDF of slides to the unit Team or bring on USB
- You may also connect your own device via a standard HDMI port if you wish

**Final note:** "The PDR does not contribute towards your final grade but is an important opportunity to shape your progress and gain an insight into what assessors will be looking for in your final deliverables."

Page number: 6 (bottom-right).

---

## Page 7 -- D4 Final Design Review

**Layout:** Portrait. Text only, shorter than page 6.

**Section: D4 Final Design Review** (red heading)

Format:
- In-person presentation with accompanying slides
- 15 min presentation + 10 min questions
- Each company member should present at least one slide each

**Audience:**
- MSc peers
- Flight Lab academics and postgrads
- Wider University colleagues
- External collaborators and guests

**Present:**
- An overview of your system and how it will meet design requirements
- What to expect in your demonstration flight
- How you worked together effectively to meet your goals

**Logistics:**
- A computer with screen will be provided
- You should upload a PowerPoint deck or PDF of slides to the unit Team or bring on USB
- You may also connect your own device via a standard HDMI port if you wish

**Final note:** "The FDR does not contribute towards your final grade but is an important opportunity to showcase your work to internal and external attendees."

Page number: 7 (bottom-right).

---

## Page 8 -- D6 Company Report (50%)

**Layout:** Portrait. Text with numbered list of report sections.

**Section: D6 Company Report (50%)** (red heading)

Submission details:
- Group submission of single PDF including link to public GitHub repository
- Maximum length: 15 pages, excluding cover page, introduction, references, and appendices.

**Required sections (numbered list):**

1. **Executive summary** -- Single page self-contained summary.
2. **Introduction** -- A summary of the context and background to the project. Company description including member bios and roles, and brief description of member contributions.
3. **Design rationale** -- Justification of design decisions including STEEPLE considerations.
4. **System description** -- The architecture of your final system. Flow charts, schematics, images recommended.
5. **Requirements verification** -- Process and evidence of satisfaction of requirements. Descriptions, images, technical details.
6. **Evaluation** -- Plus/delta review of system technical performance (footnote 2).
7. **References** -- As appropriate to cite research/design/code sources and to justify design decisions.
8. **Appendices** -- Further detail e.g. additional schematics, trade-off studies, etc. for completeness and portfolio purposes. Appendices will _not_ be assessed -- include excerpts and summaries in main sections.

**Assessment note:** "Assessment will be against relevant Level 7 criteria (footnote 3), via the tailored rubric in Appendix A."

"Peer weighting details to follow."

**Footnote 2:** "This section should focus on things that contributed to technical success. Individual reflections on team working and self-development will be undertaken in D7."

**Footnote 3:** Link to https://www.bristol.ac.uk/academic-quality/assessment/regulations-and-code-of-practice-for-taught-programmes/marking-criteria/

Page number: 8 (bottom-right).

---

## Page 9 -- D7 Individual Reflective Report (50%)

**Layout:** Portrait. Text with AHEP4 standards descriptions. Contains yellow highlighting.

**Section: D7 Individual Reflective Report (50%)** (red heading)

Submission details:
- Individual submission of single PDF.
- Maximum length: 5 pages, excluding cover page and appendices.

**AHEP4 Standards reference:** "With reference to AHEP4 standards (footnote 4), specifically p32-37, M5,7,16,17."

**"DETAIL TO FOLLOW"** -- highlighted in **yellow** background, indicating this section was incomplete at time of publication.

**AHEP4 Learning Outcomes described:**

- **M5.** Design solutions for complex problems that evidence some originality and meet a combination of societal, user, business and customer needs as appropriate. This will involve consideration of applicable health and safety, diversity, inclusion, cultural, societal, environmental and commercial matters, codes of practice and industry standards.

- **M7.** Evaluate the environmental and societal impact of solutions to complex problems (to include the entire life-cycle of a product or process) and minimise adverse impacts.

- **M16.** Function effectively as an individual, and as a member or leader of a team. Evaluate effectiveness of own and team performance.

- **M17.** Communicate effectively on complex engineering matters with technical and non-technical audiences, evaluating the effectiveness of the methods used.

**Assessment note:** "Assessment will be against relevant Level 7 criteria (footnote 5), via the tailored rubric in Appendix B."

**Footnotes:**
- Footnote 4: https://www.engc.org.uk/media/isd11em/the-accreditation-of-higher-education-programmes-ahep.pdf
- Footnote 5: https://www.bristol.ac.uk/academic-quality/assessment/regulations-and-code-of-practice-for-taught-programmes/marking-criteria/

Page number: 9 (bottom-right).

---

## Page 10 -- Clarifications, Amendments and Errata

**Layout:** Portrait. Very sparse -- a small version history table at the top, rest of page is blank.

**Section: Clarifications, amendments and errata** (red heading)

**Version History Table** with columns: **Release**, **Date**, **Sections**, **Changes**, **Author**.

| Release | Date | Sections | Changes | Author |
|---------|------|----------|---------|--------|
| 1.0 | 26 Nov 2025 | All | Initial release | S Bullock |
| 2.0 | 3 Feb 2026 | Deliverables | Reordered, dates updated | S Bullock |
| 2.1 | 4 Feb 2026 | Deliverables | Renumbered R07 onwards | S Bullock |

Author for all versions: **S Bullock** (presumably the module lead / Flight Lab staff).

Page number: 10 (bottom-right).

---

## Page 11 -- Appendix A: D6 Company Report Assessment Rubric

**Layout:** Landscape orientation. Full-page rubric table.

**Header:** "Appendix A: AENGM0074 **D6 Company Report** assessment rubric, benchmarked against University marking criteria -- level 7."

The rubric is a large table with the following structure:

**Columns (mark bands):** 0, 7, 15, 22, 29, 35 | 42, 45, 48 | 52, 55, 58 | 62, 65, 68 | 72, 75, 78 | 83, 94, 100

The higher mark bands (72-78 and 83-100) have **blue shaded headers** (gradient from medium blue to darker blue), making them visually distinct. Lower bands are unshaded/white.

**Rows (assessment criteria with weights):**

1. **Specialist skills and problem-solving (40%)**
   - 0-35: "Does not show ability to identify key aspects of complex problems or to use appropriate skills and resources to address them."
   - 42-48: "Little evidence of awareness of key aspects, weak deployment of appropriate tools and techniques."
   - 52-58: "Limited ability to identify key aspects and use appropriate resources to address them. Some understanding of technologies and approaches demonstrated."
   - 62-68: "Key aspects of task and challenges identified. Appropriate technologies and approaches selected and implemented effectively."
   - 72-78: "Key aspects of task and challenges identified. Appropriate technologies and approaches selected and implemented effectively, showing initiative and autonomy."
   - 83-100: "Confident and comprehensive identification of task and challenge aspects. Appropriate technologies and approaches selected and implemented highly effectively, showing initiative, autonomy, and creativity."

2. **Decision making (40%)**
   - 0-35: "No evidence shown of ability to make decisions in complex and unpredictable circumstances."
   - 42-48: "Little evidence of ability to make decisions in complex and unpredictable circumstances."
   - 52-58: "Shows limited ability to make decisions in complex and unpredictable circumstances."
   - 62-68: "Confident in adapting to changing and unfamiliar or challenging circumstances and making evidence-based decisions."
   - 72-78: "Confident in adapting to changing and unfamiliar/challenging circumstances and making effective, evidence-based decisions."
   - 83-100: "Shows confidence and creativity in adapting to changing and unfamiliar/challenging circumstances."

3. **Communication (20%)**
   - 0-35: "Very limited awareness of effective communication in reporting and presentation."
   - 42-48: "Limited awareness of effective communication in reporting and presentation."
   - 52-58: "Some awareness of effective communication in reporting and presentation."
   - 62-68: "Reporting and presentation are effective, making use of appropriate techniques and resources."
   - 72-78: "Reporting and presentation are effective, making use of appropriate techniques and resources."
   - 83-100: "Reporting and presentation are effective, engaging, and professional, making use of innovative techniques and resources."

Page number: 11 (bottom-right).

---

## Page 12 -- Appendix B: D7 Individual Reflective Report Assessment Rubric

**Layout:** Landscape orientation. Full-page rubric table.

**Header:** "Appendix B: AENGM0074 **D7 Individual Reflective Report** assessment rubric, benchmarked against University marking criteria -- level 7."

Same column structure as Appendix A (mark bands from 0 to 100), with the same blue shading on the 72-78 and 83-100 columns.

**Rows (assessment criteria with weights):**

1. **Teamwork**
   - 0-35: "Little or no demonstration of ability to work within a team setting."
   - 42-48: "Shows limited ability to work within a team setting."
   - 52-58: "Shows ability to work with others and contribute productively as a member of a team."
   - 62-68: "Works effectively within a team, recognising the value and contributions of others. Able to manage conflict."
   - 72-78: "Consistently demonstrates effective teamworking and leadership skills and able to ensure teams work effectively to meet their obligations and goals. Able to manage conflict."
   - 83-100: "Shows outstanding ability to work and lead a team with creativity and flexibility that is responsive to group members' interests and the obligations and goals of the team. Able to manage conflict."

2. **Self-management**
   - 0-35: "Shows very limited evidence of self-organisational skills and behaviours, and ability to meet deadlines."
   - 42-48: "Shows limited evidence of self-organisational skills and behaviours and ability to meet deadlines."
   - 52-58: "Shows some evidence of self-organisational skills and behaviours. Able to complete most tasks by deadlines."
   - 62-68: "Demonstrates good self-organisational skills and behaviours. Has a professional attitude to completing tasks."
   - 72-78: "Works autonomously demonstrating very good self-organisational skills and behaviours. Has a professional attitude to completing tasks."
   - 83-100: "Works autonomously demonstrating outstanding self-organisational skills and behaviours. Has a professional attitude to completing all tasks."

3. **Insight**
   - 0-35: "Shows very limited awareness of own strengths and weaknesses."
   - 42-48: "Displays limited awareness of own strengths or weaknesses."
   - 52-58: "Shows some ability to identify own strengths and weaknesses. Some evidence of capacity to plan self-development to improve practical and professional skills."
   - 62-68: "Confident in self-reflection and expressing own strengths and weaknesses and able to take a proactive approach to self-development to improve practical and professional skills."
   - 72-78: "Demonstrates ability to work autonomously and assess own strengths and weaknesses. Demonstrates ability to identify and implement an effective programme of self-development to improve practical and professional skills."
   - 83-100: "Shows confidence in working autonomously and setting own goals. Can assess own strengths and weaknesses. Able to identify and implement an effective programme of self-development to improve practical and professional skills. Can provide effective feedback to others to aid their self-development."

**Note:** Unlike Appendix A, the individual rubric rows do not show explicit percentage weights. The criteria are Teamwork, Self-management, and Insight -- all focused on personal/professional development rather than technical skills.

Page number: 12 (bottom-right).
