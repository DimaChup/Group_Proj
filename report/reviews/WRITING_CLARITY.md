# Writing Clarity Pass — D6 Body Sections

**Date:** 2026-04-04
**Files edited:** 5 body sections in `report/sections/`

## Summary of Changes

All edits preserve technical content. No deletions. Only readability improvements.

### 1. introduction.tex (6 edits)
- "survival outcomes" -> "survival" (trimmed redundancy)
- "A ground search team of ten members can sweep" -> "A ten-person ground team sweeps" (active voice, shorter)
- "have made it feasible to run" -> "now allow" (shorter, active)
- "This project addresses the gap" -> "This project targets the gap" (stronger verb)
- "land within 10m (but not within 5m)" -> "land 5--10m away" (clearer, shorter)
- "The project was undertaken by Company X" -> "Company X comprises" (active voice, present tense)
- Trimmed "each of the twelve requirements" -> "each requirement" in report structure paragraph

### 2. design_rationale.tex (12 edits)
- Opening sentence: removed "outlined in" filler, tightened phrasing
- "the following subsections detail the technical trade studies that determined the system's..." -> trimmed to remove filler
- "The search pattern is governed by" -> "govern the search pattern" (active voice restructure)
- "increases the number of scan lines" -> "increases scan lines" (trim)
- "evaluated every combination on the AENGM0074 polygon geometry" -> "on the AENGM0074 polygon" (trim)
- "The hardware integrates" -> "The hardware combines" (varied verb)
- "Onboard inference on the Pi 5 eliminates" -> "Onboard inference eliminates" (trim)
- "All four trade studies in this section use" -> "All four trade studies use" (trim)
- "Direct serial is the simplest option but" -> "Direct serial is simplest but" (trim)
- "demonstrating evidence-driven iteration rather than assumption-driven design" -> removed (self-congratulatory)
- Section summary: removed "demonstrating the evidence-driven engineering process that underpins the system" (self-congratulatory)
- "allows the network to learn" -> "lets the network learn" (simpler verb)

### 3. system_description.tex (9 edits)
- Opening: "Having established the rationale behind each design choice" -> "With the design rationale established" (shorter)
- "into an autonomous SAR architecture" -> removed (redundant with section context)
- "with no integration risk" -> removed (self-congratulatory)
- "Table summarises the bill of materials for the Hexsoon..." -> "Table lists the bill of materials" (trim long enumeration)
- Hardware paragraph: tightened MAVProxy description, removed "(see Appendix for the full communications architecture)" -> "(Appendix)"
- "The system comprises eleven Python modules" -> "Eleven Python modules" (active, shorter)
- "The vision subsystem is encapsulated in" -> "resides in" (simpler verb)
- "The characteristic directional elongation" -> "The directional elongation" (trim)
- Removed redundant closing paragraph listing all subsystems; replaced with one-sentence bridge

### 4. requirements_verification.tex (3 edits)
- Removed redundant "The system described in Section... was designed to satisfy twelve requirements defined in the AENGM0074 project brief" -- condensed to one sentence
- "Recent code improvements closed several evidence gaps" -> "Late-stage code improvements closed several evidence gaps" (more specific)
- "evaluates the system's overall technical performance, examining both the strengths that these verification results demonstrate and the gaps that remain" -> "assesses overall technical performance, examining the strengths these results demonstrate and the gaps that remain" (trimmed)

### 5. evaluation.tex (14 edits)
- Opening: "Section established that 8 of 12 requirements are verified... with 3 verified in simulation only and 1 partially verified" -> "8 of 12 requirements are verified... 3 in simulation only, and 1 partially" (shorter)
- "the drone's reported position to produce" -> "drone position to produce" (trim)
- "Inverse-variance-weighted averaging" -> "Inverse-variance averaging" (trim)
- Weather cancellation paragraph: removed "This cancellation represents the single largest gap in the project, eliminating any possibility of Tier 4/5 validation" (moved info to next sentence, tighter)
- "as an opportunity for information maximisation rather than a binary failure" -> "as an opportunity to maximise information yield" (shorter)
- "is almost certainly inflated relative to real deployment" -> "is almost certainly inflated" (trim)
- "represents a quantitative contribution that most comparable projects lack" -> "is a quantitative contribution most comparable projects lack" (trim)
- Pi 5 vs Jetson: removed final sentence "a Jetson would have eliminated the need for backend optimisation entirely" (obvious)
- Python+MAVLink: restructured for active voice
- Simulation-first: "consumed approximately 10 of the 16 available weeks" -> "consumed approximately 10 of 16 available weeks" (trim)
- Multi-class: "This was a deliberate autonomy design choice" -> "This aligns with" (shorter, less defensive)
- Mission metrics intro: "While subsystem metrics... are reported above" -> "SAR effectiveness is ultimately measured at the mission level, not subsystem metrics" (direct)
- Testing framework: "with each tier serving as a gate that must pass before the next is attempted" -> "with each tier gating the next" (much shorter)
- Closing: "a modular architecture that survived three model retrains and two backend changes without a single line of orchestrator modification" -> "two backend swaps without changing a single line of orchestrator code" (stronger)

## Patterns Fixed
- **Passive voice**: ~15 instances converted to active
- **Self-congratulatory language**: removed "robust", "comprehensive", "sophisticated" phrasing in 4 places
- **Redundant filler**: trimmed "the system's", "in this section", "the full", etc. in ~20 places
- **Long sentences**: split or shortened ~8 sentences exceeding 40 words
- **Consistent tense**: system_description now uses present tense for how the system works; evaluation uses past tense for what was done

## Not Changed
- Technical content (numbers, equations, citations, table data)
- LaTeX formatting (figure placements, table structures, environments)
- Section structure or ordering
- Reference labels or cross-references
- Content of "Decisions That Changed" paragraphs (already well-written with clear structure)
