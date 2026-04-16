# PP EXPANDED -- Team Development (Tuckman + Surrounding Concepts)

**Source:** `professional_practice/team_development/TUCKMAN_COMPLETE.md`
**Extracted:** 2026-04-16
**Purpose:** Every actionable concept beyond "Tuckman has 5 stages," with D7 mapping for Apollo.

---

## Extraction Format

```
{id, pri, name, src, sections, how, quote, ref}
```

- **pri**: must (essential for 70+), should (needed for 78), could (polish/distinction edge), skip (not relevant to D7)
- **sections**: D7 section where Apollo deploys it (1a-4b)
- **how**: concrete sentence Apollo writes

---

## A. Stage-Specific Emotions / Behaviours / Tasks

```
{
  id: TD-01,
  pri: must,
  name: "Forming -- dependency, politeness, anxiety, looking for leadership",
  src: TUCKMAN_COMPLETE.md Section 5,
  sections: [2a, 2b],
  how: "Map Wk12 kickoff to Forming: polite role allocation, lots of questions,
        no clear understanding of the problem yet. Apollo was looked to for
        technical direction (dependency). Use to argue Forming was too brief.",
  quote: "People will be very polite and show some goodwill to others...
          Trust will be limited and there will be a mix of excitement and anxiety",
  ref: "(Tuckman, 1965)"
}
```

```
{
  id: TD-02,
  pri: must,
  name: "Storming -- rivals compete, politeness drops, underground conflict risk",
  src: TUCKMAN_COMPLETE.md Section 6,
  sections: [2a, 2b, 2c, 4a],
  how: "Map Wk17 FSM conflict + Wk20 workload tensions. Show 'individual
        differences and ways of working start to be pronounced.' Cite the
        specific architecture disagreement (monolithic vs modular) as evidence.
        Acknowledge democratic approaches pushed issues underground initially.",
  quote: "Levels of politeness drop as individuals start to realise that the
          clock is ticking... Sometimes this can result in conflict",
  ref: "(Tuckman, 1965)"
}
```

```
{
  id: TD-03,
  pri: should,
  name: "Norming -- sense of belonging, own culture/in-jokes, constructive criticism",
  src: TUCKMAN_COMPLETE.md Section 7,
  sections: [2a, 2b],
  how: "Evidence Norming via: handoff docs created, Robin integration smooth,
        Git workflow became second nature, constructive code review became welcome.
        Mention team in-jokes or shared vocabulary if any existed.",
  quote: "A team starts to develop its own culture, possibly with its own
          language and its own in-jokes",
  ref: "(Tuckman, 1965)"
}
```

```
{
  id: TD-04,
  pri: should,
  name: "Performing -- fluidity, differences become useful, roles shift naturally",
  src: TUCKMAN_COMPLETE.md Section 8,
  sections: [2a, 3a],
  how: "Be honest: did we reach Performing? If yes, cite the field day where
        roles became fluid (Apollo ran software, others handled hardware,
        tasks moved naturally). If no, say so -- L4 honesty scores higher
        than L3 pretence.",
  quote: "Roles may become much more fluid. Moving work around becomes quite
          natural... Differences between team members become useful rather
          than troublesome",
  ref: "(Tuckman, 1965)"
}
```

```
{
  id: TD-05,
  pri: could,
  name: "Transforming / Adjourning -- loss, mourning, knowledge capture",
  src: TUCKMAN_COMPLETE.md Section 9,
  sections: [1c, 3b],
  how: "Use in future-looking sections: 'In future projects I would invest
        more in the Transforming stage -- capturing lessons learned and
        documenting institutional knowledge before the team disbands.'
        Reference the grief-like emotions if the team felt the 'sense of loss'
        about never flying autonomously.",
  quote: "When you've invested years of your life into a project and someone
          pulls the plug on it, it can be really painful",
  ref: "(Tuckman and Jensen, 1977)"
}
```

---

## B. Team Regression (Going Backwards)

```
{
  id: TD-06,
  pri: must,
  name: "Team regression -- undevelopment, moving right-to-left",
  src: TUCKMAN_COMPLETE.md Section 11,
  sections: [2a, 2c],
  how: "Map flight cancellations to regression: team was Norming, weather
        cancelled flights, trust in timeline eroded, roles needed re-clarification,
        new storming around schedule pressure. This is THE L4 move --
        showing the model is non-linear from lived experience.",
  quote: "You can go from right to left. Certainly your team could undevelop.
          This might happen if... your project changes so significantly that
          your team is thrown back a few stages in its development.",
  ref: "(Tuckman, 1965; lecture)"
}
```

```
{
  id: TD-07,
  pri: should,
  name: "Regression triggers -- 6 specific causes",
  src: TUCKMAN_COMPLETE.md Section 11 (list),
  sections: [2a, 2c],
  how: "Cite which triggers hit your team: (1) new member joins (Robin mid-project),
        (3) project scope changes (flight day cancellations changed deliverables),
        (5) external pressure (weather, hardware delays). Each trigger maps to
        a specific regression episode.",
  quote: "New members bring their own working style, temporarily disrupting
          established norms",
  ref: "(Tuckman, 1965; lecture)"
}
```

---

## C. Artificial Harmony / "Violently Agreeing"

```
{
  id: TD-08,
  pri: must,
  name: "Violently agreeing = artificial harmony = skipped Storming",
  src: TUCKMAN_COMPLETE.md Section 12,
  sections: [2b, 2c, 4a],
  how: "Ask: did the team violently agree at any point? If yes, flag it as
        a weakness -- 'With hindsight, our early consensus on X may have been
        artificial harmony rather than genuine agreement. Tuckman warns that
        violently agreeing suggests absent diversity of thought.' If no,
        use as evidence of healthy Storming.",
  quote: "You might find that you breeze through because you as a team, you
          naturally gel with each other and you're all violently agreeing with
          each other all the time. Be careful of that.",
  ref: "(Tuckman, 1965; lecture)"
}
```

```
{
  id: TD-09,
  pri: should,
  name: "True Norming = resolved conflict, not absent conflict",
  src: TUCKMAN_COMPLETE.md Section 12 (final line),
  sections: [2b],
  how: "Distinguish between 'we never argued' (bad -- artificial harmony)
        and 'we argued, resolved it, and moved on' (good -- genuine Norming).
        Apollo should show which one the team did.",
  quote: "True Norming involves resolved conflict, not absent conflict.",
  ref: "(TUCKMAN_COMPLETE.md synthesis)"
}
```

---

## D. Timeline Scenarios (Best / Probable / Worst)

```
{
  id: TD-10,
  pri: should,
  name: "Best-case timeline -- short F+S, long Performing (very rare)",
  src: TUCKMAN_COMPLETE.md Section 10,
  sections: [2a, 2c],
  how: "State that project plans are implicitly built on best-case Tuckman
        (short Storming). Acknowledge this was naive. In future, budget
        explicitly for Storming time in Gantt charts.",
  quote: "This is what all project managers will optimistically base their
          timing plans on... very, very rare",
  ref: "(Tuckman, 1965; lecture)"
}
```

```
{
  id: TD-11,
  pri: must,
  name: "Worst-case timeline -- too little Forming, jump to Storming, restart",
  src: TUCKMAN_COMPLETE.md Section 10,
  sections: [2a, 2c],
  how: "Map to team: 'Our Wk12 kickoff may have been too brief, matching
        Tuckman's worst-case scenario where too little Forming means no trust
        foundation, leading to extended Storming.' This is high-value L4.",
  quote: "Too little time spent forming, which means no building of trust in
          the team, no discussion of its aims or its goals, and just jumping
          straight into the storming phase",
  ref: "(Tuckman, 1965; lecture)"
}
```

```
{
  id: TD-12,
  pri: could,
  name: "Probable timeline -- compressed Performing due to long F+S",
  src: TUCKMAN_COMPLETE.md Section 10,
  sections: [2a],
  how: "Use as a realistic benchmark: 'Our trajectory most closely matched
        the probable case -- extended Forming and Storming compressed our
        Performing window to perhaps 2-3 weeks.'",
  quote: "Forming and storming stages are longer and that has the effect of
          compressing the performing aspect",
  ref: "(Tuckman, 1965; lecture)"
}
```

---

## E. Extroverts vs Introverts

```
{
  id: TD-13,
  pri: should,
  name: "Extroverts speak-to-think vs introverts think-to-speak",
  src: TUCKMAN_COMPLETE.md Section 1 (Drawbacks table),
  sections: [2b, 2c, 4a, 4b],
  how: "If team had both types: 'I noticed that some members processed ideas
        verbally during meetings while others needed time to reflect before
        contributing. In future, I would circulate agendas beforehand and
        allow async written input -- accommodating what Graham calls the
        difference between extroverts who speak to think and introverts who
        think to speak.'",
  quote: "Extroverts speak to think... introverts tend to think to speak --
          these differences might require differences in the way that the
          team is run",
  ref: "(lecture, Mark Graham)"
}
```

---

## F. Groupthink / Echo Chamber

```
{
  id: TD-14,
  pri: should,
  name: "Groupthink -- echo chamber from recruiting clones",
  src: TUCKMAN_COMPLETE.md Section 1 (Drawbacks table),
  sections: [2b, 2c],
  how: "Evaluate: did the team have genuine intellectual diversity? Were
        different approaches seriously considered, or did one person's view
        dominate? 'Graham warns that groupthink arises from teams that lack
        intellectual diversity -- in our case, [evidence for/against].'",
  quote: "Being surrounded by people who think just like you creates an
          echo chamber and the problem of groupthink",
  ref: "(lecture, Mark Graham)"
}
```

---

## G. Dominant Personalities

```
{
  id: TD-15,
  pri: must,
  name: "Dominant personalities exerting unequal impact -- possibly you",
  src: TUCKMAN_COMPLETE.md Section 1 (Drawbacks table),
  sections: [1a, 1b, 2b, 4a],
  how: "Apollo must self-reflect: 'As the primary software developer, I may
        have been the dominant personality Graham warns about -- exerting
        unequal impact on technical decisions. He notes this dominant
        character might even be you. In hindsight, I could have created
        more space for others to contribute architecturally.'
        This is HIGH-VALUE L4 -- self-aware critique of own dominance.",
  quote: "Dominant personalities in the group exerting an unequal impact on
          the outcomes. Possibly that dominant character might even be you",
  ref: "(lecture, Mark Graham)"
}
```

---

## H. Diffusion of Responsibility (Hiking Analogy)

```
{
  id: TD-16,
  pri: should,
  name: "Diffusion of responsibility -- nobody reading the map",
  src: TUCKMAN_COMPLETE.md Section 1 (Drawbacks table),
  sections: [2b, 3a, 4a],
  how: "Apply to project management tasks: 'Graham's hiking analogy -- where
        everyone relied on the group to manage the risk and no one realised
        no one was reading the map -- resonates with our early weeks where
        integration testing was assumed to be someone else's job.' Or apply
        to any task that fell through the cracks.",
  quote: "People were relying on the group to manage the risk and no one
          realised that no one else was reading the map either",
  ref: "(lecture, Mark Graham)"
}
```

---

## I. Collective Courage / Safety in Numbers

```
{
  id: TD-17,
  pri: could,
  name: "Collective courage -- teams attempt what individuals would not",
  src: TUCKMAN_COMPLETE.md Section 1 (Benefits table),
  sections: [1b, 3a],
  how: "Use positively: 'The scope of our project -- autonomous SAR with
        onboard AI, GPS estimation, and real-time decision-making -- would
        have been impossible for any individual. The team provided what
        Graham calls collective courage: safety in numbers that enabled us
        to attempt challenges no individual would consider alone.'",
  quote: "Teams will often undertake challenges that no individual would
          consider doing alone",
  ref: "(lecture, Mark Graham)"
}
```

---

## J. Democratic Approach Weakness

```
{
  id: TD-18,
  pri: should,
  name: "Democratic weakness -- popular != good",
  src: TUCKMAN_COMPLETE.md Section 1 (Drawbacks table),
  sections: [2b, 2c],
  how: "If a team decision was made by vote/consensus that turned out suboptimal:
        'Our decision to [X] was reached democratically, but Graham warns
        that solutions converged upon by average approval are not necessarily
        the best available. In future, I would advocate for evaluating ideas
        on technical merit rather than popularity.'",
  quote: "Just because it's popular doesn't make it good or right",
  ref: "(lecture, Mark Graham)"
}
```

```
{
  id: TD-19,
  pri: could,
  name: "Underground conflict from democratic peacekeeping",
  src: TUCKMAN_COMPLETE.md Section 6,
  sections: [2b, 2c],
  how: "If the team used voting/consensus to avoid confrontation: 'Democratic
        approaches to find peace can push issues underground rather than
        actually addressing them. Our Wk17 compromise on [X] may have done
        exactly this.'",
  quote: "Teams might just try to find some democratic approaches to find
          peace, but this can often just push issues underground rather than
          actually addressing them",
  ref: "(Tuckman, 1965; lecture)"
}
```

---

## K. Team Time Allocation Model

```
{
  id: TD-20,
  pri: should,
  name: "Team time allocation -- 4 scenarios (alone/typical/poor/ideal)",
  src: TUCKMAN_COMPLETE.md Section 2,
  sections: [2b, 2c, 3b],
  how: "Self-assess which scenario the team matched: 'Graham's time allocation
        model shows that poor teams spend >50% of time on management. During
        our Storming phase, this was us -- meetings consumed more time than
        coding. By Norming, we shifted toward the ideal, where invested
        management time reduced future overhead.'",
  quote: "Teams that invest in managing themselves well will have to spend
          less time managing themselves in the end",
  ref: "(lecture, Mark Graham)"
}
```

```
{
  id: TD-21,
  pri: must,
  name: "The irony -- teams that skip management spend MORE time managing",
  src: TUCKMAN_COMPLETE.md Section 2 (key insight),
  sections: [2b, 2c],
  how: "This is a KILLER insight for D7: 'Graham identifies an irony: teams
        that skip management discussions end up spending even more time
        managing. Early in the project, we resisted structured processes,
        but this created confusion that consumed more time than the processes
        would have. I would now advocate for early investment in team processes.'",
  quote: "Teams that don't bother to think about how they work, possibly
          because they hate talking about management, will have to spend
          even more time trying to manage the team.",
  ref: "(lecture, Mark Graham)"
}
```

---

## L. Worker vs Mid-Manager vs Senior Manager Time Split

```
{
  id: TD-22,
  pri: could,
  name: "Worker 85% technical / mid-manager 50-50 / senior manager almost 0% technical",
  src: TUCKMAN_COMPLETE.md Section 2,
  sections: [1a, 1c],
  how: "Use for career reflection in 1c: 'Graham's worker-to-manager spectrum
        shows that as engineers progress, technical work shrinks. Having
        experienced the mid-manager split during this project -- balancing
        my own CV development with coordinating team integration -- I now
        understand his warning that forced detachment from technical work
        can be too much to bear.'",
  quote: "As a senior manager... it can often feel like you never get to work
          on your own work. The reality is that the team's work is your work.",
  ref: "(lecture, Mark Graham)"
}
```

```
{
  id: TD-23,
  pri: could,
  name: "Engineering-to-management transition pain",
  src: TUCKMAN_COMPLETE.md Section 2 (final warning),
  sections: [1c],
  how: "Future reflection: 'Graham warns that the forced detachment from
        technical work -- the reason why you entered engineering -- can be
        too much to bear long-term. This resonates with my experience:
        I found the coordination aspects less satisfying than the coding,
        which is something to consider for my career path.'",
  quote: "The forced detachment from the technical work which might have been
          the reason why you entered engineering, can be too much to bear
          in the long term.",
  ref: "(lecture, Mark Graham)"
}
```

---

## M. "Teams That Invest in Managing Themselves..."

```
{
  id: TD-24,
  pri: must,
  name: "Investment paradox -- manage well now = manage less later",
  src: TUCKMAN_COMPLETE.md Section 2 (ideal team),
  sections: [2c, 3b, 4a],
  how: "Use as THE takeaway for 'what I'd do differently': 'The single most
        transferable lesson is Graham's investment paradox: teams that invest
        in managing themselves spend less time managing. In future, I would
        front-load team process discussions -- ground rules, communication
        norms, conflict resolution protocols -- even when the team resists,
        knowing this pays dividends later.'",
  quote: "Teams that invest in managing themselves well will have to spend
          less time managing themselves in the end",
  ref: "(lecture, Mark Graham)"
}
```

---

## N. Tuckman Model Limitations (Critical L4)

```
{
  id: TD-25,
  pri: must,
  name: "Limitation: original study was therapy groups, not engineering teams",
  src: TUCKMAN_COMPLETE.md Section 17 (#1),
  sections: [2a, 2c],
  how: "L4 CRITICAL move: 'Tuckman's model was derived from therapy group
        literature, which he himself admitted cannot be considered truly
        representative of small-group developmental processes (Tuckman, 1965,
        p.384). Its applicability to a time-bounded MSc engineering project
        with pre-assigned members is debatable.'",
  quote: "Tuckman reviewed literature on therapy groups... he admitted the
          literature cannot be considered truly representative",
  ref: "(Tuckman, 1965, p.384)"
}
```

```
{
  id: TD-26,
  pri: must,
  name: "Limitation: linearity assumption -- real teams oscillate",
  src: TUCKMAN_COMPLETE.md Section 17 (#2),
  sections: [2a],
  how: "L4 CRITICAL move: 'The model implies sequential progression, but our
        experience was cyclical -- we regressed after flight cancellations.
        This supports Bonebright's (2010) critique that real teams oscillate
        between stages rather than progressing linearly.'",
  quote: "The model implies sequential progression, but real teams oscillate.
          Tuckman acknowledged this but the model's visual representation
          encourages linear thinking",
  ref: "(Tuckman, 1965; Bonebright, 2010)"
}
```

```
{
  id: TD-27,
  pri: should,
  name: "Limitation: cultural bias -- 1960s American context",
  src: TUCKMAN_COMPLETE.md Section 17 (#4),
  sections: [2c],
  how: "If team was multicultural: 'Tuckman's model was developed in a 1960s
        American context. In our multicultural team, Storming may have
        manifested differently -- collectivist team members suppressed
        conflict that surfaced later, while individualist members expressed
        disagreement immediately.'",
  quote: "Collectivist cultures may exhibit different patterns (e.g.,
          suppressed Storming that surfaces later)",
  ref: "(Tuckman, 1965)"
}
```

```
{
  id: TD-28,
  pri: could,
  name: "Limitation: no timeframes given",
  src: TUCKMAN_COMPLETE.md Section 17 (#3),
  sections: [2a],
  how: "'Tuckman provides no indication of how long each stage should last,
        making it difficult to distinguish between 'healthy extended Storming'
        and 'stuck Storming.' Our 3-week Storming period felt long but may
        have been necessary.'",
  quote: "The model gives no indication of how long each stage should last.
          A team could be Storming for weeks or months",
  ref: "(Tuckman, 1965)"
}
```

```
{
  id: TD-29,
  pri: could,
  name: "Limitation: pre-assigned vs self-selected teams",
  src: TUCKMAN_COMPLETE.md Section 17 (#6),
  sections: [2a, 2c],
  how: "'University project teams are assigned, not chosen. This fundamentally
        changes Forming dynamics -- we had no say in team composition, which
        may have extended our Storming phase compared to self-selected teams.'",
  quote: "University project teams are assigned, not chosen. This changes
          Forming dynamics significantly",
  ref: "(TUCKMAN_COMPLETE.md)"
}
```

```
{
  id: TD-30,
  pri: skip,
  name: "Limitation: remote/hybrid work not covered",
  src: TUCKMAN_COMPLETE.md Section 17 (#7),
  sections: [],
  how: "Only relevant if team worked remotely. If so: 'The model predates
        remote work. Our hybrid arrangement -- some meetings in-person,
        coordination via GitHub/Discord -- may have altered how stages
        manifested, particularly Forming where trust-building is harder
        digitally.'",
  quote: "The model predates remote work. Digital communication may alter
          how stages manifest",
  ref: "(TUCKMAN_COMPLETE.md)"
}
```

---

## O. Fractal Teams (Teams of Teams)

```
{
  id: TD-31,
  pri: could,
  name: "Fractal nature -- Tuckman repeats at division/company level",
  src: TUCKMAN_COMPLETE.md Section 13 (Step 4),
  sections: [2a, 3b],
  how: "If relevant to team-of-teams structure: 'Graham notes the fractal
        nature of Tuckman -- teams within larger organisations must repeat
        the cycle at each interface level. Our sub-teams (software, hardware,
        flight ops) each went through their own micro-Tuckman cycle while
        the overall team followed a macro cycle.'",
  quote: "Your team is part of a developing division and company. You will
          need to repeat some aspects of the Tuckman cycle at each new level
          of interface. Your division is a team of teams.",
  ref: "(lecture, Mark Graham)"
}
```

---

## P. Storming Is Universal

```
{
  id: TD-32,
  pri: must,
  name: "Storming is universal -- every team, no exceptions",
  src: TUCKMAN_COMPLETE.md Section 6 (Mark's Universal Claim),
  sections: [2a, 2b],
  how: "Use to normalise conflict: 'Graham states that without exception,
        every team he has worked within or managed has experienced Storming.
        Our conflict during Wk17 was therefore not a failure but an expected
        and necessary stage.'",
  quote: "Without exception, every new team I've worked within or have
          managed has experienced this stage",
  ref: "(lecture, Mark Graham)"
}
```

---

## Q. Greater Than Sum of Parts

```
{
  id: TD-33,
  pri: could,
  name: "Good teams > sum of parts",
  src: TUCKMAN_COMPLETE.md Section 1 (Benefits table),
  sections: [3a],
  how: "Positive framing for 3a impact: 'Our combined output -- a working
        autonomous SAR system with onboard AI, GPS estimation, and progressive
        test framework -- exceeded what any individual could have built.
        The team was, as Graham puts it, more than the sum of its parts.'",
  quote: "Good teams should add up to more than the sum of their parts",
  ref: "(lecture, Mark Graham)"
}
```

---

## R. Interaction and Accidental Discovery

```
{
  id: TD-34,
  pri: could,
  name: "Team interaction creates accidental discoveries",
  src: TUCKMAN_COMPLETE.md Section 1 (Benefits table),
  sections: [2b, 3a],
  how: "If there was a serendipitous moment: 'A conversation with [teammate]
        about [X] led to the unexpected discovery that [Y]. This exemplifies
        Graham's point about teams creating opportunities for accidental
        discoveries through interaction.'",
  quote: "Being in a group does create new opportunities for interaction and
          creativity and accidental discoveries",
  ref: "(lecture, Mark Graham)"
}
```

---

## S. Hatton L4 Moves Enabled by Tuckman

```
{
  id: TD-35,
  pri: must,
  name: "L3 Dialogic: compare theory to experience",
  src: TUCKMAN_COMPLETE.md Section 15 (Hatton table),
  sections: [all],
  how: "Every Tuckman reference should be L3 minimum: 'Tuckman predicts X;
        we experienced Y.' Never just describe the model -- always compare
        to your specific experience.",
  quote: "Tuckman predicts universal Storming; we experienced this during
          Wk 17 when...",
  ref: "(Hatton & Smith, 1995)"
}
```

```
{
  id: TD-36,
  pri: must,
  name: "L4 Critical: evaluate model limitations from experience",
  src: TUCKMAN_COMPLETE.md Section 15 (Hatton table),
  sections: [2a, 2c],
  how: "At least ONE L4 move per page: 'Tuckman's model assumes linear
        progression, but our experience was cyclical -- we regressed after
        flight cancellations, supporting Bonebright's critique that real
        teams oscillate between stages.' Or question therapy-group basis.",
  quote: "Tuckman's original study was conducted on therapy groups, not
          engineering teams. Its applicability to time-bounded MSc projects
          with pre-assigned members is debatable",
  ref: "(Tuckman, 1965, p.384; Bonebright, 2010)"
}
```

```
{
  id: TD-37,
  pri: should,
  name: "L4 Critical: synthesise Tuckman with Belbin",
  src: TUCKMAN_COMPLETE.md Section 16 (cross-model table),
  sections: [2a, 2b],
  how: "Cross-model synthesis: 'Our Storming-phase conflicts align with
        Belbin's observation that teams lacking a Plant role default to safe,
        unimaginative solutions.' Or: 'Two Shapers competing explains why
        our Storming was intense.'",
  quote: "Belbin explains why Storming occurs -- role clashes. Performing
          requires role complementarity.",
  ref: "(Tuckman, 1965; Belbin, 2010)"
}
```

---

## T. Forming Surprise -- Not Actually Unpleasant

```
{
  id: TD-38,
  pri: could,
  name: "Forming is deceptively pleasant -- pressure comes later",
  src: TUCKMAN_COMPLETE.md Section 5,
  sections: [2a],
  how: "Brief mention: 'Our Forming phase felt easy -- everyone was friendly
        and deliverables were distant. Graham notes this is typical: Forming
        is not the hardest phase because there is not yet pressure to deliver.'",
  quote: "At the very beginning of projects, it's not normally the hardest
          or most unpleasant phase. At this point, everyone's mostly friendly
          and the team's deliverables are a long way off in the future",
  ref: "(lecture, Mark Graham)"
}
```

---

## U. Two Dimensions -- Group Structure + Task Activity

```
{
  id: TD-39,
  pri: could,
  name: "Tuckman's two parallel dimensions -- interpersonal + task",
  src: TUCKMAN_COMPLETE.md Section 3 (Two Axes),
  sections: [2a],
  how: "Show sophistication: 'Tuckman actually separated group functioning
        into two parallel realms -- group structure (interpersonal) and task
        activity -- that evolve in parallel. Our interpersonal development
        (trust-building) lagged behind our task development (we were
        delivering code before we had resolved interpersonal tensions).'",
  quote: "Group Structure: Testing & Dependence -> Intragroup Conflict ->
          Development of Cohesion -> Functional Role-Relatedness",
  ref: "(Tuckman, 1965)"
}
```

---

## V. Active Management Required

```
{
  id: TD-40,
  pri: should,
  name: "Best-case requires active management -- not luck or natural talent",
  src: TUCKMAN_COMPLETE.md Section 10 (Key Warning),
  sections: [2c, 3b],
  how: "Future-facing: 'Graham warns that unless naturally gifted or lucky,
        you must actively manage the team to achieve the best-case scenario.
        In future, I would not rely on organic team development but would
        schedule explicit Forming activities and facilitated Storming
        resolution.'",
  quote: "Unless you're naturally gifted or lucky with your team members,
          you will have to actually actively manage the team to achieve
          the best case scenario.",
  ref: "(lecture, Mark Graham)"
}
```

---

## W. Norming Indicators Checklist

```
{
  id: TD-41,
  pri: could,
  name: "5 indicators of reaching Norming",
  src: TUCKMAN_COMPLETE.md Section 7 (indicators list),
  sections: [2a],
  how: "Use as evidence checklist: 'Of the five Norming indicators --
        (1) constructive criticism, (2) inside jokes, (3) realistic plans,
        (4) free-flowing information, (5) sense of belonging -- our team
        demonstrated [3-4 of 5] by Wk21.'",
  quote: "1. Criticism is constructive, not personal. 2. Team has inside
          jokes. 3. Plans are detailed and realistic. 4. Information flows
          freely. 5. Members feel belonging.",
  ref: "(lecture, Mark Graham)"
}
```

---

## X. Performing vs Forming -- Unclear vs Fluid Roles

```
{
  id: TD-42,
  pri: could,
  name: "Forming: roles unclear (chaotic) vs Performing: roles flexible (intentional)",
  src: TUCKMAN_COMPLETE.md Section 8 (Key Characteristic),
  sections: [2a],
  how: "Show understanding of the distinction: 'Both Forming and Performing
        feature ambiguous roles, but for opposite reasons. In Forming, nobody
        knows who does what (chaotic). In Performing, everyone can do anything
        (intentional fluidity). We experienced both -- early confusion in
        Wk12 versus productive role-swapping during field testing.'",
  quote: "This is fundamentally different from Forming, where roles are
          unclear (chaotic), versus Performing, where roles are flexible
          (intentional).",
  ref: "(TUCKMAN_COMPLETE.md)"
}
```

---

## Y. "The Team's Work IS Your Work"

```
{
  id: TD-43,
  pri: could,
  name: "Senior manager mindset: team's work is your work",
  src: TUCKMAN_COMPLETE.md Section 2,
  sections: [1a, 1c],
  how: "Career reflection: 'Graham's insight that the team's work is your
        work reframed my frustration with coordination overhead. My role
        was not just CV development -- enabling the team to integrate and
        test was equally my work.'",
  quote: "The reality is that the team's work is your work.",
  ref: "(lecture, Mark Graham)"
}
```

---

## Z. "Worst Acts in History" -- Provocative Democratic Framing

```
{
  id: TD-44,
  pri: skip,
  name: "Will of the people -- provocative democratic critique",
  src: TUCKMAN_COMPLETE.md Section 1 (Key Quote),
  sections: [],
  how: "Too provocative for a reflective report. Skip unless you need a
        dramatic opening. Better to use the softer 'just because it's
        popular doesn't make it good' version (TD-18).",
  quote: "Some of the worst acts in history have been as a result of the
          will of the people.",
  ref: "(lecture, Mark Graham)"
}
```

---

## Summary: Priority Distribution

| Priority | Count | IDs |
|---|---|---|
| **must** | 12 | TD-01, TD-02, TD-06, TD-08, TD-11, TD-15, TD-21, TD-24, TD-25, TD-26, TD-32, TD-35, TD-36 |
| **should** | 13 | TD-03, TD-04, TD-07, TD-09, TD-10, TD-13, TD-14, TD-18, TD-20, TD-22, TD-27, TD-37, TD-40 |
| **could** | 14 | TD-05, TD-12, TD-17, TD-19, TD-23, TD-28, TD-29, TD-31, TD-33, TD-34, TD-38, TD-39, TD-41, TD-42, TD-43 |
| **skip** | 2 | TD-30, TD-44 |

## Section Heatmap (which D7 sections get the most ammo)

| Section | Must | Should | Could | Total |
|---|---|---|---|---|
| **2a (team structure)** | 5 | 5 | 6 | 16 |
| **2b (impactful elements)** | 3 | 6 | 2 | 11 |
| **2c (what to change)** | 2 | 6 | 3 | 11 |
| **1a (roles/responsibilities)** | 1 | 1 | 2 | 4 |
| **3a (drive team forward)** | 1 | 1 | 3 | 5 |
| **4a (support team)** | 1 | 2 | 0 | 3 |
| **3b (future re-focus)** | 0 | 1 | 2 | 3 |
| **1b (proud of)** | 0 | 0 | 1 | 1 |
| **1c (future focus)** | 0 | 1 | 2 | 3 |
| **4b (peer development)** | 0 | 1 | 0 | 1 |

## Top 5 Highest-Impact Moves for Apollo

1. **TD-15 (Dominant personalities)** -- self-aware critique of own dominance is the single highest L4 move available. Scores on self-awareness, honesty, and critical thinking simultaneously.
2. **TD-06 + TD-26 (Regression + non-linearity)** -- pair these to show the model breaks in practice. Lived experience contradicting theory = textbook L4.
3. **TD-21 + TD-24 (Management investment paradox)** -- use as THE "what I'd do differently" answer. Concrete, quotable, directly from course material.
4. **TD-25 (Therapy groups limitation)** -- one sentence citing Tuckman against himself. Maximum L4 impact for minimum word count.
5. **TD-08 (Violently agreeing)** -- forces honest self-assessment. Whether the team did or didn't exhibit this, the reflection itself scores points.
