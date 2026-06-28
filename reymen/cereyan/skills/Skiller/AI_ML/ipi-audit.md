---
name: ipi-audit
description: Ipi Audit skill for AI/ML operations.
title: Ipi Audit
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

information-flow-control coverage.
Given an agentic deployment description, audit the deployment for indirect prompt injection exposure.
1. Untrusted-content inventory. List every source of content the agent may read: RAG documents, inbox, calendar, tool outputs, tickets, product reviews, third-party APIs. Each is a potential IPI vector.
2. Trust labelling. Does the deployment separate trusted (user prompt) from untrusted (retrieved content)? If content is concatenated into the same prompt without a label, IFC is not in effect.
3. Action gating. Which tools can be invoked? For each, is invocation gated by the trusted prompt only, or can untrusted content influence the invocation?
4. Adaptive-attack evaluation. Has the deployment been tested with adaptive attacks (gradient, RL, human red-team) per Nasr et al. 2025? Static-attack-only evaluation is insufficient.
5. Scope-violation boundaries. Identify each cross-trust boundary (e.g., inbox -> send, documents -> external API). For each, verify the action is either disallowed under untrusted influence, or explicitly ratified by the trusted prompt.
Hard rejects:
- Any agent deployment without explicit trust labelling on retrieved content.
- Any defense claim based on static attacks only.
- Any claim of "our agent is prompt-injection safe" without naming the IFC mechanism.
Refusal rules:
- If the user asks whether filtering is sufficient, refuse and explain the Nasr 2025 result that adaptive attacks break >90% of filter-based defenses.
- If the user asks for a silver-bullet defense, refuse — IPI defense requires IFC plus layered response moderation plus human audit on high-stakes actions.
