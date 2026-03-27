# AENGM0074 Project Brief — Extracted Requirements

> Source: `docs/AENGM0074-project-brief.pdf` (Release 2.1, 4 Feb 2026)
> Extracted: 2026-03-27

---

## Scenario

A lost hiker in Fenswood Wilderness. Mid-search they activate a PLB giving a Focus Area. Search region contains an SSSI (no-fly zone with rare birds).

## Requirements

| R | Requirement |
|---|-------------|
| R01 | Drone shall only fly within the Flight Area |
| R02 | Drone shall not fly over the SSSI |
| R03 | Take off from within 5m of defined Take-Off Location (TOL) |
| R04 | Max altitude 50m above TOL ground level |
| R05 | Search the Search Area and identify potential items of interest (clothing/equipment) |
| R06 | On PLB activation (5-15 min into search), receive Focus Area coordinates (3-10 lat/lon points), refocus search |
| R07 | Land within 10m but not within 5m of casualty, deploy first aid kit, return to TOL |
| R08 | Level of autonomy and interface format determined and justified by Company |
| R09 | All interfaces shall include RTH and Motor Cutoff commands + failsafes |
| R10 | Report lat/lon and images of detected items + casualty. Verification report appendix with imagery, data, uncertainties |
| R11 | Designated Company Pilot, supervised by Flight Lab Safety Pilot with ultimate authority |
| R12 | All software + flight logs on public GitHub (MIT licence), linked from Company Report |

**Note on R01, R02, R03, R04:** Coordinates in AENGM0074.kml. Areas NOT visibly marked in field. Teams report excursions verbally + in post-flight. **Automatic geofences required.**

## Equipment (Provided)

| Item | Description |
|------|-------------|
| Hexsoon EDU-450 | Drone platform |
| Cube Orange | Flight controller |
| Here 3+ | GPS receiver |
| FrSky TW-Mini | RC receiver |
| Raspberry Pi 5 8GB | Companion computer |
| Raspberry Pi camera (global shutter) | IMX296 camera |
| Pi camera lens (6mm wide angle) | Lens |
| SanDisk Extreme PRO 128GB | Micro SD x2 |
| FrSky Twin X14 | RC transmitter |
| Tarot Payload Release Mechanism | First aid kit deploy actuator |

## Deliverables

| D | Deliverable | Due | Weight |
|---|-------------|-----|--------|
| D1 | PDR Presentation | Wed wk16 | Formative |
| D2 | Platform validation flight | Wed wk20 | Formative |
| D3 | Trial flights | Wed wk21 | Formative |
| D4 | Final Design Review presentation | Wed wk22 | Formative |
| D5 | Demonstration flights | Wed wk22 | Formative |
| **D6** | **Group Report** | **Thu wk23** | **50%** |
| **D7** | **Individual Reflective Report** | **Thu wk23** | **50%** |

## AI Usage Policy

- Software development: **Category 3 — Selective** (AI tools can be used selectively)
- Reporting and presentation: **Category 2 — Minimal** (minimal AI usage)

---

## D6 Company Report (50%) — STRUCTURE REQUIRED

- **Format:** Single PDF, group submission, peer weighted
- **Max length:** 15 pages EXCLUDING cover page, exec summary, introduction, references, appendices

### Required Sections:

1. **Executive Summary** — Single page self-contained summary (EXCLUDED from page count)
2. **Introduction** — Context, background, Company description, member bios/roles, member contributions (EXCLUDED from page count)
3. **Design Rationale** — Justification of design decisions including STEEPLE considerations
4. **System Description** — Architecture of final system. Flow charts, schematics, images recommended
5. **Requirements Verification** — Process and evidence of satisfaction of requirements. Descriptions, images, technical details
6. **Evaluation** — Plus/delta review of system technical performance (NOT team working — that's D7)
7. **References** — Cite research/design/code sources, justify design decisions (EXCLUDED from page count)
8. **Appendices** — Additional schematics, trade-off studies. NOT assessed, include excerpts in main sections (EXCLUDED from page count)

### D6 Rubric (Level 7):

| Criterion | Weight | Top Band (72-100) |
|-----------|--------|-------------------|
| **Specialist Skills & Problem-Solving** | **40%** | Confident, comprehensive identification of task/challenges. Technologies selected and implemented highly effectively with initiative, autonomy, creativity |
| **Decision Making** | **40%** | Confidence and creativity in adapting to changing/unfamiliar/challenging circumstances. Effective evidence-based decisions |
| **Communication** | **20%** | Effective, engaging, professional reporting using innovative techniques and resources |

---

## D7 Individual Reflective Report (50%) — STRUCTURE REQUIRED

- **Format:** Single PDF, individual submission
- **Max length:** 5 pages EXCLUDING cover page and appendices

### AHEP4 Standards to Address:

- **M5:** Design solutions for complex problems with originality. Consider health/safety, diversity, inclusion, cultural, societal, environmental, commercial matters, codes of practice, industry standards
- **M7:** Evaluate environmental and societal impact of solutions (entire life-cycle). Minimise adverse impacts
- **M16:** Function effectively as individual and team member/leader. Evaluate effectiveness of own and team performance
- **M17:** Communicate effectively on complex engineering matters with technical and non-technical audiences. Evaluate effectiveness of methods used

### D7 Rubric (Level 7):

| Criterion | Top Band (72-100) |
|-----------|-------------------|
| **Teamwork** | Outstanding ability to work and lead a team with creativity and flexibility. Responsive to group members' interests and obligations. Able to manage conflict |
| **Self-management** | Works autonomously, outstanding self-organisational skills, professional attitude to completing all tasks |
| **Insight** | Confidence in working autonomously, setting own goals. Assess own strengths/weaknesses. Implement effective self-development programme. Provide effective feedback to others |

---

## Key Constraints for Report Writing

1. D6 is **15 pages max** (excl. cover, exec summary, intro, refs, appendices)
2. D7 is **5 pages max** (excl. cover, appendices)
3. D6 must include **STEEPLE** analysis in design rationale
4. D6 must include **requirements verification** with evidence
5. D6 evaluation is **technical performance only** (plus/delta)
6. D7 must reference **AHEP4 M5, M7, M16, M17**
7. AI reporting usage is **Category 2 — Minimal**
8. **Automatic geofences required** (R01, R02)
9. **GitHub repo must be public, MIT licence** (R12)
10. Must include **lat/lon + images** of detections (R10)

---

## Visual Content Per Page

### Page 1 — Title Page + Aerial Map (Figure 1)

**Header:** University of Bristol logo (red shield crest with sun/horse/ship heraldic elements) in top-right corner. Text: "University of BRISTOL" with "AENGM0074 Group Project in Aerial Robotics" below.

**Title:** "Project Brief" in large bold red text. Subtitle: "Release 2.1 -- 4 February 2026".

**Section heading:** "Overview" in dark red/maroon.

**Figure 1 -- Fenswood Wilderness (kml file available):**
Large aerial/satellite photograph (Google Earth imagery) occupying roughly the bottom two-thirds of the page. Shows a green agricultural field surrounded by hedgerows and trees, with roads visible at the edges. Three colored overlay zones are drawn on the field:

- **Teal/cyan semi-transparent polygon** -- the largest zone, covering most of the central field area. This is the **Flight Area** (the outer boundary the drone must stay within).
- **Orange/amber semi-transparent polygon** -- a smaller zone inside the teal area, offset toward the lower-right portion of the field. This is the **Search Area** where the drone must survey.
- **Small red polygon** -- a small irregular shape inside the search area (lower-left quadrant of the orange zone). This is the **SSSI (Site of Specific Scientific Interest)** no-fly zone.

A **legend** is visible in the upper-right of the map image with colored boxes labeling:
- Flight Area
- Search Area
- Take-Off Location
- SSSI

The Take-Off Location appears as a small marker/point near the edge of the Flight Area. The "Google Earth" watermark is visible at the bottom-left of the satellite image.

**Footnote** at bottom: superscript 1 -- "For reassurance, no 'surprise amendments' are planned for this project. Amendments will be made in good faith in response to Company or other situational requirements."

---

### Page 2 — Scenario + Requirements Table

**No images or figures.** Text-only page.

**Section headings** "Scenario" and "Requirements" are in dark red/maroon font.

**Requirements table:** A clean table with thin black borders. Columns: R (requirement ID), Requirement (description text), Note (superscript reference numbers). The table has 12 rows (R01-R12). The "Note" column contains the number "1" for requirements R01-R04, referencing the footnote about coordinates and geofences.

**Footnote 1** at bottom of page: explains that coordinates are in AENGM0074.kml, areas will NOT be visibly marked in field trials, teams must report excursions verbally, and **use of automatic geofences is required**.

No color coding, highlighting, or special formatting in the table beyond standard black text on white background with thin cell borders.

---

### Page 3 — Equipment Table

**Section heading** "Equipment" in dark red/maroon.

**Equipment table:** A structured table with thin black borders and alternating visual grouping. Columns: Item, Description, Quantity, Specifications (containing clickable blue hyperlinks). The table has clear horizontal dividers separating equipment into logical groups:

- **Group 1 (drone platform):** Hexsoon EDU-450, Cube Orange, Here 3+, FrSky TW-Mini -- each quantity 1, with blue hyperlinks to ArduPilot docs, CubePilot docs, and FrSky product pages.
- **Visual separator** (slightly thicker line or spacing gap between groups).
- **Group 2 (companion computer + camera):** Raspberry Pi 5 8GB, Raspberry Pi camera (global shutter), Pi camera lens (6mm wide angle), Pi camera cable -- each quantity 1, with hyperlinks to raspberrypi.com product pages and thepihut.com.
- **Visual separator.**
- **Group 3 (accessories):** SanDisk Extreme PRO 128GB (quantity **2**), FrSky Twin X14 (quantity 1), Tarot Payload Release Mechanism / double throw (quantity 1) -- with hyperlinks to shop.sandisk.com, frsky-rc.com, and tarotrc.com.
- **Final row:** "Plus relevant cables, mounts, housings, etc. as required." -- no quantity or link.

All hyperlinks are rendered in standard blue underlined text. No images of the equipment are shown.

---

### Page 4 — Imagery (Rescue Dummy Photo)

**Section heading** "Imagery" in dark red/maroon.

**Large photograph** occupying most of the page: A full-body photo of the **rescue dummy** (simulated SAR casualty) lying on a grey concrete/workshop floor. Key visual details:

- **Dummy posture:** Lying flat on its back with arms spread outward (one arm extended to the left, one to the right), legs slightly apart. The pose is a classic "unconscious casualty" spread-eagle position.
- **Clothing:** The dummy is dressed in **dark green/olive overalls or coveralls** (one-piece workwear style), appearing to be a heavy-duty fabric.
- **Head/face:** The dummy has a **dark red/maroon balaclava or head covering**. No visible facial features.
- **Surroundings:** The floor is light grey concrete. Visible in the background: a **blue tarpaulin or mat** (bottom-left corner), **yellow equipment** (possibly a cart or machinery, right edge), and what appears to be shelving or workshop storage (top-left). A **red/brown object** is near the dummy's right hand area (possibly a bag or equipment piece).
- **Scale reference:** The dummy appears to be approximately life-size (human-proportioned), roughly 1.7-1.8m long based on proportions.

**Caption below photo:** "Rescue dummy -- simulated SAR casualty (will be attired differently)"

This is a critical reference image -- the note that the dummy "will be attired differently" means the clothing/colors during the actual demonstration flight may differ from this photo.

---

### Page 5 — Project Deliverables Table + AI Policy

**Section heading** "Project Deliverables" in dark red/maroon.

**Deliverables table:** Clean table with thin black borders. Columns: D (deliverable ID), Deliverable (name), Description (details), Due (date), % (weighting). Seven rows (D1-D7):

- D1-D5: All marked as "Formative" in the % column (no grade weight)
- **D6 and D7:** Both show **"50%"** in the % column -- these are the only assessed deliverables
- D6 specifies "Group submission (peer weighted)" and D7 specifies "Individual submission"
- Due dates range from "Wednesday wk16" to "Thursday wk23"
- Delivery format alternates between "In-person" (presentations/flights) and submission

**Bullet list below table** with important policy links (all rendered as blue hyperlinks):
- Week numbers reference: bristol.ac.uk/university/dates/calendar
- Dates subject to weather/logistics changes
- Blackboard submission guidelines link
- Late penalties reference (s17.4 modular programmes)
- Academic integrity checking notice with link
- **AI usage policy** with link, specifying:
  - Software development -- **Category 3: Selective** (in regular text)
  - Reporting and presentation -- **Category 2: Minimal** (in regular text)

No color coding or special formatting beyond blue hyperlinks.

---

### Page 6 — D1 PDR Presentation Details

**Section heading** "D1 Preliminary Design Review (PDR) presentation (formative)" in dark red/maroon.

**Text-only page** with structured bullet lists. No images, figures, or tables.

Content organized into clear subsections:
- Format details (bullet points): in-person, 15 min + 10 min questions, each member presents at least one slide
- **Audience:** MSc peers, Flight Lab academics and postgrads
- **Demonstrate that:** planned work meets requirements, you know what/when, working together effectively
- **You could include:** system overview with schematics/flow diagrams, progress summary with screenshots/video/demo, how to meet each requirement (data capture plans), project plan (Gantt chart), plus/delta reflections
- **Logistics:** computer provided, upload PowerPoint/PDF to Teams or USB, HDMI port available

Final paragraph notes the PDR is formative (no grade contribution) but shapes assessor expectations.

---

### Page 7 — D4 Final Design Review Details

**Section heading** "D4 Final Design Review" in dark red/maroon.

**Text-only page** with structured bullet lists. No images, figures, or tables. Very similar layout to page 6.

Content organized into:
- Format: in-person, 15 min + 10 min questions, each member presents at least one slide
- **Audience:** MSc peers, Flight Lab academics and postgrads, **wider University colleagues**, **external collaborators and guests** (broader audience than PDR)
- **Present:** system overview and how it meets design requirements, what to expect in demonstration flight, how team worked together
- **Logistics:** same as PDR (computer, PowerPoint/PDF, HDMI)

Final paragraph notes FDR is formative but an opportunity to showcase work to internal and external attendees.

---

### Page 8 — D6 Company Report Structure

**Section heading** "D6 Company Report (50%)" in dark red/maroon.

**Text-only page** with a numbered list (1-8) of required report sections. No images, figures, or tables.

Key formatting details:
- Each section name is in **bold** (Executive summary, Introduction, Design rationale, System description, Requirements verification, Evaluation, References, Appendices)
- Descriptions follow each bold heading in regular weight text
- Important constraints noted: 15 pages max excluding cover, exec summary, intro, refs, appendices
- The word "not" in "Appendices will _not_ be assessed" is **underlined** (emphasis)

**Footnotes** at bottom of page:
- Footnote 2: "This section should focus on things that contributed to technical success. Individual reflections on team working and self-development will be undertaken in D7."
- Footnote 3: Link to bristol.ac.uk marking criteria (blue hyperlink)

Assessment note: "against relevant Level 7 criteria, via the tailored rubric in Appendix A."

---

### Page 9 — D7 Individual Reflective Report + AHEP4 Standards

**Section heading** "D7 Individual Reflective Report (50%)" in dark red/maroon.

**AHEP4 standards section** with a notable visual element:

- **"DETAIL TO FOLLOW"** is rendered with **bright yellow highlighting** (yellow background behind the text) -- this is the only instance of color highlighting in the entire document. This signals that more detail about the D7 requirements may be issued later.

The four AHEP4 standards (M5, M7, M16, M17) are listed with their identifiers in **bold**:
- **M5.** Design solutions for complex problems...
- **M7.** Evaluate environmental and societal impact...
- **M16.** Function effectively as individual and team member/leader...
- **M17.** Communicate effectively on complex engineering matters...

**Footnotes** at bottom:
- Footnote 4: Link to engc.org.uk AHEP4 PDF (blue hyperlink)
- Footnote 5: Link to bristol.ac.uk marking criteria (blue hyperlink)

---

### Page 10 — Clarifications, Amendments and Errata Table

**Section heading** "Clarifications, amendments and errata" in dark red/maroon (slightly smaller than main section headings).

**Version history table:** Small compact table with thin black borders at the top of an otherwise mostly empty page. Columns: Release, Date, Sections, Changes, Author.

Three rows:
| Release | Date | Sections | Changes | Author |
|---------|------|----------|---------|--------|
| 1.0 | 26 Nov 2025 | All | Initial release | S Bullock |
| 2.0 | 3 Feb 2026 | Deliverables | Reordered, dates updated | S Bullock |
| 2.1 | 4 Feb 2026 | Deliverables | Renumbered R07 onwards | S Bullock |

The rest of the page is blank white space. No other visual elements.

---

### Page 11 — Appendix A: D6 Company Report Rubric

**Header:** "Appendix A: AENGM0074 **D6 Company Report** assessment rubric, benchmarked against University marking criteria -- level 7." The phrase "University marking criteria -- level 7" is rendered as a **blue hyperlink**.

**Full rubric table** spanning the width of the page. This is the most visually complex element in the document:

**Table structure:** 3 criterion rows x 7 grade band columns, plus a header row.

**Column headers (grade bands):** "Marks", then: **0, 7, 15, 22, 29, 35** | **42, 45, 48** | **52, 55, 58** | **62, 65, 68** | **72, 75, 78** | **83, 94, 100**

**Color-coded column headers** using a gradient from left to right:
- Columns "0-35" and "42-48": **White/no fill** background
- Column "52-58": **Light/pale blue** background
- Column "62-68": **Medium blue** background
- Column "72-78": **Darker blue** background (with white text)
- Column "83-100": **Dark navy/royal blue** background (with white text)

The blue gradient intensifies from left to right, visually emphasizing higher grade bands.

**Row criteria with weights:**
1. **Specialist skills and problem-solving (40%)** -- longest descriptor text in each cell
2. **Decision making (40%)** -- moderate length descriptors
3. **Communication (20%)** -- shortest descriptors

**Cell content style:** Each cell contains a paragraph describing performance at that grade band level. Text is small (approximately 7-8pt equivalent). The descriptors progress from negative/absent performance on the left to exemplary performance on the right.

**Key phrases in the top band (83-100):**
- Specialist skills: "Confident and comprehensive identification of task and challenge aspects. Appropriate technologies and approaches selected and implemented highly effectively, showing initiative, autonomy, and creativity."
- Decision making: "Shows confidence and creativity in adapting to changing and unfamiliar/challenging circumstances and making effective, evidence-based decisions."
- Communication: "Reporting and presentation are effective, engaging, and professional, making use of innovative techniques and resources."

---

### Page 12 — Appendix B: D7 Individual Reflective Report Rubric

**Header:** "Appendix B: AENGM0074 **D7 Individual Reflective Report** assessment rubric, benchmarked against University marking criteria -- level 7." Same blue hyperlink styling as Appendix A.

**Full rubric table** with identical visual structure to page 11:

**Same color-coded grade band columns** with the blue gradient (white on left, deepening to dark navy on right).

**Row criteria (3 rows, no explicit percentage weights shown):**
1. **Teamwork** -- longest descriptors, covering team working, leadership, conflict management
2. **Self-management** -- organisational skills, professional attitude, task completion
3. **Insight** -- self-assessment, strengths/weaknesses, self-development programme, feedback to others

**Key phrases in the top band (83-100):**
- Teamwork: "Shows outstanding ability to work and lead a team with creativity and flexibility that is responsive to group members' interests and the obligations and goals of the team. Able to manage conflict."
- Self-management: "Works autonomously demonstrating outstanding self-organisational skills and behaviours. Has a professional attitude to completing all tasks."
- Insight: "Shows confidence in working autonomously and setting own goals. Can assess own strengths and weaknesses. Able to identify and implement an effective programme of self-development to improve practical and professional skills. Can provide effective feedback to others to aid their self-development."

---

## Additional Details Missed by Text Extraction

### Exact R06 Wording (with math notation)
R06 states: "Upon PLB activation, which is expected to occur 5-15 minutes into the search, teams will receive coordinates of a Focus Area, defined by n lat/long coordinates, where 3 <= n <= 10, upon which the drone should then focus its search."

### Equipment Specification URLs (from page 3)
- Hexsoon EDU-450: https://ardupilot.org/copter/docs/reference-frames-hexsoon-edu450.html
- Cube Orange: https://docs.cubepilot.org/user-guides/autopilot/the-cube-module-overview
- Here 3+: https://docs.cubepilot.org/user-guides/here-3/here-3-manual
- FrSky TW-Mini: https://www.frsky-rc.com/product/tw-mini/
- Raspberry Pi 5: https://www.raspberrypi.com/products/raspberry-pi-5/
- Pi Camera (global shutter): https://www.raspberrypi.com/products/raspberry-pi-global-shutter-camera/
- Pi Camera Lens: https://thepihut.com/products/raspberry-pi-high-quality-camera-lens
- SanDisk SD: https://shop.sandisk.com/en-gb/product/...microsd
- FrSky Twin X14: https://www.frsky-rc.com/product/twin-x14/
- Tarot Release Mechanism: http://tarotrc.com/Product/Detail.aspx?Lang=en&Id=...

### D6 Evaluation Footnote (page 8, footnote 2)
"This section should focus on things that contributed to technical success. Individual reflections on team working and self-development will be undertaken in D7." -- This clarifies that D6 Evaluation is technical-only, not team dynamics.

### D7 "DETAIL TO FOLLOW" Warning (page 9)
The phrase "DETAIL TO FOLLOW" appears with **bright yellow highlight background** -- this is unique in the document and signals incomplete specification. The AHEP4 standards listed (M5, M7, M16, M17) reference "p32-37" of the AHEP4 document.

### Version History Details (page 10)
- Release 1.0: 26 Nov 2025 (initial)
- Release 2.0: 3 Feb 2026 (deliverables reordered, dates updated)
- Release 2.1: 4 Feb 2026 (R07 onwards renumbered) -- this is the current version
- All authored by **S Bullock**

### Rubric Grade Band Boundaries (pages 11-12)
The exact mark boundaries used: 0, 7, 15, 22, 29, 35 | 42, 45, 48 | 52, 55, 58 | 62, 65, 68 | 72, 75, 78 | 83, 94, 100. The jump from 78 to 83 (skipping 79-82) and from 94 to 100 (skipping 95-99) suggests these are representative marks within each band, not boundaries.

### Document Formatting Conventions
- **Section headings:** Dark red/maroon color, larger font
- **Subsection headings:** Same dark red/maroon, slightly smaller
- **Body text:** Black, standard serif font (appears to be a system serif like Times or similar)
- **Hyperlinks:** Standard blue with underline
- **Tables:** Thin black borders, white cell backgrounds (except rubric grade headers which use blue gradient)
- **Page numbers:** Bottom-right corner, plain black
- **Footnotes:** Separated by a horizontal line, smaller font size
