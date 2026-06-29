---
name: ecc_mle-workflow_references_decision-brain
description: Decision Brain
title: "Ecc Mle Workflow References Decision Brain"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_mle-workflow_references_decision-brain.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

## Decision Brain

Use this loop whenever the task is ambiguous, high-impact, or metric-heavy:

1. Start from the decision, not the model. Name the action that changes downstream behavior.
2. Name who cares and why. Different stakeholders pay different costs for false positives, false negatives, latency, compute spend, opacity, or missed opportunities.
3. Convert ambiguity into hypotheses. Ask what signal would separate outcomes, what evidence would disprove it, and what simple baseline should be hard to beat.
4. Research prior art or a nearby known problem before inventing a bespoke system.
5. Score choices with `(probability, confidence) x (cost, severity, importance, impact)`.
6. Consider adversarial behavior, incentives, selective disclosure, distribution shift, and feedback loops.
7. Prefer the simplest change that reduces the most important mistake. Simplicity is not laziness; it is a way to minimize blunders while preserving iteration speed.
8. Capture the decision, evidence, counterargument, and next reversible step.
