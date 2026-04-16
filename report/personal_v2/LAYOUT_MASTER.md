# D7 Main Body — Master Layout (Orchestrator Plan)

**Target:** 7-9 pages working draft, cut to 5 at the end.
**Structure:** 4 required headings (My role / My team / My impact / My support) + 10 mandatory sub-questions.
**Framework overlay:** WWW/EBI top-level + STAR per anecdote + 1 Kolb deep-dive + Schön label once.
**Voice:** First person, short sentences, named things. Honest, not performative.

---

## Page 1 — Cover slot (free)

Handled separately by cover_page.tex. Not counted.

Title block, author, student ID, team, date, 4-line stance epigraph, word count.

---

## §1 — My role (pages 1-2 of body)

Answers Q1a, Q1b, Q1c. ~1.5-2 pages.

### Slot S-1a: Roles allocated vs taken (~0.5 pp)
**Question:** What were your roles and responsibilities? Which were explicitly allocated vs taken on implicitly? Did they change?
**Evidence bank:**
- Explicit allocation at wk12 kickoff: [PLACEHOLDER — what was Apollo's formal role?]
- Implicit takes over time: simulation framework, safety layer, report writing, blueprint system, teammate script polishing, complaint letter drafting
- The "mission creep" pattern — show the progression wk12 → wk16 → wk22
**Hatton L4 move:** "I now see the drift from CV lead to 'everything infrastructure' happened because X, not because I wanted more work"

### Slot S-1b: Most proud of (~0.5-0.75 pp)
**Question:** What elements of your contribution are you most happy about / proud of?
**Evidence bank:**
- Complaint-letter thesis: "The simulation framework we created ourselves is the only reason this project produced any verifiable engineering output at all"
- 820+ commits across 3 failed flight days (resilience)
- One specific incident: [PICK ONE] — e.g. IMX296 BGR discovery, main.py 1411→754 refactor, or undistortion pipeline fix
- Why this particular thing: the Hatton L4 reframing — "I'm proud of X because it represents Y that I didn't have before"
**Avoid:** list-of-achievements. ONE specific thing with reasoning.

### Slot S-1c: Focus differently in future (~0.5 pp)
**Question:** What different things might you focus on in your future work?
**Evidence bank:**
- Less solo, more pair-programming / teaching
- Earlier explicit structure discussion (saw the need wk17, should have seen it wk12)
- Less "capability" mode, more "enablement" mode
- Named future skill: pair programming, async team coordination, documentation-as-teaching
**Hatton L4 move:** name a specific future situation (a job, a team project next year) where you'd apply the lesson

---

## §2 — My team (pages 2-4 of body)

Answers Q2a, Q2b, Q2c. ~1.5-2 pages.

### Slot S-2a: Team structure — discussed explicitly? Changed? (~0.5 pp)
**Question:** How was your team structured? Was this discussed explicitly? What changed?
**Evidence bank:**
- wk12 kickoff — [PLACEHOLDER: was structure explicitly discussed?]
- Role allocation format: slides? brain-dump? informal?
- How Robin → Demetro → Edward → PM → pilot fell into their slots
- Mid-project structural shift: what changed at wk17 / wk20?
**Hatton L4 move:** "Looking back, I now see we optimised for task division over communication patterns, which X"

### Slot S-2b: Most impactful team-working elements (~0.75 pp)
**Question:** What elements of team working were most impactful on your outputs?
**Evidence bank:**
- Robin CV integration — what enabled it (handoff docs? real-time chat? in-person sessions?)
- Demetro FDR collaboration — speaking scripts polished 4-5 times
- Edward Cube debugging — synchronous bench sessions
- Field day pivoting — team response to weather cancellation
- **THIS IS THE "WHAT WENT WELL" ZONE** — use WWW tag explicitly
**Insight slot:** What single team-working element would you CALL OUT as making/breaking the project?

### Slot S-2c: What would you change next time (~0.5 pp)
**Question:** What would you change if you were to do a similar project in future?
**Evidence bank:**
- Explicit structure discussion in wk1 (not wk12)
- Pair programming days scheduled from the start
- Earlier commitment to a shared "truth" document (we ended up with CLAUDE.md but that took weeks)
- A weekly sync format that wasn't just status — a reflection round
- **THIS IS THE "EVEN BETTER IF" ZONE** — use EBI tag explicitly
**Forward-looking:** make it concrete, not abstract

---

## §3 — My impact (pages 4-6 of body)

Answers Q3a, Q3b. ~1.5-2 pages.

### Slot S-3a: How did YOUR contributions drive the team forward? (~1-1.25 pp)
**Question:** How did your contributions drive the team forward and contribute to success?
**Evidence bank (6-8 concrete items — pick the 4 strongest):**
1. **Simulation framework** — unblocked testing despite 3 failed field days
2. **Main.py refactor** — 1411 → 754 lines, 6 modules, 146 pytest tests
3. **Progressive test ladder** — tests/flight/0a → 4, 127 unit tests
4. **Demetro FDR scripts** — polished 4-5 times, helped teammate present confidently
5. **Robin CV integration** — cv_mode polling, passive_watch_2, handoff docs
6. **Modularity audit** (3.8/5.0) + capability audit (2.1/10) — honest self-assessment others could use
7. **Goldmine + reportflow writing** — 74 → 88 across ~60 agent iterations
8. **Complaint letter** — drafted for group benefit, factual tone, got the point across

**Best form for this slot:** Kolb deep-dive ONE story (simulation framework thesis) + STAR-compact for 3 others.
**Kolb stages to name (in italics):** *Experience* (3 failed flight days), *Reflect* (noticed team was idle waiting), *Conceptualise* (simulator with real-drone parity via vision.py dual backend), *Experiment* (6 weeks of testing without a physical drone).

### Slot S-3b: Add / refocus in future (~0.5 pp)
**Question:** What might you add or re-focus on in future projects?
**Evidence bank:**
- From "building tools I need" → "building tools the team needs"
- From solo refactoring → pairing on refactor reviews
- From "I'll just fix this" → teaching the teammate who owns it
- From technical leadership → inclusive leadership
**Hatton L4 move:** name a mechanism — not a wish. E.g. "I would schedule 2hrs/week of explicit teaching sessions, measured by the teammate completing a handoff task independently within 48hrs"

---

## §4 — My support (pages 6-8 of body)

Answers Q4a, Q4b. ~1.5-2 pages.

### Slot S-4a: What did others do that helped you? (~0.75 pp)
**Question:** What did other team members do that helped you work more effectively?
**Evidence bank (name each teammate + specific help):**
- **Edward** — Cube debugging, solved the pyserial Python 3.13 issue with mavproxy bridge insight
- **Robin** — [PLACEHOLDER: specific CV/detection help]
- **Demetro** — domain knowledge on [PLACEHOLDER]
- **Pilot** — operated ground station solo on field day
- **Project manager** — [PLACEHOLDER: specific admin / budget / communications]
- **Supervisor** — [PLACEHOLDER: specific academic guidance]
**Hatton L4 move:** name ONE specific thing a teammate did that CHANGED YOUR THINKING — not just unblocked a task. E.g. "Edward's reminder that 'just because the test passes doesn't mean the hardware does' reframed how I thought about simulation fidelity."

### Slot S-4b: What did YOU do to help others? (~0.75-1 pp)
**Question:** What actions did you take that helped other individuals and/or the team as a whole work more effectively?
**Evidence bank (CRITICAL — this is the 72+ Insight gate):**

**Feedback given to named teammates with observed behaviour change:**
1. **Demetro** — revised FDR speaking script 4-5 times; he said "I feel confident presenting now" (or similar) — specific change in confidence
2. **Robin** — wrote handoff docs for CV integration → Robin integrated main.py without asking questions for 2 days
3. **Pilot** — proposed button layout on ground station → pilot operated it unaided on field day
4. **PM** — [PLACEHOLDER: feedback on documentation / workload]
5. **Complaint letter** — drafted for group benefit, not personal — team signed on, letter sent

**Tools/infrastructure built for others' use:**
- brain-dump.md / MEMORY.md / NICE_TO_HAVE.md — captured institutional memory
- Blueprint system for large files — prevented rescanning
- CLAUDE.md project ground truth — onboarding for new sessions
- Simulator with web ground station — let teammates test without the drone
- Progressive test ladder — gave pilot/hardware-lead confidence before flight

**Hatton L4 move:** "I now see that building tools for others was my version of teamwork because I struggled with real-time collaboration; future me should invest in the harder skill even though it feels less productive."

---

## Global threads to weave through all 4 sections

1. **The honest solo-led thesis** — don't hide from it. Own it. Reflect on WHY.
2. **Complaint letter as evidence of group-first action** — reference in §1b or §4b
3. **The Ukraine engineering culture** angle — could go in §1c ("what I'd focus on differently — I came in with a Ukrainian engineering mindset of 'one person delivers', and the project taught me Western team engineering is different")
4. **The "castle while the town starved" self-criticism** — powerful phrase from the existing V1 draft, keep it
5. **3 dated events must be weeks + 3 must be specific sessions** (e.g. wk12, wk17, wk20, 2026-03-11, 2026-03-30, 2026-04-03)

---

## Fill order (orchestrator dispatch plan)

I'll dispatch an agent per slot in parallel where possible. Each agent:
- Gets the slot spec above
- Reads D7_SCORING_FINAL.md for rubric
- Reads D7_RAW_MATERIAL.md for specifics
- Reads D7_EXEMPLARS.md for Hatton Level 4 templates
- Returns a LaTeX paragraph (~150-250 words)
- Uses placeholders where info is missing

Wave plan:
- **Wave 2a (parallel):** S-1a, S-1b, S-1c, S-2a, S-2b, S-2c, S-3a, S-3b, S-4a, S-4b — 10 slot-writer agents
- **Wave 2b (serial after 2a):** 1 assembler agent that stitches slots into 4 section files + compiles
- **Wave 2c (serial):** 1 scorer + 1 critic — check if all 10 slots are at Hatton L4

Estimated total: ~13 agents. Expected result: 7-9 pages working draft, all 10 questions answered with Hatton L4 depth.

Then HITL #1 (user reviews, fills placeholders) → refine loop (max 3 iterations) → HITL #2 → final polish → cut to 5 pages.
