# Innovation Methods: Down-Selection Tools

**Source:** AENGM0074 Professional Practice, University of Bristol
**Presenter:** Mark Graham
**Format:** Video lecture (~14:42) + 17 slides
**Unit-level objective:** 2. Carry out the design, build and test of a functioning major UAV assembly as part of a team, using applicable interdisciplinary concepts and methods.

## Learning Objectives (verbatim from transcript)

> "At the unit level we are working towards objective 2 but at the session level we have the following objectives."

1. **Recall** the benefits of using a structured down-selection methodology
2. **Utilise** a *numerical* and *non-numerical pairwise comparison tool* to **rank** or **weight** solution criteria
3. **Utilise** a *controlled convergence* tool to **select** an optimum solution
4. **Utilise** a *multi-criteria decision analysis (MCDA) method* to **select** an optimum solution

Objectives 2-4 are marked as "Higher Order" on the slide (arrow annotation).

> "At the end of the teaching you should be able to carry out all of these activities but you'll need some time to practise some methods to become confident at using them."

---

## 1. Divergent vs Convergent Thinking

The problem-solving process has two phases, visualised on slide 3 as a funnel diagram:

**Divergent thinking** (left side of diagram):
- "Define problem" box fans out to Solutions 1-6
- The word "divergent" is used because you want the number of available ideas to **increase**, giving a range of options to select from
- This is the idea-generation phase

**Convergent thinking** (right side of diagram):
- Solutions 1, 3, 6 are eliminated; Solutions 2, 4, 5 survive the filter
- A decision diamond labelled "solution acceptable" determines whether the remaining options proceed to "Select solution" or loop back ("No solution found" arrow returns to divergent phase)
- Reduces the number of ideas down to a small number, sometimes just one
- Allows testing or experimentation on a reasonable number of options

**The loop-back principle:** "Normally you will try to progress through the divergent and convergent processes in one sweep, but when working with challenging problems you should keep it in mind that you may need to repeat the loop and generate new ideas if the one that you converged on does not satisfy your requirements."

**Critical warning:** "Just because it's the only idea left doesn't mean it's the one that you have to use."

The four tools introduced in this lecture deal with the **convergent thinking** (down-selection) stage.

---

## 2. Requirements Analysis First

Slide 4 ("Reviewing requirements and solutions") shows a two-box flow:

| Criteria / Requirements | --> | Solutions / Designs |
|---|---|---|
| Define, Select, Weight or Rank your criteria | | Use your criteria to select your solution |
| e.g. weight, cost, time-to-market, capital investment, safety... | | e.g. design 1, design 2... |

**Key principle:** You should spend time analysing the requirements of your solution **before** you embark on selecting the solution itself.

From the transcript:
- "If you skip the requirements analysis, you'll most likely find that the solution selection takes much longer anyway as the team will find it harder to agree on what good is supposed to look like."
- "Or you might find that your definition of good evolves from one day to the next."
- Group detailed requirements into categories: **10 or fewer**, ideally **5 to 7**.
- "The tools are not rigid and you are free to create hybrid tools or develop the tools to suit your own needs. In the past, some groups have found novel ways of making the tools more democratic or flexible."

---

## 3. The Four Tools -- Overview

Slide 5 ("Tools") presents a 2x2 classification:

| | Evaluate criteria / requirements | Evaluate solutions / designs |
|---|---|---|
| **Non-numerical** | Pairwise Comparison (ranking) | Controlled Convergence |
| **Numerical** | Pairwise Comparison (numerical) | Multi-Criteria Decision Analysis (MCDA)* |

*MCDA combines evaluation of criteria AND solutions simultaneously, which "makes it one of the more popular and widely used tools within industry."

Slides 10 and 16 show this same grid with progressive green checkmarks as each tool is covered.

---

## 4. Tool 1: Simple Pairwise Comparison (Ranking)

**Purpose:** Evaluate and rank criteria/requirements (non-numerical). Can also be used to rank design solutions, but "it might not be sensitive enough for your needs."

### How It Works (step by step)

1. **List your criteria** in the left-hand column (as many or as few as you like)
2. **Compare 2 criteria** and record the letter for the more important criterion. If equal, write both letters (e.g. "AB")
3. **Repeat** until all criteria have been compared to all other criteria once (half the table is greyed out -- you only fill the upper triangle)
4. **Count** the number of times each criterion's letter appears. Where two letters appear in a box (equal importance), assign 0.5 to each
5. **Rank** the criteria based on the counts

### Example from Slide 7

The slide shows a completed matrix with 6 criteria:

**Criteria:** A = Strength (red), B = Appearance (red), C = Speed (red), D = Carbon footprint, E = Design resource, F = Durability

**Comparison matrix (upper triangle only, grey cells below diagonal):**

| | A | B | C | D | E | F |
|---|---|---|---|---|---|---|
| A (Strength) | -- | AB | A | D | E | A |
| B (Appearance) | | -- | C | E | E | F |
| C (Speed) | | | -- | C | C | F |
| D (Carbon footprint) | | | | -- | D | F |
| E (Design resource) | | | | | -- | E |
| F (Durability) | | | | | | -- |

**Count and Rank:**

| Criterion | Count | Rank |
|---|---|---|
| A (Strength) | 2.5 | 3rd |
| B (Appearance) | 0.5 | 5th |
| C (Speed) | 3 | =2nd |
| D (Carbon footprint) | 2 | 4th |
| E (Design resource) | 4 | 1st |
| F (Durability) | 3 | =2nd |

Explanation: "I have put the count for A as 2.5 because A was shown to be more important twice and equal once" (the AB cell gives A 0.5).

### Strengths
- Very simple and quick
- No numerical values needed -- purely ordinal
- Good starting point for teams new to structured decision-making
- Output (ranked list) can feed into other tools

### Limitations
- Only produces a **rank order**, not how much more important one criterion is vs another
- Not sensitive enough for complex design selections
- Equal-importance ties (0.5 scoring) can produce ambiguous rankings

---

## 5. Tool 2: Numerical Pairwise Comparison (Weighted)

**Purpose:** Evaluate and weight criteria/requirements (numerical). Produces **percentage weightings** that can be used as direct input into MCDA or other design selection tools.

### How It Works (step by step)

1. **List your criteria** and add simple details/descriptions about each (helps when revisiting decisions later)
2. **Choose a numerical scale** for importance:
   - Much more important = **9**
   - More important = **3**
   - The same = **1**
   - Less important = **1/3** (inverse of 3)
   - Much less important = **1/9** (inverse of 9)
3. **Compare each pair**: for each comparison, select from the drop-down (much more important, more important, the same, less important, much less important). You are comparing the **row** to the **column**.
4. **Percentage weightings** are automatically calculated and should always add up to 100%
5. Use the weightings as input to MCDA or discussion

### Example from Slide 9

The slide shows an Excel worksheet screenshot (small but readable) with:

**Criteria listed (4 criteria to keep things simple):**
- Initial Cost
- Durability
- Weight
- Handling

**Features/requirements table** at top with details about each criterion.

**Pairwise comparison matrix:**
- Scale chosen: 9 (much more) and 3 (more)
- Symmetric matrix (inverses auto-calculated)
- Example entry: "Initial cost vs Durability = 3" (initial cost is more important than durability)

**Output:** Percentage weightings for each criterion (yellow highlighted cells), summing to 100%.

The transcript notes: "The other numbers shown here are just the inverse of these numbers" and "To make things easier, each scoring box has a drop down list of the values you just selected above."

### Strengths
- More sensitive than simple pairwise -- captures **degree** of importance difference
- Produces percentage weightings usable in other tools (especially MCDA)
- Self-documenting (criteria descriptions preserved)
- Excel worksheet auto-calculates

### Limitations
- More complex than simple pairwise
- Scale choice (9/3) is somewhat arbitrary
- "You might not yet understand everything about how this tool works. The best way to close that gap is just to have a play with the Excel sheet."

---

## 6. Tool 3: Controlled Convergence (Pugh Matrix)

**Purpose:** Evaluate and compare design solutions against a datum (baseline). Commonly used to compare designs, but can compare anything.

### How It Works (step by step)

1. **List your criteria** in the left-hand column
2. **Choose a "Datum" design** -- normally an established or popular solution. This becomes the baseline.
3. **List the remaining design solutions** across the columns
4. **Compare each design against the datum** for each criterion:
   - Superior to datum: **+**
   - Equal to datum: **=**
   - Inferior to datum: **-**
5. **Sum** the pluses, equals, and minuses (+ = +1, = = 0, - = -1)
6. **Rank** the results. Highest net score = best solution (usually)

### Example from Slide 12

**Problem:** "Work out the best way to experience flying"

**Datum solution:** Balloon

**Alternative designs:** Helicopter, Anti-gravity shoes, Seagulls (+ 2 empty columns)

**Criteria:** Cost, Range, Safety, Altitude ceiling (+ 2 empty rows)

**Completed matrix:**

| Criteria | Balloon (DATUM) | Helicopter | Anti-gravity shoes | Seagulls |
|---|---|---|---|---|
| Cost | (baseline) | - | - | + |
| Range | (baseline) | - | - | - |
| Safety | (baseline) | + | - | - |
| Altitude ceiling | (baseline) | - | - | - |
| **Sum +** | | 1 | 0 | 1 |
| **Sum -** | | -3 | -4 | -3 |
| **Sum =** | | 0 | 0 | 0 |
| **Net Score** | (Zero) | -2 | -4 | -2 |
| **Rank (1=best)** | **1** | **2** | **3** | **2** |

**Result:** The datum concept (Balloon) came out as the best solution with a net score of zero, beating all alternatives.

> "And actually the datum concept came out as the best solution, so maybe that's the one I should go for. Sometimes that will happen, and sometimes the best solution won't be one of the datums. It depends what you pick."

### Critical caveat -- tools support, not replace, thinking

> "But why did I say in most cases you would pick the highest ranked item? Well, these are only simple tools, and they are there to support your thinking, not to replace it. In all cases, the team's decision is final and it's absolutely fine to have a gap between what the tool indicates and what you finally select, **providing there's a justifiable and explainable reason for that gap**."

### Strengths
- Simple and intuitive (+/=/- scoring)
- Forces comparison against a known baseline
- Works with any number of criteria and designs
- Quick to execute in a team setting

### Limitations
- All criteria treated equally (no weighting)
- Crude scoring: a minor advantage gets the same + as a major advantage
- Datum choice influences results
- "Just because it's the only idea left doesn't mean it's the one that you have to use"

---

## 7. Tool 4: MCDA (Multi-Criteria Decision Analysis)

**Purpose:** Evaluate both criteria AND solutions simultaneously. "This seems to be the most popular tool with engineers as the process is very logical, very effective, but not over complicated."

### How It Works (step by step)

1. **List your criteria** (left column)
2. **List your designs** (top row)
3. **Identify a scoring scale** by which to rate designs (suggested maximum of 10; "beyond that, it can become too complicated")
4. **Identify weightings** for the criteria -- either by discussion or by importing from a completed Numerical Pairwise Comparison (Tool 2). Weightings must add to 100% (shown as decimals summing to 1.0)
5. **Score each design** against each criterion using the scoring scale
6. **Calculate weighted scores**: for each cell, weighted score = raw score x weighting
7. **Sum the weighted scores** for each design. **Highest total score = best design**

### Example from Slide 15

**Input table (top right of slide):**

| Criteria | Designs | Scoring scale (i.e. 1-5, 1-10) |
|---|---|---|
| Sustainability | Lithium ion cell | 1 |
| Reliability | Hydrogen PEM cell | 2 |
| Power | Flywheel | 3 |
| Safety | Thermal store | 4 |
| (empty) | Solid oxide fuel cell | 5 |

**MCDA Matrix (main table):**

| Criteria | Weightings (must add to 100%) | Lithium ion cell | | Hydrogen PEM cell | | Flywheel | | Thermal store | | Solid oxide fuel cell | |
|---|---|---|---|---|---|---|---|---|---|---|---|
| | | score | weighted | score | weighted | score | weighted | score | weighted | score | weighted |
| Sustainability | 0.150 | 4 | 0.6 | 3 | 0.5 | 1 | 0.2 | 1 | 0.2 | 2 | 0.3 |
| Reliability | 0.300 | 1 | 0.3 | 2 | 0.6 | 3 | 0.9 | 2 | 0.6 | 0 | 0.0 |
| Power | 0.250 | 3 | 0.8 | 1 | 0.3 | 5 | 1.3 | 5 | 1.3 | 1 | 0.3 |
| Safety | 0.300 | 2 | 0.6 | 5 | 1.5 | 0 | 0.0 | 5 | 1.5 | 3 | 0.9 |
| **Total** | | | **2.3** | | **2.8** | | **2.3** | | **3.5** | | **1.5** |

**Result:** Thermal store wins with 3.5, followed by Hydrogen PEM cell (2.8), then Lithium ion cell and Flywheel tied at 2.3, and Solid oxide fuel cell last at 1.5.

**Key observation from the example:** Safety and Reliability have the highest weightings (0.300 each), Power is 0.250, Sustainability is lowest at 0.150. The Thermal store wins primarily because it scores 5/5 on both Power and Safety (the two highest-weighted criteria).

### Strengths
- Combines criteria weighting and solution scoring in one tool
- Most popular with engineers -- logical, effective, not over-complicated
- Quantitative output enables clear comparison
- Weightings can be imported from Numerical Pairwise Comparison (Tool 2), creating a pipeline
- Highest sum product = clear winner

### Limitations
- Requires meaningful weightings (garbage in, garbage out)
- Scoring is still subjective
- Can give false confidence -- numerical output feels "objective" but depends entirely on input quality
- "You can't blame the Excel sheet if you clearly select the wrong idea"

---

## 8. Benefits of Structured Tools

From the transcript and slide 16 ("Using a structured approach"):

### Benefits (left column of slide, with icons)

1. **Faster agreement:** "They should help the team find agreement more quickly and with less trouble along the way." Provides a systematic framework for discussion.

2. **Neutralises strong personalities:** "I've often found these tools are really beneficial when there's some strong personalities in the room. Without the tools to focus and streamline our thinking, your discussions can often be led too much by who has the loudest voice or is the most persuasive, or perhaps who's the most senior within the organisation. Using an analytical tool is a great way of taking the focus away from personalities and placing the debate back within the realms of logic and reason."

3. **Adds quantitative clarity:** "Adding a quantitative element to the decision making process should add clarity and reliability." Numbers can help decision making.

4. **Essential for stakeholder communication:** "These tools are useful, I would say essential for explaining to your stakeholders why you chose a particular idea. Trying to explain all of your reasoning takes a long time, but when using a methodology along with the visuals you've seen, you can highlight certain areas and just breathe over the others as your thoroughness in the process will be self-evident."

---

## 9. Risks and Traps

From the transcript and slide 16 (right column, "Risks"):

1. **Too systematic can kill creative ideas:** "Although extra speed is useful in most projects, there can be some benefit to the randomness of a team's discussion, and that randomness can often generate ideas that won't appear if you're too systematic. It's often best then to use both methods. Have your wide-ranging unstructured debates first, and then use these tools to help tidy up and structure your thoughts afterwards." Random argument and discussion can generate unexpected solutions.

2. **Passion/experience should carry weight:** "However, should everybody's voice carry equal weight? In some cases it might be logical to give greater emphasis to someone who has a real passion for the topic or possesses greater experience in that area." Maybe someone's passion for the topic should give extra weight to their view.

3. **Rubbish in = rubbish out:** "Within any analysis tool, if you put rubbish in, you will get rubbish out. You can't blame the Excel sheet if you clearly select the wrong idea." The tool is only as good as what you put into it.

4. **Don't hide behind the tool:** "The final trap, however, is to start to hide behind the tool and let it take over as the master decision maker. The team's decision is final." Avoid hiding behind the tool as a reason for your decision making.

5. **Gap between tool output and team decision is OK:** "It's absolutely fine to have a gap between what the tool indicates and what you finally select, **providing there's a justifiable and explainable reason for that gap**."

---

## 10. Key Quotes (weaponizable for D7)

Direct quotes from the transcript, useful for citation:

1. > "The tools are there to support, not replace, your thinking."

2. > "Just because it's the only idea left doesn't mean it's the one that you have to use."

3. > "It's absolutely fine to have a gap between what the tool indicates and what you finally select, providing there's a justifiable and explainable reason for that gap."

4. > "Using an analytical tool is a great way of taking the focus away from personalities and placing the debate back within the realms of logic and reason."

5. > "If you skip the requirements analysis, you'll most likely find that the solution selection takes much longer anyway as the team will find it harder to agree on what good is supposed to look like."

6. > "Have your wide-ranging unstructured debates first, and then use these tools to help tidy up and structure your thoughts afterwards."

7. > "These tools are useful, I would say essential for explaining to your stakeholders why you chose a particular idea."

8. > "If you put rubbish in, you will get rubbish out. You can't blame the Excel sheet if you clearly select the wrong idea."

9. > "The tools on their own aren't particularly clever, but when used by a team they can become powerful ways of making better decisions."

10. > "Your definition of good evolves from one day to the next." (on why requirements analysis matters)

---

## 11. D7 Application -- How to Use This in Apollo's D7 Reflection

### Did the team use structured down-selection tools?

**Potential applications in the SAR drone project:**
- **CV backend selection**: TFLite vs NCNN vs Ultralytics -- this could have been framed as an MCDA with criteria like inference speed, accuracy, Pi compatibility, ease of deployment, model size
- **Model selection**: YOLOv8n vs YOLOv8s vs custom-retrained -- Pugh matrix against the baseline (YOLOv8n)
- **Flight test priority ordering**: Simple pairwise comparison to rank which tests to run first (bench, passive, waypoint, autonomous)
- **Search pattern design**: Lawnmower vs spiral vs expanding square -- controlled convergence against lawnmower as datum
- **Inference backend**: The `DESIGN_DECISIONS.md` file documents structured reasoning (DD-01 format with rationale) -- this is evidence of structured decision-making even if not formally using these tools

### If NOT used formally (Hatton L4 reflective move)

This is the stronger D7 angle. Reflect on what would have been different:

- "Looking back, our CV backend selection (TFLite to NCNN migration) was driven by benchmark results rather than a structured MCDA. While the outcome was sound, a formal weighted comparison incorporating criteria such as deployment complexity, community support, and long-term maintainability alongside raw inference speed would have produced a more defensible decision and forced the team to articulate trade-offs explicitly."
- "Our flight test ordering followed an intuitive progressive-risk approach, but a simple pairwise comparison of test priorities could have surfaced disagreements earlier and helped the team align on what 'ready for the next step' meant."
- Graham's warning is apt: we had structured debates (design decisions document) but lacked the quantitative scaffolding that would have neutralised the loudest-voice problem in some team discussions.

### If USED formally (M16.d, M17.d evidence)

- Document the tool, the criteria, the scores, and the outcome
- Show the gap (if any) between what the tool indicated and what the team chose
- Explain the justifiable reason for that gap
- Link to `DESIGN_DECISIONS.md` as evidence of structured reasoning

### BibTeX entry

```bibtex
@misc{graham_innovation_tools,
  author       = {Graham, Mark},
  title        = {Innovation Methods: Down-Selection Tools},
  year         = {2025},
  howpublished = {AENGM0074 Professional Practice video lecture, University of Bristol},
  note         = {Covers pairwise comparison (ranking and numerical), controlled convergence (Pugh matrix), and MCDA}
}
```

### In-text citation examples

- "Drawing on the structured down-selection methodology introduced in our Professional Practice sessions (Graham, 2025), a formal MCDA would have weighted criteria such as..."
- "Graham (2025) emphasises that these tools 'are there to support, not replace, your thinking' -- a principle we applied when..."
- "As Graham (2025) warns, 'if you put rubbish in, you will get rubbish out'; the quality of our design decisions depended on the quality of our requirements analysis, not the sophistication of the selection tool."

### Connection to rubric markers

| Marker | How to evidence |
|---|---|
| M16.d (Professional practice) | Reference Graham's structured approach; show awareness of when/why to use formal tools vs informal discussion |
| M17.d (Evaluation of methods) | Evaluate whether the team's informal approach was sufficient or whether MCDA/Pugh would have improved outcomes |
| Hatton L4 (Critical reflection) | Identify the gap between what was done and what could have been done; propose specific improvements with justification |

---

## 12. Summary Table -- All Four Tools at a Glance

| Tool | Evaluates | Output | Numerical? | Best for | Feeds into |
|---|---|---|---|---|---|
| Simple Pairwise Comparison | Criteria | Rank order | No | Quick criteria prioritisation | Discussion, other tools |
| Numerical Pairwise Comparison | Criteria | % weightings | Yes | Quantifying relative importance | MCDA (as weightings input) |
| Controlled Convergence (Pugh) | Solutions | Net +/- score | Semi | Comparing designs against baseline | Decision, further iteration |
| MCDA | Both | Weighted sum product | Yes | Final design selection | Decision |

**Recommended pipeline:** Numerical Pairwise Comparison (to weight criteria) --> MCDA (to score and select designs using those weights).
