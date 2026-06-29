---
name: routing-config-designer
description: Routing Config Designer skill for AI/ML operations.
title: Routing Config Designer
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

a routing config.
Given a workload profile (latency requirements, compliance constraints, team size, spend budget), produce a routing gateway choice and configuration.
1. Gateway choice. LiteLLM (self-hosted), OpenRouter (managed SaaS), or Portkey (production w/ guardrails). One-paragraph justification.
2. Alias list. Logical model names the application uses. Example: `smart`, `fast`, `coding`, `long_context`.
3. Fallback chains. Per alias, priority-ordered concrete-model list with retry budget.
4. Guardrails. PII redaction rules, policy-violation list, output-filter rules.
5. Cost budget. Per-team / per-project spend cap, enforcement granularity.
Hard rejects:
- Any config that sends prompts to a region violating the compliance constraint.
- Any fallback chain with only one provider. One failure domain defeats the purpose.
- Any guardrail-less setup if the workload processes user input directly.
Refusal rules:
- If the workload is a single-model prototype and expected to stay that way, refuse to recommend a gateway; direct API calls are simpler.
- If the team has no SRE and picks self-hosted, flag the operational risk.
- If the user asks for a specific model without alternatives, refuse and require at least one fallback.
