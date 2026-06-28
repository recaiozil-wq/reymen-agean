---
name: failure-detector
description: Failure Detector skill for AI/ML operations.
title: Failure Detector
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

tagging the five industry-recurring modes plus domain-specific signatures.
Given a product domain and a trace store, produce detectors for agent failure modes.
1. Detector per mode: `hallucinated_action`, `scope_creep`, `cascading_errors`, `context_loss`, `tool_misuse`, `success_hallucination`.
2. Domain-specific detectors (e.g. "created a PR without linking an issue" for a dev tool, "sent an email to > 5 recipients without confirmation" for a marketing tool).
3. Tagger that applies all detectors to each trace and emits a distribution.
4. Threshold-based alerting: if >=5% of today's traces tag a mode, page or open a ticket.
5. Sample retention: for each tagged trace, keep inputs + outputs + state snapshots for operator review.
Hard rejects:
- Detectors that require LLM calls per trace in production. Use pattern-based detectors; reserve LLM-judge for sampled review.
- Tagging only on crash. Most failures produce valid-looking output. Signature checks on content + state are required.
- Storing tagged traces without PII redaction. Failure samples carry the worst content; scrub before storage.
Refusal rules:
- If the user wants "all traces stored forever," refuse for cost + compliance reasons. Sample by tag + rate.
- If the product has no "known good" baseline, refuse drift alerts. Drift needs a reference.
- If detectors are not versioned, refuse. Detector regressions break your signal without notice.
