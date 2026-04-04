# Reportflow Writing Quality Sweep

**Date:** 2026-04-04
**File:** `report/reportflow/main.tex` (1102 lines -> 1179 lines after edits)
**Backup:** `report/reportflow/main.tex.bak`

## Changes Made

### 1. Passive Voice -> Active Voice (~25 instances fixed)

| Location | Before | After |
|----------|--------|-------|
| Exec summary | "the system comprises" | "the system combines" |
| Exec summary | "Twelve formal requirements were verified" | "Verification against twelve formal requirements shows" |
| Sec 2 Constraints | "This objective is bounded by hard constraints" | "Hard constraints...bound this objective" |
| Sec 5 MCDA | "A dual-backend architecture was adopted" | "We adopted a dual-backend architecture" |
| Sec 6 Scoring | "are scored continuously and combined" | "score continuously and combine" |
| Sec 6 Scoring | "are treated as" (safety/time) | "serve as" |
| Sec 6.2 Detection | "A multiplicative combination is used" | "We use a multiplicative combination" |
| Sec 6.2 Detection | "Model mAP50 is not included" | "We exclude model mAP50" |
| Sec 6.5 Composite | "Time is treated similarly" | "Time follows the same logic" |
| Step 1 | "The YOLOv8n model was retrained" | "We retrained the YOLOv8n model" |
| Step 5 | "This approach was not adopted" | "We did not adopt this approach" |
| Step 7 | "was applied to every candidate angle" | "We applied...to every candidate angle" |
| Step 9 | "The 20% value was selected" | "We selected 20%" |
| Speed (Step 4) | "The baseline was chosen" | "We chose the baseline" |
| Speed (Step 4) | "was determined empirically" | "We determined...empirically" |
| Speed (Step 4) | "was retained for" | "We retained...for" |
| Energy | "The conservatism ensures" | "This ensures" |
| CV Pipeline | "The retrained model was trained on" | "We trained the model on" |
| CV Pipeline | "This was verified with 1440" | "We verified this with 1440" |
| Safety arch | "This was motivated by a real incident" | "A real incident motivated this design" |
| Delta | "was designed but not implemented" | "We designed...but did not implement" |
| Delta | "was calibrated on bench" | "We calibrated...on bench" |
| Localization | "were surveyed" | "We surveyed" |
| Localization | "Each was evaluated" | "We evaluated each" |
| Requirements | "were designed to satisfy" | "satisfy" |
| Testing | "were not written as an afterthought --- they are" | "are" |

### 2. Self-Congratulatory Language Removed (6 instances)

| Before | After |
|--------|-------|
| "We did not rely on intuition. A physics-based" | "A physics-based" (cut throat-clearing) |
| "not written as an afterthought --- they are integral" | "are integral" |
| "genuinely optimal, not merely" | "optimal, not merely" |
| "a near-perfect detector that validated" | "a detector that validated" |
| "A rigorous engineering process is measured not by..." (entire sentence) | Cut; section now starts with "Four significant corrections were made" |
| "demonstrated strong simulation-level capability" | "demonstrates simulation-level capability" |
| "reflects honestly on what worked" | "examines what worked" |

### 3. Vague Claims Quantified / Qualified (3 instances)

| Before | After |
|--------|-------|
| "where a casualty is unlikely to be found" | "where casualty presence is unlikely given the NFZ protection status" |
| "the selected point is the only one that avoids" | "the selected point avoids" (removed unsupported uniqueness claim) |
| "No value was assumed or rounded for convenience" | "Each value traces to measurement or regulation" |

### 4. Redundant Phrasing Tightened (4 instances)

| Before | After |
|--------|-------|
| "autonomous Search and Rescue (SAR) drone system" | "autonomous Search and Rescue (SAR) drone" |
| "a 20-state finite state machine atop" | "a 20-state finite state machine on" |
| "This is sufficient to ensure no gaps" | "This ensures gap-free coverage" |
| "A score of 1.0 would mean zero energy consumed (impossible); a score of 0.0 would mean the battery is fully depleted" | "A score of 1.0 means zero energy consumed (impossible); 0.0 means full battery depletion" |

### 5. Transition / Topic Sentence Fixes (3 instances)

| Before | After |
|--------|-------|
| "The priority ordering above did not emerge in a vacuum." | "External factors shaped this priority ordering." |
| "showing how external factors shaped" (double "shaped") | "showing how these factors influenced" |
| "The results are shown in Figure" (weak) | "Figure...shows" (direct reference) |

### 6. Tense Consistency Fix

- "demonstrated that the modular architecture **contained** errors" -> "**confined** errors" (was both a tense issue and a word error -- "contained" means held inside, "confined" means restricted to)

### 7. Conclusion Paragraph Break

Split the final paragraph of the conclusion into two paragraphs to separate the bug-fix evidence from the forward-looking framework statement.

## Assessment of Structure

### Section Topic Sentences
Every section opens with a clear purpose statement. The decision chain steps each begin with "Why this comes first/after X" which provides strong logical flow.

### Transitions
Good throughout. The chain structure (each step feeds the next) provides natural transitions. The STEEPLE -> MCDA -> Scoring -> Variables -> Chain progression reads logically.

### Executive Summary
Now more direct after edits. Leads with the system, states the method, gives the key result, and ends with verification status. The only remaining weakness: it front-loads citations (4 in the first sentence) which slows the reader. Consider moving citations to a second sentence in a future pass.

### Conclusion
Ties back well to the objective (detection probability, battery usage, safety margin). The 7.7/10 vs 2.1/10 self-assessment is honest and strong. The "re-evaluable in minutes" closing gives a forward-looking note.

## Remaining Items (not fixed, flagged for awareness)

1. **Remaining passive voice (4 instances)**: Lines 955, 982, 999, 1009, 1015 -- these are in the bug-discovery narratives and requirements status descriptions where passive voice is arguably appropriate (describing what happened to the system, not what the team did).

2. **Long sentences**: The exec summary is still one dense paragraph. Consider breaking it into 2-3 shorter paragraphs for readability.

3. **Inconsistent "we" vs impersonal**: The paper now uses "we" consistently for team actions, but some sections still use impersonal constructions for system behaviour ("the drone maintains", "the system transitions"). This is acceptable academic style -- system actions described impersonally, team decisions described with "we".

4. **Step 4 paragraph length**: The Step 4 subsection (speed determination) runs ~40 lines without a visual break. Consider splitting after the speed envelope table.
