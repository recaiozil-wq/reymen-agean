---
name: find-your-level
description: Find Your Level skill for AI/ML operations.
title: Find Your Level
version: 1.0.0
---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | AI/ML mühendisi |
| **Nerede?** | AI_ML/ |
| **Ne Zaman?** | AI/ML görevi gerektiğinde |
| **Neden?** | standardize etmek için |
| **Nasıl?** | Skill adımlarını takip ederek |

-------------------------
```
## Score-to-Entry-Point Mapping
## Personalized Learning Path
After revealing the entry point, generate a markdown table covering all 20
phases. Use the score to determine the status of each phase. Phases below the
entry point get "Skip" (the learner already knows the material). Phases at or
above the entry point get "Do". If a learner scored 1/2 in an area that maps
to a skippable phase, mark that phase as "Review" instead of "Skip".
Area-to-phase mapping for review detection:
- Math & Statistics (1/2) -> mark Phase 1 as "Review"
- Classical ML (1/2) -> mark Phase 2 as "Review"
- Deep Learning (1/2) -> mark Phase 3 as "Review"
- NLP & Transformers (1/2) -> mark Phases 5 and 7 as "Review"
- Applied AI (1/2) -> mark Phase 14 as "Review"
Read the time estimates from ROADMAP.md (the canonical source of truth). Each
phase heading contains the estimated hours in the format `(~N hours)`. Parse
these values instead of using hardcoded numbers. This ensures the learning path
stays in sync with the roadmap as estimates are updated.
## Output Format
Generate the table like this:
```markdown
```
Rules for the table:
- "Skip" phases show `--` for hours (they do not count toward the total)
- "Review" phases show full hours (the learner should skim them)
- "Do" phases show full hours
- Phase 0 (Setup & Tooling) is always "Skip" regardless of score (it is
  tooling setup, not knowledge)
- Sum the hours for "Review" and "Do" phases and show the total at the bottom
After the table, add one sentence with the estimated total: "Your personalized
Then add a brief recommendation: which phase to start with, and what to focus
on first based on their weakest area.
