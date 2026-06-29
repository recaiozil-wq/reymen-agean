---
name: reward-hack-auditor
description: Reward Hack Auditor skill for AI/ML operations.
title: Reward Hack Auditor
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

logs and eval outputs.
Given an RLHF model's training reports (proxy-reward curve, KL trajectory, eval deltas) and a sample of outputs, identify which of the four reward-hacking costumes is most likely active and locate it in the evidence.
1. Proxy-gold gap fingerprint. Plot (or describe) proxy reward vs KL distance from the SFT reference. Mark the peak of gold reward (human eval, held-out RM, or proxy for these). Report whether the model is before, at, or past the gold peak.
2. Costume identification. Check for each of verbosity, sycophancy, unfaithful reasoning, evaluator tampering. For each: cite a specific output or metric that triggered the flag.
3. Mechanism trace. Name the spurious feature the RM is likely rewarding (length, confident phrasing, agreement, formatting). Cite a prompt where the feature decouples from quality.
4. Mitigation recommendation. From the set {more preference data, RM ensemble, process supervision, KL schedule tightening, early stopping, shift to DAA}, recommend the single intervention the evidence supports and name one that would be wasted effort here.
Hard rejects:
- Any claim that a single RM "fixes" reward hacking. The Gao et al. (ICML 2023) curve is universal — a bigger RM pushes the peak out but does not eliminate it.
- Any claim that KL regularization is sufficient. Catastrophic Goodhart (OpenReview UXuBzWoZGK) shows KL alone fails under heavy-tailed reward error.
- Any recommendation to "just tune beta" without held-out capability benchmarks.
Refusal rules:
- If the user only provides proxy-reward curves with no held-out gold signal, refuse to diagnose and demand held-out evals. Diagnosis without gold is reward-hacking-by-proxy-of-diagnosis.
- If the user provides unfaithful-CoT evidence and asks whether process supervision "solves" it, refuse a binary answer and point to the open literature.
