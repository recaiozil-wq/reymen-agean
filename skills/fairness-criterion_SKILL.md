---
name: fairness-criterion
description: Fairness Criterion skill for AI/ML operations.
title: Fairness Criterion
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

assumptions.
Given a fairness claim or policy, identify which criterion is being invoked, what assumptions the claim depends on, and what the impossibility theorems imply for the remaining criteria.
1. Criterion identification. Label the claim as targeting one of: demographic parity, equalized odds, conditional use accuracy equality, individual fairness, counterfactual fairness. Ambiguous claims must be resolved before proceeding.
2. Base-rate audit. What are the per-group base rates in the deployment? Under unequal base rates, Chouldechova / KMR 2017 impossibility applies: no model satisfies all three group criteria.
3. Causal-DAG dependency. If the claim is counterfactual fairness, what is the causal DAG? Counterfactual fairness is only as justified as the DAG. Lack of a DAG invalidates the claim.
4. Similarity metric. If the claim is individual fairness, what is the similarity metric d? The choice is task-specific and is a policy decision, not a statistical one.
5. Intervention legality. If the claim uses counterfactual reasoning, are interventions on protected attributes involved? If yes, consider backtracking counterfactuals (arXiv:2401.13935) to sidestep legal issues.
Hard rejects:
- Any "fair" claim without criterion identification.
- Any "all fairness criteria satisfied" claim under unequal base rates without acknowledging Chouldechova / KMR 2017.
- Any counterfactual-fairness claim without a published causal DAG.
Refusal rules:
- If the user asks which fairness criterion is "the right one," refuse the ranking and explain it is a policy choice.
- If the user asks whether a model is "fair," refuse the binary claim; fairness is criterion-relative.
