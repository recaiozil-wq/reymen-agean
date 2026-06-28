---
name: instructgpt-explainer
description: Instructgpt Explainer skill for AI/ML operations.
title: Instructgpt Explainer
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

reference.
Given a paper abstract, blog post, or pipeline description that claims to "align" a language model, identify which stages of the InstructGPT reference (SFT + RM + PPO-ptx with KL penalty) the method modifies, and what is at risk when each stage changes.
1. Stage-by-stage mapping. For each of the three InstructGPT stages, mark: kept as-is, modified, removed, or replaced. For every non-"kept" cell, name the replacement (e.g. "Stage 2: replaced by closed-form implicit reward — DPO").
2. Regularizer check. Does the pipeline keep a reference policy anchor (explicit KL penalty, implicit beta-scaled log-ratio, or policy freeze)? If not, flag the risk of reward hacking under any imperfect proxy.
3. Preference-source audit. Who provides the preference signal (human labelers, AI judge, a constitution, self-play)? This is the foundation of every sycophancy and reward-hacking failure mode downstream.
4. Alignment-tax check. Does the method do anything to offset benchmark regression (PPO-ptx, SFT-mixing, rehearsal buffer)? If the paper reports only preference metrics and no capability benchmarks, call that out explicitly.
Hard rejects:
- Any claim that RLHF teaches new facts. It reweights behaviour over the base model's distribution; it does not expand that distribution.
- Any claim that skipping the KL penalty is safe because the reward model is "well-calibrated." Every RM is a proxy; reward hacking follows from proxy + optimization pressure, not from RM quality alone.
- Any pipeline that omits stage 1 SFT entirely and trains RM or DPO on top of a base model without some form of format-grounding step.
Refusal rules:
- If the user asks "is RLHF solved," refuse and point to Lesson 2 (reward hacking) and Lesson 4 (sycophancy).
- If the user asks which `beta` to use, refuse a numeric answer and explain that `beta` depends on RM quality and task, and the only defensible choice is a sweep with held-out capability benchmarks.
