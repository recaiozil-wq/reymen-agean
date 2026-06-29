---
name: ecc_santa-method_references_re-run-both-reviewers-on-fixed-output-fresh-agents-no-memory
description: "Re-run BOTH reviewers on fixed output (fresh agents, no memory of previous round)"
title: "Ecc Santa Method References Re Run Both Reviewers On Fixed Output Fresh Agents No Memory"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Re-run BOTH reviewers on fixed output (fresh agents, no memory of previous round) |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Re-run BOTH reviewers on fixed output (fresh agents, no memory of previous round)
    review_b = Agent(prompt=REVIEWER_PROMPT.format(output=output, ...))
    review_c = Agent(prompt=REVIEWER_PROMPT.format(output=output, ...))
