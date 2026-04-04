# Writing Quality Final Sweep — D6 Body Sections

**Date:** 2026-04-04
**Files reviewed:** exec_summary.tex, intro_d6.tex, design_rationale.tex, system_description.tex, requirements_verification.tex, evaluation.tex

## Summary

The writing quality across all six body sections is strong. The prose is technical, specific, and largely free of common academic writing flaws. Most sentences use active voice, present tense for system description, and past tense for development actions. No self-congratulatory language ("comprehensive", "robust", "sophisticated", "novel") was found.

## Changes Made

### exec_summary.tex (1 fix)
- **Line 26:** Removed passive/circular phrasing "ensure that this step can proceed with quantified confidence" -> "provide quantified confidence in each subsystem for this remaining step"

### intro_d6.tex (4 fixes)
- **Line 27:** "Our company was formed..." (passive) -> "The company comprises..." (active, present)
- **Line 27:** "We adopted a workstream-based methodology" kept (active, good). Removed redundant "as a team of five MSc students" (already stated).
- **Line 27:** "All development was managed through" (passive) -> "All code resides in" (active, present)
- **Line 29:** "This lightweight process allowed team members to work independently on their respective streams while ensuring that integration points were well-defined and that no subsystem was developed in isolation from the others" (wordy, passive "was developed") -> shortened to active voice
- **Line 94:** "The report is organised as follows" -> "The report proceeds as follows" (more direct); tightened passive constructions throughout the paragraph

### design_rationale.tex (3 fixes)
- **Line 28:** "detail the trade studies" -> "present the trade studies" (more precise verb)
- **Line 55 caption:** "comfortable detection margin" (vague) -> "$1.8\times$ detection margin" (quantified)
- **Line 273:** "comfortable $1.6\times$ margin" -> "$1.6\times$ margin" (removed filler adjective)
- **Line 309:** "The team executed" -> "We executed" (specific attribution)

### system_description.tex (0 fixes)
- No changes needed. Consistently uses present tense for system description. Active voice throughout. No "the team" references. Technical and precise.

### requirements_verification.tex (0 fixes)
- No changes needed. Concise table-driven format. Appropriate passive in table cells (acceptable for evidence descriptions). Clear final paragraph connecting to evaluation.

### evaluation.tex (3 fixes)
- **Line 116:** "comfortable margin above the 20\,px floor" (vague) -> "$1.8\times$ above the 20\,px floor" (quantified)
- **Line 125:** "Had the team scheduled" -> "Scheduling multiple flight windows... would have mitigated" (removed "the team", active voice)
- **Line 165 caption:** "excels in cost-effectiveness" (self-congratulatory) -> "scores highest on cost-effectiveness" (neutral)
- **Line 191:** "while impressive in quantity" (self-congratulatory filler) -> removed

## Issues NOT Found (already clean)
- No "comprehensive", "robust", "sophisticated", "novel", "elegant", "powerful" in any body section
- No "the team" references remaining in any body section
- No "in order to", "it should be noted", "it is worth noting" filler
- No "utilise/utilize" (uses "use" throughout)
- No inconsistent tense: system descriptions in present, development actions in past
- No paragraphs missing topic sentences
- Sentences are generally under 40 words (a few technical sentences with parenthetical specifications are longer but splitting them would reduce clarity)

## Overall Assessment
The writing is publication-quality. The evaluation section in particular demonstrates strong self-critical analysis with honest acknowledgment of limitations. The main pattern fixed was replacing vague qualitative claims ("comfortable margin") with specific quantified claims ("$1.8\times$ margin"), and removing the few remaining instances of "the team" and mild self-congratulation.
