# D7 Individual Reflective Report -- Scoring v6

> Scored against Appendix B rubric (Level 7) and AHEP4 standards.
> Previous scores: v1 (68/78/72), v2 (78/82/79), v3 (76/80/77), v4 (82/83/81), v5 (83/84/83).
> This scoring reflects the **trimmed version** (7pp -> 5pp) to assess what was lost.

---

## What Changed Since v5

The report was trimmed from ~7 pages to ~5 pages to meet the page limit. This is a
subtraction exercise: no new content was added. The question is whether the cuts
damaged any criterion.

### What Was Cut (Identified by Comparison with v5 Scoring Notes)

1. **Section 5.4 "Helping teammates develop"** -- REMOVED entirely. v5 noted this subsection
   was "one-directional" and asked "what would developmental feedback look like from this author?"
   The subsection was already flagged as incomplete, so its removal is not catastrophic, but it
   does eliminate the only place where "helping others grow" was explicitly discussed.

2. **The "once in twenty weeks" meta-reflection** -- RETAINED. Still present in Section 4,
   paragraph 2: "The state machine compromise was isolated" language is gone, but the single-
   compromise narrative is intact through the full story in the "Disagreements and compromise"
   paragraph. The quantitative self-diagnosis ("once in twenty weeks") is no longer explicit --
   **this is a loss**. The current text tells the story but does not step back to diagnose the
   pattern frequency.

3. **Development programme** -- RETAINED and intact (Section 5.4, now 5.3 equivalent). Three
   numbered actions with implementation evidence. Still lacks success metrics (same weakness as v5).

4. **Communication evaluation** -- The ground station evidence ("pilot navigated independently")
   is **RETAINED** in Section 4. The "one sentence, one diagram, one demo" framework is
   **RETAINED** in the development programme. However, the overall communication section feels
   compressed. No PDR/FDR evaluation was added (consistent with v5).

5. **Dual-use section** -- RETAINED in full (Section 3.3). The Ukrainian personal context,
   human-in-the-loop rationale, and MIT licence tension are all present. This was the strongest
   section in v5 and survives intact.

6. **Environmental impact** -- RETAINED including lifecycle gap acknowledgement ("rare-earth
   minerals in the Cube flight controller and lithium battery recycling"). Quantified CO2 and
   power comparisons survive.

---

## AHEP4 Standards Coverage Check

### M5 (Design with originality, diversity, inclusion, cultural, societal, environmental, commercial, codes of practice)

**Status: FULLY ADDRESSED**
- Originality: dual-backend architecture, simulation-first, inverse-variance weighting (Section 2.1)
- Diversity/inclusion: five nationalities, browser-based GS, lingua franca docs (Section 2.3)
- Cultural: Ukrainian background integrated throughout
- Societal: SAR application, accessible to volunteer teams (Sections 2.1, 3.1)
- Environmental: simulation replacing flights, low-power Pi (Section 3.2)
- Commercial: GBP60 Pi platform, cost barrier analysis (Sections 2.1, 3.1)
- Codes of practice: CAA regulations, SSSI geofencing (Sections 2.1, 2.2)

### M7 (Environmental and societal impact, entire life-cycle, minimise adverse impacts)

**Status: FULLY ADDRESSED**
- Environmental: CO2 quantification, power comparison, lifecycle gap acknowledged (Section 3.2)
- Societal: SAR benefits, accessibility, dual-use analysis (Sections 3.1, 3.3)
- Adverse impacts: surveillance risk, MIT licence, hardware safeguard proposals (Section 3.3)
- Life-cycle: explicitly acknowledged as incomplete with specific gaps named (Section 3.2)

### M16 (Function as individual and team member/leader, evaluate own and team performance)

**Status: ADDRESSED but slightly weakened**
- Individual function: clear throughout (software lead, 15k lines, systems integrator)
- Team member: Belbin roles, Edward collaboration, pilot training (Section 4)
- Leader: technical lead, de facto integrator (Section 4)
- Evaluate own performance: strengths/weaknesses in Section 5.3, "speed over inclusion" pattern
- Evaluate team performance: final paragraph of Section 4 ("five-person structure was suboptimal")
- **Weakened by removal of Section 5.4**: "helping others develop" is now only implicit through
  the numbered test scripts and documentation efforts mentioned in passing. No explicit reflection
  on whether the author's approach to developing teammates was corrective vs developmental.

### M17 (Communicate effectively, evaluate effectiveness of methods)

**Status: ADDRESSED but remains the weakest standard**
- Communication methods: simulator as communication device, ground station, documentation (Section 4)
- Effectiveness evaluation: pilot navigated independently (Section 4) -- this is the only concrete
  evidence of evaluated effectiveness
- Technical vs non-technical: browser GS for non-technical operators, API for technical (implicit)
- **Still missing**: PDR/FDR reflection, explicit audience adaptation analysis, communication
  cadence evaluation. v5 flagged this as the weakest standard; the trim did not improve it but
  also did not significantly damage it since the gaps were already present.

**Verdict: All 4 AHEP4 standards are still explicitly addressed. M16 slightly weakened, M17
unchanged (still the weakest).**

---

## Reflective vs Descriptive Check

The report maintains its reflective character. Key markers:

- **Kolb's cycle applied to own behaviour** (Section 4): "optimised for output over team development"
- **Cultural root cause** (Section 5.3): "Ukraine's engineering culture prizes individual competence"
- **Honest admission** (Section 4): "I bear primary responsibility" for teammate frustration
- **Limitation of own safeguards** (Section 3.3): "removing the verification prompt is a single-line code change"
- **Self-diagnosis** (Section 5.3): "speed over inclusion" as strength-weakness duality
- **Career framing** (Section 5.4): connects project lessons to Ukraine's needs

The trim has NOT made the report more descriptive. If anything, cutting weaker descriptive
material has improved the ratio of reflection to description. The remaining text is dense with
evaluative and self-critical content.

---

## "Helping Teammates Develop" Coverage

**After Section 5.4 removal:**
- The concept is still present but dispersed:
  - Section 4: "I attempted to lower the barrier with numbered test scripts and documentation"
  - Section 4: pilot walkthrough + independent navigation evidence
  - Section 4: "contribution points must be designed in from the start, not retrofitted"
  - Section 5.4 (dev programme): "define contribution points and interface contracts before implementation"
- What is LOST: the explicit framing of "did I help my teammates grow as engineers?" as a question.
  The current text addresses "did I make the system accessible?" but not "did I develop people?"
- **Impact: -1 on M16.** The distinction between "lowering barriers to contribution" and
  "investing in teammate development" was already noted as weak in v5. Its removal means the
  report no longer even attempts to address it.

---

## Rubric Criteria Scores

### 1. Teamwork (M16) -- Score: 82/100 (-1 from v5's 83)

**What survives from v5:**
- Belbin framework with honest self-assessment (Specialist + Completer-Finisher)
- Edward collaboration as strongest sub-team example
- Teammate frustration acknowledged with ownership ("I bear primary responsibility")
- State machine compromise: full story of changing direction based on team input
- Pilot training → independent navigation arc
- Team effectiveness evaluation (final paragraph)

**What was lost:**
- "Once in twenty weeks" quantitative self-diagnosis on compromise frequency. The story survives
  but the meta-reflection on its rarity does not.
- Section 5.4's explicit "helping others develop" framing

**Why -1:**
The "once in twenty weeks" quantification was the most intellectually interesting addition in v5.
Its loss removes the step-back moment where the author evaluates their own evidence base. The
compromise story is still strong, but without the meta-commentary it reads as a positive example
rather than a diagnostic one. The removal of explicit "developing teammates" language costs a
fraction more on M16's "evaluate own and team performance" requirement.

**What would restore it (+1-2):**
Add back one sentence to the compromise paragraph: "This was the one time in twenty weeks I
genuinely changed direction based on team input -- a ratio that reveals collaborative decision-
making is still my exception rather than my norm." (30 words, +1 M16, +1 Insight)

---

### 2. Self-Management (M17) -- Score: 83/100 (-1 from v5's 84)

**What survives from v5:**
- Time management structure (weekly milestones, CLAUDE.md tracking, version control)
- Self-management failure: Pi deployment underestimation, Docker test as correction
- Strengths/weaknesses: rapid prototyping vs speed-over-inclusion, visual vs verbal communication
- Development programme with 3 actions + partial implementation evidence
- Cultural root cause of speed-over-inclusion pattern

**What was lost:**
- Some compression in the self-assessment section. The dual strength-weakness analysis survives
  but feels slightly rushed.

**Why -1:**
The trim compressed Section 5 overall. While all major points survive, the breathing room
around the self-assessment is reduced. The development programme's lack of success metrics
(already a v5 weakness) becomes more noticeable in the shorter version because there is less
surrounding context to carry the reader. M17's "evaluate effectiveness of methods" sub-criterion
is addressed only by the pilot navigation evidence -- still just one data point.

**What would restore it (+1):**
Add a success metric to development programme item 3: "measured by whether teammates can
independently modify a module I wrote within one sprint" (15 words, +0.5 M17). Or add a
sentence on adapting communication for the project manager vs the pilot (audience adaptation,
+0.5 M17).

---

### 3. Insight (M5/M7) -- Score: 82/100 (-1 from v5's 83)

**What survives from v5:**
- Root cause excavation: Ukrainian engineering culture → speed-over-inclusion
- "Ongoing adjustment, not a one-time insight" metacognitive marker
- Dual-use section with personal Ukrainian context (strongest insight in the report)
- Lifecycle gap acknowledgement (self-aware about analysis boundaries)
- Design decisions explicitly linked to values (human-in-the-loop, accessibility, safety)

**What was lost:**
- "Once in twenty weeks" as quantitative self-diagnosis. This was scored as the "most
  intellectually interesting addition" in v5 and contributed +1 to Insight. Its removal
  is felt here.
- The explicit "helping others develop" reflection, which demonstrated the ability to
  evaluate one's impact on others' growth

**Why -1:**
The "once in twenty weeks" loss reduces the report's use of quantitative thinking applied
to personal behaviour -- a technique v5 specifically praised as "the same analytical instinct
applied to GPS drift and CO2 emissions, now turned inward." Without it, the self-assessment
is still strong but slightly less distinctive. The report still has excellent insight in the
dual-use section and cultural root cause, but the loss of this particular analytical move
drops it from 83 to 82.

**What would restore it (+1-2):**
Same sentence suggested under M16: the "once in twenty weeks" ratio. This single sentence
would restore both M16 and Insight scores.

---

## AHEP4 Standards Scores

| Standard | v5 | v6 | Delta | Notes |
|----------|-----|-----|-------|-------|
| M5 (Design/originality) | 82 | **82** | 0 | Unaffected by trim |
| M7 (Environmental/societal) | 81 | **81** | 0 | Lifecycle acknowledgement retained |
| M16 (Team effectiveness) | 81 | **80** | -1 | "Once in twenty weeks" + Section 5.4 lost |
| M17 (Communication) | 82 | **81** | -1 | Slight compression, still weakest standard |

---

## Composite Scores

| Criterion | v1 | v2 | v3 | v4 | v5 | v6 | Delta v5->v6 | Band |
|-----------|-----|-----|-----|-----|-----|-----|-------------|------|
| Teamwork (M16) | 68 | 78 | 76 | 82 | 83 | **82** | -1 | First (78-83 sub-band) |
| Self-management (M17) | 78 | 82 | 80 | 83 | 84 | **83** | -1 | First (83-85 sub-band) |
| Insight (M5/M7) | 72 | 79 | 77 | 81 | 83 | **82** | -1 | First (83-85 sub-band) |

**Overall estimated D7 mark: 82-83** (down from v5's 83-84)

---

## What Was Lost in Trimming -- Priority Recovery List

If you can recover ~50 words anywhere in the report, here is what to add back in
priority order:

### Priority 1: "Once in twenty weeks" ratio (30 words, +1 M16, +1 Insight)
Add to Section 4, after the state machine compromise story:
> "This was the one time in twenty weeks I changed technical direction based on team
> input---a ratio that reveals collaborative architecture remains my exception, not my norm."

This single sentence was the highest-value-per-word addition in v5 and its loss accounts
for most of the v5->v6 score drop.

### Priority 2: Teammate development sentence (20 words, +0.5 M16)
Add to Section 4, near "contribution points must be designed in":
> "I lowered barriers to contribution but did not invest in developing teammates'
> technical skills---a distinction I now recognise."

### Priority 3: Communication success metric (15 words, +0.5 M17)
Add to development programme item 3:
> "---measured by whether a teammate can independently modify a module I wrote within one sprint."

### Priority 4: Audience adaptation (20 words, +0.5 M17)
Add to Section 4, communication paragraph:
> "For the project manager, I replaced technical language with outcome-focused summaries;
> for the pilot, hands-on bench walkthroughs."

Total recovery: ~85 words, potential +2-3 points, back to v5 levels or slightly above.

---

## Assessment Summary

### The trim was mostly well-executed.

The 5-page version retains all the strongest elements:
- Dual-use section with personal Ukrainian context (best section in the report)
- Cultural root cause of speed-over-inclusion
- State machine compromise story
- Ground station effectiveness evidence
- Environmental quantification with lifecycle acknowledgement
- Safety-critical design rationale

### The damage is real but recoverable.

The ~2 point drop comes from losing two specific high-value elements:
1. The "once in twenty weeks" quantitative self-diagnosis (60% of the loss)
2. The "helping teammates develop" explicit framing (40% of the loss)

Both can be recovered with ~50 words total (Priority 1 + Priority 2 above).

### The report still feels reflective.

The trim did not introduce descriptive padding or remove reflective depth. The ratio of
reflection to description has actually improved because weaker descriptive material was
cut before stronger reflective material. The dual-use section, cultural root cause, and
compromise story -- the three pillars of the report's reflective quality -- all survive
intact.

### Realistic ceiling for the trimmed version: 83-84 with recovery additions, 82-83 without.

The structural maximum of this report (given a cancelled flight day and a 5-page limit)
remains ~85. The v6 trim puts it 2-3 points below that ceiling. The recovery additions
would close the gap to ~1 point.

---

## Final Recommendation

Add back Priority 1 ("once in twenty weeks" ratio, 30 words). This is the single
highest-ROI edit available. It restores the most intellectually distinctive element
of v5, addresses both M16 and Insight simultaneously, and fits in a single sentence
at the end of the compromise paragraph in Section 4.

If space permits, add Priority 2 (teammate development, 20 words) and Priority 3
(success metric, 15 words). Together these 65 words would restore the report to
v5 levels (83-84) within the 5-page constraint.
