---
name: obs-platform-wiring
description: Obs Platform Wiring skill for AI/ML operations.
title: Obs Platform Wiring
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

wire traces + evals + prompt versions into an existing agent.
Given an agent runtime and product requirements, pick an observability platform and scaffold the wiring.
1. Need prompt management + session replay in one place -> **Langfuse**.
2. Need deep RAG relevancy + drift/anomaly detection -> **Phoenix**.
3. Need automated prompt optimization + PII guardrails -> **Opik**.
4. Already run Datadog -> **Datadog LLM Observability** (maps GenAI natively from v1.37+).
5. Need ELv2-free license -> **Langfuse** (MIT) or **Opik** (Apache 2.0); avoid Phoenix for pure OSS distribution.
1. OTel GenAI instrumentation (Lesson 23) — this is the common substrate.
2. Platform-specific SDK or OTel exporter configuration.
3. LLM-judge rubric for your domain (factual correctness, scope, tone, refusal quality).
4. Prompt versioning wired to traces (Langfuse) or trace clustering config (Phoenix) or experiment definitions (Opik).
5. Guardrails on logged content: PII redaction, secret scrubbing.
6. Dashboards: session health, failure taxonomy, latency distribution, cost per session.
Hard rejects:
- Shipping without evals. Tracing alone is expensive logging.
- Using a self-written LLM-judge with no external verification. CRITIC pattern (Lesson 05): judges need external tools for factual grounding.
- Storing PII in span bodies. Always external store + reference IDs.
Refusal rules:
- If the user asks for "one platform for everything," refuse and offer the decision above. No single platform dominates all three axes.
- If the product has no acceptance criteria for each agent task, refuse to ship evals. An LLM-judge needs a rubric; a rubric needs product decisions.
- If the user wants "no sampling, capture everything," refuse. Trace volume scales linearly with traffic; sampling (head-based or tail-based) is required at scale.
