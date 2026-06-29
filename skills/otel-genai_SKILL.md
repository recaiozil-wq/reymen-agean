---
name: otel-genai
description: Otel Genai skill for AI/ML operations.
title: Otel Genai
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

chat, tool_call spans with correct attributes and opt-in content capture.
Given an agent runtime, wire OTel GenAI semantic conventions.
1. `invoke_agent` span per agent run. Kind CLIENT for remote agent services, INTERNAL for in-process. Name: `invoke_agent {gen_ai.agent.name}`.
2. `chat` span per LLM call with `gen_ai.operation.name=chat`, `gen_ai.provider.name`, `gen_ai.request.model`, `gen_ai.response.model`.
3. `tool_call` span per tool invocation with `gen_ai.tool.name` and, when applicable, `gen_ai.data_source.id` (RAG corpus / memory store).
4. Opt-in content capture: default OFF; when ON, store inputs/outputs externally and record `*.reference_id` on spans.
5. Context propagation: use W3C trace context headers so multi-process runs (Claude Agent SDK CLI subprocess) stitch into one trace.
Hard rejects:
- Capturing full prompts/outputs inline by default. PII and secret leakage risk; also violates the spec.
- Missing `gen_ai.provider.name`. Multi-provider dashboards break.
- Orphan tool spans. Always set parent-child relation via active context.
Refusal rules:
- If the runtime cannot propagate context across process boundaries, refuse. Multi-process trace stitching is required for Claude Agent SDK + CLI users.
- If the product has regulatory constraints (HIPAA, GDPR), refuse inline content capture. External store with access control only.
- If the backend does not set `OTEL_SEMCONV_STABILITY_OPT_IN=gen_ai_latest_experimental`, warn: attribute names may change on collector upgrade.
