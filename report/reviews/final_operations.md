# Final Operations Review: Appendix Sections

**Sections reviewed:** mission_flow.tex, testing_deep.tex, field_day_narrative.tex, test_scripts_guide.tex, contingency.tex

---

## 1. Mission Flow (mission_flow.tex) — STRONG

### Completeness: Pre-flight to RTL
The section covers the full operational sequence: pre-flight (5-step startup), takeoff, transit, search, detection/queuing, PLB redirect, investigation, verification, approach/landing, RTL, and four concurrent safety layers. Every mission phase is present and traceable to requirement identifiers (R01-R12).

### Strengths
- Excellent detail on the CV processing chain (5-step pipeline with timing: 1.5ms undistort, 206ms inference)
- The detection queuing logic is well-explained: the drone does NOT stop on first detection but continues collecting multi-angle observations. This is a strong design decision and it reads convincingly
- Safety layers section is comprehensive: NFZ geofence (4 layers), manual override (non-destructive with position save), RC kill switch, link loss
- Landing offset rationale (7.5m chosen to balance CEP50 error vs. requirement bounds) is quantitatively justified
- Payload deployment sequence with specific PWM values and timing shows implementation depth

### Issues Found

**MEDIUM — Tier numbering mismatch with testing_deep.tex:**
- mission_flow.tex references "Table~\ref{tab:flight-params}" and "Figure~\ref{fig:state_machine}" and "Figure~\ref{fig:mission_timeline}" — ensure these exist in the main report body, not just referenced
- The four safety layers list has FOUR items numbered 1-4 but uses `\enumerate` — item 3 (repulsive field) and item 2 (speed ramp) overlap: speed ramp says "within 20m" and repulsive field says "within 23m of an inner offset polygon." These distances are close enough to confuse. Clarify whether these are simultaneous or sequential

**LOW — Verify altitude mentions are consistent:**
- Search altitude: 35m (sec:mf-search). Takeoff: 35m (sec:mf-takeoff). But config.py says TARGET_ALT=30. Verify which is correct in the final report
- Transit speed: 15 m/s mentioned twice (transit and RTL) — consistent, good

**LOW — "Three independent mechanisms" for touchdown:**
- The text says "three independent mechanisms" but the third (90-second timeout with forced disarm) is a software timeout, not truly independent from the companion computer. Consider noting this

### Missing
- No mention of battery monitoring during the mission flow narrative (battery failsafe is only in contingency.tex)
- No explicit statement of total expected mission duration or battery budget

---

## 2. Progressive Testing Methodology (testing_deep.tex) — EXCELLENT

### Is the testing methodology compelling?
Yes. This is the strongest section of the five. The argument is built carefully:

1. Cost asymmetry argument (defect cost rises steeply with tier) — well-motivated
2. Five-tier framework with gate enforcement — clearly structured
3. Defect table with 12 real bugs caught — concrete evidence, not hypothetical
4. V-model mapping — academic grounding
5. Cost-risk gradient table — quantified 50:1 iteration throughput ratio

### Strengths
- The "never skip a tier" philosophy is stated clearly and justified empirically (12/15 defects caught at Tiers 1-3)
- Table~\ref{tab:bug-cost-appendix} is the most persuasive element: real bugs, real fix times, real consequences. The geofence sign convention bug and BGR/RGB discovery are particularly strong examples
- The separation of Tier 3 (passive) and Tier 4 (log-only) from standard system testing is well-argued as an extension to the V-model
- The 22 structured simulation tests claim is specific and verifiable
- The summary paragraph is excellent: "treated testing not as a phase that follows development, but as a continuous, tiered process"

### Issues Found

**MEDIUM — Script count discrepancy:**
- Table~\ref{tab:test-categories} claims 58 total scripts across 8 categories, including "Unit" (6) and "Automated" (4) directories
- The CLAUDE.md file structure and test_scripts_guide.tex only describe 6 directories. Where are `tests/unit/` and `tests/automated/`? If these exist, they need to appear in the test scripts guide. If they don't exist yet, the count is inflated
- The section title references "58 dedicated scripts" but test_scripts_guide.tex says "41 test scripts" in its opening line. This is a DIRECT CONTRADICTION that must be resolved

**LOW — Label collision:**
- Table~\ref{tab:bug-cost-appendix} uses label `tab:bug-cost-appendix` but the text references `Table~\ref{tab:bug-cost}`. These won't resolve to the same table unless both labels are defined. Check for a broken cross-reference

**LOW — Tier numbering in Table~\ref{tab:test-categories}:**
- Hardware tests are mapped to "Tier 2 (bench)" but in the text, Tier 2 IS the bench tier. The table in test_scripts_guide.tex maps hardware to "Tier 3." Pick one numbering and be consistent

---

## 3. Field Day Narrative (field_day_narrative.tex) — EXCELLENT

### Is field day adaptation framed as strength?
Yes, very effectively. The framing is strong throughout:

- "a field day defined not by flying, but by the calibration data and integration insights that only become visible when the system meets the real world"
- "This single calibration justified the field day"
- "a day spent measuring is never a day wasted"
- "the team extracted six quantitative outputs from a session that produced zero seconds of flight time"

The narrative avoids apologetic tone and instead presents the cancelled flight as evidence that the methodology works: each tier produces value independently.

### Strengths
- The three-terminal workflow description is operationally specific (T1: mavproxy, T2: diagnostics, T3: scripts) — shows real engineering practice
- FOV calibration section is the highlight: clean derivation (Eq. 4), quantified consequence (22% error = 6m at 30m altitude), and immediate correction committed to repo
- Camera colour discovery is well-told: systematic testing of all 6 permutations, counterintuitive result, trivial fix
- DJI video analysis section provides flight-data proxy results (CEP50=2.3m, GPS timing lag discovery)
- Lessons learned list is concrete and actionable, not generic

### Issues Found

**MEDIUM — Camera resolution inconsistency:**
- Section 3.2 says "640x480 frames" for camera verification, but elsewhere the system uses 1456x1088. This needs clarification — was 640x480 used for the bench stream and 1456x1088 for inference? Or is this an error?

**LOW — Section cross-references:**
- References to "Section~\ref{sec:five-tier}" and "Section~\ref{sec:localisation}" — verify these labels exist in the main report
- Reference to "Figure~\ref{fig:state_machine}" — same concern

**LOW — DJI video section:**
- "mAP50 = 0.995" is mentioned but the DJI video analysis was testing the model, not computing mAP. The mAP figure is from training validation. Rephrase to avoid implying it was measured on DJI footage

---

## 4. Test Scripts Guide (test_scripts_guide.tex) — GOOD, NEEDS FIXES

### Are 58 test scripts properly catalogued?
No — and this is the main problem. The section header says "41 test scripts" while testing_deep.tex claims 58. The tables in this section catalogue:
- Hardware: 6 scripts (Table~\ref{tab:hw-tests})
- Flight: 7 scripts (Table~\ref{tab:flight-scripts})
- Calibration: 5 scripts (Table~\ref{tab:cal-tests})
- Experiments: 6 scripts (Table~\ref{tab:experiment-scripts})
- Diagnostics: 5 scripts (listed as bullet points)
- Laptop: "10+" scripts (mentioned but not individually listed)

That sums to approximately 39-41 scripts, not 58. The "Unit" (6) and "Automated" (4) categories from testing_deep.tex Table~\ref{tab:test-categories} are completely absent from this guide.

### Strengths
- Flight test progression table is excellent: clear script names, what each proves, command level, risk rating
- Script-to-requirement mapping (Table~\ref{tab:script-req-map}) directly connects test infrastructure to the brief
- "What Was Tested on Real Hardware" section is honest and specific
- "Remaining Test Gaps" table is a strong move — admitting gaps with blocking factors shows maturity
- The three laptop drawing utilities (draw_search_area, draw_waypoints, live_map) are properly explained as support tools

### Issues Found

**HIGH — 41 vs 58 script count:**
- This MUST be reconciled with testing_deep.tex. Either:
  (a) Add the missing 17 scripts (unit tests, automated tests, and any others) to this guide, OR
  (b) Correct testing_deep.tex to say 41, and remove the Unit/Automated rows from Table~\ref{tab:test-categories}
- The discrepancy undermines credibility if a marker notices

**MEDIUM — Tier numbering inconsistency:**
- Table~\ref{tab:flight-scripts}: scripts 0a-0c are labeled "Tier 3 (Bench)" and script 1 is "Tier 4 (Passive)"
- But testing_deep.tex defines Tier 2 as bench and Tier 3 as passive flight
- These are completely different numbering schemes. The reader will be confused
- Standardise: either use the 5-tier numbering from testing_deep.tex consistently, or note the mapping explicitly

**MEDIUM — Hardware test count:**
- Description says "6 scripts" but CLAUDE.md lists 8 files in tests/hardware/ (including benchmark_full.py, cv_benchmark.py, detection_snapshot_test.py). Verify the actual count

**LOW — Experiment scripts described twice:**
- Both testing_deep.tex (Section 2.4) and test_scripts_guide.tex (Section 5) describe the same 6 experiment scripts in nearly identical detail. Consider having one section reference the other to avoid redundancy

---

## 5. Contingency Planning (contingency.tex) — STRONG

### Are contingency plans realistic?
Yes. The three-tier deliverable structure (MVD, Target, Stretch) is well-designed and the contingency table covers the right failure modes.

### Strengths
- MVD is genuinely viable: Mission Planner AUTO + passive CV + verbal confirmation. This would actually work on flight day with zero custom flight code
- The MVD explicitly acknowledges which requirements it does NOT satisfy (R06, R07) — honest and shows understanding of the brief
- Contingency table covers 8 realistic scenarios with specific detection criteria and concrete responses
- Each contingency has a mapped test script — this is excellent practice
- The "Full fallback to MVD" row closes the loop: if everything goes wrong, there's always a known-good configuration
- DO-178C citation adds credibility to the progressive approach

### Issues Found

**MEDIUM — Stretch goals vs target deliverable overlap:**
- "Multi-target detection" is listed as stretch, but the target deliverable already mentions a "detection queue with spatial clustering." The distinction between what's target and what's stretch needs sharpening
- "Live PLB focus area redirect" is stretch, but mission_flow.tex (Section 1.6) describes it as part of the normal mission flow. This is contradictory — is PLB redirect in the target deliverable or not?

**LOW — Wind threshold specificity:**
- "Sustained >8 m/s at altitude" — this is a reasonable threshold but should cite the airframe's spec sheet or a flight test observation. Currently unsourced

**LOW — Geofence misconfiguration contingency:**
- "Hardcoded fallbacks" for zone coordinates is mentioned but the hardcoded values should be documented somewhere (config.py presumably). Add a brief note about where they live

---

## Cross-Section Issues

### 1. Script count: 41 vs 58 (HIGH)
testing_deep.tex says 58 scripts across 8 categories. test_scripts_guide.tex says 41 across 6 categories. The missing categories (Unit, Automated) must either appear in the guide or be removed from the methodology section. This is the single most important fix.

### 2. Tier numbering inconsistency (HIGH)
Three different numbering schemes appear across sections:
- testing_deep.tex: Tiers 1-5 (SITL, Bench, Passive, Log-only, Full)
- test_scripts_guide.tex flight table: Tiers 3-5 (Bench=3, Passive=4, Auto=5)
- mission_flow.tex: No tier numbers, uses state names

The first two are contradictory. Standardise to ONE scheme throughout.

### 3. PLB redirect: target or stretch? (MEDIUM)
mission_flow.tex describes PLB redirect as part of normal operations. contingency.tex lists it under stretch goals. Pick one.

### 4. Search altitude: 30m or 35m? (MEDIUM)
mission_flow.tex uses 35m consistently. CLAUDE.md/config.py says TARGET_ALT=30. Verify and align.

### 5. Confidence threshold: 0.2 or 0.4? (MEDIUM)
mission_flow.tex says 0.2. CLAUDE.md says 0.4 (vision.py). The text says "deliberately low threshold" suggesting 0.2 is the intended flight value, but this should be explicit.

---

## Overall Assessment

| Section | Grade | Verdict |
|---------|-------|---------|
| Mission Flow | A- | Complete pre-flight to RTL. Quantitatively detailed. Minor altitude/threshold inconsistencies |
| Testing Methodology | A | Most compelling section. Empirical evidence, V-model mapping, cost gradient. Fix the 41/58 count |
| Field Day Narrative | A | Masterful reframing of cancelled flight as calibration success. Concrete outputs, no excuses |
| Test Scripts Guide | B+ | Good cataloguing but count discrepancy with methodology section is a credibility risk |
| Contingency Plans | A- | Realistic three-tier structure with test script mapping. PLB target/stretch ambiguity needs resolving |

### Top 5 Fixes (Priority Order)
1. **Reconcile 41 vs 58 script count** between testing_deep.tex and test_scripts_guide.tex
2. **Standardise tier numbering** across all sections (1-5 from testing_deep.tex should be canonical)
3. **Decide PLB redirect placement** — target deliverable or stretch goal, not both
4. **Verify search altitude** (30m vs 35m) and confidence threshold (0.2 vs 0.4) across all sections
5. **Fix Table~\ref{tab:bug-cost} cross-reference** (label mismatch with tab:bug-cost-appendix)
