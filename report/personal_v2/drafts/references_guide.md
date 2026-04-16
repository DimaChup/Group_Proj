# D7 References — Usage Guide

**Scope:** which references to cite, where they bite in the body, and which are
load-bearing vs decorative. A Distinction-level D7 uses **2–6 references**
(per `reviews/D7_EXEMPLARS.md`). Target here: **5–7 entries max**.

**Principle:** never cite for decoration. Every citation must support a specific
claim the marker can check. Over-referencing a 5-page reflective report reads as
performative and eats page budget in the bibliography even though the bib is
technically excluded — the in-text `[1]` markers still consume body lines.

---

## Recommended set (ranked by load)

| # | Key | Load | Where it cites in the body |
|---|-----|------|----------------------------|
| 1 | `schon1983reflective` | **LOAD-BEARING** | Anywhere the report uses "reflection-in-action" or "reflection-on-action" vocabulary. Grounds the whole reflective stance; cite once early (§ "My reflection framework" or first paragraph of the learning section). |
| 2 | `hatton1995reflection` | **LOAD-BEARING** | Wherever the report claims "critical / Level 4 reflection" — Hatton & Smith provide the four-level taxonomy (descriptive, descriptive-reflective, dialogic, critical). Cite in the self-scoring paragraph or when explicitly examining assumptions. Single most useful reference for scoring because markers rubric explicitly rewards Hatton Level 3–4. |
| 3 | `gibbs1988learning` | **LOAD-BEARING (conditional)** | Only if the body explicitly walks a Gibbs cycle (Description → Feelings → Evaluation → Analysis → Conclusion → Action Plan). If the Kolb cycle is used instead, drop this and keep Kolb only. **Do not cite both** — shows indecision. |
| 4 | `kolb1984experiential` | **LOAD-BEARING (conditional)** | Alternative to Gibbs. Kolb's concrete experience → reflective observation → abstract conceptualisation → active experimentation cycle. Prefer Kolb if the report frames learning as a *cycle of experiments* (which Apollo's 820-commit iteration pattern naturally fits). |
| 5 | `tuckman1965developmental` | **LOAD-BEARING** | Cite exactly once, in the team-dynamics paragraph, when discussing forming/storming/norming/performing. Critical because the honest claim "our team never exited storming" is the kind of specific, checkable judgement markers reward. |
| 6 | `brookfield1995critically` | **LOAD-BEARING** | Cite when the report performs the "four lenses" move (autobiographical / student / colleague / theoretical) or examines assumptions. This is the strongest reference for nudging from Hatton Level 3 → Level 4. Only cite if the body actually *does* an assumption examination. |
| 7 | `imeche2023conduct` | **DECORATIVE** unless ethics is a section | Only include if the body has a professional-conduct / ethics / responsibility paragraph (e.g. "I overran solo; IMechE Rule 3 on competence bounds says I should have escalated"). Otherwise drop. |
| 8 | `ardupilot` | **DECORATIVE** | Drop unless the body makes a technical argument hinging on ArduPilot-specific behaviour. D7 is reflection, not tech. If Apollo already cites this in D6, no need to repeat here. |

---

## Decision rule: which 5 to keep

**Mandatory (3):**
- `schon1983reflective` — the reflective vocabulary
- `hatton1995reflection` — the level taxonomy the marker scores against
- `tuckman1965developmental` — the team-dynamics hook

**Pick one of the two cycles (1):**
- `kolb1984experiential` — **preferred** for an iteration-heavy engineering project
- or `gibbs1988learning` — only if the body explicitly labels Gibbs stages

**Optional push to Level 4 (1):**
- `brookfield1995critically` — only if an assumption-examination paragraph actually exists

**Drop entirely unless the body earns them:**
- `imeche2023conduct` (no ethics section → drop)
- `ardupilot` (no protocol argument → drop)

---

## Formatting

- BibLaTeX style: inherit `main.tex` settings (`numeric`, `sorting=none`, `giveninits=true`, `\footnotesize` bibfont).
- Bibliography goes on a page *after* the body — not counted in the 5-page limit per brief.
- No URL in book entries, no DOI on the ArduPilot misc entry, no ISBN printed.
- Use `\cite{key}` inline, once per reference, at point of claim. Never cluster citations (`[1,2,3,4]`) in a reflective report — it looks academic-padding.

---

## What NOT to cite

- **Textbooks on project management (PMBOK, PRINCE2)** — these signal decorative breadth, not depth. Markers have seen them in every D7.
- **Generic leadership books (Belbin team roles, Kotter change)** — same reason. Only cite if the body genuinely uses Belbin vocabulary to categorise teammates, which is risky in a named-person report.
- **Your own code / commits** — reference these in footnotes or the appendix as `repo@<sha>`, not in the bibliography.
- **Wikipedia, Medium, blog posts** — kills credibility instantly.
- **The unit handbook / module brief** — not a reference, it is the target.

---

## Target state

`references.bib` in `personal_v2/` should end up with ~5 entries. The draft file
`drafts/references_recommended.bib` currently holds 8 so that the author can
delete the 3 they do not use. Keep the .bib lean — fewer references, each
earning its place.
