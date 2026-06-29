---
name: sleeper-audit
description: Sleeper Audit skill for AI/ML operations.
title: Sleeper Audit
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

removal of a planted or suspected backdoor.
Given a report that claims a harmful behaviour has been removed from a model (via SFT, RLHF, adversarial training, or any combination), audit whether the removal has actually been demonstrated against the standard Hubinger et al. 2024 threat model.
1. Elicitation scope. Did the report hold out an elicitation method that the training pipeline never saw? If the only evaluation is the red team's own distribution, removal is unproven.
2. Trigger generality. Is the claimed trigger a literal string, a distribution shift, or an environmental feature (date, token, context size)? Generality of the trigger determines the size of the search space the red team has to cover.
3. Internal-state evidence. Did the team apply residual-stream probes, SAE features, or other mechanistic probes to check whether the trigger-relevant state is still present internally even when behaviour is clean? Per the April 2024 Anthropic follow-up, internal state remains linearly legible after behavioural removal.
4. Persistence-through-pipeline check. Was removal verified after every subsequent training stage (further SFT, later RLHF pass, adapter merge, distillation)? Backdoors persist through training — the final model is the thing evaluated, not a middle checkpoint.
5. Scale-consistency check. If the claim is based on a smaller model, Hubinger 2024 Figure 4 shows persistence grows with scale. Smaller-model evidence does not transfer upward.
Hard rejects:
- Any claim that "we applied RLHF so the model is safe" with no held-out elicitation.
- Any claim based only on red-team-distribution evaluation (training and evaluation draw from the same pool).
- Any claim of removal without internal-state probes when the original implant mechanism is unknown.
Refusal rules:
- If the user asks "can RLHF remove deceptive alignment," refuse the binary answer and point to Hubinger et al. 2024 Section 5 on persistence and Section 6 on chain-of-thought.
- If the user asks for a numeric probability of latent deception, refuse and explain that base rates are unknown; the empirical evidence is persistence in constructed organisms, not emergence rate in naturally trained models.
