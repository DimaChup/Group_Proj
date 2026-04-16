# D7 Agentic Workflow — Prescriptive Playbook

**Purpose:** a concrete, opinionated multi-agent workflow for iterating the D7 individual reflective report to ceiling (~85/100) without wasted agent cycles.

**TL;DR recommendation:**
Run a **parallel-draft -> judge-panel -> merge -> critic-refine** pipeline, not a single writer loop. Cap at **3 refinement iterations after merge**. Use **two independent scorers** for the first merge gate, then drop to one scorer after plateau. **Human in the loop at exactly two points**: (a) after the merged draft, (b) before final polish. Stop when two consecutive scores differ by <1.5 points OR human says "this is me."

---

## 1. State of the Art (what the research actually says)

### 1.1 Anthropic's five effective-agent patterns
Anthropic's "Building Effective Agents" guide (2024) defines five patterns. Two are directly relevant to iterative writing:

- **Parallelization (voting/sectioning)** — run N independent calls on the same task, aggregate. Best when you want robustness, multiple perspectives, and low wall-clock. Increases cost linearly.
- **Evaluator-Optimizer** — a generator produces, an evaluator critiques, generator refines. Best when criteria are clear AND iteration demonstrably improves output. Anthropic explicitly warns: **set a max iteration cap** or you hit diminishing returns.

The orchestrator-workers pattern is the right framing for *you* (the user / master Claude) as orchestrator running the below waves.

Anthropic's cross-pattern rule: "add complexity only when it demonstrably improves outcomes." For a 7-page reflective essay, the answer is yes — but bounded.

### 1.2 Self-Refine (Madaan et al., 2023)
Self-Refine (same LLM as writer + feedback + refiner) improves quality by **~20% absolute on average** over single-shot. BUT Figure 4 of the paper shows **clear diminishing returns after 2-3 iterations**. Marginal gain per iteration falls off a cliff past iteration 3 on most tasks. For open-ended creative/reflective writing (no ground truth), the plateau arrives **even earlier** than for code/math.

**Implication:** hard-cap refinement at 3 iterations. Don't let agents loop forever "just in case."

### 1.3 LLM-as-judge reliability & self-preference bias
Key findings from 2024-2025 survey literature:

- **Self-preference bias is real and linearly correlated with self-recognition** (NeurIPS 2024). An LLM judge favours text it generated itself.
- **Positional bias** — judges prefer the first option shown. Must randomize order when comparing drafts.
- **Fleiss' Kappa among state-of-the-art judges averages ~0.3** — that's "fair" agreement, not "good." One judge is not enough when stakes are high.
- **Multi-judge consensus is the recommended mitigation.** Even 2 independent judges with score aggregation measurably improves reliability.
- **Judge model choice matters more than task complexity** for positional bias (IJCNLP 2025).

**Implication:** use at least 2 scorers for the critical "which draft wins" decision. They can be the same model family but must run in **separate sessions** with **randomized draft order** and a **detailed rubric** (rubrics reduce judge variance more than ensemble size).

### 1.4 Multi-agent debate vs single-agent iteration
MIT/Google Brain: multi-agent debate improves factual accuracy and reduces hallucinations on complex trade-off tasks. BUT:
- Debate's gains over **majority voting** are marginal when agents are homogeneous (same model).
- Debate costs scale super-linearly with rounds; quality gains do not.
- Debate wins on "trade-off-heavy problems with genuine ambiguity" — which reflective writing IS.

**Implication:** one round of critic-debate after the merge is worth it. Multiple rounds of debate are not.

### 1.5 Best-of-N / sampling diversity
Research on sampling diversity (Brown et al., co-scaling-law work 2024-2025) shows:
- Parallel sampling at **higher temperature** explores the output space better than serial refinement from a single seed.
- For **hard, creative** tasks: more samples + higher temperature beats fewer samples + refinement.
- For **well-defined** tasks: fewer samples + refinement beats more samples.
- Diversity in the N drafts is what makes best-of-N work. N homogeneous drafts = wasted cost.

**Implication:** your 3 parallel writers (A/B/C) must use **structurally different prompts** (different framing / narrative arc / tone) — not just different seeds. Diversity by construction, not by chance.

### 1.6 Tree of Thoughts for creative writing
ToT (Yao et al. 2023) branches, evaluates, backtracks. Documented to improve coherence and originality in creative writing. But ToT is *expensive* — branches explode — and in practice for a 7-page essay the payoff over structured best-of-N is small unless you have a specialized verifier.

**Implication:** don't do full ToT. Do "flat ToT" = best-of-3 with explicit structural priors, which is what you're already doing.

---

## 2. Recommended Workflow for OUR D7

This is the pipeline to run, phase by phase. You (the human) are orchestrator.

### Phase 0 — Foundation (DONE)
- Brief constraints, AHEP4, frameworks, exemplars -> saved as reference docs
- Raw material extracted from user
- Scoring rubric synthesized

**Gate:** rubric is finalized and shared with every downstream agent verbatim. If the rubric shifts mid-pipeline, invalidate scores.

### Phase 1 — Parallel diverse drafting (RUNNING)
- 3 writer agents (A/B/C) producing **structurally different** drafts:
  - A: chronological narrative arc
  - B: theme-based (e.g., 3 CLO clusters)
  - C: tension/critical-incident driven (STAR or Gibbs-heavy)
- Each gets the SAME raw material + rubric + brief. Different prompts enforce diversity.
- Temperature: medium-high for creativity, NOT max (avoid incoherence).
- Also running: appendix designer, cover page designer (these are independent subtasks — fine).

**Why 3, not 5 or 10:** past 3-4 drafts, marginal diversity collapses for a single-author reflective essay. The best-of-N co-scaling research shows the sweet spot for well-constrained creative tasks is N=3-5.

**Cost/quality knob:** if budget tight, 2 drafts (A + B) still works; drop C.

### Phase 2 — Independent dual scoring
- **Scorer-1**: full rubric, scores A, B, C in randomized order, no knowledge of who wrote what.
- **Scorer-2**: SAME rubric, INDEPENDENT session (fresh context), randomized order (different randomization from S1).
- Each produces: numeric scores per rubric dimension + top 3 strengths per draft + top 3 weaknesses per draft + explicit winner.

**Rule:** if S1 and S2 disagree on winner AND scores differ by >5 points on the winner, spawn Scorer-3 (tiebreaker). Otherwise, aggregate by mean.

**Why two scorers:** Fleiss Kappa ~0.3 for single judges. Two independent judges with randomized order + shared rubric demonstrably reduces self-preference and positional bias. This is the only place in the pipeline where the extra cost is justified.

**Output:** ranked drafts + consolidated strength/weakness list across all three.

### Phase 3 — Merge agent (best-of-N synthesis)
- ONE merge agent (not parallel). Input:
  - All 3 drafts
  - Both scorer reports
  - Explicit instruction: "Take the winning draft's spine. Graft in the top 2 strengths from each of the other two drafts where they fit without breaking voice. Fix the top 3 weaknesses that appear in both scorers' reports."
- This is NOT another writer from scratch. It is a **surgical integrator**.

**Why one merge agent, not parallel:** merging is a constrained editorial task, not a creative one. Multiple merge agents would produce near-identical outputs (tested in best-of-N literature — low diversity for constrained tasks).

**Output:** `D7_MERGED_V1.md`

### Phase 4 — Human checkpoint #1 (critical)
- You read the merged draft end to end once.
- Mark 3 kinds of things:
  1. **"Not me"** — voice is wrong, tone is off, claim is inaccurate
  2. **"Missing"** — an experience or insight the agents couldn't guess
  3. **"Cut this"** — filler, exaggeration, hollow phrases
- Output a short feedback note: ~10-20 line bullets.

**Why human here, not at the end:** agents cannot infer (a) what actually happened to you, (b) your actual voice, (c) what you're comfortable claiming. Human feedback at this stage is worth more than the next 5 agent iterations. The Self-Refine paper is explicit: "iterative refinement is most effective when a human articulates feedback."

### Phase 5 — Critic-refiner loop (capped at 3 iterations)
This is an evaluator-optimizer loop. Each iteration:
1. **Critic agent** reads current draft + rubric + your feedback note. Produces a critique report: specific paragraph-level issues, rubric dimensions below target, concrete rewrite suggestions.
2. **Refiner agent** rewrites the draft addressing the critique. Must preserve voice, may not exceed 7 pages.
3. **Scorer-1 only** (single scorer is fine here — the rubric is fixed, stakes lower, plateau detection matters more than judge reliability at this phase) scores the result.
4. **Plateau check:**
   - If score improvement over last iteration < 1.5 points -> STOP.
   - If any rubric dimension DROPS by >2 -> revert this iteration, stop.
   - Hard cap: 3 iterations regardless.

**Why a separate critic and refiner (not the writer self-refining):** the Self-Refine ~20% gain assumes the critic function is actually distinct from generation. Collapsing them into one agent in a single context window reintroduces self-preference bias. Separate sessions, separate prompts.

**Output:** `D7_REFINED_V{1,2,3}.md` + score trajectory.

### Phase 6 — Human checkpoint #2 (final polish pass)
- You read the refined draft.
- Fix only: voice mismatches, factual claims, tone.
- DO NOT rewrite — agents have already optimised structure and rubric alignment. Your job is owning the words.

### Phase 7 — Final polish agent (1 pass, no iteration)
- A single "copyeditor" agent: grammar, consistency, references, figure/caption formatting, page count, word count, acronym expansion on first use.
- **Not a rewriter.** Explicit instruction: "make no structural changes, only surface-level edits."

**Output:** `D7_FINAL.md`

### Phase 8 — Compile & submit
- LaTeX build, visual check, PDF export.

---

## 3. Plateau detection — when to stop

You need explicit stop rules so agents don't burn cycles chasing 0.3-point gains.

| Signal | Action |
|---|---|
| Consecutive iteration score delta < 1.5 pts | STOP refinement loop |
| Any rubric dimension drops >2 pts in an iteration | REVERT + STOP (refiner is overfitting) |
| Both scorers agree "no further improvements possible" | STOP |
| Hit hard cap of 3 refinement iterations | STOP |
| Human says "this sounds like me and hits the rubric" | STOP |
| Score hits 83+ (empirical D7 ceiling observed in prior cycles) | STOP — last marginal gains will introduce artifice |

The prior D7 session log confirms the ceiling: iterations went 68 -> 79 -> 76-77 -> 83-84 over ~6 rounds, with clear plateau at 83-84. Do not chase 85+. The page limit and rubric weightings make that mathematically very hard.

---

## 4. Human-in-the-loop checkpoints (exactly two)

| # | When | What you do | Time budget |
|---|---|---|---|
| HITL-1 | After Phase 3 merge | Mark not-me / missing / cut-this | 20-30 min |
| HITL-2 | After Phase 5 refinement loop stops | Voice + factual + tone pass only | 20-30 min |

That's it. Do NOT human-review every draft in phase 1 (wasted time — agents haven't converged), do NOT human-review every critic round (wasted time — rubric handles it). Two touches, high value each.

Optional HITL-0 at rubric finalization (Phase 0) if the rubric itself feels wrong — fixing it later costs everything downstream.

---

## 5. Cost/quality tradeoffs at different agent counts

Assuming "1 agent call" ≈ 1 unit of cost. Baseline rubric score from prior cycles: ~68 one-shot.

| Configuration | Agent calls | Expected score | Wall clock | Notes |
|---|---|---|---|---|
| Single writer, no iteration | 1 | ~68 | 5 min | One-shot baseline |
| Single writer, self-refine x3 | 4 | ~75 | 20 min | Self-refine paper average gain |
| Writer + critic + refiner (x3 loop) | 10 | ~79 | 30 min | Separated roles, bias reduced |
| **Recommended: 3 parallel + 2 judges + merge + critic-loop(x3) + polish** | **~18** | **~83-84** | **45-60 min** | **Sweet spot** |
| Above + 5 parallel drafts, 3 judges, 5 iterations | ~35 | ~84-85 | 90+ min | Diminishing returns — not worth it |
| Full ToT + debate + 3-judge ensemble + 5 refinement rounds | 60+ | ~85 | 3+ hrs | Waste. Don't. |

**Cost-optimal:** the recommended config. Going bigger adds <2 points at 2x cost. Going smaller loses 4-5 points.

**Cost-minimum usable:** 2 parallel drafts + 1 scorer + merge + 2 critic iterations + polish (~8 calls, ~78 expected). Use this if under time pressure.

---

## 6. Specific answers to the 7 questions

1. **3 independent writers or 1 writer + 2 critics?**
   **3 independent writers, THEN critic loop after merge.** Parallel diverse drafting explores the solution space (best-of-N literature); a single writer + critics is faster to local optimum but misses structural alternatives. You want both — diverse exploration first, focused refinement second.

2. **How many iterations before plateau?**
   **2-3 refinement iterations after the merge.** Self-Refine shows steep diminishing returns past iteration 3. Your own prior D7 cycles confirm this (plateau at ~83-84 by round 4-5).

3. **Scorers same model as writers or different?**
   **Same model family is fine, but in separate sessions with no knowledge of authorship + randomized order + detailed rubric.** Different model would help more (self-preference is measurable), but a good rubric + 2 independent judges closes most of the gap for far less cost and complexity.

4. **Redundant scoring worth it?**
   **Yes at the merge gate (Phase 2). No during the critic loop (Phase 5).** Merge gate decides which draft wins — high stakes, bias-sensitive, randomization + 2 judges mandatory. Critic loop is score-trajectory monitoring — 1 judge + plateau rules is enough.

5. **When human in the loop?**
   **Exactly twice: after merge (HITL-1), before polish (HITL-2).** Optional third at rubric finalization. Everywhere else the human just reviews final artifacts.

6. **"Good enough — stop" metric?**
   **Score delta < 1.5 points for 2 consecutive iterations** OR **any rubric dimension drops >2** OR **human says "this is me and hits the rubric."** Hard cap 3 iterations. Expected ceiling 83-84.

7. **Combining drafts without losing strengths?**
   **Surgical merge agent, not a fresh writer.** Input: winning draft's spine + explicit "graft these 2 strengths from draft B and these 2 from draft C" + "fix these 3 weaknesses both judges flagged." Not "rewrite synthesizing all three" — that loses voice. Merge is editing, not writing.

---

## 7. Immediate next steps for the current D7 cycle

You already have Phases 0-1 running. When they land:

1. **Don't touch the 3 drafts yet.** Launch Phase 2: two independent scorer agents, randomized draft order each, full rubric. Parallel.
2. **While scorers run**, review the appendix + cover page outputs (independent track).
3. **When both scorer reports land**, launch Phase 3: single merge agent with explicit strengths-to-graft and weaknesses-to-fix instructions.
4. **Read the merged draft yourself** — HITL-1. Write the 10-20 bullet feedback note.
5. **Launch Phase 5 critic-refine loop** with your feedback note injected into critic prompt. Cap 3 iterations.
6. **Check plateau after each iteration.** Stop early if delta <1.5.
7. **HITL-2 voice pass**, then launch Phase 7 polish agent.
8. **Compile.** Done.

Expected total: ~18 agent calls after current phase lands, ~45-60 min, landing at 83-84.

---

## Sources

- Anthropic, "Building Effective Agents" — https://www.anthropic.com/research/building-effective-agents
- Madaan et al., "Self-Refine: Iterative Refinement with Self-Feedback" — https://arxiv.org/abs/2303.17651
- Li et al., "A Survey on LLM-as-a-Judge" — https://arxiv.org/abs/2411.15594
- "Justice or Prejudice? Quantifying Biases in LLM-as-a-Judge" (NeurIPS 2024) — https://llm-judge-bias.github.io/
- "Multi-Agent Debate Strategies" — https://arxiv.org/html/2507.05981v1
- Shinn et al., "Reflexion" — commonly cited alongside Self-Refine
- "On the Effect of Sampling Diversity in Scaling LLM Inference" — https://arxiv.org/html/2502.11027v3
- "Inference-Aware Fine-Tuning for Best-of-N Sampling" — https://arxiv.org/html/2412.15287v1
- Yao et al., "Tree of Thoughts" — https://www.promptingguide.ai/techniques/tot
- "An Empirical Study of LLM-as-a-Judge" (IJCNLP 2025) — https://arxiv.org/html/2506.13639v1
