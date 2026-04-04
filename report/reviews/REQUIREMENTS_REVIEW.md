# Requirements Verification Review

**Date:** 2026-04-04
**Files reviewed:** `report/sections/requirements_verification.tex`, `report/sections/requirements_detail.tex`
**Cross-referenced against:** `docs/PROJECT_BRIEF_COMPLETE.md` (Release 2.1)

---

## 1. Are all 12 requirements listed with clear PASS/FAIL status?

**PASS** -- All 12 requirements (R01--R12) are present in Table 1 and in the appendix detail.

**Issue found:** The table uses "Verified (SITL)", "Verified (simulation + video)", "Verified (design)", "Verified (procedural + bench)", "Verified (inspection)" as status labels. These are informative but **lack a clear binary PASS/FAIL column**. Markers scanning the table want an unambiguous verdict. Recommend adding an explicit "Status" column with PASS/PARTIAL/NOT TESTED values alongside the verification fidelity.

**Current status mapping:**
| Req | Current Label | Effective Status |
|-----|--------------|-----------------|
| R01 | Verified (SITL) | PASS (sim) |
| R02 | Verified (SITL) | PASS (sim) |
| R03 | Verified (SITL) | PASS (sim) |
| R04 | Verified (SITL) | PASS (sim) |
| R05 | Verified (simulation + video) | PASS (sim) |
| R06 | Verified (SITL) | PASS (sim) |
| R07 | Verified (SITL + analysis) | PASS (sim) |
| R08 | Verified (design) | PASS (design) |
| R09 | Verified (SITL) | PASS (sim + partial HW) |
| R10 | Verified (SITL + bench) | PASS (sim + bench) |
| R11 | Verified (procedural + bench) | PASS (procedural) |
| R12 | Verified (inspection) | PASS |

**No requirement has real outdoor flight verification.** The summary paragraph acknowledges this, which is good -- but it should be more prominently stated, e.g., in the table caption or a dedicated "Verification Gap" row.

---

## 2. Does each requirement have evidence (test result, screenshot reference, data)?

**Mostly PASS, with gaps.**

| Req | Evidence Quality | Notes |
|-----|-----------------|-------|
| R01 | Strong | SITL telemetry, unit tests, code references, runtime frequency stated |
| R02 | Strong | Multi-layer description, SITL multi-angle approach, geofence diagram ref |
| R03 | Good | SITL telemetry, runtime check described, GPS CEP stated |
| R04 | Strong | Three-layer defence, 28 unit tests cited, config validation |
| R05 | Strong | mAP, FPS, bench results, probability analysis, 39 unit tests |
| R06 | Good | SITL flight log, both triggers tested, unit tests |
| R07 | Strong | Probability analysis, CEP50, unit tests, SITL smoke test, runtime check |
| R08 | Adequate | Sheridan framework cited, levels stated. No figure/table of autonomy levels. |
| R09 | Strong | Three mechanisms, SITL + field bench test, each tested independently |
| R10 | Strong | Three channels described, JSON format detailed, CSV columns listed |
| R11 | Good | 12-item checklist, field day execution, RC override test |
| R12 | Good | URL provided, commit count, LICENSE file confirmed |

**Missing evidence types:**
- **No screenshot/figure references in the table itself.** The brief says "Descriptions, images, technical details." The detail appendix references Figure ref{fig:geofence_diagram} (R02) and Figure ref{fig:mission_overview} (R05) but most requirements have NO figure reference. R10 should show a screenshot of the detection JSON/image output. R07 should show the landing offset geometry.
- **R08** has the weakest evidence -- only a design argument, no diagram showing the autonomy levels or Sheridan scale figure.
- **No flight log excerpts or telemetry plots** are directly referenced. Even a single SITL telemetry screenshot (altitude vs time for R04, position track for R01) would strengthen these.

---

## 3. Is there a traceability matrix (requirement -> test -> result)?

**PARTIAL.** The summary table (Table 1) maps Req -> Method -> Evidence -> Status, which is close to a traceability matrix. However:

- **Missing explicit test script names for most requirements.** R04 mentions "28 unit tests in test_config.py", R05 mentions "13 vision + 26 planning tests", R07 mentions "5 unit tests in test_gps_utils.py", but R01, R03, R06, R08, R09, R10, R11 don't name specific test files in the table. The detail appendix is better (R01 names 0e_geofence_test.py, R06 names 0d_planning_test.py) but the table should be self-contained.
- **No "Test ID" column.** A true traceability matrix has Requirement ID -> Test ID -> Expected Result -> Actual Result -> Pass/Fail. The current format is narrative, not tabular.

**Recommendation:** Either add a Test ID column to the existing table, or add a small supplementary table mapping R01-R12 to specific test script paths.

---

## 4. Are simulation results distinguished from real-world results?

**PASS.** This is handled well:

- The table caption says "Status indicates the highest fidelity at which each requirement has been tested."
- The status column distinguishes SITL, simulation+video, design, procedural+bench, inspection.
- The summary paragraph clearly states the verification gap: "absence of outdoor flight data for R05 and R07."
- R09 explicitly notes RC override was verified on real hardware in addition to SITL.
- R10 notes "SITL + bench."

**Minor issue:** The summary paragraph says "8 are fully verified at bench or higher fidelity (R01-R04, R09-R12)." This is misleading -- R01-R04 are SITL only, not bench. SITL is simulation, not bench. The sentence should say "8 are verified in SITL or higher."

---

## 5. Is the verification methodology clear?

**PASS.** Each requirement in the detail appendix clearly describes HOW it was tested. The methodology is generally well-explained with code-level detail (function names, config parameters, test counts).

**Minor issues:**
- R08 methodology is the weakest -- it's more of a design justification than a verification methodology. How was the autonomy level *tested*? The answer is that it was exercised in SITL (operator confirmed/rejected at VERIFY), but this is not stated.
- The detail appendix is very long and code-heavy. This is good for completeness but markers may not read all of it. The summary table + body paragraph must carry the key message.

---

## 6. Do the requirements match the project brief?

**Cross-reference of brief wording vs report wording:**

| Req | Brief Wording | Report Wording | Match? |
|-----|--------------|----------------|--------|
| R01 | "The drone shall only fly within the Flight Area." | "Fly within Flight Area" | MATCH |
| R02 | "The drone shall not fly over the SSSI." | "No SSSI overfly" | MATCH |
| R03 | "...take off from a region within 5m of the defined Take-Off Location (TOL)." | "Take off within 5m of TOL" | MATCH |
| R04 | "...shall not exceed an altitude of 50m above TOL ground level." | "Max 50m altitude" | MATCH |
| R05 | "...undertake a search of the Search Area and identify potential items of lost person clothing and equipment ('items of interest')." | "Search + identify items" | PARTIAL -- brief says "items of lost person clothing and equipment" but report only discusses dummy/casualty detection, not clothing/equipment items separately |
| R06 | "Upon PLB activation...teams will receive coordinates of a Focus Area...upon which the drone should then focus its search." | "PLB Focus Area" | MATCH |
| R07 | "...land within 10 metres but not within 5 metres of the casualty, deploy the provided first aid kit, then return to TOL." | "Land 5-10m from casualty" | PARTIAL -- Table omits "deploy first aid kit" and "return to TOL" from the short description, but the detail appendix covers both (servo deployment + return transit). The table entry should mention all three sub-requirements. |
| R08 | "The level of autonomy and interface format and functionality shall be determined and justified..." | "Autonomy justified" | MATCH |
| R09 | "All interfaces...shall include 'Return to Home' (RTH) and 'Motor Cutoff' commands and other appropriate failsafes." | "RTH + Motor Cutoff" | PARTIAL -- brief says "Motor Cutoff" specifically but report R09 detail discusses RTH and mode override, does not explicitly address Motor Cutoff (engine kill, disarm) as distinct from RTH |
| R10 | "Latitude/longitude and images of detected items of interest and of the casualty shall be reported. Verification report appendix including relevant imagery, data, uncertainties..." | "Report lat/lon + images" | MATCH |
| R11 | "The operation must have a designated Company Pilot..." | "Company Pilot designated" | MATCH |
| R12 | "All software and flight logs shall be delivered via a public GitHub repository linked from the Company Report, licensed under the MIT licence." | "Public GitHub, MIT licence" | PARTIAL -- Brief says "flight logs" must also be in the repo. Report says "Flight logs and detection data from test sessions are committed alongside the code" but this is in R12 detail, not in the table. |

**Critical gaps found:**

1. **R05 -- "items of interest" vs "casualty only."** The brief explicitly says "identify potential items of lost person clothing and equipment ('items of interest')." The current implementation only detects the full dummy body. The report should address this gap: either explain why individual clothing items are out of scope (model trained on full-body detection), or note that the multi-class model (5 classes: dummy, pants, tshirt, backpack, cone) addresses this. The R05 detail mentions the retrained model but doesn't discuss clothing/equipment item detection specifically.

2. **R07 -- three sub-requirements.** The brief has three parts: (a) land 5-10m, (b) deploy first aid kit, (c) return to TOL. The table entry only mentions (a). The detail appendix covers all three including servo deployment and return transit -- this is GOOD, but the table should reflect all three.

3. **R09 -- "Motor Cutoff" not explicitly addressed.** The brief says "Motor Cutoff" as a distinct command. The report discusses RC kill switch (mode override) and RTH but doesn't mention an explicit motor disarm/cutoff command. If the RC transmitter has a disarm switch or if `MAV_CMD_COMPONENT_ARM_DISARM` is available, this should be stated.

4. **R01 footnote -- "Use of automatic geofences is required."** This footnote applies to R01-R05 and is CRITICAL. The report does address automatic geofences for R01 and R02 (pointPolygonTest, firmware fence), but the footnote is not quoted or referenced. Recommend adding a note that the brief requires automatic geofences and that four software layers + firmware fence satisfy this.

---

## Summary of Issues to Fix

### HIGH PRIORITY (affects marks)

1. **R05 wording gap:** Address "items of interest" (clothing, equipment) vs full-body-only detection. Either explain the design decision or reference the multi-class model.

2. **R07 table entry incomplete:** Add "deploy first aid kit" and "return to TOL" to the short description in the table.

3. **R09 Motor Cutoff:** Explicitly state how motor cutoff (disarm) is commanded -- RC disarm, MAVLink disarm, or confirm that RTL→land→disarm sequence satisfies the requirement.

4. **Add figure/screenshot references:** At minimum, reference a geofence figure (R01/R02), detection output figure (R05/R10), and landing offset diagram (R07) from the table or its surrounding text.

### MEDIUM PRIORITY (improves clarity)

5. **Clarify "bench vs SITL" in summary paragraph.** Line "8 are fully verified at bench or higher" is inaccurate -- R01-R04 are SITL, not bench. Fix wording.

6. **R08 needs a test description.** Add one sentence: the autonomy levels were exercised in SITL end-to-end simulation where the operator confirmed/rejected detections at the VERIFY state.

7. **Brief footnote on automatic geofences:** Add a sentence noting that the brief requires automatic geofences (footnote 1 on R01-R05) and cross-reference the geofence implementation.

### LOW PRIORITY (polish)

8. **Add PASS/FAIL column** to the summary table for quick scanning.

9. **Add test script paths** to the summary table (or a supplementary mapping table).

10. **R12 flight logs:** Confirm flight logs are committed to the public repo as required by the brief.
