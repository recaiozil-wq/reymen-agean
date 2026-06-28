---
name: ecc_santa-method_references_failure-modes-and-mitigations
description: Failure Modes and Mitigations
title: "Ecc Santa Method References Failure Modes And Mitigations"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Failure Modes and Mitigations |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Failure Modes and Mitigations

| Failure Mode | Symptom | Mitigation |
|-------------|---------|------------|
| Infinite loop | Reviewers keep finding new issues after fixes | Max iteration cap (3). Escalate. |
| Rubber stamping | Both reviewers pass everything | Adversarial prompt: "Your job is to find problems, not approve." |
| Subjective drift | Reviewers flag style preferences, not errors | Tight rubric with objective pass/fail criteria only |
| Fix regression | Fixing issue A introduces issue B | Fresh reviewers each round catch regressions |
| Reviewer agreement bias | Both reviewers miss the same thing | Mitigated by independence, not eliminated. For critical output, add a third reviewer or human spot-check. |
| Cost explosion | Too many iterations on large outputs | Batch sampling pattern. Budget caps per verification cycle. |
