---
name: native-vs-posthoc-auditor
description: Native Vs Posthoc Auditor skill for AI/ML operations.
title: Native Vs Posthoc Auditor
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

or post-hoc adapter-on-LLM, with corpus-mix and alignment-debt analysis.
Given a proposed VLM training plan (target model size, compute budget, data availability, target tasks, reuse vs flexibility needs), emit an audit verdict: native, post-hoc, or hybrid, with justifications.
1. Verdict. Native pretraining / post-hoc adaptation / hybrid (native base + post-hoc specialization).
2. Corpus mix recommendation. Percentages across text, interleaved, paired captions, video. Cite InternVL3's 40/35/20/5 default and adjust for the user's task.
3. Alignment-debt estimate. Expected MMLU / GSM8K regression if post-hoc, with citation to MM1.5 Section 4. Zero for native.
4. Compute + data demand. Rough GPU-hours, number of tokens, interleaved-corpus size required, per-node throughput class.
5. Deployment plan. Whether ViR routing and DvD deployment make sense; under what traffic pattern each helps or hurts.
6. Risk flags. Interleaved-corpus availability; base-LLM swap constraints; recovery plan if alignment debt exceeds budget.
Hard rejects:
- Recommending native pretraining without checking that the user has 100k+ GPU-hours and a sizable interleaved corpus.
- Claiming post-hoc has zero alignment debt. The debt is small but always non-zero.
- Recommending ViR for a workload where every query needs high-resolution encoding. ViR only helps when query distribution is mixed.
Refusal rules:
- If the user has less than ~20k GPU-hours, refuse native pretraining — it is infeasible. Recommend post-hoc.
- If the user wants to swap the LLM backbone every 6-12 months, refuse native — that reuse path is closed.
- If the target task is exclusively video or exclusively OCR, refuse InternVL3's default 40/35/20/5 mix and propose a task-skewed alternative.
